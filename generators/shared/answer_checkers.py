"""Server-side answer checkers for typed (non-MCQ) practice questions."""

from __future__ import annotations

import re
import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from fractions import Fraction

from sympy import nsimplify, simplify, sympify

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


def _looks_like_mixed_fraction(value) -> bool:
    return bool(re.search(r'\d+\s+\d+/\d+', str(value or '')))


def _format_fraction(fr: Fraction) -> str:
    if fr.denominator == 1:
        return str(fr.numerator)
    return f'{fr.numerator}/{fr.denominator}'


def _parse_fraction_value(value) -> Fraction | None:
    """Parse a fraction, mixed number, decimal, or integer (e.g. 3/4, 1 1/2, 0.75)."""
    s = _normalize_numeric_string(value)
    if not s:
        return None

    mixed = re.fullmatch(r'(-?\d+)\s+(\d+)/(\d+)', s)
    if mixed:
        whole = int(mixed.group(1))
        num = int(mixed.group(2))
        den = int(mixed.group(3))
        if den == 0 or num < 0:
            return None
        sign = -1 if whole < 0 else 1
        abs_whole = abs(whole)
        return Fraction(sign * (abs_whole * den + num), den)

    if '/' in s:
        if s.count('/') != 1:
            return None
        num_s, den_s = s.split('/', 1)
        num = _parse_number(num_s.strip())
        den = _parse_number(den_s.strip())
        if num is None or den is None or den == 0:
            return None
        if num != num.to_integral_value() or den != den.to_integral_value():
            return None
        return Fraction(int(num), int(den))

    as_decimal = _parse_fraction_or_number(s)
    if as_decimal is None:
        return None
    try:
        return Fraction(as_decimal)
    except (ValueError, ZeroDivisionError):
        return None


def _parse_fraction_raw(raw) -> Fraction | None:
    """Parse canonical correct_answer_raw for answer_type fraction."""
    s = str(raw or '').strip()
    if not s:
        return None
    if '|' in s and '/' not in s:
        num_s, den_s = s.split('|', 1)
        num = _parse_number(num_s.strip())
        den = _parse_number(den_s.strip())
        if num is None or den is None or den == 0:
            return None
        if num != num.to_integral_value() or den != den.to_integral_value():
            return None
        return Fraction(int(num), int(den))
    return _parse_fraction_value(s)


def _format_fraction_user_display(user_answer, fr: Fraction) -> str:
    raw = str(user_answer or '').strip()
    if _looks_like_mixed_fraction(raw):
        return _normalize_numeric_string(raw)
    if _looks_like_fraction(raw):
        return _normalize_numeric_string(raw)
    as_decimal = _parse_fraction_or_number(raw)
    if as_decimal is not None:
        return _format_number(as_decimal)
    return _format_fraction(fr)


@register_checker('fraction')
def check_fraction(correct_raw, user_answer):
    expected = _parse_fraction_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = _format_fraction(expected)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a fraction.',
        }

    actual = _parse_fraction_value(user_answer)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': _normalize_numeric_string(user_answer),
            'normalized_correct': normalized_correct,
            'feedback': (
                'Enter a valid fraction, mixed number, or decimal '
                '(e.g. 3/4, 1 1/2, or 0.75).'
            ),
        }

    correct = actual == expected
    return {
        'correct': correct,
        'normalized_user': _format_fraction_user_display(user_answer, actual),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your fraction.',
    }


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


def _split_top_level_division(s: str) -> tuple[str, str] | None:
    """Return (numerator, denominator) when s is a single top-level division."""
    depth = 0
    for i, ch in enumerate(s):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth - 1)
        elif ch == '/' and depth == 0:
            num, den = s[:i], s[i + 1:]
            if num and den:
                return num, den
            return None
    return None


def _wrap_top_level_fraction(s: str) -> str:
    """Canonicalise a/b as (a)/(b) without double-wrapping."""
    split = _split_top_level_division(s)
    if split is None:
        return s
    num, den = split
    if not (num.startswith('(') and num.endswith(')')):
        num = f'({num})'
    if not (den.startswith('(') and den.endswith(')')):
        den = f'({den})'
    return f'{num}/{den}'


def _normalize_algebraic_division(s: str) -> str:
    """Normalise top-level divisions and subject=rhs formulae."""
    if '=' in s:
        subject, rhs = s.split('=', 1)
        return subject + '=' + _wrap_top_level_fraction(rhs)
    return _wrap_top_level_fraction(s)


def _normalize_algebraic_powers(s: str) -> str:
    """Unify t^2, t**2, t*t, and t²."""
    s = re.sub(r'\*\*', '^', s)
    s = s.replace('²', '^2')
    changed = True
    while changed:
        changed = False
        updated = re.sub(r'([a-z])\*\1', r'\1^2', s)
        if updated != s:
            s = updated
            changed = True
    return s


def _normalize_algebraic_implicit_mult(s: str) -> str:
    """Remove * only for implicit multiplication (keep numeric products like 0.5*3)."""
    s = re.sub(r'(\d)\*([a-z(])', r'\1\2', s)
    s = re.sub(r'(\))([a-z(])', r'\1\2', s)
    return s


def _algebraic_uses_bc_vector_difference(correct_raw) -> bool:
    """True when the mark scheme uses a b/c component difference (vector BC style)."""
    s = _algebraic_prepare_for_sympy(correct_raw)
    if not re.search(r'(?<![a-z])b(?![a-z])', s) or not re.search(r'(?<![a-z])c(?![a-z])', s):
        return False
    return bool(re.search(r'\([bc]-[bc]\)|(?<![a-z])[bc]-[bc](?![a-z])', s))


def _algebraic_expand_vector_labels(s: str, correct_raw) -> str:
    """Expand GCSE vector names like BC when the answer uses b and c components."""
    if not _algebraic_uses_bc_vector_difference(correct_raw):
        return s
    s = re.sub(r'(?<![a-z])bc(?![a-z])', '(c-b)', s, flags=re.IGNORECASE)
    s = re.sub(r'(?<![a-z])cb(?![a-z])', '(b-c)', s, flags=re.IGNORECASE)
    return s


def _algebraic_prepare_for_sympy(value, *, context_raw=None) -> str:
    """Convert a student/correct algebraic string into something SymPy can parse."""
    s = str(value or '').strip().lower()
    s = s.replace('\u221a', '√').replace('−', '-').replace('\u2212', '-')
    if '=' in s:
        s = s.split('=', 1)[1]
    s = re.sub(r'\s+', '', s)
    s = s.replace('π', 'pi')
    s = re.sub(r'(?<![a-z])pi(?![a-z])', 'pi', s)
    s = s.replace('²', '**2')
    s = re.sub(
        r'(?i)sqrt\(([^()]*(?:\([^()]*\)[^()]*)*)\)',
        r'sqrt(\1)',
        s,
    )
    s = re.sub(r'√\(([^()]+)\)', r'sqrt(\1)', s)
    s = re.sub(r'√([a-z0-9π]+)', r'sqrt(\1)', s)
    s = re.sub(r'\*\*', '**', s)
    s = re.sub(r'\^', '**', s)
    changed = True
    while changed:
        changed = False
        updated = re.sub(r'([a-z])\*\1', r'\1**2', s)
        if updated != s:
            s = updated
            changed = True
    # Implicit multiplication for SymPy (5t, 3t**2, (s-1)t).
    s = re.sub(r'(\d)([a-z(])', r'\1*\2', s)
    s = re.sub(r'(\))([a-z(])', r'\1*\2', s)
    if context_raw is not None:
        s = _algebraic_expand_vector_labels(s, context_raw)
    return s


def _algebraic_sympy_equivalent(correct_raw, user_raw) -> bool:
    """Fallback: accept equivalent forms such as 0.5*3*t**2 and 3*t**2/2."""
    try:
        correct_expr = sympify(_algebraic_prepare_for_sympy(correct_raw))
        user_expr = sympify(_algebraic_prepare_for_sympy(user_raw, context_raw=correct_raw))
        return bool(simplify(correct_expr - user_expr) == 0)
    except (TypeError, ValueError, SyntaxError, AttributeError, ZeroDivisionError):
        return False


