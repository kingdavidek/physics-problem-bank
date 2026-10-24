"""Lesson-quiz sweep (Phase 4): the ten-question quizzes pupils get from a GCSE maths topic page.

A GCSE maths topic has no ``lesson_bank``, so ``build_lesson_quiz`` draws MCQ problems from the same variant
slots the practice sweep already covers.  What the quiz adds is the draw itself (3 foundational, 4 intermediate,
3 difficult, no repeated question), the shuffle of the options, and the grading of a letter.  Each quiz built
here is therefore checked for:

* shape: ten questions, the 3/4/3 mix, no two the same;
* the key: a question from a generator is re-solved from its records; a question from the static bank is
  re-solved by its digest spec after the quiz's own option shuffle (so a key that drifted in the shuffle is
  caught), or is one of the reviewed exemptions;
* options: four distinct options lettered A to D, the key naming exactly one of them;
* grading: ``grade_lesson_quiz_problem`` marks the keyed letter right and every other letter wrong.

This is a test helper, not a solver, so it may import the generators.
"""
from __future__ import annotations

import contextlib
import io
import random

from generators.shared import lesson_quiz, verify_hook
from topic_registry import TOPICS

from . import mcq, register
from .engine import parse_options, verify_problem
from .latex import plain

MIX = {'foundational': 3, 'intermediate': 4, 'difficult': 3}


def topics():
    return TOPICS['gcse']['maths']


def _key(p):
    """Identifies one generated problem: the quiz rejects repeats by question text alone, so a rejected attempt
    with the same stem but other numbers must not stand in for the one that was kept."""
    return (lesson_quiz._question_key(p), tuple(str(o) for o in p.get('options') or ()), str(p.get('correct_answer')))


def build(slug, seed):
    """(quiz problems, {question key: records}) for one seeded quiz on a topic."""
    cfg = topics()[slug]
    seen = {}
    original = lesson_quiz._call_generator

    def recording(*a, **k):
        with verify_hook.recording() as sink:
            p = original(*a, **k)
        if isinstance(p, dict):
            seen[_key(p)] = list(sink)
        return p

    lesson_quiz._call_generator = recording
    try:
        random.seed(seed)
        with contextlib.redirect_stdout(io.StringIO()):
            problems = lesson_quiz.build_lesson_quiz('gcse', 'maths', slug, cfg, seed=seed)
    finally:
        lesson_quiz._call_generator = original
    return problems, seen


def digest_of(p):
    return mcq.item_digest({'q': p['question'], 'opts': p['options'], 'ans': p['correct_answer']})


def check_quiz(slug, seed, solvers_bank, wrong_keys=False):
    """Findings (strings) for one quiz, and counters {'questions', 'bank', 'bank_exempt', 'generated', 'graded'}."""
    out, n = [], dict(questions=0, bank=0, bank_exempt=0, generated=0, graded=0)
    try:
        problems, records = build(slug, seed)
    except Exception as exc:
        return [f'building the quiz raised {exc!r}'], n
    floor, _ = register.QUIZ_SHAPE.get(slug, (10, ''))
    if len(problems) < floor or len(problems) > 10:
        out.append(f'the quiz has {len(problems)} questions, not {floor if floor == 10 else f"{floor} to 10"}')
    if slug not in register.QUIZ_SHAPE:
        mix = {t: sum(1 for p in problems if p.get('difficulty') == t) for t in MIX}
        if mix != MIX:
            out.append(f'the quiz mix is {mix}, not {MIX}')
    keys = [lesson_quiz._question_key(p) for p in problems]
    if len(set(keys)) != len(keys):
        out.append('two questions in one quiz are the same')
    for i, p in enumerate(problems):
        n['questions'] += 1
        where = f'question {i + 1} ({p.get("difficulty")}, {p.get("variant_name")})'
        if not (p.get('options') and p.get('correct_answer')):
            out.append(f'{where}: not a multiple-choice question')
            continue
        item = {'q': p['question'], 'opts': p['options'], 'ans': p['correct_answer']}
        out += [f'{where}: {m}' for m in mcq.item_structure_errors(item)]
        recs = records.get(_key(p)) or []
        d = digest_of(p)
        if wrong_keys:                  # negative control: the key moves to another option, nothing else changes
            moved = next(l for l, _ in parse_options(p) if l != str(p['correct_answer']).strip().upper()[:1])
            p, item = dict(p, correct_answer=moved), dict(item, ans=moved)
        if recs and recs[-1]['family'] != 'bank':
            n['generated'] += 1
            o = verify_problem(p, recs)
            if o.status != 'verified':
                out += [f'{where}: [{k}] {m}' for k, m in (o.findings or [('norecord', 'not verified')])]
        else:
            if d in solvers_bank.SPECS:
                n['bank'] += 1
                o = verify_problem(mcq.item_problem(item), [{'family': 'bank', 'inputs': {'digest': d}, 'derived': ()}])
                if o.status != 'verified':
                    out += [f'{where}: bank item {d} after the quiz shuffle: [{k}] {m}'
                            for k, m in (o.findings or [('norecord', 'not verified')])]
            elif d in register.STATIC_EXEMPT:
                n['bank_exempt'] += 1
            else:
                out.append(f'{where}: a question that is neither re-solved nor a reviewed exemption ({d}): '
                           f'{plain(p["question"])[:70]!r}')
        right = str(p['correct_answer']).strip().upper()[:1]
        for ltr, _ in parse_options(p) or []:
            got = lesson_quiz.grade_lesson_quiz_problem(p, ltr)['correct']
            n['graded'] += 1
            if got != (ltr == right):
                out.append(f'{where}: grading letter {ltr} gave {got}, the key is {right}')
    return out, n
