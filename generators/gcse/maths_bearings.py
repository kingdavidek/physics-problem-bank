"""
GCSE Maths – Bearings
15 foundational · 18 intermediate · 18 difficult · 18 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Proof-only variants stay as 4-tuples (no auto-grade).
"""
import random
import math
from generators.shared.utils import make_problem
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


# ─────────────────────────────────────────────────────────────────────────────
# Numeric helpers
# ─────────────────────────────────────────────────────────────────────────────

def _dp(x, places=2):
    val = round(x, places)
    if val == int(val):
        return str(int(val))
    return f"{val:.{places}f}".rstrip('0').rstrip('.')


def _brg_raw(value, places=2):
    """Canonical numeric string for typed answer checking."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _dp(value, places)
    return str(value)


def _brg_answer(b):
    """Three-figure bearing (0–359) for the bearing answer checker."""
    return {'type': 'bearing', 'value': int(round(b)) % 360}


def _brg_keyword_answer(value):
    return {'type': 'keyword', 'value': str(value).strip().lower()}


def _brg_fields_answer(values, labels, places=2):
    return {
        'type': 'number_fields',
        'values': tuple(_brg_raw(v, places) for v in values),
        'labels': tuple(labels),
    }


def _brg_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            if values and len(values) == len(labels):
                extra = {
                    'correct_answer_raw': '|'.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_format_hint': (
                        'Enter a number or 3-figure bearing in every field'
                    ),
                }
        elif isinstance(raw, dict) and raw.get('type') == 'bearing':
            value = raw.get('value')
            if value is not None:
                deg = int(round(value)) % 360
                extra = {
                    'correct_answer_raw': f'{deg:03d}',
                    'answer_type': 'bearing',
                    'answer_format_hint': 'Enter a 3-figure bearing (e.g. 045)',
                }
        elif isinstance(raw, dict) and raw.get('type') == 'keyword':
            value = raw.get('value')
            if value is not None and str(value).strip():
                extra = {
                    'correct_answer_raw': str(value).strip().lower(),
                    'answer_type': 'keyword',
                    'answer_format_hint': 'Enter your answer in words',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _brg_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number (degrees optional)',
            }
        elif isinstance(raw, str):
            extra = {
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number (degrees optional)',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'bearings', **extra
    )


def _brg(b):
    """Format integer bearing as 3-digit string, e.g. 045°."""
    return f"{int(round(b)) % 360:03d}°"


def _back(b):
    return (int(b) + 180) % 360


def _E(dist, bearing):
    """East component of travel."""
    return dist * math.sin(math.radians(bearing))


def _N_comp(dist, bearing):
    """North component of travel (positive = northward)."""
    return dist * math.cos(math.radians(bearing))


def _bearing_from_EN(east, north):
    """Compute bearing from displacement components."""
    return math.degrees(math.atan2(east, north)) % 360


# ─────────────────────────────────────────────────────────────────────────────
# SVG helpers
# ─────────────────────────────────────────────────────────────────────────────

# ── Standard problem-diagram display size (site-wide standard) ──
# Every problem-generator SVG renders responsively at this width, scaling its
# content (lines + labels) uniformly via the viewBox so all diagrams share one
# consistent, legible footprint.
_STD_SVG_MAX_W = 320
_STD_SVG_MAX_H = 320


def _std_svg_open(min_x, min_y, vw, vh):
    """Standard responsive opening <svg> tag used by all problem diagrams."""
    return (
        f'<svg width="100%" viewBox="{min_x:.0f} {min_y:.0f} {vw:.0f} {vh:.0f}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'style="background:#f9f8f5;border-radius:6px;'
        f'max-width:{_STD_SVG_MAX_W}px;max-height:{_STD_SVG_MAX_H}px;'
        f'display:block;margin:10px auto;vertical-align:middle;">'
    )


_BRG_SVG_MAX_W = _STD_SVG_MAX_W
# Compact defaults for fitted multipart diagrams (frame + content scaled together)
_BRG_N_LEN = 42
_BRG_ARC_R = 20
_BRG_ARC_GAP = 14
_BRG_ARC_FONT = 11
_BRG_N_FONT = 12
_BRG_LBL_FONT = 12
_BRG_DOT_R = 3.5
_BRG_ROUTE_STROKE = 2
_BRG_JOURNEY_SPAN = 122
_BRG_RAY_LEN = 62
_BRG_FIT_MARGIN = 16


def _brg_arc_label_xy(cx, cy, bearing, arc_r, label_gap):
    mid = math.radians(bearing / 2)
    return (
        cx + (arc_r + label_gap) * math.sin(mid),
        cy - (arc_r + label_gap) * math.cos(mid),
    )


def _brg_svg_fitted(xs, ys, margin=_BRG_FIT_MARGIN):
    """Open SVG with viewBox cropped to content (+ margin for labels)."""
    min_x = min(xs) - margin
    max_x = max(xs) + margin
    min_y = min(ys) - margin
    max_y = max(ys) + margin
    vw = max(max_x - min_x, 60)
    vh = max(max_y - min_y, 60)
    return _std_svg_open(min_x, min_y, vw, vh)


def _north_elements(cx, cy, n_len=55, font_size=14):
    """North dashed arrow elements."""
    nx, ny = cx, cy - n_len
    ah = max(5, round(font_size * 0.45))
    return (
        f'<line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" '
        f'stroke="#666" stroke-width="2" stroke-dasharray="6,5"/>'
        f'<polygon points="{nx},{ny} {nx-ah},{ny+2*ah} {nx+ah},{ny+2*ah}" fill="#666"/>'
        f'<text x="{nx}" y="{ny-8}" font-size="{font_size}" fill="#444" '
        f'text-anchor="middle" font-weight="bold">N</text>'
    )


def _bearing_arc(cx, cy, bearing, arc_r=26, font_size=13, label_gap=18):
    """Clockwise arc from North to bearing direction, centred at (cx,cy)."""
    θ = math.radians(bearing)
    sx, sy = cx, cy - arc_r                          # start: North direction
    ex = cx + arc_r * math.sin(θ)
    ey = cy - arc_r * math.cos(θ)
    large = 1 if bearing > 180 else 0
    mid = math.radians(bearing / 2)
    lx = cx + (arc_r + label_gap) * math.sin(mid)
    ly = cy - (arc_r + label_gap) * math.cos(mid)
    return (
        f'<path d="M{sx},{sy} A{arc_r},{arc_r},0,{large},1,{ex:.1f},{ey:.1f}" '
        f'fill="none" stroke="#1a6fa8" stroke-width="1.5"/>',
        f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="{font_size}" fill="#1a6fa8" '
        f'text-anchor="middle" font-weight="bold">{_brg(bearing)}</text>',
    )


def _single_brg_svg(bearing, pt="A", dest="B",
                    cx=90, cy=120, n_len=55, ray=75, arc_r=26,
                    w=210, h=205):
    """
    Single-point bearing SVG: point A with North arrow, ray toward B,
    clockwise arc, and angle label.
    """
    θ = math.radians(bearing)
    rx = cx + ray * math.sin(θ)
    ry = cy - ray * math.cos(θ)
    # destination label offset (outside the ray tip)
    dlx = rx + 11 * math.sin(θ)
    dly = ry - 11 * math.cos(θ)
    # Clamp within SVG
    dlx = max(10.0, min(w - 10.0, dlx))
    dly = max(12.0, min(h - 6.0, dly))
    arc_path, arc_label = _bearing_arc(cx, cy, bearing, arc_r)
    return (
        _std_svg_open(0, 0, w, h)
        + _north_elements(cx, cy, n_len)
        + f'<line x1="{cx}" y1="{cy}" x2="{rx:.1f}" y2="{ry:.1f}" '
          f'stroke="#a13544" stroke-width="2"/>'
        + arc_path + arc_label
        + f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#333"/>'
        + f'<text x="{cx-11}" y="{cy+5}" font-size="12" fill="#333" font-weight="bold">{pt}</text>'
        + f'<text x="{dlx:.1f}" y="{dly:.1f}" font-size="12" fill="#a13544" font-weight="bold">{dest}</text>'
        + '</svg>'
    )


def _two_pt_svg(bearing, dist_px=70, ax=90, ay=135,
                show_back=True, w=240, h=220, label_a="A", label_b="B"):
    """
    Two-point bearing SVG: A and B with North arrows at both.
    Bearing of B from A is drawn with a blue arc.
    If show_back, a red-arc question mark is shown at B for the back bearing.
    """
    θ = math.radians(bearing)
    bx = ax + dist_px * math.sin(θ)
    by = ay - dist_px * math.cos(θ)
    bx = round(bx, 1)
    by = round(by, 1)
    n_len = 50
    arc_r = 22

    # Arc at A
    arc_a_path, arc_a_label = _bearing_arc(ax, ay, bearing, arc_r)

    # Back bearing arc at B (just a "?" label arc)
    back = _back(bearing)
    θb = math.radians(back)
    bsx, bsy = bx, by - arc_r
    bex = bx + arc_r * math.sin(θb)
    bey = by - arc_r * math.cos(θb)
    large_b = 1 if back > 180 else 0
    mid_b = math.radians(back / 2)
    qlx = bx + (arc_r + 14) * math.sin(mid_b)
    qly = by - (arc_r + 14) * math.cos(mid_b)

    svg = (
        _std_svg_open(0, 0, w, h)
        # North at A
        + _north_elements(ax, ay, n_len)
        # North at B
        + _north_elements(bx, by, n_len)
        # Dashed line AB
        + f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" '
          f'stroke="#888" stroke-width="1.5" stroke-dasharray="5,3"/>'
        # Arc at A (bearing shown)
        + arc_a_path + arc_a_label
        # Arc at B (back bearing "?" if show_back)
    )
    if show_back:
        svg += (
            f'<path d="M{bsx:.1f},{bsy:.1f} A{arc_r},{arc_r},0,{large_b},1,{bex:.1f},{bey:.1f}" '
            f'fill="none" stroke="#a13544" stroke-width="1.5"/>'
            + f'<text x="{qlx:.1f}" y="{qly:.1f}" font-size="13" fill="#a13544" '
              f'text-anchor="middle" font-weight="bold">?</text>'
        )
    svg += (
        f'<circle cx="{ax}" cy="{ay}" r="3.5" fill="#333"/>'
        f'<text x="{ax-11}" y="{ay+5}" font-size="12" fill="#333" font-weight="bold">{label_a}</text>'
        f'<circle cx="{bx}" cy="{by}" r="3.5" fill="#a13544"/>'
        f'<text x="{bx+8:.1f}" y="{by+5:.1f}" font-size="12" fill="#a13544" font-weight="bold">{label_b}</text>'
        '</svg>'
    )
    return svg


def _right_triangle_svg(brg, d, comp_label="d"):
    """
    Right-triangle diagram for trig bearing problems.
    Shows the bearing line, North direction, East and North components.
    """
    cx, cy = 72, 118
    leg_scale = min(90 / d, 1.5) * 76 if d > 0 else 76
    rx = round(cx + leg_scale * math.sin(math.radians(brg)), 1)
    ry = round(cy - leg_scale * math.cos(math.radians(brg)), 1)
    east = _E(leg_scale, brg)
    north = _N_comp(leg_scale, brg)
    ex = round(cx + east, 1)
    ey = round(cy - north, 1)
    ra = 8
    n_len = _BRG_N_LEN
    bounds_x = [cx, rx, ex, cx - 24, (cx + ex) // 2]
    bounds_y = [cy, ry, ey, (cy + ey) // 2, cy - n_len - 8]
    svg_open = _brg_svg_fitted(bounds_x, bounds_y)

    return (
        svg_open
        + _north_elements(cx, cy, n_len, font_size=_BRG_N_FONT)
        + f'<line x1="{cx}" y1="{cy}" x2="{rx}" y2="{ry}" stroke="#a13544" stroke-width="{_BRG_ROUTE_STROKE}"/>'
        + f'<line x1="{cx}" y1="{ey}" x2="{ex}" y2="{ey}" stroke="#059669" stroke-width="1.5" stroke-dasharray="4,3"/>'
        + f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{ey}" stroke="#1a6fa8" stroke-width="1.5" stroke-dasharray="4,3"/>'
        + f'<rect x="{cx}" y="{ey-ra}" width="{ra}" height="{ra}" fill="none" stroke="#555" stroke-width="1.2"/>'
        + f'<text x="{(cx+ex)//2}" y="{ey+14}" font-size="{_BRG_LBL_FONT}" fill="#059669" text-anchor="middle" font-weight="bold">East</text>'
        + f'<text x="{cx-24}" y="{(cy+ey)//2}" font-size="{_BRG_LBL_FONT}" fill="#1a6fa8" text-anchor="middle" font-weight="bold">North</text>'
        + f'<text x="{(cx+rx)//2+10}" y="{(cy+ry)//2}" font-size="{_BRG_LBL_FONT}" fill="#a13544" font-weight="bold">{d} km</text>'
        + f'<circle cx="{cx}" cy="{cy}" r="{_BRG_DOT_R}" fill="#333"/>'
        + f'<text x="{cx-11}" y="{cy+5}" font-size="{_BRG_LBL_FONT}" fill="#333" font-weight="bold">A</text>'
        + f'<circle cx="{rx}" cy="{ry}" r="{_BRG_DOT_R}" fill="#a13544"/>'
        + f'<text x="{rx+8}" y="{ry+5}" font-size="{_BRG_LBL_FONT}" fill="#a13544" font-weight="bold">B</text>'
        + '</svg>'
    )


def _port_two_rays_svg(b1, b2, ray1=_BRG_RAY_LEN, ray2=_BRG_RAY_LEN - 2,
                       label_o="O", label_a="A", label_b="B",
                       cx=98, cy=158):
    """Port O with two bearing rays to A and B (arcs labelled at O)."""
    n_len = _BRG_N_LEN
    arc_r1, arc_r2 = _BRG_ARC_R, _BRG_ARC_R + 10
    label_gap = _BRG_ARC_GAP
    pts = []
    bounds_x, bounds_y = [cx], [cy, cy - n_len - 10]
    for brg, ray, lbl in ((b1, ray1, label_a), (b2, ray2, label_b)):
        θ = math.radians(brg)
        px = round(cx + ray * math.sin(θ), 1)
        py = round(cy - ray * math.cos(θ), 1)
        pts.append((brg, px, py, lbl))
        bounds_x.extend([px, px + 11 * math.sin(θ)])
        bounds_y.extend([py, py - 7 * math.cos(θ)])
    for brg, arc_r in ((b1, arc_r1), (b2, arc_r2)):
        lx, ly = _brg_arc_label_xy(cx, cy, brg, arc_r, label_gap)
        bounds_x.append(lx)
        bounds_y.append(ly)
    svg = _brg_svg_fitted(bounds_x, bounds_y) + _north_elements(cx, cy, n_len, font_size=_BRG_N_FONT)
    for brg, px, py, lbl in pts:
        svg += (
            f'<line x1="{cx}" y1="{cy}" x2="{px}" y2="{py}" '
            f'stroke="#a13544" stroke-width="{_BRG_ROUTE_STROKE}"/>'
        )
    for brg, arc_r in ((b1, arc_r1), (b2, arc_r2)):
        arc_path, arc_label = _bearing_arc(
            cx, cy, brg, arc_r, font_size=_BRG_ARC_FONT, label_gap=label_gap,
        )
        svg += arc_path + arc_label
    for brg, px, py, lbl in pts:
        θ = math.radians(brg)
        lx = px + 10 * math.sin(θ)
        ly = py - 7 * math.cos(θ)
        svg += (
            f'<circle cx="{px}" cy="{py}" r="{_BRG_DOT_R}" fill="#a13544"/>'
            f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="{_BRG_LBL_FONT}" fill="#a13544" font-weight="bold">{lbl}</text>'
        )
    svg += (
        f'<circle cx="{cx}" cy="{cy}" r="{_BRG_DOT_R}" fill="#333"/>'
        f'<text x="{cx-11}" y="{cy+5}" font-size="{_BRG_LBL_FONT}" fill="#333" font-weight="bold">{label_o}</text>'
        '</svg>'
    )
    return svg


def _journey_legs_svg(legs, labels=None, max_span=_BRG_JOURNEY_SPAN, cx=54, cy=132):
    """
    Chained journey from O: legs = [(bearing°, distance_km), ...].
    North at start; bearing arc shown at each leg origin.
    """
    if labels is None:
        labels = ["O"] + [chr(ord("A") + i) for i in range(len(legs))]
    total = sum(d for _, d in legs) or 1
    scale = max_span / total
    n_len = _BRG_N_LEN
    arc_r = _BRG_ARC_R
    label_gap = _BRG_ARC_GAP
    points = [(cx, cy)]
    x, y = float(cx), float(cy)
    for brg, dist in legs:
        px = scale * dist
        x += px * math.sin(math.radians(brg))
        y -= px * math.cos(math.radians(brg))
        points.append((round(x, 1), round(y, 1)))
    bounds_x, bounds_y = [], []
    for px, py in points:
        bounds_x.append(px)
        bounds_y.append(py)
    ox, oy = points[0]
    bounds_y.append(oy - n_len - 10)
    for i, (brg, dist) in enumerate(legs):
        vx, vy = points[i]
        lx, ly = _brg_arc_label_xy(vx, vy, brg, arc_r, label_gap)
        bounds_x.append(lx)
        bounds_y.append(ly)
    for (px, py), lbl in zip(points, labels):
        if lbl == labels[0]:
            bounds_x.append(px - 13)
        else:
            bounds_x.append(px + 11)
        bounds_y.append(py + 6)
    svg = _brg_svg_fitted(bounds_x, bounds_y) + _north_elements(cx, cy, n_len, font_size=_BRG_N_FONT)
    ox, oy = cx, cy
    for i, (brg, dist) in enumerate(legs):
        bx, by = points[i + 1]
        svg += (
            f'<line x1="{ox}" y1="{oy}" x2="{bx}" y2="{by}" '
            f'stroke="#a13544" stroke-width="{_BRG_ROUTE_STROKE}"/>'
        )
        arc_path, arc_label = _bearing_arc(
            ox, oy, brg, arc_r, font_size=_BRG_ARC_FONT, label_gap=label_gap,
        )
        svg += arc_path + arc_label
        ox, oy = bx, by
    for (px, py), lbl in zip(points, labels):
        fill = "#333" if lbl == labels[0] else "#a13544"
        lx = px + (11 if lbl != labels[0] else -13)
        ly = py + (6 if lbl != labels[0] else 5)
        svg += (
            f'<circle cx="{px}" cy="{py}" r="{_BRG_DOT_R}" fill="{fill}"/>'
            f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="{_BRG_LBL_FONT}" fill="{fill}" font-weight="bold">{lbl}</text>'
        )
    svg += '</svg>'
    return svg


def _brg_abc_block(*parts):
    """Format sub-questions or solution steps as a), b), c)."""
    return "".join(
        f"<br><strong>{chr(ord('a') + i)})</strong> {text}"
        for i, text in enumerate(parts)
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _brg_found_cardinal():
    pairs = [
        ("North",       0),   ("North-East",  45),
        ("East",       90),   ("South-East",  135),
        ("South",     180),   ("South-West",  225),
        ("West",      270),   ("North-West",  315),
    ]
    name, b = random.choice(pairs)
    svg = _single_brg_svg(b, dest="")
    q = f"Write down the 3-figure bearing of {name}.<br>{svg}"
    s = (f"Bearings are measured <em>clockwise from North</em>.<br>"
         f"<strong>{_brg(b)}</strong>")
    return q, s, "N=000°, E=090°, S=180°, W=270°", 1, _brg_answer(b)


def _brg_found_back_lt_180():
    b = random.randint(20, 179)
    back = b + 180
    svg = _two_pt_svg(b, show_back=True)
    q = (f"The bearing of B from A is {_brg(b)}.<br>"
         f"Find the bearing of A from B.<br>{svg}")
    s = (f"The bearing of B from A = {_brg(b)} &lt; 180°, so add 180°:<br>"
         f"{b} + 180 = {back}<br>"
         f"<strong>{_brg(back)}</strong>")
    return q, s, "If bearing < 180°, add 180°. If bearing ≥ 180°, subtract 180°.", 2, _brg_answer(back)


def _brg_found_back_gt_180():
    b = random.randint(181, 350)
    back = b - 180
    svg = _two_pt_svg(b, show_back=True)
    q = (f"The bearing of B from A is {_brg(b)}.<br>"
         f"Find the bearing of A from B.<br>{svg}")
    s = (f"The bearing of B from A = {_brg(b)} &gt; 180°, so subtract 180°:<br>"
         f"{b} − 180 = {back}<br>"
         f"<strong>{_brg(back)}</strong>")
    return q, s, "If bearing ≥ 180°, subtract 180°. If bearing < 180°, add 180°.", 2, _brg_answer(back)


def _brg_found_compass_NE():
    x = random.randint(5, 85)
    b = x
    q = f"A compass direction is given as N{x}°E. Write this as a 3-figure bearing."
    s = (f"N{x}°E means {x}° clockwise from North toward East.<br>"
         f"<strong>{_brg(b)}</strong>")
    return q, s, "N[x]°E means x° from North toward East = bearing x°", 1, _brg_answer(b)


def _brg_found_compass_SW():
    x = random.randint(5, 85)
    b = 180 + x
    q = f"A compass direction is given as S{x}°W. Write this as a 3-figure bearing."
    s = (f"S{x}°W means {x}° from South toward West.<br>"
         f"South = 180°, then add {x}°:<br>"
         f"<strong>{_brg(b)}</strong>")
    return q, s, "S[x]°W: start at South (180°) and add x°.", 1, _brg_answer(b)


def _brg_found_compass_NW():
    x = random.randint(5, 85)
    b = 360 - x
    q = f"A compass direction is given as N{x}°W. Write this as a 3-figure bearing."
    s = (f"N{x}°W means {x}° from North toward West.<br>"
         f"North = 360°(=000°), going clockwise {360-x}° gives the same direction as going {x}° anticlockwise from North.<br>"
         f"<strong>{_brg(b)}</strong>")
    return q, s, "N[x]°W: bearing = 360° − x°", 1, _brg_answer(b)


def _brg_found_compass_SE():
    x = random.randint(5, 85)
    b = 180 - x
    q = f"A compass direction is given as S{x}°E. Write this as a 3-figure bearing."
    s = (f"S{x}°E means {x}° from South toward East.<br>"
         f"South = 180°. Going {x}° toward East (counterclockwise) = 180° − {x}° = {b}°.<br>"
         f"<strong>{_brg(b)}</strong>")
    return q, s, "S[x]°E: bearing = 180° − x°", 1, _brg_answer(b)


def _brg_found_quadrant():
    b = random.randint(1, 359)
    while b in (90, 180, 270):
        b = random.randint(1, 359)
    if 0 < b < 90:
        quad = "NE (between North and East)"
        quad_key = "ne"
    elif 90 < b < 180:
        quad = "SE (between East and South)"
        quad_key = "se"
    elif 180 < b < 270:
        quad = "SW (between South and West)"
        quad_key = "sw"
    else:
        quad = "NW (between West and North)"
        quad_key = "nw"
    q = f"A bearing of {_brg(b)} lies in which quadrant?"
    s = (f"N=000°, E=090°, S=180°, W=270°.<br>"
         f"{b}° lies between "
         f"{'000° and 090°' if 0 < b < 90 else '090° and 180°' if 90 < b < 180 else '180° and 270°' if 180 < b < 270 else '270° and 360°'}.<br>"
         f"<strong>{quad}</strong>")
    return q, s, "N=000°, E=090°, S=180°, W=270°", 1, _brg_keyword_answer(quad_key)


def _brg_found_angle_between():
    b1 = random.randint(10, 170)
    diff = random.randint(20, 80)
    b2 = b1 + diff
    q = f"Find the angle between the bearings {_brg(b1)} and {_brg(b2)}."
    s = (f"Angle between = larger − smaller<br>"
         f"= {b2}° − {b1}°<br>"
         f"<strong>= {diff}°</strong>")
    return q, s, "Subtract the smaller bearing from the larger.", 1, diff


def _brg_found_alternate_angles():
    b = random.randint(25, 155)
    back = b + 180
    q = (f"The bearing of B from A is {_brg(b)}. "
         f"The North lines at A and B are parallel. "
         f"Using alternate angles, find the bearing of A from B.")
    s = (f"The alternate angle at B (between BA and the South direction at B) equals {b}° "
         f"(alternate angles between parallel North lines).<br>"
         f"Bearing of A from B = 180° + {b}° = {back}°<br>"
         f"<strong>{_brg(back)}</strong>")
    return q, s, "Alternate angles between parallel lines are equal. Then add 180° to the South direction.", 3, _brg_answer(back)


def _brg_found_cointerior():
    b = random.randint(25, 155)
    # Co-interior angle at B = 180° - b (on the same side of the transversal)
    coint = 180 - b
    back = b + 180
    q = (f"The bearing of B from A is {_brg(b)}. "
         f"The North lines at A and B are parallel. "
         f"The co-interior angle at B on the same side as the bearing is x°. "
         f"Find x, and hence find the bearing of A from B.")
    s = (f"Co-interior angles (same side of transversal, between parallel lines) sum to 180°.<br>"
         f"x = 180° − {b}° = {coint}°<br>"
         f"The bearing of A from B = 360° − {coint}° + 180°? No — easier: back bearing = {b}° + 180° = {back}°<br>"
         f"<strong>x = {coint}°; bearing of A from B = {_brg(back)}</strong>")
    return q, s, "Co-interior angles sum to 180°. Back bearing = original ± 180°.", 3, _brg_fields_answer((coint, back), ("Co-interior angle x (°)", "Bearing of A from B"))


def _brg_found_straight_line():
    part = random.randint(30, 80)
    # Bearing goes through 180° line; angle on other side
    b = 180 - part
    remaining = 180 - part  # same value
    q = (f"A point B is on a bearing of {_brg(b)} from A. "
         f"A straight road runs due East–West through A. "
         f"Find the angle between the road (going East) and the direction AB.")
    angle = b   # angle from East = 90° - b if b < 90, else b - 90
    # The angle between East direction (090°) and bearing b:
    angle_from_E = abs(90 - b)
    s = (f"The East direction has bearing 090°.<br>"
         f"Angle between bearing {_brg(b)} and East (090°) = |90° − {b}°| = {angle_from_E}°<br>"
         f"<strong>{angle_from_E}°</strong>")
    return q, s, "The East direction has bearing 090°. Find the difference.", 2, angle_from_E


def _brg_found_reading():
    b = random.choice([35, 50, 65, 80, 100, 115, 130, 145, 215, 235, 250, 305, 320, 335])
    svg = _single_brg_svg(b)
    q = (f"The diagram shows the bearing of B from A.<br>{svg}<br>"
         f"Write down the bearing of B from A as a 3-figure bearing.")
    s = f"Reading from the diagram (clockwise from North):<br><strong>{_brg(b)}</strong>"
    return q, s, "Count degrees clockwise from the North arrow.", 1, _brg_answer(b)


def _brg_found_east_of_south():
    x = random.randint(5, 85)
    b = 180 - x
    q = (f"A direction is described as '{x}° west of South'. "
         f"Write this as a 3-figure bearing.")
    b2 = 180 + x
    # 'x° west of south' → South + x toward West → 180+x
    q = (f"A direction is described as '{x}° west of South'. "
         f"Write this as a 3-figure bearing.")
    s = (f"South = 180°. Moving {x}° toward West (clockwise from South) adds {x}°.<br>"
         f"Bearing = 180° + {x}° = {b2}°<br>"
         f"<strong>{_brg(b2)}</strong>")
    return q, s, "South = 180°. West of South → add the angle beyond 180°.", 1, _brg_answer(b2)


def _brg_found_back_context():
    b = random.randint(30, 160)
    back = b + 180
    town_a = random.choice(["Alton", "Barton", "Clifton", "Dalton"])
    town_b = random.choice(["Eastwick", "Fernhill", "Grange", "Harrow"])
    q = (f"Town {town_b} is on a bearing of {_brg(b)} from town {town_a}. "
         f"A pilot flies directly from {town_b} back to {town_a}. "
         f"What bearing should the pilot fly?")
    s = (f"The return bearing = {b}° + 180° = {back}°<br>"
         f"<strong>{_brg(back)}</strong>")
    return q, s, "Return bearing = original bearing ± 180°.", 2, _brg_answer(back)


def _brg_found_three_cities():
    b1 = random.randint(40, 80)
    b2 = b1 + random.randint(60, 100)
    diff = b2 - b1
    q = (f"From a town P, town Q is on a bearing of {_brg(b1)} and town R is on a bearing of {_brg(b2)}. "
         f"Find the angle QPR between the directions PQ and PR.")
    s = (f"Angle QPR = {b2}° − {b1}° = {diff}°<br>"
         f"<strong>{diff}°</strong>")
    return q, s, "Subtract the two bearings to find the angle between the directions.", 1, diff


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (18 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _brg_inter_east_component():
    b = random.choice([30, 45, 50, 60, 120, 135, 150])
    d = random.randint(20, 80)
    east = round(_E(d, b), 2)
    svg = _right_triangle_svg(b, d)
    q = (f"A ship sails on a bearing of {_brg(b)} for {d} km. "
         f"How far East of its starting point is it? Give your answer to 2 d.p.<br>{svg}")
    s = (f"East component = distance × sin(bearing)<br>"
         f"= {d} × sin({b}°)<br>"
         f"= {d} × {round(math.sin(math.radians(b)), 4)}<br>"
         f"<strong>= {east} km East</strong>")
    return q, s, "East component = d × sin(bearing)", 3, east


def _brg_inter_north_component():
    b = random.choice([20, 30, 40, 50, 60, 70, 80])
    d = random.randint(20, 80)
    north = round(_N_comp(d, b), 2)
    q = (f"A ship sails on a bearing of {_brg(b)} for {d} km. "
         f"How far North of its starting point is it? Give your answer to 2 d.p.")
    s = (f"North component = distance × cos(bearing)<br>"
         f"= {d} × cos({b}°)<br>"
         f"= {d} × {round(math.cos(math.radians(b)), 4)}<br>"
         f"<strong>= {north} km North</strong>")
    return q, s, "North component = d × cos(bearing)", 3, north


def _brg_inter_distance_pythagoras():
    b = 90  # due East makes a clean right triangle
    d_east = random.randint(15, 50)
    d_north = random.randint(15, 50)
    dist = round(math.sqrt(d_east**2 + d_north**2), 2)
    q = (f"A boat travels {d_north} km due North, then {d_east} km due East. "
         f"Find the straight-line distance from the starting point to 2 d.p.")
    s = (f"Using Pythagoras: distance = √(North² + East²)<br>"
         f"= √({d_north}² + {d_east}²)<br>"
         f"= √({d_north**2} + {d_east**2})<br>"
         f"= √{d_north**2 + d_east**2}<br>"
         f"<strong>= {dist} km</strong>")
    return q, s, "Use Pythagoras: d = √(North² + East²)", 3, dist


def _brg_inter_bearing_from_components():
    east = random.randint(10, 60)
    north = random.randint(10, 60)
    b = round(_bearing_from_EN(east, north), 1)
    q = (f"A ship is {north} km North and {east} km East of port. "
         f"Find the bearing of the ship from the port to 1 d.p.")
    s = (f"bearing = arctan(East / North)<br>"
         f"= arctan({east} / {north})<br>"
         f"= arctan({round(east/north, 4)})<br>"
         f"= {round(math.degrees(math.atan(east/north)), 1)}°<br>"
         f"Since East > 0 and North > 0 (NE quadrant), the bearing is in the correct range.<br>"
         f"<strong>{_brg(b)}</strong>")
    return q, s, "bearing = arctan(East ÷ North); check the quadrant.", 3, _brg_answer(b)


def _brg_inter_two_legs_distance():
    b1 = random.randint(20, 80)
    d1 = random.randint(20, 60)
    b2 = random.randint(100, 170)
    d2 = random.randint(20, 60)
    e_total = round(_E(d1, b1) + _E(d2, b2), 2)
    n_total = round(_N_comp(d1, b1) + _N_comp(d2, b2), 2)
    dist = round(math.sqrt(e_total**2 + n_total**2), 2)
    q = (f"A ship travels {d1} km on bearing {_brg(b1)}, then {d2} km on bearing {_brg(b2)}. "
         f"Find the straight-line distance from the starting point to 2 d.p.")
    s = (f"Leg 1: East = {d1} × sin{b1}° = {round(_E(d1,b1),2)} km, "
         f"North = {d1} × cos{b1}° = {round(_N_comp(d1,b1),2)} km<br>"
         f"Leg 2: East = {d2} × sin{b2}° = {round(_E(d2,b2),2)} km, "
         f"North = {d2} × cos{b2}° = {round(_N_comp(d2,b2),2)} km<br>"
         f"Total East = {e_total} km, Total North = {n_total} km<br>"
         f"Distance = √({e_total}² + {n_total}²) = √{round(e_total**2 + n_total**2,2)}<br>"
         f"<strong>= {dist} km</strong>")
    return q, s, "Find East and North components of each leg, add, then use Pythagoras.", 4, dist


def _brg_inter_two_legs_bearing():
    b1 = random.randint(30, 80)
    d1 = random.randint(30, 70)
    b2 = random.randint(100, 160)
    d2 = random.randint(30, 70)
    e_total = _E(d1, b1) + _E(d2, b2)
    n_total = _N_comp(d1, b1) + _N_comp(d2, b2)
    brg = round(_bearing_from_EN(e_total, n_total), 1)
    q = (f"A ship sails {d1} km on bearing {_brg(b1)}, then {d2} km on bearing {_brg(b2)}. "
         f"Find the bearing of the ship from the starting point, to 1 d.p.")
    s = (f"Total East = {d1}sin{b1}° + {d2}sin{b2}° = {round(_E(d1,b1),2)} + {round(_E(d2,b2),2)} = {round(e_total,2)} km<br>"
         f"Total North = {d1}cos{b1}° + {d2}cos{b2}° = {round(_N_comp(d1,b1),2)} + {round(_N_comp(d2,b2),2)} = {round(n_total,2)} km<br>"
         f"Bearing = arctan({round(e_total,2)} / {round(n_total,2)})<br>"
         f"Since East &gt; 0 and North {'&gt; 0 → NE quadrant' if n_total > 0 else '&lt; 0 → SE quadrant'}<br>"
         f"<strong>Bearing ≈ {_brg(brg)}</strong>")
    return q, s, "Total East and North components, then bearing = arctan(E/N) checking quadrant.", 4, _brg_answer(brg)


def _brg_inter_find_angle_in_triangle():
    """Two sides and included bearing angle → find angle using trig."""
    d = random.randint(40, 90)
    b = random.choice([30, 45, 60])
    east = round(_E(d, b), 1)
    q = (f"A ship leaves port on a bearing of {_brg(b)} and travels {d} km. "
         f"How far East of the port is the ship? Give exact answer to 1 d.p.")
    s = (f"East = {d} × sin({b}°) = {d} × {round(math.sin(math.radians(b)),4)}<br>"
         f"<strong>= {east} km</strong>")
    return q, s, f"East = d × sin(bearing)", 2, east


def _brg_inter_find_distance_from_bearing_angle():
    """Given east/north components, find distance (Pythagoras)."""
    east = random.randint(12, 50)
    south = random.randint(12, 50)
    dist = round(math.sqrt(east**2 + south**2), 2)
    b = round(_bearing_from_EN(east, -south), 1)
    q = (f"A ship ends up {east} km East and {south} km South of port. "
         f"Find the bearing of the ship from port (to 1 d.p.) and its distance from port (to 2 d.p.).")
    s = (f"Distance = √({east}² + {south}²) = √{east**2 + south**2} = {dist} km<br>"
         f"Bearing: East > 0, North = −{south} (southward) → SE quadrant<br>"
         f"Angle from South = arctan({east}/{south}) = {round(math.degrees(math.atan(east/south)),1)}°<br>"
         f"Bearing = 180° − {round(math.degrees(math.atan(east/south)),1)}° = {b}°<br>"
         f"<strong>Distance = {dist} km, Bearing = {_brg(b)}</strong>")
    return q, s, "Distance uses Pythagoras. Bearing: identify quadrant from E/N signs.", 4, _brg_fields_answer((dist, int(round(b))), ("Distance (km)", "Bearing"))


def _brg_inter_scale_map():
    scale = random.choice([25000, 50000, 100000])
    map_cm = round(random.uniform(4.0, 12.0), 1)
    real_km = round(map_cm * scale / 100000, 2)
    b = random.randint(20, 340)
    while abs(b - 180) < 20 or abs(b) < 20:
        b = random.randint(20, 340)
    q = (f"On a map with scale 1 : {scale:,}, two towns are {map_cm} cm apart. "
         f"Town B is on a bearing of {_brg(b)} from Town A. "
         f"What is the real distance between the towns in km?")
    s = (f"Real distance = map distance × scale ÷ 100 000<br>"
         f"= {map_cm} × {scale:,} ÷ 100 000<br>"
         f"= {map_cm * scale:,.0f} cm ÷ 100 000<br>"
         f"<strong>= {real_km} km</strong>")
    return q, s, "Real distance = map distance × scale. Convert cm to km (÷ 100 000).", 3, real_km


def _brg_inter_return_bearing_context():
    b = random.randint(40, 140)
    d = random.randint(30, 100)
    back = _back(b)
    q = (f"An aircraft flies from airport A to airport B on a bearing of {_brg(b)} "
         f"for {d} km. It then returns directly to A. "
         f"What bearing must the pilot fly on the return journey?")
    s = (f"Return bearing = {b}° + 180° = {back}°<br>"
         f"<strong>{_brg(back)}</strong>")
    return q, s, "Return bearing = original bearing + 180° (if < 180°).", 2, _brg_answer(back)


def _brg_inter_bearing_from_south():
    # Ship goes SE: easy right-angle triangle, find bearing
    south = random.randint(20, 60)
    east = random.randint(20, 60)
    dist = round(math.sqrt(east**2 + south**2), 2)
    b = round(_bearing_from_EN(east, -south), 1)
    q = (f"A ship travels {south} km South then {east} km East. "
         f"Find the bearing of the ship from its starting point, to 1 d.p.")
    s = (f"Net displacement: {east} km East, {south} km South (= −{south} km North)<br>"
         f"SE quadrant: angle from South = arctan(East/South) = arctan({east}/{south}) = {round(math.degrees(math.atan(east/south)),1)}°<br>"
         f"Bearing = 180° − {round(math.degrees(math.atan(east/south)),1)}° = {b}°<br>"
         f"<strong>Bearing = {_brg(b)}, Distance = {dist} km</strong>")
    return q, s, "Find angle from South using arctan(East/South); bearing = 180° - that angle (SE quadrant).", 4, _brg_fields_answer((int(round(b)), dist), ("Bearing", "Distance (km)"))


def _brg_inter_speed_time():
    b = random.randint(30, 150)
    speed = random.randint(15, 40)
    time_h = random.randint(2, 6)
    d = speed * time_h
    east = round(_E(d, b), 1)
    north = round(_N_comp(d, b), 1)
    q = (f"A ship travels on a bearing of {_brg(b)} at {speed} km/h for {time_h} hours. "
         f"Find how far North and how far East it is from its starting point. "
         f"Give your answers to 1 d.p.")
    s = (f"Distance = speed × time = {speed} × {time_h} = {d} km<br>"
         f"North = {d} × cos({b}°) = <strong>{north} km</strong><br>"
         f"East  = {d} × sin({b}°) = <strong>{east} km</strong>")
    return q, s, "Distance = speed × time, then split into North and East components.", 3, _brg_fields_answer((north, east), ("North (km)", "East (km)"))


def _brg_inter_angle_from_north_line():
    b = random.randint(40, 140)
    # Angle between AB and the North line = b
    # Alternate: angle at B from the North line to BA = back bearing - 180 = b
    back = _back(b)
    q = (f"In the diagram, the bearing of B from A is {_brg(b)}. "
         f"The North lines at A and B are parallel. "
         f"Find the bearing of A from B using the angle facts you know.")
    s = (f"The alternate angle at B (between line BA and the North direction at B) = {b}° "
         f"(alternate angles between parallel North lines and transversal AB).<br>"
         f"This angle is measured from North clockwise to BA... but in the {('NE' if b < 90 else 'SE' if b < 180 else 'SW' if b < 270 else 'NW')} case, "
         f"bearing of A from B = {b}° + 180° = {back}°<br>"
         f"<strong>{_brg(back)}</strong>")
    return q, s, "Use alternate angles: angle at B = bearing of B from A. Then add 180°.", 3, _brg_answer(back)


def _brg_inter_area_from_bearing():
    b = random.choice([30, 45, 60])
    d1 = random.randint(20, 50)
    d2 = random.randint(20, 50)
    area = round(0.5 * d1 * d2 * math.sin(math.radians(b)), 2)
    q = (f"Two ships leave port O. Ship A travels {d1} km on bearing {_brg(b)}, "
         f"and Ship B travels {d2} km on bearing {_brg(0)}. "
         f"Find the area of triangle OAB to 2 d.p.")
    s = (f"The angle at O between OA and OB = {b}° − 0° = {b}°<br>"
         f"Area = ½ × OA × OB × sin(angle at O)<br>"
         f"= ½ × {d1} × {d2} × sin({b}°)<br>"
         f"= ½ × {d1} × {d2} × {round(math.sin(math.radians(b)),4)}<br>"
         f"<strong>= {area} km²</strong>")
    return q, s, "Area of triangle = ½ × a × b × sin(C), where C is the included angle.", 4, area


# ---------- INTERMEDIATE (multi-step, a/b/c, with diagram) ----------

def _brg_inter_single_leg_multipart():
    """One leg from port — East, North, then bearing from components."""
    b = random.choice([35, 50, 60, 120, 135])
    d = random.randint(25, 70)
    east = round(_E(d, b), 2)
    north = round(_N_comp(d, b), 2)
    brg_check = round(_bearing_from_EN(east, north), 1)
    svg = _right_triangle_svg(b, d)
    intro = f"A ship sails from port O on a bearing of {_brg(b)} for {d} km."
    q = intro + "<br>" + svg + _brg_abc_block(
        "Find how far East of O the ship is. Give your answer to 2 d.p.",
        "Find how far North of O the ship is. Give your answer to 2 d.p.",
        "Using your answers to (a) and (b), find the bearing of the ship from O to 1 d.p.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> East = {d} × sin({b}°) = <strong>{east} km</strong><br>"
        rf"<strong>b)</strong> North = {d} × cos({b}°) = <strong>{north} km</strong><br>"
        rf"<strong>c)</strong> Bearing = arctan({east} ÷ {north}) = {round(math.degrees(math.atan(east/north)), 1)}° "
        rf"(check quadrant) → <strong>{_brg(brg_check)}</strong>"
    )
    return q, s, "East = d sin θ, North = d cos θ; then bearing = arctan(East ÷ North) with quadrant check.", 5, _brg_fields_answer((east, north, int(round(brg_check))), ("East (km)", "North (km)", "Bearing"))


def _brg_inter_two_ships_port_multipart():
    """Two ships from port — angle at O, distance AB, bearing of A from B."""
    b1 = random.randint(25, 65)
    b2 = b1 + random.randint(45, 95)
    d1 = random.randint(40, 90)
    d2 = random.randint(40, 90)
    angle = b2 - b1
    AB2 = d1**2 + d2**2 - 2 * d1 * d2 * math.cos(math.radians(angle))
    AB = round(math.sqrt(AB2), 2)
    Ax, Ay = _E(d1, b1), _N_comp(d1, b1)
    Bx, By = _E(d2, b2), _N_comp(d2, b2)
    e_AB = round(Ax - Bx, 2)
    n_AB = round(Ay - By, 2)
    brg_AB = round(_bearing_from_EN(e_AB, n_AB), 1)
    svg = _port_two_rays_svg(b1, b2)
    intro = (
        f"Two ships leave port O at the same time. Ship A sails {d1} km on bearing {_brg(b1)} "
        f"and ship B sails {d2} km on bearing {_brg(b2)}."
    )
    q = intro + "<br>" + svg + _brg_abc_block(
        "Find the angle between the two paths at O.",
        "Find the distance AB to 2 d.p.",
        "Find the bearing of A from B to 1 d.p.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Angle AOB = {b2}° − {b1}° = <strong>{angle}°</strong><br>"
        rf"<strong>b)</strong> Cosine rule: AB² = {d1}² + {d2}² − 2×{d1}×{d2}×cos({angle}°) = {round(AB2, 2)}<br>"
        rf"AB = <strong>{AB} km</strong><br>"
        rf"<strong>c)</strong> A is ({round(Ax,2)} km E, {round(Ay,2)} km N); B is ({round(Bx,2)} km E, {round(By,2)} km N)<br>"
        rf"Displacement A − B: East = {e_AB} km, North = {n_AB} km<br>"
        rf"Bearing of A from B = <strong>{_brg(brg_AB)}</strong>"
    )
    return q, s, "Angle = difference in bearings; cosine rule for AB; bearing from relative East/North.", 5, _brg_fields_answer((angle, AB, int(round(brg_AB))), ("Angle at O (°)", "Distance AB (km)", "Bearing of A from B"))


def _brg_inter_two_leg_voyage_multipart():
    """Two-leg journey — total East, total North, direct distance."""
    b1 = random.randint(25, 70)
    d1 = random.randint(30, 65)
    b2 = random.randint(100, 165)
    d2 = random.randint(30, 65)
    e_total = round(_E(d1, b1) + _E(d2, b2), 2)
    n_total = round(_N_comp(d1, b1) + _N_comp(d2, b2), 2)
    dist = round(math.sqrt(e_total**2 + n_total**2), 2)
    svg = _journey_legs_svg([(b1, d1), (b2, d2)], labels=["O", "B", "C"])
    intro = (
        f"A ship leaves O and sails {d1} km on bearing {_brg(b1)}, "
        f"then {d2} km on bearing {_brg(b2)} to C."
    )
    q = intro + "<br>" + svg + _brg_abc_block(
        "Find the total East displacement from O to C to 2 d.p.",
        "Find the total North displacement from O to C to 2 d.p.",
        "Find the straight-line distance OC to 2 d.p.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> East = {round(_E(d1,b1),2)} + {round(_E(d2,b2),2)} = <strong>{e_total} km</strong><br>"
        rf"<strong>b)</strong> North = {round(_N_comp(d1,b1),2)} + {round(_N_comp(d2,b2),2)} = <strong>{n_total} km</strong><br>"
        rf"<strong>c)</strong> OC = √({e_total}² + {n_total}²) = <strong>{dist} km</strong>"
    )
    return q, s, "Resolve each leg into East and North; add; then Pythagoras for OC.", 5, _brg_fields_answer((e_total, n_total, dist), ("East (km)", "North (km)", "Distance OC (km)"))


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (18 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _brg_diff_cosine_rule_distance():
    b1 = random.randint(20, 80)
    b2 = b1 + random.randint(30, 100)
    d1 = random.randint(40, 100)
    d2 = random.randint(40, 100)
    angle = abs(b2 - b1)
    if angle > 180:
        angle = 360 - angle
    AB2 = d1**2 + d2**2 - 2 * d1 * d2 * math.cos(math.radians(angle))
    AB = round(math.sqrt(AB2), 2)
    q = (f"Two ships leave port O simultaneously. Ship A sails {d1} km on bearing {_brg(b1)} "
         f"and Ship B sails {d2} km on bearing {_brg(b2)}. "
         f"Find the distance AB to 2 d.p.")
    s = (f"Angle at O between OA and OB = {b2}° − {b1}° = {angle}°<br>"
         f"Cosine rule: AB² = OA² + OB² − 2·OA·OB·cos(angle at O)<br>"
         f"= {d1}² + {d2}² − 2×{d1}×{d2}×cos({angle}°)<br>"
         f"= {d1**2} + {d2**2} − {2*d1*d2}×{round(math.cos(math.radians(angle)),4)}<br>"
         f"= {round(d1**2+d2**2,2)} − {round(2*d1*d2*math.cos(math.radians(angle)),2)}<br>"
         f"= {round(AB2,2)}<br>"
         f"AB = √{round(AB2,2)}<br>"
         f"<strong>= {AB} km</strong>")
    return q, s, "Find the angle at O between the two paths, then apply the cosine rule.", 5, AB


def _brg_diff_sine_rule_bearing():
    """Find bearing of C from A using sine rule in an oblique triangle."""
    b_AC = random.randint(30, 80)
    d_AB = random.randint(50, 100)
    b_AB = random.randint(20, 60)
    angle_A = b_AC - b_AB  # angle between AB and AC at A
    while angle_A <= 10 or angle_A >= 80:
        b_AC = random.randint(30, 90)
        b_AB = random.randint(10, 50)
        angle_A = b_AC - b_AB
    d_BC = random.randint(30, 70)
    # Use sine rule: BC/sin(A) = AB/sin(C)
    # Find angle B: sin(B)/d_AC = ... this gets complex. Use component method instead.
    e_total = _E(d_AB, b_AB)
    n_total = _N_comp(d_AB, b_AB)
    brg_final = round(_bearing_from_EN(e_total, n_total), 1)
    q = (f"A ship sails from A on bearing {_brg(b_AB)} for {d_AB} km to reach B. "
         f"Find the bearing of B from A and the distance AB.")
    # This is trivially b_AB and d_AB — change to a more interesting problem
    # Multi-leg: A→B→C, find bearing of C from A
    b2 = random.randint(120, 200)
    d2 = random.randint(30, 70)
    e_total2 = _E(d_AB, b_AB) + _E(d2, b2)
    n_total2 = _N_comp(d_AB, b_AB) + _N_comp(d2, b2)
    dist_AC = round(math.sqrt(e_total2**2 + n_total2**2), 2)
    brg_C = round(_bearing_from_EN(e_total2, n_total2), 1)
    q = (f"A ship leaves A and sails {d_AB} km on bearing {_brg(b_AB)} to B, "
         f"then {d2} km on bearing {_brg(b2)} to C. "
         f"Find the bearing of C from A and the distance AC. Give answers to 1 d.p.")
    s = (f"East of B from A = {d_AB}sin{b_AB}° = {round(_E(d_AB,b_AB),2)} km<br>"
         f"North of B from A = {d_AB}cos{b_AB}° = {round(_N_comp(d_AB,b_AB),2)} km<br>"
         f"East of C from B = {d2}sin{b2}° = {round(_E(d2,b2),2)} km<br>"
         f"North of C from B = {d2}cos{b2}° = {round(_N_comp(d2,b2),2)} km<br>"
         f"Total East = {round(e_total2,2)} km, Total North = {round(n_total2,2)} km<br>"
         f"AC = √({round(e_total2,2)}² + {round(n_total2,2)}²) = <strong>{dist_AC} km</strong><br>"
         f"Bearing = arctan({round(e_total2,2)}/{round(n_total2,2)}) → quadrant check<br>"
         f"<strong>Bearing of C from A = {_brg(brg_C)}</strong>")
    return q, s, "Resolve each leg into East/North. Add components. Use arctan for bearing, Pythagoras for distance.", 5, _brg_fields_answer((dist_AC, int(round(brg_C))), ("Distance AC (km)", "Bearing of C from A"))


def _brg_diff_return_to_start():
    b1 = random.randint(30, 80)
    d1 = random.randint(40, 80)
    b2 = b1 + random.randint(60, 120)
    d2 = random.randint(40, 80)
    e_net = _E(d1, b1) + _E(d2, b2)
    n_net = _N_comp(d1, b1) + _N_comp(d2, b2)
    # Return to start: reverse direction
    d_home = round(math.sqrt(e_net**2 + n_net**2), 2)
    brg_home_from_end = round(_bearing_from_EN(-e_net, -n_net), 1)
    q = (f"A yacht sails {d1} km on bearing {_brg(b1)}, then {d2} km on bearing {_brg(b2)}. "
         f"Find the distance and bearing to sail directly back to the start. Give answers to 2 d.p.")
    s = (f"Net East = {round(_E(d1,b1),2)} + {round(_E(d2,b2),2)} = {round(e_net,2)} km<br>"
         f"Net North = {round(_N_comp(d1,b1),2)} + {round(_N_comp(d2,b2),2)} = {round(n_net,2)} km<br>"
         f"To return, displace −{round(e_net,2)} km East and −{round(n_net,2)} km North.<br>"
         f"Return distance = √({round(e_net,2)}² + {round(n_net,2)}²) = <strong>{d_home} km</strong><br>"
         f"Return bearing: E={round(-e_net,2)}, N={round(-n_net,2)} → "
         f"<strong>{_brg(brg_home_from_end)}</strong>")
    return q, s, "Find net E/N displacement. To return: negate both. Distance = Pythagoras, bearing = arctan.", 5, _brg_fields_answer((d_home, int(round(brg_home_from_end))), ("Return distance (km)", "Return bearing"))


def _brg_diff_cosine_find_angle():
    """Given triangle with all three sides, find a bearing using cosine rule."""
    b1 = random.randint(20, 70)
    d_OA = random.randint(50, 100)
    d_OB = random.randint(50, 100)
    angle_O = random.randint(40, 100)
    d_AB = round(math.sqrt(d_OA**2 + d_OB**2 - 2*d_OA*d_OB*math.cos(math.radians(angle_O))), 2)
    b2 = b1 + angle_O
    q = (f"Two ships A and B leave port O at the same time. "
         f"A sails {d_OA} km on bearing {_brg(b1)}, and B sails {d_OB} km on bearing {_brg(b2)}. "
         f"Find the distance AB to 2 d.p. and the angle AOB.")
    s = (f"Angle AOB = {b2}° − {b1}° = {angle_O}°<br>"
         f"Cosine rule: AB² = {d_OA}² + {d_OB}² − 2×{d_OA}×{d_OB}×cos({angle_O}°)<br>"
         f"= {d_OA**2+d_OB**2} − {round(2*d_OA*d_OB*math.cos(math.radians(angle_O)),2)}<br>"
         f"= {round(d_OA**2+d_OB**2-2*d_OA*d_OB*math.cos(math.radians(angle_O)),2)}<br>"
         f"<strong>AB = {d_AB} km, angle AOB = {angle_O}°</strong>")
    return q, s, "Angle at O = difference in bearings. Then cosine rule: c² = a² + b² - 2ab·cos(C).", 5, _brg_fields_answer((d_AB, angle_O), ("Distance AB (km)", "Angle AOB (°)"))


def _brg_diff_find_bearing_of_third_point():
    """A, B known bearings from O; find bearing of A from B."""
    b_OA = random.randint(20, 60)
    d_OA = random.randint(50, 100)
    b_OB = random.randint(100, 160)
    d_OB = random.randint(50, 100)
    # A from B
    Ax = _E(d_OA, b_OA)
    Ay = _N_comp(d_OA, b_OA)
    Bx = _E(d_OB, b_OB)
    By = _N_comp(d_OB, b_OB)
    e_AB = round(Ax - Bx, 2)
    n_AB = round(Ay - By, 2)
    brg_AB = round(_bearing_from_EN(e_AB, n_AB), 1)
    dist_AB = round(math.sqrt(e_AB**2 + n_AB**2), 2)
    q = (f"From port O, ship A sails on bearing {_brg(b_OA)} for {d_OA} km "
         f"and ship B sails on bearing {_brg(b_OB)} for {d_OB} km. "
         f"Find the bearing of A from B and the distance AB. Give answers to 1 d.p.")
    s = (f"Position of A: East = {round(Ax,2)} km, North = {round(Ay,2)} km<br>"
         f"Position of B: East = {round(Bx,2)} km, North = {round(By,2)} km<br>"
         f"Displacement A − B: East = {e_AB} km, North = {n_AB} km<br>"
         f"AB = √({e_AB}² + {n_AB}²) = <strong>{dist_AB} km</strong><br>"
         f"Bearing of A from B = arctan({e_AB}/{n_AB}), quadrant check → <strong>{_brg(brg_AB)}</strong>")
    return q, s, "Find coordinates of A and B. Compute A−B displacement. arctan for bearing, Pythagoras for distance.", 6, _brg_fields_answer((dist_AB, int(round(brg_AB))), ("Distance AB (km)", "Bearing of A from B"))


def _brg_diff_elevation_and_bearing():
    b = random.randint(30, 150)
    horiz = random.randint(300, 900)
    angle_elev = random.randint(10, 40)
    height = round(horiz * math.tan(math.radians(angle_elev)), 1)
    q = (f"From point A, a cliff top C is on a bearing of {_brg(b)} at a horizontal distance of {horiz} m. "
         f"The angle of elevation of C from A is {angle_elev}°. "
         f"Find the height of the cliff to 1 d.p.")
    s = (f"height = horizontal distance × tan(angle of elevation)<br>"
         f"= {horiz} × tan({angle_elev}°)<br>"
         f"= {horiz} × {round(math.tan(math.radians(angle_elev)),4)}<br>"
         f"<strong>= {height} m</strong>")
    return q, s, "height = horizontal distance × tan(angle of elevation). The bearing is not needed here.", 3, height


def _brg_diff_three_legs():
    b1, d1 = random.randint(20,70), random.randint(30,70)
    b2, d2 = b1+random.randint(40,90), random.randint(30,70)
    b3, d3 = b2+random.randint(40,90), random.randint(30,70)
    e = _E(d1,b1)+_E(d2,b2)+_E(d3,b3)
    n = _N_comp(d1,b1)+_N_comp(d2,b2)+_N_comp(d3,b3)
    dist = round(math.sqrt(e**2+n**2), 2)
    brg  = round(_bearing_from_EN(e, n), 1)
    q = (f"A ship leaves port O and sails: {d1} km on bearing {_brg(b1)}, "
         f"then {d2} km on bearing {_brg(b2)}, then {d3} km on bearing {_brg(b3)}. "
         f"Find the bearing and distance from O to the final position. Give answers to 1 d.p.")
    s = (f"E = {round(_E(d1,b1),2)} + {round(_E(d2,b2),2)} + {round(_E(d3,b3),2)} = {round(e,2)} km<br>"
         f"N = {round(_N_comp(d1,b1),2)} + {round(_N_comp(d2,b2),2)} + {round(_N_comp(d3,b3),2)} = {round(n,2)} km<br>"
         f"Distance = √({round(e,2)}² + {round(n,2)}²) = <strong>{dist} km</strong><br>"
         f"<strong>Bearing ≈ {_brg(brg)}</strong>")
    return q, s, "Resolve all three legs into East and North. Sum each. Then Pythagoras + arctan.", 6, _brg_fields_answer((dist, int(round(brg))), ("Distance (km)", "Bearing"))


def _brg_diff_sine_rule_find_distance():
    b1 = random.randint(20, 60)
    d1 = random.randint(50, 100)
    angle_A = random.randint(30, 70)   # angle at A in the triangle
    angle_B = random.randint(20, 60)   # angle at B
    angle_C = 180 - angle_A - angle_B
    while angle_C <= 10:
        angle_A = random.randint(30, 60)
        angle_B = random.randint(20, 50)
        angle_C = 180 - angle_A - angle_B
    # BC/sin(A) = AB/sin(C)
    AB = d1
    BC = round(AB * math.sin(math.radians(angle_A)) / math.sin(math.radians(angle_C)), 2)
    q = (f"In a triangle OAB, OA = {d1} km, angle OAB = {angle_A}°, angle OBA = {angle_B}°. "
         f"Find the length OB to 2 d.p. using the sine rule.")
    s = (f"Angle at O = 180° − {angle_A}° − {angle_B}° = {angle_C}°<br>"
         f"Sine rule: OB/sin(∠OAB) = OA/sin(∠OBA)<br>"
         f"OB = OA × sin({angle_A}°) / sin({angle_B}°)<br>"
         f"= {d1} × {round(math.sin(math.radians(angle_A)),4)} / {round(math.sin(math.radians(angle_B)),4)}<br>"
         f"<strong>= {round(d1*math.sin(math.radians(angle_A))/math.sin(math.radians(angle_B)),2)} km</strong>")
    return q, s, "Sine rule: a/sin(A) = b/sin(B). Identify the correct angle opposite each side.", 5, BC


def _brg_diff_position_from_two_bearings():
    """Two observers with known bearings to a ship — find the ship's position."""
    sep = random.randint(60, 120)   # separation of observers (East)
    b_from_A = random.randint(30, 70)
    b_from_B = random.randint(100, 150)  # B is due East of A
    # Ship position (intersection of two rays):
    # From A(0,0): tan(b_from_A) = E/N  → E = N·tan(b_from_A)
    # From B(sep,0): direction to ship is b_from_B
    #   E - sep = N·tan(b_from_B - 90°) ... complex
    # Use: E = N·tan(b_A) and (E-sep) / N = tan(bearing_from_B adjusted)
    ta = math.tan(math.radians(b_from_A))
    tb = math.tan(math.radians(b_from_B))
    # Ship at (E_s, N_s) from A, so E_s = N_s*ta
    # From B(sep,0): (E_s - sep)/N_s = sin(b_from_B)/cos(b_from_B)... only works if bearing is in right range
    # Simpler: place ship at known position, compute bearings
    N_ship = random.randint(40, 90)
    E_ship_from_A = round(N_ship * ta, 1)
    b_from_B_actual = round(_bearing_from_EN(E_ship_from_A - sep, N_ship), 1)
    q = (f"Observer A and observer B are {sep} km apart, with B due East of A. "
         f"They observe a ship: A sees it on bearing {_brg(b_from_A)} and B sees it on bearing {_brg(b_from_B_actual)}. "
         f"Find the distance from A to the ship, to 1 d.p.")
    dist_AS = round(math.sqrt(E_ship_from_A**2 + N_ship**2), 1)
    s = (f"From A: East = N·tan({b_from_A}°). From B: East − {sep} = N·tan({_brg(b_from_B_actual)} adjusted).<br>"
         f"Ship is {N_ship} km North and {E_ship_from_A} km East of A.<br>"
         f"Distance AS = √({E_ship_from_A}² + {N_ship}²) = √{round(E_ship_from_A**2+N_ship**2,1)}<br>"
         f"<strong>= {dist_AS} km</strong>")
    return q, s, "Resolve each bearing ray into E/N; set E components equal to find N, then compute distance.", 6, dist_AS


