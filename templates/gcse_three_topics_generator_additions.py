# ------------------------------------------------------------
# GCSE Maths – Ratio/Proportion, Probability, Statistics
# Add this section to generators/gcse/maths.py
# Requires existing imports: random, math, make_problem
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
    for d in distractors:
        d = str(d)
        if d not in choices:
            choices.append(d)
    while len(choices) < 4:
        choices.append(f"{correct} ({len(choices)})")
    choices = choices[:4]
    random.shuffle(choices)
    letters = ['A', 'B', 'C', 'D']
    return [f"{letters[i]}  {choices[i]}" for i in range(4)], letters[choices.index(correct)]

# ============================================================
# RATIO AND PROPORTION
# ============================================================


def _ratio_simplify():
    a, b = random.randint(2, 12), random.randint(2, 12)
    k = random.randint(2, 9)
    x, y = a * k, b * k
    g = math.gcd(x, y)
    q = rf"Simplify the ratio {x}:{y}."
    s = rf"Divide both parts by the highest common factor, {g}: {x} ÷ {g} = {x//g} and {y} ÷ {g} = {y//g}. Answer: <strong>{x//g}:{y//g}</strong>."
    return q, s, "Divide every part by the same highest common factor.", 1


def _ratio_equivalent():
    a, b, k = random.randint(2, 8), random.randint(2, 9), random.randint(2, 7)
    q = rf"Write an equivalent ratio to {a}:{b} by multiplying each part by {k}."
    s = rf"Multiply both parts by {k}: {a}×{k} = {a*k} and {b}×{k} = {b*k}. Answer: <strong>{a*k}:{b*k}</strong>."
    return q, s, "Equivalent ratios are made by multiplying each part by the same number.", 1


def _ratio_share_two():
    a, b = random.randint(2, 7), random.randint(2, 7)
    unit = random.randint(5, 30)
    total = (a + b) * unit
    q = rf"Share £{total} in the ratio {a}:{b}."
    s = rf"Total parts = {a}+{b} = {a+b}. One part = {total} ÷ {a+b} = {unit}. Shares are {a}×{unit} = <strong>£{a*unit}</strong> and {b}×{unit} = <strong>£{b*unit}</strong>."
    return q, s, "Add the parts first, then find one part.", 3


def _ratio_share_three():
    a, b, c = random.randint(1, 5), random.randint(2, 6), random.randint(2, 7)
    unit = random.randint(4, 20)
    total = (a + b + c) * unit
    q = rf"Share {total} sweets in the ratio {a}:{b}:{c}."
    s = rf"Total parts = {a+b+c}. One part = {total} ÷ {a+b+c} = {unit}. The shares are <strong>{a*unit}, {b*unit}, {c*unit}</strong>."
    return q, s, "For a three-part ratio, add all three parts before dividing.", 3


def _ratio_fraction_of_total():
    a, b = random.randint(2, 8), random.randint(2, 8)
    total = (a + b) * random.randint(6, 20)
    q = rf"The ratio of boys to girls is {a}:{b}. There are {total} students altogether. How many are boys?"
    boys = total * a // (a+b)
    s = rf"There are {a+b} parts in total. Boys are \(\frac{{{a}}}{{{a+b}}}\) of the total, so boys = {a}/{a+b} × {total} = <strong>{boys}</strong>."
    return q, s, "Convert the ratio part into a fraction of the total.", 2


def _ratio_find_missing_part():
    a, b = random.randint(2, 8), random.randint(2, 9)
    known = a * random.randint(4, 15)
    multiplier = known // a
    missing = b * multiplier
    q = rf"The ratio A:B is {a}:{b}. If A = {known}, find B."
    s = rf"A has been multiplied by {multiplier}, because {a}×{multiplier} = {known}. Therefore B = {b}×{multiplier} = <strong>{missing}</strong>."
    return q, s, "Find the scale factor from the known part, then apply it to the other part.", 2


def _ratio_unitary_cost():
    items = random.randint(3, 9)
    cost_each = random.choice([1.2, 1.5, 2.25, 3.4, 4.75])
    new_items = random.randint(5, 15)
    total = items * cost_each
    ans = new_items * cost_each
    q = rf"{items} notebooks cost £{total:.2f}. How much do {new_items} notebooks cost?"
    s = rf"One notebook costs £{total:.2f} ÷ {items} = £{cost_each:.2f}. Therefore {new_items} notebooks cost {new_items}×£{cost_each:.2f} = <strong>£{ans:.2f}</strong>."
    return q, s, "Find the cost of one item first.", 2


