"""Solvers for vectors: column arithmetic, magnitudes, ratios and the vector-algebra proofs, recomputed exactly.

Independence rule: this module recomputes answers from first principles.  It must not import any generator
module or helper (checked by the test); only the standard library and the sibling verification modules.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from .core import Approx, Cannot, Pick, Surd, simplify_sqrt, sqrt_atom
from .latex import plain
from .registry import diagram, fr, solver
from .core import Verdict
from .solvers_loci import _step_texts, _steps_verdicts
from .solvers_svg import elements, one_svg, texts


def _pair(x, y):
    return [fr(x), fr(y)]


# ─────────────────────────────────────────────────────────────────────────────
# Column arithmetic
# ─────────────────────────────────────────────────────────────────────────────

@solver('vec_add')
def _vec_add(a0, a1, b0, b1):
    return _pair(fr(a0) + fr(b0), fr(a1) + fr(b1))


solver('vec_path_add')(_vec_add)                    # the same sum, with the triangle drawn


@solver('vec_sub')
def _vec_sub(a0, a1, b0, b1):
    return _pair(fr(a0) - fr(b0), fr(a1) - fr(b1))


@solver('vec_scale')
def _vec_scale(k, v0, v1):
    return _pair(fr(k) * fr(v0), fr(k) * fr(v1))


@solver('vec_position')
def _vec_position(x, y):
    return _pair(x, y)


@solver('vec_displacement')
def _vec_displacement(a0, a1, b0, b1):
    return _pair(fr(b0) - fr(a0), fr(b1) - fr(a1))


@solver('vec_midpoint')
def _vec_midpoint(a0, a1, b0, b1):
    return _pair((fr(a0) + fr(b0)) / 2, (fr(a1) + fr(b1)) / 2)


@solver('vec_translate')
def _vec_translate(p0, p1, v0, v1):
    return _pair(fr(p0) + fr(v0), fr(p1) + fr(v1))


@solver('vec_equation')
def _vec_equation(b0, b1, c0, c1):
    """2x + b = c."""
    return _pair((fr(c0) - fr(b0)) / 2, (fr(c1) - fr(b1)) / 2)


@solver('vec_sim')
def _vec_sim(s0, s1, d0, d1):
    """x + y = s and x - y = d."""
    s0, s1, d0, d1 = fr(s0), fr(s1), fr(d0), fr(d1)
    return [(s0 + d0) / 2, (s1 + d1) / 2, (s0 - d0) / 2, (s1 - d1) / 2]


@solver('vec_parallelogram', )
def _vec_parallelogram(ax, ay, bx, by, cx, cy):
    """ABCD a parallelogram: D = A + C - B."""
    return _pair(fr(ax) + fr(cx) - fr(bx), fr(ay) + fr(cy) - fr(by))


def _cross(a0, a1, b0, b1):
    return fr(a0) * fr(b1) - fr(a1) * fr(b0)


@solver('vec_parallel_yn')
def _vec_parallel_yn(a0, a1, b0, b1):
    return ['yes' if _cross(a0, a1, b0, b1) == 0 else 'no']


@solver('vec_equal_yn')
def _vec_equal_yn(a0, a1, b0, b1):
    return ['yes' if (fr(a0), fr(a1)) == (fr(b0), fr(b1)) else 'no']


@solver('vec_parallel_k')
def _vec_parallel_k(a0, a1, b0, b1):
    if _cross(a0, a1, b0, b1) != 0 or fr(a0) == 0:
        raise Cannot('b is not a multiple of a')
    return [fr(b0) / fr(a0)]


@solver('vec_parallel_t')
def _vec_parallel_t(a0, a1, b0):
    """(a0, a1) parallel to (b0, t)."""
    if fr(a0) == 0:
        raise Cannot('the top of a is zero')
    return [fr(b0) * fr(a1) / fr(a0)]


@solver('vec_collinear_yn')
def _vec_collinear_yn(px, py, qx, qy, rx, ry):
    cross = _cross(fr(qx) - fr(px), fr(qy) - fr(py), fr(rx) - fr(px), fr(ry) - fr(py))
    return ['yes' if cross == 0 else 'no']


@solver('vec_collinear')
def _vec_collinear(ax, ay, bx, by, cx, cy):
    ab = (fr(bx) - fr(ax), fr(by) - fr(ay))
    bc = (fr(cx) - fr(bx), fr(cy) - fr(by))
    if _cross(*ab, *bc) != 0:
        raise Cannot('the three points are not collinear')
    k = bc[0] / ab[0] if ab[0] != 0 else bc[1] / ab[1]

    def column(v):
        return Pick(lambda t, v=v: _column(t) == v, f'the column {v[0]}, {v[1]}')
    return [column(ab), column(bc), k]


def _column(text):
    m = re.fullmatch(r'\s*(-?\d+)\s*\|\s*(-?\d+)\s*', str(text))
    return (Fraction(int(m.group(1))), Fraction(int(m.group(2)))) if m else None


@solver('vec_cross_area')
def _vec_cross_area(a0, a1, b0, b1):
    area = abs(_cross(a0, a1, b0, b1))
    if area == 0:
        raise Cannot('the vectors are parallel, so there is no parallelogram')
    return [area]


# ─────────────────────────────────────────────────────────────────────────────
# Lengths
# ─────────────────────────────────────────────────────────────────────────────

def _length(sq):
    sq = fr(sq)
    if sq.denominator != 1:
        return sqrt_atom(sq)
    root = sqrt_atom(sq)
    if isinstance(root, Fraction):
        return root
    k, r = simplify_sqrt(int(sq))
    return Surd(k, r)


@solver('vec_magnitude')
def _vec_magnitude(x, y):
    return [_length(fr(x) ** 2 + fr(y) ** 2)]


@solver('vec_distance')
def _vec_distance(p0, p1, q0, q1):
    return [_length((fr(q0) - fr(p0)) ** 2 + (fr(q1) - fr(p1)) ** 2)]


@solver('vec_compare')
def _vec_compare(a0, a1, b0, b1):
    ma, mb = fr(a0) ** 2 + fr(a1) ** 2, fr(b0) ** 2 + fr(b1) ** 2
    if ma == mb:
        raise Cannot('the two vectors have the same magnitude, so "which is greater" has no answer')
    return ['a' if ma > mb else 'b']


@solver('vec_unit')
def _vec_unit(x, y):
    x, y = fr(x), fr(y)
    sq = x * x + y * y
    root = sqrt_atom(sq)
    if isinstance(root, Fraction):
        return [x / root, y / root]
    n = math.sqrt(float(sq))
    return [Approx(float(x) / n, ('dp', 3)), Approx(float(y) / n, ('dp', 3))]


# ─────────────────────────────────────────────────────────────────────────────
# Dividing a line
# ─────────────────────────────────────────────────────────────────────────────

@solver('vec_section')
def _vec_section(ax, ay, bx, by, m, n):
    """AP : PB = m : n, so P = A + m/(m+n) (B - A)."""
    m, n = fr(m), fr(n)
    t = m / (m + n)
    return _pair(fr(ax) + t * (fr(bx) - fr(ax)), fr(ay) + t * (fr(by) - fr(ay)))


@diagram('vec_section')
def _check_section(inputs, html):
    svg = one_svg(html)
    nums = sorted((x, t) for x, _y, t, _a in texts(svg) if re.fullmatch(r'\d+', t))
    out = []
    if [int(t) for _x, t in nums] != [int(fr(inputs['m'])), int(fr(inputs['n']))]:
        out.append(f'the line is labelled {[t for _x, t in nums]} but the ratio is {inputs["m"]}:{inputs["n"]}')
    dots = [c for c in elements(svg, 'circle')]
    if len(dots) != 3:
        return out + [f'expected three marked points, found {len(dots)}']
    ends = sorted(float(c['cx']) for c in dots if c.get('fill') != '#a13544')
    mark = [float(c['cx']) for c in dots if c.get('fill') == '#a13544']
    if len(ends) != 2 or len(mark) != 1:
        return out + ['cannot tell the end points from the marked point']
    frac = (mark[0] - ends[0]) / (ends[1] - ends[0])
    want = float(fr(inputs['m']) / (fr(inputs['m']) + fr(inputs['n'])))
    if abs(frac - want) > 0.012:
        out.append(f'P is drawn {frac:.3f} of the way from A to B but AP:PB = {inputs["m"]}:{inputs["n"]} needs {want:.3f}')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Vector algebra written with letters
# ─────────────────────────────────────────────────────────────────────────────

class _Lin(dict):
    """A linear combination of vectors: {'a': 1/2, 'b': 1/2}."""

    def scaled(self, k):
        return _Lin({n: c * k for n, c in self.items() if c * k != 0})

    def plus(self, other, sign=1):
        out = _Lin(self)
        for n, c in other.items():
            out[n] = out.get(n, Fraction(0)) + sign * c
            if out[n] == 0:
                del out[n]
        return out


def _tokens(text):
    return re.findall(r'\d+(?:\.\d+)?|[a-z]|[-+*/()]', plain(text).lower().replace('−', '-').replace(' ', ''))


def parse_lin(text):
    """Parse a letters-and-numbers expression such as '(a + b)/2' into a _Lin (or a plain Fraction number)."""
    toks = _tokens(text)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def mul(x, y):
        if isinstance(x, Fraction) and isinstance(y, Fraction):
            return x * y
        if isinstance(x, Fraction):
            return y.scaled(x)
        if isinstance(y, Fraction):
            return x.scaled(y)
        raise Cannot('a product of two vectors')

    def add(x, y, sign):
        if isinstance(x, Fraction) and isinstance(y, Fraction):
            return x + sign * y
        if isinstance(x, Fraction) or isinstance(y, Fraction):
            raise Cannot('a vector and a number are added')
        return x.plus(y, sign)

    def factor():
        t = take() if peek() is not None else None
        if t is None:
            raise Cannot(f'cannot read {text!r}')
        if t == '-':
            f = factor()
            return -f if isinstance(f, Fraction) else f.scaled(-1)
        if t == '(':
            v = expr()
            if peek() != ')':
                raise Cannot(f'missing bracket in {text!r}')
            take()
            return v
        if re.fullmatch(r'\d+(?:\.\d+)?', t):
            return Fraction(t)
        if re.fullmatch(r'[a-z]', t):
            return _Lin({t: Fraction(1)})
        raise Cannot(f'cannot read {text!r}')

    def term():
        v = factor()
        while peek() is not None and peek() not in '+-)':
            if peek() in ('*', '/'):
                op = take()
                w = factor()
                if op == '*':
                    v = mul(v, w)
                else:
                    if not isinstance(w, Fraction) or w == 0:
                        raise Cannot('division by a vector')
                    v = mul(v, 1 / w)
            else:                                    # implicit product such as 2b or 1/2 b
                v = mul(v, factor())
        return v

    def expr():
        v = term()
        while peek() in ('+', '-'):
            op = take()
            v = add(v, term(), 1 if op == '+' else -1)
        return v

    value = expr()
    if peek() is not None:
        raise Cannot(f'cannot read {text!r}')
    return value


def _is_lin(text, want):
    try:
        got = parse_lin(text)
    except Cannot:
        return False
    return isinstance(got, _Lin) and dict(got) == dict(want)


def _lin_pick(want, desc):
    return Pick(lambda t: _is_lin(t, want), desc)


@solver('vec_diag_proof')
def _vec_diag_proof():
    """ABCD with AB = a, AD = b: the midpoints of AC and BD from A are the same point, (a + b)/2."""
    a, b = _Lin({'a': Fraction(1)}), _Lin({'b': Fraction(1)})
    ac = a.plus(b)                                       # AC = AB + BC = a + b
    bd = b.plus(a, -1)                                   # BD = BA + AD = b - a
    mid_ac = ac.scaled(Fraction(1, 2))
    mid_bd = a.plus(bd.scaled(Fraction(1, 2)))           # AB + half of BD
    if dict(mid_ac) != dict(mid_bd):
        raise Cannot('the diagonals of a parallelogram must bisect each other')
    return [_lin_pick(mid_ac, 'the midpoint of AC from A'), _lin_pick(mid_bd, 'the midpoint of BD from A'), 'yes']


@solver('vec_tri_midpoint')
def _vec_tri_midpoint():
    """D, E the midpoints of AB, AC with AB = b, AC = c: DE = AE - AD = (c - b)/2."""
    b, c = _Lin({'b': Fraction(1)}), _Lin({'c': Fraction(1)})
    ad, ae = b.scaled(Fraction(1, 2)), c.scaled(Fraction(1, 2))
    de = ae.plus(ad, -1)
    return [_lin_pick(ad, 'AD'), _lin_pick(ae, 'AE'), _lin_pick(de, 'DE')]


@solver('vec_trapezium')
def _vec_trapezium(ratio):
    """AB parallel to DC in the same direction, AB = ratio x DC, so DC = (1/ratio) AB."""
    return [Fraction(1) / fr(ratio)]


@solver('vec_geometric_ratio')
def _vec_geometric_ratio(m, n, p, q):
    """AD : DB = m : n on AB (= b) and AE : EC = p : q on AC (= c): DE = AE - AD."""
    m, n, p, q = fr(m), fr(n), fr(p), fr(q)
    return [-m / (m + n), p / (p + q)]


def _read_triangle(svg):
    """(A, B, C, D, E) from the drawing: the triangle polygon and the two marked points."""
    polys = elements(svg, 'polygon')
    if not polys:
        raise Cannot('no triangle in the drawing')
    pts = [tuple(float(v) for v in pair.split(',')) for pair in polys[0]['points'].split()]
    if len(pts) != 3:
        raise Cannot('the polygon is not a triangle')
    dots = [(float(c['cx']), float(c['cy'])) for c in elements(svg, 'circle')]
    if len(dots) != 2:
        raise Cannot('expected two marked points D and E')
    return pts, dots


def _along(p, a, b):
    """How far p is from a towards b, as a fraction of ab (p must lie on the segment)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    off = math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))
    return t, off


