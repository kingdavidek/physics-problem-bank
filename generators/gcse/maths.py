import random
import math
import sympy as sp

from generators.shared.utils import make_problem


def gcsedecordering():
    base = random.randint(1, 9) / 10
    decimals = sorted(set(
        round(base + random.randint(0, 9) / 100 + random.randint(0, 9) / 1000, 3)
        for _ in range(5)
    ))
    random.shuffle(decimals)
    ordered = sorted(decimals)
    q = f"Write these decimals in order from smallest to largest:<br><br><strong>{', '.join(str(d) for d in decimals)}</strong>"
    s = f"Write each number to 3 decimal places to compare easily, then sort.<br><strong>{', '.join(str(d) for d in ordered)}</strong>"
    hint = "Write all numbers to the same number of decimal places, adding zeros if needed, then compare digit by digit."
    return q, s, hint, 1

def gcse_maths_decimals(difficulty, mode):
    if difficulty == "foundational":
        variant = random.choice([gcsedecordering])
    else:
        variant = random.choice([gcsedecordering])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, "gcse", "maths", "decimals")


def gcse_maths_bidmas(difficulty, mode):
    if mode == "exam":
        if difficulty == "foundational":
            variant = random.choice([
                gcsebidmassimple,
                gcsebidmasbrackets,
                gcsebidmaspower,
                gcsenegaddsubtract,
                gcsenegmultiplydivide,
            ])
        elif difficulty == "intermediate":
            variant = random.choice([
                gcsebidmasmixed,
                gcsenegpowers,
                gcsebidmaswithnegatives,
            ])
        else:
            variant = random.choice([
                gcsebidmashard,
                gcsebidmaswithnegatives,
                gcsenegpowers,
            ])
    else:
        if difficulty == "foundational":
            variant = random.choice([
                gcsebidmassimple,
                gcsebidmasbrackets,
                gcsebidmaspower,
                gcsenegaddsubtract,
                gcsenegmultiplydivide,
            ])
        elif difficulty == "intermediate":
            variant = random.choice([
                gcsebidmasmixed,
                gcsenegpowers,
                gcsebidmaswithnegatives,
            ])
        else:
            variant = random.choice([
                gcsebidmashard,
                gcsebidmaswithnegatives,
                gcsenegpowers,
            ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, "gcse", "maths", "bidmas")



def gcse_maths_fdp(difficulty, mode):
    if difficulty == "foundational":
        variant = random.choice([
            gcsefdpdecimaltopercentage,
            gcsefdppercentagetodecimal,
            gcsefdpdecimaltofraction,
            gcsefdpfractiontodecimal,
            gcsefdppercentagetofraction,
            gcsefdpfractiontopercentage,
        ])
    elif difficulty == "intermediate":
        variant = random.choice([
            gcsefdpfractiontodecimal,
            gcsefdppercentagetofraction,
            gcsefdpfractiontopercentage,
            gcsefdpmultistep,
            gcsefdpdecimaltofraction,
        ])
    else:
        variant = random.choice([
            gcsefdpmultistep,
            gcsefdprecurring,
            gcsefdppercentagetofraction,
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, "gcse", "maths", "fdp")



def gcse_maths_multiples_factors(difficulty, mode):
    if difficulty == "foundational":
        variant = random.choice([
            gcsemffindmultiple,
            gcsemffindfactor,
            gcsemfprime,
        ])
    elif difficulty == "intermediate":
        variant = random.choice([
            gcsemffactorpairs,
            gcsemfhcf,
            gcsemflcm,
            gcsemfprime,
        ])
    else:
        variant = random.choice([
            gcsemfprimefactors,
            gcsemfhcf,
            gcsemflcm,
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, "gcse", "maths", "multiples_factors")

def gcse_maths_surds(difficulty, mode):
    if mode == "exam":
        if difficulty == "foundational":
            variant = random.choice([
                gcsesurdssimplify,
                gcsesurdssimplifymultiple,
                gcsesurdsaddsubtract,
                gcsesurdsmultiply,
            ])
        elif difficulty == "intermediate":
            variant = random.choice([
                gcsesurdsexpandsimple,
                gcsesurdsexpanddouble,
                gcsesurdssquarebracket,
                gcsesurdssquarebracketminus,
                gcsesurdsrationalisesimple,
                gcsesurdsrationalisecompound,
            ])
        else:
            variant = random.choice([
                gcsesurdsshowthatrationalise,
                gcsesurdsidentity,
                gcsesurdsexactarea,
                gcsesurdsexpanddiffsubtract,
            ])
    else:
        if difficulty == "foundational":
            variant = random.choice([
                gcsesurdssimplify,
                gcsesurdssimplifymultiple,
                gcsesurdsaddsubtract,
                gcsesurdsmultiply,
            ])
        elif difficulty == "intermediate":
            variant = random.choice([
                gcsesurdsexpandsimple,
                gcsesurdsexpanddouble,
                gcsesurdssquarebracket,
                gcsesurdssquarebracketminus,
                gcsesurdsrationalisesimple,
                gcsesurdsrationalisecompound,
            ])
        else:
            variant = random.choice([
                gcsesurdsshowthatrationalise,
                gcsesurdsidentity,
                gcsesurdsexactarea,
                gcsesurdsexpanddiffsubtract,
            ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, "gcse", "maths", "surds")

def gcse_maths_algebra(difficulty, mode):
    x = sp.Symbol("x")

    if difficulty == "foundational":
        a = random.randint(2, 8)
        b = random.randint(1, 10)
        c = random.randint(b + 1, 30)
        ans = sp.Rational(c - b, a)
        q = rf"Solve \( {a}x + {b} = {c} \)"
        s = rf"Subtract {b} from both sides:<br>\( {a}x = {c-b} \)<br>Divide by {a}:<br>\( x = {sp.latex(ans)} \)"
        hint = r"Use inverse operations to isolate \(x\)."
        marks = 2

    elif difficulty == "intermediate":
        r1 = random.randint(-6, 6)
        r2 = random.randint(-6, 6)
        expr = sp.expand((x - r1) * (x - r2))
        q = rf"Solve \( {sp.latex(expr)} = 0 \)"
        s = rf"Factorise:<br>\( (x-{r1})(x-{r2}) = 0 \)<br>So \( x={r1} \) or \( x={r2} \)"
        hint = r"Find two numbers that multiply to give the constant term and add to give the coefficient of \(x\)."
        marks = 3

    else:
        ac = random.randint(1, 3)
        bc = random.randint(-8, 8)
        cc = random.randint(-10, -1)
        discriminant = bc**2 - 4 * ac * cc
        expr = ac * x**2 + bc * x + cc
        r1 = round((-bc + discriminant**0.5) / (2 * ac), 2)
        r2 = round((-bc - discriminant**0.5) / (2 * ac), 2)
        q = rf"Solve \( {sp.latex(expr)} = 0 \), giving your answers to 2 decimal places."
        s = rf"Using the quadratic formula:<br><br>\( x = \frac{{-{bc} \pm \sqrt{{{discriminant}}}}}{{{2*ac}}} \)<br><br>\( x={r1} \) or \( x={r2} \)"
        hint = r"Use the quadratic formula \(x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}\)."
        marks = 4

    return make_problem(q, s, hint, difficulty, marks, "gcse", "maths", "algebra")


# ─────────────────────────────────────────────────────────────
# GCSE MATHS — FRACTIONS, DECIMALS AND PERCENTAGES
# ─────────────────────────────────────────────────────────────

def gcse_fdp_decimal_to_percentage():
    x = random.choice([0.03, 0.07, 0.18, 0.29, 0.4, 0.75, 1.25])
    ans = x * 100
    q = rf"Write {x} as a percentage."
    s = rf"To convert a decimal to a percentage, multiply by 100.<br>{x} × 100 = <strong>{ans}%</strong>"
    hint = "Multiply the decimal by 100 and add the percentage sign."
    return q, s, hint, 1

def gcse_fdp_percentage_to_decimal():
    x = random.choice([4, 17, 18, 23, 65, 125])
    ans = x / 100
    q = rf"Write {x}% as a decimal."
    s = rf"To convert a percentage to a decimal, divide by 100.<br>{x} ÷ 100 = <strong>{ans}</strong>"
    hint = "Divide by 100, or move the decimal point two places left."
    return q, s, hint, 1

def gcse_fdp_decimal_to_fraction():
    cases = [
        (0.3, "3/10"),
        (0.25, "1/4"),
        (0.75, "3/4"),
        (0.12, "3/25"),
        (0.03, "3/100"),
        (0.4, "2/5"),
    ]
    dec, frac = random.choice(cases)
    q = rf"Write {dec} as a fraction in its simplest form."
    s = rf"Write {dec} using place value, then simplify.<br><strong>{frac}</strong>"
    hint = "Write the decimal over 10, 100 or 1000 depending on place value, then simplify."
    return q, s, hint, 1

def gcse_fdp_fraction_to_decimal():
    cases = [
        ("1/4", 1, 4, "0.25"),
        ("3/8", 3, 8, "0.375"),
        ("2/5", 2, 5, "0.4"),
        ("3/4", 3, 4, "0.75"),
        ("1/8", 1, 8, "0.125"),
    ]
    frac_str, a, b, ans = random.choice(cases)
    q = rf"Write {frac_str} as a decimal."
    s = rf"Convert a fraction to a decimal by dividing the numerator by the denominator.<br>{a} ÷ {b} = <strong>{ans}</strong>"
    hint = "Divide the top number by the bottom number."
    return q, s, hint, 1

def gcse_fdp_percentage_to_fraction():
    cases = [
        (23, "23/100"),
        (65, "13/20"),
        (17, "17/100"),
        (4, "1/25"),
        (50, "1/2"),
        (75, "3/4"),
    ]
    pct, ans = random.choice(cases)
    q = rf"Write {pct}% as a fraction in its simplest form."
    s = rf"Write the percentage over 100, then simplify.<br>{pct}% = {pct}/100 = <strong>{ans}</strong>"
    hint = "Percent means per hundred, so start with denominator 100."
    return q, s, hint, 1

def gcse_fdp_fraction_to_percentage():
    cases = [
        ("1/5", 20),
        ("1/4", 25),
        ("3/4", 75),
        ("3/8", 37.5),
        ("2/5", 40),
    ]
    frac, ans = random.choice(cases)
    q = rf"Write {frac} as a percentage."
    s = rf"Convert the fraction to a decimal, then multiply by 100.<br><strong>{frac} = {ans}%</strong>"
    hint = "Fraction to decimal first, then decimal to percentage."
    return q, s, hint, 1

def gcse_fdp_multi_step():
    cases = [
        ("3/8", "0.375", "37.5%"),
        ("1/5", "0.2", "20%"),
        ("3/4", "0.75", "75%"),
        ("1/8", "0.125", "12.5%"),
    ]
    frac, dec, pct = random.choice(cases)
    q = rf"Convert {frac} into a decimal and a percentage."
    s = rf"{frac} = <strong>{dec}</strong><br>{dec} × 100 = <strong>{pct}</strong>"
    hint = "First divide to get the decimal, then multiply by 100 for the percentage."
    return q, s, hint, 2

def gcse_fdp_recurring():
    cases = [
        ("0.333...", "1/3"),
        ("0.666...", "2/3"),
        ("0.181818...", "2/11"),
        ("0.363636...", "4/11"),
    ]
    dec, ans = random.choice(cases)
    q = rf"Write {dec} as a fraction."
    s = rf"This is a recurring decimal. Using the algebraic method gives <strong>{ans}</strong>."
    hint = "For recurring decimals, let x equal the decimal, multiply to line up the repeat, then subtract."
    return q, s, hint, 3

def gcse_maths_fdp(difficulty, mode):
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
            gcse_fdp_multi_step,
            gcse_fdp_decimal_to_fraction
        ])
    else:
        variant = random.choice([
            gcse_fdp_multi_step,
            gcse_fdp_recurring,
            gcse_fdp_percentage_to_fraction
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'fdp')


# ─────────────────────────────────────────────────────────────
# GCSE MATHS — MULTIPLES AND FACTORS
# ─────────────────────────────────────────────────────────────

def gcse_mf_find_multiple():
    n = random.choice([4, 5, 6, 7, 8, 9])
    k = random.choice([3, 4, 5, 6])
    ans = n * k
    q = rf"Write down the {k}th multiple of {n}."
    s = rf"The {k}th multiple of {n} is {n} × {k} = <strong>{ans}</strong>"
    hint = "Multiply the number by the position in the list."
    return q, s, hint, 1

def gcse_mf_find_factor():
    n = random.choice([18, 20, 24, 30, 36])
    factors = {
        18: [1,2,3,6,9,18],
        20: [1,2,4,5,10,20],
        24: [1,2,3,4,6,8,12,24],
        30: [1,2,3,5,6,10,15,30],
        36: [1,2,3,4,6,9,12,18,36],
    }
    ans = random.choice(factors[n])
    q = rf"Write down a factor of {n}."
    s = rf"One factor of {n} is <strong>{ans}</strong> because it divides exactly into {n}."
    hint = "A factor divides exactly with no remainder."
    return q, s, hint, 1

def gcse_mf_factor_pairs():
    n = random.choice([24, 30, 36, 40])
    pairs = {
        24: "1×24, 2×12, 3×8, 4×6",
        30: "1×30, 2×15, 3×10, 5×6",
        36: "1×36, 2×18, 3×12, 4×9, 6×6",
        40: "1×40, 2×20, 4×10, 5×8",
    }
    q = rf"Write down all the factor pairs of {n}."
    s = rf"The factor pairs of {n} are <strong>{pairs[n]}</strong>."
    hint = "Start with 1 and the number itself, then test 2, 3, 4 and so on."
    return q, s, hint, 2

def gcse_mf_prime():
    options = [(29, True), (33, False), (31, True), (35, False), (37, True)]
    n, is_prime = random.choice(options)
    q = rf"Is {n} a prime number? Give a reason."
    if is_prime:
        s = rf"Yes. <strong>{n}</strong> is prime because it has exactly two factors: 1 and {n}."
    else:
        div = 3 if n % 3 == 0 else 5
        s = rf"No. <strong>{n}</strong> is not prime because it is divisible by {div}."
    hint = "A prime number has exactly two factors: 1 and itself."
    return q, s, hint, 1

def gcse_mf_hcf():
    cases = [
        (12, 18, 6),
        (16, 24, 8),
        (20, 30, 10),
        (18, 27, 9),
    ]
    a, b, ans = random.choice(cases)
    q = rf"Find the highest common factor of {a} and {b}."
    s = rf"The highest common factor is the largest number that divides both exactly.<br><strong>HCF = {ans}</strong>"
    hint = "List the factors of both numbers, then choose the greatest common one."
    return q, s, hint, 2

def gcse_mf_lcm():
    cases = [
        (4, 6, 12),
        (6, 8, 24),
        (5, 12, 60),
        (3, 7, 21),
    ]
    a, b, ans = random.choice(cases)
    q = rf"Find the lowest common multiple of {a} and {b}."
    s = rf"The lowest common multiple is the smallest number in both times tables.<br><strong>LCM = {ans}</strong>"
    hint = "List multiples of both numbers until you find the first common one."
    return q, s, hint, 2

def gcse_mf_prime_factors():
    cases = [
        (24, "2³ × 3"),
        (36, "2² × 3²"),
        (40, "2³ × 5"),
        (50, "2 × 5²"),
        (200, "2³ × 5²"),
    ]
    n, ans = random.choice(cases)
    q = rf"Write {n} as a product of prime factors."
    s = rf"The product of prime factors of {n} is <strong>{ans}</strong>."
    hint = "Use a factor tree and keep splitting until all branches are prime."
    return q, s, hint, 3

def gcse_maths_multiples_factors(difficulty, mode):
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
            gcse_mf_prime
        ])
    else:
        variant = random.choice([
            gcse_mf_prime_factors,
            gcse_mf_hcf,
            gcse_mf_lcm
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'multiples_factors')




# ─────────────────────────────────────────────────────────────
#  GCSE MATHS — DECIMALS
# ─────────────────────────────────────────────────────────────

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
    s = (rf"Write each number to 3 decimal places to compare easily, then sort:<br>"
         rf"<strong>{', '.join(str(d) for d in ordered)}</strong>")
    hint = r"Write all numbers to the same number of decimal places, adding zeros if needed, then compare digit by digit."
    return q, s, hint, 1

def gcse_dec_add_subtract():
    """Foundational: add or subtract two decimals"""
    import random
    a = round(random.uniform(1.0, 50.0), 2)
    b = round(random.uniform(1.0, 20.0), 2)
    op = random.choice(['+', '−'])
    result = round(a + b, 2) if op == '+' else round(a - b, 2)
    q = rf"Calculate {a} {op} {b}"
    s = (rf"Line up the decimal points and {('add' if op == '+' else 'subtract')}:<br>"
         rf"{a} {op} {b} = <strong>{result}</strong>")
    hint = r"Write the numbers one above the other, aligning the decimal points. Add zeros to fill any gaps."
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
    s = (rf"When you {'multiply' if op == '×' else 'divide'} by {power}, move the decimal point "
         rf"{places} place{'s' if places > 1 else ''} to the {direction}:<br>"
         rf"<strong>{result_str}</strong>")
    hint = rf"× {power} → move decimal point {{{10:1, 100:2, 1000:3}[power]}} place(s) right. ÷ {power} → move left."
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
    s = (rf"Ignore decimal points: {a_int} × {b_int} = {int_product}<br>"
         rf"{a} has 1 d.p. and {b} has 1 d.p. — total of 2 decimal places.<br>"
         rf"Put the point back: <strong>{result}</strong>")
    hint = r"Multiply as integers first, then count the total decimal places in both numbers and insert the point."
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
    s = (rf"Multiply both numbers by {mult} to remove the decimal from the divisor:<br>"
         rf"{a_int} ÷ {b_int} = <strong>{result}</strong>")
    hint = rf"Multiply both the dividend and divisor by {mult} so that {b} becomes a whole number."
    return q, s, hint, 2

def gcse_dec_round():
    """Foundational: round a decimal to a specified number of decimal places"""
    import random
    n = round(random.uniform(0.001, 999.999), 4)
    dp = random.choice([1, 2, 3])
    result = round(n, dp)
    # find the deciding digit
    n_str = f"{n:.4f}"
    q = rf"Round {n} to {dp} decimal place{'s' if dp > 1 else ''}."
    s = (rf"Look at the digit in the {['', '1st', '2nd', '3rd', '4th'][dp+1]} decimal place: "
         rf"if it is 5 or more, round up; otherwise round down.<br>"
         rf"<strong>{result}</strong>")
    hint = rf"Find the digit one place after your target. 5 or above → round up the last kept digit."
    return q, s, hint, 1

def gcse_dec_fraction_to_decimal():
    """Intermediate: convert a fraction to a decimal by long division"""
    import random
    pairs = [(1,8,0.125), (3,8,0.375), (5,8,0.625), (7,8,0.875),
             (1,6,0.1667), (5,6,0.8333), (2,3,0.6667), (1,3,0.3333),
             (3,4,0.75), (7,20,0.35), (9,25,0.36)]
    num, den, dec = random.choice(pairs)
    dec_str = f"{dec:.4f}".rstrip('0').rstrip('.')
    if '6' in dec_str or '3' in dec_str:
        dec_str += "…"
    q = rf"Convert {num}/{den} to a decimal."
    s = rf"Divide {num} by {den}: {num} ÷ {den} = <strong>{dec_str}</strong>"
    hint = r"Divide the numerator by the denominator using short or long division."
    return q, s, hint, 1



def gcse_maths_decimals(difficulty, mode):
    if mode == 'exam':
        if difficulty == 'foundational':
            variant = random.choice([gcse_dec_ordering, gcse_dec_add_subtract,
                                     gcse_dec_multiply_power10, gcse_dec_round,
                                     gcse_dec_fraction_to_decimal])
        elif difficulty == 'intermediate':
            variant = random.choice([gcse_dec_multiply, gcse_dec_divide,
                                     gcse_dec_fraction_to_decimal, gcse_dec_round])
        else:
            variant = random.choice([gcse_dec_divide, gcse_dec_multiply, gcse_dec_round])
    else:  # revision
        if difficulty == 'foundational':
            variant = random.choice([gcse_dec_ordering, gcse_dec_add_subtract,
                                     gcse_dec_multiply_power10, gcse_dec_round,
                                     gcse_dec_fraction_to_decimal])
        elif difficulty == 'intermediate':
            variant = random.choice([gcse_dec_multiply, gcse_dec_divide,
                                     gcse_dec_fraction_to_decimal, gcse_dec_round])
        else:
            variant = random.choice([gcse_dec_recurring, gcse_dec_divide, gcse_dec_multiply])

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
    return q, s, hint, 1

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
    return q, s, hint, 1

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
    return q, s, hint, 1

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
    return q, s, hint, 2

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
    return q, s, hint, 1

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
        return q, s, hint, 1
    hint = r"Same signs → positive result. Different signs → negative result."
    return q, s, hint, 1

def gcse_neg_powers():
    """Intermediate: negative numbers with powers — bracket vs no bracket"""
    import random
    n = random.randint(2, 6)
    p = random.choice([2, 3])
    with_bracket = ((-n) ** p)
    without_bracket = -(n ** p)
    q = (rf"(a) Calculate (−{n})^{p}<br>"
         rf"(b) Calculate −{n}^{p}<br>"
         rf"Explain why the answers differ.")
    s = (rf"(a) (−{n})^{p} = (−{n}) × (−{n}){' × (−'+str(n)+')' if p==3 else ''} = <strong>{with_bracket}</strong> "
         rf"(the negative is inside the bracket, so it is raised to the power)<br><br>"
         rf"(b) −{n}^{p} = −({n}^{p}) = −{n**p} = <strong>{without_bracket}</strong> "
         rf"(only {n} is raised to the power; the minus sign stays outside)<br><br>"
         rf"They differ because in (a) the <strong>whole of −{n}</strong> is squared, while in (b) "
         rf"the square only applies to <strong>{n}</strong>.")
    hint = rf"The position of the brackets is critical: (−{n})^{p} ≠ −{n}^{p}."
    return q, s, hint, 2

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
    q = rf"Calculate −{a} × ( {b} − {c} )² + {d}"
    s = (rf"Step 1 — Brackets: {b} − {c} = {inner}<br>"
         rf"Step 2 — Indices: ({inner})² = {inner**2}<br>"
         rf"Step 3 — Multiply: −{a} × {inner**2} = {-a * inner**2}<br>"
         rf"Step 4 — Add: {-a * inner**2} + {d} = <strong>{result}</strong>")
    hint = rf"Remember ({inner})² = {inner**2} (squaring a negative gives a positive). Then apply the − sign in the multiplication step."
    return q, s, hint, 2

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
    q = rf"Calculate   ( {a}² − {b} ) ÷ ( {c} − {d} ) + {e}"
    s = (rf"Numerator (top brackets): {a}² − {b} = {a**2} − {b} = {top}<br>"
         rf"Denominator (bottom brackets): {c} − {d} = {bottom}<br>"
         rf"Divide: {top} ÷ {bottom} = {top/bottom:.4g}<br>"
         rf"Add: {top/bottom:.4g} + {e} = <strong>{result:.4g}</strong>")
    hint = r"Evaluate all brackets first (including the indices inside), divide, then add."
    return q, s, hint, 3


def gcse_maths_bidmas(difficulty, mode):
    if mode == 'exam':
        if difficulty == 'foundational':
            variant = random.choice([gcse_bidmas_simple, gcse_bidmas_brackets,
                                     gcse_bidmas_power, gcse_neg_add_subtract,
                                     gcse_neg_multiply_divide])
        elif difficulty == 'intermediate':
            variant = random.choice([gcse_bidmas_mixed, gcse_neg_powers,
                                     gcse_bidmas_with_negatives, gcse_bidmas_mixed])
        else:
            variant = random.choice([gcse_bidmas_hard, gcse_bidmas_with_negatives,
                                     gcse_neg_powers])
    else:  # revision
        if difficulty == 'foundational':
            variant = random.choice([gcse_bidmas_simple, gcse_bidmas_brackets,
                                     gcse_bidmas_power, gcse_neg_add_subtract,
                                     gcse_neg_multiply_divide])
        elif difficulty == 'intermediate':
            variant = random.choice([gcse_bidmas_mixed, gcse_neg_powers,
                                     gcse_bidmas_with_negatives])
        else:
            variant = random.choice([gcse_bidmas_hard, gcse_bidmas_with_negatives,
                                     gcse_neg_powers])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'bidmas')



# -----------------------------------------------
# GCSE MATHS — ALGEBRA
# -----------------------------------------------
def gcse_maths_algebra(difficulty, mode):

    x = sp.Symbol('x')

    if difficulty == 'foundational':
        a = random.randint(2, 8)
        b = random.randint(1, 10)
        c = random.randint(b + 1, 30)
        ans = sp.Rational(c - b, a)
        q = rf"Solve: \( {a}x + {b} = {c} \)"
        s = rf"Subtract \( {b} \) from both sides: \( {a}x = {c - b} \)<br>Divide by \( {a} \): \( x = \boxed{{{sp.latex(ans)}}} \)"
        hint = r"""
            <strong>Solving a linear equation</strong><br>
            Use inverse operations to isolate \( x \). Whatever is added, subtract it.
            Whatever is multiplied, divide it:
            \[ ax + b = c \Rightarrow x = \frac{c - b}{a} \]
        """
        marks = 2

    elif difficulty == 'intermediate':
        r1 = random.randint(-6, 6)
        r2 = random.randint(-6, 6)
        expr = sp.expand((x - r1) * (x - r2))
        q = rf"Solve: \( {sp.latex(expr)} = 0 \)"
        s = rf"Factorise: \( (x - {r1})(x - {r2}) = 0 \)<br>Therefore \( x = \boxed{{{r1}}} \) or \( x = \boxed{{{r2}}} \)"
        hint = r"""
            <strong>Solving a quadratic by factorisation</strong><br>
            Find two numbers that multiply to give \( c \) and add to give \( b \).
            Write as two brackets and set each equal to zero:
            \[ (x + p)(x + q) = 0 \Rightarrow x = -p \text{ or } x = -q \]
        """
        marks = 3

    else:
        a_c = random.randint(1, 3)
        b_c = random.randint(-8, 8)
        c_c = random.randint(-10, -1)
        discriminant = b_c**2 - 4 * a_c * c_c
        expr = a_c * x**2 + b_c * x + c_c
        r1 = round((-b_c + discriminant**0.5) / (2 * a_c), 2)
        r2 = round((-b_c - discriminant**0.5) / (2 * a_c), 2)
        q = rf"Solve \( {sp.latex(expr)} = 0 \), giving your answers to 2 decimal places."
        s = rf"""Using the quadratic formula:<br><br>
        \( x = \frac{{{-b_c} \pm \sqrt{{{discriminant}}}}}{{{2 * a_c}}} \)<br><br>
        \( x = \boxed{{{r1}}} \) or \( x = \boxed{{{r2}}} \)"""
        hint = r"""
            <strong>The Quadratic Formula</strong><br>
            When a quadratic cannot be factorised easily, use:
            \[ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \]
            Identify \( a \), \( b \), and \( c \) from your equation, substitute carefully,
            and calculate both the \( + \) and \( - \) versions.
        """
        marks = 4

    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'algebra')





