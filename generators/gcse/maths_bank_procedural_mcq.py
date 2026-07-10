"""
Procedural difficult-tier MCQ generators for GCSE maths topics that use fixed MCQ banks.
Each topic has two randomised generators, included only when difficulty == 'difficult'.
"""
import random
import math


def _letter_opts(correct, wrong_candidates, fmt=str):
    letters = "ABCD"
    correct_s = fmt(correct)
    wrong = []
    for cand in wrong_candidates:
        s = fmt(cand)
        if s != correct_s and s not in wrong:
            wrong.append(s)
        if len(wrong) == 3:
            break
    offset = 1
    while len(wrong) < 3:
        for cand in (correct + offset, correct - offset):
            s = fmt(cand)
            if s != correct_s and s not in wrong:
                wrong.append(s)
            if len(wrong) == 3:
                break
        offset += 1
    vals = wrong[:3] + [correct_s]
    random.shuffle(vals)
    correct_letter = letters[vals.index(correct_s)]
    opts = [f"{letters[i]}  {vals[i]}" for i in range(4)]
    return opts, correct_letter


def _string_opts(correct, candidates):
    letters = "ABCD"
    wrong = []
    for cand in candidates:
        if cand != correct and cand not in wrong:
            wrong.append(cand)
        if len(wrong) == 3:
            break
    offset = 1
    while len(wrong) < 3:
        for cand in candidates:
            alt = f"{cand}?" if offset == 1 else f"{cand} ({offset})"
            if alt != correct and alt not in wrong:
                wrong.append(alt)
            if len(wrong) == 3:
                break
        offset += 1
    vals = wrong[:3] + [correct]
    random.shuffle(vals)
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {vals[i]}" for i in range(4)]
    return opts, correct_letter


def procedural_mcq_for(topic_slug):
    return _PROCEDURAL.get(topic_slug, [])


# ══════════════════════════════════════════════════════════════════════════════
# SIMULTANEOUS EQUATIONS
# ══════════════════════════════════════════════════════════════════════════════

