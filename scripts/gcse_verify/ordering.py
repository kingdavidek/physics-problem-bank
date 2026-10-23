"""Independent model of ordered-proof answers: which orders are valid given each step's prerequisites.

Used by the verification test to check the accepted orders a problem carries (``answer_step_prereqs``).  It
shares no code with the checker: it enumerates the valid orders itself and the test compares the two.
"""
from __future__ import annotations

from itertools import permutations

MAX_ORDERS = 5000       # more than this many valid orders means the spec is too loose to be a proof


def is_valid_order(order, prereqs):
    """Every step of ``prereqs`` appears exactly once and after all of its prerequisites."""
    if sorted(order) != sorted(prereqs):
        return False
    where = {step: i for i, step in enumerate(order)}
    return all(where[need] < where[step] for step, needs in prereqs.items() for need in needs)


def linear_extensions(canonical, prereqs):
    """Every valid order of the steps, found by repeatedly placing a step whose prerequisites are all placed."""
    out = []

    def go(placed, left):
        if len(out) > MAX_ORDERS:
            return
        if not left:
            out.append(tuple(placed))
            return
        for step in left:
            if all(need in placed for need in prereqs[step]):
                go(placed + [step], [x for x in left if x != step])

    go([], list(canonical))
    return out


def dependent_pairs(canonical, prereqs):
    """Pairs (i, j) of 1-based canonical positions, i < j, where step j depends (directly or not) on step i."""
    reach = {step: set() for step in canonical}
    for step in canonical:                      # canonical order is a valid order, so prerequisites come first
        for need in prereqs[step]:
            reach[step] |= {need} | reach[need]
    pos = {step: i + 1 for i, step in enumerate(canonical)}
    return {(pos[need], pos[step]) for step in canonical for need in reach[step]}


def free_pairs(canonical, prereqs):
    """Pairs (i, j) of 1-based canonical positions, i < j, that are logically independent."""
    n = len(canonical)
    dep = dependent_pairs(canonical, prereqs)
    return {(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1) if (i, j) not in dep}


def all_permutations(canonical, limit=7):
    """Every ordering of the steps (small proofs only); None when the proof is too long to brute force."""
    return list(permutations(canonical)) if len(canonical) <= limit else None
