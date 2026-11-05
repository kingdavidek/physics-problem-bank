"""
GCSE Maths – Graphical Simultaneous Equations
5 foundational · 6 intermediate · 4 difficult · 8 MCQ (randomised, with SVG)
Graded practice variants return (question, solution, hint, marks, raw)
or an MCQ 6-tuple (question, solution, hint, marks, options, correct_letter).
"""
from generators.shared.rounding import round_half_up as round
import math
import random
from generators.shared.answer_checkers import linear_format_hint
from generators.shared.utils import make_problem
from generators.shared.verify_hook import record, verifies
from models import svg_kit
from generators.gcse.maths_variety_b import _lin, _quad
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_pool,
    run_mcq_variant,
    pick_named_variant,
)

# Standard footprint — sized for legibility (~360px wide).
_GSIM_W, _GSIM_H = 280, 200
_GSIM_PAD = 24
_GSIM_MAX_W = 360


def _gsim_display_h():
    vb_h = _GSIM_H + 2 * _GSIM_PAD
    vb_w = _GSIM_W + 2 * _GSIM_PAD
    return round(_GSIM_MAX_W * vb_h / vb_w)


def _fmt_b(b):
    if b > 0:
        return f"+ {b}"
    if b < 0:
        return f"- {abs(b)}"
    return ""


def _fmt_line_eq(m, c):
    if m == 1:
        body = "x"
    elif m == -1:
        body = "-x"
    else:
        body = f"{m}x"
    return rf"\(y = {body} {_fmt_b(c)}\)".strip()


def _gsim_raw(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:g}"
    return str(value)


def _gsim_pair_answer(x, y, label_a='x', label_b='y', sep=','):
    return {
        'type': 'number_pair',
        'values': (_gsim_raw(x), _gsim_raw(y)),
        'label_a': label_a,
        'label_b': label_b,
        'sep': sep,
    }


def _gsim_linear_answer(value, var='y'):
    return {'type': 'linear', 'value': _gsim_raw(value), 'var': str(var).strip().lower()}


def _gsim_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_gsim_raw(v) for v in values),
        'labels': tuple(labels),
    }


def _gsim_linear_raw(raw):
    var = raw.get('var') or 'x'
    val = raw.get('value')
    if var == 'x':
        return str(val)
    return f'{var}={val}'


def _gsim_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 6 and isinstance(out[4], (list, tuple)):
        # Letter order may match labels drawn on the diagram — do not reshuffle.
        extra = {
            'options': list(out[4]),
            'correct_answer': out[5],
            'choice_no_shuffle': True,
        }
    elif len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'number_pair':
                val_a, val_b = raw['values']
                extra = {
                    'correct_answer_raw': f'{val_a}|{val_b}',
                    'answer_type': 'number_pair',
                    'answer_labels': [raw['label_a'], raw['label_b']],
                    'answer_pair_sep': raw.get('sep', 'and'),
                }
            elif raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if values and len(values) == len(labels):
                    extra = {
                        'correct_answer_raw': '|'.join(str(v) for v in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_format_hint': (
                            'Enter a number in every field, with the smaller x first'
                            if len(values) == 4 else 'Enter a number in every field'
                        ),
                    }
            elif raw_type == 'linear':
                extra = {
                    'correct_answer_raw': _gsim_linear_raw(raw),
                    'answer_type': 'linear',
                    'answer_format_hint': linear_format_hint(_gsim_linear_raw(raw)),
                }
            elif raw_type == 'quadratic_roots':
                from generators.gcse.maths_variety_b import problem_extra
                extra = problem_extra(raw)
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _gsim_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
        elif isinstance(raw, str):
            extra = {
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks,
        'gcse', 'maths', 'graphical_simultaneous_equations', **extra
    )


def _parabola_line_roots(r1=None, r2=None):
    if r1 is None or r2 is None:
        r1 = random.randint(-3, -1)
        r2 = random.randint(2, 6)
        while r1 == r2 or r1 + r2 == 0:
            r2 = random.randint(2, 6)
    a = r1 + r2
    b = -r1 * r2
    return r1, r2, a, b


def _bounds(points, margin=1):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin)


def _xy(bounds, x, y):
    x0, x1, y0, y1 = bounds
    sx = _GSIM_PAD + (x - x0) / (x1 - x0) * (_GSIM_W - 2 * _GSIM_PAD)
    sy = _GSIM_H - _GSIM_PAD - (y - y0) / (y1 - y0) * (_GSIM_H - 2 * _GSIM_PAD)
    return round(sx, 1), round(sy, 1)


def _svg_wrap(inner):
    p = _GSIM_PAD
    vb_w = _GSIM_W + 2 * p
    vb_h = _GSIM_H + 2 * p
    return str(svg_kit.viewbox_svg(
        -p, -p, vb_w, vb_h,
        title='Graphical simultaneous equations',
        desc='Coordinate graph of the equations in this question.',
        body=inner,
        max_width=_GSIM_MAX_W,
        variant='chart',
    ))


