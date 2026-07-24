"""
GCSE Maths – Constructions and Loci
15 foundational · 15 intermediate · 18 difficult · 15 MCQ

Covers:
  Basic loci (equidistant from points/lines, fixed distance from point/segment)
  Standard constructions (perp. bisector, angle bisector, 60°, 90°, triangles)
  Combined loci and regions (intersection / union of conditions)
  Scale drawings (length and area)
  Advanced loci (sliding ladder, chord midpoint, Apollonius circle)
  Formal locus proofs using coordinates
"""
import random
import math
from generators.shared.utils import (
    make_problem,
    make_graded_problem,
    graded_answer_number,
    graded_answer_number_pair,
    graded_answer_number_fields,
    proof_steps_answer,
)
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


# ─────────────────────────────────────────────────────────────────────────────
# Procedural helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cl_random_sss():
    """Return three valid SSS side lengths."""
    for _ in range(50):
        a, b = random.randint(4, 10), random.randint(4, 10)
        lo, hi = abs(a - b) + 1, a + b - 1
        if hi >= lo:
            return a, b, random.randint(lo, min(hi, 12))
    return 5, 6, 7


def _cl_right_triple():
    return random.choice([
        (3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (7, 24, 25),
        (9, 12, 15), (12, 16, 20), (15, 20, 25), (20, 21, 29), (9, 40, 41),
    ])


def _cl_right_triple_scaled():
    a, b, c = _cl_right_triple()
    k = random.randint(1, 4)
    return a * k, b * k, c * k


def _cl_random_chord():
    """Return (radius, chord_length, midpoint_distance)."""
    for _ in range(100):
        R = random.randint(5, 20)
        hc = random.randint(2, R - 1)
        d_sq = R ** 2 - hc ** 2
        if d_sq <= 0:
            continue
        d = int(d_sq ** 0.5)
        if d > 0:
            return R, 2 * hc, d if d * d == d_sq else round(d_sq ** 0.5, 1)
    return 5, 8, 3


def _cl_scale_length():
    unit_out = random.choice(['m', 'km'])
    if unit_out == 'm':
        scale = random.choice([100, 200, 250, 500, 1000, 2000, 5000])
        map_d = round(random.uniform(1.5, 8.0), 1)
        actual_cm = map_d * scale
        actual_final = round(actual_cm / 100, 1)
    else:
        scale = random.choice([10000, 25000, 50000, 100000, 200000])
        map_d = round(random.uniform(1.2, 6.0), 1)
        actual_cm = map_d * scale
        actual_final = round(actual_cm / 100000, 2)
    return scale, map_d, actual_cm, actual_final, 'cm', unit_out


def _cl_scale_area():
    if random.choice([True, False]):
        scale = random.choice([10000, 25000, 50000, 100000])
        map_cm2 = round(random.uniform(2, 10), 1)
        area_scale = scale ** 2
        actual_cm2 = map_cm2 * area_scale
        return scale, map_cm2, round(actual_cm2 / 1e10, 3), 'km²'
    scale = random.choice([50, 100, 200, 250, 500])
    map_cm2 = round(random.uniform(2, 12), 1)
    area_scale = scale ** 2
    return scale, map_cm2, round(map_cm2 * area_scale), 'cm²'


# ─────────────────────────────────────────────────────────────────────────────
# SVG helpers
# ─────────────────────────────────────────────────────────────────────────────

def _perp_bisect_svg(w=220, h=188):
    """Segment AB — setup for locus / construction questions (no construction shown)."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:inline-block;margin:4px;vertical-align:middle;">'
        '<line x1="10" y1="94" x2="210" y2="94" stroke="#555" stroke-width="2"/>'
        '<circle cx="25" cy="94" r="4" fill="#1a6fa8"/>'
        '<circle cx="195" cy="94" r="4" fill="#1a6fa8"/>'
        '<text x="8" y="87" font-size="13" fill="#1a6fa8" font-weight="bold">A</text>'
        '<text x="198" y="87" font-size="13" fill="#1a6fa8" font-weight="bold">B</text>'
        '<text x="110" y="130" font-size="10" fill="#555" text-anchor="middle">Points A and B</text>'
        '</svg>'
    )


def _angle_bisect_svg(w=220, h=172):
    """Angle at B — setup only (no bisector construction shown)."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:inline-block;margin:4px;vertical-align:middle;">'
        '<circle cx="28" cy="148" r="4" fill="#333"/>'
        '<text x="5" y="161" font-size="13" fill="#333" font-weight="bold">B</text>'
        '<line x1="28" y1="148" x2="158" y2="15" stroke="#555" stroke-width="2"/>'
        '<text x="160" y="14" font-size="13" fill="#333" font-weight="bold">A</text>'
        '<line x1="28" y1="148" x2="215" y2="148" stroke="#555" stroke-width="2"/>'
        '<text x="215" y="161" font-size="13" fill="#333" font-weight="bold">C</text>'
        '<text x="110" y="8" font-size="10" fill="#555" text-anchor="middle">Two lines meeting at B</text>'
        '</svg>'
    )


def _circle_svg(r_label="r cm", w=180, h=172):
    """Fixed point P — setup only (locus not drawn)."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:inline-block;margin:4px;vertical-align:middle;">'
        '<circle cx="90" cy="86" r="4" fill="#1a6fa8"/>'
        '<text x="95" y="82" font-size="13" fill="#1a6fa8" font-weight="bold">P</text>'
        '<text x="90" y="130" font-size="10" fill="#555" text-anchor="middle">Fixed point P</text>'
        '</svg>'
    )


def _stadium_svg(w=265, h=140):
    """Segment AB — setup only (stadium locus not drawn)."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:inline-block;margin:4px;vertical-align:middle;">'
        '<line x1="62" y1="70" x2="202" y2="70" stroke="#555" stroke-width="2.5"/>'
        '<circle cx="62" cy="70" r="4" fill="#a13544"/>'
        '<circle cx="202" cy="70" r="4" fill="#a13544"/>'
        '<text x="50" y="73" font-size="12" fill="#a13544" font-weight="bold">A</text>'
        '<text x="204" y="73" font-size="12" fill="#a13544" font-weight="bold">B</text>'
        '<text x="132" y="110" font-size="10" fill="#555" text-anchor="middle">Line segment AB</text>'
        '</svg>'
    )


def _half_plane_svg(w=230, h=155):
    """Points A and B — setup only (no region shaded)."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:inline-block;margin:4px;vertical-align:middle;">'
        '<line x1="10" y1="77" x2="220" y2="77" stroke="#555" stroke-width="2"/>'
        '<circle cx="42" cy="77" r="6" fill="#1a6fa8"/>'
        '<circle cx="192" cy="77" r="6" fill="#a13544"/>'
        '<text x="44" y="70" font-size="13" fill="#1a6fa8" font-weight="bold">A</text>'
        '<text x="194" y="70" font-size="13" fill="#a13544" font-weight="bold">B</text>'
        '<text x="117" y="132" font-size="10" fill="#555" text-anchor="middle">Points A and B</text>'
        '</svg>'
    )


def _lens_svg(w=240, h=168):
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:inline-block;margin:4px;vertical-align:middle;">'
        '<circle cx="72" cy="84" r="68" fill="none" stroke="#1a6fa8" stroke-width="2" stroke-dasharray="5,3"/>'
        '<circle cx="168" cy="84" r="68" fill="none" stroke="#a13544" stroke-width="2" stroke-dasharray="5,3"/>'
        '<circle cx="72" cy="84" r="4" fill="#1a6fa8"/>'
        '<circle cx="168" cy="84" r="4" fill="#a13544"/>'
        '<text x="52" y="81" font-size="13" fill="#1a6fa8" font-weight="bold">A</text>'
        '<text x="172" y="81" font-size="13" fill="#a13544" font-weight="bold">B</text>'
        '<text x="120" y="156" font-size="10" fill="#555" text-anchor="middle">Circles centred at A and B</text>'
        '</svg>'
    )


def _garden_loci_svg(w=300, h=215):
    """Rectangular garden PQRS — setup only (no loci drawn; students describe them in parts a–c)."""
    # P top-left, Q top-right, R bottom-right, S bottom-left; 12 m × 9 m (200×150 px)
    px, py, qw, qh = 50, 48, 200, 150
    qx, qy = px + qw, py
    rx, ry = px + qw, py + qh
    sx, sy = px, py + qh
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:block;margin:8px auto;" '
        f'role="img" aria-label="Rectangular garden PQRS, 12 metres by 9 metres">'
        f'<rect x="{px}" y="{py}" width="{qw}" height="{qh}" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>'
        # Corner labels (outside the rectangle)
        f'<text x="{px-14}" y="{py+5}" font-size="13" fill="#1a6fa8" font-weight="bold">P</text>'
        f'<text x="{qx+8}" y="{qy+5}" font-size="13" fill="#1a6fa8" font-weight="bold">Q</text>'
        f'<text x="{rx+8}" y="{ry+5}" font-size="13" fill="#1a6fa8" font-weight="bold">R</text>'
        f'<text x="{sx-14}" y="{sy+5}" font-size="13" fill="#1a6fa8" font-weight="bold">S</text>'
        # Side lengths on the corresponding edges
        f'<text x="{px+qw//2}" y="{py-10}" font-size="12" fill="#555" text-anchor="middle">PQ = 12 m</text>'
        f'<text x="{qx+22}" y="{py+qh//2+4}" font-size="12" fill="#555" text-anchor="middle">QR = 9 m</text>'
        '</svg>'
    )


def _treasure_loci_svg(d_ab=80, w=260, h=175):
    """Markers A, B and C — setup only (loci not drawn)."""
    ax, bx = 40, 40 + d_ab
    mx = (ax + bx) // 2
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:block;margin:8px auto;">'
        f'<line x1="{ax}" y1="120" x2="{bx}" y2="120" stroke="#555" stroke-width="2"/>'
        f'<circle cx="{ax}" cy="120" r="4" fill="#1a6fa8"/>'
        f'<circle cx="{bx}" cy="120" r="4" fill="#1a6fa8"/>'
        f'<text x="{ax-12}" y="112" font-size="12" fill="#1a6fa8" font-weight="bold">A</text>'
        f'<text x="{bx+4}" y="112" font-size="12" fill="#1a6fa8" font-weight="bold">B</text>'
        f'<circle cx="{mx}" cy="75" r="4" fill="#8a5300"/>'
        f'<text x="{mx+6}" y="72" font-size="11" fill="#8a5300" font-weight="bold">C</text>'
        '<text x="130" y="155" font-size="10" fill="#555" text-anchor="middle">Markers A, B and C</text>'
        '</svg>'
    )


def _triangle_centres_svg(w=340, h=248, ab_label="8 cm", bc_label="6 cm", ac_label="10 cm"):
    """Right triangle ABC — setup only (centres and loci not drawn)."""
    bx, by, ax, ay, cx, cy = 45, 145, 45, 55, 105, 145
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 240 175" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:block;margin:8px auto;">'
        f'<line x1="{bx}" y1="{by}" x2="{cx}" y2="{cy}" stroke="#1a6fa8" stroke-width="2"/>'
        f'<line x1="{bx}" y1="{by}" x2="{ax}" y2="{ay}" stroke="#059669" stroke-width="2"/>'
        f'<line x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke="#a13544" stroke-width="2.5"/>'
        '<polyline points="54,145 54,136 45,136" fill="none" stroke="#333" stroke-width="1.5"/>'
        f'<text x="{bx+30}" y="162" font-size="11" fill="#1a6fa8" text-anchor="middle">{bc_label}</text>'
        f'<text x="28" y="102" font-size="11" fill="#059669">{ab_label}</text>'
        f'<text x="88" y="88" font-size="11" fill="#a13544">{ac_label}</text>'
        f'<text x="{bx-8}" y="158" font-size="11" fill="#333" font-weight="bold">B</text>'
        f'<text x="{ax-14}" y="{ay+4}" font-size="11" fill="#333" font-weight="bold">A</text>'
        f'<text x="{cx+4}" y="{cy+4}" font-size="11" fill="#333" font-weight="bold">C</text>'
        '</svg>'
    )


def _sixty_deg_svg(w=210, h=148):
    """Starting setup for 60° angle construction at A on line AB (no construction shown)."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;display:inline-block;margin:4px;vertical-align:middle;">'
        '<line x1="10" y1="115" x2="200" y2="115" stroke="#555" stroke-width="2"/>'
        '<circle cx="22" cy="115" r="4" fill="#1a6fa8"/>'
        '<text x="8" y="108" font-size="13" fill="#1a6fa8" font-weight="bold">A</text>'
        '<text x="188" y="108" font-size="13" fill="#555" font-weight="bold">B</text>'
        '<text x="105" y="138" font-size="10" fill="#555" text-anchor="middle">Line AB — construct a 60° angle at A</text>'
        '</svg>'
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _cl_mcq_return(q, s, hint, marks, correct, distractors):
    """Return a 6-tuple MCQ for constructions/loci conceptual questions."""
    choices = [correct] + list(distractors[:3])
    random.shuffle(choices)
    letters = 'ABCD'
    correct_letter = letters[choices.index(correct)]
    opts = [f"{letters[i]}  {choices[i]}" for i in range(4)]
    return q, s, hint, marks, opts, correct_letter


