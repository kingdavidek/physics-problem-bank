"""Phase M5 smoke test — run: python scripts/test_phase_m5_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Enable CORS for test origin before app import.
os.environ['CORS_ORIGINS'] = 'https://app.example.com,http://localhost:5173'
os.environ['PB_TESTING'] = '1'

from app import app  # noqa: E402


def bearer(token: str, test_ip: str) -> dict:
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Origin': 'https://app.example.com',
        'X-Forwarded-For': test_ip,
    }


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        test_ip = f'10.99.{int(suffix[:4], 16) % 250}.{int(suffix[4:8], 16) % 250}'
        base_headers = {
            'Accept': 'application/json',
            'Origin': 'https://app.example.com',
            'X-Forwarded-For': test_ip,
        }

        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pm5_{suffix}@example.com',
                'handle': f'pm5_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers=base_headers,
        )
        assert r.status_code == 201, r.data
        token = r.get_json()['token']
        auth = bearer(token, test_ip)

        # Health
        r = client.get('/api/v1/health', headers=auth)
        assert r.status_code == 200 and r.get_json()['status'] == 'up'

        # CORS headers on API response
        assert r.headers.get('Access-Control-Allow-Origin') == 'https://app.example.com'

        # CORS preflight
        r = client.options(
            '/api/v1/me/settings',
            headers={
                'Origin': 'https://app.example.com',
                'Access-Control-Request-Method': 'PATCH',
                'Access-Control-Request-Headers': 'Authorization',
            },
        )
        assert r.status_code == 204, r.status_code
        assert r.headers.get('Access-Control-Allow-Origin') == 'https://app.example.com'

        # API 404 JSON shape
        r = client.get('/api/v1/does-not-exist', headers=auth)
        assert r.status_code == 404
        body = r.get_json()
        assert body['ok'] is False and body['code'] == 'not_found'

        # Legacy lesson-progress deprecation + ok envelope
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
            headers=auth,
        )
        assert r.status_code == 200

        r = client.post(
            '/api/v1/me/lesson-progress',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'section_key': 'step-0',
                'section_label': 'Intro',
            },
            headers=auth,
        )
        assert r.status_code == 200

        # Register second user for suggest target
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pm5b_{suffix}@example.com',
                'handle': f'pm5b_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers=base_headers,
        )
        target_handle = r.get_json()['user']['handle']

        # Share rate limit metadata on success
        r = client.post(
            '/api/v1/shared-questions',
            json={'visibility': 'followers_only'},
            headers=auth,
        )
        assert r.status_code == 200, r.data
        assert 'rate_limit_remaining' in r.get_json()

        # Suggest rate limit metadata
        r = client.post(
            '/api/v1/suggestions',
            json={'recipient_handle': target_handle},
            headers=auth,
        )
        assert r.status_code == 200, r.data
        assert 'rate_limit_remaining' in r.get_json()

    print('Phase M5 smoke test passed.')


if __name__ == '__main__':
    main()
