"""GCSE maths hints after a wrong answer, Phase 1 - run: python scripts/test_gcse_maths_hints_smoke.py

Plan: docs/GCSE_MATHS_HINTS.md. Phase 1 is the key-only diagnosis in generators/shared/misconceptions.py, wired
into POST /api/v1/problems/check for GCSE maths problems bound to the session. This smoke proves:

  rule_sound      every rule's candidate differs from the key and is rejected by the checker, on every real
                  generated question (2 seeds per practice slot), including the parts of multi-part answers
  rule_reachable  every rule fires, unambiguously, on real generated questions (counts printed)
  no_collision    two different messages on one value never produce a message; the same message from two
                  rules does not count as a collision
  unit_table      hand-worked examples per rule (question, key, typed answer, expected rule), written by hand
  negative_control random wrong answers far from every candidate, the key itself, unparseable answers, other
                  subjects, wrong forms and client-supplied keys get no diagnosis
  mutation        each rule's formula perturbed by one unit makes the unit table fail for that rule
  copy_lint       every message passes the system_hint lint (models/zorp_voice.py), plus an independent scan,
                  and none gives the corrected value (D5)
  no_leak         nothing new in a problem, the session, the client payload, set work, a lesson quiz or a
                  stored row; a message is returned only by the check route, after a wrong (or, for the
                  bearing note, a correct) typed answer
  no_drift        diagnosis does not change a problem, draw a random number or import a generator; the D7 dash
                  fix reaches no GCSE-reachable checker string
  coverage        how many practice slots and answer types can produce at least one hint (ratchet)

Options: --deep (40 seeds per slot; by hand), --json (machine-readable summary).
Budget: about 17 s in the default run (Phase 5 added the pair, box and expression rules; it was 12 s).
"""
import argparse
import ast
import collections
import copy
import dataclasses
import json
import os
import random
import re
import sys
import time
import warnings
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('PB_TESTING', '1')
os.environ.setdefault('PB_ALLOW_DEV_SECRET', '1')
os.environ.setdefault('CORS_ORIGINS', 'https://app.example.com')

from generators.shared import answer_checkers as AC  # noqa: E402
from generators.shared import misconceptions as M  # noqa: E402
from generators.shared.answer_checkers import check_answer as _check_answer, problem_answer_form  # noqa: E402
from gcse_verify import harness  # noqa: E402
import gcse_hints_cd as CDT  # noqa: E402 - Phase 5 tables and checks (a helper, not a smoke)

warnings.filterwarnings('ignore', category=SyntaxWarning)
START = time.time()

_CHECKED = {}


def check_answer(answer_type, correct_raw, user_answer, **kw):
    """The checker, remembered for this run (review 2026-10-26: the same candidate is graded many times over, by the
    diagnosis's own acceptance test and by the smoke; about a fifth of the run). The checker is a pure function of its
    arguments; a copy is returned so no caller can change a remembered result."""
    try:
        key = (answer_type, correct_raw, user_answer, tuple(sorted((k, repr(v)) for k, v in kw.items())))
        hash(key)
    except TypeError:
        return _check_answer(answer_type, correct_raw, user_answer, **kw)
    if key not in _CHECKED:
        _CHECKED[key] = _check_answer(answer_type, correct_raw, user_answer, **kw)
    return copy.deepcopy(_CHECKED[key])
SEEDS_DEFAULT = 2
BUDGET_SECONDS = 15.0             # review 2026-10-26: 17 s in the Phase 5 build; about 15 s with the checker remembered
HARD_LIMIT_SECONDS = 24.0          # a loaded machine may be slower than the budget; beyond this something is wrong

# Ratchets: may only rise (measured 2026-10-24, 2 seeds per slot; the default run must keep at least this much).
# The coverage floors are shares of the practice slots, so that retiring redundant slots (docs/GCSE_MATHS_VARIETY.md,
# Phase 1) does not fail them.  Before Phase 1: generic 775 of 1,072 (72.3%), topic 657 (61.3%), either 825 (77.0%).
HINTS_FLOOR_SHARE = 0.720          # practice slots that can produce at least one generic hint
TOPIC_FLOOR_SHARE = 0.600          # practice slots with a topic hint (61.0% after Phase 3 batch C2, 716 of 1173; 61.1% after batch C1 on the default seed pair, 715 of 1171,
                                   # but 60.5% to 61.1% over other seed pairs, so the C1 review kept the floor at 0.600 rather than 0.605; 60.2% after the batch B review; 61.9% after batch A)
COMBINED_FLOOR_SHARE = 0.770       # practice slots with a generic or a topic hint (77.4% after Phase 3 batch C2, 908 of 1173; 77.5% after batch C1; 76.9% after batch B; 77.1% after batch A)
HINTS_FLOOR_TYPES = 7              # answer types that can produce a hint (and the bearing note, counted apart)
EVERY_RULE_FIRES_AT_LEAST = 1

# Facts a message may state (they name the rule of the angle fact or the bearing form, never the answer).
ALLOWED_NUMBERS = {'180', '90', '360', '5', '005'}

ISSUES = collections.defaultdict(list)


def issue(check, where, detail):
    ISSUES[check].append(f'{where}: {detail}')


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def run_diag(problem, at, raw, typed, *, topic='', level='gcse', subject='maths', form=None, result=None):
    """Diagnosis exactly as the route makes it, but through _diagnose so a fault raises instead of hiding."""
    res = result if result is not None else check_answer(at, raw, typed, form=form)
    return M._diagnose(problem, typed, res, at, raw,
                       lambda t: bool(check_answer(at, raw, t, form=form).get('correct')),
                       level, subject, topic, form)


CDT.bind((M, M._topics, M._cd, AC), check_answer, issue, run_diag)


def value_of(at, text):
    """The value a typed example stands for (scalar Fraction, pair of Decimals, or the text for roots)."""
    if at in M.SCALAR_TYPES:
        return M.read_user_scalar(at, text)
    if at in M.PAIR_TYPES:
        return M._user_pair(at, text)
    return text


def corpus(seeds):
    slots = [s for s in harness.enumerate_slots() if s.mode == 'standard']
    out = []
    for s in slots:
        for r in range(seeds):
            p, _ = harness.generate(s, r, record=False)
            out.append((s, r, p))
    return slots, out


def answer_units(problem):
    """[(answer type, key text, where)] a pupil can be diagnosed on: the whole answer, or each part of a multi-part one."""
    at, raw = problem.get('answer_type'), problem.get('correct_answer_raw')
    if raw is None:
        return []
    raw = str(raw)
    if at != 'number_fields':
        return [(at, raw, 'whole')] if at in M.DIAGNOSABLE_TYPES else []
    sep = '\x1e' if '\x1e' in raw else '|'
    types = list(problem.get('answer_field_types') or [])
    out = []
    for i, part in enumerate(raw.split(sep)):
        ft = (types[i] if i < len(types) else None) or 'number'
        if ft in M.DIAGNOSABLE_TYPES:
            out.append((ft, part, f'part {i}'))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# rule_sound, rule_reachable, no_collision, coverage (one pass over real questions)
# ─────────────────────────────────────────────────────────────────────────────

def check_real_questions(seeds):
    slots, items = corpus(seeds)
    applicable = collections.Counter()
    fired = collections.Counter()
    collided = collections.Counter()
    slot_applicable, slot_fired = set(), set()
    type_fired, type_applicable = collections.Counter(), collections.Counter()
    examples = {}
    checks = 0
    for slot, run, problem in items:
        form = problem_answer_form(problem)
        for at, raw, where in answer_units(problem):
            part = where != 'whole'
            uform = None if part else form
            ctx = M.build_ctx(problem, at, raw, slot.slug, uform)
            exs = M.typed_examples(problem, at, raw, slot.slug, uform)
            label = f'{slot.label}#{run} {where}'
            if not exs:
                continue
            slot_applicable.add(slot.label)
            type_applicable[at] += 1
            groups = collections.defaultdict(list)
            topic_vals = set()
            if not part:
                for _rule, c in M.topic_candidates(problem, at, raw, ctx) or ():
                    topic_vals.update((c, M._topic_shown(ctx, c)))
            for rid, typed in exs:
                res = check_answer(at, raw, typed, form=uform)
                checks += 1
                if res.get('correct'):
                    issue('rule_sound', label, f'{rid} candidate {typed!r} is accepted by the checker (key {raw!r})')
                    continue
                val = value_of(at, typed)
                if val is None:
                    issue('rule_sound', label, f'{rid} candidate {typed!r} cannot be read back')
                    continue
                key = ctx.key if at in M.SCALAR_TYPES else (ctx.pair if at in M.PAIR_TYPES else None)
                if key is not None and val == key:
                    issue('rule_sound', label, f'{rid} candidate {typed!r} equals the key {raw!r}')
                    continue
                if at in M.SCALAR_TYPES and ctx.key != 0 and not isinstance(val, Fraction):
                    issue('rule_sound', label, f'{rid} candidate {typed!r} is not a number')
                groups[val if not isinstance(val, list) else tuple(val)].append((rid, typed))
            for val in [v for v in groups if v in topic_vals]:
                del groups[val]                         # decided by the topic rules (precedence tested in the topic section)
            if at in M.PAIR_TYPES and not part:
                # a Phase 5 pair rule that knows the question speaks first (review 2026-10-26: found by --deep)
                accepts = lambda t, at=at, raw=raw: bool(check_answer(at, raw, t).get('correct'))      # noqa: E731
                for val in [v for v, members in groups.items()
                            if M.pair_topic_hits(problem, ctx, members[0][1], accepts)]:
                    del groups[val]
            counted = set()
            for members in groups.values():
                for rid, _ in members:
                    if rid not in counted:
                        counted.add(rid)
                        applicable[rid] += 1
            diagnosed = set()
            for val, members in groups.items():
                messages = {M.RULES_BY_ID[rid].message for rid, _ in members}
                typed = members[0][1]
                if len(messages) == 1:
                    # one diagnosis per rule per question is enough (the six place-value candidates are alike)
                    if members[0][0] in diagnosed:
                        continue
                    diagnosed.add(members[0][0])
                got = run_diag(problem, at, raw, typed, topic=slot.slug, form=uform)
                if len(messages) >= 2:
                    for a in sorted({rid for rid, _ in members}):
                        collided[a] += 1
                    if got is not None:
                        issue('no_collision', label, f'{typed!r} matches {sorted(messages)} but the pupil is shown {got.message!r}')
                    continue
                want = next(iter(messages))
                if got is None:
                    issue('rule_reachable', label, f'{typed!r} (rule {members[0][0]}, key {raw!r}) got no diagnosis')
                    continue
                if got.message != M.MESSAGES[want]:
                    issue('rule_reachable', label, f'{typed!r}: expected {want!r}, got {got.rule_id!r}')
                    continue
                fired[got.rule_id] += 1
                slot_fired.add(slot.label)
                type_fired[at] += 1
                examples.setdefault(got.rule_id, (slot.label, M.plain_text(problem.get('question'))[:90], raw, typed, got.message))
    return {
        'items': items,
        'slots': len(slots), 'questions': len(items), 'checker_calls': checks,
        'applicable': applicable, 'fired': fired, 'collided': collided,
        'slot_applicable': slot_applicable, 'slot_fired': slot_fired,
        'type_fired': type_fired, 'type_applicable': type_applicable, 'examples': examples,
    }


def check_rules_all_fire(res):
    for rule in M.GENERIC_RULES:
        n = res['fired'][rule.id]
        if n < EVERY_RULE_FIRES_AT_LEAST:
            issue('rule_reachable', rule.id, f'fires on {n} generated questions (none: a dead rule or an untested family)')
        share = n / res['applicable'][rule.id] if res['applicable'][rule.id] else 0
        if res['applicable'][rule.id] and share < 0.5:
            issue('rule_reachable', rule.id, f'unambiguous on only {share:.0%} of its candidates (below 50%: review)')
    for rid in M.RULES_BY_ID:
        if M.RULES_BY_ID[rid].message not in M.MESSAGES:
            issue('rule_reachable', rid, 'message id missing from MESSAGES')
    unused = (set(M.MESSAGES) - {r.message for r in M.GENERIC_RULES} - {r.message for r in M.TOPIC_RULES}
              - CDT.used_messages() - {'brg.three_figures'})
    if unused:
        issue('rule_reachable', 'MESSAGES', f'messages no rule uses: {sorted(unused)}')


# ─────────────────────────────────────────────────────────────────────────────
# unit_table: hand-worked examples (not generated). (name, question, type, key, typed, topic, expected rule id)
# ─────────────────────────────────────────────────────────────────────────────