def _normalize_algebraic_sqrt_quotient(s: str) -> str:
    """Collapse √a/√b (and parenthesised variants) to √(a/b)."""
    # Allow π in unparenthesised radicals (after pi → π normalisation).
    atom = r'[a-z0-9π]+'
    # Drop trivial parentheses around a single radical, e.g. (√a)/(√π).
    s = re.sub(rf'\((√\({atom}\)|√{atom}|√\([^()]+\))\)', r'\1', s)
    patterns = (
        r'√\(([^()]+)\)/√\(([^()]+)\)',
        rf'√\(([^()]+)\)/√({atom})',
        rf'√({atom})/√\(([^()]+)\)',
        rf'√({atom})/√({atom})',
    )
    changed = True
    while changed:
        changed = False
        for pattern in patterns:
            updated = re.sub(pattern, r'√(\1/\2)', s)
            if updated != s:
                s = updated
                changed = True
    return s


def _normalize_algebraic_string(value) -> str:
    s = str(value or '').strip().lower()
    s = s.replace('\u221a', '√').replace('−', '-').replace('\u2212', '-')
    s = re.sub(r'(?<![a-z])pi(?![a-z])', 'π', s)
    s = re.sub(
        r'(?i)sqrt\(([^()]*(?:\([^()]*\)[^()]*)*)\)',
        r'√(\1)',
        s,
    )
    s = re.sub(r'\s+', '', s)
    s = _normalize_algebraic_powers(s)
    s = _normalize_algebraic_implicit_mult(s)
    if s.startswith('+'):
        s = s[1:]
    s = _normalize_algebraic_sqrt_quotient(s)
    s = _normalize_algebraic_division(s)
    s = re.sub(r'√\(\(([^()]+)\)/\(([^()]+)\)\)', r'√(\1/\2)', s)
    return s


def _format_algebraic_text(value) -> str:
    return _normalize_algebraic_string(value)


def _algebraic_answers_equivalent(correct_raw, user_raw) -> bool:
    normalized_correct = _format_algebraic_text(correct_raw)
    normalized_user = _format_algebraic_text(user_raw)
    if not normalized_correct or not normalized_user:
        return False
    if normalized_user == normalized_correct:
        return True
    if '=' in normalized_correct:
        subject, rhs = normalized_correct.split('=', 1)
        if normalized_user == rhs:
            return True
        if normalized_user.startswith(subject + '='):
            if normalized_user == normalized_correct:
                return True
    if _algebraic_sympy_equivalent(correct_raw, user_raw):
        return True
    return False


def _parse_algebraic_surd_binomial_raw(raw) -> tuple[int, int, int, str] | None:
    s = str(raw or '').strip()
    parts = s.split('|')
    if len(parts) != 4:
        return None
    const = _parse_number(parts[0])
    coef = _parse_number(parts[1])
    rad = _parse_number(parts[2])
    sign = parts[3].strip()
    if const is None or coef is None or rad is None:
        return None
    if const != const.to_integral_value() or coef != coef.to_integral_value():
        return None
    if rad != rad.to_integral_value() or int(rad) <= 0:
        return None
    if sign not in ('+', '-'):
        return None
    return int(const), int(coef), int(rad), sign


def _format_algebraic_surd_binomial(const: int, coef: int, radicand: int, sign: str) -> str:
    surd = f'√{radicand}' if coef == 1 else f'{coef}√{radicand}'
    op = '+' if sign == '+' else '-'
    return f'{const}{op}{surd}'


def _parse_algebraic_surd_binomial(value) -> tuple[int, int, int, str] | None:
    s = _normalize_algebraic_string(value)
    if not s:
        return None

    patterns = (
        r'^(-?\d+)([+-])(?:(\d+)[×x*]?)?√(\d+)$',
        r'^(?:(\d+)[×x*]?)?√(\d+)([+-])(-?\d+)$',
    )
    m = re.fullmatch(patterns[0], s)
    if m:
        const = int(m.group(1))
        sign = m.group(2)
        coef = int(m.group(3) or '1')
        rad = int(m.group(4))
        return const, coef, rad, sign

    m = re.fullmatch(patterns[1], s)
    if m:
        coef = int(m.group(1) or '1')
        rad = int(m.group(2))
        sign = m.group(3)
        const = int(m.group(4))
        return const, coef, rad, sign

    return None


def _parse_algebraic_fraction_surd_raw(raw) -> tuple[int, int, int] | None:
    """Parse coef|radicand|denom for k√r / n answers."""
    s = str(raw or '').strip()
    parts = s.split('|')
    if len(parts) != 3 or parts[0] in ('b', 'd'):
        return None
    coef = _parse_number(parts[0])
    rad = _parse_number(parts[1])
    denom = _parse_number(parts[2])
    if coef is None or rad is None or denom is None:
        return None
    if coef != coef.to_integral_value() or rad != rad.to_integral_value():
        return None
    if denom != denom.to_integral_value() or int(denom) <= 0:
        return None
    if int(rad) <= 0:
        return None
    return int(coef), int(rad), int(denom)


def _parse_algebraic_fraction_binomial_raw(
    raw,
) -> tuple[int, int, int, int, int, str] | None:
    s = str(raw or '').strip()
    parts = s.split('|')
    if len(parts) != 7 or parts[0] != 'b':
        return None
    scale = _parse_number(parts[1])
    const = _parse_number(parts[2])
    surd_coef = _parse_number(parts[3])
    rad = _parse_number(parts[4])
    denom = _parse_number(parts[5])
    bracket_sign = parts[6].strip()
    if None in (scale, const, surd_coef, rad, denom):
        return None
    for val in (scale, const, surd_coef, rad, denom):
        if val != val.to_integral_value():
            return None
    if int(rad) <= 0 or int(denom) <= 0 or int(surd_coef) <= 0:
        return None
    if bracket_sign not in ('+', '-'):
        return None
    return (
        int(scale), int(const), int(surd_coef), int(rad), int(denom), bracket_sign
    )


def _parse_algebraic_fraction_two_surds_raw(
    raw,
) -> tuple[tuple[tuple[int, int], tuple[int, int]], int] | None:
    s = str(raw or '').strip()
    parts = s.split('|')
    if len(parts) != 4 or parts[0] != 'd':
        return None
    rad1 = _parse_number(parts[1])
    rad2 = _parse_number(parts[2])
    denom = _parse_number(parts[3])
    if rad1 is None or rad2 is None or denom is None:
        return None
    if rad1 != rad1.to_integral_value() or rad2 != rad2.to_integral_value():
        return None
    if denom != denom.to_integral_value() or int(denom) <= 0:
        return None
    if int(rad1) <= 0 or int(rad2) <= 0:
        return None
    terms = _normalize_two_surd_sum_terms(int(rad1), int(rad2))
    return terms, int(denom)


def _simplify_algebraic_fraction_surd(
    coef: int, radicand: int, denom: int
) -> tuple[int, int, int]:
    if coef == 0:
        return 0, radicand, denom
    g = math.gcd(abs(coef), denom)
    return coef // g, radicand, denom // g


def _binomial_to_expanded(
    scale: int, const: int, surd_coef: int, rad: int, bracket_sign: str
) -> tuple[int, int, int]:
    abs_scale = abs(scale)
    sign = 1 if scale >= 0 else -1
    int_part = sign * abs_scale * const
    if bracket_sign == '-':
        surd_part = -sign * abs_scale * surd_coef
    else:
        surd_part = sign * abs_scale * surd_coef
    return int_part, surd_part, rad


def _simplify_binomial_expanded(
    int_part: int, surd_coef: int, rad: int, denom: int
) -> tuple[int, int, int, int]:
    g = math.gcd(math.gcd(abs(int_part), abs(surd_coef)), denom)
    return int_part // g, surd_coef // g, rad, denom // g


def _format_algebraic_fraction_surd(coef: int, radicand: int, denom: int) -> str:
    num = _format_surd(Decimal(coef), Decimal(radicand))
    if denom == 1:
        return num
    return f'{num}/{denom}'


def _format_binomial_expanded(int_part: int, surd_coef: int, rad: int, denom: int) -> str:
    op = '+' if surd_coef >= 0 else '-'
    abs_sc = abs(surd_coef)
    surd = f'√{rad}' if abs_sc == 1 else f'{abs_sc}√{rad}'
    num = f'{int_part}{op}{surd}'
    if denom == 1:
        return num
    return f'{num}/{denom}'


def _format_two_surds(rads: tuple[int, int], denom: int) -> str:
    num = f'√{rads[0]}+√{rads[1]}'
    if denom == 1:
        return num
    return f'{num}/{denom}'


def _canonical_surd_term(coef: int, radicand: int) -> tuple[int, int]:
    c, r = _simplify_surd_pair(Decimal(coef), Decimal(radicand))
    return int(c), int(r)


