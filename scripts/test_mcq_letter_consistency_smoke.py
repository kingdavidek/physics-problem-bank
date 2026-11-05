"""MCQ letter consistency across every level and subject — run: python scripts/test_mcq_letter_consistency_smoke.py

Replaces ``test_mcq_consistency.py``, which demanded that every solution name the answer letter (most do not, by
design) and so reported about 1,340 false failures. What matters, and what no other suite test checks outside
GCSE maths, is that the key is a real option and that any letter a solution does name is the key after the
shuffle. GCSE maths values are checked by ``test_gcse_maths_verification_smoke.py``; this test is about letters.
"""
import collections
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generators.shared.utils import _shuffle_mcq  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

DRAWS = 24                  # seeded draws per topic and difficulty (about 6,500 problems, a few seconds)
DIFFICULTIES = ('foundational', 'intermediate', 'difficult')
# Letter references a solution can carry (the forms ``generators.shared.utils._update_solution_letter`` rewrites).
# Also "Correct answer: B" and "Answer B": the shuffle does not rewrite those, so they must already be the key.
_REFERENCE = re.compile(
    r'(?:The correct option is\s*(?:<strong>|\*\*)?|(?:[Cc]orrect answer|Answer):?\s*(?:<strong>|\*\*)?|→\s*<strong>'
    r'|Only\s*<strong>)\(?([A-D])\b'
    r'|^<strong>([A-D])</strong>')
# A distractor named by its letter ("Option B ignores efficiency") is never rewritten by the shuffle, so after it
# the letter points at a random option. Solutions describe distractors by their content instead.
_POSITIONAL = re.compile(r'\b[Oo]ptions?\s+\(?([A-D])\b')
_OPTION = re.compile(r'^([A-D])\s{2}\S')


def letter_problems(problem):
    """Messages for one MCQ problem: the key is not exactly one option, or the solution names another letter."""
    options = problem.get('options') or []
    key = str(problem.get('correct_answer') or '').strip()
    letters = []
    for o in options:
        m = _OPTION.match(str(o))
        if not m:
            return [f'option without a letter: {str(o)[:40]!r}']
        letters.append(m.group(1))
    out = []
    if letters != list('ABCD')[:len(letters)]:
        out.append(f'option letters {letters} are not A, B, C, D in order')
    if letters.count(key) != 1:
        out.append(f'key {key!r} is not exactly one of the options {letters}')
    solution = str(problem.get('solution') or '')
    named = {a or b for a, b in _REFERENCE.findall(solution)}
    if named and named != {key}:
        out.append(f'solution names {sorted(named)} but the key is {key!r}: {solution[:80]!r}')
    positional = sorted(set(_POSITIONAL.findall(solution)))
    if positional:
        out.append(f'solution names option {positional} by letter, which the shuffle does not rewrite: {solution[:80]!r}')
    return out


# Topics that have no multiple-choice mode at all (their generator returns a practice problem for 'mcq'); everything
# else must serve options on every difficulty.  Whole-change review C10: the sweep used to skip any topic and difficulty
# whose generator raised, so an MCQ mode that crashed everywhere passed unless a whole level went dark.
NO_MCQ_TOPICS = {
    ('gcse', 'physics', 'forces'), ('gcse', 'physics', 'radioactivity'),
    ('myp', 'chemistry', 'energy_changes_and_rates'), ('myp', 'chemistry', 'redox'),
}


def sweep():
    failures, checked, per_subject = [], 0, collections.Counter()
    served = collections.Counter()          # (level, subject, topic, difficulty) -> draws that served options
    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            for topic, config in topics.items():
                generator = config.get('func')
                if not generator:
                    continue
                for difficulty in DIFFICULTIES:
                    served[(level, subject, topic, difficulty)] += 0
                    for i in range(DRAWS):
                        random.seed(f'{level}/{subject}/{topic}/{difficulty}/{i}')
                        try:
                            problem = generator(difficulty, 'mcq')
                        except Exception as exc:        # noqa: BLE001 - counted and reported, never skipped
                            failures.append(f'{level}/{subject}/{topic} ({difficulty}, draw {i}): the generator raised {exc!r}')
                            continue
                        if not problem.get('options'):
                            continue
                        checked += 1
                        served[(level, subject, topic, difficulty)] += 1
                        per_subject[(level, subject)] += 1
                        for msg in letter_problems(problem):
                            failures.append(f'{level}/{subject}/{topic} ({difficulty}, draw {i}): {msg}')
    for (level, subject, topic, difficulty), n in sorted(served.items()):
        expected_none = (level, subject, topic) in NO_MCQ_TOPICS
        if n == 0 and not expected_none:
            failures.append(f'{level}/{subject}/{topic} ({difficulty}): no draw served options (list the topic in NO_MCQ_TOPICS if it has no MCQ mode)')
        if n and expected_none:
            failures.append(f'{level}/{subject}/{topic} ({difficulty}): serves options but is listed in NO_MCQ_TOPICS (remove the entry)')
    return checked, per_subject, failures


