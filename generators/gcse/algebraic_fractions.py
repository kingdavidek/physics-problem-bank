"""
GCSE Maths – Algebraic Fractions
5 foundational · 5 intermediate · 5 difficult · 8 MCQ (randomised each time)
"""
import random
from math import gcd
from generators.shared.utils import make_problem
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


def _frac(num, den):
    return rf"\dfrac{{{num}}}{{{den}}}"


def _math(tex):
    """Wrap raw TeX so MathJax renders it inline."""
    return rf"\({tex}\)"


def _af_step(content):
    """Spaced block for one solution step (rendered inside .answer)."""
    return f'<div style="margin:0 0 18px 0;line-height:1.75;">{content}</div>'


def _af_math_line(content):
    """Indented maths line with extra vertical space."""
    return f'<div style="margin:10px 0 0 20px;">{content}</div>'


def _af_answer(content):
    """Final answer line, separated from working."""
    return f'<div style="margin:14px 0 0 0;padding-top:10px;">{content}</div>'


def _fmt_linear(coeff, const=0):
    """ax + b style, coeff and const integers."""
    parts = []
    if coeff == 1:
        parts.append("x")
    elif coeff == -1:
        parts.append("-x")
    elif coeff != 0:
        parts.append(f"{coeff}x")
    if const > 0:
        parts.append(f"+ {const}")
    elif const < 0:
        parts.append(f"- {abs(const)}")
    return " ".join(parts) if parts else "0"


def _af_add_reciprocal_style_steps(n1, n2, c):
    """Step-by-step solution for n1/x + n2/(x+c) as a single fraction."""
    lcd = f"x(x + {c})"
    sum_coeff = n1 + n2
    const = n1 * c
    s = (
        _af_step(
            f"<strong>Step 1</strong> — find the lowest common denominator (LCD). "
            f"The denominators are x and (x + {c}), so LCD = <strong>{lcd}</strong>."
        )
        + _af_step(
            "<strong>Step 2</strong> — rewrite each fraction with denominator "
            f"{lcd}:"
            + _af_math_line(
                rf"\(\dfrac{{{n1}}}{{x}} = \dfrac{{{n1}(x + {c})}}{{{lcd}}}\) "
                rf"(multiply top and bottom by (x + {c}))"
            )
            + _af_math_line(
                rf"\(\dfrac{{{n2}}}{{x + {c}}} = \dfrac{{{n2}x}}{{{lcd}}}\) "
                rf"(multiply top and bottom by x)"
            )
        )
        + _af_step(
            "<strong>Step 3</strong> — add the numerators (keep the same denominator):"
            + _af_math_line(rf"\(\dfrac{{{n1}(x + {c}) + {n2}x}}{{{lcd}}}\)")
        )
        + _af_step(
            "<strong>Step 4</strong> — expand the brackets and collect like terms:"
            + _af_math_line(
                rf"\({n1}(x + {c}) + {n2}x = {n1}x + {n1 * c} + {n2}x = {sum_coeff}x + {const}\)"
            )
        )
        + _af_answer(
            f"<strong>Answer:</strong> "
            rf"\(\dfrac{{{sum_coeff}x + {const}}}{{{lcd}}}\)"
        )
    )
    hint = (
        f"When denominators are x and (x + {c}), multiply them to get the LCD: x(x + {c}). "
        f"Convert each fraction, add the numerators, expand brackets, then collect the x terms "
        f"and the number terms separately."
    )
    return s, hint


def _af_add_scaled_x_steps(p, q_num, k):
    """Step-by-step solution for p/x + q/(kx)."""
    lcd = f"{k}x"
    top = p * k + q_num
    s = (
        _af_step(
            f"<strong>Step 1</strong> — the LCD of x and {k}x is <strong>{lcd}</strong>."
        )
        + _af_step(
            f"<strong>Step 2</strong> — rewrite {p}/x with denominator {lcd}:"
            + _af_math_line(
                rf"\(\dfrac{{{p}}}{{x}} = \dfrac{{{p} \times {k}}}{{{k}x}} = \dfrac{{{p * k}}}{{{lcd}}}\)"
            )
        )
        + _af_step(
            f"<strong>Step 3</strong> — the second fraction already has denominator {lcd}. "
            f"Add the tops:"
            + _af_math_line(
                rf"\(\dfrac{{{p * k}}}{{{lcd}}} + \dfrac{{{q_num}}}{{{lcd}}} = "
                rf"\dfrac{{{p * k} + {q_num}}}{{{lcd}}} = "
                rf"<strong>\({_frac(str(top), lcd)}\)</strong>"
            )
        )
    )
    hint = (
        f"The denominators x and {k}x share a common multiple {k}x. "
        f"Multiply the first fraction's top and bottom by {k}, then add the numerators."
    )
    return s, hint


