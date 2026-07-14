"""Phase G2 smoke test — run: python scripts/test_phase_g2_smoke.py"""
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.user_data import record_generator_mcq_attempt, record_quiz_attempt  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pg2_{suffix}@example.com',
                'handle': f'pg2_{suffix}',
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

        problems = [
            {
                'question': f'Question {i}?',
                'options': ['A) one', 'B) two'],
                'correct_answer': 'A',
                'solution': f'Solution {i}',
            }
            for i in range(3)
        ]
        attempt_ids = []
        with get_db() as conn:
            for score in (1, 2, 3):
                attempt_ids.append(
                    record_quiz_attempt(
                        conn,
                        user_id,
                        'gcse',
                        'maths',
                        'bidmas',
                        score,
                        3,
                        ['A', 'B', 'A'],
                        problems,
                    )
                )
            for i in range(4):
                record_generator_mcq_attempt(
                    conn,
                    user_id,
                    'gcse',
                    'maths',
                    'bidmas',
                    'mcq',
                    'foundational',
                    'A' if i % 2 == 0 else 'B',
                    'A',
                    i % 2 == 0,
                )

        r = client.get('/api/v1/me/quiz-attempts', headers=auth)
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True
        assert len(data['quiz_attempts']) == 3
        assert data['quiz_attempts'][0]['id'] == attempt_ids[-1]
        assert data['quiz_attempts'][0]['has_review'] is True
        assert data['quiz_attempts'][0]['topic_label']
        assert data['next_before_id'] == data['quiz_attempts'][-1]['id']

        r = client.get(
            f'/api/v1/me/quiz-attempts?limit=2&before_id={attempt_ids[-1] + 1}',
            headers=auth,
        )
        assert r.status_code == 200
        page = r.get_json()['quiz_attempts']
        assert len(page) == 2

        detail_id = attempt_ids[-1]
        r = client.get(f'/api/v1/me/quiz-attempts/{detail_id}', headers=auth)
        assert r.status_code == 200, r.data
        detail = r.get_json()['quiz_attempt']
        assert detail['score'] == 3
        assert len(detail['questions']) == 3
        assert detail['questions'][0]['user_answer'] == 'A'
        assert detail['questions'][0]['correct'] is True
        assert detail['questions'][1]['correct'] is False
        assert 'solution_html' in detail['questions'][0]

        r = client.get('/api/v1/me/quiz-attempts/999999', headers=auth)
        assert r.status_code == 404

        r = client.get('/api/v1/me/mcq-attempts?limit=2', headers=auth)
        assert r.status_code == 200
        mcq = r.get_json()
        assert len(mcq['mcq_attempts']) == 2
        assert 'correct' in mcq['mcq_attempts'][0]

        mcq_id = mcq['mcq_attempts'][0]['id']
        r = client.get(f'/api/v1/me/mcq-attempts/{mcq_id}', headers=auth)
        assert r.status_code == 200
        assert r.get_json()['mcq_attempt']['id'] == mcq_id

    print('Phase G2 smoke tests passed.')


if __name__ == '__main__':
    main()
