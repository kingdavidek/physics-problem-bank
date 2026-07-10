#Radioactivity file - Combined science Edexcel future file


import random
import math
from generators.shared.utils import make_problem


# =========================================================
# EDEXCEL GCSE COMBINED SCIENCE: RADIOACTIVITY
# 10 foundational + 10 intermediate + 10 difficult variants
# =========================================================


# ---------------------------
# FOUNDATIONAL (10 variants)
# ---------------------------

def rad_found_atom_structure():
    q = (
        r"A student is describing the structure of an atom."
        r"<br><br>"
        r"<strong>a)</strong> State the relative charges of a proton, neutron and electron."
        r"<br>"
        r"<strong>b)</strong> State where each of these particles is found in the atom."
    )
    s = (
        r"<strong>a)</strong> Proton: <strong>+1</strong>, neutron: <strong>0</strong>, electron: <strong>-1</strong>."
        r"<br><br>"
        r"<strong>b)</strong> Protons and neutrons are found in the <strong>nucleus</strong>. "
        r"Electrons are found in shells / energy levels <strong>around the nucleus</strong>."
    )
    hint = r"Remember: nucleus = protons + neutrons; electrons are outside the nucleus."
    return q, s, hint, 2


def rad_found_isotope_definition():
    element = random.choice(["carbon", "uranium", "iodine", "cobalt"])
    q = (
        rf"What is meant by the term <strong>isotope</strong>?"
        rf"<br><br>"
        rf"Use {element} as an example in your explanation."
    )
    s = (
        r"Isotopes are atoms of the <strong>same element</strong> that have the <strong>same number of protons</strong> "
        r"but a <strong>different number of neutrons</strong>."
        r"<br><br>"
        rf"So isotopes of {element} all have the same proton number, but different neutron numbers."
    )
    hint = r"Same element means same proton number. The thing that changes is the number of neutrons."
    return q, s, hint, 2


def rad_found_identify_radiation():
    data = random.choice([
        ("stopped by paper", "alpha"),
        ("stopped by thin aluminium", "beta"),
        ("greatly reduced by thick lead or concrete", "gamma"),
    ])
    prop, ans = data
    q = (
        rf"A type of nuclear radiation is described as being <strong>{prop}</strong>."
        rf"<br><br>"
        rf"Name the radiation."
    )
    s = rf"The radiation is <strong>{ans}</strong>."
    hint = r"Alpha is least penetrating, beta is moderate, gamma is most penetrating."
    return q, s, hint, 1


def rad_found_penetration_order():
    q = (
        r"Put the following types of nuclear radiation in order of "
        r"<strong>increasing penetrating power</strong>."
        r"<br><br>"
        r"alpha, beta, gamma"
    )
    s = (
        r"In order of increasing penetrating power:"
        r"<br><strong>alpha, beta, gamma</strong>."
    )
    hint = r"Alpha is easiest to stop; gamma is the hardest to stop."
    return q, s, hint, 1


def rad_found_ionising_order():
    q = (
        r"Put the following types of radiation in order of "
        r"<strong>decreasing ionising power</strong>."
        r"<br><br>"
        r"alpha, beta, gamma"
    )
    s = (
        r"In order of decreasing ionising power:"
        r"<br><strong>alpha, beta, gamma</strong>."
    )
    hint = r"The most strongly ionising radiation is the least penetrating."
    return q, s, hint, 1


def rad_found_decay_definition():
    q = (
        r"What is meant by <strong>radioactive decay</strong>?"
        r"<br><br>"
        r"Your answer should include the idea of unstable nuclei."
    )
    s = (
        r"Radioactive decay is the <strong>random emission of radiation</strong> from an "
        r"<strong>unstable nucleus</strong>."
    )
    hint = r"Use the words random, unstable nucleus, and radiation."
    return q, s, hint, 2


def rad_found_activity_definition():
    q = (
        r"Define the term <strong>activity</strong> and state its unit."
    )
    s = (
        r"Activity is the <strong>rate at which unstable nuclei decay</strong>."
        r"<br><br>"
        r"It is measured in <strong>becquerels (Bq)</strong>, where 1 Bq = 1 decay per second."
    )
    hint = r"Activity = decays per second. Unit = Bq."
    return q, s, hint, 2


