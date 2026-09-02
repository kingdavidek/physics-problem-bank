"""S1 Unit 1.1 advanced Practice pools (MS / SMS). Isolated from lesson banks.

Blueprints and curated packs (topic × tier × mode), three each:

measurement SMS
  F  harbour_km_compare | sample_mass_lid_kg | field_kit_ruler_mm
  I  reserve_two_legs | pond_temp_mean_range | corridor_prefix_join
  D  field_kit_zero | survey_precise_not_accurate | calibrate_then_kg
what_is_science MS (no foundational — matrix F MS is —)
  I  count_evidence_then_reproduce | mean_times_then_public | order_enquiry_then_peer
  D  groups_then_hypothesis | order_check_then_method_keep | anecdote_then_count_evidence
what_is_science SMS
  F  club_claim_then_test | museum_repeat_groups | poster_ad_not_evidence
  I  club_enquiry_then_share | two_group_mean_critique | book_then_provisional
  D  fair_hypothesis_groups_check | anecdote_vs_table | secret_method_share
science_lab MS
  F  temps_mean_then_instrument | plan_order_then_independent | safety_pick_then_count
  I  mean_time_then_dependent | draw_order_then_error_reduce | range_then_control
  D  full_plan_order_then_three_vars | range_then_repeat_mean | control_list_then_safety
science_lab SMS
  F  heat_water_mean_then_thermo | heat_water_plan_then_indep | heat_water_safety_then_count
  I  salt_time_mean_then_dep | salt_draw_then_error | salt_range_then_control
  D  fair_test_plan_then_vars | fair_test_range_mean | fair_test_control_then_safety
"""
import random

from generators.eursc.science_shared import accuracy_targets, lab_bench, ruler_scale
from generators.shared.utils import graded_answer_number_fields, make_graded_problem
from models.svg_kit import bar_chart

_LEVEL = "eursc"
_SUBJECT = "science"


def _u11_variant(topic, mode_tag, difficulty, suffix):
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


def _u11_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _u11_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    raw = f"1|{'|'.join(step_ids)}"
    return raw, bank


def _u11_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f"c{i + 1}" for i in range(len(correct_texts)))
    bank = [{"id": cid, "text": text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    raw = f"pick|{pick_count}|{'|'.join(correct_ids)}"
    return raw, bank, pick_count


def _listed(values):
    return ", ".join(f"{v:g}" for v in values)


# ---------------------------------------------------------------------------
# measurement — situational_multi_step (MS packs stay in s1_science_lab.py)
# ---------------------------------------------------------------------------

_MEAS_SMS_F_HARBOUR_PACKS = (
    {"who": "Riley", "place": "harbour boardwalk", "km": 1, "other_m": 250},
    {"who": "Casey", "place": "museum gallery", "km": 5, "other_m": 900},
    {"who": "Morgan", "place": "rooftop garden path", "km": 6, "other_m": 2200},
)


@_u11_variant("measurement", "sms", "foundational", "harbour_km_compare")
def _measurement_foundational_sms_harbour_km_compare():
    pack = random.choice(_MEAS_SMS_F_HARBOUR_PACKS)
    metres = pack["km"] * 1000
    extra = metres - pack["other_m"]
    question = (
        f"<p>In a fictional city survey, {pack['who']} records a "
        f"{pack['place']} as {pack['km']} km on a public map.</p>"
        "<p>(i) Convert that length to metres.</p>"
        f"<p>(ii) A painted marker is {pack['other_m']} m. How many metres "
        f"longer is {pack['who']}'s recorded path?</p>"
    )
    solution = (
        f"(i) {pack['km']} km = {pack['km']} × 1000 = "
        f"<strong>{metres}</strong> m<br>"
        f"(ii) {metres} − {pack['other_m']} = <strong>{extra}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> Convert the kilometre reading first, then "
        "subtract using that metre value."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (metres, extra),
            ("Length (m)", "Difference (m)"),
            format_hint="Convert kilometres to metres, then subtract.",
        ),
    )


_MEAS_SMS_F_MASS_PACKS = (
    {"who": "Alex", "sample": "dried clay", "mass_g": 250, "lid_g": 50},
    {"who": "Sam", "sample": "sand sample", "mass_g": 400, "lid_g": 100},
    {"who": "Jordan", "sample": "salt crystals", "mass_g": 750, "lid_g": 250},
)


@_u11_variant("measurement", "sms", "foundational", "sample_mass_lid_kg")
def _measurement_foundational_sms_sample_mass_lid_kg():
    pack = random.choice(_MEAS_SMS_F_MASS_PACKS)
    total_g = pack["mass_g"] + pack["lid_g"]
    kg = total_g / 1000
    question = (
        f"<p>In a fictional field kit, {pack['who']} records a "
        f"{pack['sample']} as {pack['mass_g']} g, then adds a lid of "
        f"{pack['lid_g']} g.</p>"
        + str(lab_bench(title="Fictional field-kit bench"))
        + "<p>(i) What is the combined mass in grams?</p>"
        "<p>(ii) Convert that combined mass to kilograms.</p>"
    )
    solution = (
        f"(i) {pack['mass_g']} + {pack['lid_g']} = "
        f"<strong>{total_g}</strong> g<br>"
        f"(ii) {total_g} ÷ 1000 = <strong>{kg:g}</strong> kg"
    )
    hint = (
        "<strong>Key idea:</strong> Add the two gram readings, then convert "
        "that total: 1 kg = 1000 g."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (total_g, kg),
            ("Combined mass (g)", "Combined mass (kg)"),
            format_hint="Add the gram values, then divide by 1000.",
        ),
    )


_MEAS_SMS_F_RULER_PACKS = (
    {"who": "Riley", "cm": 3.2, "foam_mm": 4},
    {"who": "Casey", "cm": 5.5, "foam_mm": 5},
    {"who": "Morgan", "cm": 7.2, "foam_mm": 9},
)


@_u11_variant("measurement", "sms", "foundational", "field_kit_ruler_mm")
def _measurement_foundational_sms_field_kit_ruler_mm():
    pack = random.choice(_MEAS_SMS_F_RULER_PACKS)
    mm = pack["cm"] * 10
    total = mm + pack["foam_mm"]
    question = (
        f"<p>In a fictional field kit, {pack['who']} measures a rock sample "
        "on this centimetre scale, then adds packing foam.</p>"
        + str(ruler_scale(pack["cm"], title="Pointer on a centimetre field-kit scale"))
        + "<p>(i) What is the reading in millimetres?</p>"
        f"<p>(ii) Packing foam adds {pack['foam_mm']} mm. What is the packed "
        "length in millimetres?</p>"
    )
    solution = (
        f"(i) {pack['cm']:g} cm × 10 = <strong>{mm:g}</strong> mm<br>"
        f"(ii) {mm:g} + {pack['foam_mm']} = <strong>{total:g}</strong> mm"
    )
    hint = (
        "<strong>Key idea:</strong> Read the scale, convert centimetres to "
        "millimetres, then add the foam using that millimetre value."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mm, total),
            ("Reading (mm)", "Packed length (mm)"),
            format_hint="Multiply the centimetre reading by 10, then add.",
        ),
    )


_MEAS_SMS_I_LEGS_PACKS = (
    {"place": "nature-reserve transect", "a": "north leg", "b": "east leg", "a_cm": 180, "b_cm": 60},
    {"place": "wetland boardwalk", "a": "inlet span", "b": "spur", "a_cm": 500, "b_cm": 125},
    {"place": "quarry survey line", "a": "ridge tape", "b": "offset", "a_cm": 360, "b_cm": 90},
)


@_u11_variant("measurement", "sms", "intermediate", "reserve_two_legs")
def _measurement_intermediate_sms_reserve_two_legs():
    pack = random.choice(_MEAS_SMS_I_LEGS_PACKS)
    a_m = pack["a_cm"] / 100
    b_m = pack["b_cm"] / 100
    diff = a_m - b_m
    question = (
        f"<p>A fictional {pack['place']} records two tape readings:</p>"
        f"<ul><li>{pack['a']}: {pack['a_cm']} cm</li>"
        f"<li>{pack['b']}: {pack['b_cm']} cm</li></ul>"
        f"<p>(i) Convert the {pack['a']} to metres.</p>"
        f"<p>(ii) Convert the {pack['b']} to metres.</p>"
        "<p>(iii) How many metres longer is the first leg?</p>"
    )
    solution = (
        f"(i) {pack['a_cm']} cm = <strong>{a_m:g}</strong> m<br>"
        f"(ii) {pack['b_cm']} cm = <strong>{b_m:g}</strong> m<br>"
        f"(iii) {a_m:g} − {b_m:g} = <strong>{diff:g}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> Convert both centimetre tapes to metres, "
        "then subtract using those two results."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (a_m, b_m, diff),
            ("First length (m)", "Second length (m)", "Difference (m)"),
            format_hint="Divide each centimetre value by 100, then subtract.",
        ),
    )


