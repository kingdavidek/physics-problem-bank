"""S1 Unit 1.4 Puberty advanced Practice pools (MS / SMS). Isolated from lesson banks.

Three topics: puberty_maturity, reproductive_anatomy (MS only), pregnancy_sexual_health.
Third-person fictional clinical cases, textbook aggregates, public leaflet data only.
"""
import random

from generators.eursc.science_shared import menstrual_cycle_steps, organ_labels
from generators.shared.utils import graded_answer_number_fields, make_graded_problem

_LEVEL = "eursc"
_SUBJECT = "science"

_CHANGE_BANK = (
    {"id": "physical", "text": "Typical physical changes such as growth spurts and new hair"},
    {"id": "emotional", "text": "Typical mood and friendship changes for many teenagers"},
    {"id": "confess", "text": "A quiz that requires a pupil to describe their own body"},
    {"id": "rank", "text": "Ranking classmates by who looks more adult"},
)
_HORMONE_BANK = (
    {"id": "messenger", "text": "Hormones are chemical messengers in the blood"},
    {"id": "vary", "text": "The age when puberty starts varies and that is normal"},
    {"id": "same_day", "text": "Every person starts puberty on the same calendar day"},
    {"id": "fame", "text": "A celebrity's timeline is the scientific standard"},
)
_GAMETE_BANK = (
    {"id": "egg", "text": "An egg (ovum) is the female gamete"},
    {"id": "sperm", "text": "A sperm is the male gamete"},
    {"id": "bone", "text": "A bone cell is a gamete"},
    {"id": "rumour", "text": "A rumour on social media is a gamete"},
)
_CYCLE_BANK = (
    {"id": "lining", "text": "The uterus lining thickens"},
    {"id": "ovulation", "text": "An egg is released (ovulation)"},
    {"id": "period", "text": "If the egg is not fertilised, the lining is shed (a period)"},
    {"id": "quiz", "text": "The class must report who has started periods"},
)
_ORGAN_BANK = (
    {"id": "ovary", "text": "An ovary can release an egg"},
    {"id": "uterus", "text": "The uterus is where a fetus can develop"},
    {"id": "testis", "text": "A testis can produce sperm"},
    {"id": "femur", "text": "The femur is a gamete-making organ"},
)
_PREG_BANK = (
    {"id": "fertilise", "text": "Fertilisation is egg and sperm joining"},
    {"id": "develop", "text": "A fetus develops in the uterus"},
    {"id": "birth", "text": "Birth is the baby leaving the uterus"},
    {"id": "disclose_sex", "text": "Pupils must describe their own sexual experience"},
)
_HEALTH_BANK = (
    {"id": "contraception", "text": "Contraception can reduce the chance of pregnancy"},
    {"id": "sti", "text": "Some infections spread through sexual contact (STIs)"},
    {"id": "consent", "text": "Consent means a clear, voluntary yes that can be withdrawn"},
    {"id": "pressure", "text": "Pressuring someone after they say no is still allowed if they are famous"},
)
_REJECT_BANK = (
    {"id": "disclose_sex", "text": "Pupils must describe their own sexual experience"},
    {"id": "pressure", "text": "Pressuring someone after they say no is still allowed if they are famous"},
    {"id": "fertilise", "text": "Fertilisation is egg and sperm joining"},
    {"id": "consent", "text": "Consent means a clear, voluntary yes that can be withdrawn"},
)


def _u14_variant(topic, mode_tag, difficulty, suffix):
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


def _u14_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _u14_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"1|{'|'.join(step_ids)}", bank


def _u14_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f"c{i + 1}" for i in range(len(correct_texts)))
    bank = [{"id": cid, "text": text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"pick|{pick_count}|{'|'.join(correct_ids)}", bank, pick_count


def _bank_pick(ids, bank):
    texts = [item["text"] for item in bank if item["id"] in ids]
    distractors = [item["text"] for item in bank if item["id"] not in ids]
    return texts, distractors


# ---------------------------------------------------------------------------
# puberty_maturity — multi_step (MS): intermediate + difficult only
# ---------------------------------------------------------------------------

_PM_MS_I_CHART_PACKS = (
    {"started": 35, "total": 100},
    {"started": 42, "total": 100},
    {"started": 28, "total": 100},
)


@_u14_variant("puberty_maturity", "ms", "intermediate", "chart_not_started_then_hormone_mcq")
def _puberty_maturity_intermediate_ms_chart_not_started_then_hormone_mcq():
    pack = random.choice(_PM_MS_I_CHART_PACKS)
    not_started = pack["total"] - pack["started"]
    correct = "chemical messengers in the blood that help trigger puberty changes"
    distractors = (
        "rumours shared on social media",
        "bones that replace muscles",
        "a sports ranking system",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional textbook chart of "
        f"{pack['total']} fictional young people marks {pack['started']} as having "
        "started a typical physical change.</p>"
        f"<p>(i) How many of those {pack['total']} have not yet started on this chart?</p>"
        "<p>(ii) Using that aggregate chart from (i), hormones in this lesson are</p>"
    )
    solution = (
        f"(i) {pack['total']} − {pack['started']} = <strong>{not_started}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract on the chart, then name hormones as "
        "blood-borne messengers."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (not_started, letter),
            ("Not yet started (count)", "Hormone role"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract on the chart, then choose the hormone role.",
        ),
    )


@_u14_variant("puberty_maturity", "ms", "intermediate", "hormone_order_then_pick")
def _puberty_maturity_intermediate_ms_hormone_order_then_pick():
    order_raw, order_bank = _u14_order_field(
        (
            "Hormones are chemical messengers in the blood",
            "The age when puberty starts varies and that is normal",
        ),
        ("Every person starts puberty on the same calendar day",),
    )
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("messenger", "vary"), _HORMONE_BANK),
        2,
    )
    question = (
        "<p>A fictional science poster lists hormone and timing facts.</p>"
        "<p>(i) Order messenger idea, then variation in timing.</p>"
        "<p>(ii) Using that order from (i), select the two scientific hormone ideas.</p>"
    )
    solution = (
        "(i) <strong>messenger → variation</strong><br>"
        "(ii) Messenger and variation are the two scientific ideas."
    )
    hint = (
        "<strong>Key idea:</strong> Order blood messengers before timing variation, "
        "then pick those two facts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Hormone order", "Scientific hormone ideas"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order messenger then variation, then select both facts.",
        ),
    )


