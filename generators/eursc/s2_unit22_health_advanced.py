"""S2 Unit 2.2 Health advanced Practice pools (MS / SMS). Isolated from lesson banks.

Batch 3.2 (safeguarding-gated). Five topics: healthy_living, infectious_disease
(multi_step only — its situational pools shipped in the pilot and stay in
``s2_health.py``), noninfectious_disease, dependence_addiction, tobacco.

Matrix (docs/EURSC_ADVANCED_QUESTIONS.md):
  healthy_living         MS I, D   SMS F, I, D
  infectious_disease     MS F, I, D   (SMS: pilot, s2_health.py)
  noninfectious_disease  MS I, D   SMS F, I, D
  dependence_addiction   MS I, D   SMS F, I, D
  tobacco                MS I, D   SMS F, I, D
Foundational MS stays empty (matrix —) for every topic except infectious_disease.

Safeguarding gate for this batch:
  * every scenario is a third-person fictional case, a textbook/public table,
    or an aggregate count; every stem names it as fictional or public;
  * no stem asks about a pupil's body, diet, sleep, mood, screen use,
    relationships, substance use, smoking or vaping status, or family health;
  * nothing ranks classmates, bodies, homes or behaviours;
  * support is signposted to a trusted adult or qualified service, and the
    generator never diagnoses;
  * public-health figures quoted here are labelled as textbook/poster values
    used for teaching, not live statistics.
"""
import random

from generators.eursc.science_shared import (
    habit_bars,
    infection_chain,
    outbreak_bars,
)
from generators.shared.utils import graded_answer_number_fields, make_graded_problem
from models.svg_kit import bar_chart

_LEVEL = "eursc"
_SUBJECT = "science"


def _u22_variant(topic, mode_tag, difficulty, suffix):
    def decorator(builder):
        def _fn():
            return make_graded_problem(
                builder(), difficulty, _LEVEL, _SUBJECT, topic
            )

        _fn.__name__ = f"{topic}_{difficulty}_{mode_tag}_{suffix}"
        _fn._kind = "number_fields"
        _fn._randomizable = True
        return _fn

    return decorator


def _u22_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _u22_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"1|{'|'.join(step_ids)}", bank


def _u22_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f"c{i + 1}" for i in range(len(correct_texts)))
    bank = [{"id": cid, "text": text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"pick|{pick_count}|{'|'.join(correct_ids)}", bank, pick_count


def _pct(part, whole):
    return round(100 * part / whole)


# ---------------------------------------------------------------------------
# healthy_living — multi_step (I, D); foundational MS stays — (matrix)
# ---------------------------------------------------------------------------

_HL_MS_I_SURVEY_PACKS = (
    {"pupils": 200, "meets": 120, "minutes": 60},
    {"pupils": 150, "meets": 90, "minutes": 60},
    {"pupils": 250, "meets": 200, "minutes": 60},
)


@_u22_variant("healthy_living", "ms", "intermediate", "activity_pct_then_evidence_mcq")
def _healthy_living_intermediate_ms_activity_pct_then_evidence_mcq():
    pack = random.choice(_HL_MS_I_SURVEY_PACKS)
    pct = _pct(pack["meets"], pack["pupils"])
    correct = "an aggregate count for a fictional school, not a file on any pupil"
    distractors = (
        "a ranking of the pupils who moved least",
        "proof that one named pupil is unhealthy",
        "a reason to collect each pupil's step count",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook table reports that {pack['meets']} of "
        f"{pack['pupils']} pupils at an imaginary school met a public guideline of "
        f"{pack['minutes']} minutes of daily activity.</p>"
        "<p>(i) Calculate the percentage who met the guideline (whole number).</p>"
        "<p>(ii) Using the figure from (i), the table is best described as</p>"
    )
    solution = (
        f"(i) {pack['meets']} ÷ {pack['pupils']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentage = part ÷ whole × 100, then treat "
        "the result as public aggregate evidence, never a pupil profile."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pct, letter),
            ("Percentage met guideline (%)", "What the table is"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Whole-number percentage, then choose the aggregate description.",
        ),
    )


@_u22_variant("healthy_living", "ms", "intermediate", "sleep_bar_then_tradeoff_order")
def _healthy_living_intermediate_ms_sleep_bar_then_tradeoff_order():
    diagram = str(habit_bars(title="Fictional habit sketch"))
    order_raw, order_bank = _u22_order_field(
        (
            "Late unmanaged screen use runs into the night",
            "Time available for sleep is reduced",
            "Recovery and concentration the next day can suffer",
        ),
        ("The app records a named pupil's bedtime",),
    )
    question = (
        diagram
        + "<p>A fictional habit sketch shows three schematic bars (A sleep, "
        "B activity, C screen time).</p>"
        "<p>(i) Enter the number of labelled bars.</p>"
        "<p>(ii) Using bars A and C from (i), order the trade-off chain from "
        "late screens to next-day effects.</p>"
    )
    solution = (
        "(i) <strong>3</strong> bars<br>"
        "(ii) <strong>late screens → less sleep time → recovery suffers</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the bars, then follow time: screens "
        "late at night squeeze the sleep bar, and rest affects the next day."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (3, order_raw),
            ("Labelled bars", "Trade-off chain"),
            field_types=("number", "order"),
            field_options=(None, order_bank),
            format_hint="Enter 3, then order the three-step chain.",
        ),
    )


@_u22_variant("healthy_living", "ms", "intermediate", "microbiome_pick_then_pathogen_keyword")
def _healthy_living_intermediate_ms_microbiome_pick_then_pathogen_keyword():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Living microorganisms that interact with the body",
            "Some members can be helpful rather than harmful",
        ),
        (
            "A class vote on favourite snacks",
            "A list of private gut symptoms the app stores",
        ),
        2,
    )
    correct = "pathogen"
    question = (
        "<p>A fictional biology poster describes the microbiome.</p>"
        "<p>(i) Select the two statements that describe the microbiome scientifically.</p>"
        "<p>(ii) Using the second idea from (i), write the one-word term for a "
        "microorganism that <em>does</em> cause disease.</p>"
    )
    solution = (
        "(i) Living microorganisms; some helpful.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Not every microbe is harmful; the harmful "
        "ones have a specific name."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, correct),
            ("Microbiome statements", "Disease-causing microbe"),
            field_types=("pick", "keyword"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two statements, then one word.",
        ),
    )


_HL_MS_D_CLAIM_PACKS = (
    {"claim": "a drink that 'replaces sleep'", "sample": 12, "control": "no comparison group"},
    {"claim": "a snack that 'cures tiredness'", "sample": 10, "control": "no comparison group"},
    {"claim": "an app that 'guarantees eight hours'", "sample": 15, "control": "no comparison group"},
)


@_u22_variant("healthy_living", "ms", "difficult", "claim_sample_then_flaws_pick_then_verdict")
def _healthy_living_difficult_ms_claim_sample_then_flaws_pick_then_verdict():
    pack = random.choice(_HL_MS_D_CLAIM_PACKS)
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            f"Only {pack['sample']} people were tested — too few to generalise",
            f"There was {pack['control']}, so nothing was compared",
        ),
        (
            "The advert used bright colours",
            "The product was sold in a shop",
        ),
        2,
    )
    correct = "treat the claim as unproven and look for independent evidence"
    distractors = (
        "accept the claim because the sample were all happy",
        "ask classmates which of them tried it",
        "store the advert as a medical record",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional advert for {pack['claim']} says it was 'tested on "
        f"{pack['sample']} people' with {pack['control']}.</p>"
        "<p>(i) Enter the number of people tested.</p>"
        "<p>(ii) Using that number from (i), select the two flaws in the evidence.</p>"
        "<p>(iii) Given the flaws in (ii), the scientific verdict is to</p>"
    )
    solution = (
        f"(i) <strong>{pack['sample']}</strong><br>"
        "(ii) Small sample; no comparison group.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the sample size, judge the design, "
        "then treat an untested claim as unproven."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pack["sample"], pick_raw, letter),
            ("People tested", "Flaws in the evidence", "Verdict"),
            field_types=("number", "pick", "mcq"),
            field_options=(None, pick_bank, options),
            field_pick_counts=(None, pick_count, None),
            format_hint="Number, two flaws, then the verdict.",
        ),
    )


_HL_MS_D_SLEEP_PACKS = (
    {"pupils": 100, "under": 35},
    {"pupils": 200, "under": 50},
    {"pupils": 120, "under": 30},
)


@_u22_variant("healthy_living", "ms", "difficult", "sleep_share_then_signpost_mcq_then_word")
def _healthy_living_difficult_ms_sleep_share_then_signpost_mcq_then_word():
    pack = random.choice(_HL_MS_D_SLEEP_PACKS)
    pct = _pct(pack["under"], pack["pupils"])
    correct = "signpost a trusted adult or qualified help; the app does not diagnose"
    distractors = (
        "publish which pupils sleep least",
        "ask each pupil to log bedtimes in the quiz",
        "treat tiredness as always a virus",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public-health leaflet says that in an anonymous survey of "
        f"{pack['pupils']} teenagers, {pack['under']} reported getting less rest than "
        "the teaching guideline.</p>"
        "<p>(i) Calculate the percentage below the guideline (whole number).</p>"
        "<p>(ii) Using the share from (i), if a fictional character in the leaflet "
        "is persistently exhausted, the lesson's next step is to</p>"
        "<p>(iii) Write the one-word health need the leaflet is about.</p>"
    )
    solution = (
        f"(i) {pack['under']} ÷ {pack['pupils']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>sleep</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentages describe a group; an individual "
        "case is signposted, never diagnosed or ranked."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pct, letter, "sleep"),
            ("Below guideline (%)", "Next step for the case", "Health need"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Percentage, signpost choice, then one word.",
        ),
    )


@_u22_variant("healthy_living", "ms", "difficult", "needs_order_then_misuse_pick")
def _healthy_living_difficult_ms_needs_order_then_misuse_pick():
    order_raw, order_bank = _u22_order_field(
        (
            "Food supplies energy and nutrients",
            "Activity uses that energy and strengthens the body",
            "Sleep lets the body recover from the activity",
        ),
        ("A poster slogan replaces all three needs",),
    )
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Ranking pupils by body shape, meals or mood",
            "Collecting private meal or screen logs in a quiz",
        ),
        (
            "Using a fictional case to explain a trade-off",
            "Quoting a public aggregate survey",
        ),
        2,
    )
    question = (
        "<p>A fictional health curriculum poster links three needs in a cycle.</p>"
        "<p>(i) Order the cycle from food, through activity, to recovery.</p>"
        "<p>(ii) Using that cycle from (i), select the two ways a health lesson "
        "would be <em>misused</em>.</p>"
    )
    solution = (
        "(i) <strong>food → activity → sleep/recovery</strong><br>"
        "(ii) Ranking bodies or moods; harvesting private logs."
    )
    hint = (
        "<strong>Key idea:</strong> Energy in, energy used, recovery — and a "
        "lesson teaches the cycle without profiling any pupil."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Needs cycle", "Misuses"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order three needs, then select two misuses.",
        ),
    )


# healthy_living — situational_multi_step (F, I, D)

_HL_SMS_F_CANTEEN_PACKS = (
    {"who": "Alex", "place": "fictional school canteen", "groups": 4, "days": 5},
    {"who": "Sam", "place": "fictional holiday camp kitchen", "groups": 4, "days": 7},
    {"who": "Jordan", "place": "fictional sports-club café", "groups": 4, "days": 5},
)


@_u22_variant("healthy_living", "sms", "foundational", "canteen_groups_then_balance_mcq")
def _healthy_living_foundational_sms_canteen_groups_then_balance_mcq():
    pack = random.choice(_HL_SMS_F_CANTEEN_PACKS)
    correct = "a mix of food groups across the week, not one magic food"
    distractors = (
        "the same single dish every day",
        "a ranking of diners by lunch",
        "a private meal list stored by the app",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>{pack['who']} (a fictional planner) designs a {pack['days']}-day menu "
        f"for a {pack['place']} using {pack['groups']} food groups.</p>"
        "<p>(i) Enter the number of food groups on the plan.</p>"
        "<p>(ii) Using those groups from (i), a balanced menu means</p>"
    )
    solution = (
        f"(i) <strong>{pack['groups']}</strong> groups<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the groups, then remember balance is a "
        "mix over time."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["groups"], letter),
            ("Food groups", "Balanced menu means"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter the group count, then choose the balance idea.",
        ),
    )


_HL_SMS_F_CLUB_PACKS = (
    {"club": "fictional after-school club", "sessions": 3, "minutes": 60},
    {"club": "fictional youth centre", "sessions": 2, "minutes": 60},
    {"club": "fictional summer camp", "sessions": 5, "minutes": 60},
)


@_u22_variant("healthy_living", "sms", "foundational", "club_minutes_then_activity_pick")
def _healthy_living_foundational_sms_club_minutes_then_activity_pick():
    pack = random.choice(_HL_SMS_F_CLUB_PACKS)
    total = pack["sessions"] * pack["minutes"]
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Regular activity can support health in public evidence",
            "Activity is a public-health idea, not a contest about bodies",
        ),
        (
            "The club should post each member's step count",
            "Activity replaces the need for sleep",
        ),
        2,
    )
    question = (
        f"<p>A {pack['club']} runs {pack['sessions']} activity sessions a week, "
        f"each {pack['minutes']} minutes, for its fictional members.</p>"
        "<p>(i) Calculate the total activity minutes per week.</p>"
        "<p>(ii) Using that total from (i), select the two scientific statements "
        "about activity.</p>"
    )
    solution = (
        f"(i) {pack['sessions']} × {pack['minutes']} = <strong>{total}</strong> minutes<br>"
        "(ii) Supports health; public-health idea, not a body contest."
    )
    hint = (
        "<strong>Key idea:</strong> Multiply sessions by minutes, then keep the "
        "two public-health statements."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (total, pick_raw),
            ("Minutes per week", "Activity statements"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Total minutes, then two statements.",
        ),
    )


