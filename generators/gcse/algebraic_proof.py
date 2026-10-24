"""
GCSE Maths – Algebraic Proof
5 foundational · 5 intermediate · 5 difficult · 17 MCQ generators in three band pools (randomised each time)
Graded practice: expand/counterexample use algebraic/number/keyword fields;
prove-that variants use ordered proof_steps (Plan C).
"""
import random
from generators.shared.utils import (
    make_problem,
    graded_answer_number,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.answer_checkers import FORM_EXPANDED
from generators.shared.verify_hook import verifies
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_pool,
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
            1,
            None,
            r"One value where the inequality fails is enough.",
        ),
        (
            r"n^2 + 1 \text{ is prime}",
            3,
            None,
            r"Find one \(n\) where the expression is composite.",
        ),
        (
            r"n^2 \text{ is even}",
            1,
            None,
            r"Squares of odd integers are odd.",
        ),
        (
            r"2n + 1 \text{ is even}",
            1,
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


def _ap_expand_quadratic(v, a, b):
    """Canonical expanded form v^2 + (a+b)v + ab for algebraic checking."""
    linear = a + b
    parts = [f'{v}^2']
    if linear == 1:
        parts.append(f'+ {v}')
    elif linear == -1:
        parts.append(f'- {v}')
    elif linear > 0:
        parts.append(f'+ {linear}{v}')
    elif linear < 0:
        parts.append(f'- {-linear}{v}')
    product = a * b
    if product > 0:
        parts.append(f'+ {product}')
    elif product < 0:
        parts.append(f'- {-product}')
    return ' '.join(parts)


def _ap_algebraic_answer(expr, format_hint=None, form=None):
    payload = {'type': 'algebraic', 'value': str(expr)}
    if form:
        payload['form'] = form
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _ap_fields_answer(values, labels, field_types):
    return {
        'type': 'number_fields',
        'values': tuple(values),
        'labels': tuple(labels),
        'field_types': tuple(field_types),
    }


def _ap_proof_steps_answer(steps, distractors, *, format_hint='Put the proof steps in the correct order', after=None):
    bank = [{'id': f's{i + 1}', 'text': text} for i, text in enumerate(steps)]
    for j, text in enumerate(distractors):
        bank.append({'id': f'd{j + 1}', 'text': text})
    random.shuffle(bank)
    required = tuple(f's{i + 1}' for i in range(len(steps)))
    return proof_steps_answer(
        required,
        bank,
        order_matters=True,
        format_hint=format_hint,
        after=after,
    )


def _ap_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'maths', 'algebraic_proof',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        extra = problem_extra_from_graded_answer(raw)
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'algebraic_proof', **extra
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='ap_proof')
def _ap_f_even_form():
    v = _ap_var()
    coef = random.choice([2, 4, 6, 8, 10])
    expr = f"{coef}{v}"
    half = coef // 2
    q = (
        rf"Let <strong>\({v}\)</strong> be any integer. Explain why "
        rf"<strong>\({expr}\)</strong> is always <strong>even</strong>."
    )
    s = (
        rf"An even number is a multiple of 2. <strong>\({expr} = 2 \times {half}{v}\)</strong> "
        rf"has factor 2 for every integer \({v}\), so it is always even."
    )
    return q, s, "Even means divisible by 2 — write as 2 × (integer).", 2, _ap_proof_steps_answer(
        (
            "An even number is a multiple of 2 (divisible by 2).",
            rf"For any integer {v}, write {expr} = 2 × ({half}{v}).",
            rf"The bracket ({half}{v}) is an integer.",
            f"Therefore {expr} has factor 2 and is always even.",
        ),
        (
            f"{expr} is odd when {v} is odd.",
            "Only numbers ending in 0, 2, 4, 6, or 8 in the ones column are even.",
            f"{expr} = {v} + {coef}, so it has the same parity as {v}.",
            f"{expr} is always odd because {coef} is even.",
        ),
        # The definition and the rewriting are separate facts; the bracket remark needs the rewriting.
        after={2: (), 3: (2,), 4: (1, 2, 3)},
    )


@verifies('alg', task='ap_proof')
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
    return q, s, "Odd = 2n + 1 for some integer n.", 2, _ap_proof_steps_answer(
        (
            f"For any integer {v}, 2{v} is always even.",
            f"Adding an odd number ({offset}) to an even number gives an odd result.",
            f"So {expr} is always odd.",
        ),
        (
            f"{expr} is even when {v} is even.",
            f"{expr} is a multiple of 3 for every integer {v}.",
            f"Because {expr} contains 2{v}, it is always even.",
            f"Odd numbers must end in 1, 3, 5, 7, or 9 in the ones column only.",
        ),
        # "2v is even" and "even + odd is odd" are separate facts; the conclusion needs both.
        after={2: (), 3: (1, 2)},
    )


