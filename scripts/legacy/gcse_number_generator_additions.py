# ------------------------------------------------------------
# GCSE Maths – Number (15 / 15 / 15 + 15 MCQs)
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
    choices = [str(correct)] + [str(d) for d in distractors if str(d) != str(correct)]
    while len(choices) < 4:
        choices.append(str(correct) + str(len(choices)))
    choices = choices[:4]
    random.shuffle(choices)
    letters = ['A', 'B', 'C', 'D']
    options = [f"{letters[i]}  {choices[i]}" for i in range(4)]
    correct_letter = letters[choices.index(str(correct))]
    return options, correct_letter


# ---------- FOUNDATIONAL (15) ----------

def _number_found_place_value_digit():
    thousands = random.randint(2, 9)
    hundreds = random.randint(1, 9)
    tens = random.randint(1, 9)
    ones = random.randint(1, 9)
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
    return q, s, hint, 1


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
    return q, s, hint, 1


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
    return q, s, hint, 1


def _number_found_order_decimals():
    nums = sorted({round(random.randint(12, 98) / 100, 2) for _ in range(6)})[:4]
    while len(nums) < 4:
        nums = sorted({round(random.randint(12, 98) / 100, 2) for _ in range(6)})[:4]
    mixed = nums[:]
    random.shuffle(mixed)
    q = rf"Put these decimals in ascending order: {', '.join(str(x) for x in mixed)}"
    s = rf"Ascending means smallest to largest. The correct order is <strong>{', '.join(str(x) for x in nums)}</strong>."
    hint = "Ascending order means start with the smallest number."
    return q, s, hint, 2


def _number_found_round_nearest_10_100():
    n = random.randint(120, 9876)
    unit = random.choice([10, 100])
    ans = round(n / unit) * unit
    q = rf"Round {n} to the nearest {unit}."
    s = rf"To round to the nearest {unit}, look at the next place value column. <strong>{n} rounds to {ans}</strong>."
    hint = "Look one place value column to the right of the column you are rounding to."
    return q, s, hint, 1


def _number_found_round_decimal_places():
    n = round(random.uniform(2, 40), 3)
    dp = random.choice([1, 2])
    ans = round(n, dp)
    q = rf"Round {n} to {dp} decimal place{'s' if dp != 1 else ''}."
    s = rf"Keep {dp} digit{'s' if dp != 1 else ''} after the decimal point and check the next digit. The answer is <strong>{ans}</strong>."
    hint = "If the next digit is 5 or more, round up."
    return q, s, hint, 1


def _number_found_significant_figures_simple():
    n = random.randint(1200, 98700)
    sf = random.choice([1, 2, 3])
    ans = _number_sf_value(n, sf)
    q = rf"Round {n} to {sf} significant figure{'s' if sf != 1 else ''}."
    s = rf"Start counting significant figures from the first non-zero digit. Rounded to {sf} significant figure{'s' if sf != 1 else ''}, the answer is <strong>{ans}</strong>."
    hint = "The first significant figure is the first non-zero digit."
    return q, s, hint, 1


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
    return q, s, hint, 1


def _number_found_multiply_by_power_10():
    n = round(random.uniform(1.2, 98.7), 2)
    p = random.choice([10, 100, 1000])
    op = random.choice(['multiply', 'divide'])
    ans = n * p if op == 'multiply' else n / p
    symbol = '×' if op == 'multiply' else '÷'
    q = rf"Calculate {n} {symbol} {p}."
    s = rf"When you {op} by {p}, the digits move {len(str(p))-1} place{'s' if p != 10 else ''}. The answer is <strong>{_number_fmt(ans, 5)}</strong>."
    hint = "Multiplying by powers of 10 moves digits left; dividing moves them right."
    return q, s, hint, 1


