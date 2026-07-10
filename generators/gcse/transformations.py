"""
GCSE Maths – Transformations
15 foundational · 15 intermediate · 15 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
Final answers are wrapped in <strong> tags.
"""
import random
from generators.shared.utils import make_problem
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


# ─── Formatting helpers ────────────────────────────────────────────────────────

def _v(a, b):
    """Format a column vector in LaTeX."""
    return rf"\(\begin{{pmatrix}} {a} \\ {b} \end{{pmatrix}}\)"


def _fmt_tri(pts, primed=False):
    labels = ["P'", "Q'", "R'"] if primed else ["P", "Q", "R"]
    return ", ".join(f"{labels[i]}({pts[i][0]},{pts[i][1]})" for i in range(3))


# ─── Transformation rules ──────────────────────────────────────────────────────

def _apply_trans(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def _apply_refxax(pts):
    return [(x, -y) for x, y in pts]


def _apply_refyax(pts):
    return [(-x, y) for x, y in pts]


def _apply_refyx(pts):
    return [(y, x) for x, y in pts]


def _apply_refynx(pts):
    return [(-y, -x) for x, y in pts]


def _apply_refxk(pts, k):
    return [(2 * k - x, y) for x, y in pts]


def _apply_refyk(pts, k):
    return [(x, 2 * k - y) for x, y in pts]


def _apply_rot90cw(pts):
    return [(y, -x) for x, y in pts]


def _apply_rot90acw(pts):
    return [(-y, x) for x, y in pts]


def _apply_rot180(pts):
    return [(-x, -y) for x, y in pts]


def _rot90cw_about(x, y, cx, cy):
    """90° CW about (cx, cy)."""
    return cx + (y - cy), cy - (x - cx)


def _rot90acw_about(x, y, cx, cy):
    """90° ACW about (cx, cy)."""
    return cx - (y - cy), cy + (x - cx)


def _enlarge_pt(x, y, k, cx=0, cy=0):
    rx = cx + k * (x - cx)
    ry = cy + k * (y - cy)
    rx = int(rx) if rx == int(rx) else rx
    ry = int(ry) if ry == int(ry) else ry
    return rx, ry


def _enlarge_tri(pts, k, cx=0, cy=0):
    return [_enlarge_pt(x, y, k, cx, cy) for x, y in pts]


def _nice_tri():
    """Return a triangle with small positive integer coords."""
    px, py = random.randint(1, 3), random.randint(1, 3)
    qx, qy = px + random.randint(1, 3), py
    rx, ry = px, py + random.randint(1, 3)
    return [(px, py), (qx, qy), (rx, ry)]


def _sol_steps(tri, img, rule_text):
    """Build step-by-step solution for three points."""
    lines = [f"{rule_text}<br>"]
    labels = [("P", "P'"), ("Q", "Q'"), ("R", "R'")]
    for i, ((x, y), (ix, iy)) in enumerate(zip(tri, img)):
        lines.append(f"{labels[i][0]}({x},{y}) → {labels[i][1]}({ix},{iy})<br>")
    lines.append(
        rf"<strong>{_fmt_tri(img, primed=True)}</strong>"
    )
    return "".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _trans_found_translate():
    tri = _nice_tri()
    dx = random.choice([-4, -3, -2, 2, 3, 4])
    dy = random.choice([-4, -3, -2, 2, 3, 4])
    img = _apply_trans(tri, dx, dy)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Translate triangle PQR by the vector {_v(dx, dy)}.<br>"
         rf"Write down the coordinates of the image P'Q'R'.")
    s = _sol_steps(tri, img,
                   rf"Translation {_v(dx, dy)}: add {dx} to each x-coordinate and {dy} to each y-coordinate.")
    hint = "Add the vector to each vertex separately."
    return q, s, hint, 2


