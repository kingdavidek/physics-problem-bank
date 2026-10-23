"""Coverage report for the verification register."""
from __future__ import annotations

from collections import Counter, defaultdict


def coverage(slots, tallies):
    """Per-topic and overall counts. ``tallies`` holds the numbers the checks gathered."""
    from . import register
    per = defaultdict(Counter)
    for s in slots:
        if s.slug in register.VERIFIED_TOPICS:
            per[s.slug][f'{s.mode}_slots'] += 1
        else:
            per[s.slug]['pending'] += 1
    total = Counter()
    for c in per.values():
        total.update(c)
    return {'topics': {k: dict(v) for k, v in sorted(per.items())}, 'total': dict(total), **tallies}


def render(cov):
    t = cov['total']
    lines = [
        'Coverage (slots = topic/tier/variant):',
        f"  practice slots verified by re-solve : {cov.get('practice_verified', 0)} of {t.get('standard_slots', 0)}",
        f"  MCQ slots verified directly         : {cov.get('mcq_direct_verified', 0)}",
        f"  MCQ dispatch slots (bank + procedural): {cov.get('mcq_dispatch_slots', 0)} slots covered by "
        f"{cov.get('procedural_functions', 0)} procedural functions and {cov.get('pinned_items', 0)} pinned static items",
        f"  pending slots                       : {t.get('pending', 0)}",
    ]
    return '\n'.join(lines)
