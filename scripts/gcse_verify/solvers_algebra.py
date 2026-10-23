"""Algebra solvers (Phase 2): re-solve from the maths the pupil is shown, with sympy.

One family, ``alg``, carries a ``task`` name.  The solver reads the displayed ``\\( ... \\)`` segments of the
question (never the prose), works out the answer itself, and compares it with the key (a practice problem's
``correct_answer_raw``, read according to its ``answer_type``) or with the options of a multiple-choice
problem.  A generator's own numbers are never used, so the check is independent of the generator.

Judging has three canonical kinds of answer: ``val`` (one number or expression), ``set`` (roots, any order)
and ``tuple`` (ordered values), plus ``ineq`` (an inequality) and ``text`` (a keyword).  See ``judge``.
"""
from __future__ import annotations

import re
from decimal import Decimal
from fractions import Fraction

import sympy

from . import core
from .core import Cannot, Verdict
from .latex import plain
from .registry import solver
from .solvers_algebra_parse import (
    equivalent, expr, has_bracketed_sum, is_product_form, math_segments, parse, split_relations,
    strip_paren, tex_to_text, top_factors, to_sympy,
)

LETTERS = 'ABCDEFGH'
_OPT = re.compile(r'^\s*([A-H])\s*[.):]?\s+(.*)$', re.S)
_VAR = r'[a-zρθΔδ]'


def sym(name):
    return sympy.Symbol(name)


def num(v):
    """A solver-computed value as a sympy object, without ``sympify`` (which parses strings with eval)."""
    if isinstance(v, sympy.Basic):
        return v
    if isinstance(v, bool):
        raise Cannot(f'not a number: {v!r}')
    if isinstance(v, int):
        return sympy.Integer(v)
    if isinstance(v, Fraction):
        return sympy.Rational(v.numerator, v.denominator)
    if isinstance(v, (float, Decimal)):
        return sympy.Rational(str(v))
    raise Cannot(f'not a number: {v!r}')


# ───────────────────────────── context ─────────────────────────────

def read_options(p):
    opts = p.get('options')
    if not opts:
        return None
    out = []
    for o in opts:
        m = _OPT.match(str(o))
        if not m:
            return None
        out.append((m.group(1), m.group(2)))
    return out


class Ctx:
    def __init__(self, p, inputs):
        self.p = p
        self.inputs = inputs
        self.raw = str(p.get('question', ''))
        self.text = plain(self.raw)
        try:
            self.segs = [s.lower() for s in math_segments(self.raw)]
        except Cannot:
            raise
        self.at = p.get('answer_type')
        self.key = p.get('correct_answer_raw')
        self.options = read_options(p)
        self.letter = str(p.get('correct_answer', '')).strip().upper()
        self.specs = core.stated_specs(self.text)
        self.mcq = self.options is not None and self.key is None
        self.low = self.text.lower()

    def seg_with(self, pred):
        return [s for s in self.segs if pred(s)]


def eq_segments(ctx):
    """Segments that hold an equation (one plain ``=``)."""
    out = []
    for s in ctx.segs:
        parts, ops = split_relations(s)
        if ops == ['=']:
            out.append(s)
    return out


# ───────────────────────────── reading answers ─────────────────────────────

def _strip_lhs(t):
    return re.sub(rf'^\s*{_VAR}(?:_\d+)?\s*=\s*', '', t)


def read_val(text, strip_var=True):
    """sympy value of a typed answer or option text (None if it cannot be read)."""
    try:
        t = tex_to_text(text).lower()
    except Cannot:
        return None
    t = t.replace('%', '').replace('°', '')
    t = re.sub(r'^\s*[£$€]', '', t)
    if strip_var:
        t = _strip_lhs(t)
    t = t.replace(' only', '').strip()
    t = re.sub(r'^(-?\d+(?:\.\d+)?)\s*(?:km/h|km|m/s|mph|hours?|hrs?|minutes?|mins?|cm|m|kg|g|°c)$', r'\1', t)
    if not t or '=' in t or '<' in t or '>' in t:
        return None
    t = re.sub(r'(\d),(\d{3})\b', r'\1\2', t)
    try:
        return expr(t)
    except Cannot:
        return None


def split_set(text):
    t = tex_to_text(text).lower().replace(' only', '')
    t = re.sub(r'\s+(?:or|and)\s+', ',', t)
    return [x.strip() for x in t.split(',') if x.strip()]


def read_pieces(kind, text):
    """Option text to pieces of the given kind (list of strings)."""
    t = tex_to_text(text).lower().replace(' only', '')
    if kind == 'val':
        return [t]
    if kind == 'set':
        return split_set(text)
    if kind == 'tuple':
        t = t.strip()
        t = re.sub(r'^\((.*)\)$', r'\1', t)
        return [x.strip() for x in re.split(r',|;|\band\b', t) if x.strip()]
    raise Cannot(f'unknown kind {kind}')


def key_pieces(ctx, kind):
    at, raw = ctx.at, str(ctx.key)
    if at in ('number_pair', 'coordinate_pairs', 'linear_equation', 'number_fields'):
        sep = '\x1e' if '\x1e' in raw else '|'
        return raw.split(sep)
    if at == 'formula_fraction' or at == 'algebraic_fraction':
        return raw.split('|')
    if at in ('number_list', 'quadratic_roots'):
        t = re.sub(r'\s+or\s+', ',', raw)
        return [x for x in t.strip('{}').split(',') if x.strip()]
    return [raw]


def read_all(pieces):
    vals = []
    for pc in pieces:
        v = read_val(pc)
        if v is None:
            return None
        vals.append(v)
    return vals


# ───────────────────────────── comparison ─────────────────────────────

def _decimal(e):
    return Decimal(str(sympy.N(e, 40)))


def agree(exp, got, specs):
    """(ok, kind, note) whether ``got`` (sympy) is the expected value ``exp``, exactly or rounded as stated."""
    if equivalent(exp, got):
        return True, '', ''
    if not exp.free_symbols and not got.free_symbols and specs:
        try:
            for spec in specs:
                for probe in (_decimal(exp),):
                    if core.apply_spec(probe, spec) == Fraction(str(_decimal(got))):
                        return True, '', ''
        except (ValueError, ArithmeticError):
            pass
    near = False
    if not exp.free_symbols and not got.free_symbols:
        try:
            near = core._near(Fraction(str(_decimal(got))), float(exp))
        except (ValueError, ArithmeticError, TypeError):
            near = False
    return False, ('accuracy' if near else 'answer'), ''


def fmt(e):
    return str(e).replace('**', '^')


def _unstated_rounding(exp, got, specs):
    """True when ``got`` is a decimal standing in for an irrational ``exp`` with no accuracy stated."""
    return (not specs and not exp.free_symbols and not got.free_symbols and exp.is_irrational and
            got.is_Rational and not got.is_Integer)


def same_vals(kind, a, b, specs=()):
    """Equivalence of two canonical answers of the same kind."""
    if kind == 'val':
        return agree(a, b, specs)[0]
    if len(a) != len(b):
        return False
    if kind == 'tuple':
        return all(agree(x, y, specs)[0] for x, y in zip(a, b))
    left = list(b)
    for x in a:
        hit = next((i for i, y in enumerate(left) if agree(x, y, specs)[0]), None)
        if hit is None:
            return False
        left.pop(hit)
    return True


def canon_from_pieces(kind, pieces):
    vals = read_all(pieces)
    if vals is None:
        return None
    if kind == 'val':
        return vals[0] if len(vals) == 1 else None
    if kind == 'set':
        uniq = []
        for v in vals:
            if not any(equivalent(v, u) for u in uniq):
                uniq.append(v)
        return uniq
    return vals


def judge(ctx, kind, exp, form=None, allow=None):
    """Compare the expected canonical answer ``exp`` with the key or the options. Returns Verdicts.

    ``form`` ('expanded', 'factorised', 'fraction') also requires the written form of the keyed answer.
    ``allow`` is a list of further acceptable canonical answers (for example both signs of a root).
    """
    if kind == 'val' and not isinstance(exp, sympy.Basic):
        exp = num(exp)
    if kind == 'pairs':
        return _judge_pairs(ctx, exp)
    if ctx.mcq:
        return _judge_mcq(ctx, kind, exp, form, allow)
    return _judge_key(ctx, kind, exp, form, allow)


def _judge_pairs(ctx, pairs):
    """Coordinate pairs in any order. Each pair is held as x + I*y so that sets of them compare as numbers."""
    if ctx.mcq:
        raise Cannot('use judge_pred for multiple-choice coordinate pairs')
    pieces = key_pieces(ctx, 'pairs')
    vals = read_all(pieces)
    if vals is None or len(vals) % 2:
        return [Verdict(False, f'key {ctx.key!r} ({ctx.at}) cannot be read as coordinate pairs')]
    got = [vals[i] + sympy.I * vals[i + 1] for i in range(0, len(vals), 2)]
    exp = [num(a) + sympy.I * num(b) for a, b in pairs]
    if not same_vals('set', exp, got, ctx.specs):
        shown = ', '.join(f'({fmt(a)}, {fmt(b)})' for a, b in pairs)
        return [Verdict(False, f'key {ctx.key!r} but recomputed {shown}')]
    return [Verdict(True)]


def _form_ok(text, form, exp_val):
    if not form:
        return True, ''
    try:
        tree = parse(tex_to_text(text).lower() if '\\' in text else text.lower())
    except Cannot:
        return True, ''
    tree = strip_paren(tree)
    if form == 'expanded':
        if has_bracketed_sum(tree):
            return False, 'the keyed form still has brackets multiplied out'
        n = _count_terms(tree)
        want = len(sympy.Add.make_args(sympy.expand(exp_val)))
        if n != want:
            return False, f'the keyed form has {n} terms but the simplified answer has {want}'
        return True, ''
    if form == 'factorised':
        if not is_product_form(tree):
            return False, 'the keyed form is not a product of factors'
        return _fully_factorised(tree)
    return True, ''


def _count_terms(tree):
    tree = strip_paren(tree)
    if tree[0] in ('add', 'sub'):
        return _count_terms(tree[1]) + _count_terms(tree[2])
    return 1


def _fully_factorised(tree):
    for f in top_factors(strip_paren(tree)):
        f = strip_paren(f) if f[0] == 'paren' else f
        if f[0] in ('add', 'sub'):
            e = sympy.expand(to_sympy(f))
            c, facs = sympy.factor_list(e)
            if len(facs) != 1 or facs[0][1] != 1 or abs(c) != 1:
                return False, f'a bracket {fmt(e)} is not fully factorised'
            if sympy.Poly(e).degree() == 1 or True:
                content = sympy.Poly(e).content() if len(e.free_symbols) else 1
                if abs(content) != 1:
                    return False, f'a bracket {fmt(e)} still has a common factor {content}'
    return True, ''


def _judge_key(ctx, kind, exp, form, allow):
    out = []
    pieces = key_pieces(ctx, kind)
    if ctx.at in ('formula_fraction', 'algebraic_fraction') and kind == 'val' and len(pieces) == 2:
        pieces = [f'({pieces[0]})/({pieces[1]})']
    got = canon_from_pieces(kind, pieces)
    if got is None:
        return [Verdict(False, f'key {ctx.key!r} ({ctx.at}) cannot be read as a {kind}')]
    cands = [exp] + list(allow or [])
    ok = any(same_vals(kind, c, got, ctx.specs) for c in cands)
    if not ok:
        e0 = exp
        k = 'answer'
        if kind == 'val':
            k = agree(e0, got, ctx.specs)[1] or 'answer'
        out.append(Verdict(False, f'key {ctx.key!r} but recomputed {_show(kind, exp)}'
                           + (f' (stated accuracy {ctx.specs})' if ctx.specs else ''), k))
    elif kind == 'val':
        if _unstated_rounding(exp, got, ctx.specs) and not equivalent(exp, got):
            out.append(Verdict(False, f'key {ctx.key!r} is a rounded value of {fmt(exp)} but the question states no accuracy',
                               'accuracy'))
    elif kind in ('set', 'tuple'):
        for e, g in zip(exp if kind == 'tuple' else [], got):
            pass
        if (not ctx.specs) and any(g.is_Rational and not g.is_Integer and e.is_irrational for e in exp for g in got):
            out.append(Verdict(False, f'key {ctx.key!r} holds rounded values of {_show(kind, exp)} but no accuracy is stated',
                               'accuracy'))
    if form and ok:
        text = pieces[0]
        good, why = _form_ok(_strip_lhs(text.lower()), form, exp if kind == 'val' else exp[0])
        if not good:
            out.append(Verdict(False, f'key {ctx.key!r}: {why}'))
    return out or [Verdict(True)]


def _show(kind, exp):
    if kind == 'val':
        return fmt(exp)
    return '[' + ', '.join(fmt(e) for e in exp) + ']'


def _judge_mcq(ctx, kind, exp, form, allow):
    cands = [exp] + list(allow or [])
    hits, canon = [], {}
    problems = []
    for letter, text in ctx.options:
        try:
            pieces = read_pieces(kind, text)
        except Cannot:
            pieces = None
        got = canon_from_pieces(kind, pieces) if pieces else None
        canon[letter] = got
        if got is None:
            continue
        if any(same_vals(kind, c, got, ctx.specs) for c in cands):
            good, why = (True, '')
            if form:
                good, why = _form_ok(_strip_lhs(tex_to_text(text).lower()), form, exp if kind == 'val' else exp[0])
            if good:
                hits.append(letter)
            else:
                problems.append(f'option {letter} has the right value but {why}')
    keyed = ctx.letter
    out = []
    if keyed not in {l for l, _ in ctx.options}:
        out.append(Verdict(False, f'key {keyed!r} is not one of the options'))
    elif canon.get(keyed) is None:
        out.append(Verdict(False, f'keyed option {keyed} cannot be read as a {kind}'))
    if not hits:
        out.append(Verdict(False, f'no option equals the recomputed answer {_show(kind, exp)}'))
    elif hits != [keyed]:
        out.append(Verdict(False, f'recomputed {_show(kind, exp)} matches option(s) {hits} but the key is {keyed}'))
    # distractors that are equivalent to each other
    seen = []
    for letter, text in ctx.options:
        g = canon.get(letter)
        if g is None:
            continue
        for l2, g2 in seen:
            if same_vals(kind, g, g2, ()):
                out.append(Verdict(False, f'options {l2} and {letter} are equivalent'))
        seen.append((letter, g))
    out.extend(Verdict(False, m) for m in problems if keyed in m)
    return out or [Verdict(True)]


# ───────────────────────────── inequalities ─────────────────────────────

_OPMAP = {'<': '>', '>': '<', '<=': '>=', '>=': '<=', '=': '='}


def read_ineq_text(text):
    """('lin', var, op, value) or ('cmp', var, op1, lo, op2, hi) from written inequality text (None if unreadable)."""
    try:
        t = tex_to_text(text).lower()
    except Cannot:
        return None
    parts, ops = split_relations(t)
    if not ops or any(o in ('=', '==', '!=') for o in ops):
        return None
    try:
        if len(ops) == 1:
            a, b = parts
            if re.fullmatch(_VAR, a):
                return ('lin', a, ops[0], expr(b))
            if re.fullmatch(_VAR, b):
                return ('lin', b, _OPMAP[ops[0]], expr(a))
            return None
        if len(ops) == 2 and re.fullmatch(_VAR, parts[1]):
            return ('cmp', parts[1], ops[0], expr(parts[0]), ops[1], expr(parts[2]))
    except Cannot:
        return None
    return None


def read_ineq_key(ctx):
    s = str(ctx.key)
    bits = [b.strip() for b in s.split('|')]
    norm = {'≥': '>=', '≤': '<=', 'gt': '>', 'lt': '<', 'ge': '>=', 'le': '<=', '\\gt': '>', '\\lt': '<', '\\geq': '>=',
            '\\leq': '<=', '\\ge': '>=', '\\le': '<='}
    try:
        if ctx.at == 'linear_inequality' and len(bits) == 3:
            return ('lin', bits[0].lower(), norm.get(bits[1], bits[1]), expr(bits[2]))
        if ctx.at in ('compound_inequality', 'number_line') and len(bits) == 5:
            return ('cmp', bits[0].lower(), norm.get(bits[1], bits[1]), expr(bits[2]), norm.get(bits[3], bits[3]),
                    expr(bits[4]))
    except Cannot:
        return None
    return None


def ineq_equal(a, b):
    if a is None or b is None or a[0] != b[0] or a[1] != b[1]:
        return False
    if a[0] == 'lin':
        return a[2] == b[2] and equivalent(a[3], b[3])
    return a[2] == b[2] and a[4] == b[4] and equivalent(a[3], b[3]) and equivalent(a[5], b[5])


def judge_ineq(ctx, exp):
    if ctx.mcq:
        hits = [l for l, t in ctx.options if ineq_equal(exp, read_ineq_text(t))]
        out = []
        if not hits:
            out.append(Verdict(False, f'no option matches the recomputed inequality {exp}'))
        elif hits != [ctx.letter]:
            out.append(Verdict(False, f'recomputed {exp} matches {hits} but the key is {ctx.letter}'))
        return out or [Verdict(True)]
    got = read_ineq_key(ctx)
    if got is None:
        return [Verdict(False, f'key {ctx.key!r} ({ctx.at}) cannot be read as an inequality')]
    if not ineq_equal(exp, got):
        return [Verdict(False, f'key {ctx.key!r} but recomputed {exp}')]
    return [Verdict(True)]


def solve_ineq(lhs_text, op, rhs_text, var):
    """Canonical ('lin'|'cmp', ...) for a one-variable inequality ``lhs op rhs`` (linear, or quadratic between roots)."""
    x = sym(var)
    e = sympy.expand(expr(lhs_text) - expr(rhs_text))
    return ineq_from_expr(e, op, x)


