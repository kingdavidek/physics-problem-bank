"""
GCSE Maths – Simultaneous Equations
5 foundational · 5 intermediate · 5 difficult · 6 MCQ
Graded practice variants return (question, solution, hint, marks, raw)
or an MCQ 6-tuple (question, solution, hint, marks, options, correct_letter).
"""
import random
from generators.shared.utils import make_problem
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    run_mcq_variant,
    pick_named_variant,
)


def _fmt_linear(coeff_x, coeff_y, const):
    """Format ax + by = c with clean signs."""
    parts = []
    if coeff_x != 0:
        if coeff_x == 1:
            parts.append("x")
        elif coeff_x == -1:
            parts.append("-x")
        else:
            parts.append(f"{coeff_x}x")
    if coeff_y != 0:
        if coeff_y == 1:
            parts.append("+ y" if parts else "y")
        elif coeff_y == -1:
            parts.append("- y" if parts else "-y")
        elif coeff_y > 0:
            parts.append(f"+ {coeff_y}y")
        else:
            parts.append(f"- {abs(coeff_y)}y")
    if not parts:
        parts.append("0")
    lhs = parts[0]
    for p in parts[1:]:
        if p.startswith("+"):
            lhs += f" {p}"
        else:
            lhs += f" {p}"
    return rf"\({lhs} = {const}\)"


def _sim_step(content):
    """Spaced block for one line of working in the answer panel."""
    return f'<div style="margin:0 0 14px 0;line-height:1.75;">{content}</div>'


def _sim_answer(x_ans, y_ans):
    return _sim_step(rf"<strong>Answer:</strong> \(x = {x_ans},\; y = {y_ans}\)")


def _sim_raw(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:g}"
    return str(value)


def _sim_pair_answer(val_a, val_b, label_a='x', label_b='y', sep=','):
    return {
        'type': 'number_pair',
        'values': (_sim_raw(val_a), _sim_raw(val_b)),
        'label_a': label_a,
        'label_b': label_b,
        'sep': sep,
    }


def _sim_linear_answer(value, var='y'):
    return {'type': 'linear', 'value': _sim_raw(value), 'var': str(var).strip().lower()}


def _sim_linear_raw(raw):
    var = raw.get('var') or 'x'
    val = raw.get('value')
    if var == 'x':
        return str(val)
    return f'{var}={val}'


def _sim_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 6 and isinstance(out[4], (list, tuple)):
        extra = {
            'options': list(out[4]),
            'correct_answer': out[5],
        }
    elif len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'number_pair':
                val_a, val_b = raw['values']
                extra = {
                    'correct_answer_raw': f'{val_a}|{val_b}',
                    'answer_type': 'number_pair',
                    'answer_labels': [raw['label_a'], raw['label_b']],
                    'answer_pair_sep': raw.get('sep', 'and'),
                }
            elif raw_type == 'linear':
                extra = {
                    'correct_answer_raw': _sim_linear_raw(raw),
                    'answer_type': 'linear',
                    'answer_format_hint': 'Enter the value (e.g. y = 3 or just 3)',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _sim_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
        elif isinstance(raw, str):
            extra = {
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks,
        'gcse', 'maths', 'simultaneous_equations', **extra
    )


def _build_pair(x_ans, y_ans, a1, b1, a2, b2):
    """Return (eq1_str, eq2_str) for integer solution."""
    c1 = a1 * x_ans + b1 * y_ans
    c2 = a2 * x_ans + b2 * y_ans
    return _fmt_linear(a1, b1, c1), _fmt_linear(a2, b2, c2)


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

def _sim_f_add_to_eliminate():
    """x + y and x - y style — add equations."""
    x_ans = random.randint(3, 8)
    y_ans = random.randint(1, 6)
    s = x_ans + y_ans
    d = x_ans - y_ans
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\(x + y = {s}\) &nbsp;&nbsp;(1)<br>"
        rf"\(x - y = {d}\) &nbsp;&nbsp;(2)"
    )
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — add equations (1) and (2) to eliminate \(y\):"
            rf'<div style="margin:8px 0 0 16px;">\(x + y = {s}\)<br>\(x - y = {d}\)<br>'
            rf"\(2x = {s + d}\) → <strong>\(x = {x_ans}\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — substitute \(x = {x_ans}\) into equation (1):"
            rf'<div style="margin:8px 0 0 16px;">\(y = {s} - {x_ans} = {y_ans}\)</div>'
        )
        + _sim_answer(x_ans, y_ans)
    )
    hint = (
        r"When one equation has \(+y\) and the other has \(-y\), adding the equations "
        r"cancels \(y\) straight away. Then substitute back to find the other unknown."
    )
    return q, sol, hint, 2, _sim_pair_answer(x_ans, y_ans)


