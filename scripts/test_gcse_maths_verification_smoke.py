"""GCSE maths answer verification - run: python scripts/test_gcse_maths_verification_smoke.py

The structural test (test_gcse_maths_correctness_smoke.py) proves generators run and their solutions
are internally consistent.  This one re-solves each question from the numbers the generator recorded
(generators/shared/verify_hook.py) with independent solvers (scripts/gcse_verify/) and compares the
result with the key.  See docs/GCSE_MATHS_VERIFICATION.md.

Checks: practice re-solve, MCQ key (generators and the static bank), checker round-trip, ordered-proof orders and models, stated accuracy, lesson quizzes, properties, no-output-drift,
variety (kinds per tier, duplicate slots, queue repeats, MCQ kinds per band; docs/GCSE_MATHS_VARIETY.md) and retired (every variant taken out of a pool still resolves and verifies).

Options: --deep (200 seeds per slot, 40 seeds per topic quiz; run by hand, not in CI), --only NAME[,NAME] (check names or substrings),
--seed N (offsets the run numbers), --json (machine-readable summary), --print-digests (static MCQ
item digests, for updating register.py after a reviewed change), --variety-report (the variety tables of the
plan, with wider sampling: 30 seeded quizzes per topic and 25 draws per directly generated MCQ slot).
"""
import argparse
import ast
import collections
import hashlib
import json
import os
import re
import sys
import time
import zlib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('PB_TESTING', '1')

from generators.shared.answer_checkers import (  # noqa: E402
    ANSWER_FORMS,
    CHECKERS,
    FORM_AWARE_ANSWER_TYPES,
    check_answer,
)
from generators.shared import answer_units  # noqa: E402
from gcse_verify import (core, coverage, engine, forms, harness, mcq, options, ordering, ordinals, quiz,  # noqa: E402
                         register, variety)
from gcse_verify import (solvers_algebra, solvers_bank, solvers_bank_algebra, solvers_bank_geometry, solvers_proofs,  # noqa: E402,F401
                         solvers_bank_number, solvers_geometry, solvers_number, solvers_probability,
                         solvers_loci, solvers_shapes, solvers_stats, solvers_transform, solvers_variety_b,
                         solvers_variety_c, solvers_variety_c2, solvers_vectors)  # (register the solvers)
from gcse_verify.latex import plain  # noqa: E402
from gcse_verify.registry import DIAGRAM_CHECKS  # noqa: E402

PKG = ROOT / 'scripts' / 'gcse_verify'
# The modules that compute or compare expected answers: every solvers_*.py plus the shared comparison code.
SOLVER_MODULES = tuple(sorted({'core.py', 'exact.py', 'latex.py', 'registry.py', 'engine.py', 'options.py'}
                              | {p.name for p in PKG.glob('solvers_*.py')}))
ALLOWED_IMPORTS = {
    'fractions', 'decimal', 'math', 're', 'html', 'dataclasses', 'typing', 'itertools', 'functools',
    'collections', 'sympy', '__future__', 'generators.shared.rounding',
}
SIBLINGS = {name[:-3] for name in SOLVER_MODULES}

# Clumsy algebra in a question or an option: 1x, 0x, + 0, + -3, x^1, a number written before a fraction bar.
COSMETIC = {
    'a coefficient of 1 written out (1x)': re.compile(r'(?<![\w.^/])1(?=[a-zA-Z](?![a-zA-Z]))'),
    'a zero coefficient (0x)': re.compile(r'(?<![\w.^/])0(?=[a-zA-Z](?![a-zA-Z]))'),
    'adding or subtracting 0': re.compile(r'[+\-\u2212] 0(?![\d.a-zA-Z])'),
    'a sign followed by a negative number': re.compile(r'\+ ?[-\u2212]|\- ?[-\u2212]\d'),
    'a power of 1 (x^1)': re.compile(r'\^1(?!\d)'),
}
# Worked lines where the pattern is the working itself, reviewed one by one (C10): subtracting a coordinate that is 0
# ("3 - 0" in a gradient or a midpoint) and adding a vector component that is 0.  Key: slot label, value: the patterns.
COSMETIC_REVIEWED = {
    'graphs/intermediate/gcse_gra_gradient_from_graph': {'adding or subtracting 0'},
    'graphs/difficult/gcse_gra_perpendicular_bisector': {'adding or subtracting 0'},
    'vectors/foundational/vectors_mcq_foundational_1': {'adding or subtracting 0'},
    'vectors/foundational/vectors_mcq_foundational_5': {'adding or subtracting 0'},
    # fix pass 2026-11-03 (deep seed 4040): the same arithmetic with a coordinate or component that is 0 (y: 4 + 0 = 4,
    # -3 + 0 = -3, (-2 - 0), 4 + 0 + 2 after substituting x = 0); the working line is the point, not a display slip
    'vectors/foundational/vectors_mcq_foundational_7': {'adding or subtracting 0'},
    'vectors/intermediate/_vectors_inter_translation': {'adding or subtracting 0'},
    'graphs/intermediate/gcse_gra_line_through_two_points': {'adding or subtracting 0'},
    'graphs/intermediate/_gra_inter_05': {'adding or subtracting 0'},
    'vectors/foundational/_vectors_found_add_simple': {'adding or subtracting 0'},
}
# Money written with one decimal place (£45.0, £12.5, £1.8 each): a price has pence.  Scanned over every topic
# (questions, options and worked solutions); a decimal that is not an amount of money is not preceded by the symbol.
MONEY_ONE_DP = re.compile(r'[£€$]\d[\d,]*\.\d(?![\d.])')

# A question that fixes how a probability is written cannot take the probability form (which accepts 25%).
PROBABILITY_FORM_FIXED = re.compile(r'as a (fraction|decimal|percentage)|simplest form|lowest terms|decimal place|d\.p\.',
                                    re.I)

# SVG helpers number their title/desc ids from a process-wide counter, which differs between any two runs.
SVG_COUNTER = re.compile(r'(sk-[a-z]+)-\d+')

# A fixed variant (register.FIXED_VARIANTS: the same question, solution and key for every seed, such as a proof, a
# construction or a fixed formula) runs on FIXED_SEEDS seeds in the default run (--deep runs them all).
FIXED_SEEDS = 2
PROC_SAMPLES = 8          # draws per procedural MCQ function that the variety report reads

ISSUES = {}          # check name -> [message]
TALLY = {}


def issue(check, where, detail):
    ISSUES.setdefault(check, []).append(f'{where}: {detail}')


def fixed_signature(p):
    """What makes two generated problems the same question: the text, the worked solution, the options and the key."""
    return (SVG_COUNTER.sub(r'\1-N', str(p.get('question'))), SVG_COUNTER.sub(r'\1-N', str(p.get('solution'))),
            str(p.get('correct_answer_raw')), tuple(str(o) for o in p.get('options') or ()), str(p.get('correct_answer')))


def settings(args):
    if args.deep:
        return dict(practice=200, practice_algebra=200, mcq_direct=40, procedural=100, drift=3, roundtrip=20, quiz=40,
                    retired=20, variety_runs=40)
    return dict(practice=20, practice_algebra=14, mcq_direct=4, procedural=8, drift=3, roundtrip=5, quiz=2,
                retired=2, variety_runs=20)


def verified_slots(mode):
    return [s for s in harness.enumerate_slots() if s.slug in register.VERIFIED_TOPICS and s.mode == mode]


# ─────────────────────────────────────────────────────────────────────────────
# Independence and registry consistency
# ─────────────────────────────────────────────────────────────────────────────