def _normalize_two_surd_sum_terms(
    rad1: int, rad2: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    terms = sorted(
        [_canonical_surd_term(1, rad1), _canonical_surd_term(1, rad2)],
        key=lambda t: (t[1], t[0]),
    )
    return terms[0], terms[1]


def _format_two_surd_sum_terms(
    terms: tuple[tuple[int, int], tuple[int, int]], denom: int,
) -> str:
    parts = []
    for coef, rad in terms:
        if coef == 1:
            parts.append(f'√{rad}')
        else:
            parts.append(f'{coef}√{rad}')
    num = '+'.join(parts)
    if denom == 1:
        return num
    return f'{num}/{denom}'


def _parse_two_surd_sum_numerator(
    value: str,
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    s = _normalize_algebraic_string(value)
    if not s:
        return None
    if s.startswith('(') and s.endswith(')'):
        s = s[1:-1]
    if '-' in s:
        return None
    parts = [p for p in s.split('+') if p]
    if len(parts) != 2:
        return None
    terms = []
    for part in parts:
        parsed = _parse_surd_expression(part)
        if parsed is None:
            return None
        terms.append(_canonical_surd_term(int(parsed[0]), int(parsed[1])))
    ordered = sorted(terms, key=lambda t: (t[1], t[0]))
    return ordered[0], ordered[1]


def _split_algebraic_fraction_user(value) -> tuple[str, int] | None:
    raw = str(value or '').strip()
    if not raw:
        return None
    if '|' in raw:
        num_text, den_s = raw.rsplit('|', 1)
        num_text = num_text.strip()
        if not num_text:
            return None
        den_s = den_s.strip()
        if not den_s:
            return num_text, 1
        denom = _parse_number(den_s)
        if denom is None or denom != denom.to_integral_value() or int(denom) <= 0:
            return None
        return num_text, int(denom)
    s = _normalize_algebraic_string(raw)
    if '/' not in s:
        return raw.strip(), 1
    # After normalisation, slash forms may look like (3√5)/(7).
    m = re.fullmatch(r'\((.+)\)/\((\d+)\)', s)
    if not m:
        m = re.fullmatch(r'(.+)/(\d+)', s)
    if not m:
        return None
    denom = _parse_number(m.group(2))
    if denom is None or int(denom) <= 0:
        return None
    return m.group(1), int(denom)


def _parse_algebraic_fraction_surd_user(value) -> tuple[int, int, int] | None:
    split = _split_algebraic_fraction_user(value)
    if split is None:
        return None
    num_text, denom = split
    surd = _parse_surd_expression(num_text)
    if surd is None:
        return None
    coef, rad = int(surd[0]), int(surd[1])
    return _simplify_algebraic_fraction_surd(coef, rad, denom)


def _parse_algebraic_fraction_binomial_user(
    value,
) -> tuple[int, int, int, int] | None:
    split = _split_algebraic_fraction_user(value)
    if split is None:
        return None
    num_text, denom = split
    s = _normalize_algebraic_string(num_text)
    if not s:
        return None

    m = re.fullmatch(
        r'^(-?)(\d+)\((\d+)([+-])((?:\d+[×x*]?)?)?√(\d+)\)$',
        s,
    )
    if m:
        scale = int(m.group(2))
        if m.group(1) == '-':
            scale = -scale
        const = int(m.group(3))
        bracket_sign = m.group(4)
        coef_raw = m.group(5) or '1'
        if coef_raw[-1] in '×x*':
            surd_coef = int(coef_raw[:-1])
        else:
            surd_coef = int(coef_raw)
        rad = int(m.group(6))
        int_part, sc, r = _binomial_to_expanded(
            scale, const, surd_coef, rad, bracket_sign
        )
        return _simplify_binomial_expanded(int_part, sc, r, denom)

    m = re.fullmatch(r'^-\((\d+)([+-])((?:\d+[×x*]?)?)?√(\d+)\)$', s)
    if m:
        const = int(m.group(1))
        bracket_sign = m.group(2)
        coef_raw = m.group(3) or '1'
        if coef_raw[-1] in '×x*':
            surd_coef = int(coef_raw[:-1])
        else:
            surd_coef = int(coef_raw)
        rad = int(m.group(4))
        int_part, sc, r = _binomial_to_expanded(
            -1, const, surd_coef, rad, bracket_sign
        )
        return _simplify_binomial_expanded(int_part, sc, r, denom)

    m = re.fullmatch(r'^\((\d+)([+-])((?:\d+[×x*]?)?)?√(\d+)\)$', s)
    if m:
        const = int(m.group(1))
        bracket_sign = m.group(2)
        coef_raw = m.group(3) or '1'
        if coef_raw[-1] in '×x*':
            surd_coef = int(coef_raw[:-1])
        else:
            surd_coef = int(coef_raw)
        rad = int(m.group(4))
        int_part, sc, r = _binomial_to_expanded(
            1, const, surd_coef, rad, bracket_sign
        )
        return _simplify_binomial_expanded(int_part, sc, r, denom)

    m = re.fullmatch(r'^\((-?\d+)([+-])((?:\d+[×x*]?)?)?√(\d+)\)$', s)
    if m:
        int_part = int(m.group(1))
        sign = m.group(2)
        coef_raw = m.group(3) or '1'
        if coef_raw[-1] in '×x*':
            surd_coef = int(coef_raw[:-1])
        else:
            surd_coef = int(coef_raw)
        rad = int(m.group(4))
        sc = surd_coef if sign == '+' else -surd_coef
        return _simplify_binomial_expanded(int_part, sc, rad, denom)

    m = re.fullmatch(r'^(-?\d+)([+-])((?:\d+[×x*]?)?)?√(\d+)$', s)
    if m:
        int_part = int(m.group(1))
        sign = m.group(2)
        coef_raw = m.group(3) or '1'
        if coef_raw[-1] in '×x*':
            surd_coef = int(coef_raw[:-1])
        else:
            surd_coef = int(coef_raw)
        rad = int(m.group(4))
        sc = surd_coef if sign == '+' else -surd_coef
        return _simplify_binomial_expanded(int_part, sc, rad, denom)

    return None


def _parse_algebraic_fraction_two_surds_user(
    value,
) -> tuple[tuple[tuple[int, int], tuple[int, int]], int] | None:
    split = _split_algebraic_fraction_user(value)
    if split is None:
        return None
    num_text, denom = split
    terms = _parse_two_surd_sum_numerator(num_text)
    if terms is None:
        return None
    return terms, denom


def _parse_algebraic_fraction_expanded_binomial_raw(
    raw,
) -> tuple[int, int, int, int] | None:
    s = str(raw or '').strip()
    parts = s.split('|')
    if len(parts) != 5 or parts[0] != 'e':
        return None
    int_part = _parse_number(parts[1])
    surd_coef = _parse_number(parts[2])
    rad = _parse_number(parts[3])
    denom = _parse_number(parts[4])
    if None in (int_part, surd_coef, rad, denom):
        return None
    for val in (int_part, surd_coef, rad, denom):
        if val != val.to_integral_value():
            return None
    if int(rad) <= 0 or int(denom) <= 0:
        return None
    return _simplify_binomial_expanded(
        int(int_part), int(surd_coef), int(rad), int(denom)
    )


def _binomial_expanded_answers_equal(
    expected: tuple[int, int, int, int],
    actual: tuple[int, int, int, int],
) -> bool:
    if expected[1] == 0:
        return (
            actual[1] == 0
            and expected[0] == actual[0]
            and expected[3] == actual[3]
        )
    return expected == actual


def _check_algebraic_fraction_expanded_binomial(correct_raw, user_answer) -> dict:
    expected = _parse_algebraic_fraction_expanded_binomial_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = _format_binomial_expanded(*expected)

    raw_user = str(user_answer or '').strip()
    if not raw_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the numerator and denominator.',
        }

    actual = _parse_algebraic_fraction_binomial_user(raw_user)
    if actual is None and expected[1] == 0:
        split = _split_algebraic_fraction_user(raw_user)
        if split is not None:
            val = _parse_number(split[0])
            if val is not None and val == val.to_integral_value():
                actual = _simplify_binomial_expanded(
                    int(val), 0, expected[2], split[1]
                )

    if actual is None:
        return {
            'correct': False,
            'normalized_user': raw_user,
            'normalized_correct': normalized_correct,
            'feedback': (
                'Write the numerator like 6 − 3√3 (or 3(2 − √3)); '
                'denominator optional if it is 1.'
            ),
        }

    correct = _binomial_expanded_answers_equal(expected, actual)
    return {
        'correct': correct,
        'normalized_user': _format_binomial_expanded(*actual),
        'normalized_correct': normalized_correct,
        'feedback': (
            'Correct!'
            if correct
            else 'Not quite — check your simplified numerator and denominator.'
        ),
    }


def _check_algebraic_fraction_surd(correct_raw, user_answer) -> dict:
    expected = _parse_algebraic_fraction_surd_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_coef, exp_rad, exp_denom = _simplify_algebraic_fraction_surd(*expected)
    normalized_correct = _format_algebraic_fraction_surd(
        exp_coef, exp_rad, exp_denom
    )

    raw_user = str(user_answer or '').strip()
    if not raw_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the numerator and denominator.',
        }

    actual = _parse_algebraic_fraction_surd_user(raw_user)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': raw_user,
            'normalized_correct': normalized_correct,
            'feedback': (
                'Write the numerator as a surd (e.g. 3√5) and the denominator '
                'as a whole number.'
            ),
        }

    act_coef, act_rad, act_denom = actual
    correct = (
        act_coef == exp_coef
        and act_rad == exp_rad
        and act_denom == exp_denom
    )
    return {
        'correct': correct,
        'normalized_user': _format_algebraic_fraction_surd(
            act_coef, act_rad, act_denom
        ),
        'normalized_correct': normalized_correct,
        'feedback': (
            'Correct!'
            if correct
            else 'Not quite — check your surd numerator and simplified denominator.'
        ),
    }


