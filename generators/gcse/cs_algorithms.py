"""
GCSE Computer Science – Fundamentals of Algorithms
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Text / pseudocode-writing variants stay as 4-tuples (Phase 2).
"""
import random
import math
from generators.shared.utils import make_problem
from generators.shared.variant_utils import pick_named_variant


def _alg_raw_number(value):
    return str(int(value))


def _alg_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_alg_raw_number(v) for v in values),
        'labels': tuple(labels),
    }


def _alg_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            if values and len(values) == len(labels):
                extra = {
                    'correct_answer_raw': '|'.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_format_hint': 'Enter a number in every field',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _alg_raw_number(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'algorithms', **extra
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


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _alg_f1_abstraction():
    q = (
        "A school app stores each pupil as: <code>name</code>, <code>year_group</code>, "
        "<code>form</code>. The screen only shows the pupil's name and form.<br><br>"
        "Which computational thinking skill is shown by hiding the year group from the display?"
    )
    s = "Hiding unnecessary detail is <strong>abstraction</strong> — focusing on what matters for the task."
    return q, s, "Abstraction removes detail that the user or programmer does not need right now.", 1


def _alg_f2_decomposition():
    q = (
        "A teacher wants a program to: read five test scores, calculate the average, "
        "and print whether the average is a pass (50 or higher).<br><br>"
        "Write <strong>three sub-tasks</strong> (in order) that decomposition might produce."
    )
    s = (
        "Example decomposition:<br>"
        "1. <strong>Input five scores</strong><br>"
        "2. <strong>Calculate the average</strong><br>"
        "3. <strong>Compare average to 50 and output Pass/Fail</strong>"
    )
    return q, s, "Decomposition means breaking one big problem into smaller, manageable steps.", 2


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
        ("Parallelogram", "Input/Output", "B"),
        ("Diamond", "Decision", "C"),
        ("Rectangle", "Process", "A"),
        ("Rounded rectangle", "Start/Stop", "D"),
    ]
    sym, name, _ = random.choice(symbols)
    q = f"In a flowchart, a <strong>{sym.lower()}</strong> shape is used for:"
    opts_map = {
        "Input/Output": "reading or displaying data",
        "Decision": "a yes/no or true/false choice",
        "Process": "a calculation or assignment",
        "Start/Stop": "beginning or ending the algorithm",
    }
    s = f"A {sym.lower()} represents <strong>{name}</strong> — {opts_map[name]}."
    return q, s, "Learn the standard GCSE flowchart symbols: terminator, process, decision, I/O.", 1


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
    return q, s, "Algorithms can be expressed in English, pseudocode, or flowcharts before coding.", 1


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _alg_i1_pseudocode_linear():
    q = (
        "Write <strong>pseudocode</strong> for a linear search that checks each item in "
        "<code>list</code> for <code>target</code> and outputs <code>Found</code> or <code>Not found</code>."
    )
    s = (
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "found ← FALSE\nFOR i ← 0 TO LEN(list) - 1\n"
        "    IF list[i] = target THEN\n"
        "        found ← TRUE\n    ENDIF\nENDFOR\n"
        "IF found = TRUE THEN\n    OUTPUT \"Found\"\nELSE\n    OUTPUT \"Not found\"\nENDIF</pre>"
    )
    return q, s, "Use a flag variable or stop when found; GCSE pseudocode often uses FOR with indexes.", 3


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
    mid = 14 if target == 14 else 23
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
    s = f"{target} compared to {first[3]} — search continues in the <strong>{half}</strong>."
    return q, s, "If target < middle, go left (lower indices); if target > middle, go right.", 2


def _alg_i4_bubble_after_pass():
    arr = [7, 2, 9, 4, 1]
    working = arr[:]
    for i in range(len(working) - 1):
        if working[i] > working[i + 1]:
            working[i], working[i + 1] = working[i + 1], working[i]
    q = (
        f"After <strong>one complete pass</strong> of bubble sort on <strong>{arr}</strong>, "
        "what is the list?"
    )
    s = f"One pass gives <strong>{working}</strong> (largest value bubbles to the end)."
    return q, s, "After one pass, the biggest number is in the last position.", 2


def _alg_i5_merge_concept():
    q = (
        "Merge sort splits <strong>[38, 27, 43, 3]</strong> repeatedly into single-item lists, "
        "then merges pairs in sorted order.<br><br>"
        "What are the two lists immediately after the <strong>first merge step</strong> on the left side "
        "(merging [38] and [27])?"
    )
    s = "Merging [38] and [27] gives <strong>[27, 38]</strong> (smaller value first)."
    return q, s, "Merge sort: divide until length 1, then merge sorted sublists.", 2


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
    return q, s, "Trace the condition: only one branch runs.", 2


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
        "Which search is more suitable: <strong>linear</strong> or <strong>binary</strong>? "
        "Give one reason."
    )
    s = (
        "<strong>Binary search</strong> — the list is sorted and binary search is much faster "
        "on large lists because it halves the search space each step."
    )
    return q, s, "Binary search needs a sorted list but far fewer comparisons for large data.", 2


