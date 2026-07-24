import inspect
import random
import math
from fractions import Fraction
import sympy as sp

from generators.shared.utils import (
    make_problem,
    problem_from_choice_output,
    proof_steps_answer,
    proof_steps_problem_extra,
    quadratic_roots_format_hint,
    quadratic_roots_ui_labels,
)
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    normalize_mcq_bank,
    mcq_variants_from_bank_with_procedural,
    mcq_variants_from_fn,
    run_mcq_variant,
    run_practice_variant,
    pick_named_variant,
)


#This file contains generators for:
#gcse_maths_algebra,    gcse_maths_surds,
#gcse_maths_decimals,   gcse_maths_bidmas,
#gcse_maths_fdp,   gcse_maths_multiples_factors,
#gcse_vectors,   gcse_vectors_variants,
#gcse_trigonometry,   gcse_trigonometry_variants,


def _bidmas_problem_from_output(out, difficulty):
    if len(out) >= 5:
        q, s, hint, marks, raw = out[:5]
        return make_problem(
            q, s, hint, difficulty, marks, 'gcse', 'maths', 'bidmas',
            correct_answer_raw=str(raw),
            answer_type='number',
            answer_format_hint='Enter a number',
        )
    q, s, hint, marks = out[:4]
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'bidmas')


def _bidmas_problem(variant_fn, difficulty):
    return _bidmas_problem_from_output(variant_fn(), difficulty)


def _basic_maths_practice(topic, difficulty, mode, variant_name):
    from generators.gcse import maths_basic_topics_mcq as mcq_mod
    vf = getattr(mcq_mod, f"gcse_maths_{topic}_variants")
    out = run_practice_variant(vf, difficulty, mode, variant_name)
    if topic == 'bidmas':
        return _bidmas_problem_from_output(out, difficulty)
    if topic == 'fdp':
        return _fdp_problem_from_output(out, difficulty)
    if topic == 'surds':
        return _surd_problem_from_output(out, difficulty)
    if topic == 'algebra':
        return _algebra_problem_from_output(out, difficulty)
    choice = problem_from_choice_output(out, difficulty, 'gcse', 'maths', topic)
    if choice:
        return choice
    q, s, hint, marks = out[:4]
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', topic)


# ─────────────────────────────────────────────────────────────
# GCSE MATHS — BIDMAS
# ─────────────────────────────────────────────────────────────

def gcse_maths_bidmas(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        from generators.gcse.maths_basic_topics_mcq import gcse_maths_bidmas_mcq
        return gcse_maths_bidmas_mcq(difficulty, variant_name)
    if variant_name:
        return _basic_maths_practice('bidmas', difficulty, mode, variant_name)
    pools = {
        'foundational': [
            gcse_bidmas_simple, gcse_bidmas_brackets,
            gcse_bidmas_power, gcse_neg_add_subtract,
            gcse_neg_multiply_divide,
            gcse_bidmas_proc_subtract_multiply,
            gcse_bidmas_proc_divide_add,
            gcse_bidmas_proc_two_products,
        ],
        'intermediate': [
            gcse_bidmas_mixed, gcse_neg_powers,
            gcse_bidmas_with_negatives,
            gcse_bidmas_proc_nested_brackets,
            gcse_bidmas_proc_power_then_multiply,
            gcse_bidmas_proc_bracket_over_divisor,
        ],
        'difficult': [
            gcse_bidmas_hard, gcse_bidmas_with_negatives,
            gcse_neg_powers,
            gcse_bidmas_proc_square_bracket_divide,
            gcse_bidmas_proc_nested_inner_bracket,
            gcse_bidmas_proc_negative_coefficient,
        ],
    }
    variant = random.choice(pools.get(difficulty, pools['foundational']))

    return _bidmas_problem(variant, difficulty)

# ─────────────────────────────────────────────────────────────
# GCSE MATHS — FRACTIONS, DECIMALS AND PERCENTAGES
# ─────────────────────────────────────────────────────────────

from fractions import Fraction


_FDP_TERMINATING_DENS = [2, 4, 5, 8, 10, 16, 20, 25, 40, 50, 100]
_FDP_RECURRING_DENS = [3, 6, 7, 9, 11, 12, 15]


def _fdp_simplify_fraction(num, den):
    g = math.gcd(num, den)
    return num // g, den // g


def _fdp_format_decimal(dec, max_dp=4):
    return f"{dec:.{max_dp}f}".rstrip("0").rstrip(".")


def _fdp_fraction_str(num, den):
    return f"{num}/{den}"


def _fdp_random_terminating_fraction():
    den = random.choice(_FDP_TERMINATING_DENS)
    num = random.randint(1, den - 1)
    return _fdp_simplify_fraction(num, den)


def _fdp_random_recurring_fraction():
    while True:
        den = random.choice(_FDP_RECURRING_DENS)
        num = random.randint(1, den - 1)
        num, den = _fdp_simplify_fraction(num, den)
        if den > 1:
            return num, den


def _fdp_random_percentage():
    return random.randint(1, 99)


def _fdp_pct_to_fraction(pct):
    num, den = _fdp_simplify_fraction(pct, 100)
    if den == 1:
        return str(num)
    return _fdp_fraction_str(num, den)


def _fdp_recurring_decimal_display(num, den):
    """Short recurring-decimal string for GCSE (e.g. 0.333…)."""
    seen = {}
    digits = []
    remainder = num % den
    pos = 0
    while remainder and remainder not in seen and pos < 12:
        seen[remainder] = pos
        remainder *= 10
        digits.append(str(remainder // den))
        remainder %= den
        pos += 1
    if remainder in seen:
        rep_start = seen[remainder]
        body = "".join(digits[:rep_start]) + "".join(digits[rep_start:])
        if rep_start == 0:
            return f"0.{body}…"
        return f"0.{''.join(digits[:rep_start])}{''.join(digits[rep_start:])}…"
    dec = num / den
    return _fdp_format_decimal(dec)


def _fdp_recurring_digit_info(num, den):
    """Return (digits after decimal point, index where the repeat starts)."""
    seen = {}
    digits = []
    remainder = num % den
    pos = 0
    while remainder and remainder not in seen and pos < 12:
        seen[remainder] = pos
        remainder *= 10
        digits.append(str(remainder // den))
        remainder %= den
        pos += 1
    rep_start = seen[remainder] if remainder in seen else len(digits)
    return digits, rep_start


def _fdp_recurring_algebra_working(num, den):
    """Step-by-step solution and key-concept hint for recurring decimal → fraction."""
    dec = _fdp_recurring_decimal_display(num, den)
    digits, rep_start = _fdp_recurring_digit_info(num, den)
    rep_len = max(1, len(digits) - rep_start)
    mult_a = 10 ** rep_start
    mult_b = 10 ** (rep_start + rep_len)
    coeff = mult_b - mult_a
    rhs = num * coeff // den
    simp_num, simp_den = _fdp_simplify_fraction(num, den)
    frac = _fdp_fraction_str(simp_num, simp_den)

    if rep_start == 0:
        lhs_int = (num * mult_b) // den
        multiply_line = (
            f"Multiply both sides by {mult_b} so the repeating block moves to the left:<br>"
            f"&nbsp;&nbsp;{mult_b}x = {lhs_int}.{''.join(digits[rep_start:rep_start + rep_len] * 3)}…"
        )
        subtract_line = f"Subtract the original equation: {mult_b}x − x = {rhs}  →  {coeff}x = {rhs}"
    else:
        fixed = ''.join(digits[:rep_start])
        repeat = ''.join(digits[rep_start:rep_start + rep_len])
        multiply_line = (
            f"Multiply by {mult_a} to move past the non-repeating part:<br>"
            f"&nbsp;&nbsp;{mult_a}x = {fixed}.{repeat}…<br>"
            f"Multiply by {mult_b} to shift one full repeating block:<br>"
            f"&nbsp;&nbsp;{mult_b}x = … (the digits after the decimal now match and will cancel)"
        )
        subtract_line = (
            f"Subtract the two equations so the recurring tail disappears:<br>"
            f"&nbsp;&nbsp;{mult_b}x − {mult_a}x = {rhs}  →  {coeff}x = {rhs}"
        )

    solve_line = f"Divide both sides by {coeff}: x = {rhs}/{coeff} = <strong>{frac}</strong>"

    s = (
        f"This is a recurring decimal. Use the algebraic method:<br>"
        f"<strong>1.</strong> Let x = {dec}<br>"
        f"<strong>2.</strong> {multiply_line}<br>"
        f"<strong>3.</strong> {subtract_line}<br>"
        f"<strong>4.</strong> {solve_line}"
    )
    hint = (
        f"<strong>Key idea:</strong> let the decimal equal x, multiply to line up the repeating "
        f"digits, then subtract so the infinite repeating part cancels.<br><br>"
        f"<strong>Step 1:</strong> write x = {dec}<br>"
        f"<strong>Step 2:</strong> multiply x by a power of 10 so the repeat lines up "
        f"({'×' + str(mult_b) if rep_start == 0 else '×' + str(mult_a) + ' then ×' + str(mult_b)}).<br>"
        f"<strong>Step 3:</strong> subtract the equations — the recurring decimals disappear, "
        f"leaving {coeff}x = {rhs}.<br>"
        f"<strong>Step 4:</strong> solve for x and simplify: x = {rhs}/{coeff} = {frac}."
    )
    return s, hint


def _fdp_digit_sum(n):
    n = abs(int(n))
    total = 0
    while n:
        total += n % 10
        n //= 10
    return total


def _fdp_format_int(n):
    return f"{int(n):,}"


def _fdp_power10_gcse(exp):
    labels = {
        1: ("10", ""),
        2: ("100", ""),
        3: ("1,000", ""),
        4: ("10,000", ""),
        5: ("100,000", ""),
        6: ("1,000,000", " — a 1 followed by six zeros"),
    }
    if exp in labels:
        label, extra = labels[exp]
        return label, extra
    val = 10 ** exp
    return f"{val:,}", f" (10<sup>{exp}</sup>)"


def _fdp_recurring_cancel_steps(raw_num, raw_den, simp_num, simp_den):
    """GCSE-friendly cancellation lines — small divisors, not one huge HCF."""
    if raw_num == simp_num and raw_den == simp_den:
        return [f"Already in simplest form: <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>"]

    lines = [f"Simplify {_fdp_format_int(raw_num)}/{_fdp_format_int(raw_den)}:"]
    a, b = raw_num, raw_den

    div3_first = True
    while a % 3 == 0 and b % 3 == 0 and (a != simp_num or b != simp_den):
        ds_a, ds_b = _fdp_digit_sum(a), _fdp_digit_sum(b)
        a //= 3
        b //= 3
        note = ""
        if div3_first:
            note = (
                f" (add the digits: {ds_a} and {ds_b} — both divisible by 3, "
                f"so the whole numbers are too)"
            )
            div3_first = False
        lines.append(f"÷3 top and bottom{note}: → {_fdp_format_int(a)}/{_fdp_format_int(b)}")
        if a == simp_num and b == simp_den:
            lines.append(f"Simplest form: <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>")
            return lines

    for p_top in (5, 2, 7, 3, 11, 13):
        if a % p_top != 0:
            continue
        shared = a // p_top
        for p_bot in (7, 3, 5, 11, 13, 2):
            if b % p_bot == 0 and b // p_bot == shared:
                top_note = f" (ends in 5)" if p_top == 5 and str(a).endswith("5") else ""
                lines.append(
                    f"Try ÷{p_top} on the top{top_note}: {_fdp_format_int(a)} ÷ {p_top} = {_fdp_format_int(shared)}<br>"
                    f"Check ÷{p_bot} on the bottom: {_fdp_format_int(b)} ÷ {p_bot} = {_fdp_format_int(shared)} ✓ "
                    f"— same result, so the fraction is <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>"
                )
                return lines

    for p in (2, 5, 7, 11, 13):
        while a % p == 0 and b % p == 0 and (a != simp_num or b != simp_den):
            a //= p
            b //= p
            lines.append(f"÷{p} top and bottom: → {_fdp_format_int(a)}/{_fdp_format_int(b)}")
            if a == simp_num and b == simp_den:
                lines.append(f"Simplest form: <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>")
                return lines

    if a == simp_num and b == simp_den:
        lines.append(f"Simplest form: <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>")
        return lines

    g = math.gcd(a, b)
    if g > 1:
        lines.append(
            f"Both divide by {g}: {_fdp_format_int(a)} ÷ {g} = {a // g}, "
            f"{_fdp_format_int(b)} ÷ {g} = {b // g}"
        )
        lines.append(f"→ <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>")
        return lines

    lines.append(f"→ <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>")
    return lines


def _fdp_recurring_algebra_steps(num, den):
    """Step-by-step solution and key-concept hint for recurring decimal → fraction."""
    digits, rep_start = _fdp_recurring_digit_info(num, den)
    n = rep_start
    r = max(len(digits) - rep_start, 1)
    non_rep = "".join(digits[:n])
    rep_block = "".join(digits[n:n + r]) or "".join(digits[n:]) or "0"
    dec = _fdp_recurring_decimal_display(num, den)

    mult1 = 10 ** n
    mult2 = 10 ** (n + r)
    coeff = mult2 - mult1
    integer_rhs = int(coeff * Fraction(num, den))
    simp_num, simp_den = _fdp_simplify_fraction(integer_rhs, coeff)

    mult1_label, mult1_extra = _fdp_power10_gcse(n) if n else ("", "")
    mult2_label, mult2_extra = _fdp_power10_gcse(n + r)

    steps = [f"<strong>Step 1</strong> — let x = {dec}"]
    if mult1 > 1:
        steps.append(
            f"<strong>Step 2</strong> — multiply both sides by {mult1_label}{mult1_extra} "
            f"to move past the {n} non-recurring digit{'s' if n != 1 else ''}:<br>"
            f"{mult1_label}x = {non_rep}.{rep_block}…"
        )
        step_no = 3
    else:
        step_no = 2

    repeat_desc = (
        f"'{rep_block}' has {r} digit{'s' if r != 1 else ''} and repeats forever, "
        f"so multiply by {mult2_label}{mult2_extra}"
    )
    steps.append(
        f"<strong>Step {step_no}</strong> — {repeat_desc}:<br>"
        f"{mult2_label}x = "
        + (f"{non_rep}{rep_block}.{rep_block}…" if n > 0 else f"{rep_block}.{rep_block}…")
    )
    step_no += 1

    if mult1 > 1:
        lhs = f"{mult2_label}x − {mult1_label}x"
        rhs = (
            f"{_fdp_format_int(int(non_rep + rep_block))} − {_fdp_format_int(int(non_rep))} "
            f"= {_fdp_format_int(integer_rhs)}"
        )
    else:
        lhs = f"{mult2_label}x − x"
        rhs = _fdp_format_int(integer_rhs)
    steps.append(
        f"<strong>Step {step_no}</strong> — subtract so the recurring parts cancel:<br>"
        f"{lhs} = {rhs}"
    )
    step_no += 1

    coeff_label = _fdp_format_int(coeff) if coeff >= 1000 else str(coeff)
    steps.append(f"<strong>Step {step_no}</strong> — {coeff_label}x = {_fdp_format_int(integer_rhs)}")
    step_no += 1
    steps.append(
        f"<strong>Step {step_no}</strong> — x = "
        f"{_fdp_format_int(integer_rhs)}/{_fdp_format_int(coeff)}"
    )
    step_no += 1

    cancel_lines = _fdp_recurring_cancel_steps(integer_rhs, coeff, simp_num, simp_den)
    for i, line in enumerate(cancel_lines):
        prefix = f"<strong>Step {step_no}</strong> — " if i == 0 else ""
        steps.append(prefix + line)
    step_no += 1

    if simp_num == integer_rhs and simp_den == coeff:
        steps.append(f"<strong>Answer:</strong> <strong>{_fdp_fraction_str(simp_num, simp_den)}</strong>")

    if n == 0:
        hint = (
            f"The digits '{rep_block}' repeat straight away. "
            f"Let x equal the decimal, multiply by {mult2_label} so the digits after the point "
            f"match, then subtract x to cancel the infinite tail. "
            f"To simplify the fraction, divide top and bottom by 3 whenever both digit sums "
            f"are multiples of 3 — keep going until the fraction won't reduce further."
        )
    else:
        hint = (
            f"{n} digit{'s' if n != 1 else ''} after the point stay fixed; then '{rep_block}' repeats. "
            f"Multiply by {mult1_label} to clear the fixed part, then by {mult2_label} to line up "
            f"one full repeat. Subtract the two equations, then simplify by dividing top and "
            f"bottom by small numbers (try 3 first — add the digits to check)."
        )
    return "<br>".join(steps), hint


def _fdp_random_order_items(count=4):
    """Values in mixed decimal / fraction / percentage form for ordering."""
    values = []
    while len(values) < count:
        num, den = _fdp_random_terminating_fraction()
        val = round(num / den, 4)
        if val not in values:
            values.append(val)
    items = []
    for val in values:
        form = random.choice(["decimal", "fraction", "percent"])
        if form == "decimal":
            label = _fdp_format_decimal(val)
        elif form == "percent":
            pct = val * 100
            label = f"{_fdp_format_decimal(pct)}%" if pct != int(pct) else f"{int(pct)}%"
        else:
            frac = Fraction(val).limit_denominator(100)
            label = _fdp_fraction_str(frac.numerator, frac.denominator)
        items.append((label, val))
    ordered = ", ".join(x[0] for x in sorted(items, key=lambda x: x[1]))
    return items, ordered


def _fdp_fraction_of_case():
    den = random.choice([4, 5, 6, 8, 10, 12, 15, 20, 25])
    num = random.randint(1, den - 1)
    num, den = _fdp_simplify_fraction(num, den)
    mult = random.randint(8, 45)
    total = den * mult
    ans = total * num // den
    return num, den, total, ans


def _fdp_share_in_ratio_case():
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    while a == b:
        b = random.randint(2, 9)
    parts = a + b
    total = parts * random.randint(10, 45)
    return a, b, total, total * a // parts, total * b // parts


def _fdp_best_value_case():
    qty_a = random.randint(3, 8)
    qty_b = random.randint(qty_a + 1, 12)
    unit_price_a = round(random.uniform(0.35, 2.50), 2)
    unit_price_b = round(random.uniform(0.30, 2.40), 2)
    while abs(unit_price_a - unit_price_b) < 0.05:
        unit_price_b = round(random.uniform(0.30, 2.40), 2)
    price_a = round(unit_price_a * qty_a, 2)
    price_b = round(unit_price_b * qty_b, 2)
    if unit_price_a < unit_price_b:
        best, label_a, label_b = "Pack A", f"Pack A: {qty_a} for £{price_a:.2f}", f"Pack B: {qty_b} for £{price_b:.2f}"
    else:
        best, label_a, label_b = "Pack B", f"Pack A: {qty_a} for £{price_a:.2f}", f"Pack B: {qty_b} for £{price_b:.2f}"
    return label_a, label_b, best, unit_price_a, unit_price_b


def _fdp_raw(value, places=4):
    """Canonical numeric string for typed answer checking."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        val = round(value, places)
        if val == int(val):
            return str(int(val))
        return f'{val:.{places}f}'.rstrip('0').rstrip('.')
    return str(value)


def _fdp_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_fdp_raw(v) for v in values),
        'labels': tuple(labels),
    }


def _fdp_fraction_answer(value):
    return {'type': 'fraction', 'value': str(value)}


def _fdp_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            if values and len(values) == len(labels):
                extra = {
                    'correct_answer_raw': '|'.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_format_hint': 'Enter a number in every field',
                }
        elif isinstance(raw, dict) and raw.get('type') == 'fraction':
            value = raw.get('value')
            if value is not None and str(value).strip():
                extra = {
                    'correct_answer_raw': str(value).strip(),
                    'answer_type': 'fraction',
                    'answer_format_hint': 'Enter a fraction (e.g. 3/4)',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _fdp_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
        elif isinstance(raw, str):
            if '/' in raw:
                extra = {
                    'correct_answer_raw': raw,
                    'answer_type': 'fraction',
                    'answer_format_hint': 'Enter a fraction (e.g. 3/4)',
                }
            else:
                extra = {
                    'correct_answer_raw': raw,
                    'answer_type': 'number',
                    'answer_format_hint': 'Enter a number',
                }
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'fdp', **extra)


def _fdp_problem(variant_fn, difficulty):
    return _fdp_problem_from_output(variant_fn(), difficulty)


def gcse_fdp_decimal_to_percentage():
    num, den = _fdp_random_terminating_fraction()
    x = num / den
    ans = x * 100
    ans_str = _fdp_format_decimal(ans) if ans != int(ans) else str(int(ans))
    x_str = _fdp_format_decimal(x)
    q = rf"Write {x_str} as a percentage."
    s = rf"To convert a decimal to a percentage, multiply by 100.<br>{x_str} × 100 = <strong>{ans_str}%</strong>"
    hint = (
        "<strong>Key idea:</strong> percent means “out of 100”, so move the decimal point two places right.<br>"
        f"Example: 0.25 → 25 (because 0.25 = 25/100). Multiply by 100: {x_str} × 100."
    )
    return q, s, hint, 1, ans if ans == int(ans) else ans

def gcse_fdp_percentage_to_decimal():
    x = random.randint(1, 150)
    ans = x / 100
    ans_str = _fdp_format_decimal(ans, 3)
    q = rf"Write {x}% as a decimal."
    s = rf"To convert a percentage to a decimal, divide by 100.<br>{x} ÷ 100 = <strong>{ans_str}</strong>"
    hint = (
        "<strong>Key idea:</strong> divide by 100, or move the decimal point two places left.<br>"
        f"Example: 50% = 50 ÷ 100 = 0.5. Here: {x} ÷ 100 = {ans_str}."
    )
    return q, s, hint, 1, ans

def gcse_fdp_decimal_to_fraction():
    num, den = _fdp_random_terminating_fraction()
    dec = num / den
    dec_str = _fdp_format_decimal(dec)
    frac = _fdp_fraction_str(num, den)
    q = rf"Write {dec_str} as a fraction in its simplest form."
    s = rf"Write {dec_str} using place value, then simplify.<br><strong>{frac}</strong>"
    hint = (
        "<strong>Key idea:</strong> read the decimal place value, write as a fraction over 10, 100 or 1000, "
        "then cancel common factors.<br>"
        f"Example: 0.75 = 75/100 = 3/4. For {dec_str}, identify the last digit's place value, "
        "write the fraction, then simplify."
    )
    return q, s, hint, 1, _fdp_fraction_answer(frac)

def gcse_fdp_fraction_to_decimal():
    a, b = _fdp_random_terminating_fraction()
    frac_str = _fdp_fraction_str(a, b)
    ans = _fdp_format_decimal(a / b)
    q = rf"Write {frac_str} as a decimal."
    s = rf"Convert a fraction to a decimal by dividing the numerator by the denominator.<br>{a} ÷ {b} = <strong>{ans}</strong>"
    hint = (
        "<strong>Key idea:</strong> a fraction is a division, so divide the top number by the bottom.<br>"
        f"Example: 3/4 = 3 ÷ 4 = 0.75. Here: {a} ÷ {b}."
    )
    return q, s, hint, 1, a / b

def gcse_fdp_percentage_to_fraction():
    pct = _fdp_random_percentage()
    ans = _fdp_pct_to_fraction(pct)
    q = rf"Write {pct}% as a fraction in its simplest form."
    s = rf"Write the percentage over 100, then simplify.<br>{pct}% = {pct}/100 = <strong>{ans}</strong>"
    hint = (
        "<strong>Key idea:</strong> “percent” means per hundred, so write the number over 100 first.<br>"
        f"Example: 20% = 20/100 = 1/5. Here: {pct}% = {pct}/100, then simplify to {ans}."
    )
    return q, s, hint, 1, _fdp_fraction_answer(ans)

def gcse_fdp_fraction_to_percentage():
    a, b = _fdp_random_terminating_fraction()
    frac = _fdp_fraction_str(a, b)
    ans = (a / b) * 100
    ans_str = _fdp_format_decimal(ans) if ans != int(ans) else str(int(ans))
    q = rf"Write {frac} as a percentage."
    s = rf"Convert the fraction to a decimal, then multiply by 100.<br><strong>{frac} = {ans_str}%</strong>"
    hint = (
        "<strong>Key idea:</strong> turn the fraction into a decimal first, then multiply by 100 for %.<br>"
        f"Example: 1/4 = 0.25 → 25%. Here: {frac} → decimal → × 100 → {ans_str}%."
    )
    return q, s, hint, 1, ans if ans == int(ans) else ans

def gcse_fdp_multi_step():
    a, b = _fdp_random_terminating_fraction()
    frac = _fdp_fraction_str(a, b)
    dec = _fdp_format_decimal(a / b)
    pct_val = (a / b) * 100
    pct = f"{_fdp_format_decimal(pct_val)}%" if pct_val != int(pct_val) else f"{int(pct_val)}%"
    q = rf"Convert {frac} into a decimal and a percentage."
    s = rf"{frac} = <strong>{dec}</strong><br>{dec} × 100 = <strong>{pct}</strong>"
    hint = (
        "<strong>Key idea:</strong> do the conversions in order — fraction → decimal → percentage.<br>"
        f"1. Divide: {a} ÷ {b} = {dec}<br>"
        f"2. Multiply by 100: {dec} × 100 = {pct.replace('%', '')}%"
    )
    return q, s, hint, 2

def gcse_fdp_recurring():
    num, den = _fdp_random_recurring_fraction()
    dec = _fdp_recurring_decimal_display(num, den)
    q = rf"Write {dec} as a fraction."
    s, hint = _fdp_recurring_algebra_working(num, den)
    return q, s, hint, 3


# ── FDP: intermediate (non-conversion formats) ───────────────────────────────

def gcse_fdp_fraction_of_amount():
    """Find a fraction of a quantity (money or count)."""
    num, den, total, ans = _fdp_fraction_of_case()
    q = rf"Find \( \dfrac{{{num}}}{{{den}}} \) of {total}."
    s = (
        rf"Method 1: divide by {den}, then multiply by {num}.<br>"
        rf"{total} ÷ {den} = {total // den}, then × {num} = <strong>{ans}</strong><br>"
        rf"Method 2: {num}/{den} × {total} = <strong>{ans}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> “of” means multiply — find the fraction of the amount.<br>"
        f"Method 1: divide by {den} to find one part, then × {num}.<br>"
        f"Method 2: multiply directly — {num}/{den} × {total}."
    )
    return q, s, hint, 2, ans


def gcse_fdp_percentage_increase():
    """Increase an amount by a given percentage."""
    amount = random.choice([60, 80, 120, 150, 240, 350, 480])
    pct = random.choice([5, 8, 10, 12, 15, 20])
    increase = round(amount * pct / 100, 2)
    new_amount = round(amount + increase, 2)
    q = rf"A value of {amount} is increased by {pct}%. Find the new value."
    s = (
        rf"Find {pct}% of {amount}: {amount} × {pct}/100 = {increase}<br>"
        rf"Add to the original: {amount} + {increase} = <strong>{new_amount}</strong><br>"
        rf"Or use multiplier 1.{pct if pct < 10 else pct}: {amount} × {1 + pct/100} = {new_amount}"
    )
    hint = (
        "<strong>Key idea:</strong> an increase adds on a percentage of the original amount.<br>"
        f"1. Find {pct}% of {amount}: {amount} × {pct}/100 = {increase}<br>"
        f"2. Add to the original: {amount} + {increase}<br>"
        f"Or use the multiplier 1.{pct if pct < 10 else pct} in one step: {amount} × {1 + pct/100}."
    )
    return q, s, hint, 2, new_amount


def gcse_fdp_percentage_decrease():
    """Decrease an amount by a given percentage (sale / discount)."""
    amount = random.choice([50, 72, 90, 120, 160, 200, 250])
    pct = random.choice([10, 15, 20, 25, 30])
    decrease = round(amount * pct / 100, 2)
    new_amount = round(amount - decrease, 2)
    q = rf"The price of an item is £{amount}. It is reduced by {pct}% in a sale. Find the sale price."
    s = (
        rf"Discount = {pct}% of £{amount} = £{decrease}<br>"
        rf"Sale price = £{amount} − £{decrease} = <strong>£{new_amount}</strong><br>"
        rf"Multiplier method: £{amount} × {1 - pct/100} = £{new_amount}"
    )
    hint = (
        "<strong>Key idea:</strong> a reduction subtracts a percentage of the original price.<br>"
        f"1. Discount = {pct}% of £{amount} = £{decrease}<br>"
        f"2. Sale price = £{amount} − £{decrease}<br>"
        f"Or use multiplier {1 - pct/100}: £{amount} × {1 - pct/100}."
    )
    return q, s, hint, 2, new_amount


def gcse_fdp_percentage_change():
    """Find percentage increase or decrease between two values."""
    original = random.randint(20, 300)
    pct = random.choice([5, 8, 10, 12, 15, 20, 25, 30, 40, 50])
    change_type = random.choice(["increase", "decrease"])
    change = round(original * pct / 100, 2)
    new = round(original + change if change_type == "increase" else original - change, 2)
    q = (
        rf"The value changes from {original} to {new}. "
        rf"Find the percentage {change_type}."
    )
    s = (
        rf"Change = |{new} − {original}| = {change}<br>"
        rf"Percentage change = (change ÷ original) × 100<br>"
        rf"= ({change} ÷ {original}) × 100 = <strong>{pct}% {change_type}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> percentage change compares the change to the <em>original</em> value.<br>"
        f"1. Change = |new − original| = {change}<br>"
        f"2. Percentage change = (change ÷ original) × 100 = ({change} ÷ {original}) × 100<br>"
        "Always divide by the starting value, not the new value."
    )
    return q, s, hint, 3, pct


def gcse_fdp_reverse_percentage():
    """Find original amount before a percentage change."""
    pct = random.choice([10, 15, 20, 25])
    multiplier = 1 - pct / 100
    original = random.choice([40, 50, 60, 80, 100, 120])
    final = round(original * multiplier, 2)
    q = rf"After a {pct}% reduction, the price is £{final}. Find the original price."
    s = (
        rf"A {pct}% reduction uses multiplier {multiplier}.<br>"
        rf"Original × {multiplier} = {final}<br>"
        rf"Original = {final} ÷ {multiplier} = <strong>£{original}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> reverse percentages undo the multiplier — divide, don't subtract the %.<br>"
        f"A {pct}% reduction means the final price is {multiplier} of the original.<br>"
        f"So original × {multiplier} = {final} → original = {final} ÷ {multiplier}."
    )
    return q, s, hint, 3, original


def gcse_fdp_order_mixed_values():
    """Order values given in different forms (fraction, decimal, percentage)."""
    items, ordered = _fdp_random_order_items(4)
    random.shuffle(items)
    labels = [x[0] for x in items]
    q = (
        r"Write these values in order from <strong>smallest to largest</strong>:<br>"
        + ", ".join(labels)
    )
    s = (
        r"Convert each value to a decimal to compare:<br>"
        + "<br>".join(f"{lab} ≈ {_fdp_format_decimal(val)}" for lab, val in items)
        + rf"<br>Smallest to largest: <strong>{ordered}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> you cannot compare fractions, decimals and percentages directly — "
        "convert them all to the same form first.<br>"
        "Easiest method: rewrite every value as a decimal, then order from smallest to largest.<br>"
        "Check each conversion carefully before comparing."
    )
    return q, s, hint, 2


# ── FDP: difficult (multi-step / reasoning, non-conversion) ───────────────────

def gcse_fdp_compound_percentage():
    """Two successive percentage changes on an amount."""
    amount = random.choice([80, 100, 120, 150, 200, 250, 300, 400, 500])
    pct1 = random.choice([5, 8, 10, 12, 15, 20])
    pct2 = random.choice([5, 8, 10, 12, 15, 20, 25])
    after_first = round(amount * (1 + pct1 / 100), 2)
    final = round(after_first * (1 - pct2 / 100), 2)
    q = (
        rf"£{amount} is increased by {pct1}% and then decreased by {pct2}%. "
        rf"Find the final amount."
    )
    s = (
        rf"After {pct1}% increase: £{amount} × {1 + pct1/100} = £{after_first}<br>"
        rf"Then {pct2}% decrease: £{after_first} × {1 - pct2/100} = <strong>£{final}</strong><br>"
        rf"Overall multiplier: {1 + pct1/100} × {1 - pct2/100} = "
        rf"{round((1 + pct1/100) * (1 - pct2/100), 4)}"
    )
    hint = (
        "<strong>Key idea:</strong> apply each percentage change separately — do not add or subtract the percentages.<br>"
        f"1. After {pct1}% increase: multiply by {1 + pct1/100}<br>"
        f"2. Then {pct2}% decrease: multiply by {1 - pct2/100}<br>"
        "Each change applies to the <em>current</em> amount, not the original."
    )
    return q, s, hint, 3, final


def gcse_fdp_reverse_percentage_two_step():
    """Original price after increase then decrease (or vice versa)."""
    original = random.choice([60, 80, 100, 120, 150, 200, 250])
    pct_up = random.choice([5, 10, 12, 15, 20])
    pct_down = random.choice([5, 10, 12, 15, 20, 25])
    mid = round(original * (1 + pct_up / 100), 2)
    final = round(mid * (1 - pct_down / 100), 2)
    q = (
        rf"After a {pct_up}% increase followed by a {pct_down}% decrease, "
        rf"the price is £{final}. Find the original price."
    )
    s = (
        rf"Combined multiplier = {1 + pct_up/100} × {1 - pct_down/100} = "
        rf"{round((1 + pct_up/100) * (1 - pct_down/100), 4)}<br>"
        rf"Original × {round((1 + pct_up/100) * (1 - pct_down/100), 4)} = {final}<br>"
        rf"Original = {final} ÷ {round((1 + pct_up/100) * (1 - pct_down/100), 4)} "
        rf"= <strong>£{original}</strong>"
    )
    combined = round((1 + pct_up/100) * (1 - pct_down/100), 4)
    hint = (
        "<strong>Key idea:</strong> combine the multipliers first, then divide the final price.<br>"
        f"Increase ×{1 + pct_up/100}, then decrease ×{1 - pct_down/100} "
        f"→ combined multiplier = {combined}.<br>"
        f"Original × {combined} = {final}, so original = {final} ÷ {combined}."
    )
    return q, s, hint, 4, original


def gcse_fdp_share_in_ratio():
    """Share an amount in a given ratio (fractional reasoning)."""
    a, b, total, part_a, part_b = _fdp_share_in_ratio_case()
    q = rf"Share £{total} in the ratio {a}:{b}."
    s = (
        rf"Total parts = {a} + {b} = {a + b}<br>"
        rf"One part = £{total} ÷ {a + b} = £{total // (a + b)}<br>"
        rf"{a} parts = <strong>£{part_a}</strong>, {b} parts = <strong>£{part_b}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> treat the ratio as equal parts — find one part, then scale up.<br>"
        f"1. Total parts = {a} + {b} = {a + b}<br>"
        f"2. One part = £{total} ÷ {a + b}<br>"
        f"3. First share = {a} parts, second share = {b} parts."
    )
    return q, s, hint, 3, _fdp_fields_answer(
        (part_a, part_b), (f'{a} parts', f'{b} parts')
    )


def gcse_fdp_profit_loss_percentage():
    """Profit or loss as a percentage of cost price."""
    cost = random.choice([40, 55, 80, 120, 150])
    markup = random.choice([15, 20, 25, 30, 40])
    selling = cost + markup
    pct = round(markup / cost * 100, 1)
    q = (
        rf"An item costs £{cost} and is sold for £{selling}. "
        rf"Calculate the percentage profit."
    )
    s = (
        rf"Profit = £{selling} − £{cost} = £{markup}<br>"
        rf"Percentage profit = (profit ÷ cost) × 100<br>"
        rf"= ({markup} ÷ {cost}) × 100 = <strong>{pct}%</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> percentage profit is always based on the <em>cost price</em>, not the selling price.<br>"
        f"1. Profit = selling price − cost = £{selling} − £{cost} = £{markup}<br>"
        f"2. Percentage profit = (profit ÷ cost) × 100 = ({markup} ÷ {cost}) × 100."
    )
    return q, s, hint, 3, pct


def gcse_fdp_best_value_comparison():
    """Compare offers using unit cost."""
    label_a, label_b, best, unit_a, unit_b = _fdp_best_value_case()
    q = rf"Which is better value?<br><strong>{label_a}</strong><br><strong>{label_b}</strong>"
    s = (
        rf"Compare cost per item by dividing.<br>"
        rf"{label_a}: £{unit_a:.2f} per item<br>"
        rf"{label_b}: £{unit_b:.2f} per item<br>"
        rf"<strong>{best}</strong> is better value (lower cost per item)."
    )
    hint = (
        "<strong>Key idea:</strong> better value means a lower cost <em>per item</em>, not necessarily a lower pack price.<br>"
        "Divide each pack price by how many items it contains, then compare the unit costs.<br>"
        "The pack with the smaller cost per item is better value."
    )
    return q, s, hint, 3


def gcse_fdp_fraction_word_problem():
    """Multi-step fraction of a quantity in context."""
    num, den, _, _ = _fdp_fraction_of_case()
    total = den * random.randint(12, 55)
    taken = total * num // den
    left = total - taken
    q = (
        rf"A school has {total} pupils. \( \dfrac{{{num}}}{{{den}}} \) of them walk to school. "
        rf"How many pupils do <strong>not</strong> walk to school?"
    )
    s = (
        rf"Pupils who walk = \( \dfrac{{{num}}}{{{den}}} \) × {total} = {taken}<br>"
        rf"Pupils who do not walk = {total} − {taken} = <strong>{left}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> read the question carefully — it asks for pupils who do <em>not</em> walk.<br>"
        f"1. Find how many walk: {num}/{den} × {total} = {taken}<br>"
        f"2. Subtract from the total: {total} − {taken} = pupils who do not walk."
    )
    return q, s, hint, 3, left


def gcse_maths_fdp(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        from generators.gcse.maths_basic_topics_mcq import gcse_maths_fdp_mcq
        return gcse_maths_fdp_mcq(difficulty, variant_name)
    if variant_name:
        return _basic_maths_practice('fdp', difficulty, mode, variant_name)
    if difficulty == 'foundational':
        variant = random.choice([
            gcse_fdp_decimal_to_percentage,
            gcse_fdp_percentage_to_decimal,
            gcse_fdp_decimal_to_fraction,
            gcse_fdp_fraction_to_decimal,
            gcse_fdp_percentage_to_fraction,
            gcse_fdp_fraction_to_percentage
        ])
    elif difficulty == 'intermediate':
        variant = random.choice([
            gcse_fdp_fraction_to_decimal,
            gcse_fdp_percentage_to_fraction,
            gcse_fdp_fraction_to_percentage,
            gcse_fdp_fraction_of_amount,
            gcse_fdp_percentage_increase,
            gcse_fdp_percentage_decrease,
            gcse_fdp_percentage_change,
            gcse_fdp_reverse_percentage,
            gcse_fdp_order_mixed_values,
        ])
    else:
        variant = random.choice([
            gcse_fdp_multi_step,
            gcse_fdp_recurring,
            gcse_fdp_compound_percentage,
            gcse_fdp_reverse_percentage_two_step,
            gcse_fdp_share_in_ratio,
            gcse_fdp_profit_loss_percentage,
            gcse_fdp_best_value_comparison,
            gcse_fdp_fraction_word_problem,
        ])

    return _fdp_problem(variant, difficulty)


# ─────────────────────────────────────────────────────────────
# GCSE MATHS — MULTIPLES AND FACTORS
# ─────────────────────────────────────────────────────────────

_MF_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _mf_sup(n):
    return str(n).translate(_MF_SUP)


def _mf_is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _mf_all_factors(n):
    factors = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    return sorted(factors)


def _mf_factor_pairs_str(n):
    pairs = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            j = n // i
            pairs.append(f"{i}×{j}")
    return ", ".join(pairs)


def _mf_prime_factors_dict(n):
    factors = {}
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors


def _mf_pf_string(n):
    pf = _mf_prime_factors_dict(n)
    parts = []
    for p in sorted(pf):
        if pf[p] == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}{_mf_sup(pf[p])}")
    return " × ".join(parts)


def _mf_hcf_pf_string(a, b):
    d1, d2 = _mf_prime_factors_dict(a), _mf_prime_factors_dict(b)
    result = 1
    parts = []
    for p in sorted(set(d1) & set(d2)):
        exp = min(d1[p], d2[p])
        result *= p ** exp
        parts.append(f"{p}{_mf_sup(exp)}" if exp > 1 else str(p))
    return result, " × ".join(parts) if parts else "1"


def _mf_lcm_pf_string(a, b):
    d1, d2 = _mf_prime_factors_dict(a), _mf_prime_factors_dict(b)
    result = 1
    parts = []
    for p in sorted(set(d1) | set(d2)):
        exp = max(d1.get(p, 0), d2.get(p, 0))
        result *= p ** exp
        parts.append(f"{p}{_mf_sup(exp)}" if exp > 1 else str(p))
    return result, " × ".join(parts)


def _mf_lcm(a, b):
    return a * b // math.gcd(a, b)


def _mf_hcf(a, b):
    return math.gcd(a, b)


def _mf_random_composite(lo=12, hi=120):
    while True:
        n = random.randint(lo, hi)
        if not _mf_is_prime(n):
            return n


def _mf_random_pair(lo=6, hi=72):
    a = random.randint(lo, hi)
    b = random.randint(lo, hi)
    return a, b


def _mf_random_prime_check():
    if random.random() < 0.5:
        while True:
            n = random.randint(11, 99)
            if _mf_is_prime(n):
                return n, True
    n = random.randint(12, 99)
    while _mf_is_prime(n):
        n = random.randint(12, 99)
    return n, False


def _mf_small_divisor(n):
    for d in (2, 3, 5, 7, 11):
        if n % d == 0:
            return d
    return _mf_all_factors(n)[1]


def _mf_lcm_buses_case():
    a = random.randint(4, 18)
    b = random.randint(4, 18)
    while a == b:
        b = random.randint(4, 18)
    lcm = _mf_lcm(a, b)
    hour = random.randint(8, 15)
    minute = random.choice([0, 10, 15, 20, 30, 45])
    total = hour * 60 + minute + lcm
    return a, b, lcm, f"{hour}:{minute:02d}", f"{total // 60}:{total % 60:02d}"


def _mf_hcf_tiles_case():
    tile = random.choice([6, 8, 10, 12, 15, 18, 20, 24, 30])
    m = random.randint(2, 9)
    n = random.randint(2, 9)
    while math.gcd(m, n) != 1:
        n = random.randint(2, 9)
    length, width = tile * m, tile * n
    return length, width, tile


def _mf_number_from_hcf_lcm_case():
    hcf = random.randint(2, 12)
    m = random.randint(2, 10)
    n = random.randint(2, 10)
    while math.gcd(m, n) != 1:
        n = random.randint(2, 10)
    lcm = hcf * m * n
    known = hcf * m
    unknown = hcf * n
    return hcf, lcm, known, unknown


def _mf_divisibility_case():
    rule = random.choice([3, 5, 6, 9])
    if rule == 3:
        d1, d3 = random.randint(1, 9), random.randint(0, 9)
        options = [d for d in range(10) if (d1 + d + d3) % 3 == 0]
        digits = ", ".join(str(d) for d in options)
        template = f"{d1}_ {d3}"
        reason = f"Digit sum {d1} + the missing digit + {d3} must be a multiple of 3."
    elif rule == 5:
        d1 = random.randint(1, 9)
        template = f"{d1}_ 5" if random.random() < 0.5 else f"{d1}_ 0"
        digits = "any digit (0–9)" if template.endswith("5") else "0 only for 10; 0 or 5 for 5"
        reason = "Numbers divisible by 5 end in 0 or 5."
    elif rule == 6:
        d1 = random.randint(1, 9)
        options = [d for d in range(10) if (d1 + d + 4) % 3 == 0]
        digits = ", ".join(str(d) for d in options)
        template = f"{d1}_ 4"
        reason = "Must be even (ends in 4) and the digit sum must be divisible by 3."
    else:
        d1, d2 = random.randint(1, 9), random.randint(0, 9)
        options = [d for d in range(10) if (d1 + d2 + d) % 9 == 0]
        digits = ", ".join(str(d) for d in options)
        template = f"{d1}{d2}_"
        reason = f"Digit sum {d1} + {d2} + the missing digit must be a multiple of 9."
    return rule, template.replace(" ", ""), digits, reason


def _mf_primes_between(lo, hi):
    return [p for p in range(max(2, lo + 1), hi) if _mf_is_prime(p)]


def gcse_mf_find_multiple():
    n = random.randint(3, 15)
    k = random.randint(3, 12)
    ans = n * k
    q = rf"Write down the {k}th multiple of {n}."
    s = rf"The {k}th multiple of {n} is {n} × {k} = <strong>{ans}</strong>"
    hint = "Multiply the number by the position in the list."
    return q, s, hint, 1


def gcse_mf_find_factor():
    n = _mf_random_composite(12, 150)
    factors = _mf_all_factors(n)
    proper = [f for f in factors if f not in (1, n)] or factors
    ans = random.choice(proper)
    q = rf"Write down a factor of {n}."
    s = rf"One factor of {n} is <strong>{ans}</strong> because it divides exactly into {n}."
    hint = "A factor divides exactly with no remainder."
    return q, s, hint, 1


def gcse_mf_factor_pairs():
    n = _mf_random_composite(18, 120)
    pairs_str = _mf_factor_pairs_str(n)
    q = rf"Write down all the factor pairs of {n}."
    s = rf"The factor pairs of {n} are <strong>{pairs_str}</strong>."
    hint = "Start with 1 and the number itself, then test 2, 3, 4 and so on."
    return q, s, hint, 2


def gcse_mf_prime():
    n, is_prime = _mf_random_prime_check()
    q = rf"Is {n} a prime number? Give a reason."
    if is_prime:
        s = rf"Yes. <strong>{n}</strong> is prime because it has exactly two factors: 1 and {n}."
    else:
        div = _mf_small_divisor(n)
        s = rf"No. <strong>{n}</strong> is not prime because it is divisible by {div}."
    hint = "A prime number has exactly two factors: 1 and itself."
    return q, s, hint, 1


def gcse_mf_hcf():
    a, b = _mf_random_pair(8, 96)
    ans = _mf_hcf(a, b)
    q = rf"Find the highest common factor of {a} and {b}."
    s = rf"The highest common factor is the largest number that divides both exactly.<br><strong>HCF = {ans}</strong>"
    hint = "List the factors of both numbers, then choose the greatest common one."
    return q, s, hint, 2


def gcse_mf_lcm():
    a, b = _mf_random_pair(3, 24)
    ans = _mf_lcm(a, b)
    q = rf"Find the lowest common multiple of {a} and {b}."
    s = rf"The lowest common multiple is the smallest number in both times tables.<br><strong>LCM = {ans}</strong>"
    hint = "List multiples of both numbers until you find the first common one."
    return q, s, hint, 2


def gcse_mf_prime_factors():
    n = random.choice([
        random.randint(24, 48),
        random.randint(50, 99),
        random.randint(100, 250),
    ])
    while _mf_is_prime(n):
        n += 1
    ans = _mf_pf_string(n)
    q = rf"Write {n} as a product of prime factors."
    s = rf"The product of prime factors of {n} is <strong>{ans}</strong>."
    hint = "Use a factor tree and keep splitting until all branches are prime."
    return q, s, hint, 3


# ── Multiples & factors: intermediate (word problems / reasoning) ─────────────

def gcse_mf_lcm_buses_word():
    """LCM in context — when two events coincide again."""
    a, b, lcm, start, ans_time = _mf_lcm_buses_case()
    q = (
        rf"Bus A leaves a station every {a} minutes. Bus B leaves every {b} minutes. "
        rf"They both leave at {start}. At what time will they next leave together?"
    )
    s = (
        rf"Find the LCM of {a} and {b}.<br>"
        rf"LCM({a}, {b}) = {lcm} minutes<br>"
        rf"Next together: {start} + {lcm} minutes = <strong>{ans_time}</strong>"
    )
    hint = "The next time they coincide is the lowest common multiple of the two intervals."
    return q, s, hint, 3


def gcse_mf_hcf_tiles_word():
    """HCF in context — largest square tile for a rectangle."""
    length, width, tile = _mf_hcf_tiles_case()
    tile_str = f"{tile} cm"
    q = (
        rf"A rectangular floor measures {length} cm by {width} cm. "
        rf"Square tiles are used with no gaps or overlaps. "
        rf"What is the side length of the <strong>largest</strong> possible square tile?"
    )
    s = (
        rf"The tile side length must divide both {length} and {width}.<br>"
        rf"HCF({length}, {width}) = <strong>{tile_str}</strong>"
    )
    hint = "The largest square tile is the highest common factor of the length and width."
    return q, s, hint, 3


def gcse_mf_common_factors_count():
    """Count how many factors two numbers share."""
    a, b = _mf_random_pair(12, 96)
    common = sorted(set(_mf_all_factors(a)) & set(_mf_all_factors(b)))
    count = len(common)
    listed = ", ".join(str(x) for x in common)
    q = rf"How many factors do {a} and {b} have <strong>in common</strong>?"
    s = (
        rf"List factors of each number and identify those in both lists.<br>"
        rf"Common factors: {listed}<br>"
        rf"There are <strong>{count}</strong> common factors."
    )
    hint = "List all factors of each number, then count how many appear in both lists."
    return q, s, hint, 2


def gcse_mf_hcf_using_primes():
    """HCF from prime factorisations (method shown)."""
    a, b = _mf_random_pair(24, 180)
    pf_a, pf_b = _mf_pf_string(a), _mf_pf_string(b)
    hcf, pf_hcf = _mf_hcf_pf_string(a, b)
    q = rf"Find the HCF of {a} and {b} using prime factorisation."
    s = (
        rf"{a} = {pf_a}<br>{b} = {pf_b}<br>"
        rf"Take the <strong>lowest power of each common prime</strong>: {pf_hcf}<br>"
        rf"HCF = <strong>{hcf}</strong>"
    )
    hint = "Write both numbers as products of primes, then multiply the lowest index of each shared prime."
    return q, s, hint, 3


def gcse_mf_divisibility_digit():
    """Find a missing digit using divisibility rules."""
    rule, template, digits, reason = _mf_divisibility_case()
    q = (
        rf"The number {template} is divisible by {rule}. "
        rf"Which digit(s) could replace the blank?"
    )
    s = (
        rf"{reason}<br>"
        rf"Possible digits: <strong>{digits}</strong>"
    )
    hint = "Use divisibility rules for 2, 3, 5, 6, 9 and 10 as appropriate."
    return q, s, hint, 2


# ── Multiples & factors: difficult (multi-step / puzzles) ─────────────────────

def gcse_mf_hcf_three_numbers():
    """HCF of three numbers."""
    a, b = _mf_random_pair(12, 72)
    c = random.randint(12, 96)
    ans = _mf_hcf(_mf_hcf(a, b), c)
    q = rf"Find the highest common factor of {a}, {b} and {c}."
    s = (
        rf"HCF({a}, {b}) = {_mf_hcf(a, b)}<br>"
        rf"HCF({_mf_hcf(a, b)}, {c}) = <strong>{ans}</strong>"
    )
    hint = "Find the HCF of two numbers first, then find the HCF of that result with the third."
    return q, s, hint, 3


def gcse_mf_lcm_three_numbers():
    """LCM of three numbers."""
    a, b = _mf_random_pair(3, 18)
    c = random.randint(3, 20)
    ans = _mf_lcm(_mf_lcm(a, b), c)
    q = rf"Find the lowest common multiple of {a}, {b} and {c}."
    s = (
        rf"LCM({a}, {b}) = {_mf_lcm(a, b)}<br>"
        rf"LCM({_mf_lcm(a, b)}, {c}) = <strong>{ans}</strong>"
    )
    hint = "Find the LCM of two numbers first, then the LCM of that result with the third."
    return q, s, hint, 3


def gcse_mf_hcf_lcm_product_rule():
    """Verify and use HCF × LCM = product of the two numbers."""
    a, b = _mf_random_pair(8, 72)
    hcf = _mf_hcf(a, b)
    lcm = _mf_lcm(a, b)
    q = (
        rf"For {a} and {b}, find the HCF and LCM and show that "
        rf"HCF × LCM = {a} × {b}."
    )
    s = (
        rf"HCF = <strong>{hcf}</strong>, LCM = <strong>{lcm}</strong><br>"
        rf"HCF × LCM = {hcf} × {lcm} = {hcf * lcm}<br>"
        rf"{a} × {b} = {a * b}<br>"
        rf"So HCF × LCM = product of the numbers ✓"
    )
    hint = "This relationship is always true for two positive integers."
    return q, s, hint, 3


def gcse_mf_number_from_hcf_lcm():
    """Find a missing number given HCF, LCM and the other number."""
    hcf, lcm, known, unknown = _mf_number_from_hcf_lcm_case()
    q = (
        rf"Two numbers have HCF {hcf} and LCM {lcm}. "
        rf"One of the numbers is {known}. Find the other number."
    )
    s = (
        rf"Use HCF × LCM = product of the two numbers.<br>"
        rf"{hcf} × {lcm} = {hcf * lcm}<br>"
        rf"Other number = {hcf * lcm} ÷ {known} = <strong>{unknown}</strong>"
    )
    hint = "Multiply HCF by LCM, then divide by the number you know."
    return q, s, hint, 4


def gcse_mf_lcm_from_prime_forms():
    """LCM from prime factorisation forms."""
    a, b = _mf_random_pair(8, 60)
    lcm, pf_lcm = _mf_lcm_pf_string(a, b)
    form_a = f"{a} = {_mf_pf_string(a)}"
    form_b = f"{b} = {_mf_pf_string(b)}"
    q = rf"Find the LCM of {form_a} and {form_b}."
    s = (
        rf"Take the <strong>highest power</strong> of each prime that appears:<br>"
        rf"LCM = {pf_lcm} = <strong>{lcm}</strong>"
    )
    hint = "For LCM, use the highest index of each prime in either factorisation."
    return q, s, hint, 3


def gcse_mf_primes_in_range():
    """List primes in a given range."""
    lo = random.randint(10, 55)
    hi = lo + random.randint(10, 30)
    primes = _mf_primes_between(lo, hi)
    listed = ", ".join(str(p) for p in primes)
    q = rf"List all the prime numbers between {lo} and {hi}."
    s = rf"Using a sieve or systematic testing: <strong>{listed}</strong>"
    hint = "Test each number for factors; only 1 and itself means prime."
    return q, s, hint, 3


def gcse_maths_multiples_factors(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        from generators.gcse.maths_basic_topics_mcq import gcse_maths_multiples_factors_mcq
        return gcse_maths_multiples_factors_mcq(difficulty, variant_name)
    if variant_name:
        return _basic_maths_practice('multiples_factors', difficulty, mode, variant_name)
    if difficulty == 'foundational':
        variant = random.choice([
            gcse_mf_find_multiple,
            gcse_mf_find_factor,
            gcse_mf_prime
        ])
    elif difficulty == 'intermediate':
        variant = random.choice([
            gcse_mf_factor_pairs,
            gcse_mf_hcf,
            gcse_mf_lcm,
            gcse_mf_lcm_buses_word,
            gcse_mf_hcf_tiles_word,
            gcse_mf_common_factors_count,
            gcse_mf_hcf_using_primes,
            gcse_mf_divisibility_digit,
        ])
    else:
        variant = random.choice([
            gcse_mf_prime_factors,
            gcse_mf_hcf_three_numbers,
            gcse_mf_lcm_three_numbers,
            gcse_mf_hcf_lcm_product_rule,
            gcse_mf_number_from_hcf_lcm,
            gcse_mf_lcm_from_prime_forms,
            gcse_mf_primes_in_range,
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'multiples_factors')




# ─────────────────────────────────────────────────────────────
#  GCSE MATHS — DECIMALS
# ─────────────────────────────────────────────────────────────

def _dec_random_mixed_ops():
    while True:
        a = round(random.uniform(2.0, 9.0), 1)
        b = round(random.uniform(0.5, 5.0), 1)
        c = random.choice([0.2, 0.25, 0.4, 0.5, 0.8])
        op = random.choice(["+", "-"])
        inner_val = round(a + b if op == "+" else a - b, 2)
        if inner_val <= 0:
            continue
        ans = round(inner_val / c, 2)
        if abs(ans * c - inner_val) < 0.01:
            op_sym = "+" if op == "+" else "−"
            inner_expr = f"{a} {op_sym} {b}"
            return inner_expr, inner_val, c, ans


def _dec_random_unit_price():
    mass = round(random.choice([0.5, 0.75, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0]), 2)
    per_kg = round(random.uniform(1.80, 6.50), 2)
    total = round(mass * per_kg, 2)
    return mass, total, per_kg


def _dec_bounds_from_value(value, dp):
    half = 0.05 if dp == 1 else 0.005 if dp == 2 else 0.0005
    lower = round(value - half, dp + 1)
    upper = round(value + half, dp + 1)
    return lower, upper, half


def gcse_dec_ordering():
    """Foundational: order a list of decimals"""
    import random
    base = random.randint(1, 9) / 10
    decimals = sorted(set([
        round(base + random.randint(0, 9) / 100 + random.randint(0, 9) / 1000, 3)
        for _ in range(5)
    ]))
    random.shuffle(decimals)
    ordered = sorted(decimals)
    q = rf"Write these decimals in order from smallest to largest:<br><br><strong>{', '.join(str(d) for d in decimals)}</strong>"
    compare_lines = []
    for d in decimals:
        padded = f"{d:.3f}"
        compare_lines.append(f"{d} = {padded}")
    s = (
        rf"Write each value to 3 decimal places so place values line up:<br>"
        + "<br>".join(compare_lines)
        + rf"<br>Compare digit by digit (tenths, then hundredths, then thousandths).<br>"
        rf"Smallest to largest: <strong>{', '.join(str(d) for d in ordered)}</strong>"
    )
    hint = (
        r"Pad every number to the same number of decimal places (e.g. write 0.4 as 0.400). "
        r"Then compare from left to right — the first place where digits differ tells you which is larger."
    )
    return q, s, hint, 1

def gcse_dec_add_subtract():
    """Foundational: add or subtract two decimals"""
    import random
    a = round(random.uniform(1.0, 50.0), 2)
    b = round(random.uniform(1.0, 20.0), 2)
    op = random.choice(['+', '−'])
    result = round(a + b, 2) if op == '+' else round(a - b, 2)
    q = rf"Calculate {a} {op} {b}"
    verb = 'add' if op == '+' else 'subtract'
    s = (
        rf"Line up the decimal points and {verb} column by column (hundredths, then tenths, then units):<br>"
        rf"&nbsp;&nbsp;{a}<br>"
        rf"{op} {b}<br>"
        rf"= <strong>{result}</strong>"
    )
    hint = (
        r"Write one number above the other with decimal points aligned. "
        r"Add zeros on the right if needed so both numbers have the same number of decimal places, "
        r"then work from right to left like whole-number column addition or subtraction."
    )
    return q, s, hint, 1

def gcse_dec_multiply_power10():
    """Foundational: multiply or divide a decimal by a power of 10"""
    import random
    base = round(random.uniform(0.1, 99.9), 3)
    power = random.choice([10, 100, 1000])
    op = random.choice(['×', '÷'])
    if op == '×':
        result = round(base * power, 4)
        direction = "right"
        places = {10: 1, 100: 2, 1000: 3}[power]
    else:
        result = round(base / power, 6)
        direction = "left"
        places = {10: 1, 100: 2, 1000: 3}[power]
    # clean up trailing zeros in display
    result_str = f"{result:.10f}".rstrip('0').rstrip('.')
    q = rf"Calculate {base} {op} {power}"
    s = (
        rf"{'Multiplying' if op == '×' else 'Dividing'} by {power} moves every digit "
        rf"{places} place{'s' if places > 1 else ''} to the {direction}:<br>"
        rf"{base} → move the decimal point {places} place{'s' if places > 1 else ''} {direction}<br>"
        rf"= <strong>{result_str}</strong>"
    )
    hint = (
        rf"× {power}: shift the decimal point {places} place(s) to the right "
        rf"(each jump ×10). ÷ {power}: shift {places} place(s) to the left. "
        rf"Add placeholder zeros if a digit would move past the end of the number."
    )
    return q, s, hint, 1

def gcse_dec_multiply():
    """Intermediate: multiply two decimals"""
    import random
    a = round(random.uniform(1.1, 9.9), 1)
    b = round(random.uniform(1.1, 9.9), 1)
    result = round(a * b, 2)
    a_int = int(a * 10)
    b_int = int(b * 10)
    int_product = a_int * b_int
    q = rf"Calculate {a} × {b}. Show your working."
    s = (
        rf"Step 1 — remove the decimal points and multiply as whole numbers:<br>"
        rf"{a_int} × {b_int} = {int_product}<br>"
        rf"Step 2 — count decimal places: {a} has 1 d.p. and {b} has 1 d.p., so the answer needs 2 d.p.<br>"
        rf"Step 3 — put the decimal point back in {int_product}: <strong>{result}</strong>"
    )
    hint = (
        r"Treat the numbers as integers (e.g. 2.4 → 24), multiply, then count how many decimal "
        r"places were in both factors combined and insert the point that many places from the right."
    )
    return q, s, hint, 2

def gcse_dec_divide():
    """Intermediate: divide a decimal by a decimal"""
    import random
    b = round(random.choice([0.2, 0.4, 0.5, 0.25, 0.05, 0.02, 0.8]), 2)
    result = random.randint(2, 20)
    a = round(b * result, 4)
    # determine multiplier to clear divisor
    b_str = str(b)
    dp = len(b_str.split('.')[-1]) if '.' in b_str else 0
    mult = 10 ** dp
    a_int = int(round(a * mult))
    b_int = int(round(b * mult))
    q = rf"Calculate {a} ÷ {b}"
    s = (
        rf"Step 1 — multiply both numbers by {mult} so the divisor {b} becomes a whole number:<br>"
        rf"{a} × {mult} = {a_int} &nbsp;&nbsp;and&nbsp;&nbsp; {b} × {mult} = {b_int}<br>"
        rf"Step 2 — divide: {a_int} ÷ {b_int} = <strong>{result}</strong>"
    )
    hint = (
        rf"Scale both dividend and divisor by the same power of 10 until {b} has no decimal point. "
        rf"The quotient is unchanged, but the division becomes a standard whole-number calculation."
    )
    return q, s, hint, 2

def gcse_dec_round():
    """Foundational: round a decimal to a specified number of decimal places"""
    import random
    n = round(random.uniform(0.001, 999.999), 4)
    dp = random.choice([1, 2, 3])
    result = round(n, dp)
    n_str = f"{n:.4f}"
    parts = n_str.split('.')
    decide_digit = parts[1][dp] if len(parts) > 1 and len(parts[1]) > dp else '0'
    ordinals = ['', '1st', '2nd', '3rd', '4th']
    q = rf"Round {n} to {dp} decimal place{'s' if dp > 1 else ''}."
    s = (
        rf"Identify the deciding digit — the {ordinals[dp + 1]} decimal place: <strong>{decide_digit}</strong><br>"
        rf"{'5 or more → round the last kept digit up.' if int(decide_digit) >= 5 else 'Less than 5 → keep the last digit unchanged.'}<br>"
        rf"<strong>{result}</strong>"
    )
    hint = (
        rf"Find the digit one place beyond where you are rounding. "
        rf"If it is 5 or above, increase the last kept digit by 1; otherwise leave it as it is."
    )
    return q, s, hint, 1

def gcse_dec_fraction_to_decimal():
    """Intermediate: convert a fraction to a decimal by long division"""
    if random.random() < 0.75:
        num, den = _fdp_random_terminating_fraction()
        dec_str = _fdp_format_decimal(num / den)
        q = rf"Convert {num}/{den} to a decimal."
        s = (
            rf"Divide the numerator by the denominator:<br>"
            rf"{num} ÷ {den} = <strong>{dec_str}</strong><br>"
            rf"(Set up short division: how many times {den} goes into {num}, "
            rf"then continue with remainders × 10 for each decimal place.)"
        )
        hint = (
            r"Use short division — divide the top number by the bottom. "
            r"After the whole-number part, add a decimal point and keep dividing; "
            r"each remainder is multiplied by 10 for the next digit."
        )
    else:
        num, den = _fdp_random_recurring_fraction()
        dec_str = _fdp_recurring_decimal_display(num, den)
        q = rf"Convert {num}/{den} to a decimal."
        s = (
            rf"Divide {num} ÷ {den} using short division.<br>"
            rf"The remainder eventually repeats, so the decimal recurs:<br>"
            rf"<strong>{dec_str}</strong><br>"
            rf"(When the same remainder appears again, the digit pattern from that point repeats forever.)"
        )
        hint = (
            r"Carry out long or short division. Track remainders — when a remainder repeats, "
            r"the digits from that point onward form the recurring block (write … or a dot over the repeat)."
        )
    return q, s, hint, 1


# ── Decimals: intermediate (extra formats) ───────────────────────────────────

def gcse_dec_practice_word_total():
    """Total cost from unit price and quantity."""
    import random
    unit = round(random.choice([1.25, 1.50, 2.35, 2.80, 3.45, 4.20]), 2)
    qty = random.randint(4, 15)
    total = round(unit * qty, 2)
    q = rf"A shop sells items at £{unit} each. How much do {qty} items cost?"
    s = (
        rf"Total cost = unit price × quantity<br>"
        rf"£{unit} × {qty} = <strong>£{total}</strong><br>"
        rf"(Multiply as whole numbers if helpful, then place the decimal point.)"
    )
    hint = (
        r"Multiply the price of one item by how many you buy. "
        r"Line up decimal points or treat pence as whole numbers (e.g. £1.25 → 125p × quantity)."
    )
    return q, s, hint, 2


def gcse_dec_practice_decimal_to_fraction():
    """Write a terminating decimal as a fraction in simplest form."""
    num, den = _fdp_random_terminating_fraction()
    dec = num / den
    dec_str = _fdp_format_decimal(dec)
    q = rf"Write {dec_str} as a fraction in its simplest form."
    places = len(dec_str.split(".")[-1]) if "." in dec_str else 0
    raw_num = int(round(dec * (10 ** places)))
    raw_den = 10 ** places
    g = math.gcd(raw_num, raw_den)
    s = (
        rf"Step 1 — write the decimal over a power of 10 ({places} decimal place{'s' if places != 1 else ''}):<br>"
        rf"{dec_str} = {raw_num}/{raw_den}<br>"
        rf"Step 2 — cancel common factors (HCF = {g}):<br>"
        rf"{raw_num}÷{g} = {num}, &nbsp; {raw_den}÷{g} = {den}<br>"
        rf"Simplest form: <strong>{_fdp_fraction_str(num, den)}</strong>"
    )
    hint = (
        r"Count decimal places: e.g. 0.375 has 3, so write 375/1000. "
        r"Then divide numerator and denominator by their highest common factor until no number "
        r"other than 1 divides both."
    )
    return q, s, hint, 2


def gcse_dec_practice_estimate_product():
    """Estimate a product by rounding each decimal."""
    import random
    a = round(random.uniform(2.1, 9.8), 1)
    b = round(random.uniform(1.2, 6.5), 1)
    a_est = round(a)
    b_est = round(b)
    est = a_est * b_est
    exact = round(a * b, 2)
    q = rf"Estimate {a} × {b} by rounding each number to the nearest whole number."
    s = (
        rf"Round each factor to the nearest integer:<br>"
        rf"{a} ≈ {a_est} &nbsp; (nearest whole number)<br>"
        rf"{b} ≈ {b_est} &nbsp; (nearest whole number)<br>"
        rf"Estimate: {a_est} × {b_est} = <strong>{est}</strong><br>"
        rf"(Exact value is {exact} — your estimate checks the answer is about the right size.)"
    )
    hint = (
        r"Round each decimal to the nearest whole number (0.5 and above rounds up). "
        r"Multiply those rounded values — this gives a quick, sensible approximation of the true product."
    )
    return q, s, hint, 2


def gcse_dec_practice_order_mixed():
    """Order a mix of decimals and simple fractions."""
    items, order_str = _fdp_random_order_items(3)
    random.shuffle(items)
    q = (
        rf"Write these values in order from smallest to largest:<br><br>"
        rf"<strong>{', '.join(label for label, _ in items)}</strong>"
    )
    conv_lines = []
    for lab, val in items:
        conv_lines.append(f"{lab} = {_fdp_format_decimal(val)}")
    s = (
        r"Convert every value to a decimal so they can be compared:<br>"
        + "<br>".join(conv_lines)
        + rf"<br>Order from smallest to largest: <strong>{order_str}</strong>"
    )
    hint = (
        r"Put all values in the same form — usually decimals. "
        r"Divide fractions (top ÷ bottom), move the decimal point for percentages (÷ 100), "
        r"then compare place values from left to right."
    )
    return q, s, hint, 2


# ── Decimals: difficult (extra formats) ──────────────────────────────────────

def gcse_dec_recurring():
    """Write a recurring decimal as a fraction (algebraic method)."""
    num, den = _fdp_random_recurring_fraction()
    dec = _fdp_recurring_decimal_display(num, den)
    s, hint = _fdp_recurring_algebra_steps(num, den)
    q = rf"Write {dec} as a fraction in its simplest form. Show your working."
    return q, s, hint, 3


def gcse_dec_practice_mixed_ops():
    """Multi-step calculation with decimals and brackets."""
    inner, inner_val, c, ans = _dec_random_mixed_ops()
    mult = 10 if c < 0.1 else 1
    scaled_inner = int(round(inner_val * mult))
    scaled_c = int(round(c * mult))
    q = rf"Calculate ({inner}) ÷ {c}"
    s = (
        rf"Step 1 — work out the bracket first:<br>"
        rf"{inner} = {inner_val}<br>"
        rf"Step 2 — divide {inner_val} ÷ {c}"
        + (rf" (multiply both by {mult}: {scaled_inner} ÷ {scaled_c})" if mult > 1 else "")
        + rf":<br>"
        rf"<strong>{ans}</strong>"
    )
    hint = (
        r"Always evaluate brackets before division. "
        r"If the divisor is a decimal, multiply both numbers by 10 (or 100) "
        r"to make the divisor a whole number, then divide."
    )
    return q, s, hint, 3


def gcse_dec_practice_bounds():
    """Upper and lower bounds from a measurement given to d.p."""
    dp = random.choice([1, 2])
    value = round(random.uniform(2.0, 18.0), dp)
    lower, upper, half = _dec_bounds_from_value(value, dp)
    q = (
        rf"A length is recorded as {value} cm correct to {dp} decimal place"
        f"{'s' if dp > 1 else ''}. "
        rf"Write the error interval for the true length."
    )
    s = (
        rf"The value is rounded to {dp} d.p., so the unit of accuracy is "
        rf"{'0.1 cm' if dp == 1 else '0.01 cm'}.<br>"
        rf"Half of that = {half} cm (add and subtract from {value}).<br>"
        rf"Lower bound = {value} − {half} = {lower}<br>"
        rf"Upper bound = {value} + {half} = {upper} (not included)<br>"
        rf"Error interval: <strong>{lower} ≤ length &lt; {upper} cm</strong>"
    )
    hint = (
        r"A measurement to n decimal places is accurate to ± half of the last place "
        r"(e.g. 1 d.p. → ±0.05). Add half to get the upper bound and subtract half for the lower bound. "
        r"The upper value is not included in the interval."
    )
    return q, s, hint, 3


def gcse_dec_practice_word_unit_price():
    """Find unit price or amount from a total."""
    mass, total, per_kg = _dec_random_unit_price()
    q = (
        rf"{mass} kg of fruit costs £{total:.2f}. "
        rf"Find the cost per kilogram."
    )
    s = (
        rf"Cost per kg = total cost ÷ mass<br>"
        rf"£{total:.2f} ÷ {mass} kg = <strong>£{per_kg:.2f} per kg</strong><br>"
        rf"(Divide as usual; you can scale both numbers to clear the decimal in {mass} if needed.)"
    )
    hint = (
        r"Unit price means 'cost for 1 kg'. Divide the total bill by the number of kilograms. "
        r"If the mass is a decimal, multiply top and bottom by 10 to make division easier."
    )
    return q, s, hint, 3


# ── Decimals: procedural practice (extra variants) ───────────────────────────

def gcse_dec_proc_three_add():
    """Foundational: add three decimals."""
    vals = [round(random.uniform(0.5, 12.0), 2) for _ in range(3)]
    result = round(sum(vals), 2)
    expr = " + ".join(str(v) for v in vals)
    q = rf"Calculate {expr}"
    s = (
        rf"Line up all three numbers by their decimal points and add column by column:<br>"
        + "<br>".join(f"&nbsp;&nbsp;{v}" for v in vals)
        + rf"<br>+ (total)<br>"
        rf"= <strong>{result}</strong>"
    )
    hint = (
        r"Write all numbers to the same number of decimal places, stack them with points aligned, "
        r"then add from right to left — carry into the next column when a column sums to 10 or more."
    )
    return q, s, hint, 1


def gcse_dec_proc_divide_power10():
    """Foundational: divide a decimal by a power of 10."""
    base = round(random.uniform(1.0, 450.0), 2)
    power = random.choice([10, 100, 1000])
    places = {10: 1, 100: 2, 1000: 3}[power]
    result = round(base / power, places + 2)
    result_str = f"{result:.10f}".rstrip("0").rstrip(".")
    q = rf"Calculate {base} ÷ {power}"
    s = (
        rf"Dividing by {power} shifts every digit {places} place{'s' if places > 1 else ''} to the left:<br>"
        rf"{base} → move the decimal point {places} place{'s' if places > 1 else ''} left<br>"
        rf"= <strong>{result_str}</strong>"
    )
    hint = (
        rf"÷ {power} moves the decimal point {places} place(s) left. "
        rf"Add a leading zero if the point moves past the start of the number (e.g. 4.5 ÷ 10 = 0.45)."
    )
    return q, s, hint, 1


def gcse_dec_proc_difference():
    """Foundational: find the difference between two decimals."""
    lo = round(random.uniform(1.0, 8.0), 2)
    hi = round(lo + random.uniform(0.5, 6.0), 2)
    diff = round(hi - lo, 2)
    q = rf"Find the difference between {hi} and {lo}."
    s = (
        rf"Difference = larger value − smaller value<br>"
        rf"{hi} − {lo} = <strong>{diff}</strong><br>"
        rf"(Line up decimal points and subtract column by column.)"
    )
    hint = (
        r"'Difference' means subtract the smaller number from the larger. "
        r"Align decimal points, add trailing zeros if needed, then subtract."
    )
    return q, s, hint, 1


def gcse_dec_proc_money_change():
    """Intermediate: calculate change from a cash payment."""
    price = round(random.uniform(1.50, 18.50), 2)
    paid = round(math.ceil(price) + random.choice([0, 0.5, 1.0, 2.0, 5.0]), 2)
    while paid < price:
        paid = round(paid + 1.0, 2)
    change = round(paid - price, 2)
    q = rf"An item costs £{price:.2f}. How much change from £{paid:.2f}?"
    s = (
        rf"Change = amount paid − price<br>"
        rf"£{paid:.2f} − £{price:.2f} = <strong>£{change:.2f}</strong><br>"
        rf"(Subtract the pence column first, then the pounds.)"
    )
    hint = (
        r"Subtract the price from the amount handed over. "
        r"Line up the pounds and pence columns, or convert both to pence (× 100) and subtract."
    )
    return q, s, hint, 2


def gcse_dec_proc_mean():
    """Intermediate: mean of four decimals."""
    vals = [round(random.uniform(1.0, 9.0), 1) for _ in range(4)]
    total = round(sum(vals), 2)
    mean = round(total / 4, 2)
    q = rf"Find the mean of {', '.join(str(v) for v in vals)}."
    s = (
        rf"Step 1 — add all values: {' + '.join(str(v) for v in vals)} = {total}<br>"
        rf"Step 2 — divide by how many values (4): {total} ÷ 4 = <strong>{mean}</strong>"
    )
    hint = (
        r"Mean = total ÷ count. Add every value first, then divide the sum by how many numbers there are."
    )
    return q, s, hint, 2


def gcse_dec_proc_map_scale():
    """Intermediate: map scale with decimal distances."""
    cm_per_km = random.choice([0.5, 1.0, 2.0, 4.0])
    map_cm = round(random.uniform(2.0, 8.0), 1)
    real_km = round(map_cm / cm_per_km, 2)
    q = (
        rf"On a map, {cm_per_km} cm represents 1 km. "
        rf"Two towns are {map_cm} cm apart on the map. How far apart are they in km?"
    )
    s = (
        rf"Scale: {cm_per_km} cm on the map = 1 km in real life<br>"
        rf"Real distance = map distance ÷ {cm_per_km}<br>"
        rf"{map_cm} ÷ {cm_per_km} = <strong>{real_km} km</strong>"
    )
    hint = (
        rf"Each {cm_per_km} cm on the map stands for 1 km. "
        rf"Divide the map measurement by {cm_per_km} to find how many kilometres it represents."
    )
    return q, s, hint, 2


def gcse_dec_proc_multi_step_shop():
    """Difficult: total cost with multiple items and a discount."""
    unit = round(random.choice([1.25, 1.80, 2.40, 3.15, 4.50]), 2)
    qty = random.randint(3, 8)
    subtotal = round(unit * qty, 2)
    discount_pct = random.choice([10, 20])
    discount = round(subtotal * discount_pct / 100, 2)
    total = round(subtotal - discount, 2)
    q = (
        rf"{qty} items cost £{unit} each. "
        rf"A <strong>{discount_pct}%</strong> discount is applied to the total. "
        rf"What is the final price?"
    )
    s = (
        rf"Step 1 — full price before discount:<br>"
        rf"£{unit} × {qty} = £{subtotal:.2f}<br>"
        rf"Step 2 — discount ({discount_pct}% of £{subtotal:.2f}):<br>"
        rf"{discount_pct}% × £{subtotal:.2f} = £{discount:.2f}<br>"
        rf"Step 3 — subtract discount:<br>"
        rf"£{subtotal:.2f} − £{discount:.2f} = <strong>£{total:.2f}</strong>"
    )
    hint = (
        r"Work in order: find the cost of all items, calculate the percentage off that subtotal "
        r"(divide by 100, then multiply by the percentage), then subtract the discount from the subtotal."
    )
    return q, s, hint, 3


def gcse_dec_proc_bounds_dynamic():
    """Difficult: error interval from a rounded measurement."""
    dp = random.choice([1, 2])
    if dp == 1:
        value = round(random.uniform(2.0, 15.0), 1)
        half = 0.05
    else:
        value = round(random.uniform(2.0, 15.0), 2)
        half = 0.005
    lower = round(value - half, dp + 1)
    upper = round(value + half, dp + 1)
    q = (
        rf"A mass is measured as <strong>{value}</strong> kg correct to {dp} decimal "
        f"place{'s' if dp > 1 else ''}. Write the error interval."
    )
    s = (
        rf"Rounded to {dp} d.p. → unit of accuracy is {'0.1 kg' if dp == 1 else '0.01 kg'}.<br>"
        rf"Half of that = {half} kg.<br>"
        rf"Lower bound: {value} − {half} = {lower} kg<br>"
        rf"Upper bound: {value} + {half} = {upper} kg (not included)<br>"
        rf"Error interval: <strong>{lower} ≤ mass &lt; {upper} kg</strong>"
    )
    hint = (
        r"The true value lies within half a unit of the last decimal place above and below the recorded value. "
        r"Write as lower ≤ true value < upper — the upper limit is never included."
    )
    return q, s, hint, 3


def gcse_dec_proc_density():
    """Difficult: density from mass and volume (decimals)."""
    volume = round(random.choice([0.5, 0.8, 1.2, 2.5, 4.0]), 1)
    density = random.randint(2, 9)
    mass = round(volume * density, 2)
    q = (
        rf"A block has mass <strong>{mass} g</strong> and volume <strong>{volume} cm³</strong>. "
        rf"Calculate its density in g/cm³."
    )
    s = (
        rf"Density = mass ÷ volume<br>"
        rf"{mass} g ÷ {volume} cm³ = <strong>{density} g/cm³</strong><br>"
        rf"(Multiply both by 10 if needed to clear the decimal in the volume.)"
    )
    hint = (
        r"Use the formula density = mass ÷ volume. Substitute the given values and divide; "
        r"scale numerator and denominator by the same power of 10 if the volume is a decimal."
    )
    return q, s, hint, 3


def gcse_maths_decimals(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        from generators.gcse.maths_basic_topics_mcq import gcse_maths_decimals_mcq
        return gcse_maths_decimals_mcq(difficulty, variant_name)
    if variant_name:
        return _basic_maths_practice('decimals', difficulty, mode, variant_name)
    pools = {
        'foundational': [
            gcse_dec_ordering, gcse_dec_add_subtract,
            gcse_dec_multiply_power10, gcse_dec_round,
            gcse_dec_fraction_to_decimal,
            gcse_dec_proc_three_add,
            gcse_dec_proc_divide_power10,
            gcse_dec_proc_difference,
        ],
        'intermediate': [
            gcse_dec_multiply, gcse_dec_divide, gcse_dec_fraction_to_decimal, gcse_dec_round,
            gcse_dec_practice_word_total, gcse_dec_practice_decimal_to_fraction,
            gcse_dec_practice_estimate_product, gcse_dec_practice_order_mixed,
            gcse_dec_proc_money_change,
            gcse_dec_proc_mean,
            gcse_dec_proc_map_scale,
        ],
        'difficult': [
            gcse_dec_recurring, gcse_dec_divide, gcse_dec_multiply, gcse_dec_round,
            gcse_dec_practice_mixed_ops, gcse_dec_practice_bounds,
            gcse_dec_practice_word_unit_price,
            gcse_dec_proc_multi_step_shop,
            gcse_dec_proc_bounds_dynamic,
            gcse_dec_proc_density,
        ],
    }
    variant = random.choice(pools.get(difficulty, pools['foundational']))

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'decimals')


# ─────────────────────────────────────────────────────────────
#  GCSE MATHS — ORDER OF OPERATIONS & NEGATIVE NUMBERS (BIDMAS)
# ─────────────────────────────────────────────────────────────

def gcse_bidmas_simple():
    """Foundational: simple BIDMAS with +, −, ×, ÷ and no brackets"""
    import random
    a = random.randint(2, 10)
    b = random.randint(2, 6)
    c = random.randint(1, 8)
    # a + b × c  →  a + (b×c)
    result = a + b * c
    q = rf"Calculate {a} + {b} × {c}"
    s = (rf"Multiplication before addition (BIDMAS):<br>"
         rf"{b} × {c} = {b*c}<br>"
         rf"{a} + {b*c} = <strong>{result}</strong>")
    hint = r"Multiply first, then add. Don't work left to right without applying BIDMAS."
    return q, s, hint, 1, result

def gcse_bidmas_brackets():
    """Foundational: BIDMAS with one set of brackets"""
    import random
    a = random.randint(1, 5)
    b = random.randint(1, 8)
    c = random.randint(2, 6)
    result = (a + b) * c
    q = rf"Calculate ( {a} + {b} ) × {c}"
    s = (rf"Brackets first:<br>"
         rf"({a} + {b}) = {a+b}<br>"
         rf"{a+b} × {c} = <strong>{result}</strong>")
    hint = r"Always evaluate what's inside the brackets before doing anything else."
    return q, s, hint, 1, result

def gcse_bidmas_power():
    """Foundational: BIDMAS with a power"""
    import random
    a = random.randint(1, 5)
    b = random.randint(2, 4)
    c = random.randint(1, 6)
    result = a * (b ** c)
    q = rf"Calculate {a} × {b}^{c}"
    s = (rf"Indices before multiplication:<br>"
         rf"{b}^{c} = {b**c}<br>"
         rf"{a} × {b**c} = <strong>{result}</strong>")
    hint = r"Indices (powers) come before multiplication in BIDMAS."
    return q, s, hint, 1, result

def gcse_bidmas_mixed():
    """Intermediate: BIDMAS combining brackets, powers, × and +/−"""
    import random
    inner_a = random.randint(2, 5)
    inner_b = random.randint(1, 4)
    p = random.randint(2, 3)
    outer = random.randint(2, 6)
    extra = random.randint(1, 10)
    inner = inner_a - inner_b
    result = outer * (inner ** p) + extra
    q = rf"Calculate {outer} × ( {inner_a} − {inner_b} )^{p} + {extra}"
    s = (rf"Step 1 — Brackets: {inner_a} − {inner_b} = {inner}<br>"
         rf"Step 2 — Indices: {inner}^{p} = {inner**p}<br>"
         rf"Step 3 — Multiply: {outer} × {inner**p} = {outer * inner**p}<br>"
         rf"Step 4 — Add: {outer * inner**p} + {extra} = <strong>{result}</strong>")
    hint = r"Follow B → I → D/M → A/S strictly. Work out each step before moving to the next."
    return q, s, hint, 2, result

def gcse_neg_add_subtract():
    """Foundational: add and subtract negative numbers"""
    import random
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    op = random.choice(['+', '−'])
    if op == '+':
        result = a + b
        q = rf"Calculate {a} + ({b})"
        if b < 0:
            s = rf"Adding a negative is the same as subtracting: {a} + ({b}) = {a} − {abs(b)} = <strong>{result}</strong>"
        else:
            s = rf"{a} + {b} = <strong>{result}</strong>"
    else:
        result = a - b
        q = rf"Calculate {a} − ({b})"
        if b < 0:
            s = rf"Subtracting a negative is the same as adding: {a} − ({b}) = {a} + {abs(b)} = <strong>{result}</strong>"
        else:
            s = rf"{a} − {b} = <strong>{result}</strong>"
    hint = r"Think of a number line. Subtracting a negative means moving right (adding). Adding a negative means moving left (subtracting)."
    return q, s, hint, 1, result

def gcse_neg_multiply_divide():
    """Foundational: multiply or divide involving negative numbers"""
    import random
    a = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
    b = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
    op = random.choice(['×', '÷'])
    if op == '×':
        result = a * b
        sign_result = "positive (−  ×  − = +)" if a < 0 and b < 0 else "negative (different signs)" if (a < 0) != (b < 0) else "positive"
        q = rf"Calculate {a} × {b}"
        s = rf"Signs: {'same signs → positive' if (a<0)==(b<0) else 'different signs → negative'}<br>{a} × {b} = <strong>{result}</strong>"
    else:
        # make sure it divides cleanly
        result = a
        b_use = random.choice([-4, -3, -2, 2, 3, 4])
        a_use = result * b_use
        q = rf"Calculate {a_use} ÷ {b_use}"
        res = a_use // b_use
        s = rf"Signs: {'same signs → positive' if (a_use<0)==(b_use<0) else 'different signs → negative'}<br>{a_use} ÷ {b_use} = <strong>{res}</strong>"
        hint = r"Same signs → positive result. Different signs → negative result."
        return q, s, hint, 1, res
    hint = r"Same signs → positive result. Different signs → negative result."
    return q, s, hint, 1, result

def gcse_neg_powers():
    """Intermediate: negative numbers with powers — bracket vs no bracket"""
    import random
    n = random.randint(2, 6)
    p = random.choice([2, 3])
    with_bracket = ((-n) ** p)
    without_bracket = -(n ** p)
    if p == 2:
        expand_a = rf"\left(-{n}\right) \times \left(-{n}\right)"
        power_phrase = "squared"
    else:
        expand_a = (
            rf"\left(-{n}\right) \times \left(-{n}\right) \times \left(-{n}\right)"
        )
        power_phrase = "cubed"
    if random.choice((True, False)):
        result = with_bracket
        q = rf"Calculate \( \left(-{n}\right)^{{{p}}} \)"
        s = (
            rf"\( \left(-{n}\right)^{{{p}}} = {expand_a} = <strong>{with_bracket}</strong> \)<br>"
            rf"The negative is <strong>inside</strong> the brackets, so it is raised to the power."
        )
        hint = (
            rf"Bracket the whole \(-{n}\) before applying the power: "
            rf"\( \left(-{n}\right)^{{{p}}} \neq -\left({n}\right)^{{{p}}} \)."
        )
    else:
        result = without_bracket
        q = rf"Calculate \( -\left({n}\right)^{{{p}}} \)"
        s = (
            rf"\( -\left({n}\right)^{{{p}}} = -\left({n**p}\right) = <strong>{without_bracket}</strong> \)<br>"
            rf"Only <strong>{n}</strong> is {power_phrase}; the minus sign stays <strong>outside</strong> the brackets."
        )
        hint = (
            rf"The power applies to {n} only; the leading minus is not inside the brackets. "
            rf"Compare with \( \left(-{n}\right)^{{{p}}} = {with_bracket} \)."
        )
    return q, s, hint, 2, result

def gcse_bidmas_with_negatives():
    """Intermediate: BIDMAS expression combining negatives and brackets"""
    import random
    a = random.randint(2, 5)
    b = random.randint(1, 4)
    c = random.randint(2, 5)
    d = random.randint(1, 4)
    # −a × (b − c)² + d
    inner = b - c  # may be negative
    result = -a * (inner ** 2) + d
    q = rf"Calculate \( -{a} \times \left({b} - {c}\right)^{{2}} + {d} \)"
    s = (
        rf"Step 1 — Brackets: \( {b} - {c} = {inner} \)<br>"
        rf"Step 2 — Indices: \( \left({inner}\right)^{{2}} = {inner**2} \)<br>"
        rf"Step 3 — Multiply: \( -{a} \times {inner**2} = {-a * inner**2} \)<br>"
        rf"Step 4 — Add: \( {-a * inner**2} + {d} = {result} \) → <strong>{result}</strong>"
    )
    hint = (
        rf"Square the bracketed value first: \( \left({inner}\right)^{{2}} = {inner**2} \). "
        rf"Then multiply by \( -{a} \)."
    )
    return q, s, hint, 2, result

def gcse_bidmas_hard():
    """Difficult/Exam: multi-step BIDMAS with negatives, fraction bar, and powers"""
    import random
    a = random.randint(2, 5)
    b = random.randint(1, 3)
    c = random.randint(2, 4)
    d = random.randint(1, 4)
    e = random.randint(1, 3)
    # (a² − b) / (c − d) + e  where (c - d) is small non-zero
    while c - d == 0:
        c = random.randint(2, 6)
    top = a**2 - b
    bottom = c - d
    result = top / bottom + e
    raw = int(result) if float(result).is_integer() else round(result, 4)
    q = rf"Calculate   ( {a}² − {b} ) ÷ ( {c} − {d} ) + {e}"
    s = (rf"Numerator (top brackets): {a}² − {b} = {a**2} − {b} = {top}<br>"
         rf"Denominator (bottom brackets): {c} − {d} = {bottom}<br>"
         rf"Divide: {top} ÷ {bottom} = {top/bottom:.4g}<br>"
         rf"Add: {top/bottom:.4g} + {e} = <strong>{raw}</strong>")
    hint = r"Evaluate all brackets first (including the indices inside), divide, then add."
    return q, s, hint, 3, raw


# ── BIDMAS: procedural practice (extra variants) ─────────────────────────────

def gcse_bidmas_proc_subtract_multiply():
    """Foundational: subtraction before multiplication (BIDMAS)."""
    a = random.randint(10, 30)
    b = random.randint(2, 6)
    c = random.randint(2, 9)
    product = b * c
    result = a - product
    q = rf"Calculate {a} − {b} × {c}"
    s = (
        rf"Multiply first: {b} × {c} = {product}<br>"
        rf"Then subtract: {a} − {product} = <strong>{result}</strong>"
    )
    hint = r"× comes before − in BIDMAS. Do not subtract before multiplying."
    return q, s, hint, 1, result


def gcse_bidmas_proc_divide_add():
    """Foundational: division before addition."""
    c = random.randint(2, 6)
    b = random.randint(2, 9) * c
    a = random.randint(5, 20)
    quotient = b // c
    result = a + quotient
    q = rf"Calculate {a} + {b} ÷ {c}"
    s = (
        rf"Divide first: {b} ÷ {c} = {quotient}<br>"
        rf"Then add: {a} + {quotient} = <strong>{result}</strong>"
    )
    hint = r"÷ comes before + in BIDMAS."
    return q, s, hint, 1, result


def gcse_bidmas_proc_two_products():
    """Foundational: two multiplications then addition."""
    a, b = random.randint(2, 5), random.randint(2, 5)
    c, d = random.randint(2, 6), random.randint(2, 6)
    p1, p2 = a * b, c * d
    result = p1 + p2
    q = rf"Calculate {a} × {b} + {c} × {d}"
    s = (
        rf"{a} × {b} = {p1} and {c} × {d} = {p2}<br>"
        rf"{p1} + {p2} = <strong>{result}</strong>"
    )
    hint = r"Work out each multiplication, then add the results."
    return q, s, hint, 1, result


def gcse_bidmas_proc_nested_brackets():
    """Intermediate: product of two bracketed expressions."""
    a, b = random.randint(2, 6), random.randint(1, 4)
    c, d = random.randint(4, 9), random.randint(1, 3)
    while c <= d:
        c = random.randint(5, 10)
        d = random.randint(1, 4)
    left, right = a + b, c - d
    result = left * right
    q = rf"Calculate ( {a} + {b} ) × ( {c} − {d} )"
    s = (
        rf"Brackets: ({a} + {b}) = {left}, ({c} − {d}) = {right}<br>"
        rf"{left} × {right} = <strong>{result}</strong>"
    )
    hint = r"Evaluate both brackets before multiplying."
    return q, s, hint, 2, result


def gcse_bidmas_proc_power_then_multiply():
    """Intermediate: power inside brackets, then multiply and add."""
    inner = random.randint(2, 5)
    p = random.randint(2, 3)
    mult = random.randint(2, 4)
    extra = random.randint(1, 12)
    powered = inner ** p
    product = mult * powered
    result = product + extra
    q = rf"Calculate {mult} × {inner}^{p} + {extra}"
    s = (
        rf"Indices: {inner}^{p} = {powered}<br>"
        rf"Multiply: {mult} × {powered} = {product}<br>"
        rf"Add: {product} + {extra} = <strong>{result}</strong>"
    )
    hint = r"Order: indices → multiply → add."
    return q, s, hint, 2, result


def gcse_bidmas_proc_bracket_over_divisor():
    """Intermediate: bracketed sum divided by a whole number."""
    c = random.randint(2, 5)
    quotient = random.randint(3, 8)
    total = quotient * c
    a = random.randint(2, total - 1)
    b = total - a
    extra = random.randint(1, 6)
    result = quotient + extra
    q = rf"Calculate ( {a} + {b} ) ÷ {c} + {extra}"
    s = (
        rf"Brackets: {a} + {b} = {total}<br>"
        rf"Divide: {total} ÷ {c} = {quotient}<br>"
        rf"Add: {quotient} + {extra} = <strong>{result}</strong>"
    )
    hint = r"Brackets first, then division, then addition."
    return q, s, hint, 2, result


def gcse_bidmas_proc_square_bracket_divide():
    """Difficult: squared bracket expression, divide, then add."""
    a, b = random.randint(2, 5), random.randint(1, 4)
    inner = a - b
    squared = inner ** 2
    mult = random.randint(2, 4)
    divisor = random.choice([d for d in (1, 2, 4) if squared * mult % d == 0] or [1])
    extra = random.randint(1, 5)
    product = mult * squared
    divided = product // divisor
    result = divided + extra
    q = rf"Calculate {mult} × ( {a} − {b} )² ÷ {divisor} + {extra}"
    s = (
        rf"Brackets: {a} − {b} = {inner}<br>"
        rf"Indices: {inner}² = {squared}<br>"
        rf"Multiply: {mult} × {squared} = {product}<br>"
        rf"Divide: {product} ÷ {divisor} = {divided}<br>"
        rf"Add: {divided} + {extra} = <strong>{result}</strong>"
    )
    hint = r"B → I → M/D → A/S. The bracket may give a negative value before squaring."
    return q, s, hint, 3, result


def gcse_bidmas_proc_nested_inner_bracket():
    """Difficult: nested operations inside brackets."""
    a, b, c = random.randint(2, 5), random.randint(1, 3), random.randint(1, 4)
    d = random.randint(1, 6)
    inner = b * (c + a)
    result = inner - d
    q = rf"Calculate {b} × ( {c} + {a} ) − {d}"
    s = (
        rf"Inner bracket: {c} + {a} = {c + a}<br>"
        rf"Multiply: {b} × {c + a} = {inner}<br>"
        rf"Subtract: {inner} − {d} = <strong>{result}</strong>"
    )
    hint = r"Work out the bracket first, then multiply, then subtract."
    return q, s, hint, 3, result


def gcse_bidmas_proc_negative_coefficient():
    """Difficult: negative coefficient with bracket and power."""
    coeff = random.randint(2, 5)
    b, c = random.randint(3, 7), random.randint(1, 4)
    inner = b - c
    squared = inner ** 2
    product = -coeff * squared
    extra = random.randint(1, 8)
    result = product + extra
    q = rf"Calculate −{coeff} × ( {b} − {c} )² + {extra}"
    s = (
        rf"Brackets: {b} − {c} = {inner}<br>"
        rf"Indices: {inner}² = {squared}<br>"
        rf"Multiply: −{coeff} × {squared} = {product}<br>"
        rf"Add: {product} + {extra} = <strong>{result}</strong>"
    )
    hint = r"Squaring removes the sign of the bracketed value; then apply the negative multiplier."
    return q, s, hint, 3, result


# -----------------------------------------------
# GCSE MATHS — ALGEBRA (practice variants + MCQ)
# -----------------------------------------------

def _algebra_raw(value):
    """Canonical numeric string for typed answer checking."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f'{value:g}'
    if isinstance(value, sp.Rational):
        if value.q == 1:
            return str(int(value.p))
        return f'{int(value.p)}/{int(value.q)}'
    return str(value)


def _algebra_linear_answer(value, var='x'):
    return {
        'type': 'linear',
        'value': _algebra_raw(value),
        'var': str(var).strip().lower(),
    }


def _algebra_quadratic_roots_answer(*roots, format_hint=None):
    payload = {
        'type': 'quadratic_roots',
        'roots': tuple(_algebra_raw(r) for r in roots),
    }
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _algebra_number_pair_answer(val_a, val_b, label_a='x', label_b='y', sep=','):
    return {
        'type': 'number_pair',
        'values': (_algebra_raw(val_a), _algebra_raw(val_b)),
        'label_a': label_a,
        'label_b': label_b,
        'sep': sep,
    }


def _algebra_algebraic_answer(expr, format_hint=None, subject=None):
    payload = {'type': 'algebraic', 'value': str(expr)}
    if format_hint:
        payload['format_hint'] = format_hint
    if subject:
        payload['subject'] = subject
    return payload


def _algebra_expr_str(expr):
    """SymPy expression → algebraic checker string (e.g. 2*x**2 + x - 3)."""
    return sp.sstr(expr)


def _algebra_linear_raw(raw):
    var = raw.get('var') or 'x'
    val = raw.get('value')
    if var == 'x':
        return str(val)
    return f'{var}={val}'


def _algebra_problem_from_output(out, difficulty):
    choice = problem_from_choice_output(out, difficulty, 'gcse', 'maths', 'algebra')
    if choice:
        return choice
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'linear':
                extra = {
                    'correct_answer_raw': _algebra_linear_raw(raw),
                    'answer_type': 'linear',
                    'answer_format_hint': 'Enter the value (e.g. x = 3 or just 3)',
                }
            elif raw_type == 'quadratic_roots':
                roots = raw.get('roots') or ()
                extra = {
                    'correct_answer_raw': ','.join(str(r) for r in roots),
                    'answer_type': 'quadratic_roots',
                    'answer_labels': quadratic_roots_ui_labels(len(roots)),
                    'answer_format_hint': quadratic_roots_format_hint(
                        len(roots), raw.get('format_hint'),
                    ),
                }
            elif raw_type == 'number_pair':
                val_a, val_b = raw['values']
                extra = {
                    'correct_answer_raw': f'{val_a}|{val_b}',
                    'answer_type': 'number_pair',
                    'answer_labels': [raw['label_a'], raw['label_b']],
                    'answer_pair_sep': raw.get('sep', ','),
                }
            elif raw_type == 'algebraic':
                text = str(raw.get('value') or '')
                extra = {
                    'correct_answer_raw': text,
                    'answer_type': 'algebraic',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter the simplified expression',
                    ),
                }
                if raw.get('subject'):
                    extra['answer_subject'] = raw['subject']
                elif '=' in text:
                    extra['answer_subject'] = text.split('=', 1)[0]
        elif isinstance(raw, (int, float, sp.Rational)):
            extra = {
                'correct_answer_raw': _algebra_raw(raw),
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
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'algebra', **extra
    )


def _algebra_linear_equation(a_lo, a_hi, b_lo, b_hi, c_lo, c_hi):
    x = sp.Symbol('x')
    a = random.randint(a_lo, a_hi)
    b = random.randint(b_lo, b_hi)
    c = random.randint(c_lo, c_hi)
    if c <= b:
        c = b + random.randint(1, 20)
    ans = sp.Rational(c - b, a)
    q = rf"Solve: \( {a}x + {b} = {c} \)"
    s = rf"Subtract \( {b} \): \( {a}x = {c - b} \)<br>Divide by \( {a} \): \( x = \boxed{{{sp.latex(ans)}}} \)"
    hint = r"Isolate \(x\) using inverse operations."
    return q, s, hint, 2, _algebra_linear_answer(ans)


def algebra_practice_linear_1():
    return _algebra_linear_equation(2, 9, 1, 15, 10, 50)


def algebra_practice_linear_2():
    return _algebra_linear_equation(2, 12, 1, 20, 15, 80)


def algebra_practice_linear_3():
    return _algebra_linear_equation(3, 15, 2, 25, 20, 100)


def _algebra_factorise_problem(r1_range, r2_range):
    x = sp.Symbol('x')
    r1 = random.randint(*r1_range)
    r2 = random.randint(*r2_range)
    while r2 == r1:
        r2 = random.randint(*r2_range)
    expr = sp.expand((x - r1) * (x - r2))
    q = rf"Solve: \( {sp.latex(expr)} = 0 \)"
    s = rf"Factorise: \( (x - {r1})(x - {r2}) = 0 \)<br>\( x = \boxed{{{r1}}} \) or \( x = \boxed{{{r2}}} \)"
    hint = r"Factorise, then set each bracket equal to zero."
    return q, s, hint, 3, _algebra_quadratic_roots_answer(r1, r2)


def algebra_practice_factorise_1():
    return _algebra_factorise_problem((-6, 6), (-6, 6))


def algebra_practice_factorise_2():
    return _algebra_factorise_problem((-8, 8), (-8, 8))


def algebra_practice_factorise_3():
    return _algebra_factorise_problem((-10, 10), (-10, 10))


def _algebra_quadratic_formula_problem():
    x = sp.Symbol('x')
    while True:
        a_c = random.randint(1, 4)
        b_c = random.randint(-10, 10)
        c_c = random.randint(-12, 12)
        if c_c == 0:
            continue
        discriminant = b_c ** 2 - 4 * a_c * c_c
        if discriminant > 0:
            break
    expr = a_c * x ** 2 + b_c * x + c_c
    r1 = round((-b_c + discriminant ** 0.5) / (2 * a_c), 2)
    r2 = round((-b_c - discriminant ** 0.5) / (2 * a_c), 2)
    q = rf"Solve \( {sp.latex(expr)} = 0 \), giving your answers to 2 decimal places."
    s = rf"""Using the quadratic formula:<br><br>
    \( x = \frac{{{-b_c} \pm \sqrt{{{discriminant}}}}}{{{2 * a_c}}} \)<br><br>
    \( x = \boxed{{{r1}}} \) or \( x = \boxed{{{r2}}} \)"""
    hint = r"Use \( x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \)."
    return q, s, hint, 4, _algebra_quadratic_roots_answer(
        r1, r2, format_hint='Enter roots to 2 d.p., separated by commas',
    )


def _algebra_hcf_factorise_problem():
    """Factorise ax + b by extracting the HCF."""
    hcf = random.randint(2, 9)
    inner_x = random.randint(2, 9)
    inner_c = random.randint(2, 9)
    coeff_x = hcf * inner_x
    const = hcf * inner_c
    factored = f"{hcf}({inner_x}x + {inner_c})"
    q = rf"Factorise fully: \( {coeff_x}x + {const} \)"
    s = rf"HCF is {hcf}: \( {coeff_x}x + {const} = \boxed{{{factored}}} \)"
    hint = r"Find the largest number that divides both terms, and factor it out."
    return q, s, hint, 2, _algebra_algebraic_answer(
        factored, format_hint='e.g. 3(2x + 5)',
    )


def _algebra_change_subject_problem():
    """Rearrange a formula to make a variable the subject."""
    if random.random() < 0.65:
        dep = random.choice(['y', 'P', 'A', 's', 'C', 'F'])
        subj = random.choice(['x', 'y', 'w', 't', 'r', 'n'])
        if dep == subj:
            subj = 'x' if dep != 'x' else 'y'
        a = random.randint(2, 7)
        b = random.randint(1, 15)
        formula = f"{dep} = {a}{subj} + {b}"
        ans_latex = rf"{subj} = \frac{{{dep} - {b}}}{{{a}}}"
        ans_raw = f'{subj}=({dep}-{b})/{a}'
    else:
        subj, formula, ans_latex, ans_raw = random.choice([
            ('t', 'v = u + at', r't = \frac{v - u}{a}', 't=(v-u)/a'),
            ('w', 'P = 2l + 2w', r'w = \frac{P - 2l}{2}', 'w=(P-2l)/2'),
            ('h', 'A = bh', r'h = \frac{A}{b}', 'h=A/b'),
            ('x', 'y = mx + c', r'x = \frac{y - c}{m}', 'x=(y-c)/m'),
            ('r', 'C = 2\\pi r', r'r = \frac{C}{2\pi}', 'r=C/(2*pi)'),
        ])
    q = rf"Make \({subj}\) the subject of the formula: \( {formula} \)"
    s = rf"Rearrange step by step to get <strong>\( {ans_latex} \)</strong>"
    hint = r"Treat the formula like an equation: undo operations on the subject in reverse order."
    return q, s, hint, 3, _algebra_algebraic_answer(
        ans_raw,
        format_hint='Enter the rearranged formula, e.g. x=(y-3)/2',
        subject=subj,
    )


def _algebra_simultaneous_problem():
    """Simultaneous linear equations with integer solution."""
    x_val = random.randint(2, 9)
    y_val = random.randint(1, 9)
    while True:
        a1, b1 = random.randint(1, 5), random.randint(1, 5)
        a2, b2 = random.randint(1, 5), random.randint(1, 5)
        if a1 * b2 - a2 * b1 != 0:
            break
    c1 = a1 * x_val + b1 * y_val
    c2 = a2 * x_val + b2 * y_val
    q = rf"Solve simultaneously:<br>\( {a1}x + {b1}y = {c1} \)<br>\( {a2}x + {b2}y = {c2} \)"
    s = (
        rf"Eliminating one variable gives \( x = \boxed{{{x_val}}} \), \( y = \boxed{{{y_val}}} \).<br>"
        rf"Check in both equations."
    )
    hint = r"Eliminate one variable by adding or subtracting the equations, then substitute back."
    return q, s, hint, 4, _algebra_number_pair_answer(x_val, y_val)


def algebra_practice_quadratic_1():
    return _algebra_quadratic_formula_problem()


def algebra_practice_quadratic_2():
    return algebra_practice_consecutive_integers()


def algebra_practice_quadratic_3():
    return algebra_practice_expand_mixed()


# ── Algebra: intermediate (varied formats beyond factorise-and-solve) ─────────

def algebra_practice_expand_binomial():
    """Expand two linear brackets."""
    x = sp.Symbol('x')
    a, b = random.randint(1, 4), random.randint(1, 4)
    c, d = random.randint(-3, 5), random.randint(-3, 5)
    expr = sp.expand((a * x + b) * (c * x + d))
    q = rf"Expand and simplify: \( ({a}x + {b})({c}x + {d}) \)"
    s = rf"\( ({a}x + {b})({c}x + {d}) = \boxed{{{sp.latex(expr)}}} \)"
    hint = r"Multiply each term in the first bracket by each term in the second, then collect like terms."
    return q, s, hint, 2, _algebra_algebraic_answer(
        _algebra_expr_str(expr),
        format_hint='Enter the expanded expression, e.g. 2x^2 + 5x + 3',
    )


def algebra_practice_linear_both_sides():
    """Linear equation with unknown on both sides."""
    x_val = random.randint(2, 8)
    a = random.randint(3, 7)
    c = random.randint(1, 5)
    while a == c:
        c = random.randint(1, 5)
    b = random.randint(1, 10)
    rhs = (a - c) * x_val + b
    q = rf"Solve: \( {a}x + {b} = {c}x + {rhs} \)"
    s = (
        rf"Subtract \( {c}x \): \( {a - c}x + {b} = {rhs} \)<br>"
        rf"Subtract \( {b} \): \( {a - c}x = {rhs - b} \)<br>"
        rf"\( x = \boxed{{{x_val}}} \)"
    )
    hint = r"Collect \(x\) terms on one side and numbers on the other, then divide."
    return q, s, hint, 3, _algebra_linear_answer(x_val)


def algebra_practice_substitution():
    """Substitute a value into an expression."""
    x_val = random.randint(-5, 8)
    if x_val == 0:
        x_val = random.choice([-2, 2, 3, 4])
    a = random.randint(2, 4)
    b = random.randint(-6, 6)
    c = random.randint(-3, 8)
    result = a * x_val ** 2 + b * x_val + c
    q = rf"If \( x = {x_val} \), find the value of \( {a}x^2 + {b}x + {c} \)."
    s = (
        rf"Substitute \( x = {x_val} \):<br>"
        rf"\( {a}({x_val})^2 + {b}({x_val}) + {c} = {a * x_val**2} + {b * x_val} + {c} = "
        rf"\boxed{{{result}}} \)"
    )
    hint = r"Replace every \(x\) with the given number, respecting powers and negative signs."
    return q, s, hint, 2, result


def algebra_practice_factorise_hcf():
    """Factorise by taking out a common factor."""
    return _algebra_hcf_factorise_problem()


def algebra_practice_change_subject():
    """Rearrange a formula to change the subject."""
    return _algebra_change_subject_problem()


# ── Algebra: difficult (word problems, simultaneous, multi-step) ──────────────

def algebra_practice_word_linear():
    """Form and solve a linear equation from a word problem."""
    base = random.randint(10, 40)
    per = random.randint(2, 12)
    miles = random.randint(3, 15)
    total = base + per * miles
    q = (
        rf"A taxi charges a £{base} fixed fare plus £{per} per mile. "
        rf"The total fare is £{total}. How many miles were travelled?"
    )
    s = (
        rf"Let \( x \) = number of miles.<br>"
        rf"\( {base} + {per}x = {total} \)<br>"
        rf"\( {per}x = {total - base} \)<br>"
        rf"\( x = \boxed{{{miles}}} \) miles"
    )
    hint = r"Write an equation with a fixed amount plus rate × miles, then solve."
    return q, s, hint, 3, miles


def algebra_practice_simultaneous():
    """Solve a pair of simultaneous linear equations."""
    return _algebra_simultaneous_problem()


def algebra_practice_expand_mixed():
    """Expand brackets with a coefficient on x."""
    x = sp.Symbol('x')
    a = random.randint(2, 4)
    b = random.randint(1, 5)
    c = random.randint(-4, 4)
    expr = sp.expand((a * x + b) * (x + c))
    q = rf"Expand and simplify: \( ({a}x + {b})(x + {c}) \)"
    s = rf"\( ({a}x + {b})(x + {c}) = \boxed{{{sp.latex(expr)}}} \)"
    hint = r"Multiply term by term, then collect \(x^2\), \(x\) and constant terms."
    return q, s, hint, 3, _algebra_algebraic_answer(
        _algebra_expr_str(expr),
        format_hint='Enter the expanded expression, e.g. 2x^2 + 5x + 3',
    )


def algebra_practice_brackets_both_sides():
    """Equation with brackets on both sides."""
    x_val = random.randint(2, 6)
    a = random.randint(2, 4)
    b = random.randint(2, 6)
    c = random.randint(2, 4)
    d = random.randint(1, 5)
    extra = a * (x_val + b) - c * (x_val + d)
    q = rf"Solve: \( {a}(x + {b}) = {c}(x + {d}) + {extra} \)"
    s = (
        rf"Expand: \( {a}x + {a*b} = {c}x + {c*d} + {extra} \)<br>"
        rf"Collect \(x\): \( {a - c}x = {c*d + extra - a*b} \)<br>"
        rf"\( x = \boxed{{{x_val}}} \)"
    )
    hint = r"Expand brackets first, then collect \(x\) terms and solve."
    return q, s, hint, 3, _algebra_linear_answer(x_val)


def algebra_practice_consecutive_integers():
    """Consecutive integers problem leading to an equation."""
    n = random.randint(3, 8)
    start = random.randint(10, 20)
    total = sum(range(start, start + n))
    q = (
        rf"The sum of {n} consecutive integers starting from \( x \) is {total}. "
        rf"Find \( x \)."
    )
    s = (
        rf"The integers are \( x, x+1, \ldots, x+{n-1} \).<br>"
        rf"Sum \( = {n}x + {sum(range(n))} = {total} \)<br>"
        rf"\( x = \boxed{{{start}}} \)"
    )
    hint = r"Write the sum as \(nx\) plus the sum of 0,1,…,(n−1), then solve."
    return q, s, hint, 4, _algebra_linear_answer(start)


def gcse_maths_algebra(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        from generators.gcse.maths_basic_topics_mcq import gcse_maths_algebra_mcq
        return gcse_maths_algebra_mcq(difficulty, variant_name)
    if variant_name:
        return _basic_maths_practice('algebra', difficulty, mode, variant_name)

    pools = {
        'foundational': [
            algebra_practice_linear_1,
            algebra_practice_linear_2,
            algebra_practice_linear_3,
        ],
        'intermediate': [
            algebra_practice_factorise_1,
            algebra_practice_factorise_2,
            algebra_practice_factorise_3,
            algebra_practice_expand_binomial,
            algebra_practice_linear_both_sides,
            algebra_practice_substitution,
            algebra_practice_factorise_hcf,
            algebra_practice_change_subject,
        ],
        'difficult': [
            algebra_practice_quadratic_1,
            algebra_practice_word_linear,
            algebra_practice_simultaneous,
            algebra_practice_expand_mixed,
            algebra_practice_brackets_both_sides,
            algebra_practice_consecutive_integers,
            algebra_practice_quadratic_2,
            algebra_practice_quadratic_3,
        ],
    }
    variant = random.choice(pools.get(difficulty, pools['foundational']))
    return _algebra_problem_from_output(variant(), difficulty)





# ─────────────────────────────────────────────────────────────
#  GCSE MATHS — SURDS
# ─────────────────────────────────────────────────────────────

_SURD_SQUARES = [4, 9, 16, 25, 36, 49, 64]
_SURD_PRIMES = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15]


def _surd_largest_square_factor(n):
    largest_sq = 1
    for s in _SURD_SQUARES:
        if n % s == 0:
            largest_sq = s
    k = int(math.sqrt(largest_sq))
    return largest_sq, k, n // largest_sq


def _surd_decompose(n):
    _, k, rem = _surd_largest_square_factor(n)
    return k, rem


def _surd_fmt(k, r):
    if k == 1:
        return f"√{r}"
    return f"{k}√{r}"


def _surd_answer(coeff, radicand):
    """Surd answer k√r. Stored as 'coeff|radicand' when coeff != 1."""
    c = int(coeff)
    r = int(radicand)
    if c == 1:
        return {'type': 'surd', 'radicand': r}
    return {'type': 'surd', 'coeff': c, 'radicand': r}


def _surd_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_fdp_raw(v) for v in values),
        'labels': tuple(labels),
    }


def _algebraic_answer(text, format_hint=None):
    payload = {'type': 'algebraic', 'value': str(text)}
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _algebraic_surd_binomial(const, coef, radicand, surd_sign='+', format_hint=None):
    sign = '+' if str(surd_sign).strip() == '+' else '-'
    payload = {
        'type': 'algebraic',
        'kind': 'surd_binomial',
        'const': int(const),
        'coef': int(coef),
        'radicand': int(radicand),
        'surd_sign': sign,
    }
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _algebraic_fraction_surd(coef, radicand, denom, format_hint=None):
    payload = {
        'type': 'algebraic_fraction',
        'kind': 'surd_over_int',
        'coef': int(coef),
        'radicand': int(radicand),
        'denom': int(denom),
    }
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _algebraic_fraction_binomial(
    scale, const, radicand, denom, surd_coef=1, bracket_sign='-', format_hint=None
):
    sign = '-' if str(bracket_sign).strip() == '-' else '+'
    payload = {
        'type': 'algebraic_fraction',
        'kind': 'binomial_over_int',
        'scale': int(scale),
        'const': int(const),
        'surd_coef': int(surd_coef),
        'radicand': int(radicand),
        'denom': int(denom),
        'bracket_sign': sign,
    }
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _algebraic_fraction_two_surds(rad1, rad2, denom, format_hint=None):
    r1, r2 = sorted([int(rad1), int(rad2)])
    payload = {
        'type': 'algebraic_fraction',
        'kind': 'two_surds_over_int',
        'rad1': r1,
        'rad2': r2,
        'denom': int(denom),
    }
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _algebraic_fraction_hint_two_surds(rad1, rad2, denom):
    r1, r2 = sorted([int(rad1), int(rad2)])
    return (
        f'Numerator like √{r1} + √{r2} (simplified surds OK, e.g. 3√2 + √5); '
        f'denominator a whole number (leave blank if 1)'
    )


def _algebraic_fraction_hint_binomial(scale, const, rad, denom, bracket_sign='-'):
    op = '−' if bracket_sign == '-' else '+'
    inner = f'{const} {op} √{rad}'
    if scale == 1:
        factored = f'({inner})'
    elif scale == -1:
        factored = f'−({inner})'
    elif scale > 0:
        factored = f'{scale}({inner})'
    else:
        factored = f'−{abs(scale)}({inner})'
    abs_scale = abs(scale)
    sign = 1 if scale >= 0 else -1
    int_part = sign * abs_scale * const
    sc = -sign * abs_scale if bracket_sign == '-' else sign * abs_scale
    exp_op = '+' if sc >= 0 else '−'
    abs_sc = abs(sc)
    expanded = (
        f'{int_part} {exp_op} √{rad}'
        if abs_sc == 1
        else f'{int_part} {exp_op} {abs_sc}√{rad}'
    )
    return (
        f'Numerator like {expanded} or {factored}; '
        f'denominator a whole number (leave blank if 1)'
    )


def _algebraic_fraction_expanded_binomial(
    int_part, surd_coef, radicand, denom, format_hint=None
):
    payload = {
        'type': 'algebraic_fraction',
        'kind': 'expanded_binomial_over_int',
        'int_part': int(int_part),
        'surd_coef': int(surd_coef),
        'radicand': int(radicand),
        'denom': int(denom),
    }
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _algebraic_fraction_hint_expanded_binomial(int_part, surd_coef, rad):
    if surd_coef == 0:
        return 'Enter the simplified value'
    op = '+' if surd_coef >= 0 else '−'
    abs_sc = abs(surd_coef)
    surd = f'√{rad}' if abs_sc == 1 else f'{abs_sc}√{rad}'
    return (
        f'Numerator like {int_part} {op} {surd}; '
        f'denominator a whole number (leave blank if 1)'
    )


def _surd_problem_from_output(out, difficulty):
    choice = problem_from_choice_output(out, difficulty, 'gcse', 'maths', 'surds')
    if choice:
        return choice
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            if values and len(values) == len(labels):
                extra = {
                    'correct_answer_raw': '|'.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_format_hint': 'Enter a number in every field',
                }
        elif isinstance(raw, dict) and raw.get('type') == 'surd':
            coeff = int(raw.get('coeff') or 1)
            radicand = raw.get('radicand')
            if radicand is not None:
                extra = {
                    'correct_answer_raw': (
                        str(radicand) if coeff == 1 else f'{coeff}|{radicand}'
                    ),
                    'answer_type': 'surd',
                    'answer_format_hint': 'e.g. √113 — use the √ button if needed',
                }
        elif isinstance(raw, dict) and raw.get('type') == 'algebraic':
            if raw.get('kind') == 'surd_binomial':
                const = int(raw['const'])
                coef = int(raw['coef'])
                rad = int(raw['radicand'])
                sign = raw.get('surd_sign', '+')
                extra = {
                    'correct_answer_raw': f'{const}|{coef}|{rad}|{sign}',
                    'answer_type': 'algebraic',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        (
                            f'e.g. {const} + {coef}√{rad}'
                            if sign == '+'
                            else f'e.g. {const} − {coef}√{rad}'
                        ),
                    ),
                }
            else:
                text = str(raw.get('value') or '')
                extra = {
                    'correct_answer_raw': text,
                    'answer_type': 'algebraic',
                    'answer_format_hint': raw.get('format_hint', 'e.g. a - b'),
                }
        elif isinstance(raw, dict) and raw.get('type') == 'algebraic_fraction':
            kind = raw.get('kind')
            if kind == 'surd_over_int':
                coef = int(raw['coef'])
                rad = int(raw['radicand'])
                denom = int(raw['denom'])
                num_display = _surd_fmt(coef, rad)
                extra = {
                    'correct_answer_raw': f'{coef}|{rad}|{denom}',
                    'answer_type': 'algebraic_fraction',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        f'Numerator like {num_display}, denominator a whole number',
                    ),
                }
            elif kind == 'binomial_over_int':
                scale = int(raw['scale'])
                const = int(raw['const'])
                surd_coef = int(raw['surd_coef'])
                rad = int(raw['radicand'])
                denom = int(raw['denom'])
                bracket_sign = raw.get('bracket_sign', '-')
                extra = {
                    'correct_answer_raw': (
                        f'b|{scale}|{const}|{surd_coef}|{rad}|{denom}|{bracket_sign}'
                    ),
                    'answer_type': 'algebraic_fraction',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        _algebraic_fraction_hint_binomial(
                            scale, const, rad, denom, bracket_sign
                        ),
                    ),
                }
            elif kind == 'two_surds_over_int':
                rad1 = int(raw['rad1'])
                rad2 = int(raw['rad2'])
                denom = int(raw['denom'])
                extra = {
                    'correct_answer_raw': f'd|{rad1}|{rad2}|{denom}',
                    'answer_type': 'algebraic_fraction',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        _algebraic_fraction_hint_two_surds(rad1, rad2, denom),
                    ),
                }
            elif kind == 'expanded_binomial_over_int':
                int_part = int(raw['int_part'])
                surd_coef = int(raw['surd_coef'])
                rad = int(raw['radicand'])
                denom = int(raw['denom'])
                extra = {
                    'correct_answer_raw': f'e|{int_part}|{surd_coef}|{rad}|{denom}',
                    'answer_type': 'algebraic_fraction',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        _algebraic_fraction_hint_expanded_binomial(
                            int_part, surd_coef, rad
                        ),
                    ),
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _fdp_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'surds', **extra)


def _surd_problem(variant_fn, difficulty):
    return _surd_problem_from_output(variant_fn(), difficulty)


def _surd_random_radicand():
    square = random.choice(_SURD_SQUARES)
    prime = random.choice(_SURD_PRIMES)
    return square * prime, square, prime


def _surd_random_divide():
    """Return a, b and simplified answer for √a ÷ √b."""
    if random.random() < 0.7:
        ans = random.randint(2, 9)
        b = random.choice([2, 3, 5, 8, 18, 32, 50])
        a = ans * ans * b
        working = (
            rf"\( \dfrac{{\sqrt{{{a}}}}}{{\sqrt{{{b}}}}} = \sqrt{{\dfrac{{{a}}}{{{b}}}}} "
            rf"= \sqrt{{{a // b}}} = {ans}"
        )
        return a, b, str(ans), working, ans
    k = random.randint(2, 5)
    r = random.choice([2, 3, 5, 7])
    b = random.choice([2, 3, 5, 8])
    a = k * k * r * b
    ans = _surd_fmt(k, r)
    working = (
        rf"\( \dfrac{{\sqrt{{{a}}}}}{{\sqrt{{{b}}}}} = \sqrt{{\dfrac{{{a}}}{{{b}}}}} "
        rf"= \sqrt{{{k * k * r}}} = {k}\sqrt{{{r}}} = {ans}"
    )
    return a, b, ans, working, _surd_answer(k, r)


def _surd_random_compare():
    while True:
        c1 = random.randint(2, 7)
        r1 = random.choice([2, 3, 5, 7, 11])
        c2 = random.randint(2, 7)
        r2 = random.choice([2, 3, 5, 7, 11])
        v1, v2 = c1 ** 2 * r1, c2 ** 2 * r2
        if v1 != v2:
            break
    s1, s2 = f"{c1}√{r1}", f"{c2}√{r2}"
    winner = s1 if v1 > v2 else s2
    return c1, r1, c2, r2, s1, s2, winner, v1, v2


def _surd_random_mixed():
    """Build a 2–3 term like-surd expression and its simplified form."""
    p = random.choice([2, 3, 5, 7])
    n_terms = random.choice([2, 2, 3])
    terms = []
    for _ in range(n_terms):
        sq = random.choice([1, 4, 9, 16, 25, 36])
        k = int(math.sqrt(sq))
        terms.append((sq * p, k))

    total_k = terms[0][1]
    expr_parts = [rf"\sqrt{{{terms[0][0]}}}"]
    working_parts = [rf"\sqrt{{{terms[0][0]}}} = {_surd_fmt(terms[0][1], p)}"]

    for n, k in terms[1:]:
        sign = random.choice(["+", "+", "-"])
        if sign == "+":
            total_k += k
        else:
            total_k -= k
        sep = " + " if sign == "+" else " - "
        expr_parts.append(sep + rf"\sqrt{{{n}}}")
        working_parts.append(rf"\sqrt{{{n}}} = {_surd_fmt(k, p)}")

    if total_k <= 0:
        return _surd_random_mixed()

    expr = "".join(expr_parts)
    ans = _surd_fmt(total_k, p)
    working = "<br>".join(working_parts) + f"<br>Combine: <strong>{ans}</strong>"
    return expr, ans, working, _surd_answer(total_k, p)


def _surd_random_equation():
    while True:
        rhs = random.randint(3, 12)
        offset = random.randint(1, 40)
        x = rhs ** 2 - offset
        if x > 0:
            return rhs, offset, x


def _surd_random_binomial_diff():
    while True:
        b = random.choice([2, 3, 5, 6, 7, 10])
        diff = random.choice([2, 3, 4, 5, 6, 7, 8])
        a = b + diff
        if a <= 98:
            denom = a - b
            ans = rf"\dfrac{{\sqrt{{{a}}} + \sqrt{{{b}}}}}{{{denom}}}"
            return a, b, denom, ans


def _surd_random_between_integers():
    lo = random.randint(4, 14)
    hi = lo + 1
    n = random.randint(lo * lo + 1, hi * hi - 1)
    return n, lo, hi


def gcse_surds_simplify():
    """Foundational: simplify a single surd √n"""
    n, square, prime = _surd_random_radicand()
    k = int(math.sqrt(square))
    q = (rf"Write √{n} in its simplest surd form.")
    s = (rf"Find the largest square factor of {n}: that is {square} (since {square} × {prime} = {n}).<br>"
         rf"√{n} = √({square} × {prime}) = √{square} × √{prime} = <strong>{k}√{prime}</strong>")
    hint = r"Look for the largest square number that divides exactly into the number under the root."
    return q, s, hint, 2, _surd_answer(k, prime)

def gcse_surds_simplify_multiple():
    """Foundational: write p√n in the form k√r"""
    n, square, prime = _surd_random_radicand()
    p = random.randint(2, 7)
    k_inner = int(math.sqrt(square))
    k_total = p * k_inner
    q = (rf"Write {p}√{n} in the form k√{prime}, where k is an integer.")
    s = (rf"First simplify √{n}: √{n} = √({square} × {prime}) = {k_inner}√{prime}<br>"
         rf"Then multiply: {p} × {k_inner}√{prime} = <strong>{k_total}√{prime}</strong>")
    hint = rf"Simplify √{n} first by finding its square factor, then multiply by {p}."
    return q, s, hint, 2, _surd_answer(k_total, prime)

def gcse_surds_add_subtract():
    """Foundational: add or subtract surds after simplifying"""
    prime = random.choice([2, 3, 5, 7])
    a_sq = random.choice(_SURD_SQUARES)
    b_sq = random.choice(_SURD_SQUARES)
    a_coef = int(math.sqrt(a_sq))
    b_coef = int(math.sqrt(b_sq))
    n1 = a_sq * prime
    n2 = b_sq * prime
    op = random.choice(["+", "+", "-"])
    if op == "+":
        total = a_coef + b_coef
    else:
        if a_coef <= b_coef:
            a_sq, b_sq = b_sq, a_sq
            a_coef, b_coef = b_coef, a_coef
            n1, n2 = n2, n1
        total = a_coef - b_coef
    op_word = " + " if op == "+" else " − "
    q = rf"Simplify √{n1}{op_word}√{n2}. Write your answer in the form k√{prime}."
    s = (rf"√{n1} = √({a_sq} × {prime}) = {a_coef}√{prime}<br>"
         rf"√{n2} = √({b_sq} × {prime}) = {b_coef}√{prime}<br>"
         rf"{a_coef}√{prime}{op_word}{b_coef}√{prime} = <strong>{_surd_fmt(total, prime)}</strong>")
    hint = rf"Simplify each surd separately first, then combine the coefficients in front of √{prime}."
    return q, s, hint, 2, _surd_answer(total, prime)

def gcse_surds_multiply():
    """Foundational: multiply two simple surds"""
    a = random.choice(_SURD_PRIMES)
    b = random.choice(_SURD_PRIMES)
    product = a * b
    # check if product has a square factor for a nicer answer
    largest_sq = 1
    for s in [4, 9, 16, 25]:
        if product % s == 0:
            largest_sq = s
    if largest_sq > 1:
        k = int(math.sqrt(largest_sq))
        rem = product // largest_sq
        ans = f"{k}√{rem}" if rem > 1 else str(k)
        sol = (rf"√{a} × √{b} = √({a} × {b}) = √{product}<br>"
               rf"Simplify √{product}: largest square factor is {largest_sq}<br>"
               rf"√{product} = {k}√{rem} → <strong>{ans}</strong>")
        raw = k if rem == 1 else _surd_answer(k, rem)
    else:
        ans = f"√{product}"
        sol = rf"√{a} × √{b} = √({a} × {b}) = <strong>√{product}</strong>"
        raw = _surd_answer(1, product)
    q = rf"Simplify √{a} × √{b}."
    hint = r"Use the rule √a × √b = √(ab), then check if the result can be simplified further."
    return q, sol, hint, 2, raw

def gcse_surds_expand_simple():
    """Intermediate: expand (a + √b)(a − √b) — difference of two squares"""
    a = random.randint(2, 9)
    b = random.choice(_SURD_PRIMES[:8])
    result = a**2 - b
    q = rf"Expand and simplify (  {a} + √{b}  )(  {a} − √{b}  )."
    s = (rf"Use the difference of two squares pattern (p + q)(p − q) = p² − q²:<br>"
         rf"({a})² − (√{b})² = {a**2} − {b} = <strong>{result}</strong>")
    hint = r"(a + √b)(a − √b) = a² − b. The surd terms cancel out."
    return q, s, hint, 2, result

def gcse_surds_expand_double():
    """Intermediate: expand (a + √b)(c + √b) — general double bracket"""
    a = random.randint(1, 6)
    c = random.randint(1, 6)
    b = random.choice([2, 3, 5, 6, 7])
    # (a + √b)(c + √b) = ac + a√b + c√b + b = (ac+b) + (a+c)√b
    const = a * c + b
    coef  = a + c
    q = rf"Expand and simplify ( {a} + √{b} )( {c} + √{b} )."
    s = (rf"Multiply out using FOIL:<br>"
         rf"First: {a} × {c} = {a*c}<br>"
         rf"Outer: {a} × √{b} = {a}√{b}<br>"
         rf"Inner: √{b} × {c} = {c}√{b}<br>"
         rf"Last: √{b} × √{b} = {b}<br>"
         rf"Collect terms: ({a*c} + {b}) + ({a} + {c})√{b} = <strong>{const} + {coef}√{b}</strong>")
    hint = r"Use FOIL. Remember √b × √b = b (the surd disappears)."
    return q, s, hint, 2, _algebraic_surd_binomial(const, coef, b, '+')

def gcse_surds_square_bracket():
    """Intermediate: expand (a + √b)² — write in form p + q√b"""
    a = random.randint(2, 9)
    b = random.choice(_SURD_PRIMES[:8])
    # (a + √b)² = a² + 2a√b + b
    const = a**2 + b
    coef  = 2 * a
    q = rf"Write ( {a} + √{b} )² in the form p + q√{b}, where p and q are integers."
    s = (rf"( {a} + √{b} )² = ( {a} + √{b} )( {a} + √{b} )<br>"
         rf"= {a}² + {a}√{b} + {a}√{b} + (√{b})²<br>"
         rf"= {a**2} + {coef}√{b} + {b}<br>"
         rf"= <strong>{const} + {coef}√{b}</strong>")
    hint = rf"(a + √b)² = a² + 2a√b + b. Don't forget the middle term 2a√b."
    return q, s, hint, 2, _algebraic_surd_binomial(const, coef, b, '+')

def gcse_surds_square_bracket_minus():
    """Intermediate: expand (a − √b)² — write in form p + q√b"""
    a = random.randint(2, 9)
    b = random.choice(_SURD_PRIMES[:8])
    const = a**2 + b
    coef  = 2 * a  # coefficient (but negative in working, positive in result)
    q = rf"Write ( {a} − √{b} )² in the form p + q√{b}, where p and q are integers."
    s = (rf"( {a} − √{b} )² = ( {a} − √{b} )( {a} − √{b} )<br>"
         rf"= {a}² − {a}√{b} − {a}√{b} + (√{b})²<br>"
         rf"= {a**2} − {coef}√{b} + {b}<br>"
         rf"= <strong>{const} − {coef}√{b}</strong>")
    hint = rf"(a − √b)² = a² − 2a√b + b. Note: (−√b)² = +b."
    return q, s, hint, 2, _algebraic_surd_binomial(const, coef, b, '-')

def gcse_surds_rationalise_simple():
    """Intermediate: rationalise 1/√a or k/√a"""
    a = random.choice(_SURD_PRIMES[:8])
    num = random.randint(1, 9)
    from math import gcd
    g = gcd(num, a)
    n_s = num // g
    d_s = a // g
    if d_s == 1:
        ans = _surd_fmt(n_s, a)
        raw = _surd_answer(n_s, a)
    else:
        ans = f"{_surd_fmt(n_s, a)} / {d_s}"
        raw = _algebraic_fraction_surd(n_s, a, d_s)
    q = rf"Rationalise the denominator of {num} / √{a}. Write your answer in its simplest form."
    s = (rf"Multiply numerator and denominator by √{a}:<br>"
         rf"({num} × √{a}) / (√{a} × √{a}) = {num}√{a} / {a}<br>"
         rf"Simplify: <strong>{ans}</strong>")
    hint = rf"Multiply top and bottom by √{a} to clear the surd from the denominator."
    return q, s, hint, 2, raw

def gcse_surds_rationalise_compound():
    """Intermediate: rationalise k/(a + √b) using conjugate"""
    while True:
        a = random.randint(1, 6)
        b = random.choice([2, 3, 5, 6, 7, 10])
        denom = a ** 2 - b
        if denom != 0:
            break
    num = random.choice([2, 3, 4, 5, 6, 8])
    abs_denom = abs(denom)
    from math import gcd
    g = gcd(num, abs_denom)
    n_s = num // g
    d_s = abs_denom // g
    scale = n_s if denom > 0 else -n_s
    if d_s == 1:
        ans = (
            f"−{n_s}({a} − √{b})" if denom < 0 and n_s > 1
            else f"−({a} − √{b})" if denom < 0
            else f"{n_s}({a} − √{b})" if n_s > 1
            else f"({a} − √{b})"
        )
    else:
        ans = (
            f"−{n_s}({a} − √{b}) / {d_s}" if denom < 0 and n_s > 1
            else f"−({a} − √{b}) / {d_s}" if denom < 0
            else f"{n_s}({a} − √{b}) / {d_s}" if n_s > 1
            else f"({a} − √{b}) / {d_s}"
        )
    raw = _algebraic_fraction_binomial(scale, a, b, d_s, 1, '-')
    q = rf"Rationalise the denominator: {num} / ( {a} + √{b} )"
    s = (rf"Multiply top and bottom by the conjugate ( {a} − √{b} ):<br>"
         rf"Numerator: {num}({a} − √{b}) = {num*a} − {num}√{b}<br>"
         rf"Denominator: ({a} + √{b})({a} − √{b}) = {a}² − {b} = {a**2} − {b} = {denom}<br>"
         rf"Result: ({num*a} − {num}√{b}) / {denom}<br>"
         rf"Simplified: <strong>{ans}</strong>")
    hint = rf"The conjugate of ({a} + √{b}) is ({a} − √{b}). Multiplying gives a² − b, removing the surd from the denominator."
    return q, s, hint, 3, raw

def gcse_surds_show_that_rationalise():
    """Exam: 'show that' rationalise with a compound denominator"""
    while True:
        r = random.choice([2, 3, 5, 6, 7])
        a = random.randint(2, 7)
        q_coef = random.randint(1, 3)
        p = random.randint(2, 8)
        new_denom = a ** 2 - r
        if new_denom not in (0, 1, -1):
            break
    new_const = p * a - q_coef * r
    new_coef = q_coef * a - p
    from math import gcd
    g = gcd(gcd(abs(new_const), abs(new_coef)), abs(new_denom))
    nc = new_const // g
    nk = new_coef  // g
    nd = new_denom // g
    sign = "+" if nk >= 0 else "−"
    abs_nk = abs(nk)
    if nd == 1 or nd == -1:
        target = f"{nc} {sign} {abs_nk}√{r}" if abs_nk != 0 else f"{nc}"
    else:
        target = f"( {nc} {sign} {abs_nk}√{r} ) / {abs(nd)}"
    num_str = f"{p} + {q_coef}√{r}" if q_coef > 0 else f"{p}"
    q_text = rf"Show that ( {num_str} ) / ( {a} + √{r} ) can be written as {target}."
    s = (rf"Multiply numerator and denominator by the conjugate ( {a} − √{r} ):<br><br>"
         rf"Numerator: ({num_str})({a} − √{r})<br>"
         rf"= {p}×{a} + {p}×(−√{r}) + {q_coef}√{r}×{a} + {q_coef}√{r}×(−√{r})<br>"
         rf"= {p*a} − {p}√{r} + {q_coef*a}√{r} − {q_coef*r}<br>"
         rf"= ({p*a} − {q_coef*r}) + ({q_coef*a} − {p})√{r}<br>"
         rf"= {new_const} + {new_coef}√{r}<br><br>"
         rf"Denominator: ({a} + √{r})({a} − √{r}) = {a}² − {r} = {new_denom}<br><br>"
         rf"Result: ({new_const} + {new_coef}√{r}) / {new_denom}<br>"
         rf"Divide through by {g}: <strong>{target} ✓</strong>")
    hint = rf"Multiply top and bottom by the conjugate ({a} − √{r}) then expand both brackets fully before simplifying."
    if nk == 0:
        raw = nc if abs(nd) == 1 else _fdp_raw(Fraction(nc, abs(nd)))
    else:
        raw = _algebraic_fraction_expanded_binomial(nc, nk, r, abs(nd))
    return q_text, s, hint, 3, raw

def gcse_surds_identity():
    """Exam: (√a + √b)(√a − √b) = a − b as an algebraic result"""
    q_text = r"Simplify fully ( √a + √b )( √a − √b )."
    s = (r"Use the difference of two squares: (p + q)(p − q) = p² − q²<br>"
         r"Here p = √a and q = √b:<br>"
         r"(√a)² − (√b)² = <strong>a − b</strong>")
    hint = r"(√a + √b)(√a − √b) is a difference of two squares pattern."
    return q_text, s, hint, 2, _algebraic_answer('a-b', 'e.g. a - b')


gcse_surds_identity._fixed_stem = True


def gcse_surds_exact_area():
    """Exam: find area of a rectangle with surd side lengths"""
    a = random.choice([2, 3, 5, 6, 7])
    b = random.choice([2, 3, 5, 6, 7, 10])
    p = random.randint(1, 5)
    q_coef = random.randint(2, 6)
    # Rectangle: side1 = p√a, side2 = q_coef
    area_coef = p * q_coef
    q_text = (rf"A rectangle has sides of length {p}√{a} cm and {q_coef}√{b} cm. "
              rf"Find the exact area of the rectangle. Simplify your answer.")
    product_surd = a * b
    # find largest square factor
    largest_sq = 1
    for s_val in [4, 9, 16, 25, 36]:
        if product_surd % s_val == 0:
            largest_sq = s_val
    k_inner = int(math.sqrt(largest_sq))
    rem = product_surd // largest_sq
    total_k = p * q_coef * k_inner
    if rem == 1:
        ans = f"{total_k} cm²"
        sol_step = (rf"√{a} × √{b} = √{product_surd}<br>"
                    rf"√{product_surd} = {k_inner}<br>"
                    rf"Area = {p} × {q_coef} × {k_inner} = {ans}")
        raw = total_k
    else:
        ans = f"{total_k}√{rem} cm²"
        sol_step = (rf"√{a} × √{b} = √{product_surd}<br>"
                    rf"Simplify √{product_surd}: largest square factor = {largest_sq}, so √{product_surd} = {k_inner}√{rem}<br>"
                    rf"Area = {p} × {q_coef} × {k_inner}√{rem} = <strong>{ans}</strong>")
        raw = _surd_answer(total_k, rem)
    s = (rf"Area = length × width = {p}√{a} × {q_coef}√{b}<br>"
         rf"= ({p} × {q_coef}) × (√{a} × √{b})<br>"
         + sol_step)
    hint = r"Multiply the integer parts together and the surd parts together, then simplify the resulting surd."
    return q_text, s, hint, 3, raw

def gcse_surds_expand_diff_subtract():
    """Exam: expand (p + √q)² − (p − √q)², show it simplifies to k√q"""
    p = random.randint(2, 8)
    q = random.choice([2, 3, 5, 6, 7, 10])
    # (p + √q)² = p² + 2p√q + q
    # (p − √q)² = p² − 2p√q + q
    # difference = 4p√q
    k = 4 * p
    q_text = rf"Expand and simplify ( {p} + √{q} )² − ( {p} − √{q} )²"
    s = (rf"Expand ( {p} + √{q} )²:<br>"
         rf"= {p}² + 2×{p}×√{q} + (√{q})² = {p**2} + {2*p}√{q} + {q}<br><br>"
         rf"Expand ( {p} − √{q} )²:<br>"
         rf"= {p}² − 2×{p}×√{q} + (√{q})² = {p**2} − {2*p}√{q} + {q}<br><br>"
         rf"Subtract: ( {p**2} + {2*p}√{q} + {q} ) − ( {p**2} − {2*p}√{q} + {q} )<br>"
         rf"= {2*p}√{q} + {2*p}√{q} = <strong>{k}√{q}</strong>")
    hint = r"Expand each bracket separately using (a ± √b)² = a² ± 2a√b + b, then subtract — most terms cancel."
    return q_text, s, hint, 3, _surd_answer(k, q)


# ── Surds: intermediate (extra formats) ───────────────────────────────────────

def gcse_surds_practice_divide():
    """Divide one surd by another and simplify."""
    a, b, ans, working, raw = _surd_random_divide()
    q = rf"Simplify: \( \dfrac{{\sqrt{{{a}}}}}{{\sqrt{{{b}}}}} \)"
    s = rf"{working} → <strong>{ans}</strong>"
    hint = r"Use √a ÷ √b = √(a/b), then simplify the surd if possible."
    return q, s, hint, 2, raw


def gcse_surds_practice_compare():
    """Compare the size of two surd expressions."""
    c1, r1, c2, r2, _s1, _s2, _winner, v1, v2 = _surd_random_compare()
    expr1 = rf'\({c1}\sqrt{{{r1}}}\)'
    expr2 = rf'\({c2}\sqrt{{{r2}}}\)'
    from generators.shared.utils import compare_choice_payload
    correct = 'A' if v1 > v2 else 'B'
    winner_expr = expr1 if v1 > v2 else expr2
    q = rf'Which is larger: {expr1} or {expr2}?'
    s = (
        rf'Square both (positive values):<br>'
        rf'\( ({c1}\sqrt{{{r1}}})^2 = {c1**2} \times {r1} = {v1} \)<br>'
        rf'\( ({c2}\sqrt{{{r2}}})^2 = {c2**2} \times {r2} = {v2} \)<br>'
        rf'<strong>{winner_expr}</strong> is larger.'
    )
    hint = r'Compare by squaring, or rewrite each surd in simplest form and compare coefficients × root.'
    return q, s, hint, 2, compare_choice_payload(expr1, expr2, correct)


def gcse_surds_practice_mixed_simplify():
    """Simplify a multi-term surd expression."""
    expr, ans, working, raw = _surd_random_mixed()
    q = rf"Simplify fully: \( {expr} \)"
    s = working
    hint = r"Simplify each surd first, then combine like surds (same number under the root)."
    return q, s, hint, 3, raw


def gcse_surds_practice_double_bracket():
    """Expand general surd double bracket (not difference of squares)."""
    return gcse_surds_expand_double()


# ── Surds: difficult (extra formats) ──────────────────────────────────────────

def gcse_surds_practice_surd_equation():
    """Solve a simple equation involving a square root."""
    rhs, offset, x_val = _surd_random_equation()
    q = rf"Solve: \( \sqrt{{x + {offset}}} = {rhs} \)"
    s = (
        rf"Square both sides: \( x + {offset} = {rhs**2} \)<br>"
        rf"\( x = {rhs**2} - {offset} = <strong>{x_val}</strong> \)"
    )
    hint = r"Square both sides to remove the square root, then solve the linear equation."
    return q, s, hint, 3, x_val


def gcse_surds_rationalise_binomial_diff():
    """Rationalise 1/(√a − √b) using conjugate √a + √b in the numerator."""
    a, b, denom, ans = _surd_random_binomial_diff()
    q = rf"Rationalise the denominator: \( \dfrac{{1}}{{\sqrt{{{a}}} - \sqrt{{{b}}}}} \)"
    s = (
        rf"Multiply top and bottom by \( \sqrt{{{a}}} + \sqrt{{{b}}} \):<br>"
        rf"Denominator becomes \( {a} - {b} = {denom} \)<br>"
        rf"Answer: <strong>\( {ans} \)</strong>"
    )
    hint = (
        r"Multiply by the conjugate √a + √b. The denominator becomes a whole number; "
        r"write the numerator as a sum of surds."
    )
    return q, s, hint, 3, _algebraic_fraction_two_surds(a, b, denom)


def gcse_surds_practice_rationalise_binomial_diff():
    """Difficult pool: rationalise 1/(√a − √b)."""
    q, s, hint, _, raw = gcse_surds_rationalise_binomial_diff()
    return q, s, hint, 4, raw


def gcse_surds_practice_between_which_integers():
    """State between which consecutive integers a surd lies."""
    n, lo, hi = _surd_random_between_integers()
    q = rf"Between which two consecutive whole numbers does \( \sqrt{{{n}}} \) lie?"
    s = (
        rf"\( {lo}^2 = {lo**2} \) and \( {hi}^2 = {hi**2} \)<br>"
        rf"Since \( {lo**2} < {n} < {hi**2} \), \( \sqrt{{{n}}} \) is between "
        rf"<strong>{lo} and {hi}</strong>."
    )
    hint = r"Find the nearest perfect squares below and above n."
    return q, s, hint, 2, _surd_fields_answer((lo, hi), ('Lower bound', 'Upper bound'))


def gcse_surds_practice_perimeter_exact():
    """Perimeter of a shape with surd side lengths."""
    shape = random.choice(["triangle", "square"])
    side_k = random.randint(2, 7)
    surd_r = random.choice([2, 3, 5, 6, 7])
    if shape == "triangle":
        mult, shape_name = 3, "equilateral triangle"
    else:
        mult, shape_name = 4, "square"
    perim_coef = mult * side_k
    q_text = (
        rf"A {shape_name} has side length {side_k}√{surd_r} cm. "
        rf"Find the exact perimeter."
    )
    s = (
        rf"Perimeter = {mult} × {side_k}√{surd_r} = "
        rf"<strong>{_surd_fmt(perim_coef, surd_r)} cm</strong>"
    )
    hint = rf"Add the {mult} equal sides; multiply the coefficient by {mult}."
    return q_text, s, hint, 2, _surd_answer(perim_coef, surd_r)


def gcse_maths_surds(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        from generators.gcse.maths_basic_topics_mcq import gcse_maths_surds_mcq
        return gcse_maths_surds_mcq(difficulty, variant_name)
    if variant_name:
        return _basic_maths_practice('surds', difficulty, mode, variant_name)
    pools = {
        'foundational': [
            gcse_surds_simplify,
            gcse_surds_simplify_multiple,
            gcse_surds_add_subtract,
            gcse_surds_multiply,
        ],
        'intermediate': [
            gcse_surds_expand_simple,
            gcse_surds_expand_double,
            gcse_surds_square_bracket,
            gcse_surds_square_bracket_minus,
            gcse_surds_rationalise_simple,
            gcse_surds_rationalise_compound,
            gcse_surds_rationalise_binomial_diff,
            gcse_surds_practice_divide,
            gcse_surds_practice_compare,
            gcse_surds_practice_mixed_simplify,
            gcse_surds_practice_double_bracket,
        ],
        'difficult': [
            gcse_surds_show_that_rationalise,
            gcse_surds_identity,
            gcse_surds_exact_area,
            gcse_surds_expand_diff_subtract,
            gcse_surds_practice_surd_equation,
            gcse_surds_practice_rationalise_binomial_diff,
            gcse_surds_practice_between_which_integers,
            gcse_surds_practice_perimeter_exact,
        ],
    }
    variant = random.choice(pools.get(difficulty, pools['foundational']))

    return _surd_problem(variant, difficulty)



# -----------------------------------------------
# GCSE Coputer Science — Binary Conversion
# -----------------------------------------------

def gcse_cs_binary(difficulty, mode):

    if difficulty == 'foundational':
        # Denary to binary (0–15, 4-bit)
        n = random.randint(1, 15)
        binary = format(n, '04b')
        q = rf"Convert the denary (decimal) number <strong>{n}</strong> to an 8-bit binary number."
        binary_8 = format(n, '08b')
        # Build step-by-step working
        headers = '128 | 64 | 32 | 16 | 8 | 4 | 2 | 1'
        values  = ' | '.join(list(binary_8))
        s = rf"""Place value table:<br>
        <code>{headers}</code><br>
        <code>&nbsp;{values}</code><br><br>
        Reading the bits: \( {binary_8} \)<br>
        Working: { ' + '.join([str(2**i) for i, b in enumerate(reversed(binary_8)) if b == '1']) } = <strong>{n}</strong> ✓<br><br>
        Answer: <strong>{binary_8}</strong>"""
        hint = r"""
            <strong>Denary to Binary</strong><br>
            Use the place value table: 128, 64, 32, 16, 8, 4, 2, 1<br>
            Work left to right: ask "does this power of 2 fit into the number?"
            If yes, write 1 and subtract. If no, write 0.
        """
        marks = 2

    elif difficulty == 'intermediate':
        # Binary to denary (8-bit)
        n = random.randint(16, 200)
        binary_8 = format(n, '08b')
        place_values = [128, 64, 32, 16, 8, 4, 2, 1]
        working = ' + '.join([str(place_values[i]) for i, b in enumerate(binary_8) if b == '1'])
        q = rf"Convert the binary number <strong>{binary_8}</strong> to denary."
        s = rf"""Place value table:<br>
        <code>128 | 64 | 32 | 16 | 8 | 4 | 2 | 1</code><br>
        <code>&nbsp;{'  | '.join(list(binary_8))}</code><br><br>
        Add the values where there is a 1:<br>
        \( {working} = \boxed{{{n}}} \)"""
        hint = r"""
            <strong>Binary to Denary</strong><br>
            Write out the place values: 128, 64, 32, 16, 8, 4, 2, 1<br>
            Wherever there is a <strong>1</strong> in the binary number,
            add that place value to your total. Ignore 0s.
        """
        marks = 3

    else:  # difficult
        # Binary addition with potential overflow
        a = random.randint(50, 120)
        b = random.randint(50, 120)
        total = a + b
        bin_a = format(a, '08b')
        bin_b = format(b, '08b')
        overflow = total > 255
        bin_total = format(total % 256, '08b')
        overflow_note = (
            rf"<br><br>⚠️ <strong>Overflow error!</strong> The result ({total}) exceeds 255 "
            rf"and cannot be stored in 8 bits. The stored result would be {total % 256} ({bin_total})."
            if overflow else ""
        )
        q = rf"""Add the following 8-bit binary numbers and give the result in binary.
        State whether an overflow error occurs.<br><br>
        <code>&nbsp;&nbsp;{bin_a}</code><br>
        <code>+ {bin_b}</code>"""
        s = rf"""<code>&nbsp;&nbsp;{bin_a}</code> = {a}<br>
        <code>+ {bin_b}</code> = {b}<br>
        <code>{'─' * 12}</code><br>
        <code>&nbsp;&nbsp;{bin_total}</code> = {total % 256}<br><br>
        {'✅ No overflow — result fits in 8 bits.' if not overflow else ''}
        {overflow_note}"""
        hint = r"""
            <strong>Binary Addition Rules</strong><br>
            <ul style="margin:8px 0; padding-left:18px;">
                <li>0 + 0 = 0</li>
                <li>0 + 1 = 1</li>
                <li>1 + 1 = 10 (write 0, carry 1)</li>
                <li>1 + 1 + 1 = 11 (write 1, carry 1)</li>
            </ul>
            <strong>Overflow</strong> occurs when the result exceeds 255 (the maximum for 8 bits).
            Check if your answer requires a 9th bit.
        """
        marks = 4

    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'cs', 'binary')


# ------------------------------------------------------------
# GCSE Maths – Vectors
# ------------------------------------------------------------



def vectors_mcq():
    import random
    questions = [
        {
            "q": "Which of these is a vector quantity?",
            "opts": ["A  Speed", "B  Distance", "C  Velocity", "D  Time"],
            "ans": "C",
            "hint": "Velocity has both speed and direction."
        },
        {
            "q": r"What does \(\begin{pmatrix} 2 \\ -3 \end{pmatrix}\) represent?",
            "opts": ["A  2 left, 3 up", "B  2 right, 3 down", "C  2 right, 3 up", "D  2 left, 3 down"],
            "ans": "B",
            "hint": "Top = horizontal (positive = right), bottom = vertical (negative = down)."
        },
        {
            "q": r"Vector \(\mathbf{a} = \begin{pmatrix} 1 \\ 2 \end{pmatrix}\) and \(\mathbf{b} = \begin{pmatrix} 3 \\ -1 \end{pmatrix}\). Find \(\mathbf{a} + \mathbf{b}\).",
            "opts": ["A  (4, 1)", "B  (4, 3)", "C  (4, 1)", "D  (2, 1)"],
            "ans": "A",
            "hint": "Add the x's separately, then the y's: 1+3=4, 2+(-1)=1."
        },
        {
            "q": r"If \(\mathbf{a} = \begin{pmatrix} 2 \\ 5 \end{pmatrix}\), what is \(-2\mathbf{a}\)?",
            "opts": ["A  (-4, -10)", "B  (-4, 10)", "C  (4, -10)", "D  (-2, -5)"],
            "ans": "A",
            "hint": "Multiply each component by -2."
        },
        {
            "q": r"The magnitude of \(\begin{pmatrix} 6 \\ 8 \end{pmatrix}\) is:",
            "opts": ["A  10", "B  14", "C  100", "D  0"],
            "ans": "A",
            "hint": r"\(\sqrt{6^2+8^2} = \sqrt{36+64} = 10\)."
        },
        {
            "q": r"Which vector is parallel to \(\begin{pmatrix} 2 \\ 4 \end{pmatrix}\)?",
            "opts": ["A  (1,2)", "B  (2,1)", "C  (4,2)", "D  (4,4)"],
            "ans": "A",
            "hint": "Parallel vectors are scalar multiples: (1,2) = 0.5 × (2,4)."
        },
        {
            "q": r"The vector \(\overrightarrow{AB} = \begin{pmatrix} -3 \\ 1 \end{pmatrix}\) means:",
            "opts": ["A  move 3 left, 1 up", "B  move 3 right, 1 down", "C  move 1 left, 3 up", "D  move 3 left, 1 down"],
            "ans": "A",
            "hint": "Negative x = left, positive y = up."
        },
        {
            "q": r"If \(\mathbf{a} = \begin{pmatrix} 4 \\ -2 \end{pmatrix}\) and \(\mathbf{b} = \begin{pmatrix} 1 \\ 3 \end{pmatrix}\), then \(\mathbf{a} - \mathbf{b}\) =",
            "opts": ["A  (3, -5)", "B  (5, 1)", "C  (3, -5)", "D  (5, -1)"],
            "ans": "A",
            "hint": "Subtract components: 4-1=3, -2-3=-5."
        },
        {
            "q": r"The length of the vector \(\begin{pmatrix} 0 \\ 5 \end{pmatrix}\) is:",
            "opts": ["A  5", "B  0", "C  25", "D  1"],
            "ans": "A",
            "hint": r"\(\sqrt{0^2+5^2} = 5\)."
        },
        {
            "q": "Which of these columns is a unit vector?",
            "opts": ["A  (1,0)", "B  (2,2)", "C  (0,0)", "D  (1,1)"],
            "ans": "A",
            "hint": "A unit vector has magnitude 1. (1,0) has length 1."
        },
    ]
    chosen = random.choice(questions)
    q = chosen["q"]
    options = chosen["opts"]
    correct = chosen["ans"]
    s = f"Answer: {correct}\n\n{chosen['hint']}"
    hint = chosen["hint"]
    return q, s, hint, 1, options, correct

# ------------------------------------------------------------
# GCSE Maths – Vectors (full set: 10 / 10 / 10)
# ------------------------------------------------------------


# ---------- vector diagram SVG helpers ----------
def _vectors_diagram_svg(width, height, inner):
    """Compact, MathJax-safe SVG wrapper for practice questions."""
    compact = ' '.join(inner.split())
    return (
        '<div class="question-diagram tex2jax_ignore" style="text-align:center;margin:10px 0;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;" '
        f'role="img" aria-hidden="true">{compact}</svg></div>'
    )


def _svg_vector(x1, y1, x2, y2, label="", color="#01696f", width=200, height=120):
    inner = (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5" '
        f'marker-end="url(#arrow-{label})"/>'
        f'<text x="{(x1+x2)/2 + 10}" y="{(y1+y2)/2 - 6}" font-size="14" font-family="sans-serif" '
        f'fill="{color}" font-weight="bold">{label}</text>'
        f'<defs><marker id="arrow-{label}" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">'
        f'<polygon points="0 0, 10 3.5, 0 7" fill="{color}"/></marker></defs>'
    )
    return _vectors_diagram_svg(width, height, inner)


def _svg_parallelogram_diagonals():
    """Parallelogram ABCD (AB = a, AD = b) with both diagonals dashed; midpoint M marked."""
    Ax, Ay = 60, 178
    Bx, By = 245, 178
    Cx, Cy = 285, 65
    Dx, Dy = 100, 65
    Mx, My = (Ax + Cx) // 2, (Ay + Cy) // 2
    inner = (
        f'<polygon points="{Ax},{Ay} {Bx},{By} {Cx},{Cy} {Dx},{Dy}" fill="#dce8f7" stroke="#1a6fa8" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
        f'<line x1="{Ax}" y1="{Ay}" x2="{Cx}" y2="{Cy}" stroke="#a13544" stroke-width="1.8" stroke-dasharray="7,4"/>'
        f'<line x1="{Bx}" y1="{By}" x2="{Dx}" y2="{Dy}" stroke="#a13544" stroke-width="1.8" stroke-dasharray="7,4"/>'
        f'<circle cx="{Mx}" cy="{My}" r="5" fill="#a13544"/>'
        f'<text x="{Mx + 9}" y="{My - 7}" font-size="13" fill="#a13544" font-weight="bold">M</text>'
        f'<text x="{Ax - 22}" y="{Ay + 6}" font-size="15" font-weight="bold" fill="#1a6fa8">A</text>'
        f'<text x="{Bx + 7}" y="{By + 6}" font-size="15" font-weight="bold" fill="#1a6fa8">B</text>'
        f'<text x="{Cx + 7}" y="{Cy + 6}" font-size="15" font-weight="bold" fill="#1a6fa8">C</text>'
        f'<text x="{Dx - 22}" y="{Dy + 6}" font-size="15" font-weight="bold" fill="#1a6fa8">D</text>'
        f'<text x="{(Ax + Bx) // 2}" y="{Ay + 20}" font-size="13" text-anchor="middle" fill="#1a6fa8" font-style="italic">a</text>'
        f'<text x="{Ax - 30}" y="{(Ay + Dy) // 2 + 5}" font-size="13" text-anchor="middle" fill="#1a6fa8" font-style="italic">b</text>'
    )
    return _vectors_diagram_svg(360, 245, inner)


def _svg_triangle_de(t_d=2/3, t_e=1/3, label_d="D", label_e="E"):
    """Triangle ABC with D on AB at fraction t_d from A and E on AC at t_e from A; DE drawn."""
    Ax, Ay = 165, 25
    Bx, By = 45, 200
    Cx, Cy = 295, 200
    Dx, Dy = int(Ax + t_d * (Bx - Ax)), int(Ay + t_d * (By - Ay))
    Ex, Ey = int(Ax + t_e * (Cx - Ax)), int(Ay + t_e * (Cy - Ay))
    inner = (
        f'<polygon points="{Ax},{Ay} {Bx},{By} {Cx},{Cy}" fill="#dce8f7" stroke="#1a6fa8" '
        f'stroke-width="2.2" stroke-linejoin="round"/>'
        f'<line x1="{Dx}" y1="{Dy}" x2="{Ex}" y2="{Ey}" stroke="#a13544" stroke-width="2.2"/>'
        f'<circle cx="{Dx}" cy="{Dy}" r="5" fill="#a13544"/>'
        f'<circle cx="{Ex}" cy="{Ey}" r="5" fill="#a13544"/>'
        f'<text x="{Ax}" y="{Ay - 10}" font-size="15" font-weight="bold" text-anchor="middle" fill="#1a6fa8">A</text>'
        f'<text x="{Bx - 20}" y="{By + 8}" font-size="15" font-weight="bold" fill="#1a6fa8">B</text>'
        f'<text x="{Cx + 7}" y="{Cy + 8}" font-size="15" font-weight="bold" fill="#1a6fa8">C</text>'
        f'<text x="{Dx - 20}" y="{Dy + 6}" font-size="13" font-weight="bold" fill="#a13544">{label_d}</text>'
        f'<text x="{Ex + 7}" y="{Ey + 6}" font-size="13" font-weight="bold" fill="#a13544">{label_e}</text>'
    )
    return _vectors_diagram_svg(340, 225, inner)


def _svg_section_line(m, n):
    """Horizontal line A---P---B with P dividing AB in ratio m:n; ratio labeled above each segment."""
    Ax, Bx, y = 50, 310, 78
    Px = int(Ax + m / (m + n) * (Bx - Ax))
    inner = (
        f'<line x1="{Ax}" y1="{y}" x2="{Bx}" y2="{y}" stroke="#1a6fa8" stroke-width="2.5"/>'
        f'<circle cx="{Ax}" cy="{y}" r="6" fill="#1a6fa8"/>'
        f'<circle cx="{Bx}" cy="{y}" r="6" fill="#1a6fa8"/>'
        f'<circle cx="{Px}" cy="{y}" r="6" fill="#a13544"/>'
        f'<text x="{Ax}" y="{y + 22}" font-size="15" font-weight="bold" text-anchor="middle" fill="#1a6fa8">A</text>'
        f'<text x="{Bx}" y="{y + 22}" font-size="15" font-weight="bold" text-anchor="middle" fill="#1a6fa8">B</text>'
        f'<text x="{Px}" y="{y + 22}" font-size="14" font-weight="bold" text-anchor="middle" fill="#a13544">P</text>'
        f'<text x="{(Ax + Px) // 2}" y="{y - 14}" font-size="13" text-anchor="middle" fill="#555">{m}</text>'
        f'<text x="{(Px + Bx) // 2}" y="{y - 14}" font-size="13" text-anchor="middle" fill="#555">{n}</text>'
        f'<line x1="{Ax + 14}" y1="{y - 9}" x2="{Px - 14}" y2="{y - 9}" stroke="#555" stroke-width="1"/>'
        f'<line x1="{Px + 14}" y1="{y - 9}" x2="{Bx - 14}" y2="{y - 9}" stroke="#555" stroke-width="1"/>'
    )
    return _vectors_diagram_svg(360, 115, inner)


def _svg_collinear_pts_grid(ax=1, ay=2, bx=3, by=5, cx=5, cy=8):
    """Grid showing three collinear points with parallel vector arrows AB and BC."""
    xs = [ax, bx, cx]
    ys = [ay, by, cy]
    pad = 1
    xmin = min(xs) - pad
    xmax = max(xs) + pad
    ymin = min(ys) - pad
    ymax = max(ys) + pad
    x_span = max(xmax - xmin, 1)
    y_span = max(ymax - ymin, 1)

    margin_l, margin_r, margin_t, margin_b = 28, 32, 14, 30
    max_plot_w, max_plot_h = 280, 175
    cell = min(42, max_plot_w / x_span, max_plot_h / y_span)
    cell = max(18, int(cell))

    plot_w = int(x_span * cell)
    plot_h = int(y_span * cell)
    origin_x = margin_l
    origin_y = margin_t + plot_h
    width = margin_l + plot_w + margin_r
    height = margin_t + plot_h + margin_b

    def sv(x, y):
        return int(origin_x + (x - xmin) * cell), int(origin_y - (y - ymin) * cell)

    Ax, Ay = sv(ax, ay)
    Bx, By = sv(bx, by)
    Cx, Cy = sv(cx, cy)

    gh = "".join(
        f'<line x1="{origin_x}" y1="{origin_y - (y - ymin) * cell}" '
        f'x2="{origin_x + plot_w}" y2="{origin_y - (y - ymin) * cell}" '
        f'stroke="#e0ddd6" stroke-width="1"/>'
        for y in range(int(ymin), int(ymax) + 1)
    )
    gv = "".join(
        f'<line x1="{origin_x + (x - xmin) * cell}" y1="{margin_t}" '
        f'x2="{origin_x + (x - xmin) * cell}" y2="{origin_y}" '
        f'stroke="#e0ddd6" stroke-width="1"/>'
        for x in range(int(xmin), int(xmax) + 1)
    )
    xt = "".join(
        f'<text x="{origin_x + (x - xmin) * cell}" y="{origin_y + 18}" '
        f'font-size="11" text-anchor="middle" fill="#888">{x}</text>'
        for x in range(int(xmin), int(xmax) + 1)
    )
    yt = "".join(
        f'<text x="{origin_x - 14}" y="{origin_y - (y - ymin) * cell + 4}" '
        f'font-size="11" text-anchor="middle" fill="#888">{y}</text>'
        for y in range(int(ymin), int(ymax) + 1)
    )

    axis_x = sv(0, ymin)[0] if xmin <= 0 <= xmax else origin_x
    axis_y = sv(xmin, 0)[1] if ymin <= 0 <= ymax else origin_y
    axes = (
        f'<line x1="{origin_x}" y1="{origin_y}" x2="{origin_x + plot_w}" y2="{origin_y}" '
        f'stroke="#aaa" stroke-width="1.5"/>'
        f'<line x1="{origin_x}" y1="{margin_t}" x2="{origin_x}" y2="{origin_y}" '
        f'stroke="#aaa" stroke-width="1.5"/>'
    )
    if xmin <= 0 <= xmax:
        axes += (
            f'<line x1="{axis_x}" y1="{margin_t}" x2="{axis_x}" y2="{origin_y}" '
            f'stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>'
        )
    if ymin <= 0 <= ymax:
        axes += (
            f'<line x1="{origin_x}" y1="{axis_y}" x2="{origin_x + plot_w}" y2="{axis_y}" '
            f'stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>'
        )

    marker_id = f'arr-cln-{ax}-{ay}-{cx}-{cy}'
    inner = (
        f'<defs><marker id="{marker_id}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
        f'<polygon points="0 0,8 3,0 6" fill="#a13544"/></marker></defs>'
        f'{gh}{gv}{axes}{xt}{yt}'
        f'<line x1="{Ax}" y1="{Ay}" x2="{Bx}" y2="{By}" stroke="#a13544" stroke-width="2.5" '
        f'marker-end="url(#{marker_id})"/>'
        f'<line x1="{Bx}" y1="{By}" x2="{Cx}" y2="{Cy}" stroke="#a13544" stroke-width="2.5" '
        f'marker-end="url(#{marker_id})"/>'
        f'<circle cx="{Ax}" cy="{Ay}" r="5" fill="#333"/>'
        f'<circle cx="{Bx}" cy="{By}" r="5" fill="#333"/>'
        f'<circle cx="{Cx}" cy="{Cy}" r="5" fill="#333"/>'
        f'<text x="{Ax - 14}" y="{Ay + 4}" font-size="12" font-weight="bold" fill="#333" text-anchor="end">A</text>'
        f'<text x="{Bx - 14}" y="{By + 4}" font-size="12" font-weight="bold" fill="#333" text-anchor="end">B</text>'
        f'<text x="{Cx + 8}" y="{Cy + 4}" font-size="12" font-weight="bold" fill="#333">C</text>'
    )
    return _vectors_diagram_svg(width, height, inner)


def _svg_triangle_path_addition(ab=(3, 2), bc=(-1, 4), scale=28):
    """Triangle for AB + BC = AC: AB and BC have solid arrows; resultant AC shown dashed."""
    Ax, Ay = 100, 195
    Bx, By = Ax + ab[0] * scale, Ay - ab[1] * scale
    Cx, Cy = Bx + bc[0] * scale, By - bc[1] * scale
    inner = (
        '<defs>'
        '<marker id="arr-pa1" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#1a6fa8"/></marker>'
        '<marker id="arr-pa2" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#a13544"/></marker>'
        '</defs>'
        f'<line x1="{Ax}" y1="{Ay}" x2="{Bx}" y2="{By}" stroke="#1a6fa8" stroke-width="2.5" marker-end="url(#arr-pa1)"/>'
        f'<line x1="{Bx}" y1="{By}" x2="{Cx}" y2="{Cy}" stroke="#1a6fa8" stroke-width="2.5" marker-end="url(#arr-pa1)"/>'
        f'<line x1="{Ax}" y1="{Ay}" x2="{Cx}" y2="{Cy}" stroke="#a13544" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arr-pa2)"/>'
        f'<circle cx="{Ax}" cy="{Ay}" r="5" fill="#555"/>'
        f'<circle cx="{Bx}" cy="{By}" r="5" fill="#555"/>'
        f'<circle cx="{Cx}" cy="{Cy}" r="5" fill="#555"/>'
        f'<text x="{Ax - 18}" y="{Ay + 5}" font-size="14" font-weight="bold" fill="#333">A</text>'
        f'<text x="{Bx + 8}" y="{By + 5}" font-size="14" font-weight="bold" fill="#333">B</text>'
        f'<text x="{Cx - 8}" y="{Cy - 10}" font-size="14" font-weight="bold" fill="#333">C</text>'
        f'<text x="{(Ax + Bx) // 2 + 10}" y="{(Ay + By) // 2 + 5}" font-size="12" fill="#1a6fa8" font-style="italic">AB</text>'
        f'<text x="{(Bx + Cx) // 2 + 8}" y="{(By + Cy) // 2}" font-size="12" fill="#1a6fa8" font-style="italic">BC</text>'
        f'<text x="{(Ax + Cx) // 2 - 26}" y="{(Ay + Cy) // 2 + 5}" font-size="12" fill="#a13544" font-style="italic">AC</text>'
    )
    return _vectors_diagram_svg(310, 225, inner)


def _svg_triangle_find_bc():
    """Generic triangle ABC: arrows on AB and AC (given); BC shown dashed (to find)."""
    Ax, Ay = 55, 185
    Bx, By = 245, 185
    Cx, Cy = 155, 45
    inner = (
        '<defs>'
        '<marker id="arr-fb1" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#1a6fa8"/></marker>'
        '<marker id="arr-fb2" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#a13544"/></marker>'
        '</defs>'
        f'<line x1="{Ax}" y1="{Ay}" x2="{Bx}" y2="{By}" stroke="#1a6fa8" stroke-width="2.5" marker-end="url(#arr-fb1)"/>'
        f'<line x1="{Ax}" y1="{Ay}" x2="{Cx}" y2="{Cy}" stroke="#1a6fa8" stroke-width="2.5" marker-end="url(#arr-fb1)"/>'
        f'<line x1="{Bx}" y1="{By}" x2="{Cx}" y2="{Cy}" stroke="#a13544" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arr-fb2)"/>'
        f'<circle cx="{Ax}" cy="{Ay}" r="5" fill="#555"/>'
        f'<circle cx="{Bx}" cy="{By}" r="5" fill="#555"/>'
        f'<circle cx="{Cx}" cy="{Cy}" r="5" fill="#555"/>'
        f'<text x="{Ax - 18}" y="{Ay + 5}" font-size="14" font-weight="bold" fill="#333">A</text>'
        f'<text x="{Bx + 8}" y="{By + 5}" font-size="14" font-weight="bold" fill="#333">B</text>'
        f'<text x="{Cx}" y="{Cy - 10}" font-size="14" font-weight="bold" text-anchor="middle" fill="#333">C</text>'
        f'<text x="{(Ax + Bx) // 2}" y="{Ay + 20}" font-size="12" text-anchor="middle" fill="#1a6fa8" font-style="italic">AB</text>'
        f'<text x="{(Ax + Cx) // 2 - 14}" y="{(Ay + Cy) // 2}" font-size="12" fill="#1a6fa8" font-style="italic">AC</text>'
        f'<text x="{(Bx + Cx) // 2 + 14}" y="{(By + Cy) // 2}" font-size="12" fill="#a13544" font-style="italic">BC?</text>'
    )
    return _vectors_diagram_svg(310, 215, inner)


def _svg_trapezium_parallel():
    """Trapezium ABCD with AB (bottom, longer) parallel to DC (top, shorter); AB = 2 DC."""
    Ax, Ay = 50, 178
    Bx, By = 290, 178
    Cx, Cy = 230, 82
    Dx, Dy = 110, 82
    inner = (
        f'<polygon points="{Ax},{Ay} {Bx},{By} {Cx},{Cy} {Dx},{Dy}" fill="#dce8f7" stroke="#1a6fa8" '
        f'stroke-width="2.2" stroke-linejoin="round"/>'
        f'<text x="{Ax - 22}" y="{Ay + 6}" font-size="15" font-weight="bold" fill="#1a6fa8">A</text>'
        f'<text x="{Bx + 7}" y="{By + 6}" font-size="15" font-weight="bold" fill="#1a6fa8">B</text>'
        f'<text x="{Cx + 7}" y="{Cy + 5}" font-size="15" font-weight="bold" fill="#1a6fa8">C</text>'
        f'<text x="{Dx - 22}" y="{Dy + 5}" font-size="15" font-weight="bold" fill="#1a6fa8">D</text>'
        f'<text x="{(Ax + Bx) // 2}" y="{Ay + 20}" font-size="12" text-anchor="middle" fill="#555">AB (longer)</text>'
        f'<text x="{(Dx + Cx) // 2}" y="{Dy - 10}" font-size="12" text-anchor="middle" fill="#555">DC (shorter)</text>'
    )
    return _vectors_diagram_svg(360, 215, inner)


def _svg_parallelogram_three_pts(a=(1, 2), b=(4, 6), c=(9, 8), d=(6, 4)):
    """Grid with three parallelogram vertices marked; D shown as a dashed question-mark point."""
    def sv(x, y): return int(20 + x * 28), int(225 - y * 22)
    Ax, Ay = sv(*a)
    Bx, By = sv(*b)
    Cx, Cy = sv(*c)
    Dx, Dy = sv(*d)
    gh = "".join(f'<line x1="20" y1="{225 - j * 22}" x2="295" y2="{225 - j * 22}" stroke="#e0ddd6" stroke-width="1"/>' for j in range(11))
    gv = "".join(f'<line x1="{20 + i * 28}" y1="5" x2="{20 + i * 28}" y2="230" stroke="#e0ddd6" stroke-width="1"/>' for i in range(11))
    xt = "".join(f'<text x="{20 + i * 28}" y="244" font-size="10" text-anchor="middle" fill="#888">{i}</text>' for i in range(11))
    yt = "".join(f'<text x="8" y="{228 - j * 22}" font-size="10" text-anchor="middle" fill="#888">{j}</text>' for j in range(11))
    inner = (
        f'{gh}{gv}'
        '<line x1="20" y1="225" x2="300" y2="225" stroke="#aaa" stroke-width="1.5"/>'
        '<line x1="20" y1="5" x2="20" y2="230" stroke="#aaa" stroke-width="1.5"/>'
        f'{xt}{yt}'
        f'<polygon points="{Ax},{Ay} {Bx},{By} {Cx},{Cy} {Dx},{Dy}" fill="none" stroke="#1a6fa8" '
        f'stroke-width="1.5" stroke-dasharray="5,3"/>'
        f'<circle cx="{Ax}" cy="{Ay}" r="5" fill="#1a6fa8"/>'
        f'<circle cx="{Bx}" cy="{By}" r="5" fill="#1a6fa8"/>'
        f'<circle cx="{Cx}" cy="{Cy}" r="5" fill="#1a6fa8"/>'
        f'<circle cx="{Dx}" cy="{Dy}" r="6" fill="none" stroke="#a13544" stroke-width="2.5" stroke-dasharray="3,2"/>'
        f'<text x="{Ax - 18}" y="{Ay + 5}" font-size="13" font-weight="bold" fill="#1a6fa8">A</text>'
        f'<text x="{Bx - 16}" y="{By - 8}" font-size="13" font-weight="bold" fill="#1a6fa8">B</text>'
        f'<text x="{Cx + 7}" y="{Cy + 5}" font-size="13" font-weight="bold" fill="#1a6fa8">C</text>'
        f'<text x="{Dx + 8}" y="{Dy + 5}" font-size="13" font-weight="bold" fill="#a13544">D?</text>'
    )
    return _vectors_diagram_svg(330, 255, inner)


def _vectors_pythagorean_components():
    """Return (x, y, magnitude) for a Pythagorean triple suitable for GCSE."""
    if random.random() < 0.65:
        base_triples = [
            (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
            (9, 12, 15), (6, 8, 10), (11, 60, 61), (20, 21, 29),
        ]
        x, y, mag = random.choice(base_triples)
        k = random.randint(1, 4)
        if random.random() < 0.5:
            x, y = y, x
        return x * k, y * k, mag * k
    while True:
        m = random.randint(2, 8)
        n = random.randint(1, m - 1)
        leg1 = m * m - n * n
        leg2 = 2 * m * n
        if random.random() < 0.5:
            x, y = leg1, leg2
        else:
            x, y = leg2, leg1
        if 3 <= x <= 36 and 3 <= y <= 36:
            return x, y, int(math.sqrt(x * x + y * y))


def _vectors_collinear_points():
    """Return collinear A, B, C and the common direction vector."""
    ax = random.randint(0, 4)
    ay = random.randint(0, 4)
    dx = random.randint(1, 4)
    dy = random.randint(1, 4)
    k1 = random.randint(1, 3)
    k2 = k1 + random.randint(1, 3)
    a = (ax, ay)
    b = (ax + k1 * dx, ay + k1 * dy)
    c = (ax + k2 * dx, ay + k2 * dy)
    return a, b, c, (dx, dy)


def _vectors_non_parallel_b(a):
    b = (a[0] + random.randint(1, 3), a[1] + random.choice([-2, -1, 1, 2]))
    if a[0] * b[1] == a[1] * b[0]:
        b = (b[0] + 1, b[1])
    return b


def _vectors_parallel_unknown_pair():
    """Return a, b=(bx,t) parallel to a, and the unknown t."""
    while True:
        a = (random.randint(2, 9), random.randint(2, 9))
        bx = random.randint(1, 8)
        if (a[1] * bx) % a[0] == 0:
            t = a[1] * bx // a[0]
            return a, (bx, t), t


def _vectors_random_parallelogram_vertices():
    """Three known vertices A, B, C of a parallelogram ABCD; return A, B, C, D."""
    a = (random.randint(0, 4), random.randint(0, 4))
    ab = (random.randint(2, 5), random.randint(1, 5))
    ad = (random.randint(-1, 3), random.randint(2, 6))
    b = (a[0] + ab[0], a[1] + ab[1])
    c = (a[0] + ab[0] + ad[0], a[1] + ab[1] + ad[1])
    d = (a[0] + ad[0], a[1] + ad[1])
    return a, b, c, d


def _vectors_direction_words(x, y):
    horiz = f"{abs(x)} unit{'s' if abs(x) != 1 else ''} {'right' if x > 0 else 'left'}"
    if y == 0:
        return horiz
    vert = f"{abs(y)} unit{'s' if abs(y) != 1 else ''} {'up' if y > 0 else 'down'}"
    return f"{horiz} and {vert}"


def _vectors_magnitude_steps(x, y, decimal_places=3):
    """Step-by-step magnitude working and key-concept hint."""
    sq_sum = x * x + y * y
    mag = math.sqrt(sq_sum)
    steps = [
        "<strong>Step 1</strong> — the magnitude is the length of the vector (distance from the origin). "
        "Use Pythagoras on the right-angled triangle formed by the components:",
        rf"|v| = √(x² + y²) = √({x}² + {y}²) = √({x * x} + {y * y}) = √{sq_sum}",
    ]
    if mag == int(mag):
        steps.append(f"<strong>Answer:</strong> <strong>{int(mag)}</strong>")
    elif sq_sum in (2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20):
        steps.append(f"<strong>Answer:</strong> <strong>√{sq_sum}</strong> (exact surd)")
    else:
        steps.append(f"<strong>Answer:</strong> <strong>{mag:.{decimal_places}f}</strong>")
    hint = (
        "Treat the x- and y-components as the two shorter sides of a right-angled triangle. "
        "Square each component, add, then square-root. Leave as a surd (e.g. √13) if it is not "
        "a perfect square."
    )
    return "<br>".join(steps), hint


def _vectors_unit_vector_steps(x, y):
    """Step-by-step unit-vector working and key-concept hint."""
    sq_sum = x * x + y * y
    mag = math.sqrt(sq_sum)
    ux, uy = x / mag, y / mag
    steps = [
        "<strong>Step 1</strong> — find the magnitude of the given vector:",
        rf"|v| = √({x}² + {y}²) = √({x * x} + {y * y}) = √{sq_sum} ≈ {mag:.3f}",
        "<strong>Step 2</strong> — a unit vector has length 1 but points the same way. "
        "Divide <em>each</em> component by the magnitude:",
        rf"Top component: {x} ÷ {mag:.3f} ≈ {ux:.3f}",
        rf"Bottom component: {y} ÷ {mag:.3f} ≈ {uy:.3f}",
        rf"<strong>Answer:</strong> \(\begin{{pmatrix}} {ux:.3f} \\ {uy:.3f} \end{{pmatrix}}\)",
    ]
    hint = (
        "A unit vector is parallel to the original but has magnitude exactly 1. "
        "Find the length with Pythagoras first (√(x² + y²)), then divide both components by "
        "that length. Quick check: squaring and adding your answer's components should give 1."
    )
    return "<br>".join(steps), hint


_VEC_SURD_MAGNITUDES = frozenset({2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20})


def _vec_raw(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:g}"
    return str(value)


def _vec_answer(x, y):
    return {'type': 'vector', 'x': x, 'y': y}


def _vec_keyword_answer(value):
    return {'type': 'keyword', 'value': str(value).strip().lower()}


def _vec_number_pair_answer(val_a, val_b, label_a='x', label_b='y', sep=','):
    return {
        'type': 'number_pair',
        'values': (_vec_raw(val_a), _vec_raw(val_b)),
        'label_a': label_a,
        'label_b': label_b,
        'sep': sep,
    }


def _vec_format_combo_coef(value):
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return f'{value.numerator}/{value.denominator}'
    return _vec_raw(value)


def _vec_vector_combo_answer(*coefficients, labels=('b', 'c')):
    return {
        'type': 'vector_combo',
        'coefficients': tuple(coefficients),
        'labels': tuple(labels),
    }


def _vec_number_fields_answer(values, labels, field_types=None):
    types = tuple(field_types) if field_types else tuple('number' for _ in values)
    return {
        'type': 'number_fields',
        'values': tuple(str(v) for v in values),
        'labels': tuple(labels),
        'field_types': types,
    }


def _vec_two_vectors_answer(x, y, labels=('x', 'y')):
    return {
        'type': 'vector_pair',
        'vectors': (tuple(x), tuple(y)),
        'labels': tuple(labels),
    }


def _vec_magnitude_answer(x, y):
    sq_sum = x * x + y * y
    mag = math.sqrt(sq_sum)
    if mag == int(mag):
        return int(mag)
    if sq_sum in _VEC_SURD_MAGNITUDES:
        return {'type': 'surd', 'coeff': 1, 'radicand': sq_sum}
    return round(mag, 3)


def _vec_vector_raw(raw):
    return f"{_vec_raw(raw['x'])}|{_vec_raw(raw['y'])}"


def _vec_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'vector':
                extra = {
                    'correct_answer_raw': _vec_vector_raw(raw),
                    'answer_type': 'vector',
                    'answer_format_hint': 'Enter the column vector (e.g. (3, 4))',
                }
            elif raw_type == 'number_pair':
                val_a, val_b = raw['values']
                extra = {
                    'correct_answer_raw': f'{val_a}|{val_b}',
                    'answer_type': 'number_pair',
                    'answer_labels': [raw['label_a'], raw['label_b']],
                    'answer_pair_sep': raw.get('sep', 'and'),
                }
            elif raw_type == 'keyword':
                value = raw.get('value')
                if value is not None and str(value).strip():
                    extra = {
                        'correct_answer_raw': str(value).strip().lower(),
                        'answer_type': 'keyword',
                        'answer_format_hint': 'e.g. yes or no',
                    }
            elif raw_type == 'surd':
                coeff = int(raw.get('coeff') or 1)
                radicand = raw.get('radicand')
                if radicand is not None:
                    extra = {
                        'correct_answer_raw': (
                            str(radicand) if coeff == 1 else f'{coeff}|{radicand}'
                        ),
                        'answer_type': 'surd',
                        'answer_format_hint': 'e.g. √13 — use the √ button if needed',
                    }
            elif raw_type == 'vector_combo':
                coeffs = raw.get('coefficients') or ()
                labels = raw.get('labels') or ('b', 'c')
                extra = {
                    'correct_answer_raw': '|'.join(
                        _vec_format_combo_coef(coef) for coef in coeffs
                    ),
                    'answer_type': 'vector_combo',
                    'answer_labels': list(labels),
                    'answer_format_hint': (
                        'Use + or − for each term, then enter each coefficient (e.g. 1/5)'
                    ),
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
                        'answer_format_hint': 'Complete every proof step',
                    }
            elif raw_type == 'vector_pair':
                vectors = raw.get('vectors') or ((), ())
                labels = raw.get('labels') or ('x', 'y')
                parts = []
                for vec in vectors:
                    parts.extend(_vec_raw(component) for component in vec)
                extra = {
                    'correct_answer_raw': '|'.join(parts),
                    'answer_type': 'vector_pair',
                    'answer_labels': list(labels),
                    'answer_format_hint': 'Enter each component in the x and y vectors above',
                }
            elif raw_type == 'proof_steps':
                extra = proof_steps_problem_extra(raw)
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _vec_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
        elif isinstance(raw, str):
            extra = {
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'vectors', **extra)


# ---------- FOUNDATIONAL (14) ----------
def _vectors_found_column_meaning():
    x = random.randint(-6, 8)
    y = random.randint(-6, 8)
    while x == 0 and y == 0:
        y = random.randint(-6, 8)
    meaning = _vectors_direction_words(x, y)
    q = (
        rf"What does the column vector \(\begin{{pmatrix}} {x} \\ {y} \end{{pmatrix}}\) "
        rf"represent? Select all correct statements below."
    )
    s = (
        rf"<strong>Meaning:</strong> move {meaning}.<br>"
        rf"Top number = horizontal ({'right' if x > 0 else 'left' if x < 0 else 'none'}); "
        rf"bottom number = vertical ({'up' if y > 0 else 'down' if y < 0 else 'none'})."
    )
    hint = "Top number = horizontal, bottom = vertical."
    correct_full = f"It means move {meaning}."
    bank = [
        {'id': 'c1', 'text': correct_full},
        {'id': 'c2', 'text': 'The top number is the horizontal component.'},
        {'id': 'c3', 'text': 'The bottom number is the vertical component.'},
        {'id': 'd1', 'text': 'The top number is the vertical component.'},
        {'id': 'd2', 'text': 'The bottom number is the horizontal component.'},
        {
            'id': 'd3',
            'text': (
                f"It means move {_vectors_direction_words(-x if x else 1, -y if y else 1)}."
            ),
        },
        {'id': 'd4', 'text': 'This vector gives the magnitude only, not a direction.'},
    ]
    random.shuffle(bank)
    return q, s, hint, 1, proof_steps_answer(
        ('c1', 'c2', 'c3'),
        bank,
        order_matters=False,
        format_hint='Select every correct statement (order does not matter)',
    )


def _vectors_found_magnitude_3_4():
    x, y, mag = _vectors_pythagorean_components()
    q = rf"Find the magnitude of the vector \(\begin{{pmatrix}} {x} \\ {y} \end{{pmatrix}}\)."
    s, hint = _vectors_magnitude_steps(x, y)
    return q, s, hint, 2, _vec_magnitude_answer(x, y)

def _vectors_found_magnitude_6_8():
    x, y, mag = _vectors_pythagorean_components()
    q = rf"Find the magnitude of the vector \(\begin{{pmatrix}} {x} \\ {y} \end{{pmatrix}}\)."
    s, hint = _vectors_magnitude_steps(x, y)
    return q, s, hint, 2, _vec_magnitude_answer(x, y)

def _vectors_found_add_simple():
    a = (random.randint(1,5), random.randint(-3,6))
    b = (random.randint(1,5), random.randint(-6,3))
    c = (a[0]+b[0], a[1]+b[1])
    q = rf"\(\mathbf{{a}} = \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\) and \(\mathbf{{b}} = \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}}\). Find \(\mathbf{{a}} + \mathbf{{b}}\)."
    s = (
        rf"<strong>Step 1</strong> — add the top components: {a[0]} + {b[0]} = {c[0]}<br>"
        rf"<strong>Step 2</strong> — add the bottom components: {a[1]} + {b[1]} = {c[1]}<br>"
        rf"<strong>Answer:</strong> \(\mathbf{{a}} + \mathbf{{b}} = \begin{{pmatrix}} {c[0]} \\ {c[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "Column vectors add component by component — the top numbers together, "
        "then the bottom numbers together. Do not add across the diagonal."
    )
    return q, s, hint, 2, _vec_answer(c[0], c[1])

def _vectors_found_subtract_simple():
    a = (random.randint(3,7), random.randint(-2,5))
    b = (random.randint(1,4), random.randint(-5,2))
    c = (a[0]-b[0], a[1]-b[1])
    q = rf"\(\mathbf{{a}} = \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\) and \(\mathbf{{b}} = \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}}\). Find \(\mathbf{{a}} - \mathbf{{b}}\)."
    s = (
        rf"<strong>Step 1</strong> — subtract top components: {a[0]} − {b[0]} = {c[0]}<br>"
        rf"<strong>Step 2</strong> — subtract bottom components: {a[1]} − {b[1]} = {c[1]}<br>"
        rf"<strong>Answer:</strong> \(\mathbf{{a}} - \mathbf{{b}} = \begin{{pmatrix}} {c[0]} \\ {c[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "Subtract each component separately: top minus top, bottom minus bottom. "
        "Watch the signs when subtracting negative numbers."
    )
    return q, s, hint, 2, _vec_answer(c[0], c[1])

def _vectors_found_scalar_multiply():
    k = random.choice([2,3,4,-2,-3])
    v = (random.randint(1,5), random.randint(-4,4))
    res = (k*v[0], k*v[1])
    q = rf"If \(\mathbf{{v}} = \begin{{pmatrix}} {v[0]} \\ {v[1]} \end{{pmatrix}}\), find \({k}\mathbf{{v}}\)."
    s = (
        rf"<strong>Step 1</strong> — multiply the top component by {k}: {k} × {v[0]} = {res[0]}<br>"
        rf"<strong>Step 2</strong> — multiply the bottom component by {k}: {k} × {v[1]} = {res[1]}<br>"
        rf"<strong>Answer:</strong> \({k}\mathbf{{v}} = \begin{{pmatrix}} {res[0]} \\ {res[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "Scalar multiplication scales the vector — multiply <em>each</em> component by the number outside. "
        "A negative scalar reverses the direction as well as changing the length."
    )
    return q, s, hint, 2, _vec_answer(res[0], res[1])

def _vectors_found_parallel_check():
    a = (random.randint(1, 6), random.randint(1, 6))
    if random.choice([True, False]):
        k = random.choice([2, 3, -1, -2])
        b = (a[0] * k, a[1] * k)
        is_para = True
        reason = f"Yes, because one vector is a scalar multiple of the other (×{k})."
    else:
        b = _vectors_non_parallel_b(a)
        is_para = False
        reason = "No, because the top is scaled by a different factor than the bottom."
    q = rf"Is \(\begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\) parallel to \(\begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}}\)? Give a reason."
    s = reason
    hint = "Check if you can multiply one vector by a single number to get the other."
    return q, s, hint, 1, _vec_keyword_answer("yes" if is_para else "no")

def _vectors_found_zero_vector():
    v = (random.randint(-8, 8), random.randint(-8, 8))
    while v == (0, 0):
        v = (random.randint(-8, 8), random.randint(-8, 8))
    q = rf"What is the result of \(\begin{{pmatrix}} {v[0]} \\ {v[1]} \end{{pmatrix}} - \begin{{pmatrix}} {v[0]} \\ {v[1]} \end{{pmatrix}}\)?"
    s = r"\(\begin{pmatrix} 0 \\ 0 \end{pmatrix}\) – the zero vector."
    hint = "Subtracting a vector from itself gives the zero vector."
    return q, s, hint, 1, _vec_answer(0, 0)

def _vectors_found_magnitude_zero():
    q = r"What is the magnitude of the vector \(\begin{pmatrix} 0 \\ 0 \end{pmatrix}\)?"
    s = "0"
    hint = "Distance from the origin to (0,0) is zero."
    return q, s, hint, 1, 0

def _vectors_found_negative_vector():
    v = (random.randint(2,6), random.randint(-5,5))
    q = rf"Write the vector that has the same magnitude as \(\begin{{pmatrix}} {v[0]} \\ {v[1]} \end{{pmatrix}}\) but points in the opposite direction."
    s = (
        rf"Reverse the direction by changing the sign of each component:<br>"
        rf"\(\begin{{pmatrix}} {v[0]} \\ {v[1]} \end{{pmatrix}} \rightarrow \begin{{pmatrix}} {-v[0]} \\ {-v[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "Opposite direction means multiply the whole vector by −1 — flip the sign of both the top "
        "and bottom numbers. The length stays the same."
    )
    return q, s, hint, 1, _vec_answer(-v[0], -v[1])


def _vectors_found_position_vector():
    a = (random.randint(-4, 10), random.randint(-4, 10))
    q = rf"Write the position vector of point A({a[0]}, {a[1]})."
    s = rf"\(\overrightarrow{{OA}} = \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\)"
    hint = "A position vector starts at the origin O."
    return q, s, hint, 1, _vec_answer(a[0], a[1])

def _vectors_found_displacement():
    a = (random.randint(1,4), random.randint(1,4))
    b = (random.randint(5,9), random.randint(5,9))
    ab = (b[0]-a[0], b[1]-a[1])
    q = rf"Find the displacement vector \(\overrightarrow{{AB}}\) from A({a[0]},{a[1]}) to B({b[0]},{b[1]})."
    s = (
        rf"<strong>Step 1</strong> — displacement = final position − starting position:<br>"
        rf"\(\overrightarrow{{AB}} = \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}} - \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\)<br>"
        rf"<strong>Step 2</strong> — subtract components: ({b[0]}−{a[0]}, {b[1]}−{a[1]})<br>"
        rf"<strong>Answer:</strong> \(\begin{{pmatrix}} {ab[0]} \\ {ab[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "The displacement vector tells you how to get from A to B. "
        "Subtract A's coordinates from B's — x from x, y from y."
    )
    return q, s, hint, 1, _vec_answer(ab[0], ab[1])

def _vectors_found_equal_vectors():
    a = (random.randint(2,5), random.randint(2,5))
    b = (a[0], a[1]) if random.choice([True, False]) else (a[0]+1, a[1])
    eq = "Yes" if b == a else "No"
    q = rf"Are \(\begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\) and \(\begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}}\) equal?"
    s = f"{eq}. " + ("They have the same components." if eq=="Yes" else "The components differ.")
    hint = "Vectors are equal if both components are equal."
    return q, s, hint, 1, _vec_keyword_answer("yes" if b == a else "no")

def _vectors_found_inverse():
    v = (random.randint(-3,3), random.randint(-3,3))
    inv = (-v[0], -v[1])
    q = rf"Find the vector that must be added to \(\begin{{pmatrix}} {v[0]} \\ {v[1]} \end{{pmatrix}}\) to give the zero vector."
    s = rf"The additive inverse is \(\begin{{pmatrix}} {inv[0]} \\ {inv[1]} \end{{pmatrix}}\)."
    hint = "Add the negative of each component."
    return q, s, hint, 1, _vec_answer(inv[0], inv[1])

# ---------- INTERMEDIATE (14) ----------
def _vectors_inter_magnitude_advanced():
    x = random.randint(4,9)
    y = random.randint(4,9)
    sq_sum = x * x + y * y
    q = rf"Find the exact magnitude of \(\begin{{pmatrix}} {x} \\ {y} \end{{pmatrix}}\)."
    s = (
        rf"<strong>Step 1</strong> — apply Pythagoras:<br>"
        rf"|v| = √({x}² + {y}²) = √({x * x} + {y * y}) = √{sq_sum}<br>"
        rf"<strong>Answer:</strong> <strong>√{sq_sum}</strong> (leave as a surd — not a perfect square)"
    )
    hint = (
        "Square each component, add, then square-root. At GCSE, if the result is not a whole number, "
        "write it as a surd such as √41 rather than rounding."
    )
    return q, s, hint, 2, {"type": "surd", "coeff": 1, "radicand": sq_sum}

def _vectors_inter_parallel_k():
    a = (random.randint(2, 8), random.randint(2, 9))
    k = random.randint(2, 6)
    b = (k * a[0], k * a[1])
    q = rf"Vector \(\mathbf{{a}} = \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\). Find the scalar k such that \(\mathbf{{b}} = \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}} = k\mathbf{{a}}\)."
    s = (
        rf"<strong>Step 1</strong> — parallel vectors are scalar multiples, so k = (top of b) ÷ (top of a):<br>"
        rf"k = {b[0]} ÷ {a[0]} = {k}<br>"
        rf"<strong>Step 2</strong> — check with the bottom components: {b[1]} ÷ {a[1]} = {k} ✓"
    )
    hint = (
        "If b = k a, then each component of b equals k times the matching component of a. "
        "Divide one pair of components to find k, then verify with the other pair."
    )
    return q, s, hint, 2, k

def _vectors_inter_collinear_points():
    a, b, c, direction = _vectors_collinear_points()
    ab = (b[0] - a[0], b[1] - a[1])
    bc = (c[0] - b[0], c[1] - b[1])
    # BC = k · AB
    if ab[0] != 0:
        k = Fraction(bc[0], ab[0])
    else:
        k = Fraction(bc[1], ab[1])
    k_raw = str(k.numerator) if k.denominator == 1 else f'{k.numerator}/{k.denominator}'
    svg = _svg_collinear_pts_grid(*a, *b, *c)
    q = (
        f"{svg}Prove, using vectors, that the points A{a}, B{b}, and C{c} are collinear "
        f"by completing the steps below."
    )
    s = (
        rf"<strong>Method:</strong> find \(\overrightarrow{{AB}}\) and \(\overrightarrow{{BC}}\). "
        rf"If one is a scalar multiple of the other and they share a point, the points are collinear.<br><br>"
        rf"<strong>Step 1</strong> — "
        rf"\(\overrightarrow{{AB}} = \begin{{pmatrix}} {ab[0]} \\ {ab[1]} \end{{pmatrix}}\)<br>"
        rf"<strong>Step 2</strong> — "
        rf"\(\overrightarrow{{BC}} = \begin{{pmatrix}} {bc[0]} \\ {bc[1]} \end{{pmatrix}}\)<br>"
        rf"<strong>Step 3</strong> — \(\overrightarrow{{BC}} = {k_raw}\,\overrightarrow{{AB}}\) "
        rf"(parallel). They share B, so A, B, C are collinear. ✓"
    )
    hint = (
        "Find vectors AB and BC. If BC = k·AB for some scalar k, they are parallel — "
        "and as they share a common point, the three points are collinear."
    )
    return q, s, hint, 3, _vec_number_fields_answer(
        (f'{ab[0]}|{ab[1]}', f'{bc[0]}|{bc[1]}', k_raw),
        (
            'Step 1: vector AB',
            'Step 2: vector BC',
            'Step 3: scalar k such that BC = k × AB',
        ),
        ('vector', 'vector', 'fraction' if '/' in k_raw else 'number'),
    )


def _vectors_inter_path_addition():
    ab = (random.randint(1, 5), random.randint(1, 5))
    bc = (random.randint(-4, 4), random.randint(-4, 5))
    ac = (ab[0] + bc[0], ab[1] + bc[1])
    svg = _svg_triangle_path_addition(ab, bc)
    q = (f"{svg}"
         rf"If \(\overrightarrow{{AB}} = \begin{{pmatrix}} {ab[0]} \\ {ab[1]} \end{{pmatrix}}\) and \(\overrightarrow{{BC}} = \begin{{pmatrix}} {bc[0]} \\ {bc[1]} \end{{pmatrix}}\), find \(\overrightarrow{{AC}}\).")
    s = (
        rf"<strong>Step 1</strong> — follow the path: AC = AB + BC<br>"
        rf"<strong>Step 2</strong> — add components: ({ab[0]}+{bc[0]}, {ab[1]}+{bc[1]})<br>"
        rf"<strong>Answer:</strong> \(\begin{{pmatrix}} {ac[0]} \\ {ac[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "Walking from A to C via B means the overall displacement is AB followed by BC. "
        "Add the vectors component by component."
    )
    return q, s, hint, 2, _vec_answer(ac[0], ac[1])

def _vectors_inter_magnitude_distance():
    p = (random.randint(1,6), random.randint(1,6))
    qp = (random.randint(1,6), random.randint(1,6))
    vec = (qp[0]-p[0], qp[1]-p[1])
    sq_sum = vec[0]**2 + vec[1]**2
    dist = math.sqrt(sq_sum)
    q = rf"Find the distance between point P({p[0]},{p[1]}) and Q({qp[0]},{qp[1]})."
    if dist == int(dist):
        dist_str = str(int(dist))
    elif sq_sum in (2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20):
        dist_str = f"√{sq_sum}"
    else:
        dist_str = f"{dist:.3f}"
    s = (
        rf"<strong>Step 1</strong> — form the displacement vector PQ (Q − P):<br>"
        rf"\(\overrightarrow{{PQ}} = \begin{{pmatrix}} {qp[0]} - {p[0]} \\ {qp[1]} - {p[1]} \end{{pmatrix}} = \begin{{pmatrix}} {vec[0]} \\ {vec[1]} \end{{pmatrix}}\)<br>"
        rf"<strong>Step 2</strong> — distance = magnitude:<br>"
        rf"√({vec[0]}² + {vec[1]}²) = √({vec[0]**2} + {vec[1]**2}) = √{sq_sum} = <strong>{dist_str}</strong>"
    )
    hint = (
        "Distance between two points equals the length of the vector from one to the other. "
        "Subtract coordinates to get the vector, then use Pythagoras on its components."
    )
    return q, s, hint, 2, _vec_magnitude_answer(vec[0], vec[1])

def _vectors_inter_ratio_point():
    a = (random.randint(1, 6), random.randint(1, 6))
    ab = (random.randint(2, 8), random.randint(2, 8))
    ratio = random.randint(2, 5)
    b = (a[0] + ab[0], a[1] + ab[1])
    p = (a[0] + ab[0] * ratio / (ratio + 1), a[1] + ab[1] * ratio / (ratio + 1))
    if ab[0] * ratio % (ratio + 1) == 0 and ab[1] * ratio % (ratio + 1) == 0:
        p = (a[0] + ab[0] * ratio // (ratio + 1), a[1] + ab[1] * ratio // (ratio + 1))
    svg = _svg_section_line(ratio, 1)
    q = (f"{svg}"
         rf"A has coordinates ({a[0]},{a[1]}) and B has coordinates ({b[0]},{b[1]}). "
         rf"Point P lies on AB such that AP:PB = {ratio}:1. Find the coordinates of P.")
    ap_x = ab[0] * ratio / (ratio + 1)
    ap_y = ab[1] * ratio / (ratio + 1)
    s = (rf"\(\overrightarrow{{AP}} = \frac{{{ratio}}}{{{ratio + 1}}}\overrightarrow{{AB}} = \frac{{{ratio}}}{{{ratio + 1}}}\begin{{pmatrix}} {ab[0]} \\ {ab[1]} \end{{pmatrix}} = \begin{{pmatrix}} {ap_x:g} \\ {ap_y:g} \end{{pmatrix}}\)."
         rf" P = A + AP = \(({a[0]} + {ap_x:g},\ {a[1]} + {ap_y:g}) = ({p[0]:g},{p[1]:g})\)")
    hint = f"AP = ratio/(ratio+1) × AB. Multiply each component of AB by {ratio}/{ratio+1}."
    return q, s, hint, 3, _vec_number_pair_answer(p[0], p[1], "x", "y")

def _vectors_inter_parallel_unknown():
    a, b, t = _vectors_parallel_unknown_pair()
    q = (rf"Vector \(\mathbf{{a}} = \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\). "
         rf"For what value of t is \(\mathbf{{b}} = \begin{{pmatrix}} {b[0]} \\ t \end{{pmatrix}}\) parallel to \(\mathbf{{a}}\)?")
    s = (
        rf"<strong>Step 1</strong> — parallel vectors have proportional components:<br>"
        rf"\(\frac{{\text{{top of a}}}}{{\text{{top of b}}}} = \frac{{\text{{bottom of a}}}}{{\text{{bottom of b}}}}\) "
        rf"→ \(\frac{{{a[0]}}}{{{b[0]}}} = \frac{{{a[1]}}}{t}\)<br>"
        rf"<strong>Step 2</strong> — solve for t: t = {b[0]} × {a[1]} ÷ {a[0]} = <strong>{t}</strong>"
    )
    hint = (
        "Parallel column vectors are scalar multiples, so the ratio of tops equals the ratio of bottoms. "
        "Set up the proportion and solve for the unknown."
    )
    return q, s, hint, 2, t

def _vectors_inter_magnitude_comparison():
    v1 = (random.randint(3,6), random.randint(4,8))
    v2 = (random.randint(3,6), random.randint(4,8))
    mag1 = math.sqrt(v1[0]**2+v1[1]**2)
    mag2 = math.sqrt(v2[0]**2+v2[1]**2)
    if mag1>mag2: bigger = "a"
    elif mag2>mag1: bigger = "b"
    else: bigger = "equal"
    q = rf"Which vector has greater magnitude: \(\mathbf{{a}} = \begin{{pmatrix}} {v1[0]} \\ {v1[1]} \end{{pmatrix}}\) or \(\mathbf{{b}} = \begin{{pmatrix}} {v2[0]} \\ {v2[1]} \end{{pmatrix}}\)?"
    s = (
        rf"<strong>Step 1</strong> — |a| = √({v1[0]}² + {v1[1]}²) = √{v1[0]**2 + v1[1]**2} ≈ {mag1:.2f}<br>"
        rf"<strong>Step 2</strong> — |b| = √({v2[0]}² + {v2[1]}²) = √{v2[0]**2 + v2[1]**2} ≈ {mag2:.2f}<br>"
        + (f"<strong>Answer:</strong> a is longer ({mag1:.2f} > {mag2:.2f})" if bigger == "a"
           else f"<strong>Answer:</strong> b is longer ({mag2:.2f} > {mag1:.2f})" if bigger == "b"
           else f"<strong>Answer:</strong> they have equal magnitude ({mag1:.2f})")
    )
    hint = (
        "Calculate the magnitude of each vector separately using Pythagoras, then compare the two lengths."
    )
    return q, s, hint, 2, _vec_keyword_answer(bigger)

def _vectors_inter_vector_equation():
    a = (random.randint(2,4), random.randint(1,4))
    b = (random.randint(1,3), random.randint(2,5))
    c = (2*a[0]+b[0], 2*a[1]+b[1])
    q = rf"Find vector \(\mathbf{{x}}\) if \(2\mathbf{{x}} + \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}} = \begin{{pmatrix}} {c[0]} \\ {c[1]} \end{{pmatrix}}\)."
    x = ((c[0]-b[0])//2, (c[1]-b[1])//2)
    s = (
        rf"<strong>Step 1</strong> — subtract the known vector from both sides:<br>"
        rf"\(2\mathbf{{x}} = \begin{{pmatrix}} {c[0]} \\ {c[1]} \end{{pmatrix}} - \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}} = \begin{{pmatrix}} {c[0]-b[0]} \\ {c[1]-b[1]} \end{{pmatrix}}\)<br>"
        rf"<strong>Step 2</strong> — divide both components by 2:<br>"
        rf"\(\mathbf{{x}} = \begin{{pmatrix}} {x[0]} \\ {x[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "Treat this like a normal equation: subtract the fixed vector first, then divide "
        "each component by 2 to undo the scalar multiplication."
    )
    return q, s, hint, 2, _vec_answer(x[0], x[1])

def _vectors_inter_position_geometry():
    a = (random.randint(1,6), random.randint(1,6))
    b = (random.randint(1,6), random.randint(1,6))
    ab = (b[0]-a[0], b[1]-a[1])
    q = rf"Points A and B have position vectors \(\begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\) and \(\begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}}\). Find \(\overrightarrow{{AB}}\)."
    s = (
        rf"<strong>Step 1</strong> — displacement from A to B = position of B − position of A:<br>"
        rf"\(\overrightarrow{{AB}} = \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}} - \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\)<br>"
        rf"<strong>Step 2</strong> — subtract components: ({b[0]}−{a[0]}, {b[1]}−{a[1]})<br>"
        rf"<strong>Answer:</strong> \(\begin{{pmatrix}} {ab[0]} \\ {ab[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "A position vector starts at the origin. To go from A to B, subtract A's position vector "
        "from B's — component by component."
    )
    return q, s, hint, 2, _vec_answer(ab[0], ab[1])

def _vectors_inter_midpoint_vector():
    a = (random.randint(1,4), random.randint(1,4))
    b = (random.randint(5,8), random.randint(5,8))
    mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    q = rf"Find the position vector of the midpoint of points A({a[0]},{a[1]}) and B({b[0]},{b[1]})."
    s = (
        rf"<strong>Step 1</strong> — average the x-coordinates: ({a[0]} + {b[0]}) ÷ 2 = {mid[0]}<br>"
        rf"<strong>Step 2</strong> — average the y-coordinates: ({a[1]} + {b[1]}) ÷ 2 = {mid[1]}<br>"
        rf"<strong>Answer:</strong> midpoint = ({mid[0]}, {mid[1]})"
    )
    hint = (
        "The midpoint is exactly halfway between the two points — add corresponding coordinates "
        "and divide each by 2."
    )
    return q, s, hint, 2, _vec_number_pair_answer(mid[0], mid[1], "x", "y")

def _vectors_inter_translation():
    point = (random.randint(1,5), random.randint(1,5))
    vec = (random.randint(-3,3), random.randint(-3,3))
    image = (point[0]+vec[0], point[1]+vec[1])
    q = rf"Point P({point[0]},{point[1]}) is translated by vector \(\begin{{pmatrix}} {vec[0]} \\ {vec[1]} \end{{pmatrix}}\). Find the coordinates of the image P'."
    s = (
        rf"<strong>Step 1</strong> — add the translation to each coordinate:<br>"
        rf"x: {point[0]} + {vec[0]} = {image[0]}<br>"
        rf"y: {point[1]} + {vec[1]} = {image[1]}<br>"
        rf"<strong>Answer:</strong> P' = ({image[0]}, {image[1]})"
    )
    hint = (
        "A translation shifts every point by the same vector — add the vector's components "
        "to the point's x- and y-coordinates."
    )
    return q, s, hint, 2, _vec_number_pair_answer(image[0], image[1], "x", "y")

def _vectors_inter_vector_path():
    ab = (random.randint(2, 5), random.randint(1, 4))
    bc = (random.randint(-3, 3), random.randint(-3, 3))
    ac = (ab[0] + bc[0], ab[1] + bc[1])
    svg = _svg_triangle_find_bc()
    q = (f"{svg}"
         rf"In triangle ABC, \(\overrightarrow{{AB}} = \begin{{pmatrix}} {ab[0]} \\ {ab[1]} \end{{pmatrix}}\) and \(\overrightarrow{{AC}} = \begin{{pmatrix}} {ac[0]} \\ {ac[1]} \end{{pmatrix}}\). Find \(\overrightarrow{{BC}}\).")
    s = (
        rf"<strong>Step 1</strong> — use AC = AB + BC, so BC = AC − AB<br>"
        rf"<strong>Step 2</strong> — subtract components: ({ac[0]}−{ab[0]}, {ac[1]}−{ab[1]})<br>"
        rf"<strong>Answer:</strong> \(\begin{{pmatrix}} {bc[0]} \\ {bc[1]} \end{{pmatrix}}\)"
    )
    hint = (
        "The vector from A to C equals AB plus BC. Rearrange to BC = AC − AB, "
        "then subtract matching components."
    )
    return q, s, hint, 3, _vec_answer(bc[0], bc[1])

# ---------- DIFFICULT (10) ----------
def _vectors_diff_geometry_proof():
    svg = _svg_parallelogram_diagonals()
    q = (
        rf"{svg}ABCD is a parallelogram with \(\overrightarrow{{AB}} = \mathbf{{a}}\) and "
        rf"\(\overrightarrow{{AD}} = \mathbf{{b}}\). Prove, using vectors, that the diagonals "
        rf"bisect each other by completing the steps below."
    )
    s = (
        r"<strong>Method:</strong> find the midpoint of each diagonal from A; show they coincide.<br><br>"
        r"<strong>Step 1</strong> — \(\overrightarrow{AC} = \mathbf{a}+\mathbf{b}\), so midpoint M of AC "
        r"has position \(\dfrac{1}{2}(\mathbf{a}+\mathbf{b})\) from A.<br><br>"
        r"<strong>Step 2</strong> — \(\overrightarrow{BD} = \mathbf{b}-\mathbf{a}\). Midpoint of BD "
        r"from A: \(\mathbf{a}+\dfrac{1}{2}(\mathbf{b}-\mathbf{a}) = \dfrac{1}{2}(\mathbf{a}+\mathbf{b})\).<br><br>"
        r"<strong>Step 3</strong> — Both midpoints are \(\dfrac{1}{2}(\mathbf{a}+\mathbf{b})\), "
        r"so the diagonals bisect each other. ✓"
    )
    hint = "Express each diagonal in terms of a and b, find both midpoints, and show they are equal."
    return q, s, hint, 4, _vec_number_fields_answer(
        ('(a + b)/2', '(a + b)/2', 'yes'),
        (
            'Step 1: midpoint of AC from A (in terms of a and b)',
            'Step 2: midpoint of BD from A (in terms of a and b)',
            'Step 3: do the midpoints coincide? (yes/no)',
        ),
        ('algebraic', 'algebraic', 'keyword'),
    )


def _vectors_diff_ratio_theorem():
    a = (random.randint(1, 6), random.randint(1, 6))
    b = (random.randint(7, 12), random.randint(7, 12))
    ratio1 = random.randint(2, 4)
    ratio2 = random.randint(2, 5)
    op = ((ratio2 * a[0] + ratio1 * b[0]) / (ratio1 + ratio2),
          (ratio2 * a[1] + ratio1 * b[1]) / (ratio1 + ratio2))
    svg = _svg_section_line(ratio1, ratio2)
    q = (f"{svg}"
         rf"Points A({a[0]},{a[1]}) and B({b[0]},{b[1]}) have position vectors \(\mathbf{{a}}\) and \(\mathbf{{b}}\). "
         rf"Point P lies on AB such that AP:PB = {ratio1}:{ratio2}. Find the position vector of P.")
    s = (rf"Section formula: \(\overrightarrow{{OP}} = \frac{{{ratio2}\mathbf{{a}} + {ratio1}\mathbf{{b}}}}{{{ratio1 + ratio2}}} "
         rf"= \begin{{pmatrix}} \frac{{{ratio2}\times{a[0]}+{ratio1}\times{b[0]}}}{{{ratio1+ratio2}}} \\ \frac{{{ratio2}\times{a[1]}+{ratio1}\times{b[1]}}}{{{ratio1+ratio2}}} \end{{pmatrix}} "
         rf"= \begin{{pmatrix}} {op[0]:g} \\ {op[1]:g} \end{{pmatrix}}\)")
    hint = "Section formula for AP:PB = m:n: OP = (n·a + m·b) / (m+n)."
    return q, s, hint, 3, _vec_answer(op[0], op[1])

def _vectors_diff_collinear_proof():
    p, q_pt, r, direction = _vectors_collinear_points()
    pq = (q_pt[0] - p[0], q_pt[1] - p[1])
    pr = (r[0] - p[0], r[1] - p[1])
    k = pr[0] // pq[0] if pq[0] else pr[1] // pq[1]
    q = f"Points P{p}, Q{q_pt}, R{r} are given. Determine whether they are collinear."
    s = (
        rf"<strong>Step 1</strong> — find vectors along the line segments:<br>"
        rf"PQ = ({pq[0]}, {pq[1]}), PR = ({pr[0]}, {pr[1]})<br>"
        rf"<strong>Step 2</strong> — check if one is a scalar multiple of the other:<br>"
        rf"PR = {k} × PQ → the vectors are parallel<br>"
        rf"<strong>Conclusion:</strong> Yes, P, Q and R are collinear (they share point P and the directions match)."
    )
    hint = (
        "Three points are collinear if the vectors between them are parallel (one is a multiple of the other) "
        "and they share a common point."
    )
    return q, s, hint, 3, _vec_keyword_answer("yes")

def _vectors_diff_triangle_midpoint():
    svg = _svg_triangle_de(1/2, 1/2, "D", "E")
    q = (
        rf"{svg}In triangle ABC, D is the midpoint of AB and E is the midpoint of AC. "
        rf"Let \(\overrightarrow{{AB}} = \mathbf{{b}}\) and \(\overrightarrow{{AC}} = \mathbf{{c}}\). "
        rf"Prove that \(\overrightarrow{{DE}} = \frac{{1}}{{2}}\overrightarrow{{BC}}\) "
        rf"by completing the steps below."
    )
    s = (
        r"<strong>Method:</strong> use A as origin; find AD and AE, then DE = AE − AD.<br><br>"
        r"<strong>Step 1</strong> — \(\overrightarrow{AD} = \dfrac{1}{2}\mathbf{b}\)<br>"
        r"<strong>Step 2</strong> — \(\overrightarrow{AE} = \dfrac{1}{2}\mathbf{c}\)<br>"
        r"<strong>Step 3</strong> — \(\overrightarrow{DE} = \overrightarrow{AE} - \overrightarrow{AD} "
        r"= \dfrac{1}{2}\mathbf{c} - \dfrac{1}{2}\mathbf{b} = \dfrac{1}{2}(\mathbf{c}-\mathbf{b}) "
        r"= \dfrac{1}{2}\overrightarrow{BC}\).<br>"
        r"Hence DE ∥ BC and DE = ½ BC. ✓"
    )
    hint = "Express D and E using the section formula (midpoint), then find DE = AE − AD."
    return q, s, hint, 4, _vec_number_fields_answer(
        ('b/2', 'c/2', '(c - b)/2'),
        (
            'Step 1: AD in terms of b',
            'Step 2: AE in terms of c',
            'Step 3: DE in terms of b and c',
        ),
        ('algebraic', 'algebraic', 'algebraic'),
    )


def _vectors_diff_trapezium_ratio():
    svg = _svg_trapezium_parallel()
    q = (
        rf"{svg}In trapezium ABCD, AB \(\parallel\) DC and AB = 2 DC. "
        rf"Express \(\overrightarrow{{DC}}\) in terms of \(\overrightarrow{{AB}}\)."
    )
    s = r"Since AB \(\parallel\) DC and AB = 2 DC, the vectors point in the same direction but DC is half the length. Therefore \(\overrightarrow{DC} = \frac{1}{2}\overrightarrow{AB}\)."
    hint = "Parallel vectors with the same sense are positive scalar multiples. If AB = 2 DC, then DC = ½ AB."
    return q, s, hint, 2, _vec_vector_combo_answer(Fraction(1, 2), labels=('AB',))

def _vectors_diff_vector_inequality():
    q = (
        r"Prove that for any two vectors \(\mathbf{a}\) and \(\mathbf{b}\), "
        r"\(|\mathbf{a}+\mathbf{b}| \le |\mathbf{a}| + |\mathbf{b}|\). "
        r"Build the proof by selecting the correct steps in order."
    )
    s = (
        r"<strong>Triangle inequality</strong><br>"
        r"Place \(\mathbf{a}\) and \(\mathbf{b}\) tip-to-tail so they form two sides of a triangle "
        r"with \(\mathbf{a}+\mathbf{b}\) as the third side.<br>"
        r"In any triangle, each side is shorter than (or equal to) the sum of the other two.<br>"
        r"Therefore \(|\mathbf{a}+\mathbf{b}| \le |\mathbf{a}| + |\mathbf{b}|\). ✓"
    )
    hint = "Think of the vectors as sides of a triangle."
    bank = [
        {
            'id': 's1',
            'text': (
                'Place a and b tip-to-tail so they form two sides of a triangle, '
                'with a + b as the third side.'
            ),
        },
        {
            'id': 's2',
            'text': (
                'In any triangle, each side length is at most the sum of the other two side lengths.'
            ),
        },
        {
            'id': 's3',
            'text': 'Hence |a + b| ≤ |a| + |b| (the triangle inequality).',
        },
        {
            'id': 'd1',
            'text': 'In any triangle, each side is longer than the sum of the other two.',
        },
        {
            'id': 'd2',
            'text': 'Vectors always satisfy |a + b| = |a| + |b| for every a and b.',
        },
        {
            'id': 'd3',
            'text': 'Use Pythagoras: |a + b|² = |a|² + |b|² for all vectors a and b.',
        },
    ]
    random.shuffle(bank)
    return q, s, hint, 2, proof_steps_answer(
        ('s1', 's2', 's3'),
        bank,
        order_matters=True,
        format_hint='Select the correct proof steps in order',
    )


def _vectors_diff_parallelogram_area():
    a=(random.randint(2,5), random.randint(1,4))
    b=(random.randint(1,4), random.randint(2,5))
    cross = a[0]*b[1] - a[1]*b[0]
    q = rf"Vectors \(\mathbf{{a}} = \begin{{pmatrix}} {a[0]} \\ {a[1]} \end{{pmatrix}}\) and \(\mathbf{{b}} = \begin{{pmatrix}} {b[0]} \\ {b[1]} \end{{pmatrix}}\) form a parallelogram. Calculate its area."
    s = (
        rf"<strong>Step 1</strong> — area of a parallelogram from two side vectors = |a₁b₂ − a₂b₁|:<br>"
        rf"a₁b₂ − a₂b₁ = ({a[0]} × {b[1]}) − ({a[1]} × {b[0]}) = {a[0]*b[1]} − {a[1]*b[0]} = {cross}<br>"
        rf"<strong>Step 2</strong> — take the absolute value: |{cross}| = <strong>{abs(cross)}</strong>"
    )
    hint = (
        "The area equals the magnitude of the '2D cross product': multiply the top of a by the bottom of b, "
        "subtract the bottom of a times the top of b, then take the absolute value."
    )
    return q, s, hint, 3, abs(cross)

def _vectors_diff_unknown_parallel():
    p, qv, t = _vectors_parallel_unknown_pair()
    q = (rf"Vectors \(\mathbf{{p}} = \begin{{pmatrix}} {p[0]} \\ {p[1]} \end{{pmatrix}}\) and "
         rf"\(\mathbf{{q}} = \begin{{pmatrix}} {qv[0]} \\ t \end{{pmatrix}}\) are parallel. Find t.")
    s = (
        rf"<strong>Step 1</strong> — parallel vectors have equal component ratios:<br>"
        rf"\(\frac{{{p[0]}}}{{{qv[0]}}} = \frac{{{p[1]}}}{t}\)<br>"
        rf"<strong>Step 2</strong> — solve: t = {qv[0]} × {p[1]} ÷ {p[0]} = <strong>{t}</strong>"
    )
    hint = (
        "Set the ratio of tops equal to the ratio of bottoms, then solve for the unknown component."
    )
    return q, s, hint, 2, t

def _vectors_diff_geometry_parallelogram():
    a, b, c, d = _vectors_random_parallelogram_vertices()
    ab = (b[0] - a[0], b[1] - a[1])
    svg = _svg_parallelogram_three_pts(a, b, c, d)
    q = (f"{svg}Three vertices of a parallelogram ABCD are A{a}, B{b}, and C{c}. "
         f"Find the coordinates of the fourth vertex D.")
    s = (rf"In parallelogram ABCD, \(\overrightarrow{{AB}} = \overrightarrow{{DC}}\) (opposite sides equal and parallel)."
         rf"<br>\(\overrightarrow{{AB}} = \begin{{pmatrix}} {ab[0]} \\ {ab[1]} \end{{pmatrix}}\)."
         rf" Since DC = AB, D = C \(-\) AB = \(({c[0]}-{ab[0]},\ {c[1]}-{ab[1]}) = ({d[0]},{d[1]})\)."
         rf"<br>Alternatively: D = A + C \(-\) B = ({a[0]}+{c[0]}\(-\){b[0]},\ {a[1]}+{c[1]}\(-\){b[1]}) = ({d[0]},{d[1]})\).")
    hint = "Use D = A + C − B (the diagonal property: midpoints of AC and BD must coincide)."
    return q, s, hint, 3, _vec_number_pair_answer(d[0], d[1], "x", "y")

def _vectors_diff_vector_method_simultaneous():
    x = (random.randint(1, 8), random.randint(1, 8))
    y = (random.randint(1, 8), random.randint(1, 8))
    sum_v = (x[0] + y[0], x[1] + y[1])
    diff_v = (x[0] - y[0], x[1] - y[1])
    q = (rf"Solve for vectors \(\mathbf{{x}}\) and \(\mathbf{{y}}\): "
         rf"\(\mathbf{{x}}+\mathbf{{y}} = \begin{{pmatrix}}{sum_v[0]}\\{sum_v[1]}\end{{pmatrix}}\) and "
         rf"\(\mathbf{{x}}-\mathbf{{y}} = \begin{{pmatrix}}{diff_v[0]}\\{diff_v[1]}\end{{pmatrix}}\).")
    s = (
        rf"<strong>Step 1</strong> — add the equations to eliminate y:<br>"
        rf"\(2\mathbf{{x}} = \begin{{pmatrix}}{sum_v[0]+diff_v[0]}\\{sum_v[1]+diff_v[1]}\end{{pmatrix}} "
        rf"\Rightarrow \mathbf{{x}} = \begin{{pmatrix}}{x[0]}\\{x[1]}\end{{pmatrix}}\)<br>"
        rf"<strong>Step 2</strong> — substitute into x + y = ({sum_v[0]}, {sum_v[1]}):<br>"
        rf"\(\mathbf{{y}} = \begin{{pmatrix}}{sum_v[0]-x[0]}\\{sum_v[1]-x[1]}\end{{pmatrix}} = \begin{{pmatrix}}{y[0]}\\{y[1]}\end{{pmatrix}}\)"
    )
    hint = (
        "Add the two vector equations to cancel y and find x, then substitute back to find y. "
        "Work on the top and bottom components together."
    )
    return q, s, hint, 3, _vec_two_vectors_answer(x, y)

def _vectors_diff_ratio_collinear():
    a = (random.randint(1, 6), random.randint(1, 6))
    b = (random.randint(7, 12), random.randint(7, 12))
    ratio = random.randint(2, 5)
    px = (a[0] + ratio * b[0]) / (1 + ratio)
    py = (a[1] + ratio * b[1]) / (1 + ratio)
    svg = _svg_section_line(1, ratio)
    q = (f"{svg}"
         rf"Points A({a[0]},{a[1]}) and B({b[0]},{b[1]}) are given. "
         rf"Point P lies on AB such that AP:PB = 1:{ratio}. Find the coordinates of P.")
    s = (rf"Section formula (AP:PB = 1:{ratio}): "
         rf"\(\overrightarrow{{OP}} = \frac{{{ratio}\mathbf{{a}}+1\cdot\mathbf{{b}}}}{{{1+ratio}}}\). "
         rf"P = \(\left(\frac{{{ratio}\times{a[0]}+{b[0]}}}{{{1+ratio}}},\ \frac{{{ratio}\times{a[1]}+{b[1]}}}{{{1+ratio}}}\right) = ({px:.1f},\ {py:.1f})\)")
    hint = "Section formula for AP:PB = m:n: P = (n·A + m·B) / (m+n)."
    return q, s, hint, 3, _vec_number_pair_answer(round(px, 1), round(py, 1), "x", "y")

def _vectors_diff_vector_proof_sim():
    # Same parallelogram-diagonals proof as _vectors_diff_geometry_proof (Plan B scaffold).
    return _vectors_diff_geometry_proof()


def _vectors_diff_parallel_unit():
    v = (random.randint(3,6), random.randint(4,9))
    q = rf"Find a unit vector parallel to \(\begin{{pmatrix}} {v[0]} \\ {v[1]} \end{{pmatrix}}\)."
    s, hint = _vectors_unit_vector_steps(v[0], v[1])
    return q, s, hint, 3, _vec_answer(round(v[0] / math.sqrt(v[0]**2 + v[1]**2), 3), round(v[1] / math.sqrt(v[0]**2 + v[1]**2), 3))

def _vectors_diff_geometric_ratio():
    m = random.randint(2, 4)
    n = random.randint(1, 3)
    p = random.randint(1, 3)
    q_ratio = random.randint(2, 4)
    t_d = m / (m + n)
    t_e = p / (p + q_ratio)
    svg = _svg_triangle_de(t_d, t_e, "D", "E")
    q = (f"{svg}In triangle ABC, D is on AB such that AD:DB = {m}:{n} and E is on AC such that AE:EC = {p}:{q_ratio}. "
         r"Let \(\overrightarrow{AB} = \mathbf{b}\) and \(\overrightarrow{AC} = \mathbf{c}\) (with A as origin). "
         r"Express \(\overrightarrow{DE}\) in terms of \(\mathbf{b}\) and \(\mathbf{c}\).")
    s = (rf"AD:DB = {m}:{n}, so D divides AB in ratio {m}:{n} from A: \(\overrightarrow{{AD}} = \frac{{{m}}}{{{m+n}}}\mathbf{{b}}\)."
         rf"<br>AE:EC = {p}:{q_ratio}, so E divides AC in ratio {p}:{q_ratio} from A: \(\overrightarrow{{AE}} = \frac{{{p}}}{{{p+q_ratio}}}\mathbf{{c}}\)."
         rf"<br>\(\overrightarrow{{DE}} = \overrightarrow{{AE}} - \overrightarrow{{AD}} = \frac{{{p}}}{{{p+q_ratio}}}\mathbf{{c}} - \frac{{{m}}}{{{m+n}}}\mathbf{{b}}\)")
    hint = "Use the section formula for each point (fraction of the way from A), then DE = AE − AD."
    coef_b = -Fraction(m, m + n)
    coef_c = Fraction(p, p + q_ratio)
    return q, s, hint, 4, _vec_vector_combo_answer(coef_b, coef_c, labels=('b', 'c'))


_VECTORS_HELPER_NAMES = {
    '_vectors_pythagorean_components', '_vectors_collinear_points', '_vectors_non_parallel_b',
    '_vectors_parallel_unknown_pair', '_vectors_random_parallelogram_vertices', '_vectors_direction_words',
}

for _vectors_name, _vectors_fn in list(globals().items()):
    if not _vectors_name.startswith('_vectors_') or not callable(_vectors_fn):
        continue
    if _vectors_name in _VECTORS_HELPER_NAMES or _vectors_name.startswith('_vectors_diagram'):
        continue
    try:
        if len(inspect.signature(_vectors_fn).parameters) != 0:
            continue
    except (TypeError, ValueError):
        continue
    if getattr(_vectors_fn, '_fixed_stem', False):
        continue
    _vectors_fn._randomizable = True

for _vectors_fixed_stem_fn in (
    _vectors_found_magnitude_zero,
    _vectors_diff_geometry_proof,
    _vectors_diff_triangle_midpoint,
    _vectors_diff_trapezium_ratio,
    _vectors_diff_vector_inequality,
    _vectors_diff_vector_proof_sim,
):
    _vectors_fixed_stem_fn._fixed_stem = True
    _vectors_fixed_stem_fn._randomizable = False

# ---------- MCQs ----------
_VECTORS_MCQ_RAW = [
    {"q": "Which of these is a vector quantity?", "opts": ["A  Speed","B  Distance","C  Velocity","D  Time"], "ans":"C", "sol": "Velocity has magnitude <em>and</em> direction; speed and distance do not. Answer: <strong>C</strong>", "hint":"Velocity has both speed and direction — that makes it a vector."},
    {"q": r"What does \(\begin{pmatrix} 2 \\ -3 \end{pmatrix}\) represent?", "opts":["A  2 left, 3 up","B  2 right, 3 down","C  2 right, 3 up","D  2 left, 3 down"], "ans":"B", "sol": "Top = +2 (right), bottom = −3 (down). Answer: <strong>B</strong>", "hint":"Top = horizontal (positive = right), bottom = vertical (negative = down)."},
    {"q": r"Vector \(\mathbf{a} = \begin{pmatrix} 1 \\ 2 \end{pmatrix}\) and \(\mathbf{b} = \begin{pmatrix} 3 \\ -1 \end{pmatrix}\). Find \(\mathbf{a} + \mathbf{b}\).", "opts":["A  (4, 1)","B  (4, 3)","C  (2, 3)","D  (2, 1)"], "ans":"A", "sol": "Add tops: 1+3=4. Add bottoms: 2+(−1)=1. Answer: <strong>(4, 1)</strong>", "hint":"Add the x's separately, then the y's: 1+3=4, 2+(-1)=1."},
    {"q": r"If \(\mathbf{a} = \begin{pmatrix} 2 \\ 5 \end{pmatrix}\), what is \(-2\mathbf{a}\)?", "opts":["A  (-4, -10)","B  (-4, 10)","C  (4, -10)","D  (-2, -5)"], "ans":"A", "sol": "Multiply each component by −2: (−4, −10). Answer: <strong>A</strong>", "hint":"Multiply each component by -2."},
    {"q": r"The magnitude of \(\begin{pmatrix} 6 \\ 8 \end{pmatrix}\) is:", "opts":["A  10","B  14","C  100","D  0"], "ans":"A", "sol": r"√(6²+8²) = √(36+64) = √100 = <strong>10</strong>. Answer: A", "hint":r"Use Pythagoras: √(6²+8²) = √(36+64) = 10."},
    {"q": r"Which vector is parallel to \(\begin{pmatrix} 2 \\ 4 \end{pmatrix}\)?", "opts":["A  (1,2)","B  (2,1)","C  (4,2)","D  (4,4)"], "ans":"A", "sol": "(1,2) = ½ × (2,4) — same direction, half the length. Answer: <strong>A</strong>", "hint":"Parallel vectors are scalar multiples: (1,2) = 0.5 × (2,4)."},
    {"q": r"The vector \(\overrightarrow{AB} = \begin{pmatrix} -3 \\ 1 \end{pmatrix}\) means:", "opts":["A  move 3 left, 1 up","B  move 3 right, 1 down","C  move 1 left, 3 up","D  move 3 left, 1 down"], "ans":"A", "sol": "−3 = 3 left, +1 = 1 up. Answer: <strong>A</strong>", "hint":"Negative x = left, positive y = up."},
    {"q": r"If \(\mathbf{a} = \begin{pmatrix} 4 \\ -2 \end{pmatrix}\) and \(\mathbf{b} = \begin{pmatrix} 1 \\ 3 \end{pmatrix}\), then \(\mathbf{a} - \mathbf{b}\) =", "opts":["A  (3, -5)","B  (5, 1)","C  (5, -1)","D  (-3, 5)"], "ans":"A", "sol": "Subtract tops: 4−1=3. Subtract bottoms: −2−3=−5. Answer: <strong>A</strong>", "hint":"Subtract components: 4-1=3, -2-3=-5."},
    {"q": r"The length of the vector \(\begin{pmatrix} 0 \\ 5 \end{pmatrix}\) is:", "opts":["A  5","B  0","C  25","D  1"], "ans":"A", "sol": r"√(0²+5²) = √25 = <strong>5</strong>. Answer: A", "hint":r"√(0²+5²) = 5 — only the vertical component contributes."},
    {"q": "Which of these columns is a unit vector?", "opts":["A  (1,0)","B  (2,2)","C  (0,0)","D  (1,1)"], "ans":"A", "sol": r"|(1,0)| = √(1²+0²) = 1. |(2,2)| = √8 ≠ 1. Answer: <strong>A</strong>", "hint":"A unit vector has magnitude 1. Check with Pythagoras: √(1²+0²) = 1."},
]
_VECTORS_MCQ_BANK = normalize_mcq_bank(_VECTORS_MCQ_RAW)


def vectors_mcq():
    chosen = random.choice(_VECTORS_MCQ_BANK)
    q = chosen["q"]
    options = chosen["opts"]
    correct = chosen["ans"]
    s = f"Answer: {correct}\n\n{chosen['hint']}"
    hint = chosen["hint"]
    return q, s, hint, 1, options, correct

# ---------- VARIANTS & MAIN GENERATOR ----------
def gcse_vectors_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _VECTORS_MCQ_BANK, procedural_mcq_for('vectors'), 'vectors', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _vectors_found_column_meaning,
            _vectors_found_magnitude_3_4,
            _vectors_found_magnitude_6_8,
            _vectors_found_add_simple,
            _vectors_found_subtract_simple,
            _vectors_found_scalar_multiply,
            _vectors_found_parallel_check,
            _vectors_found_zero_vector,
            _vectors_found_magnitude_zero,
            _vectors_found_negative_vector,
            _vectors_found_position_vector,
            _vectors_found_displacement,
            _vectors_found_equal_vectors,
            _vectors_found_inverse,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _vectors_inter_magnitude_advanced,
            _vectors_inter_parallel_k,
            _vectors_inter_collinear_points,
            _vectors_inter_path_addition,
            _vectors_inter_magnitude_distance,
            _vectors_inter_ratio_point,
            _vectors_inter_parallel_unknown,
            _vectors_inter_magnitude_comparison,
            _vectors_inter_vector_equation,
            _vectors_inter_magnitude_distance,
            _vectors_inter_position_geometry,
            _vectors_inter_midpoint_vector,
            _vectors_inter_translation,
            _vectors_inter_vector_path,
        ]
    elif difficulty == 'difficult':
        pool = [
            _vectors_diff_geometry_proof,
            _vectors_diff_ratio_theorem,
            _vectors_diff_collinear_proof,
            _vectors_diff_triangle_midpoint,
            _vectors_diff_trapezium_ratio,
            _vectors_diff_vector_inequality,
            _vectors_diff_parallelogram_area,
            _vectors_diff_unknown_parallel,
            _vectors_diff_geometry_parallelogram,
            _vectors_diff_vector_method_simultaneous,
            _vectors_diff_ratio_collinear,
            _vectors_diff_vector_proof_sim,
            _vectors_diff_parallel_unit,
            _vectors_diff_geometric_ratio,
        ]
    else:   # mixed – blend of all, 4 found + 4 inter + 2 diff
        found = random.sample([
            _vectors_found_column_meaning,
            _vectors_found_magnitude_3_4,
            _vectors_found_magnitude_6_8,
            _vectors_found_add_simple,
            _vectors_found_subtract_simple,
            _vectors_found_scalar_multiply,
            _vectors_found_parallel_check,
            _vectors_found_zero_vector,
            _vectors_found_magnitude_zero,
            _vectors_found_negative_vector,
            _vectors_found_position_vector,
            _vectors_found_displacement,
            _vectors_found_equal_vectors,
            _vectors_found_inverse,
        ], 4)
        inter = random.sample([
            _vectors_inter_magnitude_advanced,
            _vectors_inter_parallel_k,
            _vectors_inter_collinear_points,
            _vectors_inter_path_addition,
            _vectors_inter_magnitude_distance,
            _vectors_inter_ratio_point,
            _vectors_inter_parallel_unknown,
            _vectors_inter_magnitude_comparison,
            _vectors_inter_vector_equation,
            _vectors_inter_magnitude_distance,
            _vectors_inter_position_geometry,
            _vectors_inter_midpoint_vector,
            _vectors_inter_translation,
            _vectors_inter_vector_path,
        ], 4)
        diff = random.sample([
            _vectors_diff_geometry_proof,
            _vectors_diff_ratio_theorem,
            _vectors_diff_collinear_proof,
            _vectors_diff_triangle_midpoint,
            _vectors_diff_trapezium_ratio,
            _vectors_diff_vector_inequality,
            _vectors_diff_parallelogram_area,
            _vectors_diff_unknown_parallel,
            _vectors_diff_geometry_parallelogram,
            _vectors_diff_vector_method_simultaneous,
            _vectors_diff_ratio_collinear,
            _vectors_diff_vector_proof_sim,
            _vectors_diff_parallel_unit,
            _vectors_diff_geometric_ratio,
        ], 2)
        return found + inter + diff

    return select_tier_variants(pool)


def gcse_vectors(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_vectors_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
                            'gcse', 'maths', 'vectors',
                            options=opts_mcq, correct_answer=correct_mcq)
    variants = gcse_vectors_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _vec_problem_from_output(variant(), difficulty)


# ------------------------------------------------------------
# GCSE Maths – Trigonometry (10 / 10 / 10 + 15 MCQs)
# ------------------------------------------------------------
import random
import math
from generators.shared.utils import make_problem


# ===== SVG DIAGRAM HELPERS =====

_TRIG_DIAGRAM_W = 340
_TRIG_DIAGRAM_H = 220
_TRIG_SVG_PAD = 20


def _trig_diagram_shell_open(viewbox):
    """Fixed-size frame for every trigonometry question diagram."""
    return (
        f'<div style="text-align:center;margin:10px auto 14px;max-width:{_TRIG_DIAGRAM_W}px;">'
        f'<svg class="trig-diagram" width="{_TRIG_DIAGRAM_W}" height="{_TRIG_DIAGRAM_H}" '
        f'viewBox="{viewbox}" preserveAspectRatio="xMidYMid meet" '
        f'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;'
        f'width:100%;max-width:{_TRIG_DIAGRAM_W}px;height:{_TRIG_DIAGRAM_H}px;">'
    )


def _trig_svg_open(w, h, pad=_TRIG_SVG_PAD):
    vb_w, vb_h = w + 2 * pad, h + 2 * pad
    return _trig_diagram_shell_open(f"{-pad} {-pad} {vb_w} {vb_h}")


def _trig_svg_open_bounded(vx, vy, vw, vh):
    return _trig_diagram_shell_open(f"{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}")


def _trig_svg_right_tri(adj, opp,
                         label_adj="adj", label_opp="opp", label_hyp="hyp",
                         angle_label="\u03b8", angle_val=None):
    """Right-angled triangle SVG.
    \u03b8 at bottom-left, right angle at bottom-right, third vertex top-right.
    adj = horizontal base, opp = vertical side.
    Pass actual lengths for proportional drawing; labels are the text shown.
    """
    W, H = _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H
    margin = 40
    sc = min((W - 2 * margin) / max(adj, 1), (H - 2 * margin) / max(opp, 1), 180 / max(adj, opp, 1))
    ap, op = adj * sc, opp * sc
    # Vertices
    Ax, Ay = margin + 8, H - margin         # bottom-left: angle \u03b8
    Bx, By = Ax + ap, Ay        # bottom-right: right angle
    Cx, Cy = Bx, Ay - op        # top-right

    # Right-angle square at B
    sq = 10
    ra = (f'<polyline points="{Bx:.0f},{By-sq:.0f} {Bx-sq:.0f},{By-sq:.0f} {Bx-sq:.0f},{By:.0f}"'
          f' fill="none" stroke="#555" stroke-width="1.5"/>')

    # Angle arc at A
    hyp_ang = math.atan2(op, ap)
    r = 28
    ex = Ax + r * math.cos(hyp_ang)
    ey = Ay - r * math.sin(hyp_ang)
    arc = (f'<path d="M {Ax+r:.0f},{Ay:.0f} A {r},{r} 0 0,0 {ex:.0f},{ey:.0f}"'
           f' fill="none" stroke="#a13544" stroke-width="1.5"/>')

    mid = hyp_ang / 2
    lx = Ax + (r + 16) * math.cos(mid)
    ly = Ay - (r + 16) * math.sin(mid)
    ang_text = angle_label if angle_val is None else f"{angle_label} = {angle_val}\u00b0"
    ang_lbl = (f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle"'
               f' font-size="13" font-style="italic" fill="#a13544">{ang_text}</text>')

    # Side labels
    adj_lbl = (f'<text x="{(Ax+Bx)/2:.0f}" y="{Ay+18:.0f}" text-anchor="middle"'
               f' font-size="12" fill="#333">{label_adj}</text>')
    opp_lbl = (f'<text x="{Bx+16:.0f}" y="{(By+Cy)/2:.0f}" text-anchor="start"'
               f' font-size="12" fill="#333">{label_opp}</text>')
    hmx = (Ax + Cx) / 2 - 16 * math.sin(hyp_ang)
    hmy = (Ay + Cy) / 2 - 10
    hyp_lbl = (f'<text x="{hmx:.0f}" y="{hmy:.0f}" text-anchor="middle"'
               f' font-size="12" fill="#333">{label_hyp}</text>')

    return (f'{_trig_svg_open(W, H)}'
            f'<polygon points="{Ax:.0f},{Ay:.0f} {Bx:.0f},{By:.0f} {Cx:.0f},{Cy:.0f}"'
            f' fill="#e8f4f4" stroke="#01696f" stroke-width="2"/>'
            f'{ra}{arc}{ang_lbl}{adj_lbl}{opp_lbl}{hyp_lbl}'
            f'</svg></div>')


def _trig_svg_isosceles(equal, base,
                        label_equal=None, label_base=None,
                        angle_label="\u03b8"):
    """Isosceles triangle with apex at top, equal sides and base labelled."""
    if label_equal is None:
        label_equal = f"{equal} cm"
    if label_base is None:
        label_base = f"{base} cm"

    half = base / 2
    height = math.sqrt(max(0.0, equal ** 2 - half ** 2))
    pts = [(0.0, 0.0), (base, 0.0), (half, -height)]
    (Ax, Ay), (Bx, By), (Cx, Cy) = _trig_fit_triangle_to_canvas(
        pts, _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H, margin=40, label_pad=32)

    tri = (f'<polygon points="{Ax:.0f},{Ay:.0f} {Bx:.0f},{By:.0f} {Cx:.0f},{Cy:.0f}"'
           f' fill="#e8f4f4" stroke="#01696f" stroke-width="2"/>')

    ang_a = math.atan2(Ay - Cy, Ax - Cx)
    ang_b = math.atan2(By - Cy, Bx - Cx)
    r = 24
    x1 = Cx + r * math.cos(ang_a)
    y1 = Cy + r * math.sin(ang_a)
    x2 = Cx + r * math.cos(ang_b)
    y2 = Cy + r * math.sin(ang_b)
    sweep = 1 if (ang_b - ang_a) % (2 * math.pi) < math.pi else 0
    arc = (f'<path d="M {x1:.0f},{y1:.0f} A {r},{r} 0 0,{sweep} {x2:.0f},{y2:.0f}"'
           f' fill="none" stroke="#a13544" stroke-width="1.5"/>')

    mid = ang_a + ((ang_b - ang_a + math.pi) % (2 * math.pi) - math.pi) / 2
    lx = Cx + (r + 16) * math.cos(mid)
    ly = Cy + (r + 16) * math.sin(mid)
    ang_lbl = (f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle"'
               f' font-size="13" font-style="italic" fill="#a13544">{angle_label} = ?</text>')

    def _side_lbl(p1, p2, opp, text):
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ex, ey = p2[0] - p1[0], p2[1] - p1[1]
        nx, ny = -ey, ex
        n = math.hypot(nx, ny) or 1.0
        nx, ny = nx / n, ny / n
        if (opp[0] - mx) * nx + (opp[1] - my) * ny > 0:
            nx, ny = -nx, -ny
        tx, ty = mx + nx * 18, my + ny * 18 + 4
        return (f'<text x="{tx:.0f}" y="{ty:.0f}" text-anchor="middle"'
                f' font-size="12" fill="#333">{text}</text>'), tx, ty

    leq_a, ax1, ay1 = _side_lbl((Ax, Ay), (Cx, Cy), (Bx, By), label_equal)
    leq_b, ax2, ay2 = _side_lbl((Bx, By), (Cx, Cy), (Ax, Ay), label_equal)
    lbase, bx, by = _side_lbl((Ax, Ay), (Bx, By), (Cx, Cy), label_base)

    all_x = [Ax, Bx, Cx, x1, x2, lx, ax1, ax2, bx]
    all_y = [Ay, By, Cy, y1, y2, ly, ay1, ay2, by]
    vx, vy, vw, vh = _trig_diagram_viewbox_from_coords(all_x, all_y)
    return (
        f'{_trig_svg_open_bounded(vx, vy, vw, vh)}'
        f'{tri}{arc}{ang_lbl}{leq_a}{leq_b}{lbase}'
        f'</svg></div>'
    )


def _trig_triangle_unit_coords(A_deg, B_deg, C_deg):
    """A bottom-left, B bottom-right, C above AB (unit side c = AB)."""
    Ar, Br, Cr = math.radians(A_deg), math.radians(B_deg), math.radians(C_deg)
    c_len = 1.0
    b_len = c_len * math.sin(Br) / math.sin(Cr)
    Ax, Ay = 0.0, 0.0
    Bx, By = c_len, 0.0
    Cx = b_len * math.cos(Ar)
    Cy = -abs(b_len * math.sin(Ar))
    return (Ax, Ay), (Bx, By), (Cx, Cy)


def _trig_triangle_coords_ssa(side_a, side_b, B_deg):
    """Layout from side a (opposite A), side b (opposite B), and angle B."""
    Br = math.radians(B_deg)
    a, b = float(side_a), float(side_b)
    cosB = math.cos(Br)
    disc = (a * cosB) ** 2 - (a * a - b * b)
    if disc < 0:
        c = max(a, b) * 1.15
    else:
        c = a * cosB + math.sqrt(disc)
        if c <= 0:
            c = a * cosB - math.sqrt(disc)
        if c <= 0:
            c = max(a, b) * 1.15
    Ax, Ay = 0.0, 0.0
    Bx, By = c, 0.0
    Cx = (b * b + c * c - a * a) / (2 * c)
    Cy = -math.sqrt(max(0.0, b * b - Cx * Cx))
    if Cy == 0:
        Cy = -0.35 * max(a, b, c)
    return (Ax, Ay), (Bx, By), (Cx, Cy)


def _trig_fit_triangle_to_canvas(pts, W, H, margin=48, label_pad=36, flat_threshold=0.32):
    """Scale and translate triangle vertices to fit the canvas (always stays inside bounds)."""
    coords = list(pts)
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    bw = max(max_x - min_x, 1e-6)
    bh = max(max_y - min_y, 1e-6)
    inner_w = W - 2 * margin
    inner_h = H - 2 * margin - label_pad
    sc = min(inner_w / bw * 0.92, inner_h / bh * 0.88)
    tw, th = bw * sc, bh * sc
    off_x = margin + (inner_w - tw) / 2 - min_x * sc
    off_y = margin + label_pad / 2 + (inner_h - th) / 2 - min_y * sc

    def tr(x, y):
        return x * sc + off_x, y * sc + off_y

    return tuple(tr(x, y) for x, y in coords)


def _trig_diagram_viewbox_from_coords(all_x, all_y, pad=16):
    """Tight viewBox from every x/y used in the diagram."""
    vx = min(all_x) - pad
    vy = min(all_y) - pad
    vw = max(all_x) - min(all_x) + 2 * pad
    vh = max(all_y) - min(all_y) + 2 * pad
    return vx, vy, vw, vh


def _trig_triangle_bearing_coords(d1, d2, bearing1_deg, turn_angle_deg):
    """Start A, Turn C, End B using first-leg bearing and included turn angle."""
    b1 = math.radians(bearing1_deg)
    t = math.radians(turn_angle_deg)
    Ax, Ay = 0.0, 0.0
    Cx = d1 * math.sin(b1)
    Cy = -d1 * math.cos(b1)
    b2 = b1 + math.pi - t
    Bx = Cx + d2 * math.sin(b2)
    By = Cy - d2 * math.cos(b2)
    return (Ax, Ay), (Bx, By), (Cx, Cy)


def _trig_outward_side_label(p1, p2, opp, text, dist=18, fill="#333", size=13):
    """Place an italic side label perpendicular to edge p1-p2, on the far side from the
    opposite vertex `opp`, so it never sits on the triangle's lines (robust for slivers).
    Returns (svg, x_bounds, y_bounds)."""
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    ex, ey = p2[0] - p1[0], p2[1] - p1[1]
    nx, ny = -ey, ex
    n = math.hypot(nx, ny) or 1.0
    nx, ny = nx / n, ny / n
    if (opp[0] - mx) * nx + (opp[1] - my) * ny > 0:
        nx, ny = -nx, -ny
    lx = mx + nx * dist
    ly = my + ny * dist + 4
    svg = (f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle"'
           f' font-size="{size}" font-style="italic" fill="{fill}">{text}</text>')
    half_w = 3 * len(str(text)) + 6
    return svg, [lx - half_w, lx + half_w], [ly - size, ly + 4]


def _trig_outward_vertex_label(vx, vy, gx, gy, text, dist=16, fill="#01696f", size=13):
    """Place a bold vertex label outside the triangle, away from centroid (gx, gy)."""
    dx, dy = vx - gx, vy - gy
    n = math.hypot(dx, dy) or 1.0
    lx = vx + dx / n * dist
    ly = vy + dy / n * dist + 4
    svg = (f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle"'
           f' font-size="{size}" font-weight="bold" fill="{fill}">{text}</text>')
    half_w = 4 * len(str(text)) + 6
    return svg, [lx - half_w, lx + half_w], [ly - size, ly + 4]


def _trig_svg_bearing_triangle(d1, d2, bearing1_deg, turn_angle_deg,
                               label_a, label_b, label_c,
                               mark_A="Start", mark_B="End", mark_C="Turn"):
    """Bearing journey triangle — uses real leg bearings so obtuse turns stay legible."""
    pts = _trig_triangle_bearing_coords(d1, d2, bearing1_deg, turn_angle_deg)
    (Ax, Ay), (Bx, By), (Cx, Cy) = _trig_fit_triangle_to_canvas(
        pts, _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H, margin=32, label_pad=28)

    tri = (f'<polygon points="{Ax:.0f},{Ay:.0f} {Bx:.0f},{By:.0f} {Cx:.0f},{Cy:.0f}"'
           f' fill="#e8f4f4" stroke="#01696f" stroke-width="2"/>')

    Gx, Gy = (Ax + Bx + Cx) / 3, (Ay + By + Cy) / 3
    lA, ax_v, ay_v = _trig_outward_vertex_label(Ax, Ay, Gx, Gy, mark_A)
    lB, bx_v, by_v = _trig_outward_vertex_label(Bx, By, Gx, Gy, mark_B)
    lC, cx_v, cy_v = _trig_outward_vertex_label(Cx, Cy, Gx, Gy, mark_C)

    lsa, ax_s, ay_s = _trig_outward_side_label((Bx, By), (Cx, Cy), (Ax, Ay), label_a)
    lsb, bx_s, by_s = _trig_outward_side_label((Ax, Ay), (Cx, Cy), (Bx, By), label_b)
    lsc, cx_s, cy_s = _trig_outward_side_label((Ax, Ay), (Bx, By), (Cx, Cy), label_c)

    all_x = [Ax, Bx, Cx, *ax_v, *bx_v, *cx_v, *ax_s, *bx_s, *cx_s]
    all_y = [Ay, By, Cy, *ay_v, *by_v, *cy_v, *ay_s, *by_s, *cy_s]
    vx, vy, vw, vh = _trig_diagram_viewbox_from_coords(all_x, all_y)
    return (
        f'{_trig_svg_open_bounded(vx, vy, vw, vh)}'
        f'{tri}{lA}{lB}{lC}{lsa}{lsb}{lsc}'
        f'</svg></div>'
    )


def _trig_svg_general_tri(A_deg, B_deg,
                           label_a="a", label_b="b", label_c="c",
                           mark_A="A", mark_B="B", mark_C="C",
                           side_a=None, side_b=None):
    """General (non-right) triangle: A at bottom-left, B at bottom-right, C at top."""
    C_deg = 180 - A_deg - B_deg
    if C_deg >= 1 and A_deg >= 1:
        pts = _trig_triangle_unit_coords(A_deg, B_deg, C_deg)
    elif side_a is not None and side_b is not None:
        pts = _trig_triangle_coords_ssa(side_a, side_b, B_deg)
    else:
        pts = _trig_triangle_unit_coords(max(A_deg, 5), B_deg, max(C_deg, 5))

    (Ax, Ay), (Bx, By), (Cx, Cy) = _trig_fit_triangle_to_canvas(
        pts, _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H, margin=32, label_pad=28)

    tri = (f'<polygon points="{Ax:.0f},{Ay:.0f} {Bx:.0f},{By:.0f} {Cx:.0f},{Cy:.0f}"'
           f' fill="#e8f4f4" stroke="#01696f" stroke-width="2"/>')

    Gx, Gy = (Ax + Bx + Cx) / 3, (Ay + By + Cy) / 3
    lA, ax_v, ay_v = _trig_outward_vertex_label(Ax, Ay, Gx, Gy, mark_A)
    lB, bx_v, by_v = _trig_outward_vertex_label(Bx, By, Gx, Gy, mark_B)
    lC, cx_v, cy_v = _trig_outward_vertex_label(Cx, Cy, Gx, Gy, mark_C)

    lsa, ax_s, ay_s = _trig_outward_side_label((Bx, By), (Cx, Cy), (Ax, Ay), label_a)
    lsb, bx_s, by_s = _trig_outward_side_label((Ax, Ay), (Cx, Cy), (Bx, By), label_b)
    lsc, cx_s, cy_s = _trig_outward_side_label((Ax, Ay), (Bx, By), (Cx, Cy), label_c)

    all_x = [Ax, Bx, Cx, *ax_v, *bx_v, *cx_v, *ax_s, *bx_s, *cx_s]
    all_y = [Ay, By, Cy, *ay_v, *by_v, *cy_v, *ay_s, *by_s, *cy_s]
    vx, vy, vw, vh = _trig_diagram_viewbox_from_coords(all_x, all_y)
    return (
        f'{_trig_svg_open_bounded(vx, vy, vw, vh)}'
        f'{tri}{lA}{lB}{lC}{lsa}{lsb}{lsc}'
        f'</svg></div>'
    )


def _trig_svg_ladder(length, angle_deg, height):
    """Ladder leaning against a vertical wall."""
    W, H = _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H
    gy = H - 38
    wy1 = 22
    gx1 = 28
    wall_x = W - 44
    foot_y = gy

    ang_r = math.radians(angle_deg)
    cos_a = math.cos(ang_r)
    sin_a = math.sin(ang_r)

    max_adj = wall_x - gx1 - 24
    max_opp = foot_y - wy1 - 12
    scale_by_adj = max_adj / (length * cos_a) if cos_a > 1e-6 else max_adj
    scale_by_opp = max_opp / (length * sin_a) if sin_a > 1e-6 else max_opp
    scale = min(scale_by_adj, scale_by_opp) * 0.92

    adj_px = length * cos_a * scale
    opp_px = length * sin_a * scale
    foot_x = wall_x - adj_px
    wall_y = foot_y - opp_px

    sq = 10
    ra = (f'<polyline points="{wall_x},{foot_y-sq} {wall_x-sq},{foot_y-sq} {wall_x-sq},{foot_y}"'
          f' fill="none" stroke="#555" stroke-width="1.5"/>')

    r = min(28, max(16, min(adj_px, opp_px) * 0.28))
    ex = foot_x + r * cos_a
    ey = foot_y - r * sin_a
    arc = (f'<path d="M {foot_x+r:.1f},{foot_y} A {r},{r} 0 0,0 {ex:.1f},{ey:.1f}"'
           f' fill="none" stroke="#a13544" stroke-width="1.5"/>')

    lx = foot_x + (r + 14) * math.cos(ang_r / 2)
    ly = foot_y - (r + 14) * math.sin(ang_r / 2)
    mid_x = (foot_x + wall_x) / 2 - sin_a * 10
    mid_y = (foot_y + wall_y) / 2 - cos_a * 10

    return (f'{_trig_svg_open(W, H)}'
            f'<line x1="{gx1}" y1="{gy}" x2="{wall_x}" y2="{gy}" stroke="#555" stroke-width="2"/>'
            f'<line x1="{wall_x}" y1="{wy1}" x2="{wall_x}" y2="{gy}" stroke="#555" stroke-width="2"/>'
            f'<line x1="{foot_x:.1f}" y1="{foot_y}" x2="{wall_x}" y2="{wall_y:.1f}"'
            f' stroke="#01696f" stroke-width="3"/>'
            f'{ra}{arc}'
            f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="12" fill="#a13544">{angle_deg}\u00b0</text>'
            f'<text x="{mid_x:.0f}" y="{mid_y:.0f}" text-anchor="middle" font-size="12" fill="#333">{length} m</text>'
            f'<text x="{wall_x+12}" y="{(wall_y+foot_y)//2}" text-anchor="start" font-size="12" fill="#333">? m</text>'
            f'<text x="{gx1}" y="{gy+18}" font-size="11" fill="#888">ground</text>'
            f'<text x="{wall_x-4}" y="{wy1-4}" font-size="11" fill="#888" text-anchor="end">wall</text>'
            f'</svg></div>')


def _trig_svg_elevation(height, dist, angle_deg=None):
    """Angle of elevation from observer to top of building.
    Pass angle_deg only when the angle is given in the question (not the unknown).
    """
    W, H = _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H
    obs_x, obs_y = 44, H - 42
    base_x, base_y = W - 50, H - 42
    top_x, top_y = base_x, 38

    sq = 10
    ra = (f'<polyline points="{base_x},{base_y-sq} {base_x-sq},{base_y-sq} {base_x-sq},{base_y}"'
          f' fill="none" stroke="#555" stroke-width="1.5"/>')

    # Use a typical arc position for drawing; label only if angle is known
    draw_ang = angle_deg if angle_deg is not None else round(
        math.degrees(math.atan(height / dist)), 1)
    ang_r = math.radians(draw_ang)
    r = 32
    ex = obs_x + r * math.cos(ang_r)
    ey = obs_y - r * math.sin(ang_r)
    arc = (f'<path d="M {obs_x+r},{obs_y} A {r},{r} 0 0,0 {ex:.0f},{ey:.0f}"'
           f' fill="none" stroke="#a13544" stroke-width="1.5"/>')
    lx = obs_x + (r + 18) * math.cos(ang_r / 2)
    ly = obs_y - (r + 18) * math.sin(ang_r / 2)
    ang_lbl = (f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="12" fill="#a13544">'
               f'{angle_deg}\u00b0</text>' if angle_deg is not None else
               f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="12" font-style="italic" fill="#a13544">\u03b8?</text>')

    return (f'{_trig_svg_open(W, H)}'
            f'<line x1="{obs_x}" y1="{obs_y}" x2="{base_x}" y2="{base_y}" stroke="#555" stroke-width="2"/>'
            f'<line x1="{base_x}" y1="{base_y}" x2="{top_x}" y2="{top_y}" stroke="#01696f" stroke-width="3"/>'
            f'<line x1="{obs_x}" y1="{obs_y}" x2="{top_x}" y2="{top_y}" stroke="#01696f" stroke-width="2" stroke-dasharray="6,4"/>'
            f'{ra}{arc}{ang_lbl}'
            f'<text x="{(obs_x+base_x)//2}" y="{obs_y+18}" text-anchor="middle" font-size="12" fill="#333">{dist} m</text>'
            f'<text x="{top_x+16}" y="{(top_y+base_y)//2}" text-anchor="start" font-size="12" fill="#333">{height} m</text>'
            f'<circle cx="{obs_x}" cy="{obs_y}" r="4" fill="#a13544"/>'
            f'</svg></div>')


def _trig_svg_depression(height, dist, angle_deg=None):
    """Angle of depression from cliff top to object on ground.
    Pass angle_deg only when the angle is given (not the unknown).
    """
    W, H = _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H
    obs_x, obs_y = 44, 40
    base_x, base_y = W - 50, H - 42
    draw_ang = angle_deg if angle_deg is not None else round(
        math.degrees(math.atan(height / dist)), 1)
    ang_r = math.radians(draw_ang)
    r = 30
    ex = obs_x + r * math.cos(-ang_r)
    ey = obs_y - r * math.sin(-ang_r)
    arc = (f'<path d="M {obs_x+r},{obs_y} A {r},{r} 0 0,1 {ex:.0f},{ey:.0f}"'
           f' fill="none" stroke="#a13544" stroke-width="1.5"/>')
    lx = obs_x + (r + 18) * math.cos(-ang_r / 2)
    ly = obs_y - (r + 18) * math.sin(-ang_r / 2)
    ang_lbl = (f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="12" fill="#a13544">'
               f'{angle_deg}\u00b0</text>' if angle_deg is not None else
               f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="12" font-style="italic" fill="#a13544">\u03b8?</text>')

    return (f'{_trig_svg_open(W, H)}'
            f'<line x1="{obs_x}" y1="{obs_y}" x2="{obs_x}" y2="{base_y}" stroke="#aaa" stroke-width="1" stroke-dasharray="4,4"/>'
            f'<line x1="{obs_x}" y1="{base_y}" x2="{base_x}" y2="{base_y}" stroke="#555" stroke-width="2"/>'
            f'<line x1="{obs_x}" y1="{obs_y}" x2="{base_x}" y2="{base_y}" stroke="#01696f" stroke-width="2" stroke-dasharray="6,4"/>'
            f'{arc}{ang_lbl}'
            f'<text x="{(obs_x+base_x)//2}" y="{base_y+18}" text-anchor="middle" font-size="12" fill="#333">{dist} m</text>'
            f'<text x="{obs_x-8}" y="{(obs_y+base_y)//2}" text-anchor="end" font-size="12" fill="#333">{height} m</text>'
            f'<circle cx="{obs_x}" cy="{obs_y}" r="4" fill="#a13544"/>'
            f'<circle cx="{base_x}" cy="{base_y}" r="4" fill="#01696f"/>'
            f'<text x="{obs_x+8}" y="{obs_y-6}" font-size="11" fill="#888">observer</text>'
            f'<text x="{base_x+5}" y="{base_y+4}" font-size="11" fill="#888">object</text>'
            f'</svg></div>')


def _trig_svg_bearing(north_km, east_km, dist=None):
    """North then East journey forming a right triangle.
    Pass dist only when the direct distance is given (not the unknown).
    """
    W, H = _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H
    start_x, start_y = 52, H - 42
    north_x, north_y = 52, 42
    end_x, end_y = W - 38, 42

    sq = 10
    ra = (f'<polyline points="{north_x},{north_y+sq} {north_x+sq},{north_y+sq} {north_x+sq},{north_y}"'
          f' fill="none" stroke="#555" stroke-width="1.5"/>')

    return (f'{_trig_svg_open(W, H)}'
            f'<line x1="{start_x}" y1="{start_y}" x2="{north_x}" y2="{north_y}" stroke="#01696f" stroke-width="2.5"/>'
            f'<line x1="{north_x}" y1="{north_y}" x2="{end_x}" y2="{end_y}" stroke="#01696f" stroke-width="2.5"/>'
            f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" stroke="#a13544" stroke-width="2" stroke-dasharray="6,4"/>'
            f'{ra}'
            f'<circle cx="{start_x}" cy="{start_y}" r="4" fill="#333"/>'
            f'<circle cx="{end_x}" cy="{end_y}" r="4" fill="#01696f"/>'
            f'<text x="{north_x-14}" y="{(start_y+north_y)//2}" text-anchor="end" font-size="12" fill="#333">{north_km} km N</text>'
            f'<text x="{(north_x+end_x)//2}" y="{north_y-10}" text-anchor="middle" font-size="12" fill="#333">{east_km} km E</text>'
            f'<text x="{(start_x+end_x)//2+12}" y="{(start_y+end_y)//2}" text-anchor="start" font-size="12" fill="#a13544">'
            f'{"? km" if dist is None else f"{dist} km"}</text>'
            f'<text x="{start_x-5}" y="{start_y+14}" font-size="11" fill="#888" text-anchor="end">Start</text>'
            f'<text x="{end_x+5}" y="{end_y+5}" font-size="11" fill="#888">Finish</text>'
            f'<text x="{north_x}" y="{start_y+5}" font-size="20" fill="#888" text-anchor="middle">\u2191N</text>'
            f'</svg></div>')


def _trig_raw(val):
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    if isinstance(val, int):
        return str(val)
    return str(val)


def _trig_keyword(value):
    return {'type': 'keyword', 'value': str(value).strip().lower()}


def _trig_surd(coeff, radicand):
    return {'type': 'surd', 'coeff': coeff, 'radicand': radicand}


def _trig_surd_over_int(coef, radicand, denom):
    return {
        'type': 'algebraic_fraction',
        'kind': 'surd_over_int',
        'coef': coef,
        'radicand': radicand,
        'denom': denom,
    }


def _trig_exact_from_text(text_ans):
    mapping = {
        '1/2': '1/2',
        '1': 1,
        '\u221a2/2': _trig_surd_over_int(1, 2, 2),
        '\u221a3/2': _trig_surd_over_int(1, 3, 2),
        '\u221a3': _trig_surd(1, 3),
        '1/\u221a3 = \u221a3/3': _trig_surd_over_int(1, 3, 3),
    }
    return mapping[text_ans]


def _trig_exact_compound_answer(ans):
    if ans in ('1', '0'):
        return int(ans)
    if ans == '3/2':
        return '3/2'
    if ans in ('\u221a3/2',):
        return _trig_surd_over_int(1, 3, 2)
    return ans


def _trig_number_fields_answer(values, labels, field_types=None):
    types = tuple(field_types) if field_types else tuple('number' for _ in values)
    return {
        'type': 'number_fields',
        'values': tuple(str(v) for v in values),
        'labels': tuple(labels),
        'field_types': types,
    }


def _trig_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'keyword':
                value = raw.get('value')
                if value is not None and str(value).strip():
                    extra = {
                        'correct_answer_raw': str(value).strip().lower(),
                        'answer_type': 'keyword',
                        'answer_format_hint': 'e.g. yes or no',
                    }
            elif raw_type == 'surd':
                coeff = int(raw.get('coeff') or 1)
                radicand = raw.get('radicand')
                if radicand is not None:
                    extra = {
                        'correct_answer_raw': (
                            str(radicand) if coeff == 1 else f'{coeff}|{radicand}'
                        ),
                        'answer_type': 'surd',
                        'answer_format_hint': 'e.g. √3 — use the √ button if needed',
                    }
            elif raw_type == 'algebraic_fraction' and raw.get('kind') == 'surd_over_int':
                coef = int(raw['coef'])
                rad = int(raw['radicand'])
                denom = int(raw['denom'])
                num_display = _surd_fmt(coef, rad)
                extra = {
                    'correct_answer_raw': f'{coef}|{rad}|{denom}',
                    'answer_type': 'algebraic_fraction',
                    'answer_format_hint': (
                        f'Numerator like {num_display}, denominator a whole number'
                    ),
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
                        'answer_format_hint': 'Complete every proof step',
                    }
        elif isinstance(raw, str) and '/' in raw:
            extra = {
                'correct_answer_raw': raw,
                'answer_type': 'fraction',
                'answer_format_hint': 'Enter an exact fraction (e.g. 1/2)',
            }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _trig_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'trigonometry', **extra
    )


# ===== FOUNDATIONAL (10) =====

def _trig_found_sin_side():
    angle = random.choice([30, 35, 40, 45, 50])
    hyp = random.randint(6, 20)
    opp = round(hyp * math.sin(math.radians(angle)), 2)
    svg = _trig_svg_right_tri(hyp, opp,
                               label_adj="", label_opp="?",
                               label_hyp=f"{hyp} cm",
                               angle_val=angle)
    q = (f"{svg}"
         f"In a right-angled triangle, the hypotenuse is {hyp} cm and one acute angle is {angle}\u00b0. "
         f"Use sin to find the length of the side <strong>opposite</strong> this angle. Give your answer to 2 d.p.")
    s = (rf"\(\sin {angle}° = \dfrac{{\text{{opp}}}}{{{hyp}}}\)"
         f"<br>opp = {hyp} \u00d7 sin {angle}\u00b0 = {hyp} \u00d7 {math.sin(math.radians(angle)):.4f}"
         f"<br>= <strong>{opp} cm</strong>")
    hint = "SOH: sin\u202f=\u202fopposite \u00f7 hypotenuse. Rearrange to opp = hyp \u00d7 sin\u202f\u03b8."
    return q, s, hint, 2, opp


def _trig_found_cos_side():
    angle = random.choice([30, 35, 40, 45, 50])
    hyp = random.randint(8, 18)
    adj = round(hyp * math.cos(math.radians(angle)), 2)
    svg = _trig_svg_right_tri(adj, hyp * math.sin(math.radians(angle)),
                               label_adj="?", label_opp="",
                               label_hyp=f"{hyp} m",
                               angle_val=angle)
    q = (f"{svg}"
         f"In a right-angled triangle, the hypotenuse is {hyp} m and one acute angle is {angle}\u00b0. "
         f"Use cos to find the length of the <strong>adjacent</strong> side. Give your answer to 2 d.p.")
    s = (rf"\(\cos {angle}° = \dfrac{{\text{{adj}}}}{{{hyp}}}\)"
         f"<br>adj = {hyp} \u00d7 cos {angle}\u00b0 = {hyp} \u00d7 {math.cos(math.radians(angle)):.4f}"
         f"<br>= <strong>{adj} m</strong>")
    hint = "CAH: cos\u202f=\u202fadjacent \u00f7 hypotenuse. Rearrange to adj = hyp \u00d7 cos\u202f\u03b8."
    return q, s, hint, 2, adj


def _trig_found_tan_angle():
    opp = random.randint(3, 10)
    adj = random.randint(3, 10)
    angle = round(math.degrees(math.atan(opp / adj)), 1)
    svg = _trig_svg_right_tri(adj, opp,
                               label_adj=f"{adj} cm", label_opp=f"{opp} cm",
                               label_hyp="",
                               angle_label="\u03b8 = ?")
    q = (f"{svg}"
         f"In a right-angled triangle, the opposite side is {opp} cm and the adjacent side is {adj} cm. "
         f"Use tan to find the acute angle \u03b8. Give your answer to 1 d.p.")
    s = (rf"\(\tan \theta = \dfrac{{{opp}}}{{{adj}}}\)"
         f"<br>\u03b8 = tan\u207b\u00b9\u202f({opp}/{adj})"
         f"<br>= <strong>{angle}\u00b0</strong>")
    hint = "TOA: tan\u202f=\u202fopposite \u00f7 adjacent. Use inverse tan (\u03b8 = tan\u207b\u00b9) to find the angle."
    return q, s, hint, 2, angle


def _trig_found_pythagoras():
    a = random.randint(3, 10)
    b = random.randint(3, 10)
    c = round(math.sqrt(a ** 2 + b ** 2), 2)
    svg = _trig_svg_right_tri(a, b,
                               label_adj=f"{a} cm", label_opp=f"{b} cm",
                               label_hyp="?",
                               angle_label="")
    q = (f"{svg}"
         f"The two shorter sides of a right-angled triangle are {a} cm and {b} cm. "
         f"Calculate the length of the hypotenuse, correct to 2 d.p.")
    s = (rf"\(c = \sqrt{{{a}^2 + {b}^2}} = \sqrt{{{a**2} + {b**2}}} = \sqrt{{{a**2 + b**2}}}\)"
         f"<br>= <strong>{c} cm</strong>")
    hint = "Pythagoras: c\u00b2 = a\u00b2 + b\u00b2. Square both legs, add, then take the square root."
    return q, s, hint, 2, c


def _trig_found_ladder():
    length = random.randint(4, 10)
    angle = random.choice([60, 65, 70])
    height = round(length * math.sin(math.radians(angle)), 2)
    svg = _trig_svg_ladder(length, angle, height)
    q = (f"{svg}"
         f"A ladder of length {length} m leans against a wall making an angle of {angle}\u00b0 with the ground. "
         f"How high up the wall does the ladder reach? Give your answer to 2 d.p.")
    s = (f"The ladder is the hypotenuse; the height is opposite the angle.<br>"
         rf"\(\sin {angle}° = \dfrac{{\text{{height}}}}{{{length}}}\)"
         f"<br>height = {length} \u00d7 sin {angle}\u00b0 = {length} \u00d7 {math.sin(math.radians(angle)):.4f}"
         f"<br>= <strong>{height} m</strong>")
    hint = "Draw the triangle: ladder = hyp, height = opp, ground = adj. Use SOH: sin = opp/hyp."
    return q, s, hint, 2, height


def _trig_found_find_hyp_from_opp():
    angle = random.choice([30, 35, 40, 45, 50])
    opp = random.randint(4, 12)
    hyp = round(opp / math.sin(math.radians(angle)), 2)
    adj = round(math.sqrt(hyp ** 2 - opp ** 2), 2)
    svg = _trig_svg_right_tri(adj, opp,
                               label_adj="", label_opp=f"{opp} cm",
                               label_hyp="?",
                               angle_val=angle)
    q = (f"{svg}"
         f"In a right-angled triangle, the side opposite a {angle}\u00b0 angle is {opp} cm. "
         f"Find the hypotenuse. Give your answer to 2 d.p.")
    s = (rf"\(\sin {angle}° = \dfrac{{{opp}}}{{\text{{hyp}}}}\)"
         f"<br>hyp = {opp} \u00f7 sin {angle}\u00b0 = {opp} \u00f7 {math.sin(math.radians(angle)):.4f}"
         f"<br>= <strong>{hyp} cm</strong>")
    hint = "SOH: sin = opp/hyp. Rearrange: hyp = opp \u00f7 sin\u202f\u03b8."
    return q, s, hint, 2, hyp


def _trig_found_find_adj_from_tan():
    angle = random.choice([30, 35, 40, 45, 55, 60])
    opp = random.randint(4, 14)
    adj = round(opp / math.tan(math.radians(angle)), 2)
    svg = _trig_svg_right_tri(adj, opp,
                               label_adj="?", label_opp=f"{opp} m",
                               label_hyp="",
                               angle_val=angle)
    q = (f"{svg}"
         f"In a right-angled triangle, the angle is {angle}\u00b0 and the opposite side is {opp} m. "
         f"Find the adjacent side. Give your answer to 2 d.p.")
    s = (rf"\(\tan {angle}° = \dfrac{{{opp}}}{{\text{{adj}}}}\)"
         f"<br>adj = {opp} \u00f7 tan {angle}\u00b0 = {opp} \u00f7 {math.tan(math.radians(angle)):.4f}"
         f"<br>= <strong>{adj} m</strong>")
    hint = "TOA: tan = opp/adj. Rearrange: adj = opp \u00f7 tan\u202f\u03b8."
    return q, s, hint, 2, adj


def _trig_found_pythagoras_leg():
    c = random.randint(8, 20)
    a = random.randint(3, c - 2)
    b = round(math.sqrt(c ** 2 - a ** 2), 2)
    svg = _trig_svg_right_tri(b, a,
                               label_adj="?", label_opp=f"{a} cm",
                               label_hyp=f"{c} cm",
                               angle_label="")
    q = (f"{svg}"
         f"A right-angled triangle has hypotenuse {c} cm and one shorter side {a} cm. "
         f"Calculate the length of the other shorter side. Give your answer to 2 d.p.")
    s = (rf"\(b = \sqrt{{c^2 - a^2}} = \sqrt{{{c}^2 - {a}^2}} = \sqrt{{{c**2 - a**2}}}\)"
         f"<br>= <strong>{b} cm</strong>")
    hint = "Rearrange Pythagoras: b\u00b2 = c\u00b2 \u2212 a\u00b2."
    return q, s, hint, 2, b


def _trig_found_cos_angle():
    adj = random.randint(4, 12)
    hyp = adj + random.randint(2, 8)
    angle = round(math.degrees(math.acos(adj / hyp)), 1)
    opp = round(math.sqrt(hyp ** 2 - adj ** 2), 2)
    svg = _trig_svg_right_tri(adj, opp,
                               label_adj=f"{adj} cm", label_opp="",
                               label_hyp=f"{hyp} cm",
                               angle_label="\u03b8 = ?")
    q = (f"{svg}"
         f"In a right-angled triangle, the adjacent side is {adj} cm and the hypotenuse is {hyp} cm. "
         f"Use cos to find the angle \u03b8. Give your answer to 1 d.p.")
    s = (rf"\(\cos \theta = \dfrac{{{adj}}}{{{hyp}}}\)"
         f"<br>\u03b8 = cos\u207b\u00b9\u202f({adj}/{hyp})"
         f"<br>= <strong>{angle}\u00b0</strong>")
    hint = "CAH: cos = adj/hyp. Use inverse cos to find the angle."
    return q, s, hint, 2, angle


def _trig_found_exact_values():
    choices = [
        (30, "sin", "\\frac{1}{2}", "1/2"),
        (60, "cos", "\\frac{1}{2}", "1/2"),
        (45, "sin", "\\frac{\\sqrt{2}}{2}", "\u221a2/2"),
        (45, "cos", "\\frac{\\sqrt{2}}{2}", "\u221a2/2"),
        (30, "cos", "\\frac{\\sqrt{3}}{2}", "\u221a3/2"),
        (60, "sin", "\\frac{\\sqrt{3}}{2}", "\u221a3/2"),
        (45, "tan", "1", "1"),
        (30, "tan", "\\frac{1}{\\sqrt{3}}", "1/\u221a3 = \u221a3/3"),
        (60, "tan", "\\sqrt{3}", "\u221a3"),
    ]
    ang, fn, latex_ans, text_ans = random.choice(choices)
    q = rf"Write down the <strong>exact</strong> value of \(\{fn} {ang}°\)."
    s = rf"\(\{fn} {ang}° = {latex_ans}\) &nbsp; (exact value: <strong>{text_ans}</strong>)"
    hint = "Learn the exact values for 30\u00b0, 45\u00b0, 60\u00b0 from the special triangles."
    return q, s, hint, 1, _trig_exact_from_text(text_ans)


# ===== INTERMEDIATE (10) =====

def _trig_inter_two_step():
    a = random.randint(5, 12)
    b = random.randint(3, 8)
    c = round(math.sqrt(a ** 2 + b ** 2), 2)
    short = min(a, b)
    angle = round(math.degrees(math.atan(short / max(a, b))), 1)
    svg = _trig_svg_right_tri(max(a, b), short,
                               label_adj=f"{max(a,b)} cm", label_opp=f"{short} cm",
                               label_hyp="?",
                               angle_label="\u03b8 = ?")
    q = (f"{svg}"
         f"A right-angled triangle has legs {a} cm and {b} cm. "
         f"Calculate the <strong>smallest</strong> acute angle in the triangle. Give your answer to 1 d.p.")
    s = (rf"Step 1 – Find hypotenuse: \(c = \sqrt{{{a}^2+{b}^2}} = {c}\) cm<br>"
         rf"Step 2 – Smallest angle is opposite shortest side ({short} cm):<br>"
         rf"\(\tan \theta = \dfrac{{{short}}}{{{max(a,b)}}}\) \(\Rightarrow\) "
         rf"\(\theta = \tan^{{-1}}\!\left(\dfrac{{{short}}}{{{max(a,b)}}}\right) = \) <strong>{angle}\u00b0</strong>")
    hint = "The smallest angle is opposite the shortest side. Use tan with the two legs."
    return q, s, hint, 3, angle


def _trig_inter_bearing():
    leg1 = random.randint(10, 20)
    leg2 = random.randint(8, 15)
    dist = round(math.sqrt(leg1 ** 2 + leg2 ** 2), 2)
    svg = _trig_svg_bearing(leg1, leg2)  # distance is unknown — do not label it on diagram
    q = (f"{svg}"
         f"A ship sails {leg1} km due North, then {leg2} km due East. "
         f"Calculate the direct distance from its starting point to its final position. Give your answer to 2 d.p.")
    s = (f"The north and east journeys form a right angle, so use Pythagoras:<br>"
         rf"\(d = \sqrt{{{leg1}^2 + {leg2}^2}} = \sqrt{{{leg1**2} + {leg2**2}}} = \sqrt{{{leg1**2+leg2**2}}}\)"
         f"<br>= <strong>{dist} km</strong>")
    hint = "The two legs (N and E) form a right angle. The direct distance is the hypotenuse."
    return q, s, hint, 3, dist


def _trig_inter_elevation():
    height = random.randint(15, 30)
    shadow = random.randint(8, 20)
    angle = round(math.degrees(math.atan(height / shadow)), 1)
    svg = _trig_svg_elevation(height, shadow)  # angle is unknown — do not label it on diagram
    q = (f"{svg}"
         f"A building is {height} m tall and casts a shadow {shadow} m long. "
         f"Find the angle of elevation of the sun. Give your answer to 1 d.p.")
    s = (f"The height is opposite the angle, the shadow is adjacent:<br>"
         rf"\(\tan \theta = \dfrac{{{height}}}{{{shadow}}}\)"
         f"<br>\u03b8 = tan\u207b\u00b9\u202f({height}/{shadow})"
         f"<br>= <strong>{angle}\u00b0</strong>")
    hint = "Angle of elevation: measure upward from horizontal. Use tan = opp/adj."
    return q, s, hint, 3, angle


def _trig_inter_isosceles():
    equal = random.randint(8, 15)
    base = random.randint(4, min(2 * equal - 2, 14))
    half_base = base / 2
    angle_half = round(math.degrees(math.asin(half_base / equal)), 1)
    apex = round(2 * angle_half, 1)
    svg = _trig_svg_isosceles(equal, base)
    q = (f"{svg}"
         f"An isosceles triangle has equal sides of {equal} cm and a base of {base} cm. "
         f"Find the apex angle (the angle between the two equal sides). Give your answer to 1 d.p.")
    s = (f"Drop a perpendicular from the apex to the midpoint of the base.<br>"
         f"This creates a right triangle with hypotenuse {equal} cm and opposite side {half_base} cm.<br>"
         rf"\(\sin(\theta/2) = \dfrac{{{half_base}}}{{{equal}}}\)"
         f"<br>\u03b8/2 = sin\u207b\u00b9\u202f({half_base}/{equal}) = {angle_half}\u00b0"
         f"<br>apex angle = 2 \u00d7 {angle_half}\u00b0 = <strong>{apex}\u00b0</strong>")
    hint = "Halve the base and use sin to find half the apex angle, then double it."
    return q, s, hint, 4, apex


def _trig_inter_exact_expression():
    q = (
        r"Using exact values, show that \(\sin^2 30° + \cos^2 30° = 1\) "
        r"by completing the proof steps below."
    )
    s = (
        r"<strong>Exact values:</strong> \(\sin 30° = \dfrac{1}{2}\), "
        r"\(\cos 30° = \dfrac{\sqrt{3}}{2}\).<br><br>"
        r"<strong>Step 1</strong> — \(\sin^2 30° = \left(\dfrac{1}{2}\right)^2 = \dfrac{1}{4}\)<br>"
        r"<strong>Step 2</strong> — \(\cos^2 30° = \left(\dfrac{\sqrt{3}}{2}\right)^2 = \dfrac{3}{4}\)<br>"
        r"<strong>Step 3</strong> — \(\dfrac{1}{4} + \dfrac{3}{4} = \dfrac{4}{4} = 1\) ✓"
    )
    hint = "Substitute the exact values and simplify each squared term."
    return q, s, hint, 2, _trig_number_fields_answer(
        ('1/4', '3/4', 1),
        (
            'Step 1: value of sin² 30°',
            'Step 2: value of cos² 30°',
            'Step 3: simplified LHS',
        ),
        ('fraction', 'fraction', 'number'),
    )


def _trig_inter_depression():
    height = random.randint(20, 60)
    dist = random.randint(15, 50)
    angle = round(math.degrees(math.atan(height / dist)), 1)
    svg = _trig_svg_depression(height, dist)  # angle is unknown — do not label it on diagram
    q = (f"{svg}"
         f"An observer at the top of a cliff of height {height} m looks down at an object {dist} m away "
         f"(measured horizontally). Find the angle of depression. Give your answer to 1 d.p.")
    s = (f"The height is opposite the angle, the horizontal distance is adjacent:<br>"
         rf"\(\tan \theta = \dfrac{{{height}}}{{{dist}}}\)"
         f"<br>\u03b8 = tan\u207b\u00b9\u202f({height}/{dist})"
         f"<br>= <strong>{angle}\u00b0</strong>")
    hint = "Angle of depression: measure downward from horizontal. tan = opp/adj."
    return q, s, hint, 3, angle


def _trig_inter_cosine_find_angle():
    a = random.randint(5, 12)
    b = random.randint(5, 12)
    c = random.randint(5, 12)
    # ensure valid triangle
    while a >= b + c or b >= a + c or c >= a + b:
        a, b, c = random.randint(5, 12), random.randint(5, 12), random.randint(5, 12)
    cosA = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
    cosA = max(-1, min(1, cosA))
    A = round(math.degrees(math.acos(cosA)), 1)
    A_deg_for_svg = int(A)
    B_deg_for_svg = random.randint(40, 80)
    while A_deg_for_svg + B_deg_for_svg >= 175:
        B_deg_for_svg -= 5
    svg = _trig_svg_general_tri(A_deg_for_svg, B_deg_for_svg,
                                 label_a=f"{a} cm", label_b=f"{b} cm", label_c=f"{c} cm",
                                 mark_A="A = ?")
    q = (f"{svg}"
         f"In triangle ABC, a = {a} cm, b = {b} cm, c = {c} cm. "
         f"Use the cosine rule to find angle A. Give your answer to 1 d.p.")
    s = (rf"\(\cos A = \dfrac{{b^2 + c^2 - a^2}}{{2bc}} = \dfrac{{{b}^2 + {c}^2 - {a}^2}}{{2 \times {b} \times {c}}}"
         rf" = \dfrac{{{b**2}+{c**2}-{a**2}}}{{{2*b*c}}} = {cosA:.4f}\)"
         f"<br>A = cos\u207b\u00b9\u202f({cosA:.4f})"
         f"<br>= <strong>{A}\u00b0</strong>")
    hint = "Rearranged cosine rule: cos A = (b\u00b2 + c\u00b2 \u2212 a\u00b2) / (2bc)."
    return q, s, hint, 4, A


def _trig_inter_converse_pyth():
    choices = [
        (3, 4, 5, True), (5, 12, 13, True), (8, 15, 17, True),
        (6, 8, 11, False), (7, 10, 14, False), (5, 9, 11, False),
    ]
    a, b, c, is_right = random.choice(choices)
    q = (f"A triangle has sides {a} cm, {b} cm, and {c} cm. "
         f"Determine whether this triangle is right-angled. Show your working.")
    if is_right:
        s = (f"Check if a\u00b2 + b\u00b2 = c\u00b2:<br>"
             f"{a}\u00b2 + {b}\u00b2 = {a**2} + {b**2} = {a**2+b**2}<br>"
             f"{c}\u00b2 = {c**2}<br>"
             f"Since {a**2+b**2} = {c**2}, the triangle <strong>is right-angled</strong>. \u2713")
    else:
        s = (f"Check if a\u00b2 + b\u00b2 = c\u00b2:<br>"
             f"{a}\u00b2 + {b}\u00b2 = {a**2} + {b**2} = {a**2+b**2}<br>"
             f"{c}\u00b2 = {c**2}<br>"
             f"Since {a**2+b**2} \u2260 {c**2}, the triangle is <strong>not right-angled</strong>. \u2717")
    hint = "Converse of Pythagoras: if a\u00b2 + b\u00b2 = c\u00b2, the triangle is right-angled."
    return q, s, hint, 2, _trig_keyword('yes' if is_right else 'no')


def _trig_inter_compound():
    base = random.randint(10, 20)
    h1 = random.randint(5, 12)
    angle2 = random.choice([30, 35, 40, 45, 50])
    h2 = round(base * math.tan(math.radians(angle2)), 2)
    total_h = h1 + h2
    q = (f"A flagpole stands on top of a {h1} m wall. From a point {base} m from the base of the wall "
         f"(on flat ground), the angle of elevation to the top of the flagpole is {angle2}\u00b0. "
         f"Find the total height of the flagpole and wall combined. Give your answer to 2 d.p.")
    s = (f"Let total height = h. The right triangle has:<br>"
         f"  opposite = h, adjacent = {base} m, angle = {angle2}\u00b0<br>"
         rf"\(\tan {angle2}° = \dfrac{{h}}{{{base}}}\)"
         f"<br>h = {base} \u00d7 tan {angle2}\u00b0 = {base} \u00d7 {math.tan(math.radians(angle2)):.4f}"
         f"<br>= <strong>{h2} m</strong><br>"
         f"(The wall height of {h1} m is used in setting up the scenario but the direct calculation gives total h.)")
    hint = "Set up the right triangle from the observation point to the top. Use tan."
    return q, s, hint, 3, h2


def _trig_inter_sine_find_side():
    A = random.randint(35, 55)
    C = random.randint(55, 80)
    B = 180 - A - C
    c = random.randint(8, 16)
    a = round(c * math.sin(math.radians(A)) / math.sin(math.radians(C)), 2)
    svg = _trig_svg_general_tri(A, B,
                                 label_a=f"? cm", label_b="", label_c=f"{c} cm",
                                 mark_A=f"A={A}\u00b0", mark_B=f"B={B}\u00b0", mark_C=f"C={C}\u00b0")
    q = (f"{svg}"
         f"In triangle ABC, angle A = {A}\u00b0, angle C = {C}\u00b0, and side c = {c} cm (opposite C). "
         f"Use the sine rule to find side a (opposite A). Give your answer to 2 d.p.")
    s = (rf"\(\dfrac{{a}}{{\sin A}} = \dfrac{{c}}{{\sin C}}\)"
         rf"<br>\(a = \dfrac{{{c} \times \sin {A}°}}{{\sin {C}°}}"
         rf" = \dfrac{{{c} \times {math.sin(math.radians(A)):.4f}}}{{{math.sin(math.radians(C)):.4f}}}\)"
         f"<br>= <strong>{a} cm</strong>")
    hint = "Sine rule: a/sin A = c/sin C. Multiply both sides by sin A to isolate a."
    return q, s, hint, 3, a


# ===== DIFFICULT (10) =====

def _trig_diff_sine_rule_side():
    A = random.randint(35, 50)
    B = random.randint(60, 80)
    C = 180 - A - B
    a = random.randint(8, 15)
    sin_a = math.sin(math.radians(A))
    sin_b = math.sin(math.radians(B))
    b = round(a * sin_b / sin_a, 2)
    svg = _trig_svg_general_tri(A, B,
                                 label_a=f"{a} cm", label_b="? cm", label_c="",
                                 mark_A=f"A={A}\u00b0", mark_B=f"B={B}\u00b0", mark_C=f"C={C}\u00b0")
    q = (f"{svg}"
         f"In triangle ABC, angle A = {A}\u00b0, angle B = {B}\u00b0, and side a = {a} cm (opposite A). "
         f"Use the sine rule to find side b (opposite B). Give your answer to 2 d.p.")
    s = (
        rf"<strong>Sine rule:</strong> \(\dfrac{{a}}{{\sin A}} = \dfrac{{b}}{{\sin B}}\)<br><br>"
        rf"<strong>Step 1</strong> — rearrange for \(b\):<br>"
        rf"\(b = \dfrac{{a \sin B}}{{\sin A}}\)<br><br>"
        rf"<strong>Step 2</strong> — substitute \(a = {a}\,\text{{cm}}\), \(A = {A}^\circ\), \(B = {B}^\circ\):<br>"
        rf"\(b = \dfrac{{{a} \times \sin {B}^\circ}}{{\sin {A}^\circ}}\)<br><br>"
        rf"<strong>Step 3</strong> — evaluate:<br>"
        rf"\(b = \dfrac{{{a} \times {sin_b:.4f}}}{{{sin_a:.4f}}} = {b:.2f}\)<br><br>"
        rf"<strong>Answer:</strong> \(b = {b:.2f}\,\text{{cm}}\)"
    )
    hint = "Use the pair you know (a and A) together with the unknown pair (b and B)."
    return q, s, hint, 3, b


def _trig_diff_cosine_rule_side():
    b = random.randint(6, 12)
    c = random.randint(6, 12)
    A = random.randint(40, 80)
    a = round(math.sqrt(b ** 2 + c ** 2 - 2 * b * c * math.cos(math.radians(A))), 2)
    B_approx = random.randint(40, 70)
    while A + B_approx >= 170:
        B_approx -= 5
    svg = _trig_svg_general_tri(A, B_approx,
                                 label_a="? cm", label_b=f"{b} cm", label_c=f"{c} cm",
                                 mark_A=f"A={A}\u00b0")
    q = (f"{svg}"
         f"In triangle ABC, sides b = {b} cm, c = {c} cm, and the included angle A = {A}\u00b0. "
         f"Use the cosine rule to find side a. Give your answer to 2 d.p.")
    s = (rf"\(a^2 = b^2 + c^2 - 2bc\cos A\)"
         rf"<br>\(= {b}^2 + {c}^2 - 2 \times {b} \times {c} \times \cos {A}°\)"
         rf"<br>\(= {b**2} + {c**2} - {2*b*c} \times {math.cos(math.radians(A)):.4f}\)"
         rf"<br>\(= {b**2+c**2} - {round(2*b*c*math.cos(math.radians(A)),4)} = {round(a**2,4)}\)"
         f"<br>a = <strong>{a} cm</strong>")
    hint = "Cosine rule: a\u00b2 = b\u00b2 + c\u00b2 \u2212 2bc\u202fcos\u202fA. Use when you have SAS."
    return q, s, hint, 3, a


def _trig_diff_area_sine():
    a = random.randint(6, 14)
    b = random.randint(6, 14)
    C = random.randint(40, 80)
    area = round(0.5 * a * b * math.sin(math.radians(C)), 2)
    A_deg = random.randint(35, 55)
    B_deg = 180 - C - A_deg
    svg = _trig_svg_general_tri(A_deg, B_deg,
                                 label_a=f"{a} cm", label_b=f"{b} cm", label_c="",
                                 mark_A="A", mark_B="B", mark_C=f"C={C}\u00b0")
    q = (f"{svg}"
         f"In triangle ABC, sides a = {a} cm, b = {b} cm, and the included angle C = {C}\u00b0. "
         f"Calculate the area of the triangle. Give your answer to 2 d.p.")
    s = (rf"Area \(= \dfrac{{1}}{{2}}\,ab\sin C\)"
         rf"<br>\(= \dfrac{{1}}{{2}} \times {a} \times {b} \times \sin {C}°\)"
         rf"<br>\(= \dfrac{{1}}{{2}} \times {a} \times {b} \times {math.sin(math.radians(C)):.4f}\)"
         f"<br>= <strong>{area} cm\u00b2</strong>")
    hint = "Area = \u00bd\u202fa\u202fb\u202fsin\u202fC. This formula works for any triangle when you know two sides and the included angle."
    return q, s, hint, 2, area


def _trig_diff_3d():
    l = random.randint(6, 10)
    w = random.randint(4, 8)
    h = random.randint(8, 15)
    diag_base = round(math.sqrt(l ** 2 + w ** 2), 2)
    space_diag = round(math.sqrt(l ** 2 + w ** 2 + h ** 2), 2)
    angle = round(math.degrees(math.atan(h / diag_base)), 1)
    # 3D cuboid SVG (isometric-style)
    W, H = _TRIG_DIAGRAM_W, _TRIG_DIAGRAM_H
    ox, oy = 58, H - 48
    dx, dy = 150, 0
    ex_x, ex_y = 36, -22
    fz = -88
    def pt(ix, iy, iz):
        return ox + ix*dx + iy*ex_x, oy + iy*ex_y + iz*(fz/1)
    # 8 vertices of cuboid
    p = [pt(x,y,z) for z in [0,1] for y in [0,1] for x in [0,1]]
    def line(a, b, dash=""):
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<line x1="{p[a][0]:.0f}" y1="{p[a][1]:.0f}" x2="{p[b][0]:.0f}" y2="{p[b][1]:.0f}" stroke="#888" stroke-width="1.2"{ds}/>'
    edges = (line(0,1)+line(0,2)+line(0,4)+line(1,3)+line(1,5)+line(2,3)+
             line(2,6,"")+line(4,5)+line(4,6)+line(3,7)+line(5,7)+line(6,7))
    # Space diagonal: from p[0] to p[7]
    diag_line = (f'<line x1="{p[0][0]:.0f}" y1="{p[0][1]:.0f}" x2="{p[7][0]:.0f}" y2="{p[7][1]:.0f}"'
                 f' stroke="#a13544" stroke-width="2" stroke-dasharray="5,3"/>')
    # Base diagonal: from p[0] to p[3]
    base_line = (f'<line x1="{p[0][0]:.0f}" y1="{p[0][1]:.0f}" x2="{p[3][0]:.0f}" y2="{p[3][1]:.0f}"'
                 f' stroke="#01696f" stroke-width="2" stroke-dasharray="5,3"/>')
    svg = (f'{_trig_svg_open(W, H)}'
           f'{edges}{diag_line}{base_line}'
           f'<text x="{p[0][0]-8:.0f}" y="{p[0][1]+12:.0f}" font-size="11" fill="#333">A</text>'
           f'<text x="{p[7][0]+4:.0f}" y="{p[7][1]-4:.0f}" font-size="11" fill="#333">G</text>'
           f'<text x="{p[3][0]+4:.0f}" y="{p[3][1]+4:.0f}" font-size="11" fill="#333">C</text>'
           f'<text x="{p[0][0]+5:.0f}" y="{p[0][1]+18:.0f}" font-size="10" fill="#888">{l}cm\xd7{w}cm\xd7{h}cm</text>'
           f'</svg></div>')
    q = (f"{svg}"
         f"A cuboid has length {l} cm, width {w} cm, and height {h} cm. "
         f"Calculate the angle between the space diagonal AG and the base diagonal AC. "
         f"Give your answer to 1 d.p.")
    s = (f"Step 1 \u2013 Base diagonal AC:<br>"
         rf"\(\text{{AC}} = \sqrt{{{l}^2+{w}^2}} = \sqrt{{{l**2+w**2}}} = {diag_base}\) cm<br>"
         f"Step 2 \u2013 The right triangle has AC as base ({diag_base} cm) and height CG = {h} cm:<br>"
         rf"\(\tan\theta = \dfrac{{{h}}}{{{diag_base}}}\)"
         f"<br>\u03b8 = tan\u207b\u00b9\u202f({h}/{diag_base})"
         f"<br>= <strong>{angle}\u00b0</strong>")
    hint = "Find the base diagonal with Pythagoras first, then use tan with the height."
    return q, s, hint, 4, angle


def _trig_diff_sine_rule_angle():
    a, b, B, A, C = 13, 8, 35, 59.4, 85.6
    for _ in range(40):
        a = random.randint(10, 15)
        b = random.randint(6, 9)
        B = random.randint(25, 40)
        valid = False
        for _ in range(80):
            sinA = a * math.sin(math.radians(B)) / b
            if sinA > 1 or sinA <= 0:
                B += 1
                if B > 90:
                    break
                continue
            A = math.degrees(math.asin(min(1, sinA)))
            if A + B >= 179.5:
                B += 1
                if B > 90:
                    break
                continue
            A = round(A, 1)
            C = 180 - A - B
            if C >= 1:
                valid = True
            break
        if valid:
            break
    svg = _trig_svg_general_tri(int(A), B,
                                 label_a=f"{a} cm", label_b=f"{b} cm", label_c="",
                                 mark_A=f"A=?", mark_B=f"B={B}\u00b0",
                                 side_a=a, side_b=b)
    q = (f"{svg}"
         f"In triangle ABC, side a = {a} cm (opposite A), side b = {b} cm (opposite B), and angle B = {B}\u00b0. "
         f"Use the sine rule to find the acute angle A. Give your answer to 1 d.p.")
    s = (rf"\(\dfrac{{\sin A}}{{a}} = \dfrac{{\sin B}}{{b}}\)"
         rf"<br>\(\sin A = \dfrac{{{a} \times \sin {B}°}}{{{b}}}"
         rf" = \dfrac{{{a} \times {math.sin(math.radians(B)):.4f}}}{{{b}}} = {sinA:.4f}\)"
         f"<br>A = sin\u207b\u00b9\u202f({sinA:.4f})"
         f"<br>= <strong>{A}\u00b0</strong>")
    hint = "Rearrange the sine rule: sin A = a\u202f\u00d7\u202fsin B / b, then use inverse sin."
    return q, s, hint, 4, A


def _trig_diff_cosine_rule_angle():
    b = random.randint(6, 14)
    c = random.randint(6, 14)
    a = random.randint(5, b + c - 2)
    while a >= b + c or b >= a + c or c >= a + b:
        a = random.randint(5, b + c - 2)
    cosA = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
    cosA = max(-1, min(1, cosA))
    A = round(math.degrees(math.acos(cosA)), 1)
    B_approx = random.randint(40, 70)
    while A + B_approx >= 175:
        B_approx -= 5
    svg = _trig_svg_general_tri(int(A), B_approx,
                                 label_a=f"{a} cm", label_b=f"{b} cm", label_c=f"{c} cm",
                                 mark_A="A = ?")
    q = (f"{svg}"
         f"In triangle ABC, a = {a} cm, b = {b} cm, c = {c} cm. "
         f"Use the cosine rule to find angle A. Give your answer to 1 d.p.")
    s = (rf"\(\cos A = \dfrac{{b^2+c^2-a^2}}{{2bc}} = \dfrac{{{b**2}+{c**2}-{a**2}}}{{{2*b*c}}} = {cosA:.4f}\)"
         f"<br>A = cos\u207b\u00b9\u202f({cosA:.4f})"
         f"<br>= <strong>{A}\u00b0</strong>")
    hint = "Rearranged cosine rule: cos A = (b\u00b2+c\u00b2\u2212a\u00b2)/(2bc). Use when all 3 sides are known."
    return q, s, hint, 3, A


def _trig_diff_area_find_side():
    a = random.randint(6, 14)
    C = random.randint(35, 75)
    area = random.randint(20, 60)
    # Area = 1/2 * a * b * sinC  =>  b = 2*area / (a * sinC)
    b = round(2 * area / (a * math.sin(math.radians(C))), 2)
    A_deg = random.randint(35, 55)
    B_deg = 180 - C - A_deg
    svg = _trig_svg_general_tri(A_deg, B_deg,
                                 label_a=f"{a} cm", label_b="? cm", label_c="",
                                 mark_A="A", mark_B="B", mark_C=f"C={C}\u00b0")
    q = (f"{svg}"
         f"In triangle ABC, side a = {a} cm, included angle C = {C}\u00b0, and the area is {area} cm\u00b2. "
         f"Find side b. Give your answer to 2 d.p.")
    s = (rf"Area \(= \dfrac{{1}}{{2}}\,ab\sin C\)"
         rf"<br>\({area} = \dfrac{{1}}{{2}} \times {a} \times b \times \sin {C}°\)"
         rf"<br>\({area} = {a/2} \times b \times {math.sin(math.radians(C)):.4f}\)"
         f"<br>b = {area} \u00f7 ({a / 2} \u00d7 {math.sin(math.radians(C)):.4f})"
         f"<br>= <strong>{b} cm</strong>")
    hint = "Rearrange Area = \u00bd\u202fa\u202fb\u202fsin\u202fC to make b the subject."
    return q, s, hint, 3, b


def _trig_diff_bearing_nonright():
    # Ship sails on bearing, then turns; find distance back to start using cosine rule
    d1 = random.randint(10, 20)
    d2 = random.randint(8, 18)
    turn_angle = random.randint(100, 150)  # angle between the two legs at the turning point
    dist = round(math.sqrt(d1 ** 2 + d2 ** 2 - 2 * d1 * d2 * math.cos(math.radians(turn_angle))), 2)
    bearing1 = random.choice([60, 90, 120, 45])
    svg = _trig_svg_bearing_triangle(
        d1, d2, bearing1, turn_angle,
        label_a=f"{d2} km", label_b=f"{d1} km", label_c="? km",
        mark_A="Start", mark_B="End", mark_C="Turn",
    )
    q = (f"{svg}"
         f"A ship sails {d1} km on a bearing of {bearing1:03}\u00b0, "
         f"then {d2} km on a different bearing. The angle between the two legs of the journey is {turn_angle}\u00b0. "
         f"Find the direct distance back to the starting point. Give your answer to 2 d.p.")
    s = (f"The included angle at the turning point is {turn_angle}\u00b0.<br>"
         rf"\(d^2 = {d1}^2 + {d2}^2 - 2\times{d1}\times{d2}\times\cos {turn_angle}°\)"
         rf"<br>\(= {d1**2} + {d2**2} - {2*d1*d2} \times {math.cos(math.radians(turn_angle)):.4f}\)"
         rf"<br>\(= {d1**2+d2**2} - ({round(2*d1*d2*math.cos(math.radians(turn_angle)),3)})\)"
         f"<br>\u21d2 d = <strong>{dist} km</strong>")
    hint = "Apply the cosine rule with the included angle between the two legs."
    return q, s, hint, 4, dist


def _trig_diff_exact_compound():
    choices = [
        (r"\sin 30°\cos 60° + \cos 30°\sin 60°",
         r"\frac{1}{2}\cdot\frac{1}{2}+\frac{\sqrt{3}}{2}\cdot\frac{\sqrt{3}}{2}=\frac{1}{4}+\frac{3}{4}=1",
         "This equals sin(30°+60°) = sin 90° = 1",
         "1"),
        (r"\cos^2 45° - \sin^2 45°",
         r"\left(\frac{\sqrt{2}}{2}\right)^2 - \left(\frac{\sqrt{2}}{2}\right)^2 = \frac{1}{2}-\frac{1}{2}",
         "This equals cos(2\xd745°) = cos 90° = 0",
         "0"),
        (r"\tan 45° + \sin 30°",
         r"1 + \frac{1}{2} = \frac{3}{2}",
         "tan 45° = 1, sin 30° = 1/2",
         "3/2"),
        (r"2\sin 60°\cos 60°",
         r"2 \cdot \frac{\sqrt{3}}{2} \cdot \frac{1}{2} = \frac{\sqrt{3}}{2}",
         "This equals sin(2\xd760°) = sin 120° = \u221a3/2",
         "\u221a3/2"),
    ]
    expr, working, note, ans = random.choice(choices)
    q = rf"Using exact values only, evaluate \({expr}\). Show your working."
    s = (rf"\({expr} = {working}\)"
         f"<br>= <strong>{ans}</strong>&ensp;({note})")
    hint = "Substitute the exact values for each trig function, then simplify."
    return q, s, hint, 3, _trig_exact_compound_answer(ans)


# ===== MCQ (15 questions) =====

_TRIG_MCQ_RAW = [
        {
            "q": "What does SOH CAH TOA help you remember?",
            "opts": ["A  The three trigonometric ratios", "B  The order of operations", "C  How to solve quadratics", "D  The names of the sides of a triangle"],
            "ans": "A",
            "hint": "SOH CAH TOA is a mnemonic for sin, cos, tan."
        },
        {
            "q": r"In a right-angled triangle, \(\sin\theta\) = opposite \(\div\) …",
            "opts": ["A  adjacent", "B  hypotenuse", "C  opposite", "D  angle"],
            "ans": "B",
            "hint": "SOH: sin = opposite / hypotenuse."
        },
        {
            "q": r"Which of the following is the exact value of \(\cos 60°\)?",
            "opts": [r"A  \(0\)", r"B  \(\tfrac{1}{2}\)", r"C  \(\tfrac{\sqrt{2}}{2}\)", r"D  \(\tfrac{\sqrt{3}}{2}\)"],
            "ans": "B",
            "hint": "cos 60° = 1/2."
        },
        {
            "q": "Which rule should you use to find a missing side when you know two sides and the included angle in a non-right triangle?",
            "opts": ["A  Sine rule", "B  Cosine rule", "C  Pythagoras' theorem", "D  SOH CAH TOA"],
            "ans": "B",
            "hint": "Cosine rule: a\u00b2 = b\u00b2 + c\u00b2 \u2212 2bc\u202fcos A (SAS)."
        },
        {
            "q": "The formula for the area of a triangle using sine is:",
            "opts": [r"A  \(\tfrac{1}{2}ab\sin C\)", r"B  \(\tfrac{1}{2}\times\text{base}\times\text{height}\)", r"C  \(ab\sin C\)", r"D  \(\tfrac{1}{2}ab\cos C\)"],
            "ans": "A",
            "hint": "Area = \u00bd\u202fab\u202fsin\u202fC."
        },
        {
            "q": r"In a right-angled triangle, \(\tan\theta = \tfrac{3}{4}\). What is the hypotenuse?",
            "opts": ["A  5", "B  7", "C  1", "D  12"],
            "ans": "A",
            "hint": "Opposite = 3, adjacent = 4. Hypotenuse = \u221a(3\u00b2+4\u00b2) = 5."
        },
        {
            "q": "Which of these is NOT a standard right-angled triangle trigonometric ratio at GCSE?",
            "opts": ["A  sin", "B  cos", "C  tan", "D  sec"],
            "ans": "D",
            "hint": "sec (secant) is not on the GCSE specification."
        },
        {
            "q": r"The exact value of \(\sin 45°\) is:",
            "opts": [r"A  \(\tfrac{1}{2}\)", r"B  \(\tfrac{\sqrt{2}}{2}\)", r"C  \(\tfrac{\sqrt{3}}{2}\)", "D  1"],
            "ans": "B",
            "hint": "sin 45° = 1/\u221a2 = \u221a2/2."
        },
        {
            "q": "The angle of elevation is measured:",
            "opts": ["A  upward from the horizontal", "B  downward from the horizontal", "C  upward from the vertical", "D  downward from the vertical"],
            "ans": "A",
            "hint": "Elevation = looking up from horizontal."
        },
        {
            "q": "In 3D trigonometry, what is usually the best first step?",
            "opts": ["A  Use the sine rule directly", "B  Identify a right-angled triangle within the 3D shape", "C  Apply Pythagoras in three dimensions at once", "D  Guess the answer"],
            "ans": "B",
            "hint": "Always find a 2D right triangle within the solid first."
        },
        {
            "q": r"The exact value of \(\tan 30°\) is:",
            "opts": [r"A  \(\tfrac{1}{\sqrt{3}}\)", r"B  \(\tfrac{\sqrt{3}}{2}\)", "C  1", r"D  \(\sqrt{3}\)"],
            "ans": "A",
            "hint": "tan 30° = 1/\u221a3 = \u221a3/3."
        },
        {
            "q": "To find an angle when all three sides of a triangle are known, which rule do you use?",
            "opts": ["A  Sine rule", "B  Cosine rule (rearranged for angle)", "C  Pythagoras' theorem", "D  SOH CAH TOA"],
            "ans": "B",
            "hint": "Rearranged cosine rule: cos A = (b\u00b2+c\u00b2\u2212a\u00b2)/(2bc)."
        },
        {
            "q": r"The cosine rule formula for finding angle \(A\) is:",
            "opts": [
                r"A  \(\cos A = \dfrac{b^2+c^2-a^2}{2bc}\)",
                r"B  \(\cos A = \dfrac{a^2+c^2-b^2}{2bc}\)",
                r"C  \(\cos A = \dfrac{a^2-b^2-c^2}{2bc}\)",
                r"D  \(\cos A = \dfrac{b^2-c^2+a^2}{2bc}\)",
            ],
            "ans": "A",
            "hint": "cos A = (b\u00b2 + c\u00b2 \u2212 a\u00b2) / (2bc)."
        },
        {
            "q": "The angle of depression from the top of a 20 m cliff to a point 20 m away horizontally is:",
            "opts": ["A  30\u00b0", "B  45\u00b0", "C  60\u00b0", "D  90\u00b0"],
            "ans": "B",
            "hint": "tan\u202f\u03b8 = 20/20 = 1, so \u03b8 = 45\u00b0."
        },
        {
            "q": r"When using \(\dfrac{a}{\sin A} = \dfrac{b}{\sin B}\) and \(\sin A > 1\) is obtained, this means:",
            "opts": ["A  There are two solutions", "B  The triangle is right-angled", "C  No such triangle exists", "D  A is a reflex angle"],
            "ans": "C",
            "hint": "sin of any angle cannot exceed 1, so the triangle cannot exist."
        },
]
_TRIG_MCQ_BANK = normalize_mcq_bank(_TRIG_MCQ_RAW)


def trigonometry_mcq():
    chosen = random.choice(_TRIG_MCQ_BANK)
    q = chosen["q"]
    options = chosen["opts"]
    correct = chosen["ans"]
    s = f"<strong>Answer: {correct}</strong><br>{chosen['hint']}"
    hint = chosen["hint"]
    return q, s, hint, 1, options, correct


# ===== VARIANTS FUNCTION =====

def gcse_trigonometry_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _TRIG_MCQ_BANK, procedural_mcq_for('trigonometry'), 'trigonometry', difficulty
        )
    if difficulty == 'foundational':
        pool = [
            _trig_found_sin_side,
            _trig_found_cos_side,
            _trig_found_tan_angle,
            _trig_found_pythagoras,
            _trig_found_ladder,
            _trig_found_find_hyp_from_opp,
            _trig_found_find_adj_from_tan,
            _trig_found_pythagoras_leg,
            _trig_found_cos_angle,
            _trig_found_exact_values,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _trig_inter_two_step,
            _trig_inter_bearing,
            _trig_inter_elevation,
            _trig_inter_isosceles,
            _trig_inter_exact_expression,
            _trig_inter_depression,
            _trig_inter_cosine_find_angle,
            _trig_inter_converse_pyth,
            _trig_inter_compound,
            _trig_inter_sine_find_side,
        ]
    elif difficulty == 'difficult':
        pool = [
            _trig_diff_sine_rule_side,
            _trig_diff_cosine_rule_side,
            _trig_diff_area_sine,
            _trig_diff_3d,
            _trig_diff_sine_rule_angle,
            _trig_diff_cosine_rule_angle,
            _trig_diff_area_find_side,
            _trig_diff_bearing_nonright,
            _trig_diff_exact_compound,
        ]
    else:  # mixed
        found = random.sample([
            _trig_found_sin_side, _trig_found_cos_side, _trig_found_tan_angle,
            _trig_found_pythagoras, _trig_found_ladder,
            _trig_found_find_hyp_from_opp, _trig_found_find_adj_from_tan,
            _trig_found_pythagoras_leg, _trig_found_cos_angle, _trig_found_exact_values,
        ], 3)
        inter = random.sample([
            _trig_inter_two_step, _trig_inter_bearing, _trig_inter_elevation,
            _trig_inter_isosceles, _trig_inter_exact_expression,
            _trig_inter_depression, _trig_inter_cosine_find_angle,
            _trig_inter_converse_pyth, _trig_inter_compound, _trig_inter_sine_find_side,
        ], 4)
        diff = random.sample([
            _trig_diff_sine_rule_side, _trig_diff_cosine_rule_side, _trig_diff_area_sine,
            _trig_diff_3d, _trig_diff_sine_rule_angle,
            _trig_diff_cosine_rule_angle, _trig_diff_area_find_side,
            _trig_diff_bearing_nonright, _trig_diff_exact_compound,
        ], 3)
        return found + inter + diff

    return select_tier_variants(pool)


# ===== MAIN GENERATOR =====

def gcse_trigonometry(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_trigonometry_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'trigonometry',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_trigonometry_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _trig_problem_from_output(variant(), difficulty)