def _check_de(svg, t_d, t_e):
    (a, b, c), dots = _read_triangle(svg)
    out = []
    lab = {t: (x, y) for x, y, t, _al in texts(svg)}
    if set(lab) != {'A', 'B', 'C', 'D', 'E'}:
        return [f'the drawing labels {sorted(lab)} instead of A, B, C, D, E']
    for name, want_t, end in (('D', t_d, b), ('E', t_e, c)):
        # the marked point nearest the label
        lx, ly = lab[name]
        dot = min(dots, key=lambda d: math.hypot(d[0] - lx, d[1] - ly))
        t, off = _along(dot, a, end)
        if off > 2.5:
            out.append(f'{name} is not on the side it should be on')
        elif abs(t - float(want_t)) > 0.015:
            out.append(f'{name} is drawn {t:.3f} of the way from A but should be {float(want_t):.3f}')
    return out


@diagram('vec_geometric_ratio')
def _check_geometric_ratio(inputs, html):
    m, n, p, q = (fr(inputs[k]) for k in ('m', 'n', 'p', 'q'))
    return _check_de(one_svg(html), m / (m + n), p / (p + q))


@diagram('vec_tri_midpoint')
def _check_tri_midpoint(inputs, html):
    return _check_de(one_svg(html), Fraction(1, 2), Fraction(1, 2))


