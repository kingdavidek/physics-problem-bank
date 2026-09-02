"""S2 Unit 2.1 Universe advanced Practice pools (MS / SMS). Isolated from lesson banks.

Four topics: solar_system, light_telescopes, life_earth_elsewhere, atoms_molecules.
Three named blueprints per supported topic × tier × mode; foundational MS stays
empty for life_earth_elsewhere (matrix —).
"""
import random

from generators.eursc.science_shared import (
    atom_molecule_boxes,
    earth_sun_moon,
    reflection_rays,
    solar_scale,
)
from generators.shared.utils import graded_answer_number_fields, make_graded_problem

_LEVEL = "eursc"
_SUBJECT = "science"

_SPIN_BANK = (
    {"id": "rotate", "text": "Rotation is a planet spinning on its own axis"},
    {"id": "revolve", "text": "Revolution is a planet orbiting the Sun"},
    {"id": "day", "text": "One rotation of Earth is about one day"},
    {"id": "fame", "text": "A planet spins because a famous person said so"},
)
_SEASON_BANK = (
    {"id": "tilt", "text": "Earth's axis is tilted as it orbits the Sun"},
    {"id": "sunlight", "text": "A hemisphere gets more direct sunlight in its summer"},
    {"id": "distance_only", "text": "Seasons happen only because Earth is closer in July"},
    {"id": "moon_spin", "text": "Seasons happen because the Moon spins faster in June"},
)
_MOON_BANK = (
    {"id": "satellite", "text": "The Moon orbits Earth as a natural satellite"},
    {"id": "reflect", "text": "We see the Moon by sunlight reflected from it"},
    {"id": "own_fire", "text": "The Moon is a second Sun that burns at night"},
    {"id": "no_orbit", "text": "The Moon stays fixed on one city like a street lamp"},
)
_SCALE_BANK = (
    {"id": "au", "text": "One astronomical unit is the Earth–Sun distance"},
    {"id": "planets", "text": "The eight planets orbit the Sun at different distances"},
    {"id": "equal", "text": "Every planet is the same size as the Sun"},
    {"id": "tiny_year", "text": "The universe is a few thousand years old by telescope count"},
)
_MODEL_BANK = (
    {"id": "geo", "text": "A geocentric model puts Earth at the centre"},
    {"id": "helio", "text": "A heliocentric model puts the Sun at the centre"},
    {"id": "authority", "text": "The older model must be kept because it is older"},
    {"id": "vote", "text": "Planets vote on which model is true"},
)
_RAY_BANK = (
    {"id": "straight", "text": "Light travels in straight lines in a uniform medium"},
    {"id": "speed", "text": "Light is very fast: about 300000 km/s in vacuum in this lesson"},
    {"id": "sound_same", "text": "Light and sound always take the same time to cross a field"},
    {"id": "year_time", "text": "A light-year is a unit of time like a minute"},
)
_SHADOW_BANK = (
    {"id": "block", "text": "A shadow forms when an opaque object blocks light"},
    {"id": "rays", "text": "Straight-line rays explain the shape of a simple shadow"},
    {"id": "moon_fire", "text": "Shadows form because the Moon is a second Sun"},
    {"id": "vote_dark", "text": "Darkness is voted into place by the class"},
)
_ECLIPSE_BANK = (
    {"id": "phase", "text": "Moon phases are how much of the sunlit face we see from Earth"},
    {"id": "align", "text": "An eclipse needs a special alignment of Sun, Earth and Moon"},
    {"id": "phase_eat", "text": "The Moon is eaten each month and grows back from rock"},
    {"id": "eclipse_day", "text": "Every New Moon is a solar eclipse for the whole Earth"},
)
_OPTIC_BANK = (
    {"id": "reflect", "text": "Angle of incidence equals angle of reflection"},
    {"id": "refract", "text": "Refraction is a change of direction as light enters a new medium"},
    {"id": "colour", "text": "A red filter transmits red light and absorbs other colours"},
    {"id": "lens_magic", "text": "A lens creates extra light from nothing"},
)
_NEED_BANK = (
    {"id": "energy", "text": "Life as we know it needs a source of energy"},
    {"id": "water", "text": "Liquid water is a common requirement in the simple model"},
    {"id": "chemicals", "text": "Useful chemicals (for example carbon compounds) are needed"},
    {"id": "rumour", "text": "A social-media rumour is enough to prove life on a moon"},
)
_EARTH_BANK = (
    {"id": "early", "text": "Early Earth conditions are reconstructed from rocks and models"},
    {"id": "luca", "text": "LUCA is a scientific model of a shared ancestor, not a named person in a book of kings"},
    {"id": "sudden_city", "text": "Life began as a modern city that appeared in one day"},
    {"id": "no_evidence", "text": "Scientists refuse to use any evidence for early life"},
)
_ALIEN_BANK = (
    {"id": "testable", "text": "A claim about life elsewhere must be testable with public evidence"},
    {"id": "none_yet", "text": "There is no confirmed evidence of life beyond Earth in this course"},
    {"id": "ufo_proof", "text": "A blurry photo of a light in the sky proves microbes on Mars"},
    {"id": "secret", "text": "A secret that cannot be checked is still scientific proof"},
)
_TRAVEL_BANK = (
    {"id": "distance", "text": "Other stars are so far that travel takes far longer than a school year"},
    {"id": "habitat", "text": "A habitat beyond Earth must supply air, water, energy and shielding"},
    {"id": "walk", "text": "A person can walk to Proxima Centauri in an afternoon"},
    {"id": "airless_easy", "text": "An airless world needs no engineering because rumours supply oxygen"},
)
_PART_BANK = (
    {"id": "particles", "text": "Matter is made of particles that are still there when you cannot see them"},
    {"id": "element", "text": "An element is a substance with only one type of atom"},
    {"id": "mix", "text": "A jumble of different particles is not a single element"},
    {"id": "vanish", "text": "Atoms vanish when a solid melts and new magic atoms appear"},
)
_MOL_BANK = (
    {"id": "atom", "text": "An atom is a single particle of an element in this S2 model"},
    {"id": "molecule", "text": "A molecule is atoms joined together"},
    {"id": "symbol", "text": "A chemical symbol such as O stands for an element"},
    {"id": "symbol_word", "text": "The letters in a symbol are a sentence about the weather"},
)
_RXN_BANK = (
    {"id": "rearrange", "text": "A reaction rearranges atoms; it does not create elements from nothing"},
    {"id": "word", "text": "A word equation names the reactants and products"},
    {"id": "destroy", "text": "Burning destroys all atoms so none remain"},
    {"id": "spell", "text": "A reaction is a spell that invents a new type of atom"},
)


def _u21_variant(topic, mode_tag, difficulty, suffix):
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


def _u21_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _u21_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"1|{'|'.join(step_ids)}", bank


def _u21_pick_field(correct_texts, distractor_texts, pick_count):
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
# solar_system — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_SS_MS_F_PLANET_PACKS = (
    {"place": "fictional planetarium", "moons": 1, "planets": 8},
    {"place": "fictional observatory dome", "moons": 2, "planets": 8},
    {"place": "fictional school Solar System model", "moons": 1, "planets": 8},
)


@_u21_variant("solar_system", "ms", "foundational", "planets_then_rotate_mcq")
def _solar_system_foundational_ms_planets_then_rotate_mcq():
    pack = random.choice(_SS_MS_F_PLANET_PACKS)
    correct = "Earth spinning on its own axis"
    distractors = (
        "Earth orbiting the Sun once a year",
        "the Moon becoming a second Sun",
        "a celebrity vote on spin direction",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['place']} display counts {pack['planets']} planets "
        f"and {pack['moons']} natural satellite on the classroom model.</p>"
        "<p>(i) How many planets are on this fictional display?</p>"
        "<p>(ii) Using that model from (i), rotation of Earth is</p>"
    )
    solution = (
        f"(i) <strong>{pack['planets']}</strong> planets<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the planets on the model, then "
        "separate daily spin from the yearly orbit."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["planets"], letter),
            ("Planet count", "Rotation meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count planets, then choose the spin-on-axis meaning.",
        ),
    )


@_u21_variant("solar_system", "ms", "foundational", "spin_order_then_pick")
def _solar_system_foundational_ms_spin_order_then_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "Rotation is a planet spinning on its own axis",
            "Revolution is a planet orbiting the Sun",
        ),
        ("A planet spins because a famous person said so",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("rotate", "revolve"), _SPIN_BANK),
        2,
    )
    question = (
        "<p>A fictional textbook poster lists spin and orbit facts.</p>"
        "<p>(i) Order rotation, then revolution.</p>"
        "<p>(ii) Using that order from (i), select the two scientific spin-and-orbit ideas.</p>"
    )
    solution = (
        "(i) <strong>rotation → revolution</strong><br>"
        "(ii) Rotation and revolution are the two scientific ideas."
    )
    hint = (
        "<strong>Key idea:</strong> Order spin-on-axis before orbit-around-Sun, "
        "then pick those two facts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Spin order", "Scientific ideas"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order rotation then revolution, then select both facts.",
        ),
    )


@_u21_variant("solar_system", "ms", "foundational", "earth_letter_then_reflect_mcq")
def _solar_system_foundational_ms_earth_letter_then_reflect_mcq():
    diagram = str(earth_sun_moon(title="Fictional Earth letter"))
    correct = "sunlight reflected from the Moon's surface"
    distractors = (
        "hydrogen burning inside the Moon like a star",
        "a classroom vote that switches the Moon on",
        "sound waves from the fictional observatory",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional observatory worksheet uses this schematic (sizes not to scale).</p>"
        "<p>(i) Which letter is Earth?</p>"
        "<p>(ii) Using Earth as the viewpoint from (i), we see the Moon because of</p>"
    )
    solution = (
        "(i) <strong>B</strong> is Earth<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Earth sits between the Sun and Moon on the "
        "schematic; moonlight is reflected sunlight."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("B", letter),
            ("Earth letter", "Why we see the Moon"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Read B as Earth, then choose reflected sunlight.",
        ),
    )


_SS_MS_I_TILT_PACKS = (
    {"tilt": 23, "hemisphere": "northern"},
    {"tilt": 23, "hemisphere": "southern"},
)


@_u21_variant("solar_system", "ms", "intermediate", "tilt_deg_then_day_mcq")
def _solar_system_intermediate_ms_tilt_deg_then_day_mcq():
    pack = random.choice(_SS_MS_I_TILT_PACKS)
    correct = "about one day"
    distractors = ("about one year", "about one light-year", "about eight minutes")
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional planetarium chart quotes Earth's axial tilt as "
        f"{pack['tilt']}° for the {pack['hemisphere']} hemisphere model.</p>"
        f"<p>(i) Enter the whole-number tilt in degrees from that chart.</p>"
        "<p>(ii) Using that same Earth model from (i), one rotation takes</p>"
    )
    solution = (
        f"(i) <strong>{pack['tilt']}</strong>°<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the tilt from the chart, then recall "
        "that one spin is about one day."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["tilt"], letter),
            ("Axial tilt (°)", "One rotation takes"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the tilt, then choose the time for one rotation.",
        ),
    )


