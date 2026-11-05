"""GCSE maths variety plan, Phase 3 batch C2: harder kinds that replace the last tier echoes (docs/GCSE_MATHS_VARIETY.md
section 23). Probability and ratio in the difficult tier, graphs in the intermediate and difficult tiers, one
statistics kind (frequency density) so the median class can move down to the intermediate tier.

Same shape as ``maths_variety_c``: every generator returns ``(question, solution, hint, marks, answer)`` for its topic's
``*_problem_from_output`` wrapper, records the inputs the pupil is given (``record(...)``, after any drawing record),
and is re-solved by ``scripts/gcse_verify/solvers_variety_c2.py``. The topic modules import this module lazily when they
build their pools, so it never imports them back.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from generators.gcse.maths_variety_a import _frac_text, _num_text
from generators.gcse.maths_variety_c import _Axes, _br, _fraction, _line_eq, _num, _pair, _prob, _sign_text, _text
from generators.shared.rounding import fmt_dp
from generators.shared.verify_hook import record


def _dec(value):
    """A decimal probability answer (exact text) with the probability form."""
    return {'type': 'number', 'value': _text(value), 'form': 'probability'}


def _ratio(a, b, form=None):
    return {'type': 'ratio', 'a': int(a), 'b': int(b), **({'form': form} if form else {})}


def _d(x):
    """A decimal as it is printed (0.3, 0.45), from a Fraction."""
    return _num_text(Fraction(x))


def _n(count, colour, item):
    """'1 lemon sweet', '3 red counters'."""
    return f'{count} {colour} {item if count != 1 else item[:-1]}'


def _frac_tex(f):
    f = Fraction(f)
    return str(f.numerator) if f.denominator == 1 else f'{f.numerator}/{f.denominator}'


def _mx(m, var='x'):
    """A coefficient as a pupil writes it: '3x', 'x', '-x' (never '1x')."""
    return _sign_text(m, 0, var)


def _prod(m, x):
    """m × x in a worked line: '3 × (-2)', '(-2)' when m is 1, '-(-2)' or '-3' when m is -1 (never '1 × 3')."""
    if m == 1:
        return _br(x)
    if m == -1:
        return f'−{_br(x)}' if x < 0 else f'-{x}'
    return f'{m} × {_br(x)}'


def _sub_line(m, x, y, c):
    """'Substitute (3, 5) into y = 2x + c: 5 = 2 × 3 + c = 6 + c, so c = -1.' (one step fewer when m is ±1)."""
    head = f'Substitute ({x}, {y}) into y = {_mx(m)} + c: {y} = {_prod(m, x)} + c'
    if abs(m) != 1 or x < 0:
        head += f' = {m * x} + c'
    return head + f', so c = {c}.'


# ─────────────────────────────────────────────────────────────────────────────
# Probability (difficult)
# ─────────────────────────────────────────────────────────────────────────────

_BAGS = [('counters', 'red', 'blue'), ('sweets', 'orange', 'lemon'), ('marbles', 'green', 'white'), ('beads', 'black', 'silver')]


def gcse_prob_counters_algebraic():
    """Difficult: the number of counters from P(both red) without replacement (a quadratic in the total)."""
    item, c1, c2 = random.choice(_BAGS)
    while True:
        n = random.randint(6, 16)
        r = random.randint(2, n - 2)
        p = Fraction(r * (r - 1), n * (n - 1))
        # the number of blue counters must not be a printed number, nor the slip values a hint names
        blue = n - r
        if p.denominator > 60 or blue in (r, p.numerator, p.denominator) or n in (p.numerator, p.denominator):
            continue
        # the "with replacement" slip (r/n)^2 = p gives n = r / sqrt(p); it must not land on the key
        sq = r * r / p
        if sq.denominator == 1 and math.isqrt(int(sq)) ** 2 == int(sq) and math.isqrt(int(sq)) - r == blue:
            continue
        break
    big = r * (r - 1) * p.denominator // p.numerator       # n(n - 1)
    q = (f'A bag contains only {c1} {item} and {c2} {item}. There are {_n(r, c1, item)}. '
         f'Two {item} are taken from the bag at random, without replacement. '
         f'The probability that both {item} are {c1} is {_frac_tex(p)}. '
         f'How many {c2} {item} are in the bag?')
    s = (f'Let the bag hold n {item} altogether.<br>'
         f'P(both {c1}) = {r}/n × {r - 1}/(n − 1) = {r * (r - 1)}/(n(n − 1)), and this equals {_frac_tex(p)}.<br>'
         f'So n(n − 1) = {r * (r - 1)} × {p.denominator}{"" if p.numerator == 1 else f"/{p.numerator}"} = {big}, which gives n² − n − {big} = 0.<br>'
         f'(n − {n})(n + {n - 1}) = 0, so n = {n} (a count cannot be negative).<br>'
         f'{c2.capitalize()} {item}: {n} − {r} = <strong>{blue}</strong>.')
    hint = ('Call the total n. The first pick is that colour with probability r/n, and the second r − 1 over n − 1. '
            'Set the product equal to the probability given and solve for n.')
    record('prob_counters_algebraic', r=r, p_num=p.numerator, p_den=p.denominator)
    return q, s, hint, 5, _num(blue)


def gcse_prob_independent_union():
    """Difficult: independent events given as decimals; P(A or B) or P(exactly one of them)."""
    while True:
        pa = Fraction(random.randint(1, 9), 10)
        pb = Fraction(random.randint(1, 9), 10)
        if pa == pb:
            continue
        both = pa * pb
        union = pa + pb - both
        one = pa + pb - 2 * both
        if union >= 1 or both in (pa, pb) or one in (pa, pb) or union in (pa, pb):
            continue
        break
    ask = random.choice(['union', 'exactly_one'])
    scene = random.choice([
        ('A', 'B', 'A and B are independent events.'),
        ('A', 'B', 'Two events, A and B, are independent.'),
    ])
    a, b, intro = scene
    key = union if ask == 'union' else one
    q = (f'{intro} P({a}) = {_d(pa)} and P({b}) = {_d(pb)}. '
         + (f'Find P({a} or {b}).' if ask == 'union' else f'Find the probability that exactly one of {a} and {b} happens.'))
    s = (f'Independent events: P({a} and {b}) = P({a}) × P({b}) = {_d(pa)} × {_d(pb)} = {_d(both)}.<br>'
         + (f'P({a} or {b}) = P({a}) + P({b}) − P({a} and {b}) = {_d(pa)} + {_d(pb)} − {_d(both)} = <strong>{_d(union)}</strong>.'
            if ask == 'union' else
            f'Exactly one happens when {a} happens without {b}, or {b} without {a}:<br>'
            f'P({a} only) = {_d(pa)} − {_d(both)} = {_d(pa - both)}, P({b} only) = {_d(pb)} − {_d(both)} = {_d(pb - both)}.<br>'
            f'P(exactly one) = {_d(pa - both)} + {_d(pb - both)} = <strong>{_d(one)}</strong>.'))
    hint = ('For independent events P(A and B) is the product. "A or B" includes both happening, so take the overlap away '
            'once; "exactly one" takes it away twice.')
    record('prob_independent_union', pa=_d(pa), pb=_d(pb), ask=ask)
    return q, s, hint, 3, _dec(key)


def gcse_prob_three_same_colour():
    """Difficult: three counters without replacement, P(all the same colour) or P(all different, three colours)."""
    item, c1, c2 = random.choice(_BAGS)
    while True:
        r, b = random.randint(3, 8), random.randint(3, 8)
        n = r + b
        if n < 7 or r == b:
            continue
        hits = r * (r - 1) * (r - 2) + b * (b - 1) * (b - 2)
        total = n * (n - 1) * (n - 2)
        p = Fraction(hits, total)
        if p.denominator > 200:
            continue
        break
    q = (f'A bag contains {_n(r, c1, item)} and {_n(b, c2, item)}. Three {item} are taken from the bag at random, '
         f'without replacement. Find the probability that all three {item} are the same colour.')
    last = f'{hits}/{total} = <strong>{_frac_tex(p)}</strong>.' if math.gcd(hits, total) > 1 else f'<strong>{hits}/{total}</strong>.'
    s = (f'All {c1}: {r}/{n} × {r - 1}/{n - 1} × {r - 2}/{n - 2} = {r * (r - 1) * (r - 2)}/{total}.<br>'
         f'All {c2}: {b}/{n} × {b - 1}/{n - 1} × {b - 2}/{n - 2} = {b * (b - 1) * (b - 2)}/{total}.<br>'
         f'Same colour is one or the other, so add: ({r * (r - 1) * (r - 2)} + {b * (b - 1) * (b - 2)})/{total} = {last}')
    hint = (f'Work out P(all {c1}) and P(all {c2}) as products of three fractions, with one fewer {item[:-1]} to choose '
            'from each time, then add the two results.')
    record('prob_three_same', r=r, b=b)
    return q, s, hint, 4, _prob(hits, total)


_TWO_DAY = [
    ('it rains', 'rain', 'Monday', 'Tuesday'),
    ('the bus is late', 'late', 'Monday', 'Tuesday'),
    ('Mia is late for school', 'late', 'Thursday', 'Friday'),
]


def gcse_prob_two_day_dependent():
    """Difficult: a two-stage event in words with a conditional second stage; P(exactly one day) or P(at least one day)."""
    event, short, day1, day2 = random.choice(_TWO_DAY)
    while True:
        p1 = Fraction(random.randint(1, 8), 10)
        p_given = Fraction(random.randint(1, 9), 10)
        p_not_given = Fraction(random.randint(1, 9), 10)
        if p_given == p_not_given or p_given == p1 or p_not_given == p1:
            continue
        both = p1 * p_given
        first_only = p1 * (1 - p_given)
        second_only = (1 - p1) * p_not_given
        exactly_one = first_only + second_only
        at_least = both + exactly_one
        printed = {p1, p_given, p_not_given}
        if exactly_one in printed or at_least in printed or exactly_one == at_least or both in printed:
            continue
        # the slips the hint rules name must not be printed numbers either
        if (p1 * p_not_given) in printed or (first_only + second_only + both) in printed:
            continue
        break
    ask = random.choice(['exactly_one', 'at_least_one'])
    key = exactly_one if ask == 'exactly_one' else at_least
    q = (f'The probability that {event} on {day1} is {_d(p1)}. '
         f'If {event} on {day1}, the probability that {event} on {day2} is {_d(p_given)}. '
         f'If {event.replace("is late", "is not late").replace("it rains", "it does not rain")} on {day1}, '
         f'the probability that {event} on {day2} is {_d(p_not_given)}. '
         + (f'Find the probability that {event} on exactly one of the two days.' if ask == 'exactly_one' else
            f'Find the probability that {event} on at least one of the two days.'))
    s = (f'Think of a tree diagram with {day1} first, then {day2}.<br>'
         f'{day1} yes, {day2} no: {_d(p1)} × {_d(1 - p_given)} = {_d(first_only)}.<br>'
         f'{day1} no, {day2} yes: {_d(1 - p1)} × {_d(p_not_given)} = {_d(second_only)}.<br>'
         + (f'Exactly one day: {_d(first_only)} + {_d(second_only)} = <strong>{_d(exactly_one)}</strong>.' if ask == 'exactly_one' else
            f'Both days: {_d(p1)} × {_d(p_given)} = {_d(both)}.<br>'
            f'At least one day: {_d(first_only)} + {_d(second_only)} + {_d(both)} = <strong>{_d(at_least)}</strong> '
            f'(or 1 − P(neither) = 1 − {_d(1 - p1)} × {_d(1 - p_not_given)}).'))
    hint = ('Draw a tree diagram. The second-day probability depends on what happened on the first day, so use the '
            'matching branch, then add the probabilities of the outcomes that fit.')
    record('prob_two_day', p1=_d(p1), p_given=_d(p_given), p_not_given=_d(p_not_given), ask=ask)
    return q, s, hint, 4, _dec(key)


def gcse_prob_trials_needed():
    """Difficult: the smallest number of trials for P(at least one success) to pass a threshold."""
    scene, verb, noun, win = random.choice([
        ('A biased coin lands on heads with probability {p}.', 'the coin be flipped', 'flips', 'a head'),
        ('A spinner lands on red with probability {p}.', 'the spinner be spun', 'spins', 'a red'),
        ('Each time Jo serves, the probability that the serve is an ace is {p}.', 'Jo serve', 'serves', 'an ace'),
    ])
    while True:
        p = Fraction(random.choice([1, 2, 3, 4]), 10) if random.random() < 0.7 else Fraction(1, random.choice([4, 5, 6, 8]))
        target = random.choice([Fraction(8, 10), Fraction(9, 10), Fraction(95, 100), Fraction(99, 100)])
        n = 1
        while (1 - p) ** n > 1 - target:
            n += 1
        if 3 <= n <= 25:
            break
    pt = _frac_tex(p) if p.denominator not in (2, 5, 10, 20) else _d(p)
    tt = _d(target)
    q = (f'{scene.format(p=pt)} How many times must {verb} so that the probability of at least one {win.split()[-1]} '
         f'is more than {tt}? Give the smallest number of {noun}.')
    q_not = 1 - p
    qn = _frac_tex(q_not) if q_not.denominator not in (2, 5, 10, 20) else _d(q_not)
    rows = []
    for k in range(max(1, n - 2), n + 1):
        v = 1 - q_not ** k
        rows.append(f'{k} {noun}: 1 − ({qn})<sup>{k}</sup> = {fmt_dp(float(v), 4)}')
    s = (f'P(no {win.split()[-1]} in n {noun}) = ({qn})ⁿ, so P(at least one) = 1 − ({qn})ⁿ.<br>'
         + '<br>'.join(rows) + '<br>'
         f'The first number of {noun} that takes the probability above {tt} is <strong>{n}</strong>.')
    hint = ('P(at least one) = 1 − P(none). Work out 1 − (1 − p)ⁿ for n = 1, 2, 3, ... until it passes the target.')
    record('prob_trials_needed', p=_frac_tex(p), target=_d(target))
    return q, s, hint, 4, _num(n)


def gcse_prob_which_bag():
    """Difficult: two bags, a bag chosen at random then a counter; given the colour, which bag was it (reverse conditional)."""
    item, c1, c2 = random.choice(_BAGS)
    while True:
        n1, n2 = random.randint(4, 10), random.randint(4, 10)
        r1, r2 = random.randint(1, n1 - 1), random.randint(1, n2 - 1)
        pa, pb = Fraction(r1, n1), Fraction(r2, n2)
        if pa == pb:
            continue
        joint_a, joint_b = pa / 2, pb / 2
        key = joint_a / (joint_a + joint_b)
        naive = Fraction(r1, r1 + r2)
        if key.denominator > 60 or key == naive or key == joint_a or key in (pa, pb):
            continue
        break
    q = (f'Bag A contains {_n(r1, c1, item)} and {_n(n1 - r1, c2, item)}. Bag B contains {_n(r2, c1, item)} and {_n(n2 - r2, c2, item)}. '
         f'A bag is chosen at random and one of the {item} in it is taken at random. '
         f'Given that the {item[:-1]} taken is {c1}, find the probability that it came from bag A.')
    s = (f'Each bag is chosen with probability 1/2.<br>'
         f'P(bag A and {c1}) = 1/2 × {r1}/{n1} = {_frac_tex(joint_a)}; P(bag B and {c1}) = 1/2 × {r2}/{n2} = {_frac_tex(joint_b)}.<br>'
         f'P({c1}) = {_frac_tex(joint_a)} + {_frac_tex(joint_b)} = {_frac_tex(joint_a + joint_b)}.<br>'
         f'P(bag A | {c1}) = P(bag A and {c1}) ÷ P({c1}) = {_frac_tex(joint_a)} ÷ {_frac_tex(joint_a + joint_b)} = '
         f'<strong>{_frac_tex(key)}</strong>.')
    hint = ('The colour taken is the condition: divide the probability of "bag A and that colour" by the probability of '
            'that colour from either bag.')
    record('prob_which_bag', r1=r1, n1=n1, r2=r2, n2=n2, derived=('n1', 'n2'))
    return q, s, hint, 4, _prob(key.numerator, key.denominator)


# ─────────────────────────────────────────────────────────────────────────────
# Ratio and proportion (difficult)
# ─────────────────────────────────────────────────────────────────────────────

_PAIRS = [('Amy', 'Ben'), ('Priya', 'Tom'), ('Leo', 'Zara'), ('Sam', 'Ravi')]


def gcse_ratio_ages():
    """Difficult: ages in one ratio now and another in n years' time; find an age now."""
    a_name, b_name = random.choice(_PAIRS)
    while True:
        a, b = random.randint(1, 6), random.randint(1, 9)
        c, d = random.randint(1, 9), random.randint(1, 9)
        n = random.choice([2, 3, 4, 5, 6, 8, 10, 12])
        if math.gcd(a, b) != 1 or math.gcd(c, d) != 1 or a >= b or c >= d or Fraction(a, b) >= Fraction(c, d):
            continue
        # ages a t and b t; (a t + n) / (b t + n) = c / d  ->  t (a d - b c) = n (c - d)  ->  t = n (d - c) / (b c - a d)
        den = b * c - a * d
        if den <= 0:
            continue
        t = Fraction(n * (d - c), den)
        if t.denominator != 1 or t < 1:
            continue
        t = int(t)
        age_a, age_b = a * t, b * t
        if age_a < 2 or age_b > 70 or age_a in (a, b, c, d, n) or age_b in (a, b, c, d, n) or age_a + n in (c, d):
            continue
        break
    ask = random.choice(['younger', 'older'])
    key = age_a if ask == 'younger' else age_b
    q = (f'The ages of {a_name} and {b_name} are in the ratio {a} : {b}. In {n} years\' time their ages will be in the '
         f'ratio {c} : {d}. How old is {a_name if ask == "younger" else b_name} now?')
    at, bt = _mx(a, 't'), _mx(b, 't')
    s = (f'Let the ages now be {at} and {bt}.<br>'
         f'In {n} years: ({at} + {n}) : ({bt} + {n}) = {c} : {d}, so {d}({at} + {n}) = '
         + (f'{c}({bt} + {n})' if c != 1 else f'{bt} + {n}') + '.<br>'
         f'{_mx(a * d, "t")} + {d * n} = {_mx(b * c, "t")} + {c * n}, so '
         + (f'{_mx(den, "t")} = {n * (d - c)} and t = {t}' if den != 1 else f't = {t}') + '.<br>'
         + (f'{a_name} is {a} × {t} = {age_a}' if a != 1 else f'{a_name} is {age_a}')
         + f' and {b_name} is {b} × {t} = {age_b}. '
         f'Answer: <strong>{key}</strong>.')
    hint = ('Write the ages now as multiples of the first ratio, add the years to each, and set the new pair equal to '
            'the second ratio to find the multiplier.')
    record('ratio_ages', a=a, b=b, n=n, c=c, d=d, ask=ask)
    return q, s, hint, 4, _num(key)