# ─────────────────────────────────────────────────────────────
#  GCSE MATHS — SURDS
# ─────────────────────────────────────────────────────────────

def gcse_surds_simplify():
    """Foundational: simplify a single surd √n"""
    # pick a product of a perfect square and a small prime
    square = random.choice([4, 9, 16, 25, 36, 49])
    prime  = random.choice([2, 3, 5, 6, 7])
    n = square * prime
    k = int(math.sqrt(square))
    q = (rf"Write √{n} in its simplest surd form.")
    s = (rf"Find the largest square factor of {n}: that is {square} (since {square} × {prime} = {n}).<br>"
         rf"√{n} = √({square} × {prime}) = √{square} × √{prime} = <strong>{k}√{prime}</strong>")
    hint = r"Look for the largest square number that divides exactly into the number under the root."
    return q, s, hint, 2

def gcse_surds_simplify_multiple():
    """Foundational: write p√n in the form k√r"""
    square = random.choice([4, 9, 16, 25])
    prime  = random.choice([2, 3, 5, 7])
    n = square * prime
    p = random.choice([2, 3, 4, 5])
    k_inner = int(math.sqrt(square))
    k_total = p * k_inner
    q = (rf"Write {p}√{n} in the form k√{prime}, where k is an integer.")
    s = (rf"First simplify √{n}: √{n} = √({square} × {prime}) = {k_inner}√{prime}<br>"
         rf"Then multiply: {p} × {k_inner}√{prime} = <strong>{k_total}√{prime}</strong>")
    hint = rf"Simplify √{n} first by finding its square factor, then multiply by {p}."
    return q, s, hint, 2