R2DP = 'Give your answer to 2 decimal places.'
R3SF = 'Give your answer to 3 significant figures.'
RWHOLE = 'Give your answer to the nearest whole number.'
R10 = 'Give your answer to the nearest 10.'
STRAIGHT = 'Two angles lie on a straight line. One angle is 41°. Find the other angle.'
COMP = 'Two angles are complementary. One angle is 53°. Find the other angle.'
EXAMPLES = (
    # sign: minus the key
    ('sign, positive typed for a negative key', 'Calculate 2 − 9.', 'number', '-7', '7', 'bidmas', 'gen.sign'),
    ('sign, negative typed for a positive key', 'Calculate 5 + 7.', 'number', '12', '-12', 'bidmas', 'gen.sign'),
    ('sign, fraction key', 'Find the probability.', 'fraction', '-3/5', '3/5', 'algebra', 'gen.sign'),
    ('sign, linear solution with its letter', 'Solve 3x + 6 = 0.', 'linear', 'x = -2', 'x = 2', 'algebra', 'gen.sign'),
    # factors of ten either way
    ('pow10, times 10', 'Calculate 7 × 5.', 'number', '35', '350', 'bidmas', 'gen.pow10'),
    ('pow10, times 1000', 'Calculate 7 × 5.', 'number', '35', '35000', 'bidmas', 'gen.pow10'),
    ('pow10, divide by 10', 'Calculate 7 × 5.', 'number', '35', '3.5', 'bidmas', 'gen.pow10'),
    ('pow10, divide by 100', 'Calculate 7 × 5.', 'number', '35', '0.35', 'bidmas', 'gen.pow10'),
    ('pow10, divide by 1000', 'Calculate 7 × 5.', 'number', '35', '0.035', 'bidmas', 'gen.pow10'),
    ('pow10, rounded as told (3.57 / 10 = 0.357)', 'Convert it. ' + R2DP, 'number', '3.57', '0.36', 'compound_measures', 'gen.pow10'),
    ('pow10, rounding that changes the value a lot is not matched (0.0357 -> 0.04)', 'Convert it. ' + R2DP, 'number', '3.57',
     '0.04', 'compound_measures', None),
    ('pow10, a percentage typed as a decimal is a form slip', 'Write 0.6 as a percentage.', 'number', '60', '0.6', 'fdp',
     'gen.as_percentage'),
    ('pow10, percentage change typed as a decimal', 'The value changes from 158 to 221.2. Find the percentage increase.',
     'number', '40', '0.4', 'fdp', 'gen.as_percentage'),
    ('pow10, percentage times 10 is still place value', 'Write 0.6 as a percentage.', 'number', '60', '600', 'fdp',
     'gen.pow10'),
    ('pow10, a decimal typed as the percentage is a form slip', 'Write 36% as a decimal.', 'number', '0.36', '36', 'fdp',
     'gen.as_decimal'),
    ('pow10, decimal from a percentage, times 10', 'Write 36% as a decimal.', 'number', '0.36', '3.6', 'fdp', 'gen.pow10'),
    ('pow10, "percentage" in a question that does not ask for one', 'Find 20% of 230.', 'number', '46', '0.46', 'number',
     'gen.pow10'),
    ('pow10, pi multiple', 'Find the area in terms of pi.', 'pi_multiple', '16', '160', 'mensuration', 'gen.pow10'),
    ('pow10, not on a plain 3 against 5', 'Calculate 7 × 5.', 'number', '35', '36', 'bidmas', None),
    # wrong accuracy: coarser than asked
    ('accuracy, one place short', 'Find x. ' + R2DP, 'number', '5.67', '5.7', 'trigonometry', 'gen.accuracy_coarser'),
    ('accuracy, two places short', 'Find x. ' + R2DP, 'number', '5.67', '6', 'trigonometry', 'gen.accuracy_coarser'),
    ('accuracy, one figure', 'Find x. ' + R3SF, 'number', '0.0451', '0.05', 'trigonometry', 'gen.accuracy_coarser'),
    # wrong accuracy: not rounded (any value that rounds to the key)
    ('accuracy, not rounded', 'Find x. ' + R2DP, 'number', '5.67', '5.667', 'trigonometry', 'gen.accuracy_finer'),
    ('accuracy, not rounded, long', 'Find x. ' + R2DP, 'number', '5.67', '5.6704', 'trigonometry', 'gen.accuracy_finer'),
    ('accuracy, half rounds up to the key (5.665 -> 5.67)', 'Find x. ' + R2DP, 'number', '5.67', '5.665', 'trigonometry', 'gen.accuracy_finer'),
    ('accuracy, 5.675 rounds up to 5.68, not the key', 'Find x. ' + R2DP, 'number', '5.67', '5.675', 'trigonometry', None),
    ('accuracy, significant figures not rounded', 'Find x. ' + R3SF, 'number', '0.0451', '0.04512', 'trigonometry', 'gen.accuracy_finer'),
    ('accuracy, a fraction that rounds to the key', 'Find x. ' + R2DP, 'number', '0.33', '1/3', 'decimals', 'gen.accuracy_finer'),
    ('accuracy, no accuracy stated means no accuracy hint', 'Find x.', 'number', '5.67', '5.7', 'trigonometry', None),
    # one step from the key in the last place: in a calculation (either direction, one message) ...
    ('last place, calculation, 2.47 -> 2.46', 'Find x. ' + R2DP, 'number', '2.47', '2.46', 'trigonometry', 'gen.early_round'),
    ('last place, calculation, 2.47 -> 2.48', 'Find x. ' + R2DP, 'number', '2.47', '2.48', 'trigonometry', 'gen.early_round'),
    ('last place, negative key, toward zero', 'Find x. ' + R2DP, 'number', '-2.47', '-2.46', 'trigonometry', 'gen.early_round'),
    ('last place, negative key, away from zero', 'Find x. ' + R2DP, 'number', '-2.47', '-2.48', 'trigonometry', 'gen.early_round'),
    ('last place, nearest whole number, below', 'Find the cost. ' + RWHOLE, 'number', '15', '14', 'compound_measures', 'gen.early_round'),
    ('last place, nearest whole number, above', 'Find the cost. ' + RWHOLE, 'number', '15', '16', 'compound_measures', 'gen.early_round'),
    ('last place, nearest 10', 'Work it out. ' + R10, 'number', '340', '330', 'number', 'gen.early_round'),
    ('last place, 3 s.f. (0.0451 -> 0.0450 typed 0.045)', 'Find x. ' + R3SF, 'number', '0.0451', '0.045', 'trigonometry', 'gen.early_round'),
    ('last place, 3 s.f. below a power of ten (1000 -> 999)', 'Find x. ' + R3SF, 'number', '1000', '999', 'trigonometry', 'gen.early_round'),
    ('last place, 3 s.f.: 990 is not the step below 1000', 'Find x. ' + R3SF, 'number', '1000', '990', 'trigonometry', None),
    # ... and in a task that only asks to round (rounded the wrong way, either direction)
    ('rounding task, rounded down instead of up', 'Round 2.4689 to 2 decimal places.', 'number', '2.47', '2.46', 'number', 'gen.truncated'),
    ('rounding task, rounded up instead of down', 'Round 5304 to the nearest 10.', 'number', '5300', '5310', 'number', 'gen.truncated'),
    ('rounding task, significant figures', 'Round 76243 to 1 significant figure.', 'number', '80000', '70000', 'number', 'gen.truncated'),
    ('rounding task, the number not rounded', 'Round 20.984 to 2 decimal places.', 'number', '20.98', '20.984', 'number', 'gen.accuracy_finer'),
    ('a value read off a graph gets no rounding advice', 'Estimate the median from the cumulative frequency graph, correct to 1 decimal place.',
     'number', '54', '53.9', 'statistics', None),
    ('one step off with no accuracy stated is not a rounding slip', 'Find x.', 'number', '2.47', '2.46', 'trigonometry', None),
    ('estimate: the accuracy is for the numbers in the question', 'Estimate 2.7 × 3.8 by rounding each number to the nearest whole number.',
     'number', '12', '11', 'decimals', None),
    # inverted division
    ('reciprocal, integer key', 'Find the ratio as a number.', 'number', '4', '0.25', 'ratio_proportion', 'gen.reciprocal'),
    ('reciprocal typed as a fraction', 'Find the ratio as a number.', 'number', '4', '1/4', 'ratio_proportion', 'gen.reciprocal'),
    ('reciprocal, decimal key', 'Find the speed.', 'number', '0.8', '1.25', 'compound_measures', 'gen.reciprocal'),
    ('reciprocal, rounded as told (1/7.4 = 0.135...)', 'Find the rate. ' + R2DP, 'number', '7.4', '0.14', 'compound_measures', 'gen.reciprocal'),
    ('reciprocal, linear equation solved the other way round', 'Solve 2x = 6.', 'linear', 'x = 3', 'x = 1/3', 'algebra',
     'gen.reciprocal'),
    ('reciprocal needs a division in the question', 'Calculate 6 + 2 × 1.', 'number', '8', '0.125', 'bidmas', None),
    ('reciprocal of a fraction answer', 'Write 0.6 as a fraction in its simplest form.', 'fraction', '3/5', '5/3', 'fdp', 'gen.reciprocal_fraction'),
    ('reciprocal, number key written as a fraction', 'Find the probability.', 'number', '1/6', '6', 'probability', 'gen.reciprocal_fraction'),
    ('key 1 has no reciprocal slip', 'Find x.', 'number', '1', '1.0', 'bidmas', None),
    # swapped pair
    ('pair, number pair', 'Solve the simultaneous equations.', 'number_pair', '3|-2', '-2|3', 'simultaneous_equations', 'gen.pair_swapped'),
    ('pair, HCF and LCM', 'Find the HCF and LCM.', 'number_pair', '6|396', '396|6', 'multiples_factors', 'gen.pair_swapped'),
    ('pair, vector components', 'Find the vector.', 'vector', '-2|3', '3, -2', 'vectors', 'gen.pair_swapped'),
    ('pair, one value right is not a swap', 'Solve.', 'number_pair', '3|-2', '3|2', 'simultaneous_equations', None),
    ('pair, equal values cannot be swapped', 'Solve.', 'number_pair', '4|4', '4|5', 'simultaneous_equations', None),
    # one root only
    ('roots, first root only', 'Solve x^2 + 7x + 12 = 0.', 'quadratic_roots', '-4,-3', '-4', 'algebra', 'gen.one_root'),
    ('roots, second root only', 'Solve x^2 + 7x + 12 = 0.', 'quadratic_roots', '-4,-3', '-3', 'algebra', 'gen.one_root'),
    ('roots, one root typed twice', 'Solve x^2 + 7x + 12 = 0.', 'quadratic_roots', '-4,-3', '-4, -4', 'algebra', 'gen.one_root'),
    ('roots, a single value that is not a root', 'Solve x^2 + 7x + 12 = 0.', 'quadratic_roots', '-4,-3', '3', 'algebra', None),
    ('roots, one right and one not', 'Solve x^2 + 7x + 12 = 0.', 'quadratic_roots', '-4,-3', '-4, 3', 'algebra', None),
    ('roots, a repeated root has no second solution', 'Solve x^2 + 6x + 9 = 0.', 'quadratic_roots', '-3,-3', '-3, 3', 'algebra', None),
    # angles
    ('angle, 180 minus (the given angle on a straight line)', STRAIGHT, 'number', '139', '41', 'geometry_angles', 'ang.supplement'),
    ('angle, 180 minus the key', COMP, 'number', '37', '143', 'geometry_angles', 'ang.supplement'),
    ('angle, 90 minus the key', COMP, 'number', '37', '53', 'geometry_angles', 'ang.complement'),
    ('angle, circle theorems topic', 'Find angle ABC.', 'number', '70', '110', 'circle_theorems', 'ang.supplement'),
    ('angle rules need an angle topic', STRAIGHT, 'number', '139', '41', 'bidmas', None),
    ('angle rules need an angle answer (a length)', 'A tangent touches the circle at A. Find the length AT.', 'number', '4', '176',
     'geometry_angles', None),
    ('angle rules need an angle answer (a count)', 'A regular polygon has an interior angle of 120°. Find the number of sides.',
     'number', '6', '174', 'geometry_angles', None),
    ('angle rules need an angle answer (solve for x)', 'The angles are (3x + 13)° and (2x + 12)°. Find x and each angle.',
     'number', '16', '164', 'geometry_angles', None),
    ('angle key of 90 has no 90 minus slip', 'Find the angle.', 'number', '90', '90.5', 'geometry_angles', None),
    ('angle key over 180 has no 180 minus slip', 'Find the reflex angle.', 'number', '250', '-70', 'geometry_angles', None),
    # a collision between different messages gives no message
    ('collision: 0.1 is 10 / 100 and 1 / 10', 'Find the speed.', 'number', '10', '0.1', 'compound_measures', None),
    ('collision: 10 is 0.1 x 100 and 1 / 0.1', 'Find the speed.', 'number', '0.1', '10', 'compound_measures', None),
    ('no division in the question: 0.1 is place value only', 'Find x.', 'number', '10', '0.1', 'bidmas', 'gen.pow10'),
) + CDT.GENERIC_EXAMPLES

# Shapes the table cannot express: (name, callable returning True when right).
def other_cases():
    out = []

    def case(name, ok):
        out.append((name, ok))

    q = {'question': 'Find x.'}
    # the checker's own message stays when the answer is not a number
    for typed in ('abc', '5 cm', '1/0', '1//2', '5/', '', '   '):
        res = check_answer('number', '35', typed)
        case(f'unparseable {typed!r} gets no diagnosis', run_diag(q, 'number', '35', typed, result=res) is None)
    # the key itself: correct, no misconception
    for at, raw in (('number', '35'), ('fraction', '3/5'), ('number_pair', '3|-2'), ('quadratic_roots', '-4,-3'),
                    ('vector', '-2|3'), ('linear', 'x = 4')):
        res = check_answer(at, raw, raw)
        case(f'the key {raw!r} ({at}) gets no diagnosis', res['correct'] and run_diag(q, at, raw, raw, result=res) is None)
    # other subjects and levels
    case('physics is never diagnosed', run_diag(q, 'number', '35', '350', subject='physics') is None)
    case('a-level maths is never diagnosed', run_diag(q, 'number', '35', '350', level='alevel') is None)
    # a result the checker gave its own message to
    res = check_answer('number', '35', '350')
    for extra in ({'wrong_form': 'expanded'}, {'wrong_letter': True}):
        case(f'a result with {list(extra)[0]} keeps its own message',
             run_diag(q, 'number', '35', '350', result={**res, **extra}) is None)
    res = check_answer('fraction', '1/3', '0.33', form='probability')
    case('the recurring-decimal message is kept', res['feedback'] == AC._RECURRING_FEEDBACK
         and run_diag(q, 'fraction', '1/3', '0.33', form='probability', result=res) is None)
    # types without rules
    for at, raw, typed in (('algebraic', '3x + 2', '2x + 3'), ('keyword', 'yes', 'no'), ('number_fields', '1|2', '2|1'),
                           ('standard_form', '9.6|4', '9.6|5'), ('surd', '3|2', '2|3')):
        case(f'{at} has no Phase 1 rule', run_diag(q, at, raw, typed) is None)
    # bearing: a note on a correct answer without the leading zero, nothing on a wrong one
    bq = {'question': 'Find the bearing.'}
    note = run_diag(bq, 'bearing', '45', '45', topic='bearings')
    case('bearing 45 typed for 045 gets the three-figure note', note is not None and note.kind == 'note'
         and note.rule_id == 'brg.three_figures')
    case('bearing 7 typed for 007 gets the note', (run_diag(bq, 'bearing', '7', '7', topic='bearings') or M.Diagnosis('', '', '')).kind == 'note')
    case('bearing typed with a degree sign gets the note', (run_diag(bq, 'bearing', '45', '45°', topic='bearings') or M.Diagnosis('', '', '')).kind == 'note')
    case('bearing 045 typed in full gets no note', run_diag(bq, 'bearing', '45', '045', topic='bearings') is None)
    case('bearing 245 needs no zero', run_diag(bq, 'bearing', '245', '245', topic='bearings') is None)
    case('a wrong bearing gets no diagnosis', run_diag(bq, 'bearing', '45', '46', topic='bearings') is None)
    case('bearing 405 (out of range) is wrong and gets no note or hint',
         all(run_diag(bq, 'bearing', '45', t, topic='bearings') is None for t in ('405', '-315', '765')))
    case('bearing 405 is marked wrong with the range message',
         check_answer('bearing', '45', '405')['correct'] is False
         and check_answer('bearing', '45', '405')['feedback'] == 'Bearings are between 000\u00b0 and 360\u00b0. Check your angle.')
    case('bearing 360 for 000 is correct and needs no three-figure note', run_diag(bq, 'bearing', '000', '360', topic='bearings') is None)
    # a part of a multi-part answer is an angle only when its label carries a degree sign
    mp = {'question': 'Two angles on a straight line are (4x + 10)° and (2x + 44)°. Find x and each angle.',
          'answer_type': 'number_fields', 'correct_answer_raw': '21|94|86',
          'answer_labels': ['x', 'First angle (°)', 'Second angle (°)']}
    d = run_diag(mp, 'number', '94', '86', topic='geometry_angles')
    case('a part labelled in degrees gets the angle hint', d is not None and d.rule_id == 'ang.supplement')
    case('the part labelled x gets no angle hint', run_diag(mp, 'number', '21', '159', topic='geometry_angles') is None)
    mp_str = dict(mp, answer_labels=str(mp['answer_labels']))
    d = run_diag(mp_str, 'number', '94', '86', topic='geometry_angles')
    case('labels stored as text are read too', d is not None and d.rule_id == 'ang.supplement')
    case('a bearing part gets no angle hint', run_diag(
        {'question': 'Find the bearing and the angle.', 'answer_type': 'number_fields', 'correct_answer_raw': '125|89',
         'answer_labels': ['(a) Bearing B to C (°)', '(b) Angle ABC (°)']}, 'number', '125', '55', topic='geometry_angles') is None)
    # many roots: no diagnosis, and no SymPy work beyond the checker's own
    bomb = ', '.join(['3'] * 600)
    t0 = time.time()
    res = {'correct': False, 'feedback': 'Enter 2 roots.'}
    case('600 roots get no diagnosis', run_diag(q, 'quadratic_roots', '-4,-3', bomb, result=res) is None)
    case('600 roots are rejected before any SymPy work', time.time() - t0 < 0.05)
    # the public entry point never raises
    def boom(_text):
        raise RuntimeError('checker fault')
    res = check_answer('number', '35', '350')
    case('diagnose() swallows a fault', M.diagnose(q, '350', res, answer_type='number', correct_raw='35', accepts=boom,
                                                    level='gcse', subject='maths') is None)
    case('diagnose() on junk input returns None', M.diagnose(None, None, None, answer_type='number', correct_raw=None,
                                                             accepts=boom, level='gcse', subject='maths') is None)
    # an answer the checker marked right is never diagnosed, even when it equals a candidate (a tolerant checker)
    marked_right = {'correct': True, 'normalized_user': '350', 'normalized_correct': '35', 'feedback': 'Correct!'}
    case('an answer marked right gets no misconception', run_diag(q, 'number', '35', '350', result=marked_right) is None)
    # a candidate the checker accepts is never a slip (the guard in the route)
    case('a candidate the checker accepts is dropped',
         M._diagnose(q, '350', check_answer('number', '35', '350'), 'number', '35', lambda t: True, 'gcse', 'maths', '', None) is None)
    # two rules with the same message on one value are not a collision
    saved = M.GENERIC_RULES
    twin = dataclasses.replace(M.RULES_BY_ID['gen.sign'], id='test.sign_twin')
    M.GENERIC_RULES = saved + (twin,)
    try:
        d = run_diag(q, 'number', '35', '-35')
        case('two rules, one message: shown', d is not None and d.message == M.MESSAGES['gen.sign'])
        other = dataclasses.replace(M.RULES_BY_ID['gen.sign'], id='test.other', message='gen.pow10')
        M.GENERIC_RULES = saved + (other,)
        case('two rules, two messages on one value: none', run_diag(q, 'number', '35', '-35') is None)
    finally:
        M.GENERIC_RULES = saved
    return out


def run_unit_table():
    """Run the hand-worked table. Returns the list of failing case names (with what was seen)."""
    failed = []
    for name, question, at, key, typed, topic, want in EXAMPLES:
        problem = {'question': question}
        got = run_diag(problem, at, key, typed, topic=topic)
        got_id = got.rule_id if got else None
        if got_id != want:
            failed.append(f'{name}: key {key!r}, typed {typed!r}: expected {want!r}, got {got_id!r}')
        elif got and got.message != M.MESSAGES[M.RULES_BY_ID[want].message]:
            failed.append(f'{name}: wrong message text')
    for name, ok in other_cases():
        if not ok:
            failed.append(name)
    return failed


def check_unit_table():
    for line in run_unit_table():
        issue('unit_table', 'table', line)
    covered = {e[6] for e in EXAMPLES if e[6]}
    for rule in M.GENERIC_RULES:
        if rule.id not in covered:
            issue('unit_table', rule.id, 'has no hand-worked example')


# ─────────────────────────────────────────────────────────────────────────────
# mutation: perturb each rule by one unit, the table must notice
# ─────────────────────────────────────────────────────────────────────────────

def mutant_of(rule):
    orig = rule.candidates
    if rule.kind == 'scalar':
        def cands(ctx, o=orig):
            return [c + 1 for c in o(ctx)]
    elif rule.kind == 'pair':
        def cands(ctx, o=orig):
            return [(b + 1, a) for a, b in o(ctx)]
    elif rule.kind == 'roots_set':
        def cands(ctx, o=orig):
            return [tuple(r + 1 for r in roots) for roots in o(ctx)]
    else:
        def cands(ctx, o=orig):
            return [r + 1 for r in o(ctx)]
    region = None
    if rule.region is not None:
        def region(ctx, p, o=rule.region):
            return not o(ctx, p)
    return dataclasses.replace(rule, candidates=cands, region=region)