def _cl_steps_answer(steps, distractors, *, format_hint='Put the construction steps in the correct order'):
    bank = [{'id': f's{i + 1}', 'text': text} for i, text in enumerate(steps)]
    for j, text in enumerate(distractors):
        bank.append({'id': f'd{j + 1}', 'text': text})
    random.shuffle(bank)
    required = tuple(f's{i + 1}' for i in range(len(steps)))
    return proof_steps_answer(
        required,
        bank,
        order_matters=True,
        format_hint=format_hint,
    )


def _cl_f1_equidistant_two_points():
    d = random.randint(3, 35)
    svg = _perp_bisect_svg()
    q = (f"Points A and B are {d} cm apart. "
         f"Describe the locus of all points that are equidistant from A and B.<br>{svg}")
    s = ("The locus is the <strong>perpendicular bisector of AB</strong> — a straight line "
         "that passes through the midpoint of AB at right angles (90°) to AB. "
         "Every point on this line is exactly equal in distance from A and B.")
    hint = "The locus equidistant from two fixed points is the perpendicular bisector of the line joining them."
    return _cl_mcq_return(
        q, s, hint, 2,
        "The perpendicular bisector of AB",
        [
            "A circle with diameter AB",
            "Two parallel lines each d cm from AB",
            "The midpoint of AB only",
        ],
    )


def _cl_f2_fixed_distance_point():
    r = random.randint(2, 35)
    svg = _circle_svg(f"{r} cm")
    q = (f"Describe the locus of all points that are exactly {r} cm from a fixed point P.<br>{svg}")
    s = (f"The locus is a <strong>circle with centre P and radius {r} cm</strong>. "
         "Every point on this circle is exactly the given distance from P.")
    hint = "A fixed distance from a fixed point → circle."
    return _cl_mcq_return(
        q, s, hint, 2,
        f"A circle with centre P and radius {r} cm",
        [
            f"Two parallel lines each {r} cm from P",
            f"A square of side {r} cm centred at P",
            f"A straight line {r} cm long through P",
        ],
    )


def _cl_f3_equidistant_two_lines():
    angle = random.randint(50, 130)
    svg = _angle_bisect_svg()
    q = (f"Two straight lines meet at point B, forming an angle of {angle}°. "
         f"Describe the locus of all points equidistant from both lines.<br>{svg}")
    s = ("The locus consists of the <strong>two angle bisectors</strong> of the angles formed at B. "
         f"One bisector passes through the {angle}° angle and the other through the supplementary angle. "
         "Every point on an angle bisector is equidistant from the two lines.")
    hint = "Equidistant from two intersecting lines → the angle bisector(s)."
    return _cl_mcq_return(
        q, s, hint, 2,
        "The two angle bisectors of the angles at B",
        [
            "The perpendicular bisector of the angle at B",
            f"A circle of radius {angle} cm centred at B",
            "A single line parallel to one of the arms",
        ],
    )


def _cl_f4_fixed_distance_segment():
    d = random.randint(2, 6)
    seg = random.randint(5, 12)
    svg = _stadium_svg()
    q = (f"A line segment AB has length {seg} cm. "
         f"Describe the locus of all points exactly {d} cm from the nearest point on AB.<br>{svg}")
    s = (f"The locus is a <strong>stadium shape</strong> (also called a discorectangle): "
         f"two straight lines parallel to AB, each {d} cm away (one on each side), "
         f"joined at each end by a semicircle of radius {d} cm centred at A and B respectively.")
    hint = "Fixed distance from a segment: two parallel lines joined by semicircles at the ends."
    correct = (
        f"A stadium shape: two lines parallel to AB, {d} cm away, "
        f"with semicircles of radius {d} cm at A and B"
    )
    distractors = [
        f"A circle of radius {d} cm centred at the midpoint of AB",
        f"Two parallel lines only, each {d} cm from AB (no curves at the ends)",
        f"A rectangle {seg} cm by {2 * d} cm",
    ]
    return _cl_mcq_return(q, s, hint, 2, correct, distractors)


def _cl_f5_perp_bisector_property():
    pts = random.choice([
        ("P", "Q", "R"), ("X", "Y", "Z"), ("M", "N", "L"),
        ("A", "B", "C"), ("D", "E", "F"), ("G", "H", "J"),
        ("K", "L", "M"), ("S", "T", "U"), ("V", "W", "X"),
    ])
    dist = random.randint(3, 12)
    P, Q, R = pts
    q = (f"Points {P} and {Q} lie on the perpendicular bisector of segment AB (where AB = {dist} cm). "
         f"Point {R} does NOT lie on the perpendicular bisector of AB. "
         f"What can you say about {P}A and {P}B? What about {R}A and {R}B?")
    s = (f"Since {P} is on the perpendicular bisector: <strong>{P}A = {P}B</strong>.<br>"
         f"Since {Q} is also on the perpendicular bisector: <strong>{Q}A = {Q}B</strong>.<br>"
         f"Since {R} is NOT on the perpendicular bisector: <strong>{R}A ≠ {R}B</strong>.")
    hint = "Any point on the perpendicular bisector of AB is equidistant from A and B."
    correct = f"{P}A = {P}B and {Q}A = {Q}B, but {R}A ≠ {R}B"
    distractors = [
        f"{P}A = {P}B only; {Q}A ≠ {Q}B",
        f"{P}A ≠ {P}B and {R}A = {R}B",
        "Every point is equidistant from A and B",
    ]
    return _cl_mcq_return(q, s, hint, 2, correct, distractors)


def _cl_f6_angle_bisector_property():
    angle = random.randint(40, 120)
    q = (f"The angle bisector of angle BAC (where angle BAC = {angle}°) is drawn. "
         f"Point P lies on this bisector. "
         f"What is the relationship between P's distance from line AB and from line AC?")
    s = ("Any point on the angle bisector is equidistant from the two arms of the angle. "
         f"Therefore, P's perpendicular distance from AB <strong>equals</strong> P's perpendicular distance from AC.")
    hint = "Any point on an angle bisector is equidistant from the two lines forming the angle."
    return _cl_mcq_return(
        q, s, hint, 2,
        "The perpendicular distance from AB equals the perpendicular distance from AC",
        [
            "The distance from AB is greater than the distance from AC",
            "The distance from AB is less than the distance from AC",
            "P must lie at vertex A",
        ],
    )


def _cl_f7_rolling_wheel():
    r = random.randint(2, 25)
    road = random.choice(['road', 'path', 'track', 'pavement', 'cycle lane'])
    q = (f"A wheel of radius {r} cm rolls along a flat, straight {road}. "
         f"Describe the locus traced by the centre of the wheel.")
    s = (f"The centre of the wheel stays exactly {r} cm above the {road} at all times. "
         f"The locus is a <strong>straight line parallel to the {road}, at height {r} cm</strong>.")
    hint = "The centre of a rolling circle stays at a fixed height = radius above the surface."
    return _cl_mcq_return(
        q, s, hint, 2,
        f"A straight line parallel to the {road}, at height {r} cm",
        [
            f"A circle of radius {r} cm",
            "A wavy curve (cycloid)",
            f"The {road} surface itself",
        ],
    )


def _cl_f8_closer_to_A():
    d = random.randint(3, 30)
    svg = _half_plane_svg()
    q = (f"Points A and B are {d} cm apart. "
         f"Describe and sketch the region of all points that are closer to A than to B.<br>{svg}")
    s = ("The region is all points on <strong>A's side of the perpendicular bisector of AB</strong>. "
         "The boundary is the perpendicular bisector itself (where PA = PB). "
         "The region is an infinite half-plane.")
    hint = "Closer to A → on A's side of the perpendicular bisector of AB."
    return _cl_mcq_return(
        q, s, hint, 2,
        "All points on A's side of the perpendicular bisector of AB",
        [
            "All points on B's side of the perpendicular bisector of AB",
            "Only points on the perpendicular bisector of AB",
            f"A circle of radius {d} cm centred at A",
        ],
    )


