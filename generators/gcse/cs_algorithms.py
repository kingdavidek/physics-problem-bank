"""
GCSE Computer Science – Fundamentals of Algorithms
10 foundational · 11 intermediate · 16 difficult · 22 MCQ bank
Graded practice variants return (question, solution, hint, marks, raw).
"""
import random
import math
from generators.shared.utils import (
    make_problem,
    graded_answer_number_fields,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import pick_named_variant


def _alg_raw_number(value):
    return str(int(value))


def _alg_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'cs', 'algorithms',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        if isinstance(raw, dict):
            extra = problem_extra_from_graded_answer(raw)
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _alg_raw_number(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'algorithms', **extra
    )


def _alg_mcq_payload(correct_variants, distractor_groups):
    """Four-option practice MCQ; picks one phrasing per answer and shuffles."""
    variants = correct_variants if isinstance(correct_variants, (tuple, list)) else (correct_variants,)
    groups = [
        (group,) if isinstance(group, str) else tuple(group)
        for group in distractor_groups[:3]
    ]
    correct_text = random.choice(variants)
    max_distractor_len = max(len(max(g, key=len)) for g in groups) if groups else 0
    if len(correct_text) > max_distractor_len:
        shorter = [v for v in variants if len(v) <= max_distractor_len]
        if shorter:
            correct_text = random.choice(shorter)
    distractors = []
    for group in groups:
        if random.random() < 0.55:
            distractors.append(max(group, key=len))
        else:
            distractors.append(random.choice(group))
    if distractors and len(correct_text) > max(len(d) for d in distractors):
        gi = random.randrange(len(groups))
        distractors[gi] = max(groups[gi], key=len)
    pool = [correct_text] + distractors
    random.shuffle(pool)
    letters = 'ABCD'
    correct_letter = letters[pool.index(correct_text)]
    options = [f'{letters[i]}  {pool[i]}' for i in range(len(pool))]
    return {'type': 'mcq', 'options': options, 'correct': correct_letter}


def _alg_mcq_options(correct_variants, distractor_groups):
    payload = _alg_mcq_payload(correct_variants, distractor_groups)
    return payload['options'], payload['correct']


def _alg_mcq_match_field(correct_text, distractors):
    """Shuffled 3-option inline MCQ for multipart fields."""
    pool = [correct_text] + list(distractors[:2])
    random.shuffle(pool)
    letters = 'ABC'
    return pool, letters[pool.index(correct_text)]


def _alg_pick_from_bank(correct_texts, distractor_texts, pick_count, *, format_hint=None):
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    return proof_steps_answer(
        correct_ids,
        bank,
        pick_count=pick_count,
        format_hint=format_hint,
    )


def _alg_order_from_bank(steps, distractors, *, format_hint=None):
    step_ids = tuple(f's{i + 1}' for i in range(len(steps)))
    bank = [{'id': sid, 'text': text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    return proof_steps_answer(
        step_ids,
        bank,
        order_matters=True,
        format_hint=format_hint,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sorted_unique_list(n, lo=1, hi=99):
    items = random.sample(range(lo, hi), n)
    items.sort()
    return items


def _trace_table_html(headers, rows):
    th = "".join(
        f'<th style="padding:6px 10px;border:1px solid #d4e6f1;background:#eaf4fb;">{h}</th>'
        for h in headers
    )
    body = ""
    for row in rows:
        body += "<tr>" + "".join(
            f'<td style="padding:6px 10px;border:1px solid #e2e8f0;text-align:center;">{c}</td>'
            for c in row
        ) + "</tr>"
    return (
        '<table style="width:100%;border-collapse:collapse;margin:10px 0;font-size:.9rem;">'
        f"<tr>{th}</tr>{body}</table>"
    )


def _alg_flowchart_svg(inner, *, aria_label, width=320, height=420):
    return (
        '<div style="text-align:center;margin:12px 0;">'
        f'<svg width="100%" viewBox="0 0 {width} {height}" '
        'style="background:#f9f8f5;border-radius:8px;max-width:340px;display:block;margin:0 auto;" '
        f'aria-label="{aria_label}">'
        '<defs><marker id="alg-arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">'
        '<polygon points="0,0 8,4 0,8" fill="#333"/></marker></defs>'
        f'{inner}'
        '</svg></div>'
    )


def _alg_flowchart_age_check_svg(*, decision='rectangle', swap_outputs=False):
    """Age ≥ 18 flowchart; decision may be rectangle (wrong) or diamond (correct)."""
    if decision == 'diamond':
        decision_shape = (
            '<polygon points="160,128 210,168 160,208 110,168" fill="#fef4e8" '
            'stroke="#8a5300" stroke-width="2"/>'
            '<text x="160" y="165" font-size="13" fill="#8a5300" text-anchor="middle" '
            'font-weight="bold">age ≥ 18?</text>'
        )
    else:
        decision_shape = (
            '<rect x="110" y="138" width="100" height="60" fill="#fef4e8" stroke="#8a5300" '
            'stroke-width="2"/>'
            '<text x="160" y="173" font-size="13" fill="#8a5300" text-anchor="middle" '
            'font-weight="bold">age ≥ 18?</text>'
        )
    if swap_outputs:
        yes_text, no_text = '"Child"', '"Adult"'
    else:
        yes_text, no_text = '"Adult"', '"Child"'
    inner = f'''
      <rect x="110" y="12" width="100" height="36" rx="16" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="35" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">START</text>
      <line x1="160" y1="48" x2="160" y2="68" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <polygon points="70,68 250,68 235,108 55,108" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="94" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">INPUT age</text>
      <line x1="160" y1="108" x2="160" y2="128" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      {decision_shape}
      <line x1="110" y1="168" x2="55" y2="168" stroke="#333" stroke-width="1.5"/>
      <line x1="55" y1="168" x2="55" y2="248" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <text x="82" y="158" font-size="12" fill="#059669" font-weight="bold">Yes</text>
      <polygon points="5,248 105,248 95,288 0,288" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="52" y="272" font-size="12" fill="#1a6fa8" text-anchor="middle" font-weight="bold">OUTPUT</text>
      <text x="52" y="284" font-size="10" fill="#1a6fa8" text-anchor="middle">{yes_text}</text>
      <line x1="210" y1="168" x2="265" y2="168" stroke="#333" stroke-width="1.5"/>
      <line x1="265" y1="168" x2="265" y2="248" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <text x="238" y="158" font-size="12" fill="#a13544" font-weight="bold">No</text>
      <polygon points="215,248 315,248 305,288 210,288" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="262" y="272" font-size="12" fill="#1a6fa8" text-anchor="middle" font-weight="bold">OUTPUT</text>
      <text x="262" y="284" font-size="10" fill="#1a6fa8" text-anchor="middle">{no_text}</text>
      <line x1="55" y1="288" x2="55" y2="330" stroke="#333" stroke-width="1.5"/>
      <line x1="265" y1="288" x2="265" y2="330" stroke="#333" stroke-width="1.5"/>
      <line x1="55" y1="330" x2="265" y2="330" stroke="#333" stroke-width="1.5"/>
      <line x1="160" y1="330" x2="160" y2="360" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <rect x="110" y="360" width="100" height="36" rx="16" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="383" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">STOP</text>
    '''
    return _alg_flowchart_svg(inner, aria_label='Flowchart: check if age is 18 or over', height=410)


def _alg_flowchart_average_svg(*, input_shape='rectangle', process_shape='rectangle'):
    """Average two scores; INPUT and/or PROCESS may use the wrong symbol."""
    if input_shape == 'parallelogram':
        input_shape_svg = (
            '<polygon points="55,68 265,68 250,108 40,108" fill="#e8f4fd" stroke="#1a6fa8" '
            'stroke-width="2"/>'
            '<text x="160" y="94" font-size="13" fill="#1a6fa8" text-anchor="middle" '
            'font-weight="bold">INPUT score1, score2</text>'
        )
    else:
        input_shape_svg = (
            '<rect x="55" y="68" width="210" height="40" fill="#e8f4fd" stroke="#1a6fa8" '
            'stroke-width="2"/>'
            '<text x="160" y="94" font-size="13" fill="#1a6fa8" text-anchor="middle" '
            'font-weight="bold">INPUT score1, score2</text>'
        )
    if process_shape == 'parallelogram':
        process_shape_svg = (
            '<polygon points="70,128 250,128 235,172 55,172" fill="#ecfdf5" stroke="#059669" '
            'stroke-width="2"/>'
            '<text x="160" y="148" font-size="12" fill="#059669" text-anchor="middle" '
            'font-weight="bold">average ←</text>'
            '<text x="160" y="163" font-size="11" fill="#059669" text-anchor="middle">'
            '(score1 + score2) / 2</text>'
        )
    else:
        process_shape_svg = (
            '<rect x="70" y="128" width="180" height="44" fill="#ecfdf5" stroke="#059669" '
            'stroke-width="2"/>'
            '<text x="160" y="148" font-size="12" fill="#059669" text-anchor="middle" '
            'font-weight="bold">average ←</text>'
            '<text x="160" y="163" font-size="11" fill="#059669" text-anchor="middle">'
            '(score1 + score2) / 2</text>'
        )
    inner = f'''
      <rect x="110" y="12" width="100" height="36" rx="16" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="35" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">START</text>
      <line x1="160" y1="48" x2="160" y2="68" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      {input_shape_svg}
      <line x1="160" y1="108" x2="160" y2="128" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      {process_shape_svg}
      <line x1="160" y1="172" x2="160" y2="192" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <polygon points="90,192 230,192 215,232 75,232" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="218" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">OUTPUT average</text>
      <line x1="160" y1="232" x2="160" y2="252" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <rect x="110" y="252" width="100" height="36" rx="16" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="275" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">STOP</text>
    '''
    return _alg_flowchart_svg(inner, aria_label='Flowchart: average of two scores', height=300)


def _alg_flowchart_pass_fail_svg(*, missing_stop=False):
    """Pass/fail on score; may omit STOP terminator."""
    stop_svg = ''
    if not missing_stop:
        stop_svg = '''
      <line x1="160" y1="330" x2="160" y2="350" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <rect x="110" y="350" width="100" height="36" rx="16" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="373" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">STOP</text>
        '''
    inner = f'''
      <rect x="110" y="12" width="100" height="36" rx="16" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="35" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">START</text>
      <line x1="160" y1="48" x2="160" y2="68" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <polygon points="70,68 250,68 235,108 55,108" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="160" y="94" font-size="13" fill="#1a6fa8" text-anchor="middle" font-weight="bold">INPUT score</text>
      <line x1="160" y1="108" x2="160" y2="128" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <polygon points="160,128 210,168 160,208 110,168" fill="#fef4e8" stroke="#8a5300" stroke-width="2"/>
      <text x="160" y="165" font-size="13" fill="#8a5300" text-anchor="middle" font-weight="bold">score ≥ 50?</text>
      <line x1="110" y1="168" x2="55" y2="168" stroke="#333" stroke-width="1.5"/>
      <line x1="55" y1="168" x2="55" y2="248" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <text x="82" y="158" font-size="12" fill="#059669" font-weight="bold">Yes</text>
      <polygon points="5,248 105,248 95,288 0,288" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="52" y="272" font-size="12" fill="#1a6fa8" text-anchor="middle" font-weight="bold">OUTPUT "Pass"</text>
      <line x1="210" y1="168" x2="265" y2="168" stroke="#333" stroke-width="1.5"/>
      <line x1="265" y1="168" x2="265" y2="248" stroke="#333" stroke-width="1.5" marker-end="url(#alg-arr)"/>
      <text x="238" y="158" font-size="12" fill="#a13544" font-weight="bold">No</text>
      <polygon points="215,248 315,248 305,288 210,288" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>
      <text x="262" y="272" font-size="12" fill="#1a6fa8" text-anchor="middle" font-weight="bold">OUTPUT "Fail"</text>
      <line x1="55" y1="288" x2="55" y2="330" stroke="#333" stroke-width="1.5"/>
      <line x1="265" y1="288" x2="265" y2="330" stroke="#333" stroke-width="1.5"/>
      <line x1="55" y1="330" x2="265" y2="330" stroke="#333" stroke-width="1.5"/>
      {stop_svg}
    '''
    height = 400 if missing_stop else 410
    return _alg_flowchart_svg(inner, aria_label='Flowchart: pass or fail on score', height=height)


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (11 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _alg_f1_abstraction():
    q = (
        "A school app stores each pupil as: <code>name</code>, <code>year_group</code>, "
        "<code>form</code>. The screen only shows the pupil's name and form.<br><br>"
        "Which computational thinking skill is shown by hiding the year group from the display?"
    )
    s = "Hiding unnecessary detail is <strong>abstraction</strong> — focusing on what matters for the task."
    return q, s, "Abstraction removes detail that the user or programmer does not need right now.", 1, _alg_mcq_payload(
        (
            'Abstraction',
            'Abstraction — hiding unnecessary detail',
            'Abstraction — focusing on what matters by hiding unnecessary detail',
        ),
        (
            ('Decomposition', 'Decomposition — breaking a problem into smaller sub-tasks'),
            ('Pattern recognition', 'Pattern recognition — spotting repeating rules in data'),
            ('Binary search', 'Binary search — finding an item in a sorted list by halves'),
        ),
    )


def _alg_f2_decomposition():
    q = (
        "A teacher wants a program to: read five test scores, calculate the average, "
        "and print whether the average is a pass (50 or higher).<br><br>"
        "Put three decomposition sub-tasks in the <strong>correct order</strong>."
    )
    s = (
        "Example decomposition:<br>"
        "1. <strong>Input five scores</strong><br>"
        "2. <strong>Calculate the average</strong><br>"
        "3. <strong>Compare average to 50 and output Pass/Fail</strong>"
    )
    return q, s, "Decomposition means breaking one big problem into smaller, manageable steps.", 2, _alg_order_from_bank(
        (
            'Input five scores',
            'Calculate the average',
            'Compare average to 50 and output Pass/Fail',
        ),
        (
            'Print Pass/Fail before reading any scores',
            'Sort the scores using bubble sort first',
            'Encrypt the scores with a firewall utility',
        ),
        format_hint='Put the three sub-tasks in the correct order',
    )


def _alg_f3_pattern():
    seq = random.choice([
        ([2, 4, 8, 16, 32], 64, "multiply by 2"),
        ([1, 4, 9, 16, 25], 36, "square numbers"),
        ([5, 10, 15, 20, 25], 30, "add 5 each time"),
    ])
    nums, nxt, rule = seq
    q = f"What is the next number in the sequence: <strong>{', '.join(map(str, nums))}, ?</strong>"
    s = f"The pattern is <strong>{rule}</strong>, so the next term is <strong>{nxt}</strong>."
    return q, s, "Pattern recognition means spotting how terms are generated from previous ones.", 1, nxt


def _alg_f4_flowchart_symbol():
    symbols = [
        ("Parallelogram", "Input/Output", "reading or displaying data"),
        ("Diamond", "Decision", "a yes/no or true/false choice"),
        ("Rectangle", "Process", "a calculation or assignment"),
        ("Rounded rectangle", "Start/Stop", "beginning or ending the algorithm"),
    ]
    sym, name, meaning = random.choice(symbols)
    q = f"In a flowchart, a <strong>{sym.lower()}</strong> shape is used for:"
    s = f"A {sym.lower()} represents <strong>{name}</strong> — {meaning}."
    distractors = {
        "Input/Output": (
            ('A yes/no decision', 'A yes/no or true/false decision branch'),
            ('A calculation only', 'A calculation or assignment with no input or output'),
            ('Starting the algorithm only', 'Only beginning the algorithm with no end terminator'),
        ),
        "Decision": (
            ('Reading or displaying data', 'Reading input or displaying output to the user'),
            ('A calculation only', 'A calculation or assignment with no branching'),
            ('Starting or ending only', 'Only beginning or ending the algorithm'),
        ),
        "Process": (
            ('A yes/no decision', 'A yes/no or true/false decision branch'),
            ('Reading or displaying data', 'Reading input or displaying output to the user'),
            ('Starting or ending only', 'Only beginning or ending the algorithm'),
        ),
        "Start/Stop": (
            ('A yes/no decision', 'A yes/no or true/false decision branch'),
            ('Reading or displaying data', 'Reading input or displaying output to the user'),
            ('A calculation only', 'A calculation or assignment in the middle of the algorithm'),
        ),
    }
    return q, s, "Learn the standard GCSE flowchart symbols: terminator, process, decision, I/O.", 1, _alg_mcq_payload(
        (
            name,
            f'{name} — {meaning}',
            f'{name}: {meaning}',
        ),
        distractors[name],
    )


def _alg_f5_pseudocode_output():
    q = (
        "What is printed?<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "count ← 0\nFOR i ← 1 TO 3\n    count ← count + 2\nENDFOR\nOUTPUT count</pre>"
    )
    s = "Loop runs 3 times, adding 2 each time: 0→2→4→6. Output is <strong>6</strong>."
    return q, s, "Trace the loop: how many times it runs and what changes each time.", 2, 6


def _alg_f6_linear_found():
    data = _sorted_unique_list(6)
    target = random.choice(data[1:-1])
    pos = data.index(target) + 1
    q = (
        f"A list contains (in order): <strong>{data}</strong>. "
        f"Linear search looks for <strong>{target}</strong>.<br><br>"
        "How many <strong>comparisons</strong> are made before the item is found "
        "(count each time the target is checked)?"
    )
    s = (
        f"Check each element from the start until {target} is found at position {pos}. "
        f"Comparisons = <strong>{pos}</strong>."
    )
    return q, s, "Linear search checks items one by one from the beginning until found.", 2, pos


def _alg_f7_linear_not_found():
    data = _sorted_unique_list(5)
    target = max(data) + random.choice([3, 7, 11])
    q = (
        f"List: <strong>{data}</strong>. Linear search for <strong>{target}</strong>.<br><br>"
        "How many comparisons are made before the search ends?"
    )
    s = (
        f"Every element is compared; {target} is never found after {len(data)} checks. "
        f"Answer: <strong>{len(data)}</strong> comparisons."
    )
    return q, s, "If the item is absent, linear search still checks every element (unless you stop early).", 2, len(data)


def _alg_f8_bubble_one_pass():
    arr = random.choice([
        [5, 3, 8, 1],
        [9, 2, 7, 4],
        [6, 1, 5, 3],
    ])
    n = len(arr)
    working = arr[:]
    swaps = 0
    for i in range(n - 1):
        if working[i] > working[i + 1]:
            working[i], working[i + 1] = working[i + 1], working[i]
            swaps += 1
    q = (
        f"One pass of bubble sort is performed on <strong>{arr}</strong> "
        "(compare and swap adjacent pairs left to right once).<br><br>"
        "How many <strong>swaps</strong> occur in this pass?"
    )
    s = (
        f"After one pass the list becomes <strong>{working}</strong>. "
        f"Number of swaps = <strong>{swaps}</strong>."
    )
    return q, s, "One pass: walk through adjacent pairs; swap if the left item is larger.", 2, swaps


def _alg_f9_simple_trace():
    q = (
        "Complete the missing value in the trace table.<br>"
        + _trace_table_html(
            ["Step", "x", "y", "OUTPUT"],
            [
                ["1", "3", "5", ""],
                ["2", "3", "8", ""],
                ["3", "3", "8", "?"],
            ],
        )
        + "<br>Pseudocode:<br>"
        "<code>y ← 5<br>x ← 3<br>y ← y + x<br>OUTPUT y</code>"
    )
    s = "After <code>y ← y + x</code>, y becomes 5 + 3 = <strong>8</strong>, which is output."
    return q, s, "Fill trace tables line by line — each row shows values after that step runs.", 2, 8


def _alg_f10_algorithm_definition():
    q = "Which statement best describes an <strong>algorithm</strong>?"
    s = (
        "An algorithm is a <strong>step-by-step method</strong> to solve a problem. "
        "It must be finite, executable, and unambiguous — not just computer code."
    )
    return q, s, "Algorithms can be expressed in English, pseudocode, or flowcharts before coding.", 1, _alg_mcq_payload(
        (
            'A step-by-step method to solve a problem',
            'A finite step-by-step method to solve a problem',
            'A clear, finite sequence of steps that solves a problem',
        ),
        (
            ('A random guess', 'A random guess with no planned steps'),
            ('Only a programming language', 'Only a programming language such as Python'),
            ('A type of virus', 'A type of computer virus that spreads on networks'),
        ),
    )


def _alg_f12_flowchart_fix_decision():
    q = (
        "This flowchart should print <strong>Adult</strong> or <strong>Child</strong> based on "
        "<code>age</code>, but it contains <strong>one error</strong>.<br><br>"
        + _alg_flowchart_age_check_svg(decision='rectangle')
    )
    s = (
        "The step <strong>age ≥ 18?</strong> is a <strong>decision</strong>, so it must be drawn "
        "as a <strong>diamond</strong>, not a rectangle. Rectangles are for processes/calculations; "
        "diamonds are for yes/no choices."
    )
    payload = _alg_mcq_payload(
        (
            'The decision step uses a rectangle instead of a diamond',
            'The age ≥ 18? step should be a diamond, not a rectangle',
            'A yes/no decision is shown in a rectangle — it should be a diamond',
        ),
        (
            ('INPUT age should be a rectangle', 'INPUT age should use a rectangle instead of a parallelogram'),
            ('START should be a diamond', 'The START terminator should be drawn as a diamond'),
            ('The OUTPUT steps should be diamonds', 'The OUTPUT steps should use diamond shapes'),
        ),
    )
    opts = [text.split('  ', 1)[1] for text in payload['options']]
    return q, s, "Decisions use a diamond; processes use a rectangle.", 2, graded_answer_number_fields(
        (payload['correct'],),
        ('What is wrong with this flowchart?',),
        field_types=('mcq',),
        field_options=(opts,),
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (11 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _alg_i2_binary_comparisons():
    n = random.choice([16, 32, 64, 128])
    max_cmp = int(math.ceil(math.log2(n))) if n > 1 else 1
    q = (
        f"A sorted list has <strong>{n}</strong> items. In the worst case, how many comparisons "
        "does a <strong>binary search</strong> need to narrow down to one item?"
    )
    s = (
        f"Each comparison halves the search space. Worst case ≈ log₂({n}) = "
        f"<strong>{max_cmp}</strong> comparisons."
    )
    return q, s, "Binary search halves the remaining items each time — related to log₂(n).", 2, max_cmp


def _alg_i3_binary_next_half():
    data = [2, 5, 9, 14, 18, 23, 27, 31]
    target = random.choice([14, 23])
    lo, hi = 0, len(data) - 1
    steps = []
    while lo <= hi:
        m = (lo + hi) // 2
        steps.append((lo, hi, m, data[m]))
        if data[m] == target:
            break
        if target < data[m]:
            hi = m - 1
        else:
            lo = m + 1
    first = steps[0]
    q = (
        f"Sorted list: <strong>{data}</strong>. Binary search for <strong>{target}</strong>.<br>"
        f"First comparison: middle index {first[2]}, value <strong>{first[3]}</strong>.<br><br>"
        f"Is the next search in the <strong>left half</strong> or <strong>right half</strong>?"
    )
    half = "left half" if target < first[3] else "right half"
    other = "right half" if half == "left half" else "left half"
    s = f"{target} compared to {first[3]} — search continues in the <strong>{half}</strong>."
    return q, s, "If target < middle, go left (lower indices); if target > middle, go right.", 2, _alg_mcq_payload(
        (
            half,
            f'The {half}',
            f'Search continues in the {half}',
        ),
        (
            (other, f'Search continues in the {other}'),
            ('Both halves at once', 'Search both halves of the list at the same time'),
            ('Neither half — restart from index 0', 'Restart the search from the first item every time'),
        ),
    )


def _alg_i4_bubble_after_pass():
    arr = [7, 2, 9, 4, 1]
    working = arr[:]
    for i in range(len(working) - 1):
        if working[i] > working[i + 1]:
            working[i], working[i + 1] = working[i + 1], working[i]
    correct = str(working)
    q = (
        f"After <strong>one complete pass</strong> of bubble sort on <strong>{arr}</strong>, "
        "what is the list?"
    )
    s = f"One pass gives <strong>{working}</strong> (largest value bubbles to the end)."
    return q, s, "After one pass, the biggest number is in the last position.", 2, _alg_mcq_payload(
        (
            correct,
            f'The list is {correct}',
            f'After one pass the list is {correct}',
        ),
        (
            (str(arr), f'The list is unchanged: {arr}'),
            (str(sorted(arr)), f'The list is fully sorted: {sorted(arr)}'),
            (str(arr[::-1]), f'The list is reversed: {arr[::-1]}'),
        ),
    )


def _alg_i5_merge_concept():
    q = (
        "Merge sort splits <strong>[38, 27, 43, 3]</strong> repeatedly into single-item lists, "
        "then merges pairs in sorted order.<br><br>"
        "What are the two lists immediately after the <strong>first merge step</strong> on the left side "
        "(merging [38] and [27])?"
    )
    s = "Merging [38] and [27] gives <strong>[27, 38]</strong> (smaller value first)."
    return q, s, "Merge sort: divide until length 1, then merge sorted sublists.", 2, _alg_mcq_payload(
        (
            '[27, 38]',
            'The merged list [27, 38]',
            'Merging gives the sorted pair [27, 38]',
        ),
        (
            ('[38, 27]', 'The list stays [38, 27] with no reordering'),
            ('[27, 38, 43, 3]', 'The whole original list becomes [27, 38, 43, 3]'),
            ('[3, 27]', 'The merge produces [3, 27] from the left pair'),
        ),
    )


def _alg_i6_trace_if():
    q = (
        "What is output?<br>"
        + _trace_table_html(
            ["Step", "score", "OUTPUT"],
            [["start", "72", ""], ["IF score ≥ 50", "72", ""]],
        )
        + "<br><code>IF score ≥ 50 THEN OUTPUT \"Pass\" ELSE OUTPUT \"Fail\" ENDIF</code> "
        "(score starts at 72)"
    )
    s = "72 ≥ 50 is true, so output is <strong>Pass</strong>."
    return q, s, "Trace the condition: only one branch runs.", 2, _alg_mcq_payload(
        (
            'Pass',
            'OUTPUT "Pass"',
            'The program outputs Pass',
        ),
        (
            ('Fail', 'OUTPUT "Fail"'),
            ('72', 'The program outputs the score 72'),
            ('Nothing', 'The program outputs nothing because the condition fails'),
        ),
    )


def _alg_i7_trace_loop():
    q = (
        "After the loop finishes, what is <strong>total</strong>?<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "total ← 0\nFOR i ← 1 TO 4\n    total ← total + i\nENDFOR</pre>"
    )
    s = "total = 1+2+3+4 = <strong>10</strong>."
    return q, s, "Add each value of i inside the loop; trace i and total each iteration.", 2, 10


def _alg_i8_linear_vs_binary():
    q = (
        "A sorted list of <strong>1 000 000</strong> names is searched many times per second. "
        "Which search is more suitable, and why? Select <strong>two</strong> correct statements."
    )
    s = (
        "<strong>Binary search</strong> — the list is sorted and binary search is much faster "
        "on large lists because it halves the search space each step."
    )
    return q, s, "Binary search needs a sorted list but far fewer comparisons for large data.", 2, _alg_pick_from_bank(
        (
            'Binary search is more suitable because the list is sorted',
            'Binary search is much faster on large lists because it halves the search space each step',
            'Linear search would need far more comparisons on a million-item list',
        ),
        (
            'Linear search is more suitable because the list is sorted',
            'Binary search cannot be used on a sorted list of names',
            'Linear search always halves the search space each comparison',
        ),
        2,
        format_hint='Select two correct statements about the better search',
    )


def _alg_i9_flowchart_to_pseudo():
    q = (
        "A flowchart shows: <strong>Start → Input age → Decision: age ≥ 18? → "
        "Yes: Output \"Adult\" → Stop | No: Output \"Child\" → Stop</strong>.<br><br>"
        "Build the equivalent pseudocode by putting the lines in the <strong>correct order</strong>."
    )
    s = (
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "INPUT age\nIF age &gt;= 18 THEN\n    OUTPUT \"Adult\"\nELSE\n    OUTPUT \"Child\"\nENDIF</pre>"
    )
    return q, s, "Diamond (decision) becomes IF; parallelogram (I/O) becomes INPUT/OUTPUT.", 3, _alg_order_from_bank(
        (
            'INPUT age',
            'IF age >= 18 THEN',
            'OUTPUT "Adult"',
            'ELSE',
            'OUTPUT "Child"',
            'ENDIF',
        ),
        (
            'IF age > 18 THEN',
            'IF age <= 18 THEN',
            'WHILE age >= 18',
            'INPUT "Adult"',
            'OUTPUT age',
            'ELSE IF age < 18 THEN',
        ),
        format_hint='Build the equivalent pseudocode in the correct order',
    )


def _alg_i10_bubble_passes_needed():
    arr = [4, 1, 3, 2]
    q = (
        f"List <strong>{arr}</strong> is sorted using bubble sort (full passes until no swaps). "
        "How many <strong>complete passes</strong> are needed?"
    )
    working = arr[:]
    passes = 0
    while True:
        swapped = False
        for i in range(len(working) - 1):
            if working[i] > working[i + 1]:
                working[i], working[i + 1] = working[i + 1], working[i]
                swapped = True
        passes += 1
        if not swapped:
            break
    s = f"Sorted list is [1,2,3,4] after <strong>{passes}</strong> complete passes."
    return q, s, "Stop when a pass completes with zero swaps.", 3, passes


def _alg_i11_flowchart_fix_symbols():
    q = (
        "This flowchart should read two scores, calculate their average, and output the result. "
        "It contains <strong>two symbol errors</strong>.<br><br>"
        + _alg_flowchart_average_svg(input_shape='rectangle', process_shape='parallelogram')
        + "Select the <strong>two</strong> correct statements describing the errors."
    )
    s = (
        "<strong>INPUT score1, score2</strong> should be a <strong>parallelogram</strong> "
        "(input/output), not a rectangle.<br><br>"
        "The calculation <strong>average ← (score1 + score2) / 2</strong> should be a "
        "<strong>rectangle</strong> (process), not a parallelogram."
    )
    return q, s, "Parallelograms = I/O; rectangles = processes/calculations.", 3, _alg_pick_from_bank(
        (
            'INPUT score1, score2 uses a rectangle — it should be a parallelogram',
            'The average calculation uses a parallelogram — it should be a rectangle',
        ),
        (
            'OUTPUT average should be a rectangle instead of a parallelogram',
            'START should be a diamond instead of a rounded rectangle',
            'STOP is missing from the flowchart',
            'The arrows point in the wrong direction',
        ),
        2,
        format_hint='Select the two symbol errors in this flowchart',
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (16 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _alg_d1_binary_trace():
    data = [3, 7, 11, 15, 19, 23, 27]
    target = 19
    rows = []
    lo, hi = 0, len(data) - 1
    step = 1
    while lo <= hi:
        m = (lo + hi) // 2
        rows.append([str(step), str(lo), str(hi), str(m), str(data[m])])
        if data[m] == target:
            break
        if target < data[m]:
            hi = m - 1
        else:
            lo = m + 1
        step += 1
    q = (
        f"Binary search for <strong>{target}</strong> in <strong>{data}</strong>.<br>"
        "Which row shows the comparison where the target is <strong>found</strong>?<br>"
        + _trace_table_html(["Step", "low", "high", "mid", "list[mid]"], rows)
    )
    found_step = next(i for i, r in enumerate(rows) if r[4] == str(target)) + 1
    s = f"Value {target} is found at step <strong>{found_step}</strong> when mid points to index {rows[found_step-1][3]}."
    return q, s, "Update low/high after each comparison; mid = (low + high) DIV 2.", 3, found_step


def _alg_d2_bubble_trace():
    arr = [5, 1, 4, 2]
    q = f"After <strong>two complete passes</strong> of bubble sort on <strong>{arr}</strong>, what is the list?"
    working = arr[:]
    for _ in range(2):
        for i in range(len(working) - 1):
            if working[i] > working[i + 1]:
                working[i], working[i + 1] = working[i + 1], working[i]
    correct = str(working)
    s = f"After two passes: <strong>{working}</strong>."
    return q, s, "Perform two full left-to-right passes, swapping adjacent pairs when needed.", 3, _alg_mcq_payload(
        (
            correct,
            f'The list is {correct}',
            f'After two passes the list is {correct}',
        ),
        (
            (str(arr), f'The list is unchanged: {arr}'),
            ('[1, 4, 2, 5]', 'After two passes the list is [1, 4, 2, 5]'),
            ('[1, 5, 4, 2]', 'After two passes the list is [1, 5, 4, 2]'),
        ),
    )


def _alg_d3_merge_trace():
    q = (
        "Merge sort is merging <strong>[3, 27]</strong> and <strong>[9, 39]</strong> into one sorted list. "
        "What is the <strong>third value</strong> written to the merged list?"
    )
    s = (
        "Merge picks smaller front items: 3, then 9, then <strong>27</strong> is third "
        "(list so far: 3, 9, 27 …)."
    )
    return q, s, "Compare fronts of both lists; move the smaller, repeat.", 3, 27


def _alg_d4_nested_trace():
    q = (
        "What is <strong>count</strong> when the algorithm ends?<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "count ← 0\nFOR i ← 1 TO 2\n    FOR j ← 1 TO 3\n        count ← count + 1\n    ENDFOR\nENDFOR</pre>"
    )
    s = "Outer runs 2 times, inner 3 each: count = 2×3 = <strong>6</strong>."
    return q, s, "Nested loops multiply: total iterations = outer × inner.", 2, 6


def _alg_d5_efficiency():
    n = random.choice([1000, 1024, 100])
    if n == 1024:
        q = "A sorted list has 1024 items. Worst-case binary search comparisons are about:"
        s = "1024 = 2¹⁰, so about <strong>10</strong> comparisons (log₂ 1024)."
        answer = 10
    else:
        q = f"A sorted list has {n} items. Worst-case <strong>linear</strong> search needs how many comparisons?"
        s = f"In the worst case every item is checked: <strong>{n}</strong> comparisons."
        answer = n
    return q, s, "Linear ∝ n; binary ∝ log₂ n for sorted data.", 2, answer


def _alg_numbered_code_html(lines):
    """Render numbered pseudocode lines for a correct-the-code question."""
    rows = []
    for num, text in lines:
        rows.append(
            f'<tr>'
            f'<td style="padding:4px 10px 4px 0;color:#94a3b8;text-align:right;'
            f'user-select:none;width:2.2em;">{num}</td>'
            f'<td style="padding:4px 0;white-space:pre;font-family:ui-monospace,Consolas,'
            f'monospace;">{text}</td>'
            f'</tr>'
        )
    return (
        '<div style="background:#1e293b;color:#e2e8f0;padding:12px 14px;border-radius:6px;'
        'overflow-x:auto;margin:10px 0;">'
        '<table style="border-collapse:collapse;font-size:.92rem;line-height:1.45;">'
        + ''.join(rows)
        + '</table></div>'
    )


def _alg_d6_pseudocode_binary():
    # Faults baked into this listing:
    # 1) incorrect mid line uses / instead of DIV
    # 2) missing found ← FALSE (should be inserted after line 2)
    # 3) bound updates on lines 8 and 10 are swapped
    buggy_lines = [
        (1, 'low ← 0'),
        (2, 'high ← LEN(list) - 1'),
        (3, 'WHILE low ≤ high AND found = FALSE'),
        (4, '    mid ← (low + high) / 2'),
        (5, '    IF list[mid] = target THEN'),
        (6, '        found ← TRUE'),
        (7, '    ELSE IF list[mid] &lt; target THEN'),
        (8, '        high ← mid - 1'),
        (9, '    ELSE'),
        (10, '        low ← mid + 1'),
        (11, '    ENDIF'),
        (12, 'ENDWHILE'),
    ]
    q = (
        "The pseudocode below is meant to perform a <strong>binary search</strong> on a "
        "sorted list, but it contains <strong>three faults</strong>: "
        "one <strong>incorrect line</strong>, one <strong>missing line</strong>, and "
        "two lines that are in the <strong>wrong order</strong>.<br><br>"
        + _alg_numbered_code_html(buggy_lines)
        + "<strong>a)</strong> Select the incorrect line, then write the corrected line. [2]<br>"
        "<strong>b)</strong> A line is missing. State the line number <em>after which</em> "
        "it should be inserted, then write the missing line. [2]<br>"
        "<strong>c)</strong> Two lines that update the search bounds are swapped. "
        "Enter those two line numbers in ascending order. [2]"
    )
    s = (
        "<strong>a)</strong> Line <strong>4</strong> is wrong. It should be "
        "<code>mid ← (low + high) DIV 2</code> (integer division, not <code>/</code>).<br><br>"
        "<strong>b)</strong> Insert <code>found ← FALSE</code> after line "
        "<strong>2</strong> so the flag is initialised before the loop.<br><br>"
        "<strong>c)</strong> Lines <strong>8</strong> and <strong>10</strong> are swapped. "
        "After <code>ELSE IF list[mid] &lt; target</code> you need "
        "<code>low ← mid + 1</code>; the <code>ELSE</code> branch should use "
        "<code>high ← mid - 1</code>.<br><br>"
        "Correct algorithm:<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "low ← 0\nhigh ← LEN(list) - 1\nfound ← FALSE\nWHILE low ≤ high AND found = FALSE\n"
        "    mid ← (low + high) DIV 2\n    IF list[mid] = target THEN\n"
        "        found ← TRUE\n    ELSE IF list[mid] &lt; target THEN\n"
        "        low ← mid + 1\n    ELSE\n        high ← mid - 1\n    ENDIF\nENDWHILE</pre>"
    )
    wrong_opts, wrong_ans = _alg_mcq_match_field(
        'Line 4: mid ← (low + high) / 2',
        (
            'Line 3: WHILE low ≤ high AND found = FALSE',
            'Line 6: found ← TRUE',
            'Line 12: ENDWHILE',
        ),
    )
    return (
        q, s, "Check initialisation, integer mid calculation, and which bound moves when mid is too small/large.", 6,
        graded_answer_number_fields(
            (
                wrong_ans,
                'mid|(low + high)|div',
                2,
                'found|false',
                8,
                10,
            ),
            (
                'Incorrect line',
                'Corrected line',
                'Insert after line number',
                'Missing line',
                'First swapped line (smaller number)',
                'Second swapped line (larger number)',
            ),
            field_types=('mcq', 'text', 'number', 'text', 'number', 'number'),
            field_options=(wrong_opts, None, None, None, None, None),
            row_sizes=(2, 2, 2),
            group_labels=('(a)', '(b)', '(c)'),
            inline_sections=True,
            format_hint='Enter each correction',
        ),
    )


def _alg_d7_identify_sort():
    q = (
        "A trace shows repeated comparisons of <strong>adjacent</strong> items with swaps, "
        "and after each full pass the largest value moves to the end.<br><br>"
        "Which sorting algorithm is this?"
    )
    s = "Adjacent swaps with largest bubbling right indicates <strong>bubble sort</strong>."
    return q, s, "Bubble sort signature: compare/swap neighbours; biggest reaches the end each pass.", 2, _alg_mcq_payload(
        (
            'Bubble sort',
            'Bubble sort — adjacent swaps bubble the largest to the end',
            'Bubble sort: compare adjacent items and swap so the largest moves to the end each pass',
        ),
        (
            ('Merge sort', 'Merge sort — divide and conquer by splitting then merging'),
            ('Insertion sort', 'Insertion sort — insert each item into a growing sorted section'),
            ('Binary search', 'Binary search — find an item by repeatedly halving a sorted list'),
        ),
    )


def _alg_d8_merge_full():
    q = (
        "Using merge sort on <strong>[8, 3, 5, 1]</strong>, what is the list after the "
        "<strong>second merge level</strong> (when pairs of two are merged)?"
    )
    s = (
        "Splits: [8],[3],[5],[1] → merge pairs → <strong>[3,8]</strong> and <strong>[1,5]</strong> "
        "(two lists of two)."
    )
    return q, s, "First merge combines single items; second merge combines those pairs.", 3, _alg_mcq_payload(
        (
            '[3, 8] and [1, 5]',
            'Two sorted pairs: [3, 8] and [1, 5]',
            'After merging pairs you get [3, 8] and [1, 5]',
        ),
        (
            ('[8, 3] and [5, 1]', 'The pairs stay unsorted as [8, 3] and [5, 1]'),
            ('[1, 3, 5, 8]', 'The list is already fully sorted as [1, 3, 5, 8]'),
            ('[8], [3], [5], [1]', 'Still four single-item lists: [8], [3], [5], [1]'),
        ),
    )


def _alg_d9_compare_searches():
    data = list(range(2, 42, 3))  # 14 items
    target = data[7]
    lin = data.index(target) + 1
    lo, hi, b = 0, len(data) - 1, 0
    while lo <= hi:
        b += 1
        m = (lo + hi) // 2
        if data[m] == target:
            break
        if target < data[m]:
            hi = m - 1
        else:
            lo = m + 1
    q = (
        f"Sorted list of {len(data)} integers; search for <strong>{target}</strong>.<br>"
        f"Linear search: <strong>{lin}</strong> comparisons. Binary search: <strong>{b}</strong> comparisons.<br>"
        "How many <strong>fewer</strong> comparisons does binary search use?"
    )
    s = f"Difference = {lin} − {b} = <strong>{lin - b}</strong> fewer comparisons."
    return q, s, "Subtract binary comparisons from linear for the same target.", 2, lin - b


def _alg_d10_fix_pseudocode():
    q = (
        "This pseudocode should find the largest value in a list but has an error:<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "max ← 0\nFOR i ← 0 TO LEN(list) - 1\n    IF list[i] &gt; max THEN\n"
        "        max ← i\n    ENDIF\nENDFOR\nOUTPUT max</pre><br>"
        "What should line <code>max ← i</code> be?"
    )
    s = "Store the <strong>value</strong>, not the index: <code>max ← list[i]</code>."
    return q, s, "max should hold the largest value found so far, not the position.", 2, _alg_mcq_payload(
        (
            'max ← list[i]',
            'Change it to max ← list[i]',
            'Store the value: max ← list[i]',
        ),
        (
            ('max ← i + 1', 'Change it to max ← i + 1'),
            ('max ← LEN(list)', 'Change it to max ← LEN(list)'),
            ('i ← max', 'Change it to i ← max'),
        ),
    )


def _alg_d11_insertion_pass():
    q = (
        "Insertion sort on <strong>[5, 2, 8, 1]</strong> — after inserting "
        "<strong>2</strong> into the sorted portion, what is the list?"
    )
    s = "Sorted portion becomes <strong>[2, 5]</strong>; full list <strong>[2, 5, 8, 1]</strong>."
    return q, s, "Insertion sort grows a sorted left section one item at a time.", 3, _alg_mcq_payload(
        (
            '[2, 5, 8, 1]',
            'The list is [2, 5, 8, 1]',
            'After inserting 2 the list is [2, 5, 8, 1]',
        ),
        (
            ('[5, 2, 8, 1]', 'The list is unchanged: [5, 2, 8, 1]'),
            ('[1, 2, 5, 8]', 'The list is fully sorted: [1, 2, 5, 8]'),
            ('[2, 5, 1, 8]', 'After inserting 2 the list is [2, 5, 1, 8]'),
        ),
    )


def _alg_d12_while_condition():
    q = (
        "This pseudocode outputs <strong>1, 2, 3, 4</strong> but should stop after <strong>3</strong>. "
        "What should <code>n ≤ 4</code> be changed to?<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "n ← 1\nWHILE n ≤ 4\n    OUTPUT n\n    n ← n + 1\nENDWHILE</pre>"
    )
    s = "Change to <strong>n ≤ 3</strong> so the loop runs for n = 1, 2, 3 only."
    return q, s, "Off-by-one errors often come from using ≤ when you need to stop one step earlier.", 2, _alg_mcq_payload(
        (
            'n ≤ 3',
            'Change the condition to n ≤ 3',
            'Use n ≤ 3 so the loop runs for n = 1, 2, 3 only',
        ),
        (
            ('n ≤ 5', 'Change the condition to n ≤ 5'),
            ('n < 1', 'Change the condition to n < 1'),
            ('n ≥ 4', 'Change the condition to n ≥ 4'),
        ),
    )


def _alg_d15_pseudocode_linear():
    q = (
        "Build <strong>pseudocode</strong> for a linear search that checks each item in "
        "<code>list</code> for <code>target</code> and outputs <code>Found</code> or "
        "<code>Not found</code>. Put the lines in the <strong>correct order</strong>."
    )
    s = (
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "found ← FALSE\nFOR i ← 0 TO LEN(list) - 1\n"
        "    IF list[i] = target THEN\n"
        "        found ← TRUE\n    ENDIF\nENDFOR\n"
        "IF found = TRUE THEN\n    OUTPUT \"Found\"\nELSE\n    OUTPUT \"Not found\"\nENDIF</pre>"
    )
    return q, s, "Use a flag variable or stop when found; GCSE pseudocode often uses FOR with indexes.", 3, _alg_order_from_bank(
        (
            'found ← FALSE',
            'FOR i ← 0 TO LEN(list) - 1',
            'IF list[i] = target THEN',
            'found ← TRUE',
            'ENDIF',
            'ENDFOR',
            'IF found = TRUE THEN',
            'OUTPUT "Found"',
            'ELSE',
            'OUTPUT "Not found"',
            'ENDIF',
        ),
        (
            'found = FALSE',
            'FOR i ← 0 TO LEN(list)',
            'IF list = target THEN',
            'OUTPUT Found',
            'IF found = FALSE THEN',
            'WHILE i < LEN(list)',
            'IF list[i] == target THEN',
        ),
        format_hint='Build the equivalent pseudocode in the correct order',
    )


def _alg_d16_flowchart_fix_multipart():
    q = (
        "This flowchart should classify a user as <strong>Adult</strong> or <strong>Child</strong> "
        "from their age. It contains <strong>three errors</strong>.<br><br>"
        + _alg_flowchart_age_check_svg(decision='rectangle', swap_outputs=True)
        + "<strong>a)</strong> Which step uses the <strong>wrong symbol</strong>? [1]<br>"
        "<strong>b)</strong> What symbol should that step use? [1]<br>"
        "<strong>c)</strong> What is wrong with the <strong>Yes/No branches</strong>? [2]"
    )
    s = (
        "<strong>a)</strong> The <strong>age ≥ 18?</strong> step uses a rectangle — decisions need "
        "a <strong>diamond</strong>.<br><br>"
        "<strong>b)</strong> It should be drawn as a <strong>diamond</strong> (decision symbol)."
        "<br><br>"
        "<strong>c)</strong> The <strong>Yes</strong> and <strong>No</strong> outputs are "
        "swapped: Yes should output <strong>Adult</strong> and No should output "
        "<strong>Child</strong>."
    )
    step_opts, step_ans = _alg_mcq_match_field(
        'The age ≥ 18? decision step',
        (
            'The INPUT age step',
            'The START terminator',
            'The OUTPUT "Adult" step',
        ),
    )
    symbol_opts, symbol_ans = _alg_mcq_match_field(
        'Diamond (decision)',
        (
            'Rectangle (process)',
            'Parallelogram (input/output)',
            'Rounded rectangle (terminator)',
        ),
    )
    branch_opts, branch_ans = _alg_mcq_match_field(
        'The Yes and No outputs are swapped',
        (
            'The START and STOP symbols are swapped',
            'There is no STOP terminator',
            'INPUT and OUTPUT use the same symbol',
        ),
    )
    return (
        q, s, "Check symbol choice and that each branch matches the condition.", 4,
        graded_answer_number_fields(
            (step_ans, symbol_ans, branch_ans),
            ('Wrong-symbol step', 'Correct symbol', 'Branch error'),
            field_types=('mcq', 'mcq', 'mcq'),
            field_options=(step_opts, symbol_opts, branch_opts),
            row_sizes=(1, 1, 1),
            group_labels=('(a)', '(b)', '(c)'),
            inline_sections=True,
        ),
    )


def _alg_i1_pseudocode_linear():
    """Alias for persisted queues that still request the old intermediate name."""
    return _alg_d15_pseudocode_linear()


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _alg_d13_multipart_search_compare():
    data = [4, 9, 15, 22, 31, 47, 56, 68, 79, 90]
    target = 47
    # binary search trace to count comparisons
    lo, hi, comps = 0, len(data) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        comps += 1
        if data[mid] == target:
            break
        elif data[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    linear_comps = data.index(target) + 1
    q = (
        f"A program searches the <strong>sorted</strong> list "
        f"<strong>{data}</strong> for the value <strong>{target}</strong>.<br><br>"
        f"<strong>a)</strong> State the name of a search algorithm that works on a "
        f"sorted list and is faster than linear search. [1]<br>"
        f"<strong>b)</strong> Using that algorithm, state how many comparisons are "
        f"needed to find <strong>{target}</strong>. Show the middle value checked each "
        f"time. [3]<br>"
        f"<strong>c)</strong> Explain why this algorithm would <strong>not</strong> work "
        f"correctly if the list were unsorted. [2]"
    )
    # Build the trace explanation
    lo, hi, lines = 0, len(data) - 1, []
    while lo <= hi:
        mid = (lo + hi) // 2
        lines.append(f"check index {mid} → {data[mid]}")
        if data[mid] == target:
            break
        elif data[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    trace = "; ".join(lines)
    s = (
        f"<strong>a)</strong> <strong>Binary search</strong>.<br><br>"
        f"<strong>b)</strong> {trace}.<br>"
        f"That is <strong>{comps} comparison(s)</strong> "
        f"(linear search would need {linear_comps}).<br><br>"
        f"<strong>c)</strong> Binary search decides which half to discard by assuming "
        f"items are in order. If the list is unsorted, the value being looked for could be "
        f"in the half that gets thrown away, so the algorithm may report it as "
        f"<strong>not found</strong> even when it is present."
    )
    name_opts, name_ans = _alg_mcq_match_field(
        'Binary search',
        ('Linear search', 'Bubble sort', 'Merge sort'),
    )
    why_opts, why_ans = _alg_mcq_match_field(
        'It assumes items are ordered so it may discard the half that still contains the target',
        (
            'Binary search always sorts the list automatically before searching',
            'Binary search only works on lists with an even number of items',
            'Unsorted lists make every comparison take longer on the CPU clock',
        ),
    )
    return (
        q, s, "Binary search checks the middle, then halves the search area each time.", 6,
        graded_answer_number_fields(
            (name_ans, comps, why_ans),
            ('Search algorithm name', 'Number of comparisons', 'Why unsorted fails'),
            field_types=('mcq', 'number', 'mcq'),
            field_options=(name_opts, None, why_opts),
            row_sizes=(1, 1, 1),
            group_labels=('(a)', '(b)', '(c)'),
            inline_sections=True,
        ),
    )


def _alg_d14_multipart_trace_table():
    q = (
        "Study the pseudocode below.<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "total \u2190 0\n"
        "FOR i \u2190 1 TO 4\n"
        "    total \u2190 total + i\n"
        "ENDFOR\n"
        "OUTPUT total</pre>"
        "<strong>a)</strong> Complete a trace table showing the value of "
        "<code>total</code> after each iteration. [3]<br>"
        "<strong>b)</strong> State what the program outputs. [1]<br>"
        "<strong>c)</strong> Describe in one sentence what this algorithm calculates "
        "in general. [2]"
    )
    rows = []
    total = 0
    for i in range(1, 5):
        total += i
        rows.append([str(i), str(total)])
    table = _trace_table_html(["i", "total"], rows)
    s = (
        f"<strong>a)</strong> {table}"
        f"<strong>b)</strong> The program outputs <strong>{total}</strong>.<br><br>"
        f"<strong>c)</strong> It calculates the <strong>sum of the integers from 1 to 4</strong> "
        f"(more generally, the running total of a sequence of numbers)."
    )
    totals = [int(r[1]) for r in rows]
    desc_opts, desc_ans = _alg_mcq_match_field(
        'It calculates the sum of the integers from 1 to 4',
        (
            'It multiplies the integers from 1 to 4 together',
            'It sorts the integers from 1 to 4 into descending order',
            'It counts how many even numbers appear between 1 and 4',
        ),
    )
    return (
        q, s, "Add i to total on each pass: 1, then 1+2, then +3, then +4.", 6,
        graded_answer_number_fields(
            (totals[0], totals[1], totals[2], totals[3], total, desc_ans),
            (
                'total after i=1',
                'total after i=2',
                'total after i=3',
                'total after i=4',
                'Program output',
                'What the algorithm calculates',
            ),
            field_types=('number', 'number', 'number', 'number', 'number', 'mcq'),
            field_options=(None, None, None, None, None, desc_opts),
            row_sizes=(4, 1, 1),
            group_labels=('(a)', '(b)', '(c)'),
            inline_sections=True,
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (22)
# ══════════════════════════════════════════════════════════════════════════════

_ALG_MCQ_BANK = [
    {"q": "Which computational thinking skill breaks a large problem into smaller parts?",
     "correct": (
         "Decomposition",
         "Decomposition — breaking into smaller parts",
         "Decomposition — breaking a large problem into smaller sub-tasks",
     ),
     "wrong": (
         ("Abstraction", "Abstraction — hiding unnecessary detail from the user"),
         ("Pattern recognition", "Pattern recognition — spotting repeating rules in data"),
         ("Translation", "Translation — converting code from one language to another"),
     ),
     "marks": 1,
     "sol": "Breaking into sub-problems is <strong>decomposition</strong>.",
     "hint": "Think ‘divide into steps’."},
    {"q": "Hiding unnecessary detail from the user is called:",
     "correct": (
         "Abstraction",
         "Abstraction — hiding unnecessary detail",
         "Abstraction — focusing on what matters by hiding unnecessary detail",
     ),
     "wrong": (
         ("Decomposition", "Decomposition — breaking a problem into smaller parts"),
         ("Encryption", "Encryption — scrambling data so it cannot be read"),
         ("Compilation", "Compilation — translating source code into machine code"),
     ),
     "marks": 1,
     "sol": "Removing irrelevant detail is <strong>abstraction</strong>.",
     "hint": "Focus on what matters for the task."},
    {"q": "A flowchart diamond shape represents:",
     "correct": (
         "Decision",
         "A decision (yes/no)",
         "A decision — a yes/no or true/false choice",
     ),
     "wrong": (
         ("Start/Stop", "Start/Stop — beginning or ending the algorithm"),
         ("Input/Output", "Input/Output — reading or displaying data"),
         ("Process", "Process — a calculation or assignment"),
     ),
     "marks": 1,
     "sol": "Diamond = <strong>decision</strong> (yes/no).",
     "hint": "Which shape asks a question?"},
    {"q": "Linear search on a list of 20 items. Worst-case comparisons if the item is last?",
     "correct": (
         "20",
         "20 comparisons",
         "20 comparisons — every item is checked in the worst case",
     ),
     "wrong": (
         ("1", "Only 1 comparison is needed in the worst case"),
         ("10", "About 10 comparisons — half the list length"),
         ("19", "19 comparisons — one less than the list length"),
     ),
     "marks": 2,
     "sol": "Worst case checks all <strong>20</strong> items.",
     "hint": "Worst case = item at the end or not found."},
    {"q": "Binary search requires the data to be:",
     "correct": (
         "Sorted",
         "Sorted in order",
         "Sorted so each comparison can discard half the remaining items",
     ),
     "wrong": (
         ("Random", "Stored in a completely random order"),
         ("Even length", "An even number of items only"),
         ("Stored in a graph", "Stored as nodes in a graph structure"),
     ),
     "marks": 1,
     "sol": "Binary search only works on <strong>sorted</strong> data.",
     "hint": "You compare with the middle value and discard half."},
    {"q": "After one complete pass of bubble sort on [4, 2, 7, 1], which statement is true?",
     "correct": (
         "The largest value is at the end",
         "The largest value has bubbled to the end",
         "After one pass the largest value is at the end of the list",
     ),
     "wrong": (
         ("The list is fully sorted", "The list is already fully sorted after one pass"),
         ("No swaps occurred", "No swaps occurred during the pass"),
         ("The smallest value is at the end", "The smallest value has moved to the end"),
     ),
     "marks": 2,
     "sol": "One pass bubbles the largest (7) to the end.",
     "hint": "Bubble sort pushes the biggest value right each pass."},
    {"q": "Merge sort mainly uses which approach?",
     "correct": (
         "Divide and conquer",
         "Divide and conquer — split then merge",
         "Divide and conquer: split the list, sort parts, then merge",
     ),
     "wrong": (
         ("Trial and error", "Trial and error with random guesses until sorted"),
         ("Brute force only", "Brute force only — check every possible order"),
         ("Random swapping", "Random swapping of items until the list looks sorted"),
     ),
     "marks": 1,
     "sol": "Merge sort splits (divide) then merges sorted parts.",
     "hint": "Split in half, sort pieces, merge."},
    {"q": "What is the purpose of a trace table?",
     "correct": (
         "Dry-run an algorithm step by step",
         "To dry-run an algorithm step by step",
         "To dry-run an algorithm and track variable values step by step",
     ),
     "wrong": (
         ("Store passwords", "To store passwords securely on the computer"),
         ("Draw a flowchart", "To draw a flowchart of the algorithm"),
         ("Compress files", "To compress files and save disk space"),
     ),
     "marks": 1,
     "sol": "Trace tables <strong>dry-run</strong> algorithms.",
     "hint": "Track variables after each step."},
    {"q": "Sorted list [2,5,8,11,14,17]. Binary search for 11. First middle value checked?",
     "correct": (
         "8",
         "The first middle value is 8",
         "Mid index (0+5) DIV 2 = 2, so the first middle value checked is 8",
     ),
     "wrong": (
         ("2", "The first middle value checked is 2"),
         ("5", "The first middle value checked is 5"),
         ("11", "The first middle value checked is 11"),
     ),
     "marks": 2,
     "sol": "Mid index of 6 items is 2; value at index 2 is <strong>8</strong>.",
     "hint": "Middle index of 0..5 is 2 (value 8) — GCSE often uses (low+high) DIV 2."},
    {"q": "Which search is generally faster on a large sorted list?",
     "correct": (
         "Binary search",
         "Binary search is generally faster",
         "Binary search — it halves the search space each comparison",
     ),
     "wrong": (
         ("Linear search", "Linear search — checking every item from the start"),
         ("Both the same", "Both searches take the same number of comparisons"),
         ("Neither works", "Neither search works on a sorted list"),
     ),
     "marks": 1,
     "sol": "<strong>Binary search</strong> is O(log n) vs O(n).",
     "hint": "Halving beats checking every item."},
    {"q": "Pseudocode symbol ← usually means:",
     "correct": (
         "Assignment",
         "Assignment — store a value",
         "Assignment — store a value in a variable",
     ),
     "wrong": (
         ("Is equal to (comparison)", "Is equal to — a comparison between two values"),
         ("Output", "Output — display a value to the user"),
         ("Loop start", "Loop start — begin a FOR or WHILE loop"),
     ),
     "marks": 1,
     "sol": "← means <strong>assignment</strong> (store value).",
     "hint": "Same role as = in Python."},
    {"q": "Spotting that exam scores always rise in steps of 5 is:",
     "correct": (
         "Pattern recognition",
         "Pattern recognition — spotting a repeating rule",
         "Pattern recognition — identifying a repeating rule in the data",
     ),
     "wrong": (
         ("Abstraction", "Abstraction — hiding unnecessary detail from the user"),
         ("Decomposition", "Decomposition — breaking a problem into smaller parts"),
         ("Binary search", "Binary search — finding an item in a sorted list"),
     ),
     "marks": 1,
     "sol": "Identifying a rule in data is <strong>pattern recognition</strong>.",
     "hint": "You noticed a repeating rule."},
    {"q": "Bubble sort is best described as:",
     "correct": (
         "Compare adjacent items and swap if wrong order",
         "Compare adjacent pairs and swap if out of order",
         "Compare adjacent items and swap them if they are in the wrong order",
     ),
     "wrong": (
         ("Always divide the list in half first", "Always divide the list in half before sorting"),
         ("Only works on sorted data", "Only works correctly when the data is already sorted"),
         ("Uses a queue data structure", "Uses a queue data structure to store items"),
     ),
     "marks": 1,
     "sol": "Bubble sort compares <strong>adjacent</strong> pairs.",
     "hint": "Think ‘bubble’ to the end."},
    {"q": "FOR i ← 1 TO 3 executes the loop body how many times?",
     "correct": (
         "3",
         "3 times",
         "3 times — i takes the values 1, 2 and 3",
     ),
     "wrong": (
         ("2", "2 times — i stops before reaching 3"),
         ("4", "4 times — one more than the upper bound"),
         ("1", "1 time — the loop body runs only once"),
     ),
     "marks": 1,
     "sol": "i = 1, 2, 3 → <strong>3</strong> times.",
     "hint": "Inclusive range from 1 to 3."},
    {"q": "Which is a benefit of decomposition when writing programs?",
     "correct": (
         "Each sub-task can be built and tested separately",
         "Sub-tasks can be coded and tested separately",
         "Each sub-task can be built and tested separately, making the program easier to manage",
     ),
     "wrong": (
         ("Makes code harder to test", "Makes the finished code harder to test overall"),
         ("Removes the need for algorithms", "Removes the need to design any algorithms"),
         ("Stops you using functions", "Stops you from using functions or procedures"),
     ),
     "marks": 2,
     "sol": "Sub-tasks can be coded and tested <strong>separately</strong>.",
     "hint": "Smaller pieces are easier to manage."},
    {"q": "Insertion sort builds the sorted list by:",
     "correct": (
         "Taking each item and inserting it into the correct place in the sorted part",
         "Inserting each item into the growing sorted section",
         "Taking each item and inserting it into the correct place in the sorted left part",
     ),
     "wrong": (
         ("Repeatedly swapping only the first two items", "Repeatedly swapping only the first two items in the list"),
         ("Always splitting the list in half first", "Always splitting the list in half before sorting"),
         ("Only working on unsorted data", "Only working when the data is already unsorted"),
     ),
     "marks": 2,
     "sol": "Each value is <strong>inserted</strong> into the growing sorted section.",
     "hint": "Think ‘sorted left, unsorted right’."},
    {"q": "A WHILE loop repeats while:",
     "correct": (
         "The condition is True",
         "The condition remains True",
         "The loop condition is True before each iteration",
     ),
     "wrong": (
         ("The condition is False", "The condition is False — then the loop keeps running"),
         ("The counter reaches 10 only", "Only when a counter reaches exactly 10"),
         ("The program compiles", "Only while the program is compiling"),
     ),
     "marks": 1,
     "sol": "WHILE tests the condition <strong>before each iteration</strong>.",
     "hint": "False condition → loop stops."},
    {"q": "Which flowchart symbol represents a process or calculation?",
     "correct": (
         "Rectangle",
         "A rectangle",
         "A rectangle — used for a process or calculation",
     ),
     "wrong": (
         ("Oval", "An oval — used for start/stop"),
         ("Diamond", "A diamond — used for a yes/no decision"),
         ("Parallelogram", "A parallelogram — used for input/output"),
     ),
     "marks": 1,
     "sol": "A <strong>rectangle</strong> is used for processes.",
     "hint": "Oval = start/stop, diamond = decision."},
    {"q": "On an unsorted list of 50 items, binary search:",
     "correct": (
         "Cannot be used correctly",
         "Cannot be used correctly on unsorted data",
         "Cannot be used correctly because binary search requires sorted data",
     ),
     "wrong": (
         ("Is faster than linear search", "Is faster than linear search even when unsorted"),
         ("Always needs exactly 50 comparisons", "Always needs exactly 50 comparisons"),
         ("Sorts the list first automatically", "Sorts the list first automatically then searches"),
     ),
     "marks": 2,
     "sol": "Binary search requires <strong>sorted data</strong>.",
     "hint": "Without sorting, halving the search space fails."},
    {"q": "After two complete passes of bubble sort on [5, 1, 4, 2], the two largest values are:",
     "correct": (
         "At the end of the list",
         "At the end of the list after two passes",
         "Bubbled to the end of the list after two complete passes",
     ),
     "wrong": (
         ("At the start of the list", "Moved to the start of the list"),
         ("Unchanged", "Left unchanged in their original positions"),
         ("Removed from the list", "Removed from the list entirely"),
     ),
     "marks": 2,
     "sol": "Each pass bubbles the next largest value to the <strong>end</strong>.",
     "hint": "Track 5 and 4 moving right after two passes."},
    {"q": "In pseudocode, OUTPUT usually means:",
     "correct": (
         "Display or send a value out",
         "Display or send a value to the user",
         "Display or send a value out to the user or another system",
     ),
     "wrong": (
         ("Read data from the user", "Read data from the user into a variable"),
         ("Assign a variable", "Assign a value to a variable"),
         ("End the program", "End the program immediately"),
     ),
     "marks": 1,
     "sol": "<strong>Output</strong> sends information to the user or another system.",
     "hint": "Contrast with INPUT."},
    {"q": "Which statement best describes an algorithm?",
     "correct": (
         "A step-by-step method to solve a problem",
         "A finite step-by-step method to solve a problem",
         "A clear, finite sequence of steps that solves a problem",
     ),
     "wrong": (
         ("A random guess", "A random guess with no planned steps"),
         ("Only a programming language", "Only a programming language such as Python"),
         ("A type of virus", "A type of computer virus that spreads on networks"),
     ),
     "marks": 1,
     "sol": "An algorithm is a <strong>finite sequence of steps</strong>.",
     "hint": "Must be clear, unambiguous and terminate."},
]


def algorithms_mcq():
    item = random.choice(_ALG_MCQ_BANK)
    opts, ans = _alg_mcq_options(item["correct"], item["wrong"])
    return item["q"], item["sol"], item["hint"], item["marks"], opts, ans


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _alg_f1_abstraction, _alg_f2_decomposition, _alg_f3_pattern,
    _alg_f4_flowchart_symbol, _alg_f5_pseudocode_output,
    _alg_f6_linear_found, _alg_f7_linear_not_found,
    _alg_f8_bubble_one_pass, _alg_f9_simple_trace, _alg_f10_algorithm_definition,
    _alg_f12_flowchart_fix_decision,
]

_INTERMEDIATE = [
    _alg_i2_binary_comparisons, _alg_i3_binary_next_half,
    _alg_i4_bubble_after_pass, _alg_i5_merge_concept, _alg_i6_trace_if,
    _alg_i7_trace_loop, _alg_i8_linear_vs_binary, _alg_i9_flowchart_to_pseudo,
    _alg_i10_bubble_passes_needed, _alg_i11_flowchart_fix_symbols,
]

_DIFFICULT = [
    _alg_d1_binary_trace, _alg_d2_bubble_trace, _alg_d3_merge_trace,
    _alg_d4_nested_trace, _alg_d5_efficiency, _alg_d6_pseudocode_binary,
    _alg_d7_identify_sort, _alg_d8_merge_full, _alg_d9_compare_searches,
    _alg_d10_fix_pseudocode, _alg_d11_insertion_pass, _alg_d12_while_condition,
    _alg_d13_multipart_search_compare, _alg_d14_multipart_trace_table,
    _alg_d15_pseudocode_linear, _alg_d16_flowchart_fix_multipart,
]


def gcse_algorithms_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return [algorithms_mcq] * 10

    pools = {
        "foundational": _FOUNDATIONAL,
        "intermediate": _INTERMEDIATE,
        "difficult": _DIFFICULT,
    }
    if difficulty not in pools:
        return random.sample(_FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT, 10)

    pool = pools[difficulty]
    return random.sample(pool, len(pool))


def gcse_algorithms(difficulty, mode, variant_name=None):
    if mode == "mcq":
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = algorithms_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "algorithms",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_algorithms_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _alg_problem_from_output(variant(), difficulty)
