"""Atomic daily rate-limit buckets for API actions."""
from datetime import datetime, timezone

from models.user import utc_now_iso


def utc_today_iso():
    return datetime.now(timezone.utc).date().isoformat()


def check_and_increment_rate_limit(conn, bucket_key, limit, window_day=None):
    """
    Increment a daily bucket and return (allowed, remaining, count).

    ``limit`` is the max allowed actions for the day (inclusive).
    Uses an atomic upsert so concurrent requests cannot overrun the limit.
    """
    day = window_day or utc_today_iso()
    now = utc_now_iso()
    cur = conn.execute(
        '''
        INSERT INTO rate_limit_buckets (bucket_key, window_start, count, updated_at)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(bucket_key, window_start) DO UPDATE SET
            count = count + 1,
            updated_at = excluded.updated_at
        WHERE rate_limit_buckets.count < ?
        ''',
        (bucket_key, day, now, limit),
    )
    changed = cur.rowcount
    row = conn.execute(
        '''
        SELECT count FROM rate_limit_buckets
        WHERE bucket_key = ? AND window_start = ?
        ''',
        (bucket_key, day),
    ).fetchone()
    count = int(row['count']) if row else 0
    conn.commit()
    if changed == 0:
        return False, 0, count
    remaining = max(0, limit - count)
    return True, remaining, count


def get_rate_limit_count(conn, bucket_key, window_day=None):
    day = window_day or utc_today_iso()
    row = conn.execute(
        '''
        SELECT count FROM rate_limit_buckets
        WHERE bucket_key = ? AND window_start = ?
        ''',
        (bucket_key, day),
    ).fetchone()
    return int(row['count']) if row else 0