@verifies('alg', task='expand')
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
    expanded = _ap_expand_quadratic(v, a, b)
    return q, s, "Multiply out — each term in the first bracket × each in the second.", 2, _ap_algebraic_answer(
        expanded,
        format_hint='Enter the simplified expression, e.g. n^2 + 5n + 6',
        form=FORM_EXPANDED,
    )


@verifies('alg', task='ap_parity_fields')
def _ap_f_sum_consecutive():
    v = _ap_var()
    gap = random.randint(1, 4)
    q = (
        rf"Write <strong>\({v} + ({v} + {gap})\)</strong> as a single expression, then "
        rf"state whether the result is always <strong>even</strong> or always <strong>odd</strong>."
    )
    parity = "odd" if gap % 2 == 1 else "even"      # 2v + gap has the parity of gap
    s = (
        rf"\({v} + ({v} + {gap}) = 2{v} + {gap}\), which is always <strong>{parity}</strong>."
    )
    return q, s, "Combine like terms, then compare to 2n or 2n+1 forms.", 2, _ap_fields_answer(
        (f'2{v} + {gap}', parity),
        ('Simplified expression', 'Always even or odd?'),
        ('algebraic', 'keyword'),
    )


@verifies('alg', task='counterexample')
def _ap_f_counterexample():
    stmt, n_val, expl, hint_extra = _ap_counterexample_case()
    q = (
        rf"Show that the statement “<strong>\({stmt}\)</strong> for every integer "
        rf"<strong>\(n\)</strong>” is <strong>false</strong> by giving a counterexample.<br>"
        rf"Enter the <strong>smallest positive integer</strong> value of <strong>\(n\)</strong> that disproves the statement."
    )
    s = rf"{expl} One counterexample disproves “always”."
    return q, s, hint_extra, 2, graded_answer_number(n_val)


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='ap_proof')
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
    return q, s, "Expand the square, subtract v², simplify.", 3, _ap_proof_steps_answer(
        (
            rf"Expand ({v}+{a})² = {v}² + {linear}{v} + {const}.",
            rf"Subtract {v}²: ({v}+{a})² − {v}² = {linear}{v} + {const}.",
            rf"This matches {linear}{v} + {const} as required.",
        ),
        (
            rf"({v}+{a})² − {v}² = {v}² + {const} after expanding.",
            rf"Expand ({v}+{a})² = {v}² + {a}{v} + {const}.",
            rf"Subtract {v}² to get {linear}{v} − {const}.",
            rf"Use the difference of two squares: ({v}+{a})² − {v}² = {a}² only.",
        ),
    )


@verifies('alg', task='ap_proof')
def _ap_i_product_consecutive():
    v = _ap_var()
    gap = random.choice([1, 3, 5])
    q = (
        rf"Prove that <strong>\({v}({v} + {gap})\)</strong> is always <strong>even</strong> "
        rf"for any integer <strong>\({v}\)</strong>."
    )
    s = (
        rf"\({v}\) and \({v} + {gap}\) differ by {gap} (odd), so one is even and one is odd.<br>"
        rf"Either \({v} = 2j\) and the product is \(2j({v}+{gap})\), "
        rf"or \({v}+{gap} = 2j\) and the product is \({v} \times 2j\) — "
        rf"always a multiple of <strong>2</strong>."
    )
    return q, s, "Consecutive (or near-consecutive) integers include one even number.", 3, _ap_proof_steps_answer(
        (
            rf"{v} and ({v} + {gap}) differ by {gap} (an odd number).",
            "So one of the two integers is even and the other is odd.",
            rf"If {v} is even, write {v} = 2j; then the product is 2j({v} + {gap}).",
            rf"If ({v} + {gap}) is even, the product is {v} × 2j for some integer j.",
            "In either case the product has factor 2, so it is always even.",
        ),
        (
            rf"Both {v} and ({v} + {gap}) are odd, so the product is always odd.",
            "The product of two odd numbers is always even.",
            rf"Expand to {v}² + {gap}{v}; this is always a multiple of 4, not 2.",
            rf"Because {gap} is odd, both integers must be even.",
        ),
        # The two cases (v even, v + gap even) are independent; each needs the odd/even step, and the end needs both.
        after={4: (2,), 5: (3, 4)},
    )