def gcse_ratio_fraction_of_groups():
    """Difficult: a fraction of a group in each of two sub-groups; the fraction (or ratio) of the whole."""
    scene = random.choice([
        ('In a class', 'class', 'girls', 'boys', 'walk to school'),
        ('In a club', 'club', 'adults', 'children', 'play tennis'),
        ('On a school trip', 'group', 'Year 10 pupils', 'Year 11 pupils', 'brought a packed lunch'),
    ])
    intro, whole, g1, g2, does = scene
    while True:
        f1 = Fraction(random.randint(1, 5), random.choice([2, 3, 4, 5, 6, 8]))
        if f1 >= 1 or f1.denominator == 1:
            continue
        s1 = Fraction(1, random.choice([2, 3, 4, 5, 6])) * random.choice([1, 2, 3])
        s2 = Fraction(1, random.choice([2, 3, 4, 5, 6])) * random.choice([1, 2, 3])
        if s1 >= 1 or s2 >= 1 or s1 == s2:
            continue
        total = f1 * s1 + (1 - f1) * s2
        if total.denominator > 60 or total in (f1, s1, s2, 1 - f1) or total == s1 + s2:
            continue
        break
    q = (f'{intro}, {_frac_tex(f1)} of the people are {g1} and the rest are {g2}. '
         f'{_frac_tex(s1)} of the {g1} and {_frac_tex(s2)} of the {g2} {does}. '
         f'What fraction of the whole {whole} {does}?')
    s = (f'{g1.capitalize()} who {does}: {_frac_tex(f1)} × {_frac_tex(s1)} = {_frac_tex(f1 * s1)} of the {whole}.<br>'
         f'{g2.capitalize()} are 1 − {_frac_tex(f1)} = {_frac_tex(1 - f1)} of the {whole}, so {g2} who {does}: '
         f'{_frac_tex(1 - f1)} × {_frac_tex(s2)} = {_frac_tex((1 - f1) * s2)}.<br>'
         f'Altogether: {_frac_tex(f1 * s1)} + {_frac_tex((1 - f1) * s2)} = <strong>{_frac_tex(total)}</strong>.')
    hint = ('Find the fraction of the whole group in each part first: multiply the fraction of the part by the fraction '
            'within it, then add the two.')
    record('ratio_fraction_groups', f1=_frac_tex(f1), s1=_frac_tex(s1), s2=_frac_tex(s2))
    return q, s, hint, 4, _fraction(total)