def gcse_surds_add_subtract():
    """Foundational: add or subtract surds after simplifying"""
    prime = random.choice([2, 3, 5])
    a_sq  = random.choice([4, 9, 16])
    b_sq  = random.choice([4, 9, 25])
    a_coef = int(math.sqrt(a_sq))  # coefficient after simplifying first surd
    b_coef = int(math.sqrt(b_sq))  # coefficient after simplifying second surd
    n1 = a_sq * prime
    n2 = b_sq * prime
    total = a_coef + b_coef
    q = rf"Simplify √{n1} + √{n2}. Write your answer in the form k√{prime}."
    s = (rf"√{n1} = √({a_sq} × {prime}) = {a_coef}√{prime}<br>"
         rf"√{n2} = √({b_sq} × {prime}) = {b_coef}√{prime}<br>"
         rf"{a_coef}√{prime} + {b_coef}√{prime} = <strong>{total}√{prime}</strong>")
    hint = rf"Simplify each surd separately first, then add the coefficients in front of √{prime}."
    return q, s, hint, 2

def gcse_surds_multiply():
    """Foundational: multiply two simple surds"""
    a = random.choice([2, 3, 5, 6, 7])
    b = random.choice([2, 3, 5, 6, 7])
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
    else:
        ans = f"√{product}"
        sol = rf"√{a} × √{b} = √({a} × {b}) = <strong>√{product}</strong>"
    q = rf"Simplify √{a} × √{b}."
    hint = r"Use the rule √a × √b = √(ab), then check if the result can be simplified further."
    return q, sol, hint, 2

