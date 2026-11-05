"""Quick Test and set work drawn from the whole tier pool (docs/GCSE_MATHS_VARIETY.md, decision V8, Phase 3 batch C2).

A practice queue is 7 slots drawn from a tier's pool. A 10-question Quick Test or a 20-question piece of set work
built by cycling that queue repeats a kind of question by construction, whatever the pool holds. For GCSE maths
(``uses_whole_pool``) both now draw from every slot of the chosen topic and difficulty: no slot comes up twice until
the pool is exhausted, then the pool is shuffled afresh and the same kinds come round with new numbers. After Phase 3
every practice slot is its own strict kind (the verification smoke's variety check keeps D1 and D2 at 0), so "no
repeated slot" is "no repeated kind".

Multiple choice: a band's seven positional slots each draw at random from the band's entries, so the slot is not the
kind there. The draw still walks the slots without a repeat, and (GCSE maths only) also refuses a question whose kind
(``question_kind.quiz_kind``, the text with its numbers replaced) or source generator (``variant_utils.mcq_source``)
is already in the test, for a bounded number of extra draws, as the lesson quiz builder does.

Nothing here is stored: the Quick Test session and a frozen assignment hold the generated problems whole, exactly as
before, so sessions and set work created before this change carry on unchanged. The draw takes an ``rng`` so a test
can show that one seed gives one plan; the app passes none and stays unseeded.

Mixed difficulty (not offered by the app's pickers, but accepted by the web Quick Test form) draws from the union of
the three tiers' pools, each slot once and called with its own tier (``pool_with_tiers``), so a mixed test spans the
tiers without a repeat either and each question carries the tier it came from. Quick Test and set work are always
one topic, so there is no mixed-topic mode to handle.
"""
from __future__ import annotations

import random
import re

from generators.shared.question_kind import quiz_kind
from generators.shared.variant_utils import PRACTICE_TIERS, mcq_source, normalize_mode, reset_mcq_source, tier_pool

# Extra draws allowed per question before a repeated kind, source or identical text is accepted anyway (a thin
# multiple-choice band must still fill its ten questions).
KIND_ATTEMPTS = 6
_SPACES = re.compile(r'\s+')


def uses_whole_pool(level, subject):
    """GCSE maths Quick Tests and set work draw from the whole tier pool (decision V8); other subjects keep the queue."""
    return level == 'gcse' and subject == 'maths'


class PoolDraw:
    """Variant callables drawn from a pool: every slot once in a random order, then a fresh shuffle, and so on.

    A pool of one slot yields it every time (as the queue did). ``rng`` is any object with ``shuffle``."""

    def __init__(self, pool, rng=None):
        self._pool = list(pool)
        self._rng = rng or random
        self._order = []
        self.drawn = 0

    def __len__(self):
        return len(self._pool)

    def next(self):
        if not self._pool:
            return None
        if not self._order:
            self._order = list(self._pool)
            self._rng.shuffle(self._order)
            self._order.reverse()         # pop from the end keeps the shuffled order
        self.drawn += 1
        return self._order.pop()


def pool_with_tiers(variants_func, difficulty, mode):
    """``[(tier, variant callable)]`` for one (difficulty, mode): ``tier_pool`` with the tier each slot belongs to.

    For a difficulty outside the three tiers (mixed) the slots come from the union of the tiers' pools and each keeps
    its own tier, so the generator is called with a tier it knows: six topics (algebra, bidmas, decimals, fdp,
    multiples_factors, surds) have no practice pool for any other difficulty and raised on every draw (C2 review).
    """
    if difficulty in PRACTICE_TIERS:
        return [(difficulty, fn) for fn in tier_pool(variants_func, difficulty, mode)]
    out = []
    seen = set()
    for tier in PRACTICE_TIERS:
        for fn in tier_pool(variants_func, tier, mode):
            name = getattr(fn, '__name__', None)
            if name in seen:
                continue
            seen.add(name)
            out.append((tier, fn))
    return out


def _question_key(problem):
    return _SPACES.sub(' ', str((problem or {}).get('question') or '').strip())


def _usable(problem, accept):
    if not isinstance(problem, dict) or not problem.get('question'):
        return False
    return accept(problem) if accept else True


def generate_from_pool(generator, variants_func, difficulty, mode, count, *, rng=None, accept=None,
                       kind_check=False, attempts=KIND_ATTEMPTS):
    """``count`` problems of one topic drawn from the whole (difficulty, mode) pool. Returns [(problem, variant name)].

    ``accept`` (optional) says whether a generated problem can be used (set work needs a gradable one); a refused
    problem costs one draw and the next slot is tried. ``kind_check`` also refuses a repeated kind or source
    generator while ``attempts`` extra draws remain for the question (multiple-choice bands). An identical question
    text is refused the same way in every mode. A pool with no variants falls back to the plain generator.
    """
    mode = normalize_mode(mode)
    pool = pool_with_tiers(variants_func, difficulty, mode) if variants_func else []
    draw = PoolDraw(pool, rng)
    out = []
    seen_text = set()
    seen_kinds = set()
    for _i in range(count):
        chosen = None
        for attempt in range(attempts + 1):
            if not pool:
                problem = _call(generator, difficulty, mode, None)
                name = None
            else:
                tier, fn = draw.next()
                name = getattr(fn, '__name__', None)
                reset_mcq_source()
                problem = _call(generator, tier, mode, name)
            if not _usable(problem, accept):
                continue
            text = _question_key(problem)
            if text in seen_text and attempt < attempts:
                continue
            kind = source = None
            if kind_check:
                kind = quiz_kind(problem)
                source = mcq_source()
                if (kind in seen_kinds or (source is not None and ('source', source) in seen_kinds)) and attempt < attempts:
                    continue
            chosen = (problem, name, text, kind, source)
            break
        if chosen is None:
            raise ValueError('generate_failed')
        problem, name, text, kind, source = chosen
        seen_text.add(text)
        if kind is not None:
            seen_kinds.add(kind)
        if source is not None:
            seen_kinds.add(('source', source))
        out.append((problem, name))
    return out


def _call(generator, difficulty, mode, variant_name):
    try:
        if variant_name is None:
            try:
                return generator(difficulty, mode, variant_name=None)
            except TypeError:
                return generator(difficulty, mode)
        return generator(difficulty, mode, variant_name=variant_name)
    except ValueError:
        return None