def _brg_diff_cosine_reverse():
    """Given all three sides of a triangle, find an angle → deduce bearing."""
    d1 = random.randint(50, 90)
    d2 = random.randint(50, 90)
    b1 = random.randint(20, 60)
    angle_O = random.randint(40, 90)
    b2 = b1 + angle_O
    d_AB = round(math.sqrt(d1**2 + d2**2 - 2*d1*d2*math.cos(math.radians(angle_O))), 2)
    # Now reverse: given d1, d2, d_AB, find angle_O
    cos_O = round((d1**2 + d2**2 - d_AB**2) / (2 * d1 * d2), 4)
    angle_O_check = round(math.degrees(math.acos(cos_O)), 1)
    q = (f"Two ships leave port O. Ship A sails on bearing {_brg(b1)} and is now {d1} km from O. "
         f"Ship B is {d_AB} km from A and {d2} km from O. "
         f"Find the angle AOB at the port, to 1 d.p.")
    s = (f"Cosine rule (to find angle O): cos(O) = (OA² + OB² − AB²) / (2·OA·OB)<br>"
         f"= ({d1}² + {d2}² − {d_AB}²) / (2×{d1}×{d2})<br>"
         f"= ({d1**2} + {d2**2} − {d_AB**2}) / {2*d1*d2}<br>"
         f"= {round(d1**2+d2**2-d_AB**2,2)} / {2*d1*d2}<br>"
         f"= {cos_O}<br>"
         f"angle O = arccos({cos_O})<br>"
         f"<strong>= {angle_O_check}°</strong>")
    return q, s, "Cosine rule: cos(C) = (a²+b²-c²)/(2ab). Identify which angle is opposite which side.", 5, angle_O_check


