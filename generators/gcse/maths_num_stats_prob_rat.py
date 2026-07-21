import random
import math

from generators.shared.utils import make_problem, problem_from_choice_output
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)



# ------------------------------------------------------------
# GCSE Maths – Number (15 / 19 / 19 + 18 MCQs)
# Add this section to generators/gcse/maths.py
# ------------------------------------------------------------


def _number_fmt(x, dp=2):
    """Format a decimal without unnecessary trailing zeros."""
    if isinstance(x, int):
        return str(x)
    s = f"{x:.{dp}f}"
    return s.rstrip('0').rstrip('.')


def _number_sf_value(n, sf):
    """Return n rounded to sf significant figures as a float/int suitable for display."""
    if n == 0:
        return 0
    places = sf - int(math.floor(math.log10(abs(n)))) - 1
    rounded = round(n, places)
    if places <= 0:
        return int(rounded)
    return rounded


def _number_mcq_options(correct, distractors):
    correct_s = str(correct)
    choices = [correct_s]
    seen = {correct_s}
    for d in distractors:
        ds = str(d)
        if ds not in seen:
            choices.append(ds)
            seen.add(ds)
    pad_pool = ["0", "1", "1/2", "10", "100", "0.1", "-1"]
    i = 0
    while len(choices) < 4:
        cand = pad_pool[i % len(pad_pool)]
        i += 1
        if cand not in seen:
            choices.append(cand)
            seen.add(cand)
    choices = choices[:4]
    random.shuffle(choices)
    letters = ['A', 'B', 'C', 'D']
    options = [f"{letters[i]}  {choices[i]}" for i in range(4)]
    correct_letter = letters[choices.index(correct_s)]
    return options, correct_letter


def _number_prime_factor_string(n):
    """Return GCSE-style prime factor product e.g. 2³ × 3²."""
    factors = []
    d = 2
    while d * d <= n:
        exp = 0
        while n % d == 0:
            n //= d
            exp += 1
        if exp:
            factors.append(f"{d}^{exp}" if exp > 1 else str(d))
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(str(n))
    return " × ".join(factors)


def _number_random_prime_factor_composite():
    """Build a composite from small primes so the factor form is GCSE-friendly."""
    primes = [2, 3, 5, 7]
    n = 1
    for _ in range(random.randint(2, 4)):
        p = random.choice(primes)
        exp = random.randint(1, 3)
        n *= p ** exp
    return n, _number_prime_factor_string(n)


def _number_random_hcf_lcm_pair():
    """Two numbers sharing prime structure; returns (a, b, hcf, lcm)."""
    primes = [2, 3, 5, 7, 11]
    exp_a = {p: random.randint(0, 3) for p in primes}
    exp_b = {p: random.randint(0, 3) for p in primes}
    while all(exp_a[p] == 0 and exp_b[p] == 0 for p in primes):
        p = random.choice(primes)
        exp_a[p] = random.randint(1, 3)
    a = 1
    b = 1
    hcf = 1
    lcm = 1
    for p in primes:
        ea, eb = exp_a[p], exp_b[p]
        if ea:
            a *= p ** ea
        if eb:
            b *= p ** eb
        if ea or eb:
            hcf *= p ** min(ea, eb)
            lcm *= p ** max(ea, eb)
    if a == b:
        exp_b[random.choice(primes)] += 1
        return _number_random_hcf_lcm_pair()
    return a, b, hcf, lcm


def _number_non_square_n(low_root=4, high_root=14):
    """Integer strictly between two consecutive perfect squares."""
    lo = random.randint(low_root, high_root)
    return random.randint(lo * lo + 1, (lo + 1) * (lo + 1) - 1), lo, lo + 1


def _number_recurring_decimal_case():
    """Procedural recurring-decimal → fraction (single- or two-digit repeat)."""
    if random.random() < 0.55:
        d = random.randint(1, 8)
        dec = f"0.{str(d) * 3}…"
        num, den = d, 9
    else:
        ab = random.randint(10, 98)
        while ab % 11 == 0:
            ab = random.randint(10, 98)
        dec = f"0.{str(ab) * 2}…"
        num, den = ab, 99
    g = math.gcd(num, den)
    return dec, f"{num // g}/{den // g}"


# ---------- FOUNDATIONAL (15) ----------

def _number_found_place_value_digit():
    while True:
        thousands = random.randint(2, 9)
        hundreds = random.randint(1, 9)
        tens = random.randint(1, 9)
        ones = random.randint(1, 9)
        if len({thousands, hundreds, tens, ones}) == 4:
            break
    number = thousands * 1000 + hundreds * 100 + tens * 10 + ones
    digit_name, digit, value = random.choice([
        ('thousands', thousands, thousands * 1000),
        ('hundreds', hundreds, hundreds * 100),
        ('tens', tens, tens * 10),
        ('ones', ones, ones),
    ])
    q = rf"In the number {number}, what is the value of the digit {digit}?"
    s = rf"The digit {digit} is in the {digit_name} column, so its value is <strong>{value}</strong>."
    hint = "Use the place value columns: thousands, hundreds, tens, ones."
    return q, s, hint, 1, value
def _number_found_decimal_place_value():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    c = random.randint(1, 9)
    d = random.randint(1, 9)
    number = f"{a}.{b}{c}{d}"
    position, digit, value = random.choice([
        ('tenths', b, f"{b}/10"),
        ('hundredths', c, f"{c}/100"),
        ('thousandths', d, f"{d}/1000"),
    ])
    q = rf"In the number {number}, which digit is in the {position} column?"
    s = rf"The {position} column contains the digit <strong>{digit}</strong>. Its value is {value}."
    hint = "After the decimal point the columns are tenths, hundredths, thousandths."
    return q, s, hint, 1, digit
def _number_found_compare_decimals():
    a = round(random.randint(30, 95) / 100, 2)
    b = round(a + random.choice([-0.07, -0.03, 0.04, 0.08]), 2)
    if b <= 0:
        b = round(a + 0.12, 2)
    larger = max(a, b)
    symbol = '>' if a > b else '<'
    q = rf"Insert the correct sign, &gt; or &lt;: {a} ___ {b}"
    s = rf"Line up the decimal points and compare from left to right. Since {larger} is larger, <strong>{a} {symbol} {b}</strong>."
    hint = "Write both decimals with the same number of decimal places, then compare digits."
    from generators.shared.utils import compare_choice_payload
    correct = 'A' if symbol == '>' else 'B'
    return q, s, hint, 1, compare_choice_payload('&gt;', '&lt;', correct)


def _number_found_order_decimals():
    nums = sorted({round(random.randint(12, 98) / 100, 2) for _ in range(6)})[:4]
    while len(nums) < 4:
        nums = sorted({round(random.randint(12, 98) / 100, 2) for _ in range(6)})[:4]
    mixed = nums[:]
    random.shuffle(mixed)
    q = rf"Put these decimals in ascending order: {', '.join(str(x) for x in mixed)}"
    s = rf"Ascending means smallest to largest. The correct order is <strong>{', '.join(str(x) for x in nums)}</strong>."
    hint = "Ascending order means start with the smallest number."
    return q, s, hint, 2, _number_list_answer(nums)


def _number_found_round_nearest_10_100():
    n = random.randint(120, 9876)
    unit = random.choice([10, 100])
    ans = round(n / unit) * unit
    q = rf"Round {n} to the nearest {unit}."
    s = rf"To round to the nearest {unit}, look at the next place value column. <strong>{n} rounds to {ans}</strong>."
    hint = "Look one place value column to the right of the column you are rounding to."
    return q, s, hint, 1, ans
def _number_found_round_decimal_places():
    n = round(random.uniform(2, 40), 3)
    dp = random.choice([1, 2])
    ans = round(n, dp)
    q = rf"Round {n} to {dp} decimal place{'s' if dp != 1 else ''}."
    s = rf"Keep {dp} digit{'s' if dp != 1 else ''} after the decimal point and check the next digit. The answer is <strong>{ans}</strong>."
    hint = "If the next digit is 5 or more, round up."
    return q, s, hint, 1, ans
def _number_found_significant_figures_simple():
    n = random.randint(1200, 98700)
    sf = random.choice([1, 2, 3])
    ans = _number_sf_value(n, sf)
    q = rf"Round {n} to {sf} significant figure{'s' if sf != 1 else ''}."
    s = rf"Start counting significant figures from the first non-zero digit. Rounded to {sf} significant figure{'s' if sf != 1 else ''}, the answer is <strong>{ans}</strong>."
    hint = "The first significant figure is the first non-zero digit."
    return q, s, hint, 1, ans
def _number_found_negative_add_subtract():
    a = random.randint(-12, 12)
    b = random.randint(-12, 12)
    while a == 0 or b == 0:
        a = random.randint(-12, 12)
        b = random.randint(-12, 12)
    op = random.choice(['+', '-'])
    ans = a + b if op == '+' else a - b
    q = rf"Calculate {a} {op} ({b})."
    s = rf"Using directed number rules, {a} {op} ({b}) = <strong>{ans}</strong>."
    hint = "A subtraction of a negative becomes addition. Use a number line if needed."
    return q, s, hint, 1, ans
def _number_found_multiply_by_power_10():
    n = round(random.uniform(1.2, 98.7), 2)
    p = random.choice([10, 100, 1000])
    op = random.choice(['multiply', 'divide'])
    ans = n * p if op == 'multiply' else n / p
    symbol = '×' if op == 'multiply' else '÷'
    q = rf"Calculate {n} {symbol} {p}."
    s = rf"When you {op} by {p}, the digits move {len(str(p))-1} place{'s' if p != 10 else ''}. The answer is <strong>{_number_fmt(ans, 5)}</strong>."
    hint = "Multiplying by powers of 10 moves digits left; dividing moves them right."
    return q, s, hint, 1, ans
def _number_found_square_cube():
    n = random.randint(2, 12)
    power = random.choice([2, 3])
    ans = n ** power
    q = rf"Calculate \({n}^{power}\)."
    s = rf"\({n}^{power}\) means multiply {n} by itself {power} times. Therefore \({n}^{power} = \)<strong>{ans}</strong>."
    hint = "A power means repeated multiplication."
    return q, s, hint, 1, ans
def _number_found_percentage_of_amount():
    pct = random.choice([5, 10, 12, 15, 18, 20, 25, 30, 40, 50, 75])
    amount = random.randint(20, 50) * 10
    ans = amount * pct / 100
    q = rf"Find {pct}% of {amount}."
    s = rf"{pct}% means {pct} out of 100, so {pct}% of {amount} = {amount} × {pct}/100 = <strong>{_number_fmt(ans)}</strong>."
    hint = "Convert the percentage to a fraction over 100, then multiply."
    return q, s, hint, 1, ans
def _number_found_fraction_of_amount():
    denom = random.choice([3, 4, 5, 8, 10])
    num = random.randint(1, denom - 1)
    amount = denom * random.randint(6, 20)
    ans = amount // denom * num
    q = rf"Find \(\frac{{{num}}}{{{denom}}}\) of {amount}."
    s = rf"First divide by {denom}: {amount} ÷ {denom} = {amount // denom}. Then multiply by {num}: {amount // denom} × {num} = <strong>{ans}</strong>."
    hint = "Divide by the denominator, then multiply by the numerator."
    return q, s, hint, 2, ans
def _number_found_estimate_simple():
    a = round(random.uniform(12, 99), 1)
    b = round(random.uniform(2, 12), 1)
    rounded_a = round(a / 10) * 10
    rounded_b = round(b)
    ans = rounded_a * rounded_b
    q = rf"Estimate {a} × {b} by rounding each number to 1 significant figure."
    s = rf"{a} ≈ {rounded_a} and {b} ≈ {rounded_b}. So {a} × {b} ≈ {rounded_a} × {rounded_b} = <strong>{ans}</strong>."
    hint = "Round to easy numbers first, then multiply mentally."
    return q, s, hint, 2, ans
def _number_found_standard_form_large():
    a = random.randint(11, 99)
    zeros = random.choice([3, 4, 5])
    n = a * (10 ** zeros)
    coefficient = a / 10
    power = zeros + 1
    q = rf"Write {n} in standard form."
    s = rf"Move the decimal point until the first number is between 1 and 10: {n} = <strong>{coefficient} × 10^{power}</strong>."
    hint = "Standard form is A × 10^n where 1 ≤ A < 10."
    return q, s, hint, 2, _number_standard_form_answer(coefficient, power)


def _number_found_indices_multiply():
    base = random.randint(2, 9)
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    ans_power = a + b
    q = rf"Simplify \({base}^{a} \times {base}^{b}\)."
    s = rf"When multiplying powers with the same base, add the indices: \({base}^{a} \times {base}^{b} = {base}^{{{a}+{b}}} = \)<strong>\({base}^{{{ans_power}}}\)</strong>."
    hint = "Same base and multiplication means add the powers."
    return q, s, hint, 1, _number_power_answer(base, ans_power)


# ---------- INTERMEDIATE (15) ----------

def _number_inter_standard_form_small():
    coeff = round(random.uniform(1.2, 9.8), 1)
    power = random.choice([3, 4, 5])
    ordinary = coeff / (10 ** power)
    q = rf"Write {_number_fmt(ordinary, 7)} in standard form."
    s = rf"Move the decimal point {power} places right to make a number between 1 and 10. Therefore {_number_fmt(ordinary, 7)} = <strong>{coeff} × 10^{{-{power}}}</strong>."
    hint = "Very small numbers have negative powers in standard form."
    return q, s, hint, 2, _number_standard_form_answer(coeff, -power)


def _number_inter_standard_form_to_ordinary():
    coeff = round(random.uniform(1.2, 9.8), 1)
    power = random.choice([-4, -3, -2, 3, 4, 5])
    ans = coeff * (10 ** power)
    q = rf"Write \({coeff} \times 10^{{{power}}}\) as an ordinary number."
    s = rf"Multiplying by \(10^{{{power}}}\) moves the decimal point {'right' if power > 0 else 'left'} {abs(power)} places. The answer is <strong>{_number_fmt(ans, 8)}</strong>."
    hint = "Positive powers make large numbers; negative powers make small decimals."
    return q, s, hint, 2, ans
def _number_inter_standard_form_multiply():
    a = random.randint(2, 8)
    b = random.randint(2, 8)
    p = random.randint(2, 5)
    qpow = random.randint(2, 5)
    product = a * b
    power = p + qpow
    if product >= 10:
        coeff = product / 10
        power += 1
    else:
        coeff = product
    q = rf"Calculate \(({a} \times 10^{p})({b} \times 10^{qpow})\), giving your answer in standard form."
    s = rf"Multiply the front numbers and add the powers: {a} × {b} = {product}, and {p} + {qpow} = {p + qpow}. In standard form this is <strong>{_number_fmt(coeff)} × 10^{power}</strong>."
    hint = "For multiplication in standard form, multiply coefficients and add powers."
    return q, s, hint, 2, _number_standard_form_answer(coeff, power)


def _number_inter_standard_form_divide():
    b = random.randint(2, 5)
    coeff_ans = random.randint(2, 8)
    a = b * coeff_ans
    p = random.randint(4, 8)
    qpow = random.randint(1, 3)
    power = p - qpow
    q = rf"Calculate \(({a} \times 10^{p}) \div ({b} \times 10^{qpow})\), giving your answer in standard form."
    s = rf"Divide the front numbers and subtract the powers: {a} ÷ {b} = {coeff_ans}, and {p} − {qpow} = {power}. Answer: <strong>{coeff_ans} × 10^{power}</strong>."
    hint = "For division in standard form, divide coefficients and subtract powers."
    return q, s, hint, 2, _number_standard_form_answer(coeff_ans, power)


def _number_inter_percentage_increase():
    amount = random.randint(8, 120) * 10
    pct = random.randint(3, 38)
    ans = amount * (1 + pct / 100)
    q = rf"Increase {amount} by {pct}%."
    s = rf"The multiplier for an increase of {pct}% is {1 + pct/100}. So {amount} × {1 + pct/100} = <strong>{_number_fmt(ans)}</strong>."
    hint = "Use the multiplier 1 + percentage/100."
    return q, s, hint, 2, ans
def _number_inter_percentage_decrease():
    amount = random.randint(8, 120) * 10
    pct = random.randint(3, 38)
    ans = amount * (1 - pct / 100)
    q = rf"Decrease {amount} by {pct}%."
    s = rf"The multiplier for a decrease of {pct}% is {1 - pct/100}. So {amount} × {1 - pct/100} = <strong>{_number_fmt(ans)}</strong>."
    hint = "Use the multiplier 1 - percentage/100."
    return q, s, hint, 2, ans
def _number_inter_reverse_percentage_increase():
    pct = random.randint(5, 35)
    original = random.randint(15, 400) * 10
    final = round(original * (1 + pct / 100), 2)
    q = rf"A price after a {pct}% increase is £{_number_fmt(final)}. Find the original price."
    s = rf"After a {pct}% increase, the multiplier is {1 + pct/100}. Original = {_number_fmt(final)} ÷ {1 + pct/100} = <strong>£{_number_fmt(original)}</strong>."
    hint = "For reverse percentages, divide by the multiplier."
    return q, s, hint, 3, original
def _number_inter_reverse_percentage_decrease():
    pct = random.randint(5, 40)
    original = random.randint(20, 350) * 10
    final = round(original * (1 - pct / 100), 2)
    q = rf"A price after a {pct}% decrease is £{_number_fmt(final)}. Find the original price."
    s = rf"After a {pct}% decrease, the multiplier is {1 - pct/100}. Original = {_number_fmt(final)} ÷ {1 - pct/100} = <strong>£{_number_fmt(original)}</strong>."
    hint = "The final amount is less than 100% of the original. Divide by the decimal multiplier."
    return q, s, hint, 3, original
def _number_inter_repeated_percentage_change():
    amount = random.randint(15, 150) * 10
    pct1 = random.randint(5, 25)
    pct2 = random.randint(4, 30)
    ans = amount * (1 + pct1/100) * (1 - pct2/100)
    q = rf"An amount of £{amount} is increased by {pct1}% and then decreased by {pct2}%. Find the final amount."
    s = rf"Use successive multipliers: {amount} × {1+pct1/100} × {1-pct2/100} = <strong>£{_number_fmt(ans)}</strong>."
    hint = "Apply the first multiplier, then apply the second multiplier to the new amount."
    return q, s, hint, 3, ans
def _number_inter_error_interval_whole():
    n = random.randint(12, 180)
    lower = n - 0.5
    upper = n + 0.5
    q = rf"A length is given as {n} cm to the nearest centimetre. Write the error interval for the actual length x."
    s = rf"The actual value is within 0.5 cm of {n}. Therefore <strong>{lower} ≤ x &lt; {upper}</strong>."
    hint = "For nearest whole number, subtract and add 0.5."
    return q, s, hint, 2, _number_pair_answer(lower, upper, 'Lower bound', 'Upper bound', 'to')


def _number_inter_error_interval_tenth():
    n = round(random.uniform(2, 30), 1)
    lower = round(n - 0.05, 2)
    upper = round(n + 0.05, 2)
    q = rf"A mass is given as {n} kg to the nearest 0.1 kg. Write the error interval for the actual mass m."
    s = rf"Half of 0.1 is 0.05, so <strong>{lower} ≤ m &lt; {upper}</strong>."
    hint = "The bounds are half the rounding unit below and above the rounded value."
    return q, s, hint, 2, _number_pair_answer(lower, upper, 'Lower bound', 'Upper bound', 'to')


def _number_inter_bounds_area():
    length = random.randint(8, 20)
    width = random.randint(4, 12)
    max_area = (length + 0.5) * (width + 0.5)
    min_area = (length - 0.5) * (width - 0.5)
    q = rf"A rectangle has length {length} cm and width {width} cm, each measured to the nearest centimetre. Find the minimum and maximum possible area."
    s = rf"Lower bounds: {length-0.5} and {width-0.5}, so minimum area = {length-0.5} × {width-0.5} = <strong>{_number_fmt(min_area)} cm²</strong>.<br>Upper bounds: {length+0.5} and {width+0.5}, so maximum area = {length+0.5} × {width+0.5} = <strong>{_number_fmt(max_area)} cm²</strong>."
    hint = "Use lower bounds for the minimum area and upper bounds for the maximum area."
    return q, s, hint, 4, _number_pair_answer(min_area, max_area, 'Minimum area', 'Maximum area', 'to')


def _number_inter_index_division():
    base = random.randint(2, 9)
    a = random.randint(6, 10)
    b = random.randint(1, 5)
    ans = a - b
    q = rf"Simplify \({base}^{a} \div {base}^{b}\)."
    s = rf"When dividing powers with the same base, subtract the indices: \({base}^{a} \div {base}^{b} = {base}^{{{a}-{b}}} = \)<strong>\({base}^{{{ans}}}\)</strong>."
    hint = "Same base and division means subtract the powers."
    return q, s, hint, 1, _number_power_answer(base, ans)


def _number_inter_index_power_of_power():
    base = random.randint(2, 6)
    a = random.randint(2, 5)
    b = random.randint(2, 4)
    ans = a * b
    q = rf"Simplify \(({base}^{a})^{b}\)."
    s = rf"For a power of a power, multiply the indices: \(({base}^{a})^{b} = {base}^{{{a}×{b}}} = \)<strong>\({base}^{{{ans}}}\)</strong>."
    hint = "A power raised to another power means multiply the powers."
    return q, s, hint, 1, _number_power_answer(base, ans)


def _number_inter_prime_factor_product():
    n, ans = _number_random_prime_factor_composite()
    q = rf"Write {n} as a product of prime factors."
    s = rf"Use a factor tree and split until every factor is prime. The product of prime factors is <strong>{ans}</strong>."
    hint = "Keep dividing by prime numbers such as 2, 3, 5 and 7."
    return q, s, hint, 3


def _number_inter_calculator_estimate_fraction():
    a = round(random.uniform(15, 99), 1)
    b = round(random.uniform(2, 12), 1)
    c = round(random.uniform(0.35, 2.5), 2)
    ar = round(a / 10) * 10
    br = round(b)
    cr = 0.5 if c < 1 else round(c)
    ans = ar * br / cr
    q = rf"Estimate \(\frac{{{a} \times {b}}}{{{c}}}\) by rounding each number to 1 significant figure."
    s = rf"{a} ≈ {ar}, {b} ≈ {br}, and {c} ≈ {cr}. So the estimate is \(({ar} × {br}) ÷ {cr} = \)<strong>{_number_fmt(ans)}</strong>."
    hint = "Round each value to one significant figure, then calculate."
    return q, s, hint, 3, ans

# ---------- INTERMEDIATE (extra formats) ----------

def _number_inter_sf_which_larger():
    """Compare two values given in standard form."""
    from generators.shared.utils import compare_choice_payload
    while True:
        c1 = round(random.uniform(2, 9), 1)
        p1 = random.randint(3, 7)
        c2 = round(random.uniform(2, 9), 1)
        p2 = random.randint(3, 7)
        v1, v2 = c1 * (10 ** p1), c2 * (10 ** p2)
        if v1 != v2:
            break
    expr1 = rf'\({c1} \times 10^{{{p1}}}\)'
    expr2 = rf'\({c2} \times 10^{{{p2}}}\)'
    correct = 'A' if v1 > v2 else 'B'
    winner = expr1 if v1 > v2 else expr2
    q = rf'Which is larger: {expr1} or {expr2}?'
    s = (
        rf'Compare powers of 10 first, then coefficients if needed.<br>'
        rf'<strong>{winner}</strong> is larger.'
    )
    hint = 'A larger positive power of 10 means a larger value (for positive numbers).'
    return q, s, hint, 2, compare_choice_payload(expr1, expr2, correct)


def _number_inter_vat_word_problem():
    """Price excluding VAT — find price including VAT."""
    price = random.randint(12, 80) * 5
    vat = 20
    total = round(price * 1.2, 2)
    q = (
        rf"A shop quotes £{price} excluding VAT at {vat}%. "
        rf"What is the price including VAT?"
    )
    s = (
        rf"Multiplier = 1 + {vat}/100 = 1.2<br>"
        rf"£{price} × 1.2 = <strong>£{total}</strong>"
    )
    hint = "Including VAT means multiply by 1 + VAT rate as a decimal."
    return q, s, hint, 2, total
def _number_inter_calculate_to_sf():
    """Evaluate a product/quotient and give the answer in significant figures."""
    a = round(random.uniform(2.5, 9.5), 1)
    b = round(random.uniform(0.2, 0.8), 2)
    sf = random.choice([2, 3])
    raw = a * b
    ans = _number_sf_value(raw, sf)
    q = rf"Work out {a} × {b}. Give your answer to {sf} significant figures."
    s = (
        rf"{a} × {b} = {raw:.4f}<br>"
        rf"Rounded to {sf} significant figures: <strong>{ans}</strong>"
    )
    hint = "Do the calculation first, then round — not the other way round."
    return q, s, hint, 3, ans
def _number_inter_share_ratio():
    """Divide an amount in a given ratio."""
    r1, r2 = random.choice([(2, 3), (3, 4), (3, 5), (2, 5), (4, 7), (1, 4), (5, 8)])
    mult = random.randint(8, 45)
    total = (r1 + r2) * mult
    parts = r1 + r2
    ans1 = total * r1 / parts
    ans2 = total * r2 / parts
    q = rf"Share £{total} in the ratio {r1}:{r2}."
    s = (
        rf"Total parts = {r1} + {r2} = {parts}<br>"
        rf"One part = {total} ÷ {parts} = {total // parts if total % parts == 0 else _number_fmt(total/parts)}<br>"
        rf"Shares: <strong>£{_number_fmt(ans1)}</strong> and <strong>£{_number_fmt(ans2)}</strong>"
    )
    hint = "Add the ratio parts, divide the total by that sum, then multiply by each part of the ratio."
    return q, s, hint, 3, _number_pair_answer(ans1, ans2, 'First share (£)', 'Second share (£)')


# ---------- DIFFICULT (15) ----------

def _number_diff_compound_interest():
    principal = random.randint(20, 500) * 10
    rate = random.randint(2, 8)
    years = random.randint(2, 8)
    ans = principal * ((1 + rate/100) ** years)
    q = rf"£{principal} is invested at {rate}% compound interest per year for {years} years. Find the final amount to the nearest penny."
    s = rf"Use compound interest: {principal} × \((1 + {rate}/100)^{years}\) = {principal} × {1+rate/100}^{years} = <strong>£{ans:.2f}</strong>."
    hint = "Use the percentage multiplier repeatedly, or raise it to the power of the number of years."
    return q, s, hint, 3, round(ans, 2)
def _number_diff_depreciation():
    value = random.randint(40, 250) * 100
    rate = random.randint(8, 28)
    years = random.randint(2, 6)
    ans = value * ((1 - rate/100) ** years)
    q = rf"A car worth £{value} depreciates by {rate}% each year for {years} years. Find its value after {years} years to the nearest pound."
    s = rf"Depreciation uses the multiplier {1-rate/100}. So value = {value} × {1-rate/100}^{years} = <strong>£{round(ans)}</strong>."
    hint = "A percentage decrease uses a multiplier below 1. Apply it once for each year."
    return q, s, hint, 3, round(ans)
def _number_diff_reverse_compound():
    original = round(random.uniform(150, 8000), 2)
    rate = random.randint(3, 15)
    years = random.randint(2, 6)
    final = round(original * ((1 + rate/100) ** years), 2)
    q = rf"After {years} years of compound growth at {rate}% per year, an investment is worth £{final:.2f}. Find the original investment to the nearest penny."
    s = rf"Reverse the compound multiplier: original = {final:.2f} ÷ \({1+rate/100}^{years}\) = <strong>£{original:.2f}</strong>."
    hint = "Divide by the compound multiplier instead of multiplying."
    return q, s, hint, 4, original
def _number_diff_standard_form_context():
    pop = round(random.uniform(2.0, 8.9), 1)
    count = random.randint(2, 9)
    total_coeff = pop * count
    power = 6
    if total_coeff >= 10:
        total_coeff /= 10
        power += 1
    q = rf"One city has a population of \({pop} \times 10^6\). Another {count} identical cities have the same population. Write the total population of the {count} cities in standard form."
    s = rf"Total = {count} × {pop} × 10^6 = {pop*count} × 10^6 = <strong>{_number_fmt(total_coeff)} × 10^{power}</strong>."
    hint = "Multiply the ordinary front numbers first, then adjust to standard form if the front number is 10 or more."
    return q, s, hint, 3, _number_standard_form_answer(total_coeff, power)


def _number_diff_standard_form_mixed_operations():
    a = random.randint(2, 8)
    b = random.randint(2, 8)
    c = random.choice([2, 4])
    p = random.randint(5, 8)
    qpow = random.randint(2, 4)
    r = random.randint(1, 3)
    coeff_raw = (a * b) / c
    power = p + qpow - r
    coeff = coeff_raw
    while coeff >= 10:
        coeff /= 10
        power += 1
    while coeff < 1:
        coeff *= 10
        power -= 1
    q = rf"Simplify \(\frac{{({a} \times 10^{p})({b} \times 10^{qpow})}}{{{c} \times 10^{r}}}\), giving your answer in standard form."
    s = rf"Coefficients: ({a} × {b}) ÷ {c} = {coeff_raw}. Powers: {p} + {qpow} − {r} = {p+qpow-r}. Therefore the answer is <strong>{_number_fmt(coeff)} × 10^{power}</strong>."
    hint = "Deal with coefficients and powers of 10 separately, then adjust the coefficient to be between 1 and 10."
    return q, s, hint, 4, _number_standard_form_answer(coeff, power)


def _number_diff_error_interval_product():
    a = random.randint(20, 80)
    b = random.randint(5, 30)
    min_prod = (a - 0.5) * (b - 0.5)
    max_prod = (a + 0.5) * (b + 0.5)
    q = rf"Two measurements are {a} cm and {b} cm, each rounded to the nearest centimetre. Find the minimum and maximum possible product of the measurements."
    s = rf"Use lower bounds for the minimum and upper bounds for the maximum. Minimum = {a-0.5} × {b-0.5} = <strong>{_number_fmt(min_prod)} cm²</strong>. Maximum = {a+0.5} × {b+0.5} = <strong>{_number_fmt(max_prod)} cm²</strong>."
    hint = "For a product of positive measurements, minimum uses both lower bounds and maximum uses both upper bounds."
    return q, s, hint, 4, _number_pair_answer(min_prod, max_prod, 'Minimum', 'Maximum', 'to')


def _number_diff_bounds_density():
    mass = random.randint(40, 120)
    volume = random.randint(8, 30)
    max_density = (mass + 0.5) / (volume - 0.5)
    min_density = (mass - 0.5) / (volume + 0.5)
    q = rf"Mass is {mass} g and volume is {volume} cm³, both to the nearest whole unit. Find the lower and upper bounds for density in g/cm³."
    s = rf"Density = mass ÷ volume. Minimum density uses lowest mass and highest volume: ({mass-0.5}) ÷ ({volume+0.5}) = <strong>{min_density:.3f}</strong>. Maximum density uses highest mass and lowest volume: ({mass+0.5}) ÷ ({volume-0.5}) = <strong>{max_density:.3f}</strong>."
    hint = "For a fraction, the maximum uses a large numerator and small denominator."
    return q, s, hint, 4, _number_pair_answer(round(min_density, 3), round(max_density, 3), 'Minimum density', 'Maximum density', 'to')


def _number_diff_fractional_indices():
    root = random.randint(4, 20)
    base = root * root
    q = rf"Evaluate \({base}^{{1/2}}\)."
    s = rf"A power of \(1/2\) means square root. Therefore \({base}^{{1/2}} = \sqrt{{{base}}} = \)<strong>{root}</strong>."
    hint = "The index 1/2 means square root."
    return q, s, hint, 1, root
