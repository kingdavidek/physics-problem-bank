"""GCSE maths variety plan, Phase 3 batch C1: new practice kinds for statistics, probability, graphs,
ratio_proportion and trigonometry (docs/GCSE_MATHS_VARIETY.md sections 4 and 21).

Every generator here returns the usual practice tuple ``(question, solution, hint, marks[, answer])`` that its topic's
``*_problem_from_output`` wrapper turns into a problem. The module is self-contained on purpose (shared helpers and the
earlier variety modules only): the topic modules import it lazily when they build their practice pools, so it must never
import them back. Diagrams are drawn here with ``models.svg_kit`` (CSS-variable colours, so they follow the light and
dark themes) and every drawn value is recorded, so the verification smoke can read the drawing back
(``scripts/gcse_verify/solvers_variety_c.py``) and the key can never disagree with what the pupil sees.

Each variant records the inputs the pupil is given (``record(...)``), after any drawing record, so the last record is
the one the independent solver re-solves.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from generators.gcse.maths_variety_a import _choice, _frac_text, _num_text
from generators.shared.rounding import fmt_dp
from generators.shared.verify_hook import record
from models import svg_kit

P = svg_kit.PALETTE
_FONT = f'font-size="14" font-weight="600" font-family="{svg_kit.FONT_FAMILY}"'


# ─────────────────────────────────────────────────────────────────────────────
# Answer payloads
# ─────────────────────────────────────────────────────────────────────────────

def _num(value, hint=None):
    """A number answer; exact text for a Fraction, int or terminating decimal. ``hint`` names the unit the box wants
    ("Enter the distance in metres"): it is shown under the box and read by the unit check with the question."""
    out = {'type': 'number', 'value': _text(value)}
    if hint:
        out['format_hint'] = hint
    return out


def _text(value):
    f = Fraction(value) if not isinstance(value, Fraction) else value
    return _num_text(f)


def _prob(num, den):
    """A probability keyed as a fraction in lowest terms (form: a decimal or percentage is accepted too)."""
    f = Fraction(num, den)
    if f.denominator == 1:
        return {'type': 'number', 'value': str(f.numerator), 'form': 'probability'}
    return {'type': 'fraction', 'value': _frac_text(f), 'form': 'probability'}


def _fraction(value):
    return {'type': 'fraction', 'value': _frac_text(Fraction(value))}


def _pair(a, b, label_a='x', label_b='y', sep=','):
    return {'type': 'number_pair', 'values': (_text(a), _text(b)), 'label_a': label_a, 'label_b': label_b, 'sep': sep}


def _fields(values, labels, hint=None):
    out = {'type': 'number_fields', 'values': tuple(str(v) for v in values), 'labels': tuple(labels)}
    if hint:
        out['format_hint'] = hint
    return out


def _line_eq(m, c):
    """y = mx + c with whole-number m and c (the linear_equation checker reads decimals, not fractions)."""
    return {'type': 'linear_equation', 'm': int(m), 'c': int(c)}


def _br(n):
    """A negative number in brackets for a worked line: (-4); a positive one as it is."""
    return f'({n})' if n < 0 else str(n)


def _prob_line(hits, total):
    """'Probability = 6/12 = <strong>1/2</strong>.' or, when the fraction is already in lowest terms, 'Probability = <strong>7/12</strong>.'"""
    if math.gcd(hits, total) > 1:
        return f'Probability = {hits}/{total} = <strong>{_frac_text(Fraction(hits, total))}</strong>.'
    return f'Probability = <strong>{hits}/{total}</strong>.'


def _plural(n, word):
    return f'{n} {word}' if n == 1 else f'{n} {word}s'


def _sign_text(m, c, var='x'):
    """'2x + 3', '-x - 4', 'x', '5' (never '1x' or '+ -3')."""
    parts = []
    if m != 0:
        parts.append(('-' if m < 0 else '') + (var if abs(m) == 1 else f'{abs(m)}{var}'))
    if c != 0 or not parts:
        parts.append((('- ' if c < 0 else '+ ') if parts else ('-' if c < 0 else '')) + str(abs(c)))
    return ' '.join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Drawing helpers (svg_kit root; every colour a CSS variable)
# ─────────────────────────────────────────────────────────────────────────────

def _t(x, y, text, cls, anchor='middle', fill=None):
    """A text element with a class the verification reader can find (tick labels, cells, nodes). The font is set once
    on the group that ``_wrap`` puts round the drawing (review 2026-10-28: a 6 by 6 table was 11 KB with the font
    repeated on every cell)."""
    return (f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" fill="{fill or P["ink"]}" '
            f'text-anchor="{anchor}">{svg_kit._esc(text)}</text>')


def _wrap(w, h, body, *, title, desc, max_width):
    """An svg_kit root whose body sits in one group carrying the font every text here uses."""
    return str(svg_kit.svg(w, h, title=title, desc=desc, body=f'<g {_FONT}>{body}</g>', max_width=max_width,
                           variant='chart'))


def _svg_table(col_heads, rows, *, title, desc, corner='', col_w=None, max_width=420, cls='cell', left=False):
    """A bordered table drawn as SVG: ``col_heads`` across the top, each row ``[head, cell, cell, ...]``.

    Cells are written as text elements of class ``cls`` (the reader rebuilds the grid from their positions); they are
    centred, or start at the left of the cell with ``left=True`` (the leaves of a stem and leaf diagram)."""
    ncol = len(col_heads) + 1
    widths = col_w or [max(60, 14 * max(len(str(corner)), *(len(str(r[0])) for r in rows)) + 16)] + \
        [max(56, 14 * max(len(str(h)), *(len(str(r[j + 1])) for r in rows)) + 16) for j, h in enumerate(col_heads)]
    row_h = 30
    W = sum(widths) + 2
    H = row_h * (len(rows) + 1) + 2
    parts = []
    xs = [1]
    for w in widths:
        xs.append(xs[-1] + w)
    for i in range(len(rows) + 2):
        y = 1 + i * row_h
        parts.append(f'<line x1="1" y1="{y}" x2="{W - 1}" y2="{y}" stroke="{P["ink_line"]}" stroke-width="1"/>')
    for x in xs:
        parts.append(f'<line x1="{x}" y1="1" x2="{x}" y2="{H - 1}" stroke="{P["ink_line"]}" stroke-width="1"/>')
    parts.append(f'<rect x="1" y="1" width="{W - 2}" height="{row_h}" fill="{P["brand"]}" fill-opacity="0.12"/>')
    parts.append(f'<rect x="1" y="1" width="{widths[0]}" height="{H - 2}" fill="{P["brand"]}" fill-opacity="0.12"/>')
    ymid = 1 + row_h / 2 + 4
    parts.append(_t(xs[0] + widths[0] / 2, ymid, corner, 'head'))
    for j, h in enumerate(col_heads):
        if left:
            parts.append(_t(xs[j + 1] + 12, ymid, h, 'head', anchor='start'))
        else:
            parts.append(_t(xs[j + 1] + widths[j + 1] / 2, ymid, h, 'head'))
    for i, row in enumerate(rows):
        y = 1 + (i + 1) * row_h + row_h / 2 + 4
        parts.append(_t(xs[0] + widths[0] / 2, y, row[0], 'rowhead'))
        for j in range(ncol - 1):
            if left:
                parts.append(_t(xs[j + 1] + 12, y, row[j + 1], cls, anchor='start'))
            else:
                parts.append(_t(xs[j + 1] + widths[j + 1] / 2, y, row[j + 1], cls))
    return _wrap(W, H, ''.join(parts), title=title, desc=desc, max_width=min(max_width, W))


class _Axes:
    """A coordinate frame: labelled ticks every ``x_step`` and ``y_step``, faint lines every minor step."""

    W, H = 420, 290
    PL, PR, PT, PB = 60, 18, 16, 48

    def __init__(self, x_lo, x_hi, y_lo, y_hi, x_step, y_step, x_minor=None, y_minor=None,
                 x_label='', y_label='', x_tick_fmt=str):
        self.x_lo, self.x_hi, self.y_lo, self.y_hi = x_lo, x_hi, y_lo, y_hi
        self.x_step, self.y_step = x_step, y_step
        self.x_minor, self.y_minor = x_minor, y_minor
        self.x_label, self.y_label = x_label, y_label
        self.x_tick_fmt = x_tick_fmt
        self.pw = self.W - self.PL - self.PR
        self.ph = self.H - self.PT - self.PB

    def sx(self, v):
        return self.PL + (float(v) - self.x_lo) / (self.x_hi - self.x_lo) * self.pw

    def sy(self, v):
        return self.PT + self.ph - (float(v) - self.y_lo) / (self.y_hi - self.y_lo) * self.ph

    @staticmethod
    def _ticks(lo, hi, step):
        out, v = [], math.ceil(lo / step - 1e-9) * step
        while v <= hi + 1e-9:
            out.append(round(v, 6))
            v += step
        return out

    def frame(self):
        parts = []
        x0 = self.sx(0) if self.x_lo <= 0 <= self.x_hi else self.PL
        y0 = self.sy(0) if self.y_lo <= 0 <= self.y_hi else self.PT + self.ph
        # the grid lines share their stroke through one group each (minor, then labelled), which keeps a graph with
        # sixty faint lines under 10 KB
        minor = []
        for v in (self._ticks(self.x_lo, self.x_hi, self.x_minor) if self.x_minor else []):
            x = self.sx(v)
            minor.append(f'<line x1="{x:.1f}" y1="{self.PT}" x2="{x:.1f}" y2="{self.PT + self.ph}"/>')
        for v in (self._ticks(self.y_lo, self.y_hi, self.y_minor) if self.y_minor else []):
            y = self.sy(v)
            minor.append(f'<line x1="{self.PL}" y1="{y:.1f}" x2="{self.W - self.PR}" y2="{y:.1f}"/>')
        if minor:
            parts.append(f'<g stroke="{P["ink_line"]}" stroke-width="0.6" stroke-opacity="0.55">{"".join(minor)}</g>')
        major, labels = [], []
        for v in self._ticks(self.x_lo, self.x_hi, self.x_step):
            x = self.sx(v)
            major.append(f'<line x1="{x:.1f}" y1="{self.PT}" x2="{x:.1f}" y2="{self.PT + self.ph}"/>')
            labels.append(_t(x, self.PT + self.ph + 16, self.x_tick_fmt(int(v) if float(v).is_integer() else v), 'tx',
                             fill=P['ink_muted']))
        for v in self._ticks(self.y_lo, self.y_hi, self.y_step):
            y = self.sy(v)
            major.append(f'<line x1="{self.PL}" y1="{y:.1f}" x2="{self.W - self.PR}" y2="{y:.1f}"/>')
            labels.append(_t(self.PL - 6, y + 4, _text(Fraction(str(v))), 'ty', anchor='end', fill=P['ink_muted']))
        parts.append(f'<g stroke="{P["ink_line"]}" stroke-width="1">{"".join(major)}</g>')
        parts.extend(labels)
        parts.append(f'<line x1="{self.PL}" y1="{y0:.1f}" x2="{self.W - self.PR}" y2="{y0:.1f}" '
                     f'stroke="{P["ink_muted"]}" stroke-width="1.6"/>')
        parts.append(f'<line x1="{x0:.1f}" y1="{self.PT}" x2="{x0:.1f}" y2="{self.PT + self.ph}" '
                     f'stroke="{P["ink_muted"]}" stroke-width="1.6"/>')
        if self.x_label:
            parts.append(_t(self.PL + self.pw / 2, self.H - 6, self.x_label, 'xlabel', fill=P['ink_muted']))
        if self.y_label:
            cy = self.PT + self.ph / 2
            parts.append(f'<text x="14" y="{cy:.0f}" fill="{P["ink_muted"]}" '
                         f'transform="rotate(-90,14,{cy:.0f})" text-anchor="middle">{svg_kit._esc(self.y_label)}</text>')
        return ''.join(parts)

    def polyline(self, points, colour=None, width=2.5, cls='series'):
        coords = ' '.join(f'{self.sx(x):.1f},{self.sy(y):.1f}' for x, y in points)
        return (f'<polyline class="{cls}" points="{coords}" fill="none" stroke="{colour or P["brand"]}" '
                f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')

    def marks(self, points, colour=None, r=4.5):
        return ''.join(f'<circle class="mark" cx="{self.sx(x):.1f}" cy="{self.sy(y):.1f}" r="{r}" '
                       f'fill="{colour or P["measure"]}"/>' for x, y in points)

    def label(self, x, y, text, dx=8, dy=-8, anchor='start', colour=None):
        return _t(self.sx(x) + dx, self.sy(y) + dy, text, 'note', anchor=anchor, fill=colour or P['ink'])

    def wrap(self, body, title, desc, max_width=440):
        return _wrap(self.W, self.H, self.frame() + body, title=title, desc=desc, max_width=max_width)


# ─────────────────────────────────────────────────────────────────────────────
# Statistics
# ─────────────────────────────────────────────────────────────────────────────

_TWO_WAY = [
    # row word, row names, column word, column names, the person (singular), {column: plural verb phrase},
    # {column: singular verb phrase}, the people of each row (plural), "is ..." for each row (singular)
    dict(row_word='year group', rows=('Year 10', 'Year 11'), col_word='way of travelling to school',
         cols=('Walk', 'Bus', 'Car'), person='pupil',
         plural={'Walk': 'walk to school', 'Bus': 'come by bus', 'Car': 'come by car'},
         single={'Walk': 'walks to school', 'Bus': 'comes by bus', 'Car': 'comes by car'},
         groups=('Year 10 pupils', 'Year 11 pupils'), is_in=('is in Year 10', 'is in Year 11')),
    dict(row_word='gender', rows=('Boys', 'Girls'), col_word='favourite subject', cols=('Maths', 'Science', 'Art'),
         person='pupil',
         plural={'Maths': 'chose maths', 'Science': 'chose science', 'Art': 'chose art'},
         single={'Maths': 'chose maths', 'Science': 'chose science', 'Art': 'chose art'},
         groups=('boys', 'girls'), is_in=('is a boy', 'is a girl')),
    dict(row_word='age group', rows=('Adults', 'Children'), col_word='drink', cols=('Tea', 'Juice', 'Water'),
         person='person',
         plural={'Tea': 'chose tea', 'Juice': 'chose juice', 'Water': 'chose water'},
         single={'Tea': 'chose tea', 'Juice': 'chose juice', 'Water': 'chose water'},
         groups=('adults', 'children'), is_in=('is an adult', 'is a child')),
    dict(row_word='type of pet', rows=('Dogs', 'Cats'), col_word='colour', cols=('Black', 'Brown', 'White'), person='pet',
         plural={'Black': 'are black', 'Brown': 'are brown', 'White': 'are white'},
         single={'Black': 'is black', 'Brown': 'is brown', 'White': 'is white'},
         groups=('dogs', 'cats'), is_in=('is a dog', 'is a cat')),
    dict(row_word='club', rows=('Chess club', 'Drama club'), col_word='day', cols=('Monday', 'Tuesday', 'Friday'),
         person='member',
         plural={'Monday': 'meet on Monday', 'Tuesday': 'meet on Tuesday', 'Friday': 'meet on Friday'},
         single={'Monday': 'meets on Monday', 'Tuesday': 'meets on Tuesday', 'Friday': 'meets on Friday'},
         groups=('chess club members', 'drama club members'), is_in=('is in the chess club', 'is in the drama club')),
]


def _two_way_cells():
    return [[random.randint(4, 30) for _ in range(3)] for _ in range(2)]


def _two_way_svg(spec, cells, totals=False):
    rows_, cols = spec['rows'], spec['cols']
    heads = list(cols) + (['Total'] if totals else [])
    rows = []
    for name, row in zip(rows_, cells):
        rows.append([name] + [str(v) for v in row] + ([str(sum(row))] if totals else []))
    if totals:
        rows.append(['Total'] + [str(sum(c[j] for c in cells)) for j in range(3)] + [str(sum(map(sum, cells)))])
    return _svg_table(heads, rows, title='Two-way table', desc='A two-way table of counts.')


def _people(person):
    return 'people' if person == 'person' else person + 's'


def _one(people):
    return 'person' if people == 'people' else people[:-1]


def gcse_stats_two_way_read():
    """Foundational: read a two-way table and add a row, a column or the whole table."""
    spec = random.choice(_TWO_WAY)
    row_word, rows_, col_word, cols, person, phrase = (spec[k] for k in ('row_word', 'rows', 'col_word', 'cols', 'person', 'plural'))
    cells = _two_way_cells()
    ask = random.choice(['row', 'col', 'all'])
    svg = _two_way_svg(spec, cells)
    if ask == 'row':
        i = random.randrange(2)
        total = sum(cells[i])
        q_part = f'How many {spec["groups"][i]} are there altogether?'
        working = (f'Add the numbers along the {rows_[i]} row: {" + ".join(str(v) for v in cells[i])} = <strong>{total}</strong>.')
        hint = 'Find the row for that group, then add every number along it.'
        record('stats_two_way_read', cells=cells, ask='row', index=i, group_word=spec['groups'][i], derived=('index',))
    elif ask == 'col':
        j = random.randrange(3)
        col = [cells[0][j], cells[1][j]]
        total = sum(col)
        q_part = f'How many {_people(person)} {phrase[cols[j]]} altogether?'
        working = f'Add the numbers down the {cols[j]} column: {col[0]} + {col[1]} = <strong>{total}</strong>.'
        hint = 'Find the column for that choice, then add the numbers down it.'
        record('stats_two_way_read', cells=cells, ask='col', index=j, group_word=phrase[cols[j]], derived=('index',))
    else:
        total = sum(map(sum, cells))
        q_part = f'How many {_people(person)} are there in the table altogether?'
        working = (f'Add every number in the table: {" + ".join(str(v) for row in cells for v in row)} = '
                   f'<strong>{total}</strong>.')
        hint = 'Every number in the table is part of the total.'
        record('stats_two_way_read', cells=cells, ask='all', index=0, derived=('index',))
    q = (f'The two-way table shows information about some {_people(person)}, sorted by {row_word} and {col_word}.'
         f'<br>{svg}<br>{q_part}')
    return q, working, hint, 1, _num(total)


def _rel(person):
    """The relative pronoun for the people or things of a two-way table ('pupils who', 'pets that')."""
    return 'that' if person == 'pet' else 'who'


def gcse_stats_two_way_complete():
    """Intermediate: three cells are missing from a two-way table with totals; find them."""
    spec = random.choice(_TWO_WAY)
    row_word, rows_, col_word, cols, person = (spec[k] for k in ('row_word', 'rows', 'col_word', 'cols', 'person'))
    cells = _two_way_cells()
    row_tot = [sum(r) for r in cells]
    col_tot = [cells[0][j] + cells[1][j] for j in range(3)]
    grand = sum(row_tot)
    # Hide (row 0, col 0), (row 1, col 1) and (row 1, col 2): each is found from one row or column total.
    shown = [[str(v) for v in row] for row in cells]
    shown[0][0], shown[1][1], shown[1][2] = 'a', 'b', 'c'
    rows = [[rows_[0]] + shown[0] + [str(row_tot[0])],
            [rows_[1]] + shown[1] + [str(row_tot[1])],
            ['Total'] + [str(v) for v in col_tot] + [str(grand)]]
    svg = _svg_table(list(cols) + ['Total'], rows, title='Two-way table', desc='A two-way table with three missing values.')
    q = (f'The two-way table shows information about some {_people(person)}, sorted by {row_word} and {col_word}. '
         f'Three of the values are missing.<br>{svg}<br>Work out the values of a, b and c.')
    a, b, c = cells[0][0], cells[1][1], cells[1][2]
    s = (f'a is in the {rows_[0]} row: a = {row_tot[0]} − {cells[0][1]} − {cells[0][2]} = <strong>{a}</strong>.<br>'
         f'b is in the {cols[1]} column: b = {col_tot[1]} − {cells[0][1]} = <strong>{b}</strong>.<br>'
         f'c is in the {cols[2]} column: c = {col_tot[2]} − {cells[0][2]} = <strong>{c}</strong>.<br>'
         f'Check the {rows_[1]} row: {cells[1][0]} + {b} + {c} = {row_tot[1]}.')
    hint = 'Each row and each column adds up to its total. Start with a line that has only one value missing.'
    record('stats_two_way_complete', r0c1=cells[0][1], r0c2=cells[0][2], r1c0=cells[1][0], row0=row_tot[0],
           row1=row_tot[1], col0=col_tot[0], col1=col_tot[1], col2=col_tot[2], grand=grand)
    return q, s, hint, 3, _fields([a, b, c], ['a', 'b', 'c'])


def gcse_stats_two_way_percent():
    """Difficult: a percentage of one group, read from a completed two-way table (not of everyone)."""
    spec = random.choice(_TWO_WAY)
    row_word, rows_, col_word, cols, person, phrase, groups = (
        spec[k] for k in ('row_word', 'rows', 'col_word', 'cols', 'person', 'plural', 'groups'))
    while True:
        cells = _two_way_cells()
        i, j = random.randrange(2), random.randrange(3)
        row_tot = sum(cells[i])
        grand = sum(map(sum, cells))
        pct = Fraction(100 * cells[i][j], row_tot)
        if (pct * 10).denominator == 1 and pct.denominator != 1 and cells[i][j] not in (row_tot, grand) \
                and pct not in (cells[i][j], row_tot, grand):
            break
    svg = _two_way_svg(spec, cells, totals=True)
    q = (f'The two-way table shows information about some {_people(person)}, sorted by {row_word} and {col_word}.'
         f'<br>{svg}<br>What percentage of the {groups[i]} {phrase[cols[j]]}?')
    s = (f'The question is about the {groups[i]} only, so the total to use is the {rows_[i]} row total, {row_tot}.<br>'
         f'{cells[i][j]} of the {row_tot} {groups[i]} {phrase[cols[j]]}.<br>'
         f'Percentage = {cells[i][j]} ÷ {row_tot} × 100 = <strong>{_text(pct)}%</strong>.')
    hint = 'The percentage is out of the group named in the question, not out of everyone in the table.'
    record('stats_two_way_percent', cells=cells, row=i, col=j, group_word=groups[i], col_word=phrase[cols[j]],
           derived=('row', 'col'))
    return q, s, hint, 2, _num(pct)


_STEM_CONTEXTS = [
    ('the ages, in years, of some people at a gym', 'years'),
    ('the marks of some pupils in a test', 'marks'),
    ('the heights, in cm, of some seedlings', 'cm'),
    ('the times, in minutes, taken to finish a puzzle', 'minutes'),
    ('the masses, in kg, of some parcels', 'kg'),
]


def _stem_leaf_draw(n, stems):
    """n sorted values spread over the given stems (every stem has at least one leaf)."""
    while True:
        vals = sorted(random.choice(stems) * 10 + random.randint(0, 9) for _ in range(n))
        if all(any(v // 10 == s for v in vals) for s in stems) and len(set(vals)) >= n - 1:
            return vals


def _stem_leaf_svg(vals):
    stems = sorted({v // 10 for v in vals})
    rows = [[str(s), ' '.join(str(v % 10) for v in vals if v // 10 == s)] for s in stems]
    key_val = vals[0]            # the smallest value: never the median, and the range and IQR draws avoid it
    table = _svg_table(['Leaf'], rows, corner='Stem', title='Stem and leaf diagram',
                       desc='A stem and leaf diagram.', col_w=[60, 230], cls='leaves', left=True)
    return table + f'<br>Key: {key_val // 10} | {key_val % 10} means {key_val}'


def _leaves_of(vals, stems):
    return [[v % 10 for v in vals if v // 10 == st] for st in stems]


def gcse_stats_stem_leaf_median():
    """Foundational: the median or the range from a stem and leaf diagram."""
    context, unit = random.choice(_STEM_CONTEXTS)
    n = random.choice([7, 9, 11])
    lo = random.randint(1, 5)
    stems = list(range(lo, lo + random.choice([3, 4])))
    ask = random.choice(['median', 'range'])
    while True:
        vals = _stem_leaf_draw(n, stems)
        if ask == 'median' or vals[-1] - vals[0] != vals[0]:
            break
    svg = _stem_leaf_svg(vals)
    q = f'The stem and leaf diagram shows {context}.<br>{svg}<br>Work out the {ask} of the data.'
    if ask == 'median':
        key = vals[n // 2]
        s = (f'There are {n} values, so the median is the {_ordinal(n // 2 + 1)} value in order.<br>'
             f'Counting along the leaves in order: {", ".join(str(v) for v in vals[:n // 2 + 1])}, so the median is '
             f'<strong>{key}</strong> {unit}.')
        hint = 'The leaves are already in order. Count to the middle value, then read the stem and the leaf together.'
    else:
        key = vals[-1] - vals[0]
        s = (f'Smallest value: {vals[0]}. Largest value: {vals[-1]}.<br>'
             f'Range = {vals[-1]} − {vals[0]} = <strong>{key}</strong> {unit}.')
        hint = 'The range is the largest value take away the smallest. Read each one with its stem.'
    record('stats_stem_leaf', stems=stems, leaves=_leaves_of(vals, stems), ask=ask, derived=('stems',))
    return q, s, hint, 2, _num(key)


def gcse_stats_stem_leaf_iqr():
    """Difficult: the interquartile range from a stem and leaf diagram."""
    context, unit = random.choice(_STEM_CONTEXTS)
    n = random.choice([11, 15])
    lo = random.randint(1, 5)
    stems = list(range(lo, lo + 4))
    while True:
        vals = _stem_leaf_draw(n, stems)
        q1, q3 = vals[(n + 1) // 4 - 1], vals[3 * (n + 1) // 4 - 1]
        if q3 > q1 and q3 - q1 not in (vals[-1] - vals[0], q3, q1, vals[0]):
            break
    svg = _stem_leaf_svg(vals)
    q = f'The stem and leaf diagram shows {context}.<br>{svg}<br>Work out the interquartile range of the data.'
    s = (f'There are {n} values. The lower quartile is the {_ordinal((n + 1) // 4)} value and the upper quartile '
         f'is the {_ordinal(3 * (n + 1) // 4)} value.<br>'
         f'Lower quartile = {q1}, upper quartile = {q3}.<br>'
         f'Interquartile range = {q3} − {q1} = <strong>{q3 - q1}</strong> {unit}.')
    hint = 'Find the lower quartile (a quarter of the way through) and the upper quartile (three quarters), then subtract.'
    record('stats_stem_leaf', stems=stems, leaves=_leaves_of(vals, stems), ask='iqr', derived=('stems',))
    return q, s, hint, 3, _num(q3 - q1)


def _ordinal(n):
    return f'{n}{"th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")}'


_TABLE_CONTEXTS = [
    # (what is counted, "in/by/to" the counted group, who was counted, the thing counted, one of them, smallest value,
    #  the short column heading of the drawn table)
    ('number of goals scored', 'in', 'matches', 'goals', 'goal', 0, 'Goals scored'),
    ('number of pets owned', 'by', 'pupils', 'pets', 'pet', 0, 'Pets owned'),
    ('number of books read last month', 'by', 'children', 'books', 'book', 0, 'Books read'),
    ('number of people in each car', 'for', 'cars', 'people', 'person', 1, 'People in car'),      # a car on the road has a driver
    ('number of letters delivered', 'to', 'houses', 'letters', 'letter', 0, 'Letters delivered'),
]


class _Ctx:
    """A frequency-table context: the first value is drawn at or above the context's minimum, and the drawn table's
    column headings are short enough for its 150 px and 100 px columns (review 2026-10-28: "Number of goals scored"
    and "Number of matches" ran into each other)."""

    def __init__(self):
        self.what, self.prep, self.who, self.noun, self.one, least, self.head = random.choice(_TABLE_CONTEXTS)
        self.start = random.randint(least, 2)

    def svg(self, values, shown):
        rows = [[str(v), str(f)] for v, f in zip(values, shown)]
        return _svg_table(['Frequency'], rows, corner=self.head, title='Frequency table', desc='A frequency table.',
                          col_w=[150, 100])


def gcse_stats_mode_from_table():
    """Foundational: the mode from a frequency table (the value, not its frequency)."""
    c = _Ctx()
    what, who, noun, one = c.what, c.who, c.noun, c.one
    values = list(range(c.start, c.start + random.choice([4, 5])))
    while True:
        freqs = [random.randint(2, 14) for _ in values]
        top = max(freqs)
        if freqs.count(top) == 1 and top not in values:
            break
    mode = values[freqs.index(top)]
    svg = c.svg(values, freqs)
    q = f'The table shows the {what} {c.prep} {sum(freqs)} {who}.<br>{svg}<br>Write down the mode.'
    s = (f'The mode is the value with the highest frequency. The highest frequency is {top}, in the row for '
         f'{mode} {one if mode == 1 else noun}.<br>The mode is <strong>{mode}</strong>.')
    hint = 'Look for the biggest number in the frequency column, then write down the value in that row.'
    record('stats_table_mode', values=values, freqs=freqs)
    return q, s, hint, 1, _num(mode)


def gcse_stats_median_from_table():
    """Intermediate: the median from a frequency table, by counting through the frequencies."""
    c = _Ctx()
    what, who = c.what, c.who
    values = list(range(c.start, c.start + random.choice([4, 5])))
    while True:
        freqs = [random.randint(2, 12) for _ in values]
        n = sum(freqs)
        if n % 2 == 1:
            break
    pos = (n + 1) // 2
    running, median = 0, None
    cum = []
    for v, f in zip(values, freqs):
        running += f
        cum.append(running)
        if median is None and running >= pos:
            median = v
    svg = c.svg(values, freqs)
    q = f'The table shows the {what} {c.prep} {n} {who}.<br>{svg}<br>Find the median.'
    s = (f'There are {n} {who}, so the median is the {_ordinal(pos)} value when the data are in order.<br>'
         f'Running totals down the table: {", ".join(str(c) for c in cum)}.<br>'
         f'The {_ordinal(pos)} value is in the row where the running total first reaches {pos}, so the median is '
         f'<strong>{median}</strong>.')
    hint = 'Add the frequencies as you go down the table until you pass the middle position, (n + 1) ÷ 2.'
    record('stats_table_median', values=values, freqs=freqs)
    return q, s, hint, 2, _num(median)


def gcse_stats_missing_value_mean():
    """Intermediate: the missing number in a list from its mean."""
    n = random.choice([4, 5, 6])
    kind, one = random.choice([('test marks', 'mark'), ('numbers', 'number'), ('scores', 'score'), ('ages', 'age')])
    while True:
        known = [random.randint(3, 40) for _ in range(n - 1)]
        mean = random.randint(5, 40)
        missing = mean * n - sum(known)
        if 1 <= missing <= 60 and missing not in known and missing not in (mean, n, n - 1) and len(set(known)) == n - 1:
            break
    q = (f'The mean of {n} {kind} is {mean}. {n - 1} of the {kind} are '
         f'{", ".join(str(k) for k in known[:-1])} and {known[-1]}. Work out the other {one}.')
    s = (f'Total of all {n} values = mean × {n} = {mean} × {n} = {mean * n}.<br>'
         f'Total of the known values = {" + ".join(str(k) for k in known)} = {sum(known)}.<br>'
         f'Missing value = {mean * n} − {sum(known)} = <strong>{missing}</strong>.')
    hint = 'Work out what all the values must add up to, then take away the ones you know.'
    record('stats_missing_value', n=n, mean=mean, known=known)
    return q, s, hint, 3, _num(missing)


def gcse_stats_missing_frequency_mean():
    """Difficult: a frequency table with an unknown frequency, found from the mean."""
    c = _Ctx()
    what, who = c.what, c.who
    values = list(range(min(c.start, 1), min(c.start, 1) + 4))
    while True:
        freqs = [random.randint(2, 12) for _ in values]
        n = sum(freqs)
        total = sum(v * f for v, f in zip(values, freqs))
        mean = Fraction(total, n)
        k = random.randrange(len(values))
        if (mean * 10).denominator == 1 and mean.denominator != 1 and freqs[k] not in (n, values[k]) \
                and freqs.count(freqs[k]) == 1:
            break
    shown = [str(f) for f in freqs]
    shown[k] = 'x'
    svg = c.svg(values, shown)
    other_n = n - freqs[k]
    other_total = total - values[k] * freqs[k]
    q = (f'The table shows the {what} {c.prep} some {who}. One frequency is unknown.<br>{svg}<br>'
         f'The mean {what} is {_text(mean)}. Work out the value of x.')
    v = values[k]
    vx = 'x' if v == 1 else f'{v}x'
    left = f'{other_total}' if v == 0 else f'{other_total} + {vx}'
    mn = mean * other_n
    if v > mean:
        last = f'{_text(v - mean)}x = {_text(mn - other_total)}'
    else:
        last = f'{_text(mean - v)}x = {_text(other_total - mn)}'
    s = (f'Total frequency = {other_n} + x. Total of value × frequency = {left}.<br>'
         f'Mean = ({left}) ÷ ({other_n} + x) = {_text(mean)}.<br>'
         f'{left} = {_text(mean)}({other_n} + x) = {_text(mn)} + {_text(mean)}x.<br>'
         f'{last}, so x = <strong>{freqs[k]}</strong>.')
    hint = ('Write the total frequency and the total of value × frequency with x in them, then set the mean equal '
            'to the number given.')
    record('stats_missing_freq', values=values, freqs=[None if i == k else f for i, f in enumerate(freqs)], mean=_text(mean))
    return q, s, hint, 4, _num(freqs[k])


def gcse_stats_combined_mean():
    """Difficult: the mean of two groups combined (not the mean of the two means)."""
    g1, g2, people, measure, unit, lo, hi = random.choice([
        ('Class A', 'Class B', 'pupils', 'mark', '', 20, 80), ('The boys', 'The girls', 'pupils', 'height', ' cm', 130, 170),
        ('Team A', 'Team B', 'players', 'age', '', 18, 35), ('The morning group', 'The afternoon group', 'runners', 'time', ' minutes', 20, 60),
    ])

    def intro(g, n):
        """'Class A has 30 pupils', 'The morning group has 17 runners', 'There are 20 boys'."""
        if g.endswith('s'):
            return f'There are {n} {g[4:]}'
        return f'{g} has {n} {people}'

    while True:
        n1, n2 = random.randint(5, 30), random.randint(5, 30)
        m1, m2 = random.randint(lo, hi), random.randint(lo, hi)
        if n1 == n2 or m1 == m2:
            continue
        combined = Fraction(n1 * m1 + n2 * m2, n1 + n2)
        if (combined * 10).denominator == 1 and combined != Fraction(m1 + m2, 2) and combined not in (n1, n2, m1, m2, n1 + n2):
            break
    q = (f'{intro(g1, n1)} and their mean {measure} is {m1}{unit}. '
         f'{intro(g2, n2)} and their mean {measure} is {m2}{unit}. '
         f'Work out the mean {measure} of all {n1 + n2} {people} together.')
    s = (f'Total for {g1[0].lower() + g1[1:] if g1.startswith("The") else g1} = {n1} × {m1} = {n1 * m1}.<br>'
         f'Total for {g2[0].lower() + g2[1:] if g2.startswith("The") else g2} = {n2} × {m2} = {n2 * m2}.<br>'
         f'Combined total = {n1 * m1} + {n2 * m2} = {n1 * m1 + n2 * m2}, for {n1} + {n2} = {n1 + n2} {people}.<br>'
         f'Combined mean = {n1 * m1 + n2 * m2} ÷ {n1 + n2} = <strong>{_text(combined)}</strong>.')
    hint = 'Find the total for each group first (mean × number), then divide the combined total by the combined number.'
    record('stats_combined_mean', n1=n1, m1=m1, n2=n2, m2=m2)
    return q, s, hint, 3, _num(combined)


def gcse_stats_sample_proportion():
    """Foundational: scale a sample proportion up to the population."""
    who, do, where = random.choice([
        ('pupils', 'walk to school', 'a school'), ('people', 'own a dog', 'a village'),
        ('customers', 'pay by card', 'a shop'), ('voters', 'support the plan', 'a town'),
        ('bulbs', 'are faulty', 'a batch'),
    ])
    while True:
        sample = random.choice([20, 25, 40, 50, 60, 80, 100])
        hits = random.randint(2, sample // 4) if who == 'bulbs' else random.randint(3, sample - 3)    # a few faulty bulbs
        pop = random.choice([300, 400, 500, 600, 800, 900, 1000, 1200, 1500, 2000])
        est = Fraction(hits * pop, sample)
        if est.denominator == 1 and est not in (hits, pop, sample) and math.gcd(hits, sample) > 1:
            break
    q = (f'In a random sample of {sample} {who} from {where}, {hits} {do}. '
         f'There are {pop} {who} in {where.replace("a ", "the ", 1)} altogether. Estimate how many of them {do}.')
    s = (f'Proportion in the sample = {hits}/{sample} = {_frac_text(Fraction(hits, sample))}.<br>'
         f'Estimate for the whole group = {_frac_text(Fraction(hits, sample))} × {pop} = <strong>{int(est)}</strong>.')
    hint = 'Work out the fraction of the sample, then take that fraction of the whole group.'
    record('stats_sample_scale', hits=hits, sample=sample, pop=pop)
    return q, s, hint, 2, _num(est)


def gcse_stats_capture_recapture():
    """Difficult: estimate a population by the capture-recapture method."""
    animal, place, tags, tagged = random.choice([
        ('fish', 'a lake', 'tags', 'tagged'), ('deer', 'a forest', 'marks', 'marked'),
        ('birds', 'a wood', 'rings', 'ringed'), ('rabbits', 'a field', 'tags', 'tagged'),
    ])
    while True:
        m = random.choice([20, 24, 30, 36, 40, 45, 48, 50, 60, 72, 80])
        n = random.choice([20, 24, 25, 30, 36, 40, 45, 48, 50, 60])
        k = random.randint(3, min(m, n) // 2)
        est = Fraction(m * n, k)
        if est.denominator == 1 and est not in (m, n, k, m + n, m + n - k, m * n):
            break
    the_place = place.replace('a ', 'the ', 1)
    q = (f'A scientist wants to estimate the number of {animal} in {place}. She catches {m} {animal}, {tags} them and '
         f'releases them. The next week she catches {n} {animal} and finds that {k} of them are {tagged}. '
         f'Estimate the number of {animal} in {the_place}.')
    s = (f'Let N be the number of {animal}. The fraction {tagged} in the second catch should match the fraction '
         f'{tagged} in {the_place}:<br>{k}/{n} = {m}/N.<br>'
         f'So N = {m} × {n} ÷ {k} = <strong>{int(est)}</strong>.')
    hint = ('Set the fraction tagged in the second sample equal to the fraction tagged in the whole population, '
            'then solve for the population.')
    record('stats_recapture', m=m, n=n, k=k)
    return q, s, hint, 3, _num(est)


def gcse_stats_median_class():
    """Difficult: the class interval that contains the median of grouped data."""
    width = random.choice([5, 10, 20])
    start = width * random.randint(0, 2)
    n_cls = 4
    scenario, var, unit = random.choice([
        ('the times, t minutes, taken by {n} runners', 't', 'minutes'), ('the heights, h cm, of {n} plants', 'h', 'cm'),
        ('the masses, m kg, of {n} parcels', 'm', 'kg'), ('the waiting times, t minutes, of {n} people at a clinic', 't', 'minutes'),
    ])
    intervals = [(start + width * i, start + width * (i + 1)) for i in range(n_cls)]
    while True:
        freqs = [random.randint(2, 15) for _ in intervals]
        n = sum(freqs)
        pos = Fraction(n + 1, 2)
        running, k = 0, None
        cum = []
        for i, f in enumerate(freqs):
            running += f
            cum.append(running)
            if k is None and running >= pos:
                k = i
        # Review 2026-10-28: with an even n, a running total equal to n/2 puts the n/2-th value in one class and the
        # (n/2 + 1)-th in the next, so the n/2 rule (grouped data) and the (n + 1)/2 rule disagree; such draws are out.
        if n % 2 == 0 and n // 2 in cum:
            continue
        break
    labels = [f'{a} &lt; {var} ≤ {b}' for a, b in intervals]
    rows = [[f'{a} < {var} ≤ {b}', str(f)] for (a, b), f in zip(intervals, freqs)]
    svg = _svg_table(['Frequency'], rows, corner=f'{var} ({unit})', title='Grouped frequency table',
                     desc='A grouped frequency table.', col_w=[150, 100])
    q = (f'The table shows {scenario.format(n=n)}.<br>{svg}<br>'
         f'Which class interval contains the median?')
    position = (f'the {_ordinal(int(pos))} value' if n % 2 else
                f'halfway between the {_ordinal(n // 2)} and {_ordinal(n // 2 + 1)} values')
    s = (f'With {n} values in order, the median is {position}.<br>'
         f'Running totals down the table: {", ".join(str(c) for c in cum)}.<br>'
         + (f'The running total first reaches {int(pos)} in the class ' if n % 2 else
            f'Both the {_ordinal(n // 2)} and the {_ordinal(n // 2 + 1)} values are in the class ')
         + f'<strong>{labels[k]}</strong>.')
    hint = 'Add the frequencies down the table and stop at the first class whose running total reaches the middle position.'
    record('stats_median_class', intervals=intervals, freqs=freqs)
    return q, s, hint, 2, _choice(labels, k)


_POLYGON_CONTEXTS = [
    ('the times taken by some runners to finish a race', 'runners', 't', 'minutes'),
    ('the heights of some plants', 'plants', 'h', 'cm'),
    ('the masses of some parcels', 'parcels', 'm', 'kg'),
    ('the lengths of some phone calls', 'calls', 't', 'minutes'),
]


def _polygon_classes():
    width = random.choice([10, 20])
    start = random.choice([0, 10, 20])
    n_cls = random.choice([4, 5])
    intervals = [(start + width * i, start + width * (i + 1)) for i in range(n_cls)]
    while True:
        freqs = [random.choice([2, 4, 6, 8, 10, 12, 14]) for _ in intervals]
        if len(set(freqs)) >= 3:
            return intervals, freqs


def _polygon_svg(intervals, freqs, var, unit):
    mids = [Fraction(a + b, 2) for a, b in intervals]
    x_lo, x_hi = intervals[0][0], intervals[-1][1]
    width = intervals[0][1] - intervals[0][0]
    ax = _Axes(x_lo, x_hi, 0, 16, width, 2, x_minor=width / 2, y_minor=1, x_label=f'{var} ({unit})', y_label='Frequency')
    pts = list(zip(mids, freqs))
    body = ax.polyline(pts) + ax.marks(pts)
    return ax.wrap(body, 'Frequency polygon', 'A frequency polygon plotted at the class midpoints.')


def gcse_stats_freq_polygon_read():
    """Intermediate: the total frequency from a frequency polygon."""
    scenario, who, var, unit = random.choice(_POLYGON_CONTEXTS)
    while True:
        intervals, freqs = _polygon_classes()
        if sum(freqs) not in {b for pair in intervals for b in pair}:
            break
    svg = _polygon_svg(intervals, freqs, var, unit)
    q = (f'The frequency polygon shows {scenario}. The classes are '
         f'{", ".join(f"{a} &lt; {var} ≤ {b}" for a, b in intervals)}.<br>{svg}<br>'
         f'How many {who} were there altogether?')
    s = (f'Read the frequency at each plotted point: {", ".join(str(f) for f in freqs)}.<br>'
         f'Total = {" + ".join(str(f) for f in freqs)} = <strong>{sum(freqs)}</strong>.')
    hint = 'Each point of the polygon is the frequency of one class. Read every point from the vertical axis and add them.'
    record('stats_polygon', intervals=intervals, freqs=freqs, ask='total', derived=('freqs',))
    return q, s, hint, 2, _num(sum(freqs))


def gcse_stats_freq_polygon_mean():
    """Difficult: an estimate of the mean from a frequency polygon (the points sit at the midpoints)."""
    scenario, who, var, unit = random.choice(_POLYGON_CONTEXTS)
    while True:
        intervals, freqs = _polygon_classes()
        mids = [Fraction(a + b, 2) for a, b in intervals]
        n = sum(freqs)
        mean = sum(m * f for m, f in zip(mids, freqs)) / n
        if (mean * 10).denominator == 1 and mean not in mids and mean not in {b for pair in intervals for b in pair}:
            break
    svg = _polygon_svg(intervals, freqs, var, unit)
    q = (f'The frequency polygon shows {scenario}. The classes are '
         f'{", ".join(f"{a} &lt; {var} ≤ {b}" for a, b in intervals)}.<br>{svg}<br>'
         f'Work out an estimate for the mean.')
    terms = ' + '.join(f'{_text(m)} × {f}' for m, f in zip(mids, freqs))
    s = (f'Each point is plotted at the midpoint of its class: {", ".join(_text(m) for m in mids)}.<br>'
         f'Frequencies read from the graph: {", ".join(str(f) for f in freqs)}, total {n}.<br>'
         f'Σ(midpoint × frequency) = {terms} = {_text(sum(m * f for m, f in zip(mids, freqs)))}.<br>'
         f'Estimated mean = {_text(sum(m * f for m, f in zip(mids, freqs)))} ÷ {n} = <strong>{_text(mean)}</strong> {unit}.')
    hint = 'Multiply each midpoint (where the point is plotted) by its frequency, add up, then divide by the total frequency.'
    record('stats_polygon', intervals=intervals, freqs=freqs, ask='mean', derived=('freqs',))
    return q, s, hint, 4, _num(mean)


def gcse_stats_time_series_mean():
    """Intermediate: the mean of one year's quarterly values read from a time series graph."""
    # (what, unit, seasonal shape Q1 to Q4): ice cream and visitors peak in the summer quarter, gas in the winter ones
    what, unit, shape = random.choice([
        ('ice cream sales', 'hundreds of pounds', (-4, 1, 5, -3)), ('gas used by a house', 'hundreds of units', (5, -2, -5, 3)),
        ('visitors to a museum', 'thousands', (-3, 0, 5, -2)), ('bookings at a hotel', 'hundreds', (-4, 0, 5, -1)),
    ])
    y1, y2 = random.choice([(2022, 2023), (2023, 2024), (2024, 2025)])
    while True:
        base, trend = random.randint(8, 12), random.choice([-1, 0, 1, 2])
        vals = [min(18, max(2, base + shape[q] + trend * yr + random.randint(-1, 1))) for yr in range(2) for q in range(4)]
        year = random.randrange(2)
        four = vals[4 * year:4 * year + 4]
        mean = Fraction(sum(four), 4)
        if len(set(vals)) >= 6 and mean != Fraction(sum(vals), 8) and mean not in vals:
            break
    ax = _Axes(0.5, 8.5, 0, 20, 1, 2, y_minor=1, x_label='', y_label=unit[0].upper() + unit[1:],
               x_tick_fmt=lambda v: f'Q{(int(v) - 1) % 4 + 1}')
    pts = [(i + 1, v) for i, v in enumerate(vals)]
    body = ax.polyline(pts) + ax.marks(pts)
    body += _t(ax.sx(2.5), ax.sy(0) + 32, str(y1), 'note', fill=P['ink_muted']) + _t(ax.sx(6.5), ax.sy(0) + 32, str(y2), 'note', fill=P['ink_muted'])
    svg = ax.wrap(body, 'Time series graph', f'A time series of {what} over eight quarters.')
    q = (f'The time series graph shows the {what}, in {unit}, for each quarter of {y1} and {y2}.<br>{svg}<br>'
         f'Work out the mean quarterly value for {y1 if year == 0 else y2}. Give your answer in {unit}.')
    s = (f'The four values for {y1 if year == 0 else y2} are {", ".join(str(v) for v in four)}.<br>'
         f'Mean = ({" + ".join(str(v) for v in four)}) ÷ 4 = {sum(four)} ÷ 4 = <strong>{_text(mean)}</strong>.')
    hint = 'Read the four points for that year only, add them and divide by 4.'
    record('stats_series_mean', values=vals, year=year, years=(y1, y2), asked_year=y1 if year == 0 else y2,
           derived=('values', 'year'))
    return q, s, hint, 3, _num(mean)


