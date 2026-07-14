"""Server-side answer checkers for typed (non-MCQ) practice questions."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

CHECKERS: dict[str, callable] = {}


def register_checker(name: str):
    def decorator(fn):
        CHECKERS[name] = fn
        return fn
    return decorator


def _normalize_numeric_string(value) -> str:
    s = str(value or '').strip()
    s = s.replace(',', '').replace('°', '')
    s = s.replace('\u2212', '-').replace('−', '-')
    if s.startswith('+'):
        s = s[1:].strip()
    return s


def _parse_number(value) -> Decimal | None:
    s = _normalize_numeric_string(value)
    if not s:
        return None
    if not re.fullmatch(r'-?\d+(?:\.\d+)?', s):
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _format_number(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(int(value))
    normalized = format(value.normalize(), 'f')
    if '.' in normalized:
        normalized = normalized.rstrip('0').rstrip('.')
    return normalized


@register_checker('number')
def check_number(correct_raw, user_answer):
    expected = _parse_number(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_user = _normalize_numeric_string(user_answer)
    if not normalized_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': _format_number(expected),
            'feedback': 'Enter a number.',
        }

    actual = _parse_number(user_answer)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': normalized_user,
            'normalized_correct': _format_number(expected),
            'feedback': 'Enter a valid number (digits only, optional decimal point).',
        }

    correct = actual == expected
    return {
        'correct': correct,
        'normalized_user': _format_number(actual),
        'normalized_correct': _format_number(expected),
        'feedback': 'Correct!' if correct else 'Not quite — check your working.',
    }


def check_answer(answer_type: str, correct_raw, user_answer) -> dict:
    checker = CHECKERS.get(answer_type)
    if not checker:
        raise ValueError(f'unknown_answer_type:{answer_type}')
    return checker(correct_raw, user_answer)
