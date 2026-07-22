"""
GCSE Maths – Quadratic Simultaneous Equations
5 foundational · 5 intermediate · 5 difficult · 4 MCQ (randomised each time)

Typical pair: y = x² (parabola) and y = ax + b (straight line).
Graded practice variants return (question, solution, hint, marks, raw).
Conceptual / embedded-MCQ variants stay as 4-tuples.
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_pool,
    run_mcq_variant,
    pick_named_variant,
)


def _fmt_b(b):
    if b > 0:
        return f"+ {b}"
    if b < 0:
        return f"- {abs(b)}"
    return ""


def _fmt_linear(a, b):
    if a == 1:
        return rf"\(y = x {_fmt_b(b)}\)"
    if a == -1:
        return rf"\(y = -x {_fmt_b(b)}\)"
    return rf"\(y = {a}x {_fmt_b(b)}\)"


def _factor_pair(r1, r2):
    f1 = f"(x - {r1})" if r1 > 0 else (f"(x + {abs(r1)})" if r1 < 0 else "(x)")
    f2 = f"(x - {r2})" if r2 > 0 else (f"(x + {abs(r2)})" if r2 < 0 else "(x)")
    return f1, f2


def _qsim_raw(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:g}"
    return str(value)


def _qsim_quadratic_roots_answer(*roots):
    return {'type': 'quadratic_roots', 'roots': tuple(_qsim_raw(r) for r in roots)}


def _qsim_linear_answer(value, var='y'):
    return {'type': 'linear', 'value': _qsim_raw(value), 'var': str(var).strip().lower()}


def _qsim_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_qsim_raw(v) for v in values),
        'labels': tuple(labels),
    }


def _qsim_linear_raw(raw):
    var = raw.get('var') or 'x'
    val = raw.get('value')
    if var == 'x':
        return str(val)
    return f'{var}={val}'


def _qsim_solution_fields(r1, y1, r2, y2):
    return _qsim_fields_answer(
        [r1, y1, r2, y2],
        ['x (1st solution)', 'y (1st solution)', 'x (2nd solution)', 'y (2nd solution)'],
    )


def _qsim_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict):
            raw_type = raw.get('type')
            if raw_type == 'quadratic_roots':
                roots = raw.get('roots') or ()
                extra = {
                    'correct_answer_raw': ','.join(str(r) for r in roots),
                    'answer_type': 'quadratic_roots',
                    'answer_format_hint': 'Enter roots separated by commas (e.g. 3, -2)',
                }
            elif raw_type == 'number_fields':
                values = raw.get('values') or ()
                labels = raw.get('labels') or ()
                if values and len(values) == len(labels):
                    extra = {
                        'correct_answer_raw': '|'.join(str(v) for v in values),
                        'answer_type': 'number_fields',
                        'answer_labels': list(labels),
                        'answer_format_hint': 'Enter a number in every field',
                    }
            elif raw_type == 'linear':
                extra = {
                    'correct_answer_raw': _qsim_linear_raw(raw),
                    'answer_type': 'linear',
                    'answer_format_hint': 'Enter the value (e.g. y = 9 or just 9)',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _qsim_raw(raw),
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
        q, s, hint, difficulty, marks,
        'gcse', 'maths', 'quadratic_simultaneous_equations', **extra
    )


def _roots_from_line(r1=None, r2=None, *, require_a_nonzero=True, require_a_not_one=False):
    """Integer roots r1, r2 for y=x² meeting y=ax+b with a=r1+r2, b=-r1*r2."""
    if r1 is None or r2 is None:
        while True:
            r1 = random.randint(-8, 8)
            r2 = random.randint(-8, 8)
            if r1 == r2 or r1 == 0 or r2 == 0:
                continue
            a = r1 + r2
            if require_a_nonzero and a == 0:
                continue
            if require_a_not_one and a == 1:
                continue
            break
    a = r1 + r2
    b = -r1 * r2
    return r1, r2, a, b


def _roots_positive_pair():
    """Two distinct positive integer roots (e.g. time problems)."""
    while True:
        r1 = random.randint(2, 15)
        r2 = random.randint(2, 15)
        if r1 != r2:
            break
    a = r1 + r2
    b = -r1 * r2
    return r1, r2, a, b


def _roots_with_negative():
    """One negative and one positive root."""
    while True:
        r1 = random.randint(-8, -1)
        r2 = random.randint(1, 8)
        if r1 != r2:
            break
    a = r1 + r2
    b = -r1 * r2
    return r1, r2, a, b


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

def _qsim_f_what_is_intersection():
    q = (
        r"A parabola \(y = x^2\) and a straight line meet at two points on a graph. "
        r"What does each intersection point represent?"
    )
    s = (
        r"Each point is a <strong>pair (x, y)</strong> that satisfies <strong>both</strong> "
        r"equations at the same time — a solution to the simultaneous equations."
    )
    return q, s, "Intersection = simultaneous solution.", 1


_qsim_f_what_is_intersection._fixed_stem = True


def _qsim_f_substitute_step():
    m = random.randint(1, 8)
    c = random.randint(1, 12)
    line = rf"\(y = x + {c}\)" if m == 1 else rf"\(y = {m}x + {c}\)"
    x_term = "x" if m == 1 else f"{m}x"
    q = (
        rf"Solve:<br>\(y = x^2\)<br>{line}<br><br>"
        rf"After substituting the linear equation into the parabola, which equation in <strong>x</strong> do you get?"
    )
    s = (
        rf"Replace \(y\): \(x^2 = {x_term} + {c}\) → rearrange to "
        rf"<strong>\(x^2 - {x_term} - {c} = 0\)</strong>."
    )
    return q, s, "Set x² equal to the expression for y from the line.", 2


def _qsim_f_simple_integer():
    r1, r2, a, b = _roots_from_line()
    y1, y2 = r1 * r1, r2 * r2
    q = rf"Solve:<br>\(y = x^2\)<br>{_fmt_linear(a, b)}"
    f1, f2 = _factor_pair(r1, r2)
    s = (
        rf"Substitute: \(x^2 = {a}x {_fmt_b(b)}\) → factorise {f1}{f2} = 0<br>"
        rf"\(x = {r1}\) or \(x = {r2}\)<br>"
        rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>"
    )
    return q, s, "Substitute, rearrange to zero, factorise, find y from either equation.", 3, _qsim_solution_fields(r1, y1, r2, y2)


def _qsim_f_find_y_given_x():
    r1, r2, a, b = _roots_from_line()
    x_val = random.choice([r1, r2])
    y_val = x_val * x_val
    q = (
        rf"\(y = x^2\) and {_fmt_linear(a, b)} have a solution with \(x = {x_val}\). "
        rf"What is the corresponding <strong>\(y\)</strong>?"
    )
    s = rf"Substitute \(x = {x_val}\): \(y = {x_val}^2 = <strong>{y_val}</strong> (matches the line too)."
    return q, s, "Both equations give the same y when x is a true solution.", 2, _qsim_linear_answer(y_val, 'y')


def _qsim_f_rearrange_only():
    m = random.randint(2, 9)
    c = random.randint(1, 15)
    q = (
        rf"Solve:<br>\(y = x^2\)<br>\(y = {m}x + {c}\)<br><br>"
        rf"Write the quadratic equation in <strong>x</strong> after substitution (equal to 0)."
    )
    s = rf"\(x^2 = {m}x + {c}\) → <strong>\(x^2 - {m}x - {c} = 0\)</strong>."
    return q, s, "Move all terms to one side before factorising.", 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _qsim_i_full_solve():
    r1, r2, a, b = _roots_from_line()
    y1, y2 = r1 * r1, r2 * r2
    q = rf"Solve the simultaneous equations:<br>\(y = x^2\)<br>{_fmt_linear(a, b)}"
    f1, f2 = _factor_pair(r1, r2)
    c_rearr = _fmt_b(-b)
    x_term = "x" if a == 1 else f"{a}x"
    s = (
        rf"Substitute into \(y = x^2\):<br>"
        rf"\(x^2 = {x_term} {_fmt_b(b)}\)<br>"
        rf"Rearrange: \(x^2 - {x_term} {c_rearr} = 0\)<br>"
        rf"Factorise: \({f1}{f2} = 0\)<br>"
        rf"\(x = {r1}\) or \(x = {r2}\)<br>"
        rf"When \(x = {r1}\), \(y = {y1}\). When \(x = {r2}\), \(y = {y2}\)<br>"
        rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>"
    )
    return q, s, "Substitute the line into the parabola, factorise, then find both y-values.", 4, _qsim_solution_fields(r1, y1, r2, y2)


def _qsim_i_find_x_only():
    r1, r2, a, b = _roots_from_line()
    q = (
        rf"Solve:<br>\(y = x^2\)<br>{_fmt_linear(a, b)}<br><br>"
        rf"Find all possible values of <strong>x</strong>."
    )
    s = rf"Factorise after substitution → <strong>\(x = {r1}\) or \(x = {r2}\)</strong>."
    return q, s, "Solve the quadratic in x first; y comes afterwards.", 3, _qsim_quadratic_roots_answer(r1, r2)


def _qsim_i_graph_meaning():
    from generators.gcse.graphical_simultaneous_equations import (
        _svg_parabola_line,
        _fmt_line_eq,
    )
    r1, r2, a, b = _roots_from_line()
    svg = _svg_parabola_line(r1, r2, a, b, mark="none")
    q = (
        rf"The graphs of \(y = x^2\) and {_fmt_line_eq(a, b)} are shown below.<br>{svg}<br>"
        r"How many <strong>simultaneous solutions</strong> are there?"
    )
    s = r"Two intersections on the graph → <strong>2 solutions</strong> (two (x, y) pairs)."
    return q, s, "Each intersection is one (x, y) solution pair.", 1, 2


def _qsim_i_steeper_line():
    r1, r2, a, b = _roots_from_line(require_a_not_one=True)
    y1, y2 = r1 * r1, r2 * r2
    q = rf"Solve:<br>\(y = x^2\)<br>{_fmt_linear(a, b)}"
    f1, f2 = _factor_pair(r1, r2)
    s = (
        rf"Substitute, factorise \({f1}{f2} = 0\)<br>"
        rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>"
    )
    return q, s, "Same method when the line has gradient ≠ 1.", 4, _qsim_solution_fields(r1, y1, r2, y2)


def _qsim_i_check_pair():
    r1, r2, a, b = _roots_from_line()
    correct = random.choice([r1, r2])
    wrong_x = r1 + r2 if r1 + r2 not in (r1, r2, 0) else r2 + 1
    wrong_on_parabola = (wrong_x, wrong_x * wrong_x)
    wrong_on_line = (1, a + b)
    neither = (0, 1)
    q = (
        rf"Which point lies on <strong>both</strong> \(y = x^2\) and {_fmt_linear(a, b)}?<br>"
        rf"A) \({wrong_on_parabola[0]}, {wrong_on_parabola[1]}\) &nbsp; "
        rf"B) \(({correct}, {correct*correct})\) &nbsp; "
        rf"C) \({wrong_on_line[0]}, {wrong_on_line[1]}\) &nbsp; "
        rf"D) \({neither[0]}, {neither[1]}\)"
    )
    s = rf"Check substitution — <strong>B \(({correct}, {correct*correct})\)</strong> satisfies both."
    return q, s, "Substitute x and y into both equations.", 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (5)
# ══════════════════════════════════════════════════════════════════════════════

def _qsim_d_non_monic_line():
    r1, r2, a, b = _roots_from_line(require_a_not_one=True)
    y1, y2 = r1 * r1, r2 * r2
    q = rf"Solve:<br>\(y = x^2\)<br>{_fmt_linear(a, b)}"
    f1, f2 = _factor_pair(r1, r2)
    s = (
        rf"\(x^2 = {a}x {_fmt_b(b)}\) → \({f1}{f2} = 0\)<br>"
        rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>"
    )
    return q, s, "Works the same when the line has coefficient ≠ 1.", 4, _qsim_solution_fields(r1, y1, r2, y2)


def _qsim_d_exam_multipart():
    r1, r2, a, b = _roots_from_line()
    y1, y2 = r1 * r1, r2 * r2
    f1, f2 = _factor_pair(r1, r2)
    q = (
        rf"Solve:<br>\(y = x^2\) &nbsp; (1)<br>{_fmt_linear(a, b)} &nbsp; (2)<br><br>"
        rf"<strong>(a)</strong> Show that substituting (2) into (1) gives \(x^2 - {a}x {_fmt_b(-b)} = 0\).<br>"
        rf"<strong>(b)</strong> Hence solve the simultaneous equations."
    )
    s = (
        rf"<strong>(a)</strong> \(x^2 = {a}x {_fmt_b(b)}\) rearranges correctly.<br>"
        rf"<strong>(b)</strong> \({f1}{f2} = 0\) → "
        rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>"
    )
    return q, s, "Part (a) is method marks for correct substitution and rearrangement.", 5, _qsim_solution_fields(r1, y1, r2, y2)


def _qsim_d_discriminant():
    """How many intersections from discriminant of x² - ax - b = 0."""
    r1, r2, a, b = _roots_from_line()
    disc = a * a + 4 * b  # x² - ax - b = 0, Δ = a² + 4b
    q = (
        rf"The line {_fmt_linear(a, b)} meets \(y = x^2\). "
        rf"The quadratic \(x^2 - {a}x {_fmt_b(-b)} = 0\) has discriminant \(\Delta = {disc}\). "
        rf"How many real points of intersection are there?"
    )
    n = 2 if disc > 0 else (1 if disc == 0 else 0)
    s = rf"\(\Delta > 0\) → <strong>{n} intersection points</strong> (two solutions)."
    return q, s, "Positive discriminant → two distinct real roots for x.", 3, n


def _qsim_d_word_problem():
    r1, r2, a, b = _roots_positive_pair()
    q = (
        r"A ball is thrown. Its height \(h\) metres after \(t\) seconds is modelled by "
        rf"\(h = t^2\) for part of the flight. A platform edge is at height \(h = {a}t {_fmt_b(b)}\). "
        r"When is the ball level with the platform edge? (Solve for \(t\).)"
    )
    f1, f2 = _factor_pair(r1, r2)
    s = (
        rf"Set \(t^2 = {a}t {_fmt_b(b)}\) → \({f1}{f2} = 0\)<br>"
        rf"<strong>\(t = {r1}\) s or \(t = {r2}\) s</strong>"
    )
    return q, s, "Same structure: quadratic meets linear.", 4, _qsim_quadratic_roots_answer(r1, r2)


def _qsim_d_negative_root():
    r1, r2, a, b = _roots_with_negative()
    y1, y2 = r1 * r1, r2 * r2
    q = rf"Solve:<br>\(y = x^2\)<br>{_fmt_linear(a, b)}"
    f1, f2 = _factor_pair(r1, r2)
    s = (
        rf"\({f1}{f2} = 0\) → \(x = {r1}\) or \(x = {r2}\)<br>"
        rf"<strong>\(({r1}, {y1})\) and \(({r2}, {y2})\)</strong>"
    )
    return q, s, "Include negative x-values when they factorise cleanly.", 4, _qsim_solution_fields(r1, y1, r2, y2)


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (4 procedural — randomised)
# ══════════════════════════════════════════════════════════════════════════════

def _qsim_mcq_substitution_equation():
    c = random.randint(1, 7)
    wrong = [
        rf"\(x^2 + x - {c} = 0\)",
        rf"\(x^2 + x + {c} = 0\)",
        rf"\(2x^2 - x - {c} = 0\)",
    ]
    correct = rf"\(x^2 - x - {c} = 0\)"
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"Substitute \(y = x + {c}\) into \(y = x^2\). The equation in \(x\) is:"
    sol = rf"\(x^2 = x + {c}\) → <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Rearrange so one side is zero.", 2, opts, correct_letter


def _qsim_mcq_correct_pair():
    r1, r2, a, b = _roots_from_line()
    y1, y2 = r1 * r1, r2 * r2
    correct = f"({r1}, {y1})"
    wrong = [
        f"({r2}, {y1})",
        f"({r1}, {r2})",
        f"({r1 + r2}, {(r1 + r2) ** 2})",
    ]
    pairs = wrong + [correct]
    random.shuffle(pairs)
    letters = "ABCD"
    correct_letter = letters[pairs.index(correct)]
    opts = [f"{letters[i]}  {pairs[i]}" for i in range(4)]
    q = rf"One solution of \(y = x^2\) and {_fmt_linear(a, b)} is:"
    sol = f"Check both equations — <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "y must equal x² and also ax + b.", 2, opts, correct_letter


def _qsim_mcq_number_of_solutions():
    # random line: two intersections if discriminant > 0
    r1, r2 = random.randint(-3, -1), random.randint(3, 7)
    a, b = r1 + r2, -r1 * r2
    disc = a * a + 4 * b
    n = 2 if disc > 0 else 1
    correct = str(n)
    wrong = [str(x) for x in {0, 1, 2, 3} - {n}][:3]
    vals = wrong + [correct]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct)]
    opts = [f"{letters[i]}  {v}" for i, v in enumerate(vals)]
    q = rf"How many solutions do \(y = x^2\) and {_fmt_linear(a, b)} have?"
    sol = f"<strong>{n}</strong> (discriminant of quadratic in x). Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Two distinct x-values → two (x, y) solutions.", 2, opts, correct_letter


def _qsim_mcq_find_x():
    r1, r2, a, b = _roots_from_line()
    correct_x = random.choice([r1, r2])
    wrong = [r1 + r2, r1 - r2, -correct_x, correct_x + 1]
    wrong = list(dict.fromkeys(w for w in wrong if w != correct_x))[:3]
    vals = wrong + [correct_x]
    random.shuffle(vals)
    letters = "ABCD"
    correct_letter = letters[vals.index(correct_x)]
    opts = [f"{letters[i]}  x = {v}" for i, v in enumerate(vals)]
    q = rf"Solve \(y = x^2\) and {_fmt_linear(a, b)}. One value of \(x\) is:"
    sol = rf"Solutions \(x = {r1}\) or \(x = {r2}\). Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Factorise the quadratic after substituting.", 2, opts, correct_letter


_QSIM_MCQ_POOL = [
    _qsim_mcq_substitution_equation,
    _qsim_mcq_correct_pair,
    _qsim_mcq_number_of_solutions,
    _qsim_mcq_find_x,
]


def _qsim_mcq_dispatch():
    return random.choice(_QSIM_MCQ_POOL)()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _qsim_f_what_is_intersection,
    _qsim_f_substitute_step,
    _qsim_f_simple_integer,
    _qsim_f_find_y_given_x,
    _qsim_f_rearrange_only,
]

_INTERMEDIATE = [
    _qsim_i_full_solve,
    _qsim_i_find_x_only,
    _qsim_i_graph_meaning,
    _qsim_i_steeper_line,
    _qsim_i_check_pair,
]

_DIFFICULT = [
    _qsim_d_non_monic_line,
    _qsim_d_exam_multipart,
    _qsim_d_discriminant,
    _qsim_d_word_problem,
    _qsim_d_negative_root,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_quadratic_simultaneous_equations_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_pool(
            _QSIM_MCQ_POOL, "quadratic_simultaneous_equations", difficulty, count=4
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


def gcse_quadratic_simultaneous_equations(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_quadratic_simultaneous_equations_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "quadratic_simultaneous_equations",
            options=opts, correct_answer=ans,
        )

    variants = gcse_quadratic_simultaneous_equations_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    return _qsim_problem_from_output(variant(), difficulty)