def gcse_surds_expand_simple():
    """Intermediate: expand (a + √b)(a − √b) — difference of two squares"""
    a = random.choice([2, 3, 4, 5])
    b = random.choice([2, 3, 5, 7])
    result = a**2 - b
    q = rf"Expand and simplify (  {a} + √{b}  )(  {a} − √{b}  )."
    s = (rf"Use the difference of two squares pattern (p + q)(p − q) = p² − q²:<br>"
         rf"({a})² − (√{b})² = {a**2} − {b} = <strong>{result}</strong>")
    hint = r"(a + √b)(a − √b) = a² − b. The surd terms cancel out."
    return q, s, hint, 2

def gcse_surds_expand_double():
    """Intermediate: expand (a + √b)(c + √b) — general double bracket"""
    a = random.choice([1, 2, 3])
    c = random.choice([1, 2, 3])
    b = random.choice([2, 3, 5])
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
    return q, s, hint, 2

def gcse_surds_square_bracket():
    """Intermediate: expand (a + √b)² — write in form p + q√b"""
    a = random.choice([2, 3, 4, 5])
    b = random.choice([2, 3, 5, 6])
    # (a + √b)² = a² + 2a√b + b
    const = a**2 + b
    coef  = 2 * a
    q = rf"Write ( {a} + √{b} )² in the form p + q√{b}, where p and q are integers."
    s = (rf"( {a} + √{b} )² = ( {a} + √{b} )( {a} + √{b} )<br>"
         rf"= {a}² + {a}√{b} + {a}√{b} + (√{b})²<br>"
         rf"= {a**2} + {coef}√{b} + {b}<br>"
         rf"= <strong>{const} + {coef}√{b}</strong>")
    hint = rf"(a + √b)² = a² + 2a√b + b. Don't forget the middle term 2a√b."
    return q, s, hint, 2