@_u22_variant("healthy_living", "sms", "foundational", "poster_bars_then_sleep_keyword")
def _healthy_living_foundational_sms_poster_bars_then_sleep_keyword():
    diagram = str(habit_bars(title="Fictional poster bars"))
    question = (
        diagram
        + "<p>A fictional health-week poster shows three schematic bars: A sleep, "
        "B activity, C screen time.</p>"
        "<p>(i) Which letter is the activity bar?</p>"
        "<p>(ii) Using the tallest bar next to it from (i), write the one-word "
        "health need that late screens can crowd out.</p>"
    )
    solution = (
        "(i) <strong>B</strong><br>"
        "(ii) <strong>sleep</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> B is activity; the tall bar A is the rest "
        "need."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("B", "sleep"),
            ("Activity bar letter", "Health need"),
            field_types=("keyword", "keyword"),
            format_hint="Enter B, then write sleep.",
        ),
    )


_HL_SMS_I_SURVEY_PACKS = (
    {"town": "fictional town", "asked": 400, "active": 240, "guideline": 60},
    {"town": "fictional island school", "asked": 300, "active": 210, "guideline": 60},
    {"town": "fictional city district", "asked": 500, "active": 350, "guideline": 60},
)


@_u22_variant("healthy_living", "sms", "intermediate", "survey_pct_then_use_order")
def _healthy_living_intermediate_sms_survey_pct_then_use_order():
    pack = random.choice(_HL_SMS_I_SURVEY_PACKS)
    pct = _pct(pack["active"], pack["asked"])
    order_raw, order_bank = _u22_order_field(
        (
            "Collect anonymous aggregate answers",
            "Calculate the share meeting the guideline",
            "Plan a public campaign for the whole area",
        ),
        ("Publish the names of the least active respondents",),
    )
    question = (
        f"<p>A public-health team in a {pack['town']} runs an anonymous survey: "
        f"{pack['active']} of {pack['asked']} respondents meet a "
        f"{pack['guideline']}-minute daily activity guideline.</p>"
        "<p>(i) Calculate the percentage meeting the guideline (whole number).</p>"
        "<p>(ii) Using that share from (i), order how the team should use the data.</p>"
    )
    solution = (
        f"(i) {pack['active']} ÷ {pack['asked']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) <strong>collect anonymously → calculate share → plan a campaign</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentage first; then the data serves the "
        "whole area, never a name-and-shame list."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pct, order_raw),
            ("Meeting guideline (%)", "Using the data"),
            field_types=("number", "order"),
            field_options=(None, order_bank),
            format_hint="Whole-number percentage, then order three steps.",
        ),
    )


_HL_SMS_I_CASE_PACKS = (
    {"who": "Riley", "hours": 2, "effect": "falls asleep in a fictional morning lesson"},
    {"who": "Casey", "hours": 3, "effect": "cannot concentrate in a fictional revision session"},
    {"who": "Morgan", "hours": 2, "effect": "is irritable in a fictional team practice"},
)


@_u22_variant("healthy_living", "sms", "intermediate", "case_screens_then_mechanism_mcq_then_word")
def _healthy_living_intermediate_sms_case_screens_then_mechanism_mcq_then_word():
    pack = random.choice(_HL_SMS_I_CASE_PACKS)
    correct = "late screens trade off against sleep time; recovery suffers"
    distractors = (
        "screens create energy so more is always better",
        f"{pack['who']} must upload a screen log to the quiz",
        "tiredness proves an infection",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional case study, {pack['who']} uses screens for "
        f"{pack['hours']} extra hours late at night and then {pack['effect']}.</p>"
        "<p>(i) Enter the extra late-night hours in the case.</p>"
        "<p>(ii) Using those hours from (i), the mechanism the lesson teaches is</p>"
        "<p>(iii) Write the one-word health need that the hours in (i) displaced.</p>"
    )
    solution = (
        f"(i) <strong>{pack['hours']}</strong> hours<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>sleep</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Hours are a time budget; late screens take "
        "them from rest, and the case stays fictional."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pack["hours"], letter, "sleep"),
            ("Extra late hours", "Mechanism", "Displaced need"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Hours, mechanism, then one word.",
        ),
    )


@_u22_variant("healthy_living", "sms", "intermediate", "distress_case_pick_then_signpost_keyword")
def _healthy_living_intermediate_sms_distress_case_pick_then_signpost_keyword():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Mental health is part of health",
            "Personal distress is for a trusted adult or qualified help",
        ),
        (
            "Compare the character's mood with the class",
            "Publish the story in the quiz feed",
        ),
        2,
    )
    question = (
        "<p>A fictional story in a textbook describes a character who is "
        "persistently low and withdrawn at an imaginary school.</p>"
        "<p>(i) Select the two statements that describe how the lesson treats "
        "this case.</p>"
        "<p>(ii) Using the second statement from (i), write the one-word verb "
        "for pointing someone towards qualified help.</p>"
    )
    solution = (
        "(i) Mental health is part of health; distress goes to qualified help.<br>"
        "(ii) <strong>signpost</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Name mental health as health, then point to "
        "real help — the app never diagnoses."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, "signpost"),
            ("How the lesson treats the case", "Verb for pointing to help"),
            field_types=("pick", "keyword"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two statements, then one word.",
        ),
    )


_HL_SMS_D_CAMPAIGN_PACKS = (
    {"area": "fictional county", "before": 40, "after": 55, "asked": 1000},
    {"area": "fictional region", "before": 30, "after": 45, "asked": 800},
    {"area": "fictional city", "before": 50, "after": 62, "asked": 1200},
)


@_u22_variant("healthy_living", "sms", "difficult", "campaign_change_then_caution_pick_then_verdict")
def _healthy_living_difficult_sms_campaign_change_then_caution_pick_then_verdict():
    pack = random.choice(_HL_SMS_D_CAMPAIGN_PACKS)
    change = pack["after"] - pack["before"]
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Other things may have changed in the area at the same time",
            "The survey is self-reported, so answers may be inaccurate",
        ),
        (
            "The percentage went up, so the campaign is proven",
            "Respondents should be named to check them",
        ),
        2,
    )
    correct = "the campaign may have helped, but the evidence is not conclusive"
    distractors = (
        "the campaign is proven beyond doubt",
        "the campaign harmed activity",
        "individual respondents should be ranked",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A public-health campaign in a {pack['area']} is evaluated with an "
        f"anonymous survey of {pack['asked']} people: {pack['before']}% met an "
        f"activity guideline before and {pack['after']}% after.</p>"
        "<p>(i) Calculate the change in percentage points.</p>"
        "<p>(ii) Using that change from (i), select the two cautions before "
        "crediting the campaign.</p>"
        "<p>(iii) Given the cautions in (ii), the fair conclusion is that</p>"
    )
    solution = (
        f"(i) {pack['after']} − {pack['before']} = <strong>{change}</strong> points<br>"
        "(ii) Other changes; self-reported data.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract, then ask what else could explain "
        "the change before crediting one cause."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (change, pick_raw, letter),
            ("Change (percentage points)", "Cautions", "Fair conclusion"),
            field_types=("number", "pick", "mcq"),
            field_options=(None, pick_bank, options),
            field_pick_counts=(None, pick_count, None),
            format_hint="Change, two cautions, then the conclusion.",
        ),
    )


_HL_SMS_D_MICRO_PACKS = (
    {"lab": "fictional university lab", "kinds": 3, "helpful": 2},
    {"lab": "fictional food-science lab", "kinds": 4, "helpful": 3},
    {"lab": "fictional hospital teaching lab", "kinds": 5, "helpful": 3},
)


@_u22_variant("healthy_living", "sms", "difficult", "lab_microbes_then_role_order_then_word")
def _healthy_living_difficult_sms_lab_microbes_then_role_order_then_word():
    pack = random.choice(_HL_SMS_D_MICRO_PACKS)
    harmful = pack["kinds"] - pack["helpful"]
    order_raw, order_bank = _u22_order_field(
        (
            "Identify which microorganisms live with the body",
            "Classify each as helpful or potentially harmful",
            "Explain why not every microbe is a pathogen",
        ),
        ("Ask each pupil to list private gut symptoms",),
    )
    question = (
        f"<p>A {pack['lab']} report lists {pack['kinds']} kinds of microorganism "
        f"in a public microbiome sample; {pack['helpful']} are described as helpful.</p>"
        "<p>(i) Calculate how many kinds are <em>not</em> described as helpful.</p>"
        "<p>(ii) Using the split from (i), order the lab's reasoning steps.</p>"
        "<p>(iii) Write the one-word term for the whole community of microbes "
        "living with a body.</p>"
    )
    solution = (
        f"(i) {pack['kinds']} − {pack['helpful']} = <strong>{harmful}</strong><br>"
        "(ii) <strong>identify → classify → explain</strong><br>"
        "(iii) <strong>microbiome</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract helpful from total, then follow the "
        "lab's identify–classify–explain chain."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (harmful, order_raw, "microbiome"),
            ("Kinds not helpful", "Reasoning steps", "Community term"),
            field_types=("number", "order", "keyword"),
            field_options=(None, order_bank, None),
            format_hint="Subtract, order three steps, then one word.",
        ),
    )


@_u22_variant("healthy_living", "sms", "difficult", "app_claim_pick_then_evidence_mcq")
def _healthy_living_difficult_sms_app_claim_pick_then_evidence_mcq():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Check the claim against independent public evidence",
            "Ask who funded the study behind the claim",
        ),
        (
            "Believe it because the advert is exciting",
            "Store classmates' sleep logs to test it",
        ),
        2,
    )
    correct = "an independent study with a comparison group"
    distractors = (
        "the app company's own advert",
        "a class ranking of who slept most",
        "one fictional influencer's post",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        "<p>A fictional sleep-tracking app claims it 'improves rest for everyone'. "
        "A fictional consumer group investigates.</p>"
        "<p>(i) Select the two scientific moves the group should make.</p>"
        "<p>(ii) Using the first move from (i), the strongest evidence would be</p>"
    )
    solution = (
        "(i) Check independent evidence; ask who funded it.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Claims are checked against independent "
        "evidence, and the best evidence compares groups."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, letter),
            ("Scientific moves", "Strongest evidence"),
            field_types=("pick", "mcq"),
            field_options=(pick_bank, options),
            field_pick_counts=(pick_count, None),
            format_hint="Two moves, then the evidence type.",
        ),
    )


HEALTHY_LIVING_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _healthy_living_intermediate_ms_activity_pct_then_evidence_mcq,
        _healthy_living_intermediate_ms_sleep_bar_then_tradeoff_order,
        _healthy_living_intermediate_ms_microbiome_pick_then_pathogen_keyword,
    ],
    "difficult": [
        _healthy_living_difficult_ms_claim_sample_then_flaws_pick_then_verdict,
        _healthy_living_difficult_ms_sleep_share_then_signpost_mcq_then_word,
        _healthy_living_difficult_ms_needs_order_then_misuse_pick,
    ],
}

HEALTHY_LIVING_SMS_POOLS = {
    "foundational": [
        _healthy_living_foundational_sms_canteen_groups_then_balance_mcq,
        _healthy_living_foundational_sms_club_minutes_then_activity_pick,
        _healthy_living_foundational_sms_poster_bars_then_sleep_keyword,
    ],
    "intermediate": [
        _healthy_living_intermediate_sms_survey_pct_then_use_order,
        _healthy_living_intermediate_sms_case_screens_then_mechanism_mcq_then_word,
        _healthy_living_intermediate_sms_distress_case_pick_then_signpost_keyword,
    ],
    "difficult": [
        _healthy_living_difficult_sms_campaign_change_then_caution_pick_then_verdict,
        _healthy_living_difficult_sms_lab_microbes_then_role_order_then_word,
        _healthy_living_difficult_sms_app_claim_pick_then_evidence_mcq,
    ],
}


# ---------------------------------------------------------------------------
# infectious_disease — multi_step (F, I, D). SMS pools are the pilot's, in
# s2_health.py; this module completes the slug with context-free chains.
# ---------------------------------------------------------------------------

_ID_MS_F_DOUBLE_PACKS = (
    {"start": 2, "steps": 2},
    {"start": 3, "steps": 2},
    {"start": 5, "steps": 2},
)


@_u22_variant("infectious_disease", "ms", "foundational", "double_count_then_chain_order")
def _infectious_disease_foundational_ms_double_count_then_chain_order():
    pack = random.choice(_ID_MS_F_DOUBLE_PACKS)
    final = pack["start"] * (2 ** pack["steps"])
    order_raw, order_bank = _u22_order_field(
        (
            "Source holds the pathogen",
            "Route carries it to a new host",
            "New host can become a further source",
        ),
        ("Infection jumps with no route because of a rumour",),
    )
    question = (
        f"<p>A fictional token model starts with {pack['start']} cases and the "
        f"count doubles at each of {pack['steps']} steps.</p>"
        "<p>(i) Calculate the number of cases after the two doublings.</p>"
        "<p>(ii) Each new case in (i) needed a route. Order the chain of infection.</p>"
    )
    solution = (
        f"(i) {pack['start']} → {pack['start'] * 2} → <strong>{final}</strong><br>"
        "(ii) <strong>source → route → new host</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Double twice, then remember every new case "
        "travelled source → route → host."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (final, order_raw),
            ("Cases after doubling", "Chain of infection"),
            field_types=("number", "order"),
            field_options=(None, order_bank),
            format_hint="Enter the doubled count, then order the chain.",
        ),
    )


