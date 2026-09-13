"""S3 Unit 3.1 Machines advanced Practice pools (MS / SMS). Isolated from lesson banks.

Batch 4.1. Six topics (docs/EURSC_ADVANCED_QUESTIONS.md):

  force_work_machines  MS F, I, D   SMS F, I, D   (W = Fd only; never power)
  energy               MS F, I, D   (SMS: pilot, s3_machines.py)
  electrostatics       MS F, I, D   SMS F, I, D
  electric_current     MS F, I, D   SMS F, I, D   (qualitative; never V = IR)
  magnetism            MS I, D      SMS F, I, D   (foundational MS —)
  robotics_project     MS F, I, D   SMS F, I, D   (planning / evidence only)

Syllabus boundaries for this batch, enforced by the smoke's content tests:
  * force/work items may use work = force × distance in joules; no item
    mentions power, watts, or work per unit time;
  * circuit items are qualitative (loop, series/parallel, conductor/insulator,
    switch, effects, meter placement); no item mentions V = IR, resistance,
    ohms or any resistance calculation;
  * robotics items grade requirements, component choice, sense–decide–act
    logic, test evidence and iteration — never the physical robot or a
    private code upload;
  * every scenario is a fictional lab, workshop, public dataset or textbook
    model; no household wiring, home-shock or private energy-bill prompts,
    and no ranking of pupils' builds.
"""
import random

from generators.eursc.science_shared import (
    charge_pair,
    circuit_boxes,
    lever_boxes,
    magnet_poles,
    sankey_bars,
)
from generators.shared.utils import graded_answer_number_fields, make_graded_problem

_LEVEL = "eursc"
_SUBJECT = "science"


def _u31_variant(topic, mode_tag, difficulty, suffix):
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


def _mcq(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _order(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"1|{'|'.join(step_ids)}", bank


def _pick(correct_texts, distractor_texts, pick_count):
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
# force_work_machines — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_FW_MS_F_WORK_PACKS = (
    {"force": 20, "dist": 3, "work": 60},
    {"force": 15, "dist": 4, "work": 60},
    {"force": 25, "dist": 2, "work": 50},
)


@_u31_variant("force_work_machines", "ms", "foundational", "work_then_unit_mcq")
def _force_work_machines_foundational_ms_work_then_unit_mcq():
    pack = random.choice(_FW_MS_F_WORK_PACKS)
    correct = "joule"
    distractors = ("newton", "metre", "a class ranking")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional lab card: a crate is pushed with a force of {pack['force']} N "
        f"through {pack['dist']} m along the same line.</p>"
        "<p>(i) Calculate the work done.</p>"
        "<p>(ii) The unit of the answer in (i) is the</p>"
    )
    solution = (
        f"(i) {pack['force']} × {pack['dist']} = <strong>{pack['work']}</strong> J<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Work = force × distance, measured in joules."
    return (
        question, solution, hint, 2,
        _fields((pack["work"], letter), ("Work done (J)", "Unit"),
                ("number", "mcq"), (None, options), hint="Multiply, then name the unit."),
    )


@_u31_variant("force_work_machines", "ms", "foundational", "lever_letter_then_role_order")
def _force_work_machines_foundational_ms_lever_letter_then_role_order():
    diagram = str(lever_boxes(title="Fictional lever sketch"))
    order_raw, order_bank = _order(
        (
            "The effort is applied at one end",
            "The bar turns about the fulcrum",
            "The load at the other end is moved",
        ),
        ("The fulcrum creates extra energy",),
    )
    question = (
        diagram
        + "<p>A fictional lever sketch labels A effort, B fulcrum, C load.</p>"
        "<p>(i) Enter the letter of the pivot.</p>"
        "<p>(ii) Using the pivot from (i), order how the lever moves the load.</p>"
    )
    solution = (
        "(i) <strong>B</strong><br>"
        "(ii) <strong>effort applied → turns about fulcrum → load moved</strong>"
    )
    hint = "<strong>Key idea:</strong> B is the pivot; effort turns the bar to move the load."
    return (
        question, solution, hint, 2,
        _fields(("B", order_raw), ("Pivot letter", "How it moves the load"),
                ("keyword", "order"), (None, order_bank), hint="Enter B, then order three steps."),
    )


@_u31_variant("force_work_machines", "ms", "foundational", "machine_pick_then_count")
def _force_work_machines_foundational_ms_machine_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("A lever", "A pulley", "A ramp (inclined plane)"),
        ("A private energy diary", "A robot league table"),
        3,
    )
    question = (
        "<p>A fictional workshop poster lists simple machines.</p>"
        "<p>(i) Select the three simple machines.</p>"
        "<p>(ii) Enter how many machines you selected in (i).</p>"
    )
    solution = "(i) Lever; pulley; ramp.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Three classic simple machines."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Simple machines", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_FW_MS_I_RAMP_PACKS = (
    {"force": 50, "dist": 4, "work": 200, "height": 1},
    {"force": 40, "dist": 5, "work": 200, "height": 2},
    {"force": 30, "dist": 6, "work": 180, "height": 1.5},
)


@_u31_variant("force_work_machines", "ms", "intermediate", "ramp_work_then_trade_mcq")
def _force_work_machines_intermediate_ms_ramp_work_then_trade_mcq():
    pack = random.choice(_FW_MS_I_RAMP_PACKS)
    correct = "a smaller force over a larger distance; the work is not reduced"
    distractors = (
        "a larger force over a smaller distance",
        "energy created by the ramp",
        "a ranking of who pushed hardest",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional lab card: a box is pushed up a ramp with {pack['force']} N "
        f"along {pack['dist']} m of slope to gain {pack['height']} m of height.</p>"
        "<p>(i) Calculate the work done along the slope.</p>"
        "<p>(ii) Compared with lifting straight up, the ramp in (i) trades</p>"
    )
    solution = (
        f"(i) {pack['force']} × {pack['dist']} = <strong>{pack['work']}</strong> J<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Work = Fd; a machine trades force for distance."
    return (
        question, solution, hint, 2,
        _fields((pack["work"], letter), ("Work (J)", "The ramp trades"),
                ("number", "mcq"), (None, options), hint="Multiply, then choose the trade-off."),
    )


@_u31_variant("force_work_machines", "ms", "intermediate", "vector_order_then_work_word")
def _force_work_machines_intermediate_ms_vector_order_then_work_word():
    order_raw, order_bank = _order(
        (
            "Draw the force as an arrow with size and direction",
            "Measure the distance moved along the arrow's line",
            "Multiply force by distance to find the work",
        ),
        ("Divide the distance by the force",),
    )
    question = (
        "<p>A fictional physics worksheet shows how to find the work done by a push.</p>"
        "<p>(i) Order the method.</p>"
        "<p>(ii) Write the one-word unit of the quantity found in step 3 of (i).</p>"
    )
    solution = (
        "(i) <strong>draw the vector → measure distance → multiply</strong><br>"
        "(ii) <strong>joule</strong>"
    )
    hint = "<strong>Key idea:</strong> Vector, distance, product — in joules."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "joule"), ("Method", "Unit"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_FW_MS_I_PULLEY_PACKS = (
    {"load": 100, "effort": 50, "rope": 4, "lift": 2},
    {"load": 60, "effort": 30, "rope": 6, "lift": 3},
    {"load": 80, "effort": 40, "rope": 2, "lift": 1},
)


@_u31_variant("force_work_machines", "ms", "intermediate", "pulley_pick_then_rope_count")
def _force_work_machines_intermediate_ms_pulley_pick_then_rope_count():
    pack = random.choice(_FW_MS_I_PULLEY_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        (
            "The effort is smaller than the load",
            "The rope must be pulled further than the load rises",
        ),
        (
            "The pulley creates energy",
            "The work done is halved by the pulley",
        ),
        2,
    )
    question = (
        f"<p>A fictional pulley demo lifts a {pack['load']} N load with an effort of "
        f"{pack['effort']} N; the rope is pulled {pack['rope']} m to raise the load "
        f"{pack['lift']} m.</p>"
        "<p>(i) Select the two correct statements.</p>"
        "<p>(ii) Using the trade-off from (i), enter how many times further the rope "
        "moves than the load.</p>"
    )
    solution = (
        "(i) Smaller effort; longer rope pull.<br>"
        f"(ii) {pack['rope']} ÷ {pack['lift']} = <strong>{pack['rope'] // pack['lift']}</strong>"
    )
    hint = "<strong>Key idea:</strong> Less force, more distance; work is not reduced."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, pack["rope"] // pack["lift"]), ("Statements", "Times further"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then divide."),
    )


_FW_MS_D_COMPARE_PACKS = (
    {"f1": 200, "d1": 1, "f2": 50, "d2": 4},
    {"f1": 120, "d1": 2, "f2": 40, "d2": 6},
    {"f1": 300, "d1": 1, "f2": 100, "d2": 3},
)


