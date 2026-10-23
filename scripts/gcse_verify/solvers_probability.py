"""Solvers for probability: exact Fractions only, and the Venn and tree drawings checked against the inputs.

Independence rule: this module recomputes answers from first principles.  It must not import any generator
module or helper (checked by the test); only the standard library, sympy and the sibling verification modules.
"""
from __future__ import annotations

import itertools
import re
from fractions import Fraction

from .core import Cannot
from .registry import diagram, fr, solver
from .solvers_svg import one_svg, read_tree, read_venn2, read_venn3


def _frac(n, d):
    d = fr(d)
    if d == 0:
        raise Cannot('zero denominator')
    return fr(n) / d


def _prob(x):
    if x < 0 or x > 1:
        raise Cannot(f'a probability of {x} is impossible (the numbers in the question do not fit together)')
    return x


# ─────────────────────────────────────────────────────────────────────────────
# Single events
# ─────────────────────────────────────────────────────────────────────────────

_DIE_EVENTS = (
    (re.compile(r'a score of (\d)$'), lambda m: (lambda x: x == int(m.group(1)))),
    (re.compile(r'(?:an? )?even number$|a multiple of 2$'), lambda m: (lambda x: x % 2 == 0)),
    (re.compile(r'(?:an? )?odd number$'), lambda m: (lambda x: x % 2 == 1)),
    (re.compile(r'greater than (\d+)$'), lambda m: (lambda x: x > int(m.group(1)))),
    (re.compile(r'less than (\d+)$'), lambda m: (lambda x: x < int(m.group(1)))),
    (re.compile(r'at least (\d+)$'), lambda m: (lambda x: x >= int(m.group(1)))),
    (re.compile(r'at most (\d+)$'), lambda m: (lambda x: x <= int(m.group(1)))),
    (re.compile(r'(?:a )?factor of (\d+)$'), lambda m: (lambda x: int(m.group(1)) % x == 0)),
    (re.compile(r'(?:a )?prime number$'), lambda m: (lambda x: x in (2, 3, 5))),
    (re.compile(r'(?:a )?multiple of (\d+)$'), lambda m: (lambda x: x % int(m.group(1)) == 0)),
)


@solver('prob_die')
def _prob_die(event_word):
    text = str(event_word).strip().lower()
    for pattern, make in _DIE_EVENTS:
        m = pattern.match(text)
        if m:
            test = make(m)
            hits = [x for x in range(1, 7) if test(x)]
            if not hits:
                raise Cannot(f'no face of a die satisfies {event_word!r}')
            return [Fraction(len(hits), 6)]
    raise Cannot(f'cannot read the die event {event_word!r}')


@solver('prob_bag')
def _prob_bag(n_first, first_word, n_second, second_word, colour_word):
    names = [str(first_word).lower(), str(second_word).lower()]
    colour = str(colour_word).lower()
    if colour not in names or names[0] == names[1]:
        raise Cannot(f'colour {colour_word!r} is not one of {names}')
    count = fr(n_first) if colour == names[0] else fr(n_second)
    return [_frac(count, fr(n_first) + fr(n_second))]


@solver('prob_complement')
def _prob_complement(p):
    return [_prob(1 - fr(p))]


@solver('prob_expected')
def _prob_expected(a, b, n):
    return [_frac(a, b) * fr(n)]


@solver('prob_relative')
def _prob_relative(success, trials):
    return [_frac(success, trials)]


@solver('prob_die_or')
def _prob_die_or(a, b):
    if int(a) == int(b) or not (1 <= int(a) <= 6 and 1 <= int(b) <= 6):
        raise Cannot('two different faces of a die are needed')
    return [Fraction(2, 6)]


@solver('prob_coins')
def _prob_coins(n, style_word, r=None):
    n = int(n)
    outcomes = list(itertools.product((0, 1), repeat=n))
    style = str(style_word)
    if style == 'exactly':
        hits = [o for o in outcomes if sum(o) == int(r)]
    elif style == 'at least':
        hits = [o for o in outcomes if sum(o) >= int(r)]
    elif style == 'same':
        hits = [o for o in outcomes if len(set(o)) == 1]
    else:
        raise Cannot(f'unknown coin event {style!r}')
    return [Fraction(len(hits), len(outcomes))]


@solver('prob_at_least_one')
def _prob_at_least_one(p_fail, attempts):
    return [_prob(1 - fr(p_fail) ** int(attempts))]


@solver('prob_conditional')
def _prob_conditional(pa_n, pa_d, pab_n, pab_d):
    pa, pab = _frac(pa_n, pa_d), _frac(pab_n, pab_d)
    if pab > pa:
        raise Cannot('P(A and B) cannot exceed P(A)')
    return [_prob(pab / pa)]


@solver('prob_independent')
def _prob_independent(a, b, c, d):
    return [_prob(_frac(a, b) * _frac(c, d))]


@solver('prob_union')
def _prob_union(total, a, b, both):
    if fr(both) > min(fr(a), fr(b)):
        raise Cannot('the overlap is larger than one of the groups')
    return [_prob(_frac(fr(a) + fr(b) - fr(both), total))]


# ─────────────────────────────────────────────────────────────────────────────
# Venn diagrams
# ─────────────────────────────────────────────────────────────────────────────

