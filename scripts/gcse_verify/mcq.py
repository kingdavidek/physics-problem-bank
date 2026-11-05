"""MCQ coverage: pinned static bank items, structural checks and the procedural MCQ functions."""
from __future__ import annotations

import hashlib
import re
from fractions import Fraction

from . import exact, harness, options
from .engine import parse_options, verify_problem
from .core import norm_text, parse_num
from .latex import plain

BANK_REFS = {
    'bidmas': ('generators.gcse.maths_basic_topics_mcq', '_BIDMAS_MCQ_BANK'),
    'fdp': ('generators.gcse.maths_basic_topics_mcq', '_FDP_MCQ_BANK'),
    'multiples_factors': ('generators.gcse.maths_basic_topics_mcq', '_MF_MCQ_BANK'),
    'decimals': ('generators.gcse.maths_basic_topics_mcq', '_DEC_MCQ_BANK'),
    'pythagoras': ('generators.gcse.maths_pythagoras', '_PY_MCQ_BANK'),
    'compound_measures': ('generators.gcse.maths_compound_measures', '_CM_MCQ_BANK'),
    'mensuration': ('generators.gcse.maths_mensuration', '_MENS_MCQ_BANK'),
    'bearings': ('generators.gcse.maths_bearings', '_BRG_MCQ_BANK'),
    'trigonometry': ('generators.gcse.maths', '_TRIG_MCQ_BANK'),
    'algebra': ('generators.gcse.maths_basic_topics_mcq', '_ALG_MCQ_BANK'),
    'surds': ('generators.gcse.maths_basic_topics_mcq', '_SURD_MCQ_BANK'),
    'equations_inequalities': ('generators.gcse.equations_inequalities', '_EQ_INEQ_MCQ_BANK'),
    'sequences': ('generators.gcse.sequences', '_SEQ_MCQ_BANK'),
    'simultaneous_equations': ('generators.gcse.simultaneous_equations', '_SIM_MCQ_BANK'),
    'geometry_angles': ('generators.gcse.geometry_angles', '_GEOM_MCQ_BANK'),
    'transformations': ('generators.gcse.transformations', '_TRANS_MCQ_BANK'),
    'circle_theorems': ('generators.gcse.maths_circle_theorems', '_CT_MCQ_BANK'),
    'similarity_congruence': ('generators.gcse.maths_similarity_congruence', '_SC_MCQ_BANK'),
    'constructions_loci': ('generators.gcse.maths_constructions_loci', '_CL_MCQ_BANK'),
    'vectors': ('generators.gcse.maths', '_VECTORS_MCQ_BANK'),
}

# Topics whose MCQ slots wrap a procedural generator directly (verified slot by slot).
DIRECT_TOPICS = (
    'number', 'ratio_proportion', 'changing_the_subject', 'completing_the_square',
    'quadratic_simultaneous_equations', 'graphical_simultaneous_equations', 'graphs', 'algebraic_fractions',
    'functions', 'algebraic_proof', 'statistics', 'probability',
)


