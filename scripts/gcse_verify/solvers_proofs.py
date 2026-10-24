"""Solver for the worded, ordered proofs (Phase 4): a model of each proof checked against the problem.

A proof slot asks the pupil to put sentences in order.  There is nothing numeric to recompute, so this module
holds an independent model of each of the seven proofs and checks four things:

* every keyed step says what step k of that proof must say (patterns, with the numbers taken from the question);
* no other step in the bank reads as a correct step (a distractor must be wrong);
* the steps that depend on each other are the ones the model says (the problem's ``answer_step_prereqs``, or a
  strict chain when it has none, compared as dependent pairs so that a harmless re-listing of a prerequisite is
  not flagged but a loosened order is);
* the theorem itself is true: it is tried on random coordinates, and the numbers a step states (such as
  half of 80 degrees) must be the ones the geometry gives.

Independence rule: this module recomputes from first principles.  It must not import any generator module or
helper (checked by the test); only the standard library and the sibling verification modules.
"""
from __future__ import annotations

import math
import re

from .core import Cannot, Verdict
from .latex import plain
from .registry import solver
from .solvers_loci import _step_texts, _steps_verdicts


class _Rng:
    """A small deterministic generator (a linear congruential sequence), so the same proof is always tried on the same points."""

    def __init__(self, seed):
        self.state = (sum((i + 1) * ord(c) for i, c in enumerate(seed)) or 1)

    def uniform(self, lo, hi):
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return lo + (hi - lo) * ((self.state >> 11) / (1 << 53))


def _q(_p):
    return re.sub(r'\s+', ' ', plain(str(_p.get('question', ''))).replace('−', '-')).strip().lower()


def _num_after(q, pattern):
    m = re.search(pattern, q)
    if not m:
        raise Cannot(f'{pattern!r} not found in the question')
    return int(m.group(1))


# ─────────────────────────────────────────────────────────────────────────────
# Dependencies
# ─────────────────────────────────────────────────────────────────────────────

def _closure(needs):
    """Dependent pairs (i, j), i < j, from direct prerequisites by 1-based position."""
    reach = {}
    for j in sorted(needs):
        reach[j] = set()
        for i in needs[j]:
            reach[j] |= {i} | reach[i]
    return {(i, j) for j, r in reach.items() for i in r}


def _problem_needs(_p):
    """The problem's prerequisites by 1-based position of the keyed steps (a chain when it carries none)."""
    ids = str(_p.get('correct_answer_raw')).split('|')[1:]
    spec = _p.get('answer_step_prereqs')
    if not spec:
        return {k + 1: ((k,) if k else ()) for k in range(len(ids))}
    pos = {x: k + 1 for k, x in enumerate(ids)}
    try:
        return {pos[s]: tuple(pos[n] for n in needs) for s, needs in spec.items()}
    except KeyError as e:
        raise Cannot(f'answer_step_prereqs names {e} which is not a keyed step')


def _dependency_verdicts(_p, model):
    got, want = _closure(_problem_needs(_p)), _closure(model)
    out = []
    for i, j in sorted(want - got):
        out.append(Verdict(False, f'step {j} depends on step {i} but the problem lets a pupil put it first'))
    for i, j in sorted(got - want):
        out.append(Verdict(False, f'the problem insists step {i} comes before step {j}, which the proof does not need'))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Geometry by coordinates
# ─────────────────────────────────────────────────────────────────────────────

def _d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _ang(p, v, r):
    """Angle at v between p and r, in degrees."""
    a1 = math.atan2(p[1] - v[1], p[0] - v[0])
    a2 = math.atan2(r[1] - v[1], r[0] - v[0])
    x = abs(a1 - a2) % (2 * math.pi)
    return math.degrees(min(x, 2 * math.pi - x))


def _close(a, b, tol=1e-7):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def _triangle(rng):
    while True:
        pts = [(rng.uniform(-9, 9), rng.uniform(-9, 9)) for _ in range(3)]
        (ax, ay), (bx, by), (cx, cy) = pts
        if abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) > 10:
            return pts


def _lerp(p, q, t):
    return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))