@_u21_variant("solar_system", "ms", "intermediate", "season_order_then_moon_pick")
def _solar_system_intermediate_ms_season_order_then_moon_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "Earth's axis is tilted as it orbits the Sun",
            "A hemisphere gets more direct sunlight in its summer",
        ),
        ("Seasons happen only because Earth is closer in July",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("satellite", "reflect"), _MOON_BANK),
        2,
    )
    question = (
        "<p>A fictional seasons poster links tilt, sunlight and the Moon.</p>"
        "<p>(i) Order axial tilt, then more direct summer sunlight.</p>"
        "<p>(ii) Using that seasonal model from (i), select the two Moon facts.</p>"
    )
    solution = (
        "(i) <strong>tilt → sunlight</strong><br>"
        "(ii) Natural satellite and reflected sunlight are selected."
    )
    hint = (
        "<strong>Key idea:</strong> Order tilt before summer sunlight, then pick "
        "satellite orbit and reflected light."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Season order", "Moon facts"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order tilt then sunlight, then select two Moon facts.",
        ),
    )


@_u21_variant("solar_system", "ms", "intermediate", "solar_scale_au_then_near_mcq")
def _solar_system_intermediate_ms_solar_scale_au_then_near_mcq():
    diagram = str(solar_scale(title="Fictional AU scale"))
    correct = "much smaller than 1 AU"
    distractors = (
        "also exactly 1 AU from the Sun",
        "larger than the distance to the nearest other star",
        "equal to fourteen billion years",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional distance poster uses astronomical units (AU).</p>"
        "<p>(i) On this scale, Earth is at how many AU from the Sun?</p>"
        "<p>(ii) Using that AU yardstick from (i), the Earth–Moon distance is</p>"
    )
    solution = (
        "(i) <strong>1</strong> AU<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Earth sits at 1 AU; the Moon is a nearby "
        "neighbour on that scale."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (1, letter),
            ("Earth distance (AU)", "Earth–Moon compared to 1 AU"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 1 AU for Earth, then compare the Moon distance.",
        ),
    )


@_u21_variant("solar_system", "ms", "difficult", "age_billion_then_helio_mcq")
def _solar_system_difficult_ms_age_billion_then_helio_mcq():
    age = 14
    correct = "the Sun at the centre with planets orbiting it"
    distractors = (
        "Earth at the centre with the Sun orbiting it",
        "the Moon at the centre of the universe",
        "a fictional celebrity at the centre instead of evidence",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional cosmology wall chart quotes the universe age in billions "
        "of years and compares Solar System models.</p>"
        f"<p>(i) Enter the whole number of billions of years used in this lesson.</p>"
        "<p>(ii) Using that evidence-based chart from (i), a heliocentric model puts</p>"
    )
    solution = (
        f"(i) <strong>{age}</strong> billion years<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the billion-year age, then name the "
        "Sun-centred model."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (age, letter),
            ("Universe age (billion years)", "Heliocentric model"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter the billion-year age, then choose the Sun-centred model.",
        ),
    )


@_u21_variant("solar_system", "ms", "difficult", "models_order_then_scale_pick")
def _solar_system_difficult_ms_models_order_then_scale_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "A geocentric model puts Earth at the centre",
            "A heliocentric model puts the Sun at the centre",
        ),
        ("Planets vote on which model is true",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("au", "planets"), _SCALE_BANK),
        2,
    )
    question = (
        "<p>A fictional history-of-astronomy display orders models and scale facts.</p>"
        "<p>(i) Order the Earth-centred model, then the Sun-centred model.</p>"
        "<p>(ii) Using that model sequence from (i), select the two scale ideas.</p>"
    )
    solution = (
        "(i) <strong>geocentric → heliocentric</strong><br>"
        "(ii) AU yardstick and eight planets at different distances are selected."
    )
    hint = (
        "<strong>Key idea:</strong> Order geocentric before heliocentric, then "
        "pick AU and planet-distance facts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Model order", "Scale ideas"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the two models, then select AU and planet distances.",
        ),
    )


@_u21_variant("solar_system", "ms", "difficult", "geo_evidence_chain_then_expand_mcq")
def _solar_system_difficult_ms_geo_evidence_chain_then_expand_mcq():
    models = 2
    correct = (
        "distant galaxies receding; the expanding-universe model can be checked"
    )
    distractors = (
        "a classroom vote with no measurements",
        "the Moon burning as a second Sun",
        "seasons happening only in one fictional city",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional evidence board compares two Solar System centre models "
        "and one universe claim.</p>"
        "<p>(i) How many centre models (geocentric and heliocentric) are named?</p>"
        "<p>(ii) Using that pair from (i), public evidence that the universe is "
        "expanding includes</p>"
        "<p>(iii) On the same board, the geocentric model was replaced mainly because</p>"
    )
    solution = (
        f"(i) <strong>{models}</strong> models<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) New planetary-motion evidence fitted a Sun-centred model better."
    )
    hint = (
        "<strong>Key idea:</strong> Count the two centre models, then choose "
        "galaxy recession as public evidence."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (models, letter, "evidence"),
            ("Centre models counted", "Expanding-universe evidence", "Why geocentric was replaced"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Count two models, pick galaxy recession, keyword evidence.",
        ),
    )


# solar_system — situational_multi_step (F, I, D)

_SS_SMS_F_DOME_PACKS = (
    {"who": "Alex", "place": "fictional planetarium dome", "spins": 1},
    {"who": "Sam", "place": "fictional school observatory", "spins": 2},
    {"who": "Jordan", "place": "fictional science-fair booth", "spins": 1},
)


@_u21_variant("solar_system", "sms", "foundational", "dome_spin_then_revolve_mcq")
def _solar_system_foundational_sms_dome_spin_then_revolve_mcq():
    pack = random.choice(_SS_SMS_F_DOME_PACKS)
    correct = "Earth orbiting the Sun, taking about a year"
    distractors = (
        "Earth spinning once in a minute",
        "the Sun orbiting a fictional city",
        "a season caused by the Moon's colour",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        f"<p>At a {pack['place']}, {pack['who']} turns a globe "
        f"{pack['spins']} time{'s' if pack['spins'] != 1 else ''} to show rotation.</p>"
        "<p>(i) Enter how many rotation demos were shown.</p>"
        "<p>(ii) Using that spin demo from (i), revolution of Earth is</p>"
    )
    solution = (
        f"(i) <strong>{pack['spins']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the spin demos, then name the yearly "
        "orbit around the Sun."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["spins"], letter),
            ("Rotation demos", "Revolution meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count spin demos, then choose the yearly orbit.",
        ),
    )


@_u21_variant("solar_system", "sms", "foundational", "observatory_eight_then_au_mcq")
def _solar_system_foundational_sms_observatory_eight_then_au_mcq():
    planets = 8
    correct = (
        "distances in the Solar System, based on the Earth–Sun distance"
    )
    distractors = (
        "the mass of a fictional classroom apple",
        "the temperature of a star in °C only",
        "the number of moons on Earth",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional observatory tour counts eight planets on a hallway mural.</p>"
        "<p>(i) How many planets are on that mural?</p>"
        "<p>(ii) Using that Solar System count from (i), one astronomical unit (AU) "
        "is a scale for</p>"
    )
    solution = (
        f"(i) <strong>{planets}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count eight planets, then link 1 AU to the "
        "Earth–Sun distance."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (planets, letter),
            ("Planet count", "AU meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 8 planets, then choose the AU yardstick meaning.",
        ),
    )


@_u21_variant("solar_system", "sms", "foundational", "spin_pick_then_rotation_keyword")
def _solar_system_foundational_sms_spin_pick_then_rotation_keyword():
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("rotate", "day"), _SPIN_BANK),
        2,
    )
    question = (
        "<p>A fictional planetarium handout lists spin facts for visitors.</p>"
        "<p>(i) Select the two ideas about rotation and one-day spin.</p>"
        "<p>(ii) Using those picks from (i), write the word for a planet spinning "
        "on its own axis.</p>"
    )
    solution = (
        "(i) Rotation and one-day spin are selected.<br>"
        "(ii) <strong>rotation</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick spin-on-axis and one-day timing, then "
        "name rotation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, "rotation"),
            ("Rotation ideas", "Spin word"),
            field_types=("pick", "keyword"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two spin facts, then enter rotation.",
        ),
    )


@_u21_variant("solar_system", "sms", "intermediate", "july_far_then_tilt_mcq")
def _solar_system_intermediate_sms_july_far_then_tilt_mcq():
    correct = "the northern hemisphere is tilted toward the Sun then"
    distractors = (
        "distance to the Sun is the only cause of seasons",
        "the Moon becomes a second Sun",
        "the universe stops expanding in July",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional summer-school poster notes that Earth is slightly farther "
        "from the Sun in July than in January.</p>"
        "<p>(i) Enter 1 if the poster still treats tilt as the main seasonal cause "
        "(0 if it claims distance alone is enough).</p>"
        "<p>(ii) Using that tilt-first rule from (i), July is still summer in the "
        "north because</p>"
    )
    solution = (
        "(i) <strong>1</strong> — tilt drives seasons<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 1 for tilt as the main cause, then "
        "name the hemisphere leaning toward the Sun."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (1, letter),
            ("Tilt-first rule (1/0)", "Why July is northern summer"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 1 for tilt, then choose the northern-hemisphere reason.",
        ),
    )


@_u21_variant("solar_system", "sms", "intermediate", "moon_orbit_order_then_pick")
def _solar_system_intermediate_sms_moon_orbit_order_then_pick():
    diagram = str(earth_sun_moon(title="Fictional Sun letter"))
    order_raw, order_bank = _u21_order_field(
        (
            "The Moon orbits Earth as a natural satellite",
            "We see the Moon by sunlight reflected from it",
        ),
        ("The Moon is a second Sun that burns at night",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("satellite", "reflect"), _MOON_BANK),
        2,
    )
    question = (
        diagram
        + "<p>A fictional Moon-phase workshop uses this schematic.</p>"
        "<p>(i) Which letter is the Sun on the schematic?</p>"
        "<p>(ii) Order satellite orbit, then reflected sunlight.</p>"
        "<p>(iii) Using that order from (ii), select the same two Moon facts.</p>"
    )
    solution = (
        "(i) <strong>A</strong> is the Sun<br>"
        "(ii) <strong>satellite → reflect</strong><br>"
        "(iii) Satellite and reflected light are selected."
    )
    hint = (
        "<strong>Key idea:</strong> A is the central star; order orbit then "
        "reflection, then pick those facts."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            ("A", order_raw, pick_raw),
            ("Sun letter", "Moon fact order", "Moon facts"),
            field_types=("keyword", "order", "pick"),
            field_options=(None, order_bank, pick_bank),
            field_pick_counts=(None, None, pick_count),
            format_hint="Enter A for the Sun, order facts, then select both.",
        ),
    )


