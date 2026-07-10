# ------------------------------------------------------------
# GCSE Maths Batch 2 – Equations/Inequalities, Sequences,
# Transformations
# Add this section to generators/gcse/maths.py
# Requires existing imports: random, math, make_problem
# ------------------------------------------------------------


def _b2_fmt(x, dp=2):
    if isinstance(x, int) or abs(x - int(x)) < 1e-10:
        return str(int(x))
    return f"{x:.{dp}f}".rstrip('0').rstrip('.')


def _b2_options(correct, distractors):
    correct = str(correct)
    choices = [correct]
    for d in distractors:
        d = str(d)
        if d not in choices:
            choices.append(d)
    filler = 1
    while len(choices) < 4:
        candidate = str(filler)
        if candidate not in choices:
            choices.append(candidate)
        filler += 1
    choices = choices[:4]
    random.shuffle(choices)
    letters = ['A', 'B', 'C', 'D']
    return [f"{letters[i]}  {choices[i]}" for i in range(4)], letters[choices.index(correct)]


def _b2_extract_answer(solution):
    if '<strong>' in solution:
        return solution.split('<strong>')[-1].split('</strong>')[0]
    return 'See solution'


def _b2_make_variant(name, func):
    def variant():
        return func()
    variant.__name__ = name
    variant.__qualname__ = name
    globals()[name] = variant
    return variant

# ============================================================
# EQUATIONS AND INEQUALITIES
# ============================================================


def _eq_one_step_add():
    x = random.randint(-8, 12); a = random.randint(2, 15); b = x + a
    q = rf"Solve x + {a} = {b}."
    s = rf"Subtract {a} from both sides: x = {b} − {a} = <strong>{x}</strong>."
    return q, s, "Use the inverse operation.", 1


def _eq_one_step_multiply():
    x = random.randint(2, 12); a = random.randint(2, 9); b = a*x
    q = rf"Solve {a}x = {b}."
    s = rf"Divide both sides by {a}: x = {b} ÷ {a} = <strong>{x}</strong>."
    return q, s, "Undo multiplication by dividing.", 1


def _eq_two_step():
    x = random.randint(-5, 10); a = random.randint(2, 8); c = random.randint(-9, 9); b = a*x + c
    q = rf"Solve {a}x + {c} = {b}."
    s = rf"Subtract {c}: {a}x = {b-c}. Then divide by {a}: x = <strong>{x}</strong>."
    return q, s, "Undo addition/subtraction before multiplication/division.", 2


def _eq_bracket_simple():
    x = random.randint(1, 10); a = random.randint(2, 6); c = random.randint(1, 8); b = a*(x+c)
    q = rf"Solve {a}(x + {c}) = {b}."
    s = rf"Divide by {a}: x + {c} = {b//a}. Then subtract {c}: x = <strong>{x}</strong>."
    return q, s, "You can divide before expanding if the bracket is multiplied only once.", 2


def _eq_unknowns_both_sides():
    x = random.randint(2, 12); a = random.randint(4, 9); b = random.randint(1, 4); c = random.randint(-5, 8); d = a*x + c - b*x
    q = rf"Solve {a}x + {c} = {b}x + {d}."
    s = rf"Collect x terms: {a-b}x = {d-c}. Then x = ({d-c}) ÷ {a-b} = <strong>{x}</strong>."
    return q, s, "Move x terms to one side and numbers to the other.", 2


def _eq_fraction_equation():
    x = random.randint(2, 12); a = random.randint(2, 6); b = random.randint(1, 8); rhs = x + b
    q = rf"Solve x/{a} + {b} = {rhs}."
    s = rf"Subtract {b}: x/{a} = {rhs-b}. Multiply by {a}: x = <strong>{x*a}</strong>."
    return q, s, "Clear the fraction by multiplying.", 2


def _eq_substitution_formula():
    x = random.randint(2, 8); y = random.randint(1, 7)
    ans = 3*x + 2*y
    q = rf"Calculate P = 3x + 2y when x = {x} and y = {y}."
    s = rf"Substitute: P = 3({x}) + 2({y}) = {3*x} + {2*y} = <strong>{ans}</strong>."
    return q, s, "Substitute each value into the formula.", 1


