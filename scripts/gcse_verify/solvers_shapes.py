"""Solvers for angles, polygons, circle theorems, similarity and congruence, and constructions and loci.

Independence rule: this module recomputes answers from first principles.  It must not import any generator
module or helper (checked by the test); only the standard library, sympy and the sibling verification modules.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from .core import Approx, Cannot, Pick, Ratio, norm_text, sqrt_atom
from .latex import plain
from .registry import diagram, fr, solver
from .solvers_svg import one_svg, read_centre_angle

# ─────────────────────────────────────────────────────────────────────────────
# Facts the solvers rely on (written out here, not taken from the generators)
# ─────────────────────────────────────────────────────────────────────────────

ANGLE_TOTALS = {            # what the angles of each figure add up to
    'straight line': 180, 'point': 360, 'triangle': 180, 'quadrilateral': 360, 'complementary': 90,
    'co-interior': 180, 'supplementary': 180, 'right angle': 90,
}

POLYGON_SIDES = {
    'triangle': 3, 'quadrilateral': 4, 'pentagon': 5, 'hexagon': 6, 'heptagon': 7, 'octagon': 8,
    'nonagon': 9, 'decagon': 10, 'dodecagon': 12,
}


def sides_of(name):
    key = str(name).strip().lower()
    if key not in POLYGON_SIDES:
        raise Cannot(f'unknown polygon {name!r}')
    return POLYGON_SIDES[key]


def _real(angle, lo=0, hi=360):
    if not lo < angle < hi:
        raise Cannot(f'an angle of {angle} degrees is not possible here')
    return angle


# ─────────────────────────────────────────────────────────────────────────────
# Angles on lines, in triangles and quadrilaterals
# ─────────────────────────────────────────────────────────────────────────────

@solver('ang_rule')
def _ang_rule(given, rule_word=None, rule=None):
    name = rule_word or rule
    if name not in ANGLE_TOTALS:
        raise Cannot(f'unknown angle rule {name!r}')
    return [_real(ANGLE_TOTALS[name] - sum(fr(g) for g in given))]


@solver('ang_vertical')
def _ang_vertical(angle):
    return [fr(angle), _real(180 - fr(angle), 0, 180)]


@solver('ang_cross')
def _ang_cross(angle):
    a = fr(angle)
    return [a, _real(180 - a, 0, 180), a, 180 - a]


@solver('ang_isos_apex')
def _ang_isos_apex(base):
    return [_real(180 - 2 * fr(base), 0, 180)]


@solver('ang_exterior')
def _ang_exterior(a, b):
    return [_real(fr(a) + fr(b), 0, 180)]


@solver('ang_parallel')
def _ang_parallel(kind_word, angle):
    a = fr(angle)
    if kind_word in ('corresponding', 'alternate'):
        return [a]
    if kind_word == 'co-interior':
        return [_real(180 - a, 0, 180)]
    raise Cannot(f'unknown parallel-line angle {kind_word!r}')


@solver('ang_equilateral')
def _ang_equilateral(shape_word):
    return [Fraction(180, 3)]


@solver('ang_kite')
def _ang_kite(a, b):
    # a kite has one pair of equal angles (between the unequal sides): D equals B
    return [_real(360 - fr(a) - 2 * fr(b), 0, 180), fr(b)]


@solver('ang_isos_parallel')
def _ang_isos_parallel(base):
    return [_real(180 - 2 * fr(base), 0, 180), fr(base)]


@solver('ang_alg')
def _ang_alg(terms, rule_word):
    """Angles (a x + b) in a figure whose angles add to a known total: [x, angle 1, angle 2, ...]."""
    if rule_word not in ANGLE_TOTALS or len(terms) % 2:
        raise Cannot('cannot read the algebraic angles')
    pairs = [(fr(terms[i]), fr(terms[i + 1])) for i in range(0, len(terms), 2)]
    coef = sum(a for a, _ in pairs)
    x = (ANGLE_TOTALS[rule_word] - sum(b for _, b in pairs)) / coef
    angles = [a * x + b for a, b in pairs]
    if x <= 0 or min(angles) <= 0:
        raise Cannot('the algebra gives an impossible angle')
    return [x] + angles


@solver('ang_bearing_turn')
def _ang_bearing_turn(b1, turn):
    return [fr(b1) + fr(turn), _real(180 - fr(turn), 0, 180)]


# ─────────────────────────────────────────────────────────────────────────────
# Polygons
# ─────────────────────────────────────────────────────────────────────────────

@solver('poly_sum')
def _poly_sum(n):
    if int(n) < 3:
        raise Cannot('a polygon needs at least three sides')
    return [(fr(n) - 2) * 180]


@solver('poly_exterior')
def _poly_exterior(shape_word):
    return [Fraction(360, sides_of(shape_word))]


@solver('poly_n_from_interior')
def _poly_n_from_interior(interior):
    ext = 180 - fr(interior)
    if ext <= 0:
        raise Cannot('interior angle must be under 180')
    n = 360 / ext
    if n.denominator != 1:
        raise Cannot('no regular polygon has that interior angle')
    return [n]


@solver('poly_interior_ratio')
def _poly_interior_ratio(k):
    ext = Fraction(180) / (fr(k) + 1)         # interior = k * exterior and interior + exterior = 180
    n = 360 / ext
    if n.denominator != 1:
        raise Cannot('no regular polygon fits')
    return [n]


@solver('poly_int_ext')
def _poly_int_ext(n):
    n = fr(n)
    return [(n - 2) * 180 / n, 360 / n]


@solver('poly_proof')
def _poly_proof(shape_word, interior):
    n = fr(sides_of(shape_word))
    return [n - 2, (n - 2) * 180 / n, Fraction(360)]


@solver('poly_alg')
def _poly_alg(offsets, fixed, sides):
    total = (fr(sides) - 2) * 180
    k = len(offsets)
    x = (total - sum(fr(o) for o in offsets) - fr(fixed)) / k
    return [x] + [x + fr(o) for o in offsets] + [fr(fixed)]


# ─────────────────────────────────────────────────────────────────────────────
# Circle theorems
# ─────────────────────────────────────────────────────────────────────────────

@solver('circ_centre')
def _circ_centre(angle):
    return [_real(2 * fr(angle), 0, 360)]


@solver('circ_semicircle')
def _circ_semicircle(angle):
    return [_real(90 - fr(angle), 0, 90), Fraction(90)]


@solver('circ_same_segment')
def _circ_same_segment(angle):
    return [fr(angle)]


@solver('circ_cyclic2')
def _circ_cyclic2(a, b):
    return [_real(180 - fr(a), 0, 180), _real(180 - fr(b), 0, 180)]


@solver('circ_tangent_length')
def _circ_tangent_length(r, ot):
    if fr(ot) <= fr(r):
        raise Cannot('the external point must be outside the circle')
    return [sqrt_atom(fr(ot) ** 2 - fr(r) ** 2)]


@solver('circ_alt_segment')
def _circ_alt_segment(alpha):
    return [fr(alpha), _real(2 * fr(alpha), 0, 180)]


@solver('circ_two_tangents')
def _circ_two_tangents(p):
    return [_real(180 - fr(p), 0, 180)]


@solver('circ_arcs')
def _circ_arcs(centre):
    c = fr(centre)
    return [c / 2, (360 - c) / 2]


@solver('circ_alg')
def _circ_alg(a, b, c, d):
    diff = fr(a) - 2 * fr(c)
    if diff == 0:
        raise Cannot('the equation has no single solution')
    x = (2 * fr(d) - fr(b)) / diff
    centre, circ = fr(a) * x + fr(b), fr(c) * x + fr(d)
    if x <= 0 or not 0 < circ < 90 or centre != 2 * circ:
        raise Cannot(f'x = {x} gives angles {centre} and {circ}')
    return [x, centre, circ]


@solver('circ_chord_radius')
def _circ_chord_radius(chord, d):
    return [sqrt_atom((fr(chord) / 2) ** 2 + fr(d) ** 2)]


@solver('circ_reflex')
def _circ_reflex(arc):
    return [_real(360 - 2 * fr(arc), 180, 360)]


@solver('circ_tangent_chord')
def _circ_tangent_chord(alpha, beta):
    return [fr(alpha), _real(180 - fr(alpha) - fr(beta), 0, 180)]


@solver('circ_cyclic3')
def _circ_cyclic3(a1, a2):
    if not fr(a1) < 90:
        raise Cannot('the angle at A is not on the major arc')
    return [_real(180 - fr(a1), 0, 180), _real(180 - fr(a2), 0, 180), 2 * fr(a1)]


# ─────────────────────────────────────────────────────────────────────────────
# Similar shapes
# ─────────────────────────────────────────────────────────────────────────────

@solver('sim_fields')
def _sim_fields(ab, bc, pq, ang_b):
    # triangle PQR is an enlargement of ABC with PQ matching AB and QR matching BC
    return [fr(bc) * fr(pq) / fr(ab), fr(ang_b)]


@solver('sim_area_scale')
def _sim_area_scale(p, q, area):
    return [fr(area) * (fr(q) / fr(p)) ** 2]


# ─────────────────────────────────────────────────────────────────────────────
# Proof scaffolds whose boxes hold fixed facts
# ─────────────────────────────────────────────────────────────────────────────

@solver('proof_triangle_sum')
def _proof_triangle_sum():
    # straight line = 180; the three angles at C fill the straight line = 180; the triangle sum = 180
    return [Fraction(180), Fraction(180), Fraction(180)]


@solver('proof_cyclic_quad')
def _proof_cyclic_quad():
    def is_180_minus_alpha(text):
        flat = re.sub(r'\s+', '', norm_text(text)).replace('−', '-')
        return flat in ('180-a', '-a+180', '180-α', '-α+180', '180°-a', '(180-a)')
    return [Fraction(2), Pick(is_180_minus_alpha, 'the expression 180 - a'), Fraction(180)]


@solver('poly_exterior_n')
def _poly_exterior_n(n):
    return [Fraction(360) / fr(n)]


# ─────────────────────────────────────────────────────────────────────────────
# Similar shapes in the multiple-choice functions
# ─────────────────────────────────────────────────────────────────────────────

@solver('sim_scale_length')
def _sim_scale_length(k, length):
    return [fr(k) * fr(length)]


@solver('sim_area_k')
def _sim_area_k(k, area):
    return [fr(area) * fr(k) ** 2]


# ─────────────────────────────────────────────────────────────────────────────
# Facts stated in words (multiple choice)
# ─────────────────────────────────────────────────────────────────────────────

def _says(*needles):
    wanted = [n.lower() for n in needles]

    def test(text):
        flat = norm_text(text)
        return all(n in flat for n in wanted)
    return test


@solver('fact_pick')
def _fact_pick(fact_word):
    """The one true statement for a locus or theorem question; the others must not contain it."""
    if fact_word in ('semicircle', 'tangent'):
        return [Pick(lambda t: re.sub(r'\s+', '', norm_text(t)) == '90°', 'a right angle, 90 degrees')]
    if fact_word == 'perpendicular bisector':
        return [Pick(_says('equidistant', 'a and b'), 'points equidistant from A and B')]
    if fact_word == 'angle bisector':
        return [Pick(_says('equidistant', 'two lines'), 'points equidistant from the two lines')]
    raise Cannot(f'unknown fact {fact_word!r}')


# ─────────────────────────────────────────────────────────────────────────────
# Similar shapes in the practice variants
# ─────────────────────────────────────────────────────────────────────────────

def _exact_root(x, n):
    """The n-th root of a positive rational when it is rational, else Cannot."""
    x = fr(x)
    if x <= 0:
        raise Cannot('need a positive number')
    num, den = round(x.numerator ** (1 / n)), round(x.denominator ** (1 / n))
    if num ** n != x.numerator or den ** n != x.denominator:
        raise Cannot(f'the {n}-th root of {x} is not rational')
    return Fraction(num, den)


def _ratio(x):
    return Ratio(x.numerator, x.denominator)


@solver('sim_sf')
def _sim_sf(small, large):
    return [fr(large) / fr(small)]


@solver('sim_tri_angles')
def _sim_tri_angles(a, b):
    c = 180 - fr(a) - fr(b)
    return [_real(c, 0, 180), fr(a), fr(b), c]


@solver('sim_vol_k')
def _sim_vol_k(k, vol):
    return [fr(vol) * fr(k) ** 3]


@solver('sim_lsf_from_area')
def _sim_lsf_from_area(a_small, a_large):
    return [_ratio(_exact_root(fr(a_small) / fr(a_large), 2))]


@solver('sim_lsf_two')
def _sim_lsf_two(a_small, a_large):
    r = _ratio(_exact_root(fr(a_small) / fr(a_large), 2))
    return [r, r]


@solver('sim_sides')
def _sim_sides(known_new, known_old, others):
    k = fr(known_new) / fr(known_old)
    return [k * fr(o) for o in others]


@solver('sim_map_length')
def _sim_map_length(scale, map_cm, unit_word):
    cm = fr(scale) * fr(map_cm)
    per = {'km': 100000, 'm': 100, 'cm': 1}
    if unit_word not in per:
        raise Cannot(f'unknown unit {unit_word!r}')
    return [cm / per[unit_word]]


@solver('sim_area_down')
def _sim_area_down(k, area):
    return [fr(area) / fr(k) ** 2]


@solver('sim_area_ratio')
def _sim_area_ratio(r_from, r_to, area):
    return [fr(area) * (fr(r_to) / fr(r_from)) ** 2]


@solver('sim_parallel')
def _sim_parallel(ad, db, de):
    return [fr(de) * (fr(ad) + fr(db)) / fr(ad)]


@solver('sim_dim_from_vol')
def _sim_dim_from_vol(v_small, v_large, dim_small):
    return [fr(dim_small) * _exact_root(fr(v_large) / fr(v_small), 3)]


@solver('sim_alg_prop')
def _sim_alg_prop(a1, b1, a2, b2, top, bottom):
    """(a1 x + b1) / (a2 x + b2) = top / bottom."""
    denom = fr(bottom) * fr(a1) - fr(top) * fr(a2)
    if denom == 0:
        raise Cannot('the equation has no single solution')
    x = (fr(top) * fr(b2) - fr(bottom) * fr(b1)) / denom
    if x <= 0 or fr(a1) * x + fr(b1) <= 0 or fr(a2) * x + fr(b2) <= 0:
        raise Cannot(f'x = {x} gives a side that is not positive')
    return [x]


@solver('sim_overlap')
def _sim_overlap(ab, ad, ac, ae):
    if fr(ab) * fr(ae) != fr(ac) * fr(ad):
        raise Cannot('DE would not be parallel to BC with these lengths')
    return [fr(ab) - fr(ad), fr(ac) - fr(ae), fr(ab) / fr(ad)]


@solver('sim_map_area')
def _sim_map_area(scale, map_cm2):
    return [fr(map_cm2) * fr(scale) ** 2 / Fraction(100000) ** 2]


@solver('sim_vol_from_lengths')
def _sim_vol_from_lengths(l_small, l_large, vol):
    return [fr(vol) * (fr(l_large) / fr(l_small)) ** 3]


@solver('sim_quad_angles')
def _sim_quad_angles(a, b, c):
    d = _real(360 - fr(a) - fr(b) - fr(c), 0, 180)
    return [d, fr(a), fr(b), fr(c), d]


@solver('sim_chain')
def _sim_chain(r1, r2, r3, r4, side):
    return [fr(side) * fr(r2) / fr(r1) * fr(r4) / fr(r3)]


@solver('sim_frustum')
def _sim_frustum(height, radius, cut):
    r_small = fr(radius) * fr(cut) / fr(height)
    return [(fr(radius) ** 2 * fr(height) - r_small ** 2 * fr(cut)) / 3]


@solver('sim_quad_prop')
def _sim_quad_prop(xy, add_qr, add_yz):
    """x / xy = (x + add_qr) / (x + add_yz): x^2 + (add_yz - xy) x - xy add_qr = 0, positive root."""
    b, c = fr(add_yz) - fr(xy), -fr(xy) * fr(add_qr)
    disc = b * b - 4 * c
    root = _exact_root(disc, 2) if disc > 0 else None
    if root is None:
        raise Cannot('no positive solution')
    x = (-b + root) / 2
    if x <= 0:
        raise Cannot('no positive solution')
    return [x, x / fr(xy)]


@solver('sim_bpt')
def _sim_bpt(ad, db, ac):
    ae = fr(ac) * fr(ad) / (fr(ad) + fr(db))
    return [ae, fr(ac) - ae]


@solver('sim_cone_scale')
def _sim_cone_scale(r_small, r_large, vol, sa):
    k = fr(r_large) / fr(r_small)
    return [fr(vol) * k ** 3, fr(sa) * k ** 2]


@solver('sim_shadow')
def _sim_shadow(h1, s1, s2):
    return [fr(h1) * fr(s2) / fr(s1)]


@solver('sim_bisector')
def _sim_bisector(ab, ac, bc):
    total = fr(ab) + fr(ac)
    return [fr(bc) * fr(ab) / total, fr(bc) * fr(ac) / total]


@solver('sim_rect_alg')
def _sim_rect_alg(a, b, c, d, w1, w2):
    """Rectangle (a x + b) by w1 is similar to (c x + d) by w2, sides matched in the order written."""
    denom = fr(a) * fr(w2) - fr(c) * fr(w1)
    if denom == 0:
        raise Cannot('no single solution')
    x = (fr(d) * fr(w1) - fr(b) * fr(w2)) / denom
    l1, l2 = fr(a) * x + fr(b), fr(c) * x + fr(d)
    if x <= 0 or l1 <= 0 or l2 <= 0:
        raise Cannot(f'x = {x} gives a side that is not positive')
    return [x, l1, fr(w1), l2, fr(w2)]


@solver('sim_series')
def _sim_series(sides):
    biggest = max(fr(s) for s in sides)
    total = sum((fr(s) / biggest) ** 2 for s in sides)
    return [_ratio(total)]


@solver('sim_model')
def _sim_model(scale, vol_cm3, flr_cm2):
    return [fr(vol_cm3) * fr(scale) ** 3 / 10 ** 6, fr(flr_cm2) * fr(scale) ** 2 / 10 ** 4]


@solver('sim_vol_sa')
def _sim_vol_sa(sa_small, sa_large, vol):
    k = _exact_root(fr(sa_large) / fr(sa_small), 2)
    return [k, fr(vol) * k ** 3]


# ─────────────────────────────────────────────────────────────────────────────
# Questions that are read from their own wording
# ─────────────────────────────────────────────────────────────────────────────

_SIDE_PAIR = re.compile(r'\b([A-Z])([A-Z]) = ([A-Z])([A-Z]) = (\d+) cm')
_ANGLE_PAIR = re.compile(r'angle ([A-Z]) = angle ([A-Z]) = (\d+)°')


def _congruence_condition(text):
    """The congruence condition shown by the pairs of equal parts a question states."""
    text = text.replace('−', '-')
    if 'right angle' in text and 'hypotenuse' in text:
        hyps = re.findall(r'hypotenuse [A-Z]{2} = (\d+) cm', text)
        legs = re.findall(r'and [A-Z]{2} = (\d+) cm', text)
        if len(hyps) == 2 and hyps[0] == hyps[1] and len(legs) == 2 and legs[0] == legs[1]:
            if int(legs[0]) >= int(hyps[0]):
                raise Cannot('a leg cannot be as long as the hypotenuse')
            return 'rhs'
        raise Cannot('cannot read the right-angled triangles')
    triples = re.findall(r'has sides (\d+) cm, (\d+) cm and (\d+) cm', text)
    if len(triples) == 2:
        if sorted(map(int, triples[0])) != sorted(map(int, triples[1])):
            raise Cannot('the two triangles do not have the same three sides')
        a, b, c = sorted(map(int, triples[0]))
        if a + b <= c:
            raise Cannot('these three lengths cannot make a triangle')
        return 'sss'
    sides, angles = _SIDE_PAIR.findall(text), _ANGLE_PAIR.findall(text)
    if len(sides) == 2 and len(angles) == 1:
        shared = set(sides[0][:2]) & set(sides[1][:2])
        return 'sas' if shared == {angles[0][0]} else 'ssa'
    if len(sides) == 1 and len(angles) == 2:
        ends = set(sides[0][:2])
        if sum(int(a[2]) for a in angles) >= 180:
            raise Cannot('the two angles add to 180 degrees or more')
        return 'asa' if ends == {angles[0][0], angles[1][0]} else 'aas'
    raise Cannot('cannot read which parts are equal')


@solver('sim_congruence', problem=True)
def _sim_congruence(_p=None, _records=None):
    cond = _congruence_condition(plain(_p['question']))
    return [Pick(lambda t: norm_text(t) == cond, f'the condition {cond.upper()}')]


@solver('sim_altitude', problem=True)
def _sim_altitude(_p=None, _records=None):
    text = plain(_p['question'])
    m = re.search(r'AD = (\d+) cm and DB = (\d+) cm', text)
    if not m:
        raise Cannot('cannot read AD and DB')
    cd = sqrt_atom(Fraction(int(m.group(1)) * int(m.group(2))))
    def proves_with_cbd(t):
        return 'CBD' in t and 'AD/CD = CD/DB' in t

    return [Pick(lambda t: 'common' in t and '90' in t and 'AA' in t, 'the AA reason for ACD ~ ACB'),
            Pick(_pick_test(_p, 1, proves_with_cbd), 'the proof that uses triangle CBD'), cd]


# ─────────────────────────────────────────────────────────────────────────────
# Circle theorems in the practice variants
# ─────────────────────────────────────────────────────────────────────────────

def _angle(x, lo=0, hi=180):
    return _real(fr(x), lo, hi)


@solver('circ_half')
def _circ_half(angle):
    return [_angle(fr(angle) / 2)]


@solver('circ_semicircle_90')
def _circ_semicircle_90():
    return [Fraction(90)]


@solver('circ_semi_third')
def _circ_semi_third(angle):
    return [_angle(90 - fr(angle), 0, 90)]


@solver('circ_opposite')
def _circ_opposite(angle):
    return [_angle(180 - fr(angle))]


@solver('circ_tangent_triangle')
def _circ_tangent_triangle(angle):
    return [Fraction(90), _angle(90 - fr(angle), 0, 90)]


@solver('circ_tangent_base')
def _circ_tangent_base(apex):
    return [_angle((180 - fr(apex)) / 2, 0, 90)]


@solver('circ_tangents_reflex')
def _circ_tangents_reflex(angle):
    return [_angle(360 - (180 - fr(angle)), 180, 360)]


@solver('circ_alt_straight')
def _circ_alt_straight(angle):
    return [_angle(angle), _angle(180 - fr(angle))]


@solver('circ_centre_both')
def _circ_centre_both(centre):
    c = fr(centre)
    return [_angle((180 - c) / 2, 0, 90), _angle(c / 2)]


@solver('circ_centre_minor')
def _circ_centre_minor(centre):
    c = fr(centre)
    return [_angle((180 - c) / 2, 0, 90), _angle((360 - c) / 2)]


@solver('circ_alt_parallel')
def _circ_alt_parallel(angle):
    return [_angle(angle), _angle(angle)]


@solver('circ_cyclic_alg')
def _circ_cyclic_alg(a1, b1, a2, b2):
    coef = fr(a1) + fr(a2)
    if coef == 0:
        raise Cannot('no single solution')
    x = (180 - fr(b1) - fr(b2)) / coef
    one, two = fr(a1) * x + fr(b1), fr(a2) * x + fr(b2)
    if x <= 0 or not (0 < one < 180 and 0 < two < 180):
        raise Cannot(f'x = {x} gives angles {one} and {two}')
    return [x, one, two]


@solver('circ_chord_length')
def _circ_chord_length(r, d):
    if fr(d) >= fr(r):
        raise Cannot('the chord must be closer to the centre than the radius')
    half = sqrt_atom(fr(r) ** 2 - fr(d) ** 2)
    if isinstance(half, Fraction):
        return [2 * half]
    return [Approx(2 * half.value)]


@solver('circ_isos_same_seg')
def _circ_isos_same_seg(angle):
    a = fr(angle)
    base = (180 - a) / 2
    if base.denominator != 1:
        raise Cannot(f'the base angle {base} is not a whole number of degrees')
    return [base, a]


@solver('circ_half_twice')
def _circ_half_twice(centre):
    return [_angle(fr(centre) / 2), _angle(fr(centre) / 2)]


@solver('circ_cyclic_parallel')
def _circ_cyclic_parallel(angle):
    return [_angle(180 - fr(angle)), _angle(180 - fr(angle))]


@solver('circ_reflex_half')
def _circ_reflex_half(reflex):
    return [_angle(fr(reflex) / 2, 90, 180)]


@solver('circ_both_arcs')
def _circ_both_arcs(centre):
    c = fr(centre)
    return [_angle(c / 2), _angle((360 - c) / 2)]


@solver('circ_both_arcs_sum')
def _circ_both_arcs_sum(centre):
    c = fr(centre)
    return [_angle(c / 2), _angle((360 - c) / 2), Fraction(180)]


@solver('circ_cyclic_ext')
def _circ_cyclic_ext(angle):
    return [_angle(180 - fr(angle)), _angle(fr(angle))]


@solver('circ_same_seg2')
def _circ_same_seg2(a, b):
    return [fr(a), fr(b)]


@solver('circ_alt_semicircle')
def _circ_alt_semicircle(angle):
    return [_angle(angle, 0, 90), _angle(90 - fr(angle), 0, 90)]


@solver('circ_radius_from_angle')
def _circ_radius_from_angle(apb, po):
    half = math.radians(float(fr(apb)) / 2)
    return [Approx(float(fr(po)) * math.sin(half))]


@solver('circ_centre_cyclic')
def _circ_centre_cyclic(centre):
    c = fr(centre)
    return [_angle(c / 2), _angle(180 - c / 2)]


@solver('circ_chords_angle')
def _circ_chords_angle(arc1, arc2):
    return [_angle((fr(arc1) + fr(arc2)) / 2)]


@solver('circ_secants')
def _circ_secants(far, near):
    if fr(far) <= fr(near):
        raise Cannot('the far arc must be bigger than the near arc')
    return [_angle((fr(far) - fr(near)) / 2)]


@solver('circ_alt_triangle')
def _circ_alt_triangle(angle, bac):
    return [_angle(angle), _angle(180 - fr(angle) - fr(bac))]


@solver('circ_chord_perp')
def _circ_chord_perp(r, angle):
    half = math.radians(float(fr(angle)) / 2)
    return [Approx(2 * float(fr(r)) * math.sin(half)), Approx(float(fr(r)) * math.cos(half))]


def _pick_test(_p, index, predicate):
    """Test for a 'pick one' field of a number_fields key: the keyed id's text satisfies ``predicate`` and
    no other statement in the bank does."""
    bank = {str(b.get('id')): plain(str(b.get('text')))
            for b in ((_p.get('answer_field_options') or [])[index] or [])}

    def test(raw):
        ids = str(raw).split('|')[2:]
        if len(ids) != 1 or ids[0] not in bank or not predicate(bank[ids[0]]):
            return False
        return not any(predicate(t) for i, t in bank.items() if i != ids[0])
    return test


def _relation(text, oab, adb):
    """Does 'angle ADB = ... angle OAB' hold for these two numbers?"""
    t = text.replace('−', '-')
    m = re.fullmatch(r'angle ADB = (?:(\d+)° ([-+]) angle OAB|(\d+) × angle OAB|angle OAB)', t)
    if not m:
        return False
    if m.group(1):
        k = int(m.group(1))
        return adb == (k - oab if m.group(2) == '-' else k + oab)
    if m.group(3):
        return adb == int(m.group(3)) * oab
    return adb == oab


@solver('circ_three', problem=True)
def _circ_three(centre, _p=None, _records=None):
    c = fr(centre)
    oab, acb = _angle((180 - c) / 2, 0, 90), _angle(c / 2)
    return [oab, acb, acb, Pick(_pick_test(_p, 3, lambda t: _relation(t, oab, acb)),
                                'the one relation that holds: angle ADB = 90 - angle OAB')]


@solver('circ_double')
def _circ_double(angle):
    return [_angle(2 * fr(angle), 0, 360)]


def _centre_diagram(expected):
    def check(inputs, html):
        drawn = read_centre_angle(one_svg(html))
        want = float(expected(inputs))
        return [] if abs(drawn - want) < 0.5 else [f'the drawing shows an angle of {drawn:.1f} degrees at the centre '
                                                    f'but the question says {want:g}']
    return check


diagram('circ_half')(_centre_diagram(lambda i: fr(i['angle'])))
diagram('circ_double')(_centre_diagram(lambda i: 2 * fr(i['angle'])))
