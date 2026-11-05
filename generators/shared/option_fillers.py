"""Plausible filler options for multiple-choice questions (docs/GCSE_MATHS_VERIFICATION.md, "Fillers and units").

A generator that cannot find three different distractors tops the list up with fillers. A filler must look like a
real answer: the same form, units and precision as the key, never equal in value to the key or to another option,
and never 0 or negative where the key is a positive quantity ("0" beside "Increase 100 by 20%" is an option no
pupil would pick). ``fillers`` returns such options; it draws no random number, so the question around it is
unchanged.
"""
from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

# one plain amount: an optional currency sign, a number, and a unit or sign with no digit of its own
# (12.5, £12, 7.875 hours, 5.9%, 12 cm²)
_AMOUNT = re.compile(r'^(?P<pre>[£$€]?)(?P<num>-?\d+(?:\.\d+)?)(?P<post>(?:\s*%|\s+[^\d]*|[^\d\s.][^\d]*)?)$')
_POWER = re.compile(r'[\d)][⁰¹²³⁴⁵⁶⁷⁸⁹]|\^')
_SUPER = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
_TO_SUPER = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
_SUPER_RUN = re.compile(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+')
_DIGIT_RUN = re.compile(r'\d+')
_MAX_TRIES = 40


def _amount(text):
    """(currency sign, Decimal, unit text, decimal places, zero-padded width) of one plain amount, else None (a power is not one)."""
    text = str(text).strip()
    m = _AMOUNT.match(text)
    if not m or _POWER.search(text):
        return None
    whole = m.group('num').lstrip('-').partition('.')[0]
    width = len(whole) if len(whole) > 1 and whole.startswith('0') else 0       # 090 keeps its three figures
    return m.group('pre'), Decimal(m.group('num')), m.group('post'), len(m.group('num').partition('.')[2]), width


def _numeric(correct, taken):
    """Fillers for an amount: the key moved by a few steps, in the key's own precision and units."""
    key = _amount(correct)
    if key is None:
        return
    pre, num, post, dp, width = key
    # step: the last digit the key shows (one place up when it shows three or more); for a whole number of 20 or
    # more, a ten (a hundred, a thousand...), one place below its leading digit
    if dp:
        step = Decimal(1).scaleb(-(dp if dp < 3 else dp - 1))
    elif abs(num) < 20:
        step = Decimal(1)
    else:
        lead = abs(num).adjusted()
        step = Decimal(1).scaleb(lead if lead <= 1 else lead - 1)
    seen = set()
    for t in taken:
        a = _amount(t)
        if a:
            seen.add((a[0], a[1], a[2].strip()))
    for k in range(1, _MAX_TRIES):
        for sgn in (1, -1):
            cand = num + sgn * k * step
            if (num > 0 and cand <= 0) or (num == 0 and cand < 0) or (num < 0 and cand >= 0):
                continue                      # a positive quantity is never zero or negative, nor a zero a negative
            shown = cand.quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)
            if (pre, shown, post.strip()) in seen:
                continue
            seen.add((pre, shown, post.strip()))
            digits = str(shown)
            if width:
                whole, dot, frac = digits.partition('.')
                digits = whole.zfill(width) + dot + frac
            yield f'{pre}{digits}{post}'


def _nudged(correct, taken):
    """Fillers for answers that are not one plain amount (7², 3 × 10^4, 1/8): nudge the last exponent or number."""
    text = str(correct)
    sup = list(_SUPER_RUN.finditer(text))
    runs = sup or list(_DIGIT_RUN.finditer(text))
    if not runs:
        return
    run = runs[-1]
    base = int(run.group().translate(_SUPER))
    for k in range(1, _MAX_TRIES):
        for new in (base + k, base - k):
            if new < (2 if sup else 1):          # an exponent of 1 is not written
                continue
            shown = str(new).translate(_TO_SUPER) if sup else str(new)
            cand = text[:run.start()] + shown + text[run.end():]
            if cand != text and cand not in taken:
                yield cand


def fillers(correct, taken=(), count=3):
    """Up to ``count`` filler options for ``correct`` (text), none equal to it or to anything in ``taken``."""
    taken = [str(t) for t in taken] + [str(correct)]
    out = []
    for gen in (_numeric(correct, taken), _nudged(correct, taken)):
        for cand in gen:
            if cand in taken:
                continue
            out.append(cand)
            taken.append(cand)
            if len(out) >= count:
                return out
        if out:
            break
    return out