# ─────────────────────────────────────────────────────────────────────────────
# Probability
# ─────────────────────────────────────────────────────────────────────────────

def _space_svg(n1, n2, op, name1, name2):
    """A sample space table: rows for the first spinner or die, columns for the second."""
    rows = []
    for a in range(1, n1 + 1):
        rows.append([str(a)] + [str(a + b if op == 'sum' else a * b) for b in range(1, n2 + 1)])
    return _svg_table([str(b) for b in range(1, n2 + 1)], rows, corner=f'{name1} \\ {name2}',
                      title='Sample space diagram', desc=f'A table of every {op} of the two scores.', cls='space',
                      col_w=[112] + [38] * n2, max_width=112 + 38 * n2 + 2)


def _space_event(op, n1, n2):
    """(event text, test) for a sample space question; the text names the event exactly as the solver reads it."""
    options = []
    if op == 'sum':
        equal, thresholds = range(3, n1 + n2), range(3, n1 + n2 - 1)
    else:
        equal, thresholds = (4, 6, 8, 10, 12, 16, 18, 20, 24), (6, 8, 10, 12, 15, 18, 20)
    for k in equal:
        options.append((f'equal to {k}', lambda v, k=k: v == k))
    for k in thresholds:
        options.append((f'more than {k}', lambda v, k=k: v > k))
        options.append((f'less than {k}', lambda v, k=k: v < k))
    options.append(('an even number', lambda v: v % 2 == 0))
    options.append(('an odd number', lambda v: v % 2 == 1))
    options.append(('a prime number', lambda v: v > 1 and all(v % d for d in range(2, math.isqrt(v) + 1))))
    options.append(('a square number', lambda v: math.isqrt(v) ** 2 == v))
    for k in (3, 4, 5, 6):
        options.append((f'a multiple of {k}', lambda v, k=k: v % k == 0))
    return options


