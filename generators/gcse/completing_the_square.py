"""
GCSE Maths – Completing the Square
5 foundational · 5 intermediate · 5 difficult · 8 MCQ (randomised each time)
"""
import math
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_pool,
    run_mcq_variant,
    pick_named_variant,
)


def _fmt_const(k):
    if k > 0:
        return f"+ {k}"
    if k < 0:
        return f"- {abs(k)}"
    return ""


def _fmt_adjust_constant(n):
    if n > 0:
        return f"add \\({n}\\)"
    if n < 0:
        return f"subtract \\({abs(n)}\\)"
    return "add \\(0\\)"


def _fmt_linear_x(b):
    """Coefficient of x in x² + bx + c (b = 2p)."""
    if b == 0:
        return ""
    if b == 2:
        return "+ 2x"
    if b == -2:
        return "- 2x"
    if b > 0:
        return f"+ {b}x"
    return f"- {abs(b)}x"


def _completed_form(p, k):
    """(x + p)² + k with sign formatting."""
    inner = f"(x + {p})" if p >= 0 else f"(x - {abs(p)})"
    tail = _fmt_const(k)
    return rf"{inner}^2 {tail}".strip()


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_f_half_coefficient():
    p = random.randint(2, 8)
    b = 2 * p
    c = random.randint(-12, 12)
    c_str = _fmt_const(c)
    q = (
        rf"Complete the square for \(x^2 {_fmt_linear_x(b)} {c_str}\). "
        rf"What is the value of <strong>p</strong> in \((x + p)^2 + \ldots\)?"
    )
    s = rf"Half of {b} is {p}, so <strong>\(p = {p}\)</strong>."
    return q, s, "For x² + bx + …, take half of b (the number in front of x).", 1


def _cts_f_square_the_half():
    p = random.randint(2, 7)
    b = 2 * p
    sq = p * p
    q = rf"The x² + {b}x + … form uses half the x-coefficient ({p}). What number do you <strong>subtract</strong> when building \((x + {p})^2\)?"
    s = rf"Square the half: {p}² = <strong>{sq}</strong>."
    return q, s, "You subtract p² when rewriting the constant part.", 1


def _cts_f_write_completed_form():
    p = random.randint(1, 6)
    k = random.randint(-10, 8)
    b = 2 * p
    q_val = k + p * p
    q_str = _fmt_const(q_val)
    q = rf"Write \(x^2 {_fmt_linear_x(b)} {q_str}\) in completed-square form \((x + p)^2 + k\)."
    k_str = _fmt_const(k)
    s = (
        rf"\((x + {p})^2 = x^2 {_fmt_linear_x(b)} + {p*p}\)<br>"
        rf"To get \(x^2 {_fmt_linear_x(b)} {q_str}\), subtract \({p*p}\) and {_fmt_adjust_constant(q_val)}:<br>"
        rf"\((x + {p})^2 - {p*p} {q_str} = (x + {p})^2 {k_str}\)<br>"
        rf"<strong>\((x + {p})^2 {k_str}\)</strong>"
    )
    return q, s, f"Half of {b} is {p}; subtract {p}² = {p*p} from the constant.", 2


def _cts_f_expand_check():
    p = random.randint(2, 5)
    k = random.randint(-6, 6)
    k_str = _fmt_const(k)
    q = rf"Expand <strong>\((x + {p})^2 {k_str}\)</strong> (simplify)."
    expanded_c = p * p + k
    b = 2 * p
    c_str = _fmt_const(expanded_c)
    s = rf"\(x^2 {_fmt_linear_x(b)} {c_str}\)"
    return q, s, "Expand the square first, then add the constant.", 2