@_u21_variant("solar_system", "sms", "intermediate", "year_chain_then_orbit_keyword")
def _solar_system_intermediate_sms_year_chain_then_orbit_keyword():
    days = 1
    months = 12
    correct = "orbit"
    question = (
        "<p>A fictional calendar wall at the observatory links spin and yearly motion.</p>"
        "<p>(i) One rotation of Earth is about how many days?</p>"
        "<p>(ii) One revolution is about how many months in this lesson model?</p>"
        "<p>(iii) Using that yearly trip from (ii), write the word for the path a "
        "planet follows around the Sun.</p>"
    )
    solution = (
        f"(i) <strong>{days}</strong> day<br>"
        f"(ii) <strong>{months}</strong> months<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> One spin is one day; one orbit is about a "
        "year — name that path."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (days, months, correct),
            ("Days per rotation", "Months per revolution", "Path word"),
            field_types=("number", "number", "keyword"),
            format_hint="Enter 1 day, 12 months, then the path word orbit.",
        ),
    )


@_u21_variant("solar_system", "sms", "difficult", "universe_age_order_then_moon_letter")
def _solar_system_difficult_sms_universe_age_order_then_moon_letter():
    diagram = str(earth_sun_moon(title="Fictional Moon letter"))
    order_raw, order_bank = _u21_order_field(
        (
            "A geocentric model puts Earth at the centre",
            "A heliocentric model puts the Sun at the centre",
        ),
        ("The older model must be kept because it is older",),
    )
    question = (
        diagram
        + "<p>A fictional cosmology club orders centre models on a poster that "
        "also shows the Moon schematic.</p>"
        "<p>(i) Order geocentric, then heliocentric.</p>"
        "<p>(ii) Enter the universe age in billions of years from the same poster.</p>"
        "<p>(iii) Using that schematic from (iii), which letter is the Moon?</p>"
    )
    solution = (
        "(i) <strong>geocentric → heliocentric</strong><br>"
        "(ii) <strong>14</strong> billion years<br>"
        "(iii) <strong>C</strong> is the Moon"
    )
    hint = (
        "<strong>Key idea:</strong> Order the two centre models, read 14 billion "
        "years, then find Earth's satellite."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (order_raw, 14, "C"),
            ("Model order", "Universe age (billion years)", "Moon letter"),
            field_types=("order", "number", "keyword"),
            field_options=(order_bank, None, None),
            format_hint="Order models, enter 14, then C for the Moon.",
        ),
    )


@_u21_variant("solar_system", "sms", "difficult", "scale_pick_then_season_keyword")
def _solar_system_difficult_sms_scale_pick_then_season_keyword():
    diagram = str(solar_scale(title="Fictional AU poster"))
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("au", "planets"), _SCALE_BANK),
        2,
    )
    question = (
        diagram
        + "<p>A fictional distance poster pairs AU scale with seasonal tilt facts.</p>"
        "<p>(i) Select the two scale ideas: AU and planets at different distances.</p>"
        "<p>(ii) Earth's axial tilt in this lesson is about 23°. Enter that whole number.</p>"
        "<p>(iii) Using that tilt from (ii), write the word for the yearly summer–winter "
        "pattern.</p>"
    )
    solution = (
        "(i) AU and eight planets at different distances are selected.<br>"
        "(ii) <strong>23</strong>°<br>"
        "(iii) <strong>season</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick AU and planet distances, read 23° tilt, "
        "then name seasons."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pick_raw, 23, "season"),
            ("Scale ideas", "Axial tilt (°)", "Season word"),
            field_types=("pick", "number", "keyword"),
            field_options=(pick_bank, None, None),
            field_pick_counts=(pick_count, None, None),
            format_hint="Select two scale facts, enter 23, then season.",
        ),
    )


@_u21_variant("solar_system", "sms", "difficult", "evidence_chain_then_helio_mcq")
def _solar_system_difficult_sms_evidence_chain_then_helio_mcq():
    evidence_items = 2
    correct = (
        "new evidence (for example planetary motions) fitted a Sun-centred model better"
    )
    distractors = (
        "it was newer so it had to stay",
        "planets voted on the centre",
        "the Moon asked for a new name",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional history display lists two public evidence types: planetary "
        "motions and galaxy recession.</p>"
        f"<p>(i) How many evidence types are named on that display?</p>"
        "<p>(ii) Using that evidence list from (i), the geocentric model was replaced because</p>"
        "<p>(iii) A heliocentric model puts which body at the centre? Enter Sun as one word.</p>"
    )
    solution = (
        f"(i) <strong>{evidence_items}</strong> evidence types<br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>Sun</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count two evidence types, choose better-fitting "
        "Sun-centred motions, name the Sun."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (evidence_items, letter, "Sun"),
            ("Evidence types", "Why geocentric was replaced", "Centre body"),
            field_types=("number", "mcq", "keyword"),
            field_options=(None, options, None),
            format_hint="Count 2, choose evidence-based replacement, enter Sun.",
        ),
    )


SOLAR_SYSTEM_MS_POOLS = {
    "foundational": [
        _solar_system_foundational_ms_planets_then_rotate_mcq,
        _solar_system_foundational_ms_spin_order_then_pick,
        _solar_system_foundational_ms_earth_letter_then_reflect_mcq,
    ],
    "intermediate": [
        _solar_system_intermediate_ms_tilt_deg_then_day_mcq,
        _solar_system_intermediate_ms_season_order_then_moon_pick,
        _solar_system_intermediate_ms_solar_scale_au_then_near_mcq,
    ],
    "difficult": [
        _solar_system_difficult_ms_age_billion_then_helio_mcq,
        _solar_system_difficult_ms_models_order_then_scale_pick,
        _solar_system_difficult_ms_geo_evidence_chain_then_expand_mcq,
    ],
}

SOLAR_SYSTEM_SMS_POOLS = {
    "foundational": [
        _solar_system_foundational_sms_dome_spin_then_revolve_mcq,
        _solar_system_foundational_sms_observatory_eight_then_au_mcq,
        _solar_system_foundational_sms_spin_pick_then_rotation_keyword,
    ],
    "intermediate": [
        _solar_system_intermediate_sms_july_far_then_tilt_mcq,
        _solar_system_intermediate_sms_moon_orbit_order_then_pick,
        _solar_system_intermediate_sms_year_chain_then_orbit_keyword,
    ],
    "difficult": [
        _solar_system_difficult_sms_universe_age_order_then_moon_letter,
        _solar_system_difficult_sms_scale_pick_then_season_keyword,
        _solar_system_difficult_sms_evidence_chain_then_helio_mcq,
    ],
}

# ---------------------------------------------------------------------------
# light_telescopes — multi_step (F, I, D)
# ---------------------------------------------------------------------------


@_u21_variant("light_telescopes", "ms", "foundational", "speed_c_then_ly_mcq")
def _light_telescopes_foundational_ms_speed_c_then_ly_mcq():
    speed = 300000
    correct = "the distance light travels in one year"
    distractors = (
        "a unit of time like a minute",
        "the mass of the Sun",
        "the tilt of Earth in degrees",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional optics poster quotes the rounded speed of light used in class.</p>"
        f"<p>(i) Enter that speed in km/s.</p>"
        "<p>(ii) Using that very fast light from (i), a light-year is</p>"
    )
    solution = (
        f"(i) <strong>{speed}</strong> km/s<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 300000 km/s, then recall a light-year "
        "is a distance, not a clock unit."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (speed, letter),
            ("Speed of light (km/s)", "Light-year meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 300000 km/s, then choose the distance meaning.",
        ),
    )


@_u21_variant("light_telescopes", "ms", "foundational", "shadow_pick_then_ray_order")
def _light_telescopes_foundational_ms_shadow_pick_then_ray_order():
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("block", "rays"), _SHADOW_BANK),
        2,
    )
    order_raw, order_bank = _u21_order_field(
        (
            "Light travels in straight lines in a uniform medium",
            "Light is very fast: about 300000 km/s in vacuum in this lesson",
        ),
        ("A light-year is a unit of time like a minute",),
    )
    question = (
        "<p>A fictional shadow-box demo lists ray and shadow facts.</p>"
        "<p>(i) Select the two shadow ideas: blocking and straight-line rays.</p>"
        "<p>(ii) Using those shadow facts from (i), order straight-line travel, "
        "then the huge speed of light.</p>"
    )
    solution = (
        "(i) Blocking and straight rays are selected.<br>"
        "(ii) <strong>straight → speed</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick block and rays, then order straight "
        "travel before the speed fact."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, order_raw),
            ("Shadow ideas", "Ray order"),
            field_types=("pick", "order"),
            field_options=(pick_bank, order_bank),
            field_pick_counts=(pick_count, None),
            format_hint="Select two shadow facts, then order travel then speed.",
        ),
    )


@_u21_variant("light_telescopes", "ms", "foundational", "incident_then_reflect_eq_mcq")
def _light_telescopes_foundational_ms_incident_then_reflect_eq_mcq():
    diagram = str(reflection_rays(title="Fictional incident ray"))
    correct = "equals the angle of incidence"
    distractors = (
        "is always 90° more than incidence",
        "is zero if the room is quiet",
        "depends on the planet count",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional mirror demo uses this ray diagram.</p>"
        "<p>(i) Which letter is the incident ray?</p>"
        "<p>(ii) Using that mirror setup from (i), the angle of reflection</p>"
    )
    solution = (
        "(i) <strong>A</strong> is incident<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> A heads toward the mirror; at a plane mirror "
        "i = r."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("A", letter),
            ("Incident ray letter", "Reflection angle rule"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Enter A for incident, then choose i = r.",
        ),
    )


_LT_MS_I_SEC_PACKS = (
    {"seconds": 2, "distance": 600000},
    {"seconds": 3, "distance": 900000},
)


@_u21_variant("light_telescopes", "ms", "intermediate", "two_sec_light_then_phase_mcq")
def _light_telescopes_intermediate_ms_two_sec_light_then_phase_mcq():
    pack = random.choice(_LT_MS_I_SEC_PACKS)
    correct = (
        "how much of the sunlit half of the Moon we can see from Earth"
    )
    distractors = (
        "the Moon turning into a planet",
        "a solar eclipse every night",
        "the speed of light in km/s",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional telescope club times a laser pulse at 300000 km each second.</p>"
        f"<p>(i) How many km does light travel in {pack['seconds']} s?</p>"
        "<p>(ii) Using that distance calculation from (i), a Moon phase is</p>"
    )
    solution = (
        f"(i) 300000 × {pack['seconds']} = <strong>{pack['distance']}</strong> km<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Multiply 300000 by the seconds, then name "
        "the changing view of the sunlit Moon."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["distance"], letter),
            ("Distance (km)", "Moon phase meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Multiply speed by seconds, then choose the phase meaning.",
        ),
    )


