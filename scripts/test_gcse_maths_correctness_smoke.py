"""GCSE maths correctness guard - run: python scripts/test_gcse_maths_correctness_smoke.py

Added after the 2026-10-22 hot-fix. The earlier smoke tests only proved that every
GCSE maths generator *runs*; this one checks that the answers are *right*.

For every GCSE maths topic, tier and named variant (practice variants and the MCQ
banks) it generates a handful of seeded questions and then:

1. runs the answer checker on the generated correct answer (must be accepted) and
   on known-wrong mutations (must be rejected);
2. scans each worked solution for single-line arithmetic ("a op b = c", chains,
   square roots) and checks it, including school (half-up) rounding, and that any
   rounded line is backed by a stated accuracy in the question or solution;
3. checks a stated rounding instruction ("to 2 decimal places") against the raw
   answer;
4. independently recomputes the answer for families where that is feasible
   (Pythagoras, vectors, parallel-line angles, compound measures, powers of 10,
   means, surds, similarity scale factors, decimal arithmetic);
5. for MCQs, checks the keyed option exists exactly once and no distractor equals it;
6. statically flags truncated square roots (int(math.sqrt(...)) used as an answer).

It is deterministic (seeded) and takes roughly 10 seconds.
"""
import contextlib
import io
import math
import random
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generators.shared.answer_checkers import check_answer  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

TIERS = ('foundational', 'intermediate', 'difficult')
RUNS_PER_VARIANT = 20         # walks every row of each hard-coded table, plus seeded randomness
MCQ_RUNS_PER_VARIANT = 4
BASE_SEED = 20261022

ISSUES = []


def issue(kind, where, detail):
    ISSUES.append((kind, where, detail))


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

_TAG = re.compile(r'<[^>]+>')
_SVG = re.compile(r'<svg.*?</svg>', re.S)


def plain(html):
    text = _SVG.sub(' ', str(html))
    text = _TAG.sub(' ', text)
    text = (text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
            .replace('\\(', ' ').replace('\\)', ' ').replace('\\dfrac', ' ').replace('\\times', '×'))
    return re.sub(r'\s+', ' ', text).strip()


def half_up(value, dp):
    d = Decimal(repr(float(value))) if not isinstance(value, Decimal) else value
    return float(d.quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP))


def dp_of(text):
    text = str(text)
    return len(text.split('.')[1]) if '.' in text else 0


def num(text):
    try:
        return Fraction(str(text).strip())
    except (ValueError, ZeroDivisionError):
        return None


