"""GCSE maths variety plan, Phase 3 batch B: new practice kinds for simultaneous_equations, completing_the_square,
quadratic_simultaneous_equations, algebraic_fractions, algebraic_proof, functions and equations_inequalities
(docs/GCSE_MATHS_VARIETY.md sections 4 and 19).

Every generator here returns the usual practice tuple ``(question, solution, hint, marks[, answer])`` that its topic's
``*_problem_from_output`` wrapper turns into a problem (the wrappers fall back to ``problem_extra`` below for the
answer types they did not already know). The module is self-contained on purpose (shared helpers and
``maths_variety_a`` only): the topic modules import it when they build their practice pools, so it must never import
them back. The graphical simultaneous equations generators, which need that topic's drawing helpers, live in
``graphical_simultaneous_equations.py`` itself.

Each variant records the inputs the pupil is given (``record(...)``) or is tagged ``@verifies('alg', task=...)``, so the
GCSE verification smoke re-solves it with an independent solver in ``scripts/gcse_verify/solvers_variety_b.py``.
"""
from __future__ import annotations

import math
import random
import re
from fractions import Fraction

import sympy as sp

from generators.gcse.maths_variety_a import _alg_ans, _example, _lin, _linear_ans, _num_text
from generators.shared.answer_checkers import FORM_EXPANDED, FORM_FACTORISED, FORM_SIMPLIFIED, linear_format_hint
from generators.shared.utils import (
    graded_answer_number, problem_extra_from_graded_answer, proof_steps_answer, quadratic_roots_format_hint, quadratic_roots_ui_labels,
    signed_term,
)
from generators.shared.verify_hook import record, verifies


# ─────────────────────────────────────────────────────────────────────────────
# Answer payloads and small helpers
# ─────────────────────────────────────────────────────────────────────────────

def _raw(value):
    """Canonical text for a stored answer value: '3', '-2', '1.5', '7/2' (a Fraction or int or float)."""
    f = Fraction(value) if not isinstance(value, Fraction) else value
    if f.denominator == 1:
        return str(f.numerator)
    return f'{f.numerator}/{f.denominator}'


def _dec_raw(value):
    """Decimal text for an answer that terminates (1.5, not 3/2)."""
    return _num_text(Fraction(value))


def _pair(a, b, label_a='x', label_b='y'):
    return {'type': 'number_pair', 'values': (_raw(a), _raw(b)), 'label_a': label_a, 'label_b': label_b, 'sep': ','}


def _fields(values, labels, field_types=None):
    payload = {'type': 'number_fields', 'values': tuple(str(v) for v in values), 'labels': tuple(labels)}
    if field_types:
        payload['field_types'] = tuple(field_types)
    return payload


def _roots(*roots):
    return {'type': 'quadratic_roots', 'roots': tuple(_raw(r) for r in roots)}


def _lin_ans(value, var='x'):
    return _linear_ans(value, var)


def problem_extra(raw):
    """make_problem keyword arguments for an answer payload (the topic wrappers fall back to this)."""
    if not isinstance(raw, dict):
        return {}
    kind = raw.get('type')
    if kind == 'linear':
        var = raw.get('var') or 'x'
        val = raw.get('value')
        key = str(val) if var == 'x' else f'{var}={val}'
        return {'correct_answer_raw': key, 'answer_type': 'linear', 'answer_format_hint': linear_format_hint(key)}
    if kind == 'quadratic_roots':
        roots = raw.get('roots') or ()
        return {'correct_answer_raw': ','.join(str(r) for r in roots), 'answer_type': 'quadratic_roots',
                'answer_labels': quadratic_roots_ui_labels(len(roots)),
                'answer_format_hint': quadratic_roots_format_hint(len(roots))}
    if kind == 'algebraic_fraction':
        num, den = str(raw.get('numerator') or '').strip(), str(raw.get('denominator') or '').strip()
        if not (num and den):
            return {}
        extra = {'correct_answer_raw': f'{num}|{den}', 'answer_type': 'algebraic_fraction',
                 'answer_format_hint': raw.get('format_hint', 'Enter the numerator and denominator')}
        if raw.get('form'):
            extra['answer_form'] = raw['form']
        return extra
    return problem_extra_from_graded_answer(raw)


def _two_var(a, b, v1='x', v2='y'):
    """'3x + 2y', '5x - y', '-x + 4y' (no 1x, no '+ -')."""
    def term(c, v):
        return v if abs(c) == 1 else f'{abs(c)}{v}'
    first = ('-' if a < 0 else '') + term(a, v1)
    return f'{first} {"+" if b > 0 else "-"} {term(b, v2)}'


def _signed_mul(c, n, first=False):
    """'4 × 3' / '+ 5 × 2' / '- 1 × 2' pieces for a worked substitution."""
    body = f'{abs(c)} × {n}'
    if first:
        return ('−' if c < 0 else '') + body
    return f'{"+" if c > 0 else "−"} {body}'


def _money(x):
    return f'£{Fraction(x):.2f}' if Fraction(x).denominator != 1 else f'£{int(x)}'


def _money2(x):
    """Pounds to the penny: £4.35, £2.00 is written £2.00 (a price list stays aligned)."""
    return f'£{float(x):.2f}'


def _tex_line(m, c):
    """y = mx + c as text."""
    return f'y = {_lin(m, c)}'


def _sorted_points_fields(points):
    """number_fields payload for two points, the one with the smaller x first."""
    points = sorted(points)
    (x1, y1), (x2, y2) = points
    return _fields([_raw(x1), _raw(y1), _raw(x2), _raw(y2)],
                   ['x (1st solution)', 'y (1st solution)', 'x (2nd solution)', 'y (2nd solution)'])


# ─────────────────────────────────────────────────────────────────────────────
# Simultaneous equations
# ─────────────────────────────────────────────────────────────────────────────

def gcse_sim_substitute_solution():
    """Foundational: the solution is given; put it into two equations to find the constants on the right."""
    while True:
        x, y = random.sample(range(1, 8), 2)
        p, q = random.randint(2, 5), random.randint(2, 6)
        r, s = random.randint(2, 4), random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        c, d = p * x + q * y, r * x + s * y
        if d > 0 and c != d and len({c, d, x, y, p, q, r, abs(s)}) == 8:
            break
    q_text = (rf'The simultaneous equations \( {_two_var(p, q)} = c \) and \( {_two_var(r, s)} = d \) '
              rf'have the solution \( x = {x} \) and \( y = {y} \). Find the values of \( c \) and \( d \).')
    s_text = (f'Put x = {x} and y = {y} into each equation.<br>'
              f'c = {_signed_mul(p, x, True)} {_signed_mul(q, y)} = {p * x} + {q * y} = <strong>{c}</strong>.<br>'
              f'd = {_signed_mul(r, x, True)} {_signed_mul(s, y)} = {r * x} {"+" if s > 0 else "−"} {abs(s) * y} = <strong>{d}</strong>.')
    hint = 'Replace x and y by the numbers you are given in each equation, then work out the left-hand side.'
    record('sim_sub_solution', p=p, q=q, r=r, s=s, x=x, y=y)
    return q_text, s_text, hint, 2, _pair(c, d, 'c', 'd')


def gcse_sim_numbers_sum_difference():
    """Foundational: form two equations from a sum and a difference in words, then solve them."""
    kind = random.choice(['numbers', 'ages', 'parcels'])
    while True:
        big = random.randint(9, 40)
        small = random.randint(3, big - 3)
        s_tot, d_tot = big + small, big - small
        if len({big, small, s_tot, d_tot}) == 4:
            break
    if kind == 'numbers':
        q = f'The sum of two numbers is {s_tot}. Their difference is {d_tot}. Find the two numbers.'
        labels = ('Larger number', 'Smaller number')
        names = ('the larger number', 'the smaller number')
    elif kind == 'ages':
        q = (f'Ann is {d_tot} years older than Ben. The sum of their ages is {s_tot}. '
             f'Work out how old Ann and Ben are.')
        labels = ("Ann's age", "Ben's age")
        names = ("Ann's age", "Ben's age")
    else:
        q = (f'Two parcels weigh {s_tot} kg altogether. The heavier parcel is {d_tot} kg heavier than the lighter parcel. '
             f'Work out the mass of each parcel.')
        labels = ('Heavier parcel (kg)', 'Lighter parcel (kg)')
        names = ('the mass of the heavier parcel', 'the mass of the lighter parcel')
    s = (rf'Let \( x \) be {names[0]} and \( y \) be {names[1]}.<br>'
         rf'\( x + y = {s_tot} \) and \( x - y = {d_tot} \).<br>'
         rf'Add the equations: \( 2x = {s_tot + d_tot} \), so \( x = {big} \).<br>'
         rf'Then \( y = {s_tot} - {big} = {small} \).<br>'
         rf'Check: \( {big} - {small} = {d_tot} \). Answer: <strong>{big}</strong> and <strong>{small}</strong>.')
    hint = 'Call the two unknowns x and y. Write one equation for the sum and one for the difference, then add or subtract them.'
    record('linear_system_2', a1=1, b1=1, c1=s_tot, a2=1, b2=-1, c2=d_tot)
    return q, s, hint, 3, _pair(big, small, labels[0], labels[1])


def gcse_sim_rectangle_perimeter():
    """Foundational: form simultaneous equations for the length and width of a rectangle."""
    kind = random.choice(['more', 'times'])
    while True:
        w = random.randint(3, 12)
        if kind == 'more':
            d = random.randint(2, 8)
            ln = w + d
        else:
            d = random.randint(3, 5)
            ln = d * w
        perim = 2 * (ln + w)
        if len({w, ln, d, perim}) == 4:
            break
    if kind == 'more':
        q = (f'A rectangle has a perimeter of {perim} cm. Its length is {d} cm more than its width. '
             f'Work out the length and the width of the rectangle.')
        eqs = rf'\( 2l + 2w = {perim} \) and \( l - w = {d} \)'
        sol = (rf'Halve the perimeter: \( l + w = {perim // 2} \). Together with \( l - w = {d} \):<br>'
               rf'add the equations, \( 2l = {perim // 2 + d} \), so \( l = {ln} \).<br>'
               rf'Then \( w = {perim // 2} - {ln} = {w} \).')
        record('linear_system_2', derived=('a1', 'b1'), a1=2, b1=2, c1=perim, a2=1, b2=-1, c2=d)
    else:
        q = (f'A rectangle has a perimeter of {perim} cm. Its length is {d} times its width. '
             f'Work out the length and the width of the rectangle.')
        eqs = rf'\( 2l + 2w = {perim} \) and \( l = {d}w \)'
        sol = (rf'Halve the perimeter: \( l + w = {perim // 2} \). Put \( l = {d}w \) into it:<br>'
               rf'\( {d}w + w = {perim // 2} \), so \( {d + 1}w = {perim // 2} \) and \( w = {w} \).<br>'
               rf'Then \( l = {d} \times {w} = {ln} \).')
        record('linear_system_2', derived=('a1', 'b1'), a1=2, b1=2, c1=perim, a2=1, b2=-d, c2=0)
    s = (rf'Let the length be \( l \) cm and the width \( w \) cm. The two equations are {eqs}.<br>{sol}<br>'
         rf'Answer: length <strong>{ln} cm</strong>, width <strong>{w} cm</strong>.')
    hint = 'Write one equation for the perimeter (two lengths and two widths) and one from the sentence about the length. Then solve them together.'
    return q, s, hint, 3, _pair(ln, w, 'Length (cm)', 'Width (cm)')


@verifies('alg', task='solve_system')
def gcse_sim_equate_expressions():
    """Foundational: both equations give y, so the two right-hand sides are equal."""
    while True:
        x, y = random.randint(1, 7), random.randint(2, 18)
        m1, m2 = random.sample(range(1, 6), 2)
        c1, c2 = y - m1 * x, y - m2 * x
        if c1 != c2 and x != y and abs(c1) < 25 and abs(c2) < 25 and 0 not in (c1, c2):
            break
    q = (rf'Solve the simultaneous equations.<br>\( {_tex_line(m1, c1)} \) (1)<br>\( {_tex_line(m2, c2)} \) (2)')
    dm, dc = (m1 - m2, c2 - c1) if m1 > m2 else (m2 - m1, c1 - c2)
    collect = rf'\( x = {dc} \)' if dm == 1 else rf'\( {dm}x = {dc} \), so \( x = {x} \)'     # review: no "1x"
    s = (rf'Both equations give \( y \), so the right-hand sides are equal: \( {_lin(m1, c1)} = {_lin(m2, c2)} \).<br>'
         rf'Collect the \( x \) terms on one side and the numbers on the other: {collect}.<br>'
         rf'Put \( x = {x} \) into (1): \( y = {_times(m1, x)} {signed_term(c1)} = {y} \).<br>'
         rf'Answer: <strong>x = {x}, y = {y}</strong>.')
    hint = 'Both equations start with y =, so the two right-hand sides must be equal. Solve that equation for x, then find y.'
    return q, s, hint, 3, _pair(x, y)


def _times(c, value):
    """'3 \\times 7', '7' for a coefficient of 1, '-7' for -1; a negative value goes in brackets."""
    v = _raw(value) if Fraction(value) >= 0 else f'({_raw(value)})'
    if c == 1:
        return v
    if c == -1:
        return f'-{v}'
    return rf'{c} \times {v}'


def _tail(c, var):
    """' + 2y', ' - y'."""
    return f' {"+" if c > 0 else "-"} {var if abs(c) == 1 else str(abs(c)) + var}'


def _tail_num(c, value):
    """' + 2 \\times 7', ' - 7', ' + (-7)'."""
    v = _raw(value) if Fraction(value) >= 0 else f'({_raw(value)})'
    return f' {"+" if c > 0 else "-"} {v if abs(c) == 1 else rf"{abs(c)} \times {v}"}'