def _cts_f_missing_constant():
    p = random.randint(3, 7)
    target = p * p
    b = 2 * p
    q = rf"You are completing \(x^2 {_fmt_linear_x(b)} + c\). What must <strong>c</strong> be so the expression becomes \((x + {p})^2\)?"
    s = rf"Need \(c = {p}^2 = {target}\), so <strong>\(c = {target}\)</strong>."
    return q, s, "A perfect square trinomial has c = (half of b)².", 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_i_complete_expression():
    p = random.randint(1, 7)
    q_val = random.randint(-15, 10)
    b = 2 * p
    k = q_val - p * p
    q_str = _fmt_const(q_val)
    q = rf"Complete the square: \(x^2 {_fmt_linear_x(b)} {q_str}\)."
    k_str = _fmt_const(k)
    s = (
        rf"Half of {b} is {p}, so start with \((x + {p})^2\).<br>"
        rf"\((x + {p})^2 = x^2 {_fmt_linear_x(b)} + {p*p}\)<br>"
        rf"Adjust the constant: \((x + {p})^2 - {p*p} {q_str} = (x + {p})^2 {k_str}\)<br>"
        rf"<strong>\((x + {p})^2 {k_str}\)</strong>"
    )
    return q, s, f"Use p = {p}, then adjust the constant by −{p*p}.", 3


def _cts_i_solve_integer_roots():
    p = random.randint(2, 5)
    d = random.randint(1, 4)
    r1, r2 = -p + d, -p - d
    b = 2 * p
    c = r1 * r2
    k_rhs = d * d
    q = rf"Solve \(x^2 {_fmt_linear_x(b)} {_fmt_const(c)} = 0\) by completing the square."
    sol = (
        rf"Rearrange: \(x^2 {_fmt_linear_x(b)} = {-c}\)<br>"
        rf"\((x + {p})^2 = {-c} + {p*p} = {k_rhs}\)<br>"
        rf"\(x + {p} = \pm {d}\)<br>"
        rf"<strong>\(x = {r1}\) or \(x = {r2}\)</strong>"
    )
    return q, sol, "Move the constant, complete the square, then square-root both sides.", 4


def _cts_i_turning_point():
    p = random.randint(-4, 4)
    k = random.randint(-8, 10)
    k_str = _fmt_const(k)
    inner = f"(x + {p})" if p >= 0 else f"(x - {abs(p)})"
    q = (
        rf"The graph of \(y = {inner}^2 {k_str}\) has a minimum point. "
        rf"State the coordinates of the minimum."
    )
    s = rf"Completed form shows minimum at <strong>\(({-p},\, {k})\)</strong>."
    return q, s, "For (x + p)² + k with positive square, turning point is (−p, k).", 3


def _cts_i_solve_rearrange_first():
    p = random.randint(2, 5)
    root = p + random.randint(1, 5)
    rhs = root * root - p * p
    b = 2 * p
    q = rf"Solve \(x^2 {_fmt_linear_x(b)} = {rhs}\) by completing the square."
    total = rhs + p * p
    x1, x2 = -p + root, -p - root
    s = (
        rf"\((x + {p})^2 = {rhs} + {p*p} = {total}\)<br>"
        rf"\(x + {p} = \pm {root}\)<br>"
        rf"<strong>\(x = {x1}\) or \(x = {x2}\)</strong>"
    )
    return q, s, f"Add {p}² to both sides after isolating the x terms.", 3


def _cts_i_negative_x_coeff():
    p = random.randint(2, 6)
    b = -2 * p
    q_val = random.randint(1, 12)
    k = q_val - p * p
    k_str = _fmt_const(k)
    q = rf"Complete the square: \(x^2 {_fmt_linear_x(b)} + {q_val}\)."
    s = (
        rf"Half of \(-{2*p}\) is \(-{p}\), so use \((x - {p})^2\).<br>"
        rf"\((x - {p})^2 = x^2 {_fmt_linear_x(b)} + {p*p}\)<br>"
        rf"Adjust the constant: \((x - {p})^2 - {p*p} + {q_val} = (x - {p})^2 {k_str}\)<br>"
        rf"<strong>\((x - {p})^2 {k_str}\)</strong>"
    )
    return q, s, "Half of a negative x-coefficient is negative — use (x − p)².", 3


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_d_solve_surd():
    while True:
        p = random.randint(2, 5)
        k = random.choice([3, 5, 6, 7, 10, 11])
        rhs = k + p * p
        if not _is_perfect_square(rhs):
            break
    b = 2 * p
    q = rf"Solve \(x^2 {_fmt_linear_x(b)} - {k} = 0\) by completing the square. Give exact answers."
    s = (
        rf"\(x^2 {_fmt_linear_x(b)} = {k}\)<br>"
        rf"\((x + {p})^2 = {rhs}\)<br>"
        rf"\(x + {p} = \pm\sqrt{{{rhs}}}\)<br>"
        rf"<strong>\(x = -{p} \pm \sqrt{{{rhs}}}\)</strong>"
    )
    return q, s, "Rearrange, complete the square, then take ± the square root.", 4


