"""Expected-answer atoms, stated-accuracy parsing and comparison with a generator's key.

A solver returns a list of *atoms*, one per answer field:

* ``Fraction`` / ``int``: an exact rational value.
* ``Approx(value)``: an inexact value (square roots, trigonometry, pi). The key has to be
  the half-up rounding of it to an accuracy that the question states (or ``hint``).
* ``SF(coef, power)``: standard form. ``Pw(base, exp)``: a power. ``Surd(k, r)``: k root r.
* ``Ratio(a, b, ...)``: a ratio (compared as written, so it should be in simplest form
  when the question asks for that).
* ``str``: a keyword or text answer (case and spacing ignored).

Solvers may also return ``AnyOf([...atoms...], [...atoms...])`` when more than one complete
answer is acceptable. Intentionally no ``eval``: all parsing is by regex and ``Fraction``.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from generators.shared.rounding import round_half_up


class Cannot(Exception):
    """A solver could not read the recorded inputs (fails loudly, never skipped)."""


@dataclass(frozen=True)
class Approx:
    value: float
    hint: tuple | None = None   # ('dp', n) | ('sf', n) | ('unit', Fraction): default when the question states none


@dataclass(frozen=True)
class SF:
    coef: Fraction
    power: int


@dataclass(frozen=True)
class Pw:
    base: int
    exp: int


@dataclass(frozen=True)
class Surd:
    k: int
    r: int


@dataclass(frozen=True)
class SurdOver:
    """coef * sqrt(rad) / den (an exact trigonometric value such as sqrt(3)/2)."""
    coef: int
    rad: int
    den: int

    def square(self):
        return Fraction(self.coef * self.coef * self.rad, self.den * self.den)


class Ratio(tuple):
    def __new__(cls, *parts):
        return super().__new__(cls, tuple(int(p) for p in parts))


class Pick:
    """Expected answer given as a test on the option / field text (for choice questions)."""

    def __init__(self, test, desc):
        self.test = test
        self.desc = desc

    def __repr__(self):
        return f'Pick({self.desc})'


class PickSet(Pick):
    """Choose-all-that-apply: every required item satisfies ``test`` and no other bank item does."""


class Verdict:
    """A self-contained consistency check (used when the question has no typed key to compare with)."""

    def __init__(self, ok, message='', kind='answer'):
        self.ok = bool(ok)
        self.message = message
        self.kind = kind


class AnyOf(list):
    """Several complete acceptable answers, each a list of atoms."""


def sqrt_atom(n, hint=None):
    """sqrt of a non-negative rational as an exact Fraction when it is one, else Approx."""
    n = Fraction(n)
    if n < 0:
        raise Cannot(f'sqrt of negative {n}')
    num, den = math.isqrt(n.numerator), math.isqrt(n.denominator)
    if num * num == n.numerator and den * den == n.denominator:
        return Fraction(num, den)
    return Approx(math.sqrt(n), hint)


def simplify_sqrt(n):
    """(k, r) with sqrt(n) = k * sqrt(r) and r square-free, for a positive integer n."""
    n = int(n)
    k = 1
    p = 2
    while p * p <= n:
        while n % (p * p) == 0:
            n //= p * p
            k *= p
        p += 1
    return k, n


# ─────────────────────────────────────────────────────────────────────────────
# Stated accuracy
# ─────────────────────────────────────────────────────────────────────────────

_NEAREST_UNITS = {
    'whole number': 1, 'integer': 1, 'unit': 1, 'degree': 1, 'minute': 1, 'second': 1, 'hour': 1,
    'metre': 1, 'meter': 1, 'centimetre': 1, 'centimeter': 1, 'millimetre': 1, 'kilometre': 1,
    'cm': 1, 'mm': 1, 'm': 1, 'km': 1, 'kg': 1, 'g': 1, 'gram': 1, 'kilogram': 1, 'litre': 1, 'ml': 1,
    'pound': 1, 'penny': Fraction(1, 100), 'cent': Fraction(1, 100), 'tenth': Fraction(1, 10),
    'hundredth': Fraction(1, 100), 'ten': 10, 'hundred': 100, 'thousand': 1000,
    'person': 1, 'people': 1, 'year': 1, 'day': 1, 'week': 1, 'month': 1, 'mile': 1, 'item': 1,
    'tile': 1, 'tin': 1, 'bus': 1, 'bag': 1, 'pack': 1, 'box': 1, 'car': 1,
}

_DP = re.compile(r'(\d+|one|two|three|four)\s*(?:decimal\s*places?|d\.?\s?p\.?)', re.I)
_SF = re.compile(r'(\d+|one|two|three|four)\s*(?:significant\s*figures?|s\.?\s?f\.?)', re.I)
_NEAREST = re.compile(r'nearest\s+((?:\d+(?:\.\d+)?)|(?:[a-z]+(?:\s+number)?))', re.I)
_WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4}


def _to_int(word):
    word = word.lower()
    return _WORDS.get(word) or int(word)


def stated_specs(question_text: str) -> list:
    """Rounding instructions found in the question: [('dp', n), ('sf', n), ('unit', Fraction)]."""
    q = question_text
    specs = []
    for m in _DP.finditer(q):
        specs.append(('dp', _to_int(m.group(1))))
    for m in _SF.finditer(q):
        specs.append(('sf', _to_int(m.group(1))))
    for m in _NEAREST.finditer(q):
        word = m.group(1).lower().strip()
        if re.fullmatch(r'\d+(?:\.\d+)?', word):
            specs.append(('unit', Fraction(word)))
            continue
        word = re.sub(r's$', '', word.split()[0] if word.split()[0] != 'whole' else 'whole number')
        if word == 'whole number' or word in _NEAREST_UNITS:
            specs.append(('unit', Fraction(_NEAREST_UNITS[word])))
    if re.search(r'to the nearest (?:whole|integer)', q, re.I):
        specs.append(('unit', Fraction(1)))
    # De-duplicate, keep order.
    seen, out = set(), []
    for s in specs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _dec(x):
    if isinstance(x, Fraction):
        return Decimal(x.numerator) / Decimal(x.denominator)
    if isinstance(x, float):
        return Decimal(repr(x))
    return Decimal(x)


def apply_spec(x, spec):
    """Half-up rounding of ``x`` under ``spec``; returns a Fraction."""
    kind, n = spec
    d = _dec(x)
    if kind == 'dp':
        q = d.quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP)
    elif kind == 'sf':
        if d == 0:
            return Fraction(0)
        exp = d.adjusted() - n + 1
        q = d.quantize(Decimal(1).scaleb(exp), rounding=ROUND_HALF_UP)
        if q.adjusted() > d.adjusted():          # 9.96 -> 10.0 keeps the same number of figures
            q = q.quantize(Decimal(1).scaleb(q.adjusted() - n + 1), rounding=ROUND_HALF_UP)
    elif kind == 'unit':
        u = _dec(Fraction(n))
        q = (d / u).quantize(Decimal(1), rounding=ROUND_HALF_UP) * u
    else:
        raise ValueError(spec)
    return Fraction(q)


def rounded_candidates(x, specs):
    """Fractions the key may equal: x rounded under each spec (and the neighbours when x sits on a boundary)."""
    out = []
    probes = [x]
    if isinstance(x, float):
        probes += [x - 1e-9 * max(1.0, abs(x)), x + 1e-9 * max(1.0, abs(x))]
    for spec in specs:
        for p in probes:
            c = apply_spec(p, spec)
            if c not in out:
                out.append(c)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Parsing keys and options
# ─────────────────────────────────────────────────────────────────────────────

_NUM_LOOSE = re.compile(r'^\s*(?:[£$€]\s*)?([-+]?\s*\d[\d,]*(?:\.\d+)?)(?:\s*/\s*(\d+))?\s*(.*)$', re.S)


def parse_num(text):
    """Parse a plain number, decimal or fraction (with optional currency sign, % or unit) to a Fraction, else None."""
    s = str(text).strip().replace('−', '-').replace('−', '-')
    if not s:
        return None
    m = _NUM_LOOSE.match(s)
    if not m:
        return None
    rest = m.group(3)
    if re.search(r'[\d×^√:=]', rest):
        return None
    if re.search(r'\d', rest):
        return None
    head = m.group(1).replace(' ', '').replace(',', '')
    try:
        value = Fraction(head)
    except (ValueError, ZeroDivisionError):
        return None
    if m.group(2):
        den = int(m.group(2))
        if den == 0:
            return None
        value = value / den
    return value


def parse_sf(text):
    s = str(text).strip().replace('−', '-').replace('−', '-')
    m = re.fullmatch(r'([-+]?\d+(?:\.\d+)?)\s*\|\s*(-?\d+)', s)
    if not m:
        m = re.fullmatch(r'([-+]?\d+(?:\.\d+)?)\s*[×x*]\s*10\s*\^\s*\(?\s*(-?\d+)\s*\)?', s)
    return SF(Fraction(m.group(1)), int(m.group(2))) if m else None


def parse_pw(text):
    s = str(text).strip().replace('−', '-').replace('−', '-')
    m = re.fullmatch(r'(\d+)\s*\|\s*(-?\d+)', s) or re.fullmatch(r'(\d+)\s*\^\s*\(?\s*(-?\d+)\s*\)?', s)
    return Pw(int(m.group(1)), int(m.group(2))) if m else None


def parse_surd(text):
    s = str(text).strip()
    m = re.fullmatch(r'(\d+)\s*\|\s*(\d+)', s)
    if m:
        return Surd(int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r'(\d*)\s*√\s*\(?\s*(\d+)\s*\)?', s)
    if m:
        return Surd(int(m.group(1) or 1), int(m.group(2)))
    if re.fullmatch(r'\d+', s):
        return Surd(1, int(s))
    return None


def parse_surdover(text):
    m = re.fullmatch(r'\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*', str(text))
    if m and int(m.group(3)) != 0:
        return SurdOver(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def parse_ratio(text):
    s = str(text).strip()
    parts = re.split(r'\s*[:|]\s*', s)
    if len(parts) >= 2 and all(re.fullmatch(r'\d+', p) for p in parts):
        return Ratio(*parts)
    return None


def norm_text(text):
    return re.sub(r'\s+', ' ', str(text).strip().lower())


def parse_like(atom, text):
    """Parse ``text`` in the way the expected ``atom`` calls for; None if it cannot be read that way."""
    if isinstance(atom, (Fraction, int, Approx)):
        return parse_num(text)
    if isinstance(atom, SF):
        return parse_sf(text)
    if isinstance(atom, Pw):
        return parse_pw(text)
    if isinstance(atom, Surd):
        return parse_surd(text)
    if isinstance(atom, SurdOver):
        return parse_surdover(text)
    if isinstance(atom, Ratio):
        return parse_ratio(text)
    if isinstance(atom, (str, Pick)):
        return norm_text(text)
    return None


def split_key(answer_type, raw):
    """Split a practice problem's correct_answer_raw into per-field strings."""
    raw = str(raw)
    if answer_type in ('number_fields', 'number_pair', 'vector', 'vector_pair', 'vector_combo'):
        sep = '\x1e' if '\x1e' in raw else '|'
        return raw.split(sep)
    if answer_type == 'number_list':
        return [p for p in raw.split(',')]
    if answer_type == 'number_estimate' and '~' in raw:
        return [raw.split('~')[0]]      # 'value~tolerance': the value is compared, the band is the pupil's allowance
    return [raw]