def _check_algebraic_fraction_binomial(correct_raw, user_answer) -> dict:
    expected = _parse_algebraic_fraction_binomial_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    scale, const, surd_coef, rad, denom, bracket_sign = expected
    exp = _simplify_binomial_expanded(
        *_binomial_to_expanded(scale, const, surd_coef, rad, bracket_sign),
        denom,
    )
    normalized_correct = _format_binomial_expanded(*exp)

    raw_user = str(user_answer or '').strip()
    if not raw_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the numerator and denominator.',
        }

    actual = _parse_algebraic_fraction_binomial_user(raw_user)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': raw_user,
            'normalized_correct': normalized_correct,
            'feedback': (
                'Write the numerator like 6 − 3√3 or 2(4 − √6); '
                'denominator optional if it is 1.'
            ),
        }

    correct = actual == exp
    return {
        'correct': correct,
        'normalized_user': _format_binomial_expanded(*actual),
        'normalized_correct': normalized_correct,
        'feedback': (
            'Correct!'
            if correct
            else 'Not quite — check your simplified numerator and denominator.'
        ),
    }


def _check_algebraic_fraction_two_surds(correct_raw, user_answer) -> dict:
    expected = _parse_algebraic_fraction_two_surds_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_terms, exp_denom = expected
    normalized_correct = _format_two_surd_sum_terms(exp_terms, exp_denom)

    raw_user = str(user_answer or '').strip()
    if not raw_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the numerator and denominator.',
        }

    actual = _parse_algebraic_fraction_two_surds_user(raw_user)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': raw_user,
            'normalized_correct': normalized_correct,
            'feedback': (
                'Write the numerator as a sum of two surds (e.g. √18 + √10); '
                'denominator optional if it is 1.'
            ),
        }

    act_terms, act_denom = actual
    correct = act_terms == exp_terms and act_denom == exp_denom
    return {
        'correct': correct,
        'normalized_user': _format_two_surd_sum_terms(act_terms, act_denom),
        'normalized_correct': normalized_correct,
        'feedback': (
            'Correct!'
            if correct
            else 'Not quite — check your surd sum and denominator.'
        ),
    }


@register_checker('algebraic_fraction')
def check_algebraic_fraction(correct_raw, user_answer):
    s = str(correct_raw or '').strip()
    if s.startswith('b|'):
        return _check_algebraic_fraction_binomial(correct_raw, user_answer)
    if s.startswith('e|'):
        return _check_algebraic_fraction_expanded_binomial(correct_raw, user_answer)
    if s.startswith('d|'):
        return _check_algebraic_fraction_two_surds(correct_raw, user_answer)
    # General algebraic/numeric fraction: numerator|denominator (stacked UI).
    if len(s.split('|')) == 2:
        return _check_general_algebraic_fraction(correct_raw, user_answer)
    return _check_algebraic_fraction_surd(correct_raw, user_answer)


def _check_general_algebraic_fraction(correct_raw, user_answer):
    """Check algebraic or numeric fractions entered as numerator|denominator."""
    parts = [part.strip() for part in str(correct_raw or '').split('|', 1)]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError('invalid_correct_answer')

    exp_num, exp_den = parts[0], parts[1]
    normalized_correct = f'{_format_algebraic_text(exp_num)}/{_format_algebraic_text(exp_den)}'

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the numerator and denominator.',
        }

    if '|' in user_s:
        user_parts = [part.strip() for part in user_s.split('|', 1)]
        act_num = user_parts[0]
        act_den = user_parts[1] if len(user_parts) > 1 else ''
        if not act_den:
            act_den = '1'
    else:
        split = _split_algebraic_fraction_user(user_s)
        if split is None:
            return {
                'correct': False,
                'normalized_user': user_s,
                'normalized_correct': normalized_correct,
                'feedback': 'Enter both the numerator and denominator.',
            }
        act_num, act_den_int = split
        act_den = str(act_den_int)

    if not act_num:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter both the numerator and denominator.',
        }

    normalized_user = (
        f'{_format_algebraic_text(act_num)}/{_format_algebraic_text(act_den)}'
    )
    correct = _algebraic_sympy_equivalent(
        f'({exp_num})/({exp_den})',
        f'({act_num})/({act_den})',
    )
    if not correct:
        # Accept matching parts even when overall sympy parse fails on awkward forms.
        correct = (
            _algebraic_answers_equivalent(exp_num, act_num)
            and _algebraic_answers_equivalent(exp_den, act_den)
        )
    return {
        'correct': correct,
        'normalized_user': normalized_user,
        'normalized_correct': normalized_correct,
        'feedback': (
            'Correct!'
            if correct
            else 'Not quite — check the numerator and denominator.'
        ),
    }


@register_checker('algebraic')
def check_algebraic(correct_raw, user_answer):
    binomial = _parse_algebraic_surd_binomial_raw(correct_raw)
    if binomial is not None:
        exp_const, exp_coef, exp_rad, exp_sign = binomial
        normalized_correct = _format_algebraic_surd_binomial(
            exp_const, exp_coef, exp_rad, exp_sign
        )

        raw_user = str(user_answer or '').strip()
        if not raw_user:
            return {
                'correct': False,
                'normalized_user': '',
                'normalized_correct': normalized_correct,
                'feedback': 'Enter your answer in the form p + q√r.',
            }

        actual = _parse_algebraic_surd_binomial(raw_user)
        if actual is None:
            return {
                'correct': False,
                'normalized_user': raw_user,
                'normalized_correct': normalized_correct,
                'feedback': 'Use the form p + q√r, e.g. 7 + 12√5 (click √ if needed).',
            }

        act_const, act_coef, act_rad, act_sign = actual
        correct = (
            act_const == exp_const
            and act_coef == exp_coef
            and act_rad == exp_rad
            and act_sign == exp_sign
        )
        return {
            'correct': correct,
            'normalized_user': _format_algebraic_surd_binomial(
                act_const, act_coef, act_rad, act_sign
            ),
            'normalized_correct': normalized_correct,
            'feedback': 'Correct!' if correct else 'Not quite — check your integer and surd terms.',
        }

    normalized_correct = _format_algebraic_text(correct_raw)
    if not normalized_correct:
        raise ValueError('invalid_correct_answer')

    raw_user = str(user_answer or '').strip()
    if not raw_user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter your simplified expression.',
        }

    normalized_user = _format_algebraic_text(raw_user)
    correct = _algebraic_answers_equivalent(correct_raw, raw_user)
    return {
        'correct': correct,
        'normalized_user': normalized_user,
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your simplified expression.',
    }


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


