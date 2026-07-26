"""
GCSE Computer Science – Ethical, Legal & Environmental Impacts
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
Graded definition variants add a 5th text/keyword payload (Phase 4).
List/multipart variants stay as 4-tuples.
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


def _eth_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'cs', 'ethical',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        extra = problem_extra_from_graded_answer(raw)
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'ethical', **extra
    )


def _eth_mcq_match_field(correct_text, distractors):
    """Shuffled 3-option inline MCQ for term–description matching."""
    pool = [correct_text] + list(distractors[:2])
    random.shuffle(pool)
    letters = 'ABC'
    return pool, letters[pool.index(correct_text)]


def _eth_mcq_payload(correct_text, distractors):
    """Four-option practice MCQ; returns payload for _eth_problem_from_output."""
    pool = [correct_text] + list(distractors[:3])
    random.shuffle(pool)
    letters = 'ABCD'
    correct_letter = letters[pool.index(correct_text)]
    options = [f'{letters[i]}  {pool[i]}' for i in range(len(pool))]
    return {'type': 'mcq', 'options': options, 'correct': correct_letter}


def _eth_pick_from_bank(correct_texts, distractor_texts, pick_count, *, format_hint=None):
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


def _eth_select_all_from_bank(correct_texts, distractor_texts, *, format_hint=None):
    """Shuffled bank: select every correct statement (any order)."""
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    return proof_steps_answer(
        correct_ids,
        bank,
        order_matters=False,
        format_hint=format_hint or 'Select all correct impact-and-issue pairs',
    )


def _eth_pick_field(correct_texts, distractor_texts, pick_count):
    """Inline pick-N field for ``number_fields`` (returns raw, bank, count)."""
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    raw = f"pick|{pick_count}|{'|'.join(correct_ids)}"
    return raw, bank, pick_count


def _eth_select_all_field(correct_texts, distractor_texts):
    """Inline select-all field for ``number_fields`` (returns raw, bank)."""
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    raw = f"0|{'|'.join(correct_ids)}"
    return raw, bank


def _eth_order_field(steps, distractors):
    """Inline ordered steps field for ``number_fields`` (returns raw, bank)."""
    step_ids = tuple(f's{i + 1}' for i in range(len(steps)))
    bank = [{'id': sid, 'text': text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    raw = f"1|{'|'.join(step_ids)}"
    return raw, bank


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _eth_f1_environmental():
    q = "Give <strong>two environmental impacts</strong> of digital technology."
    s = (
        "Examples: <strong>energy consumption</strong> (data centres, charging devices), "
        "<strong>e-waste</strong> from discarded hardware, <strong>manufacturing pollution</strong>, "
        "mining rare earth metals, <strong>carbon footprint</strong> of device lifecycles."
    )
    return q, s, "Think manufacture → use → disposal.", 2, graded_answer_text(
        'energy', 'waste', 'pollution', 'mining', 'carbon', required=2,
    )


def _eth_f2_gdpr():
    q = "What is <strong>UK GDPR</strong> mainly designed to protect?"
    s = (
        "<strong>Personal data</strong> — how organisations collect, store, use and share "
        "information that can identify living individuals."
    )
    return q, s, "Replaces much of the old Data Protection Act for EU/UK law.", 1, graded_answer_text('personal', 'data')


def _eth_f3_copyright():
    q = "What does the <strong>Copyright, Designs and Patents Act 1988</strong> protect?"
    s = (
        "Original <strong>creative work</strong> (software, music, images, text) so the owner "
        "controls copying and distribution; copying without permission can be illegal."
    )
    return q, s, "© symbol = copyright.", 2, _eth_mcq_payload(
        "Original creative work such as software, music, images and text",
        [
            "Personal data about living individuals only",
            "Hardware devices and computer components",
            "Network traffic between computers on the internet",
        ],
    )


def _eth_f4_cma():
    q = "What is the <strong>Computer Misuse Act 1990</strong>?"
    s = (
        "UK law making it illegal to <strong>access or modify computer systems/data without "
        "authorisation</strong> — e.g. hacking, spreading viruses, denial-of-service attacks."
    )
    return q, s, "Unauthorised access = offence.", 2, graded_answer_text('unauthorised', 'access')


def _eth_f5_open_source():
    q = "What is <strong>open-source software</strong>?"
    s = (
        "Software whose <strong>source code is publicly available</strong> to view, modify and "
        "redistribute under a licence (e.g. GNU GPL), often free of charge."
    )
    return q, s, "Opposite of closed proprietary code.", 2, _eth_mcq_payload(
        "Software whose source code is publicly available to view, modify and redistribute",
        [
            "Software sold under a licence that hides the source code from users",
            "Software that runs only in a web browser without being installed",
            "Software that automatically updates without the user's permission",
        ],
    )


def _eth_f6_proprietary():
    q = "What is <strong>proprietary software</strong>?"
    s = (
        "Commercial software where the <strong>source code is not shared</strong>; users buy a "
        "<strong>licence</strong> to use it under strict terms (e.g. Microsoft Office)."
    )
    return q, s, "You buy permission to use, not ownership of the code.", 2, graded_answer_text('source code', 'licence')


def _eth_f7_digital_divide():
    q = "What is the <strong>digital divide</strong>?"
    s = (
        "The gap between those who <strong>have access</strong> to digital technology, skills and "
        "connectivity and those who <strong>do not</strong> (often due to income, location, age, disability)."
    )
    return q, s, "Unequal access to tech and the internet.", 2, graded_answer_text('access', 'divide')


def _eth_f8_e_waste():
    q = "What is <strong>e-waste</strong>?"
    s = (
        "Discarded electrical and electronic equipment (phones, PCs, servers). "
        "Toxic materials can harm the environment if not <strong>recycled responsibly</strong>."
    )
    return q, s, "Old kit sent to landfill or export.", 1, graded_answer_text('discarded', 'electronic')


def _eth_f9_consent():
    q = "Why is <strong>consent</strong> important when collecting personal data?"
    s = (
        "People should <strong>know and agree</strong> to what data is collected and how it is used; "
        "collecting without a lawful basis or clear consent can breach data protection law."
    )
    return q, s, "Tick boxes and privacy policies.", 2, graded_answer_text('consent', 'agree')


def _eth_f10_ethical_vs_legal():
    q = (
        "What is the difference between an <strong>ethical</strong> issue and a "
        "<strong>legal</strong> issue? Match each type to the correct description."
    )
    s = (
        "<strong>Legal</strong> — breaks a law (court, fines, prison). "
        "<strong>Ethical</strong> — about right and wrong/morals; may be legal but still considered unfair "
        "(e.g. selling data in a way users dislike but law allows)."
    )
    ethical_correct = (
        "About right and wrong / morals — may be legal but still considered unfair"
    )
    legal_correct = "Breaks a law — can lead to court action, fines or prison"
    ethical_opts, ethical_ans = _eth_mcq_match_field(
        ethical_correct,
        [
            legal_correct,
            "Always the same as breaking the law",
        ],
    )
    legal_opts, legal_ans = _eth_mcq_match_field(
        legal_correct,
        [
            ethical_correct,
            "Only about whether a product looks professional",
        ],
    )
    return q, s, "Legal ≠ always ethical.", 2, graded_answer_number_fields(
        (ethical_ans, legal_ans),
        ('Ethical', 'Legal'),
        field_types=('mcq', 'mcq'),
        field_options=(ethical_opts, legal_opts),
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _eth_i1_gdpr_principles():
    q = "Name <strong>three principles</strong> organisations must follow under data protection law."
    s = (
        "Examples: <strong>lawful basis</strong> for processing, <strong>purpose limitation</strong>, "
        "<strong>data minimisation</strong>, <strong>accuracy</strong>, <strong>storage limitation</strong>, "
        "<strong>security</strong>, <strong>accountability</strong>."
    )
    return q, s, "GDPR uses principles, not a single checklist in exams.", 3, _eth_pick_from_bank(
        (
            'Lawful basis for processing personal data',
            'Purpose limitation — use data only for stated purposes',
            'Data minimisation — only collect what is needed',
            'Accuracy — keep personal data correct and up to date',
            'Storage limitation — do not keep data longer than necessary',
            'Security — protect data from loss or unauthorised access',
            'Accountability — organisations must demonstrate compliance',
        ),
        (
            'Maximum data collection — gather as much data as possible',
            'Permanent retention — keep all records indefinitely',
            'Open sharing — publish personal data publicly by default',
            'No consent required for any processing of personal data',
        ),
        3,
        format_hint='Select three correct principles',
    )


def _eth_i2_cma_offences():
    q = "Give <strong>two offences</strong> under the Computer Misuse Act."
    s = (
        "Examples: <strong>unauthorised access</strong> to computer material; "
        "<strong>unauthorised access with intent to commit further offences</strong>; "
        "<strong>unauthorised modification</strong> of computer material (e.g. viruses, ransomware)."
    )
    return q, s, "Hacking and malware distribution.", 3, _eth_pick_from_bank(
        (
            'Unauthorised access to computer material',
            'Unauthorised access with intent to commit further offences',
            'Unauthorised modification of computer material (e.g. viruses, ransomware)',
        ),
        (
            'Copying a copyrighted image into coursework without permission',
            'Collecting personal data without a lawful basis under GDPR',
            'Installing security patches on school computers with IT permission',
            'Sharing open-source software under the terms of its licence',
        ),
        2,
        format_hint='Select two correct offences',
    )


def _eth_i3_copyright_example():
    q = "A student copies a paid image from Google into their coursework without credit. Which law is relevant?"
    s = (
        "<strong>Copyright, Designs and Patents Act 1988</strong> — the image is likely protected; "
        "copying without permission or a valid licence can infringe copyright. "
        "Use royalty-free assets or create your own."
    )
    return q, s, "© applies to photos and code too.", 2, _eth_mcq_payload(
        "Copyright, Designs and Patents Act 1988",
        [
            "Computer Misuse Act 1990",
            "Data Protection Act 2018",
            "Fraud Act 2006",
        ],
    )


def _eth_i4_planned_obsolescence():
    q = (
        "Explain <strong>planned obsolescence</strong> and one environmental concern. "
        "Match each part to the correct description."
    )
    s = (
        "Products designed to <strong>become outdated or fail</strong> quickly so consumers buy replacements. "
        "Increases <strong>e-waste</strong> and manufacturing energy use."
    )
    definition_correct = (
        "Products designed to become outdated or fail quickly so consumers buy replacements"
    )
    environmental_correct = "Increases e-waste and manufacturing energy use"
    definition_opts, definition_ans = _eth_mcq_match_field(
        definition_correct,
        [
            "Products built to last as long as possible to reduce consumer waste",
            "Software that receives free security updates for the lifetime of the device",
        ],
    )
    environmental_opts, environmental_ans = _eth_mcq_match_field(
        environmental_correct,
        [
            "Reduces e-waste because devices are replaced less often",
            "Eliminates energy use in manufacturing because fewer devices are made",
        ],
    )
    return q, s, "Short replacement cycles.", 2, graded_answer_number_fields(
        (definition_ans, environmental_ans),
        ('Planned obsolescence', 'Environmental concern'),
        field_types=('mcq', 'mcq'),
        field_options=(definition_opts, environmental_opts),
    )


def _eth_i5_cloud_privacy():
    q = "Give <strong>one benefit</strong> and <strong>one risk</strong> of cloud storage for a school."
    s = (
        "<strong>Benefit:</strong> access files anywhere, easy backup, scalable storage. "
        "<strong>Risk:</strong> data held on third-party servers — <strong>privacy</strong>, "
        "jurisdiction (where data is stored), provider breach or outage."
    )
    return q, s, "AQA often uses cloud in 3.8 scenarios.", 3, graded_answer_number_fields(
        ('access', 'privacy'),
        ('Benefit', 'Risk'),
        field_types=('keyword', 'keyword'),
        format_hint='Enter your answer',
    )


def _eth_i6_surveillance():
    q = (
        "Describe <strong>one ethical argument for</strong> and <strong>one against</strong> "
        "CCTV in schools. Select one argument for and one argument against."
    )
    s = (
        "<strong>For:</strong> deters crime, protects pupils/staff, evidence after incidents. "
        "<strong>Against:</strong> constant monitoring feels intrusive; privacy concerns; "
        "who watches the footage and how long it is kept."
    )
    for_raw, for_bank, for_pick = _eth_pick_field(
        (
            'Deters crime and vandalism on school premises',
            'Protects pupils and staff from harm',
            'Provides evidence after incidents',
        ),
        (
            'Eliminates all privacy concerns for pupils and staff',
            'Allows anyone to watch live footage online without restriction',
            'Removes the need for any staff supervision on site',
        ),
        1,
    )
    against_raw, against_bank, against_pick = _eth_pick_field(
        (
            'Constant monitoring can feel intrusive to pupils and staff',
            'Raises privacy concerns about who is being watched',
            'Questions about who watches footage and how long it is kept',
            'Pupils may feel they are not trusted',
        ),
        (
            'CCTV always prevents every crime with no ethical downsides',
            'Surveillance guarantees perfect behaviour from all pupils',
            'Footage is never stored so privacy concerns do not apply',
        ),
        1,
    )
    return q, s, "Balance safety vs privacy.", 3, graded_answer_number_fields(
        (for_raw, against_raw),
        ('Argument for', 'Argument against'),
        field_types=('pick', 'pick'),
        field_options=(for_bank, against_bank),
        field_pick_counts=(for_pick, against_pick),
        row_sizes=(1, 1),
        group_labels=('Argument for', 'Argument against'),
    )


def _eth_i7_ai_bias():
    q = (
        "What is <strong>algorithmic bias</strong>? Give an example.<br><br>"
        "<strong>a)</strong> Explain what algorithmic bias means.<br>"
        "<strong>b)</strong> Select one valid example."
    )
    s = (
        "When a computer system produces <strong>unfair outcomes</strong> because training data or rules "
        "favour one group. Example: facial recognition less accurate on some skin tones; "
        "hiring AI trained on biased past decisions."
    )
    example_raw, example_bank, example_pick = _eth_pick_field(
        (
            'Facial recognition less accurate on some skin tones',
            'Hiring AI trained on biased past decisions',
            'A loan system trained on past data that favours one group unfairly',
        ),
        (
            'Antivirus software detecting malware on a student laptop',
            'A firewall blocking unauthorised access to the school network',
            'Encryption protecting passwords sent over the internet',
        ),
        1,
    )
    return q, s, "Edexcel mentions bias explicitly.", 3, graded_answer_number_fields(
        ('unfair|bias|discrimination', example_raw),
        ('Definition', 'Example'),
        field_types=('text', 'pick'),
        field_options=(None, example_bank),
        field_pick_counts=(None, example_pick),
        row_sizes=(1, 1),
        group_labels=('(a)', '(b)'),
        inline_sections=True,
    )


def _eth_i8_autonomous_vehicles():
    q = "Give <strong>one ethical issue</strong> with autonomous (self-driving) vehicles."
    s = (
        "Examples: <strong>who is liable</strong> in a crash (manufacturer, owner, software); "
        "<strong>trolley problem</strong> style choices programmed into AI; job losses for drivers; "
        "safety vs adoption speed."
    )
    return q, s, "AQA lists autonomous vehicles in 3.8.", 3, graded_answer_text(
        'liable', 'crash', 'trolley', 'jobs', 'safety', required=1,
    )


def _eth_i9_patent_trademark():
    q = (
        "What is the difference between a <strong>patent</strong> and a <strong>trademark</strong>? "
        "Match each type to the correct description."
    )
    s = (
        "<strong>Patent</strong> — protects a <strong>new invention</strong> (how something works) for a limited time. "
        "<strong>Trademark</strong> — protects <strong>brand identity</strong> (names, logos, slogans) from confusion."
    )
    patent_correct = "Protects a new invention (how something works) for a limited time"
    trademark_correct = "Protects brand identity (names, logos, slogans) from confusion"
    patent_opts, patent_ans = _eth_mcq_match_field(
        patent_correct,
        [
            trademark_correct,
            "Protects original creative work such as music, images and text",
        ],
    )
    trademark_opts, trademark_ans = _eth_mcq_match_field(
        trademark_correct,
        [
            patent_correct,
            "Protects personal data about living individuals under UK law",
        ],
    )
    return q, s, "Edexcel 5.2.3 covers IP types.", 2, graded_answer_number_fields(
        (patent_ans, trademark_ans),
        ('Patent', 'Trademark'),
        field_types=('mcq', 'mcq'),
        field_options=(patent_opts, trademark_opts),
    )


def _eth_i10_ico_role():
    q = "What is the role of the <strong>ICO</strong> (Information Commissioner's Office)?"
    s = (
        "UK regulator for <strong>data protection</strong>; investigates breaches, gives guidance, "
        "can issue fines for serious GDPR/DPA failures."
    )
    return q, s, "ICO enforces UK data law.", 2, graded_answer_text('data protection', 'regulator')


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _eth_d1_privacy_debate():
    q = (
        "Explain the <strong>privacy debate</strong> between citizens and government/security services. "
        "Select one point citizens value and one point governments argue."
    )
    s = (
        "<strong>Citizens</strong> value privacy and may oppose mass surveillance or excessive data access. "
        "<strong>Governments</strong> argue access to communications/data is needed to prevent terrorism "
        "and serious crime. Exams want <strong>balanced arguments</strong>, not one-sided rants."
    )
    citizens_raw, citizens_bank, citizens_pick = _eth_pick_field(
        (
            'Value privacy and personal freedom',
            'May oppose mass surveillance of communications',
            'May oppose excessive government access to personal data',
            'Want limits on how security services collect data',
        ),
        (
            'Want unlimited government access to all private communications',
            'Believe privacy should never be protected online',
            'Support mass surveillance without any independent oversight',
        ),
        1,
    )
    governments_raw, governments_bank, governments_pick = _eth_pick_field(
        (
            'Access to communications and data is needed to prevent terrorism',
            'Access to data is needed to investigate serious crime',
            'Surveillance can help protect national security',
        ),
        (
            'Citizens should have no privacy rights online',
            'Data access is mainly needed to improve advertising revenue',
            'Monitoring communications is never justified for any reason',
        ),
        1,
    )
    return q, s, "AQA 3.8 additional information.", 4, graded_answer_number_fields(
        (citizens_raw, governments_raw),
        ('Citizens value', 'Governments argue'),
        field_types=('pick', 'pick'),
        field_options=(citizens_bank, governments_bank),
        field_pick_counts=(citizens_pick, governments_pick),
        row_sizes=(1, 1),
        group_labels=('Citizens value', 'Governments argue'),
    )


def _eth_d2_wearable_implant():
    q = (
        "A health app on a smartwatch shares heart data with advertisers without clear opt-in. "
        "Identify impacts. Select all correct impact-and-issue pairs."
    )
    s = (
        "<strong>Legal:</strong> possible UK GDPR breach (consent, purpose, data minimisation). "
        "<strong>Ethical:</strong> trust broken, sensitive health data exploited. "
        "<strong>Environmental:</strong> device manufacture/disposal (wearable tech). "
        "AQA/OCR: link issue type to evidence in the scenario."
    )
    return q, s, "Wearables = AQA 3.8 exam context.", 4, _eth_select_all_from_bank(
        (
            'Legal — possible UK GDPR breach (consent, purpose, data minimisation)',
            'Ethical — trust broken when sensitive health data is shared without clear opt-in',
            'Ethical — sensitive health data exploited for advertising',
            'Environmental — environmental impact from wearable device manufacture and disposal',
        ),
        (
            'Legal — improved battery life from continuous heart-rate monitoring',
            'Cultural — echo chambers created by personalised social media feeds',
            'Environmental — heart data encrypted so privacy is fully protected',
            'Ethical — advertisers pay more when ads are accurately targeted',
        ),
    )


def _eth_d3_cma_vs_ethical_hack():
    q = "How is <strong>penetration testing</strong> different from an offence under the Computer Misuse Act?"
    s = (
        "Pen testing is <strong>authorised</strong> security testing with permission and scope. "
        "CMA offences involve <strong>unauthorised</strong> access or modification — same tools, "
        "different legality."
    )
    return q, s, "Permission is the key difference.", 3, graded_answer_text('authorised', 'unauthorised')


def _eth_d4_energy_datacentre():
    q = "Why do <strong>data centres</strong> raise environmental concerns?"
    s = (
        "They run <strong>24/7 servers</strong> needing huge electricity (often for cooling); "
        "carbon depends on power source; drives demand for hardware and water use in some regions."
    )
    return q, s, "Cloud = many data centres.", 3, graded_answer_text('electricity', 'cooling')


def _eth_d5_job_automation():
    q = (
        "Discuss <strong>one positive</strong> and <strong>one negative</strong> impact of automation "
        "on employment. Select one positive impact and one negative impact."
    )
    s = (
        "<strong>Positive:</strong> dangerous/repetitive jobs automated; new roles in tech maintenance. "
        "<strong>Negative:</strong> unemployment or reskilling pressure for drivers, warehouse staff, etc.; "
        "inequality if benefits go to owners not workers."
    )
    positive_raw, positive_bank, positive_pick = _eth_pick_field(
        (
            'Dangerous or repetitive jobs can be automated',
            'New roles created in tech maintenance and robotics',
            'Workers freed from hazardous manual tasks',
        ),
        (
            'All jobs disappear permanently with no new roles created',
            'Automation has no effect on any type of employment',
            'Every worker immediately receives equal shares of automation profits',
        ),
        1,
    )
    negative_raw, negative_bank, negative_pick = _eth_pick_field(
        (
            'Unemployment or reskilling pressure for drivers, warehouse staff, etc.',
            'Inequality if benefits go to owners not workers',
            'Job losses in industries replaced by automation',
        ),
        (
            'Every displaced worker instantly finds a better-paid job',
            'Automation always creates more jobs than it removes with no downsides',
            'Workers never need to retrain when their role is automated',
        ),
        1,
    )
    return q, s, "Ethical + cultural impact.", 4, graded_answer_number_fields(
        (positive_raw, negative_raw),
        ('Positive impact', 'Negative impact'),
        field_types=('pick', 'pick'),
        field_options=(positive_bank, negative_bank),
        field_pick_counts=(positive_pick, negative_pick),
        row_sizes=(1, 1),
        group_labels=('Positive impact', 'Negative impact'),
    )


def _eth_d6_licence_compare():
    q = (
        "Compare <strong>open-source</strong> and <strong>proprietary</strong> licensing "
        "for a school choosing software. Select all correct statements about each type."
    )
    s = (
        "<strong>Open source:</strong> often no licence fee, can modify, community support; "
        "may need technical staff. <strong>Proprietary:</strong> polished support contract, "
        "clear legal terms; per-seat cost, cannot legally change source, vendor lock-in risk."
    )
    os_raw, os_bank = _eth_select_all_field(
        (
            'Often no licence fee',
            'Source code can be modified',
            'Community support available',
            'May need technical staff to maintain and support',
        ),
        (
            'Per-seat licensing cost for each user',
            'Cannot legally change the source code',
            'Vendor lock-in risk if the product is discontinued',
            'Polished commercial support contract included',
        ),
    )
    prop_raw, prop_bank = _eth_select_all_field(
        (
            'Polished commercial support contract',
            'Clear legal terms in the licence agreement',
            'Per-seat licensing cost',
            'Cannot legally change the source code',
            'Vendor lock-in risk',
        ),
        (
            'Often no licence fee',
            'Source code can be modified freely',
            'Community support instead of a paid contract',
            'May need in-house technical staff to maintain',
        ),
    )
    return q, s, "Cost, freedom, support.", 4, graded_answer_number_fields(
        (os_raw, prop_raw),
        ('Open source', 'Proprietary'),
        field_types=('pick', 'pick'),
        field_options=(os_bank, prop_bank),
        field_pick_counts=(None, None),
        row_sizes=(1, 1),
        group_labels=('Open source', 'Proprietary'),
    )


def _eth_d7_breach_response():
    q = (
        "A school leaks pupil email addresses due to a mis-sent spreadsheet. "
        "Outline <strong>legal and ethical</strong> steps."
    )
    s = (
        "<strong>Legal:</strong> contain breach, assess risk, notify ICO within 72 hours if required, "
        "inform affected individuals, document actions (UK GDPR). "
        "<strong>Ethical:</strong> apologise, support affected pupils, review staff training and access controls."
    )
    legal_raw, legal_bank = _eth_order_field(
        (
            'Contain the breach',
            'Assess the risk to affected individuals',
            'Notify the ICO within 72 hours if required',
            'Inform affected individuals',
            'Document actions taken (UK GDPR)',
        ),
        (
            'Delete all pupil email accounts immediately',
            'Publish the leaked spreadsheet online for transparency',
            'Ignore the incident because only email addresses were involved',
        ),
    )
    ethical_raw, ethical_bank = _eth_order_field(
        (
            'Apologise to those affected',
            'Support affected pupils',
            'Review staff training and access controls',
        ),
        (
            'Blame the pupils whose data was leaked',
            'Refuse to tell parents or pupils about the incident',
        ),
    )
    return q, s, "Serious personal data breach.", 4, graded_answer_number_fields(
        (legal_raw, ethical_raw),
        ('Legal steps', 'Ethical steps'),
        field_types=('order', 'order'),
        field_options=(legal_bank, ethical_bank),
        row_sizes=(1, 1),
        group_labels=('Legal steps', 'Ethical steps'),
    )


def _eth_d8_implant_ethics():
    q = (
        "What ethical issues arise with <strong>computer-based implants</strong> (e.g. medical chips)? "
        "Select one ethical issue."
    )
    s = (
        "Examples: <strong>privacy</strong> of body data; <strong>security</strong> if hacked; "
        "who owns the data; <strong>consent</strong> for updates; inequality if only wealthy can afford; "
        "safety if software fails."
    )
    return q, s, "AQA 3.8 lists implants.", 3, _eth_pick_from_bank(
        (
            'Privacy of sensitive body data collected by the implant',
            'Security risk if the implant is hacked',
            'Questions about who owns the data from the implant',
            'Consent needed for software updates to the implant',
            'Inequality if only wealthy people can afford implants',
            'Safety concerns if implant software fails',
        ),
        (
            'Improved battery life for smartphones',
            'Faster download speeds on home Wi-Fi networks',
            'Reduced cost of open-source software licences',
            'Environmental impact from data centre cooling alone',
        ),
        1,
        format_hint='Select one ethical issue',
    )


def _eth_d9_exam_structure():
    q = (
        "A 6-mark question asks about <strong>environmental impacts of smartphones</strong>. "
        "Put the steps for structuring your answer in the correct order."
    )
    s = (
        "Brief intro → <strong>several distinct points</strong> (mining, manufacture energy, daily charging, "
        "short upgrade cycle/e-waste, recycling) → optional <strong>mitigation</strong> (repair, longer use, "
        "recycling schemes). Use spec terms; stay on environmental, not legal unless asked."
    )
    return q, s, "Point + explain + example.", 3, proof_steps_answer(
        ('s1', 's2', 's3'),
        (
            {'id': 's1', 'text': 'Brief intro to the question'},
            {
                'id': 's2',
                'text': (
                    'Several distinct environmental points '
                    '(e.g. mining, manufacture energy, daily charging, e-waste, recycling)'
                ),
            },
            {
                'id': 's3',
                'text': 'Optional mitigation (e.g. repair, longer use, recycling schemes)',
            },
            {'id': 'd1', 'text': 'Discuss legal impacts and GDPR compliance first'},
            {'id': 'd2', 'text': 'Start with mitigation before explaining the environmental impacts'},
            {'id': 'd3', 'text': 'Focus on ethical privacy issues from smartphone tracking'},
            {'id': 'd4', 'text': 'Write a long conclusion without any body points'},
        ),
        order_matters=True,
        format_hint='Put the answer structure in the correct order',
    )


def _eth_d10_mixed_scenario():
    q = (
        "A social media app tracks location, sells data to third parties, and uses "
        "<strong>biased</strong> feeds. Name <strong>three impact types</strong> and one issue each. "
        "Select three correct impact-and-issue pairs."
    )
    s = (
        "<strong>Legal:</strong> GDPR — consent, purpose limitation, ICO oversight. "
        "<strong>Ethical:</strong> manipulation, bias, loss of privacy. "
        "<strong>Cultural:</strong> echo chambers, mental health concerns. "
        "<strong>Environmental:</strong> (weaker here) energy of servers — accept if explained."
    )
    return q, s, "Classify impacts clearly.", 4, _eth_pick_from_bank(
        (
            'Legal — consent issues when selling data to third parties (GDPR)',
            'Legal — purpose limitation breached when data is shared beyond what users agreed',
            'Ethical — manipulation through biased feeds',
            'Ethical — loss of privacy from location tracking',
            'Cultural — echo chambers from personalised feeds',
            'Cultural — mental health concerns linked to social media use',
            'Environmental — energy consumption of servers hosting the service',
        ),
        (
            'Legal — echo chambers affecting what users see in their feed',
            'Ethical — ICO oversight of how organisations handle personal data',
            'Cultural — GDPR requires all messages to be encrypted by default',
            'Environmental — loss of privacy from tracking user location',
            'Legal — increased carbon footprint from data centre energy use',
        ),
        3,
        format_hint='Select three correct impact-and-issue pairs',
    )


def _eth_d11_right_to_erasure():
    q = (
        "Under UK GDPR, what is the <strong>right to erasure</strong> and when might a school "
        "still keep some pupil data?<br><br>"
        "<strong>a)</strong> Select the best description of the right to erasure.<br>"
        "<strong>b)</strong> Select all valid reasons a school might still retain pupil data."
    )
    s = (
        "Individuals can request <strong>deletion</strong> of personal data in certain cases. "
        "Schools may retain records where there is a <strong>legal obligation</strong> "
        "(safeguarding, exam records) or legitimate archival need — but must justify retention."
    )
    definition_raw, definition_bank, definition_pick = _eth_pick_field(
        (
            'Individuals can request deletion of personal data in certain cases',
            'The right to have personal data erased when conditions in UK GDPR are met',
        ),
        (
            'The right to access all personal data held about you',
            'The right to copy personal data to another service (data portability)',
            'Schools must delete all pupil data immediately on any request with no exceptions',
            'The right to share personal data with any third party without consent',
        ),
        1,
    )
    retention_raw, retention_bank = _eth_select_all_field(
        (
            'Legal obligation to keep certain records',
            'Safeguarding records must be retained',
            'Exam records may need to be kept',
            'Legitimate archival need with justified retention',
        ),
        (
            'Schools can keep all pupil data indefinitely without any justification',
            'Marketing preferences must always be retained forever',
            'Data must be deleted even when the law requires keeping safeguarding records',
            'Pupils have no rights over their personal data once it is stored',
        ),
    )
    return q, s, "Erasure is not absolute when law requires keeping records.", 3, graded_answer_number_fields(
        (definition_raw, retention_raw),
        ('Right to erasure', 'Reasons to retain data'),
        field_types=('pick', 'pick'),
        field_options=(definition_bank, retention_bank),
        field_pick_counts=(definition_pick, None),
        row_sizes=(1, 1),
        group_labels=('(a)', '(b)'),
        inline_sections=True,
    )


def _eth_d12_creative_commons():
    q = (
        "A student finds an image online with a <strong>Creative Commons</strong> licence. "
        "What should they check before using it in coursework?"
    )
    s = (
        "Read the <strong>licence terms</strong> (attribution required? non-commercial only? "
        "no derivatives?). Credit the <strong>creator</strong>, respect share-alike rules, "
        "and do not assume ‘free on the internet’ means unrestricted use."
    )
    return q, s, "Licences define what reuse is allowed.", 3, graded_answer_text('licence', 'attribution')


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _eth_d13_multipart_smartphone_lifecycle():
    q = (
        "A technology company releases a new smartphone every year and encourages customers "
        "to upgrade frequently.<br><br>"
        "<strong>a)</strong> Describe one <strong>environmental</strong> impact of "
        "manufacturing so many new phones. [2]<br>"
        "<strong>b)</strong> Describe one <strong>environmental</strong> problem caused when "
        "old phones are thrown away. [2]<br>"
        "<strong>c)</strong> Suggest <strong>two</strong> ways the impact could be reduced. "
        "Select two correct options. [2]"
    )
    s = (
        "<strong>a)</strong> Manufacturing uses <strong>raw materials</strong> (including "
        "rare-earth metals that must be mined) and large amounts of <strong>energy</strong>, "
        "causing pollution and carbon emissions.<br><br>"
        "<strong>b)</strong> Discarded phones become <strong>e-waste</strong>; they may end "
        "up in landfill where <strong>toxic substances</strong> (e.g. lead, lithium) can "
        "leak and harm the environment.<br><br>"
        "<strong>c)</strong> Any two: <strong>recycle</strong> old devices to recover "
        "materials; <strong>repair / reuse</strong> phones to extend their life; design "
        "phones to be <strong>more easily upgraded</strong> so they last longer; trade-in "
        "schemes."
    )
    measures_raw, measures_bank, measures_pick = _eth_pick_field(
        (
            'Recycle old devices to recover materials',
            'Repair or reuse phones to extend their life',
            'Design phones to be more easily upgraded so they last longer',
            'Trade-in schemes to return old devices',
        ),
        (
            'Encourage customers to upgrade every year',
            'Throw old phones in general waste without recycling',
            'Increase manufacturing speed to release more models each year',
            'Use more rare-earth metals in every new phone model',
        ),
        2,
    )
    return q, s, "Think mining + energy (make), toxic landfill (dispose), recycle/repair (reduce).", 6, graded_answer_number_fields(
        (
            '2@raw|material|mining|energy|pollution|carbon|rare',
            '2@e-waste|landfill|toxic|leak|lithium|lead|waste',
            measures_raw,
        ),
        ('Manufacturing impact', 'Disposal problem', 'Ways to reduce impact'),
        field_types=('text', 'text', 'pick'),
        field_options=(None, None, measures_bank),
        field_pick_counts=(None, None, measures_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


def _eth_d14_multipart_legislation():
    q = (
        "A person gains access to a company's computer system without permission and copies "
        "customer data.<br><br>"
        "<strong>a)</strong> Name the law that makes <strong>unauthorised access</strong> to "
        "computer systems illegal. [1]<br>"
        "<strong>b)</strong> Name the law that protects how the company must store and use "
        "<strong>customers' personal data</strong>. [1]<br>"
        "<strong>c)</strong> Explain the difference between something being "
        "<strong>illegal</strong> and something being <strong>unethical</strong>. "
        "Select one description of each."
    )
    s = (
        "<strong>a)</strong> The <strong>Computer Misuse Act (1990)</strong>.<br><br>"
        "<strong>b)</strong> The <strong>Data Protection Act (2018) / UK GDPR</strong>.<br><br>"
        "<strong>c)</strong> <strong>Illegal</strong> means it breaks the law and can lead "
        "to prosecution; <strong>unethical</strong> means it is morally wrong but may not "
        "break any law. For example, hacking the system in this scenario is "
        "<strong>illegal</strong>. By contrast, a company selling customers' browsing habits "
        "to advertisers after they technically agreed in a long terms-and-conditions "
        "document may be <strong>legal but widely seen as unethical</strong>."
    )
    access_opts, access_ans = _eth_mcq_match_field(
        "Computer Misuse Act 1990",
        [
            "Copyright, Designs and Patents Act 1988",
            "Fraud Act 2006",
        ],
    )
    data_opts, data_ans = _eth_mcq_match_field(
        "Data Protection Act 2018 (UK GDPR)",
        [
            "Computer Misuse Act 1990",
            "Copyright, Designs and Patents Act 1988",
        ],
    )
    illegal_raw, illegal_bank, illegal_pick = _eth_pick_field(
        (
            'Breaks the law and can lead to prosecution or fines',
            'Unauthorised access to copy customer data in this scenario is illegal',
            'Violates a statute such as the Computer Misuse Act',
        ),
        (
            'Morally wrong but may not break any law',
            'Legal but widely seen as unfair to customers',
            'Always the same as being unethical',
        ),
        1,
    )
    unethical_raw, unethical_bank, unethical_pick = _eth_pick_field(
        (
            'Morally wrong but may not break any law',
            'Legal but widely seen as unfair (e.g. selling browsing habits after buried consent)',
            'Breaks trust even when technically permitted by law',
        ),
        (
            'Breaks the law and can lead to prosecution or fines',
            'Unauthorised access under the Computer Misuse Act',
            'Always illegal whenever it feels unfair',
        ),
        1,
    )
    return q, s, "Computer Misuse Act = access; Data Protection Act = personal data; legal ≠ ethical.", 6, graded_answer_number_fields(
        (access_ans, data_ans, illegal_raw, unethical_raw),
        ('Unauthorised access law', 'Personal data law', 'Illegal', 'Unethical'),
        field_types=('mcq', 'mcq', 'pick', 'pick'),
        field_options=(access_opts, data_opts, illegal_bank, unethical_bank),
        field_pick_counts=(None, None, illegal_pick, unethical_pick),
        row_sizes=(1, 1, 1, 1),
        group_labels=('(a)', '(b)', '(c) Illegal', '(c) Unethical'),
        inline_sections=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_ETH_MCQ_BANK = [
    {"q": "UK GDPR mainly regulates:",
     "opts": ["A  CPU speed", "B  Personal data processing",
              "C  Monitor brightness", "D  Keyboard layout"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Personal data</strong> law. Answer: B",
     "hint": "Not hardware specs."},
    {"q": "The Computer Misuse Act targets:",
     "opts": ["A  Unauthorised access to computer systems",
              "B  Slow internet speeds", "C  Printing homework",
              "D  Buying legitimate software"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Unauthorised access/modification</strong>. Answer: A",
     "hint": "Hacking without permission."},
    {"q": "Copyright law protects:",
     "opts": ["A  Only paper books", "B  Original creative work such as software and images",
              "C  The colour blue", "D  RAM chips only"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Creative works</strong>. Answer: B",
     "hint": "CDPA 1988."},
    {"q": "Open-source software:",
     "opts": ["A  Never has a licence", "B  Allows access to source code under a licence",
              "C  Cannot be modified", "D  Is always illegal"],
     "ans": "B", "marks": 2,
     "sol": "Source available under <strong>licence terms</strong>. Answer: B",
     "hint": "GPL is an example."},
    {"q": "The digital divide refers to:",
     "opts": ["A  A type of firewall", "B  Unequal access to technology and skills",
              "C  A binary number", "D  A CPU register"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Inequality of access</strong>. Answer: B",
     "hint": "Rural vs urban, rich vs poor."},
    {"q": "E-waste is best described as:",
     "opts": ["A  Deleted emails", "B  Discarded electronic equipment",
              "C  Encrypted files", "D  Empty USB boxes only"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Discarded electronics</strong>. Answer: B",
     "hint": "Phones in landfill."},
    {"q": "Planned obsolescence means:",
     "opts": ["A  Products designed to last forever",
              "B  Products designed to become outdated or fail sooner to drive new sales",
              "C  Free software updates", "D  Recycling laws"],
     "ans": "B", "marks": 2,
     "sol": "Drives <strong>replacement cycles</strong>. Answer: B",
     "hint": "Environmental concern."},
    {"q": "A patent protects:",
     "opts": ["A  A brand logo only", "B  A new invention for a limited time",
              "C  Personal passwords", "D  WiFi passwords"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Inventions</strong>, not logos. Answer: B",
     "hint": "Trademark = brand."},
    {"q": "Algorithmic bias occurs when:",
     "opts": ["A  Algorithms always are fair",
              "B  Systems produce unfair outcomes due to flawed data or rules",
              "C  CPUs run faster", "D  Screens use less power"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Unfair automated decisions</strong>. Answer: B",
     "hint": "Training data matters."},
    {"q": "The ICO is responsible for:",
     "opts": ["A  Enforcing UK data protection law",
              "B  Designing CPUs", "C  Writing Python", "D  Patents only"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Data protection regulator</strong>. Answer: A",
     "hint": "Information Commissioner's Office."},
    {"q": "Storing school files in the cloud mainly risks:",
     "opts": ["A  No internet ever needed",
              "B  Data held by a third party — privacy and security depend on the provider",
              "C  Files become physical paper", "D  GDPR no longer applies"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Third-party storage</strong> risks. Answer: B",
     "hint": "Where is data stored?"},
    {"q": "An ethical issue differs from a legal issue because:",
     "opts": ["A  Ethics is always illegal",
              "B  Something can be legal but still considered morally wrong",
              "C  Laws never apply to technology", "D  Ethics only applies to animals"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Legal ≠ ethical</strong>. Answer: B",
     "hint": "Think fairness vs law."},
    {"q": "Penetration testing is legal when:",
     "opts": ["A  Done without telling anyone",
              "B  Done with explicit permission and agreed scope",
              "C  Done only by criminals", "D  Done on any network at random"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Authorised</strong> testing. Answer: B",
     "hint": "Contrast with CMA."},
    {"q": "Autonomous vehicles raise ethical questions about:",
     "opts": ["A  Monitor size only",
              "B  Liability and programmed decision-making in crashes",
              "C  Keyboard layout", "D  ASCII codes"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Who is responsible</strong> in accidents. Answer: B",
     "hint": "AQA 3.8 context."},
    {"q": "Proprietary software licences typically:",
     "opts": ["A  Give full source code to everyone",
              "B  Restrict copying/modifying source; users buy permission to use",
              "C  Ban all updates", "D  Remove copyright"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Limited use rights</strong>. Answer: B",
     "hint": "Closed source."},
    {"q": "The Freedom of Information Act allows:",
     "opts": ["A  anyone to request information held by public bodies",
              "B  companies to ignore GDPR", "C  unlimited copying of films",
              "D  hacking government servers"],
     "ans": "A", "marks": 2,
     "sol": "Access to <strong>public authority</strong> information. Answer: A",
     "hint": "Transparency law — not a hacking licence."},
    {"q": "Large data centres raise environmental concerns because they:",
     "opts": ["A  use significant electricity for servers and cooling",
              "B  eliminate all e-waste", "C  never need backup power",
              "D  remove the need for networks"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Energy and cooling</strong> demands. Answer: A",
     "hint": "Cloud still runs on physical machines."},
    {"q": "Personal data under UK GDPR includes:",
     "opts": ["A  only CPU serial numbers", "B  information that can identify a living person",
              "C  public domain software code only", "D  monitor refresh rates"],
     "ans": "B", "marks": 2,
     "sol": "Data relating to an <strong>identifiable individual</strong>. Answer: B",
     "hint": "Names, emails, photos can count."},
    {"q": "A software licence for proprietary programs usually:",
     "opts": ["A  lets anyone change and redistribute the source code freely",
              "B  restricts how the software may be copied or modified",
              "C  removes all copyright protection", "D  bans all updates"],
     "ans": "B", "marks": 2,
     "sol": "Users get <strong>limited rights</strong> under licence. Answer: B",
     "hint": "Contrast with open-source licences."},
    {"q": "Online tracking cookies can raise privacy concerns because they:",
     "opts": ["A  speed up the CPU", "B  may store browsing behaviour without clear consent",
              "C  encrypt all personal data automatically", "D  replace the need for passwords"],
     "ans": "B", "marks": 2,
     "sol": "Behaviour may be recorded <strong>without users realising</strong>. Answer: B",
     "hint": "GDPR requires lawful basis and transparency."},
    {"q": "Recycling electronic devices helps reduce:",
     "opts": ["A  network latency", "B  harmful materials entering landfill and resource waste",
              "C  the need for encryption", "D  software bugs"],
     "ans": "B", "marks": 1,
     "sol": "Recycling recovers materials and cuts <strong>e-waste harm</strong>. Answer: B",
     "hint": "Phones contain rare metals and toxins."},
    {"q": "AI used in hiring decisions may be unethical if:",
     "opts": ["A  it always uses more electricity", "B  it discriminates unfairly against some groups",
              "C  it runs on a GUI", "D  it stores data in tables"],
     "ans": "B", "marks": 2,
     "sol": "Biased training data can cause <strong>unfair outcomes</strong>. Answer: B",
     "hint": "Links to algorithmic bias."},
]


def ethical_mcq():
    item = random.choice(_ETH_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _eth_f1_environmental, _eth_f2_gdpr, _eth_f3_copyright, _eth_f4_cma,
    _eth_f5_open_source, _eth_f6_proprietary, _eth_f7_digital_divide,
    _eth_f8_e_waste, _eth_f9_consent, _eth_f10_ethical_vs_legal,
]

_INTERMEDIATE = [
    _eth_i1_gdpr_principles, _eth_i2_cma_offences, _eth_i3_copyright_example,
    _eth_i4_planned_obsolescence, _eth_i5_cloud_privacy, _eth_i6_surveillance,
    _eth_i7_ai_bias, _eth_i8_autonomous_vehicles, _eth_i9_patent_trademark,
    _eth_i10_ico_role,
]

_DIFFICULT = [
    _eth_d1_privacy_debate, _eth_d2_wearable_implant, _eth_d3_cma_vs_ethical_hack,
    _eth_d4_energy_datacentre, _eth_d5_job_automation, _eth_d6_licence_compare,
    _eth_d7_breach_response, _eth_d8_implant_ethics, _eth_d9_exam_structure,
    _eth_d10_mixed_scenario, _eth_d11_right_to_erasure, _eth_d12_creative_commons,
    _eth_d13_multipart_smartphone_lifecycle, _eth_d14_multipart_legislation,
]


def gcse_ethical_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return [ethical_mcq] * 10

    pools = {
        "foundational": _FOUNDATIONAL,
        "intermediate": _INTERMEDIATE,
        "difficult": _DIFFICULT,
    }
    if difficulty not in pools:
        return random.sample(_FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT, 10)

    pool = pools[difficulty]
    return random.sample(pool, len(pool))


def gcse_ethical(difficulty, mode, variant_name=None):
    if mode == "mcq":
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = ethical_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "ethical",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_ethical_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _eth_problem_from_output(variant(), difficulty)
