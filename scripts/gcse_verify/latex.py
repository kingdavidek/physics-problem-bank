"""Turn generated question HTML / LaTeX into plain text and pull numbers out of it."""
from __future__ import annotations

import html
import re
from fractions import Fraction

_TAG = re.compile(r'<[^>]+>')
_BR = re.compile(r'<br\s*/?>', re.I)


def strip_html(text: str, keep_svg_text: bool = True) -> str:
    """Remove tags (and, optionally, whole SVG blocks) and decode entities."""
    s = str(text)
    if not keep_svg_text:
        s = re.sub(r'<svg.*?</svg>', ' ', s, flags=re.S)
    s = _BR.sub(' ', s)
    s = _TAG.sub(' ', s)
    s = html.unescape(s)
    return s.replace('\u00a0', ' ')


def _frac_repl(m):
    return f'({m.group(1)})/({m.group(2)})'


def latex_to_text(text: str) -> str:
    """Rough LaTeX to plain text, enough to read numbers and the maths symbols we care about."""
    s = str(text)
    s = s.replace('\\(', ' ').replace('\\)', ' ').replace('\\[', ' ').replace('\\]', ' ')
    for _ in range(3):
        s = re.sub(r'\\d?frac\{([^{}]*)\}\{([^{}]*)\}', _frac_repl, s)
    s = re.sub(r'\\sqrt\{([^{}]*)\}', r'√(\1)', s)
    s = (s.replace('\\times', '×').replace('\\div', '÷').replace('\\pi', 'π')
         .replace('\\cdot', '·').replace('\\%', '%').replace('\\,', ' ').replace('\\ ', ' ')
         .replace('\\degree', '°').replace('^\\circ', '°').replace('\\circ', '°')
         .replace('\\left', '').replace('\\right', '').replace('\\text', ''))
    s = re.sub(r'\^\{([^{}]*)\}', r'^\1', s)
    s = s.replace('{', ' ').replace('}', ' ')
    return s


def plain(text: str) -> str:
    """Pupil-visible text of a question or solution: tags removed, LaTeX flattened, spaces collapsed."""
    s = latex_to_text(strip_html(text))
    s = s.replace('\u2212', '-')
    return re.sub(r'\s+', ' ', s).strip()


_NUM = re.compile(r'\d+(?:\.\d+)?')
_THOUSANDS = re.compile(r'(?<![\d.,])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\d])')


def numbers_in(text: str) -> set:
    """Every number that appears in ``text`` as a Fraction (absolute values).

    Both readings of a comma are included ("1,548" gives 1548 and, separately, 1 and 548).
    """
    out = set()
    for m in _NUM.finditer(text):
        out.add(Fraction(m.group()))
    for m in _THOUSANDS.finditer(text):
        out.add(Fraction(m.group().replace(',', '')))
    return out
