"""Coverage tables for the verification register: how much of each topic is re-solved by a solver.

Practice: a slot is fully verified when its recorded inputs are re-solved on every seed (the exemptions are slots
that are not).  MCQ: a slot that wraps one procedural generator is verified directly.  A dispatch slot draws one
entry at random from a pool (the static bank items of its tier, plus the procedural generators in the difficult
tier), so its verified share is the fraction of that pool that is re-solved; it is "strictly" verified only when
the whole pool is.  The headline MCQ percentage is the strict one; the mean verified share over all MCQ slots (the
share of generated questions that a solver re-checks) is printed beside it.  "Pinned" items are static items kept by digest only.
"""
from __future__ import annotations

from collections import defaultdict

from . import harness, mcq, register, solvers_bank

TIERS = harness.TIERS


def band_slots(slug, tier):
    """{slot name: (entries, concept)} for the MCQ slots of a dispatch topic's band, read from the variants the app
    builds (so this is what a pupil can be served): ``entries`` are the bank items (dicts) and procedural
    generators (callables) the slot draws from at random; ``concept`` is True for the band's concept slot, the one
    that serves only the reviewed definitions (register.CONCEPT_SLOTS, docs/GCSE_MATHS_VARIETY.md 5.3)."""
    variants = harness.topics()[slug]['variants_func'](tier, 'mcq') or []
    return {v.__name__: (list(getattr(v, '_mcq_entries', None) or []), bool(getattr(v, '_mcq_concept', False)))
            for v in variants}


def dispatch_pool(slug, tier):
    """(bank items the band can serve, procedural generators it can serve) for a dispatch topic's band."""
    entries = []
    for ents, _ in band_slots(slug, tier).values():
        for e in ents:
            if not any(e is x for x in entries):
                entries.append(e)
    return [e for e in entries if not callable(e)], [e for e in entries if callable(e)]


def digest_of(item):
    return mcq.item_digest(item)


_BAND_CACHE = {}


def band_slots_cached(slug, tier):
    if (slug, tier) not in _BAND_CACHE:
        _BAND_CACHE[(slug, tier)] = band_slots(slug, tier)
    return _BAND_CACHE[(slug, tier)]


def mcq_shares(slots, resolved, direct_topics):
    """Per-topic MCQ numbers. ``resolved`` is the set of static item digests that a solver re-solves."""
    per = defaultdict(lambda: defaultdict(float))
    for s in slots:
        if s.mode != 'mcq' or s.slug not in register.VERIFIED_TOPICS:
            continue
        row = per[s.slug]
        row['slots'] += 1
        if s.slug in direct_topics or s.slug not in mcq.BANK_REFS:
            row['direct'] += 1
            row['share'] += 1.0
            row['strict'] += 1
            continue
        entries, concept = band_slots_cached(s.slug, s.tier).get(s.fn, ([], False))
        done = sum(1 for it in entries if callable(it) or digest_of(it) in resolved)
        total = len(entries) or 1
        row['dispatch'] += 1
        row['share'] += done / total
        row['strict'] += 1 if done == total else 0
        row['concept'] += 1 if concept and done < total else 0
    return per


def static_counts(resolved):
    out = {}
    for slug in mcq.BANK_REFS:
        items = mcq.bank(slug)
        done = sum(1 for it in items if digest_of(it) in resolved)
        out[slug] = (done, len(items))
    return out


def practice_counts(slots, exempt_keys):
    per = defaultdict(lambda: [0, 0])
    for s in slots:
        if s.mode != 'standard' or s.slug not in register.VERIFIED_TOPICS:
            continue
        per[s.slug][1] += 1
        if f'{s.slug}/{s.mode}/{s.fn}' not in exempt_keys:
            per[s.slug][0] += 1
    return per


def tables(slots, resolved, exempt_keys, direct_topics):
    """Structured coverage: per topic and in total, for practice and MCQ."""
    practice = practice_counts(slots, exempt_keys)
    shares = mcq_shares(slots, resolved, direct_topics)
    statics = static_counts(resolved)
    topics = {}
    for slug in sorted(register.VERIFIED_TOPICS):
        p = practice.get(slug, [0, 0])
        m = shares.get(slug, {})
        d, n = statics.get(slug, (0, 0))
        topics[slug] = {
            'practice_verified': p[0], 'practice_slots': p[1],
            'mcq_slots': int(m.get('slots', 0)), 'mcq_share': round(m.get('share', 0.0), 2),
            'mcq_strict': int(m.get('strict', 0)), 'mcq_concept': int(m.get('concept', 0)),
            'static_resolved': d, 'static_items': n,
        }
    tot = defaultdict(float)
    for t in topics.values():
        for k, v in t.items():
            tot[k] += v
    return {'topics': topics, 'total': dict(tot)}


def pct(a, b):
    return f'{100 * a / b:.1f}%' if b else 'n/a'


def render(cov):
    t = cov['total']
    lines = [
        'Coverage by topic (practice slots re-solved | MCQ slots re-solved, mean share of pool | static bank items re-solved):',
        f"  {'topic':34} {'practice':>10} {'MCQ share':>10} {'strict':>7} {'concept':>8} {'static':>9}",
    ]
    for slug, r in cov['topics'].items():
        lines.append(f"  {slug:34} {r['practice_verified']:>4}/{r['practice_slots']:<5} "
                     f"{pct(r['mcq_share'], r['mcq_slots']):>10} {r['mcq_strict']:>3}/{r['mcq_slots']:<3} "
                     f"{r['mcq_concept']:>6}   {r['static_resolved']:>4}/{r['static_items']:<4}")
    lines.append(f"  {'TOTAL':34} {int(t['practice_verified']):>4}/{int(t['practice_slots']):<5} "
                 f"{pct(t['mcq_share'], t['mcq_slots']):>10} {int(t['mcq_strict']):>3}/{int(t['mcq_slots']):<3} "
                 f"{int(t['mcq_concept']):>6}   {int(t['static_resolved']):>4}/{int(t['static_items']):<4}")
    lines.append(f"  fully verified: practice {pct(t['practice_verified'], t['practice_slots'])}, "
                 f"MCQ {pct(t['mcq_strict'], t['mcq_slots'])} of slots strictly (every question a slot can serve is "
                 f"re-solved; {int(t['mcq_concept'])} more are concept slots that serve the reviewed definitions, "
                 f"register.CONCEPT_SLOTS); MCQ pool share {pct(t['mcq_share'], t['mcq_slots'])} "
                 f"(static items {pct(t['static_resolved'], t['static_items'])})")
    return '\n'.join(lines)


def resolved_digests():
    return set(solvers_bank.SPECS)
