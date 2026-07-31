"""Phase G6 (skill gaps + profile reflections) smoke test — run: python scripts/test_phase_g6_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.reflections import list_reflections, save_reflection  # noqa: E402
from models.skill_gaps import MIN_REFLECTIONS, analyze_skill_gaps  # noqa: E402
from models.user_data import record_generator_mcq_attempt, record_quiz_attempt  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pg6_{suffix}@example.com',
                'handle': f'pg6_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        token = r.get_json()['token']
        user_id = r.get_json()['user']['id']
        auth = bearer(token)

        with get_db() as conn:
            for topic in ('algebra', 'bidmas', 'surds'):
                for _ in range(MIN_REFLECTIONS):
                    save_reflection(
                        conn,
                        user_id,
                        'gcse',
                        'maths',
                        topic,
                        source='check',
                        prompt_type='forgot_formula',
                        reflection_text='Need the rule again.',
                    )
            save_reflection(
                conn,
                user_id,
                'gcse',
                'maths',
                'vectors',
                source='mcq',
                prompt_type='misread_question',
            )
            record_quiz_attempt(
                conn, user_id, 'gcse', 'maths', 'algebra', 4, 10,
                ['A'] * 10, [{'question': 'Q', 'correct_answer': 'B'}] * 10,
            )
            record_generator_mcq_attempt(
                conn, user_id, 'gcse', 'maths', 'bidmas', 'mcq', 'foundational',
                'B', 'A', False,
            )

            gaps = analyze_skill_gaps(conn, user_id, limit=5)
            assert gaps
            top = gaps[0]
            assert top['prompt_type'] == 'forgot_formula'
            assert top['reflection_count'] >= MIN_REFLECTIONS
            assert top['topic_count'] >= 2

            filtered = list_reflections(
                conn, user_id, limit=10, prompt_type='forgot_formula',
            )
            assert len(filtered) >= MIN_REFLECTIONS
            assert all(item['prompt_type'] == 'forgot_formula' for item in filtered)

        r = client.get('/api/v1/me/skill-gaps?limit=5', headers=auth)
        assert r.status_code == 200, r.data
        body = r.get_json()
        assert body['ok'] is True
        assert body['skill_gaps']
        assert body['skill_gaps'][0]['label']
        assert body['skill_gaps'][0]['topics'][0]['topic_url']

        r = client.get('/api/v1/me/reflections?prompt_type=forgot_formula&limit=5', headers=auth)
        assert r.status_code == 200, r.data
        listed = r.get_json()['reflections']
        assert listed
        assert all(item['prompt_type'] == 'forgot_formula' for item in listed)
        assert listed[0]['prompt_type_label']

        r = client.get('/api/v1/me/reflections?prompt_type=not_a_chip', headers=auth)
        assert r.get_json()['reflections'] == []

        r = client.get('/profile', headers=auth)
        assert r.status_code == 200
        assert b'Skill patterns' in r.data
        assert b'My reflections' in r.data
        assert b'Forgot a formula or rule' in r.data

        r = client.get('/profile?reflection_type=misread_question', headers=auth)
        assert b'Misread the question' in r.data

        r = client.get('/api/v1/me/skill-gaps', headers={'Accept': 'application/json'})
        assert r.status_code in (401, 403), r.data

    print('Phase G6 smoke tests passed.')


if __name__ == '__main__':
    main()
