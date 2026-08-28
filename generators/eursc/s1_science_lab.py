"""S1 Unit 1.1 Science Lab — 1.1.1–1.1.3."""
from generators.eursc.science_shared import lab_bench, ruler_scale
from generators.shared.utils import (
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import normalize_mode, pick_named_variant
from models.svg_kit import bar_chart

_LEVEL = "eursc"
_SUBJECT = "science"
_TOPIC = "measurement"

_BASE_BANK = (
    {"id": "metre", "text": "metre"},
    {"id": "kilogram", "text": "kilogram"},
    {"id": "second", "text": "second"},
    {"id": "litre", "text": "litre"},
    {"id": "newton", "text": "newton"},
    {"id": "celsius", "text": "degree Celsius"},
)

_CONVERT_BANK = (
    {"id": "write", "text": "Write the quantity with its current unit"},
    {"id": "factor", "text": "Multiply or divide by the correct power of ten"},
    {"id": "check", "text": "Check the new unit and that the size makes sense"},
    {"id": "guess", "text": "Guess a round number and stop"},
)

_CALIBRATE_BANK = (
    {"id": "standard", "text": "Obtain a known standard, for example a 100 g mass"},
    {"id": "compare", "text": "Measure the standard with the instrument"},
    {"id": "adjust", "text": "Adjust the instrument or record the correction"},
    {"id": "discard", "text": "Throw away the first reading because it looks odd"},
)

_ERROR_BANK = (
    {"id": "parallax", "text": "Reading a scale from an angle (parallax)"},
    {"id": "reaction", "text": "Human reaction time when using a stopwatch"},
    {"id": "zero", "text": "A balance that does not read zero when empty"},
    {"id": "damaged", "text": "A ruler with a worn-down zero end"},
    {"id": "repeat", "text": "Repeating the measurement and finding the mean"},
)


def _mcq(difficulty, suffix, question, options, answer, solution):
    def _fn():
        return make_problem(
            question,
            solution,
            "Use SI units, prefixes and the meaning of accuracy.",
            difficulty,
            1,
            _LEVEL,
            _SUBJECT,
            _TOPIC,
            options=options,
            correct_answer=answer,
        )

    _fn.__name__ = f"meas_{difficulty}_mcq_{suffix}"
    _fn._kind = "mcq"
    return _fn


def _typed(difficulty, suffix, kind, question, extra, solution):
    def _fn():
        payload = (
            problem_extra_from_graded_answer(extra)
            if extra.get("type")
            else dict(extra)
        )
        return make_problem(
            question,
            solution,
            "Check the unit, prefix and whether the size is sensible.",
            difficulty,
            1,
            _LEVEL,
            _SUBJECT,
            _TOPIC,
            **payload,
        )

    _fn.__name__ = f"meas_{difficulty}_{kind}_{suffix}"
    _fn._kind = kind
    return _fn


def _number(difficulty, suffix, question, value, solution):
    return _typed(
        difficulty,
        suffix,
        "number",
        question,
        {"type": "number", "value": value},
        solution,
    )


def _estimate(difficulty, suffix, question, value, tolerance, solution):
    return _typed(
        difficulty,
        suffix,
        "number_estimate",
        question,
        {
            "type": "number_estimate",
            "value": value,
            "tolerance": tolerance,
            "format_hint": "Enter the reading from the scale",
        },
        solution,
    )


def _keyword(difficulty, suffix, question, value, solution):
    return _typed(
        difficulty,
        suffix,
        "keyword",
        question,
        {"type": "keyword", "value": value},
        solution,
    )


def _order(difficulty, suffix, question, required_ids, bank, solution):
    return _typed(
        difficulty,
        suffix,
        "order",
        question,
        proof_steps_answer(required_ids, bank, order_matters=True),
        solution,
    )


def _pick(difficulty, suffix, question, required_ids, bank, pick_count, solution):
    return _typed(
        difficulty,
        suffix,
        "pick",
        question,
        proof_steps_answer(required_ids, bank, pick_count=pick_count),
        solution,
    )


_POOLS = {
    "foundational": [
        _mcq(
            "foundational",
            "universal",
            "Why do scientists in different countries use the same SI units?",
            [
                "A  Each country should keep its own units so results look familiar",
                "B  Shared units let anyone repeat and compare measurements",
                "C  SI units always make the numbers larger",
                "D  Units only matter in physics, not in biology",
            ],
            "B",
            "Universal SI units make results reproducible and comparable.",
        ),
        _mcq(
            "foundational",
            "length_unit",
            "Which is the SI base unit of length?",
            ["A  kilometre", "B  metre", "C  centimetre", "D  inch"],
            "B",
            "The metre (m) is the SI base unit of length.",
        ),
        _mcq(
            "foundational",
            "mass_unit",
            "Which is the SI base unit of mass?",
            ["A  gram", "B  kilogram", "C  tonne", "D  newton"],
            "B",
            "Mass in SI is the kilogram, not the gram.",
        ),
        _mcq(
            "foundational",
            "kilo",
            "The SI prefix kilo means",
            ["A  1000", "B  0.001", "C  100", "D  1 000 000"],
            "A",
            "kilo (k) means 10^3 = 1000.",
        ),
        _mcq(
            "foundational",
            "milli",
            "The SI prefix milli means",
            ["A  1000", "B  0.01", "C  0.001", "D  0.000001"],
            "C",
            "milli (m) means 10^-3 = 0.001.",
        ),
        _mcq(
            "foundational",
            "not_base",
            "Which of these is not an SI base unit?",
            ["A  second", "B  kelvin", "C  litre", "D  ampere"],
            "C",
            "The litre is a common derived unit of volume, not a base unit.",
        ),
        _number(
            "foundational",
            "km_to_m",
            "Convert 3 km to metres. Enter the number of metres only.",
            3000,
            "3 km = 3 x 1000 = 3000 m.",
        ),
        _number(
            "foundational",
            "m_to_cm",
            "Convert 2 m to centimetres. Enter the number of centimetres only.",
            200,
            "2 m = 2 x 100 = 200 cm.",
        ),
        _keyword(
            "foundational",
            "time_unit",
            "Write the SI base unit of time. Use the full word, not the symbol.",
            "second",
            "The SI base unit of time is the second.",
        ),
        _pick(
            "foundational",
            "two_base",
            "Select the two SI base units.",
            ["metre", "second"],
            _BASE_BANK,
            2,
            "Metre and second are SI base units; litre and newton are not.",
        ),
        _estimate(
            "foundational",
            "ruler_4",
            "<p>Read the pointer on this centimetre scale. Enter the reading in cm.</p>"
            + str(ruler_scale(4.0, title="Pointer at a whole-centimetre mark")),
            4.0,
            0.1,
            "The pointer sits on the 4 cm mark.",
        ),
    ],
    "intermediate": [
        _mcq(
            "intermediate",
            "centi",
            "1 centimetre is equal to",
            ["A  0.1 m", "B  0.01 m", "C  0.001 m", "D  10 m"],
            "B",
            "centi means 10^-2, so 1 cm = 0.01 m.",
        ),
        _mcq(
            "intermediate",
            "mega",
            "The prefix mega means",
            ["A  1000", "B  1 000 000", "C  0.000001", "D  100"],
            "B",
            "mega (M) means 10^6 = 1 000 000.",
        ),
        _mcq(
            "intermediate",
            "accuracy",
            "A measurement is accurate when it is",
            [
                "A  close to the true value",
                "B  the same every time, even if it is wrong",
                "C  written with many decimal places",
                "D  larger than the true value",
            ],
            "A",
            "Accuracy means closeness to the true value.",
        ),
        _mcq(
            "intermediate",
            "precision",
            "Repeated readings that are very close to each other are",
            ["A  accurate", "B  precise", "C  calibrated", "D  systematic"],
            "B",
            "Precision is how close repeats are to one another.",
        ),
        _mcq(
            "intermediate",
            "calibrate",
            "A laboratory balance is calibrated when you",
            [
                "A  wipe it clean before use",
                "B  compare it with a known standard mass",
                "C  use it in a warmer room",
                "D  read it from an angle",
            ],
            "B",
            "Calibration checks the instrument against a known standard.",
        ),
        _mcq(
            "intermediate",
            "random_error",
            "Which of these is a random error?",
            [
                "A  A ruler that is 2 mm too short at every mark",
                "B  A stopwatch that always runs 5 s fast",
                "C  Small scatter from reaction time on a stopwatch",
                "D  Using pounds instead of kilograms",
            ],
            "C",
            "Random errors scatter repeats around the true value.",
        ),
        _number(
            "intermediate",
            "km_to_m",
            "Convert 2.5 km to metres. Enter the number of metres only.",
            2500,
            "2.5 km = 2.5 x 1000 = 2500 m.",
        ),
        _number(
            "intermediate",
            "mm_in_m",
            "How many millimetres are there in 4 m? Enter the number only.",
            4000,
            "4 m = 4 x 1000 = 4000 mm.",
        ),
        _number(
            "intermediate",
            "mean",
            "<p>Five students measured the same wooden block. Lengths in cm: 10.2, 10.4, 10.1, 10.3 and 10.0.</p>"
            + str(
                bar_chart(
                    ["1", "2", "3", "4", "5"],
                    [10.2, 10.4, 10.1, 10.3, 10.0],
                    title="Five length readings in centimetres",
                    desc="Bar chart of five length readings: 10.2, 10.4, 10.1, 10.3 and 10.0 cm.",
                )
            )
            + "<p>What is the mean length in cm?</p>",
            10.2,
            "Sum = 51.0 cm. Mean = 51.0 / 5 = 10.2 cm.",
        ),
        _keyword(
            "intermediate",
            "mass_word",
            "Write the SI base unit of mass. Use the full word, not the symbol.",
            "kilogram",
            "The SI base unit of mass is the kilogram.",
        ),
        _order(
            "intermediate",
            "convert_steps",
            "Put these unit-conversion steps in the correct order.",
            ["write", "factor", "check"],
            _CONVERT_BANK,
            "Write the quantity, apply the power of ten, then check the result.",
        ),
        _pick(
            "intermediate",
            "random_sources",
            "Select the two sources of random error.",
            ["parallax", "reaction"],
            _ERROR_BANK,
            2,
            "Parallax and reaction time scatter repeats. Zero error and a damaged ruler are systematic.",
        ),
        _estimate(
            "intermediate",
            "ruler_47",
            "<p>Read the pointer on this centimetre scale. Enter the reading in cm.</p>"
            + str(ruler_scale(4.7, title="Pointer between 4 and 5 cm")),
            4.7,
            0.1,
            "The pointer is 7 small divisions past 4 cm, so 4.7 cm.",
        ),
    ],
    "difficult": [
        _mcq(
            "difficult",
            "precise_not_accurate",
            "Readings of 12.4 cm, 12.5 cm, 12.4 cm and 12.5 cm have a true length of 11.0 cm. The set is",
            [
                "A  accurate and precise",
                "B  precise but not accurate",
                "C  accurate but not precise",
                "D  neither accurate nor precise",
            ],
            "B",
            "The repeats cluster, so they are precise, but they are far from 11.0 cm.",
        ),
        _mcq(
            "difficult",
            "micro",
            "The prefix micro means",
            ["A  0.001", "B  0.000001", "C  0.01", "D  1 000 000"],
            "B",
            "micro means 10^-6 = 0.000001.",
        ),
        _mcq(
            "difficult",
            "kelvin",
            "Which statement about temperature units is correct?",
            [
                "A  The SI base unit of temperature is the degree Celsius",
                "B  The SI base unit of temperature is the kelvin",
                "C  Kelvin and Celsius degrees are the same size and the same zero",
                "D  Fahrenheit is an SI base unit",
            ],
            "B",
            "The SI base unit is the kelvin. Celsius uses the same degree size but a different zero.",
        ),
        _mcq(
            "difficult",
            "zero_error",
            "A balance reads 2 g when nothing is on the pan. This is mainly",
            [
                "A  a random error from draughts",
                "B  a systematic zero error; the balance needs calibration",
                "C  evidence that grams are not SI units",
                "D  a conversion error from kilograms",
            ],
            "B",
            "A non-zero empty reading is a systematic zero error. Calibrate or subtract it.",
        ),
        _mcq(
            "difficult",
            "cm_to_m",
            "Convert 3.2 cm to metres.",
            ["A  32 m", "B  3.2 m", "C  0.32 m", "D  0.032 m"],
            "D",
            "Divide by 100: 3.2 cm = 0.032 m.",
        ),
        _number(
            "difficult",
            "km_to_mm",
            "Convert 0.003 km to millimetres. Enter the number of millimetres only.",
            3000,
            "0.003 km = 3 m = 3000 mm.",
        ),
        _number(
            "difficult",
            "litre_to_cm3",
            "Convert 1.5 L to cubic centimetres. Enter the number of cm^3 only. (1 L = 1000 cm^3)",
            1500,
            "1.5 L = 1.5 x 1000 = 1500 cm^3.",
        ),
        _number(
            "difficult",
            "range",
            "Five length readings in cm are 10.2, 10.4, 10.1, 10.3 and 10.0. What is the range in cm?",
            0.4,
            "Range = largest - smallest = 10.4 - 10.0 = 0.4 cm.",
        ),
        _keyword(
            "difficult",
            "temp_unit",
            "Write the SI base unit of thermodynamic temperature. Use the full word, not the symbol.",
            "kelvin",
            "The SI base unit of temperature is the kelvin.",
        ),
        _order(
            "difficult",
            "calibrate_steps",
            "Order the steps for calibrating a measuring instrument.",
            ["standard", "compare", "adjust"],
            _CALIBRATE_BANK,
            "Use a known standard, measure it, then adjust or record the correction.",
        ),
        _pick(
            "difficult",
            "three_base",
            "Select the three SI base units.",
            ["metre", "kilogram", "second"],
            _BASE_BANK,
            3,
            "Metre, kilogram and second are base units.",
        ),
        _estimate(
            "difficult",
            "ruler_63",
            "<p>Read the pointer on this centimetre scale. Enter the reading in cm.</p>"
            + str(ruler_scale(6.3, title="Pointer between 6 and 7 cm")),
            6.3,
            0.1,
            "The pointer is 3 small divisions past 6 cm, so 6.3 cm.",
        ),
    ],
}


def eursc_science_measurement_variants(difficulty, mode="lesson"):
    mode = normalize_mode(mode)
    pool = list(_POOLS.get(difficulty) or [])
    if mode == "mcq":
        return [fn for fn in pool if getattr(fn, "_kind", "") == "mcq"]
    return pool


def eursc_science_measurement(difficulty, mode="lesson", variant_name=None):
    variants = eursc_science_measurement_variants(difficulty, mode)
    if not variants:
        variants = eursc_science_measurement_variants(difficulty, "lesson")
    fn = pick_named_variant(variants, variant_name)
    return fn()


def _topic_bank(topic):
    """MCQ / typed factories bound to one syllabus slug."""

    def mcq(difficulty, suffix, question, options, answer, solution):
        def _fn():
            return make_problem(
                question,
                solution,
                "Use evidence, variables and laboratory method.",
                difficulty,
                1,
                _LEVEL,
                _SUBJECT,
                topic,
                options=options,
                correct_answer=answer,
            )

        _fn.__name__ = f"{topic}_{difficulty}_mcq_{suffix}"
        _fn._kind = "mcq"
        return _fn

    def typed(difficulty, suffix, kind, question, extra, solution):
        def _fn():
            payload = (
                problem_extra_from_graded_answer(extra)
                if extra.get("type")
                else dict(extra)
            )
            return make_problem(
                question,
                solution,
                "Check the method, the evidence and the variables.",
                difficulty,
                1,
                _LEVEL,
                _SUBJECT,
                topic,
                **payload,
            )

        _fn.__name__ = f"{topic}_{difficulty}_{kind}_{suffix}"
        _fn._kind = kind
        return _fn

    def number(difficulty, suffix, question, value, solution):
        return typed(
            difficulty,
            suffix,
            "number",
            question,
            {"type": "number", "value": value},
            solution,
        )

    def keyword(difficulty, suffix, question, value, solution):
        return typed(
            difficulty,
            suffix,
            "keyword",
            question,
            {"type": "keyword", "value": value},
            solution,
        )

    def order(difficulty, suffix, question, required_ids, bank, solution):
        return typed(
            difficulty,
            suffix,
            "order",
            question,
            proof_steps_answer(required_ids, bank, order_matters=True),
            solution,
        )

    def pick(difficulty, suffix, question, required_ids, bank, pick_count, solution):
        return typed(
            difficulty,
            suffix,
            "pick",
            question,
            proof_steps_answer(required_ids, bank, pick_count=pick_count),
            solution,
        )

    return mcq, number, keyword, order, pick


_WIS_MCQ, _WIS_NUM, _WIS_KEY, _WIS_ORD, _WIS_PICK = _topic_bank("what_is_science")
_LAB_MCQ, _LAB_NUM, _LAB_KEY, _LAB_ORD, _LAB_PICK = _topic_bank("science_lab")

_EVIDENCE_BANK = (
    {"id": "measure", "text": "Measure with an agreed method and record the data"},
    {"id": "repeat", "text": "Repeat the test so someone else can check the result"},
    {"id": "share", "text": "Share the method so peers can criticise it"},
    {"id": "guess", "text": "Keep the method secret so nobody can copy it"},
)
_CLAIM_BANK = (
    {"id": "data", "text": "A table of repeated measurements"},
    {"id": "method", "text": "A method another group can follow"},
    {"id": "rumour", "text": "A rumour that the idea 'just feels right'"},
    {"id": "celebrity", "text": "A celebrity saying the claim is true"},
)
_NOT_SCIENCE_BANK = (
    {"id": "testable", "text": "A prediction that can be tested"},
    {"id": "repeatable", "text": "A result other groups can reproduce"},
    {"id": "authority", "text": "Accepting a claim only because a famous person said it"},
    {"id": "secret", "text": "A method that must stay secret"},
)
_METHOD_BANK = (
    {"id": "question", "text": "Ask a question that can be tested"},
    {"id": "plan", "text": "Plan a fair method and identify variables"},
    {"id": "collect", "text": "Collect measurements and record them"},
    {"id": "ignore", "text": "Ignore any result that looks inconvenient"},
)

_WIS_POOLS = {
    "foundational": [
        _WIS_MCQ(
            "foundational",
            "opinion",
            "Which statement is a scientific approach to a claim?",
            [
                "A  Believe it if a friend is very sure",
                "B  Test it with evidence that others can check",
                "C  Keep the method secret so rivals cannot copy it",
                "D  Change the question until the answer looks nicer",
            ],
            "B",
            "Science relies on public, testable evidence, not on confidence or secrecy.",
        ),
        _WIS_MCQ(
            "foundational",
            "knowledge",
            "Scientific knowledge is more reliable than a guess because it is",
            [
                "A  always the final truth",
                "B  based on evidence that can be tested again",
                "C  written in longer sentences",
                "D  decided by a vote in class",
            ],
            "B",
            "Reliability comes from evidence that can be reproduced, not from length or votes.",
        ),
        _WIS_MCQ(
            "foundational",
            "reproduce",
            "A result is reproducible when",
            [
                "A  only the original group can ever get it",
                "B  another group following the method gets a similar result",
                "C  the graph is drawn in colour",
                "D  the teacher already knew the answer",
            ],
            "B",
            "Reproducibility means an independent repeat of the method gives a similar result.",
        ),
        _WIS_MCQ(
            "foundational",
            "peer",
            "Peer critique in science means",
            [
                "A  insulting the person who did the work",
                "B  checking the method and the evidence",
                "C  copying the conclusion without reading the method",
                "D  deleting results you dislike",
            ],
            "B",
            "Peers examine methods and evidence, not the person.",
        ),
        _WIS_MCQ(
            "foundational",
            "provisional",
            "A scientific explanation is provisional. That means it is",
            [
                "A  a wild guess with no evidence",
                "B  the best current account, open to better evidence",
                "C  true forever once printed in a book",
                "D  only allowed in physics",
            ],
            "B",
            "Explanations stay open to new evidence; they are not frozen forever.",
        ),
        _WIS_MCQ(
            "foundational",
            "authority",
            "A TV presenter says a drink 'boosts energy'. What should a scientist do first?",
            [
                "A  Trust the presenter because they are famous",
                "B  Ask for the measurements and whether the test was controlled",
                "C  Repeat the advert in a louder voice",
                "D  Ban the drink without looking at any data",
            ],
            "B",
            "Fame is not evidence. Ask how it was tested.",
        ),
        _WIS_KEY(
            "foundational",
            "evidence_word",
            "Write the word for observations or measurements used to support or challenge a claim.",
            "evidence",
            "Evidence is the data that can support or challenge a claim.",
        ),
        _WIS_ORD(
            "foundational",
            "share_steps",
            "Order the steps that make a result more scientific.",
            ["measure", "repeat", "share"],
            _EVIDENCE_BANK,
            "Measure, repeat, then share so others can criticise the work.",
        ),
        _WIS_PICK(
            "foundational",
            "valid_evidence",
            "Select the two items that count as scientific evidence.",
            ["data", "method"],
            _CLAIM_BANK,
            2,
            "Data and a followable method are evidence. Rumour and celebrity are not.",
        ),
        _WIS_PICK(
            "foundational",
            "not_science",
            "Select the two choices that are not a scientific way to settle a claim.",
            ["authority", "secret"],
            _NOT_SCIENCE_BANK,
            2,
            "Authority-only and secret methods block testing.",
        ),
    ],
    "intermediate": [
        _WIS_MCQ(
            "intermediate",
            "one_trial",
            "One group gets an unexpected result once. The scientific next step is to",
            [
                "A  publish it as a law",
                "B  repeat the method and invite another group to try it",
                "C  hide the result",
                "D  change the units until the graph looks smoother",
            ],
            "B",
            "Unexpected results need repeats and independent checks.",
        ),
        _WIS_MCQ(
            "intermediate",
            "model",
            "A model of the particle nature of matter is useful because it",
            [
                "A  is a photograph of every atom",
                "B  helps explain observations and can be tested",
                "C  proves no better model will ever appear",
                "D  replaces the need for measurements",
            ],
            "B",
            "Models explain and predict; they are not final photographs of reality.",
        ),
        _WIS_MCQ(
            "intermediate",
            "disagree",
            "Two groups follow the same method and get slightly different means. This usually means",
            [
                "A  science has failed",
                "B  measurement variation is normal; compare methods and uncertainty",
                "C  the slower group must delete their data",
                "D  they should average in a celebrity opinion",
            ],
            "B",
            "Repeats scatter. Compare methods and the size of the difference.",
        ),
        _WIS_MCQ(
            "intermediate",
            "hypothesis",
            "A hypothesis is",
            [
                "A  a final law that cannot be tested",
                "B  a testable idea about what might happen and why",
                "C  a table of results",
                "D  a safety rule",
            ],
            "B",
            "A hypothesis is a testable proposed explanation or prediction.",
        ),
        _WIS_MCQ(
            "intermediate",
            "critique",
            "A peer says the thermometer was read from an angle. This critique is useful because it",
            [
                "A  attacks the student personally",
                "B  points to a method problem that could bias the data",
                "C  proves the conclusion is random",
                "D  means the investigation must be abandoned forever",
            ],
            "B",
            "Good critique targets the method, which can be improved.",
        ),
        _WIS_MCQ(
            "intermediate",
            "book",
            "A textbook explanation can still change later because",
            [
                "A  printers enjoy rewriting pages",
                "B  new evidence can improve or replace the explanation",
                "C  science is only opinions",
                "D  SI units keep changing every year",
            ],
            "B",
            "Provisional means open to better evidence, not that anything goes.",
        ),
        _WIS_KEY(
            "intermediate",
            "reproducible",
            "Write the word that means another group can follow the method and get a similar result.",
            "reproducible",
            "Reproducible work can be repeated independently.",
        ),
        _WIS_ORD(
            "intermediate",
            "enquiry",
            "Order a simple scientific enquiry.",
            ["question", "plan", "collect"],
            _METHOD_BANK,
            "Question, then plan, then collect data. Do not ignore inconvenient results.",
        ),
        _WIS_PICK(
            "intermediate",
            "public",
            "Select the two practices that make knowledge public and checkable.",
            ["measure", "share"],
            _EVIDENCE_BANK,
            2,
            "Measuring and sharing the method make the work checkable.",
        ),
        _WIS_PICK(
            "intermediate",
            "reject",
            "Select the two items that should not be treated as evidence.",
            ["rumour", "celebrity"],
            _CLAIM_BANK,
            2,
            "Rumour and celebrity endorsement are not measurements.",
        ),
    ],
    "difficult": [
        _WIS_MCQ(
            "difficult",
            "law",
            "A well-tested explanation is still not treated as forever-final because",
            [
                "A  scientists enjoy being uncertain",
                "B  a better test or a wider set of observations might appear",
                "C  opinions must always outrank data",
                "D  SI prefixes make old results invalid",
            ],
            "B",
            "Even strong explanations stay open to a better test.",
        ),
        _WIS_MCQ(
            "difficult",
            "fail",
            "A prediction from a model fails a fair test. Scientists should",
            [
                "A  ignore the test",
                "B  revise or replace the model in the light of the evidence",
                "C  change the data to match the model",
                "D  stop doing science",
            ],
            "B",
            "Failed predictions are how models improve.",
        ),
        _WIS_MCQ(
            "difficult",
            "anecdote",
            "One person feels better after a drink. Why is that weak evidence that the drink caused it?",
            [
                "A  Feelings can never be discussed",
                "B  There is no comparison, no control and no repeat",
                "C  Drinks cannot be measured",
                "D  Only physics counts as science",
            ],
            "B",
            "A single uncontrolled story cannot separate cause from coincidence.",
        ),
        _WIS_MCQ(
            "difficult",
            "secret_lab",
            "A company will not describe how a 'miracle' test was done. The main problem is",
            [
                "A  the idea might still be fashionable",
                "B  other groups cannot reproduce or criticise the method",
                "C  the font on the advert is too small",
                "D  SI units are optional in companies",
            ],
            "B",
            "Without a method, the claim is not scientifically checkable.",
        ),
        _WIS_MCQ(
            "difficult",
            "peer_fix",
            "Peer critique finds a control variable was not kept constant. The honest response is to",
            [
                "A  insult the reviewer",
                "B  improve the method and collect new data",
                "C  delete the reviewer comment",
                "D  publish only the flattering graph",
            ],
            "B",
            "Fix the method. That is how critique improves reliability.",
        ),
        _WIS_KEY(
            "difficult",
            "hypothesis_word",
            "Write the word for a testable idea about what might happen and why.",
            "hypothesis",
            "A hypothesis is a testable proposed explanation or prediction.",
        ),
        _WIS_ORD(
            "difficult",
            "check_chain",
            "Order how a community checks a surprising claim.",
            ["measure", "repeat", "share"],
            _EVIDENCE_BANK,
            "Measure carefully, repeat, then share for critique.",
        ),
        _WIS_PICK(
            "difficult",
            "scientific_pair",
            "Select the two scientific features of a claim.",
            ["testable", "repeatable"],
            _NOT_SCIENCE_BANK,
            2,
            "Testable predictions and repeatable results are scientific. Authority and secrecy are not.",
        ),
        _WIS_PICK(
            "difficult",
            "method_keep",
            "Select the two enquiry steps that belong in a scientific method.",
            ["plan", "collect"],
            _METHOD_BANK,
            2,
            "Planning and collecting data belong. Ignoring inconvenient results does not.",
        ),
        _WIS_NUM(
            "difficult",
            "groups",
            "Four independent groups repeat a method. Three get a mean near 12.1 cm and one gets 18.0 cm with a different ruler. How many groups support the original result? Enter a number.",
            3,
            "Three groups reproduce the original result; the fourth used a different instrument.",
        ),
    ],
}


def eursc_science_what_is_science_variants(difficulty, mode="lesson"):
    mode = normalize_mode(mode)
    pool = list(_WIS_POOLS.get(difficulty) or [])
    if mode == "mcq":
        return [fn for fn in pool if getattr(fn, "_kind", "") == "mcq"]
    return pool


def eursc_science_what_is_science(difficulty, mode="lesson", variant_name=None):
    variants = eursc_science_what_is_science_variants(difficulty, mode)
    if not variants:
        variants = eursc_science_what_is_science_variants(difficulty, "lesson")
    fn = pick_named_variant(variants, variant_name)
    return fn()


_VAR_BANK = (
    {"id": "indep", "text": "Independent variable: the one you change on purpose"},
    {"id": "dep", "text": "Dependent variable: the one you measure as the outcome"},
    {"id": "ctrl", "text": "Control variable: kept the same so the test is fair"},
    {"id": "guess", "text": "Guess variable: a number you invent to fill a table"},
)
_SAFETY_BANK = (
    {"id": "goggles", "text": "Wear eye protection when heating or using chemicals"},
    {"id": "tie", "text": "Tie back long hair near a flame or spinner"},
    {"id": "taste", "text": "Taste unknown laboratory chemicals to identify them"},
    {"id": "run", "text": "Run in the lab to finish first"},
)
_ERROR_REDUCE_BANK = (
    {"id": "repeat", "text": "Repeat readings and take a mean"},
    {"id": "eye", "text": "Read a scale from directly in front"},
    {"id": "change", "text": "Change two variables at the same time"},
    {"id": "skip", "text": "Skip the units on the table"},
)
_PLAN_BANK = (
    {"id": "question", "text": "Write a testable question"},
    {"id": "vars", "text": "Name independent, dependent and control variables"},
    {"id": "method", "text": "Write a method another group can follow"},
    {"id": "invent", "text": "Invent the conclusion before collecting data"},
)
_DRAW_BANK = (
    {"id": "labels", "text": "Label each piece of apparatus"},
    {"id": "simple", "text": "Use a simple 2D side view, not a decoration"},
    {"id": "art", "text": "Shade a realistic portrait of the teacher"},
    {"id": "secret", "text": "Leave the heat source unlabelled on purpose"},
)


_LAB_POOLS = {
    "foundational": [
        _LAB_MCQ(
            "foundational",
            "instrument",
            "You need the mass of a small metal cube. The best instrument is a",
            [
                "A  metre ruler",
                "B  laboratory balance",
                "C  stopwatch",
                "D  measuring cylinder",
            ],
            "B",
            "Mass is measured with a balance.",
        ),
        _LAB_MCQ(
            "foundational",
            "safety_hair",
            "Long hair near a Bunsen flame should be",
            [
                "A  left loose so it can be seen",
                "B  tied back",
                "C  sprayed with water after it catches",
                "D  used to sweep the bench",
            ],
            "B",
            "Tie hair back before using a flame.",
        ),
        _LAB_MCQ(
            "foundational",
            "independent",
            "In an investigation you change the temperature of water on purpose. Temperature is the",
            [
                "A  dependent variable",
                "B  independent variable",
                "C  control variable",
                "D  random error",
            ],
            "B",
            "The independent variable is the one you change.",
        ),
        _LAB_MCQ(
            "foundational",
            "dependent",
            "You time how long sugar takes to dissolve. The time is the",
            [
                "A  independent variable",
                "B  control variable",
                "C  dependent variable",
                "D  hazard",
            ],
            "C",
            "The dependent variable is the outcome you measure.",
        ),
        _LAB_MCQ(
            "foundational",
            "control",
            "A fair test keeps control variables",
            [
                "A  changing every trial",
                "B  the same",
                "C  secret",
                "D  larger than the independent variable",
            ],
            "B",
            "Controls stay the same so only one factor is tested.",
        ),
        _LAB_MCQ(
            "foundational",
            "goggles",
            "When heating a liquid you should",
            [
                "A  look directly down into the tube",
                "B  wear eye protection and point the tube away from people",
                "C  seal the tube completely",
                "D  taste a drop to check it is water",
            ],
            "B",
            "Eye protection and pointing away reduce harm if the liquid spatters.",
        ),
        _LAB_KEY(
            "foundational",
            "independent_word",
            "Write the word for the variable you change on purpose in a fair test.",
            "independent",
            "The independent variable is the one you change.",
        ),
        _LAB_ORD(
            "foundational",
            "plan_order",
            "Order the first three steps of planning a laboratory investigation.",
            ["question", "vars", "method"],
            _PLAN_BANK,
            "Question, variables, then a followable method.",
        ),
        _LAB_PICK(
            "foundational",
            "safety_two",
            "Select the two safe laboratory actions.",
            ["goggles", "tie"],
            _SAFETY_BANK,
            2,
            "Eye protection and tying hair back are required. Tasting and running are not.",
        ),
        _LAB_MCQ(
            "foundational",
            "bench_thermo",
            "<p>Look at this bench. Which labelled object measures temperature?</p>"
            + str(lab_bench()),
            ["A  A, the heat source", "B  B, the beaker", "C  C, the thermometer", "D  the bench itself"],
            "C",
            "C is the thermometer.",
        ),
    ],
    "intermediate": [
        _LAB_MCQ(
            "intermediate",
            "volume",
            "The volume of a liquid is best measured with a",
            [
                "A  ruler",
                "B  measuring cylinder, reading the bottom of the meniscus",
                "C  thermometer",
                "D  stopwatch",
            ],
            "B",
            "Use a measuring cylinder and read the meniscus correctly.",
        ),
        _LAB_MCQ(
            "intermediate",
            "drawing",
            "A useful technical drawing of apparatus should",
            [
                "A  be a realistic painting",
                "B  show a simple side view with labels",
                "C  hide the heat source",
                "D  use no labels so it looks cleaner",
            ],
            "B",
            "Simple labelled 2D views let another group rebuild the set-up.",
        ),
        _LAB_MCQ(
            "intermediate",
            "two_vars",
            "A group changes both temperature and stirring speed. The problem is",
            [
                "A  they will finish sooner",
                "B  they cannot tell which factor caused the change",
                "C  SI units no longer apply",
                "D  the table will have too many columns",
            ],
            "B",
            "Two independent variables at once spoil a fair test.",
        ),
        _LAB_MCQ(
            "intermediate",
            "repeat",
            "Repeating a timing three times and taking the mean mainly helps to",
            [
                "A  remove a systematic zero error on a damaged clock",
                "B  reduce the effect of random scatter such as reaction time",
                "C  change the independent variable",
                "D  replace a risk assessment",
            ],
            "B",
            "Means reduce random scatter. They do not fix a broken instrument.",
        ),
        _LAB_MCQ(
            "intermediate",
            "table",
            "A results table should include",
            [
                "A  units in the headings and all raw readings",
                "B  only the mean, with the raw readings deleted",
                "C  cartoons of the apparatus",
                "D  the teacher's favourite colour",
            ],
            "A",
            "Units and raw readings let someone else check the work.",
        ),
        _LAB_MCQ(
            "intermediate",
            "spill",
            "A small water spill on the floor should be",
            [
                "A  left, because water is safe",
                "B  wiped up so nobody slips, then the bench work can continue",
                "C  ignored if you are in a hurry",
                "D  tasted to confirm it is water",
            ],
            "B",
            "Spills are slip hazards even when the liquid is water.",
        ),
        _LAB_KEY(
            "intermediate",
            "dependent_word",
            "Write the word for the variable you measure as the outcome.",
            "dependent",
            "The dependent variable is the measured outcome.",
        ),
        _LAB_NUM(
            "intermediate",
            "mean_time",
            "Three dissolving times in seconds are 18, 20 and 22. What is the mean time in seconds?",
            20,
            "Mean = (18 + 20 + 22) / 3 = 20 s.",
        ),
        _LAB_ORD(
            "intermediate",
            "draw_order",
            "Order the useful steps when drawing apparatus.",
            ["simple", "labels"],
            _DRAW_BANK,
            "Draw a simple side view, then label each part.",
        ),
        _LAB_PICK(
            "intermediate",
            "reduce_error",
            "Select the two actions that reduce measurement error.",
            ["repeat", "eye"],
            _ERROR_REDUCE_BANK,
            2,
            "Repeats and reading from in front help. Changing two variables or skipping units does not.",
        ),
        _LAB_MCQ(
            "intermediate",
            "bench_heat",
            "<p>On this bench, which labelled object is the heat source?</p>"
            + str(lab_bench(title="Bench with heat source labelled A")),
            ["A  A", "B  B", "C  C", "D  none of them"],
            "A",
            "A is the heat source under the beaker.",
        ),
    ],
    "difficult": [
        _LAB_MCQ(
            "difficult",
            "zero",
            "A stopwatch that always reads 0.4 s high is mainly a",
            [
                "A  random error fixed by taking a mean",
                "B  systematic error; calibrate or subtract the offset",
                "C  control variable",
                "D  dependent variable",
            ],
            "B",
            "A constant offset is systematic. Averaging will not remove it.",
        ),
        _LAB_MCQ(
            "difficult",
            "range",
            "A thermometer marked every 1 C is a poor choice for a 0.2 C change because",
            [
                "A  Celsius is not an SI-related scale",
                "B  its resolution is too coarse for the effect you want to see",
                "C  all thermometers are identical",
                "D  you should use a ruler instead",
            ],
            "B",
            "Match the instrument's resolution to the size of the change.",
        ),
        _LAB_MCQ(
            "difficult",
            "eval",
            "An evaluation of a method should say",
            [
                "A  only that the experiment was 'fun'",
                "B  what limited the accuracy and how to improve the next trial",
                "C  that science is never wrong",
                "D  the names of everyone in the school",
            ],
            "B",
            "Evaluate limits and improvements, not entertainment.",
        ),
        _LAB_MCQ(
            "difficult",
            "control_list",
            "You investigate how temperature affects dissolving time. A sensible control is",
            [
                "A  the temperature of the water",
                "B  the mass of sugar and the volume of water",
                "C  the dissolving time",
                "D  whichever result you prefer",
            ],
            "B",
            "Keep sugar mass and water volume the same; temperature is independent; time is dependent.",
        ),
        _LAB_MCQ(
            "difficult",
            "diagram_c",
            "<p>Which labelled object stands in the liquid to give a temperature reading?</p>"
            + str(lab_bench(title="Thermometer labelled C in a beaker")),
            ["A  A", "B  B", "C  C", "D  the bench edge"],
            "C",
            "The thermometer (C) is in the liquid.",
        ),
        _LAB_KEY(
            "difficult",
            "control_word",
            "Write the word for a variable you keep the same so the test is fair.",
            "control",
            "Control variables are kept the same.",
        ),
        _LAB_NUM(
            "difficult",
            "range_lab",
            "Five timings in seconds are 19, 21, 20, 22 and 18. What is the range in seconds?",
            4,
            "Range = 22 - 18 = 4 s.",
        ),
        _LAB_ORD(
            "difficult",
            "full_plan",
            "Order a complete investigation plan.",
            ["question", "vars", "method"],
            _PLAN_BANK,
            "Question, variables, method. Do not invent the conclusion first.",
        ),
        _LAB_PICK(
            "difficult",
            "three_vars",
            "Select the three correct variable roles.",
            ["indep", "dep", "ctrl"],
            _VAR_BANK,
            3,
            "Independent, dependent and control are the three roles. Invented numbers are not.",
        ),
        _LAB_PICK(
            "difficult",
            "unsafe",
            "Select the two unsafe actions.",
            ["taste", "run"],
            _SAFETY_BANK,
            2,
            "Tasting chemicals and running in the lab are unsafe.",
        ),
    ],
}


def eursc_science_science_lab_variants(difficulty, mode="lesson"):
    mode = normalize_mode(mode)
    pool = list(_LAB_POOLS.get(difficulty) or [])
    if mode == "mcq":
        return [fn for fn in pool if getattr(fn, "_kind", "") == "mcq"]
    return pool


def eursc_science_science_lab(difficulty, mode="lesson", variant_name=None):
    variants = eursc_science_science_lab_variants(difficulty, mode)
    if not variants:
        variants = eursc_science_science_lab_variants(difficulty, "lesson")
    fn = pick_named_variant(variants, variant_name)
    return fn()