def rad_found_background_sources():
    source = random.choice([
        "radon gas from rocks",
        "cosmic rays from space",
        "medical exposure such as X-rays",
        "radioactive materials in food and drink",
    ])
    q = (
        r"State what is meant by <strong>background radiation</strong>."
        r"<br><br>"
        rf"Give one source, for example: <em>{source}</em>."
    )
    s = (
        r"Background radiation is the <strong>low-level radiation that is always present in the environment</strong>."
        r"<br><br>"
        rf"One valid source is <strong>{source}</strong>."
    )
    hint = r"Think of radiation we are exposed to all the time, even without a lab source nearby."
    return q, s, hint, 2


def rad_found_half_life_definition():
    q = (
        r"Define <strong>half-life</strong>."
    )
    s = (
        r"Half-life is the time taken for the <strong>number of undecayed nuclei</strong> in a sample "
        r"to halve, or for the <strong>activity / count rate</strong> to halve."
    )
    hint = r"Half-life means half remaining, or half the activity."
    return q, s, hint, 2


def rad_found_irradiation_vs_contamination():
    q = (
        r"State the difference between <strong>irradiation</strong> and <strong>contamination</strong>."
    )
    s = (
        r"<strong>Irradiation</strong> means being exposed to radiation."
        r"<br>"
        r"<strong>Contamination</strong> means radioactive material gets <strong>onto or into</strong> an object or person."
        r"<br><br>"
        r"An irradiated object does <strong>not</strong> become radioactive, but a contaminated one does."
    )
    hint = r"Contamination involves radioactive atoms actually being present."
    return q, s, hint, 3


# ---------------------------
# INTERMEDIATE (10 variants)
# ---------------------------

def rad_inter_alpha_equation():
    q = (
        r"Complete the alpha decay equation:"
        r"<br><br>"
        r"<strong>238/92 U &rarr; ____ + 4/2 He</strong>"
        r"<br><br>"
        r"State the missing nuclide."
    )
    s = (
        r"In alpha decay, the mass number decreases by <strong>4</strong> and the atomic number decreases by <strong>2</strong>."
        r"<br><br>"
        r"So the missing nuclide is <strong>234/90 Th</strong>."
    )
    hint = r"Alpha particle = 4/2 He, so subtract 4 from mass number and 2 from atomic number."
    return q, s, hint, 3


def rad_inter_beta_equation():
    q = (
        r"Complete the beta-minus decay equation:"
        r"<br><br>"
        r"<strong>14/6 C &rarr; ____ + 0/-1 e</strong>"
    )
    s = (
        r"In beta-minus decay, the <strong>mass number stays the same</strong> and the "
        r"<strong>atomic number increases by 1</strong>."
        r"<br><br>"
        r"So the missing nuclide is <strong>14/7 N</strong>."
    )
    hint = r"In beta-minus decay, a neutron becomes a proton."
    return q, s, hint, 3


def rad_inter_gamma_equation():
    q = (
        r"A nucleus emits <strong>gamma radiation</strong>."
        r"<br><br>"
        r"What happens to its <strong>mass number</strong> and <strong>atomic number</strong>?"
    )
    s = (
        r"In gamma emission, the nucleus loses energy but not particles."
        r"<br><br>"
        r"So the <strong>mass number stays the same</strong> and the <strong>atomic number stays the same</strong>."
    )
    hint = r"Gamma is electromagnetic radiation, not a particle with mass or charge."
    return q, s, hint, 2


def rad_inter_neutron_number():
    proton_number = random.choice([6, 8, 17, 26, 82])
    mass_number = proton_number + random.choice([6, 8, 10, 12, 20, 44])
    neutrons = mass_number - proton_number
    q = (
        rf"An isotope has proton number <strong>{proton_number}</strong> and mass number <strong>{mass_number}</strong>."
        rf"<br><br>"
        rf"Calculate the number of <strong>neutrons</strong> in the nucleus."
    )
    s = (
        rf"Number of neutrons = mass number - proton number"
        rf"<br>{mass_number} - {proton_number} = <strong>{neutrons}</strong>"
    )
    hint = r"Mass number = protons + neutrons."
    return q, s, hint, 2


def rad_inter_count_rate_background():
    total = random.randint(45, 120)
    background = random.randint(8, 20)
    source = total - background
    q = (
        rf"A detector measures a count rate of <strong>{total} counts per minute</strong> near a radioactive source."
        rf"<br>"
        rf"The background count rate is <strong>{background} counts per minute</strong>."
        rf"<br><br>"
        rf"Calculate the count rate due to the source alone."
    )
    s = (
        rf"Source count rate = total count rate - background count rate"
        rf"<br>{total} - {background} = <strong>{source} counts per minute</strong>"
    )
    hint = r"Always subtract background radiation first."
    return q, s, hint, 2