def _number_found_square_cube():
    n = random.randint(2, 12)
    power = random.choice([2, 3])
    ans = n ** power
    q = rf"Calculate \({n}^{power}\)."
    s = rf"\({n}^{power}\) means multiply {n} by itself {power} times. Therefore \({n}^{power} = \)<strong>{ans}</strong>."
    hint = "A power means repeated multiplication."
    return q, s, hint, 1


def _number_found_percentage_of_amount():
    pct = random.choice([5, 10, 20, 25, 50, 75])
    amount = random.choice([40, 60, 80, 120, 160, 200])
    ans = amount * pct / 100
    q = rf"Find {pct}% of {amount}."
    s = rf"{pct}% means {pct} out of 100, so {pct}% of {amount} = {amount} × {pct}/100 = <strong>{_number_fmt(ans)}</strong>."
    hint = "Convert the percentage to a fraction over 100, then multiply."
    return q, s, hint, 1


def _number_found_fraction_of_amount():
    denom = random.choice([3, 4, 5, 8, 10])
    num = random.randint(1, denom - 1)
    amount = denom * random.randint(6, 20)
    ans = amount // denom * num
    q = rf"Find \(\frac{{{num}}}{{{denom}}}\) of {amount}."
    s = rf"First divide by {denom}: {amount} ÷ {denom} = {amount // denom}. Then multiply by {num}: {amount // denom} × {num} = <strong>{ans}</strong>."
    hint = "Divide by the denominator, then multiply by the numerator."
    return q, s, hint, 2


def _number_found_estimate_simple():
    a = random.choice([19.8, 29.7, 41.2, 58.9])
    b = random.choice([4.9, 5.1, 9.8])
    rounded_a = round(a / 10) * 10
    rounded_b = round(b)
    ans = rounded_a * rounded_b
    q = rf"Estimate {a} × {b} by rounding each number to 1 significant figure."
    s = rf"{a} ≈ {rounded_a} and {b} ≈ {rounded_b}. So {a} × {b} ≈ {rounded_a} × {rounded_b} = <strong>{ans}</strong>."
    hint = "Round to easy numbers first, then multiply mentally."
    return q, s, hint, 2


def _number_found_standard_form_large():
    a = random.randint(11, 99)
    zeros = random.choice([3, 4, 5])
    n = a * (10 ** zeros)
    coefficient = a / 10
    power = zeros + 1
    q = rf"Write {n} in standard form."
    s = rf"Move the decimal point until the first number is between 1 and 10: {n} = <strong>{coefficient} × 10^{power}</strong>."
    hint = "Standard form is A × 10^n where 1 ≤ A < 10."
    return q, s, hint, 2


def _number_found_indices_multiply():
    base = random.randint(2, 9)
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    ans_power = a + b
    q = rf"Simplify \({base}^{a} \times {base}^{b}\)."
    s = rf"When multiplying powers with the same base, add the indices: \({base}^{a} \times {base}^{b} = {base}^{{{a}+{b}}} = \)<strong>\({base}^{ans_power}\)</strong>."
    hint = "Same base and multiplication means add the powers."
    return q, s, hint, 1


# ---------- INTERMEDIATE (15) ----------

def _number_inter_standard_form_small():
    coeff = round(random.uniform(1.2, 9.8), 1)
    power = random.choice([3, 4, 5])
    ordinary = coeff / (10 ** power)
    q = rf"Write {_number_fmt(ordinary, 7)} in standard form."
    s = rf"Move the decimal point {power} places right to make a number between 1 and 10. Therefore {_number_fmt(ordinary, 7)} = <strong>{coeff} × 10^{{-{power}}}</strong>."
    hint = "Very small numbers have negative powers in standard form."
    return q, s, hint, 2


