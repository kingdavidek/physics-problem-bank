"""Phase G1 smoke test — run: python scripts/test_phase_g1_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.user_data import record_generator_mcq_attempt, record_quiz_attempt  # noqa: E402
from models.weak_topics import analyze_weak_topics  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pg1_{suffix}@example.com',
                'handle': f'pg1_{suffix}',
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

        with get_db() as conn:
            record_quiz_attempt(
                conn,
                user_id,
                'gcse',
                'maths',
                'bidmas',
                3,
                10,
                ['A'] * 10,
                [{'question': 'Q', 'correct_answer': 'B'}] * 10,
            )
            record_quiz_attempt(
                conn,
                user_id,
                'gcse',
                'maths',
                'bidmas',
                4,
                10,
                ['A'] * 10,
                [{'question': 'Q', 'correct_answer': 'B'}] * 10,
            )
            for _ in range(5):
                record_generator_mcq_attempt(
                    conn,
                    user_id,
                    'gcse',
                    'maths',
                    'bidmas',
                    'mcq',
                    'foundational',
                    'A',
                    'B',
                    False,
                )
            record_quiz_attempt(
                conn,
                user_id,
                'gcse',
                'maths',
                'algebra',
                9,
                10,
                ['A'] * 10,
                [{'question': 'Q', 'correct_answer': 'A'}] * 10,
            )

            weak = analyze_weak_topics(conn, user_id, limit=8)
            assert len(weak) >= 1
            assert weak[0]['topic'] == 'bidmas'
            assert weak[0]['weakness_score'] > 0
            assert weak[0]['reasons']

        r = client.get('/api/v1/me/weak-topics', headers=auth)
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True
        assert len(data['weak_topics']) >= 1
        top = data['weak_topics'][0]
        assert top['topic'] == 'bidmas'
        assert top['topic_label']
        assert top['topic_url']
        assert 'reasons' in top

        r = client.get('/api/v1/me/weak-topics?limit=3', headers=auth)
        assert r.status_code == 200
        assert len(r.get_json()['weak_topics']) <= 3

        r = client.get('/profile', headers=auth)
        assert r.status_code == 200
        assert b'Topics to revisit' in r.data
        assert b'bidmas' in r.data.lower() or b'BIDMAS' in r.data

    print('Phase G1 smoke tests passed.')


if __name__ == '__main__':
    main()