def check_independence():
    for name in SOLVER_MODULES:
        tree = ast.parse((PKG / name).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:              # relative: only sibling solver modules
                    mods = [node.module.split('.')[0]] if node.module else [a.name for a in node.names]
                    mods = [m if m in SIBLINGS else f'.{m}' for m in mods]
                else:
                    mods = [node.module]
            for m in mods:
                if m in SIBLINGS or m in ALLOWED_IMPORTS or (m.split('.')[0] in ALLOWED_IMPORTS and m.split('.')[0] != 'generators'):
                    continue
                issue('independence', name, f'imports {m!r} (solvers may use only stdlib, sympy, rounding and siblings)')
            if isinstance(node, ast.Name) and node.id in ('eval', 'exec', '__import__', 'compile'):
                issue('independence', name, f'uses {node.id}')
            # sympify and parse_expr run eval on strings; generated text goes through solvers_algebra_parse instead
            bad = {'sympify', 'parse_expr', 'S'}
            if isinstance(node, ast.Attribute) and node.attr in bad and isinstance(node.value, ast.Name) \
                    and node.value.id == 'sympy':
                issue('independence', name, f'uses sympy.{node.attr}')
            if isinstance(node, ast.alias) and node.name in bad:
                issue('independence', name, f'imports {node.name}')
    for p in PKG.glob('*.py'):
        for node in ast.walk(ast.parse(p.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec'):
                issue('independence', p.name, f'calls {node.func.id}')


# Option values read exactly: an unworked root beside a whole-number key is a second right answer. (question, key,
# other option, flagged as a duplicate of the key). The filler options are distinct from every key here.
OPTION_VALUE_CASES = (
    ('Find the length.', '5', '\u221a25', True),
    ('Find the length.', '5', '\\sqrt{25}', True),
    ('Find the length.', '5', 'sqrt(25)', True),
    ('Find the length.', '5', '\u221a(25)', True),
    ('Find the length.', '10 units', '\u221a100 units', True),
    ('Find the length.', '6', '2\u221a9', True),
    ('Find the length.', '6', '3\u221a4', True),
    ('Find the length.', '4 cm', '\\sqrt{16} cm', True),
    ('Find the length.', '4 cm', '\u221a16 cm', True),
    ('Find the length.', '12', '\u221a144', True),
    ('Find the length.', '3/2', '\u221a(9/4)', True),
    ('Find the area.', '25 cm\u00b2', '\u221a625 cm\u00b2', True),
    ('Which is equal to 2\u221a2?', '2\u221a2', '\u221a8', True),
    ('Which is equal to \u221a8?', '\u221a8', '2\u221a2', True),
    ('Which is equal to \u221a12?', '2\u221a3', '\u221a12', True),
    ('Find the circumference.', '12\u03c0 cm', '12.0\u03c0 cm', True),
    ('Find the circumference.', '12\u03c0 cm', '\u221a144\u03c0 cm', True),
    ('Find the value.', '0.5', '1/2', True),
    ('Find the length.', '30 cm', '30.0 cm', True),
    ('Find the length.', '\u221a2/2', '1/\u221a2', True),
    # genuinely different values or units stay distinct
    ('Which is equal to \u221a8?', '\u221a8', '\u221a2', False),
    ('Which is equal to 2\u221a2?', '2\u221a2', '2\u221a3', False),
    ('Find the length.', '5', '\u221a24', False),
    ('Find the length.', '5', '\u221a5', False),
    ('Find the length.', '5', '\u221a26', False),
    ('Find the length.', '5', '25', False),
    ('Find the length.', '3', '\u221a3', False),
    ('Find the length.', '5 cm', '\u221a25 m', False),
    ('Find the area.', '25 cm\u00b2', '\u221a25 cm', False),
    ('Find the circumference.', '12\u03c0 cm', '12 cm', False),
    ('Find the circumference.', '12\u03c0 cm', '\u221a12\u03c0 cm', False),
    ('Find the length.', '4 cm', '\u221a(16 + 9) cm', False),
    # form questions keep an unworked equal option as a legitimate distractor
    ('Simplify \u221a8.', '2\u221a2', '\u221a8', False),
    ('Write \u221a72 in its simplest form.', '6\u221a2', '\u221a72', False),
    ('Rationalise 1/\u221a2.', '\u221a2/2', '1/\u221a2', False),
    ('Simplify \u221a25 + 0.', '5', '\u221a25', False),
)

# The same comparison across units (options.py): an option worth the key in another unit is a second right answer,
# whether or not the question names the unit. (question, key, other option, flagged as the key's equal)
UNIT_VALUE_CASES = (
    ('A map scale is 1:10000. A road is 3 cm on the map. What is the real distance?', '0.3 km', '300 m', True),
    ('A map scale is 1:10000. A road is 3 cm on the map. What is the real distance in km?', '0.3 km', '300 m', True),
    ('Find the length.', '1 km', '1000 m', True),
    ('Find the length.', '2.5 m', '250 cm', True),
    ('Find the length.', '12 mm', '1.2 cm', True),
    ('Find the area.', '12 cm\u00b2', '0.0012 m\u00b2', True),
    ('Find the area.', '2 km\u00b2', '2000000 m\u00b2', True),
    ('Find the volume.', '1 m\u00b3', '1000000 cm\u00b3', True),
    ('Find the volume.', '0.5 l', '500 ml', True),
    ('Find the volume.', '2 l', '2000 cm\u00b3', True),
    ('Find the mass.', '1.5 kg', '1500 g', True),
    ('Find the mass.', '2 tonnes', '2000 kg', True),
    ('How long does it take?', '2.5 hours', '150 minutes', True),
    ('How long does it take?', '90 s', '1.5 min', True),
    ('How long does it take?', '2 h', '120 min', True),
    ('What is the cost?', '\u00a30.50', '50p', True),
    ('What is the cost?', '\u00a35', '500p', True),
    ('What is the cost?', '\u00a312.5', '\u00a312.50', True),
    # different amounts, or different kinds of quantity, stay distinct
    ('Find the length.', '0.3 km', '30 m', False),
    ('Find the length.', '3 cm', '3 m', False),
    ('Find the length.', '5 min', '5 m', False),
    ('Find the length.', '1 km', '1 kg', False),
    ('Find the area.', '12 cm\u00b2', '12 cm', False),
    ('Find the area.', '12 cm\u00b2', '12 m\u00b2', False),
    ('Find the volume.', '1 m\u00b3', '1000 cm\u00b3', False),
    ('What is the cost?', '\u00a35', '5p', False),
    ('What is the cost?', '\u00a35', '5', False),
    ('How long does it take?', '2 hours', '2 minutes', False),
    ('Find the speed.', '30 km/h', '30 m/s', False),
    # a question about the form still keeps the unworked original
    ('Write 3000 g in simplest form in kg.', '3 kg', '3000 g', False),
)

# Zero or negative filler beside a positive key (options.filler_errors). (question, key, other option, flagged)
FILLER_CASES = (
    ('Increase 100 by 20%.', '120', '0', True),
    ('Decrease 100 by 20%.', '80', '0', True),
    ('A price of \u00a310 is increased by 20%. What is the new price?', '\u00a312', '0', True),
    ('A job takes 6 workers 8 hours. How long would 8 workers take?', '6 hours', '0', True),
    ('Round 12.503 to 1 decimal place.', '12.5', '0', True),
    ('Find the length.', '5 cm', '-1 cm', True),
    ('Find the length.', '5 cm', '0 cm', True),
    ('What is the real distance in km?', '0.3 km', '0.0 km', True),
    ('Write 3000 in standard form.', '3', '-1', True),
    # questions where zero or a negative is a sensible answer or slip
    ('Solve x + 3 = 5.', '2', '0', False),
    ('How many solutions do the graphs have?', '1', '0', False),
    ('What is the 3-figure bearing of due East?', '090\u00b0', '000\u00b0', False),
    ('The temperature falls 5 degrees below zero. What is it?', '5', '-1', False),
    ('Evaluate \\(3^{-2}\\).', '1/9', '-9', False),
    ('Find the gradient of the line.', '2', '0', False),
    ('What is the probability of rolling a 7?', '1', '0', False),
    # a zero or negative option beside a zero or negative key is the key's own kind
    ('Find the length.', '0', '1', False),
    ('Subtract 12 from 5.', '-7', '-1', False),
)


def check_option_values():
    """Fixed cases for the exact option-value reader (mcq.item_structure_errors, core.parse_num, solvers_bank.val
    and the engine's option check), so a regression there fails even when no current item has such an option."""
    for q, key, other, flagged in OPTION_VALUE_CASES:
        item = {'q': q, 'opts': [f'A  {key}', f'B  {other}', 'C  901', 'D  902'], 'ans': 'A'}
        got = any('same value as the key' in m for m in mcq.item_structure_errors(item))
        if got != flagged:
            issue('option_values', f'{key!r} vs {other!r} ({q})', f'flagged as a duplicate: {got}, expected {flagged}')
    for text, want in (('\u221a25', 5), ('2\u221a9', 6), ('\\sqrt{16} cm', 4), ('sqrt 49', 7), ('\u221a8', None), ('2\u221a2', None),
                       ('12\u03c0 cm', 12), ('3 + \u221a4', None), ('2 \u00d7 3', None), ('1 : 2', None), ('\u221a(-4)', None)):
        for fn in (core.parse_num, solvers_bank.val):
            got = fn(text)
            if got != want:
                issue('option_values', f'{fn.__module__}.{fn.__name__}({text!r})', f'got {got!r}, expected {want!r}')
    eq = {core.exact.value_and_unit(a) == core.exact.value_and_unit(b) for a, b in (('\u221a8', '2\u221a2'), ('\u221a12', '2\u221a3'), ('6\u221a2', '\u221a72'))}
    ne = {core.exact.value_and_unit(a) == core.exact.value_and_unit(b) for a, b in (('\u221a8', '\u221a2'), ('\u221a2', '2'), ('\u03c0', '3'))}
    if eq != {True} or ne != {False}:
        issue('option_values', 'surd identity', f'equal pairs {eq}, different pairs {ne}')
    # Reader limits: ASCII digits only, a power it does not take is not a unit, a bracketed product of two plain
    # numbers is a working, root 0 is 0, and a large prime radicand is split quickly (trial division to the cube root).
    for text in ('\u0663', '\uff15', '\u221a\u0662\u0665', '5\u00b3', '5\u00b2\u00b2', '2(3)', '(2)(3)', '3 + \u221a2', '\u221a' + '9' * 13):
        if core.exact.quantity(text) is not None:
            issue('option_values', f'exact.quantity({text!r})', f'read as {core.exact.quantity(text)!r}, expected unreadable')
    if core.exact.value_and_unit('\u221a0') != core.exact.value_and_unit('0'):
        issue('option_values', 'exact root 0', f'{core.exact.value_and_unit(chr(0x221a) + "0")!r} is not 0')
    t0 = time.perf_counter()
    big = core.exact.value_and_unit('\u221a999999999989')
    if big != ((Fraction(1), 999999999989, 0), '') or time.perf_counter() - t0 > 0.05:
        issue('option_values', 'exact large radicand', f'{big!r} in {time.perf_counter() - t0:.3f} s')
    # the engine's generic option check (procedural MCQs): an unworked root equal to the recomputed value is a second match
    p = {'options': ['A  5', 'B  \u221a25', 'C  6', 'D  7'], 'correct_answer': 'A'}
    msgs = [m for kind, m in engine._option_checks(p, [Fraction(5)], []) if kind == 'mcq']
    if not msgs:
        issue('option_values', 'engine._option_checks', 'an option written as \u221a25 beside a recomputed 5 was not flagged')
    p = {'options': ['A  \u221a8', 'B  3', 'C  6', 'D  7'], 'correct_answer': 'A'}
    if engine._option_checks(p, [Fraction(3)], []) != [('mcq', "options ['B'] all equal the recomputed value but the key is A")]:
        issue('option_values', 'engine._option_checks', 'a key that is not the recomputed value was not reported as before')
    # ...but a key is never accepted in unworked form: the exact fallback is off while a key is compared, so a
    # key of sqrt 16 for an expected 4 (say "Simplify sqrt 16") still fails, for a plain value and for a bank Pick.
    for atoms in ([Fraction(4)], solvers_bank.is_val(Fraction(4))):          # is_val returns [Pick]
        if not core.match_answer(atoms, ['4'], [])[0]:
            issue('option_values', f'core.match_answer({core.show(atoms[0])}, \'4\')', 'a plain key was rejected')
        for key in ('\u221a16', '2\u221a4', '\\sqrt{16}'):
            if core.match_answer(atoms, [key], [])[0]:
                issue('option_values', f'core.match_answer({core.show(atoms[0])}, {key!r})', 'an unworked root was accepted as the key')
    if not solvers_bank.is_val(Fraction(4))[0].test('\u221a16'):
        issue('option_values', 'solvers_bank.is_val', 'an unworked distractor no longer counts as equal to the value')


def check_option_units():
    """Fixed cases for the unit-aware option comparison and the zero or negative filler property, then the
    generators that once had these faults (map scale, percentage change, shared work, statistics fillers) over
    a fixed set of seeds, so a regression there fails even where the default sampling would not meet it."""
    for q, key, other, flagged in UNIT_VALUE_CASES:
        item = {'q': q, 'opts': [f'A  {key}', f'B  {other}', 'C  901', 'D  902'], 'ans': 'A'}
        got = any('same value as the key' in m for m in mcq.item_structure_errors(item))
        if got != flagged:
            issue('option_units', f'{key!r} vs {other!r} ({q})', f'flagged as the key\'s equal: {got}, expected {flagged}')
        p = {'question': q, 'options': item['opts'], 'correct_answer': 'A'}
        if any('same value as the key' in m for kind, m in engine._option_checks(p, [Fraction(901)], [])) != flagged:
            issue('option_units', f'engine: {key!r} vs {other!r}', f'procedural check disagrees with the static check ({flagged})')
    for q, key, other, flagged in FILLER_CASES:
        item = {'q': q, 'opts': [f'A  {key}', f'B  {other}', 'C  901', 'D  902'], 'ans': 'A'}
        got = any('filler no pupil would pick' in m for m in mcq.item_structure_errors(item))
        if got != flagged:
            issue('option_units', f'filler {other!r} beside {key!r} ({q})', f'flagged: {got}, expected {flagged}')
        p = {'question': q, 'options': item['opts'], 'correct_answer': 'A'}
        if any('filler no pupil would pick' in m for kind, m in engine._option_checks(p, [Fraction(901)], [])) != flagged:
            issue('option_units', f'engine: filler {other!r} beside {key!r}', f'procedural check disagrees with the static check ({flagged})')
    from generators.gcse import maths_num_stats_prob_rat as nsp
    import random
    calls = [(f'number_mcq({t})', lambda t=t: nsp.number_mcq(t)) for t in range(1, 19)]
    calls += [(f'ratio_proportion_mcq({t})', lambda t=t: nsp.ratio_proportion_mcq(t)) for t in range(1, 10)]
    calls += [(f'statistics_mcq({i})', lambda i=i: nsp.statistics_mcq(i, 'intermediate')) for i in range(13)]
    for slug in mcq.BANK_REFS:
        for fn in mcq.procedural(slug):
            calls.append((f'{slug}/{fn.__name__}', fn))
    for name, call in calls:
        for seed in range(30):
            random.seed(seed)
            out = call()
            q = plain(out[0])
            opts = engine.parse_options({'options': out[4]})
            keyed = [t for ltr, t in opts if ltr == out[5]]
            want = 3 if re.search(r'correlation', q, re.I) else 4          # positive, negative, none
            if len(opts) != want or len(set(t for _, t in opts)) != want or len(keyed) != 1:
                issue('option_units', f'{name} seed {seed}', f'options {[t for _, t in opts]} are not {want} different options with one key')
                continue
            for m in options.same_value_errors(q, opts, keyed[0]) + options.filler_errors(q, opts, keyed[0]):
                issue('option_units', f'{name} seed {seed}', f'{m} :: {q!r}')
    # fillers: same form as the key, never 0 or negative beside a positive key, never a duplicate
    from generators.shared.option_fillers import fillers
    for key, taken in (('120', ['20', '80']), ('\u00a312', ['\u00a330', '\u00a32']), ('7.875 hours', []), ('6 hours', ['9 hours']),
                       ('5.9%', ['6%']), ('7\u00b2', ['7\u00b3']), ('1/8', []), ('3 \u00d7 10^4', []), ('1', []), ('2', ['3', '1']),
                       ('12 cm\u00b2', []), ('090\u00b0', [])):
        got = fillers(key, taken)
        if len(got) != 3 or len(set(got) | set(taken) | {key}) != 3 + len(taken) + 1:
            issue('option_units', f'fillers({key!r}, {taken})', f'{got} are not three new options')
        for f in got:
            if re.search(r'[\u00b2\u00b3^]\s*$|\^', key) and not key.endswith(('cm\u00b2', 'm\u00b2')):
                continue                      # a power is nudged by its exponent, not read as an amount
            if options.option_amount(f) is not None and options.option_amount(key) is not None:
                if options.sign(options.option_amount(f)[0]) <= 0 or options.option_amount(f)[1] != options.option_amount(key)[1]:
                    issue('option_units', f'fillers({key!r})', f'{f!r} is not a positive amount in the key\'s unit')


ORDINAL_CASES = (
    # (text, number of wrong ordinals)
    ('the 1st, 2nd, 3rd and 4th terms', 0),
    ('the 11th, 12th and 13th terms', 0),
    ('the 21st, 22nd, 23rd and 24th terms', 0),
    ('the 101st, 102nd, 103rd, 104th, 111th, 112th, 113th term', 0),
    ('the 1,001st and 1,011th term', 0),
    ('the 0th term and the 10th, 20th, 100th term', 0),
    ('the 1th term', 1), ('the 2th term', 1), ('the 3th term', 1), ('the 21th, 22th, 23th terms', 3),
    ('the 81th term', 1), ('the 101th and 111st term', 2), ('the 12nd and 13rd term', 2), ('the 11st term', 1),
    ('the 4rd and 5nd term', 2), ('the 1,021th term', 1), ('the 33TH term', 1),
    # not ordinals: letters before the number, a decimal, a longer word, a bare number, a unit
    ('the nth term', 0), ('x2nd', 0), ('3.1st', 0), ('5thousand', 0), ('1sts', 0), ('21', 0), ('5 st', 0), ('A1st', 0),
)


FRACTION_WORD_CASES = (
    # (text, number of fractions written as ordinals)
    ('fall to one-4th of its value', 1), ('one-8th and one-16th', 2), ('1/4th of the sample', 1), ('one-2nd', 1),
    ('fall to one quarter of its value', 0), ('one eighth', 0), ('1/16 of the sample', 0), ('the 4th term and the 8th term', 0),
    ('a-4th', 1), ('two-3rds', 1), ('One-16th', 1), ('x-4thing', 0), ('the 21st-century', 0), ('1,000th', 0),
    # review 2026-10-27: algebra and other hyphenated words are not fractions
    ('the n-1th term', 0), ('the x-4th', 0), ('a re-4th', 0), ('Year-10th', 0), ('top-5th', 0),
)


def check_unit_variant_cases():
    """The unit round trip types units only on number fields (batch B review, 2026-10-28): parse_num reads -2p as
    "-2 pence", so an algebraic field (the image (-2p, -4q) of a rotation, whose question prints 180°) was typed as
    "-2p%" and expected to be refused with the unit message; only --deep --seed 7000 reached it. Fixed text, so the
    default run guards it."""
    q = 'A point has coordinates (2p, 4q). It is rotated 180° about the origin. Write down the image coordinates.'
    for raw in ('-2p\x1e-4q', '4x|3', '-2p'):
        got = forms.wrong_unit_variants('number_fields', raw, q) + forms.unit_variants('number_fields', raw, q)
        if got:
            issue('unit_roundtrip', 'self-test', f'algebraic field {raw!r} given unit variants {got}')
    if not forms.unit_variants('number_fields', '3|180', 'Find x in cm and the angle in degrees.'):
        issue('unit_roundtrip', 'self-test', 'number fields lost their unit variants (the guard is too wide)')


def check_conversion_currency():
    """The pounds-to-euros conversion graph asks for one currency: the key typed with the other currency's symbol is
    refused with the unit message and typed with its own it is right, both ways round (C2 review: the question once
    wrote "pounds (£)" and "euros (€)", which the unit model read as two currencies asked for, so "£42" passed for a
    key in euros). Fixed slot, so the default run guards it."""
    import random
    from generators.shared import answer_units
    from topic_registry import TOPICS
    gen = TOPICS['gcse']['maths']['graphs']['func']
    seen = set()
    for seed in range(80):
        random.seed(seed)
        p = gen('intermediate', 'standard', variant_name='gcse_gra_conversion_graph')
        if 'euros' not in p['question']:
            continue
        own, other = ('€', '£') if 'answer in euros' in p['question'] else ('£', '€')
        if own in seen:
            continue
        seen.add(own)
        raw, qtext = p['correct_answer_raw'], answer_units.problem_question_text(p)
        res = check_answer('number', raw, f'{other}{raw}', question=qtext)
        if res['correct'] or not str(res.get('feedback', '')).startswith('Check the units'):
            issue('unit_roundtrip', f'conversion graph ({own})', f'{other}{raw} was not refused with the unit message: {res}')
        if not check_answer('number', raw, f'{own}{raw}', question=qtext)['correct']:
            issue('unit_roundtrip', f'conversion graph ({own})', f'{own}{raw} was refused')
    if seen != {'€', '£'}:
        issue('unit_roundtrip', 'conversion graph', f'only {sorted(seen)} of the two currency asks were drawn in 80 seeds')


def check_fraction_words():
    """A fraction must not be printed as "one-4th" (GCSE physics half-life question, 2026-10-27): the detector on fixed text,
    the half-life generator over every number of half-lives, every generator's source (all levels and subjects), and a
    mutation (the old wording must be caught, in text and in a source line)."""
    for text, want in FRACTION_WORD_CASES:
        got = len(ordinals.fraction_word_errors(text))
        if got != want:
            issue('ordinals', repr(text), f'{got} fractions written as ordinals reported, expected {want}')
    from generators.gcse import physics
    import random
    seen = set()
    for seed in range(60):
        random.seed(seed)
        q, sol, hint, _marks = physics.rad_inter_half_life_time()
        for text in (q, sol, hint):
            for m in ordinals.fraction_word_errors(plain(text)) + ordinals.ordinal_errors(plain(text)):
                issue('ordinals', f'half-life time seed {seed}', m)
        seen.add(re.search(r'fall to <strong>([^<]+)</strong>', q).group(1))
    TALLY['half_life_fractions'] = len(seen)
    if seen != {'one quarter', 'one eighth', 'one sixteenth'}:
        issue('ordinals', 'half-life time', f'the question names {sorted(seen)}, expected one quarter, one eighth and one sixteenth')
    for line in ordinals.source_errors(ROOT):
        issue('ordinals', 'generator source', line)
    bad = ['rf"fall to <strong>one-{2**n_halves}th</strong> of its original value"', 'q = f"the {n}th term"',
           'rf"the {k}st term"']
    for line in bad:
        if not (ordinals._HAND_ENDING.search(line) or ordinals._FRACTION_WORD.search(line)):
            issue('ordinals', 'mutation', f'the source scan misses {line!r}')
    if not ordinals.fraction_word_errors('To fall to one-8th of the original value takes 3 half-lives.'):
        issue('ordinals', 'mutation', 'the old half-life wording is not caught')


def check_ordinals():
    """Wrong ordinal endings (21th, 81th, 1th, 22th) in anything a pupil reads: the detector on fixed text, then the
    generators that build ordinals (sequences, multiples) over many seeds, then a mutation: the same generators with
    the ending forced to -th must be caught, so the check cannot pass by looking at nothing."""
    for text, want in ORDINAL_CASES:
        got = len(ordinals.ordinal_errors(text))
        if got != want:
            issue('ordinals', repr(text), f'{got} wrong ordinals reported, expected {want}')
    import generators.shared.utils as shared_utils
    probes = [sl for sl in harness.enumerate_slots() if sl.slug in ('sequences', 'multiples_factors', 'number', 'decimals')]

    def shown_texts(p):
        return [plain(str(t or '')) for t in (p['question'], p.get('solution'), p.get('hint'), *(p.get('options') or []))]

    def sweep(slots, seeds):
        found, drawn = [], 0
        for sl in slots:
            for r in range(seeds):
                try:
                    p = harness.generate(sl, r, record=False)[0]
                except Exception as exc:
                    issue('ordinals', sl.label, f'generator raised {exc!r}')
                    break
                drawn += 1
                for text in shown_texts(p):
                    for m in ordinals.ordinal_errors(text):
                        found.append((sl.label, m))
        return found, drawn

    # Review 2026-10-27 (speed): only the slots that print an ordinal at all (looked for over 3 seeds) are swept deeply
    # and mutated; the property pass above already reads every generated question for a wrong ending.
    with_ordinals = []
    for sl in probes:
        for r in range(3):
            try:
                p = harness.generate(sl, r, record=False)[0]
            except Exception as exc:
                issue('ordinals', sl.label, f'generator raised {exc!r}')
                break
            if any(ordinals.ORDINAL_RE.search(text) for text in shown_texts(p)):
                with_ordinals.append(sl)
                break
    TALLY['ordinals_slots'] = len(with_ordinals)
    if len(with_ordinals) < 8:
        issue('ordinals', 'probe', f'only {len(with_ordinals)} slots print an ordinal (the sequence and multiple generators do)')
    found, drawn = sweep(with_ordinals, 30)
    TALLY['ordinals_questions'] = drawn
    for label, m in sorted(set(found))[:20]:
        issue('ordinals', label, m)
    # mutation: every generator that imported the helper now writes -th for every number
    mods = [m for m in sys.modules.values() if getattr(m, 'ordinal_suffix', None) is shared_utils.ordinal_suffix]
    if not mods:
        issue('ordinals', 'mutation', 'no generator module uses generators.shared.utils.ordinal_suffix (the check has nothing to look at)')
        return
    saved = [(m, m.ordinal_suffix) for m in mods]
    try:
        for m in mods:
            m.ordinal_suffix = lambda n: 'th'
        bad, _ = sweep(with_ordinals, 12)
    finally:
        for m, fn in saved:
            m.ordinal_suffix = fn
    TALLY['ordinals_mutation_caught'] = len(set(bad))
    if len(set(bad)) < 5:
        issue('ordinals', 'mutation', f'forcing every ending to -th was caught only {len(set(bad))} times (want 5 or more)')


def check_register(slots):
    topics = set(harness.topics())
    declared = set(register.VERIFIED_TOPICS) | set(register.PENDING_TOPICS)
    if set(register.VERIFIED_TOPICS) & set(register.PENDING_TOPICS):
        issue('register', 'topics', 'a topic is both verified and pending')
    for t in sorted(topics - declared):
        issue('register', t, 'topic is in neither VERIFIED_TOPICS nor PENDING_TOPICS (classify it)')
    for t in sorted(declared - topics):
        issue('register', t, 'registered topic no longer exists')
    practice_labels = {s.label for s in slots if s.mode == 'standard'}
    for name, table in (('VARIETY_EXEMPT', register.VARIETY_EXEMPT), ('VARIETY_DEFERRED', register.VARIETY_DEFERRED),
                         ('VARIETY_NEAR_DUPLICATES', register.VARIETY_NEAR_DUPLICATES)):
        for key, reason in sorted(table.items()):
            head, _, pair = key.rpartition('/')
            a, _, b = pair.partition('+')
            if not (a and b and a < b and f'{head}/{a}' in practice_labels and f'{head}/{b}' in practice_labels):
                issue('register', key, f'{name} key must be "slug/tier/a+b" (names sorted) of two practice slots of the tier')
            if len(str(reason).strip()) < 20:
                issue('register', key, f'{name} needs a reason of 20 or more characters')
    for label in sorted(set(register.FIXED_VARIANTS) - practice_labels):
        issue('register', label, 'listed in FIXED_VARIANTS but is not a practice slot any more (remove it)')
    pending = sum(1 for s in slots if s.slug in register.PENDING_TOPICS)
    TALLY['pending'] = pending
    if pending:
        issue('register', 'pending', f'{pending} slots are in pending topics: every topic must be verified '
              '(move it into VERIFIED_TOPICS with its solvers)')
    slot_keys = {f'{s.slug}/{s.mode}/{s.fn}' for s in slots}
    for key, entry in register.EXEMPT.items():
        if key.split('/')[0] not in register.VERIFIED_TOPICS:
            issue('register', key, 'EXEMPT entry is not in a verified topic')
        if key not in slot_keys:
            issue('register', key, "EXEMPT entry matches no slot (key format is 'slug/mode/fn')")
        try:
            category, reason = entry
        except (TypeError, ValueError):
            issue('register', key, 'EXEMPT entry must be (category, reason)')
            continue
        if category not in ('self-marked', 'infeasible'):
            issue('register', key, f'EXEMPT category {category!r} is not self-marked or infeasible')
        if len(str(reason).strip()) < 20:
            issue('register', key, 'EXEMPT reason must be at least 20 characters')
    for digest, entry in register.STATIC_EXEMPT.items():
        try:
            category, reason = entry
        except (TypeError, ValueError):
            issue('register', digest, 'STATIC_EXEMPT entry must be (category, reason)')
            continue
        if category not in ('conceptual', 'method', 'infeasible'):
            issue('register', digest, f'STATIC_EXEMPT category {category!r} is not conceptual, method or infeasible')
        if len(str(reason).strip()) < 20:
            issue('register', digest, 'STATIC_EXEMPT reason must be at least 20 characters')
    for slug, (floor, reason) in register.QUIZ_SHAPE.items():
        if slug not in harness.topics():
            issue('register', slug, 'QUIZ_SHAPE names a topic that does not exist')
        if not 1 <= floor <= 10 or len(str(reason).strip()) < 20:
            issue('register', slug, 'QUIZ_SHAPE needs a floor of 1 to 10 questions and a reason of 20 or more characters')
    for t in mcq.BANK_REFS:
        if t not in register.VERIFIED_TOPICS:
            issue('register', t, 'static bank mapped for a topic that is not verified')
    for t in register.VERIFIED_TOPICS:
        slot_names = {s.fn for s in slots if s.slug == t and s.mode == 'mcq'}
        dispatch = {n for n in slot_names if '_mcq_' in n}
        if t not in mcq.DIRECT_TOPICS and dispatch and t not in mcq.BANK_REFS:
            issue('register', t, 'MCQ dispatch slots but no static bank registered')


def check_concepts_and_reach(slots):
    """Phase 2: concept slots (docs/GCSE_MATHS_VARIETY.md 5.3) and MCQ reach (5.1).

    * the bank items flagged ``"concept": True`` are exactly the reviewed definitions (register.STATIC_EXEMPT);
    * in every band of a bank topic that has such items, the LAST slot serves only them and every other slot none of
      them (so those slots can be re-solved in full); register.CONCEPT_SLOTS lists those slots and nothing else;
    * every slot of a bank topic reports what it can serve (the coverage figures read it);
    * every generator a direct topic has written is in some band's list, and the bands of a topic differ;
    * every procedural generator of a bank topic is served by the difficult band, and the band lists name only
      generators of the topic."""
    from generators.gcse import maths_bank_procedural_mcq as proc
    actual = {}
    for slug in sorted(mcq.BANK_REFS):
        flagged = {mcq.item_digest(i) for i in mcq.bank(slug) if i.get('concept')}
        exempt = {mcq.item_digest(i) for i in mcq.bank(slug)} & set(register.STATIC_EXEMPT)
        for d in sorted(flagged - exempt):
            issue('register', f'{slug} concept item {d}', 'flagged "concept": True but not in STATIC_EXEMPT (concept items are the reviewed exemptions)')
        for d in sorted(exempt - flagged):
            issue('register', f'{slug} exempt item {d}', 'in STATIC_EXEMPT but not flagged "concept": True, so it is served by every slot')
        for tier in harness.TIERS:
            band = coverage.band_slots(slug, tier)
            if len(band) < variant_count():
                issue('register', f'{slug}/{tier}', f'{len(band)} MCQ slots (a topic never has fewer than {variant_count()})')
            concept_slots = []
            for name, (entries, is_concept) in band.items():
                if not entries:
                    issue('register', name, 'slot reports no entries (it must be built by mcq_variants_from_bank_with_procedural)')
                    continue
                bad = [e for e in entries if not callable(e) and mcq.item_digest(e) in register.STATIC_EXEMPT]
                if is_concept:
                    concept_slots.append(name)
                    if len(bad) != len(entries):
                        issue('register', name, 'a concept slot must serve only reviewed definitions')
                    if not name.endswith(f'_{len(band)}'):
                        issue('register', name, 'the concept slot must be the last slot of the band')
                elif bad:
                    issue('register', name, f'serves {len(bad)} reviewed definition(s) but is not the band\'s concept slot')
            has_exempt = any(callable(e) is False and mcq.item_digest(e) in register.STATIC_EXEMPT
                             for entries, _ in band.values() for e in entries)
            if has_exempt and len(concept_slots) != 1:
                issue('register', f'{slug}/{tier}', f'the band serves definitions but has {len(concept_slots)} concept slots, not 1')
            if concept_slots:
                actual[f'{slug}/{tier}'] = concept_slots[0]
        allowed = set(proc.procedural_mcq_for(slug))
        served = {fn for tier in harness.TIERS for entries, _ in coverage.band_slots(slug, tier).values()
                  for fn in entries if callable(fn)}
        if served - allowed:
            issue('register', slug, f'a band serves procedural generators that are not the topic\'s: {sorted(f.__name__ for f in served - allowed)}')
        diff = {fn for entries, _ in coverage.band_slots(slug, 'difficult').values() for fn in entries if callable(fn)}
        if allowed - diff:
            issue('register', slug, f'the difficult band no longer serves {sorted(f.__name__ for f in allowed - diff)}')
    if actual != register.CONCEPT_SLOTS:
        issue('register', 'CONCEPT_SLOTS', f'register.CONCEPT_SLOTS {sorted(register.CONCEPT_SLOTS.items())} does not match the concept '
              f'slots the generators build {sorted(actual.items())}')
    unreachable = 0
    for slug in sorted(mcq.REACH):
        written, placed, per = mcq.reach(slug)
        missing = written - placed
        stray = placed - written
        unreachable += len(missing)
        if missing:
            issue('register', slug, f'{len(missing)} MCQ generator(s) written for the topic are in no band list (unreachable): '
                  f'{sorted(getattr(m, "__name__", m) for m in missing)}')
        if stray:
            issue('register', slug, f'a band list names {len(stray)} generator(s) the topic has not written: '
                  f'{sorted(getattr(m, "__name__", m) for m in stray)}')
        if len({frozenset(v) for v in per.values()}) < len(per):
            issue('register', slug, 'two bands serve exactly the same generators (each band has its own list)')
    TALLY['mcq_unreachable'] = unreachable
    TALLY['concept_slots'] = len(actual)


def variant_count():
    from generators.shared import variant_utils
    return variant_utils.TIER_VARIANT_COUNT


def retired_static_errors(entries, slots, root=ROOT):
    """Problems with a register of retired variants that need no generation: the name is still defined (once, in one
    generator module), is in no pool, resolves through the global fallback, and its replacement is in its old pool."""
    out = []
    topics = harness.topics()
    functions = variety.generator_functions()
    pooled = collections.defaultdict(set)
    for s in slots:
        pooled[s.slug].add(s.fn)
    in_tier = collections.defaultdict(set)          # one pass (batch C1: the pairwise comprehension cost about 0.5 s a run)
    for t in slots:
        if t.mode == 'standard':
            in_tier[(t.slug, t.tier)].add(t.fn)
    from generators.shared import variant_utils
    for key, entry in sorted(entries.items()):
        try:
            replaced_by, reason, tier = entry
        except (TypeError, ValueError):
            out.append(f'{key}: RETIRED entry must be (replaced_by, reason, tier)')
            continue
        slug, _, fn = key.partition('/')
        if slug not in topics or not fn:
            out.append(f'{key}: key is not "slug/function" of a GCSE maths topic')
            continue
        if tier not in harness.TIERS or len(str(reason).strip()) < 20:
            out.append(f'{key}: needs a tier and a reason of 20 or more characters')
        if fn in pooled[slug]:
            out.append(f'{key}: still in a pool of {slug} (a retired variant must be out of every pool)')
        defs = functions.get(fn) or []
        sources = variety.defining_modules(fn, root)
        if len(defs) != 1 or len(sources) != 1:
            out.append(f'{key}: defined {len(sources)} time(s) in the source ({", ".join(sources) or "nowhere"}) and loaded from '
                       f'{len(defs)} module(s); a retired name must live in exactly one generator module')
        elif variant_utils.lookup_variant_by_name(fn) is not defs[0][1]:
            out.append(f'{key}: the global lookup finds a different function')
        if replaced_by not in in_tier.get((slug, tier), set()):
            out.append(f'{key}: replaced_by {replaced_by!r} is not a slot of {slug}/{tier}')
        elif str(reason).startswith('merged') and defs:
            # a merged sibling must still be drawn by its slot: the slot's source names it, or names the helper that
            # the sibling's one-line wrapper calls (the correlation slot calls the three graph helpers directly)
            names = _referenced_names(functions.get(replaced_by) or [])
            wrapped = re.match(r'(\w+)\(', variety.call_key(defs[0][1]) or '')
            if fn not in names and not (wrapped and wrapped.group(1) in names):
                out.append(f'{key}: merged into {replaced_by!r}, which does not draw it any more (a merged slot must '
                           f'draw every sibling it replaced)')
    return out


def _referenced_names(defs):
    """Names a module-level function's body refers to (from its source), or an empty set."""
    if not defs:
        return set()
    src = variety._function_source(defs[0][1])
    try:
        tree = ast.parse(src or '')
    except SyntaxError:
        return set()
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}


def check_retired(args, slots):
    """Every retired variant still resolves through its topic's own generator in its old tier, and the answer it
    gives is re-solved by the same family solver as a live slot (2 seeds each; 20 with --deep)."""
    cfg = settings(args)
    for m in retired_static_errors(register.RETIRED, slots):
        issue('retired', 'register', m)
    # negative control: each fault must be reported
    live = next(s for s in slots if s.mode == 'standard')
    twice = next((n for n, files in sorted(variety._SOURCE_DEFS.items())
                  if len(files) > 1 and n in variety.generator_functions()), None)
    mutants = {
        'a name still in a pool': ({f'{live.slug}/{live.fn}': (live.fn, 'a pooled name must be refused as retired', live.tier)},
                                   'still in a pool'),
        'a name that no longer exists': ({f'{live.slug}/_no_such_variant': (live.fn, 'a missing function must be refused', live.tier)},
                                         'defined 0 time(s)'),
        'a replacement outside the tier': ({f'{live.slug}/_x': (live.fn + '_x', 'the replacement must be a slot of the tier', live.tier)},
                                           'is not a slot of'),
    }
    if twice:
        slug_ = next(s.slug for s in slots)
        mutants['a name defined in two modules'] = ({f'{slug_}/{twice}': (live.fn, 'a duplicated name must be refused', live.tier)},
                                                    'exactly one generator module')
    for k, (by, why, tier) in sorted(register.RETIRED.items()):
        if not why.startswith('merged'):
            continue
        # the sibling pointed at another slot of its tier, one that does not draw it
        slug_ = k.split('/')[0]
        other = next((s.fn for s in slots if s.mode == 'standard' and s.slug == slug_ and s.tier == tier and s.fn != by), None)
        if other:
            mutants['a merged sibling its slot no longer draws'] = ({k: (other, why, tier)}, 'does not draw it')
            break
    caught = 0
    for what, (entries, expected) in mutants.items():
        if any(expected in m for m in retired_static_errors(entries, slots)):
            caught += 1
        else:
            issue('retired', 'negative control', f'{what} was not reported')
    TALLY['retired_negative_control'] = f'{caught}/{len(mutants)}'
    n = 0
    for key, (replaced_by, _reason, tier) in sorted(register.RETIRED.items()):
        slug, _, fn = key.partition('/')
        slot = harness.Slot(slug, tier, 'standard', fn)
        for r in range(args.seed, args.seed + cfg['retired']):
            try:
                p, recs = harness.generate(slot, r)
            except Exception as exc:
                issue('retired', f'{key}#{r}', f'the retired name no longer generates: {exc!r}')
                break
            n += 1
            o = engine.verify_problem(p, recs)
            if o.status != 'verified':
                for kind, msg in o.findings or [('norecord', 'no record() call reached')]:
                    issue('retired', f'{key}#{r}', f'[{kind}] {msg} :: {plain(p["question"])[-90:]!r}')
    TALLY['retired_names'] = len(register.RETIRED)
    TALLY['retired_generations'] = n


# ─────────────────────────────────────────────────────────────────────────────
# Solver unit table and negative control
# ─────────────────────────────────────────────────────────────────────────────

def check_solver_table():
    cases = [
        ('num_round_dp', dict(n=2.345, dp=2), [Fraction('2.35')]),
        ('num_round_sf', dict(n=0.0045, sf=1), [Fraction('0.005')]),
        ('num_directed', dict(a=-3, op='-', b=5), [Fraction(-8)]),
        ('num_pct_of', dict(pct=15, amount=80), [Fraction(12)]),
        ('num_frac_of', dict(num=3, den=4, amount=20), [Fraction(15)]),
        ('num_to_standard_form', dict(n=45000), [core.SF(Fraction(9, 2), 4)]),
    ]
    for fam, inputs, want in cases:
        try:
            got = engine.solve_record({'family': fam, 'inputs': inputs})
        except core.Cannot as exc:
            issue('solvers', fam, f'unreadable: {exc}')
            continue
        if got != want:
            issue('solvers', fam, f'{inputs} gave {got!r}, wanted {want!r}')
    # Negative control: a wrong rounding of a known value must be rejected by the matcher.
    ok, _, _ = core.match_atom(Fraction('2.35'), '2.34', [('dp', 2)])
    if ok:
        issue('solvers', 'negative-control', 'a wrong rounding was accepted by match_atom')
    ok, _, _ = core.match_atom(Fraction('2.35'), '2.35', [('dp', 2)])
    if not ok:
        issue('solvers', 'negative-control', 'the right rounding was rejected by match_atom')


def svg_tampers(p):
    """Copies of problem ``p`` whose drawing is damaged in one way each (a point moved, a bar resized, a label changed)."""
    html = str(p['question'])
    edits = (
        (r'(<circle\b[^>]*?\bcx=")(-?[\d.]+)', lambda m: m.group(1) + format(float(m.group(2)) + 25, 'g')),
        (r'(<rect\b[^>]*?\bheight=")([\d.]+)', lambda m: m.group(1) + format(float(m.group(2)) * 1.6 + 3, 'g')),
        (r'(<line\b[^>]*?\bx2=")(-?[\d.]+)', lambda m: m.group(1) + format(float(m.group(2)) + 25, 'g')),
        (r'(<line\b[^>]*?\by2=")(-?[\d.]+)', lambda m: m.group(1) + format(float(m.group(2)) + 25, 'g')),
        (r'(<polygon\b[^>]*?\bpoints=")(-?[\d.]+)', lambda m: m.group(1) + format(float(m.group(2)) + 25, 'g')),
        (r'(<text\b[^>]*>)(\d+)(</text>)', lambda m: m.group(1) + str(int(m.group(2)) + 1) + m.group(3)),
        (r'(<path\b[^>]*?\bd="M )(-?[\d.]+)', lambda m: m.group(1) + format(float(m.group(2)) + 25, 'g')),
        (r'(<path\b[^>]*?\bd="M [\d. -]+L )(-?[\d.]+)', lambda m: m.group(1) + format(float(m.group(2)) + 25, 'g')),
        (r'(<text\b[^>]*>[^<]*?)(\d+)', lambda m: m.group(1) + str(int(m.group(2)) + 1)),
    )
    for pattern, fn in edits:
        new, n = re.subn(pattern, fn, html, count=1)
        if n and new != html:
            q = dict(p)
            q['question'] = new
            yield q


def tamper(p):
    """A copy of problem ``p`` whose key is wrong, or None when the type has no safe mutation."""
    q = dict(p)
    if p.get('options'):
        letters = [str(o).strip()[0] for o in p['options']]
        wrong = [x for x in letters if x != str(p.get('correct_answer')).strip().upper()]
        if not wrong:
            return None
        q['correct_answer'] = wrong[0]
        return q
    at, raw = p.get('answer_type'), p.get('correct_answer_raw')
    if raw is None or not at or at in forms.UNTYPED:
        return None
    bad = forms.tampered_keys(at, raw)
    if not bad:
        return None
    q['correct_answer_raw'] = bad[0]
    return q


def proof_tampers(p):
    """(description, problem) copies of an ordered proof with something wrong in it."""
    raw = str(p['correct_answer_raw'])
    ids = raw.split('|')[1:]
    bank = [dict(b) for b in p['answer_step_bank']]
    text = {str(b['id']): b['text'] for b in bank}
    other = [b for b in bank if str(b['id']) not in ids]

    def with_bank(items):
        q = dict(p)
        q['answer_step_bank'] = items
        return q

    if p.get('answer_step_prereqs'):
        q = dict(p)
        q.pop('answer_step_prereqs')
        yield 'a strict order where the proof allows two', q
        q = dict(p)
        q['answer_step_prereqs'] = {k: [] for k in p['answer_step_prereqs']}
        yield 'no order at all', q
    else:
        q = dict(p)
        q['answer_step_prereqs'] = {k: [] for k in ids}
        yield 'no order at all', q
    q = dict(p)
    q['correct_answer_raw'] = '|'.join([raw.split('|')[0], ids[1], ids[0]] + ids[2:])
    yield 'two steps swapped', q
    yield 'a distractor reads as a keyed step', with_bank(
        [dict(b, text=text[ids[0]]) if b is other[0] else b for b in bank])
    for b in bank:
        if str(b['id']) == ids[-1]:
            b['text'] = re.sub(r'\d', lambda m: str((int(m.group()) + 1) % 10), b['text'], count=1) \
                if re.search(r'\d', b['text']) else b['text'] + ' This is not so.'
    yield 'the last step changed', with_bank(bank)


# ─────────────────────────────────────────────────────────────────────────────
# The six checks
# ─────────────────────────────────────────────────────────────────────────────

def keys_exact_or_stated(p, outcome):
    """Messages when an inexact answer is keyed without any stated accuracy in the question."""
    out = []
    expected = outcome.expected
    if expected is None or isinstance(expected, core.AnyOf):
        return out
    if expected and isinstance(expected[0], core.Verdict):
        return out
    if core.stated_specs(plain(p['question'])):
        return out
    fields, how = engine.key_fields_for(p)
    if not fields or len(fields) != len(expected):
        return out
    for atom, field in zip(expected, fields):
        if not isinstance(atom, core.Approx):
            continue
        got = core.parse_num(field) if isinstance(field, str) else None
        if got is not None and abs(float(got) - float(atom.value)) <= 1e-9 * max(1.0, abs(float(atom.value))):
            continue
        out.append(f'key {field!r} is a rounded value of {float(atom.value):.10g} but the question states no accuracy')
    return out


_FIRST = re.compile(r'\b(first|1st|one)\b', re.I)
_SECOND = re.compile(r'\b(second|2nd|other)\b', re.I)
_ORDER_WORDS = re.compile(r'smaller|larger|lower|higher|in order|ascending|least|greatest', re.I)


def unordered_box_errors(p):
    """number_pair / number_fields boxes are marked in order, so two answers of the same kind (roots,
    intersections, solutions) need the question, labels or hints to say which goes first, and a key
    labelled smaller/larger must be in that order."""
    if p.get('answer_type') not in ('number_pair', 'number_fields'):
        return []
    labels = [str(x) for x in (p.get('answer_labels') or [])]
    raw = str(p.get('correct_answer_raw') or '')
    vals = raw.split('\x1e' if '\x1e' in raw else '|')
    told = ' '.join([plain(p.get('question', '')), str(p.get('hint') or ''), str(p.get('answer_format_hint') or '')]
                    + labels)
    out = []
    for i in range(len(labels) - 1):
        a, b = labels[i], labels[i + 1]
        if _FIRST.search(a) and _SECOND.search(b) and re.search(r'root|solution|intersection|integer', a + b, re.I):
            if not _ORDER_WORDS.search(told):
                out.append(f'boxes {a!r} and {b!r} are marked in order but nothing says which value goes first')
        if re.search(r'smaller', a, re.I) and re.search(r'larger', b, re.I) and i + 1 < len(vals):
            try:
                if Fraction(vals[i].strip()) > Fraction(vals[i + 1].strip()):
                    out.append(f'boxes {a!r} and {b!r} are keyed {vals[i]} then {vals[i + 1]}')
            except (ValueError, ZeroDivisionError):
                pass
    return out


def ordering_errors(p, key, structures):
    """Problems with an ordered proof's accepted orders.

    The key shown to pupils is one canonical order.  A problem may also carry ``answer_step_prereqs`` (which
    steps each step needs first); the checker then accepts every order that respects them.  Checks: the spec is
    well formed, the canonical key is one of the valid orders, every valid order (found here independently of
    the checker) is accepted, no other permutation is, a swap of two dependent steps is refused, a missing,
    repeated or extra step is refused, the pairs judged independent are the ones a person read
    (register.ORDER_FREE_PAIRS), and a request that does not carry the stored spec gets the strict order only.
    """
    raw = str(p['correct_answer_raw'])
    canonical = tuple(raw.split('|')[1:])
    prereqs = p.get('answer_step_prereqs')
    bank = [str(b.get('id')) for b in p.get('answer_step_bank') or []]
    out = []
    reviewed = set(register.ORDER_FREE_PAIRS.get(key, ()))

    def ask(order, strict=False):
        return check_answer('proof_steps', raw, '|'.join(order), prereqs=None if strict else prereqs)['correct']

    if prereqs:
        if not isinstance(prereqs, dict) or set(prereqs) != set(canonical):
            return ['answer_step_prereqs does not list exactly the keyed steps']
        for step, needs in prereqs.items():
            if not isinstance(needs, list) or step in needs or not set(needs) <= set(canonical):
                return [f'answer_step_prereqs: bad prerequisites {needs!r} for {step}']
        spec = {step: tuple(needs) for step, needs in prereqs.items()}
    else:
        if reviewed:
            out.append('listed in register.ORDER_FREE_PAIRS but the problem carries no accepted orders')
        spec = {step: ((canonical[i - 1],) if i else ()) for i, step in enumerate(canonical)}
    if not ordering.is_valid_order(canonical, spec):
        return out + ['the keyed order does not respect its own prerequisites']
    orders = ordering.linear_extensions(canonical, spec)
    if len(orders) > ordering.MAX_ORDERS:
        return out + [f'more than {ordering.MAX_ORDERS} accepted orders']
    if canonical not in orders:
        out.append('the canonical key is not among the accepted orders')
    free = ordering.free_pairs(canonical, spec)
    if free != reviewed:
        out.append(f'independent step pairs {sorted(free)} differ from the reviewed pairs {sorted(reviewed)} '
                   f'(register.ORDER_FREE_PAIRS)')
    for order in orders:
        if not ordering.is_valid_order(order, spec):
            out.append(f'listed order {order} puts a step before one it needs')
        elif not ask(order):
            out.append(f'valid order {"|".join(order)} is refused')
    structure = (key, tuple(sorted((k, tuple(v)) for k, v in spec.items())))
    if structure not in structures:
        structures.add(structure)
        perms = ordering.all_permutations(canonical)
        if perms is None:
            perms = [canonical[::-1], canonical[1:] + canonical[:1]]
        valid = set(orders)
        for perm in perms:
            if ask(perm) != (perm in valid):
                out.append(f'order {"|".join(perm)} is {"refused" if perm in valid else "accepted"} wrongly')
                break
    dep = ordering.dependent_pairs(canonical, spec)
    for i in range(len(canonical) - 1):
        swapped = list(canonical)
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        if (i + 1, i + 2) in dep and ask(swapped):
            out.append(f'swapping dependent steps {i + 1} and {i + 2} is accepted')
    extras = [b for b in bank if b not in canonical]
    for bad in (canonical[:-1], canonical + (canonical[0],), (canonical[0],) * len(canonical)):
        if ask(bad):
            out.append(f'{"|".join(bad)} is accepted')
    if extras and ask(canonical[:-1] + (extras[0],)):
        out.append('a wrong step in place of the last one is accepted')
    if len(orders) > 1:
        alt = next(o for o in orders if o != canonical)
        if ask(alt, strict=True):
            out.append('an alternative order is accepted without the stored problem supplying it')
    return out


def run_checks(args, wanted):
    cfg = settings(args)
    base = args.seed
    slots = harness.enumerate_slots()
    practice = verified_slots('standard')
    mcq_slots = verified_slots('mcq')
    direct = [s for s in mcq_slots if s.slug in mcq.DIRECT_TOPICS]
    dispatch = [s for s in mcq_slots if s.slug not in mcq.DIRECT_TOPICS]
    t0 = time.time()

    def want(name):
        return not wanted or any(w in name for w in wanted)

    tally = {}
    proc_samples = {}       # slug -> [(family, template)] of the procedural MCQ functions, for the variety report
    qt = collections.Counter()

    # Generate once, share across the checks.
    cache = []          # (slot, run, problem, outcome)
    need_practice = any(want(n) for n in ('practice', 'roundtrip', 'accuracy', 'negative', 'answer_form', 'ordering', 'variety'))
    n_fixed = 0

    def generate_one(s, r):
        try:
            return harness.generate(s, r)
        except Exception as exc:                            # a crash is a finding, not a skip
            issue('practice_resolve', f'{s.label}#{r}', f'generator raised {exc!r}')
            return None

    def keep_one(s, r, p, recs):
        outcome = engine.verify_problem(p, recs)
        outcome.records = recs
        cache.append((s, r, p, outcome))

    if need_practice:
        unlisted_fixed = []
        for s in practice:
            n_seeds = cfg['practice_algebra'] if s.slug in register.ALGEBRA_TOPICS else cfg['practice']
            # a fixed variant (register.FIXED_VARIANTS: a proof, a construction, a fixed formula, one question for
            # every seed) runs on FIXED_SEEDS seeds in the default run; --deep runs all of them.  The list is reviewed,
            # not guessed from a few seeds: a probe of 3 seeds took 3 to 7 varied slots (up to 9 questions in 20
            # seeds) for fixed ones, depending on --seed (variety review, 2026-10-27).
            listed = s.label in register.FIXED_VARIANTS
            fixed = listed and not args.deep
            n_fixed += fixed
            sigs = set()
            for r in range(base, base + (FIXED_SEEDS if fixed else n_seeds)):
                got = generate_one(s, r)
                if got:
                    keep_one(s, r, *got)
                    if listed or args.deep:
                        sigs.add(fixed_signature(got[0]))
            if listed and len(sigs) > 1:
                issue('register', s.label, f'listed in register.FIXED_VARIANTS but gives {len(sigs)} different questions; '
                                           'take it off the list')
            elif args.deep and not listed and len(sigs) == 1:
                unlisted_fixed.append(s.label)
        if unlisted_fixed:
            tally['fixed_unlisted'] = unlisted_fixed

    # 1. practice re-solve (+ 4. stated accuracy shares the same outcomes)
    if want('practice') or want('accuracy'):
        verified = 0
        per_slot = {}
        for s, r, p, o in cache:
            exempt = f'{s.slug}/{s.mode}/{s.fn}' in register.EXEMPT
            if o.status == 'verified':
                per_slot.setdefault(s, True)
                if want('accuracy'):
                    for m in keys_exact_or_stated(p, o):
                        issue('stated_accuracy', f'{s.label}#{r}', m)
                continue
            per_slot[s] = False
            if exempt:
                continue
            for kind, msg in (o.findings or [('norecord', 'no record() call reached')]):
                name = 'stated_accuracy' if kind == 'accuracy' else 'practice_resolve'
                if (name == 'stated_accuracy' and want('accuracy')) or (name == 'practice_resolve' and want('practice')):
                    issue(name, f'{s.label}#{r}', f'[{kind}] {msg} :: {plain(p["question"])[-90:]!r}')
        for s, ok in per_slot.items():
            if ok and f'{s.slug}/{s.mode}/{s.fn}' in register.EXEMPT:
                issue('register', s.label, 'stale exemption: the slot verifies on every seed, remove it from EXEMPT')
        verified = sum(1 for ok in per_slot.values() if ok)
        tally['practice_verified'] = sum(1 for s in practice if per_slot.get(s)) if per_slot else 0
        tally['practice_questions'] = len(cache)
        del verified

    # 2. MCQ key
    if want('mcq'):
        direct_ok = set()
        for s in direct:
            ok = True
            for r in range(base, base + cfg['mcq_direct']):
                try:
                    p, recs = harness.generate(s, r)
                except Exception as exc:
                    issue('mcq_key', f'{s.label}#{r}', f'generator raised {exc!r}')
                    ok = False
                    continue
                o = engine.verify_problem(p, recs)
                if o.status != 'verified':
                    ok = False
                    for kind, msg in o.findings or [('norecord', 'no record() call reached')]:
                        name = 'stated_accuracy' if kind == 'accuracy' else 'mcq_key'
                        issue(name, f'{s.label}#{r}', f'[{kind}] {msg} :: {plain(p["question"])[-90:]!r}')
                else:
                    for m in keys_exact_or_stated(p, o):
                        issue('stated_accuracy', f'{s.label}#{r}', m)
            if ok:
                direct_ok.add(s)
        tally['mcq_direct_verified'] = len(direct_ok)
        tally['mcq_direct_total'] = len(direct)

        n_proc = 0
        for slug in sorted(mcq.BANK_REFS):
            for fn in mcq.procedural(slug):
                n_proc += 1
                for r in range(base, base + cfg['procedural']):
                    try:
                        o = mcq.verify_procedural(slug, fn, r)
                    except Exception as exc:
                        issue('mcq_key', f'{slug}/{fn.__name__}#{r}', f'raised {exc!r}')
                        continue
                    if r - base < PROC_SAMPLES:
                        proc_samples.setdefault(slug, {}).setdefault(fn.__name__, []).append(
                            (o.records[-1]['family'] if o.records else '', variety.template(o.problem.get('question', ''))))
                    if o.status != 'verified':
                        for kind, msg in o.findings or [('norecord', 'no record() call reached')]:
                            issue('mcq_key', f'{slug}/{fn.__name__}#{r}', f'[{kind}] {msg}')
                    else:
                        for m in keys_exact_or_stated(o.problem, o):
                            issue('stated_accuracy', f'{slug}/{fn.__name__}#{r}', m)
        tally['procedural_functions'] = n_proc

        resolved = exempt = 0
        bank_tried = bank_caught = 0
        root_tried = root_caught = root_spec_tried = root_spec_caught = 0
        seen = set()
        for slug in sorted(mcq.BANK_REFS):
            for i, item in enumerate(mcq.bank(slug)):
                d = mcq.item_digest(item)
                seen.add(d)
                where = f'{slug} bank item {i} ({d})'
                for m in mcq.item_structure_errors(item):
                    issue('mcq_key', where, m)
                for ltr, mutant in mcq.unworked_root_mutants(item):         # mutation: an unworked root equal to the key
                    root_tried += 1
                    shown = dict(mcq.item_view(mutant)[1])[ltr]
                    if any('same value as the key' in m for m in mcq.item_structure_errors(mutant)):
                        root_caught += 1
                    else:
                        issue('negative_control', where, f'option {ltr} rewritten as {shown!r} (the key\'s value) was not flagged as a duplicate')
                    if d in solvers_bank.SPECS:
                        root_spec_tried += 1
                        if mcq.verify_static(mutant, digest=d).status != 'verified':
                            root_spec_caught += 1
                        else:
                            issue('negative_control', where, f'option {ltr} rewritten as {shown!r} still passes its re-solve spec')
                in_specs, in_exempt = d in solvers_bank.SPECS, d in register.STATIC_EXEMPT
                if in_specs and in_exempt:
                    issue('register', where, 'item has a re-solve spec and is also listed in STATIC_EXEMPT (remove the exemption)')
                elif in_specs:
                    o = mcq.verify_static(item)
                    if o.status != 'verified':
                        for kind, msg in o.findings or [('norecord', 'no result')]:
                            issue('mcq_key', where, f'[{kind}] {msg} :: {plain(item.get("q", ""))[:70]!r}')
                    else:
                        resolved += 1
                        for q_, tried_, caught_ in mcq.tampered_item_checks(item, d):
                            bank_tried += tried_
                            bank_caught += caught_
                            if tried_ != caught_:
                                issue('negative_control', where, f'a wrong key {q_} was still verified')
                elif in_exempt:
                    exempt += 1
                else:
                    issue('mcq_key', where, f'not reviewed: digest {d} has no re-solve spec (solvers_bank_*.py) and is not in '
                          f'register.STATIC_EXEMPT (question: {plain(item.get("q", ""))[:70]!r})')
        for d in sorted(set(solvers_bank.SPECS) - seen):
            issue('mcq_key', f'bank spec {d}', 'matches no bank item (the item changed or was removed; update or remove its spec)')
        for d in sorted(set(register.STATIC_EXEMPT) - seen):
            issue('register', f'STATIC_EXEMPT {d}', 'matches no bank item (the item changed or was removed)')
        tally['bank_negative_control'] = f'{bank_caught}/{bank_tried}'
        tally['unworked_root_control'] = f'{root_caught}/{root_tried}'
        tally['unworked_root_spec_control'] = f'{root_spec_caught}/{root_spec_tried}'
        tally['resolved_items'] = resolved
        tally['pinned_items'] = exempt
        tally['mcq_dispatch_slots'] = len(dispatch)

    # 3. checker round-trip
    if want('roundtrip') or want('answer_form'):
        n = 0
        n_wrong_form = 0
        n_units = 0
        n_long = 0
        for s, r, p, o in cache:
            if r >= base + cfg['roundtrip']:
                continue
            at, raw = p.get('answer_type'), p.get('correct_answer_raw')
            if not at or raw is None or at in forms.UNTYPED:
                continue
            n += 1
            where = f'{s.label}#{r}'
            ftypes = p.get('answer_field_types') if at == 'number_fields' else None
            form, subject = p.get('answer_form'), p.get('answer_subject')

            qtext = answer_units.problem_question_text(p)       # what the app hands the checker (the units it asks for)
            if len(str(p['question'])) > answer_units.MAX_QUESTION_LEN:
                # a drawn question is 6 to 11 KB of SVG ahead of its ask; the unit reader must still reach the ask
                # (C1 review finding 3: it cut the raw text first, so eleven older drawn slots never had their unit
                # read; batch C2 pins the fix here for every long question the run generates)
                # the last words of the visible question (tags and drawings dropped, as the reader drops them)
                words = re.findall(r'[a-z]{3,}', re.sub(r'<[^>]*>', ' ', str(p['question'])).lower())
                tail = ' '.join(words[-3:])
                read = ' '.join(re.findall(r'[a-z]{3,}', answer_units.question_plain_text(qtext)))
                if tail and tail not in read:
                    issue('unit_roundtrip', where, f'the unit reader does not reach the ask of a {len(str(p["question"]))}-character question')
                n_long += 1

            def chk(name, key, typed, _ft=ftypes, _form=form, _subject=subject, _q=qtext):
                # the app passes the question's field types to number_fields, and the stored problem's
                # written form and subject letter to the other checkers (app.py). Mixed-type keys
                # (equation and pair fields) are typed by the web form, so a plain-text echo is judged
                # with and without the types and passes if either accepts it; rejections use the types.
                res = check_answer(name, key, typed, form=_form, subject=_subject, question=_q)
                if _ft and not res['correct']:
                    res = CHECKERS[name](key, typed, field_types=_ft, question=_q)
                return res
            try:
                if not chk(at, raw, forms.canonical(at, raw))['correct']:
                    issue('checker_roundtrip', where, f'{at}: key {raw!r} rejected when typed {forms.canonical(at, raw)!r}')
                for f in forms.accepted_forms(at, raw, plain(p['question'])):
                    if not chk(at, raw, f)['correct']:
                        issue('checker_roundtrip', where, f'{at}: key {raw!r} should accept {f!r}')
                for f in forms.rejected_forms(at, raw):
                    if chk(at, raw, f)['correct']:
                        issue('checker_roundtrip', where, f'{at}: key {raw!r} wrongly accepts {f!r}')
                # units and symbols the question states ride along with the number (finding 13, 2026-10-27): the key
                # typed with each of them is right, and a unit the question does not ask for is refused with the
                # unit message, never read as the same number
                good_units = forms.unit_variants(at, raw, qtext, form)
                for f in good_units:
                    if not chk(at, raw, f)['correct']:
                        issue('unit_roundtrip', where, f'{at}: key {raw!r} rejected when typed with its unit as {f!r}')
                for f in forms.wrong_unit_variants(at, raw, qtext, form):
                    res = chk(at, raw, f)
                    if res['correct'] or not str(res.get('feedback', '')).startswith('Check the units'):
                        issue('unit_roundtrip', where, f'{at}: key {raw!r}, {f!r} should be refused with the unit message, got {res}')
                n_units += bool(good_units)
                if form:
                    # a value-equal entry in the wrong written form is refused with the form message
                    for typed, kind in forms.wrong_form_entries(at, raw, form, plain(p['question'])):
                        res = chk(at, raw, typed)
                        if not check_answer(at, raw, typed)['correct']:
                            issue('answer_form', where, f'{at}: {typed!r} should be equal to key {raw!r} (bad test entry)')
                        elif res['correct'] or res.get('wrong_form') != kind:
                            issue('answer_form', where, f'{at}: key {raw!r} form {form}: {typed!r} gave {res} (want {kind})')
                        elif not res['feedback'].startswith("That's equal"):
                            issue('answer_form', where, f'form message does not read as the kind form message: {res["feedback"]!r}')
                    n_wrong_form += 1
            except Exception as exc:
                issue('checker_roundtrip', where, f'{at}: checker raised {exc!r} for key {raw!r}')
        tally['roundtrip_questions'] = n
        tally['unit_roundtrip_questions'] = n_units
        tally['long_questions_read'] = n_long
        if not wanted and n_units < 400:
            # a full run types about 1,400 questions' keys with their units; far fewer means the question reader stopped
            # finding the units (answer_units.question_units) and the check above no longer guards anything
            issue('unit_roundtrip', 'coverage', f'only {n_units} questions were typed with their units (expected 400 or more)')
        tally['wrong_form_questions'] = n_wrong_form

    # 3a. ordered proofs: any valid order is accepted, the key is one of them, a dependent swap is refused
    if want('ordering'):
        n = n_alt = 0
        structures = set()
        seen_alt = set()
        seen_slots = set()
        for s, r, p, o in cache:
            raw = p.get('correct_answer_raw')
            if p.get('answer_type') != 'proof_steps' or raw is None or not str(raw).startswith('1|'):
                continue
            key = f'{s.slug}/{s.mode}/{s.fn}'
            n += 1
            seen_slots.add(key)
            if p.get('answer_step_prereqs'):
                n_alt += 1
                seen_alt.add(key)
            for m in ordering_errors(p, key, structures):
                issue('ordering', f'{s.label}#{r}', m)
        if not wanted:
            for key in sorted(set(register.ORDER_FREE_PAIRS) - seen_alt):
                issue('ordering', key, 'listed in register.ORDER_FREE_PAIRS but no generated problem carried accepted orders')
        tally['ordering_questions'] = n
        tally['ordering_with_alternatives'] = n_alt
        tally['ordering_slots'] = len(seen_slots)
        tally['ordering_slots_with_alternatives'] = len(seen_alt)

    # 3b. every expand / factorise / simplest-surd slot names the form it needs (found by the recorded task)
    if want('roundtrip') or want('answer_form'):
        # Whole-change review C4: an answer-box example naming a different letter from the key's ("e.g. y = 3" under a
        # question that asks for k) sent a pupil who followed it to "Check the letter".  Typing the example must never
        # get that refusal, and must never be marked correct (the example may not hand over the answer).
        n_examples = 0
        seen_examples = set()
        for s, r, p, o in cache:
            hint, at, raw = str(p.get('answer_format_hint') or ''), p.get('answer_type'), p.get('correct_answer_raw')
            m = re.search(r'e\.g\.?\s+([A-Za-z])\s*=\s*(-?[\d./]+)', hint)
            if not m or not at or raw is None or at in forms.UNTYPED:
                continue
            example = f'{m.group(1)} = {m.group(2)}'
            n_examples += 1
            if (s.label, example, str(raw)) in seen_examples:
                continue
            seen_examples.add((s.label, example, str(raw)))
            res = check_answer(at, raw, example, form=p.get('answer_form'), subject=p.get('answer_subject'),
                               question=answer_units.problem_question_text(p))
            where = f'{s.label}#{r}'
            if res.get('wrong_letter') or 'Check the letter' in str(res.get('feedback') or ''):
                issue('example_letter', where, f'the box example {example!r} is refused as the wrong letter (key {raw!r})')
            if res.get('correct'):
                issue('example_letter', where, f'the box example {example!r} is marked correct (key {raw!r})')
        tally['example_letter'] = n_examples

        # Whole-change review C1: whatever the box says after "e.g." must never be the answer.  Every placeholder
        # example (first alternative, before " or ", a dash note or a bracket) is typed with the stored form, over the
        # seeds of the run; a default built from the key (surd binomials, "e.g. a - b" under the key a - b, a fixed
        # "e.g. √13" on the draw whose answer is √13) is marked correct and fails here.
        n_any = 0
        seen_any = set()
        for s, r, p, o in cache:
            hint, at, raw = str(p.get('answer_format_hint') or ''), p.get('answer_type'), p.get('correct_answer_raw')
            m = re.search(r'e\.g\.?\s+(.+)', hint)
            if not m or not at or raw is None or at in forms.UNTYPED or re.search(r'\byes or no\b', hint):
                continue
            example = re.split(r'\s+or\s+|\s+[\u2014\u2013]\s+|\s+-\s+use\b|\s+\(|\)|;', m.group(1))[0].strip().rstrip('.,')
            if not example:
                continue
            n_any += 1
            if (s.label, example, str(raw)) in seen_any:
                continue
            seen_any.add((s.label, example, str(raw)))
            res = check_answer(at, raw, example, form=p.get('answer_form'), subject=p.get('answer_subject'),
                               question=answer_units.problem_question_text(p))
            if res.get('correct'):
                issue('example_is_key', f'{s.label}#{r}', f'the box example {example!r} is marked correct (key {raw!r}, hint {hint!r})')
        tally['example_any'] = n_any

        # The shared net (generators/shared/example_hint.py) moves a coinciding example off the key, so the generators
        # themselves are checked unwrapped for the slots whose default example used to be the key (surd binomials,
        # (√a + √b)(√a − √b)), and the net has a negative control: a hint equal to the key must be changed.
        import random as _random
        from generators.shared.example_hint import keep_example_off_key
        for slug, tier, fn in (('surds', 'intermediate', 'gcse_surds_expand_single_bracket'),
                               ('surds', 'intermediate', 'gcse_surds_square_bracket'),
                               ('surds', 'intermediate', 'gcse_surds_practice_double_bracket'),
                               ('surds', 'difficult', 'gcse_surds_identity')):
            raw_func = harness.topics()[slug]['func']
            raw_func = getattr(raw_func, '__wrapped__', raw_func)
            for r in range(6):
                _random.seed(1000 + r)
                p = raw_func(tier, 'practice', variant_name=fn)
                m = re.search(r'e\.g\.?\s+(.+)', str(p.get('answer_format_hint') or ''))
                if m and check_answer(p['answer_type'], p['correct_answer_raw'], m.group(1).strip(),
                                      form=p.get('answer_form'), question=answer_units.problem_question_text(p)).get('correct'):
                    issue('example_is_key', f'{slug}/{tier}/{fn}#{r}', f'the generator itself shows the key as the example {m.group(1)!r}')
        probe = {'question': 'Write 0.75 as a fraction.', 'answer_type': 'fraction', 'correct_answer_raw': '3/4',
                 'answer_format_hint': 'Enter a fraction (e.g. 3/4)'}
        # fix pass 2026-11-03: a symbolic key written the sympy way ('2*x**2 + 5*x + 3') must also be recognised by the net
        # (its comparison lost the '*' of '**' and the example '2x^2 + 5x + 3' stayed equal to the key on one draw in 120)
        for key_raw, key_hint in (('2*x**2 + 5*x + 3', 'Enter the expanded expression, e.g. 2x^2 + 5x + 3'),
                                  ('x**2 - 4', 'Enter the expression, e.g. x^2 - 4')):
            sym = keep_example_off_key({'question': 'Expand.', 'answer_type': 'algebraic',
                                        'correct_answer_raw': key_raw, 'answer_format_hint': key_hint})
            if sym['answer_format_hint'] == key_hint:
                issue('example_is_key', 'example_hint', f'negative control: the net left the example equal to the sympy key {key_raw!r}')
        if keep_example_off_key(dict(probe)).get('answer_format_hint') == probe['answer_format_hint']:
            issue('example_is_key', 'example_hint', 'negative control: the net left an example equal to the key')
        # the moved example is the same in every process (no set order) and a fraction stays in lowest terms (fix
        # review 2026-11-03: "e.g. 1/3" became 2/3 or 1/4 by hash seed; "e.g. 3/8" could become 4/8)
        for key, want_hint in (('1/3', 'Enter a fraction (e.g. 2/3)'), ('3/4', 'Enter a fraction (e.g. 3/5)'),
                               ('3/8', 'Enter a fraction (e.g. 5/8)')):
            got = keep_example_off_key({'question': 'Find the probability.', 'answer_type': 'fraction',
                                        'correct_answer_raw': key,
                                        'answer_format_hint': f'Enter a fraction (e.g. {key})'})['answer_format_hint']
            if got != want_hint:
                issue('example_is_key', 'example_hint', f'the example for {key} moved to {got!r}, not {want_hint!r}')

    if want('answer_form'):
        n = 0
        asks = {'expand': 'expanded', 'factorise': 'factorised'}
        for s, r, p, o in cache:
            at, raw = p.get('answer_type'), str(p.get('correct_answer_raw'))
            text = plain(p['question'])
            form = p.get('answer_form')
            recs = getattr(o, 'records', None) or []
            inputs = recs[-1]['inputs'] if recs else {}
            task = inputs.get('task')
            where = f'{s.label}#{r}'
            want_form = None
            if task in asks and at == 'algebraic' and not forms._surd_binomial_parts(raw):
                want_form = asks[task]          # surd p+q root r keys fix the expanded shape in the key itself
            elif task == 'surd' and at == 'surd' and forms.FORM_QUESTION_WORDS['simplest_surd'].search(text):
                want_form = 'simplest_surd'
            elif (task == 'surd' and at == 'algebraic_fraction' and re.fullmatch(r'-?\d+\|\d+\|\d+', raw)
                  and forms.FORM_QUESTION_WORDS['simplest_surd'].search(text)):
                want_form = 'simplest_surd'
            elif task == 'surd' and inputs.get('mode') == 'identity' and at == 'algebraic':
                want_form = 'expanded'
            elif (task == 'simplify' and at == 'algebraic' and '/' not in raw
                  and forms.FORM_QUESTION_WORDS['simplified'].search(text)
                  and re.search(r'\)/\([^()]*[a-z]', text)):
                want_form = 'simplified'        # "Simplify" a fraction with a letter underneath, whole answer
            elif (task == 'simplify' and at == 'algebraic' and re.match(r'\s*simplify\b', text, re.I)
                  and re.fullmatch(r'(?:\d+\*)?[a-z]\*\*\d+', raw)):
                want_form = 'simplified'        # one term (the index laws): the question's product typed back is refused
            elif (task == 'simplify' and at == 'algebraic' and re.match(r'\s*simplify\b', text, re.I)
                  and not re.search(r'[/()]', raw) and re.search(r' [+-] ', raw)):
                want_form = 'expanded'          # collect like terms: the question's own terms typed back are refused
            elif task == 'simplify' and at == 'algebraic_fraction' and re.match(r'\s*simplify\b', text, re.I):
                # "Simplify" with a fraction key: the question's own fraction typed back is equal but not simplified
                # (batch C2: the five older algebraic_fractions slots gained the form, review finding 20.7)
                want_form = 'simplified'
            elif (at == 'algebraic' and re.search(r'\bexpand', text, re.I) and not re.search(r'[()/]', raw)
                  and re.search(r' [+-] ', raw)):
                # "Write f(g(x)) ... expanded and simplified" (batch B review, 2026-10-28): a task other than 'expand'
                # (fn_eval) with no form let (2x - 5)^2 typed back be marked right; a topic wrapper had dropped the form
                want_form = 'expanded'
            elif (s.slug == 'probability' and at in ('fraction', 'number')
                  and forms.FORM_QUESTION_WORDS['probability'].search(text)
                  and (lambda v: v is not None and 0 <= v <= 1)(forms._num(raw))):
                want_form = 'probability'       # "Find P(...)": a percentage is accepted as well
            elif at == 'fraction' and re.search(r'simplest\s+form|lowest\s+terms', text, re.I):
                # "as a fraction (or mixed number) in its simplest form": 48/88 for 6/11, 0.8 for 4/5 and 6 26/60 for
                # 6 13/30 are refused (whole-change review C2: the 13 slots that ask carried no form)
                want_form = 'simplified'
            elif at == 'ratio' and re.search(r'simplif|simplest\s+form', text, re.I):
                want_form = 'simplified'        # "Simplify the ratio 45:55": 45:55 typed back is refused (review C3)
            if want_form:
                n += 1
                if form != want_form:
                    issue('answer_form', where, f'{task} question ({at}) needs answer_form={want_form!r}, has {form!r} :: {text[:80]!r}')
            if form:
                if form not in ANSWER_FORMS:
                    issue('answer_form', where, f'unknown answer_form {form!r}')
                elif at not in FORM_AWARE_ANSWER_TYPES:
                    issue('answer_form', where, f'answer_form {form!r} on a {at} answer, which ignores it')
                elif not forms.FORM_QUESTION_WORDS[form].search(text):
                    issue('answer_form', where, f'answer_form {form!r} but the question does not ask for it :: {text[:80]!r}')
                elif form == 'probability' and PROBABILITY_FORM_FIXED.search(text):
                    # the probability form also takes a percentage, which would not answer these
                    issue('answer_form', where, f'answer_form probability but the question fixes the form :: {text[-80:]!r}')
        tally['form_questions'] = n

    # Negative control: tampered keys must fail verification, otherwise the check proves nothing.
    if want('negative') or want('practice'):
        tried = caught = 0
        seen = set()
        for s, r, p, o in cache:
            if s in seen or o.status != 'verified':
                continue
            seen.add(s)
            q = tamper(p)
            if q is None:
                continue
            recs = o.records             # the records of this very generation (cached above)
            tried += 1
            if engine.verify_problem(q, recs).status == 'verified':
                issue('negative_control', f'{s.label}#{r}', f'a tampered key was still verified: {q.get("correct_answer_raw")!r}')
            else:
                caught += 1
        tally['negative_control'] = f'{caught}/{tried}'

    # Negative control for the worded proofs: a loosened or tightened order, a swapped step, a distractor that
    # says what a keyed step says and a changed number must each fail the proof model.
    if want('negative') or want('practice'):
        tried = caught = 0
        seen = set()
        for s, r, p, o in cache:
            recs = o.records
            if s in seen or o.status != 'verified' or not recs or recs[-1]['family'] != 'proof_model':
                continue
            seen.add(s)
            for what, q in proof_tampers(p):
                tried += 1
                if engine.verify_problem(q, recs).status == 'verified':
                    issue('negative_control', f'{s.label}#{r}', f'a damaged proof ({what}) was still verified')
                else:
                    caught += 1
        tally['proof_negative_control'] = f'{caught}/{tried}'

    # Negative control for drawings: damaging the SVG must make the family's diagram check complain,
    # otherwise reading the drawing proves nothing.
    if want('negative') or want('practice'):
        state, tries = {}, collections.Counter()
        for s, r, p, o in cache:
            if o.status != 'verified' or '<svg' not in str(p.get('question', '')):
                continue
            recs = o.records
            fam = recs[-1]['family'] if recs else None
            if fam not in DIAGRAM_CHECKS or state.get(fam) or tries[fam] >= 4:
                continue
            tries[fam] += 1
            state.setdefault(fam, False)
            for q in svg_tampers(p):
                if engine.verify_problem(q, recs).status != 'verified':
                    state[fam] = True
                    break
        for fam, caught_it in sorted(state.items()):
            if not caught_it:
                issue('negative_control', f'diagram:{fam}', 'a damaged drawing was still verified')
        tally['diagram_negative_control'] = f'{sum(state.values())}/{len(state)}'

    # Negative control for the question's ask (whole-change review C8): on a drawn question the sentence after the
    # drawing is changed to ask about another amount, year, interval or group, and the key is left as it was.  Both
    # reviewer mutations (the conversion graph asks a different amount; the time series asks the other year) are in
    # it.  The change is made to the question text outside the <svg>, so it must be the sentence guard or the
    # family's own check of the printed ask that reports it.
    if want('negative') or want('practice'):
        from gcse_verify.registry import ASKED_IN_SENTENCE
        ask_state, ask_tries = {}, collections.Counter()
        for s, r, p, o in cache:
            recs = o.records
            fam = recs[-1]['family'] if recs else None
            if o.status != 'verified' or fam not in ASKED_IN_SENTENCE or ask_tries[fam] >= 6:
                continue
            q = str(p.get('question', ''))
            head, sep, tail = q.rpartition('</svg>')
            if not sep:
                continue
            ask_tries[fam] += 1
            ask_state.setdefault(fam, False)
            for name in ASKED_IN_SENTENCE[fam]:
                value = recs[-1]['inputs'].get(name)
                if value is None:
                    continue
                if isinstance(value, str):
                    new_tail = tail.replace(value, 'some other group', 1)
                elif fam == 'stats_series_mean':
                    years = [int(y) for y in recs[-1]['inputs']['years']]
                    new_tail = tail.replace(str(value), str(sum(years) - int(value)), 1)
                else:
                    new_tail = re.sub(rf'(?<![\d.]){value}(?![\d.])', str(int(value) + 1), tail, count=1)
                if new_tail != tail and engine.verify_problem(dict(p, question=head + sep + new_tail), recs).status != 'verified':
                    ask_state[fam] = True
        for fam, caught_it in sorted(ask_state.items()):
            if not caught_it:
                issue('negative_control', f'ask:{fam}', 'a question asking about another amount, year or group was still verified')
        missing = set(ASKED_IN_SENTENCE) - set(ask_state)
        if not wanted and missing:
            issue('negative_control', 'ask', f'no drawn question was found to damage for {sorted(missing)}')
        tally['ask_negative_control'] = f'{sum(ask_state.values())}/{len(ask_state)}'

    # 4b. the lesson quizzes pupils get from each topic page (scripts/gcse_verify/quiz.py)
    if want('quiz'):
        for slug in sorted(harness.topics()):
            for seed in range(base, base + cfg['quiz']):
                found, counts = quiz.check_quiz(slug, seed, solvers_bank)
                qt.update(counts)
                for m in found:
                    issue('quiz', f'{slug} quiz seed {seed}', m)
        tally['quiz'] = dict(qt)
        caught = tried = 0                  # negative control: a quiz whose keys all moved must be reported question by question
        for slug in ('bidmas', 'trigonometry', 'circle_theorems', 'probability', 'surds'):
            found, counts = quiz.check_quiz(slug, base, solvers_bank, wrong_keys=True)
            tried += counts['generated'] + counts['bank']
            caught += len({m.split(':')[0] for m in found if m.startswith('question') and '[' in m})
        tally['quiz_negative_control'] = f'{caught}/{tried}'
        if caught < tried:
            issue('negative_control', 'quiz', f'only {caught} of {tried} wrong quiz keys were reported')
        tally['quiz_quizzes'] = len(harness.topics()) * cfg['quiz']

    # 5. properties (L1).  Phase 1 topics only: the pending topics have known structural gaps that
    # move into scope with their phase (e.g. 3-option items and checker-format keys in graphs and surds).
    if want('properties'):
        n = 0
        # practice problems already generated above are reused (no_output_drift proves recording changes nothing)
        cached = {(c[0], c[1]): c[2] for c in cache}
        for s in practice + mcq_slots:
            for r in (base, base + 1):
                try:
                    p = cached[(s, r)] if (s, r) in cached else harness.generate(s, r, record=False)[0]
                except Exception as exc:
                    issue('properties', s.label, f'generator raised {exc!r}')
                    continue
                n += 1
                text = plain(p['question'])
                if s.slug in register.ALGEBRA_TOPICS or s.slug in register.PHASE3_TOPICS:
                    # whole-change review C10: the worked solution is read too (1x = 5, (x + 0)(x + 7), 1(x - 1) were
                    # all in solutions and passed)
                    shown = (text + ' ' + ' '.join(plain(str(o)) for o in p.get('options') or []) + ' '
                             + plain(str(p.get('solution') or '')))
                    for what, pat in COSMETIC.items():
                        m = pat.search(shown)
                        if m and what not in COSMETIC_REVIEWED.get(s.label, ()):
                            issue('properties', s.label, f'{what}: {shown[max(0, m.start() - 25):m.end() + 25]!r}')
                m_money = MONEY_ONE_DP.search(' '.join([text, plain(str(p.get('solution') or '')),
                                                        *(plain(str(o)) for o in p.get('options') or [])]))
                if m_money:
                    issue('properties', s.label, f'money with one decimal place: {m_money.group()!r}')
                for m in unordered_box_errors(p):
                    issue('properties', s.label, m)
                for where, shown in (('question', p['question']), ('worked solution', p.get('solution')), ('hint', p.get('hint')),
                                     *(('option', o) for o in p.get('options') or [])):
                    for m in ordinals.ordinal_errors(plain(str(shown or ''))):
                        issue('properties', s.label, f'{m} (in the {where})')
                for bad in ('None', 'nan', 'inf', '{{', '}}', 'undefined'):
                    if re.search(rf'(?<![A-Za-z]){re.escape(bad)}(?![A-Za-z])', text):
                        issue('properties', s.label, f'question contains {bad!r}')
                if p.get('options'):
                    item = {'q': p['question'], 'opts': p['options'], 'ans': p.get('correct_answer')}
                    for m in mcq.item_structure_errors(item):
                        if s.mode == 'standard' and m.endswith('(expected 4)'):
                            continue            # practice "which is larger" questions legitimately have two options
                        issue('properties', s.label, m)
                elif not p.get('answer_type') and p.get('correct_answer_raw') is not None:
                    issue('properties', s.label, 'a key without an answer_type')
        tally['properties_questions'] = n

    # 6. no output drift
    if want('drift'):
        n = 0
        for s in slots:
            for r in range(base, base + cfg['drift']):
                digests = []
                for rec in (True, False):
                    try:
                        p, _ = harness.generate(s, r, record=rec)
                    except Exception as exc:
                        digests.append(f'raised {type(exc).__name__}')
                        continue
                    blob = SVG_COUNTER.sub(r'\1-N', json.dumps(p, sort_keys=True, default=str))
                    digests.append(hashlib.sha256(blob.encode()).hexdigest())
                n += 1
                if digests[0] != digests[1]:
                    issue('no_output_drift', f'{s.label}#{r}', 'output differs with recording on and off')
        tally['drift_generations'] = n

    # 7. radio towers: both answers occur, about equally often, never borderline, and the worked solution agrees
    if want('overlap'):
        slot = next((s for s in slots if s.fn == '_cl_d12_two_radio_towers' and s.mode == 'standard'), None)
        if slot is None:
            issue('overlap_outcomes', 'constructions_loci', '_cl_d12_two_radio_towers is not a registered slot')
        else:
            n_runs, yes = (400 if args.deep else 100), 0
            for r in range(base, base + n_runs):
                p, recs = harness.generate(slot, r)
                inputs = recs[-1]['inputs'] if recs else None
                where = f'{slot.label}#{r}'
                if not inputs:
                    issue('overlap_outcomes', where, 'no record')
                    continue
                d, r1, r2 = (inputs[k] for k in ('d', 'r1', 'r2'))
                overlap = r1 + r2 > d           # worked out here, not read from the key
                yes += overlap
                if abs(d - (r1 + r2)) < 2:
                    issue('overlap_outcomes', where, f'ranges {r1} + {r2} are too close to the distance {d} (need a margin of 2 km)')
                right, wrong = ('DO overlap', 'do NOT overlap') if overlap else ('do NOT overlap', 'DO overlap')
                if right not in p['solution'] or wrong in p['solution']:
                    issue('overlap_outcomes', where, f'the worked solution does not say the zones {right.replace("DO ", "").replace("do NOT", "do not")}')
                key = plain(next(o for o in p['options'] if o.startswith(p['correct_answer'])))
                if overlap != key.split(' ', 1)[1].startswith('Yes'):
                    issue('overlap_outcomes', where, f'the keyed option disagrees with {r1} + {r2} against {d}: {key!r}')
            tally['overlap_yes'] = f'{yes} of {n_runs}'
            if not 0.3 * n_runs <= yes <= 0.7 * n_runs:
                issue('overlap_outcomes', slot.label, f'{yes} of {n_runs} questions have the answer yes (want roughly half)')

    # 8. variety: kinds per tier, duplicate slots, queue repeats, MCQ kinds per band, repeated kinds in quizzes
    if want('variety'):
        t_variety = time.perf_counter()
        vcache = [c for c in cache if c[1] < base + cfg['variety_runs']]
        pr = variety.practice(practice, vcache)
        if not proc_samples:                                # --only variety: the procedural functions are not run by the MCQ check
            from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for  # noqa: F401
            for slug in sorted(mcq.BANK_REFS):
                for fn in mcq.procedural(slug):
                    for r in range(base, base + PROC_SAMPLES):
                        p_, recs_ = harness.generate_callable(slug, fn, zlib.crc32(f'{slug}/difficult/{fn.__name__}'.encode()) + r)
                        proc_samples.setdefault(slug, {}).setdefault(fn.__name__, []).append(
                            (recs_[-1]['family'] if recs_ else '', variety.template(p_['question'])))
        bands = variety.mcq_bands(slots, proc_samples, per_slot=25 if args.variety_report else variety.MCQ_SAMPLES_PER_SLOT)
        quiz_counts = dict(qt)
        if args.variety_report:                             # 30 seeded quizzes per topic, like the plan's measurement
            quiz_counts = collections.Counter()
            for slug in sorted(harness.topics()):
                for seed in range(7000, 7030):
                    try:
                        problems, records = quiz.build(slug, seed)
                    except Exception:
                        continue
                    quiz_counts.update(quiz.repeat_counts(slug, problems))
        for m in variety.quiz_repeat_issues(quiz_counts):
            issue('variety', 'quiz kind', m)
        tally['quiz_repeat_control'] = variety.quiz_repeat_issue({'quizzes': 100, 'repeated': 3}) is not None   # negative control
        if not tally['quiz_repeat_control']:
            issue('variety', 'quiz kind', 'negative control: 3 of 100 quizzes repeating was not caught')
        tight = args.seed == 0 and not args.deep and not args.variety_report
        for m in variety.ratchet_issues(pr, bands, tight=tight):
            issue('variety', 'ratchet', m)
        tally['variety'] = variety.render(pr, bands, quiz_counts)
        if args.variety_report:
            tally['variety'] += '\n' + variety.full_tables(pr, bands)
        tally['variety_totals'] = pr['totals']
        tally['fixed_variants_cut'] = n_fixed
        tally['variety_seconds'] = round(time.perf_counter() - t_variety, 2)

    tally['seconds'] = round(time.time() - t0, 1)
    return slots, tally


CHECK_NAMES = ('independence', 'register', 'solvers', 'practice_resolve', 'mcq_key', 'checker_roundtrip', 'ordering', 'overlap_outcomes',
               'answer_form', 'stated_accuracy', 'negative_control', 'quiz', 'properties', 'no_output_drift', 'option_values',
               'variety', 'retired')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deep', action='store_true')
    ap.add_argument('--only', default='')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--print-digests', action='store_true')
    ap.add_argument('--variety-report', action='store_true')
    args = ap.parse_args()

    if args.print_digests:
        for slug in sorted(mcq.BANK_REFS):
            print(slug, sorted(mcq.item_digest(i) for i in mcq.bank(slug)))
        return

    wanted = [w for w in args.only.split(',') if w]
    if args.variety_report:
        wanted = ['variety']
    t0 = time.time()
    slots_all = harness.enumerate_slots()
    if not wanted or any(w in 'independence' for w in wanted):
        check_independence()
    if not wanted or any(w in 'option_values' for w in wanted):
        check_option_values()
    if not wanted or any(w in 'option_units' for w in wanted):
        check_option_units()
    if not wanted or any(w in 'ordinals' for w in wanted):
        check_ordinals()
        check_fraction_words()
        check_unit_variant_cases()
        check_conversion_currency()
    if not wanted or any(w in 'register' for w in wanted):
        check_register(slots_all)
        check_concepts_and_reach(slots_all)
    if not wanted or any(w in 'solvers' for w in wanted):
        check_solver_table()
    if not wanted or any(w in 'retired' for w in wanted):
        check_retired(args, slots_all)
    slots, tally = run_checks(args, wanted)
    total = round(time.time() - t0, 1)

    cov = coverage.tables(slots, coverage.resolved_digests(), set(register.EXEMPT), mcq.DIRECT_TOPICS)
    if args.json:
        print(json.dumps({'issues': ISSUES, 'tally': tally, 'coverage': cov, 'seconds': total}, indent=2, default=str))
    else:
        print(f'GCSE maths verification: {tally.get("practice_questions", 0)} practice questions, '
              f'{tally.get("roundtrip_questions", 0)} checker round-trips '
              f'({tally.get("wrong_form_questions", 0)} with a required form, '
              f'{tally.get("unit_roundtrip_questions", 0)} typed with their units, '
              f'{tally.get("long_questions_read", 0)} drawn questions over {answer_units.MAX_QUESTION_LEN} characters '
              f'read to their ask), '
              f'{tally.get("drift_generations", 0)} drift generations, {total}s')
        if 'ordering_questions' in tally:
            print(f'  ordered proofs: {tally["ordering_questions"]} questions in {tally["ordering_slots"]} slots, '
                  f'{tally["ordering_with_alternatives"]} with alternative orders '
                  f'({tally["ordering_slots_with_alternatives"]} slots)')
        print(coverage.render(cov))
        if 'variety' in tally:
            print(tally['variety'])
            print(f'  fixed variants (register.FIXED_VARIANTS) run on {FIXED_SEEDS} seeds in this run: {tally.get("fixed_variants_cut", 0)}; '
                  f'the variety check took {tally.get("variety_seconds", 0)}s')
        if 'retired_names' in TALLY:
            print(f'  retired variants: {TALLY["retired_names"]} names resolved and re-solved on {TALLY["retired_generations"]} '
                  f'generations (negative control {TALLY.get("retired_negative_control", "n/a")})')
        if tally.get('fixed_unlisted'):
            print(f'  fixed on every seed of this run but not in register.FIXED_VARIANTS (could be listed after review): '
                  f'{", ".join(tally["fixed_unlisted"])}')
        print(f'  static MCQ items: {tally.get("resolved_items", 0)} re-solved, {tally.get("pinned_items", 0)} exempt and pinned '
              f'(negative control, wrong keys caught: {tally.get("bank_negative_control", "n/a")}; unworked roots worth the key '
              f'caught: {tally.get("unworked_root_control", "n/a")} by the structure check, '
              f'{tally.get("unworked_root_spec_control", "n/a")} by the re-solve spec)')
        if 'quiz' in tally:
            q_ = tally['quiz']
            print(f'  lesson quizzes: {tally["quiz_quizzes"]} quizzes, {q_.get("questions", 0)} questions '
                  f'({q_.get("generated", 0)} from generators re-solved, {q_.get("bank", 0)} bank items re-solved after the '
                  f'quiz shuffle, {q_.get("bank_exempt", 0)} reviewed exemptions), {q_.get("graded", 0)} letters graded '
                  f'(wrong quiz keys caught: {tally.get("quiz_negative_control", "n/a")})')
        if 'negative_control' in tally:
            print(f'  negative control (tampered keys caught): {tally["negative_control"]}')
            print(f'  negative control (damaged drawings caught, by family): {tally.get("diagram_negative_control", "n/a")}')
            print(f'  negative control (damaged proofs caught): {tally.get("proof_negative_control", "n/a")}')
            print(f'  negative control (question asks about another amount, year or group, caught by family): {tally.get("ask_negative_control", "n/a")}')
        n_issues = sum(len(v) for v in ISSUES.values())
        if n_issues:
            print(f'{n_issues} issue(s):')
            # review 2026-10-27: checks added later ('ordinals', ...) are not in CHECK_NAMES; they failed the run silently
            for name in CHECK_NAMES + tuple(sorted(set(ISSUES) - set(CHECK_NAMES))):
                rows = ISSUES.get(name, [])
                if not rows:
                    continue
                print(f'  [{name}] {len(rows)}')
                for row in rows[:12]:
                    print(f'    {row}')
                if len(rows) > 12:
                    print(f'    ... and {len(rows) - 12} more')
    if total > 45 and not args.deep:
        print(f'WARNING: run took {total}s (target 30s or less)')
    if ISSUES:
        sys.exit(1)
    if not args.json:
        print('All GCSE maths verification checks passed.')


if __name__ == '__main__':
    main()
