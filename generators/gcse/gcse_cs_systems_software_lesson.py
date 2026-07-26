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


def _sw_mcq_payload(correct_variants, distractor_groups):
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


def _sw_mcq_options(correct_variants, distractor_groups):
    """Build shuffled MCQ options for bank items (returns opts list + correct letter)."""
    payload = _sw_mcq_payload(correct_variants, distractor_groups)
    return payload['options'], payload['correct']


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
        (
            'Software that manages computer resources for application software',
            'Software that manages computer resources and provides a platform for application software',
            'Software that manages computer resources and provides a platform for other application software to run on',
        ),
        (
            ('Programs for everyday tasks such as word processing', 'Programs that help users perform everyday tasks such as word processing or browsing the web'),
            ('Hardware built into the CPU that performs calculations', 'Physical hardware inside the CPU that performs arithmetic and logic calculations only'),
            ('Data stored permanently on secondary storage devices', 'Structured data stored permanently on secondary storage devices with no programs involved'),
        ),
    )


def _sw_f2_application_software():
    q = "What is <strong>application software</strong>? Select one correct answer."
    s = (
        "Programs that help users perform <strong>tasks</strong> — browsers, games, "
        "word processors, photo editors."
    )
    return q, s, "Runs on top of the OS.", 1, _sw_mcq_payload(
        (
            'Programs that help users perform tasks',
            'Programs that help users perform tasks (e.g. browsers, word processors, games)',
            'Programs that help users perform everyday tasks such as browsing, word processing or playing games',
        ),
        (
            ('Software that manages hardware resources and runs the operating system', 'System software that manages hardware resources and runs the operating system kernel'),
            ('Firmware stored in ROM that starts the computer on power-on', 'Firmware stored in ROM that starts the computer when power is switched on'),
            ('Device drivers that translate commands for peripherals only', 'Device drivers that translate commands for peripherals and nothing else'),
        ),
    )


def _sw_f3_os_purpose():
    q = "What is the main purpose of an <strong>operating system</strong>? Select one correct answer."
    s = (
        "To <strong>manage hardware and software resources</strong> and provide services "
        "so applications can run (memory, files, users, devices)."
    )
    return q, s, "Bridge between user/apps and hardware.", 2, _sw_mcq_payload(
        (
            'To manage hardware and software resources so applications can run',
            'To manage hardware and software resources and provide services so applications can run',
            'To manage hardware and software resources and provide services so application programs can run (memory, files, users, devices)',
        ),
        (
            ('To perform arithmetic and logic operations inside the CPU', 'To perform arithmetic and logic operations inside the CPU only, with no resource management'),
            ('To store the bootstrap instructions that start the computer', 'To store the bootstrap instructions that start the computer before any applications load'),
            ('To replace application programs such as web browsers', 'To replace application programs such as web browsers and word processors entirely'),
        ),
    )


def _sw_f4_gui():
    q = "What is a <strong>GUI</strong> (graphical user interface)? Select one correct answer."
    s = (
        "An interface using <strong>windows, icons, menus and pointers</strong> (WIMP) "
        "so users interact visually — e.g. Windows desktop, macOS."
    )
    return q, s, "Point-and-click.", 1, _sw_mcq_payload(
        (
            'An interface using windows, icons, menus and pointers',
            'An interface using windows, icons, menus and pointers so users interact visually',
            'An interface using windows, icons, menus and pointers (WIMP) so users interact visually with the system',
        ),
        (
            ('An interface where users type text commands only', 'An interface where users type text commands only with no visual menus or icons'),
            ('Software that encrypts files on a hard drive', 'Utility software that encrypts files on a hard drive so they cannot be read without a key'),
            ('A program that compresses files into ZIP archives', 'A compression program that reduces file size by packing files into ZIP archives'),
        ),
    )