def _elim(a1, b1, c1, a2, b2, c2, lab1='(1)', lab2='(2)', vx='x', vy='y'):
    """HTML working that solves a whole-number system by elimination; returns (html, x, y).

    The letter removed is the one whose two coefficients need the smaller multipliers. The values found are asserted
    to satisfy both equations, so a slip in the working cannot be printed.
    """
    def tex(a, b, c):
        return rf'\( {_two_var(a, b, vx, vy)} = {c} \)'

    def price(idx):
        lcm = math.lcm(abs((a1, b1)[idx]), abs((a2, b2)[idx]))
        return lcm // abs((a1, b1)[idx]) + lcm // abs((a2, b2)[idx]), lcm
    cost_x, lcm_x = price(0)
    cost_y, lcm_y = price(1)
    k, lcm = (1, lcm_y) if cost_y <= cost_x else (0, lcm_x)       # k is the index of the letter removed
    e1, e2 = (a1, b1, c1), (a2, b2, c2)
    m1, m2 = lcm // abs(e1[k]), lcm // abs(e2[k])
    lines = []
    if m1 != 1:
        e1 = tuple(v * m1 for v in e1)
        lines.append(f'Multiply {lab1} by {m1}: {tex(*e1)}.')
    if m2 != 1:
        e2 = tuple(v * m2 for v in e2)
        lines.append(f'Multiply {lab2} by {m2}: {tex(*e2)}.')
    same = (e1[k] > 0) == (e2[k] > 0)
    o = 1 - k
    d_o = e1[o] - e2[o] if same else e1[o] + e2[o]
    d_c = e1[2] - e2[2] if same else e1[2] + e2[2]
    other = Fraction(d_c, d_o)
    other_var, removed_var = (vx, vy) if k == 1 else (vy, vx)
    found = (rf'\( {other_var} = {d_c} \)' if d_o == 1 else      # review: not "y = 24, so y = 24"
             rf'\( {"-" if d_o == -1 else d_o}{other_var} = {d_c} \), so \( {other_var} = {_raw(other)} \)')
    lines.append(f'{"Subtract" if same else "Add"} the equations to remove \\( {removed_var} \\): {found}.')
    if k == 1:          # x found, y removed
        removed = Fraction(c1 - a1 * other, b1)
        lhs = _times(a1, other) + _tail(b1, vy)
        lines.append(rf'Put \( {vx} = {_raw(other)} \) into {lab1}: \( {lhs} = {c1} \), so \( {vy} = {_raw(removed)} \).')
        xv, yv = other, removed
    else:               # y found, x removed
        removed = Fraction(c1 - b1 * other, a1)
        lhs = (vx if a1 == 1 else '-' + vx if a1 == -1 else f'{a1}{vx}') + _tail_num(b1, other)
        lines.append(rf'Put \( {vy} = {_raw(other)} \) into {lab1}: \( {lhs} = {c1} \), so \( {vx} = {_raw(removed)} \).')
        xv, yv = removed, other
    assert a1 * xv + b1 * yv == c1 and a2 * xv + b2 * yv == c2, 'elimination working does not satisfy the equations'
    return '<br>'.join(lines), xv, yv


def _dec_two(a, b):
    """'0.3x + 0.5y' / '0.7x - 0.5y' from two decimal coefficients."""
    def term(c, v):
        return f'{_num_text(abs(c))}{v}'
    return f'{"-" if a < 0 else ""}{term(a, "x")} {"+" if b > 0 else "-"} {term(b, "y")}'


@verifies('alg', task='solve_system')
def gcse_sim_decimal_coefficients():
    """Intermediate: equations with decimal coefficients (multiply by 10, then eliminate)."""
    while True:
        x, y = random.sample(range(1, 10), 2)
        a1, a2, b1, b2 = (Fraction(random.randint(2, 9), 10) for _ in range(4))
        if random.random() < 0.5:
            b2 = -b1                     # +b y in (1) and -b y in (2): add to remove y
            c1, c2 = a1 * x + b1 * y, a2 * x + b2 * y
            ok = a1 != a2
        else:
            a2 = a1                      # the same x term in both: subtract to remove x
            c1, c2 = a1 * x + b1 * y, a2 * x + b2 * y
            ok = b1 != b2
        if ok and c1 > 0 and c2 > 0 and c1 != c2 and a1 * b2 - a2 * b1 != 0:
            break
    A1, B1, C1, A2, B2, C2 = (int(v * 10) for v in (a1, b1, c1, a2, b2, c2))
    q = (rf'Solve the simultaneous equations.<br>\( {_dec_two(a1, b1)} = {_num_text(c1)} \) (1)<br>'
         rf'\( {_dec_two(a2, b2)} = {_num_text(c2)} \) (2)')
    work, xv, yv = _elim(A1, B1, C1, A2, B2, C2, '(3)', '(4)')
    assert (xv, yv) == (x, y)
    s = (rf'Multiply both equations by 10 to remove the decimals.<br>'
         rf'\( {_two_var(A1, B1)} = {C1} \) (3)<br>\( {_two_var(A2, B2)} = {C2} \) (4)<br>{work}<br>'
         rf'Answer: <strong>x = {x}, y = {y}</strong>.')
    hint = 'Multiply every term of both equations by 10 so that all the coefficients are whole numbers. Then eliminate one letter.'
    return q, s, hint, 4, _pair(x, y)


def gcse_sim_two_item_check():
    """Intermediate: two purchases give the price of each item; a third purchase checks the prices."""
    items = random.choice([('notebooks', 'notebook', 'pens', 'pen'), ('sandwiches', 'sandwich', 'drinks', 'drink'),
                           ('magazines', 'magazine', 'puzzle books', 'puzzle book')])
    while True:
        pa, pb = (Fraction(random.randrange(30, 400, 5), 100) for _ in range(2))
        n1a, n1b, n2a, n2b, n3a, n3b = (random.randint(1, 6) for _ in range(6))
        det = n1a * n2b - n2a * n1b
        if det != 0 and pa != pb and (n3a, n3b) not in ((n1a, n1b), (n2a, n2b)) and n3a != n3b \
                and n1a * pa + n1b * pb != n2a * pa + n2b * pb:
            break
    t1, t2, t3 = n1a * pa + n1b * pb, n2a * pa + n2b * pb, n3a * pa + n3b * pb

    def buy(na, nb):
        return f'{na} {items[0] if na != 1 else items[1]} and {nb} {items[2] if nb != 1 else items[3]}'
    q = (f'{buy(n1a, n1b).capitalize()} cost {_money2(t1)}. {buy(n2a, n2b).capitalize()} cost {_money2(t2)}.<br>'
         f'(a) Work out the price of one {items[1]} and the price of one {items[3]}.<br>'
         f'(b) Use your answers to work out the cost of {buy(n3a, n3b)}.')
    work, av, bv = _elim(n1a, n1b, int(t1 * 100), n2a, n2b, int(t2 * 100), vx='a', vy='b')
    assert (av, bv) == (pa * 100, pb * 100)
    s = (rf'Let \( a \) be the price of one {items[1]} and \( b \) the price of one {items[3]}, both in pence.<br>'
         rf'\( {_two_var(n1a, n1b, "a", "b")} = {int(t1 * 100)} \) (1)<br>\( {_two_var(n2a, n2b, "a", "b")} = {int(t2 * 100)} \) (2)<br>'
         f'{work}<br>'
         f'So one {items[1]} costs {_money2(pa)} and one {items[3]} costs {_money2(pb)}.<br>'
         f'Check with (2): {n2a} × {_money2(pa)} + {n2b} × {_money2(pb)} = {_money2(t2)}, as in the question.<br>'
         f'(b) {n3a} × {_money2(pa)} + {n3b} × {_money2(pb)} = <strong>{_money2(t3)}</strong>.')
    hint = 'Write an equation for each purchase using a and b for the two prices. Solve them together, then use the prices for the third purchase.'
    record('sim_two_item_check', n1a=n1a, n1b=n1b, t1=float(t1), n2a=n2a, n2b=n2b, t2=float(t2), n3a=n3a, n3b=n3b)
    return q, s, hint, 5, _fields(
        [_dec_raw(pa), _dec_raw(pb), _dec_raw(t3)],
        [f'Price of one {items[1]} (£)', f'Price of one {items[3]} (£)', 'Cost of the third purchase (£)'])


def gcse_sim_value_of_expression():
    """Intermediate: solve a pair of equations, then use both values in a new expression."""
    while True:
        x, y = random.sample(range(1, 9), 2)
        a1, b1 = random.randint(1, 5), random.randint(1, 5)
        a2, b2 = random.randint(1, 5), random.randint(1, 5)
        c1, c2 = a1 * x + b1 * y, a2 * x - b2 * y
        ask = random.choice(['xy', 'x2y2'])
        value = x * y if ask == 'xy' else x * x + y * y
        if a1 * (-b2) - a2 * b1 != 0 and c2 > 0 and value not in (x, y, c1, c2) and (a1, b1) != (a2, -b2):
            break
    expr_text = r'xy' if ask == 'xy' else r'x^{2} + y^{2}'
    q = (rf'Solve the simultaneous equations.<br>\( {_two_var(a1, b1)} = {c1} \) (1)<br>\( {_two_var(a2, -b2)} = {c2} \) (2)<br>'
         rf'Then work out the value of \( {expr_text} \).')
    work, xv, yv = _elim(a1, b1, c1, a2, -b2, c2)
    assert (xv, yv) == (x, y)
    final = (rf'\( xy = {x} \times {y} = {value} \)' if ask == 'xy'
             else rf'\( x^{{2}} + y^{{2}} = {x * x} + {y * y} = {value} \)')
    s = f'{work}<br>So x = {x} and y = {y}.<br>{final}. Answer: <strong>{value}</strong>.'
    hint = 'Find x and y first by elimination. Then put both numbers into the expression the question asks for.'
    record('sim_expr_value', a1=a1, b1=b1, c1=c1, a2=a2, b2=-b2, c2=c2, ask=ask)
    return q, s, hint, 4, value


def gcse_sim_equal_sides():
    """Intermediate: opposite sides of a rectangle are equal, which gives two equations."""
    while True:
        x, y = random.sample(range(1, 9), 2)
        a1, b1, a2, b2 = (random.randint(1, 4) for _ in range(4))
        ab, bc = a1 * x + b1 * y, a2 * x + b2 * y
        if a1 * b2 - a2 * b1 != 0 and ab != bc and ab <= 40 and bc <= 40 and len({ab, bc, x, y}) == 4:
            break
    ab_t, bc_t = _two_var(a1, b1), _two_var(a2, b2)
    q = (rf'\( ABCD \) is a rectangle. \( AB = ({ab_t}) \) cm, \( BC = ({bc_t}) \) cm, \( DC = {ab} \) cm and '
         rf'\( AD = {bc} \) cm.<br>Find the values of \( x \) and \( y \).')
    work, xv, yv = _elim(a1, b1, ab, a2, b2, bc)
    assert (xv, yv) == (x, y)
    s = (rf'Opposite sides of a rectangle are equal, so \( AB = DC \) and \( BC = AD \).<br>'
         rf'\( {ab_t} = {ab} \) (1)<br>\( {bc_t} = {bc} \) (2)<br>{work}<br>Answer: <strong>x = {x}, y = {y}</strong>.')
    hint = 'Opposite sides of a rectangle are equal. Write an equation for each pair of opposite sides, then solve them together.'
    record('linear_system_2', a1=a1, b1=b1, c1=ab, a2=a2, b2=b2, c2=bc)
    return q, s, hint, 4, _pair(x, y)


@verifies('alg', task='solve_system')
def gcse_sim_fractional_coefficients():
    """Difficult: equations with fractions as coefficients (clear the fractions first)."""
    while True:
        p, q_, r, s_ = (random.choice([2, 3, 4, 5, 6]) for _ in range(4))
        sy = random.choice([1, -1])
        lx, ly = math.lcm(p, r), math.lcm(q_, s_)
        x, y = lx * random.randint(1, 3), ly * random.randint(1, 3)
        a1, b1, a2, b2 = Fraction(1, p), Fraction(1, q_), Fraction(1, r), Fraction(sy, s_)
        c1, c2 = a1 * x + b1 * y, a2 * x + b2 * y
        if (a1 * b2 - a2 * b1 != 0 and x != y and x <= 36 and y <= 36 and c1.denominator == 1 and c2.denominator == 1
                and c1 > 0 and c2 > 0 and (p, q_) != (r, s_) and c1 != c2):
            break

    def eq(a, b):
        return rf'\dfrac{{x}}{{{a.denominator}}} {"+" if b > 0 else "-"} \dfrac{{y}}{{{b.denominator}}}'
    L1, L2 = math.lcm(p, q_), math.lcm(r, s_)
    A1, B1, C1 = int(a1 * L1), int(b1 * L1), int(c1 * L1)
    A2, B2, C2 = int(a2 * L2), int(b2 * L2), int(c2 * L2)
    q = (rf'Solve the simultaneous equations.<br>\( {eq(a1, b1)} = {int(c1)} \) (1)<br>\( {eq(a2, b2)} = {int(c2)} \) (2)')
    work, xv, yv = _elim(A1, B1, C1, A2, B2, C2, '(3)', '(4)')
    assert (xv, yv) == (x, y)
    s = (rf'Clear the fractions: multiply (1) by {L1} and (2) by {L2}.<br>'
         rf'\( {_two_var(A1, B1)} = {C1} \) (3)<br>\( {_two_var(A2, B2)} = {C2} \) (4)<br>{work}<br>'
         rf'Answer: <strong>x = {x}, y = {y}</strong>.')
    hint = 'Multiply each equation by a number that every denominator divides into, so there are no fractions left. Then eliminate one letter.'
    return q, s, hint, 4, _pair(x, y)


def _ages_cases():
    """(k, m, n, child, parent): the parent is k times as old now and m times as old in n years."""
    out = []
    for k in range(3, 8):
        for m in (2, 3, 4):
            for n in range(2, 21):
                if k <= m or (n * (m - 1)) % (k - m):
                    continue
                d = n * (m - 1) // (k - m)
                if 3 <= d <= 15 and k * d - d >= 18 and k * d <= 70 and len({k, m, n, d, k * d}) == 5:
                    out.append((k, m, n, d, k * d))
    return out


_AGES_CASES = _ages_cases()