def _ratio_recipe_scale():
    people1 = random.choice([2, 4, 5, 6])
    people2 = random.choice([8, 10, 12, 15])
    ingredient = random.choice([120, 150, 200, 250, 300])
    ans = ingredient * people2 / people1
    q = rf"A recipe uses {ingredient} g of flour for {people1} people. How much flour is needed for {people2} people?"
    s = rf"Scale factor = {people2} ÷ {people1} = {_fmt_num(people2/people1)}. Flour needed = {ingredient} × {_fmt_num(people2/people1)} = <strong>{_fmt_num(ans)} g</strong>."
    return q, s, "Multiply by the same scale factor as the number of people.", 2


def _ratio_best_buy():
    a_items, b_items = random.randint(3, 8), random.randint(4, 10)
    a_price, b_price = round(random.uniform(1.5, 6.5), 2), round(random.uniform(2.0, 8.0), 2)
    a_unit, b_unit = a_price/a_items, b_price/b_items
    best = "A" if a_unit < b_unit else "B"
    q = rf"Pack A has {a_items} items for £{a_price:.2f}. Pack B has {b_items} items for £{b_price:.2f}. Which is better value?"
    s = rf"Pack A: £{a_price:.2f} ÷ {a_items} = £{a_unit:.2f} per item. Pack B: £{b_price:.2f} ÷ {b_items} = £{b_unit:.2f} per item. Better value: <strong>Pack {best}</strong>."
    return q, s, "Compare the price for one item.", 3


def _ratio_scale_map():
    scale = random.choice([5000, 10000, 25000, 50000])
    cm = random.randint(3, 12)
    real_m = cm * scale / 100
    q = rf"A map has scale 1:{scale}. A distance on the map is {cm} cm. Find the real distance in metres."
    s = rf"1 cm represents {scale} cm. Real distance = {cm}×{scale} = {cm*scale} cm = <strong>{_fmt_num(real_m)} m</strong>."
    return q, s, "Use the scale, then convert centimetres to metres.", 3


def _ratio_inverse_workers():
    workers1 = random.randint(3, 8)
    hours1 = random.randint(4, 12)
    workers2 = random.randint(2, 10)
    work = workers1 * hours1
    ans = work / workers2
    q = rf"{workers1} workers complete a job in {hours1} hours. Assuming the same rate, how long would {workers2} workers take?"
    s = rf"Total work = {workers1}×{hours1} = {work} worker-hours. Time for {workers2} workers = {work} ÷ {workers2} = <strong>{_fmt_num(ans)} hours</strong>."
    return q, s, "For inverse proportion, workers × time stays constant.", 3


def _ratio_direct_formula():
    k = random.randint(2, 8)
    x = random.randint(3, 12)
    q = rf"y is directly proportional to x. When x = {x}, y = {k*x}. Find y when x = {x+5}."
    s = rf"Since y = kx, k = {k*x} ÷ {x} = {k}. When x = {x+5}, y = {k}×{x+5} = <strong>{k*(x+5)}</strong>."
    return q, s, "Find the constant of proportionality first.", 3


def _ratio_inverse_formula():
    k = random.randint(24, 120)
    x1 = random.choice([3, 4, 5, 6, 8])
    y1 = k / x1
    x2 = random.choice([2, 3, 4, 5, 6, 8, 10])
    q = rf"y is inversely proportional to x. When x = {x1}, y = {_fmt_num(y1)}. Find y when x = {x2}."
    s = rf"For inverse proportion, y = k/x. k = xy = {x1}×{_fmt_num(y1)} = {k}. When x = {x2}, y = {k} ÷ {x2} = <strong>{_fmt_num(k/x2)}</strong>."
    return q, s, "For inverse proportion, multiply x and y to find k.", 3


def _ratio_convert_units():
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    q = rf"Simplify the ratio {a} m : {b*100} cm."
    left_cm = a * 100
    g = math.gcd(left_cm, b*100)
    s = rf"Convert to the same units: {a} m = {left_cm} cm. Ratio = {left_cm}:{b*100}. Divide by {g}: <strong>{left_cm//g}:{(b*100)//g}</strong>."
    return q, s, "Convert both quantities to the same unit before simplifying.", 2


def _ratio_density_style():
    mass = random.randint(40, 200)
    volume = random.randint(5, 40)
    q = rf"A substance has mass {mass} g and volume {volume} cm³. Find its density."
    s = rf"Density = mass ÷ volume = {mass} ÷ {volume} = <strong>{_fmt_num(mass/volume)} g/cm³</strong>."
    return q, s, "Density is mass divided by volume.", 2

# Ratio wrappers: 15 per difficulty

