"""
GCSE Computer Science – Cyber Security
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
Graded practice variants use MCQ, pick, order, or multipart fields (no weak free-text definitions).
List/multipart variants may use inline ``number_fields`` (4- or 5-tuples).
"""
import random
from generators.shared.utils import (
    make_problem,
    graded_answer_keyword,
    graded_answer_number_fields,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import pick_named_variant


def _cy_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'cs', 'cyber_security',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        extra = problem_extra_from_graded_answer(raw)
    else:
        extra = {}
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'cyber_security', **extra
    )


def _cy_mcq_match_field(correct_text, distractors):
    """Shuffled 3-option inline MCQ for term–description matching."""
    pool = [correct_text] + list(distractors[:2])
    random.shuffle(pool)
    letters = 'ABC'
    return pool, letters[pool.index(correct_text)]


def _cy_mcq_payload(correct_text, distractors):
    """Four-option practice MCQ; returns payload for _cy_problem_from_output."""
    pool = [correct_text] + list(distractors[:3])
    random.shuffle(pool)
    letters = 'ABCD'
    correct_letter = letters[pool.index(correct_text)]
    options = [f'{letters[i]}  {pool[i]}' for i in range(len(pool))]
    return {'type': 'mcq', 'options': options, 'correct': correct_letter}


def _cy_mcq_graded_field(correct_text, distractors, label='Select the best answer'):
    """Single inline MCQ field for auto-check (practice + sandbox)."""
    payload = _cy_mcq_payload(correct_text, distractors)
    opts = [text.split('  ', 1)[1] for text in payload['options']]
    return graded_answer_number_fields(
        (payload['correct'],),
        (label,),
        field_types=('mcq',),
        field_options=(opts,),
    )


def _cy_pick_from_bank(correct_texts, distractor_texts, pick_count, *, format_hint=None):
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


def _cy_pick_field(correct_texts, distractor_texts, pick_count):
    """Inline pick-N field for multipart ``number_fields`` (returns raw, bank, count)."""
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

def _cy_f1_malware_virus():
    q = "What is <strong>malware</strong>?"
    s = (
        "<strong>Malicious software</strong> designed to damage, disrupt, or gain "
        "unauthorised access to systems (viruses, worms, trojans, ransomware, etc.)."
    )
    return q, s, "Malware = malicious + software.", 1, _cy_mcq_graded_field(
        "Malicious software designed to damage, disrupt, or gain unauthorised access to systems",
        [
            "Hardware that monitors network traffic and blocks unauthorised connections",
            "Legal software that encrypts files to protect them from unauthorised access",
            "A backup copy of data stored on a separate device for recovery",
        ],
    )


def _cy_f2_phishing():
    q = "What is <strong>phishing</strong>?"
    s = (
        "Fake emails, texts, or sites that <strong>trick users</strong> into revealing "
        "passwords, bank details, or clicking malicious links."
    )
    return q, s, "Look-alike logos and urgent language are common signs.", 2, _cy_mcq_graded_field(
        "Fake emails, texts, or sites that trick users into revealing passwords or clicking malicious links",
        [
            "Software that scans files and memory for known virus signatures",
            "Encrypting all data stored on a hard drive with a secret key",
            "Flooding a server with traffic so legitimate users cannot access it",
        ],
    )


def _cy_f3_firewall():
    q = "What does a <strong>firewall</strong> do?"
    s = (
        "Monitors and <strong>filters network traffic</strong>, blocking unauthorised "
        "connections based on rules."
    )
    return q, s, "Hardware or software barrier between trusted and untrusted networks.", 2, _cy_mcq_graded_field(
        "Monitors and filters network traffic, blocking unauthorised connections",
        [
            "Scans files and memory for known malware signatures",
            "Encrypts all data stored on the hard drive",
            "Assigns IP addresses to devices on a local network",
        ],
    )


def _cy_f4_antivirus():
    q = "How does <strong>antivirus software</strong> help protect a computer?"
    s = (
        "Scans files and memory for <strong>known malware signatures</strong> and suspicious "
        "behaviour; can quarantine or remove threats."
    )
    return q, s, "Keep definitions updated for new threats.", 2, _cy_mcq_graded_field(
        "Scans files and memory for known malware signatures and suspicious behaviour",
        [
            "Encrypts all network traffic between the computer and the internet",
            "Assigns a unique IP address to each device on the network",
            "Blocks physical access to the server room with a locked door",
        ],
    )


def _cy_f5_strong_password():
    q = "Select <strong>two features</strong> of a strong password."
    s = (
        "<strong>Long</strong>, mix of upper/lower case, numbers and symbols; "
        "<strong>unique</strong> per account; not based on personal info."
    )
    return q, s, "Passphrases can be strong and memorable.", 2, _cy_pick_from_bank(
        (
            'Long with a mix of upper/lower case, numbers and symbols',
            'Unique for each account — not reused across sites',
            'Not based on easily guessed personal information',
            'Uses a passphrase that is memorable but hard to guess',
        ),
        (
            'Short and easy to remember like a pet name',
            'The same password used for every online account',
            'Only lowercase letters with no numbers or symbols',
            'Written on a sticky note attached to the monitor',
        ),
        2,
        format_hint='Select two features of a strong password',
    )