# Where the written MCQ generators of the direct topics are placed (docs/GCSE_MATHS_VARIETY.md 5.1): slug ->
# (module, name of the dict of band lists, what the topic has written).  The reach check fails when a generator
# written for the topic is in no band's list, so a generator can never again be written and never asked.
#   ('types', n): types 1..n of the generator function, a band list holds type numbers
#   ('index', n): positions 0..n-1 of a generator list, a band list holds positions
#   ('pool', name): the functions of a pool list in the module, a band list holds functions
REACH = {
    'number': ('generators.gcse.maths_num_stats_prob_rat', '_NUMBER_MCQ_BANDS', ('types', 18)),
    'ratio_proportion': ('generators.gcse.maths_num_stats_prob_rat', '_RATIO_MCQ_BANDS', ('types', 12)),
    'statistics': ('generators.gcse.maths_num_stats_prob_rat', '_STATISTICS_MCQ_BANDS', ('index', 'statistics')),
    'probability': ('generators.gcse.maths_num_stats_prob_rat', '_PROBABILITY_MCQ_BANDS', ('index', 'probability')),
    'changing_the_subject': ('generators.gcse.changing_the_subject', '_CTS_MCQ_BANDS', ('pool', '_CTS_MCQ_POOL')),
    'completing_the_square': ('generators.gcse.completing_the_square', '_CTSQ_MCQ_BANDS', ('pool', '_CTSQ_MCQ_POOL')),
    'graphical_simultaneous_equations': ('generators.gcse.graphical_simultaneous_equations', '_GSIM_MCQ_BANDS',
                                         ('pool', '_GSIM_MCQ_POOL')),
    'algebraic_fractions': ('generators.gcse.algebraic_fractions', '_AF_MCQ_BANDS', ('pool', '_AF_MCQ_POOL')),
    'functions': ('generators.gcse.functions', '_FN_MCQ_BANDS', ('pool', '_FN_MCQ_POOL')),
    'quadratic_simultaneous_equations': ('generators.gcse.quadratic_simultaneous_equations', '_QSIM_MCQ_BANDS',
                                         ('pool', '_QSIM_MCQ_POOL')),
}


def reach(slug):
    """(written, placed, per-band sets) for a direct topic: what was written and what the bands can serve."""
    import importlib
    modname, bands_name, (kind, what) = REACH[slug]
    mod = importlib.import_module(modname)
    bands = getattr(mod, bands_name)
    if kind == 'types':
        written = set(range(1, what + 1))
    elif kind == 'index':
        written = set(range(len(getattr(mod, f'_{what.upper()}_MCQ_GENERATORS'))))
    else:
        written = set(getattr(mod, what))
    per = {band: set(vals) for band, vals in bands.items()}
    placed = set().union(*per.values()) if per else set()
    return written, placed, per


def bank(slug):
    import importlib
    mod, name = BANK_REFS[slug]
    return list(getattr(importlib.import_module(mod), name))


def item_view(item):
    """(plain question, [(letter, text)], keyed text or None) for a bank item."""
    opts = parse_options({'options': item.get('opts')})
    letter = str(item.get('ans', '')).strip().upper()
    keyed = [t for ltr, t in (opts or []) if ltr == letter]
    return plain(item.get('q', '')), (opts or []), (keyed[0] if len(keyed) == 1 else None)


def item_digest(item):
    """Shuffle-invariant sha1 of a static item: question, sorted option texts and the keyed text."""
    q, opts, keyed = item_view(item)
    blob = '\x1f'.join([q, '\x1e'.join(sorted(t for _, t in opts)), keyed or ''])
    return hashlib.sha1(blob.encode()).hexdigest()[:12]


# Questions about the form of the answer itself, where an equal but unworked option is a legitimate distractor.
FORM_QUESTION = options.FORM_QUESTION


def option_quantity(text):
    """(exact value, unit) of an option that is one quantity, else None.

    The exact reader handles integers, decimals, fractions, multiples of pi and square roots (perfect or not,
    worked or not), so ``sqrt 25`` meets ``5`` and ``sqrt 8`` meets ``2 sqrt 2``. Text it cannot read keeps the
    older plain-number rule (value from ``parse_num``, unit = the text without digits and number marks).
    """
    q = exact.value_and_unit(text)
    if q is not None:
        return q
    v = parse_num(text)
    if v is None:
        return None
    return v, norm_text(re.sub(r'[-+\d.,/\s£$€]', '', text))


