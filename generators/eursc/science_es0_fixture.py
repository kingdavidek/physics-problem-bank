"""Synthetic mixed-format lesson bank for Phase ES0 tests only."""
from generators.shared.utils import (
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.eursc.science_shared import eursc_variants_for_mode
from generators.shared.variant_utils import pick_named_variant

_LEVEL = "eursc"
_SUBJECT = "science"
_TOPIC = "es0_fixture"

_METHOD_BANK = (
    {"id": "q", "text": "Ask a question"},
    {"id": "h", "text": "Form a hypothesis"},
    {"id": "t", "text": "Test with an experiment"},
    {"id": "x", "text": "Ignore the data"},
)
_SI_BANK = (
    {"id": "metre", "text": "metre"},
    {"id": "second", "text": "second"},
    {"id": "litre", "text": "litre"},
    {"id": "newton", "text": "newton"},
)


def _mcq(difficulty, suffix, question, options, answer, solution):
    def _fn():
        return make_problem(
            question,
            solution,
            "Use the SI base units.",
            difficulty,
            1,
            _LEVEL,
            _SUBJECT,
            _TOPIC,
            options=options,
            correct_answer=answer,
            choice_no_shuffle=True,
        )

    _fn.__name__ = f"es0_{difficulty}_mcq_{suffix}"
    _fn._kind = "mcq"
    return _fn


def _typed(difficulty, suffix, kind, question, extra, solution):
    def _fn():
        payload = problem_extra_from_graded_answer(extra) if extra.get("type") else dict(extra)
        return make_problem(
            question,
            solution,
            "Check the lesson bank format.",
            difficulty,
            1,
            _LEVEL,
            _SUBJECT,
            _TOPIC,
            **payload,
        )

    _fn.__name__ = f"es0_{difficulty}_{kind}_{suffix}"
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
            "1",
            "ES0-MCQ-F Which SI base unit measures length?",
            ["A  kilogram", "B  metre", "C  litre", "D  newton"],
            "B",
            "The metre is the SI base unit of length.",
        ),
        _number(
            "foundational",
            "1",
            "ES0-NUM-F Convert 2 km to metres.",
            2000,
            "2 km = 2000 m.",
        ),
        _keyword(
            "foundational",
            "1",
            "ES0-KEY-F The SI unit of time is the _____.",
            "second",
            "The SI base unit of time is the second.",
        ),
        _order(
            "foundational",
            "1",
            "ES0-ORD-F Put the scientific method steps in order.",
            ["q", "h", "t"],
            _METHOD_BANK,
            "Question, then hypothesis, then test.",
        ),
        _pick(
            "foundational",
            "1",
            "ES0-PICK-F Select the two SI base units.",
            ["metre", "second"],
            _SI_BANK,
            2,
            "Metre and second are SI base units.",
        ),
    ],
    "intermediate": [
        _mcq(
            "intermediate",
            "1",
            "ES0-MCQ-I Which prefix means 0.001?",
            ["A  kilo", "B  milli", "C  mega", "D  giga"],
            "B",
            "Milli means one thousandth.",
        ),
        _number(
            "intermediate",
            "1",
            "ES0-NUM-I How many millimetres are in 3 metres?",
            3000,
            "3 m = 3000 mm.",
        ),
        _keyword(
            "intermediate",
            "1",
            "ES0-KEY-I The SI unit of mass is the _____.",
            "kilogram",
            "The SI base unit of mass is the kilogram.",
        ),
        _order(
            "intermediate",
            "1",
            "ES0-ORD-I Order the steps: question, hypothesis, test.",
            ["q", "h", "t"],
            _METHOD_BANK,
            "Question, hypothesis, experiment.",
        ),
        _pick(
            "intermediate",
            "1",
            "ES0-PICK-I Pick the two SI base units of length and time.",
            ["metre", "second"],
            _SI_BANK,
            2,
            "Metre and second.",
        ),
    ],
    "difficult": [
        _mcq(
            "difficult",
            "1",
            "ES0-MCQ-D Which quantity is a base SI unit?",
            ["A  litre", "B  newton", "C  second", "D  joule"],
            "C",
            "The second is a base SI unit.",
        ),
        _number(
            "difficult",
            "1",
            "ES0-NUM-D Convert 0.5 km to metres.",
            500,
            "0.5 km = 500 m.",
        ),
        _keyword(
            "difficult",
            "1",
            "ES0-KEY-D The SI unit of thermodynamic temperature is the _____.",
            "kelvin",
            "Temperature in SI is the kelvin.",
        ),
        _order(
            "difficult",
            "1",
            "ES0-ORD-D Sequence the method: ask, hypothesise, test.",
            ["q", "h", "t"],
            _METHOD_BANK,
            "Ask, hypothesise, test.",
        ),
        _pick(
            "difficult",
            "1",
            "ES0-PICK-D Choose the two SI base units from the list.",
            ["metre", "second"],
            _SI_BANK,
            2,
            "Metre and second.",
        ),
    ],
}


def eursc_science_es0_fixture_variants(difficulty, mode="lesson"):
    return eursc_variants_for_mode(_POOLS.get(difficulty) or [], mode)


def eursc_science_es0_fixture(difficulty, mode="lesson", variant_name=None):
    variants = eursc_science_es0_fixture_variants(difficulty, mode)
    if not variants:
        variants = eursc_science_es0_fixture_variants(difficulty, "lesson")
    fn = pick_named_variant(variants, variant_name)
    return fn()
