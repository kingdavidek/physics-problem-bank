"""
GCSE Maths – Equations and Inequalities
17 foundational · 18 intermediate · 20 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Algebraic rearrangement, proof, and some multipart variants stay 4-tuples.
"""
import random
import math
from generators.shared.utils import make_problem
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


def _eq_abc_block(*parts):
    """Format sub-questions or solution steps as a), b), c)."""
    return "".join(
        f"<br><strong>{chr(ord('a') + i)})</strong> {text}"
        for i, text in enumerate(parts)
    )


def _eq_fmt_quad_poly(b, c):
    """Return '+ bx + c' fragment for x^2 + bx + c (clean signs, no leading x^2)."""
    parts = []
    if b != 0:
        if b == 1:
            parts.append(" + x")
        elif b == -1:
            parts.append(" - x")
        elif b > 0:
            parts.append(f" + {b}x")
        else:
            parts.append(f" - {abs(b)}x")
    if c != 0:
        if c > 0:
            parts.append(f" + {c}")
        else:
            parts.append(f" - {abs(c)}")
    return "".join(parts)


def _eq_fmt_factor_bracket(root):
    """Format (x - r) with a positive root shown as (x + |r|) when r < 0."""
    if root == 0:
        return "(x)"
    if root > 0:
        return f"(x - {root})"
    return f"(x + {abs(root)})"


