"""Variety metrics for GCSE maths practice and multiple-choice questions (docs/GCSE_MATHS_VARIETY.md, section 2).

What a pupil meets, not whether it is right: how many genuinely different kinds of question a tier offers, how
often a seven-question practice queue repeats a kind, how many kinds a multiple-choice band serves, and how often
a lesson quiz asks the same kind twice.  Everything here reads problems the verification smoke has already
generated (practice, quizzes) or enumerates the pools structurally (the static MCQ banks); the only generation it
does itself is 4 fixed-seed draws per directly generated MCQ slot.

Definitions (the plan's section 2):

* template: the question text with HTML and SVG removed, LaTeX flattened, every number replaced by ``#``,
  capitalised words outside a short function-word list by ``@``, one to three capitals by ``L`` and single
  lower-case letters by ``v``.  Two questions with the same template differ only in numbers, names or letters.
* D1 exact duplicate: two slots of one tier that call the same helper (found from the source: a one-line
  ``return helper(args)`` with the same call, or a wrapper of another slot of the tier).
* D2 sibling: not D1, but the same set of templates and the same record families over the sampled seeds.
* strict kinds of a tier: its slots after merging D1 and D2 (reviewed pairs in ``register.VARIETY_EXEMPT`` stay apart).
* queue repeat share: the exact probability that ``select_tier_variants`` (7 distinct slots drawn from the pool, or
  the whole pool cycled when it has fewer than 7) gives two slots of one strict kind.

This is a test helper, not a solver, so it may import the generators.
"""
from __future__ import annotations

import ast
import collections
import linecache
import inspect
import itertools
import math
import re
import sys
import textwrap

from generators.shared import question_kind

from . import harness, mcq, register

TIERS = harness.TIERS
QUEUE_LENGTH = 7
MCQ_SAMPLES_PER_SLOT = 4          # fixed-seed draws per directly generated MCQ slot (not offset by --seed or --deep)
MCQ_SAMPLE_BASE = 9000

flat = question_kind.flat                   # the text work lives in generators/shared/question_kind.py (the quiz builder uses it)
template = question_kind.template
KEEP = question_kind.KEEP


# ─────────────────────────────────────────────────────────────────────────────
# Where the generator functions live (the one-module rule) and one-line wrappers
# ─────────────────────────────────────────────────────────────────────────────

def generator_functions():
    """{name: [(module, function)]} for every module-level function defined in a loaded GCSE generator module."""
    out = collections.defaultdict(list)
    for modname, mod in list(sys.modules.items()):
        if not modname.startswith('generators.gcse') or mod is None:
            continue
        for name, obj in list(vars(mod).items()):
            if callable(obj) and getattr(obj, '__name__', None) == name and getattr(obj, '__module__', None) == modname:
                out[name].append((modname, obj))
    return out


_SOURCE_DEFS = {}


def defining_modules(name, root):
    """Source files under generators/ that define ``name`` at module level (``def`` or an assignment)."""
    if not _SOURCE_DEFS:
        for path in sorted((root / 'generators').rglob('*.py')):
            text = path.read_text(encoding='utf-8')
            for m in re.finditer(r'^(?:async\s+def|def)\s+(\w+)|^(\w+)\s*=(?!=)', text, re.M):
                _SOURCE_DEFS.setdefault(m.group(1) or m.group(2), []).append(str(path.relative_to(root)))
    return _SOURCE_DEFS.get(name, [])


def _function_source(fn):
    """Source lines of a module-level function (decorators included), read from the line cache."""
    code = getattr(inspect.unwrap(fn), '__code__', None)
    if code is None:
        return None
    lines = linecache.getlines(code.co_filename)
    start = code.co_firstlineno - 1
    if not lines or start >= len(lines):
        return None
    first = lines[start]
    base = len(first) - len(first.lstrip())
    block = [first]
    seen_def = first.lstrip().startswith('def ')
    for line in lines[start + 1:]:
        text = line.lstrip()
        if text and len(line) - len(text) <= base and not text.startswith(')'):
            if text.startswith('def ') and not seen_def:
                seen_def = True                 # the def line under a decorator
            elif not (text.startswith('@') and not seen_def):
                break
        block.append(line)
    return textwrap.dedent(''.join(block))