def _brg_diff_bearing_algebraic():
    a = random.randint(10, 40)
    # Bearing of B from A = (90+a)°. Bearing of A from B = ?
    b = 90 + a
    back = _back(b)
    extra = random.randint(5, 30)
    angle_C = b + extra
    q = (f"The bearing of B from A is (90 + {a})°. "
         f"Another direction C has a bearing (from A) that is {extra}° more than the bearing of B from A. "
         f"(i) Write down the bearing of A from B. "
         f"(ii) Write down the bearing of C from A as a 3-figure bearing.")
    s = (f"(i) Bearing of B from A = 90 + {a} = {b}°<br>"
         f"Back bearing = {b}° + 180° = {back}°<br>"
         f"<strong>{_brg(back)}</strong><br><br>"
         f"(ii) Bearing of C from A = {b}° + {extra}° = {angle_C}°<br>"
         f"<strong>{_brg(angle_C)}</strong>")
    return q, s, "Back bearing = bearing ± 180°. Express each bearing numerically.", 3, _brg_fields_answer((back, angle_C), ("Bearing of A from B", "Bearing of C from A"))


def _brg_diff_prove_bearing():
    b1 = random.randint(20, 50)
    diff = random.randint(90, 130)
    b2 = b1 + diff
    back_b2 = _back(b2)
    angle_from_north_at_B = b2 - 180 if b2 >= 180 else b2 + 180
    q = (f"A ship sails from O to A on bearing {_brg(b1)}, then from A to B on bearing {_brg(b2)}. "
         f"Show that the bearing of A from B is {_brg(back_b2)}.")
    s = (f"The bearing of B from A is {_brg(b2)}.<br>"
         f"The back bearing (bearing of A from B) = {b2}° − 180° = {back_b2}°<br>"
         f"(Since {b2}° &gt; 180°, we subtract 180°.)<br>"
         f"<strong>{_brg(back_b2)} ✓</strong>")
    return q, s, "Back bearing = bearing ± 180°. Show the arithmetic step clearly.", 3


