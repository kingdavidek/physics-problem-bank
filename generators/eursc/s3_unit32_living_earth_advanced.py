"""S3 Unit 3.2 Living Earth advanced Practice pools (MS / SMS). Isolated from lesson banks.

Batch 4.2. Five topics, full matrix (docs/EURSC_ADVANCED_QUESTIONS.md):

  food_environment            MS F, I, D   SMS F, I, D
  ecosystems_cycles           MS F, I, D   SMS F, I, D
  ecosystem_characteristics   MS F, I, D   SMS F, I, D
  classification_biodiversity MS F, I, D   SMS F, I, D
  ecology_field_project       MS F, I, D   SMS F, I, D

Safeguarding and syllabus boundaries for this batch, enforced by the smoke:
  * environmental scenarios use supplied public lifecycle / footprint tables,
    fictional reserves, farms and field stations, or aggregate survey data —
    never a pupil's household, diet, bin, garden, address or travel;
  * nothing ranks households, homes, families, gardens or pupils;
  * field-project items grade the question, risk plan, sampling method,
    records, analysis and reflection — never fieldwork completion, a private
    garden upload or a location-linked sample;
  * photosynthesis and respiration stay at word-equation level; matter and
    energy are conserved, never created.
"""
import random

from generators.eursc.science_shared import (
    carbon_cycle_steps,
    factor_boxes,
    key_boxes,
    lifecycle_boxes,
    trophic_boxes,
)
from generators.shared.utils import graded_answer_number_fields, make_graded_problem
from models.svg_kit import bar_chart

_LEVEL = "eursc"
_SUBJECT = "science"


def _u32_variant(topic, mode_tag, difficulty, suffix):
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
# food_environment — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_FE_MS_F_TABLE_PACKS = (
    {"rows": (("lentils", 1), ("chicken", 6), ("beef", 27)), "unit": "kg CO₂e per kg"},
    {"rows": (("potatoes", 1), ("cheese", 12), ("lamb", 24)), "unit": "kg CO₂e per kg"},
    {"rows": (("beans", 1), ("eggs", 4), ("beef", 27)), "unit": "kg CO₂e per kg"},
)


@_u32_variant("food_environment", "ms", "foundational", "table_highest_then_meaning_mcq")
def _food_environment_foundational_ms_table_highest_then_meaning_mcq():
    pack = random.choice(_FE_MS_F_TABLE_PACKS)
    rows = pack["rows"]
    top = max(rows, key=lambda r: r[1])
    correct = "a public footprint figure for comparing foods, not a private diary"
    distractors = ("a ranking of households", "a rule about what any pupil must eat", "a food group")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional textbook footprint table ({pack['unit']}): "
        + ", ".join(f"{n} {v}" for n, v in rows)
        + ".</p>"
        "<p>(i) Enter the highest value in the table.</p>"
        f"<p>(ii) The value in (i) for {top[0]} is</p>"
    )
    solution = (
        f"(i) <strong>{top[1]}</strong> ({top[0]})<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Read the maximum; footprint tables compare foods publicly."
    return (
        question, solution, hint, 2,
        _fields((top[1], letter), ("Highest value", "The value is"),
                ("number", "mcq"), (None, options), hint="Read the maximum, then choose."),
    )


@_u32_variant("food_environment", "ms", "foundational", "lifecycle_letter_then_order")
def _food_environment_foundational_ms_lifecycle_letter_then_order():
    diagram = str(lifecycle_boxes(title="Fictional food lifecycle"))
    order_raw, order_bank = _order(
        ("Produce: grow or make the food", "Use: eat or use the food", "Waste: leftover material in the system"),
        ("Diary: log every family meal",),
    )
    question = (
        diagram
        + "<p>A fictional lifecycle sketch labels A produce, B use, C waste.</p>"
        "<p>(i) Enter the letter of the first stage.</p>"
        "<p>(ii) Starting from the stage in (i), order the lifecycle.</p>"
    )
    solution = "(i) <strong>A</strong><br>(ii) <strong>produce → use → waste</strong>"
    hint = "<strong>Key idea:</strong> A starts the cycle; produce, use, waste."
    return (
        question, solution, hint, 2,
        _fields(("A", order_raw), ("First stage", "Lifecycle"),
                ("keyword", "order"), (None, order_bank), hint="Enter A, then order three stages."),
    )


@_u32_variant("food_environment", "ms", "foundational", "impact_pick_then_count")
def _food_environment_foundational_ms_impact_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Land used to grow or graze", "Water used in production", "Greenhouse gases released"),
        ("A private family carbon diary", "A ranking of whose household is greenest"),
        3,
    )
    question = (
        "<p>A fictional revision card lists environmental impacts of food systems.</p>"
        "<p>(i) Select the three impacts the lesson names.</p>"
        "<p>(ii) Enter how many impacts you selected in (i).</p>"
    )
    solution = "(i) Land; water; greenhouse gases.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Three impact types; no diary, no ranking."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Impacts", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_FE_MS_I_COMPARE_PACKS = (
    {"a": ("beef", 27), "b": ("lentils", 1)},
    {"a": ("lamb", 24), "b": ("beans", 2)},
    {"a": ("cheese", 12), "b": ("potatoes", 1)},
)


@_u32_variant("food_environment", "ms", "intermediate", "compare_ratio_then_choice_mcq")
def _food_environment_intermediate_ms_compare_ratio_then_choice_mcq():
    pack = random.choice(_FE_MS_I_COMPARE_PACKS)
    (a, av), (b, bv) = pack["a"], pack["b"]
    ratio = av // bv
    correct = f"a public canteen could cut its footprint by serving more {b} dishes"
    distractors = (f"every pupil must stop eating {a}", "households should be ranked", f"{b} has the larger footprint")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional public footprint table: {a} {av} and {b} {bv} kg CO₂e per kg.</p>"
        f"<p>(i) How many times larger is the {a} footprint?</p>"
        "<p>(ii) A fair public-choice conclusion from (i) is that</p>"
    )
    solution = (
        f"(i) {av} ÷ {bv} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then a public option — not a personal rule."
    return (
        question, solution, hint, 2,
        _fields((ratio, letter), ("Times larger", "Fair conclusion"),
                ("number", "mcq"), (None, options), hint="Divide, then choose the public option."),
    )


@_u32_variant("food_environment", "ms", "intermediate", "ghg_order_then_word")
def _food_environment_intermediate_ms_ghg_order_then_word():
    order_raw, order_bank = _order(
        ("Food production releases greenhouse gases", "The gases build up in the atmosphere", "More heat is trapped, linked to climate change"),
        ("The gases make the food heavier",),
    )
    question = (
        "<p>A fictional geography-and-science page links food to climate.</p>"
        "<p>(i) Order the chain.</p>"
        "<p>(ii) Write the one-word name for gases that trap heat (______ gases).</p>"
    )
    solution = "(i) <strong>release → build up → trap heat</strong><br>(ii) <strong>greenhouse</strong>"
    hint = "<strong>Key idea:</strong> Release, accumulate, trap."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "greenhouse"), ("Chain", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_FE_MS_I_WASTE_PACKS = (
    {"produced": 100, "wasted": 30},
    {"produced": 200, "wasted": 50},
    {"produced": 150, "wasted": 45},
)


@_u32_variant("food_environment", "ms", "intermediate", "waste_pick_then_pct")
def _food_environment_intermediate_ms_waste_pick_then_pct():
    pack = random.choice(_FE_MS_I_WASTE_PACKS)
    pct = _pct(pack["wasted"], pack["produced"])
    pick_raw, pick_bank, pick_count = _pick(
        ("Wasted food still used land, water and energy to produce", "Reducing waste is a public sustainable choice"),
        ("Wasted food has no environmental cost", "The class should log each pupil's plate"),
        2,
    )
    question = (
        f"<p>A fictional public report: {pack['produced']} tonnes of food produced, "
        f"{pack['wasted']} tonnes wasted.</p>"
        "<p>(i) Select the two correct statements.</p>"
        "<p>(ii) Using the figures behind (i), calculate the percentage wasted (whole number).</p>"
    )
    solution = (
        "(i) Waste used resources; reducing it is a public choice.<br>"
        f"(ii) {pack['wasted']} ÷ {pack['produced']} × 100 = <strong>{pct}%</strong>"
    )
    hint = "<strong>Key idea:</strong> Waste carries its production cost; percentage of the total."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, pct), ("Statements", "Wasted (%)"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then the percentage."),
    )


_FE_MS_D_ORDER_PACKS = (
    {"foods": (("apple", 0.4), ("rice", 4), ("cheese", 12), ("beef", 27)), "lowest": "apple"},
    {"foods": (("potatoes", 0.5), ("tofu", 3), ("pork", 7), ("lamb", 24)), "lowest": "potatoes"},
    {"foods": (("peas", 1), ("chicken", 6), ("prawns", 12), ("beef", 27)), "lowest": "peas"},
)


@_u32_variant("food_environment", "ms", "difficult", "order_foods_then_mcq_then_word")
def _food_environment_difficult_ms_order_foods_then_mcq_then_word():
    pack = random.choice(_FE_MS_D_ORDER_PACKS)
    foods = pack["foods"]
    order_raw, order_bank = _order(
        tuple(f"{n} ({v} kg CO₂e per kg)" for n, v in foods),
        ("a private family diary (no value)",),
    )
    correct = "public lifecycle data collected across farms, transport and processing"
    distractors = ("a survey of pupils' plates", "a ranking of households", "a guess from an advert")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional public lifecycle table gives footprints for four foods (values shown in the cards).</p>"
        "<p>(i) Order the foods from lowest to highest footprint.</p>"
        "<p>(ii) The values in (i) come from</p>"
        f"<p>(iii) Write the one-word name of the food with the lowest footprint.</p>"
    )
    solution = (
        "(i) <strong>" + " → ".join(n for n, _ in foods) + "</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        f"(iii) <strong>{pack['lowest']}</strong>"
    )
    hint = "<strong>Key idea:</strong> Order by value; lifecycle data is public."
    return (
        question, solution, hint, 3,
        _fields((order_raw, letter, pack["lowest"]), ("Lowest to highest", "Data source", "Lowest food"),
                ("order", "mcq", "keyword"), (order_bank, options, None),
                hint="Order four foods, choose, then one word."),
    )


_FE_MS_D_LAND_PACKS = (
    {"food": "beef", "land": 160, "alt": "lentils", "alt_land": 8},
    {"food": "lamb", "land": 180, "alt": "peas", "alt_land": 7},
    {"food": "cheese", "land": 80, "alt": "tofu", "alt_land": 4},
)