# ─────────────────────────────────────────────────────────────────────────────
# Matching
# ─────────────────────────────────────────────────────────────────────────────

def show(atom):
    if isinstance(atom, Fraction):
        return str(atom.numerator) if atom.denominator == 1 else f'{atom.numerator}/{atom.denominator}' + \
            (f' ({float(atom):.10g})' if atom.denominator not in (1,) else '')
    if isinstance(atom, int):
        return str(atom)
    if isinstance(atom, Approx):
        return f'{float(atom.value):.10g} (inexact)'
    if isinstance(atom, SF):
        return f'{atom.coef} x 10^{atom.power}'
    if isinstance(atom, Pw):
        return f'{atom.base}^{atom.exp}'
    if isinstance(atom, Surd):
        return f'{atom.k}√{atom.r}' if atom.k != 1 else f'√{atom.r}'
    if isinstance(atom, Ratio):
        return ':'.join(str(p) for p in atom)
    if isinstance(atom, SurdOver):
        return f'{atom.coef}√{atom.rad}/{atom.den}'
    return repr(atom)


def _near(got, exact):
    """True when ``got`` is a rounding of ``exact`` (0 to 5 d.p. or 1 to 6 s.f., half-up, either way at a tie).

    Only used to label a mismatch as an accuracy problem rather than a wrong answer; both fail.  A plain
    closeness test (say within 2%) would label an off-by-one share of 50 as "accuracy", which misleads.
    """
    try:
        x = float(exact)
    except (TypeError, ValueError):
        return False
    probes = [x, x - 1e-9 * max(1.0, abs(x)), x + 1e-9 * max(1.0, abs(x))]
    specs = [('dp', n) for n in range(6)] + [('sf', n) for n in range(1, 7)]
    return any(apply_spec(p, s) == got for p in probes for s in specs)


