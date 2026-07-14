"""Study pairs — one mutual accountability buddy (no chat)."""
from datetime import date, timedelta

from models.user import utc_now_iso

PAIR_PENDING = 'pending'
PAIR_ACTIVE = 'active'
PAIR_DECLINED = 'declined'
PAIR_ENDED = 'ended'

MAX_ACTIVE_PAIRS = 1


def _ordered_pair(user_a_id, user_b_id):
    a, b = int(user_a_id), int(user_b_id)
    if a == b:
        raise ValueError('self_pair')
    return (a, b) if a < b else (b, a)


def invite_study_pair(conn, from_user_id, to_user_id):
    if from_user_id == to_user_id:
        raise ValueError('self_pair')

    active = get_active_study_pair(conn, from_user_id)
    if active:
        raise ValueError('already_paired')

    active = get_active_study_pair(conn, to_user_id)
    if active:
        raise ValueError('target_paired')

    pending_out = conn.execute(
        '''
        SELECT id FROM study_pairs
        WHERE invited_by_id = ? AND status = ?
        ''',
        (from_user_id, PAIR_PENDING),
    ).fetchone()
    if pending_out:
        raise ValueError('pending_outgoing')

    pending_in = conn.execute(
        '''
        SELECT id FROM study_pairs
        WHERE to_user_id = ? AND status = ?
        ''',
        (from_user_id, PAIR_PENDING),
    ).fetchone()
    if pending_in:
        raise ValueError('pending_incoming')

    low, high = _ordered_pair(from_user_id, to_user_id)
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO study_pairs (
            user_low_id, user_high_id, invited_by_id, to_user_id,
            status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (low, high, from_user_id, to_user_id, PAIR_PENDING, now),
    )
    conn.commit()
    return cursor.lastrowid


def get_study_pair_row(conn, pair_id):
    row = conn.execute(
        '''
        SELECT p.*,
               u1.handle AS user_low_handle,
               u2.handle AS user_high_handle,
               inv.handle AS invited_by_handle
        FROM study_pairs p
        JOIN users u1 ON u1.id = p.user_low_id
        JOIN users u2 ON u2.id = p.user_high_id
        JOIN users inv ON inv.id = p.invited_by_id
        WHERE p.id = ?
        ''',
        (pair_id,),
    ).fetchone()
    return dict(row) if row else None


def accept_study_pair(conn, pair_id, user_id):
    row = get_study_pair_row(conn, pair_id)
    if not row or row['status'] != PAIR_PENDING or row['to_user_id'] != user_id:
        return None
    if get_active_study_pair(conn, user_id):
        raise ValueError('already_paired')
    other_id = row['user_low_id'] if row['user_high_id'] == user_id else row['user_high_id']
    if get_active_study_pair(conn, other_id):
        raise ValueError('target_paired')
    now = utc_now_iso()
    conn.execute(
        '''
        UPDATE study_pairs
        SET status = ?, activated_at = ?
        WHERE id = ?
        ''',
        (PAIR_ACTIVE, now, pair_id),
    )
    conn.commit()
    return get_study_pair_row(conn, pair_id)


def decline_study_pair(conn, pair_id, user_id):
    row = get_study_pair_row(conn, pair_id)
    if not row or row['status'] != PAIR_PENDING or row['to_user_id'] != user_id:
        return False
    conn.execute(
        'UPDATE study_pairs SET status = ? WHERE id = ?',
        (PAIR_DECLINED, pair_id),
    )
    conn.commit()
    return True


def end_study_pair(conn, user_id):
    row = conn.execute(
        '''
        SELECT id FROM study_pairs
        WHERE status = ? AND (user_low_id = ? OR user_high_id = ?)
        ''',
        (PAIR_ACTIVE, user_id, user_id),
    ).fetchone()
    if not row:
        return False
    conn.execute(
        'UPDATE study_pairs SET status = ?, ended_at = ? WHERE id = ?',
        (PAIR_ENDED, utc_now_iso(), row['id']),
    )
    conn.commit()
    return True