@verifies('alg', task='ap_proof')
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
    return q, s, rf"Factor out {m} to show {m} × (integer).", 3, _ap_proof_steps_answer(
        (
            rf"Factorise: {expr} = {m}({a}{v} + {b}).",
            rf"({a}{v} + {b}) is an integer for any integer {v}.",
            rf"Therefore {expr} is always a multiple of {m}.",
        ),
        (
            rf"Divide {expr} by {m} and get a remainder of 1 for some {v}.",
            rf"({a}{v} + {b}) is not always an integer.",
            rf"Factorise to ({a}{v} + {b}) + {m}, which is not a multiple of {m}.",
            rf"Only multiples of {a} are multiples of {m}.",
        ),
    )


@verifies('alg', task='ap_proof')
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
    return q, s, rf"Write {k} consecutive terms starting at {v}, then factor out {k}.", 4, _ap_proof_steps_answer(
        (
            rf"Sum the {k} consecutive terms: {k}{v} + {total_const}.",
            rf"Factorise: {k}{v} + {total_const} = {k}({v} + {inner}).",
            rf"({v} + {inner}) is an integer.",
            rf"Therefore the sum is always a multiple of {k}.",
        ),
        (
            rf"The sum equals {v} + {total_const} after combining like terms.",
            rf"Factorise to {k}({v} + {total_const}), which is not always a multiple of {k}.",
            rf"Only the middle term {v} + {inner} matters, so the sum is always {inner}.",
            rf"Consecutive integers always sum to an even number, not a multiple of {k}.",
        ),
    )


@verifies('alg', task='expand')
def _ap_i_identity_expand():
    v = _ap_var()
    a = random.randint(2, 7)
    b = random.randint(1, 6)
    q = (
        rf"Expand <strong>\(({v} + {a})({v} + {b})\)</strong> and write the simplified result."
    )
    ab = a * b
    expanded = _ap_expand_quadratic(v, a, b)
    s = (
        rf"\({v}^2 + {a}{v} + {b}{v} + {ab} = "
        rf"{_ap_math_strong(f'{v}^2 + {a + b}{v} + {ab}')}"
    )
    return q, s, "FOIL / grid method — collect n², n, and constant terms.", 3, _ap_algebraic_answer(
        expanded,
        format_hint='Enter the simplified expression, e.g. m^2 + 7m + 12',
        form=FORM_EXPANDED,
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='ap_proof')
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
    return q, s, "Factorise first, then use the consecutive-integer argument.", 4, _ap_proof_steps_answer(
        (
            rf"{v} and ({v} + {gap}) differ by {gap} (an odd number).",
            "So one of the two integers is even and the other is odd.",
            rf"If {v} is even, write {v} = 2j; then the product is 2j({v} + {gap}).",
            rf"If ({v} + {gap}) is even, the product is {v} × 2j for some integer j.",
            "In either case the product has factor 2, so it is always even.",
        ),
        (
            rf"Expand to {v}² + {gap}{v}; squares are always even, so the product is even.",
            rf"Both {v} and ({v} + {gap}) are odd, so the product is always odd.",
            rf"Because {gap} is even, both integers must be even.",
            rf"Factorise to {gap}({v} + 1), which is always a multiple of {gap} only.",
        ),
        # The two cases (v even, v + gap even) are independent; each needs the odd/even step, and the end needs both.
        after={4: (2,), 5: (3, 4)},
    )


@verifies('alg', task='ap_proof')
def _ap_d_odd_square():
    v = _ap_var()
    offset = random.choice([1, 3, 5])
    odd_expr = f"2{v} + {offset}"
    const_sq = offset * offset
    q = (
        rf"Let <strong>\({v}\)</strong> be an integer. Prove that "
        rf"<strong>\(({odd_expr})^2\)</strong> is always <strong>odd</strong>."
    )
    s = (
        rf"Expand: \(({odd_expr})^2 = 4{v}^2 + {4 * offset}{v} + {const_sq}\). "
        rf"The first two terms are even; adding odd {const_sq} gives an odd total.<br>"
        r"Equivalently, regroup to <strong>2 × (integer) + 1</strong>, so always odd."
    )
    return q, s, "Expand, regroup to 2×(integer) + 1.", 4, _ap_proof_steps_answer(
        (
            rf"Expand ({odd_expr})² = 4{v}² + {4 * offset}{v} + {const_sq}.",
            f"The terms 4{v}² and {4 * offset}{v} are even.",
            f"Adding the odd constant {const_sq} gives an odd total.",
            "Equivalently regroup to 2 × (integer) + 1, so the square is always odd.",
        ),
        (
            f"({odd_expr})² is even because it contains a factor 2{v}.",
            f"All squares are even, so ({odd_expr})² is even.",
            f"Expand to 4{v}² + {const_sq} only; both terms are even.",
            f"Odd numbers squared are always multiples of 4.",
        ),
    )


