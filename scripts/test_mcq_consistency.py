"""Validate MCQ letter consistency after shuffle — run: python scripts/test_mcq_consistency.py"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from topic_registry import TOPICS  # noqa: E402


def option_value(option):
    if len(option) >= 3 and option[0] in 'ABCD' and option[1:3] == '  ':
        return option[3:].strip()
    return option.strip()


def solution_mentions_letter(solution, letter):
    patterns = [
        rf'^<strong>{letter}</strong>',
        rf'The correct option is\s*<strong>{letter}</strong>',
        rf'The correct option is\s*\*\*{letter}\*\*',
        rf'Answer:\s*<strong>{letter}</strong>',
        rf'Answer:\s*\*\*{letter}\*\*',
        rf'Answer:\s*{letter}\b',
        rf'→\s*<strong>{letter}</strong>',
        rf'Only\s*<strong>{letter}\)',
        rf'\. Answer:\s*{letter}\s*$',
    ]
    return any(re.search(p, solution) for p in patterns)


def validate_problem(problem):
    letter = (problem.get('correct_answer') or '').strip()
    options = problem.get('options') or []
    solution = problem.get('solution') or ''
    if not letter or len(options) != 4:
        return None

    values = {}
    for opt in options:
        if len(opt) >= 1 and opt[0] in 'ABCD':
            values[opt[0]] = option_value(opt)

    if letter not in values:
        return f'missing option letter {letter}'

    if not solution_mentions_letter(solution, letter):
        return f'solution does not reference letter {letter}'

    return None


def main():
    failures = []
    checked = 0

    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            for topic, config in topics.items():
                generator = config.get('func')
                if not generator:
                    continue
                for difficulty in ('foundational', 'intermediate', 'difficult'):
                    for _ in range(8):
                        try:
                            problem = generator(difficulty, 'mcq')
                        except Exception:
                            continue
                        if not problem.get('options'):
                            continue
                        checked += 1
                        err = validate_problem(problem)
                        if err:
                            failures.append(
                                f'{level}/{subject}/{topic} ({difficulty}): {err}\n'
                                f'  correct={problem.get("correct_answer")}\n'
                                f'  options={problem.get("options")}\n'
                                f'  solution={problem.get("solution")[:180]}...'
                            )

    if failures:
        print(f'Checked {checked} MCQ problems; {len(failures)} failures.')
        for item in failures[:15]:
            safe = item.encode('ascii', errors='backslashreplace').decode('ascii')
            print(safe)
            print()
        if len(failures) > 15:
            print(f'... and {len(failures) - 15} more')
        sys.exit(1)

    print(f'MCQ consistency OK across {checked} generated problems.')


if __name__ == '__main__':
    main()