@_u31_variant("force_work_machines", "ms", "difficult", "compare_work_then_mcq_then_word")
def _force_work_machines_difficult_ms_compare_work_then_mcq_then_word():
    pack = random.choice(_FW_MS_D_COMPARE_PACKS)
    w1 = pack["f1"] * pack["d1"]
    w2 = pack["f2"] * pack["d2"]
    correct = "the same work is done; the machine only changes the force–distance trade"
    distractors = (
        "the machine reduces the work",
        "the machine creates energy",
        "the direct lift does less work",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional lab compares two ways to raise a load: a direct lift with "
        f"{pack['f1']} N over {pack['d1']} m, and a machine needing {pack['f2']} N "
        f"over {pack['d2']} m.</p>"
        "<p>(i) Calculate the work for the direct lift.</p>"
        "<p>(ii) The machine's work equals the value in (i), so</p>"
        "<p>(iii) Write the one-word idea that a machine cannot break: energy ______.</p>"
    )
    solution = (
        f"(i) {pack['f1']} × {pack['d1']} = <strong>{w1}</strong> J (machine: {pack['f2']} × {pack['d2']} = {w2} J)<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>conservation</strong>"
    )
    hint = "<strong>Key idea:</strong> Equal work both ways; force traded for distance."
    return (
        question, solution, hint, 3,
        _fields((w1, letter, "conservation"), ("Direct-lift work (J)", "So", "Idea"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Multiply, choose, then one word."),
    )


@_u31_variant("force_work_machines", "ms", "difficult", "lever_order_then_pick_then_letter")
def _force_work_machines_difficult_ms_lever_order_then_pick_then_letter():
    diagram = str(lever_boxes(title="Fictional lever sketch"))
    order_raw, order_bank = _order(
        (
            "Place the fulcrum nearer the load",
            "The effort arm becomes longer than the load arm",
            "A smaller effort moves the load through a shorter distance",
        ),
        ("The lever now does less work",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        (
            "A machine does not create energy",
            "A simple machine can trade a smaller force for a larger distance",
        ),
        (
            "Work is force divided by distance",
            "The fulcrum supplies extra energy",
        ),
        2,
    )
    question = (
        diagram
        + "<p>A fictional engineering card explains lever design (A effort, B fulcrum, C load).</p>"
        "<p>(i) Order how moving the fulcrum reduces the effort needed.</p>"
        "<p>(ii) Using the trade-off from (i), select the two true statements.</p>"
        "<p>(iii) Enter the letter of the part moved in step 1.</p>"
    )
    solution = (
        "(i) <strong>fulcrum nearer load → longer effort arm → smaller effort, shorter load travel</strong><br>"
        "(ii) No energy created; force traded for distance.<br>"
        "(iii) <strong>B</strong>"
    )
    hint = "<strong>Key idea:</strong> Arm lengths trade force for distance; no free energy."
    return (
        question, solution, hint, 3,
        _fields((order_raw, pick_raw, "B"), ("Lever design", "True statements", "Part moved"),
                ("order", "pick", "keyword"), (order_bank, pick_bank, None), (None, pick_count, None),
                hint="Order, two statements, then B."),
    )


_FW_MS_D_DATA_PACKS = (
    {"rows": ((10, 2), (20, 2), (30, 2)), "works": (20, 40, 60)},
    {"rows": ((15, 4), (25, 4), (35, 4)), "works": (60, 100, 140)},
    {"rows": ((12, 5), (24, 5), (36, 5)), "works": (60, 120, 180)},
)


@_u31_variant("force_work_machines", "ms", "difficult", "table_work_then_pattern_mcq_then_count")
def _force_work_machines_difficult_ms_table_work_then_pattern_mcq_then_count():
    pack = random.choice(_FW_MS_D_DATA_PACKS)
    rows = pack["rows"]
    works = pack["works"]
    correct = "work is proportional to force when the distance is fixed"
    distractors = (
        "work is proportional to the mass of the pusher",
        "work falls as force rises",
        "the table ranks who pushed hardest",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional data table records pushes over a fixed distance: "
        + ", ".join(f"{f} N over {d} m" for f, d in rows)
        + ".</p>"
        "<p>(i) Calculate the work for the largest force.</p>"
        "<p>(ii) The pattern across the table, including (i), shows that</p>"
        "<p>(iii) Enter how many trials are in the table.</p>"
    )
    solution = (
        f"(i) {rows[-1][0]} × {rows[-1][1]} = <strong>{works[-1]}</strong> J<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Fixed distance, so work scales with force."
    return (
        question, solution, hint, 3,
        _fields((works[-1], letter, 3), ("Largest work (J)", "Pattern", "Trials"),
                ("number", "mcq", "number"), (None, options, None),
                hint="Multiply, choose, then enter 3."),
    )


# force_work_machines — situational_multi_step (F, I, D)

_FW_SMS_F_SITE_PACKS = (
    {"site": "fictional building site", "force": 40, "dist": 5, "work": 200},
    {"site": "fictional theatre set workshop", "force": 30, "dist": 4, "work": 120},
    {"site": "fictional bike-repair shop", "force": 25, "dist": 2, "work": 50},
)


@_u31_variant("force_work_machines", "sms", "foundational", "site_work_then_machine_mcq")
def _force_work_machines_foundational_sms_site_work_then_machine_mcq():
    pack = random.choice(_FW_SMS_F_SITE_PACKS)
    correct = "a ramp, which lets a smaller force act over a longer distance"
    distractors = (
        "a device that creates energy",
        "a ranking of the workers",
        "a stopwatch to measure work",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>At a {pack['site']}, a fictional worker pushes a load with "
        f"{pack['force']} N over {pack['dist']} m.</p>"
        "<p>(i) Calculate the work done.</p>"
        "<p>(ii) To do the work in (i) with less force, the worker could use</p>"
    )
    solution = (
        f"(i) {pack['force']} × {pack['dist']} = <strong>{pack['work']}</strong> J<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Work = Fd; a machine trades force for distance."
    return (
        question, solution, hint, 2,
        _fields((pack["work"], letter), ("Work (J)", "Could use"),
                ("number", "mcq"), (None, options), hint="Multiply, then choose the machine."),
    )


_FW_SMS_F_SEESAW_PACKS = (
    {"who": "Alex", "place": "a fictional playground", "parts": 3},
    {"who": "Sam", "place": "a fictional science fair", "parts": 3},
    {"who": "Jordan", "place": "a fictional museum exhibit", "parts": 3},
)


@_u31_variant("force_work_machines", "sms", "foundational", "seesaw_parts_then_pick")
def _force_work_machines_foundational_sms_seesaw_parts_then_pick():
    pack = random.choice(_FW_SMS_F_SEESAW_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("The fulcrum is the pivot the bar turns about", "The load is the object the machine moves"),
        ("The fulcrum is extra energy the lever creates", "Work is force divided by distance"),
        2,
    )
    question = (
        f"<p>{pack['who']} (fictional) studies a see-saw at {pack['place']}: it has "
        f"{pack['parts']} labelled parts — effort, fulcrum, load.</p>"
        "<p>(i) Enter the number of labelled parts.</p>"
        "<p>(ii) Using the parts from (i), select the two correct statements.</p>"
    )
    solution = (
        f"(i) <strong>{pack['parts']}</strong><br>"
        "(ii) Fulcrum is the pivot; load is what moves."
    )
    hint = "<strong>Key idea:</strong> Three lever parts; no free energy."
    return (
        question, solution, hint, 2,
        _fields((pack["parts"], pick_raw), ("Labelled parts", "Correct statements"),
                ("number", "pick"), (None, pick_bank), (None, pick_count),
                hint="Count, then two statements."),
    )


@_u31_variant("force_work_machines", "sms", "foundational", "crate_order_then_joule_word")
def _force_work_machines_foundational_sms_crate_order_then_joule_word():
    order_raw, order_bank = _order(
        (
            "A push (a force) is applied to the crate",
            "The crate moves a distance along the push",
            "Work has been done on the crate",
        ),
        ("The crate ranks the pushers",),
    )
    question = (
        "<p>A fictional removals crew slides a crate across a van floor.</p>"
        "<p>(i) Order what happens.</p>"
        "<p>(ii) Write the one-word unit of the quantity in step 3 of (i).</p>"
    )
    solution = (
        "(i) <strong>force applied → crate moves → work done</strong><br>"
        "(ii) <strong>joule</strong>"
    )
    hint = "<strong>Key idea:</strong> Force, distance, work in joules."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "joule"), ("What happens", "Unit"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_FW_SMS_I_STAGE_PACKS = (
    {"crew": "fictional stage crew", "load": 400, "effort": 100, "rope": 8, "lift": 2},
    {"crew": "fictional sailing crew", "load": 300, "effort": 150, "rope": 6, "lift": 3},
    {"crew": "fictional climbing-wall staff", "load": 200, "effort": 50, "rope": 12, "lift": 3},
)


@_u31_variant("force_work_machines", "sms", "intermediate", "stage_pulley_work_then_mcq_then_word")
def _force_work_machines_intermediate_sms_stage_pulley_work_then_mcq_then_word():
    pack = random.choice(_FW_SMS_I_STAGE_PACKS)
    work = pack["effort"] * pack["rope"]
    correct = "equal to lifting the load directly; the pulley trades force for rope distance"
    distractors = (
        "less than lifting directly, because the pulley saves energy",
        "zero, because the pulley does the work",
        "a ranking of the crew's strength",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A {pack['crew']} raises a {pack['load']} N load {pack['lift']} m using a "
        f"pulley: they pull with {pack['effort']} N through {pack['rope']} m of rope.</p>"
        "<p>(i) Calculate the work done on the rope.</p>"
        "<p>(ii) The work in (i) is</p>"
        "<p>(iii) Write the one-word name of the machine used.</p>"
    )
    solution = (
        f"(i) {pack['effort']} × {pack['rope']} = <strong>{work}</strong> J<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>pulley</strong>"
    )
    hint = "<strong>Key idea:</strong> Effort × rope distance = load × height; no saving in work."
    return (
        question, solution, hint, 3,
        _fields((work, letter, "pulley"), ("Work on rope (J)", "The work is", "Machine"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Multiply, choose, then one word."),
    )


_FW_SMS_I_WHEEL_PACKS = (
    {"who": "Riley", "task": "loading a fictional wheelchair-accessible van", "ramp_m": 3, "height_m": 0.5},
    {"who": "Casey", "task": "moving boxes into a fictional lorry", "ramp_m": 4, "height_m": 1},
    {"who": "Morgan", "task": "rolling a fictional drum onto a stage", "ramp_m": 6, "height_m": 1.5},
)


@_u31_variant("force_work_machines", "sms", "intermediate", "ramp_ratio_then_pick")
def _force_work_machines_intermediate_sms_ramp_ratio_then_pick():
    pack = random.choice(_FW_SMS_I_WHEEL_PACKS)
    ratio = pack["ramp_m"] / pack["height_m"]
    ratio = int(ratio) if float(ratio).is_integer() else ratio
    pick_raw, pick_bank, pick_count = _pick(
        (
            "The ramp lets a smaller force act over a longer distance",
            "The work done is the same as lifting straight up (ignoring friction)",
        ),
        (
            "The ramp creates energy",
            "The ramp halves the work",
        ),
        2,
    )
    question = (
        f"<p>{pack['who']} (fictional) is {pack['task']} using a {pack['ramp_m']} m "
        f"ramp that rises {pack['height_m']} m.</p>"
        "<p>(i) How many times longer is the ramp than the height gained?</p>"
        "<p>(ii) Using the ratio from (i), select the two correct statements.</p>"
    )
    solution = (
        f"(i) {pack['ramp_m']} ÷ {pack['height_m']} = <strong>{ratio}</strong><br>"
        "(ii) Smaller force, longer distance; same work."
    )
    hint = "<strong>Key idea:</strong> Longer path, smaller force, same work."
    return (
        question, solution, hint, 2,
        _fields((ratio, pick_raw), ("Times longer", "Correct statements"),
                ("number", "pick"), (None, pick_bank), (None, pick_count),
                hint="Divide, then two statements."),
    )


@_u31_variant("force_work_machines", "sms", "intermediate", "bike_order_then_lever_word")
def _force_work_machines_intermediate_sms_bike_order_then_lever_word():
    order_raw, order_bank = _order(
        (
            "The rider's hand applies an effort at the end of the brake lever",
            "The lever turns about its pivot",
            "A larger force is applied to the brake cable over a shorter distance",
        ),
        ("The lever creates energy for the brake",),
    )
    question = (
        "<p>A fictional bike-shop poster explains a brake lever.</p>"
        "<p>(i) Order how the lever works.</p>"
        "<p>(ii) Write the one-word name of the pivot in step 2 of (i).</p>"
    )
    solution = (
        "(i) <strong>effort at lever end → turns about pivot → larger force, shorter distance</strong><br>"
        "(ii) <strong>fulcrum</strong>"
    )
    hint = "<strong>Key idea:</strong> A lever trades distance for force about its fulcrum."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "fulcrum"), ("How it works", "Pivot"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_FW_SMS_D_CRANE_PACKS = (
    {"site": "fictional harbour crane test", "load": 2000, "height": 5, "effort": 500, "rope": 20},
    {"site": "fictional warehouse hoist test", "load": 1200, "height": 3, "effort": 300, "rope": 12},
    {"site": "fictional rescue-winch drill", "load": 800, "height": 4, "effort": 200, "rope": 16},
)


@_u31_variant("force_work_machines", "sms", "difficult", "crane_two_works_then_pick_then_verdict")
def _force_work_machines_difficult_sms_crane_two_works_then_pick_then_verdict():
    pack = random.choice(_FW_SMS_D_CRANE_PACKS)
    w_load = pack["load"] * pack["height"]
    w_rope = pack["effort"] * pack["rope"]
    pick_raw, pick_bank, pick_count = _pick(
        (
            "Work on the load equals work on the rope (ignoring friction)",
            "The machine trades a smaller force for a longer rope pull",
        ),
        (
            "The machine reduces the work needed",
            "The machine creates energy",
        ),
        2,
    )
    correct = "the winch changes the force needed, not the work; conservation holds"
    distractors = (
        "the winch is faulty because the works match",
        "the winch generates energy",
        "the operator should be ranked",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A {pack['site']} log: a {pack['load']} N load is raised {pack['height']} m "
        f"while the winch rope is pulled {pack['rope']} m with {pack['effort']} N.</p>"
        "<p>(i) Calculate the work done on the load.</p>"
        f"<p>(ii) The work on the rope is {pack['effort']} × {pack['rope']} = {w_rope} J. "
        "Comparing with (i), select the two correct statements.</p>"
        "<p>(iii) Given (ii), the engineer's conclusion is that</p>"
    )
    solution = (
        f"(i) {pack['load']} × {pack['height']} = <strong>{w_load}</strong> J<br>"
        "(ii) Equal work; force traded for distance.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Equal work both sides; a machine changes force, not energy."
    return (
        question, solution, hint, 3,
        _fields((w_load, pick_raw, letter), ("Work on load (J)", "Correct statements", "Conclusion"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Multiply, two statements, then the conclusion."),
    )


_FW_SMS_D_FRICTION_PACKS = (
    {"lab": "fictional materials lab", "ideal": 150, "measured": 180},
    {"lab": "fictional engineering class", "ideal": 200, "measured": 250},
    {"lab": "fictional design studio", "ideal": 120, "measured": 150},
)


@_u31_variant("force_work_machines", "sms", "difficult", "friction_extra_then_order_then_word")
def _force_work_machines_difficult_sms_friction_extra_then_order_then_word():
    pack = random.choice(_FW_SMS_D_FRICTION_PACKS)
    extra = pack["measured"] - pack["ideal"]
    order_raw, order_bank = _order(
        (
            "Friction acts along the ramp against the motion",
            "Extra force is needed over the same distance",
            "Extra work is done and ends up as thermal energy",
        ),
        ("The extra work is destroyed",),
    )
    question = (
        f"<p>A {pack['lab']} predicts {pack['ideal']} J of work to push a box up a "
        f"ramp with no friction, but measures {pack['measured']} J.</p>"
        "<p>(i) Calculate the extra work measured.</p>"
        "<p>(ii) Using the extra from (i), order the explanation.</p>"
        "<p>(iii) Write the one-word idea that says the extra work is not lost, only "
        "transferred: energy ______.</p>"
    )
    solution = (
        f"(i) {pack['measured']} − {pack['ideal']} = <strong>{extra}</strong> J<br>"
        "(ii) <strong>friction opposes → extra force → extra work becomes thermal</strong><br>"
        "(iii) <strong>conservation</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then friction turns extra work into thermal energy."
    return (
        question, solution, hint, 3,
        _fields((extra, order_raw, "conservation"), ("Extra work (J)", "Explanation", "Idea"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Subtract, three steps, then one word."),
    )


@_u31_variant("force_work_machines", "sms", "difficult", "advert_pick_then_test_mcq")
def _force_work_machines_difficult_sms_advert_pick_then_test_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        (
            "A machine cannot create energy",
            "Work out = work in at best; friction makes it less",
        ),
        (
            "A clever lever can output more work than is put in",
            "Bigger adverts mean better physics",
        ),
        2,
    )
    correct = "measure force and distance on both sides and compare the two works"
    distractors = (
        "accept the claim because the video is popular",
        "rank buyers by strength",
        "weigh the machine on a balance",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional advert claims a 'miracle lever' gives out more work than "
        "is put in.</p>"
        "<p>(i) Select the two physics statements that test the claim.</p>"
        "<p>(ii) Using the first statement from (i), a fair test is to</p>"
    )
    solution = (
        "(i) No energy created; work out ≤ work in.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Compare works, not adverts."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Fair test"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the test."),
    )


FORCE_WORK_MACHINES_MS_POOLS = {
    "foundational": [
        _force_work_machines_foundational_ms_work_then_unit_mcq,
        _force_work_machines_foundational_ms_lever_letter_then_role_order,
        _force_work_machines_foundational_ms_machine_pick_then_count,
    ],
    "intermediate": [
        _force_work_machines_intermediate_ms_ramp_work_then_trade_mcq,
        _force_work_machines_intermediate_ms_vector_order_then_work_word,
        _force_work_machines_intermediate_ms_pulley_pick_then_rope_count,
    ],
    "difficult": [
        _force_work_machines_difficult_ms_compare_work_then_mcq_then_word,
        _force_work_machines_difficult_ms_lever_order_then_pick_then_letter,
        _force_work_machines_difficult_ms_table_work_then_pattern_mcq_then_count,
    ],
}

FORCE_WORK_MACHINES_SMS_POOLS = {
    "foundational": [
        _force_work_machines_foundational_sms_site_work_then_machine_mcq,
        _force_work_machines_foundational_sms_seesaw_parts_then_pick,
        _force_work_machines_foundational_sms_crate_order_then_joule_word,
    ],
    "intermediate": [
        _force_work_machines_intermediate_sms_stage_pulley_work_then_mcq_then_word,
        _force_work_machines_intermediate_sms_ramp_ratio_then_pick,
        _force_work_machines_intermediate_sms_bike_order_then_lever_word,
    ],
    "difficult": [
        _force_work_machines_difficult_sms_crane_two_works_then_pick_then_verdict,
        _force_work_machines_difficult_sms_friction_extra_then_order_then_word,
        _force_work_machines_difficult_sms_advert_pick_then_test_mcq,
    ],
}


# ---------------------------------------------------------------------------
# energy — multi_step (F, I, D). SMS pools are the pilot's, in s3_machines.py.
# ---------------------------------------------------------------------------

_EN_MS_F_SPLIT_PACKS = (
    {"input": 100, "wasted": 40},
    {"input": 80, "wasted": 30},
    {"input": 120, "wasted": 70},
)


@_u31_variant("energy", "ms", "foundational", "useful_then_wasted_form_mcq")
def _energy_foundational_ms_useful_then_wasted_form_mcq():
    pack = random.choice(_EN_MS_F_SPLIT_PACKS)
    useful = pack["input"] - pack["wasted"]
    correct = "thermal energy, a less useful form"
    distractors = ("energy that has been destroyed", "a private energy diary", "a class ranking")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional textbook Sankey split: input {pack['input']} units, "
        f"wasted {pack['wasted']} units.</p>"
        "<p>(i) Calculate the useful output.</p>"
        "<p>(ii) The wasted part left over from (i) is usually</p>"
    )
    solution = (
        f"(i) {pack['input']} − {pack['wasted']} = <strong>{useful}</strong> units<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Useful = input − wasted; waste is usually thermal."
    return (
        question, solution, hint, 2,
        _fields((useful, letter), ("Useful output", "Wasted part is"),
                ("number", "mcq"), (None, options), hint="Subtract, then choose thermal."),
    )


@_u31_variant("energy", "ms", "foundational", "sankey_letter_then_order")
def _energy_foundational_ms_sankey_letter_then_order():
    diagram = str(sankey_bars(title="Fictional Sankey split"))
    order_raw, order_bank = _order(
        (
            "Energy enters as the input",
            "Part is transformed into the useful output",
            "The rest is transferred as wasted output",
        ),
        ("The wasted part vanishes",),
    )
    question = (
        diagram
        + "<p>A fictional Sankey sketch labels A input, B useful output, C wasted output.</p>"
        "<p>(i) Enter the letter of the input.</p>"
        "<p>(ii) Starting from the bar in (i), order the split.</p>"
    )
    solution = (
        "(i) <strong>A</strong><br>"
        "(ii) <strong>input → useful → wasted</strong>"
    )
    hint = "<strong>Key idea:</strong> A comes in; it splits into useful and wasted."
    return (
        question, solution, hint, 2,
        _fields(("A", order_raw), ("Input letter", "The split"),
                ("keyword", "order"), (None, order_bank), hint="Enter A, then order three steps."),
    )


@_u31_variant("energy", "ms", "foundational", "forms_pick_then_count")
def _energy_foundational_ms_forms_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Kinetic energy (motion)", "Chemical energy (food and fuels)", "Thermal energy"),
        ("A private energy diary", "A household ranking"),
        3,
    )
    question = (
        "<p>A fictional revision card lists energy forms named in this model.</p>"
        "<p>(i) Select the three energy forms.</p>"
        "<p>(ii) Enter how many forms you selected in (i).</p>"
    )
    solution = "(i) Kinetic; chemical; thermal.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Three named forms; no diary."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Energy forms", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_EN_MS_I_PCT_PACKS = (
    {"input": 200, "useful": 50},
    {"input": 500, "useful": 100},
    {"input": 250, "useful": 100},
)


@_u31_variant("energy", "ms", "intermediate", "useful_pct_then_conserve_mcq")
def _energy_intermediate_ms_useful_pct_then_conserve_mcq():
    pack = random.choice(_EN_MS_I_PCT_PACKS)
    pct = _pct(pack["useful"], pack["input"])
    correct = "still exists as a less useful form; energy is not destroyed"
    distractors = ("has been destroyed", "was never supplied", "is stored in a class ranking")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional appliance table: input {pack['input']} units, useful output "
        f"{pack['useful']} units.</p>"
        "<p>(i) Calculate the useful output as a whole-number percentage of the input.</p>"
        "<p>(ii) The remaining percentage after (i)</p>"
    )
    solution = (
        f"(i) {pack['useful']} ÷ {pack['input']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, then conservation."
    return (
        question, solution, hint, 2,
        _fields((pct, letter), ("Useful (%)", "The remainder"),
                ("number", "mcq"), (None, options), hint="Percentage, then conservation."),
    )


@_u31_variant("energy", "ms", "intermediate", "chain_order_then_transform_word")
def _energy_intermediate_ms_chain_order_then_transform_word():
    order_raw, order_bank = _order(
        (
            "Chemical energy in the fuel",
            "Thermal energy as the fuel burns",
            "Kinetic energy of the moving vehicle",
        ),
        ("Energy created by the engine",),
    )
    question = (
        "<p>A fictional engine diagram traces energy from fuel to motion.</p>"
        "<p>(i) Order the chain.</p>"
        "<p>(ii) Write the one-word term for each change of form in (i).</p>"
    )
    solution = (
        "(i) <strong>chemical → thermal → kinetic</strong><br>"
        "(ii) <strong>transformation</strong>"
    )
    hint = "<strong>Key idea:</strong> Store to store: each change is a transformation."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "transformation"), ("Chain", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three forms, then one word."),
    )


_EN_MS_I_TWO_PACKS = (
    {"a": (100, 20), "b": (100, 60)},
    {"a": (200, 50), "b": (200, 120)},
    {"a": (150, 30), "b": (150, 90)},
)


@_u31_variant("energy", "ms", "intermediate", "two_device_pick_then_gap")
def _energy_intermediate_ms_two_device_pick_then_gap():
    pack = random.choice(_EN_MS_I_TWO_PACKS)
    (ia, ua), (ib, ub) = pack["a"], pack["b"]
    gap = ub - ua
    pick_raw, pick_bank, pick_count = _pick(
        (
            "Device B gives more useful output from the same input",
            "Both devices obey conservation: input = useful + wasted",
        ),
        (
            "Device B creates energy",
            "Device A destroys energy",
        ),
        2,
    )
    question = (
        f"<p>A fictional public appliance table: device A input {ia}, useful {ua}; "
        f"device B input {ib}, useful {ub} (same units).</p>"
        "<p>(i) Select the two correct statements.</p>"
        "<p>(ii) Using the comparison from (i), calculate how many more useful units "
        "device B gives.</p>"
    )
    solution = (
        "(i) B more useful; both conserve.<br>"
        f"(ii) {ub} − {ua} = <strong>{gap}</strong>"
    )
    hint = "<strong>Key idea:</strong> Compare useful outputs; conservation for both."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, gap), ("Correct statements", "Extra useful units"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then subtract."),
    )


_EN_MS_D_RECON_PACKS = (
    {"useful": 70, "wasted": 30},
    {"useful": 45, "wasted": 15},
    {"useful": 120, "wasted": 80},
)


@_u31_variant("energy", "ms", "difficult", "reconstruct_input_then_pct_then_word")
def _energy_difficult_ms_reconstruct_input_then_pct_then_word():
    pack = random.choice(_EN_MS_D_RECON_PACKS)
    inp = pack["useful"] + pack["wasted"]
    pct = _pct(pack["useful"], inp)
    question = (
        f"<p>A fictional Sankey sketch has lost its input label: useful "
        f"{pack['useful']} units, wasted {pack['wasted']} units.</p>"
        "<p>(i) Reconstruct the input.</p>"
        "<p>(ii) Using the input from (i), calculate the useful share as a whole-number percentage.</p>"
        "<p>(iii) Write the one-word principle that let you do step (i).</p>"
    )
    solution = (
        f"(i) {pack['useful']} + {pack['wasted']} = <strong>{inp}</strong><br>"
        f"(ii) {pack['useful']} ÷ {inp} × 100 = <strong>{pct}%</strong><br>"
        "(iii) <strong>conservation</strong>"
    )
    hint = "<strong>Key idea:</strong> Input = useful + wasted, by conservation."
    return (
        question, solution, hint, 3,
        _fields((inp, pct, "conservation"), ("Input", "Useful (%)", "Principle"),
                ("number", "number", "keyword"), hint="Add, percentage, then one word."),
    )


@_u31_variant("energy", "ms", "difficult", "source_order_then_impact_pick")
def _energy_difficult_ms_source_order_then_impact_pick():
    order_raw, order_bank = _order(
        (
            "Identify the energy source (for example fuel, wind, sunlight)",
            "Trace the transformations to the useful output",
            "Compare public environmental impacts of the sources",
        ),
        ("Rank households by their bills",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        (
            "Impacts are compared with public data, not private bills",
            "Every source still obeys conservation",
        ),
        (
            "Some sources create energy from nothing",
            "The quiz should store a household diary",
        ),
        2,
    )
    question = (
        "<p>A fictional geography-and-science project compares energy sources.</p>"
        "<p>(i) Order the project method.</p>"
        "<p>(ii) Using step 3 of (i), select the two statements the project follows.</p>"
    )
    solution = (
        "(i) <strong>identify source → trace transformations → compare impacts</strong><br>"
        "(ii) Public data; conservation."
    )
    hint = "<strong>Key idea:</strong> Source, chain, impact — with public data."
    return (
        question, solution, hint, 2,
        _fields((order_raw, pick_raw), ("Method", "Statements"),
                ("order", "pick"), (order_bank, pick_bank), (None, pick_count),
                hint="Order three steps, then two statements."),
    )


@_u31_variant("energy", "ms", "difficult", "sankey_letter_then_mcq_then_count")
def _energy_difficult_ms_sankey_letter_then_mcq_then_count():
    diagram = str(sankey_bars(title="Fictional Sankey split"))
    correct = "thermal energy spread into the surroundings, still counted in the total"
    distractors = ("energy that no longer exists", "extra input from nowhere", "a stored bill")
    options, letter = _mcq(correct, distractors)
    question = (
        diagram
        + "<p>A fictional Sankey sketch labels A input, B useful, C wasted.</p>"
        "<p>(i) Enter the letter of the wasted output.</p>"
        "<p>(ii) The bar in (i) usually represents</p>"
        "<p>(iii) Enter how many output bars the sketch has.</p>"
    )
    solution = (
        "(i) <strong>C</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> C is wasted thermal; two outputs from one input."
    return (
        question, solution, hint, 3,
        _fields(("C", letter, 2), ("Wasted letter", "Represents", "Output bars"),
                ("keyword", "mcq", "number"), (None, options, None),
                hint="Enter C, choose, then enter 2."),
    )


ENERGY_MS_POOLS = {
    "foundational": [
        _energy_foundational_ms_useful_then_wasted_form_mcq,
        _energy_foundational_ms_sankey_letter_then_order,
        _energy_foundational_ms_forms_pick_then_count,
    ],
    "intermediate": [
        _energy_intermediate_ms_useful_pct_then_conserve_mcq,
        _energy_intermediate_ms_chain_order_then_transform_word,
        _energy_intermediate_ms_two_device_pick_then_gap,
    ],
    "difficult": [
        _energy_difficult_ms_reconstruct_input_then_pct_then_word,
        _energy_difficult_ms_source_order_then_impact_pick,
        _energy_difficult_ms_sankey_letter_then_mcq_then_count,
    ],
}


# ---------------------------------------------------------------------------
# electrostatics — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_ES_MS_F_RUB_PACKS = (
    {"items": ("a balloon", "a wool jumper"), "rubs": 10},
    {"items": ("a plastic rod", "a cloth"), "rubs": 8},
    {"items": ("a comb", "a piece of fleece"), "rubs": 12},
)


@_u31_variant("electrostatics", "ms", "foundational", "rub_count_then_kinds_mcq")
def _electrostatics_foundational_ms_rub_count_then_kinds_mcq():
    pack = random.choice(_ES_MS_F_RUB_PACKS)
    correct = "two kinds of charge, which attract or repel"
    distractors = ("one kind of charge only", "eighty kinds of charge", "a ranking of sparks")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional demo card: {pack['items'][0]} is rubbed on {pack['items'][1]} "
        f"{pack['rubs']} times and then attracts small paper pieces.</p>"
        "<p>(i) Enter the number of rubs on the card.</p>"
        "<p>(ii) The rubbing in (i) separates charge; this S3 model uses</p>"
    )
    solution = (
        f"(i) <strong>{pack['rubs']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Friction separates charge; two kinds exist."
    return (
        question, solution, hint, 2,
        _fields((pack["rubs"], letter), ("Rubs", "The model uses"),
                ("number", "mcq"), (None, options), hint="Count, then choose two kinds."),
    )


@_u31_variant("electrostatics", "ms", "foundational", "pair_letter_then_order")
def _electrostatics_foundational_ms_pair_letter_then_order():
    diagram = str(charge_pair(title="Fictional charge pair"))
    order_raw, order_bank = _order(
        (
            "Two objects are rubbed together",
            "Charge is separated onto the two objects",
            "The charged objects attract or repel each other",
        ),
        ("The class votes on which is charged",),
    )
    question = (
        diagram
        + "<p>A fictional worksheet shows two charged objects labelled A and B.</p>"
        "<p>(i) Enter the letter of the first object.</p>"
        "<p>(ii) Order how objects like the one in (i) become charged and interact.</p>"
    )
    solution = (
        "(i) <strong>A</strong><br>"
        "(ii) <strong>rub → separate charge → attract or repel</strong>"
    )
    hint = "<strong>Key idea:</strong> Rub, separate, interact."
    return (
        question, solution, hint, 2,
        _fields(("A", order_raw), ("First object", "How they charge and interact"),
                ("keyword", "order"), (None, order_bank), hint="Enter A, then order three steps."),
    )


@_u31_variant("electrostatics", "ms", "foundational", "interaction_pick_then_word")
def _electrostatics_foundational_ms_interaction_pick_then_word():
    pick_raw, pick_bank, pick_count = _pick(
        ("Opposite charges attract", "Like charges repel"),
        ("All charges attract", "Charge is a kind of food group"),
        2,
    )
    question = (
        "<p>A fictional physics poster lists rules for charges.</p>"
        "<p>(i) Select the two correct rules.</p>"
        "<p>(ii) Write the one-word name for the quantity the rules in (i) are about.</p>"
    )
    solution = "(i) Opposites attract; likes repel.<br>(ii) <strong>charge</strong>"
    hint = "<strong>Key idea:</strong> Two rules, one quantity: charge."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, "charge"), ("Rules", "Quantity"),
                ("pick", "keyword"), (pick_bank, None), (pick_count, None),
                hint="Two rules, then one word."),
    )


_ES_MS_I_PATH_PACKS = (
    {"materials": ("copper wire", "plastic ruler", "steel rod", "rubber band"), "conductors": 2},
    {"materials": ("aluminium foil", "glass rod", "iron nail", "wooden ruler"), "conductors": 2},
    {"materials": ("copper strip", "plastic comb", "nylon thread", "steel paperclip"), "conductors": 2},
)


@_u31_variant("electrostatics", "ms", "intermediate", "materials_count_then_ground_mcq")
def _electrostatics_intermediate_ms_materials_count_then_ground_mcq():
    pack = random.choice(_ES_MS_I_PATH_PACKS)
    correct = "a conductor connected to the ground gives charge a path to leave"
    distractors = (
        "an insulator lets charge flow away fastest",
        "grounding creates more charge",
        "grounding ranks the objects",
    )
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional lab list: " + ", ".join(pack["materials"]) + ".</p>"
        "<p>(i) Enter how many of the four are conductors.</p>"
        "<p>(ii) Using a conductor from (i), grounding a charged object works because</p>"
    )
    solution = (
        f"(i) <strong>{pack['conductors']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Metals conduct; a grounded conductor lets charge leave."
    return (
        question, solution, hint, 2,
        _fields((pack["conductors"], letter), ("Conductors", "Grounding works because"),
                ("number", "mcq"), (None, options), hint="Count metals, then choose the path idea."),
    )


@_u31_variant("electrostatics", "ms", "intermediate", "induction_order_then_word")
def _electrostatics_intermediate_ms_induction_order_then_word():
    order_raw, order_bank = _order(
        (
            "A charged rod is brought near a neutral object without touching",
            "Charge in the object rearranges: opposite charge moves nearer the rod",
            "The object is attracted to the rod",
        ),
        ("The rod transfers charge by contact",),
    )
    question = (
        "<p>A fictional demo: a charged rod is held near a small neutral foil ball.</p>"
        "<p>(i) Order what the S3 model says happens.</p>"
        "<p>(ii) Write the one-word name for the rearranging in step 2 of (i).</p>"
    )
    solution = (
        "(i) <strong>rod near → charge rearranges → attraction</strong><br>"
        "(ii) <strong>induction</strong>"
    )
    hint = "<strong>Key idea:</strong> No contact needed; charge rearranges by induction."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "induction"), ("What happens", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


@_u31_variant("electrostatics", "ms", "intermediate", "transfer_pick_then_count")
def _electrostatics_intermediate_ms_transfer_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Charging by friction", "Charging by contact", "Charging by induction"),
        ("Charging by voting", "Charging by ranking sparks"),
        3,
    )
    question = (
        "<p>A fictional revision card lists ways an object can become charged.</p>"
        "<p>(i) Select the three ways named in this model.</p>"
        "<p>(ii) Enter how many ways you selected in (i).</p>"
    )
    solution = "(i) Friction; contact; induction.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Three charging routes."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Ways to charge", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_ES_MS_D_SAFETY_PACKS = (
    {"place": "fictional fuel depot", "steps": ("connect the tanker to an earthing cable", "wait before opening the valve", "avoid nylon clothing near the nozzle")},
    {"place": "fictional grain silo", "steps": ("earth the loading pipe", "keep dust levels low", "use grounded conveyor belts")},
    {"place": "fictional electronics workshop", "steps": ("wear an earthed wrist strap", "use an anti-static mat", "keep components in conductive bags")},
)


@_u31_variant("electrostatics", "ms", "difficult", "safety_count_then_order_then_word")
def _electrostatics_difficult_ms_safety_count_then_order_then_word():
    pack = random.choice(_ES_MS_D_SAFETY_PACKS)
    order_raw, order_bank = _order(
        (
            "Friction between moving materials separates charge",
            "Charge builds up on an insulated object",
            "A sudden discharge could make a spark",
        ),
        ("The spark ranks the workers",),
    )
    question = (
        f"<p>A fictional safety sheet for a {pack['place']} lists: "
        + "; ".join(pack["steps"])
        + ".</p>"
        "<p>(i) Enter how many safety steps are listed.</p>"
        "<p>(ii) The steps in (i) prevent this chain — order it.</p>"
        "<p>(iii) Write the one-word term for connecting an object to the ground so "
        "charge can leave safely.</p>"
    )
    solution = (
        "(i) <strong>3</strong><br>"
        "(ii) <strong>friction separates → charge builds → spark risk</strong><br>"
        "(iii) <strong>grounding</strong>"
    )
    hint = "<strong>Key idea:</strong> Prevent build-up; give charge a safe path."
    return (
        question, solution, hint, 3,
        _fields((3, order_raw, "grounding"), ("Safety steps", "Chain prevented", "Term"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Enter 3, order three steps, then one word."),
    )


@_u31_variant("electrostatics", "ms", "difficult", "pair_letter_then_mcq_then_pick")
def _electrostatics_difficult_ms_pair_letter_then_mcq_then_pick():
    diagram = str(charge_pair(title="Fictional charge pair"))
    correct = "they repel, because like charges push apart"
    distractors = ("they attract, because like charges pull together", "nothing happens", "they swap letters")
    options, letter = _mcq(correct, distractors)
    pick_raw, pick_bank, pick_count = _pick(
        ("An insulator does not let charge flow easily", "Charge can be transferred by contact"),
        ("An insulator conducts best", "The quiz should rank whose spark is biggest"),
        2,
    )
    question = (
        diagram
        + "<p>A fictional worksheet: objects A and B carry the same kind of charge.</p>"
        "<p>(i) Enter the letter of the second object.</p>"
        "<p>(ii) When A and the object in (i) are brought close,</p>"
        "<p>(iii) Select the two true statements about how such charge behaves.</p>"
    )
    solution = (
        "(i) <strong>B</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) Insulators resist flow; contact transfers charge."
    )
    hint = "<strong>Key idea:</strong> Like charges repel; insulators hold charge."
    return (
        question, solution, hint, 3,
        _fields(("B", letter, pick_raw), ("Second object", "When close", "True statements"),
                ("keyword", "mcq", "pick"), (None, options, pick_bank), (None, None, pick_count),
                hint="Enter B, choose, then two statements."),
    )


_ES_MS_D_LIGHTNING_PACKS = (
    {"claim": "a lightning conductor attracts storms", "n": 3},
    {"claim": "rubber soles make a person immune to lightning", "n": 3},
    {"claim": "a car is safe in a storm because of its tyres", "n": 3},
)


@_u31_variant("electrostatics", "ms", "difficult", "myth_mcq_then_order_then_count")
def _electrostatics_difficult_ms_myth_mcq_then_order_then_count():
    pack = random.choice(_ES_MS_D_LIGHTNING_PACKS)
    correct = "a misconception; the science is that a conductor gives charge a safe path to ground"
    distractors = ("correct physics", "a reason to rank buildings", "proof charge is created")
    options, letter = _mcq(correct, distractors)
    order_raw, order_bank = _order(
        (
            "Charge separates within a storm cloud",
            "A conducting path forms to the ground",
            "The discharge follows the conductor safely to earth",
        ),
        ("The conductor pulls the storm closer",),
    )
    question = (
        f"<p>A fictional myth-busting page tests the claim that {pack['claim']}.</p>"
        "<p>(i) In the S3 model the claim is</p>"
        "<p>(ii) Using the safe-path idea from (i), order what a lightning conductor does.</p>"
        "<p>(iii) Enter how many steps the chain in (ii) has.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>charge separates → path forms → discharge to earth</strong><br>"
        f"(iii) <strong>{pack['n']}</strong>"
    )
    hint = "<strong>Key idea:</strong> Conductors route discharge safely; they do not attract storms."
    return (
        question, solution, hint, 3,
        _fields((letter, order_raw, pack["n"]), ("The claim is", "What a conductor does", "Steps"),
                ("mcq", "order", "number"), (options, order_bank, None),
                hint="Choose, order three steps, then enter 3."),
    )


# electrostatics — situational_multi_step (F, I, D)

_ES_SMS_F_FAIR_PACKS = (
    {"where": "fictional science fair", "balloons": 4},
    {"where": "fictional birthday party", "balloons": 6},
    {"where": "fictional school open day", "balloons": 3},
)


@_u31_variant("electrostatics", "sms", "foundational", "fair_balloons_then_why_mcq")
def _electrostatics_foundational_sms_fair_balloons_then_why_mcq():
    pack = random.choice(_ES_SMS_F_FAIR_PACKS)
    correct = "rubbing separated charge, and the charged balloon attracts the wall"
    distractors = ("the balloon is a magnet", "the wall ranks balloons", "glue on the balloon")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>At a {pack['where']}, {pack['balloons']} balloons are rubbed on hair and "
        "stick to a wall.</p>"
        "<p>(i) Enter the number of balloons.</p>"
        "<p>(ii) The balloons in (i) stick because</p>"
    )
    solution = (
        f"(i) <strong>{pack['balloons']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Friction charges the balloon; charge attracts."
    return (
        question, solution, hint, 2,
        _fields((pack["balloons"], letter), ("Balloons", "They stick because"),
                ("number", "mcq"), (None, options), hint="Count, then choose the charge idea."),
    )


@_u31_variant("electrostatics", "sms", "foundational", "jumper_pick_then_count")
def _electrostatics_foundational_sms_jumper_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Friction between the jumper and shirt separated charge", "Two kinds of charge attract or repel"),
        ("The jumper is a magnet", "Charge is a kind of food group"),
        2,
    )
    question = (
        "<p>In a fictional story, a character pulls off a wool jumper in the dark "
        "and sees tiny sparks.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Enter how many kinds of charge the model in (i) uses.</p>"
    )
    solution = "(i) Friction separates; two kinds.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Friction, two kinds of charge, small discharges."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Kinds of charge"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 2."),
    )


@_u31_variant("electrostatics", "sms", "foundational", "printer_order_then_word")
def _electrostatics_foundational_sms_printer_order_then_word():
    order_raw, order_bank = _order(
        (
            "A drum is given a pattern of charge",
            "Toner particles are attracted to the charged parts",
            "The toner is transferred to the paper",
        ),
        ("The printer ranks its users",),
    )
    question = (
        "<p>A fictional office guide explains how a photocopier uses charge.</p>"
        "<p>(i) Order the steps.</p>"
        "<p>(ii) Write the one-word force effect in step 2 of (i): opposite charges ______.</p>"
    )
    solution = (
        "(i) <strong>charge the drum → toner attracted → transfer to paper</strong><br>"
        "(ii) <strong>attract</strong>"
    )
    hint = "<strong>Key idea:</strong> Charge pattern, attraction, transfer."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "attract"), ("Steps", "Effect"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_ES_SMS_I_TANKER_PACKS = (
    {"site": "fictional airport refuelling bay", "who": "the crew", "cable": "an earthing cable"},
    {"site": "fictional petrol depot", "who": "the driver", "cable": "a grounding strap"},
    {"site": "fictional chemical plant", "who": "the operator", "cable": "an earth bond"},
)


@_u31_variant("electrostatics", "sms", "intermediate", "tanker_cable_then_why_mcq_then_word")
def _electrostatics_intermediate_sms_tanker_cable_then_why_mcq_then_word():
    pack = random.choice(_ES_SMS_I_TANKER_PACKS)
    correct = "fuel flow builds charge by friction, and the cable lets it leave to ground before a spark"
    distractors = ("the cable makes the fuel flow faster", "the cable ranks the crew", "the cable creates charge")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>At a {pack['site']}, {pack['who']} must attach {pack['cable']} before "
        "fuel flows.</p>"
        "<p>(i) Enter how many cables the rule requires.</p>"
        "<p>(ii) The cable in (i) is needed because</p>"
        "<p>(iii) Write the one-word charging process at the start of (ii).</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>friction</strong>"
    )
    hint = "<strong>Key idea:</strong> Friction charges; grounding drains it safely."
    return (
        question, solution, hint, 3,
        _fields((1, letter, "friction"), ("Cables required", "Needed because", "Process"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Enter 1, choose, then one word."),
    )


_ES_SMS_I_LAB_PACKS = (
    {"lab": "fictional school lab", "rod": "a charged plastic rod", "target": "a thin stream of water"},
    {"lab": "fictional science-show stage", "rod": "a charged balloon", "target": "an empty drinks can"},
    {"lab": "fictional physics club", "rod": "a charged comb", "target": "small paper pieces"},
)


@_u31_variant("electrostatics", "sms", "intermediate", "lab_pick_then_induction_order")
def _electrostatics_intermediate_sms_lab_pick_then_induction_order():
    pack = random.choice(_ES_SMS_I_LAB_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("The rod is charged but the target is neutral", "Charge in the target rearranges without contact"),
        ("The target must be a magnet", "The class should rank the sparks"),
        2,
    )
    order_raw, order_bank = _order(
        (
            f"{pack['rod'].capitalize()} is brought near {pack['target']}",
            "Charge in the target rearranges: opposite charge moves nearer",
            "The target is pulled towards the rod",
        ),
        ("The rod pushes the target away by contact",),
    )
    question = (
        f"<p>In a {pack['lab']}, {pack['rod']} bends {pack['target']} towards it "
        "without touching.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), order the induction model.</p>"
    )
    solution = (
        "(i) Charged rod, neutral target; rearrangement without contact.<br>"
        "(ii) <strong>rod near → charge rearranges → attraction</strong>"
    )
    hint = "<strong>Key idea:</strong> Induction attracts a neutral object."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "Induction model"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_ES_SMS_I_DUST_PACKS = (
    {"plant": "fictional power station", "before": 100, "after": 5},
    {"plant": "fictional cement works", "before": 80, "after": 4},
    {"plant": "fictional steel mill", "before": 60, "after": 3},
)


@_u31_variant("electrostatics", "sms", "intermediate", "precipitator_ratio_then_mcq")
def _electrostatics_intermediate_sms_precipitator_ratio_then_mcq():
    pack = random.choice(_ES_SMS_I_DUST_PACKS)
    ratio = pack["before"] // pack["after"]
    correct = "dust particles are charged and then attracted to oppositely charged plates"
    distractors = ("dust is burned by the plates", "the plates are magnets", "the plates rank the dust")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional report on a {pack['plant']}: dust in the chimney gas falls "
        f"from {pack['before']} units to {pack['after']} units after an electrostatic "
        "precipitator is fitted.</p>"
        "<p>(i) How many times lower is the dust level after fitting?</p>"
        "<p>(ii) The device behind the change in (i) works because</p>"
    )
    solution = (
        f"(i) {pack['before']} ÷ {pack['after']} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then charged dust attracted to plates."
    return (
        question, solution, hint, 2,
        _fields((ratio, letter), ("Times lower", "It works because"),
                ("number", "mcq"), (None, options), hint="Divide, then choose the attraction idea."),
    )


_ES_SMS_D_INCIDENT_PACKS = (
    {"site": "fictional flour mill", "sparks_before": 12, "sparks_after": 2, "fix": "earthing the conveyor"},
    {"site": "fictional paint-spray booth", "sparks_before": 9, "sparks_after": 1, "fix": "grounding the spray gun"},
    {"site": "fictional printing works", "sparks_before": 15, "sparks_after": 3, "fix": "fitting anti-static bars"},
)


@_u31_variant("electrostatics", "sms", "difficult", "incident_drop_then_caution_pick_then_verdict")
def _electrostatics_difficult_sms_incident_drop_then_caution_pick_then_verdict():
    pack = random.choice(_ES_SMS_D_INCIDENT_PACKS)
    drop = pack["sparks_before"] - pack["sparks_after"]
    pick_raw, pick_bank, pick_count = _pick(
        ("Other changes at the site could also have reduced sparks", "The counts are small, so chance plays a part"),
        ("The workers should be ranked by shocks", "Zero sparks proves charge no longer exists"),
        2,
    )
    correct = "grounding gave built-up charge a safe path, so fewer discharges — within the evidence limits"
    distractors = ("charge was destroyed by the fix", "the fix created charge", "the workers stopped moving")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional safety audit of a {pack['site']}: {pack['sparks_before']} "
        f"logged spark incidents a month before {pack['fix']}, {pack['sparks_after']} after.</p>"
        "<p>(i) Calculate the fall in monthly incidents.</p>"
        "<p>(ii) Using the fall from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair conclusion is that</p>"
    )
    solution = (
        f"(i) {pack['sparks_before']} − {pack['sparks_after']} = <strong>{drop}</strong><br>"
        "(ii) Other changes; small counts.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, cautions, then a grounded-path conclusion."
    return (
        question, solution, hint, 3,
        _fields((drop, pick_raw, letter), ("Fall", "Cautions", "Conclusion"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Subtract, two cautions, then the conclusion."),
    )


_ES_SMS_D_STORM_PACKS = (
    {"where": "fictional hilltop weather station", "rods": 2},
    {"where": "fictional cathedral spire", "rods": 1},
    {"where": "fictional wind farm", "rods": 3},
)


@_u31_variant("electrostatics", "sms", "difficult", "storm_rods_then_order_then_word")
def _electrostatics_difficult_sms_storm_rods_then_order_then_word():
    pack = random.choice(_ES_SMS_D_STORM_PACKS)
    order_raw, order_bank = _order(
        (
            "Charge separates inside the storm cloud",
            "The rod provides a conducting path from the top of the structure to the ground",
            "A discharge follows the rod safely to earth instead of the building",
        ),
        ("The rod attracts more storms",),
    )
    question = (
        f"<p>A {pack['where']} is fitted with {pack['rods']} lightning conductor(s).</p>"
        "<p>(i) Enter the number of conductors fitted.</p>"
        "<p>(ii) Order how each conductor in (i) protects the structure.</p>"
        "<p>(iii) Write the one-word property of the rod's metal that makes it work.</p>"
    )
    solution = (
        f"(i) <strong>{pack['rods']}</strong><br>"
        "(ii) <strong>charge separates → conducting path → safe discharge</strong><br>"
        "(iii) <strong>conductor</strong>"
    )
    hint = "<strong>Key idea:</strong> A conductor routes discharge to earth."
    return (
        question, solution, hint, 3,
        _fields((pack["rods"], order_raw, "conductor"), ("Conductors", "How it protects", "Property"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Count, order three steps, then one word."),
    )


@_u31_variant("electrostatics", "sms", "difficult", "workshop_pick_then_rule_mcq")
def _electrostatics_difficult_sms_workshop_pick_then_rule_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("A wrist strap connected to earth lets charge leave the technician safely", "Insulating packaging can hold charge that damages components"),
        ("The strap creates charge", "The workshop ranks technicians by shocks"),
        2,
    )
    correct = "keep the technician and the bench grounded so charge cannot build up"
    distractors = ("insulate everything so charge stays put", "ask which charge tastes sweeter", "use a magnet")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional electronics-repair manual explains anti-static precautions.</p>"
        "<p>(i) Select the two statements consistent with the manual.</p>"
        "<p>(ii) Using the first statement from (i), the manual's rule is to</p>"
    )
    solution = (
        "(i) Earthed strap drains charge; insulators hold charge.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Ground the person and bench; no build-up."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Rule"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the rule."),
    )


ELECTROSTATICS_MS_POOLS = {
    "foundational": [
        _electrostatics_foundational_ms_rub_count_then_kinds_mcq,
        _electrostatics_foundational_ms_pair_letter_then_order,
        _electrostatics_foundational_ms_interaction_pick_then_word,
    ],
    "intermediate": [
        _electrostatics_intermediate_ms_materials_count_then_ground_mcq,
        _electrostatics_intermediate_ms_induction_order_then_word,
        _electrostatics_intermediate_ms_transfer_pick_then_count,
    ],
    "difficult": [
        _electrostatics_difficult_ms_safety_count_then_order_then_word,
        _electrostatics_difficult_ms_pair_letter_then_mcq_then_pick,
        _electrostatics_difficult_ms_myth_mcq_then_order_then_count,
    ],
}

ELECTROSTATICS_SMS_POOLS = {
    "foundational": [
        _electrostatics_foundational_sms_fair_balloons_then_why_mcq,
        _electrostatics_foundational_sms_jumper_pick_then_count,
        _electrostatics_foundational_sms_printer_order_then_word,
    ],
    "intermediate": [
        _electrostatics_intermediate_sms_tanker_cable_then_why_mcq_then_word,
        _electrostatics_intermediate_sms_lab_pick_then_induction_order,
        _electrostatics_intermediate_sms_precipitator_ratio_then_mcq,
    ],
    "difficult": [
        _electrostatics_difficult_sms_incident_drop_then_caution_pick_then_verdict,
        _electrostatics_difficult_sms_storm_rods_then_order_then_word,
        _electrostatics_difficult_sms_workshop_pick_then_rule_mcq,
    ],
}


# ---------------------------------------------------------------------------
# electric_current — multi_step (F, I, D). Qualitative only: never V = IR.
# ---------------------------------------------------------------------------

_EC_MS_F_LAMP_PACKS = (
    {"lamps": 2, "cells": 1},
    {"lamps": 3, "cells": 2},
    {"lamps": 1, "cells": 1},
)


@_u31_variant("electric_current", "ms", "foundational", "series_count_then_switch_mcq")
def _electric_current_foundational_ms_series_count_then_switch_mcq():
    pack = random.choice(_EC_MS_F_LAMP_PACKS)
    total = pack["lamps"] + pack["cells"]
    correct = "all the lamps go out, because the single loop is broken"
    distractors = ("only one lamp goes out", "the lamps get brighter", "the cell becomes a magnet")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional circuit card: {pack['cells']} cell(s) and {pack['lamps']} lamp(s) "
        "in one series loop with a switch.</p>"
        "<p>(i) Enter the total number of cells and lamps.</p>"
        "<p>(ii) If the switch in the loop from (i) is opened,</p>"
    )
    solution = (
        f"(i) {pack['cells']} + {pack['lamps']} = <strong>{total}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Series means one path; break it anywhere and all stop."
    return (
        question, solution, hint, 2,
        _fields((total, letter), ("Cells + lamps", "Open switch"),
                ("number", "mcq"), (None, options), hint="Add, then choose the one-path idea."),
    )


@_u31_variant("electric_current", "ms", "foundational", "circuit_letter_then_order")
def _electric_current_foundational_ms_circuit_letter_then_order():
    diagram = str(circuit_boxes(title="Fictional circuit boxes"))
    order_raw, order_bank = _order(
        (
            "The switch is closed to complete the loop",
            "Current flows around the whole loop",
            "The lamp lights",
        ),
        ("The lamp lights before the loop is complete",),
    )
    question = (
        diagram
        + "<p>A fictional circuit sketch labels A cell, B lamp, C switch in a series loop.</p>"
        "<p>(i) Enter the letter of the switch.</p>"
        "<p>(ii) Starting with the part in (i), order what happens when it closes.</p>"
    )
    solution = (
        "(i) <strong>C</strong><br>"
        "(ii) <strong>switch closes → current flows → lamp lights</strong>"
    )
    hint = "<strong>Key idea:</strong> Complete the loop, then current, then light."
    return (
        question, solution, hint, 2,
        _fields(("C", order_raw), ("Switch letter", "What happens"),
                ("keyword", "order"), (None, order_bank), hint="Enter C, then order three steps."),
    )


@_u31_variant("electric_current", "ms", "foundational", "material_pick_then_count")
def _electric_current_foundational_ms_material_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Copper wire", "Steel paperclip"),
        ("Plastic ruler", "Rubber band"),
        2,
    )
    question = (
        "<p>A fictional lab tray holds four objects to test in a gap in a circuit.</p>"
        "<p>(i) Select the two that let the lamp light (conductors).</p>"
        "<p>(ii) Enter how many of the four are insulators, using your selection in (i).</p>"
    )
    solution = "(i) Copper; steel.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Metals conduct; plastic and rubber insulate."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Conductors", "Insulators"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


_EC_MS_I_PAR_PACKS = (
    {"branches": 2, "lamps": 2},
    {"branches": 3, "lamps": 3},
    {"branches": 2, "lamps": 4},
)


@_u31_variant("electric_current", "ms", "intermediate", "parallel_paths_then_fault_mcq")
def _electric_current_intermediate_ms_parallel_paths_then_fault_mcq():
    pack = random.choice(_EC_MS_I_PAR_PACKS)
    correct = "the other branches keep working, because each has its own path"
    distractors = ("every lamp goes out", "the cell stops working", "the circuit becomes series")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional circuit card: one cell feeding {pack['branches']} parallel "
        f"branches with {pack['lamps']} lamps in total.</p>"
        "<p>(i) Enter the number of current paths.</p>"
        "<p>(ii) If a lamp in one of the paths from (i) breaks,</p>"
    )
    solution = (
        f"(i) <strong>{pack['branches']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Parallel means more than one path."
    return (
        question, solution, hint, 2,
        _fields((pack["branches"], letter), ("Current paths", "If one lamp breaks"),
                ("number", "mcq"), (None, options), hint="Count branches, then choose."),
    )


@_u31_variant("electric_current", "ms", "intermediate", "effects_order_then_word")
def _electric_current_intermediate_ms_effects_order_then_word():
    order_raw, order_bank = _order(
        (
            "A complete loop lets current flow",
            "The current passes through the lamp filament",
            "The filament heats and glows",
        ),
        ("The lamp glows with no loop",),
    )
    question = (
        "<p>A fictional worksheet explains why a lamp lights.</p>"
        "<p>(i) Order the chain.</p>"
        "<p>(ii) Write the one-word effect of current in step 3 of (i) (a ______ effect).</p>"
    )
    solution = (
        "(i) <strong>loop → current through filament → heats and glows</strong><br>"
        "(ii) <strong>heating</strong>"
    )
    hint = "<strong>Key idea:</strong> Current has a heating effect in a filament."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "heating"), ("Chain", "Effect"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


@_u31_variant("electric_current", "ms", "intermediate", "meter_pick_then_count")
def _electric_current_intermediate_ms_meter_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("An ammeter is placed in the loop, in series", "A voltmeter is placed across a component, in parallel"),
        ("An ammeter is placed across the lamp", "A voltmeter measures the colour of the lamp"),
        2,
    )
    question = (
        "<p>A fictional lab card shows where meters go in a circuit.</p>"
        "<p>(i) Select the two correct placements.</p>"
        "<p>(ii) Enter how many kinds of meter you placed in (i).</p>"
    )
    solution = "(i) Ammeter in series; voltmeter in parallel.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Ammeter in the path; voltmeter across."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Placements", "Kinds of meter"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two placements, then enter 2."),
    )


