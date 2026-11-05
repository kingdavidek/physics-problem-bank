"""Topic misconception rules, waves C and D (docs/GCSE_MATHS_HINTS.md, Phase 5).

The same design as ``misconception_topics.py`` (read its header first): ``TRUTH[family](inputs, pi)`` rebuilds the
correct answer from the numbers the question printed, as a guard; each rule gives the exact value a slip reaches; a
rule only fires when the guard reproduces the stored key. This module adds:

* probability, statistics, geometry angles, bearings and sequences (one typed value, from recorded inputs);
* algebra (linear equations, sequences, substitution) whose inputs are read from the *displayed question* by the
  parsers in ``DERIVE`` when the answer record is built (the verification hook only names the task for those
  families), so a rule can work from numbers like every other family;
* per-part rules (``PART_TRUTH`` / ``PART_RULES``) for answers typed in several boxes: the slip is a whole vector
  of values, and only the box that is being checked is compared;
* vector and coordinate pairs (``PAIR_TRUTH`` / ``PAIR_RULES``) and expression answers (``EXPR_*``) compared with the
  checker's own safe algebra.

It is imported at the bottom of ``misconception_topics`` (it needs that module's helpers and adds to its tables), never
on its own. It imports no generator, no random numbers and no database. Everything is exact (``Fraction``).
"""
from __future__ import annotations

import itertools
import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

from generators.shared.misconception_topics import (  # noqa: E402 - the host module is complete up to its tail
    F, MAX_TERMS, TopicRule, _items, _n, _r, inverse, round_unit, sqrtq, trig,
)

TRUTH: dict[str, Callable] = {}
QUIET: dict[str, Callable] = {}
ECHO_OK: frozenset = frozenset()
RULES: tuple = ()

ONE = Fraction(1)


def _sum(xs):
    total = Fraction(0)
    for x in xs:
        total += x
    return total


def _mean(xs):
    return _sum(xs) / len(xs)


def _nums(seq):
    return [F(v) for v in _items(seq)]


# =============================================================================================
# Probability
# =============================================================================================

def _die_faces(event):
    """The faces of a die that satisfy an event given in words, or None when the words are not understood."""
    text = str(event).strip().lower()
    patterns = (
        (r'a score of (\d)', lambda m: lambda x: x == int(m.group(1))),
        (r'(?:an? )?even number|a multiple of 2', lambda m: lambda x: x % 2 == 0),
        (r'(?:an? )?odd number', lambda m: lambda x: x % 2 == 1),
        (r'greater than (\d+)', lambda m: lambda x: x > int(m.group(1))),
        (r'less than (\d+)', lambda m: lambda x: x < int(m.group(1))),
        (r'at least (\d+)', lambda m: lambda x: x >= int(m.group(1))),
        (r'at most (\d+)', lambda m: lambda x: x <= int(m.group(1))),
        (r'(?:a )?factor of (\d+)', lambda m: lambda x: int(m.group(1)) % x == 0),
        (r'(?:a )?prime number', lambda m: lambda x: x in (2, 3, 5)),
        (r'(?:a )?multiple of (\d+)', lambda m: lambda x: x % int(m.group(1)) == 0),
    )
    for pattern, make in patterns:
        m = re.fullmatch(pattern, text)
        if m:
            test = make(m)
            return [x for x in range(1, 7) if test(x)]
    return None


def _die_truth(i, pi):
    faces = _die_faces(i['event_word'])
    if not faces:
        raise ValueError('event')
    return Fraction(len(faces), 6)


def _die_boundary(i, pi):
    """The count when the number named in the question is wrongly included or left out."""
    text = str(i['event_word']).strip().lower()
    m = re.fullmatch(r'(greater than|less than|at least|at most) (\d+)', text)
    if not m:
        return []
    n = int(m.group(2))
    kind = m.group(1)
    other = {'greater than': lambda x: x >= n, 'less than': lambda x: x <= n,
             'at least': lambda x: x > n, 'at most': lambda x: x < n}[kind]
    return [Fraction(len([x for x in range(1, 7) if other(x)]), 6)]


def _die_prime_one(i, pi):
    if not re.fullmatch(r'(?:a )?prime number', str(i['event_word']).strip().lower()):
        return []
    return [Fraction(4, 6)]


def _bag_counts(i):
    n1, n2 = F(i['n_first']), F(i['n_second'])
    colour = str(i['colour_word']).lower()
    first, second = str(i['first_word']).lower(), str(i['second_word']).lower()
    if first == second or colour not in (first, second):
        raise ValueError('colour')
    mine, other = (n1, n2) if colour == first else (n2, n1)
    return mine, other


def _bag_truth(i, pi):
    mine, other = _bag_counts(i)
    return mine / (mine + other)


def _bag_odds(i, pi):
    mine, other = _bag_counts(i)
    return [mine / other] if other else []


def _bag_other(i, pi):
    mine, other = _bag_counts(i)
    return [other / (mine + other)]


def _tree_stages(i):
    """(stage 1, stage 2) probabilities with replacement as in the question, plus the other kind, as Fractions."""
    n1, n2 = F(i['n_first']), F(i['n_second'])
    total = n1 + n2
    counts = (n1, n2)

    def stage(replace):
        s1 = (n1 / total, n2 / total)
        s2 = []
        for a in (0, 1):
            left = list(counts)
            if not replace:
                left[a] -= 1
            denom = total if replace else total - 1
            s2.append((left[0] / denom, left[1] / denom))
        return s1, s2

    return stage


def _tree_joint(i, replace):
    s1, s2 = _tree_stages(i)(replace)
    return {(a, b): s1[a] * s2[a][b] for a in (0, 1) for b in (0, 1)}


def _tree_value(i, replace):
    j = _tree_joint(i, replace)
    ask = i['ask']
    if ask == 'both':
        return j[(0, 0)]
    if ask == 'different':
        return j[(0, 1)] + j[(1, 0)]
    if ask == 'at_least_first':
        return 1 - j[(1, 1)]
    raise ValueError('ask')


def _tree_truth(i, pi):
    if str(i['first_word']).lower() == str(i['second_word']).lower():
        raise ValueError('colours')
    return _tree_value(i, bool(i['replace']))


def _tree_other_replacement(i, pi):
    try:
        return [_tree_value(i, not bool(i['replace']))]
    except ZeroDivisionError:
        return []


def _tree_first_only(i, pi):
    if i['ask'] != 'both':
        return []
    s1, _ = _tree_stages(i)(True)
    return [s1[0]]


def _tree_added(i, pi):
    if i['ask'] != 'both':
        return []
    s1, s2 = _tree_stages(i)(bool(i['replace']))
    return [s1[0] + s2[0][0]]


def _tree_one_order(i, pi):
    if i['ask'] != 'different':
        return []
    j = _tree_joint(i, bool(i['replace']))
    return [j[(0, 1)], j[(1, 0)]]


def _tree_complement(i, pi):
    if i['ask'] not in ('different', 'at_least_first'):
        return []
    return [1 - _tree_value(i, bool(i['replace']))]


def _tree_single_case(i, pi):
    if i['ask'] != 'at_least_first':
        return []
    return [_tree_joint(i, bool(i['replace']))[(0, 0)]]


def _coin_outcomes(i):
    n = _n(i['n'])
    if not 1 <= n <= 10:
        raise ValueError('coins')
    return [o for o in itertools.product((0, 1), repeat=n)]


def _coins_truth(i, pi):
    outcomes = _coin_outcomes(i)
    style = str(i['style_word'])
    if style == 'same':
        hits = [o for o in outcomes if len(set(o)) == 1]
    else:
        r = _n(i['r'])
        if style == 'exactly':
            hits = [o for o in outcomes if sum(o) == r]
        elif style == 'at least':
            hits = [o for o in outcomes if sum(o) >= r]
        else:
            raise ValueError('style')
    return Fraction(len(hits), len(outcomes))


def _coins_single(i, pi):
    n = _n(i['n'])
    return [Fraction(1, 2 ** n)]


# One half is the chance for a single coin, which a pupil may type for many reasons (review 2026-10-26: "3 coins, at
# least 1 head", typed 1/2, was called a boundary slip). It is never named as a slip in a coin question.
HALF = Fraction(1, 2)


def _coins_exact_only(i, pi):
    if str(i['style_word']) != 'at least':
        return []
    n, r = _n(i['n']), _n(i['r'])
    out = Fraction(math.comb(n, r), 2 ** n)
    return [out] if out != HALF else []


def _coins_boundary(i, pi):
    if str(i['style_word']) != 'at least':
        return []
    n, r = _n(i['n']), _n(i['r'])
    out = Fraction(sum(math.comb(n, k) for k in range(r + 1, n + 1)), 2 ** n)
    # one outcome only (all heads) is the single-outcome slip as well: two readings, so not offered (review --deep)
    return [out] if out and out not in (HALF, Fraction(1, 2 ** n)) else []


def _venn_counts(i):
    return F(i['a_only']), F(i['b_only']), F(i['both']), F(i['neither'])


def _venn_ask(i):
    return str(i['ask_word']).replace(' ', '').lower()


def _venn_parts(i):
    a, b, both, neither = _venn_counts(i)
    total = a + b + both + neither
    return {'p(a)': a + both, 'p(b)': b + both, 'p(aandb)': both, 'p(neither)': neither,
            'p(nota)': b + neither}, total


def _venn_truth(i, pi):
    parts, total = _venn_parts(i)
    ask = _venn_ask(i)
    if ask not in parts or total == 0:
        raise ValueError('ask')
    return parts[ask] / total


def _venn_region_only(i, pi):
    a, b, both, neither = _venn_counts(i)
    total = a + b + both + neither
    ask = _venn_ask(i)
    if ask == 'p(a)':
        return [a / total]
    if ask == 'p(b)':
        return [b / total]
    return []


def _venn_wrong_total(i, pi):
    parts, total = _venn_parts(i)
    a, b, both, neither = _venn_counts(i)
    if total - neither == 0:
        return []
    return [parts[_venn_ask(i)] / (total - neither)]



def _venn_complement(i, pi):
    ask = _venn_ask(i)
    a, b, both, neither = _venn_counts(i)
    total = a + b + both + neither
    if ask == 'p(neither)':
        return [(total - neither) / total]
    if ask == 'p(nota)':
        return [(a + both) / total]
    return []


def _venn_neither_missed(i, pi):
    if _venn_ask(i) != 'p(nota)':
        return []
    a, b, both, neither = _venn_counts(i)
    return [b / (a + b + both + neither)]


def _union_truth(i, pi):
    total, a, b, both = F(i['total']), F(i['a']), F(i['b']), F(i['both'])
    return (a + b - both) / total


def _union_counted_twice(i, pi):
    return [(F(i['a']) + F(i['b'])) / F(i['total'])]


def _union_multiplied(i, pi):
    total = F(i['total'])
    return [F(i['a']) / total * F(i['b']) / total]


def _union_removed_twice(i, pi):
    return [(F(i['a']) + F(i['b']) - 2 * F(i['both'])) / F(i['total'])]


def _union_wrong_total(i, pi):
    a, b, both = F(i['a']), F(i['b']), F(i['both'])
    return [(a + b - both) / (a + b)] if a + b else []


def _independent_p(i):
    return F(i['a']) / F(i['b']), F(i['c']) / F(i['d'])


def _at_least_truth(i, pi):
    return 1 - F(i['p_fail']) ** _n(i['attempts'])


def _at_least_fail_all(i, pi):
    return [F(i['p_fail']) ** _n(i['attempts'])]


def _at_least_one_attempt(i, pi):
    return [1 - F(i['p_fail'])]


def _at_least_all_succeed(i, pi):
    return [(1 - F(i['p_fail'])) ** _n(i['attempts'])]


def _conditional_pair(i):
    pa, pab = F(i['pa_n']) / F(i['pa_d']), F(i['pab_n']) / F(i['pab_d'])
    if pa == 0:
        raise ValueError('pa')
    return pa, pab


TRUTH.update({
    'prob_die': _die_truth,
    'prob_bag': _bag_truth,
    'prob_complement': lambda i, pi: 1 - F(i['p']),
    'prob_expected': lambda i, pi: F(i['a']) / F(i['b']) * F(i['n']),
    'prob_relative': lambda i, pi: F(i['success']) / F(i['trials']),
    'prob_die_or': lambda i, pi: Fraction(2, 6) if F(i['a']) != F(i['b']) else (_ for _ in ()).throw(ValueError('same')),
    'prob_coins': _coins_truth,
    'prob_tree': _tree_truth,
    'prob_at_least_one': _at_least_truth,
    'prob_conditional': lambda i, pi: _conditional_pair(i)[1] / _conditional_pair(i)[0],
    'prob_venn2': _venn_truth,
    'prob_union': _union_truth,
    'prob_independent': lambda i, pi: _independent_p(i)[0] * _independent_p(i)[1],
})