def _sim_proc_elimination():
    x, y = random.randint(2, 6), random.randint(2, 6)
    a1, b1 = random.randint(2, 4), 1
    a2, b2 = a1 + random.randint(1, 3), 1
    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y
    correct = x
    opts, letter = _letter_opts(correct, [y, x + 1, x - 1])
    q = (
        rf"Solve: \({a1}x + y = {c1}\) and \({a2}x + y = {c2}\). What is <strong>\(x\)</strong>?"
    )
    sol = (
        rf"<strong>Step 1</strong> — subtract (2) from (1) (the \(y\) terms match): "
        rf"\({a2 - a1}x = {c2 - c1}\) → \(x = {x}\).<br>"
        rf"<strong>Step 2</strong> — substitute into (1): \(y = {y}\).<br>"
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Subtract when the y-terms match.", 3, opts, letter


def _sim_proc_substitution():
    m, c = random.randint(2, 5), random.randint(1, 6)
    x = random.randint(2, 7)
    y = m * x + c
    a = random.randint(2, 4)
    rhs = a * x + y
    correct = y
    opts, letter = _letter_opts(correct, [x, m * x, y + 1, y - 1])
    q = (
        rf"If \(y = {m}x + {c}\) and \({a}x + y = {rhs}\), what is <strong>\(y\)</strong>?"
    )
    sub_lhs = a + m
    sub_rhs = rhs - c
    sol = (
        rf"<strong>Step 1</strong> — substitute \(y = {m}x + {c}\) into \({a}x + y = {rhs}\): "
        rf"\({a}x + {m}x + {c} = {rhs}\).<br>"
        rf"<strong>Step 2</strong> — solve: \({sub_lhs}x = {sub_rhs}\) → \(x = {x}\), "
        rf"so \(y = {m}({x}) + {c} = {y}\).<br>"
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Replace y, solve for x, then find y.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# EQUATIONS & INEQUALITIES
# ══════════════════════════════════════════════════════════════════════════════

def _eq_proc_quadratic_roots():
    r1, r2 = random.randint(2, 5), random.randint(2, 5)
    while r2 == r1:
        r2 = random.randint(2, 5)
    b, c = -(r1 + r2), r1 * r2
    correct = max(r1, r2)
    opts, letter = _letter_opts(correct, [min(r1, r2), r1 + r2, -correct])
    q = rf"Solve \(x^2 {('+' if b >= 0 else '-')} {abs(b)}x {('+' if c >= 0 else '-')} {abs(c)} = 0\). The larger root is:"
    sol = (
        rf"Factorise: \((x-{r1})(x-{r2})=0\) → \(x={r1}\) or \(x={r2}\). "
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Factorise or use the formula.", 3, opts, letter


def _eq_proc_inequality_flip():
    a = random.randint(3, 7)
    b = random.randint(8, 20)
    correct = f"x < {b // a}"
    opts, letter = _string_opts(correct, [
        f"x > {b // a}", f"x < {-(b // a)}", f"x > {-(b // a)}",
    ])
    q = rf"Solve \(-{a}x < {b}\)."
    sol = (
        rf"Divide by \(-{a}\) and flip: \(x < {b // a}\). Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Flip the inequality sign when dividing by a negative.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# BIDMAS
# ══════════════════════════════════════════════════════════════════════════════

def _bidmas_proc_nested():
    a, b, c = random.randint(2, 4), random.randint(2, 5), random.randint(2, 4)
    correct = a + b * c
    opts, letter = _letter_opts(correct, [(a + b) * c, a * b + c, a + b + c])
    q = rf"Work out \( {a} + {b} \times {c} \)."
    sol = rf"× first: \({b} \times {c} = {b*c}\), then \(+{a}\) → <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Multiply before adding.", 2, opts, letter


def _bidmas_proc_brackets_power():
    p = random.randint(2, 3)
    a, b = random.randint(2, 4), random.randint(1, 3)
    correct = (a + b) ** p
    opts, letter = _letter_opts(correct, [a ** p + b, a + b ** p, a * b * p])
    q = rf"Evaluate \(({a} + {b})^{p}\)."
    sol = rf"Bracket first: \({a+b}\), then power → <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Brackets before powers.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# FDP
# ══════════════════════════════════════════════════════════════════════════════

def _fdp_proc_reverse_percent():
    pct = random.choice([10, 20, 25])
    final = random.choice([90, 120, 150, 200])
    original = int(final * 100 / (100 - pct))
    correct = original
    opts, letter = _letter_opts(correct, [final - pct, final + pct, int(final * 100 / (100 + pct))])
    q = rf"After a <strong>{pct}% reduction</strong>, a price is <strong>£{final}</strong>. What was the original price?"
    sol = (
        rf"Original × \({100-pct})/100 = {final}\) → original = <strong>£{original}</strong>. "
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Divide by the percentage multiplier.", 3, opts, letter


def _fdp_proc_fraction_of():
    den = random.choice([4, 5, 8, 10, 20])
    num = random.randint(1, den - 1)
    g = math.gcd(num, den)
    num, den = num // g, den // g
    total = den * random.randint(8, 35)
    correct = total * num // den
    opts, letter = _letter_opts(correct, [total - correct, correct + den, total // den])
    q = rf"What is <strong>\(\dfrac{{{num}}}{{{den}}}\)</strong> of <strong>{total}</strong>?"
    sol = rf"\({total} \times {num}/{den} = {correct}\). Answer: <strong>{letter}</strong>"
    return q, sol, "Multiply by the fraction.", 2, opts, letter


def _fdp_proc_percent_change():
    original = random.randint(40, 200)
    pct = random.choice([10, 15, 20, 25])
    new = round(original * (1 + pct / 100))
    correct = f"{pct}% increase"
    opts, letter = _string_opts(correct, [
        f"{pct}% decrease",
        f"{pct + 5}% increase",
        f"{100 - pct}% increase",
    ])
    q = rf"A value changes from <strong>{original}</strong> to <strong>{new}</strong>. What is the percentage change?"
    sol = rf"Change = {new - original}; ({new - original}/{original})×100 = <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Divide change by original, then ×100.", 3, opts, letter


def _fdp_proc_decimal_to_percent():
    num, den = random.choice([(1, 4), (3, 8), (2, 5), (7, 20), (3, 5)])
    dec = num / den
    pct = dec * 100
    correct = f"{pct:g}%" if pct != int(pct) else f"{int(pct)}%"
    opts, letter = _string_opts(correct, [f"{dec:g}", f"{pct/10:g}%", f"{pct*10:g}%"])
    q = rf"Write <strong>{dec:g}</strong> as a percentage."
    sol = rf"{dec:g} × 100 = <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Multiply by 100.", 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# MULTIPLES & FACTORS
# ══════════════════════════════════════════════════════════════════════════════

def _mf_proc_hcf():
    a, b = random.randint(12, 72), random.randint(12, 72)
    g = math.gcd(a, b)
    correct = g
    opts, letter = _letter_opts(correct, [a // 2, b // 2, a + b, max(a, b)])
    q = rf"What is the HCF of <strong>{a}</strong> and <strong>{b}</strong>?"
    sol = rf"HCF = <strong>{g}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Highest common factor.", 2, opts, letter


def _mf_proc_lcm():
    a, b = random.randint(4, 18), random.randint(4, 18)
    l = (a * b) // math.gcd(a, b)
    correct = l
    opts, letter = _letter_opts(correct, [a * b, a + b, l + a, l - a])
    q = rf"What is the LCM of <strong>{a}</strong> and <strong>{b}</strong>?"
    sol = rf"LCM = <strong>{l}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Lowest number in both times tables.", 3, opts, letter


def _mf_proc_prime_factors():
    n = random.choice([random.randint(36, 72), random.randint(80, 150)])
    pf = {}
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            pf[d] = pf.get(d, 0) + 1
            temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        pf[temp] = pf.get(temp, 0) + 1
    parts = []
    for p in sorted(pf):
        parts.append(f"{p}^{pf[p]}" if pf[p] > 1 else str(p))
    correct = " × ".join(parts)
    opts, letter = _string_opts(correct, [
        " × ".join(f"{p}^{pf[p]+1}" if pf[p] > 0 else str(p) for p in sorted(pf)),
        str(n),
        " × ".join(str(p) for p in sorted(pf)),
    ])
    q = rf"Write <strong>{n}</strong> as a product of prime factors."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Use a factor tree.", 3, opts, letter


def _mf_proc_factor_of():
    n = random.randint(24, 120)
    factors = [i for i in range(1, int(n ** 0.5) + 1) if n % i == 0]
    all_f = sorted({f for i in factors for f in (i, n // i)})
    correct = random.choice([f for f in all_f if f not in (1, n)] or all_f)
    opts, letter = _letter_opts(correct, [n + 1, n - 1 if n > 2 else n + 2, correct + 1])
    q = rf"Which is a factor of <strong>{n}</strong>?"
    sol = rf"<strong>{correct}</strong> divides {n}. Answer: <strong>{letter}</strong>"
    return q, sol, "A factor divides exactly.", 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# DECIMALS
# ══════════════════════════════════════════════════════════════════════════════

def _dec_proc_bounds():
    n = round(random.uniform(2.5, 8.5), 1)
    lower = math.floor(n * 10) / 10
    upper = lower + 0.1
    correct = f"{lower} ≤ x < {upper}"
    opts, letter = _string_opts(correct, [
        f"{lower} < x ≤ {upper}",
        f"{lower - 0.1} ≤ x < {lower}",
        f"{upper} ≤ x < {upper + 0.1}",
    ])
    q = rf"\(x\) is rounded to 1 d.p. as <strong>{n}</strong>. Write the error interval."
    sol = (
        rf"1 d.p. → unit of accuracy 0.1, half = 0.05<br>"
        rf"Lower: {n} − 0.05 = {lower}, upper: {n} + 0.05 = {upper}<br>"
        rf"Error interval: <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    )
    return q, sol, (
        "Add and subtract 0.05 (half of 0.1). Write lower ≤ x < upper — the upper bound is excluded."
    ), 3, opts, letter


def _dec_proc_divide():
    a = round(random.uniform(1.2, 4.8), 1)
    b = random.choice([0.2, 0.4, 0.5])
    mult = 10
    a_int = int(round(a * mult))
    b_int = int(round(b * mult))
    correct = round(a / b, 1)
    opts, letter = _letter_opts(correct, [round(a * b, 1), round(a + b, 1), round(a / (b * 10), 1)], fmt=lambda x: f"{x:.1f}")
    q = rf"Work out <strong>{a} ÷ {b}</strong>."
    sol = (
        rf"×{mult} both: {a}×{mult} = {a_int}, {b}×{mult} = {b_int}<br>"
        rf"{a_int} ÷ {b_int} = <strong>{correct:.1f}</strong>. Answer: <strong>{letter}</strong>"
    )
    return q, sol, (
        "Multiply dividend and divisor by 10 so the divisor is a whole number, then divide as usual."
    ), 3, opts, letter


def _dec_proc_multiply():
    a = round(random.uniform(1.2, 4.9), 1)
    b = round(random.uniform(1.2, 3.9), 1)
    correct = round(a * b, 2)
    a_int = int(a * 10)
    b_int = int(b * 10)
    opts, letter = _letter_opts(correct, [round(a + b, 2), round(a / b, 2), round(a * b * 10, 2)], fmt=lambda x: f"{x:.2f}")
    q = rf"Work out <strong>{a} × {b}</strong>."
    sol = (
        rf"{a_int} × {b_int} = {a_int * b_int}; 1 d.p. + 1 d.p. = 2 d.p.<br>"
        rf"<strong>{correct:.2f}</strong>. Answer: <strong>{letter}</strong>"
    )
    return q, sol, (
        "Multiply as integers (ignore the decimal points), then count decimal places in both factors "
        "and insert the point that many places from the right."
    ), 2, opts, letter


def _dec_proc_round():
    n = round(random.uniform(1.0, 99.9), 3)
    dp = random.choice([1, 2])
    correct = round(n, dp)
    n_str = f"{n:.4f}"
    decide = n_str.split(".")[1][dp] if "." in n_str and len(n_str.split(".")[1]) > dp else "0"
    opts, letter = _letter_opts(correct, [round(n, dp + 1), round(n + 0.1, dp), round(n - 0.1, dp)], fmt=lambda x: f"{x:.{dp}f}")
    q = rf"Round <strong>{n}</strong> to {dp} decimal place{'s' if dp > 1 else ''}."
    sol = (
        rf"Deciding digit ({dp + 1}{'st' if dp == 0 else 'nd' if dp == 1 else 'rd'} d.p.): {decide}"
        f"{' → round up' if int(decide) >= 5 else ' → round down'}<br>"
        rf"<strong>{correct:.{dp}f}</strong>. Answer: <strong>{letter}</strong>"
    )
    return q, sol, (
        "Find the digit one place beyond where you round. 5 or above → increase the last kept digit by 1."
    ), 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# ALGEBRA
# ══════════════════════════════════════════════════════════════════════════════

def _alg_proc_expand():
    a, b = random.randint(2, 4), random.randint(1, 5)
    c, d = random.randint(2, 4), random.randint(1, 5)
    ac, ad_bc, bd = a * c, a * d + b * c, b * d
    correct = f"{ac}x² + {ad_bc}x + {bd}"
    opts, letter = _string_opts(correct, [
        f"{ac}x² + {a*d}x + {bd}",
        f"{(a+b)*(c+d)}x² + {bd}",
        f"{ac}x + {ad_bc}x + {bd}",
    ])
    q = rf"Expand <strong>\(({a}x + {b})({c}x + {d})\)</strong>."
    sol = rf"FOIL → <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Multiply each term in the first bracket by each in the second.", 3, opts, letter


def _alg_proc_factorise_quad():
    r1, r2 = random.randint(2, 4), random.randint(2, 5)
    while r2 == r1:
        r2 = random.randint(2, 5)
    b, c = -(r1 + r2), r1 * r2
    correct = f"(x - {r1})(x - {r2})"
    opts, letter = _string_opts(correct, [
        f"(x + {r1})(x + {r2})", f"(x - {r1})(x + {r2})", f"x(x - {r1 + r2})",
    ])
    q = rf"Factorise <strong>\(x^2 - {r1+r2}x + {c}\)</strong>."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Find two numbers that multiply to c and add to the x-coefficient.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# SURDS
# ══════════════════════════════════════════════════════════════════════════════

def _surd_proc_simplify():
    k = random.choice([2, 3, 4])
    m = random.choice([2, 3, 5])
    n = k * k * m
    correct = f"{k}√{m}"
    opts, letter = _string_opts(correct, [f"√{n}", f"{k+m}", f"{k}√{n}"])
    q = rf"Simplify <strong>√{n}</strong>."
    sol = rf"√{n} = <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Find the largest square factor.", 3, opts, letter


def _surd_proc_rationalise():
    d = random.choice([2, 3, 5])
    correct = f"√{d}/{d}"
    opts, letter = _string_opts(correct, [f"1/√{d}", f"√{d}", f"{d}/√{d}"])
    q = rf"Rationalise <strong>\(\dfrac{{1}}{{\sqrt{{{d}}}}}\)</strong>."
    sol = rf"Multiply top and bottom by √{d}: <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Multiply by √d/√d.", 3, opts, letter


def _surd_proc_multiply():
    a = random.choice([2, 3, 5, 6, 7])
    b = random.choice([2, 3, 5, 6, 12])
    product = a * b
    largest_sq = 1
    for s in (4, 9, 16, 25, 36):
        if product % s == 0:
            largest_sq = s
    if largest_sq > 1:
        k = int(math.sqrt(largest_sq))
        rem = product // largest_sq
        correct = str(k) if rem == 1 else f"{k}√{rem}"
    else:
        correct = f"√{product}"
    opts, letter = _string_opts(correct, [f"√{a + b}", f"{a}√{b}", f"√{product + 1}"])
    q = rf"Simplify <strong>\(\sqrt{{{a}}} \times \sqrt{{{b}}}\)</strong>."
    sol = rf"\(\sqrt{{{product}}}\) → <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "√a × √b = √(ab), then simplify.", 2, opts, letter


def _surd_proc_add_like():
    p = random.choice([2, 3, 5])
    c1 = random.choice([2, 3, 4, 5])
    c2 = random.choice([1, 2, 3, 4])
    n1, n2 = c1 * c1 * p, c2 * c2 * p
    total = c1 + c2
    correct = f"{total}√{p}"
    opts, letter = _string_opts(correct, [f"√{n1 + n2}", f"{c1 + c2}√{n1}", f"{total}√{n1}"])
    q = rf"Simplify <strong>\(\sqrt{{{n1}}} + \sqrt{{{n2}}}\)</strong>."
    sol = rf"{c1}√{p} + {c2}√{p} = <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Simplify each surd, then add coefficients.", 2, opts, letter


def _surd_proc_between_integers():
    lo = random.randint(5, 12)
    hi = lo + 1
    n = random.randint(lo * lo + 1, hi * hi - 1)
    correct = f"{lo} and {hi}"
    opts, letter = _string_opts(correct, [
        f"{lo - 1} and {lo}", f"{hi} and {hi + 1}", f"{lo} and {hi + 1}",
    ])
    q = rf"\(\sqrt{{{n}}}\) lies between which consecutive whole numbers?"
    sol = rf"{lo}² < {n} < {hi}² → <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Compare with nearby perfect squares.", 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# SEQUENCES
# ══════════════════════════════════════════════════════════════════════════════

def _seq_proc_nth_linear():
    a, b = random.randint(2, 6), random.randint(-3, 8)
    n = random.randint(5, 12)
    correct = a * n + b
    opts, letter = _letter_opts(correct, [a * n, a + b * n, correct + a])
    q = rf"The \(n\)th term is <strong>\({a}n + {b}\)</strong>. Find term <strong>{n}</strong>."
    sol = rf"Substitute \(n={n}\): <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Replace n in the nth-term formula.", 2, opts, letter


def _seq_proc_quadratic_diff():
    # constant second difference 2 -> n^2 sequence offset
    c = random.randint(1, 5)
    n = random.randint(4, 8)
    correct = n * n + c
    opts, letter = _letter_opts(correct, [n * (n + 1) + c, n * n, correct + 2])
    q = rf"A quadratic sequence has \(n\)th term <strong>\(n^2 + {c}\)</strong>. Find the <strong>{n}</strong>th term."
    sol = rf"\({n}^2 + {c} = {correct}\). Answer: <strong>{letter}</strong>"
    return q, sol, "Substitute the term number.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# GEOMETRY & ANGLES
# ══════════════════════════════════════════════════════════════════════════════

def _geom_proc_parallel():
    x = random.randint(40, 70)
    y = 180 - 2 * x
    correct = y
    opts, letter = _letter_opts(correct, [x, 180 - x, x + 20])
    q = (
        rf"Parallel lines cut by a transversal. One angle is <strong>{x}°</strong>. "
        rf"Co-interior angles sum to 180°. The other co-interior angle is:"
    )
    sol = rf"\(180 - {x} = {y}°\). Answer: <strong>{letter}</strong>"
    return q, sol, "Co-interior angles add to 180°.", 2, opts, letter


def _geom_proc_polygon():
    n = random.choice([5, 6, 8, 10])
    exterior = 360 // n
    correct = exterior
    opts, letter = _letter_opts(correct, [180 - exterior, 360 // (n - 1), exterior + 10])
    q = rf"Each exterior angle of a regular <strong>{n}-gon</strong> is:"
    sol = rf"\(360 ÷ {n} = {exterior}°\). Answer: <strong>{letter}</strong>"
    return q, sol, "Exterior angles sum to 360°.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# TRANSFORMATIONS
# ══════════════════════════════════════════════════════════════════════════════

def _trans_proc_translation():
    dx, dy = random.randint(-5, 5), random.randint(-5, 5)
    while dx == 0 or dy == 0:
        dx, dy = random.randint(-5, 5), random.randint(-5, 5)
    px, py = random.randint(1, 6), random.randint(1, 6)
    correct = f"({px + dx}, {py + dy})"
    opts, letter = _string_opts(correct, [
        f"({px - dx}, {py - dy})",
        f"({px}, {py + dy})",
        f"({px + dx}, {py})",
        f"({px + dy}, {py + dx})",
    ])
    vec = f"({dx}, {dy})" if dy >= 0 else f"({dx}, {dy})"
    q = rf"Point <strong>({px}, {py})</strong> is translated by <strong>{vec}</strong>. The image is:"
    sol = rf"Add the vector: <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Add dx to x and dy to y.", 2, opts, letter


def _trans_proc_reflection():
    px = random.randint(2, 7)
    correct = f"({-px}, 3)"
    opts, letter = _string_opts(correct, [
        f"({px}, -3)", f"(3, {px})", f"({-px}, -3)", f"({px}, 3)",
    ])
    q = rf"Reflect <strong>({px}, 3)</strong> in the <strong>y-axis</strong>. The image is:"
    sol = rf"x becomes \(-x\): <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Reflection in y-axis: (x,y)→(-x,y).", 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# MENSURATION
# ══════════════════════════════════════════════════════════════════════════════

def _mens_proc_circle():
    r = random.randint(3, 9)
    correct = round(math.pi * r * r, 1)
    opts, letter = _letter_opts(correct, [round(2 * math.pi * r, 1), round(math.pi * r, 1), round(r * r, 1)], fmt=lambda x: f"{x:.1f}")
    q = rf"A circle has radius <strong>{r} cm</strong>. Its area is (π ≈ 3.14):"
    sol = rf"\(A = \pi r^2 = \pi \times {r}^2\) ≈ <strong>{correct:.1f} cm²</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Use A = πr².", 3, opts, letter


def _mens_proc_trapezium():
    a, b, h = random.randint(4, 8), random.randint(6, 12), random.randint(3, 7)
    correct = (a + b) * h // 2
    opts, letter = _letter_opts(correct, [a * h, b * h, (a + b) * h])
    q = rf"A trapezium has parallel sides <strong>{a} cm</strong> and <strong>{b} cm</strong>, height <strong>{h} cm</strong>. Area ="
    sol = rf"\(\frac{{{a}+{b}}}{{2}} \times {h} = {correct}\) cm². Answer: <strong>{letter}</strong>"
    return q, sol, "Average of parallel sides × height.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# BEARINGS
# ══════════════════════════════════════════════════════════════════════════════

def _brg_proc_back_bearing():
    b = random.randint(20, 160)
    back = (b + 180) % 360
    correct = f"{back:03d}°"
    opts, letter = _string_opts(correct, [
        f"{b:03d}°",
        f"{(360-b):03d}°",
        f"{(b+90)%360:03d}°",
        f"{(b-90)%360:03d}°",
        f"{(back+45)%360:03d}°",
    ])
    q = rf"The bearing of B from A is <strong>{b:03d}°</strong>. The back bearing of A from B is:"
    sol = rf"Add 180°: <strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Back bearing = forward bearing ± 180°.", 2, opts, letter


def _brg_proc_three_figure():
    b = random.randint(5, 45)
    correct = f"{b:03d}°"
    opts, letter = _string_opts(correct, [
        f"{b}°", f"{b*10}°", f"{(b+100)%360:03d}°", f"{(b+200)%360:03d}°",
    ])
    q = rf"Which is the correct three-figure bearing for <strong>{b}°</strong> clockwise from North?"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Always use three digits.", 1, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# CIRCLE THEOREMS
# ══════════════════════════════════════════════════════════════════════════════

def _ct_proc_semicircle():
    correct = "90°"
    opts, letter = _string_opts(correct, ["45°", "180°", "60°"])
    q = r"Angle in a <strong>semicircle</strong> is:"
    sol = rf"Angle in a semicircle = <strong>90°</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Thales' theorem.", 1, opts, letter


def _ct_proc_tangent_radius():
    correct = "90°"
    opts, letter = _string_opts(correct, ["180°", "45°", "They are equal"])
    q = r"A tangent and radius at the point of contact meet at:"
    sol = rf"Tangent ⊥ radius → <strong>90°</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Tangent meets radius at right angles.", 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# COMPOUND MEASURES
# ══════════════════════════════════════════════════════════════════════════════

def _cm_proc_speed():
    d, t = random.choice([60, 90, 120]), random.choice([2, 3, 4])
    correct = d // t
    opts, letter = _letter_opts(correct, [d * t, d + t, d - t])
    q = rf"Distance <strong>{d} km</strong> in <strong>{t} hours</strong>. Average speed ="
    sol = rf"Speed = distance ÷ time = <strong>{correct} km/h</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Speed = distance / time.", 2, opts, letter


def _cm_proc_density():
    m, v = random.randint(20, 80), random.randint(4, 10)
    correct = m // v if m % v == 0 else round(m / v, 1)
    opts, letter = _letter_opts(correct, [m * v, v / m, m - v], fmt=str)
    q = rf"Mass <strong>{m} g</strong>, volume <strong>{v} cm³</strong>. Density ="
    sol = rf"\(\rho = m/V\) = <strong>{correct} g/cm³</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Density = mass ÷ volume.", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# SIMILARITY & CONGRUENCE
# ══════════════════════════════════════════════════════════════════════════════

def _sc_proc_scale_factor():
    k = random.randint(2, 5)
    side = random.randint(3, 8)
    correct = side * k
    opts, letter = _letter_opts(correct, [side + k, side * k * k, side // k if side >= k else side])
    q = rf"Two shapes are similar with scale factor <strong>{k}</strong>. A side of length <strong>{side} cm</strong> maps to:"
    sol = rf"Multiply by {k}: <strong>{correct} cm</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Corresponding lengths scale by k.", 2, opts, letter


def _sc_proc_area_factor():
    k = random.randint(2, 4)
    area = random.randint(5, 20)
    correct = area * k * k
    opts, letter = _letter_opts(correct, [area * k, area + k * k, area * 2])
    q = rf"Linear scale factor <strong>{k}</strong>. A small shape has area <strong>{area} cm²</strong>. The large area is:"
    sol = rf"Area factor = \(k^2 = {k*k}\): <strong>{correct} cm²</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Areas scale by k².", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# CONSTRUCTIONS & LOCI
# ══════════════════════════════════════════════════════════════════════════════

def _cl_proc_perp_bisector():
    correct = "Points equidistant from A and B"
    opts, letter = _string_opts(correct, [
        "Points 2 cm from A only",
        "Points on a circle centre A",
        "The midpoint of AB only",
    ])
    q = r"The perpendicular bisector of AB is the locus of:"
    sol = rf"Equidistant from A and B. Answer: <strong>{letter}</strong>"
    return q, sol, "Perp bisector = equal distance from endpoints.", 2, opts, letter


def _cl_proc_angle_bisector():
    correct = "Points equidistant from the two lines"
    opts, letter = _string_opts(correct, [
        "Points on the angle only",
        "The midpoint of the angle arc",
        "Points parallel to both lines",
    ])
    q = r"An angle bisector construction gives the locus of:"
    sol = rf"Equal perpendicular distance from both arms. Answer: <strong>{letter}</strong>"
    return q, sol, "Angle bisector = equidistant from both sides.", 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# PYTHAGORAS
# ══════════════════════════════════════════════════════════════════════════════

def _py_proc_hypotenuse():
    a, b = random.choice([3, 6, 8]), random.choice([4, 8, 15])
    c = int(math.sqrt(a * a + b * b))
    correct = c
    opts, letter = _letter_opts(correct, [a + b, abs(a - b), c + 1])
    q = rf"A right triangle has shorter sides <strong>{a}</strong> and <strong>{b}</strong>. The hypotenuse is:"
    sol = rf"\(\sqrt{{{a}^2+{b}^2}} = {c}\). Answer: <strong>{letter}</strong>"
    return q, sol, "c² = a² + b².", 2, opts, letter


def _py_proc_short_side():
    c, a = random.choice([13, 17, 25]), random.choice([5, 8, 12])
    b = int(math.sqrt(c * c - a * a))
    correct = b
    opts, letter = _letter_opts(correct, [c - a, c + a, c // a if c >= a else a])
    q = rf"Hypotenuse <strong>{c}</strong>, one side <strong>{a}</strong>. The other shorter side is:"
    sol = rf"\(\sqrt{{{c}^2-{a}^2}} = {b}\). Answer: <strong>{letter}</strong>"
    return q, sol, "Rearrange a² = c² − b².", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# VECTORS
# ══════════════════════════════════════════════════════════════════════════════

def _vec_proc_add():
    ax, ay = random.randint(1, 5), random.randint(-4, 4)
    bx, by = random.randint(1, 5), random.randint(-4, 4)
    correct = f"({ax + bx}, {ay + by})"
    opts, letter = _string_opts(correct, [
        f"({ax - bx}, {ay - by})",
        f"({bx}, {by})",
        f"({ax}, {ay + by})",
        f"({ax + bx}, {ay})",
    ])
    q = rf"\(\mathbf{{a}} = \begin{{pmatrix}} {ax} \\ {ay} \end{{pmatrix}}\), \(\mathbf{{b}} = \begin{{pmatrix}} {bx} \\ {by} \end{{pmatrix}}\). Find \(\mathbf{{a}} + \mathbf{{b}}\)."
    sol = (
        rf"Add tops: {ax}+{bx}={ax+bx}. Add bottoms: {ay}+{by}={ay+by}. "
        rf"<strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Add x-components together, then y-components — do not mix them.", 2, opts, letter


def _vec_proc_magnitude():
    x, y = random.choice([3, 6, 8]), random.choice([4, 8, 15])
    mag = int(math.sqrt(x * x + y * y))
    correct = mag
    opts, letter = _letter_opts(correct, [x + y, x * y, mag + 1])
    q = rf"Find the magnitude of \(\begin{{pmatrix}} {x} \\ {y} \end{{pmatrix}}\)."
    sol = (
        rf"√({x}²+{y}²) = √({x*x}+{y*y}) = √{x*x+y*y} = <strong>{mag}</strong>. "
        rf"Answer: <strong>{letter}</strong>"
    )
    return q, sol, "Square each component, add, then square-root (Pythagoras).", 3, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# TRIGONOMETRY
# ══════════════════════════════════════════════════════════════════════════════

def _trig_proc_find_side():
    angle = random.choice([30, 45, 60])
    adj = random.choice([5, 8, 10])
    if angle == 30:
        opp = round(adj * math.tan(math.radians(30)), 1)
    elif angle == 45:
        opp = adj
    else:
        opp = round(adj * math.tan(math.radians(60)), 1)
    correct = opp
    opts, letter = _letter_opts(correct, [adj, adj / 2, opp + 2], fmt=lambda x: f"{x:.1f}" if isinstance(x, float) else str(x))
    q = rf"In a right triangle, angle <strong>{angle}°</strong>, adjacent <strong>{adj}</strong>. Opposite = (tan {angle}°):"
    sol = rf"tan = opp/adj → <strong>{opp}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Choose the correct ratio (SOHCAHTOA).", 3, opts, letter


def _trig_proc_exact():
    angle = random.choice([30, 45, 60])
    exact = {30: "1/2", 45: "√2/2", 60: "√3/2"}[angle]
    correct = f"sin {angle}° = {exact}"
    opts, letter = _string_opts(correct, [
        f"cos {angle}° = {exact}",
        f"sin {angle}° = {angle}/180",
        f"sin {angle}° = √3",
        f"tan {angle}° = {exact}",
    ])
    q = rf"Which exact value is correct?"
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{letter}</strong>"
    return q, sol, "Learn the exact trig table.", 2, opts, letter


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

_PROCEDURAL = {
    "simultaneous_equations": [_sim_proc_elimination, _sim_proc_substitution],
    "equations_inequalities": [_eq_proc_quadratic_roots, _eq_proc_inequality_flip],
    "bidmas": [_bidmas_proc_nested, _bidmas_proc_brackets_power],
    "fdp": [
        _fdp_proc_reverse_percent, _fdp_proc_fraction_of,
        _fdp_proc_percent_change, _fdp_proc_decimal_to_percent,
    ],
    "multiples_factors": [_mf_proc_hcf, _mf_proc_lcm, _mf_proc_prime_factors, _mf_proc_factor_of],
    "decimals": [_dec_proc_bounds, _dec_proc_divide, _dec_proc_multiply, _dec_proc_round],
    "algebra": [_alg_proc_expand, _alg_proc_factorise_quad],
    "surds": [
        _surd_proc_simplify, _surd_proc_rationalise, _surd_proc_multiply,
        _surd_proc_add_like, _surd_proc_between_integers,
    ],
    "sequences": [_seq_proc_nth_linear, _seq_proc_quadratic_diff],
    "geometry_angles": [_geom_proc_parallel, _geom_proc_polygon],
    "transformations": [_trans_proc_translation, _trans_proc_reflection],
    "mensuration": [_mens_proc_circle, _mens_proc_trapezium],
    "bearings": [_brg_proc_back_bearing, _brg_proc_three_figure],
    "circle_theorems": [_ct_proc_semicircle, _ct_proc_tangent_radius],
    "compound_measures": [_cm_proc_speed, _cm_proc_density],
    "similarity_congruence": [_sc_proc_scale_factor, _sc_proc_area_factor],
    "constructions_loci": [_cl_proc_perp_bisector, _cl_proc_angle_bisector],
    "pythagoras": [_py_proc_hypotenuse, _py_proc_short_side],
    "vectors": [_vec_proc_add, _vec_proc_magnitude],
    "trigonometry": [_trig_proc_find_side, _trig_proc_exact],
}