@_u22_variant("infectious_disease", "ms", "foundational", "chain_letter_then_break_mcq")
def _infectious_disease_foundational_ms_chain_letter_then_break_mcq():
    diagram = str(infection_chain(title="Fictional chain sketch"))
    correct = "breaking the route, for example by hand hygiene"
    distractors = (
        "naming the classmate who coughed",
        "giving antibiotics for every virus",
        "waiting for the Moon to change phase",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional worksheet shows the chain of infection as three boxes "
        "(A source, B route, C new host).</p>"
        "<p>(i) Enter the letter of the route.</p>"
        "<p>(ii) Using the box from (i), spread can be slowed by</p>"
    )
    solution = (
        "(i) <strong>B</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> B is the path between source and host, so "
        "cutting the path slows the chain."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("B", letter),
            ("Route letter", "How to slow spread"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Enter B, then choose the route-breaking action.",
        ),
    )


@_u22_variant("infectious_disease", "ms", "foundational", "pathogen_pick_then_virus_word")
def _infectious_disease_foundational_ms_pathogen_pick_then_virus_word():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Bacteria are living cells that can be pathogens",
            "Viruses need a host cell to multiply",
        ),
        (
            "Bacteria and viruses are the same object",
            "The quiz should list who was ill last week",
        ),
        2,
    )
    question = (
        "<p>A fictional microbiology poster contrasts two kinds of pathogen.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), write the one-word name "
        "of the pathogen that cannot multiply outside a host cell.</p>"
    )
    solution = (
        "(i) Bacteria are living cells; viruses need a host cell.<br>"
        "(ii) <strong>virus</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Keep the two real pathogen facts, then name "
        "the host-dependent one."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, "virus"),
            ("Pathogen statements", "Host-dependent pathogen"),
            field_types=("pick", "keyword"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two statements, then one word.",
        ),
    )


_ID_MS_I_COVER_PACKS = (
    {"group": 200, "vaccinated": 160},
    {"group": 250, "vaccinated": 225},
    {"group": 300, "vaccinated": 210},
)


@_u22_variant("infectious_disease", "ms", "intermediate", "coverage_pct_then_vaccine_mcq")
def _infectious_disease_intermediate_ms_coverage_pct_then_vaccine_mcq():
    pack = random.choice(_ID_MS_I_COVER_PACKS)
    pct = _pct(pack["vaccinated"], pack["group"])
    correct = "a safe exposure that trains immunity, so fewer hosts are available"
    distractors = (
        "an antibiotic that kills every virus",
        "a record of which named pupils were injected",
        "a snack vote that makes pathogens leave",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook table gives {pack['vaccinated']} vaccinated "
        f"people in a group of {pack['group']}.</p>"
        "<p>(i) Calculate the vaccination coverage as a whole-number percentage.</p>"
        "<p>(ii) The coverage in (i) slows an outbreak because a vaccine is</p>"
    )
    solution = (
        f"(i) {pack['vaccinated']} ÷ {pack['group']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Coverage is a percentage of the group; "
        "trained immunity removes hosts from the chain."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pct, letter),
            ("Coverage (%)", "Why coverage slows spread"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Whole-number percentage, then the vaccine idea.",
        ),
    )


_ID_MS_I_SERIES_PACKS = (
    {"days": (2, 4, 8), "next": 16},
    {"days": (3, 6, 12), "next": 24},
    {"days": (1, 2, 4), "next": 8},
)


@_u22_variant("infectious_disease", "ms", "intermediate", "series_next_then_hygiene_order")
def _infectious_disease_intermediate_ms_series_next_then_hygiene_order():
    pack = random.choice(_ID_MS_I_SERIES_PACKS)
    d1, d2, d3 = pack["days"]
    chart = (
        outbreak_bars(title="Fictional outbreak model")
        if pack["days"] == (2, 4, 8)
        else bar_chart(
            ["Day 1", "Day 2", "Day 3"],
            list(pack["days"]),
            title="Fictional outbreak model",
            desc="Three day-bars in a fictional doubling model.",
        )
    )
    order_raw, order_bank = _u22_order_field(
        (
            "Wash hands and clean shared surfaces",
            "Fewer contacts carry the pathogen along the route",
            "The next day's count rises more slowly than doubling",
        ),
        ("Publish the names of the day-3 cases",),
    )
    question = (
        str(chart)
        + f"<p>A fictional outbreak model records {d1}, {d2} and {d3} cases on "
        "three days.</p>"
        "<p>(i) If the doubling pattern continues, enter the day-4 count.</p>"
        "<p>(ii) To keep day 4 <em>below</em> the value in (i), order how hygiene "
        "acts on the chain.</p>"
    )
    solution = (
        f"(i) {d3} × 2 = <strong>{pack['next']}</strong><br>"
        "(ii) <strong>hygiene → fewer route contacts → slower rise</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Continue the doubling, then trace how cutting "
        "the route changes the next count."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["next"], order_raw),
            ("Day-4 count", "How hygiene acts"),
            field_types=("number", "order"),
            field_options=(None, order_bank),
            format_hint="Double once more, then order three steps.",
        ),
    )


@_u22_variant("infectious_disease", "ms", "intermediate", "abx_target_then_resist_pick")
def _infectious_disease_intermediate_ms_abx_target_then_resist_pick():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Resistant strains survive and can spread",
            "Viruses are still not treated by antibiotics",
        ),
        (
            "Antibiotics start working on viruses",
            "The quiz should list home prescriptions",
        ),
        2,
    )
    question = (
        "<p>A fictional pharmacy leaflet lists two infections: one bacterial, "
        "one viral.</p>"
        "<p>(i) Enter how many of those two infections antibiotics can target.</p>"
        "<p>(ii) Using the target from (i), if antibiotics are used carelessly, "
        "select the two consequences the lesson teaches.</p>"
    )
    solution = (
        "(i) <strong>1</strong> (the bacterial one)<br>"
        "(ii) Resistant strains spread; viruses still untreated."
    )
    hint = (
        "<strong>Key idea:</strong> Antibiotics target bacteria only; misuse "
        "selects for resistance."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (1, pick_raw),
            ("Infections antibiotics target", "Consequences of misuse"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Enter 1, then select two consequences.",
        ),
    )


_ID_MS_D_TOTAL_PACKS = (
    {"days": (2, 4, 8), "total": 14},
    {"days": (3, 6, 12), "total": 21},
    {"days": (4, 8, 16), "total": 28},
)


@_u22_variant("infectious_disease", "ms", "difficult", "total_cases_then_host_source_mcq_then_word")
def _infectious_disease_difficult_ms_total_cases_then_host_source_mcq_then_word():
    pack = random.choice(_ID_MS_D_TOTAL_PACKS)
    d1, d2, d3 = pack["days"]
    correct = "each new host can become a further source, so the chain keeps growing"
    distractors = (
        "the total proves a named pupil started it",
        "viruses change into bacteria on day 3",
        "the model needs each pupil's medical file",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional counter model records {d1}, {d2} and {d3} new cases on "
        "three days.</p>"
        "<p>(i) Calculate the total number of cases over the three days.</p>"
        "<p>(ii) The total in (i) grows because</p>"
        "<p>(iii) Write the one-word term for the body's defence that can stop "
        "a host in (ii) becoming a source.</p>"
    )
    solution = (
        f"(i) {d1} + {d2} + {d3} = <strong>{pack['total']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>immunity</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Add the days, explain growth by hosts "
        "becoming sources, then name the defence."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pack["total"], letter, "immunity"),
            ("Total cases", "Why the total grows", "Body's defence"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Total, explanation, then one word.",
        ),
    )


_ID_MS_D_TWO_PACKS = (
    {"a": 120, "b": 300, "a_pct": 80, "b_pct": 50},
    {"a": 90, "b": 200, "a_pct": 90, "b_pct": 60},
    {"a": 160, "b": 400, "a_pct": 75, "b_pct": 40},
)


@_u22_variant("infectious_disease", "ms", "difficult", "two_group_gap_then_order_then_pick")
def _infectious_disease_difficult_ms_two_group_gap_then_order_then_pick():
    pack = random.choice(_ID_MS_D_TWO_PACKS)
    gap = pack["a_pct"] - pack["b_pct"]
    order_raw, order_bank = _u22_order_field(
        (
            "Lower coverage leaves more unprotected hosts",
            "More hosts let the route deliver more new cases",
            "New cases become further sources",
        ),
        ("The larger group is blamed as a named source",),
    )
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Compare coverage percentages, not raw group sizes",
            "Treat both figures as public aggregates",
        ),
        (
            "Rank the groups' members by who was ill",
            "Assume the bigger group is healthier because it is bigger",
        ),
        2,
    )
    question = (
        f"<p>A fictional public-health table compares two groups: group A "
        f"({pack['a']} people, {pack['a_pct']}% vaccinated) and group B "
        f"({pack['b']} people, {pack['b_pct']}% vaccinated).</p>"
        "<p>(i) Calculate the coverage gap in percentage points.</p>"
        "<p>(ii) Using the lower-coverage group from (i), order why an outbreak "
        "grows faster there.</p>"
        "<p>(iii) Select the two fair ways to read this table.</p>"
    )
    solution = (
        f"(i) {pack['a_pct']} − {pack['b_pct']} = <strong>{gap}</strong> points<br>"
        "(ii) <strong>more unprotected hosts → more new cases → further sources</strong><br>"
        "(iii) Compare percentages; treat as public aggregates."
    )
    hint = (
        "<strong>Key idea:</strong> Subtract percentages, trace hosts through "
        "the chain, and never turn a table into blame."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (gap, order_raw, pick_raw),
            ("Coverage gap (points)", "Why faster growth", "Fair reading"),
            field_types=("number", "order", "pick"),
            field_options=(None, order_bank, pick_bank),
            field_pick_counts=(None, None, pick_count),
            format_hint="Gap, three-step order, then two fair readings.",
        ),
    )


@_u22_variant("infectious_disease", "ms", "difficult", "route_pick_then_break_order_then_abx_zero")
def _infectious_disease_difficult_ms_route_pick_then_break_order_then_abx_zero():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Droplets from a cough or sneeze",
            "Contact with a shared surface",
        ),
        (
            "A rumour posted online",
            "The phase of the Moon",
        ),
        2,
    )
    order_raw, order_bank = _u22_order_field(
        (
            "Identify the route the pathogen uses",
            "Choose a control that blocks that route",
            "Check whether the new-case count slows",
        ),
        ("Give antibiotics to every host with a virus",),
    )
    question = (
        "<p>A fictional epidemiology worksheet lists possible transmission routes "
        "for a viral infection.</p>"
        "<p>(i) Select the two genuine routes.</p>"
        "<p>(ii) Using a route from (i), order the steps for breaking the chain.</p>"
        "<p>(iii) The infection is viral: enter how many of its cases antibiotics "
        "would treat.</p>"
    )
    solution = (
        "(i) Droplets; contact with a surface.<br>"
        "(ii) <strong>identify route → block it → check the count</strong><br>"
        "(iii) <strong>0</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Real routes carry pathogens; block the "
        "route; antibiotics do nothing for a virus."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pick_raw, order_raw, 0),
            ("Genuine routes", "Breaking the chain", "Viral cases treated by antibiotics"),
            field_types=("pick", "order", "number"),
            field_options=(pick_bank, order_bank, None),
            field_pick_counts=(pick_count, None, None),
            format_hint="Two routes, three steps, then 0.",
        ),
    )


INFECTIOUS_DISEASE_MS_POOLS = {
    "foundational": [
        _infectious_disease_foundational_ms_double_count_then_chain_order,
        _infectious_disease_foundational_ms_chain_letter_then_break_mcq,
        _infectious_disease_foundational_ms_pathogen_pick_then_virus_word,
    ],
    "intermediate": [
        _infectious_disease_intermediate_ms_coverage_pct_then_vaccine_mcq,
        _infectious_disease_intermediate_ms_series_next_then_hygiene_order,
        _infectious_disease_intermediate_ms_abx_target_then_resist_pick,
    ],
    "difficult": [
        _infectious_disease_difficult_ms_total_cases_then_host_source_mcq_then_word,
        _infectious_disease_difficult_ms_two_group_gap_then_order_then_pick,
        _infectious_disease_difficult_ms_route_pick_then_break_order_then_abx_zero,
    ],
}


# ---------------------------------------------------------------------------
# noninfectious_disease — multi_step (I, D); foundational MS stays — (matrix)
# ---------------------------------------------------------------------------

_NI_MS_I_TABLE_PACKS = (
    {"total": 8, "infectious": 3},
    {"total": 10, "infectious": 4},
    {"total": 6, "infectious": 2},
)


@_u22_variant("noninfectious_disease", "ms", "intermediate", "table_split_then_class_mcq")
def _noninfectious_disease_intermediate_ms_table_split_then_class_mcq():
    pack = random.choice(_NI_MS_I_TABLE_PACKS)
    non = pack["total"] - pack["infectious"]
    correct = "conditions that do not pass from host to host along a route"
    distractors = (
        "illnesses that are always caught from a classmate",
        "conditions the quiz should collect from family histories",
        "diseases that are always caused by a virus",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook table lists {pack['total']} diseases; "
        f"{pack['infectious']} are marked infectious.</p>"
        "<p>(i) Calculate how many are noninfectious.</p>"
        "<p>(ii) The group counted in (i) is defined as</p>"
    )
    solution = (
        f"(i) {pack['total']} − {pack['infectious']} = <strong>{non}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the infectious ones; the remainder "
        "do not spread by a chain of infection."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (non, letter),
            ("Noninfectious count", "Definition"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract, then choose the definition.",
        ),
    )