_MEAS_SMS_I_POND_PACKS = (
    {"place": "fictional pond station", "readings": (18, 20, 22, 19, 21)},
    {"place": "fictional canal lock", "readings": (12, 14, 16, 13, 15)},
    {"place": "fictional greenhouse tank", "readings": (24, 26, 25, 23, 27)},
)


@_u11_variant("measurement", "sms", "intermediate", "pond_temp_mean_range")
def _measurement_intermediate_sms_pond_temp_mean_range():
    pack = random.choice(_MEAS_SMS_I_POND_PACKS)
    readings = pack["readings"]
    mean = sum(readings) / len(readings)
    spread = max(readings) - min(readings)
    labels = [str(i) for i in range(1, len(readings) + 1)]
    listed = _listed(readings)
    question = (
        f"<p>Five temperature repeats at a {pack['place']}, in °C: {listed}.</p>"
        + str(
            bar_chart(
                labels,
                list(readings),
                title="Five fictional water-temperature readings in degrees Celsius",
                desc=f"Bar chart of five temperature readings in degrees Celsius: {listed}.",
            )
        )
        + "<p>(i) Find the mean temperature in °C.</p>"
        "<p>(ii) Using the same five readings, what is the range in °C?</p>"
    )
    solution = (
        f"(i) sum = {sum(readings):g}; mean = {sum(readings):g} / "
        f"{len(readings)} = <strong>{mean:g}</strong> °C<br>"
        f"(ii) {max(readings):g} − {min(readings):g} = "
        f"<strong>{spread:g}</strong> °C"
    )
    hint = (
        "<strong>Key idea:</strong> The mean uses all five readings; the range "
        "uses the largest and smallest of that same set."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mean, spread),
            ("Mean temperature (°C)", "Range (°C)"),
            format_hint="Divide the total by 5, then subtract smallest from largest.",
        ),
    )


_MEAS_SMS_I_PREFIX_PACKS = (
    {"place": "service corridor", "km": 0.001, "extra_mm": 100},
    {"place": "loading bay", "km": 0.006, "extra_mm": 300},
    {"place": "glasshouse aisle", "km": 0.008, "extra_mm": 400},
)


@_u11_variant("measurement", "sms", "intermediate", "corridor_prefix_join")
def _measurement_intermediate_sms_corridor_prefix_join():
    pack = random.choice(_MEAS_SMS_I_PREFIX_PACKS)
    metres = pack["km"] * 1000
    mm = metres * 1000
    total = mm + pack["extra_mm"]
    question = (
        f"<p>A fictional {pack['place']} is logged as {pack['km']} km.</p>"
        "<p>(i) Convert that length to metres.</p>"
        "<p>(ii) Convert the length in metres from (i) to millimetres.</p>"
        f"<p>(iii) A joining strip adds {pack['extra_mm']} mm. What is the "
        "total length in millimetres?</p>"
    )
    solution = (
        f"(i) {pack['km']} km = <strong>{metres:g}</strong> m<br>"
        f"(ii) {metres:g} × 1000 = <strong>{mm:g}</strong> mm<br>"
        f"(iii) {mm:g} + {pack['extra_mm']} = <strong>{total:g}</strong> mm"
    )
    hint = (
        "<strong>Key idea:</strong> Go km → m → mm, then add the strip to the "
        "millimetre value from (ii)."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (metres, mm, total),
            ("Length (m)", "Length (mm)", "Total length (mm)"),
            format_hint="Convert through metres, then add the extra millimetres.",
        ),
    )


_MEAS_SMS_D_ZERO_PACKS = (
    {"who": "Alex", "empty": 4, "loaded": 44},
    {"who": "Sam", "empty": 5, "loaded": 85},
    {"who": "Jordan", "empty": 6, "loaded": 206},
)


@_u11_variant("measurement", "sms", "difficult", "field_kit_zero")
def _measurement_difficult_sms_field_kit_zero():
    pack = random.choice(_MEAS_SMS_D_ZERO_PACKS)
    corrected = pack["loaded"] - pack["empty"]
    kg = corrected / 1000
    correct = "a systematic zero error; the field balance needs calibration"
    distractors = (
        "a random error from a single breeze",
        "evidence that grams are not SI units",
        "a conversion error from kilometres",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional field kit, {pack['who']}'s portable balance reads "
        f"{pack['empty']} g when the pan is empty. After a sample is placed "
        f"on the pan, the display shows {pack['loaded']} g.</p>"
        "<p>(i) What is the corrected mass in grams?</p>"
        "<p>(ii) Convert that corrected mass to kilograms.</p>"
        "<p>(iii) The empty-pan offset is mainly</p>"
    )
    solution = (
        f"(i) {pack['loaded']} − {pack['empty']} = "
        f"<strong>{corrected}</strong> g<br>"
        f"(ii) {corrected} ÷ 1000 = <strong>{kg:g}</strong> kg<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the empty reading, convert grams "
        "to kilograms, then treat a built-in offset as systematic."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (corrected, kg, letter),
            ("Corrected mass (g)", "Corrected mass (kg)", "Type of error"),
            field_types=("number", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Subtract the empty reading, convert to kg, then choose.",
        ),
    )


_MEAS_SMS_D_PRECISE_PACKS = (
    {"item": "survey stake", "readings": (14.4, 14.6, 14.4, 14.6), "true": 12.0},
    {"item": "marker post", "readings": (9.0, 9.2, 9.0, 9.2), "true": 11.0},
    {"item": "grid peg", "readings": (21.0, 21.2, 21.0, 21.2), "true": 18.0},
)


@_u11_variant("measurement", "sms", "difficult", "survey_precise_not_accurate")
def _measurement_difficult_sms_survey_precise_not_accurate():
    pack = random.choice(_MEAS_SMS_D_PRECISE_PACKS)
    readings = pack["readings"]
    mean = sum(readings) / len(readings)
    error = abs(mean - pack["true"])
    listed = _listed(readings)
    labels = [str(i) for i in range(1, len(readings) + 1)]
    correct = "precise but not accurate"
    distractors = (
        "accurate and precise",
        "accurate but not precise",
        "neither accurate nor precise",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>Four fictional survey repeats of a {pack['item']} length, in cm: "
        f"{listed}. The true length is {pack['true']:g} cm.</p>"
        + str(
            bar_chart(
                labels,
                list(readings),
                title=f"Four length readings of a {pack['item']} in centimetres",
                desc=f"Bar chart of four length readings in centimetres: {listed}.",
            )
        )
        + str(accuracy_targets(title="Accuracy and precision targets for this survey"))
        + "<p>(i) Find the mean length in cm.</p>"
        "<p>(ii) How far is that mean from the true length, in cm?</p>"
        "<p>(iii) Using the tight cluster and the result from (ii), the set is</p>"
    )
    solution = (
        f"(i) mean = {sum(readings):g} / {len(readings)} = "
        f"<strong>{mean:g}</strong> cm<br>"
        f"(ii) |{mean:g} − {pack['true']:g}| = <strong>{error:g}</strong> cm<br>"
        f"(iii) The repeats sit close together but the mean is {error:g} cm "
        f"from the true value, so the set is <strong>{correct}</strong>."
    )
    hint = (
        "<strong>Key idea:</strong> Find the mean, compare it with the true "
        "value, then judge precision (cluster) against accuracy (true value)."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (mean, error, letter),
            (
                "Mean length (cm)",
                "Distance from true value (cm)",
                "Accuracy and precision",
            ),
            field_types=("number", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Find the mean, subtract from the true value, then choose.",
        ),
    )


_MEAS_SMS_D_CAL_PACKS = (
    {"who": "Riley", "shown_std": 103, "sample_raw": 203},
    {"who": "Casey", "shown_std": 105, "sample_raw": 305},
    {"who": "Morgan", "shown_std": 102, "sample_raw": 402},
)


