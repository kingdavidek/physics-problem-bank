"""Server-side answer checkers for typed (non-MCQ) practice questions."""

from __future__ import annotations

import re
import math
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


def _parse_fraction_or_number(value) -> Decimal | None:
    """Parse a plain number or a fraction with exactly one slash."""
    s = _normalize_numeric_string(value)
    if not s:
        return None
    if '/' not in s:
        return _parse_number(s)
    if s.count('/') != 1:
        return None
    num_s, den_s = s.split('/', 1)
    num = _parse_number(num_s.strip())
    den = _parse_number(den_s.strip())
    if num is None or den is None or den == 0:
        return None
    return num / den


def _looks_like_fraction(value) -> bool:
    return '/' in str(value or '')


def _format_number(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(int(value))
    normalized = format(value.normalize(), 'f')
    if '.' in normalized:
        normalized = normalized.rstrip('0').rstrip('.')
    return normalized


def _parse_standard_form_pair(raw) -> tuple[Decimal, int] | None:
    """Parse 'coefficient|exponent' into a canonical standard-form pair."""
    s = str(raw or '').strip()
    if '|' not in s:
        return None
    coeff_s, exp_s = s.split('|', 1)
    coeff = _parse_number(coeff_s)
    exp_val = _parse_number(exp_s)
    if coeff is None or exp_val is None:
        return None
    if exp_val != exp_val.to_integral_value():
        return None
    exp = int(exp_val)
    if coeff == 0:
        return Decimal('0'), 0
    c = coeff
    e = exp
    while abs(c) >= 10:
        c /= Decimal('10')
        e += 1
    while abs(c) < 1:
        c *= Decimal('10')
        e -= 1
    return c, e


def _format_standard_form(coeff: Decimal, exp: int) -> str:
    return f'{_format_number(coeff)}|{exp}'


@register_checker('standard_form')
def check_standard_form(correct_raw, user_answer):
    expected = _parse_standard_form_pair(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_coeff, exp_power = expected
    normalized_correct = _format_standard_form(exp_coeff, exp_power)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the coefficient and power of 10.',
        }

    actual = _parse_standard_form_pair(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a valid coefficient and a whole-number power (e.g. 3.2 and 5).',
        }

    act_coeff, act_power = actual
    correct = act_coeff == exp_coeff and act_power == exp_power
    normalized_user = _format_standard_form(act_coeff, act_power)
    return {
        'correct': correct,
        'normalized_user': normalized_user,
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your coefficient and power.',
    }


@register_checker('bearing')
def check_bearing(correct_raw, user_answer):
    expected_s = _normalize_numeric_string(correct_raw)
    expected = _parse_number(expected_s)
    if expected is None:
        raise ValueError('invalid_correct_answer')
    expected_deg = int(round(expected)) % 360
    normalized_correct = f'{expected_deg:03d}'

    user_s = _normalize_numeric_string(user_answer)
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a 3-figure bearing.',
        }

    actual = _parse_number(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a valid bearing (e.g. 045 or 045°).',
        }

    actual_deg = int(round(actual)) % 360
    correct = actual_deg == expected_deg
    return {
        'correct': correct,
        'normalized_user': f'{actual_deg:03d}',
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your bearing.',
    }


@register_checker('number')
def check_number(correct_raw, user_answer):
    expected = _parse_fraction_or_number(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = (
        str(correct_raw).strip()
        if _looks_like_fraction(correct_raw)
        else _format_number(expected)
    )

    normalized_user = _normalize_numeric_string(user_answer)
    if not normalized_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a number.',
        }

    actual = _parse_fraction_or_number(user_answer)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': normalized_user,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a valid number or fraction with one slash (e.g. 1/16).',
        }

    correct = actual == expected
    normalized_user_out = (
        normalized_user
        if _looks_like_fraction(user_answer)
        else _format_number(actual)
    )
    return {
        'correct': correct,
        'normalized_user': normalized_user_out,
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your working.',
    }