@solver('vec_triangle_ineq', problem=True)
def _vec_triangle_ineq(_p=None, _records=None):
    return _steps_verdicts(_p, [
        r'^place a and b tip-to-tail so they form two sides of a triangle, with a \+ b as the third side',
        r'^in any triangle, each side length is at most the sum of the other two side lengths',
        r'^hence \|a \+ b\| ≤ \|a\| \+ \|b\|',
    ])


# ─────────────────────────────────────────────────────────────────────────────
# True or false statements about a column vector
# ─────────────────────────────────────────────────────────────────────────────

_MOVE = re.compile(r"(?:(\d+) units? (right|left))?(?: and )?(?:(\d+) units? (up|down))?")


@solver('vec_meaning', problem=True)
def _vec_meaning(_p=None, _records=None, x=None, y=None):
    x, y = fr(x), fr(y)

    def true_statement(t):
        t = plain(t).strip().lower()
        if t == 'the top number is the horizontal component.':
            return True
        if t == 'the bottom number is the vertical component.':
            return True
        m = re.fullmatch(r'it means move (.*)\.', t)
        if m:
            mv = _MOVE.fullmatch(m.group(1))
            if not mv or not m.group(1):
                return False
            dx = 0 if not mv.group(1) else int(mv.group(1)) * (1 if mv.group(2) == 'right' else -1)
            dy = 0 if not mv.group(3) else int(mv.group(3)) * (1 if mv.group(4) == 'up' else -1)
            return (dx, dy) == (x, y)
        return False
    keyed, others = _step_texts(_p)
    out = [Verdict(False, f'the key selects {t!r}, which is not true of the column ({x}, {y})')
           for t in keyed if not true_statement(t)]
    out += [Verdict(False, f'{t!r} is true of the column ({x}, {y}) but is not in the key')
            for t in others if true_statement(t)]
    return out or [Verdict(True)]