@_u32_variant("food_environment", "ms", "difficult", "land_ratio_then_pick_then_count")
def _food_environment_difficult_ms_land_ratio_then_pick_then_count():
    pack = random.choice(_FE_MS_D_LAND_PACKS)
    ratio = pack["land"] // pack["alt_land"]
    pick_raw, pick_bank, pick_count = _pick(
        ("Land use is one of several impacts, alongside water and greenhouse gases", "The figures are public averages, not a rule for any household"),
        ("Land use is the only impact that matters", "The class should rank families by land use"),
        2,
    )
    question = (
        f"<p>A fictional public table: {pack['food']} uses about {pack['land']} m² of land "
        f"per kg of protein; {pack['alt']} about {pack['alt_land']} m².</p>"
        f"<p>(i) How many times more land does {pack['food']} use?</p>"
        "<p>(ii) Using the comparison from (i), select the two fair readings.</p>"
        "<p>(iii) Enter how many impact types (land, water, greenhouse gases) the lesson names.</p>"
    )
    solution = (
        f"(i) {pack['land']} ÷ {pack['alt_land']} = <strong>{ratio}</strong><br>"
        "(ii) One of several impacts; public averages.<br>"
        "(iii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then keep the reading public and multi-impact."
    return (
        question, solution, hint, 3,
        _fields((ratio, pick_raw, 3), ("Times more land", "Fair readings", "Impact types"),
                ("number", "pick", "number"), (None, pick_bank, None), (None, pick_count, None),
                hint="Divide, two readings, then enter 3."),
    )


@_u32_variant("food_environment", "ms", "difficult", "claim_mcq_then_order_then_word")
def _food_environment_difficult_ms_claim_mcq_then_order_then_word():
    correct = "check the claim against a public lifecycle table, including transport and packaging"
    distractors = ("accept it because the label is green", "survey pupils' shopping", "rank shops by their adverts")
    options, letter = _mcq(correct, distractors)
    order_raw, order_bank = _order(
        ("Find the public lifecycle data for the product", "Compare each stage: production, transport, packaging, waste", "Judge whether the label's claim matches the evidence"),
        ("Ask each pupil what they bought",),
    )
    question = (
        "<p>A fictional product label says 'eco-friendly' with no figures.</p>"
        "<p>(i) The scientific response is to</p>"
        "<p>(ii) Order how a fictional consumer group would do (i).</p>"
        "<p>(iii) Write the one-word term for a choice that meets today's needs without harming future supply.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>find data → compare stages → judge claim</strong><br>"
        "(iii) <strong>sustainable</strong>"
    )
    hint = "<strong>Key idea:</strong> Evidence beats labels; sustainability is the goal."
    return (
        question, solution, hint, 3,
        _fields((letter, order_raw, "sustainable"), ("Response", "Method", "Term"),
                ("mcq", "order", "keyword"), (options, order_bank, None),
                hint="Choose, order three steps, then one word."),
    )


# food_environment — situational_multi_step (F, I, D)

_FE_SMS_F_CANTEEN_PACKS = (
    {"where": "a fictional school canteen", "options": ("a bean chilli", "a beef burger"), "low": "a bean chilli"},
    {"where": "a fictional festival food stall", "options": ("a lentil curry", "a lamb kebab"), "low": "a lentil curry"},
    {"where": "a fictional hospital kitchen", "options": ("a vegetable pasta", "a cheese bake"), "low": "a vegetable pasta"},
)


@_u32_variant("food_environment", "sms", "foundational", "canteen_options_then_low_mcq")
def _food_environment_foundational_sms_canteen_options_then_low_mcq():
    pack = random.choice(_FE_SMS_F_CANTEEN_PACKS)
    correct = pack["low"]
    other = [o for o in pack["options"] if o != pack["low"]][0]
    distractors = (other, "whichever pupils vote for", "the one with the nicer advert")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['where'].capitalize()} compares {pack['options'][0]} and {pack['options'][1]} "
        "using a public footprint table.</p>"
        "<p>(i) Enter the number of dishes compared.</p>"
        "<p>(ii) Of the dishes in (i), the lower-footprint choice by the table is</p>"
    )
    solution = (
        "(i) <strong>2</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Plant-based dishes sit lower on public footprint tables."
    return (
        question, solution, hint, 2,
        _fields((2, letter), ("Dishes compared", "Lower footprint"),
                ("number", "mcq"), (None, options), hint="Enter 2, then choose the dish."),
    )


_FE_SMS_F_FARM_PACKS = (
    {"farm": "a fictional dairy farm", "stages": 3},
    {"farm": "a fictional apple orchard", "stages": 3},
    {"farm": "a fictional rice paddy", "stages": 3},
)


@_u32_variant("food_environment", "sms", "foundational", "farm_stages_then_pick")
def _food_environment_foundational_sms_farm_stages_then_pick():
    pack = random.choice(_FE_SMS_F_FARM_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("Produce is the start of the food lifecycle", "Waste is leftover material in the system"),
        ("The quiz should store a private family carbon diary", "The farm ranks nearby households"),
        2,
    )
    question = (
        f"<p>A fictional school trip visits {pack['farm']}; the guide shows the "
        f"produce → use → waste lifecycle in {pack['stages']} stages.</p>"
        "<p>(i) Enter the number of stages.</p>"
        "<p>(ii) Using the stages from (i), select the two correct statements.</p>"
    )
    solution = f"(i) <strong>{pack['stages']}</strong><br>(ii) Produce starts; waste is leftover."
    hint = "<strong>Key idea:</strong> Three lifecycle stages; no diary."
    return (
        question, solution, hint, 2,
        _fields((pack["stages"], pick_raw), ("Stages", "Correct statements"),
                ("number", "pick"), (None, pick_bank), (None, pick_count),
                hint="Count, then two statements."),
    )


@_u32_variant("food_environment", "sms", "foundational", "bin_order_then_word")
def _food_environment_foundational_sms_bin_order_then_word():
    order_raw, order_bank = _order(
        ("Leftover food is collected in the canteen's food-waste bin", "It is composted or digested rather than sent to landfill", "Nutrients return to soil or energy is recovered"),
        ("Each pupil's plate is photographed",),
    )
    question = (
        "<p>A fictional canteen poster explains its food-waste bin.</p>"
        "<p>(i) Order what happens to the waste.</p>"
        "<p>(ii) Write the one-word lifecycle stage the poster is about.</p>"
    )
    solution = "(i) <strong>collect → compost or digest → return nutrients / recover energy</strong><br>(ii) <strong>waste</strong>"
    hint = "<strong>Key idea:</strong> The waste stage can return material to the system."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "waste"), ("What happens", "Stage"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_FE_SMS_I_MENU_PACKS = (
    {"canteen": "a fictional school canteen", "before": 40, "after": 25, "meals": 500},
    {"canteen": "a fictional university refectory", "before": 60, "after": 36, "meals": 1000},
    {"canteen": "a fictional workplace cafeteria", "before": 30, "after": 21, "meals": 300},
)


@_u32_variant("food_environment", "sms", "intermediate", "menu_drop_then_mcq_then_word")
def _food_environment_intermediate_sms_menu_drop_then_mcq_then_word():
    pack = random.choice(_FE_SMS_I_MENU_PACKS)
    drop = pack["before"] - pack["after"]
    correct = "a public menu change lowered the total; no individual's meals were tracked"
    distractors = ("each diner's plate was ranked", "the food lost its weight", "the canteen created energy")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['canteen'].capitalize()} reports its weekly footprint fell from "
        f"{pack['before']} to {pack['after']} units after adding plant-based options "
        f"for {pack['meals']} meals.</p>"
        "<p>(i) Calculate the fall in units.</p>"
        "<p>(ii) The fall in (i) shows that</p>"
        "<p>(iii) Write the one-word term for such a choice that protects future supply.</p>"
    )
    solution = (
        f"(i) {pack['before']} − {pack['after']} = <strong>{drop}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>sustainable</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract; public menu, not private plates."
    return (
        question, solution, hint, 3,
        _fields((drop, letter, "sustainable"), ("Fall (units)", "Shows that", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


_FE_SMS_I_TRANSPORT_PACKS = (
    {"item": "strawberries", "local_km": 50, "far_km": 5000},
    {"item": "green beans", "local_km": 80, "far_km": 8000},
    {"item": "apples", "local_km": 30, "far_km": 12000},
)


@_u32_variant("food_environment", "sms", "intermediate", "transport_pick_then_order")
def _food_environment_intermediate_sms_transport_pick_then_order():
    pack = random.choice(_FE_SMS_I_TRANSPORT_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("Transport is only one stage of the lifecycle", "Public lifecycle data, not distance alone, decides the footprint"),
        ("Distance is the whole story", "Shoppers should be ranked by postcode"),
        2,
    )
    order_raw, order_bank = _order(
        ("Look up the production footprint of each source", "Add the transport stage for each distance", "Compare the totals, not just the distances"),
        ("Assume the nearer one always wins",),
    )
    question = (
        f"<p>A fictional supermarket report compares {pack['item']} grown "
        f"{pack['local_km']} km away in a heated greenhouse with {pack['item']} shipped "
        f"{pack['far_km']} km from open fields.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), order a fair comparison.</p>"
    )
    solution = (
        "(i) Transport is one stage; lifecycle data decides.<br>"
        "(ii) <strong>production footprint → add transport → compare totals</strong>"
    )
    hint = "<strong>Key idea:</strong> Whole lifecycle, not distance alone."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "Fair comparison"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_FE_SMS_I_WATER_PACKS = (
    {"crop": "almonds", "litres": 1600, "alt": "oats", "alt_l": 200},
    {"crop": "rice", "litres": 2500, "alt": "potatoes", "alt_l": 250},
    {"crop": "avocados", "litres": 2000, "alt": "peas", "alt_l": 400},
)


@_u32_variant("food_environment", "sms", "intermediate", "water_ratio_then_mcq")
def _food_environment_intermediate_sms_water_ratio_then_mcq():
    pack = random.choice(_FE_SMS_I_WATER_PACKS)
    ratio = pack["litres"] // pack["alt_l"]
    correct = "water use is one impact; a fair comparison also weighs land and greenhouse gases"
    distractors = (f"no one should ever eat {pack['crop']}", "households should be ranked by water", "water use is not an environmental impact")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional public water-footprint table: {pack['crop']} {pack['litres']} litres "
        f"per kg, {pack['alt']} {pack['alt_l']} litres per kg.</p>"
        f"<p>(i) How many times more water does {pack['crop']} use?</p>"
        "<p>(ii) A fair reading of (i) is that</p>"
    )
    solution = (
        f"(i) {pack['litres']} ÷ {pack['alt_l']} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then keep all three impacts in view."
    return (
        question, solution, hint, 2,
        _fields((ratio, letter), ("Times more water", "Fair reading"),
                ("number", "mcq"), (None, options), hint="Divide, then choose the balanced reading."),
    )


_FE_SMS_D_TRIAL_PACKS = (
    {"study": "fictional council canteen trial", "schools_with": 20, "drop_with": 15, "schools_without": 20, "drop_without": 3},
    {"study": "fictional hospital-catering study", "schools_with": 10, "drop_with": 12, "schools_without": 10, "drop_without": 2},
    {"study": "fictional university dining report", "schools_with": 8, "drop_with": 18, "schools_without": 8, "drop_without": 4},
)


@_u32_variant("food_environment", "sms", "difficult", "trial_gap_then_caution_pick_then_verdict")
def _food_environment_difficult_sms_trial_gap_then_caution_pick_then_verdict():
    pack = random.choice(_FE_SMS_D_TRIAL_PACKS)
    gap = pack["drop_with"] - pack["drop_without"]
    pick_raw, pick_bank, pick_count = _pick(
        ("Other changes at the sites could have contributed", "The figures are aggregates; no diner was tracked"),
        ("The result proves every diner changed their diet", "The sites should be ranked publicly by greenness"),
        2,
    )
    correct = "the menu change is associated with a larger footprint fall, within the study's limits"
    distractors = ("the menu change caused a larger footprint", "the control sites wasted more food", "diners should be surveyed on their plates")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A {pack['study']}: {pack['schools_with']} sites adding plant-based options cut "
        f"their footprint by {pack['drop_with']}%; {pack['schools_without']} sites without the "
        f"change cut it by {pack['drop_without']}%.</p>"
        "<p>(i) Calculate the gap in percentage points.</p>"
        "<p>(ii) Using the gap from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['drop_with']} − {pack['drop_without']} = <strong>{gap}</strong> points<br>"
        "(ii) Other changes; aggregates.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, cautions, 'associated with'."
    return (
        question, solution, hint, 3,
        _fields((gap, pick_raw, letter), ("Gap (points)", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Subtract, two cautions, then the verdict."),
    )


_FE_SMS_D_POLICY_PACKS = (
    {"body": "a fictional city council", "policies": ("food-waste collections", "plant-based default menus", "local sourcing contracts")},
    {"body": "a fictional national agency", "policies": ("clear footprint labels", "waste-reduction targets", "support for pulse crops")},
    {"body": "a fictional school federation", "policies": ("meat-free days", "compost bins", "portion-size trials")},
)


@_u32_variant("food_environment", "sms", "difficult", "policy_count_then_order_then_word")
def _food_environment_difficult_sms_policy_count_then_order_then_word():
    pack = random.choice(_FE_SMS_D_POLICY_PACKS)
    order_raw, order_bank = _order(
        ("Measure the current footprint with public data", "Introduce the policy across the whole system", "Re-measure and compare, without tracking individuals"),
        ("Publish a league of the greenest families",),
    )
    question = (
        f"<p>{pack['body'].capitalize()} proposes: " + "; ".join(pack["policies"]) + ".</p>"
        "<p>(i) Enter the number of policies proposed.</p>"
        "<p>(ii) Order how the council would evaluate any policy from (i).</p>"
        "<p>(iii) Write the one-word goal these policies serve: ______ food systems.</p>"
    )
    solution = (
        "(i) <strong>3</strong><br>"
        "(ii) <strong>measure → introduce → re-measure</strong><br>"
        "(iii) <strong>sustainable</strong>"
    )
    hint = "<strong>Key idea:</strong> Count, evaluate at system level, aim for sustainability."
    return (
        question, solution, hint, 3,
        _fields((3, order_raw, "sustainable"), ("Policies", "Evaluation", "Goal"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Enter 3, order three steps, then one word."),
    )


@_u32_variant("food_environment", "sms", "difficult", "documentary_pick_then_verdict_mcq")
def _food_environment_difficult_sms_documentary_pick_then_verdict_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("Lifecycle figures are averages that vary by farm and method", "Choices are discussed as public options, not personal judgements"),
        ("One documentary settles the science", "Families should be ranked by footprint"),
        2,
    )
    correct = "use public lifecycle data to compare options and keep the discussion about systems, not individuals"
    distractors = ("tell each pupil what to eat", "treat one dramatic claim as settled science", "trust the documentary's most dramatic claim")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional documentary about food and climate is shown in a lesson.</p>"
        "<p>(i) Select the two statements a science teacher would add.</p>"
        "<p>(ii) Using the second statement from (i), the lesson's approach is to</p>"
    )
    solution = (
        "(i) Averages vary; public options not personal judgements.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Public data, system-level discussion."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Approach"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the approach."),
    )


FOOD_ENVIRONMENT_MS_POOLS = {
    "foundational": [
        _food_environment_foundational_ms_table_highest_then_meaning_mcq,
        _food_environment_foundational_ms_lifecycle_letter_then_order,
        _food_environment_foundational_ms_impact_pick_then_count,
    ],
    "intermediate": [
        _food_environment_intermediate_ms_compare_ratio_then_choice_mcq,
        _food_environment_intermediate_ms_ghg_order_then_word,
        _food_environment_intermediate_ms_waste_pick_then_pct,
    ],
    "difficult": [
        _food_environment_difficult_ms_order_foods_then_mcq_then_word,
        _food_environment_difficult_ms_land_ratio_then_pick_then_count,
        _food_environment_difficult_ms_claim_mcq_then_order_then_word,
    ],
}

FOOD_ENVIRONMENT_SMS_POOLS = {
    "foundational": [
        _food_environment_foundational_sms_canteen_options_then_low_mcq,
        _food_environment_foundational_sms_farm_stages_then_pick,
        _food_environment_foundational_sms_bin_order_then_word,
    ],
    "intermediate": [
        _food_environment_intermediate_sms_menu_drop_then_mcq_then_word,
        _food_environment_intermediate_sms_transport_pick_then_order,
        _food_environment_intermediate_sms_water_ratio_then_mcq,
    ],
    "difficult": [
        _food_environment_difficult_sms_trial_gap_then_caution_pick_then_verdict,
        _food_environment_difficult_sms_policy_count_then_order_then_word,
        _food_environment_difficult_sms_documentary_pick_then_verdict_mcq,
    ],
}


# ---------------------------------------------------------------------------
# ecosystems_cycles — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_EC_MS_F_CHAIN_PACKS = (
    {"chain": ("grass", "rabbit", "fox"), "n": 3},
    {"chain": ("algae", "water flea", "minnow", "heron"), "n": 4},
    {"chain": ("oak leaf", "caterpillar", "blue tit"), "n": 3},
)


@_u32_variant("ecosystems_cycles", "ms", "foundational", "chain_count_then_producer_mcq")
def _ecosystems_cycles_foundational_ms_chain_count_then_producer_mcq():
    pack = random.choice(_EC_MS_F_CHAIN_PACKS)
    chain = pack["chain"]
    correct = f"{chain[0]}, because it makes food using light energy"
    distractors = tuple(f"{c}, because it eats others" for c in chain[1:3]) + ("the quiz should rank pupils as animals",)
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional textbook food chain: " + " → ".join(chain) + ".</p>"
        "<p>(i) Enter the number of organisms in the chain.</p>"
        "<p>(ii) Of the organisms counted in (i), the producer is</p>"
    )
    solution = f"(i) <strong>{pack['n']}</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> Count, then the producer starts the chain."
    return (
        question, solution, hint, 2,
        _fields((pack["n"], letter), ("Organisms", "Producer"),
                ("number", "mcq"), (None, options), hint="Count, then choose the producer."),
    )


@_u32_variant("ecosystems_cycles", "ms", "foundational", "trophic_letter_then_order")
def _ecosystems_cycles_foundational_ms_trophic_letter_then_order():
    diagram = str(trophic_boxes(title="Fictional trophic sketch"))
    order_raw, order_bank = _order(
        ("A producer makes food using energy", "A consumer eats other organisms", "A decomposer breaks down dead material"),
        ("The quiz ranks which pupil is which animal",),
    )
    question = (
        diagram
        + "<p>A fictional sketch labels A producer, B consumer, C decomposer.</p>"
        "<p>(i) Enter the letter of the decomposer.</p>"
        "<p>(ii) Order the roles, ending with the one in (i).</p>"
    )
    solution = "(i) <strong>C</strong><br>(ii) <strong>producer → consumer → decomposer</strong>"
    hint = "<strong>Key idea:</strong> C recycles; producer, consumer, decomposer."
    return (
        question, solution, hint, 2,
        _fields(("C", order_raw), ("Decomposer letter", "Roles"),
                ("keyword", "order"), (None, order_bank), hint="Enter C, then order three roles."),
    )


@_u32_variant("ecosystems_cycles", "ms", "foundational", "cycle_pick_then_count")
def _ecosystems_cycles_foundational_ms_cycle_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("The water cycle moves water through stages", "The carbon cycle moves carbon through stages"),
        ("Matter is created from nothing in an ecosystem", "The quiz should rank which pupil is which animal"),
        2,
    )
    question = (
        "<p>A fictional revision card lists cycles in an ecosystem.</p>"
        "<p>(i) Select the two cycles the lesson names.</p>"
        "<p>(ii) Enter how many cycles you selected in (i).</p>"
    )
    solution = "(i) Water; carbon.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Two cycles; matter is not created."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Cycles", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select two, then enter 2."),
    )


_EC_MS_I_ENERGY_PACKS = (
    {"producer": 1000, "primary": 100, "secondary": 10},
    {"producer": 2000, "primary": 200, "secondary": 20},
    {"producer": 500, "primary": 50, "secondary": 5},
)