_PM_MS_I_AGE_PACKS = (
    {"a": "Sam", "b": "Lee", "age_a": 12, "age_b": 13},
    {"a": "Alex", "b": "Jordan", "age_a": 11, "age_b": 13},
    {"a": "Casey", "b": "Riley", "age_a": 12, "age_b": 14},
)


@_u14_variant("puberty_maturity", "ms", "intermediate", "classmate_age_then_timing_mcq")
def _puberty_maturity_intermediate_ms_classmate_age_then_timing_mcq():
    pack = random.choice(_PM_MS_I_AGE_PACKS)
    diff = abs(pack["age_b"] - pack["age_a"])
    correct = (
        "timing varies; neither fictional classmate should be mocked for looking different"
    )
    distractors = (
        "the younger classmate has failed science",
        "the class should vote on who looks older",
        "hormones are only rumours",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        f"<p>Two fictional classmates {pack['a']} and {pack['b']} are compared "
        f"only by age: {pack['age_a']} years and {pack['age_b']} years.</p>"
        f"<p>(i) What is the age difference in years?</p>"
        f"<p>(ii) Using those ages from (i), science says about puberty timing that</p>"
    )
    solution = (
        f"(i) |{pack['age_b']} − {pack['age_a']}| = <strong>{diff}</strong> years<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Age gap is not a puberty score; timing varies "
        "between people the same age."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("Age difference (years)", "Timing variation idea"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract the ages, then choose the variation message.",
        ),
    )


@_u14_variant("puberty_maturity", "ms", "difficult", "change_order_then_reject_pick")
def _puberty_maturity_difficult_ms_change_order_then_reject_pick():
    order_raw, order_bank = _u14_order_field(
        (
            "Typical physical changes such as growth spurts and new hair",
            "Typical mood and friendship changes for many teenagers",
        ),
        ("Ranking classmates by who looks more adult",),
    )
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("confess", "rank"), _CHANGE_BANK),
        2,
    )
    question = (
        "<p>A fictional lesson slide separates physical and emotional puberty strands.</p>"
        "<p>(i) Order a physical-change idea, then an emotional-change idea.</p>"
        "<p>(ii) Using that lesson frame from (i), select the two actions that "
        "must not happen in science class.</p>"
    )
    solution = (
        "(i) <strong>physical → emotional</strong><br>"
        "(ii) Confession quizzes and body ranking must not happen."
    )
    hint = (
        "<strong>Key idea:</strong> Order general change types, then reject "
        "confession and ranking."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Change strand order", "Actions to reject"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order physical then emotional, then pick two rejections.",
        ),
    )


_PM_MS_D_AGE_PACKS = (
    {"younger": 11, "older": 14},
    {"younger": 10, "older": 13},
    {"younger": 12, "older": 15},
)


@_u14_variant("puberty_maturity", "ms", "difficult", "late_start_age_then_range_mcq")
def _puberty_maturity_difficult_ms_late_start_age_then_range_mcq():
    pack = random.choice(_PM_MS_D_AGE_PACKS)
    diff = pack["older"] - pack["younger"]
    correct = (
        "may still be within a normal range; worry belongs with a health professional"
    )
    distractors = (
        "has failed science permanently",
        "must publish a timeline to the class",
        "has no hormones at all",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional case study compares two aggregate textbook ages only: "
        f"{pack['younger']} years and {pack['older']} years.</p>"
        f"<p>(i) What is the difference in years?</p>"
        "<p>(ii) Using that age gap from (i), a person who starts puberty later "
        "than fictional classmates</p>"
    )
    solution = (
        f"(i) {pack['older']} − {pack['younger']} = <strong>{diff}</strong> years<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract ages for a gap only; later start can "
        "still be healthy."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("Age gap (years)", "Later-start message"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the age gap, then choose the healthy-range message.",
        ),
    )


@_u14_variant("puberty_maturity", "ms", "difficult", "alex_signpost_order_then_mcq")
def _puberty_maturity_difficult_ms_alex_signpost_order_then_mcq():
    order_raw, order_bank = _u14_order_field(
        (
            "Hormones are chemical messengers in the blood",
            "The age when puberty starts varies and that is normal",
        ),
        ("A celebrity's timeline is the scientific standard",),
    )
    correct = (
        "talk to a trusted teacher or health professional; the quiz will not store private stories"
    )
    distractors = (
        "post the worry on a public leaderboard",
        "rank Alex against the class",
        "ignore all adults",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional scenario says Alex is worried about puberty timing.</p>"
        "<p>(i) Order hormone messenger, then timing variation.</p>"
        "<p>(ii) Using that classroom science from (i), Alex should</p>"
    )
    solution = (
        "(i) <strong>messenger → variation</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Teach messengers and variation, then signpost "
        "a trusted adult."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Hormone lesson order", "Advice for Alex"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order messenger then variation, then choose signposting.",
        ),
    )


# ---------------------------------------------------------------------------
# puberty_maturity — situational_multi_step (SMS)
# ---------------------------------------------------------------------------

_PM_SMS_F_CHART_PACKS = (
    {"started": 40, "total": 100},
    {"started": 45, "total": 100},
    {"started": 38, "total": 100},
)