def _sw_f5_cli():
    q = "What is a <strong>CLI</strong> (command-line interface)? Select one correct answer."
    s = (
        "Users type <strong>text commands</strong> to control the system — e.g. "
        "<code>cd</code>, <code>dir</code>, Linux shell. Powerful for admins; steeper learning curve."
    )
    return q, s, "No menus — typed commands.", 2, _sw_mcq_payload(
        (
            'Users type text commands to control the system',
            'Users type text commands to control the system (e.g. cd, dir, shell commands)',
            'Users type text commands at a prompt to control the system rather than using menus and icons',
        ),
        (
            ('Users click windows, icons, menus and pointers to control the system', 'Users click windows, icons, menus and pointers in a graphical interface to control the system'),
            ('The CPU fetches, decodes and executes machine-code instructions', 'The CPU fetches, decodes and executes machine-code instructions as part of the fetch-decode-execute cycle'),
            ('A utility that reorganises fragmented files on a hard disk', 'A defragmentation utility that reorganises fragmented files on a magnetic hard disk'),
        ),
    )


def _sw_f6_multitasking():
    q = "What is <strong>multitasking</strong>? Select one correct answer."
    s = (
        "The OS running <strong>several programs apparently at once</strong> by "
        "time-slicing the CPU or scheduling tasks."
    )
    return q, s, "Music + browser open together.", 2, _sw_mcq_payload(
        (
            'The OS runs several programs apparently at once by scheduling the CPU',
            'The OS running several programs apparently at once by time-slicing or scheduling the CPU',
            'The OS running several programs apparently at once by time-slicing the CPU or scheduling tasks fairly',
        ),
        (
            ('Running one program until it finishes before starting another', 'Running one program until it finishes completely before starting another program'),
            ('Installing device drivers for every peripheral on the computer', 'Installing device drivers for every peripheral on the computer during boot only'),
            ('Encrypting all files on the hard drive automatically', 'Encrypting all files on the hard drive automatically without any user action'),
        ),
    )


def _sw_f7_driver():
    q = "What is a <strong>device driver</strong>? Select one correct answer."
    s = (
        "Software that lets the OS <strong>communicate with a peripheral</strong> "
        "(printer, GPU, keyboard) — often installed when hardware is added."
    )
    return q, s, "Translator for hardware.", 2, _sw_mcq_payload(
        (
            'Software that lets the OS communicate with a peripheral',
            'Software that lets the OS communicate with a peripheral device',
            'Software that lets the operating system communicate with a peripheral device such as a printer or keyboard',
        ),
        (
            ('Application software that helps users write documents', 'Application software that helps users write documents and perform end-user tasks'),
            ('The main program that manages all hardware and software resources', 'The operating system kernel that manages all hardware and software resources for the whole computer'),
            ('A utility that reduces file size for email attachments', 'A compression utility that reduces file size for email attachments using ZIP-style algorithms'),
        ),
    )


def _sw_f8_utility():
    q = "What is <strong>utility software</strong>? Select one correct answer."
    s = (
        "System software that <strong>maintains or optimises</strong> the computer — "
        "encryption, defragmentation, compression (OCR), plus common extras like antivirus."
    )
    return q, s, "Helps manage the system, not write essays.", 2, _sw_mcq_payload(
        (
            'System software that maintains or optimises the computer',
            'System software that maintains or optimises the computer (e.g. antivirus, defrag, compression)',
            'System software that maintains, optimises or protects the computer rather than performing end-user tasks',
        ),
        (
            ('Programs that help users perform everyday tasks such as browsing the web', 'Application programs that help users perform everyday tasks such as browsing the web or writing documents'),
            ('Hardware inside the CPU that performs calculations', 'Physical hardware inside the CPU that performs arithmetic calculations only'),
            ('The operating system kernel that manages all resources', 'The operating system kernel that manages all hardware and software resources for every program'),
        ),
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
        (
            'The OS controls accounts, passwords and permissions',
            'The OS controls accounts, passwords and permissions for who can log in and access files',
            'The OS controls user accounts, passwords and permissions so only authorised users can access files and settings',
        ),
        (
            ('Software that reduces file size using ZIP-style compression', 'Utility software that reduces file size using ZIP-style compression algorithms'),
            ('The process of reorganising fragmented files on a hard disk', 'The process of reorganising fragmented files on a magnetic hard disk to improve read speed'),
            ('Firmware that runs POST before the operating system loads', 'Firmware stored in ROM that runs POST hardware checks before the operating system loads'),
        ),
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
        (
            'The OS controls input/output devices and loads drivers',
            'The OS controls input/output devices, loads drivers and handles device access',
            'The OS controls input/output devices, loads drivers, handles plug-and-play and reports device errors',
        ),
        (
            ('The OS organises files into folders and sets file permissions only', 'The OS organises files into folders and sets file permissions but does not manage devices'),
            ('The OS allocates RAM and manages virtual memory when RAM is full', 'The OS allocates RAM to programs and manages virtual memory on disk when physical RAM is full'),
            ('The OS compresses files to reduce storage space on the hard drive', 'The OS compresses files automatically to reduce storage space on the hard drive for every user'),
        ),
    )