def call_key(fn):
    """Source of the call a one-line wrapper returns (``return helper(args)``), else None."""
    src = _function_source(fn)
    if not src or src.count('\n') > 10:             # a wrapper is a few lines; skip parsing long bodies
        return None
    try:
        node = ast.parse(src).body[0]
    except (SyntaxError, IndexError):
        return None
    body = [b for b in getattr(node, 'body', [])
            if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]       # skip a docstring
    if len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Call):
        return ast.unparse(body[0].value)
    return None


def canonical_keys(names, functions):
    """{name: key}: slots of one tier with the same key are exact duplicates (D1)."""
    raw = {}
    for n in names:
        fns = functions.get(n) or []
        raw[n] = call_key(fns[0][1]) if fns else None
    pool = set(names)

    def key(n, seen=()):
        k = raw.get(n)
        if k is None or n in seen:
            return ('self', n)
        m = re.fullmatch(r'(\w+)\(\)', k)
        if m and m.group(1) in pool and m.group(1) != n:        # a wrapper of another slot of the tier
            return key(m.group(1), seen + (n,))
        return ('call', k)

    return {n: key(n) for n in names}


# ─────────────────────────────────────────────────────────────────────────────
# Practice
# ─────────────────────────────────────────────────────────────────────────────

def profiles(cache):
    """{slot: {'tpls': set, 'fams': set, 'texts': set, 'n': int}} from the smoke's generated practice problems."""
    out = {}
    for slot, _run, p, outcome in cache:
        row = out.setdefault(slot, {'tpls': set(), 'fams': set(), 'texts': set(), 'n': 0})
        row['n'] += 1
        q = str(p.get('question', ''))
        row['tpls'].add(template(q))
        row['texts'].add(flat(q))
        for rec in getattr(outcome, 'records', None) or []:
            row['fams'].add(rec['family'] + ':' + ','.join(sorted(rec['inputs'])))
    return out


def _find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def classes(names, keys, prof, slug, tier, exempt, deferred=None, near=None):
    """(D1 classes, D1+deferred classes, D1+deferred+D2 classes) as lists of name lists for one tier.

    ``deferred`` ('slug/tier/a+b' keys, register.VARIETY_DEFERRED) are reviewed siblings whose merge waits for a later
    phase: they always count as one kind, whatever the sampled templates show, and are not reported as D2."""
    deferred = register.VARIETY_DEFERRED if deferred is None else deferred
    parent = {n: n for n in names}
    by_key = collections.defaultdict(list)
    for n in names:
        by_key[keys[n]].append(n)
    for group in by_key.values():
        for n in group[1:]:
            parent[_find(parent, n)] = _find(parent, group[0])
    d1 = collections.defaultdict(list)
    for n in names:
        d1[_find(parent, n)].append(n)
    d1_only = list(d1.values())
    prefix = f'{slug}/{tier}/'
    for key in deferred:
        if key.startswith(prefix):
            a, _, b = key[len(prefix):].partition('+')
            if a in parent and b in parent:
                parent[_find(parent, a)] = _find(parent, b)
    d1 = collections.defaultdict(list)
    for n in names:
        d1[_find(parent, n)].append(n)
    d1_classes = list(d1.values())
    # D2: the same templates and the same record families over the sampled seeds
    sig = {}
    for c in d1_classes:
        tpls, fams = set(), set()
        for n in c:
            row = prof.get(n)
            if row:
                tpls |= row['tpls']
                fams |= row['fams']
        sig[c[0]] = (frozenset(tpls), frozenset(fams)) if tpls else None
    parent2 = {c[0]: c[0] for c in d1_classes}
    for a, b in itertools.combinations([c[0] for c in d1_classes], 2):
        if sig[a] is None or sig[a] != sig[b]:
            continue
        if f'{slug}/{tier}/' + '+'.join(sorted((a, b))) in exempt:
            continue
        parent2[_find(parent2, a)] = _find(parent2, b)
    d2 = collections.defaultdict(list)
    for c in d1_classes:
        d2[_find(parent2, c[0])].extend(c)
    # reviewed near-duplicates (register.VARIETY_NEAR_DUPLICATES, review C6) count as one kind after D2
    near = register.VARIETY_NEAR_DUPLICATES if near is None else near
    parent3 = {c[0]: c[0] for c in list(d2.values())}
    d2_list = list(d2.values())
    root_of = {n: c[0] for c in d2_list for n in c}
    for key in near:
        if key.startswith(prefix):
            a, _, b = key[len(prefix):].partition('+')
            if a in root_of and b in root_of:
                parent3[_find(parent3, root_of[a])] = _find(parent3, root_of[b])
    merged = collections.defaultdict(list)
    for c in d2_list:
        merged[_find(parent3, c[0])].extend(c)
    return d1_only, d1_classes, d2_list, list(merged.values())


