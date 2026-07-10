"""
GCSE Computer Science – Computer Systems
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
Final answers wrapped in <strong> tags.
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import pick_named_variant


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cs_f1_cpu_alu():
    q = "What is the main job of the <strong>ALU</strong> (Arithmetic Logic Unit)?"
    s = "The ALU performs <strong>calculations and logical comparisons</strong> (e.g. add, subtract, AND)."
    return q, s, "ALU = arithmetic + logic operations on data.", 1


def _cs_f2_cpu_cu():
    q = "What does the <strong>Control Unit</strong> coordinate?"
    s = (
        "The CU <strong>controls and coordinates</strong> how data moves and which "
        "operations happen — it manages the fetch-decode-execute cycle."
    )
    return q, s, "Think of the CU as the conductor of the CPU.", 1


def _cs_f3_ram_vs_rom():
    q = "Which memory is <strong>volatile</strong> and holds programs/data while the computer is running?"
    s = "<strong>RAM</strong> (Random Access Memory) — contents are lost when power is off."
    return q, s, "Volatile = lost without power; RAM is working memory.", 1


def _cs_f4_rom_use():
    q = "Give one typical use of <strong>ROM</strong> in a computer."
    s = "Stores the <strong>BIOS/UEFI firmware</strong> (bootstrap instructions to start the computer)."
    return q, s, "ROM is non-volatile — needed before the OS loads.", 2


def _cs_f5_fde_order():
    q = "Put these in order for one cycle of the CPU: <strong>Execute, Fetch, Decode</strong>."
    s = "Correct order: <strong>Fetch → Decode → Execute</strong>."
    return q, s, "F-D-E repeats billions of times per second.", 1


def _cs_f6_register():
    q = "What is a <strong>CPU register</strong>?"
    s = (
        "A very <strong>small, extremely fast</strong> storage location inside the CPU "
        "holding one item (e.g. current instruction or data being processed)."
    )
    return q, s, "Registers are faster than RAM but hold much less.", 1


def _cs_f7_os_definition():
    q = "What is an <strong>operating system</strong>?"
    s = (
        "System software that <strong>manages hardware and software resources</strong> "
        "(memory, processes, files, security) and provides a platform for applications."
    )
    return q, s, "Examples: Windows, macOS, Linux, Android.", 1


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
    return q, s, "Input sends data into the computer.", 1


def _cs_f9_ssd_hdd():
    q = "Which storage uses <strong>flash memory</strong> with no moving parts: HDD or SSD?"
    s = "<strong>SSD</strong> (Solid State Drive)."
    return q, s, "HDD uses spinning magnetic platters.", 1


def _cs_f10_embedded():
    q = "Name <strong>one example</strong> of an embedded system."
    s = "Examples: <strong>washing machine controller, car airbag system, fitness tracker, microwave timer</strong> (any valid dedicated device)."
    return q, s, "Embedded = computer built into a single-purpose device.", 1


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cs_i1_von_neumann():
    q = (
        "In the <strong>Von Neumann model</strong>, programs and data share the same memory. "
        "What is this design called, and why can it slow the CPU?"
    )
    s = (
        "<strong>Stored program</strong> concept. Programs and data use the same bus/memory, "
        "so the CPU cannot fetch code and data at the same time — <strong>Von Neumann bottleneck</strong>."
    )
    return q, s, "Harvard architecture (separate buses) avoids this but is less common in GCSE PCs.", 3


def _cs_i2_cache_purpose():
    q = "Why does the CPU use <strong>cache memory</strong>?"
    s = (
        "Cache stores <strong>frequently used instructions and data</strong> very close to the CPU, "
        "faster than RAM — reduces waiting time."
    )
    return q, s, "L1/L2/L3 cache — smaller but much faster than main memory.", 2


def _cs_i3_virtual_memory():
    q = "What is <strong>virtual memory</strong> and when is it used?"
    s = (
        "Uses <strong>secondary storage as extra “RAM”</strong> when physical RAM is full. "
        "Slower than real RAM but lets large programs/multitasking run."
    )
    return q, s, "Pages swapped between RAM and disk.", 2


def _cs_i4_os_functions():
    funcs = random.choice([
        ("memory management", "allocates RAM to programs and frees it when finished"),
        ("process management", "schedules which program runs on the CPU and when"),
        ("file management", "organises files/folders on storage devices"),
        ("security", "user accounts, permissions, and protection from malware"),
    ])
    name, desc = funcs
    q = f"Describe the OS role of <strong>{name}</strong>."
    s = f"<strong>{name.capitalize()}:</strong> {desc}."
    return q, s, "Exams often list four: memory, processor, file, security/device management.", 2


def _cs_i5_utility_software():
    q = "Give <strong>two examples</strong> of utility software and what each does."
    s = (
        "Examples: <strong>antivirus</strong> (scans for malware), <strong>disk defragmenter</strong> "
        "(reorganises files on HDD), <strong>backup tool</strong>, <strong>file compression (ZIP)</strong>."
    )
    return q, s, "Utilities maintain or optimise the system — not the same as the OS kernel.", 2


def _cs_i6_storage_compare():
    q = "Give <strong>one advantage of SSD</strong> over HDD for a laptop."
    s = "SSDs are <strong>faster</strong>, more <strong>durable</strong> (no moving parts), and use <strong>less power</strong> — better battery life."
    return q, s, "Pick one clear advantage and link to the scenario.", 2


def _cs_i7_clock_cores():
    q = (
        "CPU A: 3.0 GHz, 4 cores. CPU B: 2.5 GHz, 8 cores. "
        "Which may be better for running many programs at once, and why?"
    )
    s = (
        "<strong>CPU B</strong> — more <strong>cores</strong> help true multitasking/parallel work "
        "(clock speed alone does not double performance)."
    )
    return q, s, "GHz = cycles per second per core; cores = parallel processing units.", 2


def _cs_i8_fetch_step():
    q = "During the <strong>Fetch</strong> stage of the FDE cycle, what happens?"
    s = (
        "The next <strong>instruction is copied from memory</strong> (address in the Program Counter) "
        "into the <strong>Current Instruction Register (CIR)</strong>."
    )
    return q, s, "PC points to where to fetch; MAR/MBR often used with memory.", 2


def _cs_i9_app_vs_system():
    q = "Is <strong>Microsoft Word</strong> application software or system software? Explain briefly."
    s = "<strong>Application software</strong> — it helps the user write documents; it is not managing the whole computer."
    return q, s, "System software includes OS and utilities.", 1


def _cs_i10_secondary_primary():
    q = "Why is a USB flash drive classed as <strong>secondary storage</strong> not primary?"
    s = (
        "It is <strong>non-volatile</strong> and used for long-term file storage, "
        "not the main working memory the CPU uses during execution (RAM)."
    )
    return q, s, "Primary = RAM (and cache/registers); secondary = persistent storage.", 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cs_d1_fde_full_trace():
    q = (
        "Program Counter = 100. Memory at 100 holds instruction <code>LOAD 5</code>. "
        "Name the <strong>three stages</strong> and state what changes in the PC after fetch "
        "(assume each instruction is one address apart)."
    )
    s = (
        "<strong>Fetch:</strong> instruction at 100 → CIR; PC becomes <strong>101</strong>. "
        "<strong>Decode:</strong> control unit interprets LOAD 5. "
        "<strong>Execute:</strong> value 5 loaded into register."
    )
    return q, s, "PC usually increments during fetch so the next instruction is ready.", 4


def _cs_d2_ram_capacity():
    ram = random.choice([4, 8, 16])
    apps = random.choice([6, 10, 12])
    q = (
        f"A PC has <strong>{ram} GB RAM</strong>. A user opens programs needing "
        f"<strong>{ram + 2} GB</strong> total. What might the OS do?"
    )
    s = (
        "Use <strong>virtual memory</strong> — move less-used pages to secondary storage, "
        "freeing RAM (system may run <strong>slower</strong>)."
    )
    return q, s, "When RAM is full, swapping to disk avoids crashing.", 3


def _cs_d3_embedded_constraints():
    q = "Give <strong>two reasons</strong> why embedded systems often use specialised hardware instead of a full PC."
    s = (
        "<strong>Lower cost/power/size</strong> for one task; <strong>reliability</strong> "
        "(dedicated firmware, no general desktop OS needed)."
    )
    return q, s, "Think washing machine vs gaming PC.", 3


def _cs_d4_optical_storage():
    q = "When is <strong>optical storage</strong> (DVD/Blu-ray) still a sensible choice?"
    s = (
        "Distributing <strong>read-only media</strong> cheaply (films, software installers) "
        "where large capacity and portability matter; less common now due to downloads/cloud."
    )
    return q, s, "Optical = laser reads pits on disc; slower than SSD.", 2


def _cs_d5_heat_sink():
    q = "Why does a high-performance CPU need a <strong>heat sink</strong> and fan?"
    s = (
        "Fast CPUs produce <strong>heat</strong>; cooling prevents <strong>overheating</strong> "
        "that would cause thermal throttling or damage."
    )
    return q, s, "More GHz/cores → more heat → need cooling.", 2


def _cs_d6_multitasking_os():
    q = "Explain how the OS allows <strong>multitasking</strong> on a single-core CPU."
    s = (
        "<strong>Time slicing</strong> — rapidly switches between processes so each gets a turn "
        "on the CPU; appears simultaneous to the user."
    )
    return q, s, "Scheduler allocates small time slots per process.", 3


def _cs_d7_hdd_defrag():
    q = "Why is <strong>defragmentation</strong> mainly relevant to HDDs, not SSDs?"
    s = (
        "HDDs are slow when files are split across the disc; defrag <strong>reorders clusters</strong>. "
        "SSDs have no mechanical head — defrag gives little benefit and can <strong>wear</strong> flash cells."
    )
    return q, s, "Mechanical movement vs random access flash.", 3


def _cs_d8_bios_role():
    q = "What does <strong>BIOS/UEFI firmware</strong> do before the operating system loads?"
    s = (
        "<strong>POST</strong> (Power-On Self-Test), detects hardware, lets user change basic settings, "
        "then <strong>boots</strong> the OS from storage."
    )
    return q, s, "Firmware in ROM/flash — first code that runs on power-on.", 3


def _cs_d9_address_bus():
    q = "What is carried on the <strong>address bus</strong>?"
    s = "The <strong>memory location address</strong> the CPU wants to read from or write to (not the data itself)."
    return q, s, "Data bus carries data; control bus carries signals.", 2


def _cs_d10_open_source_os():
    q = "Give <strong>one benefit</strong> and <strong>one drawback</strong> of open-source operating systems (e.g. Linux)."
    s = (
        "<strong>Benefit:</strong> free to use/modify, community support, transparent code. "
        "<strong>Drawback:</strong> fewer commercial applications/drivers for some hardware, steeper learning curve."
    )
    return q, s, "Open source = source code available under licence.", 3


def _cs_d11_control_bus():
    q = "What signals travel on the <strong>control bus</strong>?"
    s = (
        "Control signals such as <strong>read/write</strong>, <strong>interrupt</strong>, "
        "and <strong>clock</strong> pulses that coordinate CPU and memory — not addresses or data values."
    )
    return q, s, "Address bus = location; data bus = data; control bus = commands/timing.", 2


def _cs_d12_multi_core():
    q = (
        "A CPU has <strong>4 cores</strong> but one heavy program does not run 4× faster. "
        "Give <strong>two reasons</strong> why."
    )
    s = (
        "<strong>1)</strong> The program may not be written to use multiple cores in parallel. "
        "<strong>2)</strong> Parts of the task may be sequential (one step waits for another) "
        "or share memory/buses, limiting speed-up."
    )
    return q, s, "More cores help only when work can run in parallel.", 3


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
        f"performance. [2]<br>"
        f"<strong>c)</strong> Explain how a larger <strong>cache</strong> improves "
        f"performance. [2]"
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
    return q, s, "Clock = cycles/second, cores = parallel work, cache = fast nearby memory.", 6


def _cs_d14_multipart_memory():
    q = (
        "A computer has <strong>RAM</strong>, <strong>ROM</strong>, and "
        "<strong>virtual memory</strong>.<br><br>"
        "<strong>a)</strong> State one difference between RAM and ROM in terms of "
        "<strong>volatility</strong>. [2]<br>"
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
    return q, s, "RAM = volatile working memory; virtual memory uses slow disk space as extra RAM.", 6


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
]

_INTERMEDIATE = [
    _cs_i1_von_neumann, _cs_i2_cache_purpose, _cs_i3_virtual_memory,
    _cs_i4_os_functions, _cs_i5_utility_software, _cs_i6_storage_compare,
    _cs_i7_clock_cores, _cs_i8_fetch_step, _cs_i9_app_vs_system,
    _cs_i10_secondary_primary,
]

_DIFFICULT = [
    _cs_d1_fde_full_trace, _cs_d2_ram_capacity, _cs_d3_embedded_constraints,
    _cs_d4_optical_storage, _cs_d5_heat_sink, _cs_d6_multitasking_os,
    _cs_d7_hdd_defrag, _cs_d8_bios_role, _cs_d9_address_bus,
    _cs_d10_open_source_os, _cs_d11_control_bus, _cs_d12_multi_core,
    _cs_d13_multipart_cpu_performance, _cs_d14_multipart_memory,
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

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "cs", "computer_systems",
    )
