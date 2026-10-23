"""Solvers for transformations: images of shapes, "describe fully" options, centres, and the word questions.

Independence rule: this module recomputes answers from first principles.  It must not import any generator
module or helper (checked by the test); only the standard library and the sibling verification modules.

Every transformation here is a small function on a point (a pair of Fractions).  The same functions build the
image of a shape and test whether an answer option ("Rotation 90 degrees clockwise, centre (1,2)") really
sends the shape to its image, so a keyed option is checked by what it does and not by how it is worded.
"""
from __future__ import annotations

import re
from fractions import Fraction

from .core import Cannot, Pick, norm_text, sqrt_atom
from .registry import fr, solver

SAMPLE = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)),
          (Fraction(2), Fraction(3)), (Fraction(-3), Fraction(5))]


# ─────────────────────────────────────────────────────────────────────────────
# The transformations
# ─────────────────────────────────────────────────────────────────────────────

def translate(dx, dy):
    dx, dy = fr(dx), fr(dy)
    return lambda p: (p[0] + dx, p[1] + dy)


def reflect(a, b, c):
    """Reflection in the line a x + b y = c."""
    a, b, c = fr(a), fr(b), fr(c)
    if a == 0 and b == 0:
        raise Cannot('not a line')

    def f(p):
        d = (a * p[0] + b * p[1] - c) / (a * a + b * b)
        return (p[0] - 2 * d * a, p[1] - 2 * d * b)
    return f


def rotate_cw(quarters, cx=0, cy=0):
    """Rotation through ``quarters`` quarter-turns clockwise about (cx, cy)."""
    cx, cy = fr(cx), fr(cy)
    n = int(quarters) % 4

    def f(p):
        x, y = p[0] - cx, p[1] - cy
        for _ in range(n):
            x, y = y, -x
        return (cx + x, cy + y)
    return f


def enlarge(k, cx=0, cy=0):
    k, cx, cy = fr(k), fr(cx), fr(cy)
    return lambda p: (cx + k * (p[0] - cx), cy + k * (p[1] - cy))


def compose(*fs):
    def f(p):
        for g in fs:
            p = g(p)
        return p
    return f


def _compact(text):
    return re.sub(r'\s+', '', str(text).replace('−', '-').replace('−', '-')).lower()


def line_from_text(text):
    """(a, b, c) for a mirror line written as 'x-axis', 'y = x', 'y = -x + 1', 'x = 3', 'y = 2'."""
    s = _compact(text)
    s = re.sub(r'^(?:the)?(?:line)?', '', s)
    if s == 'x-axis':
        return (0, 1, 0)
    if s == 'y-axis':
        return (1, 0, 0)
    m = re.fullmatch(r'x=(-?\d+)', s)
    if m:
        return (1, 0, int(m.group(1)))
    m = re.fullmatch(r'y=(-?\d+)', s)
    if m:
        return (0, 1, int(m.group(1)))
    m = re.fullmatch(r'y=x([+-]\d+)?', s)
    if m:
        return (-1, 1, int(m.group(1) or 0))          # y - x = c
    m = re.fullmatch(r'y=-x([+-]\d+)?', s)
    if m:
        return (1, 1, int(m.group(1) or 0))           # x + y = c
    raise Cannot(f'cannot read the mirror line {text!r}')


_VECTOR = re.compile(r'pmatrix\s*(-?\d+)\s*\\*\s*(-?\d+)|vector\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)')
_CENTRE = re.compile(r'centre\s*\(?\s*(-?\d+)\s*,\s*(-?\d+)\s*\)?')


def _centre_of(text):
    m = _CENTRE.search(text)
    if m:
        return int(m.group(1)), int(m.group(2))
    if 'origin' in text:
        return 0, 0
    raise Cannot(f'no centre in {text!r}')