def _strip_pi_suffix(value) -> str:
    """Remove a trailing π/pi so users can type 4 or 4π."""
    s = str(value or '').strip()
    s = s.replace(',', '').replace('\u2212', '-').replace('−', '-')
    if s.startswith('+'):
        s = s[1:].strip()
    s = re.sub(r'(?i)\s*[*×x]?\s*(π|pi)\s*$', '', s).strip()
    return s


@register_checker('pi_multiple')
def check_pi_multiple(correct_raw, user_answer):
    """Grade the coefficient of a multiple of π (UI shows π beside the input)."""
    expected = _parse_fraction_or_number(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = (
        str(correct_raw).strip()
        if _looks_like_fraction(correct_raw)
        else _format_number(expected)
    ) + 'π'

    raw_user = str(user_answer or '').strip()
    if not raw_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the coefficient of π.',
        }

    stripped = _strip_pi_suffix(raw_user)
    if not stripped:
        return {
            'correct': False,
            'normalized_user': raw_user,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the number that multiplies π.',
        }

    actual = _parse_fraction_or_number(stripped)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': stripped,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a number or fraction (π is already shown).',
        }

    correct = actual == expected
    normalized_user_out = (
        stripped if _looks_like_fraction(stripped) else _format_number(actual)
    ) + 'π'
    return {
        'correct': correct,
        'normalized_user': normalized_user_out,
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your working.',
    }


def _normalize_surd_string(value) -> str:
    s = str(value or '').strip()
    s = s.replace('\u221a', '√').replace('−', '-').replace('\u2212', '-')
    s = re.sub(r'\s+', '', s)
    if s.startswith('+'):
        s = s[1:]
    return s


def _simplify_surd_pair(coeff: Decimal, radicand: Decimal) -> tuple[Decimal, Decimal] | None:
    if radicand <= 0:
        return None
    if radicand == 1:
        return coeff, Decimal('1')
    if radicand != radicand.to_integral_value():
        return coeff, radicand
    r = int(radicand)
    c = coeff
    i = 2
    while i * i <= r:
        sq = i * i
        if r % sq == 0:
            c *= Decimal(i)
            r //= sq
        else:
            i += 1
    return c, Decimal(r)


def _parse_surd_pair(raw) -> tuple[Decimal, Decimal] | None:
    """Parse expected surd stored as radicand or coeff|radicand."""
    s = str(raw or '').strip()
    if '|' in s:
        coeff_s, rad_s = s.split('|', 1)
        coeff = _parse_fraction_or_number(coeff_s)
        rad = _parse_number(rad_s)
        if coeff is None or rad is None:
            return None
        return _simplify_surd_pair(coeff, rad)
    rad = _parse_number(s)
    if rad is None:
        return None
    return _simplify_surd_pair(Decimal('1'), rad)


def _parse_surd_expression(value) -> tuple[Decimal, Decimal] | None:
    s = _normalize_surd_string(value)
    if not s:
        return None

    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)[*×x]?√(\d+(?:\.\d+)?)', s)
    if m:
        coeff = _parse_fraction_or_number(m.group(1))
        rad = _parse_number(m.group(2))
        if coeff is None or rad is None:
            return None
        return _simplify_surd_pair(coeff, rad)

    m = re.fullmatch(r'√(\d+(?:\.\d+)?)', s)
    if m:
        rad = _parse_number(m.group(1))
        if rad is None:
            return None
        return _simplify_surd_pair(Decimal('1'), rad)

    m = re.fullmatch(r'(?i)(-?\d+(?:\.\d+)?)\*?sqrt\((\d+(?:\.\d+)?)\)', s)
    if m:
        coeff = _parse_fraction_or_number(m.group(1))
        rad = _parse_number(m.group(2))
        if coeff is None or rad is None:
            return None
        return _simplify_surd_pair(coeff, rad)

    m = re.fullmatch(r'(?i)sqrt\((\d+(?:\.\d+)?)\)', s)
    if m:
        rad = _parse_number(m.group(1))
        if rad is None:
            return None
        return _simplify_surd_pair(Decimal('1'), rad)

    if '√' not in s and 'sqrt' not in s.lower():
        val = _parse_fraction_or_number(s)
        if val is not None:
            return _simplify_surd_pair(val, Decimal('1'))

    return None