@register_checker('coordinate_pairs')
def check_coordinate_pairs(correct_raw, user_answer):
    def _parse_correct(raw):
        parts = [p.strip() for p in str(raw or '').split('|')]
        if len(parts) != 4:
            return None
        nums = [_parse_number(p) for p in parts]
        if any(n is None for n in nums):
            return None
        return [(nums[0], nums[1]), (nums[2], nums[3])]

    def _parse_pair_field(text):
        s = str(text or '').strip()
        if not s:
            return None
        if s.startswith('(') and s.endswith(')'):
            s = s[1:-1].strip()
        if ',' in s:
            parts = [p.strip() for p in s.split(',', 1)]
        elif '|' in s:
            parts = [p.strip() for p in s.split('|', 1)]
        else:
            return None
        if len(parts) != 2:
            return None
        x = _parse_number(parts[0])
        y = _parse_number(parts[1])
        if x is None or y is None:
            return None
        return (x, y)

    def _parse_user(raw):
        s = str(raw or '').strip()
        if not s:
            return None
        parts = [p.strip() for p in s.split('|')]
        if len(parts) == 4 and all(_parse_number(p) is not None for p in parts):
            nums = [_parse_number(p) for p in parts]
            return [(nums[0], nums[1]), (nums[2], nums[3])]
        if len(parts) == 2:
            pairs = [_parse_pair_field(p) for p in parts]
            if all(p is not None for p in pairs):
                return pairs
        single = _parse_pair_field(s)
        if single is not None:
            return [single]
        return None

    def _format_pairs(pairs):
        return '|'.join(
            f'({_format_number(x)}, {_format_number(y)})' for x, y in pairs
        )

    expected = _parse_correct(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = _format_pairs(expected)
    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter both coordinate pairs.',
        }

    actual = _parse_user(user_s)
    if actual is None or len(actual) != len(expected):
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter each solution as coordinates, e.g. (-2, 4).',
        }

    exp_sorted = sorted(expected, key=lambda p: (p[0], p[1]))
    act_sorted = sorted(actual, key=lambda p: (p[0], p[1]))
    correct = all(
        exp_x == act_x and exp_y == act_y
        for (exp_x, exp_y), (act_x, act_y) in zip(exp_sorted, act_sorted)
    )
    return {
        'correct': correct,
        'normalized_user': _format_pairs(act_sorted),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check both (x, y) pairs.',
    }


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


def _parse_two_var_equation_correct(raw) -> tuple[str, str, int, int, int] | None:
    s = str(raw or '').strip()
    if not s.startswith('eq:'):
        return None
    parts = s[3:].split(':')
    if len(parts) != 4 or ',' not in parts[0]:
        return None
    var1, var2 = [v.strip().lower() for v in parts[0].split(',', 1)]
    if not var1 or not var2 or var1 == var2:
        return None
    coef1 = _parse_number(parts[1])
    coef2 = _parse_number(parts[2])
    total = _parse_number(parts[3])
    if coef1 is None or coef2 is None or total is None:
        return None
    if (
        coef1 != coef1.to_integral_value()
        or coef2 != coef2.to_integral_value()
        or total != total.to_integral_value()
    ):
        return None
    return var1, var2, int(coef1), int(coef2), int(total)


def _normalize_two_var_equation_text(value) -> str:
    s = str(value or '').strip().lower()
    s = s.replace('\u2212', '-').replace('−', '-')
    s = s.replace('\u00d7', '*').replace('×', '*')
    s = re.sub(r'\s+', '', s)
    s = s.replace('*', '')
    return s


def _side_coefs_two_var(side: str, var1: str, var2: str) -> tuple[int, int, int] | None:
    if not side:
        return 0, 0, 0
    side = side.replace('-', '+-')
    if side.startswith('+'):
        side = side[1:]
    coef1 = coef2 = const = 0
    for term in (part for part in side.split('+') if part):
        if term in (var1, f'+{var1}'):
            coef1 += 1
            continue
        if term == f'-{var1}':
            coef1 -= 1
            continue
        if term in (var2, f'+{var2}'):
            coef2 += 1
            continue
        if term == f'-{var2}':
            coef2 -= 1
            continue
        if term.endswith(var1) and len(term) > len(var1):
            num = term[:-len(var1)]
            if num in ('', '+'):
                coef1 += 1
            elif num == '-':
                coef1 -= 1
            else:
                val = _parse_number(num)
                if val is None or val != val.to_integral_value():
                    return None
                coef1 += int(val)
            continue
        if term.endswith(var2) and len(term) > len(var2):
            num = term[:-len(var2)]
            if num in ('', '+'):
                coef2 += 1
            elif num == '-':
                coef2 -= 1
            else:
                val = _parse_number(num)
                if val is None or val != val.to_integral_value():
                    return None
                coef2 += int(val)
            continue
        val = _parse_number(term)
        if val is None or val != val.to_integral_value():
            return None
        const += int(val)
    return coef1, coef2, const


def _parse_two_var_equation_user(value, var1: str, var2: str) -> tuple[int, int, int] | None:
    s = _normalize_two_var_equation_text(value)
    if not s or s.count('=') != 1:
        return None
    left, right = s.split('=', 1)
    left_vals = _side_coefs_two_var(left, var1, var2)
    right_vals = _side_coefs_two_var(right, var1, var2)
    if left_vals is None or right_vals is None:
        return None
    lc1, lc2, lconst = left_vals
    rc1, rc2, rconst = right_vals
    return lc1 - rc1, lc2 - rc2, rconst - lconst


def _canonical_two_var_form(coef1: int, coef2: int, total: int) -> tuple[int, int, int] | None:
    if coef1 == 0 and coef2 == 0:
        return None
    if total < 0:
        coef1, coef2, total = -coef1, -coef2, -total
    if coef1 < 0 or (coef1 == 0 and coef2 < 0):
        coef1, coef2, total = -coef1, -coef2, -total
    return coef1, coef2, total


def _format_two_var_equation(var1: str, var2: str, coef1: int, coef2: int, total: int) -> str:
    def term(coef: int, var: str) -> str:
        if coef == 0:
            return ''
        if coef == 1:
            return f'+{var}'
        if coef == -1:
            return f'-{var}'
        if coef > 0:
            return f'+{coef}{var}'
        return f'{coef}{var}'

    parts = [part for part in (term(coef1, var1), term(coef2, var2)) if part]
    if not parts:
        lhs = '0'
    else:
        lhs = parts[0]
        if lhs.startswith('+'):
            lhs = lhs[1:]
        for extra in parts[1:]:
            lhs += extra
    return f'{lhs}={total}'


@register_checker('two_var_equation')
def check_two_var_equation(correct_raw, user_answer):
    expected = _parse_two_var_equation_correct(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    var1, var2, exp_a, exp_b, exp_c = expected
    normalized_correct = _format_two_var_equation(var1, var2, exp_a, exp_b, exp_c)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Write the equation using c and t.',
        }

    actual = _parse_two_var_equation_user(user_s, var1, var2)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': (
                f'Use the form ac + bt = total with a, b, c as numbers '
                f'(e.g. {exp_a}{var1} + {exp_b}{var2} = {exp_c}).'
            ),
        }

    act_a, act_b, act_c = actual
    exp_canonical = _canonical_two_var_form(exp_a, exp_b, exp_c)
    act_canonical = _canonical_two_var_form(act_a, act_b, act_c)
    if exp_canonical is None or act_canonical is None:
        correct = False
    else:
        correct = act_canonical == exp_canonical
    if act_canonical is not None:
        act_a, act_b, act_c = act_canonical
    return {
        'correct': correct,
        'normalized_user': _format_two_var_equation(var1, var2, act_a, act_b, act_c),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check the coefficients and total.',
    }


def _parse_linear_solution(value):
    """Parse a one-variable linear solution such as x=3, t = -2, or plain 3."""
    raw = str(value or '').strip()
    if not raw:
        return None, None

    compact = raw.lower().replace(' ', '')
    compact = compact.replace('\u2212', '-').replace('−', '-')

    eq_match = re.fullmatch(r'([a-z])=(-?.+)', compact)
    if eq_match:
        var = eq_match.group(1)
        val = _parse_fraction_or_number(eq_match.group(2))
        if val is None:
            return None, None
        return var, val

    val = _parse_fraction_or_number(raw)
    if val is not None:
        return None, val
    return None, None


def _format_linear_solution(var: str | None, value: Decimal) -> str:
    formatted = _format_number(value)
    if var:
        return f'{var} = {formatted}'
    return formatted


_INEQUALITY_SIGN_ALIASES = {
    '>': '>',
    '<': '<',
    '=': '=',
    '>=': '>=',
    '<=': '<=',
    '≥': '>=',
    '≤': '<=',
    'gt': '>',
    'lt': '<',
    'ge': '>=',
    'le': '<=',
    '\\gt': '>',
    '\\lt': '<',
    '\\geq': '>=',
    '\\ge': '>=',
    '\\leq': '<=',
    '\\le': '<=',
}


def _normalize_inequality_sign(sign) -> str | None:
    s = str(sign or '').strip().replace('\u2212', '-').replace('−', '-')
    if not s:
        return None
    return _INEQUALITY_SIGN_ALIASES.get(s.lower(), _INEQUALITY_SIGN_ALIASES.get(s))