def _number_inter_standard_form_to_ordinary():
    coeff = round(random.uniform(1.2, 9.8), 1)
    power = random.choice([-4, -3, -2, 3, 4, 5])
    ans = coeff * (10 ** power)
    q = rf"Write \({coeff} \times 10^{{{power}}}\) as an ordinary number."
    s = rf"Multiplying by \(10^{{{power}}}\) moves the decimal point {'right' if power > 0 else 'left'} {abs(power)} places. The answer is <strong>{_number_fmt(ans, 8)}</strong>."
    hint = "Positive powers make large numbers; negative powers make small decimals."
    return q, s, hint, 2


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
    return q, s, hint, 2


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
    return q, s, hint, 2


def _number_inter_percentage_increase():
    amount = random.choice([80, 120, 150, 240, 360, 500])
    pct = random.choice([8, 12, 15, 18, 25, 35])
    ans = amount * (1 + pct / 100)
    q = rf"Increase {amount} by {pct}%."
    s = rf"The multiplier for an increase of {pct}% is {1 + pct/100}. So {amount} × {1 + pct/100} = <strong>{_number_fmt(ans)}</strong>."
    hint = "Use the multiplier 1 + percentage/100."
    return q, s, hint, 2


def _number_inter_percentage_decrease():
    amount = random.choice([80, 120, 150, 240, 360, 500])
    pct = random.choice([8, 12, 15, 18, 25, 35])
    ans = amount * (1 - pct / 100)
    q = rf"Decrease {amount} by {pct}%."
    s = rf"The multiplier for a decrease of {pct}% is {1 - pct/100}. So {amount} × {1 - pct/100} = <strong>{_number_fmt(ans)}</strong>."
    hint = "Use the multiplier 1 - percentage/100."
    return q, s, hint, 2


def _number_inter_reverse_percentage_increase():
    original = random.choice([40, 60, 75, 120, 160, 240])
    pct = random.choice([10, 20, 25, 30])
    final = original * (1 + pct / 100)
    q = rf"A price after a {pct}% increase is £{_number_fmt(final)}. Find the original price."
    s = rf"After a {pct}% increase, the multiplier is {1 + pct/100}. Original = {_number_fmt(final)} ÷ {1 + pct/100} = <strong>£{_number_fmt(original)}</strong>."
    hint = "For reverse percentages, divide by the multiplier."
    return q, s, hint, 3


def _number_inter_reverse_percentage_decrease():
    original = random.choice([50, 80, 100, 140, 200, 320])
    pct = random.choice([10, 20, 25, 40])
    final = original * (1 - pct / 100)
    q = rf"A price after a {pct}% decrease is £{_number_fmt(final)}. Find the original price."
    s = rf"After a {pct}% decrease, the multiplier is {1 - pct/100}. Original = {_number_fmt(final)} ÷ {1 - pct/100} = <strong>£{_number_fmt(original)}</strong>."
    hint = "The final amount is less than 100% of the original. Divide by the decimal multiplier."
    return q, s, hint, 3


def _number_inter_repeated_percentage_change():
    amount = random.choice([100, 200, 500, 800])
    pct1 = random.choice([10, 15, 20])
    pct2 = random.choice([5, 10, 25])
    ans = amount * (1 + pct1/100) * (1 - pct2/100)
    q = rf"An amount of £{amount} is increased by {pct1}% and then decreased by {pct2}%. Find the final amount."
    s = rf"Use successive multipliers: {amount} × {1+pct1/100} × {1-pct2/100} = <strong>£{_number_fmt(ans)}</strong>."
    hint = "Apply the first multiplier, then apply the second multiplier to the new amount."
    return q, s, hint, 3


def _number_inter_error_interval_whole():
    n = random.randint(12, 180)
    lower = n - 0.5
    upper = n + 0.5
    q = rf"A length is given as {n} cm to the nearest centimetre. Write the error interval for the actual length x."
    s = rf"The actual value is within 0.5 cm of {n}. Therefore <strong>{lower} ≤ x &lt; {upper}</strong>."
    hint = "For nearest whole number, subtract and add 0.5."
    return q, s, hint, 2