def close(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def raw_parts(raw):
    raw = str(raw)
    sep = '\x1e' if '\x1e' in raw else '|'
    return raw.split(sep)


# '+ -3', '- -3', '× -0.5': a negative should be bracketed or the sign merged ('- 3', '+ 3', '× (-0.5)').
_SIGN_ARTEFACT = re.compile(r'(?:(?<=\s)|(?<=\d)|(?<=[A-Za-z)}]))[+−-] ?[−-] ?\d')


# Rounding / accuracy wording that makes a rounded figure legitimate.
_ROUND_WORDS = re.compile(
    r'decimal place|d\.p\.|\bdp\b|significant|s\.f\.|\bsf\b|nearest|round|approx|estimate|≈|≃|'
    r'to the nearest|correct to|truncat|\bto 1 d|\bto 2 d', re.I)


# ─────────────────────────────────────────────────────────────────────────────
# Arithmetic scanner
# ─────────────────────────────────────────────────────────────────────────────

_EXPR_CHARS = set('0123456789.,+−-×÷*/()²³ \t')
_RHS = re.compile(r'=\s*([£$€]?)(-?[−]?\d[\d.]*)')


def _safe_eval(expr):
    expr = (expr.replace('−', '-').replace('×', '*').replace('÷', '/')
            .replace('²', '**2').replace('³', '**3'))
    expr = re.sub(r'(?<=\d),(?=\d{3}\b)', '', expr)
    if not re.fullmatch(r'[\d.\s+\-*/()]+', expr.replace('**2', '').replace('**3', '')):
        return None
    if '**' in expr and not re.fullmatch(r'[\d.\s+\-*/()]*', expr.replace('**2', '').replace('**3', '')):
        return None
    import ast
    try:
        tree = ast.parse(expr.strip(), mode='eval')
    except SyntaxError:
        return None

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return Fraction(str(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BinOp):
            a, b = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            if isinstance(node.op, ast.Div):
                return a / b
            if isinstance(node.op, ast.Pow) and isinstance(node.right, ast.Constant) and node.right.value in (2, 3):
                return a ** int(node.right.value)
        raise ValueError('unsupported')

    try:
        return ev(tree)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


_NUM_TOKEN = re.compile(r'\d+(?:\.\d+)?')


def _interval(expr):
    """(low, high) of ``expr`` when every decimal operand may be off by half a unit in its last place.

    Worked solutions legitimately carry rounded intermediates ("18 × 0.8192 = 14.74");
    only a result outside this interval (or a final rounding that is wrong) is an error.
    """
    tokens = list(_NUM_TOKEN.finditer(expr))
    decimals = [m for m in tokens if '.' in m.group()]
    if not decimals:
        return None
    if len(decimals) > 8:
        return None
    lows, highs = [], []
    for mask in range(1 << len(decimals)):
        deltas = {}
        for i, m in enumerate(decimals):
            half = Decimal(1).scaleb(-dp_of(m.group())) / 2
            deltas[m.start()] = half if mask >> i & 1 else -half
        pieces, last = [], 0
        for m in tokens:
            pieces.append(expr[last:m.start()])
            pieces.append(format(Decimal(m.group()) + deltas.get(m.start(), Decimal(0)), 'f'))
            last = m.end()
        pieces.append(expr[last:])
        v = _safe_eval(''.join(pieces))
        if v is None:
            return None
        lows.append(float(v))
        highs.append(float(v))
    return min(lows), max(highs)


def scan_arithmetic(text, stated_rounding):
    """Yield (message) for solution lines 'expr = c' that are arithmetically wrong."""
    out = []
    t = re.sub(r'(?<=\d),(?=\d{3}(?!\d))', '', text)
    for m in _RHS.finditer(t):
        eq = m.start()
        k = eq
        while k > 0 and t[k - 1] in _EXPR_CHARS:
            k -= 1
        left = t[k:eq]
        # trim a leading operator/space so the expression starts at a number or bracket
        trimmed = left.lstrip()
        start = k + (len(left) - len(trimmed))
        before = t[:start].rstrip()
        stripped = trimmed.strip()
        if not stripped or stripped[0] in '+×÷*/)':
            continue
        cur, rhs = m.group(1), m.group(2).replace('−', '-')
        end = m.end(2)
        after = t[end:].lstrip()
        if before and (before[-1] in '+−-×÷*/^x√(.:' or before[-1].isalnum() or before[-1] in '/)'):
            continue
        if after and (after[0] in '+−-×÷*/^²³√(.:½⅓⅔¼¾⅛' or after[0].isdigit() or after[0] in '%'):
            continue
        if not re.search(r'[+−\-×÷*/²³]', stripped.lstrip('-−')):
            continue
        if re.search(r'\d\s+\d{3}\b', stripped):
            continue
        if stripped.count('(') != stripped.count(')'):
            continue
        value = _safe_eval(stripped)
        if value is None:
            continue
        c = num(rhs)
        if c is None:
            continue
        exact_ok = abs(float(value) - float(c)) <= 1e-9 * max(1.0, abs(float(c)))
        if exact_ok:
            continue
        d = dp_of(rhs)
        context = f'...{t[max(0, start - 25):end + 12]}'
        interval = _interval(stripped)   # None when every operand is exact (no decimals)
        half_c = 0.5 * 10 ** -d
        if interval and interval[0] - half_c - 1e-9 <= float(c) <= interval[1] + half_c + 1e-9:
            continue   # consistent with rounded intermediates and a rounded result
        if abs(half_up(float(value), d) - float(c)) <= 1e-9 * max(1.0, abs(float(c))):
            if not stated_rounding and not (cur and d <= 2):   # money to the penny / pound is understood
                out.append(f'rounded without a stated accuracy: "{stripped} = {rhs}" (exact {float(value):.6g}) in {context}')
            continue
        out.append(f'wrong arithmetic: "{stripped} = {rhs}" (should be {float(value):.6g}) in {context}')
    for m in re.finditer(r'\d\.\d{9,}(?![\d…])', t):
        out.append(f'floating-point noise shown to the pupil: "{m.group()}"')
    # square roots: √N = c
    for m in re.finditer(r'(?<![\w×÷*/:()])√\s*(\d[\d.]*)\s*(=|≈)\s*(-?\d[\d.]*)(?![\d.]*\s*[√×(a-z:+−\-÷*/^])', t):
        n, c = float(m.group(1).rstrip('.')), m.group(3).rstrip('.')   # "√37 = 6.1." ends a sentence
        prev = t[:m.start()].rstrip()
        if prev and prev[-1] in '×÷*/:(':
            continue
        d = dp_of(c)
        root = math.sqrt(n)
        if abs(half_up(root, d) - float(c)) > 1e-9 * max(1, root):
            out.append(f'wrong square root: "√{m.group(1)} = {c}" (should be {root:.6g})')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Stated rounding vs raw answer
# ─────────────────────────────────────────────────────────────────────────────

_DP_STATED = re.compile(r'(?:(?:to|correct to|nearest)\s+)?(\d)\s*(?:decimal places?|d\.p\.)', re.I)


def check_stated_rounding(q, raw, at, where):
    if at != 'number' or raw is None:
        return
    stated = {int(x) for x in _DP_STATED.findall(q)}
    if len(stated) == 1:
        limit = stated.pop()
        if dp_of(raw) > limit:
            issue('rounding', where, f'question states {limit} d.p. but expected answer is {raw}')
    sf = re.findall(r'(\d)\s*(?:significant figures?|s\.f\.)', q, re.I)
    if len(set(sf)) == 1 and '.' in str(raw) and num(raw) is not None and float(num(raw)) != 0:
        digits = re.sub(r'^-?0*', '', str(raw).replace('.', '', 1)).lstrip('0')
        if len(digits) > int(sf[0]):
            issue('rounding', where, f'question states {sf[0]} s.f. but expected answer is {raw}')
    if re.search(r'nearest (?:whole|integer|unit|gram|metre|minute|degree|cm|mm|km)', q, re.I) and \
            not re.search(r'decimal place|d\.p\.', q, re.I) and dp_of(raw) > 0:
        issue('rounding', where, f'question says "nearest" but expected answer is {raw}')


# ─────────────────────────────────────────────────────────────────────────────
# Independent recomputation for families where it is feasible
# ─────────────────────────────────────────────────────────────────────────────

def _ints(text):
    return [Fraction(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text.replace('−', '-'))]


def _eq(raw, expected, dp=None):
    got = num(raw)
    if got is None:
        return False
    if dp is not None:
        expected = half_up(expected, dp)
    return close(got, expected, 1e-9)


def _pyth_expect(name, q, raw):
    t = plain(q)
    nums = [float(x) for x in _ints(t)]
    if name == '_py_f6_rectangle_diagonal':
        w, h = nums[:2]
        return _eq(raw, math.hypot(w, h), 2)
    if name == '_py_f7_distance_on_grid':
        m = re.search(r'\((\d+), (\d+)\)', t.split('point B')[1]) if 'point B' in t else None
        return _eq(raw, math.hypot(*[float(x) for x in m.groups()]), 2) if m else None
    if name == '_py_f8_square_diagonal':
        return _eq(raw, nums[0] * math.sqrt(2), 2)
    if name == '_py_i1_perimeter':
        a, b = nums[:2]
        return _eq(raw, a + b + math.hypot(a, b), 2)
    if name == '_py_i3_isosceles_height':
        base, slant = nums[:2]
        return _eq(raw, math.sqrt(slant ** 2 - (base / 2) ** 2), 2)
    if name == '_py_i4_3d_space_diagonal':
        l, w, h = nums[:3]
        return _eq(raw, math.sqrt(l * l + w * w + h * h), 2)
    if name == '_py_i5_3d_two_step':
        l, w, h = nums[:3]
        parts = raw_parts(raw)
        return (_eq(parts[0], math.hypot(l, w), 2)
                and _eq(parts[1], math.sqrt(l * l + w * w + h * h), 2))
    if name == '_py_i6_coordinate_distance':
        m = re.findall(r'\((-?\d+), (-?\d+)\)', t)
        (x1, y1), (x2, y2) = [(float(a), float(b)) for a, b in m[:2]]
        return _eq(raw, math.hypot(x2 - x1, y2 - y1), 2)
    if name == '_py_i7_ladder_slips':
        lad, base, slide = nums[:3]
        return _eq(raw, math.sqrt(lad ** 2 - (base + slide) ** 2), 2)
    if name == '_py_i8_cone_slant':
        return _eq(raw, math.hypot(*nums[:2]), 2)
    if name == '_py_d1_composite_area':
        m = re.search(r'rectangle (\d+) cm by (\d+) cm.*?is (\d+) cm long.*?is (\d+) cm', t)
        if not m:
            return None
        length, width, c, a = [float(x) for x in m.groups()]
        return _eq(raw, length * width - a * math.sqrt(c * c - a * a) / 2, 2)
    return None


def _vec_magnitude_expect(q, raw, at):
    m = re.search(r'pmatrix\}\s*(-?\d+)\s*\\\\\s*(-?\d+)', str(q))
    if not m or at != 'number':
        return None
    x, y = float(m.group(1)), float(m.group(2))
    return _eq(raw, math.hypot(x, y), 2) or _eq(raw, math.hypot(x, y), 1) or _eq(raw, math.hypot(x, y), 3)


def _cm_expect(name, q, raw):
    t = plain(q)
    n = [float(x) for x in _ints(t)]
    one = lambda v: _eq(raw, v, 2)  # noqa: E731
    if name == '_cm_f1_sdt_find_speed':
        return one(n[0] / n[1])
    if name == '_cm_f2_sdt_find_distance':
        return one(n[0] * n[1])
    if name == '_cm_f3_sdt_find_time':
        m = re.search(r'travels (\d+) km at an average speed of (\d+) km/h', t)
        return one(float(m.group(1)) / float(m.group(2)))
    if name == '_cm_f4_dmv_find_density':
        return one(n[0] / n[1])
    if name == '_cm_f5_dmv_find_mass':
        return one(n[0] * n[1])
    if name == '_cm_f6_dmv_find_volume':
        return one(n[0] / n[1])
    if name == '_cm_f7_pfa_find_pressure':
        return one(n[0] / n[1])
    if name == '_cm_f8_pfa_find_force':
        return one(n[0] * n[1])
    if name == '_cm_f9_pfa_find_area':
        return one(n[0] / n[1])
    if name == '_cm_f12_population_density_find':
        return one(float(re.search(r'population of ([\d,]+)', t).group(1).replace(',', '')) /
                   float(re.search(r'area of (\d+)', t).group(1)))
    if name == '_cm_i2_time_hours_minutes':
        m = re.search(r'at (\d+) km/h for (\d+) hours? and (\d+) minutes', t)
        s, h, mi = [float(x) for x in m.groups()]
        return one(s * (h + mi / 60))
    if name == '_cm_i5_sdt_time_in_minutes':
        m = re.search(r'at (\d+) km/h for (\d+) minutes', t)
        s, mi = [float(x) for x in m.groups()]
        return one(s * mi / 60)
    if name == '_cm_i9_average_speed_equal_distances':
        m = re.search(r'at (\d+) km/h, then returns from B to A at (\d+) km/h', t)
        a, b = [float(x) for x in m.groups()]
        return one(2 * a * b / (a + b))
    if name == '_cm_i11_population_density_area':
        m = re.search(r'population of ([\d,]+) people and a population density of (\d+)', t)
        return one(float(m.group(1).replace(',', '')) / float(m.group(2)))
    if name == '_cm_d2_overtaking':
        m = re.search(r'travels at (\d+) km/h\. Vehicle B leaves the same point (\d+) minutes later at (\d+) km/h', t)
        slow, mins, fast = [float(x) for x in m.groups()]
        return _eq(raw, slow * mins / (fast - slow), 0)
    if name == '_cm_d6_two_pipes':
        m = re.search(r'tank of (\d+) litres has a fill pipe running at (\d+) L/min and a drain pipe at (\d+)', t)
        vol, fill, drain = [float(x) for x in m.groups()]
        return one(vol / (fill - drain))
    if name == '_cm_d13_three_leg_average':
        m = re.findall(r'(\d+) hours? at (\d+) km/h', t)
        legs = [(float(h), float(s)) for h, s in m]
        m3 = re.search(r'then (\d+) hours at (\d+) km/h', t)
        if m3 and len(legs) == 2:
            legs.append((float(m3.group(1)), float(m3.group(2))))
        if len(legs) != 3:
            return None
        return one(sum(h * s for h, s in legs) / sum(h for h, s in legs))
    return None


def _num_expect(name, q, raw):
    t = plain(q)
    if name == '_number_found_multiply_by_power_10':
        m = re.search(r'Calculate ([\d.]+) ([×÷]) (\d+)', t)
        a, op, p = Decimal(m.group(1)), m.group(2), Decimal(m.group(3))
        want = a * p if op == '×' else a / p
        return Decimal(str(raw)) == want
    if name == 'gcse_dec_proc_mean':
        vals = [Decimal(x) for x in re.findall(r'\d+\.\d', t.split('mean of')[1])]
        mean = sum(vals) / 4
        return _eq(raw, mean) if mean == mean.quantize(Decimal('0.01')) else \
            Decimal(str(raw)) == mean.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if name == 'gcse_dec_practice_mixed_ops':
        m = re.search(r'\(([\d.]+) ([+−]) ([\d.]+)\) ÷ ([\d.]+)', t)
        a, op, b, c = Decimal(m.group(1)), m.group(2), Decimal(m.group(3)), Decimal(m.group(4))
        return Decimal(str(raw)) == ((a + b) if op == '+' else (a - b)) / c
    return None


def _surd_expect(name, q, raw, at):
    t = plain(q)
    if name == 'gcse_surds_add_subtract':
        m = re.search(r'√(\d+) ([+−]) √(\d+)', t)
        n1, op, n2 = int(m.group(1)), m.group(2), int(m.group(3))
        val = math.sqrt(n1) + math.sqrt(n2) if op == '+' else math.sqrt(n1) - math.sqrt(n2)
        if abs(val) < 1e-9:
            return False   # degenerate: must not ask for a k√p answer that is zero
        coeff, rad = (raw.split('|') + ['1'])[:2] if '|' in str(raw) else (1, raw)
        if '|' in str(raw):
            c, r = str(raw).split('|')
            return close(int(c) * math.sqrt(int(r)), val)
        return None
    return None


def _sim_expect(name, q, raw):
    t = plain(q)
    if name == '_sc_i10_overlapping_similar':
        m = re.search(r'= (\d+) cm, \w+D = (\d+) cm', t)
        ab, ad = Fraction(m.group(1)), Fraction(m.group(2))
        parts = raw_parts(raw)
        return num(parts[2]) == ab / ad
    if name in ('_sc_i5_lsf_from_area_ratio', '_sc_f10_lsf_from_area'):
        a, b = [int(x) for x in re.findall(r'areas (\d+) cm² and (\d+) cm²', t)[0]]
        ra, rb = math.isqrt(a), math.isqrt(b)
        g = math.gcd(ra, rb)
        return str(raw) == f'{ra // g}:{rb // g}'
    return None


def _misc_expect(name, q, raw):
    t = plain(q)
    if name == '_vectors_diff_ratio_collinear':
        m = re.search(r'A\((-?\d+),(-?\d+)\) and B\((-?\d+),(-?\d+)\).*?AP:PB = (\d+):(\d+)', t)
        ax, ay, bx, by, m_, n_ = (Fraction(x) for x in m.groups())
        want = ((n_ * ax + m_ * bx) / (m_ + n_), (n_ * ay + m_ * by) / (m_ + n_))
        parts = raw_parts(raw)
        return all(_eq(parts[i], want[i], 1) for i in range(2))
    if name == '_cl_f15_scale_drawing_length':
        m = re.search(r'scale of 1 : ([\d,]+)\. A wall measures ([\d.]+) cm.*?in (m|km)\.', t)
        scale, d = Decimal(m.group(1).replace(',', '')), Decimal(m.group(2))
        want = d * scale / (100 if m.group(3) == 'm' else 100000)
        return Decimal(str(raw)) == want
    return None


def independent_check(topic, name, p):
    q, raw, at = p['question'], p.get('correct_answer_raw'), p.get('answer_type')
    if raw is None:
        return None
    try:
        if topic == 'pythagoras':
            return _pyth_expect(name, q, raw)
        if topic == 'vectors' and 'magnitude' in name:
            return _vec_magnitude_expect(q, raw, at)
        if topic == 'compound_measures':
            return _cm_expect(name, q, raw)
        if topic in ('number', 'decimals'):
            return _num_expect(name, q, raw)
        if topic == 'surds':
            return _surd_expect(name, q, raw, at)
        if topic == 'similarity_congruence':
            return _sim_expect(name, q, raw)
        if topic in ('vectors', 'constructions_loci'):
            return _misc_expect(name, q, raw)
    except (AttributeError, IndexError, ValueError, ZeroDivisionError, TypeError):
        return None
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Answer-checker probes
# ─────────────────────────────────────────────────────────────────────────────

def user_form(at, raw):
    """How a pupil would type the keyed answer (surd keys are stored as 'k|r')."""
    raw = str(raw)
    if at == 'surd':
        if '|' in raw:
            k, r = raw.split('|')
            return f'{k}√{r}'
        return f'√{raw}'
    return raw


def mutations(at, raw):
    """Known-wrong answers for the types where that is unambiguous."""
    raw = str(raw)
    if at == 'number':
        v = num(raw)
        if v is None:
            return []
        outs = [v + 1, v * 2 + 3, v - Fraction(1, 2)]
        if v != 0:
            outs.append(-v)
        return [str(float(o)).rstrip('0').rstrip('.') if o.denominator != 1 else str(int(o)) for o in outs
                if o != v]
    if at == 'number_fields':
        parts = raw_parts(raw)
        sep = '\x1e' if '\x1e' in raw else '|'
        out = []
        v = num(parts[0])
        if v is not None:
            out.append(sep.join([str(float(v + 1)).rstrip('0').rstrip('.')] + parts[1:]))
        return out
    return []


def probe_checker():
    cases = [
        # precedence: a sum is not a quotient
        ('algebraic', 'x=(C-7)/7', 'x=C-7/7', False),
        ('algebraic', 'x=(C-7)/7', 'C-7/7', False),
        ('algebraic', 'x=(C-7)/7', 'x=C-1', False),
        ('algebraic', 'y=(s-11)/3', 'y = s - 11/3', False),
        ('algebraic', 'y=(s-11)/3', 'y=s-11/3', False),
        ('algebraic', 'y=(s-11)/3', 'y = s/3 - 11/3', True),
        ('algebraic', 'x=(C-7)/7', 'x=(C-7)/7', True),
        ('algebraic', 'x=(C-7)/7', 'x = C/7 - 1', True),
        ('algebraic', 'x=(C-7)/7', '(C-7)/7', True),
        ('algebraic', 'r=C/(2*pi)', 'r=C/(2π)', True),
        ('algebraic', 'r=C/(2*pi)', 'C/(2π)', True),
        ('algebraic', 'r=C/(2*pi)', 'C/2*π', False),
        # pi multiples
        ('pi_multiple', '10/3', '10π/3', True),
        ('pi_multiple', '10/3', '10pi/3', True),
        ('pi_multiple', '10/3', '10/3π', True),
        ('pi_multiple', '10/3', '(10/3)π', True),
        ('pi_multiple', '10/3', '10/3', True),
        ('pi_multiple', '10/3', '5π/3', False),
        ('pi_multiple', '10/3', '10π', False),
        ('pi_multiple', '10/3', '__import__("os")pi', False),
        ('pi_multiple', '10/3', 'pi**9**9**9', False),
        ('pi_multiple', '4', '4π', True),
        ('pi_multiple', '4', '8π/2', True),
        ('pi_multiple', '4', '4', True),
        ('pi_multiple', '4', '5π', False),
        # reversed inequalities
        ('linear_inequality', 'x|<|3', 'x<3', True),
        ('linear_inequality', 'x|<|3', '3>x', True),
        ('linear_inequality', 'x|<|3', '3 > x', True),
        ('linear_inequality', 'x|<|3', '3<x', False),
        ('linear_inequality', 'x|<|3', 'x>3', False),
        ('linear_inequality', 'x|>=|2', '2<=x', True),
        ('linear_inequality', 'x|>=|2', '2>=x', False),
        # y = mx + c in any order
        ('linear_equation', '2|-3', 'y=2x-3', True),
        ('linear_equation', '2|-3', 'y=-3+2x', True),
        ('linear_equation', '2|-3', 'y = -3 + 2x', True),
        ('linear_equation', '2|-3', 'y=3-2x', False),
        ('linear_equation', '2|-3', 'y=2x+3', False),
        ('linear_equation', '-1|0', 'y=-x', True),
        ('linear_equation', '-1|0', 'y=0-x', True),
        # mixed numbers
        ('number', '55/4', '13 3/4', True),
        ('number', '55/4', '13.75', True),
        ('number', '55/4', '55/4', True),
        ('number', '55/4', '13 3/5', False),
        ('number', '55/4', '13 5/4', False),
        ('number', '13.75', '13 3/4', True),
        ('number', '13.75', '13 1/4', False),
        ('number', '4/3', '1 1/3', True),
        ('number', '27', '27', True),
        ('number', '27', '2 7', False),
        ('number', '0.04682', '0.04682', True),
        ('number', '0.04682', '0.05', False),
        ('number', '10.125', '10.125', True),
        ('number', '10.125', '10.12', False),
    ]
    for at, correct, user, expected in cases:
        try:
            got = check_answer(at, correct, user)['correct']
        except Exception as exc:   # noqa: BLE001
            got = f'EXC {exc!r}'
        if got is not expected:
            issue('checker', f'{at} {correct!r} <- {user!r}', f'expected {expected}, got {got}')


# ─────────────────────────────────────────────────────────────────────────────
# Static scan
# ─────────────────────────────────────────────────────────────────────────────

_TRUNC = re.compile(r'int\(\s*(?:math\.)?sqrt\(|int\(.*\*\*\s*0?\.5\s*\)|int\(\s*math\.pow\([^)]*0?\.5')


def static_scan():
    for path in sorted((ROOT / 'generators' / 'gcse').glob('*.py')):
        if path.name.startswith(('physics', 'cs', 'chemistry', 'gcse_cs')):
            continue
        for no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            code = line.split('#', 1)[0]
            if _TRUNC.search(code) and 'range(' not in code:
                issue('truncated-sqrt', f'{path.name}:{no}', line.strip()[:110])


# ─────────────────────────────────────────────────────────────────────────────
# Generation sweep
# ─────────────────────────────────────────────────────────────────────────────

_OPTION = re.compile(r'^\s*([A-H])\s*[.):]?\s+(.*)$', re.S)


def check_mcq(p, where):
    opts = p.get('options')
    if not opts:
        return
    key = str(p.get('correct_answer', '')).strip().upper()
    letters, texts = [], []
    for o in opts:
        m = _OPTION.match(str(o))
        if not m:
            issue('mcq', where, f'option without a letter: {str(o)[:40]!r}')
            return
        letters.append(m.group(1))
        texts.append(plain(m.group(2)).strip().lower())
    if letters.count(key) != 1:
        issue('mcq', where, f'keyed letter {key!r} present {letters.count(key)} times in {letters}')
        return
    right = texts[letters.index(key)]
    for letter, text in zip(letters, texts):
        if letter != key and text == right:
            issue('mcq', where, f'distractor {letter} equals the correct option "{right[:40]}"')
    if len(set(texts)) != len(texts):
        issue('mcq', where, 'two options have identical text')
    for o in texts:
        if re.search(r'[\d√]\?$', o):
            issue('mcq', where, f'placeholder-looking option "{o}"')


def mcq_semantic(topic, name, p, where):
    q = plain(p['question'])
    if topic == 'geometry_angles' or 'Co-interior' in str(p['question']):
        m = re.search(r'One angle is (\d+)°.*Co-interior', q)
        if m:
            x = int(m.group(1))
            key = p['correct_answer'].strip().upper()
            for o in p['options']:
                mm = _OPTION.match(str(o))
                if mm and mm.group(1) == key and plain(mm.group(2)).strip() != str(180 - x):
                    issue('mcq-answer', where, f'co-interior to {x} deg keyed as {mm.group(2)!r}, should be {180 - x}')
    m = re.search(r'magnitude of \\begin\{pmatrix\} (-?\d+) \\\\ (-?\d+)', str(p['question']))
    if m:
        x, y = int(m.group(1)), int(m.group(2))
        key = p['correct_answer'].strip().upper()
        for o in p['options']:
            mm = _OPTION.match(str(o))
            if mm and mm.group(1) == key and float(mm.group(2)) != math.hypot(x, y):
                issue('mcq-answer', where, f'magnitude of ({x}, {y}) keyed as {mm.group(2)}, should be {math.hypot(x, y):.4g}')
    m = re.search(r'shorter sides (\d+) and (\d+)\. The hypotenuse', q)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        key = p['correct_answer'].strip().upper()
        for o in p['options']:
            mm = _OPTION.match(str(o))
            if mm and mm.group(1) == key and float(mm.group(2)) != math.hypot(a, b):
                issue('mcq-answer', where, f'hypotenuse of {a}, {b} keyed as {mm.group(2)}')


# ─────────────────────────────────────────────────────────────────────────────
# Bearings: recompute from the question's numbers with atan2 (single rounding)
# ─────────────────────────────────────────────────────────────────────────────

def _bearing_deg(east, north):
    return int(half_up(math.degrees(math.atan2(east, north)) % 360, 0)) % 360


def bearing_expect(q):
    """Expected 3-figure bearing (integer) for the bearing questions we can recompute, else None."""
    t = plain(q)
    m = re.search(r'is (\d+) km North and (\d+) km East of', t)
    if m:
        return _bearing_deg(int(m.group(2)), int(m.group(1)))
    m = re.search(r'(\d+) km East and (\d+) km South of', t)
    if m:
        return _bearing_deg(int(m.group(1)), -int(m.group(2)))
    m = re.search(r'travels (\d+) km South then (\d+) km East', t)
    if m:
        return _bearing_deg(int(m.group(2)), -int(m.group(1)))
    legs = re.findall(r'(\d+(?:\.\d+)?) km on (?:bearing )?(\d{3})°|(\d+(?:\.\d+)?) km on bearing (\d{3})°', t)
    legs = [(float(a or c), int(b or d)) for a, b, c, d in legs]
    if not legs:
        legs = [(float(a), int(b)) for a, b in re.findall(r'(\d+(?:\.\d+)?) km on bearing (\d{3})°', t)]
    m2 = re.search(r'sails (\d+) km on bearing (\d{3})°, then (\d+) km on bearing (\d{3})°', t)
    if m2 and 'bearing of the ship from the starting point' in t:
        legs = [(float(m2.group(1)), int(m2.group(2))), (float(m2.group(3)), int(m2.group(4)))]
        e = sum(d * math.sin(math.radians(b)) for d, b in legs)
        n = sum(d * math.cos(math.radians(b)) for d, b in legs)
        return _bearing_deg(e, n)
    if len(legs) >= 2 and re.search(r'back to the start|return directly|directly back', t):
        e = sum(d * math.sin(math.radians(b)) for d, b in legs)
        n = sum(d * math.cos(math.radians(b)) for d, b in legs)
        return _bearing_deg(-e, -n)
    return None


def check_bearing_problem(name, p, where):
    q, raw, at = p['question'], p.get('correct_answer_raw'), p.get('answer_type')
    t = plain(q)
    # An integer bearing must be asked for "to the nearest degree", never "to 1 d.p."
    if re.search(r'(find|calculate|work out)[^.?]*\bbearing', t, re.I):
        clauses = re.split(r'(?<=[.;?])\s+|\s+and\s+', t)
        for c in clauses:
            if '1 d.p.' in c and not re.search(r'distance|East|North|height|length|[A-Z]{2}\b', c):
                issue('answer', where, f'bearing keyed to the nearest degree but worded "1 d.p.": "{c[:90]}"')
    want = bearing_expect(q)
    if want is None or raw is None:
        return
    parts = [x for x in raw_parts(raw)]
    got = {int(float(x)) % 360 for x in parts if re.fullmatch(r'-?\d+', x.strip())}
    if want not in got:
        issue('answer', where, f'bearing {sorted(got)} does not match atan2 recomputation {want:03d}: "{t[:80]}"')


def bearing_sweep(topics):
    """Many seeds over the recomputable bearing variants, to catch single-digit double-rounding slips."""
    cfg = topics['bearings']
    for diff in TIERS:
        names = []
        for i in range(40):
            random.seed(BASE_SEED + i)
            for v in cfg['variants_func'](diff, 'standard') or []:
                if v.__name__ not in names:
                    names.append(v.__name__)
        for name in names:
            for r in range(120):
                random.seed(BASE_SEED * 11 + r)
                try:
                    p = generate(cfg, diff, 'standard', name)
                except Exception:   # noqa: BLE001
                    continue
                check_bearing_problem(name, p, f'bearings/{diff}/{name}#s{r}')


def make_choice():
    original = random.choice
    state = {'row': 0}

    def choice(seq):
        try:
            if len(seq) > 1 and all(isinstance(e, (tuple, list)) and len(e) >= 2 for e in seq):
                return seq[state['row'] % len(seq)]
        except TypeError:
            pass
        return original(seq)

    return original, choice, state


def generate(cfg, diff, mode, name):
    with contextlib.redirect_stdout(io.StringIO()):
        return cfg['func'](diff, mode, variant_name=name)


def sweep():
    original_choice, choice, state = make_choice()
    topics = TOPICS['gcse']['maths']
    n_variants = n_questions = 0
    for slug, cfg in topics.items():
        for diff in TIERS:
            for mode in ('standard', 'mcq'):
                names = []
                for i in range(40):
                    random.seed(BASE_SEED + i)
                    for v in cfg['variants_func'](diff, mode) or []:
                        if v.__name__ not in names:
                            names.append(v.__name__)
                runs = MCQ_RUNS_PER_VARIANT if mode == 'mcq' else RUNS_PER_VARIANT
                for name in names:
                    n_variants += 1
                    for r in range(runs):
                        where = f'{slug}/{diff}/{name}#{r}'
                        state['row'] = r
                        random.seed(BASE_SEED * 7 + r)
                        random.choice = choice
                        try:
                            p = generate(cfg, diff, mode, name)
                        except Exception as exc:   # noqa: BLE001
                            random.choice = original_choice
                            issue('crash', where, repr(exc)[:120])
                            continue
                        finally:
                            random.choice = original_choice
                        n_questions += 1
                        check_problem(slug, diff, mode, name, p, where)
    return n_variants, n_questions


def check_problem(slug, diff, mode, name, p, where):
    q, sol = plain(p['question']), plain(p['solution'])
    raw, at = p.get('correct_answer_raw'), p.get('answer_type')

    if p.get('options'):
        check_mcq(p, where)
        mcq_semantic(slug, name, p, where)

    stated = bool(_ROUND_WORDS.search(q + ' ' + sol))
    for msg in scan_arithmetic(sol, stated):
        issue('arithmetic', where, msg)

    if raw is not None and at:
        check_stated_rounding(q, raw, at, where)
        if at in ('number', 'number_fields', 'fraction', 'ratio', 'linear', 'surd', 'quadratic_roots') \
                and not (at == 'number_fields' and '\x1e' in str(raw)):
            try:
                ok = check_answer(at, raw, user_form(at, raw))['correct']
            except Exception as exc:   # noqa: BLE001
                ok = f'EXC {exc!r}'
            if ok is not True:
                issue('checker', where, f'correct answer {raw!r} ({at}) not accepted: {ok}')
            for wrong in mutations(at, raw):
                try:
                    bad = check_answer(at, raw, wrong)['correct']
                except Exception:   # noqa: BLE001
                    bad = False
                if bad:
                    issue('checker', where, f'wrong answer {wrong!r} accepted for {raw!r} ({at})')
        verdict = independent_check(slug, name, p)
        if verdict is False:
            issue('answer', where, f'independent check failed: "{q[:90]}" expected {str(raw)[:30]}')

    if slug == 'bearings':
        check_bearing_problem(name, p, where)
    for label, text in (('question', q), ('solution', sol)):
        m = _SIGN_ARTEFACT.search(text)
        if m:
            issue('cosmetic', where, f'sign artefact "{m.group().strip()}" in {label}: "{text[max(0, m.start() - 30):m.end() + 20]}"')
    if name == '_vectors_diff_geometric_ratio':
        for a, b in re.findall(r'(\d+):(\d+)', q):
            if a == b:
                issue('cosmetic', where, f'degenerate ratio {a}:{b}')
    if re.search(r'x\^2 [+-] \d*x \+ -\d', q):
        issue('cosmetic', where, 'sign formatting "+ -" in question')


def main():
    probe_checker()
    static_scan()
    n_variants, n_questions = sweep()
    bearing_sweep(TOPICS['gcse']['maths'])
    by_kind = {}
    for kind, where, detail in ISSUES:
        by_kind.setdefault(kind, []).append((where, detail))
    print(f'GCSE maths correctness: {n_variants} variant/tier/mode combinations, {n_questions} questions generated')
    if ISSUES:
        print(f'{len(ISSUES)} issue(s):')
        for kind, rows in sorted(by_kind.items()):
            print(f'  [{kind}] {len(rows)}')
            seen = set()
            shown = 0
            for where, detail in rows:
                key = (where.rsplit('#', 1)[0], detail[:40])
                if key in seen:
                    continue
                seen.add(key)
                print(f'    {where}: {detail}')
                shown += 1
                if shown >= 12:
                    print('    ...')
                    break
        sys.exit(1)
    print('All GCSE maths correctness checks passed.')


if __name__ == '__main__':
    main()