_EC_MS_D_FAULT_PACKS = (
    {"lamps": 3, "dark": 3, "type": "series"},
    {"lamps": 4, "dark": 4, "type": "series"},
    {"lamps": 2, "dark": 2, "type": "series"},
)


@_u31_variant("electric_current", "ms", "difficult", "fault_count_then_diagnose_mcq_then_word")
def _electric_current_difficult_ms_fault_count_then_diagnose_mcq_then_word():
    pack = random.choice(_EC_MS_D_FAULT_PACKS)
    correct = "a series loop with one break; the whole path is open"
    distractors = ("a parallel circuit with one broken branch", "a circuit with too many cells", "a magnet in the loop")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional fault report: {pack['lamps']} lamps in one circuit, and "
        f"{pack['dark']} are dark after one lamp is removed.</p>"
        "<p>(i) Enter how many lamps stayed lit.</p>"
        "<p>(ii) The result in (i) means the circuit is</p>"
        "<p>(iii) Write the one-word circuit type in (ii).</p>"
    )
    solution = (
        f"(i) {pack['lamps']} − {pack['dark']} = <strong>0</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>series</strong>"
    )
    hint = "<strong>Key idea:</strong> All dark from one removal means one path."
    return (
        question, solution, hint, 3,
        _fields((0, letter, "series"), ("Lamps lit", "Circuit is", "Type"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


@_u31_variant("electric_current", "ms", "difficult", "topology_order_then_pick_then_letter")
def _electric_current_difficult_ms_topology_order_then_pick_then_letter():
    diagram = str(circuit_boxes(title="Fictional circuit boxes"))
    order_raw, order_bank = _order(
        (
            "Trace the loop from the cell around the circuit",
            "Count how many separate paths the current can take",
            "Classify it as series (one path) or parallel (more than one)",
        ),
        ("Measure the tyre pressure of the cell",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        ("Conventional current is a direction convention, distinct from electron flow", "A conductor lets current pass more easily than an insulator"),
        ("Current is used up by the first lamp", "The lamp stores current"),
        2,
    )
    question = (
        diagram
        + "<p>A fictional worksheet (A cell, B lamp, C switch) asks pupils to classify circuits.</p>"
        "<p>(i) Order the method.</p>"
        "<p>(ii) Select the two true statements about current in this model.</p>"
        "<p>(iii) Enter the letter of the component that lights.</p>"
    )
    solution = (
        "(i) <strong>trace → count paths → classify</strong><br>"
        "(ii) Direction convention; conductors pass current.<br>"
        "(iii) <strong>B</strong>"
    )
    hint = "<strong>Key idea:</strong> Trace, count, classify; B is the lamp."
    return (
        question, solution, hint, 3,
        _fields((order_raw, pick_raw, "B"), ("Method", "True statements", "Lamp letter"),
                ("order", "pick", "keyword"), (order_bank, pick_bank, None), (None, pick_count, None),
                hint="Order, two statements, then B."),
    )


_EC_MS_D_SAFE_PACKS = (
    {"rules": ("switch off before changing components", "use only the supplied low-voltage pack", "report any hot wire"), "n": 3},
    {"rules": ("keep water away from the bench", "never bypass a switch", "check leads for damage"), "n": 3},
    {"rules": ("use insulated leads", "do not connect a cell directly to itself", "follow the risk assessment"), "n": 3},
)


@_u31_variant("electric_current", "ms", "difficult", "safety_count_then_mcq_then_word")
def _electric_current_difficult_ms_safety_count_then_mcq_then_word():
    pack = random.choice(_EC_MS_D_SAFE_PACKS)
    correct = "the heating effect of current, which can make a wire dangerously hot"
    distractors = ("the magnetic effect ranking pupils", "current being stored in the lamp", "the cell being a magnet")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional classroom rule sheet lists: " + "; ".join(pack["rules"]) + ".</p>"
        "<p>(i) Enter how many rules are listed.</p>"
        "<p>(ii) The rules in (i) guard mainly against</p>"
        "<p>(iii) Write the one-word material property that makes a lead's outer coating safe to hold.</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>insulator</strong>"
    )
    hint = "<strong>Key idea:</strong> Heating effect is the hazard; insulators protect."
    return (
        question, solution, hint, 3,
        _fields((pack["n"], letter, "insulator"), ("Rules", "Guard against", "Property"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, choose, then one word."),
    )


# electric_current — situational_multi_step (F, I, D)

_EC_SMS_F_TORCH_PACKS = (
    {"who": "Alex", "thing": "a fictional torch", "cells": 2},
    {"who": "Sam", "thing": "a fictional bike lamp", "cells": 1},
    {"who": "Jordan", "thing": "a fictional camping lantern", "cells": 3},
)


@_u31_variant("electric_current", "sms", "foundational", "torch_cells_then_loop_mcq")
def _electric_current_foundational_sms_torch_cells_then_loop_mcq():
    pack = random.choice(_EC_SMS_F_TORCH_PACKS)
    correct = "the switch completes the loop so current can flow"
    distractors = ("the switch creates the cells", "the torch ranks its owners", "the bulb is a magnet")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['who']} (fictional) opens {pack['thing']} and finds {pack['cells']} cell(s), "
        "a bulb and a switch.</p>"
        "<p>(i) Enter the number of cells.</p>"
        "<p>(ii) With the cells from (i) in place, the bulb lights when pressed because</p>"
    )
    solution = (
        f"(i) <strong>{pack['cells']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> A closed switch completes the loop."
    return (
        question, solution, hint, 2,
        _fields((pack["cells"], letter), ("Cells", "Lights because"),
                ("number", "mcq"), (None, options), hint="Count, then choose the loop idea."),
    )


_EC_SMS_F_LIGHTS_PACKS = (
    {"where": "a fictional school hall", "strings": "fairy lights", "type": "series"},
    {"where": "a fictional shop window", "strings": "display lights", "type": "series"},
    {"where": "a fictional stage set", "strings": "a chain of bulbs", "type": "series"},
)


@_u31_variant("electric_current", "sms", "foundational", "lights_pick_then_paths")
def _electric_current_foundational_sms_lights_pick_then_paths():
    pack = random.choice(_EC_SMS_F_LIGHTS_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("The bulbs share one path, so one break stops them all", "It is a series circuit"),
        ("Each bulb has its own path", "The bulbs rank the room"),
        2,
    )
    question = (
        f"<p>In {pack['where']}, all the {pack['strings']} go dark when one bulb fails.</p>"
        "<p>(i) Select the two statements that explain this.</p>"
        "<p>(ii) Enter how many current paths the circuit in (i) has.</p>"
    )
    solution = "(i) One shared path; series.<br>(ii) <strong>1</strong>"
    hint = "<strong>Key idea:</strong> One path means one break stops everything."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 1), ("Explanation", "Current paths"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 1."),
    )


@_u31_variant("electric_current", "sms", "foundational", "doorbell_order_then_word")
def _electric_current_foundational_sms_doorbell_order_then_word():
    order_raw, order_bank = _order(
        (
            "The button (a switch) is pressed and completes the loop",
            "Current flows through the bell's coil",
            "The coil's magnetic effect makes the bell strike",
        ),
        ("The bell rings before the loop is complete",),
    )
    question = (
        "<p>A fictional electrician's poster explains a simple doorbell.</p>"
        "<p>(i) Order what happens.</p>"
        "<p>(ii) Write the one-word effect of current used in step 3 of (i).</p>"
    )
    solution = (
        "(i) <strong>switch closes → current in coil → magnetic effect strikes bell</strong><br>"
        "(ii) <strong>magnetic</strong>"
    )
    hint = "<strong>Key idea:</strong> Current in a coil has a magnetic effect."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "magnetic"), ("What happens", "Effect"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_EC_SMS_I_HOUSE_PACKS = (
    {"where": "a fictional model house", "rooms": 3},
    {"where": "a fictional dolls' house wiring kit", "rooms": 4},
    {"where": "a fictional stage-lighting model", "rooms": 2},
)


@_u31_variant("electric_current", "sms", "intermediate", "model_rooms_then_parallel_mcq_then_word")
def _electric_current_intermediate_sms_model_rooms_then_parallel_mcq_then_word():
    pack = random.choice(_EC_SMS_I_HOUSE_PACKS)
    correct = "each lamp is on its own path, so switching one off leaves the others lit"
    distractors = ("all lamps share one path", "the lamps are magnets", "the model ranks its builders")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional design-club project wires {pack['where']} so that each of "
        f"{pack['rooms']} room lamps can be switched independently.</p>"
        "<p>(i) Enter the number of independent lamps.</p>"
        "<p>(ii) To achieve (i) the club uses a parallel layout because</p>"
        "<p>(iii) Write the one-word name of that layout.</p>"
    )
    solution = (
        f"(i) <strong>{pack['rooms']}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>parallel</strong>"
    )
    hint = "<strong>Key idea:</strong> Parallel gives each lamp its own path."
    return (
        question, solution, hint, 3,
        _fields((pack["rooms"], letter, "parallel"), ("Independent lamps", "Because", "Layout"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Count, choose, then one word."),
    )


_EC_SMS_I_TEST_PACKS = (
    {"club": "fictional electronics club", "items": ("a copper coin", "a plastic spoon", "a graphite pencil lead", "a glass marble"), "conductors": 2},
    {"club": "fictional makerspace", "items": ("aluminium foil", "a cork", "a steel key", "a wooden peg"), "conductors": 2},
    {"club": "fictional science camp", "items": ("a brass screw", "a rubber eraser", "an iron nail", "a plastic bead"), "conductors": 2},
)


@_u31_variant("electric_current", "sms", "intermediate", "test_items_pick_then_order")
def _electric_current_intermediate_sms_test_items_pick_then_order():
    pack = random.choice(_EC_SMS_I_TEST_PACKS)
    conductors = [it for it in pack["items"] if any(w in it for w in ("copper", "graphite", "aluminium", "steel", "brass", "iron"))]
    insulators = [it for it in pack["items"] if it not in conductors]
    pick_raw, pick_bank, pick_count = _pick(tuple(conductors), tuple(insulators), 2)
    order_raw, order_bank = _order(
        (
            "Leave a gap in a working loop",
            "Bridge the gap with the test item",
            "Watch whether the lamp lights",
        ),
        ("Rank pupils by whose item was best",),
    )
    question = (
        f"<p>A {pack['club']} tests: " + ", ".join(pack["items"]) + ".</p>"
        "<p>(i) Select the two items that let the lamp light.</p>"
        "<p>(ii) Order the test method the club used to find (i).</p>"
    )
    solution = (
        f"(i) {conductors[0]}; {conductors[1]}.<br>"
        "(ii) <strong>gap → bridge → watch lamp</strong>"
    )
    hint = "<strong>Key idea:</strong> Metals and graphite conduct; test with a gap."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Conductors", "Test method"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two items, then order three steps."),
    )


_EC_SMS_I_EFFECT_PACKS = (
    {"device": "a fictional electric heater", "effect": "heating", "n": 3},
    {"device": "a fictional scrapyard electromagnet crane", "effect": "magnetic", "n": 3},
    {"device": "a fictional filament lamp", "effect": "heating", "n": 3},
)


@_u31_variant("electric_current", "sms", "intermediate", "device_effects_then_mcq")
def _electric_current_intermediate_sms_device_effects_then_mcq():
    pack = random.choice(_EC_SMS_I_EFFECT_PACKS)
    correct = f"the {pack['effect']} effect of current"
    other = "magnetic" if pack["effect"] == "heating" else "heating"
    distractors = (f"the {other} effect of current", "a stored-energy ranking", "a cooling effect that freezes the wire")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional catalogue lists {pack['n']} effects of current: heating, "
        f"lighting and magnetic. It describes {pack['device']}.</p>"
        "<p>(i) Enter the number of effects listed.</p>"
        f"<p>(ii) Of the effects in (i), {pack['device']} mainly uses</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Match the device to its main effect."
    return (
        question, solution, hint, 2,
        _fields((pack["n"], letter), ("Effects listed", "Mainly uses"),
                ("number", "mcq"), (None, options), hint="Count, then match the effect."),
    )


_EC_SMS_D_FAULT_PACKS = (
    {"where": "fictional theatre", "lamps": 12, "dark": 12, "fix": "series to parallel"},
    {"where": "fictional greenhouse", "lamps": 8, "dark": 8, "fix": "series to parallel"},
    {"where": "fictional museum case", "lamps": 6, "dark": 6, "fix": "series to parallel"},
)


@_u31_variant("electric_current", "sms", "difficult", "rewire_count_then_pick_then_verdict")
def _electric_current_difficult_sms_rewire_count_then_pick_then_verdict():
    pack = random.choice(_EC_SMS_D_FAULT_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("In series, one failed lamp opens the only path", "In parallel, each lamp keeps its own path"),
        ("Parallel wiring stores current", "The lamps should be ranked"),
        2,
    )
    correct = "rewire in parallel so a single failure no longer darkens the whole set"
    distractors = ("add more lamps in series", "remove all the switches", "replace the lamps with magnets")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional {pack['where']} technician logs that all {pack['lamps']} display "
        "lamps went dark when one failed.</p>"
        "<p>(i) Enter how many lamps stayed lit.</p>"
        "<p>(ii) Using the result from (i), select the two statements that explain the fix.</p>"
        "<p>(iii) Given (ii), the technician's recommendation is to</p>"
    )
    solution = (
        f"(i) {pack['lamps']} − {pack['dark']} = <strong>0</strong><br>"
        "(ii) Series opens the path; parallel keeps paths.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Zero lit means series; parallel fixes it."
    return (
        question, solution, hint, 3,
        _fields((0, pick_raw, letter), ("Lamps lit", "Explanation", "Recommendation"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Enter 0, two statements, then the recommendation."),
    )


_EC_SMS_D_METER_PACKS = (
    {"lab": "fictional university lab", "readings": ("A1 0.2", "A2 0.2", "A3 0.2"), "same": 1},
    {"lab": "fictional college workshop", "readings": ("A1 0.5", "A2 0.5", "A3 0.5"), "same": 1},
    {"lab": "fictional teacher-training demo", "readings": ("A1 0.3", "A2 0.3", "A3 0.3"), "same": 1},
)


@_u31_variant("electric_current", "sms", "difficult", "ammeters_same_then_order_then_word")
def _electric_current_difficult_sms_ammeters_same_then_order_then_word():
    pack = random.choice(_EC_SMS_D_METER_PACKS)
    order_raw, order_bank = _order(
        (
            "Three ammeters are placed in series at different points of one loop",
            "Each reads the same value",
            "So current is the same everywhere in a series loop",
        ),
        ("So current is used up by each lamp",),
    )
    question = (
        f"<p>A {pack['lab']} places three ammeters around one series loop; readings "
        f"(in amperes): {', '.join(pack['readings'])}.</p>"
        "<p>(i) Enter 1 if all readings are equal, otherwise 0.</p>"
        "<p>(ii) Using the result from (i), order the conclusion.</p>"
        "<p>(iii) Write the one-word name of the meter placed in the loop.</p>"
    )
    solution = (
        f"(i) <strong>{pack['same']}</strong><br>"
        "(ii) <strong>ammeters in series → same readings → current same everywhere</strong><br>"
        "(iii) <strong>ammeter</strong>"
    )
    hint = "<strong>Key idea:</strong> Equal readings show current is not used up."
    return (
        question, solution, hint, 3,
        _fields((pack["same"], order_raw, "ammeter"), ("All equal", "Conclusion", "Meter"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="1 or 0, order three steps, then one word."),
    )


@_u31_variant("electric_current", "sms", "difficult", "safety_pick_then_rule_mcq")
def _electric_current_difficult_sms_safety_pick_then_rule_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("Classroom circuits use low-voltage packs under the teacher's risk assessment", "A hot wire shows the heating effect and is reported, not touched"),
        ("The quiz should inspect whose home wiring it is", "Insulators conduct best"),
        2,
    )
    correct = "switch off, report it, and let the teacher check the circuit"
    distractors = ("touch the wire to see how hot it is", "photograph home sockets for the app", "add more cells")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional lab-safety video shows a pupil noticing a warm lead during a "
        "circuit practical.</p>"
        "<p>(i) Select the two statements consistent with the video.</p>"
        "<p>(ii) Using the second statement from (i), the correct action is to</p>"
    )
    solution = (
        "(i) Low-voltage under risk assessment; report hot wires.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Heating effect is a hazard; switch off and report."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Action"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the action."),
    )


ELECTRIC_CURRENT_MS_POOLS = {
    "foundational": [
        _electric_current_foundational_ms_series_count_then_switch_mcq,
        _electric_current_foundational_ms_circuit_letter_then_order,
        _electric_current_foundational_ms_material_pick_then_count,
    ],
    "intermediate": [
        _electric_current_intermediate_ms_parallel_paths_then_fault_mcq,
        _electric_current_intermediate_ms_effects_order_then_word,
        _electric_current_intermediate_ms_meter_pick_then_count,
    ],
    "difficult": [
        _electric_current_difficult_ms_fault_count_then_diagnose_mcq_then_word,
        _electric_current_difficult_ms_topology_order_then_pick_then_letter,
        _electric_current_difficult_ms_safety_count_then_mcq_then_word,
    ],
}

ELECTRIC_CURRENT_SMS_POOLS = {
    "foundational": [
        _electric_current_foundational_sms_torch_cells_then_loop_mcq,
        _electric_current_foundational_sms_lights_pick_then_paths,
        _electric_current_foundational_sms_doorbell_order_then_word,
    ],
    "intermediate": [
        _electric_current_intermediate_sms_model_rooms_then_parallel_mcq_then_word,
        _electric_current_intermediate_sms_test_items_pick_then_order,
        _electric_current_intermediate_sms_device_effects_then_mcq,
    ],
    "difficult": [
        _electric_current_difficult_sms_rewire_count_then_pick_then_verdict,
        _electric_current_difficult_sms_ammeters_same_then_order_then_word,
        _electric_current_difficult_sms_safety_pick_then_rule_mcq,
    ],
}


# ---------------------------------------------------------------------------
# magnetism — multi_step (I, D); foundational MS stays — (matrix)
# ---------------------------------------------------------------------------

_MG_MS_I_SORT_PACKS = (
    {"items": ("iron nail", "copper coin", "steel paperclip", "aluminium can"), "magnetic": 2},
    {"items": ("steel screw", "brass key", "iron filings", "plastic ruler"), "magnetic": 2},
    {"items": ("nickel coin", "glass marble", "iron bolt", "wooden peg"), "magnetic": 2},
)


@_u31_variant("magnetism", "ms", "intermediate", "sort_count_then_pole_mcq")
def _magnetism_intermediate_ms_sort_count_then_pole_mcq():
    pack = random.choice(_MG_MS_I_SORT_PACKS)
    correct = "attract, because unlike poles attract"
    distractors = ("repel, because unlike poles repel", "do nothing", "rank the magnets")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional lab tray: " + ", ".join(pack["items"]) + ".</p>"
        "<p>(i) Enter how many of the four are magnetic materials in this S3 model.</p>"
        "<p>(ii) If two bar magnets are placed north to south near the tray from (i), they</p>"
    )
    solution = (
        f"(i) <strong>{pack['magnetic']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Iron, steel, nickel are magnetic; unlike poles attract."
    return (
        question, solution, hint, 2,
        _fields((pack["magnetic"], letter), ("Magnetic materials", "North to south"),
                ("number", "mcq"), (None, options), hint="Count, then choose attract."),
    )


@_u31_variant("magnetism", "ms", "intermediate", "electromagnet_order_then_word")
def _magnetism_intermediate_ms_electromagnet_order_then_word():
    order_raw, order_bank = _order(
        (
            "A coil of wire is wound around an iron core",
            "Current flows through the coil",
            "The core becomes a magnet that can be switched off",
        ),
        ("The coil creates energy from nothing",),
    )
    question = (
        "<p>A fictional worksheet explains a current-made magnet.</p>"
        "<p>(i) Order the steps.</p>"
        "<p>(ii) Write the one-word name of the device made in step 3 of (i).</p>"
    )
    solution = (
        "(i) <strong>coil on core → current flows → switchable magnet</strong><br>"
        "(ii) <strong>electromagnet</strong>"
    )
    hint = "<strong>Key idea:</strong> Coil, current, switchable magnet."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "electromagnet"), ("Steps", "Device"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


@_u31_variant("magnetism", "ms", "intermediate", "compass_pick_then_poles_count")
def _magnetism_intermediate_ms_compass_pick_then_poles_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Earth can be modelled as having a magnetic field", "A compass needle lines up with that field"),
        ("A compass points to the nearest magnet shop", "The quiz should rank whose magnet is strongest"),
        2,
    )
    question = (
        "<p>A fictional orienteering guide explains how a compass works.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Enter how many poles the compass needle in (i) has.</p>"
    )
    solution = "(i) Earth's field; needle aligns.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> A needle is a small magnet with two poles."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Needle poles"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 2."),
    )


