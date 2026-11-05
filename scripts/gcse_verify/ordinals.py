"""Ordinal numbers written in question text: 1st, 2nd, 3rd, 4th, 11th, 12th, 13th, 21st, 101st, 111th.

A generator that builds "{n}th" by hand prints "21th" and "81th". This looks at every number followed by an
ordinal ending in the text a pupil reads (question, options, worked solution, hint) and flags the wrong ones.
Written from the rule, not from the generators' helper (generators.shared.utils.ordinal_suffix), so a bug in
the helper cannot hide here.
"""
from __future__ import annotations

import re

# A whole number (digits, optional thousands commas) and an ending, not part of a longer word or a decimal.
_ORDINAL = re.compile(r'(?<![\w.,])(\d{1,3}(?:,\d{3})+|\d+)(st|nd|rd|th)(?![A-Za-z0-9])', re.I)
ORDINAL_RE = _ORDINAL           # any number with an ordinal ending, right or wrong (the smoke uses it to find slots)


def expected_ending(n: int) -> str:
    """The ending English uses: -th for the teens (11 to 13 included), else -st, -nd, -rd for 1, 2, 3 and -th."""
    last_two = n % 100
    if last_two in (11, 12, 13):
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')


def ordinal_errors(text) -> list[str]:
    """One message per wrongly ended ordinal in ``text`` (a plain string; HTML tags are fine)."""
    out = []
    for m in _ORDINAL.finditer(str(text or '')):
        n = int(m.group(1).replace(',', ''))
        want = expected_ending(n)
        if m.group(2).lower() != want:
            out.append(f'ordinal {m.group(0)!r} should be {m.group(1)}{want}')
    return out


# A fraction written as a hyphenated ordinal: "one-4th", "one-16th", "1/8th". The ending is right for the number, so
# ``ordinal_errors`` cannot see it, but a pupil reads "one-4th" as a typing slip: it is "one quarter" or 1/4.
# Review 2026-10-27: only a number word (or "a") before the hyphen, so algebra such as "the n-1th term" is not flagged.
_FRACTION_WORD = re.compile(r'(?<![\w.])(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|an?)-\d+|\d+/\d+)'
                            r'(?:st|nd|rd|th)s?(?![A-Za-z0-9])', re.I)
# A placeholder with a hand-written ending in a generator's source: f"{n}th" (the helper is generators.shared.utils.ordinal)
_HAND_ENDING = re.compile(r'\}(?:st|nd|rd|th)\b')


def fraction_word_errors(text) -> list[str]:
    """One message per fraction written as a hyphenated or slashed ordinal in ``text`` (HTML tags are fine)."""
    return [f'fraction {m.group(0)!r} written as an ordinal (write it in words, as in "one quarter", or as a fraction)'
            for m in _FRACTION_WORD.finditer(str(text or ''))]


def source_errors(root, subdir='generators') -> list[str]:
    """Lines under ``root/subdir`` (every level and subject) that build an ordinal or a fraction word by hand."""
    from pathlib import Path
    out = []
    for path in sorted((Path(root) / subdir).rglob('*.py')):
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if _HAND_ENDING.search(line) or _FRACTION_WORD.search(line) or ordinal_errors(line):
                out.append(f'{path.relative_to(root)}:{number}: {line.strip()[:100]}')
    return out
