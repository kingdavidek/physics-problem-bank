"""
GCSE Maths – Graphical Simultaneous Equations
5 foundational · 5 intermediate · 5 difficult · 8 MCQ (randomised, with SVG)
"""
import math
import random
from generators.shared.utils import make_problem
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


def _svg_open():
    p = _GSIM_PAD
    vb_w = _GSIM_W + 2 * p
    vb_h = _GSIM_H + 2 * p
    return (
        f'<svg class="gsim-diagram" width="{_GSIM_MAX_W}" height="{_gsim_display_h()}" '
        f'viewBox="{-p} {-p} {vb_w} {vb_h}" preserveAspectRatio="xMidYMid meet" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )


def _svg_grid(bounds):
    x0, x1, y0, y1 = bounds
    parts = []
    x_step = _axis_stride(x0, x1)
    y_step = _axis_stride(y0, y1)
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


def _svg_two_lines(
    m1, c1, m2, c2, ix, iy,
    show_point=True,
    point_label=None,
    line_labels=True,
    axis_numbers=False,
    extra_points=None,
):
    """
    extra_points: list of (x, y, label) e.g. [('A', 3, 5)] — label is a single letter, not coordinates.
    Never pass coordinate strings as labels on exam-style read/graph questions.
    """
    x0, x1 = ix - 3, ix + 3
    pts = [(ix, iy), (x0, m1 * x0 + c1), (x1, m1 * x1 + c1), (x0, m2 * x0 + c2), (x1, m2 * x1 + c2)]
    if extra_points:
        for item in extra_points:
            pts.append((item[1], item[2]))
    bounds = _bounds(pts, 1)
    svg = _svg_open() + _svg_grid(bounds)
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
        lx, ly = _xy(bounds, bounds[0] + 0.3, m1 * (bounds[0] + 0.3) + c1)
        svg += f'<text x="{lx}" y="{ly - 6}" font-size="11" fill="#1a6fa8">L₁</text>'
        lx2, ly2 = _xy(bounds, bounds[1] - 0.5, m2 * (bounds[1] - 0.5) + c2)
        svg += f'<text x="{lx2}" y="{ly2 + 14}" font-size="11" fill="#c0392b">L₂</text>'
    return svg + "</svg>"


def _svg_parallel_lines(m, c1, c2, axis_numbers=False):
    x0, x1 = 0, 6
    pts = [(x0, m * x0 + c1), (x1, m * x1 + c1), (x0, m * x0 + c2), (x1, m * x1 + c2)]
    bounds = _bounds(pts, 1)
    svg = _svg_open() + _svg_grid(bounds)
    if axis_numbers:
        svg += _svg_axis_numbers(bounds)
    svg += _svg_polyline(bounds, _line_pts(m, c1, bounds[0], bounds[1]), "#1a6fa8")
    svg += _svg_polyline(bounds, _line_pts(m, c2, bounds[0], bounds[1]), "#c0392b", dash="6 4")
    return svg + "</svg>"


def _svg_parabola_line(r1, r2, a, b, mark="none", axis_numbers=False):
    """
    mark: 'none' | 'one' | 'both' — dots only, never coordinate labels on the diagram.
    """
    y1, y2 = r1 * r1, r2 * r2
    x0, x1 = min(r1, r2) - 1, max(r1, r2) + 1
    pts = _parabola_pts(x0, x1) + _line_pts(a, b, x0, x1)
    if mark in ("one", "both"):
        pts += [(r1, y1)]
    if mark == "both":
        pts.append((r2, y2))
    bounds = _bounds(pts, 1)
    svg = _svg_open() + _svg_grid(bounds)
    if axis_numbers:
        svg += _svg_axis_numbers(bounds)
    svg += _svg_polyline(bounds, _parabola_pts(bounds[0], bounds[1]), "#059669", width=2.8)
    svg += _svg_polyline(bounds, _line_pts(a, b, bounds[0], bounds[1]), "#1a6fa8")
    if mark in ("one", "both"):
        svg += _svg_point(bounds, r1, y1)
    if mark == "both":
        svg += _svg_point(bounds, r2, y2)
    return svg + "</svg>"


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

def _gsim_f_read_intersection():
    ix = random.randint(1, 5)
    iy = random.randint(2, 8)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True,
    )
    q = (
        rf"The graphs of two linear equations are shown. "
        rf"The lines intersect at point <strong>P</strong>.<br>{svg}<br>"
        rf"What are the coordinates of <strong>P</strong>?"
    )
    s = rf"Read from the axes: <strong>\(({ix}, {iy})\)</strong>."
    return q, s, "Read x across, then y up from the numbered axes.", 2


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
    s = (
        r"The <strong>(x, y)</strong> pair that satisfies <strong>both</strong> equations — "
        r"the solution to the simultaneous equations."
    )
    return q, s, "One point on both lines = one simultaneous solution.", 1


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
    opts = [f"({w[0]}, {w[1]})" for w in wrong] + [correct]
    random.shuffle(opts)
    letters = "ABCD"
    correct_letter = letters[opts.index(correct)]
    plotted = [(letter, *_parse_coord_pair(opt)) for letter, opt in zip(letters, opts)]
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy,
        show_point=False, axis_numbers=True, extra_points=plotted,
    )
    q = rf"Which labelled point lies on <strong>both</strong> lines?<br>{svg}<br>"
    for i, o in enumerate(opts):
        q += rf"{letters[i]}) {o} &nbsp;&nbsp;"
    s = rf"Only <strong>{correct_letter}) {correct}</strong> sits on both lines."
    return q, s, "The point on both lines is at the intersection.", 2


