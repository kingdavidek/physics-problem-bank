"""GCSE maths answer verification - run: python scripts/test_gcse_maths_verification_smoke.py

The structural test (test_gcse_maths_correctness_smoke.py) proves generators run and their solutions
are internally consistent.  This one re-solves each question from the numbers the generator recorded
(generators/shared/verify_hook.py) with independent solvers (scripts/gcse_verify/) and compares the
result with the key.  See docs/GCSE_MATHS_VERIFICATION.md.

Checks: practice re-solve, MCQ key, checker round-trip, ordered-proof orders, stated accuracy, properties, no-output-drift.

Options: --deep (many more seeds, run by hand), --only NAME[,NAME] (check names or substrings),
--seed N (offsets the run numbers), --json (machine-readable summary), --print-digests (static MCQ
item digests, for updating register.py after a reviewed change).
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
from gcse_verify import core, engine, forms, harness, mcq, ordering, register, report  # noqa: E402
from gcse_verify import (solvers_algebra, solvers_geometry, solvers_number, solvers_probability,  # noqa: E402,F401
                         solvers_loci, solvers_shapes, solvers_stats, solvers_transform, solvers_vectors)  # (register the solvers)
from gcse_verify.latex import plain  # noqa: E402
from gcse_verify.registry import DIAGRAM_CHECKS  # noqa: E402

PKG = ROOT / 'scripts' / 'gcse_verify'
# The modules that compute or compare expected answers: every solvers_*.py plus the shared comparison code.
SOLVER_MODULES = tuple(sorted({'core.py', 'latex.py', 'registry.py', 'engine.py'}
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

# A question that fixes how a probability is written cannot take the probability form (which accepts 25%).
PROBABILITY_FORM_FIXED = re.compile(r'as a (fraction|decimal|percentage)|simplest form|lowest terms|decimal place|d\.p\.',
                                    re.I)

# SVG helpers number their title/desc ids from a process-wide counter, which differs between any two runs.
SVG_COUNTER = re.compile(r'(sk-[a-z]+)-\d+')

ISSUES = {}          # check name -> [message]
TALLY = {}


def issue(check, where, detail):
    ISSUES.setdefault(check, []).append(f'{where}: {detail}')


def settings(args):
    if args.deep:
        return dict(practice=200, practice_algebra=200, mcq_direct=40, procedural=100, drift=3, roundtrip=20)
    return dict(practice=20, practice_algebra=14, mcq_direct=4, procedural=8, drift=3, roundtrip=5)


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


def check_register(slots):
    topics = set(harness.topics())
    declared = set(register.VERIFIED_TOPICS) | set(register.PENDING_TOPICS)
    if set(register.VERIFIED_TOPICS) & set(register.PENDING_TOPICS):
        issue('register', 'topics', 'a topic is both verified and pending')
    for t in sorted(topics - declared):
        issue('register', t, 'topic is in neither VERIFIED_TOPICS nor PENDING_TOPICS (classify it)')
    for t in sorted(declared - topics):
        issue('register', t, 'registered topic no longer exists')
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
    for t in mcq.BANK_REFS:
        if t not in register.VERIFIED_TOPICS:
            issue('register', t, 'static bank mapped for a topic that is not verified')
    for t in register.VERIFIED_TOPICS:
        slot_names = {s.fn for s in slots if s.slug == t and s.mode == 'mcq'}
        dispatch = {n for n in slot_names if '_mcq_' in n}
        if t not in mcq.DIRECT_TOPICS and dispatch and t not in mcq.BANK_REFS:
            issue('register', t, 'MCQ dispatch slots but no static bank registered')


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

    # Generate once, share across the checks.
    cache = []          # (slot, run, problem, outcome)
    need_practice = any(want(n) for n in ('practice', 'roundtrip', 'accuracy', 'negative', 'answer_form', 'ordering'))
    if need_practice:
        for s in practice:
            n_seeds = cfg['practice_algebra'] if s.slug in register.ALGEBRA_TOPICS else cfg['practice']
            for r in range(base, base + n_seeds):
                try:
                    p, recs = harness.generate(s, r)
                except Exception as exc:                    # a crash is a finding, not a skip
                    issue('practice_resolve', f'{s.label}#{r}', f'generator raised {exc!r}')
                    continue
                outcome = engine.verify_problem(p, recs)
                outcome.records = recs
                cache.append((s, r, p, outcome))

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
                    if o.status != 'verified':
                        for kind, msg in o.findings or [('norecord', 'no record() call reached')]:
                            issue('mcq_key', f'{slug}/{fn.__name__}#{r}', f'[{kind}] {msg}')
                    else:
                        for m in keys_exact_or_stated(o.problem, o):
                            issue('stated_accuracy', f'{slug}/{fn.__name__}#{r}', m)
        tally['procedural_functions'] = n_proc

        pinned = 0
        for slug in sorted(mcq.BANK_REFS):
            digests = set()
            for i, item in enumerate(mcq.bank(slug)):
                d = mcq.item_digest(item)
                digests.add(d)
                for m in mcq.item_structure_errors(item):
                    issue('mcq_key', f'{slug} bank item {i} ({d})', m)
                if d in register.STATIC_ITEMS.get(slug, ()):
                    pinned += 1
                else:
                    issue('mcq_key', f'{slug} bank item {i}', f'not reviewed: digest {d} is not pinned in register.STATIC_ITEMS '
                          f'(check the key by hand, then update the digest; question: {plain(item.get("q", ""))[:70]!r})')
            for d in register.STATIC_ITEMS.get(slug, ()):
                if d not in digests:
                    issue('mcq_key', f'{slug}', f'pinned digest {d} matches no bank item (item changed or removed)')
        tally['pinned_items'] = pinned
        tally['mcq_dispatch_slots'] = len(dispatch)

    # 3. checker round-trip
    if want('roundtrip') or want('answer_form'):
        n = 0
        n_wrong_form = 0
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

            def chk(name, key, typed, _ft=ftypes, _form=form, _subject=subject):
                # the app passes the question's field types to number_fields, and the stored problem's
                # written form and subject letter to the other checkers (app.py). Mixed-type keys
                # (equation and pair fields) are typed by the web form, so a plain-text echo is judged
                # with and without the types and passes if either accepts it; rejections use the types.
                res = check_answer(name, key, typed, form=_form, subject=_subject)
                if _ft and not res['correct']:
                    res = CHECKERS[name](key, typed, field_types=_ft)
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
            elif (s.slug == 'probability' and at in ('fraction', 'number')
                  and forms.FORM_QUESTION_WORDS['probability'].search(text)
                  and (lambda v: v is not None and 0 <= v <= 1)(forms._num(raw))):
                want_form = 'probability'       # "Find P(...)": a percentage is accepted as well
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
                    shown = text + ' ' + ' '.join(plain(str(o)) for o in p.get('options') or [])
                    for what, pat in COSMETIC.items():
                        m = pat.search(shown)
                        if m:
                            issue('properties', s.label, f'{what}: {shown[max(0, m.start() - 25):m.end() + 25]!r}')
                for m in unordered_box_errors(p):
                    issue('properties', s.label, m)
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

    tally['seconds'] = round(time.time() - t0, 1)
    return slots, tally


CHECK_NAMES = ('independence', 'register', 'solvers', 'practice_resolve', 'mcq_key', 'checker_roundtrip', 'ordering', 'overlap_outcomes',
               'answer_form', 'stated_accuracy', 'negative_control', 'properties', 'no_output_drift')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deep', action='store_true')
    ap.add_argument('--only', default='')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--print-digests', action='store_true')
    args = ap.parse_args()

    if args.print_digests:
        for slug in sorted(mcq.BANK_REFS):
            print(slug, sorted(mcq.item_digest(i) for i in mcq.bank(slug)))
        return

    wanted = [w for w in args.only.split(',') if w]
    t0 = time.time()
    slots_all = harness.enumerate_slots()
    if not wanted or any(w in 'independence' for w in wanted):
        check_independence()
    if not wanted or any(w in 'register' for w in wanted):
        check_register(slots_all)
    if not wanted or any(w in 'solvers' for w in wanted):
        check_solver_table()
    slots, tally = run_checks(args, wanted)
    total = round(time.time() - t0, 1)

    cov = report.coverage(slots, {
        'practice_verified': tally.get('practice_verified', 0),
        'mcq_direct_verified': tally.get('mcq_direct_verified', 0),
        'procedural_functions': tally.get('procedural_functions', 0),
        'pinned_items': tally.get('pinned_items', 0),
        'mcq_dispatch_slots': tally.get('mcq_dispatch_slots', 0),
    })
    if args.json:
        print(json.dumps({'issues': ISSUES, 'tally': tally, 'coverage': cov, 'seconds': total}, indent=2, default=str))
    else:
        print(f'GCSE maths verification: {tally.get("practice_questions", 0)} practice questions, '
              f'{tally.get("roundtrip_questions", 0)} checker round-trips '
              f'({tally.get("wrong_form_questions", 0)} with a required form), '
              f'{tally.get("drift_generations", 0)} drift generations, {total}s')
        if 'ordering_questions' in tally:
            print(f'  ordered proofs: {tally["ordering_questions"]} questions in {tally["ordering_slots"]} slots, '
                  f'{tally["ordering_with_alternatives"]} with alternative orders '
                  f'({tally["ordering_slots_with_alternatives"]} slots)')
        print(report.render(cov))
        if 'negative_control' in tally:
            print(f'  negative control (tampered keys caught): {tally["negative_control"]}')
            print(f'  negative control (damaged drawings caught, by family): {tally.get("diagram_negative_control", "n/a")}')
        n_issues = sum(len(v) for v in ISSUES.values())
        if n_issues:
            print(f'{n_issues} issue(s):')
            for name in CHECK_NAMES:
                rows = ISSUES.get(name, [])
                if not rows:
                    continue
                print(f'  [{name}] {len(rows)}')
                for row in rows[:12]:
                    print(f'    {row}')
                if len(rows) > 12:
                    print(f'    ... and {len(rows) - 12} more')
    if total > 45:
        print(f'WARNING: run took {total}s (target 30s or less)')
    if ISSUES:
        sys.exit(1)
    if not args.json:
        print('All GCSE maths verification checks passed.')


if __name__ == '__main__':
    main()