def _format_inequality_sign(sign: str) -> str:
    display = {
        '>=': '≥',
        '<=': '≤',
        '>': '>',
        '<': '<',
        '=': '=',
    }
    return display.get(sign, sign)


def _format_linear_inequality(var: str, sign: str, value: Decimal) -> str:
    return f'{var} {_format_inequality_sign(sign)} {_format_number(value)}'


def _parse_linear_inequality_raw(raw) -> tuple[str, str, Decimal] | None:
    s = str(raw or '').strip()
    if not s:
        return None
    parts = [part.strip() for part in s.split('|')]
    if len(parts) == 3 and all(parts):
        var = parts[0].lower()
        sign = _normalize_inequality_sign(parts[1])
        val = _parse_fraction_or_number(parts[2])
        if var and sign is not None and val is not None:
            return var, sign, val

    # Natural forms: "m < 40", "m≤40", "x >= 3"
    s = s.replace('−', '-').replace('\u2212', '-')
    s = s.replace('≤', '<=').replace('≥', '>=').replace('≦', '<=').replace('≧', '>=')
    s = re.sub(r'\s+', '', s.lower())
    m = re.fullmatch(r'([a-z])(<=|>=|<|>|=)(-?\d+(?:\.\d+)?(?:/\d+)?)', s)
    if not m:
        return None
    sign = _normalize_inequality_sign(m.group(2))
    val = _parse_fraction_or_number(m.group(3))
    if sign is None or val is None:
        return None
    return m.group(1), sign, val


@register_checker('linear_inequality')
def check_linear_inequality(correct_raw, user_answer):
    expected = _parse_linear_inequality_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_var, exp_sign, exp_val = expected
    normalized_correct = _format_linear_inequality(exp_var, exp_sign, exp_val)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter an inequality, e.g. m < 40.',
        }

    actual = _parse_linear_inequality_raw(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter an inequality, e.g. m < 40.',
        }

    act_var, act_sign, act_val = actual
    correct = act_var == exp_var and act_sign == exp_sign and act_val == exp_val
    return {
        'correct': correct,
        'normalized_user': _format_linear_inequality(act_var, act_sign, act_val),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check the sign and value.',
    }


def _parse_compound_inequality_raw(raw) -> tuple[str, str, Decimal, str, Decimal] | None:
    s = str(raw or '').strip()
    if not s:
        return None
    parts = [part.strip() for part in s.split('|')]
    if len(parts) != 5 or not all(parts):
        return None
    var = parts[0].lower()
    left_sign = _normalize_inequality_sign(parts[1])
    left_val = _parse_fraction_or_number(parts[2])
    right_sign = _normalize_inequality_sign(parts[3])
    right_val = _parse_fraction_or_number(parts[4])
    if (
        not var
        or left_sign is None
        or left_val is None
        or right_sign is None
        or right_val is None
    ):
        return None
    return var, left_sign, left_val, right_sign, right_val


def _format_compound_inequality(
    var: str,
    left_sign: str,
    left_val: Decimal,
    right_sign: str,
    right_val: Decimal,
) -> str:
    return (
        f'{_format_number(left_val)} {_format_inequality_sign(left_sign)} '
        f'{var} {_format_inequality_sign(right_sign)} {_format_number(right_val)}'
    )


@register_checker('compound_inequality')
def check_compound_inequality(correct_raw, user_answer):
    expected = _parse_compound_inequality_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_var, exp_ls, exp_lv, exp_rs, exp_rv = expected
    normalized_correct = _format_compound_inequality(
        exp_var, exp_ls, exp_lv, exp_rs, exp_rv
    )

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Fill in both bounds and choose each sign.',
        }

    actual = _parse_compound_inequality_raw(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Fill in both bounds and choose each sign.',
        }

    act_var, act_ls, act_lv, act_rs, act_rv = actual
    correct = (
        act_var == exp_var
        and act_ls == exp_ls
        and act_lv == exp_lv
        and act_rs == exp_rs
        and act_rv == exp_rv
    )
    return {
        'correct': correct,
        'normalized_user': _format_compound_inequality(
            act_var, act_ls, act_lv, act_rs, act_rv
        ),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check both bounds and signs.',
    }


@register_checker('formula_fraction')
def check_formula_fraction(correct_raw, user_answer):
    """Check symbolic formula fractions such as x = (d-b)/(a-c)."""
    s = str(correct_raw or '').strip()
    parts = [part.strip() for part in s.split('|')]
    if len(parts) != 2 or not all(parts):
        raise ValueError('invalid_correct_answer')

    exp_num = _format_algebraic_text(parts[0])
    exp_den = _format_algebraic_text(parts[1])
    normalized_correct = f'{exp_num}/{exp_den}'

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the numerator and denominator.',
        }

    user_parts = [part.strip() for part in user_s.split('|')]
    if len(user_parts) != 2 or not user_parts[0] or not user_parts[1]:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter both the numerator and denominator.',
        }

    act_num = _format_algebraic_text(user_parts[0])
    act_den = _format_algebraic_text(user_parts[1])
    correct = act_num == exp_num and act_den == exp_den
    return {
        'correct': correct,
        'normalized_user': f'{act_num}/{act_den}',
        'normalized_correct': normalized_correct,
        'feedback': (
            'Correct!'
            if correct
            else 'Not quite — check the numerator and denominator.'
        ),
    }


@register_checker('number_line')
def check_number_line(correct_raw, user_answer):
    """Same raw format as compound_inequality; feedback tuned for the number-line UI."""
    result = check_compound_inequality(correct_raw, user_answer)
    user_s = str(user_answer or '').strip()
    if not user_s:
        result['feedback'] = 'Set both endpoints on the number line.'
    elif not result.get('correct'):
        if 'Fill in' in (result.get('feedback') or ''):
            result['feedback'] = (
                'Set both endpoints and choose open or closed circles.'
            )
        else:
            result['feedback'] = (
                'Not quite — check the endpoints and whether each circle '
                'is open or closed.'
            )
    return result


def _parse_linear_correct_raw(correct_raw) -> tuple[str, Decimal]:
    var, val = _parse_linear_solution(correct_raw)
    if val is None:
        raise ValueError('invalid_correct_answer')
    return (var or 'x'), val


@register_checker('linear')
def check_linear(correct_raw, user_answer):
    """Check a single-variable linear equation solution (e.g. x = 3)."""
    exp_var, exp_val = _parse_linear_correct_raw(correct_raw)
    normalized_correct = _format_linear_solution(exp_var, exp_val)

    user_var, user_val = _parse_linear_solution(user_answer)
    if user_val is None:
        return {
            'correct': False,
            'normalized_user': str(user_answer or '').strip(),
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the value (e.g. x = 3 or just 3).',
        }

    display_var = user_var or exp_var
    normalized_user = _format_linear_solution(display_var, user_val)
    correct = user_val == exp_val
    return {
        'correct': correct,
        'normalized_user': normalized_user,
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check your value.',
    }