@_u14_variant("puberty_maturity", "sms", "foundational", "chart_not_started_then_hormone_pick")
def _puberty_maturity_foundational_sms_chart_not_started_then_hormone_pick():
    pack = random.choice(_PM_SMS_F_CHART_PACKS)
    not_started = pack["total"] - pack["started"]
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("messenger", "vary"), _HORMONE_BANK),
        2,
    )
    question = (
        "<p>A fictional public textbook chart of "
        f"{pack['total']} fictional young people marks {pack['started']} as having "
        "started a typical physical change.</p>"
        f"<p>(i) How many of those {pack['total']} have not yet started?</p>"
        "<p>(ii) Using that chart from (i), select the two hormone and timing facts.</p>"
    )
    solution = (
        f"(i) <strong>{not_started}</strong><br>"
        "(ii) Messenger and variation are the two facts."
    )
    hint = (
        "<strong>Key idea:</strong> Subtract on the aggregate chart, then pick "
        "messengers and variation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (not_started, pick_raw),
            ("Not yet started (count)", "Hormone and timing facts"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Subtract on the chart, then select two facts.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "foundational", "physical_mcq_then_emotional_order")
def _puberty_maturity_foundational_sms_physical_mcq_then_emotional_order():
    correct = "growth and new body hair for many young people"
    distractors = (
        "the skeleton turning into helium",
        "mass becoming zero",
        "air becoming a hormone",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    order_raw, order_bank = _u14_order_field(
        (
            "Typical physical changes such as growth spurts and new hair",
            "Typical mood and friendship changes for many teenagers",
        ),
        ("A quiz that requires a pupil to describe their own body",),
    )
    question = (
        "<p>A fictional lesson wall chart lists puberty change types.</p>"
        "<p>(i) A typical physical change at puberty is</p>"
        "<p>(ii) Using that physical idea from (i), order physical change, then "
        "emotional change.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>physical → emotional</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Name a general physical pattern, then order "
        "physical before emotional."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, order_raw),
            ("Typical physical change", "Change order"),
            field_types=("mcq", "order"),
            field_options=(options, order_bank),
            format_hint="Choose the physical change, then order the two strands.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "foundational", "hormone_mcq_then_change_pick")
def _puberty_maturity_foundational_sms_hormone_mcq_then_change_pick():
    correct = "chemical messengers that help trigger puberty changes"
    distractors = ("rumours", "bones", "banned sports drinks only")
    options, letter = _u14_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("physical", "emotional"), _CHANGE_BANK),
        2,
    )
    question = (
        "<p>A fictional science leaflet introduces puberty in third person.</p>"
        "<p>(i) Hormones in this lesson are</p>"
        "<p>(ii) Using that hormone idea from (i), select the two general puberty "
        "ideas that belong in class.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Physical and emotional general changes belong in class."
    )
    hint = (
        "<strong>Key idea:</strong> Hormones are messengers; pick general physical "
        "and emotional patterns."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Hormone role", "General puberty ideas"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the hormone role, then pick two general ideas.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "intermediate", "sam_lee_voice_then_variation_mcq")
def _puberty_maturity_intermediate_sms_sam_lee_voice_then_variation_mcq():
    correct = "timing varies; neither person should be mocked"
    distractors = (
        "Lee has failed",
        "the class should vote",
        "hormones are rumours",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("confess", "rank"), _CHANGE_BANK),
        2,
    )
    question = (
        "<p>A fictional case note says Sam and Lee are the same age. Sam has a "
        "deeper voice in the story; Lee does not yet.</p>"
        "<p>(i) Science says about their timing that</p>"
        "<p>(ii) Using that variation idea from (i), select the two actions that "
        "do not belong in this lesson.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Confession and ranking do not belong."
    )
    hint = (
        "<strong>Key idea:</strong> Same age can mean different timing; reject "
        "confession and ranking."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Timing variation message", "Actions to reject"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the variation message, then pick two rejections.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "intermediate", "blood_hormone_mcq_then_messenger_order")
def _puberty_maturity_intermediate_sms_blood_hormone_mcq_then_messenger_order():
    correct = "the blood"
    distractors = ("the skeleton only", "a distance–time graph", "a friction pad")
    options, letter = _u14_mcq_field(correct, distractors)
    order_raw, order_bank = _u14_order_field(
        (
            "Hormones are chemical messengers in the blood",
            "The age when puberty starts varies and that is normal",
        ),
        ("Every person starts puberty on the same calendar day",),
    )
    question = (
        "<p>A fictional endocrine poster is displayed in a science lab.</p>"
        "<p>(i) Hormones travel mainly in the</p>"
        "<p>(ii) Using that transport idea from (i), order messenger, then "
        "timing variation.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>messenger → variation</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Blood carries messengers; order messenger "
        "before variation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, order_raw),
            ("Hormone transport", "Lesson order"),
            field_types=("mcq", "order"),
            field_options=(options, order_bank),
            format_hint="Choose blood transport, then order the two facts.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "intermediate", "five_year_span_then_reject_pick")
def _puberty_maturity_intermediate_sms_five_year_span_then_reject_pick():
    span = 5
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("same_day", "fame"), _HORMONE_BANK),
        2,
    )
    question = (
        "<p>A fictional textbook says puberty often starts somewhere in a span of "
        f"about {span} years for many people.</p>"
        f"<p>(i) How many years is that span?</p>"
        "<p>(ii) Using that range idea from (i), select the two unscientific "
        "timing claims.</p>"
    )
    solution = (
        f"(i) <strong>{span}</strong> years<br>"
        "(ii) Same calendar day and celebrity standard are unscientific."
    )
    hint = (
        "<strong>Key idea:</strong> Copy the span length, then reject one-day "
        "and celebrity claims."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (span, pick_raw),
            ("Span (years)", "Unscientific timing claims"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Enter the span, then pick two false timing claims.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "difficult", "media_body_mcq_then_reject_pick")
def _puberty_maturity_difficult_sms_media_body_mcq_then_reject_pick():
    correct = "are not a measurement of healthy puberty"
    distractors = (
        "are controlled scientific samples",
        "replace hormones",
        "are SI units",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("same_day", "fame"), _HORMONE_BANK),
        2,
    )
    question = (
        "<p>A fictional media literacy slide discusses teenage body images.</p>"
        "<p>(i) Media images of 'ideal' teenage bodies</p>"
        "<p>(ii) Using that critique from (i), select the two unscientific "
        "timing claims about puberty.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Same-day and celebrity claims are unscientific."
    )
    hint = (
        "<strong>Key idea:</strong> Images are not clinical data; reject "
        "calendar-day and fame standards."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Media body message", "Unscientific timing claims"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the media critique, then pick two false claims.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "difficult", "gamete_ready_mcq_then_age_diff")
def _puberty_maturity_difficult_sms_gamete_ready_mcq_then_age_diff():
    pack = random.choice(_PM_MS_I_AGE_PACKS)
    diff = abs(pack["age_b"] - pack["age_a"])
    correct = (
        "sexual maturity, which arrives at different ages in the fictional textbook"
    )
    distractors = (
        "a distance–time graph",
        "friction",
        "buoyancy",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional syllabus note links gametes to maturity without asking "
        "who has started.</p>"
        "<p>(i) Producing mature sperm or eggs is part of</p>"
        f"<p>(ii) Two fictional classmates are compared only by age: "
        f"{pack['age_a']} and {pack['age_b']} years. What is the age difference?</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        f"(ii) <strong>{diff}</strong> years"
    )
    hint = (
        "<strong>Key idea:</strong> Mature gametes link to sexual maturity; age "
        "gap is not a puberty score."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, diff),
            ("Sexual maturity idea", "Age difference (years)"),
            field_types=("mcq", "number"),
            field_options=(options, None),
            format_hint="Choose the maturity idea, then subtract the ages.",
        ),
    )