@_u11_variant("measurement", "sms", "difficult", "calibrate_then_kg")
def _measurement_difficult_sms_calibrate_then_kg():
    pack = random.choice(_MEAS_SMS_D_CAL_PACKS)
    true_std = 100
    offset = pack["shown_std"] - true_std
    corrected = pack["sample_raw"] - offset
    kg = corrected / 1000
    question = (
        f"<p>In a fictional calibration tent, {pack['who']} places a 100 g "
        f"standard on a balance. The display shows {pack['shown_std']} g. "
        f"A sample then shows {pack['sample_raw']} g on the same balance.</p>"
        "<p>(i) What is the zero-style offset in grams (shown standard minus "
        "100)?</p>"
        "<p>(ii) What is the corrected sample mass in grams?</p>"
        "<p>(iii) Convert that corrected sample mass to kilograms.</p>"
    )
    solution = (
        f"(i) {pack['shown_std']} − 100 = <strong>{offset}</strong> g<br>"
        f"(ii) {pack['sample_raw']} − {offset} = "
        f"<strong>{corrected}</strong> g<br>"
        f"(iii) {corrected} ÷ 1000 = <strong>{kg:g}</strong> kg"
    )
    hint = (
        "<strong>Key idea:</strong> The offset comes from the 100 g standard, "
        "then that same offset corrects the sample before converting to kg."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (offset, corrected, kg),
            ("Offset (g)", "Corrected sample (g)", "Corrected sample (kg)"),
            format_hint="Find the offset, subtract it from the sample, then divide by 1000.",
        ),
    )


MEAS_SMS_POOLS = {
    "foundational": [
        _measurement_foundational_sms_harbour_km_compare,
        _measurement_foundational_sms_sample_mass_lid_kg,
        _measurement_foundational_sms_field_kit_ruler_mm,
    ],
    "intermediate": [
        _measurement_intermediate_sms_reserve_two_legs,
        _measurement_intermediate_sms_pond_temp_mean_range,
        _measurement_intermediate_sms_corridor_prefix_join,
    ],
    "difficult": [
        _measurement_difficult_sms_field_kit_zero,
        _measurement_difficult_sms_survey_precise_not_accurate,
        _measurement_difficult_sms_calibrate_then_kg,
    ],
}


# ---------------------------------------------------------------------------
# what_is_science — multi_step (I, D only)
# ---------------------------------------------------------------------------

_WIS_MS_I_EVIDENCE_PACKS = (
    {
        "items": (
            "a table of three mass readings in grams",
            "a stopwatch time recorded in seconds",
            "a rumour that the idea just feels right",
        ),
        "evidence": 2,
    },
    {
        "items": (
            "repeated temperature readings in a notebook",
            "a celebrity saying the claim is true",
            "a length recorded with a metre ruler",
        ),
        "evidence": 2,
    },
    {
        "items": (
            "a method another group can follow",
            "a guess with no recorded numbers",
            "a count of how many seeds germinated",
        ),
        "evidence": 2,
    },
)


@_u11_variant("what_is_science", "ms", "intermediate", "count_evidence_then_reproduce")
def _what_is_science_intermediate_ms_count_evidence_then_reproduce():
    pack = random.choice(_WIS_MS_I_EVIDENCE_PACKS)
    listed = "</li><li>".join(pack["items"])
    correct = (
        f"another group can check those {pack['evidence']} evidence items "
        "with the same method"
    )
    distractors = (
        "only a famous person can decide if the count is allowed",
        "the method should stay secret so rivals cannot copy it",
        "a longer sentence makes the count more scientific",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        "<p>A fictional class list contains these three items:</p>"
        f"<ul><li>{listed}</li></ul>"
        "<p>(i) How many of the three items are evidence a scientist can record?</p>"
        "<p>(ii) Using that count from (i), a result is reproducible when</p>"
    )
    solution = (
        f"(i) <strong>{pack['evidence']}</strong> of the three items are "
        "recordable evidence<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the items that can be measured or "
        "followed, then use that count to define a check another group can run."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["evidence"], letter),
            ("Number of evidence items", "Reproducibility"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the evidence items, then choose what reproducibility means for that count.",
        ),
    )


_WIS_MS_I_TIMES_PACKS = (
    {"a": 12, "b": 16},
    {"a": 10, "b": 14},
    {"a": 20, "b": 24},
)


@_u11_variant("what_is_science", "ms", "intermediate", "mean_times_then_public")
def _what_is_science_intermediate_ms_mean_times_then_public():
    pack = random.choice(_WIS_MS_I_TIMES_PACKS)
    mean = (pack["a"] + pack["b"]) / 2
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            f"Share the method so peers can check a similar mean of {mean:g} s",
            "Record the times with an agreed public method",
        ),
        (
            "Keep the method secret so nobody can copy the mean",
            "Accept the mean only because a celebrity quoted it",
        ),
        2,
    )
    question = (
        "<p>Two fictional groups time the same falling-ball run: "
        f"{pack['a']} s and {pack['b']} s.</p>"
        "<p>(i) What is the mean time in seconds?</p>"
        "<p>(ii) Using that mean from (i), select the two scientific actions.</p>"
    )
    solution = (
        f"(i) ({pack['a']} + {pack['b']}) / 2 = <strong>{mean:g}</strong> s<br>"
        "(ii) Share the method and record with an agreed method, using that mean."
    )
    hint = (
        "<strong>Key idea:</strong> Average the two times, then choose public "
        "actions that let others check that mean."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mean, pick_raw),
            ("Mean time (s)", "Scientific actions"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Find the mean, then select two public scientific actions.",
        ),
    )


@_u11_variant("what_is_science", "ms", "intermediate", "order_enquiry_then_peer")
def _what_is_science_intermediate_ms_order_enquiry_then_peer():
    order_raw, order_bank = _u11_order_field(
        (
            "Ask a question that can be tested",
            "Plan a fair method and identify variables",
            "Collect measurements and record them",
        ),
        ("Ignore any result that looks inconvenient",),
    )
    correct = (
        "peer critique checks the ordered method, not the person who used it"
    )
    distractors = (
        "peer critique ranks who is cleverest in the group",
        "peer critique replaces measurements with a rumour",
        "peer critique hides the method so it cannot be copied",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        "<p>A fictional enquiry needs a public sequence before anyone critiques it.</p>"
        "<p>(i) Order question, then plan, then collect.</p>"
        "<p>(ii) Using that sequence from (i), peer critique should</p>"
    )
    solution = (
        "(i) <strong>question → plan → collect</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Put the enquiry in order, then critique "
        "that method rather than the person."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Enquiry order", "Peer critique"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the enquiry, then choose what peer critique checks.",
        ),
    )


_WIS_MS_D_GROUPS_PACKS = (
    {"n": 4, "mean": 12},
    {"n": 5, "mean": 8},
    {"n": 3, "mean": 15},
)


@_u11_variant("what_is_science", "ms", "difficult", "groups_then_hypothesis")
def _what_is_science_difficult_ms_groups_then_hypothesis():
    pack = random.choice(_WIS_MS_D_GROUPS_PACKS)
    correct = (
        f"a hypothesis stays provisional until more than these {pack['n']} "
        "groups have tested it"
    )
    distractors = (
        "a hypothesis is a final law once one group likes it",
        "a hypothesis must stay secret from other groups",
        "a hypothesis is true because a celebrity repeated the mean",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>{pack['n']} fictional groups each report a similar mean of "
        f"{pack['mean']:g} s for the same method.</p>"
        "<p>(i) How many groups reported that similar mean?</p>"
        "<p>(ii) Using that number from (i), a testable idea about why the "
        "mean appears is</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong> groups<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the groups, then treat a hypothesis "
        "as provisional until more independent checks exist."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["n"], letter),
            ("Number of groups", "Hypothesis"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the groups, then choose how a hypothesis should be treated.",
        ),
    )