def _space_question(n1, n2, op, name1, name2, intro, noun):
    events = _space_event(op, n1, n2)
    while True:
        text, test = events[random.randrange(len(events))]      # randrange: a list of pairs is walked by the test harness
        hits = sum(1 for a in range(1, n1 + 1) for b in range(1, n2 + 1) if test(a + b if op == 'sum' else a * b))
        if 2 <= hits <= n1 * n2 - 2:
            break
    svg = _space_svg(n1, n2, op, name1, name2)
    q = f'{intro}<br>{svg}<br>Find the probability that the {noun} is {text}.'
    s = (f'There are {n1} × {n2} = {n1 * n2} equally likely outcomes in the table.<br>'
         f'Count the outcomes where the {noun} is {text}: there are {hits}.<br>' + _prob_line(hits, n1 * n2))
    hint = 'Every cell of the table is one equally likely outcome. Count the cells that fit, then divide by the number of cells.'
    record('prob_sample_space', n1=n1, n2=n2, op=op, event_word=text)
    return q, s, hint, 2, _prob(hits, n1 * n2)


def gcse_prob_spinner_sum_space():
    """Foundational: two spinners, a sample space table of totals."""
    n1 = random.choice([3, 4])
    n2 = random.choice([3, 4, 5])
    intro = (f'Spinner A is numbered 1 to {n1} and spinner B is numbered 1 to {n2}. Both are fair. The two spinners are '
             f'spun and the scores are added to give a total. The sample space diagram shows every possible total.')
    return _space_question(n1, n2, 'sum', 'A', 'B', intro, 'total')


