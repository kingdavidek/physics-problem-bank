"""Verification of the notes on multiple-choice distractors (docs/GCSE_MATHS_HINTS.md section 4, Phase 4).

A note says "this option is what you get if you make slip X". This module recomputes what slip X gives from the numbers
the question printed (the inputs the generator records with ``record()``) and checks that the tagged option is exactly
that value, so a note can never be attached to an option the slip does not lead to.

Independence rule (as the other verification modules): the slips below are written from the maths. They import no
generator and no helper of one; they read only the recorded inputs and the option text. The standard library and the
production note catalogue (to know which note ids exist) are all they use.

``SLIPS[(note_id, family)]`` is a function ``(inputs) -> [matcher, ...]``. A matcher is either a ``Val(x, unit)`` (the
option is the number x, rounded to the places it prints, in that unit when one is given) or a ``Pred(fn, why)`` (the
option text satisfies a test, for text options such as ``a x 10^b`` or an interval). A note id that is also the
message of a typed-answer rule (``misconception_topics.RULES``) falls back to that rule's values for the same family.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Optional

# ---------------------------------------------------------------------------------------------
# Reading an option
# ---------------------------------------------------------------------------------------------

_NUM = r'-?\d+(?:\.\d+)?'
_STD = re.compile(rf'^\s*({_NUM})\s*×\s*10\^\s*(-?\d+)\s*$')
_POW = re.compile(rf'^\s*({_NUM})\s*\^\s*(-?\d+)\s*$')
_FRAC = re.compile(r'^\s*(-?\d+)\s*/\s*(\d+)\s*$')
_RATIO = re.compile(r'^\s*(\d+)\s*:\s*(\d+)\s*$')
_INTERVAL = re.compile(rf'^\s*({_NUM})\s*(≤|<)\s*x\s*(≤|<)\s*({_NUM})\s*$')
_PLAIN = re.compile(rf'^\s*(£)?\s*({_NUM})\s*(%|[A-Za-z][A-Za-z ]*)?\s*$')


def F(x):
    if isinstance(x, Fraction):
        return x
    if isinstance(x, bool):
        raise ValueError('bool')
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(repr(x))
    return Fraction(str(x).strip().replace('−', '-'))


def dp_of(token):
    return len(token.split('.')[1]) if '.' in token else 0


@dataclass(frozen=True)
class Opt:
    kind: str                       # 'num', 'std', 'pow', 'ratio', 'interval' or 'text'
    value: Optional[Fraction] = None
    unit: str = ''
    dp: int = 0
    parts: tuple = ()               # std: (front number, power); pow: (base, exponent); ratio: (a, b); interval: (lo, lo_op, hi_op, hi)
    raw: str = ''                   # the text as shown


def read(text):
    from dataclasses import replace
    return replace(_read(text), raw=str(text).strip())


def _read(text):
    """The structure of an option's text, or ``Opt('text')`` when it is not a number, a power, a ratio or an interval."""
    t = str(text).strip().replace('−', '-')
    m = _STD.match(t)
    if m:
        front, power = F(m.group(1)), int(m.group(2))
        return Opt('std', front * Fraction(10) ** power, '', 0, (front, power))
    m = _POW.match(t)
    if m and abs(int(m.group(2))) <= 400:
        base, exp = F(m.group(1)), int(m.group(2))
        return Opt('pow', base ** exp if base != 0 or exp > 0 else None, '', 0, (base, exp))
    m = _FRAC.match(t)
    if m and int(m.group(2)):
        return Opt('num', Fraction(int(m.group(1)), int(m.group(2))), '', -1)
    m = _RATIO.match(t)
    if m:
        return Opt('ratio', None, '', 0, (int(m.group(1)), int(m.group(2))))
    m = _INTERVAL.match(t)
    if m:
        return Opt('interval', None, '', 0, (F(m.group(1)), m.group(2), m.group(3), F(m.group(4))))
    m = _PLAIN.match(t)
    if m:
        unit = (m.group(3) or '').strip().lower()
        if m.group(1):
            unit = '£' + unit
        return Opt('num', F(m.group(2)), unit, dp_of(m.group(2)))
    return Opt('text')


