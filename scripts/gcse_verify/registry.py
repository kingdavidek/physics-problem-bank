"""Solver registry: ``@solver('family')`` registers a function that recomputes an answer from recorded inputs."""
from __future__ import annotations

from fractions import Fraction

SOLVERS: dict = {}
NEEDS_PROBLEM: set = set()      # families whose solver also receives the generated problem as ``_p``
DIAGRAM_CHECKS: dict = {}       # family -> fn(inputs, question_html) -> [message]: the drawing must agree with the inputs


def solver(family, problem=False):
    """Register a solver. With ``problem=True`` it is called as ``fn(_p=problem_dict, **inputs)`` and returns
    Verdicts itself (used by the algebra families, which read the displayed maths and the key directly)."""
    def deco(fn):
        if family in SOLVERS:
            raise ValueError(f'duplicate solver {family}')
        SOLVERS[family] = fn
        if problem:
            NEEDS_PROBLEM.add(family)
        return fn
    return deco


def fr(x):
    """Exact Fraction of a recorded input (floats go through repr, so 0.1 means one tenth)."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, bool):
        raise TypeError('bool is not a number')
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(repr(x))
    return Fraction(str(x))


def diagram(family):
    """Register a diagram check: it reads the SVG the pupil sees and returns messages where it disagrees
    with the inputs the generator recorded (so a drawing and its key cannot drift apart unnoticed)."""
    def deco(fn):
        if family in DIAGRAM_CHECKS:
            raise ValueError(f'duplicate diagram check {family}')
        DIAGRAM_CHECKS[family] = fn
        return fn
    return deco