def gcse_sim_ages():
    """Difficult: two age statements (now and in some years) make simultaneous equations."""
    # review 2026-10-28: the old ranges gave 7 different questions in 3,000 draws; these are every (k, m, n) with a
    # whole-number child of 3 to 15, a parent at least 18 years older and at most 70 (23 cases, 46 with the names)
    k, m, n, d, f = random.choice(_AGES_CASES)
    who = random.choice([('A mother', 'her daughter', "Mother's age now", "Daughter's age now"),
                         ('A father', 'his son', "Father's age now", "Son's age now")])
    times = 'twice' if m == 2 else f'{m} times'
    q = (f'{who[0]} is {k} times as old as {who[1]}. In {n} years\' time, the {who[0][2:]} will be {times} as old as {who[1]}. '
         f'Work out how old each of them is now.')
    s = (rf'Let the child be \( c \) years old now, so the parent is \( {k}c \) years old.<br>'
         rf'In {n} years: parent \( {k}c + {n} \), child \( c + {n} \).<br>'
         rf'\( {k}c + {n} = {m}(c + {n}) \), so \( {k}c + {n} = {m}c + {m * n} \).<br>'
         + (rf'\( c = {m * n - n} \).<br>' if k - m == 1 else rf'\( {k - m}c = {m * n - n} \), so \( c = {d} \).<br>') +
         rf'The parent is \( {k} \times {d} = {f} \). Check: in {n} years they are {f + n} and {d + n}, and {m} × {d + n} = {f + n}.<br>'
         rf'Answer: <strong>{f}</strong> and <strong>{d}</strong>.')
    hint = 'Let the child be c years old, so the parent is a multiple of c. Write what each age will be in the future and set up the second equation from the sentence about "times as old".'
    record('sim_ages', derived=('m',) if m == 2 else (), k=k, n=n, m=m)
    return q, s, hint, 5, _pair(f, d, who[2], who[3])


def gcse_sim_no_solution_value():
    """Difficult: the value of k that makes two lines parallel (no solution) or the same line (infinitely many)."""
    while True:
        a1, b1 = random.randint(2, 4), random.randint(2, 7)
        mult = random.randint(2, 4)
        a2, k = mult * a1, mult * b1
        kind = random.choice(['none', 'infinite'])
        c1 = random.randint(3, 12)
        c2 = mult * c1 if kind == 'infinite' else mult * c1 + random.choice([-3, -2, 2, 3, 4])
        if c2 > 0 and len({k, a1, b1, a2, c1, c2}) == 6:
            break
    what = 'no solution' if kind == 'none' else 'infinitely many solutions'
    q = (rf'Find the value of \( k \) for which the simultaneous equations \( {_two_var(a1, b1)} = {c1} \) and '
         rf'\( {a2}x + ky = {c2} \) have {what}.')
    if kind == 'none':
        why = (rf'The lines must be parallel, with different right-hand sides. Multiply (1) by {mult}: '
               rf'\( {a2}x + {mult * b1}y = {mult * c1} \). The left-hand side matches \( {a2}x + ky \) when \( k = {k} \), '
               rf'and {mult * c1} is not {c2}, so the lines are parallel and never meet.')
    else:
        why = (rf'The two equations must be the same line. Multiply (1) by {mult}: '
               rf'\( {a2}x + {mult * b1}y = {mult * c1} \). This is the second equation exactly when \( k = {k} \), '
               rf'because {mult * c1} = {c2}.')
    s = f'{why}<br>Answer: <strong>k = {k}</strong>.'
    hint = 'Make the x terms in the two equations match by multiplying the first equation. Compare what is left to decide what k must be.'
    record('sim_parallel_k', kind=kind, a1=a1, b1=b1, c1=c1, a2=a2, c2=c2)
    return q, s, hint, 4, _lin_ans(k, 'k')


def gcse_sim_equal_cost():
    """Difficult: two cost formulas (a fixed fee plus a rate) are equal at one amount."""
    ctx = random.choice([('taxi firm', 'Firm A', 'Firm B', 'per mile', 'length of the journey in miles', 'Length of the journey (miles)'),
                         ('gym', 'Gym A', 'Gym B', 'per month', 'number of months', 'Number of months'),
                         ('van hire company', 'Company A', 'Company B', 'per day', 'number of days', 'Number of days')])
    while True:
        n = random.randint(3, 12)
        r2 = random.randint(1, 6)
        dr = random.randint(1, 4)
        r1 = r2 + dr
        f1 = random.randint(2, 30)
        f2 = f1 + dr * n
        cost = f1 + r1 * n
        if len({n, cost, r1, r2, f1, f2}) == 6:
            break
    word = 'fee' if ctx[0] != 'gym' else 'joining fee'
    q = (f'A {ctx[0]} offers two deals. {ctx[1]} charges a fixed {word} of £{f1} plus £{r1} {ctx[3]}. '
         f'{ctx[2]} charges a fixed {word} of £{f2} plus £{r2} {ctx[3]}. '
         f'Both deals cost the same for one particular amount of use. Work out the {ctx[4]} and that cost.')
    def rate(r):
        return 'n' if r == 1 else f'{r}n'          # review: "9 + n", not "9 + 1n"
    collect = rf'\( n = {f2 - f1} \)' if dr == 1 else rf'\( {dr}n = {f2 - f1} \), so \( n = {n} \)'
    s = (rf'Let \( n \) be the {ctx[4]}. The costs are equal when '
         rf'\( {f1} + {rate(r1)} = {f2} + {rate(r2)} \).<br>'
         rf'Collect the \( n \) terms and the numbers: {collect}.<br>'
         rf'Cost: \( {f1} + {_times(r1, n)} = £{cost} \). Check: \( {f2} + {_times(r2, n)} = £{cost} \).<br>'
         rf'Answer: <strong>{n}</strong> and <strong>£{cost}</strong>.')
    hint = 'Write each cost as a fixed fee plus a rate times the amount used. Set the two costs equal and solve for the amount, then find the cost.'
    record('sim_equal_cost', f1=f1, r1=r1, f2=f2, r2=r2)
    return q, s, hint, 4, _pair(n, cost, ctx[5], 'Cost (£)')


# ─────────────────────────────────────────────────────────────────────────────
# Completing the square
# ─────────────────────────────────────────────────────────────────────────────

def _quad(a, b, c, var='x'):
    """'x^2 + 6x - 7', '-x^2 + 4x', '2x^2 - 3' (no 1x^2, no 0x, no '+ -')."""
    lead = '' if a == 1 else '-' if a == -1 else str(a)
    out = f'{lead}{var}^2'
    if b:
        out += f' {"+" if b > 0 else "-"} {var if abs(b) == 1 else str(abs(b)) + var}'
    if c:
        out += f' {"+" if c > 0 else "-"} {abs(c)}'
    return out


def _sq(p, var='x'):
    """'(x + 3)^2' or '(x - 3)^2'."""
    return f'({var} {"+" if p >= 0 else "-"} {abs(p)})^2'


def _shift(k):
    """' + 5' / ' - 5' after a bracket ('' for 0)."""
    return '' if k == 0 else f' {"+" if k > 0 else "-"} {abs(k)}'


def _frac_tex(f):
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    return rf'{"-" if f < 0 else ""}\frac{{{abs(f.numerator)}}}{{{f.denominator}}}'


@verifies('alg', task='cts_half')
def gcse_cts_f_negative_half():
    """Foundational: p in (x + p)^2 + q when the x coefficient is negative, so p is negative."""
    p = random.randint(2, 7)
    c = random.randint(-9, 12)
    b = -2 * p
    q = (rf'The expression \( {_quad(1, b, c)} \) can be written in the form \( (x + p)^2 + q \). Find the value of \( p \).')
    s = (rf'Half of the coefficient of \( x \): \( {b} \div 2 = {-p} \).<br>So \( {_quad(1, b, c)} = (x - {p})^2 {_shift(c + 0 - p * p)} \) '
         rf'and <strong>\(p = {-p}\)</strong>.')
    hint = 'p is half of the number in front of x, keeping its sign.'
    return q, s, hint, 1, -p



@verifies('alg', task='min_x')
def gcse_cts_f_line_of_symmetry():
    """Foundational: the line of symmetry of y = (x - p)^2 + k read from the completed-square form."""
    p = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7])
    k = random.choice([-9, -7, -5, -4, -3, -2, 2, 3, 4, 6, 8])
    form = f'{_sq(-p)}{_shift(k)}'
    q = (rf'The graph of \( y = {form} \) is a parabola with a vertical line of symmetry. '
         rf'Write down the equation of the line of symmetry, in the form \( x = \ldots \).')
    s = (rf'The squared bracket is zero when \( x = {p} \), which is the turning point, so the line of symmetry is '
         rf'<strong>x = {p}</strong>.')
    hint = 'The line of symmetry passes through the turning point. Find the x value that makes the bracket equal to zero.'
    return q, s, hint, 2, _lin_ans(p, 'x')


def gcse_cts_f_read_min_value():
    """Foundational: the least value of a completed-square expression."""
    p = random.choice([-5, -4, -3, -2, 2, 3, 4, 5, 6])
    k = random.choice([-12, -9, -8, -6, -5, -3, 2, 4, 7])
    q = rf'Write down the minimum value of \( y = {_sq(p)}{_shift(k)} \).'
    s = (rf'A square is never negative, so \( {_sq(p)} \) is least when it is 0. '
         rf'The minimum value of \( y \) is <strong>{k}</strong>.')
    hint = 'A squared bracket is smallest (zero) when the bracket equals zero. What is left then?'
    # review 2026-10-28: a record family (was @verifies('alg', task='extremum_value')) so a topic rule can name the
    # x-value typed for the least value; the question and answer are unchanged
    record('cts_min_read', p=p, k=k)
    return q, s, hint, 2, k


def gcse_cts_f_find_q_given_p():
    """Foundational: the squared bracket is given; find the constant q in the completed form."""
    p = random.randint(2, 6)
    c = random.randint(-8, 14)
    k = c - p * p
    if k == 0:
        c += 1
        k = c - p * p
    b = 2 * p
    q = (rf'Given that \( {_quad(1, b, c)} = (x + {p})^2 + q \) for all values of \( x \), find the value of \( q \).')
    s = (rf'Expand the bracket: \( (x + {p})^2 = x^2 + {b}x + {p * p} \).<br>'
         rf'The constant terms must match: \( {p * p} + q = {c} \), so \( q = {c} - {p * p} \) = <strong>{k}</strong>.')
    hint = 'Expand the bracket, then compare the numbers on its own with the number at the end of the expression.'
    record('cts_q_given_p', derived=('p',), b=b, c=c, p=p)
    return q, s, hint, 2, k


def gcse_cts_i_hence_solve():
    """Intermediate: the completed-square form is given; use it to solve the quadratic equation."""
    while True:
        p = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
        d = random.randint(2, 7)
        if d != abs(p):
            break
    b, c = 2 * p, p * p - d * d
    r1, r2 = -p + d, -p - d
    q = (rf'The expression \( {_quad(1, b, c)} \) can be written as \( {_sq(p)} - {d * d} \).<br>'
         rf'Use this to solve \( {_quad(1, b, c)} = 0 \).')
    s = (rf'\( {_sq(p)} - {d * d} = 0 \), so \( {_sq(p)} = {d * d} \).<br>'
         rf'Square root both sides: \( x {"+" if p >= 0 else "-"} {abs(p)} = \pm {d} \).<br>'
         rf'\( x = {-p} + {d} = {r1} \) or \( x = {-p} - {d} = {r2} \).')
    hint = 'Set the completed-square form equal to zero, add the number to both sides, then take the square root. Remember the negative root.'
    record('cts_hence_solve', derived=('c',), b=b, c=c, p=p, k=-d * d)
    return q, s, hint, 3, _roots(r1, r2)


def gcse_cts_i_a_minus_square():
    """Intermediate: write c + bx - x^2 as a - (x - p)^2."""
    p = random.randint(1, 5)
    c = random.choice([v for v in range(-4, 13) if v])      # review: not "0 + 4x - x^2"
    b = 2 * p
    a = c + p * p
    q = (rf'Write \( {c} + {b}x - x^2 \) in the form \( a - (x - p)^2 \).')
    s = (rf'\( {c} + {b}x - x^2 = {c} - (x^2 - {b}x) \).<br>'
         rf'\( x^2 - {b}x = (x - {p})^2 - {p * p} \), so \( {c} - (x - {p})^2 + {p * p} = {a} - (x - {p})^2 \).<br>'
         rf'<strong>a = {a}, p = {p}</strong>.')
    hint = 'Take the minus sign outside the x terms first, then complete the square on x^2 and the x term.'
    record('cts_a_minus_sq', derived=('a', 'p'), c=c, b=b, a=a, p=p)
    return q, s, hint, 3, _pair(a, p, 'a', 'p')


@verifies('alg', task='min_point')
def gcse_cts_i_turning_point_expression():
    """Intermediate: the turning point of a quadratic by completing the square."""
    p = random.randint(2, 6)
    sign = random.choice([-1, 1])
    c = random.randint(-8, 14)
    b = sign * 2 * p
    q = (rf'By completing the square, find the coordinates of the minimum point of the curve \( y = {_quad(1, b, c)} \).')
    h, k = -sign * p, c - p * p
    s = (rf'\( {_quad(1, b, c)} = {_sq(sign * p)}{_shift(k)} \).<br>The minimum is where the bracket is zero, '
         rf'so <strong>({h}, {k})</strong>.')
    hint = 'Write the expression as a squared bracket plus a number. The turning point is where the bracket is zero.'
    return q, s, hint, 3, _pair(h, k, 'x', 'y')


def gcse_cts_i_count_roots():
    """Intermediate: how many solutions has the equation, decided from the completed-square form."""
    p = random.randint(1, 6)
    b = random.choice([-2, 2]) * p
    k = random.choice([-7, -4, -3, -1, 0, 0, 2, 3, 5, 8, 11])
    c = p * p + k
    h = b // 2
    n = 2 if k < 0 else 1 if k == 0 else 0
    q = (rf'Write \( {_quad(1, b, c)} \) in completed-square form. Use your answer to state how many real solutions '
         rf'\( {_quad(1, b, c)} = 0 \) has.')
    why = (rf'\( {_sq(h)} = {-k} \) has two solutions because {-k} is positive.' if k < 0 else
           rf'\( {_sq(h)} = 0 \) has one solution, \( x = {-h} \).' if k == 0 else
           rf'\( {_sq(h)} = {-k} \) has no real solutions because a square cannot be negative.')
    s = (rf'\( {_quad(1, b, c)} = {_sq(h)}{_shift(k)} \).<br>Then {why} Number of solutions: <strong>{n}</strong>.')
    hint = 'Rearrange the completed form to (bracket)^2 = a number. A square cannot equal a negative number.'
    record('cts_count_roots', b=b, c=c)
    return q, s, hint, 3, n