def _alg_i9_flowchart_to_pseudo():
    q = (
        "A flowchart shows: <strong>Start → Input age → Decision: age ≥ 18? → "
        "Yes: Output \"Adult\" → Stop | No: Output \"Child\" → Stop</strong>.<br><br>"
        "Write equivalent pseudocode."
    )
    s = (
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "INPUT age\nIF age ≥ 18 THEN\n    OUTPUT \"Adult\"\nELSE\n    OUTPUT \"Child\"\nENDIF</pre>"
    )
    return q, s, "Diamond (decision) becomes IF; parallelogram (I/O) becomes INPUT/OUTPUT.", 3


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


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10 variants)
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
    s = f"After two passes: <strong>{working}</strong>."
    return q, s, "Perform two full left-to-right passes, swapping adjacent pairs when needed.", 3


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


def _alg_d6_pseudocode_binary():
    q = "Write pseudocode for <strong>binary search</strong> on a sorted list (assume list and target exist)."
    s = (
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "low ← 0\nhigh ← LEN(list) - 1\nfound ← FALSE\nWHILE low ≤ high AND found = FALSE\n"
        "    mid ← (low + high) DIV 2\n    IF list[mid] = target THEN\n"
        "        found ← TRUE\n    ELSE IF list[mid] &lt; target THEN\n"
        "        low ← mid + 1\n    ELSE\n        high ← mid - 1\n    ENDIF\nENDWHILE</pre>"
    )
    return q, s, "Keep low/high bounds; adjust based on comparison with list[mid].", 4


def _alg_d7_identify_sort():
    q = (
        "A trace shows repeated comparisons of <strong>adjacent</strong> items with swaps, "
        "and after each full pass the largest value moves to the end.<br><br>"
        "Which sorting algorithm is this?"
    )
    s = "Adjacent swaps with largest bubbling right indicates <strong>bubble sort</strong>."
    return q, s, "Bubble sort signature: compare/swap neighbours; biggest reaches the end each pass.", 2


def _alg_d8_merge_full():
    q = (
        "Using merge sort on <strong>[8, 3, 5, 1]</strong>, what is the list after the "
        "<strong>second merge level</strong> (when pairs of two are merged)?"
    )
    s = (
        "Splits: [8],[3],[5],[1] → merge pairs → <strong>[3,8]</strong> and <strong>[1,5]</strong> "
        "(two lists of two)."
    )
    return q, s, "First merge combines single items; second merge combines those pairs.", 3


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
    return q, s, "max should hold the largest value found so far, not the position.", 2


def _alg_d11_insertion_pass():
    q = (
        "Insertion sort on <strong>[5, 2, 8, 1]</strong> — after inserting "
        "<strong>2</strong> into the sorted portion, what is the list?"
    )
    s = "Sorted portion becomes <strong>[2, 5]</strong>; full list <strong>[2, 5, 8, 1]</strong>."
    return q, s, "Insertion sort grows a sorted left section one item at a time.", 3