def ineq_from_expr(e, op, x):
    """Solution of ``e op 0`` for the polynomial e in x (degree 1, or degree 2 with a single interval)."""
    poly = sympy.Poly(e, x)
    deg = poly.degree()
    strict = op in ('<', '>')
    if deg == 1:
        a, b = poly.all_coeffs()
        r = -b / a
        less = (op in ('<', '<=')) == (a > 0)          # a*x + b < 0  <=>  x < r when a > 0
        return ('lin', x.name, ('<' if strict else '<=') if less else ('>' if strict else '>='), r)
    if deg == 2:
        a, b, c = poly.all_coeffs()
        disc = b * b - 4 * a * c
        if disc <= 0:
            raise Cannot('quadratic inequality without two real roots')
        r1, r2 = sorted([(-b - sympy.sqrt(disc)) / (2 * a), (-b + sympy.sqrt(disc)) / (2 * a)],
                        key=lambda v: float(v))
        inside = (op in ('<', '<=')) == (a > 0)
        if not inside:
            raise Cannot('outside-the-roots inequality (two intervals) is not supported')
        o = '<' if strict else '<='
        return ('cmp', x.name, o, r1, o, r2)
    raise Cannot(f'inequality of degree {deg} is not supported')


def _interval_canon(s, var):
    if not isinstance(s, sympy.Interval):
        raise Cannot(f'solution set {s} is not one interval')
    lo, hi = s.start, s.end
    if lo == -sympy.oo:
        return ('lin', var, '<' if s.right_open else '<=', hi)
    if hi == sympy.oo:
        return ('lin', var, '>' if s.left_open else '>=', lo)
    return ('cmp', var, '<' if s.left_open else '<=', lo, '<' if s.right_open else '<=', hi)


# ───────────────────────────── helpers for tasks ─────────────────────────────

def one_var(e, name=None):
    syms = sorted(e.free_symbols, key=lambda s: s.name)
    if name:
        return sym(name)
    if len(syms) != 1:
        raise Cannot(f'expected one variable in {e}, found {syms}')
    return syms[0]


def the_equation(ctx):
    """(lhs, rhs) sympy for the single equation shown."""
    segs = eq_segments(ctx)
    if len(segs) != 1:
        raise Cannot(f'expected one equation in the question, found {segs}')
    a, b = split_relations(segs[0])[0]
    return expr(a), expr(b)


def real_solutions(e, var):
    """Real solutions of ``e = 0`` in ``var``, excluding values that make a denominator zero."""
    num, den = sympy.fraction(sympy.cancel(sympy.together(e)))
    try:
        poly = sympy.Poly(num, var)
    except sympy.PolynomialError:
        poly = None
    if poly is None:
        sols = sympy.solve(e, var)
    elif poly.degree() < 1:
        sols = []
    elif poly.degree() == 1:
        c1, c0 = poly.all_coeffs()
        sols = [-c0 / c1]
    else:
        found = sympy.roots(poly, var)
        sols = list(found) if sum(found.values()) == poly.degree() else sympy.solve(num, var)
    out = []
    for r in sols:
        if r.is_real is False:
            continue
        if den.has(var) and den.subs(var, r) == 0:
            continue
        out.append(r if r.is_Rational else sympy.simplify(r))
    return out


def want_text(ctx, pat):
    return re.search(pat, ctx.low) is not None


TASKS: dict = {}


def task(name):
    def deco(fn):
        TASKS[name] = fn
        return fn
    return deco


@solver('alg', problem=True)
def alg(_p, task=None, _records=None, **kw):
    fn = TASKS.get(task)
    if fn is None:
        raise Cannot(f'no algebra task {task!r}')
    ctx = Ctx(_p, kw)
    # The drawings made by this variant are the 'gsim_drawn' records written just before its own record.
    run = []
    for r in reversed((_records or [])[:-1]):
        if not str(r.get('family', '')).endswith('_drawn'):
            break
        run.append(r['inputs'])
    ctx.drawn = list(reversed(run))
    out = fn(ctx, **kw)
    if isinstance(out, Verdict):
        out = [out]
    return out


# ───────────────────────────── tasks: equations ─────────────────────────────

@task('solve_linear')
def t_solve_linear(ctx, var=None, **kw):
    lhs, rhs = the_equation(ctx)
    x = one_var(lhs - rhs, var)
    sols = real_solutions(lhs - rhs, x)
    if len(sols) != 1:
        return Verdict(False, f'equation {lhs} = {rhs} has {len(sols)} solutions for {x}')
    return judge(ctx, 'val', sols[0])


@task('solve_poly')
def t_solve_poly(ctx, var=None, **kw):
    lhs, rhs = the_equation(ctx)
    x = one_var(lhs - rhs, var)
    if sympy.Poly(sympy.expand(lhs - rhs), x).degree() > 4:
        raise Cannot('degree above 4')
    sols = real_solutions(lhs - rhs, x)
    if not sols:
        return Verdict(False, 'the equation has no real solutions')
    return judge(ctx, 'set', sols)


@task('solve_ineq')
def t_solve_ineq(ctx, **kw):
    segs = [s for s in ctx.segs if re.search(r'<|>', s)]
    if len(segs) != 1:
        raise Cannot(f'expected one inequality, found {segs}')
    return judge_ineq(ctx, ineq_of_text(segs[0]))


def ineq_of_text(text):
    """Canonical solution of the inequality (or double inequality) written in ``text``."""
    parts, ops = split_relations(text)
    if len(ops) == 1:
        a, b = parts
        x = one_var(expr(a) - expr(b))
        return solve_ineq(a, ops[0], b, x.name)
    if len(ops) == 2 and all(o in ('<', '<=') for o in ops):
        a, m, c = parts
        mid = expr(m)
        x = one_var(mid - expr(a)) if (mid - expr(a)).free_symbols else one_var(mid)
        lo = ineq_from_expr(sympy.expand(expr(a) - mid), ops[0], x)        # a op1 mid
        hi = ineq_from_expr(sympy.expand(mid - expr(c)), ops[1], x)        # mid op2 c
        if lo[0] != 'lin' or hi[0] != 'lin' or lo[2][0] != '>' or hi[2][0] != '<':
            raise Cannot('double inequality did not reduce to a lower and an upper bound')
        flip = {'>': '<', '>=': '<='}[lo[2]]
        return ('cmp', x.name, flip, lo[3], hi[2], hi[3])
    raise Cannot('unsupported inequality')


@task('integers_in_ineq')
def t_integers(ctx, **kw):
    segs = [s for s in ctx.segs if re.search(r'<|>', s)]
    if len(segs) != 1:
        raise Cannot('expected one inequality')
    c = ineq_of_text(segs[0])
    if c[0] != 'cmp':
        raise Cannot('integer list needs a bounded range')
    lo, hi = float(c[3]), float(c[5])
    vals = [sympy.Integer(i) for i in range(-60, 61)
            if (i > lo if c[2] == '<' else i >= lo) and (i < hi if c[4] == '<' else i <= hi)]
    return judge(ctx, 'tuple', vals)


def judge_pred(ctx, pred, desc):
    """Multiple choice only: exactly the keyed option must satisfy ``pred(option_text)``."""
    if not ctx.mcq:
        raise Cannot('judge_pred is for multiple-choice problems')
    hits = []
    for letter, text in ctx.options:
        try:
            if pred(text):
                hits.append(letter)
        except Cannot:
            continue
    if hits != [ctx.letter]:
        return [Verdict(False, f'options satisfying "{desc}" are {hits} but the key is {ctx.letter}')]
    return [Verdict(True)]


def _linear_solution(e, x):
    """The one solution of e = 0 when e is linear in x (fast path; None when it is not that simple)."""
    try:
        num, den = sympy.fraction(sympy.together(e))
        if x in den.free_symbols:
            return None
        poly = sympy.Poly(sympy.expand(num), x)
        if poly.degree() != 1:
            return None
        a, b = poly.all_coeffs()
        return [sympy.cancel(-b / a)]
    except (sympy.PolynomialError, ValueError, TypeError):
        return None


def subject_of(ctx):
    m = re.search(r'make\s+([a-zρθ])\s+the\s+subject', ctx.low)
    if not m:
        raise Cannot('no "make _ the subject" in the question')
    return m.group(1)


def split_assignments(segs):
    """(assignments {sym: value}, other segments): segments of the form ``v = number``."""
    assigns, others = {}, []
    for s in segs:
        parts, ops = split_relations(s)
        if ops == ['='] and re.fullmatch(_VAR, parts[0]):
            try:
                v = expr(parts[1])
            except Cannot:
                others.append(s)
                continue
            if not v.free_symbols:
                assigns[sym(parts[0])] = v
                continue
        others.append(s)
    return assigns, others


@task('rearrange')
def t_rearrange(ctx, **kw):
    subj = subject_of(ctx)
    segs = [s for s in eq_segments(ctx)]
    assigns, formulas = split_assignments(segs)
    if len(formulas) != 1:
        raise Cannot(f'expected one formula, found {formulas}')
    a, b = split_relations(formulas[0])[0]
    e = (expr(a) - expr(b)).subs(assigns)
    x = sym(subj)
    if x not in e.free_symbols:
        return Verdict(False, f'the subject {subj} does not appear in the formula {formulas[0]}')
    sols = _linear_solution(e, x)
    if sols is None and not ctx.mcq:
        # Fast path: the keyed rearrangement must satisfy the formula (any root of it counts, as in the full path).
        key = read_val(str(ctx.key))
        if key is not None and x not in key.free_symbols and key.free_symbols and equivalent(e.subs(x, key), sympy.Integer(0)):
            return [Verdict(True)]
    if sols is None:
        sols = sympy.solve(e, x)
    sols = [s for s in sols if s.is_real is not False]
    if not sols:
        return Verdict(False, f'the formula {formulas[0]} cannot be rearranged for {subj} (no solution)')
    if any(s.has(sympy.zoo, sympy.nan, sympy.oo) for s in sols):
        return Verdict(False, f'rearranging {formulas[0]} for {subj} divides by zero')
    return judge(ctx, 'val', sols[0], allow=sols[1:])


@task('expand')
def t_expand(ctx, **kw):
    segs = [s for s in ctx.segs if not re.search(r'[=<>]', s) and not re.fullmatch(_VAR, s.strip())]
    if len(segs) != 1:
        raise Cannot(f'expected one expression, found {segs}')
    e = sympy.expand(expr(segs[0]))
    return judge(ctx, 'val', e, form='expanded')


@task('simplify')
def t_simplify(ctx, form='expanded', **kw):
    segs = [s for s in ctx.segs if not re.search(r'[=<>]', s) and not re.fullmatch(_VAR, s.strip())]
    if len(segs) != 1:
        raise Cannot(f'expected one expression, found {segs}')
    e = sympy.simplify(expr(segs[0]))
    return judge(ctx, 'val', e, form=form or None)


@task('factorise')
def t_factorise(ctx, **kw):
    segs = [s for s in ctx.segs if not re.search(r'[=<>]', s) and not re.fullmatch(_VAR, s.strip())]
    if len(segs) != 1:
        raise Cannot(f'expected one expression, found {segs}')
    e = sympy.expand(expr(segs[0]))
    return judge(ctx, 'val', e, form='factorised')


@task('substitute')
def t_substitute(ctx, target=None, **kw):
    segs = ctx.segs
    assigns, others = split_assignments(segs)
    if not assigns:
        raise Cannot('no values given to substitute')
    forms = [s for s in others if '=' in s]
    plain_exprs = [s for s in others if '=' not in s and not re.search(r'[<>]', s)]
    if plain_exprs and not forms:
        if len(plain_exprs) != 1:
            raise Cannot(f'expected one expression, found {plain_exprs}')
        val = expr(plain_exprs[0]).subs(assigns)
    elif len(forms) == 1:
        a, b = split_relations(forms[0])[0]
        e = expr(a) - expr(b)
        m = re.search(r'find\s+([a-zρθ])\b', ctx.low)
        tgt = sym(target or (m.group(1) if m else a.strip()))
        e = e.subs(assigns)
        sols = sympy.solve(e, tgt)
        if len(sols) != 1:
            raise Cannot(f'cannot isolate {tgt} in {forms[0]}')
        val = sols[0]
    else:
        raise Cannot('cannot tell which expression to evaluate')
    return judge(ctx, 'val', val)


@task('solve_system')
def t_system(ctx, ask=None, **kw):
    pairs = [split_relations(s)[0] for s in eq_segments(ctx)]
    exprs = [expr(a) - expr(b) for a, b in pairs]
    names = sorted({s.name for e in exprs for s in e.free_symbols})
    syms = [sym(n) for n in names]
    if len(exprs) < len(syms):
        raise Cannot('fewer equations than unknowns')
    sols = sympy.solve(exprs, syms, dict=True)
    if len(sols) != 1:
        return Verdict(False, f'the system has {len(sols)} solutions')
    sol = sols[0]
    return _report_solution(ctx, sol, names, ask)


def _report_solution(ctx, sol, names, ask):
    labels = [str(x).lower() for x in (ctx.p.get('answer_labels') or [])]
    m = re.search(r'what\s+is\s+([a-zρθ])\b', ctx.low)
    if ask is None and m:
        ask = m.group(1)
    if ask:
        return judge(ctx, 'val', sol[sym(ask)])
    order = labels if labels and all(l in names for l in labels) else names
    vals = [sol[sym(n)] for n in order]
    return judge(ctx, 'tuple', vals)


# ───────────────────────────── word problems (recorded numbers) ─────────────────────────────

@solver('linear_fixed_rate')
def s_linear_fixed_rate(fixed, rate, total):
    """fixed + rate * n = total, solved for n."""
    return [(Fraction(str(total)) - Fraction(str(fixed))) / Fraction(str(rate))]


@solver('consecutive_sum')
def s_consecutive_sum(n, total):
    """n consecutive integers starting from x add up to total: n*x + n(n-1)/2 = total."""
    return [(Fraction(total) - Fraction(n * (n - 1), 2)) / Fraction(n)]


# ───────────────────────────── more text tasks ─────────────────────────────

def judge_text(ctx, expected):
    exp = str(expected).strip().lower()
    if ctx.mcq:
        hits = [l for l, t in ctx.options if tex_to_text(t).strip().lower() == exp]
        return [Verdict(True)] if hits == [ctx.letter] else [Verdict(False, f'expected option text {exp!r}, matched {hits}, key {ctx.letter}')]
    got = str(ctx.key).strip().lower()
    return [Verdict(True)] if got == exp else [Verdict(False, f'key {got!r} but recomputed {exp!r}')]


@task('verify_solution')
def t_verify_solution(ctx, **kw):
    assigns, others = split_assignments(ctx.segs)
    eqs = [s for s in others if '=' in s]
    if len(assigns) != 1 or len(eqs) != 1:
        raise Cannot(f'cannot find one equation and one claimed value in {ctx.segs}')
    a, b = split_relations(eqs[0])[0]
    ok = sympy.simplify((expr(a) - expr(b)).subs(assigns)) == 0
    return judge_text(ctx, 'yes' if ok else 'no')


_WORD_REL = [
    (r'at most|no more than|not more than|maximum of|up to|cannot exceed', '<='),
    (r'at least|no fewer than|no less than|not less than|minimum of', '>='),
    (r'fewer than|less than|under|below|smaller than', '<'),
    (r'more than|greater than|over|above|exceeds?', '>'),
]


@task('ineq_from_words')
def t_ineq_words(ctx, **kw):
    rel = None
    for pat, op in _WORD_REL:
        if re.search(pat, ctx.low):
            rel = op
            break
    if rel is None:
        raise Cannot('no inequality wording found')
    m = re.search(r'(?:' + '|'.join(p for p, _ in _WORD_REL) + r')\s+£?(\d+(?:\.\d+)?)', ctx.low)
    if not m:
        raise Cannot('no number after the inequality wording')
    segvars = [s for s in ctx.segs if re.fullmatch(_VAR, s.strip())]
    if len(segvars) != 1:
        raise Cannot(f'cannot tell the variable from {ctx.segs}')
    return judge_ineq(ctx, ('lin', segvars[0].strip(), rel, expr(m.group(1))))


@task('equal_exprs')
def t_equal_exprs(ctx, **kw):
    exprs = [s for s in ctx.segs if not re.search(r'[=<>]', s) and not re.fullmatch(_VAR, s.strip())]
    if len(exprs) != 2:
        raise Cannot(f'expected two expressions, found {exprs}')
    a, b = expr(exprs[0]), expr(exprs[1])
    x = one_var(a - b)
    sols = sympy.solve(a - b, x)
    if len(sols) != 1:
        return Verdict(False, 'the two expressions are not equal for exactly one value')
    return judge(ctx, 'tuple', [sols[0], a.subs(x, sols[0])])


_ANGLE_TOTALS = [(r'triangle', 180), (r'straight line', 180), (r'quadrilateral', 360), (r'full turn|around a point', 360)]


@task('angle_sum')
def t_angle_sum(ctx, **kw):
    total = next((t for pat, t in _ANGLE_TOTALS if re.search(pat, ctx.low)), None)
    if total is None:
        raise Cannot('no angle total wording')
    exprs = [s for s in ctx.segs if not re.search(r'[=<>]', s) and not re.fullmatch(_VAR, s.strip())]
    e = sum((expr(s) for s in exprs), sympy.Integer(0)) - total
    x = one_var(e)
    sols = sympy.solve(e, x)
    if len(sols) != 1:
        return Verdict(False, 'the angle equation has no unique solution')
    return judge(ctx, 'val', sols[0])


@task('number_line')
def t_number_line(ctx, **kw):
    segs = [s for s in ctx.segs if re.search(r'<|>', s)]
    if len(segs) != 1:
        raise Cannot(f'expected one inequality, found {segs}')
    shown = read_ineq_text(segs[0])
    if shown is None:
        raise Cannot(f'cannot read {segs[0]!r}')
    return judge_ineq(ctx, shown)