@_u32_variant("ecosystems_cycles", "ms", "intermediate", "energy_pct_then_loss_mcq")
def _ecosystems_cycles_intermediate_ms_energy_pct_then_loss_mcq():
    pack = random.choice(_EC_MS_I_ENERGY_PACKS)
    pct = _pct(pack["primary"], pack["producer"])
    correct = "transferred to the surroundings, mainly as thermal energy through respiration and waste"
    distractors = ("destroyed", "created by the consumer", "stored in the quiz")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional energy-flow table (units per year): producers {pack['producer']}, "
        f"primary consumers {pack['primary']}, secondary consumers {pack['secondary']}.</p>"
        "<p>(i) Calculate the percentage passed from producers to primary consumers.</p>"
        "<p>(ii) The energy not passed on in (i) is</p>"
    )
    solution = (
        f"(i) {pack['primary']} ÷ {pack['producer']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> About a tenth passes on; the rest is transferred, not destroyed."
    return (
        question, solution, hint, 2,
        _fields((pct, letter), ("Passed on (%)", "The rest is"),
                ("number", "mcq"), (None, options), hint="Percentage, then conservation."),
    )


@_u32_variant("ecosystems_cycles", "ms", "intermediate", "carbon_order_then_word")
def _ecosystems_cycles_intermediate_ms_carbon_order_then_word():
    diagram = str(carbon_cycle_steps(title="Fictional carbon cycle"))
    order_raw, order_bank = _order(
        ("Plants take in carbon dioxide during photosynthesis", "Animals eat plants and use the carbon compounds", "Respiration and decay return carbon dioxide to the atmosphere"),
        ("Carbon is created from nothing in the soil",),
    )
    question = (
        diagram
        + "<p>A fictional carbon-cycle sketch labels A photosynthesis, B respiration, C atmosphere store.</p>"
        "<p>(i) Order the cycle starting from photosynthesis.</p>"
        "<p>(ii) Write the one-word process in step 1 of (i).</p>"
    )
    solution = "(i) <strong>photosynthesis → feeding → respiration/decay</strong><br>(ii) <strong>photosynthesis</strong>"
    hint = "<strong>Key idea:</strong> In through photosynthesis, out through respiration."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "photosynthesis"), ("Cycle", "Process"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


@_u32_variant("ecosystems_cycles", "ms", "intermediate", "equation_pick_then_count")
def _ecosystems_cycles_intermediate_ms_equation_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Photosynthesis: carbon dioxide + water → glucose + oxygen (with light)", "Respiration: glucose + oxygen → carbon dioxide + water (releasing energy)"),
        ("Photosynthesis creates matter from nothing", "Respiration happens only in animals"),
        2,
    )
    question = (
        "<p>A fictional worksheet gives word equations.</p>"
        "<p>(i) Select the two correct word equations.</p>"
        "<p>(ii) Enter how many of the equations in (i) involve carbon dioxide.</p>"
    )
    solution = "(i) Photosynthesis; respiration.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Both equations move carbon dioxide."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Word equations", "Involve CO₂"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two equations, then enter 2."),
    )


_EC_MS_D_WEB_PACKS = (
    {"removed": "foxes", "prey": "rabbits", "plant": "grass"},
    {"removed": "herons", "prey": "minnows", "plant": "pondweed"},
    {"removed": "owls", "prey": "voles", "plant": "grass seeds"},
)


@_u32_variant("ecosystems_cycles", "ms", "difficult", "web_remove_then_order_then_word")
def _ecosystems_cycles_difficult_ms_web_remove_then_order_then_word():
    pack = random.choice(_EC_MS_D_WEB_PACKS)
    order_raw, order_bank = _order(
        (f"{pack['removed'].capitalize()} are removed from the web", f"{pack['prey'].capitalize()} numbers rise with fewer predators", f"{pack['plant'].capitalize()} is eaten faster and may decline"),
        (f"{pack['plant'].capitalize()} increases because there are fewer {pack['removed']}",),
    )
    question = (
        f"<p>A fictional food-web model: {pack['plant']} → {pack['prey']} → {pack['removed']}.</p>"
        "<p>(i) Enter how many trophic levels the model shows.</p>"
        f"<p>(ii) Using the levels from (i), order what the model predicts if the {pack['removed']} are removed.</p>"
        "<p>(iii) Write the one-word term for organisms that break down the dead material this produces.</p>"
    )
    solution = (
        "(i) <strong>3</strong><br>"
        "(ii) <strong>predator removed → prey rises → plant declines</strong><br>"
        "(iii) <strong>decomposers</strong>"
    )
    hint = "<strong>Key idea:</strong> Three levels; remove the top and the chain shifts."
    return (
        question, solution, hint, 3,
        _fields((3, order_raw, "decomposers"), ("Trophic levels", "Prediction", "Term"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Enter 3, order three steps, then one word."),
    )


_EC_MS_D_CARBON_PACKS = (
    {"in": 120, "out": 118},
    {"in": 100, "out": 96},
    {"in": 150, "out": 147},
)


@_u32_variant("ecosystems_cycles", "ms", "difficult", "carbon_balance_then_mcq_then_pick")
def _ecosystems_cycles_difficult_ms_carbon_balance_then_mcq_then_pick():
    pack = random.choice(_EC_MS_D_CARBON_PACKS)
    net = pack["in"] - pack["out"]
    correct = "the forest stores a little more carbon than it releases, so it acts as a carbon store"
    distractors = ("carbon is created in the forest", "the forest destroys carbon", "the numbers rank the trees")
    options, letter = _mcq(correct, distractors)
    pick_raw, pick_bank, pick_count = _pick(
        ("Carbon is conserved: it moves between stores", "Photosynthesis takes in carbon dioxide; respiration and decay release it"),
        ("Matter is created from nothing in an ecosystem", "Only animals respire"),
        2,
    )
    question = (
        f"<p>A fictional forest carbon budget (units per year): taken in by photosynthesis "
        f"{pack['in']}, released by respiration and decay {pack['out']}.</p>"
        "<p>(i) Calculate the net carbon stored per year.</p>"
        "<p>(ii) The result in (i) means</p>"
        "<p>(iii) Select the two principles behind the budget.</p>"
    )
    solution = (
        f"(i) {pack['in']} − {pack['out']} = <strong>{net}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) Conservation; photosynthesis in, respiration out."
    )
    hint = "<strong>Key idea:</strong> Subtract, then a store; carbon is conserved."
    return (
        question, solution, hint, 3,
        _fields((net, letter, pick_raw), ("Net stored", "Meaning", "Principles"),
                ("number", "mcq", "pick"), (None, options, pick_bank), (None, None, pick_count),
                hint="Subtract, choose, then two principles."),
    )


@_u32_variant("ecosystems_cycles", "ms", "difficult", "pyramid_mcq_then_count_then_word")
def _ecosystems_cycles_difficult_ms_pyramid_mcq_then_count_then_word():
    correct = "energy is transferred to the surroundings at each level, so less is available higher up"
    distractors = ("energy is created at each level", "consumers eat the quiz", "the pyramid ranks pupils")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional textbook shows a pyramid of numbers: many plants, fewer herbivores, "
        "very few top predators.</p>"
        "<p>(i) The pyramid narrows because</p>"
        "<p>(ii) Enter how many trophic levels the pyramid described shows.</p>"
        "<p>(iii) Write the one-word process that releases energy from food at every level.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>3</strong><br>"
        "(iii) <strong>respiration</strong>"
    )
    hint = "<strong>Key idea:</strong> Transfer at each level; three levels; respiration."
    return (
        question, solution, hint, 3,
        _fields((letter, 3, "respiration"), ("Narrows because", "Levels", "Process"),
                ("mcq", "number", "keyword"), (options, None, None),
                hint="Choose, enter 3, then one word."),
    )


# ecosystems_cycles — situational_multi_step (F, I, D)

_EC_SMS_F_POND_PACKS = (
    {"where": "a fictional school pond", "producers": ("pondweed", "algae"), "consumer": "water snails"},
    {"where": "a fictional park lake", "producers": ("reeds", "algae"), "consumer": "ducks"},
    {"where": "a fictional nature-reserve stream", "producers": ("water crowfoot", "algae"), "consumer": "mayfly larvae"},
)


@_u32_variant("ecosystems_cycles", "sms", "foundational", "pond_producers_then_role_mcq")
def _ecosystems_cycles_foundational_sms_pond_producers_then_role_mcq():
    pack = random.choice(_EC_SMS_F_POND_PACKS)
    correct = "a consumer, because it eats the producers"
    distractors = ("a producer, because it makes food", "a decomposer, because it is small", "a pupil's nickname")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional class survey of {pack['where']} finds {pack['producers'][0]}, "
        f"{pack['producers'][1]} and {pack['consumer']}.</p>"
        "<p>(i) Enter how many producers were found.</p>"
        f"<p>(ii) The {pack['consumer']} feeding on the producers from (i) are</p>"
    )
    solution = f"(i) <strong>2</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> Plants and algae produce; feeders consume."
    return (
        question, solution, hint, 2,
        _fields((2, letter), ("Producers", "The feeders are"),
                ("number", "mcq"), (None, options), hint="Enter 2, then choose consumer."),
    )


@_u32_variant("ecosystems_cycles", "sms", "foundational", "compost_pick_then_count")
def _ecosystems_cycles_foundational_sms_compost_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Decomposers break down the dead material", "Nutrients are returned to the soil"),
        ("Matter is created from nothing in the heap", "The heap ranks the gardeners"),
        2,
    )
    question = (
        "<p>A fictional community-garden sign explains its compost heap.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Enter how many statements you selected in (i).</p>"
    )
    solution = "(i) Decomposers; nutrients returned.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Decomposers recycle matter."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 2."),
    )


@_u32_variant("ecosystems_cycles", "sms", "foundational", "rain_order_then_word")
def _ecosystems_cycles_foundational_sms_rain_order_then_word():
    order_raw, order_bank = _order(
        ("Water evaporates from the lake", "Water vapour condenses into cloud", "Rain falls and runs back to the lake"),
        ("The lake ranks the visitors",),
    )
    question = (
        "<p>A fictional visitor-centre display explains a lake's water cycle.</p>"
        "<p>(i) Order the stages.</p>"
        "<p>(ii) Write the one-word stage in step 2 of (i).</p>"
    )
    solution = "(i) <strong>evaporate → condense → rain returns</strong><br>(ii) <strong>condensation</strong>"
    hint = "<strong>Key idea:</strong> Evaporate, condense, precipitate."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "condensation"), ("Stages", "Stage 2"),
                ("order", "keyword"), (order_bank, None), hint="Order three stages, then one word."),
    )


_EC_SMS_I_RESERVE_PACKS = (
    {"reserve": "a fictional nature reserve", "deer": 200, "wolves": 0, "later": 350},
    {"reserve": "a fictional island reserve", "deer": 120, "wolves": 0, "later": 210},
    {"reserve": "a fictional national park", "deer": 400, "wolves": 0, "later": 640},
)


