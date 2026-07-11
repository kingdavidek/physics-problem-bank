"""Unified search smoke test — run: python scripts/test_user_search_smoke.py"""
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


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'srch_a_{suffix}'
        handle_b = f'srch_b_{suffix}'

        register(client, f'srch_a_{suffix}@example.com', handle_a)
        client.post(
            '/logout',
            data={'csrf_token': csrf_from(client.get('/profile').data.decode())},
            follow_redirects=True,
        )
        register(client, f'srch_b_{suffix}@example.com', handle_b)
        client.post(
            '/logout',
            data={'csrf_token': csrf_from(client.get('/profile').data.decode())},
            follow_redirects=True,
        )

        r = client.get('/search')
        assert r.status_code == 200
        assert b'Search' in r.data
        assert b'site-search-open' in r.data

        r = client.get('/search?q=a')
        assert r.status_code == 200
        assert b'at least 2 characters' in r.data

        r = client.get('/search?q=vector')
        assert r.status_code == 200
        assert b'Vectors' in r.data or b'vector' in r.data.lower()

        r = client.get(f'/search?q=srch_a_{suffix[:4]}')
        assert r.status_code == 200
        assert handle_a.encode() in r.data
        assert handle_b.encode() not in r.data

        r = client.get('/users/search?q=vector', follow_redirects=True)
        assert r.status_code == 200
        assert b'Vectors' in r.data or b'vector' in r.data.lower()

        r = client.get('/api/v1/search?q=vector')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert any('vector' in item['name'].lower() for item in data['topics'])

        r = client.get(f'/api/v1/search?q=srch_a_{suffix[:4]}')
        assert r.status_code == 200
        handles = [item['handle'] for item in r.get_json()['users']]
        assert handle_a in handles

        r = client.get('/api/v1/search?q=x')
        assert r.status_code == 400
        assert r.get_json()['code'] == 'query_too_short'

    print('Unified search smoke tests passed.')


if __name__ == '__main__':
    main()