def _brg_diff_complex_polygon_journey():
    legs = [(random.randint(20,60), random.randint(10,80)) for _ in range(4)]
    e_net = sum(_E(d, b) for d, b in legs)
    n_net = sum(_N_comp(d, b) for d, b in legs)
    d_return = round(math.sqrt(e_net**2 + n_net**2), 2)
    brg_return = round(_bearing_from_EN(-e_net, -n_net), 1)
    journey_str = ", ".join(f"{d} km on {_brg(b)}" for d, b in legs)
    q = (f"A ship makes four successive journeys: {journey_str}. "
         f"Find the bearing and distance to return directly to the start, to 2 d.p.")
    e_str = " + ".join(f"{round(_E(d,b),2)}" for d, b in legs)
    n_str = " + ".join(f"{round(_N_comp(d,b),2)}" for d, b in legs)
    s = (f"Total East = {e_str} = {round(e_net,2)} km<br>"
         f"Total North = {n_str} = {round(n_net,2)} km<br>"
         f"Return: East = {round(-e_net,2)} km, North = {round(-n_net,2)} km<br>"
         f"Distance = √({round(e_net,2)}² + {round(n_net,2)}²) = <strong>{d_return} km</strong><br>"
         f"<strong>Bearing = {_brg(brg_return)}</strong>")
    return q, s, "Sum all East and North components. Negate to get return displacement. Pythagoras + arctan.", 6, _brg_fields_answer((d_return, int(round(brg_return))), ("Return distance (km)", "Return bearing"))