@_u11_variant("what_is_science", "ms", "difficult", "order_check_then_method_keep")
def _what_is_science_difficult_ms_order_check_then_method_keep():
    order_raw, order_bank = _u11_order_field(
        (
            "Measure with an agreed method and record the data",
            "Repeat the test so someone else can check the result",
            "Share the method so peers can criticise it",
        ),
        ("Keep the method secret so nobody can copy it",),
    )
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Keep a method another group can follow",
            "Keep a table of repeated measurements",
        ),
        (
            "Keep a rumour that the idea just feels right",
            "Keep a celebrity saying the claim is true",
        ),
        2,
    )
    question = (
        "<p>A fictional community checks a surprising public claim.</p>"
        "<p>(i) Order measure, then repeat, then share.</p>"
        "<p>(ii) Using that check chain from (i), select the two features to keep.</p>"
    )
    solution = (
        "(i) <strong>measure → repeat → share</strong><br>"
        "(ii) Keep a followable method and a table of repeats."
    )
    hint = (
        "<strong>Key idea:</strong> Order the public check, then keep the two "
        "features that make that chain possible."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Check order", "Features to keep"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the check chain, then select two scientific features.",
        ),
    )


_WIS_MS_D_ANECDOTE_PACKS = (
    {
        "claim": "A neighbour once saw a bottle 'work overnight'",
        "rest": (
            "a table of three pH readings",
            "a method another group can follow",
            "a rumour with no recorded numbers",
        ),
        "evidence": 2,
    },
    {
        "claim": "A poster quotes a celebrity with no data",
        "rest": (
            "repeated mass readings in grams",
            "a guess that the idea just feels right",
            "a germination count in a shared notebook",
        ),
        "evidence": 2,
    },
    {
        "claim": "Someone says the result is true because it is famous",
        "rest": (
            "a stopwatch mean other groups can repeat",
            "a secret method nobody else may see",
            "a length recorded with a metre ruler",
        ),
        "evidence": 2,
    },
)


@_u11_variant("what_is_science", "ms", "difficult", "anecdote_then_count_evidence")
def _what_is_science_difficult_ms_anecdote_then_count_evidence():
    pack = random.choice(_WIS_MS_D_ANECDOTE_PACKS)
    listed = "</li><li>".join(pack["rest"])
    correct = "an anecdote, not public evidence other groups can check"
    distractors = (
        "a reproducible measurement table",
        "a peer-reviewed method sheet",
        "a testable prediction with recorded data",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional claim file opens with: {pack['claim']}.</p>"
        "<p>(i) That opening line is</p>"
        "<p>The file then lists:</p>"
        f"<ul><li>{listed}</li></ul>"
        "<p>(ii) After rejecting the anecdote in (i), how many of those three "
        "remaining items are evidence?</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        f"(ii) <strong>{pack['evidence']}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Reject the anecdote first, then count "
        "only the remaining items that can be recorded or followed."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pack["evidence"]),
            ("Opening claim", "Number of evidence items"),
            field_types=("mcq", "number"),
            field_options=(options, None),
            format_hint="Classify the anecdote, then count the remaining evidence items.",
        ),
    )


WIS_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _what_is_science_intermediate_ms_count_evidence_then_reproduce,
        _what_is_science_intermediate_ms_mean_times_then_public,
        _what_is_science_intermediate_ms_order_enquiry_then_peer,
    ],
    "difficult": [
        _what_is_science_difficult_ms_groups_then_hypothesis,
        _what_is_science_difficult_ms_order_check_then_method_keep,
        _what_is_science_difficult_ms_anecdote_then_count_evidence,
    ],
}


# ---------------------------------------------------------------------------
# what_is_science — situational_multi_step
# ---------------------------------------------------------------------------

_WIS_SMS_F_CLUB_PACKS = (
    {
        "place": "science-club drinks stand",
        "who": "Alex",
        "n_measure": 3,
        "rumour": "a celebrity said the drink 'just works'",
    },
    {
        "place": "museum science cart",
        "who": "Sam",
        "n_measure": 4,
        "rumour": "a poster claimed the idea 'feels right'",
    },
    {
        "place": "library exhibit desk",
        "who": "Jordan",
        "n_measure": 2,
        "rumour": "a rumour that the claim needs no numbers",
    },
)


@_u11_variant("what_is_science", "sms", "foundational", "club_claim_then_test")
def _what_is_science_foundational_sms_club_claim_then_test():
    pack = random.choice(_WIS_SMS_F_CLUB_PACKS)
    correct = "test the advert with a public method other groups can repeat"
    distractors = (
        "believe the celebrity because the poster is colourful",
        "keep {who}'s method secret so rivals cannot copy it".format(who=pack["who"]),
        "change the question until the advert looks nicer",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>At a fictional {pack['place']}, {pack['who']} collects "
        f"{pack['n_measure']} mass readings in grams. A nearby advert adds "
        f"{pack['rumour']}.</p>"
        "<p>(i) How many of those collected readings are measurements?</p>"
        "<p>(ii) Using that evidence count from (i), the scientific next step is</p>"
    )
    solution = (
        f"(i) <strong>{pack['n_measure']}</strong> measurements<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the recorded measurements, then use "
        "them to choose a public test rather than a rumour."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["n_measure"], letter),
            ("Number of measurements", "Next scientific step"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the measurements, then choose the next scientific step.",
        ),
    )


_WIS_SMS_F_MUSEUM_PACKS = (
    {"place": "museum gravity well", "groups": 2, "mean": 1.2},
    {"place": "planetarium drop tower", "groups": 3, "mean": 2.4},
    {"place": "science-fair pendulum booth", "groups": 4, "mean": 0.8},
)


@_u11_variant("what_is_science", "sms", "foundational", "museum_repeat_groups")
def _what_is_science_foundational_sms_museum_repeat_groups():
    pack = random.choice(_WIS_SMS_F_MUSEUM_PACKS)
    correct = (
        f"reproducible: {pack['groups']} groups following the exhibit method "
        f"got a similar mean of {pack['mean']:g} s"
    )
    distractors = (
        "true only because the museum printed it in colour",
        "final forever because a celebrity visited the exhibit",
        "secret, so other groups must not try the method",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>At a fictional {pack['place']}, {pack['groups']} visitor groups "
        f"each follow the same public method and record a similar mean of "
        f"{pack['mean']:g} s.</p>"
        "<p>(i) How many groups reproduced that similar mean?</p>"
        "<p>(ii) Using that number from (i), the result is</p>"
    )
    solution = (
        f"(i) <strong>{pack['groups']}</strong> groups<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the independent groups, then use "
        "that count to name reproducibility."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["groups"], letter),
            ("Number of groups", "What the similar means show"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the groups, then choose what their similar means show.",
        ),
    )


_WIS_SMS_F_POSTER_PACKS = (
    {"place": "county fair drinks stall", "who": "Riley"},
    {"place": "station concourse advert", "who": "Casey"},
    {"place": "after-school club poster wall", "who": "Morgan"},
)


@_u11_variant("what_is_science", "sms", "foundational", "poster_ad_not_evidence")
def _what_is_science_foundational_sms_poster_ad_not_evidence():
    pack = random.choice(_WIS_SMS_F_POSTER_PACKS)
    correct = "ask for a method and data other groups can check"
    distractors = (
        "accept the poster because a celebrity appears on it",
        "hide {who}'s notebook so the method stays unique".format(who=pack["who"]),
        "vote on the claim without any measurements",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "A rumour that the idea just feels right",
            "A celebrity saying the claim is true",
        ),
        (
            "A table of repeated measurements",
            "A method another group can follow",
        ),
        2,
    )
    question = (
        f"<p>At a fictional {pack['place']}, {pack['who']} sees a celebrity "
        "poster with no table of readings.</p>"
        "<p>(i) The first scientific step is</p>"
        "<p>(ii) Using that step from (i), select the two items that are "
        "<em>not</em> evidence.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) A rumour and a celebrity statement are not evidence."
    )
    hint = (
        "<strong>Key idea:</strong> Ask for a public method first, then mark "
        "the two items that still fail that test."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("First scientific step", "Not evidence"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the first scientific step, then select two non-evidence items.",
        ),
    )