def gcse_ratio_percent_more():
    """Difficult: share an amount so one person gets p% more than the other."""
    a_name, b_name = random.choice(_PAIRS)
    while True:
        p = random.choice([10, 20, 25, 30, 40, 50, 60, 75, 80])
        # amounts: B = t, A = t (1 + p/100); total = t (2 + p/100); choose t so that both are whole pounds
        t = random.choice([20, 30, 40, 50, 60, 80, 100, 120, 150, 200])
        a_amt = Fraction(t * (100 + p), 100)
        if a_amt.denominator != 1:
            continue
        a_amt = int(a_amt)
        total = t + a_amt
        if total > 2000 or total in (p, t, a_amt) or t == p or a_amt == p:
            continue
        break
    ask = random.choice(['more', 'less'])
    key = a_amt if ask == 'more' else t
    q = (f'{a_name} and {b_name} share £{total} so that {a_name} gets {p}% more than {b_name}. '
         f'How much does {a_name if ask == "more" else b_name} get?')
    s = (f'If {b_name} gets 100 parts, {a_name} gets {100 + p} parts, so the ratio {a_name} : {b_name} is {100 + p} : 100 '
         f'= {(100 + p) // math.gcd(100 + p, 100)} : {100 // math.gcd(100 + p, 100)}.<br>'
         f'That is {(200 + p) // math.gcd(100 + p, 100)} parts for £{total}, so one part is '
         f'£{_text(Fraction(total * math.gcd(100 + p, 100), 200 + p))}.<br>'
         f'{a_name}: £{a_amt}; {b_name}: £{t}. Answer: <strong>£{key}</strong>.')
    hint = ('"p% more" means the ratio is (100 + p) : 100. Share the total in that ratio.')
    record('ratio_percent_more', total=total, p=p, ask=ask)
    return q, s, hint, 3, _num(key)


