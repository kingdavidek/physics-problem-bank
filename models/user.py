import re
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

_HANDLE_RE = re.compile(r'^[a-z0-9_]{3,20}$')
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

RESERVED_HANDLES = frozenset({
    'admin', 'administrator', 'api', 'app', 'help', 'login', 'logout',
    'moderator', 'profile', 'register', 'root', 'settings', 'signup',
    'support', 'system', 'topics', 'user', 'users', 'www',
})


def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class User(UserMixin):
    def __init__(self, id, email, handle, password_hash, created_at, last_login_at, is_active):
        self.id = id
        self.email = email
        self.handle = handle
        self.password_hash = password_hash
        self.created_at = created_at
        self.last_login_at = last_login_at
        self._is_active = bool(is_active)

    @property
    def is_active(self):
        return self._is_active

    @property
    def display_handle(self):
        return f'@{self.handle}'

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            email=row['email'],
            handle=row['handle'],
            password_hash=row['password_hash'],
            created_at=row['created_at'],
            last_login_at=row['last_login_at'],
            is_active=row['is_active'],
        )

    @classmethod
    def get_by_id(cls, conn, user_id):
        row = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,),
        ).fetchone()
        return cls.from_row(row)

    @classmethod
    def get_by_email(cls, conn, email):
        row = conn.execute(
            'SELECT * FROM users WHERE email = ? COLLATE NOCASE',
            (email.strip(),),
        ).fetchone()
        return cls.from_row(row)

    @classmethod
    def get_by_handle(cls, conn, handle):
        row = conn.execute(
            'SELECT * FROM users WHERE handle = ? COLLATE NOCASE',
            (normalize_handle(handle),),
        ).fetchone()
        return cls.from_row(row)

    @classmethod
    def create(cls, conn, email, handle, password):
        email = normalize_email(email)
        handle = normalize_handle(handle)
        now = utc_now_iso()
        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            '''
            INSERT INTO users (email, handle, password_hash, created_at, last_login_at, is_active)
            VALUES (?, ?, ?, ?, NULL, 1)
            ''',
            (email, handle, password_hash, now),
        )
        conn.commit()
        return cls.get_by_id(conn, cursor.lastrowid)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def touch_login(self, conn):
        now = utc_now_iso()
        conn.execute(
            'UPDATE users SET last_login_at = ? WHERE id = ?',
            (now, self.id),
        )
        conn.commit()
        self.last_login_at = now


def normalize_email(email):
    return (email or '').strip().lower()


def normalize_handle(handle):
    value = (handle or '').strip().lower()
    if value.startswith('@'):
        value = value[1:]
    return value


def validate_email(email):
    email = normalize_email(email)
    if not email:
        return 'Email is required.'
    if len(email) > 254:
        return 'Email is too long.'
    if not _EMAIL_RE.match(email):
        return 'Enter a valid email address.'
    return None


def validate_handle(handle):
    handle = normalize_handle(handle)
    if not handle:
        return 'Handle is required.'
    if not _HANDLE_RE.match(handle):
        return 'Handle must be 3–20 characters: lowercase letters, numbers, and underscores only.'
    if handle in RESERVED_HANDLES:
        return 'That handle is reserved. Please choose another.'
    return None


def validate_password(password):
    if not password:
        return 'Password is required.'
    if len(password) < 8:
        return 'Password must be at least 8 characters.'
    if len(password) > 128:
        return 'Password is too long.'
    return None


def can_access_difficulty(user, difficulty):
    """Stub for future gating — difficult questions require a logged-in account."""
    if difficulty != 'difficult':
        return True
    return user is not None and getattr(user, 'is_authenticated', False)
