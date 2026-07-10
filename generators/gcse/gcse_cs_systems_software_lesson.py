"""
GCSE Computer Science – Systems Software (primarily OCR J277 §1.5)
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import pick_named_variant


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _sw_f1_system_software():
    q = "What is <strong>system software</strong>?"
    s = (
        "Software that <strong>manages computer resources</strong> and provides a platform "
        "for application software (e.g. operating system, utilities)."
    )
    return q, s, "Not end-user tasks like spreadsheets.", 1


def _sw_f2_application_software():
    q = "What is <strong>application software</strong>?"
    s = (
        "Programs that help users perform <strong>tasks</strong> — browsers, games, "
        "word processors, photo editors."
    )
    return q, s, "Runs on top of the OS.", 1


def _sw_f3_os_purpose():
    q = "What is the main purpose of an <strong>operating system</strong>?"
    s = (
        "To <strong>manage hardware and software resources</strong> and provide services "
        "so applications can run (memory, files, users, devices)."
    )
    return q, s, "Bridge between user/apps and hardware.", 2


def _sw_f4_gui():
    q = "What is a <strong>GUI</strong> (graphical user interface)?"
    s = (
        "An interface using <strong>windows, icons, menus and pointers</strong> (WIMP) "
        "so users interact visually — e.g. Windows desktop, macOS."
    )
    return q, s, "Point-and-click.", 1


def _sw_f5_cli():
    q = "What is a <strong>CLI</strong> (command-line interface)?"
    s = (
        "Users type <strong>text commands</strong> to control the system — e.g. "
        "<code>cd</code>, <code>dir</code>, Linux shell. Powerful for admins; steeper learning curve."
    )
    return q, s, "No menus — typed commands.", 2


def _sw_f6_multitasking():
    q = "What is <strong>multitasking</strong>?"
    s = (
        "The OS running <strong>several programs apparently at once</strong> by "
        "time-slicing the CPU or scheduling tasks."
    )
    return q, s, "Music + browser open together.", 2


def _sw_f7_driver():
    q = "What is a <strong>device driver</strong>?"
    s = (
        "Software that lets the OS <strong>communicate with a peripheral</strong> "
        "(printer, GPU, keyboard) — often installed when hardware is added."
    )
    return q, s, "Translator for hardware.", 2


def _sw_f8_utility():
    q = "What is <strong>utility software</strong>?"
    s = (
        "System software that <strong>maintains or optimises</strong> the computer — "
        "encryption, defragmentation, compression (OCR), plus common extras like antivirus."
    )
    return q, s, "Helps manage the system, not write essays.", 2


def _sw_f9_file_management():
    q = "What does <strong>file management</strong> by the OS include?"
    s = (
        "Organising files in <strong>folders/directories</strong>, naming, permissions, "
        "creating, deleting, copying and locating files on storage."
    )
    return q, s, "Explorer/Finder are front-ends.", 2


def _sw_f10_user_management():
    q = "What is <strong>user management</strong>?"
    s = (
        "The OS controls <strong>accounts, passwords and permissions</strong> — "
        "who can log in and what files/settings they may access."
    )
    return q, s, "Admin vs standard user.", 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _sw_i1_memory_management():
    q = "Explain <strong>memory management</strong> by the operating system."
    s = (
        "The OS <strong>allocates RAM</strong> to each running program, tracks what is in use, "
        "reclaims memory when programs close, and may use <strong>virtual memory</strong> "
        "(disk swap) when RAM is full."
    )
    return q, s, "Stops programs overwriting each other.", 3


def _sw_i2_peripheral_management():
    q = "What is <strong>peripheral management</strong>?"
    s = (
        "The OS controls <strong>input/output devices</strong> — schedules access, loads "
        "<strong>drivers</strong>, handles plug-and-play, reports errors (printer offline, etc.)."
    )
    return q, s, "Keyboard, mouse, USB, printer.", 2


def _sw_i3_encryption_utility():
    q = "How does <strong>encryption utility software</strong> help?"
    s = (
        "Encrypts files or whole drives so data is <strong>unreadable without the key</strong> — "
        "protects data if a laptop is stolen (works with OS security)."
    )
    return q, s, "BitLocker, VeraCrypt examples.", 2


def _sw_i4_defragmentation():
    q = "What does <strong>defragmentation</strong> do on a traditional HDD?"
    s = (
        "Reorganises fragmented files so related blocks are <strong>contiguous</strong>, "
        "reducing head movement and often improving read speed. "
        "<strong>Not recommended for SSDs</strong> (unnecessary wear)."
    )
    return q, s, "Fragments spread over disk.", 3


def _sw_i5_compression():
    q = "What does <strong>data compression</strong> utility software do?"
    s = (
        "Reduces file size using algorithms like <strong>ZIP</strong> — "
        "<strong>lossless</strong> for documents (exact restore); can save storage and bandwidth."
    )
    return q, s, "Smaller archives for email.", 2


def _sw_i6_gui_vs_cli():
    q = "Compare <strong>GUI</strong> and <strong>CLI</strong> for a network administrator."
    s = (
        "<strong>GUI:</strong> easier discovery, visual feedback, fewer commands to memorise. "
        "<strong>CLI:</strong> faster for repetitive tasks, scripting/automation, remote SSH, "
        "uses less resources on servers."
    )
    return q, s, "OCR requires both interfaces.", 3


def _sw_i7_os_security():
    q = "How does the OS contribute to <strong>security</strong>?"
    s = (
        "User accounts, passwords, file <strong>permissions</strong>, firewall integration, "
        "updates, logging — works with utilities like antivirus."
    )
    return q, s, "AQA lists security as OS role.", 2


def _sw_i8_processor_scheduling():
    q = "How does the OS manage the <strong>processor</strong> during multitasking?"
    s = (
        "<strong>Scheduling</strong> decides which process gets the CPU next (time slices/priority) "
        "so many programs share one CPU fairly and responsively."
    )
    return q, s, "Scheduler in the OS kernel.", 3


def _sw_i9_zip_example():
    q = "A teacher zips 200 MB of worksheets to 50 MB for email. Name the <strong>utility type</strong> and one benefit."
    s = (
        "<strong>Data compression</strong> utility — saves <strong>storage and upload time</strong>; "
        "receiver decompresses to restore files (lossless)."
    )
    return q, s, "ZIP/RAR tools.", 2


def _sw_i10_driver_install():
    q = "A new printer does not work until software is installed. Explain using <strong>drivers</strong>."
    s = (
        "The OS needs a <strong>device driver</strong> to translate generic print commands into "
        "instructions the printer understands — install from manufacturer or Windows Update."
    )
    return q, s, "Peripheral management.", 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _sw_d1_virtual_memory():
    q = "What is <strong>virtual memory</strong> and why does the OS use it?"
    s = (
        "Uses <strong>disk space as extra “RAM”</strong> when physical memory is full — "
        "allows more programs than RAM alone could hold, but <strong>slower</strong> than real RAM (thrashing if overused)."
    )
    return q, s, "Swap file / page file.", 3


def _sw_d2_ssd_defrag():
    q = "Why is <strong>defragmentation</strong> usually avoided on SSDs?"
    s = (
        "SSDs have <strong>no moving read heads</strong> — fragmentation matters less for speed; "
        "defrag causes <strong>extra write cycles</strong>, wearing flash memory without much benefit."
    )
    return q, s, "OCR exams contrast HDD vs SSD.", 3


def _sw_d3_permissions_scenario():
    q = "Pupils can read but not delete files in <code>\\Shared\\Resources</code>. Which OS functions are involved?"
    s = (
        "<strong>File management</strong> (folders, access rights) and "
        "<strong>user management</strong> (group permissions per account)."
    )
    return q, s, "NTFS permissions example.", 3


def _sw_d4_embedded_os():
    q = "How does an <strong>embedded OS</strong> differ from a desktop OS?"
    s = (
        "Embedded: <strong>single dedicated task</strong>, limited resources, real-time needs, "
        "often no GUI — e.g. washing machine controller. Desktop: general-purpose, multitasking, rich UI."
    )
    return q, s, "Not full Windows on a microwave.", 3


def _sw_d5_encryption_vs_os():
    q = "Distinguish <strong>OS security</strong> from an <strong>encryption utility</strong>."
    s = (
        "OS: accounts, permissions, patches, firewall hooks. "
        "<strong>Utility:</strong> encrypts specific files/volumes so stolen disk data stays unreadable "
        "even if OS login is bypassed."
    )
    return q, s, "Layers of protection.", 4


def _sw_d6_exam_os_functions():
    q = "List <strong>five functions</strong> of an operating system (OCR 1.5.1)."
    s = (
        "1) <strong>User interface</strong> (GUI/CLI) 2) <strong>Memory management</strong> &amp; multitasking "
        "3) <strong>Peripheral management</strong> &amp; drivers 4) <strong>User management</strong> "
        "5) <strong>File management</strong>"
    )
    return q, s, "Memorise OCR list exactly.", 4


def _sw_d7_exam_utilities():
    q = "Name <strong>three utility types</strong> required by OCR 1.5.2 and give one purpose each."
    s = (
        "<strong>Encryption</strong> — protect confidentiality of data. "
        "<strong>Defragmentation</strong> — optimise file layout on HDD. "
        "<strong>Data compression</strong> — reduce file size for storage/transmission."
    )
    return q, s, "Three named utilities.", 4


def _sw_d8_multitasking_limit():
    q = "Why can opening too many programs make a PC <strong>slow</strong> even with multitasking?"
    s = (
        "RAM fills → OS uses <strong>virtual memory</strong> on disk (much slower) or waits for CPU time slices; "
        "context switching adds overhead — <strong>appears</strong> simultaneous but resources are finite."
    )
    return q, s, "Thrashing / swapping.", 4


def _sw_d9_cli_script():
    q = "Give a <strong>CLI advantage</strong> when deploying software to 500 school PCs."
    s = (
        "Administrators can run <strong>scripts/batch files</strong> remotely (e.g. PowerShell, SSH) "
        "to install updates automatically — faster and more consistent than clicking GUI on each machine."
    )
    return q, s, "Automation.", 3


def _sw_d10_classify_software():
    q = "Classify: Windows 11, Microsoft Teams, 7-Zip, printer driver."
    s = (
        "<strong>Windows 11</strong> — operating system (system). "
        "<strong>Teams</strong> — application. "
        "<strong>7-Zip</strong> — utility (compression). "
        "<strong>Printer driver</strong> — system software (driver) for peripheral management."
    )
    return q, s, "Four-way classification.", 4


def _sw_d11_backup_strategy():
    q = (
        "A school server holds coursework folders. Describe a sensible <strong>backup strategy</strong> "
        "(frequency, full vs incremental, off-site copy)."
    )
    s = (
        "<strong>Regular automated backups</strong> (daily incremental, weekly full). "
        "Store at least one copy <strong>off-site</strong> or in the cloud. "
        "Test restores periodically; protect backup media with encryption/access control."
    )
    return q, s, "3-2-1 rule: 3 copies, 2 media types, 1 off-site.", 3


def _sw_d12_page_fault():
    q = (
        "When RAM is full, the OS may move a page to disk and later bring it back. "
        "What is this called and why is it <strong>slower</strong> than using RAM?"
    )
    s = (
        "<strong>Virtual memory / paging</strong> — disk (secondary storage) has much "
        "<strong>higher latency</strong> than RAM, so excessive paging causes thrashing and slowdown."
    )
    return q, s, "Swap file on HDD/SSD is the overflow area.", 3


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _sw_d13_multipart_os_management():
    q = (
        "An operating system manages several resources at once while a user runs a browser, "
        "a music player, and a word processor.<br><br>"
        "<strong>a)</strong> Explain how the OS uses <strong>memory management</strong> to "
        "let several programs run at the same time. [2]<br>"
        "<strong>b)</strong> Explain what the OS does as part of "
        "<strong>peripheral / device management</strong>. [2]<br>"
        "<strong>c)</strong> Explain how <strong>user management</strong> helps keep a shared "
        "computer secure. [2]"
    )
    s = (
        "<strong>a)</strong> The OS <strong>allocates a section of RAM to each program</strong> "
        "and keeps track of what is stored where, so programs do not overwrite each other. "
        "It can use virtual memory when RAM is full.<br><br>"
        "<strong>b)</strong> The OS installs and uses <strong>device drivers</strong> to "
        "communicate with peripherals (printer, keyboard, etc.) and manages the "
        "<strong>transfer of data</strong> between them and the CPU.<br><br>"
        "<strong>c)</strong> User management provides <strong>separate accounts with "
        "passwords and access rights</strong>, so each user can only see and change what "
        "they are <strong>authorised</strong> to, protecting other users' files."
    )
    return q, s, "OS = memory (share RAM), devices (drivers), users (accounts & rights).", 6


def _sw_d14_multipart_utilities():
    q = (
        "A user's laptop is running low on disk space and feels slow.<br><br>"
        "<strong>a)</strong> Name a <strong>utility</strong> that reduces file sizes to save "
        "space, and explain briefly how it helps. [2]<br>"
        "<strong>b)</strong> The laptop has a <strong>magnetic hard disk drive (HDD)</strong>. "
        "Name the utility that reorganises files stored across the disk and explain why it "
        "can improve speed. [2]<br>"
        "<strong>c)</strong> Explain why running that utility from part (b) on a "
        "<strong>solid state drive (SSD)</strong> is <strong>not</strong> recommended. [2]"
    )
    s = (
        "<strong>a)</strong> <strong>Compression</strong> software reduces the number of bits "
        "needed to store files, so <strong>more data fits</strong> in the same space.<br><br>"
        "<strong>b)</strong> <strong>Defragmentation</strong>. Over time files become split "
        "into pieces (fragmented) across the disk; defragmentation moves the pieces so each "
        "file is <strong>stored together</strong>, so the read/write head moves less and "
        "files load faster.<br><br>"
        "<strong>c)</strong> An SSD has <strong>no moving parts</strong> and can access any "
        "location equally quickly, so defragmentation gives no speed benefit. It also causes "
        "extra <strong>unnecessary write operations</strong> that <strong>shorten the SSD's "
        "lifespan</strong>."
    )
    return q, s, "Compression saves space; defrag helps HDDs but harms SSDs.", 6


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_SW_MCQ_BANK = [
    {"q": "System software:",
     "opts": ["A  Only games", "B  Manages resources and runs the platform for other software",
              "C  Is the CPU", "D  Only web browsers"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>Manages the computer</strong>. Answer: B",
     "hint": "OS + utilities."},
    {"q": "A GUI uses:",
     "opts": ["A  Typed commands only", "B  Windows, icons, menus and pointers",
              "C  No output", "D  Only machine code"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>Visual WIMP interface</strong>. Answer: B",
     "hint": "Desktop metaphor."},
    {"q": "Multitasking means:",
     "opts": ["A  One program ever", "B  Several programs appear to run at once",
              "C  No CPU", "D  Only printing"],
     "ans": "B", "marks": 2, "difficulty": "foundational",
     "sol": "OS <strong>schedules</strong> CPU time. Answer: B",
     "hint": "Time slicing."},
    {"q": "A device driver:",
     "opts": ["A  Replaces the CPU", "B  Lets the OS communicate with hardware",
              "C  Is always an application", "D  Deletes all files"],
     "ans": "B", "marks": 2, "difficulty": "foundational",
     "sol": "<strong>Hardware interface</strong>. Answer: B",
     "hint": "Printer won't work without one."},
    {"q": "Defragmentation is mainly for:",
     "opts": ["A  Traditional HDDs", "B  SSDs only", "C  Monitors", "D  Keyboards"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>HDD</strong> head movement. Answer: A",
     "hint": "Avoid on SSD."},
    {"q": "Compression utilities:",
     "opts": ["A  Increase file size always", "B  Reduce file size for storage or transfer",
              "C  Install drivers", "D  Replace the OS"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>ZIP-style</strong> tools. Answer: B",
     "hint": "Archives."},
    {"q": "User management includes:",
     "opts": ["A  Accounts and permissions", "B  Overclocking the GPU only",
              "C  Drawing icons", "D  Compiling Python"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>Who can access what</strong>. Answer: A",
     "hint": "Login accounts."},
    {"q": "File management includes:",
     "opts": ["A  Folders, create/delete/copy files", "B  Only RAM timing",
              "C  Monitor brightness", "D  Network cables"],
     "ans": "A", "marks": 1, "difficulty": "intermediate",
     "sol": "<strong>Directory structure</strong>. Answer: A",
     "hint": "Explorer tasks."},
    {"q": "A CLI interface:",
     "opts": ["A  Uses typed commands", "B  Has no keyboard", "C  Is only for printers",
              "D  Cannot run scripts"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>Command line</strong>. Answer: A",
     "hint": "Shell/CMD."},
    {"q": "Memory management by the OS:",
     "opts": ["A  Allocates RAM to programs", "B  Paints the desktop",
              "C  Sells laptops", "D  Removes copyright"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "<strong>RAM allocation</strong>. Answer: A",
     "hint": "Tracks memory use."},
    {"q": "Encryption utility software:",
     "opts": ["A  Makes data unreadable without the key", "B  Speeds up the CPU clock",
              "C  Defragments SSDs", "D  Creates user accounts"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "<strong>Confidentiality</strong>. Answer: A",
     "hint": "OCR utility type."},
    {"q": "Microsoft Word is:",
     "opts": ["A  Application software", "B  The operating system",
              "C  A device driver", "D  Firmware in the CPU"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>End-user task</strong> software. Answer: A",
     "hint": "Runs on Windows."},
    {"q": "Virtual memory uses:",
     "opts": ["A  Disk space when RAM is full", "B  Only cache inside CPU",
              "C  Monitor pixels", "D  Printer ink"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "<strong>Swap/page file</strong>. Answer: A",
     "hint": "Slower than RAM."},
    {"q": "Peripheral management involves:",
     "opts": ["A  Drivers and I/O devices", "B  Only file names",
              "C  GCSE grades", "D  Binary addition in ALU only"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "<strong>Devices + drivers</strong>. Answer: A",
     "hint": "Keyboard, USB, printer."},
    {"q": "Windows 11 kernel is:",
     "opts": ["A  Part of the operating system", "B  Application software",
              "C  A compression utility only", "D  RAM chip"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "<strong>OS core</strong>. Answer: A",
     "hint": "System software."},
    {"q": "A full backup:",
     "opts": ["A  copies all selected data each time", "B  never uses storage space",
              "C  only backs up files deleted yesterday", "D  replaces the CPU"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "Copies <strong>everything</strong> in scope. Answer: A",
     "hint": "Contrast with incremental."},
    {"q": "Thrashing occurs when:",
     "opts": ["A  the OS spends too much time swapping pages between RAM and disk",
              "B  the monitor refreshes faster", "C  a GUI uses icons",
              "D  a user logs out"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "Excessive <strong>paging</strong> slows the system. Answer: A",
     "hint": "Too little RAM for running programs."},
    {"q": "Utility software is designed to:",
     "opts": ["A  perform maintenance or security tasks on the system",
              "B  replace the operating system kernel", "C  be the CPU",
              "D  only run games"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "Utilities <strong>maintain or protect</strong> the computer. Answer: A",
     "hint": "Antivirus, defrag, compression tools."},
    {"q": "A process in an operating system is:",
     "opts": ["A  a program currently being executed", "B  only a file icon",
              "C  the monitor cable", "D  a type of keyboard"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "A running instance of a <strong>program</strong>. Answer: A",
     "hint": "Task Manager lists processes."},
    {"q": "Scheduling in the OS decides:",
     "opts": ["A  which process uses the CPU next", "B  the colour of desktop icons only",
              "C  how to print paper", "D  the price of laptops"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "CPU time is <strong>allocated between processes</strong>. Answer: A",
     "hint": "Part of multitasking."},
    {"q": "Firmware is software that is:",
     "opts": ["A  stored in non-volatile memory and controls hardware at startup",
              "B  always deleted when power is lost", "C  only a web browser",
              "D  the same as a word processor"],
     "ans": "A", "marks": 2, "difficulty": "foundational",
     "sol": "Firmware such as BIOS/UEFI is <strong>semi-permanent</strong>. Answer: A",
     "hint": "Stored on ROM/flash chips."},
    {"q": "Disk cleanup utilities help by:",
     "opts": ["A  removing unnecessary files to free storage space",
              "B  increasing CPU clock speed", "C  assigning IP addresses",
              "D  writing SQL queries"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "Deletes temp files and frees <strong>disk space</strong>. Answer: A",
     "hint": "Common Windows/macOS maintenance tool."},
]

_LESSON_QUIZ_MIX = (
    ("foundational", 3),
    ("intermediate", 4),
    ("difficult", 3),
)


def _sw_mcq_item_to_problem(item, difficulty):
    return make_problem(
        item["q"], item["sol"], item["hint"], difficulty, item["marks"],
        "gcse", "cs", "systems_software",
        options=item["opts"], correct_answer=item["ans"],
    )


def _sample_mcq_by_difficulty(difficulty, count):
    pool = [item for item in _SW_MCQ_BANK if item.get("difficulty") == difficulty]
    if len(pool) >= count:
        return random.sample(pool, count)
    return [random.choice(pool) for _ in range(count)]


def build_systems_software_lesson_quiz():
    """10-question lesson quiz: 3 foundational, 4 intermediate, 3 difficult MCQs."""
    items = []
    for difficulty, count in _LESSON_QUIZ_MIX:
        items.extend((item, difficulty) for item in _sample_mcq_by_difficulty(difficulty, count))
    random.shuffle(items)
    return [_sw_mcq_item_to_problem(item, difficulty) for item, difficulty in items]


def systems_software_mcq():
    item = random.choice(_SW_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _sw_f1_system_software, _sw_f2_application_software, _sw_f3_os_purpose,
    _sw_f4_gui, _sw_f5_cli, _sw_f6_multitasking, _sw_f7_driver,
    _sw_f8_utility, _sw_f9_file_management, _sw_f10_user_management,
]

_INTERMEDIATE = [
    _sw_i1_memory_management, _sw_i2_peripheral_management, _sw_i3_encryption_utility,
    _sw_i4_defragmentation, _sw_i5_compression, _sw_i6_gui_vs_cli,
    _sw_i7_os_security, _sw_i8_processor_scheduling, _sw_i9_zip_example,
    _sw_i10_driver_install,
]

_DIFFICULT = [
    _sw_d1_virtual_memory, _sw_d2_ssd_defrag, _sw_d3_permissions_scenario,
    _sw_d4_embedded_os, _sw_d5_encryption_vs_os, _sw_d6_exam_os_functions,
    _sw_d7_exam_utilities, _sw_d8_multitasking_limit, _sw_d9_cli_script,
    _sw_d10_classify_software, _sw_d11_backup_strategy, _sw_d12_page_fault,
    _sw_d13_multipart_os_management, _sw_d14_multipart_utilities,
]


def gcse_systems_software_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return [systems_software_mcq] * 10

    pools = {
        "foundational": _FOUNDATIONAL,
        "intermediate": _INTERMEDIATE,
        "difficult": _DIFFICULT,
    }
    if difficulty not in pools:
        return random.sample(_FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT, 10)

    pool = pools[difficulty]
    return random.sample(pool, len(pool))


def gcse_systems_software(difficulty, mode, variant_name=None):
    if mode == "mcq":
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = systems_software_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "systems_software",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_systems_software_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "cs", "systems_software",
    )