def _cl_f9_construct_perp_bisector_steps():
    q = "List the four steps to construct the perpendicular bisector of a line segment AB using only a ruler and compasses."
    s = ("<strong>Step 1:</strong> Open the compasses to more than half the length of AB.<br>"
         "<strong>Step 2:</strong> Place the compass point on A and draw an arc above and below AB.<br>"
         "<strong>Step 3:</strong> Without changing the radius, place the point on B and draw arcs above and below AB, crossing the first arcs.<br>"
         "<strong>Step 4:</strong> Join the two intersection points with a straight line. This line is the perpendicular bisector of AB.")
    hint = "Keep the same compass radius for both arcs. The arcs must cross on both sides of AB."
    return q, s, hint, 3, _cl_steps_answer(
        (
            "Open the compasses to more than half the length of AB.",
            "Place the compass point on A and draw an arc above and below AB.",
            "Without changing the radius, place the point on B and draw arcs above and below AB, crossing the first arcs.",
            "Join the two intersection points with a straight line.",
        ),
        (
            "Place the compass on the midpoint of AB and draw a circle.",
            "Use a protractor to measure 90° at the midpoint of AB.",
            "Draw one arc from A only, then join A to the arc crossing.",
            "Measure AB with a ruler and mark the midpoint with a dot only.",
        ),
    )


def _cl_f10_construct_angle_bisector_steps():
    q = "List the steps to construct the angle bisector of angle ABC using only a ruler and compasses."
    s = ("<strong>Step 1:</strong> Place the compass point on B and draw an arc that crosses both arms BA and BC.<br>"
         "<strong>Step 2:</strong> Label the crossings X (on BA) and Y (on BC).<br>"
         "<strong>Step 3:</strong> Place the compass on X and draw an arc inside the angle.<br>"
         "<strong>Step 4:</strong> Using the same radius, place the compass on Y and draw an arc crossing the previous one; label the crossing Z.<br>"
         "<strong>Step 5:</strong> Draw the ray BZ — this is the angle bisector of angle ABC.")
    hint = "Use equal radii from both arms' crossing points; join B to their intersection Z."
    bank = [
        {
            'id': 's1',
            'text': 'Place the compass point on B and draw an arc that crosses both arms BA and BC.',
        },
        {
            'id': 's2',
            'text': 'Label the crossings X (on BA) and Y (on BC).',
        },
        {
            'id': 's3',
            'text': 'Place the compass on X and draw an arc inside the angle.',
        },
        {
            'id': 's4',
            'text': (
                'Using the same radius, place the compass on Y and draw an arc '
                'crossing the previous one; label the crossing Z.'
            ),
        },
        {
            'id': 's5',
            'text': 'Draw the ray BZ — this is the angle bisector of angle ABC.',
        },
        {
            'id': 'd1',
            'text': 'Place the compass on A and draw an arc through B.',
        },
        {
            'id': 'd2',
            'text': 'Use a protractor to measure angle ABC and divide by 2.',
        },
        {
            'id': 'd3',
            'text': 'Place the compass on B and draw an arc that crosses only arm BA.',
        },
        {
            'id': 'd4',
            'text': 'Join X and Y with a straight line.',
        },
    ]
    random.shuffle(bank)
    return q, s, hint, 3, proof_steps_answer(
        ('s1', 's2', 's3', 's4', 's5'),
        bank,
        order_matters=True,
        format_hint='Put the construction steps in the correct order',
    )


def _cl_f11_triangle_tools():
    a, b, c = _cl_random_sss()
    q = (f"You are given three sides of a triangle: {a} cm, {b} cm, {c} cm. "
         f"What tools do you need to construct the triangle accurately? "
         f"You do NOT need to use a protractor — explain why.")
    s = ("You need a <strong>ruler and a pair of compasses</strong>. "
         "A protractor is not needed because all three sides are given (SSS). "
         "Use compasses to draw arcs of the correct radii from two ends of the base; "
         "the third vertex is where the arcs intersect.")
    hint = "SSS construction uses only ruler + compasses. Arcs from two vertices give the third."
    return _cl_mcq_return(
        q, s, hint, 2,
        "A ruler and a pair of compasses",
        [
            "A ruler and a protractor",
            "A ruler only",
            "A protractor and compasses",
        ],
    )


def _cl_f12_locus_around_rectangle():
    w_r = random.randint(5, 14)
    h_r = random.randint(4, 10)
    d = random.randint(2, 5)
    q = (f"A point P moves so that it is always exactly {d} cm from the nearest point on "
         f"a {w_r} cm × {h_r} cm rectangle. Describe the shape of the complete locus.")
    s = (f"The locus is a <strong>rounded rectangle</strong>: straight sections parallel to each side of the "
         f"rectangle (displaced outward by {d} cm), joined at each corner by a quarter-circle of radius {d} cm. "
         f"The total dimensions are {w_r + 2*d} cm × {h_r + 2*d} cm with rounded corners.")
    hint = "The locus hugs the rectangle's outline at a fixed distance, with circular arcs at the corners."
    return _cl_mcq_return(
        q, s, hint, 3,
        f"A rounded rectangle: sides parallel to the rectangle, {d} cm out, with quarter-circle corners of radius {d} cm",
        [
            f"A larger rectangle {w_r + 2*d} cm × {h_r + 2*d} cm with sharp corners",
            f"A circle of radius {d} cm centred at the rectangle's centre",
            f"Four separate circles of radius {d} cm, one at each corner only",
        ],
    )


def _cl_f13_bisector_right_angle():
    q = ("In rectangle ABCD, a point P is equidistant from sides AB and AD. "
         "On which line does P lie? Describe this line geometrically.")
    s = ("Since angle DAB = 90°, the angle bisector of angle DAB makes a 45° angle with both sides. "
         "P lies on the <strong>angle bisector of angle DAB</strong>, "
         "which is a line at 45° to both AB and AD, passing through vertex A.")
    hint = "Equidistant from two sides of an angle → on the angle bisector."
    return _cl_mcq_return(
        q, s, hint, 2,
        "The angle bisector of angle DAB (a 45° line through A)",
        [
            "The perpendicular bisector of diagonal BD",
            "The diagonal AC",
            "A line parallel to AB through A",
        ],
    )


def _cl_f14_two_circle_region():
    d_AB = random.randint(6, 14)
    r1 = random.randint(3, 8)
    r2 = random.randint(3, 8)
    svg = _lens_svg()
    q = (f"Points A and B are {d_AB} cm apart. "
         f"Shade the region of all points that are within {r1} cm of A AND within {r2} cm of B.<br>{svg}")
    s = (f"Draw circle A (radius {r1} cm) and circle B (radius {r2} cm). "
         f"The required region is the <strong>intersection of the two circles</strong> — "
         f"the lens-shaped (vesica) region where the two circles overlap. "
         f"{'The circles do overlap since ' + str(r1) + ' + ' + str(r2) + ' = ' + str(r1+r2) + ' > ' + str(d_AB) + '.' if r1+r2 > d_AB else 'Check whether the circles actually intersect.'}")
    hint = "Draw both circles and shade the overlapping region."
    return _cl_mcq_return(
        q, s, hint, 3,
        "The intersection (lens-shaped overlap) of the two circles",
        [
            "The union of both full circles",
            "The perpendicular bisector of AB only",
            "The region outside both circles",
        ],
    )


def _cl_f15_scale_drawing_length():
    scale, map_d, actual_cm, actual_final, unit_in, unit_out = _cl_scale_length()
    divisor = 100 if unit_out == "m" else 100000
    q = (f"A scale drawing uses a scale of 1 : {scale:,}. "
         f"A wall measures {map_d} cm on the drawing. "
         f"Find the actual length of the wall in {unit_out}.")
    s = (f"Actual length = {map_d} × {scale:,} = {actual_cm:,.0f} {unit_in}<br>"
         f"Convert to {unit_out}: {actual_cm:,.0f} ÷ {divisor:,} = <strong>{actual_final} {unit_out}</strong>")
    return q, s, f"Multiply map distance by scale factor, then convert units.", 2, graded_answer_number(actual_final)


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _cl_i1_combined_loci():
    d_AB = random.randint(6, 14)
    r = random.randint(4, 10)
    svg = _lens_svg()
    q = (f"Points A and B are {d_AB} cm apart. Describe and sketch the region satisfying BOTH:<br>"
         f"(i) Closer to B than to A, AND<br>"
         f"(ii) Less than {r} cm from A.<br>{svg}")
    s = (f"(i) Closer to B than A → on B's side of the perpendicular bisector of AB.<br>"
         f"(ii) Less than {r} cm from A → inside a circle of radius {r} cm centred at A.<br>"
         f"The required region is <strong>the part of the circle (centre A, radius {r} cm) "
         f"that lies on B's side of the perpendicular bisector of AB</strong>.")
    hint = "Draw both loci. The answer is their intersection (AND means the overlap)."
    return _cl_mcq_return(
        q, s, hint, 4,
        f"The part of the circle (centre A, radius {r} cm) on B's side of the perpendicular bisector of AB",
        [
            f"The full circle of radius {r} cm centred at A",
            "All points on B's side of the perpendicular bisector of AB",
            f"The part of the circle (centre A, radius {r} cm) on A's side of the perpendicular bisector",
        ],
    )


def _cl_i2_equilateral_triangle():
    side = random.randint(3, 30)
    q = (f"Describe the steps to construct an equilateral triangle with side length {side} cm "
         f"using only a ruler and compasses.")
    s = (f"<strong>Step 1:</strong> Draw a line segment AB = {side} cm.<br>"
         f"<strong>Step 2:</strong> Set the compasses to {side} cm.<br>"
         f"<strong>Step 3:</strong> Draw an arc from A (above AB).<br>"
         f"<strong>Step 4:</strong> Without changing the radius, draw an arc from B (above AB).<br>"
         f"<strong>Step 5:</strong> Mark point C where the arcs intersect.<br>"
         f"<strong>Step 6:</strong> Join A to C and B to C.<br>"
         f"Triangle ABC is equilateral with all sides <strong>{side} cm</strong>.")
    hint = "Keep compass set to the side length. Both arcs from A and B with the same radius give C."
    return q, s, hint, 4, _cl_steps_answer(
        (
            f"Draw a line segment AB = {side} cm.",
            f"Set the compasses to {side} cm.",
            "Draw an arc from A (above AB).",
            "Without changing the radius, draw an arc from B (above AB).",
            "Mark point C where the arcs intersect.",
            "Join A to C and B to C.",
        ),
        (
            "Use a protractor to measure 60° at A and B.",
            f"Draw a circle of radius {side} cm centred at the midpoint of AB.",
            "Draw one arc from A only, then join A to any point on the arc.",
            "Measure three equal sides with a ruler without using compasses.",
        ),
    )


