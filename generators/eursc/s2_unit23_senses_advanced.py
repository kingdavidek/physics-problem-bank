"""S2 Unit 2.3 Senses advanced Practice pools (MS / SMS). Isolated from lesson banks.

Batch 3.3 (safeguarding-gated). Eight topics with deliberately uneven cells
(docs/EURSC_ADVANCED_QUESTIONS.md):

  vision                  MS I, D      SMS F, I, D
  hearing                 MS I, D      SMS F, I, D
  touch                   MS I, D      SMS I, D      (F SMS —: no personal test)
  smell                   MS —         SMS I, D
  taste                   MS I, D      SMS I, D      (F SMS —)
  proprioception_balance  MS I, D      SMS I, D      (F SMS —)
  interoception           MS —         SMS I, D
  nonhuman_senses         MS F, I, D   SMS F, I, D

Every excluded cell is an empty list and stays fail-closed.

Safeguarding gate for this batch:
  * every scenario is a third-person fictional case, a textbook/public table,
    a supplied aggregate dataset, or a fictional lab/field model, and every
    stem names it as fictional;
  * no stem asks a pupil to test, describe, rank or record their own eyes,
    ears, skin, nose, tongue, balance, internal signals, glasses, hearing aids,
    dizziness, hunger, heartbeat or mood, and none asks classmates to test each
    other — two-point, nose-clip and rotation data are always supplied;
  * nothing ranks classmates, bodies, senses or abilities;
  * interoception cases connect an ambiguous internal signal to alternative
    interpretations and a trusted-adult / qualified-help signpost; the
    generator never diagnoses;
  * hearing-aid, glasses and clinical references stay with fictional
    characters or public aggregates, never a pupil's file.
"""
import random

from generators.eursc.science_shared import canal_boxes, ear_boxes, eye_boxes
from generators.shared.utils import graded_answer_number_fields, make_graded_problem
from models.svg_kit import bar_chart

_LEVEL = "eursc"
_SUBJECT = "science"


def _u23_variant(topic, mode_tag, difficulty, suffix):
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


def _u23_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _u23_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"1|{'|'.join(step_ids)}", bank


def _u23_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f"c{i + 1}" for i in range(len(correct_texts)))
    bank = [{"id": cid, "text": text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"pick|{pick_count}|{'|'.join(correct_ids)}", bank, pick_count


def _pct(part, whole):
    return round(100 * part / whole)


def _fields(values, labels, types, options=None, picks=None, hint=None):
    kwargs = {"field_types": types, "format_hint": hint}
    if options is not None:
        kwargs["field_options"] = options
    if picks is not None:
        kwargs["field_pick_counts"] = picks
    return graded_answer_number_fields(values, labels, **kwargs)


# ---------------------------------------------------------------------------
# vision — multi_step (I, D); foundational MS stays — (matrix)
# ---------------------------------------------------------------------------

_VI_MS_I_ERR_PACKS = (
    {"errors": ("near-sight", "far-sight"), "pick": "near-sight", "blur": "distant objects"},
    {"errors": ("far-sight", "near-sight"), "pick": "far-sight", "blur": "near objects"},
)


@_u23_variant("vision", "ms", "intermediate", "errors_count_then_blur_mcq")
def _vision_intermediate_ms_errors_count_then_blur_mcq():
    pack = random.choice(_VI_MS_I_ERR_PACKS)
    correct = f"{pack['blur']} are not in focus"
    wrong_blur = "near objects" if pack["blur"] == "distant objects" else "distant objects"
    distractors = (
        f"{wrong_blur} are not in focus",
        "the retina stops detecting light",
        "the lens has stopped changing shape",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional optics poster lists focusing errors: {pack['errors'][0]} "
        f"and {pack['errors'][1]}.</p>"
        "<p>(i) Enter how many focusing-error kinds the poster names.</p>"
        f"<p>(ii) Of the kinds counted in (i), {pack['pick']} means</p>"
    )
    solution = (
        "(i) <strong>2</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Two error kinds; each blurs one distance "
        "range."
    )
    return (
        question, solution, hint, 2,
        _fields((2, letter), ("Error kinds", f"{pack['pick']} means"),
                ("number", "mcq"), (None, options),
                hint="Count, then choose which distance blurs."),
    )


@_u23_variant("vision", "ms", "intermediate", "path_order_then_accommodation_word")
def _vision_intermediate_ms_path_order_then_accommodation_word():
    order_raw, order_bank = _u23_order_field(
        (
            "The lens refracts light to help form an image",
            "The retina detects the image",
            "Signals travel toward the brain for interpretation",
        ),
        ("The quiz ranks whose eyesight is best",),
    )
    question = (
        "<p>A fictional biology worksheet traces light through the eye.</p>"
        "<p>(i) Order the three stages.</p>"
        "<p>(ii) The first stage in (i) can change lens shape for near or far. "
        "Write the one-word term for that.</p>"
    )
    solution = (
        "(i) <strong>lens → retina → brain</strong><br>"
        "(ii) <strong>accommodation</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Bend, detect, interpret — and the bending "
        "part reshapes to focus."
    )
    return (
        question, solution, hint, 2,
        _fields((order_raw, "accommodation"), ("Light path", "Term"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three stages, then one word."),
    )


@_u23_variant("vision", "ms", "intermediate", "stereo_pick_then_eyes_count")
def _vision_intermediate_ms_stereo_pick_then_eyes_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Two slightly different views help judge depth",
            "An illusion can be the brain's interpretation of cues",
        ),
        (
            "Stereo depth needs only one identical photo",
            "Pupils must publish a private eye-test score",
        ),
        2,
    )
    question = (
        "<p>A fictional 3D-cinema explainer describes depth perception.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the first statement from (i), enter how many eyes the "
        "stereo model needs.</p>"
    )
    solution = (
        "(i) Two views; illusion as interpretation.<br>"
        "(ii) <strong>2</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Depth needs two viewpoints; the brain "
        "interprets cues."
    )
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Eyes needed"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


@_u23_variant("vision", "ms", "difficult", "illusion_order_then_cue_pick_then_word")
def _vision_difficult_ms_illusion_order_then_cue_pick_then_word():
    order_raw, order_bank = _u23_order_field(
        (
            "The retina detects the lines as drawn",
            "The brain applies depth and size cues",
            "The interpretation mismatches the object",
        ),
        ("The lens votes on which line is longer",),
    )
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Measure the lines with a ruler to check the object",
            "Explain the mismatch as interpretation of cues",
        ),
        (
            "Rank classmates by who was fooled",
            "Store each viewer's eye-test score",
        ),
        2,
    )
    question = (
        "<p>A fictional psychology-of-perception page shows two equal lines "
        "that look unequal.</p>"
        "<p>(i) Order how the illusion arises.</p>"
        "<p>(ii) Using the last step from (i), select the two scientific responses.</p>"
        "<p>(iii) Write the one-word part of the eye that detected the lines in "
        "step 1.</p>"
    )
    solution = (
        "(i) <strong>retina detects → brain applies cues → mismatch</strong><br>"
        "(ii) Measure with a ruler; explain as interpretation.<br>"
        "(iii) <strong>retina</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Detection is faithful; interpretation adds "
        "cues; checking uses measurement, not a ranking."
    )
    return (
        question, solution, hint, 3,
        _fields((order_raw, pick_raw, "retina"),
                ("How it arises", "Responses", "Detecting part"),
                ("order", "pick", "keyword"), (order_bank, pick_bank, None),
                (None, pick_count, None),
                hint="Order, two responses, then one word."),
    )


_VI_MS_D_SURVEY_PACKS = (
    {"asked": 500, "lenses": 200},
    {"asked": 400, "lenses": 180},
    {"asked": 250, "lenses": 100},
)


@_u23_variant("vision", "ms", "difficult", "lens_pct_then_reading_mcq_then_word")
def _vision_difficult_ms_lens_pct_then_reading_mcq_then_word():
    pack = random.choice(_VI_MS_D_SURVEY_PACKS)
    pct = _pct(pack["lenses"], pack["asked"])
    correct = "a public aggregate about focusing errors, not a file on anyone"
    distractors = (
        "a reason to list which pupils wear glasses",
        "proof that everyone needs corrective lenses",
        "a ranking of whose eyesight is best",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook table reports that {pack['lenses']} of "
        f"{pack['asked']} adults in an anonymous survey use corrective lenses.</p>"
        "<p>(i) Calculate that as a whole-number percentage.</p>"
        "<p>(ii) The figure in (i) is</p>"
        "<p>(iii) Write the one-word term for the eye's shape-changing focus "
        "process that lenses help with.</p>"
    )
    solution = (
        f"(i) {pack['lenses']} ÷ {pack['asked']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>accommodation</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentage of a population; aggregate, not "
        "a pupil list; accommodation is the focus process."
    )
    return (
        question, solution, hint, 3,
        _fields((pct, letter, "accommodation"),
                ("Use lenses (%)", "What the figure is", "Focus process"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Percentage, reading, then one word."),
    )


@_u23_variant("vision", "ms", "difficult", "eye_letter_then_error_mcq_then_count")
def _vision_difficult_ms_eye_letter_then_error_mcq_then_count():
    diagram = str(eye_boxes(title="Fictional eye schematic"))
    correct = "near-sight: distant objects blur because focus falls short of the retina"
    distractors = (
        "far-sight: near objects blur because focus falls short of the retina",
        "an illusion: the brain misreads cues from the blurred image",
        "normal sight: the image lands exactly on the retina",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional optics schematic labels A lens, B retina, C path to "
        "the brain.</p>"
        "<p>(i) Enter the letter of the part that refracts light.</p>"
        "<p>(ii) If the part in (i) focuses light in front of B, that is called</p>"
        "<p>(iii) Enter how many focusing-error kinds the model names in total.</p>"
    )
    solution = (
        "(i) <strong>A</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>2</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> A bends light; focus short of the retina "
        "blurs distance; two error kinds exist."
    )
    return (
        question, solution, hint, 3,
        _fields(("A", letter, 2), ("Refracting part", "Focus in front of B", "Error kinds"),
                ("keyword", "mcq", "number"), (None, options, None),
                hint="Letter, error, then 2."),
    )


# vision — situational_multi_step (F, I, D)

_VI_SMS_F_DEMO_PACKS = (
    {"place": "fictional science-museum eye exhibit", "parts": 3},
    {"place": "fictional optician's window display", "parts": 3},
    {"place": "fictional classroom eye model", "parts": 3},
)


@_u23_variant("vision", "sms", "foundational", "exhibit_parts_then_lens_mcq")
def _vision_foundational_sms_exhibit_parts_then_lens_mcq():
    pack = random.choice(_VI_SMS_F_DEMO_PACKS)
    correct = "refracts light to help form an image"
    distractors = (
        "lets light in through a small hole",
        "detects the image at the back",
        "sends the signals to the brain",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['place']} labels {pack['parts']} parts: lens, retina and "
        "the path to the brain.</p>"
        "<p>(i) Enter the number of labelled parts.</p>"
        "<p>(ii) Using the first part from (i), the lens mainly</p>"
    )
    solution = (
        f"(i) <strong>{pack['parts']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Count the parts, then the lens bends light."
    return (
        question, solution, hint, 2,
        _fields((pack["parts"], letter), ("Labelled parts", "Lens role"),
                ("number", "mcq"), (None, options),
                hint="Count, then choose the lens role."),
    )


_VI_SMS_F_FILM_PACKS = (
    {"who": "Alex", "film": "fictional 3D film", "glasses": 2},
    {"who": "Sam", "film": "fictional planetarium show", "glasses": 2},
    {"who": "Jordan", "film": "fictional VR demo", "glasses": 2},
)


@_u23_variant("vision", "sms", "foundational", "film_lenses_then_stereo_pick")
def _vision_foundational_sms_film_lenses_then_stereo_pick():
    pack = random.choice(_VI_SMS_F_FILM_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Two slightly different views help judge depth",
            "The brain combines the two views",
        ),
        (
            "One identical picture gives full depth",
            f"{pack['who']} should publish an eye-test score",
        ),
        2,
    )
    question = (
        f"<p>{pack['who']} (fictional) watches a {pack['film']}; the special "
        f"glasses have {pack['glasses']} lenses, each showing a slightly "
        "different picture.</p>"
        "<p>(i) Enter the number of different pictures the glasses show.</p>"
        "<p>(ii) Using the pictures from (i), select the two statements that "
        "explain the 3D effect.</p>"
    )
    solution = (
        f"(i) <strong>{pack['glasses']}</strong><br>"
        "(ii) Two views; the brain combines them."
    )
    hint = "<strong>Key idea:</strong> Two views, combined by the brain, give depth."
    return (
        question, solution, hint, 2,
        _fields((pack["glasses"], pick_raw), ("Different pictures", "Explanation"),
                ("number", "pick"), (None, pick_bank), (None, pick_count),
                hint="Count, then two statements."),
    )


@_u23_variant("vision", "sms", "foundational", "camera_order_then_retina_word")
def _vision_foundational_sms_camera_order_then_retina_word():
    order_raw, order_bank = _u23_order_field(
        (
            "Light enters and is bent by the lens",
            "An image forms on the light-sensitive layer",
            "The signal is sent on to be processed",
        ),
        ("The camera ranks its owners by eyesight",),
    )
    question = (
        "<p>A fictional photography club compares a camera with the eye.</p>"
        "<p>(i) Order the three steps that both share.</p>"
        "<p>(ii) In the eye, the layer in step 2 of (i) is called the — write "
        "the one word.</p>"
    )
    solution = (
        "(i) <strong>bend → image forms → signal sent</strong><br>"
        "(ii) <strong>retina</strong>"
    )
    hint = "<strong>Key idea:</strong> Lens, then detector, then processing."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "retina"), ("Shared steps", "Eye's layer"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


_VI_SMS_I_CASE_PACKS = (
    {"who": "Riley", "where": "a fictional classroom", "far": "the board", "near": "a book"},
    {"who": "Casey", "where": "a fictional bus", "far": "the route sign", "near": "a phone screen"},
    {"who": "Morgan", "where": "a fictional theatre", "far": "the stage", "near": "the programme"},
)


@_u23_variant("vision", "sms", "intermediate", "case_blur_then_error_mcq_then_word")
def _vision_intermediate_sms_case_blur_then_error_mcq_then_word():
    pack = random.choice(_VI_SMS_I_CASE_PACKS)
    correct = "near-sight: distant objects are not in focus"
    distractors = (
        "far-sight: near objects are not in focus",
        f"a faulty retina: {pack['who']} cannot detect distant light",
        f"an illusion caused by the lighting in {pack['where']}",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional case, {pack['who']} in {pack['where']} sees "
        f"{pack['near']} clearly but {pack['far']} is blurred.</p>"
        "<p>(i) Enter how many of the two objects are blurred.</p>"
        "<p>(ii) Using the blurred object from (i), the pattern fits</p>"
        "<p>(iii) Write the one-word professional the story sends the character "
        "to (the app stores nothing).</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>optician</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Far blur with near clear is the near-sight "
        "pattern; a professional checks it, not the quiz."
    )
    return (
        question, solution, hint, 3,
        _fields((1, letter, "optician"), ("Blurred objects", "Pattern fits", "Professional"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, pattern, then one word."),
    )


_VI_SMS_I_DEMO_PACKS = (
    {"lab": "fictional physics lab", "near_cm": 25, "far_m": 6},
    {"lab": "fictional optics workshop", "near_cm": 30, "far_m": 5},
    {"lab": "fictional school demo", "near_cm": 20, "far_m": 4},
)


@_u23_variant("vision", "sms", "intermediate", "demo_distances_then_accom_order")
def _vision_intermediate_sms_demo_distances_then_accom_order():
    pack = random.choice(_VI_SMS_I_DEMO_PACKS)
    far_cm = pack["far_m"] * 100
    order_raw, order_bank = _u23_order_field(
        (
            "The object moves from far to near",
            "The lens changes shape (accommodation)",
            "The image stays focused on the retina",
        ),
        ("The retina moves to a new place in the eye",),
    )
    question = (
        f"<p>A {pack['lab']} model eye focuses on a card at {pack['near_cm']} cm "
        f"and then a poster {pack['far_m']} m away.</p>"
        "<p>(i) Enter the poster distance in centimetres.</p>"
        "<p>(ii) Using the change between the two distances from (i), order how "
        "the eye keeps both in focus.</p>"
    )
    solution = (
        f"(i) {pack['far_m']} × 100 = <strong>{far_cm}</strong> cm<br>"
        "(ii) <strong>object moves → lens reshapes → image stays focused</strong>"
    )
    hint = "<strong>Key idea:</strong> Convert units, then accommodation keeps focus."
    return (
        question, solution, hint, 2,
        _fields((far_cm, order_raw), ("Poster distance (cm)", "Keeping focus"),
                ("number", "order"), (None, order_bank),
                hint="Convert, then order three steps."),
    )


@_u23_variant("vision", "sms", "intermediate", "illusion_show_pick_then_cue_keyword")
def _vision_intermediate_sms_illusion_show_pick_then_cue_keyword():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The brain interprets cues, so the drawing can look different from the object",
            "Measuring the drawing checks what is really there",
        ),
        (
            "The audience should be ranked by who was fooled",
            "The retina must be broken in everyone fooled",
        ),
        2,
    )
    question = (
        "<p>A fictional street performer shows a drawing that looks bent but "
        "is straight.</p>"
        "<p>(i) Select the two scientific explanations.</p>"
        "<p>(ii) Using the first explanation from (i), write the one-word organ "
        "that does the interpreting.</p>"
    )
    solution = (
        "(i) Interpretation of cues; measure to check.<br>"
        "(ii) <strong>brain</strong>"
    )
    hint = "<strong>Key idea:</strong> The eye detects; the brain interprets."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, "brain"), ("Explanations", "Interpreting organ"),
                ("pick", "keyword"), (pick_bank, None), (pick_count, None),
                hint="Two explanations, then one word."),
    )