def half_up(x, dp):
    x = F(x)
    scale = Fraction(10) ** dp
    n = abs(x) * scale
    r = (n + Fraction(1, 2)).__floor__()
    return (r if x >= 0 else -r) / scale


# ---------------------------------------------------------------------------------------------
# Matchers
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Val:
    x: Fraction
    unit: Optional[str] = None


@dataclass(frozen=True)
class Pred:
    fn: Callable
    why: str = ''


def matches(opt, matcher, key_dp=None):
    """Does the option show what the matcher gives? A value is rounded half up to the places the option prints, but
    never to fewer places than the key prints (review: "£3" is not what a change of £2.50 gives when the key is "£12.5")."""
    if isinstance(matcher, Pred):
        return bool(matcher.fn(opt))
    if opt.kind in ('std', 'pow'):
        return opt.value is not None and opt.value == matcher.x
    if opt.kind != 'num' or opt.value is None:
        return False
    if matcher.unit is not None and opt.unit != matcher.unit:
        return False
    if opt.dp < 0 or matcher.x == opt.value:
        return matcher.x == opt.value
    if key_dp is not None and opt.dp < key_dp:
        return False
    return half_up(matcher.x, opt.dp) == opt.value


# lengths in metres, so "300 m" is seen to be worth the same as a key of "0.3 km" (review of Phase 4)
_LENGTH = {'mm': Fraction(1, 1000), 'cm': Fraction(1, 100), 'm': Fraction(1), 'km': Fraction(1000)}
# slips that are a coarser rounding: an option that is the key rounded is exactly what they describe
ROUNDING_SLIPS = frozenset({'gen.accuracy', 'mcq.round_dropped', 'mcq.round_place', 'mcq.digits_cut'})


def _base(opt):
    if opt.unit in _LENGTH:
        return opt.value * _LENGTH[opt.unit], 'length'
    return opt.value, opt.unit


def verify_option(note_id, family, inputs, text, key_text):
    """(ok, why) for one tagged option: the text is a value the slip gives, and it is not worth the key."""
    opt = read(text)
    key = read(key_text)
    # (standard form options such as 80 x 10^2 beside 8 x 10^3 are the same number in the wrong form: that is the slip)
    same_form = opt.kind != 'std' or key.kind != 'std' or opt.parts == key.parts
    if opt.value is not None and key.value is not None and _base(opt) == _base(key) and same_form:
        return False, 'the option is worth the same as the key'
    if (opt.kind == key.kind == 'num' and opt.value is not None and key.value is not None and opt.unit == key.unit
            and 0 <= opt.dp < key.dp and half_up(key.value, opt.dp) == opt.value and note_id not in ROUNDING_SLIPS):
        return False, 'the option is the key rounded to fewer places, so a pupil who rounded the right answer picks it'
    fn = SLIPS.get((note_id, family))
    ms = None
    if fn is not None:
        try:
            ms = fn(inputs)
        except (KeyError, ValueError, TypeError, ZeroDivisionError, ArithmeticError) as exc:
            return False, f'the slip could not be worked out ({type(exc).__name__}: {exc})'
    else:
        ms = typed_rule_values(note_id, family, inputs)
        if ms is None:
            return False, f'no slip is defined for {note_id!r} on family {family!r}'
    if not ms:
        return False, 'the slip gives no value for these inputs'
    key_dp = key.dp if key.kind == 'num' and key.value is not None and key.dp >= 0 else None
    if any(matches(opt, m, key_dp) for m in ms):
        return True, ''
    shown = [m.x if isinstance(m, Val) else m.why for m in ms][:4]
    return False, f'{text!r} is not what the slip gives ({[str(v) for v in shown]})'


def typed_rule_values(note_id, family, inputs):
    """Values of the typed-answer rules whose id or message is ``note_id`` for this family (None when there are none)."""
    from generators.shared import misconception_topics as T
    rules = [r for r in T.RULES if (r.id == note_id or r.message == note_id) and family in r.families]
    if not rules:
        return None
    out = []
    for r in rules:
        try:
            out.extend(Val(F(v)) for v in r.slip(inputs, 1) if v is not None)
        except (KeyError, ValueError, TypeError, ZeroDivisionError, ArithmeticError):
            continue
    return out