def check_mutation():
    saved = M.GENERIC_RULES
    survivors = []
    try:
        for rule in saved:
            M.GENERIC_RULES = tuple(mutant_of(r) if r is rule else r for r in saved)
            if not run_unit_table():
                survivors.append(rule.id)
    finally:
        M.GENERIC_RULES = saved
    for rid in survivors:
        issue('mutation', rid, 'a rule whose formula is off by one unit still passes the unit table')
    return len(saved) - len(survivors), len(saved)


# ─────────────────────────────────────────────────────────────────────────────
# negative_control on real questions
# ─────────────────────────────────────────────────────────────────────────────

def check_negative_control(items):
    rng = random.Random(20261024)
    far = right = 0
    for slot, run, problem in items:
        for at, raw, where in answer_units(problem):
            if at not in M.SCALAR_TYPES:
                continue
            part = where != 'whole'
            form = None if part else problem_answer_form(problem)
            ctx = M.build_ctx(problem, at, raw, slot.slug, form)
            if ctx is None:
                continue
            res = check_answer(at, raw, raw, form=form)
            if res.get('correct') and run_diag(problem, at, raw, raw, topic=slot.slug, form=form, result=res) is not None:
                issue('negative_control', f'{slot.label}#{run}', f'the key {raw!r} was diagnosed')
            right += 1
            cand_values = {M.read_user_scalar(at, t) for _, t in M.typed_examples(problem, at, raw, slot.slug, form)}
            # Phase 3 batch B: the topic rules' candidates count as well (the generic ones alone let a far value land on
            # one by chance: 18 = 7 + 11 for a rectangle area of 77, once the slot list shifted the seeded draws)
            cand_values |= {Fraction(v) for _, v in (M.topic_candidates(problem, at, raw, ctx) or [])}
            for _ in range(3):
                v = ctx.key + Fraction(rng.randint(37, 997), rng.choice((3, 7, 11))) * rng.choice((1, -1))
                typed = M.format_answer(v)
                if M.read_user_scalar(at, typed) in cand_values:
                    continue
                if ctx.spec and abs(v - ctx.key) <= 2 * M.grid_unit(ctx.spec, ctx.key):
                    continue            # a value that rounds to the key is the accuracy slip, not a far answer
                got = run_diag(problem, at, raw, typed, topic=slot.slug, form=form)
                far += 1
                if got is not None:
                    issue('negative_control', f'{slot.label}#{run}',
                          f'{typed!r} (key {raw!r}, far from every candidate) was diagnosed as {got.rule_id}')
    return far, right