def rad_inter_half_life_count_simple():
    initial = random.choice([160, 240, 320, 400])
    halves = random.choice([1, 2, 3, 4])
    remaining = initial // (2 ** halves)
    q = (
        rf"A radioactive sample has an initial count rate of <strong>{initial} counts per minute</strong>."
        rf"<br>"
        rf"After <strong>{halves}</strong> half-lives, what will the count rate be?"
    )
    s = (
        rf"Each half-life halves the count rate."
        rf"<br><br>"
        rf"After {halves} half-lives:"
        rf"<br>{initial} &divide; 2^{halves} = <strong>{remaining} counts per minute</strong>"
    )
    hint = r"Divide by 2 once for each half-life."
    return q, s, hint, 3


def rad_inter_half_life_time():
    half_life = random.choice([2, 3, 5, 10])
    n_halves = random.choice([2, 3, 4])
    total_time = half_life * n_halves
    q = (
        rf"The half-life of an isotope is <strong>{half_life} hours</strong>."
        rf"<br><br>"
        rf"How long would it take for the activity to fall to <strong>one-{2**n_halves}th</strong> of its original value?"
    )
    s = (
        rf"To fall to one-{2**n_halves}th of the original value takes <strong>{n_halves}</strong> half-lives."
        rf"<br>"
        rf"Total time = {n_halves} &times; {half_life} = <strong>{total_time} hours</strong>"
    )
    hint = r"1/4 = 2 half-lives, 1/8 = 3 half-lives, 1/16 = 4 half-lives."
    return q, s, hint, 3


def rad_inter_choose_shielding():
    rad, shield = random.choice([
        ("alpha", "paper or a few cm of air"),
        ("beta", "thin aluminium"),
        ("gamma", "thick lead or concrete"),
    ])
    q = (
        rf"A scientist wants to reduce exposure to <strong>{rad}</strong> radiation."
        rf"<br><br>"
        rf"What shielding material would be suitable?"
    )
    s = rf"Suitable shielding for <strong>{rad}</strong> radiation is <strong>{shield}</strong>."
    hint = r"Alpha: paper, beta: aluminium, gamma: thick lead/concrete."
    return q, s, hint, 1


def rad_inter_medical_use():
    use = random.choice([
        ("gamma", "sterilising medical equipment", "because gamma is very penetrating and can kill microbes without direct contact"),
        ("gamma", "medical tracers", "because gamma can pass out of the body and be detected outside the body"),
        ("beta", "controlling the thickness of paper or aluminium foil", "because some beta passes through thin sheets, so changes in thickness change the detector reading"),
        ("alpha", "smoke alarms", "because alpha is strongly ionising but not very penetrating"),
    ])
    rad, app, why = use
    q = (
        rf"Give one use of <strong>{rad}</strong> radiation and explain why it is suitable."
    )
    s = rf"One use is <strong>{app}</strong>, {why}."
    hint = r"Match the use to the radiation’s penetrating or ionising ability."
    return q, s, hint, 3


def rad_inter_risk_factor():
    q = (
        r"Explain why <strong>contamination inside the body</strong> can be more dangerous than irradiation from an external source."
    )
    s = (
        r"If radioactive material gets inside the body, it can emit radiation from <strong>inside the body for a prolonged time</strong>."
        r"<br><br>"
        r"This means internal tissues and organs are continuously exposed, making contamination potentially more dangerous."
    )
    hint = r"Think about where the source is, and how long it stays there."
    return q, s, hint, 3


# ---------------------------
# DIFFICULT (10 variants)
# ---------------------------

def rad_diff_half_life_mass():
    initial = random.choice([64, 80, 96, 128])
    half_life = random.choice([5, 10, 20])
    n_halves = random.choice([3, 4])
    time = half_life * n_halves
    remaining = initial / (2 ** n_halves)
    q = (
        rf"A sample contains <strong>{initial} g</strong> of a radioactive isotope."
        rf"<br>"
        rf"The isotope has a half-life of <strong>{half_life} years</strong>."
        rf"<br><br>"
        rf"Calculate the mass remaining after <strong>{time} years</strong>."
    )
    s = (
        rf"{time} years corresponds to {n_halves} half-lives."
        rf"<br>"
        rf"Remaining mass = {initial} &divide; 2^{n_halves} = <strong>{remaining:g} g</strong>"
    )
    hint = r"First work out how many half-lives have passed, then keep halving."
    return q, s, hint, 4


