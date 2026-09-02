"""Account erasure (UK GDPR Art 17 / S0.4)."""
import json

from models.user import normalize_handle, utc_now_iso

DELETED_HANDLE_LABEL = 'a deleted account'
HANDLE_RESERVE_DAYS = 90

# Tables keyed by user_id (or equivalent) for post-delete assertions.
USER_SCOPED_CHECKS = (
    ('saved_problems', 'user_id'),
    ('lesson_progress', 'user_id'),
    ('quiz_attempts', 'user_id'),
    ('generator_mcq_attempts', 'user_id'),
    ('user_profile_settings', 'user_id'),
    ('user_activity_summary', 'user_id'),
    ('user_activity_events', 'user_id'),
    ('shared_questions', 'user_id'),
    ('email_digest_log', 'user_id'),
    ('user_streaks', 'user_id'),
    ('user_streak_freezes', 'user_id'),
    ('user_study_days', 'user_id'),
    ('user_milestones', 'user_id'),
    ('user_notifications', 'user_id'),
    ('user_problem_queues', 'user_id'),
    ('user_revision_queue', 'user_id'),
    ('user_wrong_answer_reflections', 'user_id'),
    ('user_revision_plans', 'user_id'),
    ('api_tokens', 'user_id'),
    ('qotd_attempts', 'user_id'),
    ('password_reset_tokens', 'user_id'),
    ('email_verification_tokens', 'user_id'),
    ('login_lockouts', 'user_id'),
    ('teacher_profiles', 'user_id'),
)


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _count(conn, sql, params):
    row = conn.execute(sql, params).fetchone()
    return int(row[0]) if row else 0


def _foreign_keys_on(conn):
    row = conn.execute('PRAGMA foreign_keys').fetchone()
    return bool(row and row[0])


def _scrub_payload_handle(payload_json, handle):
    if not payload_json or not handle:
        return payload_json, False
    try:
        payload = json.loads(payload_json)
    except (TypeError, json.JSONDecodeError):
        if handle in str(payload_json):
            return json.dumps({'note': DELETED_HANDLE_LABEL}), True
        return payload_json, False
    if not isinstance(payload, dict):
        return payload_json, False
    changed = False
    needle = handle.lower()
    for key, value in list(payload.items()):
        if isinstance(value, str) and value.lower().lstrip('@') == needle:
            payload[key] = DELETED_HANDLE_LABEL
            changed = True
    return json.dumps(payload), changed


def delete_user_account(conn, user_id):
    """Erase a user. Returns per-table row counts for an audit log."""
    if not _foreign_keys_on(conn):
        conn.execute('PRAGMA foreign_keys=ON')
        if not _foreign_keys_on(conn):
            raise RuntimeError('SQLite foreign_keys must be ON before account deletion')

    row = conn.execute(
        'SELECT id, handle FROM users WHERE id = ?',
        (user_id,),
    ).fetchone()
    if not row:
        return {'ok': False, 'error': 'user_not_found'}

    handle = row['handle']
    counts = {'users': 1, 'handle': handle}

    reports = conn.execute(
        'UPDATE user_reports SET reported_user_id = NULL WHERE reported_user_id = ?',
        (user_id,),
    ).rowcount
    counts['user_reports_anonymised'] = reports

    rl = conn.execute(
        "DELETE FROM rate_limit_buckets WHERE bucket_key LIKE ?",
        (f'%:user:{user_id}',),
    ).rowcount
    counts['rate_limit_buckets'] = rl

    qt_deleted = 0
    if _table_exists(conn, 'quicktest_sessions'):
        sessions = conn.execute('SELECT session_id, data FROM quicktest_sessions').fetchall()
        for session in sessions:
            data = session['data'] or ''
            drop = False
            if f'qt_u{user_id}_' in (session['session_id'] or ''):
                drop = True
            else:
                try:
                    parsed = json.loads(data)
                    if str(parsed.get('owner_user_id')) == str(user_id):
                        drop = True
                except (TypeError, json.JSONDecodeError):
                    if f'"owner_user_id": {user_id}' in data or f'"owner_user_id":{user_id}' in data:
                        drop = True
            if drop:
                conn.execute(
                    'DELETE FROM quicktest_sessions WHERE session_id = ?',
                    (session['session_id'],),
                )
                qt_deleted += 1
    counts['quicktest_sessions'] = qt_deleted

    payload_tables = []
    if _table_exists(conn, 'user_notifications'):
        payload_tables.append('user_notifications')
    if _table_exists(conn, 'user_activity_events'):
        payload_tables.append('user_activity_events')
    scrubbed = 0
    for table in payload_tables:
        rows = conn.execute(f'SELECT id, payload_json FROM {table}').fetchall()
        for item in rows:
            new_payload, changed = _scrub_payload_handle(item['payload_json'], handle)
            if changed:
                conn.execute(
                    f'UPDATE {table} SET payload_json = ? WHERE id = ?',
                    (new_payload, item['id']),
                )
                scrubbed += 1
    counts['payload_handles_scrubbed'] = scrubbed

    audit_scrubbed = 0
    if _table_exists(conn, 'class_audit_events'):
        conn.execute(
            '''
            UPDATE class_audit_events
            SET subject_handle = ?
            WHERE subject_handle = ? COLLATE NOCASE
            ''',
            (DELETED_HANDLE_LABEL, handle),
        )
        audit_rows = conn.execute(
            'SELECT id, meta_json FROM class_audit_events'
        ).fetchall()
        for item in audit_rows:
            new_payload, changed = _scrub_payload_handle(item['meta_json'], handle)
            if changed:
                conn.execute(
                    'UPDATE class_audit_events SET meta_json = ? WHERE id = ?',
                    (new_payload, item['id']),
                )
                audit_scrubbed += 1
    counts['class_audit_handles_scrubbed'] = audit_scrubbed

    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))

    now = utc_now_iso()
    conn.execute(
        '''
        INSERT OR REPLACE INTO deleted_handles (handle, deleted_at)
        VALUES (?, ?)
        ''',
        (normalize_handle(handle), now),
    )
    conn.commit()
    counts['ok'] = True
    counts['deleted_handles'] = 1
    return counts