def _sim_f_elim_same_coefficient():
    """Subtract when one variable has the same coefficient."""
    x_ans = random.randint(2, 6)
    y_ans = random.randint(2, 6)
    a1, b = random.randint(2, 4), random.randint(2, 4)
    a2 = a1 + random.randint(1, 3)
    c1 = a1 * x_ans + b * y_ans
    c2 = a2 * x_ans + b * y_ans
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\({a1}x + {b}y = {c1}\) &nbsp;&nbsp;(1)<br>"
        rf"\({a2}x + {b}y = {c2}\) &nbsp;&nbsp;(2)"
    )
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — both equations have \({b}y\), so subtract (1) from (2):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({a2}x + {b}y = {c2}\)<br>\({a1}x + {b}y = {c1}\)<br>"
            rf"\({a2 - a1}x = {c2 - c1}\) → <strong>\(x = {x_ans}\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — substitute \(x = {x_ans}\) into equation (1):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({a1}({x_ans}) + {b}y = {c1}\) → \({a1 * x_ans} + {b}y = {c1}\) "
            rf"→ <strong>\(y = {y_ans}\)</strong></div>"
        )
        + _sim_answer(x_ans, y_ans)
    )
    hint = (
        "When the same variable has the same coefficient in both equations, subtract one "
        "equation from the other to eliminate that variable, then substitute back."
    )
    return q, sol, hint, 3, _sim_pair_answer(x_ans, y_ans)


def _sim_f_substitution_y_equals():
    """y = ax + b substituted into second equation."""
    x_ans = random.randint(1, 5)
    y_ans = random.randint(1, 5)
    a1 = random.randint(1, 3)
    b1 = y_ans - a1 * x_ans
    c2, d2 = random.randint(2, 4), random.randint(1, 3)
    e2 = c2 * x_ans + d2 * y_ans
    b1_str = f"+ {b1}" if b1 >= 0 else f"- {abs(b1)}"
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\(y = {a1}x {b1_str}\) &nbsp;&nbsp;(1)<br>"
        rf"\({c2}x + {d2}y = {e2}\) &nbsp;&nbsp;(2)"
    )
    sub_lhs = c2 + d2 * a1
    sub_rhs = e2 - d2 * b1
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — equation (1) gives \(y\) in terms of \(x\). "
            rf"Substitute into equation (2):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({c2}x + {d2}({a1}x {b1_str}) = {e2}\)</div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — expand and collect \(x\) terms:"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({c2}x + {d2 * a1}x + {d2 * b1} = {e2}\)<br>"
            rf"\({sub_lhs}x = {sub_rhs}\) → <strong>\(x = {x_ans}\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 3</strong> — substitute \(x = {x_ans}\) into equation (1):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(y = {a1}({x_ans}) {b1_str} = <strong>{y_ans}</strong></div>"
        )
        + _sim_answer(x_ans, y_ans)
    )
    hint = (
        r"When one equation is already \(y = \ldots\) or \(x = \ldots\), replace that variable "
        r"in the second equation, solve for one unknown, then substitute back."
    )
    return q, sol, hint, 3, _sim_pair_answer(x_ans, y_ans)