def _gsim_f_read_y_at_crossing():
    ix = random.randint(2, 6)
    iy = random.randint(4, 10)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True,
    )
    q = (
        rf"The lines intersect at \(x = {ix}\) on the graph below.<br>{svg}<br>"
        rf"What is the value of <strong>\(y\)</strong> at the intersection?"
    )
    s = rf"At \(x = {ix}\), the lines meet at <strong>\(y = {iy}\)</strong>."
    return q, s, "The y-coordinate at the crossing is part of the solution pair.", 2


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
    return q, s, "Parallel distinct lines never meet → 0 solutions.", 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _gsim_i_equations_from_graph():
    ix, iy = random.randint(2, 5), random.randint(4, 9)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True,
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
    opts = wrong + [correct]
    random.shuffle(opts)
    letters = "ABCD"
    correct_letter = letters[opts.index(correct)]
    q += "<br>" + "<br>".join(f"{letters[i]}) {opts[i]}" for i in range(4))
    s = rf"Lines match slopes and intercepts at the crossing → <strong>{correct_letter}</strong>."
    return q, s, "Compare gradients and where each line crosses the y-axis.", 3


def _gsim_i_parabola_read_one_point():
    r1, r2, a, b = _parabola_line_roots(2, 5)
    y1 = r1 * r1
    svg = _svg_parabola_line(r1, r2, a, b, mark="one", axis_numbers=True)
    q = (
        rf"The graphs of \(y = x^2\) and {_fmt_line_eq(a, b)} are shown. "
        rf"One intersection is marked with a dot.<br>{svg}<br>"
        rf"Write this solution as coordinates <strong>(x, y)</strong>."
    )
    s = rf"Read from the axes: <strong>\(({r1}, {y1})\)</strong>."
    return q, s, "Each crossing of curve and line is one solution pair.", 3


def _gsim_i_parabola_count_intersections():
    r1, r2, a, b = _parabola_line_roots()
    svg = _svg_parabola_line(r1, r2, a, b, mark="none")
    q = (
        rf"How many solutions do \(y = x^2\) and {_fmt_line_eq(a, b)} have, "
        rf"according to the graph?<br>{svg}"
    )
    s = r"Two distinct crossings → <strong>2 solutions</strong>."
    return q, s, "Count intersection points on the diagram.", 2


def _gsim_i_no_solution_parallel():
    m = random.randint(1, 3)
    c1, c2 = random.randint(0, 3), random.randint(5, 9)
    svg = _svg_parallel_lines(m, c1, c2)
    q = (
        rf"Two lines are graphed below.<br>{svg}<br>"
        r"What can you say about solving them <strong>simultaneously</strong>?"
    )
    s = (
        r"Lines are <strong>parallel</strong> (same gradient, different intercepts) → "
        r"<strong>no solutions</strong>."
    )
    return q, s, "No intersection means no (x, y) works in both equations.", 2


def _gsim_i_negative_gradient():
    ix, iy = 3, 4
    m1, c1, m2, c2 = -1, iy + ix, 2, iy - 2 * ix
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True,
    )
    q = (
        rf"Use the graph to find the simultaneous solution (point <strong>P</strong>).<br>{svg}"
    )
    s = rf"<strong>\(x = {ix},\; y = {iy}\)</strong> at the intersection."
    return q, s, "Read x and y from the numbered axes at P.", 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

def _gsim_d_both_parabola_points():
    r1, r2, a, b = _parabola_line_roots(-2, 4)
    y1, y2 = r1 * r1, r2 * r2
    svg = _svg_parabola_line(r1, r2, a, b, mark="none", axis_numbers=True)
    q = (
        rf"Solve graphically: \(y = x^2\) and {_fmt_line_eq(a, b)}.<br>{svg}<br>"
        rf"State <strong>both</strong> coordinate pairs."
    )
    s = rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>."
    return q, s, "Both crossings are solutions — list them clearly.", 4


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
    return q, s, "Touching = one solution; crossing twice = two.", 3