def gcse_ratio_three_part_difference():
    """Difficult: a : b and b : c combined, with a difference between two shares; find a share or the total."""
    while True:
        a, b1 = random.randint(1, 6), random.randint(1, 6)
        b2, c = random.randint(1, 6), random.randint(1, 6)
        if math.gcd(a, b1) != 1 or math.gcd(b2, c) != 1 or a == b1 or b2 == c:
            continue
        lcm = b1 * b2 // math.gcd(b1, b2)
        A, B, C = a * lcm // b1, lcm, c * lcm // b2
        if A == C or max(A, B, C) > 40:
            continue
        diff = abs(C - A)
        t = random.choice([2, 3, 4, 5, 6, 8, 10])
        amounts = (A * t, B * t, C * t)
        gap = diff * t
        if gap in (a, b1, b2, c) or B * t in (a, b1, b2, c, gap) or sum(amounts) in (gap,):
            continue
        break
    ask = random.choice(['B', 'total'])
    big, small = ('C', 'A') if C > A else ('A', 'C')
    key = B * t if ask == 'B' else sum(amounts)
    q = (f'Some money is shared between A, B and C. The ratio of A\'s share to B\'s share is {a} : {b1}, '
         f'and the ratio of B\'s share to C\'s share is {b2} : {c}. {big} gets £{gap} more than {small}. '
         + ('How much does B get?' if ask == 'B' else 'How much money is shared altogether?'))
    s = (f'Make the B parts match: A : B = {a} : {b1}' + (f' = {A} : {B}' if (A, B) != (a, b1) else '')
         + f' and B : C = {b2} : {c}' + (f' = {B} : {C}' if (B, C) != (b2, c) else '')
         + f', so A : B : C = {A} : {B} : {C}.<br>'
         f'{big} has {max(A, C)} − {min(A, C)} = {diff} {"part" if diff == 1 else "parts"} more than {small}, '
         f'and that is £{gap}, so one part is £{t}.<br>'
         + (f'B: {B} × £{t} = <strong>£{B * t}</strong>.' if ask == 'B' else
            f'Total: ({A} + {B} + {C}) × £{t} = {A + B + C} × £{t} = <strong>£{sum(amounts)}</strong>.'))
    hint = ('Scale both ratios so B has the same number of parts in each, then use the difference in parts between '
            'the two people named to find what one part is worth.')
    record('ratio_three_part_difference', a=a, b1=b1, b2=b2, c=c, gap=gap, ask=ask)
    return q, s, hint, 4, _num(key)