@_u22_variant("noninfectious_disease", "ms", "intermediate", "cause_order_then_deficiency_word")
def _noninfectious_disease_intermediate_ms_cause_order_then_deficiency_word():
    order_raw, order_bank = _u22_order_field(
        (
            "A nutrient is missing from the diet over a long time",
            "The body cannot carry out a process that needs it",
            "Signs of the deficiency disease appear",
        ),
        ("A pathogen passes along a route to a new host",),
    )
    question = (
        "<p>A fictional history-of-medicine page explains scurvy among sailors "
        "using public records.</p>"
        "<p>(i) Order the chain from missing nutrient to disease.</p>"
        "<p>(ii) Using the chain from (i), write the one-word category for this "
        "kind of noninfectious disease.</p>"
    )
    solution = (
        "(i) <strong>missing nutrient → process fails → signs appear</strong><br>"
        "(ii) <strong>deficiency</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> The chain starts with a gap in the diet, "
        "not with a pathogen."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, "deficiency"),
            ("Chain to disease", "Category"),
            field_types=("order", "keyword"),
            field_options=(order_bank, None),
            format_hint="Order three steps, then one word.",
        ),
    )


@_u22_variant("noninfectious_disease", "ms", "intermediate", "cause_pick_then_count")
def _noninfectious_disease_intermediate_ms_cause_pick_then_count():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Inherited or long-term systemic conditions",
            "Exposure to pollution or an occupational hazard",
            "A missing nutrient over time",
        ),
        (
            "A pathogen travelling along a route",
            "A person's fault, to be ranked in class",
        ),
        3,
    )
    question = (
        "<p>A fictional revision card lists possible causes of disease.</p>"
        "<p>(i) Select the three cause-groups that are noninfectious.</p>"
        "<p>(ii) Enter how many cause-groups you selected in (i).</p>"
    )
    solution = (
        "(i) Inherited/systemic; pollution/occupation; deficiency.<br>"
        "(ii) <strong>3</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Three noninfectious cause-groups; a "
        "pathogen route is the infectious one."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, 3),
            ("Noninfectious cause-groups", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select three, then enter 3.",
        ),
    )


_NI_MS_D_RATE_PACKS = (
    {"cases": 30, "per": 1000, "rate": 3},
    {"cases": 50, "per": 1000, "rate": 5},
    {"cases": 24, "per": 1000, "rate": 2.4},
)


@_u22_variant("noninfectious_disease", "ms", "difficult", "rate_then_exposure_mcq_then_word")
def _noninfectious_disease_difficult_ms_rate_then_exposure_mcq_then_word():
    pack = random.choice(_NI_MS_D_RATE_PACKS)
    rate = pack["rate"]
    correct = "study the exposure with public evidence and workplace controls"
    distractors = (
        "survey pupils about relatives' jobs",
        "treat the workers as sources of infection",
        "ignore it because it is not a virus",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional occupational-health report finds {pack['cases']} cases of "
        f"a lung condition per {pack['per']} workers exposed to a dust hazard.</p>"
        f"<p>(i) Express that as cases per 100 workers.</p>"
        "<p>(ii) Given the rate in (i), the scientific response is to</p>"
        "<p>(iii) Write the one-word category for disease linked to a job.</p>"
    )
    solution = (
        f"(i) {pack['cases']} ÷ 10 = <strong>{rate}</strong> per 100<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>occupational</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Scale the rate, respond with public evidence "
        "and controls, and name the category."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (rate, letter, "occupational"),
            ("Cases per 100", "Scientific response", "Category"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Rate, response, then one word.",
        ),
    )


@_u22_variant("noninfectious_disease", "ms", "difficult", "stigma_order_then_support_pick")
def _noninfectious_disease_difficult_ms_stigma_order_then_support_pick():
    order_raw, order_bank = _u22_order_field(
        (
            "A noninfectious condition is wrongly treated as catching",
            "The person is avoided as if they were a source",
            "Unfair stigma results, with no scientific basis",
        ),
        ("Avoiding them is justified because every illness spreads",),
    )
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Mental illness is a health condition, not a joke",
            "Treatment and support are clinical; this app does not diagnose",
        ),
        (
            "Pupils must compare whose relative is ill",
            "Slogans replace care",
        ),
        2,
    )
    question = (
        "<p>A fictional case study describes a character with a long-term "
        "condition that is not catching.</p>"
        "<p>(i) Order how a wrong classification leads to stigma.</p>"
        "<p>(ii) Using the outcome from (i), select the two statements the "
        "lesson uses to counter stigma around health conditions.</p>"
    )
    solution = (
        "(i) <strong>wrong classification → avoidance → stigma</strong><br>"
        "(ii) Condition not a joke; support is clinical."
    )
    hint = (
        "<strong>Key idea:</strong> A wrong model produces stigma; correct "
        "classification and signposted support counter it."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Path to stigma", "Countering stigma"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order three steps, then select two statements.",
        ),
    )


_NI_MS_D_SORT_PACKS = (
    {"items": ("scurvy", "a cold", "an inherited blood condition", "dust-linked lung disease"), "non": 3},
    {"items": ("rickets", "flu", "an inherited eye condition", "asbestos-linked lung disease"), "non": 3},
    {"items": ("a vitamin deficiency", "chickenpox", "an inherited heart condition", "noise-linked hearing loss"), "non": 3},
)


@_u22_variant("noninfectious_disease", "ms", "difficult", "sort_count_then_infectious_mcq_then_word")
def _noninfectious_disease_difficult_ms_sort_count_then_infectious_mcq_then_word():
    pack = random.choice(_NI_MS_D_SORT_PACKS)
    items = pack["items"]
    correct = items[1]
    distractors = (items[0], items[2], items[3])
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        "<p>A fictional exam question lists four public textbook examples: "
        f"{items[0]}, {items[1]}, {items[2]}, {items[3]}.</p>"
        "<p>(i) Enter how many of the four are noninfectious.</p>"
        "<p>(ii) Using your sort from (i), which one <em>is</em> infectious?</p>"
        "<p>(iii) Write the one-word term for a condition passed on through "
        "genetic information.</p>"
    )
    solution = (
        f"(i) <strong>{pack['non']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>inherited</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Only one example passes host to host; the "
        "others are deficiency, inherited or environmental."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pack["non"], letter, "inherited"),
            ("Noninfectious count", "The infectious one", "Genetic term"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Count, choose, then one word.",
        ),
    )


# noninfectious_disease — situational_multi_step (F, I, D)

_NI_SMS_F_CLINIC_PACKS = (
    {"place": "fictional village clinic", "seen": 12, "catching": 5},
    {"place": "fictional school nurse's log", "seen": 10, "catching": 4},
    {"place": "fictional ship's sick bay", "seen": 8, "catching": 3},
)


@_u22_variant("noninfectious_disease", "sms", "foundational", "clinic_log_then_split_mcq")
def _noninfectious_disease_foundational_sms_clinic_log_then_split_mcq():
    pack = random.choice(_NI_SMS_F_CLINIC_PACKS)
    non = pack["seen"] - pack["catching"]
    correct = "they do not pass from host to host, so no chain of infection applies"
    distractors = (
        "they must be listed by name in the quiz",
        "they are always caused by a virus",
        "they are always the person's fault",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['place']} records {pack['seen']} anonymised visits in a "
        f"week; {pack['catching']} were infectious illnesses.</p>"
        "<p>(i) Enter how many visits were for noninfectious conditions.</p>"
        "<p>(ii) For the visits counted in (i),</p>"
    )
    solution = (
        f"(i) {pack['seen']} − {pack['catching']} = <strong>{non}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the catching ones; the rest have "
        "no source–route–host chain."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (non, letter),
            ("Noninfectious visits", "What that means"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract, then choose the meaning.",
        ),
    )


_NI_SMS_F_SAILOR_PACKS = (
    {"voyage": "fictional 18th-century voyage", "months": 4, "nutrient": "vitamin C"},
    {"voyage": "fictional polar expedition", "months": 6, "nutrient": "vitamin C"},
    {"voyage": "fictional trading ship", "months": 5, "nutrient": "vitamin C"},
)


@_u22_variant("noninfectious_disease", "sms", "foundational", "voyage_months_then_cause_pick")
def _noninfectious_disease_foundational_sms_voyage_months_then_cause_pick():
    pack = random.choice(_NI_SMS_F_SAILOR_PACKS)
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            f"The crew's diet lacked {pack['nutrient']} for months",
            "Scurvy is a deficiency disease, not an infection",
        ),
        (
            "A pathogen spread from the cook to the crew",
            "The sailors should be ranked by who was weakest",
        ),
        2,
    )
    question = (
        f"<p>A textbook tells the story of a {pack['voyage']} lasting "
        f"{pack['months']} months with no fresh fruit or vegetables; many of the "
        "crew developed scurvy.</p>"
        "<p>(i) Enter the number of months without fresh food.</p>"
        "<p>(ii) Using that time span from (i), select the two statements that "
        "explain the scurvy.</p>"
    )
    solution = (
        f"(i) <strong>{pack['months']}</strong> months<br>"
        f"(ii) Missing {pack['nutrient']}; deficiency, not infection."
    )
    hint = (
        "<strong>Key idea:</strong> A long gap in the diet, not a pathogen, "
        "explains a deficiency disease."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["months"], pick_raw),
            ("Months without fresh food", "Explanation"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Months, then two statements.",
        ),
    )


@_u22_variant("noninfectious_disease", "sms", "foundational", "story_support_order_then_word")
def _noninfectious_disease_foundational_sms_story_support_order_then_word():
    order_raw, order_bank = _u22_order_field(
        (
            "Recognise mental illness as a health condition",
            "Point the character to a trusted adult or qualified help",
        ),
        ("Publish the character's story as a class joke",),
    )
    question = (
        "<p>In a fictional short story, a character is living with a mental "
        "illness and is supported by a school counsellor.</p>"
        "<p>(i) Order how the story models a good response.</p>"
        "<p>(ii) Using the second step from (i), write the one-word term for "
        "help and treatment around a condition.</p>"
    )
    solution = (
        "(i) <strong>recognise → point to help</strong><br>"
        "(ii) <strong>support</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Recognise the condition, then signpost — "
        "the app teaches categories and does not diagnose."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, "support"),
            ("Good response", "Term"),
            field_types=("order", "keyword"),
            field_options=(order_bank, None),
            format_hint="Order two steps, then one word.",
        ),
    )


_NI_SMS_I_AIR_PACKS = (
    {"city": "fictional industrial city", "high": 60, "low": 40, "per": 10000},
    {"city": "fictional port city", "high": 75, "low": 45, "per": 10000},
    {"city": "fictional mining town", "high": 90, "low": 50, "per": 10000},
)


@_u22_variant("noninfectious_disease", "sms", "intermediate", "air_zones_then_link_mcq_then_word")
def _noninfectious_disease_intermediate_sms_air_zones_then_link_mcq_then_word():
    pack = random.choice(_NI_SMS_I_AIR_PACKS)
    diff = pack["high"] - pack["low"]
    correct = "the exposure is linked to disease in public evidence, so controls are worth studying"
    distractors = (
        "everyone in the high zone must be interviewed about relatives",
        "the difference proves a virus is spreading",
        "the high zone's residents are to blame",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A public-health map of a {pack['city']} gives {pack['high']} "
        f"breathing-condition cases per {pack['per']} people in a high-pollution "
        f"zone and {pack['low']} per {pack['per']} in a low-pollution zone.</p>"
        "<p>(i) Calculate the difference in cases per "
        f"{pack['per']}.</p>"
        "<p>(ii) Given the difference in (i), a fair reading is that</p>"
        "<p>(iii) Write the one-word environmental cause-group named here.</p>"
    )
    solution = (
        f"(i) {pack['high']} − {pack['low']} = <strong>{diff}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>pollution</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the rates, read the link as public "
        "evidence, and name the cause-group."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (diff, letter, "pollution"),
            (f"Difference per {pack['per']}", "Fair reading", "Cause-group"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Difference, reading, then one word.",
        ),
    )


_NI_SMS_I_CASE_PACKS = (
    {"who": "Sam", "condition": "a long-term inherited condition"},
    {"who": "Riley", "condition": "a long-term systemic condition"},
    {"who": "Casey", "condition": "an inherited condition"},
)


@_u22_variant("noninfectious_disease", "sms", "intermediate", "case_pick_then_response_order")
def _noninfectious_disease_intermediate_sms_case_pick_then_response_order():
    pack = random.choice(_NI_SMS_I_CASE_PACKS)
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            f"{pack['who']}'s condition is noninfectious",
            f"{pack['who']} is not a source of infection for classmates",
        ),
        (
            f"Classmates should avoid {pack['who']} as if it were a cold",
            f"{pack['who']}'s medical file should be shared in the quiz",
        ),
        2,
    )
    order_raw, order_bank = _u22_order_field(
        (
            "Classify the condition correctly",
            "Treat the person normally, without stigma",
            "Leave treatment to qualified people",
        ),
        ("Rank the class by who is healthiest",),
    )
    question = (
        f"<p>In a fictional case, {pack['who']} has {pack['condition']} and joins "
        "a new school.</p>"
        "<p>(i) Select the two scientifically correct statements.</p>"
        "<p>(ii) Using the classification from (i), order the fair response.</p>"
    )
    solution = (
        "(i) Noninfectious; not a source of infection.<br>"
        "(ii) <strong>classify → no stigma → qualified treatment</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Classify first; a noninfectious condition "
        "never makes someone a source."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, order_raw),
            ("Correct statements", "Fair response"),
            field_types=("pick", "order"),
            field_options=(pick_bank, order_bank),
            field_pick_counts=(pick_count, None),
            format_hint="Two statements, then order three steps.",
        ),
    )