def _cy_f6_social_engineering():
    q = "What is <strong>social engineering</strong>?"
    s = (
        "Manipulating people into <strong>breaking security rules</strong> — e.g. "
        "pretending to be IT support to get a password."
    )
    return q, s, "Targets human trust, not only technical flaws.", 2, _cy_mcq_graded_field(
        "Manipulating people into breaking security rules or revealing confidential information",
        [
            "Exploiting a software bug to gain administrator access to a server",
            "Encrypting data so it cannot be read without the decryption key",
            "Scanning network ports to find open services on a router",
        ],
    )


def _cy_f7_ransomware():
    q = "What does <strong>ransomware</strong> do?"
    s = (
        "Encrypts or locks files and <strong>demands payment</strong> for the decryption key "
        "or access restore."
    )
    return q, s, "Regular offline backups reduce impact.", 2, _cy_mcq_graded_field(
        "Encrypts or locks files and demands payment for the decryption key",
        [
            "Scans incoming email attachments for known virus signatures",
            "Monitors network traffic and blocks unauthorised connections",
            "Copies files to a backup server without the user's knowledge",
        ],
    )


def _cy_f8_physical_security():
    q = "Select <strong>two physical security</strong> measures for a school server room."
    s = (
        "Examples: <strong>locked door</strong>, CCTV, visitor log, cable locks, "
        "no unauthorised USB access."
    )
    return q, s, "Cyber security includes physical access control.", 2, _cy_pick_from_bank(
        (
            'Locked door to the server room',
            'CCTV monitoring the server room entrance',
            'Visitor log for everyone entering the room',
            'Cable locks securing equipment to desks',
            'Policy blocking unauthorised USB devices',
        ),
        (
            'Posting the admin password on the door for convenience',
            'Leaving the server room unlocked during the school day',
            'Allowing any pupil to plug in their own USB drive',
            'Disabling all software updates to avoid downtime',
        ),
        2,
        format_hint='Select two physical security measures',
    )


def _cy_f9_software_update():
    q = "Why are <strong>software updates and patches</strong> important for security?"
    s = (
        "They fix <strong>known vulnerabilities</strong> that attackers could exploit "
        "if the old version remains installed."
    )
    return q, s, "Zero-day = flaw not yet patched.", 2, _cy_mcq_graded_field(
        "They fix known vulnerabilities that attackers could exploit",
        [
            "They increase screen resolution and improve graphics performance",
            "They change keyboard layout settings for different languages",
            "They compress photos to save disk space on the hard drive",
        ],
    )


