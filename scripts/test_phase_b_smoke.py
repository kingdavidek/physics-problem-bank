"""Phase B smoke test — run: python scripts/test_phase_b_smoke.py"""
import json
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
        handle_a = f'phb_a_{suffix}'
        handle_b = f'phb_b_{suffix}'

        register(client, f'phb_a_{suffix}@example.com', handle_a)
        generate_problem(client)

        r = client.post(
            '/shared-questions/share',
            data={
                'csrf_token': csrf_from(client.get('/').data.decode()),
                'visibility': 'public',
                'note': 'Try this',
            },
            headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        share_data = r.get_json()
        share_id = share_data['share_id']

        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        r = client.get(f'/shared/{share_id}')
        assert r.status_code == 200
        assert b'Shared question' in r.data

        register(client, f'phb_b_{suffix}@example.com', handle_b)
        generate_problem(client)
        r = client.post(
            '/suggestions',
            data={
                'csrf_token': csrf_from(client.get('/').data.decode()),
                'recipient_handle': handle_a,
                'note': 'For you',
            },
            headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        )
        assert r.status_code == 200

        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        login(client, f'phb_a_{suffix}@example.com')

        r = client.get('/suggestions')
        assert r.status_code == 200
        assert handle_b.encode() in r.data

        r = client.get('/api/v1/me/suggestions')
        assert r.status_code == 200
        suggestions = r.get_json()['suggestions']
        assert len(suggestions) >= 1

        r = client.get('/api/v1/me/notifications')
        assert r.status_code == 200
        notif_data = r.get_json()
        assert notif_data['unread_count'] >= 1
        assert any(n['type'] == 'suggestion_received' for n in notif_data['notifications'])

        suggestion_id = suggestions[0]['id']
        r = client.get(f'/suggestions/{suggestion_id}')
        assert r.status_code == 200
        assert b'Suggested question' in r.data

        r = client.get('/profile/settings')
        r = client.post(
            '/profile/settings',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'profile_visibility': 'public',
                'auto_share_quiz': '1',
                'default_share_visibility': 'followers_only',
            },
            follow_redirects=True,
        )
        assert b'Settings saved' in r.data

        with app.app_context():
            from app import get_db
            from models.social import list_activity_events

            with get_db() as conn:
                events = list_activity_events(conn, 1, limit=5)
            assert isinstance(events, list)

    print('Phase B smoke tests passed.')


if __name__ == '__main__':
    main()
