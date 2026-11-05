"""Option checks that read amounts, not text: equal lengths in different units, and zero or negative fillers.

``300 m`` and ``0.3 km`` are the same length, so beside a key of ``0.3 km`` the option ``300 m`` is a second right
answer unless the question names the unit. The reader below turns an option into ``(exact value, unit key)``
with every common GCSE unit brought to one base per kind (lengths in m, areas in m squared, volumes in m cubed,
masses in g, times in s, money in pence), using ``Fraction`` arithmetic and the exact reader in ``exact.py``.
A unit it does not know stays as written, so ``5 cm`` and ``5 apples`` are still different.

Two checks use it (both run on every procedural multiple-choice problem and on every static bank item):

* ``same_value_errors``: an option worth the key, in any unit, is a second right answer (unless the question is
  about the form of the answer: simplest form, rationalise, three-figure bearings).
* ``filler_errors``: an option of 0 (or, where the key is a measured quantity or a plain number, a negative)
  beside a positive key is a filler that no pupil would pick. Questions that are about zero or negatives
  (solving, signs, temperature, indices, coordinates...) are exempt.
"""
from __future__ import annotations

import re
from fractions import Fraction

from . import exact
from .core import norm_text, parse_num

# Questions about the form of the answer itself, where an equal but unworked option is a legitimate distractor.
FORM_QUESTION = r'simplest|simplif|rationalis|rationaliz|three-figure|3-figure|prime factor'

# Questions where 0 or a negative number is a sensible answer or slip.
ZERO_OK = re.compile(
    r'zero|\bnil\b|negative|below|debt|overdrawn|temperature|lowest|bearing|how many|\bsolve\b|equation|inequalit|'
    r'\bvalue of [a-z]\b|\bwhat is \\?\(?[a-z]\b|\bfind \\?\(?[a-z]\b|intercept|root|coordinate|gradient|'
    r'turning point|expand|factoris|substitut|sequence|\bterm\b|probabilit|'
    r'translation|reflect|rotat|enlarge|vector|[-\u2212]\s*\d|\^\{?[-\u2212]',
    re.I)

_L, _A, _V, _M, _T = 'length', 'area', 'volume', 'mass', 'time'
F = Fraction

# unit text (lower case) -> (kind, size in the base unit of its kind)
_UNITS = {}


def _add(kind, size, *names):
    for n in names:
        _UNITS[n] = (kind, Fraction(size))


_add(_L, F(1, 1000), 'mm', 'millimetre', 'millimetres', 'millimeter', 'millimeters')
_add(_L, F(1, 100), 'cm', 'centimetre', 'centimetres', 'centimeter', 'centimeters')
_add(_L, 1, 'm', 'metre', 'metres', 'meter', 'meters')
_add(_L, 1000, 'km', 'kilometre', 'kilometres', 'kilometer', 'kilometers')
_add(_A, F(1, 10 ** 6), 'mm\u00b2', 'mm2', 'mm^2', 'square millimetres')
_add(_A, F(1, 10 ** 4), 'cm\u00b2', 'cm2', 'cm^2', 'square centimetres', 'sq cm')
_add(_A, 1, 'm\u00b2', 'm2', 'm^2', 'square metres', 'sq m')
_add(_A, 10 ** 6, 'km\u00b2', 'km2', 'km^2', 'square kilometres')
_add(_V, F(1, 10 ** 9), 'mm\u00b3', 'mm3', 'mm^3')
_add(_V, F(1, 10 ** 6), 'cm\u00b3', 'cm3', 'cm^3', 'cubic centimetres', 'ml', 'millilitre', 'millilitres')
_add(_V, F(1, 10 ** 5), 'cl', 'centilitre', 'centilitres')
_add(_V, F(1, 1000), 'l', 'litre', 'litres', 'liter', 'liters')
_add(_V, 1, 'm\u00b3', 'm3', 'm^3', 'cubic metres')
_add(_M, F(1, 1000), 'mg', 'milligram', 'milligrams')
_add(_M, 1, 'g', 'gram', 'grams')
_add(_M, 1000, 'kg', 'kilogram', 'kilograms')
_add(_M, 10 ** 6, 'tonne', 'tonnes')
_add(_T, 1, 's', 'sec', 'secs', 'second', 'seconds')
_add(_T, 60, 'min', 'mins', 'minute', 'minutes')
_add(_T, 3600, 'h', 'hr', 'hrs', 'hour', 'hours')
_add(_T, 86400, 'day', 'days')
_add('money', 1, 'p', 'pence')
_add('money', 100, 'pound', 'pounds')

_SYMBOLS = {'\u00a3': ('gbp', 100), '$': ('usd', 100), '\u20ac': ('eur', 100)}


def _scale(term, factor):
    return (term[0] * factor, term[1], term[2])


def amount(text):
    """(exact value, unit key) of an option that is one quantity, else None.

    Lengths come out in metres (``300 m`` and ``0.3 km`` both give 300 and 'length'), money in pence (``\u00a30.50``
    and ``50p``), times in seconds, and so on. Unknown units keep their own text as the key.
    """
    s = str(text).replace('\u2212', '-').strip()
    symbol = s[:1] if s[:1] in _SYMBOLS else None
    q = exact.quantity(s)
    if q is None:
        return None
    term, unit = q
    unit = unit.strip().rstrip('.').strip()
    if symbol:
        cur, per = _SYMBOLS[symbol]
        if unit == '':
            return exact.canon(_scale(term, per)), cur
        if unit == 'p':
            return exact.canon(term), cur
        return None
    got = _UNITS.get(unit)
    if got is None:
        return exact.canon(term), unit
    kind, size = got
    if kind == 'money':
        return exact.canon(_scale(term, size)), 'gbp'
    return exact.canon(_scale(term, size)), kind


def option_amount(text):
    """``amount`` or, for text it cannot read, the older plain-number rule (value from ``parse_num``)."""
    a = amount(text)
    if a is not None:
        return a
    v = parse_num(text)
    if v is None:
        return None
    return v, norm_text(re.sub(r'[-+\d.,/\s\u00a3$\u20ac]', '', str(text)))


def sign(value):
    coef = value[0] if isinstance(value, tuple) else value
    return (coef > 0) - (coef < 0)


def same_value_errors(question, opts, keyed):
    """Messages for options worth the key (unit-aware). ``opts`` is [(letter, text)], ``keyed`` the key's text."""
    if keyed is None or re.search(FORM_QUESTION, question, re.I):
        return []
    key = option_amount(keyed)
    if key is None:
        return []
    return [f'option {ltr} ({t!r}) has the same value as the key ({keyed!r})'
            for ltr, t in opts if t != keyed and option_amount(t) == key]


def filler_errors(question, opts, keyed):
    """Messages for a zero (or negative) option beside a positive key, unless the question is about such numbers."""
    if keyed is None or ZERO_OK.search(question):
        return []
    key = option_amount(keyed)
    if key is None or sign(key[0]) <= 0:
        return []
    out = []
    for ltr, t in opts:
        if t == keyed:
            continue
        a = option_amount(t)
        if a is None:
            continue
        s = sign(a[0])
        if s == 0:
            out.append(f'option {ltr} ({t!r}) is zero but the key ({keyed!r}) is positive: a filler no pupil would pick')
        elif s < 0:
            out.append(f'option {ltr} ({t!r}) is negative but the key ({keyed!r}) is positive: a filler no pupil would pick')
    return out