def _gsim_d_line_misses_parabola():
    """y = x² and y = x - 5 — negative discriminant, no real intersections."""
    a, b = 1, -5
    pts = _parabola_pts(-2, 4) + _line_pts(a, b, -2, 4)
    bounds = _bounds(pts, 1)
    svg = _svg_open() + _svg_grid(bounds)
    svg += _svg_polyline(bounds, _parabola_pts(bounds[0], bounds[1]), "#059669", width=2.8)
    svg += _svg_polyline(bounds, _line_pts(a, b, bounds[0], bounds[1]), "#1a6fa8")
    svg += "</svg>"
    q = (
        rf"The graphs of \(y = x^2\) and \(y = x - 5\) are sketched on the same axes.<br>{svg}<br>"
        r"How many real simultaneous solutions are there?"
    )
    s = (
        r"\(x^2 = x - 5\) → \(x^2 - x + 5 = 0\) has negative discriminant → "
        r"<strong>0 real solutions</strong> (curves do not cross)."
    )
    return q, s, "No intersection on the graph means no real simultaneous solutions.", 3


def _gsim_d_context_graph():
    ix = random.randint(3, 6)
    cost_a = random.randint(2, 4)
    cost_b = random.randint(3, 5)
    iy = cost_a * ix + random.randint(0, 2)
    m1, c1 = cost_a, iy - cost_a * ix
    m2, c2 = cost_b, iy - cost_b * ix
    while m1 == m2:
        m2 += 1
        c2 = iy - m2 * ix
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True,
    )
    q = (
        rf"Graph A shows cost of provider 1; Graph B shows provider 2 (same axes). "
        rf"They cross at point <strong>P</strong>.<br>{svg}<br>"
        rf"At how many items \(x\) do the <strong>costs match</strong>?"
    )
    s = rf"Costs match only at the intersection → <strong>\(x = {ix}\)</strong> (one value)."
    return q, s, "Equal cost at the crossing point of the two lines.", 3


def _gsim_d_verify_algebra_from_graph():
    r1, r2, a, b = _parabola_line_roots(1, 4)
    y1 = r1 * r1
    svg = _svg_parabola_line(r1, r2, a, b, mark="one", axis_numbers=True)
    q = (
        rf"The graph shows one intersection of \(y = x^2\) and {_fmt_line_eq(a, b)}.<br>{svg}<br>"
        rf"Algebra gives \(x = {r1}\) or \(x = {r2}\). Which \(x\)-value matches the <strong>marked</strong> point?"
    )
    s = rf"The marked point has <strong>\(x = {r1}\)</strong> (and \(y = {y1}\))."
    return q, s, "Graph and algebra must agree on the same solution pairs.", 3


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (8 — randomised, often with SVG)
# ══════════════════════════════════════════════════════════════════════════════

def _gsim_mcq_read_coords():
    ix = random.randint(1, 5)
    iy = random.randint(2, 8)
    m1, c1, m2, c2 = _lines_at_point(ix, iy)
    svg = _svg_two_lines(
        m1, c1, m2, c2, ix, iy, point_label="P", axis_numbers=True,
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


def _gsim_mcq_parabola_point():
    r1, r2, a, b = _parabola_line_roots()
    y1 = r1 * r1
    correct = f"({r1}, {y1})"
    candidates = [
        f"({r2}, {y1})",
        f"({r1}, {r2})",
        f"({r1 + r2}, {(r1 + r2) ** 2})",
        f"({r2}, {r2 * r2})",
        f"({r1}, {y1 + 1})",
    ]
    wrong = []
    for cand in candidates:
        if cand != correct and cand not in wrong:
            wrong.append(cand)
        if len(wrong) == 3:
            break
    pairs = wrong + [correct]
    random.shuffle(pairs)
    letters = "ABCD"
    correct_letter = letters[pairs.index(correct)]
    opts = [f"{letters[i]}  {pairs[i]}" for i in range(4)]
    svg = _svg_parabola_line(r1, r2, a, b, mark="both", axis_numbers=True)
    q = (
        rf"Which point is a solution of \(y = x^2\) and {_fmt_line_eq(a, b)}? "
        rf"(There are two intersections on the graph.)<br>{svg}"
    )
    sol = f"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "A solution lies on both the curve and the line.", 2, opts, correct_letter


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


def _gsim_mcq_dispatch():
    return random.choice(_GSIM_MCQ_POOL)()


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
]

_DIFFICULT = [
    _gsim_d_both_parabola_points,
    _gsim_d_tangent_one_solution,
    _gsim_d_line_misses_parabola,
    _gsim_d_context_graph,
    _gsim_d_verify_algebra_from_graph,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_graphical_simultaneous_equations_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_pool(
            _GSIM_MCQ_POOL, "graphical_simultaneous_equations", difficulty, count=4
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


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

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "maths", "graphical_simultaneous_equations",
    )
