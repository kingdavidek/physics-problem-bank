"""
GCSE Maths – Sequences
15 foundational · 15 intermediate · 15 difficult · 18 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Pure theorem proofs use Plan C proof_steps banks; some nth-term text variants stay ungraded.
"""
import random
import math
from fractions import Fraction
from generators.shared.utils import make_problem, proof_steps_answer, proof_steps_problem_extra
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


def _linear_nth(d, b):
    """Return a clean string for the nth term dn + b."""
    if b == 0:
        return f"{d}n"
    elif b > 0:
        return f"{d}n + {b}"
    else:
        return f"{d}n - {-b}"


def _seq_raw(value, places=2):
    """Canonical numeric string for typed answer checking."""
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        val = round(value, places)
        if val == int(val):
            return str(int(val))
        return f"{val:.{places}f}".rstrip('0').rstrip('.')
    return str(value)


def _seq_keyword_answer(value):
    return {'type': 'keyword', 'value': str(value).strip().lower()}


def _seq_fields_answer(values, labels, places=2):
    return {
        'type': 'number_fields',
        'values': tuple(_seq_raw(v, places) for v in values),
        'labels': tuple(labels),
    }


def _seq_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'proof_steps':
            extra = proof_steps_problem_extra(raw)
        elif isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            if values and len(values) == len(labels):
                extra = {
                    'correct_answer_raw': '|'.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_format_hint': (
                        'Enter a number or fraction in every field'
                    ),
                }
        elif isinstance(raw, dict) and raw.get('type') == 'keyword':
            value = raw.get('value')
            if value is not None and str(value).strip():
                extra = {
                    'correct_answer_raw': str(value).strip().lower(),
                    'answer_type': 'keyword',
                    'answer_format_hint': 'e.g. yes or no',
                }
        elif isinstance(raw, Fraction):
            extra = {
                'correct_answer_raw': str(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number or fraction',
            }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _seq_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
        elif isinstance(raw, str):
            extra = {
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'answer_format_hint': (
                    'Enter a number or fraction' if '/' in raw else 'Enter a number'
                ),
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'sequences', **extra
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _seq_found_next_term_arithmetic():
    a = random.randint(2, 20)
    d = random.randint(2, 8)
    n = 4
    terms = [a + d * i for i in range(n)]
    next_t = terms[-1] + d
    seq_str = ", ".join(str(t) for t in terms)
    q = rf"Write down the next term of the arithmetic sequence: {seq_str}, ___"
    s = (rf"The common difference is \(d = {d}\) (add {d} each time).<br>"
         rf"Next term = \({terms[-1]} + {d}\)<br>"
         rf"<strong>\(= {next_t}\)</strong>")
    hint = f"Find the difference between consecutive terms, then add it to the last term."
    return q, s, hint, 1, next_t


def _seq_found_next_term_subtract():
    a = random.randint(40, 80)
    d = random.randint(3, 9)
    n = 4
    terms = [a - d * i for i in range(n)]
    next_t = terms[-1] - d
    seq_str = ", ".join(str(t) for t in terms)
    q = rf"Write down the next term of the sequence: {seq_str}, ___"
    s = (rf"Each term decreases by {d}, so the common difference is \(d = -{d}\).<br>"
         rf"Next term = \({terms[-1]} - {d}\)<br>"
         rf"<strong>\(= {next_t}\)</strong>")
    hint = "Find the difference between consecutive terms."
    return q, s, hint, 1, next_t


def _seq_found_identify_rule():
    a = random.randint(3, 15)
    d = random.randint(3, 7)
    terms = [a + d * i for i in range(5)]
    seq_str = ", ".join(str(t) for t in terms)
    q = rf"Describe the term-to-term rule for the sequence: {seq_str}"
    s = (rf"The difference between consecutive terms is \({terms[1]} - {terms[0]} = {d}\).<br>"
         rf"<strong>Start at {a} and add {d} each time.</strong>")
    hint = "Subtract any term from the next term to find the common difference."
    return q, s, hint, 2


def _seq_found_nth_term_find_terms():
    a = random.randint(2, 6)
    d = random.randint(3, 7)
    b = a - d
    expr_str = f"{d}n" + (f" + {b}" if b > 0 else (f" - {-b}" if b < 0 else ""))
    terms = [d * n + b for n in range(1, 6)]
    terms_str = ", ".join(str(t) for t in terms[:4])
    q = rf"The nth term of a sequence is \({expr_str}\). Write down the first four terms."
    s = (rf"Substitute \(n = 1, 2, 3, 4\):<br>"
         rf"\(n=1\): \({d}(1){'+' if b>=0 else ''}{b} = {terms[0]}\),  "
         rf"\(n=2\): \({terms[1]}\),  "
         rf"\(n=3\): \({terms[2]}\),  "
         rf"\(n=4\): \({terms[3]}\)<br>"
         rf"<strong>{terms_str}</strong>")
    hint = f"Substitute n = 1, 2, 3, 4 into the expression {expr_str}."
    return q, s, hint, 2


def _seq_found_nth_term_find_value():
    a = random.randint(3, 8)
    d = random.randint(2, 6)
    b = a - d
    n_val = random.randint(10, 20)
    ans = d * n_val + b
    expr_str = f"{d}n" + (f" + {b}" if b > 0 else (f" - {-b}" if b < 0 else ""))
    q = rf"The nth term of a sequence is \({expr_str}\). Find the {n_val}th term."
    s = (rf"Substitute \(n = {n_val}\):<br>"
         rf"\({d} \times {n_val} {'+' if b >= 0 else '-'} {abs(b)} = {d*n_val} {'+' if b>=0 else '-'} {abs(b)}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = f"Replace n with {n_val} in {expr_str}."
    return q, s, hint, 1, ans


def _seq_found_is_term_in_seq():
    d = random.randint(3, 7)
    a = random.randint(2, d)
    b = a - d
    # choose a value that IS in the sequence
    k = random.randint(5, 15)
    val = d * k + b
    expr_str = f"{d}n" + (f" + {b}" if b > 0 else (f" - {-b}" if b < 0 else ""))
    q = rf"Is {val} a term in the sequence with nth term \({expr_str}\)? Show your working."
    s = (rf"Set \({expr_str} = {val}\):<br>"
         rf"\({d}n = {val - b}\)<br>"
         rf"\(n = {val - b} \div {d} = {k}\)<br>"
         rf"Since \(n = {k}\) is a positive integer, <strong>{val} is the {k}th term</strong>.")
    hint = f"Set {expr_str} = {val} and solve for n. If n is a positive integer, the value is in the sequence."
    return q, s, hint, 3, _seq_keyword_answer('yes')


def _seq_found_term_to_term_rule():
    start = random.randint(5, 20)
    mult = random.choice([2, 3])
    terms = [start * mult**i for i in range(5)]
    seq_str = ", ".join(str(t) for t in terms[:4])
    q = rf"A sequence starts: {seq_str}, ...<br>State the term-to-term rule."
    s = (rf"Each term is multiplied by {mult}: \({terms[0]} \times {mult} = {terms[1]}\), etc.<br>"
         rf"<strong>Multiply the previous term by {mult}.</strong>")
    hint = "Divide each term by the previous term to find the multiplier."
    return q, s, hint, 1


def _seq_found_geometric_next():
    a = random.randint(2, 5)
    r = random.choice([2, 3, 4])
    terms = [a * r**i for i in range(4)]
    next_t = terms[-1] * r
    seq_str = ", ".join(str(t) for t in terms)
    q = rf"Find the next term of the geometric sequence: {seq_str}, ___"
    s = (rf"Common ratio \(r = {terms[1]} \div {terms[0]} = {r}\).<br>"
         rf"Next term \(= {terms[-1]} \times {r}\)<br>"
         rf"<strong>\(= {next_t}\)</strong>")
    hint = "Divide any term by the previous term to find the common ratio r."
    return q, s, hint, 2, next_t


def _seq_found_square_numbers():
    n_val = random.randint(8, 14)
    ans = n_val ** 2
    q = rf"Write down the {n_val}th square number."
    s = (rf"The \(n\)th square number is \(n^2\).<br>"
         rf"\({n_val}^2 = {n_val} \times {n_val}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = "The nth square number is n²."
    return q, s, hint, 1, ans


def _seq_found_triangle_numbers():
    n_val = random.randint(6, 12)
    ans = n_val * (n_val + 1) // 2
    tri = [k*(k+1)//2 for k in range(1, 6)]
    tri_str = ", ".join(str(t) for t in tri)
    q = rf"The triangle numbers are {tri_str}, ...<br>Find the {n_val}th triangle number."
    s = (rf"The \(n\)th triangle number is \(\dfrac{{n(n+1)}}{{2}}\).<br>"
         rf"\(\dfrac{{{n_val} \times {n_val+1}}}{{2}} = \dfrac{{{n_val*(n_val+1)}}}{{2}}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = "The nth triangle number is n(n+1)/2."
    return q, s, hint, 2, ans


def _seq_found_odd_even_seq():
    choice = random.choice(['odd', 'even'])
    if choice == 'odd':
        terms = [2*k-1 for k in range(1, 6)]
        n_val = random.randint(10, 20)
        ans = 2*n_val - 1
        q = rf"The sequence of odd numbers starts: {', '.join(str(t) for t in terms)}, ...<br>Find the {n_val}th odd number."
        s = rf"The \(n\)th odd number is \(2n - 1\).<br>\(2 \times {n_val} - 1\)<br><strong>\(= {ans}\)</strong>"
    else:
        terms = [2*k for k in range(1, 6)]
        n_val = random.randint(10, 20)
        ans = 2*n_val
        q = rf"The sequence of even numbers starts: {', '.join(str(t) for t in terms)}, ...<br>Find the {n_val}th even number."
        s = rf"The \(n\)th even number is \(2n\).<br>\(2 \times {n_val}\)<br><strong>\(= {ans}\)</strong>"
    hint = "Use the formula for the nth term of the odd or even number sequence."
    return q, s, hint, 1, ans


def _seq_found_fibonacci_next():
    a, b = random.choice([(1, 1), (2, 3), (3, 5)])
    terms = [a, b]
    for _ in range(3):
        terms.append(terms[-1] + terms[-2])
    next_t = terms[-1] + terms[-2]
    seq_str = ", ".join(str(t) for t in terms)
    q = rf"A Fibonacci-type sequence starts: {seq_str}, ___<br>Find the next term."
    s = (rf"Each term is the sum of the two preceding terms.<br>"
         rf"Next term \(= {terms[-1]} + {terms[-2]}\)<br>"
         rf"<strong>\(= {next_t}\)</strong>")
    hint = "Add the last two terms to find the next one."
    return q, s, hint, 1, next_t


def _seq_found_missing_term():
    a = random.randint(5, 20)
    d = random.randint(3, 8)
    terms = [a + d*i for i in range(5)]
    gap_idx = random.randint(1, 3)
    displayed = [str(t) if i != gap_idx else "___" for i, t in enumerate(terms)]
    q = rf"Find the missing term: {', '.join(displayed)}"
    s = (rf"The common difference is \(d = {d}\).<br>"
         rf"Missing term \(= {terms[gap_idx - 1]} + {d}\) or \(= {terms[gap_idx + 1]} - {d}\)<br>"
         rf"<strong>\(= {terms[gap_idx]}\)</strong>")
    hint = "Use the common difference to work out the missing value."
    return q, s, hint, 1, terms[gap_idx]


def _seq_found_continue_pattern():
    patterns = [
        ([1, 4, 9, 16], r"Square numbers: \(n^2\)", 25),
        ([1, 3, 6, 10], r"Triangle numbers: \(n(n+1)/2\)", 15),
        ([2, 4, 8, 16], r"Powers of 2: \(2^n\)", 32),
    ]
    terms, rule, next_t = random.choice(patterns)
    seq_str = ", ".join(str(t) for t in terms)
    q = rf"Write down the next term in the sequence: {seq_str}, ___<br>Explain the pattern and find the next term in the sequence."
    s = (rf"Pattern: {rule}.<br>"
         rf"<strong>Next term = {next_t}</strong>")
    hint = "Look at differences or ratios to identify the pattern."
    return q, s, hint, 2, next_t


def _seq_found_count_patterns():
    pattern_n = random.randint(4, 7)
    dots_per = random.randint(3, 5)
    pattern_terms = [dots_per * k for k in range(1, pattern_n)]
    seq_str = ", ".join(str(t) for t in pattern_terms[:4])
    ans = dots_per * (pattern_n + 1)
    q = (rf"A pattern of dots follows the rule: shape 1 has {dots_per} dots, shape 2 has {2*dots_per} dots, shape 3 has {3*dots_per} dots, ...<br>"
         rf"How many dots does shape {pattern_n + 1} have?")
    s = (rf"The \(n\)th shape has \({dots_per}n\) dots.<br>"
         rf"Shape {pattern_n + 1}: \({dots_per} \times {pattern_n + 1}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = f"Find the formula (nth term), then substitute n = {pattern_n + 1}."
    return q, s, hint, 2, ans


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _seq_inter_find_nth_term():
    d = random.randint(3, 8)
    a = random.randint(2, d + 3)
    b = a - d   # nth term = dn + b
    terms = [d*n + b for n in range(1, 6)]
    seq_str = ", ".join(str(t) for t in terms[:5])
    s_expr = f"{d}n" + (f" + {b}" if b > 0 else (f" - {-b}" if b < 0 else ""))
    q = rf"Find the nth term of the arithmetic sequence: {seq_str}"
    s = (rf"Common difference \(d = {terms[1]} - {terms[0]} = {d}\).<br>"
         rf"First term \(a = {terms[0]}\).<br>"
         rf"nth term \(= a + (n-1)d = {terms[0]} + (n-1) \times {d}\)<br>"
         rf"\(= {terms[0]} + {d}n - {d} = {d}n + {b}\)<br>"
         rf"<strong>nth term \(= {s_expr}\)</strong>")
    hint = "Use nth term = a + (n-1)d, then simplify."
    return q, s, hint, 3


def _seq_inter_nth_term_negative_d():
    d = -random.randint(3, 7)
    a = random.randint(30, 60)
    b = a - d
    terms = [d*n + b for n in range(1, 6)]
    seq_str = ", ".join(str(t) for t in terms[:5])
    s_expr = f"{d}n" + (f" + {b}" if b >= 0 else f" - {-b}")
    q = rf"Find the nth term of the arithmetic sequence: {seq_str}"
    s = (rf"Common difference \(d = {terms[1]} - {terms[0]} = {d}\) (decreasing).<br>"
         rf"nth term \(= {terms[0]} + (n-1)({d})\)<br>"
         rf"\(= {terms[0]} + {d}n - ({d}) = {d}n + {b}\)<br>"
         rf"<strong>nth term \(= {s_expr}\)</strong>")
    hint = "The common difference is negative. Use the same formula: nth term = a + (n−1)d."
    return q, s, hint, 3


def _seq_inter_which_term():
    d = random.randint(3, 7)
    a = random.randint(2, d)
    b = a - d
    k = random.randint(15, 30)
    val = d * k + b
    s_expr = _linear_nth(d, b)
    q = rf"The nth term of a sequence is \({s_expr}\) Which term has value {val}?"
    s = (rf"Set \({s_expr} = {val}\):<br>"
         rf"\({d}n = {val - b}\)<br>"
         rf"\(n = {val - b} \div {d} = {k}\)<br>"
         rf"<strong>{val} is the {k}th term.</strong>")
    hint = f"Set the nth-term expression equal to {val} and solve for n."
    return q, s, hint, 3, k


def _seq_inter_not_in_seq():
    d = random.randint(3, 7)
    a = random.randint(2, d)
    b = a - d
    k = random.randint(5, 20)
    val = d * k + b + random.choice([1, 2])   # deliberately NOT a term
    s_expr = _linear_nth(d, b)
    q = rf"Show that {val} is NOT a term in the sequence with nth term \({s_expr}\)."
    numer = val - b
    s = (rf"Set \({s_expr} = {val}\):<br>"
         rf"\({d}n = {numer}\)<br>"
         rf"\(n = {numer} \div {d} = {Fraction(numer, d)}\)<br>"
         rf"Since \(n\) is not a positive integer, <strong>{val} is not a term in the sequence.</strong>")
    hint = f"Set {s_expr} = {val} and solve for n. If n is not a whole number, the value is not in the sequence."
    return q, s, hint, 3, _seq_keyword_answer('no')


def _seq_inter_first_term_over():
    d = random.randint(3, 8)
    a = random.randint(2, d)
    b = a - d
    target = random.randint(100, 200)
    # dn + b > target → n > (target - b)/d
    n_ans = math.ceil((target - b) / d)
    val = d * n_ans + b
    s_expr = _linear_nth(d, b)
    q = rf"The nth term of a sequence is \({s_expr}\)<br>Find the first term in the sequence that is greater than {target}."
    s = (rf"Solve \({s_expr} > {target}\):<br>"
         rf"\({d}n > {target - b}\)<br>"
         rf"\(n > {(target - b)/d:.4f}...\)<br>"
         rf"The first integer value is \(n = {n_ans}\).<br>"
         rf"<strong>First term greater than {target} is \({val}\) (the {n_ans}th term).</strong>")
    hint = f"Solve {s_expr} > {target} for n, then round up to the nearest whole number."
    return q, s, hint, 3, val


def _seq_inter_geometric_nth_term():
    a = random.randint(2, 5)
    r = random.choice([2, 3])
    n_val = random.randint(6, 10)
    ans = a * r**(n_val - 1)
    q = rf"A geometric sequence has first term {a} and common ratio {r}.<br>Find the {n_val}th term."
    s = (rf"The nth term of a geometric sequence is \(ar^{{n-1}}\).<br>"
         rf"\({a} \times {r}^{{{n_val}-1}} = {a} \times {r}^{{{n_val-1}}}\)<br>"
         rf"\(= {a} \times {r**(n_val-1)}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = f"Use the formula: nth term = ar^(n-1), with a = {a} and r = {r}."
    return q, s, hint, 3, ans


def _seq_inter_two_sequences_same():
    d1, d2 = random.randint(3, 6), random.randint(2, 5)
    while d1 == d2:
        d2 = random.randint(2, 5)
    a1 = random.randint(2, d1)
    a2 = random.randint(2, d2)
    b1, b2 = a1 - d1, a2 - d2
    # Find n where d1*n + b1 = d2*n + b2 → (d1-d2)*n = b2-b1
    diff = d1 - d2
    rhs = b2 - b1
    if diff != 0 and rhs % diff == 0:
        n_val = rhs // diff
    else:
        # adjust to guarantee integer solution
        b2 = b1 + 3 * diff
        rhs = b2 - b1
        n_val = rhs // diff
        a2 = d2 + b2
    e1 = f"{d1}n" + (f" + {b1}" if b1 >= 0 else f" - {-b1}")
    e2 = f"{d2}n" + (f" + {b2}" if b2 >= 0 else f" - {-b2}")
    ans = d1 * n_val + b1
    q = (rf"Sequence A has nth term \({e1}\). Sequence B has nth term \({e2}\).<br>"
         rf"Find the value that appears in both sequences at the same position.")
    s = (rf"Set the two expressions equal:<br>"
         rf"\({e1} = {e2}\)<br>"
         rf"\({d1-d2}n = {b2-b1}\)<br>"
         rf"\(n = {n_val}\)<br>"
         rf"Both sequences give the value \({e1.replace('n', str(n_val))} = {ans}\).<br>"
         rf"<strong>The shared value is {ans} (at position n = {n_val}).</strong>")
    hint = f"Set {e1} = {e2} and solve for n."
    return q, s, hint, 4, ans


def _seq_inter_sum_arithmetic():
    n = random.randint(10, 20)
    a = random.randint(2, 10)
    d = random.randint(2, 5)
    l = a + (n - 1) * d
    ans = n * (a + l) // 2
    q = rf"Find the sum of the first {n} terms of the arithmetic sequence with first term {a} and common difference {d}."
    s = (rf"Last term: \(l = a + (n-1)d = {a} + {n-1} \times {d} = {l}\)<br>"
         rf"Sum: \(S_n = \dfrac{{n(a+l)}}{{2}} = \dfrac{{{n}({a}+{l})}}{{2}} = \dfrac{{{n}({a+l})}}{{2}}\)<br>"
         rf"<strong>\(S_{{{n}}} = {ans}\)</strong>")
    hint = "Use Sn = n(a + l)/2, where l is the last term."
    return q, s, hint, 3, ans


def _seq_inter_quadratic_identify():
    # sequence: n² + c
    c = random.randint(1, 6)
    terms = [n**2 + c for n in range(1, 6)]
    seq_str = ", ".join(str(t) for t in terms[:5])
    q = rf"The sequence {seq_str}, ... has second differences that are constant.<br>Find the nth term."
    s = (rf"First differences: {', '.join(str(terms[i+1]-terms[i]) for i in range(4))}<br>"
         rf"Second differences: all equal to 2, so the sequence is quadratic with leading term \(n^2\).<br>"
         rf"Compare \(n^2\): 1, 4, 9, 16, 25. The sequence exceeds \(n^2\) by {c}.<br>"
         rf"<strong>nth term \(= n^2 + {c}\)</strong>")
    hint = "Calculate first and second differences. Constant second differences → quadratic (starts with n²)."
    return q, s, hint, 4


def _seq_inter_arithmetic_word():
    seats_row1 = random.randint(20, 30)
    extra = random.randint(3, 6)
    rows = random.randint(15, 25)
    total = rows * seats_row1 + extra * rows * (rows - 1) // 2
    q = (rf"A theatre has {rows} rows of seats. The first row has {seats_row1} seats and each subsequent row has {extra} more seats than the row in front.<br>"
         rf"Find the total number of seats in the theatre.")
    l = seats_row1 + (rows - 1) * extra
    s = (rf"The number of seats per row forms an arithmetic sequence with \(a = {seats_row1}\), \(d = {extra}\), \(n = {rows}\).<br>"
         rf"Last row: \(l = {seats_row1} + {rows-1} \times {extra} = {l}\)<br>"
         rf"Total: \(S = \dfrac{{{rows}({seats_row1}+{l})}}{{2}} = \dfrac{{{rows} \times {seats_row1+l}}}{{2}}\)<br>"
         rf"<strong>Total seats \(= {total}\)</strong>")
    hint = "The row sizes form an arithmetic sequence. Use Sn = n(a + l)/2."
    return q, s, hint, 4, total


def _seq_inter_sequences_nth_term_large():
    d = random.randint(5, 12)
    a = random.randint(2, d)
    b = a - d
    n_val = random.randint(50, 100)
    ans = d * n_val + b
    s_expr = _linear_nth(d, b)
    q = rf"The nth term of a sequence is \({s_expr}\).<br>Find the {n_val}th term"
    s = (rf"\(n = {n_val}\):<br>"
         rf"\({d} \times {n_val} {'+' if b >= 0 else '-'} {abs(b)} = {d*n_val} {'+' if b >= 0 else '-'} {abs(b)}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = f"Substitute n = {n_val} into {s_expr}."
    return q, s, hint, 1, ans


def _seq_inter_nth_term_from_context():
    wage = random.randint(200, 400)
    rise = random.randint(20, 50)
    year = random.randint(5, 10)
    ans = wage + (year - 1) * rise
    q = (rf"A worker earns £{wage} in year 1. Each year their salary increases by £{rise}.<br>"
         rf"Write a formula for the salary in year \(n\), and find the salary in year {year}.")
    s = (rf"Salary in year \(n\): \(S_n = {wage} + (n-1) \times {rise} = {rise}n + {wage-rise}\)<br>"
         rf"Year {year}: \({rise} \times {year} + {wage - rise}\)<br>"
         rf"<strong>£{ans}</strong>")
    hint = "The salary is an arithmetic sequence. Write it in the form dn + b."
    return q, s, hint, 4, ans


def _seq_inter_common_terms():
    """Find the first term common to two arithmetic sequences."""
    d1, d2 = 3, 5
    a1, a2 = random.randint(1, 3), random.randint(2, 5)
    # Common terms form an AP with difference lcm(d1,d2)
    lcm = d1 * d2 // math.gcd(d1, d2)
    # First common term: smallest n>=1 such that (a1+(n-1)d1) appears in seq 2
    for val in [a1 + k * d1 for k in range(0, 100)]:
        if (val - a2) % d2 == 0 and (val - a2) // d2 >= 0:
            first_common = val
            break
    else:
        first_common = a1  # fallback
    q = (rf"Sequence A: {a1}, {a1+d1}, {a1+2*d1}, ...<br>"
         rf"Sequence B: {a2}, {a2+d2}, {a2+2*d2}, ...<br>"
         rf"Find the first number that appears in both sequences.")
    s = (rf"Sequence A has nth term \({d1}n + {a1-d1}\); Sequence B has nth term \({d2}n + {a2-d2}\).<br>"
         rf"Common terms share a difference of \(\text{{lcm}}({d1},{d2}) = {lcm}\).<br>"
         rf"Checking terms of A: {', '.join(str(a1+k*d1) for k in range(15))}...<br>"
         rf"<strong>First common term is {first_common}.</strong>")
    hint = "List terms of both sequences and find the first one they share."
    return q, s, hint, 3, first_common


def _seq_inter_pattern_dots():
    # Pattern: each shape has an² + bn + c dots, n starting at 1
    # Simple: a=1, b=1 → shape n has n²+n = n(n+1) dots
    n_val = random.randint(6, 10)
    ans = n_val * (n_val + 1)
    q = (rf"A sequence of dot patterns: shape 1 has 2 dots, shape 2 has 6 dots, shape 3 has 12 dots.<br>"
         rf"The pattern follows \(n(n+1)\). How many dots does shape {n_val} have?")
    s = (rf"Formula: \(n(n+1)\).<br>"
         rf"Shape {n_val}: \({n_val} \times {n_val+1}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = f"Substitute n = {n_val} into n(n+1)."
    return q, s, hint, 2, ans


def _seq_inter_linear_quadratic_compare():
    d = random.randint(4, 8)
    a = random.randint(d + 2, d + 10)
    # Find first n where n² > dn+a → n²-dn-a>0
    import math
    n_cross = math.ceil((d + math.sqrt(d**2 + 4*a)) / 2)
    q = (rf"Sequence A has nth term \(n^2\). Sequence B has nth term \({d}n + {a}\).<br>"
         rf"Find the smallest value of \(n\) for which the term in sequence A exceeds the term in sequence B.")
    n_test = n_cross
    while n_test**2 <= d*n_test + a:
        n_test += 1
    s = (rf"We need \(n^2 > {d}n + {a}\), i.e. \(n^2 - {d}n - {a} > 0\).<br>"
         rf"Testing values around \(n = {n_test - 1}\): "
         rf"\(n={n_test-1}\): \({(n_test-1)**2}\) vs \({d*(n_test-1)+a}\) — "
         rf"{'A > B' if (n_test-1)**2 > d*(n_test-1)+a else 'A ≤ B'}<br>"
         rf"\(n={n_test}\): \({n_test**2}\) vs \({d*n_test+a}\) — "
         rf"{'A > B ✓' if n_test**2 > d*n_test+a else 'A ≤ B'}<br>"
         rf"<strong>Smallest \(n\) is {n_test}.</strong>")
    hint = f"Set n² > {d}n + {a} and test integer values of n."
    return q, s, hint, 3, n_test


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _seq_diff_quadratic_nth_term():
    """Find nth term of quadratic sequence: an²+bn+c."""
    a_coef = random.randint(1, 3)
    b_coef = random.randint(-4, 4)
    c_coef = random.randint(-3, 5)
    terms = [a_coef*n**2 + b_coef*n + c_coef for n in range(1, 7)]
    seq_str = ", ".join(str(t) for t in terms[:5])
    sign_b = "+" if b_coef >= 0 else "-"
    sign_c = "+" if c_coef >= 0 else "-"
    nth = (f"{a_coef}n^2"
           + (f" + {b_coef}n" if b_coef > 0 else (f" - {-b_coef}n" if b_coef < 0 else ""))
           + (f" + {c_coef}" if c_coef > 0 else (f" - {-c_coef}" if c_coef < 0 else "")))
    d1 = [terms[i+1]-terms[i] for i in range(4)]
    d2 = [d1[i+1]-d1[i] for i in range(3)]
    q = rf"Find the nth term of the sequence: {seq_str}, ..."
    s = (rf"First differences: {', '.join(str(x) for x in d1)}<br>"
         rf"Second differences: {', '.join(str(x) for x in d2)} (constant = {d2[0]})<br>"
         rf"Leading coefficient: \(\dfrac{{{d2[0]}}}{{2}} = {a_coef}\), so \(n^2\) term is \({a_coef}n^2\).<br>"
         rf"Subtract \({a_coef}n^2\) from each term: \({', '.join(str(terms[i]-a_coef*(i+1)**2) for i in range(4))}\) — a linear sequence.<br>"
         rf"Linear part: \({b_coef}n + {c_coef}\).<br>"
         rf"<strong>nth term \(= {nth}\)</strong>")
    hint = "Find second differences ÷ 2 for the n² coefficient, then subtract and find the linear part."
    return q, s, hint, 5


def _seq_diff_quadratic_verify():
    a_coef = random.randint(1, 2)
    b_coef = random.randint(1, 4)
    c_coef = random.randint(-5, -1)
    terms = [a_coef*n**2 + b_coef*n + c_coef for n in range(1, 7)]
    nth = (f"{a_coef}n^2 + {b_coef}n"
           + (f" - {-c_coef}" if c_coef < 0 else f" + {c_coef}"))
    seq_str = ", ".join(str(t) for t in terms[:5])
    n_val = random.randint(10, 20)
    ans = a_coef*n_val**2 + b_coef*n_val + c_coef
    q = (rf"A quadratic sequence starts {seq_str}.<br>"
         rf"(a) Show that the nth term is \({nth}\)<br>"
         rf"(b) Find the {n_val}th term.")
    d1 = [terms[i+1]-terms[i] for i in range(4)]
    d2 = [d1[i+1]-d1[i] for i in range(3)]
    s = (rf"(a) Second differences = {d2[0]}, so leading term is \(\dfrac{{{d2[0]}}}{{2}}n^2 = {a_coef}n^2\).<br>"
         rf"Subtracting \({a_coef}n^2\): gives {', '.join(str(terms[i]-a_coef*(i+1)**2) for i in range(4))}, a linear sequence with \(d={b_coef}\), giving \({b_coef}n + {c_coef}\).<br>"
         rf"Hence nth term \(= {nth}\). ✓<br>"
         rf"(b) \(n = {n_val}\): \({a_coef}({n_val})^2 + {b_coef}({n_val}) + ({c_coef}) = {a_coef*n_val**2} + {b_coef*n_val} - {-c_coef}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = "Use second differences to find the n² coefficient, then subtract to find the linear part."
    return q, s, hint, 5, ans


def _seq_diff_geometric_sum():
    a = random.randint(1, 3)
    r = random.choice([2, 3])
    n = random.randint(6, 10)
    ans = a * (r**n - 1) // (r - 1)
    q = rf"Find the sum of the first {n} terms of the geometric series with first term {a} and common ratio {r}."
    s = (rf"Sum formula: \(S_n = \dfrac{{a(r^n - 1)}}{{r-1}}\)<br>"
         rf"\(S_{{{n}}} = \dfrac{{{a}({r}^{{{n}}} - 1)}}{{{r}-1}} = \dfrac{{{a}({r**n} - 1)}}{{{r-1}}}"
         rf"= \dfrac{{{a*(r**n-1)}}}{{{r-1}}}\)<br>"
         rf"<strong>\(S_{{{n}}} = {ans}\)</strong>")
    hint = "Use Sn = a(rⁿ − 1)/(r − 1) for a geometric series with r ≠ 1."
    return q, s, hint, 4, ans


def _seq_diff_quadratic_is_term():
    a_coef = 1
    b_coef = random.randint(2, 5)
    c_coef = random.randint(-8, -1)
    nth = (f"n^2 + {b_coef}n"
           + (f" - {-c_coef}" if c_coef < 0 else f" + {c_coef}"))
    # choose a value that IS a term
    k = random.randint(10, 20)
    val = k**2 + b_coef*k + c_coef
    q = (rf"The nth term of a sequence is \({nth}\)<br>"
         rf"Show algebraically whether {val} is a term in this sequence.")
    s = (rf"Set \({nth} = {val}\):<br>"
         rf"\(n^2 + {b_coef}n + {c_coef} - {val} = 0\)<br>"
         rf"\(n^2 + {b_coef}n + {c_coef - val} = 0\)<br>"
         rf"Using the quadratic formula: \(n = \dfrac{{-{b_coef} \pm \sqrt{{{b_coef}^2 - 4({c_coef-val})}}}}"
         rf"{{2}}\)<br>"
         rf"\(= \dfrac{{-{b_coef} \pm \sqrt{{{b_coef**2 - 4*(c_coef-val)}}}}}{{2}} = \dfrac{{-{b_coef} \pm {int(math.sqrt(b_coef**2 - 4*(c_coef-val)))}}}"
         rf"{{2}}\)<br>"
         rf"\(n = {k}\) or \(n = {-k - b_coef}\) (rejected, not positive).<br>"
         rf"<strong>{val} is the {k}th term.</strong>")
    hint = f"Set {nth} = {val} and solve the quadratic for n."
    return q, s, hint, 5, _seq_keyword_answer('yes')


def _seq_diff_recurring_decimal_proof():
    a_rec = random.randint(1, 8)
    digits = random.randint(1, 3)
    if digits == 1:
        frac = Fraction(a_rec, 9)
        q = (
            rf"Prove, using a sequence argument, that \(0.\overline{{{a_rec}}} = "
            rf"\dfrac{{{frac.numerator}}}{{{frac.denominator}}}\) by selecting the "
            rf"correct proof steps in order."
        )
        s = (
            rf"Let \(x = 0.\overline{{{a_rec}}}\). Then \(10x = {a_rec}.\overline{{{a_rec}}}\).<br>"
            rf"Subtracting: \(9x = {a_rec}\), so \(x = \dfrac{{{a_rec}}}{{9}}\)"
            rf"\(= \dfrac{{{frac.numerator}}}{{{frac.denominator}}}\) ✓"
        )
        bank = [
            {'id': 's1', 'text': rf'Let \(x = 0.\overline{{{a_rec}}}\).'},
            {
                'id': 's2',
                'text': rf'Multiply by 10: \(10x = {a_rec}.\overline{{{a_rec}}}\).',
            },
            {
                'id': 's3',
                'text': (
                    rf'Subtract: \(10x - x = {a_rec}\), so \(9x = {a_rec}\) and '
                    rf'\(x = \dfrac{{{a_rec}}}{{9}}\).'
                ),
            },
            {
                'id': 'd1',
                'text': rf'Multiply by 100: \(100x = {a_rec}.\overline{{{a_rec}}}\).',
            },
            {
                'id': 'd2',
                'text': rf'Conclude \(x = \dfrac{{{a_rec}}}{{10}}\) without subtracting.',
            },
            {
                'id': 'd3',
                'text': 'Treat it as a geometric series with common ratio r = 10.',
            },
        ]
        required = ('s1', 's2', 's3')
    else:
        rec_num = random.randint(10, 99)
        frac = Fraction(rec_num, 99)
        q = (
            rf"Prove that \(0.\overline{{{rec_num}}} = "
            rf"\dfrac{{{frac.numerator}}}{{{frac.denominator}}}\) by selecting the "
            rf"correct proof steps in order."
        )
        s = (
            rf"Let \(x = 0.\overline{{{rec_num}}}\). Then \(100x = {rec_num}.\overline{{{rec_num}}}\).<br>"
            rf"Subtracting: \(99x = {rec_num}\), so "
            rf"\(x = \dfrac{{{rec_num}}}{{99}} = \dfrac{{{frac.numerator}}}{{{frac.denominator}}}\) ✓"
        )
        bank = [
            {'id': 's1', 'text': rf'Let \(x = 0.\overline{{{rec_num}}}\).'},
            {
                'id': 's2',
                'text': rf'Multiply by 100: \(100x = {rec_num}.\overline{{{rec_num}}}\).',
            },
            {
                'id': 's3',
                'text': (
                    rf'Subtract: \(100x - x = {rec_num}\), so \(99x = {rec_num}\) and '
                    rf'\(x = \dfrac{{{rec_num}}}{{99}}\).'
                ),
            },
            {
                'id': 'd1',
                'text': rf'Multiply by 10: \(10x = {rec_num}.\overline{{{rec_num}}}\).',
            },
            {
                'id': 'd2',
                'text': rf'Conclude \(x = \dfrac{{{rec_num}}}{{9}}\) after subtracting.',
            },
            {
                'id': 'd3',
                'text': 'Treat it as an arithmetic series with common difference 0.01.',
            },
        ]
        required = ('s1', 's2', 's3')
    hint = (
        "Let x = the recurring decimal. Multiply by a power of 10 to shift it, "
        "then subtract to eliminate the recurring part."
    )
    random.shuffle(bank)
    return q, s, hint, 4, proof_steps_answer(
        required,
        bank,
        order_matters=True,
        format_hint='Select the correct proof steps in order',
    )


def _seq_diff_sum_formula_derive():
    n = random.randint(15, 25)
    a = random.randint(3, 10)
    d = random.randint(2, 6)
    l = a + (n-1)*d
    ans = n*(a+l)//2
    q = (rf"An arithmetic series has first term {a}, last term {l}, and {n} terms.<br>"
         rf"(a) Derive the formula \(S_n = \dfrac{{n(a+l)}}{{2}}\) by pairing terms.<br>"
         rf"(b) Use the formula to find \(S_{{{n}}}\)")
    s = (rf"(a) Write the sum forwards and backwards:<br>"
         rf"\(S = a + (a+d) + \ldots + l\)<br>"
         rf"\(S = l + (l-d) + \ldots + a\)<br>"
         rf"Adding: \(2S = n(a+l)\), so \(S = \dfrac{{n(a+l)}}{{2}}\). ✓<br>"
         rf"(b) \(S_{{{n}}} = \dfrac{{{n}({a}+{l})}}{{2}} = \dfrac{{{n} \times {a+l}}}{{2}}\)<br>"
         rf"<strong>\(S_{{{n}}} = {ans}\)</strong>")
    hint = "For part (a), write the sum twice (forwards and backwards) and add them together."
    return q, s, hint, 5, ans


def _seq_diff_geometric_infinite_sum():
    a = random.randint(2, 8)
    r_num = random.choice([1, 1, 2, 3])
    r_den = random.choice([2, 3, 4])
    while r_num >= r_den:
        r_num = random.randint(1, r_den - 1)
    from fractions import Fraction
    r = Fraction(r_num, r_den)
    ans = Fraction(a, 1 - r)
    q = (rf"A geometric series has first term {a} and common ratio \(\dfrac{{{r_num}}}{{{r_den}}}\)<br>"
         rf"Find the sum to infinity.")
    s = (rf"Since \(|r| = \dfrac{{{r_num}}}{{{r_den}}} < 1\), the series converges.<br>"
         rf"\(S_\infty = \dfrac{{a}}{{1-r}} = \dfrac{{{a}}}{{1 - \dfrac{{{r_num}}}{{{r_den}}}}} = \dfrac{{{a}}}{{\dfrac{{{r_den - r_num}}}{{{r_den}}}}} = {a} \times \dfrac{{{r_den}}}{{{r_den - r_num}}}\)<br>"
         rf"<strong>\(S_\infty = {ans}\)</strong>")
    hint = "Use S∞ = a/(1 − r), valid when |r| < 1."
    return q, s, hint, 4, ans


def _seq_diff_quadratic_seq_prove():
    a_coef = random.randint(1, 2)
    b_coef = random.randint(1, 3)
    c_coef = random.randint(-5, 5)
    nth = (f"{a_coef}n^2"
           + (f" + {b_coef}n" if b_coef > 0 else "")
           + (f" + {c_coef}" if c_coef > 0 else (f" - {-c_coef}" if c_coef < 0 else "")))
    val_k = random.randint(10, 20)
    term_k = a_coef*val_k**2 + b_coef*val_k + c_coef
    q = (rf"The nth term of a sequence is \(u_n = {nth}\)<br>"
         rf"(a) Find \(u_{{{val_k}}}\)<br>"
         rf"(b) Show that the second difference is constant and state its value.")
    s = (rf"(a) \(u_{{{val_k}}} = {a_coef}({val_k})^2 + {b_coef}({val_k}) + {c_coef}"
         rf" = {a_coef*val_k**2} + {b_coef*val_k} + {c_coef}\)<br>"
         rf"<strong>\(u_{{{val_k}}} = {term_k}\)</strong><br>"
         rf"(b) \(u_{{n+1}} - u_n = {a_coef}(n+1)^2 + {b_coef}(n+1) + {c_coef} - ({nth})\)<br>"
         rf"\(= {a_coef}(2n+1) + {b_coef} = {2*a_coef}n + {a_coef + b_coef}\) (first difference)<br>"
         rf"Second difference: \(({2*a_coef}(n+1) + {a_coef+b_coef}) - ({2*a_coef}n + {a_coef+b_coef}) = {2*a_coef}\)<br>"
         rf"<strong>Constant second difference = {2*a_coef}.</strong>")
    hint = "For part (b), find uₙ₊₁ − uₙ (first difference), then find the first difference of that (second difference)."
    return q, s, hint, 5, term_k


def _seq_diff_arithmetic_mean():
    a = random.randint(5, 15)
    d = random.randint(3, 7)
    n = random.randint(20, 40)
    terms = [a + d*i for i in range(n)]
    mean = sum(terms) / n
    ans = a + (n-1)*d/2
    q = (rf"An arithmetic sequence has first term {a}, common difference {d}, and {n} terms.<br>"
         rf"Show that the mean of the sequence equals \(\dfrac{{a+l}}{{2}}\) and find the mean.")
    l = a + (n-1)*d
    s = (rf"Sum \(S_n = \dfrac{{n(a+l)}}{{2}}\).<br>"
         rf"Mean \(= \dfrac{{S_n}}{{n}} = \dfrac{{n(a+l)/2}}{{n}} = \dfrac{{a+l}}{{2}}\). ✓<br>"
         rf"Last term: \(l = {a} + {n-1} \times {d} = {l}\)<br>"
         rf"Mean \(= \dfrac{{{a}+{l}}}{{2}} = \dfrac{{{a+l}}}{{2}}\)<br>"
         rf"<strong>Mean \(= {Fraction(a+l, 2)}\)</strong>")
    hint = "Mean = Sn / n. Substitute Sn = n(a+l)/2 and simplify."
    return q, s, hint, 4, Fraction(a + l, 2)


def _seq_diff_show_divisible():
    q = (
        r"Prove that every term of the sequence with nth term \(n(n+1)\) is divisible by 2 "
        r"by selecting the correct proof steps in order."
    )
    s = (
        r"Every pair of consecutive integers \(n\) and \(n+1\) contains one even and one odd.<br>"
        r"Therefore their product \(n(n+1)\) is always even (divisible by 2).<br>"
        r"Alternatively: \(n(n+1) = 2 \times \dfrac{n(n+1)}{2}\) where "
        r"\(\dfrac{n(n+1)}{2}\) is always an integer (the \(n\)th triangle number).<br>"
        r"<strong>Hence \(n(n+1)\) is divisible by 2 for all positive integers \(n\).</strong>"
    )
    hint = "Consider whether n and n+1 are even/odd. One of any two consecutive integers must be even."
    bank = [
        {
            'id': 's1',
            'text': 'n and n+1 are consecutive integers, so one is even and one is odd.',
        },
        {
            'id': 's2',
            'text': 'The product of an even integer and any integer is even.',
        },
        {
            'id': 's3',
            'text': 'Therefore n(n+1) is always divisible by 2.',
        },
        {
            'id': 'd1',
            'text': 'n and n+1 are both always odd, so their product is odd.',
        },
        {
            'id': 'd2',
            'text': 'n(n+1) is only even when n is a multiple of 3.',
        },
        {
            'id': 'd3',
            'text': 'Use the geometric series formula for Sn to show divisibility.',
        },
    ]
    random.shuffle(bank)
    return q, s, hint, 4, proof_steps_answer(
        ('s1', 's2', 's3'),
        bank,
        order_matters=True,
        format_hint='Select the correct proof steps in order',
    )


def _seq_diff_find_a_and_d():
    a = random.randint(5, 20)
    d = random.randint(3, 8)
    t3 = a + 2*d
    t7 = a + 6*d
    q = (rf"In an arithmetic sequence, the 3rd term is {t3} and the 7th term is {t7}.<br>"
         rf"Find the first term and the common difference.")
    s = (rf"Let the first term be \(a\) and common difference \(d\).<br>"
         rf"\(a + 2d = {t3} \quad (1)\)<br>"
         rf"\(a + 6d = {t7} \quad (2)\)<br>"
         rf"Subtract (1) from (2): \(4d = {t7 - t3}\), so \(d = {d}\).<br>"
         rf"From (1): \(a = {t3} - 2({d}) = {t3 - 2*d}\).<br>"
         rf"<strong>First term \(a = {a}\), common difference \(d = {d}\).</strong>")
    hint = "Write two simultaneous equations using the nth-term formula a + (n−1)d."
    return q, s, hint, 4, _seq_fields_answer((a, d), ("First term a", "Common difference d"))


def _seq_diff_sum_of_squares():
    n = random.randint(8, 15)
    ans = n*(n+1)*(2*n+1)//6
    q = (rf"Use the result \(\displaystyle\sum_{{k=1}}^{{n}} k^2 = \dfrac{{n(n+1)(2n+1)}}{{6}}\) "
         rf"to find \(\displaystyle\sum_{{k=1}}^{{{n}}} k^2\)")
    s = (rf"Substitute \(n = {n}\):<br>"
         rf"\(\dfrac{{{n} \times {n+1} \times {2*n+1}}}{{6}} = \dfrac{{{n*(n+1)*(2*n+1)}}}{{6}}\)<br>"
         rf"<strong>\(= {ans}\)</strong>")
    hint = f"Substitute n = {n} directly into the formula n(n+1)(2n+1)/6."
    return q, s, hint, 2, ans


def _seq_diff_nth_term_with_fractions():
    """Sequences with fractional nth terms, e.g. n/(n+1) or (2n-1)/(2n+1)."""
    variant = random.choice(['type_a', 'type_b'])
    n_val = random.randint(8, 15)
    if variant == 'type_a':
        # n/(n+1): terms are 1/2, 2/3, 3/4, ...
        fracs = [Fraction(k, k + 1) for k in range(1, 5)]
        terms_display = rf"\({', '.join(
            rf'\dfrac{{{f.numerator}}}{{{f.denominator}}}' for f in fracs
        )}\)"
        ans_num, ans_den = n_val, n_val + 1
        q = (rf"A sequence starts: {terms_display}<br>"
             rf"(a) Write down the nth term.<br>"
             rf"(b) Find the {n_val}th term.")
        s = (rf"(a) Numerators: 1, 2, 3, 4, ... \(= n\). Denominators: 2, 3, 4, 5, ... \(= n+1\).<br>"
             rf"<strong>nth term \(= \dfrac{{n}}{{n+1}}\)</strong><br>"
             rf"(b) \(n = {n_val}\): \(\dfrac{{{n_val}}}{{{n_val+1}}}\)<br>"
             rf"<strong>\(= \dfrac{{{ans_num}}}{{{ans_den}}}\)</strong>")
    else:
        # (2n-1)/(2n+1): terms are 1/3, 3/5, 5/7, ...
        fracs = [Fraction(2*k - 1, 2*k + 1) for k in range(1, 5)]
        terms_display = rf"\({', '.join(
            rf'\dfrac{{{f.numerator}}}{{{f.denominator}}}' for f in fracs
        )}\)"
        ans_num, ans_den = 2*n_val - 1, 2*n_val + 1
        q = (rf"A sequence starts: {terms_display}, ...<br>"
             rf"(a) Write down the nth term.<br>"
             rf"(b) Find the {n_val}th term.")
        s = (rf"(a) Numerators: 1, 3, 5, 7, ... \(= 2n-1\). Denominators: 3, 5, 7, 9, ... \(= 2n+1\).<br>"
             rf"<strong>nth term \(= \dfrac{{2n-1}}{{2n+1}}\)</strong><br>"
             rf"(b) \(n = {n_val}\): \(\dfrac{{2({n_val})-1}}{{2({n_val})+1}} = \dfrac{{{ans_num}}}{{{ans_den}}}\)<br>"
             rf"<strong>\(= \dfrac{{{ans_num}}}{{{ans_den}}}\)</strong>")
    hint = "Look at numerators and denominators separately and express each as a formula in n."
    return q, s, hint, 3, f"{ans_num}/{ans_den}"


def _seq_diff_convergence_check():
    a = random.randint(3, 10)
    r_num = random.choice([1, 2, 3])
    r_den = random.choice([3, 4, 5])
    while r_num >= r_den:
        r_num = 1
    r = Fraction(r_num, r_den)
    s_inf = Fraction(a, 1 - r)
    n_finite = random.randint(5, 8)
    q = (rf"A geometric series has first term {a} and common ratio \(\dfrac{{{r_num}}}{{{r_den}}}\)<br>"
         rf"(a) Explain why the series converges.<br>"
         rf"(b) Find \(S_\infty\)<br>"
         rf"(c) Find the smallest value of n such that \(S_n > {int(0.99 * s_inf)}\)")
    target = int(0.99 * s_inf)
    # S_n = a(1-r^n)/(1-r) > target
    # 1-r^n > target*(1-r)/a
    lhs_coef = float(s_inf)
    import math
    ratio = float(r)
    n_ans = math.ceil(math.log(1 - target / lhs_coef) / math.log(ratio)) if ratio > 0 else n_finite
    s = (rf"(a) \(|r| = \dfrac{{{r_num}}}{{{r_den}}} < 1\) so the series converges.<br>"
         rf"(b) \(S_\infty = \dfrac{{{a}}}{{1 - \frac{{{r_num}}}{{{r_den}}}}} = \dfrac{{{a}}}{{\frac{{{r_den-r_num}}}{{{r_den}}}}} = {a} \times \dfrac{{{r_den}}}{{{r_den-r_num}}} = {s_inf}\)<br>"
         rf"<strong>\(S_\infty = {s_inf}\)</strong><br>"
         rf"(c) \(S_n = {a} \times \dfrac{{1 - ({r_num}/{r_den})^n}}{{1 - {r_num}/{r_den}}}\) Try \(n = {n_ans}\)<br>"
         rf"Test values until \(S_n > {target}\). <strong>Smallest \(n = {n_ans}\)</strong>")
    hint = "Use S∞ = a/(1−r) for part (b). For part (c), use Sn = a(1−rⁿ)/(1−r) and try values of n."
    return q, s, hint, 5, _seq_fields_answer((s_inf, int(n_ans)), ("Sum to infinity", "Smallest n"))


def _seq_diff_arithmetic_proof():
    q = (
        r"Prove that the sum of the first \(n\) odd numbers equals \(n^2\) "
        r"by selecting the correct proof steps in order."
    )
    s = (
        r"The first \(n\) odd numbers are \(1, 3, 5, \ldots, (2n-1)\).<br>"
        r"This is an arithmetic series with \(a = 1\), \(l = 2n-1\), and \(n\) terms.<br>"
        r"Sum \(= \dfrac{n(a+l)}{2} = \dfrac{n(1 + 2n-1)}{2} = \dfrac{n \cdot 2n}{2} = n^2\)<br>"
        r"<strong>Therefore the sum of the first \(n\) odd numbers is \(n^2\). ✓</strong>"
    )
    hint = "Recognise the odd numbers as an AP with a = 1, d = 2. Use Sn = n(a + l)/2."
    bank = [
        {
            'id': 's1',
            'text': 'The first n odd numbers form an AP with a = 1 and d = 2 (last term l = 2n − 1).',
        },
        {
            'id': 's2',
            'text': 'Use the AP sum formula Sn = n(a + l)/2.',
        },
        {
            'id': 's3',
            'text': 'Substitute: Sn = n(1 + 2n − 1)/2 = n(2n)/2 = n².',
        },
        {
            'id': 'd1',
            'text': 'Use the geometric series formula Sn = a(1 − rⁿ)/(1 − r).',
        },
        {
            'id': 'd2',
            'text': 'The first n odd numbers form an AP with a = 0 and d = 1.',
        },
        {
            'id': 'd3',
            'text': 'Conclude that the sum equals 2n without using a sum formula.',
        },
    ]
    random.shuffle(bank)
    return q, s, hint, 4, proof_steps_answer(
        ('s1', 's2', 's3'),
        bank,
        order_matters=True,
        format_hint='Select the correct proof steps in order',
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (18 questions)
# ══════════════════════════════════════════════════════════════════════════════

_SEQ_MCQ_BANK = [
    {
        "q": r"The nth term of a sequence is \(3n + 5\). What is the 10th term?",
        "opts": ["A  35", "B  38", "C  30", "D  40"],
        "ans": "A",
        "sol": r"\(3(10) + 5 = 30 + 5 = 35\).",
    },
    {
        "q": r"Which of the following is the nth term of the sequence 5, 8, 11, 14, ...?",
        "opts": [r"A  \(3n + 2\)", r"B  \(3n + 5\)", r"C  \(n + 4\)", r"D  \(4n + 1\)"],
        "ans": "A",
        "sol": r"Common difference = 3. First term = 5. nth term \(= 5 + (n-1) \times 3 = 3n + 2\).",
    },
    {
        "q": r"What is the sum of the arithmetic series \(2 + 5 + 8 + \ldots + 29\)?",
        "opts": ["A  155", "B  150", "C  145", "D  160"],
        "ans": "A",
        "sol": r"\(n = 10\) terms (since \(a=2\), \(d=3\), \(l=29\)). \(S_{10} = \frac{10(2+29)}{2} = 5 \times 31 = 155\).",
    },
    {
        "q": r"The sequence 4, 8, 16, 32, ... is geometric. What is the 6th term?",
        "opts": ["A  128", "B  64", "C  256", "D  512"],
        "ans": "A",
        "sol": r"\(a = 4\), \(r = 2\). 6th term \(= 4 \times 2^5 = 4 \times 32 = 128\).",
    },
    {
        "q": r"The second differences of a sequence are all equal to 4. What is the coefficient of \(n^2\) in the nth term?",
        "opts": ["A  2", "B  4", "C  1", "D  8"],
        "ans": "A",
        "sol": r"Second difference \(= 2a\) where \(a\) is the \(n^2\) coefficient. So \(a = 4 \div 2 = 2\).",
    },
    {
        "q": r"Is 97 a term in the sequence with nth term \(4n + 1\)?",
        "opts": ["A  Yes, it is the 24th term", "B  No", "C  Yes, it is the 23rd term", "D  Yes, it is the 25th term"],
        "ans": "A",
        "sol": r"Set \(4n + 1 = 97\): \(4n = 96\), \(n = 24\). Since \(n\) is a positive integer, 97 is the 24th term.",
    },
    {
        "q": r"The first term of a geometric series is 6 and the common ratio is \(\frac{1}{3}\). What is the sum to infinity?",
        "opts": ["A  9", "B  6", "C  18", "D  3"],
        "ans": "A",
        "sol": r"\(S_\infty = \frac{6}{1 - \frac{1}{3}} = \frac{6}{\frac{2}{3}} = 6 \times \frac{3}{2} = 9\).",
    },
    {
        "q": r"The sequence 1, 4, 9, 16, 25 consists of which special numbers?",
        "opts": ["A  Square numbers", "B  Cube numbers", "C  Triangle numbers", "D  Prime numbers"],
        "ans": "A",
        "sol": r"1, 4, 9, 16, 25 are \(1^2, 2^2, 3^2, 4^2, 5^2\) — the square numbers.",
    },
    {
        "q": r"The nth term of a sequence is \(n^2 + 3n - 1\). What is the 5th term?",
        "opts": ["A  39", "B  34", "C  40", "D  29"],
        "ans": "A",
        "sol": r"\(5^2 + 3(5) - 1 = 25 + 15 - 1 = 39\).",
    },
    {
        "q": r"Which arithmetic sequence has nth term \(5 - 2n\)?",
        "opts": ["A  3, 1, −1, −3, ...", "B  5, 3, 1, −1, ...", "C  3, 5, 7, 9, ...", "D  −2, −4, −6, ..."],
        "ans": "A",
        "sol": r"\(n=1\): \(5-2=3\). \(n=2\): \(5-4=1\). \(n=3\): \(5-6=-1\). So 3, 1, −1, −3, ...",
    },
    {
        "q": r"What is \(\displaystyle\sum_{k=1}^{10} k\)?",
        "opts": ["A  55", "B  50", "C  45", "D  60"],
        "ans": "A",
        "sol": r"\(\sum_{k=1}^{10} k = \frac{10 \times 11}{2} = 55\).",
    },
    {
        "q": r"A geometric series has \(a = 8\) and \(r = 0.5\). Which of these is \(S_4\)?",
        "opts": ["A  15", "B  16", "C  14", "D  12"],
        "ans": "A",
        "sol": r"\(S_4 = \frac{8(1-0.5^4)}{1-0.5} = \frac{8 \times 0.9375}{0.5} = \frac{7.5}{0.5} = 15\).",
    },
    {
        "q": r"The 4th term of an arithmetic sequence is 22 and the common difference is 5. What is the first term?",
        "opts": ["A  7", "B  12", "C  17", "D  2"],
        "ans": "A",
        "sol": r"\(a + 3d = 22\), \(d = 5\), so \(a = 22 - 15 = 7\).",
    },
    {
        "q": r"Which of the following sequences has a constant second difference of 6?",
        "opts": [
            r"A  \(3n^2 - n + 1\)",
            r"B  \(n^2 + 3\)",
            r"C  \(6n + 1\)",
            r"D  \(2n^2 - 1\)",
        ],
        "ans": "A",
        "sol": r"Second difference \(= 2 \times\) coefficient of \(n^2\). For \(3n^2\): \(2 \times 3 = 6\). ✓",
    },
    {
        "q": r"The sum of the first \(n\) terms of an arithmetic series is \(S_n = 4n^2 - n\). What is the 3rd term?",
        "opts": ["A  19", "B  27", "C  17", "D  23"],
        "ans": "A",
        "sol": r"\(u_3 = S_3 - S_2 = (4(9)-3) - (4(4)-2) = 33 - 14 = 19\).",
    },
    {
        "q": r"The nth term of a sequence is \(2n^2 + 3n - 2\). What is the 10th term?",
        "opts": ["A  228", "B  218", "C  238", "D  200"],
        "ans": "A",
        "sol": r"\(2(10)^2 + 3(10) - 2 = 200 + 30 - 2 =\) <strong>228</strong>. Answer: A",
        "hint": r"Substitute \(n = 10\) into the nth term formula.",
        "marks": 2,
        "difficulty": "difficult",
    },
    {
        "q": r"A geometric sequence begins 4, 12, 36, 108, ... Which term is the first greater than 1000?",
        "opts": ["A  7th term", "B  6th term", "C  8th term", "D  5th term"],
        "ans": "A",
        "sol": (r"\(a = 4\), \(r = 3\). Term \(= 4 \times 3^{n-1}\).<br>"
                r"\(4 \times 3^5 = 972\), \(4 \times 3^6 = 2916\).<br>"
                r"First term above 1000 is the <strong>7th term</strong>. Answer: A"),
        "hint": "Multiply by the common ratio until the term exceeds 1000.",
        "marks": 3,
        "difficulty": "difficult",
    },
    {
        "q": r"The sum of the first \(n\) terms of a series is \(S_n = 3n^2 + 2n\). What is the 6th term \(u_6\)?",
        "opts": ["A  35", "B  30", "C  40", "D  25"],
        "ans": "A",
        "sol": (r"\(S_6 = 3(36) + 12 = 120\), \(S_5 = 3(25) + 10 = 85\).<br>"
                r"\(u_6 = S_6 - S_5 = 120 - 85 =\) <strong>35</strong>. Answer: A"),
        "hint": r"Use \(u_n = S_n - S_{n-1}\).",
        "marks": 3,
        "difficulty": "difficult",
    },
]


def sequences_mcq():
    chosen = random.choice(_SEQ_MCQ_BANK)
    q = chosen["q"]
    options = chosen["opts"]
    correct = chosen["ans"]
    s = f"<strong>Answer: {correct}</strong><br><br>{chosen['sol']}"
    hint = chosen["sol"]
    return q, s, hint, 1, options, correct


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_sequences_variants(difficulty, mode):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _SEQ_MCQ_BANK, procedural_mcq_for('sequences'), 'sequences', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _seq_found_next_term_arithmetic,
            _seq_found_next_term_subtract,
            _seq_found_identify_rule,
            _seq_found_nth_term_find_terms,
            _seq_found_nth_term_find_value,
            _seq_found_is_term_in_seq,
            _seq_found_term_to_term_rule,
            _seq_found_geometric_next,
            _seq_found_square_numbers,
            _seq_found_triangle_numbers,
            _seq_found_odd_even_seq,
            _seq_found_fibonacci_next,
            _seq_found_missing_term,
            _seq_found_continue_pattern,
            _seq_found_count_patterns,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _seq_inter_find_nth_term,
            _seq_inter_nth_term_negative_d,
            _seq_inter_which_term,
            _seq_inter_not_in_seq,
            _seq_inter_first_term_over,
            _seq_inter_geometric_nth_term,
            _seq_inter_two_sequences_same,
            _seq_inter_sum_arithmetic,
            _seq_inter_quadratic_identify,
            _seq_inter_arithmetic_word,
            _seq_inter_sequences_nth_term_large,
            _seq_inter_nth_term_from_context,
            _seq_inter_common_terms,
            _seq_inter_pattern_dots,
            _seq_inter_linear_quadratic_compare,
        ]
    elif difficulty == 'difficult':
        pool = [
            _seq_diff_quadratic_nth_term,
            _seq_diff_quadratic_verify,
            _seq_diff_geometric_sum,
            _seq_diff_quadratic_is_term,
            _seq_diff_recurring_decimal_proof,
            _seq_diff_sum_formula_derive,
            _seq_diff_geometric_infinite_sum,
            _seq_diff_quadratic_seq_prove,
            _seq_diff_arithmetic_mean,
            _seq_diff_show_divisible,
            _seq_diff_find_a_and_d,
            _seq_diff_sum_of_squares,
            _seq_diff_nth_term_with_fractions,
            _seq_diff_convergence_check,
            _seq_diff_arithmetic_proof,
        ]
    else:  # mixed
        found = random.sample([
            _seq_found_next_term_arithmetic, _seq_found_nth_term_find_terms,
            _seq_found_nth_term_find_value, _seq_found_geometric_next,
            _seq_found_square_numbers, _seq_found_triangle_numbers,
        ], 4)
        inter = random.sample([
            _seq_inter_find_nth_term, _seq_inter_nth_term_negative_d,
            _seq_inter_which_term, _seq_inter_sum_arithmetic,
            _seq_inter_geometric_nth_term, _seq_inter_arithmetic_word,
        ], 4)
        diff = random.sample([
            _seq_diff_quadratic_nth_term, _seq_diff_geometric_infinite_sum,
            _seq_diff_find_a_and_d, _seq_diff_arithmetic_proof,
        ], 2)
        return found + inter + diff

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors exactly)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_sequences(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_sequences_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'sequences',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_sequences_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    out = variant()
    return _seq_problem_from_output(out, difficulty)