@_u14_variant("puberty_maturity", "sms", "difficult", "alex_worry_chain_then_signpost_mcq")
def _puberty_maturity_difficult_sms_alex_worry_chain_then_signpost_mcq():
    change_raw, change_bank = _u14_order_field(
        (
            "Typical physical changes such as growth spurts and new hair",
            "Typical mood and friendship changes for many teenagers",
        ),
        ("Ranking classmates by who looks more adult",),
    )
    hormone_raw, hormone_bank = _u14_order_field(
        (
            "Hormones are chemical messengers in the blood",
            "The age when puberty starts varies and that is normal",
        ),
        ("Every person starts puberty on the same calendar day",),
    )
    correct = (
        "talk to a trusted adult or health professional; the quiz will not store that story"
    )
    distractors = (
        "post it for the class",
        "rank Alex",
        "ignore all adults",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional classroom scenario says Alex wants private advice about "
        "body changes.</p>"
        "<p>(i) Order physical change, then emotional change.</p>"
        "<p>(ii) Order hormone messenger, then timing variation.</p>"
        "<p>(iii) Using those lesson strands from (i) and (ii), Alex should</p>"
    )
    solution = (
        "(i) <strong>physical → emotional</strong><br>"
        "(ii) <strong>messenger → variation</strong><br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order both lesson strands, then signpost "
        "a trusted adult."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (change_raw, hormone_raw, letter),
            ("Physical/emotional order", "Hormone order", "Advice for Alex"),
            field_types=("order", "order", "mcq"),
            field_options=(change_bank, hormone_bank, options),
            format_hint="Order both strands, then choose signposting.",
        ),
    )


# ---------------------------------------------------------------------------
# reproductive_anatomy — multi_step (MS only): intermediate + difficult
# ---------------------------------------------------------------------------


@_u14_variant("reproductive_anatomy", "ms", "intermediate", "uterus_fig_then_gamete_mcq")
def _reproductive_anatomy_intermediate_ms_uterus_fig_then_gamete_mcq():
    diagram = str(organ_labels(title="Fictional organ schematic"))
    correct = "egg (ovum)"
    distractors = ("sperm", "femur", "newton")
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional anatomy worksheet uses labelled boxes only.</p>"
        "<p>(i) Which letter labels the uterus on this educational schematic?</p>"
        "<p>(ii) Using that organ map from (i), the female gamete is the</p>"
    )
    solution = (
        "(i) <strong>B</strong> is the uterus<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> B is the uterus on the schematic; the female "
        "gamete is the egg."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("B", letter),
            ("Uterus letter", "Female gamete"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Read B as uterus, then choose the female gamete.",
        ),
    )


@_u14_variant("reproductive_anatomy", "ms", "intermediate", "cycle_order_then_period_mcq")
def _reproductive_anatomy_intermediate_ms_cycle_order_then_period_mcq():
    cycle = str(menstrual_cycle_steps(title="Fictional cycle schematic"))
    order_raw, order_bank = _u14_order_field(
        (
            "The uterus lining thickens",
            "An egg is released (ovulation)",
            "If the egg is not fertilised, the lining is shed (a period)",
        ),
        ("The class must report who has started periods",),
    )
    correct = (
        "the uterus lining is shed after an egg was not fertilised"
    )
    distractors = (
        "the person failed a test",
        "sperm become eggs",
        "the heart stops",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        cycle
        + "<p>A fictional textbook sequence shows the menstrual cycle in third person.</p>"
        "<p>(i) Order lining thickens, then ovulation, then period if no fertilisation.</p>"
        "<p>(ii) Using that unfertilised cycle from (i), a period happens when</p>"
    )
    solution = (
        "(i) <strong>lining → ovulation → period</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the cycle steps, then name lining shed "
        "when no fertilisation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Cycle order", "Period explanation"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the three cycle steps, then choose the period reason.",
        ),
    )