def _svg_minor_grid(bounds, x_step, y_step):
    """Faint lines at every whole number between the labelled ones, so a value such as 21 on a scale labelled in fives
    or 5 on one labelled in twos can be read exactly (batch B review, 2026-10-28: the reading slots asked for values
    that lay on no grid line in 40% to 80% of draws). Skipped on an axis spanning more than 60 units."""
    x0, x1, y0, y1 = bounds
    parts = []
    if x_step > 1 and x1 - x0 <= 60:
        major = set(_axis_ticks(x0, x1, x_step))
        for xi in _axis_ticks(x0, x1, 1):
            if xi not in major:
                sx1, sy1 = _xy(bounds, xi, y0)
                sx2, sy2 = _xy(bounds, xi, y1)
                parts.append(f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="#f1f5f8" stroke-width="0.8"/>')
    if y_step > 1 and y1 - y0 <= 60:
        major = set(_axis_ticks(y0, y1, y_step))
        for yi in _axis_ticks(y0, y1, 1):
            if yi not in major:
                sx1, sy1 = _xy(bounds, x0, yi)
                sx2, sy2 = _xy(bounds, x1, yi)
                parts.append(f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="#f1f5f8" stroke-width="0.8"/>')
    return parts


def _svg_grid(bounds, minor=False):
    x0, x1, y0, y1 = bounds
    x_step = _axis_stride(x0, x1)
    y_step = _axis_stride(y0, y1)
    parts = _svg_minor_grid(bounds, x_step, y_step) if minor else []
    for xi in _axis_ticks(x0, x1, x_step):
        sx1, sy1 = _xy(bounds, xi, y0)
        sx2, sy2 = _xy(bounds, xi, y1)
        parts.append(
            f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="#e8eef2" stroke-width="1"/>'
        )
    for yi in _axis_ticks(y0, y1, y_step):
        sx1, sy1 = _xy(bounds, x0, yi)
        sx2, sy2 = _xy(bounds, x1, yi)
        parts.append(
            f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="#e8eef2" stroke-width="1"/>'
        )
    ax_x0, ax_y0 = _xy(bounds, 0, y0)
    ax_x1, ax_y1 = _xy(bounds, 0, y1)
    ax_x2, ax_y2 = _xy(bounds, x0, 0)
    ax_x3, ax_y3 = _xy(bounds, x1, 0)
    if x0 <= 0 <= x1:
        parts.append(
            f'<line x1="{ax_x0}" y1="{ax_y0}" x2="{ax_x1}" y2="{ax_y1}" stroke="#94a3b8" stroke-width="1.2"/>'
        )
    if y0 <= 0 <= y1:
        parts.append(
            f'<line x1="{ax_x2}" y1="{ax_y2}" x2="{ax_x3}" y2="{ax_y3}" stroke="#94a3b8" stroke-width="1.2"/>'
        )
    return "".join(parts)


def _svg_polyline(bounds, pts, color, width=2.5, dash=None):
    coords = " ".join(f'{_xy(bounds, x, y)[0]},{_xy(bounds, x, y)[1]}' for x, y in pts)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<polyline points="{coords}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round"{dash_attr}/>'
    )


def _svg_point(bounds, x, y, label=None, r=5):
    sx, sy = _xy(bounds, x, y)
    dot = (
        f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="#8a5300" stroke="#fff" stroke-width="1.5"/>'
    )
    if label:
        lx, ly = sx + 8, sy - 8
        dot += f'<text x="{lx}" y="{ly}" font-size="11" fill="#8a5300" font-weight="bold">{label}</text>'
    return dot


def _axis_stride(lo, hi, target=8):
    """Pick a 'nice' label step (1, 2, 5, 10, ...) so ticks stay legible."""
    span = max(1, int(hi) - int(lo))
    raw = span / target
    if raw <= 1:
        return 1
    for step in (1, 2, 5, 10, 20, 25, 50, 100):
        if step >= raw:
            return step
    return 100


def _axis_ticks(lo, hi, step):
    """Tick values anchored to multiples of step so grid lines and number labels coincide."""
    start = math.ceil(lo / step) * step
    ticks = []
    v = start
    while v <= hi + 1e-9:
        ticks.append(int(round(v)))
        v += step
    return ticks


def _svg_axis_numbers(bounds):
    """Integer tick labels so students can read coordinates (never the answer pair)."""
    x0, x1, y0, y1 = bounds
    parts = []
    x_step = _axis_stride(x0, x1)
    y_step = _axis_stride(y0, y1)
    for xi in _axis_ticks(x0, x1, x_step):
        sx, sy = _xy(bounds, xi, y0)
        parts.append(
            f'<text x="{sx}" y="{sy + 14}" font-size="10" fill="#64748b" text-anchor="middle">{xi}</text>'
        )
    for yi in _axis_ticks(y0, y1, y_step):
        if yi == 0:
            continue
        sx, sy = _xy(bounds, x0, yi)
        parts.append(
            f'<text x="{sx - 6}" y="{sy + 4}" font-size="10" fill="#64748b" text-anchor="end">{yi}</text>'
        )
    return "".join(parts)


def _line_pts(m, c, x0, x1, n=24):
    step = (x1 - x0) / (n - 1)
    return [(x0 + i * step, m * (x0 + i * step) + c) for i in range(n)]


def _parabola_pts(x0, x1, n=30):
    step = (x1 - x0) / (n - 1)
    return [(x0 + i * step, (x0 + i * step) ** 2) for i in range(n)]


def _line_graph_bounds(m1, c1, m2, c2, ix, iy, *, x_min=None, y_min=None, x_pad=3):
    """Axis limits that include the intersection, both intercepts, and a margin beyond ix."""
    x_lo = 0 if x_min == 0 else ix - x_pad
    x_hi = ix + x_pad
    pts = [
        (ix, iy),
        (x_lo, m1 * x_lo + c1),
        (x_hi, m1 * x_hi + c1),
        (x_lo, m2 * x_lo + c2),
        (x_hi, m2 * x_hi + c2),
    ]
    if x_min is not None and x_min < x_lo:
        pts.extend([(x_min, m1 * x_min + c1), (x_min, m2 * x_min + c2)])
    if y_min is not None or x_min == 0:
        pts.extend([(0, c1), (0, c2)])
        if y_min is not None:
            pts.append((0, y_min))
    bounds = _bounds(pts, 1)
    if x_min is not None:
        bounds = (x_min, bounds[1], bounds[2], bounds[3])
    if y_min is not None:
        bounds = (bounds[0], bounds[1], y_min, bounds[3])
    return bounds


def _svg_two_lines(
    m1, c1, m2, c2, ix, iy,
    show_point=True,
    point_label=None,
    line_labels=True,
    axis_numbers=False,
    extra_points=None,
    x_min=None,
    y_min=None,
    line_label_1=None,
    line_label_2=None,
    minor_grid=False,
):
    """
    minor_grid: faint lines at every whole number between the labelled ones (the batch B reading slots; batch C2
    turned it on for the older reading slots too, docs/GCSE_MATHS_VARIETY.md section 23).
    extra_points: list of (x, y, label) e.g. [('A', 3, 5)] — label is a single letter, not coordinates.
    Never pass coordinate strings as labels on exam-style read/graph questions.
    x_min / y_min: pin axis limits (e.g. 0 for cost graphs so intercepts stay visible).
    """
    # What is drawn, for the verification test: the two lines, the marked point and any plotted letters.
    record('gsim_drawn', kind='lines', m1=m1, c1=c1, m2=m2, c2=c2,
           point=(ix, iy) if show_point else None,
           extra=[tuple(item) for item in (extra_points or [])])
    if x_min is not None or y_min is not None:
        bounds = _line_graph_bounds(m1, c1, m2, c2, ix, iy, x_min=x_min, y_min=y_min)
    else:
        x0, x1 = ix - 3, ix + 3
        pts = [
            (ix, iy),
            (x0, m1 * x0 + c1),
            (x1, m1 * x1 + c1),
            (x0, m2 * x0 + c2),
            (x1, m2 * x1 + c2),
        ]
        if extra_points:
            for item in extra_points:
                pts.append((item[1], item[2]))
        bounds = _bounds(pts, 1)
    svg = _svg_grid(bounds, minor=minor_grid)
    if axis_numbers:
        svg += _svg_axis_numbers(bounds)
    svg += _svg_polyline(bounds, _line_pts(m1, c1, bounds[0], bounds[1]), "#1a6fa8")
    svg += _svg_polyline(bounds, _line_pts(m2, c2, bounds[0], bounds[1]), "#c0392b")
    if show_point:
        svg += _svg_point(bounds, ix, iy, point_label)
    if extra_points:
        for letter, px, py in extra_points:
            svg += _svg_point(bounds, px, py, letter, r=4)
    if line_labels:
        lbl1 = line_label_1 or "L₁"
        lbl2 = line_label_2 or "L₂"
        if x_min == 0 and y_min == 0:
            lx1, ly1 = _xy(bounds, 0.15, c1)
            svg += (
                f'<text x="{lx1 + 4}" y="{ly1 + (4 if c1 <= c2 else -6)}" '
                f'font-size="10" fill="#1a6fa8">{lbl1}</text>'
            )
            lx2, ly2 = _xy(bounds, 0.15, c2)
            svg += (
                f'<text x="{lx2 + 4}" y="{ly2 + (-6 if c1 <= c2 else 4)}" '
                f'font-size="10" fill="#c0392b">{lbl2}</text>'
            )
        else:
            lx, ly = _xy(bounds, bounds[0] + 0.3, m1 * (bounds[0] + 0.3) + c1)
            svg += f'<text x="{lx}" y="{ly - 6}" font-size="11" fill="#1a6fa8">{lbl1}</text>'
            lx2, ly2 = _xy(bounds, bounds[1] - 0.5, m2 * (bounds[1] - 0.5) + c2)
            svg += f'<text x="{lx2}" y="{ly2 + 14}" font-size="11" fill="#c0392b">{lbl2}</text>'
    return _svg_wrap(svg)


def _svg_parallel_lines(m, c1, c2, axis_numbers=False):
    record('gsim_drawn', kind='lines', m1=m, c1=c1, m2=m, c2=c2, point=None, extra=[])
    x0, x1 = 0, 6
    pts = [(x0, m * x0 + c1), (x1, m * x1 + c1), (x0, m * x0 + c2), (x1, m * x1 + c2)]
    bounds = _bounds(pts, 1)
    svg = _svg_grid(bounds)
    if axis_numbers:
        svg += _svg_axis_numbers(bounds)
    svg += _svg_polyline(bounds, _line_pts(m, c1, bounds[0], bounds[1]), "#1a6fa8")
    svg += _svg_polyline(bounds, _line_pts(m, c2, bounds[0], bounds[1]), "#c0392b", dash="6 4")
    return _svg_wrap(svg)


def _svg_parabola_line(r1, r2, a, b, mark="none", axis_numbers=False, minor_grid=False):
    """
    mark: 'none' | 'one' | 'both' — dots only, never coordinate labels on the diagram.
    """
    y1, y2 = r1 * r1, r2 * r2
    record('gsim_drawn', kind='parabola', a=a, b=b,
           marks=[(r1, y1)] if mark == 'one' else ([(r1, y1), (r2, y2)] if mark == 'both' else []))
    x0, x1 = min(r1, r2) - 1, max(r1, r2) + 1
    pts = _parabola_pts(x0, x1) + _line_pts(a, b, x0, x1)
    if mark in ("one", "both"):
        pts += [(r1, y1)]
    if mark == "both":
        pts.append((r2, y2))
    bounds = _bounds(pts, 1)
    svg = _svg_grid(bounds, minor=minor_grid)
    if axis_numbers:
        svg += _svg_axis_numbers(bounds)
    svg += _svg_polyline(bounds, _parabola_pts(bounds[0], bounds[1]), "#059669", width=2.8)
    svg += _svg_polyline(bounds, _line_pts(a, b, bounds[0], bounds[1]), "#1a6fa8")
    if mark in ("one", "both"):
        svg += _svg_point(bounds, r1, y1)
    if mark == "both":
        svg += _svg_point(bounds, r2, y2)
    return _svg_wrap(svg)


def _parse_coord_pair(text):
    inner = text.strip().strip("()")
    a, b = inner.split(",")
    return int(a.strip()), int(b.strip())


def _lines_at_point(ix, iy):
    m1 = random.randint(1, 3)
    m2 = random.randint(1, 3)
    while m2 == m1:
        m2 = random.randint(1, 3)
    c1 = iy - m1 * ix
    c2 = iy - m2 * ix
    return m1, c1, m2, c2


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='gsim_point')
def _gsim_f_read_intersection():
    ix = random.randint(1, 5)
    iy = random.randint(2, 8)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True, minor_grid=True,
    )
    q = (
        rf"The graphs of two linear equations are shown. "
        rf"The lines intersect at point <strong>P</strong>.<br>{svg}<br>"
        rf"What are the coordinates of <strong>P</strong>?"
    )
    s = rf"Read from the axes: <strong>\(({ix}, {iy})\)</strong>."
    return q, s, "Read x across, then y up from the numbered axes.", 2, _gsim_pair_answer(ix, iy)


