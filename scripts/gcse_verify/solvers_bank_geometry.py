"""Bank-item re-solvers: angles, transformations, circle theorems, similarity, loci (scale) and vectors.

Each entry is keyed by the item's digest and works the answer out from the numbers in the displayed question
(see ``solvers_bank``).  Where the item is about a transformation or a vector, the options are read as points or
columns and the transformation is applied to them, so a differently written but equal option is recognised.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

import sympy

from .core import Cannot
from .solvers_algebra_parse import tex_to_text
from .solvers_bank import add, exactish, pick, root, sx, val

CORNERS = {'triangle': 3, 'quadrilateral': 4, 'pentagon': 5, 'hexagon': 6, 'heptagon': 7, 'octagon': 8,
           'nonagon': 9, 'decagon': 10}


def F(x, y=1):
    return Fraction(x) / Fraction(y)


def polygon_sides(c):
    for name, k in CORNERS.items():
        if name in c.stem.lower():
            return k
    raise Cannot('no polygon named in the question')


def angle_in(c, label):
    """The value written after 'Angle <label> =' in the question."""
    m = re.search(rf'[Aa]ngle {label}\s*=\s*(\d+(?:\.\d+)?)°', c.stem)
    if not m:
        raise Cannot(f'angle {label} not found in {c.stem!r}')
    return F(m.group(1))


def triangle_coefficients(c):
    co = {}
    for name, k in re.findall(r'angle ([PQR]) = (\d*)x', c.stem):
        co[name] = int(k) if k else 1
    return co


def angles_in_ratio(c):
    co = triangle_coefficients(c)
    x = F(180, sum(co.values()))
    want = re.search(r'Find angle ([PQR])', c.stem).group(1)
    return [co[want] * x]


def angle_between(u, v):
    return math.degrees(math.acos((u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v))))


def straight_line_sum(c):
    """A ray from a point on a straight line splits the 180 degrees: the two angles it makes with the line add up."""
    sums = set()
    for th in (20, 65, 110, 157):
        ray = (math.cos(math.radians(th)), math.sin(math.radians(th)))
        sums.add(round(angle_between(ray, (1, 0)) + angle_between(ray, (-1, 0)), 9))
    if len(sums) != 1:
        raise Cannot('the two angles should always add to the same total')
    return [exactish(sums.pop())]


def semicircle_angle(c):
    """AB a diameter of the unit circle and C anywhere else on it: measure angle ACB."""
    a, b = (-1.0, 0.0), (1.0, 0.0)
    got = set()
    for th in (25, 70, 120, 200, 310):
        cc = (math.cos(math.radians(th)), math.sin(math.radians(th)))
        got.add(round(angle_between((a[0] - cc[0], a[1] - cc[1]), (b[0] - cc[0], b[1] - cc[1])), 9))
    if len(got) != 1:
        raise Cannot('angle in a semicircle should not change')
    return [exactish(got.pop())]


def tangent_radius_angle(c):
    """The tangent at A is the direction in which the line through A meets the unit circle nowhere else."""
    got = set()
    for alpha in (0, 33, 90, 147, 250):
        a = (math.cos(math.radians(alpha)), math.sin(math.radians(alpha)))
        for deg in range(360):
            d = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
            second_hit = -2 * (a[0] * d[0] + a[1] * d[1])           # |A + t d|^2 = 1 gives t = 0 or t = this value
            if abs(second_hit) < 1e-9:
                got.add(round(angle_between(a, d), 6))
    if len(got) != 1:
        raise Cannot('the tangent should be at one angle to the radius')
    return [exactish(got.pop())]


add('geometry_angles', {
    '20dcf8ce3fc5': straight_line_sum,
    '5b74d2770c35': semicircle_angle,
    'f36a5edd860f': tangent_radius_angle,
    'fdc85f5c9575': lambda c: [c.n[0]],                                             # alternate angles are equal
    'd1bef5fd01ed': lambda c: [F((polygon_sides(c) - 2) * 180)],                    # hexagon: interior angle sum
    'a88d92c681f6': lambda c: [F(360) / c.n[0]],                                    # regular polygon, exterior 30
    '9485e7ad5ed1': lambda c: [2 * c.n[0]],                                         # angle at the centre
    '55d5afabe4f3': lambda c: [180 - c.n[0]],                                       # cyclic quadrilateral
    'a7389c6c43d6': lambda c: [F(360) / (180 - c.n[0])],                            # interior 135: number of sides
    '7c3af4f11fcb': lambda c: [180 - c.n[0]],                                       # co-interior angles
    'e94d5de2ef65': lambda c: [(180 - c.n[0]) / 2],                                 # isosceles: base angle
    '433aa3f9537f': lambda c: [F(360, polygon_sides(c))],                           # exterior angle, regular polygon
    'd62df6091868': lambda c: [180 - (180 - c.n[0] - c.n[1])],                      # exterior = 180 - third angle
    '2f1455a843bf': angles_in_ratio,                                                # 3x + 2x + x = 180
    'a3deaf1cc4a4': lambda c: [180 - c.n[0]],                                       # tangents: angle AOB
})


# ───────────────────────────── transformations ─────────────────────────────

PAIR = re.compile(r'\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)')


def pair(t):
    m = PAIR.fullmatch(t.strip().replace('−', '-'))
    return (F(m.group(1)), F(m.group(2))) if m else None


def named_map(text):
    """A transformation written in words, as a function of a point (raises Cannot when it is not fully given)."""
    t = text.strip().lower().replace('−', '-')
    if t.startswith('reflection in the x-axis'):
        return lambda p: (p[0], -p[1])
    if t.startswith('reflection in the y-axis'):
        return lambda p: (-p[0], p[1])
    if t.startswith('reflection in y = x'):
        return lambda p: (p[1], p[0])
    if re.match(r'rotation 90° (cw|clockwise)', t):
        return lambda p: (p[1], -p[0])
    if re.match(r'rotation 90° (acw|anticlockwise|anti-clockwise)', t):
        return lambda p: (-p[1], p[0])
    if t.startswith('rotation 180°'):
        return lambda p: (-p[0], -p[1])
    m = re.match(r'translation by \(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', t)
    if m:
        dx, dy = F(m.group(1)), F(m.group(2))
        return lambda p: (p[0] + dx, p[1] + dy)
    m = re.match(r'enlargement \(scale factor (\d+)\)', t)
    if m:
        k = F(m.group(1))
        return lambda p: (k * p[0], k * p[1])
    raise Cannot(f'transformation not described fully enough: {text!r}')


def _exact_trig(deg):
    """(cos, sin) of a multiple of 90 degrees, exactly."""
    if deg % 90:
        raise Cannot(f'{deg} degrees is not a multiple of 90')
    return {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}[deg % 360]


def rotation(deg):
    """Rotation about the origin by ``deg`` degrees anticlockwise (negative for clockwise)."""
    co, si = _exact_trig(deg)
    return lambda p: (co * p[0] - si * p[1], si * p[0] + co * p[1])


def reflection(line_deg):
    """Reflection in the line through the origin at ``line_deg`` degrees to the x-axis."""
    co, si = _exact_trig(2 * line_deg) if (2 * line_deg) % 90 == 0 else (None, None)
    if co is None:
        raise Cannot('mirror line not at a multiple of 45 degrees')
    return lambda p: (co * p[0] + si * p[1], si * p[0] - co * p[1])


def stem_map(stem):
    """The transformation the question describes, built from its angle, direction or mirror line."""
    t = stem.lower().replace('−', '-')
    m = re.search(r'rotat\w* (?:of )?(\d+)°\s*(clockwise|anticlockwise|anti-clockwise)?\s*about the origin', t)
    if m:
        deg = int(m.group(1))
        if m.group(2) is None and deg != 180:
            raise Cannot('rotation direction not stated')
        return rotation(-deg if m.group(2) == 'clockwise' else deg)
    m = re.search(r'reflected in the (?:line )?(x-axis|y-axis|y = x|y = -x)', t)
    if m:
        return reflection({'x-axis': 0, 'y-axis': 90, 'y = x': 45, 'y = -x': 135}[m.group(1)])
    raise Cannot(f'no transformation read from {stem!r}')


def image_is(c):
    p = (c.n[0], c.n[1])
    want = stem_map(c.stem)(p)
    return pick(lambda t: pair(t) == want, f'the point {want}')


def maps_point(c):
    a, b, a2, b2 = [F(x) for x in re.findall(r'-?\d+', c.stem.replace('−', '-'))[:4]]
    return pick(lambda t: named_map(t)((a, b)) == (a2, b2), f'maps ({a}, {b}) to ({a2}, {b2})')


def not_length_preserving(c):
    def test(t):
        f = named_map(t)
        p, q = (F(0), F(0)), (F(3), F(4))
        a, b = f(p), f(q)
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 != 25
    return pick(test, 'changes the distance between two points')


def translation_statement(c):
    dx, dy = [int(x) for x in re.findall(r'pmatrix\s+(-?\d+)\s*\\+\s*(-?\d+)', c.stem)[0]]
    horizontal = ('left' if dx < 0 else 'right', abs(dx))
    vertical = ('up' if dy > 0 else 'down', abs(dy))

    def test(t):
        m = re.fullmatch(r'each point moves (\d+) (left|right) and (\d+) (up|down)', t.strip().lower())
        return bool(m) and (m.group(2), int(m.group(1))) == horizontal and (m.group(4), int(m.group(3))) == vertical
    return pick(test, f'each point moves {horizontal[1]} {horizontal[0]} and {vertical[1]} {vertical[0]}')


def generic_rotation(c):
    pts = [(2, 5), (-3, 4), (7, 1)]
    fn = stem_map(c.stem)
    want = [fn(p) for p in pts]

    def test(t):
        m = pair_expressions(t)
        a, b = sympy.symbols('a b')
        return all((m[0].subs({a: x, b: y}), m[1].subs({a: x, b: y})) == w for (x, y), w in zip(pts, want))
    return pick(test, f'(a, b) goes where the rotation takes it: {want}')


def pair_expressions(t):
    m = re.fullmatch(r'\(\s*(.+?)\s*,\s*(.+?)\s*\)', tex_to_text(t).strip())
    if not m:
        raise Cannot(f'not a pair of expressions: {t!r}')
    return sx(m.group(1)), sx(m.group(2))


def reflect_twice(c):
    first, second = re.search(r'reflected in the (x|y)-axis then in the (x|y)-axis', c.stem).groups()
    flips = {'x': lambda p: (p[0], -p[1]), 'y': lambda p: (-p[0], p[1])}
    pts = [(F(2), F(3)), (F(-1), F(5)), (F(4), F(-2))]
    return pick(lambda t: all(named_map(t)(p) == flips[second](flips[first](p)) for p in pts),
                'does what the two reflections do together')


def two_mirrors(c):
    gap = c.n[0]
    x = F(1)
    after_first = -x                                    # reflect in the line x = 0
    after_second = 2 * gap - after_first                # reflect in the line x = gap
    return [after_second - x]


add('transformations', {
    '67e074311bc1': image_is,                                                       # (3, 4) in the x-axis
    '26ae5054fad2': image_is,                                                       # (2, 5) in the y-axis
    'f4faf6e386cd': image_is,                                                       # 90 degrees clockwise
    'bc04425ff54f': maps_point,
    'a9368b1e8f04': image_is,                                                       # reflect in y = x
    '423b0a33bcbe': lambda c: [c.n[0] * c.n[1] ** 2],                               # area scales by k^2
    'c762b200bc6a': not_length_preserving,
    'ff6d24d02cbf': image_is,                                                       # 180 degrees about the origin
    '7bfbdbe99944': translation_statement,
    'befe5a41675b': lambda c: pick(lambda t: pair(t) == (c.n[0] * c.n[1], c.n[0] * c.n[2]),
                                   'the enlarged point'),                           # SF 3, P = (2, 1)
    '813cd1ba30ed': lambda c: pick(lambda t: pair(t) == (2 * c.n[2] - c.n[0], c.n[1]),
                                   'the reflection in x = 3'),
    '8e6eb7b34c18': generic_rotation,
    '50b8e2bc28ba': reflect_twice,
    '7bc1f614251e': two_mirrors,
    'd73086105df7': lambda c: [root(c.n[1] / c.n[0])],                              # area 12 to 108: scale factor
})


# ───────────────────────────── circle theorems ─────────────────────────────

def cyclic_unknown(c):
    """x from angle DAB + angle BCD = 180 with both written as expressions in x."""
    m = (re.search(r'[Aa]ngle DAB = \((.+?)\)° and angle BCD = \((.+?)\)°', c.stem)
         or re.search(r'[Aa]ngle DAB = ([^,]+),\s*angle BCD = ([^.]+)\.', c.stem))
    if not m:
        raise Cannot('angles DAB and BCD not found')
    x = sympy.Symbol('x')
    sols = sympy.solve(sx(m.group(1)) + sx(m.group(2)) - 180, x)
    if len(sols) != 1:
        raise Cannot('expected one value of x')
    return [F(int(sols[0].p), int(sols[0].q))]


def tangent_radius(c):
    return [root(c.n[1] ** 2 - c.n[0] ** 2)]


add('circle_theorems', {
    '0edc32b7cf96': semicircle_angle,
    '52adf49854d5': tangent_radius_angle,
    '688b44c90948': lambda c: [c.n[0] / 2],                                         # centre 80, circumference 40
    '8bcfab6327cb': lambda c: [180 - c.n[0]],                                       # cyclic quadrilateral
    'e2fdd3778a05': lambda c: [c.n[0]],                                             # same segment
    '5f5fc9064e38': lambda c: [180 - c.n[0]],                                       # two tangents: AOB
    'ebacfae4638b': lambda c: [c.n[0]],                                             # alternate segment
    '94333f236935': lambda c: [2 * c.n[0]],                                         # circumference to centre
    '0dd640d9742a': lambda c: [90 - c.n[0]],                                        # diameter: third angle
    '8fd1117984c9': tangent_radius,                                                 # PA = 12, OP = 13
    'f25cfcad386b': lambda c: [(180 - c.n[0]) / 2],                                 # isosceles OAB
    '8bbf3fab178f': lambda c: [c.n[0] / 2],                                         # reflex angle at the centre
    'c2811ec8b3ab': cyclic_unknown,
    '8f5dce770721': lambda c: [360 - 2 * c.n[0]],                                   # reflex AOB
    'b560aa784220': lambda c: [(c.n[0] + c.n[1]) / 2],                              # chords meeting inside
    '3f77f9f65490': lambda c: [c.n[0] / 2],
    '23dc59c3751d': lambda c: [180 - c.n[0]],
    'ad0d97311e62': lambda c: [c.n[0]],
    'a07fc1e39dde': lambda c: [180 - c.n[0] - c.n[1]],                              # ACB = 90 and BAC = 32
    '59d6a5c4a2db': lambda c: [180 - c.n[0]],
    '4c401761a980': lambda c: [c.n[0]],
    'b6fa71f644f6': lambda c: [2 * c.n[0]],
    'd13931e539a6': cyclic_unknown,
    '3be3e50b2e2e': lambda c: [(c.n[0] + c.n[1]) / 2],
})


# ───────────────────────────── similarity and scale ─────────────────────────────

def integer_root(n, k):
    n = Fraction(n)
    r = Fraction(round(float(n) ** (1 / k)))
    if r ** k != n:
        raise Cannot(f'{n} is not a perfect power')
    return r


def ratio_value(t, lead=True):
    m = re.match(r'\s*(\d+)\s*:\s*(\d+)', t) if lead else re.fullmatch(r'\s*(\d+)\s*:\s*(\d+)\s*', t)
    return F(m.group(1), m.group(2)) if m else None


def root_ratio(c, k):
    a, b = c.n[0], c.n[1]
    return pick(lambda t: ratio_value(t, lead=False) == integer_root(a, k) / integer_root(b, k),
                f'the ratio of the {k}th roots of {a} and {b}')


def map_km(c):
    """Actual length in km for a map scale 1 : N (N written with a space, as in 50 000) and a length in cm."""
    m = re.search(r'1 : (\d[\d ]*\d) \. ?|1 : (\d[\d ]*\d)\.', c.stem)
    scale = int(re.sub(r'\s', '', next(g for g in m.groups() if g)))
    length = Fraction(re.search(r'is (\d+(?:\.\d+)?) cm on the map', c.stem).group(1))
    return [length * scale / 100000]


def volume_scale_from_surface(c):
    linear_sq = c.n[1] / c.n[0]                          # area ratio = linear^2
    num, den = integer_root(linear_sq.numerator, 2), integer_root(linear_sq.denominator, 2)
    linear = num / den
    want = linear ** 3
    return pick(lambda t: ratio_value(t) == want, f'volume scale factor {want}')


def similar_triangle_angles(c):
    """Corresponding angles of a triangle and an enlarged, turned copy of it, compared four ways."""
    tri = ((0.0, 0.0), (5.0, 0.0), (1.0, 3.0))
    k, turn = 2.5, math.radians(30)
    copy = tuple((k * (x * math.cos(turn) - y * math.sin(turn)), k * (x * math.sin(turn) + y * math.cos(turn)))
                 for x, y in tri)

    def angles(t):
        out = []
        for i in range(3):
            p, q, r = t[i], t[(i + 1) % 3], t[(i + 2) % 3]
            out.append(angle_between((q[0] - p[0], q[1] - p[1]), (r[0] - p[0], r[1] - p[1])))
        return out
    a, b = angles(tri), angles(copy)
    relations = {
        'equal': lambda x, y: abs(x - y) < 1e-9, 'supplementary': lambda x, y: abs(x + y - 180) < 1e-9,
        'complementary': lambda x, y: abs(x + y - 90) < 1e-9, 'double': lambda x, y: abs(y - 2 * x) < 1e-9,
    }
    return pick(lambda t: all(relations[t.strip().lower()](x, y) for x, y in zip(a, b)),
                'true of every pair of corresponding angles')


def _angles_from_sides(a, b, c_):
    """The angles of the triangle with sides a, b, c (cosine rule), or None when no triangle has them."""
    out = []
    for x, y, z in ((a, b, c_), (b, c_, a), (c_, a, b)):
        k = (y * y + z * z - x * x) / (2 * y * z)
        if not -1 < k < 1:
            return None
        out.append(round(math.degrees(math.acos(k)), 9))
    return tuple(out)


def _ssa_triangles(a_, b_, angle_deg):
    """Non-congruent triangles with side a opposite angle A, and side b (the ambiguous case of the sine rule)."""
    angle = math.radians(angle_deg)
    s = b_ * math.sin(angle) / a_
    if not 0 < s <= 1:
        return 0
    sol = {round(math.asin(s), 12), round(math.pi - math.asin(s), 12)}
    return sum(1 for big_b in sol if angle + big_b < math.pi)


def _triangles_with_angles(angles):
    """Non-congruent triangles with the given angles: build one at each of two sizes and compare sides."""
    a, b, c_ = (math.radians(x) for x in angles)
    sides = {tuple(round(k * math.sin(t), 9) for t in (a, b, c_)) for k in (1.0, 2.0)}
    return len(sides)


def sufficient_for_congruence(c):
    """A set of conditions is enough when only one triangle (up to congruence) fits a case of it."""
    counts = {
        'sss (three equal sides)': lambda: 1 if _angles_from_sides(5.0, 7.0, 9.0) is not None else 0,
        'ssa (two sides and a non-included angle)': lambda: _ssa_triangles(5.0, 7.0, 40),
        'aaa (three equal angles)': lambda: _triangles_with_angles((40, 60, 80)),
        'two equal angles only': lambda: _triangles_with_angles((40, 60, 180 - 40 - 60)),
    }
    return pick(lambda t: counts[t.strip().lower()]() == 1, 'fixes the triangle completely')


def congruence_condition(c):
    """Right-angled triangles ABC (right angle at C) with equal hypotenuses AB and one equal leg CA.

    Each named condition lists what it needs; it applies when the given data supply that, and SSA is refused
    because it is not a congruence test in general (the ambiguous case gives two triangles).
    """
    angles = {'C': 90}
    sides = [('A', 'B'), ('C', 'A')]
    right = [v for v, a in angles.items() if a == 90]
    opposite = {frozenset('ABC') - {v} for v in right}
    has_hyp = any(frozenset(s_) in opposite for s_ in sides)
    shared = set(sides[0]) & set(sides[1])

    fits = {
        'rhs': lambda: bool(right) and has_hyp and len(sides) >= 2,
        'sas': lambda: len(sides) >= 2 and bool(shared & set(angles)),
        'aas': lambda: len(angles) >= 2,
        'ssa': lambda: len(sides) >= 2 and _ssa_triangles(5.0, 7.0, 40) == 1,
    }
    return pick(lambda t: fits[t.strip().lower()](), 'applies to the given data and fixes the triangle')


def vector_quantity(c):
    """A quantity is a vector when making the same journey the other way changes it (it has a direction)."""
    t = 2.0

    def quantities(d):
        size = math.hypot(*d)
        return {'speed': size / t, 'distance': size, 'time': t, 'velocity': (d[0] / t, d[1] / t)}
    there, back = quantities((3.0, 4.0)), quantities((-3.0, -4.0))
    return pick(lambda name: there[name.strip().lower()] != back[name.strip().lower()],
                'changes when the journey is reversed')


add('similarity_congruence', {
    '497512b19b51': congruence_condition,
    '95846da11cd7': similar_triangle_angles,
    '6ae9a944a425': sufficient_for_congruence,
    '9cdf54b285b2': lambda c: [c.n[0] ** 2],                                        # linear 3: area scale factor
    'e962d354fc23': lambda c: [c.n[2] * c.n[1] / c.n[0]],                           # ABC ~ PQR: QR
    '52e3b9218ae5': lambda c: pick(lambda t: ratio_value(t, lead=False) == integer_root(c.n[0], 2) / integer_root(c.n[1], 2),
                                   'smaller : larger lengths from areas 36 and 81'),
    'd15198809ada': lambda c: [c.n[0] ** 3],                                        # linear 4: volume scale factor
    '70dfee339b2c': lambda c: [c.n[2] * c.n[0] / c.n[1]],                           # DE parallel to BC
    '7a339c7e19cd': lambda c: pick(lambda t: val(t) == (c.n[1] / c.n[0]) ** 2,
                                   'area scale factor from perimeters'),
    '2c730122fd3e': lambda c: root_ratio(c, 3),                                     # volumes 27 and 64: radii
    'c73b59ce358e': lambda c: [c.n[0] * c.n[1] ** 2],                               # area 20, linear factor 4
    '3edbfbcf66fa': lambda c: pick(lambda t: ratio_value(t, lead=False) == integer_root(c.n[0], 3) / integer_root(c.n[1], 3),
                                   'linear scale factor from volumes 125 and 8'),
    '06a4f43b37b4': map_km,
    '0e569f447ac2': volume_scale_from_surface,
    '75c75c9d6929': lambda c: pick(lambda t: val(t) == c.n[2] * c.n[1] / c.n[0],    # AD = 3, DB = 5, AE = 4: EC
                                   'EC from similar triangles'),
})


# ───────────────────────────── loci (scale and measures) ─────────────────────────────

def midpoint_circle_radius(c):
    chord, radius = c.n[0], c.n[1]
    r = root(radius ** 2 - (chord / 2) ** 2)
    return pick(lambda t: (m := re.search(r'circle of radius (\d+(?:\.\d+)?) cm', t)) is not None
                and F(m.group(1)) == r, f'a circle of radius {r} cm')


def ladder_midpoint(c):
    r = c.n[0] / 2                                       # the midpoint of a ladder of length L is L / 2 from the corner
    return pick(lambda t: 'quarter-circle' in t and (m := re.search(r'radius (\d+(?:\.\d+)?) m', t)) is not None
                and F(m.group(1)) == r, f'a quarter-circle of radius {r} m')


SAMPLE_GRID = [(F(x, 2), F(y, 2)) for x in range(-8, 9) for y in range(-8, 9)]


def equal_distance_locus(c, ratio=(1, 1)):
    """The locus |PA| : |PB| = ratio for A = (-1, 0), B = (1, 0), compared with the shape each option names."""
    a, b = (F(-1), F(0)), (F(1), F(0))
    p_, q_ = ratio

    def d2(p, z):
        return (p[0] - z[0]) ** 2 + (p[1] - z[1]) ** 2
    shapes = {
        'the perpendicular bisector of ab': lambda p: p[0] == 0,
        'a circle with diameter ab': lambda p: p[0] ** 2 + p[1] ** 2 == 1,
        'the midpoint of ab only': lambda p: p == (0, 0),
        'a line parallel to ab': lambda p: p[1] == F(1, 2),
    }
    return pick(lambda t: all((d2(p, a) * q_ * q_ == d2(p, b) * p_ * p_) == shapes[t.strip().lower()](p)
                              for p in SAMPLE_GRID), 'the shape made of the points that are equally far from A and B')


def circle_about_point(c):
    r = c.n[0]
    return pick(lambda t: (m := re.fullmatch(r'a circle with centre p and radius (\d+(?:\.\d+)?) cm', t.strip().lower())) is not None
                and F(m.group(1)) == r, f'a circle with centre P and radius {r} cm')


def wheel_centre(c):
    """Roll a wheel of radius r along the road: its centre moves along y = r, a straight line."""
    r = c.n[0]
    centres = [(s, r) for s in range(0, 40)]
    if len({y for _, y in centres}) != 1:
        raise Cannot('the centre should stay at one height')
    return pick(lambda t: (m := re.fullmatch(r'a straight line (\d+(?:\.\d+)?) cm above the road', t.strip().lower())) is not None
                and F(m.group(1)) == r, f'a straight line {r} cm above the road')


def bisector_angle(c):
    """Angle between AB and its perpendicular bisector (the points equally far from A and B), for several AB."""
    angles = set()
    x, y = sympy.symbols('x y')
    for ax_, ay_, bx_, by_ in ((0, 0, 1, 0), (0, 0, 3, 1), (-2, 5, 6, -1), (4, 4, -7, 9)):
        # two points equally far from A and B: solve |PA|^2 = |PB|^2 at two values of the other coordinate
        eq = sympy.expand((x - ax_) ** 2 + (y - ay_) ** 2 - (x - bx_) ** 2 - (y - by_) ** 2)
        var, other = (x, y) if eq.coeff(x) != 0 else (y, x)
        p1 = {other: 0, var: sympy.solve(eq.subs(other, 0), var)[0]}
        p2 = {other: 1, var: sympy.solve(eq.subs(other, 1), var)[0]}
        u = (bx_ - ax_, by_ - ay_)
        v = (float(p2[x] - p1[x]), float(p2[y] - p1[y]))
        angles.add(round(math.degrees(math.acos((u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v)))), 9))
    if len(angles) != 1:
        raise Cannot('the angle should not depend on the length')
    return [exactish(angles.pop())]


def meet(p1, d1, p2, d2):
    """Where the line through p1 with direction d1 meets the line through p2 with direction d2."""
    det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
    if abs(det) < 1e-12:
        raise Cannot('parallel lines')
    t = ((p2[0] - p1[0]) * (-d2[1]) - (p2[1] - p1[1]) * (-d2[0])) / det
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def triangle_centres():
    a, b, c_ = (0.0, 0.0), (7.0, 0.0), (2.0, 5.0)

    def unit(p, q):
        d = (q[0] - p[0], q[1] - p[1])
        n = math.hypot(*d)
        return (d[0] / n, d[1] / n)

    def mid(p, q):
        return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)

    def perp(d):
        return (-d[1], d[0])
    circum = meet(mid(a, b), perp(unit(a, b)), mid(b, c_), perp(unit(b, c_)))
    bis_a = (unit(a, b)[0] + unit(a, c_)[0], unit(a, b)[1] + unit(a, c_)[1])
    bis_b = (unit(b, a)[0] + unit(b, c_)[0], unit(b, a)[1] + unit(b, c_)[1])
    incentre = meet(a, bis_a, b, bis_b)
    centroid = ((a[0] + b[0] + c_[0]) / 3, (a[1] + b[1] + c_[1]) / 3)
    orthocentre = meet(a, perp(unit(b, c_)), b, perp(unit(a, c_)))
    return (a, b, c_), {'perpendicular bisectors': circum, 'angle bisectors': incentre, 'centroid': centroid,
                        'median': centroid, 'altitudes': orthocentre}


def distance_to_line(p, q, r):
    return abs((r[0] - q[0]) * (q[1] - p[1]) - (q[0] - p[0]) * (r[1] - q[1])) / math.hypot(r[0] - q[0], r[1] - q[1])


def circle_construction(equal_to):
    """The method whose meeting point is the same distance from all three vertices ('vertices') or sides ('sides')."""
    def spec(c):
        (a, b, c_), points = triangle_centres()

        def test(t):
            low = t.lower()
            key = next(k for k in ('perpendicular bisectors', 'angle bisectors', 'centroid', 'median', 'altitudes') if k in low)
            pt = points[key]
            if equal_to == 'vertices':
                ds = [math.hypot(pt[0] - v[0], pt[1] - v[1]) for v in (a, b, c_)]
            else:
                ds = [distance_to_line(pt, a, b), distance_to_line(pt, b, c_), distance_to_line(pt, c_, a)]
            return max(ds) - min(ds) < 1e-9
        return pick(test, f'gives a point the same distance from all three {equal_to}')
    return spec


add('constructions_loci', {
    'e084d2fc883a': circle_construction('vertices'),
    'ceaab716098a': circle_construction('sides'),
    '852f2a72edd4': equal_distance_locus,
    '0316bc38607f': lambda c: equal_distance_locus(c, (int(c.n[0]), int(c.n[1]))),   # PA : PB = 1 : 1
    '44e393f99df9': circle_about_point,
    '487c7828b397': wheel_centre,
    'f3f3040bb606': bisector_angle,
    '39fe133be803': lambda c: [c.n[2] * c.n[1] / c.n[0] / 100],                     # 1 : 500, 3.6 cm: metres
    '1b50d0522e9d': midpoint_circle_radius,
    '21cf0d9d5c1e': ladder_midpoint,
})


# ───────────────────────────── vectors ─────────────────────────────

def columns(stem):
    return [(F(a), F(b)) for a, b in re.findall(r'pmatrix\s+(-?\d+)\s*\\+\s*(-?\d+)', stem)]


def column_answer(fn):
    def spec(c):
        want = fn(columns(c.stem), c)
        return pick(lambda t: pair(t) == want, f'the column {want}')
    return spec


def direction_words(c):
    (dx, dy), = columns(c.stem)

    def words(t):
        m = re.fullmatch(r'(?:move )?(\d+) (left|right)(?:,| and) (\d+) (up|down)', t.strip().lower())
        if not m:
            raise Cannot(f'cannot read {t!r}')
        return (int(m.group(1)) * (1 if m.group(2) == 'right' else -1),
                int(m.group(3)) * (1 if m.group(4) == 'up' else -1))
    return pick(lambda t: words(t) == (dx, dy), f'{dx} across and {dy} up')


def scale_by(cols, c):
    k = F(re.search(r'what is (-?\d*)\\mathbf a', c.stem).group(1))
    return (k * cols[0][0], k * cols[0][1])


def has_unit_length(t):
    p = pair(t)
    return p is not None and p[0] ** 2 + p[1] ** 2 == 1


def parallel_to_given(c):
    (a, b), = columns(c.stem)
    return pick(lambda t: (p := pair(t)) is not None and p != (0, 0) and a * p[1] - b * p[0] == 0,
                f'a multiple of ({a}, {b})')


def combination_of_a_and_b(cols, c):
    """The column for k a + m b (or k a - m b) read from the question; a coefficient left out means 1."""
    m = re.search(r'find\s*(-?\d*)\\mathbf a\s*([+-])\s*(\d*)\\mathbf b', c.stem)
    if not m or len(cols) != 2:
        raise Cannot(f'cannot read the combination in {c.stem!r}')
    k = F(-1 if m.group(1) == '-' else (m.group(1) or 1))
    j = F(m.group(3) or 1) * (1 if m.group(2) == '+' else -1)
    return (k * cols[0][0] + j * cols[1][0], k * cols[0][1] + j * cols[1][1])


def length_between_position_vectors(c):
    """|XY| from the position vectors OX and OY given in the question: the length of OY - OX."""
    pos = {n: (F(a), F(b)) for n, a, b in re.findall(r'overrightarrow (\w+) = \\begin pmatrix\s+(-?\d+)\s*\\+\s*(-?\d+)', c.stem)}
    m = re.search(r'length of \\overrightarrow (\w)(\w)', c.stem)
    if not m or f'O{m.group(1)}' not in pos or f'O{m.group(2)}' not in pos:
        raise Cannot(f'cannot find the position vectors in {c.stem!r}')
    (x1, y1), (x2, y2) = pos[f'O{m.group(1)}'], pos[f'O{m.group(2)}']
    return [exactish(math.hypot(float(x2 - x1), float(y2 - y1)))]


add('vectors', {
    'f7e71d7f3dca': column_answer(combination_of_a_and_b),                          # find 2a + b
    '9f796f86ce94': length_between_position_vectors,                                # |PQ| from OP and OQ
    '496ad8a7cb8d': vector_quantity,
    'db018bc947bc': direction_words,
    'a412248e9b27': column_answer(lambda cols, c: (cols[0][0] + cols[1][0], cols[0][1] + cols[1][1])),
    'c6b92481c9bd': column_answer(scale_by),
    'cf34ab60b0f7': lambda c: [exactish(math.hypot(*[float(v) for v in columns(c.stem)[0]]))],
    '9c2be257122c': parallel_to_given,
    '49b5236d46d8': direction_words,
    'cfdc4a0e232d': column_answer(lambda cols, c: (cols[0][0] - cols[1][0], cols[0][1] - cols[1][1])),
    '962e484f56e3': lambda c: [exactish(math.hypot(*[float(v) for v in columns(c.stem)[0]]))],
    '410188067c8e': lambda c: pick(has_unit_length, 'has length 1'),
})