def _sim_f_simple_pair():
    """Two equations, different coefficients, integer solution."""
    x_ans = random.randint(2, 5)
    y_ans = random.randint(2, 5)
    a1, b1, a2, b2 = 2, 1, 1, 2
    c1 = a1 * x_ans + b1 * y_ans
    c2 = a2 * x_ans + b2 * y_ans
    eq1, eq2 = _build_pair(x_ans, y_ans, a1, b1, a2, b2)
    q = rf"Solve the simultaneous equations:<br>{eq1} &nbsp;&nbsp;(1)<br>{eq2} &nbsp;&nbsp;(2)"
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — multiply equation (1) by 2 so the \(y\) terms match:"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(2 \times ({a1}x + {b1}y = {c1})\) → \(4x + 2y = {2 * c1}\)</div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — subtract equation (2) to eliminate \(y\):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(4x + 2y = {2 * c1}\)<br>\(x + 2y = {c2}\)<br>"
            rf"\(3x = {2 * c1 - c2}\) → <strong>\(x = {x_ans}\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 3</strong> — substitute \(x = {x_ans}\) into equation (2):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({x_ans} + 2y = {c2}\) → <strong>\(y = {y_ans}\)</strong></div>"
        )
        + _sim_answer(x_ans, y_ans)
    )
    hint = (
        r"Look for matching coefficients. Here, multiply one equation so the \(y\) terms "
        r"match, subtract to find \(x\), then substitute back."
    )
    return q, sol, hint, 2, _sim_pair_answer(x_ans, y_ans)


def _sim_f_classic_pair():
    """3x + 2y and x + 2y — subtract to eliminate y."""
    x_ans, y_ans = 3, 2
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\(3x + 2y = 13\) &nbsp;&nbsp;(1)<br>"
        rf"\(x + 2y = 7\) &nbsp;&nbsp;(2)"
    )
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — subtract equation (2) from (1) (the \(y\) terms cancel):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(3x + 2y = 13\)<br>\(x + 2y = 7\)<br>"
            rf"\(2x = 6\) → <strong>\(x = {x_ans}\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — substitute \(x = {x_ans}\) into equation (2):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(3 + 2y = 7\) → <strong>\(y = {y_ans}\)</strong></div>"
        )
        + _sim_answer(x_ans, y_ans)
    )
    hint = (
        r"When the \(y\) coefficients are identical, subtract one equation from the other "
        r"to eliminate \(y\), then substitute to find \(x\)."
    )
    return q, sol, hint, 2, _sim_pair_answer(x_ans, y_ans)


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _sim_i_elimination_multiply():
    """Multiply one equation to match coefficients."""
    x_ans = random.randint(2, 6)
    y_ans = random.randint(2, 6)
    a1, b1 = random.randint(2, 5), random.randint(2, 4)
    a2, b2 = random.randint(2, 5), random.randint(2, 4)
    attempts = 0
    while a1 * b2 == a2 * b1 and attempts < 20:
        a2, b2 = random.randint(2, 5), random.randint(2, 4)
        attempts += 1
    c1 = a1 * x_ans + b1 * y_ans
    c2 = a2 * x_ans + b2 * y_ans
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\({a1}x + {b1}y = {c1}\) &nbsp;&nbsp;(1)<br>"
        rf"\({a2}x + {b2}y = {c2}\) &nbsp;&nbsp;(2)"
    )
    mult1_lhs_x, mult1_lhs_y, mult1_rhs = a1 * b2, b1 * b2, c1 * b2
    mult2_lhs_x, mult2_lhs_y, mult2_rhs = a2 * b1, b2 * b1, c2 * b1
    elim_x_coeff = mult1_lhs_x - mult2_lhs_x
    elim_rhs = mult1_rhs - mult2_rhs
    sub_into = a1 * x_ans + b1 * y_ans
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — multiply equation (1) by \({b2}\) and equation (2) by \({b1}\) "
            rf"so the \(y\) coefficients match:"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({mult1_lhs_x}x + {mult1_lhs_y}y = {mult1_rhs}\)<br>"
            rf"\({mult2_lhs_x}x + {mult2_lhs_y}y = {mult2_rhs}\)</div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — subtract the second line from the first to eliminate \(y\):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({elim_x_coeff}x = {elim_rhs}\) → <strong>\(x = {x_ans}\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 3</strong> — substitute \(x = {x_ans}\) into equation (1):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({a1}({x_ans}) + {b1}y = {c1}\) → \({sub_into} + {b1}y = {c1}\) "
            rf"→ <strong>\(y = {y_ans}\)</strong></div>"
        )
        + _sim_answer(x_ans, y_ans)
    )
    hint = (
        "When coefficients do not match yet, multiply one or both equations so one variable "
        "has the same coefficient, then add or subtract to eliminate it."
    )
    return q, sol, hint, 4, _sim_pair_answer(x_ans, y_ans)