def parse_transform(text):
    """A function for the transformation an answer option describes, or None if it is not one."""
    t = str(text).replace('−', '-').replace('−', '-').lower()
    t = re.sub(r'\s+', ' ', t)
    try:
        if t.startswith('translation'):
            m = _VECTOR.search(t)
            if not m:
                return None
            dx, dy = (m.group(1), m.group(2)) if m.group(1) is not None else (m.group(3), m.group(4))
            return translate(int(dx), int(dy))
        if t.startswith('reflection in'):
            return reflect(*line_from_text(t[len('reflection in'):]))
        if t.startswith('rotation'):
            m = re.search(r'(\d+)\s*°', t)
            if not m or int(m.group(1)) % 90:
                return None
            quarters = int(m.group(1)) // 90
            if 'anticlockwise' in t or 'anti-clockwise' in t or 'counter' in t:
                quarters = -quarters
            cx, cy = _centre_of(t)
            return rotate_cw(quarters, cx, cy)
        if t.startswith('enlargement'):
            m = re.search(r'scale factor\s*(-?\d+(?:\.\d+)?(?:\s*/\s*\d+)?)', t)
            if not m:
                return None
            k = Fraction(m.group(1).replace(' ', ''))
            cx, cy = _centre_of(t)
            return enlarge(k, cx, cy)
    except Cannot:
        return None
    return None


def _pairs(pts, img):
    pts, img = _points(pts), _points(img)
    if len(pts) != len(img) or len(pts) < 2:
        raise Cannot('need matching lists of points')
    return list(zip(pts, img))


def _points(flat):
    vals = [fr(c) for v in flat for c in (v if isinstance(v, (list, tuple)) else (v,))]
    if len(vals) % 2:
        raise Cannot('coordinates must come in pairs')
    pts = [(vals[i], vals[i + 1]) for i in range(0, len(vals), 2)]
    if len(pts) == 3:
        (x1, y1), (x2, y2), (x3, y3) = pts
        if (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1) == 0:
            raise Cannot(f'the three vertices {pts} do not make a triangle')
    return pts


def _flat(points):
    return [c for p in points for c in p]


def _maps_all(text, pairs):
    f = parse_transform(text)
    return f is not None and all(f(p) == q for p, q in pairs)


def _maps_like(text, truth):
    """The option is a transformation that moves a spread of sample points exactly as ``truth`` does."""
    f = parse_transform(text)
    return f is not None and all(f(p) == truth(p) for p in SAMPLE)


# ─────────────────────────────────────────────────────────────────────────────
# Applying a named transformation to a triangle
# ─────────────────────────────────────────────────────────────────────────────

def _turn(word):
    m = re.match(r'\s*(\d+)\s*°\s*(clockwise|anticlockwise)?', str(word))
    if not m or int(m.group(1)) % 90:
        raise Cannot(f'cannot read the turn {word!r}')
    q = int(m.group(1)) // 90
    if m.group(2) == 'anticlockwise':
        q = -q
    elif m.group(2) is None and q != 2:
        raise Cannot(f'the turn {word!r} has no direction')
    return q


@solver('trans_apply')
def _trans_apply(pts, kind, dx=0, dy=0, line_word=None, turn_word=None, k=None, k_num=None, k_den=None,
                 cx=0, cy=0, c=0):
    if kind == 'translate':
        f = translate(dx, dy)
    elif kind == 'reflect':
        f = reflect(*line_from_text(line_word))
    elif kind == 'rotate':
        f = rotate_cw(_turn(turn_word), cx, cy)
    elif kind == 'enlarge':
        scale = fr(k) if k is not None else fr(k_num) / fr(k_den)
        f = enlarge(scale, cx, cy)
    else:
        raise Cannot(f'unknown transformation {kind!r}')
    return _flat(f(p) for p in _points(pts))


@solver('trans_chain')
def _trans_chain(pts, dx, dy, ref_word, turn_word):
    f = compose(translate(dx, dy), reflect(*line_from_text(ref_word)), rotate_cw(_turn(turn_word)))
    return _flat(f(p) for p in _points(pts))


@solver('trans_reverse')
def _trans_reverse(pts, dx, dy):
    f = translate(-fr(dx), -fr(dy))
    return _flat(f(p) for p in _points(pts))


@solver('trans_describe')
def _trans_describe(pts, img):
    pairs = _pairs(pts, img)
    return [Pick(lambda t: _maps_all(t, pairs), 'a single transformation that sends every vertex to its image')]


@solver('trans_double')
def _trans_double(pts, first_word, second_word):
    f1 = reflect(*line_from_text(first_word))
    f2 = reflect(*line_from_text(second_word))
    points = _points(pts)
    step1 = [f1(p) for p in points]
    step2 = [f2(p) for p in step1]
    both = compose(f1, f2)
    return _flat(step1) + _flat(step2) + [Pick(lambda t: _maps_like(t, both),
                                                'the single transformation equal to both reflections')]