def _trans_found_reflect_xaxis():
    tri = _nice_tri()
    img = _apply_refxax(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the x-axis.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Reflection in the x-axis: \((x, y) \to (x, -y)\) — negate the y-coordinate.")
    hint = "Reflection in the x-axis: keep x, change the sign of y."
    return q, s, hint, 2


def _trans_found_reflect_yaxis():
    tri = _nice_tri()
    img = _apply_refyax(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the y-axis.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Reflection in the y-axis: \((x, y) \to (-x, y)\) — negate the x-coordinate.")
    hint = "Reflection in the y-axis: change the sign of x, keep y."
    return q, s, hint, 2


def _trans_found_reflect_yx():
    tri = _nice_tri()
    img = _apply_refyx(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the line \(y = x\).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Reflection in \(y = x\): \((x, y) \to (y, x)\) — swap x and y.")
    hint = r"Reflection in y = x: swap the two coordinates."
    return q, s, hint, 2


def _trans_found_rotate_90cw():
    tri = _nice_tri()
    img = _apply_rot90cw(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 90° clockwise about the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Rotation 90° CW about origin: \((x, y) \to (y, -x)\).")
    hint = "90° clockwise about the origin: (x, y) → (y, −x)."
    return q, s, hint, 2


def _trans_found_rotate_180():
    tri = _nice_tri()
    img = _apply_rot180(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 180° about the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Rotation 180° about origin: \((x, y) \to (-x, -y)\) — negate both coordinates.")
    hint = "180° rotation about origin: negate both x and y."
    return q, s, hint, 2


def _trans_found_enlarge_origin():
    tri = _nice_tri()
    k = random.choice([2, 3, 4])
    img = _enlarge_tri(tri, k)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Enlarge triangle PQR by scale factor {k}, centre the origin (0,0).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img,
                   rf"Enlargement SF {k} about origin: multiply each coordinate by {k}: \((x,y) \to ({k}x, {k}y)\).")
    hint = f"Multiply each coordinate by the scale factor {k}."
    return q, s, hint, 2


def _trans_found_describe_translation():
    tri = _nice_tri()
    dx = random.choice([-3, -2, 2, 3, 4])
    dy = random.choice([-4, -3, 2, 3, 4])
    img = _apply_trans(tri, dx, dy)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Its image P'Q'R' has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"Describe fully the single transformation that maps PQR onto P'Q'R'.")
    s = (rf"Find the change in x and y for any vertex:<br>"
         rf"P({tri[0][0]},{tri[0][1]}) → P'({img[0][0]},{img[0][1]}): "
         rf"change = ({img[0][0]-tri[0][0]}, {img[0][1]-tri[0][1]})<br>"
         rf"This is the same for Q and R, confirming a translation.<br>"
         rf"<strong>Translation by the vector {_v(dx, dy)}</strong>")
    hint = "Check whether the change in x and y is the same for every vertex."
    return q, s, hint, 2


def _trans_found_describe_reflection_axis():
    tri = _nice_tri()
    axis = random.choice(['x', 'y'])
    img = _apply_refxax(tri) if axis == 'x' else _apply_refyax(tri)
    ax_name = "x-axis" if axis == 'x' else "y-axis"
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Its image P'Q'R' has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"Describe fully the single transformation that maps PQR onto P'Q'R'.")
    if axis == 'x':
        reason = "The y-coordinates are negated and the x-coordinates are unchanged → reflection in the x-axis."
    else:
        reason = "The x-coordinates are negated and the y-coordinates are unchanged → reflection in the y-axis."
    s = (rf"{reason}<br>"
         rf"<strong>Reflection in the {ax_name}</strong>")
    hint = "Look at which coordinate changes sign in all vertices."
    return q, s, hint, 2


def _trans_found_describe_rotation_90():
    direction = random.choice(['clockwise', 'anticlockwise'])
    tri = _nice_tri()
    if direction == 'clockwise':
        img = _apply_rot90cw(tri)
        rule = r"\((x,y) \to (y,-x)\)"
        check = f"P({tri[0][0]},{tri[0][1]}) → P'({img[0][0]},{img[0][1]}) ✓"
    else:
        img = _apply_rot90acw(tri)
        rule = r"\((x,y) \to (-y,x)\)"
        check = f"P({tri[0][0]},{tri[0][1]}) → P'({img[0][0]},{img[0][1]}) ✓"
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Its image P'Q'R' has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"Describe fully the single transformation that maps PQR onto P'Q'R'.")
    s = (rf"Check: does {rule}? {check}<br>"
         rf"The shape is congruent → rotation.<br>"
         rf"<strong>Rotation 90° {direction}, centre the origin (0,0)</strong>")
    hint = f"Apply the rule for 90° {direction} and check it matches every image vertex."
    return q, s, hint, 3


def _trans_found_describe_rotation_180():
    tri = _nice_tri()
    img = _apply_rot180(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Its image P'Q'R' has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"Describe fully the single transformation.")
    s = (rf"Both coordinates are negated in every vertex: \((x,y) \to (-x,-y)\).<br>"
         rf"This is a rotation of 180° (half-turn).<br>"
         rf"<strong>Rotation 180°, centre the origin (0,0)</strong>")
    hint = "If both coordinates are negated, it is a 180° rotation about the origin."
    return q, s, hint, 3


def _trans_found_reflect_xk():
    tri = _nice_tri()
    k = random.choice([2, 3, 4])
    img = _apply_refxk(tri, k)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the line \(x = {k}\).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img,
                   rf"Reflection in \(x = {k}\): \((x, y) \to (2 \times {k} - x,\; y) = ({2*k} - x,\; y)\).")
    hint = f"Reflection in x = {k}: new x-coord = {2*k} − old x, y stays the same."
    return q, s, hint, 2


def _trans_found_reflect_yk():
    tri = _nice_tri()
    k = random.choice([2, 3, 4])
    img = _apply_refyk(tri, k)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the line \(y = {k}\).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img,
                   rf"Reflection in \(y = {k}\): \((x, y) \to (x,\; 2 \times {k} - y) = (x,\; {2*k} - y)\).")
    hint = f"Reflection in y = {k}: x stays the same, new y-coord = {2*k} − old y."
    return q, s, hint, 2


def _trans_found_rotate_90acw():
    tri = _nice_tri()
    img = _apply_rot90acw(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 90° anticlockwise about the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Rotation 90° ACW about origin: \((x, y) \to (-y, x)\).")
    hint = "90° anticlockwise: (x, y) → (−y, x)."
    return q, s, hint, 2


def _trans_found_identify_type():
    dx, dy = random.randint(1, 5), random.randint(1, 5)
    sf = random.choice([2, 3, 4])
    deg = random.choice([90, 180, 270])
    dirn = random.choice(['clockwise', 'anticlockwise'])
    ax = random.choice(['the x-axis', 'the y-axis', 'the line y = x', 'the line x = 2'])
    name, desc = random.choice([
        ("Translation", f"every point moves {dx} units to the right and {dy} units up"),
        ("Translation", f"every point shifts by the vector ({random.choice([-4,-3,-2,2,3,4])}, {random.choice([-4,-3,-2,2,3,4])})"),
        ("Reflection", f"the shape is flipped in {ax}"),
        ("Reflection", f"each point maps to its mirror image in the line y = −x"),
        ("Rotation", f"the shape turns {deg}° {dirn} about the origin"),
        ("Rotation", f"the shape turns 90° clockwise about the point (1, 1)"),
        ("Enlargement", f"every length is multiplied by {sf}, centre the origin"),
        ("Enlargement", f"the shape is scaled by a factor of {sf} from the point (2, 0)"),
    ])
    q = (rf"A transformation is described as follows: '{desc}'.<br>"
         rf"What type of transformation is this?")
    if name == "Translation":
        reason = "Every point moves by the same vector, with no rotation or reflection."
    elif name == "Reflection":
        reason = "The shape is flipped in a mirror line."
    elif name == "Rotation":
        reason = "The shape turns about a fixed point."
    else:
        reason = "Every length is scaled by a constant factor from a fixed centre."
    s = rf"{reason}<br><strong>{name}</strong>"
    hint = "Translation → same vector. Reflection → flip. Rotation → turn. Enlargement → size change."
    return q, s, hint, 1


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _trans_inter_reflect_y_neg_x():
    tri = _nice_tri()
    img = _apply_refynx(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the line \(y = -x\).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Reflection in \(y = -x\): \((x, y) \to (-y, -x)\).")
    hint = r"Reflection in y = −x: negate both coordinates and swap them."
    return q, s, hint, 2


def _trans_inter_enlarge_not_origin():
    cx, cy = random.choice([(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2),
                             (3, 0), (0, 3), (3, 1), (1, 3)])
    k = random.choice([2, 3, 4])
    da, db = random.choice([(1, 2), (1, 3), (2, 2), (2, 3)])
    # Use a small triangle that stays in reasonable range
    base = [(cx + 1, cy + 1), (cx + 1 + da, cy + 1), (cx + 1, cy + 1 + db)]
    img = _enlarge_tri(base, k, cx, cy)
    q = (rf"Triangle PQR has vertices {_fmt_tri(base)}.<br>"
         rf"Enlarge triangle PQR by scale factor {k}, centre ({cx},{cy}).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = (rf"For enlargement SF {k} about ({cx},{cy}): \((x,y) \to "
         rf"({cx}+{k}(x-{cx}),\; {cy}+{k}(y-{cy}))\).<br>"
         + "".join(
             rf"P{'' if i else ''}({base[i][0]},{base[i][1]}) → "
             rf"P{'Q R'[i]}'({img[i][0]},{img[i][1]})<br>"
             for i in range(3)
         ).replace("P(", "P(").replace("Q(", "Q(").replace("R(", "R(")
         + rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    # Better solution text:
    lines = [rf"For enlargement SF {k} about ({cx},{cy}): \((x,y) \to ({cx}+{k}(x-{cx}),\; {cy}+{k}(y-{cy}))\).<br>"]
    lbs = ["P", "Q", "R"]
    for i in range(3):
        lines.append(rf"{lbs[i]}({base[i][0]},{base[i][1]}) → {lbs[i]}'({img[i][0]},{img[i][1]})<br>")
    lines.append(rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    s = "".join(lines)
    hint = f"For each point: new coord = centre + {k} × (old coord − centre)."
    return q, s, hint, 3


def _trans_inter_rotate_not_origin():
    cx, cy = random.choice([(1, 1), (2, 0), (0, 2), (1, 0), (0, 1), (2, 1), (1, 2), (3, 0), (0, 3),
                             (3, 1), (1, 3), (2, 2), (3, 2), (2, 3), (4, 0), (0, 4), (4, 1), (1, 4)])
    direction = random.choice(['clockwise', 'anticlockwise'])
    tri = [(cx + 1, cy), (cx + 3, cy), (cx + 1, cy + 2)]
    if direction == 'clockwise':
        img = [(_rot90cw_about(x, y, cx, cy)) for x, y in tri]
    else:
        img = [(_rot90acw_about(x, y, cx, cy)) for x, y in tri]
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 90° {direction} about the point ({cx},{cy}).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    if direction == 'clockwise':
        rule = rf"90° CW about ({cx},{cy}): \((x,y) \to ({cx}+(y-{cy}),\; {cy}-(x-{cx}))\)."
    else:
        rule = rf"90° ACW about ({cx},{cy}): \((x,y) \to ({cx}-(y-{cy}),\; {cy}+(x-{cx}))\)."
    lines = [rule + "<br>"]
    lbs = ["P", "Q", "R"]
    for i in range(3):
        lines.append(rf"{lbs[i]}({tri[i][0]},{tri[i][1]}) → {lbs[i]}'({img[i][0]},{img[i][1]})<br>")
    lines.append(rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    s = "".join(lines)
    hint = f"Translate so that ({cx},{cy}) is the origin, rotate, then translate back."
    return q, s, hint, 3


def _trans_inter_enlarge_frac_sf():
    # Pick k_num/k_den; coords must be multiples of k_den for integer results
    k_num, k_den = random.choice([(1, 2), (1, 3), (2, 3)])
    mult = k_den  # base coords must be multiples of k_den
    # Build a triangle with coords that are multiples of k_den
    p = (random.choice([1, 2]) * mult, random.choice([1, 2]) * mult)
    q_pt = (p[0] + random.choice([1, 2, 3]) * mult, p[1])
    r_pt = (p[0], p[1] + random.choice([1, 2, 3]) * mult)
    base = [p, q_pt, r_pt]
    sf = k_num / k_den
    img = [_enlarge_pt(x, y, sf) for x, y in base]
    if k_num == 1 and k_den == 2:
        sf_str = r"\(\dfrac{1}{2}\)"
        rule = r"multiply each coordinate by \(\frac{1}{2}\)"
    elif k_num == 1 and k_den == 3:
        sf_str = r"\(\dfrac{1}{3}\)"
        rule = r"multiply each coordinate by \(\frac{1}{3}\)"
    else:
        sf_str = r"\(\dfrac{2}{3}\)"
        rule = r"multiply each coordinate by \(\frac{2}{3}\)"
    q = (rf"Triangle PQR has vertices {_fmt_tri(base)}.<br>"
         rf"Enlarge triangle PQR by scale factor {sf_str}, centre the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    lines = [rf"Enlargement SF {sf_str} about origin: {rule}.<br>"]
    for i, (lbl, (ox, oy), (ix, iy)) in enumerate(zip(["P", "Q", "R"], base, img)):
        lines.append(rf"{lbl}({ox},{oy}) → {lbl}'({ix},{iy})<br>")
    lines.append(rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    s = "".join(lines)
    hint = "A scale factor between 0 and 1 produces a smaller image."
    return q, s, hint, 3


def _trans_inter_describe_enlargement_full():
    cx, cy = random.choice([(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1),
                             (1, 2), (3, 0), (0, 3), (3, 1), (1, 3)])
    k = random.choice([2, 3, 4])
    base = [(cx + 1, cy + 1), (cx + 3, cy + 1), (cx + 1, cy + 3)]
    img = _enlarge_tri(base, k, cx, cy)
    q = (rf"Triangle PQR has vertices {_fmt_tri(base)}.<br>"
         rf"Its image P'Q'R' has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"Describe fully the single transformation that maps PQR onto P'Q'R'.")
    s = (rf"Lengths have been scaled (not preserved), so this is an enlargement.<br>"
         rf"Scale factor: \(\dfrac{{P'Q'}}{{PQ}} = \dfrac{{{abs(img[1][0]-img[0][0])}}}{{{abs(base[1][0]-base[0][0])}}} = {k}\)<br>"
         rf"Centre: the point from which lines PP', QQ', RR' all radiate from is ({cx},{cy}).<br>"
         rf"<strong>Enlargement, scale factor {k}, centre ({cx},{cy})</strong>")
    hint = "Find the scale factor from any pair of corresponding lengths, then find where the rays through corresponding points meet."
    return q, s, hint, 3


def _trans_inter_find_centre_enlargement():
    cx, cy = random.choice([(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
                             (2, 1), (1, 2), (3, 0), (0, 3)])
    k = random.choice([2, 3, 4])
    base = [(cx + 1, cy + 1), (cx + 2, cy + 1), (cx + 1, cy + 2)]
    img = _enlarge_tri(base, k, cx, cy)
    q = (rf"Triangle PQR has vertices {_fmt_tri(base)}.<br>"
         rf"It is enlarged to give P'Q'R' with vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"(a) Find the scale factor of the enlargement.<br>"
         rf"(b) Find the centre of enlargement.")
    sf = abs(img[1][0] - img[0][0]) // abs(base[1][0] - base[0][0])
    s = (rf"(a) Compare corresponding lengths: \(\dfrac{{P'Q'}}{{PQ}} = "
         rf"\dfrac{{{abs(img[1][0]-img[0][0])}}}{{{abs(base[1][0]-base[0][0])}}} = {sf}\)<br>"
         rf"<strong>Scale factor = {sf}</strong><br>"
         rf"(b) Draw lines through P and P', Q and Q'. The centre is where these lines meet.<br>"
         rf"Line PP': from ({base[0][0]},{base[0][1]}) to ({img[0][0]},{img[0][1]}) → passes through (0,0).<br>"
         rf"<strong>Centre of enlargement = (0, 0)</strong>")
    hint = "Draw straight lines through each vertex and its image — they all meet at the centre."
    return q, s, hint, 4


def _trans_inter_enlarge_neg_sf():
    cx, cy = random.choice([(1, 1), (2, 1), (1, 2), (2, 2), (3, 1), (1, 3),
                             (3, 2), (2, 3), (4, 1), (1, 4), (3, 3)])
    k = random.choice([-2, -3])
    da, db = random.choice([(1, 1), (1, 2), (2, 1), (2, 2)])
    base = [(cx + 1, cy), (cx + 1 + da, cy), (cx + 1, cy + db)]
    img = _enlarge_tri(base, k, cx, cy)
    q = (rf"Triangle PQR has vertices {_fmt_tri(base)}.<br>"
         rf"Enlarge triangle PQR by scale factor {k}, centre ({cx},{cy}).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    lines = [rf"Enlargement SF {k} about ({cx},{cy}): \((x,y) \to ({cx}+({k})(x-{cx}),\; {cy}+({k})(y-{cy}))\).<br>"]
    for i, (x, y) in enumerate(base):
        ix, iy = img[i]
        lines.append(rf"{'PQR'[i]}({x},{y}) → {'PQR'[i]}'({ix},{iy})<br>")
    lines.append(rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    s = "".join(lines)
    hint = "A negative scale factor means the image is on the opposite side of the centre."
    return q, s, hint, 3


def _trans_inter_reflect_oblique():
    # Reflection in y = x + c: (x,y) → (y-c, x+c)
    c = random.choice([1, 2, -1, -2])
    tri = _nice_tri()
    img = [(y - c, x + c) for x, y in tri]
    c_str = f"+ {c}" if c > 0 else f"- {abs(c)}"
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the line \(y = x {c_str}\).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = (rf"Reflection in \(y = x {c_str}\): \((x, y) \to (y - ({c}),\; x + ({c}))\) = \((y{'-' if c > 0 else '+'}{abs(c)},\; x{'+' if c > 0 else '-'}{abs(c)})\).<br>"
         + "".join(rf"{'PQR'[i]}({tri[i][0]},{tri[i][1]}) → {'PQR'[i]}'({img[i][0]},{img[i][1]})<br>" for i in range(3))
         + rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    hint = rf"For reflection in y = x + c: new point is (y − c, x + c)."
    return q, s, hint, 3


def _trans_inter_invariant_reflection():
    axis = random.choice(['x', 'y'])
    if axis == 'x':
        q = (r"Under a reflection in the x-axis, a point P(a, b) maps to itself (P is an invariant point).<br>"
             r"What can you deduce about b? Give an example of an invariant point.")
        s = (r"Reflection in the x-axis: \((a, b) \to (a, -b)\).<br>"
             r"For P to map to itself: \(b = -b \Rightarrow 2b = 0 \Rightarrow b = 0\).<br>"
             r"Every point on the x-axis is invariant.<br>"
             r"<strong>\(b = 0\); for example, (3, 0) is invariant</strong>")
        hint = "A point is invariant if it maps to itself. Find when (a,b) = (a,−b)."
    else:
        q = (r"Under a reflection in the y-axis, a point P(a, b) maps to itself (P is an invariant point).<br>"
             r"What can you deduce about a? Give an example of an invariant point.")
        s = (r"Reflection in the y-axis: \((a, b) \to (-a, b)\).<br>"
             r"For P to map to itself: \(a = -a \Rightarrow a = 0\).<br>"
             r"Every point on the y-axis is invariant.<br>"
             r"<strong>\(a = 0\); for example, (0, 5) is invariant</strong>")
        hint = "A point is invariant if it maps to itself. Find when (a,b) = (−a,b)."
    return q, s, hint, 3

_trans_inter_invariant_reflection._fixed_stem = True


def _trans_inter_area_after_enlargement():
    k = random.choice([2, 3, 4, 5])
    area = random.randint(2, 15)
    new_area = area * k * k
    q = (rf"A triangle has area {area} cm².<br>"
         rf"It is enlarged by scale factor {k}.<br>"
         rf"Find the area of the image triangle.")
    s = (rf"When a shape is enlarged by scale factor k, the area is multiplied by k².<br>"
         rf"Area of image = {area} × k² = {area} × {k*k} = {new_area} cm²<br>"
         rf"<strong>{new_area} cm²</strong>")
    hint = f"Area scale factor = (linear scale factor)² = {k}² = {k*k}."
    return q, s, hint, 3


def _trans_inter_combination_reflect_reflect():
    tri = _nice_tri()
    q = (rf"Triangle T has vertices {_fmt_tri(tri)}.<br>"
         r"(a) Reflect T in the x-axis to give T'.<br>"
         r"(b) Reflect T' in the y-axis to give T''.<br>"
         r"(c) Describe the single transformation that maps T directly onto T''.")
    step1 = _apply_refxax(tri)
    step2 = _apply_refyax(step1)
    s = (rf"(a) Reflect in x-axis \((x,y)\to(x,-y)\): T' has vertices {_fmt_tri(step1, primed=True)}<br>"
         rf"(b) Reflect T' in y-axis \((x,y)\to(-x,y)\): T'' has vertices {_fmt_tri(step2, primed=True)}<br>"
         rf"(c) Comparing T and T'': P({tri[0][0]},{tri[0][1]}) → P''({step2[0][0]},{step2[0][1]}), i.e. \((x,y)\to(-x,-y)\).<br>"
         rf"<strong>Single transformation: rotation 180° about the origin (0,0)</strong>")
    hint = "Two reflections in perpendicular lines through the origin give a 180° rotation."
    return q, s, hint, 4


def _trans_inter_describe_rotation_full():
    cx, cy = random.choice([(1, 1), (2, 0), (0, 2), (2, 1), (1, 2), (3, 1), (1, 3),
                             (3, 2), (2, 3), (4, 1), (1, 4), (3, 3), (4, 0), (0, 4)])
    direction = random.choice(['clockwise', 'anticlockwise'])
    tri = [(cx + 1, cy), (cx + 3, cy), (cx + 1, cy + 2)]
    if direction == 'clockwise':
        img = [_rot90cw_about(x, y, cx, cy) for x, y in tri]
        dir_desc = "clockwise"
    else:
        img = [_rot90acw_about(x, y, cx, cy) for x, y in tri]
        dir_desc = "anticlockwise"
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Its image P'Q'R' has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"Describe fully the single transformation that maps PQR onto P'Q'R'.")
    mx = (tri[0][0] + img[0][0]) // 2
    my = (tri[0][1] + img[0][1]) // 2
    s = (rf"The shape is congruent → rotation.<br>"
         rf"Midpoint of PP': \(\left(\dfrac{{{tri[0][0]}+{img[0][0]}}}{2},\dfrac{{{tri[0][1]}+{img[0][1]}}}{2}\right) = ({mx},{my})\).<br>"
         rf"Testing centre ({cx},{cy}): applying 90° {dir_desc} about ({cx},{cy}) to P({tri[0][0]},{tri[0][1]}) gives "
         rf"P'({img[0][0]},{img[0][1]}) ✓<br>"
         rf"<strong>Rotation 90° {dir_desc}, centre ({cx},{cy})</strong>")
    hint = "For a rotation, the shape stays congruent. Find the centre by drawing perpendicular bisectors of PP' etc."
    return q, s, hint, 4


def _trans_inter_reverse_transformation():
    tri = _nice_tri()
    dx, dy = random.choice([-2, 2, 3]), random.choice([-3, 2, 3])
    img = _apply_trans(tri, dx, dy)
    q = (rf"Triangle P'Q'R' (the image) has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"It was obtained by translating the original triangle PQR by the vector {_v(dx, dy)}.<br>"
         rf"Find the coordinates of the original triangle PQR.")
    orig = _apply_trans(img, -dx, -dy)
    s = (rf"To reverse a translation by {_v(dx, dy)}, apply the inverse vector {_v(-dx, -dy)}.<br>"
         + "".join(rf"{'PQR'[i]}'({img[i][0]},{img[i][1]}) → {'PQR'[i]}({orig[i][0]},{orig[i][1]})<br>" for i in range(3))
         + rf"<strong>{_fmt_tri(orig)}</strong>")
    hint = "The inverse of a translation by (a,b) is a translation by (−a, −b)."
    return q, s, hint, 2


def _trans_inter_rotation_270():
    tri = _nice_tri()
    # 270° CW = 90° ACW
    img = _apply_rot90acw(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 270° clockwise about the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = (rf"270° clockwise = 90° anticlockwise: \((x, y) \to (-y, x)\).<br>"
         + "".join(rf"{'PQR'[i]}({tri[i][0]},{tri[i][1]}) → {'PQR'[i]}'({img[i][0]},{img[i][1]})<br>" for i in range(3))
         + rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    hint = "270° clockwise = 90° anticlockwise: (x, y) → (−y, x)."
    return q, s, hint, 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _trans_diff_negative_enlarge_describe():
    cx, cy = random.choice([(2, 1), (1, 2), (3, 1), (1, 3), (2, 2), (3, 2),
                             (4, 1), (1, 4), (3, 3), (4, 2), (2, 4)])
    k = random.choice([-2, -3])
    da, db = random.choice([(1, 1), (2, 1), (1, 2)])
    base = [(cx + 1, cy), (cx + 1 + da, cy), (cx + 1, cy + db)]
    img = _enlarge_tri(base, k, cx, cy)
    q = (rf"Triangle PQR has vertices {_fmt_tri(base)}.<br>"
         rf"Its image P'Q'R' has vertices {_fmt_tri(img, primed=True)}.<br>"
         rf"Describe fully the single transformation that maps PQR onto P'Q'R'.")
    s = (rf"The image is larger (not congruent) so it is an enlargement.<br>"
         rf"Scale factor: \(\dfrac{{P'Q'}}{{PQ}} = \dfrac{{{abs(img[1][0]-img[0][0])}}}{{{abs(base[1][0]-base[0][0])}}} = {abs(k)}\)<br>"
         rf"The image is on the opposite side of ({cx},{cy}) from the original → negative scale factor.<br>"
         rf"Checking: \(({cx}+(-2)({base[0][0]}-{cx}),\; {cy}+(-2)({base[0][1]}-{cy}))\) = ({img[0][0]},{img[0][1]}) ✓<br>"
         rf"<strong>Enlargement, scale factor −{abs(k)}, centre ({cx},{cy})</strong>")
    hint = "If the image is on the opposite side of the centre, the scale factor is negative."
    return q, s, hint, 4


def _trans_diff_two_reflections_parallel():
    # Randomly reflect in vertical (x=a, x=b) or horizontal (y=a, y=b) parallel lines
    axis = random.choice(['x', 'y'])
    a = random.randint(0, 4)
    gap = random.randint(2, 6)
    b = a + gap
    tri = _nice_tri()
    if axis == 'x':
        step1 = _apply_refxk(tri, a)
        step2 = _apply_refxk(step1, b)
        ax_a, ax_b = rf"\(x = {a}\)", rf"\(x = {b}\)"
        rule_a = rf"\((x,y)\to({2*a}-x,y)\)"
        rule_b = rf"\((x,y)\to({2*b}-x,y)\)"
        trans_str = _v(2 * (b - a), 0)
        change_desc = rf"each x-coordinate has increased by {2*(b-a)}"
    else:
        step1 = _apply_refyk(tri, a)
        step2 = _apply_refyk(step1, b)
        ax_a, ax_b = rf"\(y = {a}\)", rf"\(y = {b}\)"
        rule_a = rf"\((x,y)\to(x,{2*a}-y)\)"
        rule_b = rf"\((x,y)\to(x,{2*b}-y)\)"
        trans_str = _v(0, 2 * (b - a))
        change_desc = rf"each y-coordinate has increased by {2*(b-a)}"
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"(a) Reflect PQR in the line {ax_a} to give P'Q'R'.<br>"
         rf"(b) Reflect P'Q'R' in the line {ax_b} to give P''Q''R''.<br>"
         rf"(c) Describe the single transformation that maps PQR directly onto P''Q''R''. "
         rf"What general rule does this illustrate?")
    s = (rf"(a) Reflection in {ax_a}: {rule_a}<br>"
         rf"P'Q'R': {_fmt_tri(step1, primed=True)}<br>"
         rf"(b) Reflection in {ax_b}: {rule_b}<br>"
         rf"P''Q''R'': {_fmt_tri(step2, primed=True)}<br>"
         rf"(c) Comparing PQR and P''Q''R'': {change_desc}.<br>"
         rf"<strong>Single transformation: translation by {trans_str}</strong><br>"
         rf"General rule: two reflections in parallel lines, distance \(d\) apart, give a translation of \(2d\) perpendicular to the lines.")
    hint = "Two reflections in parallel lines produce a translation; the distance is twice the gap between the lines."
    return q, s, hint, 5


def _trans_diff_two_reflections_intersecting():
    # Reflect in x-axis (y=0) then reflect in y-axis (x=0) → 180° rotation
    tri = _nice_tri()
    step1 = _apply_refxax(tri)
    step2 = _apply_refyax(step1)
    q = (rf"Triangle T has vertices {_fmt_tri(tri)}.<br>"
         rf"(a) Reflect T in the x-axis to give T'.<br>"
         rf"(b) Reflect T' in the y-axis to give T''.<br>"
         rf"(c) Describe the single transformation that maps T directly onto T''. "
         rf"What general rule does this illustrate?")
    s = (rf"(a) Reflect in x-axis: T' has vertices {_fmt_tri(step1, primed=True)}<br>"
         rf"(b) Reflect in y-axis: T'' has vertices {_fmt_tri(step2, primed=True)}<br>"
         rf"(c) P({tri[0][0]},{tri[0][1]}) → P''({step2[0][0]},{step2[0][1]}): both coordinates negated, i.e. \((x,y)\to(-x,-y)\).<br>"
         rf"<strong>Rotation 180° about the origin (0,0)</strong><br>"
         rf"General rule: two reflections in lines intersecting at angle \(\alpha\) give a rotation of \(2\alpha\) about the intersection. Here \(\alpha=90°\), so rotation = 180°.")
    hint = "Two reflections in intersecting lines give a rotation; the angle is twice the angle between the lines."
    return q, s, hint, 5


def _trans_diff_find_centre_rotation():
    cx, cy = random.choice([(1, 1), (2, 1), (1, 2), (2, 2), (3, 1), (1, 3),
                             (3, 2), (2, 3), (4, 1), (1, 4), (3, 3)])
    direction = random.choice(['clockwise', 'anticlockwise'])
    da, db = random.choice([(1, 1), (2, 1), (1, 2), (2, 2), (3, 1), (1, 3)])
    tri = [(cx + 1, cy), (cx + 1 + da, cy), (cx + 1, cy + db)]
    if direction == 'clockwise':
        img = [_rot90cw_about(x, y, cx, cy) for x, y in tri]
    else:
        img = [_rot90acw_about(x, y, cx, cy) for x, y in tri]
    q = (rf"Under a rotation of 90° {direction}, triangle PQR maps to P'Q'R'.<br>"
         rf"PQR: {_fmt_tri(tri)};  P'Q'R': {_fmt_tri(img, primed=True)}.<br>"
         rf"By finding the perpendicular bisector of PP', determine the centre of rotation.")
    mid = ((tri[0][0] + img[0][0]) / 2, (tri[0][1] + img[0][1]) / 2)
    s = (rf"Midpoint of PP': \(M = \left(\dfrac{{{tri[0][0]}+{img[0][0]}}}{2},\; "
         rf"\dfrac{{{tri[0][1]}+{img[0][1]}}}{2}\right) = ({mid[0]},{mid[1]})\)<br>"
         rf"The direction PP' is ({img[0][0]-tri[0][0]},{img[0][1]-tri[0][1]}); "
         rf"the perpendicular bisector through M is perpendicular to this.<br>"
         rf"Testing ({cx},{cy}): applying 90° {direction} about ({cx},{cy}) gives "
         rf"P({tri[0][0]},{tri[0][1]}) → ({img[0][0]},{img[0][1]}) ✓<br>"
         rf"<strong>Centre of rotation: ({cx},{cy})</strong>")
    hint = "The centre of rotation lies on the perpendicular bisector of every segment joining a point to its image."
    return q, s, hint, 5


def _trans_diff_algebraic_coords():
    a = random.randint(2, 5)
    b = random.randint(1, 4)
    c = random.randint(1, 5)
    d = random.randint(1, 4)
    dx, dy = random.choice([2, 3, 4]), random.choice([-3, -2, -1, 1, 2, 3])
    var = random.choice(['n', 'm', 'k', 't'])
    q_type = random.choice(['rot90cw', 'rot90acw', 'rot180', 'ref_xaxis', 'ref_yaxis', 'ref_yx', 'trans'])
    if q_type == 'rot90cw':
        q = (rf"A point has coordinates (p, q). It is rotated 90° clockwise about the origin.<br>"
             r"Write down the image coordinates in terms of p and q.")
        s = (r"Rotation 90° CW: \((x, y) \to (y, -x)\).<br>"
             r"Applying to (p, q): <strong>(q, −p)</strong>")
        hint = "Apply the rule (x, y) → (y, −x) with x=p and y=q."
    elif q_type == 'rot90acw':
        q = (r"A point has coordinates (p, q). It is rotated 90° anticlockwise about the origin.<br>"
             r"Write down the image coordinates in terms of p and q.")
        s = (r"Rotation 90° ACW: \((x, y) \to (-y, x)\).<br>"
             r"Applying to (p, q): <strong>(−q, p)</strong>")
        hint = "Apply the rule (x, y) → (−y, x) with x=p and y=q."
    elif q_type == 'rot180':
        q = (rf"A point has coordinates ({a}p, {b}q). It is rotated 180° about the origin.<br>"
             r"Write down the image coordinates in terms of p and q.")
        s = (rf"Rotation 180°: \((x, y) \to (-x, -y)\).<br>"
             rf"Applying to ({a}p, {b}q): <strong>(−{a}p, −{b}q)</strong>")
        hint = "Negate both coordinates."
    elif q_type == 'ref_xaxis':
        q = (rf"A point has coordinates ({a}{var}, {b}{var}+{c}). It is reflected in the x-axis.<br>"
             rf"Write down the image coordinates in terms of {var}.")
        s = (r"Reflection in x-axis: \((x, y) \to (x, -y)\).<br>"
             rf"Applying to ({a}{var}, {b}{var}+{c}): <strong>({a}{var}, −{b}{var}−{c})</strong>")
        hint = "Keep x, negate y."
    elif q_type == 'ref_yaxis':
        q = (rf"A point has coordinates ({a}{var}, {var}+{c}). It is reflected in the y-axis.<br>"
             rf"Write down the image coordinates in terms of {var}.")
        s = (r"Reflection in y-axis: \((x, y) \to (-x, y)\).<br>"
             rf"Applying to ({a}{var}, {var}+{c}): <strong>(−{a}{var}, {var}+{c})</strong>")
        hint = "Negate the x-coordinate; leave y unchanged."
    elif q_type == 'ref_yx':
        q = (rf"A point has coordinates ({a}{var}+{b}, {c}{var}). It is reflected in the line y = x.<br>"
             rf"Write down the image coordinates in terms of {var}.")
        s = (r"Reflection in y = x: \((x, y) \to (y, x)\) — swap the coordinates.<br>"
             rf"Applying to ({a}{var}+{b}, {c}{var}): <strong>({c}{var}, {a}{var}+{b})</strong>")
        hint = "Reflection in y = x: swap the two coordinate expressions."
    else:
        q = (rf"A point has coordinates ({var}+{b}, {a}{var}−{c}). It is translated by "
             + _v(dx, dy) + r".<br>"
             rf"Write down the image coordinates in terms of {var}.")
        xi = f"{var}+{b+dx}" if b + dx > 0 else f"{var}{b+dx}"
        yi_a = f"{a}{var}"
        yi_c = -c + dy
        yi = f"{yi_a}+{yi_c}" if yi_c > 0 else f"{yi_a}{yi_c}"
        s = (rf"Translation: add {dx} to x, add {dy} to y.<br>"
             rf"({var}+{b}+{dx}, {a}{var}−{c}+({dy})) = ({xi}, {yi})<br>"
             rf"<strong>Image = ({xi}, {yi})</strong>")
        hint = "Add the vector components to each coordinate expression."
    return q, s, hint, 3


def _trans_diff_area_scale_factor():
    # Given areas, find linear scale factor
    k2 = random.choice([4, 9, 25, 16])
    k = int(k2 ** 0.5)
    area_small = random.randint(3, 12)
    area_large = area_small * k2
    q = (rf"A shape has area {area_small} cm².<br>"
         rf"It is enlarged to give an image with area {area_large} cm².<br>"
         rf"Find the scale factor of the enlargement.")
    s = (rf"Area ratio \(= \dfrac{{{area_large}}}{{{area_small}}} = {k2}\)<br>"
         rf"Linear scale factor \(= \sqrt{{{k2}}} = {k}\)<br>"
         rf"<strong>Scale factor \(= {k}\)</strong>")
    hint = "Area scale factor = (linear scale factor)². Take the square root of the area ratio."
    return q, s, hint, 3


def _trans_diff_three_transformations():
    tri = _nice_tri()
    dx, dy = random.choice([-2, -1, 1, 2]), random.choice([-2, -1, 1, 2])
    ref2 = random.choice(['x-axis', 'y-axis'])
    rot3_dir = random.choice(['clockwise', 'anticlockwise'])
    t1 = _apply_trans(tri, dx, dy)
    t2 = _apply_refxax(t1) if ref2 == 'x-axis' else _apply_refyax(t1)
    t3 = _apply_rot90cw(t2) if rot3_dir == 'clockwise' else _apply_rot90acw(t2)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"The following three transformations are applied in order:<br>"
         rf"T₁: Translation by {_v(dx, dy)}<br>"
         rf"T₂: Reflection in the {ref2}<br>"
         rf"T₃: Rotation 90° {rot3_dir} about the origin<br>"
         rf"Find the final coordinates of triangle P'''Q'''R'''.")
    s = (rf"After T₁ (translate {_v(dx, dy)}): {_fmt_tri(t1, primed=True)}<br>"
         rf"After T₂ (reflect {ref2}): {_fmt_tri(t2, primed=True)}<br>"
         rf"After T₃ (90° {rot3_dir}): {_fmt_tri(t3, primed=True)}<br>"
         rf"<strong>Final image P'''Q'''R''': {_fmt_tri(t3)}</strong>")
    hint = "Apply each transformation in order, using the image of the previous step as the new input."
    return q, s, hint, 5


def _trans_diff_combination_single_equiv():
    # Reflect in x-axis (y=0), then in y=k → translation by 2k in y-direction
    k = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    px, py = random.randint(1, 5), random.randint(2, 7)
    # Step 1: (px, py) → (px, -py)  [reflect in x-axis]
    # Step 2: (px, -py) → (px, 2k - (-py)) = (px, 2k+py)  [reflect in y=k]
    cx_final, cy_final = px, 2 * k + py
    translation_y = 2 * k
    k_str = str(k)
    q = (rf"Shape A is reflected in the x-axis to give shape B.<br>"
         rf"Shape B is then reflected in the line \(y = {k_str}\) to give shape C.<br>"
         rf"(a) If A has a vertex at ({px}, {py}), find the corresponding vertex of C.<br>"
         rf"(b) Describe the single transformation that maps A directly onto C.")
    s = (rf"(a) Reflect ({px},{py}) in x-axis: \(({px},{py})\to({px},{-py})\).<br>"
         rf"Reflect ({px},{-py}) in \(y={k_str}\): \((x,y)\to(x, 2\times{k_str}-y)\): "
         rf"\(({px}, {2*k}-({-py})) = ({cx_final}, {cy_final})\).<br>"
         rf"<strong>Vertex of C: ({cx_final}, {cy_final})</strong><br>"
         rf"(b) Overall: \(({px},{py})\to({cx_final},{cy_final})\), change in y = {translation_y}. Same for all points.<br>"
         rf"<strong>Translation by {_v(0, translation_y)}</strong><br>"
         rf"Rule: two reflections in parallel lines (y=0 and y={k_str}, distance {abs(k)} apart) "
         rf"\u2192 translation of \(2\times{abs(k)}={abs(2*k)}\) in the y-direction.")
    hint = "Apply each reflection in turn, then compare the start and end positions."
    return q, s, hint, 5


def _trans_diff_invariant_rotation():
    q = (r"A rotation of 180° about the origin is applied to a point (a, b).<br>"
         r"(a) Write down the image of (a, b) under this rotation.<br>"
         r"(b) For which points is the point invariant (maps to itself)?<br>"
         r"(c) What is the invariant point of any 180° rotation?")
    s = (r"(a) Rotation 180°: \((a, b) \to (-a, -b)\). <strong>(−a, −b)</strong><br>"
         r"(b) For invariance: −a = a and −b = b, so a = 0 and b = 0.<br>"
         r"<strong>Only the origin (0, 0) is invariant.</strong><br>"
         r"(c) The only invariant point of any 180° rotation is the <strong>centre of rotation</strong>.")
    hint = "A point is invariant if it equals its own image. For 180° rotation, only the centre maps to itself."
    return q, s, hint, 4

_trans_diff_invariant_rotation._fixed_stem = True


def _trans_diff_self_inverse():
    q = (r"A transformation is called <em>self-inverse</em> if applying it twice returns to the original position.<br>"
         r"(a) Explain why a reflection is self-inverse.<br>"
         r"(b) Is a rotation of 90° self-inverse? Justify your answer.<br>"
         r"(c) Give one other self-inverse transformation.")
    s = (r"(a) Applying any reflection twice maps every point back to its original position (reflecting twice in the same mirror line is the identity). "
         r"So reflections are self-inverse.<br>"
         r"<strong>A reflection is self-inverse.</strong><br>"
         r"(b) Applying 90° CW twice gives 180° rotation, not the identity. "
         r"So 90° rotation is <strong>not</strong> self-inverse.<br>"
         r"<strong>90° rotation is NOT self-inverse.</strong><br>"
         r"(c) A rotation of 180° is also self-inverse: two 180° rotations = 360° = identity.<br>"
         r"<strong>180° rotation about any fixed point</strong>")
    hint = "Self-inverse means f(f(x)) = x for all points. Think about what applying the transformation twice does."
    return q, s, hint, 4

_trans_diff_self_inverse._fixed_stem = True


def _trans_diff_fractional_neg_sf():
    k_num, k_den = random.choice([(-1, 2), (-1, 3), (-2, 3)])
    cx, cy = random.choice([(2, 2), (2, 4), (4, 2), (3, 3), (4, 4)])
    mult = k_den
    base = [
        (cx + random.choice([1, 2]) * mult, cy),
        (cx + random.choice([2, 3]) * mult, cy),
        (cx + random.choice([1, 2]) * mult, cy + random.choice([1, 2]) * mult),
    ]
    k = k_num / k_den
    img = [_enlarge_pt(x, y, k, cx, cy) for x, y in base]
    sf_str = (rf"\(-\dfrac{{{abs(k_num)}}}{{{k_den}}}\)" if k_den > 1
              else rf"\(-{abs(k_num)}\)")
    lines = [rf"Enlargement SF {sf_str} about ({cx},{cy}): "
             rf"\((x,y)\to\left({cx}+\frac{{{k_num}}}{{{k_den}}}(x-{cx}),\; {cy}+\frac{{{k_num}}}{{{k_den}}}(y-{cy})\right)\).<br>"]
    for i, (x, y) in enumerate(base):
        ix, iy = img[i]
        lines.append(rf"{'PQR'[i]}({x},{y}) → {'PQR'[i]}'({ix},{iy})<br>")
    lines.append(rf"<strong>{_fmt_tri(img, primed=True)}</strong>")
    q = (rf"Triangle PQR has vertices {_fmt_tri(base)}.<br>"
         rf"Enlarge triangle PQR by scale factor {sf_str}, centre ({cx},{cy}).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = "".join(lines)
    hint = "A negative scale factor means the image appears on the opposite side of the centre."
    return q, s, hint, 4


def _trans_diff_prove_isometry():
    q = (r"Triangle PQR has vertices P(0,0), Q(3,0), R(0,4).<br>"
         r"It is reflected in the y-axis to give P'Q'R'.<br>"
         r"(a) Write down the coordinates of P', Q', R'.<br>"
         r"(b) Show that \(PQ = P'Q'\) and \(PR = P'R'\). What does this tell you about reflections?")
    tri = [(0, 0), (3, 0), (0, 4)]
    img = _apply_refyax(tri)
    pq = ((3 - 0) ** 2 + 0) ** 0.5
    pr = (0 + 4 ** 2) ** 0.5
    ppqq = ((-3 - 0) ** 2 + 0) ** 0.5
    pprr = (0 + 4 ** 2) ** 0.5
    s = (rf"(a) Reflection in y-axis: \((x,y)\to(-x,y)\).<br>"
         rf"P'(0,0), Q'(-3,0), R'(0,4)<br>"
         rf"<strong>P'(0,0), Q'(-3,0), R'(0,4)</strong><br>"
         rf"(b) \(PQ = \sqrt{{3^2+0^2}} = 3\); \(P'Q' = \sqrt{{(-3)^2+0^2}} = 3\). Equal ✓<br>"
         rf"\(PR = \sqrt{{0^2+4^2}} = 4\); \(P'R' = \sqrt{{0^2+4^2}} = 4\). Equal ✓<br>"
         rf"<strong>Reflection preserves all lengths — it is an isometry (congruence transformation).</strong>")
    hint = "Calculate lengths using the distance formula √[(x₂−x₁)²+(y₂−y₁)²] for both original and image."
    return q, s, hint, 4

_trans_diff_prove_isometry._fixed_stem = True


def _trans_diff_congruent_similar():
    q = (r"For each transformation below, state whether the image is congruent to the original, similar but not congruent, or neither:<br>"
         r"(a) Rotation 90° clockwise about the origin<br>"
         r"(b) Enlargement, scale factor 3, centre (0,0)<br>"
         r"(c) Enlargement, scale factor −1, centre (1,2)<br>"
         r"(d) Translation by \(\begin{pmatrix}5\\-2\end{pmatrix}\)")
    s = (r"(a) Rotation preserves lengths and angles — the image is <strong>congruent</strong>.<br>"
         r"(b) Enlargement by 3 changes all lengths by factor 3 but preserves angles — <strong>similar but not congruent</strong>.<br>"
         r"(c) Enlargement by −1 maps every point through the centre; lengths are unchanged (\(|{-1}|=1\)) — the image is <strong>congruent</strong> (this is actually a rotation of 180° about the centre).<br>"
         r"(d) Translation shifts position but changes nothing else — the image is <strong>congruent</strong>.")
    hint = "Isometries (rotation, reflection, translation) give congruent images. Enlargements with |k|≠1 give similar images."
    return q, s, hint, 4

_trans_diff_congruent_similar._fixed_stem = True


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (15 questions)
# ══════════════════════════════════════════════════════════════════════════════

_TRANS_MCQ_BANK = [
    {
        "q": r"The point (3, 4) is reflected in the x-axis. What are the new coordinates?",
        "opts": ["A  (3, −4)", "B  (−3, 4)", "C  (4, 3)", "D  (−3, −4)"],
        "ans": "A",
        "sol": r"Reflection in x-axis: \((x,y)\to(x,-y)\). So \((3,4)\to(3,-4)\).",
    },
    {
        "q": r"The point (2, 5) is reflected in the y-axis. What are the new coordinates?",
        "opts": ["A  (−2, 5)", "B  (2, −5)", "C  (5, 2)", "D  (−5, −2)"],
        "ans": "A",
        "sol": r"Reflection in y-axis: \((x,y)\to(-x,y)\). So \((2,5)\to(-2,5)\).",
    },
    {
        "q": r"What is the image of (3, 1) under a rotation of 90° clockwise about the origin?",
        "opts": ["A  (1, −3)", "B  (−1, 3)", "C  (−3, −1)", "D  (3, −1)"],
        "ans": "A",
        "sol": r"90° CW: \((x,y)\to(y,-x)\). So \((3,1)\to(1,-3)\).",
    },
    {
        "q": r"Which transformation maps (4, 2) to (−4, 2)?",
        "opts": ["A  Reflection in the y-axis", "B  Reflection in the x-axis",
                 "C  Rotation 90° CW", "D  Translation by (−8, 0)"],
        "ans": "A",
        "sol": r"Reflection in y-axis negates the x-coordinate: \((4,2)\to(-4,2)\).",
    },
    {
        "q": r"The point (2, 3) is reflected in the line \(y = x\). What are the new coordinates?",
        "opts": ["A  (3, 2)", "B  (2, −3)", "C  (−2, 3)", "D  (−3, −2)"],
        "ans": "A",
        "sol": r"Reflection in \(y=x\): swap coordinates. \((2,3)\to(3,2)\).",
    },
    {
        "q": r"A triangle with area 5 cm² is enlarged by scale factor 4. What is the area of the image?",
        "opts": ["A  80 cm²", "B  20 cm²", "C  40 cm²", "D  16 cm²"],
        "ans": "A",
        "sol": r"Area scale factor = \(4^2 = 16\). Area of image = \(5 \times 16 = 80\) cm².",
    },
    {
        "q": r"Which of the following transformations does NOT preserve lengths?",
        "opts": ["A  Enlargement (scale factor 2)", "B  Reflection", "C  Translation", "D  Rotation 90°"],
        "ans": "A",
        "sol": r"An enlargement changes all lengths by the scale factor, so lengths are not preserved.",
    },
    {
        "q": r"What is the image of (0, 3) under rotation 180° about the origin?",
        "opts": ["A  (0, −3)", "B  (3, 0)", "C  (−3, 0)", "D  (0, 3)"],
        "ans": "A",
        "sol": r"Rotation 180°: \((x,y)\to(-x,-y)\). So \((0,3)\to(0,-3)\).",
    },
    {
        "q": r"A shape is translated by \(\begin{pmatrix}−2\\5\end{pmatrix}\). Which statement is true?",
        "opts": [
            "A  Each point moves 2 left and 5 up",
            "B  Each point moves 2 right and 5 down",
            "C  The shape is rotated",
            "D  The shape changes size",
        ],
        "ans": "A",
        "sol": r"\(\begin{pmatrix}-2\\5\end{pmatrix}\) means −2 in x (left) and +5 in y (up).",
    },
    {
        "q": r"Triangle PQR is enlarged by scale factor 3, centre the origin. If P = (2, 1), where is P'?",
        "opts": ["A  (6, 3)", "B  (5, 4)", "C  (2, 3)", "D  (3, 2)"],
        "ans": "A",
        "sol": r"Enlargement SF 3 about origin: \((2,1)\to(6,3)\).",
    },
    {
        "q": r"What is the image of (5, 2) under a reflection in the line \(x = 3\)?",
        "opts": ["A  (1, 2)", "B  (5, 4)", "C  (−5, 2)", "D  (3, 2)"],
        "ans": "A",
        "sol": r"Reflection in \(x=3\): \((x,y)\to(6-x,y)\). \((5,2)\to(1,2)\).",
    },
    {
        "q": r"A rotation of 90° anticlockwise about the origin maps (a, b) to:",
        "opts": [r"A  \((-b, a)\)", r"B  \((b, -a)\)", r"C  \((-a, -b)\)", r"D  \((b, a)\)"],
        "ans": "A",
        "sol": r"90° ACW: \((x,y)\to(-y,x)\). So \((a,b)\to(-b,a)\).",
    },
    {
        "q": r"Shape A is reflected in the x-axis then in the y-axis. The single equivalent transformation is:",
        "opts": [
            "A  Rotation 180° about the origin",
            "B  Rotation 90° CW about the origin",
            "C  Translation",
            "D  Reflection in y = x",
        ],
        "ans": "A",
        "sol": r"Reflect in x-axis: \((x,y)\to(x,-y)\). Reflect in y-axis: \((x,-y)\to(-x,-y)\). Combined: 180° rotation about origin.",
    },
    {
        "q": r"Two parallel mirror lines are 4 cm apart. A shape is reflected in both lines. The single equivalent transformation is a translation of:",
        "opts": ["A  8 cm", "B  4 cm", "C  2 cm", "D  16 cm"],
        "ans": "A",
        "sol": r"Two reflections in parallel lines distance \(d\) apart give a translation of \(2d = 2 \times 4 = 8\) cm.",
    },
    {
        "q": r"A shape has area 12 cm². Its image under an enlargement has area 108 cm². What is the scale factor?",
        "opts": ["A  3", "B  9", "C  √3", "D  6"],
        "ans": "A",
        "sol": r"Area ratio = 108 ÷ 12 = 9. Scale factor = \(\sqrt{9} = 3\).",
    },
]


def transformations_mcq():
    chosen = random.choice(_TRANS_MCQ_BANK)
    q = chosen["q"]
    options = chosen["opts"]
    correct = chosen["ans"]
    s = f"<strong>Answer: {correct}</strong><br><br>{chosen['sol']}"
    return q, s, chosen["sol"], 1, options, correct


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_transformations_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _TRANS_MCQ_BANK, procedural_mcq_for('transformations'), 'transformations', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _trans_found_translate,
            _trans_found_reflect_xaxis,
            _trans_found_reflect_yaxis,
            _trans_found_reflect_yx,
            _trans_found_rotate_90cw,
            _trans_found_rotate_180,
            _trans_found_enlarge_origin,
            _trans_found_describe_translation,
            _trans_found_describe_reflection_axis,
            _trans_found_describe_rotation_90,
            _trans_found_describe_rotation_180,
            _trans_found_reflect_xk,
            _trans_found_reflect_yk,
            _trans_found_rotate_90acw,
            _trans_found_identify_type,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _trans_inter_reflect_y_neg_x,
            _trans_inter_enlarge_not_origin,
            _trans_inter_rotate_not_origin,
            _trans_inter_enlarge_frac_sf,
            _trans_inter_describe_enlargement_full,
            _trans_inter_find_centre_enlargement,
            _trans_inter_enlarge_neg_sf,
            _trans_inter_reflect_oblique,
            _trans_inter_invariant_reflection,
            _trans_inter_area_after_enlargement,
            _trans_inter_combination_reflect_reflect,
            _trans_inter_describe_rotation_full,
            _trans_inter_reverse_transformation,
            _trans_inter_rotation_270,
            _trans_inter_describe_enlargement_full,  # reuse for pool size
        ]
    elif difficulty == 'difficult':
        pool = [
            _trans_diff_negative_enlarge_describe,
            _trans_diff_two_reflections_parallel,
            _trans_diff_two_reflections_intersecting,
            _trans_diff_find_centre_rotation,
            _trans_diff_algebraic_coords,
            _trans_diff_area_scale_factor,
            _trans_diff_three_transformations,
            _trans_diff_combination_single_equiv,
            _trans_diff_invariant_rotation,
            _trans_diff_self_inverse,
            _trans_diff_fractional_neg_sf,
            _trans_diff_prove_isometry,
            _trans_diff_congruent_similar,
            _trans_diff_negative_enlarge_describe,  # reuse for pool
            _trans_diff_algebraic_coords,           # reuse for pool
        ]
    else:  # mixed
        found = random.sample([
            _trans_found_translate, _trans_found_reflect_xaxis,
            _trans_found_rotate_90cw, _trans_found_enlarge_origin,
        ], 3)
        inter = random.sample([
            _trans_inter_enlarge_not_origin, _trans_inter_enlarge_neg_sf,
            _trans_inter_area_after_enlargement, _trans_inter_combination_reflect_reflect,
        ], 4)
        diff = random.sample([
            _trans_diff_two_reflections_parallel, _trans_diff_area_scale_factor,
            _trans_diff_algebraic_coords,
        ], 3)
        return found + inter + diff

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors exactly)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_transformations(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_transformations_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'transformations',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_transformations_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    result = variant()
    if len(result) == 5:  # MCQ
        q, s, hint, marks, opts, correct = result
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'transformations',
                            options=opts, correct_answer=correct)
    q, s, hint, marks = result
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'transformations')