@_u11_variant("what_is_science", "sms", "intermediate", "club_enquiry_then_share")
def _what_is_science_intermediate_sms_club_enquiry_then_share():
    order_raw, order_bank = _u11_order_field(
        (
            "Ask a question that can be tested",
            "Plan a fair method and identify variables",
            "Collect measurements and record them",
        ),
        ("Ignore any result that looks inconvenient",),
    )
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Share the method so peers can criticise it",
            "Repeat the test so someone else can check the result",
        ),
        (
            "Keep the method secret so nobody can copy it",
            "Accept the claim only because a famous person said it",
        ),
        2,
    )
    question = (
        "<p>A fictional after-school science club investigates how long a "
        "public pendulum takes to swing.</p>"
        "<p>(i) Order question, then plan, then collect for this enquiry.</p>"
        "<p>(ii) Using that enquiry order from (i), select the two public "
        "scientific actions.</p>"
    )
    solution = (
        "(i) <strong>question → plan → collect</strong><br>"
        "(ii) Share the method and repeat the test."
    )
    hint = (
        "<strong>Key idea:</strong> Put the club enquiry in order, then choose "
        "the two actions that keep that method public."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Enquiry order", "Public scientific actions"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the enquiry, then select two public scientific actions.",
        ),
    )


_WIS_SMS_I_CRITIQUE_PACKS = (
    {"who_a": "Alex", "who_b": "Sam", "a": 10, "b": 16, "place": "fictional sports hall"},
    {"who_a": "Jordan", "who_b": "Riley", "a": 8, "b": 14, "place": "fictional playground"},
    {"who_a": "Casey", "who_b": "Morgan", "a": 20, "b": 28, "place": "fictional gym corridor"},
)


@_u11_variant("what_is_science", "sms", "intermediate", "two_group_mean_critique")
def _what_is_science_intermediate_sms_two_group_mean_critique():
    pack = random.choice(_WIS_SMS_I_CRITIQUE_PACKS)
    diff = pack["b"] - pack["a"]
    correct = (
        f"critique the methods that produced the {diff:g} s gap, not "
        f"{pack['who_a']} or {pack['who_b']} as people"
    )
    distractors = (
        "rank which group is more talented",
        "hide the slower group's notebook",
        "replace both means with a celebrity quote",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>At a {pack['place']}, {pack['who_a']}'s group times a run as "
        f"{pack['a']} s and {pack['who_b']}'s group times it as {pack['b']} s.</p>"
        "<p>(i) How many seconds larger is the second mean?</p>"
        "<p>(ii) Using that difference from (i), a scientific critique should</p>"
    )
    solution = (
        f"(i) {pack['b']} − {pack['a']} = <strong>{diff}</strong> s<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the two group times, then critique "
        "the methods that made that gap, not the people."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("Difference (s)", "What to critique"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract the two times, then choose what a scientific critique checks.",
        ),
    )


_WIS_SMS_I_BOOK_PACKS = (
    {"place": "fictional library display", "new": 5},
    {"place": "fictional archive cabinet", "new": 6},
    {"place": "fictional science-week stall", "new": 8},
)


@_u11_variant("what_is_science", "sms", "intermediate", "book_then_provisional")
def _what_is_science_intermediate_sms_book_then_provisional():
    pack = random.choice(_WIS_SMS_I_BOOK_PACKS)
    correct = (
        f"provisional: the printed explanation can change after these "
        f"{pack['new']} new measurements"
    )
    distractors = (
        "final forever because it was printed in a book",
        "true only if a celebrity signed the page",
        "secret, so the new measurements must not be shared",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['place']} shows a printed explanation of a falling-ball "
        f"rule. Staff then add {pack['new']} new public measurements that "
        "do not match the old print.</p>"
        "<p>(i) How many new measurements were added?</p>"
        "<p>(ii) Using that number from (i), the printed explanation is</p>"
    )
    solution = (
        f"(i) <strong>{pack['new']}</strong> measurements<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the new measurements, then treat "
        "the printed explanation as provisional."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["new"], letter),
            ("Number of new measurements", "Printed explanation"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the new measurements, then choose how to treat the printed explanation.",
        ),
    )


_WIS_SMS_D_FAIR_PACKS = (
    {"place": "fictional county science fair", "groups": 4},
    {"place": "fictional regional exhibit", "groups": 5},
    {"place": "fictional open-day lab", "groups": 6},
)


@_u11_variant("what_is_science", "sms", "difficult", "fair_hypothesis_groups_check")
def _what_is_science_difficult_sms_fair_hypothesis_groups_check():
    pack = random.choice(_WIS_SMS_D_FAIR_PACKS)
    order_raw, order_bank = _u11_order_field(
        (
            "Measure with an agreed method and record the data",
            "Repeat the test so someone else can check the result",
            "Share the method so peers can criticise it",
        ),
        ("Keep the method secret so nobody can copy it",),
    )
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Accepting a claim only because a famous person said it",
            "A method that must stay secret",
        ),
        (
            "A prediction that can be tested",
            "A result other groups can reproduce",
        ),
        2,
    )
    question = (
        f"<p>At a {pack['place']}, {pack['groups']} independent groups report "
        "similar means for one public method.</p>"
        "<p>(i) How many groups reported similar means?</p>"
        "<p>(ii) Order measure, then repeat, then share to check those groups.</p>"
        "<p>(iii) Using that check chain from (ii), select the two features "
        "that are <em>not</em> scientific.</p>"
    )
    solution = (
        f"(i) <strong>{pack['groups']}</strong> groups<br>"
        "(ii) <strong>measure → repeat → share</strong><br>"
        "(iii) Authority-only claims and secret methods are not scientific."
    )
    hint = (
        "<strong>Key idea:</strong> Count the groups, order the public check, "
        "then mark the two features that break that check."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pack["groups"], order_raw, pick_raw),
            ("Number of groups", "Check order", "Not scientific"),
            field_types=("number", "order", "pick"),
            field_options=(None, order_bank, pick_bank),
            field_pick_counts=(None, None, pick_count),
            format_hint="Count the groups, order the check, then select two non-scientific features.",
        ),
    )


@_u11_variant("what_is_science", "sms", "difficult", "anecdote_vs_table")
def _what_is_science_difficult_sms_anecdote_vs_table():
    correct = "the table of repeated public measurements"
    distractors = (
        "the celebrity quote with no numbers",
        "the rumour that the idea just feels right",
        "the instruction to keep the method secret",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "A celebrity saying the claim is true",
            "A rumour that the idea just feels right",
        ),
        (
            "A table of repeated measurements",
            "A method another group can follow",
        ),
        2,
    )
    question = (
        "<p>A fictional news desk compares four items about a bottled-water "
        "claim: a celebrity quote, a rumour, a secret method note, and a "
        "table of repeated public measurements.</p>"
        "<p>(i) Which item is evidence other groups can check?</p>"
        "<p>(ii) Using that choice from (i), select the two remaining items "
        "that are still not evidence.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) The celebrity quote and the rumour are not evidence."
    )
    hint = (
        "<strong>Key idea:</strong> Keep the public table, then mark the two "
        "items that still fail the evidence test."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Evidence item", "Not evidence"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the evidence item, then select two non-evidence items.",
        ),
    )


@_u11_variant("what_is_science", "sms", "difficult", "secret_method_share")
def _what_is_science_difficult_sms_secret_method_share():
    order_raw, order_bank = _u11_order_field(
        (
            "Write the method so another group can follow it",
            "Share the recorded data with the method",
            "Invite peers to criticise the method and data",
        ),
        ("Hide the steps so the result stays unique",),
    )
    correct = (
        "other groups cannot reproduce the result if the method stays secret"
    )
    distractors = (
        "secrecy makes a result more reliable",
        "a celebrity quote can replace a shared method",
        "peer critique should rank people, not methods",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        "<p>A fictional inventor booth shows a surprising timing result but "
        "keeps the apparatus steps secret.</p>"
        "<p>(i) Order write, then share, then invite critique to make the "
        "result scientific.</p>"
        "<p>(ii) Using that share chain from (i), the secret method fails because</p>"
    )
    solution = (
        "(i) <strong>write → share → invite critique</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the public share, then explain why "
        "a secret method blocks that chain."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Share order", "Why secrecy fails"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the share chain, then choose why a secret method fails.",
        ),
    )


WIS_SMS_POOLS = {
    "foundational": [
        _what_is_science_foundational_sms_club_claim_then_test,
        _what_is_science_foundational_sms_museum_repeat_groups,
        _what_is_science_foundational_sms_poster_ad_not_evidence,
    ],
    "intermediate": [
        _what_is_science_intermediate_sms_club_enquiry_then_share,
        _what_is_science_intermediate_sms_two_group_mean_critique,
        _what_is_science_intermediate_sms_book_then_provisional,
    ],
    "difficult": [
        _what_is_science_difficult_sms_fair_hypothesis_groups_check,
        _what_is_science_difficult_sms_anecdote_vs_table,
        _what_is_science_difficult_sms_secret_method_share,
    ],
}


