"""Slot enumeration and seeded generation for the GCSE maths verification test."""
from __future__ import annotations

import contextlib
import io
import random
import zlib
from typing import NamedTuple

from generators.shared import variant_utils, verify_hook
from topic_registry import TOPICS

TIERS = ('foundational', 'intermediate', 'difficult')
MODES = ('standard', 'mcq')
ENUMERATION_SEEDS = 40


class Slot(NamedTuple):
    slug: str
    tier: str
    mode: str
    fn: str

    @property
    def key(self):            # register key: tier-independent, mode-independent
        return f'{self.slug}/{self.fn}'

    @property
    def label(self):
        return f'{self.slug}/{self.tier}/{self.fn}'


def topics():
    return TOPICS['gcse']['maths']


# Building a topic's MCQ queue asks variant_utils whether each slot rerolls, which runs the slot's generator up
# to 8 times. That answer never changes the question that is then generated, but the probing is about a sixth
# of the run. The test remembers it per slot function (keyed by name and source line, never by id, so a run is
# reproducible): the first call, made while enumerate_slots warms up, probes as before; later builds do not, so
# every seeded generation after that is deterministic and probe-free. Pupil-facing code is unchanged.
_RANDOMIZABLE = {}
_probe_randomizable = variant_utils.variant_is_randomizable


def _remembered_randomizable(fn, *args, **kwargs):
    if args or kwargs:
        return _probe_randomizable(fn, *args, **kwargs)
    code = getattr(fn, '__code__', None)
    key = (getattr(fn, '__module__', None), getattr(fn, '__qualname__', None), getattr(fn, '__name__', None),
           code.co_firstlineno if code is not None else None)
    if key not in _RANDOMIZABLE:
        _RANDOMIZABLE[key] = _probe_randomizable(fn)
    return _RANDOMIZABLE[key]


variant_utils.variant_is_randomizable = _remembered_randomizable


_SLOTS = []


def enumerate_slots():
    """Every (topic, tier, mode, variant function) slot, found by sampling the variant queues (cached per process)."""
    if _SLOTS:
        return list(_SLOTS)
    out = []
    for slug, cfg in topics().items():
        for mode in MODES:
            for tier in TIERS:
                names = []
                for i in range(ENUMERATION_SEEDS):
                    random.seed(i)
                    for v in cfg['variants_func'](tier, mode) or []:
                        if v.__name__ not in names:
                            names.append(v.__name__)
                out.extend(Slot(slug, tier, mode, n) for n in names)
    _SLOTS.extend(out)
    return out


def slot_seed(slot, run):
    return zlib.crc32(f'{slot.slug}/{slot.tier}/{slot.fn}'.encode()) + run


def _make_choice(state):
    original = random.choice

    def choice(seq):
        try:
            if len(seq) > 1 and all(isinstance(e, (tuple, list)) and len(e) >= 2 for e in seq):
                return seq[state['row'] % len(seq)]
        except TypeError:
            pass
        return original(seq)

    return original, choice


def generate(slot, run=0, seed=None, record=True):
    """Generate one problem for ``slot``. Returns (problem, records).

    Hard-coded tables are walked row by row (``run`` picks the row), as in the structural test.
    """
    state = {'row': run}
    original, choice = _make_choice(state)
    random.seed(slot_seed(slot, run) if seed is None else seed)
    random.choice = choice
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            if record:
                with verify_hook.recording() as sink:
                    p = topics()[slot.slug]['func'](slot.tier, slot.mode, variant_name=slot.fn)
                return p, list(sink)
            return topics()[slot.slug]['func'](slot.tier, slot.mode, variant_name=slot.fn), []
    finally:
        random.choice = original


def generate_callable(slug, fn, seed):
    """Run one procedural MCQ function (a 6-tuple generator) as a problem. Returns (problem, records)."""
    from generators.shared.utils import make_problem
    random.seed(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        with verify_hook.recording() as sink:
            q, sol, hint, marks, opts, ans = fn()
        p = make_problem(q, sol, hint, 'difficult', marks, 'gcse', 'maths', slug,
                         options=opts, correct_answer=ans)
    return p, list(sink)