def rad_diff_half_life_activity():
    initial = random.choice([960, 720, 640, 480])
    half_life = random.choice([2, 4, 6])
    time = half_life * random.choice([2, 3, 4])
    n_halves = time // half_life
    final = initial / (2 ** n_halves)
    q = (
        rf"A radioactive source has an initial activity of <strong>{initial} Bq</strong>."
        rf"<br>"
        rf"Its half-life is <strong>{half_life} days</strong>."
        rf"<br><br>"
        rf"What is its activity after <strong>{time} days</strong>?"
    )
    s = (
        rf"Number of half-lives = {time} &divide; {half_life} = <strong>{n_halves}</strong>"
        rf"<br>"
        rf"Activity after {n_halves} half-lives = {initial} &divide; 2^{n_halves} = <strong>{final:g} Bq</strong>"
    )
    hint = r"Activity halves every half-life, just like mass or count rate."
    return q, s, hint, 4


def rad_diff_find_half_life_from_table():
    initial = random.choice([800, 600, 400])
    half_life = random.choice([3, 5, 8])
    data = [
        (0, initial),
        (half_life, initial / 2),
        (2 * half_life, initial / 4),
        (3 * half_life, initial / 8),
    ]
    q = (
        r"A radioactive sample gives the following activity data:"
        r"<br><br>"
        r"<table style='border-collapse:collapse;'>"
        r"<tr><th style='border:1px solid #ccc; padding:6px;'>Time</th><th style='border:1px solid #ccc; padding:6px;'>Activity (Bq)</th></tr>"
        + "".join(
            rf"<tr><td style='border:1px solid #ccc; padding:6px;'>{t} h</td><td style='border:1px solid #ccc; padding:6px;'>{a:g}</td></tr>"
            for t, a in data
        )
        + r"</table><br>"
        r"Determine the <strong>half-life</strong> of the isotope."
    )
    s = (
        rf"The activity falls from <strong>{initial}</strong> to <strong>{initial/2:g}</strong> in "
        rf"<strong>{half_life} hours</strong>."
        rf"<br><br>"
        rf"So the half-life is <strong>{half_life} hours</strong>."
    )
    hint = r"Half-life = time taken for the activity to drop to half its value."
    return q, s, hint, 4


def rad_diff_random_predictable():
    q = (
        r"Radioactive decay is described as <strong>random</strong>, but half-life is still predictable."
        r"<br><br>"
        r"Explain how both of these statements can be true."
    )
    s = (
        r"The decay of any <strong>individual nucleus</strong> is random, so you cannot predict exactly when one nucleus will decay."
        r"<br><br>"
        r"However, in a <strong>large sample</strong> containing many nuclei, the overall pattern is predictable, so the half-life can be measured reliably."
    )
    hint = r"Think: one nucleus = unpredictable, lots of nuclei = predictable trend."
    return q, s, hint, 4


def rad_diff_irradiation_contamination_evaluate():
    q = (
        r"A student says, <em>'If an object is irradiated, it becomes radioactive.'</em>"
        r"<br><br>"
        r"Evaluate this statement."
    )
    s = (
        r"The statement is <strong>incorrect</strong>."
        r"<br><br>"
        r"Irradiation means exposure to radiation only. It does <strong>not</strong> make the object radioactive."
        r"<br><br>"
        r"An object only becomes radioactive if it is <strong>contaminated</strong> by radioactive material."
    )
    hint = r"Exposure is not the same thing as radioactive atoms being transferred."
    return q, s, hint, 4


def rad_diff_compare_alpha_beta_gamma():
    q = (
        r"Compare <strong>alpha</strong>, <strong>beta</strong> and <strong>gamma</strong> radiation in terms of:"
        r"<br><br>"
        r"<ol style='padding-left:20px;'>"
        r"<li>nature of the radiation</li>"
        r"<li>ionising power</li>"
        r"<li>penetrating power</li>"
        r"</ol>"
    )
    s = (
        r"<strong>Alpha</strong>: helium nucleus; <strong>most ionising</strong>; <strong>least penetrating</strong>."
        r"<br>"
        r"<strong>Beta</strong>: fast electron; <strong>moderately ionising</strong>; <strong>moderately penetrating</strong>."
        r"<br>"
        r"<strong>Gamma</strong>: electromagnetic wave; <strong>least ionising</strong>; <strong>most penetrating</strong>."
    )
    hint = r"Alpha = particle with lots of ionisation, gamma = wave with high penetration."
    return q, s, hint, 5


