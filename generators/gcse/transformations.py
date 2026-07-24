"""
GCSE Maths – Transformations
15 foundational · 15 intermediate · 15 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
Final answers are wrapped in <strong> tags.
"""
import random
from generators.shared.utils import (
    make_problem,
    make_graded_problem,
    graded_answer_number,
    graded_answer_keyword,
    graded_answer_number_pair,
    graded_answer_number_fields,
    graded_answer_tri_coords,
)
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


def _trans_describe_mcq(q, s, hint, marks, correct, distractors):
    """Return a 6-tuple MCQ for 'describe fully' transformation questions."""
    choices = [correct] + list(distractors[:3])
    random.shuffle(choices)
    letters = 'ABCD'
    correct_letter = letters[choices.index(correct)]
    opts = [f"{letters[i]}  {choices[i]}" for i in range(4)]
    return q, s, hint, marks, opts, correct_letter


def _trans_mcq_field(correct_text, distractors):
    """Build shuffled 3-option inline MCQ; returns (option_texts, correct_letter)."""
    pool = [correct_text] + list(distractors[:2])
    random.shuffle(pool)
    letters = 'ABC'
    return pool, letters[pool.index(correct_text)]


_CONGRUENCE_MCQ_OPTIONS = (
    'Congruent',
    'Similar but not congruent',
    'Neither',
)


def _trans_congruence_mcq_field(correct):
    """Fixed 3-option MCQ for congruent / similar / neither questions."""
    distractors = [o for o in _CONGRUENCE_MCQ_OPTIONS if o != correct]
    return _trans_mcq_field(correct, distractors)


def _trans_cs_item_rotation():
    angle = random.choice([90, 180, 270])
    if angle == 180:
        desc = "Rotation 180° about the origin (0,0)"
        reason = "Rotation 180° preserves lengths and angles"
    else:
        direction = random.choice(['clockwise', 'anticlockwise'])
        desc = f"Rotation {angle}° {direction} about the origin"
        reason = f"Rotation {angle}° preserves lengths and angles"
    return desc, 'Congruent', reason


def _trans_cs_item_reflection():
    kind = random.choice(['x', 'y', 'yx', 'xk', 'yk'])
    if kind == 'x':
        desc = "Reflection in the x-axis"
    elif kind == 'y':
        desc = "Reflection in the y-axis"
    elif kind == 'yx':
        desc = r"Reflection in the line \(y = x\)"
    elif kind == 'xk':
        k = random.choice([1, 2, 3, 4])
        desc = rf"Reflection in the line \(x = {k}\)"
    else:
        k = random.choice([1, 2, 3, 4])
        desc = rf"Reflection in the line \(y = {k}\)"
    return desc, 'Congruent', "Reflection preserves lengths and angles"


def _trans_cs_item_translation():
    dx = random.randint(-6, 6)
    dy = random.randint(-6, 6)
    while dx == 0 and dy == 0:
        dx = random.randint(-6, 6)
        dy = random.randint(-6, 6)
    desc = f"Translation by the vector {_v(dx, dy)}"
    return desc, 'Congruent', "Translation preserves lengths and angles"


def _trans_cs_item_enlargement_similar():
    k = random.choice([2, 3, 4, 5, -2, -3, -4])
    cx, cy = random.choice([(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2)])
    k_str = str(k) if k > 0 else f"−{abs(k)}"
    desc = f"Enlargement, scale factor {k_str}, centre ({cx},{cy})"
    reason = (
        rf"Enlargement by {k_str} scales all lengths by {abs(k)} "
        rf"but preserves angles"
    )
    return desc, 'Similar but not congruent', reason


def _trans_cs_item_enlargement_congruent():
    cx, cy = random.choice([(0, 0), (1, 2), (2, 1), (3, 1), (1, 3), (2, 2)])
    desc = f"Enlargement, scale factor −1, centre ({cx},{cy})"
    reason = "Enlargement by −1 preserves lengths (|−1| = 1)"
    return desc, 'Congruent', reason