def _is_perfect_square(n):
    if n < 0:
        return False
    r = int(math.isqrt(n))
    return r * r == n


def _cts_d_decimal_roots():
    p = random.randint(3, 6)
    rhs = random.choice([11, 13, 17, 19, 23])
    b = 2 * p
    total = rhs + p * p
    q = rf"Solve \(x^2 {_fmt_linear_x(b)} = {rhs}\) by completing the square. Give answers to <strong>2 d.p.</strong>"
    x1 = -p + math.sqrt(total)
    x2 = -p - math.sqrt(total)
    s = (
        rf"\((x + {p})^2 = {total}\)<br>"
        rf"\(x + {p} = \pm\sqrt{{{total}}} \approx \pm {math.sqrt(total):.3f}\)<br>"
        rf"<strong>\(x \approx {x1:.2f}\) or \(x \approx {x2:.2f}\)</strong>"
    )
    return q, s, "Use a calculator for the square root if needed.", 4


def _cts_d_factor_a_out():
    a = random.choice([2, 3])
    p = random.randint(2, 4)
    b_inner = 2 * p
    q_inner = random.randint(-5, 8)
    k = q_inner - p * p
    k_str = _fmt_const(k)
    original_b = a * b_inner
    original_c = a * q_inner
    q = (
        rf"Complete the square for \(y = {a}x^2 {_fmt_linear_x(original_b)} {_fmt_const(original_c)}\). "
        rf"Start by factorising {a} from the expression."
    )
    s = (
        rf"\(y = {a}\left(x^2 {_fmt_linear_x(b_inner)} {_fmt_const(q_inner)}\right)\)<br>"
        rf"Inside: \(\left(x + {p}\right)^2 {k_str}\)<br>"
        rf"<strong>\(y = {a}\left((x + {p})^2 {k_str}\right)\)</strong>"
    )
    return q, s, f"Factor {a} out, complete the square inside the bracket, then multiply back.", 5


def _cts_d_minimum_value_word():
    h = random.randint(2, 6)
    max_p = random.randint(80, 200)
    q = (
        rf"Profit is \(P = -2(x - {h})^2 + {max_p}\) (£ thousands). "
        rf"What is the <strong>maximum</strong> profit?"
    )
    s = rf"Completed-square form: peak when \(x = {h}\). <strong>Maximum profit = £{max_p}000</strong>."
    return q, s, "The +k term in (x − h)² + max is the maximum (when the squared part is 0).", 3


def _cts_d_exam_show_that():
    p = random.randint(2, 5)
    k = random.randint(-9, 5)
    b = 2 * p
    q_val = k + p * p
    q_str = _fmt_const(q_val)
    k_str = _fmt_const(k)
    q = (
        rf"Show that \(x^2 {_fmt_linear_x(b)} {q_str}\) can be written as "
        rf"\((x + {p})^2 {k_str}\)."
    )
    s = (
        rf"Expand \((x + {p})^2 = x^2 {_fmt_linear_x(b)} + {p*p}\)<br>"
        rf"So \((x + {p})^2 {k_str} = x^2 {_fmt_linear_x(b)} {q_str}\) ✓"
    )
    return q, s, "Expand your completed form to verify it matches the original.", 3


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (8 procedural — randomised each call)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_mcq_half_b():
    p = random.randint(2, 9)
    b = 2 * p
    wrong = [p + 1, p - 1, 2 * p, p * p]
    wrong = [w for w in wrong if w != p][:3]
    opts_vals = wrong + [p]
    random.shuffle(opts_vals)
    letters = "ABCD"
    correct = letters[opts_vals.index(p)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(opts_vals)]
    q = rf"For \(x^2 {_fmt_linear_x(b)} + \ldots\), completing the square uses \(p\) in \((x + p)^2\). What is <strong>p</strong>?"
    sol = rf"Half of {b} is {p}. Answer: <strong>{correct}</strong>"
    return q, sol, "p = half of the coefficient of x.", 1, opts, correct