def _split_quadratic_roots_raw(raw) -> list[str] | None:
    s = str(raw or '').strip()
    if not s:
        return None
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1].strip()
    s = re.sub(r'\s+or\s+', ',', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+and\s+', ',', s, flags=re.IGNORECASE)
    sep = '|' if '|' in s and ',' not in s else ','
    parts = [part.strip() for part in s.split(sep)]
    parts = [part for part in parts if part]
    if not parts:
        return None
    return parts


def _strip_root_prefix(part: str) -> str:
    return re.sub(r'^[a-z]\s*=\s*', '', part.strip(), flags=re.IGNORECASE)


def _normalize_quadratic_root_expr(value) -> str:
    s = str(value or '').strip()
    s = s.replace('\u221a', '√').replace('−', '-').replace('\u2212', '-')
    s = re.sub(r'(?i)sqrt\((\d+(?:\.\d+)?)\)', r'sqrt(\1)', s)
    s = re.sub(r'(\d+)√(\d+(?:\.\d+)?)', r'\1*sqrt(\2)', s)
    s = re.sub(r'√(\d+(?:\.\d+)?)', r'sqrt(\1)', s)
    return s


def _expand_quadratic_root_pm(parts: list[str]) -> list[str]:
    expanded: list[str] = []
    for part in parts:
        if '±' not in part and '\u00b1' not in part:
            expanded.append(part)
            continue
        plus = part.replace('±', '+').replace('\u00b1', '+')
        minus = part.replace('±', '-').replace('\u00b1', '-')
        expanded.extend([plus, minus])
    return expanded


def _root_to_sympy(value):
    s = _strip_root_prefix(str(value or '').strip())
    if not s:
        return None

    num = _parse_fraction_or_number(s)
    if num is not None:
        return nsimplify(num)

    normalized = _normalize_quadratic_root_expr(s).replace('^', '**')
    try:
        return nsimplify(sympify(normalized))
    except (TypeError, ValueError, AttributeError, SyntaxError):
        return None


def _sympy_roots_equal(left, right) -> bool:
    try:
        return bool(nsimplify(left - right) == 0)
    except (TypeError, ValueError, AttributeError):
        return False


def _sort_sympy_roots(roots):
    def sort_key(expr):
        try:
            if expr.is_real:
                return (0, float(expr.evalf()))
        except (TypeError, ValueError):
            pass
        return (1, str(expr))

    return sorted(roots, key=sort_key)


def _format_quadratic_root(expr) -> str:
    if hasattr(expr, 'is_Rational') and expr.is_Rational:
        if expr.q == 1:
            return str(int(expr.p))
        return f'{int(expr.p)}/{int(expr.q)}'
    if hasattr(expr, 'is_Integer') and expr.is_Integer:
        return str(int(expr))
    try:
        val = _parse_fraction_or_number(str(expr))
        if val is not None:
            return _format_number(val)
    except (TypeError, ValueError):
        pass
    return str(expr)


def _format_quadratic_root_set(roots) -> str:
    ordered = _sort_sympy_roots(roots)
    return ','.join(_format_quadratic_root(root) for root in ordered)


@register_checker('quadratic_roots')
def check_quadratic_roots(correct_raw, user_answer):
    """Compare quadratic roots as an order-independent set (via SymPy)."""
    expected_parts = _split_quadratic_roots_raw(correct_raw)
    if expected_parts is None:
        raise ValueError('invalid_correct_answer')

    expected = [_root_to_sympy(part) for part in expected_parts]
    if any(root is None for root in expected):
        raise ValueError('invalid_correct_answer')

    normalized_correct = _format_quadratic_root_set(expected)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the roots.',
        }

    actual_parts = _split_quadratic_roots_raw(user_s)
    if actual_parts is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter each root (e.g. 3 and -2).',
        }

    actual_parts = _expand_quadratic_root_pm(actual_parts)

    actual = [_root_to_sympy(part) for part in actual_parts]
    if any(root is None for root in actual):
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter valid roots (e.g. 3 and -2).',
        }

    if len(actual) != len(expected):
        if len(expected) == 4:
            count_msg = 'Not quite — hint: this problem has four solutions!'
        else:
            count_msg = f'Enter {len(expected)} roots.'
        return {
            'correct': False,
            'normalized_user': _format_quadratic_root_set(actual),
            'normalized_correct': normalized_correct,
            'feedback': count_msg,
        }

    exp_sorted = _sort_sympy_roots(expected)
    act_sorted = _sort_sympy_roots(actual)
    correct = all(
        _sympy_roots_equal(exp, act)
        for exp, act in zip(exp_sorted, act_sorted)
    )
    if correct:
        wrong_feedback = 'Correct!'
    elif len(expected) == 4:
        wrong_feedback = 'Not quite — hint: this problem has four solutions!'
    elif len(expected) == 2:
        wrong_feedback = 'Not quite — check both roots.'
    else:
        wrong_feedback = 'Not quite — check your roots.'
    return {
        'correct': correct,
        'normalized_user': _format_quadratic_root_set(actual),
        'normalized_correct': normalized_correct,
        'feedback': wrong_feedback,
    }


_VECTOR_PMATRIX_RE = re.compile(
    r'\\begin\{pmatrix\}\s*([^\\]+?)\s*(?:\\\\|\\)\s*([^\\]+?)\s*\\end\{pmatrix\}',
    re.IGNORECASE | re.DOTALL,
)
_VECTOR_DP_SUFFIX_RE = re.compile(r'\|dp:(\d+)$')


def _split_vector_correct_raw(raw) -> tuple[str, int | None]:
    s = str(raw or '').strip()
    match = _VECTOR_DP_SUFFIX_RE.search(s)
    if not match:
        return s, None
    required_dp = int(match.group(1))
    return s[:match.start()], required_dp


def _extract_vector_component_texts(raw) -> tuple[str, str] | None:
    s = str(raw or '').strip()
    if not s:
        return None

    match = _VECTOR_PMATRIX_RE.search(s)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    bracket = re.search(r'[\[(]\s*([^,\];|]+)\s*[,;|]\s*([^)\]]+)\s*[\])]', s)
    if bracket:
        return bracket.group(1).strip(), bracket.group(2).strip()

    if '|' in s:
        left, right = s.split('|', 1)
        return left.strip(), right.strip()

    for sep in (',', ';'):
        if sep in s:
            parts = [part.strip() for part in s.split(sep)]
            if len(parts) == 2:
                return parts[0], parts[1]

    return None


def _infer_decimal_places_from_text(text: str) -> int | None:
    s = _normalize_numeric_string(text)
    if not s or '/' in s:
        return None
    if '.' not in s:
        return 0
    return len(s.split('.', 1)[1])


def _round_decimal(value: Decimal, dp: int) -> Decimal:
    if dp <= 0:
        return value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    quant = Decimal('1').scaleb(-dp)
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def _vector_component_matches(
    expected: Decimal,
    actual: Decimal,
    user_text: str | None,
    *,
    required_dp: int | None,
) -> bool:
    if expected == actual:
        return True
    if required_dp is not None:
        return (
            _round_decimal(expected, required_dp)
            == _round_decimal(actual, required_dp)
        )
    if user_text is None:
        return False
    dp = _infer_decimal_places_from_text(user_text)
    if dp is None:
        return expected == actual
    if dp == 0:
        return expected == actual
    return _round_decimal(expected, dp) == actual


def _parse_vector_pair(raw) -> tuple[Decimal, Decimal] | None:
    """Parse column-vector components (top, bottom) from raw or user text."""
    s, _ = _split_vector_correct_raw(raw)
    if not s:
        return None

    m = _VECTOR_PMATRIX_RE.search(s)
    if m:
        top = _parse_fraction_or_number(m.group(1).strip())
        bottom = _parse_fraction_or_number(m.group(2).strip())
        if top is not None and bottom is not None:
            return top, bottom

    bracket = re.search(r'[\[(]\s*([^,\];|]+)\s*[,;|]\s*([^)\]]+)\s*[\])]', s)
    if bracket:
        top = _parse_fraction_or_number(bracket.group(1).strip())
        bottom = _parse_fraction_or_number(bracket.group(2).strip())
        if top is not None and bottom is not None:
            return top, bottom

    if '|' in s:
        left, right = s.split('|', 1)
        top = _parse_fraction_or_number(left.strip())
        bottom = _parse_fraction_or_number(right.strip())
        if top is not None and bottom is not None:
            return top, bottom

    for sep in (',', ';'):
        if sep in s:
            parts = [part.strip() for part in s.split(sep)]
            if len(parts) == 2:
                top = _parse_fraction_or_number(parts[0])
                bottom = _parse_fraction_or_number(parts[1])
                if top is not None and bottom is not None:
                    return top, bottom

    return None


def _format_vector_pair(top: Decimal, bottom: Decimal) -> str:
    return f'({_format_number(top)}, {_format_number(bottom)})'


def _parse_two_vectors_raw(raw) -> tuple[tuple[Decimal, Decimal], tuple[Decimal, Decimal]] | None:
    s, _ = _split_vector_correct_raw(raw)
    if not s:
        return None
    parts = [part.strip() for part in s.split('|')]
    if len(parts) != 4 or any(not part for part in parts):
        return None
    nums = [_parse_fraction_or_number(part) for part in parts]
    if any(num is None for num in nums):
        return None
    return (nums[0], nums[1]), (nums[2], nums[3])


def _format_two_vectors(
    x: tuple[Decimal, Decimal],
    y: tuple[Decimal, Decimal],
    labels: tuple[str, str] = ('x', 'y'),
) -> str:
    return (
        f'{labels[0]}={_format_vector_pair(*x)}, '
        f'{labels[1]}={_format_vector_pair(*y)}'
    )