def _sw_i3_encryption_utility():
    q = "How does <strong>encryption utility software</strong> help? Select one correct answer."
    s = (
        "Encrypts files or whole drives so data is <strong>unreadable without the key</strong> — "
        "protects data if a laptop is stolen (works with OS security)."
    )
    return q, s, "BitLocker, VeraCrypt examples.", 2, _sw_mcq_payload(
        (
            'Encrypts files or drives so data is unreadable without the key',
            'Encrypts files or drives so data is unreadable without the correct key',
            'Encrypts files or whole drives so stored data is unreadable without the correct decryption key',
        ),
        (
            ('Reorganises fragmented files on a hard disk', 'Reorganises fragmented files on a magnetic hard disk so related blocks are stored contiguously'),
            ('Reduces file size using lossless compression algorithms such as ZIP', 'Reduces file size using lossless compression algorithms such as ZIP for storage or transfer'),
            ('Creates user accounts and sets login passwords for the operating system', 'Creates user accounts and sets login passwords as part of operating system user management'),
        ),
    )


def _sw_i4_defragmentation():
    q = "What does <strong>defragmentation</strong> do on a traditional HDD? Select one correct answer."
    s = (
        "Reorganises fragmented files so related blocks are <strong>contiguous</strong>, "
        "reducing head movement and often improving read speed. "
        "<strong>Not recommended for SSDs</strong> (unnecessary wear)."
    )
    return q, s, "Fragments spread over disk.", 3, _sw_mcq_payload(
        (
            'Reorganises fragmented files so related blocks are stored contiguously',
            'Reorganises fragmented files so related blocks are stored contiguously, reducing head movement',
            'Reorganises fragmented files on an HDD so related blocks are stored contiguously, reducing head movement and improving read speed',
        ),
        (
            ('Encrypts files so they cannot be read without a password', 'Encrypts files so they cannot be read without the correct password or decryption key'),
            ('Reduces file size using compression algorithms such as ZIP', 'Reduces file size using lossless compression algorithms such as ZIP for email attachments'),
            ('Allocates RAM to each running program when memory is low', 'Allocates RAM to each running program and uses virtual memory when physical RAM is low'),
        ),
    )