def _ratio_found_01(): return _ratio_simplify()
def _ratio_found_02(): return _ratio_equivalent()
def _ratio_found_03(): return _ratio_share_two()
def _ratio_found_04(): return _ratio_fraction_of_total()
def _ratio_found_05(): return _ratio_find_missing_part()
def _ratio_found_06(): return _ratio_unitary_cost()
def _ratio_found_07(): return _ratio_recipe_scale()
def _ratio_found_08(): return _ratio_convert_units()
def _ratio_found_09(): return _ratio_simplify()
def _ratio_found_10(): return _ratio_share_two()
def _ratio_found_11(): return _ratio_equivalent()
def _ratio_found_12(): return _ratio_fraction_of_total()
def _ratio_found_13(): return _ratio_unitary_cost()
def _ratio_found_14(): return _ratio_recipe_scale()
def _ratio_found_15(): return _ratio_find_missing_part()

def _ratio_inter_01(): return _ratio_share_three()
def _ratio_inter_02(): return _ratio_best_buy()
def _ratio_inter_03(): return _ratio_scale_map()
def _ratio_inter_04(): return _ratio_inverse_workers()
def _ratio_inter_05(): return _ratio_direct_formula()
def _ratio_inter_06(): return _ratio_convert_units()
def _ratio_inter_07(): return _ratio_density_style()
def _ratio_inter_08(): return _ratio_recipe_scale()
def _ratio_inter_09(): return _ratio_best_buy()
def _ratio_inter_10(): return _ratio_scale_map()
def _ratio_inter_11(): return _ratio_inverse_workers()
def _ratio_inter_12(): return _ratio_direct_formula()
def _ratio_inter_13(): return _ratio_share_three()
def _ratio_inter_14(): return _ratio_density_style()
def _ratio_inter_15(): return _ratio_find_missing_part()

def _ratio_diff_01(): return _ratio_inverse_formula()
def _ratio_diff_02(): return _ratio_direct_formula()
def _ratio_diff_03(): return _ratio_inverse_workers()
def _ratio_diff_04(): return _ratio_scale_map()
def _ratio_diff_05(): return _ratio_best_buy()
def _ratio_diff_06(): return _ratio_density_style()
def _ratio_diff_07(): return _ratio_inverse_formula()
def _ratio_diff_08(): return _ratio_direct_formula()
def _ratio_diff_09(): return _ratio_recipe_scale()
def _ratio_diff_10(): return _ratio_share_three()
def _ratio_diff_11(): return _ratio_convert_units()
def _ratio_diff_12(): return _ratio_inverse_workers()
def _ratio_diff_13(): return _ratio_scale_map()
def _ratio_diff_14(): return _ratio_best_buy()
def _ratio_diff_15(): return _ratio_inverse_formula()


def ratio_proportion_mcq():
    q, s, hint, marks = random.choice([_ratio_simplify, _ratio_share_two, _ratio_fraction_of_total, _ratio_unitary_cost, _ratio_recipe_scale, _ratio_convert_units])()
    if "<strong>" in s:
        correct = s.split("<strong>")[-1].split("</strong>")[0]
    else:
        correct = "See solution"
    options, letter = _mcq_options(correct, ["2:3", "3:2", "£24", "12"])
    return q, f"Answer: {letter}\n\n{hint}", hint, 1, options, letter