def _format_surd(coeff: Decimal, radicand: Decimal) -> str:
    if radicand == 1:
        return _format_number(coeff)
    if coeff == 1 or coeff == Decimal('1'):
        return f'√{_format_number(radicand)}'
    if coeff == -1 or coeff == Decimal('-1'):
        return f'-√{_format_number(radicand)}'
    return f'{_format_number(coeff)}√{_format_number(radicand)}'


@register_checker('surd')
def check_surd(correct_raw, user_answer):
    expected = _parse_surd_pair(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_coeff, exp_rad = expected
    normalized_correct = _format_surd(exp_coeff, exp_rad)

    raw_user = str(user_answer or '').strip()
    if not raw_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter your answer in surd form.',
        }

    actual = _parse_surd_expression(raw_user)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': raw_user,
            'normalized_correct': normalized_correct,
            'feedback': 'Use surd form, e.g. √113 or 2√5 (click √ to insert the symbol).',
        }

    act_coeff, act_rad = actual
    correct = act_coeff == exp_coeff and act_rad == exp_rad
    return {
        'correct': correct,
        'normalized_user': _format_surd(act_coeff, act_rad),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your surd form.',
    }


def _parse_number_estimate_raw(raw) -> tuple[Decimal, Decimal] | None:
    s = str(raw or '').strip()
    if '~' in s:
        value_s, tol_s = s.split('~', 1)
    elif '|' in s:
        value_s, tol_s = s.split('|', 1)
    else:
        return None
    expected = _parse_fraction_or_number(value_s)
    tolerance = _parse_number(tol_s)
    if expected is None or tolerance is None or tolerance < 0:
        return None
    return expected, tolerance


@register_checker('number_estimate')
def check_number_estimate(correct_raw, user_answer):
    parsed = _parse_number_estimate_raw(correct_raw)
    if parsed is None:
        raise ValueError('invalid_correct_answer')

    expected, tolerance = parsed
    normalized_correct = _format_number(expected)

    normalized_user = _normalize_numeric_string(user_answer)
    if not normalized_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter your estimate from the graph.',
        }

    actual = _parse_fraction_or_number(user_answer)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': normalized_user,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a valid number for your estimate.',
        }

    diff = abs(actual - expected)
    correct = diff <= tolerance
    normalized_user_out = (
        normalized_user
        if _looks_like_fraction(user_answer)
        else _format_number(actual)
    )
    return {
        'correct': correct,
        'normalized_user': normalized_user_out,
        'normalized_correct': normalized_correct,
        'feedback': (
            'Correct!'
            if correct
            else 'Not quite — check your estimate from the line of best fit.'
        ),
    }


def check_answer(answer_type: str, correct_raw, user_answer) -> dict:
    checker = CHECKERS.get(answer_type)
    if not checker:
        raise ValueError(f'unknown_answer_type:{answer_type}')
    return checker(correct_raw, user_answer)


def _parse_delimited_numbers(raw, delimiter=',') -> list[Decimal] | None:
    s = str(raw or '').strip()
    if not s:
        return None
    parts = [p.strip() for p in s.split(delimiter)]
    if not parts or any(not p for p in parts):
        return None
    nums = []
    for part in parts:
        val = _parse_number(part)
        if val is None:
            return None
        nums.append(val)
    return nums


def _format_number_list(nums: list[Decimal]) -> str:
    return ','.join(_format_number(n) for n in nums)