def _number_inter_error_interval_tenth():
    n = round(random.uniform(2, 30), 1)
    lower = round(n - 0.05, 2)
    upper = round(n + 0.05, 2)
    q = rf"A mass is given as {n} kg to the nearest 0.1 kg. Write the error interval for the actual mass m."
    s = rf"Half of 0.1 is 0.05, so <strong>{lower} ≤ m &lt; {upper}</strong>."
    hint = "The bounds are half the rounding unit below and above the rounded value."
    return q, s, hint, 2


def _number_inter_bounds_area():
    length = random.randint(8, 20)
    width = random.randint(4, 12)
    max_area = (length + 0.5) * (width + 0.5)
    min_area = (length - 0.5) * (width - 0.5)
    q = rf"A rectangle has length {length} cm and width {width} cm, each measured to the nearest centimetre. Find the minimum and maximum possible area."
    s = rf"Lower bounds: {length-0.5} and {width-0.5}, so minimum area = {length-0.5} × {width-0.5} = <strong>{_number_fmt(min_area)} cm²</strong>.<br>Upper bounds: {length+0.5} and {width+0.5}, so maximum area = {length+0.5} × {width+0.5} = <strong>{_number_fmt(max_area)} cm²</strong>."
    hint = "Use lower bounds for the minimum area and upper bounds for the maximum area."
    return q, s, hint, 4


def _number_inter_index_division():
    base = random.randint(2, 9)
    a = random.randint(6, 10)
    b = random.randint(1, 5)
    ans = a - b
    q = rf"Simplify \({base}^{a} \div {base}^{b}\)."
    s = rf"When dividing powers with the same base, subtract the indices: \({base}^{a} \div {base}^{b} = {base}^{{{a}-{b}}} = \)<strong>\({base}^{ans}\)</strong>."
    hint = "Same base and division means subtract the powers."
    return q, s, hint, 1


def _number_inter_index_power_of_power():
    base = random.randint(2, 6)
    a = random.randint(2, 5)
    b = random.randint(2, 4)
    ans = a * b
    q = rf"Simplify \(({base}^{a})^{b}\)."
    s = rf"For a power of a power, multiply the indices: \(({base}^{a})^{b} = {base}^{{{a}×{b}}} = \)<strong>\({base}^{ans}\)</strong>."
    hint = "A power raised to another power means multiply the powers."
    return q, s, hint, 1


def _number_inter_prime_factor_product():
    cases = [
        (72, "2³ × 3²"), (84, "2² × 3 × 7"), (90, "2 × 3² × 5"),
        (126, "2 × 3² × 7"), (180, "2² × 3² × 5"), (252, "2² × 3² × 7"),
    ]
    n, ans = random.choice(cases)
    q = rf"Write {n} as a product of prime factors."
    s = rf"Use a factor tree and split until every factor is prime. The product of prime factors is <strong>{ans}</strong>."
    hint = "Keep dividing by prime numbers such as 2, 3, 5 and 7."
    return q, s, hint, 3


def _number_inter_calculator_estimate_fraction():
    a = random.choice([19.8, 31.2, 48.6, 59.5])
    b = random.choice([4.9, 5.2, 9.7])
    c = random.choice([0.48, 0.51, 1.9, 2.1])
    ar = round(a / 10) * 10
    br = round(b)
    cr = 0.5 if c < 1 else round(c)
    ans = ar * br / cr
    q = rf"Estimate \(\frac{{{a} \times {b}}}{{{c}}}\) by rounding each number to 1 significant figure."
    s = rf"{a} ≈ {ar}, {b} ≈ {br}, and {c} ≈ {cr}. So the estimate is \(({ar} × {br}) ÷ {cr} = \)<strong>{_number_fmt(ans)}</strong>."
    hint = "Round each value to one significant figure, then calculate."
    return q, s, hint, 3


# ---------- DIFFICULT (15) ----------