@_u21_variant("light_telescopes", "ms", "intermediate", "eclipse_order_then_refract_mcq")
def _light_telescopes_intermediate_ms_eclipse_order_then_refract_mcq():
    order_raw, order_bank = _u21_order_field(
        (
            "Moon phases are how much of the sunlit face we see from Earth",
            "An eclipse needs a special alignment of Sun, Earth and Moon",
        ),
        ("Every New Moon is a solar eclipse for the whole Earth",),
    )
    correct = (
        "a change of direction when light goes into a different medium"
    )
    distractors = (
        "light bouncing with i = r always in glass",
        "a lens creating extra photons from fame",
        "the Moon absorbing the Sun",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional eclipse poster orders phase and alignment facts.</p>"
        "<p>(i) Order Moon phases as viewpoint, then eclipse alignment.</p>"
        "<p>(ii) Using that alignment idea from (i), refraction is</p>"
    )
    solution = (
        "(i) <strong>phase → align</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order phase before alignment, then name "
        "direction change in a new medium."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Phase/eclipse order", "Refraction meaning"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order phase then alignment, then choose refraction.",
        ),
    )


@_u21_variant("light_telescopes", "ms", "intermediate", "reflected_ray_then_refract_keyword")
def _light_telescopes_intermediate_ms_reflected_ray_then_refract_keyword():
    diagram = str(reflection_rays(title="Fictional reflected ray"))
    question = (
        diagram
        + "<p>A fictional school telescope optics sheet labels mirror rays.</p>"
        "<p>(i) Which letter is the reflected ray?</p>"
        "<p>(ii) Using that reflected ray from (i), write the word for light "
        "changing direction as it enters glass or water.</p>"
    )
    solution = (
        "(i) <strong>B</strong> is reflected<br>"
        "(ii) <strong>refraction</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> B leaves the mirror; refraction is the bend "
        "in a new material."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("B", "refraction"),
            ("Reflected ray letter", "Bend-in-glass word"),
            field_types=("keyword", "keyword"),
            format_hint="Enter B for reflected, then refraction.",
        ),
    )


@_u21_variant("light_telescopes", "ms", "difficult", "angle40_then_colour_mcq")
def _light_telescopes_difficult_ms_angle40_then_colour_mcq():
    angle = 40
    correct = "it reflects blue light and absorbs other colours"
    distractors = (
        "it emits a new kind of darkness",
        "the eye votes for blue",
        "the Moon filters all red in space",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional optics lab measures a 40° angle of incidence at a plane mirror "
        "and tests a blue card in white light.</p>"
        f"<p>(i) Enter the angle of reflection in degrees (i = r).</p>"
        "<p>(ii) Using that reflection rule from (i), a blue object in white light looks "
        "blue mainly because</p>"
    )
    solution = (
        f"(i) <strong>{angle}</strong>°<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> i = r gives 40°, then selective reflection "
        "explains the blue look."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (angle, letter),
            ("Angle of reflection (°)", "Why object looks blue"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 40 for i = r, then choose selective reflection.",
        ),
    )


@_u21_variant("light_telescopes", "ms", "difficult", "filter_order_then_lens_reject")
def _light_telescopes_difficult_ms_filter_order_then_lens_reject():
    order_raw, order_bank = _u21_order_field(
        (
            "A red filter transmits red light and absorbs other colours",
            "A lens creates extra light from nothing",
        ),
        ("Angle of incidence equals angle of reflection",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("sound_same", "year_time"), _RAY_BANK),
        2,
    )
    question = (
        "<p>A fictional colour-filter poster contrasts real filter physics with "
        "poor light models.</p>"
        "<p>(i) Order colour-by-filter, then the false lens-makes-extra-light idea.</p>"
        "<p>(ii) Using that ordered list from (i), select the two poor light models.</p>"
    )
    solution = (
        "(i) <strong>colour → lens_magic</strong><br>"
        "(ii) Sound-same-speed and light-year-as-time are selected as poor models."
    )
    hint = (
        "<strong>Key idea:</strong> Order filter colour before the false lens claim, "
        "then pick the two bad models."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Filter order", "Poor light models"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order filter then false lens, then select two poor models.",
        ),
    )


@_u21_variant("light_telescopes", "ms", "difficult", "mirror_line_chain_then_safety_mcq")
def _light_telescopes_difficult_ms_mirror_line_chain_then_safety_mcq():
    diagram = str(reflection_rays(title="Fictional mirror line"))
    correct = (
        "dangerous; never do it — follow the teacher's solar-viewing rules"
    )
    distractors = (
        "a safe way to measure 300000 km/s",
        "the only way to see Moon phases",
        "required for a light-year definition",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional telescope safety sheet labels mirror parts.</p>"
        "<p>(i) Which letter is the mirror surface?</p>"
        "<p>(ii) If the angle of incidence is 40°, enter the reflection angle in degrees.</p>"
        "<p>(iii) Using that optics setup from (ii), looking at the Sun through a "
        "telescope is</p>"
    )
    solution = (
        "(i) <strong>C</strong> is the mirror<br>"
        "(ii) <strong>40</strong>°<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> C is the mirror, i = r gives 40°, never look "
        "at the Sun through a telescope."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            ("C", 40, letter),
            ("Mirror letter", "Reflection angle (°)", "Sun-viewing rule"),
            field_types=("keyword", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Enter C, then 40°, then choose the safety rule.",
        ),
    )


# light_telescopes — situational_multi_step (F, I, D)

_LT_SMS_F_DEMO_PACKS = (
    {"who": "Alex", "place": "fictional school telescope demo"},
    {"who": "Sam", "place": "fictional science-fair optics booth"},
    {"who": "Jordan", "place": "fictional planetarium light lab"},
)


@_u21_variant("light_telescopes", "sms", "foundational", "demo_speed_then_shadow_mcq")
def _light_telescopes_foundational_sms_demo_speed_then_shadow_mcq():
    pack = random.choice(_LT_SMS_F_DEMO_PACKS)
    correct = (
        "the book blocking light that travels in straight lines"
    )
    distractors = (
        "the book voting for darkness",
        "the Moon becoming a star",
        "sound taking eight minutes",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        f"<p>At a {pack['place']}, {pack['who']} quotes light at 300000 km/s "
        "and shows a book shadow.</p>"
        "<p>(i) Enter the rounded speed of light in km/s from the demo.</p>"
        "<p>(ii) Using that straight-ray model from (i), a sharp book shadow is explained by</p>"
    )
    solution = (
        "(i) <strong>300000</strong> km/s<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 300000 km/s, then choose opaque blocking "
        "with straight rays."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (300000, letter),
            ("Speed (km/s)", "Shadow explanation"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 300000, then choose blocking with straight rays.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "foundational", "telescope_straight_then_c_number")
def _light_telescopes_foundational_sms_telescope_straight_then_c_number():
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("straight", "block"), (_RAY_BANK[0], _SHADOW_BANK[0], _SHADOW_BANK[2], _SHADOW_BANK[3])),
        2,
    )
    question = (
        "<p>A fictional telescope club handout lists how rays make shadows.</p>"
        "<p>(i) Select straight-line travel and opaque blocking.</p>"
        "<p>(ii) Using those ray ideas from (i), enter the lesson's rounded speed "
        "of light in km/s.</p>"
    )
    solution = (
        "(i) Straight travel and blocking are selected.<br>"
        "(ii) <strong>300000</strong> km/s"
    )
    hint = (
        "<strong>Key idea:</strong> Pick straight rays and blocking, then enter "
        "300000 km/s."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, 300000),
            ("Ray/shadow ideas", "Speed (km/s)"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two facts, then enter 300000.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "foundational", "ray_order_then_incident_mcq")
def _light_telescopes_foundational_sms_ray_order_then_incident_mcq():
    diagram = str(reflection_rays(title="Fictional school mirror"))
    order_raw, order_bank = _u21_order_field(
        (
            "Light travels in straight lines in a uniform medium",
            "Angle of incidence equals angle of reflection",
        ),
        ("A lens creates extra light from nothing",),
    )
    correct = "A"
    distractors = ("B", "C", "the dashed normal only")
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional mirror worksheet orders ray facts beside this diagram.</p>"
        "<p>(i) Order straight-line travel, then i = r.</p>"
        "<p>(ii) Using that mirror rule from (i), which letter is the incident ray?</p>"
    )
    solution = (
        "(i) <strong>straight → reflect</strong><br>"
        "(ii) <strong>A</strong> is incident"
    )
    hint = (
        "<strong>Key idea:</strong> Order straight rays then i = r; A heads toward "
        "the mirror."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Ray rule order", "Incident ray letter"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order straight then i = r, then choose A.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "intermediate", "school_ly_then_two_sec")
def _light_telescopes_intermediate_sms_school_ly_then_two_sec():
    seconds = 2
    distance = 600000
    question = (
        "<p>A fictional astronomy club explains that a light-year is a distance, "
        "then times a laser at 300000 km/s.</p>"
        "<p>(i) Enter 1 if a light-year is a distance (0 if it is only a time unit).</p>"
        f"<p>(ii) Using that distance definition from (i), how many km does light "
        f"travel in {seconds} s?</p>"
    )
    solution = (
        "(i) <strong>1</strong> — a light-year is a distance<br>"
        f"(ii) 300000 × {seconds} = <strong>{distance}</strong> km"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 1 for distance, then multiply 300000 by "
        "the seconds."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (1, distance),
            ("Light-year is distance (1/0)", "Distance in 2 s (km)"),
            field_types=("number", "number"),
            format_hint="Enter 1, then multiply 300000 by 2.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "intermediate", "phase_eclipse_pick_then_refract_mcq")
def _light_telescopes_intermediate_sms_phase_eclipse_pick_then_refract_mcq():
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("reflect", "refract"), _OPTIC_BANK),
        2,
    )
    correct = (
        "the Moon passes between the Sun and Earth and the shadow hits Earth"
    )
    distractors = (
        "the Moon is a second Sun",
        "Earth's axis has no tilt",
        "light travels in loops",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional eclipse workshop pairs mirror and lens facts with alignment.</p>"
        "<p>(i) Select reflection equality (i = r) and refraction.</p>"
        "<p>(ii) Using those optic ideas from (i), a solar eclipse can happen when</p>"
    )
    solution = (
        "(i) i = r and refraction are selected.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick i = r and refraction, then choose Moon "
        "shadow on Earth."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, letter),
            ("Optic ideas", "Solar eclipse condition"),
            field_types=("pick", "mcq"),
            field_options=(pick_bank, options),
            field_pick_counts=(pick_count, None),
            format_hint="Select i = r and refraction, then choose alignment shadow.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "intermediate", "refract_demo_then_reflected_mcq")