_MG_MS_D_TURNS_PACKS = (
    {"turns": (10, 20, 40), "clips": (2, 4, 8)},
    {"turns": (5, 10, 20), "clips": (1, 2, 4)},
    {"turns": (15, 30, 60), "clips": (3, 6, 12)},
)


@_u31_variant("magnetism", "ms", "difficult", "turns_pattern_then_mcq_then_word")
def _magnetism_difficult_ms_turns_pattern_then_mcq_then_word():
    pack = random.choice(_MG_MS_D_TURNS_PACKS)
    t, c = pack["turns"], pack["clips"]
    ratio = c[-1] // c[0]
    correct = "more turns give a stronger electromagnet, in this simple model"
    distractors = ("more turns weaken the magnet", "turns have no effect", "the paperclips are magnets")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional data table for an electromagnet: "
        + ", ".join(f"{tt} turns lifts {cc} paperclips" for tt, cc in zip(t, c))
        + ".</p>"
        f"<p>(i) How many times more clips does {t[-1]} turns lift than {t[0]} turns?</p>"
        "<p>(ii) The pattern behind (i) shows that</p>"
        "<p>(iii) Write the one-word material of the core that makes a good electromagnet.</p>"
    )
    solution = (
        f"(i) {c[-1]} ÷ {c[0]} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>iron</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then more turns means stronger; iron core."
    return (
        question, solution, hint, 3,
        _fields((ratio, letter, "iron"), ("Times more clips", "Pattern shows", "Core material"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Divide, choose, then one word."),
    )


@_u31_variant("magnetism", "ms", "difficult", "poles_letter_then_order_then_pick")
def _magnetism_difficult_ms_poles_letter_then_order_then_pick():
    diagram = str(magnet_poles(title="Fictional pole sketch"))
    order_raw, order_bank = _order(
        (
            "Sprinkle iron filings on paper over the magnet",
            "The filings line up along the field",
            "The pattern shows the field region between the poles",
        ),
        ("The filings rank the magnets",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        ("Magnets have poles that attract or repel", "A field region is where a magnetic effect can be shown"),
        ("All materials are magnetic", "The quiz should rank whose magnet is strongest"),
        2,
    )
    question = (
        diagram
        + "<p>A fictional sketch labels A north, B south, C the field region between them.</p>"
        "<p>(i) Enter the letter of the field region.</p>"
        "<p>(ii) Order how a filings demo reveals the region in (i).</p>"
        "<p>(iii) Select the two true statements.</p>"
    )
    solution = (
        "(i) <strong>C</strong><br>"
        "(ii) <strong>sprinkle → line up → pattern shows region</strong><br>"
        "(iii) Poles attract/repel; field region."
    )
    hint = "<strong>Key idea:</strong> C is the field; filings map it."
    return (
        question, solution, hint, 3,
        _fields(("C", order_raw, pick_raw), ("Field letter", "Filings demo", "True statements"),
                ("keyword", "order", "pick"), (None, order_bank, pick_bank), (None, None, pick_count),
                hint="Enter C, order, then two statements."),
    )


_MG_MS_D_ANIMAL_PACKS = (
    {"animal": "a migrating bird", "cue": "Earth's magnetic field"},
    {"animal": "a sea turtle", "cue": "Earth's magnetic field"},
    {"animal": "a magnetotactic bacterium", "cue": "Earth's magnetic field"},
)


@_u31_variant("magnetism", "ms", "difficult", "animal_mcq_then_count_then_word")
def _magnetism_difficult_ms_animal_mcq_then_count_then_word():
    pack = random.choice(_MG_MS_D_ANIMAL_PACKS)
    correct = "a public animal example of sensing a magnetic field, not a pupil superpower"
    distractors = ("proof the animal is a magnet", "a reason to rank pupils", "a spell")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional textbook describes {pack['animal']} using {pack['cue']} to navigate.</p>"
        "<p>(i) In this lesson the example is</p>"
        "<p>(ii) Enter how many poles Earth's field is modelled with.</p>"
        "<p>(iii) Write the one-word human instrument that uses the same cue.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>2</strong><br>"
        "(iii) <strong>compass</strong>"
    )
    hint = "<strong>Key idea:</strong> Public example, two poles, compass."
    return (
        question, solution, hint, 3,
        _fields((letter, 2, "compass"), ("The example is", "Poles", "Instrument"),
                ("mcq", "number", "keyword"), (options, None, None),
                hint="Choose, enter 2, then one word."),
    )


# magnetism — situational_multi_step (F, I, D)

_MG_SMS_F_FRIDGE_PACKS = (
    {"where": "a fictional café noticeboard", "magnets": 5},
    {"where": "a fictional classroom whiteboard", "magnets": 8},
    {"where": "a fictional workshop tool wall", "magnets": 6},
)


@_u31_variant("magnetism", "sms", "foundational", "board_magnets_then_why_mcq")
def _magnetism_foundational_sms_board_magnets_then_why_mcq():
    pack = random.choice(_MG_SMS_F_FRIDGE_PACKS)
    correct = "the board contains a magnetic material such as steel"
    distractors = ("the board is charged by friction", "the magnets are glued", "the board ranks the notes")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>On {pack['where']}, {pack['magnets']} magnets hold up notices.</p>"
        "<p>(i) Enter the number of magnets.</p>"
        "<p>(ii) The magnets in (i) stick because</p>"
    )
    solution = (
        f"(i) <strong>{pack['magnets']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Magnets attract magnetic materials."
    return (
        question, solution, hint, 2,
        _fields((pack["magnets"], letter), ("Magnets", "They stick because"),
                ("number", "mcq"), (None, options), hint="Count, then choose the material idea."),
    )


@_u31_variant("magnetism", "sms", "foundational", "scrapyard_pick_then_count")
def _magnetism_foundational_sms_scrapyard_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("The crane uses an electromagnet that switches off to drop the load", "Iron and steel are attracted; aluminium is not"),
        ("The crane uses a permanent magnet that cannot release", "The crane ranks the cars"),
        2,
    )
    question = (
        "<p>A fictional scrapyard video shows a crane lifting car bodies and dropping "
        "them on command.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Enter how many of the two named metals (iron, aluminium) the crane can lift.</p>"
    )
    solution = "(i) Switchable electromagnet; iron yes, aluminium no.<br>(ii) <strong>1</strong>"
    hint = "<strong>Key idea:</strong> Switchable magnet; only magnetic metals lift."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 1), ("Statements", "Metals liftable"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 1."),
    )


@_u31_variant("magnetism", "sms", "foundational", "hike_order_then_word")
def _magnetism_foundational_sms_hike_order_then_word():
    order_raw, order_bank = _order(
        (
            "The compass needle lines up with Earth's magnetic field",
            "The hikers read which way is north",
            "They turn the map to match",
        ),
        ("The needle points to the nearest magnet shop",),
    )
    question = (
        "<p>A fictional hiking club uses a compass in fog.</p>"
        "<p>(i) Order what happens.</p>"
        "<p>(ii) Write the one-word name for the region around Earth where the "
        "needle in step 1 feels a magnetic effect.</p>"
    )
    solution = (
        "(i) <strong>needle aligns → read north → turn map</strong><br>"
        "(ii) <strong>field</strong>"
    )
    hint = "<strong>Key idea:</strong> Needle, north, map — in Earth's field."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "field"), ("What happens", "Region"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_MG_SMS_I_RECYCLE_PACKS = (
    {"plant": "fictional recycling plant", "items": 200, "steel": 120},
    {"plant": "fictional can-sorting line", "items": 300, "steel": 180},
    {"plant": "fictional scrap-metal yard", "items": 150, "steel": 90},
)


@_u31_variant("magnetism", "sms", "intermediate", "recycle_pct_then_mcq_then_word")
def _magnetism_intermediate_sms_recycle_pct_then_mcq_then_word():
    pack = random.choice(_MG_SMS_I_RECYCLE_PACKS)
    pct = _pct(pack["steel"], pack["items"])
    correct = "steel is magnetic and is pulled out; aluminium is not and passes by"
    distractors = ("aluminium is more magnetic than steel", "the magnet ranks the cans", "the cans are charged")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A {pack['plant']} passes {pack['items']} cans under a magnet; "
        f"{pack['steel']} are lifted off the belt.</p>"
        "<p>(i) Calculate the percentage lifted (whole number).</p>"
        "<p>(ii) The cans lifted in (i) were separated because</p>"
        "<p>(iii) Write the one-word switchable magnet type such a plant uses.</p>"
    )
    solution = (
        f"(i) {pack['steel']} ÷ {pack['items']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>electromagnet</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, then magnetic sorting with an electromagnet."
    return (
        question, solution, hint, 3,
        _fields((pct, letter, "electromagnet"), ("Lifted (%)", "Because", "Magnet type"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Percentage, choose, then one word."),
    )


_MG_SMS_I_DOOR_PACKS = (
    {"where": "a fictional fire door", "device": "an electromagnetic door holder"},
    {"where": "a fictional bank vault", "device": "an electromagnetic lock"},
    {"where": "a fictional lift shaft", "device": "an electromagnetic brake"},
)


@_u31_variant("magnetism", "sms", "intermediate", "door_pick_then_order")
def _magnetism_intermediate_sms_door_pick_then_order():
    pack = random.choice(_MG_SMS_I_DOOR_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("An electromagnet is a current-made magnet that can be switched", "Switching the current off releases the magnetic effect"),
        ("A permanent magnet can be switched off with a button", "The device ranks the building's users"),
        2,
    )
    order_raw, order_bank = _order(
        (
            "Current flows through the coil",
            "The coil's core becomes magnetic and holds a steel plate",
            "The current is cut and the plate is released",
        ),
        ("The plate stays held with no current",),
    )
    question = (
        f"<p>A fictional building manual describes {pack['device']} on {pack['where']}.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the switching idea from (i), order how the device works.</p>"
    )
    solution = (
        "(i) Current-made, switchable; off releases.<br>"
        "(ii) <strong>current on → holds plate → current off releases</strong>"
    )
    hint = "<strong>Key idea:</strong> Electromagnets switch on and off with current."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "How it works"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_MG_SMS_I_SHIP_PACKS = (
    {"crew": "fictional ferry crew", "readings": 4},
    {"crew": "fictional expedition team", "readings": 6},
    {"crew": "fictional sailing-school class", "readings": 3},
)


@_u31_variant("magnetism", "sms", "intermediate", "ship_readings_then_reason_mcq")
def _magnetism_intermediate_sms_ship_readings_then_reason_mcq():
    pack = random.choice(_MG_SMS_I_SHIP_PACKS)
    correct = "the steel hull and electrical equipment have their own magnetic effects that disturb the needle"
    distractors = ("the compass is charged by friction", "Earth has no field at sea", "the crew should be ranked")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A {pack['crew']} takes {pack['readings']} compass readings and finds "
        "them slightly wrong near the ship's engine.</p>"
        "<p>(i) Enter the number of readings taken.</p>"
        "<p>(ii) The readings in (i) are disturbed because</p>"
    )
    solution = (
        f"(i) <strong>{pack['readings']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Nearby magnetic materials and currents disturb a compass."
    return (
        question, solution, hint, 2,
        _fields((pack["readings"], letter), ("Readings", "Disturbed because"),
                ("number", "mcq"), (None, options), hint="Count, then choose the disturbance idea."),
    )


_MG_SMS_D_TRIAL_PACKS = (
    {"lab": "fictional engineering lab", "turns": (20, 40), "clips": (6, 12)},
    {"lab": "fictional design-tech workshop", "turns": (25, 50), "clips": (5, 10)},
    {"lab": "fictional university outreach lab", "turns": (30, 60), "clips": (9, 18)},
)


@_u31_variant("magnetism", "sms", "difficult", "trial_ratio_then_caution_pick_then_verdict")
def _magnetism_difficult_sms_trial_ratio_then_caution_pick_then_verdict():
    pack = random.choice(_MG_SMS_D_TRIAL_PACKS)
    ratio = pack["clips"][1] // pack["clips"][0]
    pick_raw, pick_bank, pick_count = _pick(
        ("Only two trials were run, so the pattern needs more points", "The same core and current should be kept for a fair test"),
        ("The result ranks the students", "Paperclips are permanent magnets"),
        2,
    )
    correct = "more turns gave a stronger electromagnet in this trial, within its limits"
    distractors = ("turns do not matter", "the core should be plastic", "the coil creates energy")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A {pack['lab']} log: {pack['turns'][0]} turns lift {pack['clips'][0]} clips; "
        f"{pack['turns'][1]} turns lift {pack['clips'][1]} clips.</p>"
        "<p>(i) How many times more clips did the larger coil lift?</p>"
        "<p>(ii) Using the comparison from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['clips'][1]} ÷ {pack['clips'][0]} = <strong>{ratio}</strong><br>"
        "(ii) Few trials; control core and current.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Ratio, cautions, then a fair verdict."
    return (
        question, solution, hint, 3,
        _fields((ratio, pick_raw, letter), ("Times more clips", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Ratio, two cautions, then the verdict."),
    )


_MG_SMS_D_TRAIN_PACKS = (
    {"line": "fictional maglev test track", "magnets": 2},
    {"line": "fictional model maglev kit", "magnets": 2},
    {"line": "fictional airport shuttle demo", "magnets": 2},
)


@_u31_variant("magnetism", "sms", "difficult", "maglev_order_then_word_then_count")
def _magnetism_difficult_sms_maglev_order_then_word_then_count():
    pack = random.choice(_MG_SMS_D_TRAIN_PACKS)
    order_raw, order_bank = _order(
        (
            "Like poles on the track and train face each other",
            "They repel, lifting the train slightly",
            "Switching electromagnets along the track pull the train forward",
        ),
        ("Unlike poles lift the train by repelling",),
    )
    question = (
        f"<p>A fictional exhibit explains a {pack['line']}.</p>"
        "<p>(i) Order how the train floats and moves.</p>"
        "<p>(ii) Write the one-word interaction of like poles in step 2 of (i).</p>"
        "<p>(iii) Enter how many poles every magnet in the system has.</p>"
    )
    solution = (
        "(i) <strong>like poles face → repel and lift → switching magnets pull</strong><br>"
        "(ii) <strong>repel</strong><br>"
        f"(iii) <strong>{pack['magnets']}</strong>"
    )
    hint = "<strong>Key idea:</strong> Like poles repel to lift; switched magnets pull."
    return (
        question, solution, hint, 3,
        _fields((order_raw, "repel", pack["magnets"]), ("How it works", "Interaction", "Poles per magnet"),
                ("order", "keyword", "number"), (order_bank, None, None),
                hint="Order three steps, one word, then 2."),
    )


@_u31_variant("magnetism", "sms", "difficult", "myth_pick_then_test_mcq")
def _magnetism_difficult_sms_myth_pick_then_test_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("Claims about magnets must be tested with a controlled experiment", "A magnetic effect can be shown with iron filings or a compass"),
        ("A stylish advert proves a magnet works", "Magnets rank their owners"),
        2,
    )
    correct = "compare the bracelet with a non-magnetic copy in a blind test"
    distractors = ("accept the advert", "rank buyers", "ask who feels magnetic")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional consumer show tests an advert claiming a 'magnetic bracelet' "
        "has special effects.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the first statement from (i), a fair test would</p>"
    )
    solution = (
        "(i) Controlled test; effect shown with filings or compass.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Test claims; show effects with filings or a compass."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Fair test"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the test."),
    )


MAGNETISM_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _magnetism_intermediate_ms_sort_count_then_pole_mcq,
        _magnetism_intermediate_ms_electromagnet_order_then_word,
        _magnetism_intermediate_ms_compass_pick_then_poles_count,
    ],
    "difficult": [
        _magnetism_difficult_ms_turns_pattern_then_mcq_then_word,
        _magnetism_difficult_ms_poles_letter_then_order_then_pick,
        _magnetism_difficult_ms_animal_mcq_then_count_then_word,
    ],
}