def item_structure_errors(item):
    q, opts, keyed = item_view(item)
    errs = []
    # Correlation questions legitimately have three answers: positive, negative, none.
    three_ok = len(opts) == 3 and re.search(r'correlation', q, re.I)
    if len(opts) != 4 and not three_ok:
        errs.append(f'{len(opts)} options (expected 4)')
    if [ltr for ltr, _ in opts] != list('ABCD')[:len(opts)]:
        errs.append('option letters are not A, B, C, D in order')
    texts = [t for _, t in opts]
    if len(set(texts)) != len(texts):
        errs.append('duplicate option text')
    if keyed is None:
        errs.append(f'key {item.get("ans")!r} does not name exactly one option')
    # A distractor worth the same as the key (0.5 and 1/2, 30 cm and 30.0 cm, and an unworked root such as
    # sqrt 25 or 2 sqrt 9 beside 5, or sqrt 8 beside 2 sqrt 2) is a second right answer, unless the question
    # is about the form itself (simplest form, rationalise the denominator, three-figure bearings): there the
    # unsimplified or unrationalised original (1/sqrt 2 beside sqrt 2 / 2) is the standard wrong answer.
    # The comparison reads units (300 m beside 0.3 km is a second right answer) and flags a 0 or negative filler
    # beside a positive key (options.py).
    errs += options.same_value_errors(q, opts, keyed)
    errs += options.filler_errors(q, opts, keyed)
    return errs


def procedural(slug):
    from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
    return list(procedural_mcq_for(slug))


def verify_procedural(slug, fn, run):
    """Outcome for one seeded call of a procedural MCQ function."""
    import zlib
    seed = zlib.crc32(f'{slug}/difficult/{fn.__name__}'.encode()) + run
    p, recs = harness.generate_callable(slug, fn, seed)
    outcome = verify_problem(p, recs)
    outcome.problem = p
    outcome.records = recs
    return outcome


def item_problem(item):
    """A bank item shown as a problem (question, options, keyed letter), which is all a solver may read."""
    return {'question': item.get('q', ''), 'options': item.get('opts'), 'correct_answer': item.get('ans')}


def verify_static(item, key=None, digest=None):
    """Re-solve a static bank item with its registered spec (``key`` replaces the item's keyed letter).

    ``digest`` runs a changed copy of an item (a mutation test) under the spec of the original.
    """
    from . import solvers_bank
    p = item_problem(item)
    if key is not None:
        p['correct_answer'] = key
    d = digest or item_digest(item)
    if d not in solvers_bank.SPECS:
        raise KeyError(d)
    return verify_problem(p, [{'family': 'bank', 'inputs': {'digest': d}, 'derived': ()}])


def tampered_item_checks(item, digest):
    """Negative control: every wrong keyed letter must fail. Yields (letter, 1, 1 if caught else 0)."""
    right = str(item.get('ans', '')).strip().upper()
    for ltr, _ in parse_options({'options': item.get('opts')}) or []:
        if ltr != right:
            yield ltr, 1, int(verify_static(item, key=ltr).status != 'verified')


def unworked_root_mutants(item):
    """Mutation test: copies of a static item in which one wrong option is replaced by an unworked root worth
    the key (``sqrt 25`` beside 5, ``sqrt 100 units`` beside 10 units, ``2 sqrt 9`` beside 6).

    Yields (letter replaced, mutated item). Nothing is yielded unless the key is a whole number of at least 2
    and the question is not about a form (where an unsimplified equal option is a legitimate distractor).
    """
    q, opts, keyed = item_view(item)
    if keyed is None or re.search(FORM_QUESTION, q, re.I):
        return
    kq = option_quantity(keyed)
    if kq is None or not isinstance(kq[0], Fraction) or kq[0].denominator != 1 or kq[0] < 2:
        return
    if re.search(r'[\u00bc-\u00be\u2150-\u215e]', keyed) or re.match(r'(?:st|nd|rd|th)\b', kq[1]):
        return                          # mixed numbers and ordinals (6 2/3 cm, 7th term) are not plain quantities
    n, unit = int(kq[0]), kq[1]
    cur = keyed.strip()[:1] if keyed.strip()[:1] in '\u00a3$\u20ac' else ''      # the mutant keeps the currency sign
    shown = [f'\u221a{n * n}', f'{n // 2}\u221a{4}' if n % 2 == 0 and n >= 2 else f'\u221a{n * n}']
    letter = str(item.get('ans', '')).strip().upper()
    for ltr, _ in opts:
        if ltr == letter:
            continue
        for body in dict.fromkeys(shown):
            text = f'{cur}{body} {unit}'.strip()
            new = [f'{l} {text}' if l == ltr else f'{l} {t}' for l, t in opts]
            yield ltr, dict(item, opts=new)