def _alg_d12_while_condition():
    q = (
        "This pseudocode outputs <strong>1, 2, 3, 4</strong> but should stop after <strong>3</strong>. "
        "What should <code>n ≤ 4</code> be changed to?<br>"
        "<pre style='background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;'>"
        "n ← 1\nWHILE n ≤ 4\n    OUTPUT n\n    n ← n + 1\nENDWHILE</pre>"
    )
    s = "Change to <strong>n ≤ 3</strong> so the loop runs for n = 1, 2, 3 only."
    return q, s, "Off-by-one errors often come from using ≤ when you need to stop one step earlier.", 2


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
    return (
        q, s, "Binary search checks the middle, then halves the search area each time.", 6,
        _alg_fields_answer(
            (comps,),
            ('Part (b): number of comparisons to find the target',),
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
    return (
        q, s, "Add i to total on each pass: 1, then 1+2, then +3, then +4.", 6,
        _alg_fields_answer(
            (total,),
            ('Part (b): value output by the program',),
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_ALG_MCQ_BANK = [
    {"q": "Which computational thinking skill breaks a large problem into smaller parts?",
     "opts": ["A  Abstraction", "B  Decomposition", "C  Pattern recognition", "D  Translation"],
     "ans": "B", "marks": 1,
     "sol": "Breaking into sub-problems is <strong>decomposition</strong>. Answer: B",
     "hint": "Think ‘divide into steps’."},
    {"q": "Hiding unnecessary detail from the user is called:",
     "opts": ["A  Decomposition", "B  Encryption", "C  Abstraction", "D  Compilation"],
     "ans": "C", "marks": 1,
     "sol": "Removing irrelevant detail is <strong>abstraction</strong>. Answer: C",
     "hint": "Focus on what matters for the task."},
    {"q": "A flowchart diamond shape represents:",
     "opts": ["A  Start/Stop", "B  Input/Output", "C  Process", "D  Decision"],
     "ans": "D", "marks": 1,
     "sol": "Diamond = <strong>decision</strong> (yes/no). Answer: D",
     "hint": "Which shape asks a question?"},
    {"q": "Linear search on a list of 20 items. Worst-case comparisons if the item is last?",
     "opts": ["A  1", "B  10", "C  19", "D  20"],
     "ans": "D", "marks": 2,
     "sol": "Worst case checks all <strong>20</strong> items. Answer: D",
     "hint": "Worst case = item at the end or not found."},
    {"q": "Binary search requires the data to be:",
     "opts": ["A  Sorted", "B  Random", "C  Even length", "D  Stored in a graph"],
     "ans": "A", "marks": 1,
     "sol": "Binary search only works on <strong>sorted</strong> data. Answer: A",
     "hint": "You compare with the middle value and discard half."},
    {"q": "After one complete pass of bubble sort on [4, 2, 7, 1], which statement is true?",
     "opts": ["A  The list is fully sorted", "B  The largest value is at the end",
              "C  No swaps occurred", "D  The smallest value is at the end"],
     "ans": "B", "marks": 2,
     "sol": "One pass bubbles the largest (7) to the end. Answer: <strong>B</strong>",
     "hint": "Bubble sort pushes the biggest value right each pass."},
    {"q": "Merge sort mainly uses which approach?",
     "opts": ["A  Divide and conquer", "B  Trial and error", "C  Brute force only",
              "D  Random swapping"],
     "ans": "A", "marks": 1,
     "sol": "Merge sort splits (divide) then merges sorted parts. Answer: A",
     "hint": "Split in half, sort pieces, merge."},
    {"q": "What is the purpose of a trace table?",
     "opts": ["A  Store passwords", "B  Dry-run an algorithm step by step",
              "C  Draw a flowchart", "D  Compress files"],
     "ans": "B", "marks": 1,
     "sol": "Trace tables <strong>dry-run</strong> algorithms. Answer: B",
     "hint": "Track variables after each step."},
    {"q": "Sorted list [2,5,8,11,14,17]. Binary search for 11. First middle value checked?",
     "opts": ["A  2", "B  5", "C  8", "D  11"],
     "ans": "C", "marks": 2,
     "sol": "Mid index of 6 items is 2 or 3; value at index 2 is <strong>8</strong> (0-based: index 2 is 8). Answer: C",
     "hint": "Middle index of 0..5 is 2 (value 8) or 3 depending on rounding — GCSE often uses (low+high) DIV 2."},
    {"q": "Which search is generally faster on a large sorted list?",
     "opts": ["A  Linear search", "B  Binary search", "C  Both the same", "D  Neither works"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Binary search</strong> is O(log n) vs O(n). Answer: B",
     "hint": "Halving beats checking every item."},
    {"q": "Pseudocode symbol ← usually means:",
     "opts": ["A  Is equal to (comparison)", "B  Assignment", "C  Output", "D  Loop start"],
     "ans": "B", "marks": 1,
     "sol": "← means <strong>assignment</strong> (store value). Answer: B",
     "hint": "Same role as = in Python."},
    {"q": "Spotting that exam scores always rise in steps of 5 is:",
     "opts": ["A  Abstraction", "B  Decomposition", "C  Pattern recognition", "D  Binary search"],
     "ans": "C", "marks": 1,
     "sol": "Identifying a rule in data is <strong>pattern recognition</strong>. Answer: C",
     "hint": "You noticed a repeating rule."},
    {"q": "Bubble sort is best described as:",
     "opts": ["A  Compare adjacent items and swap if wrong order",
              "B  Always divide the list in half first",
              "C  Only works on sorted data", "D  Uses a queue data structure"],
     "ans": "A", "marks": 1,
     "sol": "Bubble sort compares <strong>adjacent</strong> pairs. Answer: A",
     "hint": "Think ‘bubble’ to the end."},
    {"q": "FOR i ← 1 TO 3 executes the loop body how many times?",
     "opts": ["A  2", "B  3", "C  4", "D  1"],
     "ans": "B", "marks": 1,
     "sol": "i = 1, 2, 3 → <strong>3</strong> times. Answer: B",
     "hint": "Inclusive range from 1 to 3."},
    {"q": "Which is a benefit of decomposition when writing programs?",
     "opts": ["A  Makes code harder to test", "B  Each sub-task can be built and tested separately",
              "C  Removes the need for algorithms", "D  Stops you using functions"],
     "ans": "B", "marks": 2,
     "sol": "Sub-tasks can be coded and tested <strong>separately</strong>. Answer: B",
     "hint": "Smaller pieces are easier to manage."},
    {"q": "Insertion sort builds the sorted list by:",
     "opts": ["A  repeatedly swapping only the first two items",
              "B  taking each item and inserting it into the correct place in the sorted part",
              "C  always splitting the list in half first", "D  only working on unsorted data"],
     "ans": "B", "marks": 2,
     "sol": "Each value is <strong>inserted</strong> into the growing sorted section. Answer: B",
     "hint": "Think ‘sorted left, unsorted right’."},
    {"q": "A WHILE loop repeats while:",
     "opts": ["A  the condition is True", "B  the condition is False",
              "C  the counter reaches 10 only", "D  the program compiles"],
     "ans": "A", "marks": 1,
     "sol": "WHILE tests the condition <strong>before each iteration</strong>. Answer: A",
     "hint": "False condition → loop stops."},
    {"q": "Which flowchart symbol represents a process or calculation?",
     "opts": ["A  Oval", "B  Rectangle", "C  Diamond", "D  Parallelogram"],
     "ans": "B", "marks": 1,
     "sol": "A <strong>rectangle</strong> is used for processes. Answer: B",
     "hint": "Oval = start/stop, diamond = decision."},
    {"q": "On an unsorted list of 50 items, binary search:",
     "opts": ["A  is faster than linear search", "B  cannot be used correctly",
              "C  always needs exactly 50 comparisons", "D  sorts the list first automatically"],
     "ans": "B", "marks": 2,
     "sol": "Binary search requires <strong>sorted data</strong>. Answer: B",
     "hint": "Without sorting, halving the search space fails."},
    {"q": "After two complete passes of bubble sort on [5, 1, 4, 2], the two largest values are:",
     "opts": ["A  at the start of the list", "B  at the end of the list",
              "C  unchanged", "D  removed from the list"],
     "ans": "B", "marks": 2,
     "sol": "Each pass bubbles the next largest value to the <strong>end</strong>. Answer: B",
     "hint": "Track 5 and 4 moving right after two passes."},
    {"q": "In pseudocode, OUTPUT usually means:",
     "opts": ["A  read data from the user", "B  display or send a value out",
              "C  assign a variable", "D  end the program"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Output</strong> sends information to the user or another system. Answer: B",
     "hint": "Contrast with INPUT."},
    {"q": "Which statement best describes an algorithm?",
     "opts": ["A  a random guess", "B  a step-by-step method to solve a problem",
              "C  only a programming language", "D  a type of virus"],
     "ans": "B", "marks": 1,
     "sol": "An algorithm is a <strong>finite sequence of steps</strong>. Answer: B",
     "hint": "Must be clear, unambiguous and terminate."},
]


def algorithms_mcq():
    item = random.choice(_ALG_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _alg_f1_abstraction, _alg_f2_decomposition, _alg_f3_pattern,
    _alg_f4_flowchart_symbol, _alg_f5_pseudocode_output,
    _alg_f6_linear_found, _alg_f7_linear_not_found,
    _alg_f8_bubble_one_pass, _alg_f9_simple_trace, _alg_f10_algorithm_definition,
]

_INTERMEDIATE = [
    _alg_i1_pseudocode_linear, _alg_i2_binary_comparisons, _alg_i3_binary_next_half,
    _alg_i4_bubble_after_pass, _alg_i5_merge_concept, _alg_i6_trace_if,
    _alg_i7_trace_loop, _alg_i8_linear_vs_binary, _alg_i9_flowchart_to_pseudo,
    _alg_i10_bubble_passes_needed,
]

_DIFFICULT = [
    _alg_d1_binary_trace, _alg_d2_bubble_trace, _alg_d3_merge_trace,
    _alg_d4_nested_trace, _alg_d5_efficiency, _alg_d6_pseudocode_binary,
    _alg_d7_identify_sort, _alg_d8_merge_full, _alg_d9_compare_searches,
    _alg_d10_fix_pseudocode, _alg_d11_insertion_pass, _alg_d12_while_condition,
    _alg_d13_multipart_search_compare, _alg_d14_multipart_trace_table,
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