@_u14_variant("reproductive_anatomy", "ms", "intermediate", "gamete_pick_then_count")
def _reproductive_anatomy_intermediate_ms_gamete_pick_then_count():
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("egg", "sperm"), _GAMETE_BANK),
        2,
    )
    gamete_types = 2
    question = (
        "<p>A fictional revision card lists four items about sex cells.</p>"
        "<p>(i) Select the two genuine human gametes.</p>"
        "<p>(ii) Using those selections from (i), how many types of human gamete "
        "does this lesson name?</p>"
    )
    solution = (
        "(i) Egg and sperm are the genuine gametes.<br>"
        f"(ii) <strong>{gamete_types}</strong> types"
    )
    hint = (
        "<strong>Key idea:</strong> Pick egg and sperm, then count the two "
        "gamete types named."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, gamete_types),
            ("Genuine gametes", "Gamete types named"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select egg and sperm, then enter the type count.",
        ),
    )


@_u14_variant("reproductive_anatomy", "ms", "difficult", "testis_fig_then_sperm_mcq")
def _reproductive_anatomy_difficult_ms_testis_fig_then_sperm_mcq():
    diagram = str(organ_labels(title="Fictional C testis"))
    correct = "testes"
    distractors = ("ovaries", "alveoli", "knees")
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional diagram labels C as a testis on a schematic only.</p>"
        "<p>(i) Which letter is a testis?</p>"
        "<p>(ii) Using that organ from (i), sperm are produced in the</p>"
    )
    solution = (
        "(i) <strong>C</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> C marks the testis; sperm are made in the testes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("C", letter),
            ("Testis letter", "Sperm production site"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Read C as testis, then choose where sperm are made.",
        ),
    )


@_u14_variant("reproductive_anatomy", "ms", "difficult", "fertilisation_order_then_implant_mcq")
def _reproductive_anatomy_difficult_ms_fertilisation_order_then_implant_mcq():
    order_raw, order_bank = _u14_order_field(
        ("An ovary can release an egg", "The uterus is where a fetus can develop"),
        ("The femur is a gamete-making organ",),
    )
    correct = "the uterus lining"
    distractors = ("the femur", "an alveolus", "a tendon")
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional fertilisation timeline uses third-person organ roles only.</p>"
        "<p>(i) Order ovary, then uterus, as egg-path ideas.</p>"
        "<p>(ii) Using that path from (i), if fertilisation happens, the early "
        "embryo can implant in the</p>"
    )
    solution = (
        "(i) <strong>ovary → uterus</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Egg from ovary toward uterus; implantation "
        "is in the uterus lining."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Egg-path order", "Implantation site"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order ovary then uterus, then choose implantation site.",
        ),
    )


@_u14_variant("reproductive_anatomy", "ms", "difficult", "organ_pick_then_gamete_count")
def _reproductive_anatomy_difficult_ms_organ_pick_then_gamete_count():
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("ovary", "uterus", "testis"), _ORGAN_BANK),
        3,
    )
    gamete_types = 2
    eggs_per_cycle = 1
    question = (
        "<p>A fictional organ checklist uses schematic labels only.</p>"
        "<p>(i) Select the three reproductive organs on the list.</p>"
        "<p>(ii) Using that organ set from (i), how many types of human gamete "
        "does this lesson name?</p>"
        "<p>(iii) In the simple S1 model, ovulation releases how many eggs in "
        "a typical cycle?</p>"
    )
    solution = (
        "(i) Ovary, uterus and testis are reproductive organs.<br>"
        f"(ii) <strong>{gamete_types}</strong> gamete types<br>"
        f"(iii) <strong>{eggs_per_cycle}</strong> egg"
    )
    hint = (
        "<strong>Key idea:</strong> Pick three organs, then count gamete types "
        "and the simple-model egg release."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pick_raw, gamete_types, eggs_per_cycle),
            ("Reproductive organs", "Gamete types", "Eggs per cycle (model)"),
            field_types=("pick", "number", "number"),
            field_options=(pick_bank, None, None),
            field_pick_counts=(pick_count, None, None),
            format_hint="Pick three organs, then enter gamete count and egg count.",
        ),
    )


# ---------------------------------------------------------------------------
# pregnancy_sexual_health — multi_step (MS): intermediate + difficult
# ---------------------------------------------------------------------------


@_u14_variant("pregnancy_sexual_health", "ms", "intermediate", "consent_two_then_no_mcq")
def _pregnancy_sexual_health_intermediate_ms_consent_two_then_no_mcq():
    agree_count = 2
    correct = "not consent"
    distractors = (
        "fine if Jordan is popular",
        "a hormone",
        "a buoyancy effect",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional consent leaflet says both people must agree in a "
        "two-person scenario.</p>"
        f"<p>(i) How many people must agree?</p>"
        "<p>(ii) Using that rule from (i), a fictional story says Jordan hears "
        "'no' and continues. That is</p>"
    )
    solution = (
        f"(i) <strong>{agree_count}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Both must agree; continuing after 'no' is "
        "not consent."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (agree_count, letter),
            ("People who must agree", "Jordan scenario"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count who must agree, then classify continuing after no.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "ms", "intermediate", "preg_order_then_fetus_mcq")
def _pregnancy_sexual_health_intermediate_ms_preg_order_then_fetus_mcq():
    order_raw, order_bank = _u14_order_field(
        (
            "Fertilisation is egg and sperm joining",
            "A fetus develops in the uterus",
            "Birth is the baby leaving the uterus",
        ),
        ("Pupils must describe their own sexual experience",),
    )
    correct = (
        "the developing offspring in the uterus after the early embryo stage"
    )
    distractors = (
        "a type of joint",
        "exhaled carbon dioxide",
        "a sports slogan",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional clinic poster shows the pregnancy sequence in third person.</p>"
        "<p>(i) Order fertilisation, then fetal development, then birth.</p>"
        "<p>(ii) Using that sequence from (i), a fetus is</p>"
    )
    solution = (
        "(i) <strong>fertilise → develop → birth</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order join-develop-birth, then define fetus "
        "as developing in the uterus."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Pregnancy order", "Fetus definition"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the three steps, then choose the fetus definition.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "ms", "intermediate", "health_pick_then_count")
def _pregnancy_sexual_health_intermediate_ms_health_pick_then_count():
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("contraception", "sti", "consent"), _HEALTH_BANK),
        3,
    )
    idea_count = 3
    question = (
        "<p>A fictional sexual-health factsheet lists four classroom-safe ideas.</p>"
        "<p>(i) Select the three healthy decision ideas.</p>"
        "<p>(ii) Using those selections from (i), how many ideas did you select?</p>"
    )
    solution = (
        "(i) Contraception, STI knowledge and consent are the three ideas.<br>"
        f"(ii) <strong>{idea_count}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick contraception, STI and consent; skip "
        "pressure-after-no."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, idea_count),
            ("Healthy decision ideas", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select three ideas, then count selections.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "ms", "difficult", "withdraw_count_then_comm_mcq")
