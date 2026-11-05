"""GCSE maths variety plan, Phase 3 batch A: new practice kinds for bidmas, fdp, multiples_factors, surds, decimals,
algebra, number and ratio_proportion (docs/GCSE_MATHS_VARIETY.md sections 4 and 17).

Every generator here returns the usual practice tuple ``(question, solution, hint, marks[, answer])`` that its topic's
``*_problem_from_output`` wrapper turns into a problem. The module is self-contained on purpose (shared helpers only):
the topic modules import it when they build their practice pools, so it must never import them back.

Each variant records the inputs the pupil is given (``record(...)``) or is tagged ``@verifies('alg', task=...)``, so the
GCSE verification smoke re-solves it with an independent solver in ``scripts/gcse_verify/``.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

import sympy as sp

from generators.shared.answer_checkers import FORM_EXPANDED, FORM_FACTORISED, FORM_SIMPLEST_SURD, FORM_SIMPLIFIED
from generators.shared.rounding import fmt_dp
from generators.shared.utils import bracket_neg, coef, signed_term
from generators.shared.verify_hook import record, verifies
from models import svg_kit


# ─────────────────────────────────────────────────────────────────────────────
# Small helpers
# ─────────────────────────────────────────────────────────────────────────────

def _frac_text(f):
    """'3/4' for a Fraction (a whole number has no slash)."""
    f = Fraction(f)
    return str(f.numerator) if f.denominator == 1 else f'{f.numerator}/{f.denominator}'


def _mixed_text(f):
    """'2 1/3' for an improper fraction, '3/4' for a proper one, '5' for a whole number."""
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    whole, rem = divmod(f.numerator, f.denominator)
    if whole == 0:
        return f'{rem}/{f.denominator}'
    return f'{whole} {rem}/{f.denominator}'


def _tex_frac(f):
    """LaTeX \\dfrac for a Fraction (whole numbers plain)."""
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    return rf'\dfrac{{{f.numerator}}}{{{f.denominator}}}'


def _tex_mixed(f):
    """LaTeX mixed number, e.g. 2\\dfrac{1}{3}."""
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    whole, rem = divmod(f.numerator, f.denominator)
    if whole == 0:
        return rf'\dfrac{{{rem}}}{{{f.denominator}}}'
    return rf'{whole}\dfrac{{{rem}}}{{{f.denominator}}}'


def _num_text(x):
    """A Fraction/int as a plain decimal string without trailing zeros (exact; the value must terminate)."""
    f = Fraction(x)
    if f.denominator == 1:
        return str(f.numerator)
    d = f.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    if d != 1:
        raise ValueError(f'{f} does not terminate')
    places = 1
    while (f * 10 ** places).denominator != 1:
        places += 1
    return f'{float(f):.{places}f}'


def _fraction_answer(f):
    """Key for a fraction answer: the checker reads value, so a mixed number or an improper fraction is accepted."""
    return {'type': 'fraction', 'value': _frac_text(f)}


def _simplest_fraction_answer(f):
    """Key for "give your answer as a fraction (or mixed number) in its simplest form": an equal fraction with a common
    factor left (48/88, 6 26/60) or a decimal (0.8) is refused with the form message (whole-change review C2)."""
    return dict(_fraction_answer(f), form='simplified')


def _alg_answer(expr, format_hint=None, form=None, subject=None):
    payload = {'type': 'algebraic', 'value': str(expr)}
    if form:
        payload['form'] = form
    if format_hint:
        payload['format_hint'] = format_hint
    if subject:
        payload['subject'] = subject
    return payload


def _sym_str(expr):
    return sp.sstr(expr)


def _pair_answer(a, b, label_a, label_b, sep='and'):
    return {'type': 'number_pair', 'values': (str(a), str(b)), 'label_a': label_a, 'label_b': label_b, 'sep': sep}


def _choice(options, correct_index):
    """A 'choice' answer: options are shown as written, in the given order (no shuffle)."""
    letters = 'ABCD'
    return {'type': 'choice', 'options': [f'{letters[i]}  {t}' for i, t in enumerate(options)],
            'correct': letters[correct_index]}


def _shuffled_choice(correct, wrong):
    """Choice payload with the key at a random place."""
    opts = [correct] + list(wrong)
    random.shuffle(opts)
    return _choice(opts, opts.index(correct))


# ─────────────────────────────────────────────────────────────────────────────
# BIDMAS
# ─────────────────────────────────────────────────────────────────────────────

def gcse_bidmas_inverse_check():
    """Foundational: which calculation checks a given one (inverse operations)."""
    op = random.choice(['+', '−', '×', '÷'])
    if op == '+':
        a, b = random.randint(12, 60), random.randint(12, 60)
        c = a + b
        correct, wrong = f'{c} − {b}', [f'{c} + {b}', f'{a} × {b}', f'{c} × {b}']
        s_text = rf'Adding is undone by subtracting: {c} − {b} = {a}, which is the number we started with.'
    elif op == '−':
        b, c = random.randint(12, 60), random.randint(12, 60)
        a = b + c
        correct, wrong = f'{c} + {b}', [f'{a} + {b}', f'{c} − {b}', f'{c} × {b}']
        s_text = rf'Subtracting is undone by adding: {c} + {b} = {a}, which is the number we started with.'
    elif op == '×':
        a, b = random.randint(3, 12), random.randint(3, 12)
        c = a * b
        correct, wrong = f'{c} ÷ {b}', [f'{c} × {b}', f'{c} − {b}', f'{a} + {b}']
        s_text = rf'Multiplying is undone by dividing: {c} ÷ {b} = {a}, which is the number we started with.'
    else:
        b, c = random.randint(3, 12), random.randint(3, 12)
        a = b * c
        correct, wrong = f'{c} × {b}', [f'{c} + {b}', f'{a} − {b}', f'{a} × {b}']
        s_text = rf'Dividing is undone by multiplying: {c} × {b} = {a}, which is the number we started with.'
    q = f'Which calculation can be used to check that {a} {op} {b} = {c}?'
    s = f'{s_text}<br>The check is <strong>{correct}</strong>.'
    hint = 'A check works backwards: use the answer and the opposite operation to get back to the number you started with.'
    record('bidmas_inverse_check', a=a, op=op, b=b, c=c)
    return q, s, hint, 1, _shuffled_choice(correct, wrong)


def gcse_bidmas_missing_number():
    """Intermediate: find the missing number in a line that mixes operations."""
    form = random.choice(['add_mul', 'bracket_mul', 'mul_sub', 'sub_square'])
    if form == 'add_mul':
        a, b, x = random.randint(2, 15), random.randint(2, 9), random.randint(2, 12)
        c = a + x * b
        line = f'{a} + □ × {b} = {c}'
        nums = dict(a=a, b=b, c=c)
        steps = (f'Multiplication comes before addition, so □ × {b} must be {c} − {a} = {c - a}.<br>'
                 f'□ = {c - a} ÷ {b} = <strong>{x}</strong>.')
        hint = 'The multiplication is done first, so work backwards: undo the addition, then undo the multiplication.'
    elif form == 'bracket_mul':
        a, b, x = random.randint(2, 9), random.randint(1, 9), random.randint(2, 12)
        c = a * (x + b)
        line = f'{a} × (□ + {b}) = {c}'
        nums = dict(a=a, b=b, c=c)
        steps = (f'The bracket is worked out first, so (□ + {b}) must be {c} ÷ {a} = {c // a}.<br>'
                 f'□ = {c // a} − {b} = <strong>{x}</strong>.')
        hint = 'The bracket is done first, so work backwards: undo the multiplication, then undo the addition.'
    elif form == 'mul_sub':
        a, b, x = random.randint(2, 9), random.randint(2, 20), random.randint(3, 12)
        c = a * x - b
        line = f'{a} × □ − {b} = {c}'
        nums = dict(a=a, b=b, c=c)
        steps = (f'Multiplication comes before subtraction, so {a} × □ must be {c} + {b} = {c + b}.<br>'
                 f'□ = {c + b} ÷ {a} = <strong>{x}</strong>.')
        hint = 'Work backwards: undo the subtraction first, then undo the multiplication.'
    else:
        x = random.randint(2, 9)
        a = random.randint(max(30, x * x + 1), 90)
        c = a - x * x
        line = f'{a} − □² = {c}'
        nums = dict(a=a, c=c)
        steps = (f'The square is done before the subtraction, so □² must be {a} − {c} = {a - c}.<br>'
                 f'□ = √{a - c} = <strong>{x}</strong>.')
        hint = 'Work backwards: undo the subtraction, then take the square root (the number is positive).'
    q = f'Find the positive whole number that goes in the box.<br><strong>{line}</strong>'
    s = steps
    record('bidmas_missing', form=form, **nums)
    return q, s, hint, 2, x


def gcse_bidmas_roots_indices():
    """Intermediate: square roots and powers in a line of mixed operations."""
    r = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
    root = math.isqrt(r)
    b, c = random.randint(2, 9), random.randint(2, 5)
    p = random.choice([2, 3])
    e = random.randint(1, 15)
    sup = '²' if p == 2 else '³'
    form = random.choice(['plus', 'minus'])
    if form == 'plus':
        expr = f'√{r} + {b} × {c}{sup}'
        value = root + b * c ** p
        steps = (f'Roots and powers first: √{r} = {root} and {c}{sup} = {c ** p}.<br>'
                 f'Multiply: {b} × {c ** p} = {b * c ** p}.<br>Add: {root} + {b * c ** p} = <strong>{value}</strong>.')
    else:
        expr = f'{b * c ** p + e} − √{r} × {c}'
        value = b * c ** p + e - root * c
        steps = (f'Root first: √{r} = {root}.<br>Multiply: {root} × {c} = {root * c}.<br>'
                 f'Subtract: {b * c ** p + e} − {root * c} = <strong>{value}</strong>.')
    q = f'Calculate {expr}'
    hint = 'Brackets, then indices and roots, then multiply and divide, then add and subtract.'
    if form == 'plus':
        record('bidmas_root_mix', derived=('p',), kind=0, r=r, b=b, c=c, p=p, a=0)
    else:
        record('bidmas_root_mix', derived=('p',), kind=1, r=r, b=0, c=c, p=1, a=b * c ** p + e)
    return q, steps, hint, 2, value


def gcse_bidmas_fraction_bar():
    """Intermediate: a fraction bar acts as brackets round the top and the bottom."""
    bottom = random.randint(2, 6)
    e = random.randint(1, 4)
    d = e + bottom
    k = random.randint(2, 9)
    b, c = random.randint(2, 6), random.randint(2, 6)
    a = k * bottom - b * c
    while a <= 0:
        k += 1
        a = k * bottom - b * c
    top = a + b * c
    q = rf'Calculate \( \dfrac{{{a} + {b} \times {c}}}{{{d} - {e}}} \)'
    s = (rf'The fraction bar means the top and the bottom are each worked out first.<br>'
         rf'Top: {a} + {b} × {c} = {a} + {b * c} = {top}.<br>Bottom: {d} − {e} = {bottom}.<br>'
         rf'Divide: {top} ÷ {bottom} = <strong>{k}</strong>.')
    hint = 'Work out the top line and the bottom line separately, using BIDMAS in each, then divide.'
    record('bidmas_fraction_bar', a=a, b=b, c=c, d=d, e=e)
    return q, s, hint, 3, k


def gcse_bidmas_neg_indices_division():
    """Difficult: negative numbers, indices and division in one line."""
    p = random.choice([2, 3])
    n = random.randint(2, 5)
    m = random.choice([d for d in range(2, n ** p + 1) if n ** p % d == 0 and d != n ** p])
    c, d = random.randint(2, 6), random.randint(2, 4)
    sup, supd = ('²' if p == 2 else '³'), '²'
    value = ((-n) ** p) // m + c * (-d) ** 2
    expr = f'(−{n}){sup} ÷ {m} + {c} × (−{d}){supd}'
    first = (-n) ** p
    q = f'Calculate {expr}'
    s = (rf'Indices first: (−{n}){sup} = {first} and (−{d}){supd} = {d * d}.<br>'
         rf'Then divide and multiply: {first} ÷ {m} = {first // m} and {c} × {d * d} = {c * d * d}.<br>'
         rf'Add: {first // m} + {c * d * d} = <strong>{value}</strong>.')
    hint = 'The brackets mean the negative sign is squared or cubed too. Do the indices, then divide and multiply, then add.'
    record('arith', expr=expr)
    return q, s, hint, 3, value


def gcse_bidmas_insert_brackets():
    """Difficult: where do the brackets go to make the statement true?"""
    while True:
        a, b, c, d = random.randint(2, 9), random.randint(2, 9), random.randint(2, 9), random.randint(1, 8)
        target = (a + b) * c - d
        plain_value = a + b * c - d
        other_values = {plain_value, a + b * (c - d), (a + b) * (c - d)}
        if target not in other_values and c > d and len({target} | other_values) == 4:
            break
    unbracketed = f'{a} + {b} × {c} − {d}'
    correct = f'({a} + {b}) × {c} − {d}'
    wrong = [f'{a} + ({b} × {c}) − {d}', f'{a} + {b} × ({c} − {d})', f'({a} + {b}) × ({c} − {d})']
    q = f'Brackets can be put in this calculation to make the statement correct. Which version is correct?<br><strong>{unbracketed} = {target}</strong>'
    s = (rf'Try each version. ({a} + {b}) × {c} − {d} = {a + b} × {c} − {d} = {(a + b) * c} − {d} = <strong>{target}</strong>.<br>'
         rf'The others give {plain_value}, {a + b * (c - d)} and {(a + b) * (c - d)}.')
    hint = 'Work out each version in BIDMAS order and see which one equals the number on the right.'
    record('bidmas_brackets', a=a, b=b, c=c, d=d, target=target)
    return q, s, hint, 3, _shuffled_choice(correct, wrong)


def gcse_bidmas_fraction_bar_negatives():
    """Difficult: a fraction bar with a negative power on top and a power underneath."""
    while True:
        p = random.choice([2, 3])
        n = random.randint(2, 4)
        a = random.randint(1, 20)
        e = random.randint(2, 4)
        b = random.randint(e * e + 2, e * e + 6)        # review: the bottom is never 1 (it was a third of the draws)
        bottom = b - e * e
        top = a - (-n) ** p
        if top % bottom == 0 and top != 0:
            break
    k = top // bottom
    q = rf'Calculate \( \dfrac{{{a} - (-{n})^{p}}}{{{b} - {e}^{2}}} \)'
    s = (rf'Top: (−{n})<sup>{p}</sup> = {(-n) ** p}, so {a} − ({(-n) ** p}) = {a} + {-(-n) ** p if (-n) ** p < 0 else -(-n) ** p} = {top}.<br>'
         if (-n) ** p < 0 else
         rf'Top: (−{n})<sup>{p}</sup> = {(-n) ** p}, so {a} − {(-n) ** p} = {top}.<br>')
    s += rf'Bottom: {e}<sup>2</sup> = {e * e}, so {b} − {e * e} = {bottom}.<br>Divide: {top} ÷ {bottom} = <strong>{k}</strong>.'
    hint = 'Work out the top and the bottom separately. Subtracting a negative number adds a positive one.'
    record('bidmas_fraction_bar_neg', a=a, n=n, p=p, b=b, e=e)
    return q, s, hint, 3, k


def gcse_bidmas_substitute_negatives():
    """Difficult: substitute negative numbers into an expression with a power."""
    a_val = random.choice([-5, -4, -3, -2])
    b_val = random.choice([-6, -4, -3, 2, 3, 5])
    k1, k2 = random.randint(2, 4), random.randint(2, 6)
    expr = rf'{k1}a^2 - {k2}b'
    value = k1 * a_val ** 2 - k2 * b_val
    q = rf'Work out the value of \( {expr} \) when \( a = {a_val} \) and \( b = {b_val} \).'
    taken = f'({k2 * b_val})' if b_val < 0 else f'{k2 * b_val}'      # review: "- (25)" for a positive b
    s = (rf'Substitute: \( {k1}({a_val})^2 - {k2}({b_val}) \)<br>'
         rf'Square first: \( ({a_val})^2 = {a_val ** 2} \)<br>'
         rf'\( {k1} \times {a_val ** 2} - {taken} = {k1 * a_val ** 2} {signed_term(-k2 * b_val)} = \boxed{{{value}}} \)')
    hint = r'Put each negative number in brackets. Square the bracket (the answer is positive), then multiply, then subtract.'
    record('bidmas_sub_neg', k1=k1, a=a_val, k2=k2, b=b_val)
    return q, s, hint, 3, value


def gcse_bidmas_decimals():
    """Difficult: BIDMAS with decimals (brackets, a square and a division)."""
    while True:
        a = random.choice([0.2, 0.4, 0.5, 0.6, 0.8, 1.5, 2.5])
        b = round(random.uniform(2.1, 6.0), 1)
        c = round(random.uniform(0.6, b - 0.6), 1)
        d = random.choice([0.2, 0.25, 0.4, 0.5])
        inner = Fraction(str(b)) - Fraction(str(c))
        value = Fraction(str(a)) * inner ** 2 / Fraction(str(d))
        # review: b and c are never whole (the question printed "(5.7 − 4.0)")
        # review C11: not x a ÷ a (multiplying and dividing by the same decimal cancels the decimal work)
        if inner != 0 and (value * 1000).denominator == 1 and Fraction(str(b)).denominator != 1 \
                and Fraction(str(c)).denominator != 1 and a != d:
            break
    expr = f'{a} × ({b} − {c})² ÷ {d}'
    inner_t = _num_text(inner)
    sq = _num_text(inner ** 2)
    prod = _num_text(Fraction(str(a)) * inner ** 2)
    q = f'Calculate {expr}'
    s = (f'Bracket: {b} − {c} = {inner_t}.<br>Square: {inner_t}² = {sq}.<br>'
         f'Multiply: {a} × {sq} = {prod}.<br>Divide: {prod} ÷ {d} = <strong>{_num_text(value)}</strong>.')
    hint = 'Brackets first, then the square, then multiply and divide from left to right.'
    record('arith', expr=expr)
    return q, s, hint, 3, float(value) if value.denominator != 1 else int(value)


# ─────────────────────────────────────────────────────────────────────────────
# Fractions, decimals and percentages (fdp)
# ─────────────────────────────────────────────────────────────────────────────

def _random_proper_fraction(dens=(2, 3, 4, 5, 6, 8, 9, 10, 12)):
    d = random.choice(dens)
    n = random.choice([k for k in range(1, d) if math.gcd(k, d) == 1])
    return n, d


def gcse_fdp_add_subtract_fractions():
    """Foundational: add or subtract two fractions with different denominators."""
    while True:
        n1, d1 = _random_proper_fraction()
        n2, d2 = _random_proper_fraction()
        op = random.choice(['+', '−'])
        f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
        if d1 == d2 or (op == '−' and f1 <= f2):
            continue
        if op == '+' and f1 + f2 >= 2:
            continue
        break
    result = f1 + f2 if op == '+' else f1 - f2
    lcm = math.lcm(d1, d2)
    a, b = n1 * (lcm // d1), n2 * (lcm // d2)
    combined = a + b if op == '+' else a - b
    q = (rf'Work out \( {_tex_frac(f1)} {op} {_tex_frac(f2)} \). '
         'Give your answer as a fraction in its simplest form.')
    # review: a fraction already over the common denominator is not rewritten, and the boxed answer is not repeated
    changed = [rf'\( \dfrac{{{n}}}{{{d}}} = \dfrac{{{m}}}{{{lcm}}} \)' for n, d, m in ((n1, d1, a), (n2, d2, b)) if d != lcm]
    last = rf'\dfrac{{{combined}}}{{{lcm}}}'
    if math.gcd(combined, lcm) == 1 and result < 1:
        last = rf'\boxed{{{last}}}'                     # already in its simplest form
    else:
        last += rf' = \boxed{{{_tex_mixed(result)}}}'
    s = (rf'Use a common denominator: the lowest common multiple of {d1} and {d2} is {lcm}.<br>'
         + (' and '.join(changed) + '.<br>' if changed else '')
         + rf'\( \dfrac{{{a}}}{{{lcm}}} {op} \dfrac{{{b}}}{{{lcm}}} = {last} \) in its simplest form.')
    hint = 'Change both fractions so they have the same denominator. Then add or subtract the numerators only.'
    record('frac_add_sub', n1=n1, d1=d1, op='+' if op == '+' else '-', n2=n2, d2=d2)
    return q, s, hint, 2, _simplest_fraction_answer(result)


def gcse_fdp_fraction_of_another():
    """Foundational: write one quantity as a fraction of another."""
    kind = random.choice(['plain', 'score', 'time'])
    if kind == 'time':
        whole_h = random.choice([2, 3, 4])
        part = random.choice([m for m in range(10, whole_h * 60, 5) if math.gcd(m, whole_h * 60) > 1])
        whole, scale = whole_h, 60
        q = f'Write {part} minutes as a fraction of {whole} hours. Give your fraction in its simplest form.'
        total = whole * 60
        step = f'{whole} hours = {total} minutes, so the fraction is {part}/{total}.'
    else:
        whole = random.choice([12, 15, 18, 20, 24, 25, 30, 32, 36, 40, 45, 48, 50, 60])
        part = random.choice([k for k in range(2, whole) if math.gcd(k, whole) > 1])
        scale = 1
        total = whole
        if kind == 'plain':
            q = f'Write {part} as a fraction of {whole}. Give your fraction in its simplest form.'
        else:
            q = (f'Maya scored {part} out of {whole} in a test. Write her score as a fraction in its simplest form.')
        step = f'The fraction is {part}/{whole}.'
    result = Fraction(part, total)
    s = (f'Put the part over the whole. {step}<br>Divide top and bottom by their highest common factor, '
         f'{math.gcd(part, total)}: <strong>{_frac_text(result)}</strong>.')
    hint = 'Write the part you have been given over the whole amount, then simplify the fraction.'
    record('fdp_fraction_of_other', derived=('scale',), part=part, whole=whole, scale=scale)
    return q, s, hint, 2, _simplest_fraction_answer(result)


def gcse_fdp_percentage_of_another():
    """Foundational: write one quantity as a percentage of another."""
    whole = random.choice([8, 20, 25, 40, 50, 80, 125, 200, 250])
    context = random.choice(['test', 'shop', 'plain'])
    top = whole * 3 // 2 if context == 'plain' else whole      # only the plain wording may have a part bigger than the whole
    part = random.choice([k for k in range(1, top) if k != whole and Fraction(k * 100, whole).denominator in (1, 2)])
    pct = Fraction(part * 100, whole)
    if context == 'test':
        q = f'Ben scored {part} out of {whole} in a test. What is his score as a percentage?'
    elif context == 'shop':
        q = f'A shop has {whole} T-shirts. {part} of them are blue. What percentage of the T-shirts are blue?'
    else:
        q = f'Write {part} as a percentage of {whole}.'
    shown = _num_text(pct)
    s = (f'Write the part over the whole: {part}/{whole}.<br>'
         f'Multiply by 100: {part} ÷ {whole} × 100 = <strong>{shown}%</strong>.')
    hint = 'Divide the part by the whole, then multiply by 100 to turn it into a percentage.'
    record('fdp_pct_of_other', part=part, whole=whole)
    return q, s, hint, 2, {'type': 'number', 'value': shown}


def _mixed_parts(maxwhole=4, dens=(2, 3, 4, 5, 6, 8)):
    w = random.randint(1, maxwhole)
    n, d = _random_proper_fraction(dens)
    return w, n, d


def gcse_fdp_multiply_divide_fractions():
    """Intermediate: multiply or divide two proper fractions."""
    while True:
        n1, d1 = _random_proper_fraction((3, 4, 5, 6, 8, 9, 10))
        n2, d2 = _random_proper_fraction((3, 4, 5, 6, 8, 9, 10))
        op = random.choice(['×', '÷'])
        f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
        result = f1 * f2 if op == '×' else f1 / f2
        if (n1, d1) != (n2, d2) and result.denominator != 1:      # review: 5/6 ÷ 1/6 = 5 asked for "a fraction"
            break
    q = (rf'Work out \( {_tex_frac(f1)} {op} {_tex_frac(f2)} \). '
         'Give your answer as a fraction in its simplest form.')
    if op == '×':
        s = (rf'Multiply the numerators and multiply the denominators: \( \dfrac{{{n1} \times {n2}}}{{{d1} \times {d2}}} '
             rf'= \dfrac{{{n1 * n2}}}{{{d1 * d2}}} = \boxed{{{_tex_mixed(result)}}} \) in its simplest form.')
        hint = 'Multiply the tops and multiply the bottoms. Cancel at the end, or before you multiply.'
    else:
        s = (rf'To divide, turn the second fraction upside down and multiply: '
             rf'\( \dfrac{{{n1}}}{{{d1}}} \times \dfrac{{{d2}}}{{{n2}}} = \dfrac{{{n1 * d2}}}{{{d1 * n2}}} '
             rf'= \boxed{{{_tex_mixed(result)}}} \) in its simplest form.')
        hint = 'Dividing by a fraction is the same as multiplying by the fraction turned upside down.'
    record('frac_mul_div', n1=n1, d1=d1, op='*' if op == '×' else '/', n2=n2, d2=d2)
    return q, s, hint, 2, _simplest_fraction_answer(result)


def gcse_fdp_mixed_add_subtract():
    """Intermediate: add or subtract mixed numbers."""
    while True:
        w1, n1, d1 = _mixed_parts()
        w2, n2, d2 = _mixed_parts()
        op = random.choice(['+', '−'])
        f1, f2 = w1 + Fraction(n1, d1), w2 + Fraction(n2, d2)
        # review: the answer is asked for as a mixed number, so it is more than 1 (2 5/6 − 2 1/3 = 1/2 was drawn)
        if d1 != d2 and (op == '+' or f1 - f2 > 1):
            break
    result = f1 + f2 if op == '+' else f1 - f2
    top1, top2 = w1 * d1 + n1, w2 * d2 + n2
    lcm = math.lcm(d1, d2)
    a, b = top1 * (lcm // d1), top2 * (lcm // d2)
    combined = a + b if op == '+' else a - b
    q = (rf'Work out \( {w1}\dfrac{{{n1}}}{{{d1}}} {op} {w2}\dfrac{{{n2}}}{{{d2}}} \). '
         'Give your answer as a mixed number in its simplest form.')
    s = (rf'Write both as improper fractions: \( \dfrac{{{top1}}}{{{d1}}} {op} \dfrac{{{top2}}}{{{d2}}} \).<br>'
         rf'Use the common denominator {lcm}: \( \dfrac{{{a}}}{{{lcm}}} {op} \dfrac{{{b}}}{{{lcm}}} = \dfrac{{{combined}}}{{{lcm}}} \).<br>'
         rf'Simplify and write as a mixed number: \( \boxed{{{_tex_mixed(result)}}} \).')
    hint = 'Change each mixed number into an improper fraction first, or work with the whole numbers and fractions separately.'
    record('frac_mixed_add_sub', w1=w1, n1=n1, d1=d1, op='+' if op == '+' else '-', w2=w2, n2=n2, d2=d2)
    return q, s, hint, 3, _simplest_fraction_answer(result)


def gcse_fdp_mixed_multiply_divide():
    """Intermediate: multiply or divide mixed numbers."""
    while True:
        w1, n1, d1 = _mixed_parts(3, (2, 3, 4, 5))
        w2, n2, d2 = _mixed_parts(3, (2, 3, 4, 5))
        op = random.choice(['×', '÷'])
        f1, f2 = w1 + Fraction(n1, d1), w2 + Fraction(n2, d2)
        result = f1 * f2 if op == '×' else f1 / f2
        # review: asked for a mixed number, so the answer is more than 1 and not whole (1 1/2 × 2 2/3 = 4 and
        # 1 1/3 ÷ 3 2/5 = 20/51 were drawn)
        if f1 != f2 and result > 1 and result.denominator != 1:
            break
    top1, top2 = w1 * d1 + n1, w2 * d2 + n2
    q = (rf'Work out \( {w1}\dfrac{{{n1}}}{{{d1}}} {op} {w2}\dfrac{{{n2}}}{{{d2}}} \). '
         'Give your answer as a mixed number in its simplest form.')
    if op == '×':
        mid = rf'\( \dfrac{{{top1}}}{{{d1}}} \times \dfrac{{{top2}}}{{{d2}}} = \dfrac{{{top1 * top2}}}{{{d1 * d2}}} \)'
    else:
        mid = (rf'\( \dfrac{{{top1}}}{{{d1}}} \times \dfrac{{{d2}}}{{{top2}}} = \dfrac{{{top1 * d2}}}{{{d1 * top2}}} \) '
               '(dividing is multiplying by the fraction turned upside down)')
    s = (rf'Write both as improper fractions: \( \dfrac{{{top1}}}{{{d1}}} \) and \( \dfrac{{{top2}}}{{{d2}}} \).<br>'
         rf'{mid}<br>Simplify and write as a mixed number: \( \boxed{{{_tex_mixed(result)}}} \).')
    hint = 'Change both mixed numbers to improper fractions before you multiply or divide. Do not multiply the whole numbers separately.'
    record('frac_mixed_mul_div', w1=w1, n1=n1, d1=d1, op='*' if op == '×' else '/', w2=w2, n2=n2, d2=d2)
    return q, s, hint, 3, _simplest_fraction_answer(result)


def gcse_fdp_simple_interest():
    """Intermediate: simple interest (the interest earned, or the total in the account)."""
    principal = random.choice([200, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500])
    rate = random.choice([1, 2, 3, 4, 5, 6, 2.5, 3.5])
    years = random.randint(2, 6)
    interest = Fraction(str(principal)) * Fraction(str(rate)) * years / 100
    ask = random.choice(['interest', 'total'])
    rate_t = _num_text(Fraction(str(rate)))
    if ask == 'interest':
        q = (f'Priya invests £{principal} at {rate_t}% simple interest per year. '
             f'How much interest does she earn in {years} years?')
        key = interest
        s = (f'Simple interest is the same every year: {rate_t}% of £{principal} = £{fmt_dp(float(Fraction(str(principal)) * Fraction(str(rate)) / 100), 2)}.<br>'
             f'Over {years} years: £{fmt_dp(float(Fraction(str(principal)) * Fraction(str(rate)) / 100), 2)} × {years} = <strong>£{fmt_dp(float(interest), 2)}</strong>.')
        hint = 'Work out the interest for one year, then multiply by the number of years. The interest is the same every year.'
    else:
        q = (f'Priya invests £{principal} at {rate_t}% simple interest per year. '
             f'How much is in the account after {years} years?')
        key = principal + interest
        s = (f'One year of interest: {rate_t}% of £{principal} = £{fmt_dp(float(Fraction(str(principal)) * Fraction(str(rate)) / 100), 2)}.<br>'
             f'Interest for {years} years: £{fmt_dp(float(interest), 2)}.<br>Total: £{principal} + £{fmt_dp(float(interest), 2)} = <strong>£{fmt_dp(float(key), 2)}</strong>.')
        hint = 'Find the interest for one year, multiply by the years, then add it to the amount invested.'
    record('fdp_simple_interest', principal=principal, rate=rate, years=years, ask=ask)
    return q, s, hint, 3, {'type': 'number', 'value': _num_text(key)}


def gcse_fdp_simple_vs_compound():
    """Difficult: how much more interest does compound give than simple interest?"""
    principal = random.choice([1000, 1500, 2000, 2500, 3000, 4000, 5000])
    rate = random.choice([2, 3, 4, 5, 6])
    years = random.choice([2, 3, 4])
    p, r = Fraction(principal), Fraction(rate, 100)
    simple = p * r * years
    compound = p * (1 + r) ** years - p
    diff = compound - simple
    shown = fmt_dp(float(diff.numerator) / diff.denominator, 2)
    q = (f'£{principal} is invested for {years} years at {rate}% per year. Work out how much more interest is earned with '
         f'compound interest than with simple interest. Give your answer to the nearest penny.')
    s = (f'Simple interest: {rate}% of £{principal} = £{fmt_dp(float(p * r), 2)} a year, so £{fmt_dp(float(simple), 2)} in {years} years.<br>'
         f'Compound interest: £{principal} × {_num_text(1 + r)}<sup>{years}</sup> = £{fmt_dp(float(p * (1 + r) ** years), 2)}, '
         f'so the interest is £{fmt_dp(float(compound), 2)}.<br>'
         f'Difference: £{fmt_dp(float(compound), 2)} − £{fmt_dp(float(simple), 2)} = <strong>£{shown}</strong> to the nearest penny.')
    hint = 'Simple interest is the same every year. For compound interest multiply by the percentage multiplier each year, then take away the amount invested.'
    record('fdp_simple_vs_compound', principal=principal, rate=rate, years=years)
    return q, s, hint, 4, {'type': 'number', 'value': shown}


# ─────────────────────────────────────────────────────────────────────────────
# Multiples and factors
# ─────────────────────────────────────────────────────────────────────────────

def _divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def _prime_power_text(p, e):
    return f'{p}<sup>{e}</sup>' if e > 1 else str(p)


def gcse_mf_list_factors():
    """Foundational: list every factor of a number."""
    n = random.choice([12, 18, 20, 24, 28, 30, 36, 40, 42, 45, 48, 50, 56, 60])
    facs = _divisors(n)
    pairs = ', '.join(f'{d} × {n // d}' for d in facs if d * d <= n)
    q = f'List all the factors of {n}, in order, smallest first.'
    s = (f'Find the factors in pairs that multiply to make {n}: {pairs}.<br>'
         f'In order: <strong>{", ".join(str(d) for d in facs)}</strong>.')
    hint = 'Start with 1 × the number, then test 2, 3, 4 and so on. Each factor you find gives you a partner.'
    record('mf_factors_list', n=n)
    return q, s, hint, 2, {'type': 'number_list', 'values': tuple(facs),
                           'format_hint': 'Write the factors in order, separated by commas'}


def gcse_mf_next_multiple():
    """Foundational: the smallest multiple of n above a given number."""
    n = random.choice([4, 6, 7, 8, 9, 11, 12, 13])
    m = random.randint(30, 150)
    if random.random() < 0.75 and m % n == 0:
        m += 1
    ans = (m // n + 1) * n
    q = f'What is the smallest multiple of {n} that is greater than {m}?'
    s = (f'{n} goes into {m} {m // n} times, with some left over. So {m // n} × {n} = {(m // n) * n} is not greater than {m}.<br>'
         f'The next multiple is {m // n + 1} × {n} = <strong>{ans}</strong>.')
    if m % n == 0:
        s = (f'{m} is itself a multiple of {n}, but the answer must be greater than {m}.<br>'
             f'The next multiple is {m // n + 1} × {n} = <strong>{ans}</strong>.')
    hint = 'Find how many times the number goes into the target, then go up to the next multiple.'
    record('mf_next_multiple', n=n, m=m)
    return q, s, hint, 2, ans


def gcse_mf_count_factors():
    """Foundational: how many factors does a number have?"""
    n = random.choice([12, 16, 18, 20, 24, 28, 30, 32, 36, 40, 45, 48, 50, 60, 64, 72])
    facs = _divisors(n)
    q = f'How many factors does {n} have?'
    s = (f'The factors of {n} are {", ".join(str(d) for d in facs)}.<br>'
         f'Counting them gives <strong>{len(facs)}</strong> factors (include 1 and {n} itself).')
    hint = 'List the factors in pairs, starting with 1 and the number itself, then count them all.'
    record('mf_factor_count', n=n)
    return q, s, hint, 2, len(facs)


def gcse_mf_prime_factor_exponents():
    """Intermediate: read the indices of a prime factorisation."""
    while True:
        k = random.choice([2, 2, 3])
        primes = sorted(random.sample([2, 3, 5, 7], k))
        exps = [random.randint(1, 4 if k == 2 else 3) for _ in primes]
        n = 1
        for p, e in zip(primes, exps):
            n *= p ** e
        if 40 <= n <= 700 and (k == 2 or n <= 700):
            break
    letters = 'abc'[:k]
    shape = ' × '.join(f'{p}<sup>{c}</sup>' for p, c in zip(primes, letters))
    q = f'{n} can be written as {shape}, where {" and ".join(letters) if k == 2 else "a, b and c"} are whole numbers. Find the values of {" and ".join(letters) if k == 2 else "a, b and c"}.'
    times = {1: 'once', 2: 'twice', 3: 'three times', 4: 'four times'}
    steps = [f'by {p} {times.get(e, f"{e} times")}' for p, e in zip(primes, exps)]      # review: "2 divides in 2 times"
    s = (f'Divide {n} by the primes in turn until you reach 1: ' + ', then '.join(steps) + '.<br>'
         f'So {n} = {" × ".join(_prime_power_text(p, e) for p, e in zip(primes, exps))}, giving '
         + ', '.join(f'{c} = <strong>{e}</strong>' for c, e in zip(letters, exps)) + '.')
    hint = 'Divide by the first prime as many times as you can, then the next prime, and count how many times each one divides.'
    p3 = primes[2] if k == 3 else 0
    record('mf_pf_exponents', n=n, p1=primes[0], p2=primes[1], p3=p3)
    from generators.shared.utils import graded_answer_number_fields
    return q, s, hint, 3, graded_answer_number_fields(exps, [f'{c} =' for c in letters])


def gcse_mf_hcf_simplify_fraction():
    """Intermediate: use the HCF to simplify a fraction."""
    while True:
        g = random.choice([3, 4, 5, 6, 7, 8, 9, 12])
        a, b = random.randint(2, 13), random.randint(3, 14)
        if a < b and math.gcd(a, b) == 1:
            break
    num, den = a * g, b * g
    q = f'Find the highest common factor of {num} and {den}. Use it to write {num}/{den} in its simplest form.'
    s = (f'The HCF of {num} and {den} is {g}.<br>Divide the top and bottom by {g}: '
         f'{num} ÷ {g} = {a} and {den} ÷ {g} = {b}.<br>The fraction is <strong>{a}/{b}</strong>.')
    hint = 'Find the biggest number that divides into both the top and the bottom, then divide both by it.'
    record('mf_hcf_fraction', a=num, b=den)
    return q, s, hint, 3, _simplest_fraction_answer(Fraction(a, b))


def gcse_mf_lcm_laps():
    """Intermediate: laps completed when two runners are next level."""
    a, b = random.choice([(12, 18), (15, 20), (8, 12), (10, 25), (6, 9), (14, 21), (16, 24), (9, 12), (20, 30), (18, 24),
                          (12, 20), (8, 14), (10, 12)])        # review: three more lap ratios (5:3, 7:4, 6:5)
    if random.random() < 0.5:
        a, b = b, a
    lcm = math.lcm(a, b)
    q = (f'Anil takes {a} minutes to run one lap of a track and Beth takes {b} minutes. They start together at the '
         f'start line. When they are next together at the start line, how many laps has each of them run?')
    s = (f'They are together again after the lowest common multiple of {a} and {b}, which is {lcm} minutes.<br>'
         f'Anil: {lcm} ÷ {a} = <strong>{lcm // a}</strong> laps. Beth: {lcm} ÷ {b} = <strong>{lcm // b}</strong> laps.')
    hint = 'Find when both of them are at the start line together, then divide that time by each lap time.'
    record('mf_laps', a=a, b=b)
    return q, s, hint, 3, _pair_answer(lcm // a, lcm // b, "Anil's laps", "Beth's laps")


def gcse_mf_multiples_count():
    """Intermediate: how many multiples of n lie between two numbers?"""
    n = random.choice([6, 7, 8, 9, 11, 12, 13])
    while True:
        lo = random.randint(20, 90)
        hi = lo + random.randint(5 * n, 12 * n)
        if lo % n and hi % n:
            break
    first, last = (lo // n + 1) * n, (hi // n) * n
    count = hi // n - lo // n
    q = f'How many multiples of {n} are there between {lo} and {hi}?'
    s = (f'The first multiple of {n} above {lo} is {first} and the last one below {hi} is {last}.<br>'
         f'From {lo // n + 1} × {n} to {hi // n} × {n} there are {hi // n} − {lo // n} = <strong>{count}</strong> multiples.')
    hint = 'Find the first multiple above the lower number and the last below the upper number, then count the steps.'
    record('mf_multiples_between', n=n, lo=lo, hi=hi)
    return q, s, hint, 3, count


def gcse_mf_square_multiplier():
    """Difficult: the smallest whole number that makes a product a perfect square."""
    s_part = random.choice([2, 3, 5, 6, 7, 10])
    t = random.choice([2, 3, 4])
    n = s_part * t * t
    pf = {}
    m = n
    d = 2
    while d * d <= m:
        while m % d == 0:
            pf[d] = pf.get(d, 0) + 1
            m //= d
        d += 1
    if m > 1:
        pf[m] = pf.get(m, 0) + 1
    shown = ' × '.join(_prime_power_text(p, e) for p, e in sorted(pf.items()))
    odd = ' and '.join(str(p) for p, e in sorted(pf.items()) if e % 2)
    q = f'Find the smallest positive whole number k so that {n}k is a square number.'
    s = (f'Write {n} as a product of prime factors: {n} = {shown}.<br>'
         f'A square number has an even power of every prime. The prime{"s" if " and " in odd else ""} {odd} '
         f'{"have" if " and " in odd else "has"} an odd power, so k = <strong>{s_part}</strong> '
         f'and {n} × {s_part} = {n * s_part} = {math.isqrt(n * s_part)}².')
    hint = 'Break the number into prime factors. Every prime in a square number appears an even number of times.'
    record('mf_square_multiplier', n=n)
    return q, s, hint, 3, s_part


def gcse_mf_factor_count_from_primes():
    """Difficult: count the factors of a number given as a product of prime powers."""
    k = random.choice([2, 3])
    primes = sorted(random.sample([2, 3, 5, 7], k))
    exps = [random.randint(1, 4 if k == 2 else 3) for _ in primes]
    while sum(exps) < 4:
        exps[random.randrange(k)] += 1
    p3 = primes[2] if k == 3 else 0
    e3 = exps[2] if k == 3 else 0
    shown = ' × '.join(_prime_power_text(p, e) for p, e in zip(primes, exps))
    count = 1
    for e in exps:
        count *= e + 1
    mult = ' × '.join(f'({e} + 1)' for e in exps)
    q = f'N = {shown}. How many factors does N have?'
    s = (f'Each factor uses each prime between 0 times and its full power: that is (power + 1) choices for each prime.<br>'
         f'{mult} = <strong>{count}</strong> factors.')
    hint = 'For each prime, count the choices for its power in a factor, including zero. Multiply the numbers of choices.'
    record('mf_factor_count_primes', p1=primes[0], a1=exps[0], p2=primes[1], a2=exps[1], p3=p3, a3=e3)
    return q, s, hint, 4, count


# ─────────────────────────────────────────────────────────────────────────────
# Surds
# ─────────────────────────────────────────────────────────────────────────────

_SURD_RADICANDS = [2, 3, 5, 6, 7, 10, 11, 13]


def _surd_text(k, r):
    """'3√5' (the 1 is not written)."""
    return f'{k}√{r}' if k != 1 else f'√{r}'


def _surd_answer(k, r):
    payload = {'type': 'surd', 'radicand': int(r), 'form': FORM_SIMPLEST_SURD}
    if k != 1:
        payload['coeff'] = int(k)
    return payload


def _simplify_root(n):
    """(k, r) with sqrt(n) = k sqrt(r) and r square-free."""
    k = 1
    for f in range(math.isqrt(n), 1, -1):
        if n % (f * f) == 0:
            k, n = f, n // (f * f)
            break
    return k, n


def gcse_surds_identify_irrational():
    """Foundational: pick the irrational number from four."""
    r = random.choice([2, 3, 5, 6, 7, 10, 11, 12, 13, 15, 18, 20, 24, 28])
    sq = random.choice([16, 25, 36, 49, 64, 81, 100, 121, 144])
    dec = random.choice(['0.75', '0.4', '2.5', '0.125', '1.6', '0.35'])
    n, d = random.choice([(2, 3), (5, 9), (4, 11), (7, 12), (1, 7), (5, 6)])
    correct = f'√{r}'
    wrong = [f'√{sq}', dec, f'{n}/{d}']
    q = 'Which of these numbers is irrational?'
    root = math.isqrt(sq)
    s = (f'An irrational number cannot be written as a fraction of two whole numbers.<br>'
         f'√{sq} = {root} and {dec} and {n}/{d} are all rational (a whole number, a terminating decimal and a fraction).<br>'
         f'√{r} is not a whole number and does not terminate or repeat, so <strong>{correct}</strong> is irrational.')
    hint = 'A rational number can be written as a fraction. Work out each square root: does it come out as a whole number?'
    record('surds_irrational', derived=('r', 'sq', 'n', 'd'), r=r, sq=sq, n=n, d=d)
    return q, s, hint, 1, _shuffled_choice(correct, wrong)


def gcse_surds_square_of_surd():
    """Foundational: square a multiple of a surd."""
    k = random.randint(2, 6)
    r = random.choice([2, 3, 5, 6, 7, 10, 11])
    q = f'Work out ({k}√{r})².'
    s = (f'Square the {k} and square the root: ({k}√{r})² = {k}² × (√{r})² = {k * k} × {r} = <strong>{k * k * r}</strong>.')
    hint = 'Both the number in front and the square root are squared. Squaring a square root gives the number inside it.'
    record('surds_square', k=k, r=r)
    return q, s, hint, 2, k * k * r


def gcse_surds_add_like():
    """Foundational: add or subtract like surds."""
    r = random.choice([2, 3, 5, 6, 7, 10])
    op = random.choice(['+', '−'])
    if op == '+':
        k1, k2 = random.randint(1, 8), random.randint(2, 8)
        k = k1 + k2
    else:
        k1 = random.randint(4, 12)
        k2 = random.randint(2, k1 - 2)
        k = k1 - k2
    q = f'Simplify {_surd_text(k1, r)} {op} {_surd_text(k2, r)}.'
    s = (f'These are like surds (both are multiples of √{r}), so add or subtract the numbers in front.<br>'
         f'{k1} {op} {k2} = {k}, so the answer is <strong>{_surd_text(k, r)}</strong>.')
    # review: the worked example never has the answer's number in front (3x + 4x = 7x when the answer was 7√r)
    example = '3x + 4x = 7x' if k != 7 else '5x − 2x = 3x'
    hint = f'Treat √{r} like a letter: {example}. The root stays the same, only the numbers in front change.'
    record('surds_add_like', k1=k1, op='+' if op == '+' else '-', k2=k2, r=r)
    return q, s, hint, 2, _surd_answer(k, r)


def gcse_surds_expand_single_bracket():
    """Intermediate: expand a surd multiplied by a bracket containing the same surd."""
    k = random.choice([1, 1, 2, 3])
    r = random.choice([2, 3, 5, 6, 7])
    a = random.randint(2, 9)
    sign = random.choice(['+', '−'])
    const, coef = k * r, k * a
    outside = _surd_text(k, r)
    q = f'Expand and simplify {outside}(√{r} {sign} {a}).'
    first = (f'{outside} × √{r} = {k} × (√{r} × √{r}) = {k} × {r} = {const}' if k != 1
             else f'√{r} × √{r} = {r}')                  # review: "1 × (√3 × √3) = 1 × 3"
    s = (f'Multiply each term in the bracket by {outside}:<br>'
         f'{first}<br>'
         f'{outside} × {a} = {coef}√{r}<br>'
         f'<strong>{const} {sign} {coef}√{r}</strong>')
    hint = f'Multiply both terms in the bracket by {outside}. Remember that √{r} × √{r} = {r}.'
    record('surds_expand_single', k=k, r=r, a=a, sign='+' if sign == '+' else '-')
    return q, s, hint, 3, {'type': 'algebraic', 'kind': 'surd_binomial', 'const': const, 'coef': coef,
                           'radicand': r, 'surd_sign': '+' if sign == '+' else '-'}


def gcse_surds_multiply_coefficients():
    """Intermediate: multiply surds that have numbers in front of them."""
    while True:
        r1, r2 = random.sample([2, 3, 5, 6, 7, 10], 2)
        k1, k2 = random.randint(2, 5), random.randint(2, 5)
        t, rem = _simplify_root(r1 * r2)
        if rem > 1:
            break
    k = k1 * k2 * t
    q = f'Simplify {k1}√{r1} × {k2}√{r2}. Give your answer in the form a√b, where b has no square factors.'
    unsimplified = f'{k1 * k2}√{r1 * r2}'
    if t > 1:
        last = f'{unsimplified} = {k1 * k2} × {t}√{rem} = <strong>{_surd_text(k, rem)}</strong>.'
    else:       # review: "10√6 = 10√6"
        last = f'{r1 * r2} has no square factor, so the answer is <strong>{unsimplified}</strong>.'
    s = (f'Multiply the numbers: {k1} × {k2} = {k1 * k2}. Multiply the roots: √{r1} × √{r2} = √{r1 * r2}.<br>' + last)
    hint = 'Multiply the numbers in front together and multiply the numbers under the roots together. Then simplify the root.'
    record('surds_multiply_coef', k1=k1, r1=r1, k2=k2, r2=r2)
    return q, s, hint, 3, _surd_answer(k, rem)


def gcse_surds_rationalise_coefficient():
    """Intermediate: rationalise a denominator that is a multiple of a surd."""
    r = random.choice([2, 3, 5, 6, 7])
    b = random.choice([2, 3, 4])
    k = random.randint(1, 5)
    while k == b:           # review C11: the answer k√r must not be the denominator b√r typed back
        k = random.randint(1, 5)
    a = b * r * k
    q = rf'Rationalise the denominator of \( \dfrac{{{a}}}{{{b}\sqrt{{{r}}}}} \). Give your answer in its simplest form.'
    s = (rf'Multiply the top and bottom by \( \sqrt{{{r}}} \):<br>'
         rf'\( \dfrac{{{a}\sqrt{{{r}}}}}{{{b}\sqrt{{{r}}} \times \sqrt{{{r}}}}} = \dfrac{{{a}\sqrt{{{r}}}}}{{{b * r}}} \)<br>'
         rf'Divide top and bottom by {b * r}: <strong>{_surd_text(k, r)}</strong>.')
    hint = 'Multiply the top and the bottom by the square root in the denominator, then cancel the whole numbers.'
    record('surds_rationalise_coef', a=a, b=b, r=r)
    return q, s, hint, 3, _surd_answer(k, r)


def gcse_surds_match_simplified():
    """Intermediate: which expression equals a square root written in simplest form?"""
    while True:
        k = random.choice([2, 3, 5, 6])
        r = random.choice([2, 3, 5, 6, 7])
        if k != r:
            break
    n = k * k * r
    correct = f'{k}√{r}'
    wrong = [f'{k * k}√{r}', f'{r}√{k}', f'{k} + √{r}']
    q = f'Which of these is equal to √{n}?'
    s = (f'Look for a square number that divides {n}: {n} = {k * k} × {r}.<br>'
         f'√{n} = √{k * k} × √{r} = {k}√{r}, so the answer is <strong>{correct}</strong>.')
    hint = 'Write the number under the root as a square number times another number, then take the root of the square number.'
    record('surds_match_simplified', n=n)
    return q, s, hint, 2, _shuffled_choice(correct, wrong)


def gcse_surds_pythagoras_exact():
    """Difficult: exact hypotenuse when the shorter sides are surds."""
    while True:
        a, b = random.randint(3, 20), random.randint(3, 20)
        total = a + b
        k, r = _simplify_root(total)
        if a != b and k > 1 and r > 1 and math.isqrt(a) ** 2 != a and math.isqrt(b) ** 2 != b:
            break
    q = (f'A right-angled triangle has shorter sides of length √{a} cm and √{b} cm. Find the exact length of the '
         f'hypotenuse. Give your answer in the form k√r, where r has no square factors.')
    s = (f'Pythagoras: hypotenuse² = (√{a})² + (√{b})² = {a} + {b} = {total}.<br>'
         f'Hypotenuse = √{total} = √({k * k} × {r}) = <strong>{_surd_text(k, r)} cm</strong>.')
    hint = 'Square each shorter side first. Squaring a square root gives the number inside it. Add, then take the root and simplify.'
    record('surds_pythagoras', a=a, b=b)
    return q, s, hint, 3, _surd_answer(k, r)


# ─────────────────────────────────────────────────────────────────────────────
# Decimals
# ─────────────────────────────────────────────────────────────────────────────

def _dec_from_int(n, places):
    """Fraction n / 10**places."""
    return Fraction(n, 10 ** places)


def gcse_dec_known_product():
    """Intermediate: use a given whole-number product to multiply decimals."""
    a, b = random.randint(12, 49), random.randint(12, 49)
    while a == b or a % 10 == 0 or b % 10 == 0:
        a, b = random.randint(12, 49), random.randint(12, 49)
    p = a * b
    while True:
        s1, s2 = random.randint(0, 2), random.randint(0, 2)
        if s1 + s2 >= 2:
            break
    x, y = _dec_from_int(a, s1), _dec_from_int(b, s2)
    ans = x * y
    q = f'Use the fact that {a} × {b} = {p} to work out {_num_text(x)} × {_num_text(y)}.'
    how = []
    for val, whole, sh in ((x, a, s1), (y, b, s2)):
        how.append(f'{_num_text(val)} is {whole} ÷ {10 ** sh}' if sh else f'{whole} is not changed')
    s = (f'{a} × {b} = {p}.<br>'
         f'{how[0]} and {how[1]}, so the answer is {p} ÷ {10 ** (s1 + s2)}.<br>'
         f'{p} ÷ {10 ** (s1 + s2)} = <strong>{_num_text(ans)}</strong>.')
    hint = 'Count the decimal places in both numbers together. The answer is the known product with that many decimal places.'
    record('product', a=float(x), b=float(y))
    return q, s, hint, 2, {'type': 'number', 'value': _num_text(ans)}


def gcse_dec_known_division():
    """Difficult: use a given product to divide decimals."""
    a, b = random.randint(12, 49), random.randint(12, 49)
    while a == b or a % 10 == 0 or b % 10 == 0:
        a, b = random.randint(12, 49), random.randint(12, 49)
    p = a * b
    divisor_is_a = random.random() < 0.5
    d, other = (a, b) if divisor_is_a else (b, a)
    t, u = random.randint(0, 3), random.randint(0, 2)
    if t == u:
        t += 1
    dividend, divisor = _dec_from_int(p, t), _dec_from_int(d, u)
    ans = Fraction(other) * Fraction(10) ** (u - t)
    q = f'Use the fact that {a} × {b} = {p} to work out {_num_text(dividend)} ÷ {_num_text(divisor)}.'
    top = (f'{_num_text(dividend)} is {p} ÷ {10 ** t}, which makes the answer {10 ** t} times smaller'
           if t else f'The top, {p}, is unchanged')
    bottom = (f'{_num_text(divisor)} is {d} ÷ {10 ** u}, which makes the answer {10 ** u} times bigger'
              if u else f'the bottom, {d}, is unchanged')
    # review: only the steps that happen are written ("18 ÷ 1 × 10" before)
    last = f'{other}' + (f' ÷ {10 ** t}' if t else '') + (f' × {10 ** u}' if u else '')
    s = (f'{a} × {b} = {p}, so {p} ÷ {d} = {other}.<br>'
         f'{top}{"; " if t else ", and "}{bottom}.<br>'
         f'{last} = <strong>{_num_text(ans)}</strong>.')
    hint = 'Write the question as a division you know from the fact, then ask how many times smaller the top is and how many times smaller the bottom is.'
    record('quotient', a=float(dividend), b=float(divisor))
    return q, s, hint, 3, {'type': 'number', 'value': _num_text(ans)}


def gcse_dec_rounding_error():
    """Difficult: the error made by rounding a decimal."""
    dp = random.choice([1, 2])
    while True:
        thousandths = random.randint(1000, 9999)
        extra = random.randint(1, 9)
        value = Fraction(thousandths * 10 + extra, 10 ** 4)
        scaled = value * 10 ** dp
        if scaled.denominator != 1 and abs(scaled - math.floor(scaled) - Fraction(1, 2)) > Fraction(1, 20):
            break
    rounded = Fraction(math.floor(scaled + Fraction(1, 2)), 10 ** dp)
    diff = abs(value - rounded)
    word = 'decimal place' if dp == 1 else 'decimal places'
    q = (f'x = {_num_text(value)}. x is rounded to {dp} {word}. '
         f'Work out the difference between the rounded value and x.')
    r_text = f'{float(rounded):.{dp}f}'
    s = (f'{_num_text(value)} rounded to {dp} {word} is {r_text}.<br>'
         f'The difference is {_num_text(max(value, rounded))} − {_num_text(min(value, rounded))} = <strong>{_num_text(diff)}</strong>.')
    hint = f'Round x to {dp} {word} first. Then subtract the smaller of the two numbers from the larger.'
    record('dec_round_error', x=float(value), dp=dp)
    return q, s, hint, 3, {'type': 'number', 'value': _num_text(diff)}


# ─────────────────────────────────────────────────────────────────────────────
# Algebra
# ─────────────────────────────────────────────────────────────────────────────

def _lin(a, b, var='x'):
    """'3x + 4', 'x - 3', '-2x + 5' (no 0x, no '+ -')."""
    lead = '' if a == 1 else '-' if a == -1 else str(a)
    if a == 0:
        return str(b)
    if b == 0:
        return f'{lead}{var}'
    return f'{lead}{var} {signed_term(b)}'


def _alg_ans(expr, hint=None, form=None):
    payload = {'type': 'algebraic', 'value': sp.sstr(expr)}
    if form:
        payload['form'] = form
    if hint:
        payload['format_hint'] = hint
    return payload


def _example(result, *options):
    """'e.g. ...' for the answer box: the first (text, sympy value) option that is not the answer itself.

    Review: a fixed example was sometimes the very answer (Expand 3(2x + 5) under "e.g. 6x + 15", Simplify x^2 × x^4
    under "e.g. x^6"), which hands the pupil the answer before they start.
    """
    for text, value in options:
        if sp.expand(value - result) != 0:
            return f'e.g. {text}'
    raise ValueError('every example equals the answer')


def _linear_ans(value, var='x'):
    f = Fraction(value)
    return {'type': 'linear', 'value': str(f.numerator) if f.denominator == 1 else f'{f.numerator}/{f.denominator}',
            'var': var}


def _power_text(var, n):
    return var if n == 1 else f'{var}^{{{n}}}'


def _term_text(c, var, power=1):
    """'3x', 'x^{2}', '5' for a coefficient and a power of var (never '1x')."""
    body = _power_text(var, power) if power else ''
    if power == 0:
        return str(c)
    return body if c == 1 else f'-{body}' if c == -1 else f'{c}{body}'


@verifies('alg', task='simplify', form=None)
def algebra_practice_collect_terms():
    """Foundational: collect like terms."""
    style = random.choice(['letters', 'letters', 'powers'])
    if style == 'letters':
        u, v = random.choice([('a', 'b'), ('x', 'y'), ('m', 'n'), ('p', 'q')])
        symu, symv = sp.symbols(f'{u} {v}')
        shape = [(u, 1), (v, 1), (u, 1), (v, 1)]
    else:
        u, v = 'x', 'x'
        symu, symv = sp.Symbol('x') ** 2, sp.Symbol('x')
        shape = [('x', 2), ('x', 1), ('x', 2), ('x', 1)]
    while True:
        cs = [random.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8]) for _ in range(4)]
        a_tot, b_tot = cs[0] + cs[2], cs[1] + cs[3]
        order = [0, 1, 2, 3]
        random.shuffle(order)
        if cs[order[0]] > 0 and a_tot != 0 and b_tot != 0:
            break
    parts = []
    for n, i in enumerate(order):
        c = cs[i]
        var, power = shape[i]
        t = _term_text(abs(c), var, power)
        parts.append(t if n == 0 else f'{"+" if c > 0 else "-"} {t}')
    result = a_tot * symu + b_tot * symv
    q = rf'Simplify \( {" ".join(parts)} \)'
    first, second = ('x^{2}', 'x') if style == 'powers' else (u, v)
    s = (rf'Collect the like terms.<br>'
         rf'The \( {first} \) terms: \( {cs[0]} + {bracket_neg(cs[2])} = {a_tot} \), so \( {_term_text(a_tot, first)} \).<br>'
         rf'The \( {second} \) terms: \( {cs[1]} + {bracket_neg(cs[3])} = {b_tot} \), so \( {_term_text(b_tot, second)} \).<br>'
         rf'Answer: \( \boxed{{{sp.latex(result)}}} \)')
    hint = 'Only terms with exactly the same letter part can be added or subtracted. Collect each kind together, keeping the sign in front of each term.'
    a_, b_, p_, q_ = sp.symbols('a b p q')
    # review: the answer must have its like terms collected (the expanded form), so typing the question back is refused
    return q, s, hint, 2, _alg_ans(result, _example(result, ('3a + 7b', 3 * a_ + 7 * b_), ('4p - 5q', 4 * p_ - 5 * q_)),
                                   FORM_EXPANDED)


@verifies('alg', task='simplify', form=None)
def algebra_practice_index_laws_simplify():
    """Foundational: the index laws for one letter."""
    var = random.choice(['x', 'y', 'a', 'm', 'p', 't'])
    sv = sp.Symbol(var)
    kind = random.choice(['mul', 'div', 'pow'])
    if kind == 'mul':
        a, b = random.randint(2, 5), random.randint(2, 5)
        q = rf'Simplify \( {var}^{{{a}}} \times {var}^{{{b}}} \)'
        result = sv ** (a + b)
        s = rf'To multiply powers of the same letter, add the indices: \( {a} + {b} = {a + b} \), so \( \boxed{{{var}^{{{a + b}}}}} \).'
        hint = 'When you multiply powers of the same letter, add the indices.'
    elif kind == 'div':
        b = random.randint(2, 5)
        a = b + random.randint(2, 5)
        q = rf'Simplify \( {var}^{{{a}}} \div {var}^{{{b}}} \)'
        result = sv ** (a - b)
        s = rf'To divide powers of the same letter, subtract the indices: \( {a} - {b} = {a - b} \), so \( \boxed{{{var}^{{{a - b}}}}} \).'
        hint = 'When you divide powers of the same letter, subtract the indices.'
    else:
        a, b = random.choice([(2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (4, 2), (5, 2)])
        q = rf'Simplify \( ({var}^{{{a}}})^{{{b}}} \)'
        result = sv ** (a * b)
        s = rf'To raise a power to a power, multiply the indices: \( {a} \times {b} = {a * b} \), so \( \boxed{{{var}^{{{a * b}}}}} \).'
        hint = 'A power of a power: multiply the indices together.'
    k_ = sp.Symbol('k')
    # review: the answer is one power in its simplest form, so x^2 × x^5 typed back is refused (answer_checkers)
    return q, s, hint, 2, _alg_ans(result, _example(result, ('k^5', k_ ** 5)), FORM_SIMPLIFIED)


@verifies('alg', task='expand')
def algebra_practice_expand_single():
    """Foundational: expand one bracket."""
    x = sp.Symbol('x')
    if random.random() < 0.65:
        k = random.randint(2, 9)
        a, b = random.randint(1, 4), random.choice([-8, -7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7, 8])
        shown = rf'{k}({_lin(a, b)})'
        result = sp.expand(k * (a * x + b))
        step = rf'\( {k} \times {coef(a, "x")} = {k * a}x \) and \( {k} \times {bracket_neg(b)} = {k * b} \)'
    else:
        a, b = random.randint(1, 4), random.choice([-7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7])
        shown = rf'x({_lin(a, b)})'
        result = sp.expand(x * (a * x + b))
        step = rf'\( x \times {coef(a, "x")} = {a if a != 1 else ""}x^{{2}} \) and \( x \times {bracket_neg(b)} = {b}x \)'
    q = rf'Expand \( {shown} \)'
    s = rf'Multiply every term in the bracket by the term outside: {step}.<br>\( \boxed{{{sp.latex(result)}}} \)'
    hint = 'Multiply each term inside the bracket by the term outside. Take care with the signs.'
    return q, s, hint, 2, _alg_ans(result, _example(result, ('6x + 15', 6 * x + 15), ('4x - 9', 4 * x - 9)), FORM_EXPANDED)


def algebra_practice_form_expression():
    """Foundational: write an expression from a description."""
    kind = random.choice(['cost', 'ages', 'perimeter'])
    k1, k2 = random.randint(2, 6), random.randint(2, 6)
    if kind == 'cost':
        u, v = random.choice([('p', 'n'), ('a', 'b'), ('c', 'd')])
        names = {'p': 'pens', 'n': 'notebooks', 'a': 'apples', 'b': 'bananas', 'c': 'cakes', 'd': 'drinks'}
        q = (f'{names[u].capitalize()} cost £{u} each and {names[v]} cost £{v} each. '
             f'Write an expression for the total cost, in pounds, of {k1} {names[u]} and {k2} {names[v]}.')
        result = k1 * sp.Symbol(u) + k2 * sp.Symbol(v)
        s = f'{k1} {names[u]} cost {k1} × {u} = {k1}{u}. {k2} {names[v]} cost {k2}{v}.<br>Total: <strong>{k1}{u} + {k2}{v}</strong>.'
        hint = 'Multiply the number of items by the price of one item, then add the two costs.'
        var1, var2 = u, v
    elif kind == 'ages':
        var1, var2 = 'n', ''
        q = (f'Mia is n years old. Her brother is {k1} years older than Mia and her mother is {k2} times as old as Mia. '
             f'Write an expression, in terms of n, for the total of the three ages.')
        n = sp.Symbol('n')
        result = sp.expand(n + (n + k1) + k2 * n)
        s = (f'Mia: n. Brother: n + {k1}. Mother: {k2}n.<br>Total: n + (n + {k1}) + {k2}n = <strong>{sp.latex(result)}</strong>.')
        hint = '"Older than" means add on. "Times as old" means multiply. Write each age, then add the three expressions.'
    else:
        var1, var2 = 'w', ''
        q = (f'A rectangle has width w cm. Its length is {k1} cm more than its width. '
             f'Write an expression for the perimeter of the rectangle, in centimetres.')
        w = sp.Symbol('w')
        result = sp.expand(2 * w + 2 * (w + k1))
        s = (f'Length = w + {k1}.<br>Perimeter = 2 × width + 2 × length = 2w + 2(w + {k1}) = <strong>{sp.latex(result)}</strong>.')
        hint = 'Perimeter is the distance all the way round: two widths plus two lengths. The length is the width plus the extra.'
    record('alg_form_expr', kind=kind, var1=var1, var2=var2, k1=k1, k2=k2 if kind != 'perimeter' else 0)
    p_, n_, j_ = sp.symbols('p n j')
    eg = _example(result, ('4p + 3n', 4 * p_ + 3 * n_), ('5j + 2', 5 * j_ + 2))
    return q, s, hint, 2, _alg_ans(result, f'Enter an expression, {eg}')


def algebra_practice_form_equation_shape():
    """Foundational: form an equation from the perimeter of a shape and solve it."""
    if random.random() < 0.5:
        x = random.randint(2, 12)
        a, b = random.randint(1, 8), random.randint(2, 9)
        perim = 2 * (x + a + b)
        q = (f'A rectangle has length (x + {a}) cm and width {b} cm. Its perimeter is {perim} cm. '
             f'Form an equation and solve it to find x.')
        s = (f'Perimeter = 2 × (length + width), so 2(x + {a} + {b}) = {perim}.<br>'
             f'x + {a + b} = {perim // 2}<br>x = <strong>{x}</strong>.')
        record('alg_form_perimeter', kind='rect', a=a, b=b, p=perim)
    else:
        # review: the three sides make a real triangle (x = 4 gave sides 4, 11 and 5 cm, and x = 3, b = 6 a side of 0 cm):
        # 2x - b > 0, and the longest side is shorter than the other two together (x + a < 3x - b, 2x - b < 2x + a)
        while True:
            x = random.randint(3, 12)
            a, b = random.randint(1, 8), random.randint(1, 6)
            if 2 * x - b > 0 and x + a < 3 * x - b:
                break
        perim = 4 * x + a - b
        q = (f'A triangle has sides of length x cm, (x + {a}) cm and (2x − {b}) cm. Its perimeter is {perim} cm. '
             f'Form an equation and solve it to find x.')
        simplified = f'4x {signed_term(a - b)}' if a != b else '4x'
        s = (f'Add the three sides: x + (x + {a}) + (2x − {b}) = {perim}.<br>'
             f'{simplified} = {perim}<br>4x = {perim - (a - b)}<br>x = <strong>{x}</strong>.')
        record('alg_form_perimeter', kind='tri', a=a, b=b, p=perim)
    hint = 'Write the perimeter as the sum of all the sides. Set it equal to the given perimeter, then solve the equation.'
    return q, s, hint, 3, _linear_ans(x)


@verifies('alg', task='factorise')
def algebra_practice_factorise_simple():
    """Intermediate: factorise x^2 + bx + c."""
    x = sp.Symbol('x')
    while True:
        p, r = random.randint(-9, 9), random.randint(-9, 9)
        if p and r and p != r and p + r != 0:
            break
    expr = sp.expand((x + p) * (x + r))
    factored = f'({_lin(1, p)})({_lin(1, r)})'
    q = rf'Factorise \( {sp.latex(expr)} \)'
    s = (rf'Find two numbers that multiply to {p * r} and add to {p + r}: they are {p} and {r}.<br>'
         rf'\( {sp.latex(expr)} = \boxed{{{factored}}} \)')
    hint = 'Look for two numbers that multiply to give the last number and add to give the number in front of x.'
    eg = _example(expr, ('(x + 2)(x + 5)', (x + 2) * (x + 5)), ('(x - 3)(x + 7)', (x - 3) * (x + 7)))
    return q, s, hint, 2, _alg_ans(factored, eg, FORM_FACTORISED)


@verifies('alg', task='factorise')
def algebra_practice_difference_two_squares():
    """Intermediate: factorise a difference of two squares."""
    x = sp.Symbol('x')
    while True:
        k = random.choice([1, 1, 2, 3, 4, 5])
        m = random.randint(2, 12)
        if math.gcd(k, m) == 1:
            break
    expr = k * k * x ** 2 - m * m
    factored = f'({_lin(k, -m)})({_lin(k, m)})'
    q = rf'Factorise \( {sp.latex(expr)} \)'
    first = f'{k}x' if k != 1 else 'x'
    s = (rf'This is a difference of two squares: \( {k * k if k != 1 else ""}x^{{2}} = ({first})^{{2}} \) and \( {m * m} = {m}^{{2}} \).<br>'
         rf'\( a^{{2}} - b^{{2}} = (a - b)(a + b) \), so \( \boxed{{{factored}}} \).')
    hint = 'Both terms are square numbers (or squares of a letter), with a minus between them. Use a² − b² = (a − b)(a + b).'
    eg = _example(expr, ('(x - 3)(x + 3)', x ** 2 - 9), ('(x - 7)(x + 7)', x ** 2 - 49))
    return q, s, hint, 2, _alg_ans(factored, eg, FORM_FACTORISED)


@verifies('alg', task='simplify', form=None)
def algebra_practice_index_laws_coefficients():
    """Intermediate: index laws with numbers in front."""
    x = sp.Symbol('x')
    kind = random.choice(['pow', 'mul', 'div'])
    if kind == 'pow':
        k = random.randint(2, 4)
        a, n = random.choice([(2, 2), (2, 3), (3, 2), (3, 3), (2, 4), (4, 2), (2, 5), (5, 2)])
        q = rf'Simplify \( ({k}x^{{{a}}})^{{{n}}} \)'
        result = (k * x ** a) ** n
        s = rf'Raise both the number and the power of x: \( {k}^{{{n}}} = {k ** n} \) and \( x^{{{a} \times {n}}} = x^{{{a * n}}} \), so \( \boxed{{{k ** n}x^{{{a * n}}}}} \).'
        hint = 'The power outside the bracket applies to the number and to the letter. Raise the number to the power and multiply the indices.'
    elif kind == 'mul':
        k1, k2 = random.randint(2, 6), random.randint(2, 6)
        a, b = random.randint(2, 5), random.randint(2, 5)
        q = rf'Simplify \( {k1}x^{{{a}}} \times {k2}x^{{{b}}} \)'
        result = k1 * k2 * x ** (a + b)
        s = rf'Multiply the numbers: \( {k1} \times {k2} = {k1 * k2} \). Add the indices: \( {a} + {b} = {a + b} \).<br>\( \boxed{{{k1 * k2}x^{{{a + b}}}}} \)'
        hint = 'Multiply the numbers in front, and add the indices of x.'
    else:
        k, m = random.randint(2, 6), random.randint(2, 6)
        b = random.randint(2, 4)
        a = b + random.randint(2, 4)
        q = rf'Simplify \( \dfrac{{{k * m}x^{{{a}}}}}{{{k}x^{{{b}}}}} \)'
        result = m * x ** (a - b)
        s = rf'Divide the numbers: \( {k * m} \div {k} = {m} \). Subtract the indices: \( {a} - {b} = {a - b} \).<br>\( \boxed{{{m}x^{{{a - b}}}}} \)'
        hint = 'Divide the numbers, and subtract the indices of x.'
    # review: one term in its simplest form, so (2x^2)^3 or 2x^4 × 5x^2 typed back is refused (answer_checkers)
    return q, s, hint, 3, _alg_ans(result, _example(result, ('6x^5', 6 * x ** 5), ('7x^9', 7 * x ** 9)), FORM_SIMPLIFIED)


@verifies('alg', task='solve_linear')
def algebra_practice_solve_fraction_equation():
    """Intermediate: solve an equation with a fraction on one side."""
    while True:
        d = random.choice([2, 3, 4, 5])
        a = random.randint(1, 4)
        b = random.choice([-7, -5, -3, -2, 1, 2, 3, 4, 5, 7])
        x = random.randint(2, 12)
        if (a * x + b) % d == 0 and (a * x + b) // d > 0:
            break
    c = (a * x + b) // d
    top = _lin(a, b)
    q = rf'Solve \( \dfrac{{{top}}}{{{d}}} = {c} \)'
    s = (rf'Multiply both sides by {d}: \( {top} = {c * d} \).<br>'
         + (rf'\( {coef(a, "x")} = {c * d - b} \), so \( x = \boxed{{{x}}} \).' if a != 1
            else rf'Take {b} from both sides: \( x = \boxed{{{x}}} \).' if b > 0
            else rf'Add {-b} to both sides: \( x = \boxed{{{x}}} \).'))      # review: "x = 7, so x = 7"
    hint = f'First get rid of the fraction: multiply both sides by {d}. Then solve the two-step equation.'
    return q, s, hint, 3, _linear_ans(x)


def algebra_practice_form_equation_angles():
    """Intermediate: angles in a triangle or on a straight line as expressions in x."""
    kind = random.choice(['triangle', 'line'])
    while True:
        c1, c2, c3 = random.choice([1, 2, 3]), random.choice([1, 2, 3]), random.choice([1, 2, 3])
        a, b = random.randint(5, 30), random.randint(5, 30)
        total = 180
        s_ = c1 + c2 + c3
        if (total - a + b) % s_ == 0:
            x = (total - a + b) // s_
            if 5 <= x <= 50 and c2 * x - b > 0 and not (c1 == c2 == c3):
                break
    t1, t2, t3 = f'({_lin(c1, a)})', f'({_lin(c2, -b)})', coef(c3, 'x')
    where = 'the angles of a triangle' if kind == 'triangle' else 'angles on a straight line'
    q = (f'The sizes of {where} are {t1}°, {t2}° and {t3}°. Form an equation and solve it to find x.')
    collected = f'{s_}x {signed_term(a - b)} = {total}<br>' if a != b else ''      # review: "6x + 0 = 180"
    s = (f'The angles add to {total}°: {t1} + {t2} + {t3} = {total}.<br>'
         f'{collected}{s_}x = {total - (a - b)}<br>x = <strong>{x}</strong>.')
    hint = f'The three angles add up to {total}°. Write that as an equation, collect the x terms and the numbers, then solve it.'
    record('alg_angles', derived=('total',), c1=c1, a=a, c2=c2, b=b, c3=c3, total=total)
    return q, s, hint, 3, _linear_ans(x)


@verifies('alg', task='expand')
def algebra_practice_expand_two_brackets():
    """Intermediate: expand and simplify two single brackets."""
    x = sp.Symbol('x')
    while True:
        a, c = random.randint(2, 6), random.randint(2, 5)
        b = random.randint(1, 7)
        d = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4])
        op = random.choice(['+', '-'])
        total = a + c if op == '+' else a - c
        if total != 0 and a != c:
            break
    expr = sp.expand(a * (x + b) + (c if op == '+' else -c) * (x + d))
    q = rf'Expand and simplify \( {a}({_lin(1, b)}) {op} {c}({_lin(1, d)}) \)'
    inner = _lin(c, c * d)
    s = (rf'Expand each bracket: \( {a}({_lin(1, b)}) = {_lin(a, a * b)} \) and \( {c}({_lin(1, d)}) = {inner} \).<br>'
         rf'So the expression is \( {_lin(a, a * b)} {op} ({inner}) \).<br>'
         rf'Collect like terms: \( \boxed{{{sp.latex(expr)}}} \)')
    hint = 'Expand each bracket separately. A minus sign in front of the second bracket changes the sign of both terms inside it.'
    return q, s, hint, 3, _alg_ans(expr, _example(expr, ('5x + 7', 5 * x + 7), ('3x - 4', 3 * x - 4)), FORM_EXPANDED)


@verifies('alg', task='expand')
def algebra_practice_expand_three_binomials():
    """Difficult: expand three linear brackets."""
    x = sp.Symbol('x')
    while True:
        a, b, c = (random.choice([-4, -3, -2, -1, 1, 2, 3, 4, 5]) for _ in range(3))
        if len({a, b, c}) == 3:
            break
    expr = sp.expand((x + a) * (x + b) * (x + c))
    first = sp.expand((x + a) * (x + b))
    q = rf'Expand and simplify \( ({_lin(1, a)})({_lin(1, b)})({_lin(1, c)}) \)'
    s = (rf'Expand the first two brackets: \( ({_lin(1, a)})({_lin(1, b)}) = {sp.latex(first)} \).<br>'
         rf'Multiply this by \( ({_lin(1, c)}) \): \( x \times ({sp.latex(first)}) = {sp.latex(sp.expand(x * first))} \) and '
         rf'\( {bracket_neg(c)} \times ({sp.latex(first)}) = {sp.latex(sp.expand(c * first))} \).<br>'
         rf'\( \boxed{{{sp.latex(expr)}}} \)')
    hint = 'Expand two of the brackets first. Then multiply your answer by the third bracket, one term at a time, and collect like terms.'
    eg = _example(expr, ('x^3 + 6x^2 + 11x + 6', (x + 1) * (x + 2) * (x + 3)),
                  ('x^3 - 2x^2 - 5x + 6', (x - 1) * (x + 2) * (x - 3)))
    return q, s, hint, 4, _alg_ans(expr, eg, FORM_EXPANDED)


def algebra_practice_form_quadratic_area():
    """Difficult: form and solve a quadratic from the area of a rectangle."""
    x = random.randint(3, 10)
    a = random.randint(1, 5)
    b = random.randint(1, min(3, x - 1))
    area = (x + a) * (x - b)
    q = (f'A rectangle has length (x + {a}) cm and width (x − {b}) cm. Its area is {area} cm². '
         f'Form an equation and solve it to find x.')
    expanded = sp.expand((sp.Symbol('x') + a) * (sp.Symbol('x') - b) - area)
    s = (rf'Area = length × width: \( (x + {a})(x - {b}) = {area} \).<br>'
         rf'Expand and rearrange: \( {sp.latex(expanded)} = 0 \).<br>'
         rf'Factorise or use the formula: \( x = {x} \) or \( x = {-(a - b + x)} \).<br>'
         rf'A length cannot be negative, so \( x = \boxed{{{x}}} \).')
    hint = 'Multiply the length by the width and set it equal to the area. Rearrange to a quadratic equal to zero. Reject any answer that gives a negative length.'
    record('alg_form_area', a=a, b=b, area=area)
    return q, s, hint, 4, _linear_ans(x)


# ─────────────────────────────────────────────────────────────────────────────
# Number and ratio / proportion
# ─────────────────────────────────────────────────────────────────────────────

def gcse_number_reciprocal():
    """Foundational: the reciprocal of a whole number, a fraction or a simple decimal."""
    shape = random.choice(['int', 'frac', 'dec', 'frac'])
    if shape == 'int':
        n = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 20])
        shown, num, den = str(n), n, 1
        derived = ()
    elif shape == 'frac':
        num, den = _random_proper_fraction((3, 4, 5, 6, 7, 8, 9, 10))
        shown = f'{num}/{den}'
        derived = ()
    else:
        num, den, shown = random.choice([(1, 2, '0.5'), (1, 4, '0.25'), (1, 5, '0.2'), (1, 10, '0.1'), (3, 4, '0.75'),
                                         (1, 8, '0.125'), (2, 5, '0.4'), (3, 5, '0.6')])
        derived = ('n', 'd')
    value = Fraction(den, num)
    q = f'Write down the reciprocal of {shown}.'
    # review: no "3/4 = 3/4, so the reciprocal is 4/3 = 4/3" lines
    written = f'{shown} = {num}/{den}, so the' if shown != f'{num}/{den}' else 'The'
    flipped = f'{den}/{num}'
    shown_value = f'{flipped} = <strong>{_frac_text(value)}</strong>' if _frac_text(value) != flipped \
        else f'<strong>{flipped}</strong>'
    s = (f'The reciprocal of a number is 1 divided by the number. To find the reciprocal of a fraction, turn it upside down.<br>'
         f'{written} reciprocal is {shown_value}.')
    hint = 'The reciprocal turns the number upside down. A whole number n is n/1, so its reciprocal is 1/n. It is not the same as the negative of the number.'
    record('num_reciprocal', derived=derived, n=num, d=den)
    answer = value.numerator if value.denominator == 1 else _fraction_answer(value)
    return q, s, hint, 1, answer


def gcse_number_counting_product():
    """Intermediate: the product rule for counting."""
    kind = random.choice(['menu', 'outfit', 'trip'])
    n1, n2, n3 = random.randint(2, 6), random.randint(2, 6), random.randint(2, 5)
    if kind == 'menu':
        q = (f'A café sells {n1} starters, {n2} main courses and {n3} desserts. '
             f'How many different three-course meals can be chosen, with one of each course?')
    elif kind == 'outfit':
        q = (f'Liam has {n1} shirts, {n2} pairs of trousers and {n3} pairs of shoes. '
             f'How many different outfits can he make with one of each?')
    else:
        n3 = 1
        q = (f'A ferry company runs {n1} routes from the mainland to an island and {n2} routes back. '
             f'How many different return journeys are possible?')
    total = n1 * n2 * n3
    s = (f'Multiply the number of choices at each stage: {n1} × {n2}' + (f' × {n3}' if n3 > 1 else '') + f' = <strong>{total}</strong>.')
    hint = 'For each choice of the first item there is every choice of the next item. Multiply the numbers of choices, do not add them.'
    record('num_counting', n1=n1, n2=n2, n3=n3)
    return q, s, hint, 2, total


def gcse_ratio_combine():
    """Intermediate: combine two ratios that share a part."""
    while True:
        a, b = random.randint(1, 5), random.randint(2, 6)
        c, d = random.randint(1, 6), random.randint(1, 7)
        if a != b and c != d and b != c and math.gcd(a, b) == 1 and math.gcd(c, d) == 1:
            break
    lcm = math.lcm(b, c)
    x, y, z = a * (lcm // b), lcm, d * (lcm // c)
    g = math.gcd(math.gcd(x, y), z)
    names = random.choice([('red', 'blue', 'green'), ('apples', 'pears', 'plums'), ('A', 'B', 'C')])
    if names[0] == 'A':
        q = f'A : B = {a} : {b} and B : C = {c} : {d}. Write A : B : C in its simplest form.'
    else:
        q = (f'The ratio of {names[0]} to {names[1]} is {a} : {b}. The ratio of {names[1]} to {names[2]} is {c} : {d}. '
             f'Write the ratio {names[0]} : {names[1]} : {names[2]} in its simplest form.')
    s = (f'Make the middle part the same in both ratios: the lowest common multiple of {b} and {c} is {lcm}.<br>'
         f'{a} : {b} = {a * (lcm // b)} : {lcm} and {c} : {d} = {lcm} : {d * (lcm // c)}.<br>'
         f'So the combined ratio is {x} : {y} : {z}' + (f' = <strong>{x // g} : {y // g} : {z // g}</strong> in its simplest form.' if g > 1
                                                      else ' (already in its simplest form).'))
    hint = 'Make the number that appears in both ratios the same, using the lowest common multiple. Then write all three parts together.'
    record('ratio_combine', a=a, b=b, c=c, d=d)
    return q, s, hint, 3, {'type': 'number_fields', 'values': (str(x // g), str(y // g), str(z // g)),
                           'labels': (names[0] if names[0] != 'A' else 'A', names[1] if names[0] != 'A' else 'B',
                                      names[2] if names[0] != 'A' else 'C')}


def gcse_ratio_from_difference():
    """Intermediate: use the difference between two shares to find the total or a share."""
    while True:
        a, b = random.randint(1, 7), random.randint(2, 9)
        if a < b and math.gcd(a, b) == 1:
            break
    part = random.choice([3, 4, 5, 6, 8, 10, 12, 15])
    diff = (b - a) * part
    ask = random.choice(['total', 'smaller'])
    p1, p2 = random.choice([('Ann', 'Ben'), ('Cara', 'Dev'), ('Mia', 'Sam')])
    q = (f'{p1} and {p2} share some money in the ratio {a} : {b}. {p2} gets £{diff} more than {p1}. ' +
         ('How much money is shared altogether?' if ask == 'total' else f'How much does {p1} get?'))
    key = (a + b) * part if ask == 'total' else a * part
    s = (f'The difference between the shares is {b} − {a} = {b - a} part{"s" if b - a != 1 else ""}, and this is £{diff}.<br>'
         f'1 part = £{diff} ÷ {b - a} = £{part}.<br>' +
         (f'Total parts = {a} + {b} = {a + b}, so the total is {a + b} × £{part} = <strong>£{key}</strong>.' if ask == 'total'
          else f'{p1} gets {a} parts: {a} × £{part} = <strong>£{key}</strong>.'))
    hint = f'The £{diff} is the difference between the two shares, not one part. Work out how many parts that difference is first.'
    record('ratio_from_difference', a=a, b=b, diff=diff, ask=ask)
    return q, s, hint, 3, key


def gcse_ratio_proportional_square():
    """Difficult: y is proportional to the square of x."""
    k = random.randint(2, 5)
    x1, x2 = random.sample(range(2, 8), 2)
    y1, y2 = k * x1 * x1, k * x2 * x2
    q = (f'y is directly proportional to the square of x. When x = {x1}, y = {y1}. Find the value of y when x = {x2}.')
    s = (f'y = kx². Substitute x = {x1} and y = {y1}: {y1} = k × {x1 * x1}, so k = {k}.<br>'
         f'When x = {x2}: y = {k} × {x2}² = {k} × {x2 * x2} = <strong>{y2}</strong>.')
    hint = 'y is proportional to x squared, so write y = kx². Find k from the pair of values, then use it for the new x.'
    record('prop_square', x1=x1, y1=y1, x2=x2)
    return q, s, hint, 4, y2


def gcse_dec_subtract_from_whole():
    """Foundational: subtract a decimal from a whole number."""
    a = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 20])
    places = random.choice([1, 2, 2])
    while True:
        b = Fraction(random.randint(11, a * 10 ** places - 1), 10 ** places)
        if b.denominator != 1 and b < a:
            break
    ans = a - b
    places = len(_num_text(b).split('.')[1])        # review: 2.50 is shown as 2.5, so 7.00 − 2.5 was written
    q = f'Work out {a} − {_num_text(b)}.'
    s = (f'Write {a} with the same number of decimal places as {_num_text(b)}: {a}.{"0" * places} − {_num_text(b)}.<br>'
         f'Line up the decimal points and subtract: <strong>{_num_text(ans)}</strong>.')
    hint = 'Write the whole number with a decimal point and zeros so the decimal places line up, then subtract column by column.'
    record('num_directed', a=a, op='-', b=float(b))
    return q, s, hint, 2, {'type': 'number', 'value': _num_text(ans)}