# ---------------------------------------------------------------------------
# science_lab — multi_step
# ---------------------------------------------------------------------------

_LAB_MS_F_TEMP_PACKS = (
    {"readings": (18, 20, 22)},
    {"readings": (24, 26, 28)},
    {"readings": (11, 13, 15)},
)


@_u11_variant("science_lab", "ms", "foundational", "temps_mean_then_instrument")
def _science_lab_foundational_ms_temps_mean_then_instrument():
    pack = random.choice(_LAB_MS_F_TEMP_PACKS)
    mean = sum(pack["readings"]) / len(pack["readings"])
    correct = "a thermometer"
    distractors = (
        "a laboratory balance",
        "a stopwatch",
        "a metre ruler",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    listed = _listed(pack["readings"])
    question = (
        f"<p>Three fictional bench temperatures, in °C: {listed}.</p>"
        "<p>(i) Find the mean temperature in °C.</p>"
        "<p>(ii) The instrument that produced that mean from (i) is</p>"
    )
    solution = (
        f"(i) mean = {sum(pack['readings']):g} / 3 = "
        f"<strong>{mean:g}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Average the three temperatures, then name "
        "the instrument that measures temperature."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mean, letter),
            ("Mean temperature (°C)", "Instrument"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the mean, then choose the matching instrument.",
        ),
    )


@_u11_variant("science_lab", "ms", "foundational", "plan_order_then_independent")
def _science_lab_foundational_ms_plan_order_then_independent():
    order_raw, order_bank = _u11_order_field(
        (
            "Write a testable question",
            "Name independent, dependent and control variables",
            "Write a method another group can follow",
        ),
        ("Invent the conclusion before collecting data",),
    )
    correct = "the independent variable: the one you change on purpose"
    distractors = (
        "the dependent variable: the one you measure as the outcome",
        "the control variable: kept the same so the test is fair",
        "a guess variable: a number you invent to fill a table",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        "<p>A fictional laboratory plan must be written before heating starts.</p>"
        "<p>(i) Order question, then variables, then method.</p>"
        "<p>(ii) In that variable step from (i), the factor you change on "
        "purpose is</p>"
    )
    solution = (
        "(i) <strong>question → variables → method</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Put the plan in order, then name the "
        "independent variable from that variable step."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Plan order", "Variable you change"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the plan, then choose the independent variable.",
        ),
    )


@_u11_variant("science_lab", "ms", "foundational", "safety_pick_then_count")
def _science_lab_foundational_ms_safety_pick_then_count():
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Wear eye protection when heating or using chemicals",
            "Tie back long hair near a flame or spinner",
        ),
        (
            "Taste unknown laboratory chemicals to identify them",
            "Run in the lab to finish first",
        ),
        2,
    )
    question = (
        "<p>A fictional laboratory lists four actions before a flame is lit.</p>"
        "<p>(i) Select the two safe actions.</p>"
        "<p>(ii) After keeping those two safe actions from (i), how many of "
        "the four listed actions remain unsafe?</p>"
    )
    solution = (
        "(i) Eye protection and tying back long hair are safe.<br>"
        "(ii) The two remaining actions are unsafe, so <strong>2</strong>."
    )
    hint = (
        "<strong>Key idea:</strong> Pick the two safe actions, then count the "
        "actions left on the list that are still unsafe."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, 2),
            ("Safe actions", "Number of unsafe actions"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two safe actions, then count how many listed actions remain unsafe.",
        ),
    )


_LAB_MS_I_TIME_PACKS = (
    {"readings": (12, 14, 16)},
    {"readings": (20, 22, 24)},
    {"readings": (8, 10, 12)},
)


@_u11_variant("science_lab", "ms", "intermediate", "mean_time_then_dependent")
def _science_lab_intermediate_ms_mean_time_then_dependent():
    pack = random.choice(_LAB_MS_I_TIME_PACKS)
    mean = sum(pack["readings"]) / len(pack["readings"])
    correct = "the dependent variable: the one you measure as the outcome"
    distractors = (
        "the independent variable: the one you change on purpose",
        "the control variable: kept the same so the test is fair",
        "a guess variable: a number you invent to fill a table",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    listed = _listed(pack["readings"])
    question = (
        f"<p>Three fictional stopwatch repeats, in s: {listed}.</p>"
        "<p>(i) Find the mean time in seconds.</p>"
        "<p>(ii) That mean from (i) is a reading of</p>"
    )
    solution = (
        f"(i) mean = {sum(pack['readings']):g} / 3 = "
        f"<strong>{mean:g}</strong> s<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Average the times, then name the dependent "
        "variable as the measured outcome."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mean, letter),
            ("Mean time (s)", "Variable role"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the mean, then choose the dependent variable.",
        ),
    )


@_u11_variant("science_lab", "ms", "intermediate", "draw_order_then_error_reduce")
def _science_lab_intermediate_ms_draw_order_then_error_reduce():
    order_raw, order_bank = _u11_order_field(
        (
            "Use a simple 2D side view, not a decoration",
            "Label each piece of apparatus",
        ),
        (
            "Shade a realistic portrait of the teacher",
            "Leave the heat source unlabelled on purpose",
        ),
    )
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Repeat readings and take a mean",
            "Read a scale from directly in front",
        ),
        (
            "Change two variables at the same time",
            "Skip the units on the table",
        ),
        2,
    )
    question = (
        "<p>A fictional apparatus drawing must be followable before error "
        "is discussed.</p>"
        "<p>(i) Order side view, then labels.</p>"
        "<p>(ii) Using that labelled drawing from (i), select the two ways "
        "to reduce error.</p>"
    )
    solution = (
        "(i) <strong>side view → labels</strong><br>"
        "(ii) Repeat readings and read the scale from in front."
    )
    hint = (
        "<strong>Key idea:</strong> Draw and label first, then choose error "
        "reductions that use that labelled apparatus."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Drawing order", "Error-reduction actions"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the drawing steps, then select two error-reduction actions.",
        ),
    )


_LAB_MS_I_RANGE_PACKS = (
    {"readings": (18, 21, 19, 24, 20)},
    {"readings": (10, 12, 11, 16, 13)},
    {"readings": (30, 32, 31, 36, 33)},
)


@_u11_variant("science_lab", "ms", "intermediate", "range_then_control")
def _science_lab_intermediate_ms_range_then_control():
    pack = random.choice(_LAB_MS_I_RANGE_PACKS)
    spread = max(pack["readings"]) - min(pack["readings"])
    correct = "keep the volume of water the same in every run"
    distractors = (
        "change the volume and the heat setting together",
        "invent extra temperatures to shrink the range",
        "leave units off the table so the range looks smaller",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    listed = _listed(pack["readings"])
    question = (
        f"<p>Five fictional water temperatures, in °C: {listed}.</p>"
        "<p>(i) What is the range in °C?</p>"
        "<p>(ii) To keep later repeats comparable with that range from (i), "
        "a control is</p>"
    )
    solution = (
        f"(i) {max(pack['readings']):g} − {min(pack['readings']):g} = "
        f"<strong>{spread}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract smallest from largest, then keep "
        "a control so later ranges can be compared."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (spread, letter),
            ("Range (°C)", "Control"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the range, then choose a control that keeps later repeats comparable.",
        ),
    )


@_u11_variant("science_lab", "ms", "difficult", "full_plan_order_then_three_vars")
def _science_lab_difficult_ms_full_plan_order_then_three_vars():
    order_raw, order_bank = _u11_order_field(
        (
            "Write a testable question",
            "Name independent, dependent and control variables",
            "Write a method another group can follow",
        ),
        ("Invent the conclusion before collecting data",),
    )
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Independent variable: the one you change on purpose",
            "Dependent variable: the one you measure as the outcome",
            "Control variable: kept the same so the test is fair",
        ),
        ("Guess variable: a number you invent to fill a table",),
        3,
    )
    question = (
        "<p>A fictional investigation plan must name a fair test before data "
        "are collected.</p>"
        "<p>(i) Order question, then variables, then method.</p>"
        "<p>(ii) Using that variable step from (i), select the three correct "
        "variable roles.</p>"
    )
    solution = (
        "(i) <strong>question → variables → method</strong><br>"
        "(ii) Independent, dependent and control. Invented numbers are not a role."
    )
    hint = (
        "<strong>Key idea:</strong> Order the full plan, then keep the three "
        "real variable roles from that step."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Plan order", "Variable roles"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the plan, then select the three correct variable roles.",
        ),
    )


