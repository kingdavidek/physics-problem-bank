"""Solvers for Pythagoras, compound measures, mensuration, trigonometry and bearings.

Independence rule: this module recomputes answers from first principles. It must not import
any generator module or helper (checked by the test); only the standard library and sympy.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from generators.shared.rounding import round_half_up

from .core import (AnyOf, Approx, Cannot, Pick, Surd, SurdOver, parse_num, sqrt_atom)  # noqa: F401
from .registry import fr, solver
from .solvers_number import eval_expression


def _sq(x):
    return fr(x) * fr(x)


# ─────────────────────────────────────────────────────────────────────────────
# Pythagoras
# ─────────────────────────────────────────────────────────────────────────────

@solver('pyth_hyp')
def _pyth_hyp(a, b):
    return [sqrt_atom(_sq(a) + _sq(b))]


@solver('pyth_leg')
def _pyth_leg(c, a):
    if fr(c) <= fr(a):
        raise Cannot('hypotenuse must exceed the leg')
    return [sqrt_atom(_sq(c) - _sq(a))]


@solver('pyth_is_right')
def _pyth_is_right(a, b, c):
    s = sorted([fr(a), fr(b), fr(c)])
    return ['yes' if _sq(s[0]) + _sq(s[1]) == _sq(s[2]) else 'no']


@solver('pyth_perimeter')
def _pyth_perimeter(a, b):
    h = sqrt_atom(_sq(a) + _sq(b))
    if isinstance(h, Approx):
        return [Approx(float(fr(a)) + float(fr(b)) + h.value)]
    return [fr(a) + fr(b) + h]


@solver('pyth_area_to_sides')
def _pyth_area_to_sides(area, a):
    b = 2 * fr(area) / fr(a)
    return [b, sqrt_atom(_sq(a) + _sq(b))]


@solver('pyth_isosceles_height')
def _pyth_isosceles_height(base, side):
    return [sqrt_atom(_sq(side) - _sq(fr(base) / 2))]


@solver('pyth_space_diag')
def _pyth_space_diag(l, w, h):
    return [sqrt_atom(_sq(l) + _sq(w) + _sq(h))]


@solver('pyth_space_diag_two')
def _pyth_space_diag_two(l, w, h):
    return [sqrt_atom(_sq(l) + _sq(w)), sqrt_atom(_sq(l) + _sq(w) + _sq(h))]


@solver('pyth_dist')
def _pyth_dist(x1, y1, x2, y2):
    return [sqrt_atom(_sq(fr(x2) - fr(x1)) + _sq(fr(y2) - fr(y1)))]


@solver('pyth_dist_surd')
def _pyth_dist_surd(x1, y1, x2, y2):
    n = _sq(fr(x2) - fr(x1)) + _sq(fr(y2) - fr(y1))
    return [Surd(1, int(n))]


@solver('pyth_ladder_slide')
def _pyth_ladder_slide(ladder, base, slide):
    return [sqrt_atom(_sq(ladder) - _sq(fr(base) + fr(slide)))]


@solver('pyth_ladder_height')
def _pyth_ladder_height(ladder, base):
    return [sqrt_atom(_sq(ladder) - _sq(base))]


@solver('pyth_cut_corner')
def _pyth_cut_corner(length, width, slope, cut):
    other = sqrt_atom(_sq(slope) - _sq(cut))
    if isinstance(other, Approx):
        return [Approx(float(fr(length) * fr(width)) - float(fr(cut)) * other.value / 2)]
    return [fr(length) * fr(width) - fr(cut) * other / 2]


@solver('pyth_cube_diag')
def _pyth_cube_diag(edge):
    return [Surd(int(edge), 3), Approx(float(fr(edge)) * math.sqrt(3))]


@solver('pyth_two_triangles')
def _pyth_two_triangles(a, b, c, x, y, z, ask):
    def right(s):
        s = sorted(fr(v) for v in s)
        return s[0] + s[1] > s[2] and _sq(s[0]) + _sq(s[1]) == _sq(s[2])
    r1, r2 = right((a, b, c)), right((x, y, z))
    word = 'both' if r1 and r2 else '1' if r1 else '2' if r2 else 'neither'
    perim = fr(x) + fr(y) + fr(z) if ask == 'tri2' else fr(a) + fr(b) + fr(c)
    return [word, perim]


@solver('pyth_roof_truss')
def _pyth_roof_truss(span, rise):
    rafter = sqrt_atom(_sq(fr(span) / 2) + _sq(rise))
    if isinstance(rafter, Approx):
        raise Cannot('rafter not exact')
    return [rafter, fr(rise), 2 * rafter + fr(span)]


@solver('pyth_journey')
def _pyth_journey(east, north, east2, north2):
    d = sqrt_atom(_sq(east) + _sq(north))
    ob = sqrt_atom(_sq(east2) + _sq(north2))
    if isinstance(d, Approx):
        raise Cannot('journey not exact')
    return [d, ob, fr(east) + fr(north) - d]


@solver('pyth_ladder_two')
def _pyth_ladder_two(ladder, base1, base2):
    h1 = sqrt_atom(_sq(ladder) - _sq(base1))
    h2 = sqrt_atom(_sq(ladder) - _sq(base2))
    if isinstance(h1, Approx) or isinstance(h2, Approx):
        raise Cannot('heights not exact')
    return [h1, h2, h1 - h2]


@solver('pyth_student_check')
def _pyth_student_check(a, b, c):
    """The 'student says a+b=c' choice question: keyed option must say right-angled iff a^2+b^2=c^2."""
    s = sorted([fr(a), fr(b), fr(c)])
    right = _sq(s[0]) + _sq(s[1]) == _sq(s[2])

    def test(text):
        t = text.lower()
        wrong_test = 'wrong test' in t
        says_right = 'is right-angled' in t and 'not right-angled' not in t
        return wrong_test and (says_right if right else 'not right-angled' in t)
    return [Pick(test, f'says the student used the wrong test and the triangle is {"" if right else "not "}right-angled')]


# ─────────────────────────────────────────────────────────────────────────────
# Compound measures
# ─────────────────────────────────────────────────────────────────────────────

def _alg_value(text, **variables):
    """Numeric value of a keyed algebraic expression once its variables are given numbers."""
    t = str(text)
    for name, val in variables.items():
        t = re.sub(rf'(?<![A-Za-z]){name}(?![A-Za-z])', f'({val})', t)
    return eval_expression(t)


def _alg_pick(build, desc):
    """Pick that accepts a keyed algebraic field when it equals ``build(v)`` at three test values of v."""
    def test(text):
        try:
            return all(_alg_value(text, v=v, d=v) == build(Fraction(v)) for v in (3, 7, 11))
        except Exception:
            return False
    return Pick(test, desc)


@solver('cm_kmh_to_ms')
def _cm_kmh_to_ms(kmh):
    return [fr(kmh) * 1000 / 3600]


@solver('cm_ms_to_kmh')
def _cm_ms_to_kmh(ms):
    return [fr(ms) * 3600 / 1000]


@solver('cm_density_compare')
def _cm_density_compare(a, b):
    def parse(text):
        m = re.match(r'\s*([A-Za-z]+ [A-Z]):.*?mass ([\d.]+) g, volume ([\d.]+) cm', text)
        if not m:
            raise Cannot(f'cannot read {text!r}')
        return m.group(1), fr(m.group(2)) / fr(m.group(3))
    (na, da), (nb, db) = parse(a), parse(b)
    if da == db:
        raise Cannot('equal densities')
    return [na if da > db else nb]


@solver('cm_avg_speed')
def _cm_avg_speed(legs):
    """Average speed from (distance, speed) legs."""
    dist = sum(fr(d) for d, _ in legs)
    time = sum(fr(d) / fr(s) for d, s in legs)
    return [dist / time]


@solver('cm_avg_speed_time')
def _cm_avg_speed_time(legs):
    """Average speed from (time, speed) legs."""
    dist = sum(fr(t) * fr(s) for t, s in legs)
    time = sum(fr(t) for t, _ in legs)
    return [dist / time]


@solver('cm_avg_speed_equal')
def _cm_avg_speed_equal(s1, s2):
    """Equal distances out and back: total distance 2 (one unit each way) over total time."""
    return [Fraction(2) / (1 / fr(s1) + 1 / fr(s2))]


@solver('cm_speed_hm')
def _cm_speed_hm(s, h, m):
    return [fr(s) * (fr(h) + fr(m) / 60)]


@solver('cm_dist_mins')
def _cm_dist_mins(s, mins):
    return [fr(s) * fr(mins) / 60]


@solver('cm_alloy_vol')
def _cm_alloy_vol(d1, v1, d2, v2):
    return [(fr(d1) * fr(v1) + fr(d2) * fr(v2)) / (fr(v1) + fr(v2))]


@solver('cm_box_pressure')
def _cm_box_pressure(mass, g, length, width):
    return [fr(mass) * fr(g) / (fr(length) * fr(width))]


@solver('cm_sphere_mass')
def _cm_sphere_mass(r, density):
    return [Approx(float(fr(density)) * 4 / 3 * math.pi * float(fr(r)) ** 3, ('dp', 1))]


@solver('cm_ms_and_km')
def _cm_ms_and_km(speed, time):
    dist = fr(speed) * fr(time)
    return [dist, dist / 1000]


@solver('cm_pressure_units')
def _cm_pressure_units(f, a):
    p = fr(f) / fr(a)
    return [p, p * 10000]


@solver('cm_float_sink')
def _cm_float_sink(mass, vol):
    return ['float' if fr(mass) < fr(vol) else 'sink']


@solver('cm_run')
def _cm_run(speed, mins):
    kmh = fr(speed) * 3600 / 1000
    return [kmh, Approx(kmh * fr(mins) / 60, ('dp', 2))]


@solver('cm_hollow_cyl_mass')
def _cm_hollow_cyl_mass(R, r, h, density):
    area = float(fr(R) ** 2 - fr(r) ** 2)
    return [Approx(float(fr(density)) * math.pi * area * float(fr(h)), ('unit', 1))]


@solver('cm_meeting')
def _cm_meeting(s1, s2, dist):
    t = fr(dist) / (fr(s1) + fr(s2))
    return [t, fr(s1) * t]


@solver('cm_overtake')
def _cm_overtake(slow, fast, head_min):
    gap = fr(slow) * fr(head_min) / 60
    return [Approx(gap / (fr(fast) - fr(slow)) * 60, ('unit', 1))]


@solver('cm_alloy_pct')
def _cm_alloy_pct(pa, da, pb, db):
    return [Approx(fr(100) / (fr(pa) / fr(da) + fr(pb) / fr(db)), ('sf', 3))]


@solver('cm_water_pressure')
def _cm_water_pressure(rho, g, depth):
    return [fr(rho) * fr(g) * fr(depth)]


@solver('cm_two_halves')
def _cm_two_halves(d, k):
    half = fr(d) / 2
    return [
        _alg_pick(lambda v: half / v, 'time for the first half, half/v'),
        _alg_pick(lambda v: half / (fr(k) * v), 'time for the second half, half/(k v)'),
        _alg_pick(lambda v: half / v + half / (fr(k) * v), 'total time, half/v + half/(k v)'),
    ]


@solver('cm_pipes')
def _cm_pipes(vol, fill, drain):
    if fr(fill) <= fr(drain):
        raise Cannot('tank never fills')
    return [fr(vol) / (fr(fill) - fr(drain))]


@solver('cm_harmonic_steps')
def _cm_harmonic_steps(s1, s2):
    mean = Fraction(2) / (1 / fr(s1) + 1 / fr(s2))
    return [
        _alg_pick(lambda d: d / fr(s1) + d / fr(s2), 'total time d/s1 + d/s2'),
        Pick(lambda t: _try_value(t) == mean, f'average speed expression equal to {mean}'),
        mean,
    ]


def _try_value(text):
    try:
        return eval_expression(str(text))
    except Exception:
        return None


@solver('cm_density_kgm3')
def _cm_density_kgm3(d, vol):
    dens = fr(d) * 1000
    return [dens, dens * fr(vol)]


@solver('cm_concentration')
def _cm_concentration(conc, vol, ml):
    return [fr(conc) * fr(vol), fr(conc) * fr(ml) / 1000]


@solver('cm_relative')
def _cm_relative(s1, s2, dist, direction):
    if direction not in ('same', 'opposite'):
        raise Cannot(f'unknown direction {direction!r}')
    rel = fr(s1) - fr(s2) if direction == 'same' else fr(s1) + fr(s2)
    return [Approx(fr(dist) / rel * 60, ('unit', 1))]


@solver('cm_composite_density')
def _cm_composite_density(r1, r2, d1, d2):
    return [(fr(d1) * fr(r1) + fr(d2) * fr(r2)) / (fr(r1) + fr(r2))]


@solver('cm_hydraulic')
def _cm_hydraulic(f_in, a_in, a_out):
    p = fr(f_in) / fr(a_in)
    return [p, p * fr(a_out)]


@solver('cm_min_area')
def _cm_min_area(mass, max_pressure, g):
    w = fr(mass) * fr(g)
    return [w, w / fr(max_pressure)]


@solver('cm_pipe_flow')
def _cm_pipe_flow(r, speed, density):
    area = math.pi * float(fr(r)) ** 2
    vol = area * float(fr(speed)) * 100
    return [Approx(area, ('dp', 2)), Approx(vol, ('dp', 2)), Approx(float(fr(density)) * vol, ('dp', 2))]


# ─────────────────────────────────────────────────────────────────────────────
# Mensuration
# ─────────────────────────────────────────────────────────────────────────────

def _f(x):
    return float(fr(x))


def _dp2(value):
    return Approx(value, ('dp', 2))


@solver('mens_rect_perimeter')
def _mens_rect_perimeter(l, w):
    return [2 * (fr(l) + fr(w))]


@solver('mens_tri_area')
def _mens_tri_area(b, h):
    return [fr(b) * fr(h) / 2]


@solver('mens_trapezium')
def _mens_trapezium(a, b, h):
    return [(fr(a) + fr(b)) * fr(h) / 2]


@solver('mens_circumference')
def _mens_circumference(r):
    return [_dp2(2 * math.pi * _f(r))]


@solver('mens_circle_area')
def _mens_circle_area(r):
    return [_dp2(math.pi * _f(r) ** 2)]


@solver('mens_cuboid_vol')
def _mens_cuboid_vol(l, w, h):
    return [fr(l) * fr(w) * fr(h)]


@solver('mens_cuboid_sa')
def _mens_cuboid_sa(l, w, h):
    l, w, h = fr(l), fr(w), fr(h)
    return [2 * (l * w + l * h + w * h)]


@solver('mens_tri_prism_vol')
def _mens_tri_prism_vol(b, h, length):
    return [fr(b) * fr(h) / 2 * fr(length)]


@solver('mens_l_shape')
def _mens_l_shape(a, c, b, d):
    return [fr(a) * fr(c) - fr(b) * fr(d)]


@solver('mens_cm2_to_m2')
def _mens_cm2_to_m2(l, w):
    return [fr(l) * fr(w) / 10000]


@solver('mens_diameter')
def _mens_diameter(circ):
    return [_dp2(_f(circ) / math.pi)]


@solver('mens_arc')
def _mens_arc(r, angle):
    return [_dp2(_f(angle) / 360 * 2 * math.pi * _f(r))]


@solver('mens_sector_area')
def _mens_sector_area(r, angle):
    return [_dp2(_f(angle) / 360 * math.pi * _f(r) ** 2)]


@solver('mens_cyl_vol')
def _mens_cyl_vol(r, h):
    return [_dp2(math.pi * _f(r) ** 2 * _f(h))]


@solver('mens_cyl_sa')
def _mens_cyl_sa(r, h):
    return [_dp2(2 * math.pi * _f(r) * (_f(r) + _f(h)))]


@solver('mens_cone_vol')
def _mens_cone_vol(r, h):
    return [_dp2(math.pi * _f(r) ** 2 * _f(h) / 3)]


@solver('mens_sphere_vol')
def _mens_sphere_vol(r):
    return [_dp2(4 / 3 * math.pi * _f(r) ** 3)]


@solver('mens_sphere_sa')
def _mens_sphere_sa(r):
    return [_dp2(4 * math.pi * _f(r) ** 2)]


@solver('mens_pyramid_vol')
def _mens_pyramid_vol(l, w, h):
    return [fr(l) * fr(w) * fr(h) / 3]


@solver('mens_annulus')
def _mens_annulus(R, r):
    return [_dp2(math.pi * (_f(R) ** 2 - _f(r) ** 2))]


@solver('mens_sector_perimeter')
def _mens_sector_perimeter(r, angle):
    return [_dp2(_f(angle) / 360 * 2 * math.pi * _f(r) + 2 * _f(r))]


@solver('mens_cone_sa_slant')
def _mens_cone_sa_slant(r, slant):
    return [_dp2(math.pi * _f(r) * (_f(r) + _f(slant)))]


@solver('mens_radius_from_area')
def _mens_radius_from_area(area):
    return [_dp2(math.sqrt(_f(area) / math.pi))]


@solver('mens_fill_time')
def _mens_fill_time(r, h, rate):
    return [_dp2(math.pi * _f(r) ** 2 * _f(h) / 1000 / _f(rate))]


@solver('mens_similar')
def _mens_similar(k, value, power):
    return [fr(value) * fr(k) ** int(power)]


@solver('mens_cyl_hemisphere')
def _mens_cyl_hemisphere(r, h):
    return [_dp2(math.pi * _f(r) ** 2 * _f(h) + 2 / 3 * math.pi * _f(r) ** 3)]


@solver('mens_tank')
def _mens_tank(r, h, rate):
    vol = math.pi * _f(r) ** 2 * _f(h)
    return [_dp2(vol / 1000), _dp2(2 * math.pi * _f(r) * (_f(r) + _f(h))), _dp2(vol / 1000 / _f(rate))]


@solver('mens_garden')
def _mens_garden(length, width, cost):
    l, w = _f(length), _f(width)
    area = l * w + math.pi * w * w / 8
    return [_dp2(2 * l + w + math.pi * w / 2), _dp2(area), Approx(area * _f(cost), ('dp', 2))]


@solver('mens_cone_container')
def _mens_cone_container(r, h, cost):
    r_, h_ = _f(r), _f(h)
    curved = math.pi * r_ * math.sqrt(r_ * r_ + h_ * h_)
    return [_dp2(math.pi * r_ * r_ * h_ / 3), _dp2(curved), Approx(curved / 10000 * _f(cost), ('dp', 2))]


@solver('mens_cone_sa_height')
def _mens_cone_sa_height(r, h):
    r_, h_ = _f(r), _f(h)
    return [_dp2(math.pi * r_ * (r_ + math.sqrt(r_ * r_ + h_ * h_)))]


@solver('mens_sphere_radius_from_volume')
def _mens_sphere_radius_from_volume(vol):
    return [_dp2((3 * _f(vol) / (4 * math.pi)) ** (1 / 3))]


@solver('mens_exact_pi_cyl')
def _mens_exact_pi_cyl(r, h):
    return [fr(r) ** 2 * fr(h)]


@solver('mens_frustum')
def _mens_frustum(R, r, h):
    R_, r_ = _f(R), _f(r)
    return [_dp2(math.pi * _f(h) / 3 * (R_ * R_ + R_ * r_ + r_ * r_))]


@solver('mens_hemi_cone_sa')
def _mens_hemi_cone_sa(r, h):
    r_, h_ = _f(r), _f(h)
    return [_dp2(2 * math.pi * r_ * r_ + math.pi * r_ * math.sqrt(r_ * r_ + h_ * h_))]


@solver('mens_segment_60')
def _mens_segment_60(r):
    r_ = _f(r)
    return [_dp2(math.pi * r_ * r_ / 6 - 0.5 * r_ * r_ * math.sin(math.pi / 3))]


@solver('mens_cyl_mass')
def _mens_cyl_mass(density, r, h):
    return [_dp2(_f(density) * math.pi * _f(r) ** 2 * _f(h))]


@solver('mens_submerged_rise')
def _mens_submerged_rise(sphere_r, cyl_r):
    return [_dp2(4 / 3 * _f(sphere_r) ** 3 / _f(cyl_r) ** 2)]


@solver('mens_prism_compound')
def _mens_prism_compound(a, h, b, length):
    return [(fr(a) * fr(h) + fr(a) * fr(b) / 2) * fr(length)]


@solver('mens_cyl_height')
def _mens_cyl_height(vol, r):
    return [_dp2(_f(vol) / (math.pi * _f(r) ** 2))]


@solver('mens_arc_exact')
def _mens_arc_exact(r, angle):
    return [Fraction(int(angle), 360) * 2 * fr(r)]


@solver('mens_cone_vol_from_slant')
def _mens_cone_vol_from_slant(r, slant):
    r_, l_ = _f(r), _f(slant)
    return [_dp2(math.pi * r_ * r_ * math.sqrt(l_ * l_ - r_ * r_) / 3)]


@solver('mens_tri_prism_sa')
def _mens_tri_prism_sa(a, b, length):
    a_, b_ = _f(a), _f(b)
    return [_dp2(a_ * b_ + (a_ + b_ + math.sqrt(a_ * a_ + b_ * b_)) * _f(length))]


@solver('mens_open_box')
def _mens_open_box(x, total):
    x_ = fr(x)
    h = (fr(total) - x_ * x_) / (4 * x_)
    return [_dp2(h), _dp2(x_ * x_ * h)]


@solver('mens_silo')
def _mens_silo(r, h, density):
    r_, h_ = _f(r), _f(h)
    vol = math.pi * r_ * r_ * h_ + 2 / 3 * math.pi * r_ ** 3
    return [_dp2(vol), _dp2(2 * math.pi * r_ * h_ + 2 * math.pi * r_ * r_), _dp2(vol * _f(density))]


@solver('mens_similar_cuboids')
def _mens_similar_cuboids(k, l, w, h):
    k_, l_, w_, h_ = fr(k), fr(l), fr(w), fr(h)
    sa = 2 * (l_ * w_ + l_ * h_ + w_ * h_)
    return [k_, sa * k_ ** 2, l_ * w_ * h_ * k_ ** 3]


@solver('mens_frustum_tank')
def _mens_frustum_tank(R, r, h, pct):
    R_, r_ = _f(R), _f(r)
    vol = math.pi * _f(h) / 3 * (R_ * R_ + R_ * r_ + r_ * r_)
    return [_dp2(vol), _dp2(vol * _f(pct) / 100 / 1000)]


# ─────────────────────────────────────────────────────────────────────────────
# Trigonometry
# ─────────────────────────────────────────────────────────────────────────────

def _rad(deg):
    return math.radians(_f(deg))


def _deg1(value):
    return Approx(math.degrees(value), ('dp', 1))


def _ratio_of(kind, angle):
    """The factor f with side = hyp * f for each side kind."""
    return {'hyp': 1.0, 'opp': math.sin(_rad(angle)), 'adj': math.cos(_rad(angle))}[kind]


@solver('trig_side')
def _trig_side(angle, known, known_kind, find_kind):
    hyp = _f(known) / _ratio_of(known_kind, angle)
    return [_dp2(hyp * _ratio_of(find_kind, angle))]


@solver('trig_angle')
def _trig_angle(opp=None, adj=None, hyp=None):
    if opp is not None and adj is not None:
        return [_deg1(math.atan2(_f(opp), _f(adj)))]
    if adj is not None and hyp is not None:
        return [_deg1(math.acos(_f(adj) / _f(hyp)))]
    if opp is not None and hyp is not None:
        return [_deg1(math.asin(_f(opp) / _f(hyp)))]
    raise Cannot('need two sides')


@solver('trig_isosceles_apex')
def _trig_isosceles_apex(equal, base):
    return [_deg1(2 * math.asin(_f(base) / 2 / _f(equal)))]


@solver('trig_cosine_angle')
def _trig_cosine_angle(a, b, c):
    a_, b_, c_ = _f(a), _f(b), _f(c)
    return [_deg1(math.acos((b_ * b_ + c_ * c_ - a_ * a_) / (2 * b_ * c_)))]


@solver('trig_sine_side')
def _trig_sine_side(known_angle, known_side, target_angle):
    return [_dp2(_f(known_side) * math.sin(_rad(target_angle)) / math.sin(_rad(known_angle)))]


@solver('trig_cosine_side')
def _trig_cosine_side(b, c, angle):
    b_, c_ = _f(b), _f(c)
    return [_dp2(math.sqrt(b_ * b_ + c_ * c_ - 2 * b_ * c_ * math.cos(_rad(angle))))]


@solver('trig_area')
def _trig_area(a, b, angle):
    return [_dp2(0.5 * _f(a) * _f(b) * math.sin(_rad(angle)))]


@solver('trig_area_side')
def _trig_area_side(a, angle, area):
    return [_dp2(2 * _f(area) / (_f(a) * math.sin(_rad(angle))))]


@solver('trig_3d_angle')
def _trig_3d_angle(l, w, h):
    return [_deg1(math.atan2(_f(h), math.hypot(_f(l), _f(w))))]


@solver('trig_sine_angle')
def _trig_sine_angle(a, b, angle_b):
    ratio = _f(a) * math.sin(_rad(angle_b)) / _f(b)
    if not 0 < ratio <= 1:
        raise Cannot('no triangle')
    return [_deg1(math.asin(ratio))]


def _exact_atom(value):
    """Exact atom for a trigonometric value: a rational, a square root, or a root over a whole number."""
    sq = Fraction(value * value).limit_denominator(1000)
    num, den = math.isqrt(sq.numerator), math.isqrt(sq.denominator)
    if num * num == sq.numerator and den * den == sq.denominator:
        return Fraction(num, den) if value >= 0 else -Fraction(num, den)
    if sq.denominator == 1:
        return Surd(1, sq.numerator)
    d = 1
    while (sq * d * d).denominator != 1:
        d += 1
        if d > 1000:
            raise Cannot(f'no exact form for {value}')
    return SurdOver(1, int((sq * d * d).numerator), d)


def _trig_value(fn, angle):
    return {'sin': math.sin, 'cos': math.cos, 'tan': math.tan}[fn](_rad(angle))


@solver('trig_exact')
def _trig_exact(fn, angle):
    return [_exact_atom(_trig_value(fn, angle))]


@solver('trig_sin2_cos2_30')
def _trig_sin2_cos2_30():
    s2, c2 = math.sin(_rad(30)) ** 2, math.cos(_rad(30)) ** 2
    return [Fraction(s2).limit_denominator(100), Fraction(c2).limit_denominator(100), 1]


@solver('trig_exact_expr')
def _trig_exact_expr(expr):
    """Value of a sum of products of sin/cos/tan of angles in degrees (powers of 2 allowed)."""
    text = str(expr).replace('\\', ' ').replace('°', ' ').replace('^\\circ', ' ')
    text = text.replace('\\cdot', ' ')
    toks = re.findall(r'(sin|cos|tan)\s*(\^\s*2)?\s*(\d+)|(\d+)|([+-])', text)
    if not toks:
        raise Cannot(f'cannot read {expr!r}')
    total, sign, term, pending = 0.0, 1, None, False
    for fn, sq, ang, num, op in toks:
        if op:
            if term is not None:
                total += sign * term
            sign, term = (1 if op == '+' else -1), None
            continue
        factor = float(num) if num else _trig_value(fn, ang) ** (2 if sq else 1)
        term = factor if term is None else term * factor
    if term is not None:
        total += sign * term
    return [_exact_atom(total)]


# ─────────────────────────────────────────────────────────────────────────────
# Bearings
# ─────────────────────────────────────────────────────────────────────────────

_COMPASS = {'North': 0, 'North-East': 45, 'East': 90, 'South-East': 135,
            'South': 180, 'South-West': 225, 'West': 270, 'North-West': 315}


def _bearing_pick(value, label='bearing'):
    """Pick: a typed bearing equals ``value`` rounded to the nearest degree (modulo 360)."""
    target = int(round_half_up(value, 0)) % 360

    def test(text):
        got = parse_num(text)
        return got is not None and got.denominator == 1 and int(got) % 360 == target
    return Pick(test, f'{label} {target:03d}')


def _vec(d, bearing):
    """(east, north) of a leg of length d on a bearing, in floats."""
    b = math.radians(_f(bearing))
    return _f(d) * math.sin(b), _f(d) * math.cos(b)


def _bearing_of(east, north):
    return math.degrees(math.atan2(east, north)) % 360


@solver('brg_compass_name')
def _brg_compass_name(name):
    if name not in _COMPASS:
        raise Cannot(f'unknown direction {name}')
    return [Fraction(_COMPASS[name])]


@solver('brg_back')
def _brg_back(b):
    return [Fraction((int(b) + 180) % 360)]


@solver('brg_identity')
def _brg_identity(b):
    return [Fraction(int(b) % 360)]


@solver('brg_compass')
def _brg_compass(ns, x, ew):
    x = fr(x)
    table = {('N', 'E'): x, ('S', 'E'): 180 - x, ('S', 'W'): 180 + x, ('N', 'W'): 360 - x}
    return [table[(ns, ew)] % 360]


@solver('brg_quadrant')
def _brg_quadrant(b):
    b = int(b)
    return ['ne' if 0 < b < 90 else 'se' if 90 < b < 180 else 'sw' if 180 < b < 270 else 'nw']


@solver('brg_angle_between')
def _brg_angle_between(b1, b2):
    d = abs(int(b2) - int(b1))
    return [Fraction(min(d, 360 - d))]


@solver('brg_cointerior')
def _brg_cointerior(b):
    return [Fraction(180 - int(b)), Fraction((int(b) + 180) % 360)]


@solver('brg_angle_from_east')
def _brg_angle_from_east(b):
    return [Fraction(abs(90 - int(b)))]


@solver('brg_algebraic')
def _brg_algebraic(a, extra):
    base = 90 + int(a)
    return [Fraction((base + 180) % 360), Fraction((base + int(extra)) % 360)]


@solver('brg_back_pair')
def _brg_back_pair(b):
    return [Fraction(int(b) % 360), Fraction((int(b) + 180) % 360)]


@solver('brg_meeting')
def _brg_meeting(sep, v1, v2):
    return [_dp2(_f(sep) / (_f(v1) + _f(v2)))]


def _answers(east, north, want):
    out = []
    for w in want:
        if w == 'east':
            out.append(Approx(east, ('dp', 2)))
        elif w == 'north':
            out.append(Approx(north, ('dp', 2)))
        elif w == 'dist':
            out.append(Approx(math.hypot(east, north), ('dp', 2)))
        elif w == 'bearing':
            out.append(_bearing_pick(_bearing_of(east, north)))
        elif w == 'return_bearing':
            out.append(_bearing_pick(_bearing_of(-east, -north)))
        else:
            raise Cannot(f'unknown want {w!r}')
    return out


@solver('brg_legs')
def _brg_legs(legs, want):
    """Journey of (distance, bearing) legs: totals, straight-line distance, bearings."""
    east = north = 0.0
    for d, b in legs:
        e, n = _vec(d, b)
        east += e
        north += n
    return _answers(east, north, want)


@solver('brg_speed_time')
def _brg_speed_time(speed, time, b, want):
    e, n = _vec(_f(speed) * _f(time), b)
    return _answers(e, n, want)


@solver('brg_en')
def _brg_en(east, north, want):
    return _answers(_f(east), _f(north), want)


@solver('brg_two_ships')
def _brg_two_ships(b1, d1, b2, d2, want):
    """Ships A and B leave port O on bearings b1, b2 at distances d1, d2."""
    ax, ay = _vec(d1, b1)
    bx, by = _vec(d2, b2)
    out = []
    for w in want:
        if w == 'angle':
            d = abs(int(b2) - int(b1)) % 360
            out.append(Fraction(min(d, 360 - d)))        # the angle AOB inside the triangle
        elif w == 'ab':
            out.append(Approx(math.hypot(ax - bx, ay - by), ('dp', 2)))
        elif w == 'bearing_a_from_b':
            out.append(_bearing_pick(_bearing_of(ax - bx, ay - by)))
        elif w == 'bearing_b_from_a':
            out.append(_bearing_pick(_bearing_of(bx - ax, by - ay)))
        else:
            raise Cannot(f'unknown want {w!r}')
    return out


@solver('brg_triangulate')
def _brg_triangulate(sep, bearing_a, bearing_b):
    """B is due East of A. The ship is on bearing_a from A and bearing_b from B: find the distance AS."""
    ta, tb = math.tan(math.radians(_f(bearing_a))), math.tan(math.radians(_f(bearing_b)))
    if abs(ta - tb) < 1e-9:
        raise Cannot('parallel sight lines')
    north = _f(sep) / (ta - tb)           # E = N ta  and  E - sep = N tb
    east = north * ta
    if north <= 0:
        raise Cannot('ship is not north of the baseline')
    return [Approx(math.hypot(east, north), ('dp', 1))]


# ─────────────────────────────────────────────────────────────────────────────
# Multiple-choice procedural families
# ─────────────────────────────────────────────────────────────────────────────

@solver('mens_circle_area_314')
def _mens_circle_area_314(r):
    return [Approx(3.14 * _f(r) ** 2, ('dp', 1))]


@solver('brg_back_text')
def _brg_back_text(b):
    return [f'{(int(b) + 180) % 360:03d}°']


@solver('brg_three_figure')
def _brg_three_figure(b):
    return [f'{int(b):03d}°']


def _rhs_value(text):
    """Value of '1/2', '√2/2', '√3', '30/180' or a whole number; None if unreadable."""
    t = text.strip().replace(' ', '')
    m = re.fullmatch(r'(\d+)/(\d+)', t)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = re.fullmatch(r'√(\d+)(?:/(\d+))?', t)
    if m:
        return math.sqrt(int(m.group(1))) / int(m.group(2) or 1)
    m = re.fullmatch(r'\d+(?:\.\d+)?', t)
    return float(t) if m else None


@solver('trig_exact_statement')
def _trig_exact_statement(angle):
    """Option text such as 'sin 30° = 1/2' is true for the recorded angle."""
    def test(text):
        m = re.fullmatch(r'\s*(sin|cos|tan)\s*(\d+)°\s*=\s*(.+?)\s*', text)
        if not m or int(m.group(2)) != int(angle):
            return False
        rhs = _rhs_value(m.group(3))
        return rhs is not None and abs(_trig_value(m.group(1), angle) - rhs) < 1e-9
    return [Pick(test, f'a true exact value for angle {angle}°')]