def gcse_surds_square_bracket_minus():
    """Intermediate: expand (a − √b)² — write in form p + q√b"""
    a = random.choice([2, 3, 4, 5])
    b = random.choice([2, 3, 5, 6])
    const = a**2 + b
    coef  = 2 * a  # coefficient (but negative in working, positive in result)
    q = rf"Write ( {a} − √{b} )² in the form p + q√{b}, where p and q are integers."
    s = (rf"( {a} − √{b} )² = ( {a} − √{b} )( {a} − √{b} )<br>"
         rf"= {a}² − {a}√{b} − {a}√{b} + (√{b})²<br>"
         rf"= {a**2} − {coef}√{b} + {b}<br>"
         rf"= <strong>{const} − {coef}√{b}</strong>")
    hint = rf"(a − √b)² = a² − 2a√b + b. Note: (−√b)² = +b."
    return q, s, hint, 2

def gcse_surds_rationalise_simple():
    """Intermediate: rationalise 1/√a or k/√a"""
    a   = random.choice([2, 3, 5, 6, 7])
    num = random.choice([1, 2, 3, 4, 6])
    import math as _m
    # simplify num/a if possible
    from math import gcd
    g   = gcd(num, a)
    n_s = num // g
    d_s = a // g
    if d_s == 1:
        ans = f"{n_s}√{a}"
    else:
        ans = f"{n_s}√{a} / {d_s}" if n_s > 1 else f"√{a} / {d_s}"
    q = rf"Rationalise the denominator of {num} / √{a}. Write your answer in its simplest form."
    s = (rf"Multiply numerator and denominator by √{a}:<br>"
         rf"({num} × √{a}) / (√{a} × √{a}) = {num}√{a} / {a}<br>"
         rf"Simplify: <strong>{ans}</strong>")
    hint = rf"Multiply top and bottom by √{a} to clear the surd from the denominator."
    return q, s, hint, 2