_LAB_MS_D_REPEAT_PACKS = (
    {"readings": (10, 12, 11, 15, 12)},
    {"readings": (20, 22, 21, 26, 21)},
    {"readings": (8, 9, 10, 14, 9)},
)


@_u11_variant("science_lab", "ms", "difficult", "range_then_repeat_mean")
def _science_lab_difficult_ms_range_then_repeat_mean():
    pack = random.choice(_LAB_MS_D_REPEAT_PACKS)
    readings = pack["readings"]
    spread = max(readings) - min(readings)
    mean = sum(readings) / len(readings)
    listed = _listed(readings)
    question = (
        f"<p>Five fictional laboratory repeats, in s: {listed}.</p>"
        "<p>(i) What is the range in seconds?</p>"
        "<p>(ii) Using the same five repeats, what is the mean in seconds?</p>"
    )
    solution = (
        f"(i) {max(readings):g} − {min(readings):g} = "
        f"<strong>{spread}</strong> s<br>"
        f"(ii) {sum(readings):g} / 5 = <strong>{mean:g}</strong> s"
    )
    hint = (
        "<strong>Key idea:</strong> The range uses the extremes of the set; "
        "the mean uses every value in that same set."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (spread, mean),
            ("Range (s)", "Mean (s)"),
            format_hint="Subtract smallest from largest, then divide the total by 5.",
        ),
    )


@_u11_variant("science_lab", "ms", "difficult", "control_list_then_safety")
def _science_lab_difficult_ms_control_list_then_safety():
    correct = (
        "same volume of water, same starting temperature, same thermometer"
    )
    distractors = (
        "change the volume and the heat setting in every run",
        "invent extra rows so the table looks complete",
        "leave hair loose and taste the heated water",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Wear eye protection when heating or using chemicals",
            "Tie back long hair near a flame or spinner",
        ),
        (
            "Taste unknown laboratory chemicals to identify them",
            "Run in the lab to finish first",
        ),
        2,
    )
    question = (
        "<p>A fictional heating investigation must stay a fair test.</p>"
        "<p>(i) The control list that keeps the test fair is</p>"
        "<p>(ii) Using those controls from (i), select the two safety actions "
        "that protect the people running the test.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Eye protection and tying back long hair."
    )
    hint = (
        "<strong>Key idea:</strong> Keep the fair-test controls, then choose "
        "the two safety actions that let that test run without harm."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Control list", "Safety actions"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the control list, then select two matching safety actions.",
        ),
    )


LAB_MS_POOLS = {
    "foundational": [
        _science_lab_foundational_ms_temps_mean_then_instrument,
        _science_lab_foundational_ms_plan_order_then_independent,
        _science_lab_foundational_ms_safety_pick_then_count,
    ],
    "intermediate": [
        _science_lab_intermediate_ms_mean_time_then_dependent,
        _science_lab_intermediate_ms_draw_order_then_error_reduce,
        _science_lab_intermediate_ms_range_then_control,
    ],
    "difficult": [
        _science_lab_difficult_ms_full_plan_order_then_three_vars,
        _science_lab_difficult_ms_range_then_repeat_mean,
        _science_lab_difficult_ms_control_list_then_safety,
    ],
}


# ---------------------------------------------------------------------------
# science_lab — situational_multi_step
# ---------------------------------------------------------------------------

_LAB_SMS_F_HEAT_PACKS = (
    {"who": "Alex", "readings": (40, 42, 44)},
    {"who": "Sam", "readings": (50, 52, 54)},
    {"who": "Jordan", "readings": (30, 32, 34)},
)


@_u11_variant("science_lab", "sms", "foundational", "heat_water_mean_then_thermo")
def _science_lab_foundational_sms_heat_water_mean_then_thermo():
    pack = random.choice(_LAB_SMS_F_HEAT_PACKS)
    mean = sum(pack["readings"]) / len(pack["readings"])
    correct = "C, the thermometer standing in the liquid"
    distractors = (
        "A, the heat source",
        "B, the beaker of liquid",
        "a laboratory balance on another bench",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    listed = _listed(pack["readings"])
    question = (
        f"<p>In a fictional heating investigation, {pack['who']} records three "
        f"water temperatures, in °C: {listed}.</p>"
        + str(lab_bench(title="Fictional heating bench with labelled apparatus"))
        + "<p>(i) Find the mean temperature in °C.</p>"
        "<p>(ii) The labelled object that produced that mean from (i) is</p>"
    )
    solution = (
        f"(i) mean = {sum(pack['readings']):g} / 3 = "
        f"<strong>{mean:g}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Average the three temperatures, then match "
        "that mean to the thermometer on the bench."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mean, letter),
            ("Mean temperature (°C)", "Instrument"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the mean, then choose the labelled thermometer.",
        ),
    )


@_u11_variant("science_lab", "sms", "foundational", "heat_water_plan_then_indep")
def _science_lab_foundational_sms_heat_water_plan_then_indep():
    order_raw, order_bank = _u11_order_field(
        (
            "Write a testable question",
            "Name independent, dependent and control variables",
            "Write a method another group can follow",
        ),
        ("Invent the conclusion before collecting data",),
    )
    correct = "how long the heat source is left on (the independent variable)"
    distractors = (
        "the water temperature (the dependent variable)",
        "the volume of water, kept the same (a control)",
        "a number invented to fill the table",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    question = (
        "<p>A fictional group plans to heat the same beaker of water for "
        "different times and record temperature.</p>"
        + str(lab_bench(title="Fictional heating bench"))
        + "<p>(i) Order question, then variables, then method.</p>"
        "<p>(ii) In that plan from (i), the factor changed on purpose is</p>"
    )
    solution = (
        "(i) <strong>question → variables → method</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the heating plan, then name heating "
        "time as the independent variable."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Plan order", "Factor changed"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the plan, then choose the independent variable.",
        ),
    )


@_u11_variant("science_lab", "sms", "foundational", "heat_water_safety_then_count")
def _science_lab_foundational_sms_heat_water_safety_then_count():
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Wear eye protection when heating or using chemicals",
            "Tie back long hair near a flame or spinner",
        ),
        (
            "Taste unknown laboratory chemicals to identify them",
            "Run in the lab to finish first",
        ),
        2,
    )
    question = (
        "<p>Before lighting a fictional Bunsen burner under a beaker of water, "
        "a group lists four actions.</p>"
        + str(lab_bench(title="Fictional heating bench"))
        + "<p>(i) Select the two safe actions for this heating investigation.</p>"
        "<p>(ii) After keeping those two safe actions from (i), how many of "
        "the four listed actions remain unsafe?</p>"
    )
    solution = (
        "(i) Eye protection and tying back long hair.<br>"
        "(ii) <strong>2</strong> unsafe actions remain."
    )
    hint = (
        "<strong>Key idea:</strong> Pick the two heating-safety actions, then "
        "count the remaining unsafe actions on the same list."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, 2),
            ("Safe actions", "Number of unsafe actions"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two safe actions, then count how many listed actions remain unsafe.",
        ),
    )


_LAB_SMS_I_SALT_PACKS = (
    {"who": "Riley", "readings": (40, 42, 44)},
    {"who": "Casey", "readings": (60, 62, 64)},
    {"who": "Morgan", "readings": (20, 22, 24)},
)


@_u11_variant("science_lab", "sms", "intermediate", "salt_time_mean_then_dep")
def _science_lab_intermediate_sms_salt_time_mean_then_dep():
    pack = random.choice(_LAB_SMS_I_SALT_PACKS)
    mean = sum(pack["readings"]) / len(pack["readings"])
    correct = "the dissolving time (the dependent variable)"
    distractors = (
        "the water temperature (the independent variable)",
        "the mass of salt, kept the same (a control)",
        "a guess written before the stopwatch starts",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    listed = _listed(pack["readings"])
    question = (
        f"<p>In a fictional dissolving investigation, {pack['who']} keeps the "
        "mass of salt and the volume of water the same, changes the water "
        f"temperature, and records three times in seconds: {listed}.</p>"
        + str(lab_bench(title="Fictional dissolving bench"))
        + "<p>(i) Find the mean time in seconds.</p>"
        "<p>(ii) That mean from (i) is a reading of</p>"
    )
    solution = (
        f"(i) mean = {sum(pack['readings']):g} / 3 = "
        f"<strong>{mean:g}</strong> s<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Average the dissolving times, then name "
        "time as the dependent variable."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mean, letter),
            ("Mean time (s)", "What the mean measures"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the mean, then choose the dependent variable.",
        ),
    )