def _light_telescopes_intermediate_sms_refract_demo_then_reflected_mcq():
    diagram = str(reflection_rays(title="Fictional reflected demo"))
    correct = "B"
    distractors = ("A", "C", "the Sun")
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional glass-prism demo bends light, then pupils label a mirror diagram.</p>"
        "<p>(i) Write the word for light changing direction in glass or water.</p>"
        "<p>(ii) Using that bend from (i), which letter is the reflected ray on the mirror diagram?</p>"
    )
    solution = (
        "(i) <strong>refraction</strong><br>"
        "(ii) <strong>B</strong> is reflected"
    )
    hint = (
        "<strong>Key idea:</strong> Name refraction for the prism, then B leaves "
        "the mirror."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("refraction", letter),
            ("Bend-in-glass word", "Reflected ray letter"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Enter refraction, then choose B.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "difficult", "green_filter_chain_then_lens_mcq")
def _light_telescopes_difficult_sms_green_filter_chain_then_lens_mcq():
    correct = (
        "gather light and change its direction so an image can be formed"
    )
    distractors = (
        "create mass for a planet",
        "replace the need for a classroom investigation",
        "make a light-year into a minute",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional colour-filter lab tests a green filter and a convex lens.</p>"
        "<p>(i) Enter 1 if a green filter transmits green and absorbs other colours "
        "(0 for adds green from nothing).</p>"
        "<p>(ii) A blue card mainly reflects blue. Enter 1 for selective reflection "
        "(0 for emits darkness).</p>"
        "<p>(iii) Using that real filter physics from (i)–(ii), a convex lens in a "
        "simple telescope is used to</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        "(ii) <strong>1</strong><br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 1 twice for real colour physics, then "
        "choose gather-and-focus for a lens."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (1, 1, letter),
            ("Green filter (1/0)", "Blue reflection (1/0)", "Convex lens role"),
            field_types=("number", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Enter 1, 1, then choose gather and focus.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "difficult", "angle_reflect_then_safety_pick")
def _light_telescopes_difficult_sms_angle_reflect_then_safety_pick():
    angle = 40
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("sound_same", "year_time"), _RAY_BANK),
        2,
    )
    question = (
        "<p>A fictional optics exam measures a 40° incidence angle and lists poor models.</p>"
        f"<p>(i) Enter the reflection angle in degrees (i = r).</p>"
        "<p>(ii) Using that mirror result from (i), select the two poor light models.</p>"
        "<p>(iii) Never look at the Sun through a telescope. Enter 1 for that safety rule.</p>"
    )
    solution = (
        f"(i) <strong>{angle}</strong>°<br>"
        "(ii) Sound-same-speed and light-year-as-time are selected.<br>"
        "(iii) <strong>1</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> i = r gives 40°, pick two bad models, enter 1 "
        "for Sun safety."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (angle, pick_raw, 1),
            ("Reflection angle (°)", "Poor models", "Safety rule (1)"),
            field_types=("number", "pick", "number"),
            field_options=(None, pick_bank, None),
            field_pick_counts=(None, pick_count, None),
            format_hint="Enter 40°, select two poor models, enter 1.",
        ),
    )


@_u21_variant("light_telescopes", "sms", "difficult", "colour_lens_order_then_mirror_line")
def _light_telescopes_difficult_sms_colour_lens_order_then_mirror_line():
    diagram = str(reflection_rays(title="Fictional mirror surface"))
    order_raw, order_bank = _u21_order_field(
        (
            "A red filter transmits red light and absorbs other colours",
            "A lens creates extra light from nothing",
        ),
        ("Refraction is a change of direction as light enters a new medium",),
    )
    question = (
        diagram
        + "<p>A fictional telescope poster orders colour and lens claims beside a mirror diagram.</p>"
        "<p>(i) Order colour-by-filter, then the false extra-light lens idea.</p>"
        "<p>(ii) Using that ordered list from (i), which letter is the mirror surface?</p>"
        "<p>(iii) Write the word for a shaped piece of glass that can focus light.</p>"
    )
    solution = (
        "(i) <strong>colour → lens_magic</strong><br>"
        "(ii) <strong>C</strong> is the mirror<br>"
        "(iii) <strong>lens</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order filter colour before false lens claim; "
        "C is the mirror; name lens."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (order_raw, "C", "lens"),
            ("Colour/lens order", "Mirror letter", "Focus-glass word"),
            field_types=("order", "keyword", "keyword"),
            field_options=(order_bank, None, None),
            format_hint="Order facts, enter C, then lens.",
        ),
    )


LIGHT_TELESCOPES_MS_POOLS = {
    "foundational": [
        _light_telescopes_foundational_ms_speed_c_then_ly_mcq,
        _light_telescopes_foundational_ms_shadow_pick_then_ray_order,
        _light_telescopes_foundational_ms_incident_then_reflect_eq_mcq,
    ],
    "intermediate": [
        _light_telescopes_intermediate_ms_two_sec_light_then_phase_mcq,
        _light_telescopes_intermediate_ms_eclipse_order_then_refract_mcq,
        _light_telescopes_intermediate_ms_reflected_ray_then_refract_keyword,
    ],
    "difficult": [
        _light_telescopes_difficult_ms_angle40_then_colour_mcq,
        _light_telescopes_difficult_ms_filter_order_then_lens_reject,
        _light_telescopes_difficult_ms_mirror_line_chain_then_safety_mcq,
    ],
}

LIGHT_TELESCOPES_SMS_POOLS = {
    "foundational": [
        _light_telescopes_foundational_sms_demo_speed_then_shadow_mcq,
        _light_telescopes_foundational_sms_telescope_straight_then_c_number,
        _light_telescopes_foundational_sms_ray_order_then_incident_mcq,
    ],
    "intermediate": [
        _light_telescopes_intermediate_sms_school_ly_then_two_sec,
        _light_telescopes_intermediate_sms_phase_eclipse_pick_then_refract_mcq,
        _light_telescopes_intermediate_sms_refract_demo_then_reflected_mcq,
    ],
    "difficult": [
        _light_telescopes_difficult_sms_green_filter_chain_then_lens_mcq,
        _light_telescopes_difficult_sms_angle_reflect_then_safety_pick,
        _light_telescopes_difficult_sms_colour_lens_order_then_mirror_line,
    ],
}

# ---------------------------------------------------------------------------
# life_earth_elsewhere — multi_step (I, D only; foundational MS empty)
# ---------------------------------------------------------------------------


@_u21_variant("life_earth_elsewhere", "ms", "intermediate", "luca_then_proxima_mcq")
def _life_earth_elsewhere_intermediate_ms_luca_then_proxima_mcq():
    proxima = 4
    correct = (
        "a model of a last universal common ancestor based on shared chemistry"
    )
    distractors = (
        "a planet between Earth and Mars",
        "proof that aliens visited last week",
        "a unit of distance like a light-year only",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional astrobiology poster quotes Proxima distance and defines LUCA.</p>"
        f"<p>(i) Enter the whole number of light-years used for the nearest other star.</p>"
        "<p>(ii) Using that evidence-based poster from (i), LUCA in this lesson is</p>"
    )
    solution = (
        f"(i) <strong>{proxima}</strong> light-years<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 4 ly, then name LUCA as a shared-ancestor "
        "model, not a planet."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (proxima, letter),
            ("Proxima distance (ly)", "LUCA meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 4, then choose the shared-ancestor model.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "ms", "intermediate", "early_order_then_alien_pick")
def _life_earth_elsewhere_intermediate_ms_early_order_then_alien_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "Early Earth conditions are reconstructed from rocks and models",
            "LUCA is a scientific model of a shared ancestor, not a named person in a book of kings",
        ),
        ("Life began as a modern city that appeared in one day",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("testable", "none_yet"), _ALIEN_BANK),
        2,
    )
    question = (
        "<p>A fictional origins-of-life display orders Earth history and alien claims.</p>"
        "<p>(i) Order early-Earth reconstruction, then the LUCA model.</p>"
        "<p>(ii) Using that evidence-first sequence from (i), select the two careful "
        "ideas about life elsewhere.</p>"
    )
    solution = (
        "(i) <strong>early → luca</strong><br>"
        "(ii) Testable claims and no confirmed life yet are selected."
    )
    hint = (
        "<strong>Key idea:</strong> Order rocks/models before LUCA, then pick "
        "testable claims and no confirmed life."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Origins order", "Careful alien ideas"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order early Earth then LUCA, select two careful ideas.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "ms", "intermediate", "air_habitat_then_needs_count")
def _life_earth_elsewhere_intermediate_ms_air_habitat_then_needs_count():
    needs = 3
    correct = (
        "supply breathable air by engineering, not by hoping"
    )
    distractors = (
        "rely on rumours for oxygen",
        "ignore energy needs",
        "be a 5-minute walk from Earth",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional habitat engineering sheet lists energy, liquid water and chemicals.</p>"
        f"<p>(i) How many needs are in that simple list?</p>"
        "<p>(ii) Using that needs list from (i), a habitat on an airless world must still</p>"
    )
    solution = (
        f"(i) <strong>{needs}</strong> needs<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count three needs, then name engineered air "
        "on an airless world."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (needs, letter),
            ("Needs count", "Airless-world habitat rule"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 3 needs, then choose engineered breathable air.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "ms", "difficult", "chemicals_then_habitat_keyword")
def _life_earth_elsewhere_difficult_ms_chemicals_then_habitat_keyword():
    shield_items = 4
    question = (
        "<p>A fictional habitation checklist names air, water, energy and radiation "
        "shielding for life beyond Earth.</p>"
        f"<p>(i) How many items are on that simple habitation list?</p>"
        "<p>(ii) Useful chemicals in the simple life model include carbon compounds "
        "that can be measured. Enter 1 for that public-evidence rule.</p>"
        "<p>(iii) Using that checklist from (i), write the word for a place that "
        "supplies what living things need to stay alive.</p>"
    )
    solution = (
        f"(i) <strong>{shield_items}</strong> items<br>"
        "(ii) <strong>1</strong><br>"
        "(iii) <strong>habitat</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count four constraints, enter 1 for measurable "
        "chemistry, name habitat."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (shield_items, 1, "habitat"),
            ("Habitation items", "Measurable chemicals (1)", "Place word"),
            field_types=("number", "number", "keyword"),
            format_hint="Enter 4, 1, then habitat.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "ms", "difficult", "travel_order_then_rocket_mcq")
def _life_earth_elsewhere_difficult_ms_travel_order_then_rocket_mcq():
    order_raw, order_bank = _u21_order_field(
        (
            "Other stars are so far that travel takes far longer than a school year",
            "A habitat beyond Earth must supply air, water, energy and shielding",
        ),
        ("A person can walk to Proxima Centauri in an afternoon",),
    )
    correct = (
        "would take far longer than a few years with current rockets"
    )
    distractors = (
        "takes an afternoon on foot",
        "is the same as 1 AU",
        "proves microbes exist",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional interstellar travel poster orders distance and life-support facts.</p>"
        "<p>(i) Order huge distance, then supplied habitat needs.</p>"
        "<p>(ii) Using that scale from (i), a chemical-rocket trip of a few light-years</p>"
    )
    solution = (
        "(i) <strong>distance → habitat</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order distance before habitat engineering, then "
        "note rockets are far slower than light."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Travel order", "Rocket trip time"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order distance then habitat, choose slow rocket reality.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "ms", "difficult", "open_evidence_pick_then_ufo_mcq")
def _life_earth_elsewhere_difficult_ms_open_evidence_pick_then_ufo_mcq():
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("walk", "airless_easy"), _TRAVEL_BANK),
        2,
    )
    correct = (
        "is not, by itself, evidence of extraterrestrial life"
    )
    distractors = (
        "proves life on Mars",
        "is a light-year",
        "is LUCA",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional evidence board rejects unrealistic travel claims and blurry photos.</p>"
        "<p>(i) Select the two travel claims that are not realistic.</p>"
        "<p>(ii) Using that careful stance from (i), a blurry photo of a light in the sky</p>"
    )
    solution = (
        "(i) Walk-to-Proxima and airless-no-engineering are selected.<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick two unrealistic travel claims, then reject "
        "UFO photos as automatic proof."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, letter),
            ("Unrealistic travel claims", "Blurry photo status"),
            field_types=("pick", "mcq"),
            field_options=(pick_bank, options),
            field_pick_counts=(pick_count, None),
            format_hint="Select two bad travel claims, then choose not automatic proof.",
        ),
    )