def gcse_surds_rationalise_compound():
    """Intermediate: rationalise k/(a + √b) using conjugate"""
    a   = random.choice([1, 2, 3])
    b   = random.choice([2, 3, 5])
    num = random.choice([2, 4, 6])
    # result numerator: num(a − √b), denominator: a² − b
    denom = a**2 - b
    # make sure denom != 0
    while denom == 0:
        a = random.choice([2, 3, 4])
        b = random.choice([2, 3, 5])
        denom = a**2 - b
    sign = "−" if denom > 0 else "+"
    abs_denom = abs(denom)
    from math import gcd
    g = gcd(num, abs_denom)
    n_s = num // g
    d_s = abs_denom // g
    if denom < 0:
        # flip signs
        if d_s == 1:
            ans = f"−{n_s}({a} − √{b})" if n_s > 1 else f"−({a} − √{b})"
        else:
            ans = f"−{n_s}({a} − √{b}) / {d_s}" if n_s > 1 else f"−({a} − √{b}) / {d_s}"
    else:
        if d_s == 1:
            ans = f"{n_s}({a} − √{b})" if n_s > 1 else f"({a} − √{b})"
        else:
            ans = f"{n_s}({a} − √{b}) / {d_s}" if n_s > 1 else f"({a} − √{b}) / {d_s}"
    q = rf"Rationalise the denominator: {num} / ( {a} + √{b} )"
    s = (rf"Multiply top and bottom by the conjugate ( {a} − √{b} ):<br>"
         rf"Numerator: {num}({a} − √{b}) = {num*a} − {num}√{b}<br>"
         rf"Denominator: ({a} + √{b})({a} − √{b}) = {a}² − {b} = {a**2} − {b} = {denom}<br>"
         rf"Result: ({num*a} − {num}√{b}) / {denom}<br>"
         rf"Simplified: <strong>{ans}</strong>")
    hint = rf"The conjugate of ({a} + √{b}) is ({a} − √{b}). Multiplying gives a² − b, removing the surd from the denominator."
    return q, s, hint, 3

