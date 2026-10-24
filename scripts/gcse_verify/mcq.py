"""MCQ coverage: pinned static bank items, structural checks and the procedural MCQ functions."""
from __future__ import annotations

import hashlib
import re

from . import harness
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
    # A distractor worth the same as the key (0.5 and 1/2, 30 cm and 30.0 cm) is a second right answer,
    # unless the question is about the form itself (simplest form, three-figure bearings).
    form_question = re.search(r'simplest|simplif|three-figure|3-figure', q, re.I)
    key_value = parse_num(keyed) if keyed is not None else None
    if key_value is not None and not form_question:
        unit = norm_text(re.sub(r'[-+\d.,/\s£$€]', '', keyed))
        for ltr, t in opts:
            if t != keyed and parse_num(t) == key_value and norm_text(re.sub(r'[-+\d.,/\s£$€]', '', t)) == unit:
                errs.append(f'option {ltr} ({t!r}) has the same value as the key ({keyed!r})')
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
    return outcome


def item_problem(item):
    """A bank item shown as a problem (question, options, keyed letter), which is all a solver may read."""
    return {'question': item.get('q', ''), 'options': item.get('opts'), 'correct_answer': item.get('ans')}


def verify_static(item, key=None):
    """Re-solve a static bank item with its registered spec (``key`` replaces the item's keyed letter)."""
    from . import solvers_bank
    p = item_problem(item)
    if key is not None:
        p['correct_answer'] = key
    d = item_digest(item)
    if d not in solvers_bank.SPECS:
        raise KeyError(d)
    return verify_problem(p, [{'family': 'bank', 'inputs': {'digest': d}, 'derived': ()}])


def tampered_item_checks(item, digest):
    """Negative control: every wrong keyed letter must fail. Yields (letter, 1, 1 if caught else 0)."""
    right = str(item.get('ans', '')).strip().upper()
    for ltr, _ in parse_options({'options': item.get('opts')}) or []:
        if ltr != right:
            yield ltr, 1, int(verify_static(item, key=ltr).status != 'verified')
