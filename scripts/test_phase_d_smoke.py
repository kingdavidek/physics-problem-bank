"""Phase D smoke test — run: python scripts/test_phase_d_smoke.py"""
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def register(client, email, handle):
    r = client.get('/register')
    token = csrf_from(r.data.decode())
    client.post(
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


def generate_problem(client):
    return client.post(
        '/',
        data={
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'bidmas',
            'mode': 'standard',
            'difficulty': 'foundational',
            'action': 'start',
        },
        follow_redirects=True,
    )


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle = f'phd_{suffix}'
        email = f'phd_{suffix}@example.com'

        register(client, email, handle)
        generate_problem(client)

        r = client.get('/profile')
        assert r.status_code == 200
        body = r.data.decode()
        assert 'Day study streak' in body
        assert 'This week' in body

        r = client.get('/api/v1/me/gamification')
        assert r.status_code == 200
        data = r.get_json()
        assert data.get('ok') is True
        assert data['study_streak']['current'] >= 1
        assert data['weekly_recap']['active_days'] >= 1

        r = client.get('/leaderboard/friends')
        assert r.status_code == 200
        assert b'Friend effort leaderboard' in r.data

        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        r = client.get(f'/u/{handle}')
        assert r.status_code == 200
        assert 'Study streak' not in r.data.decode()  # hidden by default when not owner

    print('Phase D smoke tests passed.')


if __name__ == '__main__':
    main()
