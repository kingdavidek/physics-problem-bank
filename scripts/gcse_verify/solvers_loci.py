"""Solvers for constructions and loci: numeric answers recomputed exactly, descriptions of a locus checked
against the geometry the question states, and construction steps checked against what each step must say.

Independence rule: this module recomputes answers from first principles.  It must not import any generator
module or helper (checked by the test); only the standard library and the sibling verification modules.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from .core import Approx, Cannot, Pick, PickSet, Verdict, sqrt_atom
from .latex import plain
from .registry import diagram, fr, solver
from .solvers_svg import one_svg, texts


def _t(text):
    """Lower-case, single-spaced, plain-minus text for matching."""
    return re.sub(r'\s+', ' ', plain(str(text)).replace('−', '-')).strip().lower()


def _num(x):
    """Text of a number as the question prints it: 5 for 5, 2.5 for 5/2."""
    x = fr(x)
    return str(x.numerator) if x.denominator == 1 else format(float(x), 'g')


# ─────────────────────────────────────────────────────────────────────────────
# "Describe the locus": each kind says what the right description must contain and what it must not
# ─────────────────────────────────────────────────────────────────────────────

def _is(expected):
    return lambda t: _t(t) == expected


def _locus_test(kind, i):
    """(predicate on the option text, description) for one describe-the-locus question."""
    def get(name):
        if name not in i:
            raise Cannot(f'loci kind {kind!r} needs {name}')
        return i[name]

    if kind == 'perp_bisector':
        return _is('the perpendicular bisector of ab'), 'the perpendicular bisector of AB'
    if kind == 'circle':
        r = _num(get('r'))
        return _is(f'a circle with centre p and radius {r} cm'), f'a circle, centre P, radius {r} cm'
    if kind == 'angle_bisectors':
        return _is('the two angle bisectors of the angles at b'), 'both angle bisectors at B'
    if kind == 'stadium':
        d = _num(get('d'))
        return (lambda t: 'stadium' in _t(t) and f'{d} cm away' in _t(t)
                and f'semicircles of radius {d} cm at a and b' in _t(t)), f'a stadium at distance {d} cm'
    if kind == 'angle_bisector_distance':
        return (lambda t: 'distance from ab equals the perpendicular distance from ac' in _t(t)
                ), 'the two perpendicular distances are equal'
    if kind == 'rolling_wheel':
        r, road = _num(get('r')), _t(get('surface_word'))
        return _is(f'a straight line parallel to the {road}, at height {r} cm'), f'a line {r} cm above the {road}'
    if kind == 'closer':
        return _is("all points on a's side of the perpendicular bisector of ab"), "A's side of the bisector"
    if kind == 'tools':
        return (lambda t: 'ruler' in _t(t) and 'compasses' in _t(t) and 'protractor' not in _t(t)
                and 'only' not in _t(t)), 'ruler and compasses, no protractor'
    if kind == 'rounded_rectangle':
        d = _num(get('d'))
        return (lambda t: _t(t).startswith('a rounded rectangle') and f'{d} cm out' in _t(t)
                and f'corners of radius {d} cm' in _t(t)), f'a rounded rectangle at distance {d} cm'
    if kind == 'angle_bisector_corner':
        return (lambda t: 'angle bisector of angle dab' in _t(t)), 'the bisector of angle DAB'
    if kind == 'combined':
        r = _num(get('r'))
        return (lambda t: _t(t).startswith(f'the part of the circle (centre a, radius {r} cm)')
                and "on b's side" in _t(t)), f"the part of circle A (radius {r}) on B's side"
    if kind == 'ladder':
        half = _num(fr(get('ladder')) / 2)
        return (lambda t: _t(t).startswith(f'a quarter-circle of radius {half} m centred at the corner')
                ), f'a quarter-circle of radius {half} m at the corner'
    if kind == 'semicircle':
        return (lambda t: _t(t).startswith('the full circle with diameter ab')), 'the full circle on diameter AB'
    if kind == 'quarter_circle':
        r = _num(get('r'))
        return _is(f'a quarter-circle of radius {r} m centred at corner a'), f'a quarter-circle of radius {r} m at A'
    if kind == 'constant_area':
        h = _num(2 * fr(get('area')) / fr(get('ab')))
        return (lambda t: _t(t).startswith(f'two straight lines parallel to ab, each {h} cm from ab')
                ), f'two parallel lines {h} cm from AB'
    if kind == 'circumcentre':
        return (lambda t: _t(t).startswith('the circumcentre') and 'perpendicular bisectors' in _t(t)
                ), 'the circumcentre'
    if kind == 'three_regions':
        b, m = _num(get('boundary')), _num(get('max_dist'))
        return (lambda t: _t(t).startswith('the intersection of all three regions')
                and f'above the line {b} m from pq' in _t(t)
                and "on p's side of the perpendicular bisector of pr" in _t(t)
                and f'inside the circle of radius {m} m centred at s' in _t(t)), 'the intersection of the three regions'
    raise Cannot(f'unknown locus kind {kind!r}')


def _feasible(length, width, boundary, reach):
    """Is there a point of the garden PQRS (P top-left, Q top-right, R bottom-right, S bottom-left) that is more
    than ``boundary`` from PQ, closer to P than to R, and within ``reach`` of S?  Checked on a fine grid."""
    length, width, boundary, reach = float(length), float(width), float(boundary), float(reach)
    steps = 40
    for i in range(steps + 1):
        x = length * i / steps
        for j in range(steps + 1):
            y = width * j / steps                          # y measured down from PQ
            if (y > boundary and x * x + y * y < (x - length) ** 2 + (y - width) ** 2
                    and x * x + (y - width) ** 2 <= reach * reach):
                return True
    return False


@solver('loci')
def _loci(kind, cond_word=None, **i):
    if kind == 'three_regions' and {'length', 'width'} <= set(i):
        if not _feasible(i['length'], i['width'], i['boundary'], i['max_dist']):
            raise Cannot('the three conditions have no point in common inside the garden')
    test, desc = _locus_test(kind, i)
    return [Pick(test, desc)]


@solver('loci_points')
def _loci_points(p_word, q_word, r_word):
    p, q, r = (str(w).lower() for w in (p_word, q_word, r_word))
    if len({p, q, r}) != 3:
        raise Cannot('the three points are not distinct')
    if {p, q, r} & {'a', 'b'}:
        raise Cannot('a point is named A or B, the ends of the segment itself')
    want = f'{p}a = {p}b and {q}a = {q}b, but {r}a ≠ {r}b'
    return [Pick(lambda t: _t(t) == want, want)]


def _lens_exists(d, r1, r2):
    d, r1, r2 = fr(d), fr(r1), fr(r2)
    return abs(r1 - r2) < d < r1 + r2


@solver('loci_lens')
def _loci_lens(d, r1, r2):
    if not _lens_exists(d, r1, r2):
        raise Cannot(f'circles of radius {r1} and {r2} with centres {d} apart do not cross, so there is no lens')
    return [Pick(lambda t: 'intersection' in _t(t) and 'lens' in _t(t), 'the lens where the two circles overlap')]


@solver('loci_overlap')
def _loci_overlap(d, r1, r2):
    """Two coverage circles, centres d apart: they overlap when the radii add to more than d.  Worked out here
    from the three numbers (never read from the key).  A clear margin is required: tangent circles or one circle
    inside the other would make the answer a matter of wording, so they are refused."""
    d, r1, r2 = fr(d), fr(r1), fr(r2)
    if abs(r1 - r2) >= d:
        raise Cannot('one coverage circle lies inside the other')
    if abs(d - (r1 + r2)) < 2:
        raise Cannot('the radii add to within 2 of the distance, so the answer is borderline (or the circles touch)')
    if r1 + r2 > d:
        return [Pick(lambda t: _t(t).startswith('yes') and 'lens' in _t(t) and 'sum of the radii exceeds' in _t(t),
                     'yes: they overlap in a lens because the radii add to more than the distance')]
    return [Pick(lambda t: _t(t).startswith('no') and 'do not overlap' in _t(t)
                 and 'sum of the radii is less than' in _t(t),
                 'no: they do not overlap because the radii add to less than the distance')]


@solver('loci_garden')
def _loci_garden(length, width, boundary, max_dist):
    if not _feasible(length, width, boundary, max_dist):
        raise Cannot('the three conditions have no point in common inside the garden')
    return _loci('three_regions', length=length, width=width, boundary=boundary, max_dist=max_dist)


@diagram('loci_garden')
def _check_garden(inputs, html):
    svg = one_svg(html)
    found = {}
    for _x, _y, text, _a in texts(svg):
        m = re.fullmatch(r'(PQ|QR) = (\d+) m', text)
        if m:
            found[m.group(1)] = int(m.group(2))
    out = []
    for name, key in (('PQ', 'length'), ('QR', 'width')):
        if name not in found:
            out.append(f'the diagram does not label {name}')
        elif fr(found[name]) != fr(inputs[key]):
            out.append(f'the diagram labels {name} = {found[name]} m but the question says {inputs[key]} m')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Counting and scale
# ─────────────────────────────────────────────────────────────────────────────

@solver('loci_circle_count')
def _loci_circle_count(d, r1, r2):
    d, r1, r2 = fr(d), fr(r1), fr(r2)
    if d > r1 + r2 or d < abs(r1 - r2):
        return [Fraction(0)]
    if d == r1 + r2 or d == abs(r1 - r2):
        return [Fraction(1)]
    return [Fraction(2)]


@solver('loci_scale_down')
def _loci_scale_down(scale, dist_km):
    return [fr(dist_km) * 100000 / fr(scale)]               # km to cm, then divide by the scale


@solver('loci_scale_area')
def _loci_scale_area(scale, map_cm2, unit_word):
    cm2 = fr(map_cm2) * fr(scale) ** 2
    unit = str(unit_word)
    if unit == 'cm²':
        return [cm2]
    if unit == 'km²':
        return [cm2 / 10 ** 10]
    if unit == 'm²':
        return [cm2 / 10 ** 4]
    raise Cannot(f'unknown area unit {unit_word!r}')


# ─────────────────────────────────────────────────────────────────────────────
# Algebraic and metric loci
# ─────────────────────────────────────────────────────────────────────────────

@solver('loci_chord_midpoint')
def _loci_chord_midpoint(radius, chord):
    R, half = fr(radius), fr(chord) / 2
    if half >= R:
        raise Cannot('the chord is longer than the diameter')
    return [sqrt_atom(R * R - half * half, ('dp', 1))]


@solver('loci_diff_squares')
def _loci_diff_squares(d, k):
    d = fr(d)
    return [(fr(k) + d * d) / (2 * d)]                      # (x^2) - (x - d)^2 = 2dx - d^2


@solver('loci_circumcentre')
def _loci_circumcentre(bx, cx, cy):
    bx, cx, cy = fr(bx), fr(cx), fr(cy)
    ox = bx / 2                                              # equidistant from A(0,0) and B(bx,0)
    oy = (cx * cx + cy * cy - 2 * ox * cx) / (2 * cy)        # OA^2 = OC^2
    return [ox, oy]


@solver('loci_incircle')
def _loci_incircle(a, b, c):
    a, b, c = fr(a), fr(b), fr(c)
    if a * a + b * b != c * c:
        raise Cannot('the sides are not a right-angled triangle')
    return [a * b / 2, (a * b / 2) / ((a + b + c) / 2)]


@solver('loci_tri_centres')
def _loci_tri_centres(a, b, c):
    a, b, c = fr(a), fr(b), fr(c)
    if a * a + b * b != c * c:
        raise Cannot('the sides are not a right-angled triangle')
    return [c / 2, (a * b / 2) / ((a + b + c) / 2)]


@solver('loci_sector')
def _loci_sector(angle, radius):
    return [Approx(float(fr(angle)) / 360 * math.pi * float(fr(radius)) ** 2)]


@solver('loci_apollonius', problem=True)
def _loci_apollonius(_p=None, _records=None, d=None, n=None, m=None):
    """PA : PB = n : m with A(0,0), B(d,0): m^2 PA^2 = n^2 PB^2 is a circle; the solution must state its centre and radius."""
    d, n, m = fr(d), fr(n), fr(m)
    if n == m:
        raise Cannot('equal ratio gives a line, not a circle')
    k = m * m - n * n
    cx = -n * n * d / k
    r = n * m * d / abs(k)
    text = _t(_p['solution'])
    got = re.search(r'circle with centre \((-?[\d.]+), 0\) and radius ([\d.]+) cm', text)
    if not got:
        raise Cannot('cannot find the stated centre and radius in the solution')
    gx, gr = fr(got.group(1)), fr(got.group(2))
    out = []
    for name, shown, exact in (('centre x', gx, cx), ('radius', gr, r)):
        if abs(shown - exact) > Fraction(1, 20) or (shown * 10).denominator != 1:
            out.append(Verdict(False, f'the solution gives {name} = {shown} but it is {float(exact):.4g}'))
    return out or [Verdict(True)]


# ─────────────────────────────────────────────────────────────────────────────
# Multi-part questions with a pick-three field
# ─────────────────────────────────────────────────────────────────────────────

def _pick_set(_p, index, predicate, count):
    """Test for a pick-N field inside number_fields: the keyed ids are exactly ``count`` statements that satisfy
    ``predicate`` and no other statement in the bank does."""
    bank = {str(b.get('id')): _t(b.get('text')) for b in ((_p.get('answer_field_options') or [])[index] or [])}

    def test(raw):
        ids = str(raw).split('|')[2:]
        if len(ids) != count or any(i not in bank for i in ids):
            return False
        if not all(predicate(bank[i]) for i in ids):
            return False
        return not any(predicate(t) for i, t in bank.items() if i not in ids)
    return test


@solver('loci_treasure', problem=True)
def _loci_treasure(_p=None, _records=None, r_c=None, unit_word=None):
    """Equidistant from A and B (perpendicular bisector) and r from C on that line: two points."""
    r, unit = _num(r_c), str(unit_word)

    def true_statement(t):
        return (t == 'condition (i) means the treasure must lie on the perpendicular bisector of ab.'
                or t == f'condition (ii) means the treasure lies on a circle of radius {r} {unit} centred at c.'
                or (t.startswith('since c lies on the perpendicular bisector, the circle crosses that line in two points')
                    and f'{r} {unit} above c and {r} {unit} below c' in t))
    return [Fraction(2), PickSet(_pick_set(_p, 1, true_statement, 3), 'the three true statements about the two loci')]


# ─────────────────────────────────────────────────────────────────────────────
# Construction steps: the keyed steps, in order, must each say the right thing, and no other step may
# ─────────────────────────────────────────────────────────────────────────────

def _steps_patterns(kind, i):
    def n(name):
        return _num(i[name]) if name in i else None

    if kind == 'perp_bisector':
        return [r'^open the compasses to more than half the length of ab',
                r'^place the compass point on a and draw an arc above and below ab',
                r'^without changing the radius, place the point on b and draw arcs above and below ab, crossing the first arcs',
                r'^join the two intersection points with a straight line']
    if kind == 'angle_bisector':
        return [r'^place the compass point on b and draw an arc that crosses both arms ba and bc',
                r'^label the crossings x \(on ba\) and y \(on bc\)',
                r'^place the compass on x and draw an arc inside the angle',
                r'^using the same radius, place the compass on y and draw an arc crossing the previous one',
                r'^draw the ray bz']
    if kind == 'equilateral':
        s = n('n')
        return [rf'^draw a line segment ab = {s} cm', rf'^set the compasses to {s} cm',
                r'^draw an arc from a \(above ab\)', r'^without changing the radius, draw an arc from b',
                r'^mark point c where the arcs intersect', r'^join a to c and b to c']
    if kind == 'perp_from_point':
        return [r'^place the compass point on p and draw an arc that crosses line l at two points',
                r'^open the compass to more than half of xy', r'^draw an arc from x below the line',
                r'^without changing radius, draw an arc from y below the line, crossing the previous arc at q',
                r'^draw the line pq']
    if kind == 'sss':
        pq, qr, pr = n('pq'), n('qr'), n('pr')
        return [rf'^draw pq = {pq} cm', rf'^set compasses to {pr} cm\. draw an arc centred at p',
                rf'^set compasses to {qr} cm\. draw an arc centred at q, crossing the previous arc at r',
                r'^join p to r and q to r']
    if kind == 'sixty':
        return [r'^set the compass to any radius r\. place the point on a and draw an arc crossing ab',
                r'^without changing r, place the compass on x and draw an arc crossing the first arc',
                r'^draw the ray ay']
    if kind == 'perp_at_point':
        return [r'^place the compass on p and draw two equal arcs along ab, crossing it at x and y',
                r'^open the compass wider', r'^draw arcs from x and y above the line, crossing each other at q',
                r'^draw the line pq']
    if kind == 'circumcircle':
        return [r'^construct the perpendicular bisector of side ab', r'^construct the perpendicular bisector of side bc',
                r'^label the intersection of the two bisectors o', r'^set the compass to oa and draw the circle centred at o']
    if kind == 'incircle':
        return [r'^construct the angle bisector of angle a', r'^construct the angle bisector of angle b',
                r'^label the intersection i \(the incentre\)',
                r'^construct a perpendicular from i to any side; its length is the inradius r',
                r'^draw the circle centred at i with radius r']
    if kind == 'hexagon':
        s = n('n')
        return [rf'^draw a circle of radius {s} cm', r'^mark any point a on the circle',
                rf'^without changing the compass \({s} cm\), step around the circle marking six points',
                r'^join consecutive points with straight lines']
    if kind == '45':
        return [r'^construct a 90° angle at point a on a line using the perpendicular-at-a-point method',
                r'^bisect the 90° angle using the angle bisector construction']
    if kind == '30':
        return [r'^construct a 60° angle using the equilateral triangle method',
                r'^bisect the 60° angle using the angle bisector construction']
    raise Cannot(f'unknown construction {kind!r}')


def _step_texts(_p):
    """(ordered keyed step texts, other bank step texts) of a proof_steps problem."""
    raw = str(_p.get('correct_answer_raw'))
    parts = raw.split('|')
    if not parts or parts[0] == 'pick':
        raise Cannot('this is not an ordered-steps key')
    bank = {str(b.get('id')): _t(b.get('text')) for b in (_p.get('answer_step_bank') or [])}
    ids = parts[1:]
    if not ids or any(x not in bank for x in ids):
        raise Cannot('the keyed step ids are not all in the bank')
    return [bank[x] for x in ids], [t for x, t in bank.items() if x not in ids]


def _steps_verdicts(_p, patterns):
    keyed, others = _step_texts(_p)
    out = []
    if len(keyed) != len(patterns):
        out.append(Verdict(False, f'the key lists {len(keyed)} steps but the construction needs {len(patterns)}'))
    else:
        for k, (text, pat) in enumerate(zip(keyed, patterns), 1):
            if not re.search(pat, text):
                out.append(Verdict(False, f'keyed step {k} {text!r} does not say what step {k} of this construction must say'))
    for text in others:
        if any(re.search(pat, text) for pat in patterns):
            out.append(Verdict(False, f'the extra step {text!r} also reads as a correct step'))
    return out or [Verdict(True)]


@solver('loci_steps', problem=True)
def _loci_steps(_p=None, _records=None, kind=None, **i):
    return _steps_verdicts(_p, _steps_patterns(kind, i))


@solver('loci_ellipse', problem=True)
def _loci_ellipse(_p=None, _records=None, ladder=None, dist=None):
    """Ladder of length L, P at distance ``dist`` from the foot: x = (L - dist) a / L, y = dist b / L,
    so x^2/(L - dist)^2 + y^2/dist^2 = 1."""
    L, dd = fr(ladder), fr(dist)
    if not 0 < dd < L:
        raise Cannot('P must be between the foot and the top of the ladder')
    sx = L - dd
    n = _num
    patterns = [
        rf'\(-a/{n(L)}, b/{n(L)}\)',
        rf'= \({n(sx)}a/{n(L)}, {n(dd)}b/{n(L)}\)',
        rf'a = {n(L)}x/{n(sx)} and b = {n(L)}y/{n(dd)}',
        rf'\({n(L)}x/{n(sx)}\)² \+ \({n(L)}y/{n(dd)}\)² = {n(L * L)}',
        rf'x²/{n(sx * sx)} \+ y²/{n(dd * dd)} = 1',
    ]
    return _steps_verdicts(_p, patterns)
