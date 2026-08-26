"""Cross-user authorisation smoke — run: python scripts/test_authz_smoke.py"""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ['SITE_URL'] = 'http://127.0.0.1:5000'
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-authz-smoke')

from app import app, get_db  # noqa: E402
from models.notifications import create_notification  # noqa: E402
from models.reflections import save_reflection  # noqa: E402
from models.revision_planner import upsert_revision_plan_settings  # noqa: E402
from models.user_data import record_quiz_attempt, save_problem  # noqa: E402


def bearer(token: str) -> dict:
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }


def register(client, email, handle):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': email,
            'handle': handle,
            'password': 'password123',
            'age_confirm': True,
        },
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 201, r.data
    body = r.get_json()
    return body['token'], body['user']['id']


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'az_a_{suffix}'
        handle_b = f'az_b_{suffix}'
        token_a, uid_a = register(client, f'az_a_{suffix}@example.com', handle_a)
        token_b, uid_b = register(client, f'az_b_{suffix}@example.com', handle_b)
        auth_a = bearer(token_a)
        auth_b = bearer(token_b)

        exam_date = (datetime.now(timezone.utc).date() + timedelta(days=21)).isoformat()
        with get_db() as conn:
            saved_id = save_problem(
                conn, uid_a, 'gcse', 'maths', 'bidmas', 'standard', 'foundational',
                {'question': 'authz', 'answer': '1'},
            )
            quiz_id = record_quiz_attempt(
                conn, uid_a, 'gcse', 'maths', 'bidmas', 1, 2,
                [{'correct': True}], [{'question': 'q'}],
            )
            reflection_id = save_reflection(
                conn, uid_a, 'gcse', 'maths', 'bidmas',
                source='check', prompt_type='guessed',
                reflection_text='authz note',
            )
            upsert_revision_plan_settings(conn, uid_a, 'gcse', 'maths', exam_date)
            note_id = create_notification(
                conn, uid_a, 'new_follower', {'handle': handle_b},
            )

        r = client.get('/api/v1/auth/tokens', headers=auth_a)
        assert r.status_code == 200
        token_id = r.get_json()['tokens'][0]['id']

        # B must not read, mutate, or delete A's rows by id.
        r = client.get(f'/api/v1/me/saved-problems/{saved_id}', headers=auth_b)
        assert r.status_code == 404, r.data
        r = client.delete(f'/api/v1/me/saved-problems/{saved_id}', headers=auth_b)
        assert r.status_code == 404, r.data

        r = client.get(f'/api/v1/me/quiz-attempts/{quiz_id}', headers=auth_b)
        assert r.status_code == 404, r.data

        r = client.get(f'/api/v1/me/reflections/{reflection_id}', headers=auth_b)
        assert r.status_code == 404, r.data

        r = client.get('/api/v1/me/revision-plan', headers=auth_b)
        assert r.status_code == 200
        assert r.get_json()['revision_plan'] is None or r.get_json()['revision_plan'] == {}
        r = client.delete('/api/v1/me/revision-plan', headers=auth_b)
        assert r.status_code in (200, 404)
        r = client.get('/api/v1/me/revision-plan', headers=auth_a)
        plan = r.get_json()['revision_plan']
        assert plan, plan

        r = client.post(
            '/api/v1/me/notifications/read',
            json={'id': note_id},
            headers=auth_b,
        )
        assert r.status_code == 404, r.data

        r = client.delete(f'/api/v1/auth/tokens/{token_id}', headers=auth_b)
        assert r.status_code == 404, r.data
        r = client.get('/api/v1/auth/tokens', headers=auth_a)
        assert any(item['id'] == token_id for item in r.get_json()['tokens'])

        # A's own reads still work.
        assert client.get(f'/api/v1/me/saved-problems/{saved_id}', headers=auth_a).status_code == 200
        assert client.get(f'/api/v1/me/quiz-attempts/{quiz_id}', headers=auth_a).status_code == 200
        assert client.get(f'/api/v1/me/reflections/{reflection_id}', headers=auth_a).status_code == 200

        # Private profile: logged-out and non-follower.
        r = client.patch(
            '/api/v1/me/settings',
            json={'profile_visibility': 'private'},
            headers=auth_a,
        )
        assert r.status_code == 200
        r = client.get(f'/api/v1/users/{handle_a}/profile')
        assert r.status_code == 403
        r = client.get(f'/api/v1/users/{handle_a}/profile', headers=auth_b)
        assert r.status_code == 403
        r = client.get(f'/u/{handle_a}')
        assert r.status_code == 200
        assert b'profile is private' in r.data.lower()

    print('Authz smoke tests passed.')


if __name__ == '__main__':
    main()