def _af_random_denominator():
    """GCSE-style linear denominator in x."""
    kind = random.randint(0, 3)
    b = random.randint(1, 9)
    if kind == 0:
        return "x"
    if kind == 1:
        return f"x + {b}"
    if kind == 2:
        return f"x - {b}"
    a = random.randint(2, 4)
    return f"{a}x" if random.random() < 0.45 else f"{a}x + {random.randint(1, 6)}"


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

def _af_f_cancel_numeric():
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    g = gcd(a, b)
    num, den = a, b
    q = rf"Simplify <strong>{_math(_frac(f'{num}x', f'{den}x'))}</strong>."
    s = (
        rf"Cancel the common factor \(x\) (and \(\gcd({num},{den})={g}\)):<br>"
        rf"<strong>\({_frac(num // g, den // g)}\)</strong>"
    )
    return q, s, "Cancel common factors in numerator and denominator only.", 2


def _af_f_same_denominator_add():
    p = random.randint(2, 12)
    q_val = random.randint(2, 12)
    d = _af_random_denominator()
    tex = _frac(str(p), d) + " + " + _frac(str(q_val), d)
    q = rf"Write as a single fraction: <strong>{_math(tex)}</strong>."
    s = rf"Same denominator: <strong>\({_frac(str(p + q_val), d)}\)</strong>"
    return q, s, "Add the numerators; keep the denominator.", 2


def _af_f_multiply():
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    g = gcd(b, a)
    tex = _frac("x", str(a)) + r" \times " + _frac(str(b), "x")
    q = rf"Simplify <strong>{_math(tex)}</strong>."
    if b == a:
        s = r"Cancel \(x\): <strong>\(1\)</strong>"
    else:
        s = rf"Multiply then cancel \(x\): <strong>\({_frac(b // g, a // g)}\)</strong>"
    return q, s, "Multiply tops and bottoms, then cancel common factors.", 2


def _af_f_divide():
    m = random.randint(2, 8)
    n = random.randint(2, 9)
    tex = _frac("x", str(m)) + r" \div " + _frac(str(n), "x")
    q = rf"Simplify <strong>{_math(tex)}</strong>."
    s = (
        rf"Flip and multiply: \(\dfrac{{x}}{{{m}}} \times \dfrac{{x}}{{{n}}} = "
        rf"\dfrac{{x^2}}{{{m * n}}}\) — or cancel to <strong>\({_frac('x^2', str(m * n))}\)</strong>."
    )
    return q, s, "Divide by a fraction = multiply by its reciprocal.", 3


def _af_f_factor_cancel():
    """(kx + kd)/(x + d) = k"""
    k = random.randint(2, 5)
    d = random.randint(2, 8)
    num = _fmt_linear(k, k * d)
    den = _fmt_linear(1, d)
    q = rf"Simplify <strong>{_math(_frac(num, den))}</strong>."
    s = (
        _af_step(rf"Factorise numerator: \({k}(x + {d})\)")
        + _af_answer(
            rf"Cancel \((x + {d})\): <strong>\({k}\)</strong> (for \(x \neq -{d}\))."
        )
    )
    return q, s, "Factorise the top fully, then cancel matching brackets.", 3


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _af_i_diff_denominator_add():
    """p/x + q/(kx) with procedural numerators."""
    p = random.randint(1, 6)
    q_num = random.randint(1, 6)
    k = random.randint(2, 7)
    q = rf"Write as a single fraction: <strong>\(\dfrac{{{p}}}{{x}} + \dfrac{{{q_num}}}{{{k}x}}\)</strong>."
    s, hint = _af_add_scaled_x_steps(p, q_num, k)
    return q, s, hint, 3


def _af_i_difference_of_squares():
    r = random.randint(2, 15)
    q = rf"Simplify <strong>{_math(_frac(f'x^2 - {r * r}', 'x - ' + str(r)))}</strong>."
    s = (
        _af_step(rf"Factorise top: \((x - {r})(x + {r})\)")
        + _af_answer(
            rf"Cancel \((x - {r})\): <strong>\(x + {r}\)</strong> (\(x \neq {r}\))."
        )
    )
    return q, s, "Difference of squares on the numerator.", 3