@_u32_variant("ecosystems_cycles", "sms", "intermediate", "reserve_rise_then_mcq_then_word")
def _ecosystems_cycles_intermediate_sms_reserve_rise_then_mcq_then_word():
    pack = random.choice(_EC_SMS_I_RESERVE_PACKS)
    rise = pack["later"] - pack["deer"]
    correct = "without predators, the deer population grew and grazed the plants harder"
    distractors = ("the deer created matter from nothing", "the reserve ranks its animals", "the plants ate the deer")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional report from {pack['reserve']}: after wolves were lost, deer rose "
        f"from {pack['deer']} to {pack['later']} in five years and young trees became rare.</p>"
        "<p>(i) Calculate the rise in deer numbers.</p>"
        "<p>(ii) The rise in (i) and the loss of young trees show that</p>"
        "<p>(iii) Write the one-word trophic role of the wolves.</p>"
    )
    solution = (
        f"(i) {pack['later']} − {pack['deer']} = <strong>{rise}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>predator</strong>"
    )
    hint = "<strong>Key idea:</strong> Remove the predator; prey rises; producers suffer."
    return (
        question, solution, hint, 3,
        _fields((rise, letter, "predator"), ("Rise in deer", "Shows that", "Wolves' role"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


_EC_SMS_I_GREENHOUSE_PACKS = (
    {"where": "a fictional research greenhouse", "day": 400, "night": 450},
    {"where": "a fictional botanic-garden glasshouse", "day": 380, "night": 430},
    {"where": "a fictional school greenhouse", "day": 410, "night": 470},
)


@_u32_variant("ecosystems_cycles", "sms", "intermediate", "greenhouse_pick_then_order")
def _ecosystems_cycles_intermediate_sms_greenhouse_pick_then_order():
    pack = random.choice(_EC_SMS_I_GREENHOUSE_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("By day photosynthesis takes in more carbon dioxide than respiration releases", "At night only respiration continues, so carbon dioxide rises"),
        ("Plants stop respiring at night", "The sensor ranks the plants"),
        2,
    )
    order_raw, order_bank = _order(
        ("Light arrives at dawn", "Photosynthesis starts and takes in carbon dioxide", "The carbon dioxide reading falls during the day"),
        ("The reading rises because photosynthesis releases carbon dioxide",),
    )
    question = (
        f"<p>A carbon-dioxide sensor in {pack['where']} reads {pack['day']} units by day "
        f"and {pack['night']} units at night.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the first statement from (i), order what happens at dawn.</p>"
    )
    solution = (
        "(i) Day: photosynthesis dominates; night: respiration only.<br>"
        "(ii) <strong>light → photosynthesis starts → reading falls</strong>"
    )
    hint = "<strong>Key idea:</strong> Photosynthesis needs light; respiration runs all day."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "At dawn"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_EC_SMS_I_FARM_PACKS = (
    {"farm": "a fictional arable farm", "returned": 60, "removed": 100},
    {"farm": "a fictional market garden", "returned": 30, "removed": 50},
    {"farm": "a fictional orchard", "returned": 40, "removed": 80},
)


@_u32_variant("ecosystems_cycles", "sms", "intermediate", "farm_pct_then_mcq")
def _ecosystems_cycles_intermediate_sms_farm_pct_then_mcq():
    pack = random.choice(_EC_SMS_I_FARM_PACKS)
    pct = _pct(pack["returned"], pack["removed"])
    correct = "harvest removes nutrients from the cycle, so the rest must be replaced by compost or fertiliser"
    distractors = ("the soil creates nutrients from nothing", "the farm ranks its fields", "nutrients are destroyed by harvesting")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional soil report for {pack['farm']}: {pack['removed']} units of "
        f"nutrients removed by harvest, {pack['returned']} returned as compost.</p>"
        "<p>(i) Calculate the percentage returned (whole number).</p>"
        "<p>(ii) The gap left by (i) shows that</p>"
    )
    solution = (
        f"(i) {pack['returned']} ÷ {pack['removed']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Matter cycles; harvest breaks the loop."
    return (
        question, solution, hint, 2,
        _fields((pct, letter), ("Returned (%)", "Shows that"),
                ("number", "mcq"), (None, options), hint="Percentage, then choose the cycle idea."),
    )


_EC_SMS_D_LAKE_PACKS = (
    {"lake": "a fictional lowland lake", "oxygen_before": 9, "oxygen_after": 3, "cause": "fertiliser run-off"},
    {"lake": "a fictional reservoir", "oxygen_before": 8, "oxygen_after": 2, "cause": "sewage overflow"},
    {"lake": "a fictional canal basin", "oxygen_before": 10, "oxygen_after": 4, "cause": "farm slurry"},
)


@_u32_variant("ecosystems_cycles", "sms", "difficult", "lake_drop_then_order_then_pick")
def _ecosystems_cycles_difficult_sms_lake_drop_then_order_then_pick():
    pack = random.choice(_EC_SMS_D_LAKE_PACKS)
    drop = pack["oxygen_before"] - pack["oxygen_after"]
    order_raw, order_bank = _order(
        (f"{pack['cause'].capitalize()} adds nutrients to the lake", "Algae grow fast, then die", "Decomposers respire, using up oxygen"),
        ("Oxygen is created by the decomposers",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        ("Decomposers respire, so they consume oxygen", "Matter cycles: the nutrients moved from land to water"),
        ("The oxygen was destroyed", "The lake should be ranked against other lakes' owners"),
        2,
    )
    question = (
        f"<p>A fictional water-quality report on {pack['lake']}: dissolved oxygen fell from "
        f"{pack['oxygen_before']} to {pack['oxygen_after']} mg per litre after {pack['cause']}.</p>"
        "<p>(i) Calculate the fall in oxygen.</p>"
        "<p>(ii) Using the fall from (i), order the chain the report describes.</p>"
        "<p>(iii) Select the two principles behind step 3.</p>"
    )
    solution = (
        f"(i) {pack['oxygen_before']} − {pack['oxygen_after']} = <strong>{drop}</strong> mg/L<br>"
        "(ii) <strong>nutrients in → algae boom and die → decomposers use oxygen</strong><br>"
        "(iii) Decomposers respire; matter cycles."
    )
    hint = "<strong>Key idea:</strong> Subtract, then nutrients → algae → decomposer respiration."
    return (
        question, solution, hint, 3,
        _fields((drop, order_raw, pick_raw), ("Oxygen fall (mg/L)", "Chain", "Principles"),
                ("number", "order", "pick"), (None, order_bank, pick_bank), (None, None, pick_count),
                hint="Subtract, order three steps, then two principles."),
    )


_EC_SMS_D_REWILD_PACKS = (
    {"project": "a fictional rewilding project", "years": 10, "trees_before": 200, "trees_after": 1400},
    {"project": "a fictional river-restoration scheme", "years": 8, "trees_before": 150, "trees_after": 900},
    {"project": "a fictional upland reserve", "years": 12, "trees_before": 100, "trees_after": 800},
)


@_u32_variant("ecosystems_cycles", "sms", "difficult", "rewild_ratio_then_caution_pick_then_verdict")
def _ecosystems_cycles_difficult_sms_rewild_ratio_then_caution_pick_then_verdict():
    pack = random.choice(_EC_SMS_D_REWILD_PACKS)
    ratio = pack["trees_after"] // pack["trees_before"]
    pick_raw, pick_bank, pick_count = _pick(
        ("Weather or other management could also have changed over the years", "One site is limited evidence; compare with untouched sites"),
        ("The predators planted the trees", "The result ranks the rangers"),
        2,
    )
    correct = "reintroducing predators is associated with tree recovery through the food web, within the study's limits"
    distractors = ("predators create trees", "the trees ate the deer", "the project proves nothing at all")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A report from {pack['project']}: {pack['years']} years after predators were "
        f"reintroduced, young trees per hectare rose from {pack['trees_before']} to {pack['trees_after']}.</p>"
        "<p>(i) How many times more young trees are there now?</p>"
        "<p>(ii) Using the rise from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['trees_after']} ÷ {pack['trees_before']} = <strong>{ratio}</strong><br>"
        "(ii) Other factors; compare sites.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Ratio, cautions, then a web-based 'associated with'."
    return (
        question, solution, hint, 3,
        _fields((ratio, pick_raw, letter), ("Times more trees", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Divide, two cautions, then the verdict."),
    )


@_u32_variant("ecosystems_cycles", "sms", "difficult", "documentary_pick_then_model_mcq")
def _ecosystems_cycles_difficult_sms_documentary_pick_then_model_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("A food web shows many linked chains, not one line", "A model is a simplification that leaves things out"),
        ("A food web shows every organism on Earth", "The web ranks pupils as animals"),
        2,
    )
    correct = "test the prediction against field counts before trusting it"
    distractors = ("accept it because the animation was impressive", "rank the species", "assume matter is created")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional documentary animates a food web and predicts what happens if one "
        "species vanishes.</p>"
        "<p>(i) Select the two statements a science teacher would add.</p>"
        "<p>(ii) Using the second statement from (i), the lesson's approach to the prediction is to</p>"
    )
    solution = (
        "(i) Webs are linked chains; models simplify.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Models simplify; predictions need testing."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Approach"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the approach."),
    )


ECOSYSTEMS_CYCLES_MS_POOLS = {
    "foundational": [
        _ecosystems_cycles_foundational_ms_chain_count_then_producer_mcq,
        _ecosystems_cycles_foundational_ms_trophic_letter_then_order,
        _ecosystems_cycles_foundational_ms_cycle_pick_then_count,
    ],
    "intermediate": [
        _ecosystems_cycles_intermediate_ms_energy_pct_then_loss_mcq,
        _ecosystems_cycles_intermediate_ms_carbon_order_then_word,
        _ecosystems_cycles_intermediate_ms_equation_pick_then_count,
    ],
    "difficult": [
        _ecosystems_cycles_difficult_ms_web_remove_then_order_then_word,
        _ecosystems_cycles_difficult_ms_carbon_balance_then_mcq_then_pick,
        _ecosystems_cycles_difficult_ms_pyramid_mcq_then_count_then_word,
    ],
}

ECOSYSTEMS_CYCLES_SMS_POOLS = {
    "foundational": [
        _ecosystems_cycles_foundational_sms_pond_producers_then_role_mcq,
        _ecosystems_cycles_foundational_sms_compost_pick_then_count,
        _ecosystems_cycles_foundational_sms_rain_order_then_word,
    ],
    "intermediate": [
        _ecosystems_cycles_intermediate_sms_reserve_rise_then_mcq_then_word,
        _ecosystems_cycles_intermediate_sms_greenhouse_pick_then_order,
        _ecosystems_cycles_intermediate_sms_farm_pct_then_mcq,
    ],
    "difficult": [
        _ecosystems_cycles_difficult_sms_lake_drop_then_order_then_pick,
        _ecosystems_cycles_difficult_sms_rewild_ratio_then_caution_pick_then_verdict,
        _ecosystems_cycles_difficult_sms_documentary_pick_then_model_mcq,
    ],
}


# ---------------------------------------------------------------------------
# ecosystem_characteristics — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CH_MS_F_FACTOR_PACKS = (
    {"items": ("light", "temperature", "grazing by rabbits", "competition for water"), "abiotic": 2},
    {"items": ("soil pH", "rainfall", "predation by owls", "disease"), "abiotic": 2},
    {"items": ("wind", "shade", "pollination by bees", "grazing by sheep"), "abiotic": 2},
)


@_u32_variant("ecosystem_characteristics", "ms", "foundational", "factors_count_then_biotic_mcq")
def _ecosystem_characteristics_foundational_ms_factors_count_then_biotic_mcq():
    pack = random.choice(_CH_MS_F_FACTOR_PACKS)
    correct = "biotic factors: living influences such as feeding or competition"
    distractors = ("abiotic factors: non-living conditions", "a ranking of habitats", "a class survey of homes")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional field-guide card lists: " + ", ".join(pack["items"]) + ".</p>"
        "<p>(i) Enter how many of the four are abiotic factors.</p>"
        "<p>(ii) The factors not counted in (i) are</p>"
    )
    solution = f"(i) <strong>{pack['abiotic']}</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> Non-living = abiotic; living = biotic."
    return (
        question, solution, hint, 2,
        _fields((pack["abiotic"], letter), ("Abiotic factors", "The others are"),
                ("number", "mcq"), (None, options), hint="Count non-living, then choose biotic."),
    )


@_u32_variant("ecosystem_characteristics", "ms", "foundational", "factor_letter_then_order")
def _ecosystem_characteristics_foundational_ms_factor_letter_then_order():
    diagram = str(factor_boxes(title="Fictional factor sketch"))
    order_raw, order_bank = _order(
        ("Choose one factor to measure, such as light", "Measure it the same way at each spot", "Record the readings with units in a table"),
        ("Rank whose back garden is best",),
    )
    question = (
        diagram
        + "<p>A fictional sketch labels A an abiotic factor, B a biotic factor, C a survey.</p>"
        "<p>(i) Enter the letter of the abiotic factor.</p>"
        "<p>(ii) Order how a survey would measure the factor in (i).</p>"
    )
    solution = "(i) <strong>A</strong><br>(ii) <strong>choose factor → measure same way → record with units</strong>"
    hint = "<strong>Key idea:</strong> A is abiotic; choose, measure, record."
    return (
        question, solution, hint, 2,
        _fields(("A", order_raw), ("Abiotic letter", "Survey method"),
                ("keyword", "order"), (None, order_bank), hint="Enter A, then order three steps."),
    )


@_u32_variant("ecosystem_characteristics", "ms", "foundational", "instrument_pick_then_count")
def _ecosystem_characteristics_foundational_ms_instrument_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Thermometer for temperature", "Light meter for light level", "pH strips for soil acidity"),
        ("A private garden photo for the app", "A league of the best habitats"),
        3,
    )
    question = (
        "<p>A fictional teacher-approved field kit list.</p>"
        "<p>(i) Select the three instrument–factor pairs.</p>"
        "<p>(ii) Enter how many pairs you selected in (i).</p>"
    )
    solution = "(i) Thermometer; light meter; pH strips.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Three abiotic factors, three instruments."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Pairs", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_CH_MS_I_SHADE_PACKS = (
    {"sun": 24, "shade": 6, "plant": "daisies"},
    {"sun": 30, "shade": 10, "plant": "clover"},
    {"sun": 18, "shade": 3, "plant": "dandelions"},
)


@_u32_variant("ecosystem_characteristics", "ms", "intermediate", "shade_ratio_then_factor_mcq")
def _ecosystem_characteristics_intermediate_ms_shade_ratio_then_factor_mcq():
    pack = random.choice(_CH_MS_I_SHADE_PACKS)
    ratio = pack["sun"] // pack["shade"]
    correct = "light, an abiotic factor that limits growth in the shade"
    distractors = ("grazing, a biotic factor", "the pupils' gardens", "the quadrat itself")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>Supplied data from a fictional school field: {pack['sun']} {pack['plant']} per "
        f"quadrat in the open, {pack['shade']} under trees.</p>"
        "<p>(i) How many times more plants were counted in the open?</p>"
        "<p>(ii) The most likely factor behind the pattern in (i) is</p>"
    )
    solution = (
        f"(i) {pack['sun']} ÷ {pack['shade']} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then light is the abiotic factor that differs."
    return (
        question, solution, hint, 2,
        _fields((ratio, letter), ("Times more", "Likely factor"),
                ("number", "mcq"), (None, options), hint="Divide, then choose light."),
    )


@_u32_variant("ecosystem_characteristics", "ms", "intermediate", "thermo_order_then_word")
def _ecosystem_characteristics_intermediate_ms_thermo_order_then_word():
    order_raw, order_bank = _order(
        ("The desert lizard's body warms in the morning sun", "It moves into shade when it gets too warm", "Its body temperature stays within a working range"),
        ("The quiz measures each pupil's temperature",),
    )
    question = (
        "<p>A fictional textbook describes a desert lizard's behaviour (a public animal example).</p>"
        "<p>(i) Order the behaviour.</p>"
        "<p>(ii) Write the one-word term for controlling body temperature.</p>"
    )
    solution = "(i) <strong>warms in sun → moves to shade → stays in range</strong><br>(ii) <strong>thermoregulation</strong>"
    hint = "<strong>Key idea:</strong> Behaviour keeps temperature in range."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "thermoregulation"), ("Behaviour", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


@_u32_variant("ecosystem_characteristics", "ms", "intermediate", "model_pick_then_count")
def _ecosystem_characteristics_intermediate_ms_model_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("A trophic model is incomplete, not the whole ecosystem", "A survey is a repeatable count another group could follow"),
        ("This web page replaces a field visit", "The quiz should rank whose backyard is the best habitat"),
        2,
    )
    question = (
        "<p>A fictional revision card lists statements about studying ecosystems.</p>"
        "<p>(i) Select the two correct statements.</p>"
        "<p>(ii) Enter how many statements you selected in (i).</p>"
    )
    solution = "(i) Models are incomplete; surveys are repeatable.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Models simplify; surveys repeat."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 2."),
    )


_CH_MS_D_TRANSECT_PACKS = (
    {"readings": ((0, 800), (5, 400), (10, 100)), "plants": (2, 6, 12)},
    {"readings": ((0, 900), (5, 450), (10, 150)), "plants": (1, 5, 10)},
    {"readings": ((0, 700), (5, 350), (10, 120)), "plants": (3, 7, 14)},
)


@_u32_variant("ecosystem_characteristics", "ms", "difficult", "transect_pattern_then_mcq_then_word")
def _ecosystem_characteristics_difficult_ms_transect_pattern_then_mcq_then_word():
    pack = random.choice(_CH_MS_D_TRANSECT_PACKS)
    r, p = pack["readings"], pack["plants"]
    drop = r[0][1] - r[-1][1]
    correct = "a shade-tolerant plant: more of it where light is lower"
    distractors = ("a plant that needs full sun", "a random pattern with no link", "a ranking of gardens")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>Supplied transect data from a fictional woodland edge: "
        + ", ".join(f"{d} m: light {lx} lux, {n} plants" for (d, lx), n in zip(r, p))
        + ".</p>"
        "<p>(i) Calculate the fall in light from 0 m to 10 m.</p>"
        "<p>(ii) Given the fall in (i) and the plant counts, the species is probably</p>"
        "<p>(iii) Write the one-word name of the line of sample points used here.</p>"
    )
    solution = (
        f"(i) {r[0][1]} − {r[-1][1]} = <strong>{drop}</strong> lux<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>transect</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, read the trend, name the method."
    return (
        question, solution, hint, 3,
        _fields((drop, letter, "transect"), ("Fall in light (lux)", "Species is", "Method"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


@_u32_variant("ecosystem_characteristics", "ms", "difficult", "fair_survey_order_then_pick_then_count")
def _ecosystem_characteristics_difficult_ms_fair_survey_order_then_pick_then_count():
    order_raw, order_bank = _order(
        ("Place quadrats at random or at fixed intervals, not where plants look best", "Count the same way in every quadrat", "Repeat and average before comparing sites"),
        ("Choose the prettiest patch to count",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        ("Abiotic factors are measured with teacher-approved instruments", "Biotic factors include competition and grazing"),
        ("The best habitat is the one with the nicest owner", "One quadrat is enough"),
        2,
    )
    question = (
        "<p>A fictional field-methods sheet explains a fair plant survey.</p>"
        "<p>(i) Order the method.</p>"
        "<p>(ii) Select the two true statements about factors.</p>"
        "<p>(iii) Enter how many quadrat placements the sheet's example uses if it says 'ten per site'.</p>"
    )
    solution = (
        "(i) <strong>random/fixed placement → same counting → repeat and average</strong><br>"
        "(ii) Instruments for abiotic; competition and grazing are biotic.<br>"
        "(iii) <strong>10</strong>"
    )
    hint = "<strong>Key idea:</strong> Unbiased placement, consistent counting, repeats."
    return (
        question, solution, hint, 3,
        _fields((order_raw, pick_raw, 10), ("Method", "Factor statements", "Quadrats per site"),
                ("order", "pick", "number"), (order_bank, pick_bank, None), (None, pick_count, None),
                hint="Order, two statements, then enter 10."),
    )


_CH_MS_D_TEMP_PACKS = (
    {"animal": "a fennec fox", "adaptation": "large ears that lose heat", "biome": "desert"},
    {"animal": "an Arctic fox", "adaptation": "small ears and thick fur that keep heat", "biome": "tundra"},
    {"animal": "a camel", "adaptation": "a hump of fat and a tolerance for temperature swings", "biome": "desert"},
)


@_u32_variant("ecosystem_characteristics", "ms", "difficult", "adaptation_mcq_then_count_then_word")
def _ecosystem_characteristics_difficult_ms_adaptation_mcq_then_count_then_word():
    pack = random.choice(_CH_MS_D_TEMP_PACKS)
    correct = f"an adaptation to the {pack['biome']}'s temperature, an abiotic factor"
    distractors = ("a response to grazing, a biotic factor", "proof the animal ranks other animals", "a random feature with no link")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional textbook describes {pack['animal']} with {pack['adaptation']}.</p>"
        "<p>(i) The feature is best explained as</p>"
        "<p>(ii) Enter how many abiotic factors (temperature, light, water, soil) the lesson lists as a set.</p>"
        "<p>(iii) Write the one-word term for keeping body temperature in range.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>4</strong><br>"
        "(iii) <strong>thermoregulation</strong>"
    )
    hint = "<strong>Key idea:</strong> Adaptation to an abiotic factor; four listed; thermoregulation."
    return (
        question, solution, hint, 3,
        _fields((letter, 4, "thermoregulation"), ("Explained as", "Abiotic factors listed", "Term"),
                ("mcq", "number", "keyword"), (options, None, None),
                hint="Choose, enter 4, then one word."),
    )


# ecosystem_characteristics — situational_multi_step (F, I, D)

_CH_SMS_F_TRIP_PACKS = (
    {"where": "a fictional nature reserve", "readings": 3},
    {"where": "a fictional beach dune", "readings": 4},
    {"where": "a fictional city park", "readings": 3},
)


@_u32_variant("ecosystem_characteristics", "sms", "foundational", "trip_readings_then_abiotic_mcq")
def _ecosystem_characteristics_foundational_sms_trip_readings_then_abiotic_mcq():
    pack = random.choice(_CH_SMS_F_TRIP_PACKS)
    correct = "abiotic factors: non-living conditions"
    distractors = ("biotic factors: living influences", "a ranking of the pupils' gardens", "the reserve's visitors")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>On a fictional class trip to {pack['where']}, a group takes {pack['readings']} "
        "temperature readings with a teacher-approved thermometer.</p>"
        "<p>(i) Enter the number of readings.</p>"
        "<p>(ii) The readings in (i) measure</p>"
    )
    solution = f"(i) <strong>{pack['readings']}</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> Temperature is non-living, so abiotic."
    return (
        question, solution, hint, 2,
        _fields((pack["readings"], letter), ("Readings", "They measure"),
                ("number", "mcq"), (None, options), hint="Count, then choose abiotic."),
    )


@_u32_variant("ecosystem_characteristics", "sms", "foundational", "rockpool_pick_then_count")
def _ecosystem_characteristics_foundational_sms_rockpool_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Salt level and temperature are abiotic factors", "Crabs eating snails is a biotic factor"),
        ("This web page replaces the visit", "The best rockpool belongs to the nicest family"),
        2,
    )
    question = (
        "<p>A fictional seaside field-centre sheet describes a rockpool.</p>"
        "<p>(i) Select the two correct statements.</p>"
        "<p>(ii) Enter how many kinds of factor (abiotic, biotic) appear in (i).</p>"
    )
    solution = "(i) Abiotic salt/temperature; biotic feeding.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Two factor kinds."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Factor kinds"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 2."),
    )