@verifies('alg', task='solve_poly')
def gcse_cts_d_leading_coefficient_solve():
    """Difficult: solve a quadratic with a leading coefficient above 1 by completing the square."""
    a = random.choice([2, 3, 4])
    p = random.choice([-4, -3, -2, -1, 1, 2, 3])
    d = random.randint(1, 4)
    if d == abs(p):
        d += 1
    b, c = 2 * a * p, a * (p * p - d * d)
    q = rf'Solve \( {_quad(a, b, c)} = 0 \) by completing the square.'
    r1, r2 = -p + d, -p - d
    s = (rf'Divide by {a}: \( {_quad(1, 2 * p, p * p - d * d)} = 0 \).<br>'
         rf'Complete the square: \( {_sq(p)} - {d * d} = 0 \), so \( {_sq(p)} = {d * d} \).<br>'
         rf'\( x {"+" if p >= 0 else "-"} {abs(p)} = \pm {d} \), so \( x = {r1} \) or \( x = {r2} \).')
    hint = f'Divide every term by {a} first so that the x^2 term has coefficient 1, then complete the square.'
    return q, s, hint, 4, _roots(r1, r2)


def gcse_cts_d_min_non_monic():
    """Difficult: the least value of a quadratic whose x^2 coefficient is not 1."""
    a = random.choice([2, 3, 5])
    p = random.randint(1, 4) * random.choice([-1, 1])
    k = random.choice([-11, -7, -5, -3, -2, 1, 4, 6])
    b, c = 2 * a * p, a * p * p + k
    q = rf'Find the minimum value of \( {_quad(a, b, c)} \) by completing the square.'
    s = (rf'\( {_quad(a, b, c)} = {a}({_quad(1, 2 * p, p * p)}){_shift(k)} = {a}{_sq(p)}{_shift(k)} \).<br>'
         rf'The bracket is least (zero) at \( x = {-p} \), so the minimum value is <strong>{k}</strong>.')
    hint = f'Take {a} out of the x^2 and x terms, complete the square inside the bracket, then multiply the bracket back out.'
    record('cts_min_nonmonic', a=a, b=b, c=c)       # review: a record family (was @verifies extremum_value), for the hints
    return q, s, hint, 4, k


@verifies('alg', task='complete_square')
def gcse_cts_d_fraction_form():
    """Difficult: odd coefficient of x, so p is a fraction."""
    b = random.choice([-9, -7, -5, -3, 3, 5, 7, 9])
    c = random.choice([v for v in range(-6, 9) if v])       # review: c = 0 printed "- 81/4 + 0" in the working
    p = Fraction(b, 2)
    k = c - p * p
    kind = 'minus' if p < 0 else 'plus'
    q = rf'Write \( {_quad(1, b, c)} \) in the form \( (x + p)^2 + q \). Give the values of \( p \) and \( q \) as decimals.'
    s = (rf'Half of {b} is \( {_frac_tex(p)} = {_num_text(p)} \).<br>'
         rf'\( {_quad(1, b, c)} = \left(x {"+" if p >= 0 else "-"} {_frac_tex(abs(p))}\right)^2 - {_frac_tex(p * p)}{_shift(c)} \) '
         rf'= \( \left(x {"+" if p >= 0 else "-"} {_frac_tex(abs(p))}\right)^2 {"+" if k >= 0 else "-"} {_frac_tex(abs(k))} \), '
         rf'so \( p = {_num_text(p)} \) and \( q = {_num_text(k)} \).')
    hint = 'Half of an odd number is a fraction. Subtract its square from the constant.'
    return q, s, hint, 4, {'type': 'completed_square', 'kind': kind, 'values': (_dec_raw(abs(p)), _dec_raw(k))}


def gcse_cts_d_vertex_to_coefficients():
    """Difficult: the minimum point is given; find b and c in y = x^2 + bx + c."""
    h = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
    k = random.choice([-9, -8, -7, -5, -4, -3, 2, 3, 5])
    b, c = -2 * h, h * h + k
    q = (rf'The curve \( y = x^2 + bx + c \) has its minimum point at \( ({h}, {k}) \). Find the values of \( b \) and \( c \).')
    s = (rf'The minimum point means \( y = (x {"-" if h >= 0 else "+"} {abs(h)})^2 {_shift(k)} \).<br>'
         rf'Expand: \( x^2 {"-" if h >= 0 else "+"} {abs(b)}x + {h * h} {_shift(k)} \).<br>'
         rf'So <strong>b = {b}</strong> and <strong>c = {c}</strong>.')
    hint = 'Write the equation in the form (x - h)^2 + k using the minimum point, then expand it.'
    record('cts_from_vertex', h=h, k=k)
    return q, s, hint, 4, _pair(b, c, 'b', 'c')


# ─────────────────────────────────────────────────────────────────────────────
# Quadratic simultaneous equations
# ─────────────────────────────────────────────────────────────────────────────

def _fields4(r1, y1, r2, y2):
    return _fields([_raw(r1), _raw(y1), _raw(r2), _raw(y2)],
                   ['x (1st solution)', 'y (1st solution)', 'x (2nd solution)', 'y (2nd solution)'])


def _distinct_roots(lo=-7, hi=7):
    while True:
        r1, r2 = sorted((random.randint(lo, hi), random.randint(lo, hi)))
        if r1 != r2 and r1 + r2 != 0 and r1 * r2 != 0:
            return r1, r2


def _factor_text(r, var='x'):
    return f'({var} {"-" if r > 0 else "+"} {abs(r)})'


def _sq_num(v):
    """'4^2', '(-3)^2' for a number squared in the working (review: not '(4)^2')."""
    return f'({v})^2' if v < 0 else f'{v}^2'


def _factors(r1, r2, var='x'):
    """'(x + 3)(x - 2)', or 'x(x + 5)' when a root is 0 (review: not '(x + 5)(x + 0)')."""
    if r1 == 0 or r2 == 0:
        return f'{var}{_factor_text(r2 if r1 == 0 else r1, var)}'
    return f'{_factor_text(r1, var)}{_factor_text(r2, var)}'


def gcse_qsim_f_expand_substitution():
    """Foundational: replace y in y = x^2 by the line, then collect everything on one side."""
    r1, r2 = _distinct_roots(-6, 6)
    m, c = r1 + r2, -r1 * r2
    q = (rf'The curve \( y = x^2 \) and the line \( y = {_lin(m, c)} \) meet where \( x^2 = {_lin(m, c)} \).<br>'
         rf'Rearrange this to the form \( x^2 + px + q = 0 \) and give the values of \( p \) and \( q \).')
    s = (rf'Subtract \( {_lin(m, 0)} \) and {"add" if c < 0 else "subtract"} {abs(c)} on both sides to get zero on the right:<br>'
         rf'\( {_quad(1, -m, -c)} = 0 \).<br>'
         rf'So <strong>p = {-m}</strong> and <strong>q = {-c}</strong>.')
    hint = 'Move every term to the left-hand side. Subtracting a positive term makes it negative.'
    record('qsim_sub_coeffs', m=m, c=c)
    return q, s, hint, 2, _pair(-m, -c, 'p', 'q')


def gcse_qsim_f_y_from_x_values():
    """Foundational: the x-values of the intersection points are given; find the y-values from the line."""
    r1, r2 = _distinct_roots(-6, 6)
    m, c = r1 + r2, -r1 * r2
    q = (rf'The curve \( y = x^2 \) meets the line \( y = {_lin(m, c)} \) where \( x = {r1} \) and \( x = {r2} \).<br>'
         rf'Work out the \( y \)-coordinate at each of these points.')
    s = (rf'Use either equation. With \( y = x^2 \): \( y = {_sq_num(r1)} = {r1 * r1} \) and \( y = {_sq_num(r2)} = {r2 * r2} \).<br>'
         rf'Check with the line: \( {_times(m, r1)} {"+" if c >= 0 else "-"} {abs(c)} = {r1 * r1} \).<br>'
         rf'The points are <strong>({r1}, {r1 * r1})</strong> and <strong>({r2}, {r2 * r2})</strong>.')
    hint = 'Put each x-value into y = x^2 (or into the line). Check that both equations give the same y.'
    record('qsim_y_from_x', m=m, c=c, x1=r1, x2=r2)
    return q, s, hint, 2, _fields([_raw(r1 * r1), _raw(r2 * r2)], [f'y when x = {r1}', f'y when x = {r2}'])


def _lattice_chords():
    """(r2, (x1, y1), (x2, y2), m, c): two lattice points on x^2 + y^2 = r2 that lie on a line y = mx + c, m and c whole."""
    out = []
    for r2 in (13, 25, 50, 65):
        pts = [(x, y) for x in range(-9, 10) for y in range(-9, 10) if x * x + y * y == r2]
        for a in pts:
            for b in pts:
                if a[0] < b[0]:
                    dx, dy = b[0] - a[0], b[1] - a[1]
                    if dy % dx == 0:
                        m = dy // dx
                        c = a[1] - m * a[0]
                        if m != 0 and c != 0:
                            out.append((r2, a, b, m, c))
    return out


_CHORDS = _lattice_chords()


def gcse_qsim_f_circle_line_y():
    """Foundational: a circle and a line meet at a given x; find the y-coordinate."""
    r2, (x1, y1), (x2, y2), m, c = random.choice(_CHORDS)
    x = random.choice([v for v in (x1, x2) if v != 0] or [x1, x2])      # review C11: x = 0 makes y the intercept, read off
    y = m * x + c
    q = (rf'The circle \( x^2 + y^2 = {r2} \) and the line \( y = {_lin(m, c)} \) meet at a point where \( x = {x} \). '
         rf'Work out the value of \( y \) at that point.')
    s = (rf'Put \( x = {x} \) into the line: \( y = {_times(m, x)} {"+" if c >= 0 else "-"} {abs(c)} = {y} \).<br>'
         rf'Check in the circle: \( {_sq_num(x)} + {_sq_num(y)} = {x * x} + {y * y} = {r2} \). So <strong>y = {y}</strong>.')
    hint = 'The line is the easier equation to use. Put the x-value into it, then check the point in the circle equation.'
    record('qsim_circle_line_y', r2=r2, m=m, c=c, x=x)
    return q, s, hint, 2, _lin_ans(y, 'y')


@verifies('alg', task='solve_poly')
def gcse_qsim_f_solve_substituted():
    """Foundational: solve the quadratic that substitution produced, then say what the roots are."""
    r1, r2 = _distinct_roots(-8, 8)
    b, c = -(r1 + r2), r1 * r2
    q = (rf'Substituting a line into a curve gives \( {_quad(1, b, c)} = 0 \).<br>'
         rf'Solve this equation to find the two possible values of \( x \).')
    s = (rf'Factorise: \( {_factor_text(r1)}{_factor_text(r2)} = 0 \).<br>So <strong>x = {r1}</strong> or <strong>x = {r2}</strong>.')
    hint = 'Find two numbers that multiply to give the constant and add to give the number in front of x.'
    return q, s, hint, 3, _roots(r1, r2)


@verifies('alg', task='qsim_solve')
def gcse_qsim_i_shifted_parabola():
    """Intermediate: y = x^2 + k against a line; two integer intersection points."""
    r1, r2 = _distinct_roots(-5, 5)
    k = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5])
    m = r1 + r2
    c = k - r1 * r2
    q = rf'Solve the simultaneous equations.<br>\( y = {_quad(1, 0, k)} \)<br>\( y = {_lin(m, c)} \)'
    y1, y2 = m * r1 + c, m * r2 + c
    s = (rf'Equate: \( {_quad(1, 0, k)} = {_lin(m, c)} \), so \( {_quad(1, -m, k - c)} = 0 \).<br>'
         rf'\( {_factor_text(r1)}{_factor_text(r2)} = 0 \), so \( x = {r1} \) or \( x = {r2} \).<br>'
         rf'Put into the line: \( y = {y1} \) and \( y = {y2} \).<br>'
         rf'Solutions: <strong>({r1}, {y1})</strong> and <strong>({r2}, {y2})</strong>.')
    hint = 'Make the two expressions for y equal, collect on one side, factorise, then find each y using the line.'
    return q, s, hint, 5, _fields4(r1, y1, r2, y2)


def gcse_qsim_i_circle_line():
    """Intermediate: a circle of whole-number radius squared and a line through two lattice points."""
    r2, (x1, y1), (x2, y2), m, c = random.choice(_CHORDS)
    q = rf'Solve the simultaneous equations.<br>\( x^2 + y^2 = {r2} \)<br>\( y = {_lin(m, c)} \)'
    quad = sp.expand(sp.Symbol('x') ** 2 + (m * sp.Symbol('x') + c) ** 2 - r2)
    a2, a1, a0 = (int(v) for v in sp.Poly(quad, sp.Symbol('x')).all_coeffs())
    g = math.gcd(math.gcd(abs(a2), abs(a1)), abs(a0))
    s = (rf'Put \( y = {_lin(m, c)} \) into the circle: \( x^2 + ({_lin(m, c)})^2 = {r2} \).<br>'
         rf'Expand and collect: \( {_quad(a2, a1, a0)} = 0 \), which simplifies to \( {_quad(a2 // g, a1 // g, a0 // g)} = 0 \).<br>'
         rf'\( {_factors(x1, x2)} = 0 \) gives \( x = {x1} \) or \( x = {x2} \).<br>'
         rf'Then \( y = {y1} \) and \( y = {y2} \). Solutions: <strong>({x1}, {y1})</strong> and <strong>({x2}, {y2})</strong>.')
    hint = 'Replace y in the circle equation by the line, expand the bracket carefully, then solve the quadratic in x.'
    record('qsim_circle_line_points', r2=r2, m=m, c=c)
    return q, s, hint, 5, _fields4(x1, y1, x2, y2)