def rad_diff_background_repeat_readings():
    q = (
        r"A student measures background radiation several times before investigating a radioactive source."
        r"<br><br>"
        r"Explain why taking repeated background readings improves the quality of the investigation."
    )
    s = (
        r"Background radiation <strong>fluctuates randomly</strong>, so a single reading may not be representative."
        r"<br><br>"
        r"Taking repeated readings and calculating a mean reduces the effect of random variation and gives a more reliable value to subtract from the total count rate."
    )
    hint = r"Background radiation isn’t perfectly steady, so one reading may be misleading."
    return q, s, hint, 4


def rad_diff_choose_source_medical():
    q = (
        r"A hospital needs a radioactive source for use as a <strong>medical tracer</strong>."
        r"<br><br>"
        r"Describe the properties that the source should have, and explain why."
    )
    s = (
        r"A suitable source should emit <strong>gamma radiation</strong>, because gamma can pass out of the body and be detected outside the body."
        r"<br><br>"
        r"It should have a <strong>short half-life</strong>, so the patient is not radioactive for longer than necessary."
        r"<br><br>"
        r"It should also be a low enough activity to reduce harm while still giving a detectable signal."
    )
    hint = r"Think about detectability outside the body and minimising patient exposure."
    return q, s, hint, 5


def rad_diff_nuclear_change_reasoning():
    decay = random.choice([
        ("alpha", "mass number decreases by 4 and atomic number decreases by 2"),
        ("beta-minus", "mass number stays the same and atomic number increases by 1"),
        ("gamma", "both mass number and atomic number stay the same"),
    ])
    mode, effect = decay
    q = (
        rf"Explain what happens to the <strong>mass number</strong> and <strong>atomic number</strong> during "
        rf"<strong>{mode}</strong> decay, and explain why."
    )
    s = (
        rf"In <strong>{mode}</strong> decay, the <strong>{effect}</strong>."
        r"<br><br>"
        + (
            r"This is because an alpha particle is a helium nucleus containing 2 protons and 2 neutrons."
            if mode == "alpha" else
            r"This is because a neutron changes into a proton and an electron is emitted."
            if mode == "beta-minus" else
            r"This is because gamma radiation is just energy emitted from the nucleus, not a particle carrying proton or nucleon number."
        )
    )
    hint = r"Link the change in numbers to what is actually emitted."
    return q, s, hint, 4


def rad_diff_multi_step_count_rate():
    total1 = random.randint(180, 260)
    background = random.randint(15, 30)
    half_lives = random.choice([2, 3, 4])
    source1 = total1 - background
    source2 = source1 / (2 ** half_lives)
    total2 = source2 + background
    q = (
        rf"A detector records a total count rate of <strong>{total1} counts per minute</strong> from a radioactive source."
        rf"<br>"
        rf"The background count rate is <strong>{background} counts per minute</strong>."
        rf"<br>"
        rf"After <strong>{half_lives}</strong> half-lives, what total count rate would the detector record?"
    )
    s = (
        rf"First subtract background:"
        rf"<br>Source count rate initially = {total1} - {background} = <strong>{source1}</strong> counts per minute."
        rf"<br><br>"
        rf"After {half_lives} half-lives, source count rate = {source1} &divide; 2^{half_lives} = <strong>{source2:g}</strong> counts per minute."
        rf"<br><br>"
        rf"Total detector reading = source + background = {source2:g} + {background} = <strong>{total2:g} counts per minute</strong>."
    )
    hint = r"Subtract background first, halve the source count, then add background back on at the end."
    return q, s, hint, 5


# ---------------------------
# LESSON PAGE CONTENT
# ---------------------------