def _truth_aa(rng):
    A, B, C = _triangle(rng)
    t = rng.uniform(0.2, 0.8)
    D, E = _lerp(A, B, t), _lerp(A, C, t)
    ok = _close(_ang(A, D, E), _ang(A, B, C)) and _close(_ang(D, A, E), _ang(B, A, C))   # corresponding; common
    ok = ok and _close(_d(D, E) / _d(B, C), t)
    return ok, 'with DE parallel to BC, angle ADE equals angle ABC, angle A is shared and the triangles are similar'


def _truth_midpoint(rng):
    A, B, C = _triangle(rng)
    D, E = _lerp(A, B, .5), _lerp(A, C, .5)
    cross = (E[0] - D[0]) * (C[1] - B[1]) - (E[1] - D[1]) * (C[0] - B[0])
    ok = _close(_d(A, D) / _d(A, B), .5) and _close(_d(A, E) / _d(A, C), .5)
    ok = ok and _close(_ang(A, D, E), _ang(A, B, C)) and abs(cross) < 1e-7 and _close(_d(D, E), _d(B, C) / 2)
    return ok, 'the midpoint theorem (DE parallel to BC and half as long)'


def _truth_isosceles(rng):
    b, h = rng.uniform(1, 9), rng.uniform(1, 9)
    A, B, C, M = (0, h), (-b, 0), (b, 0), (0, 0)
    ok = _close(_d(A, B), _d(A, C)) and _close(_d(B, M), _d(M, C)) and _close(_d(A, M), _d(A, M))
    ok = ok and _close(_d(A, B), _d(A, C)) and _close(_ang(B, A, M), _ang(C, A, M))     # the triangles do match
    return ok, 'in an isosceles triangle the median splits it into two congruent triangles'


def _truth_parallelogram(rng):
    A, B, C = _triangle(rng)
    D = (A[0] + C[0] - B[0], A[1] + C[1] - B[1])
    ok = _close(_d(A, B), _d(C, D)) and _close(_d(B, C), _d(D, A)) and _close(_d(A, C), _d(C, A))
    ok = ok and _close(_ang(A, B, C), _ang(C, D, A))
    return ok, 'in a parallelogram the diagonal makes two congruent triangles'


def _truth_centre(rng, angle):
    th = math.radians(angle)
    phi = rng.uniform(th + .1, 2 * math.pi - .1)
    O, A, B, C = (0, 0), (1, 0), (math.cos(th), math.sin(th)), (math.cos(phi), math.sin(phi))
    return (_close(_ang(A, O, B), angle) and _close(_ang(A, C, B), angle / 2),
            f'the angle at the centre is twice the angle at the circumference (AOB = {angle})')


def _truth_alt_segment(rng, angle):
    th = math.radians(angle)
    O, A = (0, 0), (1, 0)
    B = (math.cos(2 * th), math.sin(2 * th))
    T = (1, 1)                                                      # on the tangent at A, on B's side
    phi = rng.uniform(2 * th + .1, 2 * math.pi - .1)
    C = (math.cos(phi), math.sin(phi))
    ok = _close(_ang(T, A, B), angle) and _close(_ang(O, A, B), 90 - angle) and _close(_ang(A, O, B), 2 * angle)
    ok = ok and _close(_ang(A, C, B), angle) and _close(_ang(O, A, T), 90)
    return ok, f'the alternate segment theorem (TAB = {angle})'


def _truth_cyclic(rng, a):
    """A cyclic quadrilateral with DAB = a has BCD = 180 - a, and the circle is the only one through A, B, D."""
    th = math.radians(a)
    e = rng.uniform(.1, .9) * (2 * math.pi - 2 * th)
    # arc BD not containing A is 2a; place A at angle 0, B at -(pi... use inscribed angle: DAB = half arc BCD
    B = (math.cos(0.5), math.sin(0.5))
    D = (math.cos(0.5 + 2 * th), math.sin(0.5 + 2 * th))
    A = (math.cos(0.5 + 2 * th + e), math.sin(0.5 + 2 * th + e))          # on the other arc
    C = (math.cos(0.5 + th), math.sin(0.5 + th))                          # on arc BD, between B and D
    return _close(_ang(D, A, B), a) and _close(_ang(B, C, D), 180 - a), \
        f'opposite angles of a cyclic quadrilateral sum to 180 (DAB = {a})'