def _cy_f10_trojan():
    q = "How is a <strong>Trojan</strong> different from a virus?"
    s = (
        "A Trojan <strong>pretends to be legitimate software</strong> users install; "
        "it does not self-replicate like a virus spreading to other files/machines."
    )
    return q, s, "Named after the Trojan horse.", 2, _cy_mcq_graded_field(
        "It pretends to be legitimate software and does not self-replicate like a virus",
        [
            "It automatically copies itself to other files without user action",
            "It only spreads through email attachments containing macros",
            "It encrypts files and demands payment for the decryption key",
        ],
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cy_i1_dos():
    q = "What is a <strong>Denial of Service (DoS)</strong> attack?"
    s = (
        "Floods a server with traffic so <strong>legitimate users cannot access</strong> "
        "the service (website, game, etc.)."
    )
    return q, s, "DDoS uses many machines (botnet).", 2, _cy_mcq_graded_field(
        "Floods a server with traffic so legitimate users cannot access the service",
        [
            "Steals passwords by sending fake login emails",
            "Modifies database records without permission",
            "Secretly reads messages sent over an encrypted connection",
        ],
    )


def _cy_i2_brute_force():
    q = "What is a <strong>brute-force</strong> attack on a login page?"
    s = (
        "Automated trial of <strong>many password combinations</strong> until one works; "
        "slowed by lockouts, CAPTCHA, and strong passwords."
    )
    return q, s, "Rate limiting and 2FA defend against this.", 2, _cy_mcq_graded_field(
        "Automated trial of many password combinations until one works",
        [
            "Flooding a server with traffic so users cannot log in",
            "Tricking users into clicking a link in a fake email",
            "Encrypting files and demanding payment for the decryption key",
        ],
    )


def _cy_i3_2fa():
    q = "How does <strong>two-factor authentication (2FA)</strong> improve security?"
    s = (
        "Requires <strong>two different types</strong> of evidence — something you know (password) "
        "plus something you have (phone code) or are (fingerprint)."
    )
    return q, s, "Stolen password alone is not enough.", 2, _cy_mcq_graded_field(
        "Requires two different types of evidence (e.g. password plus phone code or fingerprint)",
        [
            "Uses two identical passwords entered one after the other",
            "Installs two separate firewalls on the same network",
            "Requires two different email addresses for one account",
        ],
    )


def _cy_i4_symmetric():
    q = "What is <strong>symmetric encryption</strong>? Give an example use."
    s = (
        "Same <strong>secret key</strong> encrypts and decrypts. Example: encrypting a "
        "file on a USB drive with a password."
    )
    return q, s, "Fast but key distribution must be secure.", 2, _cy_mcq_graded_field(
        "The same secret key encrypts and decrypts (e.g. a password-protected file on a USB drive)",
        [
            "A public key encrypts and a different private key decrypts",
            "One-way hashing that cannot be reversed to recover the original data",
            "Lossless compression that reduces file size without removing data",
        ],
    )


def _cy_i5_asymmetric():
    q = "What is <strong>asymmetric (public-key) encryption</strong>?"
    s = (
        "Uses a <strong>public key</strong> to encrypt and a <strong>private key</strong> "
        "to decrypt (or sign). Public key can be shared openly."
    )
    return q, s, "Used in HTTPS and secure email.", 3, _cy_mcq_graded_field(
        "Uses a public key to encrypt and a private key to decrypt (or sign)",
        [
            "Uses the same secret key to encrypt and decrypt every message",
            "Scrambles data in a way that cannot be decrypted by anyone",
            "Compresses files so they take less space on a hard drive",
        ],
    )


def _cy_i6_sql_injection():
    q = "What is <strong>SQL injection</strong>?"
    s = (
        "Entering malicious SQL in input fields to <strong>manipulate a database</strong> "
        "(e.g. bypass login or steal data)."
    )
    return q, s, "Prevent with parameterised queries and input validation.", 3, _cy_mcq_graded_field(
        "Entering malicious SQL in input fields to manipulate a database",
        [
            "Sending fake emails to trick users into revealing passwords",
            "Intercepting network traffic between a browser and a web server",
            "Encrypting database files so only the owner can read them",
        ],
    )


def _cy_i7_auth_vs_authz():
    q = (
        "Match each term to the correct description: "
        "<strong>authentication</strong> and <strong>authorisation</strong>."
    )
    s = (
        "<strong>Authentication</strong> — proving who you are (login). "
        "<strong>Authorisation</strong> — what you are allowed to access once logged in."
    )
    auth_correct = "Proving who you are (e.g. login)"
    authz_correct = "What you are allowed to access once logged in"
    auth_opts, auth_ans = _cy_mcq_match_field(
        auth_correct,
        [
            authz_correct,
            "Scrambling data so it cannot be read in transit",
        ],
    )
    authz_opts, authz_ans = _cy_mcq_match_field(
        authz_correct,
        [
            auth_correct,
            "Scanning files and memory for known malware",
        ],
    )
    return q, s, "AuthN = identity; AuthZ = permissions.", 2, graded_answer_number_fields(
        (auth_ans, authz_ans),
        ('Authentication', 'Authorisation'),
        field_types=('mcq', 'mcq'),
        field_options=(auth_opts, authz_opts),
    )


def _cy_i8_mitm():
    q = "What is a <strong>man-in-the-middle (MITM)</strong> attack?"
    s = (
        "Attacker <strong>secretly relays or alters</strong> communication between two parties "
        "who believe they talk directly."
    )
    return q, s, "HTTPS with valid certificates helps prevent this.", 3, _cy_mcq_graded_field(
        "Secretly relays or alters communication between two parties who believe they talk directly",
        [
            "Floods a server with traffic so legitimate users cannot access it",
            "Encrypts files and demands payment for the decryption key",
            "Scans files and memory for known malware signatures",
        ],
    )


def _cy_i9_acceptable_use():
    q = "Why do schools have an <strong>Acceptable Use Policy (AUP)</strong>?"
    s = (
        "Sets <strong>rules</strong> for using IT (no illegal content, no sharing passwords, "
        "respect copyright) and consequences for misuse."
    )
    return q, s, "Legal and safeguarding protection for school and pupils.", 2, _cy_mcq_graded_field(
        "Sets rules for using IT and consequences for misuse",
        [
            "Increases download speed for pupils using school Wi-Fi",
            "Replaces the need for antivirus software on school computers",
            "Encrypts all pupil data automatically without staff involvement",
        ],
    )


def _cy_i10_backup():
    q = (
        "Match each term to the correct description: "
        "<strong>full backup</strong> and <strong>incremental backup</strong>."
    )
    s = (
        "<strong>Full</strong> — copies everything each time (slow, simple restore). "
        "<strong>Incremental</strong> — only changes since last backup (faster, needs chain to restore)."
    )
    full_correct = "Copies everything each time (slow, simple restore)"
    incr_correct = "Only changes since the last backup (faster, needs chain to restore)"
    full_opts, full_ans = _cy_mcq_match_field(
        full_correct,
        [
            incr_correct,
            "Keeps one live copy and one archive copy on different media only",
        ],
    )
    incr_opts, incr_ans = _cy_mcq_match_field(
        incr_correct,
        [
            full_correct,
            "Encrypts files before uploading them to cloud storage",
        ],
    )
    return q, s, "3-2-1 rule: 3 copies, 2 media, 1 off-site.", 3, graded_answer_number_fields(
        (full_ans, incr_ans),
        ('Full backup', 'Incremental backup'),
        field_types=('mcq', 'mcq'),
        field_options=(full_opts, incr_opts),
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _cy_d1_pen_test():
    q = "What is <strong>penetration testing</strong> and why is it done legally?"
    s = (
        "Ethical experts simulate attacks to find <strong>weaknesses before criminals do</strong>; "
        "done with <strong>permission</strong> and a defined scope."
    )
    return q, s, "White-hat vs black-hat hackers.", 3, _cy_mcq_graded_field(
        "Ethical experts simulate attacks with permission to find weaknesses before criminals do",
        [
            "Hackers attack a system without permission to prove it is insecure",
            "Antivirus software scans files daily for known malware signatures",
            "Encrypting all data so attackers cannot read stolen files",
        ],
    )


def _cy_d2_gdpr_principle():
    q = "State <strong>two principles</strong> of UK GDPR relevant to schools holding pupil data."
    s = (
        "Examples: <strong>lawful basis</strong> for processing, <strong>data minimisation</strong>, "
        "<strong>security</strong>, <strong>right of access</strong>, limited retention."
    )
    return q, s, "ICO oversees data protection in the UK.", 3, _cy_pick_from_bank(
        (
            'Lawful basis for processing personal data',
            'Data minimisation — only collect what is needed',
            'Security — protect data from loss or unauthorised access',
            'Right of access — individuals can request their data',
            'Storage limitation — do not keep data longer than necessary',
        ),
        (
            'Maximum data collection — gather as much pupil data as possible',
            'Permanent retention — keep all records indefinitely',
            'Open sharing — publish pupil data publicly by default',
            'No consent required for any processing of pupil data',
        ),
        2,
        format_hint='Select two correct principles',
    )


def _cy_d3_xss():
    q = "What is <strong>cross-site scripting (XSS)</strong>?"
    s = (
        "Injecting malicious <strong>scripts into web pages</strong> viewed by others — "
        "can steal cookies or redirect users."
    )
    return q, s, "Sanitise user input and escape output.", 3, _cy_mcq_graded_field(
        "Injecting malicious scripts into web pages viewed by others",
        [
            "Entering malicious SQL in input fields to manipulate a database",
            "Flooding a server with traffic so users cannot access the website",
            "Encrypting all data stored in a database with a secret key",
        ],
    )


def _cy_d4_bio_vs_password():
    q = (
        "Select <strong>one advantage</strong> and <strong>one risk</strong> of using "
        "fingerprint biometrics instead of passwords alone."
    )
    s = (
        "<strong>Advantage:</strong> convenient, hard to guess. "
        "<strong>Risk:</strong> cannot change fingerprint if template is stolen; false accept/reject."
    )
    advantage_raw, advantage_bank, advantage_pick = _cy_pick_field(
        (
            'Convenient — no password to remember each time',
            'Hard to guess compared with a weak password',
            'Can be used as a second factor alongside a password',
        ),
        (
            'Completely impossible to spoof under any circumstances',
            'Never produces false accept or false reject errors',
            'Replaces the need for any other security measures',
        ),
        1,
    )
    risk_raw, risk_bank, risk_pick = _cy_pick_field(
        (
            'Cannot change your fingerprint if the template is stolen',
            'False accept or false reject errors can occur',
            'If compromised, you cannot reset it like a password',
        ),
        (
            'Fingerprints are always slower to use than typing a password',
            'Biometrics eliminate the need for encryption entirely',
            'Fingerprint readers never fail in normal use',
        ),
        1,
    )
    return q, s, "Often used as second factor, not sole factor.", 3, graded_answer_number_fields(
        (advantage_raw, risk_raw),
        ('Advantage', 'Risk'),
        field_types=('pick', 'pick'),
        field_options=(advantage_bank, risk_bank),
        field_pick_counts=(advantage_pick, risk_pick),
        row_sizes=(1, 1),
        group_labels=('Advantage', 'Risk'),
    )


def _cy_d5_incident_response():
    q = "A school discovers ransomware on a file server. List <strong>three immediate steps</strong> in incident response."
    s = (
        "<strong>Isolate</strong> affected systems (disconnect network), "
        "<strong>report</strong> to IT leadership/ICO if data breach, "
        "<strong>restore</strong> from clean backups — do not pay without advice."
    )
    return q, s, "Prepared incident plan reduces panic.", 4, proof_steps_answer(
        ('s1', 's2', 's3'),
        (
            {'id': 's1', 'text': 'Isolate affected systems (disconnect from the network)'},
            {'id': 's2', 'text': 'Report to IT leadership and assess whether data was breached'},
            {'id': 's3', 'text': 'Restore from clean backups'},
            {'id': 'd1', 'text': 'Pay the ransom immediately'},
            {'id': 'd2', 'text': 'Delete all pupil accounts'},
        ),
        order_matters=True,
        format_hint='Put the incident response steps in the correct order',
    )


def _cy_d6_cipher_caesar():
    q = "Caesar cipher shifts letters by 3. Encode <strong>CAT</strong>."
    s = "<strong>FDW</strong> (C→F, A→D, T→W)."
    return q, s, "Easy to break by brute force — not secure today.", 2, graded_answer_keyword('fdw')


def _cy_d7_https_role():
    q = "How does <strong>HTTPS</strong> protect data in transit (high level)?"
    s = (
        "Uses <strong>TLS</strong> to encrypt data between browser and server; "
        "certificate proves server identity; prevents casual eavesdropping."
    )
    return q, s, "Padlock icon; certificate authorities.", 3, _cy_mcq_graded_field(
        "Encrypts data in transit between browser and server using TLS",
        [
            "Compresses web pages so they download faster over slow connections",
            "Stores passwords in plain text on the server for faster login",
            "Blocks all cookies from being saved in the browser",
        ],
    )


def _cy_d8_insider_threat():
    q = "What is an <strong>insider threat</strong>?"
    s = (
        "Security risk from <strong>people inside the organisation</strong> — malicious staff, "
        "or careless actions (leaving laptop unlocked, emailing wrong attachment)."
    )
    return q, s, "Least privilege limits damage.", 3, _cy_mcq_graded_field(
        "Security risk from people inside the organisation (malicious or careless actions)",
        [
            "Attack launched only from outside the organisation over the internet",
            "Hardware fault that causes a server to crash unexpectedly",
            "Software bug that displays the wrong colour on a web page",
        ],
    )


def _cy_d9_mac_address_spoof():
    q = "Why is <strong>MAC address filtering</strong> alone weak security for WiFi?"
    s = (
        "MAC addresses can be <strong>spoofed</strong>; it does not encrypt traffic — "
        "strong WPA2/WPA3 and passwords matter more."
    )
    return q, s, "Defence in depth — multiple layers.", 3, _cy_mcq_graded_field(
        "MAC addresses can be spoofed and filtering does not encrypt traffic",
        [
            "MAC addresses are randomly generated every second so filters never match",
            "MAC filtering encrypts all WiFi traffic automatically",
            "MAC filtering prevents any device from connecting to the network",
        ],
    )


def _cy_d10_risk_assessment():
    q = (
        "In risk assessment, what do <strong>likelihood</strong> and <strong>impact</strong> "
        "help you decide?"
    )
    s = (
        "They prioritise which threats to fix first — "
        "<strong>high impact + high likelihood</strong> = greatest risk."
    )
    return q, s, "Risk = threat × vulnerability × asset value.", 3, _cy_mcq_graded_field(
        "Which threats to fix first — high impact and high likelihood mean greatest risk",
        [
            "Which hardware to buy based only on the purchase price",
            "How many staff to employ in the IT department each year",
            "Whether to use wired or wireless connections in an office",
        ],
    )


def _cy_d11_shoulder_surfing():
    q = (
        "A pupil watches a teacher type a password in the staff room. "
        "Name the attack type and select <strong>two defences</strong>."
    )
    s = (
        "<strong>Shoulder surfing</strong> (social/physical observation). "
        "Defences: shield the keyboard, use <strong>2FA</strong>, privacy screens, "
        "never share passwords, lock screen when away."
    )
    attack_opts, attack_ans = _cy_mcq_match_field(
        "Shoulder surfing",
        [
            "Phishing",
            "Denial of service (DoS)",
        ],
    )
    defence_raw, defence_bank, defence_pick = _cy_pick_field(
        (
            "Shield the keyboard when typing passwords",
            "Use two-factor authentication (2FA)",
            "Use a privacy screen on the monitor",
            "Lock the screen when stepping away",
            "Never share passwords with pupils or colleagues",
        ),
        (
            "Post the password on the staff room noticeboard for convenience",
            "Use the same short password for every account",
            "Disable the lock screen so login is faster",
        ),
        2,
    )
    return q, s, "Not all attacks are online — physical observation counts.", 3, graded_answer_number_fields(
        (attack_ans, defence_raw),
        ('Attack type', 'Defences'),
        field_types=('mcq', 'pick'),
        field_options=(attack_opts, defence_bank),
        field_pick_counts=(None, defence_pick),
        row_sizes=(1, 1),
        group_labels=('Attack type', 'Defences'),
    )


def _cy_d12_worm_vs_virus():
    q = "Compare a <strong>worm</strong> and a <strong>virus</strong> — how do they spread?"
    s = (
        "<strong>Virus:</strong> needs a host file/program and usually <strong>user action</strong> to run. "
        "<strong>Worm:</strong> self-replicates across a <strong>network</strong> without attaching to a host file."
    )
    return q, s, "Virus = attach + trigger; worm = spreads automatically.", 3, _cy_pick_from_bank(
        (
            'A virus usually needs user action (e.g. opening a file) before it can run',
            'A virus attaches to a host file or program',
            'A worm spreads automatically across a network',
            'A worm self-replicates without attaching to a host file',
        ),
        (
            'A worm must attach to a host file before it can spread',
            'A virus spreads across a network automatically without user action',
            'Viruses and worms spread in exactly the same way',
            'A worm only spreads when a user downloads and runs it manually',
        ),
        2,
        format_hint='Select two correct statements',
    )


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _cy_d13_multipart_attack_scenario():
    q = (
        "A company receives an email pretending to be from its bank, asking staff to click "
        "a link and \u201cconfirm\u201d their login details on a fake website.<br><br>"
        "<strong>a)</strong> Name this type of attack. [1]<br>"
        "<strong>b)</strong> This is an example of <strong>social engineering</strong>. "
        "Explain what social engineering means. [2]<br>"
        "<strong>c)</strong> Describe <strong>three</strong> measures the company could take "
        "to reduce the risk of this attack succeeding. [3]"
    )
    s = (
        "<strong>a)</strong> <strong>Phishing</strong>.<br><br>"
        "<strong>b)</strong> Social engineering means <strong>manipulating or tricking "
        "people</strong> into giving away confidential information or performing actions, "
        "rather than attacking the technology directly.<br><br>"
        "<strong>c)</strong> Any three: <strong>staff training</strong> to spot suspicious "
        "emails and check sender addresses; <strong>do not click unexpected links</strong> / "
        "verify with the bank directly; use <strong>two-factor authentication</strong> so a "
        "stolen password alone is not enough; <strong>email filtering / spam detection</strong> "
        "to block phishing emails."
    )
    attack_opts, attack_ans = _cy_mcq_match_field(
        "Phishing",
        [
            "Ransomware",
            "Denial of service (DoS)",
        ],
    )
    social_opts, social_ans = _cy_mcq_match_field(
        "Manipulating or tricking people into giving away confidential information",
        [
            "Exploiting a software bug to bypass a firewall",
            "Encrypting data so it cannot be read in transit",
        ],
    )
    measures_raw, measures_bank, measures_pick = _cy_pick_field(
        (
            "Staff training to spot suspicious emails and check sender addresses",
            "Do not click unexpected links — verify with the bank directly",
            "Use two-factor authentication so a stolen password alone is not enough",
            "Email filtering / spam detection to block phishing emails",
            "Keep antivirus software and systems updated",
            "Use a web filter to block known malicious sites",
        ),
        (
            "Disable all staff email accounts after one suspicious message",
            "Reply to the email with login details so IT can investigate",
            "Allow staff to use personal email for company bank access",
        ),
        3,
    )
    return q, s, "Fake email tricking users = phishing, a form of social engineering.", 6, graded_answer_number_fields(
        (attack_ans, social_ans, measures_raw),
        ('Attack type', 'Social engineering', 'Preventive measures'),
        field_types=('mcq', 'mcq', 'pick'),
        field_options=(attack_opts, social_opts, measures_bank),
        field_pick_counts=(None, None, measures_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


def _cy_d14_multipart_data_protection():
    q = (
        "An online retailer stores customers' names, addresses, and payment details.<br><br>"
        "<strong>a)</strong> Explain why <strong>encryption</strong> is used when storing or "
        "sending this data. [2]<br>"
        "<strong>b)</strong> Explain the difference between <strong>authentication</strong> "
        "and <strong>authorisation</strong>. [2]<br>"
        "<strong>c)</strong> The company performs <strong>penetration testing</strong>. "
        "State what this is and why it is useful. [2]"
    )
    s = (
        "<strong>a)</strong> Encryption <strong>scrambles the data</strong> so that if it is "
        "intercepted or stolen it cannot be read without the decryption key, protecting "
        "customers' private information.<br><br>"
        "<strong>b)</strong> <strong>Authentication</strong> proves <strong>who you are</strong> "
        "(e.g. username and password). <strong>Authorisation</strong> decides "
        "<strong>what you are allowed to do</strong> once your identity is confirmed (e.g. "
        "which records you can view).<br><br>"
        "<strong>c)</strong> Penetration testing is <strong>deliberately attacking a system "
        "(with permission)</strong> to find security weaknesses. It is useful because the "
        "company can <strong>fix the vulnerabilities before real attackers exploit "
        "them</strong>."
    )
    enc_opts, enc_ans = _cy_mcq_match_field(
        "Scrambles data so it cannot be read if intercepted or stolen without the key",
        [
            "Makes stored files smaller to save disk space",
            "Speeds up checkout by removing the need for passwords",
        ],
    )
    auth_raw, auth_bank, auth_pick = _cy_pick_field(
        (
            "Authentication proves who you are (e.g. username and password)",
            "Authorisation decides what you are allowed to do once logged in",
        ),
        (
            "Authentication decides what files and records a user can access",
            "Authorisation verifies identity using login credentials",
            "Authentication and authorisation mean the same thing",
            "Authorisation encrypts payment details before they are stored",
        ),
        2,
    )
    pent_opts, pent_ans = _cy_mcq_match_field(
        "Ethically attacking a system with permission to find weaknesses before criminals do",
        [
            "Scanning all employee laptops with antivirus software each morning",
            "Encrypting customer data without testing whether access controls work",
        ],
    )
    return q, s, "Encryption hides data; authentication = who, authorisation = what you can do.", 6, graded_answer_number_fields(
        (enc_ans, auth_raw, pent_ans),
        ('Encryption', 'Authentication vs authorisation', 'Penetration testing'),
        field_types=('mcq', 'pick', 'mcq'),
        field_options=(enc_opts, auth_bank, pent_opts),
        field_pick_counts=(None, auth_pick, None),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_CY_MCQ_BANK = [
    {"q": "Phishing attacks often use:",
     "opts": ["A  only hardware faults", "B  fake messages to steal credentials",
              "C  faster CPUs", "D  stronger encryption"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Fake messages</strong> trick users. Answer: B",
     "hint": "Social engineering online."},
    {"q": "A firewall’s main role is to:",
     "opts": ["A  increase screen resolution", "B  filter network traffic",
              "C  write programs", "D  compress photos"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Filter traffic</strong>. Answer: B",
     "hint": "Block/allow ports and addresses."},
    {"q": "Ransomware typically:",
     "opts": ["A  speeds up the CPU", "B  encrypts files and demands payment",
              "C  improves WiFi", "D  updates drivers"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Encrypt + ransom</strong>. Answer: B",
     "hint": "Backups are the best recovery."},
    {"q": "Two-factor authentication requires:",
     "opts": ["A  two passwords only", "B  two different types of evidence",
              "C  two firewalls", "D  two monitors"],
     "ans": "B", "marks": 2,
     "sol": "Different <strong>factor types</strong>. Answer: B",
     "hint": "Know + have/are."},
    {"q": "Symmetric encryption uses:",
     "opts": ["A  one shared secret key", "B  no keys at all",
              "C  only public keys", "D  only MAC addresses"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Same key</strong> both ways. Answer: A",
     "hint": "AES is symmetric."},
    {"q": "SQL injection targets:",
     "opts": ["A  printers", "B  databases via malicious input",
              "C  monitors", "D  power supplies"],
     "ans": "B", "marks": 2,
     "sol": "Exploits <strong>database queries</strong>. Answer: B",
     "hint": "Input validation prevents it."},
    {"q": "Authentication means:",
     "opts": ["A  what files you may open", "B  proving your identity",
              "C  encrypting a hard drive", "D  deleting cookies"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Prove identity</strong>. Answer: B",
     "hint": "Login step."},
    {"q": "A DoS attack aims to:",
     "opts": ["A  steal all passwords silently", "B  make a service unavailable",
              "C  improve latency", "D  install antivirus"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Deny service</strong> to users. Answer: B",
     "hint": "Overload server."},
    {"q": "Software patches mainly fix:",
     "opts": ["A  screen colour", "B  security vulnerabilities",
              "C  keyboard layout", "D  printer paper size"],
     "ans": "B", "marks": 1,
     "sol": "Close <strong>security holes</strong>. Answer: B",
     "hint": "Patch Tuesday."},
    {"q": "HTTPS protects data by:",
     "opts": ["A  deleting the website", "B  encrypting data in transit",
              "C  hiding the CPU", "D  removing DNS"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Encryption in transit</strong>. Answer: B",
     "hint": "TLS under the hood."},
    {"q": "A Trojan horse is malware that:",
     "opts": ["A  only affects printers", "B  disguises itself as legitimate software",
              "C  cannot be installed by users", "D  only runs on ROM"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Pretends to be safe</strong>. Answer: B",
     "hint": "User must run it."},
    {"q": "Penetration testing is carried out to:",
     "opts": ["A  damage systems without permission",
              "B  find weaknesses with permission before attackers do",
              "C  send spam email", "D  slow the internet"],
     "ans": "B", "marks": 2,
     "sol": "Ethical testing with <strong>permission</strong>. Answer: B",
     "hint": "White-hat security test."},
    {"q": "Social engineering relies on:",
     "opts": ["A  manipulating people", "B  faster Ethernet cables",
              "C  larger monitors", "D  binary arithmetic only"],
     "ans": "A", "marks": 1,
     "sol": "Targets <strong>human behaviour</strong>. Answer: A",
     "hint": "Not purely technical."},
    {"q": "Incremental backups store:",
     "opts": ["A  only files changed since last backup",
              "B  no data ever", "C  only the CPU", "D  only emails from 1990"],
     "ans": "A", "marks": 2,
     "sol": "Only <strong>changes</strong>. Answer: A",
     "hint": "Faster than full each time."},
    {"q": "Authorisation decides:",
     "opts": ["A  who you are", "B  what you are allowed to do after login",
              "C  your MAC address", "D  the weather"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Permissions</strong> after identity proved. Answer: B",
     "hint": "Role-based access."},
    {"q": "Shoulder surfing is:",
     "opts": ["A  watching someone enter credentials", "B  a type of firewall rule",
              "C  encrypting a hard drive", "D  a sorting algorithm"],
     "ans": "A", "marks": 1,
     "sol": "Observing <strong>secret entry</strong> physically. Answer: A",
     "hint": "Physical social engineering."},
    {"q": "Asymmetric encryption uses:",
     "opts": ["A  one shared secret key for everything",
              "B  a public key to encrypt and a private key to decrypt",
              "C  no keys", "D  only MAC addresses"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Public/private key pair</strong>. Answer: B",
     "hint": "RSA-style encryption."},
    {"q": "A virus is malware that:",
     "opts": ["A  only damages hardware physically", "B  attaches to programs and spreads when they run",
              "C  cannot copy itself", "D  only affects printers"],
     "ans": "B", "marks": 2,
     "sol": "Viruses <strong>replicate via infected files</strong>. Answer: B",
     "hint": "Needs a host program."},
    {"q": "A worm differs from a virus because a worm:",
     "opts": ["A  never uses a network", "B  can spread automatically without a host program",
              "C  only encrypts files for ransom", "D  cannot be detected"],
     "ans": "B", "marks": 2,
     "sol": "Worms <strong>self-propagate</strong> across networks. Answer: B",
     "hint": "No user needs to open an infected file."},
    {"q": "Biometric authentication uses:",
     "opts": ["A  something you know only", "B  something you are (e.g. fingerprint)",
              "C  a shared secret key", "D  a firewall rule"],
     "ans": "B", "marks": 2,
     "sol": "Biometrics = <strong>physical characteristics</strong>. Answer: B",
     "hint": "One factor type in 2FA."},
    {"q": "A strong password policy should include:",
     "opts": ["A  using one password for every account", "B  minimum length and mix of character types",
              "C  sharing passwords with friends", "D  writing passwords on public noticeboards"],
     "ans": "B", "marks": 1,
     "sol": "Length and complexity make guessing <strong>harder</strong>. Answer: B",
     "hint": "Combine letters, numbers and symbols."},
    {"q": "A full backup compared with incremental backup:",
     "opts": ["A  copies all selected data each time", "B  only copies changes since last backup",
              "C  never uses storage", "D  deletes the original files"],
     "ans": "A", "marks": 2,
     "sol": "Full backup copies <strong>everything in scope</strong>. Answer: A",
     "hint": "Incremental is faster but needs the chain of backups."},
]


def cyber_security_mcq():
    item = random.choice(_CY_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _cy_f1_malware_virus, _cy_f2_phishing, _cy_f3_firewall, _cy_f4_antivirus,
    _cy_f5_strong_password, _cy_f6_social_engineering, _cy_f7_ransomware,
    _cy_f8_physical_security, _cy_f9_software_update, _cy_f10_trojan,
]

_INTERMEDIATE = [
    _cy_i1_dos, _cy_i2_brute_force, _cy_i3_2fa, _cy_i4_symmetric,
    _cy_i5_asymmetric, _cy_i6_sql_injection, _cy_i7_auth_vs_authz,
    _cy_i8_mitm, _cy_i9_acceptable_use, _cy_i10_backup,
]

_DIFFICULT = [
    _cy_d1_pen_test, _cy_d2_gdpr_principle, _cy_d3_xss,
    _cy_d4_bio_vs_password, _cy_d5_incident_response, _cy_d6_cipher_caesar,
    _cy_d7_https_role, _cy_d8_insider_threat, _cy_d9_mac_address_spoof,
    _cy_d10_risk_assessment, _cy_d11_shoulder_surfing, _cy_d12_worm_vs_virus,
    _cy_d13_multipart_attack_scenario, _cy_d14_multipart_data_protection,
]


def gcse_cyber_security_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return [cyber_security_mcq] * 10

    pools = {
        "foundational": _FOUNDATIONAL,
        "intermediate": _INTERMEDIATE,
        "difficult": _DIFFICULT,
    }
    if difficulty not in pools:
        return random.sample(_FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT, 10)

    pool = pools[difficulty]
    return random.sample(pool, len(pool))


def gcse_cyber_security(difficulty, mode, variant_name=None):
    if mode == "mcq":
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = cyber_security_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "cyber_security",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_cyber_security_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _cy_problem_from_output(variant(), difficulty)