def _number_diff_negative_indices():
    base = random.randint(2, 9)
    power = random.choice([1, 2, 3])
    denom = base ** power
    q = rf"Evaluate \({base}^{{-{power}}}\)."
    s = rf"A negative index means reciprocal: \({base}^{{-{power}}} = \frac{{1}}{{{base}^{power}}} = \)<strong>\(\frac{{1}}{{{denom}}}\)</strong>."
    hint = "Move the power to the denominator to make the index positive."
    return q, s, hint, 2, f"1/{denom}"


def _number_diff_zero_negative_combined():
    a = random.randint(2, 9)
    b = random.randint(2, 6)
    ans_num = 1
    ans_den = b * b
    q = rf"Simplify \({a}^0 \times {b}^{{-2}}\)."
    s = rf"\({a}^0 = 1\), and \({b}^{{-2}} = \frac{{1}}{{{b}^2}} = \frac{{1}}{{{ans_den}}}\). So the answer is <strong>\(\frac{{1}}{{{ans_den}}}\)</strong>."
    hint = "Any non-zero number to the power 0 is 1; a negative index creates a reciprocal."
    return q, s, hint, 2, f"1/{ans_den}"


def _number_diff_recurring_decimal_fraction():
    dec, frac = _number_recurring_decimal_case()
    q = rf"Write {dec} as a fraction in its simplest form."
    s = rf"This is a recurring decimal. Using the standard recurring-decimal method gives <strong>{frac}</strong>."
    hint = "Let x equal the recurring decimal, multiply to line up the repeating part, then subtract."
    return q, s, hint, 3


def _number_diff_surds_estimate():
    n, lower, _ = _number_non_square_n(4, 14)
    upper = lower + 1
    q = rf"Without using a calculator, show which two consecutive integers \(\sqrt{{{n}}}\) lies between."
    s = (
        rf"Compare nearby squares: \({lower}^2 = {lower**2}\) and \({upper}^2 = {upper**2}\). "
        rf"Since \({lower**2} &lt; {n} &lt; {upper**2}\), "
        rf"\(\sqrt{{{n}}}\) lies between <strong>{lower} and {upper}</strong>."
    )
    hint = "Compare the number with nearby square numbers."
    return q, s, hint, 2, _number_pair_answer(lower, upper, 'Lower integer', 'Upper integer', 'to')


def _number_diff_hcf_lcm_prime_factors():
    a, b, hcf, lcm = _number_random_hcf_lcm_pair()
    q = rf"Find the HCF and LCM of {a} and {b}."
    s = rf"Using prime factors or systematic listing, the highest common factor is <strong>{hcf}</strong> and the lowest common multiple is <strong>{lcm}</strong>. Check: HCF × LCM = {hcf*lcm}, and {a} × {b} = {a*b}."
    hint = "Prime factor form is the most reliable method for larger numbers."
    return q, s, hint, 4, _number_pair_answer(hcf, lcm, 'HCF', 'LCM')


def _number_diff_percentage_error():
    estimate = random.choice([48, 96, 125, 240, 360])
    actual = estimate + random.choice([-12, -8, -5, 6, 10, 15])
    error = abs(estimate - actual)
    pct_error = error / actual * 100
    q = rf"An estimate is {estimate}, but the actual value is {actual}. Find the percentage error to 1 decimal place."
    s = rf"Percentage error = \(\frac{{\text{{error}}}}{{\text{{actual}}}} \times 100\). Error = |{estimate} − {actual}| = {error}. So percentage error = {error} ÷ {actual} × 100 = <strong>{pct_error:.1f}%</strong>."
    hint = "Use absolute error divided by actual value, then multiply by 100."
    return q, s, hint, 3, round(pct_error, 1)
def _number_diff_best_value():
    from generators.shared.utils import compare_choice_payload
    items1 = random.randint(3, 8)
    price1 = round(random.uniform(1.5, 6.0), 2)
    items2 = random.randint(4, 10)
    price2 = round(random.uniform(2.0, 8.0), 2)
    unit1 = price1 / items1
    unit2 = price2 / items2
    best = 'Pack A' if unit1 < unit2 else 'Pack B'
    label_a = f'Pack A ({items1} items for £{price1:.2f})'
    label_b = f'Pack B ({items2} items for £{price2:.2f})'
    correct = 'A' if best == 'Pack A' else 'B'
    q = rf"Pack A contains {items1} items for £{price1:.2f}. Pack B contains {items2} items for £{price2:.2f}. Which pack is better value?"
    s = rf"Compare unit prices. Pack A: £{price1:.2f} ÷ {items1} = £{unit1:.2f} per item. Pack B: £{price2:.2f} ÷ {items2} = £{unit2:.2f} per item. The better value is <strong>{best}</strong>."
    hint = "Find the cost per one item for each pack."
    return q, s, hint, 3, compare_choice_payload(label_a, label_b, correct)


def _number_diff_iterative_bounds():
    n, _, _ = _number_non_square_n(3, 12)
    lower = math.floor(math.sqrt(n) * 10) / 10
    upper = lower + 0.1
    q = rf"Find the two consecutive tenths that \(\sqrt{{{n}}}\) lies between."
    s = (
        rf"Square consecutive tenths near \(\sqrt{{{n}}}\): "
        rf"\({lower:.1f}^2 = {lower**2:.2f}\) and \({upper:.1f}^2 = {upper**2:.2f}\). "
        rf"Since \({lower**2:.2f} &lt; {n} &lt; {upper**2:.2f}\), "
        rf"\(\sqrt{{{n}}}\) lies between <strong>{lower:.1f} and {upper:.1f}</strong>."
    )
    hint = "Square nearby decimal values until the original number is between them."
    return q, s, hint, 3, _number_pair_answer(lower, upper, 'Lower bound', 'Upper bound', 'to')


# ---------- DIFFICULT (extra formats) ----------

def _number_diff_bounds_speed():
    """Maximum and minimum speed from bounded distance and time."""
    dist = random.randint(80, 200)
    hours = random.choice([2.0, 2.5, 3.0, 4.0])
    max_speed = (dist + 0.5) / (hours - 0.05)
    min_speed = (dist - 0.5) / (hours + 0.05)
    q = (
        rf"A journey of {dist} km (nearest km) takes {hours} hours (nearest 0.1 h). "
        rf"Find the maximum and minimum possible average speed in km/h."
    )
    s = (
        rf"Maximum speed uses upper bound distance and lower bound time:<br>"
        rf"({dist + 0.5}) ÷ ({hours - 0.05:.1f}) = <strong>{max_speed:.2f} km/h</strong><br>"
        rf"Minimum speed uses lower bound distance and upper bound time:<br>"
        rf"({dist - 0.5}) ÷ ({hours + 0.05:.1f}) = <strong>{min_speed:.2f} km/h</strong>"
    )
    hint = "Speed = distance ÷ time. Fastest speed uses the largest distance and shortest time."
    return q, s, hint, 4, _number_pair_answer(round(min_speed, 2), round(max_speed, 2), 'Minimum speed', 'Maximum speed', 'to')


def _number_diff_find_index_n():
    """Find the index in a simple exponential equation."""
    base = random.randint(2, 9)
    n = random.randint(3, 9)
    value = base ** n
    q = rf"Find the value of \(n\) if \({base}^{{n}} = {value}\)."
    s = (
        rf"Try powers of {base}:<br>"
        rf"{base}¹ = {base}, {base}² = {base**2}, …, {base}^{n} = {value}<br>"
        rf"So <strong>n = {n}</strong>"
    )
    hint = "Write out powers of the base until you reach the value on the right-hand side."
    return q, s, hint, 2, n
def _number_diff_salary_percentage_chain():
    """Two-step percentage change in context (not just repeated generic)."""
    salary = random.randint(180, 450) * 100
    rise = random.randint(2, 10)
    tax = random.randint(18, 28)
    after_rise = salary * (1 + rise / 100)
    after_tax = after_rise * (1 - tax / 100)
    q = (
        rf"A salary of £{salary} is increased by {rise}% and then income tax of {tax}% is deducted "
        rf"from the new salary. Find the amount received after tax, to the nearest pound."
    )
    s = (
        rf"After rise: {salary} × {1 + rise/100} = £{_number_fmt(after_rise)}<br>"
        rf"After tax: £{_number_fmt(after_rise)} × {1 - tax/100} = <strong>£{round(after_tax)}</strong>"
    )
    hint = "Apply each percentage change with its own multiplier, in the order given."
    return q, s, hint, 4, round(after_tax)
def _number_diff_sf_population_difference():
    """Subtract two populations given in standard form."""
    c1 = round(random.uniform(2.5, 8.5), 1)
    p1 = random.randint(5, 7)
    c2 = round(random.uniform(1.2, 4.8), 1)
    p2 = p1 - 1
    pop1 = c1 * (10 ** p1)
    pop2 = c2 * (10 ** p2)
    diff = pop1 - pop2
    coeff = diff / (10 ** p2)
    power = p2
    while coeff >= 10:
        coeff /= 10
        power += 1
    while coeff < 1 and coeff > 0:
        coeff *= 10
        power -= 1
    q = (
        rf"Town A has population \({c1} \times 10^{{{p1}}}\) and Town B has population "
        rf"\({c2} \times 10^{{{p2}}}\). Find the difference (A − B) in standard form."
    )
    s = (
        rf"Convert or subtract: {c1}×10^{p1} − {c2}×10^{p2} = {diff:.0f}<br>"
        rf"In standard form: <strong>{_number_fmt(coeff)} × 10^{power}</strong>"
    )
    hint = "Subtract the ordinary numbers (or align powers of 10), then write the result in standard form."
    return q, s, hint, 4, _number_standard_form_answer(coeff, power)


# ---------- MCQ (18) ----------