def _brg_diff_lighthouse():
    b_from_ship = random.randint(30, 80)
    dist = random.randint(10, 40)
    # Ship is at origin, lighthouse on bearing b_from_ship at distance dist km
    e_L = round(_E(dist, b_from_ship), 2)
    n_L = round(_N_comp(dist, b_from_ship), 2)
    # Closest approach: perpendicular distance from ship's track (due North) to lighthouse
    closest = round(e_L, 2)  # East offset = perpendicular distance if ship travels due North
    q = (f"A lighthouse L is on a bearing of {_brg(b_from_ship)} from ship S, at a distance of {dist} km. "
         f"The ship is travelling due North. Find the shortest distance from the ship's path to the lighthouse, "
         f"to 2 d.p.")
    s = (f"Position of lighthouse relative to ship: East = {dist}×sin({b_from_ship}°) = {e_L} km, "
         f"North = {dist}×cos({b_from_ship}°) = {n_L} km.<br>"
         f"As the ship travels due North, the East offset from the path stays constant.<br>"
         f"Shortest distance = East component = <strong>{closest} km</strong>")
    return q, s, "The shortest distance from the ship's northward track to the lighthouse = the East displacement.", 4, closest


def _brg_diff_speed_meeting():
    b1 = random.randint(20, 80)
    b2 = _back(b1) + random.randint(-20, 20)
    b2 = b2 % 360
    v1 = random.randint(15, 30)
    v2 = random.randint(15, 30)
    sep = random.randint(100, 300)
    # Ships moving toward each other (approximately): closing speed component
    # Simplify: ships on same line, opposite directions
    b1_fixed = random.randint(30, 80)
    b2_fixed = _back(b1_fixed)
    sep2 = random.randint(80, 200)
    time_h = round(sep2 / (v1 + v2), 2)
    q = (f"Ship A and ship B are {sep2} km apart. A is sailing on bearing {_brg(b1_fixed)} at {v1} km/h. "
         f"B is sailing directly toward A on the opposite bearing at {v2} km/h. "
         f"How long until they meet? Give your answer in hours to 2 d.p.")
    s = (f"The ships travel toward each other on the same line.<br>"
         f"Combined speed = {v1} + {v2} = {v1+v2} km/h<br>"
         f"Time = distance ÷ combined speed = {sep2} ÷ {v1+v2}<br>"
         f"<strong>= {time_h} hours</strong>")
    return q, s, "Combined speed = sum of speeds (moving toward each other). Time = distance ÷ speed.", 4, time_h


