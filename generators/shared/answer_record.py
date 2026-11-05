"""The answer record: a compact copy of a GCSE maths question's inputs, kept for the misconception rules.

Plan: docs/GCSE_MATHS_HINTS.md section 3.2 (Phase 2).

``generators/shared/verify_hook.record()`` already names the inputs of every GCSE maths variant, but in production
it does nothing. ``with_answer_record(func)`` wraps a topic generator so that, when exactly one record was made
and the family has misconception rules, the problem carries

    problem['answer_record'] = {'f': <family>, 'i': {<inputs>}}      (at most 256 bytes of compact JSON)

Rules for this field (all enforced by scripts/test_gcse_maths_hints_smoke.py):

* It is server-only. It is in ``models.class_assignments.SERVER_ONLY_KEYS``, so it is stripped from every payload
  a pupil receives; ``app._problem_client_payload`` is a whitelist and never copies it.
* It is never stored in a database. It lives in the session problem (the signed session cookie) and nowhere
  else: ``public_problem`` removes it before a problem is saved, shared, suggested, frozen into set work, kept
  in a Quick Test or lesson-quiz row, or put in a challenge. It is never logged.
* It is made from numbers the question already prints (the presence guard of the verification track), so it says
  nothing about the pupil.
* Capturing it never changes the problem or draws a random number: ``capture()`` only appends to a list, and the
  wrapper runs after the generator has finished.
"""
from __future__ import annotations

import functools
import json

from generators.shared import option_notes, verify_hook

KEY = 'answer_record'
MAX_BYTES = 256

# Answer types a family rule can read: one value typed in one box (Phase 2), a bearing or an equation solution
# (Phase 5), and the answers that families of their own read: a pair, an expression, or several boxes. Which family may
# sit on which type is ``misconceptions.RECORDED_FAMILIES`` (a mapping from family to its answer types).
RECORDED_ANSWER_TYPES = frozenset({'number', 'pi_multiple', 'fraction', 'bearing', 'linear', 'number_pair', 'vector',
                                   'algebraic', 'number_fields'})

# Families recorded from many questions whose rules only say which operation was needed.
OPERATION_FAMILIES = frozenset({'product', 'quotient'})

# Records of the drawing a graph question shows; the maths of the same question is recorded alongside it, and that
# record is the one a rule reads (Phase 5).
DRAWING_FAMILIES = frozenset({'gr_drawn', 'gsim_drawn'})


def _plain(value):
    """JSON-friendly copy: tuples become lists, numbers and strings stay as they are, anything else is refused."""
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        out = [_plain(v) for v in value]
        return NotImplemented if any(v is NotImplemented for v in out) else out
    return NotImplemented


def build_record(captured, problem, families):
    """The record for a finished problem, or None (no rule applies, more than one record, or too big).

    ``families`` is a set of family names, or (as ``misconceptions.RECORDED_FAMILIES``) a mapping from a family to
    the answer types it may sit on. For the algebra tasks the verification hook names only the task, so the inputs
    are read from the question text (``misconception_cd.DERIVE``).
    """
    if not isinstance(problem, dict):
        return None
    captured = [e for e in captured if e.get('family') not in DRAWING_FAMILIES] if len(captured) > 1 else captured
    if len(captured) != 1:
        return None
    if problem.get('options') or problem.get('correct_answer_raw') is None:
        return None
    answer_type = problem.get('answer_type') or 'number'
    if answer_type not in RECORDED_ANSWER_TYPES:
        return None
    entry = captured[0]
    family = entry.get('family')
    raw_inputs = entry.get('inputs') or {}
    if family == 'alg':
        from generators.shared import misconceptions       # first: it loads the topic tables that misconception_cd needs
        cd, plain_text = misconceptions._cd, misconceptions.plain_text
        derive = cd.DERIVE.get(str(raw_inputs.get('task')))
        found = derive(plain_text(problem.get('question'))) if derive is not None else None
        if found is None:
            return None
        family, raw_inputs = found
    if family not in families:
        return None
    if hasattr(families, 'get') and answer_type not in (families.get(family) or ()):
        return None
    # The one-step families ("this one needs the numbers multiplied") speak of the numbers in the question; when one
    # of them is not printed (a unit factor such as 1000 in g/cm3 to kg/m3), the message would not fit (review).
    if family in OPERATION_FAMILIES and entry.get('derived'):
        return None
    inputs = {}
    for name, value in raw_inputs.items():
        clean = _plain(value)
        if clean is NotImplemented:
            return None
        inputs[str(name)] = clean
    record = {'f': family, 'i': inputs}
    try:
        size = len(json.dumps(record, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))
    except (TypeError, ValueError):
        return None
    return record if size <= MAX_BYTES else None


def with_answer_record(func):
    """Wrap a topic generator so its problem carries ``answer_record`` when a rule can use it, and ``option_notes``
    (Phase 4: notes on multiple-choice distractors, see option_notes.py) when a tagged option builder ran."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with verify_hook.capture() as captured, option_notes.capture() as notes:
            problem = func(*args, **kwargs)
        try:
            from generators.shared.example_hint import keep_example_off_key
            keep_example_off_key(problem)
        except Exception:  # noqa: BLE001
            pass
        try:
            from generators.shared.misconceptions import RECORDED_FAMILIES
            record = build_record(captured, problem, RECORDED_FAMILIES)
        except Exception:  # noqa: BLE001 - a hint helper must never break question generation
            record = None
        if record is not None:
            problem[KEY] = record
        try:
            if not notes and isinstance(problem, dict) and problem.get('options'):
                notes = option_notes.bank_notes(problem)
            option_notes.with_notes(problem, notes)
        except Exception:  # noqa: BLE001
            pass
        return problem

    wrapper.__wrapped_answer_record__ = True
    return wrapper


def public_problem(problem, keep_notes=False):
    """The problem without its answer record (for anything that is stored or shared). Same object if it has none.

    The notes on multiple-choice options (``option_notes``) are dropped too unless ``keep_notes``: only set work, a
    lesson quiz and the Quick Test results show them, after grading, so only those rows keep them.
    """
    drop = (KEY,) if keep_notes else (KEY, option_notes.KEY)
    if isinstance(problem, dict) and any(k in problem for k in drop):
        return {k: v for k, v in problem.items() if k not in drop}
    return problem


def public_problems(problems, keep_notes=False):
    if isinstance(problems, (list, tuple)):
        return [public_problem(p, keep_notes) for p in problems]
    return problems