def _pregnancy_sexual_health_difficult_ms_withdraw_count_then_comm_mcq():
    current_decision = 1
    correct = (
        "listening and respecting a no, in third-person scenarios"
    )
    distractors = (
        "ignoring a withdrawn yes",
        "forcing a public confession in class",
        "collecting partner names in this app",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional consent case study says a person said yes, then said no.</p>"
        "<p>(i) How many of those statements is the current decision?</p>"
        "<p>(ii) Using that later answer from (i), healthy communication includes</p>"
    )
    solution = (
        f"(i) <strong>{current_decision}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Only the later no counts; healthy talk "
        "respects withdrawal."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (current_decision, letter),
            ("Current decision count", "Healthy communication"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the current decision, then choose healthy communication.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "ms", "difficult", "sti_order_then_asymptomatic_mcq")
def _pregnancy_sexual_health_difficult_ms_sti_order_then_asymptomatic_mcq():
    order_raw, order_bank = _u14_order_field(
        (
            "Contraception can reduce the chance of pregnancy",
            "Some infections spread through sexual contact (STIs)",
        ),
        ("Pressuring someone after they say no is still allowed if they are famous",),
    )
    correct = (
        "qualified testing matters; the lesson does not ask who has been tested"
    )
    distractors = (
        "testing is never useful",
        "air is an STI",
        "joints cause pregnancy",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public-health leaflet orders pregnancy-risk and infection facts.</p>"
        "<p>(i) Order contraception knowledge, then STI knowledge.</p>"
        "<p>(ii) Using that health frame from (i), some STIs can be present with "
        "few symptoms. That is why</p>"
    )
    solution = (
        "(i) <strong>contraception → STI</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order risk topics, then signpost testing "
        "without a class survey."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Health topic order", "Asymptomatic STI message"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order contraception then STI, then choose the testing message.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "ms", "difficult", "pregnancy_help_order_then_signpost_mcq")
def _pregnancy_sexual_health_difficult_ms_pregnancy_help_order_then_signpost_mcq():
    preg_raw, preg_bank = _u14_order_field(
        (
            "Fertilisation is egg and sperm joining",
            "A fetus develops in the uterus",
            "Birth is the baby leaving the uterus",
        ),
        ("Pupils must describe their own sexual experience",),
    )
    correct = (
        "a trusted adult or health professional; do not harvest private stories here"
    )
    distractors = (
        "diagnose and treat in the quiz",
        "a sports ranking",
        "post online for fame",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional character in a case study is pregnant and scared.</p>"
        "<p>(i) Order fertilisation, development, then birth.</p>"
        "<p>(ii) Using that sequence from (i), the classroom answer is to see</p>"
    )
    solution = (
        "(i) <strong>fertilise → develop → birth</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the pregnancy sequence, then signpost "
        "qualified help."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (preg_raw, letter),
            ("Pregnancy sequence", "Classroom response"),
            field_types=("order", "mcq"),
            field_options=(preg_bank, options),
            format_hint="Order the three steps, then choose signposting.",
        ),
    )


# ---------------------------------------------------------------------------
# pregnancy_sexual_health — situational_multi_step (SMS)
# ---------------------------------------------------------------------------


@_u14_variant("pregnancy_sexual_health", "sms", "foundational", "two_agree_then_consent_mcq")
def _pregnancy_sexual_health_foundational_sms_two_agree_then_consent_mcq():
    agree_count = 2
    correct = "a clear, voluntary agreement that can be withdrawn"
    distractors = (
        "silence after someone looks famous",
        "the other person already started so it is too late",
        "a teacher collecting relationship lists",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public leaflet says consent in a two-person scenario needs "
        "both people to agree.</p>"
        f"<p>(i) How many people is that?</p>"
        "<p>(ii) Using that count from (i), consent means</p>"
    )
    solution = (
        f"(i) <strong>{agree_count}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Both must agree; consent can be withdrawn."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (agree_count, letter),
            ("People who must agree", "Consent meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count both people, then choose the consent definition.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "foundational", "preg_order_then_pick_two")
def _pregnancy_sexual_health_foundational_sms_preg_order_then_pick_two():
    order_raw, order_bank = _u14_order_field(
        (
            "Fertilisation is egg and sperm joining",
            "A fetus develops in the uterus",
            "Birth is the baby leaving the uterus",
        ),
        ("Pupils must describe their own sexual experience",),
    )
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("fertilise", "develop"), _PREG_BANK),
        2,
    )
    question = (
        "<p>A fictional textbook page lists pregnancy science steps.</p>"
        "<p>(i) Order fertilisation, development, then birth.</p>"
        "<p>(ii) Using that sequence from (i), select the two early pregnancy "
        "science steps.</p>"
    )
    solution = (
        "(i) <strong>fertilise → develop → birth</strong><br>"
        "(ii) Fertilisation and development are the two early steps."
    )
    hint = (
        "<strong>Key idea:</strong> Order the full sequence, then pick join and "
        "develop."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Pregnancy order", "Early pregnancy steps"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order all three steps, then pick fertilise and develop.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "foundational", "leaflet_health_pick_then_count")
def _pregnancy_sexual_health_foundational_sms_leaflet_health_pick_then_count():
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("contraception", "sti"), _HEALTH_BANK),
        2,
    )
    idea_count = 2
    question = (
        "<p>A fictional clinic leaflet lists four sexual-health classroom facts.</p>"
        "<p>(i) Select the two sexual-health ideas taught here.</p>"
        "<p>(ii) Using those selections from (i), how many ideas did you select?</p>"
    )
    solution = (
        "(i) Contraception and STI knowledge are the two ideas.<br>"
        f"(ii) <strong>{idea_count}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick contraception and STI facts, then count."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, idea_count),
            ("Sexual-health ideas", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two ideas, then count selections.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "intermediate", "condom_mcq_then_two_agree")
