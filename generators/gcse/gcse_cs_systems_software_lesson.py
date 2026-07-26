"""
GCSE Computer Science – Systems Software (primarily OCR J277 §1.5)
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Definition-style variants use MCQ/pick/order; multipart uses inline number_fields.
"""
import random
from generators.shared.utils import (
    make_problem,
    graded_answer_number_fields,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import pick_named_variant


def _sw_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'cs', 'systems_software',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        if isinstance(raw, dict):
            extra = problem_extra_from_graded_answer(raw)
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'systems_software', **extra
    )


def _sw_mcq_payload(correct_text, distractors):
    """Four-option practice MCQ; returns payload for ``_sw_problem_from_output``."""
    pool = [correct_text] + list(distractors[:3])
    random.shuffle(pool)
    letters = 'ABCD'
    correct_letter = letters[pool.index(correct_text)]
    options = [f'{letters[i]}  {pool[i]}' for i in range(len(pool))]
    return {'type': 'mcq', 'options': options, 'correct': correct_letter}


def _sw_mcq_match_field(correct_text, distractors):
    """Shuffled 3-option inline MCQ for term–description matching."""
    pool = [correct_text] + list(distractors[:2])
    random.shuffle(pool)
    letters = 'ABC'
    return pool, letters[pool.index(correct_text)]


def _sw_pick_from_bank(correct_texts, distractor_texts, pick_count, *, format_hint=None):
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


def _sw_pick_field(correct_texts, distractor_texts, pick_count):
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

def _sw_f1_system_software():
    q = "What is <strong>system software</strong>? Select one correct answer."
    s = (
        "Software that <strong>manages computer resources</strong> and provides a platform "
        "for application software (e.g. operating system, utilities)."
    )
    return q, s, "Not end-user tasks like spreadsheets.", 1, _sw_mcq_payload(
        'Software that manages computer resources and provides a platform for application software',
        [
            'Programs that help users perform everyday tasks such as word processing',
            'Hardware built into the CPU that performs calculations',
            'Data stored permanently on secondary storage devices',
        ],
    )


def _sw_f2_application_software():
    q = "What is <strong>application software</strong>? Select one correct answer."
    s = (
        "Programs that help users perform <strong>tasks</strong> — browsers, games, "
        "word processors, photo editors."
    )
    return q, s, "Runs on top of the OS.", 1, _sw_mcq_payload(
        'Programs that help users perform tasks (e.g. browsers, word processors, games)',
        [
            'Software that manages hardware resources and runs the operating system',
            'Firmware stored in ROM that starts the computer on power-on',
            'Device drivers that translate commands for peripherals only',
        ],
    )


def _sw_f3_os_purpose():
    q = "What is the main purpose of an <strong>operating system</strong>? Select one correct answer."
    s = (
        "To <strong>manage hardware and software resources</strong> and provide services "
        "so applications can run (memory, files, users, devices)."
    )
    return q, s, "Bridge between user/apps and hardware.", 2, _sw_mcq_payload(
        'To manage hardware and software resources and provide services so applications can run',
        [
            'To perform arithmetic and logic operations inside the CPU',
            'To store the bootstrap instructions that start the computer',
            'To replace application programs such as web browsers',
        ],
    )


def _sw_f4_gui():
    q = "What is a <strong>GUI</strong> (graphical user interface)? Select one correct answer."
    s = (
        "An interface using <strong>windows, icons, menus and pointers</strong> (WIMP) "
        "so users interact visually — e.g. Windows desktop, macOS."
    )
    return q, s, "Point-and-click.", 1, _sw_mcq_payload(
        'An interface using windows, icons, menus and pointers so users interact visually',
        [
            'An interface where users type text commands only',
            'Software that encrypts files on a hard drive',
            'A program that compresses files into ZIP archives',
        ],
    )