def number_mcq(mcq_type=None):
    if mcq_type is None:
        mcq_type = random.randint(1, 18)

    if mcq_type == 1:
        n = random.randint(2000, 9000)
        hundreds = (n // 100) % 10
        correct = hundreds * 100
        q = rf"What is the value of the hundreds digit in {n}?"
        options, correct_letter = _number_mcq_options(correct, [hundreds, hundreds * 10, hundreds * 1000])
        hint = "The hundreds digit is worth digit × 100."

    elif mcq_type == 2:
        n = round(random.uniform(4, 30), 3)
        correct = round(n, 1)
        q = rf"Round {n} to 1 decimal place."
        options, correct_letter = _number_mcq_options(correct, [round(n, 2), int(n), round(n + 0.1, 1)])
        hint = "Keep one digit after the decimal point and look at the next digit."

    elif mcq_type == 3:
        n = random.randint(1200, 9800)
        correct = _number_sf_value(n, 2)
        q = rf"Round {n} to 2 significant figures."
        options, correct_letter = _number_mcq_options(correct, [round(n, -1), round(n, -3), int(str(n)[:2])])
        hint = "Start counting at the first non-zero digit."

    elif mcq_type == 4:
        pct = random.choice([10, 20, 25, 50])
        amount = random.choice([80, 120, 160, 240])
        correct = _number_fmt(amount * pct / 100)
        q = rf"What is {pct}% of {amount}?"
        options, correct_letter = _number_mcq_options(correct, [_number_fmt(amount + pct), _number_fmt(amount - pct), _number_fmt(pct / amount * 100)])
        hint = "Percentage means out of 100."

    elif mcq_type == 5:
        amount = random.choice([100, 200, 500])
        pct = random.choice([10, 15, 20])
        correct = _number_fmt(amount * (1 + pct/100))
        q = rf"Increase {amount} by {pct}%."
        options, correct_letter = _number_mcq_options(correct, [_number_fmt(amount * pct/100), _number_fmt(amount * (1 - pct/100)), _number_fmt(amount + pct)])
        hint = "Use the multiplier 1 + percentage/100."

    elif mcq_type == 6:
        amount = random.choice([100, 200, 500])
        pct = random.choice([10, 15, 20])
        correct = _number_fmt(amount * (1 - pct/100))
        q = rf"Decrease {amount} by {pct}%."
        options, correct_letter = _number_mcq_options(correct, [_number_fmt(amount * pct/100), _number_fmt(amount * (1 + pct/100)), _number_fmt(amount - pct)])
        hint = "Use the multiplier 1 - percentage/100."

    elif mcq_type == 7:
        coeff = random.randint(2, 9)
        power = random.randint(3, 6)
        ordinary = coeff * (10 ** power)
        q = rf"Write {ordinary} in standard form."
        correct = rf"{coeff} × 10^{power}"
        options, correct_letter = _number_mcq_options(correct, [rf"{coeff} × 10^{power-1}", rf"{coeff*10} × 10^{power-1}", rf"0.{coeff} × 10^{power+1}"])
        hint = "Standard form has a front number from 1 up to but not including 10."

    elif mcq_type == 8:
        coeff = random.randint(2, 9)
        power = random.randint(2, 5)
        correct = _number_fmt(coeff * (10 ** -power), 7)
        q = rf"Write \({coeff} \times 10^{{-{power}}}\) as an ordinary number."
        options, correct_letter = _number_mcq_options(correct, [_number_fmt(coeff * 10**power), _number_fmt(coeff * 10**-(power-1), 7), _number_fmt(coeff / power, 4)])
        hint = "A negative power moves the decimal point left."

    elif mcq_type == 9:
        base = random.randint(2, 9)
        a = random.randint(2, 5)
        b = random.randint(2, 5)
        correct = rf"{base}^{a+b}"
        q = rf"Simplify \({base}^{a} \times {base}^{b}\)."
        options, correct_letter = _number_mcq_options(correct, [rf"{base}^{a*b}", rf"{base}^{a-b}", rf"{base*base}^{a+b}"])
        hint = "When multiplying powers with the same base, add indices."

    elif mcq_type == 10:
        base = random.randint(2, 9)
        a = random.randint(5, 10)
        b = random.randint(1, 4)
        correct = rf"{base}^{a-b}"
        q = rf"Simplify \({base}^{a} \div {base}^{b}\)."
        options, correct_letter = _number_mcq_options(correct, [rf"{base}^{a+b}", rf"{base}^{a*b}", rf"{base-base}^{a-b}"])
        hint = "When dividing powers with the same base, subtract indices."

    elif mcq_type == 11:
        n = random.randint(20, 90)
        correct = f"{n-0.5} ≤ x < {n+0.5}"
        q = rf"A number x is rounded to {n} to the nearest whole number. What is the error interval?"
        options, correct_letter = _number_mcq_options(correct, [f"{n-1} ≤ x < {n+1}", f"{n} ≤ x < {n+1}", f"{n-0.05} ≤ x < {n+0.05}"])
        hint = "Nearest whole number means half a unit below and above."

    elif mcq_type == 12:
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        p = random.randint(2, 5)
        qpow = random.randint(2, 5)
        raw = a * b
        power = p + qpow
        coeff = raw
        if coeff >= 10:
            coeff /= 10
            power += 1
        correct = rf"{_number_fmt(coeff)} × 10^{power}"
        q = rf"Calculate \(({a} \times 10^{p})({b} \times 10^{qpow})\) in standard form."
        options, correct_letter = _number_mcq_options(correct, [rf"{raw} × 10^{p+qpow}", rf"{_number_fmt(coeff)} × 10^{p*qpow}", rf"{_number_fmt(coeff)} × 10^{power-1}"])
        hint = "Multiply coefficients and add powers, then adjust to standard form."

    elif mcq_type == 13:
        base = random.choice([4, 9, 16, 25, 36, 49, 64, 81])
        correct = int(math.sqrt(base))
        q = rf"Evaluate \({base}^{{1/2}}\)."
        options, correct_letter = _number_mcq_options(
            correct,
            [
                correct + 1,
                correct - 1 if correct > 1 else correct + 2,
                (correct + 1) ** 2,
            ],
        )
        hint = "A power of 1/2 means square root."

    elif mcq_type == 14:
        base = random.randint(2, 8)
        power = random.choice([1, 2, 3])
        correct = rf"1/{base**power}"
        q = rf"Evaluate \({base}^{{-{power}}}\)."
        options, correct_letter = _number_mcq_options(correct, [base**power, -base**power, rf"1/{base*power}"])
        hint = "A negative index means reciprocal."

    elif mcq_type == 15:
        estimate = random.choice([48, 96, 125, 240])
        actual = estimate + random.choice([6, 8, 12])
        error = abs(estimate - actual)
        correct = f"{(error/actual*100):.1f}%"
        q = rf"An estimate is {estimate} and the actual value is {actual}. What is the percentage error to 1 decimal place?"
        options, correct_letter = _number_mcq_options(correct, [f"{(error/estimate*100):.1f}%", f"{error}%", f"{(actual/estimate*100):.1f}%"])
        hint = "Percentage error = absolute error ÷ actual value × 100."

    elif mcq_type == 16:
        a, b, hcf = random.choice([(48, 72, 24), (60, 84, 12), (90, 150, 30)])
        correct = hcf
        q = rf"What is the HCF of {a} and {b}?"
        options, correct_letter = _number_mcq_options(correct, [a // hcf, hcf * 2, a * b // hcf])
        hint = "HCF is the largest number that divides both numbers exactly."

    elif mcq_type == 17:
        n, coeff, power = random.choice([(0.0038, 3.8, -3), (0.00052, 5.2, -4), (0.00071, 7.1, -4)])
        correct = rf"{coeff} × 10^{power}"
        q = rf"Write {n} in standard form."
        options, correct_letter = _number_mcq_options(
            correct,
            [rf"{coeff} × 10^{power + 1}", rf"{coeff * 10} × 10^{power - 1}", rf"{coeff / 10} × 10^{power + 1}"],
        )
        hint = "Move the decimal point until the front number is between 1 and 10."

    else:
        principal = random.choice([500, 800, 1000])
        rate = random.choice([3, 4, 5])
        years = 2
        correct = _number_fmt(principal * ((1 + rate / 100) ** years), 2)
        q = (
            rf"£{principal} is invested at {rate}% compound interest per year for {years} years. "
            rf"What is the final amount to the nearest penny?"
        )
        options, correct_letter = _number_mcq_options(
            correct,
            [
                _number_fmt(principal * (1 + rate / 100 * years), 2),
                _number_fmt(principal * (1 + rate / 100), 2),
                _number_fmt(principal * ((1 + rate / 100) ** (years + 1)), 2),
            ],
        )
        hint = "Compound interest multiplies by (1 + r/100) once per year, not just once in total."

    s = f"The correct option is <strong>{correct_letter}</strong> ({correct}).\n\n{hint}"
    return q, s, hint, 1, options, correct_letter




def _number_raw(value, dp=2):
    """Canonical numeric string for typed answer checking."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        return _number_fmt(value, dp)
    return str(value)


def _number_standard_form_answer(coefficient, power):
    return {'type': 'standard_form', 'coefficient': coefficient, 'power': int(power)}


def _number_pair_answer(val_a, val_b, label_a='Answer 1', label_b='Answer 2', sep='and'):
    return {
        'type': 'number_pair',
        'values': (val_a, val_b),
        'label_a': label_a,
        'label_b': label_b,
        'sep': sep,
    }


def _number_list_answer(values):
    return {'type': 'number_list', 'values': tuple(values)}


def _number_power_answer(base, exponent):
    return {'type': 'power', 'base': int(base), 'exponent': int(exponent)}


def _number_standard_form_raw(coefficient, power):
    return f"{_number_fmt(coefficient)}|{int(power)}"


def _number_power_raw(base, exponent):
    return f"{int(base)}|{int(exponent)}"


def _number_problem_from_output(out, difficulty):
    choice = problem_from_choice_output(out, difficulty, 'gcse', 'maths', 'number')
    if choice:
        return choice
    if len(out) >= 5:
        q, s, hint, marks, raw = out[:5]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'standard_form':
                raw_s = _number_standard_form_raw(raw['coefficient'], raw['power'])
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'number',
                    correct_answer_raw=raw_s,
                    answer_type='standard_form',
                    answer_format_hint='Coefficient and power of 10',
                )
            if raw_type == 'number_pair':
                val_a, val_b = raw['values']
                raw_s = f"{_number_raw(val_a)}|{_number_raw(val_b)}"
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'number',
                    correct_answer_raw=raw_s,
                    answer_type='number_pair',
                    answer_labels=[raw['label_a'], raw['label_b']],
                    answer_pair_sep=raw.get('sep', 'and'),
                )
            if raw_type == 'number_list':
                raw_s = ','.join(_number_raw(v) for v in raw['values'])
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'number',
                    correct_answer_raw=raw_s,
                    answer_type='number_list',
                    answer_format_hint='Enter numbers separated by commas',
                )
            if raw_type == 'power':
                raw_s = _number_power_raw(raw['base'], raw['exponent'])
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'number',
                    correct_answer_raw=raw_s,
                    answer_type='power',
                    answer_format_hint='Base and index',
                )
        if isinstance(raw, str):
            fraction_hint = 'Enter a number or fraction (e.g. 1/16)'
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'maths', 'number',
                correct_answer_raw=raw,
                answer_type='number',
                answer_format_hint=fraction_hint if '/' in raw else 'Enter a number',
            )
        if isinstance(raw, (int, float)):
            raw_s = _number_raw(raw)
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'maths', 'number',
                correct_answer_raw=raw_s,
                answer_type='number',
                answer_format_hint='Enter a number',
            )
    q, s, hint, marks = out[:4]
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'number')

# ---------- VARIANTS FUNCTION ----------

def gcse_number_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_fn(
            number_mcq, 'number', difficulty, slot_param='mcq_type'
        )

    if difficulty == 'foundational':
        pool = [
            _number_found_place_value_digit,
            _number_found_decimal_place_value,
            _number_found_compare_decimals,
            _number_found_order_decimals,
            _number_found_round_nearest_10_100,
            _number_found_round_decimal_places,
            _number_found_significant_figures_simple,
            _number_found_negative_add_subtract,
            _number_found_multiply_by_power_10,
            _number_found_square_cube,
            _number_found_percentage_of_amount,
            _number_found_fraction_of_amount,
            _number_found_estimate_simple,
            _number_found_standard_form_large,
            _number_found_indices_multiply,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _number_inter_standard_form_small,
            _number_inter_standard_form_to_ordinary,
            _number_inter_standard_form_multiply,
            _number_inter_standard_form_divide,
            _number_inter_percentage_increase,
            _number_inter_percentage_decrease,
            _number_inter_reverse_percentage_increase,
            _number_inter_reverse_percentage_decrease,
            _number_inter_repeated_percentage_change,
            _number_inter_error_interval_whole,
            _number_inter_error_interval_tenth,
            _number_inter_bounds_area,
            _number_inter_index_division,
            _number_inter_index_power_of_power,
            _number_inter_prime_factor_product,
            _number_inter_calculator_estimate_fraction,
            _number_inter_sf_which_larger,
            _number_inter_vat_word_problem,
            _number_inter_calculate_to_sf,
            _number_inter_share_ratio,
        ]
    elif difficulty == 'difficult':
        pool = [
            _number_diff_compound_interest,
            _number_diff_depreciation,
            _number_diff_reverse_compound,
            _number_diff_standard_form_context,
            _number_diff_standard_form_mixed_operations,
            _number_diff_error_interval_product,
            _number_diff_bounds_density,
            _number_diff_fractional_indices,
            _number_diff_negative_indices,
            _number_diff_zero_negative_combined,
            _number_diff_recurring_decimal_fraction,
            _number_diff_surds_estimate,
            _number_diff_hcf_lcm_prime_factors,
            _number_diff_percentage_error,
            _number_diff_best_value,
            _number_diff_iterative_bounds,
            _number_diff_bounds_speed,
            _number_diff_find_index_n,
            _number_diff_salary_percentage_chain,
            _number_diff_sf_population_difference,
        ]
    else:
        found = random.sample([
            _number_found_place_value_digit,
            _number_found_decimal_place_value,
            _number_found_compare_decimals,
            _number_found_order_decimals,
            _number_found_round_nearest_10_100,
            _number_found_round_decimal_places,
            _number_found_significant_figures_simple,
            _number_found_negative_add_subtract,
            _number_found_multiply_by_power_10,
            _number_found_square_cube,
            _number_found_percentage_of_amount,
            _number_found_fraction_of_amount,
            _number_found_estimate_simple,
            _number_found_standard_form_large,
            _number_found_indices_multiply,
        ], 4)
        inter = random.sample([
            _number_inter_standard_form_small,
            _number_inter_standard_form_to_ordinary,
            _number_inter_standard_form_multiply,
            _number_inter_standard_form_divide,
            _number_inter_percentage_increase,
            _number_inter_percentage_decrease,
            _number_inter_reverse_percentage_increase,
            _number_inter_reverse_percentage_decrease,
            _number_inter_repeated_percentage_change,
            _number_inter_error_interval_whole,
            _number_inter_error_interval_tenth,
            _number_inter_bounds_area,
            _number_inter_index_division,
            _number_inter_index_power_of_power,
            _number_inter_prime_factor_product,
            _number_inter_calculator_estimate_fraction,
            _number_inter_sf_which_larger,
            _number_inter_vat_word_problem,
            _number_inter_calculate_to_sf,
            _number_inter_share_ratio,
        ], 4)
        diff = random.sample([
            _number_diff_compound_interest,
            _number_diff_depreciation,
            _number_diff_reverse_compound,
            _number_diff_standard_form_context,
            _number_diff_standard_form_mixed_operations,
            _number_diff_error_interval_product,
            _number_diff_bounds_density,
            _number_diff_fractional_indices,
            _number_diff_negative_indices,
            _number_diff_zero_negative_combined,
            _number_diff_recurring_decimal_fraction,
            _number_diff_surds_estimate,
            _number_diff_hcf_lcm_prime_factors,
            _number_diff_percentage_error,
            _number_diff_best_value,
            _number_diff_iterative_bounds,
            _number_diff_bounds_speed,
            _number_diff_find_index_n,
            _number_diff_salary_percentage_chain,
            _number_diff_sf_population_difference,
        ], 2)
        return found + inter + diff

    return select_tier_variants(pool)


# ---------- MAIN GENERATOR ----------

def gcse_number(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_number_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'number',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_number_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    out = variant()
    return _number_problem_from_output(out, difficulty)



# ------------------------------------------------------------
# GCSE Maths – Ratio/Proportion, Probability, Statistics
# ------------------------------------------------------------


def _fmt_num(x, dp=2):
    if isinstance(x, int) or abs(x - int(x)) < 1e-10:
        return str(int(x))
    return f"{x:.{dp}f}".rstrip('0').rstrip('.')


def _simp_frac(a, b):
    g = math.gcd(abs(a), abs(b))
    return a // g, b // g


def _mcq_options(correct, distractors):
    correct = str(correct)
    choices = [correct]
    seen = {correct}
    for d in distractors:
        d = str(d)
        if d not in seen:
            choices.append(d)
            seen.add(d)
    pad_pool = ["0", "1", "1/2", "10", "100", "0.1", "-1"]
    i = 0
    while len(choices) < 4:
        cand = pad_pool[i % len(pad_pool)]
        i += 1
        if cand not in seen:
            choices.append(cand)
            seen.add(cand)
    choices = choices[:4]
    random.shuffle(choices)
    letters = ['A', 'B', 'C', 'D']
    return [f"{letters[i]}  {choices[i]}" for i in range(4)], letters[choices.index(correct)]

# ============================================================
# RATIO AND PROPORTION
# ============================================================


def _ratio_random_three_parts(lo=2, hi=8):
    while True:
        a, b, c = random.randint(lo, hi), random.randint(lo, hi), random.randint(lo, hi)
        if len({a, b, c}) >= 2:
            return a, b, c


def _ratio_random_two_part(lo=2, hi=9):
    a, b = random.randint(lo, hi), random.randint(lo, hi)
    while a == b and random.random() < 0.4:
        b = random.randint(lo, hi)
    return a, b


def _ratio_fraction_answer(num, den):
    g = math.gcd(int(num), int(den))
    n, d = int(num) // g, int(den) // g
    if d == 1:
        return n
    return {'type': 'fraction', 'value': f'{n}/{d}'}


def _ratio_simplify():
    a, b = random.randint(2, 12), random.randint(2, 12)
    k = random.randint(2, 9)
    x, y = a * k, b * k
    g = math.gcd(x, y)
    q = rf"Simplify the ratio {x}:{y}."
    s = rf"Divide both parts by the highest common factor, {g}: {x} ÷ {g} = {x//g} and {y} ÷ {g} = {y//g}. Answer: <strong>{x//g}:{y//g}</strong>."
    return q, s, "Divide every part by the same highest common factor.", 1, _ratio_answer(x // g, y // g)


def _ratio_equivalent():
    a, b, k = random.randint(2, 8), random.randint(2, 9), random.randint(2, 7)
    q = rf"Write an equivalent ratio to {a}:{b} by multiplying each part by {k}."
    s = rf"Multiply both parts by {k}: {a}×{k} = {a*k} and {b}×{k} = {b*k}. Answer: <strong>{a*k}:{b*k}</strong>."
    return q, s, "Equivalent ratios are made by multiplying each part by the same number.", 1, _ratio_answer(a * k, b * k, exact=True)


def _ratio_share_two():
    a, b = random.randint(2, 7), random.randint(2, 7)
    unit = random.randint(5, 30)
    total = (a + b) * unit
    q = rf"Share £{total} in the ratio {a}:{b}."
    s = rf"Total parts = {a}+{b} = {a+b}. One part = {total} ÷ {a+b} = {unit}. Shares are {a}×{unit} = <strong>£{a*unit}</strong> and {b}×{unit} = <strong>£{b*unit}</strong>."
    hint = "Add the parts first, then find one part."
    return q, s, hint, 3, _number_pair_answer(a * unit, b * unit, 'First share (£)', 'Second share (£)')


def _ratio_share_three():
    a, b, c = random.randint(1, 5), random.randint(2, 6), random.randint(2, 7)
    unit = random.randint(4, 20)
    total = (a + b + c) * unit
    q = rf"Share {total} sweets in the ratio {a}:{b}:{c}."
    s = rf"Total parts = {a+b+c}. One part = {total} ÷ {a+b+c} = {unit}. The shares are <strong>{a*unit}, {b*unit}, {c*unit}</strong>."
    hint = "For a three-part ratio, add all three parts before dividing."
    return q, s, hint, 3, _ratio_fields_answer(
        (a * unit, b * unit, c * unit),
        ('First share', 'Second share', 'Third share'),
    )


def _ratio_fraction_of_total():
    a, b = random.randint(2, 8), random.randint(2, 8)
    total_parts = a + b
    g = math.gcd(a, total_parts)
    frac = _ratio_fraction_answer(a, total_parts)
    q = (
        rf"The ratio of boys to girls in a class is {a}:{b}. "
        rf"What fraction of the students are boys? Give your answer in simplest form."
    )
    s = (
        rf"Total parts = {a} + {b} = {total_parts}. "
        rf"Boys are {a} out of {total_parts} parts: "
        rf"<strong>{a // g}/{total_parts // g}</strong>."
    )
    return q, s, "Write one part as a fraction of the total parts, then simplify.", 2, frac


def _ratio_three_part_as_fraction():
    a, b, c = random.randint(1, 5), random.randint(2, 6), random.randint(2, 7)
    part = random.choice(('first', 'second', 'third'))
    nums = (a, b, c)
    idx = ('first', 'second', 'third').index(part)
    num = nums[idx]
    total_parts = a + b + c
    g = math.gcd(num, total_parts)
    q = (
        rf"An amount is shared in the ratio {a}:{b}:{c}. "
        rf"What fraction of the total is the <strong>{part}</strong> share? "
        rf"Give your answer in simplest form."
    )
    s = (
        rf"Total parts = {total_parts}. The {part} share is {num} out of {total_parts}: "
        rf"<strong>{num // g}/{total_parts // g}</strong>."
    )
    return q, s, "Add all ratio parts for the denominator, then simplify.", 2, _ratio_fraction_answer(num, total_parts)


def _ratio_find_missing_part():
    a, b = random.randint(2, 8), random.randint(2, 9)
    known = a * random.randint(4, 15)
    multiplier = known // a
    missing = b * multiplier
    q = rf"The ratio A:B is {a}:{b}. If A = {known}, find B."
    s = rf"A has been multiplied by {multiplier}, because {a}×{multiplier} = {known}. Therefore B = {b}×{multiplier} = <strong>{missing}</strong>."
    return q, s, "Find the scale factor from the known part, then apply it to the other part.", 2, missing


def _ratio_unitary_cost():
    items = random.randint(3, 12)
    cost_each = round(random.uniform(0.75, 5.50), 2)
    new_items = random.randint(5, 20)
    total = items * cost_each
    ans = new_items * cost_each
    q = rf"{items} notebooks cost £{total:.2f}. How much do {new_items} notebooks cost?"
    s = rf"One notebook costs £{total:.2f} ÷ {items} = £{cost_each:.2f}. Therefore {new_items} notebooks cost {new_items}×£{cost_each:.2f} = <strong>£{ans:.2f}</strong>."
    return q, s, "Find the cost of one item first.", 2, _number_raw(ans)


def _ratio_recipe_scale():
    people1 = random.randint(2, 8)
    people2 = random.randint(people1 + 2, people1 + 12)
    ingredient = random.choice([80, 100, 120, 150, 180, 200, 240, 250, 300, 360])
    ans = ingredient * people2 / people1
    q = rf"A recipe uses {ingredient} g of flour for {people1} people. How much flour is needed for {people2} people?"
    s = rf"Scale factor = {people2} ÷ {people1} = {_fmt_num(people2/people1)}. Flour needed = {ingredient} × {_fmt_num(people2/people1)} = <strong>{_fmt_num(ans)} g</strong>."
    return q, s, "Multiply by the same scale factor as the number of people.", 2, _number_raw(ans)


def _ratio_best_buy():
    a_items, b_items = random.randint(3, 8), random.randint(4, 10)
    a_price, b_price = round(random.uniform(1.5, 6.5), 2), round(random.uniform(2.0, 8.0), 2)
    a_unit, b_unit = a_price/a_items, b_price/b_items
    best = "A" if a_unit < b_unit else "B"
    q = rf"Pack A has {a_items} items for £{a_price:.2f}. Pack B has {b_items} items for £{b_price:.2f}. Which is better value?"
    s = rf"Pack A: £{a_price:.2f} ÷ {a_items} = £{a_unit:.2f} per item. Pack B: £{b_price:.2f} ÷ {b_items} = £{b_unit:.2f} per item. Better value: <strong>Pack {best}</strong>."
    from generators.shared.utils import compare_choice_payload
    return q, s, "Compare the price for one item.", 3, compare_choice_payload('Pack A', 'Pack B', best)


def _ratio_scale_map():
    scale = random.choice([5000, 10000, 25000, 50000])
    cm = random.randint(3, 12)
    real_m = cm * scale / 100
    q = rf"A map has scale 1:{scale}. A distance on the map is {cm} cm. Find the real distance in metres."
    s = rf"1 cm represents {scale} cm. Real distance = {cm}×{scale} = {cm*scale} cm = <strong>{_fmt_num(real_m)} m</strong>."
    return q, s, "Use the scale, then convert centimetres to metres.", 3, _number_raw(real_m)


def _ratio_inverse_workers():
    workers1 = random.randint(3, 8)
    hours1 = random.randint(4, 12)
    workers2 = random.randint(2, 10)
    work = workers1 * hours1
    ans = work / workers2
    q = rf"{workers1} workers complete a job in {hours1} hours. Assuming the same rate, how long would {workers2} workers take?"
    s = rf"Total work = {workers1}×{hours1} = {work} worker-hours. Time for {workers2} workers = {work} ÷ {workers2} = <strong>{_fmt_num(ans)} hours</strong>."
    return q, s, "For inverse proportion, workers × time stays constant.", 3, _number_raw(ans)


def _ratio_direct_formula():
    k = random.randint(2, 8)
    x = random.randint(3, 12)
    q = rf"y is directly proportional to x. When x = {x}, y = {k*x}. Find y when x = {x+5}."
    s = rf"Since y = kx, k = {k*x} ÷ {x} = {k}. When x = {x+5}, y = {k}×{x+5} = <strong>{k*(x+5)}</strong>."
    return q, s, "Find the constant of proportionality first.", 3, k * (x + 5)


def _ratio_inverse_formula():
    k = random.randint(24, 120)
    x1 = random.choice([3, 4, 5, 6, 8])
    y1 = k / x1
    x2 = random.choice([2, 3, 4, 5, 6, 8, 10])
    q = rf"y is inversely proportional to x. When x = {x1}, y = {_fmt_num(y1)}. Find y when x = {x2}."
    s = rf"For inverse proportion, y = k/x. k = xy = {x1}×{_fmt_num(y1)} = {k}. When x = {x2}, y = {k} ÷ {x2} = <strong>{_fmt_num(k/x2)}</strong>."
    return q, s, "For inverse proportion, multiply x and y to find k.", 3, _number_raw(k / x2)


def _ratio_convert_units():
    a = random.randint(2, 12)
    b = random.randint(2, 15) * random.choice([10, 20, 25, 50])
    q = rf"Simplify the ratio {a} m : {b} cm."
    left_cm = a * 100
    g = math.gcd(left_cm, b)
    s = rf"Convert to the same units: {a} m = {left_cm} cm. Ratio = {left_cm}:{b}. Divide by {g}: <strong>{left_cm//g}:{b//g}</strong>."
    return q, s, "Convert both quantities to the same unit before simplifying.", 2, _ratio_answer(left_cm // g, b // g)


def _ratio_density_style():
    mass = random.randint(40, 200)
    volume = random.randint(5, 40)
    q = rf"A substance has mass {mass} g and volume {volume} cm³. Find its density."
    s = rf"Density = mass ÷ volume = {mass} ÷ {volume} = <strong>{_fmt_num(mass/volume)} g/cm³</strong>."
    return q, s, "Density is mass divided by volume.", 2, _number_raw(mass / volume)


def _ratio_abc_block(*parts):
    """Format sub-questions or solution steps as a), b), c)."""
    return "".join(
        f"<br><br><strong>{chr(ord('a') + i)})</strong> {text}"
        for i, text in enumerate(parts)
    )


def _ratio_raw(a, b):
    ai, bi = int(a), int(b)
    g = math.gcd(ai, bi)
    return f"{ai // g}|{bi // g}"


def _ratio_answer(a, b, exact=False):
    return {
        'type': 'ratio_exact' if exact else 'ratio',
        'a': int(a),
        'b': int(b),
    }


def _ratio_fields_answer(values, labels, field_types=None):
    payload = {
        'type': 'number_fields',
        'values': tuple(str(value) for value in values),
        'labels': tuple(labels),
    }
    if field_types:
        payload['field_types'] = tuple(field_types)
    return payload


# ---------- RATIO intermediate (multi-step, real-world, a/b/c) ----------

def _ratio_inter_cafe_ingredients():
    """Mixing drink ingredients in a given ratio."""
    r_m, r_s, r_e = _ratio_random_three_parts(2, 7)
    total_parts = r_m + r_s + r_e
    total_ml = total_parts * random.randint(15, 35)
    unit = total_ml // total_parts
    milk, syrup, espresso = r_m * unit, r_s * unit, r_e * unit
    intro = (
        rf"A café mixes milk, syrup and espresso in the ratio {r_m}:{r_s}:{r_e} "
        rf"to make {total_ml} ml of one batch."
    )
    q = intro + _ratio_abc_block(
        "Find the volume of milk in this batch.",
        "Find the volume of syrup.",
        "How much more milk than syrup is used?",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> Total parts = {total_parts}. One part = {total_ml} ÷ {total_parts} = {unit} ml.<br>"
        rf"Milk = {r_m} × {unit} = <strong>{milk} ml</strong><br><br>"
        rf"<strong>b)</strong> Syrup = {r_s} × {unit} = <strong>{syrup} ml</strong><br><br>"
        rf"<strong>c)</strong> Difference = {milk} − {syrup} = <strong>{milk - syrup} ml</strong>"
    )
    hint = "Add the ratio parts, find one part, then multiply each ingredient part."
    return q, s, hint, 4, _ratio_fields_answer(
        (milk, syrup, milk - syrup),
        ('Part (a): milk (ml)', 'Part (b): syrup (ml)', 'Part (c): difference (ml)'),
    )


def _ratio_inter_school_house_prize():
    """Share a prize fund between houses in a three-way ratio."""
    r1, r2, r3 = _ratio_random_three_parts(2, 8)
    unit = random.randint(35, 95)
    total = (r1 + r2 + r3) * unit
    first, second, third = r1 * unit, r2 * unit, r3 * unit
    intro = (
        rf"A school splits a £{total} prize fund between three houses in the ratio "
        rf"{r1}:{r2}:{r3} (1st : 2nd : 3rd place)."
    )
    q = intro + _ratio_abc_block(
        "Find the value of one part of the ratio.",
        "How much does the 1st-place house receive?",
        "How much more does 1st place receive than 3rd place?",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> Parts = {r1}+{r2}+{r3} = {r1+r2+r3}. "
        rf"One part = {total} ÷ {r1+r2+r3} = <strong>£{unit}</strong><br><br>"
        rf"<strong>b)</strong> 1st place = {r1} × {unit} = <strong>£{first}</strong><br><br>"
        rf"<strong>c)</strong> 3rd place = {r3} × {unit} = £{third}. "
        rf"Difference = {first} − {third} = <strong>£{first - third}</strong>"
    )
    hint = "Treat the ratio as parts of the whole fund."
    return q, s, hint, 4, _ratio_fields_answer(
        (unit, first, first - third),
        ('Part (a): one part (£)', 'Part (b): 1st place (£)', 'Part (c): difference (£)'),
    )


def _ratio_inter_map_hike():
    """Two legs of a walk on a map scale."""
    scale = random.choice([25000, 50000])
    cm1 = random.randint(5, 9)
    cm2 = round(random.uniform(3.5, 7.5), 1)
    m1 = cm1 * scale / 100
    m2 = cm2 * scale / 100
    km_total = (m1 + m2) / 1000
    intro = (
        rf"On a map with scale 1:{scale}, a hiker walks {cm1} cm east, then {cm2} cm north."
    )
    q = intro + _ratio_abc_block(
        "Find the real distance of the first leg in metres.",
        "Find the real distance of the second leg in metres.",
        "Find the total real distance in kilometres.",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> {cm1} cm × {scale} = {cm1*scale} cm = <strong>{_fmt_num(m1)} m</strong><br><br>"
        rf"<strong>b)</strong> {cm2} cm × {scale} = {cm2*scale:.0f} cm = <strong>{_fmt_num(m2)} m</strong><br><br>"
        rf"<strong>c)</strong> Total = {_fmt_num(m1)} + {_fmt_num(m2)} = {_fmt_num(m1+m2)} m = "
        rf"<strong>{_fmt_num(km_total)} km</strong>"
    )
    hint = "Multiply each map length by the scale, then convert cm to m and km."
    return q, s, hint, 4, _ratio_fields_answer(
        (_number_raw(m1), _number_raw(m2), _number_raw(km_total)),
        ('Part (a): first leg (m)', 'Part (b): second leg (m)', 'Part (c): total (km)'),
    )


def _ratio_inter_garden_compost():
    """Mix soil, compost and sand for a landscaping job."""
    r_soil, r_comp, r_sand = _ratio_random_three_parts(2, 7)
    total_parts = r_soil + r_comp + r_sand
    unit = random.randint(20, 55)
    total_kg = total_parts * unit
    soil, compost, sand = r_soil * unit, r_comp * unit, r_sand * unit
    intro = (
        rf"A gardener mixes soil, compost and sand in the ratio {r_soil}:{r_comp}:{r_sand}. "
        rf"The full mix weighs {total_kg} kg."
    )
    q = intro + _ratio_abc_block(
        "How many kilograms of compost are needed?",
        "How many kilograms of sand are needed?",
        "How much more soil than sand is used?",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> One part = {total_kg} ÷ {total_parts} = {unit} kg. "
        rf"Compost = {r_comp} × {unit} = <strong>{compost} kg</strong><br><br>"
        rf"<strong>b)</strong> Sand = {r_sand} × {unit} = <strong>{sand} kg</strong><br><br>"
        rf"<strong>c)</strong> Soil = {soil} kg. Difference = {total_kg} − {sand} - {compost} = <strong>{total_kg - sand - compost} kg</strong>"
    )
    hint = "Add ratio parts to find one share of the total mass."
    return q, s, hint, 4, _ratio_fields_answer(
        (compost, sand, total_kg - compost - sand),
        ('Part (a): compost (kg)', 'Part (b): sand (kg)', 'Part (c): difference (kg)'),
    )


# ---------- RATIO difficult (multi-step, real-world, a/b/c) ----------

def _ratio_diff_merge_classes():
    """Combine ratios from two classes to describe the whole year group."""
    a_b, a_g = _ratio_random_two_part(2, 6)
    b_b, b_g = _ratio_random_two_part(2, 6)
    students_a = (a_b + a_g) * random.randint(5, 12)
    students_b = (b_b + b_g) * random.randint(5, 12)
    boys_a = students_a * a_b // (a_b + a_g)
    girls_a = students_a - boys_a
    boys_b = students_b * b_b // (b_b + b_g)
    girls_b = students_b - boys_b
    total_boys = boys_a + boys_b
    total_girls = girls_a + girls_b
    g = math.gcd(total_boys, total_girls)
    intro = (
        rf"Class A has {students_a} students in the ratio boys : girls = {a_b}:{a_g}. "
        rf"Class B has {students_b} students in the ratio boys : girls = {b_b}:{b_g}."
    )
    q = intro + _ratio_abc_block(
        "How many girls are in Class A?",
        "How many boys are in Class B?",
        "Write the ratio boys : girls for the whole year group in its simplest form.",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> Girls in A = \(\frac{{{a_g}}}{{{a_b+a_g}}}\) × {students_a} = <strong>{girls_a}</strong><br><br>"
        rf"<strong>b)</strong> Boys in B = \(\frac{{{b_b}}}{{{b_b+b_g}}}\) × {students_b} = <strong>{boys_b}</strong><br><br>"
        rf"<strong>c)</strong> Total boys = {boys_a}+{boys_b} = {total_boys}, "
        rf"total girls = {girls_a}+{girls_b} = {total_girls}. "
        rf"Ratio = <strong>{total_boys//g}:{total_girls//g}</strong>"
    )
    hint = "Find each count from its class ratio, then add and simplify the overall ratio."
    return q, s, hint, 5, _ratio_fields_answer(
        (girls_a, boys_b, f"{total_boys // g}:{total_girls // g}"),
        (
            'Part (a): girls in Class A',
            'Part (b): boys in Class B',
            'Part (c): boys : girls (simplest form)',
        ),
        ('number', 'number', 'ratio'),
    )


def _ratio_diff_holiday_budget():
    """Split a holiday budget in a ratio and convert part of it to euros."""
    r_meals, r_act, r_souv = _ratio_random_three_parts(2, 7)
    parts = r_meals + r_act + r_souv
    unit = random.randint(25, 65)
    budget = parts * unit
    meals, activities, souvenirs = r_meals * unit, r_act * unit, r_souv * unit
    rate = round(random.uniform(1.12, 1.24), 2)
    meals_eur = round(meals * rate, 2)
    intro = (
        rf"On a school trip, £{budget} is spent in the ratio meals : activities : souvenirs = "
        rf"{r_meals}:{r_act}:{r_souv}. The exchange rate is £1 = €{rate}."
    )
    q = intro + _ratio_abc_block(
        "How much is spent on activities?",
        "How much is spent on souvenirs?",
        "How many euros are spent on meals?",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> One part = £{budget} ÷ {parts} = £{_fmt_num(unit)}. "
        rf"Activities = {r_act} parts = <strong>£{_fmt_num(activities)}</strong><br><br>"
        rf"<strong>b)</strong> Souvenirs = {r_souv} parts = <strong>£{_fmt_num(souvenirs)}</strong><br><br>"
        rf"<strong>c)</strong> Meals = £{_fmt_num(meals)}. In euros: {_fmt_num(meals)} × {rate} = "
        rf"<strong>€{meals_eur:.2f}</strong>"
    )
    hint = "Share the budget by ratio first; multiply by the exchange rate only for the part asked."
    return q, s, hint, 5, _ratio_fields_answer(
        (_number_raw(activities), _number_raw(souvenirs), _number_raw(meals_eur)),
        ('Part (a): activities (£)', 'Part (b): souvenirs (£)', 'Part (c): meals (€)'),
    )


def _ratio_diff_plumbers_job():
    """Inverse proportion: workers and hours for a plumbing job."""
    while True:
        w1 = random.randint(3, 7)
        h1 = random.randint(5, 14)
        w2 = random.randint(4, 12)
        work = w1 * h1
        valid_h3 = [d for d in range(3, 13) if work % d == 0 and d != h1]
        if valid_h3:
            h3 = random.choice(valid_h3)
            break
    h2 = work / w2
    w3 = work // h3
    intro = (
        rf"A plumbing firm says {w1} plumbers can finish a boiler installation in {h1} hours "
        rf"(same rate of work for each plumber)."
    )
    q = intro + _ratio_abc_block(
        "How many plumber-hours of work does the job need?",
        f"How long would {w2} plumbers take?",
        f"How many plumbers are needed to finish in {h3} hours?",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> Work = {w1} × {h1} = <strong>{work} plumber-hours</strong><br><br>"
        rf"<strong>b)</strong> Time = {work} ÷ {w2} = <strong>{_fmt_num(h2)} hours</strong><br><br>"
        rf"<strong>c)</strong> Plumbers = {work} ÷ {h3} = <strong>{_fmt_num(w3)} plumbers</strong>"
    )
    hint = "Workers × time is constant for inverse proportion."
    return q, s, hint, 5, _ratio_fields_answer(
        (work, _number_raw(h2), _number_raw(w3)),
        (
            'Part (a): plumber-hours',
            'Part (b): time (hours)',
            'Part (c): number of plumbers',
        ),
    )


def _ratio_diff_concert_tickets():
    """Ticket types in a ratio with different prices — total revenue."""
    ra, rc = _ratio_random_two_part(2, 6)
    unit = random.randint(70, 140)
    total_tickets = (ra + rc) * unit
    adult_tix, child_tix = ra * unit, rc * unit
    adult_price = random.choice([10, 12, 15, 18, 20, 22, 25])
    child_price = random.choice([4, 5, 6, 7, 8, 10])
    revenue = adult_tix * adult_price + child_tix * child_price
    intro = (
        rf"A concert sells adult and child tickets in the ratio {ra}:{rc}. "
        rf"{total_tickets} tickets are sold altogether. An adult ticket costs £{adult_price} "
        rf"and a child ticket costs £{child_price}."
    )
    q = intro + _ratio_abc_block(
        "How many adult tickets are sold?",
        "How many child tickets are sold?",
        "Find the total ticket revenue.",
    )
    s = (
        intro + "<br><br>"
        rf"<strong>a)</strong> Parts = {ra+rc}. One part = {total_tickets} ÷ {ra+rc} = {unit}. "
        rf"Adult tickets = {ra} × {unit} = <strong>{adult_tix}</strong><br><br>"
        rf"<strong>b)</strong> Child tickets = {rc} × {unit} = <strong>{child_tix}</strong><br><br>"
        rf"<strong>c)</strong> Revenue = {adult_tix}×£{adult_price} + {child_tix}×£{child_price} = "
        rf"<strong>£{revenue}</strong>"
    )
    hint = "Use the ratio for counts, then multiply each type by its price."
    return q, s, hint, 5, _ratio_fields_answer(
        (adult_tix, child_tix, revenue),
        ('Part (a): adult tickets', 'Part (b): child tickets', 'Part (c): revenue (£)'),
    )


# Ratio wrappers: 15 per difficulty (+ 4 intermediate / 4 difficult multi-part)

def _ratio_found_01(): return _ratio_simplify()
def _ratio_found_02(): return _ratio_equivalent()
def _ratio_found_03(): return _ratio_share_two()
def _ratio_found_04(): return _ratio_fraction_of_total()
def _ratio_found_05(): return _ratio_find_missing_part()
def _ratio_found_06(): return _ratio_unitary_cost()
def _ratio_found_07(): return _ratio_recipe_scale()
def _ratio_found_08(): return _ratio_convert_units()
def _ratio_found_09(): return _ratio_share_three()
def _ratio_found_10(): return _ratio_best_buy()
def _ratio_found_11(): return _ratio_scale_map()
def _ratio_found_12(): return _ratio_density_style()
def _ratio_found_13(): return _ratio_inverse_workers()
def _ratio_found_14(): return _ratio_direct_formula()
def _ratio_found_15(): return _ratio_inverse_formula()
def _ratio_found_16(): return _ratio_three_part_as_fraction()

def _ratio_inter_01(): return _ratio_inter_school_house_prize()
def _ratio_inter_02(): return _ratio_inter_cafe_ingredients()
def _ratio_inter_03(): return _ratio_inter_map_hike()
def _ratio_inter_04(): return _ratio_inverse_workers()
def _ratio_inter_05(): return _ratio_direct_formula()
def _ratio_inter_06(): return _ratio_convert_units()
def _ratio_inter_07(): return _ratio_density_style()
def _ratio_inter_08(): return _ratio_recipe_scale()
def _ratio_inter_09(): return _ratio_inter_garden_compost()
def _ratio_inter_10(): return _ratio_inter_school_house_prize()
def _ratio_inter_11(): return _ratio_inter_cafe_ingredients()
def _ratio_inter_12(): return _ratio_inter_map_hike()
def _ratio_inter_13(): return _ratio_inter_garden_compost()
def _ratio_inter_14(): return _ratio_best_buy()
def _ratio_inter_15(): return _ratio_find_missing_part()
def _ratio_inter_16(): return _ratio_share_three()
def _ratio_inter_17(): return _ratio_inverse_formula()
def _ratio_inter_18(): return _ratio_scale_map()
def _ratio_inter_19(): return _ratio_diff_merge_classes()

def _ratio_diff_01(): return _ratio_diff_merge_classes()
def _ratio_diff_02(): return _ratio_diff_holiday_budget()
def _ratio_diff_03(): return _ratio_diff_plumbers_job()
def _ratio_diff_04(): return _ratio_diff_concert_tickets()
def _ratio_diff_05(): return _ratio_diff_merge_classes()
def _ratio_diff_06(): return _ratio_density_style()
def _ratio_diff_07(): return _ratio_diff_holiday_budget()
def _ratio_diff_08(): return _ratio_diff_plumbers_job()
def _ratio_diff_09(): return _ratio_recipe_scale()
def _ratio_diff_10(): return _ratio_share_three()
def _ratio_diff_11(): return _ratio_convert_units()
def _ratio_diff_12(): return _ratio_diff_concert_tickets()
def _ratio_diff_13(): return _ratio_diff_plumbers_job()
def _ratio_diff_14(): return _ratio_scale_map()
def _ratio_diff_15(): return _ratio_best_buy()
def _ratio_diff_16(): return _ratio_inverse_formula()
def _ratio_diff_17(): return _ratio_direct_formula()
def _ratio_diff_18(): return _ratio_share_three()
def _ratio_diff_19(): return _ratio_inter_map_hike()




def ratio_proportion_mcq(mcq_type=None):
    if mcq_type is None:
        mcq_type = random.randint(1, 9)

    if mcq_type == 1:
        a, b, k = random.randint(2,6), random.randint(2,6), random.randint(2,5)
        correct = f"{a*k}:{b*k}"
        q = rf"Simplify the ratio {a*k}:{b*k}."
        distractors = [f"{a*k}:{b}", f"{a}:{b*k}", f"{a}:{b}"]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Divide both numbers by their highest common factor."

    elif mcq_type == 2:
        a, b = random.randint(2,7), random.randint(2,7)
        unit = random.randint(5,20)
        total = (a+b)*unit
        share_a = a*unit
        correct = f"£{share_a}"
        q = rf"Share £{total} in the ratio {a}:{b}. How much is the larger share?"
        distractors = [f"£{b*unit}", f"£{unit}", f"£{total//2}"]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Find one part first, then multiply."

    elif mcq_type == 3:
        items = random.randint(3,8)
        price = round(random.uniform(1.5,4.5),2)
        new_items = random.randint(5,12)
        total = items*price
        ans = new_items*price
        correct = f"£{ans:.2f}"
        q = rf"{items} pens cost £{total:.2f}. What do {new_items} pens cost?"
        distractors = [f"£{total:.2f}", f"£{price:.2f}", f"£{total+ans:.2f}"]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Find the price of one pen first."

    elif mcq_type == 4:
        scale = random.choice([5000,10000,25000])
        cm = random.randint(3,10)
        real_km = cm*scale/100000
        correct = f"{_fmt_num(real_km)} km"
        q = rf"A map scale is 1:{scale}. A road is {cm} cm on the map. What is the real distance?"
        distractors = [f"{_fmt_num(cm*scale/100)} m", f"{_fmt_num(cm*scale/1000)} km", f"{cm} km"]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Convert to real units: multiply by scale, then convert to km."

    elif mcq_type == 5:
        a_items, b_items = random.randint(3,6), random.randint(4,8)
        a_price, b_price = round(random.uniform(1.5,5),2), round(random.uniform(2,6),2)
        unit_a = a_price/a_items
        unit_b = b_price/b_items
        best_letter = 'A' if unit_a < unit_b else 'B'
        correct = f"Pack {best_letter}"
        q = rf"Pack A: {a_items} for £{a_price:.2f}. Pack B: {b_items} for £{b_price:.2f}. Which is better value?"
        distractors = [f"Pack {'B' if best_letter=='A' else 'A'}", "Both equal", "Cannot tell"]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Compare price per item."

    elif mcq_type == 6:
        original = random.randint(2,8)*5
        increase = random.choice([10,20,25])
        ans = original * (1+increase/100)
        correct = f"£{_fmt_num(ans)}"
        q = rf"A price of £{original} is increased by {increase}%. What is the new price?"
        distractors = [f"£{original+increase}", f"£{original*(increase/100):.0f}", f"£{original*increase/100:.0f}"]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Use the multiplier 1 + percentage/100."

    elif mcq_type == 7:
        w1 = random.randint(4, 8)
        h1 = random.randint(6, 12)
        w2 = random.randint(6, 12)
        work = w1 * h1
        correct = f"{_fmt_num(work / w2)} hours"
        q = (
            rf"A job takes {w1} workers {h1} hours. Assuming the same rate of work, "
            rf"how long would {w2} workers take?"
        )
        distractors = [
            f"{_fmt_num(h1 * w2 / w1)} hours",
            f"{_fmt_num(work)} hours",
            f"{_fmt_num(h1 * w1 / w2)} hours",
        ]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Find worker-hours first, then divide by the new number of workers."

    elif mcq_type == 8:
        a, b, c = random.randint(2, 4), random.randint(2, 5), random.randint(2, 6)
        unit = random.randint(8, 25)
        total = (a + b + c) * unit
        middle = b * unit
        correct = f"{middle}"
        q = (
            rf"A charity splits £{total} between projects A, B and C in the ratio {a}:{b}:{c}. "
            rf"How much does project B receive?"
        )
        distractors = [str(a * unit), str(c * unit), str(unit)]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Add the ratio parts, find one part, then multiply by B's share."

    else:
        a, b = random.randint(3, 8), random.randint(3, 8)
        total = (a + b) * random.randint(10, 30)
        girls = total * b // (a + b)
        correct = str(girls)
        q = (
            rf"In a club, the ratio of members who play tennis to members who play football is {a}:{b}. "
            rf"There are {total} members in total. How many play football?"
        )
        distractors = [str(total * a // (a + b)), str(total // 2), str(b)]
        options, correct_letter = _mcq_options(correct, distractors)
        hint = "Football players are b parts out of (a + b) of the total."

    s = f"Answer: {correct_letter}\n\n{hint}"
    return q, s, hint, 1, options, correct_letter


def _ratio_problem_from_output(out, difficulty):
    choice = problem_from_choice_output(out, difficulty, 'gcse', 'maths', 'ratio_proportion')
    if choice:
        return choice
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if values and len(values) == len(labels):
                    extra = {
                        'correct_answer_raw': '|'.join(str(value) for value in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_format_hint': 'Enter a number or fraction in every field',
                    }
                    field_types = raw.get('field_types')
                    if field_types:
                        extra['answer_field_types'] = list(field_types)
            elif raw_type in ('ratio', 'ratio_exact'):
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'ratio_proportion',
                    correct_answer_raw=_ratio_raw(raw['a'], raw['b']),
                    answer_type=raw_type,
                    answer_format_hint='Enter ratio as a:b (e.g. 3:5)',
                )
            elif raw_type == 'number_pair':
                val_a, val_b = raw['values']
                raw_s = f"{_number_raw(val_a)}|{_number_raw(val_b)}"
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'ratio_proportion',
                    correct_answer_raw=raw_s,
                    answer_type='number_pair',
                    answer_labels=[raw['label_a'], raw['label_b']],
                    answer_pair_sep=raw.get('sep', 'and'),
                )
            elif raw_type == 'fraction':
                value = raw.get('value')
                if value is not None and str(value).strip():
                    extra = {
                        'correct_answer_raw': str(value).strip(),
                        'answer_type': 'fraction',
                        'answer_format_hint': 'Enter a fraction (e.g. 3/8)',
                    }
        elif isinstance(raw, (str, int, float)):
            format_hint = 'Enter a number or fraction'
            if isinstance(raw, str) and '/' in raw:
                format_hint = 'Enter a number or fraction (e.g. 1/16)'
            extra = {
                'correct_answer_raw': str(raw) if isinstance(raw, str) else _number_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': format_hint,
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'ratio_proportion', **extra
    )


def gcse_ratio_proportion_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_fn(
            ratio_proportion_mcq, 'ratio_proportion', difficulty, slot_param='mcq_type'
        )
    found = [_ratio_found_01,_ratio_found_02,_ratio_found_03,_ratio_found_04,_ratio_found_05,_ratio_found_06,_ratio_found_07,_ratio_found_08,_ratio_found_09,_ratio_found_10,_ratio_found_11,_ratio_found_12,_ratio_found_13,_ratio_found_14,_ratio_found_15,_ratio_found_16]
    inter = [_ratio_inter_01,_ratio_inter_02,_ratio_inter_03,_ratio_inter_04,_ratio_inter_05,_ratio_inter_06,_ratio_inter_07,_ratio_inter_08,_ratio_inter_09,_ratio_inter_10,_ratio_inter_11,_ratio_inter_12,_ratio_inter_13,_ratio_inter_14,_ratio_inter_15,_ratio_inter_16,_ratio_inter_17,_ratio_inter_18,_ratio_inter_19]
    diff = [_ratio_diff_01,_ratio_diff_02,_ratio_diff_03,_ratio_diff_04,_ratio_diff_05,_ratio_diff_06,_ratio_diff_07,_ratio_diff_08,_ratio_diff_09,_ratio_diff_10,_ratio_diff_11,_ratio_diff_12,_ratio_diff_13,_ratio_diff_14,_ratio_diff_15,_ratio_diff_16,_ratio_diff_17,_ratio_diff_18,_ratio_diff_19]
    pool = found if difficulty == 'foundational' else inter if difficulty == 'intermediate' else diff if difficulty == 'difficult' else random.sample(found,4)+random.sample(inter,4)+random.sample(diff,2)
    return select_tier_variants(pool)


def gcse_ratio_proportion(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_ratio_proportion_variants(difficulty, 'mcq')
        q, s, hint, marks, opts, correct = run_mcq_variant(variants, variant_name)
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'ratio_proportion', options=opts, correct_answer=correct)
    variants = gcse_ratio_proportion_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _ratio_problem_from_output(variant(), difficulty)




# ============================================================
# PROBABILITY (scenarios randomised, answers in <strong>)
# ============================================================

def _prob_frac(a, b):
    g = math.gcd(abs(a), abs(b))
    return f"{a//g}/{b//g}"


def _prob_fraction_answer(a, b):
    return _ratio_fraction_answer(a, b)


def _prob_fields_answer(values, labels, field_types=None):
    payload = {
        'type': 'number_fields',
        'values': tuple(str(value) for value in values),
        'labels': tuple(labels),
    }
    if field_types:
        payload['field_types'] = tuple(field_types)
    return payload


def _prob_svg_venn(a_only, b_only, both, neither):
    total = a_only + b_only + both + neither
    return f"""<div style="text-align:center;margin:10px 0;"><svg width="480" height="260" viewBox="0 0 480 260"
      style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">
      <rect x="10" y="20" width="460" height="225" fill="none" stroke="#777" stroke-width="1.5" rx="6"/>
      <text x="456" y="38" text-anchor="end" font-size="14" font-style="italic" fill="#555">\u03be</text>
      <circle cx="185" cy="122" r="85" fill="#1a6fa8" fill-opacity="0.18" stroke="#1a6fa8" stroke-width="2"/>
      <circle cx="295" cy="122" r="85" fill="#a13544" fill-opacity="0.18" stroke="#a13544" stroke-width="2"/>
      <text x="147" y="72" text-anchor="middle" font-size="16" font-weight="bold" fill="#1a6fa8">A</text>
      <text x="333" y="72" text-anchor="middle" font-size="16" font-weight="bold" fill="#a13544">B</text>
      <text x="138" y="112" text-anchor="middle" font-size="14" font-weight="bold" fill="#1a6fa8">{a_only}</text>
      <text x="138" y="128" text-anchor="middle" font-size="10" fill="#1a6fa8">A only</text>
      <text x="240" y="112" text-anchor="middle" font-size="14" font-weight="bold" fill="#555">{both}</text>
      <text x="240" y="128" text-anchor="middle" font-size="10" fill="#555">A \u2229 B</text>
      <text x="342" y="112" text-anchor="middle" font-size="14" font-weight="bold" fill="#a13544">{b_only}</text>
      <text x="342" y="128" text-anchor="middle" font-size="10" fill="#a13544">B only</text>
      <text x="45" y="228" font-size="11" fill="#555">Neither: {neither}</text>
      <text x="435" y="228" text-anchor="end" font-size="11" fill="#555">Total = {total}</text>
    </svg></div>"""


_VENN3_R = 78
_VENN3_AX, _VENN3_AY = 214, 132
_VENN3_BX, _VENN3_BY = 306, 132
_VENN3_CX, _VENN3_CY = 260, 188
_VENN3_POS = {
    "a_only": (172, 124),
    "b_only": (348, 124),
    "c_only": (260, 232),
    "ab_only": (260, 104),
    "ac_only": (208, 162),
    "bc_only": (312, 162),
    "abc": (260, 140),
    "neither": (52, 248),
}


def _prob_venn_three_cell(x, y, value, font_size=13):
    """One region: number or dashed fill-in box."""
    if value is None:
        w, h = 34, 18
        return (
            f'<rect x="{x - w // 2}" y="{y - h + 4}" width="{w}" height="{h}" rx="3" '
            f'fill="#fffef5" stroke="#bbb" stroke-width="1.2" stroke-dasharray="3,2"/>'
            f'<text x="{x}" y="{y}" text-anchor="middle" font-size="11" fill="#bbb">?</text>'
        )
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{font_size}" '
        f'font-weight="bold" fill="#333">{value}</text>'
    )


def _prob_svg_venn_three(
    a_only, b_only, c_only,
    ab_only, ac_only, bc_only, abc, neither,
    label_a="A", label_b="B", label_c="C",
):
    """Three-set Venn diagram with counts in each region."""
    total = a_only + b_only + c_only + ab_only + ac_only + bc_only + abc + neither
    regions = {
        "a_only": a_only, "b_only": b_only, "c_only": c_only,
        "ab_only": ab_only, "ac_only": ac_only, "bc_only": bc_only,
        "abc": abc, "neither": neither,
    }
    cells = "".join(
        _prob_venn_three_cell(x, y, regions[key])
        for key, (x, y) in _VENN3_POS.items()
    )
    return f"""<div style="text-align:center;margin:10px 0;"><svg width="520" height="300" viewBox="0 0 520 300"
      style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">
      <rect x="10" y="16" width="500" height="268" fill="none" stroke="#777" stroke-width="1.5" rx="6"/>
      <text x="498" y="34" text-anchor="end" font-size="14" font-style="italic" fill="#555">\u03be</text>
      <circle cx="{_VENN3_AX}" cy="{_VENN3_AY}" r="{_VENN3_R}" fill="#1a6fa8" fill-opacity="0.16" stroke="#1a6fa8" stroke-width="2"/>
      <circle cx="{_VENN3_BX}" cy="{_VENN3_BY}" r="{_VENN3_R}" fill="#a13544" fill-opacity="0.16" stroke="#a13544" stroke-width="2"/>
      <circle cx="{_VENN3_CX}" cy="{_VENN3_CY}" r="{_VENN3_R}" fill="#2d7a4a" fill-opacity="0.16" stroke="#2d7a4a" stroke-width="2"/>
      <text x="168" y="56" text-anchor="middle" font-size="15" font-weight="bold" fill="#1a6fa8">{label_a}</text>
      <text x="352" y="56" text-anchor="middle" font-size="15" font-weight="bold" fill="#a13544">{label_b}</text>
      <text x="260" y="272" text-anchor="middle" font-size="15" font-weight="bold" fill="#2d7a4a">{label_c}</text>
      {cells}
      <text x="492" y="248" text-anchor="end" font-size="11" fill="#555">Total = {total}</text>
    </svg></div>"""


def _prob_svg_venn_three_blank(label_a="A", label_b="B", label_c="C"):
    """Empty three-set Venn — students fill every region (and neither)."""
    cells = "".join(
        _prob_venn_three_cell(x, y, None)
        for _key, (x, y) in _VENN3_POS.items()
    )
    return f"""<div style="text-align:center;margin:10px 0;"><svg width="520" height="300" viewBox="0 0 520 300"
      style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">
      <rect x="10" y="16" width="500" height="268" fill="none" stroke="#777" stroke-width="1.5" rx="6"/>
      <text x="498" y="34" text-anchor="end" font-size="14" font-style="italic" fill="#555">\u03be</text>
      <circle cx="{_VENN3_AX}" cy="{_VENN3_AY}" r="{_VENN3_R}" fill="#1a6fa8" fill-opacity="0.16" stroke="#1a6fa8" stroke-width="2"/>
      <circle cx="{_VENN3_BX}" cy="{_VENN3_BY}" r="{_VENN3_R}" fill="#a13544" fill-opacity="0.16" stroke="#a13544" stroke-width="2"/>
      <circle cx="{_VENN3_CX}" cy="{_VENN3_CY}" r="{_VENN3_R}" fill="#2d7a4a" fill-opacity="0.16" stroke="#2d7a4a" stroke-width="2"/>
      <text x="168" y="56" text-anchor="middle" font-size="15" font-weight="bold" fill="#1a6fa8">{label_a}</text>
      <text x="352" y="56" text-anchor="middle" font-size="15" font-weight="bold" fill="#a13544">{label_b}</text>
      <text x="260" y="272" text-anchor="middle" font-size="15" font-weight="bold" fill="#2d7a4a">{label_c}</text>
      {cells}
      <text x="28" y="264" font-size="10" fill="#888">Write counts in each region and for neither.</text>
    </svg></div>"""


# Legible display colours for tree branches, keyed by counter name. Tuned for the
# cream (#f9f8f5) diagram background — e.g. white/yellow are darkened so they read.
_PROB_TREE_COLOURS = {
    "red": "#c0392b",
    "green": "#2e7d32",
    "blue": "#1a6fa8",
    "black": "#333333",
    "white": "#8a8f96",
    "yellow": "#b8860b",
    "purple": "#7b3fa0",
    "orange": "#d35400",
    "pink": "#c2389a",
    "brown": "#8a5a2b",
}
_PROB_TREE_FALLBACK = ("#1a6fa8", "#a13544")


def _prob_tree_colour(name, index):
    """Map a counter name to a legible branch colour; fall back by position."""
    return _PROB_TREE_COLOURS.get(str(name).strip().lower(), _PROB_TREE_FALLBACK[index % 2])


def _prob_svg_tree(c1, c2, p1n, p1d, p2n, p2d,
                   p11n, p11d, p12n, p12d,
                   p21n, p21d, p22n, p22d,
                   title="Two-stage probability tree",
                   show_probs=True, fill_in=False):
    """SVG of a two-draw probability tree.
    show_probs=True  → display all fractions (foundational).
    show_probs=False, fill_in=True → typeable box on every branch (difficult).
    show_probs=False, fill_in=False → bare tree structure only (intermediate).
    """
    def _fr(n, d):
        g = math.gcd(abs(n), abs(d))
        return f"{n // g}/{d // g}"

    o11 = _fr(p1n * p11n, p1d * p11d)
    o12 = _fr(p1n * p12n, p1d * p12d)
    o21 = _fr(p2n * p21n, p2d * p21d)
    o22 = _fr(p2n * p22n, p2d * p22d)
    b1 = _fr(p1n, p1d); b2 = _fr(p2n, p2d)
    b11 = _fr(p11n, p11d); b12 = _fr(p12n, p12d)
    b21 = _fr(p21n, p21d); b22 = _fr(p22n, p22d)

    col1 = _prob_tree_colour(c1, 0)
    col2 = _prob_tree_colour(c2, 1)

    def _branch_label(x, y, val, color):
        """Probability on a branch line — value, fill-in box, or omitted."""
        if show_probs:
            return (f'<text x="{x}" y="{y}" text-anchor="middle" '
                    f'font-size="10" fill="{color}">{val}</text>')
        if not fill_in:
            return ''
        rx, ry = x - 22, y - 11
        return (f'<foreignObject x="{rx}" y="{ry}" width="54" height="22">'
                f'<input xmlns="http://www.w3.org/1999/xhtml" type="text" '
                f'class="prob-tree-input" data-ans="{val}" '
                f'autocomplete="off" spellcheck="false" aria-label="branch probability"/>'
                f'</foreignObject>')

    def _outcome_row(x, y, lbl, prob):
        """Outcome row at end of branch — with probability, fill-in box, or label only."""
        if show_probs:
            return (f'<text x="{x}" y="{y}" font-size="10" fill="#555">'
                    f'\u2192 {lbl} = {prob}</text>')
        if not fill_in:
            return (f'<text x="{x}" y="{y}" font-size="10" fill="#555">'
                    f'\u2192 {lbl}</text>')
        bx = x + 118  # fixed offset — safe for longest colour names
        return (f'<text x="{x}" y="{y}" font-size="10" fill="#555">'
                f'\u2192 {lbl} = </text>'
                f'<foreignObject x="{bx}" y="{y - 11}" width="48" height="22">'
                f'<input xmlns="http://www.w3.org/1999/xhtml" type="text" '
                f'class="prob-tree-input" data-ans="{prob}" '
                f'autocomplete="off" spellcheck="false" aria-label="outcome probability"/>'
                f'</foreignObject>')

    # Wider canvas only when branch/outcome fill-in boxes are shown
    w = 640 if fill_in else 600
    return (
        f'<div style="text-align:center;margin:10px 0;">'
        f'<svg width="{w}" height="290" viewBox="0 0 {w} 290" '
        f'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
        f'<text x="{w//2}" y="18" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">{title}</text>'
        # root
        f'<circle cx="55" cy="148" r="4" fill="#444"/>'
        # first-draw branch lines (coloured by the counter they lead to)
        f'<line x1="55" y1="148" x2="228" y2="76" stroke="{col1}" stroke-width="1.5"/>'
        f'<line x1="55" y1="148" x2="228" y2="220" stroke="{col2}" stroke-width="1.5"/>'
        # first-draw probability labels
        + _branch_label(132, 99, b1, col1)
        + _branch_label(132, 202, b2, col2) +
        # L1 dots and colour labels
        f'<circle cx="228" cy="76" r="3" fill="{col1}"/>'
        f'<text x="236" y="70" font-size="12" font-weight="bold" fill="{col1}">{c1}</text>'
        f'<circle cx="228" cy="220" r="3" fill="{col2}"/>'
        f'<text x="236" y="230" font-size="12" font-weight="bold" fill="{col2}">{c2}</text>'
        # second-draw branch lines (coloured by the counter they lead to)
        f'<line x1="228" y1="76" x2="390" y2="38" stroke="{col1}" stroke-width="1.5"/>'
        f'<line x1="228" y1="76" x2="390" y2="114" stroke="{col2}" stroke-width="1.5"/>'
        f'<line x1="228" y1="220" x2="390" y2="182" stroke="{col1}" stroke-width="1.5"/>'
        f'<line x1="228" y1="220" x2="390" y2="258" stroke="{col2}" stroke-width="1.5"/>'
        # second-draw probability labels
        + _branch_label(309, 49, b11, col1)
        + _branch_label(309, 103, b12, col2)
        + _branch_label(309, 194, b21, col1)
        + _branch_label(309, 255, b22, col2) +
        # L2 colour labels
        f'<text x="398" y="34" font-size="11" font-weight="bold" fill="{col1}">{c1}</text>'
        f'<text x="398" y="110" font-size="11" font-weight="bold" fill="{col2}">{c2}</text>'
        f'<text x="398" y="178" font-size="11" font-weight="bold" fill="{col1}">{c1}</text>'
        f'<text x="398" y="254" font-size="11" font-weight="bold" fill="{col2}">{c2}</text>'
        # outcome + probability column
        + _outcome_row(440, 34, f'({c1},{c1})', o11)
        + _outcome_row(440, 110, f'({c1},{c2})', o12)
        + _outcome_row(440, 178, f'({c2},{c1})', o21)
        + _outcome_row(440, 254, f'({c2},{c2})', o22) +
        # column headers
        f'<text x="228" y="278" text-anchor="middle" font-size="9" fill="#888">1st draw</text>'
        f'<text x="390" y="278" text-anchor="middle" font-size="9" fill="#888">2nd draw</text>'
        f'<text x="{w - 90}" y="278" text-anchor="middle" font-size="9" fill="#888">'
        f'{"outcome" if not show_probs and not fill_in else "outcome \u00b7 P(outcome)"}'
        f'</text>'
        f'</svg></div>'
    )


# ---------- Scenario pools ----------
BUS_LATE = [
    "a bus", "a train", "a flight", "a delivery"
]
GAME_WIN = [
    ("winning a game", "games", "wins"),
    ("scoring a penalty", "penalties", "goals"),
    ("getting a hit", "attempts", "hits"),
    ("picking a winning ticket", "draws", "winners"),
]
TRIAL_EVENT = [
    ("a spinner lands on red", "spins", "red"),
    ("a coin lands on heads", "flips", "heads"),
    ("a light is faulty", "bulbs", "faulty"),
    ("a seed germinates", "seeds", "germinated"),
]
DART_FAIL = [
    "A darts player attempts to hit the bullseye",
    "A basketball player shoots a free throw",
    "A footballer takes a penalty",
    "A student guesses a multiple-choice answer",
]
BAG_COLOURS = [
    ("red", "blue"),
    ("red", "green"),
    ("black", "white"),
    ("yellow", "purple"),
]
COUNTER_CHOOSE = [
    "A bag contains {red} {c1} and {blue} {c2} counters. One counter is chosen at random. Find P({colour}).",
    "There are {red} {c1} and {blue} {c2} marbles in a jar. A marble is picked at random. Find P({colour}).",
    "A box holds {red} {c1} and {blue} {c2} tokens. One token is drawn at random. Find P({colour}).",
    "In a hat there are {red} {c1} and {blue} {c2} tickets. One ticket is pulled at random. Find P({colour}).",
]
CONDITIONAL_SCENARIO = [
    ("study French", "student also studies German", "French", "German | French"),
    ("play football", "student also plays cricket", "football", "cricket | football"),
    ("take art", "also takes music", "art", "music | art"),
    ("own a cat", "also owns a dog", "cat", "dog | cat"),
]
TENNIS_FOOTBALL = [
    ("like tennis", "like football", "like both"),
    ("watch Netflix", "watch YouTube", "watch both"),
    ("eat pasta", "eat pizza", "eat both"),
    ("have a bike", "have a skateboard", "have both"),
]
TWO_COUNTER_SCENARIO = [
    "A bag has {red} {c1} and {blue} {c2} counters. A counter is chosen, replaced, then another is chosen.",
    "A jar contains {red} {c1} and {blue} {c2} marbles. One marble is drawn, put back, then another is drawn.",
]
TWO_COUNTER_NO_REPLACE = [
    "A bag has {red} {c1} and {blue} {c2} counters. Two counters are chosen without replacement.",
    "A box contains {red} {c1} and {blue} {c2} tokens. Two tokens are drawn without replacement.",
]
INDEPENDENT_SCENARIO = [
    ("P(A) = {a}/{b} and P(B) = {c}/{d}",),
    ("The probabilities of two independent events are {a}/{b} and {c}/{d}",),
    ("Event A has probability {a}/{b} and independent event B has probability {c}/{d}",),
    ("For two independent events, the first has probability {a}/{b} and the second has probability {c}/{d}",),
]

# ---------- Helper functions ----------

def _prob_die_favourables(target):
    """Return (count, list_string) for a fair d6."""
    faces = list(range(1, 7))
    if target == "even number":
        fav = [x for x in faces if x % 2 == 0]
    elif target == "odd number":
        fav = [x for x in faces if x % 2 == 1]
    elif target.startswith("greater than "):
        k = int(target.split()[-1])
        fav = [x for x in faces if x > k]
    elif target.startswith("less than "):
        k = int(target.split()[-1])
        fav = [x for x in faces if x < k]
    elif target.startswith("factor of "):
        n = int(target.split()[-1])
        fav = [x for x in faces if n % x == 0]
    elif target == "prime number":
        fav = [2, 3, 5]
    elif target == "multiple of 3":
        fav = [3, 6]
    else:
        fav = [x for x in faces if x % 2 == 0]
    return len(fav), ", ".join(str(x) for x in fav)


def _prob_random_die_target():
    if random.random() < 0.2:
        face = random.randint(1, 6)
        return f"a score of {face}", 1, str(face)
    k = random.randint(2, 5)
    options = [
        "even number",
        "odd number",
        f"greater than {k}",
        f"less than {k + 1}",
        f"at least {k}",
        f"at most {k + 2}",
        f"factor of {random.choice([4, 6, 8, 12])}",
        "prime number",
        "multiple of 3",
        "a multiple of 2",
    ]
    target = random.choice(options)
    if target.startswith("at least "):
        k = int(target.split()[-1])
        fav = [x for x in range(1, 7) if x >= k]
        return target, len(fav), ", ".join(str(x) for x in fav)
    if target.startswith("at most "):
        k = int(target.split()[-1])
        fav = [x for x in range(1, 7) if x <= k]
        return target, len(fav), ", ".join(str(x) for x in fav)
    if target == "a multiple of 2":
        target = "even number"
    fav, fav_list = _prob_die_favourables(target)
    if fav == 0:
        return _prob_random_die_target()
    return target, fav, fav_list


def _prob_random_conditional_pair():
    """Return ((pa_n, pa_d), (pab_n, pab_d)) with P(A∩B) < P(A)."""
    while True:
        total = random.randint(60, 180)
        n_a = random.randint(total // 5, total // 2)
        n_ab = random.randint(1, max(1, n_a // 2))
        if n_ab < n_a:
            pa_g = math.gcd(n_a, total)
            ab_g = math.gcd(n_ab, total)
            return (n_a // pa_g, total // pa_g), (n_ab // ab_g, total // ab_g)


def _prob_single_die():
    target, fav, fav_list = _prob_random_die_target()
    prob = _prob_frac(fav, 6)
    q = f"A fair six-sided die is rolled. Find P({target})."
    s = (f"Favourable outcomes ({target}): {fav_list} — {fav} out of 6 equally likely outcomes.<br>"
         f"P({target}) = {fav}/6 = <strong>{prob}</strong>.")
    hint = "List which numbers on the die satisfy the condition, count them, then divide by 6."
    return q, s, hint, 1, _prob_fraction_answer(fav, 6)


def _prob_single_bag():
    c1, c2 = random.choice(BAG_COLOURS)
    red, blue = random.randint(2, 8), random.randint(2, 8)
    total = red + blue
    colour, count = random.choice([(c1, red), (c2, blue)])
    template = random.choice(COUNTER_CHOOSE)
    q = template.format(red=red, c1=c1, blue=blue, c2=c2, colour=colour)
    prob = _prob_frac(count, total)
    s = (f"There are {count} {colour} counters out of {total} in total.<br>"
         f"P({colour}) = {count}/{total} = <strong>{prob}</strong>.")
    hint = "Count how many items match the colour asked for, then divide by the total number of items."
    return q, s, hint, 1, _prob_fraction_answer(count, total)


def _prob_complement():
    p = round(random.uniform(0.08, 0.88), 2)
    transport = random.choice(BUS_LATE)
    event_word, not_word = random.choice([
        ("late", "not late"),
        ("on time", "late"),
        ("cancelled", "not cancelled"),
        ("delayed", "not delayed"),
    ])
    q = f"The probability that {transport} is {event_word} is {p}. Find P({transport} is {not_word})."
    s = (f"All probabilities sum to 1, so we use the complement rule:<br>"
         f"P({not_word}) = 1 \u2212 P({event_word}) = 1 \u2212 {p} = <strong>{1 - p:.2f}</strong>.")
    hint = "P(not A) = 1 \u2212 P(A). An event and its complement always add up to 1."
    return q, s, hint, 1, f"{1 - p:.2f}"


def _prob_expected_frequency():
    while True:
        b = random.randint(4, 20)
        a = random.randint(1, b - 1)
        if math.gcd(a, b) == 1:
            break
    n = b * random.randint(12, 55)
    event, trials_word, successes_word = random.choice(GAME_WIN)
    ans = n * a // b
    q = f"The probability of {event} is {a}/{b}. In {n} {trials_word}, how many {successes_word} are expected?"
    s = (f"Expected frequency = probability \u00d7 number of trials<br>"
         f"= {a}/{b} \u00d7 {n} = <strong>{ans}</strong>.")
    hint = "Multiply the probability by the number of trials to predict how many successes to expect."
    return q, s, hint, 2, ans


def _prob_relative_frequency():
    trials = random.randint(50, 200)
    success = random.randint(10, trials - 10)
    event, units, adjective = random.choice(TRIAL_EVENT)
    rf = success / trials
    q = f"{event.capitalize()} in {success} out of {trials} {units}. Find the relative frequency."
    s = (f"Relative frequency = number of successes \u00f7 total trials<br>"
         f"= {success} \u00f7 {trials} = <strong>{rf:.3f}</strong> (3 d.p.)<br>"
         f"This experimental value estimates the true probability from real data.")
    hint = "Relative frequency = successes / total trials. It gets closer to the true probability as the number of trials increases."
    return q, s, hint, 2, f"{rf:.3f}"


def _prob_mutually_exclusive():
    a, b = random.sample(range(1, 7), 2)
    prob = _prob_frac(2, 6)
    q = f"A fair die is rolled. Find P({a} or {b})."
    s = (f"Rolling {a} and rolling {b} are mutually exclusive — they cannot both occur on one roll.<br>"
         f"P({a}) = 1/6 &nbsp;&nbsp; P({b}) = 1/6<br>"
         f"P({a} or {b}) = 1/6 + 1/6 = 2/6 = <strong>{prob}</strong>.")
    hint = "Mutually exclusive events cannot happen at the same time — add their individual probabilities."
    return q, s, hint, 2, _prob_fraction_answer(2, 6)


def _prob_two_coins():
    n = random.randint(2, 5)
    total = 2 ** n
    style = random.choice(["exactly", "at least", "same"])
    if style == "exactly":
        r = random.randint(0, n)
        fav = math.comb(n, r)
        head_word = "head" if r == 1 else "heads"
        qtype = f"exactly {r} {head_word}"
        method = f"Choose which {r} of the {n} coins show heads: {n}C{r} = {fav} patterns."
    elif style == "at least":
        r = random.randint(1, n)
        fav = sum(math.comb(n, k) for k in range(r, n + 1))
        head_word = "head" if r == 1 else "heads"
        qtype = f"at least {r} {head_word}"
        method = f"Add the cases with {r}, {r + 1}, \u2026 up to {n} heads."
    else:
        fav = 2
        qtype = "all coins showing the same result"
        method = "Only all heads or all tails match."
    prob = _prob_frac(fav, total)
    coin_word = "coin" if n == 1 else "coins"
    q = f"{n} fair {coin_word} are flipped. Find P({qtype})."
    s = (
        f"There are 2^{n} = {total} equally likely outcomes.<br>"
        f"{method}<br>"
        f"Favourable outcomes = {fav}.<br>"
        f"P({qtype}) = {fav}/{total} = <strong>{prob}</strong>."
    )
    hint = "Count equally likely outcomes in the sample space, or use combinations when order does not matter."
    return q, s, hint, 2, _prob_fraction_answer(fav, total)


def _prob_tree_replacement(blank=False, structure_only=False):
    c1, c2 = random.choice(BAG_COLOURS)
    red, blue = random.randint(2, 6), random.randint(2, 6)
    total = red + blue
    template = random.choice(TWO_COUNTER_SCENARIO)
    scenario = template.format(red=red, c1=c1, blue=blue, c2=c2)
    svg = _prob_svg_tree(
        c1, c2,
        red, total, blue, total,
        red, total, blue, total,
        red, total, blue, total,
        title=f"With replacement \u2014 {c1} / {c2}",
        show_probs=not blank and not structure_only,
        fill_in=blank,
    )
    ask = (f"Complete the tree diagram — type the probability on every branch — then find "
           f"P(two {c1})." if blank else f"Find P(two {c1}).")
    q = f"{scenario}\n{svg}\n{ask}"
    prob = _prob_frac(red * red, total * total)
    s = (f"The counter is <em>replaced</em>, so the bag is unchanged for the 2nd draw.<br>"
         f"P({c1} on 1st draw) = {red}/{total} &nbsp;&nbsp; P({c1} on 2nd draw) = {red}/{total} (same bag).<br>"
         f"P(both {c1}) = {red}/{total} \u00d7 {red}/{total} = <strong>{prob}</strong>.")
    hint = "With replacement: the same probabilities apply on every draw. Multiply along the branch."
    return q, s, hint, 4 if blank else 3, _prob_fraction_answer(red * red, total * total)


def _prob_tree_no_replacement(blank=False, structure_only=False):
    c1, c2 = random.choice(BAG_COLOURS)
    red, blue = random.randint(3, 7), random.randint(2, 6)
    total = red + blue
    template = random.choice(TWO_COUNTER_NO_REPLACE)
    scenario = template.format(red=red, c1=c1, blue=blue, c2=c2)
    svg = _prob_svg_tree(
        c1, c2,
        red, total, blue, total,
        red - 1, total - 1, blue, total - 1,
        red, total - 1, blue - 1, total - 1,
        title=f"Without replacement \u2014 {c1} / {c2}",
        show_probs=not blank and not structure_only,
        fill_in=blank,
    )
    ask = (f"Complete the tree diagram — type the probability on every branch — then find "
           f"P(two {c1})." if blank else f"Find P(two {c1}).")
    q = f"{scenario}\n{svg}\n{ask}"
    prob = _prob_frac(red * (red - 1), total * (total - 1))
    s = (f"1st draw: {red} {c1} from {total} counters — P({c1}) = {red}/{total}.<br>"
         f"2nd draw (no replacement): one {c1} has gone, leaving {red - 1} {c1} from "
         f"{total - 1} counters — P({c1}) = {red - 1}/{total - 1}.<br>"
         f"P(both {c1}) = {red}/{total} \u00d7 {red - 1}/{total - 1} = <strong>{prob}</strong>.")
    hint = "Without replacement: after 1st draw both the numerator (one fewer of that colour) and denominator (one fewer counter) decrease by 1."
    return q, s, hint, 4 if blank else 3, _prob_fraction_answer(red * (red - 1), total * (total - 1))


def _prob_at_least_one():
    p_not = round(random.choice([i / 10 for i in range(2, 8)] + [i / 20 for i in range(3, 17)]), 2)
    scenario = random.choice(DART_FAIL)
    attempts = random.choice([2, 3])
    p_fail_all = p_not ** attempts
    ans = 1 - p_fail_all
    q = (
        f"{scenario}. The probability of failing is {p_not}. "
        f"{attempts} independent attempts are made. Find P(at least one success)."
    )
    if attempts == 2:
        fail_calc = f"{p_not} \u00d7 {p_not} = {p_fail_all:.4f}"
    else:
        fail_calc = f"{p_not} \u00d7 {p_not} \u00d7 {p_not} = {p_fail_all:.4f}"
    s = (
        f"Use the complement rule: P(at least one success) = 1 \u2212 P(no successes at all).<br>"
        f"P(fail once) = {p_not}. The {attempts} attempts are independent, so:<br>"
        f"P(fail every time) = {fail_calc}<br>"
        f"P(at least one success) = 1 \u2212 {p_fail_all:.4f} = <strong>{ans:.4f}</strong>."
    )
    hint = "P(at least one) = 1 \u2212 P(none at all). Multiply the failure probabilities for independent events."
    return q, s, hint, 3, f"{ans:.4f}"


def _prob_conditional_simple():
    first, second, first_label, cond_label = random.choice(CONDITIONAL_SCENARIO)
    # Extract the second event label from e.g. "music | art" → "music"
    second_label = cond_label.split(" | ")[0]
    both_label = f"{first_label} and {second_label}"

    # Pairs (P(A), P(A∩B)) chosen so P(A∩B) < P(A) and the answer is a clean fraction.
    # Using unlike denominators forces students to divide two fractions explicitly.
    (pa_n, pa_d), (pab_n, pab_d) = _prob_random_conditional_pair()

    cond_n = pab_n * pa_d
    cond_d = pab_d * pa_n
    cond_prob = _prob_frac(cond_n, cond_d)

    q = (f"In a school, P({first_label}) = {pa_n}/{pa_d} and "
         f"P({both_label}) = {pab_n}/{pab_d}. "
         f"A student is chosen at random. Find P({cond_label}).")

    s = (f"Apply the conditional probability formula:<br>"
         f"P({cond_label}) = P({both_label}) \u00f7 P({first_label})<br>"
         f"= {pab_n}/{pab_d} \u00f7 {pa_n}/{pa_d}<br>"
         f"= {pab_n}/{pab_d} \u00d7 {pa_d}/{pa_n} &nbsp;&nbsp; [multiply by the reciprocal]<br>"
         f"= {pab_n * pa_d}/{pab_d * pa_n} = <strong>{cond_prob}</strong>.")

    hint = (f"P(B|A) = P(A \u2229 B) \u00f7 P(A). "
            f"To divide by a fraction, flip it and multiply (reciprocal).")

    return q, s, hint, 3, _prob_fraction_answer(cond_n, cond_d)


def _prob_venn_total():
    a_only, b_only = random.randint(5, 25), random.randint(5, 25)
    both, neither = random.randint(3, 15), random.randint(2, 18)
    total = a_only + b_only + both + neither
    svg = _prob_svg_venn(a_only, b_only, both, neither)
    ask = random.choice(["P(A)", "P(B)", "P(A and B)", "P(neither)", "P(not A)"])
    if ask == "P(A)":
        num, expl = a_only + both, (
            f"Circle A contains A only ({a_only}) and A \u2229 B ({both}). Total in A = {a_only + both}."
        )
    elif ask == "P(B)":
        num, expl = b_only + both, (
            f"Circle B contains B only ({b_only}) and A \u2229 B ({both}). Total in B = {b_only + both}."
        )
    elif ask == "P(A and B)":
        num, expl = both, f"The overlap A \u2229 B contains {both} people."
    elif ask == "P(neither)":
        num, expl = neither, f"Outside both circles: {neither} people."
    else:
        num, expl = b_only + neither, (
            f"Not in A means B only ({b_only}) plus neither ({neither}) = {b_only + neither}."
        )
    prob = _prob_frac(num, total)
    context = random.choice([
        "a school survey", "a club membership poll", "a sports registration form",
        "a customer preference survey", "a festival attendance record",
    ])
    q = f"Find {ask} for {context} of {total} people.\n{svg}"
    s = (
        f"{expl}<br>Total surveyed = {total}.<br>"
        f"{ask} = {num}/{total} = <strong>{prob}</strong>."
    )
    hint = "Add the relevant regions from the diagram, then divide by the total in the universal set."
    return q, s, hint, 2, _prob_fraction_answer(num, total)


def _prob_diff_venn_three_clubs():
    """Three-set Venn diagram with multi-step probability parts a–c."""
    act_a, act_b, act_c = random.choice([
        ("tennis", "football", "drama"),
        ("chess", "coding club", "choir"),
        ("Netflix", "YouTube", "Spotify"),
        ("cycling", "swimming", "running"),
    ])
    a_only = random.randint(8, 18)
    b_only = random.randint(6, 16)
    c_only = random.randint(5, 14)
    ab_only = random.randint(3, 10)
    ac_only = random.randint(2, 8)
    bc_only = random.randint(2, 8)
    abc = random.randint(1, 6)
    neither = random.randint(10, 25)
    total = a_only + b_only + c_only + ab_only + ac_only + bc_only + abc + neither

    exactly_one = a_only + b_only + c_only
    at_least_one = total - neither
    or_not_c = a_only + b_only + ab_only

    p_exact = _prob_frac(exactly_one, total)
    p_at_least = _prob_frac(at_least_one, total)
    p_or_not_c = _prob_frac(or_not_c, total)

    la, lb, lc = act_a[0].upper(), act_b[0].upper(), act_c[0].upper()
    svg = _prob_svg_venn_three(
        a_only, b_only, c_only, ab_only, ac_only, bc_only, abc, neither,
        label_a=la, label_b=lb, label_c=lc,
    )
    intro = (
        f"In a year group of {total} students, some take part in after-school activities. "
        f"The Venn diagram shows how many students are in {act_a} ({la}), {act_b} ({lb}), "
        f"and {act_c} ({lc}) only, in pairs, in all three, or in none."
    )
    q = (
        f"{intro}<br>{svg}"
        + _ratio_abc_block(
            "Find the probability that a student does exactly one of the three activities.",
            "Find the probability that a student does at least one activity.",
            f"Find the probability that a student does {act_a} or {act_b} but not {act_c}.",
        )
    )
    s = (
        f"{intro}<br><br>"
        f"<strong>a)</strong> Exactly one activity means {la} only, {lb} only, or {lc} only:<br>"
        f"{a_only} + {b_only} + {c_only} = {exactly_one} students.<br>"
        f"P(exactly one) = {exactly_one}/{total} = <strong>{p_exact}</strong><br><br>"
        f"<strong>b)</strong> At least one = total − neither = {total} − {neither} = {at_least_one}.<br>"
        f"P(at least one) = {at_least_one}/{total} = <strong>{p_at_least}</strong><br><br>"
        f"<strong>c)</strong> {act_a} or {act_b} but not {act_c} = {la} only + {lb} only + {la}\u2229{lb} only "
        f"(exclude {lc} only, all triple overlaps with {lc}, and neither):<br>"
        f"{a_only} + {b_only} + {ab_only} = {or_not_c}.<br>"
        f"P({act_a} or {act_b} but not {act_c}) = {or_not_c}/{total} = <strong>{p_or_not_c}</strong>"
    )
    hint = (
        "Read each region from the Venn diagram. For part (c), include A and B regions "
        "but exclude anyone in C only or the centre triple overlap."
    )
    raw = _prob_fields_answer(
        (p_exact, p_at_least, p_or_not_c),
        (
            "a) P(exactly one activity)",
            "b) P(at least one activity)",
            f"c) P({act_a} or {act_b}, not {act_c})",
        ),
        field_types=('fraction', 'fraction', 'fraction'),
    )
    return q, s, hint, 5, raw


def _prob_diff_venn_three_fill_in():
    """Complete a three-set Venn from partial survey data, then answer probability parts."""
    drink_a, drink_b, drink_c = random.choice([
        ("coffee", "tea", "hot chocolate"),
        ("cola", "lemonade", "water"),
        ("milkshake", "smoothie", "juice"),
        ("football", "rugby", "basketball"),
    ])
    la, lb, lc = drink_a[0].upper(), drink_b[0].upper(), drink_c[0].upper()

    abc = random.randint(4, 9)
    ab_only = random.randint(2, 7)
    ac_only = random.randint(2, 7)
    bc_only = random.randint(2, 7)
    a_only = random.randint(6, 16)
    b_only = random.randint(5, 14)
    c_only = random.randint(5, 14)
    neither = random.randint(8, 22)

    ab_total = ab_only + abc
    ac_total = ac_only + abc
    bc_total = bc_only + abc
    a_total = a_only + ab_only + ac_only + abc
    b_total = b_only + ab_only + bc_only + abc
    c_total = c_only + ab_only + ac_only + abc
    total = a_only + b_only + c_only + ab_only + ac_only + bc_only + abc + neither
    exactly_two = ab_only + ac_only + bc_only

    p_c = _prob_frac(c_total, total)
    p_exact_two = _prob_frac(exactly_two, total)

    is_drinks = drink_a in ("coffee", "cola", "milkshake")
    group = "customers" if is_drinks else "people"
    person = "customer" if is_drinks else "person"
    none_phrase = "none of these drinks" if is_drinks else "none of these"

    clue_lines = [
        f"{abc} {group} like all three.",
        f"{ab_total} {group} like {drink_a} and {drink_b}.",
        f"{ac_total} {group} like {drink_a} and {drink_c}.",
        f"{bc_total} {group} like {drink_b} and {drink_c}.",
        f"{a_total} {group} like {drink_a}.",
        f"{b_total} {group} like {drink_b}.",
        f"{c_total} {group} like {drink_c}.",
        f"{total} {group} were surveyed in total.",
        f"{neither} {group} like {none_phrase}.",
    ]
    random.shuffle(clue_lines)
    clues_html = "<br>".join(f"• {line}" for line in clue_lines)

    blank_svg = _prob_svg_venn_three_blank(label_a=la, label_b=lb, label_c=lc)
    filled_svg = _prob_svg_venn_three(
        a_only, b_only, c_only, ab_only, ac_only, bc_only, abc, neither,
        label_a=la, label_b=lb, label_c=lc,
    )

    venue = "A café surveyed" if is_drinks else "A school surveyed"
    intro = (
        f"{venue} {total} {group} about whether they like {drink_a} ({la}), "
        f"{drink_b} ({lb}), and {drink_c} ({lc}). "
        f"When the survey says two options (for example “{drink_a} and {drink_c}”), "
        f"that includes {group} who like all three unless it says <em>only</em>."
    )
    q = (
        f"{intro}<br><br>{clues_html}<br><br>"
        f"<strong>a)</strong> Complete the Venn diagram. Write a number in every region "
        f"({la} only, {lb} only, {lc} only, each pair, all three, and neither).<br>"
        f"{blank_svg}<br><br>"
        f"<strong>b)</strong> Find the probability that a randomly chosen {person} likes {drink_c}.<br><br>"
        f"<strong>c)</strong> Find the probability that they like exactly two of the three."
    )
    s = (
        f"{intro}<br><br>"
        f"<strong>a)</strong> Work from the centre outwards.<br>"
        f"All three ({la}\u2229{lb}\u2229{lc}): <strong>{abc}</strong>.<br>"
        f"{la}\u2229{lb} total is {ab_total}, so {la}\u2229{lb} only = {ab_total} \u2212 {abc} = <strong>{ab_only}</strong>.<br>"
        f"{la}\u2229{lc} only = {ac_total} \u2212 {abc} = <strong>{ac_only}</strong>.<br>"
        f"{lb}\u2229{lc} only = {bc_total} \u2212 {abc} = <strong>{bc_only}</strong>.<br>"
        f"{la} only: {a_total} \u2212 {ab_only} \u2212 {ac_only} \u2212 {abc} = <strong>{a_only}</strong>.<br>"
        f"{lb} only: {b_total} \u2212 {ab_only} \u2212 {bc_only} \u2212 {abc} = <strong>{b_only}</strong>.<br>"
        f"{lc} only: {c_total} \u2212 {bc_only} \u2212 {ac_only} \u2212 {abc} = <strong>{c_only}</strong> "
        f"(check: {c_only} + {bc_only} + {ac_only} + {abc} = {c_total}).<br>"
        f"Neither (given): <strong>{neither}</strong>.<br>"
        f"Check: {a_only}+{b_only}+{c_only}+{ab_only}+{ac_only}+{bc_only}+{abc}+{neither} "
        f"= {total}.<br><br>Completed diagram:<br>{filled_svg}<br><br>"
        f"<strong>b)</strong> P({drink_c}) = {c_total}/{total} = <strong>{p_c}</strong> "
        f"(using {lc} total from the diagram).<br><br>"
        f"<strong>c)</strong> Exactly two drinks = the three pair-only regions:<br>"
        f"{ab_only} + {ac_only} + {bc_only} = {exactly_two}.<br>"
        f"P(exactly two) = {exactly_two}/{total} = <strong>{p_exact_two}</strong>"
    )
    hint = (
        "Put the all-three count in the centre first. For each pair, subtract the centre "
        "from the given pair total to get the ‘only’ region. Then subtract from each "
        "single-drink total to find the ‘only’ parts on the outside."
    )
    raw = _prob_fields_answer(
        (
            a_only, b_only, c_only, ab_only, ac_only, bc_only, abc, neither,
            p_c, p_exact_two,
        ),
        (
            f"a) {la} only",
            f"a) {lb} only",
            f"a) {lc} only",
            f"a) {la}∩{lb} only",
            f"a) {la}∩{lc} only",
            f"a) {lb}∩{lc} only",
            "a) All three",
            "a) Neither",
            f"b) P({drink_c})",
            "c) P(exactly two)",
        ),
        field_types=(
            'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number',
            'fraction', 'fraction',
        ),
    )
    return q, s, hint, 6, raw


def _prob_or_not_exclusive():
    total = random.randint(40, 80)
    a = random.randint(15, 30)
    b = random.randint(15, 30)
    both = random.randint(5, min(a, b) - 1)
    act1, act2, act_both = random.choice(TENNIS_FOOTBALL)
    num = a + b - both
    prob = _prob_frac(num, total)
    q = f"In a group of {total}, {a} {act1}, {b} {act2}, and {both} {act_both}. Find P({act1} or {act2})."
    s = (f"Use the addition rule to avoid double-counting those in both groups:<br>"
         f"P(A or B) = P(A) + P(B) \u2212 P(A and B)<br>"
         f"= {a}/{total} + {b}/{total} \u2212 {both}/{total}<br>"
         f"= ({a} + {b} \u2212 {both}) / {total} = {num}/{total} = <strong>{prob}</strong>.")
    hint = "The inclusion-exclusion formula subtracts the overlap once to avoid counting those in both groups twice."
    return q, s, hint, 3, _prob_fraction_answer(num, total)


def _prob_independent_product():
    while True:
        b, d = random.randint(3, 12), random.randint(3, 12)
        a, c = random.randint(1, b - 1), random.randint(1, d - 1)
        if math.gcd(a, b) == 1 and math.gcd(c, d) == 1:
            break
    template = random.choice(INDEPENDENT_SCENARIO)[0]
    prob = _prob_frac(a*c, b*d)
    q = template.format(a=a, b=b, c=c, d=d) + " Find P(A and B)."
    s = (f"The events are independent (one does not affect the other), so their probabilities multiply:<br>"
         f"P(A and B) = P(A) \u00d7 P(B) = {a}/{b} \u00d7 {c}/{d} = <strong>{prob}</strong>.")
    hint = "Independent events: P(A and B) = P(A) \u00d7 P(B). One event has no effect on the other."
    return q, s, hint, 2, _prob_fraction_answer(a * c, b * d)


def _prob_tree_simple(blank=False):
    """Foundational: two draws WITH replacement; tree shown; ask P(both same colour)."""
    c1, c2 = random.choice(BAG_COLOURS)
    red = random.randint(2, 4)
    blue = random.randint(2, 4)
    total = red + blue
    svg = _prob_svg_tree(
        c1, c2,
        red, total, blue, total,
        red, total, blue, total,
        red, total, blue, total,
        title="Two draws with replacement",
        show_probs=not blank,
        fill_in=blank,
    )
    prob = _prob_frac(red * red, total * total)
    ask = ("Complete the tree diagram — type the probability on every branch — then use it to find "
           f"P(both counters are {c1})." if blank
           else f"Use the tree diagram to find P(both counters are {c1}).")
    q = (f"A bag has {red} {c1} and {blue} {c2} counters. A counter is drawn, its colour "
         f"noted, then put back. A second counter is drawn.\n{svg}\n{ask}")
    s = (f"The counter is replaced each time, so the bag is unchanged for every draw.<br>"
         f"P({c1}) = {red}/{total} on both draws.<br>"
         f"Follow the ({c1},{c1}) branch: {red}/{total} \u00d7 {red}/{total} = <strong>{prob}</strong>.")
    hint = "With replacement: the same fractions apply on both draws. Multiply the probabilities along the branch."
    return q, s, hint, 3 if blank else 2, _prob_fraction_answer(red * red, total * total)


def _prob_tree_different(blank=False):
    """Two draws WITHOUT replacement; blank tree for difficult, bare structure for intermediate."""
    c1, c2 = random.choice(BAG_COLOURS)
    red = random.randint(3, 6)
    blue = random.randint(3, 6)
    total = red + blue
    svg = _prob_svg_tree(
        c1, c2,
        red, total, blue, total,
        red - 1, total - 1, blue, total - 1,
        red, total - 1, blue - 1, total - 1,
        title=f"Without replacement \u2014 {c1} / {c2}" if not blank else
              f"Without replacement \u2014 complete each branch",
        show_probs=False,
        fill_in=blank,
    )
    num = 2 * red * blue
    den = total * (total - 1)
    prob = _prob_frac(num, den)
    p1 = _prob_frac(red * blue, den)
    p2 = _prob_frac(blue * red, den)
    b1 = _prob_frac(red, total); b2 = _prob_frac(blue, total)
    b11 = _prob_frac(red - 1, total - 1); b12 = _prob_frac(blue, total - 1)
    b21 = _prob_frac(red, total - 1);     b22 = _prob_frac(blue - 1, total - 1)
    if blank:
        q = (f"A bag contains {red} {c1} and {blue} {c2} counters. Two counters are drawn "
             f"without replacement.\n{svg}\n"
             f"(a) Fill in the probability on every branch of the tree diagram.\n"
             f"(b) Hence find the probability that the two counters are "
             f"<strong>different</strong> colours.")
    else:
        q = (f"A bag contains {red} {c1} and {blue} {c2} counters. Two counters are drawn "
             f"without replacement.\n{svg}\n"
             f"Use the tree diagram to find the probability that the two counters are "
             f"<strong>different</strong> colours.")
    s = (f"<strong>(a) Branch probabilities:</strong><br>"
         f"1st draw: P({c1}) = {b1}, &nbsp; P({c2}) = {b2}<br>"
         f"2nd draw from {c1}: P({c1}) = {b11}, &nbsp; P({c2}) = {b12}<br>"
         f"2nd draw from {c2}: P({c1}) = {b21}, &nbsp; P({c2}) = {b22}<br>"
         f"<strong>(b) P(different colours):</strong><br>"
         f"P({c1} then {c2}) = {red}/{total} \u00d7 {blue}/{total-1} = {p1}<br>"
         f"P({c2} then {c1}) = {blue}/{total} \u00d7 {red}/{total-1} = {p2}<br>"
         f"P(different) = {p1} + {p2} = <strong>{prob}</strong>.")
    hint = ("Fill in 1st-draw fractions first (total = {t}), then 2nd-draw fractions "
            "(total drops to {t1} because one counter is gone). "
            "Add the two mixed-colour branches for part (b).").format(t=total, t1=total-1)
    return q, s, hint, 4, _prob_fraction_answer(num, den)


def _prob_tree_at_least_one_colour(blank=False):
    """Two draws WITHOUT replacement; blank tree for difficult, bare structure for intermediate."""
    c1, c2 = random.choice(BAG_COLOURS)
    red = random.randint(3, 5)
    blue = random.randint(3, 5)
    total = red + blue
    svg = _prob_svg_tree(
        c1, c2,
        red, total, blue, total,
        red - 1, total - 1, blue, total - 1,
        red, total - 1, blue - 1, total - 1,
        title=f"Without replacement \u2014 {c1} / {c2}" if not blank else
              f"Without replacement \u2014 complete each branch",
        show_probs=False,
        fill_in=blank,
    )
    p_none_n = blue * (blue - 1)
    p_none_d = total * (total - 1)
    p_none = _prob_frac(p_none_n, p_none_d)
    prob = _prob_frac(p_none_d - p_none_n, p_none_d)
    b1 = _prob_frac(red, total); b2 = _prob_frac(blue, total)
    b11 = _prob_frac(red - 1, total - 1); b12 = _prob_frac(blue, total - 1)
    b21 = _prob_frac(red, total - 1);     b22 = _prob_frac(blue - 1, total - 1)
    if blank:
        q = (f"A bag has {red} {c1} and {blue} {c2} counters. Two are drawn without replacement.\n"
             f"{svg}\n"
             f"(a) Fill in the probability on every branch of the tree diagram.\n"
             f"(b) Hence find P(at least one {c1} counter).")
    else:
        q = (f"A bag has {red} {c1} and {blue} {c2} counters. Two are drawn without replacement.\n"
             f"{svg}\n"
             f"Use the tree diagram to find P(at least one {c1} counter).")
    s = (f"<strong>(a) Branch probabilities:</strong><br>"
         f"1st draw: P({c1}) = {b1}, &nbsp; P({c2}) = {b2}<br>"
         f"2nd draw from {c1}: P({c1}) = {b11}, &nbsp; P({c2}) = {b12}<br>"
         f"2nd draw from {c2}: P({c1}) = {b21}, &nbsp; P({c2}) = {b22}<br>"
         f"<strong>(b) P(at least one {c1}) — complement method:</strong><br>"
         f"P(no {c1}) = P({c2},{c2}) = {blue}/{total} \u00d7 {blue - 1}/{total - 1} = {p_none}<br>"
         f"P(at least one {c1}) = 1 \u2212 {p_none} = <strong>{prob}</strong>.")
    hint = (f"Fill in all six branch probabilities first. Then use complement: "
            f"P(at least one {c1}) = 1 \u2212 P({c2},{c2}).")
    return q, s, hint, 4, _prob_fraction_answer(p_none_d - p_none_n, p_none_d)


# ---- Variant wrappers ----

def _prob_found_01(): return _prob_single_die()
def _prob_found_02(): return _prob_single_bag()
def _prob_found_03(): return _prob_complement()
def _prob_found_04(): return _prob_expected_frequency()
def _prob_found_05(): return _prob_relative_frequency()
def _prob_found_06(): return _prob_mutually_exclusive()
def _prob_found_07(): return _prob_two_coins()
def _prob_found_08(): return _prob_tree_simple()
def _prob_found_09(): return _prob_tree_replacement()
def _prob_found_10(): return _prob_venn_total()
def _prob_found_11(): return _prob_independent_product()
def _prob_found_12(): return _prob_or_not_exclusive()
def _prob_found_13(): return _prob_single_die()
def _prob_found_14(): return _prob_at_least_one()
def _prob_found_15(): return _prob_conditional_simple()

def _prob_inter_01(): return _prob_two_coins()
def _prob_inter_02(): return _prob_tree_replacement(structure_only=True)
def _prob_inter_03(): return _prob_tree_no_replacement(structure_only=True)
def _prob_inter_04(): return _prob_venn_total()
def _prob_inter_05(): return _prob_independent_product()
def _prob_inter_06(): return _prob_or_not_exclusive()
def _prob_inter_07(): return _prob_expected_frequency()
def _prob_inter_08(): return _prob_relative_frequency()
def _prob_inter_09(): return _prob_diff_venn_three_clubs()
def _prob_inter_10(): return _prob_tree_different()
def _prob_inter_11(): return _prob_tree_at_least_one_colour()
def _prob_inter_12(): return _prob_diff_venn_three_fill_in()
def _prob_inter_13(): return _prob_single_die()
def _prob_inter_14(): return _prob_complement()
def _prob_inter_15(): return _prob_mutually_exclusive()

def _prob_diff_01(): return _prob_at_least_one()
def _prob_diff_02(): return _prob_conditional_simple()
def _prob_diff_03(): return _prob_or_not_exclusive()
def _prob_diff_04(): return _prob_tree_different(blank=True)
def _prob_diff_05(): return _prob_tree_at_least_one_colour(blank=True)
def _prob_diff_06(): return _prob_tree_replacement(blank=True)
def _prob_diff_07(): return _prob_venn_total()
def _prob_diff_08(): return _prob_independent_product()
def _prob_diff_09(): return _prob_relative_frequency()
def _prob_diff_10(): return _prob_expected_frequency()
def _prob_diff_11(): return _prob_single_bag()
def _prob_diff_12(): return _prob_two_coins()
def _prob_diff_13(): return _prob_tree_simple(blank=True)
def _prob_diff_14(): return _prob_mutually_exclusive()
def _prob_diff_15(): return _prob_complement()
def _prob_diff_16(): return _prob_tree_no_replacement(blank=True)
def _prob_diff_17(): return _prob_or_not_exclusive()


# ---- Probability MCQ (shows full solution) ----
_PROBABILITY_MCQ_GENERATORS = [
    _prob_single_die,
    _prob_single_bag,
    _prob_complement,
    _prob_expected_frequency,
    _prob_two_coins,
    _prob_mutually_exclusive,
    _prob_relative_frequency,
    _prob_independent_product,
]


def probability_mcq(slot_index=None):
    if slot_index is None:
        func = random.choice(_PROBABILITY_MCQ_GENERATORS)
    else:
        func = _PROBABILITY_MCQ_GENERATORS[slot_index % len(_PROBABILITY_MCQ_GENERATORS)]
    q, full_s, hint_text, marks = func()[:4]

    correct = ""
    if '<strong>' in full_s:
        parts = full_s.split('<strong>', 1)
        if len(parts) > 1:
            rest = parts[1].split('</strong>', 1)
            if rest:
                correct = rest[0].strip()
    if not correct:
        correct = '1/2'

    if 'die' in q or 'fair six' in q:
        distractors = ['1/6', '1/2', '2/3', '1/3']
    elif 'bag' in q or 'counters' in q or 'marble' in q or 'token' in q or 'ticket' in q:
        nums = [int(w) for w in q.split() if w.isdigit()]
        if len(nums) >= 2 and nums[0] + nums[1] > 0:
            red, blue = nums[0], nums[1]
            total = red + blue
            distractors = [f'{red}/{total}', f'{blue}/{total}', f'{red+blue}/{total}', '1/2']
        else:
            distractors = ['1/4', '1/2', '2/5', '3/5']
    elif 'not' in q.lower() or 'complement' in q.lower():
        distractors = ['0', '0.5', '1', '0.25']
    elif 'coin' in q:
        distractors = ['1/4', '1/2', '3/4', '1']
    elif 'expected' in q.lower():
        dist = int(correct) if correct.isdigit() else 10
        distractors = [str(dist), str(dist + 5), str(dist - 5), str(dist * 2)]
    elif 'relative frequency' in q.lower():
        distractors = [correct, '0.5', '0.25', '0.75']
    elif 'mutually exclusive' in q.lower() or ' or ' in q:
        distractors = ['1/6', '1/2', '1/3', '2/3']
    elif 'independent' in q.lower():
        distractors = ['1/4', '1/2', '1/3', '2/3']
    else:
        distractors = ['1/2', '1/3', '2/3', '1/4']

    clean_distractors = [d for d in distractors if d != correct]
    options, letter = _mcq_options(correct, clean_distractors)
    return q, full_s, hint_text, 1, options, letter


def gcse_probability_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_fn(
            probability_mcq, 'probability', difficulty, slot_param='slot_index'
        )
    found = [_prob_found_01, _prob_found_02, _prob_found_03, _prob_found_04,
             _prob_found_05, _prob_found_06, _prob_found_07, _prob_found_08,
             _prob_found_09, _prob_found_10, _prob_found_11, _prob_found_12,
             _prob_found_13, _prob_found_14, _prob_found_15]
    inter = [_prob_inter_01, _prob_inter_02, _prob_inter_03, _prob_inter_04,
             _prob_inter_05, _prob_inter_06, _prob_inter_07, _prob_inter_08,
             _prob_inter_09, _prob_inter_10, _prob_inter_11, _prob_inter_12,
             _prob_inter_13, _prob_inter_14, _prob_inter_15]
    diff = [_prob_diff_01, _prob_diff_02, _prob_diff_03, _prob_diff_04,
            _prob_diff_05, _prob_diff_06, _prob_diff_07, _prob_diff_08,
            _prob_diff_09, _prob_diff_10, _prob_diff_11, _prob_diff_12,
            _prob_diff_13, _prob_diff_14, _prob_diff_15, _prob_diff_16,
            _prob_diff_17]
    if difficulty == 'foundational':
        pool = found
    elif difficulty == 'intermediate':
        pool = inter
    elif difficulty == 'difficult':
        pool = diff
    else:
        pool = random.sample(found, 4) + random.sample(inter, 4) + random.sample(diff, 2)
    return select_tier_variants(pool)


def _prob_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if values and len(values) == len(labels):
                    extra = {
                        'correct_answer_raw': '|'.join(str(value) for value in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_format_hint': 'Enter a number or fraction in every field',
                    }
                    field_types = raw.get('field_types')
                    if field_types:
                        extra['answer_field_types'] = list(field_types)
            elif raw_type == 'fraction':
                value = raw.get('value')
                if value is not None and str(value).strip():
                    extra = {
                        'correct_answer_raw': str(value).strip(),
                        'answer_type': 'fraction',
                        'answer_format_hint': 'Enter a fraction (e.g. 3/8)',
                    }
        elif isinstance(raw, (str, int, float)):
            format_hint = 'Enter a number or fraction'
            if 'prob-tree-input' in q and '(b)' in q:
                format_hint = 'Part (b): enter a fraction'
            extra = {
                'correct_answer_raw': str(raw),
                'answer_type': 'number',
                'answer_format_hint': format_hint,
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'probability', **extra
    )


def gcse_probability(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_probability_variants(difficulty, 'mcq')
        q, s, hint, marks, opts, correct = run_mcq_variant(variants, variant_name)
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'probability',
                            options=opts, correct_answer=correct)
    variants = gcse_probability_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _prob_problem_from_output(variant(), difficulty)

# ============================================================
# STATISTICS
# ============================================================


def _stats_svg_bar_chart(categories, values):
    W, H = 400, 280
    PL, PR, PT, PB = 55, 20, 30, 52
    pw, ph = W - PL - PR, H - PT - PB
    max_val = max(values)
    n = len(categories)
    bar_w = min(55, pw // n - 12)
    bar_gap = (pw - bar_w * n) // (n + 1)

    bars = ""
    for i, (cat, val) in enumerate(zip(categories, values)):
        x = PL + bar_gap + i * (bar_w + bar_gap)
        bh = (val / max_val) * ph
        y = PT + ph - bh
        bars += f'<rect x="{x:.0f}" y="{y:.0f}" width="{bar_w}" height="{bh:.0f}" fill="#01696f" rx="2"/>'
        bars += f'<text x="{x + bar_w/2:.0f}" y="{y - 5:.0f}" text-anchor="middle" font-size="11" fill="#333">{val}</text>'
        bars += f'<text x="{x + bar_w/2:.0f}" y="{PT+ph+20:.0f}" text-anchor="middle" font-size="12">{cat}</text>'

    y_ticks = ""
    for i in range(6):
        val = round(max_val * i / 5)
        yp = PT + ph - (val / max_val) * ph
        y_ticks += f'<line x1="{PL-4}" y1="{yp:.0f}" x2="{PL}" y2="{yp:.0f}" stroke="#555"/>'
        y_ticks += f'<text x="{PL-7}" y="{yp+4:.0f}" text-anchor="end" font-size="11">{val}</text>'

    return (f'<div style="text-align:center;margin:10px 0;">'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
            f' style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
            f'<line x1="{PL}" y1="{PT+ph}" x2="{W-PR}" y2="{PT+ph}" stroke="#555" stroke-width="1.5"/>'
            f'<line x1="{PL}" y1="{PT}" x2="{PL}" y2="{PT+ph}" stroke="#555" stroke-width="1.5"/>'
            f'{y_ticks}{bars}'
            f'</svg></div>')


def _stats_svg_freq_table(values, freqs):
    """Draw a simple frequency table with fx column."""
    w, h = 300, 30 + 25 * len(values)
    rows = []
    total_f = sum(freqs)
    total_fx = sum(v * f for v, f in zip(values, freqs))
    for i, (v, f) in enumerate(zip(values, freqs)):
        y = 45 + i * 25
        rows.append(f'<text x="70" y="{y}" text-anchor="middle" font-size="12">{v}</text>')
        rows.append(f'<text x="170" y="{y}" text-anchor="middle" font-size="12">{f}</text>')
        rows.append(f'<text x="240" y="{y}" text-anchor="middle" font-size="12">{v*f}</text>')
    # totals row
    y_last = 45 + len(values) * 25
    rows.append(f'<line x1="40" y1="{y_last-15}" x2="260" y2="{y_last-15}" stroke="#555"/>')
    rows.append(f'<text x="70" y="{y_last}" text-anchor="middle" font-size="12" font-weight="bold">Σ</text>')
    rows.append(f'<text x="170" y="{y_last}" text-anchor="middle" font-size="12" font-weight="bold">{total_f}</text>')
    rows.append(f'<text x="240" y="{y_last}" text-anchor="middle" font-size="12" font-weight="bold">{total_fx}</text>')

    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"
        style="background:#f9f8f5; border-radius:8px; display:block; margin:10px auto;">
        <text x="70" y="28" text-anchor="middle" font-size="12" font-weight="bold">x</text>
        <text x="170" y="28" text-anchor="middle" font-size="12" font-weight="bold">f</text>
        <text x="240" y="28" text-anchor="middle" font-size="12" font-weight="bold">fx</text>
        {''.join(rows)}
    </svg>"""


