"""Retention prune job (S0.6 / SECURITY_AND_GDPR.md §4)."""
from datetime import datetime, timedelta, timezone

from models.account_deletion import delete_user_account
from models.user import utc_now_iso

INACTIVE_WARN_MONTHS = 24
INACTIVE_DELETE_MONTHS = 30


def _parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


def _days_ago(days):
    return (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()


def _months_ago(months):
    return datetime.now(timezone.utc) - timedelta(days=int(months * 30.44))


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return bool(row)


def prune_expired_data(conn, *, now=None, delete_inactive=True):
    """Delete expired operational data. Returns counts per table."""
    now = now or datetime.now(timezone.utc)
    counts = {}

    if _table_exists(conn, 'rate_limit_buckets'):
        cutoff = (now - timedelta(days=7)).date().isoformat()
        counts['rate_limit_buckets'] = conn.execute(
            'DELETE FROM rate_limit_buckets WHERE window_start < ?',
            (cutoff,),
        ).rowcount

    if _table_exists(conn, 'lesson_assist_usage'):
        cutoff = (now - timedelta(days=30)).date().isoformat()
        counts['lesson_assist_usage'] = conn.execute(
            'DELETE FROM lesson_assist_usage WHERE day < ?',
            (cutoff,),
        ).rowcount

    if _table_exists(conn, 'quicktest_sessions'):
        cutoff_dt = now - timedelta(days=7)
        deleted = 0
        rows = conn.execute('SELECT session_id, data FROM quicktest_sessions').fetchall()
        import json
        for row in rows:
            stamp = None
            try:
                payload = json.loads(row['data'] or '{}')
                stamp = _parse_iso(payload.get('updated_at') or payload.get('created_at'))
            except (TypeError, json.JSONDecodeError):
                stamp = None
            if stamp is None or stamp < cutoff_dt:
                conn.execute(
                    'DELETE FROM quicktest_sessions WHERE session_id = ?',
                    (row['session_id'],),
                )
                deleted += 1
        counts['quicktest_sessions'] = deleted

    if _table_exists(conn, 'email_digest_log'):
        cutoff = (now - timedelta(days=365)).isoformat()
        counts['email_digest_log'] = conn.execute(
            'DELETE FROM email_digest_log WHERE sent_at < ?',
            (cutoff,),
        ).rowcount

    if _table_exists(conn, 'user_reports'):
        cutoff = (now - timedelta(days=365)).isoformat()
        counts['user_reports'] = conn.execute(
            '''
            DELETE FROM user_reports
            WHERE resolved_at IS NOT NULL AND resolved_at < ?
            ''',
            (cutoff,),
        ).rowcount

    if _table_exists(conn, 'api_tokens'):
        cutoff = (now - timedelta(days=30)).isoformat()
        counts['api_tokens'] = conn.execute(
            'DELETE FROM api_tokens WHERE expires_at IS NOT NULL AND expires_at < ?',
            (cutoff,),
        ).rowcount

    if _table_exists(conn, 'password_reset_tokens'):
        cutoff = (now - timedelta(hours=24)).isoformat()
        counts['password_reset_tokens'] = conn.execute(
            'DELETE FROM password_reset_tokens WHERE expires_at < ?',
            (cutoff,),
        ).rowcount

    if _table_exists(conn, 'email_verification_tokens'):
        cutoff = (now - timedelta(hours=24)).isoformat()
        counts['email_verification_tokens'] = conn.execute(
            'DELETE FROM email_verification_tokens WHERE expires_at < ?',
            (cutoff,),
        ).rowcount

    if _table_exists(conn, 'deleted_handles'):
        cutoff = (now - timedelta(days=90)).isoformat()
        counts['deleted_handles'] = conn.execute(
            'DELETE FROM deleted_handles WHERE deleted_at < ?',
            (cutoff,),
        ).rowcount

    inactive_deleted = 0
    inactive_warned = 0
    if delete_inactive and _table_exists(conn, 'users'):
        warn_before = _months_ago(INACTIVE_WARN_MONTHS).isoformat()
        delete_before = _months_ago(INACTIVE_DELETE_MONTHS).isoformat()
        rows = conn.execute(
            '''
            SELECT id, last_login_at, created_at FROM users
            WHERE is_active = 1
            '''
        ).fetchall()
        for row in rows:
            last = row['last_login_at'] or row['created_at']
            if not last:
                continue
            if last < delete_before:
                delete_user_account(conn, row['id'])
                inactive_deleted += 1
            elif last < warn_before:
                inactive_warned += 1
    counts['inactive_accounts_deleted'] = inactive_deleted
    counts['inactive_accounts_warned'] = inactive_warned
    counts['ran_at'] = utc_now_iso()
    conn.commit()
    return counts