_NI_SMS_I_DEF_PACKS = (
    {"region": "fictional region", "before": 200, "after": 40, "fix": "adding iodine to salt"},
    {"region": "fictional province", "before": 150, "after": 30, "fix": "fortifying flour with a vitamin"},
    {"region": "fictional island", "before": 100, "after": 25, "fix": "supplying fresh fruit"},
)


@_u22_variant("noninfectious_disease", "sms", "intermediate", "fortify_drop_then_type_mcq")
def _noninfectious_disease_intermediate_sms_fortify_drop_then_type_mcq():
    pack = random.choice(_NI_SMS_I_DEF_PACKS)
    drop = pack["before"] - pack["after"]
    correct = "a deficiency disease, because supplying the nutrient reduced cases"
    distractors = (
        "an infectious disease, because cases fell",
        "an inherited condition, because it was in one region",
        "a mystery that needs each family's diet log",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A public-health record from a {pack['region']} shows yearly cases "
        f"falling from {pack['before']} to {pack['after']} after {pack['fix']}.</p>"
        "<p>(i) Calculate the fall in yearly cases.</p>"
        "<p>(ii) The fall in (i) suggests the condition was</p>"
    )
    solution = (
        f"(i) {pack['before']} − {pack['after']} = <strong>{drop}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> If supplying a nutrient cuts cases, the "
        "cause was a nutrient gap."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (drop, letter),
            ("Fall in cases", "Type of condition"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract, then choose the type.",
        ),
    )


_NI_SMS_D_FACTORY_PACKS = (
    {"factory": "fictional textile mill", "exposed": 400, "cases": 20, "unexposed": 400, "ucases": 4},
    {"factory": "fictional quarry", "exposed": 250, "cases": 15, "unexposed": 250, "ucases": 3},
    {"factory": "fictional shipyard", "exposed": 500, "cases": 30, "unexposed": 500, "ucases": 5},
)


@_u22_variant("noninfectious_disease", "sms", "difficult", "factory_ratio_then_control_order_then_pick")
def _noninfectious_disease_difficult_sms_factory_ratio_then_control_order_then_pick():
    pack = random.choice(_NI_SMS_D_FACTORY_PACKS)
    ratio = pack["cases"] // pack["ucases"]
    order_raw, order_bank = _u22_order_field(
        (
            "Compare the exposed and unexposed groups",
            "Identify the workplace exposure as a likely cause",
            "Introduce controls such as ventilation and protective equipment",
        ),
        ("Publish the names of the workers who fell ill",),
    )
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Both groups are the same size, so counts can be compared",
            "The condition is occupational, not infectious",
        ),
        (
            "The workers caught it from each other",
            "The bigger number proves the workers were careless",
        ),
        2,
    )
    question = (
        f"<p>A fictional occupational-health study of a {pack['factory']} compares "
        f"{pack['exposed']} exposed workers ({pack['cases']} cases of a lung "
        f"condition) with {pack['unexposed']} unexposed office staff "
        f"({pack['ucases']} cases).</p>"
        "<p>(i) How many times higher is the exposed count?</p>"
        "<p>(ii) Using the comparison from (i), order the scientific response.</p>"
        "<p>(iii) Select the two valid readings of the study.</p>"
    )
    solution = (
        f"(i) {pack['cases']} ÷ {pack['ucases']} = <strong>{ratio}</strong> times<br>"
        "(ii) <strong>compare → identify exposure → introduce controls</strong><br>"
        "(iii) Equal groups; occupational not infectious."
    )
    hint = (
        "<strong>Key idea:</strong> Divide the counts, follow compare–identify–"
        "control, and keep the reading occupational."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (ratio, order_raw, pick_raw),
            ("Times higher", "Scientific response", "Valid readings"),
            field_types=("number", "order", "pick"),
            field_options=(None, order_bank, pick_bank),
            field_pick_counts=(None, None, pick_count),
            format_hint="Ratio, three steps, then two readings.",
        ),
    )


_NI_SMS_D_TWIN_PACKS = (
    {"study": "fictional family-history study", "families": 50, "affected": 10},
    {"study": "fictional population registry", "families": 80, "affected": 20},
    {"study": "fictional genetics teaching dataset", "families": 40, "affected": 10},
)


@_u22_variant("noninfectious_disease", "sms", "difficult", "registry_pct_then_inherited_mcq_then_word")
def _noninfectious_disease_difficult_sms_registry_pct_then_inherited_mcq_then_word():
    pack = random.choice(_NI_SMS_D_TWIN_PACKS)
    pct = _pct(pack["affected"], pack["families"])
    correct = "an inherited pattern, taught with public examples, not a family survey"
    distractors = (
        "an infection passed between relatives",
        "a reason to ask pupils about their own families",
        "a deficiency caused by one region's diet",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} reports that in {pack['affected']} of "
        f"{pack['families']} anonymised families, a condition appears across "
        "generations.</p>"
        "<p>(i) Calculate that as a whole-number percentage.</p>"
        "<p>(ii) The pattern in (i) suggests</p>"
        "<p>(iii) Write the one-word term for information passed from parents "
        "to children that can carry such a condition.</p>"
    )
    solution = (
        f"(i) {pack['affected']} ÷ {pack['families']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>genetic</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> A cross-generation pattern in public data "
        "points to inheritance — never to a survey of the class."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pct, letter, "genetic"),
            ("Percentage of families", "Pattern suggests", "Information term"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Percentage, reading, then one word.",
        ),
    )


@_u22_variant("noninfectious_disease", "sms", "difficult", "campaign_pick_then_support_order")
def _noninfectious_disease_difficult_sms_campaign_pick_then_support_order():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Mental illness is a health condition that can be supported",
            "Public campaigns reduce stigma without collecting personal files",
        ),
        (
            "The campaign should rank schools by how many pupils are ill",
            "Mental illness is only a joke in a group chat",
        ),
        2,
    )
    order_raw, order_bank = _u22_order_field(
        (
            "Recognise the condition as real",
            "Signpost a trusted adult or qualified service",
            "Leave diagnosis and treatment to clinicians",
        ),
        ("Store who attended support sessions in the app",),
    )
    question = (
        "<p>A fictional national campaign about mental health runs posters in "
        "schools and public spaces.</p>"
        "<p>(i) Select the two statements that match the campaign's scientific aims.</p>"
        "<p>(ii) Using the first aim from (i), order how a school should respond "
        "when a fictional pupil in the campaign film needs help.</p>"
    )
    solution = (
        "(i) A supportable condition; stigma reduced without files.<br>"
        "(ii) <strong>recognise → signpost → clinicians treat</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Recognise, signpost, and leave diagnosis to "
        "qualified people — the app never records who attends."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, order_raw),
            ("Campaign aims", "School response"),
            field_types=("pick", "order"),
            field_options=(pick_bank, order_bank),
            field_pick_counts=(pick_count, None),
            format_hint="Two aims, then order three steps.",
        ),
    )


NONINFECTIOUS_DISEASE_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _noninfectious_disease_intermediate_ms_table_split_then_class_mcq,
        _noninfectious_disease_intermediate_ms_cause_order_then_deficiency_word,
        _noninfectious_disease_intermediate_ms_cause_pick_then_count,
    ],
    "difficult": [
        _noninfectious_disease_difficult_ms_rate_then_exposure_mcq_then_word,
        _noninfectious_disease_difficult_ms_stigma_order_then_support_pick,
        _noninfectious_disease_difficult_ms_sort_count_then_infectious_mcq_then_word,
    ],
}

NONINFECTIOUS_DISEASE_SMS_POOLS = {
    "foundational": [
        _noninfectious_disease_foundational_sms_clinic_log_then_split_mcq,
        _noninfectious_disease_foundational_sms_voyage_months_then_cause_pick,
        _noninfectious_disease_foundational_sms_story_support_order_then_word,
    ],
    "intermediate": [
        _noninfectious_disease_intermediate_sms_air_zones_then_link_mcq_then_word,
        _noninfectious_disease_intermediate_sms_case_pick_then_response_order,
        _noninfectious_disease_intermediate_sms_fortify_drop_then_type_mcq,
    ],
    "difficult": [
        _noninfectious_disease_difficult_sms_factory_ratio_then_control_order_then_pick,
        _noninfectious_disease_difficult_sms_registry_pct_then_inherited_mcq_then_word,
        _noninfectious_disease_difficult_sms_campaign_pick_then_support_order,
    ],
}


# ---------------------------------------------------------------------------
# dependence_addiction — multi_step (I, D); foundational MS stays — (matrix)
# ---------------------------------------------------------------------------

_DA_MS_I_CASEBOOK_PACKS = (
    {"cases": 20, "substance": 12},
    {"cases": 25, "substance": 10},
    {"cases": 30, "substance": 18},
)


@_u22_variant("dependence_addiction", "ms", "intermediate", "casebook_split_then_definition_mcq")
def _dependence_addiction_intermediate_ms_casebook_split_then_definition_mcq():
    pack = random.choice(_DA_MS_I_CASEBOOK_PACKS)
    behav = pack["cases"] - pack["substance"]
    correct = "finding it very hard to stop even when harm is clear"
    distractors = (
        "enjoying something once",
        "a list of what each pupil uses",
        "a popularity score for the class",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook casebook describes {pack['cases']} anonymised "
        f"cases of dependence; {pack['substance']} involve a substance.</p>"
        "<p>(i) Calculate how many cases are behavioural.</p>"
        "<p>(ii) Both groups counted in (i) share one definition: dependence means</p>"
    )
    solution = (
        f"(i) {pack['cases']} − {pack['substance']} = <strong>{behav}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the substance cases; both kinds "
        "share the hard-to-stop-despite-harm definition."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (behav, letter),
            ("Behavioural cases", "Dependence means"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract, then choose the definition.",
        ),
    )


@_u22_variant("dependence_addiction", "ms", "intermediate", "risk_order_then_kind_word")
def _dependence_addiction_intermediate_ms_risk_order_then_kind_word():
    order_raw, order_bank = _u22_order_field(
        (
            "Marketing and easy availability raise exposure",
            "Repeated use becomes a pattern that is hard to stop",
            "Harm to health, money, learning or relationships appears",
        ),
        ("The quiz asks who in the class felt pressure",),
    )
    question = (
        "<p>A fictional public-health diagram traces how dependence on a drug "
        "can develop.</p>"
        "<p>(i) Order the chain from exposure to harm.</p>"
        "<p>(ii) Using the drug in the chain from (i), write the one-word kind of "
        "dependence this is (substance or behavioural).</p>"
    )
    solution = (
        "(i) <strong>exposure → hard-to-stop pattern → harm</strong><br>"
        "(ii) <strong>substance</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Exposure comes first; a chemical makes it "
        "substance dependence."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, "substance"),
            ("Chain to harm", "Kind of dependence"),
            field_types=("order", "keyword"),
            field_options=(order_bank, None),
            format_hint="Order three steps, then one word.",
        ),
    )


@_u22_variant("dependence_addiction", "ms", "intermediate", "harm_pick_then_count")
def _dependence_addiction_intermediate_ms_harm_pick_then_count():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Health can be damaged",
            "Money can be lost",
            "Learning or relationships can suffer",
        ),
        (
            "Enjoyable things can never become harmful",
            "A named classmate should be shamed",
        ),
        3,
    )
    question = (
        "<p>A fictional revision card lists possible consequences of dependence.</p>"
        "<p>(i) Select the three harm categories the lesson names.</p>"
        "<p>(ii) Enter how many harm categories you selected in (i).</p>"
    )
    solution = (
        "(i) Health; money; learning or relationships.<br>"
        "(ii) <strong>3</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Three harm categories; shaming and "
        "'never harmful' are not science."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, 3),
            ("Harm categories", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select three, then enter 3.",
        ),
    )


_DA_MS_D_SUPPORT_PACKS = (
    {"service": "fictional helpline", "contacts": 400, "referred": 100},
    {"service": "fictional youth service", "contacts": 250, "referred": 50},
    {"service": "fictional clinic", "contacts": 300, "referred": 90},
)


@_u22_variant("dependence_addiction", "ms", "difficult", "referral_pct_then_route_mcq_then_word")
def _dependence_addiction_difficult_ms_referral_pct_then_route_mcq_then_word():
    pack = random.choice(_DA_MS_D_SUPPORT_PACKS)
    pct = _pct(pack["referred"], pack["contacts"])
    correct = "a trusted adult or qualified service; this app does not treat dependence"
    distractors = (
        "a class quiz that records what the character uses",
        "a public leaderboard of who stopped fastest",
        "ignoring the harm because the character enjoys it",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['service']} publishes anonymised figures: {pack['referred']} "
        f"of {pack['contacts']} contacts were referred for specialist support.</p>"
        "<p>(i) Calculate the referral rate as a whole-number percentage.</p>"
        "<p>(ii) The route counted in (i) shows that help for a fictional "
        "character who wants to stop is</p>"
        "<p>(iii) Write the one-word term for pointing someone to that help.</p>"
    )
    solution = (
        f"(i) {pack['referred']} ÷ {pack['contacts']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>signpost</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentages describe a service; help is "
        "signposted to qualified people, never collected here."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pct, letter, "signpost"),
            ("Referral rate (%)", "Help route", "Term"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Percentage, route, then one word.",
        ),
    )