def remaining_user_rows(conn, user_id):
    leftover = {}
    for table, column in USER_SCOPED_CHECKS:
        if not _table_exists(conn, table):
            continue
        leftover[table] = _count(conn, f'SELECT COUNT(*) FROM {table} WHERE {column} = ?', (user_id,))
    leftover['follows_as_follower'] = _count(
        conn, 'SELECT COUNT(*) FROM follows WHERE follower_id = ?', (user_id,)
    ) if _table_exists(conn, 'follows') else 0
    leftover['follows_as_following'] = _count(
        conn, 'SELECT COUNT(*) FROM follows WHERE following_id = ?', (user_id,)
    ) if _table_exists(conn, 'follows') else 0
    leftover['users'] = _count(conn, 'SELECT COUNT(*) FROM users WHERE id = ?', (user_id,))
    leftover['reports_as_subject'] = _count(
        conn, 'SELECT COUNT(*) FROM user_reports WHERE reported_user_id = ?', (user_id,)
    ) if _table_exists(conn, 'user_reports') else 0
    leftover['quiz_challenges'] = _count(
        conn,
        'SELECT COUNT(*) FROM quiz_challenges WHERE creator_id = ? OR opponent_id = ?',
        (user_id, user_id),
    ) if _table_exists(conn, 'quiz_challenges') else 0
    leftover['study_pairs'] = _count(
        conn,
        '''
        SELECT COUNT(*) FROM study_pairs
        WHERE user_low_id = ? OR user_high_id = ? OR invited_by_id = ? OR to_user_id = ?
        ''',
        (user_id, user_id, user_id, user_id),
    ) if _table_exists(conn, 'study_pairs') else 0
    leftover['user_blocks'] = _count(
        conn,
        'SELECT COUNT(*) FROM user_blocks WHERE blocker_id = ? OR blocked_id = ?',
        (user_id, user_id),
    ) if _table_exists(conn, 'user_blocks') else 0
    leftover['classes'] = _count(
        conn, 'SELECT COUNT(*) FROM classes WHERE teacher_id = ?', (user_id,)
    ) if _table_exists(conn, 'classes') else 0
    if _table_exists(conn, 'class_memberships'):
        leftover['class_memberships'] = _count(
            conn,
            'SELECT COUNT(*) FROM class_memberships WHERE student_id = ? OR removed_by_teacher_id = ?',
            (user_id, user_id),
        )
    # Phase 4 — listed when those tables exist.
    if _table_exists(conn, 'class_assignments'):
        leftover['class_assignments'] = _count(
            conn, 'SELECT COUNT(*) FROM class_assignments WHERE teacher_id = ?', (user_id,)
        )
    if _table_exists(conn, 'class_assignment_recipients'):
        leftover['class_assignment_recipients'] = _count(
            conn,
            'SELECT COUNT(*) FROM class_assignment_recipients WHERE student_id = ?',
            (user_id,),
        )
    if _table_exists(conn, 'class_assignment_previews'):
        leftover['class_assignment_previews'] = _count(
            conn, 'SELECT COUNT(*) FROM class_assignment_previews WHERE teacher_id = ?', (user_id,)
        )
    if _table_exists(conn, 'class_invites'):
        leftover['class_invites'] = _count(
            conn,
            'SELECT COUNT(*) FROM class_invites WHERE teacher_id = ? OR student_id = ?',
            (user_id, user_id),
        )
    if _table_exists(conn, 'class_audit_events'):
        leftover['class_audit_events'] = _count(
            conn, 'SELECT COUNT(*) FROM class_audit_events WHERE actor_id = ?', (user_id,)
        )
    return leftover


def handle_is_reserved(conn, handle):
    handle = normalize_handle(handle)
    row = conn.execute(
        'SELECT deleted_at FROM deleted_handles WHERE handle = ? COLLATE NOCASE',
        (handle,),
    ).fetchone()
    return bool(row)