def _number_diff_compound_interest():
    principal = random.choice([500, 800, 1200, 2000])
    rate = random.choice([2, 3, 4, 5])
    years = random.choice([3, 4, 5])
    ans = principal * ((1 + rate/100) ** years)
    q = rf"£{principal} is invested at {rate}% compound interest per year for {years} years. Find the final amount to the nearest penny."
    s = rf"Use compound interest: {principal} × \((1 + {rate}/100)^{years}\) = {principal} × {1+rate/100}^{years} = <strong>£{ans:.2f}</strong>."
    hint = "Use the percentage multiplier repeatedly, or raise it to the power of the number of years."
    return q, s, hint, 3


def _number_diff_depreciation():
    value = random.choice([6000, 8000, 12000, 15000])
    rate = random.choice([12, 15, 18, 20])
    years = random.choice([2, 3, 4])
    ans = value * ((1 - rate/100) ** years)
    q = rf"A car worth £{value} depreciates by {rate}% each year for {years} years. Find its value after {years} years to the nearest pound."
    s = rf"Depreciation uses the multiplier {1-rate/100}. So value = {value} × {1-rate/100}^{years} = <strong>£{round(ans)}</strong>."
    hint = "A percentage decrease uses a multiplier below 1. Apply it once for each year."
    return q, s, hint, 3


def _number_diff_reverse_compound():
    original = random.choice([400, 600, 1000, 1500])
    rate = random.choice([5, 10, 12])
    years = random.choice([2, 3])
    final = original * ((1 + rate/100) ** years)
    q = rf"After {years} years of compound growth at {rate}% per year, an investment is worth £{final:.2f}. Find the original investment to the nearest penny."
    s = rf"Reverse the compound multiplier: original = {final:.2f} ÷ \({1+rate/100}^{years}\) = <strong>£{original:.2f}</strong>."
    hint = "Divide by the compound multiplier instead of multiplying."
    return q, s, hint, 4


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
    return q, s, hint, 3


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
    return q, s, hint, 4


def _number_diff_error_interval_product():
    a = random.randint(20, 80)
    b = random.randint(5, 30)
    min_prod = (a - 0.5) * (b - 0.5)
    max_prod = (a + 0.5) * (b + 0.5)
    q = rf"Two measurements are {a} cm and {b} cm, each rounded to the nearest centimetre. Find the minimum and maximum possible product of the measurements."
    s = rf"Use lower bounds for the minimum and upper bounds for the maximum. Minimum = {a-0.5} × {b-0.5} = <strong>{_number_fmt(min_prod)} cm²</strong>. Maximum = {a+0.5} × {b+0.5} = <strong>{_number_fmt(max_prod)} cm²</strong>."
    hint = "For a product of positive measurements, minimum uses both lower bounds and maximum uses both upper bounds."
    return q, s, hint, 4


def _number_diff_bounds_density():
    mass = random.randint(40, 120)
    volume = random.randint(8, 30)
    max_density = (mass + 0.5) / (volume - 0.5)
    min_density = (mass - 0.5) / (volume + 0.5)
    q = rf"Mass is {mass} g and volume is {volume} cm³, both to the nearest whole unit. Find the lower and upper bounds for density in g/cm³."
    s = rf"Density = mass ÷ volume. Minimum density uses lowest mass and highest volume: ({mass-0.5}) ÷ ({volume+0.5}) = <strong>{min_density:.3f}</strong>. Maximum density uses highest mass and lowest volume: ({mass+0.5}) ÷ ({volume-0.5}) = <strong>{max_density:.3f}</strong>."
    hint = "For a fraction, the maximum uses a large numerator and small denominator."
    return q, s, hint, 4


def _number_diff_fractional_indices():
    base = random.choice([4, 9, 16, 25, 36, 49, 64, 81])
    root = int(math.sqrt(base))
    q = rf"Evaluate \({base}^{{1/2}}\)."
    s = rf"A power of \(1/2\) means square root. Therefore \({base}^{{1/2}} = \sqrt{{{base}}} = \)<strong>{root}</strong>."
    hint = "The index 1/2 means square root."
    return q, s, hint, 1