@solver('prob_venn2')
def _prob_venn2(a_only, b_only, both, neither, ask_word):
    total = fr(a_only) + fr(b_only) + fr(both) + fr(neither)
    ask = str(ask_word).replace(' ', '').lower()
    parts = {'p(a)': fr(a_only) + fr(both), 'p(b)': fr(b_only) + fr(both), 'p(aandb)': fr(both),
             'p(neither)': fr(neither), 'p(nota)': fr(b_only) + fr(neither)}
    if ask not in parts:
        raise Cannot(f'cannot read the question {ask_word!r}')
    return [_frac(parts[ask], total)]


@diagram('prob_venn2')
def _check_venn2(inputs, html):
    drawn = read_venn2(one_svg(html))
    out = []
    for key in ('a_only', 'b_only', 'both', 'neither'):
        if drawn[key] != fr(inputs[key]):
            out.append(f'the diagram shows {drawn[key]} for {key} but the question was built with {inputs[key]}')
    total = sum(fr(inputs[k]) for k in ('a_only', 'b_only', 'both', 'neither'))
    if drawn['total'] != total:
        out.append(f'the diagram total is {drawn["total"]} but the regions add to {total}')
    return out


@solver('prob_venn3_parts')
def _prob_venn3_parts(a_only, b_only, c_only, ab_only, ac_only, bc_only, abc, neither, a_word, b_word, c_word):
    regions = [fr(x) for x in (a_only, b_only, c_only, ab_only, ac_only, bc_only, abc, neither)]
    total = sum(regions)
    exactly_one = regions[0] + regions[1] + regions[2]
    at_least_one = total - regions[7]
    a_or_b_not_c = regions[0] + regions[1] + regions[3]          # A only, B only, A and B but not C
    return [_frac(exactly_one, total), _frac(at_least_one, total), _frac(a_or_b_not_c, total)]


@diagram('prob_venn3_parts')
def _check_venn3(inputs, html):
    drawn = read_venn3(one_svg(html))
    return [f'the diagram shows {drawn[k]} in {k} but the question was built with {inputs[k]}'
            for k in drawn if drawn[k] != fr(inputs[k])]


@solver('prob_venn3_clues')
def _prob_venn3_clues(abc, ab_total, ac_total, bc_total, a_total, b_total, c_total, total, neither, c_word):
    abc, ab_total, ac_total, bc_total = fr(abc), fr(ab_total), fr(ac_total), fr(bc_total)
    ab, ac, bc = ab_total - abc, ac_total - abc, bc_total - abc
    a_only = fr(a_total) - ab - ac - abc
    b_only = fr(b_total) - ab - bc - abc
    c_only = fr(c_total) - ac - bc - abc
    regions = [a_only, b_only, c_only, ab, ac, bc, abc, fr(neither)]
    if min(regions) < 0:
        raise Cannot('the survey figures give a negative region')
    if sum(regions) != fr(total):
        raise Cannot(f'the survey figures give regions that add to {sum(regions)}, not the stated {total}')
    return regions + [_frac(c_total, total), _frac(ab + ac + bc, total)]


# ─────────────────────────────────────────────────────────────────────────────
# Two-stage trees
# ─────────────────────────────────────────────────────────────────────────────

def _tree_branches(n_first, n_second, replace):
    n1, n2 = fr(n_first), fr(n_second)
    total = n1 + n2
    stage1 = [n1 / total, n2 / total]
    counts = [n1, n2]
    stage2 = []
    for i in (0, 1):
        left = list(counts)
        if not replace:
            left[i] -= 1
        denom = total if replace else total - 1
        stage2.append([left[0] / denom, left[1] / denom])
    return stage1, stage2


@solver('prob_tree')
def _prob_tree(n_first, first_word, n_second, second_word, replace, ask):
    if str(first_word).lower() == str(second_word).lower():
        raise Cannot('the two colours have the same name')
    stage1, stage2 = _tree_branches(n_first, n_second, bool(replace))
    joint = {(i, j): stage1[i] * stage2[i][j] for i in (0, 1) for j in (0, 1)}
    if ask == 'both':
        return [_prob(joint[(0, 0)])]
    if ask == 'different':
        return [_prob(joint[(0, 1)] + joint[(1, 0)])]
    if ask == 'at_least_first':
        return [_prob(joint[(0, 0)] + joint[(0, 1)] + joint[(1, 0)])]
    raise Cannot(f'unknown tree question {ask!r}')


@diagram('prob_tree')
def _check_tree(inputs, html):
    drawn = read_tree(one_svg(html))
    out = []
    first, second = str(inputs['first_word']).lower(), str(inputs['second_word']).lower()
    if tuple(str(c).lower() for c in drawn['colours']) != (first, second):
        out.append(f'the tree is labelled {drawn["colours"]} but the question is about {(first, second)}')
    stage1, stage2 = _tree_branches(inputs['n_first'], inputs['n_second'], bool(inputs['replace']))
    want = {'b1': stage1[0], 'b2': stage1[1], 'b11': stage2[0][0], 'b12': stage2[0][1],
            'b21': stage2[1][0], 'b22': stage2[1][1]}
    shown = [k for k in want if drawn[k] is not None]
    for k in shown:
        if drawn[k] != want[k]:
            out.append(f'branch {k} shows {drawn[k]} but should be {want[k]}')
    outcomes = [stage1[i] * stage2[i][j] for i in (0, 1) for j in (0, 1)]
    for got, exp in zip(drawn['outcomes'], outcomes):
        if got is not None and got != exp:
            out.append(f'an outcome shows {got} but should be {exp}')
    return out
