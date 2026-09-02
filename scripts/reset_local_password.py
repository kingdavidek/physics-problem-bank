"""Reset a local user's password (development only).

Usage:
  PB_ALLOW_DEV_SECRET=1 python scripts/reset_local_password.py EMAIL NEW_PASSWORD

Refuses to run without PB_ALLOW_DEV_SECRET=1 or PB_TESTING=1.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Never reset against ephemeral smoke DB unless PB_TESTING was explicitly requested.
if os.environ.get('PB_TESTING') == '1' and '--testing-db' not in sys.argv:
    os.environ.pop('PB_TESTING', None)
    os.environ.pop('PB_TEST_DB_PATH', None)

from werkzeug.security import generate_password_hash

from app import get_db, _db_path  # noqa: E402
from models.user import User, normalize_email  # noqa: E402


def _local_dev_allowed() -> bool:
    return (
        os.environ.get('PB_ALLOW_DEV_SECRET', '').strip() in ('1', 'true', 'True')
        or os.environ.get('PB_TESTING') == '1'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Reset a local Problem Bank password.')
    parser.add_argument('email', help='Account email')
    parser.add_argument('password', help='New password (min 8 characters)')
    args = parser.parse_args()

    if not _local_dev_allowed():
        print(
            'Refusing: set PB_ALLOW_DEV_SECRET=1 in .env (local dev only).',
            file=sys.stderr,
        )
        return 1

    email = normalize_email(args.email)
    password = args.password or ''
    if len(password) < 8:
        print('Password must be at least 8 characters.', file=sys.stderr)
        return 1

    db_path = _db_path()
    print(f'Database: {db_path}')

    with get_db() as conn:
        user = User.get_by_email(conn, email)
        if not user:
            print(f'No user for email {email}', file=sys.stderr)
            return 1
        password_hash = generate_password_hash(password)
        conn.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (password_hash, user.id),
        )
        conn.commit()

    print(f'Password updated for {email} (@{user.handle}).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