@solver('think_number')
def s_think_number(mult, add, result):
    """I think of a number, multiply by ``mult`` and add ``add``; the result is ``result``."""
    return [(Fraction(result) - Fraction(add)) / Fraction(mult)]


@solver('rect_perimeter_linear')
def s_rect_perimeter(k, perimeter):
    """Rectangle with length 2w + k and width w: 2((2w + k) + w) = perimeter."""
    return [(Fraction(perimeter) - 2 * Fraction(k)) / 6]


@solver('ratio_pair_sum')
def s_ratio_pair_sum(a, b, total):
    """Two numbers in the ratio a:b with the given sum."""
    t = Fraction(total)
    return [t * a / (a + b), t * b / (a + b)]


@solver('consecutive_list')
def s_consecutive_list(count, total, step=1):
    """``count`` consecutive integers (or evens when step=2) with the given sum; returns all of them."""
    first = (Fraction(total) - step * Fraction(count * (count - 1), 2)) / count
    return [first + step * i for i in range(count)]


@solver('rect_area_quadratic')
def s_rect_area_quadratic(a, b, area):
    """Rectangle with sides (x + a) and (x + b) and the given area: the positive root of the quadratic."""
    x = sym('x')
    roots = [r for r in sympy.solve((x + a) * (x + b) - area, x) if r.is_real and r > 0]
    if len(roots) != 1:
        raise Cannot(f'{len(roots)} positive roots')
    return [Fraction(int(roots[0].p), int(roots[0].q))] if roots[0].is_Rational else [core.Approx(float(roots[0]))]


@solver('consecutive_product')
def s_consecutive_product(k, step=1):
    """Two positive consecutive integers (step 1) or even integers (step 2) with product k."""
    n = sym('n')
    roots = [r for r in sympy.solve(n * (n + step) - k, n) if r.is_Integer and r > 0]
    if len(roots) != 1:
        raise Cannot(f'{len(roots)} positive integer solutions')
    r = int(roots[0])
    return [Fraction(r), Fraction(r + step)]


def parse_eq_field(text):
    """'eq:c,t:13:11:94' -> (var1, var2, a, b, total) for 'a var1 + b var2 = total'."""
    m = re.fullmatch(r'eq:([a-z]),([a-z]):(-?\d+):(-?\d+):(-?\d+)', str(text).strip())
    if not m:
        return None
    return m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), int(m.group(5))


def _fields(ctx):
    raw = str(ctx.key)
    return raw.split('\x1e') if '\x1e' in raw else raw.split('|')


@task('two_equations_multipart')
def t_two_equations_multipart(ctx, v1='c', v2='t', a1=0, b1=0, c1=0, a2=0, b2=0, c2=0, **kw):
    """Parts: the two equations, then the value of each unknown asked for (in the order of the parts)."""
    f = _fields(ctx)
    out = []
    want = [(v1, v2, a1, b1, c1), (v1, v2, a2, b2, c2)]
    for i, w in enumerate(want):
        got = parse_eq_field(f[i]) if i < len(f) else None
        if got != w:
            out.append(Verdict(False, f'part {i + 1}: key {f[i] if i < len(f) else None!r} but the question gives {w}'))
    x, y = sym(v1), sym(v2)
    sol = sympy.solve([a1 * x + b1 * y - c1, a2 * x + b2 * y - c2], [x, y], dict=True)
    if len(sol) != 1:
        return [Verdict(False, 'the pair of equations has no unique solution')]
    rest = f[2:]
    asks = [sol[0][x], sol[0][y]]
    if len(rest) != 2:
        return out + [Verdict(False, f'expected two value fields, key has {rest}')]
    for g, e in zip(rest, asks):
        v = read_val(g)
        if v is None or not equivalent(v, e):
            out.append(Verdict(False, f'key value {g!r} but recomputed {e}'))
    return out or [Verdict(True)]


@task('phone_plans')
def t_phone_plans(ctx, fixed_a=0, rate_a=0, fixed_b=0, rate_b=0, **kw):
    """Plan costs in pounds with rates in pence: fields are CA, CB, minutes where equal, and 'm|<|N'."""
    f = _fields(ctx)
    m = sym('m')
    ca = fixed_a + sympy.Rational(rate_a, 100) * m
    cb = fixed_b + sympy.Rational(rate_b, 100) * m
    out = []
    for i, e in enumerate((ca, cb)):
        v = read_val(f[i])
        if v is None or not equivalent(v, e):
            out.append(Verdict(False, f'part (a) expression {f[i]!r} but recomputed {e}'))
    sol = sympy.solve(ca - cb, m)
    if len(sol) != 1:
        return [Verdict(False, 'plans never cost the same')]
    v = read_val(f[2])
    if v is None or not equivalent(v, sol[0]):
        out.append(Verdict(False, f'part (b) key {f[2]!r} but the plans cost the same at m = {sol[0]}'))
    bits = f[3].split('|')
    want = solve_ineq(str(ca), '<', str(cb), 'm')
    got = ('lin', bits[0], bits[1], expr(bits[2])) if len(bits) == 3 else None
    if not ineq_equal(want, got):
        out.append(Verdict(False, f'part (c) key {f[3]!r} but recomputed {want}'))
    return out or [Verdict(True)]


@task('ineq_linear_rec')
def t_ineq_linear_rec(ctx, have=0, per=0, target=0, var='w', **kw):
    """have + per * var >= target, var a whole number of weeks (so rounded up)."""
    need = (Fraction(str(target)) - Fraction(str(have))) / Fraction(str(per))
    import math as _m
    return judge_ineq(ctx, ('lin', var, '>=', sympy.Integer(_m.ceil(need))))


@task('identity_steps')
def t_identity_steps(ctx, **kw):
    """'Show that A - B == C': the fields are expand(A), expand(B), the simplified difference."""
    seg = next((s for s in ctx.segs if '==' in s), None)
    if not seg:
        raise Cannot('no identity shown')
    lhs, rhs = seg.split('==')
    m = re.fullmatch(r'\s*(\(.*\)\^2)\s*-\s*(\(.*\)\^2)\s*', lhs)
    if not m:
        raise Cannot(f'cannot split {lhs!r} into two squares')
    a, b = expr(m.group(1)), expr(m.group(2))
    want = [sympy.expand(a), sympy.expand(b), sympy.expand(a - b)]
    if not equivalent(sympy.expand(a - b), expr(rhs)):
        return Verdict(False, f'{lhs} is not identically {rhs}')
    f = _fields(ctx)
    out = []
    for g, e in zip(f, want):
        v = read_val(g)
        if v is None or not equivalent(v, e):
            out.append(Verdict(False, f'step {g!r} but recomputed {e}'))
    return out or [Verdict(True)]


@task('complete_square')
def t_complete_square(ctx, **kw):
    """Key 'kind|...': plus/minus -> (x +/- p)^2 + k ; scaled -> a(x + p)^2 + k ; expand -> x^2 + bx + c."""
    kind = str(ctx.key).split('|')[0] if not ctx.mcq else None
    if ctx.mcq:
        _, target = _the_quad(ctx)
        return judge(ctx, 'val', target)
    segs = [s for s in ctx.segs if not re.search(r'[<>]', s)]
    x = sym('x')
    target = None
    for s in segs:
        e_text = s.split('=', 1)[1] if s.startswith('y =') else s
        if '=' in e_text and not e_text.strip().startswith('x'):
            continue
        try:
            e = sympy.expand(expr(e_text))
        except Cannot:
            continue
        if e.free_symbols == {x}:
            target = e
            break
    if target is None:
        raise Cannot(f'no quadratic found in {segs}')
    poly = sympy.Poly(target, x)
    if poly.degree() != 2:
        raise Cannot('not a quadratic')
    a, b, c = poly.all_coeffs()
    if kind == 'expand':
        shown = next(s for s in segs if '^2' in s)           # (x + p)^2 + k  ->  x^2 + bx + c
        return _check_fields(ctx, [b, c])
    p = b / (2 * a)
    k = c - a * p * p
    if kind in ('plus', 'minus'):
        if a != 1:
            return Verdict(False, f'kind {kind} used but the leading coefficient is {a}')
        want_kind = 'minus' if p < 0 else 'plus'
        if kind != want_kind:
            return Verdict(False, f'kind {kind!r} but (x {"-" if p < 0 else "+"} {abs(p)})^2 needs {want_kind!r}')
        return _check_fields(ctx, [abs(p), k])
    if kind == 'scaled':
        # y = a((x + p)^2 + k): the answer boxes put k inside the bracket
        return _check_fields(ctx, [a, p, k / a])
    raise Cannot(f'unknown completed-square kind {kind!r}')


def _check_fields(ctx, vals):
    f = str(ctx.key).split('|')[1:]
    if len(f) != len(vals):
        return Verdict(False, f'key {ctx.key!r} has {len(f)} values, expected {len(vals)}')
    for g, e in zip(f, vals):
        v = read_val(g)
        if v is None or not equivalent(v, sympy.nsimplify(e)):
            return Verdict(False, f'key {ctx.key!r} but recomputed {[fmt(sympy.nsimplify(e)) for e in vals]}')
    return Verdict(True)


@task('solve_system_nonlinear')
def t_system_nonlinear(ctx, **kw):
    pairs = [split_relations(s)[0] for s in eq_segments(ctx)]
    exprs = [expr(a) - expr(b) for a, b in pairs]
    names = sorted({s.name for e in exprs for s in e.free_symbols})
    if names != ['x', 'y']:
        raise Cannot(f'expected unknowns x and y, found {names}')
    x, y = sym('x'), sym('y')
    sols = sympy.solve(exprs, [x, y], dict=True)
    sols = [s for s in sols if all(v.is_real is not False for v in s.values())]
    if not sols:
        return Verdict(False, 'the system has no real solutions')
    sols.sort(key=lambda d: float(d[x]))
    return judge(ctx, 'pairs', [(d[x], d[y]) for d in sols])


@task('first_step')
def t_first_step(ctx, **kw):
    """To make x the subject of y = m x + c, the first step is to subtract c (undo the addition first)."""
    eqs = eq_segments(ctx)
    if len(eqs) != 1:
        raise Cannot(f'expected one formula, found {eqs}')
    a, b = split_relations(eqs[0])[0]
    x = sym(subject_of(ctx))
    rhs = sympy.Poly(sympy.expand(expr(b)), x)
    if rhs.degree() != 1:
        raise Cannot('not a linear formula')
    m, c = rhs.all_coeffs()
    want = f'subtract {abs(c)} from both sides' if c > 0 else f'add {abs(c)} to both sides'
    return judge_text(ctx, want)


