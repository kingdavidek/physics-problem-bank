"""API bearer tokens for native/mobile clients."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from models.user import utc_now_iso

TOKEN_PREFIX = 'pb_'
TOKEN_LABEL_MAX = 64
TOKEN_TOUCH_INTERVAL = timedelta(minutes=15)


def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()


def create_api_token(conn, user_id, label='', expires_at=None):
    """Create a token; returns (raw_token, token_id). Raw token is shown once."""
    raw = TOKEN_PREFIX + secrets.token_urlsafe(32)
    token_hash = _hash_token(raw)
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO api_tokens (user_id, token_hash, label, created_at, last_used_at, expires_at)
        VALUES (?, ?, ?, ?, NULL, ?)
        ''',
        (user_id, token_hash, (label or '').strip()[:TOKEN_LABEL_MAX], now, expires_at),
    )
    conn.commit()
    return raw, cursor.lastrowid


def get_token_row_by_raw(conn, raw_token):
    if not raw_token or not raw_token.startswith(TOKEN_PREFIX):
        return None
    row = conn.execute(
        'SELECT * FROM api_tokens WHERE token_hash = ?',
        (_hash_token(raw_token),),
    ).fetchone()
    if not row:
        return None
    expires_at = row['expires_at']
    if expires_at:
        try:
            expires = datetime.fromisoformat(expires_at)
        except ValueError:
            return None
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            return None
    return row


def _should_touch_last_used(last_used_at):
    if not last_used_at:
        return True
    try:
        prev = datetime.fromisoformat(last_used_at)
    except ValueError:
        return True
    if prev.tzinfo is None:
        prev = prev.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - prev >= TOKEN_TOUCH_INTERVAL


def touch_token_use(conn, token_id, last_used_at=None):
    if not _should_touch_last_used(last_used_at):
        return
    conn.execute(
        'UPDATE api_tokens SET last_used_at = ? WHERE id = ?',
        (utc_now_iso(), token_id),
    )
    conn.commit()


def revoke_token_by_raw(conn, raw_token):
    row = get_token_row_by_raw(conn, raw_token)
    if not row:
        return False
    conn.execute('DELETE FROM api_tokens WHERE id = ?', (row['id'],))
    conn.commit()
    return True


def revoke_all_tokens(conn, user_id, except_token_id=None):
    if except_token_id is not None:
        conn.execute(
            'DELETE FROM api_tokens WHERE user_id = ? AND id != ?',
            (user_id, except_token_id),
        )
    else:
        conn.execute(
            'DELETE FROM api_tokens WHERE user_id = ?',
            (user_id,),
        )
    conn.commit()


def list_user_tokens(conn, user_id):
    rows = conn.execute(
        '''
        SELECT id, label, created_at, last_used_at, expires_at
        FROM api_tokens
        WHERE user_id = ?
        ORDER BY created_at DESC
        ''',
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]
