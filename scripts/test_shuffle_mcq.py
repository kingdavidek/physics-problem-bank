"""Unit tests for MCQ shuffle letter updates — run: python scripts/test_shuffle_mcq.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generators.shared.utils import _shuffle_mcq  # noqa: E402


def test_correct_option_pattern():
    options = ['A  8', 'B  6', 'C  7', 'D  64']
    solution = 'The correct option is <strong>C</strong> (7).\n\nA power of 1/2 means square root.'
    new_opts, new_letter, new_sol = _shuffle_mcq(options, 'C', solution)
    values = {opt[0]: opt[3:].strip() for opt in new_opts}
    assert values[new_letter] == '7'
    assert f'The correct option is <strong>{new_letter}</strong> (7)' in new_sol


def test_answer_pattern():
    options = ['A  first', 'B  second', 'C  third', 'D  fourth']
    solution = 'Work shown here. Answer: <strong>B</strong>'
    _, new_letter, new_sol = _shuffle_mcq(options, 'B', solution)
    assert new_letter in 'ABCD'
    assert f'Answer: <strong>{new_letter}</strong>' in new_sol


def test_standalone_letter_solution():
    options = ['A  one', 'B  two', 'C  three', 'D  four']
    solution = '<strong>B</strong>.'
    new_opts, new_letter, new_sol = _shuffle_mcq(options, 'B', solution)
    assert new_sol.startswith(f'<strong>{new_letter}</strong>')


def main():
    test_correct_option_pattern()
    test_answer_pattern()
    test_standalone_letter_solution()
    print('_shuffle_mcq tests passed.')


if __name__ == '__main__':
    main()