def gcse_ratio_algebraic_parts():
    """Difficult: two amounts given as expressions in x are in a stated ratio; find x."""
    item, c1, c2 = random.choice(_BAGS)
    while True:
        p, q_ = random.randint(1, 6), random.randint(1, 6)
        r, s_ = random.randint(1, 6), random.randint(1, 6)
        a, b = random.randint(1, 9), random.randint(1, 9)
        if p == r or math.gcd(a, b) != 1 or a == b:
            continue
        # (p x + q) / (r x + s) = a / b  ->  b p x + b q = a r x + a s  ->  x = (a s - b q) / (b p - a r)
        den = b * p - a * r
        if den == 0:
            continue
        x = Fraction(a * s_ - b * q_, den)
        if x.denominator != 1 or x < 2 or x > 30:
            continue
        x = int(x)
        red, blue = p * x + q_, r * x + s_
        if red <= 0 or blue <= 0 or x in (p, q_, r, s_, a, b) or Fraction(red, blue) != Fraction(a, b):
            continue
        break
    q = (f'A bag contains {c1} {item} and {c2} {item}. There are {_sign_text(p, q_)} {c1} {item} and {_sign_text(r, s_)} {c2} {item}. '
         f'The ratio of {c1} {item} to {c2} {item} is {a} : {b}. Find the value of x.')
    lhs, rhs = (den, a * s_ - b * q_) if den > 0 else (-den, b * q_ - a * s_)
    s = (f'({_sign_text(p, q_)}) : ({_sign_text(r, s_)}) = {a} : {b}, so '
         + (f'{b}({_sign_text(p, q_)})' if b != 1 else _sign_text(p, q_)) + ' = '
         + (f'{a}({_sign_text(r, s_)})' if a != 1 else _sign_text(r, s_)) + '.<br>'
         f'{_mx(b * p)} + {b * q_} = {_mx(a * r)} + {a * s_}<br>'
         + (f'{_mx(lhs)} = {rhs}, so x = <strong>{x}</strong>.<br>' if lhs != 1 else f'x = <strong>{x}</strong>.<br>')
         + f'Check: {red} {c1} and {blue} {c2}, and {red} : {blue} = {a} : {b}.')
    hint = ('Write the ratio as two fractions that are equal and cross-multiply, then collect the x terms on one side.')
    record('ratio_algebraic_parts', p=p, q=q_, r=r, s=s_, a=a, b=b)
    return q, s, hint, 4, _num(x)


def gcse_ratio_expression_ratio():
    """Difficult: x : y given; find the ratio of two linear expressions in x and y."""
    while True:
        a, b = random.randint(1, 7), random.randint(1, 9)
        if a == b or math.gcd(a, b) != 1:
            continue
        p, q_ = random.randint(1, 4), random.randint(1, 4)
        r, s_ = random.randint(1, 4), random.randint(1, 4)
        if (p, q_) == (r, s_):
            continue
        top, bot = p * a + q_ * b, r * a + s_ * b
        g = math.gcd(top, bot)
        top, bot = top // g, bot // g
        if top == bot or (top, bot) in ((a, b), (b, a)) or max(top, bot) > 60:
            continue
        break
    ex1, ex2 = _sign_text(p, 0) + (f' + {q_}y' if q_ != 1 else ' + y'), _sign_text(r, 0) + (f' + {s_}y' if s_ != 1 else ' + y')
    ex1, ex2 = ex1.replace('1x', 'x'), ex2.replace('1x', 'x')
    q = f'x : y = {a} : {b}. Find the ratio ({ex1}) : ({ex2}). Give your answer in its simplest form.'
    def _terms(u, v):
        return (f'{u} × {a}' if u != 1 else str(a)) + ' + ' + (f'{v} × {b}' if v != 1 else str(b))
    s = (f'x : y = {a} : {b}, so take x = {a} and y = {b} (any pair in that ratio gives the same answer).<br>'
         f'{ex1} = {_terms(p, q_)} = {p * a + q_ * b}; {ex2} = {_terms(r, s_)} = {r * a + s_ * b}.<br>'
         f'({ex1}) : ({ex2}) = {p * a + q_ * b} : {r * a + s_ * b}'
         + (f' = <strong>{top} : {bot}</strong>.' if g > 1 else ', which is already in its simplest form: '
            f'<strong>{top} : {bot}</strong>.'))
    hint = ('Choose values of x and y in the given ratio (the simplest pair), substitute them into both expressions, '
            'and simplify the ratio of the results.')
    record('ratio_expression', a=a, b=b, p=p, q=q_, r=r, s=s_)
    return q, s, hint, 3, _ratio(top, bot, form='simplified')     # 16:42 for 8:21 is refused (review C3)