@_u32_variant("ecosystem_characteristics", "sms", "foundational", "meadow_order_then_word")
def _ecosystem_characteristics_foundational_sms_meadow_order_then_word():
    order_raw, order_bank = _order(
        ("Throw the quadrat at random points across the meadow", "Count the plants inside each quadrat", "Write the counts in a table with units"),
        ("Photograph each pupil's garden",),
    )
    question = (
        "<p>A fictional wildlife-trust volunteer shows a class how to survey a meadow.</p>"
        "<p>(i) Order the survey.</p>"
        "<p>(ii) Write the one-word name of the square frame used.</p>"
    )
    solution = "(i) <strong>random throws → count → record</strong><br>(ii) <strong>quadrat</strong>"
    hint = "<strong>Key idea:</strong> Random placement, count, record."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "quadrat"), ("Survey", "Frame"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_CH_SMS_I_RIVER_PACKS = (
    {"river": "a fictional chalk stream", "up": 12, "down": 3, "factor": "oxygen"},
    {"river": "a fictional mill river", "up": 15, "down": 5, "factor": "oxygen"},
    {"river": "a fictional moorland beck", "up": 9, "down": 3, "factor": "oxygen"},
)


@_u32_variant("ecosystem_characteristics", "sms", "intermediate", "river_ratio_then_mcq_then_word")
def _ecosystem_characteristics_intermediate_sms_river_ratio_then_mcq_then_word():
    pack = random.choice(_CH_SMS_I_RIVER_PACKS)
    ratio = pack["up"] // pack["down"]
    correct = f"an abiotic factor such as {pack['factor']} level differs between the two sites"
    distractors = ("the downstream pupils counted worse", "mayflies rank the sites", "the river creates insects")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional river-monitoring group counts mayfly larvae in {pack['river']}: "
        f"{pack['up']} per sample upstream of a town, {pack['down']} downstream.</p>"
        "<p>(i) How many times more larvae were found upstream?</p>"
        "<p>(ii) A likely explanation of (i) is that</p>"
        "<p>(iii) Write the one-word term for a species whose presence indicates water quality.</p>"
    )
    solution = (
        f"(i) {pack['up']} ÷ {pack['down']} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>indicator</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, link to an abiotic factor, name indicator species."
    return (
        question, solution, hint, 3,
        _fields((ratio, letter, "indicator"), ("Times more", "Explanation", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Divide, choose, then one word."),
    )


_CH_SMS_I_ZOO_PACKS = (
    {"animal": "a fictional zoo's meerkats", "behaviour": "basking in the morning and sheltering at noon"},
    {"animal": "a fictional wildlife park's tortoises", "behaviour": "moving between sun and shade through the day"},
    {"animal": "a fictional aquarium's iguanas", "behaviour": "sitting under a heat lamp then retreating"},
)


@_u32_variant("ecosystem_characteristics", "sms", "intermediate", "zoo_pick_then_order")
def _ecosystem_characteristics_intermediate_sms_zoo_pick_then_order():
    pack = random.choice(_CH_SMS_I_ZOO_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("The animals use behaviour to control body temperature", "Temperature is an abiotic factor they respond to"),
        ("The keepers rank pupils by warmth", "The animals create heat from nothing"),
        2,
    )
    order_raw, order_bank = _order(
        ("Body temperature falls overnight", "The animal basks to warm up", "It moves to shade before it overheats"),
        ("It stays in full sun all day",),
    )
    question = (
        f"<p>A keeper's talk describes {pack['animal']} {pack['behaviour']}.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the first statement from (i), order a day's behaviour.</p>"
    )
    solution = (
        "(i) Behavioural thermoregulation; temperature is abiotic.<br>"
        "(ii) <strong>cool overnight → bask → shade</strong>"
    )
    hint = "<strong>Key idea:</strong> Behaviour regulates temperature."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "A day's behaviour"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_CH_SMS_I_DUNE_PACKS = (
    {"where": "a fictional sand dune", "front": 2, "back": 9},
    {"where": "a fictional salt marsh", "front": 3, "back": 12},
    {"where": "a fictional quarry edge", "front": 1, "back": 8},
)


@_u32_variant("ecosystem_characteristics", "sms", "intermediate", "dune_species_then_mcq")
def _ecosystem_characteristics_intermediate_sms_dune_species_then_mcq():
    pack = random.choice(_CH_SMS_I_DUNE_PACKS)
    diff = pack["back"] - pack["front"]
    correct = "abiotic conditions change along the transect, so more species can survive further back"
    distractors = ("the back is where the nicest gardens are", "species are created by the transect", "the pupils counted better at the back")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional field-centre transect across {pack['where']} records {pack['front']} "
        f"plant species at the front and {pack['back']} at the back.</p>"
        "<p>(i) Calculate the increase in species along the transect.</p>"
        "<p>(ii) The increase in (i) is explained by</p>"
    )
    solution = (
        f"(i) {pack['back']} − {pack['front']} = <strong>{diff}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then changing abiotic conditions."
    return (
        question, solution, hint, 2,
        _fields((diff, letter), ("Increase", "Explained by"),
                ("number", "mcq"), (None, options), hint="Subtract, then choose the abiotic idea."),
    )


_CH_SMS_D_STUDY_PACKS = (
    {"study": "a fictional wildlife-trust study", "sites": 20, "grazed": 10, "species_grazed": 22, "species_ungrazed": 14},
    {"study": "a fictional national-park survey", "sites": 16, "grazed": 8, "species_grazed": 18, "species_ungrazed": 12},
    {"study": "a fictional university field project", "sites": 24, "grazed": 12, "species_grazed": 26, "species_ungrazed": 17},
)


@_u32_variant("ecosystem_characteristics", "sms", "difficult", "grazing_gap_then_caution_pick_then_verdict")
def _ecosystem_characteristics_difficult_sms_grazing_gap_then_caution_pick_then_verdict():
    pack = random.choice(_CH_SMS_D_STUDY_PACKS)
    gap = pack["species_grazed"] - pack["species_ungrazed"]
    pick_raw, pick_bank, pick_count = _pick(
        ("Sites may differ in abiotic factors such as soil or drainage", "Species counts depend on survey effort being equal"),
        ("Grazing creates species from nothing", "The result ranks the landowners"),
        2,
    )
    correct = "light grazing (a biotic factor) is associated with more plant species here, within the study's limits"
    distractors = ("grazing always increases biodiversity everywhere", "the ungrazed sites were surveyed wrongly", "the sheep planted the extra species")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['study'].capitalize()} compares {pack['grazed']} lightly grazed meadows "
        f"({pack['species_grazed']} plant species on average) with {pack['sites'] - pack['grazed']} "
        f"ungrazed meadows ({pack['species_ungrazed']}).</p>"
        "<p>(i) Calculate the difference in average species count.</p>"
        "<p>(ii) Using the difference from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['species_grazed']} − {pack['species_ungrazed']} = <strong>{gap}</strong><br>"
        "(ii) Abiotic differences; equal effort.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, cautions, then 'associated with'."
    return (
        question, solution, hint, 3,
        _fields((gap, pick_raw, letter), ("Difference", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Subtract, two cautions, then the verdict."),
    )


_CH_SMS_D_HEAT_PACKS = (
    {"city": "a fictional city", "park": 24, "street": 31},
    {"city": "a fictional port town", "park": 22, "street": 28},
    {"city": "a fictional capital", "park": 26, "street": 34},
)


@_u32_variant("ecosystem_characteristics", "sms", "difficult", "heat_island_diff_then_order_then_word")
def _ecosystem_characteristics_difficult_sms_heat_island_diff_then_order_then_word():
    pack = random.choice(_CH_SMS_D_HEAT_PACKS)
    diff = pack["street"] - pack["park"]
    order_raw, order_bank = _order(
        ("Measure temperature at matched times in park and street", "Compare the abiotic readings between the two habitats", "Relate the difference to which organisms live in each"),
        ("Rank the residents by how hot their homes are",),
    )
    question = (
        f"<p>A public climate report for {pack['city']}: afternoon temperature {pack['park']} °C "
        f"in a large park, {pack['street']} °C in a paved street.</p>"
        "<p>(i) Calculate the temperature difference.</p>"
        "<p>(ii) Order how an ecologist would use the difference in (i).</p>"
        "<p>(iii) Write the one-word class of factor temperature belongs to.</p>"
    )
    solution = (
        f"(i) {pack['street']} − {pack['park']} = <strong>{diff}</strong> °C<br>"
        "(ii) <strong>measure matched → compare habitats → relate to organisms</strong><br>"
        "(iii) <strong>abiotic</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, compare habitats, abiotic factor."
    return (
        question, solution, hint, 3,
        _fields((diff, order_raw, "abiotic"), ("Difference (°C)", "Ecologist's method", "Factor class"),
                ("number", "order", "keyword"), (None, order_bank, None),
                hint="Subtract, order three steps, then one word."),
    )


@_u32_variant("ecosystem_characteristics", "sms", "difficult", "model_pick_then_limit_mcq")
def _ecosystem_characteristics_difficult_sms_model_pick_then_limit_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("A trophic model leaves out many species and factors", "Predictions from a model should be checked against field data"),
        ("A model is the whole ecosystem", "The model ranks pupils as animals"),
        2,
    )
    correct = "treat the app's prediction as a hypothesis to test with a real survey, not as fact"
    distractors = ("accept it because the app is popular", "rank habitats by the app's score", "skip fieldwork entirely")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional ecology app predicts which species a habitat 'should' contain from "
        "a few abiotic readings.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), a class should</p>"
    )
    solution = (
        "(i) Models omit things; check predictions.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Models are hypotheses to test."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "The class should"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the approach."),
    )


ECOSYSTEM_CHARACTERISTICS_MS_POOLS = {
    "foundational": [
        _ecosystem_characteristics_foundational_ms_factors_count_then_biotic_mcq,
        _ecosystem_characteristics_foundational_ms_factor_letter_then_order,
        _ecosystem_characteristics_foundational_ms_instrument_pick_then_count,
    ],
    "intermediate": [
        _ecosystem_characteristics_intermediate_ms_shade_ratio_then_factor_mcq,
        _ecosystem_characteristics_intermediate_ms_thermo_order_then_word,
        _ecosystem_characteristics_intermediate_ms_model_pick_then_count,
    ],
    "difficult": [
        _ecosystem_characteristics_difficult_ms_transect_pattern_then_mcq_then_word,
        _ecosystem_characteristics_difficult_ms_fair_survey_order_then_pick_then_count,
        _ecosystem_characteristics_difficult_ms_adaptation_mcq_then_count_then_word,
    ],
}

ECOSYSTEM_CHARACTERISTICS_SMS_POOLS = {
    "foundational": [
        _ecosystem_characteristics_foundational_sms_trip_readings_then_abiotic_mcq,
        _ecosystem_characteristics_foundational_sms_rockpool_pick_then_count,
        _ecosystem_characteristics_foundational_sms_meadow_order_then_word,
    ],
    "intermediate": [
        _ecosystem_characteristics_intermediate_sms_river_ratio_then_mcq_then_word,
        _ecosystem_characteristics_intermediate_sms_zoo_pick_then_order,
        _ecosystem_characteristics_intermediate_sms_dune_species_then_mcq,
    ],
    "difficult": [
        _ecosystem_characteristics_difficult_sms_grazing_gap_then_caution_pick_then_verdict,
        _ecosystem_characteristics_difficult_sms_heat_island_diff_then_order_then_word,
        _ecosystem_characteristics_difficult_sms_model_pick_then_limit_mcq,
    ],
}


# ---------------------------------------------------------------------------
# classification_biodiversity — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CL_MS_F_KEY_PACKS = (
    {"q1": "Does it have wings?", "q2": "Does it have six legs?", "answer": "insect", "n": 2},
    {"q1": "Does it have a backbone?", "q2": "Does it have feathers?", "answer": "bird", "n": 2},
    {"q1": "Does it have leaves?", "q2": "Does it have flowers?", "answer": "flowering plant", "n": 2},
)


@_u32_variant("classification_biodiversity", "ms", "foundational", "key_couplets_then_feature_mcq")
def _classification_biodiversity_foundational_ms_key_couplets_then_feature_mcq():
    pack = random.choice(_CL_MS_F_KEY_PACKS)
    correct = "one checkable feature at a time, with a yes/no answer"
    distractors = ("a guess at the animal's name", "a ranking of pupils' pets", "a private home collection")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional dichotomous key: 1. {pack['q1']} 2. {pack['q2']} → {pack['answer']}.</p>"
        "<p>(i) Enter the number of couplets (questions) in the key.</p>"
        "<p>(ii) Each couplet in (i) asks</p>"
    )
    solution = f"(i) <strong>{pack['n']}</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> Count couplets; each is one yes/no feature."
    return (
        question, solution, hint, 2,
        _fields((pack["n"], letter), ("Couplets", "Each asks"),
                ("number", "mcq"), (None, options), hint="Count, then choose the couplet idea."),
    )


@_u32_variant("classification_biodiversity", "ms", "foundational", "key_letter_then_order")
def _classification_biodiversity_foundational_ms_key_letter_then_order():
    diagram = str(key_boxes(title="Fictional key sketch"))
    order_raw, order_bank = _order(
        ("Answer the first couplet", "Follow the branch to the second couplet", "Arrive at a named group another pupil could reach"),
        ("Guess the name from the picture",),
    )
    question = (
        diagram
        + "<p>A fictional key sketch labels A first couplet, B second couplet, C named group.</p>"
        "<p>(i) Enter the letter of the named group.</p>"
        "<p>(ii) Order how a key reaches the box in (i).</p>"
    )
    solution = "(i) <strong>C</strong><br>(ii) <strong>first couplet → second couplet → named group</strong>"
    hint = "<strong>Key idea:</strong> C is the end; couplets lead there."
    return (
        question, solution, hint, 2,
        _fields(("C", order_raw), ("Named-group letter", "How a key works"),
                ("keyword", "order"), (None, order_bank), hint="Enter C, then order three steps."),
    )


@_u32_variant("classification_biodiversity", "ms", "foundational", "group_pick_then_count")
def _classification_biodiversity_foundational_ms_group_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Mammals", "Birds", "Insects"),
        ("Pupils' pets ranked by cuteness", "A private home collection"),
        3,
    )
    question = (
        "<p>A fictional museum panel lists broad animal groups.</p>"
        "<p>(i) Select the three animal groups.</p>"
        "<p>(ii) Enter how many groups you selected in (i).</p>"
    )
    solution = "(i) Mammals; birds; insects.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Three broad groups."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Groups", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_CL_MS_I_SPECIES_PACKS = (
    {"habitat": "a fictional hedgerow", "before": 40, "after": 25},
    {"habitat": "a fictional wetland", "before": 60, "after": 45},
    {"habitat": "a fictional meadow", "before": 35, "after": 21},
)