def _sw_i5_compression():
    q = "What does <strong>data compression</strong> utility software do? Select one correct answer."
    s = (
        "Reduces file size using algorithms like <strong>ZIP</strong> — "
        "<strong>lossless</strong> for documents (exact restore); can save storage and bandwidth."
    )
    return q, s, "Smaller archives for email.", 2, _sw_mcq_payload(
        (
            'Reduces file size using compression algorithms',
            'Reduces file size using compression algorithms, often losslessly for documents',
            'Reduces file size using compression algorithms (often lossless for documents) to save storage and bandwidth',
        ),
        (
            ('Reorganises fragmented files on a magnetic hard disk drive', 'Reorganises fragmented files on a magnetic hard disk drive to reduce head movement'),
            ('Encrypts data so it is unreadable without the correct key', 'Encrypts data so it is unreadable without the correct decryption key or password'),
            ('Installs device drivers so peripherals can communicate with the OS', 'Installs device drivers so peripherals such as printers can communicate with the operating system'),
        ),
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
        (
            'Scheduling decides which process gets the CPU next',
            'Scheduling decides which process gets the CPU next using time slices or priority',
            'Scheduling decides which process gets the CPU next using time slices or priority so multitasking works fairly',
        ),
        (
            ('The OS runs one program until it finishes before starting the next', 'The OS runs one program until it finishes completely before starting the next program'),
            ('The OS stores all running programs permanently in ROM', 'The OS stores all running programs permanently in ROM instead of RAM during execution'),
            ('The OS defragments the hard drive while programs are running', 'The OS defragments the hard drive automatically while application programs are running'),
        ),
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
        (
            'The OS needs a device driver to translate commands for the printer',
            'The OS needs a device driver to translate commands into instructions the printer understands',
            'The OS needs a device driver to translate generic print commands into instructions the printer hardware understands',
        ),
        (
            ('The OS needs a compression utility to reduce the size of print jobs', 'The OS needs a compression utility to reduce the size of print jobs before sending them to the printer'),
            ('The OS needs an encryption utility before any file can be sent to a printer', 'The OS needs an encryption utility before any file can be sent to a printer over the network'),
            ('The OS replaces the printer hardware with virtual memory on the hard disk', 'The OS replaces the printer hardware with virtual memory stored on the hard disk instead of using a driver'),
        ),
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
        (
            'Uses disk space as extra memory when physical RAM is full',
            'Uses disk space as extra memory when physical RAM is full so more programs can run',
            'Uses disk space on the hard drive as extra memory when physical RAM is full so more programs can run, though access is slower',
        ),
        (
            ('Extra RAM chips installed inside the CPU for faster access', 'Extra RAM chips installed inside the CPU for faster access than main memory'),
            ('A compression utility that reduces the size of files on the hard drive', 'A compression utility that reduces the size of files on the hard drive using ZIP-style algorithms'),
            ('Firmware stored in ROM that starts the computer before the OS loads', 'Firmware stored in ROM that starts the computer and runs POST before the operating system loads'),
        ),
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
        (
            'Administrators can run scripts remotely to install updates automatically',
            'Administrators can run scripts or batch files remotely to install updates automatically',
            'Administrators can run scripts or batch files remotely (e.g. PowerShell, SSH) to install updates automatically on many PCs',
        ),
        (
            ('Administrators must click through the GUI on each of the 500 PCs individually', 'Administrators must click through the graphical interface on each of the 500 PCs individually to install software'),
            ('CLI cannot be used for remote administration of computers on a network', 'Command-line interfaces cannot be used for remote administration of computers on a school network'),
            ('GUI scripting is always faster than command-line tools for mass deployment', 'GUI scripting is always faster than command-line tools when deploying software to hundreds of computers'),
        ),
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
     "correct": (
         "Manages resources and runs the platform for other software",
         "Software that manages resources and provides a platform for other software",
         "System software that manages computer resources and runs the platform for application software",
     ),
     "wrong": (
         ("Only games", "Software that only runs games and nothing else"),
         ("Is the CPU", "The physical CPU chip itself with no programs involved"),
         ("Only web browsers", "Software that only runs web browsers and no other programs"),
     ),
     "marks": 1, "difficulty": "foundational",
     "sol": "<strong>Manages the computer</strong>.",
     "hint": "OS + utilities."},
    {"q": "A GUI uses:",
     "correct": (
         "Windows, icons, menus and pointers",
         "An interface with windows, icons, menus and pointers",
         "A graphical interface using windows, icons, menus and pointers (WIMP) for visual interaction",
     ),
     "wrong": (
         ("Typed commands only", "Typed text commands only with no visual menus or icons"),
         ("No output", "An interface that produces no output to the user at all"),
         ("Only machine code", "An interface that displays only raw machine code to the user"),
     ),
     "marks": 1, "difficulty": "foundational",
     "sol": "<strong>Visual WIMP interface</strong>.",
     "hint": "Desktop metaphor."},
    {"q": "Multitasking means:",
     "correct": (
         "Several programs appear to run at once",
         "The OS runs several programs apparently at once",
         "The operating system runs several programs apparently at once by scheduling CPU time",
     ),
     "wrong": (
         ("One program ever", "Only one program can ever be stored on the computer"),
         ("No CPU", "Multitasking means the computer has no CPU at all"),
         ("Only printing", "Multitasking means the computer can only run printing tasks"),
     ),
     "marks": 2, "difficulty": "foundational",
     "sol": "OS <strong>schedules</strong> CPU time.",
     "hint": "Time slicing."},
    {"q": "A device driver:",
     "correct": (
         "Lets the OS communicate with hardware",
         "Software that lets the OS communicate with hardware",
         "Software that lets the operating system communicate with a hardware device such as a printer",
     ),
     "wrong": (
         ("Replaces the CPU", "A program that replaces the CPU and performs all calculations"),
         ("Is always an application", "Is always application software for end-user tasks only"),
         ("Deletes all files", "Software that deletes all files on the hard drive automatically"),
     ),
     "marks": 2, "difficulty": "foundational",
     "sol": "<strong>Hardware interface</strong>.",
     "hint": "Printer won't work without one."},
    {"q": "Defragmentation is mainly for:",
     "correct": (
         "Traditional HDDs",
         "Traditional magnetic hard disk drives (HDDs)",
         "Traditional magnetic hard disk drives where a read/write head moves across platters",
     ),
     "wrong": (
         ("SSDs only", "Solid-state drives (SSDs) only and never magnetic hard disks"),
         ("Monitors", "Computer monitors and display screens only"),
         ("Keyboards", "Keyboards and other input devices only"),
     ),
     "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>HDD</strong> head movement.",
     "hint": "Avoid on SSD."},
    {"q": "Compression utilities:",
     "correct": (
         "Reduce file size for storage or transfer",
         "Reduce file size to save storage space or transfer time",
         "Reduce file size using compression algorithms for storage or transfer (e.g. ZIP archives)",
     ),
     "wrong": (
         ("Increase file size always", "Always increase file size every time they are used"),
         ("Install drivers", "Install device drivers so peripherals can communicate with the OS"),
         ("Replace the OS", "Replace the operating system kernel entirely on the computer"),
     ),
     "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>ZIP-style</strong> tools.",
     "hint": "Archives."},
    {"q": "User management includes:",
     "correct": (
         "Accounts and permissions",
         "User accounts, passwords and access permissions",
         "Managing user accounts, passwords and permissions so only authorised users can access files",
     ),
     "wrong": (
         ("Overclocking the GPU only", "Overclocking the GPU to increase its clock speed only"),
         ("Drawing icons", "Drawing desktop icons and choosing wallpaper colours only"),
         ("Compiling Python", "Compiling Python source code into machine code only"),
     ),
     "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>Who can access what</strong>.",
     "hint": "Login accounts."},
    {"q": "File management includes:",
     "correct": (
         "Folders, create/delete/copy files",
         "Organising folders and creating, deleting or copying files",
         "Organising files in folders and creating, deleting, copying or locating files on storage",
     ),
     "wrong": (
         ("Only RAM timing", "Setting the timing of RAM chips inside the CPU only"),
         ("Monitor brightness", "Adjusting monitor brightness and contrast settings only"),
         ("Network cables", "Installing and testing physical network cables only"),
     ),
     "marks": 1, "difficulty": "intermediate",
     "sol": "<strong>Directory structure</strong>.",
     "hint": "Explorer tasks."},
    {"q": "A CLI interface:",
     "correct": (
         "Uses typed commands",
         "Users type text commands to control the system",
         "Users type text commands at a prompt to control the system rather than using menus",
     ),
     "wrong": (
         ("Has no keyboard", "An interface that cannot use a keyboard for any input"),
         ("Is only for printers", "An interface used only for controlling printers and nothing else"),
         ("Cannot run scripts", "An interface that cannot run scripts or batch files at all"),
     ),
     "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>Command line</strong>.",
     "hint": "Shell/CMD."},
    {"q": "Memory management by the OS:",
     "correct": (
         "Allocates RAM to programs",
         "Allocates RAM to running programs and tracks memory use",
         "Allocates RAM to each running program and reclaims memory when programs close",
     ),
     "wrong": (
         ("Paints the desktop", "Paints the desktop background and window borders only"),
         ("Sells laptops", "Manages online shops that sell laptop computers to customers"),
         ("Removes copyright", "Removes copyright protection from all files automatically"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "<strong>RAM allocation</strong>.",
     "hint": "Tracks memory use."},
    {"q": "Encryption utility software:",
     "correct": (
         "Makes data unreadable without the key",
         "Encrypts data so it is unreadable without the correct key",
         "Encrypts files or drives so data is unreadable without the correct decryption key",
     ),
     "wrong": (
         ("Speeds up the CPU clock", "Increases the clock speed of the CPU for faster processing"),
         ("Defragments SSDs", "Defragments solid-state drives to reorganise fragmented files"),
         ("Creates user accounts", "Creates user accounts and sets login passwords for the OS"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "<strong>Confidentiality</strong>.",
     "hint": "OCR utility type."},
    {"q": "Microsoft Word is:",
     "correct": (
         "Application software",
         "Application software for end-user tasks",
         "Application software that helps users perform tasks such as writing documents",
     ),
     "wrong": (
         ("The operating system", "The operating system that manages all hardware and software resources"),
         ("A device driver", "A device driver that lets the OS communicate with a printer"),
         ("Firmware in the CPU", "Firmware stored inside the CPU that starts the computer on power-on"),
     ),
     "marks": 1, "difficulty": "foundational",
     "sol": "<strong>End-user task</strong> software.",
     "hint": "Runs on Windows."},
    {"q": "Virtual memory uses:",
     "correct": (
         "Disk space when RAM is full",
         "Disk space on storage when physical RAM is full",
         "Disk space used as extra memory when physical RAM is full so more programs can run",
     ),
     "wrong": (
         ("Only cache inside CPU", "Only cache memory stored inside the CPU with no disk involved"),
         ("Monitor pixels", "Memory used to store the colour of every pixel on the monitor"),
         ("Printer ink", "Ink stored inside a printer cartridge for printing documents"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "<strong>Swap/page file</strong>.",
     "hint": "Slower than RAM."},
    {"q": "Peripheral management involves:",
     "correct": (
         "Drivers and I/O devices",
         "Managing I/O devices and loading device drivers",
         "Controlling input/output devices, loading drivers and handling plug-and-play access",
     ),
     "wrong": (
         ("Only file names", "Renaming files and choosing file extensions only"),
         ("GCSE grades", "Recording GCSE grades for pupils in a school database only"),
         ("Binary addition in ALU only", "Performing binary addition inside the ALU only"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "<strong>Devices + drivers</strong>.",
     "hint": "Keyboard, USB, printer."},
    {"q": "Windows 11 kernel is:",
     "correct": (
         "Part of the operating system",
         "Core part of the operating system",
         "The core part of the operating system that manages hardware and system resources",
     ),
     "wrong": (
         ("Application software", "Application software that helps users write documents or browse the web"),
         ("A compression utility only", "A compression utility that only reduces file size using ZIP algorithms"),
         ("RAM chip", "A physical RAM chip installed on the computer's motherboard"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "<strong>OS core</strong>.",
     "hint": "System software."},
    {"q": "A full backup:",
     "correct": (
         "Copies all selected data each time",
         "Copies every file in the selected scope each time",
         "Copies all selected data in full each time the backup runs, not just changes since last time",
     ),
     "wrong": (
         ("Never uses storage space", "Never uses any storage space on backup media or cloud storage"),
         ("Only backs up files deleted yesterday", "Only backs up files that were deleted on the previous day"),
         ("Replaces the CPU", "Replaces the CPU with a faster model during the backup process"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "Copies <strong>everything</strong> in scope.",
     "hint": "Contrast with incremental."},
    {"q": "Thrashing occurs when:",
     "correct": (
         "The OS spends too much time swapping pages between RAM and disk",
         "The OS spends too much time moving pages between RAM and disk",
         "The OS spends too much time swapping pages between RAM and disk instead of running programs",
     ),
     "wrong": (
         ("The monitor refreshes faster", "The monitor refresh rate increases and the display updates faster"),
         ("A GUI uses icons", "A graphical user interface displays icons on the desktop"),
         ("A user logs out", "A user logs out of their account and ends their session"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "Excessive <strong>paging</strong> slows the system.",
     "hint": "Too little RAM for running programs."},
    {"q": "Utility software is designed to:",
     "correct": (
         "Perform maintenance or security tasks on the system",
         "Maintain, optimise or protect the computer system",
         "Perform maintenance, optimisation or security tasks on the computer system",
     ),
     "wrong": (
         ("Replace the operating system kernel", "Replace the operating system kernel and manage all hardware directly"),
         ("Be the CPU", "Act as the physical CPU that executes machine-code instructions"),
         ("Only run games", "Run games only and cannot perform any maintenance tasks"),
     ),
     "marks": 2, "difficulty": "intermediate",
     "sol": "Utilities <strong>maintain or protect</strong> the computer.",
     "hint": "Antivirus, defrag, compression tools."},
    {"q": "A process in an operating system is:",
     "correct": (
         "A program currently being executed",
         "A running instance of a program being executed",
         "A program that is currently being executed by the CPU with its own memory space",
     ),
     "wrong": (
         ("Only a file icon", "Only a graphical icon displayed on the desktop with no running code"),
         ("The monitor cable", "The cable connecting the monitor to the computer case"),
         ("A type of keyboard", "A special type of keyboard used only by system administrators"),
     ),
     "marks": 2, "difficulty": "intermediate",
     "sol": "A running instance of a <strong>program</strong>.",
     "hint": "Task Manager lists processes."},
    {"q": "Scheduling in the OS decides:",
     "correct": (
         "Which process uses the CPU next",
         "Which process gets the CPU next during multitasking",
         "Which process uses the CPU next using time slices or priority during multitasking",
     ),
     "wrong": (
         ("The colour of desktop icons only", "The colour of desktop icons and wallpaper only"),
         ("How to print paper", "How much paper to load into a printer tray only"),
         ("The price of laptops", "The retail price of laptop computers sold to customers"),
     ),
     "marks": 2, "difficulty": "difficult",
     "sol": "CPU time is <strong>allocated between processes</strong>.",
     "hint": "Part of multitasking."},
    {"q": "Firmware is software that is:",
     "correct": (
         "Stored in non-volatile memory and controls hardware at startup",
         "Stored in ROM or flash and controls hardware during startup",
         "Stored in non-volatile memory and controls hardware during startup (e.g. BIOS/UEFI)",
     ),
     "wrong": (
         ("Always deleted when power is lost", "Always deleted from memory every time power is lost"),
         ("Only a web browser", "Only a web browser application such as Chrome or Firefox"),
         ("The same as a word processor", "The same as a word processor such as Microsoft Word"),
     ),
     "marks": 2, "difficulty": "foundational",
     "sol": "Firmware such as BIOS/UEFI is <strong>semi-permanent</strong>.",
     "hint": "Stored on ROM/flash chips."},
    {"q": "Disk cleanup utilities help by:",
     "correct": (
         "Removing unnecessary files to free storage space",
         "Deleting temporary and unnecessary files to free disk space",
         "Removing unnecessary files such as temporary files to free storage space on the drive",
     ),
     "wrong": (
         ("Increasing CPU clock speed", "Increasing the clock speed of the CPU for faster program execution"),
         ("Assigning IP addresses", "Assigning IP addresses to devices on a local network automatically"),
         ("Writing SQL queries", "Writing SQL queries to search and update records in a database"),
     ),
     "marks": 2, "difficulty": "intermediate",
     "sol": "Deletes temp files and frees <strong>disk space</strong>.",
     "hint": "Common Windows/macOS maintenance tool."},
]

_LESSON_QUIZ_MIX = (
    ("foundational", 3),
    ("intermediate", 4),
    ("difficult", 3),
)


def _sw_mcq_item_to_problem(item, difficulty):
    opts, ans = _sw_mcq_options(item["correct"], item["wrong"])
    return make_problem(
        item["q"], item["sol"], item["hint"], difficulty, item["marks"],
        "gcse", "cs", "systems_software",
        options=opts, correct_answer=ans,
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
    opts, ans = _sw_mcq_options(item["correct"], item["wrong"])
    return item["q"], item["sol"], item["hint"], item["marks"], opts, ans


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