def _truth_locus(rng):
    A, B = (rng.uniform(-9, 9), rng.uniform(-9, 9)), (rng.uniform(-9, 9), rng.uniform(-9, 9))
    if _d(A, B) < 1:
        B = (A[0] + 3, A[1] + 1)
    M = _lerp(A, B, .5)
    ux, uy = (B[0] - A[0]) / _d(A, B), (B[1] - A[1]) / _d(A, B)
    s = rng.uniform(-8, 8)
    P = (M[0] - uy * s, M[1] + ux * s)                                      # on the perpendicular bisector
    ok = _close(_d(P, A), _d(P, B))
    foot = (A[0] + ux * ((P[0] - A[0]) * ux + (P[1] - A[1]) * uy), A[1] + uy * ((P[0] - A[0]) * ux + (P[1] - A[1]) * uy))
    ok = ok and _close(_d(foot, M), 0.0, 1e-7) and _close(_d(A, foot), _d(B, foot)) and _close(_ang(P, M, A), 90)
    return ok, 'points equidistant from A and B are on the perpendicular bisector of AB'


# ─────────────────────────────────────────────────────────────────────────────
# The seven proofs
# ─────────────────────────────────────────────────────────────────────────────

def _spec(proof, q):
    """(step patterns, direct prerequisites by position, truth check, question pattern) of ``proof``."""
    if proof == 'aa_parallel':
        return ([r'^de is parallel to bc \(de ∥ bc\)\.$',
                 r'^angle ade = angle abc \(corresponding angles\)\.$',
                 r'^angle a is common to both triangles ade and abc\.$',
                 r'^triangle ade ~ triangle abc by aa similarity\.$'],
                {1: (), 2: (1,), 3: (), 4: (2, 3)}, _truth_aa,
                r'^in triangle abc, d lies on ab and e lies on ac such that de is parallel to bc\. prove that triangle ade is similar to triangle abc\.$')
    if proof == 'midpoint':
        return ([r'^since d and e are midpoints, ad = ½ab and ae = ½ac\.$',
                 r'^therefore ad/ab = ae/ac = 1/2\.$',
                 r'^angle a is common to both triangles ade and abc\.$',
                 r'^triangle ade ~ triangle abc by sas similarity \(scale factor 1/2\)\.$',
                 r'^corresponding angles are equal, so angle ade = angle abc, hence de ∥ bc\.$',
                 r'^since the scale factor is 1/2, de = ½bc\.$'],
                {1: (), 2: (1,), 3: (), 4: (2, 3), 5: (4,), 6: (4,)}, _truth_midpoint,
                r'^triangle abc has d and e as the midpoints of ab and ac respectively\. prove that triangle ade is similar to triangle abc, and hence show that de ∥ bc and de = ½bc\.')
    if proof == 'congruence_isosceles':
        return ([r'^ab = ac \(given: triangle abc is isosceles\)\.$',
                 r'^bm = mc \(m is the midpoint of bc\)\.$',
                 r'^am = am \(common side\)\.$',
                 r'^triangle abm ≅ triangle acm by sss\.$'],
                {1: (), 2: (), 3: (), 4: (1, 2, 3)}, _truth_isosceles,
                r'^triangle abc is isosceles with ab = ac\. m is the midpoint of bc\. prove that triangles abm and acm are congruent\.$')
    if proof == 'congruence_parallelogram':
        return ([r'^ab = cd \(opposite sides of a parallelogram\)\.$',
                 r'^bc = da \(opposite sides of a parallelogram\)\.$',
                 r'^ac = ca \(common diagonal\)\.$',
                 r'^triangle abc ≅ triangle cda by sss\.$'],
                {1: (), 2: (), 3: (), 4: (1, 2, 3)}, _truth_parallelogram,
                r'^abcd is a parallelogram\. prove that triangles abc and cda are congruent\.$')
    if proof == 'centre_angle':
        ac = _num_after(q, r'angle aob = (\d+)°')
        ai = ac // 2 if ac % 2 == 0 else re.escape(f'{ac / 2:g}')      # half of an odd angle is not a whole number
        return ([r'^join oa, ob and oc\. these are radii, so oa = ob = oc\.$',
                 r'^triangle oac is isosceles \(oa = oc\)\. let angle oca = α\.$',
                 r'^triangle obc is isosceles \(ob = oc\)\. let angle ocb = β\.$',
                 r'^angle acb = angle oca \+ angle ocb = α \+ β\.$',
                 r'^angle aob = 2α \+ 2β = 2\(α \+ β\) = 2 × angle acb \(ct1\)\.$',
                 rf'^therefore angle acb = ½ × angle aob = ½ × {ac}° = {ai}°\.$'],
                {1: (), 2: (1,), 3: (1,), 4: (2, 3), 5: (4,), 6: (5,)}, lambda rng: _truth_centre(rng, ac),
                rf'prove that angle acb = {ai}° by putting')
    if proof == 'alt_segment':
        ang = _num_after(q, r'angle tab = (\d+)°')
        oab = 90 - ang
        return ([r'^draw radius oa\.$',
                 rf'^oa is perpendicular to the tangent at a \(ct5\), so angle oab = 90° - {ang}° = {oab}°\.$',
                 rf'^oa = ob \(both radii\), so triangle oab is isosceles and angle oba = {oab}°\.$',
                 rf'^angle aob = 180° - 2 × {oab}° = {2 * ang}°\.$',
                 rf'^by ct1, angle acb = ½ × angle aob = ½ × {2 * ang}° = {ang}°, so angle acb = angle tab\.$'],
                {1: (), 2: (1,), 3: (2,), 4: (3,), 5: (4,)}, lambda rng: _truth_alt_segment(rng, ang),
                rf'prove that angle acb = {ang}° by putting')
    if proof == 'cyclic_converse':
        a = _num_after(q, r'angle dab = (\d+)°')
        c = 180 - a
        return ([r'^angle dab and angle bcd are opposite angles in quadrilateral abcd\.$',
                 rf'^angle dab \+ angle bcd = {a}° \+ {c}° = 180°\.$',
                 r'^if opposite angles of a quadrilateral sum to 180°, the quadrilateral is cyclic \(converse of ct4\)\.$',
                 r'^since opposite angles dab and bcd sum to 180°, abcd is a cyclic quadrilateral\.$'],
                {1: (), 2: (), 3: (), 4: (1, 2, 3)}, lambda rng: _truth_cyclic(rng, a),
                rf'angle bcd = {c}°\. prove that abcd is a cyclic quadrilateral')
    if proof == 'locus_equidistant':
        return ([r'^let m be the midpoint of ab\.$',
                 r'^if p lies on the perpendicular bisector of ab, then pm ⊥ ab and am = bm\.$',
                 r'^in triangles pam and pbm: pm is common, am = bm, and angle pma = angle pmb = 90°\.$',
                 r'^by sas congruence, △pam ≅ △pbm, so pa = pb\.$',
                 r'^suppose pa = pb, and let p′ be the foot of the perpendicular from p to ab\.$',
                 r'^by rhs, △pap′ ≅ △pbp′, so ap′ = bp′\.$',
                 r'^therefore p′ coincides with m, so p lies on the perpendicular bisector of ab\.$'],
                {1: (), 2: (1,), 3: (2,), 4: (3,), 5: (), 6: (5,), 7: (1, 6)}, _truth_locus,
                r'^prove that the locus of all points equidistant from a and b is the perpendicular bisector of ab\.$')
    raise Cannot(f'unknown proof {proof!r}')


@solver('proof_model', problem=True)
def _proof_model(_p=None, _records=None, proof=None):
    q = _q(_p)
    patterns, model, truth, asked = _spec(proof, q)
    out = []
    if not re.search(asked, q):
        out.append(Verdict(False, f'the question does not ask for the {proof} proof this key proves'))
    keyed, _ = _step_texts(_p)
    if len(keyed) != len(patterns):
        out.append(Verdict(False, f'the key has {len(keyed)} steps but the {proof} proof has {len(patterns)}'))
    else:
        out += [v for v in _steps_verdicts(_p, patterns) if not v.ok]
    out += _dependency_verdicts(_p, model)
    rng = _Rng(f'proof:{proof}:{q}')
    for _ in range(25):
        ok, what = truth(rng)
        if not ok:
            out.append(Verdict(False, f'the geometry does not bear out the proof: {what}'))
            break
    return out or [Verdict(True)]