def match_atom(atom, key_text, specs):
    """(ok, message, kind) for one atom against one key field; kind is 'answer' or 'accuracy'."""
    got = parse_like(atom, key_text)
    if got is None:
        return False, f'key field {key_text!r} cannot be read as {type(atom).__name__}', 'answer'
    if isinstance(atom, str):
        return (got == norm_text(atom)), f'key {key_text!r} vs expected {atom!r}', 'answer'
    if isinstance(atom, Pick):
        return bool(atom.test(key_text)), f'key {key_text!r} does not satisfy: {atom.desc}', 'answer'
    if isinstance(atom, (Fraction, int)):
        exact = Fraction(atom)
        if got == exact:
            return True, '', ''
        kind = 'accuracy' if _near(got, exact) else 'answer'
        if specs:
            cands = rounded_candidates(exact, specs)
            if got in cands:
                return True, '', ''
            return False, (f'key {key_text} but exact value is {show(exact)}; '
                           f'stated accuracy {specs} gives {[float(c) for c in cands]}'), kind
        return False, f'key {key_text} but exact value is {show(exact)} and the question states no rounding', kind
    if isinstance(atom, Approx):
        use = specs or ([atom.hint] if atom.hint else [])
        if not use:
            kind = 'accuracy' if _near(got, atom.value) else 'answer'
            return False, (f'key {key_text} but the exact value {float(atom.value):.10g} is inexact '
                           f'and the question states no accuracy'), kind
        cands = rounded_candidates(atom.value, use)
        if got in cands:
            return True, '', ''
        kind = 'accuracy' if _near(got, atom.value) else 'answer'
        return False, f'key {key_text} but {float(atom.value):.10g} rounded under {use} gives {[float(c) for c in cands]}', kind
    if isinstance(atom, SF):
        if got.coef == atom.coef and got.power == atom.power:
            return True, '', ''
        return False, f'key {key_text} but expected {show(atom)}', 'answer'
    if isinstance(atom, Surd) and got.k * got.k * got.r == atom.k * atom.k * atom.r:
        return True, '', ''
    if isinstance(atom, SurdOver) and got.square() == atom.square():
        return True, '', ''
    if got == atom:
        return True, '', ''
    return False, f'key {key_text!r} but expected {show(atom)}', 'answer'


def match_answer(expected, key_fields, specs):
    """Compare a solver's expected atoms with the key fields. Returns (ok, [messages], kind)."""
    candidates = expected if isinstance(expected, AnyOf) else [expected]
    best = None
    for atoms in candidates:
        if len(atoms) != len(key_fields):
            msg = f'expected {len(atoms)} field(s) {[show(a) for a in atoms]}, key has {len(key_fields)}: {key_fields}'
            best = best or ([msg], 'answer')
            continue
        msgs, kinds = [], set()
        for atom, field in zip(atoms, key_fields):
            ok, msg, kind = match_atom(atom, field, specs)
            if not ok:
                msgs.append(msg)
                kinds.add(kind)
        if not msgs:
            return True, [], ''
        kind = 'answer' if 'answer' in kinds else 'accuracy'
        if best is None or len(msgs) < len(best[0]):
            best = (msgs, kind)
    return False, best[0], best[1]


def canon_option(atom, text):
    """Comparable canonical value of an MCQ option (None if unreadable)."""
    got = parse_like(atom, text)
    return got if got is not None else norm_text(text)


def half_up(value, dp=0):
    """Convenience re-export of the school rounding helper (the only generator-side module solvers may share)."""
    return round_half_up(value, dp)
