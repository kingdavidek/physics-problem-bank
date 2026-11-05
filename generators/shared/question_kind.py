"""The kind of a question: its text with every number, name, label and letter replaced by a placeholder.

Used by the GCSE maths lesson-quiz builder (a quiz does not ask two questions of one kind) and by the variety
report in ``scripts/gcse_verify/variety.py``, so the figure in the report is the behaviour pupils get
(docs/GCSE_MATHS_VARIETY.md section 2 and 6).  Pure text work: no generator is called and nothing is stored.

``template(question)``: the pupil-visible text (HTML and SVG removed, LaTeX flattened), every number (integers,
decimals, fractions, money, signs) replaced by ``#``, capitalised words outside a short function-word list (names,
places) by ``@``, one to three capital letters (labels) by ``L`` and single lower-case letters by ``v``.  Two
questions with the same template differ only in numbers, names, labels or letters.
"""
from __future__ import annotations

import html
import re

# Capitalised words that are not names (kept as words by the template).
KEEP = {'The', 'A', 'An', 'What', 'Find', 'Work', 'Give', 'Calculate', 'Show', 'Write', 'Solve', 'Simplify',
        'Expand', 'Factorise', 'How', 'Which', 'Is', 'Express', 'Use', 'Make', 'In', 'If', 'Each', 'Estimate',
        'Round', 'State', 'Explain', 'Prove', 'Here', 'This', 'Two', 'Three', 'One', 'It', 'Enter', 'Type',
        'Answer', 'Box', 'Part', 'Step', 'Point', 'Points', 'Triangle', 'Angle', 'Line', 'Hint', 'Then', 'Using',
        'Describe', 'Complete', 'Draw', 'Rearrange', 'Convert', 'Increase', 'Decrease', 'Share', 'Divide',
        'Multiply', 'Add', 'Subtract', 'When', 'For', 'Given', 'Let', 'Its', 'They', 'She', 'He', 'There', 'All',
        'Not', 'Yes', 'No', 'True', 'False', 'Total', 'North', 'Plot', 'Sketch', 'Determine', 'Decide'}

_TAG = re.compile(r'<[^>]+>')
_NUMBER = re.compile(r'-?\d+(?:[.,]\d+)*')
_FRACTION_RUN = re.compile(r'#(?:\s*/\s*#)+')
_CAPITALISED = re.compile(r'\b[A-Z][a-z]{2,}\b')
_LABEL = re.compile(r"\b[A-Z]{1,3}'?\b")
# Capital-letter words that name a kind of question, not a label (HCF and LCM are different questions).
ACRONYMS = {'HCF', 'LCM'}
_LETTER = re.compile(r'\b[a-z]\b')
_NUMBER_RUN = re.compile(r'(#\s*){2,}')
_SPACES = re.compile(r'\s+')
# A rounding instruction is not part of what is asked ("Give your answer correct to 2 decimal places.").
_ROUNDING = re.compile(r'\s*\b(?:Give|Round|Answer|Correct|Write)\b[^.?!]*\b(?:decimal places?|significant figures?|d\.p\.|s\.f\.)[^.?!]*[.?!]?')
# f^-1 (an inverse function, or sin^-1) is not a power of a number; a negative index is not a positive one.
_INVERSE = re.compile(r'\b([fgh]|sin|cos|tan)\s*\^\s*\(?\s*-\s*1\s*\)?(?!\d)')
_NEGATIVE_INDEX = re.compile(r'\^\s*\(?\s*-\s*(?=\d)')
# A quiz kind does not depend on the sign between two terms (x + 5 and x - 5 are one kind of question).
_SIGN = re.compile(r'\s[+\-\u2212]\s')
_TEMPLATES = {}
_FLAT = {}
_CACHE_LIMIT = 20000


def _latex_to_text(text: str) -> str:
    """Rough LaTeX to plain text (the same reading as scripts/gcse_verify/latex.py, which must not import this)."""
    s = str(text)
    s = s.replace('\\(', ' ').replace('\\)', ' ').replace('\\[', ' ').replace('\\]', ' ')
    for _ in range(3):
        s = re.sub(r'\\d?frac\{([^{}]*)\}\{([^{}]*)\}', lambda m: f'({m.group(1)})/({m.group(2)})', s)
    s = re.sub(r'\\sqrt\{([^{}]*)\}', r'√(\1)', s)
    s = (s.replace('\\times', '×').replace('\\div', '÷').replace('\\pi', 'π')
         .replace('\\cdot', '·').replace('\\%', '%').replace('\\,', ' ').replace('\\ ', ' ')
         .replace('\\degree', '°').replace('^\\circ', '°').replace('\\circ', '°')
         .replace('\\left', '').replace('\\right', '').replace('\\text', ''))
    s = re.sub(r'\^\{([^{}]*)\}', r'^\1', s)
    return s.replace('{', ' ').replace('}', ' ')


def flat(question) -> str:
    """Pupil-visible words and numbers of a question: tags and drawings removed, LaTeX flattened, spaces collapsed."""
    q = str(question)
    got = _FLAT.get(q)
    if got is None:
        s = q
        while True:                                 # drawings out (find is much quicker than a regex on long SVG)
            i = s.find('<svg')
            if i < 0:
                break
            j = s.find('</svg>', i)
            s = s[:i] + ' ' + (s[j + 6:] if j >= 0 else '')
        s = _TAG.sub(' ', s)
        s = _latex_to_text(html.unescape(s).replace('\u00a0', ' ')).replace('\u2212', '-')
        got = _SPACES.sub(' ', s).strip()
        if len(_FLAT) > _CACHE_LIMIT:
            _FLAT.clear()
        _FLAT[q] = got
    return got


def _cap(m):
    w = m.group(0)
    return w if w in KEEP else '@'


def template(question) -> str:
    """The normalised template of a pupil-visible question."""
    q = str(question)
    got = _TEMPLATES.get(q)
    if got is not None:
        return got
    s = flat(q).replace('\u00a3 ', '\u00a3')
    s = _INVERSE.sub(r'\1^inv', s)                       # f^-1 is the inverse function, not a power
    s = _NEGATIVE_INDEX.sub('^neg ', s)                  # 8^-2 (a negative index) is not 8^2 or 81^(1/2)
    s = _NUMBER.sub('#', s)
    stripped = _ROUNDING.sub('', s)
    if re.search(r'[A-Za-z]', stripped):                 # an instruction clause goes; a rounding question stays
        s = stripped
    s = _FRACTION_RUN.sub('#', s)
    s = _CAPITALISED.sub(_cap, s)
    s = _LABEL.sub(lambda m: m.group(0) if m.group(0) in ACRONYMS else 'L', s)
    s = _LETTER.sub('v', s)
    s = _NUMBER_RUN.sub('# ', s).strip()
    if len(_TEMPLATES) > _CACHE_LIMIT:
        _TEMPLATES.clear()
    _TEMPLATES[q] = s
    return s


def quiz_kind(problem) -> str:
    """The kind of a quiz question: the template of its question text with the sign between terms ignored
    (``If f(x) = 5x - 3`` and ``If f(x) = 2x + 7`` are one kind).  Nothing but the question text is read."""
    return _SIGN.sub(' + ', template((problem or {}).get('question') or ''))
