"""Phase M4b smoke test — run: python scripts/test_phase_m4b_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pm4b_{suffix}@example.com',
                'handle': f'pm4b_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        token = r.get_json()['token']
        auth = bearer(token)

        # Lesson metadata includes quiz API
        r = client.get('/api/v1/topics/gcse/maths/bidmas/lesson', headers=auth)
        assert r.status_code == 200, r.data
        lesson = r.get_json()['lesson']
        assert lesson['supports_lesson_quiz'] is True
        assert lesson['lesson_quiz_api'] == '/api/v1/lesson-quiz/start'

        # Start lesson quiz
        r = client.post(
            '/api/v1/lesson-quiz/start',
            json={'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas'},
            headers=auth,
        )
        assert r.status_code == 201, r.data
        start = r.get_json()
        session_id = start['session_id']
        assert session_id.startswith('lq_u')
        assert start['total'] == 10
        assert start['problem']['question_html']
        assert 'solution_html' not in start['problem']

        r = client.get(f'/api/v1/lesson-quiz/{session_id}/question', headers=auth)
        assert r.status_code == 200, r.data
        assert r.get_json()['question_number'] == 1

        total = start['total']
        attempt_id = None
        for i in range(total):
            r = client.post(
                f'/api/v1/lesson-quiz/{session_id}/answer',
                json={'user_answer': 'A'},
                headers=auth,
            )
            assert r.status_code == 200, r.data
            body = r.get_json()
            if i < total - 1:
                assert body['finished'] is False
            else:
                assert body['finished'] is True
                assert body['score'] is not None
                assert body['attempt_id'] is not None
                attempt_id = body['attempt_id']
                assert body['attempt_url']

        r = client.get(f'/api/v1/lesson-quiz/{session_id}/results', headers=auth)
        assert r.status_code == 200, r.data
        results = r.get_json()
        assert results['score'] == results['total'] or results['score'] >= 0
        assert len(results['problems']) == 10
        assert results['problems'][0]['solution_html']
        assert results['attempt_id'] == attempt_id

        # Unavailable topic
        r = client.post(
            '/api/v1/lesson-quiz/start',
            json={'level': 'gcse', 'subject': 'physics', 'topic': 'forces'},
            headers=auth,
        )
        assert r.status_code == 404
        assert r.get_json()['code'] == 'quiz_not_available'

        # Session isolation
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pm4b2_{suffix}@example.com',
                'handle': f'pm4b2_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        other = bearer(r.get_json()['token'])
        r = client.get(f'/api/v1/lesson-quiz/{session_id}/question', headers=other)
        assert r.status_code == 403

    print('Phase M4b smoke test passed.')


if __name__ == '__main__':
    main()