@verifies('alg', task='keyed_text', text='the solution to both equations (the simultaneous solution)', drawn='cross')
def _gsim_f_meaning_of_crossing():
    ix, iy = 4, 7
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", line_labels=False,
    )
    q = (
        rf"Two straight lines are drawn on the same axes and cross once.<br>{svg}<br>"
        r"What does the crossing point represent?"
    )
    correct = "The solution to both equations (the simultaneous solution)"
    distractors = [
        "The midpoint of the two lines",
        "Where the gradients are equal",
        "The average of the two y-intercepts",
    ]
    texts = [correct] + distractors
    random.shuffle(texts)
    letters = "ABCD"
    correct_letter = letters[texts.index(correct)]
    opts = [f"{letters[i]}  {texts[i]}" for i in range(4)]
    s = (
        r"The <strong>(x, y)</strong> pair that satisfies <strong>both</strong> equations — "
        r"the solution to the simultaneous equations.<br>"
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, s, "One point on both lines = one simultaneous solution.", 1, opts, correct_letter


@verifies('alg', task='gsim_which_point')
def _gsim_f_which_point_on_both():
    ix = random.randint(2, 5)
    iy = random.randint(3, 7)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    wrong = [
        (ix + 1, iy),
        (ix, iy + 2),
        (ix - 1, iy - 1),
    ]
    correct = f"({ix}, {iy})"
    coords = [f"({w[0]}, {w[1]})" for w in wrong] + [correct]
    random.shuffle(coords)
    letters = "ABCD"
    correct_letter = letters[coords.index(correct)]
    plotted = [(letter, *_parse_coord_pair(opt)) for letter, opt in zip(letters, coords)]
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy,
        show_point=False, axis_numbers=True, extra_points=plotted, minor_grid=True,
    )
    q = rf"Which labelled point lies on <strong>both</strong> lines?<br>{svg}"
    opts = [f"{letters[i]}  {coords[i]}" for i in range(4)]
    s = (
        rf"Only <strong>{correct_letter}) {correct}</strong> sits on both lines.<br>"
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, s, "The point on both lines is at the intersection.", 2, opts, correct_letter


@verifies('alg', task='gsim_y_at_x')
def _gsim_f_read_y_at_crossing():
    ix = random.randint(2, 6)
    iy = random.randint(4, 10)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True, minor_grid=True,
    )
    q = (
        rf"The lines intersect at \(x = {ix}\) on the graph below.<br>{svg}<br>"
        rf"What is the value of <strong>\(y\)</strong> at the intersection?"
    )
    s = rf"At \(x = {ix}\), the lines meet at <strong>\(y = {iy}\)</strong>."
    return q, s, "The y-coordinate at the crossing is part of the solution pair.", 2, _gsim_linear_answer(iy, "y")