@solver('linear_system_2')
def s_linear_system_2(a1, b1, c1, a2, b2, c2):
    """a1 x + b1 y = c1 and a2 x + b2 y = c2: returns [x, y]."""
    a1, b1, c1, a2, b2, c2 = (Fraction(str(v)) for v in (a1, b1, c1, a2, b2, c2))
    det = a1 * b2 - a2 * b1
    if det == 0:
        raise Cannot('the two equations are parallel or identical')
    return [(c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det]


@task('keyed_text')
def t_keyed_text(ctx, text='', drawn=None, **kw):
    """Conceptual multiple choice: the keyed option must read exactly ``text``.

    ``drawn`` ties the wording to the graph that is shown: 'parallel' (two parallel distinct lines), 'cross'
    (two lines meeting at the marked point) or 'tangent' (the line touches the parabola once).
    """
    out = []
    if drawn == 'parallel':
        d = _drawn(ctx, 'lines')
        if d['m1'] != d['m2'] or d['c1'] == d['c2']:
            out.append(Verdict(False, 'the question says the lines are parallel but the drawn lines are not'))
    elif drawn == 'cross':
        d = _drawn(ctx, 'lines')
        out += _drawn_checks(ctx, d)
        if _drawn_lines_cross(d) is None:
            out.append(Verdict(False, 'the question says the lines cross but the drawn lines are parallel'))
    elif drawn == 'tangent':
        d = _drawn(ctx, 'parabola')
        if len(set(_parabola_roots(d))) != 1:
            out.append(Verdict(False, 'the question says the line is a tangent but it does not touch the parabola once'))
    return out + judge_text(ctx, text)


# ───────────────────────────── completing the square: small questions ─────────────────────────────

def _quad_in_x(text):
    """sympy quadratic in x for a segment (a leading ``y =`` or ``p =`` is dropped), or None."""
    t = re.sub(r'^\s*[a-zρθ]\s*=\s*', '', text)
    t = re.sub(r'\s*\+\s*\.\.\.\s*$', '', t)             # "x^2 + 8x + ..." is a quadratic with the constant left out
    if re.search(r'[=<>]', t):
        return None
    try:
        e = sympy.expand(expr(t))
    except Cannot:
        return None
    x = sym('x')
    if e.free_symbols != {x} or sympy.Poly(e, x).degree() != 2:
        return None
    return e


def _the_quad(ctx, which=0):
    found = [(s, e) for s in ctx.segs for e in [_quad_in_x(s)] if e is not None]
    if len(found) <= which:
        raise Cannot(f'no quadratic in x found in {ctx.segs}')
    return found[which]


@task('cts_half')
def t_cts_half(ctx, **kw):
    """p in (x + p)^2 + ... for the quadratic shown (a monic quadratic: half the x coefficient)."""
    _, e = _the_quad(ctx)
    a, b, c = sympy.Poly(e, sym('x')).all_coeffs()
    if a != 1:
        raise Cannot('not monic')
    return judge(ctx, 'val', b / 2)


@task('cts_square_the_half')
def t_cts_square_the_half(ctx, **kw):
    """The number subtracted when building (x + p)^2 from x^2 + 2px is p^2."""
    s, e = _the_quad(ctx)
    a, b, c = sympy.Poly(e, sym('x')).all_coeffs()
    return judge(ctx, 'val', (b / 2) ** 2)


@task('cts_missing_constant')
def t_cts_missing_constant(ctx, **kw):
    """x^2 + bx + c becomes the perfect square (x + p)^2: c = p^2."""
    x, c = sym('x'), sym('c')
    exprs = [(s, expr(s)) for s in ctx.segs if not re.search(r'[=<>]', s)]
    withc = [e for s, e in exprs if c in e.free_symbols]
    square = [e for s, e in exprs if c not in e.free_symbols and e.free_symbols == {x}]
    if len(withc) != 1 or len(square) != 1:
        raise Cannot(f'expected one expression with c and one square, found {ctx.segs}')
    coeffs = sympy.Poly(sympy.expand(withc[0] - square[0]), x).coeffs()
    sols = sympy.solve(coeffs, c)
    if not isinstance(sols, dict) or c not in sols:
        return Verdict(False, 'no value of c makes the expression the stated perfect square')
    return judge(ctx, 'val', sols[c])


@task('min_point')
def t_min_point(ctx, **kw):
    """Turning point of y = a(x + p)^2 + k, or of any quadratic, as (x, y)."""
    _, e = _the_quad(ctx)
    x = sym('x')
    a, b, c = sympy.Poly(e, x).all_coeffs()
    if a < 0 and re.search(r'minimum', ctx.low):
        return Verdict(False, 'the question says minimum but the graph opens downwards')
    xv = -b / (2 * a)
    return judge(ctx, 'tuple', [xv, e.subs(x, xv)])


@task('extremum_value')
def t_extremum_value(ctx, **kw):
    """Greatest or least value of a quadratic, as the question asks."""
    _, e = _the_quad(ctx)
    x = sym('x')
    a, b, c = sympy.Poly(e, x).all_coeffs()
    if re.search(r'maximum|greatest|largest', ctx.low) and a > 0:
        return Verdict(False, 'the question asks for a maximum but the parabola opens upwards')
    if re.search(r'minimum|least|smallest', ctx.low) and a < 0:
        return Verdict(False, 'the question asks for a minimum but the parabola opens downwards')
    return judge(ctx, 'val', e.subs(x, -b / (2 * a)))


@task('show_that_square')
def t_show_that_square(ctx, **kw):
    """Show x^2 + bx + q = (x + p)^2 + k: the two expansion steps are expand((x+p)^2) and expand((x+p)^2 + k)."""
    x = sym('x')
    quads = [(s, e) for s in ctx.segs for e in [_quad_in_x(s)] if e is not None]
    if len(quads) != 2:
        raise Cannot(f'expected two forms, found {ctx.segs}')
    plain_form = next(((s, e) for s, e in quads if '(' not in s), None)
    square_form = next(((s, e) for s, e in quads if '(' in s), None)
    if not plain_form or not square_form:
        raise Cannot('cannot tell the plain form from the completed-square form')
    if sympy.expand(plain_form[1] - square_form[1]) != 0:
        return Verdict(False, 'the two forms in the question are not equal')
    m = re.match(r'\s*(\(\s*x\s*[+-]\s*\d+\s*\)\s*\^\s*2)', square_form[0])
    if not m:
        raise Cannot('cannot find the squared bracket')
    f = _fields(ctx)
    if len(f) != 2:
        return Verdict(False, f'key has {len(f)} steps, expected 2')
    want = [sympy.expand(expr(m.group(1))), square_form[1]]
    out = []
    for g, w in zip(f, want):
        v = read_val(g)
        if v is None or not equivalent(v, w):
            out.append(Verdict(False, f'step {g!r} but recomputed {w}'))
    return out or [Verdict(True)]


@task('one_root_mcq')
def t_one_root_mcq(ctx, **kw):
    """"One solution is": exactly the keyed option is a root of the equation shown."""
    lhs, rhs = the_equation(ctx)
    x = one_var(lhs - rhs)
    roots = real_solutions(lhs - rhs, x)

    def pred(text):
        v = read_val(text)
        return v is not None and any(equivalent(v, r) for r in roots)
    return judge_pred(ctx, pred, 'is a root')


@task('min_x')
def t_min_x(ctx, **kw):
    """x-coordinate of the turning point of the quadratic shown."""
    _, e = _the_quad(ctx)
    a, b, c = sympy.Poly(e, sym('x')).all_coeffs()
    return judge(ctx, 'val', -b / (2 * a))


@task('expand_const')
def t_expand_const(ctx, **kw):
    """Constant term after expanding the first quadratic shown."""
    _, e = _the_quad(ctx)
    return judge(ctx, 'val', sympy.Poly(e, sym('x')).all_coeffs()[-1])


# ───────────────────────────── a parabola and a line ─────────────────────────────

def _equations(ctx):
    """(assignments, [expr = lhs - rhs]) for the equations shown: ``v = number`` pulls out as a given value."""
    assigns, others = split_assignments([s for s in ctx.segs if '=' in s and not re.search(r'[<>]', s)])
    eqs, stated, lone = [], [], []
    for s in others:
        parts, ops = split_relations(s)
        if ops != ['=']:
            continue
        try:
            e = expr(parts[0]) - expr(parts[1])
        except Cannot:
            continue
        if re.fullmatch(_VAR, parts[0].strip()):
            eqs.append(e)
            lone.append((sym(parts[0].strip()), expr(parts[1])))
        else:
            stated.append(e)
    ctx.stated_quads = stated
    ctx.lone = lone
    return assigns, eqs


def _stated_quadratics_ok(ctx, eqs):
    """Any quadratic the question states (\"show that ... gives ...\") must be the substituted equation exactly."""
    out = []
    lone = getattr(ctx, 'lone', [])
    if len(lone) != 2:
        return out
    x = sym('x')
    curve, line = sorted((r for _, r in lone), key=lambda e: -sympy.Poly(sympy.expand(e), x).degree())
    want = sympy.expand(curve - line)
    for q in getattr(ctx, 'stated_quads', []):
        got = sympy.expand(q)
        if sympy.expand(got - want) != 0 and sympy.expand(got + want) != 0:
            out.append(Verdict(False, f'the question states {fmt(got)} = 0 but substituting gives {fmt(want)} = 0'))
        elif sympy.expand(got - want) != 0:
            out.append(Verdict(False, f'the question states {fmt(got)} = 0 but substituting gives {fmt(want)} = 0 (signs differ)'))
    return out


def _real_system(eqs, names, ctx=None):
    lone = getattr(ctx, 'lone', None)
    if lone and len(lone) == 2 and lone[0][0] == lone[1][0] and len(names) == 2:
        v = lone[0][0]
        xs = [sym(n) for n in names if n != v.name]
        if len(xs) == 1:
            x = xs[0]
            roots = real_solutions(lone[0][1] - lone[1][1], x)
            return [{x: r, v: lone[0][1].subs(x, r)} for r in roots]
    syms = [sym(n) for n in names]
    sols = sympy.solve(eqs, syms, dict=True)
    return [s for s in sols if all(v.is_real is not False for v in s.values())]


def _curve_and_line(ctx):
    assigns, eqs = _equations(ctx)
    if len(eqs) != 2:
        raise Cannot(f'expected two equations, found {len(eqs)}')
    names = sorted({s.name for e in eqs for s in e.free_symbols} - {s.name for s in assigns})
    if len(names) != 2:
        raise Cannot(f'expected two unknowns, found {names}')
    return assigns, eqs, names


@task('qsim_solve')
def t_qsim_solve(ctx, **kw):
    """Both intersection points, smaller x first, as the answer boxes (x1, y1, x2, y2) expect."""
    _, eqs, names = _curve_and_line(ctx)
    sols = _real_system(eqs, names, ctx)
    x, y = sym('x'), sym('y')
    sols.sort(key=lambda d: float(d[x]))
    if len(sols) != 2:
        return Verdict(False, f'the system has {len(sols)} real solutions, the answer boxes expect two')
    return _stated_quadratics_ok(ctx, eqs) + judge(ctx, 'tuple', [sols[0][x], sols[0][y], sols[1][x], sols[1][y]])


@task('qsim_find_y')
def t_qsim_find_y(ctx, **kw):
    assigns, eqs = _equations(ctx)
    if len(assigns) != 1 or len(ctx.lone) != 2:
        raise Cannot('expected two equations and one given value')
    ys = [sympy.expand(r.subs(assigns)) for _, r in ctx.lone]
    if ys[0] != ys[1]:
        return Verdict(False, f'the given value does not satisfy both equations (y would be {ys})')
    return judge(ctx, 'val', ys[0])


@task('qsim_x_values')
def t_qsim_x_values(ctx, **kw):
    """All values of the named unknown (x, or t in the word problem) where the curve meets the line."""
    _, eqs, names = _curve_and_line(ctx)
    m = re.search(r'values? of\s+([a-zρθ])\b|solve for\s+([a-zρθ])\b', ctx.low)
    var = (m.group(1) or m.group(2)) if m else 'x'
    sols = _real_system(eqs, names, ctx)
    return judge(ctx, 'set', [d[sym(var)] for d in sols])


@task('qsim_count')
def t_qsim_count(ctx, **kw):
    """Number of real intersections; a stated discriminant is checked too."""
    _, eqs, names = _curve_and_line(ctx)
    sols = _real_system(eqs, names, ctx)
    bad = _stated_quadratics_ok(ctx, eqs)
    if bad:
        return bad
    d = re.search(r'δ\s*=\s*(-?\d+)', ctx.low) or re.search(r'discriminant\s*(?:is|=)\s*(-?\d+)', ctx.low)
    if d:
        x, y = sym('x'), sym('y')
        quad = sympy.Poly(sympy.expand(ctx.lone[0][1] - ctx.lone[1][1]), x)
        a, b, c = quad.all_coeffs()
        if b * b - 4 * a * c != int(d.group(1)):
            return Verdict(False, f'stated discriminant {d.group(1)} but recomputed {b * b - 4 * a * c}')
    return judge(ctx, 'val', sympy.Integer(len(sols)))


def _eq_diff_expr(text):
    """lhs - rhs of the equation written in ``text`` (None if it is not an equation)."""
    try:
        t = tex_to_text(text).lower()
        parts, ops = split_relations(t)
        if ops != ['=']:
            return None
        return expr(parts[0]) - expr(parts[1])
    except Cannot:
        return None


@task('substituted_equation')
def t_substituted_equation(ctx, **kw):
    """The quadratic in x after substituting the line into y = x^2 (up to a constant multiple)."""
    assigns, eqs = _equations(ctx)
    x = sym('x')
    if len(ctx.lone) != 2:
        raise Cannot('expected y = ... twice')
    want = sympy.Poly(sympy.expand(ctx.lone[0][1] - ctx.lone[1][1]), x)
    w = want.all_coeffs()

    def pred(text):
        e = _eq_diff_expr(text)
        if e is None or e.free_symbols != {x}:
            return False
        got = sympy.Poly(sympy.expand(e), x).all_coeffs()
        if len(got) != len(w):
            return False
        ratio = got[0] / w[0]
        return ratio != 0 and all(g == ratio * c for g, c in zip(got, w))
    return judge_pred(ctx, pred, 'is the substituted equation')


@task('point_on_both')
def t_point_on_both(ctx, **kw):
    """Exactly the keyed option is a point satisfying both equations."""
    assigns, eqs = _equations(ctx)
    x, y = sym('x'), sym('y')

    def pred(text):
        pc = read_pieces('tuple', text)
        if len(pc) != 2:
            return False
        vx, vy = read_val(pc[0]), read_val(pc[1])
        return vx is not None and vy is not None and all(sympy.expand(e.subs({x: vx, y: vy})) == 0 for e in eqs)
    return judge_pred(ctx, pred, 'lies on both')


@task('x_root_of_system')
def t_x_root_of_system(ctx, **kw):
    """"One value of x is": exactly the keyed option is an x-coordinate of a solution."""
    _, eqs, names = _curve_and_line(ctx)
    xs = [d[sym('x')] for d in _real_system(eqs, names, ctx)]

    def pred(text):
        v = read_val(text)
        return v is not None and any(equivalent(v, r) for r in xs)
    return judge_pred(ctx, pred, 'is an x-value of a solution')


# ───────────────────────────── graphs drawn by the generator ─────────────────────────────

def _drawn(ctx, kind):
    got = [d for d in getattr(ctx, 'drawn', []) if d.get('kind') == kind]
    if not got:
        raise Cannot(f'no drawn {kind} was recorded for this question')
    return got[-1]


def _line_y(m, c, x):
    return sympy.Integer(m) * x + sympy.Integer(c)


def _drawn_lines_cross(d):
    m1, c1, m2, c2 = (sympy.Integer(d[k]) for k in ('m1', 'c1', 'm2', 'c2'))
    if m1 == m2:
        return None
    x = (c2 - c1) / (m1 - m2)
    return x, m1 * x + c1


def _drawn_checks(ctx, d):
    """Consistency of what is drawn: a marked point must lie on both curves; stated lines must be the drawn ones."""
    out = []
    if d['kind'] == 'lines':
        p = d.get('point')
        if p is not None:
            for i in ('1', '2'):
                if _line_y(d['m' + i], d['c' + i], sympy.Integer(p[0])) != p[1]:
                    out.append(Verdict(False, f'the marked point {tuple(p)} is not on line {i} (y = {d["m" + i]}x + {d["c" + i]})'))
    else:
        for (px, py) in d.get('marks', []):
            if py != px * px or py != d['a'] * px + d['b']:
                out.append(Verdict(False, f'the marked point {(px, py)} is not on both y = x^2 and y = {d["a"]}x + {d["b"]}'))
        # a line written in the question must be the line that is drawn
        x = sym('x')
        for t, r in _text_lines(ctx):
            if sympy.Poly(r, x).degree() == 1 and sympy.expand(r - (d['a'] * x + d['b'])) != 0:
                out.append(Verdict(False, f'the question says y = {fmt(r)} but the line drawn is y = {d["a"]}x + {d["b"]}'))
    return out


def _text_lines(ctx):
    """(var, rhs) for each ``y = ...`` equation in the question text."""
    out = []
    for s in ctx.segs:
        parts, ops = split_relations(s)
        if ops == ['='] and parts[0].strip() == 'y':
            try:
                out.append(('y', expr(parts[1])))
            except Cannot:
                pass
    return out


@task('gsim_point')
def t_gsim_point(ctx, which='cross', **kw):
    """The solution point read off the graph, as (x, y)."""
    if which == 'marked':
        d = _drawn(ctx, 'parabola')
        if not d['marks']:
            raise Cannot('no marked point')
        x, y = d['marks'][0]
        return _drawn_checks(ctx, d) + judge(ctx, 'tuple', [sympy.Integer(x), sympy.Integer(y)])
    d = _drawn(ctx, 'lines')
    cross = _drawn_lines_cross(d)
    if cross is None:
        return Verdict(False, 'the drawn lines are parallel, so there is no point to read')
    return _drawn_checks(ctx, d) + judge(ctx, 'tuple', list(cross))


@task('gsim_y_at_x')
def t_gsim_y_at_x(ctx, **kw):
    d = _drawn(ctx, 'lines')
    assigns, _ = split_assignments(ctx.segs)
    if len(assigns) != 1 or sym('x') not in assigns:
        raise Cannot('expected one given value of x')
    x = assigns[sym('x')]
    ys = [_line_y(d['m1'], d['c1'], x), _line_y(d['m2'], d['c2'], x)]
    if ys[0] != ys[1]:
        return Verdict(False, f'the drawn lines do not meet at x = {x} (y = {ys[0]} and {ys[1]})')
    return _drawn_checks(ctx, d) + judge(ctx, 'val', ys[0])


@task('gsim_x_marked')
def t_gsim_x_marked(ctx, **kw):
    d = _drawn(ctx, 'parabola')
    if not d['marks']:
        raise Cannot('no marked point')
    # the algebra stated in the question (x = r1 or x = r2) must be the two intersections
    roots = sympy.solve(sym('x') ** 2 - d['a'] * sym('x') - d['b'], sym('x'))
    out = _drawn_checks(ctx, d)
    stated = []
    for sg in ctx.segs:
        parts, ops = split_relations(sg)
        if ops == ['='] and parts[0].strip() == 'x':
            stated.append(expr(parts[1]))
    for v in stated:
        if not any(equivalent(v, r) for r in roots):
            out.append(Verdict(False, f'the question says x = {fmt(v)} but the intersections are at x = {roots}'))
    return out + judge(ctx, 'val', sympy.Integer(d['marks'][0][0]))


def _parabola_roots(d):
    x = sym('x')
    return sorted([r for r in sympy.solve(x ** 2 - d['a'] * x - d['b'], x) if r.is_real], key=float)


@task('gsim_count')
def t_gsim_count(ctx, **kw):
    """Number of solutions of what is drawn (two lines, or a parabola and a line)."""
    if any(d.get('kind') == 'parabola' for d in getattr(ctx, 'drawn', [])):
        d = _drawn(ctx, 'parabola')
        n = len(set(_parabola_roots(d)))
    else:
        d = _drawn(ctx, 'lines')
        if d['m1'] != d['m2']:
            n = 1
        else:
            n = 0 if d['c1'] != d['c2'] else None
        if n is None:
            return Verdict(False, 'the two drawn lines are identical')
    return _drawn_checks(ctx, d) + judge(ctx, 'val', sympy.Integer(n))


@task('gsim_both_points')
def t_gsim_both_points(ctx, **kw):
    d = _drawn(ctx, 'parabola')
    roots = _parabola_roots(d)
    if len(roots) != 2:
        return Verdict(False, f'the drawn curve and line meet {len(roots)} times, the answer boxes expect two')
    flat = []
    for r in roots:
        flat += [r, r * r]
    return _drawn_checks(ctx, d) + judge(ctx, 'tuple', flat)


@task('gsim_which_point')
def t_gsim_which_point(ctx, **kw):
    """Labelled points A to D are plotted on the graph: exactly the keyed one is on both lines."""
    d = _drawn(ctx, 'lines')
    plotted = {str(l).upper(): (sympy.Integer(px), sympy.Integer(py)) for l, px, py in d['extra']}
    out = []
    for letter, text in ctx.options:
        pc = read_pieces('tuple', text)
        vals = [read_val(x) for x in pc]
        if len(vals) != 2 or None in vals or letter not in plotted:
            raise Cannot(f'cannot read option {letter}: {text!r}')
        if (vals[0], vals[1]) != plotted[letter]:
            out.append(Verdict(False, f'option {letter} says {text} but the point plotted as {letter} is {tuple(plotted[letter])}'))

    def pred(text):
        pc = read_pieces('tuple', text)
        vx, vy = read_val(pc[0]), read_val(pc[1])
        return all(_line_y(d['m' + i], d['c' + i], vx) == vy for i in ('1', '2'))
    return out + judge_pred(ctx, pred, 'lies on both drawn lines')


def _line_from_text(text):
    """(m, c) of a line written ``y = mx + c``, or None."""
    try:
        t = tex_to_text(text).lower().strip()
    except Cannot:
        return None
    parts, ops = split_relations(t)
    if ops != ['='] or parts[0].strip() != 'y':
        return None
    try:
        e = sympy.expand(expr(parts[1]))
    except Cannot:
        return None
    x = sym('x')
    if e.free_symbols - {x}:
        return None
    pol = sympy.Poly(e, x)
    if pol.degree() > 1:
        return None
    co = pol.all_coeffs()
    return (co[0], co[1]) if len(co) == 2 else (sympy.Integer(0), co[0])


@task('gsim_equations_from_graph')
def t_gsim_equations_from_graph(ctx, **kw):
    """Options are pairs of lines: exactly the keyed option is the pair that is drawn."""
    d = _drawn(ctx, 'lines')
    drawn = {(sympy.Integer(d['m1']), sympy.Integer(d['c1'])), (sympy.Integer(d['m2']), sympy.Integer(d['c2']))}

    def pred(text):
        t = text.replace('\\(', ' ').replace('\\)', ' ')
        segs = [s for s in re.split(r'\s+and\s+', t) if s.strip()]
        lines = {_line_from_text(s) for s in segs}
        if len(lines) != 2 or None in lines:
            raise Cannot(f'cannot read two lines in {text!r}')
        return lines == drawn
    return _drawn_checks(ctx, d) + judge_pred(ctx, pred, 'is the pair of lines drawn')


@task('intersect_lines_text')
def t_intersect_lines_text(ctx, **kw):
    lines = _text_lines(ctx)
    if len(lines) != 2:
        raise Cannot(f'expected two lines, found {len(lines)}')
    x = sym('x')
    sols = sympy.solve(lines[0][1] - lines[1][1], x)
    if len(sols) != 1:
        return Verdict(False, 'the two lines do not meet at exactly one point')
    return judge(ctx, 'tuple', [sols[0], lines[0][1].subs(x, sols[0])])


@task('count_lines_text')
def t_count_lines_text(ctx, **kw):
    lines = _text_lines(ctx)
    if len(lines) != 2:
        raise Cannot(f'expected two lines, found {len(lines)}')
    x = sym('x')
    diff = sympy.expand(lines[0][1] - lines[1][1])
    n = 1 if sympy.Poly(diff, x).degree() == 1 else (0 if diff != 0 else None)
    if n is None:
        return Verdict(False, 'the two lines are identical')
    return judge(ctx, 'val', sympy.Integer(n))


@task('gsim_context')
def t_gsim_context(ctx, **kw):
    """Two cost plans written in the question and drawn on the graph: the number of items where the costs match."""
    d = _drawn(ctx, 'lines')
    fees = [int(m.group(1) or 0) for m in re.finditer(r'(?:a £(\d+)|no) (?:setup|joining|delivery) fee', ctx.low)]
    rates = [int(v) for v in re.findall(r'£(\d+) per', ctx.low)]
    if len(fees) != 2 or len(rates) != 2:
        raise Cannot(f'cannot read two fees and two rates from the question: {fees}, {rates}')
    text_lines = [(sympy.Integer(rates[0]), sympy.Integer(fees[0])), (sympy.Integer(rates[1]), sympy.Integer(fees[1]))]
    drawn = [(sympy.Integer(d['m1']), sympy.Integer(d['c1'])), (sympy.Integer(d['m2']), sympy.Integer(d['c2']))]
    out = _drawn_checks(ctx, d)
    if text_lines != drawn:
        out.append(Verdict(False, f'the question describes {text_lines} (rate, fee) but the graph draws {drawn}'))
    cross = _drawn_lines_cross({'m1': rates[0], 'c1': fees[0], 'm2': rates[1], 'c2': fees[1]})
    if cross is None:
        return out + [Verdict(False, 'the two plans never cost the same')]
    return out + judge(ctx, 'val', cross[0])


# ───────────────────────────── functions ─────────────────────────────

_DEF = re.compile(r'^\s*([fgh])\(x\)\s*=\s*(.+)$')
_CALL = re.compile(r'(?<![\w^])([fgh])\(((?:[^()]|\([^()]*\))*)\)')


def _fn_defs(ctx):
    defs = {}
    for s in ctx.segs:
        m = _DEF.match(s)
        if m:
            try:
                rhs = expr(m.group(2))
            except Cannot:
                continue
            if sym('x') in rhs.free_symbols:
                defs[m.group(1)] = rhs
    if not defs:
        raise Cannot('no function rule f(x) = ... found')
    return defs


def _fn_apply(defs, text):
    """Value of an expression built from function calls such as ``f(g(3)) + f(0)``."""
    x = sym('x')
    text = text.lower()
    for _ in range(12):
        m = _CALL.search(text)
        if not m:
            break
        name, arg = m.group(1), m.group(2)
        if name not in defs:
            raise Cannot(f'function {name} is not defined in the question')
        val = defs[name].subs(x, _fn_apply(defs, arg))
        text = text[:m.start()] + '(' + fmt(sympy.expand(val)) + ')' + text[m.end():]
    return expr(text)


def _fn_asks(ctx):
    return [s for s in ctx.segs if not _DEF.match(s) and _CALL.search(s) and not re.search(r'[=<>]', s)
            and '^(-1)' not in s]


@task('fn_eval')
def t_fn_eval(ctx, **kw):
    defs = _fn_defs(ctx)
    asks = _fn_asks(ctx)
    if not asks:
        raise Cannot('nothing to evaluate')
    vals = [sympy.expand(_fn_apply(defs, a)) for a in asks]
    return judge(ctx, 'val', vals[0]) if len(vals) == 1 else judge(ctx, 'tuple', vals)


@task('fn_inverse')
def t_fn_inverse(ctx, **kw):
    defs = _fn_defs(ctx)
    x, y = sym('x'), sym('y')
    sols = sympy.solve(sympy.Eq(y, defs['f']), x)
    if len(sols) != 1:
        raise Cannot('f has no unique inverse')
    return judge(ctx, 'val', sols[0].subs(y, x))


@task('fn_solve')
def t_fn_solve(ctx, many=False, **kw):
    defs = _fn_defs(ctx)
    target = None
    for s in ctx.segs:
        m = re.match(r'^\s*f\(x\)\s*=\s*(-?[\d.]+)\s*$', s)
        if m:
            target = sympy.Rational(m.group(1))
    if target is None:
        raise Cannot('no equation f(x) = number in the question')
    sols = real_solutions(defs['f'] - target, sym('x'))
    if many:
        return judge(ctx, 'set', sols)
    if len(sols) != 1:
        return Verdict(False, f'f(x) = {target} has {len(sols)} solutions')
    return judge(ctx, 'val', sols[0])


@task('fn_inverse_eval')
def t_fn_inverse_eval(ctx, **kw):
    defs = _fn_defs(ctx)
    m = re.search(r'output is (-?\d+)', ctx.low)
    if not m:
        raise Cannot('no output value in the question')
    sols = real_solutions(defs['f'] - int(m.group(1)), sym('x'))
    if len(sols) != 1:
        return Verdict(False, 'the output does not come from exactly one input')
    return judge(ctx, 'val', sols[0])


_OPS = {'×': lambda a, b: a * b, 'x': lambda a, b: a * b, '÷': lambda a, b: a / b, '+': lambda a, b: a + b,
        '-': lambda a, b: a - b, '−': lambda a, b: a - b}
_INVERSE = {'×': '÷', 'x': '÷', '÷': '×', '+': '-', '-': '+', '−': '+'}


@task('fn_machine')
def t_fn_machine(ctx, **kw):
    """A function machine of two operations, applied to an input or run backwards from an output."""
    ops = re.findall(r'applies\s+([×x÷+\-−])\s*(\d+)\s+then\s+([×x÷+\-−])\s*(\d+)', ctx.low)
    if len(ops) != 1:
        raise Cannot('cannot read the two operations of the machine')
    o1, n1, o2, n2 = ops[0]
    inp = re.search(r'input is\s+(-?\d+)', ctx.low)
    out = re.search(r'output is\s+(-?\d+)', ctx.low)
    if inp and not out:
        v = sympy.Integer(int(inp.group(1)))
        v = _OPS[o2](_OPS[o1](v, int(n1)), int(n2))
    elif out and not inp:
        v = sympy.Integer(int(out.group(1)))
        v = _OPS[_INVERSE[o1]](_OPS[_INVERSE[o2]](v, int(n2)), int(n1))
    else:
        raise Cannot('cannot tell whether an input or an output is given')
    return judge(ctx, 'val', v)


@task('fn_excluded')
def t_fn_excluded(ctx, **kw):
    defs = _fn_defs(ctx)
    _, den = sympy.fraction(sympy.together(defs['f']))
    sols = real_solutions(den, sym('x'))
    if len(sols) != 1:
        return Verdict(False, f'the denominator vanishes at {sols}')
    return judge(ctx, 'val', sols[0])


@task('fn_notation_meaning')
def t_fn_notation_meaning(ctx, **kw):
    m = next((re.fullmatch(r'f\((\d+)\)', s.strip()) for s in ctx.segs if re.fullmatch(r'f\((\d+)\)', s.strip())), None)
    if not m:
        raise Cannot('no f(n) in the question')
    return judge_text(ctx, f'the output of f when the input is {m.group(1)}')


def _fn_fields(ctx, n):
    f = _fields(ctx)
    if len(f) != n:
        raise Cannot(f'expected {n} answer fields, found {len(f)}')
    return f


def _field_is(g, want):
    v = read_val(g)
    return v is not None and equivalent(v, sympy.nsimplify(want) if not isinstance(want, sympy.Basic) else want)


@task('fn_multipart_comp')
def t_fn_multipart_comp(ctx, **kw):
    """a) f(g(x))  b) f(g(n))  c) f^-1(x)"""
    defs = _fn_defs(ctx)
    x, y = sym('x'), sym('y')
    f = _fn_fields(ctx, 3)
    asks = [s for s in ctx.segs if not _DEF.match(s) and _CALL.search(s)]
    num = next((s for s in asks if re.fullmatch(r'f\(g\(-?\d+\)\)', s.strip())), None)
    if num is None:
        raise Cannot('no f(g(n)) part')
    want = [sympy.expand(_fn_apply(defs, 'f(g(x))')), _fn_apply(defs, num), sympy.solve(sympy.Eq(y, defs['f']), x)[0].subs(y, x)]
    out = []
    for i, (g, w) in enumerate(zip(f, want)):
        if not _field_is(g, w):
            out.append(Verdict(False, f'part {"abc"[i]}: key {g!r} but recomputed {fmt(w)}'))
    return out or [Verdict(True)]


@task('fn_multipart_quadratic')
def t_fn_multipart_quadratic(ctx, **kw):
    """a) minimum point  b) f(n)  c) line of symmetry (the x-value)"""
    defs = _fn_defs(ctx)
    x = sym('x')
    f = _fn_fields(ctx, 3)
    e = sympy.expand(defs['f'])
    a, b, c = sympy.Poly(e, x).all_coeffs()
    if a <= 0:
        raise Cannot('not an upward parabola')
    xv = -b / (2 * a)
    yv = e.subs(x, xv)
    ask = next((s for s in ctx.segs if re.fullmatch(r'f\(-?\d+\)', s.strip())), None)
    if ask is None:
        raise Cannot('no f(n) part')
    pc = f[0].split('|')
    out = []
    if len(pc) != 2 or not (_field_is(pc[0], xv) and _field_is(pc[1], yv)):
        out.append(Verdict(False, f'part a: key {f[0]!r} but the minimum is ({fmt(xv)}, {fmt(yv)})'))
    if not _field_is(f[1], _fn_apply(defs, ask)):
        out.append(Verdict(False, f'part b: key {f[1]!r} but recomputed {fmt(_fn_apply(defs, ask))}'))
    if not _field_is(re.sub(r'^\s*x\s*=\s*', '', f[2]), xv):
        out.append(Verdict(False, f'part c: key {f[2]!r} but the line of symmetry is x = {fmt(xv)}'))
    return out or [Verdict(True)]


@task('fn_multipart_domain')
def t_fn_multipart_domain(ctx, **kw):
    """a) excluded input  b) reason (multiple choice)  c) f(n)"""
    defs = _fn_defs(ctx)
    f = _fn_fields(ctx, 3)
    _, den = sympy.fraction(sympy.together(defs['f']))
    sols = real_solutions(den, sym('x'))
    ask = next((s for s in ctx.segs if re.fullmatch(r'f\(-?\d+\)', s.strip())), None)
    if len(sols) != 1 or ask is None:
        raise Cannot('cannot find the excluded value and the f(n) part')
    out = []
    if not _field_is(f[0], sols[0]):
        out.append(Verdict(False, f'part a: key {f[0]!r} but the excluded input is {sols[0]}'))
    opts = (ctx.p.get('answer_field_options') or [None, None])[1] or []
    letter = f[1].strip().upper()
    idx = 'ABCDEFGH'.find(letter)
    if idx < 0 or idx >= len(opts) or tex_to_text(str(opts[idx])).strip().lower() != 'division by zero is undefined':
        out.append(Verdict(False, f'part b: key {f[1]!r} does not point at "Division by zero is undefined" in {opts}'))
    if not _field_is(f[2], _fn_apply(defs, ask)):
        out.append(Verdict(False, f'part c: key {f[2]!r} but recomputed {fmt(_fn_apply(defs, ask))}'))
    return out or [Verdict(True)]


# ───────────────────────────── algebraic proof ─────────────────────────────

_PVARS = 'nmkj'
_RANGE = range(-12, 13)


def _is_prime(n):
    return n > 1 and all(n % p for p in range(2, int(n ** 0.5) + 1))


def _property_holds(e, var, kind, n=None):
    """Whether the integer expression ``e`` in ``var`` is always even / odd / a multiple of ``n`` / prime."""
    for v in _RANGE:
        val = e.subs(var, v)
        if not val.is_Integer:
            raise Cannot(f'{e} is not an integer expression')
        val = int(val)
        if kind == 'even' and val % 2:
            return False
        if kind == 'odd' and val % 2 == 0:
            return False
        if kind == 'mult' and val % n:
            return False
        if kind == 'prime' and not _is_prime(val):
            return False
    return True


def _claim_of(text):
    low = text.lower()
    m = re.search(r'always\s+(even|odd)', low)
    if m:
        return m.group(1), None
    m = re.search(r'multiple of\s+(\d+)', low)
    if m:
        return 'mult', int(m.group(1))
    return None, None


def _proof_subject(ctx):
    """(variable, expression, claim kind, claim number) for the statement to be proved."""
    kind, num = _claim_of(ctx.low)
    letters = [v for v in _PVARS if any(re.search(rf'\b{v}\b', s) for s in ctx.segs)]
    if not letters:
        raise Cannot('no variable in the question')
    var = sym(letters[0])
    m = re.search(r'(\d+)\s+consecutive integers', ctx.low)
    if m:
        total = sum((var + i for i in range(int(m.group(1)))), sympy.Integer(0))
        return var, sympy.expand(total), kind, num
    cands = []
    for s in ctx.segs:
        if re.fullmatch(rf'[{_PVARS}]', s.strip()) or '...' in s or re.search(r'[=<>]', s):
            continue
        try:
            e = expr(s)
        except Cannot:
            continue
        if e.free_symbols == {var}:
            cands.append(e)
    if not cands:
        raise Cannot('no expression to prove a property of')
    return var, cands[0], kind, num


_MATHY = re.compile(r'^[0-9nmkj+\-*/^()\[\].,]+$')


def _norm_step(text):
    t = text.replace('²', '^2').replace('³', '^3').replace('×', '*').replace('−', '-').replace('÷', '/')
    t = re.sub(r'(?<=[0-9nmkj\)])\s*\[', '*[', t)
    return t


def _step_equations(text):
    """(lhs, rhs) text pairs for each ``a = b`` in a proof step where both sides are plain algebra.

    A left side written as the word "Sum" (or "sum of 8 consecutive integers") comes back as ``None``: the caller
    substitutes the quantity the question is about.
    """
    t = _norm_step(text)
    out = []
    for m in re.finditer(r'=', t):
        left = t[:m.start()].split()
        right = t[m.end():].split()
        lt, rt = [], []
        stop = ''
        for tok in reversed(left):
            if tok[-1] in ',;:' and lt:
                stop = ','
                break
            tok = tok.rstrip(',;:')
            if not _MATHY.match(tok):
                stop = tok.lower()
                break
            lt.append(tok)
        lhs_text = ' '.join(reversed(lt))
        if stop in ('write', 'let', 'where', 'suppose', 'say', 'put', 'set') and re.fullmatch(r'[a-z]', lhs_text):
            continue                        # a definition such as "write n = 2j", not a claim
        for tok in right:
            tok2 = tok.rstrip('.,;:')
            if not _MATHY.match(tok2):
                break
            rt.append(tok2)
            if tok2 != tok:
                break
        rhs = ' '.join(rt)
        if not lt and (stop == 'sum' or re.search(r'sum of [^=]*$', t[:m.start()].lower())):
            lhs_text = None
        elif not lhs_text:
            continue
        if rhs:
            out.append((lhs_text, rhs))
    return out


def _bracket(e):
    return e.replace('[', '(').replace(']', ')')


def _eq_status(lhs, rhs):
    """True / False / None (unreadable) for the identity lhs = rhs."""
    try:
        a, b = expr(_bracket(lhs)), expr(_bracket(rhs))
    except Cannot:
        return None
    return sympy.expand(a - b) == 0


def _clash(text):
    """'write n = 2n' style substitutions that reuse the variable they define."""
    t = _norm_step(text)
    for m in re.finditer(r'\bwrite\s+([a-z])\s*=\s*([^;,.]*)', t):
        if re.search(rf'\b\d*{m.group(1)}\b', m.group(2)):
            return m.group(0)
    return None


def _product_claims(text, subject, var):
    """Case-split steps for a product that is even: "If n is even, write n = 2j; then the product is ..." and
    "If (n + 5) is even, the product is n * 2j for some integer j"."""
    out = []
    j = sym('j')
    t = _norm_step(text).lower().replace('\u00d7', '*')
    m = re.search(r'if \(?([a-z])\)? is even, write ([a-z]) = ([^;]+); then the product is ([^.]+?)\.?$', t)
    try:
        if m and m.group(1) == m.group(2) == var.name:
            w, prod = expr(m.group(3)), expr(m.group(4).replace(' ', ''))
            if sympy.expand(prod.subs(var, w) - subject.subs(var, w)) != 0:
                out.append(Verdict(False, f'keyed step: the product is not {m.group(4)} when {var} = {m.group(3)}: "{text}"'))
        m = re.search(r'if \(([^()]+)\) is even, the product is ([^.]+?) for some integer', t)
        if m:
            cond, prod = expr(m.group(1)), expr(m.group(2))
            sol = sympy.solve(cond - 2 * j, var)
            if len(sol) == 1 and sympy.expand(prod.subs(var, sol[0]) - subject.subs(var, sol[0])) != 0:
                out.append(Verdict(False, f'keyed step: the product is not {m.group(2)} when ({m.group(1)}) = 2j: "{text}"'))
    except Cannot:
        pass
    return out


@task('ap_proof')
def t_ap_proof(ctx, **kw):
    """A proof_steps question: the statement is true, every equation in the keyed steps is true, and the last
    keyed step concludes the stated property."""
    out = []
    raw = str(ctx.key)
    parts = raw.split('|')
    bank = {str(b.get('id')): str(b.get('text')) for b in (ctx.p.get('answer_step_bank') or [])}
    ids = parts[2:] if parts[0] == 'pick' else parts[1:]
    if not ids or any(i not in bank for i in ids):
        raise Cannot(f'cannot read the keyed steps from {raw!r}')
    required = [bank[i] for i in ids]
    # 1. the statement itself
    eq_seg = next((s for s in ctx.segs if '=' in s and not re.search(r'[<>]', s)), None)
    if eq_seg:
        lhs, rhs = split_relations(eq_seg)[0]
        if not equivalent(sympy.expand(expr(lhs)), sympy.expand(expr(rhs))):
            return [Verdict(False, f'the statement {eq_seg} is not an identity')]
        kind = None
    else:
        var, e, kind, num = _proof_subject(ctx)
        if kind is None:
            raise Cannot('no property to check in the question')
        if not _property_holds(e, var, kind, num):
            return [Verdict(False, f'{fmt(e)} is not always {kind if kind != "mult" else "a multiple of " + str(num)}')]
    # 2. the keyed steps
    subject = None
    if not eq_seg:
        subject = _bracket(fmt(e)).replace('^', '^')
    for text in required:
        for lhs, rhs in _step_equations(text):
            if lhs is None:
                if subject is None:
                    continue
                lhs = subject
            if _eq_status(lhs, rhs) is False:
                out.append(Verdict(False, f'keyed step is false: "{text}" ({lhs} is not equal to {rhs})'))
        c = _clash(text)
        if c:
            out.append(Verdict(False, f'keyed step reuses its own variable: "{c}"'))
    seen = ctx.text.replace(' ', '')
    for text in required:
        if subject is not None:
            out.extend(_product_claims(text, e, var))
    for text in required:
        low = _norm_step(text).lower()
        for m in re.finditer(r'differ by (\d+) \(an? (odd|even) number\)', low):
            if int(m.group(1)) % 2 != (1 if m.group(2) == 'odd' else 0) or m.group(1) not in re.findall(r'\d+', ctx.text):
                out.append(Verdict(False, f'keyed step is false or does not match the question: "{text}"'))
        if re.search(r'bracket|is an integer', low):
            for br in re.findall(r'\(([^()]+)\)', low):
                if not re.search(r'[+\-]', br):
                    continue
                if br.replace(' ', '') not in ''.join(_norm_step(x).lower().replace(' ', '') for x in required[:required.index(text)]) \
                        and br.replace(' ', '') not in seen:
                    out.append(Verdict(False, f'keyed step names a bracket ({br}) that no earlier step produced: "{text}"'))
    if kind in ('even', 'odd'):
        if kind not in required[-1].lower():
            out.append(Verdict(False, f'the last keyed step does not conclude "{kind}": "{required[-1]}"'))
    elif kind == 'mult':
        if f'multiple of {num}' not in required[-1].lower():
            out.append(Verdict(False, f'the last keyed step does not conclude "multiple of {num}": "{required[-1]}"'))
    # 3. a distractor must not be a fully true line of algebra
    for i, t in bank.items():
        if i in ids:
            continue
        stat = [_eq_status(subject if l is None else l, r) for l, r in _step_equations(t) if l is not None or subject]
        if stat and all(s is True for s in stat):
            out.append(Verdict(False, f'distractor "{t}" only contains true equations; a pupil could reasonably use it'))
    return out or [Verdict(True)]


@task('ap_parity_fields')
def t_ap_parity_fields(ctx, **kw):
    """Fields: the simplified sum, then whether it is always even or always odd."""
    f = _fields(ctx)
    if len(f) != 2:
        raise Cannot('expected two fields')
    seg = next((s for s in ctx.segs if '(' in s and not re.search(r'[=<>]', s)), None)
    if seg is None:
        raise Cannot('no expression to simplify')
    e = sympy.expand(expr(seg))
    var = sorted(e.free_symbols, key=lambda s: s.name)[0]
    out = []
    if not _field_is(f[0], e):
        out.append(Verdict(False, f'simplified expression: key {f[0]!r} but recomputed {fmt(e)}'))
    parity = 'even' if _property_holds(e, var, 'even') else ('odd' if _property_holds(e, var, 'odd') else 'neither')
    if f[1].strip().lower() != parity:
        out.append(Verdict(False, f'parity: key {f[1]!r} but {fmt(e)} is always {parity}'))
    return out or [Verdict(True)]


@task('counterexample')
def t_counterexample(ctx, **kw):
    """The keyed whole number is the smallest positive integer for which the stated claim fails."""
    stmt = next((s for s in ctx.segs if re.search(r'is (?:prime|even)|>', s)), None)
    if stmt is None:
        raise Cannot('no statement found')
    n = sym('n')
    low = stmt
    domain_min = 1
    m = re.search(r'for n\s*>\s*(\d+)', low)
    if m:
        domain_min = int(m.group(1)) + 1
    core_text = re.sub(r'\s+for n.*$', '', low)
    if 'is prime' in core_text:
        e = expr(core_text.replace('is prime', '').strip())
        holds = lambda v: _is_prime(int(e.subs(n, v)))
    elif 'is even' in core_text:
        e = expr(core_text.replace('is even', '').strip())
        holds = lambda v: int(e.subs(n, v)) % 2 == 0
    elif '>' in core_text:
        a, b = [expr(x) for x in core_text.split('>')]
        holds = lambda v: a.subs(n, v) > b.subs(n, v)
    else:
        raise Cannot(f'cannot read the statement {stmt!r}')
    fails = [v for v in range(domain_min, 60) if not holds(v)]
    if not fails:
        return Verdict(False, f'no counterexample below 60 for {stmt!r}')
    if not re.search(r'smallest', ctx.low):
        return Verdict(False, 'several whole numbers disprove the statement but the question does not ask for the smallest; '
                       'the answer box accepts only one')
    return judge(ctx, 'val', sympy.Integer(fails[0]))


@task('ap_always')
def t_ap_always(ctx, **kw):
    """Options are expressions: exactly the keyed option is always even (or always odd) for integer n."""
    kind = 'even' if re.search(r'always\s+even', ctx.low) else ('odd' if re.search(r'always\s+odd', ctx.low) else None)
    if kind is None:
        raise Cannot('question names neither even nor odd')
    n = sym('n')

    def pred(text):
        e = read_val(text)
        if e is None:
            raise Cannot(f'cannot read {text!r}')
        return _property_holds(e, n, kind)
    return judge_pred(ctx, pred, f'is always {kind}')


_PROP_PHRASES = [
    (r'^it is always even$', ('even', None)),
    (r'^always even$', ('even', None)),
    (r'^it is always odd$', ('odd', None)),
    (r'^always odd$', ('odd', None)),
    (r'^(?:it is )?always a multiple of (\d+)$', ('mult', 'num')),
    (r'^it is always prime$', ('prime', None)),
]


@task('ap_prop')
def t_ap_prop(ctx, **kw):
    """Options state a property of the expression in the question; exactly the keyed one is true for all integers n."""
    seg = next((s for s in ctx.segs if not re.fullmatch(r'[a-z]', s.strip()) and not re.search(r'[=<>]', s)), None)
    if seg is None:
        raise Cannot('no expression in the question')
    e = expr(seg)
    var = sorted(e.free_symbols, key=lambda s: s.name)[0]

    def pred(text):
        t = tex_to_text(text).strip().lower()
        for pat, (kind, arg) in _PROP_PHRASES:
            m = re.match(pat, t)
            if m:
                return _property_holds(e, var, kind, int(m.group(1)) if arg == 'num' else None)
        raise Cannot(f'cannot read the property {text!r}')
    return judge_pred(ctx, pred, 'is true for every integer')


@task('ap_counter_mcq')
def t_ap_counter_mcq(ctx, **kw):
    """Options claim 'n = k gives n^2 + 1 = V (not prime)': exactly one is a real counterexample."""
    if 'is prime' not in ctx.low:
        raise Cannot('no prime statement')
    stmt = next((s for s in ctx.segs if re.search(r'n\^2', s)), None)
    if stmt is None:
        raise Cannot('no expression in the statement')
    e = expr(stmt.replace('is prime', '').strip())
    n = sym('n')

    def pred(text):
        t = tex_to_text(text).lower()
        m = re.match(r'\s*n\s*=\s*(\d+)\s+gives\s+(.+?)\s*=\s*(\d+)\s*\(not prime\)', t)
        if not m:
            raise Cannot('not a worked counterexample')
        v = int(m.group(1))
        val = int(e.subs(n, v))
        return int(m.group(3)) == val and not _is_prime(val)
    return judge_pred(ctx, pred, 'is a worked counterexample')


# ───────────────────────────── the "graphs" topic: plain-text questions with a drawn graph ─────────────────────────────

def gtext(ctx):
    """The question as plain lowercase text with maths characters flattened (these questions are not wrapped in \\( \\))."""
    t = ctx.text.lower()
    for a, b in (('²', '^2'), ('³', '^3'), ('×', '*'), ('−', '-'), ('‑', '-'), ('–', '-'), ('÷', '/'), (' ', ' ')):
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t)


