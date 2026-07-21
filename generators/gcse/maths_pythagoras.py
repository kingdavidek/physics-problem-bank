"""
GCSE Maths – Pythagoras' Theorem
8 foundational · 8 intermediate · 8 difficult · 10 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Exact-surd variants use answer_type surd (Phase 2.8); proof-style variants stay as 4-tuples.
Final answers wrapped in <strong> tags.
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
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fmt(v):
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return str(v)


def _pick_triple():
    """Return (a, b, c) with a ≤ b and a²+b²=c²."""
    base = random.choice([
        (3, 4, 5), (5, 12, 13), (6, 8, 10), (7, 24, 25),
        (8, 15, 17), (9, 12, 15), (12, 16, 20), (15, 20, 25),
    ])
    k = random.choice([1, 1, 1, 2, 2, 3])
    return tuple(x * k for x in base)


def _pick_non_right_triangle():
    """Return side lengths (a, b, c) that do not form a right triangle."""
    for _ in range(60):
        sides = sorted(random.sample(range(4, 26), 3))
        a, b, c = sides
        if a + b <= c:
            continue
        if a * a + b * b != c * c:
            ordered = list(sides)
            random.shuffle(ordered)
            return tuple(ordered)
    return (5, 12, 14)


def _is_right_triangle(sides):
    a, b, c = sorted(sides)
    return a + b > c and a * a + b * b == c * c


def _triangle_right_check_line(num, sides, is_right):
    a, b, c = sorted(sides)
    lhs = a * a + b * b
    rhs = c * c
    if is_right:
        return (
            f"Triangle {num}: {a}² + {b}² = {lhs} = {c}² ✓ right-angled."
        )
    return (
        f"Triangle {num}: {a}² + {b}² = {lhs} ≠ {rhs} = {c}² ✗ not right-angled."
    )


def _pyth_raw(value):
    return _fmt(value)


def _pyth_join_field_values(values):
    encoded = [str(v) for v in values]
    if any('|' in part for part in encoded):
        return '\x1e'.join(encoded)
    return '|'.join(encoded)


def _pyth_fields_answer(values, labels, field_types=None):
    def _field_val(value):
        if isinstance(value, dict) and value.get('type') == 'keyword':
            return str(value.get('value') or '').strip().lower()
        if isinstance(value, dict) and value.get('type') == 'surd':
            coeff = int(value.get('coeff') or 1)
            radicand = value['radicand']
            return str(radicand) if coeff == 1 else f'{coeff}|{radicand}'
        return _pyth_raw(value)

    payload = {
        'type': 'number_fields',
        'values': tuple(_field_val(value) for value in values),
        'labels': tuple(labels),
    }
    if field_types:
        payload['field_types'] = tuple(field_types)
    return payload


def _pyth_keyword_answer(value):
    return {'type': 'keyword', 'value': str(value).strip().lower()}


def _pyth_surd_answer(radicand, coeff=1):
    """Surd answer k√r (default k=1). Stored as 'coeff|radicand' when coeff != 1."""
    c = int(coeff)
    r = int(radicand)
    if c == 1:
        return {'type': 'surd', 'radicand': r}
    return {'type': 'surd', 'coeff': c, 'radicand': r}


def _pyth_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            if values and len(values) == len(labels):
                extra = {
                    'correct_answer_raw': _pyth_join_field_values(values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_format_hint': 'Enter a number or surd in every field',
                }
                field_types = raw.get('field_types')
                if field_types:
                    extra['answer_field_types'] = list(field_types)
        elif isinstance(raw, dict) and raw.get('type') == 'keyword':
            value = raw.get('value')
            if value is not None and str(value).strip():
                extra = {
                    'correct_answer_raw': str(value).strip().lower(),
                    'answer_type': 'keyword',
                    'answer_format_hint': 'e.g. yes or no',
                }
        elif isinstance(raw, dict) and raw.get('type') == 'surd':
            coeff = int(raw.get('coeff') or 1)
            radicand = raw.get('radicand')
            if radicand is not None:
                extra = {
                    'correct_answer_raw': (
                        str(radicand) if coeff == 1 else f'{coeff}|{radicand}'
                    ),
                    'answer_type': 'surd',
                    'answer_format_hint': 'e.g. √113 — use the √ button if needed',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _pyth_raw(raw),
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
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'pythagoras', **extra
    )


# ── Standard problem-diagram display size ──
_PYTH_SVG_MAX_W = 260
_PYTH_SVG_MAX_H = 200
_PYTH_FIT_PAD = 12


def _pyth_svg_fitted(xs, ys, pad=_PYTH_FIT_PAD):
    """Open <svg> cropped tightly to content with a consistent on-screen footprint."""
    min_x = min(xs) - pad
    max_x = max(xs) + pad
    min_y = min(ys) - pad
    max_y = max(ys) + pad
    vw = max(max_x - min_x, 48)
    vh = max(max_y - min_y, 48)
    return (
        f'<svg width="100%" viewBox="{min_x:.0f} {min_y:.0f} {vw:.0f} {vh:.0f}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'style="background:#f9f8f5;border-radius:6px;'
        f'max-width:{_PYTH_SVG_MAX_W}px;max-height:{_PYTH_SVG_MAX_H}px;'
        f'display:block;margin:8px auto;vertical-align:middle;">'
    )


def _pyth_tri_svg(leg_a, leg_b, hyp, find=None):
    """
    Right triangle, right angle bottom-left.
    find: None | 'a' | 'b' | 'c' — label unknown as '?'
    """
    ax, ay = 55, 155
    bx, by = 185, 155
    cx, cy = 55, 45
    la = "?" if find == "a" else f"{leg_a}"
    lb = "?" if find == "b" else f"{leg_b}"
    lc = "?" if find == "c" else f"{hyp}"
    bounds_x = [ax, bx, cx, 38, 120, 128, 188]
    bounds_y = [ay, by, cy, 88, 102, 172]
    return (
        _pyth_svg_fitted(bounds_x, bounds_y)
        + '<polygon points="55,155 185,155 55,45" fill="#e8f4fd" stroke="none"/>'
        + f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="#1a6fa8" stroke-width="2"/>'
        + f'<line x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke="#059669" stroke-width="2"/>'
        + f'<line x1="{cx}" y1="{cy}" x2="{bx}" y2="{by}" stroke="#a13544" stroke-width="2.5"/>'
        + '<polyline points="64,155 64,146 55,146" fill="none" stroke="#333" stroke-width="1.5"/>'
        + f'<text x="120" y="172" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">{la} cm</text>'
        + f'<text x="38" y="102" font-size="13" fill="#059669" text-anchor="middle" font-weight="bold">{lb} cm</text>'
        + f'<text x="128" y="88" font-size="13" fill="#a13544" text-anchor="middle" font-weight="bold">{lc} cm</text>'
        + '</svg>'
    )


def _rect_diag_svg(w_cm, h_cm, diag, find=None):
    rx, ry, rw, rh = 60, 50, 150, 100
    wl = "?" if find == "w" else f"{w_cm}"
    hl = "?" if find == "h" else f"{h_cm}"
    dl = "?" if find == "d" else f"{diag}"
    bounds_x = [rx, rx + rw, rx - 18, rx + rw // 2 + 12]
    bounds_y = [ry, ry + rh, ry + rh + 22, ry + rh // 2]
    return (
        _pyth_svg_fitted(bounds_x, bounds_y)
        + f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>'
        + f'<line x1="{rx}" y1="{ry}" x2="{rx+rw}" y2="{ry+rh}" stroke="#a13544" stroke-width="2.5" stroke-dasharray="6,3"/>'
        + '<polyline points="68,150 68,141 59,141" fill="none" stroke="#333" stroke-width="1.5"/>'
        + f'<text x="{rx+rw//2}" y="{ry+rh+22}" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">{wl} cm</text>'
        + f'<text x="{rx-18}" y="{ry+rh//2}" font-size="13" fill="#059669" text-anchor="middle" font-weight="bold">{hl} cm</text>'
        + f'<text x="{rx+rw//2+12}" y="{ry+rh//2-8}" font-size="13" fill="#a13544" font-weight="bold">{dl} cm</text>'
        + '</svg>'
    )


def _roof_truss_svg(half_span=60, rise=80, span_m=12, height_m=8):
    """Isosceles roof truss: each half is a right triangle (10 px per metre)."""
    ox, peak_y = 135, 165 - rise
    lx, ly = ox - half_span, 165
    rx, ry = ox + half_span, 165
    bounds_x = [lx, rx, ox, ox - 42, 168]
    bounds_y = [ly, peak_y, ly + 22, 108]
    return (
        _pyth_svg_fitted(bounds_x, bounds_y)
        + f'<line x1="{lx}" y1="{ly}" x2="{rx}" y2="{ry}" stroke="#1a6fa8" stroke-width="2"/>'
        + f'<line x1="{lx}" y1="{ly}" x2="{ox}" y2="{peak_y}" stroke="#a13544" stroke-width="2.5"/>'
        + f'<line x1="{rx}" y1="{ry}" x2="{ox}" y2="{peak_y}" stroke="#a13544" stroke-width="2.5"/>'
        + f'<line x1="{ox}" y1="{peak_y}" x2="{ox}" y2="{ly}" stroke="#059669" stroke-width="1.5" stroke-dasharray="5,3"/>'
        + '<polyline points="144,165 144,156 135,156" fill="none" stroke="#333" stroke-width="1.5"/>'
        + f'<text x="{ox}" y="{ly+22}" font-size="12" fill="#1a6fa8" text-anchor="middle" font-weight="bold">{span_m} m</text>'
        + f'<text x="{ox-42}" y="108" font-size="12" fill="#059669" text-anchor="middle">{height_m} m</text>'
        + f'<text x="168" y="108" font-size="12" fill="#a13544" font-weight="bold">? m</text>'
        + '</svg>'
    )


def _coord_journey_svg(dx=60, dy=80, east_km=None, north_km=None):
    """Right-angled journey on a coordinate grid."""
    ox, oy = 50, 160
    px, py = ox + dx, oy - dy
    east_km = east_km if east_km is not None else dx // 10
    north_km = north_km if north_km is not None else dy // 10
    bounds_x = [ox - 12, px + 50, ox + dx // 2]
    bounds_y = [py - 8, oy + 16, oy - dy // 2]
    return (
        _pyth_svg_fitted(bounds_x, bounds_y)
        + f'<line x1="{ox}" y1="{oy}" x2="{px}" y2="{oy}" stroke="#1a6fa8" stroke-width="2"/>'
        + f'<line x1="{px}" y1="{oy}" x2="{px}" y2="{py}" stroke="#059669" stroke-width="2"/>'
        + f'<line x1="{ox}" y1="{oy}" x2="{px}" y2="{py}" stroke="#a13544" stroke-width="2.5" stroke-dasharray="6,3"/>'
        + f'<circle cx="{ox}" cy="{oy}" r="4" fill="#333"/><circle cx="{px}" cy="{py}" r="4" fill="#333"/>'
        + f'<text x="{ox-12}" y="{oy+16}" font-size="11" fill="#333" font-weight="bold">O</text>'
        + f'<text x="{px+4}" y="{py-4}" font-size="11" fill="#333" font-weight="bold">L</text>'
        + f'<text x="{ox+dx//2}" y="{oy+16}" font-size="11" fill="#1a6fa8" text-anchor="middle">{east_km} km E</text>'
        + f'<text x="{px+14}" y="{oy-dy//2}" font-size="11" fill="#059669">{north_km} km N</text>'
        + '</svg>'
    )


def _ladder_two_position_svg(base1_m, base2_m, height1_m, height2_m, length_m=None):
    """Ladder against wall in two foot positions.

    Labels foot distances only. Wall reach heights are marked '?' so the
    diagram does not give away the answers. Ladder tops sit at different heights.
    """
    # Scale so the larger base / taller height fit the canvas.
    scale = 100 / max(base2_m, height1_m, 1)
    wx, ground = 200, 160
    bx1 = wx - base1_m * scale
    bx2 = wx - base2_m * scale
    ty1 = ground - height1_m * scale
    ty2 = ground - height2_m * scale
    wall_top = min(ty1, ty2) - 12
    bounds_x = [min(bx1, bx2) - 20, wx + 28]
    bounds_y = [wall_top, ground + 16]
    return (
        _pyth_svg_fitted(bounds_x, bounds_y)
        + f'<line x1="{wx}" y1="{wall_top}" x2="{wx}" y2="{ground}" stroke="#555" stroke-width="2"/>'
        + f'<line x1="{min(bx1, bx2) - 16}" y1="{ground}" x2="{wx + 10}" y2="{ground}" stroke="#555" stroke-width="2"/>'
        # First (closer) position — faded
        + f'<line x1="{bx1}" y1="{ground}" x2="{wx}" y2="{ty1}" stroke="#a13544" stroke-width="2.5" opacity="0.45"/>'
        + f'<circle cx="{bx1}" cy="{ground}" r="3" fill="#94a3b8"/>'
        + f'<circle cx="{wx}" cy="{ty1}" r="3" fill="#94a3b8"/>'
        + f'<text x="{wx + 14}" y="{ty1 + 4}" font-size="12" fill="#64748b" font-weight="bold">?</text>'
        # Second (further) position — solid
        + f'<line x1="{bx2}" y1="{ground}" x2="{wx}" y2="{ty2}" stroke="#a13544" stroke-width="2.5"/>'
        + f'<circle cx="{bx2}" cy="{ground}" r="4" fill="#a13544"/>'
        + f'<circle cx="{wx}" cy="{ty2}" r="3.5" fill="#a13544"/>'
        + f'<text x="{wx + 14}" y="{ty2 + 4}" font-size="12" fill="#a13544" font-weight="bold">?</text>'
        # Foot distances only (given in the question)
        + f'<text x="{bx1}" y="{ground + 14}" font-size="11" fill="#666" text-anchor="middle">{base1_m} m</text>'
        + f'<text x="{bx2}" y="{ground + 14}" font-size="11" fill="#a13544" text-anchor="middle">{base2_m} m</text>'
        + '</svg>'
    )


def _cuboid_svg(l, w, h, diag, find=None):
    """Cuboid with space diagonal. find='d' labels the diagonal as '?'."""
    ox, oy = 70, 150
    dx, dy = 90, -55
    dl = "?" if find == "d" else f"{diag}"
    bounds_x = [ox - 12, ox + 80 + dx, ox + 95]
    bounds_y = [oy + 18, oy + dy - 90, oy - 55, oy - 40]
    return (
        _pyth_svg_fitted(bounds_x, bounds_y)
        # front face
        + f'<polygon points="{ox},{oy} {ox+dx},{oy+dy} {ox+dx+80},{oy+dy} {ox+80},{oy}" '
        'fill="#e8f4fd" stroke="#1a6fa8" stroke-width="1.5"/>'
        # top
        + f'<polygon points="{ox},{oy} {ox+80},{oy} {ox+80+dx},{oy+dy} {ox+dx},{oy+dy}" '
        'fill="#dbeafe" stroke="#1a6fa8" stroke-width="1.5"/>'
        # side
        + f'<polygon points="{ox+80},{oy} {ox+80+dx},{oy+dy} {ox+80+dx},{oy+dy-90} {ox+80},{oy-90}" '
        'fill="#bfdbfe" stroke="#1a6fa8" stroke-width="1.5"/>'
        + f'<line x1="{ox}" y1="{oy}" x2="{ox+80+dx}" y2="{oy+dy-90}" stroke="#a13544" stroke-width="2" stroke-dasharray="5,3"/>'
        + f'<text x="{ox+40}" y="{oy+18}" font-size="12" fill="#1a6fa8" text-anchor="middle">{l} cm</text>'
        + f'<text x="{ox+95}" y="{oy-42}" font-size="12" fill="#059669">{w} cm</text>'
        + f'<text x="{ox-12}" y="{oy-40}" font-size="12" fill="#059669">{h} cm</text>'
        + f'<text x="{ox+55}" y="{oy-55}" font-size="12" fill="#a13544" font-weight="bold">{dl} cm</text>'
        + '</svg>'
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (8 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _py_f1_find_hypotenuse():
    a, b, c = _pick_triple()
    svg = _pyth_tri_svg(a, b, c, find="c")
    q = (f"In a right-angled triangle the two shorter sides are {a} cm and {b} cm. "
         f"Find the length of the hypotenuse.<br>{svg}")
    s = (f"a² + b² = c²<br>"
         f"{a}² + {b}² = c² → {a*a} + {b*b} = c² → c² = {c*c}<br>"
         f"c = √{c*c} = <strong>{c} cm</strong>")
    return q, s, "Hypotenuse c is the longest side, opposite the right angle. Use c² = a² + b².", 2, c


def _py_f2_find_shorter_side():
    a, b, c = _pick_triple()
    # Show the known leg; hide the missing leg (not the known one).
    if random.choice([True, False]):
        known, missing, find_lbl = a, b, "b"
    else:
        known, missing, find_lbl = b, a, "a"
    svg = _pyth_tri_svg(a, b, c, find=find_lbl)
    q = (f"A right-angled triangle has hypotenuse {c} cm and one shorter side {known} cm. "
         f"Find the other shorter side.<br>{svg}")
    s = (f"a² + b² = c²<br>"
         f"{missing}² + {known}² = {c}² → {missing}² = {c*c} − {known*known} = {c*c - known*known}<br>"
         f"{missing} = √{c*c - known*known} = <strong>{missing} cm</strong>")
    return q, s, "Rearrange: (shorter side)² = c² − (other shorter side)².", 3, missing


def _py_f3_is_right_yes():
    a, b, c = _pick_triple()
    q = (f"A triangle has sides {a} cm, {b} cm and {c} cm. "
         f"Is it right-angled?")
    s = (f"Check whether a² + b² = c² (with {c} as the longest side):<br>"
         f"{a}² + {b}² = {a*a} + {b*b} = {a*a + b*b}<br>"
         f"{c}² = {c*c}<br>"
         f"Since {a*a + b*b} = {c*c}, the triangle <strong>is right-angled</strong>.")
    return q, s, "Square the longest side and compare with the sum of squares of the other two.", 2, _pyth_keyword_answer('yes')


def _py_f4_is_right_no():
    a, b, _ = _pick_triple()
    c_wrong = random.choice([a + b - 2, a + b, int(math.sqrt(a * a + b * b)) + random.choice([2, 3, 4])])
    while c_wrong <= max(a, b) or a * a + b * b == c_wrong * c_wrong:
        c_wrong += 1
    q = (f"A triangle has sides {a} cm, {b} cm and {c_wrong} cm. Is it right-angled?")
    lhs = a * a + b * b
    rhs = c_wrong * c_wrong
    s = (f"Longest side is {c_wrong} cm. Check a² + b² = c²:<br>"
         f"{a}² + {b}² = {lhs}, but {c_wrong}² = {rhs}<br>"
         f"{lhs} ≠ {rhs}, so the triangle is <strong>not right-angled</strong>.")
    return q, s, "If a² + b² ≠ (longest side)², the triangle is not right-angled.", 2, _pyth_keyword_answer('no')


def _py_f5_ladder_wall():
    combos = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)]
    h, base, lad = random.choice(combos)
    k = random.choice([1, 2])
    h, base, lad = h * k, base * k, lad * k
    svg = _pyth_tri_svg(base, h, lad, find="c")
    q = (f"A ladder reaches {h} m up a wall. Its foot is {base} m from the wall. "
         f"How long is the ladder?<br>{svg}")
    s = (f"Ladder is the hypotenuse:<br>"
         f"{base}² + {h}² = L² → {base*base + h*h} = L²<br>"
         f"L = <strong>{lad} m</strong>")
    return q, s, "Wall and ground are perpendicular — ladder is the hypotenuse.", 2, lad


def _py_f6_rectangle_diagonal():
    w, h = random.choice([(6, 8), (9, 12), (5, 12), (8, 15), (7, 24)])
    d = int(math.sqrt(w * w + h * h))
    svg = _rect_diag_svg(w, h, d, find="d")
    q = (f"A rectangle is {w} cm by {h} cm. Find the length of its diagonal.<br>{svg}")
    s = (f"Diagonal is the hypotenuse of a right triangle with legs {w} cm and {h} cm:<br>"
         f"{w}² + {h}² = d² → {w*w + h*h} = d²<br>"
         f"d = <strong>{d} cm</strong>")
    return q, s, "Split the rectangle into two right-angled triangles using the diagonal.", 2, d


def _py_f7_distance_on_grid():
    dx, dy = random.choice([(3, 4), (6, 8), (5, 12), (9, 12), (8, 15)])
    d = int(math.sqrt(dx * dx + dy * dy))
    q = (f"Point A is at (0, 0) and point B is at ({dx}, {dy}) on a square grid "
         f"(1 unit = 1 cm). Find the straight-line distance AB.")
    s = (f"Horizontal change = {dx} cm, vertical change = {dy} cm.<br>"
         f"AB² = {dx}² + {dy}² = {dx*dx + dy*dy}<br>"
         f"AB = <strong>{d} cm</strong>")
    return q, s, "Count horizontal and vertical steps — they are the two shorter sides.", 2, d


def _py_f8_square_diagonal():
    s = random.choice([4, 6, 8, 10, 12])
    d2 = 2 * s * s
    d = int(math.sqrt(d2))
    q = (f"A square has side length {s} cm. Find the length of its diagonal."
         f"<br>{_rect_diag_svg(s, s, d, find='d')}")
    sol = (f"Diagonal splits the square into two right isosceles triangles with legs {s} cm:<br>"
           f"{s}² + {s}² = d² → {d2} = d²<br>"
           f"d = √{d2} = <strong>{d} cm</strong>")
    return q, sol, "In a square, the diagonal is the hypotenuse of a right triangle with two equal legs.", 2, d


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (8 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _py_i1_perimeter():
    a, b, c = _pick_triple()
    p = a + b + c
    svg = _pyth_tri_svg(a, b, c)
    q = (f"A right-angled triangle has shorter sides {a} cm and {b} cm. "
         f"Find its perimeter.<br>{svg}")
    s = (f"First find hypotenuse: c² = {a}² + {b}² = {c*c}, so c = {c} cm.<br>"
         f"Perimeter = {a} + {b} + {c} = <strong>{p} cm</strong>")
    return q, s, "Find the missing hypotenuse, then add all three sides.", 3, p


def _py_i2_area_then_side():
    a, b, c = _pick_triple()
    area = a * b // 2
    q = (f"A right-angled triangle has area {area} cm² and one shorter side {a} cm. "
         f"Find the other shorter side and the hypotenuse.")
    s = (f"Area = ½ × a × b → {area} = ½ × {a} × b → b = <strong>{b} cm</strong><br>"
         f"c² = {a}² + {b}² = {c*c} → c = <strong>{c} cm</strong>")
    return q, s, "Use Area = ½ab for a right triangle, then Pythagoras for the hypotenuse.", 4, _pyth_fields_answer(
        (b, c),
        ('Other shorter side (cm)', 'Hypotenuse (cm)'),
    )


def _py_i3_isosceles_height():
    half, h, slant = random.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17)])
    base = half * 2
    q = (f"An isosceles triangle has base {base} cm and equal sides {slant} cm. "
         f"Find the perpendicular height from the apex to the base.")
    s = (f"Height splits the base into two {half} cm segments, forming a right triangle:<br>"
         f"{half}² + h² = {slant}² → h² = {slant*slant} − {half*half} = {slant*slant - half*half}<br>"
         f"h = <strong>{h} cm</strong>")
    return q, s, "The height bisects the base in an isosceles triangle — use Pythagoras on half the triangle.", 3, h


def _py_i4_3d_space_diagonal():
    l, w, h = random.choice([(3, 4, 5), (6, 8, 10), (4, 4, 4)])
    d = int(math.sqrt(l * l + w * w + h * h))
    svg = _cuboid_svg(l, w, h, d, find="d")
    q = (f"A cuboid is {l} cm by {w} cm by {h} cm. Find the length of its space diagonal.<br>{svg}")
    s = (f"Space diagonal AG satisfies AG² = AB² + BC² + CG²<br>"
         f"AG² = {l}² + {w}² + {h}² = {l*l + w*w + h*h}<br>"
         f"AG = <strong>{d} cm</strong>")
    return q, s, "3D Pythagoras: square all three edges, add, then square root.", 3, d


def _py_i5_3d_two_step():
    l, w, h = 6, 8, 10
    face = int(math.sqrt(l * l + w * w))
    space = int(math.sqrt(l * l + w * w + h * h))
    svg = _cuboid_svg(l, w, h, space, find="d")
    q = (f"A cuboid is {l} cm × {w} cm × {h} cm. "
         f"(i) Find the diagonal of the base. (ii) Find the space diagonal.<br>{svg}")
    s = (f"(i) Base diagonal = √({l}² + {w}²) = √{l*l + w*w} = <strong>{face} cm</strong><br>"
         f"(ii) Space diagonal = √({face}² + {h}²) = √{face*face + h*h} = <strong>{space} cm</strong>")
    return q, s, "Find a face diagonal first, then use it with the height as the two legs.", 4, _pyth_fields_answer(
        (face, space),
        ('Base diagonal (cm)', 'Space diagonal (cm)'),
    )


def _py_i6_coordinate_distance():
    x1, y1 = 1, 2
    x2, y2 = random.choice([(4, 6), (7, 11), (10, 14), (13, 5)])
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    d = int(math.sqrt(dx * dx + dy * dy))
    q = (f"Find the distance between A({x1}, {y1}) and B({x2}, {y2}).")
    s = (f"Δx = {dx}, Δy = {dy}<br>"
         f"AB² = {dx}² + {dy}² = {dx*dx + dy*dy}<br>"
         f"AB = <strong>{d}</strong>")
    return q, s, "Difference in x and difference in y are the legs of a right triangle.", 3, d


def _py_i7_ladder_slips():
    lad, base = random.choice([(10, 6), (13, 5), (15, 9), (17, 8)])
    h = int(math.sqrt(lad * lad - base * base))
    new_base = base + random.choice([2, 3, 4])
    if new_base >= lad:
        new_base = base + 2
    new_h = int(math.sqrt(lad * lad - new_base * new_base))
    q = (f"A {lad} m ladder leans against a wall with its foot {base} m away. "
         f"The foot is slid {new_base - base} m further from the wall. How high does the ladder reach now?")
    s = (f"Original height = √({lad}² − {base}²) = {h} m (check).<br>"
         f"New distance from wall = {new_base} m. Height = √({lad}² − {new_base}²)<br>"
         f"= √{lad*lad - new_base*new_base} = <strong>{new_h} m</strong>")
    return q, s, "Ladder length stays fixed — only the horizontal distance changes.", 4, new_h


def _py_i8_cone_slant():
    r, h = random.choice([(3, 4), (5, 12), (6, 8), (8, 15)])
    s = int(math.sqrt(r * r + h * h))
    q = (f"A cone has base radius {r} cm and perpendicular height {h} cm. Find the slant height.")
    s_txt = (f"Radius and height are perpendicular:<br>"
             f"s² = {r}² + {h}² = {r*r + h*h}<br>"
             f"Slant height = <strong>{s} cm</strong>")
    return q, s_txt, "Slant height is the hypotenuse of the triangle formed by radius and height.", 3, s


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _py_d1_composite_area():
    a, b, c = 6, 8, 10
    tri_area = a * b // 2
    rect_area = a * c
    total = tri_area + rect_area
    q = (f"A shape is made from a rectangle {a} cm by {c} cm with a right-angled triangle "
         f"(legs {a} cm and {b} cm) removed from one corner. Find the area of the shape.")
    s = (f"Rectangle area = {a} × {c} = {rect_area} cm²<br>"
         f"Triangle removed = ½ × {a} × {b} = {tri_area} cm²<br>"
         f"Shaded area = {rect_area} − {tri_area} = <strong>{total} cm²</strong>")
    return q, s, "Subtract the right triangle area from the rectangle area.", 4, total


def _py_d2_distance_formula():
    x1, y1 = random.randint(-4, 2), random.randint(-3, 3)
    dx = random.choice([5, 6, 8, 9, 12])
    dy = random.choice([4, 5, 7, 8, 12, 15])
    x2, y2 = x1 + dx, y1 + dy
    sum_sq = dx * dx + dy * dy
    d = int(math.sqrt(sum_sq))
    q = (f"Find the exact distance between P({x1}, {y1}) and Q({x2}, {y2}). "
         f"Give your answer in surd form if needed.")
    s = (f"Δx = {x2} − ({x1}) = {dx}, Δy = {y2} − ({y1}) = {dy}<br>"
         f"PQ = √({dx}² + {dy}²) = √{sum_sq}"
         + (f" = <strong>{d}</strong>" if sum_sq == d * d else
            f" = <strong>√{sum_sq}</strong>"))
    hint = "Use PQ² = (Δx)² + (Δy)² — the coordinate form of Pythagoras."
    return q, s, hint, 4, _pyth_surd_answer(sum_sq)


def _py_d3_3d_diagonal_exact():
    edge = random.choice([2, 4, 5, 6])
    sum_sq = 3 * edge * edge
    dec = round(math.sqrt(sum_sq), 1)
    q = (f"A cube has edge length {edge} cm.<br>"
         f"(a) Find the exact length of its space diagonal in surd form.<br>"
         f"(b) Give the decimal length correct to 1 d.p.")
    s = (f"AG² = {edge}² + {edge}² + {edge}² = 3 × {edge}² = {sum_sq}<br>"
         f"(a) AG = √{sum_sq} = <strong>{edge}√3 cm</strong><br>"
         f"(b) ≈ <strong>{dec} cm</strong> (1 d.p.)")
    hint = "In a cube all three edges are equal — add three squares of the edge, then simplify the surd."
    return q, s, hint, 5, _pyth_fields_answer(
        (_pyth_surd_answer(3, edge), dec),
        ('(a) Exact space diagonal', '(b) Decimal length (1 d.p.)'),
        field_types=('surd', 'number'),
    )


def _py_d4_pythagoras_proof_check():
    a, b, c = 9, 12, 15
    q = (f"A student says a triangle with sides {a} cm, {b} cm and {c} cm is right-angled "
         f"because {a}+{b}={c}. Explain the error and decide whether the triangle is right-angled.")
    ok = a * a + b * b == c * c
    s = (f"The student used a + b = c, but Pythagoras requires <strong>a² + b² = c²</strong>, not a + b = c.<br>"
         f"Check: {a}² + {b}² = {a*a + b*b} and {c}² = {c*c}. "
         f"{'They are equal, so the triangle <strong>is</strong> right-angled.' if ok else 'They are not equal.'}")
    return q, s, "Always compare squares of sides, never just the lengths.", 3


def _py_d5_two_triangles():
    scenario = random.choice(['both', '1', '2', 'neither'])
    if scenario == 'both':
        t1 = _pick_triple()
        t2 = _pick_triple()
        while sorted(t1) == sorted(t2):
            t2 = _pick_triple()
    elif scenario == '1':
        t1 = _pick_triple()
        t2 = _pick_non_right_triangle()
    elif scenario == '2':
        t1 = _pick_non_right_triangle()
        t2 = _pick_triple()
    else:
        t1 = _pick_non_right_triangle()
        t2 = _pick_non_right_triangle()
        while sorted(t1) == sorted(t2):
            t2 = _pick_non_right_triangle()

    a, b, c = t1
    x, y, z = t2
    p1 = a + b + c
    p2 = x + y + z
    right1 = _is_right_triangle(t1)
    right2 = _is_right_triangle(t2)

    if scenario == 'both':
        perim = p1
        perim_label = 'Perimeter of triangle 1 (cm)'
        q_suffix = 'Find the perimeter of triangle 1.'
        answer_line = (
            'Both triangles are right-angled, so the first answer is '
            '<strong>both</strong>.'
        )
    elif scenario == '1':
        perim = p1
        perim_label = 'Perimeter of triangle 1 (cm)'
        q_suffix = 'Find the perimeter of triangle 1.'
        answer_line = (
            'Only triangle 1 is right-angled, so the first answer is '
            '<strong>1</strong>.'
        )
    elif scenario == '2':
        perim = p2
        perim_label = 'Perimeter of triangle 2 (cm)'
        q_suffix = 'Find the perimeter of triangle 2.'
        answer_line = (
            'Only triangle 2 is right-angled, so the first answer is '
            '<strong>2</strong>.'
        )
    else:
        perim = p1
        perim_label = 'Perimeter of triangle 1 (cm)'
        q_suffix = 'Find the perimeter of triangle 1.'
        answer_line = (
            'Neither triangle is right-angled, so the first answer is '
            '<strong>neither</strong>.'
        )

    q = (f"Triangle 1 has sides {a} cm, {b} cm, {c} cm. "
         f"Triangle 2 has sides {x} cm, {y} cm, {z} cm. "
         f"Which triangle is right-angled? (Enter 1, 2, both, or neither.) "
         f"{q_suffix}")
    s = (
        f"{_triangle_right_check_line(1, t1, right1)}<br>"
        f"{_triangle_right_check_line(2, t2, right2)}<br>"
        f"{answer_line}<br>"
        f"{perim_label.replace(' (cm)', '')} = "
        f"<strong>{perim} cm</strong> "
        f"(triangle 1 perimeter = {p1} cm, triangle 2 perimeter = {p2} cm)."
    )
    return q, s, "Test a² + b² = c² for each triangle using the longest side as c.", 4, _pyth_fields_answer(
        (_pyth_keyword_answer(scenario), perim),
        ('Which triangle? (1, 2, both, or neither)', perim_label),
        field_types=('keyword', 'number'),
    )


def _py_d6_roof_truss_multi():
    half, rise, rafter = 6, 8, 10
    svg = _roof_truss_svg(half * 10, rise * 10, span_m=half * 2, height_m=rise)
    q = (f"A symmetric roof truss rests on a horizontal beam 12 m long. "
         f"The apex is 8 m above the beam (see diagram).<br>{svg}"
         f"(a) Find the length of one rafter (sloping timber from an end to the apex).<br>"
         f"(b) Find the perpendicular height from the beam to the apex (confirm from the diagram).<br>"
         f"(c) Find the total length of timber in the two rafters and the beam.")
    s = (f"(a) Each half forms a right triangle with legs {half} m (half-span) and {rise} m (height):<br>"
         f"Rafter² = {half}² + {rise}² = {half*half + rise*rise} → rafter = <strong>{rafter} m</strong>.<br>"
         f"(b) The perpendicular height is given as <strong>{rise} m</strong> (the dashed line at the centre).<br>"
         f"(c) Total = 2 × {rafter} + 12 = <strong>{2*rafter + 12} m</strong>.")
    return q, s, "Use Pythagoras on half the truss; the height is one leg, half the span is the other.", 6, _pyth_fields_answer(
        (rafter, rise, 2 * rafter + 12),
        ('(a) Rafter length (m)', '(b) Height (m)', '(c) Total timber (m)'),
    )


def _py_d7_coordinate_journey_multi():
    dx, dy, dist = 6, 8, 10
    svg = _coord_journey_svg(dx * 10, dy * 10, east_km=dx, north_km=dy)
    q = (f"A ship leaves port O and sails 6 km due east, then 8 km due north to lighthouse L.<br>{svg}"
         f"(a) Find the direct distance OL.<br>"
         f"(b) A second ship sails from O to a buoy B that is 8 km east and 6 km north of O. "
         f"Find OB.<br>"
         f"(c) The ship could also sail 6 km east and 8 km north in two straight legs (14 km total). "
         f"How much shorter is the direct route OL?")
    ob = int(math.sqrt(8 * 8 + 6 * 6))
    saving = 6 + 8 - dist
    s = (f"(a) OL² = 6² + 8² = 36 + 64 = 100 → OL = <strong>{dist} km</strong>.<br>"
         f"(b) OB² = 8² + 6² = 64 + 36 = 100 → OB = <strong>{ob} km</strong>.<br>"
         f"(c) Two-leg distance = 6 + 8 = 14 km. Direct route = {dist} km.<br>"
         f"Saving = 14 − {dist} = <strong>{saving} km</strong> (the direct line is shorter).")
    return q, s, "East/north legs are perpendicular; use Pythagoras for the hypotenuse OL.", 6, _pyth_fields_answer(
        (dist, ob, saving),
        ('(a) Direct distance OL (km)', '(b) Distance OB (km)', '(c) Saving (km)'),
    )


def _py_d8_ladder_slip_multi():
    # Same ladder length with two integer foot/height swaps from a Pythagorean triple.
    a, b, c = random.choice([
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29),
    ])
    k = random.choice([1, 1, 2, 2, 3])
    a, b, c = a * k, b * k, c * k
    # Start closer to the wall (taller reach), then slide further out.
    base1, h1 = min(a, b), max(a, b)
    base2, h2 = max(a, b), min(a, b)
    lad = c
    drop = h1 - h2
    svg = _ladder_two_position_svg(base1, base2, h1, h2, length_m=lad)
    q = (f"A {lad} m ladder leans against a vertical wall. Its foot is {base1} m from the wall "
         f"(see diagram).<br>{svg}"
         f"(a) Find how high the ladder reaches on the wall.<br>"
         f"(b) The foot is slid out to {base2} m from the wall. The ladder length stays {lad} m. "
         f"Find the new height on the wall.<br>"
         f"(c) By how many metres does the top of the ladder move down?")
    s = (f"(a) h² = {lad}² − {base1}² = {lad*lad - base1*base1} → h = <strong>{h1} m</strong>.<br>"
         f"(b) New height = √({lad}² − {base2}²) = √{lad*lad - base2*base2} = <strong>{h2} m</strong>.<br>"
         f"(c) Drop = {h1} − {h2} = <strong>{drop} m</strong>.")
    return q, s, "The ladder is the hypotenuse; wall height and ground distance are the legs.", 6, _pyth_fields_answer(
        (h1, h2, drop),
        ('(a) First height (m)', '(b) New height (m)', '(c) Drop (m)'),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (10 questions)
# ══════════════════════════════════════════════════════════════════════════════

_PY_MCQ_BANK = [
    {"q": "In a right-angled triangle, which side is the hypotenuse?",
     "opts": ["A  The side opposite the right angle",
              "B  The shortest side",
              "C  The side next to the right angle only",
              "D  Any side you choose"],
     "ans": "A", "marks": 1,
     "sol": "The hypotenuse is opposite the right angle and is always the <strong>longest</strong> side. Answer: A",
     "hint": "Hypotenuse = longest side, opposite the 90° angle."},

    {"q": "A right triangle has shorter sides 6 cm and 8 cm. What is the hypotenuse?",
     "opts": ["A  14 cm", "B  10 cm", "C  28 cm", "D  100 cm"],
     "ans": "B", "marks": 1,
     "sol": "c² = 6² + 8² = 36 + 64 = 100 → c = <strong>10 cm</strong>. Answer: B",
     "hint": "Use c² = a² + b²."},

    {"q": "A right triangle has hypotenuse 13 cm and one side 5 cm. What is the other shorter side?",
     "opts": ["A  8 cm", "B  12 cm", "C  18 cm", "D  194 cm"],
     "ans": "B", "marks": 2,
     "sol": "b² = 13² − 5² = 169 − 25 = 144 → b = <strong>12 cm</strong>. Answer: B",
     "hint": "Rearrange: (shorter side)² = c² − a²."},

    {"q": "Which formula is Pythagoras' theorem for legs a, b and hypotenuse c?",
     "opts": ["A  c = a + b", "B  c² = a² + b²", "C  c² = a² − b²", "D  a² = c² + b²"],
     "ans": "B", "marks": 1,
     "sol": "Pythagoras: <strong>c² = a² + b²</strong> where c is the hypotenuse. Answer: B",
     "hint": "Add the squares of the two shorter sides."},

    {"q": "Do sides 7 cm, 24 cm and 25 cm form a right-angled triangle?",
     "opts": ["A  Yes", "B  No", "C  Only if the angle is 45°", "D  Cannot tell"],
     "ans": "A", "marks": 2,
     "sol": "7² + 24² = 49 + 576 = 625 = 25². <strong>Yes</strong>. Answer: A",
     "hint": "Check whether (smaller)² + (middle)² = (largest)²."},

    {"q": "A rectangle is 9 cm by 12 cm. What is the diagonal length?",
     "opts": ["A  21 cm", "B  15 cm", "C  225 cm", "D  10.5 cm"],
     "ans": "B", "marks": 2,
     "sol": "d² = 9² + 12² = 81 + 144 = 225 → d = <strong>15 cm</strong>. Answer: B",
     "hint": "Diagonal of a rectangle — use Pythagoras on width and height."},

    {"q": "A cuboid is 3 cm × 4 cm × 5 cm. What is the space diagonal?",
     "opts": ["A  12 cm", "B  √50 cm only", "C  7 cm", "D  √50 cm ≈ 7.07 cm"],
     "ans": "D", "marks": 2,
     "sol": "AG² = 3²+4²+5² = 50 → AG = √50 = 5√2 ≈ <strong>7.07 cm</strong>. Answer: D",
     "hint": "Space diagonal: √(l² + w² + h²)."},

    {"q": "Which calculation finds the distance from (0,0) to (6,8)?",
     "opts": ["A  6 + 8", "B  √(6 + 8)", "C  √(6² + 8²)", "D  6 × 8"],
     "ans": "C", "marks": 1,
     "sol": "Distance = √((Δx)² + (Δy)²) = √(36+64) = <strong>√(6²+8²)</strong>. Answer: C",
     "hint": "Horizontal and vertical differences are the two legs."},

    {"q": "A 10 m ladder touches a wall 6 m high. How far is the foot from the wall?",
     "opts": ["A  4 m", "B  8 m", "C  16 m", "D  64 m"],
     "ans": "B", "marks": 2,
     "sol": "base² = 10² − 6² = 100 − 36 = 64 → base = <strong>8 m</strong>. Answer: B",
     "hint": "Ladder is the hypotenuse; height and base are the legs."},

    {"q": "A triangle has sides 5 cm, 12 cm and 14 cm. Is it right-angled?",
     "opts": ["A  Yes", "B  No", "C  Yes, because 5+12>14", "D  Yes, because 5×12=60"],
     "ans": "B", "marks": 2,
     "sol": "5²+12² = 169, but 14² = 196. Not equal → <strong>not right-angled</strong>. Answer: B",
     "hint": "Compare sum of squares of the two shorter sides with square of the longest."},
]


def pythagoras_mcq():
    item = random.choice(_PY_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

def gcse_pythagoras_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_bank_with_procedural(
            _PY_MCQ_BANK, procedural_mcq_for('pythagoras'), 'pythagoras', difficulty
        )

    pools = {
        "foundational": [
            _py_f1_find_hypotenuse, _py_f2_find_shorter_side,
            _py_f3_is_right_yes, _py_f4_is_right_no,
            _py_f5_ladder_wall, _py_f6_rectangle_diagonal,
            _py_f7_distance_on_grid, _py_f8_square_diagonal,
        ],
        "intermediate": [
            _py_i1_perimeter, _py_i2_area_then_side,
            _py_i3_isosceles_height, _py_i4_3d_space_diagonal,
            _py_i5_3d_two_step, _py_i6_coordinate_distance,
            _py_i7_ladder_slips, _py_i8_cone_slant,
        ],
        "difficult": [
            _py_d1_composite_area, _py_d2_distance_formula,
            _py_d3_3d_diagonal_exact, _py_d4_pythagoras_proof_check,
            _py_d5_two_triangles,
            _py_d6_roof_truss_multi, _py_d7_coordinate_journey_multi,
            _py_d8_ladder_slip_multi,
        ],
    }
    if difficulty not in pools:
        f = pools["foundational"][:4]
        i = pools["intermediate"][:4]
        d = pools["difficult"][:2]
        return random.sample(f + i + d, len(f + i + d))

    pool = pools[difficulty]
    return select_tier_variants(pool)


def gcse_pythagoras(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_pythagoras_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "maths", "pythagoras",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_pythagoras_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    out = variant()
    return _pyth_problem_from_output(out, difficulty)