# ─────────────────────────────────────────────────────────────────────────────
# Graphs (intermediate and difficult)
# ─────────────────────────────────────────────────────────────────────────────

def _pt(x, y):
    return f'({x}, {y})'


def gcse_gra_line_through_two_points():
    """Intermediate: the equation of the straight line through two points."""
    while True:
        m = random.choice([-3, -2, -1, 1, 2, 3, 4])
        c = random.randint(-8, 8)
        x1, x2 = random.sample(range(-5, 7), 2)
        y1, y2 = m * x1 + c, m * x2 + c
        if c == 0 or abs(y1) > 20 or abs(y2) > 20 or x1 == 0 or x2 == 0 or y1 == y2:
            continue
        break
    q = f'Find the equation of the straight line that passes through the points {_pt(x1, y1)} and {_pt(x2, y2)}. Give your answer in the form y = mx + c.'
    s = (f'Gradient m = ({y2} − {_br(y1)}) ÷ ({x2} − {_br(x1)}) = {y2 - y1} ÷ {_br(x2 - x1)} = {m}.<br>'
         f'{_sub_line(m, x1, y1, c)}<br>'
         f'<strong>y = {_sign_text(m, c)}</strong>')
    hint = 'Find the gradient from the two points (change in y over change in x), then use one point to find c.'
    record('gr_line_two_points', x1=x1, y1=y1, x2=x2, y2=y2)
    return q, s, hint, 3, _line_eq(m, c)


def gcse_gra_x_intercept():
    """Intermediate: where a line crosses the x-axis."""
    while True:
        m = random.choice([-4, -3, -2, -1, 1, 2, 3, 4, 5])
        x0 = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
        c = -m * x0
        if c == 0 or abs(c) > 24 or x0 == c or x0 == m:
            continue
        break
    q = f'The straight line y = {_sign_text(m, c)} crosses the x-axis at the point P. Find the coordinates of P.'
    s = (f'On the x-axis, y = 0: 0 = {_sign_text(m, c)}, so ' + (f'{_mx(m)} = {-c} and x = {x0}' if m != 1 else f'x = {x0}') + '.<br>'
         f'P is <strong>({x0}, 0)</strong>.')
    hint = 'Every point on the x-axis has y = 0. Put y = 0 into the equation and solve for x.'
    record('gr_x_intercept', m=m, c=c)
    return q, s, hint, 2, _pair(x0, 0)


def gcse_gra_missing_coordinate():
    """Intermediate: a point with one unknown coordinate lies on a line; find the unknown."""
    while True:
        m = random.choice([-3, -2, -1, 2, 3, 4, 5])
        c = random.randint(-9, 9)
        x = random.randint(-6, 8)
        y = m * x + c
        ask = random.choice(['x', 'y'])
        if c == 0 or x == 0 or y == 0 or abs(y) > 30:
            continue
        if ask == 'x' and (x in (m, c, y) or y in (m, c)):
            continue
        if ask == 'y' and (y in (m, c, x) or x in (m, c)):
            continue
        break
    letter = random.choice(['k', 'a', 'p'])
    if ask == 'y':
        q = f'The point ({x}, {letter}) lies on the straight line y = {_sign_text(m, c)}. Find the value of {letter}.'
        s = (f'Substitute x = {x}: {letter} = {_prod(m, x)} {"+" if c >= 0 else "−"} {abs(c)}'
             + (f' = {m * x} {"+" if c >= 0 else "−"} {abs(c)}' if abs(m) != 1 or x < 0 else '')
             + f' = <strong>{y}</strong>.')
        key = y
    else:
        q = f'The point ({letter}, {y}) lies on the straight line y = {_sign_text(m, c)}. Find the value of {letter}.'
        s = (f'Substitute y = {y}: {y} = {_mx(m, letter)} {"+" if c >= 0 else "−"} {abs(c)}, so {_mx(m, letter)} = {y - c} and '
             f'{letter} = <strong>{x}</strong>.')
        key = x
    hint = 'A point lies on a line when its coordinates fit the equation. Substitute the coordinate you know and solve.'
    record('gr_missing_coordinate', m=m, c=c, ask=ask, given=x if ask == 'y' else y)
    return q, s, hint, 2, _num(key)


def gcse_gra_parallel_through_point():
    """Intermediate: the equation of the line parallel to a given line through a given point."""
    while True:
        m = random.choice([-3, -2, -1, 1, 2, 3, 4, 5])
        c1 = random.randint(-8, 8)
        x, y = random.randint(-5, 6), random.randint(-8, 10)
        c2 = y - m * x
        if c1 == 0 or c2 == 0 or c2 == c1 or x == 0 or c2 in (x, y, m) or abs(c2) > 24:
            continue
        break
    q = (f'Line L has the equation y = {_sign_text(m, c1)}. Find the equation of the line that is parallel to L and '
         f'passes through the point {_pt(x, y)}. Give your answer in the form y = mx + c.')
    s = (f'Parallel lines have the same gradient, so the gradient is {m}.<br>'
         f'{_sub_line(m, x, y, c2)}<br>'
         f'<strong>y = {_sign_text(m, c2)}</strong>')
    hint = 'Keep the gradient of the given line, then use the point to find the new value of c.'
    record('gr_parallel_through', m=m, x=x, y=y)
    return q, s, hint, 3, _line_eq(m, c2)


