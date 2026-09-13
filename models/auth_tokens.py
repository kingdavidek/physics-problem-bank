"""Password-reset and email-verification tokens (S0.7)."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from models.user import utc_now_iso

RESET_TTL_MINUTES = 60
VERIFY_TTL_HOURS = 48
TOKEN_BYTES = 32


def _hash_token(raw):
    return hashlib.sha256((raw or '').encode('utf-8')).hexdigest()


def _parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


def create_password_reset_token(conn, user_id):
    raw = secrets.token_urlsafe(TOKEN_BYTES)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(minutes=RESET_TTL_MINUTES)
    conn.execute(
        '''
        INSERT INTO password_reset_tokens (user_id, token_hash, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        ''',
        (user_id, _hash_token(raw), now.isoformat(), expires.isoformat()),
    )
    conn.commit()
    return raw


def invalidate_password_reset_tokens(conn, user_id):
    now = utc_now_iso()
    conn.execute(
        '''
        UPDATE password_reset_tokens
        SET used_at = ?
        WHERE user_id = ? AND used_at IS NULL
        ''',
        (now, user_id),
    )
    conn.commit()


def consume_password_reset_token(conn, raw_token):
    """Return user_id if the token is valid, else None. Marks it used."""
    token_hash = _hash_token(raw_token)
    row = conn.execute(
        '''
        SELECT id, user_id, expires_at, used_at
        FROM password_reset_tokens
        WHERE token_hash = ?
        ''',
        (token_hash,),
    ).fetchone()
    if not row or row['used_at']:
        return None
    expires = _parse_iso(row['expires_at'])
    now = datetime.now(timezone.utc)
    if expires is None or expires < now:
        return None
    conn.execute(
        'UPDATE password_reset_tokens SET used_at = ? WHERE id = ?',
        (utc_now_iso(), row['id']),
    )
    conn.commit()
    return int(row['user_id'])


def peek_password_reset_token(conn, raw_token):
    """True if token exists, unused, and unexpired (does not consume)."""
    token_hash = _hash_token(raw_token)
    row = conn.execute(
        '''
        SELECT expires_at, used_at
        FROM password_reset_tokens
        WHERE token_hash = ?
        ''',
        (token_hash,),
    ).fetchone()
    if not row or row['used_at']:
        return False
    expires = _parse_iso(row['expires_at'])
    now = datetime.now(timezone.utc)
    return expires is not None and expires >= now


def create_email_verification_token(conn, user_id):
    raw = secrets.token_urlsafe(TOKEN_BYTES)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(hours=VERIFY_TTL_HOURS)
    conn.execute(
        '''
        INSERT INTO email_verification_tokens (user_id, token_hash, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        ''',
        (user_id, _hash_token(raw), now.isoformat(), expires.isoformat()),
    )
    conn.commit()
    return raw


def consume_email_verification_token(conn, raw_token):
    token_hash = _hash_token(raw_token)
    row = conn.execute(
        '''
        SELECT id, user_id, expires_at, used_at
        FROM email_verification_tokens
        WHERE token_hash = ?
        ''',
        (token_hash,),
    ).fetchone()
    if not row or row['used_at']:
        return None
    expires = _parse_iso(row['expires_at'])
    now = datetime.now(timezone.utc)
    if expires is None or expires < now:
        return None
    conn.execute(
        'UPDATE email_verification_tokens SET used_at = ? WHERE id = ?',
        (utc_now_iso(), row['id']),
    )
    conn.execute(
        'UPDATE users SET email_verified_at = ? WHERE id = ? AND email_verified_at IS NULL',
        (utc_now_iso(), row['user_id']),
    )
    conn.commit()
    return int(row['user_id'])
