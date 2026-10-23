"""Readers for the SVG diagrams the generators draw (charts, Venn diagrams, probability trees, pies).

The checks read what is actually on the page: the drawn shapes, the axis tick labels and the printed
numbers, never the numbers the generator started from.  Shape sizes are rounded to whole pixels in the
drawing, so every reading carries a small tolerance (``PX``); the callers decide how much that matters.

Independence rule: this module imports nothing from the generators (checked by the test).
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from .core import Cannot

PX = 1.01        # drawing coordinates are rounded to whole pixels, so shapes can be this far out

_SVG = re.compile(r'<svg\b.*?</svg>', re.S)
_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
_TEXT = re.compile(r'<text\b([^>]*)>(.*?)</text>', re.S)
_TAG = re.compile(r'<[^>]+>')


def svgs(html):
    return _SVG.findall(str(html))


def one_svg(html, index=0):
    found = svgs(html)
    if len(found) <= index:
        raise Cannot('the question has no diagram')
    return found[index]


def attrs(chunk):
    return dict(_ATTR.findall(chunk))


def _f(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def texts(svg):
    """[(x, y, text, anchor)] for every <text> in the drawing (rotated axis titles are left out)."""
    out = []
    for m in _TEXT.finditer(svg):
        a = attrs(m.group(1))
        if 'transform' in a:
            continue
        x, y = _f(a.get('x')), _f(a.get('y'))
        if x is None or y is None:
            continue
        out.append((x, y, _TAG.sub('', m.group(2)).replace('&#8722;', '-').replace('−', '-').strip(),
                    a.get('text-anchor', 'start')))
    return out


def numeric(text):
    try:
        return Fraction(str(text).strip())
    except (ValueError, ZeroDivisionError):
        return None


def elements(svg, tag):
    """[attrs dict] for every <tag .../> or <tag ...>."""
    return [attrs(m.group(1)) for m in re.finditer(rf'<{tag}\b([^>]*?)/?>', svg)]


class Axis:
    """A linear map between pixels and data values, calibrated from labelled ticks."""

    def __init__(self, pairs):
        pairs = sorted(set((float(p), float(v)) for p, v in pairs))
        if len(pairs) < 2 or pairs[0][0] == pairs[-1][0]:
            raise Cannot('axis has fewer than two labelled ticks')
        (p0, v0), (p1, v1) = pairs[0], pairs[-1]
        self.scale = (v1 - v0) / (p1 - p0)       # value per pixel
        self.p0, self.v0 = p0, v0
        for p, v in pairs:
            if abs(self.value(p) - v) > abs(self.scale) * 2.5 + 1e-9:
                raise Cannot('axis ticks are not evenly spaced')

    def value(self, pixel):
        return self.v0 + (pixel - self.p0) * self.scale

    def px_per_unit(self):
        return 1.0 / abs(self.scale)


def y_axis_from_labels(svg, x_label, tol=2):
    """Calibrate a vertical axis from right-aligned tick labels at ``x_label``; the tick sits 4px above the text base."""
    pairs = []
    for x, y, t, anchor in texts(svg):
        v = numeric(t)
        if anchor == 'end' and abs(x - x_label) <= tol and v is not None:
            pairs.append((y - 4, v))
    return Axis(pairs)


def x_axis_from_labels(svg, y_label, tol=3):
    pairs = []
    for x, y, t, anchor in texts(svg):
        v = numeric(t)
        if anchor == 'middle' and abs(y - y_label) <= tol and v is not None:
            pairs.append((x, v))
    return Axis(pairs)


# ─────────────────────────────────────────────────────────────────────────────
# Frequency table
# ─────────────────────────────────────────────────────────────────────────────

def read_freq_table(svg):
    """[(x, f, fx)] rows of the frequency table drawing; the totals row is checked against the data rows."""
    rows = {}
    for x, y, t, _ in texts(svg):
        rows.setdefault(y, {})[round(x)] = t
    ys = sorted(rows)
    if len(ys) < 3:
        raise Cannot('frequency table drawing has no data rows')
    data, total = ys[1:-1], rows[ys[-1]]
    out = []
    for y in data:
        r = rows[y]
        vals = [numeric(r.get(c)) for c in (70, 170, 240)]
        if None in vals:
            raise Cannot('frequency table row is not numeric')
        out.append(tuple(vals))
    fsum, fxsum = numeric(total.get(170)), numeric(total.get(240))
    if fsum != sum(f for _, f, _ in out) or fxsum != sum(fx for _, _, fx in out):
        raise Cannot('frequency table totals do not add up')
    if any(x * f != fx for x, f, fx in out):
        raise Cannot('frequency table fx column is not x times f')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Bar chart
# ─────────────────────────────────────────────────────────────────────────────

def read_bar_chart(svg):
    """[(category, height read from the axis scale, number printed above the bar)]."""
    axis = y_axis_from_labels(svg, 48)
    bars = [a for a in elements(svg, 'rect') if a.get('rx') == '2']
    t = texts(svg)
    out = []
    for b in bars:
        x, y, w, h = (float(b[k]) for k in ('x', 'y', 'width', 'height'))
        height = h * abs(axis.scale)
        cx = x + w / 2
        printed = next((numeric(tt) for tx, ty, tt, _ in t if abs(tx - cx) <= 1 and abs(ty - (y - 5)) <= 2), None)
        cat = next((tt for tx, ty, tt, _ in t if abs(tx - cx) <= 1 and ty > y + h), None)
        out.append((cat, height, printed))
    if not out:
        raise Cannot('no bars found')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Histogram
# ─────────────────────────────────────────────────────────────────────────────

def read_histogram(svg):
    """[(low, high, density)] from bar geometry, the class-boundary labels and the frequency-density scale."""
    yaxis = y_axis_from_labels(svg, 58)
    xaxis = x_axis_from_labels(svg, 276, tol=3)
    bars = [a for a in elements(svg, 'rect') if a.get('opacity') == '0.85']
    if not bars:
        raise Cannot('no histogram bars found')
    out = []
    for b in bars:
        x, y, w, h = (float(b[k]) for k in ('x', 'y', 'width', 'height'))
        out.append((xaxis.value(x), xaxis.value(x + w), h * abs(yaxis.scale)))
    return out


def read_cf_curve(svg):
    """[(upper boundary, cumulative frequency)] including the starting point, read from the drawn curve."""
    m = re.search(r'<path d="(M-?[\d.]+,[^"]*)" fill="none"', svg)
    if not m:
        raise Cannot('no curve found')
    pts = [tuple(float(v) for v in pair.split(',')) for pair in re.findall(r'(-?[\d.]+,-?[\d.]+)', m.group(1))]
    yaxis = y_axis_from_labels(svg, 55)
    xaxis = x_axis_from_labels(svg, 308, tol=3)
    return [(xaxis.value(px), yaxis.value(py)) for px, py in pts]


def read_box_plot(svg):
    """The five labelled numbers and the box edges and median line read from the drawing."""
    t = texts(svg)
    names = {'Min': 'min', 'Q₁': 'q1', 'Median': 'median', 'Q₃': 'q3', 'Max': 'max'}
    labelled = {}
    for x, y, tt, _ in t:
        if tt in names:
            num = next((numeric(t2) for x2, y2, t2, _ in t if abs(x2 - x) <= 1.5 and y2 > y and numeric(t2) is not None), None)
            labelled[names[tt]] = (x, num)
    if len(labelled) != 5 or any(v[1] is None for v in labelled.values()):
        raise Cannot('box plot labels are incomplete')
    axis = Axis([(labelled['min'][0], labelled['min'][1]), (labelled['max'][0], labelled['max'][1])])
    rect = next((a for a in elements(svg, 'rect') if a.get('stroke-width') == '2'), None)
    if rect is None:
        raise Cannot('box plot has no box')
    rx, rw = float(rect['x']), float(rect['width'])
    med = next((a for a in elements(svg, 'line') if a.get('stroke-width') == '2.5' and a.get('x1') == a.get('x2')), None)
    drawn = {'q1': axis.value(rx), 'q3': axis.value(rx + rw), 'median': axis.value(float(med['x1'])) if med else None}
    return {'labelled': {k: v[1] for k, v in labelled.items()}, 'drawn': drawn, 'per_px': abs(axis.scale)}


# ─────────────────────────────────────────────────────────────────────────────
# Pie chart
# ─────────────────────────────────────────────────────────────────────────────

def read_pie_sectors(svg):
    """Sector angles in degrees, read from the drawn wedges (start and end points around the centre)."""
    out = []
    for m in re.finditer(r'<path d="M ([\d.]+) ([\d.]+) L ([\d.]+) ([\d.]+) A ([\d.]+) [\d.]+ 0 ([01]) 1 ([\d.]+) ([\d.]+) Z"', svg):
        cx, cy, x1, y1, _r, large, x2, y2 = (float(g) for g in m.groups())
        a1 = math.atan2(y1 - cy, x1 - cx)
        a2 = math.atan2(y2 - cy, x2 - cx)
        sweep = math.degrees((a2 - a1) % (2 * math.pi))
        if large == 1 and sweep < 180:
            sweep += 180            # numerical wobble at exactly half
        out.append(sweep)
    if not out:
        raise Cannot('no pie sectors found')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Venn diagrams
# ─────────────────────────────────────────────────────────────────────────────

VENN3_POS = {   # the printed count of each region sits at these coordinates
    'a_only': (172, 124), 'b_only': (348, 124), 'c_only': (260, 232), 'ab_only': (260, 104),
    'ac_only': (208, 162), 'bc_only': (312, 162), 'abc': (260, 140), 'neither': (52, 248),
}


def read_venn3(svg):
    """{region: printed integer, or None for an empty '?' cell}."""
    t = texts(svg)
    out = {}
    for key, (x, y) in VENN3_POS.items():
        hit = next((tt for tx, ty, tt, _ in t if abs(tx - x) <= 1 and abs(ty - y) <= 1), None)
        out[key] = None if hit in (None, '?') else numeric(hit)
    return out


def read_venn2(svg):
    t = texts(svg)
    out = {}
    for key, label in (('a_only', 'A only'), ('both', 'A ∩ B'), ('b_only', 'B only')):
        lab = next(((x, y) for x, y, tt, _ in t if tt == label), None)
        if lab is None:
            raise Cannot(f'Venn label {label!r} missing')
        num = next((numeric(tt) for x, y, tt, _ in t if abs(x - lab[0]) <= 1 and 10 <= lab[1] - y <= 20), None)
        out[key] = num
    neither = next((re.search(r'Neither:\s*(\d+)', tt) for _, _, tt, _ in t if tt.startswith('Neither')), None)
    total = next((re.search(r'Total\s*=\s*(\d+)', tt) for _, _, tt, _ in t if tt.startswith('Total')), None)
    out['neither'] = Fraction(neither.group(1)) if neither else None
    out['total'] = Fraction(total.group(1)) if total else None
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Probability tree
# ─────────────────────────────────────────────────────────────────────────────

_FRAC = re.compile(r'^\d+/\d+$')


def read_tree(svg):
    """Branch probabilities of a two-stage tree as Fractions (None when not shown): b1, b2, b11, b12, b21, b22,
    read from the printed labels or, on a fill-in tree, the answers stored on the input boxes; the four
    outcome probabilities; and the colour names of the first and second stage."""
    t = texts(svg)
    pos = {'b1': (132, 99), 'b2': (132, 202), 'b11': (309, 49), 'b12': (309, 103), 'b21': (309, 194), 'b22': (309, 255)}
    out = {}
    inputs = re.findall(r'<foreignObject x="([\d.]+)" y="([\d.]+)"[^>]*>.*?data-ans="([^"]*)"', svg, re.S)
    for key, (x, y) in pos.items():
        val = next((tt for tx, ty, tt, _ in t if abs(tx - x) <= 1 and abs(ty - y) <= 1), None)
        if val is None:
            for ix, iy, ans in inputs:
                if abs(float(ix) - (x - 22)) <= 1 and abs(float(iy) - (y - 11)) <= 1:
                    val = ans
        out[key] = Fraction(val) if val and _FRAC.match(val) else None
    outcomes = []
    for y in (34, 110, 178, 254):
        val = None
        row = next((tt for tx, ty, tt, _ in t if abs(ty - y) <= 1 and tx >= 440), None)
        if row and '=' in row and row.split('=')[-1].strip():
            val = row.split('=')[-1].strip()
        else:
            for ix, iy, ans in inputs:
                if abs(float(iy) - (y - 11)) <= 1 and float(ix) > 500:
                    val = ans
        outcomes.append(Fraction(val) if val and _FRAC.match(val) else None)
    out['outcomes'] = outcomes
    first = next((tt for tx, ty, tt, _ in t if abs(tx - 236) <= 1 and abs(ty - 70) <= 1), None)
    second = next((tt for tx, ty, tt, _ in t if abs(tx - 236) <= 1 and abs(ty - 230) <= 1), None)
    out['colours'] = (first, second)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Scatter graph (the r=5 circles are the points)
# ─────────────────────────────────────────────────────────────────────────────

def read_scatter_points(svg):
    pts = [(float(a['cx']), float(a['cy'])) for a in elements(svg, 'circle') if a.get('r') == '5']
    if len(pts) < 5:
        raise Cannot('fewer than five scatter points found')
    return pts


def pearson(points):
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points)
    syy = sum((p[1] - my) ** 2 for p in points)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points)
    if sxx == 0 or syy == 0:
        raise Cannot('scatter points have no spread')
    return sxy / math.sqrt(sxx * syy)


def read_centre_angle(svg):
    """Angle in degrees between the two radii drawn from the centre of the circle (CT1 diagram)."""
    circles = [c for c in elements(svg, 'circle') if _f(c.get('r'), 0) > 20]
    if len(circles) != 1:
        raise Cannot('expected one large circle')
    cx, cy = _f(circles[0].get('cx')), _f(circles[0].get('cy'))
    rays = []
    for ln in elements(svg, 'line'):
        x1, y1, x2, y2 = (_f(ln.get(k)) for k in ('x1', 'y1', 'x2', 'y2'))
        if None in (x1, y1, x2, y2):
            continue
        if abs(x1 - cx) < 0.05 and abs(y1 - cy) < 0.05:
            rays.append((x2 - cx, y2 - cy))
    if len(rays) != 2:
        raise Cannot(f'expected two radii from the centre, found {len(rays)}')
    (ax, ay), (bx, by) = rays
    cos = (ax * bx + ay * by) / (math.hypot(ax, ay) * math.hypot(bx, by))
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))