def _cts_mcq_completed_form():
    p = random.randint(2, 6)
    k = random.randint(-8, 6)
    b = 2 * p
    q_val = k + p * p
    correct_str = f"(x + {p})^2 {_fmt_const(k)}"
    wrong = [
        f"(x + {p})^2 {_fmt_const(k + 1)}",
        f"(x + {p + 1})^2 {_fmt_const(k)}",
        f"(x - {p})^2 {_fmt_const(k)}",
    ]
    forms = wrong + [correct_str]
    random.shuffle(forms)
    letters = "ABCD"
    correct = letters[forms.index(correct_str)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q_str = _fmt_const(q_val)
    q = rf"Which is \(x^2 {_fmt_linear_x(b)} {q_str}\) written in completed-square form?"
    sol = rf"<strong>{correct_str}</strong>. Answer: <strong>{correct}</strong>"
    return q, sol, f"Use p = {p}, constant adjustment {k}.", 2, opts, correct


def _cts_mcq_solve_roots():
    p = random.randint(2, 5)
    d = random.randint(1, 4)
    r1, r2 = -p + d, -p - d
    b = -(r1 + r2)
    c = r1 * r2
    correct_x = random.choice([r1, r2])
    wrong_candidates = [r1 + 1, r2 - 1, -correct_x, p, correct_x + 2, correct_x - 2]
    wrong = []
    for value in wrong_candidates:
        if value != correct_x and value not in wrong:
            wrong.append(value)
        if len(wrong) == 3:
            break
    vals = wrong + [correct_x]
    random.shuffle(vals)
    letters = "ABCD"
    correct = letters[vals.index(correct_x)]
    opts = [f"{letters[i]}  x = {v}" for i, v in enumerate(vals)]
    q = rf"Solve \(x^2 {_fmt_linear_x(b)} {_fmt_const(c)} = 0\) by completing the square. One solution is:"
    sol = rf"Solutions \(x = {r1}\) and \(x = {r2}\). Answer: <strong>{correct}</strong>"
    return q, sol, "Complete the square, then ± square root.", 2, opts, correct


def _cts_mcq_minimum_y():
    p = random.randint(-5, 5)
    k = random.randint(-6, 12)
    inner = f"(x + {p})" if p >= 0 else f"(x - {abs(p)})"
    k_str = _fmt_const(k)
    wrong_candidates = [k + 1, k - 1, -k, p, k + 2, k - 2]
    wrong = []
    for value in wrong_candidates:
        if value != k and value not in wrong:
            wrong.append(value)
        if len(wrong) == 3:
            break
    vals = wrong + [k]
    random.shuffle(vals)
    letters = "ABCD"
    correct = letters[vals.index(k)]
    opts = [f"{letters[i]}  y = {v}" for i, v in enumerate(vals)]
    q = rf"The minimum value of \(y = {inner}^2 {k_str}\) is:"
    sol = rf"Minimum at turning point \(({-p}, {k})\). Answer: <strong>{correct}</strong>"
    return q, sol, "The constant k is the minimum y-value.", 1, opts, correct


def _cts_mcq_square_constant():
    p = random.randint(2, 7)
    b = 2 * p
    correct = p * p
    wrong_candidates = [b, p, 2 * p * p, p * p + 1, p * p - 1]
    wrong = []
    for v in wrong_candidates:
        if v != correct and v not in wrong:
            wrong.append(v)
        if len(wrong) == 3:
            break
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = rf"Writing \(x^2 {_fmt_linear_x(b)} + \ldots\) as \((x + {p})^2 - \square\), what number fills the box (\(p^2\))?"
    sol = rf"\(p = {p}\), so \(p^2 = {correct}\). Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Subtract p², where p is half the x-coefficient.", 1, opts, correct_letter


def _cts_mcq_turning_point():
    p = random.randint(-5, 5)
    while p == 0:
        p = random.randint(-5, 5)
    k = random.choice([v for v in range(-6, 9) if v != 0])
    inner = f"(x + {p})" if p >= 0 else f"(x - {abs(p)})"
    tx = -p
    correct_str = f"({tx}, {k})"
    wrong = [f"({p}, {k})", f"({tx}, {-k})", f"({p}, {-k})"]
    forms = wrong + [correct_str]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct_str)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"The turning point of \(y = {inner}^2 {_fmt_const(k)}\) is:"
    sol = rf"Completed-square form gives turning point \(({tx}, {k})\). Answer: <strong>{correct_letter}</strong>"
    return q, sol, "For (x − h)² + k the turning point is (h, k).", 2, opts, correct_letter


