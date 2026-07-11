"""Social API v1 smoke test — run: python scripts/test_social_api_smoke.py"""
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


def logout(client):
    r = client.get('/profile')
    client.post(
        '/logout',
        data={'csrf_token': csrf_from(r.data.decode())},
        follow_redirects=True,
    )


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'api_a_{suffix}'
        handle_b = f'api_b_{suffix}'
        email_a = f'api_a_{suffix}@example.com'
        email_b = f'api_b_{suffix}@example.com'

        register(client, email_a, handle_a)
        logout(client)
        register(client, email_b, handle_b)
        logout(client)

        # Anonymous profile fetch
        r = client.get(f'/api/v1/users/{handle_a}/profile')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['profile']['handle'] == handle_a

        # Settings require auth
        r = client.get('/api/v1/me/settings')
        assert r.status_code == 401

        login(client, email_a)
        r = client.get('/api/v1/me/settings')
        assert r.status_code == 200
        assert r.get_json()['settings']['profile_visibility'] == 'public'

        r = client.patch(
            '/api/v1/me/settings',
            json={'profile_visibility': 'followers_only', 'show_quiz_stats': False},
        )
        assert r.status_code == 200
        settings = r.get_json()['settings']
        assert settings['profile_visibility'] == 'followers_only'
        assert settings['show_quiz_stats'] is False

        r = client.patch(
            '/api/v1/me/settings',
            json={'profile_visibility': 'not_a_choice'},
        )
        assert r.status_code == 400

        logout(client)

        # B cannot view A's followers-only profile
        login(client, email_b)
        r = client.get(f'/api/v1/users/{handle_a}/profile')
        assert r.status_code == 403
        assert r.get_json()['code'] == 'profile_private'

        # Toggle follow via POST
        r = client.post(f'/api/v1/users/{handle_a}/follow')
        assert r.status_code == 200
        follow_data = r.get_json()
        assert follow_data['following'] is True
        assert follow_data['followers_count'] == 1

        r = client.get(f'/api/v1/users/{handle_a}/profile')
        assert r.status_code == 200
        assert r.get_json()['profile']['viewer_follows'] is True

        # Toggle off via POST
        r = client.post(f'/api/v1/users/{handle_a}/follow')
        assert r.status_code == 200
        assert r.get_json()['following'] is False

        # Follow again, then DELETE unfollow
        client.post(f'/api/v1/users/{handle_a}/follow')
        r = client.delete(f'/api/v1/users/{handle_a}/follow')
        assert r.status_code == 200
        assert r.get_json()['following'] is False

        # Private profile blocks even followers
        logout(client)
        login(client, email_a)
        client.patch('/api/v1/me/settings', json={'profile_visibility': 'private'})
        logout(client)
        login(client, email_b)
        client.post(f'/api/v1/users/{handle_a}/follow')
        r = client.get(f'/api/v1/users/{handle_a}/profile')
        assert r.status_code == 403

        r = client.get('/api/v1/users/does_not_exist_xyz/profile')
        assert r.status_code == 404

    print('Social API v1 smoke tests passed.')


if __name__ == '__main__':
    main()