# ---------- DIFFICULT (multi-step, a/b/c, with diagram) ----------

def _brg_diff_cosine_port_multipart():
    """Two ships from port — angle, AB (cosine), bearing of B from A."""
    b1 = random.randint(20, 55)
    b2 = b1 + random.randint(50, 110)
    d1 = random.randint(50, 100)
    d2 = random.randint(50, 100)
    angle = b2 - b1
    AB2 = d1**2 + d2**2 - 2 * d1 * d2 * math.cos(math.radians(angle))
    AB = round(math.sqrt(AB2), 2)
    Ax, Ay = _E(d1, b1), _N_comp(d1, b1)
    Bx, By = _E(d2, b2), _N_comp(d2, b2)
    e_BA = round(Bx - Ax, 2)
    n_BA = round(By - Ay, 2)
    brg_BA = round(_bearing_from_EN(e_BA, n_BA), 1)
    svg = _port_two_rays_svg(b1, b2)
    intro = (
        f"From port O, ship A is {d1} km away on bearing {_brg(b1)} "
        f"and ship B is {d2} km away on bearing {_brg(b2)}."
    )
    q = intro + "<br>" + svg + _brg_abc_block(
        "Find the angle AOB between the two lines of sight from O.",
        "Find the distance AB to 2 d.p.",
        "Find the bearing of B from A to 1 d.p.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Angle AOB = <strong>{angle}°</strong><br>"
        rf"<strong>b)</strong> AB = √({d1}² + {d2}² − 2×{d1}×{d2}×cos {angle}°) = <strong>{AB} km</strong><br>"
        rf"<strong>c)</strong> B − A: East = {e_BA} km, North = {n_BA} km → "
        rf"<strong>{_brg(brg_BA)}</strong>"
    )
    return q, s, "Angle at O from bearings; cosine rule; displacement B−A then arctan with quadrant.", 6, _brg_fields_answer((angle, AB, int(round(brg_BA))), ("Angle AOB (°)", "Distance AB (km)", "Bearing of B from A"))