def _parse_number_field_part(part) -> tuple[str, object] | None:
    """Parse one pipe-delimited field as a number or ratio (a:b)."""
    s = str(part or '').strip()
    if not s:
        return None
    if ':' in s or '|' in s:
        ratio = _parse_ratio_parts(s)
        if ratio is not None:
            return 'ratio', _normalize_ratio_parts(*ratio)
    num = _parse_fraction_or_number(s)
    if num is not None:
        return 'number', num
    return None


def _format_number_field_part(kind: str, value) -> str:
    if kind == 'ratio':
        return _format_ratio(*value)
    return _format_number(value)


def _parse_number_fields(raw) -> list[tuple[str, object]] | None:
    """Parse pipe-delimited fields; each may be a number/fraction or ratio."""
    s = str(raw or '').strip()
    if not s:
        return None
    sep = '\x1e' if '\x1e' in s else '|'
    parts = [part.strip() for part in s.split(sep)]
    if not parts or any(not part for part in parts):
        return None
    values = [_parse_number_field_part(part) for part in parts]
    if any(value is None for value in values):
        return None
    return values


def _normalize_number_fields(raw) -> str:
    parsed = _parse_number_fields(raw)
    s = str(raw or '').strip()
    sep = '\x1e' if '\x1e' in s else '|'
    if parsed is None:
        return sep.join(part.strip() for part in s.split(sep))
    return sep.join(_format_number_field_part(kind, val) for kind, val in parsed)


@register_checker('number_fields')
def check_number_fields(correct_raw, user_answer):
    expected = _parse_number_fields(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = _normalize_number_fields(correct_raw)
    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Complete every answer field.',
        }

    actual = _parse_number_fields(user_s)
    if actual is None or len(actual) != len(expected):
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': (
                f'Enter a valid number, fraction, or ratio (a:b) in all {len(expected)} fields. '
                'Use at most one slash per fraction.'
            ),
        }

    correct = all(
        exp_val == act_val
        for (_, exp_val), (_, act_val) in zip(expected, actual)
    )
    return {
        'correct': correct,
        'normalized_user': _normalize_number_fields(user_s),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check each field.',
    }


def _parse_ratio_parts(value) -> tuple[int, int] | None:
    """Parse a ratio from a:b or a|b notation (positive integers only)."""
    s = _normalize_numeric_string(value).replace(' ', '')
    if '|' in s:
        parts = s.split('|', 1)
    elif ':' in s:
        parts = s.split(':', 1)
    else:
        return None
    if len(parts) != 2:
        return None
    a = _parse_number(parts[0])
    b = _parse_number(parts[1])
    if a is None or b is None:
        return None
    if a != a.to_integral_value() or b != b.to_integral_value():
        return None
    ai, bi = int(a), int(b)
    if ai <= 0 or bi <= 0:
        return None
    return ai, bi


def _normalize_ratio_parts(a: int, b: int) -> tuple[int, int]:
    g = math.gcd(a, b)
    return a // g, b // g


def _format_ratio(a: int, b: int) -> str:
    return f'{a}:{b}'


def _ratio_checker_result(correct: bool, user_parts: tuple[int, int], expected_parts: tuple[int, int]) -> dict:
    exp_n = _normalize_ratio_parts(*expected_parts)
    act_n = _normalize_ratio_parts(*user_parts)
    return {
        'correct': correct,
        'normalized_user': _format_ratio(*act_n),
        'normalized_correct': _format_ratio(*exp_n),
        'feedback': 'Correct!' if correct else 'Not quite — check your ratio.',
    }


