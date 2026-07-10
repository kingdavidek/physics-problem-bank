"""Social Phase A smoke test — run: python scripts/test_social_smoke.py"""
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
    assert r.status_code == 200


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        register(client, f'social_a_{suffix}@example.com', f'soc_a_{suffix}')
        handle_a = f'soc_a_{suffix}'

        client.post(
            '/logout',
            data={'csrf_token': csrf_from(client.get('/profile').data.decode())},
            follow_redirects=True,
        )
        register(client, f'social_b_{suffix}@example.com', f'soc_b_{suffix}')
        handle_b = f'soc_b_{suffix}'

        client.post(
            '/logout',
            data={'csrf_token': csrf_from(client.get('/').data.decode())},
            follow_redirects=True,
        )

        # Log in as A
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': f'social_a_{suffix}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )

        r = client.get(f'/u/{handle_a}')
        assert r.status_code == 200
        assert b'Public profile' in r.data

        r = client.post(
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
        assert r.status_code == 200

        r = client.get('/topic/gcse/maths/bidmas')
        assert r.status_code == 200

        r = client.get(f'/u/{handle_a}')
        assert b'Last topic opened' in r.data or b'Order of Operations' in r.data

        r = client.get('/profile/settings')
        assert r.status_code == 200
        r = client.post(
            '/profile/settings',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'profile_visibility': 'public',
                'show_member_since': '1',
                'show_last_topic': '1',
                'show_last_activity': '1',
                'show_lesson_progress': '1',
                'show_quiz_stats': '1',
            },
            follow_redirects=True,
        )
        assert b'Privacy settings saved' in r.data

        # B views A and follows
        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': f'social_b_{suffix}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )

        r = client.get(f'/u/{handle_a}')
        assert r.status_code == 200
        r = client.post(
            f'/u/{handle_a}/follow',
            data={'csrf_token': csrf_from(r.data.decode())},
            follow_redirects=True,
        )
        assert b'following' in r.data.lower()

        r = client.get(f'/u/{handle_a}/followers')
        assert handle_a.encode() in r.data or f'@{handle_a}'.encode() in r.data

        # A sets private — B cannot see
        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': f'social_a_{suffix}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )
        r = client.get('/profile/settings')
        client.post(
            '/profile/settings',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'profile_visibility': 'private',
            },
            follow_redirects=True,
        )

        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': f'social_b_{suffix}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )
        r = client.get(f'/u/{handle_a}')
        assert b'profile is private' in r.data.lower()

    print('Social Phase A smoke tests passed.')


if __name__ == '__main__':
    main()
