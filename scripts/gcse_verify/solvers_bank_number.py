"""Bank-item re-solvers: number, fractions/decimals/percentages, factors, Pythagoras, measures, bearings, trigonometry.

Each entry is keyed by the item's digest (``python scripts/test_gcse_maths_verification_smoke.py --print-digests``)
and works the answer out from the numbers in the displayed question.  See ``solvers_bank``.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

import sympy

from .core import Approx, Cannot
from .solvers_bank import (add, calc, exactish, is_prime, is_square, is_val, lcm, pick, root, simplest, sx,
                           val, values)

PI = math.pi


def F(x, y=1):
    return Fraction(x) / Fraction(y)


def gcd_all(xs):
    g = 0
    for x in xs:
        g = math.gcd(g, int(x))
    return g


def lcm_all(xs):
    out = 1
    for x in xs:
        out = lcm(out, int(x))
    return out


def is_whole(v):
    return v is not None and v.denominator == 1


# ───────────────────────────── BIDMAS ─────────────────────────────

_OP_NAME = {'+': 'addition', '-': 'subtraction', '×': 'multiplication', '÷': 'division', '^': 'indices'}
_PREC = {'^': 3, '×': 2, '÷': 2, '+': 1, '-': 1}


def first_operation(c):
    """The operation BIDMAS does first in the expression written in the question (no brackets in it)."""
    e = c.arith()
    if '(' in e:
        raise Cannot('first_operation does not handle brackets')
    ops = [(-_PREC[ch], i, ch) for i, ch in enumerate(e) if ch in _PREC]
    name = _OP_NAME[min(ops)[2]]
    return pick(lambda t: t.strip().lower() == name, f'the operation done first is {name}')


def arithmetic(c):
    return [calc(c.arith())]


add('bidmas', {
    '46a8c827b617': first_operation,                    # which operation is done first in 3 + 4 x 5
    'c34249ff6ac5': arithmetic, 'aeb202fa4816': arithmetic, '198ad44fd5c0': arithmetic,
    '000b2f7bf5fa': arithmetic, '6175fde23c7a': arithmetic, '4bc29cddfee2': arithmetic,
    '734d9ce38036': arithmetic, '7179d4c76daf': arithmetic, 'cd341dacece6': arithmetic,
    '090102e52a4c': arithmetic, '8d4d452d5137': arithmetic, 'de6a72371a71': arithmetic,
    '1e2b1883daf4': arithmetic,
})


# ───────────────────────────── fractions, decimals, percentages ─────────────────────────────

def dec_and_pct(c):
    x = c.n[0] / c.n[1]

    def test(t):
        m = re.fullmatch(r'\s*([\d.]+) and ([\d.]+)%\s*', t)
        return bool(m) and F(m.group(1)) == x and F(m.group(2)) / 100 == x
    return pick(test, f'{x} as a decimal and {x * 100}%')


add('fdp', {
    'b75710af999f': lambda c: [c.n[0] * 100],                                       # 0.25 as a percentage
    'b2de8d6815d0': lambda c: [c.n[0] / 100],                                       # 50% as a decimal
    '928c205e3716': lambda c: [c.n[0] / c.n[1]],                                    # 1/4 as a decimal
    'c517a599698e': lambda c: simplest(c.n[0]),                                     # 0.75 as a fraction, simplest form
    '5c46977a9f20': lambda c: simplest(c.n[0] / 100),                               # 20% as a fraction, simplest form
    'e4ae98ad32ff': lambda c: [c.n[0] / c.n[1] * 100],                              # 3/5 as a percentage
    'cffd533ea26c': lambda c: is_val(c.n[0]),                                       # 0.125 as a fraction
    '3757907ddc80': lambda c: is_val(c.n[0] / 100),                                 # 37.5% as a fraction
    '5b146eae23a1': lambda c: pick(lambda t: val(t) == max(values(c.texts)), 'the largest value'),
    'dd97af4c33f0': lambda c: [c.n[0] / c.n[1]],                                    # 1/3 as a decimal to 2 d.p.
    '7ab26dbec5b5': lambda c: [c.n[0] * (1 + c.n[1] / 100)],                        # increase 80 by 10%
    'a0910ef9d500': lambda c: [(c.n[0] - c.n[1]) / c.n[0] * 100],                   # price drops 50 to 40
    '53b6a0fa2e12': lambda c: [F(int(c.n[0] * 10), 9)],                             # 0.2 recurring as a fraction
    'd9eccb616a3d': dec_and_pct,                                                    # 3/8 as decimal and percentage
    'ca4bed529ea7': lambda c: pick(lambda t: val(t) == c.n[0] / c.n[1], 'equals the fraction in the question'),
    '63ff7ac08d0a': lambda c: [c.n[0] / c.n[1] * c.n[2]],                           # 3/8 of 240
    '7373f1c0ff22': lambda c: [c.n[0] * (1 + c.n[1] / 100)],                        # 150 increased by 12%
    '0510547f2998': lambda c: [c.n[0] * (1 - c.n[1] / 100)],                        # 80 reduced by 25%
    '531a98af4ca9': lambda c: [(c.n[1] - c.n[0]) / c.n[0] * 100],                   # 50 to 65 percentage increase
    '55baec307617': lambda c: [c.n[1] / (1 - c.n[0] / 100)],                        # after 20% discount 56, original
    'd85b97b3c4a0': lambda c: [c.n[0] * (1 + c.n[1] / 100) * (1 - c.n[2] / 100)],   # +10% then -10%
    'f19eb05d36ac': lambda c: [c.n[0] * max(c.n[1], c.n[2]) / (c.n[1] + c.n[2])],   # share 165 in 4:7, larger share
    'c9cad793dd4b': lambda c: [(c.n[1] - c.n[0]) / c.n[0] * 100],                   # bought 40 sold 52 profit %
    '38aeab7adb0f': lambda c: [c.n[0] * (1 - c.n[1] / c.n[2])],                     # 420 pupils, 5/12 walk, not walk
    '27f3a73ae928': lambda c: [c.n[2] / ((1 + c.n[0] / 100) * (1 - c.n[1] / 100))],  # +15% then -10% gives 103.50
})


# ───────────────────────────── multiples and factors ─────────────────────────────

_SUPER = {'²': 2, '³': 3, '⁴': 4}


def prime_product(text):
    """The number a product of primes written as '2³ × 3' stands for, or None when a factor is not prime."""
    total = 1
    for part in re.split(r'\s*×\s*', text.replace(' only', '').strip()):
        m = re.fullmatch(r'(\d+)([²³⁴]?)', part.strip())
        if not m or not is_prime(int(m.group(1))):
            return None
        total *= int(m.group(1)) ** _SUPER.get(m.group(2), 1)
    return total


def integer_of(t):
    v = val(t)
    return int(v) if is_whole(v) else None


def prime_property(c):
    odd_primes = [p for p in range(3, 200) if is_prime(p)]
    tests = {
        'even': lambda p: p % 2 == 0, 'odd': lambda p: p % 2 == 1,
        'multiples of 3': lambda p: p % 3 == 0, 'square': is_square,
    }
    return pick(lambda t: all(tests[t.strip().lower()](p) for p in odd_primes), 'true of every odd prime')


def digits_for_six(c):
    m = re.search(r'(\d)_(\d) is divisible by (\d+)', c.stem)
    if not m:
        raise Cannot('no "a_b is divisible by n" in the question')
    k = int(m.group(3))
    ok = {d for d in range(10) if int(m.group(1) + str(d) + m.group(2)) % k == 0}
    return pick(lambda t: set(int(x) for x in re.findall(r'\d', t)) == ok, f'digits {sorted(ok)}')


def hcf_lcm_identity(c):
    a, b = int(c.n[0]), int(c.n[1])
    if (math.gcd(a, b), lcm(a, b)) != (int(c.n[2]), int(c.n[3])):
        raise Cannot('the HCF and LCM stated in the question are wrong')
    asked = re.search(r'Does (\d+) × (\d+) = (\d+) × (\d+)\?', c.stem)
    if not asked:
        raise Cannot('no "Does p × q = r × s?" in the question')
    p_, q_, r_, s_ = (int(x) for x in asked.groups())
    if {p_, q_} != {math.gcd(a, b), lcm(a, b)} or {r_, s_} != {a, b}:
        raise Cannot('the products asked about are not HCF x LCM and the two numbers')
    left, right = p_ * q_, r_ * s_
    if left != right:
        return pick(lambda t: t.strip().lower() == 'no', 'No')
    return pick(lambda t: (m := re.fullmatch(r'yes, both equal (\d+)', t.strip().lower())) is not None
                and int(m.group(1)) == left, f'Yes, both equal {left}')


def next_meeting(c):
    a, b, hour, minute = int(c.n[0]), int(c.n[1]), int(c.n[2]), int(c.n[3])
    gap = lcm(a, b)

    def test(t):
        m = re.fullmatch(r'\s*(\d+):(\d+)\s*', t)
        return bool(m) and int(m.group(1)) * 60 + int(m.group(2)) == hour * 60 + minute + gap
    return pick(test, f'{gap} minutes after the start')


def paired_numbers(c):
    """The numbers written before ' (=' in a question such as 'HCF of 72 (= 2^3 x 3^2) and 120 (= ...)'."""
    return [int(x) for x in re.findall(r'(\d+) \(=', c.stem)]


def why_not_prime(c):
    """A reason works when it is true of the number and no prime has it (so it really shows the number is not prime)."""
    n = int(c.n[0])
    primes = [p for p in range(2, 200) if is_prime(p)]
    reasons = {
        'it is odd': lambda k: k % 2 == 1,
        'it is less than 40': lambda k: k < 40,
        'it has exactly two factors': lambda k: sum(1 for d in range(1, k + 1) if k % d == 0) == 2,
    }

    def holds(text):
        key = text.strip().lower()
        if key in reasons:
            return reasons[key]
        m = re.fullmatch(r'it is divisible by (\d+) and (\d+)', key)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            return lambda k: k % a == 0 and k % b == 0 and a > 1 and b > 1
        raise Cannot(f'unknown reason {text!r}')

    def test(t):
        f = holds(t)
        return f(n) and not any(f(p) for p in primes)
    return pick(test, f'is true of {n} but of no prime')


add('multiples_factors', {
    '9fc10ebbcc29': lambda c: pick(lambda t: is_whole(val(t)) and val(t) % c.n[0] == 0, f'a multiple of {c.n[0]}'),
    '2b98ac3d2294': lambda c: pick(lambda t: is_whole(val(t)) and c.n[0] % val(t) == 0, f'a factor of {c.n[0]}'),
    '762d08cec45b': lambda c: [c.n[0] * c.n[1]],                                    # 4th multiple of 5
    '9341b5963474': lambda c: pick(lambda t: is_prime(integer_of(t)), 'is prime'),
    'bbe085a5eb2e': lambda c: pick(lambda t: is_whole(val(t)) and c.n[0] % val(t) != 0, f'not a factor of {c.n[0]}'),
    '32cbbc6e84a6': lambda c: [F(math.gcd(int(c.n[0]), int(c.n[1])))],              # HCF of 12 and 18
    'ca4d350cfb9e': lambda c: [F(lcm(int(c.n[0]), int(c.n[1])))],                   # LCM of 4 and 6
    'cbd06ecb1dad': lambda c: pick(lambda t: prime_product(t) == c.n[0], f'a product of primes equal to {c.n[0]}'),
    '8c62f0da7244': lambda c: pick(lambda t: prime_product(t) == c.n[0], f'a product of primes equal to {c.n[0]}'),
    '650b4ae17fba': prime_property,
    '1c0e4946c132': why_not_prime,                                                  # why 33 is not prime
    '3f415f0e59a4': lambda c: [F(math.gcd(int(c.n[0]), int(c.n[1])))],              # HCF of 16 and 24
    'e658a77a98eb': lambda c: [F(lcm(int(c.n[0]), int(c.n[1])))],                   # LCM of 5 and 12
    'ba8030a7d2f7': lambda c: pick(lambda t: prime_product(t) == c.n[0], f'a product of primes equal to {c.n[0]}'),
    'c2e4dbb0ce39': lambda c: pick(lambda t: (m := re.match(r'\s*(\d+) and (\d+)\s*$', t)) is not None
                                   and int(m.group(1)) * int(m.group(2)) == c.n[0], f'two numbers with product {c.n[0]}'),
    '76cf4d6edee6': next_meeting,                                                   # buses every 8 and 12 minutes
    '11433e9d06aa': lambda c: [F(math.gcd(int(c.n[0]), int(c.n[1])))],              # largest square tile, 120 by 84
    '77cc5fa750c5': lambda c: [F(sum(1 for d in range(1, int(c.n[0]) + 1)
                                     if int(c.n[0]) % d == 0 and int(c.n[1]) % d == 0))],   # common factors of 12 and 18
    '2372f0de4ba1': lambda c: [F(math.gcd(*paired_numbers(c)))],                    # HCF of 72 and 120
    'e7a10ff5f23b': digits_for_six,                                                 # 5_4 divisible by 6
    '41857bb1029e': lambda c: [F(gcd_all(c.n))],                                    # HCF of 24, 36 and 60
    '9cb2528b5cda': lambda c: [F(lcm_all(c.n))],                                    # LCM of 4, 6 and 10
    '46b407f316cd': hcf_lcm_identity,                                               # 7 x 70 = 14 x 35 ?
    'e7494c37dc0f': lambda c: [c.n[0] * c.n[1] / c.n[2]],                           # HCF 6, LCM 72, one number 24
    '4275d70a92b9': lambda c: [F(lcm(*paired_numbers(c)))],                         # LCM of 12 and 18
})


# ───────────────────────────── decimals ─────────────────────────────

def ordered_values(c):
    want = sorted(c.n)

    def test(t):
        got = [val(x) for x in t.split(',')]
        return got == want
    return pick(test, 'smallest to largest')


add('decimals', {
    '0bad6320cd7c': lambda c: pick(lambda t: val(t) == max(values(c.texts)), 'the largest value'),
    'bc57517553bf': lambda c: [calc(c.arith())], '6c57f67cad4a': lambda c: [calc(c.arith())],
    '0d3627d1f62c': lambda c: [calc(c.arith())], '0480831ed0a9': lambda c: [calc(c.arith())],
    '773812c6456e': lambda c: [calc(c.arith())], '6fbbd1012207': lambda c: [calc(c.arith())],
    'cf371e9e4594': lambda c: [calc(c.arith())], 'f0f652072911': lambda c: [calc(c.arith())],
    'd1697344d644': lambda c: [calc(c.arith())], '70662c177240': lambda c: [calc(c.arith())],
    'fbab5153e41b': lambda c: [c.n[0] / c.n[1]],                                    # 3/8 as a decimal
    'c4a44cd8e194': lambda c: [c.n[0]],                                             # round 4.567 to 2 d.p.
    '9fcb67f84d9d': lambda c: simplest(F(int(c.n[0] * 10), 9)),                     # 0.3 recurring, simplest form
    '8e00daa8ae72': ordered_values,
    '6e3177c902a1': lambda c: pick(lambda t: val(t) == c.n[0] + F(5, 10 ** (int(c.n[1]) + 1)),
                                   'the upper bound of a value given to the stated decimal places'),
    '460a2f5b9ee9': lambda c: [c.n[1] / c.n[0]],                                    # 2.4 kg costs 7.20
    '4e23096ddb5c': lambda c: simplest(c.n[0]),                                     # 0.625 in simplest form
})


# ───────────────────────────── Pythagoras ─────────────────────────────

TRIPLES = ((3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25))


def pythagoras_formula(c):
    """A formula for the legs a, b and hypotenuse c is right when both sides agree on every right-angled triple."""
    def test(t):
        left, right = [sx(s) for s in t.split('=')]
        a, b, h = sympy.symbols('a b c')
        return all((left - right).subs({a: x, b: y, h: z}) == 0 for x, y, z in TRIPLES)
    return pick(test, 'true for 3-4-5, 5-12-13, 8-15-17, 7-24-25')


def evaluates_to(x):
    def test(t):
        return abs(float(sympy.N(sx(t))) - float(x)) < 1e-9
    return test


def space_diagonal(c):
    s = int(c.n[0] ** 2 + c.n[1] ** 2 + c.n[2] ** 2)
    return pick(lambda t: f'√{s}' in t and f'{math.sqrt(s):.2f}' in t, f'√{s} (about {math.sqrt(s):.2f})')


def right_angled(c):
    a, b, h = sorted(int(x) for x in c.n[:3])
    ans = 'yes' if a * a + b * b == h * h else 'no'
    return pick(lambda t: t.strip().lower() == ans, ans)


def rectangle_area_from_diagonal(c):
    """Area of a rectangle from its diagonal and one side: the other side by Pythagoras, then side times side."""
    diag = int(re.search(r'diagonal of (\d+)', c.stem).group(1))
    side = int(re.search(r'one side of (\d+)', c.stem).group(1))
    if diag <= side:
        raise Cannot('the diagonal must be longer than the side')
    return [exactish(side * math.sqrt(diag ** 2 - side ** 2))]


def distance_between_points(c):
    """Distance between the two points written (x, y) in the question, by Pythagoras on the differences."""
    pts = [(int(x), int(y)) for x, y in re.findall(r'\((-?\d+),\s*(-?\d+)\)', c.stem)]
    if len(pts) != 2:
        raise Cannot(f'expected two points, found {pts}')
    return [exactish(math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]))]


add('pythagoras', {
    '41bb0a2b4cf9': rectangle_area_from_diagonal,                                   # diagonal 17, side 8: area
    '73e15ff484d0': distance_between_points,                                        # A (1, 2) to B (7, 10)
    'ea9c92542c88': lambda c: [root(c.n[0] ** 2 + c.n[1] ** 2)],                    # legs 6 and 8
    '9268cccf7426': lambda c: [root(c.n[0] ** 2 - c.n[1] ** 2)],                    # hypotenuse 13, side 5
    '46d54d281364': pythagoras_formula,
    'e034b9e8ec2f': right_angled,                                                   # 7, 24, 25
    '8887750e9f47': lambda c: [root(c.n[0] ** 2 + c.n[1] ** 2)],                    # rectangle 9 by 12, diagonal
    '75d34ba89aa3': space_diagonal,                                                 # cuboid 3 x 4 x 5
    '230298cd2634': lambda c: pick(evaluates_to(math.hypot(float(c.n[2] - c.n[0]), float(c.n[3] - c.n[1]))),
                                   'a calculation that gives the distance'),
    '81906023f08c': lambda c: [root(c.n[0] ** 2 - c.n[1] ** 2)],                    # 10 m ladder, 6 m wall
    '6ecb3b0c8247': right_angled,                                                   # 5, 12, 14
})


# ───────────────────────────── compound measures ─────────────────────────────

def floats(c):
    density = c.n[0] / c.n[1]
    water = c.n[2]
    sinks = density > water
    return pick(lambda t: t.strip().lower().startswith('yes') == (not sinks)
                and (('<' in t) == (not sinks)) and ('>' in t) == sinks
                and not t.lower().startswith(('exactly', 'cannot')), 'floats when less dense than water')


add('compound_measures', {
    '92023abde6bc': lambda c: [c.n[0] / c.n[1]],                                    # 150 km in 2.5 h
    '19bfcfc74bce': lambda c: [c.n[0] * c.n[1]],                                    # 80 km/h for 3.5 h
    '7963cdae54e7': lambda c: [c.n[0] / c.n[1]],                                    # 240 km at 60 km/h
    '1f7872830aba': lambda c: [c.n[0] / c.n[1]],                                    # mass 560 g, volume 80 cm3
    '08144339f331': lambda c: [c.n[0] * c.n[1]],                                    # density 8.9, 100 cm3
    '132df6323edf': lambda c: [c.n[0] * 1000 / 3600],                               # 72 km/h in m/s
    '30c7e55e1e43': lambda c: [c.n[0] * 3600 / 1000],                               # 15 m/s in km/h
    'c66f42706d9d': lambda c: [c.n[0] / c.n[1]],                                    # 600 N on 30 m2
    'adb16c4197df': lambda c: [2 * c.n[0] * c.n[1] / (c.n[0] + c.n[1])],            # 40 out, 60 back, average speed
    '71b36d2d6ff3': floats,                                                         # 80 g, 120 cm3: does it float
    '7f4e269eb6f9': lambda c: [c.n[0] / c.n[1]],                                    # 24,000 people in 40 km2
    '8b601053e147': lambda c: [c.n[0] * F(10 ** 6, 1000)],                          # 2.7 g/cm3 in kg/m3
    'df1c566af552': lambda c: [c.n[0] * c.n[1]],                                    # 5 L/min for 20 min
    '2e2a48c231b3': lambda c: [c.n[0] / c.n[1]],                                    # 500 N on 25 cm2
    '61e088843bcb': lambda c: [(c.n[0] + c.n[2] + c.n[4]) / (c.n[1] + c.n[3] + c.n[5])],   # three legs, average speed
})


# ───────────────────────────── mensuration ─────────────────────────────

def pi_coefficient(c):
    r = c.n[0]
    return pick(lambda t: (m := re.match(r'\s*(\d+)π', t)) is not None and F(m.group(1)) == r * r,
                f'{r * r}π')


add('mensuration', {
    '3325a11a76b5': lambda c: [c.n[0] * c.n[1] / 2],                                # triangle base 10, height 6
    '6bdfa7c2f363': lambda c: [Approx(PI * float(c.n[0]))],                         # circumference, diameter 14
    '264815e1d101': lambda c: [c.n[0] * c.n[1] * c.n[2]],                           # cuboid 5 x 3 x 4
    '303780b23d4e': pi_coefficient,                                                 # exact area, radius 6
    '5b5cffb36764': lambda c: [(c.n[0] + c.n[1]) / 2 * c.n[2]],                     # trapezium 8, 12, height 5
    'b37d8fa193dd': lambda c: [Approx(PI * float(c.n[0] ** 2 * c.n[1]))],           # cylinder r 4, h 10
    '4df8a7f5572e': lambda c: [Approx(4 / 3 * PI * float(c.n[0] ** 3))],            # sphere r 3 volume
    '9d49c551a49a': lambda c: [Approx(4 * PI * float(c.n[0] ** 2))],                # sphere r 5 surface area
    '1503f6f3a6ae': lambda c: [Approx(PI * float(c.n[0] ** 2 * c.n[1] / 360))],     # sector r 8, 90 degrees
    '4c0c374833fc': lambda c: [2 * (c.n[0] * c.n[1] + c.n[0] * c.n[2] + c.n[1] * c.n[2])],  # cuboid surface area
    'a3f1f575328f': lambda c: [Approx(PI * float(c.n[0] ** 2 * c.n[1]) / 3)],       # cone r 6, h 9
    'c6671c01bdb5': lambda c: [Approx(2 * PI * float(c.n[0] * c.n[1] / 360))],      # arc length r 10, 120 degrees
    '5602bf882f5d': lambda c: [c.n[2] * (c.n[1] / c.n[0]) ** 3],                    # similar cylinders 1 : 3, V = 20
    '7f0ae1b06743': lambda c: [Approx(4 / 3 * PI * float(c.n[0] ** 3 * c.n[1]))],    # rubber ball r 4, density 1.2
    'cff2a5382636': lambda c: [Approx(PI * float(c.n[2]) / 3 * float(c.n[0] ** 2 + c.n[0] * c.n[1] + c.n[1] ** 2))],
    'bc3c5d56420b': lambda c: [Approx(PI * float(c.n[0] ** 2 * c.n[1]) + 2 / 3 * PI * float(c.n[2] ** 3))],  # silo
    'ca01635809c6': lambda c: [Approx(PI * float(c.n[0]) * (float(c.n[0]) + math.hypot(float(c.n[0]), float(c.n[1]))))],
    'ba2842c89804': lambda c: [c.n[2] * (c.n[1] / c.n[0]) ** 2],                    # similar solids 2 : 3, SA 48
})


# ───────────────────────────── bearings ─────────────────────────────

COMPASS = {'north': 0, 'east': 90, 'south': 180, 'west': 270}


def due(c):
    word = next(w for w in COMPASS if w in c.stem.lower())
    return [F(COMPASS[word])]


def quadrant(c):
    b = float(c.n[0])
    name = 'NE' if b < 90 else 'SE' if b < 180 else 'SW' if b < 270 else 'NW'
    return pick(lambda t: t.strip().startswith(name + ' ') or t.strip() == name, f'the {name} quadrant')


def quarter_bearing(c):
    m = re.search(r'([NS])\s*(\d+)°\s*([EW])', c.stem)
    a = int(m.group(2))
    table = {('N', 'E'): a, ('N', 'W'): 360 - a, ('S', 'E'): 180 - a, ('S', 'W'): 180 + a}
    return [F(table[(m.group(1), m.group(3))])]


def displacement(legs):
    e = sum(d * math.sin(math.radians(b)) for d, b in legs)
    n = sum(d * math.cos(math.radians(b)) for d, b in legs)
    return e, n


def legs_of(c):
    pairs = re.findall(r'(\d+) km(?: away)? on (?:a )?(?:bearing )?(\d+)°', c.stem)
    return [(float(d), float(b)) for d, b in pairs]


def bearing_of(e, n):
    return math.degrees(math.atan2(e, n)) % 360


def distance_between_ships(c):
    (d1, b1), (d2, b2) = legs_of(c)
    e1, n1 = displacement([(d1, b1)])
    e2, n2 = displacement([(d2, b2)])
    return [Approx(math.hypot(e2 - e1, n2 - n1))]


def back_bearing_formula(c):
    """The return bearing is the bearing of the reversed displacement, worked out with coordinates."""
    def test(t):
        for theta in (65, 230, 10, 300):
            s = t.replace('\\theta', f'({theta})')
            e, n = displacement([(1.0, float(theta))])
            if abs(float(calc(s)) - bearing_of(-e, -n)) > 1e-9:
                return False
        return True
    return pick(test, 'gives the back bearing for every bearing tried')


add('bearings', {
    '0fbf9bea334a': due,                                                            # due East
    '063d100b9c66': lambda c: [(c.n[0] + 180) % 360],                               # back bearing of 065
    'bad4fc2267fd': lambda c: [(c.n[0] + 180) % 360],                               # back bearing of 230
    'ad8a12cdb230': quarter_bearing,                                                # N45W
    '4fcfa4747799': quarter_bearing,                                                # S30E
    'c777a259d3d6': quadrant,                                                       # 290 degrees
    '496ea3eacb9e': lambda c: [Approx(float(c.n[1]) * math.sin(math.radians(float(c.n[0]))))],   # east: 40 sin 60
    'c74bf642c05d': lambda c: [Approx(float(c.n[1]) * math.cos(math.radians(float(c.n[0]))))],   # north: 50 cos 30
    'eb3e3b638e5a': lambda c: [abs(c.n[1] - c.n[0])],                               # between 050 and 140
    'bd0b36e8e801': lambda c: [exactish(math.hypot(float(c.n[0]), float(c.n[1])))],  # 30 N, 40 E
    '2b0fb6295ba4': lambda c: [exactish(bearing_of(float(c.n[1]), float(c.n[0])))],  # 30 N, 30 E: bearing
    'a28f9ce7863b': lambda c: [abs(c.n[2] - c.n[0])],                               # ships on 040 and 130
    'e44711f668fa': distance_between_ships,                                         # OA = 80 on 030, OB = 60 on 090
    '2ce353347cfd': back_bearing_formula,
    '8207977e52fd': lambda c: [exactish(bearing_of(float(c.n[0]), float(c.n[1])))],  # 20 East then 20 North
    'b89579cfe00e': lambda c: [Approx(math.hypot(*displacement(legs_of(c))))],      # 45 km on 030 then 60 km on 120
    '071a75ce1ed2': lambda c: [Approx((bearing_of(*displacement(legs_of(c))) + 180) % 360)],   # return bearing
    '300494877bfb': distance_between_ships,                                         # A 70 km on 025, B 90 km on 095
})


# ───────────────────────────── trigonometry ─────────────────────────────

def exact_trig_value(c):
    """The option whose value equals sin, cos or tan of the angle in the question."""
    m = re.search(r'(sin|cos|tan)\s*(\d+)°', c.stem)
    f = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan}[m.group(1)]
    want = f(math.radians(int(m.group(2))))

    def test(t):
        s = re.sub(r'\\tfrac\s+(√\(\d+\)|\d+)\s+(√\(\d+\)|\d+)', r'((\1)/(\2))', t)
        return abs(float(sympy.N(sx(s))) - want) < 1e-9
    return pick(test, f'equals {m.group(1)} {m.group(2)} degrees')


def sine_ratio(c):
    """sin of the angle of a 3-4-5 triangle is opposite over the option's side."""
    opp, adj, hyp = 3.0, 4.0, 5.0
    theta = math.atan2(opp, adj)
    sides = {'adjacent': adj, 'hypotenuse': hyp, 'opposite': opp}
    return pick(lambda t: abs(opp / sides[t.strip().lower()] - math.sin(theta)) < 1e-12,
                'opposite divided by it gives sin of the angle')