@solver('trans_refl_chain')
def _trans_refl_chain(px, py, k):
    both = compose(reflect(0, 1, 0), reflect(0, 1, fr(k)))
    x, y = both((fr(px), fr(py)))
    return [x, y, Pick(lambda t: _maps_like(t, both), 'the single transformation equal to both reflections')]


@solver('trans_enlarge_centre')
def _trans_enlarge_centre(pts, img):
    pairs = _pairs(pts, img)
    (p0, q0), (p1, q1) = pairs[0], pairs[1]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ex, ey = q1[0] - q0[0], q1[1] - q0[1]
    if dx != 0:
        k = ex / dx
    elif dy != 0:
        k = ey / dy
    else:
        raise Cannot('two vertices coincide')
    if k == 1:
        raise Cannot('a scale factor of 1 has no single centre')
    cx = (q0[0] - k * p0[0]) / (1 - k)
    cy = (q0[1] - k * p0[1]) / (1 - k)
    f = enlarge(k, cx, cy)
    if any(f(p) != q for p, q in pairs):
        raise Cannot('the image is not an enlargement of the shape')
    return [k, cx, cy]


@solver('trans_rot_centre')
def _trans_rot_centre(pts, img, turn_word):
    pairs = _pairs(pts, img)
    quarters = _turn(turn_word)
    if quarters % 4 not in (1, 3):
        raise Cannot('only quarter turns are solved here')
    (x, y), (u, v) = pairs[0]
    if quarters % 4 == 1:       # clockwise: u = cx - cy + y, v = cx + cy - x
        cx, cy = (u + v + x - y) / 2, (y + x - u + v) / 2
    else:                       # anticlockwise: u = cx + cy - y, v = cy - cx + x
        cx, cy = (u - v + y + x) / 2, (u + v + y - x) / 2
    f = rotate_cw(quarters, cx, cy)
    if any(f(p) != q for p, q in pairs):
        raise Cannot('the image is not a rotation of the shape')
    return [cx, cy]


# ─────────────────────────────────────────────────────────────────────────────
# Algebraic coordinates
# ─────────────────────────────────────────────────────────────────────────────

def parse_linear(text):
    """{variable: coefficient, '': constant} for a linear expression such as '-3n-2', or None."""
    s = _compact(text).replace('(', '').replace(')', '')
    if not s:
        return None
    out = {}
    for term in re.findall(r'[+-]?[^+-]+', s):
        m = re.fullmatch(r'([+-]?)(\d*)([a-z]?)', term)
        if not m or not (m.group(2) or m.group(3)):
            return None
        coef = Fraction(m.group(2) or 1) * (-1 if m.group(1) == '-' else 1)
        key = m.group(3)
        out[key] = out.get(key, 0) + coef
    return {k: v for k, v in out.items() if v != 0}


def _lin(**terms):
    return {('' if k == 'one' else k): Fraction(v) for k, v in terms.items() if v != 0}


def _lin_pick(expect, desc):
    return Pick(lambda t: parse_linear(t) == expect, desc)


@solver('trans_alg')
def _trans_alg(kind, var='n', a=0, b=0, c=0, dx=0, dy=0):
    a, b, c, dx, dy = fr(a), fr(b), fr(c), fr(dx), fr(dy)
    if kind == 'rot90cw':           # (p, q) -> (q, -p)
        out = [_lin(q=1), _lin(p=-1)]
    elif kind == 'rot90acw':        # (p, q) -> (-q, p)
        out = [_lin(q=-1), _lin(p=1)]
    elif kind == 'rot180':          # (a p, b q) -> (-a p, -b q)
        out = [_lin(p=-a), _lin(q=-b)]
    elif kind == 'ref_xaxis':       # (a v, b v + c) -> (a v, -b v - c)
        out = [{var: a}, {var: -b, '': -c}]
    elif kind == 'ref_yaxis':       # (a v, v + c) -> (-a v, v + c)
        out = [{var: -a}, {var: Fraction(1), '': c}]
    elif kind == 'ref_yx':          # (a v + b, c v) -> (c v, a v + b)
        out = [{var: c}, {var: a, '': b}]
    elif kind == 'trans':           # (v + b, a v - c) + (dx, dy)
        out = [{var: Fraction(1), '': b + dx}, {var: a, '': dy - c}]
    else:
        raise Cannot(f'unknown algebraic transformation {kind!r}')
    return [_lin_pick({k: v for k, v in e.items() if v != 0}, 'an expression equal to the image coordinate')
            for e in out]