@verifies('alg', task='gsim_count')
def _gsim_f_how_many_solutions_lines():
    parallel = random.choice([True, False])
    if parallel:
        m = random.randint(1, 2)
        c1, c2 = random.randint(1, 4), random.randint(6, 9)
        svg = _svg_parallel_lines(m, c1, c2)
        n, word = 0, "no"
    else:
        ix, iy = random.randint(2, 5), random.randint(3, 7)
        m1, c1, m2, c2 = _lines_at_point(ix, iy)
        svg = _svg_two_lines(m1, c1, m2, c2, ix, iy, show_point=False)
        n, word = 1, "one"
    q = (
        rf"How many simultaneous solutions do these two lines have?<br>{svg}"
    )
    s = rf"Distinct crossing → <strong>{word}</strong> solution ({n})."
    return q, s, "Parallel distinct lines never meet → 0 solutions.", 2, n


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='gsim_equations_from_graph')
def _gsim_i_equations_from_graph():
    ix, iy = random.randint(2, 5), random.randint(4, 9)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True, minor_grid=True,
    )
    q = (
        rf"The solution to a pair of simultaneous equations is shown on the graph "
        rf"(point <strong>P</strong>).<br>{svg}<br>"
        rf"Which pair of equations could produce this graph?"
    )
    correct = f"{_fmt_line_eq(m1, c1)} and {_fmt_line_eq(m2, c2)}"
    wrong = [
        f"{_fmt_line_eq(m1, c1 + 2)} and {_fmt_line_eq(m2, c2)}",
        f"{_fmt_line_eq(m2, c1)} and {_fmt_line_eq(m1, c2)}",
        f"{_fmt_line_eq(-m1, c1)} and {_fmt_line_eq(m2, c2)}",
    ]
    texts = wrong + [correct]
    random.shuffle(texts)
    letters = "ABCD"
    correct_letter = letters[texts.index(correct)]
    opts = [f"{letters[i]}  {texts[i]}" for i in range(4)]
    s = (
        rf"Lines match slopes and intercepts at the crossing → "
        rf"<strong>{correct_letter}</strong>. Answer: <strong>{correct_letter}</strong>"
    )
    return q, s, "Compare gradients and where each line crosses the y-axis.", 3, opts, correct_letter


@verifies('alg', task='gsim_point', which='marked')
def _gsim_i_parabola_read_one_point():
    r1, r2, a, b = _parabola_line_roots()
    # Prefer marking the left root so the diagram stays readable.
    if r1 > r2:
        r1, r2 = r2, r1
    y1 = r1 * r1
    svg = _svg_parabola_line(r1, r2, a, b, mark="one", axis_numbers=True, minor_grid=True)
    q = (
        rf"The graphs of \(y = x^2\) and {_fmt_line_eq(a, b)} are shown. "
        rf"One intersection is marked with a dot.<br>{svg}<br>"
        rf"Write this solution as coordinates <strong>(x, y)</strong>."
    )
    s = rf"Read from the axes: <strong>\(({r1}, {y1})\)</strong>."
    return q, s, "Each crossing of curve and line is one solution pair.", 3, _gsim_pair_answer(r1, y1)


@verifies('alg', task='gsim_count')
def _gsim_i_parabola_count_intersections():
    r1, r2, a, b = _parabola_line_roots()
    svg = _svg_parabola_line(r1, r2, a, b, mark="none")
    q = (
        rf"How many solutions do \(y = x^2\) and {_fmt_line_eq(a, b)} have, "
        rf"according to the graph?<br>{svg}"
    )
    s = r"Two distinct crossings → <strong>2 solutions</strong>."
    return q, s, "Count intersection points on the diagram.", 2, 2


@verifies('alg', task='keyed_text', text='there are no solutions (the lines are parallel)', drawn='parallel')
def _gsim_i_no_solution_parallel():
    m = random.randint(1, 3)
    c1, c2 = random.randint(0, 3), random.randint(5, 9)
    svg = _svg_parallel_lines(m, c1, c2)
    q = (
        rf"Two lines are graphed below.<br>{svg}<br>"
        r"What can you say about solving them <strong>simultaneously</strong>?"
    )
    correct = "There are no solutions (the lines are parallel)"
    distractors = [
        "There is exactly one solution",
        "There are two solutions",
        "There are infinitely many solutions",
    ]
    texts = [correct] + distractors
    random.shuffle(texts)
    letters = "ABCD"
    correct_letter = letters[texts.index(correct)]
    opts = [f"{letters[i]}  {texts[i]}" for i in range(4)]
    s = (
        r"Lines are <strong>parallel</strong> (same gradient, different intercepts) → "
        r"<strong>no solutions</strong>.<br>"
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, s, "No intersection means no (x, y) works in both equations.", 2, opts, correct_letter


@verifies('alg', task='gsim_point')
def _gsim_i_negative_gradient():
    """One positive and one negative gradient meeting at an integer point."""
    ix = random.randint(2, 5)
    iy = random.randint(2, 8)
    m_neg = -random.randint(1, 3)
    m_pos = random.randint(1, 3)
    c1 = iy - m_neg * ix
    c2 = iy - m_pos * ix
    svg = _svg_two_lines(
        m_neg, c1, m_pos, c2, ix, iy, point_label="P", axis_numbers=True, minor_grid=True,
    )
    q = (
        rf"Use the graph to find the simultaneous solution (point <strong>P</strong>).<br>{svg}"
    )
    s = rf"<strong>\(x = {ix},\; y = {iy}\)</strong> at the intersection."
    return q, s, "Read x and y from the numbered axes at P.", 2, _gsim_pair_answer(ix, iy)


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='gsim_both_points')
def _gsim_d_both_parabola_points():
    r1, r2, a, b = _parabola_line_roots()
    y1, y2 = r1 * r1, r2 * r2
    svg = _svg_parabola_line(r1, r2, a, b, mark="none", axis_numbers=True, minor_grid=True)
    q = (
        rf"Solve graphically: \(y = x^2\) and {_fmt_line_eq(a, b)}.<br>{svg}<br>"
        rf"State <strong>both</strong> coordinate pairs."
    )
    s = rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>."
    return q, s, "Both crossings are solutions — list them clearly.", 4, _gsim_fields_answer([r1, y1, r2, y2], ["x (1st)", "y (1st)", "x (2nd)", "y (2nd)"])


@verifies('alg', task='gsim_count')
def _gsim_d_tangent_one_solution():
    """Line tangent to y=x² at x=k → one repeated root."""
    k = random.randint(2, 5)
    a = 2 * k
    b = -k * k
    svg = _svg_parabola_line(k, k, a, b, mark="one", axis_numbers=True)
    q = (
        rf"The line touches the parabola \(y = x^2\) at exactly one point (tangent).<br>{svg}<br>"
        r"How many simultaneous solutions are there?"
    )
    s = r"One touching point → <strong>1 solution</strong> (repeated root algebraically)."
    return q, s, "Touching = one solution; crossing twice = two.", 3, 1


@verifies('alg', task='gsim_count')
def _gsim_d_line_misses_parabola():
    """y = x² and a line with no real intersections."""
    # Line y = mx + c below the parabola for integer m, so discriminant < 0.
    m = random.randint(1, 3)
    c = -random.randint(4, 8)
    # x² - mx - c = 0 → disc = m² + 4c; with c <= -4 and m <= 3, disc < 0.
    record('gsim_drawn', kind='parabola', a=m, b=c, marks=[])
    pts = _parabola_pts(-2, 4) + _line_pts(m, c, -2, 4)
    bounds = _bounds(pts, 1)
    svg = _svg_grid(bounds)
    svg += _svg_polyline(bounds, _parabola_pts(bounds[0], bounds[1]), "#059669", width=2.8)
    svg += _svg_polyline(bounds, _line_pts(m, c, bounds[0], bounds[1]), "#1a6fa8")
    svg = _svg_wrap(svg)
    q = (
        rf"The graphs of \(y = x^2\) and {_fmt_line_eq(m, c)} are sketched on the same axes.<br>{svg}<br>"
        r"How many real simultaneous solutions are there?"
    )
    s = (
        rf"Set \(x^2\) equal to the line {_fmt_line_eq(m, c)}; rearranging gives a quadratic "
        r"with negative discriminant → <strong>0 real solutions</strong> (curves do not cross)."
    )
    return q, s, "No intersection on the graph means no real simultaneous solutions.", 3, 0