@_u22_variant("dependence_addiction", "ms", "difficult", "sort_pick_then_shared_order")
def _dependence_addiction_difficult_ms_sort_pick_then_shared_order():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Repeated gaming that harms sleep and learning yet cannot be stopped",
            "Repeated gambling that harms money yet cannot be stopped",
        ),
        (
            "Continued use of a drug despite clear harm",
            "Enjoying a film once at the weekend",
        ),
        2,
    )
    order_raw, order_bank = _u22_order_field(
        (
            "A pleasure or relief is repeated",
            "Stopping becomes very hard",
            "Harm continues despite wanting to stop",
        ),
        ("The person is shamed in front of the class",),
    )
    question = (
        "<p>A fictional exam question lists four patterns from a textbook.</p>"
        "<p>(i) Select the two <em>behavioural</em> dependence patterns.</p>"
        "<p>(ii) Using the patterns from (i) and the substance pattern in the list, "
        "order the sequence they all share.</p>"
    )
    solution = (
        "(i) Gaming and gambling patterns are behavioural.<br>"
        "(ii) <strong>repeated → hard to stop → harm despite wanting to stop</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Behavioural means an action, not a chemical; "
        "every kind follows the same hard-to-stop sequence."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, order_raw),
            ("Behavioural patterns", "Shared sequence"),
            field_types=("pick", "order"),
            field_options=(pick_bank, order_bank),
            field_pick_counts=(pick_count, None),
            format_hint="Two patterns, then order three steps.",
        ),
    )


_DA_MS_D_FACTOR_PACKS = (
    {"factors": ("easy availability", "heavy marketing", "peer pressure", "a stressful environment"), "n": 4},
    {"factors": ("cheap price", "advertising to young people", "boredom", "family stress"), "n": 4},
    {"factors": ("availability near school", "influencer promotion", "loneliness", "sleep loss"), "n": 4},
)


@_u22_variant("dependence_addiction", "ms", "difficult", "factors_count_then_social_mcq_then_word")
def _dependence_addiction_difficult_ms_factors_count_then_social_mcq_then_word():
    pack = random.choice(_DA_MS_D_FACTOR_PACKS)
    correct = "risk factors that raise the chance of dependence, taught without asking who felt them"
    distractors = (
        "proof that any one person will become dependent",
        "questions the quiz should put to each pupil",
        "reasons to rank classmates by risk",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    factors = pack["factors"]
    question = (
        "<p>A fictional public-health report lists: "
        f"{factors[0]}, {factors[1]}, {factors[2]} and {factors[3]}.</p>"
        "<p>(i) Enter how many risk factors are listed.</p>"
        "<p>(ii) The items counted in (i) are</p>"
        "<p>(iii) Write the one-word term for damage the factors make more likely.</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>harm</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the factors, read them as population "
        "risk, and name the harm they raise."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pack["n"], letter, "harm"),
            ("Risk factors listed", "What they are", "Term"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Count, reading, then one word.",
        ),
    )


# dependence_addiction — situational_multi_step (F, I, D)

_DA_SMS_F_STORY_PACKS = (
    {"who": "Jordan", "hours": 5, "harm": "falls behind in a fictional school project"},
    {"who": "Sam", "hours": 6, "harm": "misses a fictional team training"},
    {"who": "Riley", "hours": 4, "harm": "stops seeing friends in the fictional story"},
)


@_u22_variant("dependence_addiction", "sms", "foundational", "story_hours_then_kind_mcq")
def _dependence_addiction_foundational_sms_story_hours_then_kind_mcq():
    pack = random.choice(_DA_SMS_F_STORY_PACKS)
    correct = "behavioural dependence, because it is a repeated action, not a chemical"
    distractors = (
        "substance dependence, because games are a drug",
        "ordinary pleasure with no harm",
        f"a reason to ask {pack['who']}'s classmates about their own gaming",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional story, {pack['who']} games {pack['hours']} hours every "
        f"night, wants to cut down, cannot, and {pack['harm']}.</p>"
        "<p>(i) Enter the nightly hours in the story.</p>"
        "<p>(ii) Using the pattern behind those hours from (i), the lesson "
        "would classify this as</p>"
    )
    solution = (
        f"(i) <strong>{pack['hours']}</strong> hours<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the number, then ask: action or "
        "chemical? Hard to stop despite harm?"
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["hours"], letter),
            ("Nightly hours", "Classification"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Hours, then choose the kind.",
        ),
    )


_DA_SMS_F_POSTER_PACKS = (
    {"town": "fictional town", "routes": 2},
    {"town": "fictional seaside resort", "routes": 3},
    {"town": "fictional market town", "routes": 2},
)


@_u22_variant("dependence_addiction", "sms", "foundational", "poster_routes_then_help_pick")
def _dependence_addiction_foundational_sms_poster_routes_then_help_pick():
    pack = random.choice(_DA_SMS_F_POSTER_PACKS)
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Support is a trusted adult or qualified service",
            "Dependence can harm health, money, learning or relationships",
        ),
        (
            "The scientific method is to shame a named person",
            "Help should never be signposted",
        ),
        2,
    )
    question = (
        f"<p>A youth centre in a {pack['town']} displays a fictional poster "
        f"listing {pack['routes']} local support routes for anyone worried "
        "about dependence.</p>"
        "<p>(i) Enter the number of support routes on the poster.</p>"
        "<p>(ii) Using the poster's purpose from (i), select the two statements "
        "it agrees with.</p>"
    )
    solution = (
        f"(i) <strong>{pack['routes']}</strong> routes<br>"
        "(ii) Support is qualified help; dependence can cause harm."
    )
    hint = (
        "<strong>Key idea:</strong> A support poster signposts help and names "
        "harm — it never shames."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["routes"], pick_raw),
            ("Support routes", "Poster statements"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count, then two statements.",
        ),
    )


@_u22_variant("dependence_addiction", "sms", "foundational", "cafe_order_then_pleasure_word")
def _dependence_addiction_foundational_sms_cafe_order_then_pleasure_word():
    order_raw, order_bank = _u22_order_field(
        (
            "Enjoying a weekly treat with friends",
            "Needing it daily and feeling unable to stop",
            "Continuing even though money and sleep suffer",
        ),
        ("Confessing the pattern in a class quiz",),
    )
    question = (
        "<p>A fictional comic strip follows a character's visits to a café over "
        "a year.</p>"
        "<p>(i) Order the frames from ordinary enjoyment to dependence.</p>"
        "<p>(ii) Using the first frame from (i), write the one-word term for "
        "enjoyment that is <em>not</em> dependence.</p>"
    )
    solution = (
        "(i) <strong>weekly treat → daily need → harm continues</strong><br>"
        "(ii) <strong>pleasure</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Ordinary pleasure sits at the start; "
        "dependence is when stopping becomes very hard despite harm."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, "pleasure"),
            ("Comic-strip order", "Term"),
            field_types=("order", "keyword"),
            field_options=(order_bank, None),
            format_hint="Order three frames, then one word.",
        ),
    )


_DA_SMS_I_SURVEY_PACKS = (
    {"country": "fictional country", "asked": 2000, "reported": 300},
    {"country": "fictional region", "asked": 1500, "reported": 150},
    {"country": "fictional city", "asked": 1000, "reported": 200},
)


@_u22_variant("dependence_addiction", "sms", "intermediate", "survey_pct_then_reading_mcq_then_word")
def _dependence_addiction_intermediate_sms_survey_pct_then_reading_mcq_then_word():
    pack = random.choice(_DA_SMS_I_SURVEY_PACKS)
    pct = _pct(pack["reported"], pack["asked"])
    correct = "an anonymous aggregate for planning services, not a file on any person"
    distractors = (
        "a list of who should be shamed",
        "proof that every respondent is dependent",
        "a reason to survey the class about their own use",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A public-health agency in a {pack['country']} publishes an anonymous "
        f"survey: {pack['reported']} of {pack['asked']} adults reported a "
        "problematic gambling pattern.</p>"
        "<p>(i) Calculate the share as a whole-number percentage.</p>"
        "<p>(ii) The figure in (i) is</p>"
        "<p>(iii) Write the one-word kind of dependence gambling belongs to "
        "(substance or behavioural).</p>"
    )
    solution = (
        f"(i) {pack['reported']} ÷ {pack['asked']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>behavioural</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentage of a population; used to plan "
        "services; gambling is an action, not a chemical."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pct, letter, "behavioural"),
            ("Share (%)", "What the figure is", "Kind"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Percentage, reading, then one word.",
        ),
    )


_DA_SMS_I_CASE_PACKS = (
    {"who": "Alex", "thing": "a substance", "harm": "money and health"},
    {"who": "Casey", "thing": "a substance", "harm": "sleep and schoolwork"},
    {"who": "Morgan", "thing": "a substance", "harm": "friendships and money"},
)


@_u22_variant("dependence_addiction", "sms", "intermediate", "case_pick_then_response_order")
def _dependence_addiction_intermediate_sms_case_pick_then_response_order():
    pack = random.choice(_DA_SMS_I_CASE_PACKS)
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            f"{pack['who']} keeps using despite harm to {pack['harm']}",
            f"{pack['who']} wants to stop but finds it very hard",
        ),
        (
            f"{pack['who']} enjoys it, so it cannot be harmful",
            f"{pack['who']} should be named and ranked in class",
        ),
        2,
    )
    order_raw, order_bank = _u22_order_field(
        (
            "Recognise the pattern as dependence",
            "Signpost a trusted adult or qualified service",
            "Leave treatment to qualified people",
        ),
        ("Record the use history in the app",),
    )
    question = (
        f"<p>In a fictional case study, {pack['who']} keeps using {pack['thing']} "
        f"although it harms {pack['harm']}, and says stopping feels impossible.</p>"
        "<p>(i) Select the two features that fit the dependence model.</p>"
        "<p>(ii) Using the model from (i), order the response the lesson teaches.</p>"
    )
    solution = (
        "(i) Continued use despite harm; very hard to stop.<br>"
        "(ii) <strong>recognise → signpost → qualified treatment</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Two model features, then recognise–"
        "signpost–treat; no record is kept here."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, order_raw),
            ("Model features", "Response"),
            field_types=("pick", "order"),
            field_options=(pick_bank, order_bank),
            field_pick_counts=(pick_count, None),
            format_hint="Two features, then order three steps.",
        ),
    )


_DA_SMS_I_SHOP_PACKS = (
    {"street": "fictional high street", "before": 2, "after": 6},
    {"street": "fictional shopping centre", "before": 1, "after": 4},
    {"street": "fictional station road", "before": 3, "after": 9},
)


@_u22_variant("dependence_addiction", "sms", "intermediate", "shops_change_then_risk_mcq")
def _dependence_addiction_intermediate_sms_shops_change_then_risk_mcq():
    pack = random.choice(_DA_SMS_I_SHOP_PACKS)
    change = pack["after"] - pack["before"]
    correct = "availability is a risk factor that can raise uptake in an area"
    distractors = (
        "the shops prove which residents are dependent",
        "the count is a reason to survey pupils about visits",
        "availability has no link to dependence",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional council report counts betting shops on a {pack['street']}: "
        f"{pack['before']} five years ago, {pack['after']} now.</p>"
        "<p>(i) Calculate the increase in shops.</p>"
        "<p>(ii) The change in (i) matters to public health because</p>"
    )
    solution = (
        f"(i) {pack['after']} − {pack['before']} = <strong>{change}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract, then link availability to "
        "population risk — not to any named person."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (change, letter),
            ("Increase in shops", "Why it matters"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract, then choose the risk-factor reading.",
        ),
    )


_DA_SMS_D_TRIAL_PACKS = (
    {"programme": "fictional school prevention programme", "with": 500, "with_cases": 25, "without": 500, "without_cases": 50},
    {"programme": "fictional youth outreach scheme", "with": 400, "with_cases": 16, "without": 400, "without_cases": 40},
    {"programme": "fictional community campaign", "with": 600, "with_cases": 30, "without": 600, "without_cases": 60},
)


@_u22_variant("dependence_addiction", "sms", "difficult", "trial_pct_then_caution_pick_then_verdict")
def _dependence_addiction_difficult_sms_trial_pct_then_caution_pick_then_verdict():
    pack = random.choice(_DA_SMS_D_TRIAL_PACKS)
    with_pct = _pct(pack["with_cases"], pack["with"])
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "The two groups might differ in other ways",
            "Self-reported answers may be inaccurate",
        ),
        (
            "The lower figure proves the programme cured everyone",
            "Participants should be named to verify them",
        ),
        2,
    )
    correct = "the programme is associated with fewer cases, but the evidence is not conclusive"
    distractors = (
        "the programme is proven to work for every individual",
        "the programme caused dependence",
        "the groups should be ranked by who was weakest",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['programme']} is evaluated anonymously: {pack['with_cases']} "
        f"of {pack['with']} young people who took part later reported a problematic "
        f"pattern, compared with {pack['without_cases']} of {pack['without']} who "
        "did not take part.</p>"
        "<p>(i) Calculate the percentage among those who took part (whole number).</p>"
        "<p>(ii) Using the comparison from (i), select the two cautions.</p>"
        "<p>(iii) Given the cautions in (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['with_cases']} ÷ {pack['with']} × 100 = <strong>{with_pct}%</strong><br>"
        "(ii) Groups may differ; self-report may be inaccurate.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentage, then design cautions, then an "
        "honest 'associated with' verdict."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (with_pct, pick_raw, letter),
            ("Took part (%)", "Cautions", "Verdict"),
            field_types=("number", "pick", "mcq"),
            field_options=(None, pick_bank, options),
            field_pick_counts=(None, pick_count, None),
            format_hint="Percentage, two cautions, then the verdict.",
        ),
    )


_DA_SMS_D_ADVERT_PACKS = (
    {"product": "an energy-drink brand", "channel": "gaming streams"},
    {"product": "a betting app", "channel": "football highlights"},
    {"product": "a vape brand", "channel": "short-video feeds"},
)