@_u11_variant("science_lab", "sms", "intermediate", "salt_draw_then_error")
def _science_lab_intermediate_sms_salt_draw_then_error():
    order_raw, order_bank = _u11_order_field(
        (
            "Use a simple 2D side view, not a decoration",
            "Label each piece of apparatus",
        ),
        (
            "Shade a realistic portrait of the teacher",
            "Leave the heat source unlabelled on purpose",
        ),
    )
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Repeat readings and take a mean",
            "Read a scale from directly in front",
        ),
        (
            "Change two variables at the same time",
            "Skip the units on the table",
        ),
        2,
    )
    question = (
        "<p>A fictional group dissolving salt must draw the bench before "
        "timing starts.</p>"
        + str(lab_bench(title="Fictional dissolving bench"))
        + "<p>(i) Order side view, then labels.</p>"
        "<p>(ii) Using that labelled drawing from (i), select the two ways "
        "to reduce timing error.</p>"
    )
    solution = (
        "(i) <strong>side view → labels</strong><br>"
        "(ii) Repeat readings and read the scale from in front."
    )
    hint = (
        "<strong>Key idea:</strong> Draw and label the dissolving bench, then "
        "choose error reductions that use that labelled kit."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Drawing order", "Error-reduction actions"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the drawing steps, then select two error-reduction actions.",
        ),
    )


_LAB_SMS_I_SALT_RANGE_PACKS = (
    {"who": "Alex", "readings": (30, 34, 32, 40, 33)},
    {"who": "Sam", "readings": (50, 54, 52, 60, 53)},
    {"who": "Jordan", "readings": (18, 20, 19, 26, 21)},
)


@_u11_variant("science_lab", "sms", "intermediate", "salt_range_then_control")
def _science_lab_intermediate_sms_salt_range_then_control():
    pack = random.choice(_LAB_SMS_I_SALT_RANGE_PACKS)
    spread = max(pack["readings"]) - min(pack["readings"])
    correct = "keep the mass of salt and the volume of water the same"
    distractors = (
        "change the mass of salt and the temperature together",
        "invent extra times to shrink the range",
        "taste the mixture to decide when it has dissolved",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    listed = _listed(pack["readings"])
    question = (
        f"<p>In a fictional dissolving investigation, {pack['who']} records "
        f"five times in seconds: {listed}.</p>"
        + str(lab_bench(title="Fictional dissolving bench"))
        + "<p>(i) What is the range in seconds?</p>"
        "<p>(ii) To keep later repeats comparable with that range from (i), "
        "a control is</p>"
    )
    solution = (
        f"(i) {max(pack['readings']):g} − {min(pack['readings']):g} = "
        f"<strong>{spread}</strong> s<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the range of the dissolving times, "
        "then keep salt mass and water volume as controls."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (spread, letter),
            ("Range (s)", "Control"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the range, then choose a control that keeps later repeats comparable.",
        ),
    )


@_u11_variant("science_lab", "sms", "difficult", "fair_test_plan_then_vars")
def _science_lab_difficult_sms_fair_test_plan_then_vars():
    order_raw, order_bank = _u11_order_field(
        (
            "Write a testable question",
            "Name independent, dependent and control variables",
            "Write a method another group can follow",
        ),
        ("Invent the conclusion before collecting data",),
    )
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Independent variable: the one you change on purpose",
            "Dependent variable: the one you measure as the outcome",
            "Control variable: kept the same so the test is fair",
        ),
        ("Guess variable: a number you invent to fill a table",),
        3,
    )
    question = (
        "<p>A fictional fair-test team will change only the water temperature "
        "while dissolving the same mass of salt.</p>"
        + str(lab_bench(title="Fictional fair-test bench"))
        + "<p>(i) Order question, then variables, then method.</p>"
        "<p>(ii) Using that variable step from (i), select the three correct "
        "variable roles.</p>"
    )
    solution = (
        "(i) <strong>question → variables → method</strong><br>"
        "(ii) Independent, dependent and control."
    )
    hint = (
        "<strong>Key idea:</strong> Order the fair-test plan, then keep the "
        "three real variable roles from that step."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Plan order", "Variable roles"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the plan, then select the three correct variable roles.",
        ),
    )


_LAB_SMS_D_RANGE_PACKS = (
    {"who": "Riley", "readings": (12, 14, 13, 18, 13)},
    {"who": "Casey", "readings": (22, 24, 23, 28, 23)},
    {"who": "Morgan", "readings": (6, 8, 7, 12, 7)},
)


@_u11_variant("science_lab", "sms", "difficult", "fair_test_range_mean")
def _science_lab_difficult_sms_fair_test_range_mean():
    pack = random.choice(_LAB_SMS_D_RANGE_PACKS)
    readings = pack["readings"]
    spread = max(readings) - min(readings)
    mean = sum(readings) / len(readings)
    listed = _listed(readings)
    question = (
        f"<p>In a fictional fair test, {pack['who']} records five dissolving "
        f"times in seconds: {listed}.</p>"
        + str(lab_bench(title="Fictional fair-test bench"))
        + "<p>(i) What is the range in seconds?</p>"
        "<p>(ii) Using the same five repeats, what is the mean in seconds?</p>"
    )
    solution = (
        f"(i) {max(readings):g} − {min(readings):g} = "
        f"<strong>{spread}</strong> s<br>"
        f"(ii) {sum(readings):g} / 5 = <strong>{mean:g}</strong> s"
    )
    hint = (
        "<strong>Key idea:</strong> The range uses the extremes; the mean uses "
        "every dissolving time in that same set."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (spread, mean),
            ("Range (s)", "Mean (s)"),
            format_hint="Subtract smallest from largest, then divide the total by 5.",
        ),
    )


@_u11_variant("science_lab", "sms", "difficult", "fair_test_control_then_safety")
def _science_lab_difficult_sms_fair_test_control_then_safety():
    correct = (
        "same mass of salt, same volume of water, same stirring method"
    )
    distractors = (
        "change the mass of salt and the temperature in every run",
        "invent extra times so the table looks complete",
        "taste each mixture to decide when it has dissolved",
    )
    options, letter = _u11_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _u11_pick_field(
        (
            "Wear eye protection when heating or using chemicals",
            "Tie back long hair near a flame or spinner",
        ),
        (
            "Taste unknown laboratory chemicals to identify them",
            "Run in the lab to finish first",
        ),
        2,
    )
    question = (
        "<p>A fictional fair-test team will heat water and dissolve salt on "
        "one bench.</p>"
        + str(lab_bench(title="Fictional fair-test bench"))
        + "<p>(i) The control list that keeps the dissolving test fair is</p>"
        "<p>(ii) Using those controls from (i), select the two safety actions "
        "that protect the people running the test.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Eye protection and tying back long hair."
    )
    hint = (
        "<strong>Key idea:</strong> Keep the dissolving controls, then choose "
        "the two safety actions that let that fair test run without harm."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Control list", "Safety actions"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose the control list, then select two matching safety actions.",
        ),
    )


LAB_SMS_POOLS = {
    "foundational": [
        _science_lab_foundational_sms_heat_water_mean_then_thermo,
        _science_lab_foundational_sms_heat_water_plan_then_indep,
        _science_lab_foundational_sms_heat_water_safety_then_count,
    ],
    "intermediate": [
        _science_lab_intermediate_sms_salt_time_mean_then_dep,
        _science_lab_intermediate_sms_salt_draw_then_error,
        _science_lab_intermediate_sms_salt_range_then_control,
    ],
    "difficult": [
        _science_lab_difficult_sms_fair_test_plan_then_vars,
        _science_lab_difficult_sms_fair_test_range_mean,
        _science_lab_difficult_sms_fair_test_control_then_safety,
    ],
}
