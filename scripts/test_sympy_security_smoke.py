"""SymPy grading security smoke — RCE payloads must not execute.

Run: python scripts/test_sympy_security_smoke.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from generators.shared.answer_checkers import (  # noqa: E402
    _is_safe_math_expr,
    _safe_sympify,
    check_algebraic,
    check_quadratic_roots,
)
from app import app  # noqa: E402


RCE_PAYLOADS = (
    "__import__('os').name",
    "__import__('os').system('echo pwned')",
    "().__class__.__mro__",
    "os.system('id')",
    "getattr(__import__('os'), 'system')('id')",
)


def test_safe_sympify_rejects_rce_payloads():
    for payload in RCE_PAYLOADS:
        assert _is_safe_math_expr(payload) is False, payload
        assert _safe_sympify(payload) is None, payload
        assert check_algebraic('a-b', payload)['correct'] is False, payload
        assert check_quadratic_roots('1,2', payload)['correct'] is False, payload


def test_safe_sympify_accepts_legit_math():
    assert check_algebraic('a-b', 'a-b')['correct'] is True
    assert check_algebraic('3*t**2/2', '1.5*t**2')['correct'] is True
    assert check_quadratic_roots('3,-2', '3, -2')['correct'] is True
    assert _safe_sympify('3*t**2/2') is not None


def test_check_api_rejects_sessionless_sympy_types():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': "__import__('os').name",
                'correct_answer_raw': 'a-b',
                'answer_type': 'algebraic',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 400, r.data
        data = r.get_json()
        assert data.get('code') == 'session_required'


def test_check_api_session_bound_rce_is_incorrect_not_500():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'surds',
                'mode': 'practice',
                'difficulty': 'intermediate',
                'problem': {
                    'correct_answer_raw': 'a-b',
                    'answer_type': 'algebraic',
                },
            }
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': "__import__('os').name",
                'correct_answer_raw': 'a-b',
                'answer_type': 'algebraic',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is False


def test_check_api_rejects_overlong_answer():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '1' * 2001,
                'correct_answer_raw': '1',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 400, r.data
        assert r.get_json().get('code') == 'answer_too_long'


if __name__ == '__main__':
    tests = [v for k, v in sorted(globals().items()) if k.startswith('test_')]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f'OK  {fn.__name__}')
        except Exception as exc:
            failed += 1
            print(f'FAIL {fn.__name__}: {exc}')
    if failed:
        sys.exit(1)
    print(f'All {len(tests)} sympy security smoke tests passed.')
