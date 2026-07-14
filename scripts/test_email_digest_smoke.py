"""Email digest smoke test — run: python scripts/test_email_digest_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ['SITE_URL'] = 'http://127.0.0.1:5000'
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-digest-smoke')

from app import app  # noqa: E402
from models.email_digest import (  # noqa: E402
    make_unsubscribe_token,
    render_digest_html,
    render_digest_text,
    verify_unsubscribe_token,
)


def bearer(token: str) -> dict:
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]

        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'ed_{suffix}@example.com',
                'handle': f'ed_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        body = r.get_json()
        token = body['token']
        user_id = body['user']['id']
        auth = bearer(token)

        # Default off
        r = client.get('/api/v1/me/settings', headers=auth)
        assert r.status_code == 200
        assert r.get_json()['settings']['email_weekly_digest'] is False

        # Opt in via API
        r = client.patch(
            '/api/v1/me/settings',
            json={'email_weekly_digest': True},
            headers=auth,
        )
        assert r.status_code == 200
        assert r.get_json()['settings']['email_weekly_digest'] is True

        # Preview endpoint
        r = client.get('/api/v1/me/email/digest-preview', headers=auth)
        assert r.status_code == 200
        preview = r.get_json()['preview']
        assert preview['subject']
        assert 'Active days' in preview['text'] or 'active day' in preview['text'].lower()
        assert '<html>' in preview['html'].lower()

        # Test send (console provider)
        r = client.post('/api/v1/me/email/test-digest', headers=auth)
        assert r.status_code == 200, r.data

        # Unsubscribe token round-trip
        unsub = make_unsubscribe_token(user_id, app.secret_key)
        assert verify_unsubscribe_token(unsub, app.secret_key) == user_id

        r = client.get(f'/email/unsubscribe?token={unsub}')
        assert r.status_code == 200
        assert b'unsubscribed' in r.data.lower()

        r = client.get('/api/v1/me/settings', headers=auth)
        assert r.get_json()['settings']['email_weekly_digest'] is False

        # Render helpers produce content
        assert 'Problem Bank' in render_digest_text({'handle': 'x', 'recap': {'active_days': 1, 'days': 7, 'topics_practised': 0, 'activity_count': 0}, 'profile_url': '/profile'})
        assert 'Problem Bank' in render_digest_html({'handle': 'x', 'recap': {'active_days': 0, 'days': 7}, 'profile_url': '/profile', 'settings_url': '/settings'})

    print('Email digest smoke test passed.')


if __name__ == '__main__':
    main()
