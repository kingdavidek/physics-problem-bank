import random
import re


def format_light_markdown(text):
    """Turn lightweight markdown markers into HTML for question/solution prose."""
    if not text:
        return text

    def _code(match):
        return f"<code>{match.group(1)}</code>"

    out = re.sub(r"`([^`]+)`", _code, text)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out


def format_cs_prose(text):
    """Turn lightweight markdown in CS question text into HTML."""
    return format_light_markdown(text)


def format_cs_mcq_option(option):
    """Format the option text after the 'A  ' label."""
    if len(option) >= 3 and option[0] in "ABCD" and option[1:3] == "  ":
        return option[:3] + format_cs_prose(option[3:])
    return format_cs_prose(option)


def _update_solution_letter(solution, old_letter, new_letter):
    """Rewrite MCQ answer-letter references after options are shuffled."""
    if old_letter == new_letter:
        return solution

    patterns = [
        (
            rf'(The correct option is\s*<strong>){re.escape(old_letter)}(</strong>)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(The correct option is\s*\*\*){re.escape(old_letter)}(\*\*)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(Answer:\s*<strong>){re.escape(old_letter)}(</strong>)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(Answer:\s*\*\*){re.escape(old_letter)}(\*\*)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(Answer:\s*){re.escape(old_letter)}(\b)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(→\s*<strong>){re.escape(old_letter)}(</strong>)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(Only\s*<strong>){re.escape(old_letter)}(\))',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(\. Answer:\s*){re.escape(old_letter)}(\s*$)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'^(<strong>){re.escape(old_letter)}(</strong>)',
            rf'\g<1>{new_letter}\2',
        ),
        (
            rf'(remove the constant term first → <strong>){re.escape(old_letter)}(</strong>)',
            rf'\g<1>{new_letter}\2',
        ),
    ]
    updated = solution
    for pattern, repl in patterns:
        updated = re.sub(pattern, repl, updated)
    return updated


def _shuffle_mcq(options, correct_letter, solution):
    """Randomly reorder MCQ options and update the correct-answer letter.

    Options are expected in the format ["A  content", "B  content", ...].
    The correct_letter (e.g. "A") is found by position, the list is shuffled,
    labels are reassigned A–D, and the solution string is updated to reflect
    the new letter.  Works even if two options share identical content.
    """
    labels = ["A", "B", "C", "D"]

    if correct_letter not in labels:
        return options, correct_letter, solution

    def strip_label(opt):
        # Handles "A  content" (letter + 2 spaces) and plain strings.
        if len(opt) >= 3 and opt[0] in labels and opt[1:3] == "  ":
            return opt[3:]
        return opt

    contents = [strip_label(opt) for opt in options]
    correct_idx = labels.index(correct_letter)

    # Shuffle by permuting indices so duplicate content can't cause confusion.
    indices = list(range(len(contents)))
    random.shuffle(indices)

    new_correct_pos = indices.index(correct_idx)
    new_correct_letter = labels[new_correct_pos]

    new_options = [f"{labels[i]}  {contents[indices[i]]}" for i in range(len(contents))]

    new_solution = _update_solution_letter(solution, correct_letter, new_correct_letter)

    return new_options, new_correct_letter, new_solution


def make_problem(question, solution, hint, difficulty, marks, level, subject, topic, **extra):
    # Shuffle MCQ options so the correct answer is not always A.
    if "options" in extra and "correct_answer" in extra:
        extra["options"], extra["correct_answer"], solution = _shuffle_mcq(
            extra["options"], extra["correct_answer"], solution
        )

    data = {
        "question": question,
        "solution": solution,
        "hint": hint,
        "difficulty": difficulty,
        "marks": marks,
        "topic_url": f"/topic/{level}/{subject}/{topic}",
        "topic_name": topic.replace("-", " ").title(),
        "level": level,
        "subject": subject,
        "topic": topic,
    }
    data.update(extra)
    return data
