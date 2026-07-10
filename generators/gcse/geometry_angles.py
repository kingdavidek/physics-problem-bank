"""
GCSE Maths – Geometry and Angles
15 foundational · 15 intermediate · 15 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
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


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _geom_found_straight_line():
    a = random.randint(35, 145)
    b = 180 - a
    q = (rf"Two angles lie on a straight line. One angle is {a}°. "
         rf"Find the other angle.")
    s = (rf"Angles on a straight line add up to 180°.<br>"
         rf"\({a}° + x = 180°\)<br>"
         rf"\(x = 180° - {a}°\)<br>"
         rf"<strong>\(x = {b}°\)</strong>")
    hint = "Angles on a straight line sum to 180°."
    return q, s, hint, 1


def _geom_found_around_point():
    a = random.randint(80, 130)
    b = random.randint(60, 100)
    c = 360 - a - b
    while c <= 15:
        a, b = random.randint(80, 120), random.randint(60, 100)
        c = 360 - a - b
    q = (rf"Three angles meet at a point. Two of the angles are {a}° and {b}°. "
         rf"Find the third angle.")
    s = (rf"Angles around a point sum to 360°.<br>"
         rf"\({a}° + {b}° + x = 360°\)<br>"
         rf"\(x = 360° - {a + b}°\)<br>"
         rf"<strong>\(x = {c}°\)</strong>")
    hint = "Angles around a point sum to 360°."
    return q, s, hint, 1


def _geom_found_vertically_opposite():
    a = random.randint(35, 145)
    b = 180 - a
    q = (rf"Two straight lines cross. One of the four angles formed is {a}°.<br>"
         rf"(a) Write down the vertically opposite angle.<br>"
         rf"(b) Find the other two angles and give a reason.")
    s = (rf"(a) Vertically opposite angles are equal.<br>"
         rf"<strong>Vertically opposite angle \(= {a}°\)</strong><br>"
         rf"(b) Angles on a straight line: \({a}° + x = 180°\) → \(x = {b}°\)<br>"
         rf"The other two angles are both <strong>{b}°</strong> (vertically opposite to each other).")
    hint = "Vertically opposite angles are equal; adjacent angles on a straight line sum to 180°."
    return q, s, hint, 2


def _geom_found_triangle_sum():
    a = random.randint(30, 80)
    b = random.randint(30, 80)
    while a + b >= 170:
        b = random.randint(20, 70)
    c = 180 - a - b
    q = rf"In a triangle, two angles are {a}° and {b}°. Find the third angle."
    s = (rf"Angles in a triangle sum to 180°.<br>"
         rf"\({a}° + {b}° + x = 180°\)<br>"
         rf"\(x = 180° - {a + b}°\)<br>"
         rf"<strong>\(x = {c}°\)</strong>")
    hint = "Angles in a triangle sum to 180°."
    return q, s, hint, 1


def _geom_found_isosceles():
    base = random.randint(25, 70)
    apex = 180 - 2 * base
    while apex <= 5:
        base = random.randint(25, 70)
        apex = 180 - 2 * base
    q = (rf"An isosceles triangle has a base angle of {base}°. "
         rf"Find the apex angle.")
    s = (rf"Base angles of an isosceles triangle are equal.<br>"
         rf"Angle sum: \({base}° + {base}° + \text{{apex}} = 180°\)<br>"
         rf"Apex angle \(= 180° - {2 * base}°\)<br>"
         rf"<strong>Apex angle \(= {apex}°\)</strong>")
    hint = "The two base angles are equal in an isosceles triangle."
    return q, s, hint, 2


def _geom_found_exterior_angle():
    a = random.randint(30, 65)
    b = random.randint(30, 65)
    while a + b >= 160:
        b = random.randint(25, 60)
    ext = a + b
    q = (rf"In a triangle, two interior angles are {a}° and {b}°. "
         rf"Find the exterior angle at the third vertex.")
    s = (rf"The exterior angle of a triangle equals the sum of the two non-adjacent interior angles.<br>"
         rf"Exterior angle \(= {a}° + {b}°\)<br>"
         rf"<strong>\(= {ext}°\)</strong>")
    hint = "Exterior angle = sum of the two opposite interior angles."
    return q, s, hint, 2


def _geom_found_quadrilateral():
    a, b, c = 0, 0, 0
    d = -1
    while d <= 20 or d >= 179:
        a = random.randint(70, 110)
        b = random.randint(70, 110)
        c = random.randint(70, 110)
        d = 360 - a - b - c
    q = (rf"A quadrilateral has three angles: {a}°, {b}°, and {c}°. "
         rf"Find the fourth angle.")
    s = (rf"Angles in a quadrilateral sum to 360°.<br>"
         rf"\({a}° + {b}° + {c}° + x = 360°\)<br>"
         rf"\(x = 360° - {a + b + c}°\)<br>"
         rf"<strong>\(x = {d}°\)</strong>")
    hint = "Angles in a quadrilateral sum to 360°."
    return q, s, hint, 1


def _geom_found_corresponding():
    a = random.randint(40, 140)
    q = (rf"Two parallel lines are cut by a transversal. "
         rf"One angle formed at the first line is {a}°. "
         rf"Find the corresponding angle at the second line, giving a reason.")
    s = (rf"Corresponding angles are equal when lines are parallel (F-shape).<br>"
         rf"<strong>Corresponding angle \(= {a}°\)</strong>")
    hint = "Corresponding angles (F-shape) are equal on parallel lines."
    return q, s, hint, 1


def _geom_found_alternate():
    a = random.randint(35, 145)
    q = (rf"Two parallel lines are cut by a transversal. "
         rf"One angle formed is {a}°. "
         rf"Find the alternate interior angle, giving a reason.")
    s = (rf"Alternate interior angles are equal when lines are parallel (Z-shape).<br>"
         rf"<strong>Alternate angle \(= {a}°\)</strong>")
    hint = "Alternate angles (Z-shape) are equal on parallel lines."
    return q, s, hint, 1


def _geom_found_cointerior():
    a = random.randint(40, 140)
    b = 180 - a
    q = (rf"Two parallel lines are cut by a transversal. "
         rf"One co-interior (allied) angle is {a}°. "
         rf"Find the other co-interior angle, giving a reason.")
    s = (rf"Co-interior angles (C-shape) sum to 180° when lines are parallel.<br>"
         rf"\({a}° + x = 180°\)<br>"
         rf"<strong>\(x = {b}°\)</strong>")
    hint = "Co-interior angles (C-shape) sum to 180° on parallel lines."
    return q, s, hint, 1


def _geom_found_polygon_sum():
    n = random.randint(5, 10)
    total = (n - 2) * 180
    q = (rf"Find the sum of the interior angles of a {_polygon_name(n)} "
         rf"({n} sides).")
    s = (rf"Sum of interior angles \(= (n-2) \times 180°\)<br>"
         rf"\(= ({n} - 2) \times 180°\)<br>"
         rf"\(= {n - 2} \times 180°\)<br>"
         rf"<strong>\(= {total}°\)</strong>")
    hint = "Use the formula (n − 2) × 180°."
    return q, s, hint, 2


def _geom_found_regular_exterior():
    n = random.choice([3, 4, 5, 6, 8, 9, 10, 12])
    ext = 360 // n
    q = rf"Find the exterior angle of a regular {_polygon_name(n)}."
    s = (rf"Exterior angle of a regular polygon \(= \dfrac{{360°}}{{n}}\)<br>"
         rf"\(= \dfrac{{360°}}{{{n}}}\)<br>"
         rf"<strong>\(= {ext}°\)</strong>")
    hint = "Exterior angle of a regular n-gon = 360° ÷ n."
    return q, s, hint, 2


def _geom_found_complementary():
    a = random.randint(15, 75)
    b = 90 - a
    q = (rf"Two angles are complementary. One angle is {a}°. "
         rf"Find the other angle.")
    s = (rf"Complementary angles sum to 90°.<br>"
         rf"\({a}° + x = 90°\)<br>"
         rf"<strong>\(x = {b}°\)</strong>")
    hint = "Complementary angles sum to 90°."
    return q, s, hint, 1


def _geom_found_equilateral():
    q = (r"An equilateral triangle has all three sides equal. "
         r"What is each interior angle? Explain why.")
    s = (r"All sides are equal, so all angles are equal.<br>"
         r"Sum of angles in any triangle \(= 180°\).<br>"
         r"Each angle \(= 180° \div 3\)<br>"
         r"<strong>Each angle \(= 60°\)</strong>")
    hint = "All angles are equal in an equilateral triangle, and they must sum to 180°."
    return q, s, hint, 2


def _geom_found_multistep_lines():
    a = random.randint(40, 80)
    b = 180 - a
    q = (rf"Two straight lines intersect. One angle formed is {a}°.<br>"
         rf"Find all four angles at the intersection, giving reasons for each.")
    s = (rf"Label the four angles A, B, C, D going clockwise.<br>"
         rf"A \(= {a}°\) (given).<br>"
         rf"B \(= 180° - {a}° = {b}°\)  (angles on a straight line).<br>"
         rf"C \(= {a}°\)  (vertically opposite to A).<br>"
         rf"D \(= {b}°\)  (vertically opposite to B).<br>"
         rf"<strong>The four angles are {a}°, {b}°, {a}°, {b}°.</strong>")
    hint = "Use: angles on a straight line = 180°, and vertically opposite angles are equal."
    return q, s, hint, 3


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
    q = (rf"Two angles on a straight line are \(({a}x + {b})°\) and \(({c}x + {d})°\).<br>"
         rf"Find the value of \(x\) and the size of each angle.")
    s = (rf"Angles on a straight line sum to 180°:<br>"
         rf"\(({a}x + {b}) + ({c}x + {d}) = 180\)<br>"
         rf"\({a + c}x + {b + d} = 180\)<br>"
         rf"\({a + c}x = {180 - b - d}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angles: \({a}({x_val})+{b} = {ang1}°\) and \({c}({x_val})+{d} = {ang2}°\)<br>"
         rf"<strong>\(x = {x_val}\); angles are {ang1}° and {ang2}°</strong>")
    hint = f"Set the two expressions equal to 180 and solve for x."
    return q, s, hint, 3


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
    q = (rf"The angles of a triangle are \(({a}x + {b})°\), \(({c}x + {d})°\), and \(({e}x + {f})°\).<br>"
         rf"Find \(x\) and the size of each angle.")
    s = (rf"Angles in a triangle sum to 180°:<br>"
         rf"\({a + c + e}x + {b + d + f} = 180\)<br>"
         rf"\({a + c + e}x = {180 - b - d - f}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angles: \({ang1}°\), \({ang2}°\), \({ang3}°\)<br>"
         rf"<strong>\(x = {x_val}\); angles are {ang1}°, {ang2}°, {ang3}°</strong>")
    hint = "Set the sum of the three expressions equal to 180."
    return q, s, hint, 3


def _geom_inter_regular_polygon_n():
    # Given interior angle, find n
    # Interior angle of regular n-gon = (n-2)*180/n
    # Choose n from sensible values
    n = random.choice([5, 6, 8, 9, 10, 12])
    interior = (n - 2) * 180 // n
    q = (rf"A regular polygon has an interior angle of {interior}°. "
         rf"Find the number of sides.")
    s = (rf"Exterior angle \(= 180° - {interior}° = {180 - interior}°\)<br>"
         rf"Number of sides \(= \dfrac{{360°}}{{{180 - interior}°}} = {n}\)<br>"
         rf"<strong>\(n = {n}\) sides</strong>")
    hint = "Find the exterior angle first (= 180° − interior angle), then n = 360° ÷ exterior angle."
    return q, s, hint, 3


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
    q = (rf"Line \(l_1\) is parallel to line \(l_2\). Point A lies on \(l_1\) and points B and C lie on \(l_2\).<br>"
         rf"The angle between \(l_1\) and AB (measured below \(l_1\)) is {p}° and angle ACB = {q_ang}°.<br>"
         rf"Find angle BAC.")
    s = (rf"Angle ABC \(= {p}°\) (alternate angles, \(l_1 \parallel l_2\), AB is transversal).<br>"
         rf"In triangle ABC: angle BAC \(= 180° - {p}° - {q_ang}°\)<br>"
         rf"<strong>Angle BAC \(= {ang_bac}°\)</strong>")
    hint = "Use alternate angles to find angle ABC first, then use the triangle angle sum."
    return q, s, hint, 3


def _geom_inter_angle_at_centre():
    circ = random.randint(20, 60)
    centre = 2 * circ
    q = (rf"O is the centre of a circle. Points A, B, and C lie on the circle.<br>"
         rf"Angle ACB = {circ}°. Find angle AOB, giving a reason.")
    s = (rf"The angle at the centre is twice the angle at the circumference when both are subtended by the same arc.<br>"
         rf"Angle AOB \(= 2 \times {circ}°\)<br>"
         rf"<strong>Angle AOB \(= {centre}°\)</strong>")
    hint = "Angle at centre = 2 × angle at circumference (same arc)."
    return q, s, hint, 2


def _geom_inter_angle_semicircle():
    b_ang = random.randint(25, 60)
    a_ang = 90 - b_ang
    q = (rf"AB is a diameter of a circle. C is a point on the circle.<br>"
         rf"Angle ABC = {b_ang}°. Find angle BAC and angle ACB, giving reasons.")
    s = (rf"Angle ACB \(= 90°\) (angle in a semicircle — angle subtended by a diameter).<br>"
         rf"In triangle ACB: angle BAC \(= 180° - 90° - {b_ang}°\)<br>"
         rf"<strong>Angle BAC \(= {a_ang}°\);  angle ACB \(= 90°\)</strong>")
    hint = "The angle subtended by a diameter at the circumference is always 90°."
    return q, s, hint, 3


def _geom_inter_same_segment():
    ang = random.randint(25, 65)
    q = (rf"Points P, Q, R, and S lie on a circle. "
         rf"Angle PRQ = {ang}°. "
         rf"Find angle PSQ, giving a reason.")
    s = (rf"Angles in the same segment are equal — both PRQ and PSQ are subtended by arc PQ from the same side.<br>"
         rf"<strong>Angle PSQ \(= {ang}°\)</strong>")
    hint = "Angles in the same segment (subtended by the same chord from the same side) are equal."
    return q, s, hint, 2


def _geom_inter_cyclic_quad():
    a = random.randint(60, 110)
    b = random.randint(60, 110)
    c = 180 - a
    d = 180 - b
    q = (rf"ABCD is a cyclic quadrilateral (all four vertices lie on a circle).<br>"
         rf"Angle DAB = {a}° and angle ABC = {b}°. Find angles BCD and CDA, giving reasons.")
    s = (rf"Opposite angles in a cyclic quadrilateral sum to 180°.<br>"
         rf"Angle BCD \(= 180° - {a}° = {c}°\)<br>"
         rf"Angle CDA \(= 180° - {b}° = {d}°\)<br>"
         rf"<strong>Angle BCD \(= {c}°\);  angle CDA \(= {d}°\)</strong>")
    hint = "Opposite angles in a cyclic quadrilateral add up to 180°."
    return q, s, hint, 3


def _geom_inter_tangent_radius():
    # Pythagorean triple: radius r, distance OT, tangent length AT
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10)]
    r, t_len, ot = random.choice(triples)
    q = (rf"A tangent from external point T touches a circle at A. "
         rf"The radius OA = {r} cm and the distance OT = {ot} cm.<br>"
         rf"Find the length AT. (Tangent is perpendicular to radius at point of contact.)")
    s = (rf"Since OA is a radius and AT is a tangent at A, angle OAT = 90°.<br>"
         rf"By Pythagoras in triangle OAT:<br>"
         rf"\(AT^2 = OT^2 - OA^2 = {ot}^2 - {r}^2 = {ot**2} - {r**2} = {ot**2 - r**2}\)<br>"
         rf"\(AT = \sqrt{{{ot**2 - r**2}}}\)<br>"
         rf"<strong>AT \(= {t_len}\) cm</strong>")
    hint = "The tangent is perpendicular to the radius at the point of contact. Use Pythagoras."
    return q, s, hint, 3


def _geom_inter_bearing():
    b1 = random.choice([40, 50, 55, 60, 65, 70])
    back = b1 + 180
    q = (rf"The bearing of town Q from town P is {b1:03d}°. "
         rf"Find the bearing of town P from town Q.")
    s = (rf"To find the reverse bearing, add 180° (since the bearing is less than 180°).<br>"
         rf"Bearing of P from Q \(= {b1}° + 180°\)<br>"
         rf"<strong>\(= {back:03d}°\)</strong>")
    hint = "Add 180° to the forward bearing to get the back-bearing (if the result ≤ 360°)."
    return q, s, hint, 2


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
    q = (rf"Triangle ABC is similar to triangle PQR (same shape, different size).<br>"
         rf"AB = {ab} cm, BC = {bc} cm, PQ = {pq} cm, and angle ABC = {ang_b}°.<br>"
         rf"(a) Find QR.  (b) Find angle PQR.")
    s = (rf"(a) Scale factor \(= \dfrac{{PQ}}{{AB}} = \dfrac{{{pq}}}{{{ab}}} = \dfrac{{{scale_den}}}{{{scale_num}}}\)<br>"
         rf"\(QR = BC \times \dfrac{{{scale_den}}}{{{scale_num}}} = {bc} \times \dfrac{{{scale_den}}}{{{scale_num}}} = {qr}\) cm<br>"
         rf"<strong>QR \(= {qr}\) cm</strong><br>"
         rf"(b) Corresponding angles in similar triangles are equal.<br>"
         rf"<strong>Angle PQR \(= {ang_b}°\)</strong>")
    hint = "Find the scale factor = PQ ÷ AB, then multiply BC. Corresponding angles are equal."
    return q, s, hint, 4


def _geom_inter_polygon_algebra():
    # Interior + exterior = 180; interior = k × exterior → k*ext + ext = 180 → ext = 180/(k+1)
    k = random.choice([2, 3, 4, 5])
    ext = 180 // (k + 1)
    interior = 180 - ext
    n = 360 // ext
    q = (rf"A regular polygon has an interior angle that is {k} times its exterior angle. "
         rf"Find the number of sides of the polygon.")
    s = (rf"Let exterior angle \(= x°\). Interior angle \(= {k}x°\).<br>"
         rf"Interior + exterior \(= 180°\): \({k}x + x = 180° \Rightarrow {k + 1}x = 180°\)<br>"
         rf"\(x = {ext}°\)  (exterior angle)<br>"
         rf"Number of sides \(= \dfrac{{360°}}{{{ext}°}} = {n}\)<br>"
         rf"<strong>\(n = {n}\) sides</strong>")
    hint = "Interior + exterior = 180°. Set up an equation with the given ratio."
    return q, s, hint, 4


def _geom_inter_isosceles_parallel():
    base_ang = random.randint(30, 65)
    apex = 180 - 2 * base_ang
    corr = base_ang   # corresponding or alternate angle on parallel line
    q = (rf"Triangle ABC is isosceles with AB = AC. A line DE is parallel to BC, "
         rf"with D on AB and E on AC.<br>"
         rf"Angle ABC = {base_ang}°.<br>"
         rf"(a) Find angle BAC.  (b) Find angle ADE, giving a reason.")
    s = (rf"(a) Since AB = AC, base angles are equal: angle ABC = angle ACB = {base_ang}°.<br>"
         rf"Angle BAC \(= 180° - {base_ang}° - {base_ang}° = {apex}°\)<br>"
         rf"<strong>Angle BAC \(= {apex}°\)</strong><br>"
         rf"(b) Since DE ∥ BC, angle ADE = angle ABC = {base_ang}° (corresponding angles).<br>"
         rf"<strong>Angle ADE \(= {base_ang}°\)</strong>")
    hint = "Find angle BAC using isosceles triangle, then use corresponding/alternate angles for DE ∥ BC."
    return q, s, hint, 4


def _geom_inter_interior_exterior():
    n = random.choice([5, 6, 8, 10, 12])
    interior = (n - 2) * 180 // n
    exterior = 360 // n
    q = (rf"A regular {_polygon_name(n)} has {n} sides.<br>"
         rf"(a) Calculate the interior angle.<br>"
         rf"(b) Calculate the exterior angle.<br>"
         rf"(c) Verify that interior angle + exterior angle = 180°.")
    s = (rf"(a) Interior angle \(= \dfrac{{(n-2) \times 180°}}{{n}} = \dfrac{{{(n-2)*180}°}}{{{n}}} = {interior}°\)<br>"
         rf"<strong>Interior angle \(= {interior}°\)</strong><br>"
         rf"(b) Exterior angle \(= \dfrac{{360°}}{{{n}}} = {exterior}°\)<br>"
         rf"<strong>Exterior angle \(= {exterior}°\)</strong><br>"
         rf"(c) \({interior}° + {exterior}° = {interior + exterior}° = 180°\) ✓")
    hint = "Interior angle = (n−2)×180°/n; exterior angle = 360°/n. They must sum to 180°."
    return q, s, hint, 3


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
    q = (rf"In kite ABCD, AB = AD and CB = CD. "
         rf"Angle A = {ang_a}° and angle B = {ang_b}°.<br>"
         rf"Find angles C and D, giving reasons.")
    s = (rf"In a kite, the two angles between unequal sides are equal: angle B = angle D.<br>"
         rf"Angle D \(= {ang_d}°\)<br>"
         rf"Angle sum: angle A + angle B + angle C + angle D = 360°<br>"
         rf"\({ang_a}° + {ang_b}° + \text{{angle C}} + {ang_d}° = 360°\)<br>"
         rf"Angle C \(= 360° - {ang_a + ang_b + ang_d}° = {ang_c}°\)<br>"
         rf"<strong>Angle C \(= {ang_c}°\);  angle D \(= {ang_d}°\)</strong>")
    hint = "In a kite, the two angles between the unequal sides are equal."
    return q, s, hint, 3


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _geom_diff_alternate_segment():
    alpha = random.randint(30, 65)
    centre = 2 * alpha
    q = (rf"A tangent to a circle at point T makes an angle of {alpha}° with chord TA.<br>"
         rf"Point B lies on the major arc TA. O is the centre of the circle.<br>"
         rf"(a) Find angle TBA (alternate segment theorem).<br>"
         rf"(b) Hence find angle TOA.")
    s = (rf"(a) By the alternate segment theorem, the angle between a tangent and a chord equals "
         rf"the inscribed angle in the alternate segment.<br>"
         rf"<strong>Angle TBA \(= {alpha}°\)</strong><br>"
         rf"(b) Angle at centre = 2 × angle at circumference (same arc TA):<br>"
         rf"Angle TOA \(= 2 \times {alpha}°\)<br>"
         rf"<strong>Angle TOA \(= {centre}°\)</strong>")
    hint = "Use the alternate segment theorem, then angle at centre = 2 × angle at circumference."
    return q, s, hint, 5


def _geom_diff_two_tangents():
    angle_p = random.randint(25, 65)
    angle_aob = 180 - angle_p
    q = (rf"From external point P, two tangents PA and PB touch a circle (centre O) at A and B respectively.<br>"
         rf"Angle APB = {angle_p}°. Find angle AOB, showing your working clearly.")
    s = (rf"OA is perpendicular to PA (tangent ⊥ radius): angle OAP = 90°.<br>"
         rf"OB is perpendicular to PB (tangent ⊥ radius): angle OBP = 90°.<br>"
         rf"Quadrilateral OAPB: angle sum = 360°.<br>"
         rf"\({angle_p}° + 90° + \text{{angle AOB}} + 90° = 360°\)<br>"
         rf"Angle AOB \(= 360° - {angle_p + 180}° = {360 - angle_p - 180}°\)<br>"
         rf"<strong>Angle AOB \(= {angle_aob}°\)</strong>")
    hint = "Each tangent is perpendicular to the radius at the point of contact. Use quadrilateral angle sum."
    return q, s, hint, 4


def _geom_diff_multi_circle():
    # A, B, C, D on circle. Angle AOC (at centre) given. Find circumference angle + reflex.
    centre_ang = random.choice([80, 100, 110, 120, 130, 140])
    circ_major = centre_ang // 2
    reflex = 360 - centre_ang
    circ_minor = reflex // 2
    q = (rf"O is the centre of a circle. A and C are points on the circle. "
         rf"Angle AOC = {centre_ang}° (the non-reflex angle).<br>"
         rf"Point D lies on the major arc AC. Point B lies on the minor arc AC.<br>"
         rf"Find: (a) angle ADC  (b) angle ABC")
    s = (rf"(a) Angle at circumference = ½ angle at centre (same arc AC, major arc side).<br>"
         rf"Angle ADC \(= \dfrac{{{centre_ang}°}}{{2}}\)<br>"
         rf"<strong>Angle ADC \(= {circ_major}°\)</strong><br>"
         rf"(b) B is on the minor arc, so use the reflex angle at O.<br>"
         rf"Reflex angle AOC \(= 360° - {centre_ang}° = {reflex}°\)<br>"
         rf"Angle ABC \(= \dfrac{{{reflex}°}}{{2}}\)<br>"
         rf"<strong>Angle ABC \(= {circ_minor}°\)</strong><br>"
         rf"Check: {circ_major}° + {circ_minor}° = {circ_major + circ_minor}° (opposite angles in cyclic quad → should sum to 180° ✓)")
    hint = "For the major-arc angle use the direct centre angle; for the minor-arc angle use the reflex centre angle."
    return q, s, hint, 5


def _geom_diff_similar_area():
    # Two similar shapes, sides in ratio p:q, find area ratio
    p = random.randint(2, 4)
    q_rat = p + random.randint(1, 3)
    area_small = p * p * random.randint(3, 8)
    area_large = area_small * q_rat * q_rat // (p * p)
    q_str = (rf"Two similar triangles have corresponding sides in the ratio \({p}:{q_rat}\)<br>"
             rf"The area of the smaller triangle is {area_small} cm².<br>"
             rf"Find the area of the larger triangle.")
    s = (rf"For similar shapes, area ratio \(= (\text{{length ratio}})^2\).<br>"
         rf"Area ratio \(= \left(\dfrac{{{q_rat}}}{{{p}}}\right)^2 = \dfrac{{{q_rat**2}}}{{{p**2}}}\)<br>"
         rf"Area of larger triangle \(= {area_small} \times \dfrac{{{q_rat**2}}}{{{p**2}}} = \dfrac{{{area_small * q_rat**2}}}{{{p**2}}}\)<br>"
         rf"<strong>\(= {area_small * q_rat**2 // p**2}\) cm²</strong>")
    hint = "Area ratio = (length ratio)². Square the ratio of corresponding sides."
    return q_str, s, hint, 4


def _geom_diff_prove_triangle_sum():
    q = (r"Prove that the angles in a triangle sum to 180°. "
         r"You may use the fact that alternate angles on parallel lines are equal.")
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
    q = (rf"O is the centre of a circle. A, B, C are points on the circle.<br>"
         rf"Angle AOB \(= ({a_coef}x + {b_off})°\) and angle ACB \(= ({c_coef}x + {d_off})°\)<br>"
         rf"Find x and the size of each angle.")
    s = (rf"Angle at centre = 2 × angle at circumference (same arc AB):<br>"
         rf"\({a_coef}x + {b_off} = 2({c_coef}x + {d_off})\)<br>"
         rf"\({a_coef}x + {b_off} = {2*c_coef}x + {2*d_off}\)<br>"
         rf"\({diff}x = {rhs}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angle AOB \(= {centre_ang}°\),  angle ACB \(= {circ_ang}°\)<br>"
         rf"<strong>\(x = {x_val}\);  angle AOB \(= {centre_ang}°\),  angle ACB \(= {circ_ang}°\)</strong>")
    hint = "Use: angle at centre = 2 × angle at circumference, then solve for x."
    return q, s, hint, 5


def _geom_diff_chord_distance():
    # Chord at distance d from centre, half-chord h, radius r = sqrt(d²+h²)
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)]
    d, h, r = random.choice(triples)
    chord = 2 * h
    q = (rf"A chord of a circle has length {chord} cm. "
         rf"The perpendicular distance from the centre O to the chord is {d} cm.<br>"
         rf"Find the radius of the circle.")
    s = (rf"The perpendicular from the centre bisects the chord.<br>"
         rf"Half-chord \(= {chord} \div 2 = {h}\) cm.<br>"
         rf"In the right-angled triangle formed:<br>"
         rf"\(r^2 = {d}^2 + {h}^2 = {d**2} + {h**2} = {d**2 + h**2}\)<br>"
         rf"\(r = \sqrt{{{d**2 + h**2}}}\)<br>"
         rf"<strong>Radius \(= {r}\) cm</strong>")
    hint = "The perpendicular from the centre bisects the chord. Use Pythagoras with half the chord length."
    return q, s, hint, 4


def _geom_diff_cyclic_quad_proof():
    q = (r"ABCD is a cyclic quadrilateral. Prove that angle DAB + angle BCD = 180°.")
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
    q = (rf"(a) Show that the interior angle of a regular {_polygon_name(n)} is {interior}°.<br>"
         rf"(b) Prove that the exterior angles of any convex polygon sum to 360°.")
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
    q = (rf"A pentagon has angles \({angles_list}, \text{{and }} {fixed}^\circ\)<br>"
         rf"Find x and all five angles.")
    s = (rf"Sum of interior angles of a pentagon \(= (5-2) \times 180° = 540°\).<br>"
         rf"\((x+{a}) + (x+{b}) + (x+{c}) + (x+{d}) + {fixed} = 540\)<br>"
         rf"\(4x + {a+b+c+d+fixed} = 540\)<br>"
         rf"\(4x = {540-a-b-c-d-fixed}\)<br>"
         rf"\(x = {x_val}\)<br>"
         rf"Angles: \({ang1}^\circ, {ang2}^\circ, {ang3}^\circ, {ang4}^\circ, {fixed}^\circ\)<br>"
         rf"<strong>\(x = {x_val}\); angles are {ang1}°, {ang2}°, {ang3}°, {ang4}°, {fixed}°</strong>")
    hint = "Sum of pentagon angles = 540°. Collect the x terms and constants, then solve."
    return q, s, hint, 4


def _geom_diff_reflex_centre():
    arc_ang = random.choice([40, 50, 55, 60, 65, 70, 80])
    reflex = 360 - 2 * arc_ang
    q = (rf"O is the centre of a circle. A and B are points on the circle. "
         rf"A point P on the major arc subtends angle APB = {arc_ang}°.<br>"
         rf"Find the reflex angle AOB.")
    s = (rf"Non-reflex angle AOB \(= 2 \times \angle APB = 2 \times {arc_ang}° = {2*arc_ang}°\) "
         rf"(angle at centre = 2 × angle at circumference).<br>"
         rf"Reflex angle AOB \(= 360° - {2*arc_ang}°\)<br>"
         rf"<strong>Reflex angle AOB \(= {reflex}°\)</strong>")
    hint = "Find the non-reflex angle at centre first (= 2 × angle at circumference), then subtract from 360°."
    return q, s, hint, 3


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
    q = (rf"A tangent at point T and a chord TP are drawn. "
         rf"The angle between the tangent and chord TP is {alpha}°.<br>"
         rf"Point B lies on the major arc TP, and angle TPB = {beta}°.<br>"
         rf"Find: (a) angle TBP  (b) angle BTP")
    s = (rf"(a) Alternate segment theorem: angle between tangent and chord = angle in alternate segment.<br>"
         rf"<strong>Angle TBP \(= {alpha}°\)</strong><br>"
         rf"(b) In triangle TBP: angles sum to 180°.<br>"
         rf"Angle BTP \(= 180° - {alpha}° - {beta}°\)<br>"
         rf"<strong>Angle BTP \(= {180 - alpha - beta}°\)</strong>")
    hint = "Apply the alternate segment theorem to find angle TBP, then use triangle angle sum."
    return q, s, hint, 5


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
    q_str = (rf"A ship leaves port A on a bearing of {b1:03d}°. "
             rf"It sails to point B, then turns clockwise by {turn}° and sails to C.<br>"
             rf"(a) Find the bearing from B to C.<br>"
             rf"(b) Find the interior angle ABC of the triangle formed.")
    s = (rf"(a) The ship was heading on bearing {b1:03d}°; it turns clockwise by {turn}°.<br>"
         rf"New bearing \(= {b1}° + {turn}° = {b2_result}°\)<br>"
         rf"<strong>Bearing from B to C \(= {b2_result:03d}°\)</strong><br>"
         rf"(b) The exterior angle at B (turn) \(= {turn}°\).<br>"
         rf"Interior angle ABC \(= 180° - {turn}°\)<br>"
         rf"<strong>Angle ABC \(= {angle_abc}°\)</strong>")
    hint = "The clockwise turn gives the change in bearing. Interior angle = 180° − exterior turn angle."
    return q_str, s, hint, 4


def _geom_diff_inscribed_angles():
    # Multiple inscribed angle relationships in one diagram
    ang1 = random.randint(25, 50)
    ang2 = random.randint(25, 50)
    # ABCD cyclic quad. Given two angles, find others using all circle theorems
    opp_ang1 = 180 - ang1
    opp_ang2 = 180 - ang2
    centre_ang = 2 * ang1
    q = (rf"A, B, C, D are four points on a circle with centre O.<br>"
         rf"Angle DAB = {ang1}° and angle ABC = {ang2}°.<br>"
         rf"Find: (a) angle BCD  (b) angle CDA  (c) angle BOD")
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
    return q, s, hint, 5


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

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        'gcse', 'maths', 'geometry_angles',
    )