def gcse_qsim_i_sum_and_product():
    """Intermediate: two numbers with a given sum and product (x + y = s, xy = p)."""
    r1, r2 = sorted(random.sample(range(1, 13), 2))
    tot, prod = r1 + r2, r1 * r2
    q = (rf'Two numbers \( x \) and \( y \) satisfy \( x + y = {tot} \) and \( xy = {prod} \).<br>'
         rf'Find the two possible values of \( x \).')
    s = (rf'From the first equation \( y = {tot} - x \). Put this into the second: \( x({tot} - x) = {prod} \).<br>'
         rf'\( {tot}x - x^2 = {prod} \), so \( x^2 - {tot}x + {prod} = 0 \).<br>'
         rf'\( {_factor_text(r1)}{_factor_text(r2)} = 0 \), so <strong>x = {r1}</strong> or <strong>x = {r2}</strong> '
         rf'(then \( y = {r2} \) or \( y = {r1} \)).')
    hint = 'Write y in terms of x from the sum, then put it into the product. You get a quadratic in x.'
    record('qsim_sum_product', total=tot, product=prod)
    return q, s, hint, 4, _roots(r1, r2)


def gcse_qsim_i_hyperbola_line():
    """Intermediate: xy = k with a line; one positive and one negative solution."""
    while True:
        r1 = random.randint(-8, -1)
        r2 = random.randint(1, 8)
        m = r1 + r2                         # y = x + d, so x(x + d) = k
        if m != 0 and r1 != -r2:
            break
    d = -(r1 + r2)
    k = r1 * (r1 + d)
    if k <= 0 or d == 0:
        return gcse_qsim_i_hyperbola_line()
    y1, y2 = r1 + d, r2 + d
    q = rf'Solve the simultaneous equations.<br>\( xy = {k} \)<br>\( y = {_lin(1, d)} \)'
    s = (rf'Put \( y = {_lin(1, d)} \) into \( xy = {k} \): \( x({_lin(1, d)}) = {k} \), so \( {_quad(1, d, -k)} = 0 \).<br>'
         rf'\( {_factor_text(r1)}{_factor_text(r2)} = 0 \), so \( x = {r1} \) or \( x = {r2} \).<br>'
         rf'Then \( y = {y1} \) and \( y = {y2} \). Solutions: <strong>({r1}, {y1})</strong> and <strong>({r2}, {y2})</strong>.')
    hint = 'Replace y in xy = k by the line. Expand the bracket and move every term to one side before factorising.'
    record('qsim_hyperbola_line_points', k=k, d=d)
    return q, s, hint, 5, _fields4(r1, y1, r2, y2)


def gcse_qsim_d_tangent_k():
    """Difficult: the value of k that makes the line a tangent to the parabola (a repeated root)."""
    m = random.choice([-8, -6, -4, -2, 2, 4, 6, 8])
    while True:
        c0 = random.choice([-3, -2, -1, 0, 1, 2, 4])
        kk = c0 - m * m // 4
        if kk != 0:
            break
    curve = f'y = {_quad(1, 0, c0)}' if c0 else 'y = x^2'
    q = (rf'The line \( y = {m}x + k \) is a tangent to the curve \( {curve} \). Find the value of \( k \).')
    s = (rf'Equate: \( {_quad(1, 0, c0) if c0 else "x^2"} = {m}x + k \), so \( {_quad(1, -m, c0 - 0)} - k = 0 \).<br>'
         rf'A tangent touches once, so the discriminant is zero: \( {f"({-m})" if -m < 0 else -m}^2 - 4 \times ({c0} - k) = 0 \).<br>'
         rf'\( {m * m}{_shift(-4 * c0)} + 4k = 0 \), so \( 4k = {4 * kk} \) and <strong>k = {kk}</strong>.')
    hint = 'Make the two expressions equal and rearrange to zero. A tangent means exactly one solution, so b^2 - 4ac = 0.'
    record('qsim_tangent_k', m=m, c0=c0)
    return q, s, hint, 4, _lin_ans(kk, 'k')


def gcse_qsim_d_largest_k_miss():
    """Difficult: the greatest whole number k for which a line misses the parabola."""
    # review 2026-10-28: m alone gave 6 different questions; the curve's constant and the sign of m now vary too
    m = random.choice([-8, -7, -6, -5, -4, -3, 3, 4, 5, 6, 7, 8])
    c0 = random.choice([-3, -2, -1, 0, 0, 1, 2, 4])
    bound = c0 - Fraction(m * m, 4)
    kk = math.ceil(bound) - 1
    curve = f'y = {_quad(1, 0, c0)}' if c0 else 'y = x^2'
    q = (rf'The line \( y = {m}x + k \) does not meet the curve \( {curve} \). '
         rf'Find the greatest whole number value of \( k \).')
    s = (rf'Equate: \( {_quad(1, 0, c0) if c0 else "x^2"} = {m}x + k \), so \( {_quad(1, -m, c0)} - k = 0 \).<br>'
         rf'No real solutions needs \( b^2 - 4ac < 0 \): \( {m * m}{_shift(-4 * c0)} + 4k < 0 \), '
         rf'so \( k < {_num_text(bound)} \).<br>'
         rf'The greatest whole number below {_num_text(bound)} is <strong>{kk}</strong>.')
    hint = 'No intersection means the quadratic has no real roots, so its discriminant is negative. Solve the inequality for k.'
    record('qsim_largest_k_miss', m=m, c0=c0)
    return q, s, hint, 4, kk


def gcse_qsim_d_midpoint_of_chord():
    """Difficult: find the midpoint of the chord joining the two intersection points."""
    r1, r2 = _distinct_roots(-6, 6)
    m, c = r1 + r2, -r1 * r2
    y1, y2 = r1 * r1, r2 * r2
    mx, my = Fraction(r1 + r2, 2), Fraction(y1 + y2, 2)
    q = (rf'The curve \( y = x^2 \) and the line \( y = {_lin(m, c)} \) meet at the points \( A \) and \( B \).<br>'
         rf'Find the coordinates of the midpoint of \( AB \).')
    s = (rf'\( x^2 = {_lin(m, c)} \) gives \( {_quad(1, -m, -c)} = 0 \), so \( {_factor_text(r1)}{_factor_text(r2)} = 0 \).<br>'
         rf'\( A = ({r1}, {y1}) \) and \( B = ({r2}, {y2}) \).<br>'
         rf'Midpoint: \( \left(\frac{{{r1} + {r2 if r2 >= 0 else f"({r2})"}}}{{2}}, \frac{{{y1} + {y2}}}{{2}}\right) \) = '
         rf'<strong>({_num_text(mx)}, {_num_text(my)})</strong>.')
    hint = 'Find both intersection points first. The midpoint has the mean of the two x-values and the mean of the two y-values.'
    record('qsim_midpoint', m=m, c=c)
    payload = _pair(0, 0, 'x', 'y')
    payload['values'] = (_num_text(mx), _num_text(my))          # decimals: the pair checker does not read 1/2
    return q, s, hint, 5, payload


def gcse_qsim_d_circle_show_that():
    """Difficult: show-that quadratic from a circle and a line, then solve; the pupil's answer is the solution."""
    r2, (x1, y1), (x2, y2), m, c = random.choice(_CHORDS)
    quad = sp.expand(sp.Symbol('x') ** 2 + (m * sp.Symbol('x') + c) ** 2 - r2)
    a2, a1, a0 = (int(v) for v in sp.Poly(quad, sp.Symbol('x')).all_coeffs())
    g = math.gcd(math.gcd(abs(a2), abs(a1)), abs(a0))
    target = _quad(a2 // g, a1 // g, a0 // g)
    q = (rf'The circle \( x^2 + y^2 = {r2} \) and the line \( y = {_lin(m, c)} \) intersect at two points.<br>'
         rf'(a) Show that the \( x \)-coordinates of the points satisfy \( {target} = 0 \).<br>'
         rf'(b) Hence find the coordinates of the two points.')
    s = (rf'(a) \( x^2 + ({_lin(m, c)})^2 = {r2} \) expands to \( {_quad(a2, a1, a0)} = 0 \)'
         + (rf', and dividing by {g} gives \( {target} = 0 \).' if g > 1 else '.') +
         rf'<br>(b) \( {_factors(x1, x2)} = 0 \), so \( x = {x1} \) or \( x = {x2} \). '
         rf'Using the line, \( y = {y1} \) and \( y = {y2} \).<br>'
         rf'Points: <strong>({x1}, {y1})</strong> and <strong>({x2}, {y2})</strong>.')
    hint = 'For part (a), replace y by the line and expand the squared bracket. Part (b): solve the quadratic, then use the line for y.'
    record('qsim_circle_line_points', r2=r2, m=m, c=c)
    return q, s, hint, 6, _fields4(x1, y1, x2, y2)


# ─────────────────────────────────────────────────────────────────────────────
# Algebraic fractions
# ─────────────────────────────────────────────────────────────────────────────

_X = sp.Symbol('x')


def _pt(e):
    """Plain text of a sympy expression as a pupil writes it: 'x^2 - 3x - 4', 'x(x + 2)'."""
    t = sp.sstr(e).replace('**', '^')
    t = re.sub(r'(\d)\*([a-z(])', r'\1\2', t)
    t = re.sub(r'([a-z)])\*([a-z(])', r'\1\2', t)
    return t.replace('*', '')


def _df(num, den):
    return rf'\dfrac{{{num}}}{{{den}}}'


def _lin_p(a, b):
    """'x + 3', '2x - 5', '-x + 4' as text."""
    return _lin(a, b)


def _fraction_key(num, den, hint=None):
    payload = {'type': 'algebraic_fraction', 'numerator': _pt(num), 'denominator': _pt(den), 'form': FORM_SIMPLIFIED}
    payload['format_hint'] = hint or 'Enter the numerator and the denominator, fully simplified'
    return payload


def _lowest(e):
    """(numerator, denominator) of a rational expression in lowest terms, as sympy expressions."""
    n, d = sp.fraction(sp.cancel(sp.together(e)))
    if sp.Poly(d, _X).LC() < 0:
        n, d = -n, -d
    return sp.expand(n), d


@verifies('alg', task='simplify', form=None)
def gcse_af_f_numeric_common_factor():
    """Foundational: cancel a numerical common factor from a fraction with an x term."""
    g = random.choice([2, 3, 4, 5, 6])
    a, b = random.choice([(2, 3), (3, 4), (5, 2), (4, 5), (3, 5), (7, 2), (2, 5)])
    num, den = g * a, g * b
    q = rf'Simplify <strong>\({_df(f"{num}x", str(den))}\)</strong>.'
    s = rf'The numbers {num} and {den} share the factor {g}. Divide top and bottom by {g}: <strong>\({_df(f"{a}x", str(b))}\)</strong>.'
    hint = f'Find the biggest number that divides into both {num} and {den}.'
    return q, s, hint, 2, _fraction_key(a * _X, b)



@verifies('alg', task='simplify', form=None)
def gcse_af_f_add_expression_numerators():
    """Foundational: add two fractions with the same numerical denominator, each numerator a linear expression."""
    d = random.choice([3, 4, 5, 6, 7])
    a1, b1 = random.randint(1, 4), random.randint(-4, 5)
    a2, b2 = random.randint(1, 4), random.randint(-4, 5)
    n = sp.expand((a1 + a2) * _X + b1 + b2)
    if sp.gcd(sp.Poly(n, _X).all_coeffs()[0], sp.gcd(sp.Poly(n, _X).all_coeffs()[1], d)) != 1 or b1 + b2 == 0 \
            or any(bi == 0 and math.gcd(ai, d) > 1 for ai, bi in ((a1, b1), (a2, b2))):
        # review: no fraction in the question that cancels on its own (3x/3, 2x/4)
        return gcse_af_f_add_expression_numerators()
    q = (rf'Write as a single fraction, fully simplified: <strong>\({_df(_lin(a1, b1), str(d))} + {_df(_lin(a2, b2), str(d))}\)</strong>.')
    s = (rf'The denominators are the same, so add the numerators: \( {_df(f"({_lin(a1, b1)}) + ({_lin(a2, b2)})", str(d))} \).<br>'
         rf'Collect like terms: <strong>\({_df(_pt(n), str(d))}\)</strong>.')
    hint = 'Keep the common denominator and add the two numerators. Collect the x terms and the numbers separately.'
    return q, s, hint, 3, _fraction_key(n, d)


@verifies('alg', task='substitute')
def gcse_af_f_evaluate_fraction():
    """Foundational: the value of an algebraic fraction at a given x, as a fraction."""
    while True:
        a, b = random.randint(2, 5), random.randint(1, 6)
        c, d = random.randint(1, 3), random.randint(-6, -1)
        x = random.randint(2, 8)
        den = c * x + d
        num = a * x + b
        if den > 1 and math.gcd(num, den) == 1 and den != num:
            break
    q = rf'Work out the value of <strong>\({_df(_lin(a, b), _lin(c, d))}\)</strong> when \( x = {x} \). Give your answer as a fraction, fully simplified.'
    s = (rf'Numerator: \( {a} \times {x} {"+" if b > 0 else "-"} {abs(b)} = {num} \).<br>'
         rf'Denominator: \( {c} \times {x} {"+" if d > 0 else "-"} {abs(d)} = {den} \).<br>'
         rf'The value is <strong>\({_df(str(num), str(den))}\)</strong>, which cannot be simplified.')
    hint = 'Work out the top and the bottom separately by putting in the value of x, then write one over the other.'
    return q, s, hint, 3, {'type': 'algebraic_fraction', 'numerator': str(num), 'denominator': str(den), 'form': FORM_SIMPLIFIED}


def gcse_af_f_undefined_value():
    """Foundational: the value of x for which a fraction is undefined."""
    a = random.choice([1, 1, 2, 3])
    r = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7])
    b = -a * r
    n = random.randint(2, 9)
    q = rf'For what value of \( x \) is the fraction <strong>\({_df(str(n), _lin(a, b))}\)</strong> not defined?'
    s = (rf'A fraction is not defined when its denominator is zero.<br>'
         + (rf'\( {_lin(a, b)} = 0 \) gives <strong>x = {r}</strong>.' if a == 1 else
            rf'\( {_lin(a, b)} = 0 \) gives \( {a}x = {-b} \), so <strong>x = {r}</strong>.'))
    hint = 'You cannot divide by zero. Find the value of x that makes the bottom of the fraction equal to 0.'
    record('af_undefined', a=a, b=b)
    return q, s, hint, 2, _lin_ans(r, 'x')