MAGNETISM_SMS_POOLS = {
    "foundational": [
        _magnetism_foundational_sms_board_magnets_then_why_mcq,
        _magnetism_foundational_sms_scrapyard_pick_then_count,
        _magnetism_foundational_sms_hike_order_then_word,
    ],
    "intermediate": [
        _magnetism_intermediate_sms_recycle_pct_then_mcq_then_word,
        _magnetism_intermediate_sms_door_pick_then_order,
        _magnetism_intermediate_sms_ship_readings_then_reason_mcq,
    ],
    "difficult": [
        _magnetism_difficult_sms_trial_ratio_then_caution_pick_then_verdict,
        _magnetism_difficult_sms_maglev_order_then_word_then_count,
        _magnetism_difficult_sms_myth_pick_then_test_mcq,
    ],
}


# ---------------------------------------------------------------------------
# robotics_project — multi_step (F, I, D); situational (F, I, D).
# Grades requirements, component choice, logic, test evidence and iteration.
# ---------------------------------------------------------------------------

_RB_MS_F_REQ_PACKS = (
    {"reqs": ("move 20 cm on a table", "stop at a black line", "carry a 50 g load"), "n": 3},
    {"reqs": ("turn 90° on a mat", "beep when it sees an obstacle"), "n": 2},
    {"reqs": ("push a cup 10 cm", "reverse when the bumper is pressed", "run for 30 s", "stay inside a taped box"), "n": 4},
)