def gcse_surds_show_that_rationalise():
    """Exam: 'show that' rationalise with a compound denominator"""
    # (p + q√r) / (a + √r) → show it equals a given simplified form
    r  = random.choice([2, 3, 5])
    a  = random.choice([1, 2, 3])
    q_coef = random.choice([1, 2])
    p  = random.choice([2, 3, 4, 5])
    # numerator: p + q_coef*√r,  denominator: a + √r
    # multiply by conjugate (a - √r)
    # num * conj = (p + q√r)(a - √r) = pa - p√r + qa√r - q*r
    #            = (pa - qr) + (qa - p)√r
    # denom * conj = a² - r
    new_const = p * a - q_coef * r
    new_coef  = q_coef * a - p
    new_denom = a**2 - r
    # avoid trivial / undefined
    if new_denom == 0 or new_denom == 1:
        # fallback values
        r, a, q_coef, p = 2, 3, 1, 5
        new_const = p * a - q_coef * r
        new_coef  = q_coef * a - p
        new_denom = a**2 - r
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
    return q_text, s, hint, 3

def gcse_surds_identity():
    """Exam: (√a + √b)(√a − √b) = a − b as an algebraic result"""
    q_text = r"Simplify fully ( √a + √b )( √a − √b )."
    s = (r"Use the difference of two squares: (p + q)(p − q) = p² − q²<br>"
         r"Here p = √a and q = √b:<br>"
         r"(√a)² − (√b)² = <strong>a − b</strong>")
    hint = r"(√a + √b)(√a − √b) is a difference of two squares pattern."
    return q_text, s, hint, 2

