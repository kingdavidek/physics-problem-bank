"""Phase 2 smoke test — run: python scripts/test_user_data_smoke.py"""
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


def register_and_login(client, email, handle):
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
        register_and_login(client, f'phase2_{suffix}@example.com', f'p2_{suffix}')

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

        r = client.post(
            '/saved-problems/save',
            data={'csrf_token': csrf_from(r.data.decode())},
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            },
        )
        assert r.status_code == 200
        save_data = r.get_json()
        assert save_data['ok'] is True
        saved_id = save_data['saved_id']

        r = client.get('/profile')
        assert b'Saved questions' in r.data
        assert b'bidmas' in r.data.lower() or b'Order of Operations' in r.data

        r = client.get(f'/saved-problems/{saved_id}')
        assert r.status_code == 200
        if b'New numbers' in r.data:
            r = client.post(
                f'/saved-problems/{saved_id}/reroll',
                data={'csrf_token': csrf_from(r.data.decode())},
                headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                },
            )
            assert r.status_code == 200
            assert r.get_json()['ok'] is True

        r = client.post(
            '/api/lesson-progress',
            json={
                'csrf_token': csrf_from(client.get('/profile').data.decode()),
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'section_key': 'step-1',
                'section_label': 'Negative numbers',
                'completed_keys': ['step-0', 'step-1'],
            },
        )
        assert r.get_json()['ok'] is True

        r = client.get('/api/lesson-progress/gcse/maths/bidmas')
        data = r.get_json()
        assert data['progress']['section_key'] == 'step-1'
        assert data['progress']['completed_keys'] == ['step-0', 'step-1']

        from app import get_db
        from models.user_data import record_quiz_attempt

        with get_db() as conn:
            from models.user import User
            user = User.get_by_email(conn, f'phase2_{suffix}@example.com')
            sample_problems = [{
                'question': 'What is 2 + 2?',
                'options': ['A) 3', 'B) 4', 'C) 5', 'D) 6'],
                'correct_answer': 'B',
                'solution': '2 + 2 = 4',
            }]
            attempt_id = record_quiz_attempt(
                conn, user.id, 'gcse', 'maths', 'bidmas', 0, 1, ['A'], sample_problems
            )

        r = client.get(f'/quiz-attempts/{attempt_id}')
        assert r.status_code == 200
        assert b'What is 2 + 2?' in r.data
        assert b'Explanation' in r.data

        r = client.get('/profile')
        assert b'8/10' not in r.data
        assert b'View results' in r.data

    print('Phase 2 smoke tests passed.')


if __name__ == '__main__':
    main()
