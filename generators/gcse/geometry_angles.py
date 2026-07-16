"""
GCSE Maths – Geometry and Angles
15 foundational · 15 intermediate · 15 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Proof-only variants stay as 4-tuples (no auto-grade).
Final answers are wrapped in <strong> tags.
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


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _polygon_name(n):
    names = {
        3: "triangle", 4: "quadrilateral", 5: "pentagon",
        6: "hexagon", 7: "heptagon", 8: "octagon",
        9: "nonagon", 10: "decagon", 12: "dodecagon",
    }
    return names.get(n, f"{n}-sided polygon")


def _geom_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(str(int(v)) for v in values),
        'labels': tuple(labels),
    }


def _geom_problem_from_output(out, difficulty):
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
                    'answer_format_hint': 'Enter a number in every field (degrees optional)',
                }
        elif isinstance(raw, (int, float)):
            raw_s = str(int(raw)) if float(raw) == int(raw) else str(raw)
            extra = {
                'correct_answer_raw': raw_s,
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
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'geometry_angles', **extra
    )



def _geom_svg(w, h, inner, max_w=300):
    display_h = max(1, round(max_w * h / w))
    return (
        f'<svg class="geom-diagram" viewBox="0 0 {w} {h}" '
        f'width="{max_w}" height="{display_h}" '
        f'style="background:#f9f8f5;border-radius:6px;'
        f'max-width:{max_w}px !important;width:{max_w}px !important;height:auto;'
        f'display:block;margin:6px auto;">'
        f'{inner}</svg>'
    )


def _g_line(x1, y1, x2, y2, color="#444", w=1.8, dash=""):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{w}"{da}/>')


def _g_txt(x, y, text, color="#333", size=12, anchor="middle", bold=False):
    fw = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}"{fw}>{text}</text>')


def _g_dot(x, y, color="#333", r=3):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'


def _g_poly(points, fill="#e8f4fd", stroke="#1a6fa8", w=1.8, opacity=None):
    pts = " ".join(f"{x},{y}" for x, y in points)
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<polygon points="{pts}" fill="{fill}"{op} '
        f'stroke="{stroke}" stroke-width="{w}"/>'
    )


def _g_circle(cx, cy, r, fill="#e8f4fd", stroke="#1a6fa8", w=2):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>'


def _g_arc_label(cx, cy, r, deg1, deg2, label, color="#a13544", size=11):
    """Arc from deg1 to deg2 (SVG degrees: 0=east, positive=clockwise), with mid label."""
    a1, a2 = math.radians(deg1), math.radians(deg2)
    sweep = (deg2 - deg1) % 360
    if sweep == 0:
        sweep = 360
    large = 1 if sweep > 180 else 0
    sx = round(cx + r * math.cos(a1), 1)
    sy = round(cy + r * math.sin(a1), 1)
    ex = round(cx + r * math.cos(a2), 1)
    ey = round(cy + r * math.sin(a2), 1)
    mid = math.radians(deg1 + sweep / 2)
    lx = round(cx + (r + 13) * math.cos(mid), 1)
    ly = round(cy + (r + 13) * math.sin(mid) + 4, 1)
    path = (f'<path d="M{sx},{sy} A{r},{r},0,{large},1,{ex},{ey}" '
            f'fill="none" stroke="{color}" stroke-width="1.5"/>')
    return path + _g_txt(lx, ly, label, color, size)


def _g_right_mark(vx, vy, p1, p2, size=9, color="#059669"):
    p1x, p1y = p1
    p2x, p2y = p2
    d1x, d1y = p1x - vx, p1y - vy
    d1 = math.hypot(d1x, d1y) or 1
    u1x, u1y = d1x / d1, d1y / d1
    d2x, d2y = p2x - vx, p2y - vy
    d2 = math.hypot(d2x, d2y) or 1
    u2x, u2y = d2x / d2, d2y / d2
    x1 = round(vx + size * u1x, 1)
    y1 = round(vy + size * u1y, 1)
    x2 = round(vx + size * u1x + size * u2x, 1)
    y2 = round(vy + size * u1y + size * u2y, 1)
    x3 = round(vx + size * u2x, 1)
    y3 = round(vy + size * u2y, 1)
    return (f'<polyline points="{x1},{y1} {x2},{y2} {x3},{y3}" '
            f'fill="none" stroke="{color}" stroke-width="1.5"/>')


def _g_tick(p, q, color="#a13544"):
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy) or 1
    px, py = -dy / L * 7, dx / L * 7
    return _g_line(mx - px, my - py, mx + px, my + py, color, 1.6)


def _geom_svg_straight_line(known_deg, known_label=None, unknown_label="x"):
    k = max(25, min(155, int(known_deg)))
    known_label = known_label if known_label is not None else f"{known_deg}°"
    # Ray above the line; left wedge = known
    rx = round(140 + 80 * math.cos(math.radians(180 - k)), 1)
    ry = round(80 - 80 * math.sin(math.radians(k)), 1)
    ray_deg = math.degrees(math.atan2(ry - 80, rx - 140)) % 360
    inner = (
        _g_line(20, 80, 260, 80, "#1a6fa8", 2.2)
        + _g_line(140, 80, rx, ry, "#444", 1.8)
        + _g_dot(140, 80)
        + _g_arc_label(140, 80, 28, 180, ray_deg, known_label, "#a13544")
        + _g_arc_label(140, 80, 28, ray_deg, 0, unknown_label, "#059669")
    )
    return _geom_svg(280, 130, inner)


def _geom_svg_around_point(a, b):
    cx, cy = 130, 110
    parts = []
    for deg in (0, a, a + b):
        rad = math.radians(deg)
        parts.append(_g_line(
            cx, cy,
            round(cx + 85 * math.cos(rad), 1),
            round(cy + 85 * math.sin(rad), 1),
            "#444", 1.8,
        ))
    parts.append(_g_dot(cx, cy))
    parts.append(_g_arc_label(cx, cy, 30, 0, a, f"{a}°", "#a13544"))
    parts.append(_g_arc_label(cx, cy, 30, a, a + b, f"{b}°", "#1a6fa8"))
    parts.append(_g_arc_label(cx, cy, 30, a + b, 360, "x", "#059669"))
    return _geom_svg(260, 220, "".join(parts))


def _geom_svg_crossing(known_deg, label_regions=False):
    inner = (
        _g_line(40, 40, 240, 160, "#1a6fa8", 2)
        + _g_line(40, 160, 240, 40, "#1a6fa8", 2)
        + _g_dot(140, 100)
    )
    a_ne = math.degrees(math.atan2(40 - 100, 240 - 140)) % 360
    a_se = math.degrees(math.atan2(160 - 100, 240 - 140)) % 360
    inner += _g_arc_label(140, 100, 26, a_ne, a_se, f"{known_deg}°", "#a13544")
    if label_regions:
        inner += (
            _g_txt(198, 68, "A", "#333", 12, bold=True)
            + _g_txt(198, 142, "B", "#333", 12, bold=True)
            + _g_txt(78, 68, "C", "#333", 12, bold=True)
            + _g_txt(78, 142, "D", "#333", 12, bold=True)
        )
    return _geom_svg(280, 200, inner)


def _geom_svg_triangle_angles(lab_a, lab_b, lab_c):
    A, B, C = (140, 30), (40, 160), (240, 160)
    inner = (
        _g_poly([A, B, C])
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(140, 18, "A", "#333", 13, bold=True)
        + _g_txt(28, 175, "B", "#333", 13, bold=True)
        + _g_txt(252, 175, "C", "#333", 13, bold=True)
        + _g_txt(140, 55, lab_a, "#a13544", 12)
        + _g_txt(70, 145, lab_b, "#1a6fa8", 12)
        + _g_txt(200, 145, lab_c, "#059669", 12)
    )
    return _geom_svg(280, 195, inner)


def _geom_svg_isosceles(base_label, apex_label="?"):
    A, B, C = (140, 28), (50, 160), (230, 160)
    inner = (
        _g_poly([A, B, C])
        + _g_tick(A, B) + _g_tick(A, C)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(140, 16, "A", "#333", 13, bold=True)
        + _g_txt(38, 175, "B", "#333", 13, bold=True)
        + _g_txt(242, 175, "C", "#333", 13, bold=True)
        + _g_txt(140, 52, apex_label, "#059669", 12)
        + _g_txt(72, 145, base_label, "#a13544", 12)
        + _g_txt(198, 145, base_label, "#a13544", 12)
    )
    return _geom_svg(280, 195, inner)


def _geom_svg_exterior(a_lbl, b_lbl):
    A, B, C, D = (120, 30), (40, 150), (180, 150), (250, 150)
    inner = (
        _g_poly([A, B, C])
        + _g_line(*C, *D, "#1a6fa8", 2)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C) + _g_dot(*D)
        + _g_txt(120, 18, "A", "#333", 13, bold=True)
        + _g_txt(28, 165, "B", "#333", 13, bold=True)
        + _g_txt(175, 168, "C", "#333", 13, bold=True)
        + _g_txt(255, 165, "D", "#333", 12, bold=True)
        + _g_txt(100, 55, a_lbl, "#a13544", 12)
        + _g_txt(70, 135, b_lbl, "#1a6fa8", 12)
        + _g_txt(212, 135, "x", "#059669", 13, bold=True)
    )
    return _geom_svg(280, 190, inner)


def _geom_svg_quadrilateral(a, b, c):
    pts = [(60, 40), (220, 35), (240, 150), (40, 155)]
    labs = [
        (75, 58, f"{a}°", "#a13544"),
        (200, 55, f"{b}°", "#1a6fa8"),
        (210, 138, f"{c}°", "#1a6fa8"),
        (58, 138, "x", "#059669"),
    ]
    inner = _g_poly(pts)
    for p, (lx, ly, lab, col) in zip(pts, labs):
        inner += _g_dot(*p) + _g_txt(lx, ly, lab, col, 12)
    return _geom_svg(280, 185, inner)


def _geom_svg_parallel_transversal(kind, known_deg):
    inner = (
        _g_line(30, 50, 250, 50, "#1a6fa8", 2.2)
        + _g_line(30, 140, 250, 140, "#1a6fa8", 2.2)
        + _g_txt(258, 54, "ℓ₁", "#1a6fa8", 12, "start", True)
        + _g_txt(258, 144, "ℓ₂", "#1a6fa8", 12, "start", True)
        + _g_line(118, 46, 128, 54, "#1a6fa8", 1.4)
        + _g_line(118, 136, 128, 144, "#1a6fa8", 1.4)
        + _g_line(60, 20, 200, 170, "#444", 2)
    )
    i1, i2 = (88, 50), (172, 140)
    inner += _g_dot(*i1) + _g_dot(*i2)
    # Transversal angle ~47° from horizontal
    if kind == "corresponding":
        inner += (
            _g_arc_label(i1[0], i1[1], 18, 315, 0, f"{known_deg}°", "#a13544")
            + _g_arc_label(i2[0], i2[1], 18, 315, 0, "?", "#059669")
            + _g_txt(145, 185, "corresponding (F)", "#777", 11)
        )
    elif kind == "alternate":
        inner += (
            _g_arc_label(i1[0], i1[1], 18, 0, 45, f"{known_deg}°", "#a13544")
            + _g_arc_label(i2[0], i2[1], 18, 180, 225, "?", "#059669")
            + _g_txt(145, 185, "alternate (Z)", "#777", 11)
        )
    else:
        inner += (
            _g_arc_label(i1[0], i1[1], 18, 0, 45, f"{known_deg}°", "#a13544")
            + _g_arc_label(i2[0], i2[1], 18, 315, 0, "?", "#059669")
            + _g_txt(145, 185, "co-interior (C)", "#777", 11)
        )
    return _geom_svg(300, 200, inner)


def _geom_svg_regular_polygon(n, corner_label=None, caption=None):
    cx, cy, r = 130, 115, 78
    pts = []
    for i in range(n):
        ang = math.radians(-90 + i * 360 / n)
        pts.append((round(cx + r * math.cos(ang), 1), round(cy + r * math.sin(ang), 1)))
    inner = _g_poly(pts)
    for p in pts:
        inner += _g_dot(*p, r=2.5)
    if corner_label:
        p0, p_last = pts[0], pts[-1]
        dx, dy = p0[0] - p_last[0], p0[1] - p_last[1]
        L = math.hypot(dx, dy) or 1
        ext = (round(p0[0] + dx / L * 40, 1), round(p0[1] + dy / L * 40, 1))
        inner += _g_line(*p0, *ext, "#a13544", 1.6, "4 3")
        inner += _g_txt((p0[0] + ext[0]) / 2 + 10, (p0[1] + ext[1]) / 2, corner_label, "#a13544", 11)
    if caption:
        inner += _g_txt(cx, cy + 4, caption, "#777", 11)
    return _geom_svg(260, 230, inner)


def _geom_svg_complementary(known_deg):
    O, Ax, Ay = (50, 160), (200, 160), (50, 40)
    k = max(15, min(75, int(known_deg)))
    rx = round(50 + 110 * math.sin(math.radians(k)), 1)
    ry = round(160 - 110 * math.cos(math.radians(k)), 1)
    ray_deg = math.degrees(math.atan2(ry - 160, rx - 50)) % 360
    inner = (
        _g_line(*O, *Ax, "#1a6fa8", 2.2)
        + _g_line(*O, *Ay, "#1a6fa8", 2.2)
        + _g_line(*O, rx, ry, "#444", 1.8)
        + _g_right_mark(50, 160, Ax, Ay)
        + _g_dot(*O)
        + _g_arc_label(50, 160, 34, 0, ray_deg, f"{known_deg}°", "#a13544")
        + _g_arc_label(50, 160, 26, ray_deg, 270, "x", "#059669")
    )
    return _geom_svg(230, 195, inner)


def _geom_svg_equilateral():
    A, B, C = (140, 30), (45, 165), (235, 165)
    inner = (
        _g_poly([A, B, C])
        + _g_tick(A, B) + _g_tick(A, C) + _g_tick(B, C)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(140, 55, "?", "#059669", 13, bold=True)
        + _g_txt(70, 145, "?", "#059669", 13, bold=True)
        + _g_txt(200, 145, "?", "#059669", 13, bold=True)
    )
    return _geom_svg(280, 195, inner)


def _geom_svg_parallel_triangle(p_lbl, q_lbl):
    """l1 || l2 with triangle ABC, A on l1, B,C on l2."""
    inner = (
        _g_line(20, 45, 260, 45, "#1a6fa8", 2)
        + _g_line(20, 160, 260, 160, "#1a6fa8", 2)
        + _g_line(118, 41, 128, 49, "#1a6fa8", 1.4)
        + _g_line(118, 156, 128, 164, "#1a6fa8", 1.4)
        + _g_txt(265, 49, "ℓ₁", "#1a6fa8", 12, "start", True)
        + _g_txt(265, 164, "ℓ₂", "#1a6fa8", 12, "start", True)
    )
    A, B, C = (130, 45), (60, 160), (210, 160)
    inner += (
        _g_poly([A, B, C], fill="#e8f4fd", stroke="#444", w=1.8, opacity=0.55)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(130, 32, "A", "#333", 13, bold=True)
        + _g_txt(48, 175, "B", "#333", 13, bold=True)
        + _g_txt(220, 175, "C", "#333", 13, bold=True)
        + _g_txt(95, 55, p_lbl, "#a13544", 11)
        + _g_txt(175, 145, q_lbl, "#1a6fa8", 11)
        + _g_txt(125, 95, "?", "#059669", 13, bold=True)
    )
    return _geom_svg(300, 195, inner)


def _geom_svg_circle_centre(circ_lbl, centre_lbl="?"):
    cx, cy, r = 130, 120, 85
    # A, B near top; C at bottom
    A = (round(cx + r * math.cos(math.radians(200)), 1), round(cy + r * math.sin(math.radians(200)), 1))
    B = (round(cx + r * math.cos(math.radians(340)), 1), round(cy + r * math.sin(math.radians(340)), 1))
    C = (round(cx + r * math.cos(math.radians(90)), 1), round(cy + r * math.sin(math.radians(90)), 1))
    O = (cx, cy)
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*O, *A, "#a13544", 1.6)
        + _g_line(*O, *B, "#a13544", 1.6)
        + _g_line(*C, *A, "#444", 1.6)
        + _g_line(*C, *B, "#444", 1.6)
        + _g_dot(*O) + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(cx - 12, cy + 4, "O", "#a13544", 12, bold=True)
        + _g_txt(A[0] - 12, A[1], "A", "#333", 12, bold=True)
        + _g_txt(B[0] + 12, B[1], "B", "#333", 12, bold=True)
        + _g_txt(C[0], C[1] + 16, "C", "#333", 12, bold=True)
        + _g_txt(cx, cy - 28, centre_lbl, "#a13544", 12)
        + _g_txt(C[0], C[1] - 22, circ_lbl, "#059669", 12)
    )
    return _geom_svg(260, 250, inner)


def _geom_svg_semicircle(b_lbl):
    cx, cy, r = 140, 130, 90
    A, B = (cx - r, cy), (cx + r, cy)
    # C on upper semicircle
    C = (round(cx + r * math.cos(math.radians(230)), 1), round(cy + r * math.sin(math.radians(230)), 1))
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*A, *B, "#a13544", 2.2)
        + _g_line(*A, *C, "#444", 1.6)
        + _g_line(*B, *C, "#444", 1.6)
        + _g_right_mark(*C, A, B)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(A[0] - 12, A[1] + 4, "A", "#333", 12, bold=True)
        + _g_txt(B[0] + 12, B[1] + 4, "B", "#333", 12, bold=True)
        + _g_txt(C[0], C[1] - 12, "C", "#333", 12, bold=True)
        + _g_txt((B[0] + C[0]) / 2 + 8, (B[1] + C[1]) / 2, b_lbl, "#a13544", 11)
        + _g_txt((A[0] + C[0]) / 2 - 8, (A[1] + C[1]) / 2, "?", "#059669", 12)
        + _g_txt(C[0], C[1] + 22, "90°", "#059669", 11)
    )
    return _geom_svg(280, 250, inner)


def _geom_svg_same_segment(ang_lbl):
    cx, cy, r = 130, 120, 85
    P = (round(cx + r * math.cos(math.radians(210)), 1), round(cy + r * math.sin(math.radians(210)), 1))
    Q = (round(cx + r * math.cos(math.radians(330)), 1), round(cy + r * math.sin(math.radians(330)), 1))
    R = (round(cx + r * math.cos(math.radians(90)), 1), round(cy + r * math.sin(math.radians(90)), 1))
    S = (round(cx + r * math.cos(math.radians(50)), 1), round(cy + r * math.sin(math.radians(50)), 1))
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*P, *R, "#444", 1.5)
        + _g_line(*Q, *R, "#444", 1.5)
        + _g_line(*P, *S, "#1a6fa8", 1.5)
        + _g_line(*Q, *S, "#1a6fa8", 1.5)
        + _g_line(*P, *Q, "#a13544", 1.5, "4 3")
        + _g_dot(*P) + _g_dot(*Q) + _g_dot(*R) + _g_dot(*S)
        + _g_txt(P[0] - 12, P[1], "P", "#333", 12, bold=True)
        + _g_txt(Q[0] + 12, Q[1], "Q", "#333", 12, bold=True)
        + _g_txt(R[0], R[1] + 16, "R", "#333", 12, bold=True)
        + _g_txt(S[0] + 10, S[1] - 8, "S", "#333", 12, bold=True)
        + _g_txt(R[0], R[1] - 18, ang_lbl, "#a13544", 11)
        + _g_txt(S[0] - 5, S[1] + 20, "?", "#059669", 12)
    )
    return _geom_svg(260, 250, inner)


def _geom_svg_cyclic_quad(a_lbl, b_lbl):
    cx, cy, r = 130, 120, 85
    pts = []
    labels = ["A", "B", "C", "D"]
    angles = [225, 315, 45, 135]
    for ang in angles:
        pts.append((
            round(cx + r * math.cos(math.radians(ang)), 1),
            round(cy + r * math.sin(math.radians(ang)), 1),
        ))
    A, B, C, D = pts
    inner = (
        _g_circle(cx, cy, r)
        + _g_poly(pts, fill="#e8f4fd", stroke="#444", w=1.8, opacity=0.4)
        + "".join(_g_dot(*p) for p in pts)
        + _g_txt(A[0] - 12, A[1], "A", "#333", 12, bold=True)
        + _g_txt(B[0] + 12, B[1], "B", "#333", 12, bold=True)
        + _g_txt(C[0] + 12, C[1], "C", "#333", 12, bold=True)
        + _g_txt(D[0] - 12, D[1], "D", "#333", 12, bold=True)
        + _g_txt((A[0] + B[0] + D[0]) / 3, (A[1] + B[1] + D[1]) / 3, a_lbl, "#a13544", 11)
        + _g_txt((A[0] + B[0] + C[0]) / 3 + 10, (A[1] + B[1] + C[1]) / 3, b_lbl, "#1a6fa8", 11)
        + _g_txt((B[0] + C[0] + D[0]) / 3, (B[1] + C[1] + D[1]) / 3 + 8, "?", "#059669", 12)
    )
    return _geom_svg(260, 250, inner)


def _geom_svg_tangent_radius():
    cx, cy, r = 100, 120, 55
    O = (cx, cy)
    A = (cx + r, cy)  # touch point on right
    T = (cx + r + 70, cy - 55)
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*O, *A, "#a13544", 1.8)
        + _g_line(*A, *T, "#444", 1.8)
        + _g_line(*O, *T, "#1a6fa8", 1.5, "4 3")
        + _g_right_mark(*A, O, T)
        + _g_dot(*O) + _g_dot(*A) + _g_dot(*T)
        + _g_txt(O[0] - 14, O[1] + 4, "O", "#a13544", 12, bold=True)
        + _g_txt(A[0] + 8, A[1] + 16, "A", "#333", 12, bold=True)
        + _g_txt(T[0] + 8, T[1], "T", "#333", 12, bold=True)
        + _g_txt((O[0] + A[0]) / 2, (O[1] + A[1]) / 2 - 10, "r", "#a13544", 11)
        + _g_txt((A[0] + T[0]) / 2 + 8, (A[1] + T[1]) / 2, "?", "#059669", 12)
    )
    return _geom_svg(280, 220, inner)


def _geom_svg_bearing(deg):
    cx, cy = 120, 120
    rad = math.radians(deg - 90)  # 0 bearing = north = up
    qx = round(cx + 70 * math.cos(rad), 1)
    qy = round(cy + 70 * math.sin(rad), 1)
    inner = (
        _g_line(cx, cy - 85, cx, cy + 20, "#999", 1.2, "3 3")
        + _g_txt(cx, cy - 92, "N", "#333", 13, bold=True)
        + _g_line(cx, cy, qx, qy, "#1a6fa8", 2.2)
        + _g_dot(cx, cy) + _g_dot(qx, qy)
        + _g_txt(cx - 14, cy + 4, "P", "#333", 12, bold=True)
        + _g_txt(qx + 12, qy, "Q", "#333", 12, bold=True)
        + _g_arc_label(cx, cy, 32, 270, 270 + deg, f"{deg}°", "#a13544")
    )
    return _geom_svg(240, 230, inner)


def _geom_svg_similar_triangles(ab, bc, pq, ang_b):
    # small ABC left, larger PQR right
    A, B, C = (70, 40), (30, 140), (120, 140)
    scale = 1.35
    P = (200, 25)
    Q = (155, 155)
    R = (270, 155)
    inner = (
        _g_poly([A, B, C])
        + _g_poly([P, Q, R], fill="#fef4e8", stroke="#8a5300")
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_dot(*P) + _g_dot(*Q) + _g_dot(*R)
        + _g_txt(70, 28, "A", "#333", 11, bold=True)
        + _g_txt(20, 155, "B", "#333", 11, bold=True)
        + _g_txt(128, 155, "C", "#333", 11, bold=True)
        + _g_txt(200, 14, "P", "#333", 11, bold=True)
        + _g_txt(145, 170, "Q", "#333", 11, bold=True)
        + _g_txt(278, 170, "R", "#333", 11, bold=True)
        + _g_txt(45, 85, f"{ab}", "#a13544", 11)
        + _g_txt(75, 155, f"{bc}", "#a13544", 11)
        + _g_txt(55, 125, f"{ang_b}°", "#1a6fa8", 11)
        + _g_txt(170, 85, f"{pq}", "#8a5300", 11)
        + _g_txt(215, 170, "?", "#059669", 12)
        + _g_txt(175, 130, "?", "#059669", 12)
    )
    return _geom_svg(300, 190, inner, max_w=320)


def _geom_svg_isos_parallel(base_lbl):
    A, B, C = (140, 25), (40, 165), (240, 165)
    D = (90, 95)
    E = (190, 95)
    inner = (
        _g_poly([A, B, C])
        + _g_line(*D, *E, "#a13544", 2)
        + _g_line(85, 91, 95, 99, "#a13544", 1.3)
        + _g_line(118, 161, 128, 169, "#1a6fa8", 1.3)
        + _g_tick(A, B) + _g_tick(A, C)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C) + _g_dot(*D) + _g_dot(*E)
        + _g_txt(140, 14, "A", "#333", 12, bold=True)
        + _g_txt(28, 178, "B", "#333", 12, bold=True)
        + _g_txt(250, 178, "C", "#333", 12, bold=True)
        + _g_txt(78, 92, "D", "#333", 11, bold=True)
        + _g_txt(200, 92, "E", "#333", 11, bold=True)
        + _g_txt(70, 150, base_lbl, "#a13544", 11)
        + _g_txt(140, 55, "?", "#059669", 12)
        + _g_txt(95, 85, "?", "#059669", 12)
    )
    return _geom_svg(280, 195, inner)


def _geom_svg_kite(a_lbl, b_lbl):
    A, B, C, D = (140, 25), (220, 100), (140, 175), (60, 100)
    inner = (
        _g_poly([A, B, C, D], fill="#e8f4fd", stroke="#1a6fa8", w=2)
        + _g_tick(A, B) + _g_tick(A, D)
        + _g_tick(C, B, "#8a5300") + _g_tick(C, D, "#8a5300")
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C) + _g_dot(*D)
        + _g_txt(140, 14, "A", "#333", 12, bold=True)
        + _g_txt(232, 104, "B", "#333", 12, bold=True)
        + _g_txt(140, 192, "C", "#333", 12, bold=True)
        + _g_txt(48, 104, "D", "#333", 12, bold=True)
        + _g_txt(140, 55, a_lbl, "#a13544", 12)
        + _g_txt(185, 100, b_lbl, "#1a6fa8", 12)
        + _g_txt(140, 155, "?", "#059669", 12)
        + _g_txt(90, 100, "?", "#059669", 12)
    )
    return _geom_svg(280, 210, inner)


def _geom_svg_alternate_segment(alpha_lbl):
    cx, cy, r = 120, 125, 70
    T = (round(cx + r * math.cos(math.radians(200)), 1), round(cy + r * math.sin(math.radians(200)), 1))
    A = (round(cx + r * math.cos(math.radians(320)), 1), round(cy + r * math.sin(math.radians(320)), 1))
    B = (round(cx + r * math.cos(math.radians(60)), 1), round(cy + r * math.sin(math.radians(60)), 1))
    O = (cx, cy)
    # tangent direction perpendicular to radius OT
    tx, ty = T[0] - cx, T[1] - cy
    L = math.hypot(tx, ty) or 1
    px, py = -ty / L, tx / L
    T1 = (round(T[0] + px * 55, 1), round(T[1] + py * 55, 1))
    T2 = (round(T[0] - px * 40, 1), round(T[1] - py * 40, 1))
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*T1, *T2, "#8a5300", 2)
        + _g_line(*T, *A, "#444", 1.6)
        + _g_line(*T, *B, "#1a6fa8", 1.5)
        + _g_line(*A, *B, "#1a6fa8", 1.5)
        + _g_line(*O, *T, "#a13544", 1.4, "3 3")
        + _g_line(*O, *A, "#a13544", 1.4, "3 3")
        + _g_dot(*T) + _g_dot(*A) + _g_dot(*B) + _g_dot(*O)
        + _g_txt(T[0] - 14, T[1] + 4, "T", "#333", 12, bold=True)
        + _g_txt(A[0] + 12, A[1], "A", "#333", 12, bold=True)
        + _g_txt(B[0] + 10, B[1] - 8, "B", "#333", 12, bold=True)
        + _g_txt(O[0] - 12, O[1] + 4, "O", "#a13544", 11, bold=True)
        + _g_txt((T[0] + A[0]) / 2 - 5, (T[1] + A[1]) / 2 - 8, alpha_lbl, "#8a5300", 11)
        + _g_txt((T[0] + B[0]) / 2 + 8, (T[1] + B[1]) / 2, "?", "#059669", 12)
    )
    return _geom_svg(280, 250, inner, max_w=300)


def _geom_svg_two_tangents(p_lbl):
    cx, cy, r = 120, 120, 55
    O = (cx, cy)
    A = (cx - 40, cy - 38)
    # place A,B on circle
    A = (round(cx + r * math.cos(math.radians(220)), 1), round(cy + r * math.sin(math.radians(220)), 1))
    B = (round(cx + r * math.cos(math.radians(320)), 1), round(cy + r * math.sin(math.radians(320)), 1))
    P = (cx, cy + r + 55)
    # better external point below
    P = (cx, 220)
    # recompute tangency-ish visual
    A = (cx - 45, cy + 30)
    B = (cx + 45, cy + 30)
    # project onto circle
    def on_circ(x, y):
        dx, dy = x - cx, y - cy
        L = math.hypot(dx, dy) or 1
        return (round(cx + r * dx / L, 1), round(cy + r * dy / L, 1))
    A, B = on_circ(*A), on_circ(*B)
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*P, *A, "#444", 1.8)
        + _g_line(*P, *B, "#444", 1.8)
        + _g_line(*O, *A, "#a13544", 1.5)
        + _g_line(*O, *B, "#a13544", 1.5)
        + _g_right_mark(*A, O, P)
        + _g_right_mark(*B, O, P)
        + _g_dot(*O) + _g_dot(*A) + _g_dot(*B) + _g_dot(*P)
        + _g_txt(O[0] - 12, O[1], "O", "#a13544", 12, bold=True)
        + _g_txt(A[0] - 14, A[1], "A", "#333", 12, bold=True)
        + _g_txt(B[0] + 14, B[1], "B", "#333", 12, bold=True)
        + _g_txt(P[0], P[1] + 16, "P", "#333", 12, bold=True)
        + _g_txt(P[0], P[1] - 28, p_lbl, "#a13544", 12)
        + _g_txt(cx, cy - r - 12, "?", "#059669", 13, bold=True)
    )
    return _geom_svg(250, 255, inner)


def _geom_svg_multi_circle(centre_lbl):
    return _geom_svg_circle_centre("?", centre_lbl)


def _geom_svg_chord_distance(chord_lbl, d_lbl):
    cx, cy, r = 130, 120, 80
    d = 28
    h = 55
    # horizontal chord below centre
    y = cy + d
    half = 50
    A, B = (cx - half, y), (cx + half, y)
    M = (cx, y)
    O = (cx, cy)
    # edge of circle for radius look
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*A, *B, "#444", 2)
        + _g_line(*O, *M, "#a13544", 1.6)
        + _g_line(*O, *A, "#1a6fa8", 1.4, "4 3")
        + _g_right_mark(*M, O, B)
        + _g_dot(*O) + _g_dot(*A) + _g_dot(*B) + _g_dot(*M)
        + _g_txt(O[0] - 12, O[1] - 4, "O", "#a13544", 12, bold=True)
        + _g_txt(cx + 12, (cy + y) / 2, d_lbl, "#a13544", 11)
        + _g_txt(cx, y + 16, chord_lbl, "#444", 11)
        + _g_txt((O[0] + A[0]) / 2 - 10, (O[1] + A[1]) / 2, "r=?", "#059669", 12)
    )
    return _geom_svg(260, 240, inner)


def _geom_svg_prove_triangle_sum():
    A, B, C = (70, 150), (210, 150), (140, 50)
    # parallel through C
    inner = (
        _g_line(30, 50, 250, 50, "#1a6fa8", 1.8, "4 3")
        + _g_txt(20, 45, "D", "#1a6fa8", 11, bold=True)
        + _g_txt(258, 45, "E", "#1a6fa8", 11, bold=True)
        + _g_poly([A, B, C], fill="#e8f4fd", opacity=0.55)
        + _g_line(100, 46, 110, 54, "#1a6fa8", 1.3)
        + _g_line(100, 146, 110, 154, "#1a6fa8", 1.3)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(70, 168, "A", "#333", 12, bold=True)
        + _g_txt(210, 168, "B", "#333", 12, bold=True)
        + _g_txt(140, 38, "C", "#333", 12, bold=True)
    )
    return _geom_svg(280, 190, inner)


def _geom_svg_tangent_chord(alpha_lbl, beta_lbl):
    cx, cy, r = 130, 120, 70
    T = (round(cx + r * math.cos(math.radians(200)), 1), round(cy + r * math.sin(math.radians(200)), 1))
    P = (round(cx + r * math.cos(math.radians(330)), 1), round(cy + r * math.sin(math.radians(330)), 1))
    B = (round(cx + r * math.cos(math.radians(70)), 1), round(cy + r * math.sin(math.radians(70)), 1))
    tx, ty = T[0] - cx, T[1] - cy
    L = math.hypot(tx, ty) or 1
    px, py = -ty / L, tx / L
    T1 = (round(T[0] + px * 50, 1), round(T[1] + py * 50, 1))
    T2 = (round(T[0] - px * 35, 1), round(T[1] - py * 35, 1))
    inner = (
        _g_circle(cx, cy, r)
        + _g_line(*T1, *T2, "#8a5300", 2)
        + _g_line(*T, *P, "#444", 1.6)
        + _g_line(*T, *B, "#1a6fa8", 1.5)
        + _g_line(*P, *B, "#1a6fa8", 1.5)
        + _g_dot(*T) + _g_dot(*P) + _g_dot(*B)
        + _g_txt(T[0] - 14, T[1], "T", "#333", 12, bold=True)
        + _g_txt(P[0] + 12, P[1], "P", "#333", 12, bold=True)
        + _g_txt(B[0] + 10, B[1] - 8, "B", "#333", 12, bold=True)
        + _g_txt((T[0] + P[0]) / 2 - 8, (T[1] + P[1]) / 2 - 8, alpha_lbl, "#8a5300", 11)
        + _g_txt((P[0] + B[0]) / 2 + 8, (P[1] + B[1]) / 2, beta_lbl, "#1a6fa8", 11)
        + _g_txt((T[0] + B[0]) / 2, (T[1] + B[1]) / 2, "?", "#059669", 12)
    )
    return _geom_svg(280, 250, inner)


def _geom_svg_bearing_path(b1, turn):
    A = (50, 160)
    # go on bearing b1
    rad1 = math.radians(b1 - 90)
    B = (round(A[0] + 90 * math.cos(rad1), 1), round(A[1] + 90 * math.sin(rad1), 1))
    rad2 = math.radians(b1 + turn - 90)
    C = (round(B[0] + 70 * math.cos(rad2), 1), round(B[1] + 70 * math.sin(rad2), 1))
    inner = (
        _g_line(A[0], A[1] - 50, A[0], A[1] + 10, "#999", 1, "3 3")
        + _g_txt(A[0], A[1] - 58, "N", "#333", 11, bold=True)
        + _g_line(*A, *B, "#1a6fa8", 2)
        + _g_line(*B, *C, "#a13544", 2)
        + _g_dot(*A) + _g_dot(*B) + _g_dot(*C)
        + _g_txt(A[0] - 12, A[1] + 4, "A", "#333", 12, bold=True)
        + _g_txt(B[0] + 10, B[1] - 8, "B", "#333", 12, bold=True)
        + _g_txt(C[0] + 10, C[1], "C", "#333", 12, bold=True)
        + _g_txt((A[0] + B[0]) / 2 - 10, (A[1] + B[1]) / 2, f"{b1}°", "#1a6fa8", 11)
        + _g_txt(B[0] + 18, B[1] + 8, f"turn {turn}°", "#a13544", 11)
    )
    # Fit viewBox roughly
    xs = [A[0], B[0], C[0], A[0]]
    ys = [A[1], B[1], C[1], A[1] - 60]
    minx, maxx = min(xs) - 30, max(xs) + 40
    miny, maxy = min(ys) - 20, max(ys) + 30
    # shift into positive viewBox
    def sh(x, y):
        return x - minx, y - miny
    # rebuild shifted — simpler: use generous canvas
    return _geom_svg(300, 260, inner, max_w=320)


def _geom_svg_pentagon():
    return _geom_svg_regular_polygon(5)


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _geom_found_straight_line():
    a = random.randint(35, 145)
    b = 180 - a
    svg = _geom_svg_straight_line(a)
    q = (rf"Two angles lie on a straight line. One angle is {a}°. "
         rf"Find the other angle.<br>{svg}")
    s = (rf"Angles on a straight line add up to 180°.<br>"
         rf"\({a}° + x = 180°\)<br>"
         rf"\(x = 180° - {a}°\)<br>"
         rf"<strong>\(x = {b}°\)</strong>")
    hint = "Angles on a straight line sum to 180°."
    return q, s, hint, 1, b


def _geom_found_around_point():
    a = random.randint(80, 130)
    b = random.randint(60, 100)
    c = 360 - a - b
    while c <= 15:
        a, b = random.randint(80, 120), random.randint(60, 100)
        c = 360 - a - b
    svg = _geom_svg_around_point(a, b)
    q = (rf"Three angles meet at a point. Two of the angles are {a}° and {b}°. "
         rf"Find the third angle.<br>{svg}")
    s = (rf"Angles around a point sum to 360°.<br>"
         rf"\({a}° + {b}° + x = 360°\)<br>"
         rf"\(x = 360° - {a + b}°\)<br>"
         rf"<strong>\(x = {c}°\)</strong>")
    hint = "Angles around a point sum to 360°."
    return q, s, hint, 1, c


def _geom_found_vertically_opposite():
    a = random.randint(35, 145)
    b = 180 - a
    svg = _geom_svg_crossing(a)
    q = (rf"Two straight lines cross. One of the four angles formed is {a}°.<br>{svg}"
         rf"(a) Write down the vertically opposite angle.<br>"
         rf"(b) Find the other two angles and give a reason.")
    s = (rf"(a) Vertically opposite angles are equal.<br>"
         rf"<strong>Vertically opposite angle \(= {a}°\)</strong><br>"
         rf"(b) Angles on a straight line: \({a}° + x = 180°\) → \(x = {b}°\)<br>"
         rf"The other two angles are both <strong>{b}°</strong> (vertically opposite to each other).")
    hint = "Vertically opposite angles are equal; adjacent angles on a straight line sum to 180°."
    return q, s, hint, 2, _geom_fields_answer(
        (a, b),
        ('(a) Vertically opposite angle (°)', '(b) Adjacent angles (°)'),
    )


def _geom_found_triangle_sum():
    a = random.randint(30, 80)
    b = random.randint(30, 80)
    while a + b >= 170:
        b = random.randint(20, 70)
    c = 180 - a - b
    svg = _geom_svg_triangle_angles(f"{a}°", f"{b}°", "x")
    q = rf"In a triangle, two angles are {a}° and {b}°. Find the third angle.<br>{svg}"
    s = (rf"Angles in a triangle sum to 180°.<br>"
         rf"\({a}° + {b}° + x = 180°\)<br>"
         rf"\(x = 180° - {a + b}°\)<br>"
         rf"<strong>\(x = {c}°\)</strong>")
    hint = "Angles in a triangle sum to 180°."
    return q, s, hint, 1, c


def _geom_found_isosceles():
    base = random.randint(25, 70)
    apex = 180 - 2 * base
    while apex <= 5:
        base = random.randint(25, 70)
        apex = 180 - 2 * base
    svg = _geom_svg_isosceles(f"{base}°", "?")
    q = (rf"An isosceles triangle has a base angle of {base}°. "
         rf"Find the apex angle.<br>{svg}")
    s = (rf"Base angles of an isosceles triangle are equal.<br>"
         rf"Angle sum: \({base}° + {base}° + \text{{apex}} = 180°\)<br>"
         rf"Apex angle \(= 180° - {2 * base}°\)<br>"
         rf"<strong>Apex angle \(= {apex}°\)</strong>")
    hint = "The two base angles are equal in an isosceles triangle."
    return q, s, hint, 2, apex


def _geom_found_exterior_angle():
    a = random.randint(30, 65)
    b = random.randint(30, 65)
    while a + b >= 160:
        b = random.randint(25, 60)
    ext = a + b
    svg = _geom_svg_exterior(f"{a}°", f"{b}°")
    q = (rf"In a triangle, two interior angles are {a}° and {b}°. "
         rf"Find the exterior angle at the third vertex.<br>{svg}")
    s = (rf"The exterior angle of a triangle equals the sum of the two non-adjacent interior angles.<br>"
         rf"Exterior angle \(= {a}° + {b}°\)<br>"
         rf"<strong>\(= {ext}°\)</strong>")
    hint = "Exterior angle = sum of the two opposite interior angles."
    return q, s, hint, 2, ext


def _geom_found_quadrilateral():
    a, b, c = 0, 0, 0
    d = -1
    while d <= 20 or d >= 179:
        a = random.randint(70, 110)
        b = random.randint(70, 110)
        c = random.randint(70, 110)
        d = 360 - a - b - c
    svg = _geom_svg_quadrilateral(a, b, c)
    q = (rf"A quadrilateral has three angles: {a}°, {b}°, and {c}°. "
         rf"Find the fourth angle.<br>{svg}")
    s = (rf"Angles in a quadrilateral sum to 360°.<br>"
         rf"\({a}° + {b}° + {c}° + x = 360°\)<br>"
         rf"\(x = 360° - {a + b + c}°\)<br>"
         rf"<strong>\(x = {d}°\)</strong>")
    hint = "Angles in a quadrilateral sum to 360°."
    return q, s, hint, 1, d


def _geom_found_corresponding():
    a = random.randint(40, 140)
    svg = _geom_svg_parallel_transversal('corresponding', a)
    q = (rf"Two parallel lines are cut by a transversal. "
         rf"One angle formed at the first line is {a}°. "
         rf"Find the corresponding angle at the second line, giving a reason.<br>{svg}")
    s = (rf"Corresponding angles are equal when lines are parallel (F-shape).<br>"
         rf"<strong>Corresponding angle \(= {a}°\)</strong>")
    hint = "Corresponding angles (F-shape) are equal on parallel lines."
    return q, s, hint, 1, a


def _geom_found_alternate():
    a = random.randint(35, 145)
    svg = _geom_svg_parallel_transversal('alternate', a)
    q = (rf"Two parallel lines are cut by a transversal. "
         rf"One angle formed is {a}°. "
         rf"Find the alternate interior angle, giving a reason.<br>{svg}")
    s = (rf"Alternate interior angles are equal when lines are parallel (Z-shape).<br>"
         rf"<strong>Alternate angle \(= {a}°\)</strong>")
    hint = "Alternate angles (Z-shape) are equal on parallel lines."
    return q, s, hint, 1, a


def _geom_found_cointerior():
    a = random.randint(40, 140)
    b = 180 - a
    svg = _geom_svg_parallel_transversal('cointerior', a)
    q = (rf"Two parallel lines are cut by a transversal. "
         rf"One co-interior (allied) angle is {a}°. "
         rf"Find the other co-interior angle, giving a reason.<br>{svg}")
    s = (rf"Co-interior angles (C-shape) sum to 180° when lines are parallel.<br>"
         rf"\({a}° + x = 180°\)<br>"
         rf"<strong>\(x = {b}°\)</strong>")
    hint = "Co-interior angles (C-shape) sum to 180° on parallel lines."
    return q, s, hint, 1, b


def _geom_found_polygon_sum():
    n = random.randint(5, 10)
    total = (n - 2) * 180
    svg = _geom_svg_regular_polygon(n)
    q = (rf"Find the sum of the interior angles of a {_polygon_name(n)} "
         rf"({n} sides).<br>{svg}")
    s = (rf"Sum of interior angles \(= (n-2) \times 180°\)<br>"
         rf"\(= ({n} - 2) \times 180°\)<br>"
         rf"\(= {n - 2} \times 180°\)<br>"
         rf"<strong>\(= {total}°\)</strong>")
    hint = "Use the formula (n − 2) × 180°."
    return q, s, hint, 2, total


def _geom_found_regular_exterior():
    n = random.choice([3, 4, 5, 6, 8, 9, 10, 12])
    ext = 360 // n
    svg = _geom_svg_regular_polygon(n, corner_label="?")
    q = rf"Find the exterior angle of a regular {_polygon_name(n)}.<br>{svg}"
    s = (rf"Exterior angle of a regular polygon \(= \dfrac{{360°}}{{n}}\)<br>"
         rf"\(= \dfrac{{360°}}{{{n}}}\)<br>"
         rf"<strong>\(= {ext}°\)</strong>")
    hint = "Exterior angle of a regular n-gon = 360° ÷ n."
    return q, s, hint, 2, ext


def _geom_found_complementary():
    a = random.randint(15, 75)
    b = 90 - a
    svg = _geom_svg_complementary(a)
    q = (rf"Two angles are complementary. One angle is {a}°. "
         rf"Find the other angle.<br>{svg}")
    s = (rf"Complementary angles sum to 90°.<br>"
         rf"\({a}° + x = 90°\)<br>"
         rf"<strong>\(x = {b}°\)</strong>")
    hint = "Complementary angles sum to 90°."
    return q, s, hint, 1, b


def _geom_found_equilateral():
    svg = _geom_svg_equilateral()
    q = (r"An equilateral triangle has all three sides equal. "
         rf"What is each interior angle? Explain why.<br>{svg}")
    s = (r"All sides are equal, so all angles are equal.<br>"
         r"Sum of angles in any triangle \(= 180°\).<br>"
         r"Each angle \(= 180° \div 3\)<br>"
         r"<strong>Each angle \(= 60°\)</strong>")
    hint = "All angles are equal in an equilateral triangle, and they must sum to 180°."
    return q, s, hint, 2, 60


def _geom_found_multistep_lines():
    a = random.randint(40, 80)
    b = 180 - a
    svg = _geom_svg_crossing(a, label_regions=True)
    q = (rf"Two straight lines intersect. One angle formed is {a}°.<br>{svg}"
         rf"Find all four angles at the intersection, giving reasons for each.")
    s = (rf"Label the four angles A, B, C, D going clockwise.<br>"
         rf"A \(= {a}°\) (given).<br>"
         rf"B \(= 180° - {a}° = {b}°\)  (angles on a straight line).<br>"
         rf"C \(= {a}°\)  (vertically opposite to A).<br>"
         rf"D \(= {b}°\)  (vertically opposite to B).<br>"
         rf"<strong>The four angles are {a}°, {b}°, {a}°, {b}°.</strong>")
    hint = "Use: angles on a straight line = 180°, and vertically opposite angles are equal."
    return q, s, hint, 3, _geom_fields_answer(
        (a, b, a, b),
        ('Angle A (°)', 'Angle B (°)', 'Angle C (°)', 'Angle D (°)'),
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _geom_inter_algebraic_straight():
    # (ax + b) + (cx + d) = 180
    while True:
        a = random.randint(2, 4)
        c = random.randint(1, 3)
        if c == a:
            continue
        x_val = random.randint(12, 22)
        b = random.randint(5, 18)
        d = 180 - (a + c) * x_val - b
        if 5 <= d <= 60 and (a * x_val + b) >= 25 and (c * x_val + d) >= 25:
            break
    ang1 = a * x_val + b
    ang2 = c * x_val + d
    svg = _geom_svg_straight_line(
        90, known_label=f"({a}x+{b})°", unknown_label=f"({c}x+{d})°"
    )
    q = (rf"Two angles on a straight line are \(({a}x + {b})°\) and \(({c}x + {d})°\).<br>{svg}"
         rf"Find the value of \(x\) and the size of each angle.")
    s = (rf"Angles on a straight line sum to 180°:<br>"
         rf"\(({a}x + {b}) + ({c}x + {d}) = 180\)<br>"
         rf"\({a + c}x + {b + d} = 180\)<br>"
         rf"\({a + c}x = {180 - b - d}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angles: \({a}({x_val})+{b} = {ang1}°\) and \({c}({x_val})+{d} = {ang2}°\)<br>"
         rf"<strong>\(x = {x_val}\); angles are {ang1}° and {ang2}°</strong>")
    hint = f"Set the two expressions equal to 180 and solve for x."
    return q, s, hint, 3, _geom_fields_answer(
        (x_val, ang1, ang2),
        ('x', 'First angle (°)', 'Second angle (°)'),
    )


def _geom_inter_algebraic_triangle():
    # three angles: (ax+b), (cx+d), (ex+f) summing to 180
    while True:
        a = random.randint(2, 4)
        c = random.randint(1, 3)
        e = random.randint(1, 3)
        x_val = random.randint(8, 16)
        b = random.randint(5, 15)
        d = random.randint(5, 15)
        f = 180 - (a + c + e) * x_val - b - d
        if 5 <= f <= 50 and (a * x_val + b) >= 20 and (c * x_val + d) >= 15 and (e * x_val + f) >= 15:
            break
    ang1, ang2, ang3 = a * x_val + b, c * x_val + d, e * x_val + f
    svg = _geom_svg_triangle_angles(rf"({a}x+{b})°", rf"({c}x+{d})°", rf"({e}x+{f})°")
    q = (rf"The angles of a triangle are \(({a}x + {b})°\), \(({c}x + {d})°\), and \(({e}x + {f})°\).<br>{svg}"
         rf"Find \(x\) and the size of each angle.")
    s = (rf"Angles in a triangle sum to 180°:<br>"
         rf"\({a + c + e}x + {b + d + f} = 180\)<br>"
         rf"\({a + c + e}x = {180 - b - d - f}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angles: \({ang1}°\), \({ang2}°\), \({ang3}°\)<br>"
         rf"<strong>\(x = {x_val}\); angles are {ang1}°, {ang2}°, {ang3}°</strong>")
    hint = "Set the sum of the three expressions equal to 180."
    return q, s, hint, 3, _geom_fields_answer(
        (x_val, ang1, ang2, ang3),
        ('x', 'Angle 1 (°)', 'Angle 2 (°)', 'Angle 3 (°)'),
    )


def _geom_inter_regular_polygon_n():
    # Given interior angle, find n
    # Interior angle of regular n-gon = (n-2)*180/n
    # Choose n from sensible values
    n = random.choice([5, 6, 8, 9, 10, 12])
    interior = (n - 2) * 180 // n
    svg = _geom_svg_regular_polygon(n, corner_label=f"{interior}°")
    q = (rf"A regular polygon has an interior angle of {interior}°. "
         rf"Find the number of sides.<br>{svg}")
    s = (rf"Exterior angle \(= 180° - {interior}° = {180 - interior}°\)<br>"
         rf"Number of sides \(= \dfrac{{360°}}{{{180 - interior}°}} = {n}\)<br>"
         rf"<strong>\(n = {n}\) sides</strong>")
    hint = "Find the exterior angle first (= 180° − interior angle), then n = 360° ÷ exterior angle."
    return q, s, hint, 3, n


def _geom_inter_complex_parallel():
    # Triangle between two parallel lines; use alternate/co-interior to find a triangle angle
    p = random.randint(35, 70)
    q_ang = random.randint(35, 70)
    r_ang = p + q_ang   # exterior, so angle in triangle = 180 - r_ang? No.
    # Setup: line l1 ∥ l2. A is on l1, B and C are on l2.
    # Angle between l1 and AB (alternate to angle ABC) = p°
    # Angle ACB = q_ang°
    # Find angle BAC
    ang_abc = p  # alternate angles (AB as transversal between parallels)
    ang_bac = 180 - ang_abc - q_ang
    svg = _geom_svg_parallel_triangle(f"{p}°", f"{q_ang}°")
    q = (rf"Line \(l_1\) is parallel to line \(l_2\). Point A lies on \(l_1\) and points B and C lie on \(l_2\).<br>"
         rf"The angle between \(l_1\) and AB (measured below \(l_1\)) is {p}° and angle ACB = {q_ang}°.<br>"
         rf"Find angle BAC.<br>{svg}")
    s = (rf"Angle ABC \(= {p}°\) (alternate angles, \(l_1 \parallel l_2\), AB is transversal).<br>"
         rf"In triangle ABC: angle BAC \(= 180° - {p}° - {q_ang}°\)<br>"
         rf"<strong>Angle BAC \(= {ang_bac}°\)</strong>")
    hint = "Use alternate angles to find angle ABC first, then use the triangle angle sum."
    return q, s, hint, 3, ang_bac


def _geom_inter_angle_at_centre():
    circ = random.randint(20, 60)
    centre = 2 * circ
    svg = _geom_svg_circle_centre(f"{circ}°", "?")
    q = (rf"O is the centre of a circle. Points A, B, and C lie on the circle.<br>"
         rf"Angle ACB = {circ}°. Find angle AOB, giving a reason.<br>{svg}")
    s = (rf"The angle at the centre is twice the angle at the circumference when both are subtended by the same arc.<br>"
         rf"Angle AOB \(= 2 \times {circ}°\)<br>"
         rf"<strong>Angle AOB \(= {centre}°\)</strong>")
    hint = "Angle at centre = 2 × angle at circumference (same arc)."
    return q, s, hint, 2, centre


def _geom_inter_angle_semicircle():
    b_ang = random.randint(25, 60)
    a_ang = 90 - b_ang
    svg = _geom_svg_semicircle(f"{b_ang}°")
    q = (rf"AB is a diameter of a circle. C is a point on the circle.<br>"
         rf"Angle ABC = {b_ang}°. Find angle BAC and angle ACB, giving reasons.<br>{svg}")
    s = (rf"Angle ACB \(= 90°\) (angle in a semicircle — angle subtended by a diameter).<br>"
         rf"In triangle ACB: angle BAC \(= 180° - 90° - {b_ang}°\)<br>"
         rf"<strong>Angle BAC \(= {a_ang}°\);  angle ACB \(= 90°\)</strong>")
    hint = "The angle subtended by a diameter at the circumference is always 90°."
    return q, s, hint, 3, _geom_fields_answer(
        (a_ang, 90),
        ('Angle BAC (°)', 'Angle ACB (°)'),
    )


def _geom_inter_same_segment():
    ang = random.randint(25, 65)
    svg = _geom_svg_same_segment(f"{ang}°")
    q = (rf"Points P, Q, R, and S lie on a circle. "
         rf"Angle PRQ = {ang}°. "
         rf"Find angle PSQ, giving a reason.<br>{svg}")
    s = (rf"Angles in the same segment are equal — both PRQ and PSQ are subtended by arc PQ from the same side.<br>"
         rf"<strong>Angle PSQ \(= {ang}°\)</strong>")
    hint = "Angles in the same segment (subtended by the same chord from the same side) are equal."
    return q, s, hint, 2, ang


def _geom_inter_cyclic_quad():
    a = random.randint(60, 110)
    b = random.randint(60, 110)
    c = 180 - a
    d = 180 - b
    svg = _geom_svg_cyclic_quad(f"{a}°", f"{b}°")
    q = (rf"ABCD is a cyclic quadrilateral (all four vertices lie on a circle).<br>"
         rf"Angle DAB = {a}° and angle ABC = {b}°. Find angles BCD and CDA, giving reasons.<br>{svg}")
    s = (rf"Opposite angles in a cyclic quadrilateral sum to 180°.<br>"
         rf"Angle BCD \(= 180° - {a}° = {c}°\)<br>"
         rf"Angle CDA \(= 180° - {b}° = {d}°\)<br>"
         rf"<strong>Angle BCD \(= {c}°\);  angle CDA \(= {d}°\)</strong>")
    hint = "Opposite angles in a cyclic quadrilateral add up to 180°."
    return q, s, hint, 3, _geom_fields_answer(
        (c, d),
        ('Angle BCD (°)', 'Angle CDA (°)'),
    )


def _geom_inter_tangent_radius():
    # Pythagorean triple: radius r, distance OT, tangent length AT
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10)]
    r, t_len, ot = random.choice(triples)
    svg = _geom_svg_tangent_radius()
    q = (rf"A tangent from external point T touches a circle at A. "
         rf"The radius OA = {r} cm and the distance OT = {ot} cm.<br>"
         rf"Find the length AT. (Tangent is perpendicular to radius at point of contact.)<br>{svg}")
    s = (rf"Since OA is a radius and AT is a tangent at A, angle OAT = 90°.<br>"
         rf"By Pythagoras in triangle OAT:<br>"
         rf"\(AT^2 = OT^2 - OA^2 = {ot}^2 - {r}^2 = {ot**2} - {r**2} = {ot**2 - r**2}\)<br>"
         rf"\(AT = \sqrt{{{ot**2 - r**2}}}\)<br>"
         rf"<strong>AT \(= {t_len}\) cm</strong>")
    hint = "The tangent is perpendicular to the radius at the point of contact. Use Pythagoras."
    return q, s, hint, 3, t_len


def _geom_inter_bearing():
    b1 = random.choice([40, 50, 55, 60, 65, 70])
    back = b1 + 180
    svg = _geom_svg_bearing(b1)
    q = (rf"The bearing of town Q from town P is {b1:03d}°. "
         rf"Find the bearing of town P from town Q.<br>{svg}")
    s = (rf"To find the reverse bearing, add 180° (since the bearing is less than 180°).<br>"
         rf"Bearing of P from Q \(= {b1}° + 180°\)<br>"
         rf"<strong>\(= {back:03d}°\)</strong>")
    hint = "Add 180° to the forward bearing to get the back-bearing (if the result ≤ 360°)."
    return q, s, hint, 2, back


def _geom_inter_similar_triangles():
    scale_num = random.randint(2, 4)
    scale_den = scale_num + random.randint(1, 3)
    ab = random.randint(4, 10)
    bc = random.randint(4, 10)
    pq = ab * scale_den // scale_num if ab % scale_num == 0 else ab + scale_den
    # ensure clean values
    ab = scale_num * random.randint(2, 5)
    pq = ab * scale_den // scale_num
    bc = scale_num * random.randint(2, 4)
    qr = bc * scale_den // scale_num
    ang_b = random.randint(30, 70)
    svg = _geom_svg_similar_triangles(ab, bc, pq, ang_b)
    q = (rf"Triangle ABC is similar to triangle PQR (same shape, different size).<br>"
         rf"AB = {ab} cm, BC = {bc} cm, PQ = {pq} cm, and angle ABC = {ang_b}°.<br>"
         rf"(a) Find QR.  (b) Find angle PQR.<br>{svg}")
    s = (rf"(a) Scale factor \(= \dfrac{{PQ}}{{AB}} = \dfrac{{{pq}}}{{{ab}}} = \dfrac{{{scale_den}}}{{{scale_num}}}\)<br>"
         rf"\(QR = BC \times \dfrac{{{scale_den}}}{{{scale_num}}} = {bc} \times \dfrac{{{scale_den}}}{{{scale_num}}} = {qr}\) cm<br>"
         rf"<strong>QR \(= {qr}\) cm</strong><br>"
         rf"(b) Corresponding angles in similar triangles are equal.<br>"
         rf"<strong>Angle PQR \(= {ang_b}°\)</strong>")
    hint = "Find the scale factor = PQ ÷ AB, then multiply BC. Corresponding angles are equal."
    return q, s, hint, 4, _geom_fields_answer(
        (qr, ang_b),
        ('(a) QR (cm)', '(b) Angle PQR (°)'),
    )


def _geom_inter_polygon_algebra():
    # Interior + exterior = 180; interior = k × exterior → k*ext + ext = 180 → ext = 180/(k+1)
    k = random.choice([2, 3, 4, 5])
    ext = 180 // (k + 1)
    interior = 180 - ext
    n = 360 // ext
    svg = _geom_svg_regular_polygon(n)
    q = (rf"A regular polygon has an interior angle that is {k} times its exterior angle. "
         rf"Find the number of sides of the polygon.<br>{svg}")
    s = (rf"Let exterior angle \(= x°\). Interior angle \(= {k}x°\).<br>"
         rf"Interior + exterior \(= 180°\): \({k}x + x = 180° \Rightarrow {k + 1}x = 180°\)<br>"
         rf"\(x = {ext}°\)  (exterior angle)<br>"
         rf"Number of sides \(= \dfrac{{360°}}{{{ext}°}} = {n}\)<br>"
         rf"<strong>\(n = {n}\) sides</strong>")
    hint = "Interior + exterior = 180°. Set up an equation with the given ratio."
    return q, s, hint, 4, n


def _geom_inter_isosceles_parallel():
    base_ang = random.randint(30, 65)
    apex = 180 - 2 * base_ang
    corr = base_ang   # corresponding or alternate angle on parallel line
    svg = _geom_svg_isos_parallel(f"{base_ang}°")
    q = (rf"Triangle ABC is isosceles with AB = AC. A line DE is parallel to BC, "
         rf"with D on AB and E on AC.<br>"
         rf"Angle ABC = {base_ang}°.<br>"
         rf"(a) Find angle BAC.  (b) Find angle ADE, giving a reason.<br>{svg}")
    s = (rf"(a) Since AB = AC, base angles are equal: angle ABC = angle ACB = {base_ang}°.<br>"
         rf"Angle BAC \(= 180° - {base_ang}° - {base_ang}° = {apex}°\)<br>"
         rf"<strong>Angle BAC \(= {apex}°\)</strong><br>"
         rf"(b) Since DE ∥ BC, angle ADE = angle ABC = {base_ang}° (corresponding angles).<br>"
         rf"<strong>Angle ADE \(= {base_ang}°\)</strong>")
    hint = "Find angle BAC using isosceles triangle, then use corresponding/alternate angles for DE ∥ BC."
    return q, s, hint, 4, _geom_fields_answer(
        (apex, base_ang),
        ('(a) Angle BAC (°)', '(b) Angle ADE (°)'),
    )


def _geom_inter_interior_exterior():
    n = random.choice([5, 6, 8, 10, 12])
    interior = (n - 2) * 180 // n
    exterior = 360 // n
    svg = _geom_svg_regular_polygon(n, corner_label="ext?")
    q = (rf"A regular {_polygon_name(n)} has {n} sides.<br>{svg}"
         rf"(a) Calculate the interior angle.<br>"
         rf"(b) Calculate the exterior angle.<br>"
         rf"(c) Verify that interior angle + exterior angle = 180°.")
    s = (rf"(a) Interior angle \(= \dfrac{{(n-2) \times 180°}}{{n}} = \dfrac{{{(n-2)*180}°}}{{{n}}} = {interior}°\)<br>"
         rf"<strong>Interior angle \(= {interior}°\)</strong><br>"
         rf"(b) Exterior angle \(= \dfrac{{360°}}{{{n}}} = {exterior}°\)<br>"
         rf"<strong>Exterior angle \(= {exterior}°\)</strong><br>"
         rf"(c) \({interior}° + {exterior}° = {interior + exterior}° = 180°\) ✓")
    hint = "Interior angle = (n−2)×180°/n; exterior angle = 360°/n. They must sum to 180°."
    return q, s, hint, 3, _geom_fields_answer(
        (interior, exterior),
        ('(a) Interior angle (°)', '(b) Exterior angle (°)'),
    )


def _geom_inter_kite_angles():
    ang_a = random.randint(60, 110)
    ang_b = random.randint(50, 80)
    ang_d = ang_b  # kite: angles between unequal sides are equal
    ang_c = 360 - ang_a - 2 * ang_b
    while ang_c <= 10 or ang_c >= 350:
        ang_a = random.randint(60, 100)
        ang_b = random.randint(50, 80)
        ang_d = ang_b
        ang_c = 360 - ang_a - 2 * ang_b
    svg = _geom_svg_kite(f"{ang_a}°", f"{ang_b}°")
    q = (rf"In kite ABCD, AB = AD and CB = CD. "
         rf"Angle A = {ang_a}° and angle B = {ang_b}°.<br>"
         rf"Find angles C and D, giving reasons.<br>{svg}")
    s = (rf"In a kite, the two angles between unequal sides are equal: angle B = angle D.<br>"
         rf"Angle D \(= {ang_d}°\)<br>"
         rf"Angle sum: angle A + angle B + angle C + angle D = 360°<br>"
         rf"\({ang_a}° + {ang_b}° + \text{{angle C}} + {ang_d}° = 360°\)<br>"
         rf"Angle C \(= 360° - {ang_a + ang_b + ang_d}° = {ang_c}°\)<br>"
         rf"<strong>Angle C \(= {ang_c}°\);  angle D \(= {ang_d}°\)</strong>")
    hint = "In a kite, the two angles between the unequal sides are equal."
    return q, s, hint, 3, _geom_fields_answer(
        (ang_c, ang_d),
        ('Angle C (°)', 'Angle D (°)'),
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _geom_diff_alternate_segment():
    alpha = random.randint(30, 65)
    centre = 2 * alpha
    svg = _geom_svg_alternate_segment(f"{alpha}°")
    q = (rf"A tangent to a circle at point T makes an angle of {alpha}° with chord TA.<br>"
         rf"Point B lies on the major arc TA. O is the centre of the circle.<br>{svg}"
         rf"(a) Find angle TBA (alternate segment theorem).<br>"
         rf"(b) Hence find angle TOA.")
    s = (rf"(a) By the alternate segment theorem, the angle between a tangent and a chord equals "
         rf"the inscribed angle in the alternate segment.<br>"
         rf"<strong>Angle TBA \(= {alpha}°\)</strong><br>"
         rf"(b) Angle at centre = 2 × angle at circumference (same arc TA):<br>"
         rf"Angle TOA \(= 2 \times {alpha}°\)<br>"
         rf"<strong>Angle TOA \(= {centre}°\)</strong>")
    hint = "Use the alternate segment theorem, then angle at centre = 2 × angle at circumference."
    return q, s, hint, 5, _geom_fields_answer(
        (alpha, centre),
        ('(a) Angle TBA (°)', '(b) Angle TOA (°)'),
    )


def _geom_diff_two_tangents():
    angle_p = random.randint(25, 65)
    angle_aob = 180 - angle_p
    svg = _geom_svg_two_tangents(f"{angle_p}°")
    q = (rf"From external point P, two tangents PA and PB touch a circle (centre O) at A and B respectively.<br>"
         rf"Angle APB = {angle_p}°. Find angle AOB, showing your working clearly.<br>{svg}")
    s = (rf"OA is perpendicular to PA (tangent ⊥ radius): angle OAP = 90°.<br>"
         rf"OB is perpendicular to PB (tangent ⊥ radius): angle OBP = 90°.<br>"
         rf"Quadrilateral OAPB: angle sum = 360°.<br>"
         rf"\({angle_p}° + 90° + \text{{angle AOB}} + 90° = 360°\)<br>"
         rf"Angle AOB \(= 360° - {angle_p + 180}° = {360 - angle_p - 180}°\)<br>"
         rf"<strong>Angle AOB \(= {angle_aob}°\)</strong>")
    hint = "Each tangent is perpendicular to the radius at the point of contact. Use quadrilateral angle sum."
    return q, s, hint, 4, angle_aob


def _geom_diff_multi_circle():
    # A, B, C, D on circle. Angle AOC (at centre) given. Find circumference angle + reflex.
    centre_ang = random.choice([80, 100, 110, 120, 130, 140])
    circ_major = centre_ang // 2
    reflex = 360 - centre_ang
    circ_minor = reflex // 2
    svg = _geom_svg_multi_circle(f"{centre_ang}°")
    q = (rf"O is the centre of a circle. A and C are points on the circle. "
         rf"Angle AOC = {centre_ang}° (the non-reflex angle).<br>"
         rf"Point D lies on the major arc AC. Point B lies on the minor arc AC.<br>"
         rf"Find: (a) angle ADC  (b) angle ABC<br>{svg}")
    s = (rf"(a) Angle at circumference = ½ angle at centre (same arc AC, major arc side).<br>"
         rf"Angle ADC \(= \dfrac{{{centre_ang}°}}{{2}}\)<br>"
         rf"<strong>Angle ADC \(= {circ_major}°\)</strong><br>"
         rf"(b) B is on the minor arc, so use the reflex angle at O.<br>"
         rf"Reflex angle AOC \(= 360° - {centre_ang}° = {reflex}°\)<br>"
         rf"Angle ABC \(= \dfrac{{{reflex}°}}{{2}}\)<br>"
         rf"<strong>Angle ABC \(= {circ_minor}°\)</strong><br>"
         rf"Check: {circ_major}° + {circ_minor}° = {circ_major + circ_minor}° (opposite angles in cyclic quad → should sum to 180° ✓)")
    hint = "For the major-arc angle use the direct centre angle; for the minor-arc angle use the reflex centre angle."
    return q, s, hint, 5, _geom_fields_answer(
        (circ_major, circ_minor),
        ('(a) Angle ADC (°)', '(b) Angle ABC (°)'),
    )


def _geom_diff_similar_area():
    # Two similar shapes, sides in ratio p:q, find area ratio
    p = random.randint(2, 4)
    q_rat = p + random.randint(1, 3)
    area_small = p * p * random.randint(3, 8)
    area_large = area_small * q_rat * q_rat // (p * p)
    svg = _geom_svg_similar_triangles(p, p, q_rat, 60)
    q_str = (rf"Two similar triangles have corresponding sides in the ratio \({p}:{q_rat}\)<br>"
             rf"The area of the smaller triangle is {area_small} cm².<br>"
             rf"Find the area of the larger triangle.<br>{svg}")
    s = (rf"For similar shapes, area ratio \(= (\text{{length ratio}})^2\).<br>"
         rf"Area ratio \(= \left(\dfrac{{{q_rat}}}{{{p}}}\right)^2 = \dfrac{{{q_rat**2}}}{{{p**2}}}\)<br>"
         rf"Area of larger triangle \(= {area_small} \times \dfrac{{{q_rat**2}}}{{{p**2}}} = \dfrac{{{area_small * q_rat**2}}}{{{p**2}}}\)<br>"
         rf"<strong>\(= {area_small * q_rat**2 // p**2}\) cm²</strong>")
    hint = "Area ratio = (length ratio)². Square the ratio of corresponding sides."
    return q_str, s, hint, 4, area_large


def _geom_diff_prove_triangle_sum():
    svg = _geom_svg_prove_triangle_sum()
    q = (r"Prove that the angles in a triangle sum to 180°. "
         rf"You may use the fact that alternate angles on parallel lines are equal.<br>{svg}")
    s = (r"Draw triangle ABC. Through vertex C, draw line DE parallel to AB.<br>"
         r"Angle DCA = angle CAB (alternate angles, DE ∥ AB, AC transversal).<br>"
         r"Angle ECB = angle CBA (alternate angles, DE ∥ AB, BC transversal).<br>"
         r"Angle DCA + angle ACB + angle ECB = 180° (angles on straight line DCE).<br>"
         r"Substituting: angle CAB + angle ACB + angle CBA = 180°.<br>"
         r"<strong>Therefore the angles in triangle ABC sum to 180°. ✓</strong>")
    hint = "Draw a line through one vertex parallel to the opposite side, then use alternate angles."
    return q, s, hint, 4


def _geom_diff_algebraic_circle():
    # angle at centre = 2 × angle at circumference, both expressed algebraically
    x_val = random.randint(15, 30)
    a_coef = random.randint(2, 4)
    b_off = random.randint(5, 20)
    c_coef = random.randint(1, 2)
    d_off = random.randint(5, 20)
    # Centre = 2 × circumference: a*x + b = 2*(c*x + d)
    # (a - 2c)*x = 2d - b
    diff = a_coef - 2 * c_coef
    rhs = 2 * d_off - b_off
    if diff == 0 or rhs % diff != 0:
        a_coef, c_coef, x_val = 4, 1, 20
        b_off, d_off = 10, 20
        diff = 4 - 2
        rhs = 40 - 10
    x_val = rhs // diff
    centre_ang = a_coef * x_val + b_off
    circ_ang = c_coef * x_val + d_off
    svg = _geom_svg_circle_centre(rf"({c_coef}x+{d_off})°", rf"({a_coef}x+{b_off})°")
    q = (rf"O is the centre of a circle. A, B, C are points on the circle.<br>"
         rf"Angle AOB \(= ({a_coef}x + {b_off})°\) and angle ACB \(= ({c_coef}x + {d_off})°\)<br>"
         rf"Find x and the size of each angle.<br>{svg}")
    s = (rf"Angle at centre = 2 × angle at circumference (same arc AB):<br>"
         rf"\({a_coef}x + {b_off} = 2({c_coef}x + {d_off})\)<br>"
         rf"\({a_coef}x + {b_off} = {2*c_coef}x + {2*d_off}\)<br>"
         rf"\({diff}x = {rhs}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angle AOB \(= {centre_ang}°\),  angle ACB \(= {circ_ang}°\)<br>"
         rf"<strong>\(x = {x_val}\);  angle AOB \(= {centre_ang}°\),  angle ACB \(= {circ_ang}°\)</strong>")
    hint = "Use: angle at centre = 2 × angle at circumference, then solve for x."
    return q, s, hint, 5, _geom_fields_answer(
        (x_val, centre_ang, circ_ang),
        ('x', 'Angle AOB (°)', 'Angle ACB (°)'),
    )


def _geom_diff_chord_distance():
    # Chord at distance d from centre, half-chord h, radius r = sqrt(d²+h²)
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)]
    d, h, r = random.choice(triples)
    chord = 2 * h
    svg = _geom_svg_chord_distance(f"{chord} cm", f"{d} cm")
    q = (rf"A chord of a circle has length {chord} cm. "
         rf"The perpendicular distance from the centre O to the chord is {d} cm.<br>"
         rf"Find the radius of the circle.<br>{svg}")
    s = (rf"The perpendicular from the centre bisects the chord.<br>"
         rf"Half-chord \(= {chord} \div 2 = {h}\) cm.<br>"
         rf"In the right-angled triangle formed:<br>"
         rf"\(r^2 = {d}^2 + {h}^2 = {d**2} + {h**2} = {d**2 + h**2}\)<br>"
         rf"\(r = \sqrt{{{d**2 + h**2}}}\)<br>"
         rf"<strong>Radius \(= {r}\) cm</strong>")
    hint = "The perpendicular from the centre bisects the chord. Use Pythagoras with half the chord length."
    return q, s, hint, 4, r


def _geom_diff_cyclic_quad_proof():
    svg = _geom_svg_cyclic_quad("α", "?")
    q = (rf"ABCD is a cyclic quadrilateral. Prove that angle DAB + angle BCD = 180°.<br>{svg}")
    s = (r"Let angle DAB \(= \alpha\). The arc BCD subtends angle \(\alpha\) at the circumference (point A).<br>"
         r"By the angle at centre theorem, the angle at O subtended by arc BCD \(= 2\alpha\).<br>"
         r"The remaining arc BAD subtends the reflex angle at O \(= 360° - 2\alpha\).<br>"
         r"Angle BCD (at circumference, subtended by arc BAD) \(= \dfrac{360° - 2\alpha}{2} = 180° - \alpha\).<br>"
         r"Therefore angle DAB + angle BCD \(= \alpha + (180° - \alpha) = 180°\).<br>"
         r"<strong>Opposite angles in a cyclic quadrilateral sum to 180°. ✓</strong>")
    hint = "Use the angle at centre theorem for both arcs, noting that the two arcs together form the full 360°."
    return q, s, hint, 5


def _geom_diff_regular_polygon_proof():
    n = random.choice([5, 6, 8, 10])
    interior = (n - 2) * 180 // n
    svg = _geom_svg_regular_polygon(n)
    q = (rf"(a) Show that the interior angle of a regular {_polygon_name(n)} is {interior}°.<br>"
         rf"(b) Prove that the exterior angles of any convex polygon sum to 360°.<br>{svg}")
    s = (rf"(a) A regular {_polygon_name(n)} can be divided into \({n} - 2 = {n-2}\) triangles.<br>"
         rf"Total interior angle sum \(= {n-2} \times 180° = {(n-2)*180}°\)<br>"
         rf"Each interior angle \(= \dfrac{{{(n-2)*180}°}}{{{n}}} = {interior}°\) ✓<br>"
         rf"(b) At each vertex, interior + exterior = 180°.<br>"
         rf"Summing all \(n\) vertices: (sum of interior angles) + (sum of exterior angles) \(= 180n°\)<br>"
         rf"\((n-2) \times 180° + \text{{exterior sum}} = 180n°\)<br>"
         rf"Exterior sum \(= 180n° - (n-2) \times 180° = 180n° - 180n° + 360° = 360°\). ✓<br>"
         rf"<strong>Exterior angles of any convex polygon sum to 360°.</strong>")
    hint = "For (a) divide into triangles. For (b) use interior + exterior = 180° at each vertex."
    return q, s, hint, 5


def _geom_diff_polygon_algebra():
    # Pentagon: four algebraic angles (x+a),(x+b),(x+c),(x+d) plus one fixed angle.
    # 4x + (a+b+c+d) + fixed = 540
    presets = [
        (70, [20, 30, 50, 60], 100),   # x=70: 90,100,120,130,100 → sum 540
        (65, [20, 30, 50, 60], 120),   # x=65: 85,95,115,125,120 → sum 540
        (55, [40, 50, 60, 80],  90),   # x=55: 95,105,115,135, 90 → sum 540
    ]
    x_val, offs, fixed = random.choice(presets)
    a, b, c, d = offs
    ang1, ang2, ang3, ang4 = x_val+a, x_val+b, x_val+c, x_val+d
    angles_list = ", ".join(rf"(x + {o})^\circ" for o in (a, b, c, d))
    svg = _geom_svg_pentagon()
    q = (rf"A pentagon has angles \({angles_list}, \text{{and }} {fixed}^\circ\)<br>"
         rf"Find x and all five angles.<br>{svg}")
    s = (rf"Sum of interior angles of a pentagon \(= (5-2) \times 180° = 540°\).<br>"
         rf"\((x+{a}) + (x+{b}) + (x+{c}) + (x+{d}) + {fixed} = 540\)<br>"
         rf"\(4x + {a+b+c+d+fixed} = 540\)<br>"
         rf"\(4x = {540-a-b-c-d-fixed}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angles: \({ang1}^\circ, {ang2}^\circ, {ang3}^\circ, {ang4}^\circ, {fixed}^\circ\)<br>"
         rf"<strong>\(x = {x_val}\); angles are {ang1}°, {ang2}°, {ang3}°, {ang4}°, {fixed}°</strong>")
    hint = "Sum of pentagon angles = 540°. Collect the x terms and constants, then solve."
    return q, s, hint, 4, _geom_fields_answer(
        (x_val, ang1, ang2, ang3, ang4, fixed),
        ('x', 'Angle 1 (°)', 'Angle 2 (°)', 'Angle 3 (°)', 'Angle 4 (°)', 'Angle 5 (°)'),
    )


def _geom_diff_reflex_centre():
    arc_ang = random.choice([40, 50, 55, 60, 65, 70, 80])
    reflex = 360 - 2 * arc_ang
    svg = _geom_svg_circle_centre(f"{arc_ang}°", "reflex ?")
    q = (rf"O is the centre of a circle. A and B are points on the circle. "
         rf"A point P on the major arc subtends angle APB = {arc_ang}°.<br>"
         rf"Find the reflex angle AOB.<br>{svg}")
    s = (rf"Non-reflex angle AOB \(= 2 \times \angle APB = 2 \times {arc_ang}° = {2*arc_ang}°\) "
         rf"(angle at centre = 2 × angle at circumference).<br>"
         rf"Reflex angle AOB \(= 360° - {2*arc_ang}°\)<br>"
         rf"<strong>Reflex angle AOB \(= {reflex}°\)</strong>")
    hint = "Find the non-reflex angle at centre first (= 2 × angle at circumference), then subtract from 360°."
    return q, s, hint, 3, reflex


def _geom_diff_tangent_chord():
    alpha = random.randint(35, 65)
    # tangent-chord angle = inscribed angle in alternate segment
    # In triangle: angle at T (tangent-chord) = alpha
    # On the other arc, inscribed angle = alpha
    # Find another angle using isosceles triangle OTA (OT is radius, OA is radius)
    # OTA is isosceles: OT = OA (radii? No, OT is not a radius)
    # Let's use: tangent at T, chord TP, angle PTQ (between tangent and chord) = alpha
    # B is on major arc, angle TBP = alpha (alt segment)
    # Angle TPB = beta (given), find angle BTQ
    beta = random.randint(20, 40)
    svg = _geom_svg_tangent_chord(f"{alpha}°", f"{beta}°")
    q = (rf"A tangent at point T and a chord TP are drawn. "
         rf"The angle between the tangent and chord TP is {alpha}°.<br>"
         rf"Point B lies on the major arc TP, and angle TPB = {beta}°.<br>"
         rf"Find: (a) angle TBP  (b) angle BTP<br>{svg}")
    s = (rf"(a) Alternate segment theorem: angle between tangent and chord = angle in alternate segment.<br>"
         rf"<strong>Angle TBP \(= {alpha}°\)</strong><br>"
         rf"(b) In triangle TBP: angles sum to 180°.<br>"
         rf"Angle BTP \(= 180° - {alpha}° - {beta}°\)<br>"
         rf"<strong>Angle BTP \(= {180 - alpha - beta}°\)</strong>")
    hint = "Apply the alternate segment theorem to find angle TBP, then use triangle angle sum."
    return q, s, hint, 5, _geom_fields_answer(
        (alpha, 180 - alpha - beta),
        ('(a) Angle TBP (°)', '(b) Angle BTP (°)'),
    )


def _geom_diff_bearing_complex():
    # Three-point bearing problem
    ang_n = random.randint(30, 60)
    # Ship goes from A north-east (bearing ang_n), then turns.
    b1 = ang_n
    turn = random.randint(70, 100)
    b2 = b1 + turn
    q = (rf"A ship leaves port A on a bearing of {b1:03d}°. "
         rf"After sailing for some time it turns clockwise by {turn}° and continues to port C.<br>"
         rf"(a) Find the bearing of C from the ship's turning point B.<br>"
         rf"(b) Find the angle ABC.")
    b2_result = b1 + turn
    angle_abc = 180 - turn
    svg = _geom_svg_bearing_path(b1, turn)
    q_str = (rf"A ship leaves port A on a bearing of {b1:03d}°. "
             rf"It sails to point B, then turns clockwise by {turn}° and sails to C.<br>"
             rf"(a) Find the bearing from B to C.<br>"
             rf"(b) Find the interior angle ABC of the triangle formed.<br>{svg}")
    s = (rf"(a) The ship was heading on bearing {b1:03d}°; it turns clockwise by {turn}°.<br>"
         rf"New bearing \(= {b1}° + {turn}° = {b2_result}°\)<br>"
         rf"<strong>Bearing from B to C \(= {b2_result:03d}°\)</strong><br>"
         rf"(b) The exterior angle at B (turn) \(= {turn}°\).<br>"
         rf"Interior angle ABC \(= 180° - {turn}°\)<br>"
         rf"<strong>Angle ABC \(= {angle_abc}°\)</strong>")
    hint = "The clockwise turn gives the change in bearing. Interior angle = 180° − exterior turn angle."
    return q_str, s, hint, 4, _geom_fields_answer(
        (b2_result, angle_abc),
        ('(a) Bearing B to C (°)', '(b) Angle ABC (°)'),
    )


def _geom_diff_inscribed_angles():
    # Multiple inscribed angle relationships in one diagram
    ang1 = random.randint(25, 50)
    ang2 = random.randint(25, 50)
    # ABCD cyclic quad. Given two angles, find others using all circle theorems
    opp_ang1 = 180 - ang1
    opp_ang2 = 180 - ang2
    centre_ang = 2 * ang1
    svg = _geom_svg_cyclic_quad(f"{ang1}°", f"{ang2}°")
    q = (rf"A, B, C, D are four points on a circle with centre O.<br>"
         rf"Angle DAB = {ang1}° and angle ABC = {ang2}°.<br>"
         rf"Find: (a) angle BCD  (b) angle CDA  (c) angle BOD<br>{svg}")
    s = (rf"(a) Opposite angles in cyclic quadrilateral sum to 180°.<br>"
         rf"Angle BCD \(= 180° - {ang1}° = {opp_ang1}°\)<br>"
         rf"<strong>Angle BCD \(= {opp_ang1}°\)</strong><br>"
         rf"(b) Angle CDA \(= 180° - {ang2}° = {opp_ang2}°\) (opposite angles in cyclic quad).<br>"
         rf"<strong>Angle CDA \(= {opp_ang2}°\)</strong><br>"
         rf"(c) Angle BOD = 2 × angle BCD? No — angle BOD is subtended by arc BAD.<br>"
         rf"Arc BAD subtends angle BCD = {opp_ang1}° at circumference.<br>"
         rf"Angle BOD \(= 2 \times {opp_ang1}° = {2*opp_ang1}°\) (but check if reflex is needed).<br>"
         rf"Since {2*opp_ang1}° {'< 360°' if 2*opp_ang1 < 360 else '≥ 360°'}:<br>"
         rf"<strong>Angle BOD \(= {min(2*opp_ang1, 360-2*opp_ang1)}°\)</strong> (non-reflex)")
    hint = "Use cyclic quadrilateral for (a) and (b), then angle at centre = 2 × angle at circumference for (c)."
    bod = min(2 * opp_ang1, 360 - 2 * opp_ang1)
    return q, s, hint, 5, _geom_fields_answer(
        (opp_ang1, opp_ang2, bod),
        ('(a) Angle BCD (°)', '(b) Angle CDA (°)', '(c) Angle BOD (°)'),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (15 questions)
# ══════════════════════════════════════════════════════════════════════════════

_GEOM_MCQ_BANK = [
    {
        "q": r"Angles on a straight line sum to:",
        "opts": ["A  180°", "B  360°", "C  90°", "D  270°"],
        "ans": "A",
        "sol": r"Angles on a straight line always add up to 180°.",
    },
    {
        "q": r"Two parallel lines are cut by a transversal. One angle is 65°. What is the alternate interior angle?",
        "opts": ["A  65°", "B  115°", "C  25°", "D  130°"],
        "ans": "A",
        "sol": r"Alternate interior angles (Z-angles) are equal on parallel lines: 65°.",
    },
    {
        "q": r"What is the sum of interior angles of a hexagon?",
        "opts": ["A  720°", "B  540°", "C  900°", "D  1080°"],
        "ans": "A",
        "sol": r"\((6-2) \times 180° = 4 \times 180° = 720°\).",
    },
    {
        "q": r"A regular polygon has an exterior angle of 30°. How many sides does it have?",
        "opts": ["A  12", "B  10", "C  15", "D  8"],
        "ans": "A",
        "sol": r"\(n = 360° \div 30° = 12\).",
    },
    {
        "q": r"O is the centre of a circle. Angle ACB = 38°. What is angle AOB?",
        "opts": ["A  76°", "B  38°", "C  19°", "D  142°"],
        "ans": "A",
        "sol": r"Angle at centre = 2 × angle at circumference: \(2 \times 38° = 76°\).",
    },
    {
        "q": r"ABCD is a cyclic quadrilateral. Angle A = 112°. What is angle C?",
        "opts": ["A  68°", "B  112°", "C  248°", "D  56°"],
        "ans": "A",
        "sol": r"Opposite angles in a cyclic quadrilateral sum to 180°: \(180° - 112° = 68°\).",
    },
    {
        "q": r"AB is a diameter of a circle. C is on the circle. What is angle ACB?",
        "opts": ["A  90°", "B  45°", "C  180°", "D  60°"],
        "ans": "A",
        "sol": r"The angle in a semicircle (subtended by a diameter) is always 90°.",
    },
    {
        "q": r"The interior angle of a regular polygon is 135°. How many sides does it have?",
        "opts": ["A  8", "B  6", "C  10", "D  12"],
        "ans": "A",
        "sol": r"Exterior angle = \(180° - 135° = 45°\). Number of sides = \(360° \div 45° = 8\).",
    },
    {
        "q": r"Two angles are co-interior (allied angles) on parallel lines. One is 72°. What is the other?",
        "opts": ["A  108°", "B  72°", "C  18°", "D  144°"],
        "ans": "A",
        "sol": r"Co-interior angles sum to 180°: \(180° - 72° = 108°\).",
    },
    {
        "q": r"An isosceles triangle has an apex angle of 40°. What is each base angle?",
        "opts": ["A  70°", "B  40°", "C  140°", "D  80°"],
        "ans": "A",
        "sol": r"Base angles are equal: \((180° - 40°) \div 2 = 70°\).",
    },
    {
        "q": r"What is the exterior angle of a regular pentagon?",
        "opts": ["A  72°", "B  108°", "C  60°", "D  54°"],
        "ans": "A",
        "sol": r"\(360° \div 5 = 72°\).",
    },
    {
        "q": r"The tangent from an external point P to a circle touches at A. OA is a radius. What is angle OAP?",
        "opts": ["A  90°", "B  45°", "C  60°", "D  depends on radius"],
        "ans": "A",
        "sol": r"A tangent is always perpendicular to the radius at the point of contact: 90°.",
    },
    {
        "q": r"What is the exterior angle of a triangle that has interior angles 55° and 70°?",
        "opts": ["A  125°", "B  55°", "C  110°", "D  180°"],
        "ans": "A",
        "sol": r"Exterior angle = sum of two non-adjacent interior angles: \(55° + 70° = 125°\).",
    },
    {
        "q": r"Angles P, Q, and R in a triangle satisfy: angle P = 3x, angle Q = 2x, angle R = x. Find angle P.",
        "opts": ["A  90°", "B  60°", "C  30°", "D  120°"],
        "ans": "A",
        "sol": r"\(3x + 2x + x = 180° \Rightarrow 6x = 180° \Rightarrow x = 30°\). Angle P \(= 3 \times 30° = 90°\).",
    },
    {
        "q": r"Two tangents from point P touch a circle at A and B. Angle APB = 50°. What is angle AOB?",
        "opts": ["A  130°", "B  50°", "C  100°", "D  80°"],
        "ans": "A",
        "sol": r"Angles OAP = OBP = 90° (tangent ⊥ radius). Quadrilateral OAPB: \(360° - 50° - 90° - 90° = 130°\).",
    },
]


def geometry_angles_mcq():
    chosen = random.choice(_GEOM_MCQ_BANK)
    q = chosen["q"]
    options = chosen["opts"]
    correct = chosen["ans"]
    s = f"<strong>Answer: {correct}</strong><br><br>{chosen['sol']}"
    hint = chosen["sol"]
    return q, s, hint, 1, options, correct


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_geometry_angles_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _GEOM_MCQ_BANK, procedural_mcq_for('geometry_angles'), 'geometry_angles', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _geom_found_straight_line,
            _geom_found_around_point,
            _geom_found_vertically_opposite,
            _geom_found_triangle_sum,
            _geom_found_isosceles,
            _geom_found_exterior_angle,
            _geom_found_quadrilateral,
            _geom_found_corresponding,
            _geom_found_alternate,
            _geom_found_cointerior,
            _geom_found_polygon_sum,
            _geom_found_regular_exterior,
            _geom_found_complementary,
            _geom_found_equilateral,
            _geom_found_multistep_lines,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _geom_inter_algebraic_straight,
            _geom_inter_algebraic_triangle,
            _geom_inter_regular_polygon_n,
            _geom_inter_complex_parallel,
            _geom_inter_angle_at_centre,
            _geom_inter_angle_semicircle,
            _geom_inter_same_segment,
            _geom_inter_cyclic_quad,
            _geom_inter_tangent_radius,
            _geom_inter_bearing,
            _geom_inter_similar_triangles,
            _geom_inter_polygon_algebra,
            _geom_inter_isosceles_parallel,
            _geom_inter_kite_angles,
            _geom_inter_interior_exterior,
        ]
    elif difficulty == 'difficult':
        pool = [
            _geom_diff_alternate_segment,
            _geom_diff_two_tangents,
            _geom_diff_multi_circle,
            _geom_diff_similar_area,
            _geom_diff_prove_triangle_sum,
            _geom_diff_algebraic_circle,
            _geom_diff_chord_distance,
            _geom_diff_cyclic_quad_proof,
            _geom_diff_regular_polygon_proof,
            _geom_diff_polygon_algebra,
            _geom_diff_reflex_centre,
            _geom_diff_tangent_chord,
            _geom_diff_bearing_complex,
            _geom_diff_inscribed_angles,
            _geom_diff_alternate_segment,   # reuse for pool size
        ]
    else:  # mixed
        found = random.sample([
            _geom_found_straight_line, _geom_found_triangle_sum,
            _geom_found_isosceles, _geom_found_corresponding,
            _geom_found_alternate, _geom_found_polygon_sum,
        ], 4)
        inter = random.sample([
            _geom_inter_algebraic_triangle, _geom_inter_angle_at_centre,
            _geom_inter_cyclic_quad, _geom_inter_similar_triangles,
            _geom_inter_polygon_algebra, _geom_inter_angle_semicircle,
        ], 4)
        diff = random.sample([
            _geom_diff_two_tangents, _geom_diff_chord_distance,
            _geom_diff_polygon_algebra, _geom_diff_prove_triangle_sum,
        ], 2)
        return found + inter + diff

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors exactly)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_geometry_angles(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_geometry_angles_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'geometry_angles',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_geometry_angles_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _geom_problem_from_output(variant(), difficulty)