def _gdrawn(ctx, kind):
    got = [d for d in getattr(ctx, 'drawn', []) if d.get('kind') == kind]
    if not got:
        raise Cannot(f'no drawn {kind} was recorded for this question')
    return got[-1]


def _search(ctx, pattern):
    m = re.search(pattern, gtext(ctx))
    if not m:
        raise Cannot(f'question does not match {pattern!r}')
    return m


@task('gr_quadrant')
def t_gr_quadrant(ctx, **kw):
    m = _search(ctx, r'the point \((-?\d+), (-?\d+)\) is plotted')
    x, y = int(m.group(1)), int(m.group(2))
    out = []
    d = _gdrawn(ctx, 'point')
    if (d['x'], d['y']) != (x, y):
        out.append(Verdict(False, f'the question says ({x}, {y}) but the point drawn is ({d["x"]}, {d["y"]})'))
    if x == 0 or y == 0:
        return out + [Verdict(False, 'the point lies on an axis')]
    quad = {(1, 1): 'i', (-1, 1): 'ii', (-1, -1): 'iii', (1, -1): 'iv'}[(1 if x > 0 else -1, 1 if y > 0 else -1)]
    return out + judge_text(ctx, f'quadrant {quad}')


@task('gr_subst')
def t_gr_subst(ctx, **kw):
    m = _search(ctx, r'for y = (.+?), find y when x = (-?\d+)')
    e = expr(m.group(1))
    return judge(ctx, 'val', e.subs(sym('x'), int(m.group(2))))


def _two_points(ctx):
    m = _search(ctx, r'\((-?\d+),\s*(-?\d+)\) and \((-?\d+),\s*(-?\d+)\)')
    return tuple(int(g) for g in m.groups())


def _segment_checks(ctx, pts):
    d = _gdrawn(ctx, 'segment')
    if (d['x1'], d['y1'], d['x2'], d['y2']) != pts:
        return [Verdict(False, f'the question gives {pts} but the line drawn runs through '
                        f'({d["x1"]}, {d["y1"]}) and ({d["x2"]}, {d["y2"]})')]
    return []


@task('gr_gradient2')
def t_gr_gradient2(ctx, **kw):
    x1, y1, x2, y2 = _two_points(ctx)
    return _segment_checks(ctx, (x1, y1, x2, y2)) + judge(ctx, 'val', sympy.Rational(y2 - y1, x2 - x1))


@task('gr_yint')
def t_gr_yint(ctx, **kw):
    m = _search(ctx, r'passes through the point \((-?\d+),\s*(-?\d+)\)')
    x0, y0 = int(m.group(1)), int(m.group(2))
    d = _gdrawn(ctx, 'line')
    out = []
    if d['m'] * x0 + d['c'] != y0:
        out.append(Verdict(False, f'the point ({x0}, {y0}) is not on the drawn line y = {d["m"]}x + {d["c"]}'))
    return out + judge(ctx, 'val', sympy.Integer(d['c']))


@task('gr_equation_from')
def t_gr_equation_from(ctx, **kw):
    m = _search(ctx, r'gradient (-?\d+) and y-intercept (-?\d+)')
    pc = str(ctx.key).split('|')
    if len(pc) != 2 or (int(pc[0]), int(pc[1])) != (int(m.group(1)), int(m.group(2))):
        return Verdict(False, f'key {ctx.key!r} but the question gives gradient {m.group(1)} and intercept {m.group(2)}')
    return Verdict(True)


@task('gr_parallel')
def t_gr_parallel(ctx, **kw):
    m = _search(ctx, r'parallel to y = (.+?)\.')
    e = sympy.expand(expr(m.group(1)))
    return judge(ctx, 'val', sympy.Poly(e, sym('x')).all_coeffs()[0])


@task('gr_speed')
def t_gr_speed(ctx, **kw):
    m = _search(ctx, r'(\d+) km in (\d+) hours')
    dist, hrs = int(m.group(1)), int(m.group(2))
    d = _gdrawn(ctx, 'distance_time')
    out = []
    if (d['distance'], d['time']) != (dist, hrs):
        out.append(Verdict(False, f'the question says {dist} km in {hrs} h but the graph shows {d["distance"]} km in {d["time"]} h'))
    return out + judge(ctx, 'val', sympy.Rational(dist, hrs))


@task('gr_roots')
def t_gr_roots(ctx, **kw):
    m = _search(ctx, r'roots of y = (.+?)\.')
    e = expr(m.group(1))
    return judge(ctx, 'set', real_solutions(e, sym('x')))


@task('gr_midpoint')
def t_gr_midpoint(ctx, **kw):
    x1, y1, x2, y2 = _two_points(ctx)
    return judge(ctx, 'tuple', [sympy.Rational(x1 + x2, 2), sympy.Rational(y1 + y2, 2)])


@task('gr_intersect')
def t_gr_intersect(ctx, **kw):
    m = _search(ctx, r'intersection of y = (.+?) and y = (.+?)\.')
    a, b = expr(m.group(1)), expr(m.group(2))
    x = sym('x')
    sols = sympy.solve(a - b, x)
    if len(sols) != 1:
        return Verdict(False, 'the lines do not meet at one point')
    return judge(ctx, 'tuple', [sols[0], a.subs(x, sols[0])])


def _pearson(points):
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points)
    sxx = sum((p[0] - mx) ** 2 for p in points)
    syy = sum((p[1] - my) ** 2 for p in points)
    return sxy / (sxx * syy) ** 0.5, sxy / sxx, mx, my


def _correlation_word(points):
    r = _pearson(points)[0]
    if r >= 0.6:
        return 'positive'
    if r <= -0.6:
        return 'negative'
    if abs(r) <= 0.3:
        return 'none'
    raise Cannot(f'correlation {r:.2f} is neither clearly strong nor clearly absent')


@task('gr_corr')
def t_gr_corr(ctx, **kw):
    d = _gdrawn(ctx, 'scatter')
    word = _correlation_word(d['points'])
    return judge_text(ctx, {'positive': 'positive correlation', 'negative': 'negative correlation',
                            'none': 'no correlation'}[word])


def _fit_checks(d):
    """The line of best fit drawn must be close to the least-squares line of the points."""
    if not d.get('fit'):
        return []
    m, c = d['fit']
    r, slope, mx, my = _pearson(d['points'])
    out = []
    if abs(slope - m) > 0.35 * abs(m) or abs((m * mx + c) - my) > 2.0:
        out.append(Verdict(False, f'the drawn line y = {m}x + {c} is not a good fit (least squares slope {slope:.2f}, '
                           f'it misses the mean point by {abs((m * mx + c) - my):.1f})'))
    return out


def _est_value(field):
    v, _, tol = str(field).partition('~')
    return read_val(v), tol


@task('gr_estimate')
def t_gr_estimate(ctx, **kw):
    d = _gdrawn(ctx, 'scatter')
    m = _search(ctx, r'when x = (\d+)')
    m_, c_ = d['fit']
    want = sympy.Rational(str(m_)) * int(m.group(1)) + sympy.Rational(str(c_))
    val, tol = _est_value(ctx.key)
    out = _fit_checks(d)
    if val is None or abs(val - want) > sympy.Rational(1, 2) or not tol:
        out.append(Verdict(False, f'key {ctx.key!r} but the drawn line gives {fmt(want)} at x = {m.group(1)}'))
    return out or [Verdict(True)]


@task('gr_line_multipart')
def t_gr_line_multipart(ctx, **kw):
    x1, y1, x2, y2 = _two_points(ctx)
    out = _segment_checks(ctx, (x1, y1, x2, y2))
    f = _fields(ctx)
    m = sympy.Rational(y2 - y1, x2 - x1)
    c = y1 - m * x1
    if len(f) != 3 or not _field_is(f[0], m) or not _field_is(f[1], c) or f[2] != f'{int(m)}:{int(c)}':
        out.append(Verdict(False, f'key {f!r} but recomputed gradient {m}, intercept {c}, equation {m}:{c}'))
    return out or [Verdict(True)]


@task('gr_journey')
def t_gr_journey(ctx, **kw):
    m = _search(ctx, r'journey of (\d+) km in (\d+) hours')
    dist, hrs = int(m.group(1)), int(m.group(2))
    d = _gdrawn(ctx, 'distance_time')
    out = []
    if (d['distance'], d['time']) != (dist, hrs):
        out.append(Verdict(False, f'the question says {dist} km in {hrs} h but the graph shows {d["distance"]} km in {d["time"]} h'))
    extra = int(_search(ctx, r'another (\d+) hours').group(1))
    far = int(_search(ctx, r'travel (\d+) km at the same speed').group(1))
    speed = sympy.Rational(dist, hrs)
    f = _fields(ctx)
    want = [speed, speed * extra, far / speed]
    if len(f) != 3 or not all(_field_is(g, w) for g, w in zip(f, want)):
        out.append(Verdict(False, f'key {f!r} but recomputed {[fmt(w) for w in want]}'))
    return out or [Verdict(True)]


@task('gr_scatter_multipart')
def t_gr_scatter_multipart(ctx, **kw):
    d = _gdrawn(ctx, 'scatter')
    out = _fit_checks(d)
    low = gtext(ctx)
    b = re.search(r'\bb\) (.*?) c\) use the same line', low)
    c_part = re.search(r'c\) use the same line to (.*)$', low)
    if not b or not c_part:
        raise Cannot('cannot find parts b) and c)')
    xq = float(re.search(r'-?\d+(?:\.\d+)?', b.group(1)).group())
    yq = float(re.search(r'-?\d+(?:\.\d+)?', c_part.group(1)).group())
    m_, c_ = d['fit']
    f = _fields(ctx)
    if len(f) != 3:
        raise Cannot('expected three fields')
    word = _correlation_word(d['points'])
    if f[0].strip().lower() != word:
        out.append(Verdict(False, f'part a: key {f[0]!r} but the points show {word} correlation'))
    yv, _ = _est_value(f[1])
    xv, _ = _est_value(f[2])
    if yv is None or abs(float(yv) - (m_ * xq + c_)) > 0.5:
        out.append(Verdict(False, f'part b: key {f[1]!r} but the line gives {m_ * xq + c_:.1f} at x = {xq:g}'))
    if xv is None or abs(float(xv) - (yq - c_) / m_) > 0.06:
        out.append(Verdict(False, f'part c: key {f[2]!r} but the line gives x = {(yq - c_) / m_:.2f} at y = {yq:g}'))
    return out or [Verdict(True)]


@task('gr_quad_features')
def t_gr_quad_features(ctx, **kw):
    m = _search(ctx, r'the quadratic y = (.+?)\.')
    e = sympy.expand(expr(m.group(1)))
    x = sym('x')
    d = _gdrawn(ctx, 'quadratic')
    a, b, c = sympy.Poly(e, x).all_coeffs()
    out = []
    if (d['a'], d['b'], d['c']) != (a, b, c):
        out.append(Verdict(False, f'the question says y = {fmt(e)} but the graph draws a={d["a"]}, b={d["b"]}, c={d["c"]}'))
    roots = sorted(real_solutions(e, x), key=float)
    tp = -b / (2 * a)
    want = [c] + roots + [tp, e.subs(x, tp)]
    f = _fields(ctx)
    if len(f) != len(want) or not all(_field_is(g, w) for g, w in zip(f, want)):
        out.append(Verdict(False, f'key {f!r} but recomputed {[fmt(w) for w in want]}'))
    return out or [Verdict(True)]


@task('gr_quad_intersection')
def t_gr_quad_intersection(ctx, **kw):
    m = _search(ctx, r'y = x\^2 and y = (.+?)\.')
    line = expr(m.group(1))
    x = sym('x')
    d = _gdrawn(ctx, 'quadratic')
    out = []
    if d['line'] is None or (sympy.Integer(d['line'][0]), sympy.Integer(d['line'][1])) != tuple(sympy.Poly(line, x).all_coeffs()):
        out.append(Verdict(False, f'the question says y = {fmt(line)} but the graph draws the line {d["line"]}'))
    roots = sorted(real_solutions(x ** 2 - line, x), key=float)
    if len(roots) != 2:
        return out + [Verdict(False, 'the line does not cut the parabola twice')]
    want = [roots[0], roots[0] ** 2, roots[1], roots[1] ** 2, roots[0], roots[1]]
    f = _fields(ctx)
    if len(f) != 6 or not all(_field_is(g, w) for g, w in zip(f, want)):
        out.append(Verdict(False, f'key {f!r} but recomputed {[fmt(w) for w in want]}'))
    return out or [Verdict(True)]


# ───────────────────────────── sequences ─────────────────────────────

_ORD = r'(\d+)\s?(?:st|nd|rd|th)'
_HASN = re.compile(r'(?<![a-z])n(?![a-z])')


def _lines(ctx):
    return [plain(x) for x in re.split(r'<br\s*/?>', ctx.raw)]


def _seq_terms(ctx, line=0):
    """Terms written after the first colon of a line: (values, index of the blank or None)."""
    ln = _lines(ctx)[line]
    if ':' in ln:
        after = ln.split(':', 1)[1]
    else:
        m = re.search(r'((?:-?\d+\s*,\s*)+\S*)', ln)
        if not m:
            raise Cannot('no terms in the line')
        after = m.group(1)
    vals, blank = [], None
    for part in after.split(','):
        part = part.strip().rstrip('.?').strip()
        if not part or part in ('...', '\u2026', '\\ldots', '\\dots'):
            continue
        if '_' in part:
            blank = len(vals)
            vals.append(None)
            continue
        v = read_val(part)
        if v is None:
            raise Cannot(f'cannot read the term {part!r}')
        vals.append(v)
    return vals, blank


def _diffs(v):
    return [b - a for a, b in zip(v, v[1:])]


def _const(v):
    return len(v) >= 2 and all(x == v[0] for x in v)


def _extend(terms):
    """Next term of a displayed sequence under the simplest rule (arithmetic, geometric, Fibonacci, quadratic)."""
    d1 = _diffs(terms)
    if len(terms) >= 3 and _const(d1):
        return terms[-1] + d1[0], 'arith'
    if len(terms) >= 3 and all(t != 0 for t in terms) and _const([b / a for a, b in zip(terms, terms[1:])]):
        return terms[-1] * terms[1] / terms[0], 'geom'
    if len(terms) >= 4 and all(terms[i] == terms[i - 1] + terms[i - 2] for i in range(2, len(terms))):
        return terms[-1] + terms[-2], 'fib'
    d2 = _diffs(d1)
    if len(terms) >= 4 and _const(d2):
        return terms[-1] + d1[-1] + d2[0], 'quad'
    raise Cannot(f'no simple rule for the terms {terms}')


@task('seq_next')
def t_seq_next(ctx, kind='auto', **kw):
    terms, blank = _seq_terms(ctx)
    if blank is None:
        raise Cannot('no blank in the sequence')
    if blank == len(terms) - 1:
        known = terms[:-1]
        want, found = _extend([sympy.nsimplify(t) for t in known])
        if kind != 'auto' and found != kind:
            return Verdict(False, f'expected a {kind} sequence but the terms {known} follow a {found} rule')
        return judge(ctx, 'val', want)
    # a missing term inside an arithmetic sequence
    pairs = [(terms[i], terms[i + 1]) for i in range(len(terms) - 1) if terms[i] is not None and terms[i + 1] is not None]
    if not pairs:
        raise Cannot('no two neighbouring known terms')
    d = pairs[0][1] - pairs[0][0]
    if any(b - a != d for a, b in pairs):
        return Verdict(False, f'the known terms do not share one common difference: {terms}')
    want = terms[blank + 1] - d if blank + 1 < len(terms) else terms[blank - 1] + d
    if blank > 0 and terms[blank - 1] + d != want:
        return Verdict(False, f'the terms around the blank do not form an arithmetic sequence: {terms}')
    return judge(ctx, 'val', want)


def _rule_ok(text, terms):
    t = tex_to_text(text).lower()
    nums = [sympy.nsimplify(x) for x in re.findall(r'-?\d+(?:\.\d+)?', t)]
    m = re.search(r'start at (-?\d+)', t)
    if m:
        if sympy.Integer(int(m.group(1))) != terms[0]:
            return False
        nums = [x for x in nums if x != sympy.Integer(int(m.group(1)))] or nums[1:]
    if not nums:
        raise Cannot(f'no number in the rule {text!r}')
    k = nums[-1]
    pairs = list(zip(terms, terms[1:]))
    if re.search(r'\badd', t):
        return all(b - a == k for a, b in pairs)
    if re.search(r'subtract|take away', t):
        return all(a - b == k for a, b in pairs)
    if re.search(r'multiply', t):
        return all(a * k == b for a, b in pairs)
    if re.search(r'divide', t):
        return all(b * k == a for a, b in pairs)
    raise Cannot(f'cannot read the rule {text!r}')


@task('seq_rule')
def t_seq_rule(ctx, **kw):
    terms, _ = _seq_terms(ctx)
    return judge_pred(ctx, lambda t: _rule_ok(t, terms), 'is the term-to-term rule')


def _ordinal(ctx):
    m = re.search(_ORD + r'(?: term| (?:square|triangle|odd|even))', ctx.low) or re.search(r'find term (\d+)', ctx.low)
    if not m:
        raise Cannot('no ordinal in the question')
    return int(m.group(1))


def _nth_expr(ctx):
    n = sym('n')
    for s in ctx.segs:
        if _HASN.search(s) and s.strip() != 'n' and not re.search(r'[<>]|\\sum', s):
            s2 = re.sub(r'^u_n\s*=\s*', '', s)
            if '=' in s2:
                continue
            return expr(s2), n
    raise Cannot('no nth term expression in the question')


@task('seq_nth_value')
def t_seq_nth_value(ctx, **kw):
    e, n = _nth_expr(ctx)
    k = _ordinal(ctx) if not re.search(r'u_\{?\d+', ' '.join(ctx.segs)) else None
    if k is None:
        k = int(re.search(r'u_\{?(\d+)', ' '.join(ctx.segs)).group(1))
    return judge(ctx, 'val', e.subs(n, k))


@task('seq_first_terms')
def t_seq_first_terms(ctx, **kw):
    e, n = _nth_expr(ctx)
    m = re.search(r'first (\w+) terms', ctx.low)
    count = {'three': 3, 'four': 4, 'five': 5, 'six': 6}.get(m.group(1)) if m else None
    if count is None:
        raise Cannot('cannot read how many terms')
    return judge(ctx, 'tuple', [e.subs(n, i) for i in range(1, count + 1)])


@task('seq_special')
def t_seq_special(ctx, **kw):
    k = _ordinal(ctx)
    m = re.search(r'(square|triangle|odd|even) number', ctx.low)
    if not m:
        raise Cannot('no special number named')
    kind = m.group(1)
    f = {'square': lambda i: i * i, 'triangle': lambda i: i * (i + 1) // 2,
         'odd': lambda i: 2 * i - 1, 'even': lambda i: 2 * i}[kind]
    out = []
    shown = [int(x) for x in re.findall(r'\d+', _lines(ctx)[0].split(':', 1)[1])] if ':' in _lines(ctx)[0] else []
    if shown and shown != [f(i) for i in range(1, len(shown) + 1)]:
        out.append(Verdict(False, f'the listed terms {shown} are not the {kind} numbers'))
    return out + judge(ctx, 'val', sympy.Integer(f(k)))


def _target_number(ctx):
    t = re.sub(r'\\\(.*?\\\)', ' ', ctx.raw)
    m = re.search(r'(?:Is|Show that|whether)\s+(\d+)', plain(t))
    if m:
        return int(m.group(1))
    raise Cannot('no target number in the question')


@task('seq_is_term')
def t_seq_is_term(ctx, **kw):
    e, n = _nth_expr(ctx)
    target = _target_number(ctx)
    sols = [s for s in sympy.solve(e - target, n)]
    yes = any(s.is_integer and s > 0 for s in sols)
    return judge_text(ctx, 'yes' if yes else 'no')


@task('seq_which_term')
def t_seq_which_term(ctx, **kw):
    e, n = _nth_expr(ctx)
    m = re.search(r'value (\d+)', ctx.low)
    if not m:
        raise Cannot('no value in the question')
    sols = [s for s in sympy.solve(e - int(m.group(1)), n) if s.is_integer and s > 0]
    if len(sols) != 1:
        return Verdict(False, f'{fmt(e)} = {m.group(1)} has no unique positive whole-number solution ({sols})')
    return judge(ctx, 'val', sols[0])


@task('seq_first_over')
def t_seq_first_over(ctx, **kw):
    e, n = _nth_expr(ctx)
    m = re.search(r'greater than (\d+)', ctx.low)
    if not m:
        raise Cannot('no threshold in the question')
    t = int(m.group(1))
    i = 1
    while e.subs(n, i) <= t:
        i += 1
        if i > 5000:
            raise Cannot('no term above the threshold')
    return judge(ctx, 'val', e.subs(n, i))


def _fit(terms):
    """nth term of a displayed linear or quadratic sequence (n starts at 1), checked against every term."""
    n = sym('n')
    d1 = _diffs(terms)
    if len(terms) >= 3 and _const(d1):
        e = d1[0] * n + (terms[0] - d1[0])
    else:
        d2 = _diffs(d1)
        if len(terms) >= 4 and _const(d2):
            a = d2[0] / 2
            b = d1[0] - 3 * a
            c = terms[0] - a - b
            e = a * n ** 2 + b * n + c
        else:
            raise Cannot(f'the terms {terms} are neither linear nor quadratic')
    if any(sympy.simplify(e.subs(n, i + 1) - t) != 0 for i, t in enumerate(terms)):
        raise Cannot('fit failed')
    return sympy.expand(e)


@task('seq_find_nth')
def t_seq_find_nth(ctx, **kw):
    terms, _ = _seq_terms(ctx)
    terms = [sympy.nsimplify(t) for t in terms]
    return judge(ctx, 'val', _fit(terms))


@task('seq_two_same')
def t_seq_two_same(ctx, **kw):
    n = sym('n')
    es = []
    for s in ctx.segs:
        if _HASN.search(s) and '=' not in s:
            es.append(expr(s))
    if len(es) != 2:
        raise Cannot('expected two nth terms')
    sols = sympy.solve(es[0] - es[1], n)
    good = [s for s in sols if s.is_integer and s > 0]
    if len(good) != 1:
        return Verdict(False, f'the two sequences meet at n = {sols}, not at a positive whole-number position')
    return judge(ctx, 'val', es[0].subs(n, good[0]))


def _arith_list(ctx, line):
    terms, _ = _seq_terms(ctx, line)
    terms = [sympy.nsimplify(t) for t in terms]
    d = terms[1] - terms[0]
    if not _const(_diffs(terms)):
        raise Cannot('not arithmetic')
    return terms[0], d


@task('seq_common_terms')
def t_seq_common_terms(ctx, **kw):
    lines = _lines(ctx)
    a1, d1 = _arith_list(ctx, 0)
    a2, d2 = _arith_list(ctx, 1)
    s1 = {a1 + i * d1 for i in range(400)}
    s2 = {a2 + i * d2 for i in range(400)}
    common = sorted(s1 & s2)
    if not common:
        return Verdict(False, 'the sequences share no term in the first 400')
    return judge(ctx, 'val', common[0])


@task('seq_lq_compare')
def t_seq_lq_compare(ctx, **kw):
    n = sym('n')
    es = [expr(s) for s in ctx.segs if _HASN.search(s) and '=' not in s and not s.strip() == 'n']
    if len(es) != 2:
        raise Cannot('expected two nth terms')
    i = 1
    while not es[0].subs(n, i) > es[1].subs(n, i):
        i += 1
        if i > 1000:
            raise Cannot('never exceeds')
    return judge(ctx, 'val', sympy.Integer(i))


def _ints(text):
    return [int(x) for x in re.findall(r'-?\d+', text)]


