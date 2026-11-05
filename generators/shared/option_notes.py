"""Notes on multiple-choice distractors (docs/GCSE_MATHS_HINTS.md section 4, Phase 4).

A wrong pick in a GCSE maths multiple-choice question can say which slip leads to that option ("That looks like the
side lengths added directly"). The note belongs to the option, not to its letter, because ``utils.make_problem``
reshuffles the options after the generator returns.

How a note gets from a generator to a pupil:

1. A generator builds its options with a tagged builder (``_letter_opts_tagged``, ``_string_opts_tagged``,
   ``_number_mcq_options`` and ``_mcq_options`` take tagged candidates too). A tagged candidate is a pair
   ``(value, note_id)``. The builder makes exactly the random calls of its untagged twin (it calls it), then looks at
   which tagged candidates survived as options and ``register``s ``{option text: note id}``. Filler options carry no
   note. Two tagged candidates that format to the same text with different note ids make the option ambiguous, so it
   keeps none ("prefer silence over a misleading note").
2. ``registry.with_answer_record`` (the wrapper every GCSE maths topic function already has) runs the generator inside
   ``capture()`` and, if the finished problem is multiple choice, stores the notes for options that exist and are not
   the key as ``problem['option_notes']``.
3. ``option_notes`` is server-only (``models.class_assignments.SERVER_ONLY_KEYS``): it is stripped from every payload a
   pupil receives and is never in a template. The practice page learns only that the question has notes, not which
   option has one. The note for one picked option is returned by ``POST /api/v1/problems/option-note`` after a wrong
   pick in practice, and by ``graded_message`` after grading in set work, a lesson quiz and the Quick Test results.

This module draws no random number, imports no generator and, until a note is read, no copy.
"""
from __future__ import annotations

import contextlib
import contextvars
import re
from decimal import ROUND_HALF_UP, Decimal

KEY = 'option_notes'
MAX_NOTES = 4

_SINK = contextvars.ContextVar('pb_option_notes', default=None)
_LABEL = re.compile(r'^[A-D]  ')
_AMOUNT = re.compile(r'^(£?)(-?\d+(?:\.\d+)?)(\s*[^\d\s.].*)?$')
# notes whose slip is a coarser rounding, so an option that is the key rounded is exactly what they describe
ROUNDING_NOTES = frozenset({'gen.accuracy', 'mcq.round_dropped', 'mcq.round_place', 'mcq.digits_cut'})


def rounds_from_key(text, key_text):
    """True when an option is the key rounded to fewer decimal places, in the same unit ("6%" beside a key of "5.9%").

    A pupil who worked out the right answer and rounded it picks that option, so a note naming another slip would
    mislead (review of Phase 4): such an option keeps no note unless the note is itself about rounding.
    """
    opt, key = _AMOUNT.match(str(text).strip()), _AMOUNT.match(str(key_text).strip())
    if not opt or not key or opt.group(1) != key.group(1) or (opt.group(3) or '').strip() != (key.group(3) or '').strip():
        return False
    places = len(opt.group(2).partition('.')[2])
    if places >= len(key.group(2).partition('.')[2]):
        return False
    return Decimal(key.group(2)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP) == Decimal(opt.group(2))


def option_text(option):
    """The text of an option written "B  12 cm" (without its letter)."""
    text = str(option)
    return text[3:] if _LABEL.match(text) else text


@contextlib.contextmanager
def capture():
    """Collect the notes registered while one generator runs (the registry wrapper and the verification test use it)."""
    sink = {}
    token = _SINK.set(sink)
    try:
        yield sink
    finally:
        _SINK.reset(token)


def register(notes):
    """Record ``{option text: note id}`` for the question being built. The last call wins (a retry replaces a draft)."""
    sink = _SINK.get()
    if sink is not None:
        sink.clear()
        sink.update(notes)


def split(candidates):
    """(plain candidates, note ids) for a list whose tagged members are ``(value, 'note.id')`` pairs."""
    plain, tags = [], []
    for cand in candidates:
        if isinstance(cand, tuple) and len(cand) == 2 and isinstance(cand[1], str):
            plain.append(cand[0])
            tags.append(cand[1])
        else:
            plain.append(cand)
            tags.append(None)
    return plain, tags


def notes_for(options, cand_texts, tags):
    """``{option text: note id}`` for the tagged candidates that are options (never the key's text, never ambiguous).

    ``options`` is the finished list ("A  text", ...); ``cand_texts`` the text each candidate was shown as, in order.
    A tagged candidate that did not survive (equal to the key, a duplicate, cut after the third) is not an option and
    gets nothing. A text claimed by two different note ids is ambiguous and gets nothing.
    """
    shown = {option_text(o) for o in options}
    found, clash = {}, set()
    for text, tag in zip(cand_texts, tags):
        if tag is None or text not in shown:
            continue
        if text in found and found[text] != tag:
            clash.add(text)
        found[text] = tag
    return {t: n for t, n in found.items() if t not in clash}


