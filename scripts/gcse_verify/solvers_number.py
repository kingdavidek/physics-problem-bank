"""Solvers for number, BIDMAS, multiples and factors, decimals, FDP and ratio/proportion.

Independence rule: this module recomputes answers from first principles. It must not import
any generator module or helper (checked by the test); only the standard library and sympy.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from .core import (AnyOf, Approx, Cannot, Pick, PickSet, Pw, Ratio, SF, Surd, Verdict,  # noqa: F401
                   apply_spec, parse_sf, sqrt_atom)
from .registry import fr, solver


def sf_norm(value):
    """Standard form (coefficient, power) of a non-zero rational, coefficient in [1, 10)."""
    v = fr(value)
    if v == 0:
        raise Cannot('zero has no standard form')
    sign = -1 if v < 0 else 1
    v = abs(v)
    power = 0
    while v >= 10:
        v /= 10
        power += 1
    while v < 1:
        v *= 10
        power -= 1
    return SF(sign * v, power)


def _pf(n):
    out, d = {}, 2
    n = int(n)
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


_SUP = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}


def _read_pf_text(text):
    """{prime: exponent} from text such as '2^3 × 3^2', '2³ × 3²' or '2 × 2 × 3' (None if unreadable)."""
    out = {}
    for part in re.split(r'\s*[×x*·]\s*', text.strip()):
        part = part.strip()
        m = re.fullmatch(r'(\d+)\s*(?:\^\s*(\d+)|([⁰¹²³⁴⁵⁶⁷⁸⁹]+))?', part)
        if not m:
            return None
        base = int(m.group(1))
        if m.group(2):
            exp = int(m.group(2))
        elif m.group(3):
            exp = int(''.join(_SUP[c] for c in m.group(3)))
        else:
            exp = 1
        out[base] = out.get(base, 0) + exp
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Number: place value, rounding, directed numbers, powers
# ─────────────────────────────────────────────────────────────────────────────

@solver('num_place_value_digit')
def _num_place_value_digit(number, digit):
    s = str(int(number))
    if s.count(str(int(digit))) != 1:
        raise Cannot('digit not unique in the number')
    pos = len(s) - 1 - s.index(str(int(digit)))
    return [int(digit) * 10 ** pos]


@solver('num_digit_value')
def _num_digit_value(n, column):
    return [(int(n) // int(column)) % 10 * int(column)]


@solver('num_decimal_place')
def _num_decimal_place(number, position):
    frac_digits = str(number).split('.')[1]
    idx = {'tenths': 0, 'hundredths': 1, 'thousandths': 2}[position]
    return [int(frac_digits[idx])]


@solver('num_compare')
def _num_compare(a, b):
    want = '>' if fr(a) > fr(b) else '<'
    return [Pick(lambda t: t.strip() == want, f'option is "{want}"')]


@solver('num_order')
def _num_order(values):
    return [fr(v) for v in sorted(values, key=fr)]


@solver('num_round_unit')
def _num_round_unit(n, unit):
    return [apply_spec(fr(n), ('unit', fr(unit)))]


@solver('num_round_dp')
def _num_round_dp(n, dp):
    return [apply_spec(fr(n), ('dp', int(dp)))]


@solver('num_round_sf')
def _num_round_sf(n, sf):
    return [apply_spec(fr(n), ('sf', int(sf)))]


@solver('num_directed')
def _num_directed(a, op, b):
    return [fr(a) + fr(b) if op == '+' else fr(a) - fr(b)]


@solver('num_scale_pow10')
def _num_scale_pow10(n, op, p):
    return [fr(n) * fr(p) if op == 'multiply' else fr(n) / fr(p)]


@solver('num_power')
def _num_power(base, exp):
    return [fr(base) ** int(exp)]


@solver('num_pct_of')
def _num_pct_of(pct, amount):
    return [fr(amount) * fr(pct) / 100]


@solver('num_frac_of')
def _num_frac_of(num, den, amount):
    return [fr(amount) * fr(num) / fr(den)]


@solver('num_estimate_product_1sf')
def _num_estimate_product_1sf(a, b):
    return [apply_spec(fr(a), ('sf', 1)) * apply_spec(fr(b), ('sf', 1))]


@solver('num_estimate_fraction_1sf')
def _num_estimate_fraction_1sf(a, b, c):
    return [apply_spec(fr(a), ('sf', 1)) * apply_spec(fr(b), ('sf', 1)) / apply_spec(fr(c), ('sf', 1))]


@solver('num_to_standard_form')
def _num_to_standard_form(n):
    return [sf_norm(n)]


@solver('num_from_standard_form')
def _num_from_standard_form(coef, power):
    return [fr(coef) * Fraction(10) ** int(power)]


@solver('num_sf_product')
def _num_sf_product(a, p, b, q):
    return [sf_norm(fr(a) * fr(b) * Fraction(10) ** (int(p) + int(q)))]


@solver('num_sf_quotient')
def _num_sf_quotient(a, p, b, q):
    return [sf_norm(fr(a) / fr(b) * Fraction(10) ** (int(p) - int(q)))]


@solver('num_sf_mixed')
def _num_sf_mixed(a, p, b, q, c, r):
    return [sf_norm(fr(a) * fr(b) / fr(c) * Fraction(10) ** (int(p) + int(q) - int(r)))]


@solver('num_sf_total')
def _num_sf_total(pop, count):
    return [sf_norm(fr(pop) * fr(count) * 10 ** 6)]


@solver('num_sf_difference')
def _num_sf_difference(c1, p1, c2, p2):
    return [sf_norm(fr(c1) * Fraction(10) ** int(p1) - fr(c2) * Fraction(10) ** int(p2))]


@solver('num_index_mult')
def _num_index_mult(base, a, b):
    return [Pw(int(base), int(a) + int(b))]


@solver('num_index_div')
def _num_index_div(base, a, b):
    return [Pw(int(base), int(a) - int(b))]


@solver('num_index_pow')
def _num_index_pow(base, a, b):
    return [Pw(int(base), int(a) * int(b))]


@solver('num_frac_index')
def _num_frac_index(base, num, den):
    b, n, d = int(base), int(num), int(den)
    root = round(b ** (1 / d))
    for cand in (root - 1, root, root + 1):
        if cand ** d == b:
            return [Fraction(cand) ** n]
    raise Cannot('base is not a perfect power')


@solver('num_neg_index')
def _num_neg_index(base, power):
    return [Fraction(1, int(base) ** int(power))]


@solver('num_zero_neg_index')
def _num_zero_neg_index(a, b):
    return [Fraction(1, int(b) ** 2)]


def read_recurring(text):
    """Exact value of a displayed recurring decimal such as 0.4666…, 0.454545… or 0.285714285714…."""
    t = str(text).strip()
    if re.fullmatch(r'\d+\.\d+', t):          # a terminating decimal is shown as itself
        return Fraction(t)
    m = re.fullmatch(r'0\.(\d+)…', t)
    if not m:
        raise Cannot(f'cannot read the recurring decimal {text!r}')
    digits = m.group(1)
    for w in range(1, len(digits) // 2 + 1):
        for p in range(0, len(digits) - 2 * w + 1):
            tail = digits[p:]
            if len(tail) % w == 0 and tail == tail[:w] * (len(tail) // w):
                pre, block = digits[:p], tail[:w]
                num = int(pre + block) - (int(pre) if pre else 0)
                return Fraction(num, (10 ** w - 1) * 10 ** p)
    raise Cannot(f'no repeating block is visible in {text!r}')


@solver('num_recurring_text')
def _num_recurring_text(dec):
    return [read_recurring(dec)]


@solver('dec_recurring_display')
def _dec_recurring_display(num, den, dec):
    """Check that a displayed recurring decimal really is num/den (the question has no typed key)."""
    got = read_recurring(dec)
    ok = got == Fraction(int(num), int(den))
    return [Verdict(ok, f'{dec} reads as {got} but the question is about {num}/{den}')]


@solver('num_between_sqrt')
def _num_between_sqrt(n):
    r = math.isqrt(int(n))
    return [r, r + 1]


@solver('num_sqrt_tenths')
def _num_sqrt_tenths(n):
    lo = Fraction(math.isqrt(int(n) * 100), 10)
    return [lo, lo + Fraction(1, 10)]


@solver('num_find_index')
def _num_find_index(base, value):
    b, v, n = int(base), int(value), 0
    cur = 1
    while cur < v:
        cur *= b
        n += 1
    if cur != v:
        raise Cannot('value is not a power of the base')
    return [n]


@solver('num_hcf')
def _num_hcf(a, b):
    return [math.gcd(int(a), int(b))]


@solver('num_lcm')
def _num_lcm(a, b):
    return [math.lcm(int(a), int(b))]


@solver('num_hcf_lcm')
def _num_hcf_lcm(a, b):
    return [math.gcd(int(a), int(b)), math.lcm(int(a), int(b))]


@solver('num_prime_factors')
def _num_prime_factors(n):
    want = _pf(n)
    return [Pick(lambda t: _read_pf_text(t) == want, f'product of prime factors of {n}')]


# ── percentages and money ────────────────────────────────────────────────────

def _sgn(word):
    if word not in ('up', 'down'):
        raise Cannot(f"sign must be 'up' or 'down', got {word!r}")
    return 1 if word == 'up' else -1


@solver('num_pct_change')
def _num_pct_change(amount, pct, sign):
    return [fr(amount) * (1 + _sgn(sign) * fr(pct) / 100)]


@solver('num_reverse_pct')
def _num_reverse_pct(final, pct, sign):
    return [fr(final) / (1 + _sgn(sign) * fr(pct) / 100)]


@solver('num_two_pct_changes')
def _num_two_pct_changes(amount, pct1, pct2):
    return [_money(fr(amount) * (1 + fr(pct1) / 100) * (1 - fr(pct2) / 100))]


@solver('num_compound')
def _num_compound(principal, rate, years, sign):
    return [fr(principal) * (1 + _sgn(sign) * fr(rate) / 100) ** int(years)]


@solver('num_reverse_compound')
def _num_reverse_compound(final, rate, years):
    return [fr(final) / (1 + fr(rate) / 100) ** int(years)]


@solver('num_vat_inclusive')
def _num_vat_inclusive(price, vat):
    return [fr(price) * (1 + fr(vat) / 100)]


@solver('num_product_sf')
def _num_product_sf(a, b):
    return [fr(a) * fr(b)]


@solver('num_share_ratio')
def _num_share_ratio(total, r1, r2):
    t = fr(r1) + fr(r2)
    return [fr(total) * fr(r1) / t, fr(total) * fr(r2) / t]


@solver('num_pct_error')
def _num_pct_error(estimate, actual):
    return [abs(fr(estimate) - fr(actual)) / fr(actual) * 100]


# ── bounds ───────────────────────────────────────────────────────────────────

@solver('num_error_interval')
def _num_error_interval(value, unit):
    half = fr(unit) / 2
    return [fr(value) - half, fr(value) + half]


@solver('num_error_interval_text')
def _num_error_interval_text(value, unit):
    lo, hi = fr(value) - fr(unit) / 2, fr(value) + fr(unit) / 2

    def test(text):
        m = re.fullmatch(r'\s*(-?[\d.]+)\s*≤\s*x\s*<\s*(-?[\d.]+)\s*', text)
        return bool(m) and Fraction(m.group(1)) == lo and Fraction(m.group(2)) == hi
    return [Pick(test, f'{lo} ≤ x < {hi}')]


@solver('num_bounds_area')
def _num_bounds_area(length, width, unit):
    h = fr(unit) / 2
    return [(fr(length) - h) * (fr(width) - h), (fr(length) + h) * (fr(width) + h)]


@solver('num_bounds_product')
def _num_bounds_product(a, b, unit):
    h = fr(unit) / 2
    return [(fr(a) - h) * (fr(b) - h), (fr(a) + h) * (fr(b) + h)]


@solver('num_bounds_density')
def _num_bounds_density(mass, volume, unit):
    h = fr(unit) / 2
    return [(fr(mass) - h) / (fr(volume) + h), (fr(mass) + h) / (fr(volume) - h)]


@solver('num_bounds_speed')
def _num_bounds_speed(dist, hours, dist_unit, time_unit):
    hd, ht = fr(dist_unit) / 2, fr(time_unit) / 2
    return [(fr(dist) - hd) / (fr(hours) + ht), (fr(dist) + hd) / (fr(hours) - ht)]


# ── comparisons ──────────────────────────────────────────────────────────────

@solver('num_compare_sf')
def _num_compare_sf(c1, p1, c2, p2):
    v1, v2 = fr(c1) * Fraction(10) ** int(p1), fr(c2) * Fraction(10) ** int(p2)
    if v1 == v2:
        raise Cannot('values equal')
    big = max(v1, v2)

    def test(text):
        sf = parse_sf(text)
        return sf is not None and sf.coef * Fraction(10) ** sf.power == big
    return [Pick(test, 'the larger of the two values')]


@solver('num_best_value')
def _num_best_value(items1, price1, items2, price2):
    u1, u2 = fr(price1) / fr(items1), fr(price2) / fr(items2)
    if u1 == u2:
        raise Cannot('equal unit prices: no better value')
    word = 'pack a' if u1 < u2 else 'pack b'
    return [Pick(lambda t: t.strip().lower().startswith(word), f'option starts with "{word}"')]


# ─────────────────────────────────────────────────────────────────────────────
# Ratio and proportion
# ─────────────────────────────────────────────────────────────────────────────

def _shares(total, parts):
    s = sum(fr(p) for p in parts)
    return [fr(total) * fr(p) / s for p in parts]


@solver('ratio_simplify')
def _ratio_simplify(a, b):
    g = math.gcd(int(a), int(b))
    return [Ratio(int(a) // g, int(b) // g)]


@solver('ratio_equivalent')
def _ratio_equivalent(a, b, k):
    return [Ratio(int(a) * int(k), int(b) * int(k))]


@solver('ratio_share')
def _ratio_share(total, parts):
    return _shares(total, parts)


@solver('ratio_larger_share')
def _ratio_larger_share(total, parts):
    shares = _shares(total, parts)
    if shares.count(max(shares)) > 1:
        return [Verdict(False, f'asks for the larger share but the ratio {":".join(str(p) for p in parts)} has equal parts')]
    return [max(shares)]


def _more(big, small, what):
    """Guard for "how much more X than Y" parts: the difference has to be positive."""
    if big <= small:
        return Verdict(False, f'asks how much more {what}, but the first quantity is {big} and the second {small}')
    return None


@solver('ratio_share_one')
def _ratio_share_one(total, parts, which):
    return [_shares(total, parts)[int(which)]]


@solver('ratio_part_fraction')
def _ratio_part_fraction(parts, which):
    return [fr(parts[int(which)]) / sum(fr(p) for p in parts)]


@solver('ratio_find_missing')
def _ratio_find_missing(a, b, known):
    return [fr(known) * fr(b) / fr(a)]


@solver('ratio_unitary')
def _ratio_unitary(n1, total, n2):
    return [fr(total) / fr(n1) * fr(n2)]


@solver('prop_scale')
def _prop_scale(q1, n1, n2):
    """Direct proportion: q1 for n1 people, so quantity for n2 is q1 * n2 / n1."""
    return [fr(q1) * fr(n2) / fr(n1)]


@solver('ratio_map_scale')
def _ratio_map_scale(scale, cm, to):
    real_cm = fr(cm) * fr(scale)
    return [real_cm / 100 if to == 'm' else real_cm / 100000]


@solver('prop_inverse')
def _prop_inverse(a, b, c):
    """Inverse proportion: a * b is constant, so the new value is a * b / c."""
    return [fr(a) * fr(b) / fr(c)]


@solver('prop_direct')
def _prop_direct(x1, y1, x2):
    return [fr(y1) / fr(x1) * fr(x2)]


@solver('ratio_units')
def _ratio_units(a_m, b_cm):
    x, y = int(a_m) * 100, int(b_cm)
    g = math.gcd(x, y)
    return [Ratio(x // g, y // g)]


@solver('quotient')
def _quotient(a, b):
    return [fr(a) / fr(b)]


@solver('ratio_share_diff')
def _ratio_share_diff(total, parts):
    s = _shares(total, parts)
    bad = _more(s[0], s[1], 'of the first ingredient than the second')
    return [bad] if bad else [s[0], s[1], s[0] - s[1]]


@solver('ratio_prize')
def _ratio_prize(total, parts):
    s = _shares(total, parts)
    bad = _more(s[0], s[2], 'first place gets than third')
    return [bad] if bad else [fr(total) / sum(fr(p) for p in parts), s[0], s[0] - s[2]]


@solver('ratio_hike')
def _ratio_hike(scale, cm1, cm2):
    m1, m2 = fr(cm1) * fr(scale) / 100, fr(cm2) * fr(scale) / 100
    return [m1, m2, (m1 + m2) / 1000]


@solver('ratio_garden')
def _ratio_garden(total, parts):
    s = _shares(total, parts)
    bad = _more(s[0], s[2], 'soil than sand')
    return [bad] if bad else [s[1], s[2], s[0] - s[2]]


@solver('ratio_merge')
def _ratio_merge(students_a, a_parts, students_b, b_parts):
    ga = fr(students_a) * a_parts[1] / sum(a_parts)
    bb = fr(students_b) * b_parts[0] / sum(b_parts)
    boys = fr(students_a) * a_parts[0] / sum(a_parts) + bb
    girls = ga + fr(students_b) * b_parts[1] / sum(b_parts)
    g = math.gcd(int(boys), int(girls))
    return [ga, bb, Ratio(int(boys) // g, int(girls) // g)]


@solver('ratio_holiday')
def _ratio_holiday(budget, parts, rate):
    s = _shares(budget, parts)
    return [s[1], s[2], s[0] * fr(rate)]


@solver('prop_plumbers')
def _prop_plumbers(w1, h1, w2, h3):
    work = fr(w1) * fr(h1)
    return [work, work / fr(w2), work / fr(h3)]


@solver('ratio_concert')
def _ratio_concert(total, parts, adult_price, child_price):
    s = _shares(total, parts)
    return [s[0], s[1], s[0] * fr(adult_price) + s[1] * fr(child_price)]


# ─────────────────────────────────────────────────────────────────────────────
# Arithmetic expressions (BIDMAS and decimals)
# ─────────────────────────────────────────────────────────────────────────────

_TOKEN = re.compile(r'\s*(?:(\d+(?:\.\d+)?)|(.))')
_SUPERSCRIPT = {'²': 2, '³': 3}


def eval_expression(text):
    """Evaluate +, -, ×, ÷, brackets and integer powers exactly (no eval): precedence and unary minus as in school."""
    toks = []
    for m in _TOKEN.finditer(text.replace('−', '-').replace('×', '*').replace('÷', '/')):
        if m.group(1):
            toks.append(('n', Fraction(m.group(1))))
        elif m.group(2).strip():
            toks.append(('o', m.group(2)))
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else (None, None)

    def take():
        t = peek()
        pos[0] += 1
        return t

    def expr():
        v = term()
        while peek() in (('o', '+'), ('o', '-')):
            op = take()[1]
            r = term()
            v = v + r if op == '+' else v - r
        return v

    def term():
        v = unary()
        while peek() in (('o', '*'), ('o', '/')):
            op = take()[1]
            r = unary()
            if op == '/':
                if r == 0:
                    raise Cannot('division by zero in the expression')
                v = v / r
            else:
                v = v * r
        return v

    def unary():
        if peek() == ('o', '-'):
            take()
            return -unary()
        if peek() == ('o', '+'):
            take()
            return unary()
        return power()

    def power():
        base = atom()
        while True:
            if peek() == ('o', '^'):
                take()
                neg = False
                if peek() == ('o', '-'):
                    take()
                    neg = True
                kind, val = take()
                if kind != 'n' or val.denominator != 1 or val > 12:
                    raise Cannot('unsupported exponent')
                e = -int(val) if neg else int(val)
                base = base ** e
            elif peek()[0] == 'o' and peek()[1] in _SUPERSCRIPT:
                base = base ** _SUPERSCRIPT[take()[1]]
            else:
                return base

    def atom():
        kind, val = take()
        if kind == 'n':
            return val
        if (kind, val) == ('o', '('):
            v = expr()
            if take() != ('o', ')'):
                raise Cannot('missing closing bracket')
            return v
        raise Cannot(f'unexpected token {val!r} in {text!r}')

    v = expr()
    if pos[0] != len(toks):
        raise Cannot(f'trailing text in expression {text!r}')
    return v


@solver('arith')
def _arith(expr):
    return [eval_expression(expr)]


@solver('product')
def _product(a, b):
    return [fr(a) * fr(b)]


@solver('num_estimate_product_whole')
def _num_estimate_product_whole(a, b):
    return [apply_spec(fr(a), ('unit', 1)) * apply_spec(fr(b), ('unit', 1))]


def _money(x):
    """A money answer: the exact value, accepted to the nearest penny (the universal convention for £)."""
    return Approx(fr(x), ('dp', 2))


# ── multiples and factors ────────────────────────────────────────────────────

@solver('mf_multiple')
def _mf_multiple(n, k):
    return [int(n) * int(k)]


@solver('mf_factor_of')
def _mf_factor_of(n):
    def test(text):
        t = text.strip()
        return t.isdigit() and int(n) % int(t) == 0
    return [Pick(test, f'a factor of {n}')]


@solver('mf_factor_pairs')
def _mf_factor_pairs(n):
    def test(text):
        m = re.fullmatch(r'\s*(\d+)\s*[×x]\s*(\d+)\s*', text)
        return bool(m) and int(m.group(1)) * int(m.group(2)) == int(n)
    return [PickSet(test, f'a factor pair of {n}')]


@solver('mf_is_prime')
def _mf_is_prime(n):
    n = int(n)
    prime = n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))
    return ['yes' if prime else 'no']


@solver('mf_buses')
def _mf_buses(a, b, start):
    h, m = [int(x) for x in str(start).split(':')]
    total = h * 60 + m + math.lcm(int(a), int(b))
    return [f'{total // 60}:{total % 60:02d}']


@solver('mf_common_factor_count')
def _mf_common_factor_count(a, b):
    g = math.gcd(int(a), int(b))
    return [sum(1 for d in range(1, g + 1) if g % d == 0)]


@solver('mf_divisibility')
def _mf_divisibility(rule, before, after):
    valid = [d for d in range(10) if int(f'{before}{d}{after}') % int(rule) == 0]
    if len(valid) == 10:
        return [Pick(lambda t: 'any digit' in t.lower(), 'any digit from 0 to 9')]
    return valid


@solver('mf_hcf3')
def _mf_hcf3(a, b, c):
    return [math.gcd(math.gcd(int(a), int(b)), int(c))]


@solver('mf_lcm3')
def _mf_lcm3(a, b, c):
    return [math.lcm(int(a), int(b), int(c))]


@solver('mf_other_number')
def _mf_other_number(hcf, lcm, known):
    return [fr(hcf) * fr(lcm) / fr(known)]


@solver('mf_primes_between')
def _mf_primes_between(lo, hi):
    return [n for n in range(int(lo) + 1, int(hi)) if n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))]


# ── decimals and FDP ─────────────────────────────────────────────────────────

@solver('fdp_decimal_to_pct')
def _fdp_decimal_to_pct(x):
    return [fr(x) * 100]


@solver('fdp_pct_to_decimal')
def _fdp_pct_to_decimal(pct):
    return [fr(pct) / 100]


@solver('fdp_decimal_to_fraction')
def _fdp_decimal_to_fraction(dec):
    return [fr(dec)]


@solver('fdp_fraction_to_pct')
def _fdp_fraction_to_pct(a, b):
    return [fr(a) / fr(b) * 100]


@solver('fdp_pct_to_fraction')
def _fdp_pct_to_fraction(pct):
    return [fr(pct) / 100]


@solver('fdp_dec_and_pct')
def _fdp_dec_and_pct(a, b):
    return [fr(a) / fr(b), fr(a) / fr(b) * 100]


@solver('fdp_pct_change')
def _fdp_pct_change(original, new):
    return [abs(fr(new) - fr(original)) / fr(original) * 100]


@solver('fdp_pct_change_text')
def _fdp_pct_change_text(original, new):
    change = (fr(new) - fr(original)) / fr(original) * 100
    word = 'increase' if change > 0 else 'decrease'
    shown = f'{abs(change).numerator}' if abs(change).denominator == 1 else f'{float(abs(change)):.4g}'
    return [f'{shown}% {word}']


@solver('fdp_profit_pct')
def _fdp_profit_pct(cost, selling):
    return [(fr(selling) - fr(cost)) / fr(cost) * 100]


@solver('fdp_fraction_not')
def _fdp_fraction_not(num, den, total):
    return [fr(total) - fr(total) * fr(num) / fr(den)]


@solver('fdp_reverse_two_step')
def _fdp_reverse_two_step(final, pct_up, pct_down):
    return [_money(fr(final) / ((1 + fr(pct_up) / 100) * (1 - fr(pct_down) / 100)))]


@solver('fdp_shop_discount')
def _fdp_shop_discount(unit, qty, discount_pct):
    return [_money(fr(unit) * fr(qty) * (1 - fr(discount_pct) / 100))]


@solver('dec_mean')
def _dec_mean(values):
    return [sum(fr(v) for v in values) / len(values)]


def _read_label(text):
    """Value of an ordering label such as '3/8', '0.4' or '37.5%'."""
    t = text.strip().replace('−', '-')
    pct = t.endswith('%')
    t = t.rstrip('%').strip()
    v = Fraction(t) if '/' in t else fr(t)
    return v / 100 if pct else v


@solver('order_values')
def _order_values(labels):
    ordered = sorted((_read_label(x), str(x).strip()) for x in labels)
    return [text for _, text in ordered]