def _cl_i3_ladder_midpoint():
    L = random.randint(4, 30)
    half_L = L / 2
    q = (f"A {L} m ladder has its foot on level ground and leans against a vertical wall. "
         f"As the foot slides away from the wall, describe the locus of the midpoint M of the ladder.")
    s = (f"Let the foot be at (a, 0) and the top at (0, b). Since the ladder is {L} m: a² + b² = {L**2}.<br>"
         f"The midpoint M = (a/2, b/2). Let x = a/2, y = b/2.<br>"
         f"Then a = 2x, b = 2y, so (2x)² + (2y)² = {L**2} → x² + y² = {L**2 // 4}.<br>"
         f"The locus is a <strong>quarter-circle of radius {half_L} m centred at the corner</strong> "
         f"(where the wall meets the floor), sweeping from the floor to the wall.")
    hint = "Set up coordinates with the corner at origin. The midpoint's coordinates satisfy a circle equation."
    half_display = int(half_L) if half_L == int(half_L) else half_L
    return _cl_mcq_return(
        q, s, hint, 4,
        f"A quarter-circle of radius {half_display} m centred at the corner (where wall meets floor)",
        [
            f"A full circle of radius {L} m centred at the corner",
            f"A straight line parallel to the floor at height {half_display} m",
            f"A semicircle of radius {L} m",
        ],
    )


def _cl_i4_semicircle_locus():
    q = ("AB is the diameter of a circle. Point P moves so that angle APB = 90°. "
         "Describe the complete locus of P.")
    s = ("By the angle in a semicircle theorem (converse), any point P on a circle with diameter AB "
         "makes angle APB = 90°. "
         "Therefore the locus of P is <strong>the full circle with diameter AB</strong> "
         "(excluding points A and B themselves, where the angle is undefined).")
    hint = "Angle in semicircle theorem: if angle APB = 90°, P lies on the circle with diameter AB."
    return _cl_mcq_return(
        q, s, hint, 3,
        "The full circle with diameter AB (excluding A and B)",
        [
            "The semicircle above diameter AB only",
            "The perpendicular bisector of AB",
            "Two parallel lines through A and B",
        ],
    )


def _cl_i5_treasure_hunt():
    d_AB = random.randint(5, 12)
    r_C = random.randint(2, 6)
    d_MC = random.randint(2, 5)
    # C is on the perp bisector, d_MC above midpoint
    # Circle from C intersects perp bisector if r_C > 0 (always)
    # Two intersections if r_C > 0 (always two, since C is on the perp bisector line)
    q = (f"Treasure is buried such that:<br>"
         f"(i) It is equidistant from points A and B ({d_AB} cm apart), AND<br>"
         f"(ii) It is exactly {r_C} cm from point C, where C is on the perpendicular bisector "
         f"of AB, {d_MC} cm from the midpoint M of AB.<br>"
         f"How many possible locations are there? Explain your reasoning.")
    # Check: P on perp bisector AND at distance r_C from C.
    # On perp bisector (x=0 say, perp bisector is the y-axis), C=(0, d_MC).
    # Circle: x²+(y-d_MC)²=r_C². On perp bisector x=0: (y-d_MC)²=r_C² → two solutions y=d_MC±r_C.
    n_locations = 2
    s = (f"Condition (i) means P must lie on the <strong>perpendicular bisector of AB</strong>.<br>"
         f"Condition (ii) means P lies on a circle of radius {r_C} cm centred at C.<br>"
         f"C lies on the perpendicular bisector, so the circle crosses the perpendicular bisector at "
         f"{r_C} cm above C and {r_C} cm below C — giving "
         f"<strong>{n_locations} possible locations</strong> for the treasure.")
    return q, s, "Each condition gives a locus; count how many times they intersect.", 4, graded_answer_number(n_locations)


def _cl_i6_perp_from_external_point():
    q = ("Describe the steps to construct the perpendicular from external point P to line l "
         "(where P is not on l), using only a ruler and compasses.")
    s = ("<strong>Step 1:</strong> Place the compass point on P and draw an arc that crosses line l at two points; label them X and Y.<br>"
         "<strong>Step 2:</strong> Open the compass to more than half of XY.<br>"
         "<strong>Step 3:</strong> Draw an arc from X below the line.<br>"
         "<strong>Step 4:</strong> Without changing radius, draw an arc from Y below the line, crossing the previous arc at Q.<br>"
         "<strong>Step 5:</strong> Draw the line PQ. The foot of the perpendicular is where PQ meets l.<br>"
         "<strong>PQ is perpendicular to l.</strong>")
    hint = "The two arcs from X and Y (equal radii) locate Q on the far side of l from P."
    return q, s, hint, 4, _cl_steps_answer(
        (
            "Place the compass point on P and draw an arc that crosses line l at two points; label them X and Y.",
            "Open the compass to more than half of XY.",
            "Draw an arc from X below the line.",
            "Without changing radius, draw an arc from Y below the line, crossing the previous arc at Q.",
            "Draw the line PQ.",
        ),
        (
            "Use a protractor at P to measure 90° to line l.",
            "Draw one arc from P and join P to the first crossing on l.",
            "Bisect segment XY with a ruler only, without compasses.",
            "Draw a circle centred at P through l.",
        ),
    )


def _cl_i7_triangle_sss_steps():
    PQ, QR, PR = _cl_random_sss()
    q = (f"Describe the steps to construct triangle PQR where PQ = {PQ} cm, QR = {QR} cm, PR = {PR} cm.")
    s = (f"<strong>Step 1:</strong> Draw PQ = {PQ} cm with a ruler.<br>"
         f"<strong>Step 2:</strong> Set compasses to {PR} cm. Draw an arc centred at P.<br>"
         f"<strong>Step 3:</strong> Set compasses to {QR} cm. Draw an arc centred at Q, crossing the previous arc at R.<br>"
         f"<strong>Step 4:</strong> Join P to R and Q to R.<br>"
         f"Triangle PQR has sides <strong>PQ = {PQ} cm, QR = {QR} cm, PR = {PR} cm</strong>.")
    hint = "Draw the base, then use compasses to locate the third vertex where two arcs intersect."
    return q, s, hint, 4, _cl_steps_answer(
        (
            f"Draw PQ = {PQ} cm with a ruler.",
            f"Set compasses to {PR} cm. Draw an arc centred at P.",
            f"Set compasses to {QR} cm. Draw an arc centred at Q, crossing the previous arc at R.",
            "Join P to R and Q to R.",
        ),
        (
            f"Use a protractor to mark angles at P and Q.",
            f"Draw one arc of radius {PR} cm from P only, then guess R.",
            "Measure all three sides after drawing a random triangle.",
            f"Draw a circle of radius {PQ} cm centred at P.",
        ),
    )


def _cl_i8_construct_60():
    svg = _sixty_deg_svg()
    q = (f"Describe the steps to construct an angle of exactly 60° at point A on line AB, "
         f"using only a ruler and compasses.<br>{svg}")
    s = ("<strong>Step 1:</strong> Set the compass to any radius r. Place the point on A and draw an arc crossing AB; label the crossing X.<br>"
         "<strong>Step 2:</strong> Without changing r, place the compass on X and draw an arc crossing the first arc; label this crossing Y.<br>"
         "<strong>Step 3:</strong> Draw the ray AY.<br>"
         "Angle YAX = <strong>60°</strong> (since AX = AY = XY = r, so triangle AXY is equilateral).")
    hint = "Both arcs have the same radius r. Triangle AXY is equilateral → angles are all 60°."
    return q, s, hint, 4, _cl_steps_answer(
        (
            "Set the compass to any radius r. Place the point on A and draw an arc crossing AB; label the crossing X.",
            "Without changing r, place the compass on X and draw an arc crossing the first arc; label this crossing Y.",
            "Draw the ray AY.",
        ),
        (
            "Use a protractor to measure 60° at A.",
            "Draw a perpendicular at A, then bisect the 90° angle.",
            "Draw two arcs from A with different radii.",
            "Mark 60° using a ruler by measuring equal segments only.",
        ),
    )


def _cl_i9_perp_at_point_on_line():
    q = ("Describe how to construct a perpendicular to line AB at point P, where P lies on AB.")
    s = ("<strong>Step 1:</strong> Place the compass on P and draw two equal arcs along AB, crossing it at X and Y (equidistant from P).<br>"
         "<strong>Step 2:</strong> Open the compass wider (more than PX).<br>"
         "<strong>Step 3:</strong> Draw arcs from X and Y above the line, crossing each other at Q.<br>"
         "<strong>Step 4:</strong> Draw the line PQ. <strong>PQ ⊥ AB</strong>.")
    hint = "X and Y are equidistant from P; Q is equidistant from X and Y → PQ is the perp. bisector of XY, hence ⊥ AB."
    return q, s, hint, 4, _cl_steps_answer(
        (
            "Place the compass on P and draw two equal arcs along AB, crossing it at X and Y (equidistant from P).",
            "Open the compass wider (more than PX).",
            "Draw arcs from X and Y above the line, crossing each other at Q.",
            "Draw the line PQ.",
        ),
        (
            "Use a protractor at P to measure 90°.",
            "Draw one large arc from P only.",
            "Join P directly to any point above AB without compasses.",
            "Bisect the whole line AB at P using only a ruler.",
        ),
    )


def _cl_i10_scale_bearing():
    scale = random.choice([50000, 100000, 200000])
    dist_km = random.choice([3, 4, 5, 6])
    bearing = random.choice([45, 90, 135, 225, 315])
    map_cm = dist_km * 100000 / scale
    q = (f"A scale drawing uses scale 1 : {scale:,}. "
         f"A ship sails {dist_km} km on a bearing of {bearing:03d}°. "
         f"(i) How long should the line be on the scale drawing? "
         f"(ii) Describe how to draw the line at the correct bearing.")
    s = (f"(i) Length on drawing = {dist_km} km × 1000 m/km × 100 cm/m ÷ {scale:,}<br>"
         f"= {dist_km * 100000:,} ÷ {scale:,} = <strong>{map_cm:.1f} cm</strong><br>"
         f"(ii) Draw a north arrow at the starting point. Use a protractor to measure {bearing:03d}° clockwise "
         f"from north, then draw the line <strong>{map_cm:.1f} cm</strong> in that direction.")
    return q, s, "Convert real distance to cm, divide by scale. Bearings are measured clockwise from north.", 4, graded_answer_number(round(map_cm, 1))