def _pregnancy_sexual_health_intermediate_sms_condom_mcq_then_two_agree():
    correct = (
        "a barrier method that can reduce pregnancy chance and some STI risk"
    )
    distractors = (
        "a way to rank classmates",
        "proof that consent is optional",
        "an SI unit",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    agree_count = 2
    question = (
        "<p>A fictional public-health poster discusses barrier methods in third person.</p>"
        "<p>(i) A condom is discussed here as</p>"
        "<p>(ii) Using that method knowledge from (i), consent in a two-person "
        "scenario needs how many people to agree?</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        f"(ii) <strong>{agree_count}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Name the barrier method, then count who "
        "must agree."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, agree_count),
            ("Condom role", "People who must agree"),
            field_types=("mcq", "number"),
            field_options=(options, None),
            format_hint="Choose the condom role, then enter how many must agree.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "intermediate", "health_order_then_reject_pick")
def _pregnancy_sexual_health_intermediate_sms_health_order_then_reject_pick():
    order_raw, order_bank = _u14_order_field(
        (
            "Contraception can reduce the chance of pregnancy",
            "Some infections spread through sexual contact (STIs)",
        ),
        ("Pressuring someone after they say no is still allowed if they are famous",),
    )
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("disclose_sex", "pressure"), _REJECT_BANK),
        2,
    )
    question = (
        "<p>A fictional lesson chart orders pregnancy-risk topics.</p>"
        "<p>(i) Order contraception knowledge, then STI knowledge.</p>"
        "<p>(ii) Using that classroom frame from (i), select the two items that "
        "must not happen in this quiz.</p>"
    )
    solution = (
        "(i) <strong>contraception → STI</strong><br>"
        "(ii) Disclosure and pressure-after-no must not happen."
    )
    hint = (
        "<strong>Key idea:</strong> Order the two risk topics, then reject "
        "disclosure and pressure."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Health topic order", "Quiz items to reject"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order contraception then STI, then pick two rejections.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "intermediate", "birth_mcq_then_consent_pick")
def _pregnancy_sexual_health_intermediate_sms_birth_mcq_then_consent_pick():
    correct = (
        "the baby leaving the uterus, often through the vagina"
    )
    distractors = (
        "the fetus remaining in the ovary forever",
        "a pulse measurement",
        "unrelated to pregnancy",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("contraception", "consent"), _HEALTH_BANK),
        2,
    )
    question = (
        "<p>A fictional midwife leaflet describes birth in clinical language.</p>"
        "<p>(i) Birth is usually</p>"
        "<p>(ii) Using that pregnancy endpoint from (i), select contraception and "
        "consent as two classroom facts.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Contraception and consent are the two facts."
    )
    hint = (
        "<strong>Key idea:</strong> Define birth clinically, then pick "
        "contraception and consent."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Birth definition", "Classroom health facts"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the birth definition, then pick two facts.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "difficult", "limit_fail_mcq_then_three_pick")
def _pregnancy_sexual_health_difficult_sms_limit_fail_mcq_then_three_pick():
    correct = (
        "methods reduce chance; they are not a magic shield, and personal choices "
        "belong with qualified advice"
    )
    distractors = (
        "science never mentions it",
        "STIs cannot exist",
        "consent is optional",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("contraception", "sti", "consent"), _HEALTH_BANK),
        3,
    )
    question = (
        "<p>A fictional pharmacist leaflet discusses contraception limits.</p>"
        "<p>(i) Contraception can fail. That is why</p>"
        "<p>(ii) Using that limit idea from (i), select the three healthy "
        "decision ideas.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Contraception, STI knowledge and consent are the three ideas."
    )
    hint = (
        "<strong>Key idea:</strong> Methods reduce chance; pick all three "
        "healthy decision facts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Contraception limit message", "Healthy decision ideas"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the limit message, then select three ideas.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "difficult", "sti_symptoms_mcq_then_testing_order")
def _pregnancy_sexual_health_difficult_sms_sti_symptoms_mcq_then_testing_order():
    correct = (
        "few symptoms does not mean there is no infection; qualified testing still matters"
    )
    distractors = (
        "testing is never useful",
        "air is an STI",
        "joints cause pregnancy",
    )
    options, letter = _u14_mcq_field(correct, distractors)
    order_raw, order_bank = _u14_order_field(
        (
            "Qualified health advice and testing",
            "The lesson does not ask who has been tested",
        ),
        ("Post symptoms on a public leaderboard",),
    )
    question = (
        "<p>A fictional STI factsheet is written for a science classroom.</p>"
        "<p>(i) Some STIs can be present with few symptoms. That is why</p>"
        "<p>(ii) Using that asymptomatic idea from (i), order qualified testing, "
        "then no class test-history survey.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>testing → no survey</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Asymptomatic STIs need testing; signpost "
        "care without a class survey."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, order_raw),
            ("Asymptomatic STI message", "Testing classroom order"),
            field_types=("mcq", "order"),
            field_options=(options, order_bank),
            format_hint="Choose the asymptomatic message, then order the two steps.",
        ),
    )