# ---------------------------------------------------------------------------------------------
# Slips
# ---------------------------------------------------------------------------------------------

SLIPS: dict = {}


def slip(note_id, *families):
    def deco(fn):
        for fam in families:
            SLIPS[(note_id, fam)] = fn
        return fn
    return deco


def vals(*xs, unit=None):
    return [Val(F(x), unit) for x in xs]


def _expr_numbers(expr, pattern):
    m = re.fullmatch(pattern, str(expr).replace('−', '-').strip())
    if not m:
        raise ValueError(f'unexpected expression {expr!r}')
    return [F(g) for g in m.groups()]


# bidmas -----------------------------------------------------------------------------------------

@slip('bidmas.left_to_right', 'arith')
def _left_to_right(i):
    a, b, c = _expr_numbers(i['expr'], r'(\d+) \+ (\d+) × (\d+)')
    return vals((a + b) * c)


@slip('mcq.power_one_term', 'arith')
def _power_one_term(i):
    a, b, p = _expr_numbers(i['expr'], r'\((\d+) \+ (\d+)\)\^(\d+)')
    return vals(a ** int(p) + b, a + b ** int(p))


# fractions, decimals, percentages -------------------------------------------------------------------

@slip('mcq.pct_as_amount', 'num_reverse_pct')
def _reverse_as_amount(i):
    return vals(F(i['final']) - F(i['pct']), F(i['final']) + F(i['pct']))


@slip('mcq.pct_as_amount', 'num_pct_of')
def _pct_of_as_amount(i):
    return vals(F(i['amount']) + F(i['pct']), F(i['amount']) - F(i['pct']))


@slip('mcq.pct_as_amount', 'num_pct_change')
def _change_as_amount(i):
    return vals(F(i['amount']) + F(i['pct']), F(i['amount']) - F(i['pct']))


@slip('mcq.fraction_remainder', 'num_frac_of')
def _remainder(i):
    amount, num, den = F(i['amount']), F(i['num']), F(i['den'])
    return vals(amount - amount * num / den)


@slip('fdp.bottom_only', 'num_frac_of')
def _bottom_only(i):
    return vals(F(i['amount']) / F(i['den']))


@slip('mcq.direction_text', 'fdp_pct_change_text')
def _direction(i):
    orig, new = F(i['original']), F(i['new'])
    pct = abs(new - orig) / orig * 100
    word = 'decrease' if new > orig else 'increase'
    shown = f'{float(pct):g}% {word}'
    return [Pred(lambda o: o.raw == shown, shown)]


@slip('gen.as_percentage', 'fdp_decimal_to_pct')
def _as_percentage(i):
    return vals(F(i['x']))


@slip('gen.pow10', 'fdp_decimal_to_pct')
def _pct_pow10(i):
    pct = F(i['x']) * 100
    return vals(pct / 10, pct * 10)


@slip('gen.pow10', 'quotient')
def _quotient_pow10(i):
    return vals(F(i['a']) / F(i['b']) / 10)


@slip('gen.pow10', 'product')
def _product_pow10(i):
    return vals(F(i['a']) * F(i['b']) * 10)


@slip('op.multiplied_for_quotient', 'quotient')
def _multiplied_for_quotient(i):
    return vals(F(i['a']) * F(i['b']))


@slip('op.divided_for_product', 'product')
def _divided_for_product(i):
    return vals(F(i['a']) / F(i['b']), F(i['b']) / F(i['a']))


def _bounds_interval(i):
    n, unit = F(i['value']), F(i['unit'])
    return n, unit


def _interval_pred(lo, lo_op, hi_op, hi, why):
    return Pred(lambda o: o.kind == 'interval' and o.parts == (lo, lo_op, hi_op, hi), why)


@slip('mcq.bounds_truncated', 'num_error_interval_text')
def _bounds_truncated(i):
    n, unit = _bounds_interval(i)
    # the value taken as the lower bound (cutting off), whichever unit of accuracy the question names
    return [_interval_pred(n, '≤', '<', n + unit, 'value as lower bound')]