def _af_i_single_fraction_add():
    a = random.randint(1, 4)
    b = random.randint(1, 5)
    c = random.randint(2, 6)
    q = rf"Write as a single fraction: <strong>\(\dfrac{{{a}}}{{x}} + \dfrac{{{b}}}{{x + {c}}}\)</strong>."
    s, hint = _af_add_reciprocal_style_steps(a, b, c)
    return q, s, hint, 4


def _af_i_multiply_two():
    p = random.randint(1, 8)
    q_val = random.randint(1, 8)
    tex = (
        _frac(f"x + {p}", "x")
        + r" \times "
        + _frac("x", f"x + {q_val}")
    )
    q = rf"Simplify <strong>{_math(tex)}</strong>."
    s = (
        _af_step(
            "<strong>Step 1</strong> — multiply numerators and denominators:"
            + _af_math_line(
                rf"\(\dfrac{{(x + {p}) \times x}}{{x \times (x + {q_val})}} = "
                rf"\dfrac{{(x + {p})x}}{{x(x + {q_val})}}\)"
            )
        )
        + _af_step(
            "<strong>Step 2</strong> — cancel the common factor x (x ≠ 0):"
            + _af_math_line(rf"<strong>\({_frac(f'x + {p}', f'x + {q_val}')}\)</strong>")
        )
    )
    hint = (
        "Multiply tops together and bottoms together, then look for common factors "
        "in the numerator and denominator before cancelling."
    )
    return q, s, hint, 3


def _af_i_quadratic_cancel():
    lo = random.randint(2, 9)
    hi = random.randint(2, 9)
    while hi == lo:
        hi = random.randint(2, 9)
    sum_r = lo + hi
    prod = lo * hi
    q = rf"Simplify <strong>{_math(_frac(f'x^2 - {sum_r}x + {prod}', f'x - {lo}'))}</strong>."
    s = (
        _af_step(rf"Factorise: \((x - {lo})(x - {hi})\) on top")
        + _af_answer(
            rf"Cancel \((x - {lo})\): <strong>\(x - {hi}\)</strong> (\(x \neq {lo}\))."
        )
    )
    return q, s, "Factorise the quadratic numerator first.", 4


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

def _af_d_solve_simple():
    """a/x = p/q style with integer solution."""
    a = random.randint(2, 12)
    rhs_num = random.randint(1, 4)
    rhs_den = random.randint(2, 9)
    while gcd(a, rhs_num) != 1 and random.random() < 0.5:
        rhs_num = random.randint(1, 4)
    x_ans = a * rhs_den // rhs_num
    if rhs_num * x_ans != a * rhs_den:
        rhs_den = rhs_num * random.randint(2, 5)
        x_ans = a * rhs_den // rhs_num
    tex = _frac(str(a), "x") + " = " + _frac(str(rhs_num), str(rhs_den))
    q = rf"Solve <strong>{_math(tex)}</strong>."
    s = (
        _af_step(
            "<strong>Step 1</strong> — multiply both sides by x to clear the denominator:"
            + _af_math_line(rf"\({a} = \dfrac{{{rhs_num}x}}{{{rhs_den}}}\)")
        )
        + _af_step(
            f"<strong>Step 2</strong> — multiply both sides by {rhs_den}:"
            + _af_math_line(rf"\({a * rhs_den} = {rhs_num}x\)")
        )
        + _af_answer(
            f"<strong>Step 3</strong> — divide both sides by {rhs_num}: "
            rf"<strong>\(x = {x_ans}\)</strong>"
        )
    )
    hint = (
        "Remove fractions by multiplying both sides by the denominators, one at a time. "
        "Start by multiplying by x, then by the remaining denominator."
    )
    return q, s, hint, 4


def _af_d_add_reciprocal_style():
    n1 = random.randint(2, 7)
    n2 = random.randint(2, 7)
    c = random.randint(2, 9)
    q = rf"Write as a single fraction: <strong>\(\dfrac{{{n1}}}{{x}} + \dfrac{{{n2}}}{{x + {c}}}\)</strong>."
    s, hint = _af_add_reciprocal_style_steps(n1, n2, c)
    return q, s, hint, 4