def _cl_i11_circumcircle():
    q = ("Describe how to find the circumscribed circle (circumcircle) of triangle ABC.")
    s = ("<strong>Step 1:</strong> Construct the perpendicular bisector of side AB.<br>"
         "<strong>Step 2:</strong> Construct the perpendicular bisector of side BC.<br>"
         "<strong>Step 3:</strong> Label the intersection of the two bisectors O (the circumcentre). "
         "All three perpendicular bisectors meet at O.<br>"
         "<strong>Step 4:</strong> Set the compass to OA (= OB = OC) and draw the circle centred at O.<br>"
         "The circumcircle <strong>passes through all three vertices</strong>.")
    hint = "The circumcentre is equidistant from all three vertices → on all three perpendicular bisectors."
    return q, s, hint, 4, _cl_steps_answer(
        (
            "Construct the perpendicular bisector of side AB.",
            "Construct the perpendicular bisector of side BC.",
            "Label the intersection of the two bisectors O (the circumcentre).",
            "Set the compass to OA and draw the circle centred at O.",
        ),
        (
            "Construct the angle bisectors of all three angles and use their intersection.",
            "Draw a circle through A only with any radius.",
            "Find the midpoint of BC and draw a circle centred there.",
            "Use a protractor to measure angles at each vertex.",
        ),
    )


def _cl_i12_incircle():
    q = ("Describe how to find the inscribed circle (incircle) of triangle ABC.")
    s = ("<strong>Step 1:</strong> Construct the angle bisector of angle A.<br>"
         "<strong>Step 2:</strong> Construct the angle bisector of angle B.<br>"
         "<strong>Step 3:</strong> Label the intersection I (the incentre). All three bisectors meet at I.<br>"
         "<strong>Step 4:</strong> Construct a perpendicular from I to any side; its length is the inradius r.<br>"
         "<strong>Step 5:</strong> Draw the circle centred at I with radius r.<br>"
         "The incircle <strong>touches (is tangent to) all three sides</strong>.")
    hint = "The incentre is equidistant from all three sides → on all three angle bisectors."
    return q, s, hint, 4, _cl_steps_answer(
        (
            "Construct the angle bisector of angle A.",
            "Construct the angle bisector of angle B.",
            "Label the intersection I (the incentre).",
            "Construct a perpendicular from I to any side; its length is the inradius r.",
            "Draw the circle centred at I with radius r.",
        ),
        (
            "Construct the perpendicular bisectors of all three sides.",
            "Draw a circle through the three vertices.",
            "Use the centroid as the centre of the incircle.",
            "Measure each side with a protractor.",
        ),
    )


def _cl_i13_garden_sprinkler():
    length = random.randint(6, 16)
    width = random.randint(5, 12)
    range_m = random.randint(4, 9)
    q = (f"A rectangular garden ABCD is {length} m × {width} m. "
         f"A sprinkler at corner A can reach any point within {range_m} m. "
         f"Describe the region of the garden watered by the sprinkler.")
    area = round(0.25 * math.pi * range_m**2, 2)
    s = (f"The sprinkler waters the region within {range_m} m of A. "
         f"This is a quarter-circle of radius {range_m} m centred at A (since the garden is a rectangle). "
         f"The area watered ≈ ¼ × π × {range_m}² = <strong>{area} m²</strong> "
         f"(assuming the full quarter-circle fits inside the garden).")
    hint = "Region within range of corner = quarter-circle of that radius at that corner."
    return _cl_mcq_return(
        q, s, hint, 4,
        f"A quarter-circle of radius {range_m} m centred at corner A",
        [
            f"A full circle of radius {range_m} m centred at A",
            f"A semicircle of radius {range_m} m centred at A",
            f"A square of side {range_m} m at corner A",
        ],
    )


def _cl_i14_count_loci_intersections():
    d_AB = random.randint(5, 14)
    r1 = random.randint(2, 8)
    r2 = random.randint(2, 8)
    low, high = abs(r1 - r2), r1 + r2
    if d_AB < low:
        n = 0
        desc = f"{d_AB} < {low}, so one circle is inside the other — no intersection"
    elif d_AB == low:
        n = 1
        desc = f"{d_AB} = {low}, circles touch internally — one point"
    elif d_AB == high:
        n = 1
        desc = f"{d_AB} = {high}, circles touch externally — one point"
    elif d_AB > high:
        n = 0
        desc = f"{d_AB} > {high}, circles are too far apart — no intersection"
    else:
        n = 2
        desc = f"{low} < {d_AB} < {high}, so the circles cross in two places"
    q = (f"A and B are {d_AB} cm apart. Construct the locus of points {r1} cm from A "
         f"and the locus of points {r2} cm from B. "
         f"How many points satisfy BOTH conditions simultaneously?")
    s = (f"Circle A has radius {r1} cm; circle B has radius {r2} cm, centres {d_AB} cm apart.<br>"
         f"Sum of radii = {r1+r2}; difference = {abs(r1-r2)}.<br>"
         f"Since {desc}, there are <strong>{n} point{'s' if n != 1 else ''}</strong> satisfying both conditions.")
    return q, s, "Two circles intersect in 0, 1, or 2 points depending on how the radii and distance compare.", 4, graded_answer_number(n)


def _cl_i15_scale_area():
    scale, map_cm2, actual_final, unit = _cl_scale_area()
    area_scale = scale ** 2
    actual_cm2 = map_cm2 * area_scale
    if unit == "km²":
        conv = actual_cm2 / 1e10
        q = (f"A map has scale 1 : {scale:,}. A field appears as {map_cm2} cm² on the map. "
             f"Find the actual area of the field in {unit}.")
        s = (f"Area scale factor = {scale:,}² = {area_scale:,}<br>"
             f"Actual area = {map_cm2} × {area_scale:,} cm² = {actual_cm2:,.0f} cm²<br>"
             f"= {actual_cm2:,.0f} ÷ 10,000,000,000 = <strong>{actual_final} {unit}</strong>")
    else:
        q = (f"A scale model uses scale 1 : {scale}. A floor appears as {map_cm2} cm² on the model. "
             f"Find the actual floor area in {unit}.")
        s = (f"Area scale factor = {scale}² = {area_scale:,}<br>"
             f"Actual area = {map_cm2} × {area_scale:,} = <strong>{actual_cm2:,.0f} {unit}</strong>")
    return q, s, "Area scales as (linear scale)². Multiply map area by scale².", 4, graded_answer_number(actual_final)


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _cl_d1_locus_proof():
    q = ("Prove that the locus of all points equidistant from A and B is the perpendicular bisector of AB.")
    s = ("Let M be the midpoint of AB. We prove in two directions:<br>"
         "<strong>Part 1 (P on perp bisector → PA = PB):</strong><br>"
         "If P is on the perpendicular bisector, then PM ⊥ AB and AM = MB.<br>"
         "In triangles PAM and PBM: PM = PM (common), AM = BM (M is midpoint), angle PMA = angle PMB = 90°.<br>"
         "By SAS congruence, △PAM ≅ △PBM, so PA = PB. ✓<br>"
         "<strong>Part 2 (PA = PB → P on perp bisector):</strong><br>"
         "If PA = PB, let P' be the foot of the perpendicular from P to AB. "
         "In triangles PAP' and PBP': PP' = PP' (common), PA = PB (given), so by RHS △PAP' ≅ △PBP', giving AP' = BP'. "
         "So P' = M, meaning P lies on the perpendicular through M — the <strong>perpendicular bisector of AB</strong>. ✓")
    return q, s, "Prove both directions: (1) on perp bisector implies equidistant, (2) equidistant implies on perp bisector.", 6

_cl_d1_locus_proof._fixed_stem = True


def _cl_d2_ladder_ellipse():
    L = random.randint(4, 12)
    dist = random.randint(1, L - 1)
    L_sq = L ** 2
    # P is dist m from foot: P = (a*(L-dist)/L, b*dist/L)
    semi_x = L - dist
    semi_y = dist
    q = (f"A {L} m ladder has its foot at point (a, 0) on the ground and its top at (0, b) against a wall, "
         f"where a² + b² = {L_sq}. Point P is {dist} m from the foot of the ladder along its length. "
         f"Show that the locus of P is an ellipse and state its equation.")
    s = (f"The ladder goes from (a, 0) to (0, b). The unit vector along the ladder is (−a/{L}, b/{L}).<br>"
         f"P is {dist} m from (a, 0): P = (a − {dist}a/{L}, {dist}b/{L}) = ({semi_x}a/{L}, {dist}b/{L}).<br>"
         f"Let x = {semi_x}a/{L}, y = {dist}b/{L}, so a = {L}x/{semi_x} and b = {L}y/{dist}.<br>"
         f"Substituting into a² + b² = {L_sq}: ({L}x/{semi_x})² + ({L}y/{dist})² = {L_sq}<br>"
         f"<strong>x²/{semi_x**2} + y²/{dist**2} = 1</strong><br>"
         f"This is an ellipse with semi-axes {semi_x} m (horizontal) and {dist} m (vertical).")
    return q, s, "Express P's coordinates in terms of a and b, substitute into a²+b²=L², simplify to get ellipse form.", 6


def _cl_d3_chord_midpoint():
    R, chord, d = _cl_random_chord()
    hc = chord // 2
    q = (f"A circle has centre O and radius {R} cm. A chord of length {chord} cm slides around inside "
         f"the circle (always remaining a chord). Find the locus of the midpoint M of the chord.")
    s = (f"The line from centre O to midpoint M is perpendicular to the chord (by the perpendicular bisector theorem for circles).<br>"
         f"In right triangle OMX (where X is an endpoint of the chord): OM² + {hc}² = {R}²<br>"
         f"OM² = {R**2} − {hc**2} = {R**2 - hc**2}<br>"
         f"OM = {d} cm (constant, independent of the chord's position).<br>"
         f"The locus is a <strong>circle of radius {d} cm, centred at O</strong>.")
    return q, s, "OM ⊥ chord; use Pythagoras OM² + (half-chord)² = R². OM is constant → circle.", 5, graded_answer_number(d)


