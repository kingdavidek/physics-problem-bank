"""Solvers for the Phase 3 batch C2 record families (docs/GCSE_MATHS_VARIETY.md section 23): the harder probability,
ratio, graphs and statistics kinds that replaced the last tier echoes.

Independence rule: each answer is recomputed from the numbers the pupil is shown, from first principles, with the
standard library and sympy only; no generator module is imported (checked by the test). The two drawn graphs are read
back from their SVG (``@diagram``): the marked points through the tick labels, and the line through them.
"""
from __future__ import annotations

import math
from fractions import Fraction

import sympy

from .core import Cannot, Ratio
from .registry import diagram, fr, solver
from .solvers_algebra import Ctx, judge
from .solvers_svg import elements, one_svg
from .solvers_variety_c import _axis, read_marks


def _tuple(_p, m, c):
    return judge(Ctx(_p, {}), 'tuple', [sympy.Rational(m.numerator, m.denominator), sympy.Rational(c.numerator, c.denominator)])


# ───────────────────────── probability ─────────────────────────

@solver('prob_counters_algebraic')
def _prob_counters_algebraic(r, p_num, p_den):
    r, p = fr(r), Fraction(int(p_num), int(p_den))
    # r (r - 1) / (n (n - 1)) = p  ->  n^2 - n - N = 0 with N = r (r - 1) / p
    big = r * (r - 1) / p
    if big.denominator != 1:
        raise Cannot('n(n - 1) is not a whole number')
    disc = 1 + 4 * int(big)
    root = math.isqrt(disc)
    if root * root != disc or (1 + root) % 2:
        raise Cannot('the total is not a whole number')
    n = Fraction((1 + root) // 2)
    if n <= r:
        raise Cannot('no room for another colour')
    return [n - r]


@solver('prob_independent_union')
def _prob_independent_union(pa, pb, ask):
    pa, pb = fr(pa), fr(pb)
    both = pa * pb
    if ask == 'union':
        return [pa + pb - both]
    if ask == 'exactly_one':
        return [pa + pb - 2 * both]
    raise Cannot(f'unknown ask {ask!r}')


@solver('prob_three_same')
def _prob_three_same(r, b):
    r, b = int(r), int(b)
    n = r + b
    if n < 3:
        raise Cannot('fewer than three counters')
    return [Fraction(r * (r - 1) * (r - 2) + b * (b - 1) * (b - 2), n * (n - 1) * (n - 2))]


@solver('prob_two_day')
def _prob_two_day(p1, p_given, p_not_given, ask):
    p1, pg, pn = fr(p1), fr(p_given), fr(p_not_given)
    first_only = p1 * (1 - pg)
    second_only = (1 - p1) * pn
    if ask == 'exactly_one':
        return [first_only + second_only]
    if ask == 'at_least_one':
        return [1 - (1 - p1) * (1 - pn)]
    raise Cannot(f'unknown ask {ask!r}')


@solver('prob_trials_needed')
def _prob_trials_needed(p, target):
    p, target = Fraction(str(p)), fr(target)
    if not 0 < p < 1 or not 0 < target < 1:
        raise Cannot('probabilities out of range')
    n = 1
    while 1 - (1 - p) ** n <= target:
        n += 1
        if n > 500:
            raise Cannot('no number of trials reaches the target')
    return [Fraction(n)]


@solver('prob_which_bag')
def _prob_which_bag(r1, n1, r2, n2):
    r1, n1, r2, n2 = (fr(v) for v in (r1, n1, r2, n2))
    ja, jb = r1 / n1 / 2, r2 / n2 / 2
    if ja + jb == 0:
        raise Cannot('the colour cannot be taken')
    return [ja / (ja + jb)]


# ───────────────────────── ratio and proportion ─────────────────────────

@solver('ratio_ages')
def _ratio_ages(a, b, n, c, d, ask):
    a, b, n, c, d = (fr(v) for v in (a, b, n, c, d))
    # (a t + n) / (b t + n) = c / d
    den = b * c - a * d
    if den == 0:
        raise Cannot('the ratio does not change')
    t = n * (d - c) / den
    if t <= 0:
        raise Cannot('no positive multiplier')
    if ask == 'younger':
        return [a * t]
    if ask == 'older':
        return [b * t]
    raise Cannot(f'unknown ask {ask!r}')


@solver('ratio_fraction_groups')
def _ratio_fraction_groups(f1, s1, s2):
    f1, s1, s2 = (Fraction(str(v)) for v in (f1, s1, s2))
    return [f1 * s1 + (1 - f1) * s2]


@solver('ratio_percent_more')
def _ratio_percent_more(total, p, ask):
    total, p = fr(total), fr(p)
    less = total / (2 + p / 100)
    more = less * (1 + p / 100)
    if ask == 'more':
        return [more]
    if ask == 'less':
        return [less]
    raise Cannot(f'unknown ask {ask!r}')


@solver('ratio_three_part_difference')
def _ratio_three_part_difference(a, b1, b2, c, gap, ask):
    a, b1, b2, c = (int(v) for v in (a, b1, b2, c))
    gap = fr(gap)
    lcm = b1 * b2 // math.gcd(b1, b2)
    pa, pb, pc = a * lcm // b1, lcm, c * lcm // b2
    diff = abs(pc - pa)
    if diff == 0:
        raise Cannot('A and C have equal shares')
    part = gap / diff
    if ask == 'B':
        return [pb * part]
    if ask == 'total':
        return [(pa + pb + pc) * part]
    raise Cannot(f'unknown ask {ask!r}')


@solver('ratio_algebraic_parts')
def _ratio_algebraic_parts(p, q, r, s, a, b):
    p, q, r, s, a, b = (fr(v) for v in (p, q, r, s, a, b))
    # (p x + q) / (r x + s) = a / b
    den = b * p - a * r
    if den == 0:
        raise Cannot('no single value of x')
    return [(a * s - b * q) / den]


@solver('ratio_expression')
def _ratio_expression(a, b, p, q, r, s):
    a, b, p, q, r, s = (int(v) for v in (a, b, p, q, r, s))
    top, bot = p * a + q * b, r * a + s * b
    g = math.gcd(top, bot)
    return [Ratio(top // g, bot // g)]


# ───────────────────────── graphs ─────────────────────────

@solver('gr_line_two_points', problem=True)
def _gr_line_two_points(_p, _records, x1, y1, x2, y2):
    x1, y1, x2, y2 = (fr(v) for v in (x1, y1, x2, y2))
    if x1 == x2:
        raise Cannot('a vertical line has no y = mx + c form')
    m = (y2 - y1) / (x2 - x1)
    return _tuple(_p, m, y1 - m * x1)


@solver('gr_x_intercept')
def _gr_x_intercept(m, c):
    m, c = fr(m), fr(c)
    if m == 0:
        raise Cannot('a horizontal line does not cross the x-axis')
    return [-c / m, Fraction(0)]


@solver('gr_missing_coordinate')
def _gr_missing_coordinate(m, c, ask, given):
    m, c, given = fr(m), fr(c), fr(given)
    if ask == 'y':
        return [m * given + c]
    if ask == 'x':
        if m == 0:
            raise Cannot('a horizontal line fixes y, not x')
        return [(given - c) / m]
    raise Cannot(f'unknown ask {ask!r}')


@solver('gr_parallel_through', problem=True)
def _gr_parallel_through(_p, _records, m, x, y):
    m, x, y = fr(m), fr(x), fr(y)
    return _tuple(_p, m, y - m * x)


@solver('gr_gradient_graph')
def _gr_gradient_graph(x1, y1, x2, y2):
    x1, y1, x2, y2 = (fr(v) for v in (x1, y1, x2, y2))
    if x1 == x2:
        raise Cannot('the marked points share an x-coordinate')
    return [(y2 - y1) / (x2 - x1)]


def _line_through(svg, pts, tol=0.02):
    """Messages when the drawn polyline does not pass through every point in ``pts`` (read through the tick labels)."""
    ax, ay = _axis(svg, 'tx'), _axis(svg, 'ty')
    lines = [e for e in elements(svg, 'polyline') if e.get('class') == 'series']
    if len(lines) != 1:
        return [f'expected one drawn line, found {len(lines)}']
    coords = [tuple(float(v) for v in pair.split(',')) for pair in lines[0]['points'].split()]
    if len(coords) < 2:
        return ['the drawn line has fewer than two points']
    (px0, py0), (px1, py1) = coords[0], coords[-1]
    x0, y0, x1, y1 = ax.value(px0), ay.value(py0), ax.value(px1), ay.value(py1)
    out = []
    span = max(abs(float(x1 - x0)), 1e-9)
    for x, y in pts:
        expect = y0 + (y1 - y0) * (float(x) - float(x0)) / span
        if abs(expect - float(y)) > tol * max(1.0, abs(float(y1 - y0))):
            out.append(f'the drawn line does not pass through ({x}, {y})')
    return out


@diagram('gr_gradient_graph')
def _gr_gradient_graph_drawn(inputs, question):
    svg = one_svg(question)
    marks = read_marks(svg)
    want = sorted([(fr(inputs['x1']), fr(inputs['y1'])), (fr(inputs['x2']), fr(inputs['y2']))])
    out = []
    if len(marks) != 2 or any(abs(float(a - b)) > 0.05 for m, w in zip(marks, want) for a, b in zip(m, w)):
        out.append(f'the marked points read as {marks}, the record says {want}')
    out.extend(_line_through(svg, want))
    return out


@solver('gr_conversion')
def _gr_conversion(x, y, ask, amount=None):
    x, y = fr(x), fr(y)
    if amount is not None:
        # C8: the amount to convert is the one the sentence prints; the line gives the rate
        if x == 0 or y == 0:
            raise Cannot('the marked point gives no rate')
        return [fr(amount) * y / x] if ask == 'to' else [fr(amount) * x / y]
    if ask == 'to':
        return [y]
    if ask == 'from':
        return [x]
    raise Cannot(f'unknown ask {ask!r}')


@diagram('gr_conversion')
def _gr_conversion_drawn(inputs, question):
    svg = one_svg(question)
    marks = read_marks(svg)
    want = (fr(inputs['x']), fr(inputs['y']))
    out = []
    if len(marks) != 1 or any(abs(float(a - b)) > 0.05 for a, b in zip(marks[0], want)):
        out.append(f'the marked point reads as {marks}, the record says {want}')
    out.extend(_line_through(svg, [(Fraction(0), Fraction(0)), want]))
    return out


@solver('gr_perp_bisector', problem=True)
def _gr_perp_bisector(_p, _records, x1, y1, x2, y2):
    x1, y1, x2, y2 = (fr(v) for v in (x1, y1, x2, y2))
    if x1 == x2 or y1 == y2:
        raise Cannot('the bisector of a horizontal or vertical segment has no y = mx + c form or no gradient')
    m_ab = (y2 - y1) / (x2 - x1)
    perp = -1 / m_ab
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    return _tuple(_p, perp, my - perp * mx)


# ───────────────────────── statistics ─────────────────────────

@solver('stats_frequency_density')
def _stats_frequency_density(lo, hi, ask, freq=None, fd=None):
    lo, hi = fr(lo), fr(hi)
    width = hi - lo
    if width <= 0:
        raise Cannot('the class has no width')
    if ask == 'density':
        return [fr(freq) / width]
    if ask == 'frequency':
        return [Fraction(str(fd)) * width]
    raise Cannot(f'unknown ask {ask!r}')