def _stats_svg_histogram(intervals, freqs):
    W, H = 460, 310
    PL, PR, PT, PB = 65, 22, 32, 52
    pw, ph = W - PL - PR, H - PT - PB
    densities = [f / (high - low) for (low, high), f in zip(intervals, freqs)]
    max_d = max(densities)
    x_span = intervals[-1][1] - intervals[0][0]

    def sx(v): return PL + (v - intervals[0][0]) / x_span * pw

    bars = ""
    for (low, high), f, d in zip(intervals, freqs, densities):
        x = sx(low)
        bw = sx(high) - x
        bh = (d / max_d) * ph
        y = PT + ph - bh
        bars += f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="#01696f" opacity="0.85" stroke="#01696f" stroke-width="0.5"/>'
        bars += f'<text x="{x:.0f}" y="{PT+ph+18}" text-anchor="middle" font-size="11">{low}</text>'
    bars += f'<text x="{sx(intervals[-1][1]):.0f}" y="{PT+ph+18}" text-anchor="middle" font-size="11">{intervals[-1][1]}</text>'

    y_step = max(1, int(max_d / 5) + 1)
    y_ticks = ""
    for val in range(0, int(max_d) + y_step, y_step):
        yp = PT + ph - (val / max_d) * ph
        if PT - 5 <= yp <= PT + ph:
            y_ticks += f'<line x1="{PL-4}" y1="{yp:.0f}" x2="{PL}" y2="{yp:.0f}" stroke="#555"/>'
            y_ticks += f'<text x="{PL-7}" y="{yp+4:.0f}" text-anchor="end" font-size="11">{val}</text>'

    cy_lbl = PT + ph // 2
    return (f'<div style="text-align:center;margin:10px 0;">'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
            f' style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
            f'<line x1="{PL}" y1="{PT+ph}" x2="{W-PR}" y2="{PT+ph}" stroke="#555" stroke-width="1.5"/>'
            f'<line x1="{PL}" y1="{PT}" x2="{PL}" y2="{PT+ph}" stroke="#555" stroke-width="1.5"/>'
            f'{y_ticks}{bars}'
            f'<text x="{W//2}" y="{H-8}" text-anchor="middle" font-size="12">Class intervals</text>'
            f'<text x="14" y="{cy_lbl}" transform="rotate(-90,14,{cy_lbl})" text-anchor="middle" font-size="12">Frequency density</text>'
            f'</svg></div>')