def _cl_d4_constant_area_locus():
    AB = random.randint(4, 14)
    h = random.randint(2, 10)
    area = AB * h // 2
    q = (f"Fixed line segment AB has length {AB} cm. Point P moves so that the area of triangle PAB "
         f"is always {area} cm². Describe the locus of P.")
    s = (f"Area = ½ × base × height = ½ × {AB} × h = {area}<br>"
         f"So h = 2 × {area} ÷ {AB} = {h} cm.<br>"
         f"P must always be exactly {h} cm from line AB. "
         f"The locus consists of <strong>two straight lines parallel to AB, each {h} cm away</strong> "
         f"(one on each side of AB).")
    hint = "Area = ½ × base × height; solve for h. P must be at constant height → lines parallel to AB."
    return _cl_mcq_return(
        q, s, hint, 5,
        f"Two straight lines parallel to AB, each {h} cm from AB (one on each side)",
        [
            f"A single line parallel to AB, {h} cm from AB",
            f"A circle of radius {h} cm centred at the midpoint of AB",
            f"The perpendicular bisector of AB",
        ],
    )


def _cl_d5_apollonius_circle():
    d_AB = random.randint(8, 16)
    ratio_num, ratio_den = random.choice([(1, 2), (1, 3), (2, 3)])
    q = (f"Points A and B are {d_AB} cm apart. Point P moves such that PA : PB = {ratio_num} : {ratio_den}. "
         f"Show algebraically that the locus of P is a circle, and state its centre and radius.")
    # PA/PB = ratio_num/ratio_den => ratio_den² PA² = ratio_num² PB²
    rn2, rd2 = ratio_num ** 2, ratio_den ** 2
    # 4(x²+y²) = (x-d)²+y² for 1:2 case generalised:
    # rd2(x²+y²) = rn2((x-d)²+y²)
    # rd2 x² + rd2 y² = rn2 x² - 2*rn2*d*x + rn2*d² + rn2 y²
    # (rd2-rn2)x² + 2*rn2*d*x + (rd2-rn2)y² = rn2*d²
    # For 1:2, d=12: 3x²+24x+3y²=144 => (x+4)²+y²=64, centre (-d*rn2/(rd2-rn2), 0), r = ...
    coeff = rd2 - rn2
    cx = -d_AB * rn2 / coeff
    # Complete square: coeff*(x² + 2*rn2*d/coeff*x) + coeff*y² = rn2*d²
    # x² + 2*cx*x + cx² + y² = rn2*d²/coeff + cx²
    r_sq = rn2 * d_AB ** 2 / coeff + cx ** 2
    r = int(r_sq ** 0.5) if r_sq == int(r_sq ** 0.5) else round(r_sq ** 0.5, 1)
    cx_int = int(cx) if cx == int(cx) else round(cx, 1)
    s = (f"Let A = (0, 0) and B = ({d_AB}, 0). Let P = (x, y).<br>"
         f"PA² = x² + y²;&nbsp; PB² = (x − {d_AB})² + y²<br>"
         f"Since PA/PB = {ratio_num}/{ratio_den}: {rd2}·PA² = {rn2}·PB²<br>"
         f"{rd2}(x² + y²) = {rn2}((x − {d_AB})² + y²)<br>"
         f"Expanding and simplifying gives a circle equation.<br>"
         f"The locus is a <strong>circle with centre ({cx_int}, 0) and radius {r} cm</strong>.")
    return q, s, "Set PA/PB = ratio, square both sides, expand and simplify to complete-the-square form.", 6


def _cl_d6_difference_squares():
    d = random.randint(6, 14)
    x_ans = random.randint(4, 10)
    k = 2 * d * x_ans - d ** 2
    x_calc = (k + d ** 2) / (2 * d)
    q = (f"Points A and B are {d} cm apart. A point P satisfies PA² − PB² = {k}. "
         f"Find the locus of P.")
    s = (f"Place A at (0, 0) and B at ({d}, 0). Let P = (x, y).<br>"
         f"PA² − PB² = {k}<br>"
         f"(x² + y²) − ((x − {d})² + y²) = {k}<br>"
         f"x² − x² + {2*d}x − {d**2} = {k}<br>"
         f"{2*d}x = {k + d**2}<br>"
         f"x = {x_calc}<br>"
         f"The locus is the <strong>vertical line x = {x_calc} cm from A</strong>, perpendicular to AB.")
    return q, s, "Expand PA² and PB², subtract. The y² terms cancel, giving a simple linear equation.", 5, graded_answer_number(x_calc)


def _cl_d7_three_loci():
    q = ("Three villages A, B, and C form a triangle. A mobile phone mast must be placed so that it is:<br>"
         "(i) equidistant from villages A and B,<br>"
         "(ii) equidistant from villages B and C,<br>"
         "(iii) equidistant from all three villages.<br>"
         "Describe the construction and name the special point found.")
    s = ("(i) Draw the perpendicular bisector of AB — the mast is on this line.<br>"
         "(ii) Draw the perpendicular bisector of BC — the mast is also on this line.<br>"
         "(iii) The point equidistant from all three vertices is where all three perpendicular bisectors meet. "
         "This unique point is the <strong>circumcentre</strong> of triangle ABC. "
         "It is equidistant from A, B, and C, and is the centre of the circumscribed circle.")
    hint = "Equidistant from two points → perp bisector. All three → circumcentre (all perp bisectors meet)."
    return _cl_mcq_return(
        q, s, hint, 5,
        "The circumcentre — where the perpendicular bisectors of the sides meet",
        [
            "The incentre — where the angle bisectors meet",
            "The centroid — where the medians meet",
            "The orthocentre — where the altitudes meet",
        ],
    )


def _cl_d8_circumcentre_coords():
    Bx = random.randint(6, 18)
    Cx = random.randint(2, Bx - 2)
    Cy = random.randint(4, 14)
    A, B, C = (0, 0), (Bx, 0), (Cx, Cy)
    Ox = Bx / 2
    mid_AC = (Cx / 2, Cy / 2)
    slope_ac = Cy / Cx if Cx else 0
    if Cy:
        Oy = mid_AC[1] + (Cx / Cy) * (Ox - mid_AC[0])
    else:
        Oy = Cy / 2
    O = (Ox, Oy)
    q = (f"Triangle ABC has A = {A}, B = {B}, C = {C}. "
         f"Find the circumcentre by constructing the perpendicular bisectors of AB and AC algebraically.")
    # Compute perp bisector of AB: midpoint=(B[0]/2, B[1]/2), slope AB = (B[1]-A[1])/(B[0]-A[0])
    mid_AB = ((A[0]+B[0])/2, (A[1]+B[1])/2)
    mid_AC = ((A[0]+C[0])/2, (A[1]+C[1])/2)
    s = (f"Midpoint of AB = {mid_AB}. Since AB is horizontal, perp bisector is x = {mid_AB[0]}.<br>"
         f"Midpoint of AC = {mid_AC}. Slope of AC = ({C[1]}−{A[1]})/({C[0]}−{A[0]}) = {(C[1]-A[1])}/{(C[0]-A[0])}.<br>"
         f"Perp slope = −{C[0]-A[0]}/{C[1]-A[1]}.<br>"
         f"Perp bisector of AC: y − {mid_AC[1]} = −{(C[0]-A[0])}/{(C[1]-A[1])} × (x − {mid_AC[0]}).<br>"
         f"At x = {mid_AB[0]}: solve for y to find circumcentre = <strong>{O}</strong>.")
    ox = round(Ox, 2) if Oy != int(Oy) else int(Ox)
    oy = round(Oy, 2) if Oy != int(Oy) else int(Oy)
    return q, s, "Perp bisector of horizontal segment → vertical line. Substitute into second bisector equation.", 6, graded_answer_number_pair(ox, oy, 'Circumcentre x', 'Circumcentre y')


def _cl_d9_regular_hexagon():
    side = random.randint(3, 30)
    q = (f"Describe how to construct a regular hexagon with side length {side} cm, "
         f"using only a ruler and compasses.")
    s = (f"<strong>Step 1:</strong> Draw a circle of radius {side} cm (the side length equals the radius).<br>"
         f"<strong>Step 2:</strong> Mark any point A on the circle.<br>"
         f"<strong>Step 3:</strong> Without changing the compass ({side} cm), step around the circle marking points: starting at A, mark B, then C, D, E, F — each {side} cm from the previous, totalling 6 points.<br>"
         f"<strong>Step 4:</strong> Join consecutive points with straight lines.<br>"
         f"The result is a regular hexagon with all sides <strong>{side} cm</strong> and all interior angles 120°.")
    hint = "A regular hexagon fits exactly 6 equilateral triangles; the radius equals the side length."
    return q, s, hint, 5, _cl_steps_answer(
        (
            f"Draw a circle of radius {side} cm.",
            "Mark any point A on the circle.",
            f"Without changing the compass ({side} cm), step around the circle marking six points A through F.",
            "Join consecutive points with straight lines.",
        ),
        (
            f"Draw six separate equilateral triangles of side {side} cm and join them.",
            "Use a protractor to mark 120° at each vertex.",
            f"Draw a square of side {side} cm and extend the sides.",
            "Mark six random points on a circle with a ruler only.",
        ),
    )


def _cl_d10_incircle_radius():
    a, b, c = _cl_right_triple_scaled()
    area = a * b / 2
    s_val = (a + b + c) / 2
    r = area / s_val
    q = (f"A triangle has sides {a} cm, {b} cm, {c} cm. "
         f"(i) Find the area of the triangle. "
         f"(ii) Find the radius of the incircle using the formula r = Area / s, where s is the semi-perimeter.")
    r_display = int(r) if r == int(r) else round(r, 1)
    s = (f"(i) This is a right triangle (check: {a}² + {b}² = {a**2+b**2} = {c}²). "
         f"Area = ½ × {a} × {b} = <strong>{area} cm²</strong><br>"
         f"(ii) Semi-perimeter s = ({a} + {b} + {c}) / 2 = {s_val}<br>"
         f"Inradius r = Area / s = {area} / {s_val} = <strong>{r_display} cm</strong>")
    return q, s, "For a right triangle, area = ½ × legs. Inradius = area ÷ semi-perimeter.", 5, graded_answer_number_fields(
        (area, r_display),
        ('Area (cm²)', 'Inradius (cm)'),
    )


def _cl_d11_sector_area_sprinkler():
    R = random.randint(6, 14)
    angle_deg = random.choice([40, 50, 60, 70, 80, 90, 100, 120])
    length = random.randint(6, 16)
    area = round(angle_deg / 360 * math.pi * R**2, 2)
    q = (f"A garden has a straight hedge of length {length} m along one side. "
         f"A sprinkler at corner A has range {R} m and rotates through {angle_deg}°. "
         f"Find the area watered by the sprinkler.")
    s = (f"The watered region is a sector of radius {R} m and angle {angle_deg}°.<br>"
         f"Area = ({angle_deg}/360) × π × {R}² = <strong>{area} m²</strong> (to 2 d.p.)")
    return q, s, "Area of sector = (angle/360) × π × r².", 4, graded_answer_number(area)