def check_near_key(items):
    """Whole-change review 2026-11-03 (F1, F2, F9): values next to the key on real questions with an answer record (one
    either side of a whole-number key; a key that is not whole rounded or cut to no and to one decimal place) never get
    a topic message by rounding a slip to the pupil's places. A topic rule may speak there only at its exact slip value,
    and on the key written short only when its slip is that by nature (M.CUT_SHORT_RULES). Returns the values typed."""
    typed_n = 0
    for slot, run, problem in items:
        if not isinstance(problem.get('answer_record'), dict) or problem.get('options'):
            continue
        for at, raw, where in answer_units(problem):
            if at not in M.SCALAR_TYPES:
                continue
            part = int(where.split()[1]) if where != 'whole' else None
            form = None if part is not None else problem_answer_form(problem)
            key = M.read_key(at, raw)
            ctx = M.build_ctx(problem, at, raw, slot.slug, form)
            if key is None or ctx is None:
                continue
            # the key written short: rounded or cut to no or one decimal place, where that keeps a digit of it (not 0 or 1
            # for 0.5)
            short = set()
            for places in (0, 1) if key.denominator != 1 else ():
                unit = Fraction(1, 10 ** places)
                if unit <= abs(key):
                    scaled = abs(key) / unit
                    cut = Fraction(scaled.numerator // scaled.denominator)
                    up = cut + (1 if scaled - cut >= Fraction(1, 2) else 0)
                    short |= {(1 if key > 0 else -1) * cut * unit, (1 if key > 0 else -1) * up * unit}
            short.discard(key)
            for v in sorted(CDT.near_key_values(key)):
                typed = M.format_answer(v)
                res = check_answer(at, raw, typed, form=form)
                if res.get('correct'):
                    continue
                typed_n += 1
                got = M._diagnose(problem, typed, res, at, raw, lambda t: bool(check_answer(at, raw, t, form=form).get('correct')),
                                  'gcse', 'maths', slot.slug, form, part=part)
                if got is None or got.rule_id in M.RULES_BY_ID:
                    continue             # silence, or a generic line (early rounding, accuracy)
                if part is None:
                    exact = {Fraction(c) for _, c in (M.topic_candidates(problem, at, raw, ctx) or [])}
                else:
                    found = M.part_topic(problem, part, at, raw, slot.slug, form)
                    exact = {Fraction(c) for _, c in (found[1] if found else [])}
                read = M.read_user_scalar(at, typed, form)
                if read not in exact:
                    issue('negative_control', f'{slot.label}#{run} {where}',
                          f'{typed!r} next to the key {raw!r} was named {got.rule_id} by rounding a slip to the pupil\'s places')
                elif v in short and ctx.spec is None and got.rule_id not in M.CUT_SHORT_RULES:
                    issue('negative_control', f'{slot.label}#{run} {where}',
                          f'{typed!r} is the key {raw!r} written short, but was named {got.rule_id}')
    return typed_n


# ─────────────────────────────────────────────────────────────────────────────
# copy_lint
# ─────────────────────────────────────────────────────────────────────────────

def check_copy(res):
    from models import zorp_voice
    items, errors = zorp_voice.extract()
    for e in errors:
        issue('copy_lint', 'extract', e)
    hints = [i for i in items if i.surface == 'system_hint']
    # MESSAGES plus, from Phase 3, the rung 1 nudges and the ladder words (prefixed 'nudge:' and 'ladder:')
    from generators.shared import mcq_notes
    wanted = set(M.MESSAGES) | {'nudge:' + k for k in M.NUDGES} | {'ladder:' + k for k in M.LADDER_COPY}
    wanted |= {'note:' + k for k in list(mcq_notes.NOTES) + list(mcq_notes.BANK_NOTES)}      # Phase 4: distractor notes
    wanted.add('nudge:default')          # whole-change review 2026-11-03 (F10): NUDGE_DEFAULT, the last rung 1 line
    if {i.where for i in hints} != wanted:
        issue('copy_lint', 'extract', 'the voice lint does not read every message in MESSAGES, NUDGES, LADDER_COPY and the distractor notes')
    for v in zorp_voice.lint(hints):
        if v.level in ('error', 'warn'):
            issue('copy_lint', v.item.where, f'{v.rule}: {v.detail}')
    # an independent scan that does not use the lint code
    banned = r"\b(wrong|incorrect|mistakes?|careless|silly|just|easy|simply|obviously|failed|you forgot)\b"
    for mid, text in M.MESSAGES.items():
        if len(text) > 120:
            issue('copy_lint', mid, f'{len(text)} characters')
        if re.search('[–—]|\\s-\\s', text) or re.search('[\U0001F000-\U0001FAFF☀-➿⭐️]', text):
            issue('copy_lint', mid, 'dash or emoji')
        if text.count('!') > 1:
            issue('copy_lint', mid, 'more than one exclamation mark')
        if len(re.findall(r'[.!?](?:\s|$)', text)) > 2:
            issue('copy_lint', mid, 'more than two sentences')
        if re.search(banned, text, re.I):
            issue('copy_lint', mid, 'unkind or banned word')
        if re.search(r'\b(I|my|me)\b', text):
            issue('copy_lint', mid, 'first person (system voice)')
        if re.search(r'\b(color|center|analyze|math)\b', text, re.I):
            issue('copy_lint', mid, 'US spelling')
        if '{' in text or '}' in text:
            issue('copy_lint', mid, 'a placeholder (Phase 1 messages are fixed text)')
        for num in re.findall(r'\d+', text):
            if num not in ALLOWED_NUMBERS:
                issue('copy_lint', mid, f'the number {num} (D5: a message names the slip, never a value)')
    # D5: no fired message contains the key or the typed value of the question it was shown for
    for rid, (label, q, raw, typed, msg) in res['examples'].items():
        for token in {str(raw).strip(), typed.strip()}:
            if token and token not in ALLOWED_NUMBERS and re.search(rf'(?<![\w.]){re.escape(token)}(?![\w.])', msg):
                issue('copy_lint', rid, f'the message contains {token!r} from {label}')


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: topic rules from the recorded inputs
# ─────────────────────────────────────────────────────────────────────────────

from generators.shared import answer_record as AR  # noqa: E402
from generators.shared import misconception_topics as T  # noqa: E402

R1DP = 'Give your answer to 1 decimal place.'
Q = 'Work out the answer.'


def topic_problem(family, inputs, at, key, question=Q):
    """A session problem as the app holds it: the question, the key, and the answer record."""
    return {'question': question, 'answer_type': at, 'correct_answer_raw': key,
            'answer_record': {'f': family, 'i': inputs}}


def run_topic(problem, typed, topic='', *, accepts=None):
    at, raw = problem['answer_type'], problem['correct_answer_raw']
    res = check_answer(at, raw, typed)
    if accepts is None:
        return run_diag(problem, at, raw, typed, topic=topic, result=res)
    return M._diagnose(problem, typed, res, at, raw, accepts, 'gcse', 'maths', topic, None)


# Hand-worked examples, one or more per topic rule, the numbers worked by hand and not by the rule code.
# (rule id, family, recorded inputs, answer type, key, typed answer(s) that must get that rule's message, question)
# pi_multiple keys are the coefficient of pi, so the arithmetic is by hand; the accuracy is in the question otherwise.
TX = (
    # ---- mensuration ----
    ('mens.area_uses_circumference', 'mens_circle_area', {'r': 3}, 'pi_multiple', '9', '6', Q),
    ('mens.area_not_squared', 'mens_circle_area', {'r': 3}, 'pi_multiple', '9', '3', Q),
    ('mens.circumference_uses_area', 'mens_circumference', {'r': 3}, 'pi_multiple', '6', '9', Q),
    ('mens.circumference_pi_r', 'mens_circumference', {'r': 3}, 'pi_multiple', '6', '3', Q),
    ('mens.circumference_of_diameter_doubled', 'mens_circumference', {'r': 3}, 'pi_multiple', '6', '12', Q),
    ('mens.sector_whole_circle', 'mens_sector_area', {'r': 6, 'angle': 60}, 'pi_multiple', '6', '36', Q),
    ('mens.sector_uses_arc', 'mens_sector_area', {'r': 6, 'angle': 60}, 'pi_multiple', '6', '2', Q),
    ('mens.arc_whole_circle', 'mens_arc', {'r': 6, 'angle': 60}, 'pi_multiple', '2', '12', Q),
    ('mens.arc_whole_circle', 'mens_arc_exact', {'r': 6, 'angle': 60}, 'pi_multiple', '2', '12', Q),
    ('mens.arc_uses_sector', 'mens_arc', {'r': 6, 'angle': 60}, 'pi_multiple', '2', '6', Q),
    ('mens.sector_perimeter_arc_only', 'mens_sector_perimeter', {'r': 6, 'angle': 60}, 'pi_multiple', '14', '2', Q),
    ('mens.cylinder_volume_not_squared', 'mens_cyl_vol', {'r': 3, 'h': 5}, 'pi_multiple', '45', '15', Q),
    ('mens.cylinder_volume_not_squared', 'mens_exact_pi_cyl', {'r': 3, 'h': 5}, 'pi_multiple', '45', '15', Q),
    ('mens.cylinder_volume_is_area', 'mens_cyl_vol', {'r': 3, 'h': 5}, 'pi_multiple', '45', '48', Q),
    ('mens.cylinder_area_curved_only', 'mens_cyl_sa', {'r': 3, 'h': 5}, 'pi_multiple', '48', '30', Q),
    ('mens.cylinder_area_is_volume', 'mens_cyl_sa', {'r': 3, 'h': 5}, 'pi_multiple', '48', '45', Q),
    ('mens.cone_area_curved_only', 'mens_cone_sa_slant', {'r': 3, 'slant': 5}, 'pi_multiple', '24', '15', Q),
    ('mens.cone_volume_no_third', 'mens_cone_vol', {'r': 3, 'h': 4}, 'pi_multiple', '12', '36', Q),
    ('mens.pyramid_volume_no_third', 'mens_pyramid_vol', {'l': 3, 'w': 4, 'h': 5}, 'number', '20', '60', Q),
    ('mens.cone_volume_slant_as_height', 'mens_cone_vol_from_slant', {'r': 3, 'slant': 5}, 'pi_multiple', '12', '15', Q),
    ('mens.cone_area_height_as_slant', 'mens_cone_sa_height', {'r': 3, 'h': 4}, 'pi_multiple', '24', '21', Q),
    ('mens.sphere_area_is_volume', 'mens_sphere_sa', {'r': 6}, 'pi_multiple', '144', '288', Q),
    ('mens.sphere_volume_is_area', 'mens_sphere_vol', {'r': 6}, 'pi_multiple', '288', '144', Q),
    ('mens.sphere_volume_not_cubed', 'mens_sphere_vol', {'r': 6}, 'pi_multiple', '288', '48', Q),
    ('mens.sphere_volume_not_cubed', 'cm_sphere_mass', {'r': 6, 'density': 2}, 'pi_multiple', '576', '96', Q),
    ('mens.triangle_full_rectangle', 'mens_tri_area', {'b': 6, 'h': 4}, 'number', '12', '24', Q),
    ('mens.trapezium_full_rectangle', 'mens_trapezium', {'a': 3, 'b': 5, 'h': 4}, 'number', '16', '32', Q),
    ('mens.prism_full_rectangle', 'mens_tri_prism_vol', {'b': 3, 'h': 4, 'length': 5}, 'number', '30', '60', Q),
    ('mens.cuboid_volume_is_area', 'mens_cuboid_vol', {'l': 2, 'w': 3, 'h': 4}, 'number', '24', '52', Q),
    ('mens.cuboid_area_is_volume', 'mens_cuboid_sa', {'l': 2, 'w': 3, 'h': 4}, 'number', '52', '24', Q),
    ('mens.cuboid_area_faces_missed', 'mens_cuboid_sa', {'l': 2, 'w': 3, 'h': 4}, 'number', '52', '26', Q),
    ('mens.rectangle_perimeter_is_area', 'mens_rect_perimeter', {'l': 5, 'w': 3}, 'number', '16', '15', Q),
    ('mens.rectangle_perimeter_half', 'mens_rect_perimeter', {'l': 5, 'w': 3}, 'number', '16', '8', Q),
    ('mens.l_shape_added', 'mens_l_shape', {'a': 8, 'b': 3, 'c': 6, 'd': 2}, 'number', '42', '54', Q),
    ('mens.annulus_squared_difference', 'mens_annulus', {'R': 5, 'r': 3}, 'pi_multiple', '16', '4', Q),
    ('mens.annulus_outer_only', 'mens_annulus', {'R': 5, 'r': 3}, 'pi_multiple', '16', '25', Q),
    ('mens.pipe_squared_difference', 'cm_hollow_cyl_mass', {'R': 5, 'r': 3, 'h': 10, 'density': 2}, 'pi_multiple', '320', '80', Q),
    ('mens.pipe_solid', 'cm_hollow_cyl_mass', {'R': 5, 'r': 3, 'h': 10, 'density': 2}, 'pi_multiple', '320', '500', Q),
    ('mens.diameter_found_for_radius', 'mens_radius_from_area', {'area': 50.3}, 'number', '4', '8', 'Find the radius. ' + R1DP),
    ('mens.radius_found_for_diameter', 'mens_diameter', {'circ': 31.4}, 'number', '10', '5', 'Find the diameter. ' + R1DP),
    ('mens.radius_squared_not_rooted', 'mens_radius_from_area', {'area': 50.3}, 'number', '4', '16', 'Find the radius. ' + R1DP),
    ('mens.height_from_volume_not_squared', 'mens_cyl_height', {'vol': 141.4, 'r': 3}, 'number', '5', '15', 'Find the height. ' + R1DP),
    ('mens.area_units_squared', 'mens_cm2_to_m2', {'l': 200, 'w': 300}, 'number', '6', '600', Q),
    ('mens.area_units_not_converted', 'mens_cm2_to_m2', {'l': 200, 'w': 300}, 'number', '6', '60000', Q),
    ('mens.litres_not_converted', 'mens_fill_time', {'r': 10, 'h': 20, 'rate': 2}, 'number', '3.14', '3140', 'How long? ' + R3SF),
    ('mens.similar_power', 'mens_similar', {'k': 2, 'value': 5, 'power': 2}, 'number', '20', ('10', '40'), Q),
    ('mens.similar_power', 'mens_similar', {'k': 3, 'value': 4, 'power': 3}, 'number', '108', ('12', '36'), Q),
    ('mens.diameter_as_radius.mens_circle_area', 'mens_circle_area', {'r': 3}, 'pi_multiple', '9', '36', Q),
    ('mens.diameter_as_radius.mens_cyl_vol', 'mens_cyl_vol', {'r': 3, 'h': 5}, 'pi_multiple', '45', '180', Q),
    ('mens.diameter_as_radius.mens_cone_vol', 'mens_cone_vol', {'r': 3, 'h': 4}, 'pi_multiple', '12', '48', Q),
    ('mens.diameter_as_radius.mens_sphere_vol', 'mens_sphere_vol', {'r': 12}, 'pi_multiple', '2304', '18432', Q),
    ('mens.diameter_as_radius.mens_sphere_sa', 'mens_sphere_sa', {'r': 3}, 'pi_multiple', '36', '144', Q),
    # ---- Pythagoras ----
    ('pyth.hyp_not_rooted', 'pyth_hyp', {'a': 3, 'b': 4}, 'number', '5', '25', Q),
    ('pyth.hyp_sides_added', 'pyth_hyp', {'a': 3, 'b': 4}, 'number', '5', '7', Q),
    ('pyth.hyp_subtracted', 'pyth_hyp', {'a': 6, 'b': 8}, 'number', '10', '5.3', R1DP),
    ('pyth.leg_added', 'pyth_leg', {'c': 10, 'a': 6}, 'number', '8', '11.7', R1DP),
    ('pyth.leg_not_rooted', 'pyth_leg', {'c': 10, 'a': 6}, 'number', '8', '64', Q),
    ('pyth.leg_sides_subtracted', 'pyth_leg', {'c': 10, 'a': 6}, 'number', '8', '4', Q),
    ('pyth.distance_not_rooted', 'pyth_dist', {'x1': 1, 'y1': 2, 'x2': 4, 'y2': 6}, 'number', '5', '25', Q),
    ('pyth.distance_differences_added', 'pyth_dist', {'x1': 1, 'y1': 2, 'x2': 4, 'y2': 6}, 'number', '5', '7', Q),
    ('pyth.perimeter_sides', 'pyth_perimeter', {'a': 3, 'b': 4}, 'number', '12', ('5', '7'), Q),
    ('pyth.height_base_not_halved', 'pyth_isosceles_height', {'side': 13, 'base': 10}, 'number', '12', '8.3', R1DP),
    ('pyth.height_added', 'pyth_isosceles_height', {'side': 13, 'base': 10}, 'number', '12', '13.9', R1DP),
    ('pyth.height_not_rooted', 'pyth_isosceles_height', {'side': 13, 'base': 10}, 'number', '12', '144', Q),
    ('pyth.space_not_rooted', 'pyth_space_diag', {'l': 2, 'w': 3, 'h': 6}, 'number', '7', '49', Q),
    ('pyth.space_one_step_short', 'pyth_space_diag', {'l': 2, 'w': 3, 'h': 6}, 'number', '7', '3.6', R1DP),
    ('pyth.space_sides_added', 'pyth_space_diag', {'l': 2, 'w': 3, 'h': 6}, 'number', '7', '11', Q),
    ('pyth.ladder_original_position', 'pyth_ladder_slide', {'ladder': 13, 'base': 3, 'slide': 2}, 'number', '12', '12.6', R1DP),
    # ---- trigonometry ----
    ('trig.side_wrong_ratio', 'trig_side', {'known': 10, 'angle': 30, 'known_kind': 'hyp', 'find_kind': 'opp'}, 'number', '5', '8.7', R1DP),
    ('trig.side_rearranged', 'trig_side', {'known': 10, 'angle': 30, 'known_kind': 'hyp', 'find_kind': 'opp'}, 'number', '5', '20', R1DP),
    ('trig.side_radians', 'trig_side', {'known': 10, 'angle': 30, 'known_kind': 'hyp', 'find_kind': 'opp'}, 'number', '5', '-9.9', R1DP),
    ('trig.angle_radians', 'trig_angle', {'opp': 3, 'adj': 4}, 'number', '36.87', '0.64', 'Find the angle. ' + R2DP),
    ('trig.angle_ratio_only', 'trig_angle', {'opp': 3, 'adj': 4}, 'number', '36.87', '0.75', 'Find the angle. ' + R2DP),
    ('trig.angle_other', 'trig_angle', {'opp': 3, 'adj': 4}, 'number', '36.87', '53.13', 'Find the angle. ' + R2DP),
    ('trig.angle_ratio_only', 'trig_sine_angle', {'a': 4, 'angle_b': 30, 'b': 5}, 'number', '23.58', '0.4', 'Find the angle. ' + R2DP),
    ('trig.angle_ratio_only', 'trig_cosine_angle', {'a': 3, 'b': 4, 'c': 5}, 'number', '36.87', '0.8', 'Find the angle. ' + R2DP),
    ('trig.angle_radians', 'trig_sine_angle', {'a': 4, 'angle_b': 30, 'b': 5}, 'number', '23.58', '0.41', 'Find the angle. ' + R2DP),
    ('trig.angle_radians', 'trig_cosine_angle', {'a': 3, 'b': 4, 'c': 5}, 'number', '36.87', '0.64', 'Find the angle. ' + R2DP),
    ('trig.cosine_side_not_rooted', 'trig_cosine_side', {'b': 10, 'c': 10, 'angle': 60}, 'number', '10', '100', R1DP),
    ('trig.cosine_side_sign', 'trig_cosine_side', {'b': 10, 'c': 10, 'angle': 60}, 'number', '10', '17.3', R1DP),
    ('trig.cosine_side_radians', 'trig_cosine_side', {'b': 10, 'c': 10, 'angle': 60}, 'number', '10', '19.8', R1DP),
    # angle 40, not 30: with sin 30 = 0.5 the full product a b sin C equals a b / 2 (the sine left out), a quiet value
    ('trig.area_full_product', 'trig_area', {'a': 10, 'b': 10, 'angle': 40}, 'number', '32.1', '64.3', R1DP),
    ('trig.area_radians', 'trig_area', {'a': 10, 'b': 10, 'angle': 40}, 'number', '32.1', '37.3', R1DP),
    ('trig.area_cosine', 'trig_area', {'a': 10, 'b': 10, 'angle': 40}, 'number', '32.1', '38.3', R1DP),
    ('trig.sine_side_inverted', 'trig_sine_side', {'known_side': 10, 'known_angle': 30, 'target_angle': 90}, 'number', '20', '5', R1DP),
    ('trig.sine_side_radians', 'trig_sine_side', {'known_side': 10, 'known_angle': 30, 'target_angle': 90}, 'number', '20', '-9', R1DP),
    ('trig.apex_half', 'trig_isosceles_apex', {'base': 6, 'equal': 5}, 'number', '73.7', '36.9', R1DP),
    # ---- percentages, fractions and number ----
    ('pct.change_only', 'num_pct_change', {'amount': 200, 'pct': 15, 'sign': 'up'}, 'number', '230', '30', Q),
    ('pct.change_opposite', 'num_pct_change', {'amount': 200, 'pct': 15, 'sign': 'up'}, 'number', '230', '170', Q),
    ('pct.reverse_as_forward', 'num_reverse_pct', {'final': 240, 'pct': 20, 'sign': 'up'}, 'number', '200', '192', Q),
    ('pct.reverse_opposite', 'num_reverse_pct', {'final': 240, 'pct': 20, 'sign': 'up'}, 'number', '200', '300', Q),
    ('pct.vat_only', 'num_vat_inclusive', {'price': 50, 'vat': 20}, 'number', '60', '10', Q),
    ('pct.vat_taken_off', 'num_vat_inclusive', {'price': 50, 'vat': 20}, 'number', '60', '40', Q),
    ('pct.changes_added', 'num_two_pct_changes', {'amount': 200, 'pct1': 10, 'pct2': 20}, 'number', '176', '180', Q),
    ('pct.reverse_two_added', 'fdp_reverse_two_step', {'final': 192, 'pct_up': 20, 'pct_down': 20}, 'number', '200', '192', Q),
    ('pct.compound_simple', 'num_compound', {'principal': 1000, 'rate': 10, 'years': 2, 'sign': 'up'}, 'number', '1210', '1200', Q),
    ('pct.compound_opposite', 'num_compound', {'principal': 1000, 'rate': 10, 'years': 2, 'sign': 'up'}, 'number', '1210', '810', Q),
    ('pct.reverse_compound_forward', 'num_reverse_compound', {'final': 1210, 'rate': 10, 'years': 2}, 'number', '1000', '980.1', Q),
    ('pct.reverse_compound_one_year', 'num_reverse_compound', {'final': 1210, 'rate': 10, 'years': 2}, 'number', '1000', '1100', Q),
    ('pct.of_divided', 'num_pct_of', {'amount': 200, 'pct': 20}, 'number', '40', '10', Q),
    ('pct.wrong_base', 'fdp_pct_change', {'original': 40, 'new': 50}, 'number', '25', '20', Q),
    ('pct.wrong_base', 'fdp_profit_pct', {'cost': 40, 'selling': 50}, 'number', '25', '20', Q),
    ('pct.change_not_compared', 'fdp_pct_change', {'original': 40, 'new': 50}, 'number', '25', '10', Q),
    ('pct.error_wrong_base', 'num_pct_error', {'estimate': 40, 'actual': 50}, 'number', '20', '25', Q),
    ('pct.error_not_compared', 'num_pct_error', {'estimate': 40, 'actual': 50}, 'number', '20', '10', Q),
    ('pct.discount_only', 'fdp_shop_discount', {'unit': 5, 'qty': 4, 'discount_pct': 10}, 'number', '18', '2', Q),
    ('pct.discount_added', 'fdp_shop_discount', {'unit': 5, 'qty': 4, 'discount_pct': 10}, 'number', '18', '22', Q),
    ('fdp.other_part', 'fdp_fraction_not', {'total': 40, 'num': 3, 'den': 8}, 'number', '25', '15', Q),
    ('fdp.fraction_inverted_of', 'num_frac_of', {'amount': 40, 'num': 2, 'den': 5}, 'number', '16', '100', Q),
    ('fdp.bottom_only', 'num_frac_of', {'amount': 40, 'num': 2, 'den': 5}, 'number', '16', '8', Q),
    ('fdp.fraction_to_pct_inverted', 'fdp_fraction_to_pct', {'a': 1, 'b': 4}, 'number', '25', '400', Q),
    ('fdp.decimal_fraction_place_value', 'fdp_decimal_to_fraction', {'dec': 0.25}, 'fraction', '1/4', ('1/40', '5/2'), Q),
    ('fdp.pct_fraction_per_cent', 'fdp_pct_to_fraction', {'pct': 25}, 'fraction', '1/4', ('5/2', '1/40'), Q),
    ('dec.mean_total', 'dec_mean', {'values': [2, 4, 6]}, 'number', '4', '12', Q),
    ('est.exact_product', 'num_estimate_product_1sf', {'a': 3.8, 'b': 6.2}, 'number', '24', '23.56', Q),
    ('est.exact_product', 'num_estimate_product_whole', {'a': 3.8, 'b': 6.2}, 'number', '24', '23.56', Q),
    ('est.exact_fraction', 'num_estimate_fraction_1sf', {'a': 3.8, 'b': 6.2, 'c': 1.9}, 'number', '12', '12.4', Q),
    ('est.rounded_late', 'num_estimate_product_1sf', {'a': 3.8, 'b': 6.2}, 'number', '24', '20', Q),
    ('est.rounded_late_fraction', 'num_estimate_fraction_1sf', {'a': 3.8, 'b': 6.2, 'c': 1.9}, 'number', '12', '10', Q),
    ('num.double_negative', 'num_directed', {'a': 5, 'op': '-', 'b': -3}, 'number', '8', '2', Q),
    ('idx.multiplied', 'num_power', {'base': 3, 'exp': 4}, 'number', '81', '12', Q),
    ('idx.negative_power', 'num_neg_index', {'base': 2, 'power': 3}, 'number', '0.125', ('-8', '-0.125'), Q),
    ('idx.power_sign_ignored', 'num_neg_index', {'base': 2, 'power': 3}, 'number', '0.125', '8', Q),
    ('idx.zero_power', 'num_zero_neg_index', {'a': 3, 'b': 2}, 'number', '0.25', ('0.75', '0'), Q),
    ('idx.fraction_power', 'num_frac_index', {'base': 16, 'num': 1, 'den': 2}, 'number', '4', '8', Q),
    # ---- order of operations ----
    ('bidmas.left_to_right', 'arith', {'expr': '2 + 3 × 4'}, 'number', '14', '20', 'Calculate 2 + 3 × 4.'),
    ('bidmas.brackets_ignored', 'arith', {'expr': '(2 + 3) × 4'}, 'number', '20', '14', 'Calculate (2 + 3) × 4.'),
    ('bidmas.power_multiplied', 'arith', {'expr': '3 + 2^3'}, 'number', '11', '9', 'Calculate 3 + 2^3.'),
    ('bidmas.negative_square', 'arith', {'expr': '(−3)^2'}, 'number', '9', '-9', 'Calculate (-3)^2.'),
    ('op.divided_for_product', 'product', {'a': 6, 'b': 4}, 'number', '24', ('1.5', '10'), Q),
    ('op.multiplied_for_quotient', 'quotient', {'a': 24, 'b': 4}, 'number', '6', '96', Q),
    ('op.quotient_inverted', 'quotient', {'a': 25, 'b': 4}, 'number', '6.25', ('0.16', '4/25'), Q),
    # ---- ratio and proportion ----
    ('ratio.map_not_converted', 'ratio_map_scale', {'cm': 5, 'scale': 50000, 'to': 'km'}, 'number', '2.5', '250000', Q),
    ('ratio.map_divided', 'ratio_map_scale', {'cm': 5, 'scale': 50000, 'to': 'km'}, 'number', '2.5', '0.0001', Q),
    ('ratio.direct_inverse_used', 'prop_direct', {'y1': 12, 'x1': 3, 'x2': 5}, 'number', '20', '7.2', Q),
    ('ratio.direct_additive', 'prop_direct', {'y1': 12, 'x1': 3, 'x2': 5}, 'number', '20', '14', Q),
    ('ratio.direct_unit_only', 'prop_direct', {'y1': 12, 'x1': 3, 'x2': 5}, 'number', '20', '4', Q),
    ('ratio.inverse_direct_used', 'prop_inverse', {'a': 6, 'b': 4, 'c': 3}, 'number', '8', '2', Q),
    ('ratio.scale_inverse_used', 'prop_scale', {'q1': 12, 'n1': 4, 'n2': 6}, 'number', '18', '8', Q),
    ('ratio.scale_unit_only', 'prop_scale', {'q1': 12, 'n1': 4, 'n2': 6}, 'number', '18', '3', Q),
    ('ratio.scale_additive', 'prop_scale', {'q1': 12, 'n1': 4, 'n2': 6}, 'number', '18', '14', Q),
    ('ratio.unitary_unit_only', 'ratio_unitary', {'total': 12, 'n1': 4, 'n2': 5}, 'number', '15', '3', Q),
    ('ratio.unitary_inverse_used', 'ratio_unitary', {'total': 12, 'n1': 4, 'n2': 5}, 'number', '15', '9.6', Q),
    ('ratio.missing_parts_swapped', 'ratio_find_missing', {'known': 12, 'a': 3, 'b': 5}, 'number', '20', '7.2', Q),
    ('ratio.missing_unit_only', 'ratio_find_missing', {'known': 12, 'a': 3, 'b': 5}, 'number', '20', '4', Q),
    ('ratio.missing_additive', 'ratio_find_missing', {'known': 12, 'a': 3, 'b': 5}, 'number', '20', '14', Q),
    ('ratio.part_to_part', 'ratio_part_fraction', {'parts': [2, 3], 'which': 0}, 'fraction', '2/5', '2/3', Q),
    # ---- compound measures ----
    ('cm.speed_direction_kmh', 'cm_kmh_to_ms', {'kmh': 36}, 'number', '10', '129.6', Q),
    ('cm.speed_one_unit_kmh', 'cm_kmh_to_ms', {'kmh': 36}, 'number', '10', ('36000', '0.01'), Q),
    ('cm.speed_direction_ms', 'cm_ms_to_kmh', {'ms': 18}, 'number', '64.8', '5', Q),
    ('cm.speed_one_unit_ms', 'cm_ms_to_kmh', {'ms': 18}, 'number', '64.8', ('64800', '0.018'), Q),
    ('cm.minutes_decimal_hm', 'cm_speed_hm', {'s': 60, 'h': 1, 'm': 30}, 'number', '90', '78', Q),
    ('cm.minutes_unconverted_hm', 'cm_speed_hm', {'s': 60, 'h': 1, 'm': 30}, 'number', '90', '5400', Q),
    ('cm.minutes_decimal_mins', 'cm_dist_mins', {'s': 60, 'mins': 30}, 'number', '30', '18', Q),
    ('cm.minutes_unconverted_mins', 'cm_dist_mins', {'s': 60, 'mins': 30}, 'number', '30', '1800', Q),
    ('cm.mean_of_speeds', 'cm_avg_speed', {'legs': [[60, 30], [60, 60]]}, 'number', '40', '45', Q),
    ('cm.mean_of_speeds_time', 'cm_avg_speed_time', {'legs': [[1, 30], [2, 60]]}, 'number', '50', '45', Q),
    ('cm.mean_of_two_speeds', 'cm_avg_speed_equal', {'s1': 30, 's2': 60}, 'number', '40', '45', Q),
    ('cm.mean_of_densities', 'cm_alloy_vol', {'d1': 2, 'd2': 6, 'v1': 1, 'v2': 3}, 'number', '5', '4', Q),
    ('cm.mean_of_densities', 'cm_composite_density', {'r1': 1, 'd1': 2, 'r2': 3, 'd2': 6}, 'number', '5', '4', Q),
    ('cm.alloy_weighted_mean', 'cm_alloy_pct', {'pa': 20, 'pb': 80, 'da': 2, 'db': 8}, 'number', '5', '6.8', Q),
    ('cm.pressure_from_mass', 'cm_box_pressure', {'mass': 10, 'g': 10, 'length': 2, 'width': 5}, 'number', '10', '1', Q),
    ('cm.pipes_combined', 'cm_pipes', {'vol': 60, 'fill': 8, 'drain': 4}, 'number', '15', ('5', '7.5'), Q),
    ('cm.closing_speed_overtake', 'cm_overtake', {'head_min': 30, 'slow': 40, 'fast': 60}, 'number', '60', '12', Q),
    ('cm.closing_speed_relative', 'cm_relative', {'s1': 50, 's2': 30, 'dist': 20, 'direction': 'same'}, 'number', '60', '15', Q),
) + CDT.TX


def run_topic_table(only_rule=None, only_family=None):
    """Run the hand-worked topic table. Returns the failing case descriptions."""
    failed = []
    for rid, fam, inputs, at, key, typed, question in TX:
        if (only_rule and rid != only_rule) or (only_family and fam != only_family):
            continue
        rule = T.RULES_BY_ID[rid]
        if fam not in rule.families:
            failed.append(f'{rid}: example family {fam} is not one of the rule families {rule.families}')
            continue
        prob = topic_problem(fam, inputs, at, key, question)
        for t in (typed if isinstance(typed, tuple) else (typed,)):
            if check_answer(at, key, t).get('correct'):
                failed.append(f'{rid} ({fam}): the example {t!r} is accepted by the checker (key {key!r})')
                continue
            got = run_topic(prob, t)
            if got is None or got.message != M.MESSAGES[rule.message]:
                failed.append(f'{rid} ({fam}): key {key!r}, typed {t!r}: expected {rule.message!r}, got '
                              f'{got.rule_id if got else None!r}')
    return failed


def topic_cases():
    out = []

    def case(name, ok):
        out.append((name, ok))

    neg = topic_problem('num_neg_index', {'base': 2, 'power': 3}, 'number', '0.125')
    plain = {k: v for k, v in neg.items() if k != 'answer_record'}
    # precedence: a topic message wins over a generic one on the same typed value
    g = run_topic(plain, '-0.125')
    case('without a record -0.125 is only the generic sign slip', g is not None and g.rule_id == 'gen.sign')
    t = run_topic(neg, '-0.125')
    case('with a record the same value gets the topic message, not the generic one',
         t is not None and t.rule_id == 'idx.negative_power')
    t = run_topic(neg, '8')
    case('with a record 8 gets the topic message', t is not None and t.rule_id == 'idx.power_sign_ignored')
    # no topic hit: the generic rules still run
    g = run_topic(neg, '1.25')
    case('a value no topic rule claims falls back to the generic rule', g is not None and g.rule_id == 'gen.pow10')
    case('a record never silences the key', run_topic(neg, '0.125') is None)
    # two different topic messages on one value: nothing is shown, and the generic rule does not step in
    prod = topic_problem('product', {'a': 6, 'b': 4}, 'number', '24')
    base = T.RULES_BY_FAMILY['product']
    plain_prod = {k: v for k, v in prod.items() if k != 'answer_record'}
    case('240 is a generic factor-of-ten slip without a record',
         (run_topic(plain_prod, '240') or M.Diagnosis('', '', '')).rule_id == 'gen.pow10')
    saved = dict(T.RULES_BY_FAMILY)
    try:
        a = dataclasses.replace(base[0], id='test.a', message='op.multiply_needed', slip=lambda i, pi: [Fraction(240)])
        b = dataclasses.replace(base[0], id='test.b', message='op.divide_needed', slip=lambda i, pi: [Fraction(240)])
        T.RULES_BY_FAMILY['product'] = (a, b)
        case('two topic messages on one value: nothing is shown and the generic rule does not step in',
             run_topic(prod, '240') is None)
        c = dataclasses.replace(a, id='test.c')
        T.RULES_BY_FAMILY['product'] = (a, c)
        d = run_topic(prod, '240')
        case('two topic rules with one message: shown', d is not None and d.message == M.MESSAGES['op.multiply_needed'])
    finally:
        T.RULES_BY_FAMILY.clear()
        T.RULES_BY_FAMILY.update(saved)
    rect = topic_problem('mens_rect_perimeter', {'l': 2, 'w': 2}, 'number', '8')
    case('a 2 by 2 rectangle: area and half perimeter are both 4, so nothing is shown', run_topic(rect, '4') is None)
    case('a 5 by 3 rectangle: area is shown', run_topic(topic_problem('mens_rect_perimeter', {'l': 5, 'w': 3}, 'number', '16'),
                                                       '15') is not None)
    # the guard: the rebuilt answer must reproduce the stored key
    hyp = topic_problem('pyth_hyp', {'a': 3, 'b': 4}, 'number', '5')
    case('the record reproduces the key: 25 is the squared sum', run_topic(hyp, '25').rule_id == 'pyth.hyp_not_rooted')
    bad = topic_problem('pyth_hyp', {'a': 3, 'b': 4}, 'number', '6')
    case('inputs that do not reproduce the key give no topic message', run_topic(bad, '25') is None)
    case('... and the generic rules still run on that question', (run_topic(bad, '60') or M.Diagnosis('', '', '')).rule_id == 'gen.pow10')
    other = topic_problem('pyth_hyp', {'a': 6, 'b': 8}, 'number', '5')
    case('a record for another question (key 10) on a key of 5 is ignored', run_topic(other, '100') is None)
    case('a record whose key differs from the one being checked is ignored',
         M.read_record(hyp, 'number', '7') is None and M.read_record(hyp, 'number', '5') is not None)
    case('a record on a different answer type is ignored',
         M.read_record(dict(hyp, answer_type='number_fields'), 'number_fields', '5') is None
         and M.read_record(hyp, 'algebraic', '5') is None)
    # bad records never raise and never produce a message
    for name, rec in (('unknown family', {'f': 'nope', 'i': {'a': 3}}), ('missing input', {'f': 'pyth_hyp', 'i': {'a': 3}}),
                      ('inputs not a dict', {'f': 'pyth_hyp', 'i': [3, 4]}), ('not a dict', 'pyth_hyp'),
                      ('text for a number', {'f': 'pyth_hyp', 'i': {'a': 'x', 'b': 'y'}}),
                      ('zero divisor', {'f': 'num_frac_of', 'i': {'amount': 4, 'num': 1, 'den': 0}}),
                      ('huge number', {'f': 'num_power', 'i': {'base': 10 ** 400, 'exp': 5}})):
        prob = dict(hyp, answer_record=rec)
        try:
            got = M.diagnose(prob, '25', check_answer('number', '5', '25'), answer_type='number', correct_raw='5',
                             accepts=lambda t: False, level='gcse', subject='maths')
            ok = got is None or got.rule_id.startswith('gen.')
        except Exception:  # noqa: BLE001
            ok = False
        case(f'a bad record ({name}) is ignored', ok)
    # an answer the checker accepts is never a slip
    case('a candidate the checker accepts is dropped', run_topic(hyp, '25', accepts=lambda t: True) is None)
    # accuracy: exact or half-up at the stated accuracy, within the 5% guard
    circle = topic_problem('mens_circle_area', {'r': 3}, 'number', '28.3', 'Find the area. ' + R1DP)
    case('circle area to 1 d.p.: 2 pi r = 18.85 rounds to 18.8 (shown)', run_topic(circle, '18.8').rule_id == 'mens.area_uses_circumference')
    case('... 18.85 is not the rounding the question asked for', run_topic(circle, '18.85') is None)
    case('... 18.9 is not the value either', run_topic(circle, '18.9') is None)
    case('... pi r = 9.42 rounds to 9.4 (not squared)', run_topic(circle, '9.4').rule_id == 'mens.area_not_squared')
    frac = topic_problem('prop_direct', {'y1': 1, 'x1': 8, 'x2': 16}, 'number', '2', 'Find the cost. ' + R2DP)
    case('half rounds up: 0.125 to 2 d.p. is 0.13', run_topic(frac, '0.13').rule_id == 'ratio.direct_unit_only')
    case('... 0.12 is not a half-up rounding', run_topic(frac, '0.12') is None)
    case('... the exact 0.125 is the unit value too', run_topic(frac, '0.125').rule_id == 'ratio.direct_unit_only')
    km = topic_problem('ratio_map_scale', {'cm': 5, 'scale': 50000, 'to': 'km'}, 'number', '2.5')
    case('no accuracy stated: the exact value is matched', run_topic(km, '0.0001').rule_id == 'ratio.map_divided')
    case('... a different value is not', run_topic(km, '0.0002') is None)
    case('... nor a rounded one (within the 5% guard only when an accuracy is stated)', run_topic(km, '0.0') is None)
    # the key itself, wrong forms and unparseable answers
    for typed in ('5', '5.0', 'abc', '', '1/0'):
        case(f'pyth hyp key {typed!r}: no topic message', run_topic(hyp, typed) is None)
    # review 2026-10-26: quiet values, the near-key guard, percentage error, input caps
    space = topic_problem('pyth_space_diag', {'l': 3, 'w': 4, 'h': 5}, 'number', '7.07', 'Find it. ' + R2DP)
    case('3, 4, 5 cuboid: the face diagonal 5 is also the height printed in the question, so nothing is said',
         run_topic(space, '5') is None)
    case('... and the squared sum still is', (run_topic(space, '50') or M.Diagnosis('', '', '')).rule_id == 'pyth.space_not_rooted')
    quarter = topic_problem('quotient', {'a': 1, 'b': 4}, 'number', '0.25', 'Convert 1/4 to a decimal.')
    case('1/4 typed as 4: the 4 of the question, read by the generic rule as a division the other way round',
         (run_topic(quarter, '4') or M.Diagnosis('', '', '')).rule_id == 'gen.reciprocal')
    cos66 = topic_problem('trig_cosine_side', {'b': 9, 'c': 9, 'angle': 66}, 'number', '9.8', 'Find a. ' + R2DP)
    case('cosine rule, 66 degrees: radians give 18.00, which is also the two sides added, so no radians message',
         run_topic(cos66, '18') is None)
    case('... the squared value is still named', (run_topic(cos66, '96.11') or M.Diagnosis('', '', '')).rule_id
         == 'trig.cosine_side_not_rooted')
    cub = topic_problem('mens_cuboid_sa', {'l': 9, 'w': 7, 'h': 4}, 'number', '254')
    case('surface area 254, typed 252: next to the key (a small slip), not "a volume"', run_topic(cub, '252') is None)
    case('... the faces-missed value 127 is still named', (run_topic(cub, '127') or M.Diagnosis('', '', '')).rule_id
         == 'mens.cuboid_area_faces_missed')
    rev = topic_problem('num_reverse_pct', {'final': 72, 'pct': 10, 'sign': 'down'}, 'number', '80')
    case('reverse percentage, key 80: 79.2 is the slip', (run_topic(rev, '79.2') or M.Diagnosis('', '', '')).rule_id
         == 'pct.reverse_as_forward')
    case('... but 79 (one away from the key) is not matched by rounding 79.2 to the pupil\'s places', run_topic(rev, '79') is None)
    err = topic_problem('num_pct_error', {'estimate': 240, 'actual': 250}, 'number', '4', 'Find it. ' + R1DP)
    case('percentage error divides by the actual value; the estimate as the base is named',
         (run_topic(err, '4.2') or M.Diagnosis('', '', '')).rule_id == 'pct.error_wrong_base')
    circ = topic_problem('mens_circle_area', {'r': 3}, 'pi_multiple', '9')
    case('a coefficient of pi equal to a printed number is not a copied number (3 pi is the radius not squared)',
         (run_topic(circ, '3') or M.Diagnosis('', '', '')).rule_id == 'mens.area_not_squared')
    # whole-change review 2026-11-03 (F1): the key rounded or cut to the pupil's places is the right answer written
    # short, for every answer type; only a slip that is the key written short by its nature speaks there, at its exact value
    tree = topic_problem('prob_tree', {'n_first': 6, 'first_word': 'red', 'n_second': 3, 'second_word': 'blue', 'replace': True,
                                       'ask': 'both'}, 'fraction', '4/9', 'A bag has 6 red and 3 blue counters. A counter is chosen, '
                                                                            'replaced, then another is chosen. Find P(two red).')
    case('F1: P(two red) = 4/9 typed 0.4 (the key to 1 d.p.) is not "the item is put back"', run_topic(tree, '0.4') is None)
    case('F1: ... nor typed 0.44', run_topic(tree, '0.44') is None)
    case('F1: ... the slip itself (5/12, without replacement) is still named', (run_topic(tree, '5/12') or M.Diagnosis('', '', '')).rule_id
         == 'prob.tree_put_back_missed')
    tree2 = topic_problem('prob_tree', {'n_first': 3, 'first_word': 'red', 'n_second': 2, 'second_word': 'blue', 'replace': True,
                                        'ask': 'both'}, 'fraction', '9/25', Q)
    case('F1: P(two red) = 9/25 typed 0.3 (the key cut to 1 d.p.) is silent, though without replacement is exactly 3/10',
         run_topic(tree2, '0.3') is None)
    case('F1: ... and 3/10 typed as a fraction is named', (run_topic(tree2, '3/10') or M.Diagnosis('', '', '')).rule_id
         == 'prob.tree_put_back_missed')
    dice = topic_problem('prob_sample_space', {'n1': 6, 'n2': 6, 'op': 'product', 'event_word': 'less than 12'}, 'fraction', '19/36', Q)
    case('F1: P(product < 12) = 19/36 typed 0.5 (the key to 1 d.p.) is silent, though nine of 18 distinct products is exactly 1/2',
         run_topic(dice, '0.5') is None)
    case('F1: ... the slip typed as a fraction is still named', (run_topic(dice, '1/2') or M.Diagnosis('', '', '')).rule_id
         == 'prob.space_distinct_totals')
    for key, dec, typed in (('1/3', '0.333…', '0.3'), ('2/3', '0.666…', '0.6')):
        rec = topic_problem('num_recurring_text', {'dec': dec}, 'fraction', key, f'Write {dec} as a fraction.')
        case(f'F1: {typed} for {key}: a recurring decimal read as ending is still named (the slip is the key written short)',
             (run_topic(rec, typed) or M.Diagnosis('', '', '')).rule_id == 'num.recurring_terminating')
    # whole-change review 2026-11-03 (F2): a slip that is not whole never matches a whole typed value by rounding
    frac_eq = topic_problem('lin_eq', {'a': ['3/2', '1/2', 0, 17]}, 'linear', '11', 'Solve (3x + 1)/2 = 17.')
    case('F2: x = 11 typed 12 is not "the sign of the term that moved" (35/3 = 11.67 rounded to no places)', run_topic(frac_eq, '12') is None)
    case('F2: ... that slip typed to 2 d.p. is still named', (run_topic(frac_eq, '11.67') or M.Diagnosis('', '', '')).rule_id
         == 'alg.lin_sign_moved')
    brk = topic_problem('lin_eq', {'a': [3, 3, 0, 24], 'br': [[0, 3, 1, 3]]}, 'linear', '7', 'Solve 3(x + 1) = 24.')
    case('F2: x = 7 typed 8 is not "check the brackets" (23/3 = 7.67 rounded to no places)', run_topic(brk, '8') is None)
    # whole-change review 2026-11-03 (F3): the key at a coarser accuracy than stated is the generic accuracy line
    legs = {'legs': [[55, 31], [34, 96], [44, 170]], 'want': ['dist', 'bearing']}
    boxes = {'question': 'A ship sails 55 km on bearing 031°, then 34 km on bearing 096°, then 44 km on bearing 170°. Find the '
                         'bearing (to the nearest degree) and distance (to 1 d.p.) from the start.',
             'answer_type': 'number_fields', 'correct_answer_raw': '69.8|90', 'answer_record': {'f': 'brg_legs', 'i': legs}}
    for typed in ('70', '70.0'):
        got = M._diagnose(boxes, typed, check_answer('number', '69.8', typed), 'number', '69.8',
                          lambda t: bool(check_answer('number', '69.8', t).get('correct')), 'gcse', 'maths', 'bearings', None, part=0)
        case(f'F3: distance 69.8 (1 d.p.) typed {typed}: round to the accuracy asked, not "the side lengths added"',
             got is not None and got.rule_id == 'gen.accuracy_coarser')
    # whole-change review 2026-11-03 (F10): an exact half bearing rebuilds as the generator rounds it; a decimal bearing
    # is read as typed
    half = {'question': 'A ship sails 63 km on a bearing of 062°, then 63 km on a bearing of 155°. Find the bearing of the '
                        'ship from its start, to the nearest degree.', 'answer_type': 'bearing', 'correct_answer_raw': '109',
            'answer_record': {'f': 'brg_legs', 'i': {'legs': [[63, 62], [63, 155]], 'want': ['bearing']}}}
    case('F10: two equal legs on 062° and 155° give exactly 108.5°, key 109: the record rebuilds it, so its rules stay on',
         bool(M.topic_candidates(half, 'bearing', '109', M.build_ctx(half, 'bearing', '109', 'bearings'))))
    one = {'question': 'A ship sails 10 km on a bearing of 082°. Find its bearing from the start.', 'answer_type': 'bearing',
           'correct_answer_raw': '082', 'answer_record': {'f': 'brg_legs', 'i': {'legs': [[10, 82]], 'want': ['bearing']}}}
    case('F10: 8.2 typed for the bearing 082 is not read as 8 ("measured from east")', run_diag(one, 'bearing', '082', '8.2') is None)
    case('F10: ... 8 itself still is', (run_diag(one, 'bearing', '082', '8') or M.Diagnosis('', '', '')).rule_id == 'brg.legs_from_east')
    t0 = time.time()
    for rec in ({'f': 'num_compound', 'i': {'principal': 1000, 'rate': 10, 'years': 10 ** 9, 'sign': 'up'}},
                {'f': 'num_power', 'i': {'base': 10 ** 13, 'exp': 2}},
                {'f': 'num_pct_of', 'i': {'amount': '1e999999', 'pct': 10}},
                {'f': 'pyth_hyp', 'i': {'a': 3.0, 'b': float('inf')}}):
        bad = dict(topic_problem(rec['f'], {}, 'number', '1210'), answer_record=rec)
        case(f'a record with a huge or odd input is not used ({rec["f"]})', M.topic_candidates(
            bad, 'number', '1210', M.build_ctx(bad, 'number', '1210')) == [])
    case('... and costs almost nothing', time.time() - t0 < 0.5)
    big = dict(hyp, answer_record={'f': 'pyth_hyp', 'i': {'a': 3, 'b': 4, 'pad': 'x' * 300}})
    case('a record over 256 bytes is not read', M.read_record(big, 'number', '5') is None)
    # multi-part answers get no topic record
    multi = {'question': 'q', 'answer_type': 'number_fields', 'correct_answer_raw': '5|7', 'answer_record': hyp['answer_record']}
    case('a part of a multi-part answer is not diagnosed from a whole-answer record',
         run_diag(multi, 'number', '5', '25', topic='pythagoras') is None
         or run_diag(multi, 'number', '5', '25', topic='pythagoras').rule_id.startswith('gen.'))
    return out


def check_topic_table():
    for line in run_topic_table():
        issue('unit_table', 'topic table', line)
    for name, ok in topic_cases():
        if not ok:
            issue('unit_table', 'topic cases', name)
    have_rules = {e[0] for e in TX}
    for rule in T.RULES:
        if rule.id not in have_rules:
            issue('unit_table', rule.id, 'topic rule has no hand-worked example')
    have_fams = {e[1] for e in TX}
    for fam in sorted(T.FAMILIES - have_fams):
        issue('unit_table', fam, 'recorded family has no hand-worked example (its truth guard is untested)')
    for rid in sorted(have_rules - set(T.RULES_BY_ID)):
        issue('unit_table', rid, 'example for a rule that does not exist')
    for rule in T.RULES:
        if rule.message not in M.MESSAGES:
            issue('unit_table', rule.id, f'message id {rule.message!r} missing from MESSAGES')


def check_topic_mutation():
    """Perturb each topic rule's value by one unit, and each family's truth by one unit: the table must notice."""
    saved_by_family = dict(T.RULES_BY_FAMILY)
    saved_truth = dict(T.TRUTH)
    killed = total = 0
    try:
        for rule in T.RULES:
            total += 1
            orig = rule.slip
            mutant = dataclasses.replace(rule, slip=lambda i, pi, o=orig: [Fraction(c) * Fraction(21, 20) + 3 for c in o(i, pi)])
            for fam in rule.families:
                T.RULES_BY_FAMILY[fam] = tuple(mutant if r is rule else r for r in saved_by_family[fam])
            if run_topic_table(only_rule=rule.id):
                killed += 1
            else:
                issue('mutation', rule.id, 'a topic rule whose value is off by one still passes the table')
            for fam in rule.families:
                T.RULES_BY_FAMILY[fam] = saved_by_family[fam]
        for fam in sorted(T.FAMILIES):
            total += 1
            orig = saved_truth[fam]
            T.TRUTH[fam] = lambda i, pi, o=orig: Fraction(o(i, pi)) + 1
            if run_topic_table(only_family=fam):
                killed += 1
            else:
                issue('mutation', fam, 'a truth guard that is off by one still passes the table')
            T.TRUTH[fam] = orig
    finally:
        T.RULES_BY_FAMILY.clear()
        T.RULES_BY_FAMILY.update(saved_by_family)
        T.TRUTH.clear()
        T.TRUTH.update(saved_truth)
    return killed, total


# ─────────────────────────────────────────────────────────────────────────────
# topic rules on real generated questions: sound, reachable, unambiguous, collisions silent
# ─────────────────────────────────────────────────────────────────────────────

NINE_TOPICS = ('bidmas', 'decimals', 'fdp', 'number', 'ratio_proportion', 'pythagoras', 'trigonometry', 'mensuration',
               'compound_measures', 'surds', 'multiples_factors')
GUARD_FAIL_SHARE_MAX = 0.03         # records whose rebuilt answer does not reproduce the key (they only lose the topic rule)


def new_topic_state():
    return {'records': 0, 'guard_fail': [], 'sizes': [], 'slot_record': set(), 'slot_fired': set(), 'slot_fired_near': set(),
            'fired': collections.Counter(), 'applicable': collections.Counter(), 'collided': collections.Counter(),
            'examples': {}, 'checks': 0, 'slot_rule_done': set(), 'preempts': 0, 'families': collections.defaultdict(set), 'cd': CDT.new_state()}


def topic_item(slot, run, problem, st):
    rec = problem.get('answer_record')
    if rec is None:
        return
    at, raw = problem.get('answer_type') or 'number', str(problem.get('correct_answer_raw'))
    label = f'{slot.label}#{run}'
    st['records'] += 1
    st['slot_record'].add(slot.label)
    size = len(json.dumps(rec, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))
    st['sizes'].append(size)
    if size > AR.MAX_BYTES:
        issue('no_leak', label, f'answer_record is {size} bytes (limit {AR.MAX_BYTES})')
    if CDT.handles(problem):
        CDT.item(slot, run, problem, st['cd'])
        return
    if at not in AR.RECORDED_ANSWER_TYPES or problem.get('options') or rec.get('f') not in T.FAMILIES \
            or at not in M.RECORDED_FAMILIES.get(rec.get('f'), ()):
        issue('rule_sound', label, f'a record on a question that cannot use one ({at}, family {rec.get("f")!r})')
        return
    st['families'][rec['f']].add(slot.label)
    form = problem_answer_form(problem)
    ctx = M.build_ctx(problem, at, raw, slot.slug, form)
    cands = M.topic_candidates(problem, at, raw, ctx)
    if cands is None:
        issue('rule_sound', label, 'the record cannot be read back')
        return
    if not cands and not T.RULES_BY_FAMILY.get(rec['f']):
        return
    # the truth guard: does the rebuilt answer reproduce the key?
    pi = Fraction(1) if at == 'pi_multiple' else T.PI
    try:
        agrees = M._agrees(T.TRUTH[rec['f']](rec['i'], pi), ctx)
    except Exception:  # noqa: BLE001
        agrees = False
    if not agrees:
        st['guard_fail'].append(label)
        return
    accepts = lambda t: bool(check_answer(at, raw, t, form=form).get('correct'))      # noqa: E731
    exs = M.topic_examples(problem, at, raw, slot.slug, form)
    applicable = set()
    diagnosed = set()
    for rid, typed in exs:
        st['checks'] += 1
        res = check_answer(at, raw, typed, form=form)
        if res.get('correct'):
            issue('rule_sound', label, f'{rid} candidate {typed!r} is accepted by the checker (key {raw!r})')
            continue
        val = M.read_user_scalar(at, typed, form)
        if val is None:
            issue('rule_sound', label, f'{rid} candidate {typed!r} cannot be read back')
            continue
        if val == ctx.key:
            issue('rule_sound', label, f'{rid} candidate {typed!r} equals the key {raw!r}')
            continue
        if ctx.spec is None and val.denominator != 1 and rid not in M.CUT_SHORT_RULES \
                and M._key_cut_short(ctx, val, M._typed_places(typed)):
            # whole-change review 2026-11-03 (F1): a slip whose decimal is the key written short (3/10 for 9/25) is named
            # only when typed in full, as a fraction
            typed = f'{val.numerator}/{val.denominator}'
            res = check_answer(at, raw, typed, form=form)
        hits = M._topic_hits(ctx, cands, typed, accepts)
        rule = T.RULES_BY_ID[rid]
        if rule.message not in hits:
            issue('rule_reachable', label, f'{rid}: its own candidate {typed!r} does not match itself (key {raw!r})')
            continue
        applicable.add(rid)
        if (rid, typed) in diagnosed:
            continue
        diagnosed.add((rid, typed))
        # whole-change review 2026-11-03 (F9): a firing next to the key (one either side of a whole key, the key to no or
        # one decimal place) is far likelier an arithmetic slip or the key written short: it does not cover the slot
        near = val in CDT.near_key_values(ctx.key)
        if len(hits) == 1 and (rid, slot.label) in st['slot_rule_done']:
            # Phase 5b (speed): the full diagnosis of a rule on a slot is run once per slot; later seeds of the same
            # slot only check that the candidate still matches itself alone (the unambiguous count stays honest)
            st['fired'][rid] += 1
            st['slot_fired_near' if near else 'slot_fired'].add(slot.label)
            continue
        got = run_diag(problem, at, raw, typed, topic=slot.slug, form=form, result=res)
        if len(hits) >= 2:
            st['collided'][rid] += 1
            if got is not None:
                issue('no_collision', label, f'{typed!r} matches {sorted(hits)} but the pupil is shown {got.message!r}')
            continue
        if got is None or got.message != M.MESSAGES[rule.message]:
            issue('rule_reachable', label, f'{typed!r} (rule {rid}, key {raw!r}) got {got.rule_id if got else None!r}')
            continue
        generic = M.typed_examples(problem, at, raw, slot.slug, form)
        if any(M.read_user_scalar(at, t, form) == val and M.RULES_BY_ID[g].message != rule.message for g, t in generic):
            st['preempts'] += 1             # a generic rule would have said something else: the topic message won
        st['fired'][rid] += 1
        st['slot_rule_done'].add((rid, slot.label))
        st['slot_fired_near' if near else 'slot_fired'].add(slot.label)
        st['examples'].setdefault(rid, (slot.label, M.plain_text(problem.get('question'))[:90], raw, typed, got.message))
    for rid in applicable:
        st['applicable'][rid] += 1


def check_topic_questions(items):
    st = new_topic_state()
    for slot, run, problem in items:
        topic_item(slot, run, problem, st)
    return st


def topic_more_seeds(st, slots, first_seed, rounds=10):
    """Rarely drawn variants: more seeds, in the nine topics only, until every topic rule has fired or the rounds end.

    Review 2026-10-27: Phase 5b stopped this after 2.5 s, which made the topic slot count and the "every rule fires" check
    depend on the speed of the machine (635 slots and 8 unfired rules with no extra seeds, 640 and none with all of
    them). The rounds bound it now; it takes about 1 s.
    """
    for r in range(first_seed, first_seed + rounds):
        unfired = [rule for rule in T.RULES if not st['fired'][rule.id]]
        # Phase 3 batch A: the pair, box and expression rules of a rarely drawn variant need the extra seeds too
        unfired += [rule for rule in M._cd.PAIR_RULES + M._cd.PART_RULES + M._cd.EXPR_RULES if not st['cd']['fired'][rule.id]]
        if not unfired:
            break
        # only the practice slots that carry a family with a rule that has not fired yet (Phase 5: the pool was the nine topics)
        wanted = {fam for rule in unfired for fam in rule.families}
        carried = {fam: st['families'][fam] | st['cd']['families'][fam] for fam in wanted}
        labels = set().union(*carried.values()) if wanted else set()
        # once every wanted family is carried by some slot, only those slots can still fire the rule (Phase 1: this keeps
        # the rounds cheap, so that a rarely drawn die or coin question can be given enough of them)
        known = all(carried[fam] for fam in wanted)
        pool = [s for s in slots if s.label in labels or (not known and s.slug in NINE_TOPICS)]
        for s in pool:
            p, _ = harness.generate(s, r, record=False)
            if p.get('answer_record') is not None:
                topic_item(s, r, p, st)


def check_topic_rules_fire(st):
    for rule in T.RULES:
        n = st['fired'][rule.id]
        if n < EVERY_RULE_FIRES_AT_LEAST:
            issue('rule_reachable', rule.id, 'a topic rule that never fires on a generated question (dead rule or untested family)')
        app_n = st['applicable'][rule.id]
        if app_n and n / app_n < 0.5:
            issue('rule_reachable', rule.id, f'unambiguous on only {n}/{app_n} of its candidates (below 50%: review)')
    if st['records'] and len(st['guard_fail']) / st['records'] > GUARD_FAIL_SHARE_MAX:
        issue('rule_sound', 'guard', f'{len(st["guard_fail"])} of {st["records"]} records do not reproduce their key: '
                                     f'{st["guard_fail"][:4]}')
    for fam in sorted(T.FAMILIES):
        if fam not in st['families']:
            issue('rule_reachable', fam, 'a recorded family that no generated practice question carries')


# ─────────────────────────────────────────────────────────────────────────────
# the answer record itself: capture, size, session ceiling, storage, no drift
# ─────────────────────────────────────────────────────────────────────────────

SESSION_COOKIE_LIMIT = 4093         # a browser keeps a cookie of about 4,093 bytes
SESSION_CEILING = 3000              # the largest practice session problem we accept (measured max 2,727 with a record)
SESSION_GROWTH_MAX = 120            # the record may add at most this much to the compressed cookie


def _pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))] if xs else 0