_VI_SMS_D_SCREEN_PACKS = (
    {"study": "fictional school-nurse aggregate", "asked": 300, "referred": 45},
    {"study": "fictional public-health screening report", "asked": 600, "referred": 120},
    {"study": "fictional textbook screening dataset", "asked": 200, "referred": 30},
)


@_u23_variant("vision", "sms", "difficult", "screening_pct_then_caution_pick_then_verdict")
def _vision_difficult_sms_screening_pct_then_caution_pick_then_verdict():
    pack = random.choice(_VI_SMS_D_SCREEN_PACKS)
    pct = _pct(pack["referred"], pack["asked"])
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "A screening referral is not a diagnosis",
            "The figure is an anonymous aggregate, not a list of pupils",
        ),
        (
            "The referred pupils should be named in class",
            "The percentage proves everyone else has perfect sight",
        ),
        2,
    )
    correct = "some children may need a professional eye check; the report itself diagnoses nobody"
    distractors = (
        "the school should rank pupils by eyesight",
        "every referred child needs glasses",
        "the report should store each child's prescription",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} says {pack['referred']} of {pack['asked']} "
        "children screened were referred for a full eye check.</p>"
        "<p>(i) Calculate the referral rate as a whole-number percentage.</p>"
        "<p>(ii) Using the rate from (i), select the two fair readings.</p>"
        "<p>(iii) Given (ii), the report's conclusion is that</p>"
    )
    solution = (
        f"(i) {pack['referred']} ÷ {pack['asked']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) Referral is not diagnosis; aggregate not a list.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Percentage, then screening ≠ diagnosis, "
        "and aggregates never name pupils."
    )
    return (
        question, solution, hint, 3,
        _fields((pct, pick_raw, letter), ("Referral rate (%)", "Fair readings", "Conclusion"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Percentage, two readings, then the conclusion."),
    )


_VI_SMS_D_RAY_PACKS = (
    {"lab": "fictional optics bench", "focal_cm": 20, "object_cm": 40},
    {"lab": "fictional lens kit", "focal_cm": 10, "object_cm": 30},
    {"lab": "fictional camera workshop", "focal_cm": 15, "object_cm": 45},
)


@_u23_variant("vision", "sms", "difficult", "bench_ratio_then_model_order_then_word")
def _vision_difficult_sms_bench_ratio_then_model_order_then_word():
    pack = random.choice(_VI_SMS_D_RAY_PACKS)
    ratio = pack["object_cm"] // pack["focal_cm"]
    order_raw, order_bank = _u23_order_field(
        (
            "Rays from the object are refracted by the lens",
            "The rays converge to form an image on the screen",
            "Moving the object changes where the image forms",
        ),
        ("The screen votes on the image position",),
    )
    question = (
        f"<p>On a {pack['lab']}, a converging lens of focal length "
        f"{pack['focal_cm']} cm forms an image of a lamp placed "
        f"{pack['object_cm']} cm away on a screen.</p>"
        "<p>(i) How many focal lengths away is the lamp?</p>"
        "<p>(ii) Using the set-up from (i), order what the bench shows.</p>"
        "<p>(iii) In the eye, the screen's job is done by the — write the one word.</p>"
    )
    solution = (
        f"(i) {pack['object_cm']} ÷ {pack['focal_cm']} = <strong>{ratio}</strong><br>"
        "(ii) <strong>refract → converge → image moves with object</strong><br>"
        "(iii) <strong>retina</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Divide distances, follow the rays, then map "
        "the screen to the retina."
    )
    return (
        question, solution, hint, 3,
        _fields((ratio, order_raw, "retina"), ("Focal lengths", "What the bench shows", "Eye's screen"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Ratio, three steps, then one word."),
    )


@_u23_variant("vision", "sms", "difficult", "clinic_pick_then_signpost_mcq")
def _vision_difficult_sms_clinic_pick_then_signpost_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Prescriptions stay with the clinic, not in a class quiz",
            "Corrective lenses adjust where light focuses",
        ),
        (
            "The clinic should publish a league of best eyesight",
            "Glasses cure illusions",
        ),
        2,
    )
    correct = "refer the character to an optician; the app stores no prescription"
    distractors = (
        "type the character's prescription into the quiz",
        "compare the character with classmates",
        "tell the character to cover one eye to fix the blur",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional documentary follows an eye clinic for a day.</p>"
        "<p>(i) Select the two statements consistent with the documentary.</p>"
        "<p>(ii) Using the first statement from (i), if a fictional character "
        "in the film reports blurred distance vision, the right response is to</p>"
    )
    solution = (
        "(i) Prescriptions stay clinical; lenses adjust focus.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Clinical records are clinical; the app signposts."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Consistent statements", "Response"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the response."),
    )


VISION_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _vision_intermediate_ms_errors_count_then_blur_mcq,
        _vision_intermediate_ms_path_order_then_accommodation_word,
        _vision_intermediate_ms_stereo_pick_then_eyes_count,
    ],
    "difficult": [
        _vision_difficult_ms_illusion_order_then_cue_pick_then_word,
        _vision_difficult_ms_lens_pct_then_reading_mcq_then_word,
        _vision_difficult_ms_eye_letter_then_error_mcq_then_count,
    ],
}

VISION_SMS_POOLS = {
    "foundational": [
        _vision_foundational_sms_exhibit_parts_then_lens_mcq,
        _vision_foundational_sms_film_lenses_then_stereo_pick,
        _vision_foundational_sms_camera_order_then_retina_word,
    ],
    "intermediate": [
        _vision_intermediate_sms_case_blur_then_error_mcq_then_word,
        _vision_intermediate_sms_demo_distances_then_accom_order,
        _vision_intermediate_sms_illusion_show_pick_then_cue_keyword,
    ],
    "difficult": [
        _vision_difficult_sms_screening_pct_then_caution_pick_then_verdict,
        _vision_difficult_sms_bench_ratio_then_model_order_then_word,
        _vision_difficult_sms_clinic_pick_then_signpost_mcq,
    ],
}


# ---------------------------------------------------------------------------
# hearing — multi_step (I, D); foundational MS stays — (matrix)
# ---------------------------------------------------------------------------

_HE_MS_I_TABLE_PACKS = (
    {"rows": (("whisper", 30), ("normal talk", 60), ("busy road", 80)), "loudest": "busy road"},
    {"rows": (("library", 40), ("vacuum cleaner", 70), ("motorbike", 90)), "loudest": "motorbike"},
    {"rows": (("rustling leaves", 20), ("rainfall", 50), ("lawnmower", 90)), "loudest": "lawnmower"},
)


@_u23_variant("hearing", "ms", "intermediate", "table_loudest_then_medium_mcq")
def _hearing_intermediate_ms_table_loudest_then_medium_mcq():
    pack = random.choice(_HE_MS_I_TABLE_PACKS)
    rows = pack["rows"]
    loudest_db = max(v for _, v in rows)
    correct = "vibration that needs a medium such as air to travel"
    distractors = (
        "a wave that travels fastest through empty space",
        "a vibration that gets louder the further it travels",
        "light of a very low frequency",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional textbook table gives sound levels in decibels: "
        + ", ".join(f"{name} {db} dB" for name, db in rows)
        + ".</p>"
        "<p>(i) Enter the highest level in the table.</p>"
        "<p>(ii) Every sound in the table, including the one in (i), is</p>"
    )
    solution = (
        f"(i) <strong>{loudest_db}</strong> dB ({pack['loudest']})<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Read the table, then recall sound is vibration in a medium."
    return (
        question, solution, hint, 2,
        _fields((loudest_db, letter), ("Highest level (dB)", "Sound is"),
                ("number", "mcq"), (None, options),
                hint="Read the maximum, then choose the definition."),
    )


@_u23_variant("hearing", "ms", "intermediate", "ear_order_then_cochlea_word")
def _hearing_intermediate_ms_ear_order_then_cochlea_word():
    order_raw, order_bank = _u23_order_field(
        (
            "The outer ear collects sound",
            "The middle ear passes vibration inward",
            "The inner ear senses the vibration",
        ),
        ("The quiz ranks whose hearing is best",),
    )
    question = (
        "<p>A fictional anatomy worksheet traces sound through the ear.</p>"
        "<p>(i) Order the three regions.</p>"
        "<p>(ii) Name the coiled sensing structure in the last region of (i) — one word.</p>"
    )
    solution = (
        "(i) <strong>outer → middle → inner</strong><br>"
        "(ii) <strong>cochlea</strong>"
    )
    hint = "<strong>Key idea:</strong> Collect, pass on, sense — and the sensing coil is the cochlea."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "cochlea"), ("Sound path", "Sensing structure"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three regions, then one word."),
    )


