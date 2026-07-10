"""Quick auth smoke test — run: python scripts/test_auth_smoke.py"""
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402
from models.user import can_access_difficulty  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def main():
    assert can_access_difficulty(None, 'difficult') is False
    assert can_access_difficulty(None, 'intermediate') is True

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        email = f'smoke_{suffix}@example.com'
        handle = f'smoke_{suffix}'

        r = client.get('/register')
        assert r.status_code == 200
        token = csrf_from(r.data.decode())

        r = client.post(
            '/register',
            data={
                'csrf_token': token,
                'email': email,
                'handle': handle,
                'password': 'password123',
                'confirm_password': 'password123',
                'age_confirm': '1',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data[:500]
        assert f'@{handle}'.encode() in r.data

        r = client.get('/profile')
        token = csrf_from(r.data.decode())
        client.post('/logout', data={'csrf_token': token})

        r = client.get('/login')
        token = csrf_from(r.data.decode())
        r = client.post(
            '/login',
            data={
                'csrf_token': token,
                'email': email,
                'password': 'password123',
                'remember': '1',
            },
            follow_redirects=True,
        )
        assert f'@{handle}'.encode() in r.data

        r = client.get('/profile')
        token = csrf_from(r.data.decode())
        client.post('/logout', data={'csrf_token': token})

        r = client.post(
            '/',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'standard',
                'difficulty': 'difficult',
                'action': 'start',
            },
        )
        assert b'Difficult questions require' in r.data

    print('Auth smoke tests passed.')


if __name__ == '__main__':
    main()
