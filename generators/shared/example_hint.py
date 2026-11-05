"""Answer-box examples that are never the answer (whole-change review C1).

A box placeholder such as "e.g. 3/4" is a format hint.  On the draw whose key is 3/4 it hands the pupil the answer.
``keep_example_off_key(problem)`` runs once, after a GCSE maths problem is built: if typing the hint's own example is
marked correct by the problem's checker, the example's numbers are shifted (all copies of one number together, then a
swapped sign or fraction) until it is not.  It draws no random numbers, changes nothing else and leaves a hint alone
unless it coincides with the key.
"""
import math
import re

_EXAMPLE = re.compile(r'(e\.g\.?\s+)(.+)')
_CUT = re.compile(r'\s+or\s+|\s+[—–]\s+|\s+\(|\)|;|\s*$')
_NUM = re.compile(r'\d+')


def _example_span(hint):
    m = _EXAMPLE.search(hint)
    if not m:
        return None
    rest = m.group(2)
    end = _CUT.search(rest).start()
    example = rest[:end].rstrip('.,')
    if not example or re.fullmatch(r'(yes|no|true|false)', example.strip(), re.I):
        return None
    start = m.start(2)
    return start, start + len(example), example


def _in_lowest_terms(text):
    """False when a fraction a/b written in ``text`` has a factor in common or is a/a (4/4, 4/8)."""
    for a, b in re.findall(r'(\d+)\s*/\s*(\d+)', text):
        if int(a) == int(b) or math.gcd(int(a), int(b)) > 1:
            return False
    return True


def _candidates(example):
    # The numbers in the order they first appear, longest first: a set's order changes from one process to the next,
    # so the example shown changed with it (fix review 2026-11-03: "e.g. 1/3" became 2/3 or 1/4 by hash seed). A
    # fraction in lowest terms stays in lowest terms ("e.g. 3/8" under "simplest form" never becomes 4/8).
    nums = sorted(dict.fromkeys(_NUM.findall(example)), key=lambda t: -len(t))
    tidy = _in_lowest_terms(example)
    for cand in _shifted(example, nums):
        if not tidy or _in_lowest_terms(cand):
            yield cand


def _shifted(example, nums):
    for shift in (1, 2, 3, 4):
        for n in nums:
            new = str(int(n) + shift).zfill(len(n))
            yield re.sub(rf'(?<!\d){n}(?!\d)', new, example)
    if '+' in example:
        yield example.replace('+', '-')
    elif ' - ' in example:
        yield example.replace(' - ', ' + ')
    if '/' in example:
        a, _, b = example.partition('/')
        yield f'{b}/{a}'


def keep_example_off_key(problem):
    if not isinstance(problem, dict):
        return problem
    hint = problem.get('answer_format_hint')
    at, raw = problem.get('answer_type'), problem.get('correct_answer_raw')
    if not isinstance(hint, str) or not at or raw is None or 'e.g' not in hint:
        return problem
    span = _example_span(hint)
    if span is None:
        return problem
    try:
        from generators.shared import answer_units
        from generators.shared.answer_checkers import check_answer
        question = answer_units.problem_question_text(problem)

        def squash(t):
            # '**' first: a sympy key '2*x**2 + 5*x' lost its '*' to the strip below and read '2x2+5x', so the example
            # '2x^2 + 5x' never matched it (fix pass 2026-11-03, algebra_practice_expand_mixed)
            return re.sub(r'[\s*()]|\\cdot', '', str(t).replace('**', '^')).replace('\u2212', '-').lower()

        def accepted(text):
            if str(at).startswith('algebraic'):
                # A symbolic check costs milliseconds on every generated problem: here the net compares the written form
                # (the verification smoke runs the full checker over every example, so an algebraically equal
                # but differently written example is still caught there).
                keys = {squash(raw), squash(str(raw).split('=', 1)[-1])}
                return squash(text) in keys or squash(text.split('=', 1)[-1]) in keys
            res = check_answer(at, raw, text, form=problem.get('answer_form'), subject=problem.get('answer_subject'),
                               question=question)
            return bool(res.get('correct'))

        start, end, example = span
        if not accepted(example):
            return problem
        for cand in _candidates(example):
            if cand != example and not accepted(cand):
                problem['answer_format_hint'] = hint[:start] + cand + hint[end:]
                break
    except Exception:  # noqa: BLE001 - a hint helper must never break question generation
        pass
    return problem