@register_checker('vector_pair')
def check_vector_pair(correct_raw, user_answer):
    raw_correct, required_dp = _split_vector_correct_raw(correct_raw)
    expected = _parse_two_vectors_raw(raw_correct)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_x, exp_y = expected
    normalized_correct = _format_two_vectors(exp_x, exp_y)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter both vectors x and y.',
        }

    actual = _parse_two_vectors_raw(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter both components of each vector.',
        }

    act_x, act_y = actual
    component_texts = _extract_vector_component_texts(user_s)
    if component_texts and '|' in user_s and user_s.count('|') >= 3:
        texts = [part.strip() for part in user_s.split('|')[:4]]
    else:
        texts = [None, None, None, None]

    checks = (
        (exp_x[0], act_x[0], texts[0]),
        (exp_x[1], act_x[1], texts[1]),
        (exp_y[0], act_y[0], texts[2]),
        (exp_y[1], act_y[1], texts[3]),
    )
    correct = all(
        _vector_component_matches(exp, act, text, required_dp=required_dp)
        for exp, act, text in checks
    )
    return {
        'correct': correct,
        'normalized_user': _format_two_vectors(act_x, act_y),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check both vectors.',
    }


@register_checker('vector')
def check_vector(correct_raw, user_answer):
    """Check a 2D column vector (top, bottom components)."""
    raw_correct, required_dp = _split_vector_correct_raw(correct_raw)
    expected = _parse_vector_pair(raw_correct)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    exp_top, exp_bottom = expected
    normalized_correct = _format_vector_pair(exp_top, exp_bottom)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter the vector (e.g. (3, 4)).',
        }

    actual = _parse_vector_pair(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter both components (e.g. (3, 4) or 3, 4).',
        }

    act_top, act_bottom = actual
    component_texts = _extract_vector_component_texts(user_s)
    top_text = component_texts[0] if component_texts else None
    bottom_text = component_texts[1] if component_texts else None
    correct = (
        _vector_component_matches(
            exp_top, act_top, top_text, required_dp=required_dp
        )
        and _vector_component_matches(
            exp_bottom, act_bottom, bottom_text, required_dp=required_dp
        )
    )
    return {
        'correct': correct,
        'normalized_user': _format_vector_pair(act_top, act_bottom),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check both components.',
    }


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
    'both': ('both', 'both triangles', '1 and 2', 'triangles 1 and 2', '1 & 2'),
    'neither': ('neither', 'none', 'no triangle', 'not right angled', 'not right-angled'),
    '1': ('1', 'triangle 1', 'one', 'first'),
    '2': ('2', 'triangle 2', 'two', 'second'),
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


@register_checker('mcq')
def check_mcq(correct_raw, user_answer):
    """Check a single-letter MCQ choice (A, B, C, …)."""
    correct = str(correct_raw or '').strip().upper()[:1]
    if not correct or correct not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        raise ValueError('invalid_correct_answer')
    user = str(user_answer or '').strip().upper()[:1]
    if not user:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': correct,
            'feedback': 'Choose an option.',
        }
    ok = user == correct
    return {
        'correct': ok,
        'normalized_user': user,
        'normalized_correct': correct,
        'feedback': 'Correct!' if ok else 'Not quite — try another option.',
    }


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


_COMPLETED_SQUARE_KINDS = frozenset({'plus', 'minus', 'scaled', 'expand'})
_COMPLETED_SQUARE_FIELD_COUNTS = {
    'plus': 2,
    'minus': 2,
    'scaled': 3,
    'expand': 2,
}


def _parse_completed_square_values(raw, *, kind=None, require_kind=False):
    """Parse completed-square field values; optional kind prefix on stored answer."""
    s = str(raw or '').strip()
    if not s:
        return None
    parts = [part.strip() for part in s.split('|')]
    if not parts or any(not part for part in parts):
        return None
    if parts[0].lower() in _COMPLETED_SQUARE_KINDS:
        parsed_kind = parts[0].lower()
        values = parts[1:]
    elif kind:
        parsed_kind = kind.lower()
        values = parts
    else:
        return None
    if parsed_kind not in _COMPLETED_SQUARE_KINDS:
        return None
    expected_count = _COMPLETED_SQUARE_FIELD_COUNTS[parsed_kind]
    if require_kind and parts[0].lower() not in _COMPLETED_SQUARE_KINDS:
        return None
    if len(values) != expected_count:
        return None
    numbers = [_parse_number(part) for part in values]
    if any(num is None for num in numbers):
        return None
    return parsed_kind, numbers


def _format_completed_square(kind, numbers) -> str:
    return kind + '|' + '|'.join(_format_number(num) for num in numbers)


def _format_vector_combo_coef(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f'{value.numerator}/{value.denominator}'


def _parse_vector_combo_raw(raw) -> list[Fraction] | None:
    s = str(raw or '').strip()
    if not s:
        return None
    parts = [part.strip() for part in s.split('|')]
    if not parts or any(not part for part in parts):
        return None
    coeffs = [_parse_fraction_value(part) for part in parts]
    if any(coef is None for coef in coeffs):
        return None
    return coeffs


def _format_vector_combo(coefficients: list[Fraction]) -> str:
    return '|'.join(_format_vector_combo_coef(coef) for coef in coefficients)


@register_checker('vector_combo')
def check_vector_combo(correct_raw, user_answer):
    expected = _parse_vector_combo_raw(correct_raw)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    normalized_correct = _format_vector_combo(expected)
    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a coefficient for each vector.',
        }

    actual = _parse_vector_combo_raw(user_s)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Enter each coefficient as a fraction or number (e.g. 1/5).',
        }

    if len(actual) != len(expected):
        return {
            'correct': False,
            'normalized_user': _format_vector_combo(actual),
            'normalized_correct': normalized_correct,
            'feedback': 'Enter a coefficient for each vector shown.',
        }

    correct = actual == expected
    return {
        'correct': correct,
        'normalized_user': _format_vector_combo(actual),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check each coefficient.',
    }


@register_checker('completed_square')
def check_completed_square(correct_raw, user_answer):
    expected = _parse_completed_square_values(correct_raw, require_kind=True)
    if expected is None:
        raise ValueError('invalid_correct_answer')

    kind, exp_numbers = expected
    normalized_correct = _format_completed_square(kind, exp_numbers)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': 'Fill in every blank.',
        }

    actual = _parse_completed_square_values(user_s, kind=kind)
    if actual is None:
        return {
            'correct': False,
            'normalized_user': user_s,
            'normalized_correct': normalized_correct,
            'feedback': 'Use + or − for each term, then enter a number in every blank.',
        }

    _, act_numbers = actual
    correct = act_numbers == exp_numbers
    return {
        'correct': correct,
        'normalized_user': _format_completed_square(kind, act_numbers),
        'normalized_correct': normalized_correct,
        'feedback': 'Correct!' if correct else 'Not quite — check each blank.',
    }


def _parse_proof_steps_raw(raw) -> tuple[bool, list[str]] | None:
    """Parse ``orderFlag|id1|id2|...`` (orderFlag is 0 or 1)."""
    s = str(raw or '').strip()
    if not s:
        return None
    parts = [p.strip() for p in s.split('|') if p.strip()]
    if len(parts) < 2:
        return None
    flag = parts[0]
    if flag not in ('0', '1'):
        # Legacy / bare id list: treat as ordered.
        return True, parts
    ids = parts[1:]
    if not ids:
        return None
    return flag == '1', ids


@register_checker('proof_steps')
def check_proof_steps(correct_raw, user_answer):
    """Plan C: selected step ids from a bank (order optional)."""
    parsed = _parse_proof_steps_raw(correct_raw)
    if parsed is None:
        raise ValueError('invalid_correct_answer')
    order_matters, expected_ids = parsed
    normalized_correct = '|'.join(expected_ids)

    user_s = str(user_answer or '').strip()
    if not user_s:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': (
                'Select the correct proof steps in order.'
                if order_matters
                else 'Select all correct statements.'
            ),
        }

    user_ids = [p.strip() for p in user_s.split('|') if p.strip()]
    if not user_ids:
        return {
            'correct': False,
            'normalized_user': '',
            'normalized_correct': normalized_correct,
            'feedback': (
                'Select the correct proof steps in order.'
                if order_matters
                else 'Select all correct statements.'
            ),
        }

    if order_matters:
        correct = user_ids == expected_ids
        feedback = (
            'Correct!'
            if correct
            else 'Not quite — check which steps belong and their order.'
        )
    else:
        correct = set(user_ids) == set(expected_ids)
        feedback = (
            'Correct!'
            if correct
            else 'Not quite — select every correct statement and leave out the rest.'
        )

    return {
        'correct': correct,
        'normalized_user': '|'.join(user_ids),
        'normalized_correct': normalized_correct,
        'feedback': feedback,
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