@verifies('alg', task='gsim_context')
def _gsim_d_context_graph():
    """Real-world cost comparison: two companies, break-even number of items."""
    ix = random.randint(3, 6)
    # One firm: lower joining fee, higher per-unit rate.
    # Other: higher joining fee, cheaper per unit — they break even at P.
    rate_steep = random.randint(3, 5)
    rate_gentle = random.randint(2, rate_steep - 1)
    fee_steep = random.randint(0, 2)
    iy = rate_steep * ix + fee_steep
    fee_gentle = iy - rate_gentle * ix  # positive because rate_gentle < rate_steep
    m1, c1 = rate_steep, fee_steep
    m2, c2 = rate_gentle, fee_gentle

    def _fee_phrase(amount, kind):
        if amount == 0:
            return f"no {kind}"
        return f"a £{amount} {kind}"

    scenarios = [
        {
            "line_a": "QuickCopy",
            "line_b": "PrintPro",
            "intro": (
                rf"A school is comparing two photocopying firms.<br>"
                rf"<strong>QuickCopy</strong> charges {_fee_phrase(fee_steep, 'setup fee')} plus £{rate_steep} per booklet.<br>"
                rf"<strong>PrintPro</strong> charges {_fee_phrase(fee_gentle, 'setup fee')} plus £{rate_gentle} per booklet.<br>"
                rf"The graphs show total cost \(y\) (in pounds) against number of booklets \(x\)."
            ),
            "unit": "booklets",
        },
        {
            "line_a": "NetFast",
            "line_b": "WebWise",
            "intro": (
                rf"Two broadband companies advertise these plans:<br>"
                rf"<strong>NetFast</strong>: {_fee_phrase(fee_steep, 'joining fee')}, then £{rate_steep} per GB of data.<br>"
                rf"<strong>WebWise</strong>: {_fee_phrase(fee_gentle, 'joining fee')}, then £{rate_gentle} per GB of data.<br>"
                rf"The graphs show total cost \(y\) (in pounds) against data used \(x\) (in GB)."
            ),
            "unit": "GB",
        },
        {
            "line_a": "SnackHire",
            "line_b": "PopCo",
            "intro": (
                rf"A cinema hires popcorn machines from two suppliers.<br>"
                rf"<strong>SnackHire</strong>: {_fee_phrase(fee_steep, 'delivery fee')} plus £{rate_steep} per bag of popcorn sold.<br>"
                rf"<strong>PopCo</strong>: {_fee_phrase(fee_gentle, 'delivery fee')} plus £{rate_gentle} per bag sold.<br>"
                rf"The graphs show total cost \(y\) (in pounds) against bags sold \(x\)."
            ),
            "unit": "bags",
        },
    ]
    scene = random.choice(scenarios)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy,
        point_label="P",
        axis_numbers=True,
        x_min=0,
        y_min=0,
        line_label_1=scene["line_a"],
        line_label_2=scene["line_b"],
        minor_grid=True,
    )
    q = (
        rf"{scene['intro']}<br>{svg}<br>"
        rf"The lines cross at point <strong>P</strong>. "
        rf"At how many {scene['unit']} \(x\) do the <strong>two costs match</strong>?"
    )
    s = (
        rf"The costs are equal only at the intersection P.<br>"
        rf"Read the \(x\)-coordinate of P: <strong>\(x = {ix}\)</strong> {scene['unit']}."
    )
    hint = (
        "Find where the two cost lines cross — that x-value is where both companies charge the same."
    )
    return q, s, hint, 3, ix


@verifies('alg', task='gsim_x_marked')
def _gsim_i_verify_algebra_from_graph():
    r1, r2, a, b = _parabola_line_roots()
    if r1 > r2:
        r1, r2 = r2, r1
    y1 = r1 * r1
    svg = _svg_parabola_line(r1, r2, a, b, mark="one", axis_numbers=True, minor_grid=True)
    q = (
        rf"The graph shows one intersection of \(y = x^2\) and {_fmt_line_eq(a, b)}.<br>{svg}<br>"
        rf"Algebra gives \(x = {r1}\) or \(x = {r2}\). Which \(x\)-value matches the <strong>marked</strong> point?"
    )
    s = rf"The marked point has <strong>\(x = {r1}\)</strong> (and \(y = {y1}\))."
    return q, s, "Graph and algebra must agree on the same solution pairs.", 3, _gsim_linear_answer(r1, "x")


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (8 — randomised, often with SVG)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='gsim_point')
def _gsim_mcq_read_coords():
    ix = random.randint(1, 5)
    iy = random.randint(2, 8)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True, minor_grid=True,
    )
    correct = f"({ix}, {iy})"
    wrong = [f"({ix+1}, {iy})", f"({ix}, {iy+2})", f"({ix-1}, {iy-1})"]
    pairs = wrong + [correct]
    random.shuffle(pairs)
    letters = "ABCD"
    correct_letter = letters[pairs.index(correct)]
    opts = [f"{letters[i]}  {pairs[i]}" for i in range(4)]
    q = rf"From the graph, the simultaneous solution is:<br>{svg}"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Read the intersection coordinates.", 2, opts, correct_letter


@verifies('alg', task='gsim_count')
def _gsim_mcq_parallel_count():
    parallel = random.choice([True, False])
    if parallel:
        m = random.randint(1, 2)
        svg = _svg_parallel_lines(m, 2, 7)
        correct, n = "0", "0"
    else:
        ix, iy = 3, 6
        m1, c1, m2, c2 = _lines_at_point(ix, iy)
        svg = _svg_two_lines(m1, c1, m2, c2, ix, iy, show_point=False)
        correct, n = "1", "1"
    vals = ["0", "1", "2", "3"]
    wrong = [v for v in vals if v != correct][:3]
    opts_vals = wrong + [correct]
    random.shuffle(opts_vals)
    letters = "ABCD"
    correct_letter = letters[opts_vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(opts_vals)]
    q = rf"How many solutions do these simultaneous equations have?<br>{svg}"
    sol = f"<strong>{n}</strong> solution(s). Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Count intersections on the graph.", 2, opts, correct_letter


@verifies('alg', task='gsim_count')
def _gsim_mcq_parabola_intersections():
    r1, r2, a, b = _parabola_line_roots()
    svg = _svg_parabola_line(r1, r2, a, b, mark="none")
    correct = "2"
    wrong = [v for v in ["0", "1", "3"] if v != correct]
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = rf"How many solutions are shown?<br>{svg}"
    sol = f"Two crossings → <strong>2</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Count where the line meets the parabola.", 2, opts, correct_letter