def _eq_rearrange_add():
    q = "Make x the subject of y = x + 7."
    s = "Subtract 7 from both sides: <strong>x = y − 7</strong>."
    return q, s, "Undo the +7.", 1


def _eq_rearrange_multiply():
    a = random.randint(2, 9)
    q = rf"Make x the subject of y = {a}x."
    s = rf"Divide both sides by {a}: <strong>x = y/{a}</strong>."
    return q, s, "Undo multiplication by dividing.", 1


def _eq_rearrange_complex():
    a = random.randint(2, 7); b = random.randint(1, 9)
    q = rf"Make x the subject of y = {a}x + {b}."
    s = rf"Subtract {b}: y − {b} = {a}x. Divide by {a}: <strong>x = (y − {b})/{a}</strong>."
    return q, s, "Use inverse operations in reverse order.", 2


def _eq_linear_inequality():
    x = random.randint(2, 10); a = random.randint(2, 6); c = random.randint(-5, 5); rhs = a*x + c
    q = rf"Solve {a}x + {c} > {rhs}."
    s = rf"Subtract {c}: {a}x > {rhs-c}. Divide by {a}: <strong>x > {x}</strong>."
    return q, s, "Solve like an equation when dividing by a positive number.", 2


def _eq_negative_inequality():
    x = random.randint(2, 10); a = random.randint(2, 6); rhs = -a*x
    q = rf"Solve -{a}x < {rhs}."
    s = rf"Divide by -{a} and reverse the sign: <strong>x > {x}</strong>."
    return q, s, "Reverse the inequality when multiplying or dividing by a negative.", 2


def _eq_quadratic_factorise():
    r1, r2 = random.sample(range(1, 8), 2)
    b = r1 + r2; c = r1*r2
    q = rf"Solve x² − {b}x + {c} = 0."
    s = rf"Factorise: (x − {r1})(x − {r2}) = 0. Therefore <strong>x = {r1} or x = {r2}</strong>."
    return q, s, "Find two numbers that multiply to the constant and add to the x coefficient.", 3


def _eq_simultaneous_elimination():
    x = random.randint(1, 8); y = random.randint(1, 8)
    a1, b1, a2, b2 = 2, 1, 1, -1
    c1 = a1*x + b1*y; c2 = a2*x + b2*y
    q = rf"Solve simultaneously: 2x + y = {c1} and x − y = {c2}."
    s = rf"Add the equations: 3x = {c1+c2}, so x = {x}. Substitute into x − y = {c2}: y = <strong>{y}</strong>. Therefore <strong>x = {x}, y = {y}</strong>."
    return q, s, "Eliminate one variable by adding or subtracting the equations.", 3


def _eq_form_expression():
    n = random.randint(2, 9); total = 3*n + 5
    q = rf"A number is multiplied by 3 and then 5 is added. The result is {total}. Form and solve an equation."
    s = rf"Let the number be n. 3n + 5 = {total}. Subtract 5: 3n = {total-5}. Divide by 3: <strong>n = {n}</strong>."
    return q, s, "Translate words into algebra first.", 2

# ============================================================
# SEQUENCES
# ============================================================


def _seq_next_terms_add():
    start = random.randint(1, 20); d = random.randint(2, 9)
    terms = [start + i*d for i in range(5)]
    q = rf"Find the next two terms: {terms[0]}, {terms[1]}, {terms[2]}, ..."
    s = rf"The sequence increases by {d}. The next two terms are <strong>{terms[3]}, {terms[4]}</strong>."
    return q, s, "Look for the common difference.", 1


def _seq_next_terms_subtract():
    start = random.randint(40, 80); d = random.randint(3, 12)
    terms = [start - i*d for i in range(5)]
    q = rf"Find the next two terms: {terms[0]}, {terms[1]}, {terms[2]}, ..."
    s = rf"The sequence decreases by {d}. The next two terms are <strong>{terms[3]}, {terms[4]}</strong>."
    return q, s, "Check whether the sequence is going down by a constant amount.", 1