def check_session_size(items):
    from app import app, _slim_problem_for_session
    ser = app.session_interface.get_signing_serializer(app)

    def cookie(problem, topic):
        return len(ser.dumps({'last_problem_payload': {
            'level': 'gcse', 'subject': 'maths', 'topic': topic, 'mode': 'standard', 'difficulty': 'foundational',
            'variant_name': problem.get('variant_name'), 'problem': _slim_problem_for_session(problem)}}))

    after, before, grow = [], [], []
    for slot, run, problem in items:
        a = cookie(problem, slot.slug)
        if 'answer_record' in problem:
            b = cookie({k: v for k, v in problem.items() if k != 'answer_record'}, slot.slug)
            grow.append(a - b)
        else:
            b = a
        after.append(a)
        before.append(b)
    out = {'n': len(after), 'p50': _pct(after, .5), 'p90': _pct(after, .9), 'max': max(after),
           'p50_before': _pct(before, .5), 'p90_before': _pct(before, .9), 'max_before': max(before),
           'records': len(grow), 'grow_max': max(grow) if grow else 0, 'grow_median': _pct(grow, .5)}
    if out['max'] > SESSION_CEILING:
        issue('session_size', 'ceiling', f'the largest practice session problem is {out["max"]} bytes (ceiling {SESSION_CEILING})')
    if out['grow_max'] > SESSION_GROWTH_MAX:
        issue('session_size', 'record', f'a record adds {out["grow_max"]} bytes to the cookie (limit {SESSION_GROWTH_MAX})')
    if out['max_before'] + AR.MAX_BYTES + 200 > SESSION_COOKIE_LIMIT:
        issue('session_size', 'headroom', 'the biggest question plus a full-size record could pass the cookie limit')
    return out