@verifies('alg', task='simplify', form=None)
def gcse_af_i_simplify_two_quadratics():
    """Intermediate: factorise the numerator and the denominator, cancel the common bracket."""
    while True:
        p, q1, r = (random.randint(-6, 6) for _ in range(3))
        if len({p, q1, r}) == 3 and 0 not in (p, q1, r):
            break
    common = _X + r
    n = sp.expand((_X + p) * common)
    d = sp.expand((_X + q1) * common)
    q = rf'Simplify <strong>\({_df(_pt(n), _pt(d))}\)</strong> fully.'
    s = (rf'Factorise both: top \( {_factor_text(-p)}{_factor_text(-r)} \), bottom \( {_factor_text(-q1)}{_factor_text(-r)} \).<br>'
         rf'Cancel the common bracket \( {_factor_text(-r)} \): <strong>\({_df(_pt(_X + p), _pt(_X + q1))}\)</strong>.')
    hint = 'Factorise the top and the bottom into brackets. Cancel any bracket that appears on both.'
    return q, s, hint, 4, _fraction_key(_X + p, _X + q1)



@verifies('alg', task='simplify', form=None)
def gcse_af_i_divide_fractions():
    """Intermediate: divide one algebraic fraction by another with a common bracket."""
    while True:
        a, b, c = (random.randint(-5, 6) for _ in range(3))
        if len({a, b, c}) == 3 and 0 not in (a, b, c):
            break
    top1, bot1 = _X + a, _X + b
    top2, bot2 = _X + a, _X + c
    q = (rf'Simplify <strong>\({_df(_pt(top1), _pt(bot1))} \div {_df(_pt(top2), _pt(bot2))}\)</strong>.')
    n, d = _lowest(top1 / bot1 * bot2 / top2)
    s = (rf'Turn the second fraction upside down and multiply: \( {_df(_pt(top1), _pt(bot1))} \times {_df(_pt(bot2), _pt(top2))} \).<br>'
         rf'Cancel \( {_pt(_X + a)} \) from the top and the bottom: <strong>\({_df(_pt(n), _pt(d))}\)</strong>.')
    hint = 'Dividing by a fraction means multiplying by its reciprocal. Then cancel any common bracket.'
    return q, s, hint, 3, _fraction_key(n, d)


@verifies('alg', task='simplify', form=None)
def gcse_af_i_add_numeric_denominators():
    """Intermediate: (x + a)/m + (x + b)/n with different numerical denominators."""
    while True:
        m, n2 = random.choice([(2, 3), (3, 4), (4, 5), (2, 5), (3, 5), (4, 3), (6, 4), (3, 2)])
        a, b = random.randint(-5, 6), random.randint(-5, 6)
        if m != n2 and a != b:
            break
    lcd = math.lcm(m, n2)
    k1, k2 = lcd // m, lcd // n2
    num = sp.expand(k1 * (_X + a) + k2 * (_X + b))
    co = sp.Poly(num, _X).all_coeffs()
    if math.gcd(math.gcd(abs(int(co[0])), abs(int(co[1]))), lcd) != 1 or int(co[1]) == 0:
        return gcse_af_i_add_numeric_denominators()
    q = rf'Write as a single fraction, fully simplified: <strong>\({_df(_lin(1, a), str(m))} + {_df(_lin(1, b), str(n2))}\)</strong>.'
    s = (rf'The lowest common denominator is {lcd}.<br>'
         rf'\( {_df(f"{k1}({_lin(1, a)})", str(lcd))} + {_df(f"{k2}({_lin(1, b)})", str(lcd))} = {_df(_pt(num), str(lcd))} \).<br>'
         rf'The top and bottom have no common factor, so the answer is <strong>\({_df(_pt(num), str(lcd))}\)</strong>.')
    hint = 'Change both fractions so they have the same denominator, the lowest common multiple of the two. Multiply each top by the same number.'
    return q, s, hint, 4, _fraction_key(num, lcd)


@verifies('alg', task='solve_linear')
def gcse_af_i_solve_cross_multiply():
    """Intermediate: an equation with a fraction on each side."""
    while True:
        m, n2 = random.choice([(2, 3), (3, 4), (4, 5), (2, 5), (3, 2), (5, 3), (4, 3)])
        a, b = random.randint(-6, 8), random.randint(-6, 8)
        # (x + a) / m = (x + b) / n  ->  n (x + a) = m (x + b)  ->  (n - m) x = m b - n a
        if m == n2:
            continue
        x_num = m * b - n2 * a
        x_den = n2 - m
        if x_num % x_den == 0 and a != b:
            x = x_num // x_den
            if x not in (0, a, b, m, n2):       # review: not (x - 1)/3 = x/4 with x = 4
                break
    q = rf'Solve <strong>\({_df(_lin(1, a), str(m))} = {_df(_lin(1, b), str(n2))}\)</strong>.'
    s = (rf'Multiply both sides by {m} and by {n2}: \( {n2}({_lin(1, a)}) = {m}({_lin(1, b)}) \).<br>'
         rf'Expand: \( {_lin(n2, n2 * a)} = {_lin(m, m * b)} \).<br>'
         + (rf'Collect: <strong>\(x = {x}\)</strong>.' if n2 - m == 1 else
            rf'Collect: \( {_lin(n2 - m, 0)} = {m * b - n2 * a} \), so <strong>x = {x}</strong>.'))
    hint = 'Multiply both sides by each denominator (cross-multiply) to remove the fractions, then expand the brackets and solve.'
    return q, s, hint, 4, _lin_ans(x, 'x')


@verifies('alg', task='simplify', form=None)
def gcse_af_d_subtract_linear_denominators():
    """Difficult: subtract two fractions with different linear denominators."""
    while True:
        a, b = random.sample([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5], 2)
        p, q1 = random.randint(1, 4), random.randint(1, 5)
        num = sp.expand(p * (_X + b) - q1 * (_X + a))
        n_, d_ = _lowest(p / (_X + a) - q1 / (_X + b))
        if sp.degree(n_, _X) >= 1 and sp.gcd(n_, d_) == 1 and not n_.is_number:
            break
    q = rf'Write as a single fraction, fully simplified: <strong>\({_df(str(p), _pt(_X + a))} - {_df(str(q1), _pt(_X + b))}\)</strong>.'
    s = (rf'The common denominator is \( ({_pt(_X + a)})({_pt(_X + b)}) \), with each bracket kept.<br>'
         rf'\( {_df(f"{p}({_pt(_X + b)}) - {q1}({_pt(_X + a)})", f"({_pt(_X + a)})({_pt(_X + b)})")} \) '
         rf'= \( {_df(_pt(num), f"({_pt(_X + a)})({_pt(_X + b)})")} \).<br>'
         rf'Nothing cancels, so the answer is <strong>\({_df(_pt(n_), _pt(d_))}\)</strong>.')
    hint = 'Use the product of the two denominators as the common denominator. Multiply each numerator by the other bracket and take care with the minus sign.'
    return q, s, hint, 5, _fraction_key(n_, d_)


def gcse_af_d_solve_reciprocal_quadratic():
    """Difficult: k / x = x + d leads to a quadratic with two integer solutions."""
    while True:
        r1, r2 = random.randint(-7, -1), random.randint(1, 7)
        d = -(r1 + r2)
        k = -r1 * r2
        if d != 0:
            break
    q = rf'Solve <strong>\({_df(str(k), "x")} = {_lin(1, d)}\)</strong>.'
    s = (rf'Multiply both sides by \( x \): \( {k} = x({_lin(1, d)}) \), so \( {k} = {_quad(1, d, 0)} \).<br>'
         rf'Rearrange: \( {_quad(1, d, -k)} = 0 \), so \( {_factor_text(r1)}{_factor_text(r2)} = 0 \).<br>'
         rf'<strong>x = {r1}</strong> or <strong>x = {r2}</strong> (neither makes the denominator zero).')
    hint = 'Multiply both sides by x to remove the fraction. You get a quadratic: rearrange it to equal zero and factorise.'
    record('af_solve_quad_recip', k=k, d=d)
    return q, s, hint, 5, _roots(r1, r2)


@verifies('alg', task='simplify', form=None)
def gcse_af_d_simplify_non_monic():
    """Difficult: cancel a bracket whose x term has a coefficient above 1."""
    while True:
        a = random.choice([2, 3])
        s1, s2 = random.randint(-4, 4), random.randint(-5, 5)
        t = random.randint(1, 4) * random.choice([-1, 1])
        # review: gcd(a, t) = 1, so the bracket that cancels is (2x + 3), never (2x - 2) = 2(x - 1), which a teacher
        # would factorise as 2(x - 1)(x - 3) and which is really a monic question with a 2 taken out
        if s1 != s2 and s1 != 0 and s2 != 0 and t not in (s1, s2) and a * s1 != -t and math.gcd(a, abs(t)) == 1:
            break
    common = a * _X + t
    n = sp.expand(common * (_X + s1))
    d = sp.expand(common * (_X + s2))
    n_, d_ = _lowest(n / d)
    q = rf'Simplify <strong>\({_df(_pt(n), _pt(d))}\)</strong> fully.'
    s = (rf'Factorise: top \( ({_pt(common)})({_pt(_X + s1)}) \), bottom \( ({_pt(common)})({_pt(_X + s2)}) \).<br>'
         rf'Cancel \( ({_pt(common)}) \): <strong>\({_df(_pt(n_), _pt(d_))}\)</strong>.')
    hint = 'Factorise the top and bottom, using the factor that has a number in front of x. Cancel the common bracket.'
    return q, s, hint, 5, _fraction_key(n_, d_)


def _two_fraction_cases():
    out = []
    for a in range(-9, 10):
        for b in range(-9, 10):
            if a == 0 or b == 0 or a == b or a == -b:
                continue
            # a(x - 1) + b(x + 1) = x^2 - 1  ->  x^2 - (a + b)x - (b - a) - 1 = 0
            disc = (a + b) ** 2 + 4 * (b - a + 1)
            r = math.isqrt(disc) if disc >= 0 else -1
            if r < 0 or r * r != disc or (a + b + r) % 2:
                continue
            r1, r2 = (a + b - r) // 2, (a + b + r) // 2
            # review: {r1, r2} == {a, b} (-3/(x + 1) + 2/(x - 1) = 1 has the roots -3 and 2) let the printed
            # numerators be typed as the answer; those two cases are left out
            if r1 != r2 and not {r1, r2} & {1, -1, 0} and {r1, r2} != {a, b}:
                out.append((a, b, r1, r2))
    return out


_TWO_FRACTION_CASES = _two_fraction_cases()


def gcse_af_d_solve_two_fractions():
    """Difficult: a/(x + 1) + b/(x - 1) = 1 style equations that become a quadratic."""
    a, b, r1, r2 = random.choice(_TWO_FRACTION_CASES)
    lhs = (rf'{_df(str(a), "x + 1")} {"+" if b > 0 else "-"} {_df(str(abs(b)), "x - 1")}')
    q = rf'Solve <strong>\({lhs} = 1\)</strong>.'
    s = (rf'Multiply every term by \( (x + 1)(x - 1) \): \( {a}(x - 1) {"+" if b > 0 else "-"} {abs(b)}(x + 1) = (x + 1)(x - 1) \).<br>'
         rf'Expand: \( {_lin(a + b, b - a)} = x^2 - 1 \), so \( {_quad(1, -(a + b), -(b - a) - 1)} = 0 \).<br>'
         rf'\( {_factor_text(r1)}{_factor_text(r2)} = 0 \), so <strong>x = {r1}</strong> or <strong>x = {r2}</strong>.')
    hint = 'Multiply every term by both denominators to clear the fractions. Expand, rearrange to equal zero and factorise.'
    record('af_solve_two_fractions', a=a, b=b)
    return q, s, hint, 6, _roots(r1, r2)


# ─────────────────────────────────────────────────────────────────────────────
# Algebraic proof
# ─────────────────────────────────────────────────────────────────────────────

def _pv():
    return random.choice(['n', 'm', 'k'])


def _proof_steps(steps, distractors, after=None):
    """Ordered proof_steps payload: the steps in order, mixed with distractors in a shuffled bank."""
    bank = [{'id': f's{i + 1}', 'text': text} for i, text in enumerate(steps)]
    bank += [{'id': f'd{j + 1}', 'text': text} for j, text in enumerate(distractors)]
    random.shuffle(bank)
    return proof_steps_answer(tuple(f's{i + 1}' for i in range(len(steps))), bank, order_matters=True,
                              format_hint='Put the proof steps in the correct order', after=after)


def gcse_ap_f_simplify_to_constant():
    """Foundational: simplify an expression whose x terms cancel, so its value does not depend on n."""
    v = _pv()
    a, b = random.randint(2, 6), random.randint(2, 9)
    q = (rf'Simplify <strong>\({a}({v} + {b}) - {a}{v}\)</strong>. '
         rf'Your answer is a number, so the expression has the same value for every integer \( {v} \). What is it?')
    s = rf'Expand the bracket: \( {a}{v} + {a * b} - {a}{v} \). The \( {v} \) terms cancel, leaving <strong>{a * b}</strong>.'
    hint = 'Multiply out the bracket, then collect like terms. What is left once the letters cancel?'
    record('ap_bracket_const', a=a, b=b)           # review: a record family (was @verifies simplify), for the hints
    return q, s, hint, 2, a * b


@verifies('alg', task='expand')
def gcse_ap_f_expand_even_product():
    """Foundational: the product of consecutive even numbers 2n and 2n + 2, expanded."""
    v = _pv()
    a, b = random.choice([(2, 2), (2, 4), (4, 2), (2, 6), (6, 2)])
    q = (rf'Expand and simplify <strong>\({a}{v}({a}{v} + {b})\)</strong>. '
         rf'It is the product of two even numbers, where \( {v} \) is an integer.')
    prod = sp.expand(a * sp.Symbol(v) * (a * sp.Symbol(v) + b))
    s = rf'Multiply each term in the bracket by \( {a}{v} \): <strong>\({_pt(prod)}\)</strong>.'
    hint = f'Multiply {a}{v} by each term inside the bracket, then write the answer with the highest power first.'
    return q, s, hint, 2, _alg_ans(prod, 'Enter the expanded expression, e.g. 3n^2 + 5n', FORM_EXPANDED)