def _seq_term_to_term_rule():
    start = random.randint(1, 12); d = random.randint(2, 10)
    terms = [start + i*d for i in range(4)]
    q = rf"State the term-to-term rule for {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}."
    s = rf"Each term increases by {d}, so the rule is <strong>add {d}</strong>."
    return q, s, "Compare consecutive terms.", 1


def _seq_nth_linear_positive():
    a = random.randint(2, 9); b = random.randint(1, 10)
    terms = [a*n+b for n in range(1,5)]
    q = rf"Find the nth term of the sequence {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ..."
    s = rf"The common difference is {a}, so start with {a}n. The first term of {a}n is {a}, so add {b}. The nth term is <strong>{a}n + {b}</strong>."
    return q, s, "The common difference is the coefficient of n.", 2


def _seq_nth_linear_negative_const():
    a = random.randint(3, 9); b = random.randint(-8, -1)
    terms = [a*n+b for n in range(1,5)]
    q = rf"Find the nth term of the sequence {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ..."
    sign = '-' if b < 0 else '+'
    s = rf"The common difference is {a}, so start with {a}n. Compare the first term: {a}n gives {a}, and {a} {sign} {abs(b)} gives {terms[0]}. The nth term is <strong>{a}n {sign} {abs(b)}</strong>."
    return q, s, "Compare with the matching times table.", 2


def _seq_nth_decreasing():
    a = -random.randint(2, 8); b = random.randint(20, 40)
    terms = [a*n+b for n in range(1,5)]
    q = rf"Find the nth term of the sequence {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ..."
    s = rf"The common difference is {a}, so the coefficient of n is {a}. Since the first term is {terms[0]}, the nth term is <strong>{a}n + {b}</strong>."
    return q, s, "A decreasing linear sequence has a negative coefficient of n.", 2


def _seq_find_term_from_nth():
    a = random.randint(2, 9); b = random.randint(-5, 10); n = random.randint(8, 25)
    val = a*n + b
    q = rf"The nth term of a sequence is {a}n + {b}. Find the {n}th term."
    s = rf"Substitute n = {n}: {a}({n}) + {b} = <strong>{val}</strong>."
    return q, s, "Substitute the position number for n.", 1


def _seq_is_number_in_sequence():
    a = random.randint(3, 9); b = random.randint(1, 8); n = random.randint(5, 15); val = a*n + b
    q = rf"The nth term is {a}n + {b}. Is {val} in the sequence?"
    s = rf"Set {a}n + {b} = {val}. Then {a}n = {val-b}, so n = {n}. Since n is a positive whole number, <strong>yes</strong>."
    return q, s, "Solve for n and check whether it is a positive integer.", 2


def _seq_position_of_term():
    a = random.randint(2, 8); b = random.randint(-4, 8); n = random.randint(6, 20); val = a*n+b
    q = rf"In the sequence with nth term {a}n + {b}, which term is {val}?"
    s = rf"Solve {a}n + {b} = {val}. This gives {a}n = {val-b}, so n = <strong>{n}</strong>."
    return q, s, "Set the nth term equal to the value.", 2


def _seq_square_numbers():
    n = random.randint(6, 14); val = n*n
    q = rf"Find the {n}th square number."
    s = rf"The nth square number is n². So {n}² = <strong>{val}</strong>."
    return q, s, "Square the position number.", 1


def _seq_triangular_numbers():
    n = random.randint(5, 15); val = n*(n+1)//2
    q = rf"Find the {n}th triangular number."
    s = rf"Triangular number = n(n+1)/2 = {n}×{n+1}/2 = <strong>{val}</strong>."
    return q, s, "Use n(n+1)/2.", 2


def _seq_fibonacci_type():
    a, b = random.randint(1, 6), random.randint(4, 10)
    terms = [a,b,a+b,a+2*b,2*a+3*b]
    q = rf"Find the next two terms: {terms[0]}, {terms[1]}, {terms[2]}, ..."
    s = rf"Each term is the sum of the two previous terms. The next two terms are <strong>{terms[3]}, {terms[4]}</strong>."
    return q, s, "Add the previous two terms.", 2


