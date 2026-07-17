"""Phase 1 numeric auto-grade smoke — run: python scripts/test_phase1_numeric_smoke.py

Covers:
  - All Phase 1 answer_type checkers (unit + /api/v1/problems/check)
  - Spot-check graded practice problems across Phase 1 topics
  - Session binding / mismatch behaviour
  - Quick Test free-response payload includes grading fields
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402
from generators.shared.answer_checkers import CHECKERS, check_answer  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

# Phase 1 topics expected to expose at least one graded practice variant.
# decimals / multiples_factors remain ungraded (still on the Phase 1 backlog).
PHASE1_TOPICS = (
    ('gcse', 'maths', 'bidmas'),
    ('gcse', 'maths', 'number'),
    ('gcse', 'maths', 'probability'),
    ('gcse', 'maths', 'statistics'),
    ('gcse', 'maths', 'graphs'),
    ('gcse', 'maths', 'ratio_proportion'),
    ('gcse', 'maths', 'geometry_angles'),
    ('gcse', 'maths', 'mensuration'),
    ('gcse', 'maths', 'pythagoras'),
    ('gcse', 'maths', 'compound_measures'),
    ('gcse', 'maths', 'bearings'),
    ('gcse', 'maths', 'sequences'),
    ('gcse', 'cs', 'data_rep'),
    ('gcse', 'cs', 'algorithms'),
    ('gcse', 'cs', 'computer_systems'),
    ('gcse', 'cs', 'computer_networks'),
)

DIFFICULTIES = ('foundational', 'intermediate', 'difficult')

# (answer_type, correct_raw, good_user, bad_user)
CHECKER_CASES = (
    ('number', '42', '42', '41'),
    ('number', '1/2', '0.5', '1/3'),
    ('fraction', '3/4', '0.75', '1/2'),
    ('fraction', '3/2', '1 1/2', '1 1/3'),
    ('standard_form', '3.2|5', '3.2|5', '3.2|4'),
    ('number_pair', '3|4', '3|4', '3|5'),
    ('number_list', '1,2,3', '1,2,3', '1,2,4'),
    ('power', '2|10', '2|10', '2|9'),
    ('number_fields', '12|5', '12|5', '12|6'),
    ('ratio', '2|3', '4:6', '2:5'),
    ('ratio_exact', '8|12', '8:12', '2:3'),
    ('linear_equation', '2|3', 'y = 2x + 3', 'y=2x+4'),
    ('keyword', 'positive', 'Positive', 'negative'),
    ('number_estimate', '10~2', '11', '20'),
    ('bearing', '045', '45', '046'),
    ('pi_multiple', '4', '4', '5'),
    ('pi_multiple', '1/2', '0.5π', '1'),
    ('surd', '1|113', '√113', '√112'),
    ('binary', '8|10010110', '10010110', '10010111'),
    ('hex', '0|FF', 'ff', 'FE'),
)


def _assert_check_result(result, *, expect_correct):
    assert isinstance(result, dict), result
    assert 'correct' in result
    assert 'normalized_user' in result
    assert 'normalized_correct' in result
    assert 'feedback' in result
    assert result['correct'] is expect_correct, result


def test_all_phase1_checkers_registered():
    expected = {case[0] for case in CHECKER_CASES}
    missing = expected - set(CHECKERS)
    assert not missing, f'Missing checkers: {sorted(missing)}'


def test_checker_unit_cases():
    for answer_type, correct_raw, good, bad in CHECKER_CASES:
        ok = check_answer(answer_type, correct_raw, good)
        _assert_check_result(ok, expect_correct=True)
        wrong = check_answer(answer_type, correct_raw, bad)
        _assert_check_result(wrong, expect_correct=False)


def test_check_api_all_answer_types():
    with app.test_client() as client:
        for answer_type, correct_raw, good, bad in CHECKER_CASES:
            r = client.post(
                '/api/v1/problems/check',
                json={
                    'user_answer': good,
                    'correct_answer_raw': correct_raw,
                    'answer_type': answer_type,
                },
                headers={'Accept': 'application/json'},
            )
            assert r.status_code == 200, (answer_type, r.data)
            body = r.get_json()
            assert body.get('ok') is True
            assert body.get('correct') is True, (answer_type, body)

            r = client.post(
                '/api/v1/problems/check',
                json={
                    'user_answer': bad,
                    'correct_answer_raw': correct_raw,
                    'answer_type': answer_type,
                },
                headers={'Accept': 'application/json'},
            )
            assert r.status_code == 200, (answer_type, r.data)
            assert r.get_json().get('correct') is False, answer_type


def test_check_api_validation_errors():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            data='not-json',
            headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
        )
        assert r.status_code == 400

        r = client.post(
            '/api/v1/problems/check',
            json={'correct_answer_raw': '1', 'answer_type': 'number'},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 400
        assert r.get_json().get('code') == 'missing_fields'

        r = client.post(
            '/api/v1/problems/check',
            json={'user_answer': '1', 'answer_type': 'number'},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 400
        assert r.get_json().get('code') == 'missing_fields'

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '1',
                'correct_answer_raw': '1',
                'answer_type': 'not_a_real_type',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 400
        assert r.get_json().get('code') == 'unknown_answer_type'


def test_check_api_session_mismatch():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
                'problem': {
                    'correct_answer_raw': '14',
                    'answer_type': 'number',
                },
            }

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
        assert r.get_json()['correct'] is True

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '99',
                'correct_answer_raw': '99',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 403, r.data
        assert r.get_json().get('code') == 'session_mismatch'


def _first_graded_problem(level, subject, topic):
    cfg = TOPICS[level][subject][topic]
    func = cfg['func']
    variants_func = cfg.get('variants_func')
    for difficulty in DIFFICULTIES:
        if variants_func:
            try:
                variants = variants_func(difficulty, 'practice') or []
            except TypeError:
                variants = variants_func(difficulty) or []
            for vf in variants:
                name = getattr(vf, '__name__', None)
                try:
                    problem = func(difficulty, 'practice', variant_name=name)
                except TypeError:
                    problem = func(difficulty, 'practice')
                if problem and problem.get('correct_answer_raw') and not problem.get('options'):
                    return difficulty, name, problem
        else:
            for _ in range(6):
                problem = func(difficulty, 'practice')
                if problem and problem.get('correct_answer_raw') and not problem.get('options'):
                    return difficulty, None, problem
    return None, None, None


def test_phase1_topics_expose_graded_problem_and_check():
    with app.test_client() as client:
        for level, subject, topic in PHASE1_TOPICS:
            difficulty, variant, problem = _first_graded_problem(level, subject, topic)
            assert problem is not None, f'No graded practice problem for {level}/{subject}/{topic}'
            raw = str(problem['correct_answer_raw'])
            answer_type = problem.get('answer_type') or 'number'

            user_answer = _user_answer_from_raw(raw, answer_type)
            r = client.post(
                '/api/v1/problems/check',
                json={
                    'user_answer': user_answer,
                    'correct_answer_raw': raw,
                    'answer_type': answer_type,
                    'level': level,
                    'subject': subject,
                    'topic': topic,
                    'difficulty': difficulty,
                },
                headers={'Accept': 'application/json'},
            )
            assert r.status_code == 200, (
                f'{level}/{subject}/{topic}/{variant}: {r.data}'
            )
            body = r.get_json()
            assert body.get('correct') is True, (
                f'{level}/{subject}/{topic}/{variant} type={answer_type} raw={raw!r} -> {body}'
            )


def _user_answer_from_raw(raw, answer_type):
    """Build a user_answer the checker should accept for the stored raw."""
    if answer_type == 'standard_form':
        return raw  # coeff|exp
    if answer_type == 'number_pair':
        return raw
    if answer_type == 'power':
        return raw
    if answer_type == 'number_fields':
        # Prefer full multipart answer when possible
        return raw.replace('\x1e', '|')
    if answer_type == 'ratio' or answer_type == 'ratio_exact':
        if '|' in raw:
            return raw.replace('|', ':')
        return raw
    if answer_type == 'binary':
        # width|bits → user enters bits only
        return raw.split('|', 1)[1] if '|' in raw else raw
    if answer_type == 'hex':
        return raw.split('|', 1)[1] if '|' in raw else raw
    if answer_type == 'bearing':
        return raw
    if answer_type == 'number_estimate':
        # centre~tol → submit centre
        return raw.split('~', 1)[0]
    if answer_type == 'surd':
        # coeff|radicand
        if '|' in raw:
            coeff, rad = raw.split('|', 1)
            if coeff in ('1', '1.0'):
                return f'√{rad}'
            return f'{coeff}√{rad}'
        return raw
    if answer_type == 'pi_multiple':
        return raw
    return raw


def test_quicktest_api_includes_grading_fields():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/quicktest/start',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        problem = r.get_json().get('problem') or {}
        assert problem.get('correct_answer_raw') is not None
        assert problem.get('answer_type')


def test_generator_api_includes_grading_fields():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/generate',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        problem = r.get_json().get('problem') or {}
        assert problem.get('correct_answer_raw') is not None
        assert problem.get('answer_type') == 'number'


def main():
    test_all_phase1_checkers_registered()
    test_checker_unit_cases()
    test_check_api_all_answer_types()
    test_check_api_validation_errors()
    test_check_api_session_mismatch()
    test_phase1_topics_expose_graded_problem_and_check()
    test_quicktest_api_includes_grading_fields()
    test_generator_api_includes_grading_fields()
    print('test_phase1_numeric_smoke: all checks passed')


if __name__ == '__main__':
    main()