def _trans_cs_pick_items():
    """Pick four distinct transformations with at least one similar-not-congruent."""
    similar = _trans_cs_item_enlargement_similar()
    builders = (
        _trans_cs_item_rotation,
        _trans_cs_item_reflection,
        _trans_cs_item_translation,
        _trans_cs_item_enlargement_congruent,
    )
    items = [similar]
    seen = {similar[0]}
    shuffled = list(builders)
    random.shuffle(shuffled)
    for builder in shuffled:
        if len(items) >= 4:
            break
        item = builder()
        if item[0] in seen:
            continue
        items.append(item)
        seen.add(item[0])
    attempts = 0
    while len(items) < 4 and attempts < 30:
        item = random.choice(builders)()
        attempts += 1
        if item[0] in seen:
            continue
        items.append(item)
        seen.add(item[0])
    random.shuffle(items)
    return items


def _trans_double_reflect_graded(step1, step2, *, correct_c, distractors_c):
    """Grade double reflection: (a) first image coords, (b) second, (c) single transform MCQ."""
    values = []
    labels = []
    row_sizes = []
    group_labels = []
    for pts, part, names in (
        (step1, '(a)', ("P'", "Q'", "R'")),
        (step2, '(b)', ("P''", "Q''", "R''")),
    ):
        for name, (x, y) in zip(names, pts):
            values.extend([x, y])
            labels.extend(['x', 'y'])
            row_sizes.append(2)
            group_labels.append(f'{part} {name}')
    opts_c, ans_c = _trans_mcq_field(correct_c, distractors_c)
    values.append(ans_c)
    labels.append('Single transformation')
    row_sizes.append(1)
    group_labels.append('(c)')
    field_count = len(values)
    return graded_answer_number_fields(
        tuple(values),
        tuple(labels),
        field_types=tuple(['number'] * (field_count - 1) + ['mcq']),
        field_options=tuple([None] * (field_count - 1) + [opts_c]),
        row_sizes=tuple(row_sizes),
        group_labels=tuple(group_labels),
        format_hint='Enter each coordinate; choose the best option for (c)',
        inline_sections=True,
    )


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
    return q, s, hint, 2, graded_answer_tri_coords(img)