def _seq_geometric_next():
    start = random.randint(2, 6); r = random.choice([2,3,4])
    terms = [start*r**i for i in range(5)]
    q = rf"Find the next two terms: {terms[0]}, {terms[1]}, {terms[2]}, ..."
    s = rf"Each term is multiplied by {r}. The next two terms are <strong>{terms[3]}, {terms[4]}</strong>."
    return q, s, "Look for a multiplication rule.", 2


def _seq_quadratic_nth():
    a = random.choice([1,2,3]); b = random.randint(-3,4); c = random.randint(-2,5)
    terms = [a*n*n + b*n + c for n in range(1,5)]
    q = rf"The sequence {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ... has nth term an² + bn + c. State the nth term."
    s = rf"The second difference is {2*a}, so the n² coefficient is {a}. Checking the terms gives <strong>{a}n² + {b}n + {c}</strong>."
    return q, s, "For a quadratic sequence, half the second difference gives the n² coefficient.", 3


def _seq_quadratic_term():
    n = random.randint(5, 12); a = random.choice([1,2]); b = random.randint(-2,5); c = random.randint(-3,5)
    val = a*n*n + b*n + c
    q = rf"Find the {n}th term of the sequence with nth term {a}n² + {b}n + {c}."
    s = rf"Substitute n = {n}: {a}({n})² + {b}({n}) + {c} = <strong>{val}</strong>."
    return q, s, "Substitute carefully into the quadratic nth term.", 2

# ============================================================
# TRANSFORMATIONS
# ============================================================


def _trn_translate_point():
    x,y = random.randint(-5,5), random.randint(-5,5); dx,dy = random.randint(-4,4), random.randint(-4,4)
    if dx == 0 and dy == 0: dx = 3
    q = rf"Translate the point ({x}, {y}) by the vector ({dx}, {dy})."
    s = rf"Add the vector to the coordinates: ({x}+{dx}, {y}+{dy}) = <strong>({x+dx}, {y+dy})</strong>."
    return q, s, "Add the top number to x and the bottom number to y.", 1


def _trn_find_translation_vector():
    x1,y1 = random.randint(-5,5), random.randint(-5,5); dx,dy = random.randint(-5,5), random.randint(-5,5)
    if dx == 0 and dy == 0: dy = -2
    q = rf"Point A({x1}, {y1}) maps to A'({x1+dx}, {y1+dy}). Find the translation vector."
    s = rf"Change in x = {x1+dx} − {x1} = {dx}. Change in y = {y1+dy} − {y1} = {dy}. Vector = <strong>({dx}, {dy})</strong>."
    return q, s, "Subtract old coordinates from new coordinates.", 1


def _trn_reflect_x_axis():
    x,y = random.randint(-6,6), random.choice([i for i in range(-6,7) if i != 0])
    q = rf"Reflect the point ({x}, {y}) in the x-axis."
    s = rf"Reflection in the x-axis keeps x the same and changes the sign of y. Image: <strong>({x}, {-y})</strong>."
    return q, s, "In the x-axis, y changes sign.", 1


def _trn_reflect_y_axis():
    x,y = random.choice([i for i in range(-6,7) if i != 0]), random.randint(-6,6)
    q = rf"Reflect the point ({x}, {y}) in the y-axis."
    s = rf"Reflection in the y-axis changes the sign of x and keeps y the same. Image: <strong>({-x}, {y})</strong>."
    return q, s, "In the y-axis, x changes sign.", 1


def _trn_reflect_y_equals_x():
    x,y = random.randint(-6,6), random.randint(-6,6)
    q = rf"Reflect the point ({x}, {y}) in the line y = x."
    s = rf"Reflection in y = x swaps the coordinates. Image: <strong>({y}, {x})</strong>."
    return q, s, "Swap x and y.", 2


