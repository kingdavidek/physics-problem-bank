"""Answer check smoke test — run: python scripts/test_answer_check_smoke.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generators.gcse.maths import (  # noqa: E402
    _bidmas_problem,
    gcse_bidmas_brackets,
    gcse_bidmas_power,
    gcse_bidmas_simple,
    gcse_maths_bidmas,
    gcse_neg_add_subtract,
)
from generators.shared.answer_checkers import check_answer, check_number  # noqa: E402
from app import app  # noqa: E402


def test_checker_unit():
    ok = check_number('42', '42')
    assert ok['correct'] is True
    assert ok['normalized_user'] == '42'
    assert ok['normalized_correct'] == '42'

    ok = check_number('42', ' 42 ')
    assert ok['correct'] is True

    bad = check_number('42', 'abc')
    assert bad['correct'] is False

    neg = check_number('-5', '−5')
    assert neg['correct'] is True

    via_registry = check_answer('number', '10', '10')
    assert via_registry['correct'] is True


def test_bidmas_variants_expose_raw():
    for fn in (gcse_bidmas_simple, gcse_bidmas_brackets, gcse_bidmas_power, gcse_neg_add_subtract):
        out = fn()
        assert len(out) == 5, fn.__name__
        q, s, hint, marks, raw = out
        assert q and s and hint
        assert isinstance(raw, int)


def test_bidmas_generator_payload():
    pilot = _bidmas_problem(gcse_bidmas_simple, 'foundational')
    assert pilot.get('correct_answer_raw') is not None
    assert pilot.get('answer_type') == 'number'

    queued = gcse_maths_bidmas('foundational', 'practice', variant_name='gcse_bidmas_simple')
    assert queued.get('correct_answer_raw') is not None


def test_check_api_without_session():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '14',
                'correct_answer_raw': '14',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '13',
                'correct_answer_raw': '14',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['correct'] is False


def test_check_api_with_session_binding():
    problem = _bidmas_problem(gcse_bidmas_simple, 'foundational')
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
                'problem': problem,
            }

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': '99999',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 403, r.data
        assert r.get_json()['code'] == 'session_mismatch'


def test_generator_page_renders_free_response():
    with app.test_client() as client:
        for _ in range(12):
            r = client.post(
                '/',
                data={
                    'level': 'gcse',
                    'subject': 'maths',
                    'topic': 'bidmas',
                    'mode': 'practice',
                    'difficulty': 'foundational',
                    'action': 'start',
                },
                follow_redirects=True,
            )
            assert r.status_code == 200, r.data
            body = r.data.decode()
            if 'free-response-inline' in body:
                assert 'free-response-check-btn' in body
                return
    raise AssertionError('expected free-response UI for a pilot BIDMAS variant')


def main():
    test_checker_unit()
    test_bidmas_variants_expose_raw()
    test_bidmas_generator_payload()
    test_check_api_without_session()
    test_check_api_with_session_binding()
    test_generator_page_renders_free_response()
    print('test_answer_check_smoke: all checks passed')


if __name__ == '__main__':
    main()