@register_checker('ratio')
def check_ratio(correct_raw, user_answer):
    expected = _parse_ratio_parts(str(correct_raw or '').replace('|', ':'))
    if expected is None:
        raise ValueError('invalid_correct_answer')

    user_parts = _parse_ratio_parts(user_answer)
    if user_parts is None:
        return {
            'correct': False,
            'normalized_user': str(user_answer or '').strip(),
            'normalized_correct': _format_ratio(*_normalize_ratio_parts(*expected)),
            'feedback': 'Enter a ratio as a:b (e.g. 3:5).',
        }

    exp_n = _normalize_ratio_parts(*expected)
    act_n = _normalize_ratio_parts(*user_parts)
    return _ratio_checker_result(exp_n == act_n, user_parts, expected)


@register_checker('ratio_exact')
def check_ratio_exact(correct_raw, user_answer):
    expected = _parse_ratio_parts(str(correct_raw or ''))
    if expected is None:
        raise ValueError('invalid_correct_answer')

    user_parts = _parse_ratio_parts(user_answer)
    if user_parts is None:
        return {
            'correct': False,
            'normalized_user': str(user_answer or '').strip(),
            'normalized_correct': _format_ratio(*expected),
            'feedback': 'Enter a ratio as a:b (e.g. 8:12).',
        }

    return _ratio_checker_result(user_parts == expected, user_parts, expected)


def _parse_linear_equation(value) -> tuple[Decimal, Decimal] | None:
    """Parse y = mx + c (or variants without spaces / y =)."""
    s = str(value or '').strip().lower().replace(' ', '')
    s = re.sub(r'^y=', '', s)
    if not s:
        return None
    m = re.match(r'^([+-]?\d*)x([+-]\d+(?:\.\d+)?)?$', s)
    if m:
        ms, cs = m.group(1), m.group(2)
        if ms in ('', '+'):
            m_val = Decimal(1)
        elif ms == '-':
            m_val = Decimal(-1)
        else:
            m_val = _parse_number(ms)
            if m_val is None:
                return None
        c_val = _parse_number(cs) if cs else Decimal(0)
        if c_val is None:
            return None
        return m_val, c_val
    c_only = _parse_number(s)
    if c_only is not None:
        return Decimal(0), c_only
    return None


def _format_linear_equation(m: Decimal, c: Decimal) -> str:
    mi = int(m) if m == m.to_integral_value() else m
    ci = int(c) if c == c.to_integral_value() else c
    if m == 0:
        return f'y = {ci}'
    if m == 1:
        mx = 'x'
    elif m == -1:
        mx = '-x'
    else:
        mx = f'{mi}x'
    if c == 0:
        return f'y = {mx}'
    if c > 0:
        return f'y = {mx} + {ci}'
    return f'y = {mx} - {abs(int(c) if c == c.to_integral_value() else c)}'


@register_checker('linear_equation')
def check_linear_equation(correct_raw, user_answer):
    s = str(correct_raw or '').strip()
    if '|' in s:
        m_s, c_s = s.split('|', 1)
    elif ':' in s:
        m_s, c_s = s.split(':', 1)
    else:
        raise ValueError('invalid_correct_answer')
    exp_m = _parse_number(m_s)
    exp_c = _parse_number(c_s)
    if exp_m is None or exp_c is None:
        raise ValueError('invalid_correct_answer')

    actual = _parse_linear_equation(user_answer)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': str(user_answer or '').strip(),
            'normalized_correct': _format_linear_equation(exp_m, exp_c),
            'feedback': 'Enter the equation as y = mx + c (e.g. y = 2x + 3).',
        }
    act_m, act_c = actual
    correct = act_m == exp_m and act_c == exp_c
    return {
        'correct': correct,
        'normalized_user': _format_linear_equation(act_m, act_c),
        'normalized_correct': _format_linear_equation(exp_m, exp_c),
        'feedback': 'Correct!' if correct else 'Not quite — check your gradient and y-intercept.',
    }