@_u22_variant("dependence_addiction", "sms", "difficult", "advert_order_then_factor_pick_then_word")
def _dependence_addiction_difficult_sms_advert_order_then_factor_pick_then_word():
    pack = random.choice(_DA_SMS_D_ADVERT_PACKS)
    order_raw, order_bank = _u22_order_field(
        (
            f"Marketing on {pack['channel']} raises exposure among young viewers",
            "Repeated use can become a pattern that is hard to stop",
            "Harm to health, money or learning can follow",
        ),
        ("Viewers are asked to confess what they use",),
    )
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Marketing aimed at young people",
            "Easy availability",
        ),
        (
            "A pupil's name on a class list",
            "Enjoyment on its own",
        ),
        2,
    )
    question = (
        f"<p>A fictional media-studies report finds {pack['product']} advertised "
        f"heavily on {pack['channel']} watched mainly by teenagers.</p>"
        "<p>(i) Order the chain the report warns about.</p>"
        "<p>(ii) Using the first link from (i), select the two social risk factors "
        "the lesson names.</p>"
        "<p>(iii) Write the one-word term for damage at the end of the chain.</p>"
    )
    solution = (
        "(i) <strong>marketing exposure → hard-to-stop pattern → harm</strong><br>"
        "(ii) Marketing to young people; availability.<br>"
        "(iii) <strong>harm</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Marketing is exposure; exposure plus "
        "availability are social risk factors; harm ends the chain."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (order_raw, pick_raw, "harm"),
            ("Warning chain", "Social risk factors", "Term"),
            field_types=("order", "pick", "keyword"),
            field_options=(order_bank, pick_bank, None),
            field_pick_counts=(None, pick_count, None),
            format_hint="Order three links, two factors, then one word.",
        ),
    )


@_u22_variant("dependence_addiction", "sms", "difficult", "clinic_pick_then_signpost_mcq")
def _dependence_addiction_difficult_sms_clinic_pick_then_signpost_mcq():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Treatment records stay with the clinic, not in a class quiz",
            "Both substance and behavioural dependence can be treated",
        ),
        (
            "The clinic should publish a leaderboard of recoveries",
            "Only substance dependence is real",
        ),
        2,
    )
    correct = "signpost the service and let qualified staff decide; the app does not diagnose"
    distractors = (
        "type the character's use history into the quiz",
        "compare the character with classmates",
        "tell the character enjoyment means no harm",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        "<p>A fictional documentary follows a specialist clinic that treats "
        "both substance and behavioural dependence.</p>"
        "<p>(i) Select the two statements consistent with the documentary.</p>"
        "<p>(ii) Using the first statement from (i), if a fictional character in "
        "the film wants help, the lesson's response is to</p>"
    )
    solution = (
        "(i) Records stay clinical; both kinds treatable.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Clinical records are clinical; the app "
        "signposts and never diagnoses."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, letter),
            ("Consistent statements", "Response"),
            field_types=("pick", "mcq"),
            field_options=(pick_bank, options),
            field_pick_counts=(pick_count, None),
            format_hint="Two statements, then the response.",
        ),
    )


DEPENDENCE_ADDICTION_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _dependence_addiction_intermediate_ms_casebook_split_then_definition_mcq,
        _dependence_addiction_intermediate_ms_risk_order_then_kind_word,
        _dependence_addiction_intermediate_ms_harm_pick_then_count,
    ],
    "difficult": [
        _dependence_addiction_difficult_ms_referral_pct_then_route_mcq_then_word,
        _dependence_addiction_difficult_ms_sort_pick_then_shared_order,
        _dependence_addiction_difficult_ms_factors_count_then_social_mcq_then_word,
    ],
}

DEPENDENCE_ADDICTION_SMS_POOLS = {
    "foundational": [
        _dependence_addiction_foundational_sms_story_hours_then_kind_mcq,
        _dependence_addiction_foundational_sms_poster_routes_then_help_pick,
        _dependence_addiction_foundational_sms_cafe_order_then_pleasure_word,
    ],
    "intermediate": [
        _dependence_addiction_intermediate_sms_survey_pct_then_reading_mcq_then_word,
        _dependence_addiction_intermediate_sms_case_pick_then_response_order,
        _dependence_addiction_intermediate_sms_shops_change_then_risk_mcq,
    ],
    "difficult": [
        _dependence_addiction_difficult_sms_trial_pct_then_caution_pick_then_verdict,
        _dependence_addiction_difficult_sms_advert_order_then_factor_pick_then_word,
        _dependence_addiction_difficult_sms_clinic_pick_then_signpost_mcq,
    ],
}


# ---------------------------------------------------------------------------
# tobacco — multi_step (I, D); foundational MS stays — (matrix)
# ---------------------------------------------------------------------------

_TB_MS_I_START_PACKS = (
    {"asked": 100, "young": 80},
    {"asked": 200, "young": 170},
    {"asked": 150, "young": 120},
)


@_u22_variant("tobacco", "ms", "intermediate", "start_young_pct_then_risk_mcq")
def _tobacco_intermediate_ms_start_young_pct_then_risk_mcq():
    pack = random.choice(_TB_MS_I_START_PACKS)
    pct = _pct(pack["young"], pack["asked"])
    correct = "starting young raises addiction risk, so prevention targets uptake"
    distractors = (
        "the quiz should record each pupil's age of first use",
        "nicotine is a vitamin for young people",
        "the figure ranks which pupils are most at risk",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook table reports that {pack['young']} of "
        f"{pack['asked']} adult smokers in an anonymous survey started before age 18.</p>"
        "<p>(i) Calculate that as a whole-number percentage.</p>"
        "<p>(ii) The share in (i) supports the public-health idea that</p>"
    )
    solution = (
        f"(i) {pack['young']} ÷ {pack['asked']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentage first; a high share starting "
        "young is why prevention focuses on uptake."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pct, letter),
            ("Started young (%)", "Public-health idea"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Whole-number percentage, then the idea.",
        ),
    )


@_u22_variant("tobacco", "ms", "intermediate", "chain_order_then_nicotine_word")
def _tobacco_intermediate_ms_chain_order_then_nicotine_word():
    order_raw, order_bank = _u22_order_field(
        (
            "Nicotine reaches the brain quickly when inhaled",
            "Repeated use makes stopping very hard",
            "Long-term use is linked to disease and earlier death",
        ),
        ("The quiz records which pupils have tried it",),
    )
    question = (
        "<p>A fictional health-education diagram traces tobacco use from first "
        "puff to long-term harm.</p>"
        "<p>(i) Order the diagram's chain.</p>"
        "<p>(ii) Using the first link from (i), write the one-word name of the "
        "addictive chemical.</p>"
    )
    solution = (
        "(i) <strong>nicotine reaches brain → hard to stop → disease link</strong><br>"
        "(ii) <strong>nicotine</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> The chemical acts first; dependence and "
        "then disease follow."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, "nicotine"),
            ("Chain", "Addictive chemical"),
            field_types=("order", "keyword"),
            field_options=(order_bank, None),
            format_hint="Order three links, then one word.",
        ),
    )


@_u22_variant("tobacco", "ms", "intermediate", "source_pick_then_count")
def _tobacco_intermediate_ms_source_pick_then_count():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "A peer-reviewed study of mortality data",
            "A national public-health statistics table",
        ),
        (
            "A stylish industry advert",
            "An influencer's sponsored post",
        ),
        2,
    )
    question = (
        "<p>A fictional media-literacy worksheet lists four sources about "
        "tobacco and vaping.</p>"
        "<p>(i) Select the two independent scientific sources.</p>"
        "<p>(ii) Enter how many of the four sources are marketing rather than "
        "evidence, using your selection in (i).</p>"
    )
    solution = (
        "(i) Peer-reviewed study; public statistics table.<br>"
        "(ii) <strong>2</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Independent evidence versus marketing; the "
        "rest of the list is the advert count."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, 2),
            ("Independent sources", "Marketing sources"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two, then enter 2.",
        ),
    )


_TB_MS_D_DEATH_PACKS = (
    {"per": 100000, "smokers": 400, "non": 100},
    {"per": 100000, "smokers": 600, "non": 150},
    {"per": 100000, "smokers": 500, "non": 100},
)


@_u22_variant("tobacco", "ms", "difficult", "mortality_ratio_then_reading_mcq_then_word")
def _tobacco_difficult_ms_mortality_ratio_then_reading_mcq_then_word():
    pack = random.choice(_TB_MS_D_DEATH_PACKS)
    ratio = pack["smokers"] // pack["non"]
    correct = "public evidence links tobacco use to disease and earlier death"
    distractors = (
        "each named smoker will certainly die early",
        "the table is a reason to ask who smokes at home",
        "the ratio proves adverts are accurate",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook mortality table gives {pack['smokers']} deaths "
        f"from a lung disease per {pack['per']} smokers and {pack['non']} per "
        f"{pack['per']} non-smokers.</p>"
        "<p>(i) How many times higher is the smokers' rate?</p>"
        "<p>(ii) The ratio in (i) is read as</p>"
        "<p>(iii) Write the one-word public-health aim of reducing uptake.</p>"
    )
    solution = (
        f"(i) {pack['smokers']} ÷ {pack['non']} = <strong>{ratio}</strong> times<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>prevention</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Divide the rates, read them as population "
        "evidence, and name the aim."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (ratio, letter, "prevention"),
            ("Times higher", "Reading", "Aim"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Ratio, reading, then one word.",
        ),
    )


@_u22_variant("tobacco", "ms", "difficult", "vape_pick_then_uncertainty_order")
def _tobacco_difficult_ms_vape_pick_then_uncertainty_order():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Many vapes contain nicotine, so addiction risk remains",
            "Long-term harm from vaping is still uncertain",
        ),
        (
            "Vaping is proven harmless for everyone",
            "Pupils must list devices they have tried",
        ),
        2,
    )
    order_raw, order_bank = _u22_order_field(
        (
            "Note what the evidence does and does not yet show",
            "Keep nicotine's known addiction risk in the picture",
            "Treat 'totally safe' claims as marketing to critique",
        ),
        ("Accept a stylish advert as a health study",),
    )
    question = (
        "<p>A fictional science-magazine article reviews what is known about "
        "vaping.</p>"
        "<p>(i) Select the two statements that match the S2 position.</p>"
        "<p>(ii) Using the uncertainty from (i), order how a scientist should "
        "handle a 'totally safe' advert.</p>"
    )
    solution = (
        "(i) Nicotine risk remains; long-term harm uncertain.<br>"
        "(ii) <strong>note the evidence → keep nicotine risk → critique the claim</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Uncertainty plus a known addictive chemical "
        "means 'safe' claims get critiqued, not copied."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, order_raw),
            ("S2 position", "Handling the advert"),
            field_types=("pick", "order"),
            field_options=(pick_bank, order_bank),
            field_pick_counts=(pick_count, None),
            format_hint="Two statements, then order three steps.",
        ),
    )


_TB_MS_D_POLICY_PACKS = (
    {"policies": ("plain packaging", "a minimum age of sale", "higher prices", "advertising bans"), "n": 4},
    {"policies": ("smoke-free public places", "health warnings on packs", "higher prices", "a minimum age of sale"), "n": 4},
    {"policies": ("advertising bans", "plain packaging", "smoke-free public places", "quit-support services"), "n": 4},
)


@_u22_variant("tobacco", "ms", "difficult", "policy_count_then_aim_mcq_then_word")
def _tobacco_difficult_ms_policy_count_then_aim_mcq_then_word():
    pack = random.choice(_TB_MS_D_POLICY_PACKS)
    p = pack["policies"]
    correct = "reduce uptake and exposure across a population without questioning individuals"
    distractors = (
        "identify which pupils smoke",
        "prove vaping is harmless",
        "replace evidence with a slogan",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional government fact sheet lists: {p[0]}, {p[1]}, {p[2]} "
        f"and {p[3]}.</p>"
        "<p>(i) Enter how many prevention policies are listed.</p>"
        "<p>(ii) Together, the policies counted in (i) aim to</p>"
        "<p>(iii) Write the one-word name of the addictive chemical these "
        "policies are ultimately about.</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>nicotine</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the policies, read their population "
        "aim, and name the chemical behind the dependence."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pack["n"], letter, "nicotine"),
            ("Policies listed", "Aim", "Chemical"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Count, aim, then one word.",
        ),
    )


# tobacco — situational_multi_step (F, I, D)

_TB_SMS_F_ADVERT_PACKS = (
    {"where": "fictional bus shelter", "claims": 3, "product": "a vape"},
    {"where": "fictional music festival", "claims": 2, "product": "a nicotine pouch"},
    {"where": "fictional online game", "claims": 4, "product": "a vape"},
)


@_u22_variant("tobacco", "sms", "foundational", "advert_claims_then_source_mcq")
def _tobacco_foundational_sms_advert_claims_then_source_mcq():
    pack = random.choice(_TB_SMS_F_ADVERT_PACKS)
    correct = "marketing, not independent scientific evidence"
    distractors = (
        "the same as a peer-reviewed study",
        "a reason to ask who has tried the product",
        "a health warning from a doctor",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>At a {pack['where']}, a fictional advert for {pack['product']} makes "
        f"{pack['claims']} bold claims about being 'clean' and 'safe'.</p>"
        "<p>(i) Enter the number of claims on the advert.</p>"
        "<p>(ii) Using the claims from (i), the advert should be treated as</p>"
    )
    solution = (
        f"(i) <strong>{pack['claims']}</strong> claims<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the claims, then remember an advert "
        "is marketing to critique."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["claims"], letter),
            ("Claims on advert", "Treat the advert as"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count, then choose the source type.",
        ),
    )


_TB_SMS_F_CAMPAIGN_PACKS = (
    {"town": "fictional town", "posters": 12},
    {"town": "fictional harbour town", "posters": 8},
    {"town": "fictional hill village", "posters": 6},
)