def _trn_rotate_180_origin():
    x,y = random.choice([i for i in range(-6,7) if i != 0]), random.choice([i for i in range(-6,7) if i != 0])
    q = rf"Rotate the point ({x}, {y}) 180° about the origin."
    s = rf"A 180° rotation about the origin changes both signs. Image: <strong>({-x}, {-y})</strong>."
    return q, s, "For 180° about the origin, multiply both coordinates by −1.", 1


def _trn_rotate_90_cw_origin():
    x,y = random.randint(-6,6), random.randint(-6,6)
    q = rf"Rotate the point ({x}, {y}) 90° clockwise about the origin."
    s = rf"A 90° clockwise rotation maps (x, y) to (y, −x). Image: <strong>({y}, {-x})</strong>."
    return q, s, "For 90° clockwise about the origin, use (x, y) → (y, −x).", 2


def _trn_rotate_90_acw_origin():
    x,y = random.randint(-6,6), random.randint(-6,6)
    q = rf"Rotate the point ({x}, {y}) 90° anticlockwise about the origin."
    s = rf"A 90° anticlockwise rotation maps (x, y) to (−y, x). Image: <strong>({-y}, {x})</strong>."
    return q, s, "For 90° anticlockwise about the origin, use (x, y) → (−y, x).", 2


def _trn_enlarge_origin():
    x,y = random.randint(-4,4), random.randint(-4,4); k = random.choice([2,3,4])
    q = rf"Enlarge the point ({x}, {y}) by scale factor {k} about the origin."
    s = rf"Multiply both coordinates by {k}: <strong>({k*x}, {k*y})</strong>."
    return q, s, "For enlargement from the origin, multiply each coordinate by the scale factor.", 1


def _trn_enlarge_fraction():
    x,y = random.choice([2,4,6,8]), random.choice([2,4,6,8]); k = 0.5
    q = rf"Enlarge the point ({x}, {y}) by scale factor 1/2 about the origin."
    s = rf"Multiply both coordinates by 1/2: <strong>({_b2_fmt(x*k)}, {_b2_fmt(y*k)})</strong>."
    return q, s, "A fractional scale factor makes the image smaller.", 2


def _trn_negative_enlargement():
    x,y = random.randint(1,5), random.randint(1,5); k = -2
    q = rf"Enlarge the point ({x}, {y}) by scale factor -2 about the origin."
    s = rf"Multiply both coordinates by -2: <strong>({k*x}, {k*y})</strong>."
    return q, s, "Negative scale factors place the image on the opposite side of the centre.", 3


def _trn_describe_reflection():
    axis = random.choice(['x-axis','y-axis'])
    if axis == 'x-axis':
        x,y = random.randint(-5,5), random.randint(1,6); image = (x,-y)
    else:
        x,y = random.randint(1,6), random.randint(-5,5); image = (-x,y)
    q = rf"Point ({x}, {y}) maps to {image}. Describe the transformation."
    s = rf"Only one coordinate changes sign. The transformation is <strong>reflection in the {axis}</strong>."
    return q, s, "Compare the signs of the coordinates.", 2


def _trn_describe_rotation_180():
    x,y = random.randint(1,6), random.randint(1,6)
    q = rf"Point ({x}, {y}) maps to ({-x}, {-y}). Describe the transformation."
    s = "Both coordinates change sign, so the transformation is <strong>rotation 180° about the origin</strong>."
    return q, s, "A 180° rotation about the origin changes both signs.", 2


def _trn_combined_translation_reflection():
    x,y = random.randint(-4,4), random.randint(-4,4); dx,dy = random.randint(1,4), random.randint(-4,4)
    tx,ty = x+dx, y+dy
    q = rf"Translate ({x}, {y}) by ({dx}, {dy}), then reflect the result in the y-axis."
    s = rf"After translation: ({tx}, {ty}). Reflect in the y-axis: <strong>({-tx}, {ty})</strong>."
    return q, s, "Do the transformations in order.", 3


def _trn_invariant_point():
    q = "Which point stays fixed when a shape is rotated about the origin?"
    s = "The centre of rotation stays fixed. Here that point is <strong>(0, 0)</strong>."
    return q, s, "The centre of rotation does not move.", 1