def gcse_ratio_proportion_variants(difficulty, mode):
    if mode == 'mcq': return [ratio_proportion_mcq] * 10
    found = [_ratio_found_01,_ratio_found_02,_ratio_found_03,_ratio_found_04,_ratio_found_05,_ratio_found_06,_ratio_found_07,_ratio_found_08,_ratio_found_09,_ratio_found_10,_ratio_found_11,_ratio_found_12,_ratio_found_13,_ratio_found_14,_ratio_found_15]
    inter = [_ratio_inter_01,_ratio_inter_02,_ratio_inter_03,_ratio_inter_04,_ratio_inter_05,_ratio_inter_06,_ratio_inter_07,_ratio_inter_08,_ratio_inter_09,_ratio_inter_10,_ratio_inter_11,_ratio_inter_12,_ratio_inter_13,_ratio_inter_14,_ratio_inter_15]
    diff = [_ratio_diff_01,_ratio_diff_02,_ratio_diff_03,_ratio_diff_04,_ratio_diff_05,_ratio_diff_06,_ratio_diff_07,_ratio_diff_08,_ratio_diff_09,_ratio_diff_10,_ratio_diff_11,_ratio_diff_12,_ratio_diff_13,_ratio_diff_14,_ratio_diff_15]
    pool = found if difficulty == 'foundational' else inter if difficulty == 'intermediate' else diff if difficulty == 'difficult' else random.sample(found,4)+random.sample(inter,4)+random.sample(diff,2)
    shuffled = random.sample(pool, len(pool))
    return (shuffled * (10 // len(shuffled) + 1))[:10]


def gcse_ratio_proportion(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = ratio_proportion_mcq()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'ratio_proportion', options=opts, correct_answer=correct)
    variants = gcse_ratio_proportion_variants(difficulty, mode)
    variant = random.choice(variants) if variant_name is None else {v.__name__: v for v in variants}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'ratio_proportion')

# ============================================================
# PROBABILITY
# ============================================================


def _prob_die():
    evens = [2,4,6]; target = random.choice(['even number','number greater than 4','factor of 6'])
    if target == 'even number': fav = 3
    elif target == 'number greater than 4': fav = 2
    else: fav = 4
    a,b = _simp_frac(fav,6)
    q = rf"A fair six-sided die is rolled. Find the probability of rolling a {target}."
    s = rf"There are {fav} favourable outcomes out of 6 equally likely outcomes. Probability = <strong>{a}/{b}</strong>."
    return q, s, "Probability = favourable outcomes ÷ total outcomes.", 1


def _prob_bag_single():
    red, blue = random.randint(2,8), random.randint(2,8)
    total = red + blue
    colour, count = random.choice([('red',red),('blue',blue)])
    a,b = _simp_frac(count,total)
    q = rf"A bag contains {red} red counters and {blue} blue counters. One counter is chosen at random. Find P({colour})."
    s = rf"There are {count} {colour} counters out of {total} counters, so P({colour}) = <strong>{a}/{b}</strong>."
    return q, s, "Put the number of wanted outcomes over the total number of outcomes.", 1


def _prob_complement():
    p = random.choice([0.12,0.25,0.37,0.6,0.72])
    q = rf"The probability that a train is late is {p}. Find the probability that it is not late."
    s = rf"Use the complement rule: 1 − {p} = <strong>{_fmt_num(1-p)}</strong>."
    return q, s, "The probabilities of an event and its complement add to 1.", 1


def _prob_expected_frequency():
    a,b = random.choice([(1,4),(2,5),(3,10),(3,8)])
    trials = b * random.randint(10,40)
    ans = trials * a // b
    q = rf"The probability of winning a game is {a}/{b}. In {trials} games, how many wins are expected?"
    s = rf"Expected frequency = probability × trials = {a}/{b} × {trials} = <strong>{ans}</strong>."
    return q, s, "Multiply probability by the number of trials.", 2


def _prob_relative_frequency():
    trials = random.randint(50,200)
    success = random.randint(10,trials-10)
    q = rf"In an experiment, an event happens {success} times in {trials} trials. Find the relative frequency."
    s = rf"Relative frequency = successes ÷ trials = {success}/{trials} = <strong>{_fmt_num(success/trials,3)}</strong>."
    return q, s, "Relative frequency is experimental probability.", 2


def _prob_mutually_exclusive():
    a,b = random.sample(range(1,7),2)
    q = rf"A fair die is rolled. Find the probability of rolling {a} or {b}."
    s = rf"The events are mutually exclusive. P({a} or {b}) = 1/6 + 1/6 = 2/6 = <strong>1/3</strong>."
    return q, s, "For mutually exclusive events, add the probabilities.", 2


def _prob_two_coins():
    q = "Two fair coins are flipped. Find the probability of getting exactly one head."
    s = "The equally likely outcomes are HH, HT, TH, TT. Exactly one head occurs in HT and TH, so probability = 2/4 = <strong>1/2</strong>."
    return q, s, "List all possible outcomes systematically.", 2


def _prob_tree_replacement():
    red, blue = random.randint(2,6), random.randint(2,6)
    total = red + blue
    q = rf"A bag has {red} red and {blue} blue counters. A counter is chosen, replaced, then another is chosen. Find P(two red)."
    a,b = _simp_frac(red*red,total*total)
    s = rf"With replacement, probabilities stay the same. P(two red) = {red}/{total} × {red}/{total} = <strong>{a}/{b}</strong>."
    return q, s, "Multiply along the branches of a tree diagram.", 3


def _prob_tree_no_replacement():
    red, blue = random.randint(3,7), random.randint(2,6)
    total = red + blue
    q = rf"A bag has {red} red and {blue} blue counters. Two counters are chosen without replacement. Find P(two red)."
    num, den = red*(red-1), total*(total-1)
    a,b = _simp_frac(num,den)
    s = rf"Without replacement, totals change. P(two red) = {red}/{total} × {red-1}/{total-1} = <strong>{a}/{b}</strong>."
    return q, s, "After the first counter is removed, reduce both the wanted count and the total.", 3


def _prob_at_least_one():
    p_not = random.choice([0.2,0.3,0.4,0.5])
    q = rf"The probability that one attempt fails is {p_not}. Two independent attempts are made. Find the probability of at least one success."
    ans = 1 - p_not*p_not
    s = rf"Use the complement. P(no successes) = {p_not}×{p_not} = {_fmt_num(p_not*p_not)}. Therefore P(at least one success) = 1 − {_fmt_num(p_not*p_not)} = <strong>{_fmt_num(ans)}</strong>."
    return q, s, "At least one is often easiest using 1 − probability of none.", 3


def _prob_conditional_simple():
    french, both = random.randint(20,40), random.randint(5,19)
    q = rf"In a year group, {french} students study French and {both} of these also study German. A French student is chosen. Find the probability they also study German."
    a,b = _simp_frac(both,french)
    s = rf"The condition is that the student studies French, so the denominator is {french}. Probability = {both}/{french} = <strong>{a}/{b}</strong>."
    return q, s, "The condition changes the denominator.", 3


def _prob_venn_total():
    a_only,b_only,both,neither = random.randint(5,20),random.randint(5,20),random.randint(3,12),random.randint(2,10)
    total = a_only+b_only+both+neither
    q = rf"In a Venn diagram, A only = {a_only}, B only = {b_only}, both = {both}, neither = {neither}. Find P(A)."
    num = a_only + both
    x,y = _simp_frac(num,total)
    s = rf"Set A includes A only and both: {a_only}+{both} = {num}. Total = {total}. P(A) = <strong>{x}/{y}</strong>."
    return q, s, "Include the overlap when finding the probability of a set.", 2


def _prob_sample_space():
    q = "A fair coin and a fair six-sided die are used. How many outcomes are in the sample space?"
    s = "There are 2 coin outcomes and 6 die outcomes, so total outcomes = 2×6 = <strong>12</strong>."
    return q, s, "Multiply the number of choices at each stage.", 1


def _prob_or_not_exclusive():
    total = random.randint(40,80); a = random.randint(15,30); b = random.randint(15,30); both = random.randint(5,14)
    q = rf"In a group of {total}, {a} like tennis, {b} like football, and {both} like both. Find the probability that a person likes tennis or football."
    num = a+b-both; x,y = _simp_frac(num,total)
    s = rf"For overlapping events, add then subtract the overlap: {a}+{b}-{both} = {num}. Probability = <strong>{x}/{y}</strong>."
    return q, s, "Do not count the overlap twice.", 3


def _prob_independent_product():
    a,b = random.choice([(1,2),(1,3),(2,5),(3,4)])
    c,d = random.choice([(1,2),(2,3),(3,5),(4,5)])
    x,y = _simp_frac(a*c,b*d)
    q = rf"Two independent events have probabilities {a}/{b} and {c}/{d}. Find the probability that both happen."
    s = rf"For independent events, multiply: {a}/{b} × {c}/{d} = <strong>{x}/{y}</strong>."
    return q, s, "Independent events are multiplied for 'and'.", 2

# Probability wrappers

def _prob_found_01(): return _prob_die()
def _prob_found_02(): return _prob_bag_single()
def _prob_found_03(): return _prob_complement()
def _prob_found_04(): return _prob_expected_frequency()
def _prob_found_05(): return _prob_relative_frequency()
def _prob_found_06(): return _prob_mutually_exclusive()
def _prob_found_07(): return _prob_sample_space()
def _prob_found_08(): return _prob_die()
def _prob_found_09(): return _prob_bag_single()
def _prob_found_10(): return _prob_complement()
def _prob_found_11(): return _prob_expected_frequency()
def _prob_found_12(): return _prob_relative_frequency()
def _prob_found_13(): return _prob_mutually_exclusive()
def _prob_found_14(): return _prob_sample_space()
def _prob_found_15(): return _prob_two_coins()

def _prob_inter_01(): return _prob_two_coins()
def _prob_inter_02(): return _prob_tree_replacement()
def _prob_inter_03(): return _prob_tree_no_replacement()
def _prob_inter_04(): return _prob_venn_total()
def _prob_inter_05(): return _prob_independent_product()
def _prob_inter_06(): return _prob_or_not_exclusive()
def _prob_inter_07(): return _prob_expected_frequency()
def _prob_inter_08(): return _prob_relative_frequency()
def _prob_inter_09(): return _prob_tree_replacement()
def _prob_inter_10(): return _prob_tree_no_replacement()
def _prob_inter_11(): return _prob_venn_total()
def _prob_inter_12(): return _prob_independent_product()
def _prob_inter_13(): return _prob_or_not_exclusive()
def _prob_inter_14(): return _prob_at_least_one()
def _prob_inter_15(): return _prob_conditional_simple()

def _prob_diff_01(): return _prob_at_least_one()
def _prob_diff_02(): return _prob_conditional_simple()
def _prob_diff_03(): return _prob_or_not_exclusive()
def _prob_diff_04(): return _prob_tree_no_replacement()
def _prob_diff_05(): return _prob_tree_replacement()
def _prob_diff_06(): return _prob_independent_product()
def _prob_diff_07(): return _prob_venn_total()
def _prob_diff_08(): return _prob_at_least_one()
def _prob_diff_09(): return _prob_conditional_simple()
def _prob_diff_10(): return _prob_or_not_exclusive()
def _prob_diff_11(): return _prob_tree_no_replacement()
def _prob_diff_12(): return _prob_independent_product()
def _prob_diff_13(): return _prob_venn_total()
def _prob_diff_14(): return _prob_tree_replacement()
def _prob_diff_15(): return _prob_conditional_simple()


def probability_mcq():
    q, s, hint, marks = random.choice([_prob_die,_prob_bag_single,_prob_complement,_prob_expected_frequency,_prob_two_coins,_prob_sample_space])()
    correct = s.split("<strong>")[-1].split("</strong>")[0]
    options, letter = _mcq_options(correct, ["1/2", "1/3", "0.25", "12"])
    return q, f"Answer: {letter}\n\n{hint}", hint, 1, options, letter


def gcse_probability_variants(difficulty, mode):
    if mode == 'mcq': return [probability_mcq] * 10
    found = [_prob_found_01,_prob_found_02,_prob_found_03,_prob_found_04,_prob_found_05,_prob_found_06,_prob_found_07,_prob_found_08,_prob_found_09,_prob_found_10,_prob_found_11,_prob_found_12,_prob_found_13,_prob_found_14,_prob_found_15]
    inter = [_prob_inter_01,_prob_inter_02,_prob_inter_03,_prob_inter_04,_prob_inter_05,_prob_inter_06,_prob_inter_07,_prob_inter_08,_prob_inter_09,_prob_inter_10,_prob_inter_11,_prob_inter_12,_prob_inter_13,_prob_inter_14,_prob_inter_15]
    diff = [_prob_diff_01,_prob_diff_02,_prob_diff_03,_prob_diff_04,_prob_diff_05,_prob_diff_06,_prob_diff_07,_prob_diff_08,_prob_diff_09,_prob_diff_10,_prob_diff_11,_prob_diff_12,_prob_diff_13,_prob_diff_14,_prob_diff_15]
    pool = found if difficulty == 'foundational' else inter if difficulty == 'intermediate' else diff if difficulty == 'difficult' else random.sample(found,4)+random.sample(inter,4)+random.sample(diff,2)
    shuffled = random.sample(pool, len(pool))
    return (shuffled * (10 // len(shuffled) + 1))[:10]


def gcse_probability(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = probability_mcq()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'probability', options=opts, correct_answer=correct)
    variants = gcse_probability_variants(difficulty, mode)
    variant = random.choice(variants) if variant_name is None else {v.__name__: v for v in variants}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'probability')

# ============================================================
# STATISTICS
# ============================================================


def _stats_mean_list():
    vals = [random.randint(2,20) for _ in range(5)]
    q = rf"Find the mean of: {', '.join(map(str, vals))}."
    s = rf"Mean = total ÷ number of values = {sum(vals)} ÷ {len(vals)} = <strong>{_fmt_num(sum(vals)/len(vals))}</strong>."
    return q, s, "Add the values and divide by how many values there are.", 2


def _stats_median_list():
    vals = [random.randint(1,30) for _ in range(7)]
    ordered = sorted(vals); med = ordered[len(vals)//2]
    q = rf"Find the median of: {', '.join(map(str, vals))}."
    s = rf"Put the values in order: {', '.join(map(str, ordered))}. The middle value is <strong>{med}</strong>."
    return q, s, "Put the values in order first.", 2


def _stats_mode_list():
    mode = random.randint(2,9); vals = [mode,mode] + [random.randint(1,12) for _ in range(5)]
    random.shuffle(vals)
    q = rf"Find the mode of: {', '.join(map(str, vals))}."
    s = rf"The mode is the value that occurs most often. Here, <strong>{mode}</strong> occurs most often."
    return q, s, "The mode is the most frequent value.", 1


def _stats_range_list():
    vals = [random.randint(5,50) for _ in range(6)]
    q = rf"Find the range of: {', '.join(map(str, vals))}."
    s = rf"Range = highest − lowest = {max(vals)} − {min(vals)} = <strong>{max(vals)-min(vals)}</strong>."
    return q, s, "Range measures spread: highest minus lowest.", 1


def _stats_freq_mean():
    values = [1,2,3,4]
    freqs = [random.randint(2,10) for _ in values]
    total_f = sum(freqs); total_fx = sum(v*f for v,f in zip(values,freqs))
    q = rf"A frequency table has values 1, 2, 3, 4 with frequencies {freqs[0]}, {freqs[1]}, {freqs[2]}, {freqs[3]}. Find the mean."
    s = rf"Calculate \(\sum fx\): {total_fx}. Total frequency = {total_f}. Mean = {total_fx} ÷ {total_f} = <strong>{_fmt_num(total_fx/total_f)}</strong>."
    return q, s, "Use mean = Σfx ÷ Σf.", 3


def _stats_grouped_midpoint():
    low = random.choice([0,10,20,30])
    high = low + random.choice([10,20])
    q = rf"Find the midpoint of the class interval {low} &lt; x ≤ {high}."
    s = rf"Midpoint = ({low}+{high}) ÷ 2 = <strong>{(low+high)/2:.0f}</strong>."
    return q, s, "Add the class boundaries and divide by 2.", 1


def _stats_estimated_mean_grouped():
    intervals = [(0,10),(10,20),(20,30)]
    freqs = [random.randint(2,10) for _ in intervals]
    mids = [(a+b)/2 for a,b in intervals]
    total_fx = sum(m*f for m,f in zip(mids,freqs)); total_f=sum(freqs)
    q = rf"Grouped data has intervals 0-10, 10-20, 20-30 with frequencies {freqs[0]}, {freqs[1]}, {freqs[2]}. Estimate the mean."
    s = rf"Use midpoints 5, 15, 25. \(\sum fx\) = {total_fx:.0f}, \(\sum f\) = {total_f}. Estimated mean = <strong>{_fmt_num(total_fx/total_f)}</strong>."
    return q, s, "Use class midpoints because exact values are unknown.", 4


def _stats_pie_angle():
    total = random.choice([60,80,100,120])
    freq = random.randint(10,total-10)
    angle = 360 * freq / total
    q = rf"In a pie chart, a category has frequency {freq} out of {total}. Find its sector angle."
    s = rf"Sector angle = frequency/total × 360 = {freq}/{total} × 360 = <strong>{_fmt_num(angle)}°</strong>."
    return q, s, "A full pie chart is 360°.", 2


def _stats_bar_read():
    a,b,c = random.randint(5,25), random.randint(5,25), random.randint(5,25)
    q = rf"A bar chart shows category A = {a}, B = {b}, C = {c}. How many items are there altogether?"
    s = rf"Add the frequencies: {a}+{b}+{c} = <strong>{a+b+c}</strong>."
    return q, s, "Total frequency is the sum of the bar heights.", 1


def _stats_scatter_correlation():
    corr = random.choice(['positive','negative','no'])
    if corr == 'positive': desc = 'as x increases, y tends to increase'
    elif corr == 'negative': desc = 'as x increases, y tends to decrease'
    else: desc = 'there is no clear pattern'
    q = rf"A scatter graph shows that {desc}. What type of correlation is shown?"
    s = rf"This is <strong>{corr} correlation</strong>."
    return q, s, "Look for the overall direction of the points.", 1


def _stats_line_best_fit():
    x1,y1 = 2, random.randint(5,10)
    gradient = random.randint(2,5)
    x2 = random.randint(5,10); y2 = y1 + gradient*(x2-x1)
    xq = random.randint(3,9); yq = y1 + gradient*(xq-x1)
    q = rf"A line of best fit passes through ({x1}, {y1}) and ({x2}, {y2}). Estimate y when x = {xq}."
    s = rf"Gradient = ({y2}-{y1})/({x2}-{x1}) = {gradient}. Using the line pattern, when x = {xq}, y ≈ <strong>{yq}</strong>."
    return q, s, "Use the line of best fit to interpolate within the data range.", 3


def _stats_cumulative_frequency():
    freqs = [random.randint(3,12) for _ in range(4)]
    upto = random.randint(1,3)
    q = rf"Frequencies are {freqs}. Find the cumulative frequency after the first {upto+1} groups."
    s = rf"Add the frequencies up to that group: {'+'.join(map(str,freqs[:upto+1]))} = <strong>{sum(freqs[:upto+1])}</strong>."
    return q, s, "Cumulative frequency is a running total.", 2


def _stats_box_iqr():
    q1 = random.randint(10,30); q3 = q1 + random.randint(10,30)
    q = rf"A box plot has lower quartile {q1} and upper quartile {q3}. Find the interquartile range."
    s = rf"IQR = upper quartile − lower quartile = {q3} − {q1} = <strong>{q3-q1}</strong>."
    return q, s, "The interquartile range is Q3 − Q1.", 1


def _stats_hist_density():
    width = random.choice([5,10,20]); freq = width * random.randint(2,8)
    q = rf"A histogram class has frequency {freq} and class width {width}. Find the frequency density."
    s = rf"Frequency density = frequency ÷ class width = {freq} ÷ {width} = <strong>{freq//width}</strong>."
    return q, s, "Histogram bar height is frequency density.", 2


def _stats_compare_distributions():
    med1, med2 = random.randint(20,50), random.randint(20,50)
    iqr1, iqr2 = random.randint(5,20), random.randint(5,20)
    q = rf"Class A has median {med1} and IQR {iqr1}. Class B has median {med2} and IQR {iqr2}. Which class has the greater typical value and which is more consistent?"
    typical = 'A' if med1 > med2 else 'B'
    consistent = 'A' if iqr1 < iqr2 else 'B'
    s = rf"Greater typical value means higher median: <strong>Class {typical}</strong>. More consistent means smaller IQR: <strong>Class {consistent}</strong>."
    return q, s, "Compare medians for typical value and IQRs for consistency.", 2

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
def _stats_inter_09(): return _stats_freq_mean()
def _stats_inter_10(): return _stats_estimated_mean_grouped()
def _stats_inter_11(): return _stats_line_best_fit()
def _stats_inter_12(): return _stats_cumulative_frequency()
def _stats_inter_13(): return _stats_box_iqr()
def _stats_inter_14(): return _stats_hist_density()
def _stats_inter_15(): return _stats_compare_distributions()

def _stats_diff_01(): return _stats_estimated_mean_grouped()
def _stats_diff_02(): return _stats_hist_density()
def _stats_diff_03(): return _stats_compare_distributions()
def _stats_diff_04(): return _stats_line_best_fit()
def _stats_diff_05(): return _stats_cumulative_frequency()
def _stats_diff_06(): return _stats_freq_mean()
def _stats_diff_07(): return _stats_pie_angle()
def _stats_diff_08(): return _stats_box_iqr()
def _stats_diff_09(): return _stats_hist_density()
def _stats_diff_10(): return _stats_compare_distributions()
def _stats_diff_11(): return _stats_estimated_mean_grouped()
def _stats_diff_12(): return _stats_line_best_fit()
def _stats_diff_13(): return _stats_cumulative_frequency()
def _stats_diff_14(): return _stats_freq_mean()
def _stats_diff_15(): return _stats_hist_density()


def statistics_mcq():
    q, s, hint, marks = random.choice([_stats_mean_list,_stats_median_list,_stats_mode_list,_stats_range_list,_stats_grouped_midpoint,_stats_hist_density])()
    correct = s.split("<strong>")[-1].split("</strong>")[0]
    options, letter = _mcq_options(correct, ["mean", "median", "10", "5"])
    return q, f"Answer: {letter}\n\n{hint}", hint, 1, options, letter


def gcse_statistics_variants(difficulty, mode):
    if mode == 'mcq': return [statistics_mcq] * 10
    found = [_stats_found_01,_stats_found_02,_stats_found_03,_stats_found_04,_stats_found_05,_stats_found_06,_stats_found_07,_stats_found_08,_stats_found_09,_stats_found_10,_stats_found_11,_stats_found_12,_stats_found_13,_stats_found_14,_stats_found_15]
    inter = [_stats_inter_01,_stats_inter_02,_stats_inter_03,_stats_inter_04,_stats_inter_05,_stats_inter_06,_stats_inter_07,_stats_inter_08,_stats_inter_09,_stats_inter_10,_stats_inter_11,_stats_inter_12,_stats_inter_13,_stats_inter_14,_stats_inter_15]
    diff = [_stats_diff_01,_stats_diff_02,_stats_diff_03,_stats_diff_04,_stats_diff_05,_stats_diff_06,_stats_diff_07,_stats_diff_08,_stats_diff_09,_stats_diff_10,_stats_diff_11,_stats_diff_12,_stats_diff_13,_stats_diff_14,_stats_diff_15]
    pool = found if difficulty == 'foundational' else inter if difficulty == 'intermediate' else diff if difficulty == 'difficult' else random.sample(found,4)+random.sample(inter,4)+random.sample(diff,2)
    shuffled = random.sample(pool, len(pool))
    return (shuffled * (10 // len(shuffled) + 1))[:10]


def gcse_statistics(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = statistics_mcq()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'statistics', options=opts, correct_answer=correct)
    variants = gcse_statistics_variants(difficulty, mode)
    variant = random.choice(variants) if variant_name is None else {v.__name__: v for v in variants}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'statistics')
