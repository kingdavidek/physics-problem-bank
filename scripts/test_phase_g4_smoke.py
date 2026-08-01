"""Phase G4 (wrong-answer reflection) smoke test — run: python scripts/test_phase_g4_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.reflections import get_reflection, list_reflections, save_reflection  # noqa: E402
from models.user_data import record_generator_mcq_attempt  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pg4_{suffix}@example.com',
                'handle': f'pg4_{suffix}',
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
            attempt_id = record_generator_mcq_attempt(
                conn,
                user_id,
                'gcse',
                'maths',
                'bidmas',
                'mcq',
                'foundational',
                'B',
                'A',
                False,
            )

        # POST reflection linked to attempt.
        r = client.post(
            '/api/v1/me/reflections',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'source': 'check',
                'attempt_id': attempt_id,
                'prompt_type': 'calculation_error',
                'reflection_text': 'Forgot BIDMAS order on the second step.',
            },
            headers=auth,
        )
        assert r.status_code == 201, r.data
        data = r.get_json()
        assert data['ok'] is True
        reflection = data['reflection']
        assert reflection['id']
        assert reflection['topic'] == 'bidmas'
        assert reflection['topic_label']
        assert reflection['topic_url']
        assert reflection['source'] == 'check'
        assert reflection['attempt_id'] == attempt_id
        assert reflection['prompt_type'] == 'calculation_error'
        assert 'Forgot BIDMAS' in reflection['reflection_text']
        reflection_id = reflection['id']

        # Chip-only reflection (no free text).
        r = client.post(
            '/api/v1/me/reflections',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebra',
                'source': 'mcq',
                'prompt_type': 'misread_question',
            },
            headers=auth,
        )
        assert r.status_code == 201, r.data
        assert r.get_json()['reflection']['prompt_type'] == 'misread_question'

        # Free-text-only reflection.
        r = client.post(
            '/api/v1/me/reflections',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'surds',
                'source': 'mcq',
                'reflection_text': 'Need to practise rationalising.',
            },
            headers=auth,
        )
        assert r.status_code == 201, r.data

        # GET list (newest first).
        r = client.get('/api/v1/me/reflections?limit=10', headers=auth)
        assert r.status_code == 200, r.data
        listed = r.get_json()
        assert listed['ok'] is True
        assert len(listed['reflections']) == 3
        assert listed['reflections'][0]['id'] == reflection_id or listed['reflections'][0]['topic'] == 'surds'
        assert listed['next_before_id'] == listed['reflections'][-1]['id']

        # Topic filter.
        r = client.get('/api/v1/me/reflections?topic=bidmas', headers=auth)
        assert len(r.get_json()['reflections']) == 1
        assert r.get_json()['reflections'][0]['topic'] == 'bidmas'

        # Model-level read.
        with get_db() as conn:
            row = get_reflection(conn, user_id, reflection_id)
            assert row['attempt_id'] == attempt_id
            rows = list_reflections(conn, user_id, limit=5)
            assert len(rows) == 3

        # Check API returns attempt_id when recording.
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
                'problem': {
                    'correct_answer_raw': '42',
                    'answer_type': 'number',
                },
            }
        r = client.post(
            '/api/v1/problems/check',
            json={'user_answer': '7'},
            headers=auth,
        )
        assert r.status_code == 200, r.data
        check_body = r.get_json()
        assert check_body['ok'] is True
        assert check_body['correct'] is False
        assert isinstance(check_body.get('attempt_id'), int)

        # MCQ answer API returns attempt_id (graded from session problem).
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
                'problem': {
                    'correct_answer': 'A',
                    'options': ['A  1', 'B  2', 'C  3', 'D  4'],
                },
            }
        r = client.post(
            '/api/v1/generator/mcq-answer',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
                'user_answer': 'B',
            },
            headers=auth,
        )
        assert r.status_code == 200, r.data
        mcq_body = r.get_json()
        assert mcq_body.get('correct') is False
        assert isinstance(mcq_body.get('attempt_id'), int)

        # Validation errors.
        r = client.post(
            '/api/v1/me/reflections',
            json={'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas', 'source': 'check'},
            headers=auth,
        )
        assert r.status_code == 400, r.data
        assert r.get_json()['code'] == 'empty_reflection'

        r = client.post(
            '/api/v1/me/reflections',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'source': 'check',
                'prompt_type': 'not_a_real_chip',
            },
            headers=auth,
        )
        assert r.status_code == 400, r.data
        assert r.get_json()['code'] == 'invalid_prompt_type'

        r = client.post(
            '/api/v1/me/reflections',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'source': 'check',
                'attempt_id': 999999,
                'prompt_type': 'other',
            },
            headers=auth,
        )
        assert r.status_code == 404, r.data
        assert r.get_json()['code'] == 'not_found'

        r = client.post(
            '/api/v1/me/reflections',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'nope',
                'source': 'check',
                'prompt_type': 'other',
            },
            headers=auth,
        )
        assert r.status_code == 400, r.data
        assert r.get_json()['code'] == 'invalid_topic'

        # Unauthenticated.
        r = client.post(
            '/api/v1/me/reflections',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'source': 'check',
                'prompt_type': 'other',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code in (401, 403), r.data

    print('Phase G4 smoke tests passed.')


if __name__ == '__main__':
    main()
