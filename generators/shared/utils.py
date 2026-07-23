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


def compare_choice_payload(label_a, label_b, correct_letter):
    """Build a 5-tuple payload for two-button compare / which-is-larger practice items."""
    letter = str(correct_letter).strip().upper()
    if letter not in ('A', 'B'):
        raise ValueError('compare_choice correct letter must be A or B')
    return {
        'type': 'choice',
        'options': [f'A  {label_a}', f'B  {label_b}'],
        'correct': letter,
    }


def problem_from_choice_output(out, difficulty, level, subject, topic):
    """Turn a variant 5-tuple with compare_choice_payload into an MCQ-style problem."""
    if len(out) < 5:
        return None
    raw = out[4]
    if not (isinstance(raw, dict) and raw.get('type') == 'choice'):
        return None
    q, s, hint, marks = out[:4]
    return make_problem(
        q, s, hint, difficulty, marks, level, subject, topic,
        options=raw['options'],
        correct_answer=raw['correct'],
        choice_no_shuffle=True,
    )


def quadratic_roots_ui_labels(n):
    """Labels for multi-field quadratic-root answer UI (order-independent)."""
    try:
        count = int(n or 0)
    except (TypeError, ValueError):
        count = 0
    if count <= 0:
        return []
    return [f'Root {i}' for i in range(1, count + 1)]


def quadratic_roots_format_hint(n, custom=None):
    if custom:
        return custom
    try:
        count = int(n or 0)
    except (TypeError, ValueError):
        count = 0
    if count >= 4:
        return 'Enter each solution in its own box'
    if count >= 2:
        return 'Enter each root in its own box'
    return 'Enter the root'


def make_problem(question, solution, hint, difficulty, marks, level, subject, topic, **extra):
    # Shuffle MCQ options so the correct answer is not always A.
    if "options" in extra and "correct_answer" in extra:
        if not extra.pop("choice_no_shuffle", False):
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


def proof_steps_answer(required_ids, bank, *, order_matters=True, format_hint=None):
    """Plan C payload: select correct proof steps from a shuffled bank.

    bank items are dicts ``{id, text}``. ``required_ids`` lists the correct step
    ids (in order when ``order_matters`` is True).
    """
    required = tuple(str(i) for i in required_ids)
    steps = []
    for item in bank:
        step_id = str(item.get('id') or '').strip()
        text = str(item.get('text') or '').strip()
        if not step_id or not text:
            continue
        steps.append({'id': step_id, 'text': text})
    if not required or not steps:
        raise ValueError('proof_steps bank and required_ids are required')
    bank_ids = {step['id'] for step in steps}
    if any(rid not in bank_ids for rid in required):
        raise ValueError('proof_steps required_ids must appear in bank')
    payload = {
        'type': 'proof_steps',
        'required_ids': required,
        'order_matters': bool(order_matters),
        'bank': steps,
    }
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def proof_steps_problem_extra(raw):
    """Convert a proof_steps payload into make_problem kwargs."""
    if not isinstance(raw, dict) or raw.get('type') != 'proof_steps':
        return {}
    required = tuple(str(i) for i in (raw.get('required_ids') or ()))
    bank = list(raw.get('bank') or [])
    if not required or not bank:
        return {}
    order_matters = bool(raw.get('order_matters', True))
    hint = raw.get('format_hint') or (
        'Select the correct proof steps in order'
        if order_matters
        else 'Select all correct statements'
    )
    return {
        'correct_answer_raw': (
            f"{'1' if order_matters else '0'}|{('|'.join(required))}"
        ),
        'answer_type': 'proof_steps',
        'answer_step_bank': bank,
        'answer_order_matters': order_matters,
        'answer_format_hint': hint,
    }