def _cl_d12_two_radio_towers():
    d = random.choice([8, 10, 12])
    r1 = random.choice([5, 6, 7])
    r2 = random.choice([5, 6, 7])
    q = (f"Two radio towers A and B are {d} km apart. "
         f"Tower A has range {r1} km. Tower B has range {r2} km. "
         f"(i) Find the total area covered by at least one tower (treat each coverage zone as a full circle). "
         f"(ii) Verify that the two coverage zones overlap, given that {r1} + {r2} = {r1+r2} > {d}.")
    area1 = round(math.pi * r1**2, 2)
    area2 = round(math.pi * r2**2, 2)
    q_str = (f"(i) If you assume no overlap: approximate total = π×{r1}² + π×{r2}² ≈ {area1} + {area2} = {area1+area2:.2f} km².<br>"
             f"(ii) Since {r1} + {r2} = {r1+r2} > {d} (distance between towers), the circles DO overlap. "
             f"The actual total coverage area (with overlap removed) is less than {area1+area2:.2f} km².<br>"
             f"The overlap region is a <strong>lens (intersection of two circles)</strong>, "
             f"confirming that the circles overlap. No single formula at GCSE — describe the region geometrically.")
    s = q_str
    hint = "Sum of radii > distance → circles overlap. Total ≠ sum of areas (overlap counted twice)."
    return _cl_mcq_return(
        q, s, hint, 5,
        "Yes — the circles overlap in a lens-shaped region because the sum of the radii exceeds the distance between the towers",
        [
            "No — the circles do not overlap because each tower covers less than half the distance between them",
            "Yes — they overlap along the perpendicular bisector of AB only (a straight line)",
            "No — the circles touch at exactly one point but do not overlap",
        ],
    )


def _cl_d13_construct_45():
    q = ("Describe how to construct an angle of 45° using only a ruler and compasses.")
    s = ("<strong>Step 1:</strong> Construct a 90° angle at point A on a line: "
         "use the perpendicular-at-a-point method (arcs from A on both sides, then arcs crossing above).<br>"
         "<strong>Step 2:</strong> Bisect the 90° angle using the angle bisector construction.<br>"
         "The bisector of a 90° angle gives a <strong>45° angle</strong>.")
    hint = "45° = half of 90°. First construct 90°, then bisect it."
    return q, s, hint, 4, _cl_steps_answer(
        (
            "Construct a 90° angle at point A on a line using the perpendicular-at-a-point method.",
            "Bisect the 90° angle using the angle bisector construction.",
        ),
        (
            "Construct a 60° angle and subtract 15° with a protractor.",
            "Draw a perpendicular bisector of a line segment.",
            "Use a protractor to measure 45° directly.",
            "Construct an equilateral triangle and trisect one angle.",
        ),
    )


def _cl_d14_construct_30():
    q = ("Describe how to construct an angle of 30° using only a ruler and compasses.")
    s = ("<strong>Step 1:</strong> Construct a 60° angle (equilateral triangle method: "
         "draw an arc from A crossing the base at X; without changing radius, arc from X gives point Y; line AY = 60°).<br>"
         "<strong>Step 2:</strong> Bisect the 60° angle using the angle bisector construction.<br>"
         "The bisector of a 60° angle gives a <strong>30° angle</strong>.")
    hint = "30° = half of 60°. Construct 60° first (equilateral triangle), then bisect."
    return q, s, hint, 4, _cl_steps_answer(
        (
            "Construct a 60° angle using the equilateral triangle method.",
            "Bisect the 60° angle using the angle bisector construction.",
        ),
        (
            "Construct a 90° angle and subtract 60° with a protractor.",
            "Use a protractor to measure 30° directly.",
            "Construct a 45° angle and halve it again.",
            "Draw a perpendicular bisector of a line segment.",
        ),
    )


def _cl_d15_multi_locus_garden():
    length = random.randint(10, 16)
    width = random.randint(7, 12)
    boundary_dist = random.randint(3, 6)
    max_dist = random.randint(5, 9)
    q = (f"A rectangular garden PQRS has PQ = {length} m and QR = {width} m. A tree is to be planted such that:<br>"
         f"(i) it is more than {boundary_dist} m from the boundary PQ,<br>"
         f"(ii) it is closer to P than to R,<br>"
         f"(iii) it is at most {max_dist} m from Q.<br>"
         f"Which of the following best describes the feasible region?")
    s = (f"(i) More than {boundary_dist} m from PQ → above the line parallel to PQ at height {boundary_dist} m.<br>"
         f"(ii) Closer to P than R → on P's side of the perpendicular bisector of PR "
         f"(diagonal of garden: midpoint M of PR).<br>"
         f"(iii) Within {max_dist} m of Q → inside a circle centred at Q, radius {max_dist} m.<br>"
         f"The feasible region is the <strong>intersection of these three regions</strong>: "
         f"above the {boundary_dist} m line, on P's half of the garden (P-side of the diagonal bisector), "
         f"and inside the {max_dist} m circle from Q.")
    hint = "Describe each constraint as a region, then find their intersection."
    return _cl_mcq_return(
        q, s, hint, 6,
        f"The intersection of all three regions: above the line {boundary_dist} m from PQ, on P's side of the perpendicular bisector of PR, and inside the circle of radius {max_dist} m centred at Q",
        [
            "The union of all three regions (any one condition is enough)",
            f"Only the region inside the circle of radius {max_dist} m centred at Q",
            f"Only the region more than {boundary_dist} m from PQ",
        ],
    )


def _cl_d16_garden_sprinkler_multi():
    length = random.randint(10, 16)
    width = random.randint(7, 12)
    boundary_dist = random.randint(3, 6)
    max_dist = random.randint(5, 9)
    svg = _garden_loci_svg()
    q = (f"A rectangular garden PQRS has PQ = {length} m and QR = {width} m (P top-left, Q top-right, "
         f"R bottom-right, S bottom-left). A tree is planted at T such that:<br>"
         f"(a) T is more than {boundary_dist} m from the side PQ,<br>"
         f"(b) T is closer to P than to R,<br>"
         f"(c) T is at most {max_dist} m from Q.<br>"
         f"Which of the following best describes the feasible region?<br>{svg}")
    s = (f"(a) More than {boundary_dist} m from PQ → the region <strong>above the line parallel to PQ, "
         f"{boundary_dist} m inside the garden</strong> (not including the boundary line).<br>"
         f"(b) Closer to P than R → on <strong>P's side of the perpendicular bisector of diagonal PR</strong> "
         f"(the line through the midpoint of PR at right angles to it).<br>"
         f"(c) At most {max_dist} m from Q → <strong>inside or on a circle of radius {max_dist} m centred at Q</strong>.<br>"
         f"The feasible region is the <strong>intersection</strong> of these three regions.")
    hint = "Translate each bullet into one locus; the answer is where all three overlap."
    return _cl_mcq_return(
        q, s, hint, 6,
        f"The intersection of all three regions: above the line {boundary_dist} m from PQ, on P's side of the perpendicular bisector of PR, and inside the circle of radius {max_dist} m centred at Q",
        [
            "The union of all three regions (any one condition is enough)",
            f"Only the region inside the circle of radius {max_dist} m centred at Q",
            f"Only the region on P's side of the perpendicular bisector of PR",
        ],
    )


def _cl_d17_treasure_hunt_multi():
    d_ab = random.randint(6, 14)
    r_c = random.randint(2, 6)
    d_mc = random.randint(2, 5)
    svg = _treasure_loci_svg(d_ab * 8)
    q = (f"Treasure is buried so that:<br>"
         f"(a) It is equidistant from markers A and B, which are {d_ab} m apart.<br>"
         f"(b) It is exactly {r_c} m from marker C, where C lies on the perpendicular bisector of AB "
         f"and is {d_mc} m from the midpoint M of AB.<br>"
         f"(c) How many possible burial positions are there? Justify your answer.<br>{svg}")
    s = ("(a) Equidistant from A and B → on the <strong>perpendicular bisector of AB</strong>.<br>"
         f"(b) Exactly {r_c} m from C → on a <strong>circle of radius {r_c} m centred at C</strong>. "
         f"Since C lies on the perpendicular bisector, this circle crosses that line in two symmetric points.<br>"
         f"(c) There are <strong>2 possible positions</strong> — the two intersection points of the circle "
         f"and the perpendicular bisector ({d_mc} ± {r_c} m along the bisector from C).")
    return q, s, "Each condition is a locus; count intersections of the line and circle.", 6, graded_answer_number(2)