def _brg_diff_return_voyage_multipart():
    """Two-leg voyage — net displacement, then return bearing and distance."""
    b1 = random.randint(30, 75)
    d1 = random.randint(40, 80)
    b2 = b1 + random.randint(55, 115)
    d2 = random.randint(40, 80)
    e_net = round(_E(d1, b1) + _E(d2, b2), 2)
    n_net = round(_N_comp(d1, b1) + _N_comp(d2, b2), 2)
    d_home = round(math.sqrt(e_net**2 + n_net**2), 2)
    brg_home = round(_bearing_from_EN(-e_net, -n_net), 1)
    svg = _journey_legs_svg([(b1, d1), (b2, d2)])
    intro = (
        f"A yacht sails {d1} km on bearing {_brg(b1)}, then {d2} km on bearing {_brg(b2)}."
    )
    q = intro + "<br>" + svg + _brg_abc_block(
        "Find the net East displacement from the start to 2 d.p.",
        "Find the net North displacement from the start to 2 d.p.",
        "The yacht returns directly to the start. Find the return distance and bearing to 2 d.p. and 1 d.p. respectively.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Net East = <strong>{e_net} km</strong><br>"
        rf"<strong>b)</strong> Net North = <strong>{n_net} km</strong><br>"
        rf"<strong>c)</strong> Return: East = {round(-e_net,2)} km, North = {round(-n_net,2)} km<br>"
        rf"Distance = <strong>{d_home} km</strong>, bearing = <strong>{_brg(brg_home)}</strong>"
    )
    return q, s, "Sum components for the outbound journey; negate for the return; Pythagoras and arctan.", 6, _brg_fields_answer((e_net, n_net, d_home, int(round(brg_home))), ("Net East (km)", "Net North (km)", "Return distance (km)", "Return bearing"))


def _brg_diff_three_leg_multipart():
    """Three-leg journey — East, North, final bearing and distance."""
    b1 = random.randint(25, 60)
    d1 = random.randint(25, 55)
    b2 = b1 + random.randint(40, 75)
    d2 = random.randint(25, 55)
    b3 = b2 + random.randint(40, 75)
    d3 = random.randint(25, 55)
    e = round(_E(d1, b1) + _E(d2, b2) + _E(d3, b3), 2)
    n = round(_N_comp(d1, b1) + _N_comp(d2, b2) + _N_comp(d3, b3), 2)
    dist = round(math.sqrt(e**2 + n**2), 2)
    brg = round(_bearing_from_EN(e, n), 1)
    svg = _journey_legs_svg([(b1, d1), (b2, d2), (b3, d3)], labels=["O", "P", "Q", "R"])
    intro = (
        f"A ship leaves O and sails: {d1} km on {_brg(b1)}, "
        f"then {d2} km on {_brg(b2)}, then {d3} km on {_brg(b3)} to R."
    )
    q = intro + "<br>" + svg + _brg_abc_block(
        "Find the total East displacement from O to R to 2 d.p.",
        "Find the total North displacement from O to R to 2 d.p.",
        "Find the bearing of R from O and the distance OR. Give bearing to 1 d.p. and distance to 2 d.p.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Total East = <strong>{e} km</strong><br>"
        rf"<strong>b)</strong> Total North = <strong>{n} km</strong><br>"
        rf"<strong>c)</strong> OR = √({e}² + {n}²) = <strong>{dist} km</strong>, "
        rf"bearing = <strong>{_brg(brg)}</strong>"
    )
    return q, s, "Resolve all three legs; sum East and North; Pythagoras and arctan for OR.", 6, _brg_fields_answer((e, n, dist, int(round(brg))), ("East (km)", "North (km)", "Distance OR (km)", "Bearing of R from O"))


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (18 questions)
# ══════════════════════════════════════════════════════════════════════════════

