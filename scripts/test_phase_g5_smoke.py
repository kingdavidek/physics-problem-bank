"""Phase G5 (anonymous cohort stats) smoke test — run: python scripts/test_phase_g5_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.cohort_stats import (  # noqa: E402
    MIN_SAMPLE_SIZE,
    compute_problem_key,
    get_cohort_stats,
    record_and_get_cohort,
    record_cohort_sample,
    serialize_cohort_stats,
)


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def sample_problem(question='What is 2 + 2?', correct_raw='4'):
    return {
        'question': question,
        'solution': '4',
        'hint': 'Add',
        'correct_answer_raw': correct_raw,
        'answer_type': 'number',
        'variant_name': 'test_variant',
    }


def main():
    problem = sample_problem()
    key = compute_problem_key(
        problem,
        level='gcse',
        subject='maths',
        topic='bidmas',
        variant_name='test_variant',
    )
    assert key
    assert len(key) == 32

    same_key = compute_problem_key(
        sample_problem('What is 2 + 2?', '4'),
        level='gcse',
        subject='maths',
        topic='bidmas',
        variant_name='test_variant',
    )
    assert key == same_key

    different_key = compute_problem_key(
        sample_problem('What is 3 + 3?', '6'),
        level='gcse',
        subject='maths',
        topic='bidmas',
        variant_name='test_variant',
    )
    assert different_key != key

    mcq_problem = {
        'question': 'Which is a prime number?',
        'options': ['A  4', 'B  7', 'C  9'],
        'correct_answer': 'B',
    }
    mcq_key = compute_problem_key(
        mcq_problem,
        level='gcse',
        subject='maths',
        topic='bidmas',
    )
    assert mcq_key

    with get_db() as conn:
        for i in range(MIN_SAMPLE_SIZE - 1):
            record_cohort_sample(conn, key, 'gcse', 'maths', 'bidmas', correct=(i % 3 == 0))
        stats = get_cohort_stats(conn, key)
        assert serialize_cohort_stats(stats) is None

        record_cohort_sample(conn, key, 'gcse', 'maths', 'bidmas', correct=False)
        public = record_and_get_cohort(
            conn,
            problem,
            level='gcse',
            subject='maths',
            topic='bidmas',
            variant_name='test_variant',
            correct=True,
        )
        assert public is not None
        assert public['sample_size'] >= MIN_SAMPLE_SIZE
        assert public['wrong_pct'] is not None

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pg5_{suffix}@example.com',
                'handle': f'pg5_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        token = r.get_json()['token']
        auth = bearer(token)

        unique_problem = sample_problem(f'Cohort smoke {suffix}?', '99')
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
                'variant_name': 'test_variant',
                'problem': unique_problem,
            }

        cohort = None
        for i in range(MIN_SAMPLE_SIZE):
            r = client.post(
                '/api/v1/problems/check',
                json={'user_answer': 'wrong' if i else '99'},
                headers=auth,
            )
            assert r.status_code == 200, r.data
            body = r.get_json()
            cohort = body.get('cohort')
            if cohort:
                break

        assert cohort is not None, 'expected cohort stats after enough samples'
        assert cohort['sample_size'] >= MIN_SAMPLE_SIZE
        assert 0 <= cohort['wrong_pct'] <= 100

        with get_db() as conn:
            for i in range(MIN_SAMPLE_SIZE):
                record_cohort_sample(conn, mcq_key, 'gcse', 'maths', 'bidmas', correct=(i % 2 == 0))

        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
                'problem': mcq_problem,
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
        assert r.get_json().get('correct') is True
        assert r.get_json().get('cohort') is not None

    print('Phase G5 smoke tests passed.')


if __name__ == '__main__':
    main()