@_u23_variant("hearing", "ms", "intermediate", "localise_pick_then_ears_count")
def _hearing_intermediate_ms_localise_pick_then_ears_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Sound reaches the nearer ear slightly earlier and louder",
            "The brain compares the two ears to locate the source",
        ),
        (
            "One ear alone locates sources perfectly",
            "The app should store who uses a hearing aid",
        ),
        2,
    )
    question = (
        "<p>A fictional physics poster explains how a listener locates a sound.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the comparison in (i), enter how many ears the model uses.</p>"
    )
    solution = (
        "(i) Nearer ear earlier/louder; brain compares.<br>"
        "(ii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Two ears give two signals to compare."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Ears used"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


_HE_MS_D_NOISE_PACKS = (
    {"workers": 400, "loss": 60},
    {"workers": 250, "loss": 50},
    {"workers": 500, "loss": 100},
)


@_u23_variant("hearing", "ms", "difficult", "noise_pct_then_control_order_then_word")
def _hearing_difficult_ms_noise_pct_then_control_order_then_word():
    pack = random.choice(_HE_MS_D_NOISE_PACKS)
    pct = _pct(pack["loss"], pack["workers"])
    order_raw, order_bank = _u23_order_field(
        (
            "Measure the noise level at the workplace",
            "Reduce exposure with quieter machines or ear protection",
            "Re-check the rate of hearing loss over time",
        ),
        ("Publish the names of the affected workers",),
    )
    question = (
        f"<p>A fictional occupational-health table reports {pack['loss']} cases of "
        f"noise-linked hearing loss among {pack['workers']} factory workers.</p>"
        "<p>(i) Calculate that as a whole-number percentage.</p>"
        "<p>(ii) Given the rate in (i), order the scientific response.</p>"
        "<p>(iii) Write the one-word unit used for the noise level in step 1.</p>"
    )
    solution = (
        f"(i) {pack['loss']} ÷ {pack['workers']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) <strong>measure → reduce exposure → re-check</strong><br>"
        "(iii) <strong>decibel</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, measure–reduce–recheck, decibels."
    return (
        question, solution, hint, 3,
        _fields((pct, order_raw, "decibel"), ("Hearing loss (%)", "Response", "Unit"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Percentage, three steps, then one word."),
    )


@_u23_variant("hearing", "ms", "difficult", "vacuum_pick_then_ear_letter_then_mcq")
def _hearing_difficult_ms_vacuum_pick_then_ear_letter_then_mcq():
    diagram = str(ear_boxes(title="Fictional ear schematic"))
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The bell is silent because there is no medium to carry vibration",
            "Light from the bell still reaches the observer",
        ),
        (
            "Sound travels best in a vacuum",
            "The observer's hearing should be ranked",
        ),
        2,
    )
    correct = "the inner ear, where vibration is sensed"
    distractors = (
        "the outer ear, which collects sound",
        "the middle ear, which passes vibration on",
        "the eardrum, where sound is interpreted",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional demonstration rings a bell inside a jar as the air is "
        "pumped out; the schematic labels A outer, B middle, C inner ear.</p>"
        "<p>(i) Select the two correct observations.</p>"
        "<p>(ii) When air is let back in, vibration reaches which letter last?</p>"
        "<p>(iii) The region at the letter in (ii) is</p>"
    )
    solution = (
        "(i) No medium, no sound; light still arrives.<br>"
        "(ii) <strong>C</strong><br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> No medium, no sound; the path ends at the inner ear."
    return (
        question, solution, hint, 3,
        _fields((pick_raw, "C", letter), ("Observations", "Last letter", "Region"),
                ("pick", "keyword", "mcq"), (pick_bank, None, options), (pick_count, None, None),
                hint="Two observations, letter C, then the region."),
    )


_HE_MS_D_ILLUSION_PACKS = (
    {"clip": "a fictional audio clip that seems to rise in pitch forever"},
    {"clip": "a fictional recording where one word is heard two ways"},
    {"clip": "a fictional tone that seems to move around the room"},
)


@_u23_variant("hearing", "ms", "difficult", "illusion_mcq_then_order_then_count")
def _hearing_difficult_ms_illusion_mcq_then_order_then_count():
    pack = random.choice(_HE_MS_D_ILLUSION_PACKS)
    correct = "the brain interpreting cues in a way that mismatches the sound"
    distractors = (
        "proof that the listeners' ears are damaged",
        "a sound that reaches the ear without any vibration",
        "a sign the sound was travelling through a vacuum",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    order_raw, order_bank = _u23_order_field(
        (
            "The ears detect the vibrations faithfully",
            "The brain applies expectations and cues",
            "The interpretation differs from the recording",
        ),
        ("The cochlea invents a new sound",),
    )
    question = (
        f"<p>A fictional science show plays {pack['clip']}.</p>"
        "<p>(i) An auditory illusion like this is</p>"
        "<p>(ii) Using the idea in (i), order how the illusion arises.</p>"
        "<p>(iii) Enter how many ears the brain compares in step 1.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>detect → apply cues → mismatch</strong><br>"
        "(iii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Faithful detection, interpreted cues, two ears."
    return (
        question, solution, hint, 3,
        _fields((letter, order_raw, 2), ("Illusion is", "How it arises", "Ears compared"),
                ("mcq", "order", "number"), (options, order_bank, None),
                hint="Choose, order three steps, then enter 2."),
    )


# hearing — situational_multi_step (F, I, D)

_HE_SMS_F_CONCERT_PACKS = (
    {"where": "fictional school concert", "speakers": 2},
    {"where": "fictional village fête", "speakers": 4},
    {"where": "fictional drama rehearsal", "speakers": 2},
)


@_u23_variant("hearing", "sms", "foundational", "concert_speakers_then_vibration_mcq")
def _hearing_foundational_sms_concert_speakers_then_vibration_mcq():
    pack = random.choice(_HE_SMS_F_CONCERT_PACKS)
    correct = "vibration travelling through the air to the listeners' ears"
    distractors = (
        "a wave that needs no air to travel",
        "electricity flowing through the air to the listeners",
        "light travelling from the speakers to the listeners' eyes",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>At a {pack['where']}, {pack['speakers']} loudspeakers play to the hall.</p>"
        "<p>(i) Enter the number of loudspeakers.</p>"
        "<p>(ii) The sound from the speakers in (i) reaches the audience as</p>"
    )
    solution = (
        f"(i) <strong>{pack['speakers']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Count, then sound is vibration in air."
    return (
        question, solution, hint, 2,
        _fields((pack["speakers"], letter), ("Loudspeakers", "Sound reaches audience as"),
                ("number", "mcq"), (None, options),
                hint="Count, then choose the vibration idea."),
    )


_HE_SMS_F_ECHO_PACKS = (
    {"where": "fictional canyon", "claps": 3},
    {"where": "fictional empty sports hall", "claps": 2},
    {"where": "fictional tunnel", "claps": 4},
)


@_u23_variant("hearing", "sms", "foundational", "echo_claps_then_ear_pick")
def _hearing_foundational_sms_echo_claps_then_ear_pick():
    pack = random.choice(_HE_SMS_F_ECHO_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The outer ear collects the returning sound",
            "The inner ear senses the vibration",
        ),
        (
            "Sound travels best where there is no air",
            "The hikers should rank whose hearing is best",
        ),
        2,
    )
    question = (
        f"<p>Fictional hikers in a {pack['where']} clap {pack['claps']} times and hear "
        "each clap return as an echo.</p>"
        "<p>(i) Enter the number of echoes they hear.</p>"
        "<p>(ii) Using the echoes from (i), select the two statements about how "
        "the ear receives them.</p>"
    )
    solution = (
        f"(i) <strong>{pack['claps']}</strong><br>"
        "(ii) Outer ear collects; inner ear senses."
    )
    hint = "<strong>Key idea:</strong> One echo per clap; collect then sense."
    return (
        question, solution, hint, 2,
        _fields((pack["claps"], pick_raw), ("Echoes", "How the ear receives them"),
                ("number", "pick"), (None, pick_bank), (None, pick_count),
                hint="Count, then two statements."),
    )


@_u23_variant("hearing", "sms", "foundational", "drum_order_then_medium_word")
def _hearing_foundational_sms_drum_order_then_medium_word():
    order_raw, order_bank = _u23_order_field(
        (
            "The drum skin vibrates",
            "The air carries the vibration across the room",
            "The listener's ear collects and senses it",
        ),
        ("The drum ranks the listeners",),
    )
    question = (
        "<p>A fictional music teacher demonstrates a drum to a class.</p>"
        "<p>(i) Order how the sound reaches a listener.</p>"
        "<p>(ii) Using step 2 of (i), write the one-word name for the substance "
        "sound travels through.</p>"
    )
    solution = (
        "(i) <strong>drum vibrates → air carries → ear senses</strong><br>"
        "(ii) <strong>medium</strong>"
    )
    hint = "<strong>Key idea:</strong> Source, medium, receiver."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "medium"), ("Sound path", "Term"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


_HE_SMS_I_CASE_PACKS = (
    {"who": "Riley", "role": "a fictional grandparent character", "device": "hearing aid"},
    {"who": "Casey", "role": "a fictional sound engineer", "device": "hearing aid"},
    {"who": "Morgan", "role": "a fictional teacher character", "device": "hearing aid"},
)


@_u23_variant("hearing", "sms", "intermediate", "case_aid_pick_then_order")
def _hearing_intermediate_sms_case_aid_pick_then_order():
    pack = random.choice(_HE_SMS_I_CASE_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            f"A {pack['device']} is a tool that can help; the app stores nothing about it",
            "The device makes vibrations easier for the inner ear to sense",
        ),
        (
            f"{pack['who']} should be ranked against classmates",
            "The device replaces the need for a medium",
        ),
        2,
    )
    order_raw, order_bank = _u23_order_field(
        (
            "Sound is collected by the outer ear",
            "The device amplifies the vibration",
            "The inner ear senses the stronger vibration",
        ),
        ("The app records who uses the device",),
    )
    question = (
        f"<p>In a fictional story, {pack['who']}, {pack['role']}, uses a "
        f"{pack['device']}.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), order how the device fits "
        "into the sound path.</p>"
    )
    solution = (
        "(i) A helpful tool, nothing stored; easier to sense.<br>"
        "(ii) <strong>collect → amplify → sense</strong>"
    )
    hint = "<strong>Key idea:</strong> A tool that amplifies, placed between collecting and sensing."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "Device in the path"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_HE_SMS_I_SURVEY_PACKS = (
    {"place": "fictional school corridor", "readings": (55, 70, 85), "limit": 80},
    {"place": "fictional station platform", "readings": (60, 75, 90), "limit": 85},
    {"place": "fictional workshop", "readings": (65, 80, 95), "limit": 85},
)


@_u23_variant("hearing", "sms", "intermediate", "survey_over_limit_then_action_mcq_then_word")
def _hearing_intermediate_sms_survey_over_limit_then_action_mcq_then_word():
    pack = random.choice(_HE_SMS_I_SURVEY_PACKS)
    over = sum(1 for r in pack["readings"] if r > pack["limit"])
    correct = "reduce the noise or add protection at that spot; no one's hearing is tested"
    distractors = (
        "test each pupil's hearing in the quiz",
        "rank people by who complains least",
        "ignore it because loud sound cannot harm hearing",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    chart = bar_chart(
        ["Spot 1", "Spot 2", "Spot 3"],
        list(pack["readings"]),
        title="Fictional noise survey",
        desc="Three noise readings in decibels at three spots.",
    )
    question = (
        str(chart)
        + f"<p>A fictional noise survey of a {pack['place']} records "
        + ", ".join(f"{r} dB" for r in pack["readings"])
        + f" at three spots; the guideline limit is {pack['limit']} dB.</p>"
        "<p>(i) Enter how many spots exceed the limit.</p>"
        "<p>(ii) For the spot(s) counted in (i), the public-health action is to</p>"
        "<p>(iii) Write the one-word unit of the readings.</p>"
    )
    solution = (
        f"(i) <strong>{over}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>decibel</strong>"
    )
    hint = "<strong>Key idea:</strong> Compare with the limit, fix the place not the people."
    return (
        question, solution, hint, 3,
        _fields((over, letter, "decibel"), ("Spots over limit", "Action", "Unit"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, action, then one word."),
    )


_HE_SMS_I_LOCATE_PACKS = (
    {"who": "Alex", "where": "a fictional forest", "source": "a bird call"},
    {"who": "Sam", "where": "a fictional dark cave", "source": "dripping water"},
    {"who": "Jordan", "where": "a fictional foggy harbour", "source": "a foghorn"},
)


@_u23_variant("hearing", "sms", "intermediate", "locate_ears_then_reason_mcq")
def _hearing_intermediate_sms_locate_ears_then_reason_mcq():
    pack = random.choice(_HE_SMS_I_LOCATE_PACKS)
    correct = "the sound reaches one ear slightly earlier and louder, and the brain compares"
    distractors = (
        "one ear is enough because sound has no direction",
        f"{pack['who']} feels the vibration through the skin",
        "the outer ear points itself at the source",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional story, {pack['who']} in {pack['where']} turns towards "
        f"{pack['source']} without seeing it.</p>"
        "<p>(i) Enter how many ears the character uses to locate the source.</p>"
        "<p>(ii) Using the number from (i), the character can locate it because</p>"
    )
    solution = (
        "(i) <strong>2</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Two ears, two slightly different signals."
    return (
        question, solution, hint, 2,
        _fields((2, letter), ("Ears used", "Why it works"),
                ("number", "mcq"), (None, options),
                hint="Enter 2, then choose the comparison idea."),
    )


_HE_SMS_D_ECHO_PACKS = (
    {"where": "fictional cliff", "t": 2, "v": 340, "d": 340},
    {"where": "fictional quarry wall", "t": 1, "v": 340, "d": 170},
    {"where": "fictional ship's sonar test", "t": 4, "v": 1500, "d": 3000},
)


@_u23_variant("hearing", "sms", "difficult", "echo_distance_then_order_then_word")
def _hearing_difficult_sms_echo_distance_then_order_then_word():
    pack = random.choice(_HE_SMS_D_ECHO_PACKS)
    order_raw, order_bank = _u23_order_field(
        (
            "The sound travels out through the medium",
            "It reflects from the surface",
            "The returning vibration is sensed by the ear or sensor",
        ),
        ("The echo returns instantly with no medium",),
    )
    question = (
        f"<p>At a {pack['where']}, a fictional surveyor hears an echo {pack['t']} s "
        f"after a clap; sound travels at {pack['v']} m/s in that medium.</p>"
        "<p>(i) Calculate the distance to the reflecting surface (the sound goes "
        "there and back).</p>"
        "<p>(ii) Using the journey in (i), order what happens to the sound.</p>"
        "<p>(iii) Write the one-word term for the returning sound.</p>"
    )
    solution = (
        f"(i) {pack['v']} × {pack['t']} ÷ 2 = <strong>{pack['d']}</strong> m<br>"
        "(ii) <strong>travel out → reflect → sensed on return</strong><br>"
        "(iii) <strong>echo</strong>"
    )
    hint = "<strong>Key idea:</strong> Distance = speed × time ÷ 2 for a round trip."
    return (
        question, solution, hint, 3,
        _fields((pack["d"], order_raw, "echo"), ("Distance (m)", "Sound journey", "Term"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Halve the round trip, order three steps, then one word."),
    )


_HE_SMS_D_STUDY_PACKS = (
    {"study": "fictional audiology teaching dataset", "users": 200, "improved": 150},
    {"study": "fictional public hearing-service report", "users": 400, "improved": 320},
    {"study": "fictional university trial", "users": 100, "improved": 80},
)


@_u23_variant("hearing", "sms", "difficult", "aid_pct_then_caution_pick_then_verdict")
def _hearing_difficult_sms_aid_pct_then_caution_pick_then_verdict():
    pack = random.choice(_HE_SMS_D_STUDY_PACKS)
    pct = _pct(pack["improved"], pack["users"])
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Improvement was self-reported, so some answers may be inaccurate",
            "The figures are anonymous aggregates, not files on named users",
        ),
        (
            "The users should be listed in class",
            "The percentage proves every device works for everyone",
        ),
        2,
    )
    correct = "hearing aids helped most users in this group, within the limits of the study"
    distractors = (
        "hearing aids cure hearing loss for every user",
        "users should be ranked by hearing",
        "the study should store each user's test",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} reports that {pack['improved']} of {pack['users']} "
        "hearing-aid users said conversation became easier.</p>"
        "<p>(i) Calculate that as a whole-number percentage.</p>"
        "<p>(ii) Using the figure from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['improved']} ÷ {pack['users']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) Self-report; anonymous aggregate.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, design cautions, honest verdict."
    return (
        question, solution, hint, 3,
        _fields((pct, pick_raw, letter), ("Improved (%)", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Percentage, two cautions, then the verdict."),
    )


@_u23_variant("hearing", "sms", "difficult", "space_pick_then_medium_mcq")
def _hearing_difficult_sms_space_pick_then_medium_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Sound needs a medium, so it cannot cross the vacuum between ships",
            "Radio (light-family waves) can cross the vacuum",
        ),
        (
            "Shouting louder would cross the vacuum",
            "The crew should rank whose hearing is best",
        ),
        2,
    )
    correct = "inside the cabin, the air carries the vibration to the crew's ears"
    distractors = (
        "inside the cabin there is still no medium",
        "sound needs no medium over short distances",
        "radio waves carry their voices inside the cabin",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>In a fictional space film, two ships pass in silence but the crew "
        "can talk inside their cabin.</p>"
        "<p>(i) Select the two scientific statements about the silence outside.</p>"
        "<p>(ii) Using the medium idea from (i), the crew can talk because</p>"
    )
    solution = (
        "(i) No medium outside; radio can cross.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> No air, no sound; air inside carries speech."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Why talk works inside"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the reason."),
    )


HEARING_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _hearing_intermediate_ms_table_loudest_then_medium_mcq,
        _hearing_intermediate_ms_ear_order_then_cochlea_word,
        _hearing_intermediate_ms_localise_pick_then_ears_count,
    ],
    "difficult": [
        _hearing_difficult_ms_noise_pct_then_control_order_then_word,
        _hearing_difficult_ms_vacuum_pick_then_ear_letter_then_mcq,
        _hearing_difficult_ms_illusion_mcq_then_order_then_count,
    ],
}

HEARING_SMS_POOLS = {
    "foundational": [
        _hearing_foundational_sms_concert_speakers_then_vibration_mcq,
        _hearing_foundational_sms_echo_claps_then_ear_pick,
        _hearing_foundational_sms_drum_order_then_medium_word,
    ],
    "intermediate": [
        _hearing_intermediate_sms_case_aid_pick_then_order,
        _hearing_intermediate_sms_survey_over_limit_then_action_mcq_then_word,
        _hearing_intermediate_sms_locate_ears_then_reason_mcq,
    ],
    "difficult": [
        _hearing_difficult_sms_echo_distance_then_order_then_word,
        _hearing_difficult_sms_aid_pct_then_caution_pick_then_verdict,
        _hearing_difficult_sms_space_pick_then_medium_mcq,
    ],
}


# ---------------------------------------------------------------------------
# touch — multi_step (I, D); situational (I, D). Foundational stays — (matrix):
# no personal two-point test is ever needed or appropriate; data is supplied.
# ---------------------------------------------------------------------------

_TO_MS_I_TABLE_PACKS = (
    {"rows": (("fingertip", 2), ("palm", 10), ("back", 40)), "dense": "fingertip"},
    {"rows": (("lips", 2), ("forearm", 30), ("calf", 45)), "dense": "lips"},
    {"rows": (("fingertip", 3), ("shoulder", 35), ("thigh", 40)), "dense": "fingertip"},
)


@_u23_variant("touch", "ms", "intermediate", "table_smallest_then_density_mcq")
def _touch_intermediate_ms_table_smallest_then_density_mcq():
    pack = random.choice(_TO_MS_I_TABLE_PACKS)
    rows = pack["rows"]
    smallest = min(v for _, v in rows)
    correct = "the region with the most densely packed touch receptors"
    distractors = (
        "the region with the fewest receptors",
        "the region with the thickest skin",
        "the region with the largest surface area",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional textbook table of supplied two-point-threshold data gives: "
        + ", ".join(f"{name} {mm} mm" for name, mm in rows)
        + ".</p>"
        "<p>(i) Enter the smallest threshold in the table.</p>"
        f"<p>(ii) The region with the value in (i) ({pack['dense']}) is</p>"
    )
    solution = (
        f"(i) <strong>{smallest}</strong> mm<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Smaller threshold = denser receptors."
    return (
        question, solution, hint, 2,
        _fields((smallest, letter), ("Smallest threshold (mm)", "That region is"),
                ("number", "mcq"), (None, options),
                hint="Read the minimum, then the density idea."),
    )


@_u23_variant("touch", "ms", "intermediate", "receptor_pick_then_count")
def _touch_intermediate_ms_receptor_pick_then_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Pressure or contact receptors",
            "Temperature receptors",
            "Pain receptors that warn of damage",
        ),
        (
            "Receptors that rank whose skin is toughest",
            "Receptors that store a private body map",
        ),
        3,
    )
    question = (
        "<p>A fictional revision card lists skin receptor types.</p>"
        "<p>(i) Select the three receptor types.</p>"
        "<p>(ii) Enter how many types you selected in (i).</p>"
    )
    solution = (
        "(i) Pressure; temperature; pain.<br>"
        "(ii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Three receptor types; ranking skin is not one."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Receptor types", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


@_u23_variant("touch", "ms", "intermediate", "reflex_order_then_pain_word")
def _touch_intermediate_ms_reflex_order_then_pain_word():
    order_raw, order_bank = _u23_order_field(
        (
            "A receptor in the skin detects the hot surface",
            "A signal travels along a nerve",
            "The hand is pulled away before damage spreads",
        ),
        ("The class votes on whether it was hot",),
    )
    question = (
        "<p>A fictional safety poster shows a hand touching a hot pan in a "
        "cartoon.</p>"
        "<p>(i) Order the protective chain.</p>"
        "<p>(ii) Write the one-word receptor type in step 1 of (i) that warns "
        "of possible damage.</p>"
    )
    solution = (
        "(i) <strong>detect → nerve signal → pull away</strong><br>"
        "(ii) <strong>pain</strong>"
    )
    hint = "<strong>Key idea:</strong> Detect, signal, act; pain receptors warn."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "pain"), ("Protective chain", "Receptor type"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


_TO_MS_D_RATIO_PACKS = (
    {"a": ("fingertip", 2), "b": ("back", 40)},
    {"a": ("lips", 2), "b": ("calf", 44)},
    {"a": ("fingertip", 3), "b": ("thigh", 45)},
)


@_u23_variant("touch", "ms", "difficult", "ratio_then_density_order_then_word")
def _touch_difficult_ms_ratio_then_density_order_then_word():
    pack = random.choice(_TO_MS_D_RATIO_PACKS)
    (a_name, a_mm), (b_name, b_mm) = pack["a"], pack["b"]
    ratio = b_mm // a_mm
    order_raw, order_bank = _u23_order_field(
        (
            f"Receptors are packed more densely in the {a_name}",
            "Two nearby points stimulate different receptors there",
            "So two points are felt as two at a smaller separation",
        ),
        ("So the region should be ranked as the toughest skin",),
    )
    question = (
        f"<p>Supplied data from a fictional textbook: two-point threshold {a_mm} mm for the "
        f"{a_name} and {b_mm} mm for the {b_name}.</p>"
        f"<p>(i) How many times larger is the {b_name} threshold?</p>"
        f"<p>(ii) Using the comparison from (i), order why the {a_name} is more "
        "sensitive.</p>"
        "<p>(iii) Write the one-word property of receptor packing that explains it.</p>"
    )
    solution = (
        f"(i) {b_mm} ÷ {a_mm} = <strong>{ratio}</strong><br>"
        "(ii) <strong>denser packing → different receptors → felt as two</strong><br>"
        "(iii) <strong>density</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then denser packing means finer discrimination."
    return (
        question, solution, hint, 3,
        _fields((ratio, order_raw, "density"), ("Times larger", "Why more sensitive", "Property"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Ratio, three steps, then one word."),
    )


@_u23_variant("touch", "ms", "difficult", "method_pick_then_consent_mcq_then_count")
def _touch_difficult_ms_method_pick_then_consent_mcq_then_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Use supplied aggregate data rather than testing classmates",
            "Compare regions, never people",
        ),
        (
            "Touch pupils without consent to collect data",
            "Store a private body map in the app",
        ),
        2,
    )
    correct = "a consented, aggregated measurement of regions, not a league of bodies"
    distractors = (
        "a ranking of whose skin is toughest",
        "a reason to store each pupil's map",
        "a test pupils must do on each other",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional textbook explains how two-point-threshold tables are made.</p>"
        "<p>(i) Select the two rules the lesson follows.</p>"
        "<p>(ii) Under the rules from (i), a published threshold table is</p>"
        "<p>(iii) Enter how many receptor types (pressure, temperature, pain) that is.</p>"
    )
    solution = (
        "(i) Supplied data; compare regions not people.<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Supplied, consented, aggregate — and three receptor types."
    return (
        question, solution, hint, 3,
        _fields((pick_raw, letter, 3), ("Rules", "Published table is", "Receptor types"),
                ("pick", "mcq", "number"), (pick_bank, options, None), (pick_count, None, None),
                hint="Two rules, the reading, then 3."),
    )


_TO_MS_D_TEMP_PACKS = (
    {"warm": 40, "cool": 15, "diff": 25},
    {"warm": 38, "cool": 12, "diff": 26},
    {"warm": 42, "cool": 20, "diff": 22},
)


@_u23_variant("touch", "ms", "difficult", "temp_diff_then_receptor_mcq_then_word")
def _touch_difficult_ms_temp_diff_then_receptor_mcq_then_word():
    pack = random.choice(_TO_MS_D_TEMP_PACKS)
    correct = "temperature receptors, which detect hot or cold"
    distractors = (
        "pressure receptors, which detect contact",
        "pain receptors, which warn of damage",
        "smell receptors, which detect chemicals",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional lab demonstration uses two water baths at {pack['warm']} °C "
        f"and {pack['cool']} °C with a model 'skin' probe.</p>"
        "<p>(i) Calculate the temperature difference.</p>"
        "<p>(ii) The difference in (i) would be detected in real skin by</p>"
        "<p>(iii) If the warm bath were hot enough to damage skin, write the "
        "one-word receptor type that would warn.</p>"
    )
    solution = (
        f"(i) {pack['warm']} − {pack['cool']} = <strong>{pack['diff']}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>pain</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, temperature receptors, pain warns of damage."
    return (
        question, solution, hint, 3,
        _fields((pack["diff"], letter, "pain"), ("Difference (°C)", "Detected by", "Warning receptor"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


# touch — situational_multi_step (I, D only)

_TO_SMS_I_GLOVE_PACKS = (
    {"lab": "fictional robotics lab", "sensors": 12, "region": "fingertip"},
    {"lab": "fictional prosthetics workshop", "sensors": 8, "region": "fingertip"},
    {"lab": "fictional games-controller studio", "sensors": 6, "region": "thumb pad"},
)


@_u23_variant("touch", "sms", "intermediate", "glove_sensors_then_copy_mcq_then_word")
def _touch_intermediate_sms_glove_sensors_then_copy_mcq_then_word():
    pack = random.choice(_TO_SMS_I_GLOVE_PACKS)
    correct = f"the {pack['region']} has densely packed touch receptors in the skin model"
    distractors = (
        "fingertips have no receptors at all",
        f"the {pack['region']} has thicker skin than other regions",
        "receptors in the skin only detect temperature",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['lab']} builds a sensing glove with {pack['sensors']} pressure "
        f"sensors clustered on the {pack['region']}.</p>"
        "<p>(i) Enter the number of sensors on the glove.</p>"
        "<p>(ii) The engineers clustered the sensors in (i) there because</p>"
        "<p>(iii) Write the one-word receptor type the sensors imitate.</p>"
    )
    solution = (
        f"(i) <strong>{pack['sensors']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>pressure</strong>"
    )
    hint = "<strong>Key idea:</strong> Engineers copy where the skin is most sensitive."
    return (
        question, solution, hint, 3,
        _fields((pack["sensors"], letter, "pressure"), ("Sensors", "Why there", "Receptor imitated"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, reason, then one word."),
    )


_TO_SMS_I_STUDY_PACKS = (
    {"study": "fictional textbook study of 40 volunteers", "fingertip": 2, "back": 40},
    {"study": "fictional university dataset of 60 adults", "fingertip": 3, "back": 42},
    {"study": "fictional physiology handout", "fingertip": 2, "back": 38},
)


@_u23_variant("touch", "sms", "intermediate", "study_pick_then_density_order")
def _touch_intermediate_sms_study_pick_then_density_order():
    pack = random.choice(_TO_SMS_I_STUDY_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The fingertip has the smaller threshold, so it is more sensitive",
            "The data are averages from consenting volunteers, not a class test",
        ),
        (
            "The back is more sensitive because its number is bigger",
            "Pupils should measure each other to check",
        ),
        2,
    )
    order_raw, order_bank = _u23_order_field(
        (
            "Receptors are more densely packed in the fingertip",
            "Nearby points reach different receptors",
            "Two points are felt as two at a small gap",
        ),
        ("The fingertip is ranked as the toughest skin",),
    )
    question = (
        f"<p>A {pack['study']} reports average two-point thresholds of "
        f"{pack['fingertip']} mm (fingertip) and {pack['back']} mm (back).</p>"
        "<p>(i) Select the two correct readings of the data.</p>"
        "<p>(ii) Using the first reading from (i), order why the fingertip "
        "discriminates better.</p>"
    )
    solution = (
        "(i) Smaller threshold = more sensitive; consented averages.<br>"
        "(ii) <strong>dense packing → different receptors → felt as two</strong>"
    )
    hint = "<strong>Key idea:</strong> Smaller gap, denser receptors — from supplied data only."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Readings", "Why fingertip is better"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two readings, then order three steps."),
    )


_TO_SMS_I_SAFETY_PACKS = (
    {"where": "fictional school kitchen", "hazards": 3},
    {"where": "fictional pottery studio with a kiln", "hazards": 2},
    {"where": "fictional science-lab hot-plate station", "hazards": 4},
)


@_u23_variant("touch", "sms", "intermediate", "safety_hazards_then_chain_order")
def _touch_intermediate_sms_safety_hazards_then_chain_order():
    pack = random.choice(_TO_SMS_I_SAFETY_PACKS)
    order_raw, order_bank = _u23_order_field(
        (
            "Pain and temperature receptors detect the heat",
            "A signal travels to the nervous system",
            "The hand withdraws and a burn is limited",
        ),
        ("The class votes on whether it was hot",),
    )
    question = (
        f"<p>A fictional risk assessment for a {pack['where']} lists "
        f"{pack['hazards']} hot-surface hazards.</p>"
        "<p>(i) Enter the number of hot-surface hazards listed.</p>"
        "<p>(ii) For any hazard counted in (i), order the body's protective response.</p>"
    )
    solution = (
        f"(i) <strong>{pack['hazards']}</strong><br>"
        "(ii) <strong>detect → signal → withdraw</strong>"
    )
    hint = "<strong>Key idea:</strong> Count hazards, then detect–signal–withdraw."
    return (
        question, solution, hint, 2,
        _fields((pack["hazards"], order_raw), ("Hazards", "Protective response"),
                ("number", "order"), (None, order_bank),
                hint="Count, then order three steps."),
    )


_TO_SMS_D_BRAILLE_PACKS = (
    {"library": "fictional public library", "dot_mm": 2.5, "fingertip_mm": 2},
    {"library": "fictional school resource centre", "dot_mm": 2.5, "fingertip_mm": 2},
    {"library": "fictional museum touch-tour", "dot_mm": 3, "fingertip_mm": 2},
)


@_u23_variant("touch", "sms", "difficult", "braille_compare_then_order_then_word")
def _touch_difficult_sms_braille_compare_then_order_then_word():
    pack = random.choice(_TO_SMS_D_BRAILLE_PACKS)
    fits = 1 if pack["dot_mm"] > pack["fingertip_mm"] else 0
    order_raw, order_bank = _u23_order_field(
        (
            "Dots are spaced wider than the fingertip's two-point threshold",
            "Each dot stimulates a separate receptor group",
            "The pattern of dots is read as a character",
        ),
        ("Readers are ranked by whose skin is best",),
    )
    question = (
        f"<p>A {pack['library']} explains braille: dots are about {pack['dot_mm']} mm "
        f"apart, and supplied data give the fingertip two-point threshold as about "
        f"{pack['fingertip_mm']} mm.</p>"
        "<p>(i) Enter 1 if the dot spacing exceeds the threshold, otherwise 0.</p>"
        "<p>(ii) Using the comparison from (i), order why braille can be read by touch.</p>"
        "<p>(iii) Write the one-word receptor type that detects the raised dots.</p>"
    )
    solution = (
        f"(i) <strong>{fits}</strong><br>"
        "(ii) <strong>spacing exceeds threshold → separate receptors → pattern read</strong><br>"
        "(iii) <strong>pressure</strong>"
    )
    hint = "<strong>Key idea:</strong> Spacing beats threshold, so dots are felt separately."
    return (
        question, solution, hint, 3,
        _fields((fits, order_raw, "pressure"), ("Spacing exceeds threshold", "Why readable", "Receptor"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="1 or 0, three steps, then one word."),
    )


_TO_SMS_D_TRIAL_PACKS = (
    {"trial": "fictional prosthetic-hand trial", "users": 50, "success": 40},
    {"trial": "fictional robot-gripper test", "users": 80, "success": 60},
    {"trial": "fictional haptic-glove study", "users": 40, "success": 30},
)


@_u23_variant("touch", "sms", "difficult", "trial_pct_then_caution_pick_then_verdict")
def _touch_difficult_sms_trial_pct_then_caution_pick_then_verdict():
    pack = random.choice(_TO_SMS_D_TRIAL_PACKS)
    pct = _pct(pack["success"], pack["users"])
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The sample is small, so the figure is uncertain",
            "The result is an aggregate, not a ranking of users",
        ),
        (
            "The failures should be named to check them",
            "The percentage proves the device works for everyone",
        ),
        2,
    )
    correct = "the pressure-sensing feedback helped most users in this trial, with limits"
    distractors = (
        "the device proves skin receptors are unnecessary",
        "users should be ranked by skin toughness",
        "the trial should store each user's body map",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['trial']} reports that {pack['success']} of {pack['users']} "
        "users could grip an egg without breaking it using pressure feedback.</p>"
        "<p>(i) Calculate that as a whole-number percentage.</p>"
        "<p>(ii) Using the figure from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['success']} ÷ {pack['users']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) Small sample; aggregate not ranking.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, cautions, honest verdict."
    return (
        question, solution, hint, 3,
        _fields((pct, pick_raw, letter), ("Success (%)", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Percentage, two cautions, then the verdict."),
    )


@_u23_variant("touch", "sms", "difficult", "clinic_pick_then_ethics_mcq")
def _touch_difficult_sms_clinic_pick_then_ethics_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Sensation tests are done with consent by trained staff",
            "Results stay in the clinic, not in a class quiz",
        ),
        (
            "Pupils should test each other's skin for homework",
            "The clinic ranks patients by toughest skin",
        ),
        2,
    )
    correct = "use the textbook's supplied data and never touch classmates"
    distractors = (
        "run the test on each other in class",
        "store a private body map in the app",
        "rank pupils by skin sensitivity",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional documentary shows a neurology clinic checking skin "
        "sensation after an injury.</p>"
        "<p>(i) Select the two statements consistent with the documentary.</p>"
        "<p>(ii) Using the first statement from (i), a school lesson on "
        "receptor density should</p>"
    )
    solution = (
        "(i) Consent and trained staff; results stay clinical.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Consent, clinical records, supplied data in class."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Consistent statements", "School lesson should"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the rule."),
    )


TOUCH_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _touch_intermediate_ms_table_smallest_then_density_mcq,
        _touch_intermediate_ms_receptor_pick_then_count,
        _touch_intermediate_ms_reflex_order_then_pain_word,
    ],
    "difficult": [
        _touch_difficult_ms_ratio_then_density_order_then_word,
        _touch_difficult_ms_method_pick_then_consent_mcq_then_count,
        _touch_difficult_ms_temp_diff_then_receptor_mcq_then_word,
    ],
}

TOUCH_SMS_POOLS = {
    "foundational": [],
    "intermediate": [
        _touch_intermediate_sms_glove_sensors_then_copy_mcq_then_word,
        _touch_intermediate_sms_study_pick_then_density_order,
        _touch_intermediate_sms_safety_hazards_then_chain_order,
    ],
    "difficult": [
        _touch_difficult_sms_braille_compare_then_order_then_word,
        _touch_difficult_sms_trial_pct_then_caution_pick_then_verdict,
        _touch_difficult_sms_clinic_pick_then_ethics_mcq,
    ],
}


# ---------------------------------------------------------------------------
# smell — multi_step stays — (matrix: no authentic context-free chain);
# situational_multi_step (I, D) from supplied public examples only.
# ---------------------------------------------------------------------------

_SM_SMS_I_GAS_PACKS = (
    {"company": "fictional gas supplier", "odorant": "a strong-smelling additive"},
    {"company": "fictional utility company", "odorant": "an added sulfur-smelling chemical"},
    {"company": "fictional campsite gas depot", "odorant": "an added warning odorant"},
)


@_u23_variant("smell", "sms", "intermediate", "gas_chain_order_then_receptor_word")
def _smell_intermediate_sms_gas_chain_order_then_receptor_word():
    pack = random.choice(_SM_SMS_I_GAS_PACKS)
    order_raw, order_bank = _u23_order_field(
        (
            f"Molecules of {pack['odorant']} spread through the air",
            "Smell receptors in the nose detect the chemical",
            "The brain interprets it as a warning and people leave",
        ),
        ("The class ranks whose nose is best",),
    )
    question = (
        f"<p>A {pack['company']} explains in a public leaflet that natural gas has "
        f"no smell, so {pack['odorant']} is mixed in.</p>"
        "<p>(i) Order how the additive becomes a warning.</p>"
        "<p>(ii) Write the one-word name for the cells in step 2 of (i) that "
        "detect airborne chemicals.</p>"
    )
    solution = (
        "(i) <strong>molecules spread → receptors detect → brain warns</strong><br>"
        "(ii) <strong>receptors</strong>"
    )
    hint = "<strong>Key idea:</strong> Chemical signal, receptor, interpretation."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "receptors"), ("Warning chain", "Detecting cells"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


_SM_SMS_I_PANEL_PACKS = (
    {"panel": "fictional food-science tasting panel", "samples": 5, "categories": ("fruity", "smoky", "floral")},
    {"panel": "fictional perfume-training class", "samples": 6, "categories": ("citrus", "woody", "floral")},
    {"panel": "fictional coffee-roaster lab", "samples": 4, "categories": ("nutty", "fruity", "smoky")},
)


@_u23_variant("smell", "sms", "intermediate", "panel_samples_then_category_mcq")
def _smell_intermediate_sms_panel_samples_then_category_mcq():
    pack = random.choice(_SM_SMS_I_PANEL_PACKS)
    cats = pack["categories"]
    correct = "grouping smells using public example categories such as " + ", ".join(cats)
    distractors = (
        "ranking panellists by whose nose is best",
        "listing each panellist's private home odours",
        "forcing everyone to sniff an unknown chemical",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['panel']} smells {pack['samples']} labelled samples and sorts "
        f"them into categories: {', '.join(cats)}.</p>"
        "<p>(i) Enter the number of samples.</p>"
        "<p>(ii) What the panel does with the samples in (i) is</p>"
    )
    solution = (
        f"(i) <strong>{pack['samples']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Count, then categorise with public examples."
    return (
        question, solution, hint, 2,
        _fields((pack["samples"], letter), ("Samples", "What the panel does"),
                ("number", "mcq"), (None, options),
                hint="Count, then choose the categorising idea."),
    )


@_u23_variant("smell", "sms", "intermediate", "bakery_context_pick_then_count")
def _smell_intermediate_sms_bakery_context_pick_then_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Context can change what a smell is taken to mean",
            "Different receptor types respond to different chemicals",
        ),
        (
            "There is only one smell receptor in the whole species",
            "Shoppers should be ranked by nose",
        ),
        2,
    )
    question = (
        "<p>A fictional shopping-centre study finds the same baking smell is "
        "described as 'welcoming' near a bakery but 'burnt' near a fire exit.</p>"
        "<p>(i) Select the two scientific ideas the study illustrates.</p>"
        "<p>(ii) Enter how many different places the same smell was judged in.</p>"
    )
    solution = (
        "(i) Context changes meaning; receptor diversity.<br>"
        "(ii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Same chemical, different context, different meaning."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Ideas", "Places judged"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


_SM_SMS_D_DOG_PACKS = (
    {"study": "fictional detection-dog study", "trials": 100, "correct": 90, "task": "finding a hidden sample"},
    {"study": "fictional search-and-rescue training log", "trials": 50, "correct": 45, "task": "locating a scent trail"},
    {"study": "fictional airport-dog evaluation", "trials": 80, "correct": 72, "task": "flagging a target scent"},
)


@_u23_variant("smell", "sms", "difficult", "dog_pct_then_caution_pick_then_verdict")
def _smell_difficult_sms_dog_pct_then_caution_pick_then_verdict():
    pack = random.choice(_SM_SMS_D_DOG_PACKS)
    pct = _pct(pack["correct"], pack["trials"])
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Trials must be blinded so handlers cannot cue the dog",
            "One dog's result is an aggregate of trials, not proof for all dogs",
        ),
        (
            "The dog's nose should be ranked against pupils' noses",
            "Success proves the dog reads minds",
        ),
        2,
    )
    correct = "the dog detected the target chemical signal reliably in these trials, within limits"
    distractors = (
        "dogs have only one smell receptor",
        "the dog's brain needs no interpretation",
        "pupils should sniff the samples to compare",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} reports {pack['correct']} correct out of "
        f"{pack['trials']} trials when {pack['task']}.</p>"
        "<p>(i) Calculate the success rate as a whole-number percentage.</p>"
        "<p>(ii) Using the rate from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['correct']} ÷ {pack['trials']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) Blinded trials; aggregate of one dog.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, blinding, honest verdict."
    return (
        question, solution, hint, 3,
        _fields((pct, pick_raw, letter), ("Success (%)", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Percentage, two cautions, then the verdict."),
    )


_SM_SMS_D_WINE_PACKS = (
    {"panel": "fictional tea-tasting panel", "with": 20, "without": 6, "total": 24},
    {"panel": "fictional chocolate-flavour panel", "with": 18, "without": 5, "total": 20},
    {"panel": "fictional juice-blend panel", "with": 27, "without": 9, "total": 30},
)


@_u23_variant("smell", "sms", "difficult", "noseclip_drop_then_order_then_word")
def _smell_difficult_sms_noseclip_drop_then_order_then_word():
    pack = random.choice(_SM_SMS_D_WINE_PACKS)
    drop = pack["with"] - pack["without"]
    order_raw, order_bank = _u23_order_field(
        (
            "Airborne molecules from the sample reach the nose",
            "Smell receptors send signals to the brain",
            "The brain combines smell with taste to identify the flavour",
        ),
        ("The panellists are ranked by whose nose is best",),
    )
    question = (
        f"<p>A {pack['panel']} of {pack['total']} volunteers identifies a sample "
        f"correctly {pack['with']} times normally but only {pack['without']} times "
        "with a supplied nose clip (aggregate results).</p>"
        "<p>(i) Calculate how many fewer correct identifications there were with the clip.</p>"
        "<p>(ii) Using the drop from (i), order what the clip blocked.</p>"
        "<p>(iii) Write the one-word sense that smell combines with here.</p>"
    )
    solution = (
        f"(i) {pack['with']} − {pack['without']} = <strong>{drop}</strong><br>"
        "(ii) <strong>molecules reach nose → receptors signal → brain combines</strong><br>"
        "(iii) <strong>taste</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then the blocked chain; flavour = smell + taste."
    return (
        question, solution, hint, 3,
        _fields((drop, order_raw, "taste"), ("Fewer correct", "What the clip blocked", "Combined sense"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Subtract, three steps, then one word."),
    )


@_u23_variant("smell", "sms", "difficult", "warning_pick_then_interpret_mcq")
def _smell_difficult_sms_warning_pick_then_interpret_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The same chemical signal can be interpreted differently in different contexts",
            "Public safety uses smell as a warning because receptors detect small amounts",
        ),
        (
            "Everyone must sniff an unknown chemical to learn this",
            "The quiz should collect a private odour diary",
        ),
        2,
    )
    correct = "context: the brain interprets the signal using where the person is and what they expect"
    distractors = (
        "the receptors change type between rooms",
        "one location has a better nose",
        "the chemical changes its molecules",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional fire-safety film notes that smoke from a barbecue is read "
        "as 'dinner' outdoors but 'danger' indoors at night.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the first statement from (i), what changes the meaning is</p>"
    )
    solution = (
        "(i) Context-dependent interpretation; warning use.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Same signal, context decides the meaning."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "What changes the meaning"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the reason."),
    )


SMELL_MS_POOLS = {
    "foundational": [],
    "intermediate": [],
    "difficult": [],
}

SMELL_SMS_POOLS = {
    "foundational": [],
    "intermediate": [
        _smell_intermediate_sms_gas_chain_order_then_receptor_word,
        _smell_intermediate_sms_panel_samples_then_category_mcq,
        _smell_intermediate_sms_bakery_context_pick_then_count,
    ],
    "difficult": [
        _smell_difficult_sms_dog_pct_then_caution_pick_then_verdict,
        _smell_difficult_sms_noseclip_drop_then_order_then_word,
        _smell_difficult_sms_warning_pick_then_interpret_mcq,
    ],
}


# ---------------------------------------------------------------------------
# taste — multi_step (I, D); situational (I, D). Foundational SMS stays —
# (no forced tasting, no private menu).
# ---------------------------------------------------------------------------

_TA_MS_I_LIST_PACKS = (
    {"listed": ("sweet", "salt", "sour", "bitter", "umami"), "extra": "spicy"},
    {"listed": ("sweet", "sour", "salt", "umami", "bitter"), "extra": "minty"},
    {"listed": ("bitter", "umami", "sweet", "salt", "sour"), "extra": "crunchy"},
)


@_u23_variant("taste", "ms", "intermediate", "list_count_then_extra_mcq")
def _taste_intermediate_ms_list_count_then_extra_mcq():
    pack = random.choice(_TA_MS_I_LIST_PACKS)
    correct = f"'{pack['extra']}' is a sensation or texture, not one of the five tastes"
    distractors = (
        f"'{pack['extra']}' is the sixth taste",
        f"'{pack['extra']}' is a mix of sweet and salt",
        f"'{pack['extra']}' is detected by the nose, not the tongue",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional food-science poster lists: "
        + ", ".join(pack["listed"])
        + f" — and someone has pencilled in '{pack['extra']}'.</p>"
        "<p>(i) Enter how many basic tastes there are.</p>"
        f"<p>(ii) Given the count in (i), the pencilled '{pack['extra']}'</p>"
    )
    solution = (
        "(i) <strong>5</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Five named tastes; texture and heat are different senses."
    return (
        question, solution, hint, 2,
        _fields((5, letter), ("Tastes named", "The pencilled word"),
                ("number", "mcq"), (None, options),
                hint="Enter 5, then judge the extra word."),
    )


@_u23_variant("taste", "ms", "intermediate", "flavour_order_then_smell_word")
def _taste_intermediate_ms_flavour_order_then_smell_word():
    order_raw, order_bank = _u23_order_field(
        (
            "Taste receptors on the tongue detect the basic tastes",
            "Smell receptors detect airborne molecules from the food",
            "The brain combines both into flavour",
        ),
        ("The class ranks whose tongue is best",),
    )
    question = (
        "<p>A fictional cookery-school diagram explains flavour.</p>"
        "<p>(i) Order the three stages.</p>"
        "<p>(ii) Write the one-word sense in stage 2 of (i) that taste is "
        "combined with.</p>"
    )
    solution = (
        "(i) <strong>taste receptors → smell receptors → brain combines</strong><br>"
        "(ii) <strong>smell</strong>"
    )
    hint = "<strong>Key idea:</strong> Flavour is taste plus smell, combined by the brain."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "smell"), ("Flavour stages", "Combined sense"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three stages, then one word."),
    )


@_u23_variant("taste", "ms", "intermediate", "context_pick_then_count")
def _taste_intermediate_ms_context_pick_then_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Colour and context can change how a food is judged",
            "Smell and taste work together in flavour",
        ),
        (
            "Everyone must eat an unknown food for the quiz",
            "Pupils must upload a private menu",
        ),
        2,
    )
    question = (
        "<p>A fictional restaurant-science article reports a supplied controlled "
        "test: the same drink was judged 'fruitier' when coloured red.</p>"
        "<p>(i) Select the two scientific ideas the test supports.</p>"
        "<p>(ii) Enter how many senses combine to make flavour.</p>"
    )
    solution = (
        "(i) Colour/context effect; smell + taste.<br>"
        "(ii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Context shapes judgement; two senses make flavour."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Ideas", "Senses in flavour"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


_TA_MS_D_CLIP_PACKS = (
    {"panel": 40, "correct_open": 36, "correct_clip": 12},
    {"panel": 30, "correct_open": 27, "correct_clip": 9},
    {"panel": 50, "correct_open": 45, "correct_clip": 15},
)


@_u23_variant("taste", "ms", "difficult", "clip_drop_then_reason_mcq_then_word")
def _taste_difficult_ms_clip_drop_then_reason_mcq_then_word():
    pack = random.choice(_TA_MS_D_CLIP_PACKS)
    drop = pack["correct_open"] - pack["correct_clip"]
    correct = "smell contributes most of what people call flavour, so blocking it removes the cues"
    distractors = (
        "the nose clip damaged the taste receptors",
        "the clip blocked the taste receptors on the tongue",
        "the five tastes are detected in the nose",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook reports a supplied controlled test: {pack['panel']} "
        f"volunteers identified a juice correctly {pack['correct_open']} times "
        f"normally and {pack['correct_clip']} times with a nose clip.</p>"
        "<p>(i) Calculate the drop in correct identifications.</p>"
        "<p>(ii) The drop in (i) happens because</p>"
        "<p>(iii) Write the one-word term for the combined taste-and-smell experience.</p>"
    )
    solution = (
        f"(i) {pack['correct_open']} − {pack['correct_clip']} = <strong>{drop}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>flavour</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then smell's share of flavour."
    return (
        question, solution, hint, 3,
        _fields((drop, letter, "flavour"), ("Drop", "Because", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, reason, then one word."),
    )


@_u23_variant("taste", "ms", "difficult", "colour_order_then_control_pick")
def _taste_difficult_ms_colour_order_then_control_pick():
    order_raw, order_bank = _u23_order_field(
        (
            "Give panellists the same drink in two colours",
            "Record how each colour is judged, without names",
            "Compare the judgements to see the colour effect",
        ),
        ("Rank panellists by whose tongue is best",),
    )
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Keep the drink identical apart from colour",
            "Do not tell panellists which is which",
        ),
        (
            "Force everyone to taste an unknown food",
            "Publish each panellist's private menu",
        ),
        2,
    )
    question = (
        "<p>A fictional consumer lab plans a colour-and-taste experiment.</p>"
        "<p>(i) Order the fair-test method.</p>"
        "<p>(ii) Using step 1 of (i), select the two controls that make it fair.</p>"
    )
    solution = (
        "(i) <strong>same drink, two colours → record anonymously → compare</strong><br>"
        "(ii) Identical apart from colour; blind."
    )
    hint = "<strong>Key idea:</strong> Change one variable, keep it blind, compare."
    return (
        question, solution, hint, 2,
        _fields((order_raw, pick_raw), ("Method", "Controls"),
                ("order", "pick"), (order_bank, pick_bank), (None, pick_count),
                hint="Order three steps, then two controls."),
    )


_TA_MS_D_MAP_PACKS = (
    {"claim": "each taste has its own exclusive zone on the tongue"},
    {"claim": "the tip of the tongue detects only sweet"},
    {"claim": "bitter is sensed only at the very back"},
)


@_u23_variant("taste", "ms", "difficult", "myth_mcq_then_count_then_word")
def _taste_difficult_ms_myth_mcq_then_count_then_word():
    pack = random.choice(_TA_MS_D_MAP_PACKS)
    correct = "an oversimplified 'tongue map'; all regions with receptors detect the tastes"
    distractors = (
        "correct: each taste has its own zone of the tongue",
        "true because it appears in many textbooks",
        "correct for sweet and salt but not for bitter",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional old textbook claims that {pack['claim']}.</p>"
        "<p>(i) This claim is</p>"
        "<p>(ii) Enter how many basic tastes the model names.</p>"
        "<p>(iii) Write the one-word sense that must join taste to give full flavour.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>5</strong><br>"
        "(iii) <strong>smell</strong>"
    )
    hint = "<strong>Key idea:</strong> The zone map is a myth; five tastes; smell completes flavour."
    return (
        question, solution, hint, 3,
        _fields((letter, 5, "smell"), ("The claim is", "Basic tastes", "Joining sense"),
                ("mcq", "number", "keyword"), (options, None, None),
                hint="Choose, enter 5, then one word."),
    )


# taste — situational_multi_step (I, D only)

_TA_SMS_I_CANTEEN_PACKS = (
    {"who": "Alex", "place": "a fictional canteen", "dish": "a soup", "taste": "salt"},
    {"who": "Sam", "place": "a fictional café", "dish": "a lemonade", "taste": "sour"},
    {"who": "Jordan", "place": "a fictional bakery", "dish": "a pastry", "taste": "sweet"},
)


@_u23_variant("taste", "sms", "intermediate", "cold_case_then_flavour_mcq_then_word")
def _taste_intermediate_sms_cold_case_then_flavour_mcq_then_word():
    pack = random.choice(_TA_SMS_I_CANTEEN_PACKS)
    correct = "a blocked nose removes the smell part, so flavour seems weaker"
    distractors = (
        "the taste receptors were removed by the cold",
        f"{pack['who']}'s tongue stopped detecting the five tastes",
        "the food lost its taste chemicals",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional story, {pack['who']} has a blocked nose from a cold and "
        f"finds {pack['dish']} in {pack['place']} tastes 'flat', though the "
        f"{pack['taste']} is still noticeable.</p>"
        f"<p>(i) Enter how many of the five basic tastes the story names as still noticed.</p>"
        "<p>(ii) The flatness alongside the taste in (i) happens because</p>"
        "<p>(iii) Write the one-word sense that is blocked.</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>smell</strong>"
    )
    hint = "<strong>Key idea:</strong> Taste works; smell is missing; flavour drops."
    return (
        question, solution, hint, 3,
        _fields((1, letter, "smell"), ("Tastes still noticed", "Because", "Blocked sense"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, reason, then one word."),
    )


_TA_SMS_I_PANEL_PACKS = (
    {"panel": "fictional school cookery club panel", "n": 20, "red": 14, "clear": 6},
    {"panel": "fictional drinks-company test panel", "n": 30, "red": 21, "clear": 9},
    {"panel": "fictional food-fair panel", "n": 40, "red": 28, "clear": 12},
)


@_u23_variant("taste", "sms", "intermediate", "panel_colour_pick_then_order")
def _taste_intermediate_sms_panel_colour_pick_then_order():
    pack = random.choice(_TA_SMS_I_PANEL_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Colour and context changed the judgement of an identical drink",
            "The results are anonymous aggregates, not a ranking of panellists",
        ),
        (
            "The red drink had extra sugar",
            "Panellists should upload their private menus",
        ),
        2,
    )
    order_raw, order_bank = _u23_order_field(
        (
            "The eyes see the colour before tasting",
            "The brain forms an expectation",
            "The expectation shapes how the taste is judged",
        ),
        ("The tongue grows extra receptors for red drinks",),
    )
    question = (
        f"<p>A {pack['panel']} of {pack['n']} people tastes an identical drink twice: "
        f"{pack['red']} call the red version 'sweeter' and {pack['clear']} call the "
        "clear version 'sweeter'.</p>"
        "<p>(i) Select the two correct readings.</p>"
        "<p>(ii) Using the first reading from (i), order how colour changes the judgement.</p>"
    )
    solution = (
        "(i) Colour/context effect; anonymous aggregate.<br>"
        "(ii) <strong>see colour → expectation → shapes judgement</strong>"
    )
    hint = "<strong>Key idea:</strong> Expectation from colour alters the judged taste."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Readings", "How colour acts"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two readings, then order three steps."),
    )


_TA_SMS_I_MENU_PACKS = (
    {"chef": "a fictional chef", "tastes": ("sweet", "sour", "salt"), "n": 3},
    {"chef": "a fictional food-truck cook", "tastes": ("salt", "umami", "bitter"), "n": 3},
    {"chef": "a fictional pastry chef", "tastes": ("sweet", "bitter"), "n": 2},
)


@_u23_variant("taste", "sms", "intermediate", "chef_tastes_then_balance_mcq")
def _taste_intermediate_sms_chef_tastes_then_balance_mcq():
    pack = random.choice(_TA_SMS_I_MENU_PACKS)
    correct = "the dish is balanced across several of the five basic tastes"
    distractors = (
        "the dish has all eight tastes",
        "the dish uses only sweet and salt",
        "the tastes are detected by the nose alone",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>{pack['chef'].capitalize()} designs a dish combining "
        + ", ".join(pack["tastes"])
        + ".</p>"
        "<p>(i) Enter how many of the five basic tastes the dish combines.</p>"
        "<p>(ii) The count in (i) shows that</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Count the named tastes out of five."
    return (
        question, solution, hint, 2,
        _fields((pack["n"], letter), ("Tastes combined", "This shows"),
                ("number", "mcq"), (None, options),
                hint="Count, then choose the balance idea."),
    )


_TA_SMS_D_AIRLINE_PACKS = (
    {"study": "fictional airline catering study", "ground": 40, "air": 25, "n": 50},
    {"study": "fictional altitude-lab report", "ground": 36, "air": 20, "n": 45},
    {"study": "fictional cabin-crew training dataset", "ground": 48, "air": 30, "n": 60},
)


@_u23_variant("taste", "sms", "difficult", "altitude_drop_then_factor_pick_then_verdict")
def _taste_difficult_sms_altitude_drop_then_factor_pick_then_verdict():
    pack = random.choice(_TA_SMS_D_AIRLINE_PACKS)
    drop = pack["ground"] - pack["air"]
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Dry cabin air reduces the smell contribution to flavour",
            "Context and expectation in a cabin can change judgements",
        ),
        (
            "Passengers' tongues lose their receptors in flight",
            "Passengers should be ranked by taste",
        ),
        2,
    )
    correct = "flavour perception is weaker in the cabin, likely through smell and context, within the study's limits"
    distractors = (
        "the five tastes do not exist at altitude",
        "the study should store each passenger's menu",
        "the tongue map explains it",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} reports that {pack['ground']} of {pack['n']} panellists "
        f"identified a sauce on the ground but only {pack['air']} did so in a "
        "simulated cabin.</p>"
        "<p>(i) Calculate the drop in correct identifications.</p>"
        "<p>(ii) Using the drop from (i), select the two likely factors.</p>"
        "<p>(iii) Given (ii), the fair conclusion is that</p>"
    )
    solution = (
        f"(i) {pack['ground']} − {pack['air']} = <strong>{drop}</strong><br>"
        "(ii) Dry air reduces smell; context.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then smell and context explain most of the drop."
    return (
        question, solution, hint, 3,
        _fields((drop, pick_raw, letter), ("Drop", "Likely factors", "Conclusion"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Subtract, two factors, then the conclusion."),
    )


_TA_SMS_D_LAB_PACKS = (
    {"lab": "fictional flavour-chemistry lab", "compounds": 4, "detected": 3},
    {"lab": "fictional university sensory lab", "compounds": 6, "detected": 5},
    {"lab": "fictional food-safety lab", "compounds": 5, "detected": 4},
)


@_u23_variant("taste", "sms", "difficult", "lab_compounds_then_order_then_word")
def _taste_difficult_sms_lab_compounds_then_order_then_word():
    pack = random.choice(_TA_SMS_D_LAB_PACKS)
    missed = pack["compounds"] - pack["detected"]
    order_raw, order_bank = _u23_order_field(
        (
            "A compound dissolves in saliva on the tongue",
            "Taste receptors respond and signal the brain",
            "The brain combines the signal with smell into flavour",
        ),
        ("The lab ranks volunteers by tongue",),
    )
    question = (
        f"<p>A {pack['lab']} tests {pack['compounds']} supplied flavour compounds "
        f"on a consenting panel; {pack['detected']} are detected by taste alone.</p>"
        "<p>(i) Calculate how many compounds were <em>not</em> detected by taste alone.</p>"
        "<p>(ii) For the compounds that were detected in (i)'s comparison, order the pathway.</p>"
        "<p>(iii) Write the one-word sense that would be needed to detect the rest.</p>"
    )
    solution = (
        f"(i) {pack['compounds']} − {pack['detected']} = <strong>{missed}</strong><br>"
        "(ii) <strong>dissolve → receptors signal → brain combines</strong><br>"
        "(iii) <strong>smell</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, follow the taste pathway, smell fills the gap."
    return (
        question, solution, hint, 3,
        _fields((missed, order_raw, "smell"), ("Not detected by taste", "Taste pathway", "Needed sense"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Subtract, three steps, then one word."),
    )


@_u23_variant("taste", "sms", "difficult", "ethics_pick_then_method_mcq")
def _taste_difficult_sms_ethics_pick_then_method_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Panellists consent and can decline any sample",
            "Results are reported as anonymous aggregates",
        ),
        (
            "Everyone must eat an unknown food",
            "Each panellist's private menu is published",
        ),
        2,
    )
    correct = "use supplied results from consenting panels, never forced tasting in class"
    distractors = (
        "make pupils taste unknown foods",
        "rank pupils by tongue",
        "collect private menus",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional food-industry documentary shows how tasting panels are run.</p>"
        "<p>(i) Select the two rules the panels follow.</p>"
        "<p>(ii) Using the first rule from (i), a school lesson on taste should</p>"
    )
    solution = (
        "(i) Consent; anonymous aggregates.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Consent and aggregates; supplied data in class."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Panel rules", "School lesson should"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two rules, then the method."),
    )


TASTE_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _taste_intermediate_ms_list_count_then_extra_mcq,
        _taste_intermediate_ms_flavour_order_then_smell_word,
        _taste_intermediate_ms_context_pick_then_count,
    ],
    "difficult": [
        _taste_difficult_ms_clip_drop_then_reason_mcq_then_word,
        _taste_difficult_ms_colour_order_then_control_pick,
        _taste_difficult_ms_myth_mcq_then_count_then_word,
    ],
}

TASTE_SMS_POOLS = {
    "foundational": [],
    "intermediate": [
        _taste_intermediate_sms_cold_case_then_flavour_mcq_then_word,
        _taste_intermediate_sms_panel_colour_pick_then_order,
        _taste_intermediate_sms_chef_tastes_then_balance_mcq,
    ],
    "difficult": [
        _taste_difficult_sms_altitude_drop_then_factor_pick_then_verdict,
        _taste_difficult_sms_lab_compounds_then_order_then_word,
        _taste_difficult_sms_ethics_pick_then_method_mcq,
    ],
}


# ---------------------------------------------------------------------------
# proprioception_balance — multi_step (I, D); situational (I, D).
# Foundational SMS stays — (no spinning task, symptom prompt or dizziness record).
# ---------------------------------------------------------------------------

_PR_MS_I_SYS_PACKS = (
    {"systems": ("semicircular canals", "vision", "proprioception"), "n": 3},
    {"systems": ("vision", "proprioception", "semicircular canals"), "n": 3},
    {"systems": ("proprioception", "semicircular canals", "vision"), "n": 3},
)


@_u23_variant("proprioception_balance", "ms", "intermediate", "systems_count_then_canal_mcq")
def _proprioception_balance_intermediate_ms_systems_count_then_canal_mcq():
    pack = random.choice(_PR_MS_I_SYS_PACKS)
    correct = "rotation of the head"
    distractors = ("the position of the limbs", "sound vibrations in the air", "the speed of walking")
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional physiology poster lists the systems that work together for "
        "balance: " + ", ".join(pack["systems"]) + ".</p>"
        "<p>(i) Enter how many systems the poster lists.</p>"
        "<p>(ii) Of the systems counted in (i), the semicircular canals detect</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Three systems; canals sense rotation."
    return (
        question, solution, hint, 2,
        _fields((pack["n"], letter), ("Systems listed", "Canals detect"),
                ("number", "mcq"), (None, options),
                hint="Count, then choose rotation."),
    )


@_u23_variant("proprioception_balance", "ms", "intermediate", "canal_order_then_word")
def _proprioception_balance_intermediate_ms_canal_order_then_word():
    diagram = str(canal_boxes(title="Fictional canal schematic"))
    order_raw, order_bank = _u23_order_field(
        (
            "The head rotates",
            "Fluid in a semicircular canal lags and moves sensors",
            "A signal about rotation reaches the brain",
        ),
        ("The class ranks who is least dizzy",),
    )
    question = (
        diagram
        + "<p>A fictional inner-ear schematic shows three semicircular canal loops.</p>"
        "<p>(i) Order how a canal reports a turn.</p>"
        "<p>(ii) Enter the number of canal loops shown in the schematic.</p>"
    )
    solution = (
        "(i) <strong>head rotates → fluid lags → signal to brain</strong><br>"
        "(ii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Rotation, fluid lag, signal; three loops."
    return (
        question, solution, hint, 2,
        _fields((order_raw, 3), ("How a canal reports a turn", "Loops shown"),
                ("order", "number"), (order_bank, None),
                hint="Order three steps, then enter 3."),
    )


@_u23_variant("proprioception_balance", "ms", "intermediate", "position_pick_then_word")
def _proprioception_balance_intermediate_ms_position_pick_then_word():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Proprioception senses body position without looking",
            "Vision can help balance",
        ),
        (
            "Pupils must be spun until unwell for the quiz",
            "The app should store who felt dizzy",
        ),
        2,
    )
    question = (
        "<p>A fictional sports-science card describes how an athlete stands on one leg.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Write the one-word sense from (i) that reports limb position "
        "without looking.</p>"
    )
    solution = (
        "(i) Position sense; vision helps.<br>"
        "(ii) <strong>proprioception</strong>"
    )
    hint = "<strong>Key idea:</strong> Position sense plus vision keep balance."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, "proprioception"), ("Statements", "Position sense"),
                ("pick", "keyword"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then one word."),
    )


_PR_MS_D_MODEL_PACKS = (
    {"turns": 3, "seconds": 6},
    {"turns": 2, "seconds": 8},
    {"turns": 5, "seconds": 10},
)


@_u23_variant("proprioception_balance", "ms", "difficult", "model_rate_then_lag_mcq_then_word")
def _proprioception_balance_difficult_ms_model_rate_then_lag_mcq_then_word():
    pack = random.choice(_PR_MS_D_MODEL_PACKS)
    secs_per_turn = pack["seconds"] // pack["turns"]
    correct = "the fluid keeps moving briefly after the model stops, so the canals report turning that is not happening"
    distractors = (
        "the canals switch off after any rotation",
        "vision stops working after a turn",
        "the fluid stops instantly, so the canals report nothing",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional lab uses a fluid-filled ring on a turntable as a canal model: "
        f"{pack['turns']} turns take {pack['seconds']} s.</p>"
        "<p>(i) Calculate the time for one turn.</p>"
        "<p>(ii) When the turntable in (i) stops suddenly, the model shows why a "
        "sense of spinning can continue:</p>"
        "<p>(iii) Write the one-word other sense that helps the brain correct this.</p>"
    )
    solution = (
        f"(i) {pack['seconds']} ÷ {pack['turns']} = <strong>{secs_per_turn}</strong> s<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>vision</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, fluid lag explains after-spin, vision corrects."
    return (
        question, solution, hint, 3,
        _fields((secs_per_turn, letter, "vision"), ("Time per turn (s)", "Why spinning continues", "Correcting sense"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Divide, choose, then one word."),
    )


@_u23_variant("proprioception_balance", "ms", "difficult", "dark_order_then_pick")
def _proprioception_balance_difficult_ms_dark_order_then_pick():
    order_raw, order_bank = _u23_order_field(
        (
            "Vision is removed as one balance input",
            "The brain relies more on canals and proprioception",
            "Small sways are corrected more slowly",
        ),
        ("The class records who wobbled most",),
    )
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Canals, vision and proprioception work together",
            "Removing one input makes the others work harder",
        ),
        (
            "Balance uses only the eyes",
            "Pupils should be spun to test this",
        ),
        2,
    )
    question = (
        "<p>A fictional textbook describes a supplied study in which volunteers "
        "stood still with lights on and then in darkness.</p>"
        "<p>(i) Order what the model predicts in darkness.</p>"
        "<p>(ii) Using the prediction from (i), select the two conclusions.</p>"
    )
    solution = (
        "(i) <strong>vision removed → rely on canals/proprioception → slower correction</strong><br>"
        "(ii) Systems work together; others compensate."
    )
    hint = "<strong>Key idea:</strong> Three inputs cooperate; lose one, the others carry more."
    return (
        question, solution, hint, 2,
        _fields((order_raw, pick_raw), ("Prediction in darkness", "Conclusions"),
                ("order", "pick"), (order_bank, pick_bank), (None, pick_count),
                hint="Order three steps, then two conclusions."),
    )


_PR_MS_D_COUNT_PACKS = (
    {"planes": ("side-to-side", "forwards-backwards", "up-and-down turn"), "n": 3},
    {"planes": ("nodding", "shaking the head", "tilting"), "n": 3},
    {"planes": ("pitch", "yaw", "roll"), "n": 3},
)


@_u23_variant("proprioception_balance", "ms", "difficult", "planes_count_then_mcq_then_word")
def _proprioception_balance_difficult_ms_planes_count_then_mcq_then_word():
    pack = random.choice(_PR_MS_D_COUNT_PACKS)
    correct = "three canals at different angles, one for each kind of rotation"
    distractors = (
        "one canal that detects every direction",
        "three canals all lying in the same plane",
        "two canals, one for each ear",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional anatomy card lists head movements: " + ", ".join(pack["planes"]) + ".</p>"
        "<p>(i) Enter how many kinds of rotation are listed.</p>"
        "<p>(ii) The number in (i) matches the inner ear's</p>"
        "<p>(iii) Write the one-word term for keeping the body oriented against a fall.</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>balance</strong>"
    )
    hint = "<strong>Key idea:</strong> Three rotations, three canals, balance."
    return (
        question, solution, hint, 3,
        _fields((pack["n"], letter, "balance"), ("Rotations listed", "Matches", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, choose, then one word."),
    )


# proprioception_balance — situational_multi_step (I, D only)

_PR_SMS_I_GYM_PACKS = (
    {"who": "Riley", "sport": "a fictional gymnastics routine", "inputs": 3},
    {"who": "Casey", "sport": "a fictional tightrope act", "inputs": 3},
    {"who": "Morgan", "sport": "a fictional skateboard trick", "inputs": 3},
)


@_u23_variant("proprioception_balance", "sms", "intermediate", "athlete_inputs_then_mcq_then_word")
def _proprioception_balance_intermediate_sms_athlete_inputs_then_mcq_then_word():
    pack = random.choice(_PR_SMS_I_GYM_PACKS)
    correct = "canals, vision and proprioception working together"
    distractors = (
        "only the eyes",
        "only the semicircular canals",
        "touch receptors alone",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional case, {pack['who']} performs {pack['sport']}; a coach's "
        f"diagram shows {pack['inputs']} balance inputs.</p>"
        "<p>(i) Enter the number of inputs on the diagram.</p>"
        "<p>(ii) The inputs counted in (i) are</p>"
        "<p>(iii) Write the one-word input that senses limb position without looking.</p>"
    )
    solution = (
        f"(i) <strong>{pack['inputs']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>proprioception</strong>"
    )
    hint = "<strong>Key idea:</strong> Three inputs cooperate; position sense is one."
    return (
        question, solution, hint, 3,
        _fields((pack["inputs"], letter, "proprioception"), ("Inputs", "They are", "Position input"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, choose, then one word."),
    )


_PR_SMS_I_ASTRO_PACKS = (
    {"crew": "fictional astronaut trainees", "place": "a fictional rotating training room"},
    {"crew": "fictional pilots", "place": "a fictional flight simulator"},
    {"crew": "fictional sailors", "place": "a fictional ship simulator"},
)


@_u23_variant("proprioception_balance", "sms", "intermediate", "trainee_pick_then_order")
def _proprioception_balance_intermediate_sms_trainee_pick_then_order():
    pack = random.choice(_PR_SMS_I_ASTRO_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The canals report rotation while vision shows a still cabin",
            "Conflicting inputs can confuse the brain's balance model",
        ),
        (
            "Trainees should be ranked by who is least dizzy",
            "Vision is the only balance input",
        ),
        2,
    )
    order_raw, order_bank = _u23_order_field(
        (
            "Rotation stimulates the semicircular canals",
            "Vision reports a different picture",
            "The brain must reconcile the two signals",
        ),
        ("The app stores who felt unwell",),
    )
    question = (
        f"<p>A fictional training manual for {pack['crew']} explains why "
        f"{pack['place']} can feel confusing.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the conflict from (i), order what happens.</p>"
    )
    solution = (
        "(i) Canals vs vision; conflict confuses.<br>"
        "(ii) <strong>canals stimulated → vision differs → brain reconciles</strong>"
    )
    hint = "<strong>Key idea:</strong> Two inputs disagree; the brain has to reconcile them."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "What happens"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_PR_SMS_I_ROBOT_PACKS = (
    {"lab": "fictional robotics lab", "sensors": ("a gyroscope", "a camera", "joint-angle sensors")},
    {"lab": "fictional drone workshop", "sensors": ("a gyroscope", "a camera", "leg-position encoders")},
    {"lab": "fictional exoskeleton studio", "sensors": ("a tilt sensor", "a camera", "joint-angle sensors")},
)


@_u23_variant("proprioception_balance", "sms", "intermediate", "robot_sensors_then_match_mcq")
def _proprioception_balance_intermediate_sms_robot_sensors_then_match_mcq():
    pack = random.choice(_PR_SMS_I_ROBOT_PACKS)
    s = pack["sensors"]
    correct = f"{s[0]} ↔ semicircular canals; {s[1]} ↔ vision; {s[2]} ↔ proprioception"
    distractors = (
        f"{s[0]} ↔ taste; {s[1]} ↔ smell; {s[2]} ↔ hearing",
        f"{s[0]} ↔ vision; {s[1]} ↔ proprioception; {s[2]} ↔ semicircular canals",
        "the sensors replace the need for a brain",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['lab']} builds a walking robot with {s[0]}, {s[1]} and {s[2]}.</p>"
        "<p>(i) Enter how many balance sensors the robot has.</p>"
        "<p>(ii) The sensors counted in (i) match the human systems as</p>"
    )
    solution = (
        "(i) <strong>3</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Rotation, sight, position — same three jobs."
    return (
        question, solution, hint, 2,
        _fields((3, letter), ("Balance sensors", "Matching"),
                ("number", "mcq"), (None, options),
                hint="Enter 3, then match the sensors."),
    )


_PR_SMS_D_STUDY_PACKS = (
    {"study": "fictional physiotherapy teaching dataset", "n": 60, "eyes_open": 54, "eyes_closed": 36},
    {"study": "fictional sports-lab report", "n": 40, "eyes_open": 36, "eyes_closed": 24},
    {"study": "fictional balance-research summary", "n": 80, "eyes_open": 72, "eyes_closed": 48},
)


@_u23_variant("proprioception_balance", "sms", "difficult", "study_drop_then_caution_pick_then_verdict")
def _proprioception_balance_difficult_sms_study_drop_then_caution_pick_then_verdict():
    pack = random.choice(_PR_SMS_D_STUDY_PACKS)
    drop = pack["eyes_open"] - pack["eyes_closed"]
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The data are supplied aggregates from consenting volunteers",
            "Other factors such as fatigue could also matter",
        ),
        (
            "Pupils should repeat it on each other and record who wobbled",
            "The drop proves vision is the only balance input",
        ),
        2,
    )
    correct = "vision contributes to balance, alongside canals and proprioception, within the study's limits"
    distractors = (
        "balance needs no vision at all",
        "vision is the only thing that keeps balance",
        "the canals stop working in darkness",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} reports that {pack['eyes_open']} of {pack['n']} volunteers "
        f"held a one-leg stance for 30 s with eyes open but {pack['eyes_closed']} did so "
        "with eyes closed.</p>"
        "<p>(i) Calculate the drop in the number who held the stance.</p>"
        "<p>(ii) Using the drop from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair conclusion is that</p>"
    )
    solution = (
        f"(i) {pack['eyes_open']} − {pack['eyes_closed']} = <strong>{drop}</strong><br>"
        "(ii) Supplied aggregates; other factors.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, cautions, then vision as one input of three."
    return (
        question, solution, hint, 3,
        _fields((drop, pick_raw, letter), ("Drop", "Cautions", "Conclusion"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Subtract, two cautions, then the conclusion."),
    )


_PR_SMS_D_SHIP_PACKS = (
    {"where": "a fictional ferry", "who": "a fictional passenger character"},
    {"where": "a fictional virtual-reality demo", "who": "a fictional tester character"},
    {"where": "a fictional funfair ride", "who": "a fictional rider character"},
)


@_u23_variant("proprioception_balance", "sms", "difficult", "conflict_order_then_word_then_count")
def _proprioception_balance_difficult_sms_conflict_order_then_word_then_count():
    pack = random.choice(_PR_SMS_D_SHIP_PACKS)
    order_raw, order_bank = _u23_order_field(
        (
            "Canals report movement of the head",
            "Vision reports a still or different scene",
            "The mismatch is interpreted as motion sickness",
        ),
        ("The character is ranked against others",),
    )
    question = (
        f"<p>A fictional explainer describes why {pack['who']} on {pack['where']} "
        "feels queasy while a fixed cabin looks still.</p>"
        "<p>(i) Order the mismatch model.</p>"
        "<p>(ii) Write the one-word inner-ear structures in step 1 of (i).</p>"
        "<p>(iii) Enter how many balance inputs disagree.</p>"
    )
    solution = (
        "(i) <strong>canals report motion → vision differs → mismatch felt</strong><br>"
        "(ii) <strong>canals</strong><br>"
        "(iii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Canals versus vision — two inputs in conflict."
    return (
        question, solution, hint, 3,
        _fields((order_raw, "canals", 2), ("Mismatch model", "Structures", "Inputs disagreeing"),
                ("order", "keyword", "number"), (order_bank, None, None),
                hint="Order three steps, one word, then 2."),
    )


@_u23_variant("proprioception_balance", "sms", "difficult", "clinic_pick_then_ethics_mcq")
def _proprioception_balance_difficult_sms_clinic_pick_then_ethics_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Balance tests are done by trained staff with consent",
            "Results stay with the clinic, not in a class quiz",
        ),
        (
            "Pupils should spin each other until unwell",
            "The clinic ranks patients by dizziness",
        ),
        2,
    )
    correct = "use supplied study data and models; never spin pupils or record who felt unwell"
    distractors = (
        "spin the class and record who wobbled",
        "store who felt dizzy in the app",
        "rank pupils by balance",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional documentary shows a balance clinic assessing a patient "
        "after an ear infection.</p>"
        "<p>(i) Select the two statements consistent with the documentary.</p>"
        "<p>(ii) Using the first statement from (i), a school lesson on balance should</p>"
    )
    solution = (
        "(i) Consent and trained staff; results stay clinical.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Clinical tests are clinical; class uses models and data."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Consistent statements", "School lesson should"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the rule."),
    )


PROPRIOCEPTION_BALANCE_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _proprioception_balance_intermediate_ms_systems_count_then_canal_mcq,
        _proprioception_balance_intermediate_ms_canal_order_then_word,
        _proprioception_balance_intermediate_ms_position_pick_then_word,
    ],
    "difficult": [
        _proprioception_balance_difficult_ms_model_rate_then_lag_mcq_then_word,
        _proprioception_balance_difficult_ms_dark_order_then_pick,
        _proprioception_balance_difficult_ms_planes_count_then_mcq_then_word,
    ],
}

PROPRIOCEPTION_BALANCE_SMS_POOLS = {
    "foundational": [],
    "intermediate": [
        _proprioception_balance_intermediate_sms_athlete_inputs_then_mcq_then_word,
        _proprioception_balance_intermediate_sms_trainee_pick_then_order,
        _proprioception_balance_intermediate_sms_robot_sensors_then_match_mcq,
    ],
    "difficult": [
        _proprioception_balance_difficult_sms_study_drop_then_caution_pick_then_verdict,
        _proprioception_balance_difficult_sms_conflict_order_then_word_then_count,
        _proprioception_balance_difficult_sms_clinic_pick_then_ethics_mcq,
    ],
}


# ---------------------------------------------------------------------------
# interoception — multi_step stays — (a context-free chain would invite
# artificial inference about internal states); situational (I, D) only, with
# fictional cases: ambiguous signal → alternative interpretations → signpost.
# ---------------------------------------------------------------------------

_IN_SMS_I_STAGE_PACKS = (
    {"who": "Riley", "event": "a fictional school play", "signal": "a fast heartbeat"},
    {"who": "Casey", "event": "a fictional piano recital", "signal": "a fluttery stomach"},
    {"who": "Morgan", "event": "a fictional football final", "signal": "tense shoulders"},
)


@_u23_variant("interoception", "sms", "intermediate", "stage_signal_then_interpret_mcq_then_word")
def _interoception_intermediate_sms_stage_signal_then_interpret_mcq_then_word():
    pack = random.choice(_IN_SMS_I_STAGE_PACKS)
    correct = "the same signal could mean excitement or nerves; the story does not decide for the character"
    distractors = (
        "the signal proves an illness the app can diagnose",
        f"{pack['who']} should compare moods with classmates",
        "a fast heartbeat always means fear",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional story, {pack['who']} notices {pack['signal']} just before "
        f"{pack['event']}.</p>"
        "<p>(i) Enter how many possible meanings (excitement, nerves) the story offers "
        "for the signal.</p>"
        "<p>(ii) Given the meanings in (i), the scientific reading is that</p>"
        "<p>(iii) Write the one-word name of the sense that notices internal signals.</p>"
    )
    solution = (
        "(i) <strong>2</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>interoception</strong>"
    )
    hint = "<strong>Key idea:</strong> One signal, more than one interpretation, no diagnosis."
    return (
        question, solution, hint, 3,
        _fields((2, letter, "interoception"), ("Possible meanings", "Lesson's reading", "Sense"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Enter 2, choose, then one word."),
    )


_IN_SMS_I_LUNCH_PACKS = (
    {"who": "Alex", "signal": "a rumbling stomach", "context": "a fictional long exam morning"},
    {"who": "Sam", "signal": "a dry mouth", "context": "a fictional hot sports day"},
    {"who": "Jordan", "signal": "heavy eyelids", "context": "a fictional late-night coach trip"},
)


@_u23_variant("interoception", "sms", "intermediate", "need_signal_pick_then_order")
def _interoception_intermediate_sms_need_signal_pick_then_order():
    pack = random.choice(_IN_SMS_I_LUNCH_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Interoception senses internal states such as hunger or thirst",
            "The same signal can be interpreted in more than one way",
        ),
        (
            f"The quiz should collect how {pack['who']}'s classmates feel right now",
            "Internal signals are only a joke",
        ),
        2,
    )
    order_raw, order_bank = _u23_order_field(
        (
            "An internal signal is noticed",
            "The context suggests a likely need",
            "The character acts, for example by eating or drinking",
        ),
        ("The class ranks who felt it most",),
    )
    question = (
        f"<p>In a fictional case, {pack['who']} notices {pack['signal']} during "
        f"{pack['context']}.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), order how the character "
        "makes sense of the signal.</p>"
    )
    solution = (
        "(i) Internal sense; multiple interpretations.<br>"
        "(ii) <strong>notice → context suggests need → act</strong>"
    )
    hint = "<strong>Key idea:</strong> Signal, context, action — in a fictional case only."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "Making sense of the signal"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


@_u23_variant("interoception", "sms", "intermediate", "helpline_story_order_then_word")
def _interoception_intermediate_sms_helpline_story_order_then_word():
    order_raw, order_bank = _u23_order_field(
        (
            "The character notices an unfamiliar internal signal that keeps returning",
            "The character talks to a trusted adult about it",
            "A qualified person decides what, if anything, is needed",
        ),
        ("The app diagnoses the character from the story",),
    )
    question = (
        "<p>A fictional short film follows a character who keeps noticing a "
        "worrying internal signal.</p>"
        "<p>(i) Order the response the film models.</p>"
        "<p>(ii) Write the one-word verb from step 2 of (i) for pointing someone "
        "towards a trusted adult or qualified help.</p>"
    )
    solution = (
        "(i) <strong>notice → trusted adult → qualified person decides</strong><br>"
        "(ii) <strong>signpost</strong>"
    )
    hint = "<strong>Key idea:</strong> Notice, tell a trusted adult, let qualified people decide."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "signpost"), ("Response modelled", "Verb"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


_IN_SMS_D_SURVEY_PACKS = (
    {"study": "fictional anonymous wellbeing survey", "asked": 400, "helpful": 300},
    {"study": "fictional textbook teaching dataset", "asked": 250, "helpful": 200},
    {"study": "fictional public-health leaflet aggregate", "asked": 500, "helpful": 350},
)


@_u23_variant("interoception", "sms", "difficult", "survey_pct_then_caution_pick_then_verdict")
def _interoception_difficult_sms_survey_pct_then_caution_pick_then_verdict():
    pack = random.choice(_IN_SMS_D_SURVEY_PACKS)
    pct = _pct(pack["helpful"], pack["asked"])
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The survey is anonymous and aggregated; no individual is profiled",
            "Self-reported answers are not a measurement of anyone's health",
        ),
        (
            "The class should repeat the survey and compare moods",
            "The figure diagnoses the respondents",
        ),
        2,
    )
    correct = "many people find noticing internal signals useful; the survey diagnoses nobody"
    distractors = (
        "the app can now diagnose anxiety from a heartbeat story",
        "respondents should be ranked by mood",
        "noticing signals means the person is ill",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['study']} reports that {pack['helpful']} of {pack['asked']} "
        "adults said that noticing internal signals helped them look after "
        "their wellbeing.</p>"
        "<p>(i) Calculate that as a whole-number percentage.</p>"
        "<p>(ii) Using the figure from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair reading is that</p>"
    )
    solution = (
        f"(i) {pack['helpful']} ÷ {pack['asked']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) Anonymous aggregate; self-report.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage of a group, never a profile of a person."
    return (
        question, solution, hint, 3,
        _fields((pct, pick_raw, letter), ("Found it useful (%)", "Cautions", "Fair reading"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Percentage, two cautions, then the reading."),
    )


_IN_SMS_D_AMBIG_PACKS = (
    {"who": "a fictional exam candidate", "signal": "a racing heartbeat", "alts": ("caffeine", "nerves", "excitement")},
    {"who": "a fictional marathon runner", "signal": "light-headedness", "alts": ("not enough to drink", "heat", "effort")},
    {"who": "a fictional new pupil", "signal": "a churning stomach", "alts": ("hunger", "nerves", "a bug going round")},
)


@_u23_variant("interoception", "sms", "difficult", "ambiguous_count_then_order_then_word")
def _interoception_difficult_sms_ambiguous_count_then_order_then_word():
    pack = random.choice(_IN_SMS_D_AMBIG_PACKS)
    alts = pack["alts"]
    order_raw, order_bank = _u23_order_field(
        (
            "Notice the signal without assuming one cause",
            "Consider the alternative explanations and the context",
            "If it persists or worries the character, tell a trusted adult",
        ),
        ("Let the quiz diagnose the character",),
    )
    question = (
        f"<p>A fictional case study: {pack['who']} notices {pack['signal']}. The "
        f"textbook lists possible explanations: {alts[0]}, {alts[1]}, {alts[2]}.</p>"
        "<p>(i) Enter how many alternative explanations are listed.</p>"
        "<p>(ii) Given the alternatives in (i), order the scientific approach.</p>"
        "<p>(iii) Write the one-word name of the sense that noticed the signal.</p>"
    )
    solution = (
        "(i) <strong>3</strong><br>"
        "(ii) <strong>notice → weigh alternatives → tell a trusted adult if it persists</strong><br>"
        "(iii) <strong>interoception</strong>"
    )
    hint = "<strong>Key idea:</strong> Several explanations; weigh, don't diagnose; signpost."
    return (
        question, solution, hint, 3,
        _fields((3, order_raw, "interoception"), ("Alternatives", "Approach", "Sense"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Enter 3, order three steps, then one word."),
    )


@_u23_variant("interoception", "sms", "difficult", "app_claim_pick_then_verdict_mcq")
def _interoception_difficult_sms_app_claim_pick_then_verdict_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "A heart-rate number is a signal, not a diagnosis",
            "Interpretation depends on context and can differ between people",
        ),
        (
            "The app should tell users which illness they have",
            "Pupils should compare their readings in class",
        ),
        2,
    )
    correct = "treat the claim as unproven and keep diagnosis with qualified people"
    distractors = (
        "install it and compare classmates' readings",
        "accept it because the advert is confident",
        "use it to rank the class by calmness",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional consumer-affairs report reviews a wearable app that claims "
        "to 'diagnose stress from a pulse reading'.</p>"
        "<p>(i) Select the two scientific statements the report makes.</p>"
        "<p>(ii) Using the first statement from (i), the report's verdict is to</p>"
    )
    solution = (
        "(i) Signal not diagnosis; context-dependent.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> A number is not a diagnosis; qualified people decide."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Verdict"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the verdict."),
    )


INTEROCEPTION_MS_POOLS = {
    "foundational": [],
    "intermediate": [],
    "difficult": [],
}

INTEROCEPTION_SMS_POOLS = {
    "foundational": [],
    "intermediate": [
        _interoception_intermediate_sms_stage_signal_then_interpret_mcq_then_word,
        _interoception_intermediate_sms_need_signal_pick_then_order,
        _interoception_intermediate_sms_helpline_story_order_then_word,
    ],
    "difficult": [
        _interoception_difficult_sms_survey_pct_then_caution_pick_then_verdict,
        _interoception_difficult_sms_ambiguous_count_then_order_then_word,
        _interoception_difficult_sms_app_claim_pick_then_verdict_mcq,
    ],
}


# ---------------------------------------------------------------------------
# nonhuman_senses — multi_step (F, I, D); situational (F, I, D)
# ---------------------------------------------------------------------------

_NH_MS_F_LIST_PACKS = (
    {"animals": (("bee", "ultraviolet"), ("snake", "infrared"), ("bat", "echolocation")), "pick": ("bat", "echolocation")},
    {"animals": (("bird", "magnetic cues"), ("dolphin", "echolocation"), ("shark", "electric cues")), "pick": ("dolphin", "echolocation")},
    {"animals": (("bee", "ultraviolet"), ("bat", "echolocation"), ("snake", "infrared")), "pick": ("snake", "infrared")},
)


@_u23_variant("nonhuman_senses", "ms", "foundational", "list_count_then_signal_mcq")
def _nonhuman_senses_foundational_ms_list_count_then_signal_mcq():
    pack = random.choice(_NH_MS_F_LIST_PACKS)
    animal, sense = pack["pick"]
    meaning = {
        "echolocation": "returning sound used to locate objects",
        "infrared": "a heat-related signal humans do not see the same way",
        "ultraviolet": "light humans do not see the same way",
    }[sense]
    correct = meaning
    distractors = tuple(m for s, m in {
        "echolocation": "returning sound used to locate objects",
        "infrared": "a heat-related signal humans do not see the same way",
        "ultraviolet": "light humans do not see the same way",
    }.items() if s != sense) + ("light the animal gives out to see in the dark",)
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional zoo sign lists: "
        + ", ".join(f"{a} — {s}" for a, s in pack["animals"])
        + ".</p>"
        "<p>(i) Enter how many animals the sign lists.</p>"
        f"<p>(ii) Of the animals counted in (i), the {animal}'s {sense} is</p>"
    )
    solution = (
        "(i) <strong>3</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Count, then match the sense to its signal."
    return (
        question, solution, hint, 2,
        _fields((3, letter), ("Animals listed", f"{animal}'s {sense} is"),
                ("number", "mcq"), (None, options),
                hint="Enter 3, then choose the signal."),
    )


@_u23_variant("nonhuman_senses", "ms", "foundational", "echo_order_then_word")
def _nonhuman_senses_foundational_ms_echo_order_then_word():
    order_raw, order_bank = _u23_order_field(
        (
            "The animal sends out a sound",
            "The sound reflects from an object",
            "The returning sound tells the animal where the object is",
        ),
        ("The animal casts a spell to find the object",),
    )
    question = (
        "<p>A fictional nature documentary explains how a bat hunts in the dark.</p>"
        "<p>(i) Order the three steps.</p>"
        "<p>(ii) Write the one-word name for this way of sensing.</p>"
    )
    solution = (
        "(i) <strong>send sound → reflects → returning sound locates</strong><br>"
        "(ii) <strong>echolocation</strong>"
    )
    hint = "<strong>Key idea:</strong> Send, bounce, receive."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "echolocation"), ("Steps", "Way of sensing"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


@_u23_variant("nonhuman_senses", "ms", "foundational", "signal_pick_then_count")
def _nonhuman_senses_foundational_ms_signal_pick_then_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Some animals sense UV that humans do not see the same way",
            "Some animals sense infrared as a heat-related signal",
        ),
        (
            "Nonhuman senses are spells, not detectable signals",
            "The quiz should rank which pupil has a superpower",
        ),
        2,
    )
    question = (
        "<p>A fictional science-museum panel describes animal senses.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Enter how many kinds of light-family signal (UV, infrared) you "
        "selected in (i).</p>"
    )
    solution = (
        "(i) UV; infrared.<br>"
        "(ii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Two bands beyond human sight."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Light-family signals"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


_NH_MS_I_ULTRA_PACKS = (
    {"animal": "bat", "khz": 50, "limit": 20},
    {"animal": "dolphin", "khz": 100, "limit": 20},
    {"animal": "moth-hunting bat", "khz": 40, "limit": 20},
)


@_u23_variant("nonhuman_senses", "ms", "intermediate", "ultrasound_ratio_then_band_mcq")
def _nonhuman_senses_intermediate_ms_ultrasound_ratio_then_band_mcq():
    pack = random.choice(_NH_MS_I_ULTRA_PACKS)
    ratio = pack["khz"] // pack["limit"]
    correct = "above the usual human hearing band, so people cannot hear it"
    distractors = (
        "below the human band, so it sounds very low",
        "a form of light, so it is seen not heard",
        "within the human band, but too quiet to hear",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook gives a {pack['animal']}'s call as about "
        f"{pack['khz']} kHz and the usual upper human hearing limit as "
        f"{pack['limit']} kHz.</p>"
        "<p>(i) How many times higher is the call frequency than the human limit?</p>"
        "<p>(ii) The call in (i) is ultrasound, which is</p>"
    )
    solution = (
        f"(i) {pack['khz']} ÷ {pack['limit']} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then 'above the band' means inaudible to us."
    return (
        question, solution, hint, 2,
        _fields((ratio, letter), ("Times higher", "Ultrasound is"),
                ("number", "mcq"), (None, options),
                hint="Divide, then choose the band idea."),
    )


@_u23_variant("nonhuman_senses", "ms", "intermediate", "receptor_order_then_tech_word")
def _nonhuman_senses_intermediate_ms_receptor_order_then_tech_word():
    order_raw, order_bank = _u23_order_field(
        (
            "A warm animal gives off infrared",
            "A pit receptor on the snake detects the infrared",
            "The snake locates the prey in darkness",
        ),
        ("The snake votes on where the prey is",),
    )
    question = (
        "<p>A fictional reptile-house display explains a pit viper's heat sense.</p>"
        "<p>(i) Order the chain.</p>"
        "<p>(ii) Name the human technology that detects the same signal as step 2 "
        "of (i) — one word (a thermal ____).</p>"
    )
    solution = (
        "(i) <strong>infrared given off → pit receptor detects → prey located</strong><br>"
        "(ii) <strong>camera</strong>"
    )
    hint = "<strong>Key idea:</strong> Signal, receptor, function — and a thermal camera copies it."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "camera"), ("Chain", "Technology"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


@_u23_variant("nonhuman_senses", "ms", "intermediate", "match_pick_then_count")
def _nonhuman_senses_intermediate_ms_match_pick_then_count():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Echolocation ↔ sonar",
            "Infrared sensing ↔ thermal camera",
            "Magnetic sensing ↔ compass",
        ),
        (
            "Echolocation ↔ a spell book",
            "UV sensing ↔ a pupil superpower ranking",
        ),
        3,
    )
    question = (
        "<p>A fictional engineering worksheet pairs animal senses with technology.</p>"
        "<p>(i) Select the three correct pairs.</p>"
        "<p>(ii) Enter how many pairs you selected in (i).</p>"
    )
    solution = (
        "(i) Sonar; thermal camera; compass.<br>"
        "(ii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Each sense has a technology that detects the same signal."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Correct pairs", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_NH_MS_D_ECHO_PACKS = (
    {"animal": "bat", "t_ms": 20, "v": 340, "d": 3.4},
    {"animal": "dolphin", "t_ms": 40, "v": 1500, "d": 30},
    {"animal": "bat", "t_ms": 10, "v": 340, "d": 1.7},
)