def edexcel_combined_physics_radioactivity_lesson():
    return {
        "title": "GCSE Combined Science Physics: Radioactivity",
        "intro": (
            "This topic covers unstable nuclei, alpha/beta/gamma radiation, activity, half-life, "
            "background radiation, and the difference between irradiation and contamination."
        ),
        "sections": [
            {
                "heading": "Atomic structure and isotopes",
                "content": [
                    "Atoms contain protons and neutrons in the nucleus, with electrons in shells around the nucleus.",
                    "The proton number identifies the element.",
                    "Isotopes are atoms of the same element with the same number of protons but different numbers of neutrons.",
                    "Some isotopes are unstable and radioactive."
                ]
            },
            {
                "heading": "Types of nuclear radiation",
                "content": [
                    "Alpha radiation is a helium nucleus.",
                    "Beta-minus radiation is a fast electron emitted from the nucleus.",
                    "Gamma radiation is electromagnetic radiation.",
                    "Alpha is the most ionising and least penetrating; gamma is the least ionising and most penetrating."
                ]
            },
            {
                "heading": "Radioactive decay and equations",
                "content": [
                    "Radioactive decay is random.",
                    "Alpha decay reduces mass number by 4 and atomic number by 2.",
                    "Beta-minus decay leaves the mass number unchanged but increases the atomic number by 1.",
                    "Gamma emission does not change mass number or atomic number."
                ]
            },
            {
                "heading": "Activity, count rate and background radiation",
                "content": [
                    "Activity is the rate of decay and is measured in becquerels (Bq).",
                    "Count rate is the number of detected counts per second or per minute.",
                    "Background radiation comes from sources such as radon gas, cosmic rays, and medical sources.",
                    "Background count should be measured and subtracted."
                ]
            },
            {
                "heading": "Half-life",
                "content": [
                    "Half-life is the time taken for half the undecayed nuclei to decay, or for the activity/count rate to halve.",
                    "The decay of a single nucleus is unpredictable, but the behaviour of a large sample is predictable.",
                    "After each half-life, the number remaining is halved again."
                ]
            },
            {
                "heading": "Contamination and irradiation",
                "content": [
                    "Irradiation means being exposed to radiation.",
                    "Contamination means radioactive material gets onto or into an object or person.",
                    "Contamination is usually more dangerous if it enters the body, because it continues to irradiate tissues from inside."
                ]
            },
            {
                "heading": "Uses and hazards",
                "content": [
                    "Alpha is used in smoke alarms.",
                    "Beta can be used in thickness monitoring.",
                    "Gamma is used for sterilising equipment and as a medical tracer.",
                    "A suitable medical tracer should emit gamma and have a short half-life."
                ]
            }
        ]
    }


# ---------------------------
# MAIN ROUTER
# ---------------------------

def edexcel_combined_physics_radioactivity(difficulty, mode):
    foundational = [
        rad_found_atom_structure,
        rad_found_isotope_definition,
        rad_found_identify_radiation,
        rad_found_penetration_order,
        rad_found_ionising_order,
        rad_found_decay_definition,
        rad_found_activity_definition,
        rad_found_background_sources,
        rad_found_half_life_definition,
        rad_found_irradiation_vs_contamination,
    ]

    intermediate = [
        rad_inter_alpha_equation,
        rad_inter_beta_equation,
        rad_inter_gamma_equation,
        rad_inter_neutron_number,
        rad_inter_count_rate_background,
        rad_inter_half_life_count_simple,
        rad_inter_half_life_time,
        rad_inter_choose_shielding,
        rad_inter_medical_use,
        rad_inter_risk_factor,
    ]

    difficult = [
        rad_diff_half_life_mass,
        rad_diff_half_life_activity,
        rad_diff_find_half_life_from_table,
        rad_diff_random_predictable,
        rad_diff_irradiation_contamination_evaluate,
        rad_diff_compare_alpha_beta_gamma,
        rad_diff_background_repeat_readings,
        rad_diff_choose_source_medical,
        rad_diff_nuclear_change_reasoning,
        rad_diff_multi_step_count_rate,
    ]

    if mode == "lesson":
        lesson = edexcel_combined_physics_radioactivity_lesson()
        return make_problem(
            lesson["title"],
            lesson,
            "Use the revision page to review the key ideas, then try generated questions.",
            difficulty,
            0,
            "gcse",
            "physics",
            "radioactivity",
        )

    if difficulty == "mixed":
        difficulty = random.choices(
            ["foundational", "intermediate", "difficult"],
            weights=[50, 30, 20]
        )[0]

    if difficulty == "foundational":
        variant = random.choice(foundational)
    elif difficulty == "intermediate":
        variant = random.choice(intermediate)
    elif difficulty == "difficult":
        variant = random.choice(difficult)
    else:
        variant = random.choice(foundational + intermediate + difficult)

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, "gcse", "physics", "radioactivity")