@_u31_variant("robotics_project", "ms", "foundational", "requirements_count_then_testable_mcq")
def _robotics_project_foundational_ms_requirements_count_then_testable_mcq():
    pack = random.choice(_RB_MS_F_REQ_PACKS)
    correct = "another group could test each one and say pass or fail"
    distractors = ("they store a league of whose robot is best", "they replace the teacher's risk assessment", "they need a private photo upload")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional team's plan lists requirements: " + "; ".join(pack["reqs"]) + ".</p>"
        "<p>(i) Enter the number of requirements.</p>"
        "<p>(ii) The requirements in (i) are good because</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Count, then testable means pass/fail by another group."
    return (
        question, solution, hint, 2,
        _fields((pack["n"], letter), ("Requirements", "Good because"),
                ("number", "mcq"), (None, options), hint="Count, then choose testability."),
    )


@_u31_variant("robotics_project", "ms", "foundational", "phases_order_then_word")
def _robotics_project_foundational_ms_phases_order_then_word():
    order_raw, order_bank = _order(
        (
            "Write requirements another group could test",
            "Choose simple machines and parts that match them",
            "Test, then iterate the design",
        ),
        ("Upload private home-workshop photos to the app",),
    )
    question = (
        "<p>A fictional project board shows the phases of a classroom robot build.</p>"
        "<p>(i) Order the phases.</p>"
        "<p>(ii) Write the one-word name for changing the design after a test (step 3 of (i)).</p>"
    )
    solution = (
        "(i) <strong>requirements → choose parts → test and iterate</strong><br>"
        "(ii) <strong>iterate</strong>"
    )
    hint = "<strong>Key idea:</strong> Need, mechanism, test, iterate."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "iterate"), ("Phases", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three phases, then one word."),
    )