def gcse_surds_exact_area():
    """Exam: find area of a rectangle with surd side lengths"""
    a = random.choice([2, 3, 5])
    b = random.choice([2, 3, 5, 7])
    # sides: (p + √a) and (q + √b) — but keep it simple for GCSE
    p = random.choice([1, 2, 3])
    # Area = p√a × q√b — or use a simpler rectangle
    q_coef = random.choice([2, 3, 4])
    side1 = p
    side2_surd = a
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
    else:
        ans = f"{total_k}√{rem} cm²"
        sol_step = (rf"√{a} × √{b} = √{product_surd}<br>"
                    rf"Simplify √{product_surd}: largest square factor = {largest_sq}, so √{product_surd} = {k_inner}√{rem}<br>"
                    rf"Area = {p} × {q_coef} × {k_inner}√{rem} = <strong>{ans}</strong>")
    s = (rf"Area = length × width = {p}√{a} × {q_coef}√{b}<br>"
         rf"= ({p} × {q_coef}) × (√{a} × √{b})<br>"
         + sol_step)
    hint = r"Multiply the integer parts together and the surd parts together, then simplify the resulting surd."
    return q_text, s, hint, 3

def gcse_surds_expand_diff_subtract():
    """Exam: expand (p + √q)² − (p − √q)², show it simplifies to k√q"""
    p  = random.choice([2, 3, 4])
    q  = random.choice([2, 3, 5])
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
    return q_text, s, hint, 3


def gcse_maths_surds(difficulty, mode):
    if mode == 'exam':
        if difficulty == 'foundational':
            variant = random.choice([
                gcse_surds_simplify,
                gcse_surds_simplify_multiple,
                gcse_surds_add_subtract,
                gcse_surds_multiply,
            ])
        elif difficulty == 'intermediate':
            variant = random.choice([
                gcse_surds_expand_simple,
                gcse_surds_expand_double,
                gcse_surds_square_bracket,
                gcse_surds_square_bracket_minus,
                gcse_surds_rationalise_simple,
                gcse_surds_rationalise_compound,
            ])
        else:  # difficult
            variant = random.choice([
                gcse_surds_show_that_rationalise,
                gcse_surds_identity,
                gcse_surds_exact_area,
                gcse_surds_expand_diff_subtract,
            ])
    else:  # revision mode
        if difficulty == 'foundational':
            variant = random.choice([
                gcse_surds_simplify,
                gcse_surds_simplify_multiple,
                gcse_surds_add_subtract,
                gcse_surds_multiply,
            ])
        elif difficulty == 'intermediate':
            variant = random.choice([
                gcse_surds_expand_simple,
                gcse_surds_expand_double,
                gcse_surds_square_bracket,
                gcse_surds_square_bracket_minus,
                gcse_surds_rationalise_simple,
                gcse_surds_rationalise_compound,
            ])
        else:  # difficult
            variant = random.choice([
                gcse_surds_show_that_rationalise,
                gcse_surds_identity,
                gcse_surds_exact_area,
                gcse_surds_expand_diff_subtract,
            ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'surds')



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