def gcse_ap_f_common_factor_bracket():
    """Foundational: take out the common factor to finish a proof that a sum is a multiple of m."""
    m = random.choice([3, 4, 5, 6, 7, 8, 9])
    c1, c2 = random.sample(range(1, 6), 2)
    sign = random.choice([1, -1])
    p, q2 = m * c1, sign * m * c2
    a, b = sp.symbols('a b')
    body = _two_var(p, q2, 'a', 'b')
    inner = _two_var(c1, sign * c2, 'a', 'b')
    q = (rf'\( a \) and \( b \) are integers. Complete this proof that \( {body} \) is a multiple of {m}.<br>'
         rf'\( {body} = {m}( \ldots ) \)<br>Write the expression that goes in the bracket.')
    s = (rf'Both terms have a factor of {m}, so \( {body} = {m}({inner}) \).<br>'
         rf'Since \( {inner} \) is an integer, the expression is {m} times an integer, so it is a multiple of {m}. '
         rf'The bracket is <strong>{inner}</strong>.')
    hint = f'Take {m} out of both terms. What is left in each term?'
    record('ap_common_factor', m=m, p=p, q=q2)
    ans = c1 * a + sign * c2 * b
    # review: the fixed example "2a + 3b" was the answer when the bracket is 2a + 3b
    example = _example(ans, ('2a + 3b', 2 * a + 3 * b), ('3a - 2b', 3 * a - 2 * b))
    return q, s, hint, 2, _alg_ans(ans, f'Enter the expression, {example}')


@verifies('alg', task='ap_proof')
def gcse_ap_f_multiple_of_five_form():
    """Foundational: explain why 10k + 5 is a multiple of 5 (take out the factor, name the bracket)."""
    v = _pv()
    a = random.choice([2, 3, 4])
    expr_text = f'{5 * a}{v} + 5'
    q = (rf'Let <strong>\({v}\)</strong> be any integer. Explain why <strong>\({expr_text}\)</strong> is always a '
         rf'<strong>multiple of 5</strong>.')
    s = (rf'\( {expr_text} = 5({a}{v} + 1) \). The bracket \( {a}{v} + 1 \) is an integer, so the expression is 5 times an '
         rf'integer, which makes it a multiple of 5.')
    hint = 'Take 5 out of both terms. Then say why what is left in the bracket is a whole number.'
    return q, s, hint, 3, _proof_steps(
        (f'Write {expr_text} = 5({a}{v} + 1).',
         f'The bracket ({a}{v} + 1) is an integer for every integer {v}.',
         f'So {expr_text} is 5 times an integer, which means it is always a multiple of 5.'),
        (f'{expr_text} = 5({a}{v} + 5).',
         f'The bracket ({a}{v} + 1) is a fraction when {v} is odd.',
         f'{expr_text} ends in 5, so it is always odd.'))


@verifies('alg', task='ap_proof')
def gcse_ap_i_sum_consecutive_odds():
    """Intermediate: the sum of two consecutive odd numbers is a multiple of 4."""
    v = _pv()
    q = (rf'The sum of two consecutive odd numbers can be written <strong>\((2{v}+1) + (2{v}+3)\)</strong>, where '
         rf'\( {v} \) is an integer. Prove that this sum is always a <strong>multiple of 4</strong>.')
    s = (rf'\( (2{v} + 1) + (2{v} + 3) = 4{v} + 4 = 4({v} + 1) \). Since \( {v} + 1 \) is an integer, the sum is a multiple of 4.')
    hint = 'Add the two expressions and collect like terms, then take out the common factor of the result.'
    return q, s, hint, 4, _proof_steps(
        (f'Consecutive odd numbers are 2{v} + 1 and 2{v} + 3.',
         f'Their sum is (2{v} + 1) + (2{v} + 3) = 4{v} + 4.',
         f'Factorise: 4{v} + 4 = 4({v} + 1).',
         f'{v} + 1 is an integer, so the sum is 4 times an integer: it is a multiple of 4.'),
        (f'Their sum is (2{v} + 1) + (2{v} + 3) = 4{v} + 3.',
         f'Their sum is (2{v} + 1) + (2{v} + 3) = 2{v} + 4.',
         f'Odd numbers cannot add to a multiple of 4.'))


@verifies('alg', task='ap_proof')
def gcse_ap_i_consecutive_squares_difference_odd():
    """Intermediate: (n + 1)^2 - n^2 is always odd."""
    v = _pv()
    q = rf'Prove that <strong>\(({v} + 1)^2 - {v}^2\)</strong> is always <strong>odd</strong> for any integer \( {v} \).'
    s = (rf'\( ({v} + 1)^2 - {v}^2 = {v}^2 + 2{v} + 1 - {v}^2 = 2{v} + 1 \). \( 2{v} \) is even, so \( 2{v} + 1 \) is odd.')
    hint = 'Expand the bracket and subtract. Then say why the result is one more than an even number.'
    return q, s, hint, 4, _proof_steps(
        (f'Expand ({v} + 1)² = {v}² + 2{v} + 1.',
         f'Subtract {v}²: ({v} + 1)² − {v}² = 2{v} + 1.',
         f'2{v} is even for every integer {v}.',
         f'An even number plus 1 is odd, so 2{v} + 1 is always odd.'),
        (f'Expand ({v} + 1)² = {v}² + 1.',
         f'Subtract {v}²: ({v} + 1)² − {v}² = 2{v} − 1.',
         f'({v} + 1)² − {v}² is always even because it is a difference of two squares.'))


@verifies('alg', task='ap_proof')
def gcse_ap_i_difference_of_squares_identity():
    """Intermediate: prove the identity (n + 3)^2 - (n - 3)^2 = 12n with two independent expansions."""
    v = _pv()
    a = random.choice([2, 3, 4, 5])
    q = rf'Prove that <strong>\(({v} + {a})^2 - ({v} - {a})^2 = {4 * a}{v}\)</strong> for any integer \( {v} \).'
    s = (rf'\( ({v} + {a})^2 = {v}^2 + {2 * a}{v} + {a * a} \) and \( ({v} - {a})^2 = {v}^2 - {2 * a}{v} + {a * a} \).<br>'
         rf'Subtracting gives \( {4 * a}{v} \).')
    hint = 'Expand each bracket separately. When you subtract the second from the first, change all its signs.'
    return q, s, hint, 4, _proof_steps(
        (f'Expand ({v} + {a})² = {v}² + {2 * a}{v} + {a * a}.',
         f'Expand ({v} − {a})² = {v}² − {2 * a}{v} + {a * a}.',
         f'Subtract: ({v} + {a})² − ({v} − {a})² = {4 * a}{v}.'),
        (f'Expand ({v} + {a})² = {v}² + {a * a}.',
         f'Expand ({v} − {a})² = {v}² − {a}{v} + {a * a}.',
         f'Subtract: ({v} + {a})² − ({v} − {a})² = {2 * a}{v}.'),
        after={2: (), 3: (1, 2)})


@verifies('alg', task='factorise')
def gcse_ap_i_factorise_to_show_multiple():
    """Intermediate: factorise completely, the first step of showing an expression is a multiple."""
    v = _pv()
    a = random.choice([4, 6, 8, 9, 10, 12])
    c = random.choice([2, 3, 4, 5])
    q = (rf'Factorise completely <strong>\({a}{v}^2 + {a * c}{v}\)</strong>. '
         rf'Use your answer to explain why the expression is a multiple of {a} when \( {v} \) is an integer.')
    s = (rf'The common factor is {a}{v}: \( {a}{v}^2 + {a * c}{v} = {a}{v}({v} + {c}) \).<br>'
         rf'It is {a} times the integer \( {v}({v} + {c}) \), so it is a multiple of {a}.')
    hint = 'Find the biggest number and the highest power of the letter that divide into both terms, and take both outside the bracket.'
    return q, s, hint, 3, _alg_ans(a * sp.Symbol(v) * (sp.Symbol(v) + c), 'Enter the factorised expression', FORM_FACTORISED)


@verifies('alg', task='ap_proof')
def gcse_ap_d_sum_consecutive_squares_odd():
    """Difficult: the sum of the squares of two consecutive integers is odd."""
    v = _pv()
    q = (rf'Prove that the sum of the squares of two consecutive integers, <strong>\({v}^2 + ({v} + 1)^2\)</strong>, '
         rf'is always <strong>odd</strong>.')
    s = (rf'\( ({v} + 1)^2 = {v}^2 + 2{v} + 1 \), so the sum is \( 2{v}^2 + 2{v} + 1 = 2({v}^2 + {v}) + 1 \), '
         rf'which is an even number plus 1.')
    hint = 'Expand the second square and add. Show the first two terms of the result have a common factor of 2.'
    return q, s, hint, 5, _proof_steps(
        (f'Expand ({v} + 1)² = {v}² + 2{v} + 1.',
         f'So {v}² + ({v} + 1)² = 2{v}² + 2{v} + 1.',
         f'2{v}² + 2{v} = 2({v}² + {v}), which is even because it has a factor of 2.',
         f'An even number plus 1 is odd, so {v}² + ({v} + 1)² is always odd.'),
        (f'Expand ({v} + 1)² = {v}² + 1.',
         f'So {v}² + ({v} + 1)² = 2{v}² + 1.',
         f'One of {v} and {v} + 1 is odd, so the sum of their squares is always even.'))


@verifies('alg', task='ap_proof')
def gcse_ap_d_difference_squares_multiple_of_eight():
    """Difficult: (n + 2)^2 - (n - 2)^2 is a multiple of 8."""
    v = _pv()
    q = (rf'Prove that <strong>\(({v} + 2)^2 - ({v} - 2)^2\)</strong> is always a <strong>multiple of 8</strong> '
         rf'for any integer \( {v} \).')
    s = (rf'\( ({v} + 2)^2 = {v}^2 + 4{v} + 4 \) and \( ({v} - 2)^2 = {v}^2 - 4{v} + 4 \). '
         rf'The difference is \( 8{v} \), which is 8 times an integer.')
    hint = 'Expand both brackets, subtract carefully, and write the result as 8 times something.'
    return q, s, hint, 5, _proof_steps(
        (f'Expand ({v} + 2)² = {v}² + 4{v} + 4.',
         f'Expand ({v} − 2)² = {v}² − 4{v} + 4.',
         f'Subtract: ({v} + 2)² − ({v} − 2)² = 8{v}.',
         f'8{v} is 8 times an integer, so it is always a multiple of 8.'),
        (f'Expand ({v} + 2)² = {v}² + 4.',
         f'Subtract: ({v} + 2)² − ({v} − 2)² = 4{v}.',
         f'The difference of two squares is always even, so it is a multiple of 8.'),
        after={2: (), 3: (1, 2), 4: (3,)})


@verifies('alg', task='counterexample')
def gcse_ap_d_euler_prime_counterexample():
    """Difficult: a prime-generating expression that eventually fails; find the smallest n."""
    # review 2026-10-28: n^2 - n + 41 had the answer 41, the number printed in the question, and the 41 versions
    # needed 40 values up to 1,601 checked for primes to show the answer is the smallest. These five fail first at
    # n = 8 to 16 with every earlier value a prime below 260, and no answer is a number in the question.
    b, c = random.choice([(1, 11), (1, 17), (3, 13), (5, 17), (3, 19)])
    f = (lambda n: n * n + b * n + c)
    stmt = rf'n^2 + {"" if b == 1 else b}n + {c} \text{{ is prime}}'
    n_val = next(n for n in range(1, 100) if not _is_prime_num(f(n)))
    val = f(n_val)
    p_small = next(p for p in range(2, val + 1) if val % p == 0)
    earlier = ', '.join(str(f(n)) for n in range(1, n_val))
    q = (rf'The statement “<strong>\({stmt}\)</strong> for every positive integer <strong>\(n\)</strong>” is false. '
         rf'Give a <strong>counterexample</strong>: enter the <strong>smallest</strong> value of <strong>\(n\)</strong> '
         rf'that disproves it.')
    s = (rf'For \( n = 1 \) to \( {n_val - 1} \) the values are {earlier}, which are all prime.<br>'
         rf'At \( n = {n_val} \) it equals {val} = {p_small} × {val // p_small}, which is not prime. '
         rf'So <strong>n = {n_val}</strong>.')
    hint = 'Work through n = 1, 2, 3, ... until the value is a number with a factor other than 1 and itself.'
    return q, s, hint, 4, graded_answer_number(n_val)


def _is_prime_num(v):
    return v > 1 and all(v % p for p in range(2, int(v ** 0.5) + 1))


@verifies('alg', task='ap_proof')
def gcse_ap_d_odd_squares_difference_multiple_of_eight():
    """Difficult: the difference of the squares of two consecutive odd numbers is a multiple of 8."""
    v = _pv()
    q = (rf'The squares of two consecutive odd numbers are subtracted. Prove that '
         rf'<strong>\((2{v} + 3)^2 - (2{v} + 1)^2\)</strong> is always a <strong>multiple of 8</strong> for any integer \( {v} \).')
    s = (rf'\( (2{v} + 3)^2 = 4{v}^2 + 12{v} + 9 \) and \( (2{v} + 1)^2 = 4{v}^2 + 4{v} + 1 \). '
         rf'The difference is \( 8{v} + 8 = 8({v} + 1) \), 8 times an integer.')
    hint = 'Expand both squares first (do the middle term properly), subtract, then take out the common factor of 8.'
    return q, s, hint, 5, _proof_steps(
        (f'Expand (2{v} + 3)² = 4{v}² + 12{v} + 9 and (2{v} + 1)² = 4{v}² + 4{v} + 1.',
         f'Subtract: (2{v} + 3)² − (2{v} + 1)² = 8{v} + 8.',
         f'Factorise: 8{v} + 8 = 8({v} + 1).',
         f'{v} + 1 is an integer, so 8({v} + 1) is a multiple of 8.'),
        (f'Expand (2{v} + 3)² = 4{v}² + 9 and (2{v} + 1)² = 4{v}² + 1.',
         f'Subtract: (2{v} + 3)² − (2{v} + 1)² = 8.',
         f'Odd squares are odd, so their difference is even, and therefore a multiple of 8.'))