_BRG_MCQ_BANK = [
    {
        "q": "What is the 3-figure bearing of due East?",
        "opts": ["A  090°", "B  180°", "C  270°", "D  000°"],
        "ans": "A", "marks": 1,
        "sol": "East is a quarter-turn clockwise from North. <strong>090°</strong>. Answer: A",
        "hint": "N=000°, E=090°, S=180°, W=270°",
    },
    {
        "q": "The bearing of B from A is 065°. What is the bearing of A from B?",
        "opts": ["A  245°", "B  115°", "C  295°", "D  065°"],
        "ans": "A", "marks": 2,
        "sol": "065° < 180°, so add 180°: 065 + 180 = <strong>245°</strong>. Answer: A",
        "hint": "If bearing < 180°, add 180°.",
    },
    {
        "q": "The bearing of B from A is 230°. What is the bearing of A from B?",
        "opts": ["A  050°", "B  130°", "C  410°", "D  310°"],
        "ans": "A", "marks": 2,
        "sol": "230° > 180°, so subtract 180°: 230 − 180 = <strong>050°</strong>. Answer: A",
        "hint": "If bearing ≥ 180°, subtract 180°.",
    },
    {
        "q": "Which 3-figure bearing represents N45°W?",
        "opts": ["A  315°", "B  045°", "C  225°", "D  135°"],
        "ans": "A", "marks": 1,
        "sol": "N45°W: 45° west of North. Bearing = 360° − 45° = <strong>315°</strong>. Answer: A",
        "hint": "N[x]°W means bearing = 360° − x°.",
    },
    {
        "q": "Which 3-figure bearing represents S30°E?",
        "opts": ["A  150°", "B  120°", "C  210°", "D  030°"],
        "ans": "A", "marks": 1,
        "sol": "S30°E: 30° east of South. Bearing = 180° − 30° = <strong>150°</strong>. Answer: A",
        "hint": "S[x]°E: bearing = 180° − x°.",
    },
    {
        "q": "A bearing of 290° is in which quadrant?",
        "opts": ["A  NW (between West and North)", "B  NE", "C  SW", "D  SE"],
        "ans": "A", "marks": 1,
        "sol": "270° = West, 360° = North. 290° is between them → <strong>NW</strong>. Answer: A",
        "hint": "W=270°, N=360°. Between 270° and 360° = NW.",
    },
    {
        "q": "A ship sails on bearing 060° for 40 km. How far East of the start is it? (to 2 d.p.)",
        "opts": ["A  34.64 km", "B  20.00 km", "C  40.00 km", "D  46.19 km"],
        "ans": "A", "marks": 2,
        "sol": "East = 40 × sin(60°) = 40 × 0.8660 = <strong>34.64 km</strong>. Answer: A",
        "hint": "East = d × sin(bearing).",
    },
    {
        "q": "A ship sails on bearing 030° for 50 km. How far North of the start is it? (to 2 d.p.)",
        "opts": ["A  43.30 km", "B  25.00 km", "C  50.00 km", "D  57.74 km"],
        "ans": "A", "marks": 2,
        "sol": "North = 50 × cos(30°) = 50 × 0.8660 = <strong>43.30 km</strong>. Answer: A",
        "hint": "North = d × cos(bearing).",
    },
    {
        "q": "The angle between bearings 050° and 140° is:",
        "opts": ["A  90°", "B  40°", "C  50°", "D  190°"],
        "ans": "A", "marks": 1,
        "sol": "140° − 050° = <strong>90°</strong>. Answer: A",
        "hint": "Subtract the smaller bearing from the larger.",
    },
    {
        "q": "A ship is 30 km North and 40 km East of port. What is its distance from port?",
        "opts": ["A  50 km", "B  70 km", "C  35 km", "D  25 km"],
        "ans": "A", "marks": 2,
        "sol": "Distance = √(30² + 40²) = √(900 + 1600) = √2500 = <strong>50 km</strong>. Answer: A",
        "hint": "Pythagoras: d = √(North² + East²).",
    },
    {
        "q": "A ship is 30 km North and 30 km East of port. What is its bearing from port?",
        "opts": ["A  045°", "B  135°", "C  315°", "D  225°"],
        "ans": "A", "marks": 2,
        "sol": "Equal East and North → 45° from North. NE quadrant → <strong>045°</strong>. Answer: A",
        "hint": "arctan(East/North). NE quadrant: bearing is between 000° and 090°.",
    },
    {
        "q": "Two ships from port: ship A on 040° for 60 km, ship B on 130° for 60 km. Angle between paths?",
        "opts": ["A  90°", "B  130°", "C  40°", "D  170°"],
        "ans": "A", "marks": 2,
        "sol": "130° − 040° = <strong>90°</strong>. Answer: A",
        "hint": "Angle between paths = difference in bearings.",
    },
    {
        "q": "Two ships leave port: OA = 80 km on 030°, OB = 60 km on 090°. Use the cosine rule to find AB. (to 2 d.p.)",
        "opts": ["A  56.57 km", "B  100.00 km", "C  72.11 km", "D  44.72 km"],
        "ans": "C", "marks": 3,
        "sol": ("Angle at O = 090° − 030° = 60°. "
                "AB² = 80² + 60² − 2×80×60×cos(60°) = 6400 + 3600 − 4800 = 5200. "
                "AB = √5200 ≈ <strong>72.11 km</strong>. Answer: C"),
        "hint": "Angle at O = difference in bearings; cosine rule: c² = a² + b² − 2ab cos C.",
    },
    {
        "q": r"Which formula gives the back bearing (return bearing) for a bearing \(\theta\)?",
        "opts": [r"A  \((\theta + 180°)\mod 360°\)", r"B  \(360° - \theta\)",
                 r"C  \(\theta - 90°\)", r"D  \(180° - \theta\)"],
        "ans": "A", "marks": 1,
        "sol": r"Back bearing = \((\theta + 180°)\mod 360°\). Answer: A",
        "hint": "Add 180° and use mod 360° to keep it in range.",
    },
    {
        "q": "A ship travels 20 km East then 20 km North. What is the bearing of the final position from the start?",
        "opts": ["A  045°", "B  135°", "C  315°", "D  225°"],
        "ans": "A", "marks": 2,
        "sol": "Equal East and North → arctan(20/20) = 45° from North → NE quadrant → <strong>045°</strong>. Answer: A",
        "hint": "bearing = arctan(East ÷ North). NE quadrant (E>0, N>0) → between 000° and 090°.",
    },
    {
        "q": "A ship sails 45 km on bearing 030°, then 60 km on bearing 120°. Find the straight-line distance from the start to the final position (to 2 d.p.).",
        "opts": ["A  75.00 km", "B  105.00 km", "C  62.45 km", "D  88.74 km"],
        "ans": "A", "marks": 3, "difficulty": "difficult",
        "sol": ("Leg 1: East = 45 sin 30° = 22.5 km, North = 45 cos 30° ≈ 38.97 km.<br>"
                "Leg 2: East = 60 sin 120° ≈ 51.96 km, North = 60 cos 120° = −30 km.<br>"
                "Total East ≈ 74.46 km, Total North ≈ 8.97 km.<br>"
                "Distance = √(74.46² + 8.97²) ≈ <strong>75.00 km</strong>. Answer: A"),
        "hint": "Resolve each leg into East and North, add, then use Pythagoras.",
    },
    {
        "q": "After sailing 40 km on bearing 060° then 50 km on bearing 200°, a yacht returns directly to port. What return bearing should it steer (to the nearest degree)?",
        "opts": ["A  327°", "B  147°", "C  033°", "D  213°"],
        "ans": "A", "marks": 3, "difficulty": "difficult",
        "sol": ("Net East ≈ 34.64 − 17.10 ≈ 17.54 km, Net North ≈ 20 − 46.98 ≈ −27.0 km.<br>"
                "To return: East ≈ −17.54 km, North ≈ 27.0 km.<br>"
                "Bearing = arctan(East ÷ North) with quadrant check → <strong>327°</strong>. Answer: A"),
        "hint": "Find net East and North; negate for the return leg; use arctan and check the quadrant.",
    },
    {
        "q": "From port O, ship A is 70 km away on bearing 025° and ship B is 90 km away on bearing 095°. Find AB using the cosine rule (to 2 d.p.).",
        "opts": ["A  98.62 km", "B  160.00 km", "C  72.11 km", "D  110.45 km"],
        "ans": "A", "marks": 3, "difficulty": "difficult",
        "sol": ("Angle AOB = 095° − 025° = 70°.<br>"
                "AB² = 70² + 90² − 2×70×90×cos(70°) ≈ 4900 + 8100 − 3275 = 9725.<br>"
                "AB = √9725 ≈ <strong>98.62 km</strong>. Answer: A"),
        "hint": "Angle at O = difference in bearings; then AB² = OA² + OB² − 2·OA·OB·cos(angle).",
    },
]


def bearings_mcq():
    item = random.choice(_BRG_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_bearings_variants(difficulty, mode='practice'):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _BRG_MCQ_BANK, procedural_mcq_for('bearings'), 'bearings', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _brg_found_cardinal,
            _brg_found_back_lt_180,
            _brg_found_back_gt_180,
            _brg_found_compass_NE,
            _brg_found_compass_SW,
            _brg_found_compass_NW,
            _brg_found_compass_SE,
            _brg_found_quadrant,
            _brg_found_angle_between,
            _brg_found_alternate_angles,
            _brg_found_cointerior,
            _brg_found_straight_line,
            _brg_found_reading,
            _brg_found_east_of_south,
            _brg_found_back_context,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _brg_inter_east_component,
            _brg_inter_north_component,
            _brg_inter_distance_pythagoras,
            _brg_inter_bearing_from_components,
            _brg_inter_two_legs_distance,
            _brg_inter_two_legs_bearing,
            _brg_inter_find_angle_in_triangle,
            _brg_inter_find_distance_from_bearing_angle,
            _brg_inter_scale_map,
            _brg_inter_return_bearing_context,
            _brg_inter_bearing_from_south,
            _brg_inter_speed_time,
            _brg_inter_angle_from_north_line,
            _brg_inter_area_from_bearing,
            _brg_found_three_cities,      # suitable intermediate question
            _brg_inter_single_leg_multipart,
            _brg_inter_two_ships_port_multipart,
            _brg_inter_two_leg_voyage_multipart,
        ]
    elif difficulty == 'difficult':
        pool = [
            _brg_diff_cosine_rule_distance,
            _brg_diff_sine_rule_bearing,
            _brg_diff_return_to_start,
            _brg_diff_cosine_find_angle,
            _brg_diff_find_bearing_of_third_point,
            _brg_diff_elevation_and_bearing,
            _brg_diff_three_legs,
            _brg_diff_sine_rule_find_distance,
            _brg_diff_position_from_two_bearings,
            _brg_diff_cosine_reverse,
            _brg_diff_bearing_algebraic,
            _brg_diff_prove_bearing,
            _brg_diff_complex_polygon_journey,
            _brg_diff_lighthouse,
            _brg_diff_speed_meeting,
            _brg_diff_cosine_port_multipart,
            _brg_diff_return_voyage_multipart,
            _brg_diff_three_leg_multipart,
        ]
    else:  # mixed
        found = random.sample([
            _brg_found_cardinal, _brg_found_back_lt_180, _brg_found_back_gt_180,
            _brg_found_compass_NE, _brg_found_quadrant, _brg_found_alternate_angles,
        ], 4)
        inter = random.sample([
            _brg_inter_east_component, _brg_inter_bearing_from_components,
            _brg_inter_two_legs_distance, _brg_inter_two_legs_bearing,
            _brg_inter_speed_time, _brg_inter_return_bearing_context,
        ], 4)
        diff = random.sample([
            _brg_diff_cosine_rule_distance, _brg_diff_return_to_start,
            _brg_diff_three_legs, _brg_diff_sine_rule_find_distance,
        ], 2)
        return found + inter + diff

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors exactly)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_bearings(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_bearings_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'bearings',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_bearings_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    out = variant()
    return _brg_problem_from_output(out, difficulty)