@_u23_variant("nonhuman_senses", "ms", "difficult", "echo_distance_then_mcq_then_word")
def _nonhuman_senses_difficult_ms_echo_distance_then_mcq_then_word():
    pack = random.choice(_NH_MS_D_ECHO_PACKS)
    correct = "the returning sound; a shorter delay means a nearer object"
    distractors = (
        "the colour of the object",
        "a magnetic field from the object",
        "the heat given off by the object",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional textbook gives a {pack['animal']}'s echo delay as "
        f"{pack['t_ms']} ms with sound at {pack['v']} m/s in its medium.</p>"
        "<p>(i) Calculate the distance to the object (sound goes there and back).</p>"
        "<p>(ii) The animal judges the distance in (i) from</p>"
        "<p>(iii) Write the one-word technology that uses the same principle at sea.</p>"
    )
    solution = (
        f"(i) {pack['v']} × {pack['t_ms']}/1000 ÷ 2 = <strong>{pack['d']}</strong> m<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>sonar</strong>"
    )
    hint = "<strong>Key idea:</strong> Distance = speed × time ÷ 2; delay encodes distance."
    return (
        question, solution, hint, 3,
        _fields((pack["d"], letter, "sonar"), ("Distance (m)", "Judged from", "Technology"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Halve the round trip, choose, then one word."),
    )


@_u23_variant("nonhuman_senses", "ms", "difficult", "evidence_order_then_pick")
def _nonhuman_senses_difficult_ms_evidence_order_then_pick():
    order_raw, order_bank = _u23_order_field(
        (
            "Observe that birds still navigate when the sky is hidden",
            "Test by changing the magnetic field around the birds",
            "Conclude they use magnetic cues if their direction changes",
        ),
        ("Conclude they use magic because the result is surprising",),
    )
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The conclusion must come from a testable experiment",
            "A technology sensor (a compass) detects the same cue",
        ),
        (
            "Nonhuman senses are spells",
            "The birds should be ranked by superpower",
        ),
        2,
    )
    question = (
        "<p>A fictional research summary describes how scientists tested whether "
        "migrating birds use magnetic cues.</p>"
        "<p>(i) Order the scientific method used.</p>"
        "<p>(ii) Using the conclusion step from (i), select the two statements "
        "that keep it scientific.</p>"
    )
    solution = (
        "(i) <strong>observe → change the field → conclude from the change</strong><br>"
        "(ii) Testable experiment; compass detects the same cue."
    )
    hint = "<strong>Key idea:</strong> Observe, test, conclude — and compare with a sensor."
    return (
        question, solution, hint, 2,
        _fields((order_raw, pick_raw), ("Method", "Keeping it scientific"),
                ("order", "pick"), (order_bank, pick_bank), (None, pick_count),
                hint="Order three steps, then two statements."),
    )