# life_earth_elsewhere — situational_multi_step (F, I, D)

_LF_SMS_F_SITE_PACKS = (
    {"who": "Alex", "place": "fictional Mars-habitat design club"},
    {"who": "Sam", "place": "fictional astrobiology fair booth"},
    {"who": "Jordan", "place": "fictional space-week classroom"},
)


@_u21_variant("life_earth_elsewhere", "sms", "foundational", "needs_three_then_water_mcq")
def _life_earth_elsewhere_foundational_sms_needs_three_then_water_mcq():
    pack = random.choice(_LF_SMS_F_SITE_PACKS)
    needs = 3
    correct = "many Earth life processes happen in water"
    distractors = (
        "it is a unit of time",
        "it proves UFOs",
        "it is the same as a light-year",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        f"<p>At a {pack['place']}, {pack['who']} lists energy, liquid water and "
        "useful chemicals as needs for life as we know it.</p>"
        f"<p>(i) How many needs are on that fictional list?</p>"
        "<p>(ii) Using that list from (i), liquid water matters because</p>"
    )
    solution = (
        f"(i) <strong>{needs}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count three needs, then name water as a solvent "
        "for Earth life processes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (needs, letter),
            ("Needs count", "Why liquid water matters"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 3, then choose the solvent/chemistry reason.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "foundational", "energy_water_order_then_pick")
def _life_earth_elsewhere_foundational_sms_energy_water_order_then_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "Life as we know it needs a source of energy",
            "Liquid water is a common requirement in the simple model",
        ),
        ("A social-media rumour is enough to prove life on a moon",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("energy", "water"), _NEED_BANK),
        2,
    )
    question = (
        "<p>A fictional space-week poster orders life needs for visitors.</p>"
        "<p>(i) Order energy, then liquid water.</p>"
        "<p>(ii) Using that order from (i), select energy and water from the simple list.</p>"
    )
    solution = (
        "(i) <strong>energy → water</strong><br>"
        "(ii) Energy and water are selected."
    )
    hint = (
        "<strong>Key idea:</strong> Order energy before water, then pick those "
        "two needs."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Needs order", "Energy and water"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order energy then water, then select both.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "foundational", "travel_far_then_needs_keyword")
def _life_earth_elsewhere_foundational_sms_travel_far_then_needs_keyword():
    question = (
        "<p>A fictional starship poster warns that other stars are enormously far away.</p>"
        "<p>(i) Enter 1 if travel to another star takes far longer than a school year "
        "at realistic speeds (0 if stars are closer than the Moon).</p>"
        "<p>(ii) Using that distance fact from (i), write the liquid this lesson treats "
        "as a common need for life as we know it.</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        "(ii) <strong>water</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 1 for huge star distances, then name "
        "liquid water."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (1, "water"),
            ("Stars are far (1/0)", "Liquid need word"),
            field_types=("number", "keyword"),
            format_hint="Enter 1, then water.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "intermediate", "luca_poster_then_ufo_reject_mcq")
def _life_earth_elsewhere_intermediate_sms_luca_poster_then_ufo_reject_mcq():
    correct = (
        "is not, by itself, evidence of extraterrestrial life"
    )
    distractors = (
        "proves life on Mars",
        "is a light-year",
        "is LUCA",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional LUCA poster explains a shared-ancestor model from chemistry.</p>"
        "<p>(i) Enter 1 if LUCA is a scientific model of relatedness (0 if it is a king "
        "in a history book).</p>"
        "<p>(ii) Using that model stance from (i), a blurry photo of a light in the sky</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 1 for the LUCA model, then reject blurry "
        "lights as automatic proof."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (1, letter),
            ("LUCA is model (1/0)", "Blurry photo status"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 1, then choose not automatic proof.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "intermediate", "proxima_years_then_claim_testable")
def _life_earth_elsewhere_intermediate_sms_proxima_years_then_claim_testable():
    proxima = 4
    question = (
        "<p>A fictional star-distance chart quotes Proxima at a few light-years.</p>"
        f"<p>(i) Enter the whole number of years for light to reach the nearest other star.</p>"
        "<p>(ii) At light speed that trip still takes a few years. Enter 1 if that is true "
        "(0 if it takes a few seconds).</p>"
        "<p>(iii) Using that honest distance from (i), a scientific claim about moon microbes "
        "must be testable. Enter the word testable.</p>"
    )
    solution = (
        f"(i) <strong>{proxima}</strong> years<br>"
        "(ii) <strong>1</strong><br>"
        "(iii) <strong>testable</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 4, then 1 for years-not-seconds, then "
        "testable claims."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (proxima, 1, "testable"),
            ("Proxima years", "Years at light speed (1)", "Claim property"),
            field_types=("number", "number", "keyword"),
            format_hint="Enter 4, 1, then testable.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "intermediate", "early_earth_order_then_alien_pick")
def _life_earth_elsewhere_intermediate_sms_early_earth_order_then_alien_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "Early Earth conditions are reconstructed from rocks and models",
            "LUCA is a scientific model of a shared ancestor, not a named person in a book of kings",
        ),
        ("Scientists refuse to use any evidence for early life",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("testable", "none_yet"), _ALIEN_BANK),
        2,
    )
    question = (
        "<p>A fictional museum trail orders early Earth and extraterrestrial-life ideas.</p>"
        "<p>(i) Order early-Earth reconstruction, then the LUCA model.</p>"
        "<p>(ii) Using that public-evidence path from (i), select testable claims and "
        "no confirmed life yet.</p>"
    )
    solution = (
        "(i) <strong>early → luca</strong><br>"
        "(ii) Testable and none-yet are selected."
    )
    hint = (
        "<strong>Key idea:</strong> Order rocks/models before LUCA, pick testable "
        "and no confirmed life."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Origins order", "Careful alien ideas"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order early Earth then LUCA, select two careful ideas.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "difficult", "habitat_four_then_travel_not_pick")
def _life_earth_elsewhere_difficult_sms_habitat_four_then_travel_not_pick():
    items = 4
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("walk", "airless_easy"), _TRAVEL_BANK),
        2,
    )
    question = (
        "<p>A fictional Mars-habitat engineering sheet lists air, water, energy and shielding.</p>"
        f"<p>(i) How many habitation constraints are named?</p>"
        "<p>(ii) Using that engineering list from (i), select the two unrealistic travel claims.</p>"
        "<p>(iii) The honest S2 position is to search with testable methods. Enter 1 for that rule.</p>"
    )
    solution = (
        f"(i) <strong>{items}</strong> constraints<br>"
        "(ii) Walk-to-Proxima and airless-no-engineering are selected.<br>"
        "(iii) <strong>1</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count four constraints, pick two bad travel claims, "
        "enter 1 for testable search."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (items, pick_raw, 1),
            ("Habitation items", "Unrealistic travel claims", "Testable search (1)"),
            field_types=("number", "pick", "number"),
            field_options=(None, pick_bank, None),
            field_pick_counts=(None, pick_count, None),
            format_hint="Enter 4, select two bad claims, enter 1.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "difficult", "rocket_slow_chain_then_open_mcq")
def _life_earth_elsewhere_difficult_sms_rocket_slow_chain_then_open_mcq():
    needs = 3
    correct = (
        "search with testable methods; do not treat rumours as results"
    )
    distractors = (
        "it is already proved by any bright star",
        "it is rude to ask for evidence",
        "telescopes must be pointed at the Sun to find it",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional astrobiology debate lists three life needs and rocket speeds.</p>"
        f"<p>(i) How many needs are in energy, liquid water, chemicals?</p>"
        "<p>(ii) Chemical rockets are much slower than light. Enter 1 for that rule.</p>"
        "<p>(iii) Using that evidence-first stance from (ii), the honest S2 position on "
        "extraterrestrial life is</p>"
    )
    solution = (
        f"(i) <strong>{needs}</strong><br>"
        "(ii) <strong>1</strong><br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count three needs, enter 1 for slow rockets, choose "
        "testable search without rumours."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (needs, 1, letter),
            ("Needs count", "Rockets slower than light (1)", "Honest S2 position"),
            field_types=("number", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Enter 3, 1, then choose testable search.",
        ),
    )


@_u21_variant("life_earth_elsewhere", "sms", "difficult", "chemicals_luca_order_then_energy_keyword")
def _life_earth_elsewhere_difficult_sms_chemicals_luca_order_then_energy_keyword():
    order_raw, order_bank = _u21_order_field(
        (
            "Useful chemicals (for example carbon compounds) are needed",
            "LUCA is a scientific model of a shared ancestor, not a named person in a book of kings",
        ),
        ("A social-media rumour is enough to prove life on a moon",),
    )
    question = (
        "<p>A fictional origins poster orders chemicals and the LUCA model for visitors.</p>"
        "<p>(i) Order useful chemicals, then the LUCA model.</p>"
        "<p>(ii) Using that sequence from (i), write the word for a source living things "
        "use to do work (sunlight or chemicals).</p>"
        "<p>(iii) There is no confirmed evidence of life beyond Earth in this course. "
        "Enter 1 for that honest claim.</p>"
    )
    solution = (
        "(i) <strong>chemicals → luca</strong><br>"
        "(ii) <strong>energy</strong><br>"
        "(iii) <strong>1</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order chemicals before LUCA, name energy, enter 1 "
        "for no confirmed life yet."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (order_raw, "energy", 1),
            ("Chemicals/LUCA order", "Work-source word", "No confirmed life (1)"),
            field_types=("order", "keyword", "number"),
            field_options=(order_bank, None, None),
            format_hint="Order chemicals then LUCA, enter energy, then 1.",
        ),
    )


LIFE_EARTH_ELSEWHERE_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _life_earth_elsewhere_intermediate_ms_luca_then_proxima_mcq,
        _life_earth_elsewhere_intermediate_ms_early_order_then_alien_pick,
        _life_earth_elsewhere_intermediate_ms_air_habitat_then_needs_count,
    ],
    "difficult": [
        _life_earth_elsewhere_difficult_ms_chemicals_then_habitat_keyword,
        _life_earth_elsewhere_difficult_ms_travel_order_then_rocket_mcq,
        _life_earth_elsewhere_difficult_ms_open_evidence_pick_then_ufo_mcq,
    ],
}