@_u31_variant("robotics_project", "ms", "foundational", "sda_pick_then_count")
def _robotics_project_foundational_ms_sda_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Sense: a bumper or light sensor detects something", "Decide: a simple rule chooses what to do", "Act: a motor or buzzer responds"),
        ("Rank: the app stores whose robot is best", "Upload: private code is sent to the app"),
        3,
    )
    question = (
        "<p>A fictional worksheet models a classroom program.</p>"
        "<p>(i) Select the three stages of sense–decide–act.</p>"
        "<p>(ii) Enter how many stages you selected in (i).</p>"
    )
    solution = "(i) Sense; decide; act.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Three stages; no league, no upload."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Stages", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_RB_MS_I_MACHINE_PACKS = (
    {"need": "lift a small load onto a shelf", "machine": "a pulley", "others": ("a ramp", "a lever")},
    {"need": "push a heavy box up onto a platform", "machine": "a ramp", "others": ("a pulley", "a lever")},
    {"need": "flip a switch with a small push", "machine": "a lever", "others": ("a pulley", "a ramp")},
)


@_u31_variant("robotics_project", "ms", "intermediate", "match_machine_then_test_mcq")
def _robotics_project_intermediate_ms_match_machine_then_test_mcq():
    pack = random.choice(_RB_MS_I_MACHINE_PACKS)
    correct = pack["machine"]
    distractors = pack["others"] + ("a stored league table",)
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional team's requirement: '{pack['need']}'. They consider a lever, "
        "a pulley and a ramp.</p>"
        "<p>(i) Enter how many simple machines they consider.</p>"
        "<p>(ii) For the requirement, the best match among the machines in (i) is</p>"
    )
    solution = (
        "(i) <strong>3</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Match the machine to the job."
    return (
        question, solution, hint, 2,
        _fields((3, letter), ("Machines considered", "Best match"),
                ("number", "mcq"), (None, options), hint="Enter 3, then choose the machine."),
    )


@_u31_variant("robotics_project", "ms", "intermediate", "test_order_then_evidence_word")
def _robotics_project_intermediate_ms_test_order_then_evidence_word():
    order_raw, order_bank = _order(
        (
            "Run the robot against one requirement",
            "Record the result as pass or fail with a measurement",
            "Change one thing in the design and test again",
        ),
        ("Declare the robot best in class",),
    )
    question = (
        "<p>A fictional test log template guides a classroom team.</p>"
        "<p>(i) Order the test cycle.</p>"
        "<p>(ii) Write the one-word term for the recorded results that the class "
        "rubric grades (step 2 of (i)).</p>"
    )
    solution = (
        "(i) <strong>run → record → change one thing and retest</strong><br>"
        "(ii) <strong>evidence</strong>"
    )
    hint = "<strong>Key idea:</strong> Test, record evidence, iterate."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "evidence"), ("Test cycle", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


@_u31_variant("robotics_project", "ms", "intermediate", "parts_pick_then_count")
def _robotics_project_intermediate_ms_parts_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Use only teacher-approved low-voltage parts", "Plan electromagnets or electronics with a risk assessment"),
        ("Use any household mains part", "Photograph home wiring for the app"),
        2,
    )
    question = (
        "<p>A fictional parts-request form lists rules for electrical components.</p>"
        "<p>(i) Select the two rules the project follows.</p>"
        "<p>(ii) Enter how many rules you selected in (i).</p>"
    )
    solution = "(i) Approved low-voltage parts; risk assessment.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Approved parts under a risk assessment."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Rules", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two rules, then enter 2."),
    )


_RB_MS_D_LOG_PACKS = (
    {"trials": 5, "passes": 3, "req": "stop at the black line"},
    {"trials": 8, "passes": 6, "req": "carry the 50 g load"},
    {"trials": 4, "passes": 1, "req": "turn 90° on the mat"},
)