def _b2_register(prefix, funcs):
    for i, func in enumerate(funcs, 1):
        _b2_make_variant(f"_{prefix}_{i:02d}", func)

_eq_found_funcs = [_eq_one_step_add,_eq_one_step_multiply,_eq_two_step,_eq_bracket_simple,_eq_substitution_formula,_eq_rearrange_add,_eq_rearrange_multiply,_eq_linear_inequality,_eq_one_step_add,_eq_one_step_multiply,_eq_two_step,_eq_substitution_formula,_eq_rearrange_add,_eq_rearrange_multiply,_eq_form_expression]
_eq_inter_funcs = [_eq_two_step,_eq_bracket_simple,_eq_unknowns_both_sides,_eq_fraction_equation,_eq_rearrange_complex,_eq_linear_inequality,_eq_negative_inequality,_eq_form_expression,_eq_substitution_formula,_eq_bracket_simple,_eq_unknowns_both_sides,_eq_fraction_equation,_eq_rearrange_complex,_eq_linear_inequality,_eq_negative_inequality]
_eq_diff_funcs = [_eq_unknowns_both_sides,_eq_fraction_equation,_eq_rearrange_complex,_eq_negative_inequality,_eq_quadratic_factorise,_eq_simultaneous_elimination,_eq_form_expression,_eq_bracket_simple,_eq_linear_inequality,_eq_quadratic_factorise,_eq_simultaneous_elimination,_eq_unknowns_both_sides,_eq_fraction_equation,_eq_rearrange_complex,_eq_negative_inequality]

_seq_found_funcs = [_seq_next_terms_add,_seq_next_terms_subtract,_seq_term_to_term_rule,_seq_nth_linear_positive,_seq_find_term_from_nth,_seq_square_numbers,_seq_geometric_next,_seq_next_terms_add,_seq_next_terms_subtract,_seq_term_to_term_rule,_seq_nth_linear_positive,_seq_find_term_from_nth,_seq_square_numbers,_seq_geometric_next,_seq_fibonacci_type]
_seq_inter_funcs = [_seq_nth_linear_positive,_seq_nth_linear_negative_const,_seq_nth_decreasing,_seq_find_term_from_nth,_seq_is_number_in_sequence,_seq_position_of_term,_seq_triangular_numbers,_seq_fibonacci_type,_seq_geometric_next,_seq_quadratic_term,_seq_nth_linear_positive,_seq_nth_linear_negative_const,_seq_position_of_term,_seq_triangular_numbers,_seq_quadratic_term]
_seq_diff_funcs = [_seq_nth_decreasing,_seq_is_number_in_sequence,_seq_position_of_term,_seq_triangular_numbers,_seq_fibonacci_type,_seq_geometric_next,_seq_quadratic_nth,_seq_quadratic_term,_seq_nth_linear_negative_const,_seq_nth_decreasing,_seq_is_number_in_sequence,_seq_position_of_term,_seq_quadratic_nth,_seq_quadratic_term,_seq_fibonacci_type]

_trn_found_funcs = [_trn_translate_point,_trn_find_translation_vector,_trn_reflect_x_axis,_trn_reflect_y_axis,_trn_rotate_180_origin,_trn_enlarge_origin,_trn_invariant_point,_trn_translate_point,_trn_find_translation_vector,_trn_reflect_x_axis,_trn_reflect_y_axis,_trn_rotate_180_origin,_trn_enlarge_origin,_trn_invariant_point,_trn_describe_reflection]
_trn_inter_funcs = [_trn_translate_point,_trn_find_translation_vector,_trn_reflect_x_axis,_trn_reflect_y_axis,_trn_reflect_y_equals_x,_trn_rotate_180_origin,_trn_rotate_90_cw_origin,_trn_rotate_90_acw_origin,_trn_enlarge_origin,_trn_enlarge_fraction,_trn_describe_reflection,_trn_describe_rotation_180,_trn_combined_translation_reflection,_trn_invariant_point,_trn_reflect_y_equals_x]
_trn_diff_funcs = [_trn_reflect_y_equals_x,_trn_rotate_90_cw_origin,_trn_rotate_90_acw_origin,_trn_enlarge_fraction,_trn_negative_enlargement,_trn_describe_reflection,_trn_describe_rotation_180,_trn_combined_translation_reflection,_trn_translate_point,_trn_find_translation_vector,_trn_negative_enlargement,_trn_combined_translation_reflection,_trn_rotate_90_cw_origin,_trn_rotate_90_acw_origin,_trn_enlarge_fraction]