_KEYWORD_ALIASES = {
    'positive': ('positive', 'positive correlation'),
    'negative': ('negative', 'negative correlation'),
    'none': ('none', 'no correlation', 'no'),
    'yes': ('yes', 'right-angled', 'right angled'),
    'no': ('no', 'not right-angled', 'not right angled'),
    'float': ('float', 'floats'),
    'sink': ('sink', 'sinks'),
    'object b': ('object b', 'b'),
    'material y': ('material y', 'y'),
    'stone b': ('stone b', 'b'),
    'ne': ('ne', 'north-east', 'north east', 'ne (between north and east)'),
    'se': ('se', 'south-east', 'south east', 'se (between east and south)'),
    'sw': ('sw', 'south-west', 'south west', 'sw (between south and west)'),
    'nw': ('nw', 'north-west', 'north west', 'nw (between west and north)'),
    'lossy': ('lossy',),
    'lossless': ('lossless',),
    'doubles': (
        'doubles',
        'double',
        'doubles the file size',
        'double the file size',
        'twice',
        'twice as large',
        '2 times',
        'x2',
    ),
}


def _normalize_keyword(value) -> str:
    return re.sub(r'\s+', ' ', str(value or '').strip().lower())


@register_checker('keyword')
def check_keyword(correct_raw, user_answer):
    correct_key = _normalize_keyword(correct_raw)
    aliases = _KEYWORD_ALIASES.get(correct_key, (correct_key,))
    user = _normalize_keyword(user_answer)
    if not user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': correct_key,
            'feedback': 'Enter an answer.',
        }
    ok = any(alias in user or user == alias for alias in aliases)
    return {
        'correct': ok,
        'normalized_user': user,
        'normalized_correct': correct_key,
        'feedback': 'Correct!' if ok else 'Not quite — check your wording.',
    }


def _parse_number_pair(raw) -> tuple[Decimal, Decimal] | None:
    s = str(raw or '').strip()
    if '|' not in s:
        return None
    left, right = s.split('|', 1)
    a = _parse_number(left)
    b = _parse_number(right)
    if a is None or b is None:
        return None
    return a, b


def _format_number_pair(a: Decimal, b: Decimal) -> str:
    return f'{_format_number(a)}|{_format_number(b)}'


def _parse_power_pair(raw) -> tuple[int, int] | None:
    s = str(raw or '').strip()
    if '|' not in s:
        return None
    base_s, exp_s = s.split('|', 1)
    base = _parse_number(base_s.strip())
    exp_val = _parse_number(exp_s.strip())
    if base is None or exp_val is None:
        return None
    if base != base.to_integral_value() or exp_val != exp_val.to_integral_value():
        return None
    return int(base), int(exp_val)


def _format_power_pair(base: int, exponent: int) -> str:
    return f'{base}|{exponent}'


@register_checker('power')
def check_power(correct_raw, user_answer):
    expected = _parse_power_pair(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_base, exp_power = expected
    normalized_correct = _format_power_pair(exp_base, exp_power)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the base and index.',
        }

    actual = _parse_power_pair(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a whole-number base and index (e.g. 2 and 12).',
        }

    act_base, act_power = actual
    correct = act_base == exp_base and act_power == exp_power
    return {
        'correct': correct,
        'normalized_user': _format_power_pair(act_base, act_power),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check the base and index.',
    }


@register_checker('number_pair')
def check_number_pair(correct_raw, user_answer):
    expected = _parse_number_pair(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_a, exp_b = expected
    normalized_correct = _format_number_pair(exp_a, exp_b)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter both values.',
        }

    actual = _parse_number_pair(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a valid number in each box.',
        }

    act_a, act_b = actual
    correct = act_a == exp_a and act_b == exp_b
    return {
        'correct': correct,
        'normalized_user': _format_number_pair(act_a, act_b),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check both values.',
    }