def _line_graph_svg(m, c, x_lo, x_hi, y_lo, y_hi, marks, *, x_label='x', y_label='y', x_step=1, y_step=None):
    y_step = y_step or (5 if y_hi - y_lo > 24 else 2 if y_hi - y_lo > 10 else 1)
    ax = _Axes(x_lo, x_hi, y_lo, y_hi, x_step, y_step, x_minor=1 if x_step > 1 else None,
               y_minor=1 if y_step > 1 else None, x_label=x_label, y_label=y_label)
    pts = [(x_lo, m * x_lo + c), (x_hi, m * x_hi + c)]
    body = ax.polyline(pts) + ax.marks(marks)
    return ax.wrap(body, 'Straight-line graph', 'A straight line drawn on labelled axes.')


def gcse_gra_gradient_from_graph():
    """Intermediate: the gradient of a drawn straight line, read through two marked points."""
    while True:
        m = Fraction(random.choice([-3, -2, -1, 1, 2, 3]), random.choice([1, 1, 1, 2]))
        c = random.randint(-4, 6)
        x1 = random.randint(0, 3)
        run = random.choice([2, 3, 4]) if m.denominator == 2 else random.choice([1, 2, 3, 4])
        if (m * run).denominator != 1:
            continue
        x2 = x1 + run
        y1, y2 = m * x1 + c, m * x2 + c
        if y1.denominator != 1 or y2.denominator != 1 or min(y1, y2) < -8 or max(y1, y2) > 14 or y1 == y2:
            continue
        if m in (y1, y2, c) or m == x2:
            continue
        break
    y1, y2 = int(y1), int(y2)
    x_lo, x_hi = min(0, x1) - 1, x2 + 2
    y_lo = min(int(m * x_lo + c), int(m * x_hi + c), y1, y2, 0) - 1
    y_hi = max(int(m * x_lo + c), int(m * x_hi + c), y1, y2, 0) + 1
    svg = _line_graph_svg(m, c, x_lo, x_hi, y_lo, y_hi, [(x1, y1), (x2, y2)])
    q = (f'The graph shows a straight line. The marked points have whole-number coordinates.<br>{svg}<br>'
         f'Work out the gradient of the line.')
    s = (f'The marked points are {_pt(x1, y1)} and {_pt(x2, y2)}.<br>'
         f'Gradient = change in y ÷ change in x = ({y2} − {_br(y1)}) ÷ ({x2} − {_br(x1)}) = {y2 - y1} ÷ {x2 - x1} = '
         f'<strong>{_text(m)}</strong>.')
    hint = 'Pick the two marked points. Gradient is the change in y divided by the change in x between them.'
    record('gr_gradient_graph', x1=x1, y1=y1, x2=x2, y2=y2, derived=('x1', 'y1', 'x2', 'y2'))    # read from the drawing
    return q, s, hint, 2, _num(m)


# (unit words the checker's unit model reads, so a pupil's "40 miles" is right and "40 km" is refused for an answer in
# miles; kilograms to pounds is left out because "pounds" reads as money)
_CONVERSIONS = [
    ('miles', 'kilometres', Fraction(8, 5), 50, 'Distance (miles)', 'Distance (kilometres)'),
    ('pounds', 'euros', Fraction(6, 5), 50, 'Pounds', 'Euros'),      # no "(£)" on an axis: the unit model reads a bracketed symbol as a currency asked for
    ('inches', 'centimetres', Fraction(5, 2), 20, 'Length (inches)', 'Length (centimetres)'),
]
_SYMBOL = {'pounds': '£', 'euros': '€'}


def _amount(value, unit):
    """'40 miles', '£40', '€48': an amount with its unit as the question writes it."""
    return f'{_SYMBOL[unit]}{value}' if unit in _SYMBOL else f'{value} {unit}'


def gcse_gra_conversion_graph():
    """Intermediate: read a conversion from a drawn straight-line conversion graph (either way)."""
    u1, u2, k, x_hi, x_label, y_label = random.choice(_CONVERSIONS)
    while True:
        x = random.randint(4, x_hi) if x_hi <= 20 else random.randrange(5, x_hi + 1, 5)      # not too close to the origin to read
        y = k * x
        if y.denominator != 1 or y == x or x == 0:
            continue
        break
    y = int(y)
    y_hi = int(k * x_hi)
    ask = random.choice(['to', 'from'])
    x_step = 5 if x_hi > 20 else 2
    y_step = 10 if y_hi > 40 else 5 if y_hi > 20 else 2
    ax = _Axes(0, x_hi, 0, y_hi, x_step, y_step, x_minor=1, y_minor=1, x_label=x_label, y_label=y_label)
    body = ax.polyline([(0, 0), (x_hi, y_hi)]) + ax.marks([(x, y)])
    # the description avoids "X to Y": the checker's unit model would read "to kilometres" as the unit asked for
    svg = ax.wrap(body, 'Conversion graph', f'A straight-line conversion graph for {u1} and {u2}.')
    # the currency is written as a symbol on the amount given and as a word in the ask ("convert £40 to euros. Give
    # your answer in euros"): the checker's unit model then asks for that currency alone, so "£48" is refused for an
    # answer in euros (a bracketed symbol, "(£)", would read as a second currency asked for; C2 review)
    q = (f'The graph can be used to convert between {u1} and {u2}. A point on the line is marked.<br>{svg}<br>'
         + (f'Use the graph to convert {_amount(x, u1)} to {u2}. Give your answer in {u2}.' if ask == 'to' else
            f'Use the graph to convert {_amount(y, u2)} to {u1}. Give your answer in {u1}.'))
    s = (f'The marked point is at ({x}, {y}): {_amount(x, u1)} is {_amount(y, u2)}.<br>'
         + (f'So {_amount(x, u1)} = <strong>{_amount(y, u2)}</strong>.' if ask == 'to' else
            f'So {_amount(y, u2)} = <strong>{_amount(x, u1)}</strong>.'))
    hint = ('Find the value on one axis, go across (or up) to the line, then read the matching value on the other axis.')
    record('gr_conversion', x=x, y=y, ask=ask, amount=x if ask == 'to' else y, derived=('y',) if ask == 'to' else ('x',))    # the other is read from the drawing
    unit_word = u2 if ask == 'to' else u1
    return q, s, hint, 2, _num(y if ask == 'to' else x, f'Enter the number of {unit_word}')