@slip('mcq.bounds_signs', 'num_error_interval_text')
def _bounds_signs(i):
    n, unit = _bounds_interval(i)
    return [_interval_pred(n - unit / 2, '<', '≤', n + unit / 2, 'signs the other way round')]


@slip('mcq.bounds_full_unit', 'num_error_interval_text')
def _bounds_full_unit(i):
    n, unit = _bounds_interval(i)
    return [_interval_pred(n - unit, '≤', '<', n + unit, 'a whole unit each side')]


@slip('mcq.bounds_wrong_unit', 'num_error_interval_text')
def _bounds_wrong_unit(i):
    n, unit = _bounds_interval(i)
    return [_interval_pred(n - unit / 20, '≤', '<', n + unit / 20, 'half of a tenth of the unit')]


# mensuration, pythagoras, trigonometry ----------------------------------------------------------------

PI_314 = Fraction(314, 100)


@slip('mens.circumference_formula', 'mens_circle_area_314')
def _circle_uses_circumference(i):
    return vals(2 * PI_314 * F(i['r']))


@slip('mens.not_squared', 'mens_circle_area_314')
def _circle_not_squared(i):
    return vals(PI_314 * F(i['r']))


@slip('mcq.circle_pi_missing', 'mens_circle_area_314')
def _circle_pi_missing(i):
    return vals(F(i['r']) ** 2)


@slip('mcq.trapezium_one_side', 'mens_trapezium')
def _trapezium_one_side(i):
    return vals(F(i['a']) * F(i['h']), F(i['b']) * F(i['h']))


@slip('mens.full_rectangle', 'mens_trapezium')
def _trapezium_full(i):
    return vals((F(i['a']) + F(i['b'])) * F(i['h']))


@slip('pyth.sides_not_squares', 'pyth_hyp')
def _hyp_sides(i):
    a, b = F(i['a']), F(i['b'])
    return vals(a + b, abs(a - b))


@slip('pyth.sides_not_squares', 'pyth_leg')
def _leg_sides(i):
    c, a = F(i['c']), F(i['a'])
    return vals(c - a, c + a)


def _sin_cos_tan(angle):
    d = math.radians(float(angle))
    return {'sin': math.sin(d), 'cos': math.cos(d), 'tan': math.tan(d)}


@slip('trig.wrong_ratio', 'trig_side')
def _wrong_ratio(i):
    # the side is known adjacent and the unknown opposite; the right ratio is tan, so sin and cos (either way up) are the slips
    known, angle = F(i['known']), i['angle']
    f = _sin_cos_tan(angle)
    right = 'tan' if (i['known_kind'], i['find_kind']) in (('adj', 'opp'), ('opp', 'adj')) else None
    out = []
    for name in ('sin', 'cos', 'tan'):
        if name == right:
            continue
        r = Fraction(round(f[name], 10)).limit_denominator(10 ** 10)
        out.append(Val(known * r))
        if r:
            out.append(Val(known / r))
    return out


# number -----------------------------------------------------------------------------------------------