def check_record_unit():
    from generators.shared import verify_hook
    state = random.getstate()
    with verify_hook.capture() as cap:
        verify_hook.record('pyth_hyp', a=3, b=4)
    if len(cap) != 1 or cap[0]['family'] != 'pyth_hyp' or cap[0]['inputs'] != {'a': 3, 'b': 4}:
        issue('record', 'capture', f'capture() collected {cap!r}')
    verify_hook.record('pyth_hyp', a=3, b=4)             # outside any sink: a no-op
    with verify_hook.recording() as outer:
        with verify_hook.capture() as inner:
            verify_hook.record('pyth_hyp', a=3, b=4)
        verify_hook.record('pyth_hyp', a=5, b=12)
    if len(inner) != 1 or len(outer) != 2:
        issue('record', 'sinks', f'nested sinks lost records: capture {len(inner)}, recording {len(outer)}')
    with verify_hook.capture() as outer_c:
        with verify_hook.recording() as inner_r:
            verify_hook.record('pyth_hyp', a=3, b=4)
    if len(inner_r) != 1 or len(outer_c) != 1:
        issue('record', 'sinks', 'a verification run inside a capture lost a record')
    if random.getstate() != state:
        issue('record', 'rng', 'recording drew a random number')
    fams = M.RECORDED_FAMILIES
    good = {'family': 'pyth_hyp', 'inputs': {'a': 3, 'b': 4}}
    prob = {'answer_type': 'number', 'correct_answer_raw': '5'}
    if AR.build_record([good], prob, fams) != {'f': 'pyth_hyp', 'i': {'a': 3, 'b': 4}}:
        issue('record', 'build', 'a plain record was not built')
    for name, args in (
        ('two records', ([good, good], prob)), ('no record', ([], prob)),
        ('a multiple-choice question', ([good], dict(prob, options=['a', 'b']))),
        ('no key', ([good], {'answer_type': 'number', 'correct_answer_raw': None})),
        ('a multi-part answer', ([good], dict(prob, answer_type='number_fields'))),
        ('a family with no rule', ([{'family': 'nope', 'inputs': {'a': 1}}], prob)),
        ('an object that is not JSON', ([{'family': 'pyth_hyp', 'inputs': {'a': object()}}], prob)),
        ('more than 256 bytes', ([{'family': 'pyth_hyp', 'inputs': {'a': 'x' * 300}}], prob)),
        ('a list holding an object that is not JSON', ([{'family': 'pyth_hyp', 'inputs': {'a': [object()], 'b': 4}}], prob)),
        ('a one-step family with an unprinted input (review)',
         ([{'family': 'product', 'inputs': {'a': 2.7, 'b': 1000}, 'derived': ('b',)}], dict(prob, correct_answer_raw='2700'))),
    ):
        if AR.build_record(args[0], args[1], fams) is not None:
            issue('record', 'build', f'a record was built for {name}')
    tup = AR.build_record([{'family': 'pyth_hyp', 'inputs': {'a': (1, 2), 'b': 4}}], prob, fams)
    if tup != {'f': 'pyth_hyp', 'i': {'a': [1, 2], 'b': 4}}:
        issue('record', 'build', f'a tuple input became {tup!r}')
    p = {'question': 'q', AR.KEY: {'f': 'x', 'i': {}}}
    if AR.KEY in AR.public_problem(p) or AR.KEY not in p or AR.public_problem({'question': 'q'}) != {'question': 'q'}:
        issue('record', 'public_problem', 'public_problem must return a copy without the key and leave the original alone')
    # the wrapper: a fault inside it never breaks a question
    def maker(*a, **k):
        verify_hook.record('pyth_hyp', a=object(), b=4)
        return {'question': 'q', 'answer_type': 'number', 'correct_answer_raw': '5'}
    got = AR.with_answer_record(maker)()
    if AR.KEY in got or got != {'question': 'q', 'answer_type': 'number', 'correct_answer_raw': '5'}:
        issue('record', 'wrapper', f'a bad record changed the problem: {got!r}')