@verifies('alg', task='ap_proof')
def _ap_d_even_sum_squares():
    v = _ap_var()
    step = random.choice([2, 4, 6])
    e1 = f"{step}{v}"
    e2 = f"{step}{v} + {step}"
    step_sq = step * step
    q = (
        rf"Prove that <strong>\(({e1})^2 + ({e2})^2\)</strong> is always <strong>even</strong> "
        rf"for any integer <strong>\({v}\)</strong>."
    )
    s = (
        rf"\(({step}{v})^2 = {step_sq}{v}^2\) and "
        rf"\(({step}{v}+{step})^2 = {step_sq}({v}+1)^2\)<br>"
        rf"Sum = {step_sq}[{v}^2 + ({v}+1)^2] = "
        rf"{_ap_math_strong(f'{step_sq} \\times (\\text{{integer}})')}<br>"
        rf"Since {step_sq} has factor <strong>2</strong>, the sum is always even."
    )
    return q, s, "Expand evens — factor out a multiple of 4 (hence 2).", 4, _ap_proof_steps_answer(
        (
            rf"({step}{v})² = {step_sq}{v}² and ({step}{v} + {step})² = {step_sq}({v} + 1)².",
            rf"Sum = {step_sq}[{v}² + ({v} + 1)²].",
            rf"{step_sq} has factor 2 because {step} is even.",
            "Therefore the sum is always even.",
        ),
        (
            rf"Both squares are odd, so their sum is always odd.",
            rf"Sum = {step_sq}{v}² + {step_sq} only; this is always a multiple of {step_sq}, not 2.",
            rf"({step}{v})² and ({step}{v} + {step})² are both multiples of {step} only.",
            "The sum of two even squares is always odd.",
        ),
    )


@verifies('alg', task='counterexample')
def _ap_d_disprove_always_prime():
    cases = [
        (r"n^2 + 1 \text{ is prime}", lambda n: n * n + 1),
        (r"n^2 + 2 \text{ is prime}", lambda n: n * n + 2),
        (r"n^2 - 1 \text{ is prime for } n > 1", lambda n: n * n - 1),
    ]
    stmt, expr_fn = random.choice(cases)
    # The answer box takes one number, so the question asks for the smallest counterexample (unique).
    n_val = 2 if stmt.startswith(r"n^2 - 1") else 1
    while True:
        val = expr_fn(n_val)
        if val >= 4 and any(val % p == 0 for p in range(2, int(val ** 0.5) + 1)):
            break
        n_val += 1
    p_small = next(p for p in range(2, val + 1) if val % p == 0)
    factor_tex = rf"{p_small} \times {val // p_small}"
    q = (
        rf"The statement “<strong>\({stmt}\)</strong> for every positive integer "
        rf"<strong>\(n\)</strong>” is false. Give a <strong>counterexample</strong>: "
        rf"enter the <strong>smallest</strong> value of <strong>\(n\)</strong> that disproves it."
    )
    s = (
        rf"Try <strong>\(n = {n_val}\)</strong>: value = {val} = {_ap_math(factor_tex)}, not prime. "
        r"One failure is enough to disprove “for every \(n\)”."
    )
    return q, s, "Find one n where the expression is composite.", 3, graded_answer_number(n_val)