MIN_ECHO_TEMPLATE = 30            # shorter templates ("Calculate #") are too generic to call an echo


def template_echoes(slots, by_slot):
    """Whole-change review C7: [(slug, tier, slot, lower tier, lower slot)] where a slot asks a question whose template
    (and record family) also occurs in a slot of a LOWER tier of the same topic.

    ``echo_slots`` only sees one-line wrappers that call one helper from two tiers; a slot with its own body that
    asks the same question never counted, so "no echo into a difficult tier" could not be measured.  Templates are
    read from the sampled draws, so a slot with a few templates can echo through one of them."""
    rows = collections.defaultdict(dict)            # (slug, tier) -> {fn: ({templates}, {families})}
    for s in slots:
        row = by_slot.get(s)
        if not row:
            continue
        tpls = {t for t in row['tpls'] if len(t) >= MIN_ECHO_TEMPLATE}
        fams = {f.split(':', 1)[0] for f in row['fams']}
        if tpls:
            rows[(s.slug, s.tier)][s.fn] = (tpls, fams)
    out = []
    for (slug, tier), fns in sorted(rows.items()):
        for lower in TIERS[:TIERS.index(tier)]:
            for fn, (tpls, fams) in sorted(fns.items()):
                for lfn, (ltpls, lfams) in sorted(rows.get((slug, lower), {}).items()):
                    if tpls & ltpls and fams & lfams:
                        out.append((slug, tier, fn, lower, lfn))
    return out


def queue_repeat(class_sizes, n_slots, length=QUEUE_LENGTH):
    """Exact probability that a queue of ``length`` slots repeats a kind (one kind = one class of slots)."""
    if n_slots < length:
        return 1.0                      # the pool is cycled, so some slot (and kind) comes up twice
    poly = [1] + [0] * length           # elementary symmetric polynomial of the class sizes
    for s in class_sizes:
        for k in range(length, 0, -1):
            poly[k] += poly[k - 1] * s
    return 1.0 - poly[length] / math.comb(n_slots, length)


