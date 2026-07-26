"""
GCSE Computer Science – Computer Systems
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Definition-style variants use answer_type text or keyword; structured variants use
pick/order/mcq inline fields or multipart number_fields.
"""
import random
from generators.shared.utils import (
    make_problem,
    graded_answer_keyword,
    graded_answer_number_fields,
    graded_answer_text,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import pick_named_variant


def _cs_raw_number(value):
    if isinstance(value, float):
        val = round(value, 2)
        if val == int(val):
            return str(int(val))
        return f'{val:.2f}'.rstrip('0').rstrip('.')
    return str(int(value))


def _cs_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_cs_raw_number(v) for v in values),
        'labels': tuple(labels),
    }


def _cs_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'cs', 'computer_systems',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        if isinstance(raw, dict):
            extra = problem_extra_from_graded_answer(raw)
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _cs_raw_number(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'computer_systems', **extra
    )


def _cs_mcq_match_field(correct_text, distractors):
    """Shuffled 3-option inline MCQ for term–description matching."""
    pool = [correct_text] + list(distractors[:2])
    random.shuffle(pool)
    letters = 'ABC'
    return pool, letters[pool.index(correct_text)]


def _cs_mcq_payload(correct_text, distractors):
    """Four-option practice MCQ; returns payload for ``_cs_problem_from_output``."""
    pool = [correct_text] + list(distractors[:3])
    random.shuffle(pool)
    letters = 'ABCD'
    correct_letter = letters[pool.index(correct_text)]
    options = [f'{letters[i]}  {pool[i]}' for i in range(len(pool))]
    return {'type': 'mcq', 'options': options, 'correct': correct_letter}


