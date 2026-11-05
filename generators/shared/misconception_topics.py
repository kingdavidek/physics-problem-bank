"""Topic misconception rules for GCSE maths (docs/GCSE_MATHS_HINTS.md, Phase 2), worked from recorded inputs.

Phase 1 rules (``misconceptions.GENERIC_RULES``) see only the key. These rules also see the numbers the question
printed (``problem['answer_record']``, see ``answer_record.py``), so they can compute the value a particular slip
gives: the diameter used as the radius, the hypotenuse left squared, a percentage taken of the wrong amount.

Two tables:

* ``TRUTH[family](i, pi)`` rebuilds the correct answer from the recorded inputs ``i``. It is a guard, not a
  grader: a rule fires only if the rebuilt answer reproduces the stored key (at the accuracy the question states).
  If a generator ever changes what a family means, or one family name serves two different questions, the guard
  fails and the rules stay silent. Silence is better than a misleading hint.
* ``RULES`` lists the slips. Each rule gives, for a family, the exact value (or values) a pupil who made the slip
  would reach. ``pi`` is the number pi for an answer in decimals, and 1 for an answer "in terms of pi" (the
  recorded coefficient), so one formula serves both.

The formulas are written from the maths, never by calling a generator helper, so a generator bug cannot hide
inside a rule. This module imports no generator, no random numbers and no database.

Everything is exact: ``Fraction``. Roots, pi and trigonometry are held to 40 or more correct digits (trigonometry
to ten decimal places, which cannot move a value across a rounding boundary that a classroom answer has).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Callable

PI = Fraction(Decimal('3.14159265358979323846264338327950288419716939937510582097494'))
ONE = Fraction(1)
MAX_TERMS = 12


# ---------------------------------------------------------------------------------------------
# Small exact-arithmetic helpers
# ---------------------------------------------------------------------------------------------

MAX_INPUT = 10 ** 12          # no classroom question prints a bigger number; a bigger input is not a real record
MAX_EXPONENT = 60             # years, powers and indices (keeps every power cheap, whatever the record says)


def F(x):
    """An input as an exact Fraction (a float is read as the decimal it prints: 2.39 is 239/100).

    Recorded inputs are question numbers, so anything huge, or a long or exponent-style string, is refused: a
    record that does not look like a question's numbers is simply not used (and never costs much time).
    """
    if isinstance(x, Fraction):
        return x
    if isinstance(x, bool):
        raise ValueError('bool')
    if isinstance(x, int):
        out = Fraction(x)
    elif isinstance(x, float):
        if not math.isfinite(x):
            raise ValueError('not finite')
        out = Fraction(repr(x))
    elif isinstance(x, str):
        text = x.strip().replace('−', '-')
        if len(text) > 32 or 'e' in text.lower():
            raise ValueError('not a plain number')
        out = Fraction(text)
    else:
        raise ValueError('not a number')
    if abs(out) > MAX_INPUT:
        raise ValueError('too big')
    return out


def _n(x):
    """A small whole number input (years, a power, an index), or ValueError."""
    if isinstance(x, bool) or not isinstance(x, int) or not 0 <= x <= MAX_EXPONENT:
        raise ValueError('not a small whole number')
    return x


def sqrtq(x):
    """Square root of a non-negative Fraction: exact when it is a perfect square, else 60 digits."""
    x = F(x)
    if x < 0:
        raise ValueError('negative root')
    a, b = math.isqrt(x.numerator), math.isqrt(x.denominator)
    if a * a == x.numerator and b * b == x.denominator:
        return Fraction(a, b)
    with localcontext() as ctx:
        ctx.prec = 70
        return Fraction((Decimal(x.numerator) / Decimal(x.denominator)).sqrt())


def _fl(x):
    """A float result as a Fraction with the float noise removed (ten decimal places)."""
    return Fraction(Decimal(format(float(x), '.10f')))


def _angle(deg, radians):
    d = float(deg)
    return d if radians else math.radians(d)


def trig(fn, deg, radians=False):
    return _fl(getattr(math, fn)(_angle(deg, radians)))


def inverse(fn, ratio, radians=False):
    """Inverse sin, cos or tan of a ratio, in degrees (or radians), or None when it does not exist."""
    r = float(ratio)
    if fn in ('asin', 'acos') and abs(r) > 1:
        return None
    a = getattr(math, fn)(r)
    return _fl(a if radians else math.degrees(a))


def round_sf(x, sf=1):
    x = F(x)
    if x == 0:
        return x
    e = 0
    a = abs(x)
    while a >= 10:
        a /= 10
        e += 1
    while a < 1:
        a *= 10
        e -= 1
    unit = Fraction(10) ** (e - sf + 1)
    q = abs(x) / unit
    n = (q + Fraction(1, 2)).__floor__()
    return (n if x > 0 else -n) * unit


def round_unit(x, unit=1):
    x = F(x)
    q = abs(x) / unit
    n = (q + Fraction(1, 2)).__floor__()
    return (n if x >= 0 else -n) * unit


def _items(seq):
    if not isinstance(seq, (list, tuple)) or not 0 < len(seq) <= MAX_TERMS:
        raise ValueError('bad list')
    return seq


# ---------------------------------------------------------------------------------------------
# Arithmetic expressions (BIDMAS): a tiny parser of its own (no eval, no SymPy)
# ---------------------------------------------------------------------------------------------

_TOKEN_RE = re.compile(r'\s*(?:(\d+(?:\.\d+)?)|(.))')
_SUPERSCRIPTS = {'²': 2, '³': 3}


def _tokens(expr):
    if not isinstance(expr, str) or len(expr) > 80:
        raise ValueError('bad expression')
    out = []
    pos = 0
    text = expr.replace('−', '-')
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        if m.group(1) is not None:
            out.append(('n', Fraction(m.group(1))))
        else:
            ch = m.group(2)
            if ch in '+-×÷^()':
                out.append((ch, None))
            elif ch in _SUPERSCRIPTS:
                out.append(('^', None))
                out.append(('n', Fraction(_SUPERSCRIPTS[ch])))
            elif ch.strip():
                raise ValueError('bad character')
    if not out or len(out) > 60:
        raise ValueError('bad expression')
    return out


class _Parser:
    """expr := term (('+'|'-') term)* ; term := factor (('x'|'/') factor)* ; factor := '-'? power ;
    power := atom ('^' atom)? ; atom := number | '(' expr ')'.

    ``mode`` changes one thing: 'left' evaluates + - x / strictly left to right (the slip), 'standard' uses
    the usual order, ``power_as_product`` replaces x^p by x times p (the slip of multiplying by the power).
    """

    def __init__(self, tokens, mode='standard', power_as_product=False):
        self.t = tokens
        self.i = 0
        self.mode = mode
        self.pp = power_as_product

    def peek(self):
        return self.t[self.i][0] if self.i < len(self.t) else None

    def take(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def expr(self):
        if self.mode == 'left':
            return self.left_to_right()
        value = self.term()
        while self.peek() in ('+', '-'):
            op = self.take()[0]
            rhs = self.term()
            value = value + rhs if op == '+' else value - rhs
        return value

    def left_to_right(self):
        value = self.factor()
        while self.peek() in ('+', '-', '×', '÷'):
            op = self.take()[0]
            rhs = self.factor()
            if op == '+':
                value += rhs
            elif op == '-':
                value -= rhs
            elif op == '×':
                value *= rhs
            else:
                if rhs == 0:
                    raise ValueError('divide by zero')
                value /= rhs
        return value

    def term(self):
        value = self.factor()
        while self.peek() in ('×', '÷'):
            op = self.take()[0]
            rhs = self.factor()
            if op == '×':
                value *= rhs
            else:
                if rhs == 0:
                    raise ValueError('divide by zero')
                value /= rhs
        return value

    def factor(self):
        if self.peek() == '-':
            self.take()
            return -self.power()
        return self.power()

    def power(self):
        base = self.atom()
        if self.peek() == '^':
            self.take()
            exp = self.atom()
            if exp.denominator != 1 or abs(exp) > 12 or abs(base) > 10 ** 6:
                raise ValueError('power too big')
            return base * exp if self.pp else base ** int(exp)
        return base

    def atom(self):
        kind = self.peek()
        if kind == 'n':
            return self.take()[1]
        if kind == '(':
            self.take()
            value = self.expr()
            if self.peek() != ')':
                raise ValueError('missing bracket')
            self.take()
            return value
        raise ValueError('unexpected token')


def evaluate(expr, mode='standard', power_as_product=False):
    parser = _Parser(_tokens(expr), mode, power_as_product)
    value = parser.expr()
    if parser.i != len(parser.t):
        raise ValueError('trailing tokens')
    return value


def _drop_brackets(expr):
    """The expression with every bracket removed except those that carry a power (those cannot be dropped)."""
    text = expr.replace('−', '-')
    out, stack = [], []
    for ch_i, ch in enumerate(text):
        if ch == '(':
            stack.append(len(out))
            out.append(ch)
        elif ch == ')':
            start = stack.pop()
            after = text[ch_i + 1: ch_i + 2]
            if after in ('^', '²', '³'):
                out.append(ch)
            else:
                out[start] = ''
        else:
            out.append(ch)
    return ''.join(out)


_NEG_SQUARE_A = re.compile(r'^\(-(\d+(?:\.\d+)?)\)\^(\d+)$')
_NEG_SQUARE_B = re.compile(r'^-\((\d+(?:\.\d+)?)\)\^(\d+)$')


def _expr_left_to_right(i, pi):
    e = i['expr']
    return [evaluate(e, 'left')]


def _expr_brackets_ignored(i, pi):
    e = i['expr']
    stripped = _drop_brackets(e)
    return [] if stripped == e.replace('−', '-') else [evaluate(stripped)]


def _expr_power_multiplied(i, pi):
    e = i['expr']
    if '^' not in e and not any(s in e for s in _SUPERSCRIPTS):
        return []
    return [evaluate(e, 'standard', power_as_product=True)]


def _expr_negative_square(i, pi):
    e = i['expr'].replace('−', '-').replace(' ', '')
    m = _NEG_SQUARE_A.match(e)
    if m:
        return [-(Fraction(m.group(1)) ** int(m.group(2)))]
    m = _NEG_SQUARE_B.match(e)
    if m:
        return [(-Fraction(m.group(1))) ** int(m.group(2))]
    return []


# ---------------------------------------------------------------------------------------------
# Truth: the correct answer rebuilt from the recorded inputs (a guard for the rules)
# ---------------------------------------------------------------------------------------------

def _g(i, *names):
    return [F(i[n]) for n in names]


def _circle_area(r, pi):
    return pi * r * r


def _arc(i, pi):
    r, a = _g(i, 'r', 'angle')
    return a / 360 * 2 * pi * r


def _cone_slant(r, h):
    return sqrtq(r * r + h * h)


def _ratio_t(i):
    fn, op = RATIO_OF[(i['known_kind'], i['find_kind'])]
    return fn, op


# (known side, wanted side) -> (trig function, whether the known side is multiplied or divided by it)
RATIO_OF = {
    ('hyp', 'opp'): ('sin', 'mul'), ('hyp', 'adj'): ('cos', 'mul'),
    ('opp', 'hyp'): ('sin', 'div'), ('adj', 'hyp'): ('cos', 'div'),
    ('opp', 'adj'): ('tan', 'div'), ('adj', 'opp'): ('tan', 'mul'),
}


def _trig_side_value(i, fn, op, radians=False):
    known, angle = F(i['known']), F(i['angle'])
    ratio = trig(fn, angle, radians)
    if op == 'mul':
        return known * ratio
    return None if ratio == 0 else known / ratio


def _angle_inputs(i):
    """(inverse function, ratio) for a recorded trig_angle: opp and adj, adj and hyp, or opp and hyp."""
    if 'opp' in i and 'adj' in i:
        return 'atan', F(i['opp']) / F(i['adj'])
    if 'adj' in i and 'hyp' in i:
        return 'acos', F(i['adj']) / F(i['hyp'])
    if 'opp' in i and 'hyp' in i:
        return 'asin', F(i['opp']) / F(i['hyp'])
    raise ValueError('unknown angle inputs')


def _mean(values):
    return sum(values) / len(values)


def _legs_distance_speed(i):
    legs = [(F(d), F(s)) for d, s in _items(i['legs'])]
    return legs


def _legs_time_speed(i):
    return [(F(t), F(s)) for t, s in _items(i['legs'])]


TRUTH: dict[str, Callable] = {
    # mensuration (areas, volumes and the like: the radius is given in every practice question)
    'mens_circle_area': lambda i, pi: _circle_area(F(i['r']), pi),
    'mens_circumference': lambda i, pi: 2 * pi * F(i['r']),
    'mens_cyl_vol': lambda i, pi: pi * F(i['r']) ** 2 * F(i['h']),
    'mens_cyl_sa': lambda i, pi: 2 * pi * F(i['r']) * (F(i['r']) + F(i['h'])),
    'mens_cone_vol': lambda i, pi: pi * F(i['r']) ** 2 * F(i['h']) / 3,
    'mens_sphere_vol': lambda i, pi: Fraction(4, 3) * pi * F(i['r']) ** 3,
    'mens_sphere_sa': lambda i, pi: 4 * pi * F(i['r']) ** 2,
    'mens_pyramid_vol': lambda i, pi: F(i['l']) * F(i['w']) * F(i['h']) / 3,
    'mens_tri_area': lambda i, pi: F(i['b']) * F(i['h']) / 2,
    'mens_trapezium': lambda i, pi: (F(i['a']) + F(i['b'])) * F(i['h']) / 2,
    'mens_tri_prism_vol': lambda i, pi: F(i['b']) * F(i['h']) * F(i['length']) / 2,
    'mens_cuboid_vol': lambda i, pi: F(i['l']) * F(i['w']) * F(i['h']),
    'mens_cuboid_sa': lambda i, pi: 2 * (F(i['l']) * F(i['w']) + F(i['l']) * F(i['h']) + F(i['w']) * F(i['h'])),
    'mens_rect_perimeter': lambda i, pi: 2 * (F(i['l']) + F(i['w'])),
    'mens_l_shape': lambda i, pi: F(i['a']) * F(i['c']) - F(i['b']) * F(i['d']),
    'mens_annulus': lambda i, pi: pi * (F(i['R']) ** 2 - F(i['r']) ** 2),
    'mens_sector_area': lambda i, pi: F(i['angle']) / 360 * pi * F(i['r']) ** 2,
    'mens_arc': _arc,
    'mens_arc_exact': _arc,
    'mens_sector_perimeter': lambda i, pi: _arc(i, pi) + 2 * F(i['r']),
    'mens_cm2_to_m2': lambda i, pi: F(i['l']) * F(i['w']) / 10000,
    'mens_diameter': lambda i, pi: F(i['circ']) / pi,
    'mens_radius_from_area': lambda i, pi: sqrtq(F(i['area']) / pi),
    'mens_cyl_height': lambda i, pi: F(i['vol']) / (pi * F(i['r']) ** 2),
    'mens_cone_sa_slant': lambda i, pi: pi * F(i['r']) * (F(i['r']) + F(i['slant'])),
    'mens_cone_sa_height': lambda i, pi: pi * F(i['r']) * (F(i['r']) + _cone_slant(F(i['r']), F(i['h']))),
    'mens_cone_vol_from_slant': lambda i, pi: pi * F(i['r']) ** 2 * sqrtq(F(i['slant']) ** 2 - F(i['r']) ** 2) / 3,
    'mens_exact_pi_cyl': lambda i, pi: pi * F(i['r']) ** 2 * F(i['h']),
    'mens_fill_time': lambda i, pi: pi * F(i['r']) ** 2 * F(i['h']) / 1000 / F(i['rate']),
    'mens_similar': lambda i, pi: F(i['value']) * F(i['k']) ** _n(i['power']),
    # Pythagoras
    'pyth_hyp': lambda i, pi: sqrtq(F(i['a']) ** 2 + F(i['b']) ** 2),
    'pyth_leg': lambda i, pi: sqrtq(F(i['c']) ** 2 - F(i['a']) ** 2),
    'pyth_dist': lambda i, pi: sqrtq((F(i['x2']) - F(i['x1'])) ** 2 + (F(i['y2']) - F(i['y1'])) ** 2),
    'pyth_perimeter': lambda i, pi: F(i['a']) + F(i['b']) + sqrtq(F(i['a']) ** 2 + F(i['b']) ** 2),
    'pyth_isosceles_height': lambda i, pi: sqrtq(F(i['side']) ** 2 - (F(i['base']) / 2) ** 2),
    'pyth_space_diag': lambda i, pi: sqrtq(F(i['l']) ** 2 + F(i['w']) ** 2 + F(i['h']) ** 2),
    'pyth_ladder_slide': lambda i, pi: sqrtq(F(i['ladder']) ** 2 - (F(i['base']) + F(i['slide'])) ** 2),
    # trigonometry
    'trig_side': lambda i, pi: _trig_side_value(i, *_ratio_t(i)),
    'trig_angle': lambda i, pi: inverse(*_angle_inputs(i)),
    'trig_cosine_side': lambda i, pi: sqrtq(
        F(i['b']) ** 2 + F(i['c']) ** 2 - 2 * F(i['b']) * F(i['c']) * trig('cos', F(i['angle']))),
    'trig_area': lambda i, pi: F(i['a']) * F(i['b']) * trig('sin', F(i['angle'])) / 2,
    'trig_sine_side': lambda i, pi: F(i['known_side']) * trig('sin', F(i['target_angle'])) / trig('sin', F(i['known_angle'])),
    'trig_sine_angle': lambda i, pi: inverse('asin', F(i['a']) * trig('sin', F(i['angle_b'])) / F(i['b'])),
    'trig_cosine_angle': lambda i, pi: inverse(
        'acos', (F(i['b']) ** 2 + F(i['c']) ** 2 - F(i['a']) ** 2) / (2 * F(i['b']) * F(i['c']))),
    'trig_isosceles_apex': lambda i, pi: 2 * inverse('asin', F(i['base']) / 2 / F(i['equal'])),
    # percentages, fractions and number
    'num_pct_change': lambda i, pi: F(i['amount']) * (1 + _sgn(i) * F(i['pct']) / 100),
    'num_reverse_pct': lambda i, pi: F(i['final']) / (1 + _sgn(i) * F(i['pct']) / 100),
    'num_two_pct_changes': lambda i, pi: F(i['amount']) * (1 + F(i['pct1']) / 100) * (1 - F(i['pct2']) / 100),
    'num_vat_inclusive': lambda i, pi: F(i['price']) * (1 + F(i['vat']) / 100),
    'num_compound': lambda i, pi: F(i['principal']) * (1 + _sgn(i) * F(i['rate']) / 100) ** _n(i['years']),
    'num_reverse_compound': lambda i, pi: F(i['final']) / (1 + F(i['rate']) / 100) ** _n(i['years']),
    'num_pct_of': lambda i, pi: F(i['amount']) * F(i['pct']) / 100,
    'num_pct_error': lambda i, pi: abs(F(i['actual']) - F(i['estimate'])) / F(i['actual']) * 100,
    'num_directed': lambda i, pi: _directed(i, 1),
    'num_power': lambda i, pi: F(i['base']) ** _n(i['exp']),
    'num_neg_index': lambda i, pi: ONE / F(i['base']) ** _n(i['power']),
    'num_zero_neg_index': lambda i, pi: ONE / F(i['b']) ** 2,
    'num_frac_index': lambda i, pi: sqrtq(F(i['base'])) if (i['num'], i['den']) == (1, 2) else None,
    'num_frac_of': lambda i, pi: F(i['amount']) * F(i['num']) / F(i['den']),
    'num_estimate_product_1sf': lambda i, pi: round_sf(F(i['a']), 1) * round_sf(F(i['b']), 1),
    'num_estimate_fraction_1sf': lambda i, pi: round_sf(F(i['a']), 1) * round_sf(F(i['b']), 1) / round_sf(F(i['c']), 1),
    'num_estimate_product_whole': lambda i, pi: round_unit(F(i['a'])) * round_unit(F(i['b'])),
    'fdp_pct_change': lambda i, pi: abs(F(i['new']) - F(i['original'])) / F(i['original']) * 100,
    'fdp_profit_pct': lambda i, pi: (F(i['selling']) - F(i['cost'])) / F(i['cost']) * 100,
    'fdp_reverse_two_step': lambda i, pi: F(i['final']) / ((1 + F(i['pct_up']) / 100) * (1 - F(i['pct_down']) / 100)),
    'fdp_fraction_not': lambda i, pi: F(i['total']) - F(i['total']) * F(i['num']) / F(i['den']),
    'fdp_shop_discount': lambda i, pi: F(i['unit']) * F(i['qty']) * (1 - F(i['discount_pct']) / 100),
    'fdp_fraction_to_pct': lambda i, pi: F(i['a']) / F(i['b']) * 100,
    'fdp_decimal_to_fraction': lambda i, pi: F(i['dec']),
    'fdp_pct_to_fraction': lambda i, pi: F(i['pct']) / 100,
    'dec_mean': lambda i, pi: _mean([F(v) for v in _items(i['values'])]),
    'arith': lambda i, pi: evaluate(i['expr']),
    'product': lambda i, pi: F(i['a']) * F(i['b']),
    'quotient': lambda i, pi: F(i['a']) / F(i['b']),
    # ratio and proportion
    'ratio_map_scale': lambda i, pi: F(i['cm']) * F(i['scale']) / {'m': 100, 'km': 100000}[i['to']],
    'prop_direct': lambda i, pi: F(i['y1']) * F(i['x2']) / F(i['x1']),
    'prop_inverse': lambda i, pi: F(i['a']) * F(i['b']) / F(i['c']),
    'prop_scale': lambda i, pi: F(i['q1']) * F(i['n2']) / F(i['n1']),
    'ratio_unitary': lambda i, pi: F(i['total']) * F(i['n2']) / F(i['n1']),
    'ratio_find_missing': lambda i, pi: F(i['known']) * F(i['b']) / F(i['a']),
    'ratio_part_fraction': lambda i, pi: _part_fraction(i),
    # compound measures
    'cm_kmh_to_ms': lambda i, pi: F(i['kmh']) * 5 / 18,
    'cm_ms_to_kmh': lambda i, pi: F(i['ms']) * Fraction(18, 5),
    'cm_speed_hm': lambda i, pi: F(i['s']) * (F(i['h']) + F(i['m']) / 60),
    'cm_dist_mins': lambda i, pi: F(i['s']) * F(i['mins']) / 60,
    'cm_avg_speed': lambda i, pi: (sum(d for d, s in _legs_distance_speed(i))
                                   / sum(d / s for d, s in _legs_distance_speed(i))),
    'cm_avg_speed_equal': lambda i, pi: 2 * F(i['s1']) * F(i['s2']) / (F(i['s1']) + F(i['s2'])),
    'cm_avg_speed_time': lambda i, pi: (sum(t * s for t, s in _legs_time_speed(i))
                                        / sum(t for t, s in _legs_time_speed(i))),
    'cm_alloy_vol': lambda i, pi: (F(i['d1']) * F(i['v1']) + F(i['d2']) * F(i['v2'])) / (F(i['v1']) + F(i['v2'])),
    'cm_alloy_pct': lambda i, pi: (F(i['pa']) + F(i['pb'])) / (F(i['pa']) / F(i['da']) + F(i['pb']) / F(i['db'])),
    'cm_composite_density': lambda i, pi: (F(i['r1']) * F(i['d1']) + F(i['r2']) * F(i['d2'])) / (F(i['r1']) + F(i['r2'])),
    'cm_box_pressure': lambda i, pi: F(i['mass']) * F(i['g']) / (F(i['length']) * F(i['width'])),
    'cm_pipes': lambda i, pi: F(i['vol']) / (F(i['fill']) - F(i['drain'])),
    'cm_overtake': lambda i, pi: F(i['head_min']) * F(i['slow']) / (F(i['fast']) - F(i['slow'])),
    'cm_relative': lambda i, pi: _relative_time(i, i['direction']),
    'cm_hollow_cyl_mass': lambda i, pi: pi * (F(i['R']) ** 2 - F(i['r']) ** 2) * F(i['h']) * F(i['density']),
    'cm_sphere_mass': lambda i, pi: Fraction(4, 3) * pi * F(i['r']) ** 3 * F(i['density']),
}


def _sgn(i):
    return {'up': 1, 'down': -1}[i['sign']]


def _directed(i, flip):
    a, b = F(i['a']), F(i['b']) * flip
    op = i['op']
    if op == '+':
        return a + b
    if op in ('-', '−'):
        return a - b
    raise ValueError('operator')


def _part_fraction(i):
    parts = [F(p) for p in _items(i['parts'])]
    which = _n(i['which'])
    if not 0 <= which < len(parts):
        raise ValueError('which')
    return parts[which] / sum(parts)


def _relative_time(i, direction):
    s1, s2, dist = F(i['s1']), F(i['s2']), F(i['dist'])
    if direction == 'same':
        return dist / abs(s1 - s2) * 60
    if direction == 'opposite':
        return dist / (s1 + s2) * 60
    raise ValueError('direction')


def _relative_wrong(i):
    s1, s2, dist = F(i['s1']), F(i['s2']), F(i['dist'])
    other = 'opposite' if i['direction'] == 'same' else 'same'
    return [_relative_time(i, other)]


# ---------------------------------------------------------------------------------------------
# Rules: for each family, the values a slip gives
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class TopicRule:
    id: str
    message: str                       # a key of misconceptions.MESSAGES
    families: tuple
    slip: Callable                     # (inputs, pi) -> list of exact values (may be empty)


def _r(rid, message, families, slip):
    return TopicRule(rid, message, tuple(families), slip)


def _trig_side_wrong_ratio(i, pi):
    fn, op = _ratio_t(i)
    out = []
    for f2 in ('sin', 'cos', 'tan'):
        if f2 == fn:
            continue
        for o2 in ('mul', 'div'):
            v = _trig_side_value(i, f2, o2)
            if v is not None:
                out.append(v)
    return out


def _trig_side_rearranged(i, pi):
    fn, op = _ratio_t(i)
    v = _trig_side_value(i, fn, 'div' if op == 'mul' else 'mul')
    return [] if v is None else [v]


def _trig_side_radians(i, pi):
    fn, op = _ratio_t(i)
    v = _trig_side_value(i, fn, op, radians=True)
    return [] if v is None else [v]


def _trig_angle_radians(i, pi):
    fn, ratio = _angle_inputs(i)
    v = inverse(fn, ratio, radians=True)
    return [] if v is None else [v]


def _trig_angle_ratio(i, pi):
    fn, ratio = _angle_inputs(i)
    return [ratio]


def _trig_angle_other(i, pi):
    fn, ratio = _angle_inputs(i)
    v = inverse(fn, ratio)
    return [] if v is None else [90 - v]


def _cosine_side_parts(i, radians=False, plus=False):
    b, c, angle = F(i['b']), F(i['c']), F(i['angle'])
    cos_a = trig('cos', angle, radians)
    inside = b * b + c * c + (1 if plus else -1) * 2 * b * c * cos_a
    return inside


def _cosine_side_no_root(i, pi):
    return [_cosine_side_parts(i)]


def _cosine_side_plus(i, pi):
    v = _cosine_side_parts(i, plus=True)
    return [sqrtq(v)] if v >= 0 else []


def _cosine_side_radians(i, pi):
    v = _cosine_side_parts(i, radians=True)
    return [sqrtq(v)] if v >= 0 else []


def _sector_fraction(i):
    return F(i['angle']) / 360


def _scale_sim(i, pi):
    value, k, power = F(i['value']), F(i['k']), _n(i['power'])
    return [value * k ** p for p in (1, 2, 3) if p != power]


def _mean_speed_leg_pairs(i, pi):
    return [_mean([s for d, s in _legs_distance_speed(i)])]


def _mean_speed_time_legs(i, pi):
    return [_mean([s for t, s in _legs_time_speed(i)])]


def _pct_change_pair(i):
    """(base, other) for the percentage families: the amount a percentage is taken of, and the other amount.

    Percentage change and profit divide by the original amount (the cost); percentage error divides by the actual
    value, so its "wrong base" is the estimate (review 2026-10-26: the estimate was used as the base before, which
    made the wrong-base value equal the key, so the rule never fired).
    """
    if 'original' in i:
        return F(i['original']), F(i['new'])
    if 'cost' in i:
        return F(i['cost']), F(i['selling'])
    return F(i['actual']), F(i['estimate'])


RULES: tuple = (
    # ---- mensuration -------------------------------------------------------------------------------
    _r('mens.area_uses_circumference', 'mens.circumference_formula', ['mens_circle_area'],
       lambda i, pi: [2 * pi * F(i['r'])]),
    _r('mens.area_not_squared', 'mens.not_squared', ['mens_circle_area'],
       lambda i, pi: [pi * F(i['r'])]),
    _r('mens.circumference_uses_area', 'mens.area_formula', ['mens_circumference'],
       lambda i, pi: [pi * F(i['r']) ** 2]),
    _r('mens.circumference_pi_r', 'mens.radius_not_diameter', ['mens_circumference'],
       lambda i, pi: [pi * F(i['r'])]),
    _r('mens.circumference_of_diameter_doubled', 'mens.diameter_as_radius', ['mens_circumference'],
       lambda i, pi: [4 * pi * F(i['r'])]),
    _r('mens.sector_whole_circle', 'mens.whole_circle', ['mens_sector_area'],
       lambda i, pi: [pi * F(i['r']) ** 2]),
    _r('mens.sector_uses_arc', 'mens.arc_formula', ['mens_sector_area'],
       lambda i, pi: [_arc(i, pi)]),
    _r('mens.arc_whole_circle', 'mens.whole_circle', ['mens_arc', 'mens_arc_exact'],
       lambda i, pi: [2 * pi * F(i['r'])]),
    _r('mens.arc_uses_sector', 'mens.sector_formula', ['mens_arc', 'mens_arc_exact'],
       lambda i, pi: [_sector_fraction(i) * pi * F(i['r']) ** 2]),
    _r('mens.sector_perimeter_arc_only', 'mens.perimeter_arc_only', ['mens_sector_perimeter'],
       lambda i, pi: [_arc(i, pi)]),
    _r('mens.cylinder_volume_not_squared', 'mens.not_squared', ['mens_cyl_vol', 'mens_exact_pi_cyl'],
       lambda i, pi: [pi * F(i['r']) * F(i['h'])]),
    _r('mens.cylinder_volume_is_area', 'mens.area_for_volume', ['mens_cyl_vol', 'mens_exact_pi_cyl'],
       lambda i, pi: [2 * pi * F(i['r']) * (F(i['r']) + F(i['h']))]),
    _r('mens.cylinder_area_curved_only', 'mens.curved_only', ['mens_cyl_sa'],
       lambda i, pi: [2 * pi * F(i['r']) * F(i['h'])]),
    _r('mens.cylinder_area_is_volume', 'mens.volume_for_area', ['mens_cyl_sa'],
       lambda i, pi: [pi * F(i['r']) ** 2 * F(i['h'])]),
    _r('mens.cone_area_curved_only', 'mens.curved_only', ['mens_cone_sa_slant'],
       lambda i, pi: [pi * F(i['r']) * F(i['slant'])]),
    _r('mens.cone_volume_no_third', 'mens.no_third', ['mens_cone_vol'],
       lambda i, pi: [pi * F(i['r']) ** 2 * F(i['h'])]),
    _r('mens.pyramid_volume_no_third', 'mens.no_third', ['mens_pyramid_vol'],
       lambda i, pi: [F(i['l']) * F(i['w']) * F(i['h'])]),
    _r('mens.cone_volume_slant_as_height', 'mens.slant_for_height', ['mens_cone_vol_from_slant'],
       lambda i, pi: [pi * F(i['r']) ** 2 * F(i['slant']) / 3]),
    _r('mens.cone_area_height_as_slant', 'mens.height_for_slant', ['mens_cone_sa_height'],
       lambda i, pi: [pi * F(i['r']) * (F(i['r']) + F(i['h']))]),
    _r('mens.sphere_area_is_volume', 'mens.volume_for_area', ['mens_sphere_sa'],
       lambda i, pi: [Fraction(4, 3) * pi * F(i['r']) ** 3]),
    _r('mens.sphere_volume_is_area', 'mens.area_for_volume', ['mens_sphere_vol'],
       lambda i, pi: [4 * pi * F(i['r']) ** 2]),
    _r('mens.sphere_volume_not_cubed', 'mens.not_cubed', ['mens_sphere_vol', 'cm_sphere_mass'],
       lambda i, pi: [Fraction(4, 3) * pi * F(i['r']) ** 2 * (F(i['density']) if 'density' in i else 1)]),
    _r('mens.triangle_full_rectangle', 'mens.full_rectangle', ['mens_tri_area'],
       lambda i, pi: [F(i['b']) * F(i['h'])]),
    _r('mens.trapezium_full_rectangle', 'mens.full_rectangle', ['mens_trapezium'],
       lambda i, pi: [(F(i['a']) + F(i['b'])) * F(i['h'])]),
    _r('mens.prism_full_rectangle', 'mens.full_rectangle', ['mens_tri_prism_vol'],
       lambda i, pi: [F(i['b']) * F(i['h']) * F(i['length'])]),
    _r('mens.cuboid_volume_is_area', 'mens.area_for_volume', ['mens_cuboid_vol'],
       lambda i, pi: [2 * (F(i['l']) * F(i['w']) + F(i['l']) * F(i['h']) + F(i['w']) * F(i['h']))]),
    _r('mens.cuboid_area_is_volume', 'mens.volume_for_area', ['mens_cuboid_sa'],
       lambda i, pi: [F(i['l']) * F(i['w']) * F(i['h'])]),
    _r('mens.cuboid_area_faces_missed', 'mens.faces_missed', ['mens_cuboid_sa'],
       lambda i, pi: [F(i['l']) * F(i['w']) + F(i['l']) * F(i['h']) + F(i['w']) * F(i['h'])]),
    _r('mens.rectangle_perimeter_is_area', 'mens.area_for_perimeter', ['mens_rect_perimeter'],
       lambda i, pi: [F(i['l']) * F(i['w'])]),
    _r('mens.rectangle_perimeter_half', 'mens.half_perimeter', ['mens_rect_perimeter'],
       lambda i, pi: [F(i['l']) + F(i['w'])]),
    _r('mens.l_shape_added', 'mens.cutout_added', ['mens_l_shape'],
       lambda i, pi: [F(i['a']) * F(i['c']) + F(i['b']) * F(i['d'])]),
    _r('mens.annulus_squared_difference', 'mens.annulus_order', ['mens_annulus'],
       lambda i, pi: [pi * (F(i['R']) - F(i['r'])) ** 2]),
    _r('mens.annulus_outer_only', 'mens.hole_ignored', ['mens_annulus'],
       lambda i, pi: [pi * F(i['R']) ** 2]),
    _r('mens.pipe_squared_difference', 'mens.annulus_order', ['cm_hollow_cyl_mass'],
       lambda i, pi: [pi * (F(i['R']) - F(i['r'])) ** 2 * F(i['h']) * F(i['density'])]),
    _r('mens.pipe_solid', 'mens.hole_ignored', ['cm_hollow_cyl_mass'],
       lambda i, pi: [pi * F(i['R']) ** 2 * F(i['h']) * F(i['density'])]),
    _r('mens.diameter_found_for_radius', 'mens.diameter_found', ['mens_radius_from_area'],
       lambda i, pi: [2 * sqrtq(F(i['area']) / pi)]),
    _r('mens.radius_found_for_diameter', 'mens.radius_found', ['mens_diameter'],
       lambda i, pi: [F(i['circ']) / (2 * pi)]),
    _r('mens.radius_squared_not_rooted', 'gen.squared', ['mens_radius_from_area'],
       lambda i, pi: [F(i['area']) / pi]),
    _r('mens.height_from_volume_not_squared', 'mens.not_squared', ['mens_cyl_height'],
       lambda i, pi: [F(i['vol']) / (pi * F(i['r']))]),
    _r('mens.area_units_squared', 'mens.area_units', ['mens_cm2_to_m2'],
       lambda i, pi: [F(i['l']) * F(i['w']) / 100]),
    _r('mens.area_units_not_converted', 'unit.not_converted', ['mens_cm2_to_m2'],
       lambda i, pi: [F(i['l']) * F(i['w'])]),
    _r('mens.litres_not_converted', 'mens.volume_units', ['mens_fill_time'],
       lambda i, pi: [pi * F(i['r']) ** 2 * F(i['h']) / F(i['rate'])]),
    _r('mens.similar_power', 'sim.wrong_power', ['mens_similar'], _scale_sim),
    # ---- Pythagoras --------------------------------------------------------------------------------
    _r('pyth.hyp_not_rooted', 'gen.squared', ['pyth_hyp'], lambda i, pi: [F(i['a']) ** 2 + F(i['b']) ** 2]),
    _r('pyth.hyp_sides_added', 'pyth.sides_not_squares', ['pyth_hyp'], lambda i, pi: [F(i['a']) + F(i['b'])]),
    _r('pyth.hyp_subtracted', 'pyth.subtracted_for_hyp', ['pyth_hyp'],
       lambda i, pi: [sqrtq(abs(F(i['a']) ** 2 - F(i['b']) ** 2))] if F(i['a']) != F(i['b']) else []),
    _r('pyth.leg_added', 'pyth.added_for_short', ['pyth_leg'],
       lambda i, pi: [sqrtq(F(i['c']) ** 2 + F(i['a']) ** 2)]),
    _r('pyth.leg_not_rooted', 'gen.squared', ['pyth_leg'], lambda i, pi: [F(i['c']) ** 2 - F(i['a']) ** 2]),
    _r('pyth.leg_sides_subtracted', 'pyth.sides_not_squares', ['pyth_leg'], lambda i, pi: [F(i['c']) - F(i['a'])]),
    _r('pyth.distance_not_rooted', 'gen.squared', ['pyth_dist'],
       lambda i, pi: [(F(i['x2']) - F(i['x1'])) ** 2 + (F(i['y2']) - F(i['y1'])) ** 2]),
    _r('pyth.distance_differences_added', 'pyth.sides_not_squares', ['pyth_dist'],
       lambda i, pi: [abs(F(i['x2']) - F(i['x1'])) + abs(F(i['y2']) - F(i['y1']))]),
    _r('pyth.perimeter_sides', 'pyth.perimeter_sides', ['pyth_perimeter'],
       lambda i, pi: [sqrtq(F(i['a']) ** 2 + F(i['b']) ** 2), F(i['a']) + F(i['b'])]),
    _r('pyth.height_base_not_halved', 'pyth.base_not_halved', ['pyth_isosceles_height'],
       lambda i, pi: [sqrtq(F(i['side']) ** 2 - F(i['base']) ** 2)] if F(i['side']) >= F(i['base']) else []),
    _r('pyth.height_added', 'pyth.added_for_short', ['pyth_isosceles_height'],
       lambda i, pi: [sqrtq(F(i['side']) ** 2 + (F(i['base']) / 2) ** 2)]),
    _r('pyth.height_not_rooted', 'gen.squared', ['pyth_isosceles_height'],
       lambda i, pi: [F(i['side']) ** 2 - (F(i['base']) / 2) ** 2]),
    _r('pyth.space_not_rooted', 'gen.squared', ['pyth_space_diag'],
       lambda i, pi: [F(i['l']) ** 2 + F(i['w']) ** 2 + F(i['h']) ** 2]),
    _r('pyth.space_one_step_short', 'pyth.one_step_short', ['pyth_space_diag'],
       lambda i, pi: [sqrtq(F(i['l']) ** 2 + F(i['w']) ** 2)]),
    _r('pyth.space_sides_added', 'pyth.sides_not_squares', ['pyth_space_diag'],
       lambda i, pi: [F(i['l']) + F(i['w']) + F(i['h'])]),
    _r('pyth.ladder_original_position', 'pyth.original_position', ['pyth_ladder_slide'],
       lambda i, pi: [sqrtq(F(i['ladder']) ** 2 - F(i['base']) ** 2)]),
    # ---- trigonometry ------------------------------------------------------------------------------
    _r('trig.side_wrong_ratio', 'trig.wrong_ratio', ['trig_side'], _trig_side_wrong_ratio),
    _r('trig.side_rearranged', 'trig.rearranged', ['trig_side'], _trig_side_rearranged),
    _r('trig.side_radians', 'trig.radians', ['trig_side'], _trig_side_radians),
    _r('trig.angle_radians', 'trig.radians', ['trig_angle', 'trig_sine_angle', 'trig_cosine_angle'],
       lambda i, pi: _angle_radians_any(i)),
    _r('trig.angle_ratio_only', 'trig.ratio_not_inverted', ['trig_angle', 'trig_sine_angle', 'trig_cosine_angle'],
       lambda i, pi: _angle_ratio_any(i)),
    _r('trig.angle_other', 'trig.other_angle', ['trig_angle'], _trig_angle_other),
    _r('trig.cosine_side_not_rooted', 'gen.squared', ['trig_cosine_side'], _cosine_side_no_root),
    _r('trig.cosine_side_sign', 'trig.cosine_sign', ['trig_cosine_side'], _cosine_side_plus),
    _r('trig.cosine_side_radians', 'trig.radians', ['trig_cosine_side'], _cosine_side_radians),
    _r('trig.area_full_product', 'trig.area_parallelogram', ['trig_area'],
       lambda i, pi: [F(i['a']) * F(i['b']) * trig('sin', F(i['angle']))]),
    _r('trig.area_radians', 'trig.radians', ['trig_area'],
       lambda i, pi: [F(i['a']) * F(i['b']) * trig('sin', F(i['angle']), True) / 2]),
    _r('trig.area_cosine', 'trig.area_sine', ['trig_area'],
       lambda i, pi: [F(i['a']) * F(i['b']) * trig('cos', F(i['angle'])) / 2]),
    _r('trig.sine_side_inverted', 'trig.sine_rule_inverted', ['trig_sine_side'],
       lambda i, pi: [F(i['known_side']) * trig('sin', F(i['known_angle'])) / trig('sin', F(i['target_angle']))]),
    _r('trig.sine_side_radians', 'trig.radians', ['trig_sine_side'],
       lambda i, pi: [F(i['known_side']) * trig('sin', F(i['target_angle']), True) / trig('sin', F(i['known_angle']), True)]),
    _r('trig.apex_half', 'trig.half_angle', ['trig_isosceles_apex'],
       lambda i, pi: [inverse('asin', F(i['base']) / 2 / F(i['equal']))]),
    # ---- percentages, fractions and number ---------------------------------------------------------
    _r('pct.change_only', 'pct.change_not_applied', ['num_pct_change'],
       lambda i, pi: [F(i['amount']) * F(i['pct']) / 100]),
    _r('pct.change_opposite', 'pct.opposite', ['num_pct_change'],
       lambda i, pi: [F(i['amount']) * (1 - _sgn(i) * F(i['pct']) / 100)]),
    _r('pct.reverse_as_forward', 'pct.reverse_as_forward', ['num_reverse_pct'],
       lambda i, pi: [F(i['final']) * (1 - _sgn(i) * F(i['pct']) / 100)]),
    _r('pct.reverse_opposite', 'pct.opposite', ['num_reverse_pct'],
       lambda i, pi: [F(i['final']) / (1 - _sgn(i) * F(i['pct']) / 100)]),
    _r('pct.vat_only', 'pct.change_not_applied', ['num_vat_inclusive'],
       lambda i, pi: [F(i['price']) * F(i['vat']) / 100]),
    _r('pct.vat_taken_off', 'pct.opposite', ['num_vat_inclusive'],
       lambda i, pi: [F(i['price']) * (1 - F(i['vat']) / 100)]),
    _r('pct.changes_added', 'pct.changes_added', ['num_two_pct_changes'],
       lambda i, pi: [F(i['amount']) * (1 + (F(i['pct1']) - F(i['pct2'])) / 100)]),
    _r('pct.reverse_two_added', 'pct.changes_added', ['fdp_reverse_two_step'],
       lambda i, pi: [F(i['final']) / (1 + (F(i['pct_up']) - F(i['pct_down'])) / 100)]),
    _r('pct.compound_simple', 'pct.same_each_year', ['num_compound'],
       lambda i, pi: [F(i['principal']) * (1 + _sgn(i) * F(i['rate']) / 100 * _n(i['years']))]),
    _r('pct.compound_opposite', 'pct.opposite', ['num_compound'],
       lambda i, pi: [F(i['principal']) * (1 - _sgn(i) * F(i['rate']) / 100) ** _n(i['years'])]),
    _r('pct.reverse_compound_forward', 'pct.reverse_as_forward', ['num_reverse_compound'],
       lambda i, pi: [F(i['final']) * (1 - F(i['rate']) / 100) ** _n(i['years'])]),
    _r('pct.reverse_compound_one_year', 'pct.years_missed', ['num_reverse_compound'],
       lambda i, pi: [F(i['final']) / (1 + F(i['rate']) / 100)]),
    _r('pct.of_divided', 'pct.of_divided', ['num_pct_of'],
       lambda i, pi: [F(i['amount']) / F(i['pct'])]),
    _r('pct.wrong_base', 'pct.wrong_base', ['fdp_pct_change', 'fdp_profit_pct'],
       lambda i, pi: _wrong_base(i)),
    _r('pct.change_not_compared', 'pct.change_not_compared', ['fdp_pct_change', 'fdp_profit_pct'],
       lambda i, pi: _change_only(i)),
    # Percentage error has its own words: the error is compared with the actual value, not an "original amount".
    _r('pct.error_wrong_base', 'pct.error_wrong_base', ['num_pct_error'], lambda i, pi: _wrong_base(i)),
    _r('pct.error_not_compared', 'pct.error_not_compared', ['num_pct_error'], lambda i, pi: _change_only(i)),
    _r('pct.discount_only', 'pct.change_not_applied', ['fdp_shop_discount'],
       lambda i, pi: [F(i['unit']) * F(i['qty']) * F(i['discount_pct']) / 100]),
    _r('pct.discount_added', 'pct.opposite', ['fdp_shop_discount'],
       lambda i, pi: [F(i['unit']) * F(i['qty']) * (1 + F(i['discount_pct']) / 100)]),
    _r('fdp.other_part', 'fdp.other_part', ['fdp_fraction_not'],
       lambda i, pi: [F(i['total']) * F(i['num']) / F(i['den'])]),
    _r('fdp.fraction_inverted_of', 'fdp.fraction_inverted', ['num_frac_of'],
       lambda i, pi: [F(i['amount']) * F(i['den']) / F(i['num'])]),
    _r('fdp.bottom_only', 'fdp.bottom_only', ['num_frac_of'],
       lambda i, pi: [F(i['amount']) / F(i['den'])]),
    _r('fdp.fraction_to_pct_inverted', 'fdp.fraction_inverted', ['fdp_fraction_to_pct'],
       lambda i, pi: [F(i['b']) / F(i['a']) * 100]),
    _r('fdp.decimal_fraction_place_value', 'fdp.place_value_fraction', ['fdp_decimal_to_fraction'],
       lambda i, pi: [F(i['dec']) / 10, F(i['dec']) * 10]),
    _r('fdp.pct_fraction_per_cent', 'fdp.per_cent', ['fdp_pct_to_fraction'],
       lambda i, pi: [F(i['pct']) / 10, F(i['pct']) / 1000]),
    _r('dec.mean_total', 'dec.mean_total', ['dec_mean'],
       lambda i, pi: [sum(F(v) for v in _items(i['values']))]),
    _r('est.exact_product', 'dec.estimate_exact', ['num_estimate_product_1sf', 'num_estimate_product_whole'],
       lambda i, pi: [F(i['a']) * F(i['b'])]),
    _r('est.exact_fraction', 'dec.estimate_exact', ['num_estimate_fraction_1sf'],
       lambda i, pi: [F(i['a']) * F(i['b']) / F(i['c'])]),
    _r('est.rounded_late', 'dec.estimate_order', ['num_estimate_product_1sf'],
       lambda i, pi: [round_sf(F(i['a']) * F(i['b']), 1)]),
    _r('est.rounded_late_fraction', 'dec.estimate_order', ['num_estimate_fraction_1sf'],
       lambda i, pi: [round_sf(F(i['a']) * F(i['b']) / F(i['c']), 1)]),
    _r('num.double_negative', 'num.double_negative', ['num_directed'],
       lambda i, pi: [_directed(i, -1)] if F(i['b']) < 0 else []),
    _r('idx.multiplied', 'idx.multiplied', ['num_power'],
       lambda i, pi: [F(i['base']) * F(i['exp'])]),
    _r('idx.negative_power', 'idx.negative_power', ['num_neg_index'],
       lambda i, pi: [-(F(i['base']) ** _n(i['power'])), -ONE / F(i['base']) ** _n(i['power'])]),
    _r('idx.power_sign_ignored', 'idx.power_sign_ignored', ['num_neg_index'],
       lambda i, pi: [F(i['base']) ** _n(i['power'])]),
    _r('idx.zero_power', 'idx.zero_power', ['num_zero_neg_index'],
       lambda i, pi: [F(i['a']) / F(i['b']) ** 2, Fraction(0)]),
    _r('idx.fraction_power', 'idx.fraction_power', ['num_frac_index'],
       lambda i, pi: [F(i['base']) * F(i['num']) / F(i['den'])]),
    # ---- order of operations -----------------------------------------------------------------------
    _r('bidmas.left_to_right', 'bidmas.left_to_right', ['arith'], _expr_left_to_right),
    _r('bidmas.brackets_ignored', 'bidmas.brackets_ignored', ['arith'], _expr_brackets_ignored),
    _r('bidmas.power_multiplied', 'idx.multiplied', ['arith'], _expr_power_multiplied),
    _r('bidmas.negative_square', 'bidmas.negative_square', ['arith'], _expr_negative_square),
    # ---- one-step products and quotients (any topic) -----------------------------------------------
    _r('op.divided_for_product', 'op.multiply_needed', ['product'],
       lambda i, pi: [F(i['a']) / F(i['b']), F(i['b']) / F(i['a']), F(i['a']) + F(i['b'])]),
    _r('op.multiplied_for_quotient', 'op.divide_needed', ['quotient'],
       lambda i, pi: [F(i['a']) * F(i['b'])]),
    # Review 2026-10-26: the formula-triangle slip (volume over mass for a density, time over distance for a speed).
    # The generic reciprocal rule names the same slip but, with no stated accuracy, only for the exact value; with
    # the inputs the value rounded to the pupil's own places is matched too. Same message as the generic rule.
    _r('op.quotient_inverted', 'gen.reciprocal', ['quotient'],
       lambda i, pi: [F(i['b']) / F(i['a'])]),
    # ---- ratio and proportion ----------------------------------------------------------------------
    _r('ratio.map_not_converted', 'unit.not_converted', ['ratio_map_scale'],
       lambda i, pi: [F(i['cm']) * F(i['scale'])]),
    _r('ratio.map_divided', 'ratio.scale_direction', ['ratio_map_scale'],
       lambda i, pi: [F(i['cm']) / F(i['scale'])]),
    _r('ratio.direct_inverse_used', 'ratio.inverse_for_direct', ['prop_direct'],
       lambda i, pi: [F(i['y1']) * F(i['x1']) / F(i['x2'])]),
    _r('ratio.direct_additive', 'ratio.additive', ['prop_direct'],
       lambda i, pi: [F(i['y1']) + F(i['x2']) - F(i['x1'])]),
    _r('ratio.direct_unit_only', 'ratio.unit_only', ['prop_direct'],
       lambda i, pi: [F(i['y1']) / F(i['x1'])]),
    _r('ratio.inverse_direct_used', 'ratio.direct_for_inverse', ['prop_inverse'],
       lambda i, pi: [F(i['b']) * F(i['c']) / F(i['a'])]),
    _r('ratio.scale_inverse_used', 'ratio.inverse_for_direct', ['prop_scale'],
       lambda i, pi: [F(i['q1']) * F(i['n1']) / F(i['n2'])]),
    _r('ratio.scale_unit_only', 'ratio.unit_only', ['prop_scale'],
       lambda i, pi: [F(i['q1']) / F(i['n1'])]),
    _r('ratio.scale_additive', 'ratio.additive', ['prop_scale'],
       lambda i, pi: [F(i['q1']) + F(i['n2']) - F(i['n1'])]),
    _r('ratio.unitary_unit_only', 'ratio.unit_only', ['ratio_unitary'],
       lambda i, pi: [F(i['total']) / F(i['n1'])]),
    _r('ratio.unitary_inverse_used', 'ratio.inverse_for_direct', ['ratio_unitary'],
       lambda i, pi: [F(i['total']) * F(i['n1']) / F(i['n2'])]),
    _r('ratio.missing_parts_swapped', 'ratio.parts_swapped', ['ratio_find_missing'],
       lambda i, pi: [F(i['known']) * F(i['a']) / F(i['b'])]),
    _r('ratio.missing_unit_only', 'ratio.unit_only', ['ratio_find_missing'],
       lambda i, pi: [F(i['known']) / F(i['a'])]),
    _r('ratio.missing_additive', 'ratio.additive', ['ratio_find_missing'],
       lambda i, pi: [F(i['known']) + F(i['b']) - F(i['a'])]),
    _r('ratio.part_to_part', 'ratio.part_to_part', ['ratio_part_fraction'],
       lambda i, pi: _part_to_part(i)),
    # ---- compound measures -------------------------------------------------------------------------
    _r('cm.speed_direction_kmh', 'cm.speed_direction', ['cm_kmh_to_ms'],
       lambda i, pi: [F(i['kmh']) * Fraction(18, 5)]),
    _r('cm.speed_one_unit_kmh', 'cm.speed_one_unit', ['cm_kmh_to_ms'],
       lambda i, pi: [F(i['kmh']) * 1000, F(i['kmh']) / 3600]),
    _r('cm.speed_direction_ms', 'cm.speed_direction', ['cm_ms_to_kmh'],
       lambda i, pi: [F(i['ms']) * Fraction(5, 18)]),
    _r('cm.speed_one_unit_ms', 'cm.speed_one_unit', ['cm_ms_to_kmh'],
       lambda i, pi: [F(i['ms']) * 3600, F(i['ms']) / 1000]),
    _r('cm.minutes_decimal_hm', 'cm.minutes_decimal', ['cm_speed_hm'],
       lambda i, pi: [F(i['s']) * (F(i['h']) + F(i['m']) / 100)]),
    _r('cm.minutes_unconverted_hm', 'cm.minutes_not_converted', ['cm_speed_hm'],
       lambda i, pi: [F(i['s']) * (F(i['h']) * 60 + F(i['m']))]),
    _r('cm.minutes_decimal_mins', 'cm.minutes_decimal', ['cm_dist_mins'],
       lambda i, pi: [F(i['s']) * F(i['mins']) / 100]),
    _r('cm.minutes_unconverted_mins', 'cm.minutes_not_converted', ['cm_dist_mins'],
       lambda i, pi: [F(i['s']) * F(i['mins'])]),
    _r('cm.mean_of_speeds', 'cm.mean_of_speeds', ['cm_avg_speed'], _mean_speed_leg_pairs),
    _r('cm.mean_of_speeds_time', 'cm.mean_of_speeds', ['cm_avg_speed_time'], _mean_speed_time_legs),
    _r('cm.mean_of_two_speeds', 'cm.mean_of_speeds', ['cm_avg_speed_equal'],
       lambda i, pi: [(F(i['s1']) + F(i['s2'])) / 2]),
    _r('cm.mean_of_densities', 'cm.mean_of_densities', ['cm_alloy_vol', 'cm_composite_density'],
       lambda i, pi: [(F(i['d1']) + F(i['d2'])) / 2]),
    _r('cm.alloy_weighted_mean', 'cm.mean_of_densities', ['cm_alloy_pct'],
       lambda i, pi: [(F(i['pa']) * F(i['da']) + F(i['pb']) * F(i['db'])) / (F(i['pa']) + F(i['pb'])),
                      (F(i['da']) + F(i['db'])) / 2]),
    _r('cm.pressure_from_mass', 'cm.weight_force', ['cm_box_pressure'],
       lambda i, pi: [F(i['mass']) / (F(i['length']) * F(i['width']))]),
    _r('cm.pipes_combined', 'cm.rates_combined', ['cm_pipes'],
       lambda i, pi: [F(i['vol']) / (F(i['fill']) + F(i['drain'])), F(i['vol']) / F(i['fill'])]),
    _r('cm.closing_speed_overtake', 'cm.relative_speed', ['cm_overtake'],
       lambda i, pi: [F(i['head_min']) * F(i['slow']) / (F(i['fast']) + F(i['slow']))]),
    _r('cm.closing_speed_relative', 'cm.relative_speed', ['cm_relative'],
       lambda i, pi: _relative_wrong(i)),
)


def _part_to_part(i):
    parts = [F(p) for p in _items(i['parts'])]
    which = _n(i['which'])
    total = sum(parts)
    rest = total - parts[which]
    return [] if rest == 0 else [parts[which] / rest]


def _wrong_base(i):
    original, new = _pct_change_pair(i)
    change = abs(new - original)
    return [change / new * 100] if new != 0 else []


def _change_only(i):
    original, new = _pct_change_pair(i)
    return [abs(new - original)]


def _angle_radians_any(i, pi=None):
    if 'a' in i and 'angle_b' in i:                          # sine rule angle
        r = F(i['a']) * trig('sin', F(i['angle_b'])) / F(i['b'])
        v = inverse('asin', r, radians=True)
    elif 'a' in i and 'c' in i:                              # cosine rule angle
        r = (F(i['b']) ** 2 + F(i['c']) ** 2 - F(i['a']) ** 2) / (2 * F(i['b']) * F(i['c']))
        v = inverse('acos', r, radians=True)
    else:
        fn, r = _angle_inputs(i)
        v = inverse(fn, r, radians=True)
    return [] if v is None else [v]


def _angle_ratio_any(i, pi=None):
    if 'a' in i and 'angle_b' in i:
        return [F(i['a']) * trig('sin', F(i['angle_b'])) / F(i['b'])]
    if 'a' in i and 'c' in i:
        return [(F(i['b']) ** 2 + F(i['c']) ** 2 - F(i['a']) ** 2) / (2 * F(i['b']) * F(i['c']))]
    return [_angle_inputs(i)[1]]


# The "diameter used where the radius belongs" rule needs the family's own formula with 2r in place of r, so it is
# built from TRUTH (the formula under test) rather than repeating each formula; a rule can only ever fire for a
# family whose truth reproduces the key, so reusing TRUTH here cannot hide a formula error.
_DIAMETER_FAMILIES = ('mens_circle_area', 'mens_cyl_vol', 'mens_cone_vol', 'mens_sphere_vol', 'mens_sphere_sa')


def _diameter_as_radius(family):
    def slip(i, pi):
        doubled = dict(i)
        doubled['r'] = 2 * F(i['r'])
        return [TRUTH[family](doubled, pi)]
    return slip


RULES = RULES + tuple(
    _r(f'mens.diameter_as_radius.{fam}', 'mens.diameter_as_radius', [fam], _diameter_as_radius(fam))
    for fam in _DIAMETER_FAMILIES)


# ---------------------------------------------------------------------------------------------
# Quiet values (review 2026-10-26): values a pupil may well type for a reason no rule names. A rule's value that
# coincides with one of them (at the accuracy the pupil gives) is not shown, because the coincidence makes the named
# slip only one of several explanations. Silence is better than a misleading hint.
#
# * Every number the question prints (``input_numbers``): a typed number copied from the question, or a slip that
#   happens to land on one (the face diagonal of a 3, 4, 5 cuboid is the height 5; 1 x 4 for "1/4 as a decimal" is
#   the 4 of the question, which is better read as a division done the other way round).
# * ``QUIET[family]``: other plausible slips with no message of their own. A calculator in radians can land on them
#   by chance (cos of 66 radians is almost minus one, so the cosine rule in radians gives about b + c).
#
# ``ECHO_OK`` lists the rules whose slip naturally gives back a number of the question: +15% then -15% taken to
# cancel; the mean of three speeds (80, 60 and 40 km/h) is the middle speed, and typing 60 there is the slip, not a
# copied number.
# ---------------------------------------------------------------------------------------------

_NUMBER_IN_TEXT = re.compile(r'\d+(?:\.\d+)?')


def input_numbers(inputs):
    """Every number in the recorded inputs (lists walked, numbers inside an expression read), as Fractions."""
    out = []

    def walk(v, depth=0):
        if depth > 3 or len(out) > 40:
            return
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, (int, float)):
            try:
                out.append(F(v))
            except (ValueError, ZeroDivisionError, OverflowError):
                pass
        elif isinstance(v, str):
            for m in _NUMBER_IN_TEXT.findall(v[:80]):
                try:
                    out.append(F(m))
                except (ValueError, ZeroDivisionError):
                    pass
        elif isinstance(v, (list, tuple)):
            for x in v[:MAX_TERMS]:
                walk(x, depth + 1)

    if isinstance(inputs, dict):
        for value in list(inputs.values())[:MAX_TERMS]:
            walk(value)
    return out


QUIET: dict[str, Callable] = {
    # the cosine rule with the cosine term left out, or the sides added or subtracted directly
    'trig_cosine_side': lambda i, pi: [F(i['b']) + F(i['c']), abs(F(i['b']) - F(i['c'])),
                                       sqrtq(F(i['b']) ** 2 + F(i['c']) ** 2)],
    # the area of a triangle with the sine left out (with or without the half)
    'trig_area': lambda i, pi: [F(i['a']) * F(i['b']) / 2, F(i['a']) * F(i['b'])],
}

ECHO_OK = frozenset({'pct.reverse_two_added', 'pct.changes_added', 'cm.mean_of_speeds', 'cm.mean_of_speeds_time'})


def quiet_values(family, inputs, pi):
    """(input numbers, other quiet values) for a record; never raises."""
    nums = input_numbers(inputs)
    extra = []
    fn = QUIET.get(family)
    if fn is not None:
        try:
            extra = [Fraction(v) for v in fn(inputs, pi) if v is not None]
        except Exception:  # noqa: BLE001 - a record that does not fit is handled by the truth guard
            extra = []
    return nums, extra


# Phase 5 (waves C and D) lives in its own module, which needs the helpers above and adds to these tables. It is
# imported here, last, so that every name it takes from this module already exists; never import it on its own.
from generators.shared import misconception_cd as _cd  # noqa: E402

TRUTH.update(_cd.TRUTH)
QUIET.update(_cd.QUIET)
ECHO_OK = ECHO_OK | _cd.ECHO_OK
RULES = RULES + _cd.RULES

FAMILIES = frozenset(f for r in RULES for f in r.families) & frozenset(TRUTH)
RULES_BY_FAMILY: dict[str, tuple] = {}
for _rule in RULES:
    for _fam in _rule.families:
        RULES_BY_FAMILY.setdefault(_fam, ())
        RULES_BY_FAMILY[_fam] += (_rule,)
del _rule, _fam
RULES_BY_ID = {r.id: r for r in RULES}
