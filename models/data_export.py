"""Subject-access / portability export (UK GDPR Art 15/20 / S0.5)."""
import json

from models.user import utc_now_iso

SCHEMA_VERSION = 1

_TABLES = (
    ('saved_problems', 'user_id'),
    ('lesson_progress', 'user_id'),
    ('quiz_attempts', 'user_id'),
    ('generator_mcq_attempts', 'user_id'),
    ('user_activity_summary', 'user_id'),
    ('user_activity_events', 'user_id'),
    ('shared_questions', 'user_id'),
    ('email_digest_log', 'user_id'),
    ('user_streaks', 'user_id'),
    ('user_streak_freezes', 'user_id'),
    ('user_study_days', 'user_id'),
    ('user_milestones', 'user_id'),
    ('user_notifications', 'user_id'),
    ('user_revision_queue', 'user_id'),
    ('user_wrong_answer_reflections', 'user_id'),
    ('user_revision_plans', 'user_id'),
    ('qotd_attempts', 'user_id'),
)


def _rows(conn, sql, params=()):
    found = conn.execute(sql, params).fetchall()
    return [dict(row) for row in found]


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return bool(row)


def build_user_export(conn, user_id):
    user = conn.execute(
        '''
        SELECT id, email, handle, created_at, last_login_at, is_active, email_verified_at
        FROM users WHERE id = ?
        ''',
        (user_id,),
    ).fetchone()
    if not user:
        return None

    settings_row = conn.execute(
        'SELECT * FROM user_profile_settings WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    settings = dict(settings_row) if settings_row else {}

    practice = {}
    for table, column in _TABLES:
        if not _table_exists(conn, table):
            continue
        practice[table] = _rows(conn, f'SELECT * FROM {table} WHERE {column} = ?', (user_id,))

    following = _rows(
        conn,
        '''
        SELECT u.handle, f.created_at
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ORDER BY f.created_at
        ''',
        (user_id,),
    ) if _table_exists(conn, 'follows') else []
    followers = _rows(
        conn,
        '''
        SELECT u.handle, f.created_at
        FROM follows f
        JOIN users u ON u.id = f.follower_id
        WHERE f.following_id = ?
        ORDER BY f.created_at
        ''',
        (user_id,),
    ) if _table_exists(conn, 'follows') else []

    tokens = []
    if _table_exists(conn, 'api_tokens'):
        tokens = _rows(
            conn,
            '''
            SELECT id, label, created_at, last_used_at, expires_at
            FROM api_tokens WHERE user_id = ?
            ''',
            (user_id,),
        )

    teacher = None
    if _table_exists(conn, 'teacher_profiles'):
        profile = conn.execute(
            'SELECT user_id, enabled_at FROM teacher_profiles WHERE user_id = ?',
            (user_id,),
        ).fetchone()
        classes = []
        if _table_exists(conn, 'classes'):
            classes = _rows(
                conn,
                '''
                SELECT id, name, level, subject, org_id, join_code,
                       join_code_rotated_at, created_at, archived_at
                FROM classes WHERE teacher_id = ?
                ORDER BY created_at
                ''',
                (user_id,),
            )
        teacher = {
            'enabled': bool(profile),
            'enabled_at': profile['enabled_at'] if profile else None,
            'classes': classes,
        }

    classes_joined = []
    if _table_exists(conn, 'class_memberships'):
        classes_joined = _rows(
            conn,
            '''
            SELECT c.id, c.name, c.level, c.subject, c.archived_at,
                   u.handle AS teacher_handle,
                   m.status, m.joined_at, m.removed_at
            FROM class_memberships m
            JOIN classes c ON c.id = m.class_id
            JOIN users u ON u.id = c.teacher_id
            WHERE m.student_id = ?
            ORDER BY m.joined_at
            ''',
            (user_id,),
        )

    class_work = []
    if _table_exists(conn, 'class_assignment_recipients'):
        raw_work = _rows(
            conn,
            '''
            SELECT a.id AS assignment_id, a.class_id, c.name AS class_name,
                   a.level, a.subject, a.topic, a.mode, a.difficulty,
                   a.question_count, a.created_at,
                   r.status, r.answers_json, r.score, r.completed_at
            FROM class_assignment_recipients r
            JOIN class_assignments a ON a.id = r.assignment_id
            JOIN classes c ON c.id = a.class_id
            WHERE r.student_id = ?
            ORDER BY a.created_at
            ''',
            (user_id,),
        )
        for item in raw_work:
            answers = []
            try:
                parsed = json.loads(item.pop('answers_json', None) or '[]')
            except (TypeError, ValueError):
                parsed = []
            if isinstance(parsed, list):
                for index, slot in enumerate(parsed):
                    if not isinstance(slot, dict):
                        continue
                    answers.append({
                        'index': index,
                        'user_answer': slot.get('user_answer'),
                        'correct': bool(slot.get('correct')),
                    })
            item['answers'] = answers
            class_work.append(item)

    assignments_created = []
    if teacher is not None and _table_exists(conn, 'class_assignments'):
        assignments_created = _rows(
            conn,
            '''
            SELECT a.id, a.class_id, c.name AS class_name,
                   a.level, a.subject, a.topic, a.mode, a.difficulty,
                   a.question_count, a.created_at,
                   COUNT(r.student_id) AS recipient_count,
                   SUM(CASE WHEN r.status = 'complete' THEN 1 ELSE 0 END) AS complete_count
            FROM class_assignments a
            JOIN classes c ON c.id = a.class_id
            LEFT JOIN class_assignment_recipients r ON r.assignment_id = a.id
            WHERE a.teacher_id = ?
            GROUP BY a.id
            ORDER BY a.created_at
            ''',
            (user_id,),
        )
        teacher['assignments_created'] = assignments_created

    class_invites_received = []
    class_invites_sent = []
    if _table_exists(conn, 'class_invites'):
        class_invites_received = _rows(
            conn,
            '''
            SELECT i.id, i.class_id, c.name AS class_name, u.handle AS teacher_handle,
                   i.status, i.created_at, i.responded_at
            FROM class_invites i
            JOIN classes c ON c.id = i.class_id
            JOIN users u ON u.id = i.teacher_id
            WHERE i.student_id = ?
            ORDER BY i.created_at
            ''',
            (user_id,),
        )
        class_invites_sent = _rows(
            conn,
            '''
            SELECT i.id, i.class_id, c.name AS class_name, u.handle AS student_handle,
                   i.status, i.created_at, i.responded_at
            FROM class_invites i
            JOIN classes c ON c.id = i.class_id
            JOIN users u ON u.id = i.student_id
            WHERE i.teacher_id = ?
            ORDER BY i.created_at
            ''',
            (user_id,),
        )

    class_audit = []
    if teacher is not None and _table_exists(conn, 'class_audit_events'):
        class_audit = _rows(
            conn,
            '''
            SELECT e.id, e.class_id, c.name AS class_name, e.action,
                   e.subject_handle, e.meta_json, e.created_at
            FROM class_audit_events e
            JOIN classes c ON c.id = e.class_id
            WHERE c.teacher_id = ?
            ORDER BY e.id
            ''',
            (user_id,),
        )
        for item in class_audit:
            try:
                meta = json.loads(item.pop('meta_json', None) or '{}')
            except (TypeError, ValueError, json.JSONDecodeError):
                meta = {}
            if not isinstance(meta, dict):
                meta = {}
            item['meta'] = {
                key: value for key, value in meta.items()
                if key in (
                    'name', 'via', 'topic', 'question_count',
                    'recipient_count', 'assignment_id', 'invite_id',
                )
            }
        teacher['class_audit'] = class_audit

    if teacher is not None:
        teacher['invites_sent'] = class_invites_sent

    return {
        'generated_at': utc_now_iso(),
        'schema_version': SCHEMA_VERSION,
        'account': dict(user),
        'settings': settings,
        'practice': practice,
        'social': {
            'following': following,
            'followers': followers,
        },
        'teacher': teacher,
        'classes_joined': classes_joined,
        'class_work': class_work,
        'class_invites_received': class_invites_received,
        'notes': {
            'api_sessions': tokens,
        },
    }
