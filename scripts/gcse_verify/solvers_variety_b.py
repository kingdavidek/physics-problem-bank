"""Solvers for the Phase 3 batch B record families (docs/GCSE_MATHS_VARIETY.md section 19).

Independence rule: these recompute each answer from the numbers the pupil is shown, from first principles, with the
standard library and sympy only. They must not import any generator module or helper (checked by the test).
"""
from __future__ import annotations

import math  # noqa: F401
import re
from fractions import Fraction

import sympy

from . import core
from .core import Cannot
from .registry import fr, solver
from .solvers_algebra import (Ctx, _drawn, _drawn_lines_cross, _line_y, _parabola_roots, _text_lines, judge, sym,
                              task)
from .solvers_algebra_parse import expr, split_relations


def _solve2(a1, b1, c1, a2, b2, c2):
    a1, b1, c1, a2, b2, c2 = (fr(v) for v in (a1, b1, c1, a2, b2, c2))
    det = a1 * b2 - a2 * b1
    if det == 0:
        raise Cannot('the two equations are parallel or identical')
    return (c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det


# ───────────────────────── simultaneous equations ─────────────────────────

@solver('sim_sub_solution')
def _sim_sub_solution(p, q, r, s, x, y):
    """c = p x + q y and d = r x + s y at the given solution."""
    return [fr(p) * fr(x) + fr(q) * fr(y), fr(r) * fr(x) + fr(s) * fr(y)]


@solver('sim_two_item_check')
def _sim_two_item_check(n1a, n1b, t1, n2a, n2b, t2, n3a, n3b):
    a, b = _solve2(n1a, n1b, t1, n2a, n2b, t2)
    return [a, b, fr(n3a) * a + fr(n3b) * b]


@solver('sim_expr_value')
def _sim_expr_value(a1, b1, c1, a2, b2, c2, ask):
    x, y = _solve2(a1, b1, c1, a2, b2, c2)
    if ask == 'xy':
        return [x * y]
    if ask == 'x2y2':
        return [x * x + y * y]
    raise Cannot(f'unknown expression {ask!r}')


@solver('sim_ages')
def _sim_ages(k, n, m):
    """parent = k child now; in n years parent = m child: returns [parent, child]."""
    k, n, m = fr(k), fr(n), fr(m)
    # k c + n = m (c + n)  ->  (k - m) c = (m - 1) n
    if k == m:
        raise Cannot('no unique age')
    c = (m - 1) * n / (k - m)
    return [k * c, c]


@solver('sim_parallel_k')
def _sim_parallel_k(kind, a1, b1, c1, a2, c2):
    """a1 x + b1 y = c1 and a2 x + k y = c2: k for no solution (parallel) or infinitely many (same line)."""
    a1, b1, c1, a2, c2 = (fr(v) for v in (a1, b1, c1, a2, c2))
    k = a2 * b1 / a1                  # same direction: a1 / a2 = b1 / k
    same_line = c1 * a2 == c2 * a1    # the right-hand sides scale by the same factor
    if kind == 'none' and same_line:
        raise Cannot('the lines are the same, so there are infinitely many solutions, not none')
    if kind == 'infinite' and not same_line:
        raise Cannot('the lines are parallel, so there is no solution, not infinitely many')
    if kind not in ('none', 'infinite'):
        raise Cannot(f'unknown kind {kind!r}')
    return [k]


@solver('sim_equal_cost')
def _sim_equal_cost(f1, r1, f2, r2):
    """f1 + r1 n = f2 + r2 n: returns [n, cost]."""
    f1, r1, f2, r2 = (fr(v) for v in (f1, r1, f2, r2))
    if r1 == r2:
        raise Cannot('the rates are equal')
    n = (f2 - f1) / (r1 - r2)
    return [n, f1 + r1 * n]


# ───────────────────────── completing the square ─────────────────────────

@solver('cts_q_given_p')
def _cts_q_given_p(b, c, p):
    """x^2 + b x + c = (x + p)^2 + q for all x: q = c - p^2 (and b = 2p must hold)."""
    b, c, p = fr(b), fr(c), fr(p)
    if b != 2 * p:
        raise Cannot('the bracket does not match the x term')
    return [c - p * p]


@solver('cts_min_read')
def _cts_min_read(p, k):
    """The least value of y = (x + p)^2 + k: where dy/dx = 0 (review 2026-10-28; was an 'alg' task)."""
    x = sympy.Symbol('x')
    y = (x + sympy.Rational(str(p))) ** 2 + sympy.Rational(str(k))
    (x_min,) = sympy.solve(sympy.diff(y, x), x)
    return [fr(str(y.subs(x, x_min)))]


@solver('cts_min_nonmonic')
def _cts_min_nonmonic(a, b, c):
    """The least value of a x^2 + b x + c (a > 0) from the turning point (review 2026-10-28; was an 'alg' task)."""
    if fr(a) <= 0:
        raise Cannot('no minimum: the x^2 term is not positive')
    x = sympy.Symbol('x')
    y = sympy.Rational(str(a)) * x ** 2 + sympy.Rational(str(b)) * x + sympy.Rational(str(c))
    (x_min,) = sympy.solve(sympy.diff(y, x), x)
    return [fr(str(y.subs(x, x_min)))]


@solver('cts_hence_solve', problem=True)
def _cts_hence_solve(_p, _records, b, c, p, k):
    """x^2 + b x + c = (x + p)^2 + k must be an identity; the roots of x^2 + b x + c = 0 are compared as a set."""
    b, c, p, k = (fr(v) for v in (b, c, p, k))
    if b != 2 * p or c != p * p + k:
        raise Cannot('the stated completed-square form is not equal to the expression')
    x = sympy.Symbol('x')
    roots = sympy.solve(x ** 2 + sympy.Rational(b.numerator, b.denominator) * x
                        + sympy.Rational(c.numerator, c.denominator), x)
    return judge(Ctx(_p, {}), 'set', roots)


@solver('cts_a_minus_sq')
def _cts_a_minus_sq(c, b, a, p):
    """c + b x - x^2 = a - (x - p)^2: returns [a, p] after checking the identity."""
    c, b, a, p = (fr(v) for v in (c, b, a, p))
    x = sympy.Symbol('x')

    def rat(f):
        return sympy.Rational(f.numerator, f.denominator)
    # solve for the unique a and p
    p_want = b / 2
    a_want = c + p_want * p_want
    if (p, a) != (p_want, a_want):
        raise Cannot(f'recorded a={a}, p={p} but the identity needs a={a_want}, p={p_want}')
    if sympy.expand(rat(c) + rat(b) * x - x ** 2 - (rat(a_want) - (x - rat(p_want)) ** 2)) != 0:
        raise Cannot('identity fails')
    return [a_want, p_want]


@solver('cts_count_roots')
def _cts_count_roots(b, c):
    """Number of real roots of x^2 + b x + c = 0, from the sign of c - (b/2)^2."""
    b, c = fr(b), fr(c)
    k = c - (b / 2) ** 2
    return [Fraction(2 if k < 0 else 1 if k == 0 else 0)]


@solver('cts_from_vertex')
def _cts_from_vertex(h, k):
    """y = x^2 + b x + c with minimum point (h, k): b = -2h, c = h^2 + k."""
    h, k = fr(h), fr(k)
    return [-2 * h, h * h + k]


# ───────────────────── quadratic simultaneous equations ─────────────────────

@solver('qsim_sub_coeffs')
def _qsim_sub_coeffs(m, c):
    """x^2 = m x + c rearranged to x^2 + p x + q = 0: [p, q]."""
    return [-fr(m), -fr(c)]


@solver('qsim_y_from_x')
def _qsim_y_from_x(m, c, x1, x2):
    """y at x1 and x2, which must really be intersections of y = x^2 and y = m x + c."""
    m, c, x1, x2 = (fr(v) for v in (m, c, x1, x2))
    for x in (x1, x2):
        if x * x != m * x + c:
            raise Cannot(f'x = {x} is not an intersection of y = x^2 and y = {m}x + {c}')
    return [x1 * x1, x2 * x2]


@solver('qsim_circle_line_y')
def _qsim_circle_line_y(r2, m, c, x):
    """The line gives y at x; the point must also lie on x^2 + y^2 = r2."""
    r2, m, c, x = (fr(v) for v in (r2, m, c, x))
    y = m * x + c
    if x * x + y * y != r2:
        raise Cannot('the point is not on the circle')
    return [y]


@solver('qsim_sum_product', problem=True)
def _qsim_sum_product(_p, _records, total, product):
    """x + y = total and x y = product: the possible values of x are the roots of t^2 - total t + product."""
    t = sympy.Symbol('t')
    roots = sympy.solve(t ** 2 - sympy.Rational(str(total)) * t + sympy.Rational(str(product)), t)
    return judge(Ctx(_p, {}), 'set', roots)


@solver('qsim_tangent_k')
def _qsim_tangent_k(m, c0):
    """y = m x + k touches y = x^2 + c0: x^2 - m x + (c0 - k) = 0 has a repeated root, m^2 = 4 (c0 - k)."""
    m, c0 = fr(m), fr(c0)
    return [c0 - m * m / 4]


@solver('qsim_largest_k_miss')
def _qsim_largest_k_miss(m, c0=0):
    """y = m x + k misses y = x^2 + c0 when x^2 - m x + (c0 - k) = 0 has no real root, m^2 - 4 (c0 - k) < 0: the
    greatest whole k below c0 - m^2 / 4."""
    bound = fr(c0) - fr(m) ** 2 / 4
    k = math.floor(bound)
    if k == bound:
        k -= 1
    return [Fraction(k)]


def _two_points(eqs):
    x, y = sympy.symbols('x y')
    sols = sympy.solve(eqs, [x, y], dict=True)
    if len(sols) != 2:
        raise Cannot(f'{len(sols)} intersections')
    sols.sort(key=lambda d: d[x])
    return [(d[x], d[y]) for d in sols]


@solver('qsim_midpoint')
def _qsim_midpoint(m, c):
    """Midpoint of the two points where y = x^2 meets y = m x + c."""
    x, y = sympy.symbols('x y')
    (x1, y1), (x2, y2) = _two_points([y - x ** 2, y - sympy.Rational(str(m)) * x - sympy.Rational(str(c))])
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    if not (mx.is_rational and my.is_rational):
        raise Cannot('midpoint is not rational')
    return [Fraction(int(mx.p), int(mx.q)), Fraction(int(my.p), int(my.q))]


@solver('qsim_circle_line_points')
def _qsim_circle_line_points(r2, m, c):
    """Both intersections of x^2 + y^2 = r2 and y = m x + c, smaller x first: [x1, y1, x2, y2]."""
    x, y = sympy.symbols('x y')
    pts = _two_points([x ** 2 + y ** 2 - sympy.Rational(str(r2)), y - sympy.Rational(str(m)) * x - sympy.Rational(str(c))])
    out = []
    for px, py in pts:
        if not (px.is_rational and py.is_rational):
            raise Cannot('intersections are not rational')
        out += [Fraction(int(px.p), int(px.q)), Fraction(int(py.p), int(py.q))]
    return out


@solver('qsim_hyperbola_line_points')
def _qsim_hyperbola_line_points(k, d):
    """Both intersections of x y = k and y = x + d, smaller x first: [x1, y1, x2, y2]."""
    x, y = sympy.symbols('x y')
    pts = _two_points([x * y - sympy.Rational(str(k)), y - x - sympy.Rational(str(d))])
    out = []
    for px, py in pts:
        if not (px.is_rational and py.is_rational):
            raise Cannot('intersections are not rational')
        out += [Fraction(int(px.p), int(px.q)), Fraction(int(py.p), int(py.q))]
    return out


# ───────────────────────────── algebraic fractions ─────────────────────────────

@solver('af_undefined')
def _af_undefined(a, b):
    """k / (a x + b) is undefined where the denominator is zero: x = -b / a."""
    a, b = fr(a), fr(b)
    if a == 0:
        raise Cannot('the denominator does not contain x')
    return [-b / a]


@solver('af_solve_quad_recip', problem=True)
def _af_solve_quad_recip(_p, _records, k, d):
    """k / x = x + d: the roots (x = 0 is excluded)."""
    x = sympy.Symbol('x')
    eq = sympy.Rational(str(k)) / x - (x + sympy.Rational(str(d)))
    roots = [r for r in sympy.solve(eq, x) if r != 0]
    return judge(Ctx(_p, {}), 'set', roots)


@solver('af_solve_two_fractions', problem=True)
def _af_solve_two_fractions(_p, _records, a, b):
    """a / (x + 1) + b / (x - 1) = 1: the roots, with x = 1 and x = -1 excluded."""
    x = sympy.Symbol('x')
    eq = sympy.Rational(str(a)) / (x + 1) + sympy.Rational(str(b)) / (x - 1) - 1
    roots = [r for r in sympy.solve(eq, x) if r not in (1, -1)]
    return judge(Ctx(_p, {}), 'set', roots)


# ───────────────────────────── algebraic proof ─────────────────────────────

@solver('ap_common_factor', problem=True)
def _ap_common_factor(_p, _records, m, p, q):
    """p a + q b = m ( ... ): the bracket is (p / m) a + (q / m) b."""
    a, b = sympy.symbols('a b')
    m, p, q = (sympy.Rational(str(v)) for v in (m, p, q))
    if (p / m).q != 1 or (q / m).q != 1:
        raise Cannot('m is not a common factor')
    return judge(Ctx(_p, {}), 'val', p / m * a + q / m * b)


@solver('ap_bracket_const')
def _ap_bracket_const(a, b):
    """a(n + b) - a n: the letter cancels and the value is the same for every n (review 2026-10-28)."""
    n = sympy.Symbol('n')
    e = sympy.expand(sympy.Rational(str(a)) * (n + sympy.Rational(str(b))) - sympy.Rational(str(a)) * n)
    if e.free_symbols:
        raise Cannot('the letter does not cancel')
    return [fr(str(e))]


# ───────────────────────────── functions ─────────────────────────────

@solver('fn_neg_input')
def _fn_neg_input(c, m, x):
    """f(x) = c - m x at the given (negative) input (review 2026-10-28; was an 'alg' task)."""
    return [fr(c) - fr(m) * fr(x)]


@solver('fn_inverse_value')
def _fn_inverse_value(m, c, y):
    """f(x) = m x + c: f^-1(y) = (y - c) / m."""
    m, c, y = fr(m), fr(c), fr(y)
    if m == 0:
        raise Cannot('f has no inverse')
    return [(y - c) / m]


# ───────────────────── graphical simultaneous equations ─────────────────────

def _drawn_point_ok(d):
    """A point marked on a drawing of two lines must lie on both of them."""
    out = []
    p = d.get('point')
    if p is not None:
        for i in ('1', '2'):
            if _line_y(d['m' + i], d['c' + i], sympy.Integer(p[0])) != p[1]:
                out.append(core.Verdict(False, f'the marked point {tuple(p)} is not on line {i}'))
    return out


@task('gsim_coord')
def _t_gsim_coord(ctx, which='x', **kw):
    """The x or the y of the point where the two drawn lines cross."""
    d = _drawn(ctx, 'lines')
    cross = _drawn_lines_cross(d)
    if cross is None:
        return core.Verdict(False, 'the drawn lines are parallel, so there is no crossing point')
    return _drawn_point_ok(d) + judge(ctx, 'val', cross[0 if which == 'x' else 1])


def _which_line(ctx):
    m = re.search(r'line\s+l\s*([\u2081\u2082])', ctx.low)
    if not m:
        raise Cannot('the question does not name line L1 or L2')
    return '1' if m.group(1) == '\u2081' else '2'


@task('gsim_intercept')
def _t_gsim_intercept(ctx, **kw):
    """The y-intercept of the named drawn line (the drawing must show x = 0)."""
    d = _drawn(ctx, 'lines')
    return _drawn_point_ok(d) + judge(ctx, 'val', sympy.Integer(d['c' + _which_line(ctx)]))


@task('gsim_gradient')
def _t_gsim_gradient(ctx, **kw):
    d = _drawn(ctx, 'lines')
    return _drawn_point_ok(d) + judge(ctx, 'val', sympy.Integer(d['m' + _which_line(ctx)]))


def _stated_lines(ctx):
    """(m, c) of every linear equation written in the question, in any arrangement (y = 2x + 1, x + y = 7)."""
    x, y = sym('x'), sym('y')
    out = []
    for seg in ctx.segs:
        parts, ops = split_relations(seg)
        if ops != ['=']:
            continue
        try:
            e = sympy.expand(expr(parts[0]) - expr(parts[1]))
        except Cannot:
            continue
        if e.free_symbols != {x, y}:
            continue
        poly = sympy.Poly(e, x, y)
        if poly.total_degree() != 1:
            continue
        a, b, c = poly.coeff_monomial(x), poly.coeff_monomial(y), poly.coeff_monomial(1)
        if b == 0:
            raise Cannot('a vertical line is not a graph of y')
        out.append((-a / b, -c / b))
    return out


@task('gsim_solve_stated')
def _t_gsim_solve_stated(ctx, **kw):
    """Two equations are written and drawn: they must be the lines drawn, and the key is their crossing point."""
    d = _drawn(ctx, 'lines')
    stated = _stated_lines(ctx)
    drawn = [(sympy.Integer(d['m1']), sympy.Integer(d['c1'])), (sympy.Integer(d['m2']), sympy.Integer(d['c2']))]
    out = _drawn_point_ok(d)
    if len(stated) != 2:
        raise Cannot(f'expected two stated lines, found {stated}')
    if set(stated) != set(drawn):
        out.append(core.Verdict(False, f'the question states {stated} but the graph draws {drawn}'))
    cross = _drawn_lines_cross(d)
    if cross is None:
        return out + [core.Verdict(False, 'the lines are parallel')]
    return out + judge(ctx, 'tuple', list(cross))


@task('gsim_x_values')
def _t_gsim_x_values(ctx, **kw):
    """The x-values where the drawn parabola meets the drawn line; any equation written in x must have the same roots."""
    d = _drawn(ctx, 'parabola')
    roots = _parabola_roots(d)
    x = sym('x')
    out = []
    for (px, py) in d.get('marks', []):
        if py != px * px or py != d['a'] * px + d['b']:
            out.append(core.Verdict(False, f'the marked point {(px, py)} is not on both curves'))
    for _, rhs in _text_lines(ctx):
        if sympy.Poly(rhs, x).degree() <= 1 and sympy.expand(rhs - (d['a'] * x + d['b'])) != 0:
            out.append(core.Verdict(False, f'the question states the line y = {rhs} but the line drawn is y = {d["a"]}x + {d["b"]}'))
    for seg in ctx.segs:
        parts, ops = split_relations(seg)
        if ops == ['='] and 'y' not in seg:
            try:
                e = sympy.expand(expr(parts[0]) - expr(parts[1]))
            except Cannot:
                continue
            if e.free_symbols == {x} and sympy.Poly(e, x).degree() == 2:
                if sorted(sympy.solve(e, x), key=float) != sorted(roots, key=float):
                    out.append(core.Verdict(False, f'the equation {seg} does not have the drawn intersections {roots} as its roots'))
    if len(roots) != 2:
        return out + [core.Verdict(False, f'the drawn graphs meet {len(roots)} times, the answer boxes expect two')]
    return out + judge(ctx, 'set', roots)


@task('gsim_tangent_k')
def _t_gsim_tangent_k(ctx, **kw):
    """y = a x + k touches the drawn parabola: k is the intercept of the drawn tangent."""
    d = _drawn(ctx, 'parabola')
    out = []
    if d['a'] ** 2 + 4 * d['b'] != 0:
        out.append(core.Verdict(False, 'the drawn line is not a tangent to the parabola'))
    for (px, py) in d.get('marks', []):
        if py != px * px or py != d['a'] * px + d['b']:
            out.append(core.Verdict(False, f'the marked point {(px, py)} is not on both curves'))
    m = re.search(r'y\s*=\s*(-?\d+)\s*x\s*\+\s*k', ' '.join(ctx.segs))
    if not m or int(m.group(1)) != d['a']:
        out.append(core.Verdict(False, 'the line written in the question is not the line drawn'))
    return out + judge(ctx, 'val', sympy.Integer(d['b']))


def _cost_plans(ctx, d):
    """[(rate, fee), (rate, fee)] written in the question, checked against the two drawn lines."""
    fees = [int(m.group(1) or 0) for m in re.finditer(r'(?:a \u00a3(\d+)|no) [a-z]+ fee', ctx.low)]
    rates = [int(v) for v in re.findall(r'\u00a3(\d+) per', ctx.low)]
    if len(fees) != 2 or len(rates) != 2:
        raise Cannot(f'cannot read two fees and two rates from the question: {fees}, {rates}')
    plans = [(rates[0], fees[0]), (rates[1], fees[1])]
    drawn = [(d['m1'], d['c1']), (d['m2'], d['c2'])]
    out = _drawn_point_ok(d)
    if plans != drawn:
        out.append(core.Verdict(False, f'the question describes {plans} (rate, fee) but the graph draws {drawn}'))
    return plans, out


@task('gsim_context_cost')
def _t_gsim_context_cost(ctx, **kw):
    """The common cost where the two plans meet."""
    d = _drawn(ctx, 'lines')
    plans, out = _cost_plans(ctx, d)
    (r1, f1), (r2, f2) = plans
    if r1 == r2:
        return out + [core.Verdict(False, 'the two plans never cost the same')]
    n = sympy.Rational(f2 - f1, r1 - r2)
    return out + judge(ctx, 'val', r1 * n + f1)


@task('gsim_context_cheaper')
def _t_gsim_context_cheaper(ctx, **kw):
    """The largest whole number of units for which the first plan is strictly cheaper than the second."""
    d = _drawn(ctx, 'lines')
    plans, out = _cost_plans(ctx, d)
    (r1, f1), (r2, f2) = plans
    cheaper = [n for n in range(0, 400) if r1 * n + f1 < r2 * n + f2]
    if not cheaper or cheaper[-1] >= 399:
        return out + [core.Verdict(False, 'the first plan is not cheaper for a bounded range')]
    return out + judge(ctx, 'val', sympy.Integer(cheaper[-1]))


@task('gsim_second_intercept')
def _t_gsim_second_intercept(ctx, **kw):
    """L2 has the stated gradient and passes through the marked point P: its y-intercept."""
    d = _drawn(ctx, 'lines')
    p = d.get('point')
    if p is None:
        raise Cannot('no marked point')
    m = re.search(r'gradient\s*(-?\d+)', ctx.low.replace(' ', ' '))
    if not m:
        raise Cannot('no stated gradient')
    m2 = int(m.group(1))
    c2 = p[1] - m2 * p[0]
    out = _drawn_point_ok(d)
    if (d['m2'], d['c2']) != (m2, c2):
        out.append(core.Verdict(False, f'L2 is drawn as y = {d["m2"]}x + {d["c2"]} but the question gives gradient {m2} through {tuple(p)}'))
    return out + judge(ctx, 'val', sympy.Integer(c2))


# ───────────────────────────── equations: iteration ─────────────────────────────

@solver('eq_iterate_linear')
def _eq_iterate_linear(a, b, x0):
    """x(n+1) = a x(n) + b: [x1, x2]."""
    a, b, x = fr(a), fr(b), fr(x0)
    x1 = a * x + b
    return [x1, a * x1 + b]


@solver('eq_iterate_recip')
def _eq_iterate_recip(a, b, x0):
    """x(n+1) = a + b / x(n): [x1, x2]."""
    a, b, x = fr(a), fr(b), fr(x0)
    if x == 0:
        raise Cannot('x0 is zero')
    x1 = a + b / x
    if x1 == 0:
        raise Cannot('x1 is zero')
    return [x1, a + b / x1]


@solver('eq_sign_change')
def _eq_sign_change(p, k):
    """f(x) = x^3 + p x - k: [f(1), f(2), f(3), n] where the sign changes between n and n + 1."""
    p, k = fr(p), fr(k)
    f = [fr(x) ** 3 + p * fr(x) - k for x in (1, 2, 3)]
    changes = [n for n in (1, 2) if f[n - 1] * f[n] < 0]
    if len(changes) != 1:
        raise Cannot(f'the sign changes {len(changes)} times between 1 and 3')
    return f + [Fraction(changes[0])]