def sine_area_formula(c):
    """Sides a = CB and b = CA with angle C between them; the true area comes from the coordinates (shoelace)."""
    a_, b_, big_c = 5.0, 7.0, math.radians(40)
    pc, pa, pb = (0.0, 0.0), (b_, 0.0), (a_ * math.cos(big_c), a_ * math.sin(big_c))
    true_area = abs((pa[0] - pc[0]) * (pb[1] - pc[1]) - (pb[0] - pc[0]) * (pa[1] - pc[1])) / 2

    def test(t):
        s = (t.replace('\\tfrac 1 2', '(1/2)').replace('\\sin C', ' s ').replace('\\cos C', ' k ').replace('×', '*'))
        if not re.fullmatch(r'[()\d\s/*abks]*', s):
            raise Cannot('not a formula in a, b and C')
        a, b, s_, k = sympy.symbols('a b s k')
        value = sx(s).subs({a: a_, b: b_, s_: math.sin(big_c), k: math.cos(big_c)})
        return abs(float(value) - true_area) < 1e-9
    return pick(test, 'gives the area of a triangle with sides a, b and angle C between them')


def cosine_rule_angle(c):
    """cos A from the sides a, b, c: checked on triangles built from a chosen angle A, so the rule is not assumed."""
    cases = [(50.0, 7.0, 9.0), (70.0, 5.0, 8.0), (110.0, 4.0, 6.0)]

    def test(t):
        rhs = sx(t.split('=', 1)[1])
        a, b, cc = sympy.symbols('a b c')
        for angle, b_, c_ in cases:
            th = math.radians(angle)
            a_ = math.hypot(c_ - b_ * math.cos(th), b_ * math.sin(th))        # distance from B=(c,0) to C=(b cos A, b sin A)
            if abs(float(rhs.subs({a: a_, b: b_, cc: c_})) - math.cos(th)) > 1e-9:
                return False
        return True
    return pick(test, 'equals cos A on triangles built from a known angle')


add('trigonometry', {
    'd5c271303b47': sine_ratio,
    'affe6d8ffa4a': exact_trig_value,                                               # exact cos 60
    '4955f0684fe7': sine_area_formula,
    '645ecc6c79b3': lambda c: [root(c.n[0] ** 2 + c.n[1] ** 2)],                    # opposite 3, adjacent 4
    'ff41b25457e7': exact_trig_value,                                               # exact sin 45
    'd1609bb6b58b': exact_trig_value,                                               # exact tan 30
    '74b5d9001f35': cosine_rule_angle,
    '0ce6a30f37d9': lambda c: [exactish(math.degrees(math.atan2(float(c.n[0]), float(c.n[1]))))],   # depression
})