def _stats_svg_boxplot(min_val, q1, q2, q3, max_val):
    W, H = 460, 175
    PL, PR = 50, 30
    pw = W - PL - PR
    by1, by2, wcy = 45, 115, 80  # box top, box bottom, whisker centre

    scale = pw / max(1, max_val - min_val)
    def x(val): return PL + (val - min_val) * scale

    lmap = {min_val: 'Min', q1: 'Q\u2081', q2: 'Median', q3: 'Q\u2083', max_val: 'Max'}
    ticks = ""
    for val in [min_val, q1, q2, q3, max_val]:
        xp = x(val)
        ticks += f'<line x1="{xp:.0f}" y1="{by2}" x2="{xp:.0f}" y2="{by2+5}" stroke="#555"/>'
        ticks += f'<text x="{xp:.0f}" y="{by2+20}" text-anchor="middle" font-size="12">{val}</text>'
        ticks += f'<text x="{xp:.0f}" y="{by1-10}" text-anchor="middle" font-size="10" fill="#666">{lmap[val]}</text>'

    return (f'<div style="text-align:center;margin:10px 0;">'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
            f' style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
            f'<line x1="{PL}" y1="{by2}" x2="{W-PR}" y2="{by2}" stroke="#555" stroke-width="1.5"/>'
            f'<line x1="{x(min_val):.0f}" y1="{wcy}" x2="{x(q1):.0f}" y2="{wcy}" stroke="#01696f" stroke-width="2.5"/>'
            f'<line x1="{x(min_val):.0f}" y1="{by1+6}" x2="{x(min_val):.0f}" y2="{by2-6}" stroke="#01696f" stroke-width="2"/>'
            f'<rect x="{x(q1):.0f}" y="{by1}" width="{x(q3)-x(q1):.0f}" height="{by2-by1}" fill="#dce8f7" stroke="#01696f" stroke-width="2"/>'
            f'<line x1="{x(q2):.0f}" y1="{by1}" x2="{x(q2):.0f}" y2="{by2}" stroke="#a13544" stroke-width="2.5"/>'
            f'<line x1="{x(q3):.0f}" y1="{wcy}" x2="{x(max_val):.0f}" y2="{wcy}" stroke="#01696f" stroke-width="2.5"/>'
            f'<line x1="{x(max_val):.0f}" y1="{by1+6}" x2="{x(max_val):.0f}" y2="{by2-6}" stroke="#01696f" stroke-width="2"/>'
            f'{ticks}'
            f'</svg></div>')

