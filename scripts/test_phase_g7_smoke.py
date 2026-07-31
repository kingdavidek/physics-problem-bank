"""Phase G7 (exam revision planner) smoke test — run: python scripts/test_phase_g7_smoke.py"""
import os
import re
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.revision_planner import (  # noqa: E402
    build_revision_plan,
    revision_plan_for_user,
    upsert_revision_plan_settings,
)
from models.user_data import record_generator_mcq_attempt, record_quiz_attempt  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, 'csrf token not found'
    return match.group(1)


def main():
    exam_date = (date.today() + timedelta(days=14)).isoformat()

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pg7_{suffix}@example.com',
                'handle': f'pg7_{suffix}',
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
            for topic, score, total in (
                ('bidmas', 3, 10),
                ('algebra', 5, 10),
                ('surds', 9, 10),
            ):
                record_quiz_attempt(
                    conn, user_id, 'gcse', 'maths', topic, score, total,
                    ['A'] * total, [{'question': 'Q', 'correct_answer': 'B'}] * total,
                )
                record_generator_mcq_attempt(
                    conn, user_id, 'gcse', 'maths', topic, 'mcq', 'foundational',
                    'B', 'A', False,
                )
                record_generator_mcq_attempt(
                    conn, user_id, 'gcse', 'maths', topic, 'mcq', 'foundational',
                    'B', 'A', False,
                )
                record_generator_mcq_attempt(
                    conn, user_id, 'gcse', 'maths', topic, 'mcq', 'foundational',
                    'B', 'A', False,
                )

            upsert_revision_plan_settings(
                conn, user_id, 'gcse', 'maths', exam_date,
            )
            plan = revision_plan_for_user(conn, user_id)
            assert plan is not None
            assert plan['exam_date'] == exam_date
            assert plan['topics_scheduled'] >= 1
            assert plan['sessions']

            built = build_revision_plan(
                conn, user_id, level='gcse', subject='maths', exam_date=exam_date,
            )
            assert built['study_day_count'] >= 1
            assert built['weak_topic_count'] >= 1

        r = client.get('/api/v1/me/revision-plan', headers=auth)
        assert r.status_code == 200, r.data
        body = r.get_json()
        assert body['ok'] is True
        assert body['revision_plan']['exam_date'] == exam_date
        assert body['revision_plan']['sessions']

        r = client.put(
            '/api/v1/me/revision-plan',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'exam_date': (date.today() + timedelta(days=21)).isoformat(),
            },
            headers=auth,
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['revision_plan']['days_remaining'] == 21

        r = client.put(
            '/api/v1/me/revision-plan',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'exam_date': (date.today() - timedelta(days=1)).isoformat(),
            },
            headers=auth,
        )
        assert r.status_code == 400, r.data
        assert r.get_json()['code'] == 'exam_date_past'

        r = client.delete('/api/v1/me/revision-plan', headers=auth)
        assert r.status_code == 200, r.data
        r = client.get('/api/v1/me/revision-plan', headers=auth)
        assert r.get_json()['revision_plan'] is None

        login_page = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(login_page.data.decode()),
                'email': f'pg7_{suffix}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )
        profile_page = client.get('/profile')
        r = client.post(
            '/profile/revision-plan',
            data={
                'csrf_token': csrf_from(profile_page.data.decode()),
                'level': 'gcse',
                'subject': 'maths',
                'exam_date': exam_date,
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert b'Exam revision plan' in r.data

        r = client.get('/profile')
        assert b'Exam revision plan' in r.data

    print('Phase G7 smoke tests passed.')


if __name__ == '__main__':
    main()
