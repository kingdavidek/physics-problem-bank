"""Per-account login lockout smoke — run: python scripts/test_login_lockout_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ['SITE_URL'] = 'http://127.0.0.1:5000'
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-lockout-smoke')

from app import app, get_db  # noqa: E402
from models.login_lockout import (  # noqa: E402
    LOCKOUT_THRESHOLD,
    clear_login_failures,
    is_login_locked,
    record_login_failure,
)


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        email = f'lk_{suffix}@example.com'
        handle = f'lk_{suffix}'
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'handle': handle,
                'password': 'password123',
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        uid = r.get_json()['user']['id']

        with get_db() as conn:
            for _ in range(LOCKOUT_THRESHOLD - 1):
                locked = record_login_failure(conn, uid)
                assert locked is False
            assert is_login_locked(conn, uid) is False
            assert record_login_failure(conn, uid) is True
            assert is_login_locked(conn, uid) is True

        r = client.post(
            '/api/v1/auth/login',
            json={'email': email, 'password': 'password123'},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 401, r.data
        assert r.get_json()['error'] == 'Invalid email or password'

        r = client.post(
            '/login',
            data={'email': email, 'password': 'password123', 'csrf_token': 'x'},
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert b'Invalid email or password' in r.data

        with get_db() as conn:
            clear_login_failures(conn, uid)
            assert is_login_locked(conn, uid) is False

        r = client.post(
            '/api/v1/auth/login',
            json={'email': email, 'password': 'password123'},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['ok'] is True

    print('Login lockout smoke tests passed.')


if __name__ == '__main__':
    main()