def _number_diff_negative_indices():
    base = random.randint(2, 9)
    power = random.choice([1, 2, 3])
    denom = base ** power
    q = rf"Evaluate \({base}^{{-{power}}}\)."
    s = rf"A negative index means reciprocal: \({base}^{{-{power}}} = \frac{{1}}{{{base}^{power}}} = \)<strong>\(\frac{{1}}{{{denom}}}\)</strong>."
    hint = "Move the power to the denominator to make the index positive."
    return q, s, hint, 2


def _number_diff_zero_negative_combined():
    a = random.randint(2, 9)
    b = random.randint(2, 6)
    ans_num = 1
    ans_den = b * b
    q = rf"Simplify \({a}^0 \times {b}^{{-2}}\)."
    s = rf"\({a}^0 = 1\), and \({b}^{{-2}} = \frac{{1}}{{{b}^2}} = \frac{{1}}{{{ans_den}}}\). So the answer is <strong>\(\frac{{1}}{{{ans_den}}}\)</strong>."
    hint = "Any non-zero number to the power 0 is 1; a negative index creates a reciprocal."
    return q, s, hint, 2


def _number_diff_recurring_decimal_fraction():
    cases = [('0.333...', '1/3'), ('0.666...', '2/3'), ('0.111...', '1/9'), ('0.272727...', '3/11'), ('0.454545...', '5/11')]
    dec, frac = random.choice(cases)
    q = rf"Write {dec} as a fraction in its simplest form."
    s = rf"This is a recurring decimal. Using the standard recurring-decimal method gives <strong>{frac}</strong>."
    hint = "Let x equal the recurring decimal, multiply to line up the repeating part, then subtract."
    return q, s, hint, 3


def _number_diff_surds_estimate():
    n = random.choice([20, 30, 50, 75, 120, 200])
    lower = int(math.sqrt(n))
    upper = lower + 1
    q = rf"Without using a calculator, show which two consecutive integers \(\sqrt{{{n}}}\) lies between."
    s = rf"Since {lower}² = {lower**2} and {upper}² = {upper**2}, and {lower**2} &lt; {n} &lt; {upper**2}, we have <strong>{lower} &lt; \sqrt{{{n}}} &lt; {upper}</strong>."
    hint = "Compare the number with nearby square numbers."
    return q, s, hint, 2


def _number_diff_hcf_lcm_prime_factors():
    cases = [
        (72, 120, 24, 360), (84, 126, 42, 252), (90, 150, 30, 450),
        (108, 180, 36, 540), (96, 144, 48, 288),
    ]
    a, b, hcf, lcm = random.choice(cases)
    q = rf"Find the HCF and LCM of {a} and {b}."
    s = rf"Using prime factors or systematic listing, the highest common factor is <strong>{hcf}</strong> and the lowest common multiple is <strong>{lcm}</strong>. Check: HCF × LCM = {hcf*lcm}, and {a} × {b} = {a*b}."
    hint = "Prime factor form is the most reliable method for larger numbers."
    return q, s, hint, 4


def _number_diff_percentage_error():
    estimate = random.choice([48, 96, 125, 240, 360])
    actual = estimate + random.choice([-12, -8, -5, 6, 10, 15])
    error = abs(estimate - actual)
    pct_error = error / actual * 100
    q = rf"An estimate is {estimate}, but the actual value is {actual}. Find the percentage error to 1 decimal place."
    s = rf"Percentage error = \(\frac{{\text{{error}}}}{{\text{{actual}}}} \times 100\). Error = |{estimate} − {actual}| = {error}. So percentage error = {error} ÷ {actual} × 100 = <strong>{pct_error:.1f}%</strong>."
    hint = "Use absolute error divided by actual value, then multiply by 100."
    return q, s, hint, 3