@slip('mcq.digit_not_value', 'num_digit_value')
def _digit_not_value(i):
    n, col = int(F(i['n'])), int(F(i['column']))
    return vals((n // col) % 10)


@slip('mcq.wrong_column', 'num_digit_value')
def _wrong_column(i):
    n, col = int(F(i['n'])), int(F(i['column']))
    digit = (n // col) % 10
    return vals(*(digit * c for c in (1, 10, 100, 1000, 10000) if c != col and c != 1))


@slip('gen.accuracy', 'num_round_dp')
def _round_more_places(i):
    n, dp = F(i['n']), int(i['dp'])
    return vals(half_up(n, dp + 1), half_up(n, dp + 2))


@slip('mcq.round_dropped', 'num_round_dp')
def _round_dropped(i):
    return vals(math.floor(F(i['n'])))


@slip('gen.accuracy', 'num_round_sf')
def _round_sf_more(i):
    n = F(i['n'])
    return vals(half_up(n, -1), half_up(n, -2))


@slip('mcq.round_place', 'num_round_sf')
def _round_sf_place(i):
    n = F(i['n'])
    return vals(half_up(n, -3), half_up(n, -4))


@slip('mcq.digits_cut', 'num_round_sf')
def _digits_cut(i):
    return vals(int(str(int(F(i['n'])))[:int(i['sf'])]))


@slip('mcq.pct_of_inverted', 'num_pct_of')
def _pct_of_inverted(i):
    return vals(F(i['pct']) / F(i['amount']) * 100)


@slip('pct.change_not_applied', 'num_pct_change')
def _change_only(i):
    return vals(F(i['amount']) * F(i['pct']) / 100)


@slip('pct.opposite', 'num_pct_change')
def _change_opposite(i):
    sign = 1 if i['sign'] == 'up' else -1
    return vals(F(i['amount']) * (1 - sign * F(i['pct']) / 100))


def _true_standard_value(family, i):
    if family == 'num_to_standard_form':
        return F(i['n'])
    if family == 'num_sf_product':
        return F(i['a']) * Fraction(10) ** int(i['p']) * F(i['b']) * Fraction(10) ** int(i['q'])
    raise ValueError(family)


def _std_pred(fn, why):
    return Pred(lambda o: o.kind == 'std' and fn(o.parts[0], o.parts[1], o.value), why)


def _register_standard_form():
    for fam in ('num_to_standard_form', 'num_sf_product'):
        def power_off(i, fam=fam):
            v = _true_standard_value(fam, i)
            return [_std_pred(lambda front, power, value: 1 <= front < 10 and value in (v / 10, v * 10), 'power one out')]

        def front_number(i, fam=fam):
            v = _true_standard_value(fam, i)
            return [_std_pred(lambda front, power, value: not (1 <= front < 10) and value == v, 'right value, front number not 1 to 10')]

        SLIPS[('mcq.sf_power_off', fam)] = power_off
        SLIPS[('mcq.sf_front_number', fam)] = front_number


_register_standard_form()


@slip('mcq.index_mult', 'num_sf_product')
def _sf_multiplied_powers(i):
    v = _true_standard_value('num_sf_product', i)
    front, power = v, 0
    while front >= 10:
        front, power = front / 10, power + 1
    while 0 < front < 1:
        front, power = front * 10, power - 1
    wrong = front * Fraction(10) ** (int(i['p']) * int(i['q']))
    return [Val(wrong)]


@slip('idx.power_sign_ignored', 'num_from_standard_form')
def _sign_ignored_sf(i):
    return vals(F(i['coef']) * Fraction(10) ** abs(int(i['power'])))


@slip('gen.pow10', 'num_from_standard_form')
def _sf_place_off(i):
    return vals(F(i['coef']) * Fraction(10) ** (int(i['power']) + 1))


@slip('mcq.power_as_divisor', 'num_from_standard_form')
def _power_as_divisor(i):
    return vals(F(i['coef']) / abs(int(i['power'])))


def _pow_pred(fn, why):
    return Pred(lambda o: o.kind == 'pow' and fn(*o.parts), why)


@slip('mcq.index_mult', 'num_index_mult')
def _index_mult(i):
    base, a, b = F(i['base']), int(i['a']), int(i['b'])
    return [_pow_pred(lambda bs, ex: bs == base and ex in (a * b, a - b), 'indices multiplied or subtracted')]


@slip('mcq.index_base_changed', 'num_index_mult')
def _index_base_changed(i):
    base, a, b = F(i['base']), int(i['a']), int(i['b'])
    return [_pow_pred(lambda bs, ex: bs == base * base and ex == a + b, 'bases multiplied')]


@slip('mcq.index_div', 'num_index_div')
def _index_div(i):
    base, a, b = F(i['base']), int(i['a']), int(i['b'])
    return [_pow_pred(lambda bs, ex: bs == base and ex in (a + b, a * b), 'indices added or multiplied')]


@slip('idx.power_sign_ignored', 'num_neg_index')
def _neg_index_sign(i):
    return vals(F(i['base']) ** int(i['power']))


@slip('idx.negative_power', 'num_neg_index')
def _neg_index_negative(i):
    b, p = F(i['base']), int(i['power'])
    return vals(-(b ** p), -(1 / b ** p))


@slip('mcq.base_times_power', 'num_neg_index')
def _base_times_power(i):
    return vals(1 / (F(i['base']) * int(i['power'])))


@slip('pct.error_wrong_base', 'num_pct_error')
def _error_wrong_base(i):
    e, a = F(i['estimate']), F(i['actual'])
    return vals(abs(a - e) / e * 100)


@slip('pct.error_not_compared', 'num_pct_error')
def _error_not_compared(i):
    return vals(abs(F(i['actual']) - F(i['estimate'])))


@slip('mcq.pct_error_ratio', 'num_pct_error')
def _error_ratio(i):
    return vals(F(i['actual']) / F(i['estimate']) * 100)


@slip('mcq.hcf_cofactor', 'num_hcf')
def _hcf_cofactor(i):
    # only when the cofactor does not divide the other number; otherwise it is a smaller common factor (next slip)
    a, b = int(F(i['a'])), int(F(i['b']))
    co = a // math.gcd(a, b)
    return vals(co) if b % co else []


@slip('mcq.hcf_not_highest', 'num_hcf')
def _hcf_not_highest(i):
    a, b = int(F(i['a'])), int(F(i['b']))
    g = math.gcd(a, b)
    return [Pred(lambda o: o.kind == 'num' and o.value is not None and o.value.denominator == 1
                 and 1 < o.value < g and a % int(o.value) == 0 and b % int(o.value) == 0, 'a common factor below the HCF')]


@slip('mcq.hcf_for_lcm', 'num_hcf')
def _hcf_for_lcm(i):
    a, b = int(F(i['a'])), int(F(i['b']))
    return vals(a * b // math.gcd(a, b))


@slip('pct.same_each_year', 'num_compound')
def _simple_interest(i):
    p, r, y = F(i['principal']), F(i['rate']), int(i['years'])
    sign = 1 if i.get('sign', 'up') == 'up' else -1
    return vals(p * (1 + sign * r / 100 * y))


@slip('pct.years_missed', 'num_compound')
def _wrong_years(i):
    p, r, y = F(i['principal']), F(i['rate']), int(i['years'])
    sign = 1 if i.get('sign', 'up') == 'up' else -1
    m = 1 + sign * r / 100
    return vals(p * m ** (y - 1), p * m ** (y + 1))


# ratio and proportion ---------------------------------------------------------------------------------

def _ratio_pred(fn, why):
    return Pred(lambda o: o.kind == 'ratio' and fn(*o.parts), why)


@slip('mcq.ratio_unsimplified', 'ratio_simplify')
def _ratio_unsimplified(i):
    a, b = int(F(i['a'])), int(F(i['b']))
    return [_ratio_pred(lambda x, y: (x, y) == (a, b), 'the ratio as given')]


@slip('mcq.ratio_one_side', 'ratio_simplify')
def _ratio_one_side(i):
    a, b = int(F(i['a'])), int(F(i['b']))
    g = math.gcd(a, b)
    sa, sb = a // g, b // g
    return [_ratio_pred(lambda x, y: (x, y) in ((a, sb), (sa, b)), 'one part divided and not the other')]


def _parts_of(i):
    parts = i['parts']
    return [int(F(p)) for p in parts]


@slip('mcq.ratio_smaller_share', 'ratio_larger_share')
def _smaller_share(i):
    parts, total = _parts_of(i), F(i['total'])
    return vals(total / sum(parts) * min(parts), unit='£')


@slip('mcq.ratio_one_part', 'ratio_larger_share', 'ratio_share_one')
def _one_part(i):
    parts, total = _parts_of(i), F(i['total'])
    return vals(total / sum(parts))


@slip('mcq.ratio_equal_split', 'ratio_larger_share')
def _equal_split_money(i):
    # an equal split between the two people (exactly half: an odd total has no whole-pound half)
    return vals(F(i['total']) / 2, unit='£') if len(_parts_of(i)) == 2 else []


@slip('mcq.ratio_equal_split', 'ratio_share_one')
def _equal_split(i):
    return vals(F(i['total']) / 2) if len(_parts_of(i)) == 2 else []


@slip('ratio.parts_swapped', 'ratio_share_one')
def _other_part(i):
    parts, total, which = _parts_of(i), F(i['total']), int(i['which'])
    one = total / sum(parts)
    return vals(*(one * p for k, p in enumerate(parts) if k != which))


@slip('mcq.ratio_part_as_amount', 'ratio_share_one')
def _part_as_amount(i):
    parts, which = _parts_of(i), int(i['which'])
    return vals(parts[which])


@slip('mcq.unitary_given_total', 'ratio_unitary')
def _unitary_given_total(i):
    return vals(F(i['total']), unit='£')


@slip('ratio.unit_only', 'ratio_unitary')
def _unitary_one(i):
    return vals(F(i['total']) / F(i['n1']), unit='£')


@slip('mcq.map_km_factor', 'ratio_map_scale')
def _map_km_factor(i):
    return vals(F(i['cm']) * F(i['scale']) / 1000, unit='km')


@slip('mcq.map_scale_ignored', 'ratio_map_scale')
def _map_scale_ignored(i):
    return vals(F(i['cm']), unit='km')


@slip('ratio.direct_for_inverse', 'prop_inverse')
def _inverse_as_direct(i):
    a, b, c = F(i['a']), F(i['b']), F(i['c'])
    return vals(b * c / a, unit='hours')


@slip('mcq.work_not_shared', 'prop_inverse')
def _work_not_shared(i):
    return vals(F(i['a']) * F(i['b']), unit='hours')


# ---------------------------------------------------------------------------------------------
# Fixed bank questions (BANK_WHY rows)
# ---------------------------------------------------------------------------------------------

def eval_expr(expr):
    """Exact value (Fraction) of a small arithmetic expression: numbers, + - * / **, unary minus, int() (truncation)."""
    import ast
    import operator

    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Pow: operator.pow}

    def go(node):
        if isinstance(node, ast.Expression):
            return go(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return F(repr(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -go(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            a, b = go(node.left), go(node.right)
            if isinstance(node.op, ast.Pow):
                if b.denominator != 1:
                    raise ValueError('fractional power')
                return a ** int(b)
            return ops[type(node.op)](a, b)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'int'
                and len(node.args) == 1):
            return F(math.trunc(go(node.args[0])))
        raise ValueError(f'unsupported expression {expr!r}')

    return go(ast.parse(expr, mode='eval'))


def verify_bank_row(row, items):
    """(ok, why) for one ``BANK_WHY`` row against the bank items (dicts with q, opts, ans): the question exists with the
    stated key, the distractor is one of its options, and (when the row gives the slip as an expression) the distractor
    is what the expression gives, to the places it prints."""
    note_id, question, key_text, option, expr = row
    found = False
    for item in items:
        if item.get('q') != question:
            continue
        opts = {str(o)[0]: str(o)[3:] for o in item.get('opts') or []}
        if opts.get(str(item.get('ans', '')).strip().upper()[:1]) != key_text:
            continue
        if option in opts.values() and option != key_text:
            found = True
            break
    if not found:
        return False, 'no bank item has this question, this key and this distractor'
    if expr is None:
        return True, ''
    opt = read(re.sub(r'[°²]', '', option))        # degrees and square units: Phase 5 angle and area rows
    if opt.kind != 'num' or opt.value is None:
        return False, 'the distractor is not a plain number, so an expression cannot check it'
    try:
        got = eval_expr(expr)
    except (ValueError, ZeroDivisionError, SyntaxError) as exc:
        return False, f'the expression does not work out ({exc})'
    if half_up(got, opt.dp) != opt.value:
        return False, f'{expr} gives {float(got):g}, not {option}'
    return True, ''


def bank_row_pin(row, note_text):
    """A short hash of a reviewed row and the words of its note: change either and the pin in the smoke must be re-reviewed."""
    import hashlib
    return hashlib.sha1('\x1f'.join([*(str(x) for x in row), note_text]).encode()).hexdigest()[:10]
