"""User blocks and content reports."""
import json

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


def list_open_reports(conn, limit=100):
    rows = conn.execute(
        '''
        SELECT r.id, r.reporter_id, r.reported_user_id, r.report_type, r.note,
               r.context_json, r.created_at, r.resolved_at,
               reporter.handle AS reporter_handle,
               reported.handle AS reported_handle
        FROM user_reports r
        JOIN users reporter ON reporter.id = r.reporter_id
        LEFT JOIN users reported ON reported.id = r.reported_user_id
        WHERE r.resolved_at IS NULL
        ORDER BY r.created_at ASC
        LIMIT ?
        ''',
        (limit,),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        try:
            item['context'] = json.loads(item.pop('context_json') or '{}')
        except json.JSONDecodeError:
            item['context'] = {}
        out.append(item)
    return out


def resolve_report(conn, report_id):
    cursor = conn.execute(
        '''
        UPDATE user_reports
        SET resolved_at = ?
        WHERE id = ? AND resolved_at IS NULL
        ''',
        (utc_now_iso(), report_id),
    )
    conn.commit()
    return cursor.rowcount > 0

