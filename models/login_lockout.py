"""Per-account login lockout (S1.6)."""
from datetime import datetime, timedelta, timezone

from models.user import utc_now_iso

LOCKOUT_THRESHOLD = 10
LOCKOUT_MINUTES = 15


def _parse_iso(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def is_login_locked(conn, user_id, *, now=None):
    now = now or datetime.now(timezone.utc)
    row = conn.execute(
        'SELECT fail_count, locked_until FROM login_lockouts WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    if not row:
        return False
    locked_until = _parse_iso(row['locked_until'])
    if locked_until and locked_until > now:
        return True
    if locked_until and locked_until <= now:
        clear_login_failures(conn, user_id)
    return False


def record_login_failure(conn, user_id, *, now=None, threshold=LOCKOUT_THRESHOLD, lock_minutes=LOCKOUT_MINUTES):
    """Increment failures. Returns True if the account is now locked."""
    now = now or datetime.now(timezone.utc)
    row = conn.execute(
        'SELECT fail_count, locked_until FROM login_lockouts WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    locked_until = _parse_iso(row['locked_until']) if row else None
    if locked_until and locked_until > now:
        return True
    count = int(row['fail_count']) + 1 if row else 1
    lock_stamp = None
    if count >= threshold:
        lock_stamp = (now + timedelta(minutes=lock_minutes)).isoformat()
        count = threshold
    conn.execute(
        '''
        INSERT INTO login_lockouts (user_id, fail_count, locked_until, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            fail_count = excluded.fail_count,
            locked_until = excluded.locked_until,
            updated_at = excluded.updated_at
        ''',
        (user_id, count, lock_stamp, utc_now_iso()),
    )
    conn.commit()
    return lock_stamp is not None


def clear_login_failures(conn, user_id):
    conn.execute('DELETE FROM login_lockouts WHERE user_id = ?', (user_id,))
    conn.commit()