def _cs_order_field(steps, distractors):
    """Inline ordered steps field for ``number_fields`` (returns raw, bank)."""
    step_ids = tuple(f's{i + 1}' for i in range(len(steps)))
    bank = [{'id': sid, 'text': text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    raw = f"1|{'|'.join(step_ids)}"
    return raw, bank


def _cs_pick_from_bank(correct_texts, distractor_texts, pick_count, *, format_hint=None):
    """Shuffled option bank: pick exactly ``pick_count`` correct statements."""
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


def _cs_order_from_bank(steps, distractors, *, format_hint=None):
    """Shuffled bank: put the correct steps in order."""
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


def _cs_pick_field(correct_texts, distractor_texts, pick_count):
    """Inline pick-N field for ``number_fields`` (returns raw, bank, count)."""
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    raw = f"pick|{pick_count}|{'|'.join(correct_ids)}"
    return raw, bank, pick_count


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cs_f1_cpu_alu():
    q = "What is the main job of the <strong>ALU</strong> (Arithmetic Logic Unit)?"
    s = "The ALU performs <strong>calculations and logical comparisons</strong> (e.g. add, subtract, AND)."
    return q, s, "ALU = arithmetic + logic operations on data.", 1, graded_answer_text('calculations', 'logic')


def _cs_f2_cpu_cu():
    q = "What does the <strong>Control Unit</strong> coordinate?"
    s = (
        "The CU <strong>controls and coordinates</strong> how data moves and which "
        "operations happen — it manages the fetch-decode-execute cycle."
    )
    return q, s, "Think of the CU as the conductor of the CPU.", 1, graded_answer_text('controls', 'coordinates')


def _cs_f3_ram_vs_rom():
    q = "Which memory is <strong>volatile</strong> and holds programs/data while the computer is running?"
    s = "<strong>RAM</strong> (Random Access Memory) — contents are lost when power is off."
    return q, s, "Volatile = lost without power; RAM is working memory.", 1, graded_answer_keyword('ram')


def _cs_f4_rom_use():
    q = "Give one typical use of <strong>ROM</strong> in a computer."
    s = "Stores the <strong>BIOS/UEFI firmware</strong> (bootstrap instructions to start the computer)."
    return q, s, "ROM is non-volatile — needed before the OS loads.", 2, graded_answer_text('bios', 'firmware')


def _cs_f5_fde_order():
    q = (
        "Put the stages of one CPU cycle in the correct order: "
        "<strong>Execute, Fetch, Decode</strong>."
    )
    s = "Correct order: <strong>Fetch → Decode → Execute</strong>."
    return q, s, "F-D-E repeats billions of times per second.", 1, _cs_order_from_bank(
        (
            'Fetch',
            'Decode',
            'Execute',
        ),
        (
            'Execute before the instruction is fetched',
            'Decode after execute in every cycle',
            'Fetch after execute in every cycle',
        ),
        format_hint='Put Fetch, Decode, and Execute in the correct order',
    )


def _cs_f6_register():
    q = "What is a <strong>CPU register</strong>?"
    s = (
        "A very <strong>small, extremely fast</strong> storage location inside the CPU "
        "holding one item (e.g. current instruction or data being processed)."
    )
    return q, s, "Registers are faster than RAM but hold much less.", 1, _cs_mcq_payload(
        'A very small, extremely fast storage location inside the CPU holding one item',
        [
            'Main working memory (RAM) shared by all running programs',
            'Non-volatile secondary storage used for long-term files (e.g. hard drive or SSD)',
            'Firmware stored in ROM that starts the computer when power is switched on',
        ],
    )


def _cs_f7_os_definition():
    q = "What is an <strong>operating system</strong>?"
    s = (
        "System software that <strong>manages hardware and software resources</strong> "
        "(memory, processes, files, security) and provides a platform for applications."
    )
    return q, s, "Examples: Windows, macOS, Linux, Android.", 1, graded_answer_text('manages', 'resources')


def _cs_f8_input_device():
    devices = [
        ("keyboard", "entering text"),
        ("microphone", "capturing sound"),
        ("touchscreen", "touch input"),
        ("barcode scanner", "reading product codes"),
    ]
    dev, use = random.choice(devices)
    q = f"Is a <strong>{dev}</strong> an input or output device? State its main purpose."
    s = f"<strong>Input</strong> — {use}."
    return q, s, "Input sends data into the computer.", 1, graded_answer_keyword('input')


def _cs_f9_ssd_hdd():
    q = "Which storage uses <strong>flash memory</strong> with no moving parts: HDD or SSD?"
    s = "<strong>SSD</strong> (Solid State Drive)."
    return q, s, "HDD uses spinning magnetic platters.", 1, graded_answer_keyword('ssd')


def _cs_f10_embedded():
    q = "Name <strong>one example</strong> of an embedded system. Select one correct example."
    s = "Examples: <strong>washing machine controller, car airbag system, fitness tracker, microwave timer</strong> (any valid dedicated device)."
    return q, s, "Embedded = computer built into a single-purpose device.", 1, _cs_pick_from_bank(
        (
            'Washing machine controller',
            'Car airbag control system',
            'Fitness tracker',
            'Microwave oven timer/controller',
            'Engine management system in a car',
        ),
        (
            'Desktop PC running a general-purpose operating system',
            'Web browser on a laptop',
            'Spreadsheet software package',
        ),
        1,
        format_hint='Select one embedded system example',
    )


def _cs_f11_fde_stage_count():
    q = (
        "How many main stages are there in one cycle of the "
        "<strong>fetch–decode–execute</strong> (FDE) cycle?"
    )
    s = "The three stages are <strong>Fetch → Decode → Execute</strong>."
    return q, s, "F-D-E repeats billions of times per second.", 1, 3


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cs_i1_von_neumann():
    q = (
        "In the <strong>Von Neumann model</strong>, programs and data share the same memory. "
        "Select two correct statements about this design."
    )
    s = (
        "<strong>Stored program</strong> concept. Programs and data use the same bus/memory, "
        "so the CPU cannot fetch code and data at the same time — <strong>Von Neumann bottleneck</strong>."
    )
    return q, s, "Harvard architecture (separate buses) avoids this but is less common in GCSE PCs.", 3, _cs_pick_from_bank(
        (
            'Programs and instructions are stored in the same memory as data (stored program concept)',
            'The CPU cannot fetch code and data at the same time over the same bus',
            'This shared path can create a Von Neumann bottleneck',
        ),
        (
            'Programs and data always use completely separate memory with no shared bus',
            'The Von Neumann model removes the need for a Program Counter',
            'Data and instructions are always fetched in parallel with no delay',
        ),
        2,
        format_hint='Select two correct statements',
    )


def _cs_i11_pc_after_fetch():
    pc = random.choice([100, 150, 200, 250])
    next_pc = pc + 1
    q = (
        f"The <strong>Program Counter</strong> holds <strong>{pc}</strong>. "
        f"One instruction is fetched from that address (each instruction uses one address). "
        f"What value should the Program Counter hold <strong>after</strong> the fetch stage?"
    )
    s = (
        f"During fetch the instruction at address {pc} is copied to the CIR and the PC is "
        f"incremented to <strong>{next_pc}</strong> ready for the next instruction."
    )
    return q, s, "PC usually increases by 1 during fetch when each instruction is one address.", 2, next_pc


def _cs_i12_clock_billion_cycles():
    clock = random.choice([2.0, 2.5, 3.0, 3.6])
    q = (
        f"A CPU core runs at <strong>{clock} GHz</strong>. "
        f"How many <strong>billion</strong> fetch–decode–execute cycles can that core "
        f"perform in one second?"
    )
    s = (
        f"<strong>{clock} GHz</strong> means <strong>{clock}</strong> billion cycles "
        f"per second on that core."
    )
    return q, s, "1 GHz = 1 billion cycles per second per core.", 2, clock


def _cs_i2_cache_purpose():
    q = "Why does the CPU use <strong>cache memory</strong>? Select one correct reason."
    s = (
        "Cache stores <strong>frequently used instructions and data</strong> very close to the CPU, "
        "faster than RAM — reduces waiting time."
    )
    return q, s, "L1/L2/L3 cache — smaller but much faster than main memory.", 2, _cs_pick_from_bank(
        (
            'Stores frequently used instructions and data very close to the CPU',
            'Provides faster access than RAM for data the CPU needs often',
            'Reduces waiting time by keeping common data near the processor',
        ),
        (
            'Replaces RAM completely so main memory is not needed',
            'Stores the BIOS firmware before the operating system loads',
            'Increases the clock speed measured in GHz',
        ),
        1,
        format_hint='Select one correct reason',
    )


def _cs_i3_virtual_memory():
    q = "What is <strong>virtual memory</strong> and when is it used?"
    s = (
        "Uses <strong>secondary storage as extra “RAM”</strong> when physical RAM is full. "
        "Slower than real RAM but lets large programs/multitasking run."
    )
    return q, s, "Pages swapped between RAM and disk.", 2, graded_answer_text('secondary', 'storage')


def _cs_i4_os_functions():
    funcs = random.choice([
        ("memory management", "allocates RAM to programs and frees it when finished", ('memory', 'allocates')),
        ("process management", "schedules which program runs on the CPU and when", ('process', 'schedules')),
        ("file management", "organises files/folders on storage devices", ('file', 'organises')),
        ("security", "user accounts, permissions, and protection from malware", ('security', 'accounts')),
    ])
    name, desc, keywords = funcs
    q = f"Describe the OS role of <strong>{name}</strong>."
    s = f"<strong>{name.capitalize()}:</strong> {desc}."
    return q, s, "Exams often list four: memory, processor, file, security/device management.", 2, graded_answer_text(*keywords)


def _cs_i5_utility_software():
    q = (
        "Give <strong>two examples</strong> of utility software and what each does. "
        "Select two correct examples."
    )
    s = (
        "Examples: <strong>antivirus</strong> (scans for malware), <strong>disk defragmenter</strong> "
        "(reorganises files on HDD), <strong>backup tool</strong>, <strong>file compression (ZIP)</strong>."
    )
    return q, s, "Utilities maintain or optimise the system — not the same as the OS kernel.", 2, _cs_pick_from_bank(
        (
            'Antivirus software — scans for malware',
            'Disk defragmenter — reorganises files on an HDD',
            'Backup tool — copies files for recovery',
            'File compression (ZIP) — reduces file sizes',
        ),
        (
            'Operating system kernel — manages all hardware directly',
            'Word processor — used to write documents',
            'Web browser — used to view websites',
        ),
        2,
        format_hint='Select two utility software examples',
    )


def _cs_i6_storage_compare():
    q = "Give <strong>one advantage of SSD</strong> over HDD for a laptop. Select one correct advantage."
    s = "SSDs are <strong>faster</strong>, more <strong>durable</strong> (no moving parts), and use <strong>less power</strong> — better battery life."
    return q, s, "Pick one clear advantage and link to the scenario.", 2, _cs_pick_from_bank(
        (
            'Faster access because there are no moving parts',
            'More durable — no mechanical read/write head to damage',
            'Uses less power — better battery life in a laptop',
        ),
        (
            'Always cheaper per terabyte than an HDD',
            'Must be defragmented regularly to stay fast',
            'Uses spinning magnetic platters like an HDD',
        ),
        1,
        format_hint='Select one advantage of SSD over HDD',
    )


def _cs_i7_clock_cores():
    q = (
        "CPU A: 3.0 GHz, 4 cores. CPU B: 2.5 GHz, 8 cores. "
        "Which may be better for running many programs at once? Select one answer."
    )
    s = (
        "<strong>CPU B</strong> — more <strong>cores</strong> help true multitasking/parallel work "
        "(clock speed alone does not double performance)."
    )
    return q, s, "GHz = cycles per second per core; cores = parallel processing units.", 2, _cs_pick_from_bank(
        (
            'CPU B — more cores help run many programs at once (multitasking/parallel work)',
            'CPU B — eight cores can handle more parallel tasks even at a lower clock speed',
        ),
        (
            'CPU A — higher clock speed always beats more cores for multitasking',
            'Neither — the number of cores does not affect multitasking',
            'CPU A — four cores are always better than eight cores',
        ),
        1,
        format_hint='Select the best answer',
    )


def _cs_i8_fetch_step():
    q = "During the <strong>Fetch</strong> stage of the FDE cycle, what happens? Select one correct statement."
    s = (
        "The next <strong>instruction is copied from memory</strong> (address in the Program Counter) "
        "into the <strong>Current Instruction Register (CIR)</strong>."
    )
    return q, s, "PC points to where to fetch; MAR/MBR often used with memory.", 2, _cs_pick_from_bank(
        (
            'The next instruction is copied from memory into the Current Instruction Register (CIR)',
            'The instruction at the address in the Program Counter is fetched from memory',
        ),
        (
            'The ALU performs arithmetic on the result of the last instruction',
            'The operating system loads before any instruction is fetched',
            'The Program Counter is reset to zero during fetch',
        ),
        1,
        format_hint='Select what happens during Fetch',
    )


def _cs_i9_app_vs_system():
    q = (
        "Is <strong>Microsoft Word</strong> application software or system software? "
        "Select one correct answer."
    )
    s = "<strong>Application software</strong> — it helps the user write documents; it is not managing the whole computer."
    return q, s, "System software includes OS and utilities.", 1, _cs_pick_from_bank(
        (
            'Application software — it helps the user write documents',
        ),
        (
            'System software — it manages hardware and runs the whole computer',
            'System software — it includes the operating system kernel',
            'Firmware stored in ROM that starts the computer on power-up',
        ),
        1,
        format_hint='Select application or system software',
    )


def _cs_i10_secondary_primary():
    q = "Why is a USB flash drive classed as <strong>secondary storage</strong> not primary?"
    s = (
        "It is <strong>non-volatile</strong> and used for long-term file storage, "
        "not the main working memory the CPU uses during execution (RAM)."
    )
    return q, s, "Primary = RAM (and cache/registers); secondary = persistent storage.", 2, graded_answer_text('non-volatile', 'secondary')


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cs_d1_fde_full_trace():
    q = (
        "Program Counter = 100. Memory at address 100 holds instruction <code>LOAD 5</code>. "
        "Assume each instruction occupies one memory address.<br><br>"
        "Put what happens during <strong>fetch</strong>, <strong>decode</strong>, and "
        "<strong>execute</strong> in the correct order."
    )
    s = (
        "<strong>Fetch:</strong> instruction at 100 → CIR; PC becomes <strong>101</strong>. "
        "<strong>Decode:</strong> control unit interprets LOAD 5. "
        "<strong>Execute:</strong> value 5 loaded into register."
    )
    return q, s, "PC usually increments during fetch so the next instruction is ready.", 4, _cs_order_from_bank(
        (
            'Fetch: instruction at address 100 is copied to the CIR; PC becomes 101',
            'Decode: the control unit interprets the LOAD 5 instruction',
            'Execute: the value 5 is loaded into a register',
        ),
        (
            'Execute: the value 5 is loaded before the instruction is decoded',
            'Fetch: the Program Counter decrements to 99',
            'Decode: the operating system loads before the instruction is fetched',
        ),
        format_hint='Put the fetch–decode–execute steps in the correct order',
    )


def _cs_d2_ram_capacity():
    ram = random.choice([4, 8, 16])
    needed = ram + random.choice([2, 4, 6])
    shortfall = needed - ram
    q = (
        f"A PC has <strong>{ram} GB RAM</strong>. The programs a user opens need "
        f"<strong>{needed} GB</strong> in total. "
        f"How many gigabytes <strong>over</strong> the physical RAM limit is this?"
    )
    s = (
        f"{needed} − {ram} = <strong>{shortfall} GB</strong> over the installed RAM. "
        f"The OS may use <strong>virtual memory</strong> on secondary storage, "
        f"which runs slower than real RAM."
    )
    return q, s, "When RAM is full, swapping to disk avoids crashing.", 3, shortfall


def _cs_d3_embedded_constraints():
    q = (
        "Give <strong>two reasons</strong> why embedded systems often use specialised hardware "
        "instead of a full PC. Select two correct reasons."
    )
    s = (
        "<strong>Lower cost/power/size</strong> for one task; <strong>reliability</strong> "
        "(dedicated firmware, no general desktop OS needed)."
    )
    return q, s, "Think washing machine vs gaming PC.", 3, _cs_pick_from_bank(
        (
            'Lower cost because the hardware is designed for one dedicated task',
            'Lower power use and better battery life for a single purpose',
            'Smaller, more compact hardware that fits the device',
            'More reliable with dedicated firmware and no general desktop OS needed',
        ),
        (
            'Easier to run a full desktop operating system with many apps',
            'More RAM and storage than a general-purpose PC',
            'Users can install any application from an app store',
            'Requires a constant internet connection before it can boot',
        ),
        2,
        format_hint='Select two correct reasons',
    )


def _cs_d4_optical_storage():
    q = (
        "When is <strong>optical storage</strong> (DVD/Blu-ray) still a sensible choice? "
        "Select one correct answer."
    )
    s = (
        "Distributing <strong>read-only media</strong> cheaply (films, software installers) "
        "where large capacity and portability matter; less common now due to downloads/cloud."
    )
    return q, s, "Optical = laser reads pits on disc; slower than SSD.", 2, _cs_pick_from_bank(
        (
            'Distributing read-only media cheaply (e.g. films, software installers)',
            'When large capacity and portability matter for distribution',
            'Sharing content that does not need to be edited after burning',
        ),
        (
            'When the fastest possible random access speed is required',
            'As the main working memory while programs run',
            'When data must be erased and rewritten millions of times daily',
        ),
        1,
        format_hint='Select one sensible use of optical storage',
    )


def _cs_d5_heat_sink():
    q = "Why does a high-performance CPU need a <strong>heat sink</strong> and fan?"
    s = (
        "Fast CPUs produce <strong>heat</strong>; cooling prevents <strong>overheating</strong> "
        "that would cause thermal throttling or damage."
    )
    return q, s, "More GHz/cores → more heat → need cooling.", 2, graded_answer_text('heat', 'cooling')


def _cs_d6_multitasking_os():
    q = (
        "Explain how the OS allows <strong>multitasking</strong> on a single-core CPU. "
        "Put the steps in the correct order."
    )
    s = (
        "<strong>Time slicing</strong> — rapidly switches between processes so each gets a turn "
        "on the CPU; appears simultaneous to the user."
    )
    return q, s, "Scheduler allocates small time slots per process.", 3, _cs_order_from_bank(
        (
            'The OS uses time slicing to give each process a short turn on the CPU',
            'The OS rapidly switches between processes',
            'It appears to the user that programs run at the same time',
        ),
        (
            'Each program runs to completion before the next one starts',
            'The CPU runs all processes on separate physical cores',
            'Multitasking requires at least four CPU cores',
        ),
        format_hint='Put the multitasking steps in the correct order',
    )


def _cs_d7_hdd_defrag():
    q = (
        "Why is <strong>defragmentation</strong> mainly relevant to HDDs, not SSDs? "
        "Select two correct reasons."
    )
    s = (
        "HDDs are slow when files are split across the disc; defrag <strong>reorders clusters</strong>. "
        "SSDs have no mechanical head — defrag gives little benefit and can <strong>wear</strong> flash cells."
    )
    return q, s, "Mechanical movement vs random access flash.", 3, _cs_pick_from_bank(
        (
            'HDDs are slow when files are split across the disc — defrag reorders clusters',
            'HDDs have a mechanical read/write head that moves across the platter',
            'SSDs have no mechanical head — defrag gives little benefit',
            'Defragmentation on SSDs can wear out flash memory cells',
        ),
        (
            'SSDs must be defragmented weekly to stay fast',
            'HDDs store data using laser-read pits like optical discs',
            'Defragmentation increases the clock speed of the CPU',
        ),
        2,
        format_hint='Select two correct reasons',
    )


def _cs_d8_bios_role():
    q = (
        "What does <strong>BIOS/UEFI firmware</strong> do before the operating system loads? "
        "Put the steps in the correct order."
    )
    s = (
        "<strong>POST</strong> (Power-On Self-Test), detects hardware, lets user change basic settings, "
        "then <strong>boots</strong> the OS from storage."
    )
    return q, s, "Firmware in ROM/flash — first code that runs on power-on.", 3, _cs_order_from_bank(
        (
            'Run POST (Power-On Self-Test) to check the system',
            'Detect and identify hardware components',
            'Allow the user to change basic settings if needed',
            'Boot the operating system from storage',
        ),
        (
            'Load the user\'s applications before checking hardware',
            'Start multitasking between programs before POST finishes',
            'Run the fetch–decode–execute cycle before any hardware checks',
        ),
        format_hint='Put the startup steps in the correct order',
    )


def _cs_d9_address_bus():
    q = "What is carried on the <strong>address bus</strong>?"
    s = "The <strong>memory location address</strong> the CPU wants to read from or write to (not the data itself)."
    return q, s, "Data bus carries data; control bus carries signals.", 2, graded_answer_text('address', 'memory')


def _cs_d10_open_source_os():
    q = "Give <strong>one benefit</strong> and <strong>one drawback</strong> of open-source operating systems (e.g. Linux)."
    s = (
        "<strong>Benefit:</strong> free to use/modify, community support, transparent code. "
        "<strong>Drawback:</strong> fewer commercial applications/drivers for some hardware, steeper learning curve."
    )
    return q, s, "Open source = source code available under licence.", 3, graded_answer_number_fields(
        (
            '1@free|modify|community|support|transparent|licence|license|cost|open',
            '1@commercial|application|applications|driver|drivers|hardware|learning|curve|steep|difficult|compatible|compatibility|fewer',
        ),
        ('Benefit', 'Drawback'),
        field_types=('text', 'text'),
        format_hint='Enter your answer',
    )


def _cs_d11_control_bus():
    q = "What signals travel on the <strong>control bus</strong>? Select one correct answer."
    s = (
        "Control signals such as <strong>read/write</strong>, <strong>interrupt</strong>, "
        "and <strong>clock</strong> pulses that coordinate CPU and memory — not addresses or data values."
    )
    return q, s, "Address bus = location; data bus = data; control bus = commands/timing.", 2, _cs_pick_from_bank(
        (
            'Control and timing signals such as read/write and interrupt',
            'Clock pulses that coordinate the CPU and memory',
            'Commands that tell components when to read or write — not the data itself',
        ),
        (
            'Memory addresses the CPU wants to read from or write to',
            'The actual data values being transferred between components',
            'User passwords and login credentials',
        ),
        1,
        format_hint='Select what travels on the control bus',
    )


def _cs_d12_multi_core():
    q = (
        "A CPU has <strong>4 cores</strong> but one heavy program does not run 4× faster. "
        "Give <strong>two reasons</strong> why. Select two correct reasons."
    )
    s = (
        "<strong>1)</strong> The program may not be written to use multiple cores in parallel. "
        "<strong>2)</strong> Parts of the task may be sequential (one step waits for another) "
        "or share memory/buses, limiting speed-up."
    )
    return q, s, "More cores help only when work can run in parallel.", 3, _cs_pick_from_bank(
        (
            'The program may not be written to use multiple cores in parallel',
            'Parts of the task may be sequential — one step waits for another',
            'Tasks may share memory or buses, limiting speed-up from extra cores',
        ),
        (
            'Every program automatically uses all cores equally from the moment it starts',
            'Four cores always make every program run exactly four times faster',
            'More cores increase the clock speed measured in GHz',
            'Multicore CPUs do not need any operating system support',
        ),
        2,
        format_hint='Select two correct reasons',
    )


def _cs_d15_core_count():
    cores = random.choice([2, 4, 6, 8])
    threads = cores * 2
    q = (
        f"A CPU has <strong>{cores} cores</strong> and supports two threads per core "
        f"(hyper-threading). How many <strong>threads</strong> can run at the same time?"
    )
    s = (
        f"{cores} cores × 2 threads per core = <strong>{threads}</strong> hardware threads."
    )
    return q, s, "Threads per core × number of cores.", 2, threads


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _cs_d13_multipart_cpu_performance():
    clock = random.choice([2.4, 3.0, 3.6])
    cores = random.choice([2, 4, 8])
    cache = random.choice([4, 8, 16])
    q = (
        f"A laptop's CPU is advertised as: <strong>{clock} GHz</strong>, "
        f"<strong>{cores} cores</strong>, <strong>{cache} MB cache</strong>.<br><br>"
        f"<strong>a)</strong> Explain what the <strong>clock speed of {clock} GHz</strong> "
        f"tells you about the CPU. [2]<br>"
        f"<strong>b)</strong> Explain how having <strong>{cores} cores</strong> can improve "
        f"performance. Select a reason, then the consequence — in the correct order. [2]<br>"
        f"<strong>c)</strong> Explain how a larger <strong>cache</strong> improves "
        f"performance. Select a reason, then the consequence — in the correct order. [2]"
    )
    s = (
        f"<strong>a)</strong> Clock speed is the number of "
        f"<strong>fetch–decode–execute cycles per second</strong>. "
        f"{clock} GHz means about {clock} billion cycles each second, so a higher clock "
        f"speed generally means more instructions processed per second.<br><br>"
        f"<strong>b)</strong> Each core can fetch and execute instructions "
        f"<strong>independently</strong>, so multiple instructions or programs can be "
        f"processed <strong>at the same time</strong> (true parallel processing), as long "
        f"as the software is written to use multiple cores.<br><br>"
        f"<strong>c)</strong> Cache is fast memory close to the CPU. A larger cache stores "
        f"<strong>more frequently used instructions and data</strong>, so the CPU has to "
        f"fetch from slower RAM <strong>less often</strong>, reducing waiting time."
    )
    clock_opts, clock_ans = _cs_mcq_match_field(
        f"The CPU can perform about {clock:g} billion fetch–decode–execute cycles per second",
        [
            f"The CPU has {cores} independent processing units that share one cache",
            f"The CPU has {cache} megabytes of fast memory built into the chip",
        ],
    )
    cores_raw, cores_bank = _cs_order_field(
        (
            'Each core can fetch and execute instructions independently',
            'Multiple instructions or programs can be processed at the same time (parallel processing)',
        ),
        (
            'All programs always run twice as fast automatically with more cores',
            'More cores mean the clock speed in GHz is multiplied',
            'Cores are fast memory that stores frequently used data close to the CPU',
        ),
    )
    cache_raw, cache_bank = _cs_order_field(
        (
            'A larger cache stores more frequently used instructions and data close to the CPU',
            'The CPU has to fetch from slower RAM less often, reducing waiting time',
        ),
        (
            'Cache replaces RAM completely so main memory is no longer needed',
            'A larger cache increases the clock speed measured in GHz',
            'Cache memory keeps its contents when the power is switched off',
        ),
    )
    return q, s, "Clock = cycles/second, cores = parallel work, cache = fast nearby memory.", 6, graded_answer_number_fields(
        (clock_ans, cores_raw, cache_raw),
        ('Clock speed', 'Multiple cores', 'Cache'),
        field_types=('mcq', 'order', 'order'),
        field_options=(clock_opts, cores_bank, cache_bank),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


def _cs_d14_multipart_memory():
    q = (
        "A computer has <strong>RAM</strong>, <strong>ROM</strong>, and "
        "<strong>virtual memory</strong>.<br><br>"
        "<strong>a)</strong> State one difference between RAM and ROM in terms of "
        "<strong>volatility</strong>. Select one correct statement. [2]<br>"
        "<strong>b)</strong> Explain what <strong>virtual memory</strong> is and when it "
        "is used. [2]<br>"
        "<strong>c)</strong> Explain why using a lot of virtual memory can make a computer "
        "<strong>run slowly</strong>. [2]"
    )
    s = (
        "<strong>a)</strong> RAM is <strong>volatile</strong> — it loses its contents when "
        "power is switched off. ROM is <strong>non-volatile</strong> — it keeps its "
        "contents without power.<br><br>"
        "<strong>b)</strong> Virtual memory is space on <strong>secondary storage</strong> "
        "(e.g. the hard disk/SSD) used as if it were RAM. It is used when the RAM becomes "
        "<strong>full</strong>, by moving data not currently needed out of RAM to make "
        "room.<br><br>"
        "<strong>c)</strong> Secondary storage is <strong>much slower</strong> than RAM, and "
        "constantly moving data between RAM and disk (\u201cdisk thrashing\u201d) takes time, "
        "so the computer slows down."
    )
    volatility_raw, volatility_bank, volatility_pick = _cs_pick_field(
        (
            'RAM is volatile — it loses its contents when power is switched off',
            'ROM is non-volatile — it keeps its contents without power',
        ),
        (
            'RAM is non-volatile and keeps firmware when power is off',
            'ROM is volatile and loses all data when power is switched off',
            'Both RAM and ROM lose their contents immediately when power is off',
        ),
        1,
    )
    return q, s, "RAM = volatile working memory; virtual memory uses slow disk space as extra RAM.", 6, graded_answer_number_fields(
        (
            volatility_raw,
            '1@secondary|storage|full|ram|disk|hard|swap|page',
            '1@slower|secondary|thrash|thrashing|disk|swap|moving',
        ),
        ('Volatility', 'Virtual memory', 'Why it slows down'),
        field_types=('pick', 'text', 'text'),
        field_options=(volatility_bank, None, None),
        field_pick_counts=(volatility_pick, None, None),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_CS_MCQ_BANK = [
    {"q": "Which component performs arithmetic operations?",
     "opts": ["A  Control Unit", "B  ALU", "C  Hard drive", "D  Cache only"],
     "ans": "B", "marks": 1,
     "sol": "The <strong>ALU</strong> does calculations. Answer: B",
     "hint": "Arithmetic Logic Unit."},
    {"q": "Correct order of the fetch-decode-execute cycle:",
     "opts": ["A  Decode, Fetch, Execute", "B  Fetch, Decode, Execute",
              "C  Execute, Fetch, Decode", "D  Fetch, Execute, Decode"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Fetch → Decode → Execute</strong>. Answer: B",
     "hint": "F-D-E."},
    {"q": "RAM is described as volatile because:",
     "opts": ["A  it is very expensive", "B  data is lost when power is off",
              "C  it cannot be upgraded", "D  it stores the BIOS"],
     "ans": "B", "marks": 1,
     "sol": "Volatile = <strong>lost without power</strong>. Answer: B",
     "hint": "Contrast with ROM."},
    {"q": "Which is secondary storage?",
     "opts": ["A  Cache", "B  Register", "C  RAM", "D  SSD"],
     "ans": "D", "marks": 1,
     "sol": "<strong>SSD</strong> is non-volatile secondary storage. Answer: D",
     "hint": "Long-term, not working memory."},
    {"q": "Virtual memory uses:",
     "opts": ["A  cache only", "B  secondary storage as extension of RAM",
              "C  registers only", "D  ROM instead of RAM"],
     "ans": "B", "marks": 2,
     "sol": "Disk space acts as extra RAM. Answer: B",
     "hint": "Swapping pages to disk."},
    {"q": "An operating system is best described as:",
     "opts": ["A  a word processor", "B  hardware inside the CPU",
              "C  system software managing resources", "D  a web browser"],
     "ans": "C", "marks": 1,
     "sol": "OS = <strong>system software</strong>. Answer: C",
     "hint": "Manages memory, files, processes."},
    {"q": "Which is utility software?",
     "opts": ["A  Windows kernel", "B  Antivirus scanner", "C  CPU", "D  Spreadsheet"],
     "ans": "B", "marks": 2,
     "sol": "Antivirus is a <strong>utility</strong>. Answer: B",
     "hint": "Maintains or protects the system."},
    {"q": "Embedded systems are designed to:",
     "opts": ["A  run any program from the internet",
              "B  perform one dedicated function within a device",
              "C  replace the operating system on PCs", "D  only store photos"],
     "ans": "B", "marks": 1,
     "sol": "Dedicated <strong>single-purpose</strong> control. Answer: B",
     "hint": "Microwave, car ECU, etc."},
    {"q": "Cache memory is placed close to the CPU to:",
     "opts": ["A  store the BIOS", "B  speed up access to frequent data",
              "C  replace the hard drive", "D  cool the processor"],
     "ans": "B", "marks": 2,
     "sol": "Cache = <strong>fast, small</strong> buffer. Answer: B",
     "hint": "Faster than RAM."},
    {"q": "During FETCH, the instruction is loaded into the:",
     "opts": ["A  Hard drive", "B  Current Instruction Register",
              "C  Monitor", "D  Power supply"],
     "ans": "B", "marks": 2,
     "sol": "Fetched instruction → <strong>CIR</strong>. Answer: B",
     "hint": "Also PC points to next address."},
    {"q": "A higher clock speed (GHz) generally means:",
     "opts": ["A  more instructions per second per core",
              "B  more storage space", "C  less heat", "D  longer battery always"],
     "ans": "A", "marks": 2,
     "sol": "More cycles per second → <strong>faster processing</strong> per core. Answer: A",
     "hint": "GHz = billion cycles per second."},
    {"q": "ROM is typically used for:",
     "opts": ["A  temporary web browsing tabs", "B  firmware / bootstrap code",
              "C  saving user documents", "D  virtual memory"],
     "ans": "B", "marks": 2,
     "sol": "ROM holds <strong>startup firmware</strong>. Answer: B",
     "hint": "Non-volatile, rarely changes."},
    {"q": "SSD vs HDD — a clear advantage of SSD is:",
     "opts": ["A  moving parts for reliability", "B  faster access with no moving parts",
              "C  always cheaper per terabyte", "D  must be defragmented weekly"],
     "ans": "B", "marks": 2,
     "sol": "SSD = flash, <strong>faster, no mechanics</strong>. Answer: B",
     "hint": "No read/write head."},
    {"q": "The Von Neumann bottleneck relates to:",
     "opts": ["A  shared memory/bus for data and instructions",
              "B  monitor resolution", "C  keyboard layout", "D  printer ink"],
     "ans": "A", "marks": 2,
     "sol": "Same memory path limits speed. Answer: A",
     "hint": "Stored program architecture."},
    {"q": "Application software is:",
     "opts": ["A  the operating system kernel", "B  programs for end-user tasks",
              "C  the CPU", "D  cache memory"],
     "ans": "B", "marks": 1,
     "sol": "Apps = <strong>user tasks</strong> (browser, games). Answer: B",
     "hint": "Not system software."},
    {"q": "The control bus carries:",
     "opts": ["A  memory addresses only", "B  control and timing signals",
              "C  pixel colours", "D  user passwords"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Control/timing</strong> signals. Answer: B",
     "hint": "Not the data values themselves."},
    {"q": "A quad-core processor has:",
     "opts": ["A  four separate processing units on one chip", "B  four hard drives",
              "C  four monitors", "D  four operating systems always"],
     "ans": "A", "marks": 1,
     "sol": "<strong>Four cores</strong> on one CPU package. Answer: A",
     "hint": "Core = processing unit."},
    {"q": "The Program Counter (PC) holds:",
     "opts": ["A  the address of the next instruction", "B  the result of the last calculation",
              "C  the monitor resolution", "D  the hard drive capacity"],
     "ans": "A", "marks": 2,
     "sol": "PC points to the <strong>next instruction address</strong>. Answer: A",
     "hint": "Updated during the fetch stage."},
    {"q": "Which bus carries memory addresses?",
     "opts": ["A  Data bus", "B  Address bus", "C  Control bus only", "D  Power bus"],
     "ans": "B", "marks": 2,
     "sol": "The <strong>address bus</strong> locates memory. Answer: B",
     "hint": "Data bus carries values; address bus carries locations."},
    {"q": "An input device is used to:",
     "opts": ["A  send data into the computer", "B  display results only",
              "C  store data permanently", "D  cool the processor"],
     "ans": "A", "marks": 1,
     "sol": "Input devices <strong>enter data</strong> into the system. Answer: A",
     "hint": "Keyboard, microphone, sensor."},
    {"q": "Optical storage (e.g. DVD) reads data using:",
     "opts": ["A  magnetic heads", "B  a laser and reflected light",
              "C  only flash memory cells", "D  liquid cooling"],
     "ans": "B", "marks": 2,
     "sol": "Laser reads <strong>pits and lands</strong> on the disc surface. Answer: B",
     "hint": "Contrast with HDD magnetic platters."},
    {"q": "A heat sink on a CPU is used to:",
     "opts": ["A  increase clock speed directly", "B  dissipate heat away from the processor",
              "C  store instructions", "D  connect to the internet"],
     "ans": "B", "marks": 2,
     "sol": "Spreads heat to keep the CPU <strong>cooler</strong>. Answer: B",
     "hint": "Often paired with a fan."},
]


def computer_systems_mcq():
    item = random.choice(_CS_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _cs_f1_cpu_alu, _cs_f2_cpu_cu, _cs_f3_ram_vs_rom, _cs_f4_rom_use,
    _cs_f5_fde_order, _cs_f6_register, _cs_f7_os_definition,
    _cs_f8_input_device, _cs_f9_ssd_hdd, _cs_f10_embedded,
    _cs_f11_fde_stage_count,
]

_INTERMEDIATE = [
    _cs_i1_von_neumann, _cs_i2_cache_purpose, _cs_i3_virtual_memory,
    _cs_i4_os_functions, _cs_i5_utility_software, _cs_i6_storage_compare,
    _cs_i7_clock_cores, _cs_i8_fetch_step, _cs_i9_app_vs_system,
    _cs_i10_secondary_primary, _cs_i11_pc_after_fetch, _cs_i12_clock_billion_cycles,
]

_DIFFICULT = [
    _cs_d1_fde_full_trace, _cs_d2_ram_capacity, _cs_d3_embedded_constraints,
    _cs_d4_optical_storage, _cs_d5_heat_sink, _cs_d6_multitasking_os,
    _cs_d7_hdd_defrag, _cs_d8_bios_role, _cs_d9_address_bus,
    _cs_d10_open_source_os, _cs_d11_control_bus, _cs_d12_multi_core,
    _cs_d13_multipart_cpu_performance, _cs_d14_multipart_memory,
    _cs_d15_core_count,
]


def gcse_computer_systems_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return [computer_systems_mcq] * 10

    pools = {
        "foundational": _FOUNDATIONAL,
        "intermediate": _INTERMEDIATE,
        "difficult": _DIFFICULT,
    }
    if difficulty not in pools:
        return random.sample(_FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT, 10)

    pool = pools[difficulty]
    return random.sample(pool, len(pool))


def gcse_computer_systems(difficulty, mode, variant_name=None):
    if mode == "mcq":
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = computer_systems_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "computer_systems",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_computer_systems_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _cs_problem_from_output(variant(), difficulty)