def _sw_f5_cli():
    q = "What is a <strong>CLI</strong> (command-line interface)? Select one correct answer."
    s = (
        "Users type <strong>text commands</strong> to control the system — e.g. "
        "<code>cd</code>, <code>dir</code>, Linux shell. Powerful for admins; steeper learning curve."
    )
    return q, s, "No menus — typed commands.", 2, _sw_mcq_payload(
        'Users type text commands to control the system',
        [
            'Users click windows, icons, menus and pointers to control the system',
            'The CPU fetches, decodes and executes machine-code instructions',
            'A utility that reorganises fragmented files on a hard disk',
        ],
    )


def _sw_f6_multitasking():
    q = "What is <strong>multitasking</strong>? Select one correct answer."
    s = (
        "The OS running <strong>several programs apparently at once</strong> by "
        "time-slicing the CPU or scheduling tasks."
    )
    return q, s, "Music + browser open together.", 2, _sw_mcq_payload(
        'The OS running several programs apparently at once by time-slicing or scheduling the CPU',
        [
            'Running one program until it finishes before starting another',
            'Installing device drivers for every peripheral on the computer',
            'Encrypting all files on the hard drive automatically',
        ],
    )


def _sw_f7_driver():
    q = "What is a <strong>device driver</strong>? Select one correct answer."
    s = (
        "Software that lets the OS <strong>communicate with a peripheral</strong> "
        "(printer, GPU, keyboard) — often installed when hardware is added."
    )
    return q, s, "Translator for hardware.", 2, _sw_mcq_payload(
        'Software that lets the OS communicate with a peripheral device',
        [
            'Application software that helps users write documents',
            'The main program that manages all hardware and software resources',
            'A utility that reduces file size for email attachments',
        ],
    )


def _sw_f8_utility():
    q = "What is <strong>utility software</strong>? Select one correct answer."
    s = (
        "System software that <strong>maintains or optimises</strong> the computer — "
        "encryption, defragmentation, compression (OCR), plus common extras like antivirus."
    )
    return q, s, "Helps manage the system, not write essays.", 2, _sw_mcq_payload(
        'System software that maintains or optimises the computer',
        [
            'Programs that help users perform everyday tasks such as browsing the web',
            'Hardware inside the CPU that performs calculations',
            'The operating system kernel that manages all resources',
        ],
    )


def _sw_f9_file_management():
    q = (
        "What does <strong>file management</strong> by the OS include? "
        "Select two correct statements."
    )
    s = (
        "Organising files in <strong>folders/directories</strong>, naming, permissions, "
        "creating, deleting, copying and locating files on storage."
    )
    return q, s, "Explorer/Finder are front-ends.", 2, _sw_pick_from_bank(
        (
            'Organising files in folders or directories on storage',
            'Setting file permissions and controlling who can access files',
            'Creating, deleting, copying and locating files',
        ),
        (
            'Allocating RAM to each running program',
            'Scheduling which process uses the CPU next',
            'Encrypting the entire hard drive without user action',
        ),
        2,
        format_hint='Select two things file management includes',
    )