@verifies('alg', task='gsim_point', which='marked')
def _gsim_mcq_parabola_point():
    r1, r2, a, b = _parabola_line_roots()
    y1 = r1 * r1
    correct = f"({r1}, {y1})"
    candidates = [
        f"({r2}, {y1})",
        f"({r1}, {r2})",
        f"({r1 + r2}, {(r1 + r2) ** 2})",
        f"({r1}, {y1 + 1})",
        f"({r2}, {r2 * r2 + 1})",
    ]
    other = f"({r2}, {r2 * r2})"            # the second intersection is also a solution, so never a distractor
    wrong = []
    for cand in candidates:
        if cand != correct and cand != other and cand not in wrong:
            wrong.append(cand)
        if len(wrong) == 3:
            break
    pairs = wrong + [correct]
    random.shuffle(pairs)
    letters = "ABCD"
    correct_letter = letters[pairs.index(correct)]
    opts = [f"{letters[i]}  {pairs[i]}" for i in range(4)]
    svg = _svg_parabola_line(r1, r2, a, b, mark="both", axis_numbers=True, minor_grid=True)
    q = (
        rf"Which point is a solution of \(y = x^2\) and {_fmt_line_eq(a, b)}? "
        rf"(There are two intersections on the graph.)<br>{svg}"
    )
    sol = f"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "A solution lies on both the curve and the line.", 2, opts, correct_letter