def _af_d_simplify_nested():
    k = random.randint(2, 7)
    d = random.randint(3, 12)
    q = rf"Simplify <strong>{_math(_frac(f'{k}(x^2 - {d * d})', f'(x - {d})(x + {d})'))}</strong>."
    s = (
        _af_step(rf"Top: \({k}(x - {d})(x + {d})\)")
        + _af_answer(rf"Cancel \((x - {d})(x + {d})\): <strong>\({k}\)</strong>")
    )
    return q, s, "Recognise difference of squares in both parts.", 4


def _af_d_subtract_fractions():
    p = random.randint(4, 14)
    q_val = random.randint(2, 10)
    d = _af_random_denominator()
    tex = _frac(str(p), d) + " - " + _frac(str(q_val), d)
    q = rf"Simplify <strong>{_math(tex)}</strong>."
    ans = p - q_val
    s = rf"<strong>\({_frac(str(ans), d)}\)</strong>"
    return q, s, "Subtract numerators when denominators match.", 3


def _af_d_equation_with_linear_den():
    """(x + c)/x = r style with integer solution."""
    c = random.randint(2, 12)
    rhs = random.randint(2, 6)
    x_ans = c // (rhs - 1)
    if rhs == 1 or (rhs - 1) * x_ans != c:
        rhs = random.randint(2, 4)
        c = random.randint(2, 12) * (rhs - 1)
        x_ans = c // (rhs - 1)
    tex = _frac(f"x + {c}", "x") + f" = {rhs}"
    q = rf"Solve <strong>{_math(tex)}</strong>."
    s = (
        _af_step(
            "<strong>Step 1</strong> — multiply both sides by x (x ≠ 0):"
            + _af_math_line(rf"\(x + {c} = {rhs}x\)")
        )
        + _af_step(
            "<strong>Step 2</strong> — bring x terms to one side:"
            + _af_math_line(rf"\({c} = {rhs}x - x = {rhs - 1}x\)")
        )
        + _af_answer(
            f"<strong>Step 3</strong> — divide by {rhs - 1}: "
            rf"<strong>\(x = {x_ans}\)</strong>"
        )
    )
    hint = (
        "Multiply through by x to remove the fraction, then collect x terms on one side "
        "and numbers on the other. Remember x cannot be 0."
    )
    return q, s, hint, 4


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (8 — randomised)
# ══════════════════════════════════════════════════════════════════════════════

def _af_mcq_cancel():
    k = random.randint(2, 5)
    d = random.randint(2, 7)
    correct = str(k)
    wrong = []
    for cand in (k + 1, d, k + d, k - 1, k + 2, 2 * k):
        s = str(cand)
        if s != correct and s not in wrong:
            wrong.append(s)
        if len(wrong) == 3:
            break
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    num = _fmt_linear(k, k * d)
    den = _fmt_linear(1, d)
    q = rf"Simplify {_math(_frac(num, den))}."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Factorise and cancel the common bracket.", 2, opts, correct_letter


