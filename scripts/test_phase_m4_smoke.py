"""Phase M4 smoke test — run: python scripts/test_phase_m4_smoke.py"""
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle = f'pm4_{suffix}'
        email = f'pm4_{suffix}@example.com'
        password = 'password123'

        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'handle': handle,
                'password': password,
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        token = r.get_json()['token']
        auth = bearer(token)

        # Lesson content
        r = client.get('/api/v1/topics/gcse/maths/bidmas/lesson', headers=auth)
        assert r.status_code == 200, r.data
        lesson = r.get_json()['lesson']
        assert lesson['title']
        assert 'BIDMAS' in lesson['html'] or 'Order of Operations' in lesson['html']
        assert lesson['supports_lesson_quiz'] is True

        # Lesson progress v1
        r = client.post(
            '/api/v1/me/lesson-progress',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'section_key': 'step-0',
                'section_label': 'What is BIDMAS?',
                'completed_keys': ['step-0'],
            },
            headers=auth,
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['progress']['completed_keys'] == ['step-0']

        r = client.get('/api/v1/me/lesson-progress/gcse/maths/bidmas', headers=auth)
        assert r.status_code == 200, r.data
        assert r.get_json()['progress']['section_key'] == 'step-0'

        r = client.get('/api/v1/me/lesson-progress', headers=auth)
        assert r.status_code == 200, r.data
        assert any(item['topic'] == 'bidmas' for item in r.get_json()['items'])

        # Quick Test API
        r = client.post(
            '/api/v1/quicktest/start',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'mcq',
                'difficulty': 'foundational',
            },
            headers=auth,
        )
        assert r.status_code == 201, r.data
        start = r.get_json()
        session_id = start['session_id']
        assert start['total'] > 0
        assert start['problem']['question_html']

        r = client.get(f'/api/v1/quicktest/{session_id}/question', headers=auth)
        assert r.status_code == 200, r.data
        assert 'solution_html' not in r.get_json()['problem']

        total = start['total']
        for i in range(total):
            r = client.post(
                f'/api/v1/quicktest/{session_id}/answer',
                json={'user_answer': 'A'},
                headers=auth,
            )
            assert r.status_code == 200, r.data
            body = r.get_json()
            if i < total - 1:
                assert body['finished'] is False
            else:
                assert body['finished'] is True

        r = client.get(f'/api/v1/quicktest/{session_id}/results', headers=auth)
        assert r.status_code == 200, r.data
        results = r.get_json()
        assert len(results['problems']) == total
        assert results['problems'][0]['solution_html']

        # Owned session isolation
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pm4b_{suffix}@example.com',
                'handle': f'pm4b_{suffix}',
                'password': password,
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        other_token = r.get_json()['token']
        r = client.get(
            f'/api/v1/quicktest/{session_id}/question',
            headers=bearer(other_token),
        )
        assert r.status_code == 403

        r = client.delete(
            '/api/v1/me/lesson-progress/gcse/maths/bidmas',
            headers=auth,
        )
        assert r.status_code == 200, r.data
        r = client.get('/api/v1/me/lesson-progress/gcse/maths/bidmas', headers=auth)
        assert r.get_json()['progress'] is None

    print('Phase M4 smoke test passed.')


if __name__ == '__main__':
    main()