@_u32_variant("classification_biodiversity", "ms", "intermediate", "species_loss_then_meaning_mcq")
def _classification_biodiversity_intermediate_ms_species_loss_then_meaning_mcq():
    pack = random.choice(_CL_MS_I_SPECIES_PACKS)
    loss = pack["before"] - pack["after"]
    correct = "a fall in biodiversity, linked in public evidence to habitat change"
    distractors = ("species being created elsewhere", "a ranking of the surveyors", "proof the key was wrong")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional public survey of {pack['habitat']}: {pack['before']} species "
        f"recorded twenty years ago, {pack['after']} now.</p>"
        "<p>(i) Calculate the number of species lost.</p>"
        "<p>(ii) The loss in (i) is</p>"
    )
    solution = (
        f"(i) {pack['before']} − {pack['after']} = <strong>{loss}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract; fewer species means lower biodiversity."
    return (
        question, solution, hint, 2,
        _fields((loss, letter), ("Species lost", "The loss is"),
                ("number", "mcq"), (None, options), hint="Subtract, then choose biodiversity."),
    )


@_u32_variant("classification_biodiversity", "ms", "intermediate", "linnaeus_order_then_word")
def _classification_biodiversity_intermediate_ms_linnaeus_order_then_word():
    order_raw, order_bank = _order(
        ("Kingdom: the broadest group", "Genus: a group of closely related species", "Species: organisms that can breed and produce fertile offspring"),
        ("Pet: the most popular group in class",),
    )
    question = (
        "<p>A fictional textbook page on Linnaeus's grouping system.</p>"
        "<p>(i) Order from broadest to narrowest.</p>"
        "<p>(ii) Write the one-word name for this grouping science.</p>"
    )
    solution = "(i) <strong>kingdom → genus → species</strong><br>(ii) <strong>taxonomy</strong>"
    hint = "<strong>Key idea:</strong> Broad to narrow; taxonomy."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "taxonomy"), ("Broad to narrow", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three ranks, then one word."),
    )


@_u32_variant("classification_biodiversity", "ms", "intermediate", "feature_pick_then_count")
def _classification_biodiversity_intermediate_ms_feature_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Number of legs", "Presence of a backbone", "Type of body covering"),
        ("How much a pupil likes it", "Where a pupil's family keeps it"),
        3,
    )
    question = (
        "<p>A fictional worksheet asks which features make good key couplets.</p>"
        "<p>(i) Select the three checkable features.</p>"
        "<p>(ii) Enter how many features you selected in (i).</p>"
    )
    solution = "(i) Legs; backbone; covering.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Checkable, observable features only."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Features", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_CL_MS_D_DESCENT_PACKS = (
    {"pair": ("humans", "chimpanzees"), "shared": 98},
    {"pair": ("horses", "donkeys"), "shared": 95},
    {"pair": ("wolves", "dogs"), "shared": 99},
)


@_u32_variant("classification_biodiversity", "ms", "difficult", "descent_pct_then_mcq_then_word")
def _classification_biodiversity_difficult_ms_descent_pct_then_mcq_then_word():
    pack = random.choice(_CL_MS_D_DESCENT_PACKS)
    diff = 100 - pack["shared"]
    correct = "common descent: the two share a more recent ancestor than distant groups do"
    distractors = ("one species turned into the other last year", "a ranking of which pupil is most related to an ape", "the key was wrong")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional textbook says {pack['pair'][0]} and {pack['pair'][1]} share about "
        f"{pack['shared']}% of a compared set of genes (public teaching figure).</p>"
        "<p>(i) Calculate the percentage that differs.</p>"
        "<p>(ii) The high shared figure behind (i) is explained by</p>"
        "<p>(iii) Write the one-word grouping science that places them in related groups.</p>"
    )
    solution = (
        f"(i) 100 − {pack['shared']} = <strong>{diff}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>taxonomy</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then common descent, then taxonomy."
    return (
        question, solution, hint, 3,
        _fields((diff, letter, "taxonomy"), ("Differs (%)", "Explained by", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


@_u32_variant("classification_biodiversity", "ms", "difficult", "key_build_order_then_pick_then_count")
def _classification_biodiversity_difficult_ms_key_build_order_then_pick_then_count():
    order_raw, order_bank = _order(
        ("Choose a feature that splits the set into two clear groups", "Write it as a yes/no couplet", "Repeat until every organism reaches its own named group"),
        ("Ask which one the class likes best",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        ("A dichotomous key asks one checkable feature at a time", "The key ends in a named group another pupil could reach"),
        ("The quiz should harvest a private home collection", "A key ranks organisms by beauty"),
        2,
    )
    question = (
        "<p>A fictional biology club builds a key for six supplied leaf specimens.</p>"
        "<p>(i) Order the building method.</p>"
        "<p>(ii) Select the two rules a good key follows.</p>"
        "<p>(iii) Enter the minimum number of couplets needed to separate six specimens.</p>"
    )
    solution = (
        "(i) <strong>choose splitting feature → write couplet → repeat to named groups</strong><br>"
        "(ii) One feature at a time; ends in a named group.<br>"
        "(iii) <strong>5</strong>"
    )
    hint = "<strong>Key idea:</strong> Each couplet separates one group; n specimens need n − 1 couplets."
    return (
        question, solution, hint, 3,
        _fields((order_raw, pick_raw, 5), ("Method", "Rules", "Minimum couplets"),
                ("order", "pick", "number"), (order_bank, pick_bank, None), (None, pick_count, None),
                hint="Order, two rules, then enter 5."),
    )


_CL_MS_D_LOSS_PACKS = (
    {"cause": "habitat loss to farming", "n": 3},
    {"cause": "pollution of rivers", "n": 3},
    {"cause": "climate change shifting ranges", "n": 3},
)


@_u32_variant("classification_biodiversity", "ms", "difficult", "loss_mcq_then_count_then_word")
def _classification_biodiversity_difficult_ms_loss_mcq_then_count_then_word():
    pack = random.choice(_CL_MS_D_LOSS_PACKS)
    correct = "a driver of biodiversity loss supported by public evidence, discussed as a system-level issue"
    distractors = ("a reason to rank families", "proof species are created elsewhere", "an advert")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional public report names {pack['cause']} among {pack['n']} main drivers "
        "of species loss.</p>"
        "<p>(i) In this lesson the named cause is</p>"
        "<p>(ii) Enter how many main drivers the report names.</p>"
        "<p>(iii) Write the one-word term for the variety of living things in an area.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        f"(ii) <strong>{pack['n']}</strong><br>"
        "(iii) <strong>biodiversity</strong>"
    )
    hint = "<strong>Key idea:</strong> Public driver, count, biodiversity."
    return (
        question, solution, hint, 3,
        _fields((letter, pack["n"], "biodiversity"), ("The cause is", "Drivers", "Term"),
                ("mcq", "number", "keyword"), (options, None, None),
                hint="Choose, count, then one word."),
    )


# classification_biodiversity — situational_multi_step (F, I, D)

_CL_SMS_F_MUSEUM_PACKS = (
    {"where": "a fictional natural-history museum", "specimens": 4},
    {"where": "a fictional botanic garden", "specimens": 5},
    {"where": "a fictional field-centre lab", "specimens": 3},
)


@_u32_variant("classification_biodiversity", "sms", "foundational", "museum_specimens_then_key_mcq")
def _classification_biodiversity_foundational_sms_museum_specimens_then_key_mcq():
    pack = random.choice(_CL_SMS_F_MUSEUM_PACKS)
    correct = "a dichotomous key that asks one checkable feature at a time"
    distractors = ("a guess from the label colour", "a ranking of pupils' pets", "a private collection list")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>On a fictional class visit to {pack['where']}, a guide hands out "
        f"{pack['specimens']} labelled specimens to identify.</p>"
        "<p>(i) Enter the number of specimens.</p>"
        "<p>(ii) To identify the specimens in (i), the class uses</p>"
    )
    solution = f"(i) <strong>{pack['specimens']}</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> Count, then use a key."
    return (
        question, solution, hint, 2,
        _fields((pack["specimens"], letter), ("Specimens", "The class uses"),
                ("number", "mcq"), (None, options), hint="Count, then choose the key."),
    )


@_u32_variant("classification_biodiversity", "sms", "foundational", "garden_pick_then_count")
def _classification_biodiversity_foundational_sms_garden_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Counting species in a public park is a biodiversity measure", "Grouping uses checkable features"),
        ("The best garden belongs to the richest family", "The quiz should harvest a private home collection"),
        2,
    )
    question = (
        "<p>A fictional park ranger runs a public 'count the species' day.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Enter how many statements you selected in (i).</p>"
    )
    solution = "(i) Species counts measure biodiversity; grouping uses features.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Public counts, checkable features."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Statements", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 2."),
    )