_NH_MS_D_UV_PACKS = (
    {"flower": "a fictional yellow flower", "human": 1, "uv": 2},
    {"flower": "a fictional white orchid", "human": 1, "uv": 3},
    {"flower": "a fictional dandelion-like flower", "human": 1, "uv": 2},
)


@_u23_variant("nonhuman_senses", "ms", "difficult", "uv_pattern_count_then_mcq_then_word")
def _nonhuman_senses_difficult_ms_uv_pattern_count_then_mcq_then_word():
    pack = random.choice(_NH_MS_D_UV_PACKS)
    extra = pack["uv"] - pack["human"]
    correct = "bees sense UV that humans do not see the same way, so the flower shows extra markings"
    distractors = (
        "bees see the same colours as humans, only more sharply",
        "the camera invents patterns",
        "the flower changes colour when a bee lands",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional botany page shows {pack['flower']}: a normal photo shows "
        f"{pack['human']} colour zone, a UV camera shows {pack['uv']} zones.</p>"
        "<p>(i) Calculate how many extra zones the UV camera reveals.</p>"
        "<p>(ii) The extra zones in (i) matter to a bee because</p>"
        "<p>(iii) Write the one-word technology sensor that revealed them (a UV ____).</p>"
    )
    solution = (
        f"(i) {pack['uv']} − {pack['human']} = <strong>{extra}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>camera</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then a different band shows different patterns."
    return (
        question, solution, hint, 3,
        _fields((extra, letter, "camera"), ("Extra zones", "Why it matters", "Sensor"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


# nonhuman_senses — situational_multi_step (F, I, D)

_NH_SMS_F_CAVE_PACKS = (
    {"where": "fictional cave tour", "bats": 40, "animal": "bat"},
    {"where": "fictional night safari", "bats": 25, "animal": "bat"},
    {"where": "fictional aquarium show", "bats": 6, "animal": "dolphin"},
)


@_u23_variant("nonhuman_senses", "sms", "foundational", "tour_count_then_echo_mcq")
def _nonhuman_senses_foundational_sms_tour_count_then_echo_mcq():
    pack = random.choice(_NH_SMS_F_CAVE_PACKS)
    correct = "returning sound to locate objects"
    distractors = (
        "heat given off by warm objects",
        "light humans do not see the same way",
        "smell trails to locate objects",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>On a {pack['where']}, a guide counts {pack['bats']} {pack['animal']}s "
        "finding their way in the dark.</p>"
        f"<p>(i) Enter the number of {pack['animal']}s counted.</p>"
        f"<p>(ii) The {pack['animal']}s counted in (i) find their way using</p>"
    )
    solution = (
        f"(i) <strong>{pack['bats']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Count, then echolocation."
    return (
        question, solution, hint, 2,
        _fields((pack["bats"], letter), (f"{pack['animal'].capitalize()}s counted", "They navigate using"),
                ("number", "mcq"), (None, options),
                hint="Count, then choose echolocation."),
    )


_NH_SMS_F_ZOO_PACKS = (
    {"where": "fictional reptile house", "animal": "pit viper", "signal": "infrared"},
    {"where": "fictional butterfly house", "animal": "butterfly", "signal": "ultraviolet"},
    {"where": "fictional aquarium", "animal": "shark", "signal": "electric cues"},
)


@_u23_variant("nonhuman_senses", "sms", "foundational", "zoo_signal_pick_then_count")
def _nonhuman_senses_foundational_sms_zoo_signal_pick_then_count():
    pack = random.choice(_NH_SMS_F_ZOO_PACKS)
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            f"The {pack['animal']} detects {pack['signal']}, a real detectable signal",
            "A human-made sensor can detect the same signal",
        ),
        (
            "The animal's sense is a spell",
            "Visitors should be ranked by superpower",
        ),
        2,
    )
    question = (
        f"<p>A sign at a {pack['where']} explains that the {pack['animal']} senses "
        f"{pack['signal']}.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Enter how many statements you selected in (i).</p>"
    )
    solution = (
        "(i) Real signal; a sensor can detect it too.<br>"
        "(ii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Detectable signal, matched by technology."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


@_u23_variant("nonhuman_senses", "sms", "foundational", "sonar_order_then_word")
def _nonhuman_senses_foundational_sms_sonar_order_then_word():
    order_raw, order_bank = _u23_order_field(
        (
            "The ship sends out a sound pulse",
            "The pulse reflects from the seabed",
            "The returning pulse gives the depth",
        ),
        ("The ship ranks its crew by hearing",),
    )
    question = (
        "<p>A fictional fishing-boat skipper explains the boat's depth finder.</p>"
        "<p>(i) Order how it works.</p>"
        "<p>(ii) Write the one-word animal sense that works the same way.</p>"
    )
    solution = (
        "(i) <strong>send pulse → reflect → returning pulse gives depth</strong><br>"
        "(ii) <strong>echolocation</strong>"
    )
    hint = "<strong>Key idea:</strong> Sonar copies echolocation."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "echolocation"), ("How it works", "Animal sense"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


_NH_SMS_I_DRONE_PACKS = (
    {"team": "fictional rescue team", "device": "a thermal camera", "signal": "infrared", "animal": "pit viper"},
    {"team": "fictional survey team", "device": "a sonar unit", "signal": "returning sound", "animal": "dolphin"},
    {"team": "fictional flower-mapping team", "device": "a UV camera", "signal": "ultraviolet", "animal": "bee"},
)


@_u23_variant("nonhuman_senses", "sms", "intermediate", "team_device_then_animal_mcq_then_word")
def _nonhuman_senses_intermediate_sms_team_device_then_animal_mcq_then_word():
    pack = random.choice(_NH_SMS_I_DRONE_PACKS)
    correct = f"the {pack['animal']}, which senses {pack['signal']}"
    others = [a for a in ("pit viper", "dolphin", "bee") if a != pack["animal"]]
    distractors = (
        f"the {others[0]}, which senses something else",
        f"the {others[1]}, which senses something else",
        "no animal; only instruments can sense this",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['team']} uses {pack['device']} that detects {pack['signal']}.</p>"
        "<p>(i) Enter how many devices the team uses.</p>"
        "<p>(ii) The device in (i) copies the sense of</p>"
        "<p>(iii) Write the one-word term for a detectable physical input like "
        f"{pack['signal']} (a ______ the sensor picks up).</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>signal</strong>"
    )
    hint = "<strong>Key idea:</strong> Technology and animal detect the same signal."
    return (
        question, solution, hint, 3,
        _fields((1, letter, "signal"), ("Devices", "Copies the sense of", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Enter 1, choose, then one word."),
    )


_NH_SMS_I_FARM_PACKS = (
    {"place": "fictional farm", "pest": "moths", "khz": 45, "limit": 20},
    {"place": "fictional orchard", "pest": "insects", "khz": 60, "limit": 20},
    {"place": "fictional warehouse", "pest": "rodents", "khz": 30, "limit": 20},
)


@_u23_variant("nonhuman_senses", "sms", "intermediate", "deterrent_ratio_then_pick")
def _nonhuman_senses_intermediate_sms_deterrent_ratio_then_pick():
    pack = random.choice(_NH_SMS_I_FARM_PACKS)
    ratio = pack["khz"] // pack["limit"]
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "The sound is above the usual human hearing band",
            "Some animals hear frequencies humans do not",
        ),
        (
            "The device works by magic",
            "Workers should be ranked by hearing",
        ),
        2,
    )
    question = (
        f"<p>A {pack['place']} installs a device emitting {pack['khz']} kHz to "
        f"deter {pack['pest']}; the usual upper human limit is {pack['limit']} kHz.</p>"
        "<p>(i) How many times higher is the device's frequency than the human limit?</p>"
        "<p>(ii) Using the comparison from (i), select the two statements that "
        "explain why workers hear nothing.</p>"
    )
    solution = (
        f"(i) {pack['khz']} ÷ {pack['limit']} = <strong>{ratio}</strong><br>"
        "(ii) Above the human band; some animals hear higher."
    )
    hint = "<strong>Key idea:</strong> Divide, then ultrasound is above our band."
    return (
        question, solution, hint, 2,
        _fields((ratio, pick_raw), ("Times higher", "Why workers hear nothing"),
                ("number", "pick"), (None, pick_bank), (None, pick_count),
                hint="Divide, then two statements."),
    )


@_u23_variant("nonhuman_senses", "sms", "intermediate", "migration_order_then_compass_word")
def _nonhuman_senses_intermediate_sms_migration_order_then_compass_word():
    order_raw, order_bank = _u23_order_field(
        (
            "Earth's magnetic field provides a cue",
            "Sensing structures in the bird respond to it",
            "The bird keeps a heading over long distances",
        ),
        ("The bird asks a fictional celebrity for directions",),
    )
    question = (
        "<p>A fictional wildlife-tracking project follows tagged birds migrating "
        "at night.</p>"
        "<p>(i) Order the model the project uses.</p>"
        "<p>(ii) Write the one-word instrument humans use to detect the cue in step 1.</p>"
    )
    solution = (
        "(i) <strong>magnetic cue → sensing structures → heading kept</strong><br>"
        "(ii) <strong>compass</strong>"
    )
    hint = "<strong>Key idea:</strong> Cue, receptor, function — matched by a compass."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "compass"), ("Model", "Instrument"),
                ("order", "keyword"), (order_bank, None),
                hint="Order three steps, then one word."),
    )