def get_active_study_pair(conn, user_id):
    row = conn.execute(
        '''
        SELECT p.*,
               u1.handle AS user_low_handle,
               u2.handle AS user_high_handle
        FROM study_pairs p
        JOIN users u1 ON u1.id = p.user_low_id
        JOIN users u2 ON u2.id = p.user_high_id
        WHERE p.status = ?
          AND (p.user_low_id = ? OR p.user_high_id = ?)
        ORDER BY p.activated_at DESC
        LIMIT 1
        ''',
        (PAIR_ACTIVE, user_id, user_id),
    ).fetchone()
    if not row:
        return None
    data = dict(row)
    data['buddy_id'] = (
        data['user_high_id'] if data['user_low_id'] == user_id else data['user_low_id']
    )
    data['buddy_handle'] = (
        data['user_high_handle'] if data['user_low_id'] == user_id else data['user_low_handle']
    )
    return data


def list_pending_study_pair_invites(conn, user_id):
    rows = conn.execute(
        '''
        SELECT p.*, inv.handle AS invited_by_handle
        FROM study_pairs p
        JOIN users inv ON inv.id = p.invited_by_id
        WHERE p.to_user_id = ? AND p.status = ?
        ORDER BY p.created_at DESC
        ''',
        (user_id, PAIR_PENDING),
    ).fetchall()
    return [dict(row) for row in rows]


def buddy_weekly_recap(conn, user_id, days=7):
    """Shared practice summary for an active study pair."""
    pair = get_active_study_pair(conn, user_id)
    if not pair:
        return None

    buddy_id = pair['buddy_id']
    start_day = (date.today() - timedelta(days=days - 1)).isoformat()

    def _active_days(uid):
        row = conn.execute(
            '''
            SELECT COUNT(*) AS n FROM user_study_days
            WHERE user_id = ? AND study_date >= ?
            ''',
            (uid, start_day),
        ).fetchone()
        return row['n'] if row else 0

    def _topic_keys(uid):
        rows = conn.execute(
            '''
            SELECT DISTINCT
                json_extract(payload_json, '$.level') || '|' ||
                json_extract(payload_json, '$.subject') || '|' ||
                json_extract(payload_json, '$.topic') AS key
            FROM user_activity_events
            WHERE user_id = ?
              AND created_at >= ?
              AND json_extract(payload_json, '$.topic') IS NOT NULL
            ''',
            (uid, f'{start_day}T00:00:00'),
        ).fetchall()
        return {row['key'] for row in rows if row['key']}

    your_topics = _topic_keys(user_id)
    buddy_topics = _topic_keys(buddy_id)
    shared = your_topics & buddy_topics

    return {
        'buddy_handle': pair['buddy_handle'],
        'days': days,
        'your_active_days': _active_days(user_id),
        'buddy_active_days': _active_days(buddy_id),
        'your_topics': len(your_topics),
        'buddy_topics': len(buddy_topics),
        'shared_topics': len(shared),
    }


def serialize_study_pair(pair, viewer_id):
    if not pair:
        return None
    buddy_id = pair.get('buddy_id')
    if not buddy_id:
        buddy_id = (
            pair['user_high_id'] if pair['user_low_id'] == viewer_id else pair['user_low_id']
        )
    buddy_handle = pair.get('buddy_handle')
    if not buddy_handle:
        buddy_handle = (
            pair['user_high_handle']
            if pair['user_low_id'] == viewer_id
            else pair['user_low_handle']
        )
    return {
        'id': pair['id'],
        'status': pair['status'],
        'buddy_id': buddy_id,
        'buddy_handle': buddy_handle,
        'invited_by_id': pair.get('invited_by_id'),
        'to_user_id': pair.get('to_user_id'),
        'created_at': pair.get('created_at'),
        'activated_at': pair.get('activated_at'),
    }