# ─────────────────────────────────────────────────────────────────────────────
# Parallelogram drawn on a grid with three vertices marked
# ─────────────────────────────────────────────────────────────────────────────

@diagram('vec_parallelogram')
def _check_parallelogram(inputs, html):
    svg = one_svg(html)
    xs, ys = [], []
    for x, y, t, anchor in texts(svg):
        if re.fullmatch(r'\d+', t):
            if anchor == 'middle' and abs(y - 244) <= 3:
                xs.append((x, int(t)))
            elif abs(x - 8) <= 2:
                ys.append((y - 3, int(t)))                  # the label sits 3px below its grid line
    if len(xs) < 11 or len(ys) < 11:
        return ['the grid is not labelled from 0 to 10 on both axes']
    xs.sort()
    ys.sort()
    top = max(v for _x, v in xs)
    if top < max(int(fr(inputs[k])) for k in ('ax', 'bx', 'cx')):
        return [f'the x axis stops at {top} but a vertex lies further out']
    if max(v for _y, v in ys) < max(int(fr(inputs[k])) for k in ('ay', 'by', 'cy')):
        return ['the y axis stops before the highest vertex']
    px_per_x = (xs[-1][0] - xs[0][0]) / (xs[-1][1] - xs[0][1])
    px_per_y = (ys[-1][0] - ys[0][0]) / (ys[-1][1] - ys[0][1])

    def data(cx, cy):
        return ((cx - xs[0][0]) / px_per_x + xs[0][1], (cy - ys[0][0]) / px_per_y + ys[0][1])

    marks = [data(float(c['cx']), float(c['cy'])) for c in elements(svg, 'circle')]
    want = [(fr(inputs['ax']), fr(inputs['ay'])), (fr(inputs['bx']), fr(inputs['by'])),
            (fr(inputs['cx']), fr(inputs['cy']))]
    out = []
    # D is the answer, so the drawing must not show it: no fourth point, no D label, no closed shape.
    if any(re.fullmatch(r'D\??', t) for _x, _y, t, _a in texts(svg)):
        out.append('the drawing labels D, which gives the answer away')
    if elements(svg, 'polygon'):
        out.append('the drawing closes the parallelogram, which shows where D is')
    if len(marks) != 3:
        return out + [f'expected three marked vertices (A, B, C), found {len(marks)}']
    for name, (wx, wy), (gx, gy) in zip('ABC', want, marks):
        if abs(gx - float(wx)) > 0.15 or abs(gy - float(wy)) > 0.15:
            out.append(f'{name} is drawn at ({gx:.2f}, {gy:.2f}) but the question gives ({float(wx):g}, {float(wy):g})')
    return out


