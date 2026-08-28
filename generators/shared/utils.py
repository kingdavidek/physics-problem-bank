import json
import random
import re

from generators.shared.text_keywords import text_keyword_labels
from generators.shared.sql_checker import normalize_sql_query


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


def proof_steps_answer(required_ids, bank, *, order_matters=True, format_hint=None,
                       pick_count=None):
    """Plan C payload: select correct proof steps from a shuffled bank.

    bank items are dicts ``{id, text}``. ``required_ids`` lists the correct step
    ids (in order when ``order_matters`` is True). When ``pick_count`` is set,
    ``required_ids`` lists every correct option id and the student must choose
    exactly that many (any correct combination; distractors in the bank fail).
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
    if pick_count is not None:
        pick_count = int(pick_count)
        if pick_count < 1 or pick_count > len(required):
            raise ValueError('proof_steps pick_count must be between 1 and len(required_ids)')
        order_matters = False
    payload = {
        'type': 'proof_steps',
        'required_ids': required,
        'order_matters': bool(order_matters),
        'bank': steps,
    }
    if pick_count is not None:
        payload['pick_count'] = pick_count
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


def graded_answer_sql(query, *, lines=3, format_hint=None):
    payload = {'type': 'sql', 'query': normalize_sql_query(query)}
    if lines != 3:
        payload['lines'] = int(lines)
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _normalize_python_stdout(value) -> str:
    return str(value or '').replace('\r\n', '\n').replace('\r', '\n').strip()


def graded_answer_python_run(tests, *, starter=None, lines=4, format_hint=None, setup=None):
    """Tier-2 Python write-code grading via stdin/stdout fixtures."""
    normalized = []
    for item in tests:
        entry = {
            'stdin': str(item.get('stdin', '')),
            'stdout': _normalize_python_stdout(item.get('stdout', '')),
        }
        test_setup = item.get('setup', setup)
        if test_setup is not None and str(test_setup).strip():
            entry['setup'] = str(test_setup)
        if item.get('min_inputs') is not None:
            entry['min_inputs'] = int(item['min_inputs'])
        if item.get('validate'):
            entry['validate'] = str(item['validate'])
        files = item.get('files')
        if files:
            entry['files'] = {str(k): str(v) for k, v in files.items()}
        normalized.append(entry)
    payload = {'type': 'python_run', 'tests': tuple(normalized)}
    if starter:
        payload['starter'] = str(starter)
    if lines != 4:
        payload['lines'] = int(lines)
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def graded_answer_text(*keywords, required=None, format_hint=None, labels=None):
    kws = tuple(str(k).strip().lower() for k in keywords if str(k).strip())
    payload = {'type': 'text', 'keywords': kws}
    if required is not None:
        payload['required'] = int(required)
    if format_hint:
        payload['format_hint'] = format_hint
    if labels:
        payload['labels'] = tuple(labels)
    return payload


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
                                field_options=None, inline_sections=False,
                                field_pick_counts=None):
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
    if field_pick_counts is not None:
        payload['field_pick_counts'] = tuple(field_pick_counts)
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
        elif raw_type == 'number_estimate':
            value = raw.get('value')
            tolerance = raw.get('tolerance')
            if value is not None and tolerance is not None:
                extra = {
                    'correct_answer_raw': (
                        f'{_graded_format_num(value)}~{_graded_format_num(tolerance)}'
                    ),
                    'answer_type': 'number_estimate',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter your estimate from the scale',
                    ),
                }
        elif raw_type == 'keyword':
            value = raw.get('value')
            if value is not None and str(value).strip():
                key = str(value).strip().lower()
                extra = {
                    'correct_answer_raw': key,
                    'answer_type': 'keyword',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter your answer',
                    ),
                    'answer_text_keywords': text_keyword_labels([key]),
                }
        elif raw_type == 'text':
            keywords = raw.get('keywords') or ()
            labels = raw.get('labels')
            required = raw.get('required')
            if keywords:
                display = list(labels) if labels else text_keyword_labels(keywords)
                kw_joined = '|'.join(str(k) for k in keywords)
                if required is not None and required < len(keywords):
                    raw_encoded = f'{required}@{kw_joined}'
                else:
                    raw_encoded = kw_joined
                extra = {
                    'correct_answer_raw': raw_encoded,
                    'answer_type': 'text',
                    'answer_text_keywords': display,
                    'answer_format_hint': raw.get('format_hint', 'Enter your answer'),
                }
                if required is not None and required < len(keywords):
                    extra['answer_text_required'] = int(required)
        elif raw_type == 'sql':
            query = str(raw.get('query') or '').strip()
            if query:
                lines = int(raw.get('lines', 3))
                extra = {
                    'correct_answer_raw': query,
                    'answer_type': 'sql',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Write your SQL query (one statement)',
                    ),
                    'answer_input_lines': lines,
                }
        elif raw_type == 'python_run':
            tests = raw.get('tests') or ()
            if tests:
                canonical = []
                client_tests = []
                for t in tests:
                    if t.get('validate'):
                        entry = {'validate': str(t['validate'])}
                    else:
                        entry = {
                            'stdout': _normalize_python_stdout(t.get('stdout', '')),
                        }
                        if t.get('min_inputs') is not None:
                            entry['min_inputs'] = int(t['min_inputs'])
                    canonical.append(entry)
                    client_item = {
                        'stdin': str(t.get('stdin', '')),
                        'stdout': _normalize_python_stdout(t.get('stdout', '')),
                    }
                    if t.get('setup') is not None and str(t.get('setup', '')).strip():
                        client_item['setup'] = str(t['setup'])
                    if t.get('min_inputs') is not None:
                        client_item['min_inputs'] = int(t['min_inputs'])
                    if t.get('validate'):
                        client_item['validate'] = str(t['validate'])
                    files = t.get('files')
                    if files:
                        client_item['files'] = {
                            str(k): str(v) for k, v in files.items()
                        }
                    client_tests.append(client_item)
                extra = {
                    'correct_answer_raw': json.dumps(
                        canonical,
                        separators=(',', ':'),
                    ),
                    'answer_type': 'python_run',
                    'answer_tests': client_tests,
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Write Python code, then Check runs it against sample inputs.',
                    ),
                    'answer_input_lines': int(raw.get('lines', 4)),
                }
                starter = raw.get('starter')
                if starter:
                    extra['answer_python_starter'] = str(starter)
        elif raw_type == 'number_pair':
            val_a, val_b = raw['values']
            extra = {
                'correct_answer_raw': f'{val_a}|{val_b}',
                'answer_type': 'number_pair',
                'answer_labels': [raw['label_a'], raw['label_b']],
                'answer_pair_sep': raw.get('sep', 'and'),
            }
        elif raw_type == 'number_list':
            values = raw.get('values') or ()
            if values:
                extra = {
                    'correct_answer_raw': ','.join(str(v) for v in values),
                    'answer_type': 'number_list',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter numbers separated by commas',
                    ),
                }
        elif raw_type == 'fraction':
            value = raw.get('value')
            if value is not None and str(value).strip():
                extra = {
                    'correct_answer_raw': str(value).strip(),
                    'answer_type': 'fraction',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter a fraction (e.g. 3/4)',
                    ),
                }
        elif raw_type == 'algebraic':
            text = str(raw.get('value') or '')
            if text.strip():
                extra = {
                    'correct_answer_raw': text,
                    'answer_type': 'algebraic',
                    'answer_format_hint': raw.get(
                        'format_hint',
                        'Enter the simplified expression',
                    ),
                }
                if raw.get('subject'):
                    extra['answer_subject'] = raw['subject']
                if raw.get('wrong_hint'):
                    extra['answer_wrong_hint'] = raw['wrong_hint']
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
                field_pick_counts = raw.get('field_pick_counts') or ()
                if field_pick_counts:
                    extra['answer_field_pick_counts'] = list(field_pick_counts)
                if raw.get('inline_sections'):
                    extra['answer_inline_sections'] = True
                    section_keys = raw.get('section_keys') or ()
                    if section_keys:
                        extra['answer_field_section_keys'] = list(section_keys)
                if field_types:
                    field_hints = []
                    for label, val, ft in zip(labels, values, field_types):
                        if ft == 'keyword' and val is not None and str(val).strip():
                            key = str(val).strip().lower()
                            hint = text_keyword_labels([key])[0]
                            field_hints.append(f'{label}: {hint}')
                    if field_hints:
                        extra['answer_field_hints'] = field_hints
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
    pick_count = raw.get('pick_count')
    if pick_count is not None:
        pick_count = int(pick_count)
        hint = raw.get('format_hint') or f'Select {pick_count} correct options'
        correct_raw = f"pick|{pick_count}|{('|'.join(required))}"
    else:
        hint = raw.get('format_hint') or (
            'Select the correct proof steps in order'
            if order_matters
            else 'Select all correct statements'
        )
        correct_raw = f"{'1' if order_matters else '0'}|{('|'.join(required))}"
    extra = {
        'correct_answer_raw': correct_raw,
        'answer_type': 'proof_steps',
        'answer_step_bank': bank,
        'answer_order_matters': order_matters,
        'answer_format_hint': hint,
    }
    if pick_count is not None:
        extra['answer_pick_count'] = pick_count
    return extra