RULES += (
    _r('prob.die_boundary', 'prob.boundary', ['prob_die'], _die_boundary),
    _r('prob.die_one_prime', 'prob.one_not_prime', ['prob_die'], _die_prime_one),
    _r('prob.bag_odds', 'ratio.part_to_part', ['prob_bag'], _bag_odds),
    _r('prob.bag_other_colour', 'prob.other_colour', ['prob_bag'], _bag_other),
    _r('prob.complement_not_taken', 'prob.not_complemented', ['prob_complement'], lambda i, pi: [F(i['p'])]),
    _r('prob.expected_inverted', 'fdp.fraction_inverted', ['prob_expected'],
       lambda i, pi: [F(i['b']) / F(i['a']) * F(i['n'])] if F(i['a']) else []),
    _r('prob.expected_not_scaled', 'prob.expected_not_scaled', ['prob_expected'],
       lambda i, pi: [F(i['a']) / F(i['b'])]),
    _r('prob.relative_other', 'prob.other_outcome', ['prob_relative'],
       lambda i, pi: [(F(i['trials']) - F(i['success'])) / F(i['trials'])]),
    _r('prob.relative_odds', 'ratio.part_to_part', ['prob_relative'],
       lambda i, pi: [F(i['success']) / (F(i['trials']) - F(i['success']))] if F(i['trials']) != F(i['success']) else []),
    _r('prob.die_or_multiplied', 'prob.multiplied_for_or', ['prob_die_or'], lambda i, pi: [Fraction(1, 36)]),
    _r('prob.die_or_one_outcome', 'prob.one_outcome', ['prob_die_or'], lambda i, pi: [Fraction(1, 6)]),
    _r('prob.coins_single', 'prob.single_outcome', ['prob_coins'], _coins_single),
    _r('prob.coins_exact_only', 'prob.single_outcome', ['prob_coins'], _coins_exact_only),
    _r('prob.coins_boundary', 'prob.boundary', ['prob_coins'], _coins_boundary),
    _r('prob.tree_put_back_missed', 'prob.put_back_missed', ['prob_tree'],
       lambda i, pi: _tree_other_replacement(i, pi) if bool(i['replace']) else []),
    _r('prob.tree_removed_missed', 'prob.removed_missed', ['prob_tree'],
       lambda i, pi: _tree_other_replacement(i, pi) if not bool(i['replace']) else []),
    _r('prob.tree_first_only', 'prob.first_draw_only', ['prob_tree'], _tree_first_only),
    _r('prob.tree_added', 'prob.added_for_and', ['prob_tree'], _tree_added),
    _r('prob.tree_one_order', 'prob.one_order', ['prob_tree'], _tree_one_order),
    _r('prob.tree_complement', 'prob.complement_missed', ['prob_tree'], _tree_complement),
    _r('prob.tree_single_case', 'prob.single_outcome', ['prob_tree'], _tree_single_case),
    _r('prob.at_least_fail_all', 'prob.complement_missed', ['prob_at_least_one'], _at_least_fail_all),
    _r('prob.at_least_one_attempt', 'prob.one_attempt', ['prob_at_least_one'], _at_least_one_attempt),
    _r('prob.at_least_all_succeed', 'prob.all_succeed', ['prob_at_least_one'], _at_least_all_succeed),
    _r('prob.conditional_joint', 'prob.joint_not_conditional', ['prob_conditional'],
       lambda i, pi: [_conditional_pair(i)[1]]),
    _r('prob.venn_overlap_missed', 'prob.overlap_missed', ['prob_venn2'], _venn_region_only),
    _r('prob.venn_wrong_total', 'prob.total_wrong', ['prob_venn2'], _venn_wrong_total),
    _r('prob.venn_complement', 'prob.complement_missed', ['prob_venn2'],
       lambda i, pi: [c for c in _venn_complement(i, pi) if _venn_ask(i) == 'p(neither)']),
    _r('prob.venn_not_complemented', 'prob.not_complemented', ['prob_venn2'],
       lambda i, pi: [c for c in _venn_complement(i, pi) if _venn_ask(i) == 'p(nota)']),
    _r('prob.venn_neither_missed', 'prob.neither_missed', ['prob_venn2'], _venn_neither_missed),
    _r('prob.union_counted_twice', 'prob.overlap_counted_twice', ['prob_union'], _union_counted_twice),
    _r('prob.union_multiplied', 'prob.multiplied_for_or', ['prob_union'], _union_multiplied),
    _r('prob.union_removed_twice', 'prob.overlap_removed_twice', ['prob_union'], _union_removed_twice),
    _r('prob.union_wrong_total', 'prob.total_wrong', ['prob_union'], _union_wrong_total),
    _r('prob.independent_added', 'prob.added_for_and', ['prob_independent'],
       lambda i, pi: [_independent_p(i)[0] + _independent_p(i)[1]]),
)
ECHO_OK = ECHO_OK | frozenset({'prob.complement_not_taken'})


# =============================================================================================
# Statistics
# =============================================================================================

def _list_values(i):
    return _nums(i['values'])