def practice(slots, cache, exempt=None):
    """The practice side of the report.

    ``slots``: standard-mode Slot tuples; ``cache``: [(slot, run, problem, outcome)] from the smoke.
    Returns {'tiers': {(slug, tier): {...}}, 'totals': {...}, 'd2_groups': [...], 'echo_slots': n, 'fixed': [...]}.
    """
    exempt = register.VARIETY_EXEMPT if exempt is None else exempt
    functions = generator_functions()
    by_slot = profiles(cache)           # keyed by Slot, so tier-specific; the D2 test compares names inside one tier
    tiers = {}
    d2_groups = []
    by_topic_key = collections.defaultdict(lambda: collections.defaultdict(set))
    for slug in sorted({s.slug for s in slots}):
        for tier in TIERS:
            names = [s.fn for s in slots if s.slug == slug and s.tier == tier]
            if not names:
                continue
            keys = canonical_keys(names, functions)
            tier_prof = {s.fn: by_slot[s] for s in slots if s.slug == slug and s.tier == tier and s in by_slot}
            d1o, d1c, d2c, nkc = classes(names, keys, tier_prof, slug, tier, exempt)
            sizes = [len(c) for c in nkc]
            tiers[(slug, tier)] = {
                'slots': len(names), 'd1': len(names) - len(d1o), 'deferred': len(d1o) - len(d1c),
                'd2': len(d1c) - len(d2c), 'near': len(d2c) - len(nkc), 'kinds': len(nkc), 'repeat': queue_repeat(sizes, len(names)),
            }
            for c in d2c:
                members = {tuple(sorted(x)) for x in d1c if set(x) <= set(c)}
                if len(members) > 1:
                    d2_groups.append((slug, tier, sorted(c)))
            for n in names:
                if keys[n][0] == 'call':
                    by_topic_key[slug][keys[n][1]].add((tier, n))
    tpl_echoes = template_echoes(slots, by_slot)
    echo_slots = 0                      # a helper used in k tiers is k - 1 echoes
    for groups in by_topic_key.values():
        for members in groups.values():
            echo_slots += max(len({t for t, _ in members}) - 1, 0)
    fixed = sorted((s.label for s in slots if s in by_slot and len(by_slot[s]['texts']) <= 2 and by_slot[s]['n'] >= 2))
    n = len(tiers)
    totals = {
        'slots': sum(t['slots'] for t in tiers.values()), 'tiers': n,
        'd1': sum(t['d1'] for t in tiers.values()), 'd2': sum(t['d2'] for t in tiers.values()),
        'deferred': sum(t['deferred'] for t in tiers.values()), 'near': sum(t['near'] for t in tiers.values()),
        'tiers_below9': sorted(f'{k[0]}/{k[1]}={t["kinds"]}' for k, t in tiers.items() if t['kinds'] < 9),
        'kinds': sum(t['kinds'] for t in tiers.values()),
        'below7': sum(1 for t in tiers.values() if t['kinds'] < QUEUE_LENGTH),
        'below9': sum(1 for t in tiers.values() if t['kinds'] < 9),
        'slots_below7': sum(1 for t in tiers.values() if t['slots'] < QUEUE_LENGTH),
        'repeat_mean': sum(t['repeat'] for t in tiers.values()) / max(n, 1),
        'repeat_always': sum(1 for t in tiers.values() if t['repeat'] >= 0.9999),
        'echo_slots': echo_slots, 'fixed': len(fixed),
        'tpl_echo_slots': len({(a, b, c) for a, b, c, _, _ in tpl_echoes}),
        'tpl_echo_difficult': len({(a, b, c) for a, b, c, _, _ in tpl_echoes if b == 'difficult'}),
    }
    return {'tiers': tiers, 'totals': totals, 'd2_groups': d2_groups, 'fixed': fixed, 'template_echoes': tpl_echoes}


# ─────────────────────────────────────────────────────────────────────────────
# Multiple choice
# ─────────────────────────────────────────────────────────────────────────────

def mcq_samples(slots, per_slot=MCQ_SAMPLES_PER_SLOT):
    """{(slug, tier): [(family, template)]} from fixed-seed draws of every directly generated MCQ slot."""
    out = collections.defaultdict(list)
    for s in slots:
        if s.mode != 'mcq' or s.slug not in mcq.DIRECT_TOPICS or s.slug not in register.VERIFIED_TOPICS:
            continue
        for i in range(per_slot):
            try:
                p, recs = harness.generate(s, MCQ_SAMPLE_BASE + i)
            except Exception:                       # a crash is reported by the MCQ key check, not here
                continue
            out[(s.slug, s.tier)].append((recs[-1]['family'] if recs else '', template(p.get('question', ''))))
    return out


