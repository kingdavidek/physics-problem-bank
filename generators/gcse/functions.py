"""
GCSE Maths – Functions
7 foundational · 5 intermediate · 5 difficult · 8 MCQ (randomised each time)
Graded practice variants return (question, solution, hint, marks, raw).
Inverse/composite-rule algebra and multipart variants stay as 4-tuples.
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_pool,
    run_mcq_variant,
    pick_named_variant,
)


def _fmt_b(b):
    if b > 0:
        return f"+ {b}"
    if b < 0:
        return f"- {abs(b)}"
    return ""


def _linear(m, c):
    if m == 1:
        body = "x"
    elif m == -1:
        body = "-x"
    else:
        body = f"{m}x"
    return rf"{body} {_fmt_b(c)}".strip()


def _x_term(b):
    """Coefficient of x in x² + bx + c."""
    if b == 0:
        return ""
    if b == 1:
        return "+ x"
    if b == -1:
        return "- x"
    if b > 0:
        return f"+ {b}x"
    return f"- {abs(b)}x"


def _quadratic_rule(b, c):
    return rf"x^2 {_x_term(b)} {_fmt_b(c)}".strip()


def _sub_num(n):
    return f"({n})" if n < 0 else str(n)


def _three_numeric_distractors(correct, candidates):
    wrong = []
    for value in candidates:
        value = str(value)
        if value != correct and value not in wrong:
            wrong.append(value)
        if len(wrong) == 3:
            return wrong

    base = int(correct)
    offset = 1
    while len(wrong) < 3:
        for value in (base + offset, base - offset):
            value = str(value)
            if value != correct and value not in wrong:
                wrong.append(value)
            if len(wrong) == 3:
                break
        offset += 1
    return wrong


def _fn_raw(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:g}"
    return str(value)


def _fn_quadratic_roots_answer(*roots):
    return {'type': 'quadratic_roots', 'roots': tuple(_fn_raw(r) for r in roots)}


def _fn_linear_answer(value, var='x'):
    return {'type': 'linear', 'value': _fn_raw(value), 'var': str(var).strip().lower()}


def _fn_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_fn_raw(v) for v in values),
        'labels': tuple(labels),
    }


def _fn_linear_raw(raw):
    var = raw.get('var') or 'x'
    val = raw.get('value')
    if var == 'x':
        return str(val)
    return f'{var}={val}'


def _fn_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'quadratic_roots':
                roots = raw.get('roots') or ()
                extra = {
                    'correct_answer_raw': ','.join(str(r) for r in roots),
                    'answer_type': 'quadratic_roots',
                    'answer_format_hint': 'Enter roots separated by commas (e.g. 3, -2)',
                }
            elif raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if values and len(values) == len(labels):
                    extra = {
                        'correct_answer_raw': '|'.join(str(v) for v in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_format_hint': 'Enter a number in every field',
                    }
            elif raw_type == 'linear':
                extra = {
                    'correct_answer_raw': _fn_linear_raw(raw),
                    'answer_type': 'linear',
                    'answer_format_hint': 'Enter the value (e.g. y = 9 or just 9)',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _fn_raw(raw),
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
        'gcse', 'maths', 'functions', **extra
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (7)
# ══════════════════════════════════════════════════════════════════════════════

def _fn_f_evaluate_linear():
    m = random.randint(2, 7)
    c = random.randint(-8, 12)
    x = random.randint(-5, 8)
    ans = m * x + c
    q = (
        rf"A function is defined by <strong>\(f(x) = {_linear(m, c)}\)</strong>. "
        rf"Find <strong>\(f({x})\)</strong>."
    )
    s = (
        rf"Substitute \(x = {x}\):<br>"
        rf"\(f({x}) = {m} \times {_sub_num(x)} {_fmt_b(c)} = {ans}\)<br>"
        rf"<strong>\(f({x}) = {ans}\)</strong>"
    )
    return q, s, "Replace every x in the rule with the given number.", 2, ans


def _fn_f_evaluate_square():
    b = random.randint(-4, 4)
    c = random.randint(-5, 10)
    x = random.randint(-4, 5)
    ans = x * x + b * x + c
    rule = _quadratic_rule(b, c)
    q = rf"If <strong>\(f(x) = {rule}\)</strong>, find <strong>\(f({x})\)</strong>."
    if b == 0:
        middle = ""
    elif b == 1:
        middle = rf"+ {_sub_num(x)}"
    elif b == -1:
        middle = rf"- {_sub_num(x)}"
    elif b > 0:
        middle = rf"+ {b} \times {_sub_num(x)}"
    else:
        middle = rf"- {abs(b)} \times {_sub_num(x)}"
    s = (
        rf"Substitute \(x = {x}\):<br>"
        rf"\(f({x}) = {_sub_num(x)}^2 {middle} {_fmt_b(c)}\)<br>"
        rf"\(f({x}) = {x*x} {_fmt_b(b*x)} {_fmt_b(c)} = {ans}\)<br>"
        rf"<strong>\(f({x}) = {ans}\)</strong>"
    )
    return q, s, "Substitute carefully with negative values — use brackets.", 2, ans


def _fn_f_input_output():
    m = random.randint(2, 5)
    c = random.randint(1, 9)
    x = random.randint(1, 6)
    y = m * x + c
    q = (
        rf"A function machine applies <strong>×{m}</strong> then <strong>+{c}</strong>. "
        rf"The input is <strong>{x}</strong>. What is the output?"
    )
    s = (
        rf"Apply the operations in order:<br>"
        rf"\({x} \times {m} = {m*x}\)<br>"
        rf"\({m*x} + {c} = {y}\)<br>"
        rf"<strong>Output = {y}</strong>"
    )
    return q, s, "Apply each step in order, or use f(x) notation.", 2, y


def _fn_f_machine_add_then_multiply():
    """Function machine: add first, then multiply (order matters)."""
    c = random.randint(1, 8)
    m = random.randint(2, 5)
    x = random.randint(1, 7)
    after_add = x + c
    y = m * after_add
    q = (
        rf"A function machine applies <strong>+{c}</strong> then <strong>×{m}</strong>. "
        rf"The input is <strong>{x}</strong>. What is the output?"
    )
    s = (
        rf"<strong>Step 1</strong> — add {c} first:<br>"
        rf"\({x} + {c} = {after_add}\)<br>"
        rf"<strong>Step 2</strong> — then multiply by {m}:<br>"
        rf"\({after_add} \times {m} = {y}\)<br>"
        rf"<strong>Output = {y}</strong>"
    )
    hint = "Apply the operations in the order shown on the machine — here, add before you multiply."
    return q, s, hint, 2, y


def _fn_f_machine_find_input():
    """Function machine: output given — work backwards to find the input."""
    m = random.randint(2, 5)
    c = random.randint(1, 9)
    x = random.randint(2, 8)
    y = m * x + c
    q = (
        rf"A function machine applies <strong>×{m}</strong> then <strong>+{c}</strong>. "
        rf"The <strong>output</strong> is <strong>{y}</strong>. What was the <strong>input</strong>?"
    )
    after_mult = y - c
    s = (
        rf"Work backwards, undoing each step in reverse order:<br>"
        rf"<strong>Step 1</strong> — undo the addition (subtract {c}):<br>"
        rf"\({y} - {c} = {after_mult}\)<br>"
        rf"<strong>Step 2</strong> — undo the multiplication (divide by {m}):<br>"
        rf"\({after_mult} \div {m} = {x}\)<br>"
        rf"<strong>Input = {x}</strong>"
    )
    hint = "Reverse the machine: undo the last operation first, then undo the first operation."
    return q, s, hint, 3, x


def _fn_f_find_input_linear():
    m = random.randint(2, 6)
    c = random.randint(1, 10)
    x = random.randint(2, 8)
    target = m * x + c
    q = (
        rf"<strong>\(f(x) = {_linear(m, c)}\)</strong> and <strong>\(f(x) = {target}\)</strong>. "
        rf"Find <strong>\(x\)</strong>."
    )
    s = (
        rf"\({target} = {m}x {_fmt_b(c)}\) → \({target - c} = {m}x\) → "
        rf"<strong>\(x = {x}\)</strong>"
    )
    return q, s, "Set f(x) equal to the target value and solve like a linear equation.", 3, _fn_linear_answer(x, 'x')


def _fn_f_meaning_notation():
    m = random.randint(2, 4)
    c = random.randint(1, 6)
    x1, x2 = random.randint(1, 4), random.randint(5, 9)
    y1, y2 = m * x1 + c, m * x2 + c
    q = (
        rf"\(f(x) = {_linear(m, c)}\). Find <strong>\(f({x1})\)</strong> and "
        rf"<strong>\(f({x2})\)</strong>."
    )
    s = (
        rf"\(f({x1}) = {m} \times {x1} + {c} = {y1}\)<br>"
        rf"\(f({x2}) = {m} \times {x2} + {c} = {y2}\)<br>"
        rf"<strong>\(f({x1}) = {y1}\)</strong> and <strong>\(f({x2}) = {y2}\)</strong>"
    )
    return q, s, "f(a) means the output when the input is a.", 2, _fn_fields_answer(
        [y1, y2], [f'f({x1})', f'f({x2})']
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _fn_i_composite_linear():
    a = random.randint(2, 4)
    b = random.randint(1, 5)
    c = random.randint(1, 4)
    d = random.randint(0, 6)
    x = random.randint(1, 5)
    gx = c * x + d
    ans = a * gx + b
    q = (
        rf"\(f(x) = {_linear(a, b)}\) and \(g(x) = {_linear(c, d)}\). "
        rf"Find <strong>\(f(g({x}))\)</strong>."
    )
    s = (
        rf"First \(g({x}) = {c} \times {x} {_fmt_b(d)} = {gx}\)<br>"
        rf"Then \(f({gx}) = {a} \times {gx} {_fmt_b(b)} = {ans}\)<br>"
        rf"<strong>\(f(g({x})) = {ans}\)</strong>"
    )
    return q, s, "Work inside out: find g(x) first, then apply f.", 3, ans


def _fn_i_sum_two_values():
    m = random.randint(2, 5)
    c = random.randint(-4, 8)
    x1 = random.randint(-3, 2)
    x2 = random.randint(3, 7)
    s_val = (m * x1 + c) + (m * x2 + c)
    q = (
        rf"\(f(x) = {_linear(m, c)}\). Find <strong>\(f({x1}) + f({x2})\)</strong>."
    )
    s = (
        rf"\(f({x1}) = {m * x1 + c}\), \(f({x2}) = {m * x2 + c}\)<br>"
        rf"Sum = <strong>{s_val}</strong>"
    )
    return q, s, "Evaluate each output separately, then add.", 3, s_val


def _fn_i_quadratic_eval():
    r1 = random.randint(1, 4)
    r2 = random.randint(1, 4)
    x = random.choice([-r1, r2, 0])
    # f(x) = (x - r1)(x + r2) expanded: x² + (r2-r1)x - r1*r2
    b = r2 - r1
    c = -r1 * r2
    ans = x * x + b * x + c
    rule = _quadratic_rule(b, c)
    q = rf"\(f(x) = {rule}\). Find <strong>\(f({x})\)</strong>."
    if b == 0:
        middle = ""
    elif b > 0:
        middle = rf"+ {b} \times {_sub_num(x)}"
    else:
        middle = rf"- {abs(b)} \times {_sub_num(x)}"
    s = (
        rf"Substitute \(x = {x}\):<br>"
        rf"\(f({x}) = {_sub_num(x)}^2 {middle} {_fmt_b(c)}\)<br>"
        rf"\(f({x}) = {x*x} {_fmt_b(b*x)} {_fmt_b(c)} = {ans}\)<br>"
        rf"<strong>\(f({x}) = {ans}\)</strong>"
    )
    return q, s, "Substitute into the quadratic expression.", 3, ans


def _fn_i_inverse_linear():
    m = random.randint(2, 6)
    c = random.randint(1, 12)
    q = rf"The function <strong>\(f(x) = {_linear(m, c)}\)</strong> has inverse <strong>\(f^{{-1}}(x)\)</strong>. Find \(f^{{-1}}(x)\)."
    s = (
        rf"Let \(y = {m}x {_fmt_b(c)}\). Swap and rearrange:<br>"
        rf"\(x = {m}y {_fmt_b(c)}\) → \(x {_fmt_b(-c)} = {m}y\) → "
        rf"<strong>\(f^{{-1}}(x) = \dfrac{{x {_fmt_b(-c)}}}{{{m}}}\)</strong>"
    )
    return q, s, "Inverse undoes f: solve y = f(x) for x in terms of y.", 4


def _fn_i_write_composite_rule():
    a = random.randint(2, 3)
    c = random.randint(2, 4)
    q = (
        rf"\(f(x) = {a}x\) and \(g(x) = x + {c}\). "
        rf"Write an expression for <strong>\(f(g(x))\)</strong>."
    )
    s = (
        rf"\(g(x) = x + {c}\), so replace \(x\) in \(f(x)\) with \(x + {c}\):<br>"
        rf"\(f(g(x)) = {a}(x + {c})\)<br>"
        rf"\(f(g(x)) = {a}x + {a * c}\)<br>"
        rf"<strong>\(f(g(x)) = {a}x + {a * c}\)</strong>"
    )
    return q, s, "Substitute g(x) into f in place of x.", 3


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

def _fn_d_composite_quadratic():
    """f(x) = x², g(x) = x + k, find f(g(x)) and evaluate at a point."""
    k = random.randint(1, 5)
    x = random.randint(2, 6)
    gx = x + k
    ans = gx * gx
    q = (
        rf"\(f(x) = x^2\) and \(g(x) = x + {k}\). "
        rf"Find <strong>\(f(g({x}))\)</strong>."
    )
    s = (
        rf"\(g({x}) = {gx}\)<br>"
        rf"\(f(g({x})) = f({gx}) = {gx}^2 = {ans}\)<br>"
        rf"<strong>\(f(g({x})) = {ans}\)</strong>"
    )
    return q, s, "Composite: apply g, then f.", 4, ans


def _fn_d_solve_f_equals():
    r1 = random.randint(2, 6)
    r2 = random.randint(2, 6)
    while r2 == r1:
        r2 = random.randint(2, 6)
    lo, hi = min(r1, r2), max(r1, r2)
    b, c = -(lo + hi), lo * hi
    q = (
        rf"\(f(x) = {_quadratic_rule(b, c)}\). "
        rf"Solve <strong>\(f(x) = 0\)</strong>."
    )
    s = (
        rf"Factorise: \((x - {lo})(x - {hi}) = 0\)<br>"
        rf"<strong>\(x = {lo}\) or \(x = {hi}\)</strong>"
    )
    return q, s, "f(x) = 0 is a quadratic equation — factorise or use the formula.", 4, _fn_quadratic_roots_answer(lo, hi)


def _fn_d_inverse_then_eval():
    m = random.randint(2, 5)
    c = random.randint(2, 9)
    y_in = random.randint(10, 30)
    x_back = (y_in - c) // m
    if m * x_back + c != y_in:
        y_in = m * 4 + c
        x_back = 4
    q = (
        rf"\(f(x) = {_linear(m, c)}\). The output is <strong>{y_in}</strong>. "
        rf"What was the <strong>input</strong>? (Use \(f^{{-1}}\).)"
    )
    s = (
        rf"Use the inverse to work from output back to input:<br>"
        rf"\(f^{{-1}}({y_in}) = \dfrac{{{y_in} - {c}}}{{{m}}}\)<br>"
        rf"\(f^{{-1}}({y_in}) = \dfrac{{{y_in - c}}}{{{m}}} = {x_back}\)<br>"
        rf"<strong>Input = {x_back}</strong>"
    )
    return q, s, "Inverse maps output back to input.", 4, x_back


def _fn_d_ff_linear():
    a = random.randint(2, 4)
    b = random.randint(1, 5)
    x = random.randint(1, 4)
    once = a * x + b
    ans = a * once + b
    q = (
        rf"\(f(x) = {_linear(a, b)}\). Find <strong>\(f(f({x}))\)</strong> "
        rf"(apply \(f\) twice)."
    )
    s = (
        rf"\(f({x}) = {once}\)<br>"
        rf"\(f(f({x})) = f({once}) = {a} \times {once} {_fmt_b(b)} = {ans}\)<br>"
        rf"<strong>\(f(f({x})) = {ans}\)</strong>"
    )
    return q, s, "f(f(x)) means substitute f(x) into f again.", 4, ans


def _fn_d_domain_valid():
    q = (
        r"\(f(x) = \dfrac{1}{x}\). Which value of \(x\) "
        r"cannot be used as an input? Explain briefly."
    )
    s = r"<strong>\(x = 0\)</strong> — division by zero is not defined."
    return q, s, "The input must not make the denominator zero.", 2, 0


def _fn_d_multipart_composite_inverse():
    a = random.randint(2, 5)
    b = random.randint(1, 8)
    k = random.randint(2, 6)
    x_val = random.randint(1, 5)
    gx = x_val + k
    fgx = a * gx + b
    q = (
        rf"\(f(x) = {_linear(a, b)}\) and \(g(x) = x + {k}\).<br><br>"
        rf"<strong>a)</strong> Find an expression for \(f(g(x))\). [2]<br>"
        rf"<strong>b)</strong> Find \(f(g({x_val}))\). [2]<br>"
        rf"<strong>c)</strong> Find \(f^{{-1}}(x)\). [3]"
    )
    s = (
        rf"<strong>a)</strong> Replace \(x\) in \(f(x)\) with \(g(x) = x + {k}\):<br>"
        rf"\(f(g(x)) = {a}(x + {k}) {_fmt_b(b)}\)<br>"
        rf"\(f(g(x)) = {a}x + {a*k} {_fmt_b(b)} = {a}x {_fmt_b(a*k + b)}\)<br>"
        rf"<strong>\(f(g(x)) = {a}x {_fmt_b(a*k + b)}\)</strong><br><br>"
        rf"<strong>b)</strong> First \(g({x_val}) = {x_val} + {k} = {gx}\).<br>"
        rf"Then \(f({gx}) = {a} \times {gx} {_fmt_b(b)} = {fgx}\).<br>"
        rf"<strong>\(f(g({x_val})) = {fgx}\)</strong><br><br>"
        rf"<strong>c)</strong> Let \(y = {a}x {_fmt_b(b)}\). Swap \(x\) and \(y\):<br>"
        rf"\(x = {a}y {_fmt_b(b)}\)<br>"
        rf"\(x {_fmt_b(-b)} = {a}y\)<br>"
        rf"<strong>\(f^{{-1}}(x) = \dfrac{{x {_fmt_b(-b)}}}{{{a}}}\)</strong>"
    )
    return q, s, "For a composite, work inside out. For an inverse, swap x and y then rearrange.", 7


def _fn_d_multipart_quadratic_graph():
    h = random.randint(-4, 4)
    while h == 0:
        h = random.randint(-4, 4)
    k = random.randint(-6, 8)
    x_val = h + random.choice([-2, -1, 1, 2])
    fx = (x_val - h) ** 2 + k
    q = (
        rf"A function is given in completed-square form: \(f(x) = (x {_fmt_b(-h)})^2 {_fmt_b(k)}\).<br><br>"
        rf"<strong>a)</strong> State the coordinates of the minimum point. [2]<br>"
        rf"<strong>b)</strong> Find \(f({x_val})\). [2]<br>"
        rf"<strong>c)</strong> State the equation of the line of symmetry of the graph. [2]"
    )
    s = (
        rf"<strong>a)</strong> In \(f(x) = (x - h)^2 + k\), the minimum is \((h, k)\).<br>"
        rf"Here \(h = {h}\) and \(k = {k}\), so the minimum is "
        rf"<strong>\(({h},\, {k})\)</strong>.<br><br>"
        rf"<strong>b)</strong> Substitute \(x = {x_val}\):<br>"
        rf"\(f({x_val}) = ({x_val} {_fmt_b(-h)})^2 {_fmt_b(k)}\)<br>"
        rf"\(f({x_val}) = ({x_val - h})^2 {_fmt_b(k)} = {fx}\)<br>"
        rf"<strong>\(f({x_val}) = {fx}\)</strong><br><br>"
        rf"<strong>c)</strong> The line of symmetry passes through the minimum point, so "
        rf"<strong>\(x = {h}\)</strong>."
    )
    return q, s, "Completed-square form shows the turning point directly.", 6


def _fn_d_multipart_domain_range():
    excluded = random.choice([-4, -3, -2, 2, 3, 4])
    x_val = random.choice([n for n in range(-5, 6) if n != excluded])
    fx = 1 / (x_val - excluded)
    q = (
        rf"\(f(x) = \dfrac{{1}}{{x {_fmt_b(-excluded)}}}\).<br><br>"
        rf"<strong>a)</strong> State the value of \(x\) that cannot be used as an input. [1]<br>"
        rf"<strong>b)</strong> Explain why this input is not allowed. [2]<br>"
        rf"<strong>c)</strong> Find \(f({x_val})\). [2]"
    )
    if fx.is_integer():
        fx_str = str(int(fx))
    else:
        denominator = x_val - excluded
        fx_str = rf"\dfrac{{1}}{{{denominator}}}"
    q_sub = x_val - excluded
    s = (
        rf"<strong>a)</strong> The denominator must not be zero. \(x {_fmt_b(-excluded)} = 0\), "
        rf"so <strong>\(x = {excluded}\)</strong> is not allowed.<br><br>"
        rf"<strong>b)</strong> If \(x = {excluded}\), the denominator is \(0\). "
        rf"Division by zero is <strong>undefined</strong>, so the function would not give a valid output.<br><br>"
        rf"<strong>c)</strong> Substitute \(x = {x_val}\):<br>"
        rf"\(f({x_val}) = \dfrac{{1}}{{{x_val} {_fmt_b(-excluded)}}} = \dfrac{{1}}{{{q_sub}}}\)<br>"
        rf"<strong>\(f({x_val}) = {fx_str}\)</strong>"
    )
    return q, s, "Set the denominator equal to zero to find the excluded input.", 5


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (8 — randomised)
# ══════════════════════════════════════════════════════════════════════════════

def _fn_mcq_evaluate():
    m = random.randint(2, 7)
    c = random.randint(-6, 10)
    x = random.randint(-4, 7)
    correct = str(m * x + c)
    wrong = _three_numeric_distractors(correct, [m * x + c + 1, m * x, c, x])
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = rf"If \(f(x) = {_linear(m, c)}\), what is \(f({x})\)?"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Substitute x into the rule.", 2, opts, correct_letter


def _fn_mcq_composite():
    a, b, c, d = 2, 1, 3, 4
    x = random.randint(1, 4)
    gx = c * x + d
    correct = str(a * gx + b)
    wrong = _three_numeric_distractors(correct, [a * x + b, gx, a * gx, a * x + d])
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = rf"\(f(x) = {_linear(a, b)}\), \(g(x) = {_linear(c, d)}\). Find \(f(g({x}))\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Calculate g(x) first.", 2, opts, correct_letter


def _fn_mcq_inverse():
    m = random.randint(2, 5)
    c = random.randint(1, 8)
    correct = rf"\(\dfrac{{x {_fmt_b(-c)}}}{{{m}}}\)"
    wrong = [
        rf"\(\dfrac{{x {_fmt_b(c)}}}{{{m}}}\)",
        rf"\({m}x {_fmt_b(c)}\)",
        rf"\(\dfrac{{x}}{{{m}}} {_fmt_b(c)}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"Find \(f^{{-1}}(x)\) when \(f(x) = {_linear(m, c)}\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Solve y = mx + c for x.", 3, opts, correct_letter


def _fn_mcq_fg_expression():
    a = random.randint(2, 4)
    k = random.randint(2, 6)
    correct = rf"\({a}x + {a * k}\)"
    wrong = [
        rf"\({a}x + {k}\)",
        rf"\(x + {k}\)",
        rf"\({a}(x + {k})\)",
    ]
    # last wrong might equal correct - fix
    wrong = [
        rf"\({a}x + {k}\)",
        rf"\(x^{a} + {k}\)",
        rf"\({a} + x + {k}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"\(f(x) = {a}x\) and \(g(x) = x + {k}\). Which is \(f(g(x))\)?"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Replace x in f with g(x).", 2, opts, correct_letter


def _fn_mcq_evaluate_quadratic():
    b = random.randint(-4, 4)
    c = random.randint(-6, 6)
    x = random.randint(-3, 4)
    correct = str(x * x + b * x + c)
    wrong = _three_numeric_distractors(
        correct, [x * x + b * x + c + 1, x * x + c, b * x + c, 2 * x + b + c]
    )
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = rf"If \(f(x) = {_quadratic_rule(b, c)}\), what is \(f({_sub_num(x)})\)?"
    sol = rf"Substitute \(x = {x}\): <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Substitute the value, squaring first.", 2, opts, correct_letter


def _fn_mcq_gf_composite():
    a, b, c, d = 2, 1, 3, 4
    x = random.randint(1, 4)
    fx = a * x + b
    correct = str(c * fx + d)
    wrong = _three_numeric_distractors(
        correct, [a * (c * x + d) + b, fx, c * x + d, c * fx]
    )
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = rf"\(f(x) = {_linear(a, b)}\), \(g(x) = {_linear(c, d)}\). Find \(g(f({x}))\)."
    sol = (
        rf"First \(f({x}) = {fx}\), then \(g({fx}) = {correct}\). "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Work out f(x) first, then apply g.", 2, opts, correct_letter


def _fn_mcq_solve_linear():
    m = random.randint(2, 5)
    c = random.randint(-5, 5)
    x = random.randint(1, 6)
    k = m * x + c
    correct = str(x)
    wrong = _three_numeric_distractors(correct, [x + 1, k, k - c, x - 2])
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  x = {v}" for i, v in enumerate(vals)]
    q = rf"\(f(x) = {_linear(m, c)}\). Solve \(f(x) = {k}\)."
    sol = (
        rf"\({m}x {_fmt_b(c)} = {k}\) → \(x = {x}\). "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Set the rule equal to the value and solve for x.", 3, opts, correct_letter


def _fn_mcq_notation_meaning():
    n = random.randint(2, 6)
    correct = f"The output of f when the input is {n}"
    wrong = [
        f"f multiplied by {n}",
        f"The input that gives output {n}",
        f"The gradient of f at {n}",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"What does \(f({n})\) mean?"
    sol = (
        rf"\(f({n})\) is the value (output) of the function when \(x = {n}\). "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "f(input) gives the output for that input.", 1, opts, correct_letter


_FN_MCQ_POOL = [
    _fn_mcq_evaluate,
    _fn_mcq_composite,
    _fn_mcq_inverse,
    _fn_mcq_fg_expression,
    _fn_mcq_evaluate_quadratic,
    _fn_mcq_gf_composite,
    _fn_mcq_solve_linear,
    _fn_mcq_notation_meaning,
]


def _fn_mcq_dispatch():
    return random.choice(_FN_MCQ_POOL)()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _fn_f_evaluate_linear,
    _fn_f_evaluate_square,
    _fn_f_input_output,
    _fn_f_machine_add_then_multiply,
    _fn_f_machine_find_input,
    _fn_f_find_input_linear,
    _fn_f_meaning_notation,
]

_INTERMEDIATE = [
    _fn_i_composite_linear,
    _fn_i_sum_two_values,
    _fn_i_quadratic_eval,
    _fn_i_inverse_linear,
    _fn_i_write_composite_rule,
]

_DIFFICULT = [
    _fn_d_composite_quadratic,
    _fn_d_solve_f_equals,
    _fn_d_inverse_then_eval,
    _fn_d_ff_linear,
    _fn_d_domain_valid,
    _fn_d_multipart_composite_inverse,
    _fn_d_multipart_quadratic_graph,
    _fn_d_multipart_domain_range,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_functions_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_pool(
            _FN_MCQ_POOL, "functions", difficulty, count=4
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


def gcse_functions(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_functions_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "functions",
            options=opts, correct_answer=ans,
        )

    variants = gcse_functions_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    return _fn_problem_from_output(variant(), difficulty)