@_u32_variant("classification_biodiversity", "sms", "foundational", "beetle_order_then_word")
def _classification_biodiversity_foundational_sms_beetle_order_then_word():
    order_raw, order_bank = _order(
        ("Does it have six legs? Yes", "Does it have hard wing cases? Yes", "It is a beetle"),
        ("Does the class like it? Yes",),
    )
    question = (
        "<p>A fictional field-guide app walks a visitor through a key for a small animal.</p>"
        "<p>(i) Order the steps.</p>"
        "<p>(ii) Write the one-word broad group the first couplet in (i) points to.</p>"
    )
    solution = "(i) <strong>six legs → wing cases → beetle</strong><br>(ii) <strong>insect</strong>"
    hint = "<strong>Key idea:</strong> Six legs means insect; wing cases narrow to beetle."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "insect"), ("Steps", "Broad group"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_CL_SMS_I_SURVEY_PACKS = (
    {"reserve": "a fictional wetland reserve", "y1": 30, "y2": 42, "action": "reed-bed restoration"},
    {"reserve": "a fictional urban nature park", "y1": 18, "y2": 27, "action": "wildflower planting"},
    {"reserve": "a fictional coastal reserve", "y1": 25, "y2": 35, "action": "dune fencing"},
)


@_u32_variant("classification_biodiversity", "sms", "intermediate", "survey_gain_then_mcq_then_word")
def _classification_biodiversity_intermediate_sms_survey_gain_then_mcq_then_word():
    pack = random.choice(_CL_SMS_I_SURVEY_PACKS)
    gain = pack["y2"] - pack["y1"]
    correct = "biodiversity rose after the habitat action, within the limits of a two-year comparison"
    distractors = ("species were created by the volunteers", "the reserve ranks its visitors", "the key produced extra species")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional public survey of {pack['reserve']}: {pack['y1']} bird species before "
        f"{pack['action']}, {pack['y2']} two years after.</p>"
        "<p>(i) Calculate the gain in species.</p>"
        "<p>(ii) The gain in (i) suggests that</p>"
        "<p>(iii) Write the one-word term for the variety of species measured.</p>"
    )
    solution = (
        f"(i) {pack['y2']} − {pack['y1']} = <strong>{gain}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>biodiversity</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, cautious reading, biodiversity."
    return (
        question, solution, hint, 3,
        _fields((gain, letter, "biodiversity"), ("Gain", "Suggests", "Term"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Subtract, choose, then one word."),
    )


_CL_SMS_I_APP_PACKS = (
    {"who": "Riley", "app": "a fictional plant-ID app", "specimen": "a leaf"},
    {"who": "Casey", "app": "a fictional bird-call app", "specimen": "a recording"},
    {"who": "Morgan", "app": "a fictional insect-ID app", "specimen": "a photo"},
)


@_u32_variant("classification_biodiversity", "sms", "intermediate", "app_pick_then_order")
def _classification_biodiversity_intermediate_sms_app_pick_then_order():
    pack = random.choice(_CL_SMS_I_APP_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("An app's suggestion is a hypothesis to check with a key", "Checkable features decide the group, not the app's confidence score"),
        ("The app is always right", f"{pack['who']} should upload a private home collection"),
        2,
    )
    order_raw, order_bank = _order(
        ("Note the app's suggestion", "Check the checkable features with a key", "Accept or reject the suggestion on the evidence"),
        ("Rank classmates by how many species they own",),
    )
    question = (
        f"<p>In a fictional case, {pack['who']} uses {pack['app']} on {pack['specimen']} "
        "during a field trip.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the first statement from (i), order the checking method.</p>"
    )
    solution = (
        "(i) A hypothesis to check; features decide.<br>"
        "(ii) <strong>note suggestion → check with key → accept or reject</strong>"
    )
    hint = "<strong>Key idea:</strong> Apps suggest; keys check."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Statements", "Checking method"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two statements, then order three steps."),
    )


_CL_SMS_I_ISLAND_PACKS = (
    {"island": "a fictional island", "mainland": 120, "island_n": 30},
    {"island": "a fictional volcanic island", "mainland": 200, "island_n": 40},
    {"island": "a fictional lake island", "mainland": 90, "island_n": 30},
)


@_u32_variant("classification_biodiversity", "sms", "intermediate", "island_ratio_then_mcq")
def _classification_biodiversity_intermediate_sms_island_ratio_then_mcq():
    pack = random.choice(_CL_SMS_I_ISLAND_PACKS)
    ratio = pack["mainland"] // pack["island_n"]
    correct = "smaller, more isolated areas usually hold fewer species — a public pattern in biodiversity"
    distractors = ("islands create species from nothing", "the island's surveyors were worse", "the mainland ranks the island")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional biogeography table: {pack['mainland']} beetle species on the mainland, "
        f"{pack['island_n']} on {pack['island']} nearby.</p>"
        "<p>(i) How many times more species does the mainland hold?</p>"
        "<p>(ii) The ratio in (i) illustrates that</p>"
    )
    solution = (
        f"(i) {pack['mainland']} ÷ {pack['island_n']} = <strong>{ratio}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Divide, then area and isolation shape biodiversity."
    return (
        question, solution, hint, 2,
        _fields((ratio, letter), ("Times more", "Illustrates"),
                ("number", "mcq"), (None, options), hint="Divide, then choose the pattern."),
    )


_CL_SMS_D_CITIZEN_PACKS = (
    {"scheme": "a fictional national garden-bird count", "records": 5000, "checked": 4500},
    {"scheme": "a fictional butterfly-count app", "records": 8000, "checked": 7200},
    {"scheme": "a fictional river-life survey", "records": 2000, "checked": 1700},
)


@_u32_variant("classification_biodiversity", "sms", "difficult", "citizen_pct_then_caution_pick_then_verdict")
def _classification_biodiversity_difficult_sms_citizen_pct_then_caution_pick_then_verdict():
    pack = random.choice(_CL_SMS_D_CITIZEN_PACKS)
    pct = _pct(pack["checked"], pack["records"])
    pick_raw, pick_bank, pick_count = _pick(
        ("Volunteer identifications need checking against keys or experts", "Records cluster where people live, so coverage is uneven"),
        ("Volunteers should be ranked by garden size", "Every record is automatically correct"),
        2,
    )
    correct = "the scheme gives useful public biodiversity data once records are verified and coverage is accounted for"
    distractors = ("the scheme proves biodiversity rose everywhere", "unverified records are as good as verified ones", "the scheme should map each volunteer's address")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['scheme'].capitalize()} received {pack['records']} public records; "
        f"{pack['checked']} passed expert verification.</p>"
        "<p>(i) Calculate the percentage verified (whole number).</p>"
        "<p>(ii) Using the figure from (i), select the two cautions.</p>"
        "<p>(iii) Given (ii), the fair verdict is that</p>"
    )
    solution = (
        f"(i) {pack['checked']} ÷ {pack['records']} × 100 = <strong>{pct}%</strong><br>"
        "(ii) Verification; uneven coverage.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage, then verification and coverage."
    return (
        question, solution, hint, 3,
        _fields((pct, pick_raw, letter), ("Verified (%)", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Percentage, two cautions, then the verdict."),
    )


_CL_SMS_D_FOSSIL_PACKS = (
    {"museum": "a fictional museum", "fossil": "an early whale ancestor with small hind legs"},
    {"museum": "a fictional university collection", "fossil": "a feathered dinosaur"},
    {"museum": "a fictional geology centre", "fossil": "an early horse with several toes"},
)


@_u32_variant("classification_biodiversity", "sms", "difficult", "fossil_order_then_word_then_count")
def _classification_biodiversity_difficult_sms_fossil_order_then_word_then_count():
    pack = random.choice(_CL_SMS_D_FOSSIL_PACKS)
    order_raw, order_bank = _order(
        ("Compare the fossil's features with living groups", "Place it on a branching family tree by shared features", "Treat the placement as a scientific model open to revision"),
        ("Rank pupils by how related they are to the fossil",),
    )
    question = (
        f"<p>{pack['museum'].capitalize()} displays {pack['fossil']}.</p>"
        "<p>(i) Order how scientists classify it.</p>"
        "<p>(ii) Write the one-word idea that living groups share ancestors: common ______.</p>"
        "<p>(iii) Enter how many steps the method in (i) has.</p>"
    )
    solution = (
        "(i) <strong>compare features → place on tree → treat as model</strong><br>"
        "(ii) <strong>descent</strong><br>"
        "(iii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Shared features, branching tree, common descent."
    return (
        question, solution, hint, 3,
        _fields((order_raw, "descent", 3), ("Method", "Term", "Steps"),
                ("order", "keyword", "number"), (order_bank, None, None),
                hint="Order three steps, one word, then enter 3."),
    )


@_u32_variant("classification_biodiversity", "sms", "difficult", "policy_pick_then_choice_mcq")
def _classification_biodiversity_difficult_sms_policy_pick_then_choice_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("Biodiversity loss is linked to public evidence on habitat change", "Protected areas and habitat corridors are system-level responses"),
        ("Families should be ranked by garden wildlife", "Species can be created to replace lost ones"),
        2,
    )
    correct = "evaluate the plan with public survey data before and after, at the level of the whole area"
    distractors = ("rank households by wildlife", "assume the plan works because it sounds green", "count only the prettiest species")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional council consults on a biodiversity action plan.</p>"
        "<p>(i) Select the two scientific statements.</p>"
        "<p>(ii) Using the second statement from (i), a fair way to judge the plan is to</p>"
    )
    solution = (
        "(i) Public evidence of loss; system-level responses.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Public data, whole-area evaluation."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Fair judgement"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the method."),
    )


CLASSIFICATION_BIODIVERSITY_MS_POOLS = {
    "foundational": [
        _classification_biodiversity_foundational_ms_key_couplets_then_feature_mcq,
        _classification_biodiversity_foundational_ms_key_letter_then_order,
        _classification_biodiversity_foundational_ms_group_pick_then_count,
    ],
    "intermediate": [
        _classification_biodiversity_intermediate_ms_species_loss_then_meaning_mcq,
        _classification_biodiversity_intermediate_ms_linnaeus_order_then_word,
        _classification_biodiversity_intermediate_ms_feature_pick_then_count,
    ],
    "difficult": [
        _classification_biodiversity_difficult_ms_descent_pct_then_mcq_then_word,
        _classification_biodiversity_difficult_ms_key_build_order_then_pick_then_count,
        _classification_biodiversity_difficult_ms_loss_mcq_then_count_then_word,
    ],
}

CLASSIFICATION_BIODIVERSITY_SMS_POOLS = {
    "foundational": [
        _classification_biodiversity_foundational_sms_museum_specimens_then_key_mcq,
        _classification_biodiversity_foundational_sms_garden_pick_then_count,
        _classification_biodiversity_foundational_sms_beetle_order_then_word,
    ],
    "intermediate": [
        _classification_biodiversity_intermediate_sms_survey_gain_then_mcq_then_word,
        _classification_biodiversity_intermediate_sms_app_pick_then_order,
        _classification_biodiversity_intermediate_sms_island_ratio_then_mcq,
    ],
    "difficult": [
        _classification_biodiversity_difficult_sms_citizen_pct_then_caution_pick_then_verdict,
        _classification_biodiversity_difficult_sms_fossil_order_then_word_then_count,
        _classification_biodiversity_difficult_sms_policy_pick_then_choice_mcq,
    ],
}


# ---------------------------------------------------------------------------
# ecology_field_project — multi_step (F, I, D); situational (F, I, D).
# Grades question, risk, sampling, records, analysis and reflection only.
# ---------------------------------------------------------------------------

_FP_MS_F_Q_PACKS = (
    {"q": "How does shade affect daisy counts on the school lawn?", "n": 1},
    {"q": "Do more woodlice live under logs than under stones in the school grounds?", "n": 1},
    {"q": "Is moss cover higher on the north side of the school wall?", "n": 1},
)


@_u32_variant("ecology_field_project", "ms", "foundational", "question_then_testable_mcq")
def _ecology_field_project_foundational_ms_question_then_testable_mcq():
    pack = random.choice(_FP_MS_F_Q_PACKS)
    correct = "another group could test it with a count or measurement"
    distractors = ("it ranks whose garden plot is best", "it needs a private home-garden upload", "it replaces the field visit")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional team writes the field question: '{pack['q']}'.</p>"
        "<p>(i) Enter the number of variables being compared (shade/no shade, log/stone, north/other).</p>"
        "<p>(ii) The question in (i) is a good field question because</p>"
    )
    solution = f"(i) <strong>{pack['n']}</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> One comparison; testable by another group."
    return (
        question, solution, hint, 2,
        _fields((pack["n"], letter), ("Variables compared", "Good because"),
                ("number", "mcq"), (None, options), hint="Enter 1, then choose testability."),
    )


@_u32_variant("ecology_field_project", "ms", "foundational", "phases_order_then_word")
def _ecology_field_project_foundational_ms_phases_order_then_word():
    order_raw, order_bank = _order(
        ("Write a field question another group could test", "Plan risk with the teacher's assessment", "Choose a sampling idea such as a quadrat the teacher approves"),
        ("Upload private home-garden photos to the app",),
    )
    question = (
        "<p>A fictional project board shows the planning phases of a field study.</p>"
        "<p>(i) Order the phases.</p>"
        "<p>(ii) Write the one-word sampling frame named in step 3 of (i).</p>"
    )
    solution = "(i) <strong>question → risk → sampling</strong><br>(ii) <strong>quadrat</strong>"
    hint = "<strong>Key idea:</strong> Question, risk, sampling."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "quadrat"), ("Phases", "Frame"),
                ("order", "keyword"), (order_bank, None), hint="Order three phases, then one word."),
    )


@_u32_variant("ecology_field_project", "ms", "foundational", "record_pick_then_count")
def _ecology_field_project_foundational_ms_record_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Record a method another group could repeat, with units", "Analyse the pattern with numbers from the table", "Present and reflect on what was found"),
        ("Rank whose garden plot is best", "Upload private home-garden photos to the app"),
        3,
    )
    question = (
        "<p>A fictional field-study rubric lists what is graded.</p>"
        "<p>(i) Select the three graded items.</p>"
        "<p>(ii) Enter how many items you selected in (i).</p>"
    )
    solution = "(i) Method; analysis; presentation and reflection.<br>(ii) <strong>3</strong>"
    hint = "<strong>Key idea:</strong> Method, analysis, reflection — not the plot."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 3), ("Graded items", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Select three, then enter 3."),
    )


_FP_MS_I_DATA_PACKS = (
    {"sun": (12, 14, 10), "shade": (4, 6, 5)},
    {"sun": (20, 18, 22), "shade": (8, 6, 7)},
    {"sun": (9, 11, 10), "shade": (2, 4, 3)},
)


@_u32_variant("ecology_field_project", "ms", "intermediate", "mean_then_conclusion_mcq")
def _ecology_field_project_intermediate_ms_mean_then_conclusion_mcq():
    pack = random.choice(_FP_MS_I_DATA_PACKS)
    mean_sun = sum(pack["sun"]) // 3
    mean_shade = sum(pack["shade"]) // 3
    correct = "more plants were counted in the open than in shade in this study; repeats would strengthen it"
    distractors = ("shade creates plants", "the study proves it for every lawn on Earth", "the counts show the quadrat is broken")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>Supplied data from a fictional team: open quadrats {', '.join(map(str, pack['sun']))}; "
        f"shaded quadrats {', '.join(map(str, pack['shade']))} plants.</p>"
        "<p>(i) Calculate the mean count for the open quadrats.</p>"
        f"<p>(ii) Comparing (i) with the shade mean of {mean_shade}, the fair conclusion is that</p>"
    )
    solution = (
        f"(i) ({' + '.join(map(str, pack['sun']))}) ÷ 3 = <strong>{mean_sun}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Mean of three, then a cautious comparison."
    return (
        question, solution, hint, 2,
        _fields((mean_sun, letter), ("Open mean", "Fair conclusion"),
                ("number", "mcq"), (None, options), hint="Average, then choose the cautious reading."),
    )


@_u32_variant("ecology_field_project", "ms", "intermediate", "risk_order_then_word")
def _ecology_field_project_intermediate_ms_risk_order_then_word():
    order_raw, order_bank = _order(
        ("Identify hazards at the site, such as water or uneven ground", "Decide controls, such as boundaries and pairs", "Check the plan against the teacher's risk assessment"),
        ("Skip the check because the site looks safe",),
    )
    question = (
        "<p>A fictional planning sheet covers safety for a pond-dipping study.</p>"
        "<p>(i) Order the risk planning.</p>"
        "<p>(ii) Write the one-word term for the teacher's document in step 3 of (i): risk ______.</p>"
    )
    solution = "(i) <strong>identify hazards → decide controls → check with assessment</strong><br>(ii) <strong>assessment</strong>"
    hint = "<strong>Key idea:</strong> Hazards, controls, assessment."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "assessment"), ("Risk planning", "Term"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


@_u32_variant("ecology_field_project", "ms", "intermediate", "sampling_pick_then_count")
def _ecology_field_project_intermediate_ms_sampling_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Place quadrats at random, not where plants look best", "Use the same quadrat size at every point"),
        ("Count only the prettiest patch", "Sample each pupil's own garden"),
        2,
    )
    question = (
        "<p>A fictional sampling-methods card lists rules for a fair survey.</p>"
        "<p>(i) Select the two fair-sampling rules.</p>"
        "<p>(ii) Enter how many rules you selected in (i).</p>"
    )
    solution = "(i) Random placement; same size.<br>(ii) <strong>2</strong>"
    hint = "<strong>Key idea:</strong> Random and consistent."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 2), ("Rules", "Number selected"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two rules, then enter 2."),
    )


_FP_MS_D_PCT_PACKS = (
    {"quadrats": 10, "with": 7, "species": "clover"},
    {"quadrats": 8, "with": 2, "species": "moss"},
    {"quadrats": 12, "with": 9, "species": "plantain"},
)


@_u32_variant("ecology_field_project", "ms", "difficult", "frequency_pct_then_mcq_then_word")
def _ecology_field_project_difficult_ms_frequency_pct_then_mcq_then_word():
    pack = random.choice(_FP_MS_D_PCT_PACKS)
    pct = _pct(pack["with"], pack["quadrats"])
    correct = "a frequency: the share of quadrats containing the species, which another group could repeat"
    distractors = ("a ranking of the team's gardens", "proof of the total number of plants on Earth", "a guess")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>Supplied data from a fictional field study: {pack['species']} was present in {pack['with']} of "
        f"{pack['quadrats']} random quadrats.</p>"
        "<p>(i) Calculate the percentage of quadrats containing the species.</p>"
        "<p>(ii) The figure in (i) is</p>"
        "<p>(iii) Write the one-word term for the square sampling frame used.</p>"
    )
    solution = (
        f"(i) {pack['with']} ÷ {pack['quadrats']} × 100 = <strong>{pct}%</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>quadrat</strong>"
    )
    hint = "<strong>Key idea:</strong> Percentage frequency; repeatable method."
    return (
        question, solution, hint, 3,
        _fields((pct, letter, "quadrat"), ("Frequency (%)", "The figure is", "Frame"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Percentage, choose, then one word."),
    )


@_u32_variant("ecology_field_project", "ms", "difficult", "analysis_order_then_pick_then_count")
def _ecology_field_project_difficult_ms_analysis_order_then_pick_then_count():
    order_raw, order_bank = _order(
        ("Put the counts in a table with units", "Calculate means for each condition", "Compare the means and state what they suggest, with limits"),
        ("Declare the result true for every site",),
    )
    pick_raw, pick_bank, pick_count = _pick(
        ("Present and reflect; the field product is not auto-graded here", "Record a method another group could repeat"),
        ("Upload private home-garden photos", "Rank whose garden plot is best"),
        2,
    )
    question = (
        "<p>A fictional rubric describes the analysis phase.</p>"
        "<p>(i) Order the analysis.</p>"
        "<p>(ii) Select the two rubric statements.</p>"
        "<p>(iii) Enter how many conditions a shade-versus-open comparison has.</p>"
    )
    solution = (
        "(i) <strong>table → means → compare with limits</strong><br>"
        "(ii) Reflect, not auto-graded; repeatable method.<br>"
        "(iii) <strong>2</strong>"
    )
    hint = "<strong>Key idea:</strong> Table, means, cautious comparison."
    return (
        question, solution, hint, 3,
        _fields((order_raw, pick_raw, 2), ("Analysis", "Rubric statements", "Conditions"),
                ("order", "pick", "number"), (order_bank, pick_bank, None), (None, pick_count, None),
                hint="Order, two statements, then enter 2."),
    )


_FP_MS_D_FLAW_PACKS = (
    {"flaw": "all shaded quadrats were placed under one tree", "n": 3},
    {"flaw": "counts were taken at different times of day", "n": 3},
    {"flaw": "two team members counted using different rules", "n": 3},
)


@_u32_variant("ecology_field_project", "ms", "difficult", "flaw_mcq_then_count_then_word")
def _ecology_field_project_difficult_ms_flaw_mcq_then_count_then_word():
    pack = random.choice(_FP_MS_D_FLAW_PACKS)
    correct = "a method flaw to record in the reflection and fix in a repeat"
    distractors = ("a reason to rank the team", "proof the site is bad", "something to hide in the write-up")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>A fictional team's reflection notes that {pack['flaw']}.</p>"
        "<p>(i) In the rubric this is</p>"
        "<p>(ii) Enter how many phases (question, risk, sampling) the planning stage has.</p>"
        "<p>(iii) Write the one-word rubric phase where such notes belong.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        f"(ii) <strong>{pack['n']}</strong><br>"
        "(iii) <strong>reflection</strong>"
    )
    hint = "<strong>Key idea:</strong> Flaws are reflected on, not hidden."
    return (
        question, solution, hint, 3,
        _fields((letter, pack["n"], "reflection"), ("This is", "Planning phases", "Phase"),
                ("mcq", "number", "keyword"), (options, None, None),
                hint="Choose, enter 3, then one word."),
    )


# ecology_field_project — situational_multi_step (F, I, D)

_FP_SMS_F_TEAM_PACKS = (
    {"team": "Team Heron (fictional)", "site": "the school pond", "quadrats": 6},
    {"team": "Team Beetle (fictional)", "site": "the playing-field edge", "quadrats": 8},
    {"team": "Team Lichen (fictional)", "site": "the school wall", "quadrats": 5},
)


@_u32_variant("ecology_field_project", "sms", "foundational", "team_quadrats_then_first_mcq")
def _ecology_field_project_foundational_sms_team_quadrats_then_first_mcq():
    pack = random.choice(_FP_SMS_F_TEAM_PACKS)
    correct = "write a field question another group could test"
    distractors = ("upload private garden photos", "rank the other teams' plots", "skip the risk assessment")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['team']} plans to sample {pack['site']} with {pack['quadrats']} quadrats.</p>"
        "<p>(i) Enter the number of quadrats planned.</p>"
        "<p>(ii) Before placing the quadrats in (i), the team's first phase is to</p>"
    )
    solution = f"(i) <strong>{pack['quadrats']}</strong><br>(ii) <strong>{correct}</strong>"
    hint = "<strong>Key idea:</strong> Question first."
    return (
        question, solution, hint, 2,
        _fields((pack["quadrats"], letter), ("Quadrats", "First phase"),
                ("number", "mcq"), (None, options), hint="Count, then choose the question."),
    )