def _eq_raw(value):
    """Canonical numeric string for typed answer checking."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:g}"
    return str(value)


def _eq_linear_answer(value, var='x'):
    return {'type': 'linear', 'value': _eq_raw(value), 'var': str(var).strip().lower()}


def _eq_quadratic_roots_answer(*roots, format_hint=None):
    payload = {'type': 'quadratic_roots', 'roots': tuple(_eq_raw(r) for r in roots)}
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _eq_number_pair_answer(val_a, val_b, label_a='Answer 1', label_b='Answer 2', sep='and'):
    return {
        'type': 'number_pair',
        'values': (_eq_raw(val_a), _eq_raw(val_b)),
        'label_a': label_a,
        'label_b': label_b,
        'sep': sep,
    }


def _eq_coord_pairs_answer(x1, y1, x2, y2):
    return {
        'type': 'coordinate_pairs',
        'values': (_eq_raw(x1), _eq_raw(y1), _eq_raw(x2), _eq_raw(y2)),
        'labels': ('1st solution (x, y)', '2nd solution (x, y)'),
    }


def _eq_number_list_answer(values):
    return {'type': 'number_list', 'values': tuple(_eq_raw(v) for v in values)}


def _eq_keyword_answer(value):
    return {'type': 'keyword', 'value': str(value).strip().lower()}


def _eq_latex_sign_to_canonical(sym: str) -> str:
    mapping = {
        r'\gt': '>',
        r'\geq': '>=',
        r'\ge': '>=',
        r'\lt': '<',
        r'\leq': '<=',
        r'\le': '<=',
    }
    return mapping.get(str(sym).strip(), str(sym).strip())


def _eq_linear_inequality_answer(value, sign, var='x'):
    return {
        'type': 'linear_inequality',
        'var': str(var).strip().lower(),
        'sign': _eq_latex_sign_to_canonical(sign),
        'value': _eq_raw(value),
    }


def _eq_compound_inequality_answer(var, left_sign, left_val, right_sign, right_val):
    return {
        'type': 'compound_inequality',
        'var': str(var).strip().lower(),
        'left_sign': _eq_latex_sign_to_canonical(left_sign),
        'left': _eq_raw(left_val),
        'right_sign': _eq_latex_sign_to_canonical(right_sign),
        'right': _eq_raw(right_val),
    }


def _eq_number_line_answer(var, left_sign, left_val, right_sign, right_val,
                           axis_min=None, axis_max=None):
    left = int(left_val)
    right = int(right_val)
    amin = int(axis_min) if axis_min is not None else left - 1
    amax = int(axis_max) if axis_max is not None else right + 1
    if amax - amin < 4:
        amax = amin + 4
    return {
        'type': 'number_line',
        'var': str(var).strip().lower(),
        'left_sign': _eq_latex_sign_to_canonical(left_sign),
        'left': _eq_raw(left_val),
        'right_sign': _eq_latex_sign_to_canonical(right_sign),
        'right': _eq_raw(right_val),
        'axis_min': amin,
        'axis_max': amax,
    }


def _eq_formula_fraction_answer(numerator, denominator, var='x'):
    return {
        'type': 'formula_fraction',
        'var': str(var).strip().lower(),
        'numerator': str(numerator).strip(),
        'denominator': str(denominator).strip(),
    }


def _eq_subj_frac(num, den):
    if den == 1:
        return str(num)
    return f'({num})/({den})'


def _eq_subj_sqrt(inner):
    return f'√({inner})'


def _eq_subj_formula(subject, rhs):
    return f'{subject}={rhs}'


def _eq_algebraic_answer(expr, subject=None, format_hint=None):
    payload = {'type': 'algebraic', 'value': str(expr)}
    if subject:
        payload['subject'] = str(subject).strip().lower()
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _eq_completed_square_answer(kind, *values, subject=None):
    payload = {
        'type': 'completed_square',
        'kind': str(kind),
        'values': tuple(_eq_raw(v) for v in values),
    }
    if subject:
        payload['subject'] = str(subject)
    return payload


def _eq_number_fields_answer(values, labels, field_types=None):
    types = tuple(field_types) if field_types else tuple('number' for _ in values)
    return {
        'type': 'number_fields',
        'values': tuple(_eq_raw(v) for v in values),
        'labels': tuple(labels),
        'field_types': types,
    }


def _eq_two_var_equation_raw(var1, var2, coef1, coef2, total):
    return f'eq:{var1},{var2}:{coef1}:{coef2}:{total}'


def _eq_linear_inequality_raw(raw):
    var = raw.get('var') or 'x'
    sign = raw.get('sign') or '>='
    val = raw.get('value')
    return f'{var}|{sign}|{val}'


def _eq_compound_inequality_raw(raw):
    var = raw.get('var') or 'x'
    return '|'.join([
        var,
        raw.get('left_sign') or '<',
        _eq_raw(raw.get('left')),
        raw.get('right_sign') or '<=',
        _eq_raw(raw.get('right')),
    ])


def _eq_linear_raw(raw):
    var = raw.get('var') or 'x'
    val = raw.get('value')
    if var == 'x':
        return str(val)
    return f'{var}={val}'


def _eq_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'linear':
                extra = {
                    'correct_answer_raw': _eq_linear_raw(raw),
                    'answer_type': 'linear',
                    'answer_format_hint': 'Enter the value (e.g. x = 3 or just 3)',
                }
            elif raw_type == 'quadratic_roots':
                roots = raw.get('roots') or ()
                hint = raw.get('format_hint')
                if not hint:
                    if len(roots) == 4:
                        hint = 'Enter all four roots separated by commas (e.g. 1, -1, 2, -2)'
                    else:
                        hint = 'Enter roots separated by commas (e.g. 3, -2)'
                extra = {
                    'correct_answer_raw': ','.join(str(r) for r in roots),
                    'answer_type': 'quadratic_roots',
                    'answer_format_hint': hint,
                }
            elif raw_type == 'number_pair':
                val_a, val_b = raw['values']
                extra = {
                    'correct_answer_raw': f'{val_a}|{val_b}',
                    'answer_type': 'number_pair',
                    'answer_labels': [raw['label_a'], raw['label_b']],
                    'answer_pair_sep': raw.get('sep', 'and'),
                }
            elif raw_type == 'coordinate_pairs':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if len(values) == 4:
                    extra = {
                        'correct_answer_raw': '|'.join(str(v) for v in values),
                        'answer_type': 'coordinate_pairs',
                        'answer_labels': list(labels) if labels else [
                            '1st solution (x, y)',
                            '2nd solution (x, y)',
                        ],
                        'answer_format_hint': 'Enter each solution as coordinates, e.g. (-2, 4)',
                    }
            elif raw_type == 'number_list':
                extra = {
                    'correct_answer_raw': ','.join(str(v) for v in raw['values']),
                    'answer_type': 'number_list',
                    'answer_format_hint': 'Enter numbers separated by commas',
                }
            elif raw_type == 'keyword':
                value = raw.get('value')
                if value is not None and str(value).strip():
                    extra = {
                        'correct_answer_raw': str(value).strip().lower(),
                        'answer_type': 'keyword',
                        'answer_format_hint': 'e.g. yes or no',
                    }
            elif raw_type == 'linear_inequality':
                extra = {
                    'correct_answer_raw': _eq_linear_inequality_raw(raw),
                    'answer_type': 'linear_inequality',
                    'answer_subject': raw.get('var') or 'x',
                    'answer_format_hint': 'Choose the sign, then enter the value',
                }
            elif raw_type == 'compound_inequality':
                extra = {
                    'correct_answer_raw': _eq_compound_inequality_raw(raw),
                    'answer_type': 'compound_inequality',
                    'answer_subject': raw.get('var') or 'x',
                    'answer_format_hint': 'Enter both bounds and choose each sign',
                }
            elif raw_type == 'number_line':
                extra = {
                    'correct_answer_raw': _eq_compound_inequality_raw(raw),
                    'answer_type': 'number_line',
                    'answer_subject': raw.get('var') or 'x',
                    'answer_axis_min': raw.get('axis_min'),
                    'answer_axis_max': raw.get('axis_max'),
                    'answer_format_hint': (
                        'Drag the endpoints. Click a circle to toggle open or closed.'
                    ),
                }
            elif raw_type == 'formula_fraction':
                extra = {
                    'correct_answer_raw': '|'.join([
                        raw.get('numerator') or '',
                        raw.get('denominator') or '',
                    ]),
                    'answer_type': 'formula_fraction',
                    'answer_subject': raw.get('var') or 'x',
                    'answer_format_hint': 'Enter the numerator and denominator',
                }
            elif raw_type == 'algebraic':
                text = str(raw.get('value') or '')
                extra = {
                    'correct_answer_raw': text,
                    'answer_type': 'algebraic',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter the rearranged formula, e.g. x = (y - 3)/2',
                    ),
                }
                if raw.get('subject'):
                    extra['answer_subject'] = raw['subject']
            elif raw_type == 'completed_square':
                kind = raw.get('kind') or 'plus'
                values = raw.get('values') or ()
                extra = {
                    'correct_answer_raw': '|'.join([kind, *[str(v) for v in values]]),
                    'answer_type': 'completed_square',
                    'answer_template_kind': kind,
                    'answer_subject': raw.get('subject', ''),
                    'answer_format_hint': 'Use + or − for each term, then enter each number',
                }
            elif raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                field_types = raw.get('field_types') or ()
                if values and labels and len(values) == len(labels):
                    sep = (
                        '\x1e'
                        if field_types and any(t != 'number' for t in field_types)
                        else '|'
                    )
                    extra = {
                        'correct_answer_raw': sep.join(str(v) for v in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_field_types': list(field_types) if field_types else (
                            ['number'] * len(labels)
                        ),
                        'answer_format_hint': 'Enter a number in every field',
                    }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _eq_raw(raw),
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
        'gcse', 'maths', 'equations_inequalities', **extra
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (17 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _eq_found_one_step_add():
    b = random.randint(2, 15)
    ans = random.randint(2, 12)
    c = ans + b
    q = rf"Solve \(x + {b} = {c}\)."
    s = (rf"Subtract {b} from both sides:<br>"
         rf"\(x = {c} - {b}\)<br>"
         rf"<strong>\(x = {ans}\)</strong>")
    hint = f"Subtract {b} from both sides."
    return q, s, hint, 1, _eq_linear_answer(ans)


def _eq_found_one_step_multiply():
    a = random.randint(2, 9)
    ans = random.randint(2, 10)
    c = a * ans
    q = rf"Solve \({a}x = {c}\)."
    s = (rf"Divide both sides by {a}:<br>"
         rf"\(x = \dfrac{{{c}}}{{{a}}}\)<br>"
         rf"<strong>\(x = {ans}\)</strong>")
    hint = f"Divide both sides by {a}."
    return q, s, hint, 1, _eq_linear_answer(ans)


def _eq_found_two_step():
    a = random.randint(2, 6)
    b = random.randint(1, 10)
    ans = random.randint(1, 8)
    c = a * ans + b
    q = rf"Solve \({a}x + {b} = {c}\)."
    s = (rf"Step 1 — subtract {b} from both sides: \({a}x = {c - b}\)<br>"
         rf"Step 2 — divide both sides by {a}: \(x = \dfrac{{{c-b}}}{{{a}}}\)<br>"
         rf"<strong>\(x = {ans}\)</strong>")
    hint = f"First subtract {b}, then divide by {a}."
    return q, s, hint, 2, _eq_linear_answer(ans)


def _eq_found_substitute_formula():
    v = random.randint(10, 30)
    u = random.randint(2, v - 1)
    a = random.randint(1, 5)
    # v = u + at  → t = (v-u)/a (ensure divisible)
    a = v - u  # make t = 1 always to keep it clean
    t_ans = 1
    q = rf"Using the formula \(v = u + at\), find \(t\) when \(v = {v}\), \(u = {u}\), \(a = {a}\)."
    s = (rf"Substitute the values: \({v} = {u} + {a}t\)<br>"
         rf"Subtract {u}: \({v - u} = {a}t\)<br>"
         rf"Divide by {a}: \(t = \dfrac{{{v-u}}}{{{a}}}\)<br>"
         rf"<strong>\(t = {t_ans}\)</strong>")
    hint = "Substitute the numbers, then rearrange to find t."
    return q, s, hint, 2, _eq_linear_answer(t_ans, "t")


def _eq_found_simple_inequality():
    b = random.randint(1, 8)
    ans = random.randint(2, 10)
    c = ans + b
    sym = random.choice([r"\gt", r"\geq"])
    sign = _eq_latex_sign_to_canonical(sym)
    q = rf"Solve \(x + {b} {sym} {c}\)."
    s = (rf"Subtract {b} from both sides:<br>"
         rf"<strong>\(x {sym} {ans}\)</strong>")
    hint = f"Treat it like an equation — subtract {b} from both sides."
    return q, s, hint, 1, _eq_linear_inequality_answer(ans, sign)


def _eq_found_double_inequality():
    lo = random.randint(1, 4)
    hi = lo + random.randint(3, 6)
    mid_lo = lo + 1
    q = rf"List the integer values of \(x\) such that \({lo} \lt x \leq {hi}\)."
    ints = list(range(mid_lo, hi + 1))
    ints_str = ", ".join(str(i) for i in ints)
    q_part2 = rf"(Note: \(x\) is an integer.)"
    s = (rf"The inequality \({lo} \lt x \leq {hi}\) means \(x\) is greater than {lo} and at most {hi}.<br>"
         rf"Integers satisfying this: <strong>{ints_str}</strong>")
    hint = f"x must be greater than {lo} (not including {lo}) and up to and including {hi}."
    return rf"{q} {q_part2}", s, hint, 2, _eq_number_list_answer(ints)


def _eq_found_ineq_solve_two_step():
    a = random.randint(2, 5)
    b = random.randint(1, 8)
    ans = random.randint(2, 7)
    c = a * ans + b
    sym = random.choice([r"\lt", r"\leq"])
    sign = _eq_latex_sign_to_canonical(sym)
    q = rf"Solve \({a}x + {b} {sym} {c}\)."
    s = (rf"Step 1 — subtract {b}: \({a}x {sym} {c - b}\)<br>"
         rf"Step 2 — divide by {a}: "
         rf"<strong>\(x {sym} {ans}\)</strong>")
    hint = f"Subtract {b} then divide by {a}. The inequality symbol stays the same."
    return q, s, hint, 2, _eq_linear_inequality_answer(ans, sign)


def _eq_found_verify_solution():
    a = random.randint(2, 5)
    b = random.randint(1, 9)
    ans = random.randint(2, 8)
    c = a * ans + b
    wrong = ans + random.choice([-1, 1, 2])
    q = (rf"A student says the solution to \({a}x + {b} = {c}\) is \(x = {wrong}\). "
         rf"Are they correct? Show your working.")
    lhs = a * wrong + b
    correct = lhs == c
    s = (rf"Substitute \(x = {wrong}\) into the left-hand side:<br>"
         rf"\({a} \times {wrong} + {b} = {lhs}\)<br>"
         + (rf"This equals {c}, so the student is <strong>correct</strong>."
            if correct else
            rf"This gives {lhs}, not {c}, so the student is <strong>incorrect</strong>. "
            rf"The correct solution is \(x = {ans}\)."))
    hint = f"Substitute x = {wrong} into {a}x + {b} and check if you get {c}."
    return q, s, hint, 2, _eq_keyword_answer("yes" if correct else "no")


def _eq_found_form_and_solve_words():
    n = random.randint(3, 9)
    result = random.randint(20, 40)
    # "I think of a number, multiply by n, and add 5" → n*x + 5 = result
    add = random.randint(2, 8)
    ans = random.randint(2, 6)
    result = n * ans + add
    q = (rf"I think of a number. I multiply it by {n} and add {add}. "
         rf"The result is {result}. What is the number?")
    s = (rf"Let the number be \(x\).<br>"
         rf"Form the equation: \({n}x + {add} = {result}\)<br>"
         rf"Subtract {add}: \({n}x = {result - add}\)<br>"
         rf"Divide by {n}: "
         rf"<strong>\(x = {ans}\)</strong>")
    hint = "Write an equation using the information, then solve it."
    return q, s, hint, 3, _eq_linear_answer(ans)


def _eq_found_brackets_simple():
    a = random.randint(2, 4)
    b = random.randint(1, 6)
    ans = random.randint(2, 7)
    c = a * (ans + b)
    q = rf"Solve \({a}(x + {b}) = {c}\)."
    s = (rf"Method 1 — divide both sides by {a} first:<br>"
         rf"\(x + {b} = {c // a}\)<br>"
         rf"Subtract {b}: <strong>\(x = {ans}\)</strong><br><br>"
         rf"Method 2 — expand first:<br>"
         rf"\({a}x + {a*b} = {c}\)<br>"
         rf"Subtract {a*b}: \({a}x = {c - a*b}\)<br>"
         rf"Divide by {a}: <strong>\(x = {ans}\)</strong>")
    hint = f"Either divide both sides by {a} first, or expand the brackets."
    return q, s, hint, 2, _eq_linear_answer(ans)


def _eq_found_rearrange_one_step():
    # Make v the subject: v = u + at  (one step: subtract u)
    q = r"Make \(u\) the subject of the formula \(v = u + at\)."
    s = (r"Subtract \(at\) from both sides:<br>"
         r"<strong>\(u = v - at\)</strong>")
    hint = "Move the unwanted terms to the opposite side."
    return q, s, hint, 2, _eq_algebraic_answer(
        _eq_subj_formula('u', 'v-at'),
        subject='u',
        format_hint='Enter the expression after u =, e.g. v - at',
    )


def _eq_found_fraction_eq():
    ans = random.randint(2, 9)
    a = random.randint(2, 5)
    b = a * ans
    q = rf"Solve \(\dfrac{{x}}{{{a}}} = {ans}\)."
    s = (rf"Multiply both sides by {a}:<br>"
         rf"<strong>\(x = {b}\)</strong>")
    hint = f"Multiply both sides by {a}."
    return q, s, hint, 1, _eq_linear_answer(b)


def _eq_found_negative_answer():
    a = random.randint(2, 5)
    ans = -random.randint(1, 5)
    b = random.randint(2, 8)
    c = a * ans + b
    q = rf"Solve \({a}x + {b} = {c}\)."
    s = (rf"Subtract {b}: \({a}x = {c} - {b} = {c - b}\)<br>"
         rf"Divide by {a}: "
         rf"<strong>\(x = {ans}\)</strong>")
    hint = "Don't be surprised if the answer is negative — just follow the steps."
    return q, s, hint, 2, _eq_linear_answer(ans)


def _eq_found_ineq_integer_list():
    lo = random.randint(-3, 0)
    hi = lo + random.randint(4, 7)
    q = rf"Write down all integer values of \(n\) such that \({lo} \leq n \lt {hi}\)."
    ints = list(range(lo, hi))
    ints_str = ", ".join(str(i) for i in ints)
    s = (rf"\(n\) must be at least {lo} and less than {hi}.<br>"
         rf"<strong>\(n = {ints_str}\)</strong>")
    hint = f"Start from {lo} (included) and go up to, but not including, {hi}."
    return q, s, hint, 2, _eq_number_list_answer(ints)


def _eq_found_write_ineq_from_words():
    n = random.randint(10, 25)
    q = (rf"A bag can hold at most {n} kg. Write an inequality for the weight \(w\) "
         rf"(in kg) that the bag can hold.")
    s = (rf"'At most {n} kg' means the weight is less than or equal to {n}:<br>"
         rf"<strong>\(w \leq {n}\)</strong>")
    hint = "'At most' means ≤; 'at least' means ≥; 'more than' means >."
    return q, s, hint, 1, _eq_linear_inequality_answer(n, '<=', 'w')


def _eq_found_rearrange_numeric_var():
    """Rearrange a linear formula with random numerical coefficients."""
    choice = random.choice(["y_mx_c", "s_kt", "p_aw_b"])
    if choice == "y_mx_c":
        m = random.randint(2, 7)
        c = random.randint(1, 12)
        q = rf"Make \(x\) the subject of \(y = {m}x + {c}\)."
        s = (rf"Subtract {c} from both sides: \(y - {c} = {m}x\)<br>"
             rf"Divide both sides by {m}: "
             rf"<strong>\(x = \dfrac{{y - {c}}}{{{m}}}\)</strong>")
        hint = f"Subtract {c}, then divide by {m}."
        return q, s, hint, 2, _eq_formula_fraction_answer(f'y-{c}', str(m), 'x')
    if choice == "s_kt":
        k = random.randint(2, 9)
        q = rf"Make \(t\) the subject of \(s = {k}t\)."
        s = rf"Divide both sides by {k}: <strong>\(t = \dfrac{{s}}{{{k}}}\)</strong>"
        hint = f"Divide both sides by {k}."
        return q, s, hint, 2, _eq_formula_fraction_answer('s', str(k), 't')
    a = random.randint(2, 6)
    b = random.randint(1, 10)
    q = rf"Make \(w\) the subject of \(P = {a}w + {b}\)."
    s = (rf"Subtract {b} from both sides: \(P - {b} = {a}w\)<br>"
         rf"Divide both sides by {a}: "
         rf"<strong>\(w = \dfrac{{P - {b}}}{{{a}}}\)</strong>")
    hint = f"Subtract {b}, then divide by {a}."
    return q, s, hint, 2, _eq_formula_fraction_answer(f'p-{b}', str(a), 'w')


def _eq_found_substitute_formula_var():
    """Substitute random values into a familiar formula."""
    choice = random.choice(["F_ma", "v_uat", "s_vt"])
    if choice == "F_ma":
        m = random.randint(2, 8)
        a = random.randint(2, 6)
        ans = m * a
        q = (rf"The force \(F\) (in newtons) is given by \(F = ma\). "
             rf"Find \(F\) when \(m = {m}\) and \(a = {a}\).")
        s = (rf"Substitute: \(F = {m} \times {a}\)<br>"
             rf"<strong>\(F = {ans}\) N</strong>")
        hint = "Replace m and a in the formula, then multiply."
    elif choice == "v_uat":
        u = random.randint(0, 15)
        a = random.randint(2, 5)
        t = random.randint(2, 8)
        ans = u + a * t
        q = rf"Using \(v = u + at\), find \(v\) when \(u = {u}\), \(a = {a}\) and \(t = {t}\)."
        s = (rf"Substitute: \(v = {u} + {a} \times {t}\)<br>"
             rf"\(v = {u} + {a * t}\)<br>"
             rf"<strong>\(v = {ans}\)</strong>")
        hint = "Substitute all three values into v = u + at."
    else:
        v = random.randint(5, 20)
        t = random.randint(2, 6)
        ans = v * t
        q = rf"Using \(s = vt\), find \(s\) when \(v = {v}\) and \(t = {t}\)."
        s = (rf"Substitute: \(s = {v} \times {t}\)<br>"
             rf"<strong>\(s = {ans}\)</strong>")
        hint = "Multiply speed by time."
    return q, s, hint, 2, ans


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (18 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _eq_inter_both_sides():
    # ax + b = cx + d with a > c, integer answer
    c = random.randint(1, 3)
    a = c + random.randint(1, 4)
    ans = random.randint(2, 8)
    d = random.randint(2, 10)
    b = (a - c) * ans - d  # ensures rhs = d + (a-c)*ans + b ... wait, recalc
    # ax + b = cx + d → (a-c)x = d - b → x = (d-b)/(a-c)
    b = random.randint(1, 6)
    d = (a - c) * ans + b
    q = rf"Solve \({a}x + {b} = {c}x + {d}\)."
    s = (rf"Collect \(x\)-terms on the left: \({a}x - {c}x = {d} - {b}\)<br>"
         rf"\({a-c}x = {d-b}\)<br>"
         rf"Divide by {a-c}: "
         rf"<strong>\(x = {ans}\)</strong>")
    hint = f"Subtract {c}x from both sides to collect x-terms."
    return q, s, hint, 3, _eq_linear_answer(ans)


def _eq_inter_expand_both_sides():
    a = random.randint(2, 4)
    b = random.randint(1, 5)
    c = random.randint(2, 4)
    ans = random.randint(2, 6)
    # a(x + b) = c(x + ?) → ax + ab = cx + c*?
    # need ax + ab = cx + d → (a-c)x = d - ab → x = (d-ab)/(a-c); require a != c
    while a == c:
        c = random.randint(2, 4)
    d_bracket = random.randint(1, 5)  # second bracket offset
    # Compute: a(x+b) = c(x + d_bracket) → ax+ab = cx+cd → (a-c)x = cd-ab
    cd = c * d_bracket
    ab = a * b
    ans_num = cd - ab
    ans_den = a - c
    if ans_den == 0 or ans_num % ans_den != 0:
        # fallback to safe values
        a, b, c, d_bracket = 3, 2, 1, 8
        ab, cd = a * b, c * d_bracket
        ans_num, ans_den = cd - ab, a - c
    ans = ans_num // ans_den
    q = rf"Solve \({a}(x + {b}) = {c}(x + {d_bracket})\)."
    s = (rf"Expand both sides:<br>"
         rf"\({a}x + {ab} = {c}x + {cd}\)<br>"
         rf"Collect \(x\)-terms: \({a}x - {c}x = {cd} - {ab}\)<br>"
         rf"\({a-c}x = {cd - ab}\)<br>"
         rf"<strong>\(x = {ans}\)</strong>")
    hint = "Expand each bracket first, then collect like terms."
    return q, s, hint, 3, _eq_linear_answer(ans)


def _eq_inter_simult_elim():
    x_ans = random.randint(1, 6)
    y_ans = random.randint(1, 6)
    # eq1: a1x + b1y = c1; eq2: a2x + b2y = c2 — choose so elimination easy
    a1, b1 = random.randint(1, 4), random.randint(1, 3)
    a2 = a1 + random.randint(1, 3)
    b2 = b1  # same y coefficient so we can subtract
    c1 = a1 * x_ans + b1 * y_ans
    c2 = a2 * x_ans + b2 * y_ans
    q = (rf"Solve the simultaneous equations:<br>"
         rf"\({a1}x + {b1}y = {c1}\) &nbsp;&nbsp;(1)<br>"
         rf"\({a2}x + {b2}y = {c2}\) &nbsp;&nbsp;(2)")
    s = (rf"Since the \(y\)-coefficients are equal, subtract (1) from (2):<br>"
         rf"\(({a2}-{a1})x = {c2}-{c1}\)<br>"
         rf"\({a2-a1}x = {c2-c1}\)<br>"
         rf"\(x = {x_ans}\)<br>"
         rf"Substitute into (1): \({a1}\times{x_ans} + {b1}y = {c1}\)<br>"
         rf"\({b1}y = {c1 - a1*x_ans}\)<br>"
         rf"<strong>\(x = {x_ans},\; y = {y_ans}\)</strong>")
    hint = "Subtract the equations to eliminate y (they have the same y coefficient)."
    return q, s, hint, 4, _eq_number_pair_answer(x_ans, y_ans, "x", "y", sep=",")


def _eq_inter_simult_sub():
    x_ans = random.randint(1, 5)
    y_ans = random.randint(1, 5)
    # eq1: y = ax + b; eq2: cx + dy = e
    a1 = random.randint(1, 3)
    b1 = y_ans - a1 * x_ans
    c2, d2 = random.randint(1, 4), random.randint(1, 3)
    e2 = c2 * x_ans + d2 * y_ans
    b1_str = f"+ {b1}" if b1 >= 0 else f"- {-b1}"
    q = (rf"Solve the simultaneous equations:<br>"
         rf"\(y = {a1}x {b1_str}\) &nbsp;&nbsp;(1)<br>"
         rf"\({c2}x + {d2}y = {e2}\) &nbsp;&nbsp;(2)")
    sub_result = c2 * x_ans + d2 * (a1 * x_ans + b1)
    coeff_x = c2 + d2 * a1
    const_term = d2 * b1
    const_str = f"+ {const_term}" if const_term >= 0 else f"- {-const_term}"
    s = (rf"Substitute (1) into (2):<br>"
         rf"\({c2}x + {d2}({a1}x {b1_str}) = {e2}\)<br>"
         rf"\({coeff_x}x {const_str} = {e2}\)<br>"
         rf"\({coeff_x}x = {e2 - const_term}\)<br>"
         rf"\(x = {x_ans}\)<br>"
         rf"Substitute into (1): \(y = {a1}\times{x_ans} {b1_str} = {y_ans}\)<br>"
         rf"<strong>\(x = {x_ans},\; y = {y_ans}\)</strong>")
    hint = "Substitute the expression for y into the second equation."
    return q, s, hint, 4, _eq_number_pair_answer(x_ans, y_ans, "x", "y", sep=",")


def _eq_inter_rearrange_two_step():
    q = r"Make \(t\) the subject of \(s = \dfrac{1}{2}at^2\)."
    s = (r"Multiply both sides by 2: \(2s = at^2\)<br>"
         r"Divide both sides by \(a\): \(t^2 = \dfrac{2s}{a}\)<br>"
         r"Square root both sides: "
         r"<strong>\(t = \sqrt{\dfrac{2s}{a}}\)</strong>")
    hint = "Isolate t² first, then take the square root."
    return q, s, hint, 3, _eq_algebraic_answer(
        _eq_subj_formula('t', _eq_subj_sqrt('2s/a')),
        subject='t',
        format_hint='Enter the expression after t =, e.g. √(2s/a)',
    )


def _eq_inter_word_perimeter():
    ans = random.randint(4, 12)
    # Rectangle: l = 2w + k, perimeter = 2(l + w) = P
    k = random.randint(2, 5)
    l = 2 * ans + k
    w = ans
    P = 2 * (l + w)
    q = (rf"A rectangle has length \({2}\text{{w}} + {k}\) and width \(\text{{w}}\). "
         rf"Its perimeter is {P} cm. Find \(w\).")
    s = (rf"Perimeter = \(2(\text{{length}} + \text{{width}})\):<br>"
         rf"\({P} = 2((2w + {k}) + w)\)<br>"
         rf"\({P} = 2(3w + {k})\)<br>"
         rf"\({P} = 6w + {2*k}\)<br>"
         rf"\(6w = {P - 2*k}\)<br>"
         rf"<strong>\(w = {ans}\) cm</strong>")
    hint = "Write an expression for the perimeter in terms of w, set it equal to the given perimeter."
    return q, s, hint, 4, _eq_linear_answer(ans, "w")


def _eq_inter_compound_ineq():
    lo_ans = random.randint(-2, 2)
    hi_ans = lo_ans + random.randint(3, 6)
    a = random.randint(2, 4)
    b = random.randint(1, 5)
    # a*lo_ans + b < a*x + b ≤ a*hi_ans + b
    c = a * lo_ans + b
    d = a * hi_ans + b
    q = rf"Solve \({c} \lt {a}x + {b} \leq {d}\)."
    s = (rf"Subtract {b} from all three parts:<br>"
         rf"\({c - b} \lt {a}x \leq {d - b}\)<br>"
         rf"Divide all three parts by {a}:<br>"
         rf"<strong>\({lo_ans} \lt x \leq {hi_ans}\)</strong>")
    hint = "Work on all three parts simultaneously — subtract then divide."
    return q, s, hint, 3, _eq_compound_inequality_answer('x', '<', lo_ans, '<=', hi_ans)


def _eq_inter_neg_ineq_flip():
    ans = random.randint(-5, -1)
    a = random.randint(2, 4)
    b = random.randint(1, 8)
    # -a*x + b > c, ans = (b-c)/a  → c = b - a*ans
    c = b - a * ans
    sym = random.choice([r"\gt", r"\geq"])
    flip = r"\lt" if sym == r"\gt" else r"\leq"
    sign = _eq_latex_sign_to_canonical(flip)
    q = rf"Solve \(-{a}x + {b} {sym} {c}\)."
    s = (rf"Subtract {b} from both sides: \(-{a}x {sym} {c - b}\)<br>"
         rf"Divide both sides by \(-{a}\) — <strong>flip the inequality sign</strong>!<br>"
         rf"<strong>\(x {flip} {ans}\)</strong>")
    hint = "When you divide by a negative number the inequality sign reverses."
    return q, s, hint, 3, _eq_linear_inequality_answer(ans, sign)


def _eq_inter_frac_eq():
    ans = random.randint(2, 8)
    a = random.randint(2, 5)
    b = random.randint(1, 6)
    # (x + b)/a = ans  → x = a*ans - b
    rhs = ans
    lhs_num = a * ans - b
    q = rf"Solve \(\dfrac{{x + {b}}}{{{a}}} = {rhs}\)."
    s = (rf"Multiply both sides by {a}:<br>"
         rf"\(x + {b} = {a * rhs}\)<br>"
         rf"Subtract {b}:<br>"
         rf"<strong>\(x = {lhs_num}\)</strong>")
    hint = f"Multiply both sides by {a} to clear the fraction."
    return q, s, hint, 2, _eq_linear_answer(lhs_num)


def _eq_inter_angle_equation():
    # Angles in a triangle: ax + b + cx + d + ex + f = 180
    x_ans = random.randint(5, 20)
    a, c, e = random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)
    b = random.randint(5, 30)
    d = random.randint(5, 30)
    f_val = 180 - (a + c + e) * x_ans - b - d
    if f_val < 5:
        f_val += 10
        b, d = b - 5, d - 5
    total_coeff = a + c + e
    total_const = b + d + f_val
    q = (rf"The angles in a triangle are \({a}x + {b}\)°, \({c}x + {d}\)°, "
         rf"and \({e}x + {f_val}\)°.<br>Form an equation and find \(x\).")
    s = (rf"Angles in a triangle sum to 180°:<br>"
         rf"\(({a}x + {b}) + ({c}x + {d}) + ({e}x + {f_val}) = 180\)<br>"
         rf"\({total_coeff}x + {total_const} = 180\)<br>"
         rf"\({total_coeff}x = {180 - total_const}\)<br>"
         rf"<strong>\(x = {x_ans}\)</strong>")
    hint = "Sum the three angles and set equal to 180°."
    return q, s, hint, 4, _eq_linear_answer(x_ans)


def _eq_inter_consec_integers():
    n = random.randint(5, 15)
    # n + (n+1) + (n+2) = 3n + 3 = sum
    total = 3 * n + 3
    q = rf"The sum of three consecutive integers is {total}. Find the integers."
    s = (rf"Let the smallest integer be \(n\).<br>"
         rf"\(n + (n+1) + (n+2) = {total}\)<br>"
         rf"\(3n + 3 = {total}\)<br>"
         rf"\(3n = {total - 3}\)<br>"
         rf"\(n = {n}\)<br>"
         rf"<strong>The integers are {n}, {n+1}, {n+2}.</strong>")
    hint = "Let the three integers be n, n+1, n+2 and form an equation."
    return q, s, hint, 3, _eq_number_list_answer([n, n + 1, n + 2])


def _eq_inter_ratio_equation():
    # Two quantities in ratio a:b, total = T
    a = random.randint(2, 5)
    b = random.randint(1, 4)
    k = random.randint(3, 8)
    total = (a + b) * k
    q = (rf"Two numbers are in the ratio \({a}:{b}\). Their sum is {total}. "
         rf"Find both numbers.")
    s = (rf"Let the two numbers be \({a}k\) and \({b}k\).<br>"
         rf"\({a}k + {b}k = {total}\)<br>"
         rf"\({a+b}k = {total}\)<br>"
         rf"\(k = {k}\)<br>"
         rf"<strong>The numbers are \({a*k}\) and \({b*k}\).</strong>")
    hint = f"Let the parts be {a}k and {b}k, then their sum = {total}."
    return q, s, hint, 3, _eq_number_pair_answer(a * k, b * k, "First number", "Second number")


def _eq_inter_rearrange_sqrt():
    q = r"Make \(r\) the subject of \(A = \pi r^2\)."
    s = (r"Divide both sides by \(\pi\): \(r^2 = \dfrac{A}{\pi}\)<br>"
         r"Square root both sides: "
         r"<strong>\(r = \sqrt{\dfrac{A}{\pi}}\)</strong>")
    hint = "Divide by π first, then square root."
    return q, s, hint, 3, _eq_algebraic_answer(
        _eq_subj_formula('r', _eq_subj_sqrt('a/π')),
        subject='r',
        format_hint='Enter the expression after r =, e.g. √(A/π)',
    )


def _eq_inter_word_both_sides():
    # "Two friends: Alice has 3x+5 sweets, Bob has 5x-3. They have the same."
    ans = random.randint(3, 8)
    a_coeff = random.randint(2, 5)
    a_const = random.randint(2, 10)
    b_coeff = a_coeff + random.randint(1, 3)
    b_const = b_coeff * ans - a_coeff * ans + a_const
    q = (rf"Alice has \({a_coeff}x + {a_const}\) stickers and Bob has "
         rf"\({b_coeff}x - {b_const}\) stickers. They have the same number. "
         rf"Find \(x\) and the number of stickers each person has.")
    n_stickers = a_coeff * ans + a_const
    s = (rf"Set the expressions equal:<br>"
         rf"\({a_coeff}x + {a_const} = {b_coeff}x - {b_const}\)<br>"
         rf"\({a_const} + {b_const} = {b_coeff}x - {a_coeff}x\)<br>"
         rf"\({a_const + b_const} = {b_coeff - a_coeff}x\)<br>"
         rf"\(x = {ans}\)<br>"
         rf"Stickers each: \({a_coeff}\times{ans} + {a_const} = {n_stickers}\)<br>"
         rf"<strong>\(x = {ans}\); each person has {n_stickers} stickers.</strong>")
    hint = "Set the two expressions equal to each other."
    return q, s, hint, 4, _eq_number_pair_answer(ans, n_stickers, "x", "Number of stickers", sep=",")


def _eq_inter_ineq_on_number_line():
    lo = random.randint(-3, 1)
    hi = lo + random.randint(3, 5)
    sym_lo = random.choice([r"\lt", r"\leq"])
    sym_hi = random.choice([r"\lt", r"\leq"])
    left_sign = _eq_latex_sign_to_canonical(sym_lo)
    right_sign = _eq_latex_sign_to_canonical(sym_hi)
    q = (rf"Show \({lo} {sym_lo} x {sym_hi} {hi}\) on the number line below. "
         rf"Drag the endpoints and click each circle to make it open or closed.")
    s = (rf"The solution is all values from {lo} to {hi}.<br>"
         rf"At \(x = {lo}\): {'included (filled circle)' if sym_lo == r'\leq' else 'not included (open circle)'}.<br>"
         rf"At \(x = {hi}\): {'included (filled circle)' if sym_hi == r'\leq' else 'not included (open circle)'}.<br>"
         rf"<strong>Draw a line from {lo} to {hi} with the appropriate circles at each end.</strong>")
    hint = "'<' means open circle (not included); '≤' means filled circle (included)."
    return (
        q, s, hint, 3,
        _eq_number_line_answer('x', left_sign, lo, right_sign, hi),
    )


def _eq_inter_rearrange_two_step_numeric_var():
    """Make t the subject of s = (num/den)at² with random coefficients."""
    num = random.randint(1, 3)
    den = random.choice([2, 4])
    a = random.randint(2, 6)
    q = rf"Make \(t\) the subject of \(s = \dfrac{{{num}}}{{{den}}}{a}t^2\)."
    s = (rf"Multiply both sides by {den}: \(s \times {den} = {num}{a}t^2\)<br>"
         rf"Divide both sides by {num * a}: "
         rf"\(t^2 = \dfrac{{{den}s}}{{{num * a}}}\)<br>"
         rf"Square root: "
         rf"<strong>\(t = \sqrt{{\dfrac{{{den}s}}{{{num * a}}}}}\)</strong>")
    hint = "Clear the fraction, isolate t², then square root."
    return q, s, hint, 3, _eq_algebraic_answer(
        _eq_subj_formula('t', _eq_subj_sqrt(f'{den}s/{num * a}')),
        subject='t',
        format_hint=f'Enter the expression after t =, e.g. √({den}s/{num * a})',
    )


def _eq_inter_simult_elimination_general_var():
    """Simultaneous equations with random coefficients (elimination required)."""
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
    q = (rf"Solve the simultaneous equations:<br>"
         rf"\({a1}x + {b1}y = {c1}\) &nbsp;&nbsp;(1)<br>"
         rf"\({a2}x + {b2}y = {c2}\) &nbsp;&nbsp;(2)")
    s = (rf"Multiply (1) by {b2}: \({a1 * b2}x + {b1 * b2}y = {c1 * b2}\) &nbsp;&nbsp;(3)<br>"
         rf"Multiply (2) by {b1}: \({a2 * b1}x + {b2 * b1}y = {c2 * b1}\) &nbsp;&nbsp;(4)<br>"
         rf"Subtract (4) from (3): \({a1 * b2 - a2 * b1}x = {c1 * b2 - c2 * b1}\)<br>"
         rf"\(x = {x_ans}\)<br>"
         rf"Substitute into (1): \({a1}({x_ans}) + {b1}y = {c1}\)<br>"
         rf"\({b1}y = {c1 - a1 * x_ans}\)<br>"
         rf"<strong>\(x = {x_ans},\; y = {y_ans}\)</strong>")
    hint = "Match the y-coefficients by multiplying one or both equations, then subtract."
    return q, s, hint, 4, _eq_number_pair_answer(x_ans, y_ans, "x", "y", sep=",")


def _eq_inter_savings_inequality_var():
    """Word problem: weeks needed to reach a savings target."""
    weekly = random.randint(8, 25)
    already = random.randint(10, 60)
    target = already + weekly * random.randint(4, 10)
    weeks_needed = (target - already + weekly - 1) // weekly
    q = (rf"Mia has saved £{already}. She saves £{weekly} each week. "
         rf"Write and solve an inequality to find how many more weeks \(w\) she needs "
         rf"to have at least £{target}.")
    s = (rf"After \(w\) more weeks she will have \( {already} + {weekly}w \) pounds.<br>"
         rf"Need \( {already} + {weekly}w \geq {target} \)<br>"
         rf"Subtract {already}: \( {weekly}w \geq {target - already} \)<br>"
         rf"Divide by {weekly}: "
         rf"<strong>\(w \geq {weeks_needed}\)</strong> (at least {weeks_needed} more weeks)")
    hint = "Form an expression for total savings, then use ≥ for 'at least'."
    return q, s, hint, 3, _eq_linear_inequality_answer(weeks_needed, '>=', 'w')


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (20 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _eq_diff_quadratic_factorise():
    r1 = random.randint(-6, -1)
    r2 = random.randint(1, 6)
    # (x - r1)(x - r2) = x² - (r1+r2)x + r1*r2
    b = -(r1 + r2)
    c = r1 * r2
    poly = _eq_fmt_quad_poly(b, c)
    q = rf"Solve \(x^2{poly} = 0\) by factorising."
    s = (rf"Find two numbers that multiply to {c} and add to {b}: "
         rf"these are {-r1} and {-r2}.<br>"
         rf"Factorise: \({_eq_fmt_factor_bracket(r1)}{_eq_fmt_factor_bracket(r2)} = 0\)<br>"
         rf"So \(x = {r1}\) or \(x = {r2}\)<br>"
         rf"<strong>\(x = {r1}\) or \(x = {r2}\)</strong>")
    hint = "Find two numbers that multiply to the constant and add to the x-coefficient."
    return q, s, hint, 3, _eq_quadratic_roots_answer(r1, r2)


def _eq_diff_quadratic_formula():
    # Choose a, b, c with real roots and discriminant a perfect square for clean answers
    pairs = [
        (1, -5, 6, 3, 2), (1, -7, 12, 4, 3), (2, -7, 3, 3, 0.5),
        (1, 2, -8, 2, -4), (1, -1, -6, 3, -2), (3, -10, 3, 3, 1/3),
    ]
    a_v, b_v, c_v, r1, r2 = random.choice(pairs)
    poly = _eq_fmt_quad_poly(b_v, c_v)
    a_str = "" if a_v == 1 else str(a_v)
    disc = b_v * b_v - 4 * a_v * c_v
    sqrt_disc = int(math.isqrt(disc))
    q = rf"Use the quadratic formula to solve \({a_str}x^2{poly} = 0\) Give exact answers."
    s = (rf"Using \(x = \dfrac{{-b \pm \sqrt{{b^2 - 4ac}}}}{{2a}}\) with \(a={a_v}, b={b_v}, c={c_v}\):<br>"
         rf"\(\Delta = ({b_v})^2 - 4({a_v})({c_v}) = {b_v*b_v} - {4*a_v*c_v} = {disc}\)<br>"
         rf"\(\sqrt{{\Delta}} = {sqrt_disc}\)<br>"
         rf"\(x = \dfrac{{{-b_v} \pm {sqrt_disc}}}{{{2*a_v}}}\)<br>"
         rf"<strong>\(x = {r1}\) or \(x = {r2}\)</strong>")
    hint = "Identify a, b, c then substitute into the formula. Simplify the discriminant first."
    return q, s, hint, 4, _eq_quadratic_roots_answer(r1, r2)


def _eq_diff_complete_square():
    p = random.randint(1, 5)
    q_val = random.choice([-9, -8, -7, -5, -4, -3, 7, 8, 11])
    # x² + 2px + q_val = (x+p)² - p² + q_val
    k = q_val - p * p
    k_str = f"- {-k}" if k < 0 else f"+ {k}"
    q_str_k = f"- {-k}" if k < 0 else f"+ {k}"
    q = rf"Complete the square for \(x^2 + {2*p}x + {q_val}\)."
    s = (rf"Write as \((x + {p})^2 - {p}^2 + {q_val}\)<br>"
         rf"\(= (x + {p})^2 - {p*p} + {q_val}\)<br>"
         rf"<strong>\(= (x + {p})^2 {q_str_k}\)</strong>")
    hint = f"Half the x-coefficient is {p}. Write (x + {p})² and then adjust the constant."
    return q, s, hint, 3, _eq_completed_square_answer('plus', p, k)


def _eq_diff_simult_non_integer():
    # ax + by = c; dx + ey = f — multiply to eliminate, fractional answer OK
    x_ans_n, x_ans_d = random.choice([(3, 2), (5, 2), (7, 3), (4, 3)])
    y_ans_n, y_ans_d = random.choice([(1, 2), (2, 3), (5, 4)])
    a, b = 2, 3
    c1_n = a * x_ans_n * y_ans_d + b * y_ans_n * x_ans_d
    c1_d = x_ans_d * y_ans_d
    from math import gcd
    g = gcd(c1_n, c1_d)
    c1_n, c1_d = c1_n // g, c1_d // g
    # fallback to a simpler fixed pair
    q = (r"Solve the simultaneous equations:<br>"
         r"\(2x + 3y = 8\) &nbsp;&nbsp;(1)<br>"
         r"\(5x - y = 3\) &nbsp;&nbsp;(2)")
    s = (r"Multiply (2) by 3: \(15x - 3y = 9\) &nbsp;&nbsp;(3)<br>"
         r"Add (1) and (3): \(17x = 17\)<br>"
         r"\(x = 1\)<br>"
         r"Substitute into (2): \(5(1) - y = 3 \Rightarrow y = 2\)<br>"
         r"<strong>\(x = 1,\; y = 2\)</strong>")
    hint = "Multiply one equation so that a coefficient matches, then add or subtract."
    return q, s, hint, 4, _eq_number_pair_answer(1, 2, "x", "y", sep=",")


def _eq_diff_quadratic_from_geometry():
    # Rectangle: (x + a) wide, (x + b) long, area = A
    a = random.randint(1, 4)
    b = random.randint(1, 4)
    x_ans = random.randint(2, 6)
    area = (x_ans + a) * (x_ans + b)
    b_coef = a + b
    c_coef = a * b - area
    c_part = _eq_fmt_quad_poly(0, c_coef)  # constant term only
    q = (rf"A rectangle has sides \((x + {a})\) cm and \((x + {b})\) cm. "
         rf"Its area is {area} cm². Form a quadratic equation and solve for \(x\).")
    s = (rf"Area = \((x + {a})(x + {b}) = {area}\)<br>"
         rf"Expand: \(x^2 + {b_coef}x + {a*b} = {area}\)<br>"
         rf"Rearrange: \(x^2 + {b_coef}x{c_part} = 0\)<br>"
         rf"Factorise: \((x + {x_ans + b_coef - x_ans})(x - {x_ans}) = 0\)"
         rf" — test: the positive root is valid.<br>"
         rf"<strong>\(x = {x_ans}\) cm</strong> (taking the positive value since \(x\) is a length)")
    hint = "Set up (x+a)(x+b) = area, expand, rearrange to 0, then factorise."
    return q, s, hint, 5, _eq_linear_answer(x_ans)


def _eq_diff_rearrange_complex():
    q = r"Make \(v\) the subject of \(E = \dfrac{1}{2}mv^2\)."
    s = (r"Multiply both sides by 2: \(2E = mv^2\)<br>"
         r"Divide both sides by \(m\): \(v^2 = \dfrac{2E}{m}\)<br>"
         r"Square root: "
         r"<strong>\(v = \sqrt{\dfrac{2E}{m}}\)</strong>")
    hint = "Isolate v² first, then square root."
    return q, s, hint, 3, _eq_algebraic_answer(
        _eq_subj_formula('v', _eq_subj_sqrt('2e/m')),
        subject='v',
        format_hint='Enter the expression after v =, e.g. √(2E/m)',
    )


def _eq_diff_quadratic_ineq():
    r1, r2 = sorted(random.sample(range(-3, 5), 2))
    # (x - r1)(x - r2) < 0 → r1 < x < r2
    b = -(r1 + r2)
    c = r1 * r2
    poly = _eq_fmt_quad_poly(b, c)
    factors = _eq_fmt_factor_bracket(r1) + _eq_fmt_factor_bracket(r2)
    q = rf"Solve the inequality \(x^2{poly} \lt 0\)"
    s = (rf"Factorise the quadratic: \({factors} \lt 0\)<br>"
         rf"The parabola opens upward and crosses the \(x\)-axis at \(x = {r1}\) and \(x = {r2}\).<br>"
         rf"The expression is negative <em>between</em> the roots:<br>"
         rf"<strong>\({r1} \lt x \lt {r2}\)</strong>")
    hint = "Factorise, sketch the parabola (opens up), then identify where it is below the x-axis."
    return q, s, hint, 4, _eq_compound_inequality_answer('x', '<', r1, '<', r2)


def _eq_diff_fractional_eq():
    ans = random.randint(2, 6)
    a = random.randint(1, 4)
    b = random.randint(1, 4)
    while a == b:
        b = random.randint(1, 4)
    # a/(x-a) + b/(x-b) = ... build from known answer
    # Use simple form: (x+a)/(x-1) = b+2, solve
    # Keep it clean: x/a + x/b = c
    lcm_ab = (a * b) // math.gcd(a, b)
    # x/a + x/b = x(a+b)/(ab) = ans → x = ans*ab/(a+b)
    if (ans * lcm_ab) % (a + b) != 0:
        ans = a + b
    x_val = ans * a * b // ((a + b))
    # fallback clean version
    q = rf"Solve \(\dfrac{{x}}{{{a}}} + \dfrac{{x}}{{{b}}} = {ans}\)."
    s = (rf"Multiply every term by \({a*b}\) (the LCM of {a} and {b}):<br>"
         rf"\({b}x + {a}x = {ans * a * b}\)<br>"
         rf"\({a+b}x = {ans * a * b}\)<br>"
         rf"<strong>\(x = {ans * a * b // (a+b)}\)</strong>")
    hint = f"Multiply through by {a*b} to clear both fractions."
    return q, s, hint, 4, _eq_linear_answer(ans * a * b // (a + b))


def _eq_diff_disguised_quadratic():
    """Biquadratic x⁴ + bx² + c = 0 with random perfect-square roots."""
    s1, s2 = sorted(random.sample(range(1, 7), 2))
    ua, ub = s1 * s1, s2 * s2
    b_u = -(ua + ub)
    c_u = ua * ub
    b_str = f"+ {b_u}" if b_u >= 0 else f"- {abs(b_u)}"
    c_str = f"+ {c_u}" if c_u >= 0 else f"- {abs(c_u)}"
    q = rf"Solve \(x^4 {b_str}x^2 {c_str} = 0\)."
    s = (rf"Let \(u = x^2\). Then \(u^2 {b_str}u {c_str} = 0\)<br>"
         rf"Factorise: \((u - {ua})(u - {ub}) = 0\)<br>"
         rf"So \(u = {ua}\) or \(u = {ub}\), i.e. \(x^2 = {ua}\) or \(x^2 = {ub}\)<br>"
         rf"<strong>\(x = \pm {s1}\) or \(x = \pm {s2}\)</strong>")
    hint = "Let u = x² to get a quadratic in u, solve for u, then take square roots."
    return q, s, hint, 5, _eq_quadratic_roots_answer(
        -s2, -s1, s1, s2,
        format_hint='Enter all four roots separated by commas (e.g. 1, -1, 2, -2)',
    )


def _eq_diff_simult_one_quadratic():
    """Simultaneous y = x² and y = ax + b with random integer intersection points."""
    r1 = random.randint(-4, -1)
    r2 = random.randint(2, 6)
    while r1 + r2 == 0:
        r2 = random.randint(2, 6)
    a = r1 + r2
    b = -r1 * r2
    b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    c_rearr = f"- {b}" if b >= 0 else f"+ {abs(b)}"
    if a == 1:
        linear = rf"\(y = x {b_str}\)"
    else:
        linear = rf"\(y = {a}x {b_str}\)"
    y1, y2 = r1 * r1, r2 * r2
    q = (rf"Solve the simultaneous equations:<br>"
         rf"\(y = x^2\)<br>"
         rf"{linear}")
    factors = _eq_fmt_factor_bracket(r1) + _eq_fmt_factor_bracket(r2)
    x_term = "x" if a == 1 else f"{a}x"
    s = (rf"Substitute the linear equation into \(y = x^2\):<br>"
         rf"\(x^2 = {x_term} {b_str}\)<br>"
         rf"Rearrange: \(x^2 - {x_term} {c_rearr} = 0\)<br>"
         rf"Factorise: \({factors} = 0\)<br>"
         rf"\(x = {r1}\) or \(x = {r2}\)<br>"
         rf"When \(x = {r1}\): \(y = {y1}\). When \(x = {r2}\): \(y = {y2}\)<br>"
         rf"<strong>Solutions: \(({r1},\, {y1})\) and \(({r2},\, {y2})\)</strong>")
    hint = "Substitute the linear equation into the quadratic, then factorise."
    return q, s, hint, 5, _eq_coord_pairs_answer(r1, y1, r2, y2)


def _eq_diff_subject_appears_twice():
    q = r"Make \(x\) the subject of \(ax + b = cx + d\)."
    s = (r"Collect \(x\)-terms on one side:<br>"
         r"\(ax - cx = d - b\)<br>"
         r"Factorise: \(x(a - c) = d - b\)<br>"
         r"Divide by \((a - c)\):<br>"
         r"<strong>\(x = \dfrac{d - b}{a - c}\)</strong>")
    hint = "Collect all x-terms on one side, factorise x out, then divide."
    return q, s, hint, 4, _eq_formula_fraction_answer('d-b', 'a-c', 'x')


def _eq_diff_prove_identity():
    q = r"Show that \((x + 3)^2 - (x - 3)^2 \equiv 12x\)."
    s = (r"Expand \((x+3)^2 = x^2 + 6x + 9\)<br>"
         r"Expand \((x-3)^2 = x^2 - 6x + 9\)<br>"
         r"Subtract: \((x^2 + 6x + 9) - (x^2 - 6x + 9)\)<br>"
         r"\(= x^2 + 6x + 9 - x^2 + 6x - 9\)<br>"
         r"\(= 12x\)<br>"
         r"<strong>LHS = \(12x\) = RHS ✓</strong>")
    hint = "Expand each bracket fully, then subtract and simplify."
    return q, s, hint, 4


def _eq_diff_complete_square_solve():
    p = random.randint(1, 4)
    k = random.choice([7, 11, 12, 20, 23])
    # x² + 2px = k → (x+p)² = k + p²
    rhs = k + p * p
    q = rf"Solve \(x^2 + {2*p}x - {k} = 0\) by completing the square. Give answers to 2 d.p."
    s = (rf"Rearrange: \(x^2 + {2*p}x = {k}\)<br>"
         rf"Complete the square: \((x + {p})^2 = {k} + {p}^2 = {rhs}\)<br>"
         rf"\(x + {p} = \pm\sqrt{{{rhs}}}\)<br>"
         rf"<strong>\(x = {-p} + \sqrt{{{rhs}}} \approx {-p + math.sqrt(rhs):.2f}\) "
         rf"or \(x = {-p} - \sqrt{{{rhs}}} \approx {-p - math.sqrt(rhs):.2f}\)</strong>")
    hint = f"Add {p}² = {p*p} to both sides after moving the constant."
    return q, s, hint, 4, _eq_quadratic_roots_answer(round(-p + math.sqrt(rhs), 2), round(-p - math.sqrt(rhs), 2))


def _eq_diff_rearrange_fraction():
    """Make x the subject of (x + p)/(x − q) = k with random numerical coefficients."""
    p = random.randint(1, 6)
    q_val = random.randint(2, 7)
    k = random.randint(2, 5)
    rhs_const = k * q_val
    lhs_const = -rhs_const - p
    num = k * q_val + p
    den = k - 1
    q = rf"Make \(x\) the subject of \(\dfrac{{x + {p}}}{{x - {q_val}}} = {k}\)."
    if num % den == 0:
        ans = num // den
        ans_str = rf"<strong>\(x = {ans}\)</strong>"
    else:
        ans_str = rf"<strong>\(x = \dfrac{{{num}}}{{{den}}}\)</strong>"
    s = (rf"Multiply both sides by \((x - {q_val})\): \(x + {p} = {k}(x - {q_val})\)<br>"
         rf"Expand: \(x + {p} = {k}x - {rhs_const}\)<br>"
         rf"Collect \(x\)-terms: \(x - {k}x = -{rhs_const} - {p}\)<br>"
         rf"Factorise: \((1 - {k})x = {lhs_const}\)<br>"
         rf"Divide: {ans_str}")
    hint = "Multiply through by the denominator, expand, then collect terms in x."
    if num % den == 0:
        raw = _eq_linear_answer(num // den)
    else:
        raw = _eq_linear_answer(f"{num}/{den}")
    return q, s, hint, 4, raw


def _eq_diff_quadratic_from_consecutive():
    # n(n+2) = k → n² + 2n - k = 0
    n = random.randint(4, 10)
    k = n * (n + 2)
    q = (rf"The product of two consecutive even integers is {k}. "
         rf"Form a quadratic equation and find the integers.")
    s = (rf"Let the integers be \(n\) and \(n+2\).<br>"
         rf"\(n(n+2) = {k}\)<br>"
         rf"\(n^2 + 2n - {k} = 0\)<br>"
         rf"Factorise: \((n - {n})(n + {n+2}) = 0\)<br>"
         rf"\(n = {n}\) (taking the positive value)<br>"
         rf"<strong>The integers are {n} and {n+2}.</strong>")
    hint = "Let the integers be n and n+2, multiply, rearrange to 0, then factorise."
    return q, s, hint, 4, _eq_number_pair_answer(n, n + 2, "First integer", "Second integer")


def _eq_diff_rearrange_kinetic_var():
    """Rearrange kinetic energy with a random mass value."""
    m = random.randint(2, 12)
    q = (rf"A body of mass {m} kg has kinetic energy \(E\) (in joules) given by "
         rf"\(E = \dfrac{{1}}{{2}} \times {m} \times v^2\), where \(v\) is speed in m/s. "
         rf"Rearrange the formula to make \(v\) the subject.")
    s = (rf"Multiply both sides by 2: \(2E = {m}v^2\)<br>"
         rf"Divide both sides by {m}: \(v^2 = \dfrac{{2E}}{{{m}}}\)<br>"
         rf"Square root: <strong>\(v = \sqrt{{\dfrac{{2E}}{{{m}}}}}\)</strong>")
    hint = "Isolate v² first (multiply by 2, divide by mass), then take the square root."
    return q, s, hint, 3, _eq_algebraic_answer(
        _eq_subj_formula('v', _eq_subj_sqrt(f'2e/{m}')),
        subject='v',
        format_hint=f'Enter the expression after v =, e.g. √(2E/{m})',
    )


def _eq_diff_quadratic_formula_generated():
    """Quadratic formula with coefficients built from random integer roots."""
    r1 = random.randint(-6, -1)
    r2 = random.randint(2, 9)
    b = -(r1 + r2)
    c = r1 * r2
    poly = _eq_fmt_quad_poly(b, c)
    disc = b * b - 4 * c
    sqrt_disc = int(math.isqrt(disc))
    q = rf"Use the quadratic formula to solve \(x^2{poly} = 0\). Give exact answers."
    s = (rf"Here \(a = 1\), \(b = {b}\), \(c = {c}\).<br>"
         rf"\(\Delta = b^2 - 4ac = ({b})^2 - 4(1)({c}) = {disc}\)<br>"
         rf"\(\sqrt{{\Delta}} = {sqrt_disc}\)<br>"
         rf"\(x = \dfrac{{-{b} \pm {sqrt_disc}}}{{2}}\)<br>"
         rf"<strong>\(x = {r2}\) or \(x = {r1}\)</strong>")
    hint = "Identify a, b, c from the equation, evaluate the discriminant, then substitute."
    return q, s, hint, 4, _eq_quadratic_roots_answer(r1, r2)


def _eq_diff_simult_linear_pair_var():
    """Two linear simultaneous equations with fully random integer solutions."""
    x_ans = random.randint(2, 7)
    y_ans = random.randint(2, 7)
    a1, b1 = random.randint(2, 6), random.randint(2, 5)
    a2, b2 = random.randint(2, 6), random.randint(2, 5)
    attempts = 0
    while a1 * b2 == a2 * b1 and attempts < 20:
        a2, b2 = random.randint(2, 6), random.randint(2, 5)
        attempts += 1
    c1 = a1 * x_ans + b1 * y_ans
    c2 = a2 * x_ans + b2 * y_ans
    q = (rf"Solve the simultaneous equations:<br>"
         rf"\({a1}x + {b1}y = {c1}\) &nbsp;&nbsp;(1)<br>"
         rf"\({a2}x + {b2}y = {c2}\) &nbsp;&nbsp;(2)")
    s = (rf"Multiply (1) by {b2}: \({a1 * b2}x + {b1 * b2}y = {c1 * b2}\) &nbsp;&nbsp;(3)<br>"
         rf"Multiply (2) by {b1}: \({a2 * b1}x + {b2 * b1}y = {c2 * b1}\) &nbsp;&nbsp;(4)<br>"
         rf"Subtract (4) from (3): \({a1 * b2 - a2 * b1}x = {c1 * b2 - c2 * b1}\)<br>"
         rf"\(x = {x_ans}\)<br>"
         rf"Substitute into (1): \(y = {y_ans}\)<br>"
         rf"<strong>\(x = {x_ans},\; y = {y_ans}\)</strong>")
    hint = "Match the y-coefficients by multiplying, then subtract to eliminate y."
    return q, s, hint, 4, _eq_number_pair_answer(x_ans, y_ans, "x", "y", sep=",")


# ---------- DIFFICULT (multi-step, real-world, a/b/c) ----------

def _eq_diff_cafe_prices_multipart():
    """Café sales — simultaneous equations for drink prices."""
    coffee_p = random.randint(2, 4)
    tea_p = random.randint(2, 5)
    while tea_p == coffee_p:
        tea_p = random.randint(2, 5)
    n_c1, n_t1 = random.randint(10, 16), random.randint(6, 12)
    n_c2, n_t2 = random.randint(4, 9), random.randint(12, 18)
    total1 = n_c1 * coffee_p + n_t1 * tea_p
    total2 = n_c2 * coffee_p + n_t2 * tea_p
    coeff_c = n_c1 * n_t2 - n_c2 * n_t1
    rhs_c = total1 * n_t2 - total2 * n_t1
    intro = (
        f"A café sells coffee and tea. On Monday it sells {n_c1} coffees and {n_t1} teas "
        f"and takes <strong>£{total1}</strong>. On Tuesday it sells {n_c2} coffees and "
        f"{n_t2} teas and takes <strong>£{total2}</strong>. "
        r"Let c be the price of one coffee and t the price of one tea (in pounds)."
    )
    q = intro + _eq_abc_block(
        r"Write two equations for c and t using the information above.",
        r"Solve your equations to find the price of one coffee.",
        r"Hence find the price of one tea.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Monday: <strong>\({n_c1}c + {n_t1}t = {total1}\)</strong> &nbsp; (1); "
        rf"Tuesday: <strong>\({n_c2}c + {n_t2}t = {total2}\)</strong> &nbsp; (2)<br>"
        rf"<strong>b)</strong> Eliminate \(t\): multiply (1) by {n_t2}, (2) by {n_t1}, then subtract:<br>"
        rf"\({coeff_c}c = {rhs_c}\) \(\Rightarrow\) <strong>\(c = {coffee_p}\)</strong> pounds.<br>"
        rf"<strong>c)</strong> Substitute into (1): \({n_c1}({coffee_p}) + {n_t1}t = {total1}\)<br>"
        rf"\({n_t1}t = {total1 - n_c1 * coffee_p}\) \(\Rightarrow\) "
        rf"<strong>\(t = {tea_p}\)</strong> pounds."
    )
    hint = (
        r"Write one equation per day, then eliminate one unknown by multiplying "
        r"and subtracting the equations."
    )
    return q, s, hint, 5, _eq_number_fields_answer(
        (
            _eq_two_var_equation_raw('c', 't', n_c1, n_t1, total1),
            _eq_two_var_equation_raw('c', 't', n_c2, n_t2, total2),
            coffee_p,
            tea_p,
        ),
        (
            'Part (a): Monday equation',
            'Part (a): Tuesday equation',
            'Part (b): price of one coffee (£)',
            'Part (c): price of one tea (£)',
        ),
        ('two_var_equation', 'two_var_equation', 'number', 'number'),
    )


def _eq_diff_phone_plans_multipart():
    """Mobile phone plans — equation and inequality."""
    fixed_a = random.randint(12, 22)
    rate_a = random.randint(6, 12)
    fixed_b = fixed_a + random.randint(8, 18)
    rate_b = random.randint(3, rate_a - 1)
    m_equal = (fixed_b - fixed_a) * 100 // (rate_a - rate_b)
    intro = (
        f"Two mobile plans charge a fixed monthly fee plus a cost per minute of calls.<br>"
        f"<strong>Plan A:</strong> £{fixed_a} per month plus {rate_a}p per minute.<br>"
        f"<strong>Plan B:</strong> £{fixed_b} per month plus {rate_b}p per minute.<br>"
        r"Let m be the number of minutes used in a month."
    )
    q = intro + _eq_abc_block(
        r"Write expressions for the monthly cost of Plan A and Plan B in terms of m.",
        r"Find the number of minutes for which both plans cost the same amount.",
        r"Write an inequality for when Plan A is cheaper than Plan B.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Plan A: "
        rf"<strong>\(C_A = {fixed_a} + \dfrac{{{rate_a}m}}{{100}}\)</strong> (pounds); "
        rf"Plan B: <strong>\(C_B = {fixed_b} + \dfrac{{{rate_b}m}}{{100}}\)</strong>.<br>"
        rf"<strong>b)</strong> Set \(C_A = C_B\):<br>"
        rf"\({fixed_a} + \dfrac{{{rate_a}m}}{{100}} = {fixed_b} + \dfrac{{{rate_b}m}}{{100}}\)<br>"
        rf"\(\dfrac{{{rate_a - rate_b}m}}{{100}} = {fixed_b - fixed_a}\)<br>"
        rf"<strong>\(m = {m_equal}\)</strong> minutes.<br>"
        rf"<strong>c)</strong> Plan A is cheaper when \(C_A \lt C_B\): "
        rf"<strong>\(m \lt {m_equal}\)</strong> (under {m_equal} minutes per month)."
    )
    hint = (
        r"Convert pence to pounds in your expressions; equate costs for part (b); "
        r"for (c) compare the two expressions using <."
    )
    return q, s, hint, 5, _eq_number_fields_answer(
        (
            m_equal,
            f'm|<|{m_equal}',
        ),
        (
            'Part (b): minutes when both plans cost the same',
            'Part (c): Plan A cheaper when… (e.g. m < 40)',
        ),
        ('number', 'linear_inequality'),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (15 questions)
# ══════════════════════════════════════════════════════════════════════════════

_EQ_INEQ_MCQ_BANK = [
        {
            "q": r"What is the solution to \(3x + 5 = 14\)?",
            "opts": ["A  x = 2", "B  x = 3", "C  x = 19/3", "D  x = 4"],
            "ans": "B",
            "sol": r"Subtract 5: \(3x = 9\). Divide by 3: \(x = 3\).",
        },
        {
            "q": r"Which value satisfies \(2x - 7 \gt 3\)?",
            "opts": ["A  x = 4", "B  x = 5", "C  x = 6", "D  x = 3"],
            "ans": "C",
            "sol": r"Solve: \(2x \gt 10 \Rightarrow x \gt 5\). Only 6 is greater than 5.",
        },
        {
            "q": r"Solve \(5(x - 2) = 20\). What is \(x\)?",
            "opts": ["A  x = 2", "B  x = 4", "C  x = 6", "D  x = 8"],
            "ans": "C",
            "sol": r"Divide by 5: \(x - 2 = 4\). Add 2: \(x = 6\).",
        },
        {
            "q": r"The solution to \(4x + 3 = 2x + 11\) is:",
            "opts": ["A  x = 2", "B  x = 4", "C  x = 7", "D  x = 3"],
            "ans": "B",
            "sol": r"Subtract \(2x\): \(2x + 3 = 11\). Subtract 3: \(2x = 8\). So \(x = 4\).",
        },
        {
            "q": r"Which inequality is shown by an open circle at \(-1\) with an arrow pointing right?",
            "opts": [r"A  \(x \geq -1\)", r"B  \(x \gt -1\)", r"C  \(x \lt -1\)", r"D  \(x \leq -1\)"],
            "ans": "B",
            "sol": r"An open circle means the endpoint is not included, and the arrow points to values greater than \(-1\). So \(x \gt -1\).",
        },
        {
            "q": r"What are the solutions to \(x^2 - 5x + 6 = 0\)?",
            "opts": ["A  x = 1 or x = 6", "B  x = 2 or x = 3", "C  x = −2 or x = −3", "D  x = 5 or x = 1"],
            "ans": "B",
            "sol": r"Factorise: \((x-2)(x-3)=0\), so \(x=2\) or \(x=3\).",
        },
        {
            "q": r"Solve simultaneously: \(x + y = 7\) and \(x - y = 3\). What is \(x\)?",
            "opts": ["A  x = 2", "B  x = 5", "C  x = 4", "D  x = 3"],
            "ans": "B",
            "sol": r"Add the equations: \(2x = 10 \Rightarrow x = 5\).",
        },
        {
            "q": r"Which of these is equivalent to \((x+4)^2 - 16\)?",
            "opts": [r"A  \(x^2 + 8x\)", r"B  \(x^2 + 4x\)", r"C  \(x^2 + 8x + 32\)", r"D  \(x^2 + 16\)"],
            "ans": "A",
            "sol": r"\((x+4)^2 - 16 = x^2 + 8x + 16 - 16 = x^2 + 8x\).",
        },
        {
            "q": r"Make \(t\) the subject of \(s = ut + \frac{1}{2}at^2\) when \(u = 0\). Which is correct?",
            "opts": [
                r"A  \(t = \sqrt{\frac{2s}{a}}\)",
                r"B  \(t = \frac{2s}{a}\)",
                r"C  \(t = \frac{s}{a}\)",
                r"D  \(t = \sqrt{\frac{s}{2a}}\)",
            ],
            "ans": "A",
            "sol": r"With \(u=0\): \(s = \frac{1}{2}at^2 \Rightarrow t^2 = \frac{2s}{a} \Rightarrow t = \sqrt{\frac{2s}{a}}\).",
        },
        {
            "q": r"Solve \(-3x \geq 12\). Which answer is correct?",
            "opts": [r"A  \(x \geq -4\)", r"B  \(x \leq -4\)", r"C  \(x \leq 4\)", r"D  \(x \geq 4\)"],
            "ans": "B",
            "sol": r"Divide by \(-3\) and flip the sign: \(x \leq \frac{12}{-3} = -4\).",
        },
        {
            "q": r"The discriminant of \(2x^2 - 3x + 1 = 0\) is:",
            "opts": ["A  1", "B  17", "C  7", "D  −1"],
            "ans": "A",
            "sol": r"\(\Delta = b^2 - 4ac = 9 - 8 = 1\).",
        },
        {
            "q": r"Which pair satisfies \(2x + y = 9\) and \(x - y = 0\)?",
            "opts": ["A  (3, 3)", "B  (4, 1)", "C  (2, 5)", "D  (5, 4)"],
            "ans": "A",
            "sol": r"From eq 2: \(x = y\). Substitute: \(2x + x = 9 \Rightarrow 3x = 9 \Rightarrow x = 3\), \(y = 3\).",
        },
        {
            "q": r"The integer values satisfying \(-2 \leq x \lt 3\) are:",
            "opts": ["A  −2, −1, 0, 1, 2", "B  −1, 0, 1, 2, 3", "C  −2, −1, 0, 1, 2, 3", "D  0, 1, 2"],
            "ans": "A",
            "sol": r"\(x\) must be \(\geq -2\) (included) and \(\lt 3\) (excluded): −2, −1, 0, 1, 2.",
        },
        {
            "q": r"Which gives the solutions to \(x^2 + 2x - 8 = 0\)?",
            "opts": ["A  x = 2 or x = −4", "B  x = −2 or x = 4", "C  x = 4 or x = −4", "D  x = 1 or x = −8"],
            "ans": "A",
            "sol": r"Factorise: \((x+4)(x-2)=0\), so \(x=-4\) or \(x=2\).",
        },
        {
            "q": r"If \(3x - 1 \lt 2x + 4\), what is the range of \(x\)?",
            "opts": [r"A  \(x \lt 5\)", r"B  \(x \gt 5\)", r"C  \(x \lt 3\)", r"D  \(x \gt 3\)"],
            "ans": "A",
            "sol": r"Subtract \(2x\): \(x - 1 \lt 4\). Add 1: \(x \lt 5\).",
        },
]


def equations_inequalities_mcq():
    chosen = random.choice(_EQ_INEQ_MCQ_BANK)
    q = chosen["q"]
    options = chosen["opts"]
    correct = chosen["ans"]
    s = f"<strong>Answer: {correct}</strong><br><br>{chosen['sol']}"
    hint = chosen["sol"]
    return q, s, hint, 1, options, correct


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_equations_inequalities_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _EQ_INEQ_MCQ_BANK,
            procedural_mcq_for('equations_inequalities'),
            'equations_inequalities',
            difficulty,
        )

    if difficulty == 'foundational':
        pool = [
            _eq_found_one_step_add,
            _eq_found_one_step_multiply,
            _eq_found_two_step,
            _eq_found_substitute_formula,
            _eq_found_simple_inequality,
            _eq_found_double_inequality,
            _eq_found_ineq_solve_two_step,
            _eq_found_verify_solution,
            _eq_found_form_and_solve_words,
            _eq_found_brackets_simple,
            _eq_found_rearrange_one_step,
            _eq_found_fraction_eq,
            _eq_found_negative_answer,
            _eq_found_ineq_integer_list,
            _eq_found_write_ineq_from_words,
            _eq_found_rearrange_numeric_var,
            _eq_found_substitute_formula_var,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _eq_inter_both_sides,
            _eq_inter_expand_both_sides,
            _eq_inter_simult_elim,
            _eq_inter_simult_sub,
            _eq_inter_rearrange_two_step,
            _eq_inter_word_perimeter,
            _eq_inter_compound_ineq,
            _eq_inter_neg_ineq_flip,
            _eq_inter_frac_eq,
            _eq_inter_angle_equation,
            _eq_inter_consec_integers,
            _eq_inter_ratio_equation,
            _eq_inter_rearrange_sqrt,
            _eq_inter_word_both_sides,
            _eq_inter_ineq_on_number_line,
            _eq_inter_rearrange_two_step_numeric_var,
            _eq_inter_simult_elimination_general_var,
            _eq_inter_savings_inequality_var,
        ]
    elif difficulty == 'difficult':
        pool = [
            _eq_diff_quadratic_factorise,
            _eq_diff_quadratic_formula,
            _eq_diff_complete_square,
            _eq_diff_simult_non_integer,
            _eq_diff_quadratic_from_geometry,
            _eq_diff_rearrange_complex,
            _eq_diff_quadratic_ineq,
            _eq_diff_fractional_eq,
            _eq_diff_disguised_quadratic,
            _eq_diff_simult_one_quadratic,
            _eq_diff_subject_appears_twice,
            _eq_diff_prove_identity,
            _eq_diff_complete_square_solve,
            _eq_diff_rearrange_fraction,
            _eq_diff_quadratic_from_consecutive,
            _eq_diff_cafe_prices_multipart,
            _eq_diff_phone_plans_multipart,
            _eq_diff_rearrange_kinetic_var,
            _eq_diff_quadratic_formula_generated,
            _eq_diff_simult_linear_pair_var,
        ]
    else:  # mixed
        found = random.sample([
            _eq_found_one_step_add, _eq_found_one_step_multiply, _eq_found_two_step,
            _eq_found_simple_inequality, _eq_found_brackets_simple,
            _eq_found_form_and_solve_words, _eq_found_fraction_eq,
        ], 4)
        inter = random.sample([
            _eq_inter_both_sides, _eq_inter_simult_elim, _eq_inter_simult_sub,
            _eq_inter_word_perimeter, _eq_inter_neg_ineq_flip, _eq_inter_consec_integers,
        ], 4)
        diff = random.sample([
            _eq_diff_quadratic_factorise, _eq_diff_quadratic_formula,
            _eq_diff_simult_one_quadratic, _eq_diff_quadratic_ineq,
        ], 2)
        return found + inter + diff

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors exactly)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_equations_inequalities(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_equations_inequalities_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'equations_inequalities',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_equations_inequalities_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    return _eq_problem_from_output(variant(), difficulty)