_SVG_COUNTER = re.compile(r'(sk-[a-z]+-)\d+')


def _steady(problem):
    """The problem as text, without the SVG element counters (they rise on every call, wrapped or not)."""
    return _SVG_COUNTER.sub(r'\1N', json.dumps(problem, sort_keys=True, default=str))


def check_wrapper_drift(items, slots):
    """The wrapped generator returns what the original returned, draws the same random numbers, and is the only change."""
    topics = harness.topics()
    by_key = {(s.label, r): p for s, r, p in items}
    unwrapped_calls = 0
    for n, slot in enumerate(slots):
        cfg = topics[slot.slug]
        wrapped = cfg['func']
        if not getattr(wrapped, '__wrapped_answer_record__', False) or not hasattr(wrapped, '__wrapped__'):
            issue('no_drift', slot.slug, 'the topic function is not wrapped by with_answer_record')
            continue
        cfg['func'] = wrapped.__wrapped__
        try:
            p0, _ = harness.generate(slot, 0, record=False)
            state0 = random.getstate()
        finally:
            cfg['func'] = wrapped
        unwrapped_calls += 1
        p1 = by_key.get((slot.label, 0))
        if p1 is None:
            continue
        # the one change the wrapper may make: an answer-box example that is the key is moved off it (review C1)
        from generators.shared.example_hint import keep_example_off_key
        p0 = keep_example_off_key(dict(p0))
        if _steady({k: v for k, v in p1.items() if k != AR.KEY}) != _steady(p0):
            issue('no_drift', slot.label, 'the wrapped generator returned a different problem from the original')
        if n % 4 == 0:
            harness.generate(slot, 0, record=False)
            if random.getstate() != state0:
                issue('no_drift', slot.label, 'the wrapper changed the random draws')
    # the generators themselves never mention the record, and no template or script ships it
    for path in list((ROOT / 'generators' / 'gcse').glob('*.py')):
        if 'answer_record' in path.read_text(encoding='utf-8'):
            issue('no_drift', path.name, 'a GCSE generator mentions answer_record (it is added by the registry wrapper only)')
    for path in list((ROOT / 'static').rglob('*.js')) + list((ROOT / 'templates').rglob('*.html')):
        if 'answer_record' in path.read_text(encoding='utf-8', errors='ignore'):
            issue('no_leak', path.relative_to(ROOT).as_posix(), 'the client code mentions answer_record')
    return unwrapped_calls


def check_record_storage(items):
    """No database write holds the record: saved, shared, suggested, challenge, Quick Test, lesson-quiz and set-work rows."""
    from unittest import mock
    from models import challenges, class_assignments, quicktest, sharing, user_data
    sample = next(p for s, r, p in items if p.get('answer_record') and p.get('question'))
    key = 'answer_record'

    def calls_of(fn, *args, **kw):
        conn = mock.MagicMock()
        row = {'n': 0, 'id': 1, 'class_id': 1, 'status': 'active', 'role': 'teacher'}
        conn.execute.return_value.fetchone.return_value = row
        conn.execute.return_value.fetchall.return_value = []
        conn.execute.return_value.lastrowid = 1
        conn.execute.return_value.rowcount = 1
        try:
            fn(conn, *args, **kw)
        except Exception:  # noqa: BLE001 - only the writes made before any later fault matter
            pass
        return [str(c) for c in conn.execute.call_args_list]

    writes = {
        'save_problem': calls_of(user_data.save_problem, 1, 'gcse', 'maths', 'bidmas', 'standard', 'foundational', sample),
        'update_saved_problem': calls_of(user_data.update_saved_problem, 1, 1, sample),
        'record_quiz_attempt': calls_of(user_data.record_quiz_attempt, 1, 'gcse', 'maths', 'bidmas', 1, 1, ['1'], [sample]),
        'create_shared_question': calls_of(sharing.create_shared_question, 1, 'gcse', 'maths', 'bidmas', 'standard', 'foundational', sample),
        'create_suggestion': calls_of(sharing.create_suggestion, 1, 2, 'gcse', 'maths', 'bidmas', 'standard', 'foundational', sample),
        'create_challenge': calls_of(challenges.create_challenge, 1, 2, 'gcse', 'maths', 'bidmas', [sample], seed=1),
        'save_quicktest_session': calls_of(quicktest.save_quicktest_session, 'sid', {'problems': [sample], 'answers': []}),
        'save_preview': calls_of(class_assignments.save_preview, 1, 1, level='gcse', subject='maths', topic='bidmas',
                                 mode='standard', difficulty='foundational', problems=[sample]),
        'create_assignment': calls_of(class_assignments.create_assignment, 1, 1, level='gcse', subject='maths', topic='bidmas',
                                      mode='standard', difficulty='foundational', problems=[sample], student_ids=[2]),
    }
    for name, calls in writes.items():
        text = '\n'.join(calls)
        if key in text:
            issue('no_leak', name, 'a database write holds answer_record')
        if 'correct_answer_raw' not in text:
            issue('no_leak', name, 'the write was not reached, so this check proved nothing (test setup)')
    # set work: the freeze copies no record, and nothing a pupil is sent holds one
    from app import _freeze_problem_payload
    frozen = _freeze_problem_payload(sample)
    if key in frozen:
        issue('no_leak', 'set work', 'a frozen set-work problem holds answer_record')
    # a problem the server holds in the lesson-quiz data is stripped before it is stored
    from app import _without_answer_records
    data = _without_answer_records({'problems': [sample], 'index': 0})
    if key in json.dumps(data, default=str):
        issue('no_leak', 'lesson quiz', 'the lesson-quiz row would hold answer_record')
    if key not in sample:
        issue('no_leak', 'test setup', 'the sample lost its record')         # the helpers above must copy, never edit


# ─────────────────────────────────────────────────────────────────────────────
# no_leak and no_drift
# ─────────────────────────────────────────────────────────────────────────────

def _functions_using(tree, names):
    found = set()
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(fn):
                if (isinstance(node, ast.Name) and node.id in names) or \
                        (isinstance(node, ast.ImportFrom) and node.module and node.module.endswith('misconceptions')):
                    found.add(fn.name)
    return found


def check_no_leak(items):
    # 1. only the check route reaches the module (set work, lesson quizzes, saved problems, cohorts never do)
    users = []
    for p in list(ROOT.glob('*.py')) + list((ROOT / 'models').glob('*.py')) + list((ROOT / 'generators').rglob('*.py')):
        if p.name == 'misconceptions.py':
            continue
        text = p.read_text(encoding='utf-8')
        if 'misconceptions' not in text:
            continue
        for node in ast.walk(ast.parse(text)):
            names = []
            if isinstance(node, ast.ImportFrom):
                names = [node.module or ''] + [a.name for a in node.names]
            elif isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            if any(n.split('.')[-1] == 'misconceptions' for n in names):
                users.append(p.relative_to(ROOT).as_posix())
                break
    app_tree = ast.parse((ROOT / 'app.py').read_text(encoding='utf-8'))
    where = _functions_using(app_tree, {'diagnose', 'misconceptions'})
    # nested helpers count as their parents: keep only functions that are routes
    if where != {'api_v1_problems_check'}:
        issue('no_leak', 'app.py', f'functions that call diagnose: {sorted(where)} (expected only api_v1_problems_check)')
    # 2. Flask: the check route
    from app import app, _problem_client_payload, _freeze_problem_payload
    from models.class_assignments import SERVER_ONLY_KEYS, grade_frozen_answer, strip_problem_keys
    bad_names = ('misconception', 'candidate', 'answer_record', 'option_notes', 'diagnos')
    messages = list(M.MESSAGES.values())

    sample = None
    for slot, run, problem in items:
        if slot.slug == 'geometry_angles' and problem.get('answer_type') == 'number' and problem.get('correct_answer_raw'):
            sample = (slot, problem)
            break
    assert sample, 'no geometry_angles number question to test with'
    slot, problem = sample
    key = Fraction(str(problem['correct_answer_raw']))
    wrong = M.format_answer(180 - key)

    def bind(client, prob, topic=slot.slug, subject='maths', level='gcse'):
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {'level': level, 'subject': subject, 'topic': topic, 'mode': 'practice',
                                            'difficulty': 'foundational', 'problem': prob}

    def stored(client):
        with client.session_transaction() as sess:
            return copy.deepcopy(sess.get('last_problem_payload'))

    with app.test_client() as client:
        hdr = {'Accept': 'application/json'}
        bind(client, problem)
        before = stored(client)
        r = client.post('/api/v1/problems/check', json={'user_answer': wrong}, headers=hdr)
        body = r.get_json()
        if r.status_code != 200 or body.get('correct') is not False:
            issue('no_leak', 'route', f'unexpected check response {r.status_code} {body}')
        elif body.get('feedback') != M.MESSAGES['ang.supplement'] or body.get('hint') != {'kind': 'misconception', 'id': 'ang.supplement'}:
            issue('no_leak', 'route', f'a wrong answer typed as 180 minus the key got {body.get("feedback")!r} {body.get("hint")!r}')
        if stored(client) != before:
            issue('no_leak', 'session', 'the session problem changed after a check (nothing may be stored)')
        extra = set(body) - {'ok', 'correct', 'normalized_user', 'normalized_correct', 'feedback', 'hint', 'cohort',
                             'practice_streak', 'attempt_id', 'score', 'score_total'}
        if extra:
            issue('no_leak', 'route', f'unexpected response keys {sorted(extra)}')
        # correct answer: no hint field, no message
        r = client.post('/api/v1/problems/check', json={'user_answer': str(problem['correct_answer_raw'])}, headers=hdr)
        body = r.get_json()
        if body.get('correct') is not True or 'hint' in body or body.get('feedback') in messages:
            issue('no_leak', 'route', f'a correct answer carried a hint or a message: {body}')
        # a key the client supplies, with no session problem: no diagnosis
        with client.session_transaction() as sess:
            sess.pop('last_problem_payload', None)
        r = client.post('/api/v1/problems/check', json={
            'user_answer': '350', 'correct_answer_raw': '35', 'answer_type': 'number',
            'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas'}, headers=hdr)
        body = r.get_json()
        if 'hint' in body or body.get('feedback') in messages or body.get('feedback') != 'Not quite. Check your working.':
            issue('no_leak', 'route', f'a client-supplied key was diagnosed: {body}')
        # another subject in the session: no diagnosis
        bind(client, {'correct_answer_raw': '35', 'answer_type': 'number', 'question': 'Find x.'}, topic='motion', subject='physics', level='gcse')
        body = client.post('/api/v1/problems/check', json={'user_answer': '350'}, headers=hdr).get_json()
        if 'hint' in body or body.get('feedback') in messages:
            issue('no_leak', 'route', f'a physics question was diagnosed: {body}')
        # a multi-part answer: the per-part path is diagnosed against that part's key only
        multi = next((p for s, r_, p in items if s.slug == 'geometry_angles' and p.get('answer_type') == 'number_fields'), None)
        if multi:
            raw = str(multi['correct_answer_raw'])
            sep = '\x1e' if '\x1e' in raw else '|'
            part0 = raw.split(sep)[0]
            bind(client, multi)
            body = client.post('/api/v1/problems/check', json={
                'user_answer': M.format_answer(180 - Fraction(part0)), 'correct_answer_raw': part0,
                'answer_type': 'number', 'part_index': 0, 'part_total': 1}, headers=hdr).get_json()
            if body.get('correct') is not False:
                pass            # 180 minus the part may equal another valid reading; only the leak shape matters here
            elif Fraction(part0) not in (Fraction(90),) and 'hint' not in body:
                issue('no_leak', 'route', f'a wrong angle in a multi-part answer was not diagnosed: {body}')
            # the whole multi-part answer is never diagnosed
            body = client.post('/api/v1/problems/check', json={'user_answer': '1|2|3|4'}, headers=hdr).get_json()
            if 'hint' in body or body.get('feedback') in messages:
                issue('no_leak', 'route', 'a whole multi-part answer was diagnosed')
        # the bearing note: a correct answer, feedback only (no hint object)
        bearing = next((p for s, r_, p in items if p.get('answer_type') == 'bearing'), None)
        if bearing:
            key_b = str(int(Decimal_str(bearing['correct_answer_raw'])) % 360)
            if int(key_b) < 100:
                bind(client, bearing, topic='bearings')
                body = client.post('/api/v1/problems/check', json={'user_answer': key_b}, headers=hdr).get_json()
                if body.get('correct') is not True or body.get('feedback') != M.MESSAGES['brg.three_figures'] or 'hint' in body:
                    issue('no_leak', 'route', f'the bearing note response is wrong: {body}')

    # 3. nothing in what a pupil is sent before answering, in set work, or in a lesson quiz payload
    for slot_, run, prob in items:
        if slot_.slug not in ('geometry_angles', 'bidmas', 'algebra', 'pythagoras', 'mensuration', 'number', 'trigonometry'):
            continue
        payload = _problem_client_payload(prob)
        blob = json.dumps(payload, default=str)
        for text in messages:
            if text in blob:
                issue('no_leak', f'{slot_.label}#{run}', 'a hint message is in the client payload before an answer')
        for k in payload:
            if any(b in k.lower() for b in bad_names):
                issue('no_leak', f'{slot_.label}#{run}', f'client payload key {k!r}')
        frozen = _freeze_problem_payload(prob)
        for revealed in (False, True):
            for k in strip_problem_keys(frozen, reveal=revealed):
                if any(b in k.lower() for b in bad_names):
                    issue('no_leak', f'{slot_.label}#{run}', f'set-work key {k!r} (reveal={revealed})')
        for k in prob:
            if k == 'answer_record':
                continue                    # the session problem holds it; every other place is tested here and below
            if any(b in k.lower() for b in bad_names):
                issue('no_leak', f'{slot_.label}#{run}', f'problem key {k!r}')
        if 'answer_record' in payload or 'answer_record' in frozen or 'answer_record' in strip_problem_keys(frozen, reveal=True):
            issue('no_leak', f'{slot_.label}#{run}', 'answer_record reached a client payload or a frozen set-work problem')
        if prob.get('answer_type') in M.SCALAR_TYPES and prob.get('correct_answer_raw') is not None:
            graded = grade_frozen_answer(frozen, '123456')
            if not (isinstance(graded, tuple) and len(graded) == 2):
                issue('no_leak', f'{slot_.label}#{run}', f'set-work grading returns {graded!r}')
    from app import grade_lesson_quiz_problem
    sample_q = next(p for s, r_, p in items if s.slug == 'bidmas' and p.get('answer_type') == 'number')
    graded = grade_lesson_quiz_problem(sample_q, '350')
    if any(any(b in k.lower() for b in bad_names + ('hint',)) for k in graded):
        issue('no_leak', 'lesson quiz', f'the quiz grading result carries {sorted(graded)}')
    if 'misconception' in json.dumps(graded, default=str).lower() or any(t in json.dumps(graded, default=str) for t in messages):
        issue('no_leak', 'lesson quiz', 'the quiz grading result carries a hint message')
    if SERVER_ONLY_KEYS and any('misconception' in k for k in SERVER_ONLY_KEYS):
        issue('no_leak', 'class_assignments', 'a misconception key was added to the stored set-work keys')
    from models.class_assignments import NOT_FROZEN_KEYS
    if 'answer_record' not in SERVER_ONLY_KEYS or 'answer_record' not in NOT_FROZEN_KEYS:
        issue('no_leak', 'class_assignments', 'answer_record must be a server-only key that set work never freezes')
    # the route reads the record from the session problem only
    with app.test_client() as client:
        hdr = {'Accept': 'application/json'}
        hyp = topic_problem('pyth_hyp', {'a': 3, 'b': 4}, 'number', '5', 'Find the hypotenuse.')
        bind(client, hyp, topic='pythagoras')
        before = stored(client)
        body = client.post('/api/v1/problems/check', json={'user_answer': '25'}, headers=hdr).get_json()
        if body.get('correct') is not False or body.get('hint') != {'kind': 'misconception', 'id': 'pyth.hyp_not_rooted'} \
                or body.get('feedback') != M.MESSAGES['gen.squared']:
            issue('no_leak', 'route', f'a topic slip in the session was not diagnosed by the check route: {body}')
        if 'answer_record' in json.dumps(body) or stored(client) != before:
            issue('no_leak', 'route', 'the check response or the session changed')
        # a record sent by the pupil is never trusted: the session problem has none
        bind(client, {k: v for k, v in hyp.items() if k != 'answer_record'}, topic='pythagoras')
        body = client.post('/api/v1/problems/check', json={
            'user_answer': '25', 'answer_record': {'f': 'pyth_hyp', 'i': {'a': 3, 'b': 4}}}, headers=hdr).get_json()
        if 'hint' in body or body.get('feedback') in messages:
            issue('no_leak', 'route', f'an answer_record sent by the client was used: {body}')
        CDT.check_routes(client, bind, stored, messages)
        # the practice question the pupil is sent has no record
        for topic in ('pythagoras', 'mensuration', 'number', 'trigonometry'):
            for difficulty in ('foundational', 'intermediate'):
                r = client.post('/api/v1/problems/generate', json={'level': 'gcse', 'subject': 'maths', 'topic': topic,
                                                                   'difficulty': difficulty}, headers=hdr)
                if r.status_code == 200 and ('answer_record' in r.get_data(as_text=True) or any(m in r.get_data(as_text=True) for m in messages)):
                    issue('no_leak', 'generate', f'{topic}/{difficulty} sent a pupil an answer record or a hint message')
    check_record_storage(items)