@_u14_variant("pregnancy_sexual_health", "sms", "difficult", "scared_pregnancy_chain_then_pick")
def _pregnancy_sexual_health_difficult_sms_scared_pregnancy_chain_then_pick():
    preg_raw, preg_bank = _u14_order_field(
        (
            "Fertilisation is egg and sperm joining",
            "A fetus develops in the uterus",
            "Birth is the baby leaving the uterus",
        ),
        ("Pupils must describe their own sexual experience",),
    )
    pick_raw, pick_bank, pick_count = _u14_pick_field(
        *_bank_pick(("fertilise", "birth"), _PREG_BANK),
        2,
    )
    signpost = 1
    question = (
        "<p>A fictional scared-pregnancy case study is discussed in third person.</p>"
        "<p>(i) Order fertilisation, development, then birth.</p>"
        "<p>(ii) Using that sequence from (i), select fertilisation and birth.</p>"
        "<p>(iii) The classroom signposts one trusted adult or health professional "
        "(enter 1 for that rule).</p>"
    )
    solution = (
        "(i) <strong>fertilise → develop → birth</strong><br>"
        "(ii) Fertilisation and birth are selected.<br>"
        f"(iii) <strong>{signpost}</strong> signposted route"
    )
    hint = (
        "<strong>Key idea:</strong> Order the sequence, pick endpoints, then "
        "count one signposted help route."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (preg_raw, pick_raw, signpost),
            ("Pregnancy order", "Endpoint steps", "Signposted help routes"),
            field_types=("order", "pick", "number"),
            field_options=(preg_bank, pick_bank, None),
            field_pick_counts=(None, pick_count, None),
            format_hint="Order all steps, pick two endpoints, enter 1 for signposting.",
        ),
    )


PUBERTY_MATURITY_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _puberty_maturity_intermediate_ms_chart_not_started_then_hormone_mcq,
        _puberty_maturity_intermediate_ms_hormone_order_then_pick,
        _puberty_maturity_intermediate_ms_classmate_age_then_timing_mcq,
    ],
    "difficult": [
        _puberty_maturity_difficult_ms_change_order_then_reject_pick,
        _puberty_maturity_difficult_ms_late_start_age_then_range_mcq,
        _puberty_maturity_difficult_ms_alex_signpost_order_then_mcq,
    ],
}

PUBERTY_MATURITY_SMS_POOLS = {
    "foundational": [
        _puberty_maturity_foundational_sms_chart_not_started_then_hormone_pick,
        _puberty_maturity_foundational_sms_physical_mcq_then_emotional_order,
        _puberty_maturity_foundational_sms_hormone_mcq_then_change_pick,
    ],
    "intermediate": [
        _puberty_maturity_intermediate_sms_sam_lee_voice_then_variation_mcq,
        _puberty_maturity_intermediate_sms_blood_hormone_mcq_then_messenger_order,
        _puberty_maturity_intermediate_sms_five_year_span_then_reject_pick,
    ],
    "difficult": [
        _puberty_maturity_difficult_sms_media_body_mcq_then_reject_pick,
        _puberty_maturity_difficult_sms_gamete_ready_mcq_then_age_diff,
        _puberty_maturity_difficult_sms_alex_worry_chain_then_signpost_mcq,
    ],
}

REPRODUCTIVE_ANATOMY_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _reproductive_anatomy_intermediate_ms_uterus_fig_then_gamete_mcq,
        _reproductive_anatomy_intermediate_ms_cycle_order_then_period_mcq,
        _reproductive_anatomy_intermediate_ms_gamete_pick_then_count,
    ],
    "difficult": [
        _reproductive_anatomy_difficult_ms_testis_fig_then_sperm_mcq,
        _reproductive_anatomy_difficult_ms_fertilisation_order_then_implant_mcq,
        _reproductive_anatomy_difficult_ms_organ_pick_then_gamete_count,
    ],
}

PREGNANCY_SEXUAL_HEALTH_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _pregnancy_sexual_health_intermediate_ms_consent_two_then_no_mcq,
        _pregnancy_sexual_health_intermediate_ms_preg_order_then_fetus_mcq,
        _pregnancy_sexual_health_intermediate_ms_health_pick_then_count,
    ],
    "difficult": [
        _pregnancy_sexual_health_difficult_ms_withdraw_count_then_comm_mcq,
        _pregnancy_sexual_health_difficult_ms_sti_order_then_asymptomatic_mcq,
        _pregnancy_sexual_health_difficult_ms_pregnancy_help_order_then_signpost_mcq,
    ],
}

PREGNANCY_SEXUAL_HEALTH_SMS_POOLS = {
    "foundational": [
        _pregnancy_sexual_health_foundational_sms_two_agree_then_consent_mcq,
        _pregnancy_sexual_health_foundational_sms_preg_order_then_pick_two,
        _pregnancy_sexual_health_foundational_sms_leaflet_health_pick_then_count,
    ],
    "intermediate": [
        _pregnancy_sexual_health_intermediate_sms_condom_mcq_then_two_agree,
        _pregnancy_sexual_health_intermediate_sms_health_order_then_reject_pick,
        _pregnancy_sexual_health_intermediate_sms_birth_mcq_then_consent_pick,
    ],
    "difficult": [
        _pregnancy_sexual_health_difficult_sms_limit_fail_mcq_then_three_pick,
        _pregnancy_sexual_health_difficult_sms_sti_symptoms_mcq_then_testing_order,
        _pregnancy_sexual_health_difficult_sms_scared_pregnancy_chain_then_pick,
    ],
}