LIFE_EARTH_ELSEWHERE_SMS_POOLS = {
    "foundational": [
        _life_earth_elsewhere_foundational_sms_needs_three_then_water_mcq,
        _life_earth_elsewhere_foundational_sms_energy_water_order_then_pick,
        _life_earth_elsewhere_foundational_sms_travel_far_then_needs_keyword,
    ],
    "intermediate": [
        _life_earth_elsewhere_intermediate_sms_luca_poster_then_ufo_reject_mcq,
        _life_earth_elsewhere_intermediate_sms_proxima_years_then_claim_testable,
        _life_earth_elsewhere_intermediate_sms_early_earth_order_then_alien_pick,
    ],
    "difficult": [
        _life_earth_elsewhere_difficult_sms_habitat_four_then_travel_not_pick,
        _life_earth_elsewhere_difficult_sms_rocket_slow_chain_then_open_mcq,
        _life_earth_elsewhere_difficult_sms_chemicals_luca_order_then_energy_keyword,
    ],
}

# ---------------------------------------------------------------------------
# atoms_molecules — multi_step (F, I, D)
# ---------------------------------------------------------------------------


@_u21_variant("atoms_molecules", "ms", "foundational", "water_atoms_then_element_mcq")
def _atoms_molecules_foundational_ms_water_atoms_then_element_mcq():
    atoms = 3
    correct = "a substance made of only one type of atom"
    distractors = (
        "any mixture of different atoms",
        "a molecule of water only",
        "a unit of time",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional lab poster models water as H2O with 2 hydrogen and 1 oxygen atom.</p>"
        f"<p>(i) How many atoms are in one water molecule on that poster?</p>"
        "<p>(ii) Using that particle picture from (i), an element is</p>"
    )
    solution = (
        f"(i) <strong>{atoms}</strong> atoms<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Add 2 H and 1 O, then define an element as one "
        "type of atom."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (atoms, letter),
            ("Atoms in H2O", "Element meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count three atoms, then choose the element definition.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "foundational", "atom_box_then_particle_order")
def _atoms_molecules_foundational_ms_atom_box_then_particle_order():
    diagram = str(atom_molecule_boxes(title="Fictional single atom"))
    order_raw, order_bank = _u21_order_field(
        (
            "Matter is made of particles that are still there when you cannot see them",
            "An element is a substance with only one type of atom",
        ),
        ("Atoms vanish when a solid melts and new magic atoms appear",),
    )
    question = (
        diagram
        + "<p>A fictional particle-model wall chart uses this sketch.</p>"
        "<p>(i) Which letter is a single atom?</p>"
        "<p>(ii) Using that single-atom box from (i), order particles-always-there, "
        "then element as one type of atom.</p>"
    )
    solution = (
        "(i) <strong>A</strong> is one atom<br>"
        "(ii) <strong>particles → element</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> A is one atom; order persistent particles before "
        "one-type-of-atom element."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("A", order_raw),
            ("Single-atom letter", "Particle-model order"),
            field_types=("keyword", "order"),
            field_options=(None, order_bank),
            format_hint="Enter A, then order particles before element.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "foundational", "symbol_o_then_atom_keyword")
def _atoms_molecules_foundational_ms_symbol_o_then_atom_keyword():
    hydrogen = 2
    question = (
        "<p>A fictional elements poster shows O for oxygen and H2O for water.</p>"
        "<p>(i) How many hydrogen atoms are in one water molecule?</p>"
        "<p>(ii) Using that H2O count from (i), write the word for a single particle "
        "of an element in this S2 model.</p>"
    )
    solution = (
        f"(i) <strong>{hydrogen}</strong><br>"
        "(ii) <strong>atom</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count two hydrogens in H2O, then name atom."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (hydrogen, "atom"),
            ("Hydrogen atoms in H2O", "Single-particle word"),
            field_types=("number", "keyword"),
            format_hint="Enter 2, then atom.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "intermediate", "h_in_water_then_mol_box_mcq")
def _atoms_molecules_intermediate_ms_h_in_water_then_mol_box_mcq():
    diagram = str(atom_molecule_boxes(title="Fictional molecule box"))
    hydrogen = 2
    correct = "B"
    distractors = ("A", "C", "the empty page")
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional bonding worksheet pairs H2O counting with particle boxes.</p>"
        f"<p>(i) How many hydrogen atoms are in the water-molecule model?</p>"
        "<p>(ii) Using that joined-particle idea from (i), which letter is two atoms "
        "joined as a molecule?</p>"
    )
    solution = (
        f"(i) <strong>{hydrogen}</strong><br>"
        "(ii) <strong>B</strong> is the molecule"
    )
    hint = (
        "<strong>Key idea:</strong> Count two H in water; B shows two joined atoms."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (hydrogen, letter),
            ("Hydrogen count", "Molecule box letter"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 2, then choose B.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "intermediate", "word_eq_then_conservation_mcq")
def _atoms_molecules_intermediate_ms_word_eq_then_conservation_mcq():
    reactants = 2
    correct = "are rearranged; the counts should match"
    distractors = (
        "appear from nowhere as a new element",
        "leave the universe",
        "become light-years",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional reaction poster shows hydrogen + oxygen → water as a word equation.</p>"
        f"<p>(i) How many reactant names appear before the arrow?</p>"
        "<p>(ii) Using that closed reaction story from (i), atoms in the mixture</p>"
    )
    solution = (
        f"(i) <strong>{reactants}</strong> reactants<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count hydrogen and oxygen before the arrow, then "
        "choose conservation by rearrangement."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (reactants, letter),
            ("Reactant count", "Atom conservation rule"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Enter 2 reactants, then choose rearrangement conservation.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "intermediate", "mol_order_then_sym_pick")
def _atoms_molecules_intermediate_ms_mol_order_then_sym_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "An atom is a single particle of an element in this S2 model",
            "A molecule is atoms joined together",
        ),
        ("The letters in a symbol are a sentence about the weather",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("atom", "molecule"), _MOL_BANK),
        2,
    )
    question = (
        "<p>A fictional lab symbols sheet orders atom and molecule ideas.</p>"
        "<p>(i) Order single atom, then joined molecule.</p>"
        "<p>(ii) Using that order from (i), select atom and molecule.</p>"
    )
    solution = (
        "(i) <strong>atom → molecule</strong><br>"
        "(ii) Atom and molecule are selected."
    )
    hint = (
        "<strong>Key idea:</strong> Order atom before molecule, then pick both terms."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Atom/molecule order", "Atom and molecule"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order atom then molecule, select both.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "difficult", "co2_rearrange_then_fe_keyword")
def _atoms_molecules_difficult_ms_co2_rearrange_then_fe_keyword():
    oxygen = 1
    question = (
        "<p>A fictional combustion poster shows carbon + oxygen → carbon dioxide.</p>"
        f"<p>(i) How many oxygen atoms are in one water molecule in this lesson's model?</p>"
        "<p>(ii) The same poster notes atoms rearrange, not vanish. Enter 1 for that rule.</p>"
        "<p>(iii) Using that conservation idea from (ii), the symbol Fe stands for which element? "
        "Enter iron as one word.</p>"
    )
    solution = (
        f"(i) <strong>{oxygen}</strong><br>"
        "(ii) <strong>1</strong><br>"
        "(iii) <strong>iron</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> One O in H2O, enter 1 for conservation, Fe is iron."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (oxygen, 1, "iron"),
            ("Oxygen in H2O", "Conservation rule (1)", "Fe element"),
            field_types=("number", "number", "keyword"),
            format_hint="Enter 1, 1, then iron.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "difficult", "mix_box_then_not_element_mcq")
def _atoms_molecules_difficult_ms_mix_box_then_not_element_mcq():
    diagram = str(atom_molecule_boxes(title="Fictional mixed jumble"))
    correct = (
        "an element needs one type of atom, not a jumble"
    )
    distractors = (
        "elements cannot be drawn",
        "molecules are forbidden",
        "symbols must be sentences",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional particle quiz uses this sketch of mixed particles.</p>"
        "<p>(i) Which letter is a mixed jumble of different particles?</p>"
        "<p>(ii) Using that mixed box from (i), it is not an element because</p>"
    )
    solution = (
        "(i) <strong>C</strong> is mixed<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> C is the jumble; an element needs one atom type."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("C", letter),
            ("Mixed box letter", "Why not an element"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Enter C, then choose one-type-of-atom rule.",
        ),
    )


@_u21_variant("atoms_molecules", "ms", "difficult", "rxn_order_then_rearrange_pick")
def _atoms_molecules_difficult_ms_rxn_order_then_rearrange_pick():
    order_raw, order_bank = _u21_order_field(
        (
            "A reaction rearranges atoms; it does not create elements from nothing",
            "A word equation names the reactants and products",
        ),
        ("Burning destroys all atoms so none remain",),
    )
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("rearrange", "word"), _RXN_BANK),
        2,
    )
    question = (
        "<p>A fictional conservation poster orders reaction ideas for a closed system.</p>"
        "<p>(i) Order rearrangement of atoms, then writing a word equation.</p>"
        "<p>(ii) Using that sequence from (i), select rearrangement and word equation.</p>"
    )
    solution = (
        "(i) <strong>rearrange → word</strong><br>"
        "(ii) Rearrangement and word equation are selected."
    )
    hint = (
        "<strong>Key idea:</strong> Order what happens before how we write it, then "
        "pick those two ideas."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Reaction order", "Reaction ideas"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order rearrange then word equation, select both.",
        ),
    )


# atoms_molecules — situational_multi_step (F, I, D)

_AM_SMS_F_LAB_PACKS = (
    {"who": "Alex", "place": "fictional school science lab"},
    {"who": "Sam", "place": "fictional chemistry fair booth"},
    {"who": "Jordan", "place": "fictional particle-model museum corner"},
)


@_u21_variant("atoms_molecules", "sms", "foundational", "lab_poster_atoms_then_water_n")
def _atoms_molecules_foundational_sms_lab_poster_atoms_then_water_n():
    pack = random.choice(_AM_SMS_F_LAB_PACKS)
    atoms = 3
    question = (
        f"<p>At a {pack['place']}, {pack['who']} hangs a poster showing H2O as "
        "2 hydrogen joined to 1 oxygen.</p>"
        "<p>(i) Write the word for a single particle of an element.</p>"
        f"<p>(ii) Using that particle word from (i), how many atoms are in one water "
        "molecule on the poster?</p>"
    )
    solution = (
        "(i) <strong>atom</strong><br>"
        f"(ii) <strong>{atoms}</strong> atoms"
    )
    hint = (
        "<strong>Key idea:</strong> Name atom first, then count 2 H + 1 O."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("atom", atoms),
            ("Single-particle word", "Atoms in H2O"),
            field_types=("keyword", "number"),
            format_hint="Enter atom, then 3.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "foundational", "element_molecule_pick_then_atom_box")
def _atoms_molecules_foundational_sms_element_molecule_pick_then_atom_box():
    diagram = str(atom_molecule_boxes(title="Fictional atom box"))
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("particles", "element"), _PART_BANK),
        2,
    )
    question = (
        diagram
        + "<p>A fictional lab open day lists particle-model facts beside this sketch.</p>"
        "<p>(i) Select persistent particles and one-type-of-atom element ideas.</p>"
        "<p>(ii) Using those picks from (i), which letter is a single atom?</p>"
    )
    solution = (
        "(i) Particles and element are selected.<br>"
        "(ii) <strong>A</strong> is one atom"
    )
    hint = (
        "<strong>Key idea:</strong> Pick particles and element, then A is the lone atom."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, "A"),
            ("Particle-model ideas", "Single-atom letter"),
            field_types=("pick", "keyword"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two ideas, then enter A.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "foundational", "particles_order_then_h2o_mcq")
def _atoms_molecules_foundational_sms_particles_order_then_h2o_mcq():
    order_raw, order_bank = _u21_order_field(
        (
            "Matter is made of particles that are still there when you cannot see them",
            "An element is a substance with only one type of atom",
        ),
        ("A jumble of different particles is not a single element",),
    )
    correct = "hydrogen and oxygen atoms joined"
    distractors = (
        "one atom of iron",
        "a mixture of eight planets",
        "empty space with no particles",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional lab poster orders particle facts before water models.</p>"
        "<p>(i) Order particles-always-there, then element as one type of atom.</p>"
        "<p>(ii) Using that particle model from (i), a water molecule is modelled as</p>"
    )
    solution = (
        "(i) <strong>particles → element</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order particle facts, then choose H and O joined."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Particle order", "Water molecule model"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order particle facts, then choose H and O joined.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "intermediate", "join_bond_then_mol_word")
def _atoms_molecules_intermediate_sms_join_bond_then_mol_word():
    joined = 2
    question = (
        "<p>A fictional bonding demo joins two hydrogen atoms as one particle.</p>"
        f"<p>(i) How many atoms are joined in that demo molecule?</p>"
        "<p>(ii) Using that joined pair from (i), the atoms are still there, now bonded. "
        "Enter 1 for that rule.</p>"
        "<p>(iii) Write the word for atoms joined together.</p>"
    )
    solution = (
        f"(i) <strong>{joined}</strong><br>"
        "(ii) <strong>1</strong><br>"
        "(iii) <strong>molecule</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count two joined atoms, enter 1 for still-there, "
        "name molecule."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (joined, 1, "molecule"),
            ("Atoms joined", "Still there when bonded (1)", "Joined-atoms word"),
            field_types=("number", "number", "keyword"),
            format_hint="Enter 2, 1, then molecule.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "intermediate", "mix_jumble_then_word_eq_mcq")
def _atoms_molecules_intermediate_sms_mix_jumble_then_word_eq_mcq():
    diagram = str(atom_molecule_boxes(title="Fictional mixed particles"))
    correct = "hydrogen + oxygen → water"
    distractors = (
        "water → hydrogen + oxygen only as a creation spell",
        "Sun + Moon → water",
        "rotation + season → water",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional lab wall shows mixed particles and a water word equation.</p>"
        "<p>(i) Which letter is a mixed jumble of different particles?</p>"
        "<p>(ii) Using that mixture idea from (i), the correct word equation for making "
        "water is</p>"
    )
    solution = (
        "(i) <strong>C</strong> is mixed<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> C is the jumble; reactants go before the arrow."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            ("C", letter),
            ("Mixed box letter", "Water word equation"),
            field_types=("keyword", "mcq"),
            field_options=(None, options),
            format_hint="Enter C, then choose hydrogen + oxygen → water.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "intermediate", "h_symbol_chain_then_mol_box")
def _atoms_molecules_intermediate_sms_h_symbol_chain_then_mol_box():
    diagram = str(atom_molecule_boxes(title="Fictional joined atoms"))
    hydrogen = 2
    question = (
        "<p>A fictional symbols quiz chains H, O and joined particles.</p>"
        "<p>(i) The symbol H stands for hydrogen. Enter 1 if that is true in this lesson.</p>"
        f"<p>(ii) How many hydrogen atoms are in one water molecule?</p>"
        + diagram
        + "<p>(iii) Using that H2O count from (ii), which letter is two atoms joined as a molecule?</p>"
    )
    solution = (
        "(i) <strong>1</strong><br>"
        f"(ii) <strong>{hydrogen}</strong><br>"
        "(iii) <strong>B</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Enter 1 for H = hydrogen, count two H in water, B is joined."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (1, hydrogen, "B"),
            ("H is hydrogen (1)", "Hydrogen in H2O", "Molecule letter"),
            field_types=("number", "number", "keyword"),
            format_hint="Enter 1, 2, then B.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "difficult", "burn_h2o_chain_then_o_count")
def _atoms_molecules_difficult_sms_burn_h2o_chain_then_o_count():
    oxygen = 1
    correct = (
        "rearranging hydrogen and oxygen atoms into water molecules"
    )
    distractors = (
        "destroying hydrogen atoms forever",
        "creating iron atoms from light",
        "a season on Earth",
    )
    options, letter = _u21_mcq_field(correct, distractors)
    question = (
        "<p>A fictional combustion demo burns hydrogen in oxygen to make water.</p>"
        f"<p>(i) How many oxygen atoms are in one water molecule?</p>"
        "<p>(ii) Enter 1 if atoms are conserved by rearrangement in a closed story.</p>"
        "<p>(iii) Using that conservation rule from (ii), burning hydrogen in oxygen is best described as</p>"
    )
    solution = (
        f"(i) <strong>{oxygen}</strong><br>"
        "(ii) <strong>1</strong><br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> One O in H2O, enter 1 for conservation, choose rearrangement."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (oxygen, 1, letter),
            ("Oxygen in H2O", "Conservation (1)", "Combustion description"),
            field_types=("number", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Enter 1, 1, then choose rearrangement into water.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "difficult", "count_conservation_then_mix_box")
def _atoms_molecules_difficult_sms_count_conservation_then_mix_box():
    diagram = str(atom_molecule_boxes(title="Fictional mixture box"))
    products = 2
    question = (
        "<p>A fictional count story says 2 hydrogen molecules and 1 oxygen molecule "
        "make 2 water molecules if counts match.</p>"
        f"<p>(i) How many water molecules are named as products?</p>"
        "<p>(ii) Atoms are conserved: they change partners. Enter 1 for that rule.</p>"
        + diagram
        + "<p>(iii) Using that conservation idea from (ii), which letter is a mixed jumble "
        "of different particles (not one element)?</p>"
    )
    solution = (
        f"(i) <strong>{products}</strong><br>"
        "(ii) <strong>1</strong><br>"
        "(iii) <strong>C</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Two water products, enter 1 for conservation, C is mixed."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (products, 1, "C"),
            ("Water molecules", "Conservation (1)", "Mixed box letter"),
            field_types=("number", "number", "keyword"),
            format_hint="Enter 2, 1, then C.",
        ),
    )


@_u21_variant("atoms_molecules", "sms", "difficult", "rxn_pick_then_el_keyword")
def _atoms_molecules_difficult_sms_rxn_pick_then_el_keyword():
    pick_raw, pick_bank, pick_count = _u21_pick_field(
        *_bank_pick(("rearrange", "word"), _RXN_BANK),
        2,
    )
    question = (
        "<p>A fictional reaction review poster contrasts real equations with magic-spell claims.</p>"
        "<p>(i) Select rearrangement of atoms and word equation ideas.</p>"
        "<p>(ii) Using those reaction ideas from (i), write the word for a substance made "
        "of only one type of atom.</p>"
        "<p>(iii) Box C in the particle sketch is a mixture, not an element. Enter C.</p>"
    )
    solution = (
        "(i) Rearrangement and word equation are selected.<br>"
        "(ii) <strong>element</strong><br>"
        "(iii) <strong>C</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Pick rearrange and word equation, name element, enter C."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (pick_raw, "element", "C"),
            ("Reaction ideas", "One-type-of-atom word", "Mixture box letter"),
            field_types=("pick", "keyword", "keyword"),
            field_options=(pick_bank, None, None),
            field_pick_counts=(pick_count, None, None),
            format_hint="Select two ideas, enter element, then C.",
        ),
    )


ATOMS_MOLECULES_MS_POOLS = {
    "foundational": [
        _atoms_molecules_foundational_ms_water_atoms_then_element_mcq,
        _atoms_molecules_foundational_ms_atom_box_then_particle_order,
        _atoms_molecules_foundational_ms_symbol_o_then_atom_keyword,
    ],
    "intermediate": [
        _atoms_molecules_intermediate_ms_h_in_water_then_mol_box_mcq,
        _atoms_molecules_intermediate_ms_word_eq_then_conservation_mcq,
        _atoms_molecules_intermediate_ms_mol_order_then_sym_pick,
    ],
    "difficult": [
        _atoms_molecules_difficult_ms_co2_rearrange_then_fe_keyword,
        _atoms_molecules_difficult_ms_mix_box_then_not_element_mcq,
        _atoms_molecules_difficult_ms_rxn_order_then_rearrange_pick,
    ],
}

ATOMS_MOLECULES_SMS_POOLS = {
    "foundational": [
        _atoms_molecules_foundational_sms_lab_poster_atoms_then_water_n,
        _atoms_molecules_foundational_sms_element_molecule_pick_then_atom_box,
        _atoms_molecules_foundational_sms_particles_order_then_h2o_mcq,
    ],
    "intermediate": [
        _atoms_molecules_intermediate_sms_join_bond_then_mol_word,
        _atoms_molecules_intermediate_sms_mix_jumble_then_word_eq_mcq,
        _atoms_molecules_intermediate_sms_h_symbol_chain_then_mol_box,
    ],
    "difficult": [
        _atoms_molecules_difficult_sms_burn_h2o_chain_then_o_count,
        _atoms_molecules_difficult_sms_count_conservation_then_mix_box,
        _atoms_molecules_difficult_sms_rxn_pick_then_el_keyword,
    ],
}