@register_checker('number_list')
def check_number_list(correct_raw, user_answer):
    expected = _parse_delimited_numbers(correct_raw, ',')
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = _format_number_list(expected)
    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter your answer.',
        }

    actual = _parse_delimited_numbers(user_s, ',')
    if actual is None or len(actual) != len(expected):
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': f'Enter {len(expected)} numbers separated by commas.',
        }

    correct = actual == expected
    return {
        'correct': correct,
        'normalized_user': _format_number_list(actual),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check the order and values.',
    }


def _normalize_bit_string(value) -> str:
    return re.sub(r'\s+', '', str(value or '').strip())


def _normalize_hex_string(value) -> str:
    return str(value or '').strip().upper().replace('0X', '').replace(' ', '')


def _parse_width_value_spec(raw, *, kind: str) -> tuple[int, str] | None:
    s = str(raw or '').strip()
    if '|' in s:
        width_s, value = s.split('|', 1)
        try:
            width = int(width_s.strip())
        except ValueError:
            return None
    else:
        width = 0
        value = s
    if kind == 'binary':
        value = _normalize_bit_string(value)
        if not value or not re.fullmatch(r'[01]+', value):
            return None
    else:
        value = _normalize_hex_string(value)
        if not value or not re.fullmatch(r'[0-9A-F]+', value):
            return None
    if width < 0:
        return None
    return width, value


def _canonical_binary(bits: str, width: int) -> str | None:
    bits = _normalize_bit_string(bits)
    if not bits or not re.fullmatch(r'[01]+', bits):
        return None
    if width > 0:
        if len(bits) > width:
            return None
        return format(int(bits, 2), f'0{width}b')
    return bits.lstrip('0') or '0'


def _canonical_hex(hex_value: str, width: int) -> str | None:
    hex_value = _normalize_hex_string(hex_value)
    if not hex_value or not re.fullmatch(r'[0-9A-F]+', hex_value):
        return None
    if width > 0:
        if len(hex_value) > width:
            return None
        return format(int(hex_value, 16), f'0{width}X')
    return format(int(hex_value, 16), 'X')


def _format_binary_spec(width: int, bits: str) -> str:
    return f'{width}|{_canonical_binary(bits, width)}'


def _format_hex_spec(width: int, hex_value: str) -> str:
    return f'{width}|{_canonical_hex(hex_value, width)}'


@register_checker('binary')
def check_binary(correct_raw, user_answer):
    expected = _parse_width_value_spec(correct_raw, kind='binary')
    if expected is None:
        raise ValueError('invalid_correct_answer')

    width, expected_bits = expected
    normalized_correct = _format_binary_spec(width, expected_bits)
    exp_canonical = _canonical_binary(expected_bits, width)

    user_s = _normalize_bit_string(user_answer)
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a binary number using 0 and 1.',
        }

    act_canonical = _canonical_binary(user_s, width)
    if act_canonical is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Use only the digits 0 and 1.',
        }

    correct = act_canonical == exp_canonical
    return {
        'correct': correct,
        'normalized_user': act_canonical,
        'normalized_correct': normalized_correct.split('|', 1)[1],
        'feedback': 'Correct!' if correct else 'Not quite — check your binary digits.',
    }


@register_checker('hex')
def check_hex(correct_raw, user_answer):
    expected = _parse_width_value_spec(correct_raw, kind='hex')
    if expected is None:
        raise ValueError('invalid_correct_answer')

    width, expected_hex = expected
    normalized_correct = _format_hex_spec(width, expected_hex)
    exp_canonical = _canonical_hex(expected_hex, width)

    user_s = _normalize_hex_string(user_answer)
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a hexadecimal value (0–9, A–F).',
        }

    act_canonical = _canonical_hex(user_s, width)
    if act_canonical is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Use hexadecimal digits 0–9 and A–F only.',
        }

    correct = act_canonical == exp_canonical
    return {
        'correct': correct,
        'normalized_user': act_canonical,
        'normalized_correct': normalized_correct.split('|', 1)[1],
        'feedback': 'Correct!' if correct else 'Not quite — check your hex digits.',
    }