def _cl_d18_triangle_centres_multi():
    a, b, c = _cl_right_triple_scaled()
    area = a * b // 2
    s_val = (a + b + c) / 2
    r_in = area / s_val
    r_circ = c / 2
    svg = _triangle_centres_svg(ab_label=f"{a} cm", bc_label=f"{b} cm", ac_label=f"{c} cm")
    q = (f"Triangle ABC is right-angled at B, with AB = {a} cm, BC = {b} cm and AC = {c} cm.<br>"
         f"(a) Explain why the circumcentre lies on AC and find the circumradius.<br>"
         f"(b) Find the inradius of the triangle.<br>"
         f"(c) A point P moves so that it is equidistant from AB and BC. "
         f"Which construction line must P lie on?<br>{svg}")
    s = (f"(a) In a right-angled triangle the circumcentre is the <strong>midpoint of the hypotenuse AC</strong>. "
         f"Circumradius = ½ × AC = <strong>{r_circ} cm</strong>.<br>"
         f"(b) Area = ½ × {a} × {b} = {area} cm²; semi-perimeter s = {s_val} cm.<br>"
         f"Inradius r = Area ÷ s = {area} ÷ {s_val} = <strong>{r_in} cm</strong>.<br>"
         f"(c) Equidistant from the two legs meeting at B → on the <strong>angle bisector of angle ABC</strong> "
         f"(the line at 45° to both legs through B).")
    r_in_display = int(r_in) if r_in == int(r_in) else round(r_in, 2)
    return q, s, "Right triangle: circumcentre = midpoint of hypotenuse; incentre uses r = Area/s.", 6, graded_answer_number_fields(
        (r_circ, r_in_display),
        ('Circumradius (cm)', 'Inradius (cm)'),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ  (15 questions)
# ══════════════════════════════════════════════════════════════════════════════

_CL_MCQ_BANK = [
    {"q": "What is the locus of all points equidistant from two fixed points A and B?",
     "opts": ["A  The perpendicular bisector of AB",
              "B  The angle bisector of angle AOB",
              "C  A circle with diameter AB",
              "D  The midpoint of AB only"],
     "ans": "A", "marks": 1,
     "sol": "Equidistant from two fixed points → <strong>perpendicular bisector of AB</strong>. Answer: A",
     "hint": "Equal distance from two points → perpendicular bisector."},

    {"q": "What is the locus of all points exactly 5 cm from a fixed point P?",
     "opts": ["A  A circle with centre P and radius 5 cm",
              "B  Two parallel lines 5 cm from P",
              "C  A square of side 5 cm centred at P",
              "D  A line 5 cm long through P"],
     "ans": "A", "marks": 1,
     "sol": "Fixed distance from a point → <strong>circle</strong> centred at P, radius 5 cm. Answer: A",
     "hint": "Fixed distance from one point → circle."},

    {"q": "A wheel of radius 4 cm rolls along a flat road. What is the locus of the wheel's centre?",
     "opts": ["A  A straight line 4 cm above the road",
              "B  A circle of radius 4 cm",
              "C  A wavy curve (cycloid)",
              "D  The road surface itself"],
     "ans": "A", "marks": 1,
     "sol": "The centre stays at constant height = radius → <strong>a straight line parallel to the road, 4 cm above it</strong>. Answer: A",
     "hint": "Centre stays at constant height = radius above the road."},

    {"q": "How do you find the circumscribed circle of a triangle?",
     "opts": ["A  Construct perpendicular bisectors of the sides — they meet at the circumcentre",
              "B  Construct angle bisectors — they meet at the incentre",
              "C  Draw the median from each vertex to the midpoint of the opposite side",
              "D  Find the centroid and draw a circle of radius equal to the altitude"],
     "ans": "A", "marks": 2,
     "sol": "Perpendicular bisectors of the sides meet at the <strong>circumcentre</strong>. Answer: A",
     "hint": "Circumcentre = equidistant from all three vertices → perp bisectors."},

    {"q": "How do you find the inscribed circle (incircle) of a triangle?",
     "opts": ["A  Construct angle bisectors — they meet at the incentre",
              "B  Construct perpendicular bisectors of the sides",
              "C  Draw the altitudes",
              "D  Find the centroid and draw a circle of radius = 1/3 altitude"],
     "ans": "A", "marks": 2,
     "sol": "Angle bisectors meet at the <strong>incentre</strong>, which is equidistant from all three sides. Answer: A",
     "hint": "Incentre = equidistant from all three sides → angle bisectors."},

    {"q": "What angle does the perpendicular bisector of AB make with AB?",
     "opts": ["A  90°", "B  45°", "C  60°", "D  It depends on the length of AB"],
     "ans": "A", "marks": 1,
     "sol": "The perpendicular bisector is always at <strong>90°</strong> to AB. Answer: A",
     "hint": "Perpendicular means 90°."},

    {"q": "To construct a triangle with sides 5 cm, 7 cm, 9 cm, you need:",
     "opts": ["A  A ruler and compasses only",
              "B  A ruler, compasses and protractor",
              "C  A protractor only",
              "D  A ruler and protractor"],
     "ans": "A", "marks": 1,
     "sol": "SSS construction needs only a <strong>ruler and compasses</strong>. Protractor is not needed. Answer: A",
     "hint": "SSS = ruler + compasses only. No angles needed."},

    {"q": "What is the locus of all points equidistant from two intersecting lines?",
     "opts": ["A  The angle bisectors of the angles formed",
              "B  The perpendicular bisector of the line joining the intersection point to a point on each line",
              "C  A circle centred at the intersection point",
              "D  A line parallel to both"],
     "ans": "A", "marks": 2,
     "sol": "Equidistant from two lines → <strong>angle bisectors</strong> of the angles they form. Answer: A",
     "hint": "Equidistant from two lines → angle bisector."},

    {"q": "A map has scale 1:500. A path is 3.6 cm on the map. What is the actual length?",
     "opts": ["A  18 m", "B  1.8 m", "C  180 m", "D  0.18 m"],
     "ans": "A", "marks": 2,
     "sol": "3.6 × 500 = 1800 cm = <strong>18 m</strong>. Answer: A",
     "hint": "Multiply map length by scale factor, then convert cm → m."},

    {"q": "You want points closer to A AND within 6 cm of B. The region is:",
     "opts": ["A  The part of the circle (radius 6, centre B) on A's side of the perpendicular bisector of AB",
              "B  The entire circle of radius 6 about B",
              "C  The perpendicular bisector of AB only",
              "D  The region between two parallel lines"],
     "ans": "A", "marks": 3,
     "sol": "Closer to A → A's half-plane. Within 6 of B → circle. The answer is their <strong>intersection</strong>. Answer: A",
     "hint": "AND = intersection of both regions."},

    {"q": "PA : PB = 1 : 1. What is the locus of P?",
     "opts": ["A  The perpendicular bisector of AB",
              "B  A circle with diameter AB",
              "C  The midpoint of AB",
              "D  A line parallel to AB"],
     "ans": "A", "marks": 1,
     "sol": "PA = PB → locus is the <strong>perpendicular bisector of AB</strong>. Answer: A",
     "hint": "PA:PB = 1:1 means PA = PB → equidistant from A and B."},

    {"q": "A chord of length 8 cm slides inside a circle of radius 5 cm. What is the locus of the chord's midpoint?",
     "opts": ["A  A circle of radius 3 cm centred at O",
              "B  A circle of radius 5 cm centred at O",
              "C  A circle of radius 4 cm centred at O",
              "D  The centre O only"],
     "ans": "A", "marks": 3,
     "sol": "OM² + 4² = 5² → OM = 3. Locus is a <strong>circle of radius 3 cm</strong>. Answer: A",
     "hint": "Pythagoras: OM² + (half-chord)² = radius². OM is constant."},

    {"q": "What shape is the locus of all points exactly d cm from a straight line segment?",
     "opts": ["A  A stadium shape (rectangle with semicircles at the ends)",
              "B  A rectangle of width 2d",
              "C  Two parallel lines only",
              "D  An ellipse"],
     "ans": "A", "marks": 2,
     "sol": "Two parallel lines joined by semicircles = <strong>stadium shape</strong>. Answer: A",
     "hint": "From a segment: parallel lines along the sides, semicircles at the ends."},

    {"q": "A 10 m ladder slides down a wall. What is the locus of the midpoint of the ladder?",
     "opts": ["A  A quarter-circle of radius 5 m",
              "B  A straight line at 45°",
              "C  A semicircle of radius 10 m",
              "D  An ellipse"],
     "ans": "A", "marks": 3,
     "sol": "Midpoint traces x² + y² = 25 (a circle of radius 5 m). In context: a <strong>quarter-circle of radius 5 m</strong>. Answer: A",
     "hint": "Midpoint = (a/2, b/2); substitute into a²+b²=100 → x²+y²=25."},

    {"q": "Construct 30° using only ruler and compasses. The method is:",
     "opts": ["A  Construct 60° then bisect it",
              "B  Construct 90° then bisect it",
              "C  Construct 45° then subtract 15°",
              "D  Use a protractor"],
     "ans": "A", "marks": 2,
     "sol": "30° = 60° ÷ 2. Construct 60° (equilateral triangle), then <strong>bisect it</strong>. Answer: A",
     "hint": "30° = half of 60°. Equilateral triangle gives 60°; bisect to get 30°."},
]


def constructions_loci_mcq():
    item = random.choice(_CL_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_constructions_loci_variants(difficulty, mode='practice'):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _CL_MCQ_BANK, procedural_mcq_for('constructions_loci'), 'constructions_loci', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _cl_f1_equidistant_two_points, _cl_f2_fixed_distance_point,
            _cl_f3_equidistant_two_lines, _cl_f4_fixed_distance_segment,
            _cl_f5_perp_bisector_property, _cl_f6_angle_bisector_property,
            _cl_f7_rolling_wheel, _cl_f8_closer_to_A,
            _cl_f9_construct_perp_bisector_steps, _cl_f10_construct_angle_bisector_steps,
            _cl_f11_triangle_tools, _cl_f12_locus_around_rectangle,
            _cl_f13_bisector_right_angle, _cl_f14_two_circle_region,
            _cl_f15_scale_drawing_length,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _cl_i1_combined_loci, _cl_i2_equilateral_triangle,
            _cl_i3_ladder_midpoint, _cl_i4_semicircle_locus,
            _cl_i5_treasure_hunt, _cl_i6_perp_from_external_point,
            _cl_i7_triangle_sss_steps, _cl_i8_construct_60,
            _cl_i9_perp_at_point_on_line, _cl_i10_scale_bearing,
            _cl_i11_circumcircle, _cl_i12_incircle,
            _cl_i13_garden_sprinkler, _cl_i14_count_loci_intersections,
            _cl_i15_scale_area,
        ]
    elif difficulty == 'difficult':
        pool = [
            _cl_d1_locus_proof, _cl_d2_ladder_ellipse,
            _cl_d3_chord_midpoint, _cl_d4_constant_area_locus,
            _cl_d5_apollonius_circle, _cl_d6_difference_squares,
            _cl_d7_three_loci, _cl_d8_circumcentre_coords,
            _cl_d9_regular_hexagon, _cl_d10_incircle_radius,
            _cl_d11_sector_area_sprinkler, _cl_d12_two_radio_towers,
            _cl_d13_construct_45, _cl_d14_construct_30,
            _cl_d15_multi_locus_garden,
            _cl_d16_garden_sprinkler_multi, _cl_d17_treasure_hunt_multi,
            _cl_d18_triangle_centres_multi,
        ]
    else:
        f = random.sample([_cl_f1_equidistant_two_points, _cl_f2_fixed_distance_point,
                           _cl_f9_construct_perp_bisector_steps, _cl_f15_scale_drawing_length], 3)
        i = random.sample([_cl_i1_combined_loci, _cl_i3_ladder_midpoint,
                           _cl_i5_treasure_hunt, _cl_i8_construct_60], 4)
        d = random.sample([_cl_d1_locus_proof, _cl_d3_chord_midpoint,
                           _cl_d5_apollonius_circle, _cl_d9_regular_hexagon], 3)
        return f + i + d

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_constructions_loci(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_constructions_loci_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'constructions_loci',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_constructions_loci_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    result = variant()
    if len(result) == 6:
        q, s, hint, marks, opts, correct = result
        return make_problem(
            q, s, hint, difficulty, marks,
            'gcse', 'maths', 'constructions_loci',
            options=opts, correct_answer=correct,
        )
    return make_graded_problem(result, difficulty, 'gcse', 'maths', 'constructions_loci')