def _sim_i_substitution_rearrange():
    """Rearrange one equation then substitute."""
    x_ans = random.randint(2, 5)
    y_ans = random.randint(2, 5)
    a, b, c = 2, 3, 2 * x_ans + 3 * y_ans
    d, e, f = 4, 1, 4 * x_ans + y_ans
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\({a}x + {b}y = {c}\) &nbsp;&nbsp;(1)<br>"
        rf"\({d}x + {e}y = {f}\) &nbsp;&nbsp;(2)"
    )
    x_coeff = a - b * d
    x_rhs = c - b * f
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — rearrange equation (2) to make \(y\) the subject:"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(y = {f} - {d}x\)</div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — substitute into equation (1):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({a}x + {b}({f} - {d}x) = {c}\)<br>"
            rf"\({a}x + {b * f} - {b * d}x = {c}\)<br>"
            rf"\({x_coeff}x = {x_rhs}\) → <strong>\(x = {x_ans}\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 3</strong> — substitute \(x = {x_ans}\) back into \(y = {f} - {d}x\):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(y = {f} - {d}({x_ans}) = <strong>{y_ans}</strong></div>"
        )
        + _sim_answer(x_ans, y_ans)
    )
    hint = (
        r"When neither variable is isolated, rearrange the easier equation first "
        r"(here, equation (2) has \(y\) with coefficient 1), then substitute."
    )
    return q, sol, hint, 3, _sim_pair_answer(x_ans, y_ans)


def _sim_i_word_tickets():
    """Two days of sales — find adult and child ticket prices."""
    adult_p = random.randint(8, 12)
    child_p = random.randint(4, 7)
    while child_p == adult_p:
        child_p = random.randint(4, 7)
    n1a, n1c = random.randint(15, 25), random.randint(20, 35)
    n2a, n2c = random.randint(10, 18), random.randint(25, 40)
    total1 = adult_p * n1a + child_p * n1c
    total2 = adult_p * n2a + child_p * n2c
    q = (
        rf"Adult tickets cost \(a\) pounds and child tickets cost \(c\) pounds.<br>"
        rf"Day 1: {n1a} adult and {n1c} child tickets sold for <strong>£{total1}</strong>.<br>"
        rf"Day 2: {n2a} adult and {n2c} child tickets sold for <strong>£{total2}</strong>.<br>"
        rf"Find \(a\) and \(c\)."
    )
    mult1_a_coeff = n1a * n2c
    mult1_c_coeff = n1c * n2c
    mult1_rhs = total1 * n2c
    mult2_a_coeff = n2a * n1c
    mult2_c_coeff = n2c * n1c
    mult2_rhs = total2 * n1c
    elim_a_coeff = mult1_a_coeff - mult2_a_coeff
    elim_rhs = mult1_rhs - mult2_rhs
    sub_line = n1a * adult_p + n1c * child_p
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — write one equation per day:"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({n1a}a + {n1c}c = {total1}\) &nbsp;&nbsp;(1)<br>"
            rf"\({n2a}a + {n2c}c = {total2}\) &nbsp;&nbsp;(2)</div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — multiply (1) by \({n2c}\) and (2) by \({n1c}\) "
            rf"so the \(c\) terms match:"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({mult1_a_coeff}a + {mult1_c_coeff}c = {mult1_rhs}\)<br>"
            rf"\({mult2_a_coeff}a + {mult2_c_coeff}c = {mult2_rhs}\)</div>"
        )
        + _sim_step(
            rf"<strong>Step 3</strong> — subtract to eliminate \(c\):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({elim_a_coeff}a = {elim_rhs}\) → <strong>\(a = {adult_p}\)</strong> pounds</div>"
        )
        + _sim_step(
            rf"<strong>Step 4</strong> — substitute \(a = {adult_p}\) into equation (1):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\({n1a}({adult_p}) + {n1c}c = {total1}\) → \({sub_line} + {n1c}c = {total1}\) "
            rf"→ <strong>\(c = {child_p}\)</strong> pounds</div>"
        )
        + _sim_step(rf"<strong>Answer:</strong> adult ticket \(a = {adult_p}\) pounds, child ticket \(c = {child_p}\) pounds")
    )
    hint = (
        "Translate each day's sales into an equation. Then use elimination — multiply "
        "equations if the coefficients do not match yet."
    )
    return q, sol, hint, 4, _sim_pair_answer(adult_p, child_p, "Adult price (£)", "Child price (£)")


