"""User blocks and content reports."""
from models.user import utc_now_iso

REPORT_TYPES = frozenset({
    'spam',
    'harassment',
    'inappropriate',
    'other',
})
MAX_REPORT_NOTE = 500


def is_blocked(conn, viewer_id, other_id):
    """True if either user has blocked the other."""
    if not viewer_id or not other_id or viewer_id == other_id:
        return False
    row = conn.execute(
        '''
        SELECT 1 FROM user_blocks
        WHERE (blocker_id = ? AND blocked_id = ?)
           OR (blocker_id = ? AND blocked_id = ?)
        LIMIT 1
        ''',
        (viewer_id, other_id, other_id, viewer_id),
    ).fetchone()
    return row is not None


def block_user(conn, blocker_id, blocked_id):
    if blocker_id == blocked_id:
        return False
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT OR IGNORE INTO user_blocks (blocker_id, blocked_id, created_at)
        VALUES (?, ?, ?)
        ''',
        (blocker_id, blocked_id, now),
    )
    # Also remove follow relationships both ways
    conn.execute(
        'DELETE FROM follows WHERE follower_id = ? AND following_id = ?',
        (blocker_id, blocked_id),
    )
    conn.execute(
        'DELETE FROM follows WHERE follower_id = ? AND following_id = ?',
        (blocked_id, blocker_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def unblock_user(conn, blocker_id, blocked_id):
    cursor = conn.execute(
        '''
        DELETE FROM user_blocks
        WHERE blocker_id = ? AND blocked_id = ?
        ''',
        (blocker_id, blocked_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def list_blocked_users(conn, blocker_id, limit=100):
    rows = conn.execute(
        '''
        SELECT u.id, u.handle, b.created_at AS blocked_at
        FROM user_blocks b
        JOIN users u ON u.id = b.blocked_id
        WHERE b.blocker_id = ?
        ORDER BY b.created_at DESC
        LIMIT ?
        ''',
        (blocker_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def create_report(
    conn,
    reporter_id,
    *,
    reported_user_id=None,
    report_type='other',
    note='',
    context=None,
):
    if report_type not in REPORT_TYPES:
        report_type = 'other'
    note = (note or '').strip()[:MAX_REPORT_NOTE]
    import json
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO user_reports (
            reporter_id, reported_user_id, report_type, note, context_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            reporter_id,
            reported_user_id,
            report_type,
            note,
            json.dumps(context or {}),
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid
