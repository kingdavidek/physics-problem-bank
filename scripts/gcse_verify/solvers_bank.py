"""Re-solvers for the fixed, hand-written MCQ bank items (Phase 4).

Until Phase 4 the 334 static bank items were reviewed by a person and pinned by digest.  Here each item that can
be computed gets its own small solver, keyed by the item's digest (``mcq.item_digest``).  A solver reads the
numbers and maths out of the item's displayed question (never its solution or hint, never the key), works out the
answer itself, and returns either an expected value or a ``Pick`` test on the option text.  The generic MCQ
checks in ``engine.verify_problem`` then require that the keyed option is the recomputed answer and that no
other option is.  Items with nothing to compute (definitions, wording, choice of method) stay pinned and are
listed with a reason in ``register.STATIC_EXEMPT``.

This module holds the toolkit and the ``bank`` family.  The specs themselves live in ``solvers_bank_number``,
``solvers_bank_algebra`` and ``solvers_bank_geometry`` and register through ``add``.

Independence rule: standard library, sympy and sibling solver modules only.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from . import core
from .core import Approx, Cannot, Pick, parse_num
from .registry import solver
from .solvers_algebra_parse import expr, tex_to_text

SPECS: dict = {}            # item digest -> function(Ctx) -> atoms
TOPIC_OF: dict = {}         # item digest -> topic slug (for the coverage report)


def add(topic, table):
    """Register ``{digest: spec}`` for ``topic``. A digest may belong to one spec only."""
    for digest, fn in table.items():
        if digest in SPECS and SPECS[digest] is not fn:
            raise ValueError(f'duplicate bank spec {digest}')
        SPECS[digest] = fn
        TOPIC_OF.setdefault(digest, topic)


# ─────────────────────────────────────────────────────────────────────────────
# Reading the item
# ─────────────────────────────────────────────────────────────────────────────

_NUM = re.compile(r'(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?!\d)|\d+(?:\.\d+)?')
_VULGAR = {'½': Fraction(1, 2), '⅓': Fraction(1, 3), '⅔': Fraction(2, 3), '¼': Fraction(1, 4), '¾': Fraction(3, 4)}


def numbers(text):
    """Every number in ``text`` (absolute values, in order) as a Fraction."""
    return [Fraction(m.group().replace(',', '')) for m in _NUM.finditer(text)]


class Ctx:
    """What a spec can see: the plain question, its options and the numbers in the question stem."""

    def __init__(self, q, opts):
        self.q = q
        self.opts = opts                                    # [(letter, text)]
        self.stem = re.split(r'Circle theorem diagram', q)[0].strip()   # the prose, without diagram labels
        self.n = numbers(self.stem)

    @property
    def texts(self):
        return [t for _, t in self.opts]

    def arith(self):
        """The arithmetic expression written in the question."""
        m = re.search(r'[-(]*\d[\d\s.+\-×÷*/^()²³]*', self.stem)
        if not m:
            raise Cannot(f'no arithmetic expression in {self.stem!r}')
        return m.group().strip()

    def after(self, pattern, end=r'[?:]|$'):
        """Text after ``pattern`` up to ``end``."""
        m = re.search(pattern + r'\s*(.*?)\s*(?:' + end + ')', self.stem)
        if not m:
            raise Cannot(f'{pattern!r} not found in {self.stem!r}')
        return m.group(1)


def val(text):
    """Value of an option or key text: plain number, decimal, fraction, % (scaled), currency or unit text."""
    s = str(text).strip().replace('−', '-').replace(',', '')
    m = re.fullmatch(r'(-?\d+)?\s*([½⅓⅔¼¾])\s*(.*)', s)
    if m and not re.search(r'\d', m.group(3)):
        whole = Fraction(int(m.group(1))) if m.group(1) else Fraction(0)
        return whole + _VULGAR[m.group(2)]
    v = parse_num(s)
    if v is None:
        return None
    return v / 100 if s.endswith('%') else v


def sx(text):
    """sympy value of maths written as plain text, LaTeX remnants or unicode (√, ², ×)."""
    return expr(tex_to_text(text))


def values(texts):
    return [val(t) for t in texts]


def pick(test, desc):
    """A Pick atom: exactly the keyed option must satisfy ``test(option text)``."""
    def safe(text):
        try:
            return bool(test(text))
        except (Cannot, ValueError, ZeroDivisionError, ArithmeticError, TypeError, AttributeError, KeyError,
                IndexError):
            return False
    return [Pick(safe, desc)]


def is_val(x):
    x = Fraction(x)
    return pick(lambda t: val(t) == x, f'equals {x}')


def simplest(x):
    """A fraction in lowest terms with value ``x``."""
    x = Fraction(x)

    def test(t):
        m = re.fullmatch(r'\s*(-?\d+)\s*/\s*(\d+)\s*', t)
        return bool(m) and math.gcd(int(m.group(1)), int(m.group(2))) == 1 and Fraction(int(m.group(1)), int(m.group(2))) == x
    return pick(test, f'{x} in lowest terms')


# ─────────────────────────────────────────────────────────────────────────────
# Exact arithmetic on the expression as written
# ─────────────────────────────────────────────────────────────────────────────

_TOKEN = re.compile(r'\s*(\d+(?:\.\d+)?|mod|[-+×÷*/^()²³])')


def calc(text):
    """Value of a written arithmetic expression, exactly (BIDMAS; unary minus below powers; ``mod`` allowed)."""
    s = text.replace('−', '-').replace('°', '').replace('\\mod', ' mod ')
    toks, i = [], 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        m = _TOKEN.match(s, i)
        if not m:
            raise Cannot(f'cannot read {s[i:i + 10]!r} in {text!r}')
        toks.append(m.group(1))
        i = m.end()
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def eat():
        pos[0] += 1
        return toks[pos[0] - 1]

    def addsub():
        v = muldiv()
        while peek() in ('+', '-'):
            v = v + muldiv() if eat() == '+' else v - muldiv()
        return v

    def muldiv():
        v = unary()
        while peek() in ('×', '*', '÷', '/', 'mod'):
            op = eat()
            r = unary()
            if op in ('×', '*'):
                v = v * r
            elif op == 'mod':
                v = v % r
            else:
                if r == 0:
                    raise Cannot('division by zero')
                v = v / r
        return v

    def unary():
        if peek() == '-':
            eat()
            return -unary()
        if peek() == '+':
            eat()
            return unary()
        return power()

    def power():
        b = atom()
        while peek() in ('^', '²', '³'):
            op = eat()
            if op == '^':
                neg = peek() == '-'
                if neg:
                    eat()
                e = atom()
                if e.denominator != 1 or abs(e) > 12:
                    raise Cannot('exponent too large or not whole')
                e = -int(e) if neg else int(e)
            else:
                e = 2 if op == '²' else 3
            b = b ** e
        return b

    def atom():
        t = eat() if peek() is not None else None
        if t is None:
            raise Cannot(f'unfinished expression {text!r}')
        if t == '(':
            v = addsub()
            if peek() != ')':
                raise Cannot(f'missing ) in {text!r}')
            eat()
            return v
        if re.fullmatch(r'\d+(?:\.\d+)?', t):
            return Fraction(t)
        raise Cannot(f'unexpected {t!r} in {text!r}')

    v = addsub()
    if pos[0] != len(toks):
        raise Cannot(f'unread tokens in {text!r}')
    return v


def exactish(x, tol=1e-9):
    """A float that is a whole number to within rounding noise becomes that integer; otherwise it stays inexact."""
    return Fraction(round(x)) if abs(x - round(x)) < tol else Approx(x)


def root(n):
    """sqrt of a non-negative rational: exact when it is one, inexact otherwise."""
    return core.sqrt_atom(Fraction(n))


def is_square(n):
    n = int(n)
    return n >= 0 and math.isqrt(n) ** 2 == n


def is_prime(n):
    n = int(n)
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def whole(x):
    """The integer value of a Fraction, or None."""
    return int(x) if isinstance(x, Fraction) and x.denominator == 1 else None


def lcm(a, b):
    return a * b // math.gcd(a, b)


# ─────────────────────────────────────────────────────────────────────────────
# The family
# ─────────────────────────────────────────────────────────────────────────────

@solver('bank', problem=True)
def bank(digest=None, _p=None, _records=None):
    """Re-solve a static bank item. ``_p`` is the item shown as a problem ({question, options, correct_answer})."""
    from .engine import parse_options
    from .latex import plain
    fn = SPECS.get(digest)
    if fn is None:
        raise Cannot(f'no re-solve spec for bank item {digest}')
    opts = parse_options(_p)
    if not opts:
        raise Cannot('item has no readable options')
    out = fn(Ctx(plain(_p['question']), opts))
    if isinstance(out, (core.AnyOf,)):
        return out
    return out if isinstance(out, list) else [out]


__all__ = ['Approx', 'Ctx', 'SPECS', 'add', 'calc', 'exactish', 'root', 'sx', 'is_prime', 'is_square', 'is_val', 'lcm', 'numbers',
           'pick', 'simplest', 'val', 'values', 'whole']