def mcq_bands(slots, proc_samples, per_slot=MCQ_SAMPLES_PER_SLOT):
    """{(slug, tier): {'kinds': set, 'bank': n, 'proc': n}} for every MCQ band.

    A band of a topic with a static bank is enumerated structurally from the entries its slots can draw (read from
    the variants the app builds: the bank items, and the procedural generators placed in the band): the template of
    each bank item, and the (family, template) pairs of each procedural generator, read from ``proc_samples``
    ({slug: {function name: [(family, template)]}}, the draws the smoke made).  A direct topic's band is read from
    fixed-seed draws of its slots.
    """
    from . import coverage
    direct = mcq_samples(slots, per_slot)
    out = {}
    for slug in sorted({s.slug for s in slots if s.mode == 'mcq'}):
        for tier in TIERS:
            if slug in mcq.BANK_REFS:
                pool, procs = coverage.dispatch_pool(slug, tier)
                bank_kinds = {('bank', '', template(it.get('q', ''))) for it in pool}
                proc_kinds = set()
                for fn in procs:
                    proc_kinds |= {('proc', fam, tpl) for fam, tpl in proc_samples.get(slug, {}).get(fn.__name__, [])}
                out[(slug, tier)] = {'kinds': bank_kinds | proc_kinds, 'bank': len(bank_kinds), 'proc': len(proc_kinds),
                                     'bank_only': not procs, 'sampled': False}
            else:
                kinds = {('proc', fam, tpl) for fam, tpl in direct.get((slug, tier), [])}
                out[(slug, tier)] = {'kinds': kinds, 'bank': 0, 'proc': len(kinds), 'bank_only': False, 'sampled': True}
    return out


BLIND_JACCARD = 0.6


def band_blind_topics(bands):
    """Topics whose three bands serve (nearly) the same kinds: every pair of bands shares at least BLIND_JACCARD of
    its kinds (a topic that ignores the band, such as statistics, shows 0.8 and more because bands drawn from fixed
    seeds differ by chance; bands with their own questions share nothing or little)."""
    out = []
    for slug in sorted({s for s, _ in bands}):
        sets = [{(k[1], k[2]) for k in bands[(slug, t)]['kinds']} for t in TIERS if (slug, t) in bands]
        if len(sets) == 3 and all(len(a & b) / max(len(a | b), 1) >= BLIND_JACCARD for a, b in itertools.combinations(sets, 2)):
            out.append(slug)
    return out