def attach(options, candidates, fmt, key_text=None):
    """Register the notes of ``candidates`` once ``options`` are built; returns nothing. ``fmt`` shows a value as text."""
    plain, tags = split(candidates)
    if not any(tags):
        register({})
        return plain
    texts = [fmt(v) for v in plain]
    notes = notes_for(options, texts, tags)
    if key_text is not None:
        notes.pop(key_text, None)
        notes = {t: n for t, n in notes.items() if n in ROUNDING_NOTES or not rounds_from_key(t, key_text)}
    register(notes)
    return plain


def with_notes(problem, notes):
    """Put ``notes`` on a finished multiple-choice problem: only options that exist and are not the key, at most four."""
    if not isinstance(problem, dict) or not notes:
        return problem
    options = problem.get('options') or []
    letter = str(problem.get('correct_answer') or '').strip().upper()[:1]
    texts = {}
    for opt in options:
        opt = str(opt)
        if _LABEL.match(opt):
            texts[opt[0]] = opt[3:]
    key_text = texts.get(letter)
    kept = {t: n for t, n in notes.items() if t in texts.values() and t != key_text}
    if kept and len(kept) <= MAX_NOTES and len(set(texts.values())) == len(texts):
        problem[KEY] = kept
    return problem


_BANK_INDEX = None


def bank_notes(problem):
    """``{option text: note id}`` for a fixed bank question listed in ``mcq_notes.BANK_WHY`` (same question, same key,
    the distractor still one of the options), else {}. A reworded bank item matches nothing and so shows no note."""
    global _BANK_INDEX
    if _BANK_INDEX is None:
        from generators.shared import mcq_notes
        index = {}
        for note_id, question, key_text, option, _slip in mcq_notes.BANK_WHY:
            index.setdefault(question, []).append((key_text, option, note_id))
        _BANK_INDEX = index
    rows = _BANK_INDEX.get(str(problem.get('question') or ''))
    if not rows:
        return {}
    letter = str(problem.get('correct_answer') or '').strip().upper()[:1]
    texts = {str(o)[0]: option_text(o) for o in problem.get('options') or [] if _LABEL.match(str(o))}
    key_text = texts.get(letter)
    return {opt: nid for key, opt, nid in rows if key == key_text and opt in texts.values()}


def _resolve(note_id):
    from generators.shared import mcq_notes
    if note_id in mcq_notes.BANK_NOTES:
        return mcq_notes.BANK_NOTES[note_id]
    if note_id in mcq_notes.NOTES:
        return mcq_notes.NOTES[note_id]
    from generators.shared import misconceptions
    if note_id in misconceptions.MESSAGES:
        return misconceptions.MESSAGES[note_id]
    from generators.shared import misconception_topics
    rule = misconception_topics.RULES_BY_ID.get(note_id)
    if rule is not None:
        return misconceptions.MESSAGES.get(rule.message, '')
    return ''


def note_text(note_id):
    """The text of a note id, or '' when the id is unknown."""
    try:
        return _resolve(str(note_id))
    except Exception:  # noqa: BLE001 - a courtesy line; the grade is already decided
        return ''


def picked_note(problem, letter):
    """The note for the option with this letter, or '' (no note, the key itself, an unknown letter, a damaged problem).

    Reads the problem the server holds (the session problem or the frozen set-work or quiz problem), never the request.
    Never raises.
    """
    try:
        if not isinstance(problem, dict):
            return ''
        notes = problem.get(KEY)
        if not isinstance(notes, dict) or not notes:
            return ''
        pick = str(letter or '').strip().upper()[:1]
        correct = str(problem.get('correct_answer') or '').strip().upper()[:1]
        if not pick or pick == correct:
            return ''
        for opt in problem.get('options') or []:
            opt = str(opt)
            if _LABEL.match(opt) and opt[0] == pick:
                return note_text(notes.get(opt[3:], '')) if notes.get(opt[3:]) else ''
        return ''
    except Exception:  # noqa: BLE001
        return ''


def fingerprint(problem):
    """A short tag of the question on screen (question and options, never the key), so a stale tab cannot read a note
    that belongs to a different question."""
    import hashlib
    if not isinstance(problem, dict):
        return ''
    blob = '\x1f'.join([str(problem.get('question') or '')] + [str(o) for o in (problem.get('options') or [])])
    return hashlib.sha1(blob.encode('utf-8')).hexdigest()[:10]