def Decimal_str(value):
    from decimal import Decimal
    return Decimal(str(value))


def check_no_drift(items):
    # diagnosis changes nothing, draws no random number, imports no generator
    problem = next(p for s, r, p in items if p.get('answer_type') == 'number' and p.get('correct_answer_raw'))
    before_problem = copy.deepcopy(problem)
    state = random.getstate()
    raw = str(problem['correct_answer_raw'])
    for typed in ('350', '-1', '0.1', raw + '0', 'abc'):
        res = check_answer('number', raw, typed)
        res_before = copy.deepcopy(res)
        run_diag(problem, 'number', raw, typed, topic='bidmas', result=res)
        if res != res_before:
            issue('no_drift', 'diagnose', 'the checker result was changed')
    if problem != before_problem:
        issue('no_drift', 'diagnose', 'the problem was changed')
    if random.getstate() != state:
        issue('no_drift', 'diagnose', 'diagnosis drew a random number')
    base_allowed = {'__future__', 'ast', 'html', 're', 'dataclasses', 'fractions', 'typing', 'generators', 'answer_checkers',
                    'math', 'decimal', 'json'}
    for fname, extra in (('misconceptions.py', {'misconception_topics', 'misconception_cd'}), ('misconception_topics.py', set()),
                         ('misconception_cd.py', {'misconception_topics', 'itertools', 'sympy', 'misconception_5b'}),
                         ('misconception_5b.py', {'misconception_topics'})):
        tree = ast.parse((ROOT / 'generators' / 'shared' / fname).read_text(encoding='utf-8'))
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                if fname == 'misconception_topics.py' and node.module == 'generators.shared' \
                        and [a.name for a in node.names] == ['misconception_cd']:
                    continue                    # the tail hook that adds the Phase 5 tables (checked as its own file)
                mods.add((node.module or '').split('.')[0] if node.level == 0 else '.')
                if node.module == 'generators.shared':
                    mods.update(a.name for a in node.names)
                if (node.module or '').startswith('generators') and not (node.module or '').startswith('generators.shared'):
                    mods.add(node.module)       # a question generator: never
        if fname == 'misconception_topics.py':
            allowed = base_allowed - {'generators', 'answer_checkers', 'ast', 'html'}
        elif fname in ('misconception_cd.py', 'misconception_5b.py'):
            allowed = (base_allowed | extra) - {'ast', 'html'}
        else:
            # Phase 4: graded_message reads the note of a picked option; answer_units (pure: re, html) drops a typed unit
            allowed = base_allowed | extra | {'option_notes', 'answer_units'}
        if mods - allowed:
            issue('no_drift', 'imports', f'{fname} imports {sorted(mods - allowed)} (no random, no generators, no database)')
        if 'random' in mods or 'sqlite3' in mods:
            issue('no_drift', 'imports', f'{fname}: random or sqlite3 imported')
    # D7: no GCSE-reachable checker string keeps the em dash
    src = (ROOT / 'generators' / 'shared' / 'answer_checkers.py').read_text(encoding='utf-8')
    cs_only = {'check_sql', 'check_python_run', 'check_text', 'check_binary', 'check_hex', '_python_run_check_result',
               'check_hex_value'}
    for fn in ast.parse(src).body:
        if isinstance(fn, ast.FunctionDef) and fn.name in cs_only:
            continue
        docs = set()
        for node in ast.walk(fn):
            if isinstance(node, (ast.FunctionDef, ast.Module)) and node.body and isinstance(node.body[0], ast.Expr) \
                    and isinstance(node.body[0].value, ast.Constant):
                docs.add(id(node.body[0].value))
        if isinstance(fn, ast.Expr) and isinstance(fn.value, ast.Constant):
            continue                    # module docstring
        for node in ast.walk(fn):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and '\u2014' in node.value \
                    and id(node) not in docs:
                issue('no_drift', getattr(fn, 'name', 'module level'), f'em dash left in {node.value[:60]!r} (D7)')
    seen_types = set()
    for slot, run, problem in items:
        at = problem.get('answer_type')
        raw = problem.get('correct_answer_raw')
        if at in (None, 'number_fields') or raw is None or at in seen_types or at in ('sql', 'python_run', 'text', 'binary', 'hex'):
            continue
        seen_types.add(at)
        try:
            fb = check_answer(at, str(raw), '987654.321', form=problem_answer_form(problem)).get('feedback') or ''
        except ValueError:
            continue
        if '—' in fb or '–' in fb:
            issue('no_drift', at, f'the feedback for a wrong {at} answer still has a dash: {fb!r}')
    n_checked = len(seen_types)
    # the strings the old tests asserted, in the new style
    r = check_answer('number', '35', '36')
    if r['feedback'] != 'Not quite. Check your working.':
        issue('no_drift', 'D7', f'check_number feedback is {r["feedback"]!r}')
    r = check_answer('quadratic_roots', '-4,-3', '1,2')
    if r['feedback'] != 'Not quite. Check both roots.':
        issue('no_drift', 'D7', f'check_quadratic_roots feedback is {r["feedback"]!r}')
    return n_checked


# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deep', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    seeds = 40 if args.deep else SEEDS_DEFAULT

    res = check_real_questions(seeds)
    check_rules_all_fire(res)
    check_unit_table()
    check_topic_table()
    CDT.check_tables()
    killed, total_rules = check_mutation()
    t_killed, t_total = check_topic_mutation()
    p_killed, p_total = CDT.check_mutation()
    items = [(s_, r_, p_) for s_, r_, p_ in res['items'] if r_ == 0]
    st = check_topic_questions(res['items'])
    slots_all = [s for s in harness.enumerate_slots() if s.mode == 'standard']
    topic_more_seeds(st, slots_all, seeds, rounds=30 if args.deep else 90)
    check_topic_rules_fire(st)
    CDT.check_rules_fire(st['cd'])
    far, right = check_negative_control(items)
    near_typed = check_near_key(items)
    check_copy({'examples': {**res['examples'], **st['examples'], **st['cd']['examples']}})
    check_no_leak(items)
    types_checked = check_no_drift(items)
    check_record_unit()
    wrapped_calls = check_wrapper_drift(items, slots_all)
    sizes = check_session_size(items)

    n_slots = res['slots']
    n_generic = len(res['slot_fired'])
    cd = st['cd']
    topic_slots = st['slot_fired'] | cd['slot_fired']
    # whole-change review 2026-11-03 (F9): slots whose only topic firing is next to the key are not counted
    near_only = (st['slot_fired_near'] | cd['slot_fired_near']) - topic_slots
    n_topic = len(topic_slots)
    n_union = len(res['slot_fired'] | topic_slots)
    n_hint = n_union
    n_types = len([t for t, n in res['type_fired'].items() if n])
    if n_generic < HINTS_FLOOR_SHARE * n_slots and not args.deep:
        issue('coverage', 'slots', f'{n_generic} practice slots can produce a generic hint, below the floor {HINTS_FLOOR_SHARE:.1%} of {n_slots}')
    if n_topic < TOPIC_FLOOR_SHARE * n_slots and not args.deep:
        issue('coverage', 'topic', f'{n_topic} practice slots can produce a topic hint, below the floor {TOPIC_FLOOR_SHARE:.1%} of {n_slots}')
    if n_union < COMBINED_FLOOR_SHARE * n_slots and not args.deep:
        issue('coverage', 'combined', f'{n_union} practice slots can produce any hint, below the floor {COMBINED_FLOOR_SHARE:.1%} of {n_slots}')
    if n_types < HINTS_FLOOR_TYPES and not args.deep:
        issue('coverage', 'types', f'{n_types} answer types can produce a hint, below the floor {HINTS_FLOOR_TYPES}')

    elapsed = time.time() - START
    summary = {
        'seeds_per_slot': seeds, 'questions': res['questions'], 'slots': n_slots,
        'slots_with_generic_hint': n_generic, 'slots_with_topic_hint': n_topic, 'slots_with_any_hint': n_union,
        'slots_with_any_hint_share': round(n_union / n_slots, 3), 'slots_with_topic_hint_share': round(n_topic / n_slots, 3),
        'slots_with_record': len(st['slot_record']),
        'slots_applicable': len(res['slot_applicable']),
        'answer_types_with_hint': sorted(t for t, n in res['type_fired'].items() if n),
        'rule_fires': {r.id: [res['fired'][r.id], res['applicable'][r.id], res['collided'][r.id]] for r in M.GENERIC_RULES},
        'topic_rule_fires': {r.id: [st['fired'][r.id], st['applicable'][r.id], st['collided'][r.id]] for r in T.RULES},
        'phase5_rule_fires': {r.id: [cd['fired'][r.id], cd['applicable'][r.id], cd['collided'][r.id]]
                              for r in M._cd.PAIR_RULES + M._cd.PART_RULES + M._cd.EXPR_RULES},
        'unit_cases': len(EXAMPLES) + len(other_cases()), 'topic_unit_cases': len(TX) + len(topic_cases()),
        'phase5_unit_cases': len(CDT.PAIR_TX) + len(CDT.PART_TX) + len(CDT.EXPR_TX) + len(CDT.DERIVE_TX) + len(CDT.other_cases()),
        'mutants_killed': f'{killed}/{total_rules}', 'topic_mutants_killed': f'{t_killed}/{t_total}',
        'phase5_mutants_killed': f'{p_killed}/{p_total}',
        'negative_control': {'far_answers': far, 'keys': right, 'near_key_answers': near_typed},
        'slots_with_topic_hint_only_near_key': sorted(near_only),
        'records': st['records'], 'record_bytes_max': max(st['sizes'] or [0]), 'guard_failures': len(st['guard_fail']),
        'session': sizes, 'checker_calls': res['checker_calls'] + st['checks'], 'seconds': round(elapsed, 1),
    }
    if args.json:
        print(json.dumps({'issues': ISSUES, 'summary': summary}, indent=2, default=str))
    else:
        print(f'GCSE maths hints (Phase 1 + 2): {res["questions"]} generated questions ({seeds} seeds x {n_slots} practice slots), '
              f'{summary["checker_calls"]} candidates checked, {elapsed:.1f}s (budget {BUDGET_SECONDS:g}s)')
        print(f'  slots that can produce a generic hint (Phase 1): {n_generic} of {n_slots} ({n_generic / n_slots:.0%}); '
              f'slots with a candidate at all: {len(res["slot_applicable"])}')
        print(f'  slots that can produce a topic hint (Phase 2): {n_topic} of {n_slots} ({n_topic / n_slots:.1%}) '
              f'({len(st["slot_record"])} slots carry an answer record; {len(near_only)} more fire only next to the key, '
              f'not counted)')
        print(f'  slots that can produce either: {n_union} of {n_slots} ({n_union / n_slots:.1%})')
        print(f'  answer types with a generic hint ({n_types}): ' + ', '.join(
            f'{t} {res["type_fired"][t]}/{res["type_applicable"][t]}' for t in sorted(summary["answer_types_with_hint"])))
        print('  generic rule: questions where it fired / questions with a candidate / collisions (same value, different message)')
        for r in M.GENERIC_RULES:
            print(f'    {r.id:26s} {res["fired"][r.id]:5d} / {res["applicable"][r.id]:5d} / {res["collided"][r.id]:4d}')
        print(f'  topic rules ({len(T.RULES)}, {len(T.FAMILIES)} recorded families): '
              f'{sum(1 for r in T.RULES if st["fired"][r.id])} fire on generated questions; '
              f'{sum(st["fired"].values())} unambiguous diagnoses, {sum(st["collided"].values())} silent collisions, '
              f'{st["preempts"]} where a generic rule would have said something else')
        p5 = M._cd.PAIR_RULES + M._cd.PART_RULES + M._cd.EXPR_RULES
        print(f'  pair, box and expression rules ({len(p5)}): {sum(1 for r in p5 if cd["fired"][r.id])} fire on generated '
              f'questions; {sum(cd["fired"].values())} unambiguous diagnoses, {sum(cd["collided"].values())} silent collisions, '
              f'{sum(cd["quiet"].values())} left quiet (printed in the question); {cd["records"]} records')
        print(f'  records: {st["records"]} on generated questions, at most {max(st["sizes"] or [0])} bytes; '
              f'{len(st["guard_fail"])} fail the truth guard (they fall back to the generic rules)')
        print(f'  session cookie, practice question (n={sizes["n"]}): p50 {sizes["p50"]} (before {sizes["p50_before"]}), '
              f'p90 {sizes["p90"]} ({sizes["p90_before"]}), max {sizes["max"]} ({sizes["max_before"]}) of about {SESSION_COOKIE_LIMIT}; '
              f'a record adds {sizes["grow_median"]} bytes (max {sizes["grow_max"]}) on {sizes["records"]} questions')
        print(f'  unit table: {len(EXAMPLES) + len(other_cases())} generic and {len(TX) + len(topic_cases())} topic hand-worked cases; '
              f'mutation: {killed} of {total_rules} generic, {t_killed} of {t_total} topic and {p_killed} of {p_total} '
              f'pair, box and expression perturbations caught')
        print(f'  negative control: {far} far-away wrong answers and {right} exact keys, none diagnosed; {near_typed} '
              f'values next to the key, none named by rounding a slip')
        print(f'  no_drift: {types_checked} answer types checked for dashes; {wrapped_calls} slots generated with and without the wrapper')
        if os.environ.get('HINTS_VERBOSE'):
            for rid, (label, q, raw, typed, msg) in sorted({**res['examples'], **st['examples'], **st['cd']['examples']}.items()):
                print(f'    e.g. {rid}: {q!r} key {raw} typed {typed} -> {msg}')
    if ISSUES:
        for check, lines in ISSUES.items():
            print(f'FAIL {check}: {len(lines)}')
            for line in lines[:12]:
                print(f'  {line}')
            if len(lines) > 12:
                print(f'  ... and {len(lines) - 12} more')
        sys.exit(1)
    if elapsed > HARD_LIMIT_SECONDS and not args.deep:
        print(f'FAIL budget: {elapsed:.1f}s is over the {HARD_LIMIT_SECONDS:g}s limit (budget {BUDGET_SECONDS:g}s)')
        sys.exit(1)
    if elapsed > BUDGET_SECONDS and not args.deep:
        print(f'  note: {elapsed:.1f}s is over the {BUDGET_SECONDS:g}s budget (machine load?)')
    print('GCSE maths hints smoke (Phase 1 + 2) passed.')


if __name__ == '__main__':
    main()