def mcq_summary(bands):
    counts = sorted(len(b['kinds']) for b in bands.values())
    return {
        'bands': len(bands), 'median': counts[len(counts) // 2] if counts else 0, 'min': counts[0] if counts else 0,
        'below5': sum(1 for c in counts if c < 5), 'below7': sum(1 for c in counts if c < 7),
        'bank_only': sum(1 for b in bands.values() if b['bank_only']), 'identical_topics': band_blind_topics(bands),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Quizzes
# ─────────────────────────────────────────────────────────────────────────────

def quiz_kinds(problems, records=None, key_of=None):
    """The kind of every question of one quiz, as the quiz builder sees it: the template of the question text
    (generators/shared/question_kind.py, which ``lesson_quiz`` uses to refuse a second question of one kind).  The
    figure in the report is therefore the behaviour pupils get."""
    return [question_kind.quiz_kind(p) for p in problems]


def quiz_kinds_by_family(problems, records, key_of):
    """The older, finer measure (Phases 0 and 1, kept for comparison): bank items by template, generated ones by
    (record family, template).  A quiz with no repeat by ``quiz_kinds`` has none by this either."""
    out = []
    for p in problems:
        recs = records.get(key_of(p)) or []
        tpl = template(p.get('question', ''))
        generated = bool(recs) and recs[-1]['family'] != 'bank'
        out.append(f"proc:{recs[-1]['family']}|{tpl}" if generated else f'bank:{tpl}')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Report and ratchets
# ─────────────────────────────────────────────────────────────────────────────

QUEUE_REPEAT_SLACK = 0.005      # the ceiling on the mean queue-repeat share may sit this far above the measured value


def ratchet_issues(pr, bands, tight=False):
    """Messages when a variety ratchet in register.py is broken.  Enforcing from Phase 1.

    ``tight`` (the default verification run only: seed offset 0, default sampling) also fails a floor that sits below
    what is measured, or a tier or band with no floor: a ratchet that never binds would let a later change lose
    variety unnoticed.  Floors of bands read from fixed-seed draws may sit one under the measured value."""
    out = []
    if tight:
        floors = register.VARIETY_FLOORS
        for (slug, tier), t in sorted(pr['tiers'].items()):
            floor = floors['tier_kinds'].get(f'{slug}/{tier}')
            if floor is None:
                out.append(f'{slug}/{tier}: no floor in VARIETY_FLOORS["tier_kinds"] (measured {t["kinds"]})')
            elif floor < t['kinds']:
                out.append(f'{slug}/{tier}: the floor {floor} is below the measured {t["kinds"]} strict kinds (raise it: '
                           f'a ratchet only rises)')
        for (slug, tier), b in sorted(bands.items()):
            floor = floors['mcq_kinds'].get(f'{slug}/{tier}')
            slack = 1 if b['sampled'] else 0
            if floor is None:
                out.append(f'{slug}/{tier} MCQ: no floor in VARIETY_FLOORS["mcq_kinds"] (measured {len(b["kinds"])})')
            elif floor < len(b['kinds']) - slack:
                out.append(f'{slug}/{tier} MCQ: the floor {floor} is below the measured {len(b["kinds"])} kinds (raise it)')
        if floors['queue_repeat_mean_max'] > pr['totals']['repeat_mean'] + QUEUE_REPEAT_SLACK:
            out.append(f'queue repeat ceiling {floors["queue_repeat_mean_max"]} is above the measured '
                       f'{pr["totals"]["repeat_mean"]:.3f} by more than {QUEUE_REPEAT_SLACK} (lower it)')
    for (slug, tier), t in sorted(pr['tiers'].items()):
        if t['d1']:
            out.append(f'{slug}/{tier}: {t["d1"]} slots are exact duplicates of another slot of the tier '
                       f'(retire them: register.RETIRED)')
        if t['d2']:
            out.append(f'{slug}/{tier}: {t["d2"]} slots are siblings of another slot of the tier '
                       f'(merge them, or list the pair in register.VARIETY_EXEMPT with a reason)')
        floor = register.VARIETY_FLOORS['tier_kinds'].get(f'{slug}/{tier}', 0)
        if t['kinds'] < floor:
            out.append(f'{slug}/{tier}: {t["kinds"]} strict kinds, below the floor {floor}')
    for (slug, tier), b in sorted(bands.items()):
        floor = register.VARIETY_FLOORS['mcq_kinds'].get(f'{slug}/{tier}', 0)
        if len(b['kinds']) < floor:
            out.append(f'{slug}/{tier} MCQ: {len(b["kinds"])} kinds, below the floor {floor}')
    ceiling = register.VARIETY_FLOORS['queue_repeat_mean_max']
    if pr['totals']['repeat_mean'] > ceiling:
        out.append(f'queue repeat share {pr["totals"]["repeat_mean"]:.3f} is above the ceiling {ceiling}')
    return out


def quiz_repeat_issues(counts):
    """Messages for the quiz kind ratchet: the ceiling over the topics that have enough kinds, and every topic listed
    in ``register.QUIZ_THIN_TOPICS`` must still repeat (else the entry is stale and must go)."""
    out = []
    m = quiz_repeat_issue(counts)
    if m:
        out.append(m)
    counts = counts or {}
    for slug in sorted(register.QUIZ_THIN_TOPICS):
        n = counts.get(f'thin_quizzes:{slug}', 0)
        if n and not counts.get(f'thin_repeated:{slug}', 0):
            out.append(f'{slug} is in QUIZ_THIN_TOPICS but none of its {n} quizzes repeated a kind: remove the entry')
    return out


def quiz_repeat_issue(counts):
    """A message when more lesson quizzes repeat a kind than ``VARIETY_FLOORS['quiz_repeat_max']`` allows, else None."""
    n = (counts or {}).get('quizzes') or 0
    ceiling = register.VARIETY_FLOORS['quiz_repeat_max']
    if n and counts['repeated'] / n > ceiling:
        return (f'{counts["repeated"]} of {n} lesson quizzes ask two questions of one kind '
                f'({100 * counts["repeated"] / n:.1f}%), above the ceiling {100 * ceiling:.0f}%')
    return None


def render(pr, bands, quiz_counts=None):
    t = pr['totals']
    ms = mcq_summary(bands)
    lines = [
        'Variety (docs/GCSE_MATHS_VARIETY.md):',
        f"  practice: {t['slots']} slots in {t['tiers']} tiers, {t['kinds']} strict kinds "
        f"(D1 exact duplicates {t['d1']}, D2 siblings {t['d2']}, siblings deferred to a later phase {t['deferred']}, reviewed near-duplicates merged {t['near']}); tiers below 7 kinds {t['below7']}, below 9 kinds {t['below9']}; "
        f"tiers below 7 slots {t['slots_below7']}" + (f"; below 9: {', '.join(t['tiers_below9'])}" if t['tiers_below9'] else ''),
        f"  practice queues (7 questions) that repeat a kind: mean {100 * t['repeat_mean']:.1f}% over tiers, "
        f"{t['repeat_always']} tiers repeat in every queue; tier echoes {t['echo_slots']} slots; fixed variants {t['fixed']}",
        f"  MCQ: {ms['bands']} bands, kinds per band median {ms['median']}, minimum {ms['min']}, below 5: {ms['below5']}, "
        f"below 7: {ms['below7']}; bank-only bands {ms['bank_only']}; topics with identical kinds in every band "
        f"{len(ms['identical_topics'])}",
    ]
    if quiz_counts and quiz_counts.get('quizzes'):
        q = quiz_counts
        total = q['quizzes'] + q.get('thin_quizzes', 0)
        thin = sum(v for k, v in q.items() if k.startswith('thin_repeated:'))
        lines.append(f"  lesson quizzes ({q['quizzes']} built by the sweep, topics with ten kinds or more): "
                     f"{100 * q['repeated'] / q['quizzes']:.1f}% have two questions of one kind; mean "
                     f"{q['distinct_kinds'] / total:.2f} distinct kinds in 10 over all {total}; "
                     f"{thin} of {q.get('thin_quizzes', 0)} in the thin topics (register.QUIZ_THIN_TOPICS) repeat one; "
                     f"{100 * q.get('source_repeated', 0) / total:.1f}% ask two questions from one generator")
    lines.append(f"  template echoes (a slot whose question template and record family occur in a lower tier of its topic; "
                 f"listed by --variety-report, reviewed in docs/GCSE_MATHS_VARIETY.md section 23): {t['tpl_echo_slots']} slots, "
                 f"{t['tpl_echo_difficult']} of them in a difficult tier")
    for slug, tier, names in pr['d2_groups']:
        lines.append(f'  merged by the sibling rule (D2): {slug}/{tier}: {", ".join(names)}')
    return '\n'.join(lines)


def full_tables(pr, bands):
    """The section 1.2 / 1.3 style tables for ``--variety-report`` (slots / strict kinds per tier, MCQ kinds per band)."""
    rows = ['Practice, per topic: slots / strict kinds / queue repeat share for F, I, D']
    for slug in sorted({s for s, _ in pr['tiers']}):
        cells = []
        for tier in TIERS:
            t = pr['tiers'].get((slug, tier))
            cells.append(f"{t['slots']}/{t['kinds']}/{100 * t['repeat']:.0f}%" if t else '-')
        rows.append(f'  {slug:34} ' + '  '.join(f'{c:>14}' for c in cells))
    rows.append('Template echoes (slot of the higher tier : slot of a lower tier of the same topic with the same template and family)')
    for slug, tier, fn, lower, lfn in pr.get('template_echoes', []):
        rows.append(f'  {slug}/{tier}/{fn}  =  {lower}/{lfn}')
    rows.append('MCQ kinds per band (F, I, D)  [* sampled from fixed seeds, others enumerated from the pools]')
    for slug in sorted({s for s, _ in bands}):
        cells = []
        for tier in TIERS:
            b = bands[(slug, tier)]
            cells.append(f"{len(b['kinds'])}{'*' if b['sampled'] else ''}")
        rows.append(f'  {slug:34} ' + '  '.join(f'{c:>6}' for c in cells))
    return '\n'.join(rows)