@task('seq_sum_arith')
def t_seq_sum_arith(ctx, **kw):
    m = re.search(r'first (\d+) terms .*first term (-?\d+) and common difference (-?\d+)', ctx.low)
    if not m:
        raise Cannot('cannot read the series')
    N, a, d = (int(x) for x in m.groups())
    return judge(ctx, 'val', sympy.Integer(N * (2 * a + (N - 1) * d) // 2))


@task('seq_rows')
def t_seq_rows(ctx, **kw):
    m = re.search(r'has (\d+) rows .*first row has (\d+) seats and each subsequent row has (\d+) more', ctx.low)
    if not m:
        raise Cannot('cannot read the rows')
    N, a, d = (int(x) for x in m.groups())
    return judge(ctx, 'val', sympy.Integer(sum(a + i * d for i in range(N))))


@task('seq_context')
def t_seq_context(ctx, **kw):
    m = re.search(r'£(\d+) in year 1\. each year .*increases by £(\d+)', ctx.low)
    k = re.search(r'salary in year (\d+)', ctx.low)
    if not m or not k:
        raise Cannot('cannot read the salary question')
    a, d, n = int(m.group(1)), int(m.group(2)), int(k.group(1))
    return judge(ctx, 'val', sympy.Integer(a + (n - 1) * d))


@task('seq_geometric')
def t_seq_geometric(ctx, kind='nth', **kw):
    m = re.search(r'first term (-?\d+) and common ratio (-?\d+)', ctx.low)
    if not m:
        raise Cannot('cannot read the geometric sequence')
    a, r = int(m.group(1)), int(m.group(2))
    k = re.search(_ORD + r' term', ctx.low)
    if kind == 'nth':
        return judge(ctx, 'val', sympy.Integer(a * r ** (int(k.group(1)) - 1)))
    N = int(re.search(r'first (\d+) terms', ctx.low).group(1))
    return judge(ctx, 'val', sympy.Integer(sum(a * r ** i for i in range(N))))


def _first_ratio(ctx):
    t = ctx.text
    a = int(re.search(r'first term (-?\d+)', t).group(1))
    seg = next((s for s in ctx.segs if re.fullmatch(r'\\?d?frac\{?.*', s) or '/' in s or 'frac' in s), None)
    if seg is None:
        raise Cannot('no ratio in the question')
    return a, expr(seg), seg


@task('seq_geometric_infinite')
def t_seq_geometric_infinite(ctx, **kw):
    a, r, _ = _first_ratio(ctx)
    if abs(r) >= 1:
        return Verdict(False, f'ratio {r} does not converge')
    return judge(ctx, 'val', sympy.nsimplify(a / (1 - r)))


@task('seq_convergence')
def t_seq_convergence(ctx, **kw):
    a, r, seg = _first_ratio(ctx)
    out = []
    if abs(r) >= 1:
        return [Verdict(False, f'ratio {r} does not converge')]
    m = re.search(r'frac\{(\d+)\}\{(\d+)\}|(\d+)/(\d+)', ctx.raw.replace('\\dfrac', 'frac'))
    p, q = (int(g) for g in (m.group(1), m.group(2))) if m and m.group(1) else (None, None)
    if p is not None and sympy.gcd(p, q) != 1:
        out.append(Verdict(False, f'the common ratio {p}/{q} is not in its simplest form'))
    T = int(re.search(r'S_n\s*>\s*(\d+)', ctx.raw.replace('\\(', '').replace('\\)', '').replace(' ', '')).group(1))
    inf = sympy.nsimplify(a / (1 - r))
    n = 1
    s = sympy.Integer(a)
    while not s > T:
        n += 1
        s = a * (1 - r ** n) / (1 - r)
        if n > 2000:
            return out + [Verdict(False, f'S_n never exceeds {T}')]
    if inf <= T:
        return out + [Verdict(False, f'S_n never exceeds {T} because the sum to infinity is {inf}')]
    f = _fields(ctx)
    if len(f) != 2 or not (_field_is(f[0], inf) and _field_is(f[1], n)):
        out.append(Verdict(False, f'key {f!r} but recomputed [{inf}, {n}]'))
    return out or [Verdict(True)]


def _frac_terms(ctx):
    segs = [s for s in ctx.segs if 'frac' in s or '/' in s]
    ln = tex_to_text(re.sub(r'<br\s*/?>.*', '', ctx.raw, flags=re.S))
    parts = re.findall(r'\(?(-?\d+)\)?\s*/\s*\(?(-?\d+)\)?', ln)
    if len(parts) < 3:
        raise Cannot('cannot read the fractions')
    return [(int(a), int(b)) for a, b in parts]


@task('seq_fraction_nth')
def t_seq_fraction_nth(ctx, **kw):
    terms = _frac_terms(ctx)
    nums = [sympy.Integer(a) for a, _ in terms]
    dens = [sympy.Integer(b) for _, b in terms]
    n = sym('n')
    if not (_const(_diffs(nums)) and _const(_diffs(dens))):
        raise Cannot('numerators and denominators are not both linear')
    N = nums[0] + (n - 1) * (nums[1] - nums[0])
    D = dens[0] + (n - 1) * (dens[1] - dens[0])
    k = int(re.search(_ORD + r' term', ctx.low).group(1))
    return judge(ctx, 'val', sympy.nsimplify((N / D).subs(n, k)))


@task('seq_pattern_dots')
def t_seq_pattern_dots(ctx, **kw):
    n = sym('n')
    shown = [int(a) for a in re.findall(r'shape \d+ has (\d+) dots', ctx.low)]
    k = int(re.search(r'shape (\d+) have', ctx.low).group(1))
    seg = next((s for s in ctx.segs if _HASN.search(s)), None)
    out = []
    if seg is not None:
        e = expr(seg)
        if [e.subs(n, i + 1) for i in range(len(shown))] != shown:
            out.append(Verdict(False, f'the stated rule {seg} does not give the shapes {shown}'))
        value = e.subs(n, k)
    else:
        if not _const(_diffs(shown)):
            raise Cannot('shapes are not linear')
        d = shown[1] - shown[0]
        value = shown[0] + (k - 1) * d
    return out + judge(ctx, 'val', sympy.Integer(value))


@task('seq_mean')
def t_seq_mean(ctx, **kw):
    m = re.search(r'first term (-?\d+), common difference (-?\d+), and (\d+) terms', ctx.low)
    if not m:
        raise Cannot('cannot read the series')
    a, d, N = (int(x) for x in m.groups())
    return judge(ctx, 'val', sympy.nsimplify(sympy.Integer(2 * a + (N - 1) * d) / 2))


@task('seq_sum_last')
def t_seq_sum_last(ctx, **kw):
    m = re.search(r'first term (-?\d+), last term (-?\d+), and (\d+) terms', ctx.low)
    if not m:
        raise Cannot('cannot read the series')
    a, l, N = (int(x) for x in m.groups())
    if (l - a) % (N - 1):
        return Verdict(False, f'{N} terms from {a} to {l} do not have a whole-number common difference')
    return judge(ctx, 'val', sympy.Integer(N * (a + l) // 2))


@task('seq_quadratic_verify')
def t_seq_quadratic_verify(ctx, **kw):
    n = sym('n')
    ln = _lines(ctx)[0]
    terms = [sympy.nsimplify(x) for x in re.findall(r'-?\d+', ln.split('starts', 1)[1])]
    shown = next((s for s in ctx.segs if _HASN.search(s)), None)
    if shown is None:
        raise Cannot('no formula shown')
    e = expr(shown)
    out = []
    if [e.subs(n, i + 1) for i in range(len(terms))] != terms:
        out.append(Verdict(False, f'the shown nth term {shown} does not give the terms {terms}'))
    k = int(re.search(_ORD + r' term', ctx.low).group(1))
    return out + judge(ctx, 'val', e.subs(n, k))


@task('seq_sum_squares')
def t_seq_sum_squares(ctx, **kw):
    raw = ctx.raw.replace(' ', '')
    m = re.search(r'\\sum_\{k=1\}\^\{(\d+)\}k\^2\\\)\s*$', raw)
    if not m or '\\dfrac{n(n+1)(2n+1)}{6}' not in raw:
        raise Cannot('cannot read the sum of squares')
    N = int(m.group(1))
    return judge(ctx, 'val', sympy.Integer(sum(i * i for i in range(1, N + 1))))


@task('seq_u_n')
def t_seq_u_n(ctx, **kw):
    n = sym('n')
    seg = next((s for s in ctx.segs if s.replace(' ', '').startswith('u_n=')), None)
    if seg is None:
        raise Cannot('no u_n shown')
    e = expr(seg.split('=', 1)[1])
    k = int(re.search(r'u_\{?(\d+)', ' '.join(ctx.segs[1:])).group(1))
    return judge(ctx, 'val', e.subs(n, k))


@task('seq_a_and_d')
def t_seq_a_and_d(ctx, **kw):
    m = re.search(_ORD + r' term is (-?\d+) and the ' + _ORD + r' term is (-?\d+)', ctx.low)
    if not m:
        raise Cannot('cannot read the two terms')
    i, vi, j, vj = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    d = sympy.Rational(vj - vi, j - i)
    a = vi - (i - 1) * d
    f = _fields(ctx)
    if len(f) != 2 or not (_field_is(f[0], a) and _field_is(f[1], d)):
        return Verdict(False, f'key {f!r} but recomputed [{a}, {d}]')
    return Verdict(True)


@task('seq_proof')
def t_seq_proof(ctx, kind=None, **kw):
    """Fixed proofs: every equation in the keyed steps is true and the distractors are not all-true algebra."""
    raw = str(ctx.key)
    bank = {str(b.get('id')): str(b.get('text')) for b in (ctx.p.get('answer_step_bank') or [])}
    ids = raw.split('|')[1:]
    if not ids or any(i not in bank for i in ids):
        raise Cannot(f'cannot read the keyed steps from {raw!r}')
    out = []
    steps = [bank[i] for i in ids]
    if kind == 'recurring':
        m = re.search(r'0\.\\overline\{(\d+)\}\s*=\s*\\dfrac\{(\d+)\}\{(\d+)\}', ctx.raw)
        if not m:
            raise Cannot('cannot read the recurring decimal')
        digits, p, q = m.group(1), int(m.group(2)), int(m.group(3))
        x = sympy.Rational(int(digits), 10 ** len(digits) - 1)
        if sympy.Rational(p, q) != x:
            out.append(Verdict(False, f'0.{digits} recurring is {x}, not {p}/{q}'))
        mult = 10 ** len(digits)
        body = [tex_to_text(s).replace(' ', '') for s in steps]
        want = [f'x=0.[{digits}]', f'{mult}x={digits}.[{digits}]', f'{mult}x-x={digits}']
        if len(body) != 3:
            raise Cannot('expected three keyed steps')
        for k, needle in enumerate(want):
            if needle not in body[k]:
                out.append(Verdict(False, f'keyed step {k + 1} does not read {needle!r}: "{steps[k]}"'))
        fm = re.search(r'x=\(\((\d+)\)/\((\d+)\)\)', body[2])
        if not fm or sympy.Rational(int(fm.group(1)), int(fm.group(2))) != x:
            out.append(Verdict(False, f'the last keyed step does not end with x = {x}: "{steps[2]}"'))
        if f'{mult - 1}x={digits}' not in body[2]:
            out.append(Verdict(False, f'the last keyed step never states {mult - 1}x = {digits}'))
    elif kind == 'odd_sum':
        text = ' '.join(steps)
        if 'n(a + l)/2' not in steps[1] or 'Sn' not in steps[1]:
            out.append(Verdict(False, f'the second keyed step must state Sn = n(a + l)/2: "{steps[1]}"'))
        if 'a = 1' not in steps[0] or 'd = 2' not in steps[0] or '2n \u2212 1' not in steps[0]:
            out.append(Verdict(False, 'the first keyed step must set a = 1, d = 2 and l = 2n - 1'))
        for lhs, rhs in _step_equations(steps[-1]):
            pass
        last = steps[-1].replace('\u2212', '-')
        chain = re.search(r'Sn = ([^=]+) = ([^=]+) = ([^=.]+)', last)
        if not chain:
            raise Cannot('cannot read the final substitution')
        n = sym('n')
        vals = [expr(c.strip().replace('\u00b2', '^2').replace(' ', '')) for c in chain.groups()]
        if any(sympy.simplify(v - n ** 2) != 0 for v in vals):
            out.append(Verdict(False, f'the final substitution is not equal to n^2: "{steps[-1]}"'))
    elif kind == 'divisible':
        n = sym('n')
        if not _property_holds(n * (n + 1), n, 'mult', 2):
            out.append(Verdict(False, 'n(n+1) is not always even'))
        low = ' '.join(steps).lower()
        for need in ('consecutive', 'even', 'divisible by 2'):
            if need not in low:
                out.append(Verdict(False, f'the keyed steps never mention {need!r}'))
    else:
        raise Cannot(f'unknown proof kind {kind}')
    for i, t in bank.items():
        if i in ids:
            continue
        stat = [_eq_status(l, r) for l, r in _step_equations(t) if l is not None]
        if stat and all(s is True for s in stat):
            out.append(Verdict(False, f'distractor "{t}" only contains true equations'))
    return out or [Verdict(True)]


# ───────────────────────────── surds ─────────────────────────────

def _squarefree(n):
    n = int(n)
    return n > 1 and all(f[1] == 1 for f in sympy.factorint(n).items())


def _surd_key(ctx):
    """(value, shape) of a keyed surd answer: ``shape`` lists the radicands and notes the form to check."""
    at, raw = ctx.at, str(ctx.key)
    parts = raw.split('|')
    S = sympy.sqrt
    try:
        if at == 'surd':
            k, r = (1, int(parts[0])) if len(parts) == 1 else (int(parts[0]), int(parts[1]))
            return k * S(r), {'rads': [r], 'pos': k >= 1}
        if at == 'algebraic' and len(parts) == 4 and parts[3] in ('+', '-'):
            c, b, r = int(parts[0]), int(parts[1]), int(parts[2])
            return c + (b if parts[3] == '+' else -b) * S(r), {'rads': [r], 'pos': b >= 1}
        if at == 'algebraic_fraction':
            if parts[0] == 'b' and len(parts) == 7:
                scale, const, coef, rad, den = (int(x) for x in parts[1:6])
                s = 1 if parts[6] == '+' else -1
                return sympy.Rational(scale, den) * (const + s * coef * S(rad)), \
                    {'rads': [rad], 'pos': coef >= 1 and den >= 1, 'reduced': sympy.gcd(scale, den) == 1}
            if parts[0] == 'd' and len(parts) == 4:
                r1, r2, den = int(parts[1]), int(parts[2]), int(parts[3])
                return (S(r1) + S(r2)) / den, {'rads': [], 'pos': den >= 1}
            if parts[0] == 'e' and len(parts) == 5:
                ip, sc, rad, den = (int(x) for x in parts[1:])
                return (ip + sc * S(rad)) / den, {'rads': [rad], 'pos': den >= 1,
                                                  'reduced': sympy.gcd(sympy.gcd(ip, sc), den) == 1}
            if len(parts) == 3:
                coef, rad, den = (int(x) for x in parts)
                return sympy.Rational(coef, den) * S(rad), {'rads': [rad], 'pos': coef >= 1 and den >= 1,
                                                            'reduced': sympy.gcd(coef, den) == 1}
    except (ValueError, ZeroDivisionError):
        pass
    v = read_val(raw)
    if v is None:
        raise Cannot(f'cannot read the surd key {raw!r} ({at})')
    return v, {'rads': [], 'pos': True}


def _surd_form_ok(text):
    """An option written as a surd answer: every radicand square-free and no root in a denominator."""
    t = tex_to_text(text).lower()
    for m in re.finditer(r'sqrt\(?(\d+)\)?', t):
        if int(m.group(1)) > 1 and not _squarefree(int(m.group(1))):
            return False
    if '/' in t and 'sqrt' in t.rsplit('/', 1)[1]:
        return False
    return True


def surd_judge(ctx, exp, rad=None, simple=True):
    """Judge the key (or the options) against the recomputed surd value ``exp``."""
    if ctx.mcq:
        def pred(text):
            v = read_val(text)
            if v is None:
                raise Cannot(f'cannot read {text!r}')
            return equivalent(v, exp) and (not simple or _surd_form_ok(text))
        return judge_pred(ctx, pred, f'equals {fmt(exp)} in simplest form')
    got, shape = _surd_key(ctx)
    out = []
    if not equivalent(got, exp):
        out.append(Verdict(False, f'key {ctx.key!r} is {fmt(got)} but recomputed {fmt(exp)}'))
        return out
    for r in shape['rads']:
        if not _squarefree(r):
            out.append(Verdict(False, f'key {ctx.key!r} leaves the radicand {r} unsimplified'))
    if rad is not None and shape['rads'] and shape['rads'][0] != rad:
        out.append(Verdict(False, f'the question asks for k√{rad} but the key has radicand {shape["rads"][0]}'))
    if not shape.get('pos', True):
        out.append(Verdict(False, f'key {ctx.key!r} has a non-positive coefficient or denominator'))
    if shape.get('reduced') is False:
        out.append(Verdict(False, f'key {ctx.key!r} is not in lowest terms'))
    return out or [Verdict(True)]


def _stext(ctx):
    return tex_to_text(ctx.raw).lower().replace('×', '*')


def _surd_search(ctx, pattern):
    m = re.search(pattern, _stext(ctx))
    if not m:
        raise Cannot(f'question does not match {pattern!r}')
    return m


@task('surd')
def t_surd(ctx, mode=None, **kw):
    S = sympy.sqrt
    if mode == 'simplify':
        m = _surd_search(ctx, r'^(?:write|simplify) (.+?)(?: in its simplest surd form)?\.?$')
        return surd_judge(ctx, expr(m.group(1)))
    if mode == 'form_k':
        m = _surd_search(ctx, r'(?:write|simplify) (.+?)\.? ?(?:write your answer )?in the form k\s*sqrt\(?(\d+)\)?')
        return surd_judge(ctx, expr(m.group(1)), rad=int(m.group(2)))
    if mode == 'expand_num':
        m = _surd_search(ctx, r'expand and simplify (.+?)\.?$')
        return surd_judge(ctx, sympy.expand(expr(m.group(1))), simple=False)
    if mode == 'expand_form':
        m = _surd_search(ctx, r'write (.+?) in the form p \+ q')
        return surd_judge(ctx, sympy.expand(expr(m.group(1))), simple=False)
    if mode == 'divide':
        return surd_judge(ctx, expr(_stext(ctx).split(':', 1)[1].strip()))
    if mode == 'mixed':
        return surd_judge(ctx, expr(_stext(ctx).split(':', 1)[1].strip()))
    if mode == 'multiply':
        m = _surd_search(ctx, r'simplify (.+?)\.?$')
        return surd_judge(ctx, expr(m.group(1)))
    if mode == 'rationalise':
        m = _surd_search(ctx, r'rationalise(?: the denominator)?(?: of|:)? (.+?)\.?(?: write.*)?$')
        e = expr(m.group(1))
        return surd_judge(ctx, e, simple=True)
    if mode == 'area':
        m = _surd_search(ctx, r'sides of length (.+?) cm and (.+?) cm')
        return surd_judge(ctx, sympy.simplify(expr(m.group(1)) * expr(m.group(2))))
    if mode == 'perimeter':
        m = _surd_search(ctx, r'a (equilateral triangle|square) has side length (.+?) cm')
        mult = 3 if m.group(1).startswith('equi') else 4
        return surd_judge(ctx, mult * expr(m.group(2)))
    if mode == 'identity':
        a, b = sym('a'), sym('b')
        want = a - b
        got = read_val(str(ctx.key))
        if got is None or not equivalent(got, want):
            return Verdict(False, f'key {ctx.key!r} but (√a + √b)(√a − √b) = a − b')
        return Verdict(True)
    if mode == 'equation':
        m = _surd_search(ctx, r'sqrt\(x \+ (\d+)\) = (\d+)')
        off, rhs = int(m.group(1)), int(m.group(2))
        return judge(ctx, 'val', sympy.Integer(rhs * rhs - off))
    if mode == 'between':
        m = _surd_search(ctx, r'sqrt\((\d+)\)')
        n = int(m.group(1))
        lo = sympy.floor(S(n))
        f = _fields(ctx)
        if len(f) != 2 or not (_field_is(f[0], lo) and _field_is(f[1], lo + 1)):
            return Verdict(False, f'key {f!r} but sqrt({n}) lies between {lo} and {lo + 1}')
        return Verdict(True)
    if mode == 'between_mcq':
        m = _surd_search(ctx, r'sqrt\((\d+)\) lies between')
        lo = int(sympy.floor(S(int(m.group(1)))))

        def pred(text):
            nums = [int(x) for x in re.findall(r'\d+', text)]
            if len(nums) != 2:
                raise Cannot(f'cannot read {text!r}')
            return nums == [lo, lo + 1]
        return judge_pred(ctx, pred, f'are the whole numbers either side of sqrt({m.group(1)})')
    if mode == 'compare':
        segs = [s for s in ctx.segs if 'sqrt' in s]
        if len(segs) != 2 or not ctx.mcq:
            raise Cannot('expected two surds and options')
        a, b = expr(segs[0]), expr(segs[1])
        want = segs[0] if a > b else segs[1]
        hits = [l for l, t in ctx.options if equivalent(read_val(t), a if a > b else b) and read_val(t) is not None]
        return [Verdict(True)] if hits == [ctx.letter] else [Verdict(False, f'larger is {want} (options {hits}) but key {ctx.letter}')]
    raise Cannot(f'unknown surd mode {mode!r}')


@task('eq_larger_root')
def t_eq_larger_root(ctx, **kw):
    """\"Solve x^2 + bx + c = 0. The larger root is:\" with numeric options."""
    lhs, rhs = the_equation(ctx)
    x = one_var(lhs - rhs)
    roots = real_solutions(lhs - rhs, x)
    if len(roots) < 2:
        return Verdict(False, f'the equation has {len(roots)} distinct real roots')
    if not re.search(r'larger root', ctx.low):
        raise Cannot('question does not ask for the larger root')
    return judge(ctx, 'val', max(roots, key=float))
