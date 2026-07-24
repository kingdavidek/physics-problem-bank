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


def _graded_format_num(val):
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    if isinstance(val, float):
        return str(val)
    return str(val)


def graded_answer_number(val):
    return {'type': 'number', 'value': val}


def graded_answer_keyword(val):
    return {'type': 'keyword', 'value': str(val).strip().lower()}


def graded_answer_number_pair(val_a, val_b, label_a='x', label_b='y', sep=','):
    return {
        'type': 'number_pair',
        'values': (_graded_format_num(val_a), _graded_format_num(val_b)),
        'label_a': label_a,
        'label_b': label_b,
        'sep': sep,
    }


def graded_answer_number_fields(values, labels, field_types=None, *,
                                row_sizes=None, group_labels=None, format_hint=None,
                                field_options=None, inline_sections=False):
    types = tuple(field_types) if field_types else tuple('number' for _ in values)
    payload = {
        'type': 'number_fields',
        'values': tuple(_graded_format_num(v) for v in values),
        'labels': tuple(labels),
        'field_types': types,
    }
    if row_sizes:
        payload['row_sizes'] = tuple(int(n) for n in row_sizes)
    if group_labels:
        payload['group_labels'] = tuple(group_labels)
    if format_hint:
        payload['format_hint'] = format_hint
    if field_options is not None:
        payload['field_options'] = tuple(field_options)
    if inline_sections and group_labels:
        keys = []
        for gl in group_labels:
            key = str(gl).split(' ', 1)[0]
            if key and (not keys or keys[-1] != key):
                keys.append(key)
        if keys:
            payload['inline_sections'] = True
            payload['section_keys'] = tuple(keys)
    return payload


def graded_answer_tri_coords(img, vertex_labels=("P'", "Q'", "R'")):
    labels = []
    values = []
    for _name, (x, y) in zip(vertex_labels, img):
        labels.extend(['x', 'y'])
        values.extend([x, y])
    return graded_answer_number_fields(
        values,
        labels,
        row_sizes=(2, 2, 2),
        group_labels=vertex_labels,
        format_hint='Enter each coordinate',
    )


def problem_extra_from_graded_answer(raw):
    """Build make_problem kwargs from a graded-answer payload (5th tuple element)."""
    extra = {}
    if raw is None:
        return extra
    if isinstance(raw, dict):
        raw_type = raw.get('type')
        if raw_type == 'number':
            extra = {
                'correct_answer_raw': _graded_format_num(raw['value']),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
        elif raw_type == 'keyword':
            value = raw.get('value')
            if value is not None and str(value).strip():
                extra = {
                    'correct_answer_raw': str(value).strip().lower(),
                    'answer_type': 'keyword',
                    'answer_format_hint': 'Enter one word (e.g. yes or no)',
                }
        elif raw_type == 'number_pair':
            val_a, val_b = raw['values']
            extra = {
                'correct_answer_raw': f'{val_a}|{val_b}',
                'answer_type': 'number_pair',
                'answer_labels': [raw['label_a'], raw['label_b']],
                'answer_pair_sep': raw.get('sep', 'and'),
            }
        elif raw_type == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            field_types = raw.get('field_types') or ()
            if values and labels and len(values) == len(labels):
                sep = (
                    '\x1e'
                    if field_types and any(t != 'number' for t in field_types)
                    else '|'
                )
                extra = {
                    'correct_answer_raw': sep.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_field_types': list(field_types) if field_types else (
                        ['number'] * len(labels)
                    ),
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter each value in its own box',
                    ),
                }
                row_sizes = raw.get('row_sizes')
                if row_sizes:
                    extra['answer_field_row_sizes'] = list(row_sizes)
                group_labels = raw.get('group_labels')
                if group_labels:
                    extra['answer_field_group_labels'] = list(group_labels)
                field_options = raw.get('field_options') or ()
                if field_options:
                    extra['answer_field_options'] = [
                        list(opts) if opts else None for opts in field_options
                    ]
                if raw.get('inline_sections'):
                    extra['answer_inline_sections'] = True
                    section_keys = raw.get('section_keys') or ()
                    if section_keys:
                        extra['answer_field_section_keys'] = list(section_keys)
        elif raw_type == 'proof_steps':
            extra = proof_steps_problem_extra(raw)
    elif isinstance(raw, (int, float)):
        extra = {
            'correct_answer_raw': _graded_format_num(raw),
            'answer_type': 'number',
            'answer_format_hint': 'Enter a number',
        }
    elif isinstance(raw, str) and raw.strip():
        extra = {
            'correct_answer_raw': raw.strip(),
            'answer_type': 'number',
            'answer_format_hint': 'Enter a number',
        }
    return extra


def make_graded_problem(out, difficulty, level, subject, topic):
    q, s, hint, marks = out[:4]
    extra = problem_extra_from_graded_answer(out[4] if len(out) >= 5 else None)
    return make_problem(q, s, hint, difficulty, marks, level, subject, topic, **extra)


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