def _number_diff_best_value():
    items1 = random.randint(3, 8)
    price1 = round(random.uniform(1.5, 6.0), 2)
    items2 = random.randint(4, 10)
    price2 = round(random.uniform(2.0, 8.0), 2)
    unit1 = price1 / items1
    unit2 = price2 / items2
    best = 'Pack A' if unit1 < unit2 else 'Pack B'
    q = rf"Pack A contains {items1} items for £{price1:.2f}. Pack B contains {items2} items for £{price2:.2f}. Which pack is better value?"
    s = rf"Compare unit prices. Pack A: £{price1:.2f} ÷ {items1} = £{unit1:.2f} per item. Pack B: £{price2:.2f} ÷ {items2} = £{unit2:.2f} per item. The better value is <strong>{best}</strong>."
    hint = "Find the cost per one item for each pack."
    return q, s, hint, 3


def _number_diff_iterative_bounds():
    n = random.choice([18, 30, 45, 70, 95])
    lower = math.floor(math.sqrt(n) * 10) / 10
    upper = lower + 0.1
    q = rf"Find the two consecutive tenths that \(\sqrt{{{n}}}\) lies between."
    s = rf"Check tenths around \(\sqrt{{{n}}}\): {lower}² = {lower**2:.2f} and {upper:.1f}² = {upper**2:.2f}. Since {lower**2:.2f} &lt; {n} &lt; {upper**2:.2f}, <strong>{lower:.1f} &lt; \sqrt{{{n}}} &lt; {upper:.1f}</strong>."
    hint = "Square nearby decimal values until the original number is between them."
    return q, s, hint, 3


# ---------- MCQ (15) ----------

def number_mcq():
    mcq_type = random.randint(1, 15)

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
        options, correct_letter = _number_mcq_options(correct, [base/2, base*2, base**2])
        hint = "A power of 1/2 means square root."

    elif mcq_type == 14:
        base = random.randint(2, 8)
        power = random.choice([1, 2, 3])
        correct = rf"1/{base**power}"
        q = rf"Evaluate \({base}^{{-{power}}}\)."
        options, correct_letter = _number_mcq_options(correct, [base**power, -base**power, rf"1/{base*power}"])
        hint = "A negative index means reciprocal."

    else:
        estimate = random.choice([48, 96, 125, 240])
        actual = estimate + random.choice([6, 8, 12])
        error = abs(estimate - actual)
        correct = f"{(error/actual*100):.1f}%"
        q = rf"An estimate is {estimate} and the actual value is {actual}. What is the percentage error to 1 decimal place?"
        options, correct_letter = _number_mcq_options(correct, [f"{(error/estimate*100):.1f}%", f"{error}%", f"{(actual/estimate*100):.1f}%"])
        hint = "Percentage error = absolute error ÷ actual value × 100."

    s = f"Answer: {correct_letter}\n\n{hint}"
    return q, s, hint, 1, options, correct_letter


# ---------- VARIANTS FUNCTION ----------

def gcse_number_variants(difficulty, mode):
    if mode == 'mcq':
        return [number_mcq] * 10

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
            _number_inter_calculator_estimate_fraction,
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
            _number_diff_iterative_bounds,
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
            _number_inter_calculator_estimate_fraction,
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
            _number_diff_iterative_bounds,
        ], 2)
        return found + inter + diff

    shuffled = random.sample(pool, len(pool))
    return (shuffled * (10 // len(shuffled) + 1))[:10]


# ---------- MAIN GENERATOR ----------

def gcse_number(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = number_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'number',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_number_variants(difficulty, mode)
    if variant_name is None:
        variant = random.choice(variants)
    else:
        variant_map = {v.__name__: v for v in variants}
        if variant_name not in variant_map:
            variant = random.choice(variants)
        else:
            variant = variant_map[variant_name]

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'number')
