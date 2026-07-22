"""
GCSE Maths – Changing the Subject
8 foundational · 10 intermediate · 10 difficult · 12 MCQ types (randomised each time)
Graded practice variants return (question, solution, hint, marks, raw).
The first-step MCQ variant stays as a 4-tuple.
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_pool,
    run_mcq_variant,
    pick_named_variant,
)


def _q_make(subject, formula):
    return rf"Make <strong>\({subject}\)</strong> the subject of the formula \({formula}\)."


def _frac(n, d):
    if d == 1:
        return str(n)
    return rf"\dfrac{{{n}}}{{{d}}}"


def _sqrt_tex(expr):
    """Wrap LaTeX expression in \\sqrt{...} without nested f-string brace errors."""
    return rf"\sqrt{{{expr}}}"


def _subj_frac(num, den):
    if den == 1:
        return str(num)
    return f'({num})/({den})'


def _subj_sqrt(inner):
    return f'√({inner})'


def _subj_formula(subject, rhs):
    return f'{subject}={rhs}'


def _subj_algebraic_answer(expr, format_hint=None):
    payload = {'type': 'algebraic', 'value': str(expr)}
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _subj_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'algebraic':
            text = str(raw.get('value') or '')
            extra = {
                'correct_answer_raw': text,
                'answer_type': 'algebraic',
                'answer_format_hint': raw.get(
                    'format_hint',
                    'Enter the rearranged formula, e.g. x = (y - 3)/2',
                ),
            }
    return make_problem(
        q, s, hint, difficulty, marks,
        'gcse', 'maths', 'changing_the_subject', **extra
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (5)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_f_one_step_add():
    a = random.randint(2, 9)
    if random.choice([True, False]):
        q = _q_make("u", rf"v = u + {a}t")
        s = (
            rf"Subtract \({a}t\) from both sides:<br>"
            rf"<strong>\(u = v - {a}t\)</strong>"
        )
        hint = rf"Move the \({a}t\) term to the other side."
        ans = _subj_algebraic_answer(_subj_formula('u', f'v-{a}t'))
    else:
        q = _q_make("t", rf"v = u + {a}t")
        s = (
            rf"Subtract \(u\) from both sides: \(v - u = {a}t\)<br>"
            rf"Divide by \({a}\): <strong>\(t = \dfrac{{v - u}}{{{a}}}\)</strong>"
        )
        hint = "Subtract u, then divide by the coefficient of t."
        ans = _subj_algebraic_answer(_subj_formula('t', _subj_frac('v-u', a)))
    return q, s, hint, 2, ans


def _cts_f_one_step_divide():
    k = random.randint(2, 12)
    letter = random.choice(["t", "x", "n"])
    rhs = random.choice(["s", "d", "y"])
    q = _q_make(letter, rf"{rhs} = {k}{letter}")
    s = rf"Divide both sides by \({k}\): <strong>\({letter} = \dfrac{{{rhs}}}{{{k}}}\)</strong>"
    return q, s, "Undo multiplication by dividing both sides.", 1, _subj_algebraic_answer(
        _subj_formula(letter, _subj_frac(rhs, k))
    )


def _cts_f_two_step_y_mx_c():
    m = random.randint(2, 9)
    c = random.randint(1, 15)
    q = _q_make("x", rf"y = {m}x + {c}")
    s = (
        rf"Subtract \({c}\): \(y - {c} = {m}x\)<br>"
        rf"Divide by \({m}\): <strong>\(x = \dfrac{{y - {c}}}{{{m}}}\)</strong>"
    )
    return q, s, "Undo +c first, then divide by the coefficient of x.", 2, _subj_algebraic_answer(
        _subj_formula('x', _subj_frac(f'y-{c}', m))
    )


def _cts_f_perimeter():
    if random.choice([True, False]):
        q = _q_make("w", r"P = 2l + 2w")
        s = (
            r"Subtract \(2l\) from both sides: \(P - 2l = 2w\)<br>"
            r"Divide by 2: <strong>\(w = \dfrac{P - 2l}{2}\)</strong>"
        )
        ans = _subj_algebraic_answer(_subj_formula('w', _subj_frac('p-2l', 2)))
    else:
        q = _q_make("l", r"P = 2l + 2w")
        s = (
            r"Subtract \(2w\) from both sides: \(P - 2w = 2l\)<br>"
            r"Divide by 2: <strong>\(l = \dfrac{P - 2w}{2}\)</strong>"
        )
        ans = _subj_algebraic_answer(_subj_formula('l', _subj_frac('p-2w', 2)))
    return q, s, "Treat P = 2l + 2w like a normal equation.", 2, ans


def _cts_f_ax_plus_by():
    a = random.randint(2, 6)
    b = random.randint(2, 5)
    c = random.randint(12, 36)
    q = _q_make("y", rf"{a}x + {b}y = {c}")
    s = (
        rf"Subtract \({a}x\) from both sides: \({b}y = {c} - {a}x\)<br>"
        rf"<strong>\(y = \dfrac{{{c} - {a}x}}{{{b}}}\)</strong>"
    )
    return q, s, "Treat x as a known value; isolate y like a normal equation.", 2, _subj_algebraic_answer(
        _subj_formula('y', _subj_frac(f'{c}-{a}x', b))
    )


def _cts_f_speed_time():
    if random.choice([True, False]):
        q = _q_make("t", r"v = \dfrac{s}{t}")
        s = (
            r"Multiply by \(t\): \(vt = s\)<br>"
            r"Divide by \(v\): <strong>\(t = \dfrac{s}{v}\)</strong>"
        )
        hint = "Remove the fraction: multiply by t, then divide by v."
        ans = _subj_algebraic_answer(_subj_formula('t', _subj_frac('s', 'v')))
    else:
        q = _q_make("s", r"v = \dfrac{s}{t}")
        s = (
            r"Multiply by \(t\): <strong>\(s = vt\)</strong>"
        )
        hint = "Multiply both sides by t to clear the denominator."
        ans = _subj_algebraic_answer(_subj_formula('s', 'v*t'))
    return q, s, hint, 2, ans


def _cts_f_work_formula():
    if random.choice([True, False]):
        q = _q_make("F", r"W = Fd")
        s = r"Divide both sides by \(d\): <strong>\(F = \dfrac{W}{d}\)</strong>"
        hint = "W = Fd is linear in F — divide by d."
        ans = _subj_algebraic_answer(_subj_formula('f', _subj_frac('w', 'd')))
    else:
        q = _q_make("d", r"W = Fd")
        s = r"Divide both sides by \(F\): <strong>\(d = \dfrac{W}{F}\)</strong>"
        hint = "Divide both sides by F to isolate d."
        ans = _subj_algebraic_answer(_subj_formula('d', _subj_frac('w', 'f')))
    return q, s, hint, 2, ans


def _cts_f_first_step():
    m = random.randint(2, 7)
    c = random.randint(1, 12)
    q = (
        rf"To make \(x\) the subject of \(y = {m}x + {c}\), "
        rf"what should you do <strong>first</strong>?"
    )
    correct = rf"Subtract \({c}\) from both sides"
    wrong = [
        rf"Divide both sides by \({m}\)",
        rf"Add \({c}\) to both sides",
        rf"Square both sides",
    ]
    opts = wrong + [correct]
    random.shuffle(opts)
    letters = "ABCD"
    correct_letter = letters[opts.index(correct)]
    q += "<br>" + "<br>".join(f"{letters[i]}) {opts[i]}" for i in range(4))
    s = rf"Remove the constant term first → <strong>{correct_letter}</strong>."
    return q, s, "Undo operations in reverse order: +c before ×m.", 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (5)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_i_vuat():
    a = random.randint(2, 8)
    q = _q_make("t", rf"v = u + {a}t")
    s = (
        rf"\(v - u = {a}t\)<br>"
        rf"<strong>\(t = \dfrac{{v - u}}{{{a}}}\)</strong>"
    )
    return q, s, "Isolate the term in t, then divide.", 3, _subj_algebraic_answer(
        _subj_formula('t', _subj_frac('v-u', a))
    )


def _cts_i_sqrt_area():
    q = _q_make("r", r"A = \pi r^2")
    s = (
        r"Divide by \(\pi\): \(A/\pi = r^2\)<br>"
        r"Square root both sides: <strong>\(r = \sqrt{\dfrac{A}{\pi}}\)</strong>"
    )
    return q, s, "Undo squaring with a square root.", 3, _subj_algebraic_answer(
        _subj_formula('r', _subj_sqrt('a/π'))
    )


def _cts_i_half_at_squared():
    a = random.randint(2, 6)
    num, den = 1, 2
    q = _q_make("t", rf"s = \dfrac{{{num}}}{{{den}}}{a}t^2")
    inner = _frac(f"{den}s", a)
    s = (
        rf"Multiply by \({den}\): \({den}s = {a}t^2\)<br>"
        rf"Divide by \({a}\): \({inner} = t^2\)<br>"
        rf"<strong>\(t = {_sqrt_tex(inner)}\)</strong>"
    )
    inner = _subj_frac(f'{den}s', a)
    return q, s, "Clear the fraction, isolate t², then take the square root.", 4, _subj_algebraic_answer(
        _subj_formula('t', _subj_sqrt(inner))
    )


def _cts_i_linear_fraction():
    a = random.randint(2, 5)
    b = random.randint(1, 9)
    c = random.randint(2, 6)
    q = _q_make("x", rf"y = \dfrac{{{a}x + {b}}}{{{c}}}")
    s = (
        rf"Multiply by \({c}\): \(cy = {a}x + {b}\)<br>"
        rf"Subtract \({b}\): \(cy - {b} = {a}x\)<br>"
        rf"<strong>\(x = \dfrac{{cy - {b}}}{{{a}}}\)</strong>"
    )
    return q, s, "Remove the fraction first (multiply by the denominator).", 3, _subj_algebraic_answer(
        _subj_formula('x', _subj_frac(f'c*y-{b}', a))
    )


def _cts_i_distance_speed():
    k = random.randint(3, 9)
    q = _q_make("t", rf"D = {k}t")
    s = rf"<strong>\(t = \dfrac{{D}}{{{k}}}\)</strong>"
    return q, s, "Same as solving D = kt for t.", 2, _subj_algebraic_answer(
        _subj_formula('t', _subj_frac('d', k))
    )


def _cts_i_F_ma():
    a = random.randint(2, 9)
    if random.choice([True, False]):
        q = _q_make("m", rf"F = {a}m")
        s = rf"Divide both sides by \({a}\): <strong>\(m = \dfrac{{F}}{{{a}}}\)</strong>"
        hint = "F = ma with a numerical coefficient — divide by a."
        ans = _subj_algebraic_answer(_subj_formula('m', _subj_frac('f', a)))
    else:
        q = _q_make("a", rf"F = {a}m")
        s = rf"Divide both sides by \(m\): <strong>\(a = \dfrac{{F}}{{m}}\)</strong>"
        hint = "Divide by m to make a the subject."
        ans = _subj_algebraic_answer(_subj_formula('a', _subj_frac('f', 'm')))
    return q, s, hint, 3, ans


def _cts_i_circumference():
    q = _q_make("r", r"C = 2\pi r")
    s = r"Divide both sides by \(2\pi\): <strong>\(r = \dfrac{C}{2\pi}\)</strong>"
    return q, s, "Undo multiplication by 2π.", 3, _subj_algebraic_answer(
        _subj_formula('r', _subj_frac('c', '2π'))
    )


def _cts_i_triangle_area():
    q = _q_make("h", r"A = \dfrac{1}{2}bh")
    s = (
        r"Multiply by 2: \(2A = bh\)<br>"
        r"Divide by \(b\): <strong>\(h = \dfrac{2A}{b}\)</strong>"
    )
    return q, s, "Clear the ½ first, then divide by b.", 3, _subj_algebraic_answer(
        _subj_formula('h', _subj_frac('2a', 'b'))
    )


def _cts_i_y_ax_squared():
    a = random.randint(2, 7)
    inner = _frac("y", a)
    q = _q_make("x", rf"y = {a}x^2")
    s = (
        rf"Divide by \({a}\): \(y/{a} = x^2\)<br>"
        rf"<strong>\(x = {_sqrt_tex(inner)}\)</strong>"
    )
    return q, s, "Divide by the coefficient, then square root.", 3, _subj_algebraic_answer(
        _subj_formula('x', _subj_sqrt(_subj_frac('y', a)))
    )


def _cts_i_suvat_make_u():
    a = random.randint(2, 5)
    q = _q_make("u", rf"s = ut + \dfrac{{1}}{{2}}{a}t^2")
    s = (
        rf"Subtract \(\dfrac{{1}}{{2}}{a}t^2\): \(s - \dfrac{{1}}{{2}}{a}t^2 = ut\)<br>"
        rf"Divide by \(t\): <strong>\(u = \dfrac{{s - \dfrac{{1}}{{2}}{a}t^2}}{{t}}\)</strong>"
    )
    return q, s, "Remove the ½at² term, then divide by t.", 4, _subj_algebraic_answer(
        _subj_formula('u', _subj_frac(f's-{a}*t^2/2', 't'))
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (9)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_d_kinetic():
    if random.choice([True, False]):
        q = _q_make("v", r"E = \dfrac{1}{2}mv^2")
        s = (
            r"Multiply by 2: \(2E = mv^2\)<br>"
            r"Divide by \(m\): \(\dfrac{2E}{m} = v^2\)<br>"
            r"<strong>\(v = \sqrt{\dfrac{2E}{m}}\)</strong>"
        )
        hint = "Clear the fraction and the square, then square root."
        ans = _subj_algebraic_answer(_subj_formula('v', _subj_sqrt(_subj_frac('2e', 'm'))))
    else:
        q = _q_make("m", r"E = \dfrac{1}{2}mv^2")
        s = (
            r"Multiply by 2: \(2E = mv^2\)<br>"
            r"<strong>\(m = \dfrac{2E}{v^2}\)</strong>"
        )
        hint = "Multiply by 2, then divide by v²."
        ans = _subj_algebraic_answer(_subj_formula('m', _subj_frac('2e', 'v^2')))
    return q, s, hint, 4, ans


def _cts_d_v_squared_u():
    a = random.randint(2, 6)
    inner = f"v^2 - {a}s"
    q = _q_make("u", rf"v^2 = u^2 + {a}s")
    s = (
        rf"Subtract \({a}s\): \(v^2 - {a}s = u^2\)<br>"
        rf"<strong>\(u = {_sqrt_tex(inner)}\)</strong>"
    )
    return q, s, "Isolate u², then take the square root.", 4, _subj_algebraic_answer(
        _subj_formula('u', _subj_sqrt(f'v^2-{a}s'))
    )


def _cts_d_density():
    q = _q_make("V", r"\rho = \dfrac{m}{V}")
    s = (
        r"Multiply by \(V\): \(\rho V = m\)<br>"
        r"Divide by \(\rho\): <strong>\(V = \dfrac{m}{\rho}\)</strong>"
    )
    return q, s, "Multiply by the denominator, then divide by ρ.", 4, _subj_algebraic_answer(
        _subj_formula('v', _subj_frac('m', 'ρ'))
    )


def _cts_d_inverse_proportion():
    k = random.randint(3, 18)
    q = _q_make("x", rf"y = \dfrac{{{k}}}{{x}}")
    s = (
        rf"Multiply by \(x\): \(xy = {k}\)<br>"
        rf"Divide by \(y\): <strong>\(x = {_frac(k, 'y')}\)</strong>"
    )
    return q, s, "Clear the fraction: multiply by x.", 4, _subj_algebraic_answer(
        _subj_formula('x', _subj_frac(k, 'y'))
    )


def _cts_d_P_VI():
    if random.choice([True, False]):
        q = _q_make("I", r"P = VI")
        s = r"Divide both sides by \(V\): <strong>\(I = \dfrac{P}{V}\)</strong>"
        hint = "P = VI — divide by V to isolate I."
        ans = _subj_algebraic_answer(_subj_formula('i', _subj_frac('p', 'v')))
    else:
        q = _q_make("V", r"P = VI")
        s = r"Divide both sides by \(I\): <strong>\(V = \dfrac{P}{I}\)</strong>"
        hint = "Divide by I to make V the subject."
        ans = _subj_algebraic_answer(_subj_formula('v', _subj_frac('p', 'i')))
    return q, s, hint, 3, ans


def _cts_d_V_lwh():
    q = _q_make("h", r"V = lwh")
    s = (
        r"Divide both sides by \(lw\): <strong>\(h = \dfrac{V}{lw}\)</strong>"
    )
    return q, s, "Divide by the product of the other two dimensions.", 3, _subj_algebraic_answer(
        _subj_formula('h', _subj_frac('v', 'l*w'))
    )


def _cts_d_y_ax2_plus_c():
    a = random.randint(2, 5)
    c = random.randint(1, 12)
    inner = _frac(f"y - {c}", a)
    q = _q_make("x", rf"y = {a}x^2 + {c}")
    s = (
        rf"Subtract \({c}\): \(y - {c} = {a}x^2\)<br>"
        rf"Divide by \({a}\): \(x^2 = {inner}\)<br>"
        rf"<strong>\(x = {_sqrt_tex(inner)}\)</strong>"
    )
    return q, s, "Undo +c, divide by a, then square root.", 4, _subj_algebraic_answer(
        _subj_formula('x', _subj_sqrt(_subj_frac(f'y-{c}', a)))
    )


def _cts_d_suvat_u_zero():
    a = random.randint(2, 5)
    q = _q_make("t", rf"s = \dfrac{{1}}{{2}}{a}t^2")
    inner = _frac("2s", a)
    s = (
        rf"Multiply by 2: \(2s = {a}t^2\)<br>"
        rf"Divide by \({a}\): \(t^2 = {inner}\)<br>"
        rf"<strong>\(t = {_sqrt_tex(inner)}\)</strong>"
    )
    inner = _subj_frac('2s', a)
    return q, s, "When u = 0, suvat reduces to s = ½at².", 4, _subj_algebraic_answer(
        _subj_formula('t', _subj_sqrt(inner))
    )


def _cts_d_subject_on_both_sides():
    a = random.randint(2, 4)
    b = random.randint(1, 8)
    c = random.randint(1, 5)
    d = random.randint(3, 12)
    q = _q_make("x", rf"{a}x + {b} = {c}x + {d}")
    coeff = a - c
    const = d - b
    s = (
        rf"Subtract \({c}x\) and \({b}\): \({coeff}x = {const}\)<br>"
        rf"<strong>\(x = {_frac(const, coeff)}\)</strong>"
    )
    return q, s, "Collect x terms on one side, numbers on the other.", 4, _subj_algebraic_answer(
        _subj_formula('x', _subj_frac(const, coeff))
    )


def _cts_d_rational_x():
    p = random.randint(1, 5)
    q_val = random.randint(2, 6)
    k = random.randint(2, 5)
    q = _q_make("x", rf"\dfrac{{x + {p}}}{{x - {q_val}}} = {k}")
    s = (
        rf"Multiply by \(x - {q_val}\): \(x + {p} = {k}(x - {q_val})\)<br>"
        rf"Expand: \(x + {p} = {k}x - {k * q_val}\)<br>"
        rf"Collect \(x\): \(x - {k}x = -{k * q_val} - {p}\)<br>"
        rf"<strong>\(x = {_frac(-k * q_val - p, 1 - k)}\)</strong>"
    )
    num = -k * q_val - p
    den = 1 - k
    return q, s, "Multiply by the denominator, then collect like terms.", 5, _subj_algebraic_answer(
        _subj_formula('x', _subj_frac(num, den))
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (12 — randomised)
# ══════════════════════════════════════════════════════════════════════════════

def _cts_mcq_y_mx_c():
    m = random.randint(2, 8)
    c = random.randint(1, 14)
    correct = rf"\(x = \dfrac{{y - {c}}}{{{m}}}\)"
    wrong = [
        rf"\(x = \dfrac{{y + {c}}}{{{m}}}\)",
        rf"\(x = {m}(y - {c})\)",
        rf"\(x = \dfrac{{{m}y - {c}}}{{{m}}}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"Make \(x\) the subject of \(y = {m}x + {c}\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Subtract c, then divide by m.", 2, opts, correct_letter


def _cts_mcq_vuat():
    a = random.randint(2, 9)
    correct = rf"\(t = \dfrac{{v - u}}{{{a}}}\)"
    wrong = [
        rf"\(t = \dfrac{{v + u}}{{{a}}}\)",
        rf"\(t = {a}(v - u)\)",
        rf"\(t = \dfrac{{u - v}}{{{a}}}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"Make \(t\) the subject of \(v = u + {a}t\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Subtract u, then divide by a.", 2, opts, correct_letter


def _cts_mcq_sqrt_r():
    correct = r"\(r = \sqrt{\dfrac{A}{\pi}}\)"
    wrong = [
        r"\(r = \dfrac{A}{\pi}\)",
        r"\(r = \sqrt{A\pi}\)",
        r"\(r = \dfrac{\sqrt{A}}{\pi}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Make \(r\) the subject of \(A = \pi r^2\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Divide by π, then square root.", 2, opts, correct_letter


def _cts_mcq_kinetic():
    if random.choice([True, False]):
        correct = r"\(v = \sqrt{\dfrac{2E}{m}}\)"
        wrong = [
            r"\(v = \dfrac{2E}{m}\)",
            r"\(v = \sqrt{\dfrac{E}{2m}}\)",
            r"\(v = \dfrac{\sqrt{2E}}{m}\)",
        ]
        q = r"Make \(v\) the subject of \(E = \dfrac{1}{2}mv^2\)."
        hint = "Multiply by 2, divide by m, then square root."
    else:
        correct = r"\(m = \dfrac{2E}{v^2}\)"
        wrong = [
            r"\(m = \dfrac{E}{2v^2}\)",
            r"\(m = \dfrac{2E}{v}\)",
            r"\(m = \dfrac{E}{v^2}\)",
        ]
        q = r"Make \(m\) the subject of \(E = \dfrac{1}{2}mv^2\)."
        hint = "Multiply by 2, then divide by v²."
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, hint, 3, opts, correct_letter


def _cts_mcq_triangle_h():
    correct = r"\(h = \dfrac{2A}{b}\)"
    wrong = [
        r"\(h = \dfrac{A}{2b}\)",
        r"\(h = \dfrac{A}{b}\)",
        r"\(h = 2Ab\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Make \(h\) the subject of \(A = \dfrac{1}{2}bh\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Multiply by 2, then divide by b.", 2, opts, correct_letter


def _cts_mcq_circumference():
    correct = r"\(r = \dfrac{C}{2\pi}\)"
    wrong = [
        r"\(r = \dfrac{C}{\pi}\)",
        r"\(r = \dfrac{2C}{\pi}\)",
        r"\(r = C - 2\pi\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Make \(r\) the subject of \(C = 2\pi r\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Divide both sides by 2π.", 2, opts, correct_letter


def _cts_mcq_inverse():
    k = random.randint(4, 15)
    correct = rf"\(x = {_frac(k, 'y')}\)"
    wrong = [
        rf"\(x = {_frac('y', k)}\)",
        rf"\(x = {k}y\)",
        rf"\(x = y - {k}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"Make \(x\) the subject of \(y = \dfrac{{{k}}}{{x}}\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Multiply by x, then divide by y.", 2, opts, correct_letter


def _cts_mcq_density():
    correct = r"\(V = \dfrac{m}{\rho}\)"
    wrong = [
        r"\(V = m\rho\)",
        r"\(V = \dfrac{\rho}{m}\)",
        r"\(V = m - \rho\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Make \(V\) the subject of \(\rho = \dfrac{m}{V}\)."
    sol = rf"<strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Multiply by V, then divide by ρ.", 3, opts, correct_letter


def _cts_mcq_two_step():
    a = random.randint(2, 6)
    b = random.randint(2, 6)
    correct = rf"\(x = \dfrac{{y + {b}}}{{{a}}}\)"
    wrong = [
        rf"\(x = \dfrac{{y - {b}}}{{{a}}}\)",
        rf"\(x = {a}y + {b}\)",
        rf"\(x = \dfrac{{y}}{{{a}}} + {b}\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = rf"Make \(x\) the subject of \(y = {a}x - {b}\)."
    sol = rf"Add {b}, then divide by {a}: <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Add the constant, then divide by the coefficient.", 2, opts, correct_letter


def _cts_mcq_pythagoras():
    correct = r"\(a = \sqrt{c^2 - b^2}\)"
    wrong = [
        r"\(a = c^2 - b^2\)",
        r"\(a = \sqrt{c^2 + b^2}\)",
        r"\(a = c - b\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Make \(a\) the subject of \(c^2 = a^2 + b^2\)."
    sol = rf"Subtract \(b^2\), then square root: <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Isolate a², then take the square root.", 3, opts, correct_letter


def _cts_mcq_speed():
    correct = r"\(t = \dfrac{d}{v}\)"
    wrong = [
        r"\(t = dv\)",
        r"\(t = \dfrac{v}{d}\)",
        r"\(t = d - v\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Make \(t\) the subject of \(v = \dfrac{d}{t}\)."
    sol = rf"Multiply by t, then divide by v: <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Multiply both sides by t first.", 2, opts, correct_letter


def _cts_mcq_force():
    correct = r"\(a = \dfrac{F}{m}\)"
    wrong = [
        r"\(a = Fm\)",
        r"\(a = \dfrac{m}{F}\)",
        r"\(a = F - m\)",
    ]
    forms = wrong + [correct]
    random.shuffle(forms)
    letters = "ABCD"
    correct_letter = letters[forms.index(correct)]
    opts = [f"{letters[i]}  {forms[i]}" for i in range(4)]
    q = r"Make \(a\) the subject of \(F = ma\)."
    sol = rf"Divide both sides by m: <strong>{correct}</strong>. Answer: <strong>{correct_letter}</strong>"
    return q, sol, "Divide both sides by the other factor.", 2, opts, correct_letter


_CTS_MCQ_POOL = [
    _cts_mcq_y_mx_c,
    _cts_mcq_vuat,
    _cts_mcq_sqrt_r,
    _cts_mcq_kinetic,
    _cts_mcq_triangle_h,
    _cts_mcq_circumference,
    _cts_mcq_inverse,
    _cts_mcq_density,
    _cts_mcq_two_step,
    _cts_mcq_pythagoras,
    _cts_mcq_speed,
    _cts_mcq_force,
]


def _cts_mcq_dispatch():
    return random.choice(_CTS_MCQ_POOL)()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _cts_f_one_step_add,
    _cts_f_one_step_divide,
    _cts_f_two_step_y_mx_c,
    _cts_f_perimeter,
    _cts_f_first_step,
    _cts_f_ax_plus_by,
    _cts_f_speed_time,
    _cts_f_work_formula,
]

_INTERMEDIATE = [
    _cts_i_vuat,
    _cts_i_sqrt_area,
    _cts_i_half_at_squared,
    _cts_i_linear_fraction,
    _cts_i_distance_speed,
    _cts_i_F_ma,
    _cts_i_circumference,
    _cts_i_triangle_area,
    _cts_i_y_ax_squared,
    _cts_i_suvat_make_u,
]

_DIFFICULT = [
    _cts_d_kinetic,
    _cts_d_suvat_u_zero,
    _cts_d_subject_on_both_sides,
    _cts_d_rational_x,
    _cts_d_v_squared_u,
    _cts_d_density,
    _cts_d_inverse_proportion,
    _cts_d_P_VI,
    _cts_d_V_lwh,
    _cts_d_y_ax2_plus_c,
]

_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_changing_the_subject_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return mcq_variants_from_pool(
            _CTS_MCQ_POOL, "changing_the_subject", difficulty, count=4
        )

    pool = _POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return select_tier_variants(combined, 5)
    return select_tier_variants(pool, 5)


def gcse_changing_the_subject(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_changing_the_subject_variants(difficulty, "mcq")
        q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
        return make_problem(
            q, s, hint, difficulty, marks,
            "gcse", "maths", "changing_the_subject",
            options=opts, correct_answer=ans,
        )

    variants = gcse_changing_the_subject_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    return _subj_problem_from_output(variant(), difficulty)