# ─────────────────────────────────────────────────────────────────────────────
# Word questions
# ─────────────────────────────────────────────────────────────────────────────

@solver('trans_identify')
def _trans_identify(desc_word):
    t = norm_text(desc_word)
    if re.search(r'\bmoves\b|\bshifts\b|\bslides\b', t):
        return ['translation']
    if re.search(r'flipped|mirror', t):
        return ['reflection']
    if re.search(r'\bturns\b|\brotated\b', t):
        return ['rotation']
    if re.search(r'multiplied|scaled|enlarged', t):
        return ['enlargement']
    raise Cannot(f'cannot classify {desc_word!r}')


@solver('trans_cs')
def _trans_cs(t1_word, k1, t2_word, k2, t3_word, k3, t4_word, k4):
    """Congruent / similar but not congruent, for four transformations (k is the scale factor, 0 if none)."""
    out = []
    for word, k in ((t1_word, k1), (t2_word, k2), (t3_word, k3), (t4_word, k4)):
        w = str(word).lower()
        if w in ('rotation', 'reflection', 'translation'):
            same = True
        elif w == 'enlargement':
            same = abs(fr(k)) == 1
        else:
            raise Cannot(f'unknown transformation {word!r}')
        want = 'congruent' if same else 'similar but not congruent'
        out.append(Pick(lambda t, want=want: norm_text(t) == want, want))
    return out


def _says(*needles):
    wanted = [n.lower() for n in needles]
    return lambda text: all(n in norm_text(text) for n in wanted)


@solver('trans_invariant_refl')
def _trans_invariant_refl(axis_word):
    if axis_word == 'x-axis':
        letter, f = 'b', reflect(0, 1, 0)
    elif axis_word == 'y-axis':
        letter, f = 'a', reflect(1, 0, 0)
    else:
        raise Cannot(f'unknown axis {axis_word!r}')

    def deduce(text):
        return _compact(text) == f'{letter}=0'

    def example(text):
        m = re.fullmatch(r'\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*', str(text).replace('−', '-'))
        return bool(m) and f((Fraction(m.group(1)), Fraction(m.group(2)))) == (Fraction(m.group(1)),
                                                                                  Fraction(m.group(2)))
    return [Pick(deduce, f'{letter} = 0'), Pick(example, 'a point that the reflection leaves where it is')]


@solver('trans_invariant_rot')
def _trans_invariant_rot(topic):
    if topic != 'rotation 180':
        raise Cannot(f'unknown topic {topic!r}')

    def image(text):
        return _compact(text).replace('(', '').replace(')', '') == '-a,-b'
    return [Pick(image, 'the point (-a, -b)'), 'origin', Pick(_says('centre of rotation'), 'the centre of rotation')]


@solver('trans_self_inverse')
def _trans_self_inverse(topic):
    if topic != 'self-inverse':
        raise Cannot(f'unknown topic {topic!r}')
    return [Pick(_says('twice', 'original position'), 'two reflections in the same line return a point'),
            Pick(lambda t: norm_text(t).startswith('no') and '180' in t, 'no: 90 degrees twice is 180 degrees'),
            Pick(lambda t: '180' in t and 'rotation' in norm_text(t), 'a half turn')]


@solver('sim_k_from_area')
def _sim_k_from_area(small, large):
    if fr(small) <= 0:
        raise Cannot('area must be positive')
    return [sqrt_atom(fr(large) / fr(small))]


# ─────────────────────────────────────────────────────────────────────────────
# Points in the multiple-choice functions
# ─────────────────────────────────────────────────────────────────────────────

def _point_is(x, y):
    def test(text):
        m = re.fullmatch(r'\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*', str(text).replace('−', '-'))
        return bool(m) and (Fraction(m.group(1)), Fraction(m.group(2))) == (fr(x), fr(y))
    return Pick(test, f'the point ({x}, {y})')


@solver('trans_translate_point')
def _trans_translate_point(px, py, dx, dy):
    x, y = translate(dx, dy)((fr(px), fr(py)))
    return [_point_is(x, y)]


@solver('trans_reflect_point')
def _trans_reflect_point(px, py, axis_word):
    x, y = reflect(*line_from_text(axis_word))((fr(px), fr(py)))
    return [_point_is(x, y)]