_b2_register('equations_inequalities_foundational', _eq_found_funcs)
_b2_register('equations_inequalities_intermediate', _eq_inter_funcs)
_b2_register('equations_inequalities_difficult', _eq_diff_funcs)
_b2_register('sequences_foundational', _seq_found_funcs)
_b2_register('sequences_intermediate', _seq_inter_funcs)
_b2_register('sequences_difficult', _seq_diff_funcs)
_b2_register('transformations_foundational', _trn_found_funcs)
_b2_register('transformations_intermediate', _trn_inter_funcs)
_b2_register('transformations_difficult', _trn_diff_funcs)


def _b2_pool(topic, difficulty):
    prefix_map = {
        'equations_inequalities': 'equations_inequalities',
        'sequences': 'sequences',
        'transformations': 'transformations',
    }
    prefix = prefix_map[topic]
    found = [globals()[f'_{prefix}_foundational_{i:02d}'] for i in range(1,16)]
    inter = [globals()[f'_{prefix}_intermediate_{i:02d}'] for i in range(1,16)]
    diff = [globals()[f'_{prefix}_difficult_{i:02d}'] for i in range(1,16)]
    if difficulty == 'foundational': return found
    if difficulty == 'intermediate': return inter
    if difficulty == 'difficult': return diff
    return random.sample(found,4) + random.sample(inter,4) + random.sample(diff,2)


def _b2_variants(topic, difficulty, mode):
    if mode == 'mcq':
        return [_b2_mcq_factory(topic)] * 10
    pool = _b2_pool(topic, difficulty)
    shuffled = random.sample(pool, len(pool))
    return (shuffled * (10 // len(shuffled) + 1))[:10]


def _b2_mcq_factory(topic):
    def mcq():
        pool = _b2_pool(topic, random.choice(['foundational','intermediate','difficult']))
        q, s, hint, marks = random.choice(pool)()
        correct = _b2_extract_answer(s)
        options, letter = _b2_options(correct, ['x = 1', '0', '(0, 0)'])
        return q, f"Answer: {letter}\n\n{hint}", hint, 1, options, letter
    mcq.__name__ = f'{topic}_mcq'
    return mcq


def gcse_equations_inequalities_variants(difficulty, mode):
    return _b2_variants('equations_inequalities', difficulty, mode)


def gcse_sequences_variants(difficulty, mode):
    return _b2_variants('sequences', difficulty, mode)


def gcse_transformations_variants(difficulty, mode):
    return _b2_variants('transformations', difficulty, mode)


def gcse_equations_inequalities(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = _b2_mcq_factory('equations_inequalities')()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'equations_inequalities', options=opts, correct_answer=correct)
    variants = gcse_equations_inequalities_variants(difficulty, mode)
    if variant_name is None:
        variant = random.choice(variants)
    else:
        full_pool = _b2_pool('equations_inequalities', difficulty)
        variant = {v.__name__: v for v in full_pool}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'equations_inequalities')


def gcse_sequences(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = _b2_mcq_factory('sequences')()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'sequences', options=opts, correct_answer=correct)
    variants = gcse_sequences_variants(difficulty, mode)
    if variant_name is None:
        variant = random.choice(variants)
    else:
        full_pool = _b2_pool('sequences', difficulty)
        variant = {v.__name__: v for v in full_pool}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'sequences')


def gcse_transformations(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = _b2_mcq_factory('transformations')()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'transformations', options=opts, correct_answer=correct)
    variants = gcse_transformations_variants(difficulty, mode)
    if variant_name is None:
        variant = random.choice(variants)
    else:
        full_pool = _b2_pool('transformations', difficulty)
        variant = {v.__name__: v for v in full_pool}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'transformations')
