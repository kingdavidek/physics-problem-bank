import json

from models.user import utc_now_iso

NOTIFICATION_SUGGESTION = 'suggestion_received'
NOTIFICATION_FOLLOW = 'new_follower'
NOTIFICATION_CHALLENGE = 'challenge_received'
NOTIFICATION_CHALLENGE_COMPLETE = 'challenge_complete'
NOTIFICATION_STUDY_PAIR = 'study_pair_invite'


def create_notification(conn, user_id, notification_type, payload):
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO user_notifications (
            user_id, notification_type, payload_json, created_at
        ) VALUES (?, ?, ?, ?)
        ''',
        (user_id, notification_type, json.dumps(payload or {}), now),
    )
    conn.commit()
    return cursor.lastrowid


def count_unread_notifications(conn, user_id):
    row = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM user_notifications
        WHERE user_id = ? AND read_at IS NULL
        ''',
        (user_id,),
    ).fetchone()
    return row['n'] if row else 0


def list_notifications(conn, user_id, limit=20, before_id=None):
    params = [user_id]
    before_clause = ''
    if before_id is not None:
        before_clause = 'AND id < ?'
        params.append(int(before_id))
    params.append(limit)
    rows = conn.execute(
        f'''
        SELECT id, notification_type, payload_json, read_at, created_at
        FROM user_notifications
        WHERE user_id = ?
        {before_clause}
        ORDER BY id DESC
        LIMIT ?
        ''',
        params,
    ).fetchall()
    out = []
    for row in rows:
        data = dict(row)
        raw = data.pop('payload_json', None) or '{}'
        try:
            data['payload'] = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            data['payload'] = {}
        out.append(data)
    return out


def mark_notification_read(conn, user_id, notification_id):
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        UPDATE user_notifications
        SET read_at = ?
        WHERE id = ? AND user_id = ? AND read_at IS NULL
        ''',
        (now, notification_id, user_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def mark_all_notifications_read(conn, user_id):
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        UPDATE user_notifications
        SET read_at = ?
        WHERE user_id = ? AND read_at IS NULL
        ''',
        (now, user_id),
    )
    conn.commit()
    return cursor.rowcount


def mark_suggestion_notifications_read(conn, user_id, suggestion_id):
    rows = conn.execute(
        '''
        SELECT id, payload_json FROM user_notifications
        WHERE user_id = ? AND notification_type = ? AND read_at IS NULL
        ''',
        (user_id, NOTIFICATION_SUGGESTION),
    ).fetchall()
    now = utc_now_iso()
    marked = 0
    for row in rows:
        try:
            payload = json.loads(row['payload_json'] or '{}')
        except (TypeError, ValueError, json.JSONDecodeError):
            payload = {}
        if payload.get('suggestion_id') == suggestion_id:
            conn.execute(
                'UPDATE user_notifications SET read_at = ? WHERE id = ?',
                (now, row['id']),
            )
            marked += 1
    if marked:
        conn.commit()
    return marked
