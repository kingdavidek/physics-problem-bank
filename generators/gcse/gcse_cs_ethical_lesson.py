"""
GCSE Computer Science – Ethical, Legal & Environmental Impacts
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import pick_named_variant


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
    return q, s, "Think manufacture → use → disposal.", 2


def _eth_f2_gdpr():
    q = "What is <strong>UK GDPR</strong> mainly designed to protect?"
    s = (
        "<strong>Personal data</strong> — how organisations collect, store, use and share "
        "information that can identify living individuals."
    )
    return q, s, "Replaces much of the old Data Protection Act for EU/UK law.", 1


def _eth_f3_copyright():
    q = "What does the <strong>Copyright, Designs and Patents Act 1988</strong> protect?"
    s = (
        "Original <strong>creative work</strong> (software, music, images, text) so the owner "
        "controls copying and distribution; copying without permission can be illegal."
    )
    return q, s, "© symbol = copyright.", 2


def _eth_f4_cma():
    q = "What is the <strong>Computer Misuse Act 1990</strong>?"
    s = (
        "UK law making it illegal to <strong>access or modify computer systems/data without "
        "authorisation</strong> — e.g. hacking, spreading viruses, denial-of-service attacks."
    )
    return q, s, "Unauthorised access = offence.", 2


def _eth_f5_open_source():
    q = "What is <strong>open-source software</strong>?"
    s = (
        "Software whose <strong>source code is publicly available</strong> to view, modify and "
        "redistribute under a licence (e.g. GNU GPL), often free of charge."
    )
    return q, s, "Opposite of closed proprietary code.", 2


def _eth_f6_proprietary():
    q = "What is <strong>proprietary software</strong>?"
    s = (
        "Commercial software where the <strong>source code is not shared</strong>; users buy a "
        "<strong>licence</strong> to use it under strict terms (e.g. Microsoft Office)."
    )
    return q, s, "You buy permission to use, not ownership of the code.", 2


def _eth_f7_digital_divide():
    q = "What is the <strong>digital divide</strong>?"
    s = (
        "The gap between those who <strong>have access</strong> to digital technology, skills and "
        "connectivity and those who <strong>do not</strong> (often due to income, location, age, disability)."
    )
    return q, s, "Unequal access to tech and the internet.", 2


def _eth_f8_e_waste():
    q = "What is <strong>e-waste</strong>?"
    s = (
        "Discarded electrical and electronic equipment (phones, PCs, servers). "
        "Toxic materials can harm the environment if not <strong>recycled responsibly</strong>."
    )
    return q, s, "Old kit sent to landfill or export.", 1


def _eth_f9_consent():
    q = "Why is <strong>consent</strong> important when collecting personal data?"
    s = (
        "People should <strong>know and agree</strong> to what data is collected and how it is used; "
        "collecting without a lawful basis or clear consent can breach data protection law."
    )
    return q, s, "Tick boxes and privacy policies.", 2


def _eth_f10_ethical_vs_legal():
    q = "What is the difference between an <strong>ethical</strong> issue and a <strong>legal</strong> issue?"
    s = (
        "<strong>Legal</strong> — breaks a law (court, fines, prison). "
        "<strong>Ethical</strong> — about right and wrong/morals; may be legal but still considered unfair "
        "(e.g. selling data in a way users dislike but law allows)."
    )
    return q, s, "Legal ≠ always ethical.", 2


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
    return q, s, "GDPR uses principles, not a single checklist in exams.", 3


def _eth_i2_cma_offences():
    q = "Give <strong>two offences</strong> under the Computer Misuse Act."
    s = (
        "Examples: <strong>unauthorised access</strong> to computer material; "
        "<strong>unauthorised access with intent to commit further offences</strong>; "
        "<strong>unauthorised modification</strong> of computer material (e.g. viruses, ransomware)."
    )
    return q, s, "Hacking and malware distribution.", 3


def _eth_i3_copyright_example():
    q = "A student copies a paid image from Google into their coursework without credit. Which law is relevant?"
    s = (
        "<strong>Copyright, Designs and Patents Act 1988</strong> — the image is likely protected; "
        "copying without permission or a valid licence can infringe copyright. "
        "Use royalty-free assets or create your own."
    )
    return q, s, "© applies to photos and code too.", 2


def _eth_i4_planned_obsolescence():
    q = "Explain <strong>planned obsolescence</strong> and one environmental concern."
    s = (
        "Products designed to <strong>become outdated or fail</strong> quickly so consumers buy replacements. "
        "Increases <strong>e-waste</strong> and manufacturing energy use."
    )
    return q, s, "Short replacement cycles.", 2


def _eth_i5_cloud_privacy():
    q = "Give <strong>one benefit</strong> and <strong>one risk</strong> of cloud storage for a school."
    s = (
        "<strong>Benefit:</strong> access files anywhere, easy backup, scalable storage. "
        "<strong>Risk:</strong> data held on third-party servers — <strong>privacy</strong>, "
        "jurisdiction (where data is stored), provider breach or outage."
    )
    return q, s, "AQA often uses cloud in 3.8 scenarios.", 3


def _eth_i6_surveillance():
    q = "Describe <strong>one ethical argument for</strong> and <strong>one against</strong> CCTV in schools."
    s = (
        "<strong>For:</strong> deters crime, protects pupils/staff, evidence after incidents. "
        "<strong>Against:</strong> constant monitoring feels intrusive; privacy concerns; "
        "who watches the footage and how long it is kept."
    )
    return q, s, "Balance safety vs privacy.", 3


def _eth_i7_ai_bias():
    q = "What is <strong>algorithmic bias</strong>? Give an example."
    s = (
        "When a computer system produces <strong>unfair outcomes</strong> because training data or rules "
        "favour one group. Example: facial recognition less accurate on some skin tones; "
        "hiring AI trained on biased past decisions."
    )
    return q, s, "Edexcel mentions bias explicitly.", 3


def _eth_i8_autonomous_vehicles():
    q = "Give <strong>one ethical issue</strong> with autonomous (self-driving) vehicles."
    s = (
        "Examples: <strong>who is liable</strong> in a crash (manufacturer, owner, software); "
        "<strong>trolley problem</strong> style choices programmed into AI; job losses for drivers; "
        "safety vs adoption speed."
    )
    return q, s, "AQA lists autonomous vehicles in 3.8.", 3


def _eth_i9_patent_trademark():
    q = "What is the difference between a <strong>patent</strong> and a <strong>trademark</strong>?"
    s = (
        "<strong>Patent</strong> — protects a <strong>new invention</strong> (how something works) for a limited time. "
        "<strong>Trademark</strong> — protects <strong>brand identity</strong> (names, logos, slogans) from confusion."
    )
    return q, s, "Edexcel 5.2.3 covers IP types.", 2


def _eth_i10_ico_role():
    q = "What is the role of the <strong>ICO</strong> (Information Commissioner's Office)?"
    s = (
        "UK regulator for <strong>data protection</strong>; investigates breaches, gives guidance, "
        "can issue fines for serious GDPR/DPA failures."
    )
    return q, s, "ICO enforces UK data law.", 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _eth_d1_privacy_debate():
    q = "Explain the <strong>privacy debate</strong> between citizens and government/security services."
    s = (
        "<strong>Citizens</strong> value privacy and may oppose mass surveillance or excessive data access. "
        "<strong>Governments</strong> argue access to communications/data is needed to prevent terrorism "
        "and serious crime. Exams want <strong>balanced arguments</strong>, not one-sided rants."
    )
    return q, s, "AQA 3.8 additional information.", 4


def _eth_d2_wearable_implant():
    q = "A health app on a smartwatch shares heart data with advertisers without clear opt-in. Identify impacts."
    s = (
        "<strong>Legal:</strong> possible UK GDPR breach (consent, purpose, data minimisation). "
        "<strong>Ethical:</strong> trust broken, sensitive health data exploited. "
        "<strong>Environmental:</strong> device manufacture/disposal (wearable tech). "
        "AQA/OCR: link issue type to evidence in the scenario."
    )
    return q, s, "Wearables = AQA 3.8 exam context.", 4


def _eth_d3_cma_vs_ethical_hack():
    q = "How is <strong>penetration testing</strong> different from an offence under the Computer Misuse Act?"
    s = (
        "Pen testing is <strong>authorised</strong> security testing with permission and scope. "
        "CMA offences involve <strong>unauthorised</strong> access or modification — same tools, "
        "different legality."
    )
    return q, s, "Permission is the key difference.", 3


def _eth_d4_energy_datacentre():
    q = "Why do <strong>data centres</strong> raise environmental concerns?"
    s = (
        "They run <strong>24/7 servers</strong> needing huge electricity (often for cooling); "
        "carbon depends on power source; drives demand for hardware and water use in some regions."
    )
    return q, s, "Cloud = many data centres.", 3


def _eth_d5_job_automation():
    q = "Discuss <strong>one positive</strong> and <strong>one negative</strong> impact of automation on employment."
    s = (
        "<strong>Positive:</strong> dangerous/repetitive jobs automated; new roles in tech maintenance. "
        "<strong>Negative:</strong> unemployment or reskilling pressure for drivers, warehouse staff, etc.; "
        "inequality if benefits go to owners not workers."
    )
    return q, s, "Ethical + cultural impact.", 4


def _eth_d6_licence_compare():
    q = "Compare <strong>open-source</strong> and <strong>proprietary</strong> licensing for a school choosing software."
    s = (
        "<strong>Open source:</strong> often no licence fee, can modify, community support; "
        "may need technical staff. <strong>Proprietary:</strong> polished support contract, "
        "clear legal terms; per-seat cost, cannot legally change source, vendor lock-in risk."
    )
    return q, s, "Cost, freedom, support.", 4


def _eth_d7_breach_response():
    q = "A school leaks pupil email addresses due to a mis-sent spreadsheet. Outline <strong>legal and ethical</strong> steps."
    s = (
        "<strong>Legal:</strong> contain breach, assess risk, notify ICO within 72 hours if required, "
        "inform affected individuals, document actions (UK GDPR). "
        "<strong>Ethical:</strong> apologise, support affected pupils, review staff training and access controls."
    )
    return q, s, "Serious personal data breach.", 4


def _eth_d8_implant_ethics():
    q = "What ethical issues arise with <strong>computer-based implants</strong> (e.g. medical chips)?"
    s = (
        "Examples: <strong>privacy</strong> of body data; <strong>security</strong> if hacked; "
        "who owns the data; <strong>consent</strong> for updates; inequality if only wealthy can afford; "
        "safety if software fails."
    )
    return q, s, "AQA 3.8 lists implants.", 3


def _eth_d9_exam_structure():
    q = "A 6-mark question asks about <strong>environmental impacts of smartphones</strong>. How should you structure your answer?"
    s = (
        "Brief intro → <strong>several distinct points</strong> (mining, manufacture energy, daily charging, "
        "short upgrade cycle/e-waste, recycling) → optional <strong>mitigation</strong> (repair, longer use, "
        "recycling schemes). Use spec terms; stay on environmental, not legal unless asked."
    )
    return q, s, "Point + explain + example.", 3


def _eth_d10_mixed_scenario():
    q = (
        "A social media app tracks location, sells data to third parties, and uses "
        "<strong>biased</strong> feeds. Name <strong>three impact types</strong> and one issue each."
    )
    s = (
        "<strong>Legal:</strong> GDPR — consent, purpose limitation, ICO oversight. "
        "<strong>Ethical:</strong> manipulation, bias, loss of privacy. "
        "<strong>Cultural:</strong> echo chambers, mental health concerns. "
        "<strong>Environmental:</strong> (weaker here) energy of servers — accept if explained."
    )
    return q, s, "Classify impacts clearly.", 4


def _eth_d11_right_to_erasure():
    q = (
        "Under UK GDPR, what is the <strong>right to erasure</strong> and when might a school "
        "still keep some pupil data?"
    )
    s = (
        "Individuals can request <strong>deletion</strong> of personal data in certain cases. "
        "Schools may retain records where there is a <strong>legal obligation</strong> "
        "(safeguarding, exam records) or legitimate archival need — but must justify retention."
    )
    return q, s, "Erasure is not absolute when law requires keeping records.", 3


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
    return q, s, "Licences define what reuse is allowed.", 3


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _eth_d13_multipart_smartphone_lifecycle():
    q = (
        "A technology company releases a new smartphone every year and encourages customers "
        "to upgrade frequently.<br><br>"
        "<strong>a)</strong> Describe one <strong>environmental</strong> impact of "
        "manufacturing so many new phones. [2]<br>"
        "<strong>b)</strong> Describe one <strong>environmental</strong> problem caused when "
        "old phones are thrown away. [2]<br>"
        "<strong>c)</strong> Suggest <strong>two</strong> ways the impact could be reduced. [2]"
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
    return q, s, "Think mining + energy (make), toxic landfill (dispose), recycle/repair (reduce).", 6


def _eth_d14_multipart_legislation():
    q = (
        "A person gains access to a company's computer system without permission and copies "
        "customer data.<br><br>"
        "<strong>a)</strong> Name the law that makes <strong>unauthorised access</strong> to "
        "computer systems illegal. [1]<br>"
        "<strong>b)</strong> Name the law that protects how the company must store and use "
        "<strong>customers' personal data</strong>. [1]<br>"
        "<strong>c)</strong> Explain the difference between something being "
        "<strong>illegal</strong> and something being <strong>unethical</strong>, using an "
        "example. [4]"
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
    return q, s, "Computer Misuse Act = access; Data Protection Act = personal data; legal ≠ ethical.", 6


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

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "cs", "ethical",
    )