@_u32_variant("ecology_field_project", "sms", "foundational", "field_day_pick_then_count")
def _ecology_field_project_foundational_sms_field_day_pick_then_count():
    pick_raw, pick_bank, pick_count = _pick(
        ("Field time needs the class, kit and the teacher's risk assessment", "The field product is graded in class with a rubric"),
        ("This web page replaces the field visit", "The app stores whose plot is best"),
        2,
    )
    question = (
        "<p>A fictional field-centre notice explains how the project day works.</p>"
        "<p>(i) Select the two statements consistent with the notice.</p>"
        "<p>(ii) Enter how many field products this app auto-grades as finished work.</p>"
    )
    solution = "(i) Class field time; rubric in class.<br>(ii) <strong>0</strong>"
    hint = "<strong>Key idea:</strong> Practical in the field; this page grades planning."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, 0), ("Statements", "Products auto-graded"),
                ("pick", "number"), (pick_bank, None), (pick_count, None),
                hint="Two statements, then enter 0."),
    )


@_u32_variant("ecology_field_project", "sms", "foundational", "pond_dip_order_then_word")
def _ecology_field_project_foundational_sms_pond_dip_order_then_word():
    order_raw, order_bank = _order(
        ("Sweep the net the same way each time", "Tip the catch into a tray and identify with a key", "Record the counts in a table"),
        ("Photograph each pupil's garden pond",),
    )
    question = (
        "<p>A fictional ranger demonstrates pond dipping to a class.</p>"
        "<p>(i) Order the method.</p>"
        "<p>(ii) Write the one-word tool used to identify the catch in step 2 of (i).</p>"
    )
    solution = "(i) <strong>sweep → identify → record</strong><br>(ii) <strong>key</strong>"
    hint = "<strong>Key idea:</strong> Consistent sweep, key, record."
    return (
        question, solution, hint, 2,
        _fields((order_raw, "key"), ("Method", "Tool"),
                ("order", "keyword"), (order_bank, None), hint="Order three steps, then one word."),
    )


_FP_SMS_I_LOG_PACKS = (
    {"team": "Team Heron (fictional)", "logs": (9, 11, 10), "stones": (3, 2, 4)},
    {"team": "Team Beetle (fictional)", "logs": (14, 12, 16), "stones": (5, 7, 6)},
    {"team": "Team Lichen (fictional)", "logs": (6, 8, 7), "stones": (1, 3, 2)},
)


@_u32_variant("ecology_field_project", "sms", "intermediate", "woodlice_mean_then_mcq_then_word")
def _ecology_field_project_intermediate_sms_woodlice_mean_then_mcq_then_word():
    pack = random.choice(_FP_SMS_I_LOG_PACKS)
    mean_logs = sum(pack["logs"]) // 3
    mean_stones = sum(pack["stones"]) // 3
    correct = "woodlice were more common under logs in this study; a possible link to moisture, a factor to test next"
    distractors = ("logs create woodlice", "the team's garden is best", "stones repel all animals")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['team']} counts woodlice: under logs {', '.join(map(str, pack['logs']))}; "
        f"under stones {', '.join(map(str, pack['stones']))}.</p>"
        "<p>(i) Calculate the mean count under logs.</p>"
        f"<p>(ii) Comparing (i) with the stone mean of {mean_stones}, a fair conclusion is that</p>"
        "<p>(iii) Write the one-word term for the non-living condition (moisture) suggested.</p>"
    )
    solution = (
        f"(i) ({' + '.join(map(str, pack['logs']))}) ÷ 3 = <strong>{mean_logs}</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>abiotic</strong>"
    )
    hint = "<strong>Key idea:</strong> Mean, cautious comparison, abiotic factor."
    return (
        question, solution, hint, 3,
        _fields((mean_logs, letter, "abiotic"), ("Log mean", "Fair conclusion", "Factor class"),
                ("number", "mcq", "keyword"), (None, options, None),
                hint="Average, choose, then one word."),
    )


_FP_SMS_I_RISK_PACKS = (
    {"team": "Team Heron (fictional)", "site": "a stream bank"},
    {"team": "Team Beetle (fictional)", "site": "a quarry edge"},
    {"team": "Team Lichen (fictional)", "site": "a coastal path"},
)


@_u32_variant("ecology_field_project", "sms", "intermediate", "risk_pick_then_order")
def _ecology_field_project_intermediate_sms_risk_pick_then_order():
    pack = random.choice(_FP_SMS_I_RISK_PACKS)
    pick_raw, pick_bank, pick_count = _pick(
        ("Hazards are identified before the visit", "Controls follow the teacher's risk assessment"),
        ("Risk is ignored if the site looks pretty", "Pupils sample their own gardens instead"),
        2,
    )
    order_raw, order_bank = _order(
        (f"List the hazards of {pack['site']}", "Agree boundaries and work in pairs", "Get the plan approved before the visit"),
        ("Go alone to save time",),
    )
    question = (
        f"<p>{pack['team']} wants to sample {pack['site']}.</p>"
        "<p>(i) Select the two rules that apply.</p>"
        "<p>(ii) Using the approval rule from (i), order the risk planning.</p>"
    )
    solution = (
        "(i) Identify hazards; controls per assessment.<br>"
        "(ii) <strong>list hazards → boundaries and pairs → approval</strong>"
    )
    hint = "<strong>Key idea:</strong> Hazards, controls, approval."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, order_raw), ("Rules", "Risk planning"),
                ("pick", "order"), (pick_bank, order_bank), (pick_count, None),
                hint="Two rules, then order three steps."),
    )


_FP_SMS_I_LICHEN_PACKS = (
    {"team": "Team Lichen (fictional)", "busy": 2, "quiet": 7},
    {"team": "Team Heron (fictional)", "busy": 3, "quiet": 9},
    {"team": "Team Beetle (fictional)", "busy": 1, "quiet": 5},
)


@_u32_variant("ecology_field_project", "sms", "intermediate", "lichen_diff_then_mcq")
def _ecology_field_project_intermediate_sms_lichen_diff_then_mcq():
    pack = random.choice(_FP_SMS_I_LICHEN_PACKS)
    diff = pack["quiet"] - pack["busy"]
    correct = "lichen types differ between the sites; air quality (an abiotic factor) is a hypothesis to test"
    distractors = ("the busy road creates lichens", "the team should rank the streets' residents", "the count proves the cause")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['team']} counts lichen types on trees: {pack['busy']} by a busy road, "
        f"{pack['quiet']} in a quiet park (school-grounds study).</p>"
        "<p>(i) Calculate the difference in lichen types.</p>"
        "<p>(ii) A fair reading of (i) is that</p>"
    )
    solution = (
        f"(i) {pack['quiet']} − {pack['busy']} = <strong>{diff}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, then hypothesis not proof."
    return (
        question, solution, hint, 2,
        _fields((diff, letter), ("Difference", "Fair reading"),
                ("number", "mcq"), (None, options), hint="Subtract, then choose the hypothesis reading."),
    )


_FP_SMS_D_REPEAT_PACKS = (
    {"team": "Team Heron (fictional)", "year1": 12, "year2": 18, "quadrats": 10},
    {"team": "Team Beetle (fictional)", "year1": 20, "year2": 26, "quadrats": 12},
    {"team": "Team Lichen (fictional)", "year1": 8, "year2": 14, "quadrats": 8},
)


@_u32_variant("ecology_field_project", "sms", "difficult", "repeat_gain_then_caution_pick_then_verdict")
def _ecology_field_project_difficult_sms_repeat_gain_then_caution_pick_then_verdict():
    pack = random.choice(_FP_SMS_D_REPEAT_PACKS)
    gain = pack["year2"] - pack["year1"]
    pick_raw, pick_bank, pick_count = _pick(
        ("Weather and season may differ between the two years", "Different pupils counting may use slightly different rules"),
        ("The gain proves the wildflower area caused it", "The team's gardens should be ranked"),
        2,
    )
    correct = "species rose after the wildflower planting in this study; the link needs more repeats and a control area"
    distractors = ("the planting created species", "the first count was wrong", "the result applies to every school")
    options, letter = _mcq(correct, distractors)
    question = (
        f"<p>{pack['team']} repeats a school-grounds survey a year after a wildflower "
        f"area was planted: {pack['year1']} species in {pack['quadrats']} quadrats before, "
        f"{pack['year2']} after.</p>"
        "<p>(i) Calculate the gain in species.</p>"
        "<p>(ii) Using the gain from (i), select the two cautions for the reflection.</p>"
        "<p>(iii) Given (ii), the fair verdict for the write-up is that</p>"
    )
    solution = (
        f"(i) {pack['year2']} − {pack['year1']} = <strong>{gain}</strong><br>"
        "(ii) Weather/season; counting rules.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Subtract, cautions, then a cautious verdict."
    return (
        question, solution, hint, 3,
        _fields((gain, pick_raw, letter), ("Gain", "Cautions", "Verdict"),
                ("number", "pick", "mcq"), (None, pick_bank, options), (None, pick_count, None),
                hint="Subtract, two cautions, then the verdict."),
    )


_FP_SMS_D_METHOD_PACKS = (
    {"team": "Team Heron (fictional)", "problem": "counting daisies only in the greenest patches"},
    {"team": "Team Beetle (fictional)", "problem": "using a different quadrat size at each site"},
    {"team": "Team Lichen (fictional)", "problem": "sampling the busy road at noon and the park at dusk"},
)


@_u32_variant("ecology_field_project", "sms", "difficult", "method_fix_order_then_word_then_count")
def _ecology_field_project_difficult_sms_method_fix_order_then_word_then_count():
    pack = random.choice(_FP_SMS_D_METHOD_PACKS)
    order_raw, order_bank = _order(
        ("Name the flaw in the reflection", "Change the method so another group could repeat it fairly", "Repeat the sampling and compare with the first run"),
        ("Delete the first data set and say nothing",),
    )
    question = (
        f"<p>{pack['team']} realises they were {pack['problem']}.</p>"
        "<p>(i) Order how the rubric expects them to respond.</p>"
        "<p>(ii) Write the one-word rubric phase in step 1 of (i).</p>"
        "<p>(iii) Enter how many steps the response in (i) has.</p>"
    )
    solution = (
        "(i) <strong>name the flaw → fix the method → repeat and compare</strong><br>"
        "(ii) <strong>reflection</strong><br>"
        "(iii) <strong>3</strong>"
    )
    hint = "<strong>Key idea:</strong> Own the flaw, fix, repeat."
    return (
        question, solution, hint, 3,
        _fields((order_raw, "reflection", 3), ("Response", "Phase", "Steps"),
                ("order", "keyword", "number"), (order_bank, None, None),
                hint="Order three steps, one word, then enter 3."),
    )


@_u32_variant("ecology_field_project", "sms", "difficult", "judge_pick_then_grading_mcq")
def _ecology_field_project_difficult_sms_judge_pick_then_grading_mcq():
    pick_raw, pick_bank, pick_count = _pick(
        ("Judges look for a testable question, a repeatable method and honest reflection", "Records with units and a clear analysis matter more than a dramatic result"),
        ("Judges rank pupils' gardens", "Home-garden photos are required"),
        2,
    )
    correct = "question, risk plan, sampling, records, analysis and reflection; fieldwork itself is judged in class"
    distractors = ("only the biggest species count", "a private garden upload", "whose family helped most")
    options, letter = _mcq(correct, distractors)
    question = (
        "<p>A fictional judging guide for a school ecology fair is published for all teams.</p>"
        "<p>(i) Select the two statements consistent with the guide.</p>"
        "<p>(ii) Using the first statement from (i), this app's part of the grade covers</p>"
    )
    solution = (
        "(i) Testable, repeatable, honest; records over drama.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = "<strong>Key idea:</strong> Process and evidence graded; fieldwork stays in class."
    return (
        question, solution, hint, 2,
        _fields((pick_raw, letter), ("Statements", "Grade covers"),
                ("pick", "mcq"), (pick_bank, options), (pick_count, None),
                hint="Two statements, then the scope."),
    )


ECOLOGY_FIELD_PROJECT_MS_POOLS = {
    "foundational": [
        _ecology_field_project_foundational_ms_question_then_testable_mcq,
        _ecology_field_project_foundational_ms_phases_order_then_word,
        _ecology_field_project_foundational_ms_record_pick_then_count,
    ],
    "intermediate": [
        _ecology_field_project_intermediate_ms_mean_then_conclusion_mcq,
        _ecology_field_project_intermediate_ms_risk_order_then_word,
        _ecology_field_project_intermediate_ms_sampling_pick_then_count,
    ],
    "difficult": [
        _ecology_field_project_difficult_ms_frequency_pct_then_mcq_then_word,
        _ecology_field_project_difficult_ms_analysis_order_then_pick_then_count,
        _ecology_field_project_difficult_ms_flaw_mcq_then_count_then_word,
    ],
}

ECOLOGY_FIELD_PROJECT_SMS_POOLS = {
    "foundational": [
        _ecology_field_project_foundational_sms_team_quadrats_then_first_mcq,
        _ecology_field_project_foundational_sms_field_day_pick_then_count,
        _ecology_field_project_foundational_sms_pond_dip_order_then_word,
    ],
    "intermediate": [
        _ecology_field_project_intermediate_sms_woodlice_mean_then_mcq_then_word,
        _ecology_field_project_intermediate_sms_risk_pick_then_order,
        _ecology_field_project_intermediate_sms_lichen_diff_then_mcq,
    ],
    "difficult": [
        _ecology_field_project_difficult_sms_repeat_gain_then_caution_pick_then_verdict,
        _ecology_field_project_difficult_sms_method_fix_order_then_word_then_count,
        _ecology_field_project_difficult_sms_judge_pick_then_grading_mcq,
    ],
}
