"""Exact value of a displayed option such as ``5``, ``3/4``, ``12π cm``, ``√25``, ``2√9``, ``2√2 units``.

A value is one term ``coef * sqrt(r) * pi**pe`` with ``r`` square-free, so ``√8`` and ``2√2`` meet and
``√8`` and ``√2`` do not. Whatever follows the value is returned as its unit text. There is no ``eval``,
``exec`` or ``sympify``: a small hand-written reader over ``Fraction`` and integer square roots.

Sums and differences are not read (``3 + √2`` is unreadable, not a value), nor are products of two plain
numbers (``2 × 3``): the reader is for options that are one quantity, not for workings.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

_MAX_LEN = 80
_MAX_ROOT = 10 ** 12            # radicand cap: trial division only runs to the cube root (10 ** 4 steps at most)
_NUMBER = re.compile(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?', re.ASCII)       # ASCII digits only
_DIGITS = '0123456789'
_CURRENCY = '£$€'


class _Unreadable(Exception):
    pass


def _split_root(n):
    """(k, r) with sqrt(n) = k * sqrt(r), r square-free, for a positive integer n."""
    if n > _MAX_ROOT:
        raise _Unreadable
    k, r, p = 1, 1, 2
    while p * p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        k *= p ** (e // 2)
        r *= p ** (e % 2)
        p += 1 if p == 2 else 2
    # What is left has no prime factor up to its cube root, so it is 1, a prime, a prime squared or two primes.
    s = math.isqrt(n)
    if s * s == n:
        return k * s, r
    return k, r * n


def _term(coef, r=1, pe=0):
    if coef == 0:
        return (Fraction(0), 1, 0)
    return (Fraction(coef), r, pe)


def _mul(a, b):
    k, r = _split_root(a[1] * b[1])
    return _term(a[0] * b[0] * k, r, a[2] + b[2])


def _inv(a):
    if a[0] == 0:
        raise _Unreadable
    # 1 / (c sqrt(r)) = sqrt(r) / (c r)
    return _term(Fraction(1) / (a[0] * a[1]), a[1], -a[2])


def _sqrt(a):
    if a[1] != 1 or a[2] != 0 or a[0] < 0:
        raise _Unreadable
    q = a[0]
    if q == 0:
        return _term(0)
    k, r = _split_root(q.numerator * q.denominator)       # sqrt(p/q) = sqrt(pq) / q
    return _term(Fraction(k, q.denominator), r, 0)


def _rational(a):
    return a[1] == 1 and a[2] == 0


class _Reader:
    def __init__(self, text):
        self.s = text
        self.i = 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else ''

    def skip(self):
        while self.peek() == ' ':
            self.i += 1

    def eat(self, chars):
        self.skip()
        if self.peek() and self.peek() in chars:
            self.i += 1
            return True
        return False

    def starts_factor(self):
        self.skip()
        c = self.peek()
        return c in ('√', 'π', '(') or (c != '' and c in _DIGITS)

    def atom(self, depth=0):
        """number | pi | root-sign atom | ( product ), then an optional square."""
        if depth > 6:
            raise _Unreadable
        self.skip()
        c = self.peek()
        if c == '√':
            self.i += 1
            self.skip()
            if self.peek() == '(':
                self.i += 1
                inner = self.product(depth + 1)
                if not self.eat(')'):
                    raise _Unreadable
            else:
                m = _NUMBER.match(self.s, self.i)
                if not m:
                    raise _Unreadable
                self.i = m.end()
                inner = _term(Fraction(m.group().replace(',', '')))
            t = _sqrt(inner)
        elif c == 'π':
            self.i += 1
            t = _term(1, 1, 1)
        elif c == '(':
            self.i += 1
            t = self.product(depth + 1)
            if not self.eat(')'):
                raise _Unreadable
        else:
            m = _NUMBER.match(self.s, self.i)
            if not m:
                raise _Unreadable
            self.i = m.end()
            t = _term(Fraction(m.group().replace(',', '')))
        # a square written straight after the factor: (√5)², 5², π^2
        if self.s.startswith('²', self.i):
            self.i += 1
            t = _mul(t, t)
        elif re.match(r'\^\s*2(?!\d)', self.s[self.i:]):
            self.i = re.compile(r'\^\s*2').match(self.s, self.i).end()
            t = _mul(t, t)
        return t

    def product(self, depth=0):
        """sign? atom (( '×' | juxtaposition | '/' ) atom)*, with the rules in the module docstring."""
        self.skip()
        sign = 1
        if self.peek() in ('-', '+'):
            sign = -1 if self.peek() == '-' else 1
            self.i += 1
        first = self.atom(depth)
        val = _term(first[0] * sign, first[1], first[2])
        irrational = not _rational(first)
        slashes = 0
        explicit = False
        while True:
            save = self.i
            if self.eat('×*·'):
                op = '*'
                explicit = True
            elif self.eat('/'):
                op = '/'
            elif self.s[save:save + 1] != ' ' and self.starts_factor() and self.peek() in ('√', 'π', '('):
                op = '*'            # 2√9, 3π, 2(√3): glued to the previous factor
                explicit = explicit or self.peek() == '('       # 2(3) is a working; 2(√3) is still a value
            else:
                self.i = save
                break
            if not self.starts_factor():
                if op == '/':
                    self.i = save           # "3/" or "6/ cm": not a quotient
                    break
                raise _Unreadable
            nxt = self.atom(depth)
            irrational = irrational or not _rational(nxt)
            if op == '/':
                slashes += 1
                val = _mul(val, _inv(nxt))
            else:
                val = _mul(val, nxt)
        if not irrational and (explicit or slashes > 1):
            raise _Unreadable           # 2 × 3 and 1/2/3 are workings, not a value
        return val


def quantity(text):
    """(term, unit) for ``text``: the leading quantity as an exact term and the unit text after it, else None.

    ``unit`` is lower-cased with spaces collapsed; a leading currency sign is dropped. Text whose remainder
    still holds digits, ``× ^ √ : =`` (a ratio, a working, a second number) is not a quantity.
    """
    s = str(text).replace('−', '-').replace('\u00a0', ' ').strip()
    if not s or len(s) > _MAX_LEN:
        return None
    s = s.lstrip(_CURRENCY).lstrip()
    s = re.sub(r'\\sqrt\s*\{([^{}]*)\}', r'√(\1)', s)
    s = re.sub(r'\bsqrt\s*\(', '√(', s, flags=re.I)
    s = re.sub(r'\bsqrt\s*(?=\d)', '√', s, flags=re.I)
    s = s.replace('\\pi', 'π').replace('\\times', '×').replace('\\cdot', '·')
    if not re.match(r'[-+]?\s*[\d√π(]', s):
        return None
    reader = _Reader(s)
    try:
        term = reader.product()
    except _Unreadable:
        return None
    rest = s[reader.i:]
    if re.search(r'[\d×^√:=]', rest) or rest[:1] in ('²', '³'):
        return None                     # 5³ or 5²² is a power the reader did not take, not a unit
    return term, re.sub(r'\s+', ' ', rest.strip().lower())


def canon(term):
    """A hashable value: a Fraction when rational, else (coef, r, pi power)."""
    if term[1] == 1 and term[2] == 0:
        return term[0]
    return term


def value_and_unit(text):
    """(canonical value, unit) of an option, or None when it is not one exact quantity."""
    q = quantity(text)
    return None if q is None else (canon(q[0]), q[1])


def rational_value(text):
    """Fraction for text that is exactly rational (``√25``, ``2√9``, ``3/4``), else None."""
    q = quantity(text)
    if q is None or not _rational(q[0]):
        return None
    return q[0][0]