def gcse_gra_perpendicular_bisector():
    """Difficult: the equation of the perpendicular bisector of a line segment."""
    # AB has gradient ±1, ±1/2 or ±1/3, drawn evenly (the first draw gave ±1 three times in four: C2 review), so the
    # perpendicular gradient is a whole number (the linear_equation key reads decimals, not fractions) and the
    # reciprocal is more than a sign change in two draws of three; the run keeps the midpoint on whole numbers
    while True:
        m_ab = random.choice([Fraction(1), Fraction(-1), Fraction(1, 2), Fraction(-1, 2), Fraction(1, 3), Fraction(-1, 3)])
        perp = -1 / m_ab
        x1 = random.randint(-6, 6)
        run = random.choice({1: [2, 4, 6], 2: [4, 8], 3: [6]}[m_ab.denominator])
        x2 = x1 + run
        y1 = random.randint(-6, 8)
        y2 = y1 + m_ab * run
        if y2.denominator != 1 or abs(y2) > 12:
            continue
        y2 = int(y2)
        mx, my = Fraction(x1 + x2, 2), Fraction(y1 + y2, 2)
        c = my - perp * mx
        if mx.denominator != 1 or my.denominator != 1 or c.denominator != 1 or c == 0 or abs(c) > 30:
            continue
        if int(c) in (x1, y1, x2, y2) or int(perp) in (x1, y1, x2, y2):
            continue
        break
    perp, c = int(perp), int(c)
    q = (f'A is the point {_pt(x1, y1)} and B is the point {_pt(x2, y2)}. Find the equation of the perpendicular bisector '
         f'of AB. Give your answer in the form y = mx + c.')
    s = (f'Midpoint of AB: (({x1} + {_br(x2)})/2, ({y1} + {_br(y2)})/2) = ({int(mx)}, {int(my)}).<br>'
         f'Gradient of AB = ({y2} − {_br(y1)}) ÷ ({x2} − {_br(x1)}) = {y2 - y1} ÷ {run} = {_frac_tex(m_ab)}, so the '
         f'perpendicular gradient is −1 ÷ {"(" + _frac_tex(m_ab) + ")" if m_ab < 0 else _frac_tex(m_ab)} = {perp}.<br>'
         f'Through ({int(mx)}, {int(my)}): {int(my)} = {_prod(perp, int(mx))} + c'
         + (f' = {perp * int(mx)} + c' if abs(perp) != 1 or int(mx) < 0 else '') + f', so c = {c}.<br>'
         f'<strong>y = {_sign_text(perp, c)}</strong>')
    hint = ('The perpendicular bisector passes through the midpoint of AB with the negative reciprocal of the gradient '
            'of AB.')
    record('gr_perp_bisector', x1=x1, y1=y1, x2=x2, y2=y2)
    return q, s, hint, 4, _line_eq(perp, c)


# ─────────────────────────────────────────────────────────────────────────────
# Statistics (difficult)
# ─────────────────────────────────────────────────────────────────────────────

_FD_SCENES = [
    ('t', 'minutes', 'the times, t minutes, taken by some runners'),
    ('m', 'grams', 'the masses, m grams, of some apples'),
    ('h', 'cm', 'the heights, h cm, of some plants'),
]


def gcse_stats_frequency_density():
    """Difficult: a histogram with unequal classes; the frequency of a class from the height of its bar."""
    # Whole-change review C5: the other draw (frequency density from a frequency) was the intermediate calculation of
    # _stats_inter_07 and took about half of the draws; only the reverse is a Higher step, so only it is kept.
    var, unit, what = random.choice(_FD_SCENES)
    while True:
        edges = [0]
        for w in random.choice([(10, 10, 20, 40), (5, 5, 10, 20), (10, 20, 20, 50), (20, 10, 10, 40)]):
            edges.append(edges[-1] + w)
        k = random.randint(0, 3)
        width = edges[k + 1] - edges[k]
        fd = Fraction(random.choice([3, 4, 5, 6, 8, 12, 15, 16, 18, 24, 25, 32]), 10)
        freq = fd * width
        if freq.denominator != 1 or freq in (width, fd) or freq < 2:
            continue
        key = int(freq)
        break
    cls = f'{edges[k]} &lt; {var} ≤ {edges[k + 1]}'
    width_text = f'{edges[k + 1]} − {edges[k]} = {width}' if edges[k] else f'{width}'
    q = (f'A histogram shows {what}. The bar for the class {cls} has a height (frequency density) of {_text(fd)}. '
         f'Work out the frequency of this class.')
    s = (f'Frequency = frequency density × class width.<br>'
         f'The class {cls} has width {width_text}.<br>'
         f'Frequency = {_text(fd)} × {width} = <strong>{int(freq)}</strong>.')
    hint = 'On a histogram the area of a bar gives the frequency: multiply the height by the class width.'
    record('stats_frequency_density', lo=edges[k], hi=edges[k + 1], ask='frequency', freq=None, fd=_text(fd))
    return q, s, hint, 2, _num(key)