@verifies('alg', task='keyed_text', text='the solution of both equations')
def _gsim_mcq_solution_meaning():
    correct = "The solution of both equations"
    wrong = [
        "The y-intercept of one line",
        "The gradient of both lines",
        "The midpoint of the axes",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = "On a graph of two straight lines, what does the point where they cross represent?"
    sol = (
        rf"The crossing point fits both equations, so it is <strong>the solution of both "
        rf"equations</strong>. Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "The intersection satisfies both lines at once.", 1, opts, correct_letter


@verifies('alg', task='intersect_lines_text')
def _gsim_mcq_find_intersection():
    ix = random.randint(1, 4)
    iy = random.randint(2, 7)
    while iy == ix:
        iy = random.randint(2, 7)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    correct = f"({ix}, {iy})"
    wrong = [f"({ix + 1}, {iy})", f"({ix}, {iy - 2})", f"({iy}, {ix})"]
    pairs = wrong + [correct]
    random.shuffle(pairs)
    letters = "ABCD"
    correct_letter = letters[pairs.index(correct)]
    opts = [f"{letters[i]}  {pairs[i]}" for i in range(4)]
    q = rf"Where do {_fmt_line_eq(m1, c1)} and {_fmt_line_eq(m2, c2)} intersect?"
    sol = (
        rf"Set the equations equal and solve: \(x = {ix}\), \(y = {iy}\), so "
        rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Set the two right-hand sides equal, then solve for x.", 3, opts, correct_letter


@verifies('alg', task='count_lines_text')
def _gsim_mcq_parallel_zero():
    m = random.randint(1, 3)
    c1 = random.randint(1, 4)
    c2 = c1 + random.randint(1, 4)
    correct = "0"
    wrong = ["1", "2", "Infinitely many"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"How many solutions does the pair {_fmt_line_eq(m, c1)} and {_fmt_line_eq(m, c2)} have?"
    sol = (
        rf"Same gradient ({m}) but different intercepts → parallel lines that never meet → "
        rf"<strong>0</strong> solutions. Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Equal gradients mean the lines are parallel.", 2, opts, correct_letter


@verifies('alg', task='keyed_text', text='1')
def _gsim_mcq_tangent_count():
    correct = "1"
    wrong = ["0", "2", "Infinitely many"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = "A straight line is a tangent to a parabola (it just touches the curve). How many solutions does this give?"
    sol = (
        rf"A tangent meets the curve at exactly one point → <strong>1</strong> solution. "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "A tangent touches the curve at a single point.", 2, opts, correct_letter


_GSIM_MCQ_POOL = [
    _gsim_mcq_read_coords,
    _gsim_mcq_parallel_count,
    _gsim_mcq_parabola_intersections,
    _gsim_mcq_parabola_point,
    _gsim_mcq_solution_meaning,
    _gsim_mcq_find_intersection,
    _gsim_mcq_parallel_zero,
    _gsim_mcq_tangent_count,
]

# Phase 2 (2026-10-27): each band has its own list of the 8 generators (before, every band served the first four).
# Reading a crossing point off two lines and what a crossing means are Foundation; solving two lines for the
# intersection and a point on a line and a parabola are the middle and top; the tangent (one solution) is the top.
_GSIM_MCQ_BANDS = {
    "foundational": [_gsim_mcq_read_coords, _gsim_mcq_solution_meaning, _gsim_mcq_parallel_count,
                     _gsim_mcq_parallel_zero, _gsim_mcq_parabola_intersections],
    "intermediate": [_gsim_mcq_find_intersection, _gsim_mcq_parabola_intersections, _gsim_mcq_parabola_point,
                     _gsim_mcq_read_coords, _gsim_mcq_parallel_zero, _gsim_mcq_parallel_count],
    "difficult": [_gsim_mcq_tangent_count, _gsim_mcq_parabola_point, _gsim_mcq_find_intersection,
                  _gsim_mcq_parabola_intersections, _gsim_mcq_parallel_zero],
}


def _gsim_mcq_dispatch():
    return random.choice(_GSIM_MCQ_POOL)()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 BATCH B (docs/GCSE_MATHS_VARIETY.md section 19): new kinds. They live here because they draw with the
# helpers above; the checks that read these drawings are in scripts/gcse_verify/solvers_variety_b.py.
# ══════════════════════════════════════════════════════════════════════════════

def _line_cases():
    """(m1, c1, m2, c2, ix, iy): two lines in the first quadrant, y-intercepts 0 to 6, meeting at a whole-number point."""
    out = []
    for m1 in range(1, 5):
        for m2 in range(1, 5):
            for c1 in range(0, 7):
                for c2 in range(0, 7):
                    if m1 > m2 and c2 > c1 and (c2 - c1) % (m1 - m2) == 0:
                        ix = (c2 - c1) // (m1 - m2)
                        if 1 <= ix <= 6:
                            out.append((m1, c1, m2, c2, ix, m1 * ix + c1))
    return out


_LINE_CASES = _line_cases()


@verifies('alg', task='gsim_coord', which='x')
def _gsim_f_read_x_at_crossing():
    ix, iy = random.randint(1, 6), random.randint(3, 9)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True, minor_grid=True)
    q = (rf"The graph shows two straight lines that meet at the point <strong>P</strong>.<br>{svg}<br>"
         rf"Write down the <strong>x</strong>-coordinate of <strong>P</strong>.")
    s = rf"Go down from P to the x-axis: <strong>\(x = {ix}\)</strong>."
    return q, s, "The x-coordinate is how far P is across, read on the horizontal axis.", 1, _gsim_linear_answer(ix, "x")


@verifies('alg', task='gsim_intercept')
def _gsim_f_read_y_intercept():
    m1, c1, m2, c2, ix, iy = random.choice(_LINE_CASES)
    which = random.choice([1, 2])
    svg = _svg_two_lines(m1, c1, m2, c2, ix, iy, point_label=None, axis_numbers=True, x_min=0, y_min=0, minor_grid=True)
    c = c1 if which == 1 else c2
    q = (rf"The graph shows the lines \(L_1\) (blue) and \(L_2\) (red).<br>{svg}<br>"
         rf"Write down the y-intercept of line L{'₁' if which == 1 else '₂'}.")
    s = (rf"The y-intercept is where the line crosses the y-axis, at \( x = 0 \). "
         rf"Line L{'₁' if which == 1 else '₂'} crosses at <strong>\(y = {c}\)</strong>.")
    return q, s, "Find where the line meets the vertical axis (the line x = 0).", 1, c


@verifies('alg', task='gsim_solve_stated')
def _gsim_f_solve_from_equations():
    ix, iy = random.randint(1, 5), random.randint(3, 9)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(m1, c1, m2, c2, ix, iy, show_point=False, axis_numbers=True, minor_grid=True)
    q = (rf"The lines {_fmt_line_eq(m1, c1)} and {_fmt_line_eq(m2, c2)} are drawn on the grid.<br>{svg}<br>"
         rf"Use the graph to solve the simultaneous equations.")
    s = rf"The solution is where the lines cross: <strong>\(x = {ix},\; y = {iy}\)</strong>."
    return q, s, "The solution of the pair of equations is the point where the two lines cross.", 2, _gsim_pair_answer(ix, iy)


@verifies('alg', task='gsim_gradient')
def _gsim_f_read_gradient():
    ix, iy = random.randint(2, 5), random.randint(4, 9)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    which = random.choice([1, 2])
    svg = _svg_two_lines(m1, c1, m2, c2, ix, iy, show_point=False, axis_numbers=True, minor_grid=True)
    m = m1 if which == 1 else m2
    q = (rf"The graph shows two lines, \(L_1\) (blue) and \(L_2\) (red).<br>{svg}<br>"
         rf"Work out the gradient of line L{'₁' if which == 1 else '₂'}.")
    s = (rf"Choose two points on the line and divide the change up by the change across. "
         rf"Each 1 across gives {m} up, so the gradient is <strong>{m}</strong>.")
    return q, s, "Gradient is the change in y divided by the change in x between two points on the line.", 2, m


@verifies('alg', task='gsim_solve_stated')
def _gsim_i_standard_form_pair():
    """Intermediate: one equation is written as x + y = k (a negative gradient), the other as y = mx + c."""
    ix, iy = random.randint(2, 5), random.randint(2, 7)
    s_tot = ix + iy
    m2 = random.randint(1, 3)
    c2 = iy - m2 * ix
    svg = _svg_two_lines(-1, s_tot, m2, c2, ix, iy, show_point=False, axis_numbers=True, minor_grid=True)
    q = (rf"The equations \( x + y = {s_tot} \) and {_fmt_line_eq(m2, c2)} are shown as straight lines.<br>{svg}<br>"
         rf"Use the graph to find the solution of the simultaneous equations.")
    s = (rf"\( x + y = {s_tot} \) is the line \( y = -x + {s_tot} \), which slopes down. The two lines cross at "
         rf"<strong>\(x = {ix},\; y = {iy}\)</strong>.")
    return q, s, "Rewrite x + y = k as y = -x + k to see which line is which, then read the crossing point.", 3, _gsim_pair_answer(ix, iy)


@verifies('alg', task='gsim_context_cost')
def _gsim_i_cost_at_break_even():
    """Intermediate: the cost at which two plans match, read from the graph."""
    ix = random.randint(3, 6)
    rate_steep = random.randint(3, 5)
    rate_gentle = random.randint(2, rate_steep - 1)
    fee_steep = random.randint(0, 2)
    iy = rate_steep * ix + fee_steep
    fee_gentle = iy - rate_gentle * ix

    def fee(amount, kind):
        return f"no {kind}" if amount == 0 else f"a £{amount} {kind}"
    names = random.choice([("FastPrint", "LowCost", "setup fee", "poster"), ("CityBikes", "RideEasy", "joining fee", "hour"),
                           ("BrightSpark", "VoltCo", "setup fee", "unit of power")])
    svg = _svg_two_lines(rate_steep, fee_steep, rate_gentle, fee_gentle, ix, iy, point_label="P", axis_numbers=True,
                         x_min=0, y_min=0, line_label_1=names[0], line_label_2=names[1], minor_grid=True)
    q = (rf"Two firms charge for the same job.<br><strong>{names[0]}</strong>: {fee(fee_steep, names[2])} plus £{rate_steep} per {names[3]}.<br>"
         rf"<strong>{names[1]}</strong>: {fee(fee_gentle, names[2])} plus £{rate_gentle} per {names[3]}.<br>{svg}<br>"
         rf"The lines cross at <strong>P</strong>. What is the total cost, in pounds, when the two firms charge the same?")
    s = (rf"The firms charge the same at P. Read the y-coordinate (the cost) of P: <strong>£{iy}</strong>.<br>"
         rf"Check: {fee_steep} + {rate_steep} × {ix} = {iy} and {fee_gentle} + {rate_gentle} × {ix} = {iy}.")
    return q, s, "Costs are equal where the lines cross. The cost is the vertical (y) value of that point.", 3, iy


@verifies('alg', task='gsim_x_values')
def _gsim_i_parabola_two_solutions():
    r1, r2, a, b = _parabola_line_roots()
    svg = _svg_parabola_line(r1, r2, a, b, mark="both", axis_numbers=True, minor_grid=True)
    q = (rf"The graphs of \(y = x^2\) and {_fmt_line_eq(a, b)} are drawn and the two points where they cross are marked.<br>{svg}<br>"
         rf"Write down the two solutions of \( x^2 = {_lin(a, b)} \).")
    s = rf"The solutions are the x-coordinates of the crossing points: <strong>x = {r1}</strong> and <strong>x = {r2}</strong>."
    return q, s, "Solutions of x^2 = (line) are the x-values where the two graphs meet.", 3, {'type': 'quadratic_roots', 'roots': (str(r1), str(r2))}


@verifies('alg', task='gsim_x_values')
def _gsim_d_horizontal_line_roots():
    """Difficult: rearrange an equation to x^2 = k, then read the two crossings of y = k with y = x^2.

    Review 2026-10-28: "use the graph to solve x^2 = 16" was a Foundation reading with three possible questions; the
    equation is now written so that it has to be rearranged first (x^2 - 16 = 0, 2x^2 = 32 or x^2 + 3 = 19).
    """
    r = random.randint(2, 5)
    k = r * r
    form = random.choice(['minus', 'times', 'plus'])
    if form == 'minus':
        eq, step = rf'x^2 - {k} = 0', rf'Add {k} to both sides: \( x^2 = {k} \).'
    elif form == 'times':
        a = random.choice([2, 3, 4])
        eq, step = rf'{a}x^2 = {a * k}', rf'Divide both sides by {a}: \( x^2 = {k} \).'
    else:
        c = random.randint(2, 9)
        eq, step = rf'x^2 + {c} = {k + c}', rf'Subtract {c} from both sides: \( x^2 = {k} \).'
    svg = _svg_parabola_line(-r, r, 0, k, mark="none", axis_numbers=True, minor_grid=True)
    q = (rf"The graphs of \(y = x^2\) and \(y = {k}\) are drawn.<br>{svg}<br>"
         rf"Use the graph to solve \( {eq} \).")
    s = (rf"{step} So the solutions are where the horizontal line \( y = {k} \) meets the curve: "
         rf"<strong>x = {-r}</strong> or <strong>x = {r}</strong>.")
    return q, s, "Rearrange the equation to x^2 = a number first. Then read where that horizontal line crosses the curve: there are two answers.", 3, {'type': 'quadratic_roots', 'roots': (str(-r), str(r))}


@verifies('alg', task='gsim_tangent_k')
def _gsim_d_tangent_constant():
    r = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])          # review: negative gradients too (was 4 questions)
    a, b = 2 * r, -r * r
    svg = _svg_parabola_line(r, r, a, b, mark="one", axis_numbers=True, minor_grid=True)
    rr = f'({r})' if r < 0 else str(r)
    q = (rf"The line \(y = {a}x + k\) touches the curve \(y = x^2\) at the marked point, as shown.<br>{svg}<br>"
         rf"Find the value of \( k \).")
    s = (rf"The touching point is \( ({r}, {r * r}) \), and it is on the line: \( {r * r} = {a} \times {rr} + k \).<br>"
         rf"So \( k = {r * r} - {a * r} \) = <strong>{b}</strong>.")
    return q, s, "The touching point lies on both the curve and the line. Put its coordinates into the line equation.", 3, _gsim_linear_answer(b, "k")


@verifies('alg', task='gsim_context_cheaper')
def _gsim_d_cheaper_up_to():
    ix = random.randint(3, 6)
    rate_steep = random.randint(3, 5)
    rate_gentle = random.randint(2, rate_steep - 1)
    fee_steep = random.randint(0, 2)
    iy = rate_steep * ix + fee_steep
    fee_gentle = iy - rate_gentle * ix
    names = random.choice([("Hire A", "Hire B", "booking fee", "day"), ("Plan X", "Plan Y", "joining fee", "week")])

    def fee(amount, kind):
        return f"no {kind}" if amount == 0 else f"a £{amount} {kind}"
    svg = _svg_two_lines(rate_steep, fee_steep, rate_gentle, fee_gentle, ix, iy, point_label="P", axis_numbers=True,
                         x_min=0, y_min=0, line_label_1=names[0], line_label_2=names[1], minor_grid=True)
    q = (rf"<strong>{names[0]}</strong> charges {fee(fee_steep, names[2])} plus £{rate_steep} per {names[3]}. "
         rf"<strong>{names[1]}</strong> charges {fee(fee_gentle, names[2])} plus £{rate_gentle} per {names[3]}.<br>{svg}<br>"
         rf"What is the largest whole number of {names[3]}s for which <strong>{names[0]}</strong> is cheaper than <strong>{names[1]}</strong>?")
    s = (rf"The lines cross at \( x = {ix} \), where the costs are equal. To the left of P the {names[0]} line is lower, so it is cheaper "
         rf"for fewer than {ix} {names[3]}s. The largest whole number is <strong>{ix - 1}</strong>.")
    return q, s, "Find where the lines cross. The cheaper plan is the lower line, and it must be strictly cheaper, so the crossing value itself is not included.", 4, ix - 1


@verifies('alg', task='gsim_x_values')
def _gsim_d_read_roots_then_check():
    r1, r2, a, b = _parabola_line_roots()
    svg = _svg_parabola_line(r1, r2, a, b, mark="none", axis_numbers=True, minor_grid=True)
    q = (rf"The graphs of \(y = x^2\) and {_fmt_line_eq(a, b)} are shown.<br>{svg}<br>"
         rf"Use the graph to find the solutions of \( {_quad(1, -a, -b)} = 0 \).")
    s = (rf"Rearranging \( {_quad(1, -a, -b)} = 0 \) gives \( x^2 = {_lin(a, b)} \), so the solutions are where the curve and line cross: "
         rf"<strong>x = {r1}</strong> and <strong>x = {r2}</strong>.<br>Check: \( ({r1})^2 = {r1 * r1} \) and \( {a} \times ({r1}) {'+' if b >= 0 else '-'} {abs(b)} = {r1 * r1} \).")
    return q, s, "Move the terms to get x^2 on its own on one side. Then the answers are the x-values at the crossings.", 4, {'type': 'quadratic_roots', 'roots': (str(r1), str(r2))}


@verifies('alg', task='gsim_second_intercept')
def _gsim_d_find_second_constant():
    """Difficult: line L2 has a stated gradient and passes through P; find its y-intercept."""
    ix, iy = random.randint(2, 5), random.randint(4, 9)
    m1 = random.randint(1, 3)
    c1 = iy - m1 * ix
    m2 = -random.randint(1, 2)
    c2 = iy - m2 * ix
    svg = _svg_two_lines(m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True, minor_grid=True)
    q = (rf"The graph shows the lines \(L_1\) and \(L_2\) meeting at <strong>P</strong>.<br>{svg}<br>"
         rf"\(L_2\) has gradient \( {m2} \) and the equation of \(L_2\) is \( y = {'-' if m2 == -1 else m2}x + c \). Use the coordinates of P to find the value of \( c \).")
    s = (rf"P is \( ({ix}, {iy}) \). Put this into \( y = {'-' if m2 == -1 else m2}x + c \): \( {iy} = {m2} \times {ix} + c \), so \( c = {iy} + {-m2 * ix} \) = <strong>{c2}</strong>.")
    return q, s, "P lies on L2, so its x and y values must fit the equation of L2. Substitute them and solve for c.", 4, _gsim_linear_answer(c2, "c")


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _gsim_f_read_intersection,
    _gsim_f_meaning_of_crossing,
    _gsim_f_which_point_on_both,
    _gsim_f_read_y_at_crossing,
    _gsim_f_how_many_solutions_lines,
]

_INTERMEDIATE = [
    _gsim_i_equations_from_graph,
    _gsim_i_parabola_read_one_point,
    _gsim_i_parabola_count_intersections,
    _gsim_i_no_solution_parallel,
    _gsim_i_negative_gradient,
    _gsim_i_verify_algebra_from_graph,
]

_DIFFICULT = [
    _gsim_d_both_parabola_points,
    _gsim_d_tangent_one_solution,
    _gsim_d_line_misses_parabola,
    _gsim_d_context_graph,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def _batch_b_pools():
    return {
        "foundational": _FOUNDATIONAL + [_gsim_f_read_x_at_crossing, _gsim_f_read_y_intercept,
                                         _gsim_f_solve_from_equations, _gsim_f_read_gradient],
        "intermediate": _INTERMEDIATE + [_gsim_i_standard_form_pair, _gsim_i_cost_at_break_even,
                                         _gsim_i_parabola_two_solutions],
        "difficult": _DIFFICULT + [_gsim_d_horizontal_line_roots, _gsim_d_tangent_constant, _gsim_d_cheaper_up_to,
                                   _gsim_d_read_roots_then_check, _gsim_d_find_second_constant],
    }


def gcse_graphical_simultaneous_equations_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_pool(
            _GSIM_MCQ_BANDS.get(difficulty, _GSIM_MCQ_POOL), "graphical_simultaneous_equations", difficulty
        )

    pools = _batch_b_pools()
    pool = pools.get(difficulty)
    if not pool:
        return select_tier_variants(pools["foundational"] + pools["intermediate"] + pools["difficult"])
    return select_tier_variants(pool)


def gcse_graphical_simultaneous_equations(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_graphical_simultaneous_equations_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "graphical_simultaneous_equations",
            options=opts, correct_answer=ans,
        )

    variants = gcse_graphical_simultaneous_equations_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    return _gsim_problem_from_output(variant(), difficulty)