_NH_SMS_D_TRIAL_PACKS = (
    {"trial": "fictional rescue-drone field trial", "finds_thermal": 45, "finds_normal": 15, "n": 50},
    {"trial": "fictional coastguard sonar trial", "finds_thermal": 40, "finds_normal": 10, "n": 50},
    {"trial": "fictional wildlife-survey trial", "finds_thermal": 36, "finds_normal": 12, "n": 40},
)


@_u23_variant("nonhuman_senses", "sms", "difficult", "trial_ratio_then_caution_pick_then_verdict")
def _nonhuman_senses_difficult_sms_trial_ratio_then_caution_pick_then_verdict():
    pack = random.choice(_NH_SMS_D_TRIAL_PACKS)
    ratio = pack["finds_thermal"] // pack["finds_normal"]
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "Conditions such as weather could differ between runs",
            "One trial is limited evidence; repeat it",
        ),
        (
            "The sensor works by magic",
            "Operators should be ranked by superpower",
        ),
        2,
    )
    correct = "the bio-inspired sensor found more targets in this trial, within its limits"
    distractors = (
        "the sensor copies the animal's sense perfectly",
        "the trial should rank operators",
        "the sensor detects nothing real",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['trial']} reports {pack['finds_thermal']} finds out of "
        f"{pack['n']} targets with a bio-inspired sensor versus "
        f"{pack['finds_normal']} with ordinary equipment.</p>"
        "<p>(i) How many times more finds did the bio-inspired sensor make?</p>"
        "<p>(ii) Using the comparison from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['finds_thermal']} ÷ {pack['finds_normal']} = <strong>{ratio}</strong><br>"
        "(ii) Conditions may differ; repeat the trial.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Ratio, cautions, honest verdict."
    return (
        question, solution, hint, 3,
        _fields((ratio, pick_raw, letter), ("Times more finds", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Ratio, two cautions, then the verdict."),
    )


_NH_SMS_D_SHARK_PACKS = (
    {"lab": "fictional marine lab", "animal": "shark", "cue": "weak electric fields from prey muscles"},
    {"lab": "fictional river station", "animal": "electric fish", "cue": "distortions in its own electric field"},
    {"lab": "fictional aquarium research unit", "animal": "ray", "cue": "electric signals from buried prey"},
)


@_u23_variant("nonhuman_senses", "sms", "difficult", "electric_order_then_word_then_count")
def _nonhuman_senses_difficult_sms_electric_order_then_word_then_count():
    pack = random.choice(_NH_SMS_D_SHARK_PACKS)
    order_raw, order_bank = _u23_order_field(
        (
            f"The prey produces {pack['cue']}",
            f"Special receptors on the {pack['animal']} detect the field",
            f"The {pack['animal']} locates hidden prey",
        ),
        ("The animal uses a spell to find prey",),
    )
    question = (
        f"<p>A {pack['lab']} explains how a {pack['animal']} finds prey it cannot see.</p>"
        "<p>(i) Order the sensing chain.</p>"
        "<p>(ii) Write the one-word human instrument that detects electric signals "
        "(a volt_____).</p>"
        "<p>(iii) Enter how many steps the chain in (i) has.</p>"
    )
    solution = (
        "(i) <strong>prey's field → receptors detect → prey located</strong><br>"
        "(ii) <strong>voltmeter</strong><br>"
        "(iii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Signal, receptor, function — and a voltmeter detects the same."
    return (
        question, solution, hint, 3,
        _fields((order_raw, "voltmeter", 3), ("Sensing chain", "Instrument", "Steps"),
                ("order", "keyword", "number"), (order_bank, None, None),
                hint="Order three steps, one word, then 3."),
    )


@_u23_variant("nonhuman_senses", "sms", "difficult", "claim_pick_then_test_mcq")
def _nonhuman_senses_difficult_sms_claim_pick_then_test_mcq():
    pick_raw, pick_bank, pick_count = _u23_pick_field(
        (
            "A sense must detect a real, measurable signal",
            "The claim can be tested with a controlled experiment",
        ),
        (
            "Nonhuman senses are spells",
            "The animal should be ranked as the class superpower",
        ),
        2,
    )
    correct = "test it: hide the food where no smell, sound or sight cue is possible and see if the dog still finds it"
    distractors = (
        "accept it because the video is popular",
        "accept it because dogs have a strong sense of smell",
        "assume the dog guessed by luck every time",
    )
    options, letter = _u23_mcq_field(correct, distractors)
    question = (
        "<p>A fictional viral video claims a dog can 'sense' hidden food through "
        "a sixth sense.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), the scientific response is to</p>"
    )
    solution = (
        "(i) Real measurable signal; testable.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Senses detect signals; claims get controlled tests."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Response"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the test."),
    )


NONHUMAN_SENSES_MS_POOLS = {
    "foundational": [
        _nonhuman_senses_foundational_ms_list_count_then_signal_mcq,
        _nonhuman_senses_foundational_ms_echo_order_then_word,
        _nonhuman_senses_foundational_ms_signal_pick_then_count,
    ],
    "intermediate": [
        _nonhuman_senses_intermediate_ms_ultrasound_ratio_then_band_mcq,
        _nonhuman_senses_intermediate_ms_receptor_order_then_tech_word,
        _nonhuman_senses_intermediate_ms_match_pick_then_count,
    ],
    "difficult": [
        _nonhuman_senses_difficult_ms_echo_distance_then_mcq_then_word,
        _nonhuman_senses_difficult_ms_evidence_order_then_pick,
        _nonhuman_senses_difficult_ms_uv_pattern_count_then_mcq_then_word,
    ],
}

NONHUMAN_SENSES_SMS_POOLS = {
    "foundational": [
        _nonhuman_senses_foundational_sms_tour_count_then_echo_mcq,
        _nonhuman_senses_foundational_sms_zoo_signal_pick_then_count,
        _nonhuman_senses_foundational_sms_sonar_order_then_word,
    ],
    "intermediate": [
        _nonhuman_senses_intermediate_sms_team_device_then_animal_mcq_then_word,
        _nonhuman_senses_intermediate_sms_deterrent_ratio_then_pick,
        _nonhuman_senses_intermediate_sms_migration_order_then_compass_word,
    ],
    "difficult": [
        _nonhuman_senses_difficult_sms_trial_ratio_then_caution_pick_then_verdict,
        _nonhuman_senses_difficult_sms_electric_order_then_word_then_count,
        _nonhuman_senses_difficult_sms_claim_pick_then_test_mcq,
    ],
}
