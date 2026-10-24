"""Bank-item re-solvers: algebra, surds, equations and inequalities, sequences, simultaneous equations.

Each entry is keyed by the item's digest and works the answer out from the maths in the displayed question with
sympy (see ``solvers_bank``).  Options are read as maths too, so any equivalent written form is recognised and a
distractor that happens to be equal to the key is reported.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

import sympy

from .core import Cannot
from .solvers_algebra_parse import equivalent, parse, split_relations, strip_paren, tex_to_text, to_sympy, top_factors
from .solvers_bank import add, pick, sx

X, Y, N = sympy.symbols('x y n')


def rat(v):
    """A sympy rational as a Fraction (for the generic comparison)."""
    v = sympy.nsimplify(v) if not isinstance(v, sympy.Rational) else v
    if not isinstance(v, sympy.Rational):
        raise Cannot(f'{v} is not rational')
    return Fraction(int(v.p), int(v.q))


def runs(stem, letters='xy'):
    """Equations written in the question: maximal runs of maths characters that hold one '='."""
    cls = rf'[0-9{letters}+\-*/^()²³ .]'
    found = re.findall(rf'{cls}+={cls}+', stem)
    return [f.strip().rstrip('.').strip() for f in found]


def lhs_rhs(eq):
    parts = tex_to_text(eq).split('=')
    if len(parts) != 2:
        raise Cannot(f'not an equation: {eq!r}')
    return sx(parts[0]), sx(parts[1])


def solve_values(eq, var='x'):
    left, right = lhs_rhs(eq)
    sols = sympy.solve(left - right, sympy.Symbol(var))
    if not sols:
        raise Cannot(f'no solution found for {eq!r}')
    return sols


def option_values(t, var='x'):
    """Values in an option such as 'x = 4 or x = -4', 'x = 4 only' or 'x = 19/3'."""
    out = []
    for piece in re.split(r'\s+or\s+', t.replace(' only', '').strip()):
        m = re.fullmatch(rf'\s*{var}\s*=\s*(.+)', tex_to_text(piece))
        if not m:
            raise Cannot(f'not a solution: {piece!r}')
        out.append(sx(m.group(1)))
    return out


def same_values(a, b):
    if len(a) != len(b):
        return False
    left = list(b)
    for x in a:
        hit = next((i for i, y in enumerate(left) if equivalent(x, y)), None)
        if hit is None:
            return False
        left.pop(hit)
    return True


def solves_to(eq, var='x'):
    sols = solve_values(eq, var)
    return pick(lambda t: same_values(option_values(t, var), sols), f'the solutions of {eq} are {sols}')


def stem_eq(c, letters='x'):
    eqs = runs(c.stem, letters)
    if len(eqs) != 1:
        raise Cannot(f'expected one equation in {c.stem!r}, found {eqs}')
    return eqs[0]


def solve_the_equation(c):
    return solves_to(stem_eq(c))


# ───────────────────────────── algebra ─────────────────────────────

def after_colon(c):
    return c.stem.split(':', 1)[1].strip()


def equals_expression(c, expanded=False, factorised=False):
    """Options equal to the expression after the colon (and in the written form the question asks for)."""
    target = sx(after_colon(c))

    def test(t):
        if not equivalent(sx(t), target):
            return False
        if expanded:
            return '(' not in t
        if factorised:
            return fully_factorised(t, target)
        return True
    return pick(test, f'equals {target}' + (' expanded' if expanded else ' factorised' if factorised else ''))


def fully_factorised(t, target):
    """A product whose polynomial factors are all irreducible with no common number left inside a bracket."""
    node = strip_paren(parse(tex_to_text(t)))
    factors = [to_sympy(f) for f in top_factors(node)]
    if len(factors) < 2:
        return False
    product = sympy.Integer(1)
    for f in factors:
        product *= f
        if f.free_symbols:
            content, parts = sympy.factor_list(sympy.expand(f))
            if abs(content) != 1 or len(parts) != 1 or parts[0][1] != 1:
                return False
    return equivalent(sympy.expand(product), sympy.expand(target))


def rearranged(c):
    m = re.search(r'Make (\w) the subject: (.+)', c.stem)
    subject = sympy.Symbol(m.group(1))
    left, right = lhs_rhs(m.group(2))
    want = sympy.solve(left - right, subject)
    if len(want) != 1:
        raise Cannot('expected one rearrangement')

    def test(t):
        mm = re.fullmatch(rf'\s*{m.group(1)}\s*=\s*(.+)', tex_to_text(t))
        return bool(mm) and equivalent(sx(mm.group(1)), want[0])
    return pick(test, f'{m.group(1)} = {want[0]}')


def first_terms(c):
    m = re.search(r'nth term (.+?) gives', c.stem)
    f = sx(m.group(1))
    terms = [f.subs(N, k) for k in (1, 2, 3)]
    return pick(lambda t: [sympy.Integer(int(x)) for x in re.findall(r'-?\d+', t)] == terms, f'starts {terms}')


def substitute(c):
    m = re.search(r'If (\w) = (-?\d+), what is (.+?)\?', c.stem)
    v = sx(m.group(3)).subs(sympy.Symbol(m.group(1)), int(m.group(2)))
    return [rat(v)]


def system_of(c, letters='xy'):
    return [lhs_rhs(e) for e in runs(c.stem, letters)]


def solve_system(eqs):
    sol = sympy.solve([l - r for l, r in eqs], [X, Y], dict=True)
    if len(sol) != 1:
        raise Cannot('expected one solution')
    return sol[0]


def reads_pair(t):
    """(x, y) values from '(3, 2)' or 'x = 3, y = 4'."""
    s = tex_to_text(t).strip()
    m = re.fullmatch(r'\(\s*(.+?)\s*,\s*(.+?)\s*\)', s)
    if m:
        return sx(m.group(1)), sx(m.group(2))
    m = re.fullmatch(r'x\s*=\s*(.+?)\s*,\s*y\s*=\s*(.+)', s)
    if m:
        return sx(m.group(1)), sx(m.group(2))
    raise Cannot(f'not a pair: {t!r}')


def system_solution(c):
    sol = solve_system(system_of(c))
    return pick(lambda t: tuple(reads_pair(t)) == (sol[X], sol[Y]), f'x = {sol[X]}, y = {sol[Y]}')


def system_asks(c, var):
    sol = solve_system(system_of(c))
    return pick(lambda t: option_values(t, var) == [sol[sympy.Symbol(var)]], f'{var} = {sol[sympy.Symbol(var)]}')


def plumber(c):
    call_out, per_hour, total = c.n[0], c.n[1], c.n[2]
    return [(total - call_out) / per_hour]


add('algebra', {
    '2b62f347a3e9': solve_the_equation, '2fc38e7e05bc': solve_the_equation, '56117d825f6c': solve_the_equation,
    '74e4c734fbed': solve_the_equation, 'fba129a022fa': solve_the_equation,
    'fad343f9339e': lambda c: equals_expression(c, expanded=True),                  # expand 3(x + 2)
    '461e13da155c': lambda c: equals_expression(c, expanded=True),                  # expand (x + 3)(x + 2)
    'f7f4fba9ffcb': lambda c: equals_expression(c, factorised=True),                # factorise 6x + 9
    'a4c885644fc2': lambda c: equals_expression(c, factorised=True),                # factorise x^2 - 9
    '7ef22be66291': equals_expression,                                              # simplify 4a + 3a
    '246130852f96': equals_expression,                                              # simplify 3x^2 x 2x
    'e394d28c8ec2': lambda c: solves_to(c.stem.split('Solve', 1)[1].strip()),       # x^2 = 16
    'ef421a715cca': solve_the_equation,                                             # x^2 - 5x + 6 = 0
    '14769f569561': solve_the_equation,                                             # x^2 = 2x
    '6fe013163a85': rearranged,
    '40f2db08ad9a': first_terms,                                                    # nth term 3n + 2
    '13dad57dd7e9': substitute,                                                     # x = 4: 2x^2 - 3x + 1
    'a3f9acd9de37': system_solution,                                                # x + y = 7, 2x - y = 2
    '9e035c8c8e3f': plumber,
})


# ───────────────────────────── surds ─────────────────────────────

def squarefree_radicands(t):
    """Every radicand under a root sign in ``t`` has no square factor."""
    for r in re.findall(r'√\s*\(?\s*(\d+)', t):
        n = int(r)
        if any(n % (d * d) == 0 for d in range(2, math.isqrt(n) + 1)):
            return False
    return True


def last_value(t):
    """Value of an option, reading 'a = b' as b."""
    return sx(t.split('=')[-1])


def surd_value(c, expression, simplified=False, rationalised=False):
    target = sx(expression)

    def test(t):
        if not equivalent(last_value(t), target):
            return False
        if simplified and not squarefree_radicands(t):
            return False
        if rationalised and '√' in t.rsplit('/', 1)[-1]:
            return False
        return True
    return pick(test, f'equals {target}')


def surd_after(prefix, end, **kw):
    def spec(c):
        m = re.search(prefix + r'\s*(.+?)\s*' + end, c.stem)
        if not m:
            raise Cannot(f'{prefix!r} ... {end!r} not found in {c.stem!r}')
        return surd_value(c, m.group(1), **kw)
    return spec


simplifies_to = surd_after(r'^', r'simplifies to', simplified=True)
equals = surd_after(r'^', r'equals:')


def irrational(c):
    return pick(lambda t: sx(t).is_irrational is True, 'is irrational')


def between_integers(c):
    root = math.sqrt(float(re.search(r'√(\d+)', c.stem).group(1)))

    def test(t):
        lo, hi = [int(x) for x in re.findall(r'\d+', t)]
        return hi == lo + 1 and lo < root < hi
    return pick(test, f'consecutive integers either side of {root:.3f}')


def solve_root_equation(c):
    return solves_to(c.stem.split(':', 1)[1].strip())


add('surds', {
    '822ccdfca769': simplifies_to,                                                  # sqrt 36
    '077c1fbc65fd': surd_after(r'^', r'in simplified surd form is:', simplified=True),
    '13a2ca2acb03': simplifies_to,                                                  # sqrt 12
    '650fc3aa68dd': equals,                                                         # sqrt 8 + sqrt 2
    '15fbb63dfb30': equals,                                                         # sqrt 18 / sqrt 2
    '19b36b93e868': surd_after(r'Rationalise:', r'gives:', rationalised=True),
    '988e94464cbc': equals,                                                         # sqrt 3 x sqrt 12
    '7be46e194b20': equals,                                                         # (sqrt 5)^2
    'ae311f812a99': equals,                                                         # sqrt 20 - sqrt 5
    '982582d63c8d': irrational,
    '0a4fd9c74612': simplifies_to,                                                  # sqrt 48
    '6be565420193': surd_after(r'Expand', r'equals:'),
    'db974b36ca26': surd_after(r'^', r'in simplest form is:', simplified=True),     # sqrt 75
    'dda1671504d8': surd_after(r'^', r'rationalised is best written as:', rationalised=True),
    '56dd598839e6': simplifies_to,                                                  # sqrt2 x sqrt8 + sqrt18
    'b5e2ea5acecb': surd_after(r'Which equals', r'\?'),
    '66a73fcf79ea': simplifies_to,                                                  # sqrt 72 / sqrt 8
    '3d63037f4925': solve_root_equation,
    'fc8a8ffd985a': between_integers,
})


# ───────────────────────────── equations and inequalities ─────────────────────────────

def rel_holds(text, value, var=X):
    """Whether the (possibly chained) relation ``text`` is true when var = value."""
    parts, ops = split_relations(tex_to_text(text))
    vals = [sx(p).subs(var, value) for p in parts]
    ok = {'<': lambda a, b: a < b, '<=': lambda a, b: a <= b, '>': lambda a, b: a > b, '>=': lambda a, b: a >= b,
          '=': lambda a, b: a == b}
    return all(bool(ok[op](vals[i], vals[i + 1])) for i, op in enumerate(ops))


SAMPLES = [sympy.Rational(k, 2) for k in range(-40, 41)]


def same_relation(a, b):
    """Two inequalities in x are the same when they agree on a grid of values (half-integers from -20 to 20)."""
    return all(rel_holds(a, v) == rel_holds(b, v) for v in SAMPLES)


def value_satisfies(c):
    rel = re.search(r'satisfies (.+?) \?', c.stem).group(1)
    return pick(lambda t: rel_holds(rel, option_values(t)[0]), f'satisfies {rel}')


def solve_inequality(c):
    rel = re.search(r'Solve (.+?) \.', c.stem).group(1)
    return pick(lambda t: same_relation(t, rel), f'same solutions as {rel}')


def range_of_x(c):
    rel = re.search(r'If (.+?) , what is the range', c.stem).group(1)
    return pick(lambda t: same_relation(t, rel), f'same solutions as {rel}')


def number_line(c):
    low = re.search(r'at (-?\d+)', c.stem).group(1)
    strict = 'open circle' in c.stem
    right = 'pointing right' in c.stem
    op = ('>' if right else '<') if strict else ('>=' if right else '<=')
    return pick(lambda t: same_relation(t, f'x {op} {low}'), f'x {op} {low}')


def equivalent_to(c):
    target = sx(c.stem.split('equivalent to', 1)[1].strip(' ?'))
    return pick(lambda t: equivalent(sx(t), target), f'equals {target}')


def subject_t(c):
    """Make t the subject of the formula in the question, with the stated value of u put in: an option is right
    when, for several positive t and a, putting s from the formula into the option gives t back."""
    m = re.search(r'Make (\w) the subject of (\w) = (.+?) when (\w) = (-?\d+)', c.stem)
    if not m:
        raise Cannot(f'no "make t the subject of s = ... when u = k" in {c.stem!r}')
    subj, lhs, formula, given, value = m.groups()
    a_, s_, t_ = sympy.Symbol('a'), sympy.Symbol(lhs), sympy.Symbol(subj)
    f = sx(formula).subs(sympy.Symbol(given), int(value))
    if f.free_symbols - {a_, t_}:
        raise Cannot(f'unexpected letters in {formula!r}')

    def test(t):
        mm = re.fullmatch(rf'\s*{subj}\s*=\s*(.+)', tex_to_text(t))
        if not mm:
            return False
        rhs = sx(mm.group(1))
        for a, tt in ((4, 3), (2, 5), (6, 2), (8, 7)):
            s = f.subs({a_: a, t_: tt})
            if abs(float(rhs.subs({a_: a, s_: s})) - tt) > 1e-9:
                return False
        return True
    return pick(test, f'gives {subj} back from {lhs} = {f}')


def discriminant(c):
    left, right = lhs_rhs(c.stem.split('of', 1)[1].split('is:')[0])
    poly = sympy.Poly(sympy.expand(left - right), X)
    a, b, cc = poly.all_coeffs()
    return [rat(b * b - 4 * a * cc)]


def pair_satisfies(c):
    eqs = system_of(c)
    return pick(lambda t: all(l.subs({X: reads_pair(t)[0], Y: reads_pair(t)[1]}) == r.subs({X: reads_pair(t)[0], Y: reads_pair(t)[1]})
                              for l, r in eqs), 'satisfies both equations')


def integers_in_range(c):
    rel = re.search(r'satisfying (.+?) are', c.stem).group(1)
    want = [k for k in range(-30, 31) if rel_holds(rel, k)]
    return pick(lambda t: [int(x) for x in re.findall(r'-?\d+', t)] == want, f'the integers {want}')


add('equations_inequalities', {
    '0df4b5b366bf': lambda c: solves_to(stem_eq(c)),                                # 3x + 5 = 14
    '6ba223c4a238': value_satisfies,
    '3e3ca8e8bfc7': lambda c: solves_to(stem_eq(c)),                                # 5(x - 2) = 20
    '25251fe5bad2': lambda c: solves_to(stem_eq(c)),                                # 4x + 3 = 2x + 11
    '759664658cbf': number_line,
    '116870fea915': lambda c: solves_to(stem_eq(c)),                                # x^2 - 5x + 6 = 0
    'edfb0f82eb27': lambda c: system_asks(c, 'x'),                                  # x + y = 7, x - y = 3: x
    '24d320986a1f': equivalent_to,
    '5715064775f3': subject_t,
    '3bda85e52799': solve_inequality,
    'd67e3038e363': discriminant,
    'e1b6539b61e6': pair_satisfies,
    'ce3d9e2d9855': integers_in_range,
    '3636b076ce66': lambda c: solves_to(stem_eq(c)),                                # x^2 + 2x - 8 = 0
    '30ada404a608': range_of_x,
})


# ───────────────────────────── sequences ─────────────────────────────

def ordinal_term(c):
    """(formula text, k) from '... is 3n + 5 . What is the 10th term?'."""
    m = re.search(r'\bis (.+?) \. What is the (\d+)(?:st|nd|rd|th)', c.stem)
    if not m:
        raise Cannot(f'no formula and term number in {c.stem!r}')
    return m.group(1), int(m.group(2))


def value_of_term(c):
    formula, k = ordinal_term(c)
    return [rat(sx(formula).subs(N, k))]


def formula_matching_terms(c):
    terms = [sympy.Integer(int(x)) for x in re.findall(r'-?\d+', c.stem.split('sequence', 1)[1])]

    def test(t):
        f = sx(t)
        return all(f.subs(N, i + 1) == term for i, term in enumerate(terms))
    return pick(test, f'gives the terms {terms}')


def arithmetic_series_sum(c):
    a, b, last = c.n[0], c.n[1], c.n[3]
    d = b - a
    if c.n[2] - b != d:
        raise Cannot('the terms shown are not an arithmetic series')
    count = (last - a) / d + 1
    if count.denominator != 1 or count < 1:
        raise Cannot('the last term is not in the series')
    return [count * (a + last) / 2]


def geometric_term(c):
    a, b, k = c.n[0], c.n[1], c.n[4]
    if any(c.n[i + 1] / c.n[i] != b / a for i in range(3)):
        raise Cannot('the terms shown are not geometric')
    return [a * (b / a) ** (int(k) - 1)]


def sum_to_infinity(c):
    a, num, den = c.n[0], c.n[1], c.n[2]
    r = num / den
    if abs(r) >= 1:
        raise Cannot('the series does not converge')
    return [a / (1 - r)]


def membership(c):
    m = re.search(r'Is (\d+) a term in the sequence with nth term (.+?) \?', c.stem)
    target, f = int(m.group(1)), sx(m.group(2))
    sols = [s for s in sympy.solve(f - target, N) if s.is_integer and s > 0]
    if not sols:
        return pick(lambda t: t.strip().lower() == 'no', 'not a term')
    k = int(sols[0])
    suffix = 'th' if 10 <= k % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(k % 10, 'th')
    return pick(lambda t: t.lower().startswith('yes') and f'{k}{suffix}' in t, f'yes, the {k}{suffix} term')


def special_numbers(c):
    terms = [int(x) for x in c.n[:5]]
    classes = {
        'square numbers': lambda n: math.isqrt(n) ** 2 == n,
        'cube numbers': lambda n: round(n ** (1 / 3)) ** 3 == n,
        'triangle numbers': lambda n: math.isqrt(8 * n + 1) ** 2 == 8 * n + 1,
        'prime numbers': lambda n: n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1)),
    }
    return pick(lambda t: all(classes[t.strip().lower()](n) for n in terms), f'all of {terms} belong to it')


def second_difference_formula(c):
    want = c.n[0]

    def test(t):
        f = sx(t)
        v = [f.subs(N, k) for k in range(1, 6)]
        second = [v[i + 2] - 2 * v[i + 1] + v[i] for i in range(3)]
        return all(s == want for s in second)
    return pick(test, f'constant second difference {want}')


def sum_formula_term(c):
    m = re.search(r'S_n = (.+?) \. What is the (\d+)', c.stem)
    s = sx(m.group(1))
    k = int(m.group(2))
    return [rat(s.subs(N, k) - s.subs(N, k - 1))]


def first_term_over(c):
    a, ratio, bound = c.n[0], c.n[1] / c.n[0], c.n[4]
    if any(c.n[i + 1] / c.n[i] != ratio for i in range(3)):
        raise Cannot('the terms shown are not geometric')
    k = 1
    while a * ratio ** (k - 1) <= bound:
        k += 1
    suffix = 'th' if 10 <= k % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(k % 10, 'th')
    return pick(lambda t: t.strip() == f'{k}{suffix} term', f'the {k}{suffix} term')


def terms_of_formula(c):
    f = sx(re.search(r'nth term (.+?) \?', c.stem).group(1))

    def test(t):
        got = [int(x) for x in re.findall(r'-?\d+', t)]
        return all(f.subs(N, i + 1) == v for i, v in enumerate(got))
    return pick(test, 'starts with the terms of the nth term')


add('sequences', {
    '83d6299edd38': value_of_term,                                                  # 3n + 5: 10th term
    '7dc5ceadc8ad': formula_matching_terms,                                         # 5, 8, 11, 14
    'be4f8e44dd4a': arithmetic_series_sum,                                          # 2 + 5 + ... + 29
    '52c530a4f7f0': geometric_term,                                                 # 4, 8, 16, 32: 6th
    '6a40da80e363': lambda c: [c.n[0] / 2],                                         # second differences 4: n^2 coefficient
    '1ad5cbb2503e': membership,                                                     # is 97 in 4n + 1
    'fb134107cd78': sum_to_infinity,                                                # a = 6, r = 1/3
    '9e83dff51dff': special_numbers,
    'cfa97e4876b6': value_of_term,                                                  # n^2 + 3n - 1: 5th
    'b674064fe029': terms_of_formula,                                               # 5 - 2n
    '7ceaf686ab6d': lambda c: [Fraction(sum(range(int(c.n[0]), int(c.n[1]) + 1)))],  # sum of k, 1 to 10
    '6c7eb074424b': lambda c: [c.n[0] * (1 - c.n[1] ** int(c.n[2])) / (1 - c.n[1])],  # S_4, a = 8, r = 0.5
    '4e796a6325a4': lambda c: [c.n[1] - (c.n[0] - 1) * c.n[2]],                     # 4th term 22, d = 5: first term
    '110c3ec7f1a1': second_difference_formula,
    'b4ff7602e4bc': sum_formula_term,                                               # S_n = 4n^2 - n: 3rd term
    '7fb5abc3b228': value_of_term,                                                  # 2n^2 + 3n - 2: 10th
    '9434f1bdd098': first_term_over,                                                # 4, 12, 36, ...: first over 1000
    'fc7140e93aac': sum_formula_term,                                               # S_n = 3n^2 + 2n: 6th term
})


# ───────────────────────────── simultaneous equations ─────────────────────────────

def intersect_at(c):
    return system_solution(c)


def eliminate_variable(c):
    var = sympy.Symbol(re.search(r'eliminate (\w)', c.stem).group(1))
    (l1, r1), (l2, r2) = system_of(c)
    ops = {'add the equations': sympy.expand(l1 + l2), 'subtract the equations': sympy.expand(l1 - l2)}
    return pick(lambda t: ops[t.strip().lower()].coeff(var) == 0, f'removes {var}')


def after_subtracting(c):
    """The equation left after subtracting the second equation from the first (the x terms are equal and cancel)."""
    (l1, r1), (l2, r2) = system_of(c)
    left, right = sympy.expand(l1 - l2), r1 - r2
    if left.coeff(X) != 0:
        raise Cannot('x does not cancel')

    def test(t):
        ol, orr = lhs_rhs(t)
        ol = sympy.expand(ol)
        return ol.coeff(X) == 0 and ol.coeff(Y) == left.coeff(Y) and orr == right
    return pick(test, f'{left} = {right}')


def one_common_point(c):
    """Two lines that are not parallel meet at exactly one point (counted over several pairs of lines)."""
    counts = set()
    for a1, b1, a2, b2 in ((1, 2, 3, -1), (2, 5, 7, 1), (1, -1, 2, 3), (4, 1, 3, -2)):
        sol = sympy.linsolve([a1 * X + b1 * Y - 3, a2 * X + b2 * Y - 5], X, Y)
        counts.add(len(sol))
    if counts != {1}:
        raise Cannot('non-parallel lines should meet once')
    return pick(lambda t: t.strip() == '1', 'one point')


def best_first_step(c):
    """The step that leaves one equation in one unknown: try each step on the two equations in the question."""
    (l1, r1), (l2, r2) = system_of(c)
    one, two = runs(c.stem)

    def unknowns_after(t):
        low = t.strip().lower()
        if low == 'add the equations':
            return len((l1 + l2 - r1 - r2).free_symbols & {X, Y})
        if low.startswith('divide both equations by'):
            return len(((l1 - r1) / 2).free_symbols | ((l2 - r2) / 2).free_symbols)
        m = re.fullmatch(r'substitute (.+?) into (.+)', tex_to_text(t).strip(), flags=re.I)
        if m:
            (ls, rs), (lt, rt) = lhs_rhs(m.group(1)), lhs_rhs(m.group(2))
            var = next(iter(ls.free_symbols))
            if ls != var:
                raise Cannot('can only substitute a rearranged equation')
            return len((lt - rt).subs(var, rs).free_symbols)
        raise Cannot(f'not an algebraic step: {t!r}')
    return pick(lambda t: unknowns_after(t) == 1, 'leaves one equation in one unknown')


def ticket_prices(c):
    """Two purchases written 'k adult tickets and m child tickets cost £t': solve for the price asked about."""
    rows = re.findall(r'(\d+) adult tickets? and (\d+) child tickets? cost £(\d+)', c.stem)
    ask = re.search(r'one (adult|child) ticket\?', c.stem)
    if len(rows) != 2 or not ask:
        raise Cannot(f'cannot read two purchases and a question in {c.stem!r}')
    adult, child = sympy.symbols('adult child')
    sol = sympy.solve([int(k) * adult + int(m) * child - int(t) for k, m, t in rows], [adult, child], dict=True)
    if len(sol) != 1:
        raise Cannot('expected one solution')
    want = sol[0][adult if ask.group(1) == 'adult' else child]
    return pick(lambda t: sx(t.replace('£', '')) == want, f'£{want}')


add('simultaneous_equations', {
    '53a5338e1f14': lambda c: system_asks(c, 'x'),                                  # 3x + 2y = 16, x + y = 6: x
    'a3253f6f877e': ticket_prices,                                                  # 2a + c = 14, a + c = 9: adult
    'da21e3ef3a6c': best_first_step,
    # edfb0f82eb27 (x + y = 7, x - y = 3) is the same item as in equations_inequalities and is solved there
    '48dc92ef5f05': intersect_at,                                                   # 3x + 2y = 13, x + 2y = 7
    '555c3eec06b1': one_common_point,
    '868fa030b6f8': after_subtracting,                                                    # 2x + 3y = 12, 2x + y = 8
    'd09214678733': lambda c: system_asks(c, 'y'),                                  # x + y = 10, x - y = 4: y
    'f9b02235d17b': lambda c: system_asks(c, 'y'),                                  # x + y = 9, x = 5
    '8fc0ba79942f': eliminate_variable,                                             # eliminate y from 2x + y = 7, 3x - y = 8
    '320bd27c5745': after_subtracting,                                              # 4x + 3y = 18, 4x - y = 2
})