def _af_mcq_add_same():
    p = random.randint(2, 6)
    q_val = random.randint(2, 6)
    while p * q_val == p + q_val:
        q_val = random.randint(2, 6)
    d = r"x + 3"
    correct = rf"\({_frac(str(p + q_val), d)}\)"
    wrong = [
        rf"\({_frac(str(p * q_val), d)}\)",
        rf"\({_frac(str(p), d)} + {_frac(str(q_val), 'x')}\)",
        rf"\({_frac(str(p + q_val), 'x')}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"\({_frac(str(p), d)} + {_frac(str(q_val), d)}\) simplifies to:"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Add numerators.", 2, opts, correct_letter


def _af_mcq_diff_squares():
    r = random.randint(3, 6)
    correct = rf"\(x + {r}\)"
    wrong = [rf"\(x - {r}\)", rf"\(x^2 + {r}\)", rf"\(x + {r^2}\)"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"{_math(_frac(f'x^2 - {r * r}', f'x - {r}'))} ="
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Factorise x² − r².", 2, opts, correct_letter


def _af_mcq_solve():
    c = random.randint(3, 6)
    correct = rf"\(x = {c}\)"
    wrong = [rf"\(x = {c + 1}\)", rf"\(x = 0\)", rf"\(x = -{c}\)"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    tex = _frac(f"x + {c}", "x") + " = 2"
    q = rf"Solve {_math(tex)}."
    sol = (
        f"Multiply by x: x + {c} = 2x → {c} = x → "
        rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Multiply both sides by x, then collect x terms on one side.", 3, opts, correct_letter


def _af_mcq_multiply():
    a = random.randint(2, 5)
    b = random.randint(2, 6)
    while b == a:
        b = random.randint(2, 6)
    g = gcd(a, b)
    correct = rf"\({_frac(b // g, a // g)}\)"
    wrong = [
        rf"\({_frac(a // g, b // g)}\)",
        rf"\({_frac(a * b, 'x^2')}\)",
        rf"\({_frac('x^2', a * b)}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    tex = _frac("x", str(a)) + r" \times " + _frac(str(b), "x")
    q = rf"Simplify {_math(tex)}."
    sol = rf"Multiply and cancel \(x\): <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Multiply tops and bottoms, then cancel x.", 2, opts, correct_letter


def _af_mcq_divide():
    m = random.randint(2, 4)
    n = random.randint(2, 5)
    while m * n == m + n:
        n = random.randint(2, 5)
    correct = rf"\({_frac('x^2', m * n)}\)"
    wrong = [
        rf"\({_frac('x^2', m + n)}\)",
        rf"\({_frac(m * n, 'x^2')}\)",
        rf"\({_frac(1, m * n)}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    tex = _frac("x", str(m)) + r" \div " + _frac(str(n), "x")
    q = rf"Simplify {_math(tex)}."
    sol = (
        rf"Flip and multiply: \(\dfrac{{x}}{{{m}}} \times \dfrac{{x}}{{{n}}} = "
        rf"{correct}\). Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Dividing by a fraction = multiply by its reciprocal.", 3, opts, correct_letter


def _af_mcq_subtract_same():
    p = random.randint(5, 9)
    q_val = random.randint(2, 4)
    d = random.choice([r"x + 1", r"x - 2", r"2x"])
    correct = rf"\({_frac(str(p - q_val), d)}\)"
    wrong = [
        rf"\({_frac(str(p + q_val), d)}\)",
        rf"\({_frac(str(p - q_val), 'x')}\)",
        rf"\({p - q_val}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"\({_frac(str(p), d)} - {_frac(str(q_val), d)}\) simplifies to:"
    sol = rf"Subtract numerators over the same denominator: <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Subtract the numerators; keep the denominator.", 2, opts, correct_letter


def _af_mcq_factor_cancel():
    r1 = random.randint(2, 5)
    r2 = random.randint(2, 5)
    while r2 == r1:
        r2 = random.randint(2, 5)
    b = r1 + r2
    c = r1 * r2
    num = f"x^2 + {b}x + {c}"
    den = f"x + {r1}"
    correct = rf"\(x + {r2}\)"
    wrong = [rf"\(x + {r1}\)", rf"\(x - {r2}\)", rf"\(x + {b}\)"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"Simplify {_math(_frac(num, den))}."
    sol = (
        rf"Factorise the numerator: \((x + {r1})(x + {r2})\), then cancel "
        rf"\((x + {r1})\): <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Factorise the quadratic, then cancel the common bracket.", 3, opts, correct_letter


def _af_mcq_dispatch():
    return random.choice([
        _af_mcq_cancel,
        _af_mcq_add_same,
        _af_mcq_diff_squares,
        _af_mcq_solve,
        _af_mcq_multiply,
        _af_mcq_divide,
        _af_mcq_subtract_same,
        _af_mcq_factor_cancel,
    ])()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _af_f_cancel_numeric,
    _af_f_same_denominator_add,
    _af_f_multiply,
    _af_f_divide,
    _af_f_factor_cancel,
]

_INTERMEDIATE = [
    _af_i_diff_denominator_add,
    _af_i_difference_of_squares,
    _af_i_single_fraction_add,
    _af_i_multiply_two,
    _af_i_quadratic_cancel,
]

_DIFFICULT = [
    _af_d_solve_simple,
    _af_d_add_reciprocal_style,
    _af_d_simplify_nested,
    _af_d_subtract_fractions,
    _af_d_equation_with_linear_den,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_algebraic_fractions_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_fn(
            _af_mcq_dispatch, "algebraic_fractions", difficulty, count=4
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


def gcse_algebraic_fractions(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_algebraic_fractions_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "algebraic_fractions",
            options=opts, correct_answer=ans,
        )

    variants = gcse_algebraic_fractions_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "maths", "algebraic_fractions",
    )
