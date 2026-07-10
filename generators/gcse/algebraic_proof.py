"""
GCSE Maths – Algebraic Proof
5 foundational · 5 intermediate · 5 difficult · 9 MCQ (randomised each time)
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


def _ap_var():
    return random.choice(["n", "m", "k"])


def _ap_math(tex):
    """Wrap TeX for MathJax inline rendering."""
    return rf"\({tex}\)"


def _ap_math_strong(tex):
    return rf"<strong>\({tex}\)</strong>"


def _ap_counterexample_case():
    """Return (statement_tex, counter_n, counter_value, explanation)."""
    cases = [
        (
            r"n^2 > n",
            random.choice([0, 1]),
            None,
            r"One value where the inequality fails is enough.",
        ),
        (
            r"n^2 + 1 \text{ is prime}",
            random.choice([3, 5, 7, 8, 9]),
            None,
            r"Find one \(n\) where the expression is composite.",
        ),
        (
            r"n^2 \text{ is even}",
            random.choice([1, 3, 5]),
            None,
            r"Squares of odd integers are odd.",
        ),
        (
            r"2n + 1 \text{ is even}",
            random.randint(1, 6),
            None,
            r"Odd numbers are one more than a multiple of 2.",
        ),
    ]
    stmt, n_val, forced_val, hint_extra = random.choice(cases)
    if "prime" in stmt:
        val = n_val * n_val + 1
        if val % 2 == 0:
            factor = f"2 \\times {val // 2}"
        elif val % 3 == 0:
            factor = f"3 \\times {val // 3}"
        elif val % 5 == 0:
            factor = f"5 \\times {val // 5}"
        else:
            factor = "2 \\times 5" if val == 10 else f"\\text{{a non-trivial factor}}"
        expl = (
            rf"Try <strong>\(n = {n_val}\)</strong>: \({n_val}^2 + 1 = {val} = {factor}\), "
            r"which is not prime."
        )
    elif ">" in stmt:
        sq = n_val * n_val
        expl = (
            rf"Try <strong>\(n = {n_val}\)</strong>: \({n_val}^2 = {sq}\) and "
            rf"\({sq} \not> {n_val}\)."
        )
    elif "2n + 1" in stmt:
        expr = 2 * n_val + 1
        expl = (
            rf"Try <strong>\(n = {n_val}\)</strong>: \(2({n_val}) + 1 = {expr}\), which is odd, not even."
        )
    else:
        sq = n_val * n_val
        expl = (
            rf"Try <strong>\(n = {n_val}\)</strong>: \({n_val}^2 = {sq}\) is odd, not even."
        )
    return stmt, n_val, expl, hint_extra


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

def _ap_f_even_form():
    v = _ap_var()
    coef = random.choice([2, 4, 6, 8, 10])
    expr = f"{coef}{v}"
    q = (
        rf"Let <strong>\({v}\)</strong> be any integer. Explain why "
        rf"<strong>\({expr}\)</strong> is always <strong>even</strong>."
    )
    s = (
        rf"An even number is a multiple of 2. <strong>\({expr} = 2 \times {coef // 2}{v}\)</strong> "
        rf"has factor 2 for every integer \({v}\), so it is always even."
    )
    return q, s, "Even means divisible by 2 — write as 2 × (integer).", 2


def _ap_f_odd_form():
    v = _ap_var()
    offset = random.choice([1, 3, 5, 7, 9])
    expr = f"2{v} + {offset}"
    q = (
        rf"Let <strong>\({v}\)</strong> be any integer. Explain why "
        rf"<strong>\({expr}\)</strong> is always <strong>odd</strong>."
    )
    s = (
        r"Odd numbers are one more than an even number (or differ from an even number by an odd amount). "
        rf"<strong>\({expr}\)</strong> is not divisible by 2, so it is always odd."
    )
    return q, s, "Odd = 2n + 1 for some integer n.", 2


def _ap_f_expand_consecutive():
    v = _ap_var()
    a = random.randint(1, 5)
    b = a + random.randint(1, 4)
    q = (
        rf"Expand and simplify <strong>\(({v} + {a})({v} + {b})\)</strong> "
        rf"(two expressions in \({v}\) with constants {a} and {b})."
    )
    s = (
        rf"\(({v} + {a})({v} + {b}) = {v}^2 + {b}{v} + {a}{v} + {a * b} = "
        rf"{_ap_math_strong(f'{v}^2 + {a + b}{v} + {a * b}')}"
    )
    return q, s, "Multiply out — each term in the first bracket × each in the second.", 2


def _ap_f_sum_consecutive():
    v = _ap_var()
    gap = random.randint(1, 4)
    q = (
        rf"Write <strong>\({v} + ({v} + {gap})\)</strong> as a single expression and "
        r"state whether the result is always even or always odd."
    )
    parity = "even" if gap % 2 == 1 else "odd"
    s = (
        rf"\({v} + ({v} + {gap}) = 2{v} + {gap}\), which is always <strong>{parity}</strong>."
    )
    return q, s, "Combine like terms, then compare to 2n or 2n+1 forms.", 2


def _ap_f_counterexample():
    stmt, n_val, expl, hint_extra = _ap_counterexample_case()
    q = (
        rf"Show that the statement “<strong>\({stmt}\)</strong> for every integer "
        rf"<strong>\(n\)</strong>” is <strong>false</strong> by giving a counterexample."
    )
    s = rf"{expl} One counterexample disproves “always”."
    return q, s, hint_extra, 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _ap_i_square_difference():
    v = _ap_var()
    a = random.randint(1, 6)
    linear = 2 * a
    const = a * a
    q = (
        rf"Prove that for any integer <strong>\({v}\)</strong>, "
        rf"<strong>\(({v}+{a})^2 - {v}^2 = {linear}{v} + {const}\)</strong>."
    )
    s = (
        rf"Expand: \(({v}+{a})^2 = {v}^2 + {linear}{v} + {const}\)<br>"
        rf"So \(({v}+{a})^2 - {v}^2 = {_ap_math_strong(f'{linear}{v} + {const}')} ✓"
    )
    return q, s, "Expand the square, subtract v², simplify.", 3


def _ap_i_product_consecutive():
    v = _ap_var()
    gap = random.choice([1, 3, 5])
    q = (
        rf"Prove that <strong>\({v}({v} + {gap})\)</strong> is always <strong>even</strong> "
        rf"for any integer <strong>\({v}\)</strong>."
    )
    s = (
        rf"\({v}\) and \({v} + {gap}\) differ by {gap} (odd), so one is even and one is odd.<br>"
        rf"Either \({v} = 2k\) and the product is \(2k({v}+{gap})\), "
        rf"or \({v}+{gap} = 2k\) and the product is \({v} \times 2k\) — "
        rf"always a multiple of <strong>2</strong>."
    )
    return q, s, "Consecutive (or near-consecutive) integers include one even number.", 3


def _ap_i_multiple_of_three():
    v = _ap_var()
    m = random.choice([3, 4, 5, 6])
    a = random.randint(2, 7)
    b = random.randint(2, 8)
    expr = f"{a * m}{v} + {b * m}"
    q = (
        rf"Show that <strong>\({expr}\)</strong> is always a multiple of "
        rf"<strong>{m}</strong> for any integer <strong>\({v}\)</strong>."
    )
    s = (
        rf"Factorise: \({expr} = {m}({a}{v} + {b})\). "
        rf"Since \({a}{v} + {b}\) is an integer, <strong>\({expr}\) is a multiple of {m}</strong>."
    )
    return q, s, rf"Factor out {m} to show {m} × (integer).", 3


def _ap_i_sum_three_consecutive():
    v = _ap_var()
    k = random.choice([3, 5])
    total_const = k * (k - 1) // 2
    inner = (k - 1) // 2
    q = (
        rf"Prove that the sum of any <strong>{k} consecutive integers</strong> "
        rf"\({v}, {v}+1, \ldots, {v}+{k-1}\) is a multiple of <strong>{k}</strong>."
    )
    s = (
        rf"Sum = {k}{v} + {total_const} = {_ap_math_strong(f'{k}({v} + {inner})')}<br>"
        rf"So the sum is always a multiple of <strong>{k}</strong>."
    )
    return q, s, rf"Write {k} consecutive terms starting at {v}, then factor out {k}.", 4


def _ap_i_identity_expand():
    v = _ap_var()
    a = random.randint(2, 7)
    b = random.randint(1, 6)
    q = (
        rf"Expand <strong>\(({v} + {a})({v} + {b})\)</strong> and write the simplified result."
    )
    ab = a * b
    s = (
        rf"\({v}^2 + {a}{v} + {b}{v} + {ab} = "
        rf"{_ap_math_strong(f'{v}^2 + {a + b}{v} + {ab}')}"
    )
    return q, s, "FOIL / grid method — collect n², n, and constant terms.", 3


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

def _ap_d_n_squared_plus_n():
    v = _ap_var()
    gap = random.choice([1, 3, 5])
    q = (
        rf"Prove that <strong>\({v}({v} + {gap})\)</strong> is always <strong>even</strong> "
        rf"for any integer <strong>\({v}\)</strong>."
    )
    s = (
        rf"Expand or factorise: <strong>\({v}({v} + {gap}) = {v}^2 + {gap}{v}\)</strong><br>"
        rf"\({v}\) and \({v}+{gap}\) differ by {gap} (odd), so one is even → product is even."
    )
    return q, s, "Factorise first, then use the consecutive-integer argument.", 4


def _ap_d_odd_square():
    v = _ap_var()
    offset = random.choice([1, 3, 5])
    odd_expr = f"2{v} + {offset}"
    q = (
        rf"Let <strong>\({v}\)</strong> be an integer. Prove that "
        rf"<strong>\(({odd_expr})^2\)</strong> is always <strong>odd</strong>."
    )
    s = (
        rf"Expand: \(({odd_expr})^2 = 4{v}^2 + {4 * offset}{v} + {offset * offset}\). "
        rf"The first two terms are even; adding odd {offset * offset} gives an odd total.<br>"
        r"Equivalently, regroup to <strong>2 × (integer) + 1</strong>, so always odd."
    )
    return q, s, "Expand, regroup to 2×(integer) + 1.", 4


def _ap_d_even_sum_squares():
    v = _ap_var()
    step = random.choice([2, 4, 6])
    e1 = f"{step}{v}"
    e2 = f"{step}{v} + {step}"
    q = (
        rf"Prove that <strong>\(({e1})^2 + ({e2})^2\)</strong> is always <strong>even</strong> "
        rf"for any integer <strong>\({v}\)</strong>."
    )
    s = (
        rf"\(({step}{v})^2 = {step * step}{v}^2\) and "
        rf"\(({step}{v}+{step})^2 = {step * step}({v}+1)^2\)<br>"
        rf"Sum = {step * step}[{v}^2 + ({v}+1)^2] = "
        rf"{_ap_math_strong(f'{step * step} \\times (\\text{{integer}})')}<br>"
        rf"Since {step * step} has factor <strong>2</strong>, the sum is always even."
    )
    return q, s, "Expand evens — factor out a multiple of 4 (hence 2).", 4


def _ap_d_disprove_always_prime():
    cases = [
        (r"n^2 + 1 \text{ is prime}", lambda n: n * n + 1),
        (r"n^2 + 2 \text{ is prime}", lambda n: n * n + 2),
        (r"n^2 - 1 \text{ is prime for } n > 1", lambda n: n * n - 1),
    ]
    stmt, expr_fn = random.choice(cases)
    candidates = [3, 5, 7, 8, 9, 10, 11]
    random.shuffle(candidates)
    n_val = None
    val = None
    for cand in candidates:
        if stmt.startswith(r"n^2 - 1") and cand <= 1:
            continue
        trial = expr_fn(cand)
        if trial < 2:
            continue
        if trial % 2 == 0 or any(trial % p == 0 for p in (3, 5, 7, 11) if trial > p):
            n_val, val = cand, trial
            break
    if n_val is None:
        n_val, val = 8, expr_fn(8)
    if val % 2 == 0:
        factor_tex = rf"2 \times {val // 2}"
    elif val % 5 == 0:
        factor_tex = rf"5 \times {val // 5}"
    elif val % 3 == 0:
        factor_tex = rf"3 \times {val // 3}"
    else:
        factor_tex = rf"7 \times {val // 7}"
    q = (
        rf"The statement “<strong>\({stmt}\)</strong> for every positive integer "
        rf"<strong>\(n\)</strong>” is false. Prove it with a <strong>counterexample</strong>."
    )
    s = (
        rf"Try <strong>\(n = {n_val}\)</strong>: value = {val} = {_ap_math(factor_tex)}, not prime. "
        r"One failure is enough to disprove “for every \(n\)”."
    )
    return q, s, "Find one n where the expression is composite.", 3


def _ap_d_four_consecutive():
    v = _ap_var()
    k = random.choice([4, 8])
    total_const = k * (k - 1) // 2
    q = (
        rf"Prove that the sum of <strong>{k} consecutive integers</strong> "
        rf"\({v}, {v}+1, \ldots, {v}+{k-1}\) is always <strong>even</strong>."
    )
    s = (
        rf"Sum = {k}{v} + {total_const} = {_ap_math_strong(f'2({k // 2}{v} + {total_const // 2})')}<br>"
        rf"<strong>Factor 2</strong> → always even."
    )
    return q, s, rf"Write {k} consecutive terms starting at {v}, then collect and factor.", 4


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (9 — randomised)
# ══════════════════════════════════════════════════════════════════════════════

def _ap_mcq_even_odd():
    forms = [
        ("Always even", "2n"),
        ("Always odd", "2n + 1"),
        ("Always even", "2n + 2"),
        ("Always odd", "2n - 1"),
    ]
    pick = random.choice(forms)
    correct_label, correct_expr = pick
    wrong = [f for f in forms if f != pick]
    random.shuffle(wrong)
    letters = "ABCD"
    opts_list = [pick] + wrong[:3]
    random.shuffle(opts_list)
    correct_letter = letters[opts_list.index(pick)]
    opts = [f"{letters[i]}  {opts_list[i][1]} is {opts_list[i][0]}" for i in range(4)]
    q = rf"For any integer \(n\), which expression is <strong>{correct_label.lower()}</strong>?"
    sol = rf"<strong>{correct_expr}</strong> — {correct_label.lower()}. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Even = 2n; odd = 2n+1.", 2, opts, correct_letter


def _ap_mcq_square_diff():
    correct = r"\(2n + 1\)"
    wrong = [r"\(2n\)", r"\(n + 1\)", r"\(n^2 + 1\)"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"\((n+1)^2 - n^2\) simplifies to:"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Expand (n+1)² and subtract n².", 2, opts, correct_letter


def _ap_mcq_consecutive_product():
    correct = "It is always even"
    wrong = [
        "It is always odd",
        "It is always a multiple of 3",
        "It can be prime only",
    ]
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = r"For any integer \(n\), what is true about <strong>\(n(n+1)\)</strong>?"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Consecutive integers — one is even.", 2, opts, correct_letter


def _ap_mcq_counterexample():
    correct = r"\(n = 3\) gives \(n^2 + 1 = 10\) (not prime)"
    wrong = [
        r"\(n = 1\) proves the statement for all \(n\)",
        r"\(n = 2\) shows \(n^2 + 1\) is never prime",
        r"No counterexample exists",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Which disproves “\(n^2 + 1\) is prime for every positive integer \(n\)”?"
    sol = rf"<strong>{correct_letter}</strong>."
    return q, sol, "One failing example is enough.", 2, opts, correct_letter


def _ap_mcq_sum_consecutive():
    correct = r"\(2n + 1\)"
    wrong = [r"\(2n\)", r"\(n^2 + 1\)", r"\(2n + 2\)"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"For any integer \(n\), \(n + (n + 1)\) simplifies to:"
    sol = (
        rf"Combine like terms: \(n + n + 1 = 2n + 1\), which is always odd. "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Add the two consecutive terms.", 2, opts, correct_letter


def _ap_mcq_three_consecutive():
    correct = r"\(3n\)"
    wrong = [r"\(3n + 1\)", r"\(n^3\)", r"\(3n^2\)"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"\((n - 1) + n + (n + 1)\) simplifies to:"
    sol = (
        rf"Collect terms: \(3n\), so the sum is always a multiple of 3. "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Three consecutive integers always sum to 3n.", 2, opts, correct_letter


def _ap_mcq_factorise_even():
    correct = r"\(n(n + 1)\)"
    wrong = [r"\(n^2 + 1\)", r"\((n + 1)^2\)", r"\(2n\)"]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Factorise \(n^2 + n\)."
    sol = (
        rf"Take out common factor \(n\): <strong>\(n(n + 1)\)</strong>, which is always even. "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Factorise first, then explain using consecutive integers.", 2, opts, correct_letter


def _ap_mcq_odd_square():
    correct = "Always odd"
    wrong = ["Always even", "Always a multiple of 4", "Sometimes prime only"]
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = r"For any integer \(n\), \((2n + 1)^2\) is:"
    sol = (
        rf"Expand: \(4n^2 + 4n + 1 = 2(2n^2 + 2n) + 1\) — one more than an even number, so always odd. "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Square of an odd number is always odd.", 2, opts, correct_letter


def _ap_mcq_proof_valid():
    correct = r"Let \(n\) be any integer and show the algebra works for all \(n\)"
    wrong = [
        r"Test \(n = 1, 2, 3\) and stop when they all work",
        "Draw a graph and read off one point",
        "Assume the statement is false and stop",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Which is a valid way to prove a result for <strong>all</strong> integers?"
    sol = (
        rf"A proof must work for every integer, not just a few examples. "
        rf"Answer: <strong>{correct_letter}</strong>"
    )
    return q, sol, "Proof uses algebra for general n; testing examples alone is not enough.", 1, opts, correct_letter


def _ap_mcq_dispatch():
    return random.choice([
        _ap_mcq_even_odd,
        _ap_mcq_square_diff,
        _ap_mcq_consecutive_product,
        _ap_mcq_counterexample,
        _ap_mcq_sum_consecutive,
        _ap_mcq_three_consecutive,
        _ap_mcq_factorise_even,
        _ap_mcq_odd_square,
        _ap_mcq_proof_valid,
    ])()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _ap_f_even_form,
    _ap_f_odd_form,
    _ap_f_expand_consecutive,
    _ap_f_sum_consecutive,
    _ap_f_counterexample,
]

_INTERMEDIATE = [
    _ap_i_square_difference,
    _ap_i_product_consecutive,
    _ap_i_multiple_of_three,
    _ap_i_sum_three_consecutive,
    _ap_i_identity_expand,
]

_DIFFICULT = [
    _ap_d_n_squared_plus_n,
    _ap_d_odd_square,
    _ap_d_even_sum_squares,
    _ap_d_disprove_always_prime,
    _ap_d_four_consecutive,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_algebraic_proof_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_fn(
            _ap_mcq_dispatch, "algebraic_proof", difficulty, count=4
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


def gcse_algebraic_proof(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_algebraic_proof_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "algebraic_proof",
            options=opts, correct_answer=ans,
        )

    variants = gcse_algebraic_proof_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "maths", "algebraic_proof",
    )