def _sw_f10_user_management():
    q = "What is <strong>user management</strong>? Select one correct answer."
    s = (
        "The OS controls <strong>accounts, passwords and permissions</strong> — "
        "who can log in and what files/settings they may access."
    )
    return q, s, "Admin vs standard user.", 2, _sw_mcq_payload(
        'The OS controls accounts, passwords and permissions for who can log in and access files',
        [
            'Software that reduces file size using ZIP-style compression',
            'The process of reorganising fragmented files on a hard disk',
            'Firmware that runs POST before the operating system loads',
        ],
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _sw_i1_memory_management():
    q = (
        "Select the <strong>two</strong> correct statements about "
        "<strong>memory management</strong> by the operating system."
    )
    s = (
        "The OS <strong>allocates RAM</strong> to each running program, tracks what is in use, "
        "reclaims memory when programs close, and may use <strong>virtual memory</strong> "
        "(disk swap) when RAM is full."
    )
    return q, s, "Stops programs overwriting each other.", 3, _sw_pick_from_bank(
        (
            'The OS allocates RAM to each running program',
            'The OS tracks which memory is in use and reclaims it when programs close',
            'The OS may use virtual memory on disk when physical RAM is full',
        ),
        (
            'Memory management only applies to ROM, not RAM',
            'The OS never allows more than one program to use RAM at a time',
            'Virtual memory is faster than physical RAM when heavily used',
        ),
        2,
        format_hint='Select two correct statements about memory management',
    )


def _sw_i2_peripheral_management():
    q = "What is <strong>peripheral management</strong>? Select one correct answer."
    s = (
        "The OS controls <strong>input/output devices</strong> — schedules access, loads "
        "<strong>drivers</strong>, handles plug-and-play, reports errors (printer offline, etc.)."
    )
    return q, s, "Keyboard, mouse, USB, printer.", 2, _sw_mcq_payload(
        'The OS controls input/output devices, loads drivers and handles device access',
        [
            'The OS organises files into folders and sets file permissions only',
            'The OS allocates RAM and manages virtual memory when RAM is full',
            'The OS compresses files to reduce storage space on the hard drive',
        ],
    )


def _sw_i3_encryption_utility():
    q = "How does <strong>encryption utility software</strong> help? Select one correct answer."
    s = (
        "Encrypts files or whole drives so data is <strong>unreadable without the key</strong> — "
        "protects data if a laptop is stolen (works with OS security)."
    )
    return q, s, "BitLocker, VeraCrypt examples.", 2, _sw_mcq_payload(
        'Encrypts files or drives so data is unreadable without the correct key',
        [
            'Reorganises fragmented files so they are stored contiguously on a hard disk',
            'Reduces file size using lossless compression algorithms such as ZIP',
            'Creates user accounts and sets login passwords for the operating system',
        ],
    )


def _sw_i4_defragmentation():
    q = "What does <strong>defragmentation</strong> do on a traditional HDD? Select one correct answer."
    s = (
        "Reorganises fragmented files so related blocks are <strong>contiguous</strong>, "
        "reducing head movement and often improving read speed. "
        "<strong>Not recommended for SSDs</strong> (unnecessary wear)."
    )
    return q, s, "Fragments spread over disk.", 3, _sw_mcq_payload(
        'Reorganises fragmented files so related blocks are stored contiguously, reducing head movement',
        [
            'Encrypts files so they cannot be read without a password',
            'Reduces file size using compression algorithms such as ZIP',
            'Allocates RAM to each running program when memory is low',
        ],
    )


def _sw_i5_compression():
    q = "What does <strong>data compression</strong> utility software do? Select one correct answer."
    s = (
        "Reduces file size using algorithms like <strong>ZIP</strong> — "
        "<strong>lossless</strong> for documents (exact restore); can save storage and bandwidth."
    )
    return q, s, "Smaller archives for email.", 2, _sw_mcq_payload(
        'Reduces file size using compression algorithms, often losslessly for documents',
        [
            'Reorganises fragmented files on a magnetic hard disk drive',
            'Encrypts data so it is unreadable without the correct key',
            'Installs device drivers so peripherals can communicate with the OS',
        ],
    )


def _sw_i6_gui_vs_cli():
    q = (
        "Compare <strong>GUI</strong> and <strong>CLI</strong> for a network administrator. "
        "Select <strong>four</strong> correct statements (two GUI advantages and two CLI advantages)."
    )
    s = (
        "<strong>GUI:</strong> easier discovery, visual feedback, fewer commands to memorise. "
        "<strong>CLI:</strong> faster for repetitive tasks, scripting/automation, remote SSH, "
        "uses less resources on servers."
    )
    return q, s, "OCR requires both interfaces.", 3, _sw_pick_from_bank(
        (
            'GUI: easier discovery of features through menus and icons',
            'GUI: visual feedback makes status and results easy to see',
            'CLI: faster for repetitive tasks once commands are known',
            'CLI: supports scripting and automation (e.g. batch files, SSH)',
            'CLI: uses fewer resources on servers than a full graphical desktop',
        ),
        (
            'GUI: requires memorising long command names for every action',
            'CLI: impossible to use for remote administration of servers',
            'CLI: always slower than clicking through a GUI for every task',
            'GUI: cannot show visual feedback or status information',
        ),
        4,
        format_hint='Select four correct statements (two GUI and two CLI advantages)',
    )


def _sw_i7_os_security():
    q = (
        "How does the OS contribute to <strong>security</strong>? "
        "Select two correct statements."
    )
    s = (
        "User accounts, passwords, file <strong>permissions</strong>, firewall integration, "
        "updates, logging — works with utilities like antivirus."
    )
    return q, s, "AQA lists security as OS role.", 2, _sw_pick_from_bank(
        (
            'User accounts and passwords control who can log in',
            'File permissions control who can read, write or delete files',
            'Security updates and patches fix known vulnerabilities',
            'Integration with firewalls to monitor network traffic',
        ),
        (
            'The OS automatically encrypts every file without any user setup',
            'The OS removes the need for antivirus utility software entirely',
            'Security is handled only by application software, not the OS',
        ),
        2,
        format_hint='Select two ways the OS contributes to security',
    )


def _sw_i8_processor_scheduling():
    q = (
        "How does the OS manage the <strong>processor</strong> during multitasking? "
        "Select one correct answer."
    )
    s = (
        "<strong>Scheduling</strong> decides which process gets the CPU next (time slices/priority) "
        "so many programs share one CPU fairly and responsively."
    )
    return q, s, "Scheduler in the OS kernel.", 3, _sw_mcq_payload(
        'Scheduling decides which process gets the CPU next using time slices or priority',
        [
            'The OS runs one program until it finishes before starting the next',
            'The OS stores all running programs permanently in ROM',
            'The OS defragments the hard drive while programs are running',
        ],
    )


def _sw_i9_zip_example():
    q = (
        "A teacher zips 200 MB of worksheets to 50 MB for email. "
        "Select the <strong>utility type</strong> and <strong>one benefit</strong>."
    )
    s = (
        "<strong>Data compression</strong> utility — saves <strong>storage and upload time</strong>; "
        "receiver decompresses to restore files (lossless)."
    )
    return q, s, "ZIP/RAR tools.", 2, _sw_pick_from_bank(
        (
            'Data compression utility',
            'Saves storage space on the device or server',
            'Reduces upload or download time when sending files',
            'Receiver can decompress to restore the original files (lossless)',
        ),
        (
            'Defragmentation utility',
            'Encryption utility that makes files unreadable without a key',
            'Device driver that lets the OS communicate with a printer',
            'Operating system kernel that manages all hardware resources',
        ),
        2,
        format_hint='Select the utility type and one benefit',
    )


def _sw_i10_driver_install():
    q = (
        "A new printer does not work until software is installed. "
        "Select one correct explanation using <strong>drivers</strong>."
    )
    s = (
        "The OS needs a <strong>device driver</strong> to translate generic print commands into "
        "instructions the printer understands — install from manufacturer or Windows Update."
    )
    return q, s, "Peripheral management.", 2, _sw_mcq_payload(
        'The OS needs a device driver to translate commands into instructions the printer understands',
        [
            'The OS needs a compression utility to reduce the size of print jobs',
            'The OS needs an encryption utility before any file can be sent to a printer',
            'The OS replaces the printer hardware with virtual memory on the hard disk',
        ],
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _sw_d1_virtual_memory():
    q = (
        "What is <strong>virtual memory</strong> and why does the OS use it? "
        "Select one correct answer."
    )
    s = (
        "Uses <strong>disk space as extra “RAM”</strong> when physical memory is full — "
        "allows more programs than RAM alone could hold, but <strong>slower</strong> than real RAM (thrashing if overused)."
    )
    return q, s, "Swap file / page file.", 3, _sw_mcq_payload(
        'Uses disk space as extra memory when physical RAM is full so more programs can run',
        [
            'Extra RAM chips installed inside the CPU for faster access',
            'A compression utility that reduces the size of files on the hard drive',
            'Firmware stored in ROM that starts the computer before the OS loads',
        ],
    )


def _sw_d2_ssd_defrag():
    q = (
        "Why is <strong>defragmentation</strong> usually avoided on SSDs? "
        "Select two correct reasons."
    )
    s = (
        "SSDs have <strong>no moving read heads</strong> — fragmentation matters less for speed; "
        "defrag causes <strong>extra write cycles</strong>, wearing flash memory without much benefit."
    )
    return q, s, "OCR exams contrast HDD vs SSD.", 3, _sw_pick_from_bank(
        (
            'SSDs have no moving read/write heads — fragmentation matters less for speed',
            'Defragmentation causes extra write cycles that wear flash memory',
            'Defrag gives little speed benefit on SSDs but can shorten their lifespan',
        ),
        (
            'SSDs must be defragmented weekly to maintain performance',
            'Defragmentation increases the clock speed of the CPU on SSD systems',
            'SSDs store data using a mechanical head that benefits from contiguous files',
        ),
        2,
        format_hint='Select two reasons defragmentation is avoided on SSDs',
    )


def _sw_d3_permissions_scenario():
    q = (
        "Pupils can read but not delete files in <code>\\Shared\\Resources</code>. "
        "Select the <strong>two</strong> OS functions involved."
    )
    s = (
        "<strong>File management</strong> (folders, access rights) and "
        "<strong>user management</strong> (group permissions per account)."
    )
    return q, s, "NTFS permissions example.", 3, _sw_pick_from_bank(
        (
            'File management — folders and file access rights',
            'User management — group permissions per account',
        ),
        (
            'Data compression — reducing file size for storage',
            'Defragmentation — reorganising files on a hard disk',
            'Processor scheduling — deciding which process uses the CPU next',
        ),
        2,
        format_hint='Select the two OS functions involved',
    )


def _sw_d4_embedded_os():
    q = (
        "How does an <strong>embedded OS</strong> differ from a desktop OS? "
        "Select two correct differences."
    )
    s = (
        "Embedded: <strong>single dedicated task</strong>, limited resources, real-time needs, "
        "often no GUI — e.g. washing machine controller. Desktop: general-purpose, multitasking, rich UI."
    )
    return q, s, "Not full Windows on a microwave.", 3, _sw_pick_from_bank(
        (
            'Embedded OS is designed for a single dedicated task',
            'Embedded systems have limited resources compared to a desktop PC',
            'Desktop OS supports general-purpose multitasking with a rich user interface',
            'Embedded systems often have no GUI or a very simple interface',
        ),
        (
            'Embedded OS always runs the same full Windows desktop as a gaming PC',
            'Desktop OS cannot multitask or run more than one program',
            'Embedded systems always have more RAM and storage than desktop computers',
        ),
        2,
        format_hint='Select two correct differences',
    )


def _sw_d5_encryption_vs_os():
    q = (
        "Distinguish <strong>OS security</strong> from an <strong>encryption utility</strong>. "
        "Select one correct statement about each."
    )
    s = (
        "OS: accounts, permissions, patches, firewall hooks. "
        "<strong>Utility:</strong> encrypts specific files/volumes so stolen disk data stays unreadable "
        "even if OS login is bypassed."
    )
    return q, s, "Layers of protection.", 4, _sw_pick_from_bank(
        (
            'OS security: user accounts, permissions, patches and firewall integration',
            'Encryption utility: encrypts files or volumes so stolen disk data stays unreadable',
        ),
        (
            'OS security: only compresses files to save disk space',
            'Encryption utility: replaces the need for any user accounts or passwords',
            'OS security: reorganises fragmented files on a hard disk drive',
            'Encryption utility: decides which process gets the CPU next during multitasking',
        ),
        2,
        format_hint='Select one statement about OS security and one about encryption utilities',
    )


def _sw_d6_exam_os_functions():
    q = "Select <strong>five functions</strong> of an operating system (OCR 1.5.1)."
    s = (
        "1) <strong>User interface</strong> (GUI/CLI) 2) <strong>Memory management</strong> &amp; multitasking "
        "3) <strong>Peripheral management</strong> &amp; drivers 4) <strong>User management</strong> "
        "5) <strong>File management</strong>"
    )
    return q, s, "Memorise OCR list exactly.", 4, _sw_pick_from_bank(
        (
            'Provides a user interface (GUI or CLI)',
            'Memory management and multitasking',
            'Peripheral management and device drivers',
            'User management (accounts and permissions)',
            'File management (folders, create, delete, copy files)',
        ),
        (
            'Performs arithmetic operations inside the ALU',
            'Stores the bootstrap firmware in ROM permanently',
            'Replaces all application software on the computer',
            'Increases the physical clock speed of the CPU hardware',
        ),
        5,
        format_hint='Select five functions of an operating system',
    )


def _sw_d7_exam_utilities():
    q = (
        "Select <strong>three utility types</strong> required by OCR 1.5.2, "
        "each with its correct purpose."
    )
    s = (
        "<strong>Encryption</strong> — protect confidentiality of data. "
        "<strong>Defragmentation</strong> — optimise file layout on HDD. "
        "<strong>Data compression</strong> — reduce file size for storage/transmission."
    )
    return q, s, "Three named utilities.", 4, _sw_pick_from_bank(
        (
            'Encryption — protects confidentiality of data by making it unreadable without a key',
            'Defragmentation — optimises file layout on a hard disk drive',
            'Data compression — reduces file size for storage or transmission',
        ),
        (
            'Processor scheduling — decides which process uses the CPU next',
            'User interface — provides windows, icons, menus and pointers',
            'Virtual memory — uses disk space when physical RAM is full',
            'Device driver — only used for installing application software',
        ),
        3,
        format_hint='Select three utility types with their correct purpose',
    )


def _sw_d8_multitasking_limit():
    q = (
        "Why can opening too many programs make a PC <strong>slow</strong> even with multitasking? "
        "Select two correct reasons."
    )
    s = (
        "RAM fills → OS uses <strong>virtual memory</strong> on disk (much slower) or waits for CPU time slices; "
        "context switching adds overhead — <strong>appears</strong> simultaneous but resources are finite."
    )
    return q, s, "Thrashing / swapping.", 4, _sw_pick_from_bank(
        (
            'RAM fills up so the OS uses virtual memory on disk, which is much slower',
            'The CPU must share time slices between many processes, adding overhead',
            'Excessive paging (thrashing) slows the system when memory is overcommitted',
        ),
        (
            'Multitasking allows unlimited programs with no performance impact',
            'Opening more programs always increases the physical clock speed of the CPU',
            'Virtual memory is faster than RAM when many programs are open',
        ),
        2,
        format_hint='Select two reasons the PC becomes slow',
    )


def _sw_d9_cli_script():
    q = (
        "Give a <strong>CLI advantage</strong> when deploying software to 500 school PCs. "
        "Select one correct answer."
    )
    s = (
        "Administrators can run <strong>scripts/batch files</strong> remotely (e.g. PowerShell, SSH) "
        "to install updates automatically — faster and more consistent than clicking GUI on each machine."
    )
    return q, s, "Automation.", 3, _sw_mcq_payload(
        'Administrators can run scripts or batch files remotely to install updates automatically',
        [
            'Administrators must click through the GUI on each of the 500 PCs individually',
            'CLI cannot be used for remote administration of computers on a network',
            'GUI scripting is always faster than command-line tools for mass deployment',
        ],
    )


def _sw_d10_classify_software():
    q = (
        "Classify each item: <strong>Windows 11</strong>, <strong>Microsoft Teams</strong>, "
        "<strong>7-Zip</strong>, <strong>printer driver</strong>."
    )
    s = (
        "<strong>Windows 11</strong> — operating system (system). "
        "<strong>Teams</strong> — application. "
        "<strong>7-Zip</strong> — utility (compression). "
        "<strong>Printer driver</strong> — system software (driver) for peripheral management."
    )
    win_opts, win_ans = _sw_mcq_match_field(
        'Operating system (system software)',
        [
            'Application software for end-user tasks',
            'Utility software for data compression',
        ],
    )
    teams_opts, teams_ans = _sw_mcq_match_field(
        'Application software',
        [
            'Operating system (system software)',
            'Device driver for peripheral management',
        ],
    )
    zip_opts, zip_ans = _sw_mcq_match_field(
        'Utility software (compression)',
        [
            'Operating system (system software)',
            'Application software for communication',
        ],
    )
    driver_opts, driver_ans = _sw_mcq_match_field(
        'System software (device driver)',
        [
            'Application software for end-user tasks',
            'Utility software for defragmentation',
        ],
    )
    return q, s, "Four-way classification.", 4, graded_answer_number_fields(
        (win_ans, teams_ans, zip_ans, driver_ans),
        ('Windows 11', 'Microsoft Teams', '7-Zip', 'Printer driver'),
        field_types=('mcq', 'mcq', 'mcq', 'mcq'),
        field_options=(win_opts, teams_opts, zip_opts, driver_opts),
    )


def _sw_d11_backup_strategy():
    q = (
        "A school server holds coursework folders. "
        "Select <strong>three</strong> elements of a sensible <strong>backup strategy</strong>."
    )
    s = (
        "<strong>Regular automated backups</strong> (daily incremental, weekly full). "
        "Store at least one copy <strong>off-site</strong> or in the cloud. "
        "Test restores periodically; protect backup media with encryption/access control."
    )
    return q, s, "3-2-1 rule: 3 copies, 2 media types, 1 off-site.", 3, _sw_pick_from_bank(
        (
            'Regular automated backups (e.g. daily incremental, weekly full)',
            'Store at least one backup copy off-site or in the cloud',
            'Test restores periodically to ensure backups work',
            'Protect backup media with encryption or access control',
        ),
        (
            'Never test whether backups can be restored',
            'Keep all backup copies on the same server with no off-site copy',
            'Back up only once per year with no incremental copies',
        ),
        3,
        format_hint='Select three elements of a sensible backup strategy',
    )


def _sw_d12_page_fault():
    q = (
        "When RAM is full, the OS may move a page to disk and later bring it back. "
        "Select the correct <strong>name</strong> for this process and <strong>one reason</strong> "
        "it is slower than using RAM."
    )
    s = (
        "<strong>Virtual memory / paging</strong> — disk (secondary storage) has much "
        "<strong>higher latency</strong> than RAM, so excessive paging causes thrashing and slowdown."
    )
    return q, s, "Swap file on HDD/SSD is the overflow area.", 3, _sw_pick_from_bank(
        (
            'Virtual memory / paging',
            'Disk (secondary storage) has much higher latency than RAM',
            'Excessive paging causes thrashing and slows the system down',
        ),
        (
            'Defragmentation of the hard drive',
            'RAM is slower than disk because it is non-volatile',
            'Compression reduces the number of pages stored in memory',
        ),
        2,
        format_hint='Select the name and one reason it is slower than RAM',
    )


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _sw_d13_multipart_os_management():
    q = (
        "An operating system manages several resources at once while a user runs a browser, "
        "a music player, and a word processor.<br><br>"
        "<strong>a)</strong> Select <strong>two</strong> correct statements about how the OS uses "
        "<strong>memory management</strong>. [2]<br>"
        "<strong>b)</strong> Select <strong>two</strong> correct statements about "
        "<strong>peripheral / device management</strong>. [2]<br>"
        "<strong>c)</strong> Select <strong>two</strong> correct statements about how "
        "<strong>user management</strong> helps keep a shared computer secure. [2]"
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
    mem_raw, mem_bank, mem_pick = _sw_pick_field(
        (
            'Allocates a section of RAM to each program',
            'Keeps track of what is stored where so programs do not overwrite each other',
            'Can use virtual memory when physical RAM is full',
        ),
        (
            'Allows every program to use the same memory addresses with no tracking',
            'Stores all running programs permanently in ROM instead of RAM',
        ),
        2,
    )
    periph_raw, periph_bank, periph_pick = _sw_pick_field(
        (
            'Installs and uses device drivers to communicate with peripherals',
            'Manages the transfer of data between peripherals and the CPU',
            'Schedules access to input/output devices',
        ),
        (
            'Only organises files into folders on the hard drive',
            'Replaces the need for any device drivers on the system',
        ),
        2,
    )
    user_raw, user_bank, user_pick = _sw_pick_field(
        (
            'Provides separate accounts with passwords for each user',
            'Sets access rights so users only see files they are authorised to access',
            'Protects other users\u2019 files from unauthorised changes',
        ),
        (
            'Gives every user full administrator access to all files',
            'Removes the need for any passwords on shared computers',
        ),
        2,
    )
    return q, s, "OS = memory (share RAM), devices (drivers), users (accounts & rights).", 6, graded_answer_number_fields(
        (mem_raw, periph_raw, user_raw),
        ('Memory management', 'Peripheral management', 'User management'),
        field_types=('pick', 'pick', 'pick'),
        field_options=(mem_bank, periph_bank, user_bank),
        field_pick_counts=(mem_pick, periph_pick, user_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


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
    comp_raw, comp_bank, comp_pick = _sw_pick_field(
        (
            'Data compression \u2014 reduces file size so more data fits in the same space',
        ),
        (
            'Defragmentation \u2014 splits files into smaller pieces across the disk',
            'Encryption \u2014 makes files unreadable without a password',
        ),
        1,
    )
    defrag_raw, defrag_bank, defrag_pick = _sw_pick_field(
        (
            'Defragmentation \u2014 moves fragmented file pieces so each file is stored together',
            'Defragmentation reduces head movement so files load faster on an HDD',
        ),
        (
            'Compression \u2014 reduces the number of bits needed to store each file',
            'Encryption \u2014 protects files from unauthorised access',
        ),
        1,
    )
    ssd_raw, ssd_bank, ssd_pick = _sw_pick_field(
        (
            'An SSD has no moving parts and accesses any location equally quickly',
            'Defragmentation causes extra unnecessary write operations on an SSD',
            'Defragmentation can shorten the SSD\u2019s lifespan with little speed benefit',
        ),
        (
            'SSDs must be defragmented weekly to stay fast',
            'Defragmentation always doubles the read speed of any SSD',
        ),
        2,
    )
    return q, s, "Compression saves space; defrag helps HDDs but harms SSDs.", 6, graded_answer_number_fields(
        (comp_raw, defrag_raw, ssd_raw),
        ('Compression utility', 'Defrag on HDD', 'Why not on SSD'),
        field_types=('pick', 'pick', 'pick'),
        field_options=(comp_bank, defrag_bank, ssd_bank),
        field_pick_counts=(comp_pick, defrag_pick, ssd_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


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

    return _sw_problem_from_output(variant(), difficulty)