def _stats_svg_cf_curve(upper_bounds, cum_freqs):
    W, H = 520, 340
    PL, PR, PT, PB = 62, 22, 35, 52
    pw, ph = W - PL - PR, H - PT - PB
    max_cf = cum_freqs[-1]
    x_min_d, x_max_d = upper_bounds[0], upper_bounds[-1]
    x_span = x_max_d - x_min_d
    # start curve at (lower bound of first class, 0)
    class_w = upper_bounds[1] - upper_bounds[0] if len(upper_bounds) > 1 else x_span
    lb0 = upper_bounds[0] - class_w
    all_x = [lb0] + list(upper_bounds)
    all_cf = [0] + list(cum_freqs)
    x_lo = lb0

    def sx(v): return PL + (v - x_lo) / (x_max_d - x_lo) * pw
    def sy(v): return PT + ph - (v / max_cf) * ph

    path = "M" + " L".join(f"{sx(v):.0f},{sy(c):.0f}" for v, c in zip(all_x, all_cf))

    ticks = ""
    for ub in all_x:
        xp = sx(ub)
        ticks += f'<line x1="{xp:.0f}" y1="{PT+ph}" x2="{xp:.0f}" y2="{PT+ph+5}" stroke="#555"/>'
        ticks += f'<text x="{xp:.0f}" y="{PT+ph+20}" text-anchor="middle" font-size="11">{ub}</text>'

    y_step = max(1, max_cf // 5)
    for val in range(0, max_cf + 1, y_step):
        yp = sy(val)
        if PT - 5 <= yp <= PT + ph:
            ticks += f'<line x1="{PL-4}" y1="{yp:.0f}" x2="{PL}" y2="{yp:.0f}" stroke="#555"/>'
            ticks += f'<text x="{PL-7}" y="{yp+4:.0f}" text-anchor="end" font-size="11">{val}</text>'

    circles = "".join(f'<circle cx="{sx(v):.0f}" cy="{sy(c):.0f}" r="4" fill="#a13544"/>'
                      for v, c in zip(all_x[1:], all_cf[1:]))
    cy_lbl = PT + ph // 2
    return (f'<div style="text-align:center;margin:10px 0;">'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
            f' style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
            f'<line x1="{PL}" y1="{PT+ph}" x2="{W-PR}" y2="{PT+ph}" stroke="#555" stroke-width="1.5"/>'
            f'<line x1="{PL}" y1="{PT}" x2="{PL}" y2="{PT+ph}" stroke="#555" stroke-width="1.5"/>'
            f'{ticks}'
            f'<path d="{path}" fill="none" stroke="#01696f" stroke-width="2.5"/>'
            f'{circles}'
            f'<text x="{W//2}" y="{H-8}" text-anchor="middle" font-size="12">Upper class boundary</text>'
            f'<text x="14" y="{cy_lbl}" transform="rotate(-90,14,{cy_lbl})" text-anchor="middle" font-size="12">Cumulative frequency</text>'
            f'</svg></div>')





_STATS_CONTEXTS = [
    ("runners", "finishing times", "minutes"),
    ("apples", "masses", "grams"),
    ("students", "test scores", "marks"),
    ("seedlings", "heights", "cm"),
    ("commuters", "daily distances", "km"),
    ("participants", "reaction times", "ms"),
    ("customers", "bill totals", "\u00a3"),
    ("parcels", "weights", "kg"),
    ("patients", "waiting times", "minutes"),
    ("leaves", "lengths", "mm"),
    ("cyclists", "times taken", "seconds"),
    ("households", "weekly spend", "\u00a3"),
    ("dogs", "masses", "kg"),
    ("phone calls", "durations", "seconds"),
    ("packages", "delivery distances", "km"),
]


def _stats_random_context(n=None):
    """Return (scenario_sentence, unit) for a graph/chart question.

    When ``n`` is supplied it is woven into the sentence so the lead text
    (and therefore the stem) varies with the sample size, not just the wording.
    """
    subject, measured, unit = random.choice(_STATS_CONTEXTS)
    if n is None:
        sentence = f"The {measured} of a group of {subject} were recorded."
    else:
        sentence = f"The {measured} of {n} {subject} were recorded."
    return sentence, unit


def _stats_freq_mean():
    n_vals = random.randint(4, 6)
    start = random.randint(0, 2)
    values = list(range(start, start + n_vals))
    freqs = [random.randint(2, 12) for _ in values]
    total_f = sum(freqs)
    total_fx = sum(v * f for v, f in zip(values, freqs))
    svg = _stats_svg_freq_table(values, freqs)
    noun, who = random.choice([
        ("pets", "students"),
        ("siblings", "pupils"),
        ("goals scored per match", "matches"),
        ("books read last month", "children"),
        ("emails received per hour", "workers"),
        ("cars passing per minute", "intervals"),
    ])
    scenario = f"A survey of {total_f} {who} recorded the number of {noun}."
    q = f"{scenario}\n{svg}\nFind the mean number of {noun} (to 2 d.p.)."
    mean_val = total_fx / total_f
    terms = ' + '.join(f'{v} × {f}' for v, f in zip(values, freqs))
    s = (
        f"Σfx = {terms} = {total_fx}<br>"
        f"Σf = {total_f}<br>"
        f"Mean = {total_fx} ÷ {total_f} = <strong>{mean_val:.2f}</strong><br>"
        f"The mean number of {noun} is <strong>{mean_val:.2f}</strong>."
    )
    hint = "Use mean = Σfx ÷ Σf."
    return q, s, hint, 3, _number_raw(mean_val)


def _stats_estimated_mean_grouped():
    width = random.choice([5, 10, 20])
    start = width * random.randint(0, 3)
    n_classes = random.randint(3, 4)
    intervals = [(start + width * i, start + width * (i + 1)) for i in range(n_classes)]
    freqs = [random.randint(2, 12) for _ in intervals]
    total_f = sum(freqs)
    scenario, unit = _stats_random_context(total_f)
    svg = _stats_svg_histogram(intervals, freqs)
    mids = [(a + b) / 2 for a, b in intervals]
    total_fx = sum(m * f for m, f in zip(mids, freqs))
    est_mean = total_fx / total_f
    mid_terms = ' + '.join(f'{m:.0f} × {f}' for m, f in zip(mids, freqs))
    q = f"{scenario}\n{svg}\nEstimate the mean (in {unit})."
    s = (
        f"Midpoints: {', '.join(f'{m:.0f}' for m in mids)}<br>"
        f"Σfx = {mid_terms} = {total_fx:.0f}<br>"
        f"Σf = {total_f}<br>"
        f"Estimated mean = {total_fx:.0f} ÷ {total_f} = <strong>{est_mean:.2f}</strong><br>"
        f"The estimated mean is <strong>{est_mean:.2f}</strong> {unit}."
    )
    hint = "Use class midpoints."
    return q, s, hint, 4, _number_raw(est_mean)


def _stats_grouped_midpoint():
    width = random.choice([5, 10, 15, 20, 25])
    low = width * random.randint(0, 8)
    high = low + width
    var = random.choice(['x', 't', 'h', 'm', 'w'])
    mid = (low + high) / 2
    mid_str = f"{mid:.0f}" if mid == int(mid) else f"{mid:.1f}"
    q = rf"Find the midpoint of the class interval {low} &lt; {var} ≤ {high}."
    s = rf"Midpoint = ({low}+{high}) ÷ 2 = <strong>{mid_str}</strong>."
    return q, s, "Add the class boundaries and divide by 2.", 1, _number_raw(mid)


def _stats_range_list():
    scenario = random.choice([
        "daily temperatures (°C) recorded over a week",
        "scores of students in a quiz",
        "heights of plants in a biology experiment",
    ])
    vals = [random.randint(5, 50) for _ in range(6)]
    q = f"The {scenario} are: {', '.join(map(str, vals))}. Find the range."
    s = f"Range = highest − lowest = {max(vals)} − {min(vals)} = <strong>{max(vals) - min(vals)}</strong>."
    hint = "Range = max − min."
    return q, s, hint, 1, max(vals) - min(vals)


def _stats_median_list():
    scenario = random.choice([
        "test scores of a group of students",
        "number of goals scored by a football team in each match",
        "hourly wages of part‑time workers",
    ])
    vals = [random.randint(1, 30) for _ in range(7)]
    ordered = sorted(vals)
    med = ordered[len(vals)//2]
    q = f"The {scenario} are: {', '.join(map(str, vals))}. Find the median."
    s = f"Values in order: {', '.join(map(str, ordered))}. The middle value is <strong>{med}</strong>."
    hint = "Put in order first."
    return q, s, hint, 2, med


def _stats_mode_list():
    scenario = random.choice([
        "shoe sizes of a group of students",
        "favourite ice‑cream flavours voted by a class",
        "number of siblings of each student in a year group",
    ])
    mode = random.randint(2, 9)
    pool = [x for x in range(1, 13) if x != mode]
    others = random.sample(pool, 4)
    vals = [mode, mode, mode] + others
    random.shuffle(vals)
    q = f"The {scenario} are: {', '.join(map(str, vals))}. Find the mode."
    s = f"The mode is the most common value. <strong>{mode}</strong> occurs most often."
    hint = "The mode is the value with the highest frequency."
    return q, s, hint, 1, mode


def _stats_mean_list():
    scenario = random.choice([
        "daily rainfall (mm) over a week",
        "running speeds (km/h) of a group of athletes",
        "weekly pocket money (£) of a group of friends",
    ])
    vals = [random.randint(2, 20) for _ in range(5)]
    mean = sum(vals) / len(vals)
    q = f"The {scenario} are: {', '.join(map(str, vals))}. Find the mean."
    s = f"Sum = {'+'.join(map(str, vals))} = {sum(vals)}. Count = {len(vals)}. Mean = {sum(vals)} ÷ {len(vals)} = <strong>{mean:.2f}</strong>."
    hint = "Add them all, then divide by how many there are."
    return q, s, hint, 2, _number_raw(mean)


def _stats_pie_angle():
    pairs = [
        ("a survey of favourite subjects", "chose maths"),
        ("an election with three candidates", "voted for candidate A"),
        ("a school cafeteria menu choice", "chose pizza"),
        ("a survey of pet ownership", "own a dog"),
    ]
    scenario, label = random.choice(pairs)
    total = random.choice([60, 80, 100, 120])
    freq = random.randint(10, total - 10)
    angle = 360 * freq / total
    q = rf"In {scenario}, {freq} out of {total} respondents {label}. Find the sector angle for this category in a pie chart."
    s = f"Sector angle = (frequency ÷ total) × 360 = ({freq} ÷ {total}) × 360 = <strong>{angle:.1f}°</strong>."
    hint = "A full pie chart is 360°."
    return q, s, hint, 2, _number_raw(angle, dp=1)


def _stats_scatter_correlation():
    scenario = random.choice([
        ("Hours of revision", "Exam score (%)"),
        ("Distance from city centre (km)", "House price (£000s)"),
        ("Temperature (°C)", "Ice creams sold"),
        ("Age of car (years)", "Resale value (£000s)"),
        ("Daily rainfall (mm)", "Beach visitors"),
        ("Hours of TV per day", "Hours of sleep"),
        ("Height (cm)", "Shoe size"),
        ("Engine size (litres)", "Fuel economy (mpg)"),
        ("Number of practice sessions", "Free throws made"),
        ("Outdoor temperature (°C)", "Heating cost (£)"),
    ])
    corr = random.choice(['positive', 'negative', 'no'])
    n = random.randint(9, 14)
    if corr == 'positive':
        points = [(i + random.uniform(-0.5, 0.5), 2*i + random.uniform(-1.5, 1.5)) for i in range(1, n + 1)]
        lof = (2, 0)
    elif corr == 'negative':
        points = [(i + random.uniform(-0.5, 0.5), -2*i + 2*n + random.uniform(-1.5, 1.5)) for i in range(1, n + 1)]
        lof = (-2, 2 * n)
    else:
        points = [(random.uniform(1, n), random.uniform(1, n)) for _ in range(n)]
        lof = None
    svg = _gr_svg_scatter(points, f"{scenario[0]} vs {scenario[1]}", scenario[0], scenario[1], lof)
    q = (f"A scatter graph was plotted for {n} data pairs of "
         f"{scenario[0].lower()} and {scenario[1].lower()}.\n{svg}\n"
         f"What type of correlation does this scatter graph show?")
    s = f"This is <strong>{corr} correlation</strong>."
    hint = "Look at the overall direction of the data points."
    corr_options = [
        'A  Positive correlation',
        'B  Negative correlation',
        'C  No correlation',
    ]
    corr_letters = {'positive': 'A', 'negative': 'B', 'no': 'C'}
    raw = {
        'type': 'choice',
        'options': corr_options,
        'correct': corr_letters[corr],
    }
    return q, s, hint, 1, raw




def _stats_line_best_fit():
    x_lab, y_lab = random.choice([
        ("x", "y"),
        ("Hours studied", "Score"),
        ("Week", "Sales"),
        ("Temperature", "Sales"),
        ("Distance", "Time"),
        ("Age", "Height"),
    ])
    x1, y1 = 2, random.randint(5, 10)
    gradient = random.randint(2, 5)
    x2 = random.randint(5, 10)
    y2 = y1 + gradient * (x2 - x1)
    xq = random.randint(3, 9)
    y_val = y1 + gradient * (xq - x1)
    # Build scatter points near the line y = gradient*x + c
    c_lof = y1 - gradient * x1
    n = random.randint(9, 13)
    x_vals = [random.uniform(1, 11) for _ in range(n)]
    points = [(x, gradient * x + c_lof + random.uniform(-2, 2)) for x in x_vals]
    svg = _gr_svg_scatter(points, f"{x_lab} vs {y_lab}", x_lab, y_lab, (gradient, c_lof))
    _, y_step = _gr_scatter_axis_steps(points)
    y_tol = _gr_estimate_tolerance(y_step)
    y_disp = int(round(y_val))
    q = (f"The scatter graph shows {y_lab} against {x_lab} for {n} data points.\n{svg}\n"
         f"The line of best fit passes through ({x1},\u2009{y1}) and ({x2},\u2009{y2}). "
         f"Estimate {y_lab} when {x_lab}\u2009=\u2009{xq}.")
    s = (f"Gradient = ({y2}\u2212{y1})\u00f7({x2}\u2212{x1}) = {gradient}.<br>"
         f"When x = {xq}: y \u2248 {y1} + {gradient}\u00d7({xq}\u2212{x1}) = <strong>{y_disp}</strong> "
         f"(accept estimates within \u00b1{y_tol}).")
    hint = "Use the line of best fit to interpolate within the data range."
    return q, s, hint, 3, _gr_number_estimate_answer(y_val, y_tol)


def _stats_cumulative_frequency():
    width = random.choice([5, 10, 20])
    start = width * random.randint(1, 3)
    n_classes = random.randint(4, 5)
    upper_bounds = [start + width * (i + 1) for i in range(n_classes)]
    cum_freqs = [random.randint(3, 8)]
    for _ in range(1, len(upper_bounds)):
        cum_freqs.append(cum_freqs[-1] + random.randint(4, 12))
    scenario, unit = _stats_random_context(cum_freqs[-1])
    svg = _stats_svg_cf_curve(upper_bounds, cum_freqs)
    q = f"{scenario}\nThe cumulative frequency graph is shown.\n{svg}\nEstimate the median (in {unit})."
    half = cum_freqs[-1] / 2
    # Find which interval contains the half value
    median_approx = 25  # fallback
    for ub, cf in zip(upper_bounds, cum_freqs):
        if cf >= half:
            # linear interpolation within the interval
            prev_cf = cum_freqs[cum_freqs.index(cf) - 1] if cum_freqs.index(cf) > 0 else 0
            prev_ub = upper_bounds[cum_freqs.index(cf) - 1] if cum_freqs.index(cf) > 0 else 0
            median_approx = prev_ub + (half - prev_cf) / (cf - prev_cf) * (ub - prev_ub)
            break
    s = (f"Total frequency = {cum_freqs[-1]}. Half = {half:.1f}.<br>"
         f"Read across from {half:.1f} on the y‑axis to the curve, then down to the x‑axis.<br>"
         f"The median is approximately <strong>{median_approx:.0f}</strong> "
         f"(accept estimates within \u00b1{max(2, width // 2)}).")
    hint = "Find half the total frequency, then read from the curve."
    return q, s, hint, 3, _gr_number_estimate_answer(
        median_approx, max(2, width // 2)
    )

def _stats_box_iqr():
    min_val = random.randint(5, 15)
    q1 = min_val + random.randint(2, 8)
    q2 = q1 + random.randint(2, 8)
    q3 = q2 + random.randint(2, 8)
    max_val = q3 + random.randint(2, 10)
    svg = _stats_svg_boxplot(min_val, q1, q2, q3, max_val)
    scenario, unit = _stats_random_context(random.randint(20, 200))
    q = f"{scenario}\nThe data are summarised in the box plot below.\n{svg}\nFind the interquartile range (in {unit})."
    s = f"IQR = Q₃ − Q₁ = {q3} − {q1} = <strong>{q3 - q1}</strong> {unit}."
    hint = "IQR = upper quartile − lower quartile."
    return q, s, hint, 2, q3 - q1

def _stats_bar_read():
    a, b, c = random.randint(5, 25), random.randint(5, 25), random.randint(5, 25)
    cats = ['A', 'B', 'C']
    vals = [a, b, c]
    svg = _stats_svg_bar_chart(cats, vals)
    q = f"A bar chart shows category A = {a}, B = {b}, C = {c}.\n{svg}\nHow many items are there altogether?"
    s = f"Add the frequencies: {a} + {b} + {c} = <strong>{a+b+c}</strong>."
    hint = "Total frequency = sum of the bar heights."
    return q, s, hint, 1, a + b + c


def _stats_hist_density():
    """Histogram FD question: the diagram matches the class named in the text."""
    width_q = random.choice([5, 10, 20])
    density_q = random.randint(2, 8)
    freq_q = width_q * density_q

    # Second class: different width and integer FD so the chart has two distinct bars
    w2 = random.choice([w for w in (5, 10, 15, 20) if w != width_q])
    density2 = random.choice([d for d in range(2, 9) if d != density_q])
    f2 = w2 * density2

    low = 0
    high1 = width_q
    high2 = width_q + w2
    intervals = [(low, high1), (high1, high2)]
    freqs = [freq_q, f2]

    svg = _stats_svg_histogram(intervals, freqs)

    scenario, unit = _stats_random_context(freq_q + f2)
    q = (
        f"{scenario}\nThe grouped data are shown in the histogram below.\n{svg}\n"
        f"For the class interval <strong>{low} – {high1}</strong>, the frequency is <strong>{freq_q}</strong> "
        f"and the class width is <strong>{width_q}</strong>. "
        f"Find the frequency density for this class."
    )
    s = (
        f"Frequency density = frequency ÷ class width = {freq_q} ÷ {width_q} = "
        f"<strong>{density_q}</strong>."
    )
    hint = "Use frequency density = frequency ÷ class width (frequency per unit along the horizontal axis)."
    return q, s, hint, 2, density_q


def _stats_compare_distributions():
    med1, med2 = random.randint(20, 50), random.randint(20, 50)
    iqr1, iqr2 = random.randint(5, 20), random.randint(5, 20)
    q = rf"Class A has median {med1} and IQR {iqr1}. Class B has median {med2} and IQR {iqr2}. Which class has the greater typical value and which is more consistent?"
    if med1 > med2:
        typical = "greater typical value: Class A"
    elif med2 > med1:
        typical = "greater typical value: Class B"
    else:
        typical = "equal medians (same typical value in both classes)"
    if iqr1 < iqr2:
        consistent = "more consistent: Class A (smaller IQR)"
    elif iqr2 < iqr1:
        consistent = "more consistent: Class B (smaller IQR)"
    else:
        consistent = "equal IQRs (same consistency in both classes)"
    correct = f"{typical}; {consistent}"
    s = rf"<strong>{correct}</strong>."
    hint = "Compare medians for typical value and IQRs for consistency."
    distractors = [
        'greater typical value: Class B; more consistent: Class A (smaller IQR)',
        'greater typical value: Class A; more consistent: Class B (smaller IQR)',
        'greater typical value: Class B; more consistent: Class B (smaller IQR)',
        'greater typical value: Class A; more consistent: Class A (larger IQR)',
    ]
    options, letter = _mcq_options(correct, [d for d in distractors if d != correct])
    raw = {'type': 'choice', 'options': options, 'correct': letter}
    return q, s, hint, 2, raw


def _stats_cf_interp(upper_bounds, cum_freqs, fraction):
    """Estimate the value at a given cumulative fraction (e.g. 0.5 for median)."""
    total = cum_freqs[-1]
    target = total * fraction
    class_w = upper_bounds[1] - upper_bounds[0]
    bounds = [upper_bounds[0] - class_w] + list(upper_bounds)
    cfs = [0] + list(cum_freqs)
    for i in range(1, len(bounds)):
        if cfs[i] >= target:
            x0, x1 = bounds[i - 1], bounds[i]
            c0, c1 = cfs[i - 1], cfs[i]
            if c1 == c0:
                return x1
            return x0 + (target - c0) / (c1 - c0) * (x1 - x0)
    return bounds[-1]


def _stats_cf_count_below(upper_bounds, cum_freqs, x_value):
    """Estimate cumulative count below x_value using linear interpolation on the CF curve."""
    class_w = upper_bounds[1] - upper_bounds[0]
    bounds = [upper_bounds[0] - class_w] + list(upper_bounds)
    cfs = [0] + list(cum_freqs)
    if x_value <= bounds[0]:
        return 0
    if x_value >= bounds[-1]:
        return cfs[-1]
    for i in range(1, len(bounds)):
        if x_value <= bounds[i]:
            x0, x1 = bounds[i - 1], bounds[i]
            c0, c1 = cfs[i - 1], cfs[i]
            if x1 == x0:
                return c1
            return c0 + (x_value - x0) / (x1 - x0) * (c1 - c0)
    return cfs[-1]


def _stats_diff_cf_multipart():
    """Cumulative frequency graph — median, IQR, and a count from the curve."""
    unit, ctx_noun = random.choice([
        ("minutes", "the times taken by runners to finish a race"),
        ("grams", "the masses of apples picked from an orchard"),
        ("marks", "the scores in a maths test"),
        ("cm", "the heights of plants in a nursery"),
        ("km", "the daily distances cycled by commuters"),
        ("seconds", "the call durations at a help centre"),
        ("\u00a3", "the weekly grocery spend of households"),
        ("kg", "the weights of luggage at check-in"),
    ])
    class_w = random.choice([5, 10])
    start = random.randint(10, 30)
    n_classes = 5
    upper_bounds = [start + class_w * (i + 1) for i in range(n_classes)]
    while True:
        freqs = [random.randint(3, 12) for _ in range(n_classes)]
        total = sum(freqs)
        if total % 4 == 0:
            break
    scenario = f"The cumulative frequency graph summarises {ctx_noun} (sample size {total})."
    cum_freqs = []
    running = 0
    for f in freqs:
        running += f
        cum_freqs.append(running)

    median = _stats_cf_interp(upper_bounds, cum_freqs, 0.5)
    q1 = _stats_cf_interp(upper_bounds, cum_freqs, 0.25)
    q3 = _stats_cf_interp(upper_bounds, cum_freqs, 0.75)
    iqr = q3 - q1
    threshold = random.choice(upper_bounds[1:-1])
    below_threshold = round(_stats_cf_count_below(upper_bounds, cum_freqs, threshold))

    svg = _stats_svg_cf_curve(upper_bounds, cum_freqs)
    intro = f"{scenario}<br>{svg}"
    q = (
        intro + _ratio_abc_block(
            f"Estimate the median (give your answer in {unit}).",
            "Estimate the interquartile range.",
            f"How many items have a value of {threshold} {unit} or less?",
        )
    )
    s = (
        intro + "<br><br>"
        f"<strong>a)</strong> Total frequency = {total}. Median position = {total // 2}.<br>"
        f"Read across from {total // 2} on the cumulative frequency axis to the curve, then down.<br>"
        f"Median \u2248 <strong>{median:.1f} {unit}</strong>.<br><br>"
        f"<strong>b)</strong> Q\u2081 is at {total // 4} (\u2248{q1:.1f} {unit}) and "
        f"Q\u2083 is at {3 * total // 4} (\u2248{q3:.1f} {unit}).<br>"
        f"IQR = Q\u2083 \u2212 Q\u2081 \u2248 {q3:.1f} \u2212 {q1:.1f} = <strong>{iqr:.1f} {unit}</strong>.<br><br>"
        f"<strong>c)</strong> Read up from {threshold} {unit} to the curve, then across to the axis.<br>"
        f"Cumulative frequency up to {threshold} \u2248 {below_threshold}.<br>"
        f"So <strong>{below_threshold}</strong> items are {threshold} {unit} or less."
    )
    hint = (
        "Use half the total for the median, the lower and upper quartile positions for the IQR, "
        "and read cumulative frequency directly from the graph for part (c)."
    )
    raw = _prob_fields_answer(
        (_number_raw(median, dp=1), _number_raw(iqr, dp=1), below_threshold),
        ('Part (a): median', 'Part (b): IQR', 'Part (c): count'),
    )
    return q, s, hint, 5, raw


def _stats_diff_histogram_multipart():
    """Grouped histogram — estimated mean, frequency density, and a proportion."""
    unit, ctx_noun = random.choice([
        ("cm", "the heights of plants in a greenhouse"),
        ("m", "the distances thrown in a javelin competition"),
        ("ms", "the reaction times of participants in a science experiment"),
        ("kg", "the masses of dogs at a veterinary clinic"),
        ("minutes", "the times spent on a fitness app per day"),
        ("\u00a3", "the amounts donated at a charity event"),
    ])
    class_w = random.choice([5, 10])
    low = (
        random.randint(140, 160) if unit == "cm"
        else random.randint(20, 40) if unit == "m"
        else random.randint(200, 280) if unit == "ms"
        else random.randint(5, 40)
    )
    n_classes = 4
    intervals = [(low + class_w * i, low + class_w * (i + 1)) for i in range(n_classes)]
    freqs = [random.randint(4, 18) for _ in range(n_classes)]
    total = sum(freqs)
    scenario = f"The histogram summarises {ctx_noun} (sample size {total})."
    mids = [(a + b) / 2 for a, b in intervals]
    total_fx = sum(m * f for m, f in zip(mids, freqs))
    est_mean = total_fx / total

    target_i = random.randint(0, n_classes - 1)
    t_low, t_high = intervals[target_i]
    t_freq = freqs[target_i]
    t_fd = t_freq / class_w
    t_pct = _prob_frac(t_freq, total)

    svg = _stats_svg_histogram(intervals, freqs)
    intro = f"{scenario}<br>{svg}"
    q = (
        intro + _ratio_abc_block(
            f"Estimate the mean (in {unit}).",
            f"Find the frequency density for the class interval {t_low}–{t_high} {unit}.",
            f"What fraction of the data lie in the class interval {t_low}–{t_high} {unit}?",
        )
    )
    mid_terms = " + ".join(
        f"{m:.0f}\\times{f}" if class_w == 10 else f"{m:.1f}\\times{f}" for m, f in zip(mids, freqs)
    )
    s = (
        intro + "<br><br>"
        f"<strong>a)</strong> Midpoints: {', '.join(f'{m:.0f}' for m in mids)} {unit}.<br>"
        rf"\(\sum fx = {mid_terms} = {total_fx:.0f}\), \(\sum f = {total}\).<br>"
        rf"Estimated mean = \(\frac{{{total_fx:.0f}}}{{{total}}}\) = <strong>{est_mean:.2f} {unit}</strong>.<br><br>"
        f"<strong>b)</strong> Class width = {class_w} {unit}, frequency = {t_freq}.<br>"
        f"Frequency density = {t_freq} \u00f7 {class_w} = <strong>{t_fd:.2f}</strong> "
        f"(per {unit}).<br><br>"
        f"<strong>c)</strong> Frequency in {t_low}–{t_high} = {t_freq} out of {total}.<br>"
        f"Fraction = {t_freq}/{total} = <strong>{t_pct}</strong>."
    )
    hint = (
        "Use midpoints for the mean, frequency \u00f7 class width for density, "
        "and frequency \u00f7 total for the fraction in one class."
    )
    raw = _prob_fields_answer(
        (_number_raw(est_mean), _number_raw(t_fd), t_pct),
        (
            f'Part (a): estimated mean ({unit})',
            f'Part (b): frequency density ({unit})',
            'Part (c): fraction',
        ),
    )
    return q, s, hint, 5, raw


# Statistics wrappers

def _stats_found_01(): return _stats_mean_list()
def _stats_found_02(): return _stats_median_list()
def _stats_found_03(): return _stats_mode_list()
def _stats_found_04(): return _stats_range_list()
def _stats_found_05(): return _stats_grouped_midpoint()
def _stats_found_06(): return _stats_bar_read()
def _stats_found_07(): return _stats_scatter_correlation()
def _stats_found_08(): return _stats_pie_angle()
def _stats_found_09(): return _stats_mean_list()
def _stats_found_10(): return _stats_median_list()
def _stats_found_11(): return _stats_mode_list()
def _stats_found_12(): return _stats_range_list()
def _stats_found_13(): return _stats_grouped_midpoint()
def _stats_found_14(): return _stats_bar_read()
def _stats_found_15(): return _stats_scatter_correlation()

def _stats_inter_01(): return _stats_freq_mean()
def _stats_inter_02(): return _stats_estimated_mean_grouped()
def _stats_inter_03(): return _stats_pie_angle()
def _stats_inter_04(): return _stats_line_best_fit()
def _stats_inter_05(): return _stats_cumulative_frequency()
def _stats_inter_06(): return _stats_box_iqr()
def _stats_inter_07(): return _stats_hist_density()
def _stats_inter_08(): return _stats_compare_distributions()
def _stats_inter_09(): return _stats_bar_read()
def _stats_inter_10(): return _stats_estimated_mean_grouped()
def _stats_inter_11(): return _stats_scatter_correlation()
def _stats_inter_12(): return _stats_cumulative_frequency()
def _stats_inter_13(): return _stats_box_iqr()
def _stats_inter_14(): return _stats_hist_density()
def _stats_inter_15(): return _stats_compare_distributions()

def _stats_diff_01(): return _stats_estimated_mean_grouped()
def _stats_diff_02(): return _stats_diff_histogram_multipart()
def _stats_diff_03(): return _stats_compare_distributions()
def _stats_diff_04(): return _stats_line_best_fit()
def _stats_diff_05(): return _stats_diff_cf_multipart()
def _stats_diff_06(): return _stats_freq_mean()
def _stats_diff_07(): return _stats_pie_angle()
def _stats_diff_08(): return _stats_box_iqr()
def _stats_diff_09(): return _stats_diff_histogram_multipart()
def _stats_diff_10(): return _stats_compare_distributions()
def _stats_diff_11(): return _stats_diff_cf_multipart()
def _stats_diff_12(): return _stats_line_best_fit()
def _stats_diff_13(): return _stats_diff_cf_multipart()
def _stats_diff_14(): return _stats_freq_mean()
def _stats_diff_15(): return _stats_diff_histogram_multipart()
def _stats_diff_16(): return _stats_diff_cf_multipart()
def _stats_diff_17(): return _stats_diff_histogram_multipart()



_STATISTICS_MCQ_GENERATORS = [
    _stats_mean_list,
    _stats_median_list,
    _stats_mode_list,
    _stats_range_list,
    _stats_grouped_midpoint,
    _stats_pie_angle,
    _stats_bar_read,
    _stats_scatter_correlation,
    _stats_freq_mean,
    _stats_estimated_mean_grouped,
    _stats_box_iqr,
    _stats_hist_density,
    _stats_compare_distributions,
]


def statistics_mcq(slot_index=None):
    if slot_index is None:
        func = random.choice(_STATISTICS_MCQ_GENERATORS)
    else:
        func = _STATISTICS_MCQ_GENERATORS[slot_index % len(_STATISTICS_MCQ_GENERATORS)]
    q, full_s, hint_text, marks = func()[:4]

    # Extract correct answer from the full solution
    correct = ""
    if '<strong>' in full_s:
        parts = full_s.split('<strong>', 1)
        if len(parts) > 1:
            rest = parts[1].split('</strong>', 1)
            if rest:
                correct = rest[0].strip()

    # Distractors based on the CONTENT of the question
    if 'typical value' in q.lower() or 'more consistent' in q.lower():
        distractors = [
            'greater typical value: Class B; more consistent: Class A (smaller IQR)',
            'greater typical value: Class A; more consistent: Class B (smaller IQR)',
            'greater typical value: Class B; more consistent: Class B (smaller IQR)',
            'greater typical value: Class A; more consistent: Class A (larger IQR)',
        ]
    elif 'correlation' in q.lower():
        distractors = ['positive', 'negative', 'none', 'quadrant I']
    elif 'interquartile' in q.lower() or 'box plot' in q.lower():
        try:
            c = int(correct)
            distractors = [str(c + 2), str(c - 2), str(c * 2)]
        except:
            distractors = ['5', '10', '15', '20']
    elif 'frequency density' in q.lower() or 'histogram' in q.lower():
        try:
            c = float(correct)
            distractors = [str(round(c * 2, 1)), str(round(c / 2, 1)), str(int(c) + 2)]
        except:
            distractors = ['2', '4', '6', '8']
    elif 'frequency table' in q.lower() or 'fx' in q.lower() or '∑' in q:
        try:
            c = round(float(correct), 1)
            distractors = [str(round(c + 2, 1)), str(round(c - 1, 1)), str(int(c) + 3)]
        except:
            distractors = ['10', '12', '14', '16']
    elif 'sector' in q.lower() or 'pie' in q.lower() or 'angle' in q.lower():
        distractors = ['90°', '180°', '270°', '360°']
    elif 'midpoint' in q.lower():
        try:
            c = int(correct)
            distractors = [str(c + 5), str(c - 5), str(c + 10)]
        except:
            distractors = ['15', '25', '35', '45']
    elif 'bar chart' in q.lower() or 'altogether' in q.lower():
        try:
            c = int(correct)
            distractors = [str(c + 2), str(c - 1), str(c * 2)]
        except:
            distractors = ['10', '20', '30', '40']
    else:
        try:
            c = float(correct)
            distractors = [str(c + 3), str(c - 2), str(c * 2)]
        except:
            distractors = ['10', '20', '30', '40']

    clean_distractors = [d for d in distractors if d != correct]
    options, letter = _mcq_options(correct, clean_distractors)

    # Return the FULL step‑by‑step solution, not just the hint
    return q, full_s, hint_text, marks, options, letter



def _stats_problem_from_output(out, difficulty):
    choice = problem_from_choice_output(out, difficulty, 'gcse', 'maths', 'statistics')
    if choice:
        return choice
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if values and len(values) == len(labels):
                    extra = {
                        'correct_answer_raw': '|'.join(str(value) for value in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_format_hint': 'Enter a number or fraction in every field',
                    }
            elif raw_type == 'number_estimate':
                tol = int(raw['tolerance'])
                dp = raw.get('dp', 0)
                extra = {
                    'correct_answer_raw': _gr_estimate_raw(raw['value'], tol, dp=dp),
                    'answer_type': 'number_estimate',
                    'answer_format_hint': 'Enter your estimate from the graph (close answers are accepted)',
                }
        elif isinstance(raw, (str, int, float)):
            format_hint = 'Enter a number or fraction'
            q_lower = q.lower()
            if 'to 2 d.p.' in q_lower:
                format_hint = 'Enter a number to 2 decimal places'
            elif 'sector angle' in q_lower or 'pie chart' in q_lower:
                format_hint = 'Enter the angle in degrees (no ° symbol)'
            elif 'estimate' in q_lower and 'median' in q_lower:
                format_hint = 'Enter your estimate as a whole number'
            extra = {
                'correct_answer_raw': str(raw),
                'answer_type': 'number',
                'answer_format_hint': format_hint,
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'statistics', **extra
    )


def gcse_statistics_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_fn(
            statistics_mcq, 'statistics', difficulty, slot_param='slot_index'
        )
    found = [_stats_found_01,_stats_found_02,_stats_found_03,_stats_found_04,_stats_found_05,_stats_found_06,_stats_found_07,_stats_found_08,_stats_found_09,_stats_found_10,_stats_found_11,_stats_found_12,_stats_found_13,_stats_found_14,_stats_found_15]
    inter = [_stats_inter_01,_stats_inter_02,_stats_inter_03,_stats_inter_04,_stats_inter_05,_stats_inter_06,_stats_inter_07,_stats_inter_08,_stats_inter_09,_stats_inter_10,_stats_inter_11,_stats_inter_12,_stats_inter_13,_stats_inter_14,_stats_inter_15]
    diff = [_stats_diff_01,_stats_diff_02,_stats_diff_03,_stats_diff_04,_stats_diff_05,_stats_diff_06,_stats_diff_07,_stats_diff_08,_stats_diff_09,_stats_diff_10,_stats_diff_11,_stats_diff_12,_stats_diff_13,_stats_diff_14,_stats_diff_15,_stats_diff_16,_stats_diff_17]
    pool = found if difficulty == 'foundational' else inter if difficulty == 'intermediate' else diff if difficulty == 'difficult' else random.sample(found,4)+random.sample(inter,4)+random.sample(diff,2)
    return select_tier_variants(pool)


def gcse_statistics(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_statistics_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'statistics',
            options=opts_mcq, correct_answer=correct_mcq,
        )
    variants = gcse_statistics_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _stats_problem_from_output(variant(), difficulty)




def _gr_fmt_linear(m, c):
    """Return a clean 'y = mx + c' string with proper sign handling."""
    if m == 1:
        mx = "x"
    elif m == -1:
        mx = "−x"
    elif m < 0:
        mx = f"−{abs(m)}x"
    else:
        mx = f"{m}x"
    if c >= 0:
        return f"y = {mx} + {c}"
    return f"y = {mx} − {abs(c)}"

def _gr_fmt_bracket(r):
    """Return '(x - r)' or '(x + |r|)' with proper sign."""
    if r >= 0:
        return f"(x − {r})"
    else:
        return f"(x + {abs(r)})"


def _gr_fmt_quadratic(a, b, c):
    """Return 'y = ax² + bx + c' with clean GCSE sign formatting."""
    if a == 1:
        lead = "x²"
    elif a == -1:
        lead = "−x²"
    else:
        lead = f"{a}x²"
    if b != 0:
        if b == 1:
            lead += " + x"
        elif b == -1:
            lead += " − x"
        elif b > 0:
            lead += f" + {b}x"
        else:
            lead += f" − {abs(b)}x"
    if c != 0:
        if c > 0:
            lead += f" + {c}"
        else:
            lead += f" − {abs(c)}"
    return f"y = {lead}"


def _gr_quad_y(x, a, b, c):
    return a * x * x + b * x + c


# ============================================================
# GRAPHS (improved – scatter SVGs, line sketches)
# ============================================================

def _gr_bounds_with_origin(x_lo, x_hi, y_lo, y_hi, padding=1):
    """Expand plot bounds so x = 0 and y = 0 lie inside the window (GCSE axes)."""
    return (
        min(x_lo, 0) - padding,
        max(x_hi, 0) + padding,
        min(y_lo, 0) - padding,
        max(y_hi, 0) + padding,
    )


def _gr_scatter_axis_steps(points):
    """Match tick spacing used by _gr_svg_cartesian_frame for scatter graphs."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_pad = max(1, (max(xs) - min(xs)) * 0.12) if len(xs) > 1 else 1
    y_pad = max(1, (max(ys) - min(ys)) * 0.12) if len(ys) > 1 else 1
    x_lo, x_hi, y_lo, y_hi = _gr_bounds_with_origin(
        min(xs) - x_pad, max(xs) + x_pad,
        min(ys) - y_pad, max(ys) + y_pad,
        padding=0,
    )
    x_step = max(1, round((x_hi - x_lo) / 6))
    y_step = max(1, round((y_hi - y_lo) / 6))
    return x_step, y_step


def _gr_estimate_tolerance(axis_step):
    """Allow roughly half a grid square when reading from a graph."""
    return max(2, round(axis_step * 0.5))


def _gr_estimate_raw(value, tolerance, dp=0):
    val = _number_raw(value, dp) if dp else str(int(round(value)))
    return f"{val}~{int(tolerance)}"


def _gr_number_estimate_answer(value, tolerance, dp=0):
    return {
        'type': 'number_estimate',
        'value': value,
        'tolerance': tolerance,
        'dp': dp,
    }


def _gr_svg_cartesian_frame(PL, PR, PT, PB, W, H, x_lo, x_hi, y_lo, y_hi):
    """
    Grid, axes through (0, 0), and tick labels.
    Returns (grid, axes, ticks, sx, sy, x0_px, y0_px).
    """
    pw, ph = W - PL - PR, H - PT - PB
    x_span = max(1e-9, x_hi - x_lo)
    y_span = max(1e-9, y_hi - y_lo)

    def sx(v):
        return PL + (v - x_lo) / x_span * pw

    def sy(v):
        return PT + ph - (v - y_lo) / y_span * ph

    x0 = sx(0) if x_lo <= 0 <= x_hi else None
    y0 = sy(0) if y_lo <= 0 <= y_hi else None

    x_step = max(1, round(x_span / 6))
    y_step = max(1, round(y_span / 6))
    x_tick_start = int(x_lo // x_step) * x_step
    y_tick_start = int(y_lo // y_step) * y_step

    grid = ""
    for v in range(x_tick_start, int(x_hi) + x_step, x_step):
        xp = sx(v)
        if PL <= xp <= W - PR:
            grid += (
                f'<line x1="{xp:.0f}" y1="{PT}" x2="{xp:.0f}" y2="{PT + ph}" '
                f'stroke="#e8e4de" stroke-width="0.8"/>'
            )
    for v in range(y_tick_start, int(y_hi) + y_step, y_step):
        yp = sy(v)
        if PT <= yp <= PT + ph:
            grid += (
                f'<line x1="{PL}" y1="{yp:.0f}" x2="{W - PR}" y2="{yp:.0f}" '
                f'stroke="#e8e4de" stroke-width="0.8"/>'
            )

    axes = ""
    if x0 is not None:
        axes += (
            f'<line x1="{x0:.0f}" y1="{PT}" x2="{x0:.0f}" y2="{PT + ph}" '
            f'stroke="#555" stroke-width="1.5"/>'
        )
    if y0 is not None:
        axes += (
            f'<line x1="{PL}" y1="{y0:.0f}" x2="{W - PR}" y2="{y0:.0f}" '
            f'stroke="#555" stroke-width="1.5"/>'
        )

    ticks = ""
    x_tick_base = y0 if y0 is not None else PT + ph
    x_label_y = x_tick_base + 17
    for v in range(x_tick_start, int(x_hi) + x_step, x_step):
        xp = sx(v)
        if PL <= xp <= W - PR:
            ticks += (
                f'<line x1="{xp:.0f}" y1="{x_tick_base:.0f}" x2="{xp:.0f}" '
                f'y2="{x_tick_base + 4:.0f}" stroke="#555"/>'
            )
            ticks += f'<text x="{xp:.0f}" y="{x_label_y:.0f}" text-anchor="middle" font-size="11">{v}</text>'

    y_tick_x = (x0 - 10) if x0 is not None else PL - 7
    for v in range(y_tick_start, int(y_hi) + y_step, y_step):
        yp = sy(v)
        if PT <= yp <= PT + ph:
            tick_x = x0 if x0 is not None else PL
            ticks += (
                f'<line x1="{tick_x - 4:.0f}" y1="{yp:.0f}" x2="{tick_x:.0f}" '
                f'y2="{yp:.0f}" stroke="#555"/>'
            )
            ticks += f'<text x="{y_tick_x:.0f}" y="{yp + 4:.0f}" text-anchor="end" font-size="11">{v}</text>'

    return grid, axes, ticks, sx, sy, x0, y0


def _gr_axis_labels(W, H, PT, ph, x0, y0, x_lbl="x", y_lbl="y"):
    """Standard x/y axis titles positioned beside the origin axes."""
    axis_lbl_x = W // 2
    axis_lbl_y_x = (x0 - 28) if x0 is not None else 12
    axis_lbl_y_y = (y0 if y0 is not None else PT + ph // 2)
    return (
        f'<text x="{axis_lbl_x}" y="{H - 6}" text-anchor="middle" font-size="12">{x_lbl}</text>'
        f'<text x="{axis_lbl_y_x:.0f}" y="{axis_lbl_y_y:.0f}" '
        f'transform="rotate(-90,{axis_lbl_y_x:.0f},{axis_lbl_y_y:.0f})" '
        f'text-anchor="middle" font-size="12">{y_lbl}</text>'
    )


def _gr_svg_scatter(points, title="", xlabel="", ylabel="", lof=None):
    W, H = 440, 360
    PL, PR, PT, PB = 68, 22, 42, 55

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_pad = max(1, (max(xs) - min(xs)) * 0.12) if len(xs) > 1 else 1
    y_pad = max(1, (max(ys) - min(ys)) * 0.12) if len(ys) > 1 else 1
    x_lo, x_hi, y_lo, y_hi = _gr_bounds_with_origin(
        min(xs) - x_pad, max(xs) + x_pad,
        min(ys) - y_pad, max(ys) + y_pad,
        padding=0,
    )

    grid, axes, ticks, sx, sy, x0, y0 = _gr_svg_cartesian_frame(
        PL, PR, PT, PB, W, H, x_lo, x_hi, y_lo, y_hi
    )

    pts_svg = "".join(
        f'<circle cx="{sx(x):.0f}" cy="{sy(y):.0f}" r="5" fill="#01696f"/>'
        for x, y in points
    )

    line_svg = ""
    if lof:
        m, c = lof
        lx1, lx2 = x_lo, x_hi
        ly1, ly2 = m * lx1 + c, m * lx2 + c
        if m != 0:
            if ly1 < y_lo:
                lx1, ly1 = (y_lo - c) / m, y_lo
            elif ly1 > y_hi:
                lx1, ly1 = (y_hi - c) / m, y_hi
            if ly2 < y_lo:
                lx2, ly2 = (y_lo - c) / m, y_lo
            elif ly2 > y_hi:
                lx2, ly2 = (y_hi - c) / m, y_hi
        line_svg = (
            f'<line x1="{sx(lx1):.0f}" y1="{sy(ly1):.0f}" x2="{sx(lx2):.0f}" y2="{sy(ly2):.0f}" '
            f'stroke="#a13544" stroke-width="2" stroke-dasharray="6,4"/>'
        )

    title_block = (
        f'<text x="{W // 2}" y="26" text-anchor="middle" font-size="14" '
        f'font-weight="bold" fill="#333">{title}</text>'
        if title else ""
    )
    axis_lbl = _gr_axis_labels(W, H, PT, H - PT - PB, x0, y0, xlabel or "x", ylabel or "y")

    return (
        f'<div style="text-align:center;margin:10px 0;">'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
        f'{grid}{axes}{ticks}{pts_svg}{line_svg}{title_block}{axis_lbl}'
        f'</svg></div>'
    )




def _gr_svg_line(m, c, title="", show_y_intercept_marker=False):
    """Line graph for y = mx + c; axes at x = 0 and y = 0."""
    W, H = 340, 310
    PL, PR, PT, PB = 60, 20, 38, 52
    x_min, x_max = -5, 5
    y_at_edges = [m * x_min + c, m * x_max + c, c]
    x_lo, x_hi, y_lo, y_hi = _gr_bounds_with_origin(
        x_min, x_max, min(y_at_edges) - 2, max(y_at_edges) + 2, padding=0
    )

    grid, axes, ticks, sx, sy, x0, y0 = _gr_svg_cartesian_frame(
        PL, PR, PT, PB, W, H, x_lo, x_hi, y_lo, y_hi
    )

    yint_dot = ""
    if show_y_intercept_marker and y_lo <= c <= y_hi and x_lo <= 0 <= x_hi and x0 is not None:
        yint_dot = f'<circle cx="{x0:.0f}" cy="{sy(c):.0f}" r="5" fill="#a13544"/>'

    title_block = (
        f'<text x="{W // 2}" y="24" text-anchor="middle" font-size="13" font-weight="bold">{title}</text>'
        if title else ""
    )
    axis_lbl = _gr_axis_labels(W, H, PT, H - PT - PB, x0, y0)

    return (
        f'<div style="text-align:center;margin:10px 0;">'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
        f'{grid}{axes}{ticks}'
        f'<line x1="{sx(x_min):.0f}" y1="{sy(m * x_min + c):.0f}" '
        f'x2="{sx(x_max):.0f}" y2="{sy(m * x_max + c):.0f}" stroke="#01696f" stroke-width="2.5"/>'
        f'{yint_dot}{title_block}{axis_lbl}'
        f'</svg></div>'
    )


def _gr_svg_coord_grid(x_pt, y_pt):
    """Coordinate grid (−6 to 6) with one plotted point highlighted."""
    W, H = 310, 310
    CX, CY, SC = 155, 155, 22

    def sx(v): return CX + v * SC
    def sy(v): return CY - v * SC

    gh = "".join(f'<line x1="{sx(-6)}" y1="{sy(j)}" x2="{sx(6)}" y2="{sy(j)}" stroke="#e0ddd6" stroke-width="0.8"/>' for j in range(-6, 7))
    gv = "".join(f'<line x1="{sx(i)}" y1="{sy(-6)}" x2="{sx(i)}" y2="{sy(6)}" stroke="#e0ddd6" stroke-width="0.8"/>' for i in range(-6, 7))
    lbls = "".join(
        f'<text x="{sx(i)}" y="{CY+15}" text-anchor="middle" font-size="10" fill="#888">{i}</text>'
        f'<text x="{CX-12}" y="{sy(i)+4}" text-anchor="end" font-size="10" fill="#888">{i}</text>'
        for i in range(-5, 6) if i != 0
    )
    lx = sx(x_pt) + (10 if x_pt <= 3 else -10)
    anchor = "start" if x_pt <= 3 else "end"
    return (f'<div style="text-align:center;margin:10px 0;">'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
            f' style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
            f'{gh}{gv}'
            f'<line x1="{sx(-6)}" y1="{CY}" x2="{sx(6)}" y2="{CY}" stroke="#555" stroke-width="1.5"/>'
            f'<line x1="{CX}" y1="{sy(-6)}" x2="{CX}" y2="{sy(6)}" stroke="#555" stroke-width="1.5"/>'
            f'{lbls}'
            f'<text x="{sx(6)+8}" y="{CY+5}" font-size="12" fill="#555">x</text>'
            f'<text x="{CX+5}" y="{sy(6)-5}" font-size="12" fill="#555">y</text>'
            f'<circle cx="{sx(x_pt)}" cy="{sy(y_pt)}" r="6" fill="#a13544"/>'
            f'<text x="{lx}" y="{sy(y_pt)-10}" font-size="12" font-weight="bold" fill="#a13544" text-anchor="{anchor}">({x_pt},{y_pt})</text>'
            f'</svg></div>')


def _gr_svg_two_point_line(x1, y1, x2, y2, label_points=False):
    """Two points on a line segment; GCSE axes at x = 0 and y = 0."""
    W, H = 320, 290
    PL, PR, PT, PB = 55, 22, 32, 50
    pad = 1
    x_lo, x_hi, y_lo, y_hi = _gr_bounds_with_origin(
        min(x1, x2) - pad, max(x1, x2) + pad,
        min(y1, y2) - pad, max(y1, y2) + pad,
        padding=0,
    )

    grid, axes, ticks, sx, sy, x0, y0 = _gr_svg_cartesian_frame(
        PL, PR, PT, PB, W, H, x_lo, x_hi, y_lo, y_hi
    )

    labels = ""
    if label_points:
        labels = (
            f'<text x="{sx(x1) + 8:.0f}" y="{sy(y1) - 8:.0f}" font-size="11" fill="#01696f">'
            f'({x1},{y1})</text>'
            f'<text x="{sx(x2) + 8:.0f}" y="{sy(y2) - 8:.0f}" font-size="11" fill="#01696f">'
            f'({x2},{y2})</text>'
        )

    axis_lbl = _gr_axis_labels(W, H, PT, H - PT - PB, x0, y0)

    return (
        f'<div style="text-align:center;margin:10px 0;">'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
        f'{grid}{axes}{ticks}'
        f'<line x1="{sx(x1):.0f}" y1="{sy(y1):.0f}" x2="{sx(x2):.0f}" y2="{sy(y2):.0f}" '
        f'stroke="#01696f" stroke-width="2.5"/>'
        f'{labels}{axis_lbl}'
        f'</svg></div>'
    )


def _gr_svg_quadratic(a, b, c, line=None):
    """Parabola y = ax² + bx + c on GCSE axes; optional line y = mx + d as (m, d)."""
    W, H = 360, 310
    PL, PR, PT, PB = 58, 22, 38, 52

    tp_x = -b / (2 * a)
    xs = {tp_x, 0}
    disc = b * b - 4 * a * c
    if disc >= 0:
        sd = disc ** 0.5
        xs.add((-b - sd) / (2 * a))
        xs.add((-b + sd) / (2 * a))

    if line:
        m, d = line
        qa = a
        qb = b - m
        qc = c - d
        qdisc = qb * qb - 4 * qa * qc
        if qdisc >= 0:
            qsd = qdisc ** 0.5
            xs.add((-qb - qsd) / (2 * qa))
            xs.add((-qb + qsd) / (2 * qa))

    x_pad = 1.5
    x_lo = min(xs) - x_pad
    x_hi = max(xs) + x_pad
    sample_x = [x_lo + (x_hi - x_lo) * i / 28 for i in range(29)]
    y_vals = [_gr_quad_y(x, a, b, c) for x in sample_x]
    if line:
        m, d = line
        y_vals.extend(m * x + d for x in sample_x)
    y_lo = min(y_vals) - 2
    y_hi = max(y_vals) + 2
    x_lo, x_hi, y_lo, y_hi = _gr_bounds_with_origin(x_lo, x_hi, y_lo, y_hi, padding=0)

    grid, axes, ticks, sx, sy, x0, y0 = _gr_svg_cartesian_frame(
        PL, PR, PT, PB, W, H, x_lo, x_hi, y_lo, y_hi
    )

    quad_pts = " ".join(
        f"{sx(x):.0f},{sy(_gr_quad_y(x, a, b, c)):.0f}" for x in sample_x
    )
    curve = (
        f'<polyline points="{quad_pts}" fill="none" stroke="#1a6fa8" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
    )

    line_svg = ""
    if line:
        m, d = line
        lx1, lx2 = x_lo, x_hi
        ly1, ly2 = m * lx1 + d, m * lx2 + d
        if m != 0:
            if ly1 < y_lo:
                lx1, ly1 = (y_lo - d) / m, y_lo
            elif ly1 > y_hi:
                lx1, ly1 = (y_hi - d) / m, y_hi
            if ly2 < y_lo:
                lx2, ly2 = (y_lo - d) / m, y_lo
            elif ly2 > y_hi:
                lx2, ly2 = (y_hi - d) / m, y_hi
        line_svg = (
            f'<line x1="{sx(lx1):.0f}" y1="{sy(ly1):.0f}" x2="{sx(lx2):.0f}" '
            f'y2="{sy(ly2):.0f}" stroke="#a13544" stroke-width="2.5"/>'
        )

    axis_lbl = _gr_axis_labels(W, H, PT, H - PT - PB, x0, y0)

    return (
        f'<div style="text-align:center;margin:10px 0;">'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
        f'{grid}{axes}{ticks}{curve}{line_svg}{axis_lbl}'
        f'</svg></div>'
    )


def _gr_svg_distance_time(distance, time_hr):
    """Distance-time graph from (0, 0); axes at x = 0 and y = 0."""
    W, H = 340, 280
    PL, PR, PT, PB = 60, 22, 32, 52
    x_lo, x_hi, y_lo, y_hi = _gr_bounds_with_origin(
        0, time_hr + 0.3, 0, distance * 1.12, padding=0
    )

    grid, axes, ticks, sx, sy, x0, y0 = _gr_svg_cartesian_frame(
        PL, PR, PT, PB, W, H, x_lo, x_hi, y_lo, y_hi
    )
    axis_lbl = _gr_axis_labels(
        W, H, PT, H - PT - PB, x0, y0, "Time (hours)", "Distance (km)"
    )

    return (
        f'<div style="text-align:center;margin:10px 0;">'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'style="background:#f9f8f5;border-radius:8px;display:block;margin:0 auto;max-width:100%;">'
        f'{grid}{axes}{ticks}'
        f'<line x1="{sx(0):.0f}" y1="{sy(0):.0f}" x2="{sx(time_hr):.0f}" y2="{sy(distance):.0f}" '
        f'stroke="#01696f" stroke-width="2.5"/>'
        f'{axis_lbl}'
        f'</svg></div>'
    )


# ---- Graph helper functions ----

def _gr_linear_eq_raw(m, c):
    return f"{int(m)}|{int(c)}"


def _gr_linear_eq_field_value(m, c):
    """Colon form for use inside pipe-delimited number_fields payloads."""
    return f"{int(m)}:{int(c)}"


def _gr_linear_eq_answer(m, c):
    return {'type': 'linear_equation', 'm': int(m), 'c': int(c)}


def _gr_quadrant_choice(quadrant):
    options = [
        'A  Quadrant I',
        'B  Quadrant II',
        'C  Quadrant III',
        'D  Quadrant IV',
    ]
    letters = {'I': 'A', 'II': 'B', 'III': 'C', 'IV': 'D'}
    return {
        'type': 'choice',
        'options': options,
        'correct': letters[quadrant],
    }


def _gr_correlation_choice(kind):
    options = [
        'A  Positive correlation',
        'B  Negative correlation',
        'C  No correlation',
    ]
    letters = {'positive': 'A', 'negative': 'B', 'none': 'C'}
    return {
        'type': 'choice',
        'options': options,
        'correct': letters[kind],
    }


def _gra_coordinate_quadrant():
    x, y = random.choice([-5,-4,-3,3,4,5]), random.choice([-5,-4,-3,3,4,5])
    if x > 0 and y > 0: qd = 'I'
    elif x < 0 and y > 0: qd = 'II'
    elif x < 0 and y < 0: qd = 'III'
    else: qd = 'IV'
    svg = _gr_svg_coord_grid(x, y)
    q = f"The point ({x}, {y}) is plotted on the grid below. Which quadrant does it lie in?\n{svg}"
    s = f"x is {'positive' if x>0 else 'negative'}, y is {'positive' if y>0 else 'negative'} → <strong>Quadrant {qd}</strong>."
    hint = "Quadrant I: (+,+)  II: (−,+)  III: (−,−)  IV: (+,−)."
    return q, s, hint, 1, _gr_quadrant_choice(qd)


def _gra_substitute_linear():
    m, c, x = random.randint(2, 6), random.randint(-5, 8), random.randint(-3, 7)
    eq = _gr_fmt_linear(m, c)
    y = m * x + c
    q = f"For {eq}, find y when x = {x}."
    if c >= 0:
        s = f"y = {m}×{x} + {c} = {y}."
    else:
        s = f"y = {m}×{x} − {abs(c)} = {y}."
    hint = "Substitute x into the equation."
    return q, s, hint, 1, y


def _gra_gradient_two_points():
    x1, y1 = random.randint(-3, 3), random.randint(-4, 4)
    m = random.randint(1, 5)
    x2 = x1 + random.randint(2, 6)
    y2 = y1 + m * (x2 - x1)
    svg = _gr_svg_two_point_line(x1, y1, x2, y2)
    q = f"Find the gradient of the line through ({x1},\u2009{y1}) and ({x2},\u2009{y2}).\n{svg}"
    s = f"Gradient = ({y2}\u2212{y1})\u00f7({x2}\u2212{x1}) = <strong>{m}</strong>."
    hint = "Gradient = rise \u00f7 run = change in y \u00f7 change in x."
    return q, s, hint, 2, m


def _gra_y_intercept():
    m, c = random.randint(-5, 5), random.randint(-8, 8)
    if m == 0:
        m = 2
    svg = _gr_svg_line(m, c, show_y_intercept_marker=False)
    eq = _gr_fmt_linear(m, c)
    x0 = random.choice([-3, -2, -1, 1, 2, 3])
    y0 = m * x0 + c
    q = (f"A straight line passes through the point ({x0},\u2009{y0}), as shown on the graph. "
         f"Find the y‑intercept (where the line crosses the y‑axis).\n{svg}")
    s = (
        f"The line crosses the y‑axis where x = 0. Reading from the graph, that point is (0, {c}).<br>"
        f"So the y‑intercept is <strong>{c}</strong> (equation: {eq})."
    )
    hint = "Find where the line crosses the vertical axis through the origin (x = 0)."
    return q, s, hint, 1, c


def _gra_equation_from_gradient_intercept():
    m, c = random.randint(-5,5), random.randint(-8,8)
    if m == 0: m = 3
    eq = _gr_fmt_linear(m, c)
    q = f"A line has gradient {m} and y‑intercept {c}. Write its equation."
    s = f"y = mx + c → {eq}."
    hint = "Use y = mx + c."
    return q, s, hint, 2, _gr_linear_eq_answer(m, c)



def _gra_parallel_gradient():
    m, c = random.randint(-5,5), random.randint(-8,8)
    if m == 0: m = -2
    eq = _gr_fmt_linear(m, c)
    q = f"A line is parallel to {eq}. What is its gradient?"
    s = f"Parallel lines have the same gradient: {m}."
    hint = "Parallel lines have equal gradients."
    return q, s, hint, 1, m



def _gra_distance_time_speed():
    distance, time = random.randint(20, 120), random.choice([2, 3, 4, 5, 6])
    mover = random.choice(["a car", "a cyclist", "a train", "a hiker", "a delivery van", "a runner"])
    svg = _gr_svg_distance_time(distance, time)
    q = (f"The distance‑time graph below shows {mover} travelling {distance}\u2009km in {time}\u2009hours "
         f"at a constant speed. Find its speed.\n{svg}")
    s = (f"Speed = gradient of line = distance \u00f7 time<br>"
         f"= {distance} \u00f7 {time} = <strong>{distance/time:.1f}\u2009km/h</strong>.")
    hint = "The gradient of a distance\u2013time graph equals the speed."
    return q, s, hint, 2, _number_raw(distance / time)


def _gra_quadratic_substitute():
    a, b, c, x = 1, random.randint(-4, 4), random.randint(-5, 5), random.randint(-3, 4)
    y = a * x * x + b * x + c
    rhs = "x²"
    if b != 0:
        if b == 1:
            rhs += " + x"
        elif b == -1:
            rhs += " − x"
        elif b > 0:
            rhs += f" + {b}x"
        else:
            rhs += f" − {abs(b)}x"
    if c != 0:
        if c > 0:
            rhs += f" + {c}"
        else:
            rhs += f" − {abs(c)}"
    q = f"For y = {rhs}, find y when x = {x}."
    s = f"When x = {x}: ({x})² + ({b})×({x}) + ({c}) = {x*x} + {b*x} + {c} = {y}."
    hint = "Substitute carefully."
    return q, s, hint, 2, y


def _gra_root_from_factorised():
    r1, r2 = random.sample(range(-5,6), 2)
    b1 = _gr_fmt_bracket(r1)
    b2 = _gr_fmt_bracket(r2)
    q = f"Find the roots of y = {b1}{b2}."
    s = f"Set each bracket to zero → x = {r1}, x = {r2}."
    hint = "Roots when y = 0."
    return q, s, hint, 2, _number_pair_answer(r1, r2, 'First root', 'Second root')



def _gra_midpoint():
    x1,y1,x2,y2 = random.randint(-5,5), random.randint(-5,5), random.randint(-5,5), random.randint(-5,5)
    mx, my = (x1+x2)/2, (y1+y2)/2
    q = f"Find the midpoint of ({x1}, {y1}) and ({x2}, {y2})."
    s = f"Midpoint = (({x1}+{x2})/2, ({y1}+{y2})/2) = ({mx:.1f}, {my:.1f})."
    hint = "Average the coordinates."
    return q, s, hint, 2, _number_pair_answer(mx, my, 'x-coordinate', 'y-coordinate', sep=',')


def _gra_line_intersection_simple():
    m1,c1,m2,c2 = 2, random.randint(-4,4), -1, random.randint(2,8)
    x = (c2-c1)/(m1-m2); y = m1*x + c1
    q = f"Find the intersection of y = {m1}x + {c1} and y = {m2}x + {c2}."
    s = f"Set equal → {m1}x + {c1} = {m2}x + {c2} → x = {x:.2f}, y = {y:.2f}."
    hint = "At intersection, both equations give same x and y."
    return q, s, hint, 3, _number_pair_answer(round(x, 2), round(y, 2), 'x', 'y', sep=',')


def _gra_reciprocal_value():
    k, x = random.choice([6,8,10,12,15,20]), random.choice([2,3,4,5])
    q = f"For y = {k}/x, find y when x = {x}."
    s = f"y = {k}/{x} = {k/x:.2f}."
    hint = "Substitute into the reciprocal equation."
    return q, s, hint, 1, _number_raw(k / x)


def _gra_cubic_substitute():
    a = random.randint(-3, 3)
    b = random.randint(-6, 6)
    x = random.choice([-3, -2, -1, 1, 2, 3])
    y = x**3 + a * x + b
    terms = "x\u00b3"
    if a:
        terms += f" + {a}x" if a > 0 else f" \u2212 {abs(a)}x"
    if b:
        terms += f" + {b}" if b > 0 else f" \u2212 {abs(b)}"
    q = f"For y = {terms}, find y when x = {x}."
    ax_str = f" + {a}\u00d7({x})" if a >= 0 else f" \u2212 {abs(a)}\u00d7({x})"
    b_str = f" + {b}" if b >= 0 else f" \u2212 {abs(b)}"
    s = f"({x})\u00b3{ax_str}{b_str} = {x**3} + {a*x} + {b} = <strong>{y}</strong>."
    hint = "Cube first, then add the remaining terms."
    return q, s, hint, 2, y


# ---- Scatter‑graph correlation questions ----

def _gra_scatter_positive():
    n = random.randint(8, 15)
    points = [(i + random.uniform(-0.5, 0.5), 2*i + random.uniform(-1, 1)) for i in range(n)]
    svg = _gr_svg_scatter(points, "Scatter graph", "x", "y", (2, 0))
    q = f"Scatter graph:\n{svg}\nWhat type of correlation does this show?"
    s = "Positive correlation (y increases as x increases)."
    hint = "Look at the overall direction."
    return q, s, hint, 1, _gr_correlation_choice('positive')


def _gra_scatter_negative():
    n = random.randint(8, 15)
    points = [(i + random.uniform(-0.5, 0.5), -2*i + 20 + random.uniform(-1, 1)) for i in range(n)]
    svg = _gr_svg_scatter(points, "Scatter graph", "x", "y", (-2, 20))
    q = f"Scatter graph:\n{svg}\nWhat type of correlation does this show?"
    s = "Negative correlation (y decreases as x increases)."
    hint = "Points slope downwards."
    return q, s, hint, 1, _gr_correlation_choice('negative')


def _gra_scatter_no_correlation():
    n = random.randint(10, 18)
    points = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(n)]
    svg = _gr_svg_scatter(points, "Scatter graph", "x", "y")
    q = f"Scatter graph:\n{svg}\nWhat type of correlation does this show?"
    s = "No correlation (no clear pattern)."
    hint = "Points show no upward or downward trend."
    return q, s, hint, 1, _gr_correlation_choice('none')


def _gra_scatter_line_of_best_fit():
    m = random.randint(2, 5)
    c = random.randint(1, 5)
    n = random.randint(8, 14)
    points = [(i + random.uniform(-0.8, 0.8), m*i + c + random.uniform(-2, 2)) for i in range(n)]
    svg = _gr_svg_scatter(points, "Scatter graph", "Hours", "Score", (m, c))
    # ask to estimate value for x = something
    xq = random.randint(3, 8)
    y_val = m * xq + c
    x_step, y_step = _gr_scatter_axis_steps(points)
    y_tol = _gr_estimate_tolerance(y_step)
    y_disp = int(round(y_val))
    q = f"Scatter graph:\n{svg}\nUse the line of best fit to estimate y when x = {xq}."
    s = (
        f"On the line, when x ≈ {xq}, y ≈ {y_disp} "
        f"(accept estimates within ±{y_tol})."
    )
    hint = "Read from the line, not from individual points."
    return q, s, hint, 3, _gr_number_estimate_answer(y_val, y_tol)


# ---------- GRAPHS difficult (multi-step, a/b/c) ----------

def _gra_diff_line_equation_multipart():
    """Straight line through two points: gradient, y-intercept, then equation."""
    x1, y1 = random.randint(-2, 2), random.randint(-4, 4)
    m = random.randint(2, 5) * random.choice([-1, 1])
    x2 = x1 + random.randint(3, 6) * (1 if m > 0 else -1)
    y2 = y1 + m * (x2 - x1)
    c = y1 - m * x1
    eq = _gr_fmt_linear(m, c)
    svg = _gr_svg_two_point_line(x1, y1, x2, y2)
    intro = (
        f"The graph shows a straight line through ({x1},\u2009{y1}) and ({x2},\u2009{y2})."
    )
    q = f"{intro}\n{svg}" + _ratio_abc_block(
        "Find the gradient of the line.",
        "Find the y-intercept.",
        "Write the equation of the line in the form y = mx + c.",
    )
    s = (
        f"{intro}<br><br>"
        f"<strong>a)</strong> Gradient = ({y2}\u2212{y1})\u00f7({x2}\u2212{x1}) "
        f"= {y2 - y1}\u00f7{x2 - x1} = <strong>{m}</strong>.<br><br>"
        f"<strong>b)</strong> Using y = mx + c with ({x1}, {y1}):<br>"
        f"{y1} = {m}\u00d7{x1} + c \u21d2 c = <strong>{c}</strong>.<br><br>"
        f"<strong>c)</strong> Equation: <strong>{eq}</strong>."
    )
    hint = "Gradient = change in y \u00f7 change in x; then substitute a point to find c."
    return q, s, hint, 5, _ratio_fields_answer(
        (m, c, _gr_linear_eq_field_value(m, c)),
        (
            'Part (a): gradient',
            'Part (b): y-intercept',
            'Part (c): equation (y = mx + c)',
        ),
        ('number', 'number', 'linear_equation'),
    )


def _gra_diff_journey_multipart():
    """Distance\u2013time graph: speed, further distance, and time for a longer journey."""
    distance = random.randint(40, 120)
    time_hr = random.choice([2, 3, 4, 5, 6])
    speed = distance / time_hr
    extra_hr = random.randint(1, 3)
    extra_dist = speed * extra_hr
    double_dist = 2 * distance
    double_time = double_dist / speed
    svg = _gr_svg_distance_time(distance, time_hr)
    intro = (
        f"A cyclist travels at a constant speed. The distance\u2013time graph shows "
        f"a journey of {distance}\u2009km in {time_hr}\u2009hours."
    )
    q = f"{intro}\n{svg}" + _ratio_abc_block(
        "Find the cyclist\u2019s speed in km/h.",
        f"At the same speed, how far would the cyclist travel in another {extra_hr}\u2009hours?",
        f"How long would it take to travel {double_dist}\u2009km at the same speed?",
    )
    s = (
        f"{intro}<br><br>"
        f"<strong>a)</strong> Speed = gradient = distance \u00f7 time "
        f"= {distance} \u00f7 {time_hr} = <strong>{_fmt_num(speed)} km/h</strong>.<br><br>"
        f"<strong>b)</strong> Distance = speed \u00d7 time = {_fmt_num(speed)} \u00d7 {extra_hr} "
        f"= <strong>{_fmt_num(extra_dist)} km</strong>.<br><br>"
        f"<strong>c)</strong> Time = distance \u00f7 speed = {double_dist} \u00f7 {_fmt_num(speed)} "
        f"= <strong>{_fmt_num(double_time)} hours</strong>."
    )
    hint = "Use the gradient of the distance\u2013time graph for speed; then distance = speed \u00d7 time."
    return q, s, hint, 5, _ratio_fields_answer(
        (_number_raw(speed), _number_raw(extra_dist), _number_raw(double_time)),
        (
            'Part (a): speed (km/h)',
            f'Part (b): distance in {extra_hr} hours (km)',
            f'Part (c): time for {double_dist} km (hours)',
        ),
    )


def _gra_diff_scatter_multipart():
    """Scatter graph: correlation, estimate y from x, then estimate x from y."""
    m = random.randint(2, 5)
    c = random.randint(3, 12)
    n = random.randint(10, 14)
    points = [
        (i + random.uniform(-0.6, 0.6), m * i + c + random.uniform(-2, 2))
        for i in range(n)
    ]
    xq = random.randint(4, n - 2)
    y_est = m * xq + c
    yq = int(m * (n // 2) + c)
    x_est = (yq - c) / m
    x_step, y_step = _gr_scatter_axis_steps(points)
    y_tol = _gr_estimate_tolerance(y_step)
    x_tol = _gr_estimate_tolerance(x_step)
    ctx, xl, yl, bq, cq, corr = random.choice([
        ("the revision hours and test scores of {n} students", "Revision hours", "Test score",
         f"estimate the test score when a student revises for {xq} hours",
         f"estimate how many hours of revision are needed for a test score of {yq}",
         "As revision hours increase, test scores tend to increase"),
        ("the daily temperature and ice creams sold on {n} days", "Temperature (\u00b0C)", "Ice creams sold",
         f"estimate the number of ice creams sold when the temperature is {xq}\u00b0C",
         f"estimate the temperature when {yq} ice creams are sold",
         "As the temperature increases, ice cream sales tend to increase"),
        ("the heights and weights of {n} people", "Height", "Weight",
         f"estimate the weight when the height reading is {xq}",
         f"estimate the height when the weight reading is {yq}",
         "As height increases, weight tends to increase"),
        ("the practice sessions and goals scored by {n} players", "Practice sessions", "Goals scored",
         f"estimate the goals scored after {xq} practice sessions",
         f"estimate the practice sessions needed to score {yq} goals",
         "As the number of practice sessions increases, goals scored tend to increase"),
        ("the advertising spend and sales over {n} weeks", "Advert spend", "Sales",
         f"estimate the sales when the advert spend reading is {xq}",
         f"estimate the advert spend needed for sales of {yq}",
         "As advertising spend increases, sales tend to increase"),
    ])
    svg = _gr_svg_scatter(points, f"{xl} vs {yl}", xl, yl, (m, c))
    intro = f"A study recorded {ctx.format(n=n)}. The scatter graph and line of best fit are shown."
    q = f"{intro}\n{svg}" + _ratio_abc_block(
        "Describe the correlation shown.",
        bq[0].upper() + bq[1:] + ".",
        "Use the same line to " + cq + ".",
    )
    s = (
        f"{intro}<br><br>"
        f"<strong>a)</strong> {corr} \u2192 <strong>positive correlation</strong>.<br><br>"
        f"<strong>b)</strong> On the line of best fit, when x \u2248 {xq}, y \u2248 "
        f"{m}\u00d7{xq} + {c} = <strong>{int(round(y_est))}</strong> "
        f"(accept answers within \u00b1{y_tol}).<br><br>"
        f"<strong>c)</strong> Set y = {yq}: {yq} = {m}x + {c} \u21d2 x = ({yq}\u2212{c})\u00f7{m} "
        f"\u2248 <strong>{_fmt_num(x_est, 1)}</strong> "
        f"(accept answers within \u00b1{x_tol})."
    )
    hint = (
        "State whether the trend is positive, negative, or none; read from the line of best fit "
        "for (b), and rearrange y = mx + c for (c)."
    )
    return q, s, hint, 5, _ratio_fields_answer(
        ('positive', _gr_estimate_raw(y_est, y_tol), _gr_estimate_raw(x_est, x_tol, dp=1)),
        (
            'Part (a): correlation (positive / negative / none)',
            'Part (b): estimated y',
            'Part (c): estimated x',
        ),
        ('keyword', 'number_estimate', 'number_estimate'),
    )


def _gra_diff_quadratic_features_multipart():
    """Quadratic graph: y-intercept, roots, then minimum point."""
    r1, r2 = sorted(random.sample(range(-5, 4), 2))
    b = -(r1 + r2)
    c = r1 * r2
    eq = _gr_fmt_quadratic(1, b, c)
    tp_x = (r1 + r2) / 2
    tp_y = _gr_quad_y(tp_x, 1, b, c)
    fac = f"{_gr_fmt_bracket(r1)}{_gr_fmt_bracket(r2)}"
    svg = _gr_svg_quadratic(1, b, c)
    intro = f"The graph shows the quadratic {eq}."
    q = f"{intro}\n{svg}" + _ratio_abc_block(
        "Write the y-intercept.",
        "Find the roots (the x-values where y = 0).",
        "Find the coordinates of the minimum point.",
    )
    roots_txt = (
        f"x = {r1} and x = {r2}"
        if r1 != r2
        else f"x = {r1} (repeated root)"
    )
    s = (
        f"{intro}<br><br>"
        f"<strong>a)</strong> When x = 0, y = <strong>{c}</strong> "
        f"(the curve crosses the y-axis at (0, {c})).<br><br>"
        f"<strong>b)</strong> Set y = 0: {fac} = 0 "
        f"(or solve {eq.replace('y = ', '')} = 0) \u21d2 <strong>{roots_txt}</strong>.<br><br>"
        f"<strong>c)</strong> Minimum at x = \u2212b\u00f7(2a) = {b}\u00f72 = {tp_x:.1f}.<br>"
        f"y = ({tp_x:.1f})\u00b2 + ({b})({tp_x:.1f}) + ({c}) = <strong>({tp_x:.1f}, {tp_y:.1f})</strong>."
    )
    hint = (
        "Read the y-intercept at x = 0; roots are where the curve crosses the x-axis; "
        "the minimum of a positive x² graph is at x = \u2212b/(2a)."
    )
    return q, s, hint, 5, _ratio_fields_answer(
        (c, r1, r2, _number_raw(tp_x, dp=1), _number_raw(tp_y, dp=1)),
        (
            'Part (a): y-intercept',
            'Part (b): first root',
            'Part (b): second root',
            'Part (c): minimum x',
            'Part (c): minimum y',
        ),
    )


def _gra_diff_quadratic_intersection_multipart():
    """Solve x² = mx + c using a graph of y = x² and a straight line."""
    while True:
        x_lo, x_hi = sorted(random.sample(range(-4, 6), 2))
        # x² = mx + k has roots x_lo, x_hi ⇒ m = sum of roots, k = −(product).
        m = x_lo + x_hi
        k = -(x_lo * x_hi)
        if m != 0 and k != 0:  # avoid degenerate "0x"/"+ 0" formatting
            break
    y_lo, y_hi = x_lo * x_lo, x_hi * x_hi
    line_txt = _gr_fmt_linear(m, k)
    line_rhs = line_txt.replace("y = ", "")
    svg = _gr_svg_quadratic(1, 0, 0, line=(m, k))
    intro = f"The graph shows <strong>y = x²</strong> and <strong>{line_txt}</strong>."
    q = f"{intro}\n{svg}" + _ratio_abc_block(
        "Write the coordinates of one point where the graphs intersect.",
        "Write the coordinates of the other point of intersection.",
        f"Solve x² = {line_rhs} algebraically to verify your answers.",
    )
    k_term = f"\u2212 {k}" if k >= 0 else f"+ {abs(k)}"
    m_coeff = "" if abs(m) == 1 else str(abs(m))
    m_term = f"\u2212 {m_coeff}x" if m >= 0 else f"+ {m_coeff}x"
    s = (
        f"{intro}<br><br>"
        f"<strong>a)</strong> One intersection: read from the graph \u2192 "
        f"<strong>({x_lo}, {y_lo})</strong>.<br><br>"
        f"<strong>b)</strong> The other intersection: <strong>({x_hi}, {y_hi})</strong>.<br><br>"
        f"<strong>c)</strong> x² = {line_rhs} \u21d2 x² {m_term} {k_term} = 0.<br>"
        f"Factorise: {_gr_fmt_bracket(x_lo)}{_gr_fmt_bracket(x_hi)} = 0.<br>"
        f"So x = <strong>{x_lo}</strong> or x = <strong>{x_hi}</strong>."
    )
    hint = (
        "Intersections are where the curves meet; set the equations equal and "
        "factorise (or use the quadratic formula)."
    )
    return q, s, hint, 5, _ratio_fields_answer(
        (x_lo, y_lo, x_hi, y_hi, x_lo, x_hi),
        (
            'Part (a): intersection x',
            'Part (a): intersection y',
            'Part (b): other intersection x',
            'Part (b): other intersection y',
            'Part (c): first root',
            'Part (c): second root',
        ),
    )


# ---- Wrappers (ensuring the variants list is 10+ entries) ----

def _gra_found_01(): return _gra_coordinate_quadrant()
def _gra_found_02(): return _gra_substitute_linear()
def _gra_found_03(): return _gra_gradient_two_points()
def _gra_found_04(): return _gra_y_intercept()
def _gra_found_05(): return _gra_equation_from_gradient_intercept()
def _gra_found_06(): return _gra_parallel_gradient()
def _gra_found_07(): return _gra_distance_time_speed()
def _gra_found_08(): return _gra_midpoint()
def _gra_found_09(): return _gra_reciprocal_value()
def _gra_found_10(): return _gra_scatter_positive()
def _gra_found_11(): return _gra_scatter_negative()
def _gra_found_12(): return _gra_scatter_no_correlation()
def _gra_found_13(): return _gra_substitute_linear()
def _gra_found_14(): return _gra_y_intercept()
def _gra_found_15(): return _gra_midpoint()

def _gra_inter_01(): return _gra_gradient_two_points()
def _gra_inter_02(): return _gra_equation_from_gradient_intercept()
def _gra_inter_03(): return _gra_parallel_gradient()
def _gra_inter_04(): return _gra_distance_time_speed()
def _gra_inter_05(): return _gra_quadratic_substitute()
def _gra_inter_06(): return _gra_root_from_factorised()
def _gra_inter_07(): return _gra_midpoint()
def _gra_inter_08(): return _gra_line_intersection_simple()
def _gra_inter_09(): return _gra_reciprocal_value()
def _gra_inter_10(): return _gra_cubic_substitute()
def _gra_inter_11(): return _gra_scatter_positive()
def _gra_inter_12(): return _gra_scatter_negative()
def _gra_inter_13(): return _gra_scatter_no_correlation()
def _gra_inter_14(): return _gra_scatter_line_of_best_fit()
def _gra_inter_15(): return _gra_root_from_factorised()

def _gra_diff_01(): return _gra_diff_line_equation_multipart()
def _gra_diff_02(): return _gra_diff_quadratic_features_multipart()
def _gra_diff_03(): return _gra_root_from_factorised()
def _gra_diff_04(): return _gra_diff_quadratic_intersection_multipart()
def _gra_diff_05(): return _gra_reciprocal_value()
def _gra_diff_06(): return _gra_diff_scatter_multipart()
def _gra_diff_07(): return _gra_midpoint()
def _gra_diff_08(): return _gra_line_intersection_simple()
def _gra_diff_09(): return _gra_equation_from_gradient_intercept()
def _gra_diff_10(): return _gra_diff_journey_multipart()
def _gra_diff_11(): return _gra_diff_line_equation_multipart()
def _gra_diff_12(): return _gra_scatter_line_of_best_fit()
def _gra_diff_13(): return _gra_diff_scatter_multipart()
def _gra_diff_14(): return _gra_distance_time_speed()
def _gra_diff_15(): return _gra_diff_journey_multipart()
def _gra_diff_16(): return _gra_diff_quadratic_features_multipart()
def _gra_diff_17(): return _gra_diff_quadratic_intersection_multipart()


# --- MCQ ---
_GRAPHS_MCQ_GENERATORS = [
    _gra_coordinate_quadrant,
    _gra_substitute_linear,
    _gra_y_intercept,
    _gra_equation_from_gradient_intercept,
    _gra_parallel_gradient,
    _gra_distance_time_speed,
    _gra_scatter_positive,
    _gra_scatter_negative,
    _gra_scatter_no_correlation,
    _gra_midpoint,
    _gra_reciprocal_value,
    _gra_cubic_substitute,
]


def graphs_mcq(slot_index=None):
    if slot_index is None:
        func = random.choice(_GRAPHS_MCQ_GENERATORS)
    else:
        func = _GRAPHS_MCQ_GENERATORS[slot_index % len(_GRAPHS_MCQ_GENERATORS)]
    q, s, hint, marks = func()[:4]

    correct = ""
    if '<strong>' in s:
        parts = s.split('<strong>', 1)
        if len(parts) > 1:
            rest = parts[1].split('</strong>', 1)
            if rest:
                correct = rest[0].strip()

    # Build distractors based on question type
    if 'quadrant' in q:
        distractors = ['I', 'II', 'III', 'IV']
    elif 'gradient' in q and 'parallel' in q:
        distractors = [correct, '0', '1', '-1']
    elif 'gradient' in q:
        distractors = ['1', '2', '3', '4']
    elif 'y‑intercept' in q or 'y-intercept' in q:
        distractors = ['0', '1', '-1', '2']
    elif 'equation' in q:
        # Build equation‑style distractors
        m, c = 2, 3  # fallback
        # try to extract m and c from the question
        distractors = [correct, f"y = x + 1", f"y = x - 1", f"y = 2x"]
    elif 'speed' in q:
        distractors = ['10', '20', '30', '40']
    elif 'scatter' in q or 'correlation' in q:
        distractors = ['positive', 'negative', 'none', 'quadrant I']
    elif 'midpoint' in q:
        # Build plausible coordinate distractors
        distractors = [correct, '(0,0)', '(1,1)', '(2,2)']
    elif 'reciprocal' in q or '/x' in q:
        distractors = ['1', '2', '3', '4']
    elif 'cubic' in q:
        distractors = ['0', '1', '-1', '2']
    else:
        distractors = ['0', '1', '2', '3']

    clean_distractors = [d for d in distractors if d != correct]
    options, letter = _mcq_options(correct, clean_distractors)
    return q, f"Answer: {letter}\n\n{hint}", hint, 1, options, letter


def _gr_problem_from_output(out, difficulty):
    choice = problem_from_choice_output(out, difficulty, 'gcse', 'maths', 'graphs')
    if choice:
        return choice
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if values and len(values) == len(labels):
                    extra = {
                        'correct_answer_raw': '|'.join(str(value) for value in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_format_hint': 'Enter a number or fraction in every field',
                    }
                    field_types = raw.get('field_types')
                    if field_types:
                        extra['answer_field_types'] = list(field_types)
            elif raw_type == 'linear_equation':
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'graphs',
                    correct_answer_raw=_gr_linear_eq_raw(raw['m'], raw['c']),
                    answer_type='linear_equation',
                    answer_format_hint='Enter as y = mx + c (e.g. y = 2x + 3)',
                )
            elif raw_type == 'number_estimate':
                tol = int(raw['tolerance'])
                dp = raw.get('dp', 0)
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'graphs',
                    correct_answer_raw=_gr_estimate_raw(raw['value'], tol, dp=dp),
                    answer_type='number_estimate',
                    answer_format_hint='Enter your estimate from the graph (close answers are accepted)',
                )
            elif raw_type == 'number_pair':
                val_a, val_b = raw['values']
                raw_s = f"{_number_raw(val_a)}|{_number_raw(val_b)}"
                return make_problem(
                    q, s, hint, difficulty, marks, 'gcse', 'maths', 'graphs',
                    correct_answer_raw=raw_s,
                    answer_type='number_pair',
                    answer_labels=[raw['label_a'], raw['label_b']],
                    answer_pair_sep=raw.get('sep', 'and'),
                )
        elif isinstance(raw, (str, int, float)):
            format_hint = 'Enter a number or fraction'
            extra = {
                'correct_answer_raw': str(raw) if isinstance(raw, str) else _number_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': format_hint,
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'graphs', **extra
    )


def gcse_graphs_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_fn(
            graphs_mcq, 'graphs', difficulty, slot_param='slot_index'
        )
    found = [_gra_found_01, _gra_found_02, _gra_found_03, _gra_found_04,
             _gra_found_05, _gra_found_06, _gra_found_07, _gra_found_08,
             _gra_found_09, _gra_found_10, _gra_found_11, _gra_found_12,
             _gra_found_13, _gra_found_14, _gra_found_15]
    inter = [_gra_inter_01, _gra_inter_02, _gra_inter_03, _gra_inter_04,
             _gra_inter_05, _gra_inter_06, _gra_inter_07, _gra_inter_08,
             _gra_inter_09, _gra_inter_10, _gra_inter_11, _gra_inter_12,
             _gra_inter_13, _gra_inter_14, _gra_inter_15]
    diff = [_gra_diff_01, _gra_diff_02, _gra_diff_03, _gra_diff_04,
            _gra_diff_05, _gra_diff_06, _gra_diff_07, _gra_diff_08,
            _gra_diff_09, _gra_diff_10, _gra_diff_11, _gra_diff_12,
            _gra_diff_13, _gra_diff_14, _gra_diff_15, _gra_diff_16,
            _gra_diff_17]
    if difficulty == 'foundational':
        pool = found
    elif difficulty == 'intermediate':
        pool = inter
    elif difficulty == 'difficult':
        pool = diff
    else:
        pool = random.sample(found, 4) + random.sample(inter, 4) + random.sample(diff, 2)
    return select_tier_variants(pool)


def gcse_graphs(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_graphs_variants(difficulty, 'mcq')
        q, s, hint, marks, opts, correct = run_mcq_variant(variants, variant_name)
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'graphs',
                            options=opts, correct_answer=correct)
    variants = gcse_graphs_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _gr_problem_from_output(variant(), difficulty)