def _list_truth(i, pi):
    vals = sorted(_list_values(i))
    stat = str(i['stat_word'])
    n = len(vals)
    if stat == 'range':
        return vals[-1] - vals[0]
    if stat == 'mean':
        return _sum(vals) / n
    if stat == 'median':
        mid = n // 2
        return vals[mid] if n % 2 else (vals[mid - 1] + vals[mid]) / 2
    if stat == 'mode':
        counts: dict = {}
        for v in vals:
            counts[v] = counts.get(v, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            raise ValueError('no single mode')
        return ranked[0][0]
    raise ValueError('stat')


def _stat_is(i, word):
    return str(i['stat_word']) == word


def _median_unsorted(i, pi):
    if not _stat_is(i, 'median'):
        return []
    vals = _list_values(i)
    n = len(vals)
    if n % 2:
        return [vals[n // 2]]
    return [(vals[n // 2 - 1] + vals[n // 2]) / 2]



def _median_is_mean(i, pi):
    return [_mean(_list_values(i))] if _stat_is(i, 'median') else []


def _range_largest(i, pi):
    return [max(_list_values(i))] if _stat_is(i, 'range') else []


def _range_first_last(i, pi):
    if not _stat_is(i, 'range'):
        return []
    vals = _list_values(i)
    out = abs(vals[-1] - vals[0])
    return [out] if out else []


def _mean_total(i, pi):
    return [_sum(_list_values(i))] if _stat_is(i, 'mean') else []


def _mean_divisor(i, pi):
    vals = _list_values(i)
    return [_sum(vals) / (len(vals) - 1)] if _stat_is(i, 'mean') and len(vals) > 1 else []


def _mean_is_median(i, pi):
    if not _stat_is(i, 'mean'):
        return []
    vals = sorted(_list_values(i))
    n = len(vals)
    return [vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2]


def _mode_count(i, pi):
    if not _stat_is(i, 'mode'):
        return []
    vals = _list_values(i)
    best = max(vals.count(v) for v in set(vals))
    return [Fraction(best)]


def _fm_pairs(i):
    values, freqs = _nums(i['values']), _nums(i['freqs'])
    if len(values) != len(freqs):
        raise ValueError('lengths')
    return values, freqs


def _fm_truth(i, pi):
    values, freqs = _fm_pairs(i)
    return _sum(v * f for v, f in zip(values, freqs)) / _sum(freqs)


def _hist_mids(i, which=None):
    out = []
    for lo, hi in _items(i['intervals']):
        lo, hi = F(lo), F(hi)
        out.append((lo + hi) / 2 if which is None else (lo if which == 'low' else hi))
    return out


def _hist_truth(i, pi):
    mids, freqs = _hist_mids(i), _nums(i['freqs'])
    if len(mids) != len(freqs) or not _sum(freqs):
        raise ValueError('lengths')
    return _sum(m * f for m, f in zip(mids, freqs)) / _sum(freqs)


def _hist_ends(i, pi):
    freqs = _nums(i['freqs'])
    total = _sum(freqs)
    return [_sum(m * f for m, f in zip(_hist_mids(i, w), freqs)) / total for w in ('low', 'high')]



def _hist_total(i, pi):
    mids, freqs = _hist_mids(i), _nums(i['freqs'])
    return [_sum(m * f for m, f in zip(mids, freqs))]


def _hist_rows(i, pi):
    mids, freqs = _hist_mids(i), _nums(i['freqs'])
    return [_sum(m * f for m, f in zip(mids, freqs)) / len(mids)]


def _fm_unweighted(i, pi):
    values, _ = _fm_pairs(i)
    return [_mean(values)]


def _fm_total(i, pi):
    values, freqs = _fm_pairs(i)
    return [_sum(v * f for v, f in zip(values, freqs))]


def _fm_rows(i, pi):
    values, freqs = _fm_pairs(i)
    return [_sum(v * f for v, f in zip(values, freqs)) / len(values)]


def _pie_truth(i, pi):
    freq, total = F(i['freq']), F(i['total'])
    if freq >= total or total == 0:
        raise ValueError('pie')
    return 360 * freq / total


def _box_truth(i, pi):
    lo, q1, q2, q3, hi = (F(i[k]) for k in ('min_val', 'q1', 'q2', 'q3', 'max_val'))
    if not lo <= q1 <= q2 <= q3 <= hi:
        raise ValueError('order')
    return q3 - q1


TRUTH.update({
    'stats_list': _list_truth,
    'stats_midpoint': lambda i, pi: (F(i['low']) + F(i['high'])) / 2,
    'stats_freq_mean': _fm_truth,
    'stats_hist_mean': _hist_truth,
    'stats_pie': _pie_truth,
    'stats_box': _box_truth,
    'stats_fd': lambda i, pi: F(i['freq']) / F(i['width']),
})

RULES += (
    _r('stats.median_unsorted', 'stats.median_unsorted', ['stats_list'], _median_unsorted),
    _r('stats.median_is_mean', 'stats.median_mean', ['stats_list'], _median_is_mean),
    _r('stats.range_largest', 'stats.range_largest', ['stats_list'], _range_largest),
    _r('stats.range_first_last', 'stats.range_unsorted', ['stats_list'], _range_first_last),
    _r('stats.mean_total', 'dec.mean_total', ['stats_list'], _mean_total),
    _r('stats.mean_divisor', 'stats.mean_divisor', ['stats_list'], _mean_divisor),
    _r('stats.mean_is_median', 'stats.mean_median', ['stats_list'], _mean_is_median),
    _r('stats.mode_count', 'stats.mode_count', ['stats_list'], _mode_count),
    _r('stats.midpoint_width', 'stats.midpoint_width', ['stats_midpoint'],
       lambda i, pi: [F(i['high']) - F(i['low'])]),
    _r('stats.midpoint_not_halved', 'stats.midpoint_not_halved', ['stats_midpoint'],
       lambda i, pi: [F(i['high']) + F(i['low'])]),
    _r('stats.freq_unweighted', 'stats.freq_ignored', ['stats_freq_mean'], _fm_unweighted),
    _r('stats.freq_total', 'dec.mean_total', ['stats_freq_mean'], _fm_total),
    _r('stats.freq_rows', 'stats.mean_divisor_rows', ['stats_freq_mean'], _fm_rows),
    _r('stats.hist_ends', 'stats.use_midpoint', ['stats_hist_mean'], _hist_ends),
    _r('stats.hist_total', 'dec.mean_total', ['stats_hist_mean'], _hist_total),
    _r('stats.hist_rows', 'stats.mean_divisor_rows', ['stats_hist_mean'], _hist_rows),
    _r('stats.pie_percentage', 'stats.pie_percentage', ['stats_pie'],
       lambda i, pi: [100 * F(i['freq']) / F(i['total'])]),
    _r('stats.pie_one_item', 'stats.pie_one_item', ['stats_pie'], lambda i, pi: [360 / F(i['total'])]),
    _r('stats.pie_other_sector', 'stats.pie_other_sector', ['stats_pie'],
       lambda i, pi: [360 - 360 * F(i['freq']) / F(i['total'])]),
    _r('stats.iqr_range', 'stats.iqr_range', ['stats_box'], lambda i, pi: [F(i['max_val']) - F(i['min_val'])]),
    _r('stats.iqr_upper_quartile', 'stats.iqr_upper_quartile', ['stats_box'], lambda i, pi: [F(i['q3'])]),
    _r('stats.fd_multiplied', 'stats.fd_multiplied', ['stats_fd'], lambda i, pi: [F(i['freq']) * F(i['width'])]),
    _r('stats.fd_inverted', 'gen.reciprocal', ['stats_fd'],
       lambda i, pi: [F(i['width']) / F(i['freq'])] if F(i['freq']) else []),
)
ECHO_OK = ECHO_OK | frozenset({
    'stats.median_unsorted', 'stats.range_largest', 'stats.mean_is_median',
    'stats.freq_total', 'stats.iqr_upper_quartile',
})


# =============================================================================================
# Geometry angles
# =============================================================================================

_TOTALS = {'straight line': 180, 'point': 360, 'triangle': 180, 'quadrilateral': 360, 'complementary': 90}


def _rule_total(i):
    word = str(i.get('rule_word', i.get('rule', ''))).lower()
    if word not in _TOTALS:
        raise ValueError('rule')
    return Fraction(_TOTALS[word])


def _rule_truth(i, pi):
    return _rule_total(i) - _sum(_nums(i['given']))


def _rule_sum(i, pi):
    return [_sum(_nums(i['given']))]


def _rule_wrong_total(i, pi):
    total = _rule_total(i)
    given = _sum(_nums(i['given']))
    return [Fraction(t) - given for t in (90, 180, 360) if Fraction(t) != total and Fraction(t) > given]


def _rule_one_missed(i, pi):
    given = _nums(i['given'])
    if len(given) < 2:
        return []
    total = _rule_total(i)
    return [total - (_sum(given) - g) for g in given]


_POLY_SIDES = {'triangle': 3, 'quadrilateral': 4, 'pentagon': 5, 'hexagon': 6, 'heptagon': 7, 'octagon': 8,
               'nonagon': 9, 'decagon': 10, 'undecagon': 11, 'dodecagon': 12}


def _poly_n(i):
    name = str(i['shape_word']).strip().lower()
    if name not in _POLY_SIDES:
        raise ValueError('shape')
    return Fraction(_POLY_SIDES[name])


def _para_kind(i):
    kind = str(i['kind_word']).lower()
    if kind not in ('alternate', 'corresponding', 'co-interior'):
        raise ValueError('kind')
    return kind


def _para_truth(i, pi):
    a = F(i['angle'])
    return 180 - a if _para_kind(i) == 'co-interior' else a


def _para_supplement(i, pi):
    return [180 - F(i['angle'])] if _para_kind(i) != 'co-interior' else []


def _para_equal(i, pi):
    return [F(i['angle'])] if _para_kind(i) == 'co-interior' else []


TRUTH.update({
    'ang_rule': _rule_truth,
    'ang_parallel': _para_truth,
    'ang_exterior': lambda i, pi: F(i['a']) + F(i['b']),
    'poly_sum': lambda i, pi: (F(i['n']) - 2) * 180,
    'poly_exterior': lambda i, pi: 360 / _poly_n(i),
    'poly_n_from_interior': lambda i, pi: 360 / (180 - F(i['interior'])),
    'poly_interior_ratio': lambda i, pi: 2 * (F(i['k']) + 1),
    'ang_isos_apex': lambda i, pi: 180 - 2 * F(i['base']),
    'ang_equilateral': lambda i, pi: Fraction(60) if str(i['shape_word']).lower() == 'equilateral' else (_ for _ in ()).throw(ValueError('shape')),
})

RULES += (
    _r('ang.rule_sum_not_subtracted', 'ang.sum_not_subtracted', ['ang_rule'], _rule_sum),
    _r('ang.rule_wrong_total', 'ang.wrong_total', ['ang_rule'], _rule_wrong_total),
    _r('ang.rule_angle_missed', 'ang.angle_missed', ['ang_rule'], _rule_one_missed),
    _r('ang.alternate_supplemented', 'ang.parallel_equal', ['ang_parallel'], _para_supplement),
    _r('ang.cointerior_equalled', 'ang.cointerior_total', ['ang_parallel'], _para_equal),
    _r('ang.exterior_interior', 'ang.interior_for_exterior', ['ang_exterior'],
       lambda i, pi: [180 - F(i['a']) - F(i['b'])]),
    _r('ang.poly_n_times', 'ang.polygon_n', ['poly_sum'], lambda i, pi: [F(i['n']) * 180]),
    _r('ang.poly_exterior_total', 'ang.exterior_sum_confused', ['poly_sum'], lambda i, pi: [Fraction(360)]),
    _r('ang.poly_one_interior', 'ang.one_interior', ['poly_sum'],
       lambda i, pi: [(F(i['n']) - 2) * 180 / F(i['n'])] if F(i['n']) else []),
    _r('ang.poly_ext_interior', 'ang.interior_for_exterior_poly', ['poly_exterior'],
       lambda i, pi: [(_poly_n(i) - 2) * 180 / _poly_n(i)]),
    _r('ang.poly_ext_half', 'ang.exterior_total', ['poly_exterior'], lambda i, pi: [180 / _poly_n(i)]),
    _r('ang.poly_n_interior_as_exterior', 'ang.interior_as_exterior', ['poly_n_from_interior'],
       lambda i, pi: [360 / F(i['interior'])] if F(i['interior']) else []),
    _r('ang.poly_n_angle_found', 'ang.angle_for_sides', ['poly_n_from_interior'],
       lambda i, pi: [180 - F(i['interior'])]),
    _r('ang.poly_ratio_angle_found', 'ang.angle_for_sides', ['poly_interior_ratio'],
       lambda i, pi: [180 / (F(i['k']) + 1)]),
    _r('ang.isos_one_base', 'ang.isos_one_base', ['ang_isos_apex'], lambda i, pi: [180 - F(i['base'])]),
    _r('ang.isos_bases_added', 'ang.isos_bases_added', ['ang_isos_apex'], lambda i, pi: [2 * F(i['base'])]),
    _r('ang.equilateral_total', 'ang.equilateral_total', ['ang_equilateral'], lambda i, pi: [Fraction(180)]),
)
ECHO_OK = ECHO_OK | frozenset({'ang.cointerior_equalled'})


# =============================================================================================
# Bearings
# =============================================================================================

def _deg(x):
    """A whole-degree bearing 0 to 359 from an exact value.

    Whole-change review 2026-11-03 (F10): the angle comes from sines and cosines to ten places, so an exact half (two
    equal legs on 062 and 155 degrees: 108.5) can land a hair below it and round down, while the generator rounds the
    exact half up (109). A value within a millionth of a half is taken as that half."""
    x = F(x)
    half = round(x - Fraction(1, 2)) + Fraction(1, 2)
    if abs(x - half) < Fraction(1, 10 ** 6):
        x = half
    return round_unit(x) % 360


def _b(i, key='b'):
    b = F(i[key])
    if b != int(b):
        raise ValueError('bearing')
    return b


def _leg_vector(i, radians=False):
    """(east, north) of a journey of (distance, bearing) legs, with sine and cosine to ten places."""
    east = north = Fraction(0)
    for d, b in _items(i['legs']):
        east += F(d) * trig('sin', F(b), radians)
        north += F(d) * trig('cos', F(b), radians)
    return east, north


def _en_vector(i):
    """(east, north) of a family that gives them directly (brg_en) or as legs (brg_legs)."""
    if 'legs' in i:
        return _leg_vector(i)
    return F(i['east']), F(i['north'])


def _bearing_from(east, north):
    """Whole-degree bearing of a point east and north of the start, or None for the start itself."""
    if east == 0 and north == 0:
        return None
    angle = inverse('acos', north / sqrtq(east * east + north * north)) if north != 0 or east != 0 else None
    if angle is None:
        return None
    return _deg(angle if east >= 0 else 360 - angle)


def _single_want(i):
    want = i.get('want')
    if not isinstance(want, (list, tuple)) or len(want) != 1:
        raise ValueError('want')
    return str(want[0])


def _legs_truth(i, pi):
    want = _single_want(i)
    east, north = _en_vector(i)
    if want == 'east':
        return east
    if want == 'north':
        return north
    if want == 'dist':
        return sqrtq(east * east + north * north)
    if want in ('bearing', 'return_bearing'):
        b = _bearing_from(east, north) if want == 'bearing' else _bearing_from(-east, -north)
        if b is None:
            raise ValueError('origin')
        return b
    raise ValueError('want')


def _legs_swapped(i, pi):
    want = _single_want(i)
    east, north = _en_vector(i)
    return [north] if want == 'east' else ([east] if want == 'north' else [])


def _legs_radians(i, pi):
    if 'legs' not in i:
        return []
    want = _single_want(i)
    east, north = _leg_vector(i, radians=True)
    return [east] if want == 'east' else ([north] if want == 'north' else [])


def _legs_path(i, pi):
    if 'legs' not in i or _single_want(i) != 'dist' or len(i['legs']) < 2:
        return []
    return [_sum(F(d) for d, b in _items(i['legs']))]


def _legs_components_added(i, pi):
    if _single_want(i) != 'dist':
        return []
    east, north = _en_vector(i)
    return [abs(east) + abs(north)]


def _legs_acute(i, pi):
    """The angle from the north-south line (no quarter turn) and from the east-west line."""
    if _single_want(i) != 'bearing':
        return []
    east, north = _en_vector(i)
    if east == 0 or north == 0:
        return []
    hyp = sqrtq(east * east + north * north)
    from_ns = inverse('acos', abs(north) / hyp)
    return [_deg(from_ns)] if from_ns is not None else []


def _legs_from_east(i, pi):
    if _single_want(i) != 'bearing':
        return []
    east, north = _en_vector(i)
    if east == 0 or north == 0:
        return []
    hyp = sqrtq(east * east + north * north)
    from_ew = inverse('asin', abs(north) / hyp)
    return [_deg(from_ew)] if from_ew is not None else []


def _compass_table(i):
    x = F(i['x'])
    table = {('N', 'E'): x, ('S', 'E'): 180 - x, ('S', 'W'): 180 + x, ('N', 'W'): 360 - x}
    ns, ew = str(i['ns']), str(i['ew'])
    if (ns, ew) not in table:
        raise ValueError('compass')
    return table, (ns, ew), x


def _compass_truth(i, pi):
    table, key, _ = _compass_table(i)
    return table[key] % 360


def _compass_quadrant(i, pi):
    table, key, x = _compass_table(i)
    return [v % 360 for k, v in table.items() if k != key and v % 360 != x]


TRUTH.update({
    'brg_back': lambda i, pi: (_b(i) + 180) % 360,
    'brg_compass': _compass_truth,
    'brg_angle_between': lambda i, pi: min(abs(_b(i, 'b2') - _b(i, 'b1')), 360 - abs(_b(i, 'b2') - _b(i, 'b1'))),
    'brg_angle_from_east': lambda i, pi: abs(90 - _b(i)),
    'brg_legs': _legs_truth,
    'brg_en': _legs_truth,
})

RULES += (
    _r('brg.back_same_direction', 'brg.same_direction', ['brg_back'], lambda i, pi: [_b(i)]),
    _r('brg.back_anticlockwise', 'brg.anticlockwise', ['brg_back'], lambda i, pi: [(360 - _b(i)) % 360]),
    _r('brg.back_north_line', 'brg.north_line', ['brg_back'],
       lambda i, pi: [180 - _b(i)] if _b(i) < 180 else []),
    _r('brg.compass_angle_only', 'brg.angle_only', ['brg_compass'], lambda i, pi: [F(i['x'])]),
    _r('brg.compass_quadrant', 'brg.quadrant', ['brg_compass'], _compass_quadrant),
    _r('brg.between_added', 'brg.added', ['brg_angle_between'], lambda i, pi: [_b(i, 'b1') + _b(i, 'b2')]),
    _r('brg.between_reflex', 'brg.reflex', ['brg_angle_between'],
       lambda i, pi: [360 - min(abs(_b(i, 'b2') - _b(i, 'b1')), 360 - abs(_b(i, 'b2') - _b(i, 'b1')))]),
    _r('brg.east_from_north', 'brg.from_north', ['brg_angle_from_east'], lambda i, pi: [_b(i)]),
    _r('brg.east_other_end', 'brg.road_other_end', ['brg_angle_from_east'],
       lambda i, pi: [180 - abs(90 - _b(i))]),
    _r('brg.legs_swapped', 'brg.east_north_swapped', ['brg_legs', 'brg_en'], _legs_swapped),
    _r('brg.legs_radians', 'trig.radians', ['brg_legs'], _legs_radians),
    _r('brg.legs_path', 'brg.path_length', ['brg_legs'], _legs_path),
    _r('brg.legs_components_added', 'pyth.sides_not_squares', ['brg_legs', 'brg_en'], _legs_components_added),
    _r('brg.legs_acute', 'brg.quarter_missed', ['brg_legs', 'brg_en'], _legs_acute),
    _r('brg.legs_from_east', 'brg.from_east_not_north', ['brg_legs', 'brg_en'], _legs_from_east),
)
ECHO_OK = ECHO_OK | frozenset({'brg.back_same_direction', 'brg.compass_angle_only', 'brg.east_from_north',
                               'brg.legs_swapped', 'brg.part_swapped'})      # brg_en prints the east and north legs


# =============================================================================================
# Reading the displayed question (algebra, sequences, graphs)
#
# The verification hook records only the task name for these families (the maths is on the page), so the answer
# record is built from the question text when the problem is finished (``answer_record.build_record``). Every parser
# is small, bounded and exact; text it does not understand gives None and the question simply has no topic rule.
# =============================================================================================

MAX_QUESTION_TEXT = 600
_MATH_SEGMENT = re.compile(r'\\\(\s*(.*?)\s*\\\)')


def _clean_math(text):
    t = str(text).replace('−', '-').replace('–', '-').replace('\\left', '').replace('\\right', '')
    t = re.sub(r'\\[dt]?frac', 'F', t)
    t = t.replace('\\times', '*').replace('\\cdot', '*').replace('×', '*').replace('÷', '/')
    t = t.replace('²', '^2').replace('³', '^3')
    return t


_AFF_TOKEN = re.compile(r'\s*(?:(\d+(?:\.\d+)?)|([A-Za-z])|(.))')


def _aff_tokens(text):
    t = _clean_math(text)
    if len(t) > 80:
        raise ValueError('long')
    out = []
    pos = 0
    while pos < len(t):
        m = _AFF_TOKEN.match(t, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        if m.group(1) is not None:
            out.append(('n', Fraction(m.group(1))))
        elif m.group(2) is not None:
            out.append(('F', None) if m.group(2) == 'F' else ('v', m.group(2)))
        else:
            ch = m.group(3)
            if ch.strip() == '':
                continue
            if ch not in '+-*/(){}':
                raise ValueError('character')
            out.append((ch, None))
    if not out or len(out) > 40:
        raise ValueError('size')
    return out


class _Aff:
    """a x + b with exact Fraction parts, for the one-variable linear expressions of a question."""
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        self.a, self.b = Fraction(a), Fraction(b)

    def const(self):
        return self.a == 0

    def __add__(self, o):
        return _Aff(self.a + o.a, self.b + o.b)

    def __sub__(self, o):
        return _Aff(self.a - o.a, self.b - o.b)

    def __neg__(self):
        return _Aff(-self.a, -self.b)

    def __mul__(self, o):
        if self.const():
            return _Aff(self.b * o.a, self.b * o.b)
        if o.const():
            return _Aff(self.a * o.b, self.b * o.b)
        raise ValueError('not linear')

    def div(self, o):
        if not o.const() or o.b == 0:
            raise ValueError('not linear')
        return _Aff(self.a / o.b, self.b / o.b)


class _AffParser:
    def __init__(self, text, var):
        self.t = _aff_tokens(text)
        self.i = 0
        self.var = var
        self.depth = 0
        self.tops = []                    # top-level bracketed terms: (k, p, q) for k(px + q)
        self.used_var = False

    def peek(self):
        return self.t[self.i][0] if self.i < len(self.t) else None

    def take(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def parse(self):
        value = self.expr()
        if self.i != len(self.t):
            raise ValueError('trailing')
        return value

    def expr(self):
        total = _Aff()
        sign = 1
        if self.peek() == '-':
            self.take()
            sign = -1
        elif self.peek() == '+':
            self.take()
        while True:
            term, bracket = self.term()
            if self.depth == 0 and bracket is not None:
                k, p, q = bracket
                self.tops.append((sign * k, p, q))
            total = total + term if sign > 0 else total - term
            if self.peek() in ('+', '-'):
                sign = 1 if self.take()[0] == '+' else -1
                continue
            return total

    def term(self):
        value, parts = self.factor()
        factors = [parts]
        while True:
            nxt = self.peek()
            if nxt == '*':
                self.take()
                f, parts = self.factor()
                value = value * f
                factors.append(parts)
            elif nxt == '/':
                self.take()
                f, _parts = self.factor()
                value = value.div(f)
                factors.append(None)
            elif nxt in ('v', '(', 'F'):
                f, parts = self.factor()
                value = value * f
                factors.append(parts)
            else:
                break
        bracket = None
        if len(factors) == 2 and isinstance(factors[0], Fraction) and isinstance(factors[1], tuple):
            bracket = (factors[0], factors[1][0], factors[1][1])
        return value, bracket

    def factor(self):
        """(_Aff, parts) where parts is the Fraction for a plain number, (p, q) for a bracket, else None."""
        kind = self.peek()
        if kind == 'n':
            v = self.take()[1]
            return _Aff(0, v), v
        if kind == 'v':
            name = self.take()[1]
            if name != self.var:
                raise ValueError('other variable')
            self.used_var = True
            return _Aff(1, 0), None
        if kind == '(':
            self.take()
            self.depth += 1
            inner = self.expr()
            self.depth -= 1
            if self.peek() != ')':
                raise ValueError('bracket')
            self.take()
            return inner, (inner.a, inner.b)
        if kind == 'F':
            self.take()
            num = self.group()
            den = self.group()
            return num.div(den), None
        if kind == '-':
            self.take()
            inner, _ = self.factor()
            return -inner, None
        raise ValueError('token')

    def group(self):
        if self.peek() != '{':
            raise ValueError('brace')
        self.take()
        self.depth += 1
        inner = self.expr()
        self.depth -= 1
        if self.peek() != '}':
            raise ValueError('brace')
        self.take()
        return inner


def _parse_aff(text, var):
    p = _AffParser(text, var)
    value = p.parse()
    return value, p


def _only_variable(text):
    """The single letter used as the unknown in a piece of maths (after fraction commands are removed), or None."""
    letters = set(re.findall(r'[A-Za-z]', re.sub(r'\\[A-Za-z]+', '', str(text))))
    return letters.pop() if len(letters) == 1 else None


def _fmt(x):
    x = Fraction(x)
    return int(x) if x.denominator == 1 else f'{x.numerator}/{x.denominator}'


def _equation_segment(text):
    """The first maths segment of the question that holds one equals sign."""
    for m in _MATH_SEGMENT.finditer(str(text)[:MAX_QUESTION_TEXT]):
        seg = m.group(1)
        if seg.count('=') == 1:
            return seg
    return None


def derive_lin_eq(text):
    seg = _equation_segment(text)
    if seg is None:
        return None
    var = _only_variable(seg)
    if var is None:
        return None
    left, right = seg.split('=')
    try:
        (l_aff, l_p), (r_aff, r_p) = _parse_aff(left, var), _parse_aff(right, var)
    except (ValueError, ZeroDivisionError, RecursionError):
        return None
    if not (l_p.used_var or r_p.used_var):
        return None
    inputs = {'a': [_fmt(l_aff.a), _fmt(l_aff.b), _fmt(r_aff.a), _fmt(r_aff.b)]}
    brackets = [[0, _fmt(k), _fmt(p), _fmt(q)] for k, p, q in l_p.tops] + \
               [[1, _fmt(k), _fmt(p), _fmt(q)] for k, p, q in r_p.tops]
    if brackets:
        inputs['br'] = brackets[:3]
    return 'lin_eq', inputs


def _lin_parts(i):
    a = [F(v) for v in _items(i['a'])]
    if len(a) != 4:
        raise ValueError('shape')
    return a


def _lin_solve(a_l, b_l, a_r, b_r):
    if a_l == a_r:
        raise ValueError('no unique root')
    return (b_r - b_l) / (a_l - a_r)


def _lin_truth(i, pi):
    return _lin_solve(*_lin_parts(i))


def _lin_sign_moved(i, pi):
    a_l, b_l, a_r, b_r = _lin_parts(i)
    out = []
    if a_l != a_r:
        out.append((b_r + b_l) / (a_l - a_r))
    if a_r != 0 and a_l + a_r != 0:
        out.append((b_r - b_l) / (a_l + a_r))
    return out


def _lin_wrong_inverse(i, pi):
    """k x = c (or x / m = c): the pupil multiplies where they should divide, and the other way round."""
    a_l, b_l, a_r, b_r = _lin_parts(i)
    if a_r == 0 and b_l == 0 and a_l not in (0, 1) and b_r != 0:
        return [b_r * a_l]
    return []


def _lin_one_term_divided(i, pi):
    """k x + b = c: only c is divided by k. Only for a whole-number k (review 2026-10-26): for (x + 3)/5 = 4 the
    solving step multiplies, and "when both sides are divided" would not describe it."""
    a_l, b_l, a_r, b_r = _lin_parts(i)
    if a_r == 0 and b_l != 0 and a_l not in (0, 1) and a_l.denominator == 1:
        return [b_r / a_l - b_l]
    return []


def _lin_bracket_partial(i, pi):
    a_l, b_l, a_r, b_r = _lin_parts(i)
    out = []
    for side, k, p, q in [(s, F(k), F(p), F(q)) for s, k, p, q in _items(i.get('br', [[0, 1, 0, 0]]))]:
        if k == 1:
            continue
        shift = q - k * q                  # x is multiplied, the number inside the bracket is not
        if side == 0:
            out.append(_lin_solve(a_l, b_l + shift, a_r, b_r))
        else:
            out.append(_lin_solve(a_l, b_l, a_r, b_r + shift))
    return out


TRUTH['lin_eq'] = _lin_truth
RULES += (
    _r('alg.lin_sign_moved', 'alg.sign_moved', ['lin_eq'], _lin_sign_moved),
    _r('alg.lin_wrong_inverse', 'alg.wrong_inverse', ['lin_eq'], _lin_wrong_inverse),
    _r('alg.lin_one_term_divided', 'alg.one_term_divided', ['lin_eq'], _lin_one_term_divided),
    _r('alg.lin_bracket_partial', 'alg.bracket_partial', ['lin_eq'], _lin_bracket_partial),
)


# ---- sequences --------------------------------------------------------------------------------------

_SEQ_ITEM = re.compile(r'\s*(-?\d+(?:\.\d+)?|_{2,}|…|\.\.\.)\s*(?:,|$)')


def _seq_items(text, start):
    """The comma-separated numbers (and one blank) that follow position ``start``."""
    items = []
    pos = start
    while True:
        m = _SEQ_ITEM.match(text, pos)
        if not m:
            # a blank or an ellipsis may be followed by a sentence without a comma
            m2 = re.compile(r'\s*(_{2,}|…|\.\.\.)').match(text, pos)
            if m2:
                items.append(m2.group(1))
            break
        items.append(m.group(1))
        pos = m.end()
        if len(items) > 14:
            return None
    return items


def derive_seq_next(text):
    t = str(text)[:MAX_QUESTION_TEXT].replace('−', '-')
    if ':' not in t:
        return None
    items = _seq_items(t, t.index(':') + 1)
    if not items:
        return None
    blanks = [k for k, v in enumerate(items) if v.startswith('_')]
    if len(blanks) != 1:
        return None
    k = blanks[0]
    known = [v for v in items if not v.startswith('_') and v not in ('…', '...')]
    if any(v in ('…', '...') for v in items) or len(known) < 3:
        return None
    try:
        terms = [_fmt(Fraction(v)) for v in known]
    except ValueError:
        return None
    return 'seq_terms', {'t': terms, 'at': k}


def _seq_pattern(i):
    """(kind, value at the blank, step) for an arithmetic, geometric, Fibonacci-type or quadratic pattern."""
    t = [F(v) for v in _items(i['t'])]
    at = _n(i['at'])
    full = t[:at] + [None] + t[at:]
    n = len(full)
    if at > n - 1 or at < 1:
        raise ValueError('blank')
    pairs = [(k, full[k], full[k + 1]) for k in range(n - 1) if full[k] is not None and full[k + 1] is not None]
    diffs = {b - a for _, a, b in pairs}
    if len(pairs) >= 2 and len(diffs) == 1:
        d = diffs.pop()
        value = full[at - 1] + d
        if at + 1 < n and full[at + 1] is not None and full[at + 1] != value + d:
            raise ValueError('inconsistent')
        return 'arith', value, d
    ratios = {b / a for _, a, b in pairs if a != 0}
    if len(pairs) >= 2 and len(ratios) == 1 and all(a != 0 for _, a, _b in pairs):
        r = ratios.pop()
        value = full[at - 1] * r
        if at + 1 < n and full[at + 1] is not None and full[at + 1] != value * r:
            raise ValueError('inconsistent')
        return 'geom', value, r
    if at == n - 1 and n >= 4:
        if all(full[k] == full[k - 1] + full[k - 2] for k in range(2, n - 1)):
            return 'fib', full[n - 2] + full[n - 3], None
        d = [full[k + 1] - full[k] for k in range(n - 2)]
        dd = {d[k + 1] - d[k] for k in range(len(d) - 1)}
        if len(d) >= 3 and len(dd) == 1:
            second = dd.pop()
            return 'quad', full[n - 2] + d[-1] + second, d[-1]
    raise ValueError('pattern')


def _seq_truth(i, pi):
    return _seq_pattern(i)[1]


def _seq_step(i, pi):
    kind, _value, step = _seq_pattern(i)
    return [step] if kind in ('arith', 'geom') and step is not None else []


def _seq_added_for_geometric(i, pi):
    kind, _value, step = _seq_pattern(i)
    if kind != 'geom':
        return []
    t = [F(v) for v in _items(i['t'])]
    at = _n(i['at'])
    return [t[at - 1] + (t[at - 1] - t[at - 2])] if at >= 2 else []


def _seq_gaps_constant(i, pi):
    kind, _value, step = _seq_pattern(i)
    if kind != 'quad':
        return []
    t = [F(v) for v in _items(i['t'])]
    return [t[-1] + step]


TRUTH['seq_terms'] = _seq_truth
RULES += (
    _r('seq.step_as_term', 'seq.step_as_term', ['seq_terms'], _seq_step),
    _r('seq.geometric_added', 'seq.pattern_multiplied', ['seq_terms'], _seq_added_for_geometric),
    _r('seq.quadratic_gaps', 'seq.gaps_not_constant', ['seq_terms'], _seq_gaps_constant),
)


_NTH_TERM = re.compile(r'nth term[^\\]*?\\\(\s*([^\\]*?)\s*\\\)', re.I)


def _nth_linear(text):
    """(a, b) for an nth term a n + b written in the question, else None."""
    m = _NTH_TERM.search(str(text)[:MAX_QUESTION_TEXT])
    if not m or _only_variable(m.group(1)) != 'n':
        return None
    try:
        aff, _p = _parse_aff(m.group(1), 'n')
    except (ValueError, ZeroDivisionError, RecursionError):
        return None
    return (aff.a, aff.b) if aff.a != 0 else None


def derive_seq_nth(text):
    lin = _nth_linear(text)
    m = re.search(r'\b(\d+)(?:st|nd|rd|th)\s+term\b', str(text)[:MAX_QUESTION_TEXT])
    if lin is None or not m:
        return None
    return 'seq_nth', {'a': _fmt(lin[0]), 'b': _fmt(lin[1]), 'n': int(m.group(1))}


def derive_seq_which(text):
    lin = _nth_linear(text)
    m = re.search(r'\bvalue\s+(-?\d+(?:\.\d+)?)', str(text)[:MAX_QUESTION_TEXT])
    if lin is None or not m:
        return None
    return 'seq_which', {'a': _fmt(lin[0]), 'b': _fmt(lin[1]), 'v': _fmt(Fraction(m.group(1)))}


TRUTH['seq_nth'] = lambda i, pi: F(i['a']) * F(i['n']) + F(i['b'])
TRUTH['seq_which'] = lambda i, pi: (F(i['v']) - F(i['b'])) / F(i['a'])
RULES += (
    _r('seq.nth_constant_forgotten', 'seq.constant_forgotten', ['seq_nth'], lambda i, pi: [F(i['a']) * F(i['n'])]),
    _r('seq.nth_constant_sign', 'seq.constant_sign', ['seq_nth'], lambda i, pi: [F(i['a']) * F(i['n']) - F(i['b'])]),
    _r('seq.nth_position_off', 'seq.position_off', ['seq_nth'],
       lambda i, pi: [F(i['a']) * (F(i['n']) + d) + F(i['b']) for d in (-1, 1)]),
    _r('seq.which_inverse', 'seq.constant_inverse', ['seq_which'], lambda i, pi: [(F(i['v']) + F(i['b'])) / F(i['a'])]),
    _r('seq.which_divide_first', 'seq.constant_first', ['seq_which'],
       lambda i, pi: [F(i['v']) / F(i['a']), F(i['v']) / F(i['a']) - F(i['b'])]),
)


# ---- graphs and substitution (numbers read from the question) --------------------------------------

def _subst_expression(text):
    """(expression in x, value of x) for "For y = 5x + 5, find y when x = -2.", else None."""
    t = str(text)[:MAX_QUESTION_TEXT].replace('\u2212', '-')
    m = re.search(r'\bFor\s+y\s*=\s*([^,]+?),\s*find\s+y\s+when\s+x\s*=\s*(-?\d+(?:\.\d+)?)', t)
    if not m:
        return None
    expr, x = m.group(1).strip(), m.group(2)
    if len(expr) > 40 or not re.fullmatch(r'[0-9x+\-*/^\s.\u00b2\u00b3()]+', expr):
        return None
    return expr, x


def _subst_text(expr, x, bracket=True):
    """The expression with x replaced by the value (in brackets or bare), in the notation of ``evaluate``."""
    e = expr.replace('\u2212', '-').replace('*', '\u00d7').replace('/', '\u00f7')
    e = re.sub(r'(\d)x', '\\1\u00d7x', e)
    return e.replace('x', f'({x})' if bracket else str(x))


def derive_gr_subst(text):
    found = _subst_expression(text)
    if found is None:
        return None
    expr, x = found
    return 'gr_subst', {'e': expr, 'x': _fmt(Fraction(x))}


def _gr_value(i, mode='standard', power_as_product=False, bracket=True):
    from generators.shared import misconception_topics as host
    return host.evaluate(_subst_text(i['e'], i['x'], bracket), mode, power_as_product)


def _gr_negative_power(i, pi):
    if F(i['x']) >= 0 or not re.search(r'\^|\u00b2|\u00b3', str(i['e'])):
        return []
    return [_gr_value(i, bracket=False)]


def _gr_power_multiplied(i, pi):
    if not re.search(r'\^|\u00b2|\u00b3', str(i['e'])):
        return []
    return [_gr_value(i, power_as_product=True)]


TRUTH['gr_subst'] = lambda i, pi: _gr_value(i)
RULES += (
    _r('gr.subst_negative_power', 'bidmas.negative_square', ['gr_subst'], _gr_negative_power),
    _r('gr.subst_power_multiplied', 'idx.multiplied', ['gr_subst'], _gr_power_multiplied),
)


TRUTH['vec_magnitude'] = lambda i, pi: sqrtq(F(i['x']) ** 2 + F(i['y']) ** 2)
RULES += (
    _r('vec.magnitude_not_rooted', 'gen.squared', ['vec_magnitude'], lambda i, pi: [F(i['x']) ** 2 + F(i['y']) ** 2]),
    _r('vec.magnitude_added', 'pyth.sides_not_squares', ['vec_magnitude'], lambda i, pi: [abs(F(i['x'])) + abs(F(i['y']))]),
)


# =============================================================================================
# Pairs (vectors and coordinates): the rule gives whole (x, y) pairs
# =============================================================================================

PAIR_TRUTH: dict = {}
PAIR_RULES: tuple = ()


def _p2(i, a, b):
    return F(i[a]), F(i[b])


def _add(u, v):
    return (u[0] + v[0], u[1] + v[1])


def _sub(u, v):
    return (u[0] - v[0], u[1] - v[1])


def _half(u):
    return (u[0] / 2, u[1] / 2)


def _ab(i):
    return _p2(i, 'a0', 'a1'), _p2(i, 'b0', 'b1')


def _section(i):
    a, b = _p2(i, 'ax', 'ay'), _p2(i, 'bx', 'by')
    m, n = F(i['m']), F(i['n'])
    if m + n == 0:
        raise ValueError('ratio')
    return a, b, m, n


def _section_point(a, b, m, n):
    t = m / (m + n)
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


PAIR_TRUTH.update({
    'vec_sub': lambda i: _sub(*_ab(i)),
    'vec_displacement': lambda i: _sub(_ab(i)[1], _ab(i)[0]),
    'vec_add': lambda i: _add(*_ab(i)),
    'vec_path_add': lambda i: _add(*_ab(i)),
    'vec_scale': lambda i: (F(i['k']) * F(i['v0']), F(i['k']) * F(i['v1'])),
    'vec_translate': lambda i: _add(_p2(i, 'p0', 'p1'), _p2(i, 'v0', 'v1')),
    'vec_midpoint': lambda i: _half(_add(*_ab(i))),
    'vec_section': lambda i: _section_point(*_section(i)),
    'vec_equation': lambda i: ((F(i['c0']) - F(i['b0'])) / 2, (F(i['c1']) - F(i['b1'])) / 2),
    'gr_midpoint': lambda i: _half(_add(_p2(i, 'x1', 'y1'), _p2(i, 'x2', 'y2'))),
})


def _scale_added(i):
    k = F(i['k'])
    return [(F(i['v0']) + k, F(i['v1']) + k)] if abs(k) != 1 else []


def _section_reversed(i):
    a, b, m, n = _section(i)
    return [_section_point(a, b, n, m)] if m != n else []


def _equation_not_divided(i):
    return [(F(i['c0']) - F(i['b0']), F(i['c1']) - F(i['b1']))]


def _equation_sign(i):
    return [((F(i['c0']) + F(i['b0'])) / 2, (F(i['c1']) + F(i['b1'])) / 2)]


PAIR_RULES += (
    _r('vec.sub_reversed', 'vec.order_reversed', ['vec_sub'], lambda i: [_sub(_ab(i)[1], _ab(i)[0])]),
    _r('vec.sub_added', 'vec.added_for_sub', ['vec_sub'], lambda i: [_add(*_ab(i))]),
    _r('vec.displacement_reversed', 'vec.order_reversed', ['vec_displacement'],
       lambda i: [_sub(_ab(i)[0], _ab(i)[1])]),
    _r('vec.add_subtracted', 'vec.subtracted_for_add', ['vec_add', 'vec_path_add'], lambda i: [_sub(*_ab(i))]),
    _r('vec.scale_added', 'vec.scalar_added', ['vec_scale'], _scale_added),
    _r('vec.translate_opposite', 'trans.translate_opposite', ['vec_translate'],
       lambda i: [_sub(_p2(i, 'p0', 'p1'), _p2(i, 'v0', 'v1'))]),
    _r('vec.translate_swapped', 'trans.vector_swapped', ['vec_translate'],
       lambda i: [_add(_p2(i, 'p0', 'p1'), (F(i['v1']), F(i['v0'])))]),
    _r('vec.midpoint_sum', 'vec.midpoint_not_halved', ['vec_midpoint'], lambda i: [_add(*_ab(i))]),
    _r('vec.midpoint_difference', 'vec.midpoint_difference', ['vec_midpoint'], lambda i: [_half(_sub(*_ab(i)))]),
    _r('vec.section_reversed', 'ratio.parts_swapped', ['vec_section'], _section_reversed),
    _r('vec.equation_sign', 'alg.sign_moved', ['vec_equation'], _equation_sign),
    _r('vec.equation_not_divided', 'vec.not_divided', ['vec_equation'], _equation_not_divided),
    _r('gr.midpoint_sum', 'vec.midpoint_not_halved', ['gr_midpoint'],
       lambda i: [_add(_p2(i, 'x1', 'y1'), _p2(i, 'x2', 'y2'))]),
    _r('gr.midpoint_difference', 'vec.midpoint_difference', ['gr_midpoint'],
       lambda i: [_half(_sub(_p2(i, 'x1', 'y1'), _p2(i, 'x2', 'y2')))]),
)

_MIDPOINT_TEXT = re.compile(r'midpoint of\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)\s*and\s*'
                            r'\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)')


def derive_gr_midpoint(text):
    m = _MIDPOINT_TEXT.search(str(text)[:MAX_QUESTION_TEXT].replace('\u2212', '-'))
    if not m:
        return None
    x1, y1, x2, y2 = (_fmt(Fraction(g)) for g in m.groups())
    return 'gr_midpoint', {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}


# ---- roots read from a factorised quadratic: "Find the roots of y = (x - 5)(x - 2)" -------------------

_ROOTS_TEXT = re.compile(r'roots of y\s*=\s*\(\s*x\s*([+-])\s*(\d+)\s*\)\s*\(?\s*x?\s*([+-]?)\s*(\d*)\s*\)?')


def derive_gr_roots(text):
    t = str(text)[:MAX_QUESTION_TEXT].replace('\u2212', '-')
    m = re.search(r'roots of y\s*=\s*\(\s*x\s*([+-])\s*(\d+)\s*\)\s*\(\s*x\s*([+-])\s*(\d+)\s*\)', t)
    if m:
        return 'gr_roots', {'s1': m.group(1), 'c1': int(m.group(2)), 's2': m.group(3), 'c2': int(m.group(4))}
    m = re.search(r'roots of y\s*=\s*\(\s*x\s*([+-])\s*(\d+)\s*\)\s*x\b', t)
    if m:
        return 'gr_roots', {'s1': m.group(1), 'c1': int(m.group(2)), 's2': '+', 'c2': 0}
    return None


def _root_pair(i):
    s1, s2 = str(i['s1']), str(i['s2'])
    if s1 not in '+-' or s2 not in '+-':
        raise ValueError('sign')
    r1 = -F(i['c1']) if s1 == '+' else F(i['c1'])
    r2 = -F(i['c2']) if s2 == '+' else F(i['c2'])
    return (r1, r2) if r1 <= r2 else (r2, r1)         # the boxes are "smaller root" then "larger root"


def _roots_negated(i):
    """Both roots with their signs flipped (in either order); nothing when the roots are r and -r, where flipping the
    signs gives the same two roots (review 2026-10-26: (2, -2) for roots -2 and 2 is the order, not the signs)."""
    r1, r2 = _root_pair(i)
    if {-r1, -r2} == {r1, r2}:
        return []
    return [(-r1, -r2), (-r2, -r1)]


PAIR_TRUTH['gr_roots'] = _root_pair
PAIR_RULES += (
    _r('gr.roots_signs', 'alg.root_signs', ['gr_roots'], _roots_negated),
)
ECHO_OK = ECHO_OK | frozenset({'gr.roots_signs'})          # the slip is the pair of numbers printed in the brackets


# =============================================================================================
# Per-part answers (several boxes): a vector of correct values, and slips that are whole vectors
# =============================================================================================

PART_TRUTH: dict = {}
PART_TOKENS: dict = {}
PART_RULES: tuple = ()
INTEGER_TOKENS = frozenset({'bearing', 'return_bearing', 'bearing_a_from_b', 'bearing_b_from_a'})
DECIMAL_TOKENS = frozenset({'east', 'north', 'dist', 'ab'})


def _leg_tokens(i):
    want = i.get('want')
    if not isinstance(want, (list, tuple)) or not 1 < len(want) <= 6:
        raise ValueError('want')
    return [str(w) for w in want]


def _token_value(i, token):
    east, north = _en_vector(i)
    if token == 'east':
        return east
    if token == 'north':
        return north
    if token == 'dist':
        return sqrtq(east * east + north * north)
    if token == 'bearing':
        return _bearing_from(east, north)
    if token == 'return_bearing':
        return _bearing_from(-east, -north)
    raise ValueError('token')


def _legs_vector(i):
    values = [_token_value(i, t) for t in _leg_tokens(i)]
    if any(v is None for v in values):
        raise ValueError('origin')
    return values


def _ships_points(i):
    d1, d2 = F(i['d1']), F(i['d2'])
    b1, b2 = F(i['b1']), F(i['b2'])
    a = (d1 * trig('sin', b1), d1 * trig('cos', b1))
    b = (d2 * trig('sin', b2), d2 * trig('cos', b2))
    return a, b


def _ships_value(i, token):
    a, b = _ships_points(i)
    if token == 'angle':
        d = abs(F(i['b2']) - F(i['b1'])) % 360
        return min(d, 360 - d)
    if token == 'ab':
        return sqrtq((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    if token == 'bearing_a_from_b':
        return _bearing_from(a[0] - b[0], a[1] - b[1])
    if token == 'bearing_b_from_a':
        return _bearing_from(b[0] - a[0], b[1] - a[1])
    raise ValueError('token')


def _ships_tokens(i):
    want = i.get('want')
    if not isinstance(want, (list, tuple)) or not 1 < len(want) <= 6:
        raise ValueError('want')
    return [str(w) for w in want]


def _ships_vector(i):
    values = [_ships_value(i, t) for t in _ships_tokens(i)]
    if any(v is None for v in values):
        raise ValueError('origin')
    return values


PART_TOKENS['brg_legs'] = _leg_tokens
PART_TOKENS['brg_en'] = _leg_tokens
PART_TOKENS['brg_two_ships'] = _ships_tokens
PART_TRUTH['brg_legs'] = _legs_vector
PART_TRUTH['brg_en'] = _legs_vector
PART_TRUTH['brg_two_ships'] = _ships_vector


def _map_tokens(tokens, fn):
    """A slip vector: for each token the candidate values ``fn(token)`` gives (a list, or None for no slip)."""
    return [fn(t) for t in tokens]


def _legs_slip(fn):
    def slip(i, pi=None):
        tokens = _leg_tokens(i)
        return [_map_tokens(tokens, lambda t: fn(i, t))]
    return slip


def _part_swapped(i, token):
    east, north = _en_vector(i)
    return [north] if token == 'east' else ([east] if token == 'north' else None)


def _part_radians(i, token):
    if 'legs' not in i or token not in ('east', 'north'):
        return None
    east, north = _leg_vector(i, radians=True)
    return [east if token == 'east' else north]


def _part_path(i, token):
    if 'legs' not in i or token != 'dist' or len(i['legs']) < 2:
        return None
    return [_sum(F(d) for d, b in _items(i['legs']))]


def _part_components_added(i, token):
    if token != 'dist':
        return None
    east, north = _en_vector(i)
    return [abs(east) + abs(north)]


def _part_acute(i, token):
    if token not in ('bearing', 'return_bearing'):
        return None
    east, north = _en_vector(i)
    if east == 0 or north == 0:
        return None
    hyp = sqrtq(east * east + north * north)
    angle = inverse('acos', abs(north) / hyp)
    return None if angle is None else [_deg(angle)]


def _part_from_east(i, token):
    if token not in ('bearing', 'return_bearing'):
        return None
    east, north = _en_vector(i)
    if east == 0 or north == 0:
        return None
    hyp = sqrtq(east * east + north * north)
    angle = inverse('asin', abs(north) / hyp)
    return None if angle is None else [_deg(angle)]


def _part_bearing_reversed(token_set):
    def fn(i, token):
        if token not in token_set:
            return None
        v = _token_value(i, token) if 'legs' in i or 'east' in i else _ships_value(i, token)
        return None if v is None else [(v + 180) % 360]
    return fn


def _part_bearing_anticlockwise(token_set):
    def fn(i, token):
        if token not in token_set:
            return None
        v = _token_value(i, token) if 'legs' in i or 'east' in i else _ships_value(i, token)
        return None if v is None or v in (0, 180) else [(360 - v) % 360]
    return fn


_LEG_BEARINGS = frozenset({'bearing', 'return_bearing'})
_SHIP_BEARINGS = frozenset({'bearing_a_from_b', 'bearing_b_from_a'})


def _ships_slip(fn):
    def slip(i, pi=None):
        tokens = _ships_tokens(i)
        return [_map_tokens(tokens, lambda t: fn(i, t))]
    return slip


def _ship_added(i, token):
    return [F(i['b1']) + F(i['b2'])] if token == 'angle' else None


def _ship_reflex(i, token):
    return [360 - _ships_value(i, 'angle')] if token == 'angle' else None


def _ship_sides_added(i, token):
    return [F(i['d1']) + F(i['d2'])] if token == 'ab' else None


def _ship_pythagoras(i, token):
    return [sqrtq(F(i['d1']) ** 2 + F(i['d2']) ** 2)] if token == 'ab' else None


def _ship_reversed(i, token):
    return _part_bearing_reversed(_SHIP_BEARINGS)(i, token)


def _ship_anticlockwise(i, token):
    return _part_bearing_anticlockwise(_SHIP_BEARINGS)(i, token)


PART_RULES += (
    _r('brg.part_swapped', 'brg.east_north_swapped', ['brg_legs', 'brg_en'], _legs_slip(_part_swapped)),
    _r('brg.part_radians', 'trig.radians', ['brg_legs'], _legs_slip(_part_radians)),
    _r('brg.part_path', 'brg.path_length', ['brg_legs'], _legs_slip(_part_path)),
    _r('brg.part_components_added', 'pyth.sides_not_squares', ['brg_legs', 'brg_en'],
       _legs_slip(_part_components_added)),
    _r('brg.part_acute', 'brg.quarter_missed', ['brg_legs', 'brg_en'], _legs_slip(_part_acute)),
    _r('brg.part_from_east', 'brg.from_east_not_north', ['brg_legs', 'brg_en'], _legs_slip(_part_from_east)),
    _r('brg.part_reversed', 'brg.reversed', ['brg_legs', 'brg_en'], _legs_slip(_part_bearing_reversed(_LEG_BEARINGS))),
    _r('brg.part_anticlockwise', 'brg.anticlockwise', ['brg_legs', 'brg_en'],
       _legs_slip(_part_bearing_anticlockwise(_LEG_BEARINGS))),
    _r('brg.ships_added', 'brg.added', ['brg_two_ships'], _ships_slip(_ship_added)),
    _r('brg.ships_reflex', 'brg.reflex', ['brg_two_ships'], _ships_slip(_ship_reflex)),
    _r('brg.ships_sides_added', 'pyth.sides_not_squares', ['brg_two_ships'], _ships_slip(_ship_sides_added)),
    _r('brg.ships_pythagoras', 'brg.pythagoras_misused', ['brg_two_ships'], _ships_slip(_ship_pythagoras)),
    _r('brg.ships_reversed', 'brg.reversed', ['brg_two_ships'], _ships_slip(_ship_reversed)),
    _r('brg.ships_anticlockwise', 'brg.anticlockwise', ['brg_two_ships'], _ships_slip(_ship_anticlockwise)),
)


# ---- transformations ----------------------------------------------------------------------------------

def _points(i):
    pts = [(F(x), F(y)) for x, y in _items(i['pts'])]
    if not 1 <= len(pts) <= 4:
        raise ValueError('points')
    return pts


def _centre(i):
    return F(i.get('cx', 0)), F(i.get('cy', 0))


def _reflect_point(line, p):
    x, y = p
    line = str(line).strip()
    if line == 'x-axis':
        return (x, -y)
    if line == 'y-axis':
        return (-x, y)
    m = re.fullmatch(r'y = (-?\d+)', line)
    if m:
        return (x, 2 * int(m.group(1)) - y)
    m = re.fullmatch(r'x = (-?\d+)', line)
    if m:
        return (2 * int(m.group(1)) - x, y)
    if line == 'y = x':
        return (y, x)
    if line == 'y = -x':
        return (-y, -x)
    m = re.fullmatch(r'y = x ([+-]) (\d+)', line)
    if m:
        c = int(m.group(2)) * (1 if m.group(1) == '+' else -1)
        return (y - c, x + c)
    raise ValueError('line')


def _turn(i):
    """Quarter turns clockwise (0 to 3) from the words of the question."""
    word = str(i['turn_word']).lower()
    m = re.match(r'(90|180|270)', word)
    if not m:
        raise ValueError('turn')
    angle = int(m.group(1))
    if angle == 180:
        return 2
    quarters = angle // 90
    return quarters if 'anticlockwise' not in word else (4 - quarters) % 4


def _rotate_point(quarters, p, c):
    x, y = p[0] - c[0], p[1] - c[1]
    for _ in range(quarters % 4):
        x, y = y, -x                       # a quarter turn clockwise about the centre
    return (c[0] + x, c[1] + y)


def _scale_factor(i):
    if 'k_num' in i:
        return F(i['k_num']) / F(i['k_den'])
    return F(i['k'])


def _enlarge_point(k, p, c):
    return (c[0] + k * (p[0] - c[0]), c[1] + k * (p[1] - c[1]))


def _image(i, kind=None, **override):
    """The image points of a trans_apply record (override lets a slip change one thing)."""
    kind = str(i['kind'])
    pts = _points(i)
    if kind == 'reflect':
        line = override.get('line', i['line_word'])
        return [_reflect_point(line, p) for p in pts]
    if kind == 'rotate':
        quarters = override.get('quarters', _turn(i))
        c = override.get('centre', _centre(i))
        return [_rotate_point(quarters, p, c) for p in pts]
    if kind == 'enlarge':
        k = override.get('k', _scale_factor(i))
        c = override.get('centre', _centre(i))
        return [_enlarge_point(k, p, c) for p in pts]
    if kind == 'translate':
        dx, dy = override.get('d', (F(i['dx']), F(i['dy'])))
        return [(p[0] + dx, p[1] + dy) for p in pts]
    raise ValueError('kind')


def _flat(points):
    return [c for p in points for c in p]


def _trans_vector(i):
    return _flat(_image(i))


PART_TRUTH['trans_apply'] = _trans_vector
PART_TOKENS['trans_apply'] = lambda i: ['x' if k % 2 == 0 else 'y' for k in range(2 * len(_points(i)))]


def _trans_swapped(i, pi=None):
    return [_flat([(y, x) for x, y in _image(i)])]


def _trans_wrong_axis(i, pi=None):
    if str(i['kind']) != 'reflect':
        return []
    line = str(i['line_word']).strip()
    other = {'x-axis': 'y-axis', 'y-axis': 'x-axis', 'y = x': 'y = -x', 'y = -x': 'y = x'}.get(line)
    if other is None:
        m = re.fullmatch(r'(y|x) = (-?\d+)', line)
        if m:
            other = f'{"x" if m.group(1) == "y" else "y"} = {m.group(2)}'
    return [] if other is None else [_flat(_image(i, line=other))]


def _trans_line_ignored(i, pi=None):
    if str(i['kind']) != 'reflect':
        return []
    line = str(i['line_word']).strip()
    if re.fullmatch(r'y = -?\d+', line):
        return [_flat(_image(i, line='x-axis'))]
    if re.fullmatch(r'x = -?\d+', line):
        return [_flat(_image(i, line='y-axis'))]
    if re.fullmatch(r'y = x [+-] \d+', line):
        return [_flat(_image(i, line='y = x'))]
    return []


def _trans_rotate_opposite(i, pi=None):
    if str(i['kind']) != 'rotate':
        return []
    q = _turn(i)
    return [] if q == 2 else [_flat(_image(i, quarters=(4 - q) % 4))]


def _trans_centre_ignored(i, pi=None):
    kind = str(i['kind'])
    if kind not in ('rotate', 'enlarge') or _centre(i) == (0, 0):
        return []
    return [_flat(_image(i, centre=(Fraction(0), Fraction(0))))]


def _trans_enlarge_added(i, pi=None):
    if str(i['kind']) != 'enlarge':
        return []
    k = _scale_factor(i)
    return [_flat([(x + k, y + k) for x, y in _points(i)])]


def _trans_enlarge_inverted(i, pi=None):
    if str(i['kind']) != 'enlarge':
        return []
    k = _scale_factor(i)
    return [] if k == 0 or abs(k) == 1 else [_flat(_image(i, k=1 / k))]


def _trans_negative_ignored(i, pi=None):
    if str(i['kind']) != 'enlarge':
        return []
    k = _scale_factor(i)
    return [_flat(_image(i, k=abs(k)))] if k < 0 else []


def _trans_translate_opposite(i, pi=None):
    if str(i['kind']) != 'translate':
        return []
    return [_flat(_image(i, d=(-F(i['dx']), -F(i['dy']))))]


def _trans_vector_swapped(i, pi=None):
    if str(i['kind']) != 'translate' or F(i['dx']) == F(i['dy']):
        return []
    return [_flat(_image(i, d=(F(i['dy']), F(i['dx']))))]


PART_RULES += (
    _r('trans.coords_swapped', 'trans.coords_swapped', ['trans_apply'], _trans_swapped),
    _r('trans.wrong_axis', 'trans.wrong_axis', ['trans_apply'], _trans_wrong_axis),
    _r('trans.line_ignored', 'trans.line_ignored', ['trans_apply'], _trans_line_ignored),
    _r('trans.rotate_opposite', 'trans.rotate_opposite', ['trans_apply'], _trans_rotate_opposite),
    _r('trans.centre_ignored', 'trans.centre_ignored', ['trans_apply'], _trans_centre_ignored),
    _r('trans.enlarge_added', 'trans.enlarge_added', ['trans_apply'], _trans_enlarge_added),
    _r('trans.enlarge_inverted', 'trans.enlarge_inverted', ['trans_apply'], _trans_enlarge_inverted),
    _r('trans.negative_ignored', 'trans.negative_ignored', ['trans_apply'], _trans_negative_ignored),
    _r('trans.translate_opposite', 'trans.translate_opposite', ['trans_apply'], _trans_translate_opposite),
    _r('trans.vector_swapped', 'trans.vector_swapped', ['trans_apply'], _trans_vector_swapped),
)

# ---- simultaneous equations, quadratic simultaneous equations, completing the square ---------------------

_LIN2_TERM = re.compile(r'([+-]?)(\d+(?:\.\d+)?)?([xy])?')


def _lin2_side(side):
    """(x coefficient, y coefficient, constant) of one side of an equation in x and y, or ValueError."""
    t = re.sub(r'\s+', '', _clean_math(side))
    if not t or len(t) > 24:
        raise ValueError('size')
    cx = cy = k = Fraction(0)
    pos = 0
    while pos < len(t):
        m = _LIN2_TERM.match(t, pos)
        if not m or m.end() == pos or (m.group(2) is None and m.group(3) is None):
            raise ValueError('term')
        val = Fraction(m.group(2)) if m.group(2) is not None else ONE
        if m.group(1) == '-':
            val = -val
        if m.group(3) == 'x':
            cx += val
        elif m.group(3) == 'y':
            cy += val
        else:
            k += val
        pos = m.end()
    return cx, cy, k


def derive_solve_system(text):
    segments = [m.group(1) for m in _MATH_SEGMENT.finditer(str(text)[:MAX_QUESTION_TEXT]) if m.group(1).count('=') == 1]
    if len(segments) != 2:
        return None
    row = []
    try:
        for seg in segments:
            left, right = seg.split('=')
            (lx, ly, lk), (rx, ry, rk) = _lin2_side(left), _lin2_side(right)
            row += [lx - rx, ly - ry, rk - lk]
    except ValueError:
        return None
    a1, b1, c1, a2, b2, c2 = row
    if a1 * b2 - a2 * b1 == 0:
        return None
    return 'linear_system_2', dict(zip(('a1', 'b1', 'c1', 'a2', 'b2', 'c2'), (_fmt(v) for v in row)))


def _ls(i):
    return [F(i[k]) for k in ('a1', 'b1', 'c1', 'a2', 'b2', 'c2')]


def _ls_solution(i):
    a1, b1, c1, a2, b2, c2 = _ls(i)
    d = a1 * b2 - a2 * b1
    if d == 0:
        raise ValueError('no unique solution')
    return (c1 * b2 - c2 * b1) / d, (a1 * c2 - a2 * c1) / d


def _ls_back_sign(i):
    """One value right; the other found by putting it back into an equation with the term moved without its sign changing."""
    a1, b1, c1, a2, b2, c2 = _ls(i)
    x, y = _ls_solution(i)
    out = []
    if b1:
        out.append((x, (c1 + a1 * x) / b1))
    if b2:
        out.append((x, (c2 + a2 * x) / b2))
    if a1:
        out.append(((c1 + b1 * y) / a1, y))
    if a2:
        out.append(((c2 + b2 * y) / a2, y))
    return out


def _ls_back_not_divided(i):
    a1, b1, c1, a2, b2, c2 = _ls(i)
    x, y = _ls_solution(i)
    out = []
    if abs(b1) not in (0, 1):
        out.append((x, c1 - a1 * x))
    if abs(b2) not in (0, 1):
        out.append((x, c2 - a2 * x))
    if abs(a1) not in (0, 1):
        out.append((c1 - b1 * y, y))
    if abs(a2) not in (0, 1):
        out.append((c2 - b2 * y, y))
    return out


PAIR_TRUTH['linear_system_2'] = _ls_solution
PAIR_RULES += (
    _r('sim.back_sign', 'alg.sign_moved', ['linear_system_2'], _ls_back_sign),
    _r('sim.back_not_divided', 'sim.not_divided', ['linear_system_2'], _ls_back_not_divided),
)


def derive_qsim_solve(text):
    """y = x^2 together with y = m x + c: the record holds m and c."""
    parabola = False
    lines = []
    for m in _MATH_SEGMENT.finditer(str(text)[:MAX_QUESTION_TEXT]):
        seg = m.group(1)
        if seg.count('=') != 1:
            continue
        left, right = seg.split('=')
        if re.sub(r'\s+', '', _clean_math(left)) != 'y':
            continue
        if re.sub(r'\s+', '', _clean_math(right)) == 'x^2':
            parabola = True
            continue
        try:
            cx, cy, k = _lin2_side(right)
        except ValueError:
            return None
        if cy != 0:
            return None
        lines.append((cx, k))
    if not parabola or len(lines) != 1:
        return None
    return 'qsim_solve', {'m': _fmt(lines[0][0]), 'c': _fmt(lines[0][1])}


def _qsim_roots(i):
    m, c = F(i['m']), F(i['c'])
    if m.denominator != 1 or c.denominator != 1:
        raise ValueError('integers only')
    disc = int(m * m + 4 * c)
    if disc <= 0:
        raise ValueError('two solutions needed')
    r = math.isqrt(disc)
    if r * r != disc:
        raise ValueError('roots are not whole numbers')
    return (m - r) / 2, (m + r) / 2


def _qsim_vector(i):
    r1, r2 = _qsim_roots(i)
    return [r1, r1 * r1, r2, r2 * r2]


def _qsim_signs(i, pi=None):
    """The x values with their signs flipped, in either order. The y boxes say nothing (review 2026-10-26: in the
    second order a y box is only the other pair's y value, which is a pairing slip, not a sign slip)."""
    r1, r2 = _qsim_roots(i)
    if {-r1, -r2} == {r1, r2}:
        return []                       # roots r and -r: flipping the signs only changes the order
    return [[-r1, None, -r2, None], [-r2, None, -r1, None]]


def _qsim_swapped(i, pi=None):
    r1, r2 = _qsim_roots(i)
    return [[r1 * r1, r1, r2 * r2, r2]]


def _qsim_doubled(i, pi=None):
    r1, r2 = _qsim_roots(i)
    return [[r1, 2 * r1, r2, 2 * r2]]


PART_TRUTH['qsim_solve'] = _qsim_vector
PART_TOKENS['qsim_solve'] = lambda i: ['x', 'y', 'x', 'y']
PART_RULES += (
    _r('qsim.root_signs', 'alg.root_signs', ['qsim_solve'], _qsim_signs),
    _r('qsim.pairs_swapped', 'gen.pair_swapped', ['qsim_solve'], _qsim_swapped),
    _r('qsim.y_doubled', 'idx.multiplied', ['qsim_solve'], _qsim_doubled),
)

_CTS_QUADRATIC = re.compile(r'x\^2\s*([+-])\s*(\d+)\s*x')


def _cts_b(text):
    m = _CTS_QUADRATIC.search(_clean_math(str(text)[:MAX_QUESTION_TEXT]))
    if not m:
        return None
    return Fraction(m.group(2)) * (-1 if m.group(1) == '-' else 1)


def derive_cts_square(text):
    b = _cts_b(text)
    return None if b is None else ('cts_square', {'b': _fmt(b)})


def derive_cts_half(text):
    b = _cts_b(text)
    return None if b is None else ('cts_half', {'b': _fmt(b)})


TRUTH['cts_square'] = lambda i, pi: (F(i['b']) / 2) ** 2
TRUTH['cts_half'] = lambda i, pi: F(i['b']) / 2
RULES += (
    _r('cts.half_not_squared', 'cts.half_not_squared', ['cts_square'], lambda i, pi: [F(i['b']) / 2]),
    _r('cts.whole_squared', 'cts.whole_squared', ['cts_square'], lambda i, pi: [F(i['b']) ** 2]),
    _r('cts.not_halved', 'cts.not_halved', ['cts_half'], lambda i, pi: [F(i['b'])]),
)
ECHO_OK = ECHO_OK | frozenset({'cts.half_not_squared', 'cts.not_halved'})        # the half and the coefficient are printed


# Phase 5b: circle theorems, similarity and the topics after them are data in their own module, added here.
from generators.shared import misconception_5b as _b5  # noqa: E402

_b5.install(globals())
MESSAGES_5B = _b5.MESSAGES

PART_FAMILIES = frozenset(PART_TRUTH)
PAIR_FAMILIES = frozenset(PAIR_TRUTH)


# =============================================================================================
# Expressions (an algebraic answer): slips are expression texts, compared with the checker's own safe algebra
# =============================================================================================

EXPR_TRUTH: dict = {}      # family -> fn(inputs) -> (subject, expression text)
EXPR_RULES: tuple = ()


def _num(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f'({x.numerator}/{x.denominator})'


def _signed(x):
    x = Fraction(x)
    if x == 0:
        return ''
    return ('+' if x > 0 else '-') + (str(abs(x.numerator)) if x.denominator == 1
                                      else f'({abs(x.numerator)}/{x.denominator})')


def _linear_text(a, b, var='n'):
    a = Fraction(a)
    lead = '' if a == 1 else ('-' if a == -1 else f'{_num(a)}*')
    return f'{lead}{var}{_signed(b)}'


def derive_seq_find(text):
    t = str(text)[:MAX_QUESTION_TEXT].replace('−', '-')
    if ':' not in t or re.search(r'second|quadratic|geometric', t, re.I):
        return None
    items = _seq_items(t, t.index(':') + 1)
    if not items or len(items) < 3 or any(not re.fullmatch(r'-?\d+(?:\.\d+)?', v) for v in items):
        return None
    terms = [Fraction(v) for v in items]
    if len({b - a for a, b in zip(terms, terms[1:])}) != 1:
        return None
    return 'seq_nth_find', {'t': [_fmt(v) for v in terms]}


def _seq_find_dc(i):
    t = [F(v) for v in _items(i['t'])]
    if len(t) < 3 or len({b - a for a, b in zip(t, t[1:])}) != 1:
        raise ValueError('not arithmetic')
    d = t[1] - t[0]
    return d, t[0] - d, t[0]


def _seq_find_truth(i):
    d, c, _first = _seq_find_dc(i)
    return '', _linear_text(d, c)


EXPR_TRUTH['seq_nth_find'] = _seq_find_truth
EXPR_RULES += (
    _r('seq.find_first_term', 'seq.first_term_constant', ['seq_nth_find'],
       lambda i: [_linear_text(_seq_find_dc(i)[0], _seq_find_dc(i)[2])]),
    _r('seq.find_difference_constant', 'seq.difference_constant', ['seq_nth_find'],
       lambda i: [_linear_text(_seq_find_dc(i)[0], _seq_find_dc(i)[0])]),
    _r('seq.find_constant_sign', 'seq.constant_sign_rule', ['seq_nth_find'],
       lambda i: [_linear_text(_seq_find_dc(i)[0], -_seq_find_dc(i)[1])]),
    _r('seq.find_add_not_multiply', 'seq.add_not_multiply', ['seq_nth_find'],
       lambda i: [_linear_text(1, _seq_find_dc(i)[0])]),
)


def derive_expand2(text):
    seg = None
    for m in _MATH_SEGMENT.finditer(str(text)[:MAX_QUESTION_TEXT]):
        if '=' not in m.group(1):
            seg = m.group(1)
            break
    if seg is None:
        return None
    m = re.fullmatch(r'\(([^()]+)\)\s*\(([^()]+)\)', seg.strip())
    if not m or _only_variable(seg) != 'x':
        return None
    try:
        (u, _pu), (w, _pw) = _parse_aff(m.group(1), 'x'), _parse_aff(m.group(2), 'x')
    except (ValueError, ZeroDivisionError, RecursionError):
        return None
    if u.a == 0 or w.a == 0:
        return None
    return 'expand2', {'p': _fmt(u.a), 'q': _fmt(u.b), 'r': _fmt(w.a), 's': _fmt(w.b)}


def _expand_text(i, middle):
    p, q, r, s = (F(i[k]) for k in ('p', 'q', 'r', 's'))
    return f'{_num(p * r)}*x**2{_signed(middle)}{"*x" if middle != 0 else ""}{_signed(q * s)}'


def _expand_truth(i):
    p, q, r, s = (F(i[k]) for k in ('p', 'q', 'r', 's'))
    return '', _expand_text(i, p * s + q * r)


def _expand_cross_missed(i):
    p, q, r, s = (F(i[k]) for k in ('p', 'q', 'r', 's'))
    return [_expand_text(i, 0), _expand_text(i, p * s), _expand_text(i, q * r)]


EXPR_TRUTH['expand2'] = _expand_truth
EXPR_RULES += (
    _r('alg.expand_cross_missed', 'alg.expand_cross_missed', ['expand2'], _expand_cross_missed),
)


# ---- forming an expression (Phase 3 batch A: algebra_practice_form_expression) ---------------------------------------

def _form_truth_text(i):
    k1, k2, v1, v2 = int(i['k1']), int(i['k2']), str(i['var1']), str(i['var2'])
    if i['kind'] == 'cost':
        return f'{k1}*{v1}+{k2}*{v2}'
    if i['kind'] == 'ages':
        return f'{v1}+({v1}+{k1})+{k2}*{v1}'
    return f'2*{v1}+2*({v1}+{k1})'


def _form_truth(i):
    return '', _form_truth_text(i)


def _form_cost_swapped(i):
    if i['kind'] != 'cost':
        return []
    return [f"{int(i['k1'])}*{i['var2']}+{int(i['k2'])}*{i['var1']}"]


def _form_times_as_more(i):
    if i['kind'] != 'ages':
        return []
    v, k1, k2 = str(i['var1']), int(i['k1']), int(i['k2'])
    return [f'{v}+({v}+{k1})+({v}+{k2})']


def _form_one_length(i):
    if i['kind'] != 'perimeter':
        return []
    w, k1 = str(i['var1']), int(i['k1'])
    return [f'{w}+({w}+{k1})']


EXPR_TRUTH['alg_form_expr'] = _form_truth
EXPR_RULES += (
    _r('alg.form_cost_swapped', 'alg.form_numbers_swapped', ['alg_form_expr'], _form_cost_swapped),
    _r('alg.form_times_as_more', 'alg.form_times_added', ['alg_form_expr'], _form_times_as_more),
    _r('alg.form_one_length', 'alg.form_one_length', ['alg_form_expr'], _form_one_length),
)


# ---- changing the subject ----------------------------------------------------------------------------

def _formula_to_py(seg):
    t = _clean_math(seg).lower()
    t = t.replace('\\pi', '§')
    for _ in range(4):
        t = re.sub(r'f\{([^{}]*)\}\{([^{}]*)\}', r'((\1)/(\2))', t)
    if '\\' in t or '{' in t or '}' in t or 'sqrt' in t:
        return None
    t = re.sub(r'\s+', '', t).replace('^', '**')
    t = re.sub(r'(?<=[0-9a-z§)])(?=[a-z§(])', '*', t)
    return t.replace('§', 'pi')


def derive_rearrange(text):
    t = str(text)[:MAX_QUESTION_TEXT]
    m = re.search(r'make\s+\\\(\s*([A-Za-z])\s*\\\)\s+the\s+subject', t, re.I)
    seg = _equation_segment(t)
    if not m or seg is None:
        return None
    if 'x_' in seg or len(seg) > 70:
        return None
    letters = set(re.findall(r'[A-Za-z]', re.sub(r'\\[A-Za-z]+', '', seg)))
    if any(c.lower() != c and c.lower() in letters for c in letters):
        return None                                    # V and v in one formula: lower-casing would merge them
    subject = m.group(1).lower()
    formula = _formula_to_py(seg)
    if formula is None or formula.count('=') != 1 or len(formula) > 64 or subject not in formula:
        return None
    if _in_denominator(formula, subject):
        return None                                     # the subject under a division: not a one-step rearrangement
    return 'rearrange', {'v': subject, 'f': formula}


def _in_denominator(formula, subject):
    """True when the subject letter sits in the bottom of a division."""
    for m in re.finditer(r'/', formula):
        rest = formula[m.end():]
        if rest.startswith('('):
            depth, end = 0, 0
            for k, ch in enumerate(rest):
                depth += ch == '('
                depth -= ch == ')'
                if depth == 0:
                    end = k + 1
                    break
            group = rest[:end]
        else:
            group = re.match(r'[a-z0-9.]+', rest).group(0) if re.match(r'[a-z0-9.]+', rest) else ''
        if re.search(r'(?<![a-z])' + re.escape(subject) + r'(?![a-z])', group):
            return True
    return False


def _rearr_parts(i):
    """(sympy symbol, linear/quadratic kind, rest terms, coefficient) for a formula to rearrange, or ValueError."""
    import sympy
    from generators.shared import answer_checkers as ac
    left, right = str(i['f']).split('=')
    lhs, rhs = ac._safe_sympify(left), ac._safe_sympify(right)
    if lhs is None or rhs is None or len(str(i['v'])) != 1:
        raise ValueError('formula')
    sym = sympy.Symbol(str(i['v']))
    total = sympy.expand(lhs - rhs)
    terms = sympy.Add.make_args(total)
    if len(terms) > 8:
        raise ValueError('long')
    with_v = [t for t in terms if t.has(sym)]
    rest = [t for t in terms if not t.has(sym)]
    if not with_v or not rest:
        raise ValueError('shape')
    s = sympy.Add(*with_v)
    c1 = sympy.cancel(s / sym)
    if not c1.has(sym) and c1 != 0:
        return sympy, sym, 'lin', rest, c1
    c2 = sympy.cancel(s / sym ** 2)
    if not c2.has(sym) and c2 != 0:
        return sympy, sym, 'sq', rest, c2
    raise ValueError('not a simple rearrangement')


def _rearr_text(sympy, expr):
    return sympy.sstr(sympy.together(sympy.expand(expr)))


def _rearr_root(sympy, value):
    """sqrt(radicand), written so that the checker's equivalence reads it as the square root of the whole fraction."""
    num, den = sympy.fraction(sympy.together(sympy.expand(value)))
    return f'sqrt(({sympy.sstr(num)})/({sympy.sstr(den)}))'


def _rearr_truth(i):
    sympy, sym, kind, rest, c = _rearr_parts(i)
    value = -sympy.Add(*rest) / c
    if kind == 'sq':
        return str(i['v']), _rearr_root(sympy, value)
    return str(i['v']), _rearr_text(sympy, value)


def _rearr_wrap(fn):
    def slip(i):
        try:
            return fn(i)
        except Exception:  # noqa: BLE001 - a formula the rules do not understand simply has no slip
            return []
    return slip


def _subject_prefix(i):
    return str(i['v']) + '='


def _rearr_moving(sympy, i, sym):
    """The terms (as they stand in ``rest``) that sit on the subject's side and so must move to the other side.

    Review 2026-10-26: "Make I the subject of P = VI" has no term that moves, but -P/V was called "the sign of the
    term that moved". Only a term that starts beside the subject can be moved with the wrong sign.
    """
    from generators.shared import answer_checkers as ac
    left, right = str(i['f']).split('=')
    lhs, rhs = ac._safe_sympify(left), ac._safe_sympify(right)
    if lhs is None or rhs is None:
        raise ValueError('formula')
    lhs, rhs = sympy.expand(lhs), sympy.expand(rhs)
    if lhs.has(sym) and not rhs.has(sym):
        return [t for t in sympy.Add.make_args(lhs) if not t.has(sym)]
    if rhs.has(sym) and not lhs.has(sym):
        return [-t for t in sympy.Add.make_args(rhs) if not t.has(sym)]
    return []


def _rearr_sign(i):
    sympy, sym, kind, rest, c = _rearr_parts(i)
    if kind == 'sq' and len(rest) < 2:
        return []                                       # a flipped lone term would put a negative under the root
    moving = _rearr_moving(sympy, i, sym)
    out = []
    for k in range(len(rest)):
        if not any(sympy.expand(rest[k] - m) == 0 for m in moving):
            continue
        flipped = [(-t if j == k else t) for j, t in enumerate(rest)]
        value = -sympy.Add(*flipped) / c
        out.append(_rearr_root(sympy, value) if kind == 'sq' else _rearr_text(sympy, value))
    return out


def _rearr_one_term(i):
    sympy, sym, kind, rest, c = _rearr_parts(i)
    if kind != 'lin' or len(rest) < 2 or c in (1, -1):
        return []
    out = []
    for k in range(len(rest)):
        value = rest[k] / (-c) + sympy.Add(*[t for j, t in enumerate(rest) if j != k])
        out.append(_rearr_text(sympy, value))
    return out


def _rearr_wrong_inverse(i):
    sympy, sym, kind, rest, c = _rearr_parts(i)
    if kind != 'lin' or len(rest) != 1 or c in (1, -1):
        return []
    return [_rearr_text(sympy, -rest[0] * c)]


def _rearr_root_missed(i):
    sympy, sym, kind, rest, c = _rearr_parts(i)
    if kind != 'sq':
        return []
    return [_rearr_text(sympy, -sympy.Add(*rest) / c)]


EXPR_TRUTH['rearrange'] = _rearr_truth
EXPR_RULES += (
    _r('alg.rearr_sign_moved', 'alg.sign_moved', ['rearrange'], _rearr_wrap(_rearr_sign)),
    _r('alg.rearr_one_term_divided', 'alg.one_term_divided', ['rearrange'], _rearr_wrap(_rearr_one_term)),
    _r('alg.rearr_wrong_inverse', 'alg.wrong_inverse', ['rearrange'], _rearr_wrap(_rearr_wrong_inverse)),
    _r('alg.rearr_root_missed', 'alg.root_missed', ['rearrange'], _rearr_wrap(_rearr_root_missed)),
)


# =============================================================================================
# Tables the answer record and the diagnosis read
# =============================================================================================

DERIVE: dict = {
    'solve_linear': derive_lin_eq,
    'seq_next': derive_seq_next,
    'seq_nth_value': derive_seq_nth,
    'seq_which_term': derive_seq_which,
    'seq_find_nth': derive_seq_find,
    'solve_system': derive_solve_system,
    'qsim_solve': derive_qsim_solve,
    'cts_missing_constant': derive_cts_square,
    'cts_square_the_half': derive_cts_square,
    'cts_half': derive_cts_half,
    'gr_subst': derive_gr_subst,
    'gr_midpoint': derive_gr_midpoint,
    'gr_roots': derive_gr_roots,
    'expand': derive_expand2,
    'rearrange': derive_rearrange,
}
DERIVE.update(_b5.DERIVE)

EXPR_FAMILIES = frozenset(EXPR_TRUTH)
EXPR_BY_FAMILY: dict = {}
for _rule in EXPR_RULES:
    for _fam in _rule.families:
        EXPR_BY_FAMILY[_fam] = EXPR_BY_FAMILY.get(_fam, ()) + (_rule,)
PART_BY_FAMILY: dict = {}
for _rule in PART_RULES:
    for _fam in _rule.families:
        PART_BY_FAMILY[_fam] = PART_BY_FAMILY.get(_fam, ()) + (_rule,)
PAIR_BY_FAMILY: dict = {}
for _rule in PAIR_RULES:
    for _fam in _rule.families:
        PAIR_BY_FAMILY[_fam] = PAIR_BY_FAMILY.get(_fam, ()) + (_rule,)
del _rule, _fam
ALL_NEW_RULES = RULES + PAIR_RULES + PART_RULES + EXPR_RULES
