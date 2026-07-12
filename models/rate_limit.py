"""Simple daily rate-limit buckets for API actions."""
from datetime import date

from models.user import utc_now_iso


def check_and_increment_rate_limit(conn, bucket_key, limit, window_day=None):
    """
    Increment a daily bucket and return (allowed, remaining, count).

    ``limit`` is the max allowed actions for the day (inclusive).
    """
    day = window_day or date.today().isoformat()
    row = conn.execute(
        '''
        SELECT count FROM rate_limit_buckets
        WHERE bucket_key = ? AND window_start = ?
        ''',
        (bucket_key, day),
    ).fetchone()
    count = int(row['count']) if row else 0
    if count >= limit:
        return False, 0, count

    if row:
        conn.execute(
            '''
            UPDATE rate_limit_buckets
            SET count = count + 1
            WHERE bucket_key = ? AND window_start = ?
            ''',
            (bucket_key, day),
        )
        count += 1
    else:
        conn.execute(
            '''
            INSERT INTO rate_limit_buckets (bucket_key, window_start, count, updated_at)
            VALUES (?, ?, 1, ?)
            ''',
            (bucket_key, day, utc_now_iso()),
        )
        count = 1
    conn.commit()
    remaining = max(0, limit - count)
    return True, remaining, count


def get_rate_limit_count(conn, bucket_key, window_day=None):
    day = window_day or date.today().isoformat()
    row = conn.execute(
        '''
        SELECT count FROM rate_limit_buckets
        WHERE bucket_key = ? AND window_start = ?
        ''',
        (bucket_key, day),
    ).fetchone()
    return int(row['count']) if row else 0
