import json

from models.social import (
    VISIBILITY_CHOICES,
    VISIBILITY_FOLLOWERS,
    VISIBILITY_PUBLIC,
    can_view_profile,
    get_profile_settings,
    is_following,
)
from models.user import utc_now_iso

MAX_SHARED_QUESTIONS = 200
MAX_SUGGESTIONS_INBOX = 100
MAX_NOTE_LEN = 200

SUGGESTION_PENDING = 'pending'
SUGGESTION_OPENED = 'opened'
SUGGESTION_DISMISSED = 'dismissed'


def _normalize_visibility(value):
    if value in VISIBILITY_CHOICES:
        return value
    return VISIBILITY_FOLLOWERS


def _normalize_note(note):
    return (note or '').strip()[:MAX_NOTE_LEN]


def can_view_share(conn, viewer_id, owner_id, visibility):
    if viewer_id and viewer_id == owner_id:
        return True
    if visibility == VISIBILITY_PUBLIC:
        return True
    if visibility == VISIBILITY_FOLLOWERS:
        return is_following(conn, viewer_id, owner_id)
    settings = get_profile_settings(conn, owner_id)
    return can_view_profile(conn, viewer_id, owner_id, settings)


def create_shared_question(
    conn,
    user_id,
    level,
    subject,
    topic,
    mode,
    difficulty,
    problem,
    *,
    visibility=VISIBILITY_FOLLOWERS,
    note='',
):
    count = conn.execute(
        'SELECT COUNT(*) AS n FROM shared_questions WHERE user_id = ?',
        (user_id,),
    ).fetchone()['n']
    if count >= MAX_SHARED_QUESTIONS:
        raise ValueError('share_limit')

    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO shared_questions (
            user_id, level, subject, topic, mode, difficulty,
            problem_json, visibility, note, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            level,
            subject,
            topic,
            mode,
            difficulty,
            json.dumps(problem),
            _normalize_visibility(visibility),
            _normalize_note(note),
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_shared_question(conn, share_id):
    row = conn.execute(
        '''
        SELECT s.id, s.user_id, s.level, s.subject, s.topic, s.mode, s.difficulty,
               s.problem_json, s.visibility, s.note, s.created_at,
               u.handle AS owner_handle
        FROM shared_questions s
        JOIN users u ON u.id = s.user_id
        WHERE s.id = ?
        ''',
        (share_id,),
    ).fetchone()
    return _shared_row(row) if row else None


def list_shared_questions(conn, user_id, limit=20):
    rows = conn.execute(
        '''
        SELECT id, user_id, level, subject, topic, mode, difficulty,
               problem_json, visibility, note, created_at
        FROM shared_questions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [_shared_row(row) for row in rows]


def create_suggestion(
    conn,
    sender_id,
    recipient_id,
    level,
    subject,
    topic,
    mode,
    difficulty,
    problem,
    *,
    note='',
):
    if sender_id == recipient_id:
        raise ValueError('self_suggest')

    pending = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM question_suggestions
        WHERE recipient_id = ? AND status = ?
        ''',
        (recipient_id, SUGGESTION_PENDING),
    ).fetchone()['n']
    if pending >= MAX_SUGGESTIONS_INBOX:
        raise ValueError('inbox_limit')

    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO question_suggestions (
            sender_id, recipient_id, level, subject, topic, mode, difficulty,
            problem_json, note, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            sender_id,
            recipient_id,
            level,
            subject,
            topic,
            mode,
            difficulty,
            json.dumps(problem),
            _normalize_note(note),
            SUGGESTION_PENDING,
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def count_pending_suggestions(conn, recipient_id):
    row = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM question_suggestions
        WHERE recipient_id = ? AND status = ?
        ''',
        (recipient_id, SUGGESTION_PENDING),
    ).fetchone()
    return row['n'] if row else 0


def list_suggestions_inbox(conn, recipient_id, *, status=None, limit=50):
    sql = '''
        SELECT s.id, s.sender_id, s.recipient_id, s.level, s.subject, s.topic,
               s.mode, s.difficulty, s.problem_json, s.note, s.status,
               s.created_at, s.read_at, u.handle AS sender_handle
        FROM question_suggestions s
        JOIN users u ON u.id = s.sender_id
        WHERE s.recipient_id = ?
    '''
    params = [recipient_id]
    if status:
        sql += ' AND s.status = ?'
        params.append(status)
    sql += ' ORDER BY s.created_at DESC LIMIT ?'
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [_suggestion_row(row) for row in rows]


def get_suggestion(conn, suggestion_id, *, recipient_id=None, sender_id=None):
    sql = '''
        SELECT s.id, s.sender_id, s.recipient_id, s.level, s.subject, s.topic,
               s.mode, s.difficulty, s.problem_json, s.note, s.status,
               s.created_at, s.read_at,
               sender.handle AS sender_handle,
               recipient.handle AS recipient_handle
        FROM question_suggestions s
        JOIN users sender ON sender.id = s.sender_id
        JOIN users recipient ON recipient.id = s.recipient_id
        WHERE s.id = ?
    '''
    params = [suggestion_id]
    if recipient_id is not None:
        sql += ' AND s.recipient_id = ?'
        params.append(recipient_id)
    if sender_id is not None:
        sql += ' AND s.sender_id = ?'
        params.append(sender_id)
    row = conn.execute(sql, params).fetchone()
    return _suggestion_row(row) if row else None


def mark_suggestion_opened(conn, suggestion_id, recipient_id):
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        UPDATE question_suggestions
        SET status = ?, read_at = COALESCE(read_at, ?)
        WHERE id = ? AND recipient_id = ? AND status != ?
        ''',
        (SUGGESTION_OPENED, now, suggestion_id, recipient_id, SUGGESTION_DISMISSED),
    )
    conn.commit()
    return cursor.rowcount > 0


def dismiss_suggestion(conn, suggestion_id, recipient_id):
    cursor = conn.execute(
        '''
        UPDATE question_suggestions
        SET status = ?
        WHERE id = ? AND recipient_id = ?
        ''',
        (SUGGESTION_DISMISSED, suggestion_id, recipient_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def _shared_row(row):
    if row is None:
        return None
    data = dict(row)
    data['problem'] = json.loads(data.pop('problem_json'))
    return data


def _suggestion_row(row):
    if row is None:
        return None
    data = dict(row)
    data['problem'] = json.loads(data.pop('problem_json'))
    return data