def _cts_mcq_min_x():
    p = random.randint(2, 6)
    b = random.choice([1, -1]) * 2 * p
    c = random.randint(-8, 8)
    correct = -b // 2
    wrong_candidates = [b // 2, b, -b, correct + 1, correct - 1]
    wrong = []
    for v in wrong_candidates:
        if v != correct and v not in wrong:
            wrong.append(v)
        if len(wrong) == 3:
            break
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  x = {v}" for i, v in enumerate(vals)]
    q = rf"The minimum point of \(y = x^2 {_fmt_linear_x(b)} {_fmt_const(c)}\) occurs at \(x = \):"
    sol = rf"Minimum at \(x = -\dfrac{{b}}{{2}} = {correct}\). Answer: <strong>{correct_letter}</strong>"
    return q, sol, "The minimum is at x = −b/2 (half the x-coefficient, sign flipped).", 2, opts, correct_letter


def _cts_mcq_expand_c():
    p = random.randint(2, 6)
    k = random.randint(-6, 6)
    b = 2 * p
    c = p * p + k
    correct = c
    wrong_candidates = [p * p - k, k, p * p, c + 1, c - 1, 2 * p + k]
    wrong = []
    for v in wrong_candidates:
        if v != correct and v not in wrong:
            wrong.append(v)
        if len(wrong) == 3:
            break
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  c = {v}" for i, v in enumerate(vals)]
    q = rf"Expanding \((x + {p})^2 {_fmt_const(k)}\) gives \(x^2 {_fmt_linear_x(b)} + c\). What is \(c\)?"
    sol = (
        rf"\((x + {p})^2 = x^2 + {b}x + {p * p}\), then {_fmt_adjust_constant(k)}: "
        rf"\(c = {p * p} {_fmt_const(k)} = {c}\). Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Expand the bracket, then combine the constants.", 2, opts, correct_letter


_CTSQ_MCQ_POOL = [
    _cts_mcq_half_b,
    _cts_mcq_completed_form,
    _cts_mcq_solve_roots,
    _cts_mcq_minimum_y,
    _cts_mcq_square_constant,
    _cts_mcq_turning_point,
    _cts_mcq_min_x,
    _cts_mcq_expand_c,
]


def _cts_mcq_dispatch():
    """Randomly pick one of eight MCQ types (values randomised inside)."""
    return random.choice(_CTSQ_MCQ_POOL)()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _cts_f_half_coefficient,
    _cts_f_square_the_half,
    _cts_f_write_completed_form,
    _cts_f_expand_check,
    _cts_f_missing_constant,
]

_INTERMEDIATE = [
    _cts_i_complete_expression,
    _cts_i_solve_integer_roots,
    _cts_i_turning_point,
    _cts_i_solve_rearrange_first,
    _cts_i_negative_x_coeff,
]

_DIFFICULT = [
    _cts_d_solve_surd,
    _cts_d_decimal_roots,
    _cts_d_factor_a_out,
    _cts_d_minimum_value_word,
    _cts_d_exam_show_that,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_completing_the_square_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_pool(
            _CTSQ_MCQ_POOL, "completing_the_square", difficulty, count=4
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


def gcse_completing_the_square(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_completing_the_square_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "completing_the_square",
            options=opts, correct_answer=ans,
        )

    variants = gcse_completing_the_square_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "maths", "completing_the_square",
    )