@verifies('alg', task='ap_proof')
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
    return q, s, rf"Write {k} consecutive terms starting at {v}, then collect and factor.", 4, _ap_proof_steps_answer(
        (
            rf"Sum of {k} consecutive integers = {k}{v} + {total_const}.",
            rf"Factorise: {k}{v} + {total_const} = 2({k // 2}{v} + {total_const // 2}).",
            f"The bracket ({k // 2}{v} + {total_const // 2}) is an integer.",
            "Therefore the sum is always even.",
        ),
        (
            rf"The sum equals {v} + {total_const} after combining like terms.",
            rf"Factorise to {k}({v} + {total_const}), which is not always even.",
            rf"Consecutive integers always sum to a multiple of {k}, not necessarily even.",
            rf"Because {k} is even, the sum is always a multiple of {k} only, not 2.",
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (three band pools, randomised)
# ══════════════════════════════════════════════════════════════════════════════

@verifies('alg', task='ap_always')
def _ap_mcq_even_odd():
    """Which expression is always even (or odd)? Exactly one option has the stated parity."""
    evens = ["2n", "2n + 2", "4n", "6n", "2n - 4"]
    odds = ["2n + 1", "2n - 1", "2n + 3", "4n + 1", "6n - 3"]
    want_even = random.choice([True, False])
    right_pool, wrong_pool = (evens, odds) if want_even else (odds, evens)
    correct_expr = random.choice(right_pool)
    exprs = random.sample(wrong_pool, 3) + [correct_expr]
    random.shuffle(exprs)
    letters = "ABCD"
    correct_letter = letters[exprs.index(correct_expr)]
    opts = [rf"{letters[i]}  \({exprs[i]}\)" for i in range(4)]
    word = "even" if want_even else "odd"
    q = rf"For any integer \(n\), which expression is always <strong>{word}</strong>?"
    sol = rf"<strong>\({correct_expr}\)</strong> is always {word}. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Even = 2n; odd = 2n+1.", 2, opts, correct_letter


@verifies('alg', task='simplify', form=None)
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


@verifies('alg', task='ap_prop')
def _ap_mcq_consecutive_product():
    correct = "It is always even"
    wrong = [
        "It is always odd",
        "It is always a multiple of 3",
        "It is always prime",
    ]
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = r"For any integer \(n\), what is true about <strong>\(n(n+1)\)</strong>?"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Consecutive integers: one of them is even.", 2, opts, correct_letter


@verifies('alg', task='ap_counter_mcq')
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


@verifies('alg', task='simplify', form=None)
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


@verifies('alg', task='simplify', form=None)
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
    return q, sol, "Collect the n terms, then collect the number terms.", 2, opts, correct_letter


@verifies('alg', task='factorise')
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
    return q, sol, "Look for a factor that both terms share.", 2, opts, correct_letter


@verifies('alg', task='ap_prop')
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


@verifies('alg', task='keyed_text', text='let n be any integer and show the algebra works for all n')
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


def _ap_options(correct, wrong):
    """Shuffle ``correct`` among ``wrong`` and return (lettered options, correct letter)."""
    forms = list(wrong) + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    return [f"{letters[i]}  {f}" for i, f in enumerate(forms)], letters[forms.index(correct)]


def _ap_is_prime(v):
    return v > 1 and all(v % d for d in range(2, int(v ** 0.5) + 1))


@verifies('alg', task='ap_consecutive_form')
def _ap_mcq_consecutive_form():
    """Which pair of expressions is always two consecutive odd (or even) numbers? Exactly one pair is."""
    kind = random.choice(["odd", "even"])
    if kind == "odd":
        correct = r"\(2n + 1\) and \(2n + 3\)"
        pool = [
            r"\(2n\) and \(2n + 1\)",
            r"\(2n + 1\) and \(2n + 2\)",
            r"\(n\) and \(n + 2\)",
            r"\(2n + 1\) and \(2n + 5\)",
        ]
        sol = (
            r"An odd number is \(2n + 1\). The next odd number is 2 more, \(2n + 3\)."
        )
    else:
        correct = r"\(2n\) and \(2n + 2\)"
        pool = [
            r"\(2n\) and \(2n + 1\)",
            r"\(2n + 1\) and \(2n + 3\)",
            r"\(n\) and \(n + 2\)",
            r"\(2n\) and \(2n + 4\)",
        ]
        sol = r"An even number is \(2n\). The next even number is 2 more, \(2n + 2\)."
    opts, letter = _ap_options(correct, random.sample(pool, 3))
    q = rf"Which pair of expressions always represents two consecutive <strong>{kind}</strong> numbers, for any integer \(n\)?"
    sol += (
        r" Consecutive odd or even numbers differ by 2, and the form \(2n\) or \(2n + 1\) keeps the parity "
        rf"for every integer \(n\). Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Write the first number as 2n or 2n + 1, then add 2.", 2, opts, letter


@verifies('alg', task='ap_prop')
def _ap_mcq_sum_two_odds():
    """The sum of two consecutive odd numbers is always a multiple of 4 (and not always of 8)."""
    correct = "Always a multiple of 4"
    wrong = ["Always odd", "Always a multiple of 3", "Always a multiple of 8"]
    opts, letter = _ap_options(correct, wrong)
    q = (
        r"The sum of two consecutive odd numbers is \((2n + 1) + (2n + 3)\). "
        r"For any integer \(n\), this sum is:"
    )
    sol = (
        r"\((2n + 1) + (2n + 3) = 4n + 4 = 4(n + 1)\), so it is always a multiple of 4. "
        r"It is not always a multiple of 8: when \(n = 0\) the sum is 4. "
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Collect like terms, then factorise.", 2, opts, letter


@verifies('alg', task='ap_mult_expr')
def _ap_mcq_multiple_expression():
    """Which expression is always a multiple of k (k varies)? Exactly one is."""
    k = random.choice([3, 4, 5, 6, 7, 9])
    j = random.choice([1, 2, 3])
    sign = random.choice(["+", "-", "factorised"])
    if sign == "factorised":
        correct = rf"\({k}(n + {j})\)"
        why = rf"{correct} is {k} times the whole number \(n + {j}\)"
    else:
        correct = rf"\({k}n {sign} {k * j}\)"
        why = rf"\({k}n {sign} {k * j} = {k}(n {sign} {j})\), which is {k} times a whole number"
    pool = [
        rf"\(n + {k}\)",
        rf"\({k}n + {k // 2}\)",
        rf"\(n^2 + {k}\)",
        rf"\(n(n + {k})\)",
    ]
    opts, letter = _ap_options(correct, random.sample(pool, 3))
    q = rf"For any integer \(n\), which expression is always a multiple of <strong>{k}</strong>?"
    sol = (
        rf"{why} for every integer \(n\), so it is always a multiple of {k}. "
        rf"Each other expression fails for some \(n\) (try \(n = 1\)). Answer: <strong>{letter}</strong>"
    )
    return q, sol, f"A multiple of {k} has {k} as a factor. Test n = 1 on each option.", 2, opts, letter


_AP_PRIME_CLAIMS = [
    (r"2n + 1", lambda n: 2 * n + 1),
    (r"n^2 + n + 1", lambda n: n * n + n + 1),
    (r"6n + 1", lambda n: 6 * n + 1),
]


@verifies('alg', task='ap_counter_value')
def _ap_mcq_counterexample_value():
    """Which value of n disproves 'f(n) is prime for every positive integer n'? Exactly one does."""
    tex, f = random.choice(_AP_PRIME_CLAIMS)
    fails = [n for n in range(2, 11) if not _ap_is_prime(f(n))]
    passes = [n for n in range(1, 11) if _ap_is_prime(f(n))]
    key = random.choice(fails)
    values = sorted(random.sample(passes, 3) + [key])
    opts = [rf"{'ABCD'[i]}  \(n = {v}\)" for i, v in enumerate(values)]
    letter = "ABCD"[values.index(key)]
    total = f(key)
    d = next(d for d in range(2, total) if total % d == 0)
    q = rf"Which value of \(n\) is a counterexample to the claim that \({tex}\) is prime for every positive integer \(n\)?"
    sol = (
        rf"When \(n = {key}\), \({tex}\) is {total}, and {total} = {d} × {total // d}, so it is not prime. "
        rf"Each other value gives a prime. Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Substitute each value of n and check whether the result is prime.", 2, opts, letter


@verifies('alg', task='ap_mult_expr')
def _ap_mcq_multiple_of_eight():
    correct = r"\((2n + 1)^2 - 1\)"
    wrong = [r"\((2n + 1)^2 + 1\)", r"\((2n)^2 + 4\)", r"\((2n + 2)^2 - 4\)"]
    opts, letter = _ap_options(correct, wrong)
    q = r"For any integer \(n\), which expression is always a multiple of <strong>8</strong>?"
    sol = (
        r"\((2n + 1)^2 - 1 = 4n^2 + 4n = 4n(n + 1)\). The product \(n(n + 1)\) of two consecutive integers is even, "
        r"so it is \(2m\) for some integer \(m\), and \(4n(n + 1) = 8m\). "
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Expand, factorise, then use the fact that n(n + 1) is always even.", 3, opts, letter


@verifies('alg', task='simplify', form=None)
def _ap_mcq_odd_squares_difference():
    correct = r"\(8(n + 1)\)"
    wrong = [r"\(8\)", r"\(12n + 8\)", r"\(4n + 4\)"]
    opts, letter = _ap_options(correct, wrong)
    q = (
        r"The difference between the squares of two consecutive odd numbers is \((2n + 3)^2 - (2n + 1)^2\). "
        r"This simplifies to:"
    )
    sol = (
        r"\((2n + 3)^2 = 4n^2 + 12n + 9\) and \((2n + 1)^2 = 4n^2 + 4n + 1\). "
        r"Subtracting gives \(8n + 8 = 8(n + 1)\), so the difference is always a multiple of 8. "
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Expand both brackets carefully, including the middle term, then subtract.", 3, opts, letter


def _ap_find_error_lines(k, scenario):
    """The four lines of working for (2n + k)^2 - k^2, with the first mistake in line ``scenario`` (0 for none).

    The lines after a mistake follow correctly from the wrong line, so only one step is wrong.
    """
    k2 = k * k
    l1 = rf"(2n + {k})^2 - {k2}"
    l2 = rf"= 4n^2 + {4 * k}n + {k2} - {k2}"
    l3 = rf"= 4n^2 + {4 * k}n"
    l4 = rf"= 4n(n + {k})"
    if scenario == 2:       # the middle term of the expansion is halved
        l2 = rf"= 4n^2 + {2 * k}n + {k2} - {k2}"
        l3 = rf"= 4n^2 + {2 * k}n"
        l4 = rf"= 2n(2n + {k})"
    elif scenario == 3:     # the n is lost from the middle term
        l3 = rf"= 4n^2 + {4 * k}"
        l4 = rf"= 4(n^2 + {k})"
    elif scenario == 4:     # factorising: 4n(n + k) written as 4(n + k)
        l4 = rf"= 4(n + {k})"
    return [l1, l2, l3, l4]


_AP_ERROR_SCENARIOS = [
    (0, "no mistake", "Every line follows from the line before it, so there is no mistake."),
    (2, "line 2", r"In line 2 the middle term of the expansion should be \(2 \times 2n \times {k} = {m}n\)."),
    (3, "line 3", r"In line 3 the \(n\) has been lost from the middle term \({m}n\)."),
    (4, "line 4", r"In line 4 the factor \(n\) has been lost: \(4n^2 + {m}n = 4n(n + {k})\)."),
]


@verifies('alg', task='ap_find_error')
def _ap_mcq_find_error():
    """Spot the first mistake (or none) in four lines of working. The lines are re-checked with algebra."""
    scenario, _, why = random.choice(_AP_ERROR_SCENARIOS)
    k = random.choice([1, 3, 5])
    lines = _ap_find_error_lines(k, scenario)
    shown = "<br>".join(rf"Line {i + 1}: \({ln}\)" for i, ln in enumerate(lines))
    q = (
        "A student is showing that the expression in line 1 is a multiple of 4. "
        "Which line of the working contains the first mistake, if any?<br>" + shown
    )
    opts = ["A  Line 2", "B  Line 3", "C  Line 4", "D  There is no mistake"]
    letter = {2: "A", 3: "B", 4: "C", 0: "D"}[scenario]
    sol = (
        why.format(k=k, m=4 * k) + " Check each line by expanding it and comparing it with the line before. "
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Expand line 1, then compare each line with the one before it.", 3, opts, letter


_AP_PROPERTY_EXPRESSIONS = [
    (r"n^2 + (n + 1)^2", lambda n: n * n + (n + 1) ** 2,
     r"\(n^2 + (n + 1)^2 = 2n^2 + 2n + 1 = 2(n^2 + n) + 1\), one more than an even number."),
    (r"3n + 1", lambda n: 3 * n + 1,
     r"When \(n = 0\), \(3n + 1 = 1\) (odd), and when \(n = 1\), \(3n + 1 = 4\) (even)."),
    (r"2n(2n + 2)", lambda n: 2 * n * (2 * n + 2),
     r"\(2n(2n + 2) = 4n(n + 1)\), and \(n(n + 1)\) is even (one of two consecutive integers is even), "
     r"so \(4n(n + 1)\) is 8 times a whole number."),
    (r"n^3 - n", lambda n: n ** 3 - n,
     r"\(n^3 - n = (n - 1)n(n + 1)\), three consecutive integers multiplied together: "
     r"one of them is even and one of them is a multiple of 3."),
    (r"n^2 + n + 1", lambda n: n * n + n + 1,
     r"\(n^2 + n + 1 = n(n + 1) + 1\), and \(n(n + 1)\) is even, so this is one more than an even number."),
    (r"(n + 1)^2 - (n - 1)^2", lambda n: (n + 1) ** 2 - (n - 1) ** 2,
     r"\((n^2 + 2n + 1) - (n^2 - 2n + 1) = 4n\)."),
    (r"(n + 3)^2 - n^2", lambda n: (n + 3) ** 2 - n * n,
     r"\((n^2 + 6n + 9) - n^2 = 6n + 9 = 3(2n + 3)\), and \(6n + 9 = 2(3n + 4) + 1\) is one more than an even number."),
]

_AP_PROPERTY_STATEMENTS = [
    ("Always even", lambda vs: all(v % 2 == 0 for v in vs)),
    ("Always odd", lambda vs: all(v % 2 == 1 for v in vs)),
    ("Always a multiple of 3", lambda vs: all(v % 3 == 0 for v in vs)),
    ("Always a multiple of 4", lambda vs: all(v % 4 == 0 for v in vs)),
    ("Always a multiple of 8", lambda vs: all(v % 8 == 0 for v in vs)),
    ("Sometimes even and sometimes odd", lambda vs: len({v % 2 for v in vs}) == 2),
]


def _ap_property_counterexample(statement, f):
    """Why ``statement`` (a false one) fails for ``f``: a value of n where it breaks, as a sentence."""
    if statement.startswith("Sometimes"):
        word = "even" if f(0) % 2 == 0 else "odd"
        return rf"“{statement}” is wrong: the expression is always {word}."
    test = dict(_AP_PROPERTY_STATEMENTS)[statement]
    n = next(v for v in (0, 1, 2, 3, -1, 4, 5) if not test([f(v)]))
    return rf"“{statement}” fails when \(n = {n}\): the expression is {f(n)}."


@verifies('alg', task='ap_prop')
def _ap_mcq_expression_property():
    """What is true of an expression for every integer n? Exactly one offered statement is true."""
    tex, f, working = random.choice(_AP_PROPERTY_EXPRESSIONS)
    vs = [f(n) for n in range(-12, 13)]
    true = [t for t, test in _AP_PROPERTY_STATEMENTS if test(vs)]
    false = [t for t, test in _AP_PROPERTY_STATEMENTS if not test(vs)]
    correct = random.choice(true)
    wrong = random.sample(false, 3)
    opts, letter = _ap_options(correct, wrong)
    q = rf"For any integer \(n\), the expression \({tex}\) is:"
    sol = (
        rf"{working} So it is {correct.lower()}. "
        + " ".join(_ap_property_counterexample(w, f) for w in wrong)
        + rf" Answer: <strong>{letter}</strong>"
    )
    hint = "Expand and simplify first. To rule an option out, find one value of n where it fails."
    return q, sol, hint, 3, opts, letter


@verifies('alg', task='ap_square_parity')
def _ap_mcq_square_parity():
    """If n squared is even (or odd), what must be true of n?"""
    parity = random.choice(["even", "odd"])
    if parity == "even":
        correct = r"\(n\) is even"
        wrong = [r"\(n\) is odd", r"\(n\) could be either odd or even", r"\(n\) is a multiple of 4"]
        why = r"An odd number squared is odd (odd × odd = odd), so \(n^2\) even forces \(n\) to be even."
    else:
        correct = r"\(n\) is odd"
        wrong = [r"\(n\) is even", r"\(n\) could be either odd or even", r"\(n\) is a multiple of 3"]
        why = r"An even number squared is even (\((2m)^2 = 4m^2\)), so \(n^2\) odd forces \(n\) to be odd."
    opts, letter = _ap_options(correct, wrong)
    q = rf"\(n\) is a whole number and \(n^2\) is {parity}. Which statement must be true?"
    sol = rf"{why} Answer: <strong>{letter}</strong>"
    return q, sol, "Try an even n and an odd n and see what happens to n squared.", 3, opts, letter


# One pool per band, so a lesson quiz (3 foundational, 4 intermediate, 3 difficult, no repeated question) is
# never short of distinct questions. Every function here is re-solved by the verification test.
_AP_MCQ_FOUNDATIONAL = [
    _ap_mcq_even_odd,
    _ap_mcq_sum_consecutive,
    _ap_mcq_three_consecutive,
    _ap_mcq_proof_valid,
]

_AP_MCQ_INTERMEDIATE = [
    _ap_mcq_square_diff,
    _ap_mcq_consecutive_product,
    _ap_mcq_counterexample,
    _ap_mcq_factorise_even,
    _ap_mcq_consecutive_form,
    _ap_mcq_sum_two_odds,
    _ap_mcq_multiple_expression,
    _ap_mcq_counterexample_value,
]

_AP_MCQ_DIFFICULT = [
    _ap_mcq_multiple_of_eight,
    _ap_mcq_odd_squares_difference,
    _ap_mcq_find_error,
    _ap_mcq_expression_property,
    _ap_mcq_square_parity,
]

_AP_MCQ_POOLS = {
    "foundational": _AP_MCQ_FOUNDATIONAL,
    "intermediate": _AP_MCQ_INTERMEDIATE,
    "difficult": _AP_MCQ_DIFFICULT,
}

# Kept for callers that want every multiple-choice generator in one list.
_AP_MCQ_POOL = _AP_MCQ_FOUNDATIONAL + _AP_MCQ_INTERMEDIATE + _AP_MCQ_DIFFICULT


def _ap_mcq_dispatch():
    return random.choice(_AP_MCQ_POOL)()


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
        pool = _AP_MCQ_POOLS.get(difficulty) or _AP_MCQ_POOL
        return mcq_variants_from_pool(
            pool, "algebraic_proof", difficulty, count=len(pool)
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

    out = variant()
    return _ap_problem_from_output(out, difficulty)