def _trans_found_reflect_xaxis():
    tri = _nice_tri()
    img = _apply_refxax(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the x-axis.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Reflection in the x-axis: \((x, y) \to (x, -y)\) — negate the y-coordinate.")
    hint = "Reflection in the x-axis: keep x, change the sign of y."
    return q, s, hint, 2, graded_answer_tri_coords(img)


def _trans_found_reflect_yaxis():
    tri = _nice_tri()
    img = _apply_refyax(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the y-axis.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Reflection in the y-axis: \((x, y) \to (-x, y)\) — negate the x-coordinate.")
    hint = "Reflection in the y-axis: change the sign of x, keep y."
    return q, s, hint, 2, graded_answer_tri_coords(img)


def _trans_found_reflect_yx():
    tri = _nice_tri()
    img = _apply_refyx(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Reflect triangle PQR in the line \(y = x\).<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Reflection in \(y = x\): \((x, y) \to (y, x)\) — swap x and y.")
    hint = r"Reflection in y = x: swap the two coordinates."
    return q, s, hint, 2, graded_answer_tri_coords(img)


def _trans_found_rotate_90cw():
    tri = _nice_tri()
    img = _apply_rot90cw(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 90° clockwise about the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Rotation 90° CW about origin: \((x, y) \to (y, -x)\).")
    hint = "90° clockwise about the origin: (x, y) → (y, −x)."
    return q, s, hint, 2, graded_answer_tri_coords(img)


def _trans_found_rotate_180():
    tri = _nice_tri()
    img = _apply_rot180(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 180° about the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Rotation 180° about origin: \((x, y) \to (-x, -y)\) — negate both coordinates.")
    hint = "180° rotation about origin: negate both x and y."
    return q, s, hint, 2, graded_answer_tri_coords(img)


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
    return q, s, hint, 2, graded_answer_tri_coords(img)


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
    correct = f"Translation by the vector {_v(dx, dy)}"
    distractors = [
        f"Translation by the vector {_v(-dx, -dy)}",
        f"Translation by the vector {_v(dy, dx)}",
        "Reflection in the x-axis",
        "Rotation 90° clockwise, centre the origin (0,0)",
    ]
    return _trans_describe_mcq(q, s, hint, 2, correct, distractors)


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
    other = "y-axis" if axis == 'x' else "x-axis"
    correct = f"Reflection in the {ax_name}"
    distractors = [
        f"Reflection in the {other}",
        "Rotation 180°, centre the origin (0,0)",
        "Rotation 90° clockwise, centre the origin (0,0)",
        f"Translation by the vector {_v(1, 1)}",
    ]
    return _trans_describe_mcq(q, s, hint, 2, correct, distractors)


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
    correct = f"Rotation 90° {direction}, centre the origin (0,0)"
    opposite = 'anticlockwise' if direction == 'clockwise' else 'clockwise'
    distractors = [
        f"Rotation 90° {opposite}, centre the origin (0,0)",
        "Rotation 180°, centre the origin (0,0)",
        "Reflection in the x-axis",
        "Reflection in the y-axis",
    ]
    return _trans_describe_mcq(q, s, hint, 3, correct, distractors)


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
    correct = "Rotation 180°, centre the origin (0,0)"
    distractors = [
        "Reflection in the x-axis",
        "Reflection in the y-axis",
        "Rotation 90° clockwise, centre the origin (0,0)",
        f"Translation by the vector {_v(-2, -2)}",
    ]
    return _trans_describe_mcq(q, s, hint, 3, correct, distractors)


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
    return q, s, hint, 2, graded_answer_tri_coords(img)


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
    return q, s, hint, 2, graded_answer_tri_coords(img)


def _trans_found_rotate_90acw():
    tri = _nice_tri()
    img = _apply_rot90acw(tri)
    q = (rf"Triangle PQR has vertices {_fmt_tri(tri)}.<br>"
         rf"Rotate triangle PQR by 90° anticlockwise about the origin.<br>"
         rf"Write down the coordinates of P'Q'R'.")
    s = _sol_steps(tri, img, r"Rotation 90° ACW about origin: \((x, y) \to (-y, x)\).")
    hint = "90° anticlockwise: (x, y) → (−y, x)."
    return q, s, hint, 2, graded_answer_tri_coords(img)


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
    return q, s, hint, 1, graded_answer_keyword(name.lower())


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
    return q, s, hint, 2, graded_answer_tri_coords(img)


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
    return q, s, hint, 3, graded_answer_tri_coords(img)


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
    return q, s, hint, 3, graded_answer_tri_coords(img)


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
    return q, s, hint, 3, graded_answer_tri_coords(img)


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
    correct = f"Enlargement, scale factor {k}, centre ({cx},{cy})"
    wrong_k = k + 1 if k < 4 else k - 1
    distractors = [
        f"Enlargement, scale factor {wrong_k}, centre ({cx},{cy})",
        f"Enlargement, scale factor {k}, centre ({cx + 1},{cy})",
        f"Translation by the vector {_v(k, k)}",
        "Rotation 90° clockwise, centre the origin (0,0)",
    ]
    return _trans_describe_mcq(q, s, hint, 3, correct, distractors)


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
         rf"Line PP': from ({base[0][0]},{base[0][1]}) to ({img[0][0]},{img[0][1]}) "
         rf"→ passes through ({cx},{cy}).<br>"
         rf"<strong>Centre of enlargement = ({cx}, {cy})</strong>")
    hint = "Draw straight lines through each vertex and its image — they all meet at the centre."
    return q, s, hint, 4, graded_answer_number_fields(
        (sf, cx, cy),
        ('Scale factor', 'Centre x', 'Centre y'),
    )


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
    return q, s, hint, 3, graded_answer_tri_coords(img)


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
    return q, s, hint, 3, graded_answer_tri_coords(img)


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
        deduce_label = "What can you deduce about b?"
        deduce_correct = r"\(b = 0\)"
        deduce_distractors = [r"\(a = 0\)", r"\(b = a\)", r"\(a = -b\)"]
        ex = random.randint(2, 7)
        example_correct = f"({ex}, 0)"
        example_distractors = [f"(0, {ex})", f"({ex}, {ex})", "(0, 0)"]
    else:
        q = (r"Under a reflection in the y-axis, a point P(a, b) maps to itself (P is an invariant point).<br>"
             r"What can you deduce about a? Give an example of an invariant point.")
        s = (r"Reflection in the y-axis: \((a, b) \to (-a, b)\).<br>"
             r"For P to map to itself: \(a = -a \Rightarrow a = 0\).<br>"
             r"Every point on the y-axis is invariant.<br>"
             r"<strong>\(a = 0\); for example, (0, 5) is invariant</strong>")
        hint = "A point is invariant if it maps to itself. Find when (a,b) = (−a,b)."
        deduce_label = "What can you deduce about a?"
        deduce_correct = r"\(a = 0\)"
        deduce_distractors = [r"\(b = 0\)", r"\(a = b\)", r"\(a = -b\)"]
        ex = random.randint(2, 7)
        example_correct = f"(0, {ex})"
        example_distractors = [f"({ex}, 0)", f"(0, -{ex})", "(0, 0)"]
    deduce_opts, deduce_ans = _trans_mcq_field(deduce_correct, deduce_distractors)
    example_opts, example_ans = _trans_mcq_field(example_correct, example_distractors)
    return q, s, hint, 3, graded_answer_number_fields(
        (deduce_ans, example_ans),
        (deduce_label, "Example of an invariant point"),
        field_types=('mcq', 'mcq'),
        field_options=(deduce_opts, example_opts),
        format_hint='Choose the correct option for each part',
    )

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
    return q, s, hint, 3, graded_answer_number(new_area)


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
    return q, s, hint, 4, _trans_double_reflect_graded(
        step1, step2,
        correct_c="Rotation 180°, centre the origin (0,0)",
        distractors_c=[
            "Rotation 90° clockwise, centre the origin (0,0)",
            "Reflection in the x-axis",
            "Translation by the vector (0, 0)",
        ],
    )


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
    correct = f"Rotation 90° {dir_desc}, centre ({cx},{cy})"
    opposite = 'anticlockwise' if direction == 'clockwise' else 'clockwise'
    distractors = [
        f"Rotation 90° {opposite}, centre ({cx},{cy})",
        f"Rotation 90° {dir_desc}, centre ({cx + 1},{cy})",
        f"Rotation 180°, centre ({cx},{cy})",
        "Reflection in the x-axis",
    ]
    return _trans_describe_mcq(q, s, hint, 4, correct, distractors)


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
    return q, s, hint, 2, graded_answer_tri_coords(orig, vertex_labels=('P', 'Q', 'R'))


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
    return q, s, hint, 2, graded_answer_tri_coords(img)


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
    correct = f"Enlargement, scale factor −{abs(k)}, centre ({cx},{cy})"
    distractors = [
        f"Enlargement, scale factor {abs(k)}, centre ({cx},{cy})",
        f"Enlargement, scale factor −{abs(k) + 1}, centre ({cx},{cy})",
        f"Enlargement, scale factor −{abs(k)}, centre ({cx + 1},{cy})",
        "Reflection in the x-axis",
    ]
    return _trans_describe_mcq(q, s, hint, 4, correct, distractors)


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
        trans_dx, trans_dy = 2 * (b - a), 0
        trans_str = _v(trans_dx, trans_dy)
        change_desc = rf"each x-coordinate has increased by {trans_dx}"
        distractors_c = [
            f"Translation by the vector {_v(-trans_dx, 0)}",
            f"Translation by the vector {_v(0, trans_dx)}",
            "Rotation 180°, centre the origin (0,0)",
        ]
    else:
        step1 = _apply_refyk(tri, a)
        step2 = _apply_refyk(step1, b)
        ax_a, ax_b = rf"\(y = {a}\)", rf"\(y = {b}\)"
        rule_a = rf"\((x,y)\to(x,{2*a}-y)\)"
        rule_b = rf"\((x,y)\to(x,{2*b}-y)\)"
        trans_dx, trans_dy = 0, 2 * (b - a)
        trans_str = _v(trans_dx, trans_dy)
        change_desc = rf"each y-coordinate has increased by {trans_dy}"
        distractors_c = [
            f"Translation by the vector {_v(0, -trans_dy)}",
            f"Translation by the vector {_v(trans_dy, 0)}",
            "Rotation 180°, centre the origin (0,0)",
        ]
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
    return q, s, hint, 5, _trans_double_reflect_graded(
        step1, step2,
        correct_c=f"Translation by the vector {trans_str}",
        distractors_c=distractors_c,
    )


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
    return q, s, hint, 5, _trans_double_reflect_graded(
        step1, step2,
        correct_c="Rotation 180°, centre the origin (0,0)",
        distractors_c=[
            "Rotation 90° clockwise, centre the origin (0,0)",
            "Reflection in the x-axis",
            "Translation by the vector (0, 0)",
        ],
    )


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
    return q, s, hint, 5, graded_answer_number_pair(cx, cy, 'Centre x', 'Centre y')


def _trans_diff_algebraic_coords():
    a = random.randint(2, 5)
    b = random.randint(1, 4)
    c = random.randint(1, 5)
    d = random.randint(1, 4)
    dx, dy = random.choice([2, 3, 4]), random.choice([-3, -2, -1, 1, 2, 3])
    var = random.choice(['n', 'm', 'k', 't'])
    q_type = random.choice(['rot90cw', 'rot90acw', 'rot180', 'ref_xaxis', 'ref_yaxis', 'ref_yx', 'trans'])
    ans_x = ans_y = None
    if q_type == 'rot90cw':
        q = (rf"A point has coordinates (p, q). It is rotated 90° clockwise about the origin.<br>"
             r"Write down the image coordinates in terms of p and q.")
        s = (r"Rotation 90° CW: \((x, y) \to (y, -x)\).<br>"
             r"Applying to (p, q): <strong>(q, −p)</strong>")
        hint = "Apply the rule (x, y) → (y, −x) with x=p and y=q."
        ans_x, ans_y = 'q', '-p'
    elif q_type == 'rot90acw':
        q = (r"A point has coordinates (p, q). It is rotated 90° anticlockwise about the origin.<br>"
             r"Write down the image coordinates in terms of p and q.")
        s = (r"Rotation 90° ACW: \((x, y) \to (-y, x)\).<br>"
             r"Applying to (p, q): <strong>(−q, p)</strong>")
        hint = "Apply the rule (x, y) → (−y, x) with x=p and y=q."
        ans_x, ans_y = '-q', 'p'
    elif q_type == 'rot180':
        q = (rf"A point has coordinates ({a}p, {b}q). It is rotated 180° about the origin.<br>"
             r"Write down the image coordinates in terms of p and q.")
        s = (rf"Rotation 180°: \((x, y) \to (-x, -y)\).<br>"
             rf"Applying to ({a}p, {b}q): <strong>(−{a}p, −{b}q)</strong>")
        hint = "Negate both coordinates."
        ans_x, ans_y = f'-{a}p', f'-{b}q'
    elif q_type == 'ref_xaxis':
        q = (rf"A point has coordinates ({a}{var}, {b}{var}+{c}). It is reflected in the x-axis.<br>"
             rf"Write down the image coordinates in terms of {var}.")
        s = (r"Reflection in x-axis: \((x, y) \to (x, -y)\).<br>"
             rf"Applying to ({a}{var}, {b}{var}+{c}): <strong>({a}{var}, −{b}{var}−{c})</strong>")
        hint = "Keep x, negate y."
        ans_x, ans_y = f'{a}{var}', f'-{b}{var}-{c}'
    elif q_type == 'ref_yaxis':
        q = (rf"A point has coordinates ({a}{var}, {var}+{c}). It is reflected in the y-axis.<br>"
             rf"Write down the image coordinates in terms of {var}.")
        s = (r"Reflection in y-axis: \((x, y) \to (-x, y)\).<br>"
             rf"Applying to ({a}{var}, {var}+{c}): <strong>(−{a}{var}, {var}+{c})</strong>")
        hint = "Negate the x-coordinate; leave y unchanged."
        ans_x, ans_y = f'-{a}{var}', f'{var}+{c}'
    elif q_type == 'ref_yx':
        q = (rf"A point has coordinates ({a}{var}+{b}, {c}{var}). It is reflected in the line y = x.<br>"
             rf"Write down the image coordinates in terms of {var}.")
        s = (r"Reflection in y = x: \((x, y) \to (y, x)\) — swap the coordinates.<br>"
             rf"Applying to ({a}{var}+{b}, {c}{var}): <strong>({c}{var}, {a}{var}+{b})</strong>")
        hint = "Reflection in y = x: swap the two coordinate expressions."
        ans_x, ans_y = f'{c}{var}', f'{a}{var}+{b}'
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
        ans_x, ans_y = xi, yi
    return q, s, hint, 3, graded_answer_number_fields(
        (ans_x, ans_y),
        ('x', 'y'),
        ('algebraic', 'algebraic'),
        row_sizes=(2,),
        group_labels=('Image',),
        format_hint='Enter each coordinate expression',
    )


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
    return q, s, hint, 3, graded_answer_number(k)


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
    return q, s, hint, 5, graded_answer_tri_coords(t3)


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
    correct_b = f"Translation by the vector {_v(0, translation_y)}"
    distractors_b = [
        f"Translation by the vector {_v(translation_y, 0)}",
        f"Translation by the vector {_v(0, -translation_y)}",
        "Reflection in the x-axis",
    ]
    opts_b, ans_b = _trans_mcq_field(correct_b, distractors_b)
    return q, s, hint, 5, graded_answer_number_fields(
        (cx_final, cy_final, ans_b),
        ('Vertex x', 'Vertex y', 'Single transformation'),
        field_types=('number', 'number', 'mcq'),
        field_options=(None, None, opts_b),
        row_sizes=(2, 1),
        group_labels=('(a)', '(b)'),
        format_hint='Enter coordinates for (a); choose the best option for (b)',
        inline_sections=True,
    )


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
    opts_c, ans_c = _trans_mcq_field(
        "The centre of rotation",
        [
            "Any point on the x-axis",
            "Every point on the shape",
        ],
    )
    return q, s, hint, 4, graded_answer_number_fields(
        ('(-a,-b)', 'origin', ans_c),
        (
            "(a) Image of (a, b)",
            "(b) Invariant points",
            "(c) Invariant point of any 180° rotation",
        ),
        field_types=('algebraic', 'keyword', 'mcq'),
        field_options=(None, None, opts_c),
        format_hint='Enter each answer; use coordinates where appropriate',
    )

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
    opts_a, ans_a = _trans_mcq_field(
        "Reflecting twice in the same mirror line returns every point to its original position",
        [
            "A reflection only moves points once, so it cannot be undone",
            "Reflections change the size of the shape",
        ],
    )
    opts_b, ans_b = _trans_mcq_field(
        "No — applying 90° twice gives 180°, not the identity",
        [
            "Yes — two 90° rotations always return to the start",
            "Yes — every rotation is self-inverse",
        ],
    )
    opts_c, ans_c = _trans_mcq_field(
        "180° rotation about any fixed point",
        [
            "Translation by any non-zero vector",
            "Enlargement with scale factor 2",
        ],
    )
    return q, s, hint, 4, graded_answer_number_fields(
        (ans_a, ans_b, ans_c),
        (
            "(a) Why is a reflection self-inverse?",
            "(b) Is a rotation of 90° self-inverse?",
            "(c) One other self-inverse transformation",
        ),
        field_types=('mcq', 'mcq', 'mcq'),
        field_options=(opts_a, opts_b, opts_c),
        format_hint='Choose the best answer for each part',
    )

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
    return q, s, hint, 4, graded_answer_tri_coords(img)


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
    return q, s, hint, 4, graded_answer_tri_coords(img)

_trans_diff_prove_isometry._fixed_stem = True


def _trans_diff_congruent_similar():
    items = _trans_cs_pick_items()
    part_labels = ('(a)', '(b)', '(c)', '(d)')
    q_lines = [
        r"For each transformation below, state whether the image is congruent "
        r"to the original, similar but not congruent, or neither:<br>",
    ]
    s_lines = []
    answers = []
    field_options = []
    for label, (desc, category, reason) in zip(part_labels, items):
        q_lines.append(f"{label} {desc}<br>")
        cat_lower = (
            category.lower()
            if category == 'Congruent'
            else category
        )
        s_lines.append(f"{label} {reason} — <strong>{cat_lower}</strong>.")
        opts, ans = _trans_congruence_mcq_field(category)
        answers.append(ans)
        field_options.append(opts)
    q = ''.join(q_lines)
    s = '<br>'.join(s_lines)
    hint = (
        "Isometries (rotation, reflection, translation) give congruent images. "
        "Enlargements with |k|≠1 give similar images."
    )
    return q, s, hint, 4, graded_answer_number_fields(
        tuple(answers),
        ('', '', '', ''),
        field_types=('mcq', 'mcq', 'mcq', 'mcq'),
        field_options=tuple(field_options),
        row_sizes=(1, 1, 1, 1),
        group_labels=part_labels,
        format_hint='Choose congruent, similar but not congruent, or neither',
        inline_sections=True,
    )


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
    if len(result) == 6:
        q, s, hint, marks, opts, correct = result
        return make_problem(
            q, s, hint, difficulty, marks,
            'gcse', 'maths', 'transformations',
            options=opts, correct_answer=correct,
        )
    return make_graded_problem(result, difficulty, 'gcse', 'maths', 'transformations')
