"""Solvers for the Phase 3 batch C1 record families (docs/GCSE_MATHS_VARIETY.md section 21): statistics,
probability, graphs, ratio and trigonometry.

Independence rule: these recompute each answer from the numbers the pupil is shown, from first principles, with the
standard library and sympy only. They must not import any generator module or helper (checked by the test).

The drawn questions are checked against the drawing itself (``@diagram``): the tables, trees, polygons, series and
graphs are read back from the SVG the pupil sees (text elements carry a class, tick labels calibrate the axes), and
compared with the recorded inputs, so a drawing and its key cannot disagree.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

import sympy

from .core import Approx, Cannot, Pick
from .registry import diagram, fr, solver
from .solvers_algebra import Ctx, judge
from .latex import strip_html
from .solvers_svg import Axis, elements, one_svg, read_venn2

_CLASSED = re.compile(r'<text class="([a-z]+)"([^>]*)>(.*?)</text>', re.S)
_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
_TAG = re.compile(r'<[^>]+>')


def _unescape(t):
    return t.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#8722;', '-').replace('−', '-')


def classed_texts(svg):
    """[(class, x, y, text, attrs)] for every text element that carries a class."""
    out = []
    for m in _CLASSED.finditer(svg):
        a = dict(_ATTR.findall(m.group(2)))
        out.append((m.group(1), float(a['x']), float(a['y']), _unescape(_TAG.sub('', m.group(3)).strip()), a))
    return out


def read_grid(svg, body_classes=('cell', 'rowhead', 'leaves', 'space')):
    """The drawn table as rows of text (the header row first), read from the text positions."""
    rows = {}
    for cls, x, y, t, _ in classed_texts(svg):
        if cls in ('head',) + tuple(body_classes):
            rows.setdefault(round(y), []).append((x, t))
    if len(rows) < 2:
        raise Cannot('the table drawing has fewer than two rows')
    return [[t for _, t in sorted(rows[y])] for y in sorted(rows)]


def _axis(svg, cls):
    """Calibrate an axis from its tick labels (class tx or ty); every label must sit on the line through the end ones
    (a label that has been changed, even by one unit, makes the axis unreadable)."""
    pairs = []
    for c, x, y, t, _ in classed_texts(svg):
        if c == cls:
            try:
                v = Fraction(t)
            except ValueError:
                continue
            pairs.append(((x if cls == 'tx' else y - 4), v))     # a y label's baseline sits 4px under its tick
    axis = Axis(pairs)
    span = max(v for _, v in pairs) - min(v for _, v in pairs)
    for px, v in pairs:
        if abs(axis.value(px) - v) > float(span) * 0.004 + 1e-9:
            raise Cannot(f'the tick labelled {v} is not where its value puts it on the {cls} axis')
    return axis


def read_marks(svg):
    """[(x value, y value)] of the marked points, read through the tick labels."""
    ax, ay = _axis(svg, 'tx'), _axis(svg, 'ty')
    pts = [(ax.value(float(c['cx'])), ay.value(float(c['cy']))) for c in elements(svg, 'circle') if c.get('class') == 'mark']
    if not pts:
        raise Cannot('no marked points found')
    return sorted(pts)


def read_series(svg):
    """[(x value, y value)] of the polyline vertices."""
    ax, ay = _axis(svg, 'tx'), _axis(svg, 'ty')
    m = re.search(r'<polyline class="series" points="([^"]*)"', svg)
    if not m:
        raise Cannot('no series polyline found')
    pts = []
    for pair in m.group(1).split():
        px, py = (float(v) for v in pair.split(','))
        pts.append((ax.value(px), ay.value(py)))
    return pts


def read_marks_y_order(svg):
    """y values of the marked points in left-to-right order (a categorical x axis)."""
    ay = _axis(svg, 'ty')
    marks = sorted((float(c['cx']), float(c['cy'])) for c in elements(svg, 'circle') if c.get('class') == 'mark')
    if not marks:
        raise Cannot('no marked points found')
    return [ay.value(cy) for _, cy in marks]


def _near(a, b, tol=0.12):
    return abs(float(a) - float(b)) <= tol


def _grid_mismatch(rows, want):
    """Messages where the drawn table rows (text) differ from the expected rows (text)."""
    out = []
    if len(rows) != len(want):
        return [f'the table has {len(rows)} rows but {len(want)} were expected']
    for i, (got, exp) in enumerate(zip(rows, want)):
        g = [str(x) for x in got]
        e = [str(x) for x in exp]
        if g != e:
            out.append(f'row {i} of the table reads {g} but the question was built with {e}')
    return out


# ───────────────────────── statistics: two-way tables ─────────────────────────

@solver('stats_two_way_read')
def _stats_two_way_read(cells, ask, index, group_word=None):
    cells = [[fr(v) for v in row] for row in cells]
    if ask == 'row':
        return [sum(cells[int(index)])]
    if ask == 'col':
        return [sum(row[int(index)] for row in cells)]
    if ask == 'all':
        return [sum(sum(row) for row in cells)]
    raise Cannot(f'unknown ask {ask!r}')


@diagram('stats_two_way_read')
def _check_two_way_read(inputs, html):
    rows = read_grid(one_svg(html))
    body = [r[1:] for r in rows[1:]]
    want = [[str(v) for v in row] for row in inputs['cells']]
    return [] if body == want else [f'the table body reads {body} but the question was built with {want}']


@solver('stats_two_way_complete')
def _stats_two_way_complete(r0c1, r0c2, r1c0, row0, row1, col0, col1, col2, grand):
    r0c1, r0c2, r1c0, row0, row1, col0, col1, col2, grand = (fr(v) for v in (r0c1, r0c2, r1c0, row0, row1, col0, col1, col2, grand))
    a = row0 - r0c1 - r0c2
    b = col1 - r0c1
    c = col2 - r0c2
    if a <= 0 or b <= 0 or c <= 0:
        raise Cannot('a missing cell is not positive')
    if a + r1c0 != col0 or r1c0 + b + c != row1 or row0 + row1 != grand or col0 + col1 + col2 != grand:
        raise Cannot('the totals of the table do not agree with each other')
    return [a, b, c]


@diagram('stats_two_way_complete')
def _check_two_way_complete(inputs, html):
    rows = read_grid(one_svg(html))
    i = inputs
    want = [['a', str(i['r0c1']), str(i['r0c2']), str(i['row0'])], [str(i['r1c0']), 'b', 'c', str(i['row1'])],
            [str(i['col0']), str(i['col1']), str(i['col2']), str(i['grand'])]]
    body = [r[1:] for r in rows[1:]]
    if rows[0][-1] != 'Total' or rows[-1][0] != 'Total':
        return ['the table has no Total row or column']
    return [] if body == want else [f'the table body reads {body} but the question was built with {want}']


@solver('stats_two_way_percent')
def _stats_two_way_percent(cells, row, col, group_word=None, col_word=None):
    cells = [[fr(v) for v in r] for r in cells]
    return [100 * cells[int(row)][int(col)] / sum(cells[int(row)])]


def _check_two_way_totals(cells, html):
    rows = read_grid(one_svg(html))
    cells = [[int(v) for v in r] for r in cells]
    want = [[str(v) for v in r] + [str(sum(r))] for r in cells]
    want.append([str(sum(r[j] for r in cells)) for j in range(len(cells[0]))] + [str(sum(map(sum, cells)))])
    body = [r[1:] for r in rows[1:]]
    return [] if body == want else [f'the table body reads {body} but the question was built with {want}']


@diagram('stats_two_way_percent')
def _check_two_way_percent(inputs, html):
    return _check_two_way_totals(inputs['cells'], html)


# ───────────────────────── statistics: stem and leaf, tables ─────────────────────────

def _stem_values(stems, leaves):
    vals = []
    for st, row in zip(stems, leaves):
        for leaf in row:
            vals.append(10 * int(st) + int(leaf))
    if vals != sorted(vals):
        raise Cannot('the leaves are not in order')
    return vals


@solver('stats_stem_leaf')
def _stats_stem_leaf(stems, leaves, ask):
    vals = _stem_values(stems, leaves)
    n = len(vals)
    if ask == 'median':
        if n % 2 == 0:
            raise Cannot('an even number of values: the median is not a single value')
        return [Fraction(vals[n // 2])]
    if ask == 'range':
        return [Fraction(vals[-1] - vals[0])]
    if ask == 'iqr':
        if (n + 1) % 4:
            raise Cannot('the quartile positions are not whole numbers')
        return [Fraction(vals[3 * (n + 1) // 4 - 1] - vals[(n + 1) // 4 - 1])]
    raise Cannot(f'unknown ask {ask!r}')


@diagram('stats_stem_leaf')
def _check_stem_leaf(inputs, html):
    rows = read_grid(one_svg(html))
    want = [[str(st), ' '.join(str(x) for x in row)] for st, row in zip(inputs['stems'], inputs['leaves'])]
    body = rows[1:]
    out = [] if body == want else [f'the diagram reads {body} but the question was built with {want}']
    key = re.search(r'Key:\s*(\d+)\s*\|\s*(\d)\s*means\s*(\d+)', html)
    if not key or int(key.group(1)) * 10 + int(key.group(2)) != int(key.group(3)):
        out.append('the key line does not read "stem | leaf means stem-leaf"')
    return out


def _table_rows_check(values, freqs, html, unknown=None):
    rows = read_grid(one_svg(html))
    want = [[str(v), 'x' if f is None else str(f)] for v, f in zip(values, freqs)]
    body = rows[1:]
    return [] if body == want else [f'the table reads {body} but the question was built with {want}']


@solver('stats_table_mode')
def _stats_table_mode(values, freqs):
    freqs = [int(f) for f in freqs]
    top = max(freqs)
    if freqs.count(top) != 1:
        raise Cannot('the table has more than one mode')
    return [fr(values[freqs.index(top)])]


@diagram('stats_table_mode')
def _check_table_mode(inputs, html):
    return _table_rows_check(inputs['values'], inputs['freqs'], html)


@solver('stats_table_median')
def _stats_table_median(values, freqs):
    n = sum(int(f) for f in freqs)
    if n % 2 == 0:
        raise Cannot('an even total: the median may fall between two values')
    pos, running = (n + 1) // 2, 0
    for v, f in zip(values, freqs):
        running += int(f)
        if running >= pos:
            return [fr(v)]
    raise Cannot('the frequencies do not reach the median position')


@diagram('stats_table_median')
def _check_table_median(inputs, html):
    return _table_rows_check(inputs['values'], inputs['freqs'], html)


@solver('stats_missing_value')
def _stats_missing_value(n, mean, known):
    if len(known) != int(n) - 1:
        raise Cannot('the number of known values does not match n')
    return [fr(mean) * int(n) - sum(fr(k) for k in known)]


@solver('stats_missing_freq')
def _stats_missing_freq(values, freqs, mean):
    mean = fr(mean)
    unknown = [i for i, f in enumerate(freqs) if f is None]
    if len(unknown) != 1:
        raise Cannot('exactly one frequency must be unknown')
    k = unknown[0]
    x = sympy.Symbol('x')
    total_f = sum(int(f) for f in freqs if f is not None) + x
    total_fx = sum(fr(v) * int(f) for v, f in zip(values, freqs) if f is not None) + fr(values[k]) * x
    sols = sympy.solve(sympy.Eq(total_fx, sympy.Rational(mean.numerator, mean.denominator) * total_f), x)
    if len(sols) != 1 or not sols[0].is_integer or sols[0] <= 0:
        raise Cannot(f'the mean does not give one positive whole frequency: {sols}')
    return [Fraction(int(sols[0]))]


@diagram('stats_missing_freq')
def _check_missing_freq(inputs, html):
    return _table_rows_check(inputs['values'], inputs['freqs'], html)


@solver('stats_combined_mean')
def _stats_combined_mean(n1, m1, n2, m2):
    n1, m1, n2, m2 = (fr(v) for v in (n1, m1, n2, m2))
    return [(n1 * m1 + n2 * m2) / (n1 + n2)]


@solver('stats_sample_scale')
def _stats_sample_scale(hits, sample, pop):
    if fr(hits) > fr(sample):
        raise Cannot('more hits than the sample size')
    return [fr(hits) / fr(sample) * fr(pop)]


@solver('stats_recapture')
def _stats_recapture(m, n, k):
    if fr(k) > fr(n) or fr(k) <= 0:
        raise Cannot('the tagged count in the second sample is impossible')
    return [fr(m) * fr(n) / fr(k)]


@solver('stats_median_class')
def _stats_median_class(intervals, freqs):
    n = sum(int(f) for f in freqs)
    pos = Fraction(n + 1, 2)
    running, chosen = 0, None
    for (lo, hi), f in zip(intervals, freqs):
        running += int(f)
        if n % 2 == 0 and running == n // 2:
            # the n/2-th value ends this class and the (n/2 + 1)-th starts the next: the n/2 rule used for grouped
            # data and the (n + 1)/2 rule name different classes, so the question has no single answer
            raise Cannot(f'the median of {n} values falls between two classes')
        if chosen is None and running >= pos:
            chosen = (fr(lo), fr(hi))
    if chosen is None:
        raise Cannot('the frequencies do not reach the median position')

    def test(text):
        nums = [Fraction(t) for t in re.findall(r'-?\d+(?:\.\d+)?', _unescape(text))]
        return len(nums) == 2 and (nums[0], nums[1]) == chosen
    return [Pick(test, f'the class from {chosen[0]} to {chosen[1]} contains the median')]


@diagram('stats_median_class')
def _check_median_class(inputs, html):
    rows = read_grid(one_svg(html))
    body = rows[1:]
    out = []
    if len(body) != len(inputs['intervals']):
        return [f'the table has {len(body)} classes but {len(inputs["intervals"])} were recorded']
    for (lo, hi), f, row in zip(inputs['intervals'], inputs['freqs'], body):
        nums = re.findall(r'-?\d+', row[0])
        if [int(x) for x in nums[:2]] != [int(lo), int(hi)] or row[1] != str(f):
            out.append(f'the table row {row} does not match the class {lo} to {hi} with frequency {f}')
    return out


# ───────────────────────── statistics: drawn polygon and series ─────────────────────────

@solver('stats_polygon')
def _stats_polygon(intervals, freqs, ask):
    freqs = [fr(f) for f in freqs]
    if ask == 'total':
        return [sum(freqs)]
    if ask == 'mean':
        mids = [(fr(lo) + fr(hi)) / 2 for lo, hi in intervals]
        return [sum(m * f for m, f in zip(mids, freqs)) / sum(freqs)]
    raise Cannot(f'unknown ask {ask!r}')


@diagram('stats_polygon')
def _check_polygon(inputs, html):
    svg = one_svg(html)
    marks = read_marks(svg)
    series = read_series(svg)
    want = [((fr(lo) + fr(hi)) / 2, fr(f)) for (lo, hi), f in zip(inputs['intervals'], inputs['freqs'])]
    out = []
    if len(marks) != len(want):
        return [f'{len(marks)} points are drawn but {len(want)} classes were recorded']
    for (gx, gy), (wx, wy) in zip(marks, want):
        if not _near(gx, wx, 0.6) or not _near(gy, wy):
            out.append(f'a point is drawn at ({gx:.2f}, {gy:.2f}) but the class midpoint and frequency are ({wx}, {wy})')
    if len(series) != len(want) or any(not _near(sy, wy) for (_, sy), (_, wy) in zip(sorted(series), want)):
        out.append('the polygon line does not pass through the recorded points')
    return out


@solver('stats_series_mean')
def _stats_series_mean(values, year, years=None, asked_year=None):
    if asked_year is not None:
        # C8: the year is the one the sentence prints, not an index into the drawing
        if asked_year not in years:
            raise Cannot(f'the asked year {asked_year} is not one of the years {years}')
        year = list(years).index(asked_year)
    four = [fr(v) for v in values[4 * int(year):4 * int(year) + 4]]
    if len(four) != 4:
        raise Cannot('the year does not have four quarters')
    return [sum(four) / 4]


@diagram('stats_series_mean')
def _check_series(inputs, html):
    out = []
    asked = re.search(r'mean quarterly value for (\d{4})', strip_html(html, keep_svg_text=False))
    if inputs.get('asked_year') is not None and (not asked or int(asked.group(1)) != int(inputs['asked_year'])):
        out.append(f'the question asks for {asked.group(1) if asked else "no year"} but the key is the mean for {inputs["asked_year"]}')
    ys = read_marks_y_order(one_svg(html))
    want = [fr(v) for v in inputs['values']]
    if len(ys) != len(want):
        return out + [f'{len(ys)} points are drawn but {len(want)} values were recorded']
    return out + [f'point {i + 1} is drawn at {gy:.2f} but the question was built with {wy}'
            for i, (gy, wy) in enumerate(zip(ys, want)) if not _near(gy, wy)]


# ───────────────────────── probability ─────────────────────────

_EVENTS = (
    (re.compile(r'equal to (\d+)$'), lambda m: (lambda v: v == int(m.group(1)))),
    (re.compile(r'more than (\d+)$'), lambda m: (lambda v: v > int(m.group(1)))),
    (re.compile(r'less than (\d+)$'), lambda m: (lambda v: v < int(m.group(1)))),
    (re.compile(r'an even number$'), lambda m: (lambda v: v % 2 == 0)),
    (re.compile(r'an odd number$'), lambda m: (lambda v: v % 2 == 1)),
    (re.compile(r'a prime number$'), lambda m: (lambda v: v > 1 and all(v % d for d in range(2, int(math.isqrt(v)) + 1)))),
    (re.compile(r'a square number$'), lambda m: (lambda v: math.isqrt(v) ** 2 == v)),
    (re.compile(r'a multiple of (\d+)$'), lambda m: (lambda v: v % int(m.group(1)) == 0)),
)


def _event_test(text):
    t = str(text).strip().lower()
    for pattern, make in _EVENTS:
        m = pattern.match(t)
        if m:
            return make(m)
    raise Cannot(f'cannot read the event {text!r}')


@solver('prob_sample_space')
def _prob_sample_space(n1, n2, op, event_word):
    n1, n2 = int(n1), int(n2)
    test = _event_test(event_word)
    outcomes = [(a + b if op == 'sum' else a * b) for a in range(1, n1 + 1) for b in range(1, n2 + 1)]
    hits = sum(1 for v in outcomes if test(v))
    if hits == 0 or hits == len(outcomes):
        raise Cannot('the event is impossible or certain')
    return [Fraction(hits, len(outcomes))]


@diagram('prob_sample_space')
def _check_sample_space(inputs, html):
    rows = read_grid(one_svg(html))
    n1, n2, op = int(inputs['n1']), int(inputs['n2']), inputs['op']
    want = [[str(a + b if op == 'sum' else a * b) for b in range(1, n2 + 1)] for a in range(1, n1 + 1)]
    heads = rows[0][1:]
    body = [r[1:] for r in rows[1:]]
    out = []
    if heads != [str(b) for b in range(1, n2 + 1)] or [r[0] for r in rows[1:]] != [str(a) for a in range(1, n1 + 1)]:
        out.append('the row or column headings of the sample space are not 1 to n')
    if body != want:
        out.append(f'the sample space reads {body} but every {op} should give {want}')
    return out


def _tree_nodes(html):
    svg = one_svg(html)
    nodes = {}
    for cls, x, y, t, a in classed_texts(svg):
        if cls == 'node':
            nodes[a.get('data-k')] = t
    if set(nodes) != {'root', 'a', 'b', 'aa', 'ab', 'ba', 'bb'}:
        raise Cannot('the frequency tree does not have seven boxes')
    return nodes


@solver('prob_freq_tree_fill')
def _prob_freq_tree_fill(total, a, aa, bb):
    total, a, aa, bb = (fr(v) for v in (total, a, aa, bb))
    b = total - a
    ab = a - aa
    ba = b - bb
    if min(b, ab, ba) <= 0:
        raise Cannot('a box of the tree is not positive')
    return [b, ab, ba]


@diagram('prob_freq_tree_fill')
def _check_tree_fill(inputs, html):
    nodes = _tree_nodes(html)
    want = {'root': str(inputs['total']), 'a': str(inputs['a']), 'aa': str(inputs['aa']), 'bb': str(inputs['bb']),
            'b': 'a', 'ab': 'b', 'ba': 'c'}
    return [f'box {k} shows {nodes[k]!r} but should show {v!r}' for k, v in want.items() if nodes[k] != v]


@solver('prob_freq_tree_cond')
def _prob_freq_tree_cond(aa, ab, ba, bb, cond, group):
    aa, ab, ba, bb = (fr(v) for v in (aa, ab, ba, bb))
    pool = (aa + ba) if cond == 'yes' else (ab + bb)
    if group == 'g1':
        hits = aa if cond == 'yes' else ab
    elif group == 'g2':
        hits = ba if cond == 'yes' else bb
    else:
        raise Cannot(f'unknown group {group!r}')
    return [hits / pool]


@diagram('prob_freq_tree_cond')
def _check_tree_cond(inputs, html):
    nodes = _tree_nodes(html)
    aa, ab, ba, bb = (int(inputs[k]) for k in ('aa', 'ab', 'ba', 'bb'))
    want = {'aa': aa, 'ab': ab, 'ba': ba, 'bb': bb, 'a': aa + ab, 'b': ba + bb, 'root': aa + ab + ba + bb}
    return [f'box {k} shows {nodes[k]!r} but should show {v}' for k, v in want.items() if nodes[k] != str(v)]


@solver('prob_two_way')
def _prob_two_way(cells, ask, row, col, row_word=None, col_word=None):
    cells = [[fr(v) for v in r] for r in cells]
    i, j = int(row), int(col)
    grand = sum(sum(r) for r in cells)
    if ask == 'cell':
        return [cells[i][j] / grand]
    if ask == 'col':
        return [sum(r[j] for r in cells) / grand]
    if ask == 'row':
        return [sum(cells[i]) / grand]
    if ask == 'given_row':
        return [cells[i][j] / sum(cells[i])]
    if ask == 'given_col':
        return [cells[i][j] / sum(r[j] for r in cells)]
    raise Cannot(f'unknown ask {ask!r}')


@diagram('prob_two_way')
def _check_prob_two_way(inputs, html):
    return _check_two_way_totals(inputs['cells'], html)


@solver('prob_venn_set')
def _prob_venn_set(a_only, b_only, both, neither, ask_word, given=None):
    a, b, c, d = (fr(v) for v in (a_only, b_only, both, neither))
    total = a + b + c + d
    if given is not None:
        # a conditional probability: chosen from one circle (including its overlap), in the other circle too
        if given == 'A':
            return [c / (a + c)]
        if given == 'B':
            return [c / (b + c)]
        raise Cannot(f'unknown given set {given!r}')
    sets = {'A ∪ B': a + b + c, 'A ∩ B': c, "A'": b + d, "A' ∩ B": b, "A ∩ B'": a, "(A ∪ B)'": d}
    if ask_word not in sets:
        raise Cannot(f'cannot read the set {ask_word!r}')
    return [sets[ask_word] / total]


@diagram('prob_venn_set')
def _check_venn_set(inputs, html):
    drawn = read_venn2(one_svg(html))
    out = [f'the diagram shows {drawn[k]} for {k} but the question was built with {inputs[k]}'
           for k in ('a_only', 'b_only', 'both', 'neither') if drawn[k] != fr(inputs[k])]
    total = sum(fr(inputs[k]) for k in ('a_only', 'b_only', 'both', 'neither'))
    if drawn['total'] != total:
        out.append(f'the diagram total is {drawn["total"]} but the regions add to {total}')
    return out


# ───────────────────────── graphs ─────────────────────────

@solver('gr_perp_gradient')
def _gr_perp_gradient(m_num, m_den):
    m = Fraction(int(m_num), int(m_den))
    if m == 0:
        raise Cannot('a horizontal line has no perpendicular gradient')
    return [-1 / m]


@solver('gr_perp_line', problem=True)
def _gr_perp_line(_p, _records, m_num, m_den, c, x1, y1):
    m = Fraction(int(m_num), int(m_den))
    perp = -1 / m
    c2 = fr(y1) - perp * fr(x1)
    return judge(Ctx(_p, {}), 'tuple', [sympy.Rational(perp.numerator, perp.denominator),
                                        sympy.Rational(c2.numerator, c2.denominator)])


@solver('gr_circle_k')
def _gr_circle_k(ask, x=None, y=None, k=None):
    if ask == 'k':
        return [fr(x) ** 2 + fr(y) ** 2]
    if ask == 'radius':
        k = fr(k)
        r = math.isqrt(int(k))
        if r * r != k:
            raise Cannot(f'{k} is not a square number')
        return [Fraction(r)]
    raise Cannot(f'unknown ask {ask!r}')


@solver('gr_tangent', problem=True)
def _gr_tangent(_p, _records, a, b, k):
    a, b, k = (fr(v) for v in (a, b, k))
    if a * a + b * b != k:
        raise Cannot(f'the point ({a}, {b}) is not on the circle x^2 + y^2 = {k}')
    if b == 0:
        raise Cannot('a vertical tangent has no y = mx + c form')
    m = -a / b
    c = b - m * a
    return judge(Ctx(_p, {}), 'tuple', [sympy.Rational(m.numerator, m.denominator), sympy.Rational(c.numerator, c.denominator)])


@solver('gr_vt')
def _gr_vt(v, t1, t2, t3, ask, t_asked=None):
    v, t1, t2, t3 = (fr(x) for x in (v, t1, t2, t3))
    if ask == 'first':
        return [v / t1]
    if ask == 'last':
        return [v / t3]
    if ask == 'distance':
        return [v * t1 / 2 + v * t2 + v * t3 / 2]
    raise Cannot(f'unknown ask {ask!r}')


@diagram('gr_vt')
def _check_vt(inputs, html):
    series = read_series(one_svg(html))
    v, t1, t2, t3 = (fr(inputs[k]) for k in ('v', 't1', 't2', 't3'))
    want = [(0, 0), (t1, v), (t1 + t2, v), (t1 + t2 + t3, 0)]
    if len(series) != 4:
        return [f'the graph has {len(series)} vertices, not 4']
    return [f'vertex {i + 1} is drawn at ({gx:.2f}, {gy:.2f}) but should be ({wx}, {wy})'
            for i, ((gx, gy), (wx, wy)) in enumerate(zip(series, want)) if not _near(gx, wx, 0.2) or not _near(gy, wy, 0.2)]


@solver('gr_transform_point')
def _gr_transform_point(kind, a, x, y):
    a, x, y = (fr(v) for v in (a, x, y))
    moves = {'f(x) + {a}': (x, y + a), 'f(x) - {a}': (x, y - a), 'f(x + {a})': (x - a, y), 'f(x - {a})': (x + a, y),
             '-f(x)': (x, -y), 'f(-x)': (-x, y)}
    if kind not in moves:
        raise Cannot(f'unknown transformation {kind!r}')
    return list(moves[kind])


@solver('gr_exponential')
def _gr_exponential(ys):
    ys = [fr(v) for v in ys]
    if len(ys) < 3 or ys[0] <= 0:
        raise Cannot('fewer than three points')
    a = ys[0]
    b = ys[1] / a
    for i in range(2, len(ys)):
        if ys[i] != a * b ** i:
            raise Cannot('the points are not on one exponential curve')
    return [a, b]


@diagram('gr_exponential')
def _check_exponential(inputs, html):
    marks = read_marks(one_svg(html))
    want = [(i, fr(v)) for i, v in enumerate(inputs['ys'])]
    if len(marks) != len(want):
        return [f'{len(marks)} points are marked but {len(want)} were recorded']
    return [f'a point is marked at ({gx:.2f}, {gy:.2f}) but should be at ({wx}, {wy})'
            for (gx, gy), (wx, wy) in zip(marks, want) if not _near(gx, wx, 0.05) or not _near(gy, wy, 0.4)]


# ───────────────────────── ratio and proportion ─────────────────────────

@solver('prop_power')
def _prop_power(p, x1, y1, given, x2=None, y2=None):
    p, x1, y1 = int(p), fr(x1), fr(y1)
    k = y1 / x1 ** p
    if given == 'x':
        return [k * fr(x2) ** p]
    if given == 'y':
        ratio = fr(y2) / k
        root = sympy.root(sympy.Rational(ratio.numerator, ratio.denominator), p)
        if not root.is_rational:
            raise Cannot('x is not a whole number or fraction')
        return [Fraction(str(root))]
    raise Cannot(f'unknown given {given!r}')


@solver('prop_root')
def _prop_root(x1, y1, given, x2=None, y2=None):
    x1, y1 = fr(x1), fr(y1)
    r1 = math.isqrt(int(x1))
    if r1 * r1 != x1:
        raise Cannot(f'{x1} is not a square number')
    k = y1 / r1
    if given == 'x':
        r2 = math.isqrt(int(fr(x2)))
        if r2 * r2 != fr(x2):
            raise Cannot(f'{x2} is not a square number')
        return [k * r2]
    if given == 'y':
        return [(fr(y2) / k) ** 2]
    raise Cannot(f'unknown given {given!r}')


@solver('prop_inverse_square')
def _prop_inverse_square(x1, y1, given, x2=None, y2=None):
    x1, y1 = fr(x1), fr(y1)
    k = y1 * x1 ** 2
    if given == 'x':
        return [k / fr(x2) ** 2]
    if given == 'y':
        sq = k / fr(y2)
        r = math.isqrt(int(sq))
        if r * r != sq:
            raise Cannot('x squared is not a square number')
        return [Fraction(r)]
    raise Cannot(f'unknown given {given!r}')


@solver('ratio_change')
def _ratio_change(a, b, n, c, d, ask):
    a, b, n, c, d = (fr(v) for v in (a, b, n, c, d))
    # (a t + n) / (b t) = c / d
    den = b * c - a * d
    if den == 0:
        raise Cannot('the ratio does not change')
    t = n * d / den
    if t <= 0:
        raise Cannot('no positive number of parts')
    if ask == 'blue':
        return [b * t]
    if ask == 'total':
        return [(a + b) * t]
    raise Cannot(f'unknown ask {ask!r}')


@solver('ratio_limiting')
def _ratio_limiting(per, a1, a2, have1, have2):
    per, a1, a2, have1, have2 = (fr(v) for v in (per, a1, a2, have1, have2))
    return [min(have1 / a1 * per, have2 / a2 * per)]


# ───────────────────────── trigonometry ─────────────────────────

_TRIG = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan}


@solver('trig_graph_read')
def _trig_graph_read(fn_word, k, lo, hi):
    f = _TRIG[str(fn_word)]
    k, lo, hi = fr(k), fr(lo), fr(hi)
    sols = [x for x in range(int(lo), int(hi) + 1) if abs(f(math.radians(x)) - float(k)) < 1e-9]
    if len(sols) != 1:
        raise Cannot(f'{fn_word} x = {k} has {len(sols)} whole-degree solutions between {lo} and {hi}')
    return [Fraction(sols[0])]


def _check_trig_curve(fn_word, html):
    svg = one_svg(html)
    series = read_series(svg)
    f = _TRIG[str(fn_word)]
    out = []
    xt = sorted(Fraction(t) for c, _, _, t, _ in classed_texts(svg) if c == 'tx')
    if xt != [0, 90, 180, 270, 360]:
        out.append(f'the x axis is labelled {[str(v) for v in xt]}, not 0 to 360 in steps of 90')
    bad = [(x, y) for x, y in series if abs(f(math.radians(float(x))) - float(y)) > 0.02]
    if bad:
        out.append(f'the curve is not y = {fn_word} x at {len(bad)} of {len(series)} drawn points')
    return out


@diagram('trig_graph_read')
def _check_trig_read(inputs, html):
    return _check_trig_curve(inputs['fn_word'], html)


@solver('trig_solve_k')
def _trig_solve_k(fn_word, k):
    k = float(fr(k))
    fn = str(fn_word)
    if fn == 'sin':
        x1 = math.degrees(math.asin(k))
        x2 = 180 - x1
    elif fn == 'cos':
        x1 = math.degrees(math.acos(k))
        x2 = 360 - x1
    elif fn == 'tan':
        x1 = math.degrees(math.atan(k))
        x2 = x1 + 180
    else:
        raise Cannot(f'unknown function {fn_word!r}')
    return [Approx(min(x1, x2)), Approx(max(x1, x2))]


@solver('trig_graph_feature')
def _trig_graph_feature(fn_word, feature_word):
    fn = str(fn_word)
    text = str(feature_word)
    f = _TRIG[fn]
    m = re.search(r'where x = (\d+)$', text)
    if m:
        x0 = int(m.group(1))
        y0 = Fraction(f(math.radians(x0))).limit_denominator(2)
        if abs(float(y0) - f(math.radians(x0))) > 1e-9:
            raise Cannot(f'{fn} {x0} is not a grid value')
        return [Fraction(x0), y0]
    if 'maximum' in text:
        xs = [x for x in range(0, 361) if abs(f(math.radians(x)) - 1) < 1e-9]
    elif 'minimum' in text:
        xs = [x for x in range(0, 361) if abs(f(math.radians(x)) + 1) < 1e-9]
    else:
        m = re.search(r'between (\d+)° and (\d+)°', text)
        if not m:
            raise Cannot(f'cannot read the feature {feature_word!r}')
        lo, hi = int(m.group(1)), int(m.group(2))
        xs = [x for x in range(lo, hi + 1) if abs(f(math.radians(x))) < 1e-9]
    if len(xs) != 1:
        raise Cannot(f'the feature {feature_word!r} is not a single point: {xs}')
    return [Fraction(xs[0]), Fraction(round(f(math.radians(xs[0]))))]


@diagram('trig_graph_feature')
def _check_trig_feature(inputs, html):
    return _check_trig_curve(inputs['fn_word'], html)


# ───────────────────────── pythagoras ─────────────────────────

def _sqrt(n):
    n = fr(n)
    r = math.isqrt(int(n))
    if r * r != n:
        raise Cannot(f'{n} is not a square number')
    return Fraction(r)


@solver('pyth_rhombus')
def _pyth_rhombus(d1, d2):
    h1, h2 = fr(d1) / 2, fr(d2) / 2
    return [_sqrt(h1 * h1 + h2 * h2)]


@solver('pyth_square_area_diag')
def _pyth_square_area_diag(d):
    return [fr(d) ** 2 / 2]


@solver('pyth_algebraic')
def _pyth_algebraic(a, b):
    """x^2 + (x + a)^2 = (x + b)^2: the positive root."""
    a, b = fr(a), fr(b)
    x = sympy.Symbol('x')
    roots = sympy.solve(x ** 2 + (x + sympy.Rational(a.numerator, a.denominator)) ** 2
                        - (x + sympy.Rational(b.numerator, b.denominator)) ** 2, x)
    pos = [r for r in roots if r.is_rational and r > 0]
    if len(pos) != 1:
        raise Cannot(f'no single positive root: {roots}')
    return [Fraction(str(pos[0]))]