def gcse_prob_two_dice_sum():
    """Intermediate: two fair dice, the total score."""
    intro = ('Two fair six-sided dice are rolled and the scores are added together. The sample space diagram shows '
             'every possible total.')
    return _space_question(6, 6, 'sum', 'First', 'Second', intro, 'total')


def gcse_prob_two_dice_product():
    """Difficult: two fair dice, the product of the scores."""
    intro = ('Two fair six-sided dice are rolled and the two scores are multiplied together. The sample space diagram '
             'shows every possible product.')
    return _space_question(6, 6, 'product', 'First', 'Second', intro, 'product')


_FREQ_TREE = [
    # (people, group 1, group 2, property, not property, relative pronoun)
    ('people', 'adults', 'children', 'are vegetarian', 'are not vegetarian', 'who'),
    ('pupils', 'boys', 'girls', 'walk to school', 'do not walk', 'who'),
    ('customers', 'members', 'non-members', 'paid by card', 'paid in cash', 'who'),
    ('plants', 'roses', 'tulips', 'flowered', 'did not flower', 'that'),
]


def _tree_svg(root, a, b, aa, ab, ba, bb, labels):
    """A frequency tree: the root, two branches and four leaves, numbers (or letters) in boxes."""
    g1, g2, yes, no = labels
    # 430 wide (a phone shows it at about 0.57 scale; the older probability trees are 600 wide), branch labels 13 px
    W, H = 430, 240
    nodes = {'root': (30, 120, root), 'a': (186, 60, a), 'b': (186, 180, b),
             'aa': (396, 28, aa), 'ab': (396, 92, ab), 'ba': (396, 148, ba), 'bb': (396, 212, bb)}
    edges = [('root', 'a', g1), ('root', 'b', g2), ('a', 'aa', yes), ('a', 'ab', no), ('b', 'ba', yes), ('b', 'bb', no)]
    parts = []
    for u, v, lab in edges:
        x1, y1, _ = nodes[u]
        x2, y2, _ = nodes[v]
        parts.append(f'<line x1="{x1 + 26}" y1="{y1}" x2="{x2 - 26}" y2="{y2}" stroke="{P["ink_muted"]}" stroke-width="1.5"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dy = -7 if y2 < y1 else 16          # the label sits above a rising branch and below a falling one
        parts.append(f'<text class="branch" x="{mx:.1f}" y="{my + dy:.1f}" fill="{P["ink_muted"]}" font-size="13" '
                     f'text-anchor="middle">{svg_kit._esc(lab)}</text>')
    for key, (x, y, val) in nodes.items():
        parts.append(f'<rect x="{x - 26}" y="{y - 14}" width="52" height="28" rx="4" fill="{P["surface"]}" '
                     f'stroke="{P["brand"]}" stroke-width="1.5"/>')
        parts.append(f'<text class="node" data-k="{key}" x="{x}" y="{y + 5}" fill="{P["ink"]}" '
                     f'text-anchor="middle">{svg_kit._esc(val)}</text>')
    return _wrap(W, H, ''.join(parts), title='Frequency tree', desc='A frequency tree with two stages.', max_width=430)


def _tree_counts():
    while True:
        a = random.randint(20, 90)
        b = random.randint(20, 90)
        aa = random.randint(5, a - 5)
        ba = random.randint(5, b - 5)
        counts = (a + b, a, b, aa, a - aa, ba, b - ba)
        if len(set(counts)) == 7:
            return counts


def gcse_prob_frequency_tree_complete():
    """Foundational: three values missing from a frequency tree, worked out from the others."""
    people, g1, g2, yes, no, _who = random.choice(_FREQ_TREE)
    total, a, b, aa, ab, ba, bb = _tree_counts()
    svg = _tree_svg(str(total), str(a), 'a', str(aa), 'b', 'c', str(bb), (g1, g2, yes, no))
    q = (f'The frequency tree shows information about {total} {people}. {a} of them are {g1}. '
         f'Of the {g1}, {aa} {yes}. Of the {g2}, {bb} {no}.<br>{svg}<br>'
         f'Work out the values of a, b and c.')
    s = (f'a = {total} − {a} = <strong>{b}</strong> ({g2} altogether).<br>'
         f'b = {a} − {aa} = <strong>{ab}</strong> ({g1} who {no}).<br>'
         f'c = a − {bb} = {b} − {bb} = <strong>{ba}</strong> ({g2} who {yes}).')
    hint = 'The two branches from each box add up to the number in that box. Find the first branch before the second.'
    record('prob_freq_tree_fill', total=total, a=a, aa=aa, bb=bb)
    return q, s, hint, 3, _fields([b, ab, ba], ['a', 'b', 'c'])


def gcse_prob_frequency_tree_conditional():
    """Difficult: a conditional probability read from a completed frequency tree."""
    people, g1, g2, yes, no, who = random.choice(_FREQ_TREE)
    total, a, b, aa, ab, ba, bb = _tree_counts()
    svg = _tree_svg(str(total), str(a), str(b), str(aa), str(ab), str(ba), str(bb), (g1, g2, yes, no))
    which = random.choice(['yes_g1', 'yes_g2', 'no_g1', 'no_g2'])
    if which.startswith('yes'):
        cond, pool, cond_word = yes, aa + ba, yes
    else:
        cond, pool, cond_word = no, ab + bb, no
    want_g1 = which.endswith('g1')
    hits = (aa if cond == yes else ab) if want_g1 else (ba if cond == yes else bb)
    group = g1 if want_g1 else g2
    q = (f'The frequency tree shows information about {total} {people}.<br>{svg}<br>'
         f'One of the {people} {who} {cond_word} is chosen at random. Find the probability that this {_one(people)} '
         f'is one of the {group}.')
    s = (f'The {people} {who} {cond_word} are the two boxes on the "{cond}" branches: {aa if cond == yes else ab} + '
         f'{ba if cond == yes else bb} = {pool}.<br>'
         f'Of these, {hits} are {group}.<br>' + _prob_line(hits, pool))
    hint = 'The condition picks out a smaller group. Count that group first and use it as the bottom of the fraction.'
    record('prob_freq_tree_cond', aa=aa, ab=ab, ba=ba, bb=bb, cond='yes' if which.startswith('yes') else 'no',
           group='g1' if want_g1 else 'g2')
    return q, s, hint, 2, _prob(hits, pool)


def _two_way_prob_setup():
    spec = random.choice(_TWO_WAY)
    cells = _two_way_cells()
    return spec, cells, _two_way_svg(spec, cells, totals=True)


def gcse_prob_two_way_table():
    """Intermediate: a probability from a two-way table, out of everyone in the table."""
    spec, cells, svg = _two_way_prob_setup()
    row_word, col_word, cols, person, single, is_in = (
        spec[k] for k in ('row_word', 'col_word', 'cols', 'person', 'single', 'is_in'))
    grand = sum(map(sum, cells))
    i, j = random.randrange(2), random.randrange(3)
    ask = random.choice(['cell', 'col', 'row'])
    if ask == 'cell':
        hits = cells[i][j]
        event = f'{is_in[i]} and {single[cols[j]]}'
    elif ask == 'col':
        hits = cells[0][j] + cells[1][j]
        event = single[cols[j]]
    else:
        hits = sum(cells[i])
        event = is_in[i]
    q = (f'The two-way table shows information about some {_people(person)}, sorted by {row_word} and {col_word}.'
         f'<br>{svg}<br>One of the {_people(person)} is chosen at random. Find the probability that this {person} {event}.')
    s = (f'The {person} is chosen from everyone in the table, so the total is {grand}.<br>'
         f'Number of {_people(person)} who fit: {hits}.<br>' + _prob_line(hits, grand))
    hint = 'The bottom of the fraction is the number the choice is made from: here, everyone in the table.'
    words = {'cell': {'row_word': is_in[i], 'col_word': single[cols[j]]}, 'col': {'col_word': single[cols[j]]},
             'row': {'row_word': is_in[i]}}[ask]
    record('prob_two_way', cells=cells, ask=ask, row=i, col=j, derived=('row', 'col'), **words)
    return q, s, hint, 2, _prob(hits, grand)


def gcse_prob_two_way_conditional():
    """Difficult: a conditional probability from a two-way table (the choice is made from one group)."""
    spec, cells, svg = _two_way_prob_setup()
    row_word, rows_, col_word, cols, person, phrase, single, groups, is_in = (
        spec[k] for k in ('row_word', 'rows', 'col_word', 'cols', 'person', 'plural', 'single', 'groups', 'is_in'))
    i, j = random.randrange(2), random.randrange(3)
    ask = random.choice(['given_row', 'given_col'])
    hits = cells[i][j]
    if ask == 'given_row':
        pool = sum(cells[i])
        q_part = f'One of the {groups[i]} is chosen at random. Find the probability that this {person} {single[cols[j]]}.'
        where = f'the {rows_[i]} row total, {pool}'
    else:
        pool = cells[0][j] + cells[1][j]
        q_part = (f'One of the {_people(person)} {_rel(person)} {phrase[cols[j]]} is chosen at random. Find the '
                  f'probability that this {person} {is_in[i]}.')
        where = f'the {cols[j]} column total, {pool}'
    q = (f'The two-way table shows information about some {_people(person)}, sorted by {row_word} and {col_word}.'
         f'<br>{svg}<br>{q_part}')
    s = (f'The choice is made from a smaller group, so the total is {where}.<br>'
         f'Of these, {hits} fit the question.<br>' + _prob_line(hits, pool))
    hint = 'Read which group the choice is made from. That group\'s total is the bottom of the fraction, not the whole table.'
    words = ({'row_word': groups[i], 'col_word': single[cols[j]]} if ask == 'given_row' else
             {'row_word': is_in[i], 'col_word': phrase[cols[j]]})
    record('prob_two_way', cells=cells, ask=ask, row=i, col=j, derived=('row', 'col'), **words)
    return q, s, hint, 2, _prob(hits, pool)


def _venn_setup():
    a_only, b_only = random.randint(4, 24), random.randint(4, 24)
    both, neither = random.randint(3, 14), random.randint(2, 16)
    total = a_only + b_only + both + neither
    svg = str(svg_kit.venn2(a_only, b_only, both, neither))
    context = random.choice([
        # (survey, plural phrase for A, plural for B, singular for A, singular for B)
        ('a school survey', 'play football', 'play hockey', 'plays football', 'plays hockey'),
        ('a library survey', 'borrow novels', 'borrow comics', 'borrows novels', 'borrows comics'),
        ('a cafe survey', 'drink tea', 'drink coffee', 'drinks tea', 'drinks coffee'),
        ('a club survey', 'swim', 'cycle', 'swims', 'cycles'),
    ])
    return a_only, b_only, both, neither, total, svg, context


_VENN_SETS = {
    'A ∪ B': (lambda a, b, c, d: a + b + c, 'A ∪ B means in A or in B or in both, so count everyone inside the two circles'),
    'A ∩ B': (lambda a, b, c, d: c, 'A ∩ B means in both A and B, so count the overlap only'),
    "A'": (lambda a, b, c, d: b + d, "A' means not in A, so count B only and neither"),
    "A' ∩ B": (lambda a, b, c, d: b, "A' ∩ B means in B but not in A, so count the B only region"),
    "A ∩ B'": (lambda a, b, c, d: a, "A ∩ B' means in A but not in B, so count the A only region"),
    "(A ∪ B)'": (lambda a, b, c, d: d, "(A ∪ B)' means in neither A nor B, so count outside both circles"),
}


def _venn_question(ask):
    a_only, b_only, both, neither, total, svg, (survey, do_a, do_b, _sa, _sb) = _venn_setup()
    count_fn, meaning = _VENN_SETS[ask]
    hits = count_fn(a_only, b_only, both, neither)
    q = (f'In {survey} of {total} people, A is the set of people who {do_a} and B is the set of people who {do_b}. '
         f'The Venn diagram shows the results.<br>{svg}<br>One of the {total} people is chosen at random. Find P({ask}).')
    s = f'{meaning}: {hits} people.<br>' + _prob_line(hits, total).replace('Probability', f'P({ask})')
    record('prob_venn_set', a_only=a_only, b_only=b_only, both=both, neither=neither, ask_word=ask)
    return q, s, hits, total


def gcse_prob_venn_union():
    """Intermediate: P(A ∪ B) or P(A ∩ B) from a Venn diagram, in set notation."""
    ask = random.choice(['A ∪ B', 'A ∩ B'])
    q, s, hits, total = _venn_question(ask)
    hint = 'The symbol ∪ (union) means in either set or both; ∩ (intersection) means in both sets at once.'
    return q, s, hint, 2, _prob(hits, total)


def gcse_prob_venn_set_notation():
    """Difficult: a complement in set notation (A', A' ∩ B, A ∩ B', (A ∪ B)') from a Venn diagram."""
    ask = random.choice(["A'", "A' ∩ B", "A ∩ B'", "(A ∪ B)'"])
    q, s, hits, total = _venn_question(ask)
    hint = "A dash means the complement: everything that is not in that set. Shade the region first, then count it."
    return q, s, hint, 2, _prob(hits, total)


# ─────────────────────────────────────────────────────────────────────────────
# Graphs
# ─────────────────────────────────────────────────────────────────────────────

_GRADIENTS = [Fraction(v) for v in (2, 3, 4, 5, -2, -3, -4, -5)] + \
    [Fraction(n, d) for n, d in ((1, 2), (1, 3), (1, 4), (1, 5), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (2, 3), (-2, 3), (3, 2), (-3, 2))]


def _tex_frac(m):
    """A gradient in TeX: 3, -3, \\frac{1}{2}, and a negative fraction in brackets, \\left(-\\frac{1}{2}\\right)."""
    m = Fraction(m)
    if m.denominator == 1:
        return str(m.numerator)
    body = rf'\frac{{{abs(m.numerator)}}}{{{m.denominator}}}'
    return rf'\left(-{body}\right)' if m < 0 else body


def _tex_line(m, c, var='x'):
    """TeX for y = mx + c with a fraction gradient written as \\frac."""
    m = Fraction(m)
    if m.denominator == 1:
        mx = ('-' if m < 0 else '') + (var if abs(m) == 1 else f'{abs(m)}{var}')
    else:
        mx = ('-' if m < 0 else '') + rf'\frac{{{abs(m.numerator)}}}{{{m.denominator}}}{var}'
    if c == 0:
        return f'y = {mx}'
    return f'y = {mx} {"+" if c > 0 else "-"} {abs(c)}'


def gcse_gra_perpendicular_gradient():
    """Intermediate: the gradient of a line perpendicular to a given line (negative reciprocal)."""
    m = random.choice(_GRADIENTS)
    c = random.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
    perp = -1 / m
    form = random.choice(['equation', 'gradient'])
    if form == 'equation':
        q = rf'Line L has the equation \( {_tex_line(m, c)} \). Write down the gradient of a line that is perpendicular to L.'
        s_first = rf'The gradient of L is the number in front of x: \( {_tex_frac(m)} \).<br>'
    else:
        q = rf'A straight line has gradient \( {_tex_frac(m)} \). Write down the gradient of a line perpendicular to it.'
        s_first = ''
    s = (s_first +
         rf'Perpendicular gradients multiply to give −1, so the perpendicular gradient is \( -1 \div {_tex_frac(m)} \).<br>'
         rf'Turn the gradient upside down and change its sign: <strong>\( {_tex_frac(perp)} \)</strong>.')
    hint = 'The product of the two gradients is −1. Flip the fraction over and change the sign.'
    record('gr_perp_gradient', m_num=m.numerator, m_den=m.denominator, derived=('m_num', 'm_den'))
    return q, s, hint, 1, _fraction(perp)


def gcse_gra_perpendicular_line():
    """Difficult: the equation of the perpendicular to a given line through a given point (y = mx + c)."""
    while True:
        m = random.choice([Fraction(n, d) for n, d in ((1, 2), (-1, 2), (1, 3), (-1, 3), (1, 4), (-1, 4), (1, 5), (-1, 5), (1, 1), (-1, 1))])
        c = random.randint(-6, 6)
        x1, y1 = random.randint(-6, 6), random.randint(-6, 6)
        perp = -1 / m
        c2 = y1 - perp * x1
        if c != 0 and x1 != 0 and y1 != 0 and c2 != 0 and abs(c2) != abs(c) and abs(c2) <= 30 and y1 != m * x1 + c:
            break
    q = (rf'Line L has the equation \( {_tex_line(m, c)} \). Find the equation of the line that is perpendicular to L '
         rf'and passes through the point \( ({x1}, {y1}) \). Give your answer in the form \( y = mx + c \).')
    s = (rf'The gradient of L is \( {_tex_frac(m)} \), so the perpendicular gradient is \( -1 \div {_tex_frac(m)} = {int(perp)} \).<br>'
         rf'The new line is \( y = {_sign_text(int(perp), 0)} + c \). Put in \( ({x1}, {y1}) \): '
         rf'\( {y1} = {_br(int(perp))} \times {_br(x1)} + c \), so \( c = {y1} - {_br(int(perp * x1))} = {int(c2)} \).<br>'
         rf'Equation: <strong>\( {_tex_line(perp, int(c2))} \)</strong>.')
    hint = 'Find the perpendicular gradient first (flip and change the sign), then use the point to find c.'
    record('gr_perp_line', m_num=m.numerator, m_den=m.denominator, c=c, x1=x1, y1=y1, derived=('m_num', 'm_den'))
    return q, s, hint, 3, _line_eq(perp, c2)


def gcse_gra_circle_equation():
    """Difficult: k in x^2 + y^2 = k for a circle with centre O through a given point."""
    # Whole-change review C11: the second draw type (read the radius off x^2 + y^2 = r^2) was a one-step recall item in
    # the difficult tier and is dropped; only the point-on-circle question remains.
    while True:
        if random.random() < 0.35:
            x, y = random.choice([(3, 4), (4, 3), (6, 8), (8, 6), (5, 12), (12, 5), (8, 15), (15, 8), (9, 12), (12, 9)])
            x, y = x * random.choice([1, -1]), y * random.choice([1, -1])
        else:
            x, y = random.randint(-9, 9), random.randint(-9, 9)
        k = x * x + y * y
        if x != 0 and y != 0 and abs(x) != abs(y) and k != abs(x) + abs(y):
            break
    q = (rf'A circle has centre O, the origin, and passes through the point \( ({x}, {y}) \). '
         rf'The equation of the circle is \( x^2 + y^2 = k \). Work out the value of k.')
    r_note = (f' The radius is √{k} = {math.isqrt(k)}, so k is the radius squared, not the radius.'
              if math.isqrt(k) ** 2 == k else f' The radius is √{k}, so k is the radius squared, not the radius.')
    s = (rf'Every point on the circle is the same distance from O, and \( x^2 + y^2 \) is that distance squared.<br>'
         rf'Put the point in: \( k = {_br(x)}^2 + {_br(y)}^2 = {x * x} + {y * y} = \) <strong>{k}</strong>.{r_note}')
    hint = 'A point on the circle satisfies its equation. Put the x and y values into x² + y².'
    record('gr_circle_k', ask='k', x=x, y=y)
    return q, s, hint, 2, _num(k)


# |y| >= 2: with |y| = 1 the tangent y = -ax + k printed both numbers of its answer in the question (review C12)
_TANGENT_POINTS = [(4, 2), (6, 2), (8, 2), (10, 2), (6, 3), (9, 3), (12, 3), (8, 4), (12, 4), (10, 5), (12, 6)]


def gcse_gra_circle_tangent():
    """Difficult: the tangent to x^2 + y^2 = k at a point on the circle (gradient perpendicular to the radius)."""
    a, b = random.choice(_TANGENT_POINTS)
    a *= random.choice([1, -1])
    b *= random.choice([1, -1])
    k = a * a + b * b
    m_rad = Fraction(b, a)
    m_tan = -1 / m_rad
    c = b - m_tan * a
    q = (rf'The circle \( x^2 + y^2 = {k} \) has centre O. The point P\( ({a}, {b}) \) lies on the circle. '
         rf'Find the equation of the tangent to the circle at P. Give your answer in the form \( y = mx + c \).')
    s = (rf'The gradient of the radius OP, from \( (0, 0) \) to \( ({a}, {b}) \), is \( {_br(b)} \div {_br(a)} = {_tex_frac(m_rad)} \).<br>'
         rf'The tangent is perpendicular to the radius, so its gradient is \( -1 \div {_tex_frac(m_rad)} = {int(m_tan)} \).<br>'
         rf'Through P: \( {b} = {_br(int(m_tan))} \times {_br(a)} + c \), so \( c = {b} - {_br(int(m_tan * a))} = {int(c)} \).<br>'
         rf'Tangent: <strong>\( {_tex_line(m_tan, int(c))} \)</strong>.')
    hint = 'The tangent is at right angles to the radius OP. Find the gradient of OP, then the perpendicular gradient, then use P.'
    record('gr_tangent', a=a, b=b, k=k)
    return q, s, hint, 4, _line_eq(m_tan, c)


def _vt_draw():
    """(v, t1, t2, t3): a trapezium-shaped journey with whole-number acceleration and distance."""
    while True:
        v = random.choice([4, 6, 8, 10, 12, 15, 16, 18, 20, 24, 30])
        t1, t2, t3 = random.choice([2, 4, 5, 6, 8, 10]), random.choice([4, 5, 6, 8, 10, 12]), random.choice([2, 4, 5, 6, 8, 10])
        if t1 + t2 + t3 > 30:
            continue
        acc, dec = Fraction(v, t1), Fraction(v, t3)
        dist = Fraction(v * t1, 2) + v * t2 + Fraction(v * t3, 2)
        printed = {t1, t2, t3, t1 + t2 + t3, v}
        # the slips the hint rules name (the area of a sloping part typed for a gradient, the middle rectangle typed
        # for the distance) must not land on a printed number either, or a copied number gets a wrong cause
        slips = {Fraction(v * t1, 2), Fraction(v * t3, 2), v * t2}
        if acc != dec and (acc * 4).denominator == 1 and (dec * 4).denominator == 1 and dist.denominator == 1 \
                and acc not in printed and dec not in printed and dist not in printed and not (slips & printed):
            return v, t1, t2, t3


def _vt_svg(v, t1, t2, t3):
    total = t1 + t2 + t3
    x_step = 5 if total > 12 else 2
    y_step = next(st for st in (2, 4, 5, 6) if v % st == 0 and v // st <= 8)      # v itself is a labelled tick
    ax = _Axes(0, total, 0, (v // y_step + 1) * y_step, x_step, y_step, x_minor=1, y_minor=1,
               x_label='Time (seconds)', y_label='Velocity (m/s)')
    pts = [(0, 0), (t1, v), (t1 + t2, v), (total, 0)]
    body = ax.polyline(pts) + ax.marks(pts[1:3], r=3.5)
    return ax.wrap(body, 'Velocity-time graph', 'A velocity-time graph of a journey in three stages.')


def gcse_gra_vt_acceleration():
    """Intermediate: acceleration as the gradient of a velocity-time graph."""
    v, t1, t2, t3 = _vt_draw()
    svg = _vt_svg(v, t1, t2, t3)
    vehicle = random.choice(['car', 'train', 'cyclist', 'lorry', 'runner'])
    ask = random.choice(['first', 'last'])
    t = t1 if ask == 'first' else t3
    acc = Fraction(v, t)
    q = (f'The velocity-time graph shows the first {t1 + t2 + t3} seconds of the journey of a {vehicle}.<br>{svg}<br>'
         + (f'Work out the acceleration of the {vehicle} during the first {t1} seconds.' if ask == 'first' else
            f'Work out the deceleration of the {vehicle} during the last {t3} seconds.'))
    s = (f'Acceleration is the gradient of the velocity-time graph.<br>'
         + (f'In the first {t1} seconds the velocity goes from 0 to {v} m/s.<br>'
            f'Acceleration = {v} ÷ {t1} = <strong>{_text(acc)}</strong> m/s².' if ask == 'first' else
            f'In the last {t3} seconds the velocity goes from {v} m/s down to 0.<br>'
            f'Deceleration = {v} ÷ {t3} = <strong>{_text(acc)}</strong> m/s².'))
    hint = 'Acceleration is the change in velocity divided by the time taken: the gradient of that part of the graph.'
    record('gr_vt', v=v, t1=t1, t2=t2, t3=t3, ask=ask, t_asked=t, derived=('t1', 't2', 't3'))
    return q, s, hint, 2, _num(acc, f'Enter the {"acceleration" if ask == "first" else "deceleration"} in m/s²')


def gcse_gra_vt_distance():
    """Difficult: distance as the area under a velocity-time graph (a trapezium)."""
    v, t1, t2, t3 = _vt_draw()
    svg = _vt_svg(v, t1, t2, t3)
    vehicle = random.choice(['car', 'train', 'cyclist', 'lorry', 'runner'])
    total = t1 + t2 + t3
    d1, d2, d3 = Fraction(v * t1, 2), v * t2, Fraction(v * t3, 2)
    dist = d1 + d2 + d3
    q = (f'The velocity-time graph shows the journey of a {vehicle}, which lasts {total} seconds.<br>{svg}<br>'
         f'Work out the total distance travelled by the {vehicle}.')
    s = (f'Distance is the area under the velocity-time graph. Split it into a triangle, a rectangle and a triangle.<br>'
         f'First {t1} s: ½ × {t1} × {v} = {_text(d1)} m.<br>'
         f'Next {t2} s: {t2} × {v} = {d2} m.<br>'
         f'Last {t3} s: ½ × {t3} × {v} = {_text(d3)} m.<br>'
         f'Total distance = {_text(d1)} + {d2} + {_text(d3)} = <strong>{int(dist)}</strong> m.')
    hint = 'The distance is the area between the graph and the time axis. Split the shape into triangles and a rectangle.'
    record('gr_vt', v=v, t1=t1, t2=t2, t3=t3, ask='distance', t_asked=total, derived=('t1', 't2', 't3'))
    return q, s, hint, 3, _num(dist, 'Enter the distance in metres')


_TRANSFORMS = [
    # (TeX of the new curve, how the point moves, explanation)
    ('f(x) + {a}', lambda x, y, a: (x, y + a), 'y = f(x) + {a} moves the graph up by {a}: add {a} to the y-coordinate'),
    ('f(x) - {a}', lambda x, y, a: (x, y - a), 'y = f(x) − {a} moves the graph down by {a}: subtract {a} from the y-coordinate'),
    ('f(x + {a})', lambda x, y, a: (x - a, y), 'y = f(x + {a}) moves the graph {a} {u} to the left: subtract {a} from the x-coordinate'),
    ('f(x - {a})', lambda x, y, a: (x + a, y), 'y = f(x − {a}) moves the graph {a} {u} to the right: add {a} to the x-coordinate'),
    ('-f(x)', lambda x, y, a: (x, -y), 'y = −f(x) reflects the graph in the x-axis: the y-coordinate changes sign'),
    ('f(-x)', lambda x, y, a: (-x, y), 'y = f(−x) reflects the graph in the y-axis: the x-coordinate changes sign'),
]


def gcse_gra_transformation_point():
    """Difficult: where a point of y = f(x) goes under f(x) + a, f(x + a), -f(x) or f(-x)."""
    while True:
        tex, move, why = _TRANSFORMS[random.randrange(len(_TRANSFORMS))]
        a = random.randint(1, 6) if '{a}' in tex else 0
        x, y = random.randint(-7, 7), random.randint(-7, 7)
        if x == 0 or y == 0:
            continue
        nx, ny = move(x, y, a)
        changed = nx if nx != x else ny
        # x != y: with (4, 4) the swapped pair (10, 4) is also the inside-outside slip, so the hint could name the wrong cause
        if (nx, ny) != (x, y) and abs(nx) <= 12 and abs(ny) <= 12 and nx != 0 and ny != 0 and changed not in (x, y) and x != y:
            break
    kind = tex.replace('{a}', str(a))
    name = random.choice(['P', 'A', 'M', 'Q'])
    what = random.choice(['lies on', 'is the maximum point of', 'is the minimum point of'])
    feature = None if what == 'lies on' else what.split()[2]
    # y = -f(x) turns the graph over, so the image of a maximum is a minimum (review 2026-10-28: the question used
    # to ask for "the maximum point" of y = -f(x), which is the image of a point the pupil is not given)
    if feature and tex == '-f(x)':
        feature = 'minimum' if feature == 'maximum' else 'maximum'
    where = 'the image of this point' if feature is None else f'the {feature} point'
    q = (rf'The point {name}\( ({x}, {y}) \) {what} the curve \( y = f(x) \). '
         rf'Write down the coordinates of {where} on the curve \( y = {kind} \).')
    s = (f'{why.replace("{a}", str(a)).replace("{u}", "unit" if a == 1 else "units")}.<br>'
         + (f'The graph is turned upside down, so the {what.split()[2]} point of y = f(x) becomes the {feature} point '
            f'of y = {kind}.<br>' if feature and tex == '-f(x)' else '')
         + rf'\( ({x}, {y}) \) becomes <strong>\( ({nx}, {ny}) \)</strong>.')
    if tex in ('-f(x)', 'f(-x)'):
        hint = 'A minus sign outside f reflects the graph in the x-axis; a minus sign inside the bracket reflects it in the y-axis.'
    else:
        hint = 'A number added outside f moves the graph up or down; a number inside the bracket moves it sideways, the opposite way to its sign.'
    record('gr_transform_point', kind=tex, a=a, x=x, y=y)
    return q, s, hint, 2, _pair(nx, ny)


def gcse_gra_exponential_read():
    """Difficult: a and b of y = a × b^x read from the drawn curve (its points at x = 0, 1, 2, 3)."""
    # Every case keeps the points at x = 0, 1 and 2 (the ones the solution reads) on a faint grid line: minor lines
    # are every unit up to 30 and every 2 above, so (1, 4), (2, 4) and (81, 3) are out (review 2026-10-28).
    growth = random.choice([True, True, False])
    if growth:
        a, b = random.choice([(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (1, 3), (2, 3)])
        ys = [a * b ** i for i in range(4)]
        b_text = str(b)
    else:
        a, b = random.choice([(16, 2), (24, 2), (32, 2), (40, 2), (48, 2), (56, 2), (64, 2), (72, 2), (80, 2),
                              (27, 3), (54, 3), (64, 4)])
        ys = [a // b ** i for i in range(4)]
        b_text = _frac_text(Fraction(1, b))
        b = Fraction(1, b)
    y_max = max(ys)
    y_step = 10 if y_max > 40 else 5 if y_max > 16 else 2
    top = (y_max // y_step + 1) * y_step
    ax = _Axes(0, 3.5, 0, top, 1, y_step, x_minor=0.5, y_minor=1 if top <= 30 else y_step / 5, x_label='x', y_label='y')
    curve = [(i / 20, a * float(b) ** (i / 20)) for i in range(0, 71)]
    pts = list(zip(range(4), ys))
    body = ax.polyline(curve) + ax.marks(pts)
    svg = ax.wrap(body, 'Exponential graph', 'The graph of y = a times b to the power x, with four marked points.')
    q = (rf'The graph shows the curve \( y = a \times b^x \), where a and b are positive constants. '
         rf'The marked points have whole-number coordinates.<br>{svg}<br>Use the graph to find the values of a and b.')
    s = (rf'At \( x = 0 \), \( b^0 = 1 \), so \( y = a \). Reading the graph at x = 0: <strong>a = {a}</strong>.<br>'
         rf'At \( x = 1 \), \( y = a \times b = {ys[1]} \), so \( b = {ys[1]} \div {a} = \) <strong>{b_text}</strong>.<br>'
         rf'Check at x = 2: \( {a} \times {("(" + b_text + ")") if "/" in str(b_text) else b_text}^2 = {ys[2]} \), which matches the graph.')
    hint = 'The y-intercept gives a. Then compare y at x = 1 with y at x = 0: the graph multiplies by b each time x goes up by 1.'
    record('gr_exponential', ys=ys, derived=('ys',))
    return q, s, hint, 3, _fields([a, b_text], ['a', 'b'])


# ─────────────────────────────────────────────────────────────────────────────
# Ratio and proportion
# ─────────────────────────────────────────────────────────────────────────────

def gcse_ratio_proportional_cube():
    """Difficult: y proportional to the cube of x; find k, then y or x."""
    k = Fraction(random.choice([2, 3, 4, 5, 10]))
    ask = random.choice(['y', 'x'])
    while True:
        x1, x2 = random.sample([2, 3, 4, 5, 6], 2)       # x = 1 would make k x^3 = k (no cube to take)
        y1, y2 = k * x1 ** 3, k * x2 ** 3
        if y1.denominator == 1 and y2.denominator == 1 and y1 != y2 and y1 not in (x1, x2) and y2 not in (x1, x2):
            break
    if ask == 'y':
        q = (f'y is directly proportional to the cube of x. When x = {x1}, y = {int(y1)}. '
             f'Find the value of y when x = {x2}.')
        s = (f'y = kx³. Substitute x = {x1} and y = {int(y1)}: {int(y1)} = k × {x1 ** 3}, so k = {_frac_text(k)}.<br>'
             f'When x = {x2}: y = {_frac_text(k)} × {x2}³ = {_frac_text(k)} × {x2 ** 3} = <strong>{int(y2)}</strong>.')
        key = y2
        record('prop_power', p=3, x1=x1, y1=int(y1), given='x', x2=x2, derived=('p',))
    else:
        q = (f'y is directly proportional to the cube of x. When x = {x1}, y = {int(y1)}. '
             f'Find the value of x when y = {int(y2)}.')
        s = (f'y = kx³. Substitute x = {x1} and y = {int(y1)}: {int(y1)} = k × {x1 ** 3}, so k = {_frac_text(k)}.<br>'
             f'When y = {int(y2)}: {int(y2)} = {_frac_text(k)}x³, so x³ = {int(y2)} ÷ {_frac_text(k)} = {x2 ** 3} '
             f'and x = ∛{x2 ** 3} = <strong>{x2}</strong>.')
        key = x2
        record('prop_power', p=3, x1=x1, y1=int(y1), given='y', y2=int(y2), derived=('p',))
    hint = 'Write y = kx³, find k from the pair of values you are given, then use the formula for the new value.'
    return q, s, hint, 3, _num(key)


def gcse_ratio_proportional_root():
    """Difficult: y proportional to the square root of x; find k, then y or x."""
    k = random.choice([2, 3, 4, 5, 6, 10])
    ask = random.choice(['y', 'x'])
    while True:
        r1, r2 = random.sample([2, 3, 4, 5, 6, 7, 8, 9, 10], 2)
        x1, x2 = r1 * r1, r2 * r2
        y1, y2 = k * r1, k * r2
        if y1 not in (x1, x2) and y2 not in (x1, x2) and y1 != k:
            break
    if ask == 'y':
        q = (f'y is directly proportional to the square root of x. When x = {x1}, y = {y1}. '
             f'Find the value of y when x = {x2}.')
        s = (f'y = k√x. Substitute x = {x1} and y = {y1}: {y1} = k × √{x1} = {r1}k, so k = {k}.<br>'
             f'When x = {x2}: y = {k} × √{x2} = {k} × {r2} = <strong>{y2}</strong>.')
        key = y2
        record('prop_root', x1=x1, y1=y1, given='x', x2=x2)
    else:
        q = (f'y is directly proportional to the square root of x. When x = {x1}, y = {y1}. '
             f'Find the value of x when y = {y2}.')
        s = (f'y = k√x. Substitute x = {x1} and y = {y1}: {y1} = k × √{x1} = {r1}k, so k = {k}.<br>'
             f'When y = {y2}: {y2} = {k}√x, so √x = {r2} and x = {r2}² = <strong>{x2}</strong>.')
        key = x2
        record('prop_root', x1=x1, y1=y1, given='y', y2=y2)
    hint = 'Write y = k√x, find k from the pair of values you are given, then use the formula for the new value.'
    return q, s, hint, 3, _num(key)


def gcse_ratio_inverse_square():
    """Difficult: y inversely proportional to the square of x; find k, then y or x."""
    ask = random.choice(['y', 'x'])
    while True:
        x1, x2 = random.sample([1, 2, 3, 4, 5, 6, 10], 2)
        k = random.choice([36, 48, 50, 72, 80, 100, 144, 150, 180, 200, 288, 300, 400])
        y1, y2 = Fraction(k, x1 * x1), Fraction(k, x2 * x2)
        if y1.denominator == 1 and y2.denominator == 1 and x1 != 1 and y1 not in (1, x1, x2, k) and y2 not in (1, x1, x2, k) \
                and y1 != y2:
            break
    y1, y2 = int(y1), int(y2)
    if ask == 'y':
        q = (f'y is inversely proportional to the square of x. When x = {x1}, y = {y1}. '
             f'Find the value of y when x = {x2}.')
        s = (f'y = k/x². Substitute x = {x1} and y = {y1}: {y1} = k ÷ {x1 * x1}, so k = {y1} × {x1 * x1} = {k}.<br>'
             f'When x = {x2}: y = {k} ÷ {x2}² = {k} ÷ {x2 * x2} = <strong>{y2}</strong>.')
        key = y2
        record('prop_inverse_square', x1=x1, y1=y1, given='x', x2=x2)
    else:
        q = (f'y is inversely proportional to the square of x. When x = {x1}, y = {y1}. '
             f'Find the positive value of x when y = {y2}.')
        s = (f'y = k/x². Substitute x = {x1} and y = {y1}: {y1} = k ÷ {x1 * x1}, so k = {y1} × {x1 * x1} = {k}.<br>'
             f'When y = {y2}: {y2} = {k} ÷ x², so x² = {k} ÷ {y2} = {x2 * x2} and x = <strong>{x2}</strong>.')
        key = x2
        record('prop_inverse_square', x1=x1, y1=y1, given='y', y2=y2)
    hint = 'Write y = k/x² (k over x squared), find k from the pair of values you are given, then use the formula.'
    return q, s, hint, 3, _num(key)


def _ct(n):
    return 't' if n == 1 else f'{n}t'


def _mul(k, sep=''):
    """A multiplier written before a bracket or a term: nothing for 1, else the number (and a separator)."""
    return '' if k == 1 else f'{k}{sep}'


def _times(k, t):
    """'5 × 6' for the working line '5t = 5 × 6 = 30', or just '6' for a coefficient of 1."""
    return str(t) if k == 1 else f'{k} × {t}'


def gcse_ratio_change_after_adding():
    """Difficult: a ratio changes when some items are added; find a starting amount."""
    item, c1, c2 = random.choice([('counters', 'red', 'blue'), ('sweets', 'orange', 'lemon'), ('marbles', 'green', 'white'),
                                  ('beads', 'black', 'silver')])
    while True:
        a, b = random.randint(1, 5), random.randint(1, 5)
        c, d = random.randint(1, 6), random.randint(1, 6)
        n = random.choice([4, 6, 8, 10, 12, 15, 18, 20, 24, 30])
        if math.gcd(a, b) != 1 or math.gcd(c, d) != 1 or Fraction(a, b) == Fraction(c, d) or Fraction(c, d) <= Fraction(a, b):
            continue
        # red = a t, blue = b t; (a t + n) / (b t) = c / d  ->  t (a d - b c) = -n d  ->  t = n d / (b c - a d)
        den = b * c - a * d
        if den <= 0:
            continue
        t = Fraction(n * d, den)
        if t.denominator != 1 or t < 2:
            continue
        t = int(t)
        red, blue = a * t, b * t
        if blue in (n, a, b, c, d) or red + blue in (n, a, b, c, d) or blue > 200:
            continue
        break
    ask = random.choice(['blue', 'total'])
    key = blue if ask == 'blue' else red + blue
    q = (f'A bag contains {c1} {item} and {c2} {item} in the ratio {a} : {b}. '
         f'{n} more {c1} {item} are put in the bag. The ratio of {c1} to {c2} {item} is now {c} : {d}. '
         + (f'How many {c2} {item} are in the bag?' if ask == 'blue' else f'How many {item} were in the bag at the start?'))
    s = (f'Let the bag have {_ct(a)} {c1} and {_ct(b)} {c2} {item} at the start.<br>'
         f'After {n} more {c1}: ({_ct(a)} + {n}) : {_ct(b)} = {c} : {d}, so {_mul(d)}({_ct(a)} + {n}) = {_mul(c, " × ")}{_ct(b)}.<br>'
         f'{_ct(a * d)} + {n * d} = {_ct(b * c)}, so ' + (f'{_ct(den)} = {n * d} and t = {t}.<br>' if den != 1 else f't = {t}.<br>')
         + (f'{c2.capitalize()} {item}: {_ct(b)} = {_times(b, t) + " = " if b != 1 else ""}<strong>{blue}</strong>.' if ask == 'blue' else
            f'At the start: {_ct(a)} + {_ct(b)} = {_times(a, t)} + {_times(b, t)} = {red} + {blue} = '
            f'<strong>{red + blue}</strong> {item}.'))
    hint = ('Call the two amounts at the start a multiple of the first ratio, add the extra to one of them, and set the new '
            'pair equal to the new ratio.')
    record('ratio_change', a=a, b=b, n=n, c=c, d=d, ask=ask)
    return q, s, hint, 4, _num(key)


def gcse_ratio_recipe_limiting():
    """Difficult: the greatest number that can be made when one ingredient runs out first."""
    thing, per, ing1, u1, ing2, u2 = random.choice([
        ('cakes', 12, 'flour', 'g', 'eggs', ''), ('biscuits', 20, 'butter', 'g', 'sugar', 'g'),
        ('pancakes', 8, 'milk', 'ml', 'eggs', ''), ('muffins', 10, 'flour', 'g', 'milk', 'ml'),
    ])
    while True:
        a1 = random.choice([100, 120, 150, 200, 240, 250, 300]) if u1 else random.randint(2, 4)
        a2 = random.choice([2, 3, 4, 5]) if not u2 else random.choice([50, 60, 75, 80, 100, 120, 150])
        have1 = a1 * random.choice([Fraction(k, 2) for k in range(3, 13)])
        have2 = a2 * random.choice([Fraction(k, 2) for k in range(3, 13)])
        if have1.denominator != 1 or have2.denominator != 1:
            continue
        have1, have2 = int(have1), int(have2)
        m1, m2 = Fraction(have1 * per, a1), Fraction(have2 * per, a2)
        if m1 == m2 or m1.denominator != 1 or m2.denominator != 1 or have1 == a1 or have2 == a2:
            continue
        if not u2 and have2 > 30:
            continue
        if min(m1, m2) in (per, a1, a2, have1, have2):
            continue
        break
    best = min(m1, m2)
    q = (f'A recipe for {per} {thing} needs {a1} {u1} of {ing1} and {a2} {u2 + " of " if u2 else ""}{ing2}. '
         f'Sam has {have1} {u1} of {ing1} and {have2} {u2 + " of " if u2 else ""}{ing2}. '
         f'What is the greatest number of {thing} Sam can make?')
    short = ing1 if m1 < m2 else ing2
    s = (f'{ing1.capitalize()}: {have1} ÷ {a1} = {_text(Fraction(have1, a1))} batches, enough for {int(m1)} {thing}.<br>'
         f'{ing2.capitalize()}: {have2} ÷ {a2} = {_text(Fraction(have2, a2))} batches, enough for {int(m2)} {thing}.<br>'
         f'There {"are" if short == "eggs" else "is"} not enough {short} for more than that, so the greatest number is '
         f'<strong>{int(best)}</strong>.')
    hint = 'Work out how many could be made from each ingredient on its own. The smaller number is the answer.'
    record('ratio_limiting', per=per, a1=a1, a2=a2, have1=have1, have2=have2)
    return q, s, hint, 3, _num(best)


# ─────────────────────────────────────────────────────────────────────────────
# Trigonometry
# ─────────────────────────────────────────────────────────────────────────────

def _trig_graph_svg(fn):
    ax = _Axes(0, 360, -1, 1, 90, 0.5, x_minor=30, y_minor=0.25, x_label='x (degrees)', y_label=f'y = {fn} x')
    f = math.sin if fn == 'sin' else math.cos
    curve = [(x, f(math.radians(x))) for x in range(0, 361, 5)]
    body = ax.polyline(curve)
    return ax.wrap(body, f'Graph of y = {fn} x', f'The graph of y = {fn} x from 0 to 360 degrees.')


_TRIG_READ = {
    # (fn, k): every solution of fn x = k in 0 < x < 360 that lies on the grid (30 degree lines, quarter lines)
    ('sin', Fraction(1, 2)): (30, 150), ('sin', Fraction(-1, 2)): (210, 330), ('sin', Fraction(0)): (180,),
    ('sin', Fraction(1)): (90,), ('sin', Fraction(-1)): (270,),
    ('cos', Fraction(1, 2)): (60, 300), ('cos', Fraction(-1, 2)): (120, 240), ('cos', Fraction(0)): (90, 270),
    ('cos', Fraction(-1)): (180,),
}


def gcse_trig_graph_read():
    """Intermediate: read a solution of sin x = k or cos x = k from the graph, within a stated range."""
    (fn, k), sols = random.choice(list(_TRIG_READ.items()))
    x = sols[random.randrange(len(sols))]
    half = random.choice([30, 45, 60])
    lo, hi = max(0, x - half), min(360, x + half)
    svg = _trig_graph_svg(fn)
    q = (f'The graph shows y = {fn} x for 0° ≤ x ≤ 360°.<br>{svg}<br>'
         f'Use the graph to find the value of x, where {lo}° ≤ x ≤ {hi}°, for which {fn} x = {_text(k)}.')
    all_sols = [v for v in range(0, 361, 30) if abs((math.sin if fn == "sin" else math.cos)(math.radians(v)) - float(k)) < 1e-9]
    others = [v for v in all_sols if v != x]
    s = (f'Draw the line y = {_text(k)} across the graph. It meets the curve at x = '
         f'{", ".join(f"{v}°" for v in all_sols)}.<br>'
         f'Only x = {x}° is between {lo}° and {hi}°, so x = <strong>{x}</strong>°'
         + (f' (the other solution{"s" if len(others) > 1 else ""}, {", ".join(f"{v}°" for v in others)}, '
            f'{"are" if len(others) > 1 else "is"} outside the range).' if others else '.'))
    hint = f'Draw a horizontal line at y = {_text(k)} and read across to the curve, then down to the x-axis.'
    record('trig_graph_read', fn_word=fn, k=_text(k), lo=lo, hi=hi)
    return q, s, hint, 2, _num(x)


def gcse_trig_solve_two_solutions():
    """Difficult: both solutions of sin x = k, cos x = k or tan x = k in 0 to 360 degrees, to 1 decimal place."""
    fn = random.choice(['sin', 'cos', 'tan'])
    while True:
        if fn == 'tan':
            k = Fraction(random.randint(2, 35), 10)
        else:
            k = Fraction(random.randint(5, 95), 100)
        if fn == 'sin':
            x1 = math.degrees(math.asin(float(k)))
            x2 = 180 - x1
        elif fn == 'cos':
            x1 = math.degrees(math.acos(float(k)))
            x2 = 360 - x1
        else:
            x1 = math.degrees(math.atan(float(k)))
            x2 = x1 + 180
        r1, r2 = fmt_dp(x1, 1), fmt_dp(x2, 1)
        # not within 0.02 of a whole degree, and not within 0.003 of a 1 d.p. rounding boundary (xx.x5), where a
        # calculator display rounded to 2 d.p. first would give the other neighbour (review 2026-10-28)
        if r1 != r2 and abs(x1 - round(x1)) > 0.02 and abs((x1 * 10) % 1 - 0.5) > 0.03:
            break
    rule = {'sin': 'the second solution is 180° − the first', 'cos': 'the second solution is 360° − the first',
            'tan': 'the second solution is the first + 180°'}[fn]
    q = (f'Solve {fn} x = {_text(k)} for 0° ≤ x ≤ 360°. Give both solutions, correct to 1 decimal place.')
    inv = {'sin': 'sin⁻¹', 'cos': 'cos⁻¹', 'tan': 'tan⁻¹'}[fn]
    s = (f'First solution: x = {inv}({_text(k)}) = {r1}°.<br>'
         f'From the symmetry of the {fn} graph, {rule}: '
         + {'sin': f'180 − {r1} = {r2}°', 'cos': f'360 − {r1} = {r2}°', 'tan': f'{r1} + 180 = {r2}°'}[fn] + '.<br>'
         f'Solutions: <strong>{r1}°</strong> and <strong>{r2}°</strong>.')
    hint = f'Use the inverse function for the first solution, then use the shape of the {fn} graph to find the second one.'
    record('trig_solve_k', fn_word=fn, k=_text(k))
    return q, s, hint, 3, _fields([r1, r2], ['Smaller solution (degrees)', 'Larger solution (degrees)'],
                                  hint='Enter each solution to 1 decimal place')


def gcse_trig_graph_feature():
    """Intermediate: coordinates of a maximum, minimum, axis crossing or grid point of y = sin x or y = cos x."""
    fn = random.choice(['sin', 'cos'])
    feats = {'sin': [('maximum point of the graph', (90, 1)), ('minimum point of the graph', (270, -1)),
                     ('point where the graph crosses the x-axis between 90° and 270°', (180, 0))],
             'cos': [('minimum point of the graph', (180, -1)),
                     ('point where the graph crosses the x-axis between 0° and 180°', (90, 0)),
                     ('point where the graph crosses the x-axis between 180° and 360°', (270, 0))]}
    grid_x = {'sin': (30, 150, 210, 330), 'cos': (60, 120, 240, 300)}
    if random.random() < 0.4:
        x = random.choice(grid_x[fn])
        y = Fraction(1, 2) * (1 if (math.sin if fn == 'sin' else math.cos)(math.radians(x)) > 0 else -1)
        name = f'point on the curve where x = {x}'
    else:
        name, (x, y) = random.choice(feats[fn])
    svg = _trig_graph_svg(fn)
    q = (f'The graph shows y = {fn} x for 0° ≤ x ≤ 360°.<br>{svg}<br>'
         f'Write down the coordinates of the {name}.')
    if name.startswith('point on the curve'):
        s = f'Reading up from x = {x}° to the curve and across to the y-axis gives y = {_text(y)}.<br>'
    else:
        s = (f'Reading from the graph, the {name.split(" between")[0].replace(" of the graph", "")} is at x = {x}°, '
             f'where y = {_text(y)}.<br>')
    s += f'Coordinates: <strong>({x}, {_text(y)})</strong>.'
    hint = 'Find the feature on the curve, then read its x-value from the horizontal axis and its y-value from the vertical axis.'
    record('trig_graph_feature', fn_word=fn, feature_word=name)
    return q, s, hint, 2, _pair(x, y, 'x', 'y')


def gcse_prob_venn_conditional():
    """Difficult: a conditional probability from a Venn diagram (the choice is made from one set)."""
    a_only, b_only, both, neither, total, svg, (survey, do_a, do_b, single_a, single_b) = _venn_setup()
    given = random.choice(['A', 'B'])
    pool = a_only + both if given == 'A' else b_only + both
    do_given, does_other, other = (do_a, single_b, 'B') if given == 'A' else (do_b, single_a, 'A')
    q = (f'In {survey} of {total} people, A is the set of people who {do_a} and B is the set of people who {do_b}. '
         f'The Venn diagram shows the results.<br>{svg}<br>One of the people who {do_given} is chosen at random. '
         f'Find the probability that this person also {does_other}.')
    s = (f'The choice is made from set {given} only: {given} only ({a_only if given == "A" else b_only}) plus the overlap '
         f'({both}), which is {pool} people.<br>'
         f'Of these, the {both} in the overlap are also in {other}.<br>' + _prob_line(both, pool))
    hint = 'The people chosen from are the whole of one circle, including its overlap. Use that circle\'s total as the bottom.'
    record('prob_venn_set', a_only=a_only, b_only=b_only, both=both, neither=neither, ask_word=f'who {do_given}',
           given=given)
    return q, s, hint, 2, _prob(both, pool)