def check_shuffle_keeps_letters():
    """Whatever the key and whichever form the solution uses, the shuffle moves its letter with the key."""
    forms = (
        'The correct option is <strong>{k}</strong> (x).',
        'The correct option is **{k}**.',
        'Because of this. Answer: <strong>{k}</strong>',
        'Because of this. Answer: **{k}**',
        '<strong>Add</strong> new rows. Answer: {k}',
        '<strong>{k}</strong>. Short.',
        'step → <strong>{k}</strong>',
    )
    for form in forms:
        for key in 'ABCD':
            for seed in range(6):
                random.seed(seed)
                options = [f'{c}  option {c}' for c in 'ABCD']
                new_options, new_key, new_solution = _shuffle_mcq(options, key, form.format(k=key))
                assert new_options[ord(new_key) - 65] == f'{new_key}  option {key}', (form, key, new_options, new_key)
                problem = {'options': new_options, 'correct_answer': new_key, 'solution': new_solution}
                assert not letter_problems(problem), (form, key, letter_problems(problem))


def check_negative_controls(sample):
    """The check must see a moved key, a missing option and a stale solution letter."""
    good = {'options': ['A  1', 'B  2', 'C  3', 'D  4'], 'correct_answer': 'C', 'solution': '3. Answer: <strong>C</strong>'}
    assert not letter_problems(good)
    assert letter_problems(dict(good, correct_answer='A')), 'a key that disagrees with the solution letter was accepted'
    assert letter_problems(dict(good, solution='3. Answer: B')), 'a stale solution letter was accepted'
    assert letter_problems(dict(good, correct_answer='E')), 'a key that is not an option was accepted'
    assert letter_problems(dict(good, options=['A  1', 'B  2', 'D  3', 'C  4'])), 'out-of-order letters were accepted'
    assert letter_problems(dict(good, options=['A  1', 'B  2', 'B  3', 'D  4'])), 'a repeated letter was accepted'
    assert not letter_problems(dict(good, solution='3 is the value.')), 'a solution with no letter must be allowed'
    assert letter_problems(dict(good, solution='<strong>Correct answer: A</strong> 3.')), 'a stale "Correct answer" letter was accepted'
    assert letter_problems(dict(good, solution='3 — <strong>Answer A</strong>.')), 'a stale "Answer A" letter was accepted'
    assert letter_problems(dict(good, solution='3. Answer: C. Option B ignores the 2.')), 'a distractor named by letter was accepted'
    assert not letter_problems(dict(good, solution='The correct option is <strong>C</strong>.')), 'a key reference was rejected'
    assert sample >= 3000, f'only {sample} MCQ problems were generated; the sweep is not reaching the generators'


def check_magnetism_standard_sweep(draws=400):
    """A-level magnetism standard mode once crashed on about 4 to 5 percent of draws: three AQA variants returned a
    {'question', 'solution'} dict where the caller unpacked (q, s, hint, marks). Every variant, seeded."""
    from generators.alevel import magnetism as mag

    failures = []
    for tier, pool in mag._MAG_POOL_BY_TIER.items():
        for variant in pool:
            for seed in range(draws):
                random.seed(seed)
                try:
                    problem = mag.alevel_physics_magnetism(tier, 'standard', variant_name=variant.__name__)
                except Exception as exc:  # noqa: BLE001
                    failures.append(f'{tier}/{variant.__name__} seed {seed}: {exc!r}')
                    break
                if not problem.get('question') or not problem.get('solution') or not problem.get('hint') or not problem.get('marks'):
                    failures.append(f'{tier}/{variant.__name__} seed {seed}: incomplete problem')
                    break
    for tier in ('foundational', 'intermediate', 'difficult', 'mixed'):
        for seed in range(draws):
            random.seed(seed)
            try:
                mag.alevel_physics_magnetism(tier, 'standard')
            except Exception as exc:  # noqa: BLE001
                failures.append(f'{tier} random draw seed {seed}: {exc!r}')
                break
    assert not failures, 'magnetism standard sweep: ' + '; '.join(failures[:10])
    print(f'Magnetism standard-mode sweep OK ({draws} seeded draws per variant and per tier).')
    # The MCQ options are shuffled after the explanation is written, so an explanation may name the correct letter
    # (rewritten by the shuffle) but no other option by its letter (fix review 2026-11-03: the transformer question
    # said "(B and D)" and "(C and D)", wrong on most draws).
    named = re.compile(r'\(\s*[A-D]\s*(?:,|and|&)\s*[A-D]\s*\)|\boptions?\s+[A-D]\s+(?:and|or|,)')
    for seed in range(draws):
        random.seed(seed)
        problem = mag.alevel_physics_magnetism('intermediate', 'mcq')
        tail = re.sub(r'The correct option is <strong>[A-D]</strong>', '', str(problem.get('solution') or ''))
        assert not named.search(tail), ('magnetism MCQ explanation names an option letter', seed, tail[-200:])


def main():
    check_shuffle_keeps_letters()
    checked, per_subject, failures = sweep()
    check_negative_controls(checked)
    missing = {('gcse', 'maths'), ('gcse', 'cs'), ('alevel', 'physics'), ('eursc', 'science')} - set(per_subject)
    assert not missing, f'no MCQ problems generated for {sorted(missing)}'
    if failures:
        print(f'Checked {checked} MCQ problems; {len(failures)} failures.')
        for line in failures[:15]:
            print(line.encode('ascii', errors='backslashreplace').decode('ascii'))
        if len(failures) > 15:
            print(f'... and {len(failures) - 15} more')
        sys.exit(1)
    subjects = ', '.join(f'{lv}/{sub} {n}' for (lv, sub), n in sorted(per_subject.items()))
    print(f'MCQ letter consistency OK across {checked} generated problems ({subjects}).')


if __name__ == '__main__':
    check_magnetism_standard_sweep()
    main()