@_u31_variant("robotics_project", "ms", "difficult", "log_pct_then_next_mcq_then_word")
def _robotics_project_difficult_ms_log_pct_then_next_mcq_then_word():
    pack = random.choice(_RB_MS_D_LOG_PACKS)
    pct = _pct(pack["passes"], pack["trials"])
    correct = "change one part of the design, then repeat the same test"
    distractors = ("declare the requirement met", "store the robot in a league", "change everything at once")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional test log: requirement '{pack['req']}' passed {pack['passes']} "
        f"of {pack['trials']} trials.</p>"
        "<p>(i) Calculate the pass rate as a whole-number percentage.</p>"
        "<p>(ii) Given the rate in (i), the next iteration step is to</p>"
        "<p>(iii) Write the one-word name for the recorded trials the rubric grades.</p>"
    )
    solution = (
        f"(i) {pack['passes']} ÷ {pack['trials']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>evidence</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, then one change at a time."
    return (
        question, solution, hint, 3,
        _fields((pct, letter, "evidence"), ("Pass rate (%)", "Next step", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Percentage, choose, then one word."),
    )


@_u31_variant("robotics_project", "ms", "difficult", "logic_order_then_pick_then_count")
def _robotics_project_difficult_ms_logic_order_then_pick_then_count():
    order_raw, order_bank = _order(
        (
            "Sense: the bumper switch closes on contact",
            "Decide: if the bumper is pressed, choose reverse",
            "Act: the motor runs backwards for one second",
        ),
        ("Rank: the app stores whose robot is best",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        ("The physical robot is graded in class with a rubric, not by this app", "Only the plan, evidence and reflection are graded here"),
        ("Private code must be uploaded to be graded", "The fastest robot wins a stored league"),
        2,
    )
    question = (
        "<p>A fictional flowchart describes a bump-and-reverse behaviour.</p>"
        "<p>(i) Order the sense–decide–act chain.</p>"
        "<p>(ii) Select the two statements about how this project is graded.</p>"
        "<p>(iii) Enter how many stages the chain in (i) has.</p>"
    )
    solution = (
        "(i) <strong>sense bumper → decide reverse → act motor</strong><br>"
        "(ii) Rubric in class; plan and evidence here.<br>"
        "(iii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Sense–decide–act; grading covers planning and evidence."
    return (
        question, solution, hint, 3,
        _fields((order_raw, pick_raw, 3), ("Chain", "Grading statements", "Stages"),
                ("order", "pick", "number"), (order_bank, pick_bank, None), (None, pick_count, None),
                hint="Order, two statements, then enter 3."),
    )


_RB_MS_D_BUDGET_PACKS = (
    {"budget": 20, "spent": 14, "items": ("two motors", "a bumper switch", "a battery pack")},
    {"budget": 30, "spent": 24, "items": ("a light sensor", "a buzzer", "a gearbox")},
    {"budget": 25, "spent": 15, "items": ("a motor", "a pulley kit", "a battery pack")},
)


@_u31_variant("robotics_project", "ms", "difficult", "budget_left_then_mcq_then_word")
def _robotics_project_difficult_ms_budget_left_then_mcq_then_word():
    pack = random.choice(_RB_MS_D_BUDGET_PACKS)
    left = pack["budget"] - pack["spent"]
    correct = "check each part against a requirement before ordering"
    distractors = ("buy the most expensive part", "order household mains parts", "spend it on a league trophy")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional team has a {pack['budget']} token parts budget and has spent "
        f"{pack['spent']} on {', '.join(pack['items'])}.</p>"
        "<p>(i) Calculate the tokens left.</p>"
        "<p>(ii) Before spending the tokens from (i), the team should</p>"
        "<p>(iii) Write the one-word name of the testable need each part must serve.</p>"
    )
    solution = (
        f"(i) {pack['budget']} − {pack['spent']} = <strong>{left}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>requirement</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then parts serve requirements."
    return (
        question, solution, hint, 3,
        _fields((left, letter, "requirement"), ("Tokens left", "Should", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


# robotics_project — situational_multi_step (F, I, D)

_RB_SMS_F_TEAM_PACKS = (
    {"team": "Team Comet (fictional)", "goal": "deliver a marker pen across a desk", "reqs": 3},
    {"team": "Team Otter (fictional)", "goal": "sort two colours of counters", "reqs": 2},
    {"team": "Team Pixel (fictional)", "goal": "follow a taped line", "reqs": 4},
)


@_u31_variant("robotics_project", "sms", "foundational", "team_reqs_then_first_mcq")
def _robotics_project_foundational_sms_team_reqs_then_first_mcq():
    pack = random.choice(_RB_SMS_F_TEAM_PACKS)
    correct = "write requirements another group could test"
    distractors = ("upload private photos to the app", "rank the other teams", "skip the risk assessment")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['team']} wants a robot to {pack['goal']}; their plan has "
        f"{pack['reqs']} requirements.</p>"
        "<p>(i) Enter the number of requirements.</p>"
        "<p>(ii) Before the requirements in (i) were written, the first project phase was to</p>"
    )
    solution = (
        f"(i) <strong>{pack['reqs']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Requirements first."
    return (
        question, solution, hint, 2,
        _fields((pack["reqs"], letter), ("Requirements", "First phase"),
                ("number", "mcq"), (None, options), hint="Count, then choose requirements."),
    )


@_u31_variant("robotics_project", "sms", "foundational", "club_pick_then_count")
def _robotics_project_foundational_sms_club_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Build time needs the class, parts and the teacher's risk assessment", "The physical robot is graded in class with a rubric"),
        ("This web page replaces the practical", "The app stores whose robot is best"),
        2,
    )
    question = (
        "<p>A fictional robotics-club notice explains how the term project works.</p>"
        "<p>(i) Select the two statements consistent with the notice.</p>"
        "<p>(ii) Enter how many physical robots this app auto-grades as a finished product.</p>"
    )
    solution = "(i) Class build; rubric in class.<br>(ii) <strong>0</strong>"
    hint = "<strong>Key idea:</strong> Practical in class; this page grades planning."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 0), ("Statements", "Robots auto-graded"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 0."),
    )


@_u31_variant("robotics_project", "sms", "foundational", "line_follow_order_then_word")
def _robotics_project_foundational_sms_line_follow_order_then_word():
    order_raw, order_bank = _order(
        (
            "A light sensor senses the dark line",
            "The program decides which way to steer",
            "The motors act to turn the robot",
        ),
        ("The app uploads the private code",),
    )
    question = (
        "<p>A fictional demo robot follows a taped line around a mat.</p>"
        "<p>(i) Order its behaviour.</p>"
        "<p>(ii) Write the one-word first stage of that model (step 1 of (i)).</p>"
    )
    solution = (
        "(i) <strong>sense line → decide steer → act motors</strong><br>"
        "(ii) <strong>sense</strong>"
    )
    hint = "<strong>Key idea:</strong> Sense, decide, act."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "sense"), ("Behaviour", "First stage"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_RB_SMS_I_FAIL_PACKS = (
    {"team": "Team Comet (fictional)", "fail": "the gripper drops the pen", "change": "add a second rubber pad to the gripper"},
    {"team": "Team Otter (fictional)", "fail": "the sorter jams", "change": "widen the chute by 5 mm"},
    {"team": "Team Pixel (fictional)", "fail": "the robot overshoots the line", "change": "slow the motors near the sensor"},
)


@_u31_variant("robotics_project", "sms", "intermediate", "fail_change_then_mcq_then_word")
def _robotics_project_intermediate_sms_fail_change_then_mcq_then_word():
    pack = random.choice(_RB_SMS_I_FAIL_PACKS)
    correct = "one change at a time, then the same test again, so the effect can be seen"
    distractors = ("change everything and hope", "stop testing and declare success", "rank the team")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['team']} logs that {pack['fail']}; they plan to {pack['change']}.</p>"
        "<p>(i) Enter how many design changes they plan.</p>"
        "<p>(ii) The plan in (i) is good iteration because it makes</p>"
        "<p>(iii) Write the one-word term for this test-change-retest process.</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>iteration</strong>"
    )
    hint = "<strong>Key idea:</strong> One change, same test, compare."
    return (
        question, solution, hint, 3,
        _fields((1, letter, "iteration"), ("Changes planned", "Good because", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Enter 1, choose, then one word."),
    )


_RB_SMS_I_SAFE_PACKS = (
    {"team": "Team Otter (fictional)", "wants": "an electromagnet gripper"},
    {"team": "Team Pixel (fictional)", "wants": "a buzzer circuit"},
    {"team": "Team Comet (fictional)", "wants": "a second motor"},
)


@_u31_variant("robotics_project", "sms", "intermediate", "parts_request_pick_then_order")
def _robotics_project_intermediate_sms_parts_request_pick_then_order():
    pack = random.choice(_RB_SMS_I_SAFE_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("The part must be teacher-approved and low-voltage", "The plan needs a risk assessment before building"),
        ("Any household mains part is fine", "Photos of home wiring must be uploaded"),
        2,
    )
    order_raw, order_bank = _order(
        (
            "Explain which requirement the part serves",
            "Get the part approved under the risk assessment",
            "Build and test with the class",
        ),
        ("Order the part from a private supplier in secret",),
    )
    question = (
        f"<p>{pack['team']} requests {pack['wants']} for their robot.</p>"
        "<p>(i) Select the two rules that apply.</p>"
        "<p>(ii) Using the approval rule from (i), order the request process.</p>"
    )
    solution = (
        "(i) Approved low-voltage; risk assessment.<br>"
        "(ii) <strong>link to requirement → approval → build and test</strong>"
    )
    hint = "<strong>Key idea:</strong> Requirement, approval, then build."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Rules", "Request process"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two rules, then order three steps."),
    )


_RB_SMS_I_LOAD_PACKS = (
    {"team": "Team Comet (fictional)", "load": 50, "machine": "a pulley"},
    {"team": "Team Otter (fictional)", "load": 30, "machine": "a lever"},
    {"team": "Team Pixel (fictional)", "load": 80, "machine": "a ramp"},
)


@_u31_variant("robotics_project", "sms", "intermediate", "load_machine_then_reason_mcq")
def _robotics_project_intermediate_sms_load_machine_then_reason_mcq():
    pack = random.choice(_RB_SMS_I_LOAD_PACKS)
    correct = "it trades a smaller motor force for a larger distance, which the small motor can supply"
    distractors = ("it creates energy for the motor", "it makes the load lighter", "it ranks the teams")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['team']} must lift a {pack['load']} g load with a small motor, so "
        f"they add {pack['machine']}.</p>"
        "<p>(i) Enter the load in grams.</p>"
        f"<p>(ii) {pack['machine'].capitalize()} helps with the load in (i) because</p>"
    )
    solution = (
        f"(i) <strong>{pack['load']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> A simple machine trades force for distance."
    return (
        question, solution, hint, 2,
        _fields((pack["load"], letter), ("Load (g)", "Helps because"),
                ("number", "mcq"), (None, options), hint="Enter the load, then choose the trade-off."),
    )


_RB_SMS_D_SHOW_PACKS = (
    {"team": "Team Comet (fictional)", "trials": 10, "passes": 7},
    {"team": "Team Otter (fictional)", "trials": 6, "passes": 3},
    {"team": "Team Pixel (fictional)", "trials": 8, "passes": 2},
)


@_u31_variant("robotics_project", "sms", "difficult", "showcase_pct_then_caution_pick_then_verdict")
def _robotics_project_difficult_sms_showcase_pct_then_caution_pick_then_verdict():
    pack = random.choice(_RB_SMS_D_SHOW_PACKS)
    pct = _pct(pack["passes"], pack["trials"])
    pick_raw, pick_bank, pick_count = _pick(
        ("The number of trials is small, so the rate is uncertain", "The log shows evidence and iteration, which is what the rubric grades"),
        ("The team should be ranked in a stored league", "A low rate means the plan was worthless"),
        2,
    )
    correct = "the evidence and reflection are strong even though the pass rate is imperfect"
    distractors = ("the robot must be uploaded to be graded", "the team failed the project", "the rate should be hidden")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>At a fictional showcase, {pack['team']} presents a log: {pack['passes']} "
        f"passes in {pack['trials']} trials, with three iterations documented.</p>"
        "<p>(i) Calculate the pass rate as a whole-number percentage.</p>"
        "<p>(ii) Using the rate from (i), select the two fair readings.</p>"
        "<p>(iii) Given (ii), the rubric's verdict is that</p>"
    )
    solution = (
        f"(i) {pack['passes']} ÷ {pack['trials']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) Small sample; evidence and iteration count.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> The rubric grades process, not the pass rate alone."
    return (
        question, solution, hint, 3,
        _fields((pct, pick_raw, letter), ("Pass rate (%)", "Fair readings", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Percentage, two readings, then the verdict."),
    )


_RB_SMS_D_SENSOR_PACKS = (
    {"team": "Team Pixel (fictional)", "sensor": "a light sensor", "false": 4, "total": 20},
    {"team": "Team Otter (fictional)", "sensor": "a bumper switch", "false": 2, "total": 10},
    {"team": "Team Comet (fictional)", "sensor": "a distance sensor", "false": 5, "total": 25},
)


@_u31_variant("robotics_project", "sms", "difficult", "sensor_errors_then_order_then_word")
def _robotics_project_difficult_sms_sensor_errors_then_order_then_word():
    pack = random.choice(_RB_SMS_D_SENSOR_PACKS)
    pct = _pct(pack["false"], pack["total"])
    order_raw, order_bank = _order(
        (
            "Identify which stage failed: sense, decide or act",
            "Change one thing at that stage, for example the sensor position",
            "Repeat the same trials and compare the error rate",
        ),
        ("Replace the whole robot and skip the log",),
    )
    question = (
        f"<p>{pack['team']} logs that {pack['sensor']} triggered wrongly {pack['false']} "
        f"times in {pack['total']} trials.</p>"
        "<p>(i) Calculate the false-trigger rate as a whole-number percentage.</p>"
        "<p>(ii) Using the rate from (i), order the debugging method.</p>"
        "<p>(iii) Write the one-word stage of sense–decide–act that the sensor belongs to.</p>"
    )
    solution = (
        f"(i) {pack['false']} ÷ {pack['total']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) <strong>identify stage → change one thing → repeat and compare</strong><br>"
        "(iii) <strong>sense</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, then locate the failing stage and iterate."
    return (
        question, solution, hint, 3,
        _fields((pct, order_raw, "sense"), ("False triggers (%)", "Debugging method", "Stage"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Percentage, three steps, then one word."),
    )


@_u31_variant("robotics_project", "sms", "difficult", "judge_pick_then_grading_mcq")
def _robotics_project_difficult_sms_judge_pick_then_grading_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("Judges look for testable requirements and documented iteration", "Presenting evidence matters more than a flawless run"),
        ("Judges store a private league of pupils", "Home-workshop photos are required"),
        2,
    )
    correct = "planning, evidence, iteration and reflection; the physical robot is judged in class"
    distractors = ("only the fastest robot", "the private code upload", "whose parents helped most")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional judging guide for a school robotics fair is published for all teams.</p>"
        "<p>(i) Select the two statements consistent with the guide.</p>"
        "<p>(ii) Using the first statement from (i), this app's part of the grade covers</p>"
    )
    solution = (
        "(i) Testable requirements and iteration; evidence over perfection.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Process and evidence are graded; the build stays in class."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Grade covers"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the scope."),
    )


ROBOTICS_PROJECT_MS_POOLS = {
    "foundational": [
        _robotics_project_foundational_ms_requirements_count_then_testable_mcq,
        _robotics_project_foundational_ms_phases_order_then_word,
        _robotics_project_foundational_ms_sda_pick_then_count,
    ],
    "intermediate": [
        _robotics_project_intermediate_ms_match_machine_then_test_mcq,
        _robotics_project_intermediate_ms_test_order_then_evidence_word,
        _robotics_project_intermediate_ms_parts_pick_then_count,
    ],
    "difficult": [
        _robotics_project_difficult_ms_log_pct_then_next_mcq_then_word,
        _robotics_project_difficult_ms_logic_order_then_pick_then_count,
        _robotics_project_difficult_ms_budget_left_then_mcq_then_word,
    ],
}

ROBOTICS_PROJECT_SMS_POOLS = {
    "foundational": [
        _robotics_project_foundational_sms_team_reqs_then_first_mcq,
        _robotics_project_foundational_sms_club_pick_then_count,
        _robotics_project_foundational_sms_line_follow_order_then_word,
    ],
    "intermediate": [
        _robotics_project_intermediate_sms_fail_change_then_mcq_then_word,
        _robotics_project_intermediate_sms_parts_request_pick_then_order,
        _robotics_project_intermediate_sms_load_machine_then_reason_mcq,
    ],
    "difficult": [
        _robotics_project_difficult_sms_showcase_pct_then_caution_pick_then_verdict,
        _robotics_project_difficult_sms_sensor_errors_then_order_then_word,
        _robotics_project_difficult_sms_judge_pick_then_grading_mcq,
    ],
}
