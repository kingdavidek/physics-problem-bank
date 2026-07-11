"""Phase C smoke test — run: python scripts/test_phase_c_smoke.py"""
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


def login(client, email):
    r = client.get('/login')
    client.post(
        '/login',
        data={
            'csrf_token': csrf_from(r.data.decode()),
            'email': email,
            'password': 'password123',
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
        handle_a = f'phc_a_{suffix}'
        handle_b = f'phc_b_{suffix}'
        email_a = f'phc_a_{suffix}@example.com'
        email_b = f'phc_b_{suffix}@example.com'

        register(client, email_a, handle_a)
        generate_problem(client)

        r = client.post(
            '/shared-questions/share',
            data={
                'csrf_token': csrf_from(client.get('/').data.decode()),
                'visibility': 'public',
                'note': 'Feed test',
            },
            headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        share_data = r.get_json()
        assert share_data.get('share_id')

        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})

        register(client, email_b, handle_b)
        r = client.post(f'/api/v1/users/{handle_a}/follow')
        assert r.status_code == 200
        assert r.get_json().get('following') is True

        r = client.get('/feed')
        assert r.status_code == 200
        assert b'Activity feed' in r.data
        assert handle_a.encode() in r.data
        assert b'shared a question' in r.data

        r = client.get('/api/v1/feed?filter=shares')
        assert r.status_code == 200
        data = r.get_json()
        assert data.get('ok') is True
        assert data.get('filter') == 'shares'
        items = data.get('items') or []
        assert len(items) >= 1
        assert items[0].get('card_type') == 'share'
        assert handle_a in items[0].get('message', '')

        r = client.get('/api/v1/feed?filter=quizzes')
        assert r.status_code == 200
        assert r.get_json().get('filter') == 'quizzes'

        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        login(client, email_a)
        r = client.get('/feed')
        assert r.status_code == 200
        assert b'Follow people' in r.data

    print('Phase C smoke tests passed.')


if __name__ == '__main__':
    main()