@diagram('vec_path_add')
def _check_path_add(inputs, html):
    """The arrows AB, BC and AC must be drawn to one scale and match the column vectors."""
    svg = one_svg(html)
    lines = [(float(l['x1']), float(l['y1']), float(l['x2']), float(l['y2'])) for l in elements(svg, 'line')]
    if len(lines) != 3:
        return [f'expected three arrows, found {len(lines)}']
    ab, bc, ac = [(x2 - x1, y1 - y2) for x1, y1, x2, y2 in lines]          # screen y points down
    want = {'AB': (fr(inputs['a0']), fr(inputs['a1'])), 'BC': (fr(inputs['b0']), fr(inputs['b1']))}
    want['AC'] = (want['AB'][0] + want['BC'][0], want['AB'][1] + want['BC'][1])
    out = []
    comps = [(name, axis, got, float(want[name][i]))
             for name, drawn in (('AB', ab), ('BC', bc), ('AC', ac)) for i, (axis, got) in enumerate(zip(('across', 'up'), drawn))]
    big = max(comps, key=lambda c: abs(c[3]))
    scale = big[2] / big[3]                      # pixels per unit, from the longest component
    if scale <= 0:
        return [f'{big[0]} is drawn the wrong way round']
    for name, axis, got, exp in comps:
        if abs(got - scale * exp) > 2.5:
            out.append(f'{name} is drawn {got:.0f}px {axis} but the vectors need {scale * exp:.0f}px at this scale')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Multiple choice
# ─────────────────────────────────────────────────────────────────────────────

@solver('vec_add_options')
def _vec_add_options(ax, ay, bx, by):
    want = (fr(ax) + fr(bx), fr(ay) + fr(by))

    def test(text):
        m = re.fullmatch(r'\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*', plain(text).replace('−', '-'))
        return bool(m) and (Fraction(int(m.group(1))), Fraction(int(m.group(2)))) == want
    return [Pick(test, f'the column ({want[0]}, {want[1]})')]