# ─────────────────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────────────────

def _signed_num(n):
    return f'({n})' if n < 0 else str(n)


def gcse_fn_f_negative_input():
    """Foundational: a rule written with the constant first, evaluated at a negative input."""
    c = random.randint(4, 15)
    m = random.randint(2, 6)
    x = random.randint(-5, -1)
    ans = c - m * x
    q = rf'The function \( f \) is given by <strong>\(f(x) = {c} - {m}x\)</strong>. Work out <strong>\(f({x})\)</strong>.'
    s = (rf'Replace \( x \) with \( {x} \): \( f({x}) = {c} - {m} \times ({x}) = {c} + {m * -x} = {ans} \).<br>'
         rf'A negative times a negative is positive, so <strong>f({x}) = {ans}</strong>.')
    hint = 'Put the number in brackets when you substitute. Subtracting a negative number adds.'
    record('fn_neg_input', c=c, m=m, x=x)           # review: a record family (was @verifies fn_eval), for the hints
    return q, s, hint, 2, ans


@verifies('alg', task='fn_eval')
def gcse_fn_f_three_values_quadratic():
    """Foundational: complete a small table of outputs for a quadratic rule."""
    b = random.choice([-4, -3, -2, 2, 3, 4])
    c = random.randint(-5, 6)
    xs = random.sample([-2, -1, 0, 1, 2, 3, 4], 3)
    xs.sort()
    vals = [x * x + b * x + c for x in xs]
    q = (rf'The function \( f \) is given by <strong>\(f(x) = {_quad(1, b, c)}\)</strong>. Work out '
         rf'<strong>\(f({xs[0]})\)</strong>, <strong>\(f({xs[1]})\)</strong> and <strong>\(f({xs[2]})\)</strong>.')
    # review: not "((-2))^2" or "+ 0"
    lines = '<br>'.join(rf'\( f({x}) = {_sq_num(x)} {"+" if b > 0 else "-"} {abs(b)} \times {_signed_num(x)}{_shift(c)} = {v} \)'
                        for x, v in zip(xs, vals))
    s = lines + '<br>Answers: ' + ', '.join(f'<strong>{v}</strong>' for v in vals) + '.'
    hint = 'Work out each value on its own. Square the input first, then multiply, then add the constant.'
    return q, s, hint, 3, _fields([str(v) for v in vals], [f'f({x})' for x in xs])


@verifies('alg', task='fn_eval')
def gcse_fn_i_composite_both_orders():
    """Intermediate: f(g(a)) and g(f(a)) are different."""
    while True:
        a, b = random.randint(2, 5), random.randint(-4, 6)
        c, d = random.randint(2, 4), random.randint(-5, 5)
        x = random.randint(1, 5)
        fg = a * (c * x + d) + b
        gf = c * (a * x + b) + d
        if fg != gf and b != 0 and d != 0:
            break
    q = (rf'\( f(x) = {_lin(a, b)} \) and \( g(x) = {_lin(c, d)} \). Work out <strong>\(f(g({x}))\)</strong> and '
         rf'<strong>\(g(f({x}))\)</strong>.')
    s = (rf'\( g({x}) = {c} \times {x} {"+" if d > 0 else "-"} {abs(d)} = {c * x + d} \), so \( f(g({x})) = {a} \times {_signed_num(c * x + d)} '
         rf'{"+" if b > 0 else "-"} {abs(b)} = {fg} \).<br>'
         rf'\( f({x}) = {a} \times {x} {"+" if b > 0 else "-"} {abs(b)} = {a * x + b} \), so \( g(f({x})) = {c} \times {_signed_num(a * x + b)} '
         rf'{"+" if d > 0 else "-"} {abs(d)} = {gf} \).<br>The answers are <strong>{fg}</strong> and <strong>{gf}</strong>, which differ.')
    hint = 'Work from the inside out. In f(g(x)) do g first; in g(f(x)) do f first.'
    return q, s, hint, 4, _fields([str(fg), str(gf)], [f'f(g({x}))', f'g(f({x}))'])


@verifies('alg', task='fn_solve', many=True)
def gcse_fn_i_solve_square_equals():
    """Intermediate: f(x) = k for a quadratic with no x term, so there are two solutions."""
    r = random.randint(2, 9)
    c = random.randint(-8, 8)
    k = r * r + c
    q = (rf'The function \( f \) is given by <strong>\(f(x) = {_quad(1, 0, c)}\)</strong>. '
         rf'Find the two values of \( x \) for which <strong>\(f(x) = {k}\)</strong>.')
    s = (rf'Set \( {_quad(1, 0, c)} = {k} \) and rearrange to leave \( x^2 \) on its own.<br>'
         rf'Square root both sides, remembering both signs: <strong>x = {r}</strong> or <strong>x = {-r}</strong>.')
    hint = 'Rearrange to x^2 = a number. Remember that a square root has a positive and a negative value.'
    return q, s, hint, 3, _roots(-r, r)


def gcse_fn_i_inverse_value():
    """Intermediate: the value of an inverse function at a number."""
    while True:
        m = random.randint(2, 6)
        c = random.randint(-9, 9)
        x = random.randint(1, 8)
        y = m * x + c
        if c != 0 and y != x and x not in (m, abs(c)):     # review: not f(x) = 4x + 5, f^-1(25) = 5
            break
    q = (rf'\( f(x) = {_lin(m, c)} \). Work out <strong>\(f^{{-1}}({y})\)</strong>.')
    s = (rf'\( f^{{-1}}({y}) \) is the input that gives the output {y}. Solve \( {_lin(m, c)} = {y} \): '
         rf'\( {m}x = {y - c} \), so <strong>x = {x}</strong>.<br>Check: \( f({x}) = {m} \times {x} {"+" if c > 0 else "-"} {abs(c)} = {y} \).')
    hint = 'The inverse undoes the function. Find the input x that makes f(x) equal to the number in the bracket.'
    record('fn_inverse_value', m=m, c=c, y=y)
    return q, s, hint, 3, x


@verifies('alg', task='fn_inverse')
def gcse_fn_i_inverse_divide():
    """Intermediate: the inverse of f(x) = x / m + c."""
    m = random.randint(2, 5)
    c = random.randint(-6, 8)
    if c == 0:
        c = 3
    q = rf'The function \( f \) is given by <strong>\(f(x) = \dfrac{{x}}{{{m}}} {"+" if c > 0 else "-"} {abs(c)}\)</strong>. Find <strong>\(f^{{-1}}(x)\)</strong>.'
    ans = sp.expand(m * (_X - c))
    s = (rf'Let \( y = \dfrac{{x}}{{{m}}} {"+" if c > 0 else "-"} {abs(c)} \). Make \( x \) the subject: \( y {"-" if c > 0 else "+"} {abs(c)} = \dfrac{{x}}{{{m}}} \), '
         rf'so \( x = {m}(y {"-" if c > 0 else "+"} {abs(c)}) \).<br>Swap the letters: <strong>\(f^{{-1}}(x) = {m}(x {"-" if c > 0 else "+"} {abs(c)}) = {_pt(ans)}\)</strong>.')
    hint = 'Write y = f(x), then rearrange to make x the subject. Undo the addition first, then the division.'
    # review: the fixed example "4x - 8" was the answer for f(x) = x/4 + 2
    example = _example(ans, ('4x - 8', 4 * _X - 8), ('5x + 10', 5 * _X + 10))
    return q, s, hint, 4, {'type': 'algebraic', 'value': _pt(ans), 'format_hint': f'Enter the inverse, {example}',
                           'subject': 'f⁻¹(x)'}


@verifies('alg', task='fn_eval')
def gcse_fn_d_composite_square_expression():
    """Difficult: f(g(x)) where f squares, so the bracket must be expanded."""
    a = random.randint(2, 4)
    b = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    q = (rf'\( f(x) = x^2 \) and \( g(x) = {_lin(a, b)} \). Write <strong>\(f(g(x))\)</strong> as an expression in \( x \), '
         rf'expanded and simplified.')
    ans = sp.expand((a * _X + b) ** 2)
    s = (rf'\( f(g(x)) = ({_lin(a, b)})^2 = ({_lin(a, b)})({_lin(a, b)}) \).<br>'
         rf'Expand: \( {a * a}x^2 {"+" if a * b > 0 else "-"} {abs(2 * a * b)}x + {b * b} \).<br>'
         rf'<strong>\(f(g(x)) = {_pt(ans)}\)</strong>.')
    hint = 'Replace x in f with the whole of g(x), keeping it in brackets. Then multiply the bracket by itself, taking care with the middle term.'
    # review: the fixed example was the answer for g(x) = 2x + 3 (and the functions wrapper dropped the form)
    example = _example(ans, ('4x^2 + 12x + 9', 4 * _X ** 2 + 12 * _X + 9), ('9x^2 - 12x + 4', 9 * _X ** 2 - 12 * _X + 4))
    return q, s, hint, 4, {'type': 'algebraic', 'value': _pt(ans), 'format_hint': f'Enter the expanded expression, {example}',
                           'form': FORM_EXPANDED}


# ─────────────────────────────────────────────────────────────────────────────
# Equations and inequalities: iteration and the change of sign (section 4, P2 gap rows)
# ─────────────────────────────────────────────────────────────────────────────

def gcse_eq_i_iteration_linear():
    """Intermediate: two steps of x(n+1) = a x(n) + b from a given starting value."""
    while True:
        a = random.randint(2, 4)
        b = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 6])
        x0 = random.randint(1, 5)
        if a * x0 + b != x0:        # review: x(n+1) = 2x(n) - 5 from 5 stays at 5 (5 in 100 draws)
            break
    x1 = a * x0 + b
    x2 = a * x1 + b
    q = (rf'A sequence is generated by the iteration formula \( x_{{n+1}} = {_lin(a, b, "x_n")} \) with \( x_0 = {x0} \).<br>'
         rf'Work out \( x_1 \) and \( x_2 \).')
    s = (rf'\( x_1 = {a} \times {x0} {"+" if b > 0 else "-"} {abs(b)} = {x1} \).<br>'
         rf'\( x_2 = {a} \times {_signed_num(x1)} {"+" if b > 0 else "-"} {abs(b)} = {x2} \).<br>'
         rf'So <strong>x₁ = {x1}</strong> and <strong>x₂ = {x2}</strong>.')
    hint = 'Use the answer to each step as the next input. x_1 comes from x_0, then x_2 comes from x_1.'
    record('eq_iterate_linear', a=a, b=b, x0=x0)
    return q, s, hint, 3, _fields([str(x1), str(x2)], ['x₁', 'x₂'])


def gcse_eq_d_iteration_reciprocal():
    """Difficult: x(n+1) = a + b / x(n); the second term is a terminating decimal."""
    while True:
        a = random.randint(1, 5)
        b = random.choice([6, 8, 10, 12, 15, 20])
        divs = [d for d in (1, 2, 3, 4, 5, 6) if b % d == 0]
        x0 = random.choice(divs)
        x1 = Fraction(a) + Fraction(b, x0)
        x2 = a + Fraction(b) / x1
        d = x2.denominator
        for p in (2, 5):
            while d % p == 0:
                d //= p
        if d == 1 and x1 != x0 and x2.denominator != 1:
            break
    q = (rf'An iteration formula is \( x_{{n+1}} = {a} + \dfrac{{{b}}}{{x_n}} \) with \( x_0 = {x0} \).<br>'
         rf'Work out \( x_1 \) and \( x_2 \). Give \( x_2 \) as a decimal.')
    s = (rf'\( x_1 = {a} + \dfrac{{{b}}}{{{x0}}} = {_num_text(x1)} \).<br>'
         rf'\( x_2 = {a} + \dfrac{{{b}}}{{{_num_text(x1)}}} = {a} + {_num_text(Fraction(b) / x1)} = {_num_text(x2)} \).<br>'
         rf'So <strong>x₁ = {_num_text(x1)}</strong> and <strong>x₂ = {_num_text(x2)}</strong>.')
    hint = 'Put x_0 into the formula to get x_1. Then put your value of x_1 into the formula to get x_2. A calculator is not needed.'
    record('eq_iterate_recip', a=a, b=b, x0=x0)
    return q, s, hint, 4, _fields([_num_text(x1), _num_text(x2)], ['x₁', 'x₂'])


def gcse_eq_d_change_of_sign():
    """Difficult: tabulate f(1), f(2), f(3) and say between which whole numbers the root lies."""
    while True:
        p = random.randint(1, 4)
        k = random.randint(2, 40)
        f = [x ** 3 + p * x - k for x in (1, 2, 3)]
        if f[0] < 0 < f[2] and f[1] != 0 and len({abs(v) for v in f}) == 3 and k > 4:
            break
    n = 1 if f[1] > 0 else 2
    q = (rf'\( f(x) = {_cubic_text(p, k)} \) has a root between two consecutive whole numbers.<br>'
         rf'Work out \( f(1) \), \( f(2) \) and \( f(3) \). Then write down the whole number \( n \) so that the root lies between '
         rf'\( x = n \) and \( x = n + 1 \).')
    s = (rf'\( f(1) = 1 + {p} - {k} = {f[0]} \), \( f(2) = 8 + {2 * p} - {k} = {f[1]} \), \( f(3) = 27 + {3 * p} - {k} = {f[2]} \).<br>'
         rf'The sign changes from negative to positive between \( x = {n} \) and \( x = {n + 1} \), '
         rf'so there is a root in that interval and <strong>n = {n}</strong>.')
    hint = 'Substitute each value into f(x). A root lies where the answer changes from negative to positive (or the reverse).'
    record('eq_sign_change', p=p, k=k)
    return q, s, hint, 4, _fields([str(v) for v in f] + [str(n)], ['f(1)', 'f(2)', 'f(3)', 'n'])


def _cubic_text(p, k):
    return f'x^3 + {p}x - {k}' if p != 1 else f'x^3 + x - {k}'
