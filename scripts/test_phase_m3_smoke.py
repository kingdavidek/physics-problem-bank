"""Phase M3 smoke test — run: python scripts/test_phase_m3_smoke.py"""
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


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle = f'pm3_{suffix}'
        email = f'pm3_{suffix}@example.com'
        password = 'password123'

        # Register via API
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'handle': handle,
                'password': password,
                'age_confirm': True,
                'label': 'Smoke test',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        body = r.get_json()
        assert body['ok'] is True
        assert body['user']['handle'] == handle
        token = body['token']
        assert token.startswith('pb_')

        # Session cookie should NOT be set for API register
        assert not client.get_cookie('session')

        # Bearer auth works on protected route
        r = client.get('/api/v1/auth/me', headers=bearer(token))
        assert r.status_code == 200, r.data
        assert r.get_json()['user']['email'] == email

        r = client.get('/api/v1/me/settings', headers=bearer(token))
        assert r.status_code == 200, r.data

        r = client.post(
            '/api/v1/problems/generate',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'mcq',
                'difficulty': 'foundational',
                'action': 'start',
            },
            headers=bearer(token),
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['ok'] is True

        # List tokens
        r = client.get('/api/v1/auth/tokens', headers=bearer(token))
        assert r.status_code == 200, r.data
        tokens = r.get_json()['tokens']
        assert len(tokens) == 1
        assert tokens[0]['is_current'] is True
        assert tokens[0]['label'] == 'Smoke test'

        # Login issues second token
        r = client.post(
            '/api/v1/auth/login',
            json={'email': email, 'password': password, 'label': 'Second device'},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        token2 = r.get_json()['token']
        assert token2 != token

        r = client.get('/api/v1/auth/tokens', headers=bearer(token2))
        assert len(r.get_json()['tokens']) == 2

        # Logout revokes only current token
        r = client.post('/api/v1/auth/logout', headers=bearer(token2))
        assert r.status_code == 200, r.data
        r = client.get('/api/v1/auth/me', headers=bearer(token2))
        assert r.status_code == 401
        r = client.get('/api/v1/auth/me', headers=bearer(token))
        assert r.status_code == 200

        # Revoke all (keep current)
        r = client.post(
            '/api/v1/auth/revoke-all',
            json={'keep_current': True},
            headers=bearer(token),
        )
        assert r.status_code == 200, r.data
        r = client.get('/api/v1/auth/tokens', headers=bearer(token))
        assert len(r.get_json()['tokens']) == 1

        # Web settings revoke-all (session auth)
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(client.get('/login').data.decode()),
                'email': email,
                'password': password,
            },
            follow_redirects=True,
        )
        r = client.post(
            '/profile/settings',
            data={
                'csrf_token': csrf_from(client.get('/profile/settings').data.decode()),
                'action': 'revoke_all_api_tokens',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert b'All app sessions have been signed out' in r.data

        client.post(
            '/logout',
            data={'csrf_token': csrf_from(client.get('/profile').data.decode())},
            follow_redirects=True,
        )

        r = client.get('/api/v1/auth/me', headers=bearer(token))
        assert r.status_code == 401, r.data

        # Invalid credentials
        r = client.post(
            '/api/v1/auth/login',
            json={'email': email, 'password': 'wrong-password'},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 401
        assert r.get_json()['code'] == 'invalid_credentials'

    print('Phase M3 smoke test passed.')


if __name__ == '__main__':
    main()