def _sim_i_find_y_only():
    """Solve and state y only (exam-style)."""
    x_ans, y_ans = 4, 1
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\(x + y = 5\) &nbsp;&nbsp;(1)<br>"
        rf"\(x - y = 3\) &nbsp;&nbsp;(2)<br><br>"
        rf"What is <strong>\(y\)</strong>?"
    )
    sol = (
        _sim_step(
            rf"<strong>Step 1</strong> — add equations (1) and (2) to eliminate \(y\):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(x + y = 5\)<br>\(x - y = 3\)<br>"
            rf"\(2x = 8\) → <strong>\(x = 4\)</strong></div>"
        )
        + _sim_step(
            rf"<strong>Step 2</strong> — substitute \(x = 4\) into equation (1):"
            f'<div style="margin:8px 0 0 16px;">'
            rf"\(4 + y = 5\) → <strong>\(y = {y_ans}\)</strong></div>"
        )
        + _sim_step(rf"<strong>Answer:</strong> the question asks for \(y\) only, so <strong>\(y = {y_ans}\)</strong>")
    )
    hint = (
        "Solve the pair fully, but only state the variable the question asks for in your final answer."
    )
    return q, sol, hint, 2, _sim_linear_answer(y_ans, "y")


def _sim_i_graph_interpret():
    """Link to intersection of two lines — MCQ."""
    m1 = random.randint(1, 3)
    c1 = random.randint(1, 5)
    m2 = -random.randint(1, 3)
    c2 = random.randint(4, 10)
    q = (
        rf"The lines \(y = {m1}x + {c1}\) and \(y = {m2}x + {c2}\) are drawn on the same axes. "
        r"What do the coordinates of their point of intersection represent?"
    )
    correct = "The solution to the simultaneous equations"
    distractors = [
        "The midpoint between the two y-intercepts",
        "The gradient of both lines",
        "Where the lines are parallel",
    ]
    texts = [correct] + distractors
    random.shuffle(texts)
    letters = "ABCD"
    correct_letter = letters[texts.index(correct)]
    opts = [f"{letters[i]}  {texts[i]}" for i in range(4)]
    sol = (
        rf"The intersection is the <strong>solution to the simultaneous equations</strong> "
        rf"\(y = {m1}x + {c1}\) and \(y = {m2}x + {c2}\) — the only \((x, y)\) that satisfies both.<br>"
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    hint = "Graphical solution = algebraic solution = point where lines cross."
    return q, sol, hint, 2, opts, correct_letter


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

def _sim_d_general_elimination():
    """Fully random integer coefficients (non-parallel)."""
    x_ans = random.randint(2, 7)
    y_ans = random.randint(2, 7)
    a1, b1 = random.randint(2, 6), random.randint(2, 5)
    a2, b2 = random.randint(2, 6), random.randint(2, 5)
    attempts = 0
    while a1 * b2 == a2 * b1 and attempts < 25:
        a2, b2 = random.randint(2, 6), random.randint(2, 5)
        attempts += 1
    c1 = a1 * x_ans + b1 * y_ans
    c2 = a2 * x_ans + b2 * y_ans
    q = (
        rf"Solve the simultaneous equations:<br>"
        rf"\({a1}x + {b1}y = {c1}\) &nbsp;&nbsp;(1)<br>"
        rf"\({a2}x + {b2}y = {c2}\) &nbsp;&nbsp;(2)"
    )
    sol = (
        rf"Eliminate one variable (multiply if needed), substitute back.<br>"
        rf"<strong>\(x = {x_ans},\; y = {y_ans}\)</strong>"
    )
    return q, sol, "Show multiplying equations and subtracting — examiners award method marks.", 4, _sim_pair_answer(x_ans, y_ans)


def _sim_d_cafe_prices():
    """Two days, two drinks — simultaneous equations."""
    coffee = random.randint(2, 4)
    tea = random.randint(2, 5)
    while tea == coffee:
        tea = random.randint(2, 5)
    n1c, n1t = random.randint(8, 14), random.randint(6, 12)
    n2c, n2t = random.randint(4, 9), random.randint(10, 16)
    total1 = n1c * coffee + n1t * tea
    total2 = n2c * coffee + n2t * tea
    q = (
        rf"On Monday a café sells {n1c} coffees and {n1t} teas for <strong>£{total1}</strong>. "
        rf"On Tuesday it sells {n2c} coffees and {n2t} teas for <strong>£{total2}</strong>. "
        rf"Let \(c\) = price of one coffee and \(t\) = price of one tea (in pounds). "
        rf"Write two equations and solve for \(c\) and \(t\)."
    )
    sol = (
        rf"\({n1c}c + {n1t}t = {total1}\), \({n2c}c + {n2t}t = {total2}\). "
        rf"Eliminate \(t\) (or \(c\)) by multiplying and subtracting.<br>"
        rf"<strong>\(c = {coffee}\), \(t = {tea}\)</strong> pounds."
    )
    return q, sol, "One equation per day; two unknowns need two independent equations.", 5, _sim_pair_answer(coffee, tea, "Coffee (£)", "Tea (£)")


def _sim_d_matching_x_terms():
    """Subtract when x-coefficients match."""
    x_ans, y_ans = 2, 1
    q = (
        r"Solve the simultaneous equations:<br>"
        r"\(5x + 2y = 12\) &nbsp;&nbsp;(1)<br>"
        r"\(5x - y = 9\) &nbsp;&nbsp;(2)"
    )
    sol = (
        r"Subtract (2) from (1): \(3y = 3\) → <strong>\(y = 1\)</strong><br>"
        r"Substitute into (2): \(5x - 1 = 9\) → <strong>\(x = 2\)</strong><br>"
        rf"<strong>\(x = {x_ans},\; y = {y_ans}\)</strong>"
    )
    return q, sol, "Subtract equations when the x-terms match.", 4, _sim_pair_answer(x_ans, y_ans)


def _sim_d_apples_oranges():
    """Shop word problem with two unknown prices."""
    apple = random.randint(30, 50)
    orange = random.randint(20, 40)
    n1a, n1o = random.randint(4, 8), random.randint(5, 10)
    n2a, n2o = random.randint(6, 12), random.randint(2, 6)
    t1 = apple * n1a + orange * n1o
    t2 = apple * n2a + orange * n2o
    q = (
        rf"A shop sells apples at \(a\) p each and oranges at \(o\) p each.<br>"
        rf"Customer 1 buys {n1a} apples and {n1o} oranges and pays <strong>{t1}p</strong>.<br>"
        rf"Customer 2 buys {n2a} apples and {n2o} oranges and pays <strong>{t2}p</strong>.<br>"
        rf"Find \(a\) and \(o\)."
    )
    sol = (
        rf"\({n1a}a + {n1o}o = {t1}\), \({n2a}a + {n2o}o = {t2}\). "
        rf"Solve by elimination.<br>"
        rf"<strong>\(a = {apple}\)p, \(o = {orange}\)p</strong>"
    )
    return q, sol, "Two purchases → two equations in two unknowns.", 5, _sim_pair_answer(apple, orange, "Apple (p)", "Orange (p)")


def _sim_d_exam_multipart():
    """Short (a)(b) style — form equations from a word problem, then solve."""
    x_ans = random.randint(2, 6)
    y_ans = random.randint(2, 6)
    n_y = random.randint(2, 4)
    n_x1 = random.randint(1, 3)
    n_x2 = n_x1 + random.randint(1, 3)
    total1 = n_x1 * x_ans + n_y * y_ans
    total2 = n_x2 * x_ans + n_y * y_ans
    diff_x = n_x2 - n_x1
    diff_rhs = total2 - total1
    eq1, eq2 = _build_pair(x_ans, y_ans, n_x1, n_y, n_x2, n_y)
    q = (
        rf"At a shop, each item of type X costs \(x\) pounds and each item of type Y costs \(y\) pounds.<br>"
        rf"Customer A buys <strong>{n_x1}</strong> of type X and <strong>{n_y}</strong> of type Y "
        rf"and pays <strong>{total1} pounds</strong>.<br>"
        rf"Customer B buys <strong>{n_x2}</strong> of type X and <strong>{n_y}</strong> of type Y "
        rf"and pays <strong>{total2} pounds</strong>.<br><br>"
        rf"<strong>(a)</strong> Write two equations relating \(x\) and \(y\).<br>"
        rf"<strong>(b)</strong> Solve your equations to find \(x\) and \(y\)."
    )
    sol = (
        rf"<strong>(a)</strong> {eq1} &nbsp;&nbsp;(1); {eq2} &nbsp;&nbsp;(2)<br>"
        rf"<strong>(b)</strong> Both equations have {n_y}y, so subtract (1) from (2):<br>"
        rf"\({diff_x}x = {diff_rhs}\) → <strong>\(x = {x_ans}\)</strong><br>"
        rf"Substitute into (1): \({n_x1}({x_ans}) + {n_y}y = {total1}\) → "
        rf"<strong>\(y = {y_ans}\)</strong><br>"
        rf"<strong>\(x = {x_ans},\; y = {y_ans}\)</strong>"
    )
    return q, sol, "Part (a): one equation per customer; part (b): subtract when y-terms match.", 4, _sim_pair_answer(x_ans, y_ans)


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (10)
# ══════════════════════════════════════════════════════════════════════════════

_SIM_MCQ_BANK = [
    {
        "difficulty": "foundational",
        "q": r"Solve simultaneously: \(x + y = 7\) and \(x - y = 3\). What is \(x\)?",
        "opts": ["A  x = 2", "B  x = 5", "C  x = 4", "D  x = 3"],
        "ans": "B",
        "marks": 2,
        "sol": (
            r"<strong>Step 1</strong> — add the equations (\(+y\) and \(-y\) cancel): "
            r"\(2x = 10\) → \(x = 5\).<br>"
            r"Answer: <strong>B</strong>"
        ),
        "hint": "Adding the equations eliminates y.",
    },
    {
        "difficulty": "foundational",
        "q": r"Lines \(3x + 2y = 13\) and \(x + 2y = 7\) intersect at:",
        "opts": ["A  (2, 3)", "B  (3, 2)", "C  (3, 1)", "D  (5, 2)"],
        "ans": "B",
        "marks": 2,
        "sol": (
            r"<strong>Step 1</strong> — subtract (2) from (1) (the \(2y\) terms cancel): "
            r"\(2x = 6\) → \(x = 3\).<br>"
            r"<strong>Step 2</strong> — substitute into (2): \(3 + 2y = 7\) → \(y = 2\). "
            r"Intersection: \((3, 2)\).<br>"
            r"Answer: <strong>B</strong>"
        ),
        "hint": "The intersection point solves both equations.",
    },
    {
        "difficulty": "intermediate",
        "q": r"To solve \(y = 2x + 1\) and \(3x + y = 14\), the best first step is:",
        "opts": [
            "A  Add the equations",
            r"B  Substitute \(y = 2x + 1\) into \(3x + y = 14\)",
            "C  Divide both equations by 2",
            "D  Graph only — no algebra",
        ],
        "ans": "B",
        "marks": 2,
        "sol": (
            r"<strong>Step 1</strong> — equation (1) is already \(y = 2x + 1\). "
            r"Substitute into (2): \(3x + (2x + 1) = 14\).<br>"
            r"Answer: <strong>B</strong>"
        ),
        "hint": "Substitution works when one variable is isolated.",
    },
    {
        "difficulty": "intermediate",
        "q": r"How many solutions do two non-parallel straight lines have in common?",
        "opts": ["A  0", "B  1", "C  2", "D  Infinitely many"],
        "ans": "B",
        "marks": 1,
        "sol": r"Non-parallel lines cross once. Answer: <strong>B</strong>",
        "hint": "Think about the graph — one intersection point.",
    },
    {
        "difficulty": "difficult",
        "q": r"\(2x + 3y = 12\) and \(5x - y = 9\). After eliminating \(x\), you get:",
        "opts": [r"A  \(y = 1\)", r"B  \(3y = 3\)", r"C  \(y = 3\)", r"D  \(5y = 15\)"],
        "ans": "B",
        "marks": 2,
        "sol": r"Subtract (2) from (1): \(3y = 3\). Answer: <strong>B</strong>",
        "hint": "Subtract the equations when the x-terms match (5x and 5x).",
    },
    {
        "difficulty": "difficult",
        "q": r"Which describes <strong>elimination</strong> for simultaneous equations?",
        "opts": [
            "A  Multiply one equation only",
            "B  Add or subtract equations to remove one variable",
            "C  Always substitute into a quadratic",
            "D  Guess values until both work",
        ],
        "ans": "B",
        "marks": 1,
        "sol": r"Elimination combines equations to knock out x or y. Answer: <strong>B</strong>",
        "hint": "Eliminate = remove one unknown by adding/subtracting.",
    },
    {
        "difficulty": "foundational",
        "q": r"Solve simultaneously: \(x + y = 10\) and \(x - y = 4\). What is \(y\)?",
        "opts": ["A  y = 3", "B  y = 7", "C  y = 5", "D  y = 4"],
        "ans": "A",
        "marks": 2,
        "sol": (
            r"<strong>Step 1</strong> — subtract (2) from (1): \((x + y) - (x - y) = 10 - 4\) "
            r"→ \(2y = 6\) → \(y = 3\).<br>"
            r"Answer: <strong>A</strong>"
        ),
        "hint": "Subtracting the equations eliminates x.",
    },
    {
        "difficulty": "foundational",
        "q": r"If \(x + y = 9\) and \(x = 5\), what is \(y\)?",
        "opts": ["A  y = 4", "B  y = 5", "C  y = 14", "D  y = 45"],
        "ans": "A",
        "marks": 1,
        "sol": r"Substitute \(x = 5\): \(5 + y = 9\) → \(y = 4\). Answer: <strong>A</strong>",
        "hint": "Put the known value of x into the first equation.",
    },
    {
        "difficulty": "intermediate",
        "q": r"To eliminate \(y\) from \(2x + y = 7\) and \(3x - y = 8\), you should:",
        "opts": [
            "A  Add the equations",
            "B  Subtract the equations",
            "C  Multiply the first equation by 3",
            "D  Graph both lines",
        ],
        "ans": "A",
        "marks": 2,
        "sol": (
            r"<strong>Step 1</strong> — add the equations (\(+y\) and \(-y\) cancel): "
            r"\(5x = 15\) → \(x = 3\).<br>"
            r"Answer: <strong>A</strong>"
        ),
        "hint": "Add when the matching terms have opposite signs.",
    },
    {
        "difficulty": "difficult",
        "q": r"\(4x + 3y = 18\) and \(4x - y = 2\). Subtracting equation (2) from (1) gives:",
        "opts": [r"A  \(4y = 16\)", r"B  \(2y = 20\)", r"C  \(4y = 20\)", r"D  \(y = 16\)"],
        "ans": "A",
        "marks": 2,
        "sol": r"The x-terms match (4x), so subtract: \(4y = 16\) → \(y = 4\). Answer: <strong>A</strong>",
        "hint": "Subtract when the x-terms are identical.",
    },
]


def simultaneous_equations_mcq():
    item = random.choice(_SIM_MCQ_BANK)
    return item["q"], item["sol"], item.get("hint", ""), item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _sim_f_add_to_eliminate,
    _sim_f_elim_same_coefficient,
    _sim_f_substitution_y_equals,
    _sim_f_simple_pair,
    _sim_f_classic_pair,
]

_INTERMEDIATE = [
    _sim_i_elimination_multiply,
    _sim_i_substitution_rearrange,
    _sim_i_word_tickets,
    _sim_i_find_y_only,
    _sim_i_graph_interpret,
]

_DIFFICULT = [
    _sim_d_general_elimination,
    _sim_d_cafe_prices,
    _sim_d_matching_x_terms,
    _sim_d_apples_oranges,
    _sim_d_exam_multipart,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_simultaneous_equations_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_bank_with_procedural(
            _SIM_MCQ_BANK,
            procedural_mcq_for("simultaneous_equations"),
            "simultaneous_equations",
            difficulty,
            count=6,
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


def gcse_simultaneous_equations(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_simultaneous_equations_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "simultaneous_equations",
            options=opts, correct_answer=ans,
        )

    variants = gcse_simultaneous_equations_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    return _sim_problem_from_output(variant(), difficulty)