@_u22_variant("tobacco", "sms", "foundational", "campaign_posters_then_pick")
def _tobacco_foundational_sms_campaign_posters_then_pick():
    pack = random.choice(_TB_SMS_F_CAMPAIGN_PACKS)
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Tobacco use is linked to disease and earlier death in public evidence",
            "Nicotine is addictive",
        ),
        (
            "Tobacco smoke is a health food",
            "The campaign should ask who smokes",
        ),
        2,
    )
    question = (
        f"<p>A health team in a {pack['town']} puts up {pack['posters']} fictional "
        "prevention posters.</p>"
        "<p>(i) Enter the number of posters.</p>"
        "<p>(ii) Using the posters' purpose from (i), select the two facts they "
        "would print.</p>"
    )
    solution = (
        f"(i) <strong>{pack['posters']}</strong> posters<br>"
        "(ii) Disease link; nicotine is addictive."
    )
    hint = (
        "<strong>Key idea:</strong> Prevention posters print public harm "
        "evidence and the addictive chemical — never a question about who smokes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["posters"], pick_raw),
            ("Posters", "Facts printed"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count, then two facts.",
        ),
    )


@_u22_variant("tobacco", "sms", "foundational", "story_order_then_tobacco_word")
def _tobacco_foundational_sms_story_order_then_tobacco_word():
    order_raw, order_bank = _u22_order_field(
        (
            "A fictional character tries a cigarette because of an advert",
            "Nicotine makes stopping harder each week",
            "Years later, public evidence links the habit to disease",
        ),
        ("The class is asked who has tried smoking",),
    )
    question = (
        "<p>A fictional graphic novel used in health lessons follows one "
        "character over twenty years.</p>"
        "<p>(i) Order the three panels the novel uses.</p>"
        "<p>(ii) Using the first panel from (i), write the one-word plant "
        "product the character tried.</p>"
    )
    solution = (
        "(i) <strong>advert → harder to stop → disease link</strong><br>"
        "(ii) <strong>tobacco</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Uptake, then dependence, then long-term "
        "harm — and the product is tobacco."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, "tobacco"),
            ("Panel order", "Product"),
            field_types=("order", "keyword"),
            field_options=(order_bank, None),
            format_hint="Order three panels, then one word.",
        ),
    )


_TB_SMS_I_TREND_PACKS = (
    {"country": "fictional country", "y1": 30, "y2": 15, "years": 20},
    {"country": "fictional republic", "y1": 40, "y2": 24, "years": 25},
    {"country": "fictional island nation", "y1": 25, "y2": 10, "years": 15},
)


@_u22_variant("tobacco", "sms", "intermediate", "trend_drop_then_policy_mcq_then_word")
def _tobacco_intermediate_sms_trend_drop_then_policy_mcq_then_word():
    pack = random.choice(_TB_SMS_I_TREND_PACKS)
    drop = pack["y1"] - pack["y2"]
    correct = "prevention policies such as price rises, advertising bans and age limits"
    distractors = (
        "a survey that asked every pupil whether they smoke",
        "adverts that proved smoking was safe",
        "ranking towns by how many residents smoke",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A public-health chart for a {pack['country']} shows adult smoking "
        f"falling from {pack['y1']}% to {pack['y2']}% over {pack['years']} years.</p>"
        "<p>(i) Calculate the fall in percentage points.</p>"
        "<p>(ii) The fall in (i) is usually credited to</p>"
        "<p>(iii) Write the one-word public-health aim behind those measures.</p>"
    )
    solution = (
        f"(i) {pack['y1']} − {pack['y2']} = <strong>{drop}</strong> points<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>prevention</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract, credit population-level policy, "
        "and name the aim."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (drop, letter, "prevention"),
            ("Fall (points)", "Credited to", "Aim"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Fall, policy, then one word.",
        ),
    )


_TB_SMS_I_CASE_PACKS = (
    {"who": "Alex", "hook": "a sporty vape advert"},
    {"who": "Jordan", "hook": "a celebrity-endorsed vape"},
    {"who": "Casey", "hook": "a 'natural' tobacco brand advert"},
)


@_u22_variant("tobacco", "sms", "intermediate", "case_pick_then_reply_order")
def _tobacco_intermediate_sms_case_pick_then_reply_order():
    pack = random.choice(_TB_SMS_I_CASE_PACKS)
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Sporty or glamorous branding is not evidence of safety",
            "The product can still contain addictive nicotine",
        ),
        (
            f"Ask {pack['who']} what they use",
            "The advert must be true because it looks professional",
        ),
        2,
    )
    order_raw, order_bank = _u22_order_field(
        (
            "Identify the source as marketing",
            "Look for independent evidence instead",
            "Explain the addiction risk from nicotine",
        ),
        ("Store the character's smoking status",),
    )
    question = (
        f"<p>In a fictional case, {pack['who']} is impressed by {pack['hook']} and "
        "believes the product is harmless.</p>"
        "<p>(i) Select the two scientific replies.</p>"
        "<p>(ii) Using the first reply from (i), order how the lesson would "
        "respond.</p>"
    )
    solution = (
        "(i) Branding is not evidence; nicotine can still addict.<br>"
        "(ii) <strong>identify marketing → find evidence → explain nicotine risk</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Branding is marketing; evidence comes from "
        "independent sources; nicotine is the risk."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, order_raw),
            ("Scientific replies", "Lesson response"),
            field_types=("pick", "order"),
            field_options=(pick_bank, order_bank),
            field_pick_counts=(pick_count, None),
            format_hint="Two replies, then order three steps.",
        ),
    )


_TB_SMS_I_SHARED_PACKS = (
    {"place": "fictional café", "before": 20, "after": 4},
    {"place": "fictional office", "before": 30, "after": 6},
    {"place": "fictional taxi fleet", "before": 15, "after": 3},
)


@_u22_variant("tobacco", "sms", "intermediate", "smokefree_drop_then_exposure_mcq")
def _tobacco_intermediate_sms_smokefree_drop_then_exposure_mcq():
    pack = random.choice(_TB_SMS_I_SHARED_PACKS)
    ratio = pack["before"] // pack["after"]
    correct = "smoke in a shared space exposes others, so smoke-free rules protect them"
    distractors = (
        "staff should be interviewed about who smokes at home",
        "the drop proves vaping is harmless",
        "second-hand smoke is a health food",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional air-quality study in a {pack['place']} measures an "
        f"indoor smoke indicator of {pack['before']} units before a smoke-free "
        f"rule and {pack['after']} units after.</p>"
        "<p>(i) How many times lower is the reading after the rule?</p>"
        "<p>(ii) The change in (i) illustrates that</p>"
    )
    solution = (
        f"(i) {pack['before']} ÷ {pack['after']} = <strong>{ratio}</strong> times<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Divide the readings, then read it as a "
        "public exposure idea, not a household interrogation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (ratio, letter),
            ("Times lower", "What it illustrates"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Ratio, then the exposure idea.",
        ),
    )


_TB_SMS_D_STUDY_PACKS = (
    {"study": "fictional national study", "quit_support": 1000, "quit_ok": 250, "alone": 1000, "alone_ok": 50},
    {"study": "fictional health-service trial", "quit_support": 800, "quit_ok": 160, "alone": 800, "alone_ok": 40},
    {"study": "fictional university study", "quit_support": 500, "quit_ok": 150, "alone": 500, "alone_ok": 25},
)


@_u22_variant("tobacco", "sms", "difficult", "quit_ratio_then_caution_pick_then_verdict")
def _tobacco_difficult_sms_quit_ratio_then_caution_pick_then_verdict():
    pack = random.choice(_TB_SMS_D_STUDY_PACKS)
    ratio = pack["quit_ok"] // pack["alone_ok"]
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "People who chose support may differ from those who did not",
            "Quitting was self-reported, so some answers may be wrong",
        ),
        (
            "The bigger number proves support works for every person",
            "Participants should be named to check them",
        ),
        2,
    )
    correct = "support is associated with more quitting, but the design limits how sure we can be"
    distractors = (
        "support is proven to work for every individual",
        "nicotine is not addictive after all",
        "the study should have asked pupils who smokes",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} reports anonymised results: {pack['quit_ok']} of "
        f"{pack['quit_support']} smokers who used a quit-support service had "
        f"stopped a year later, versus {pack['alone_ok']} of {pack['alone']} who "
        "tried alone.</p>"
        "<p>(i) How many times more quitters were there with support?</p>"
        "<p>(ii) Using the comparison from (i), select the two cautions.</p>"
        "<p>(iii) Given the cautions in (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['quit_ok']} ÷ {pack['alone_ok']} = <strong>{ratio}</strong> times<br>"
        "(ii) Groups may differ; self-report.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Divide, then judge the design before "
        "turning 'more' into 'proven'."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (ratio, pick_raw, letter),
            ("Times more quitters", "Cautions", "Verdict"),
            field_types=("number", "pick", "mcq"),
            field_options=(None, pick_bank, options),
            field_pick_counts=(None, pick_count, None),
            format_hint="Ratio, two cautions, then the verdict.",
        ),
    )


_TB_SMS_D_MARKET_PACKS = (
    {"company": "a fictional vape company", "spend": 40, "unit": "million", "claim": "'99% safer than smoking'"},
    {"company": "a fictional tobacco firm", "spend": 60, "unit": "million", "claim": "'a lifestyle choice'"},
    {"company": "a fictional nicotine-pouch brand", "spend": 25, "unit": "million", "claim": "'tobacco-free and clean'"},
)


@_u22_variant("tobacco", "sms", "difficult", "marketing_spend_then_order_then_word")
def _tobacco_difficult_sms_marketing_spend_then_order_then_word():
    pack = random.choice(_TB_SMS_D_MARKET_PACKS)
    doubled = pack["spend"] * 2
    order_raw, order_bank = _u22_order_field(
        (
            "Ask who paid for the message",
            "Check the claim against independent evidence",
            "Keep the known nicotine addiction risk in view",
        ),
        ("Accept the claim because the budget is large",),
    )
    question = (
        f"<p>A fictional investigative report says {pack['company']} spent "
        f"{pack['spend']} {pack['unit']} on marketing last year, doubling its "
        f"budget, with the slogan {pack['claim']}.</p>"
        f"<p>(i) Enter this year's budget in {pack['unit']}s if it doubled again.</p>"
        "<p>(ii) The spending in (i) is a reason to order these critical steps.</p>"
        "<p>(iii) Write the one-word term for messages designed to sell rather "
        "than to inform.</p>"
    )
    solution = (
        f"(i) {pack['spend']} × 2 = <strong>{doubled}</strong> {pack['unit']}<br>"
        "(ii) <strong>who paid → check evidence → keep nicotine risk</strong><br>"
        "(iii) <strong>marketing</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Double the budget, then critique the source "
        "before the claim — a big budget is not evidence."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (doubled, order_raw, "marketing"),
            (f"Budget ({pack['unit']}s)", "Critical steps", "Term"),
            field_types=("number", "order", "keyword"),
            field_options=(None, order_bank, None),
            format_hint="Doubled budget, three steps, then one word.",
        ),
    )


@_u22_variant("tobacco", "sms", "difficult", "policy_pick_then_uncertainty_mcq")
def _tobacco_difficult_sms_policy_pick_then_uncertainty_mcq():
    pick_raw, pick_bank, pick_count = _u22_pick_field(
        (
            "Age limits and price rises reduce uptake across a population",
            "Prevention does not require asking individuals whether they use",
        ),
        (
            "Schools should publish which pupils vape",
            "Vaping is proven harmless so no policy is needed",
        ),
        2,
    )
    correct = "scientists do not yet have the full long-term picture; nicotine can still addict"
    distractors = (
        "vaping is proven safer than water",
        "adverts settle the question",
        "pupils should list devices they have tried",
    )
    options, letter = _u22_mcq_field(correct, distractors)
    question = (
        "<p>A fictional parliamentary committee hears evidence on youth vaping "
        "and considers new rules.</p>"
        "<p>(i) Select the two statements a public-health witness would make.</p>"
        "<p>(ii) Using the second statement from (i), the witness's honest "
        "position on long-term vaping harm is that</p>"
    )
    solution = (
        "(i) Population policies reduce uptake; no individual questioning.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Policy works at population level, and the "
        "honest position keeps both uncertainty and nicotine risk."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, letter),
            ("Witness statements", "Position on long-term harm"),
            field_types=("pick", "mcq"),
            field_options=(pick_bank, options),
            field_pick_counts=(pick_count, None),
            format_hint="Two statements, then the position.",
        ),
    )


TOBACCO_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _tobacco_intermediate_ms_start_young_pct_then_risk_mcq,
        _tobacco_intermediate_ms_chain_order_then_nicotine_word,
        _tobacco_intermediate_ms_source_pick_then_count,
    ],
    "difficult": [
        _tobacco_difficult_ms_mortality_ratio_then_reading_mcq_then_word,
        _tobacco_difficult_ms_vape_pick_then_uncertainty_order,
        _tobacco_difficult_ms_policy_count_then_aim_mcq_then_word,
    ],
}

TOBACCO_SMS_POOLS = {
    "foundational": [
        _tobacco_foundational_sms_advert_claims_then_source_mcq,
        _tobacco_foundational_sms_campaign_posters_then_pick,
        _tobacco_foundational_sms_story_order_then_tobacco_word,
    ],
    "intermediate": [
        _tobacco_intermediate_sms_trend_drop_then_policy_mcq_then_word,
        _tobacco_intermediate_sms_case_pick_then_reply_order,
        _tobacco_intermediate_sms_smokefree_drop_then_exposure_mcq,
    ],
    "difficult": [
        _tobacco_difficult_sms_quit_ratio_then_caution_pick_then_verdict,
        _tobacco_difficult_sms_marketing_spend_then_order_then_word,
        _tobacco_difficult_sms_policy_pick_then_uncertainty_mcq,
    ],
}
