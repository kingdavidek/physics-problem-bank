"""S2 Unit 2.1 Universe — 2.1.1–2.1.4."""
from generators.eursc.science_shared import (
    bind_eursc_topic,
    atom_molecule_boxes,
    earth_sun_moon,
    reflection_rays,
)
from generators.shared.utils import (
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)

_LEVEL = "eursc"
_SUBJECT = "science"


def _topic_bank(topic):
    def mcq(difficulty, suffix, question, options, answer, solution, hint):
        def _fn():
            return make_problem(
                question,
                solution,
                hint,
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

    def typed(difficulty, suffix, kind, question, extra, solution, hint):
        def _fn():
            payload = (
                problem_extra_from_graded_answer(extra)
                if extra.get("type")
                else dict(extra)
            )
            return make_problem(
                question,
                solution,
                hint,
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

    def number(difficulty, suffix, question, value, solution, hint):
        return typed(
            difficulty,
            suffix,
            "number",
            question,
            {"type": "number", "value": value},
            solution,
            hint,
        )

    def keyword(difficulty, suffix, question, value, solution, hint):
        return typed(
            difficulty,
            suffix,
            "keyword",
            question,
            {"type": "keyword", "value": value},
            solution,
            hint,
        )

    def order(difficulty, suffix, question, required_ids, bank, solution, hint):
        return typed(
            difficulty,
            suffix,
            "order",
            question,
            proof_steps_answer(required_ids, bank, order_matters=True),
            solution,
            hint,
        )

    def pick(difficulty, suffix, question, required_ids, bank, pick_count, solution, hint):
        return typed(
            difficulty,
            suffix,
            "pick",
            question,
            proof_steps_answer(required_ids, bank, pick_count=pick_count),
            solution,
            hint,
        )

    return mcq, number, keyword, order, pick


def _mcq_opts(a, b, c, d):
    return [f"A  {a}", f"B  {b}", f"C  {c}", f"D  {d}"]


_SS_MCQ, _SS_NUM, _SS_KEY, _SS_ORD, _SS_PICK = _topic_bank("solar_system")
_LT_MCQ, _LT_NUM, _LT_KEY, _LT_ORD, _LT_PICK = _topic_bank("light_telescopes")
_LF_MCQ, _LF_NUM, _LF_KEY, _LF_ORD, _LF_PICK = _topic_bank("life_earth_elsewhere")
_AM_MCQ, _AM_NUM, _AM_KEY, _AM_ORD, _AM_PICK = _topic_bank("atoms_molecules")

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

_SS_POOLS = {
    "foundational": [
        _SS_MCQ("foundational", "rotate", "Rotation of Earth is", _mcq_opts("Earth orbiting the Sun", "Earth spinning on its axis", "the Moon becoming a star", "the universe shrinking"), "B", "Rotation is spin on an axis.", "Think about Earth turning on the line through its poles, not about going around the Sun."),
        _SS_MCQ("foundational", "revolve", "Revolution of Earth is", _mcq_opts("Earth spinning once in a minute", "Earth orbiting the Sun, taking about a year", "the Sun orbiting a city", "a season caused by the Moon's colour"), "B", "Revolution is the yearly orbit.", "This is the yearly trip around the Sun, not the daily spin."),
        _SS_MCQ("foundational", "moon_see", "We see the Moon because", _mcq_opts("it is a second Sun", "it reflects sunlight", "it burns hydrogen in a classroom", "cities vote it alight"), "B", "Reflected sunlight.", "The Moon does not make its own daylight. What kind of light reaches your eye from it?"),
        _SS_MCQ("foundational", "planets_n", "How many planets are counted in the Solar System in this course?", _mcq_opts("two", "eight", "eighty", "one"), "B", "Eight planets orbit the Sun.", "Count the planets that orbit the Sun in the classroom model — not moons, not stars."),
        _SS_MCQ("foundational", "au", "An astronomical unit (AU) is a scale for", _mcq_opts("the mass of a classroom apple", "distances in the Solar System, based on the Earth–Sun distance", "the temperature of a star in °C only", "the number of moons on Earth"), "B", "1 AU is the Earth–Sun distance.", "This unit is a yardstick for how far planets sit from the Sun, based on our own orbit."),
        _SS_MCQ("foundational", "earth_letter", "<p>Which letter is Earth in this schematic (sizes not to scale)?</p>" + str(earth_sun_moon(title="Earth letter")), _mcq_opts("A", "B", "C", "none of the letters"), "B", "B is Earth.", "On the schematic, Earth is the planet between the Sun and the Moon — match that box to a letter."),
        _SS_KEY("foundational", "spin_word", "Write the word for a planet spinning on its own axis.", "rotation", "Rotation is spin, not the yearly orbit.", "Name the spin of a planet on the line through its poles, not the yearly path around the Sun."),
        _SS_NUM("foundational", "eight", "Enter the number of planets in the Solar System used in this lesson.", 8, "Eight planets.", "Count only the planets in this lesson's Solar System list — not moons or dwarf worlds."),
        _SS_ORD("foundational", "spin_then_orbit", "Order rotation of Earth, then revolution around the Sun.", ["rotate", "revolve"], _SPIN_BANK, "Spin first, then the yearly orbit.", "Put daily spin first, then the yearly trip around the Sun. Skip fame as a cause."),
        _SS_PICK("foundational", "spin_ok", "Select the two correct spin-and-orbit ideas.", ["rotate", "revolve"], _SPIN_BANK, 2, "Rotation and revolution. Fame is not a cause.", "Choose the spin-on-an-axis idea and the orbit-around-the-Sun idea. A celebrity is not a cause."),
    ],
    "intermediate": [
        _SS_MCQ("intermediate", "day", "One rotation of Earth takes about", _mcq_opts("one year", "one day", "one century", "one light-year of time"), "B", "A day is one spin.", "How long does one full spin of Earth take in everyday time?"),
        _SS_MCQ("intermediate", "year", "One revolution of Earth around the Sun takes about", _mcq_opts("one hour", "one year", "one minute", "eight minutes of moonlight"), "B", "A year is one orbit.", "How long does one full trip of Earth around the Sun take?"),
        _SS_MCQ("intermediate", "tilt", "Seasons on Earth happen mainly because", _mcq_opts("the Moon turns off in winter", "Earth's axis is tilted as Earth orbits the Sun", "the Sun moves to a different galaxy each June", "cities are closer to Mars in July"), "B", "Tilt plus orbit.", "Summer and winter are not because the Moon switches off. Think about Earth's axis as it goes around the Sun."),
        _SS_MCQ("intermediate", "july_far", "Earth is slightly farther from the Sun in July than in January. July is still summer in the north because", _mcq_opts("distance to the Sun is the only cause of seasons", "the northern hemisphere is tilted toward the Sun then", "the Moon becomes a second Sun", "the universe stops expanding in July"), "B", "Tilt, not a tiny distance change, drives seasons.", "July is a tiny bit farther from the Sun, yet the north is warm. Which hemisphere is leaning toward the sunlight then?"),
        _SS_MCQ("intermediate", "moon_orbit", "The Moon is", _mcq_opts("a star that Earth orbits", "a natural satellite that orbits Earth", "an eighth planet beyond Neptune", "a geocentric vote"), "B", "Natural satellite.", "What kind of natural body goes around Earth, not the other way around?"),
        _SS_MCQ("intermediate", "sun_letter", "<p>Which letter is the Sun?</p>" + str(earth_sun_moon(title="Sun letter")), _mcq_opts("B", "A", "C", "the word Moon"), "B", "A is the Sun.", "On the schematic, find the central star and match that box to a letter."),
        _SS_KEY("intermediate", "orbit_word", "Write the word for the path a planet follows around the Sun.", "orbit", "An orbit is the path of revolution.", "Name the path a planet follows as it goes around the Sun — one word, not 'spin'."),
        _SS_NUM("intermediate", "tilt_deg", "This lesson uses about how many degrees for Earth's axial tilt? Enter the whole number.", 23, "About 23°.", "The lesson quotes Earth's lean as a whole number of degrees, a bit more than twenty."),
        _SS_ORD("intermediate", "season_ord", "Order axial tilt, then more direct sunlight in that hemisphere's summer.", ["tilt", "sunlight"], _SEASON_BANK, "Tilt, then the sunlight pattern.", "First the axis leaning as Earth goes around the Sun, then the hemisphere that gets more direct sunlight in its summer."),
        _SS_PICK("intermediate", "moon_ok", "Select the two Moon facts.", ["satellite", "reflect"], _MOON_BANK, 2, "Satellite and reflected sunlight.", "Choose the idea that the Moon goes around Earth, and the idea that we see it by bounced sunlight."),
    ],
    "difficult": [
        _SS_MCQ("difficult", "expand", "Public evidence that the universe is expanding includes", _mcq_opts("a vote in a classroom", "distant galaxies receding; the model can be checked", "the Moon burning as a second Sun", "seasons happening only in one city"), "B", "Galaxy spectra / recession, not authority.", "Look for public evidence such as distant galaxies moving away, not a classroom vote."),
        _SS_MCQ("difficult", "age", "The age of the universe in this S2 model is of the order of", _mcq_opts("fourteen days", "fourteen billion years", "fourteen minutes", "eight planets"), "B", "About 14 billion years.", "The S2 model uses billions of years, not days or the planet count."),
        _SS_MCQ("difficult", "helio", "A heliocentric model of the Solar System puts", _mcq_opts("Earth at the centre with the Sun orbiting it", "the Sun at the centre with planets orbiting it", "the Moon at the centre of the universe", "authority at the centre instead of evidence"), "B", "Sun-centred.", "Which body sits at the centre, with the planets going around it?"),
        _SS_MCQ("difficult", "geo_why", "The geocentric model was replaced because", _mcq_opts("it was newer so it had to stay", "new evidence (for example planetary motions) fitted a Sun-centred model better", "planets voted", "the Moon asked for a new name"), "B", "Evidence, not age of the idea.", "Older ideas were dropped because new observations fitted a different centre better — not because planets voted."),
        _SS_MCQ("difficult", "scale", "On a scale where Earth–Sun is 1 AU, the Earth–Moon distance is", _mcq_opts("also 1 AU", "much smaller than 1 AU", "larger than the distance to the nearest other star", "equal to fourteen billion years"), "B", "The Moon is nearby on an AU scale.", "The Moon is a nearby neighbour. Compared with the Earth–Sun yardstick, is that gap huge or tiny?"),
        _SS_MCQ("difficult", "moon_letter", "<p>Which letter is the Moon?</p>" + str(earth_sun_moon(title="Moon letter")), _mcq_opts("A", "C", "B", "the Sun box"), "B", "C is the Moon.", "On the schematic, find Earth's natural satellite and match that box to a letter."),
        _SS_KEY("difficult", "season_word", "Write the word for the yearly pattern of summer and winter caused by tilt and orbit.", "season", "Seasons come from tilt plus revolution.", "Name the yearly summer-and-winter pattern that comes from lean plus going around the Sun."),
        _SS_NUM("difficult", "age_n", "Enter the whole number of billions of years used in this lesson for the age of the universe.", 14, "About 14 billion years.", "The lesson quotes the universe's age as a whole number of billions of years — a bit more than ten."),
        _SS_ORD("difficult", "models", "Order the Earth-centred model, then the Sun-centred model.", ["geo", "helio"], _MODEL_BANK, "Geocentric, then heliocentric.", "Put the Earth-centred picture first, then the Sun-centred picture."),
        _SS_PICK("difficult", "scale_ok", "Select the two scale ideas that belong in this lesson.", ["au", "planets"], _SCALE_BANK, 2, "AU and eight planets at different distances.", "Choose the Earth–Sun yardstick and the idea that the eight planets sit at different distances."),
    ],
}

_SS_STANDARD = {
    "foundational": (
        'solar_system_foundational_mcq_au',
        'solar_system_foundational_keyword_spin_word',
        'solar_system_foundational_number_eight',
        'solar_system_foundational_order_spin_then_orbit',
        'solar_system_foundational_pick_spin_ok',
    ),
    "intermediate": (
        'solar_system_intermediate_mcq_day',
        'solar_system_intermediate_keyword_orbit_word',
        'solar_system_intermediate_number_tilt_deg',
        'solar_system_intermediate_order_season_ord',
        'solar_system_intermediate_pick_moon_ok',
    ),
    "difficult": (
        'solar_system_difficult_mcq_age',
        'solar_system_difficult_keyword_season_word',
        'solar_system_difficult_number_age_n',
        'solar_system_difficult_order_models',
        'solar_system_difficult_pick_scale_ok',
    ),
}
eursc_science_solar_system, eursc_science_solar_system_variants = bind_eursc_topic(
    'solar_system', _SS_POOLS, _SS_STANDARD
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

_LT_POOLS = {
    "foundational": [
        _LT_MCQ("foundational", "straight", "In air, a ray of light is modelled as travelling", _mcq_opts("in random loops only", "in a straight line unless it hits a new surface or medium", "only through metal", "only at night"), "B", "Straight-line rays.", "In air, a ray is drawn as a straight line until it meets a new surface or a new material."),
        _LT_MCQ("foundational", "speed", "A rounded speed of light used in this lesson is", _mcq_opts("3 km/s", "300000 km/s", "8 m/s", "14 km/s"), "B", "About 300000 km/s.", "The classroom figure is hundreds of thousands of kilometres each second, not a walking pace."),
        _LT_MCQ("foundational", "ly", "A light-year is", _mcq_opts("a unit of time like a minute", "the distance light travels in one year", "the mass of the Sun", "the tilt of Earth in degrees"), "B", "Distance, not time.", "The word 'year' in the name is the travel time used to define a length, not a clock unit."),
        _LT_MCQ("foundational", "shadow", "A sharp shadow of a book on a table is explained by", _mcq_opts("the book voting for darkness", "the book blocking light that travels in straight lines", "the Moon becoming a star", "sound taking eight minutes"), "B", "Opaque object, straight rays.", "An opaque book stops light that travels in straight lines. That blocked region is the shadow."),
        _LT_MCQ("foundational", "reflect_eq", "At a plane mirror, the angle of reflection", _mcq_opts("is always 90° more than incidence", "equals the angle of incidence", "is zero if the room is quiet", "depends on the planet count"), "B", "i = r.", "At a flat mirror, the incoming angle and the outgoing angle match."),
        _LT_MCQ("foundational", "incident", "<p>Which letter is the incident ray?</p>" + str(reflection_rays(title="Incident ray")), _mcq_opts("B", "A", "C", "the dashed normal only"), "B", "A is incident.", "On the ray diagram, find the arrow heading toward the mirror and match that ray to a letter."),
        _LT_KEY("foundational", "reflect_word", "Write the word for light bouncing off a mirror.", "reflection", "Reflection at a surface.", "Name what happens when light bounces off a mirror, not when it bends into glass."),
        _LT_NUM("foundational", "c_kms", "Enter the rounded speed of light in km/s used in this lesson.", 300000, "300000 km/s.", "Think hundreds of thousands of kilometres each second. Enter the lesson's rounded whole number in km/s."),
        _LT_ORD("foundational", "travel", "Order straight-line travel, then the high speed of light.", ["straight", "speed"], _RAY_BANK, "Straight rays, then the huge speed.", "Put straight-line travel first, then the huge speed figure."),
        _LT_PICK("foundational", "shadow_ok", "Select the two shadow ideas.", ["block", "rays"], _SHADOW_BANK, 2, "Block plus straight rays.", "Choose blocking of light by an opaque object, and straight-line rays that explain the shadow's shape."),
    ],
    "intermediate": [
        _LT_MCQ("intermediate", "two_s", "Light travels 300000 km in 1 s. In 2 s it travels", _mcq_opts("150000 km", "600000 km", "300000 km", "2 km"), "B", "2 × 300000 = 600000 km.", "If light covers that many kilometres in one second, the distance in two seconds is twice as far."),
        _LT_MCQ("intermediate", "ly_not_time", "Calling a light-year a time is wrong because", _mcq_opts("light does not move", "the name uses a year to measure a distance", "the Sun is 1 AU from the Moon", "eclipses last fourteen billion years"), "B", "The year is the travel-time used to define a distance.", "A year here is how long the light travels while you measure a distance, not a time you write on a clock."),
        _LT_MCQ("intermediate", "phase", "A Moon phase is", _mcq_opts("the Moon turning into a planet", "how much of the sunlit half of the Moon we can see from Earth", "a solar eclipse every night", "the speed of light in km/s"), "B", "Geometry of sunlight and viewpoint.", "From Earth we see different amounts of the Moon's sunlit half. That changing view is a phase."),
        _LT_MCQ("intermediate", "eclipse", "A solar eclipse can happen when", _mcq_opts("the Moon is a second Sun", "the Moon passes between the Sun and Earth and the shadow hits Earth", "Earth's axis has no tilt", "light travels in loops"), "B", "Alignment and shadow.", "A solar eclipse needs the Moon's shadow to fall on Earth — a special line-up, not the Moon turning into a star."),
        _LT_MCQ("intermediate", "refract", "Refraction is", _mcq_opts("light bouncing with i = r always in glass", "a change of direction when light goes into a different medium", "a lens creating extra photons from fame", "the Moon absorbing the Sun"), "B", "New medium, new direction.", "When light enters glass or water it can change direction. That is not the same as bouncing with equal angles."),
        _LT_MCQ("intermediate", "reflected", "<p>Which letter is the reflected ray?</p>" + str(reflection_rays(title="Reflected ray")), _mcq_opts("A", "B", "C", "the Sun"), "B", "B is reflected.", "On the ray diagram, find the arrow leaving the mirror and match that ray to a letter."),
        _LT_KEY("intermediate", "refract_word", "Write the word for light changing direction as it enters glass or water.", "refraction", "Refraction, not reflection.", "Name the change of direction as light enters a new material such as glass or water."),
        _LT_NUM("intermediate", "two_sec", "Light travels 300000 km each second. How many km in 2 s?", 600000, "600000 km.", "Each second covers 300000 km. For two seconds, scale that distance up by the number of seconds."),
        _LT_ORD("intermediate", "eclipse_ord", "Order Moon phases as viewpoint, then eclipse as alignment.", ["phase", "align"], _ECLIPSE_BANK, "Phases first, then rare alignment.", "Put the changing view of the sunlit Moon first, then the rare line-up that makes an eclipse."),
        _LT_PICK("intermediate", "optic_two", "Select reflection equality and refraction.", ["reflect", "refract"], _OPTIC_BANK, 2, "i = r and refraction.", "Choose equal incoming and outgoing angles at a mirror, and the change of direction in a new material."),
    ],
    "difficult": [
        _LT_MCQ("difficult", "angle40", "If the angle of incidence is 40°, the angle of reflection at a plane mirror is", _mcq_opts("50°", "40°", "90°", "0°"), "B", "i = r = 40°.", "At a plane mirror the two angles match. The incoming angle is already given."),
        _LT_MCQ("difficult", "colour", "A blue object in white light looks blue mainly because", _mcq_opts("it emits a new kind of darkness", "it reflects blue light and absorbs other colours", "the eye votes for blue", "the Moon filters all red in space"), "B", "Selective reflection.", "A blue object in white light sends blue toward your eye and keeps the other colours."),
        _LT_MCQ("difficult", "filter", "A green filter in front of a lamp", _mcq_opts("adds extra green light from nothing", "transmits green and absorbs other colours", "reflects every colour equally into the eye as white", "stops light having a speed"), "B", "Transmission of green.", "A green filter lets green through and soaks up the other colours — it does not invent extra light."),
        _LT_MCQ("difficult", "lens", "A convex lens in a simple telescope is used to", _mcq_opts("create mass for a planet", "gather light and change its direction so an image can be formed", "replace the need for a classroom investigation", "make a light-year into a minute"), "B", "Gather and focus.", "A convex lens gathers light and bends it so an image can form. It does not create mass or extra photons from nothing."),
        _LT_MCQ("difficult", "sun_scope", "Looking at the Sun through a telescope or binoculars is", _mcq_opts("a safe way to measure 300000 km/s", "dangerous; never do it — follow the teacher's solar-viewing rules", "the only way to see Moon phases", "required for a light-year definition"), "B", "Eye safety.", "Never look at the Sun through a telescope. Follow the teacher's solar-viewing rules."),
        _LT_MCQ("difficult", "mirror_line", "<p>Which letter is the mirror surface?</p>" + str(reflection_rays(title="Mirror line")), _mcq_opts("A", "C", "B", "the incident arrow only"), "B", "C is the mirror.", "On the ray diagram, find the reflecting surface itself and match that line to a letter."),
        _LT_KEY("difficult", "lens_word", "Write the word for a shaped piece of glass or plastic that can focus light.", "lens", "A lens refracts in a controlled way.", "Name the shaped piece of glass or plastic that can gather and focus light."),
        _LT_NUM("difficult", "i40", "Angle of incidence is 40 degrees at a plane mirror. Enter the angle of reflection in degrees.", 40, "i = r.", "At a plane mirror the reflection angle matches the given incidence angle. Copy that same number of degrees."),
        _LT_ORD("difficult", "colour_lens", "Order colour-by-filter, then the false idea that a lens makes extra light.", ["colour", "lens_magic"], _OPTIC_BANK, "Filter colour is real; extra light from a lens is not.", "Put a filter transmitting one colour first, then the false claim that a lens makes extra light from nothing."),
        _LT_PICK("difficult", "ray_not", "Select the two statements that are not good light models.", ["sound_same", "year_time"], _RAY_BANK, 2, "Light is not as slow as sound across a field; a light-year is not a time.", "Choose the two poor models: light taking as long as sound across a field, and a light-year treated as a clock unit."),
    ],
}

_LT_STANDARD = {
    "foundational": (
        'light_telescopes_foundational_mcq_incident',
        'light_telescopes_foundational_keyword_reflect_word',
        'light_telescopes_foundational_number_c_kms',
        'light_telescopes_foundational_order_travel',
        'light_telescopes_foundational_pick_shadow_ok',
    ),
    "intermediate": (
        'light_telescopes_intermediate_mcq_eclipse',
        'light_telescopes_intermediate_keyword_refract_word',
        'light_telescopes_intermediate_number_two_sec',
        'light_telescopes_intermediate_order_eclipse_ord',
        'light_telescopes_intermediate_pick_optic_two',
    ),
    "difficult": (
        'light_telescopes_difficult_mcq_angle40',
        'light_telescopes_difficult_keyword_lens_word',
        'light_telescopes_difficult_number_i40',
        'light_telescopes_difficult_order_colour_lens',
        'light_telescopes_difficult_pick_ray_not',
    ),
}
eursc_science_light_telescopes, eursc_science_light_telescopes_variants = bind_eursc_topic(
    'light_telescopes', _LT_POOLS, _LT_STANDARD
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

_LF_POOLS = {
    "foundational": [
        _LF_MCQ("foundational", "need", "A simple list of needs for life as we know it includes", _mcq_opts("only rumours", "energy, liquid water and useful chemicals", "a geocentric vote", "a light-year of time"), "B", "Energy, water, chemicals.", "The simple list is energy, liquid water and useful chemicals — not rumours or a vote."),
        _LF_MCQ("foundational", "water", "Liquid water matters in this model because", _mcq_opts("it is a unit of time", "many Earth life processes happen in water", "it proves UFOs", "it is the same as a light-year"), "B", "Solvent / chemistry of life.", "Many Earth life processes happen in a liquid solvent. Which liquid does the lesson treat as typical?"),
        _LF_MCQ("foundational", "energy", "A source of energy for life can be", _mcq_opts("a secret that cannot be measured", "sunlight or chemical energy that can be tested", "the age of a rumour in days", "a planet voting"), "B", "Testable energy source.", "Living things need a source they can use to do work — sunlight or chemicals that can be measured, not a secret."),
        _LF_MCQ("foundational", "elsewhere", "Life beyond Earth, in this course, is", _mcq_opts("already proved by any night-time light", "an open scientific question needing evidence", "impossible to think about", "proved by a social-media story"), "B", "Open, evidence-based.", "Life beyond Earth is still an open question. It needs evidence, not a night-time light or a social-media story."),
        _LF_MCQ("foundational", "travel", "Travel to another star is hard mainly because", _mcq_opts("stars are closer than the Moon", "distances are enormous compared with a human lifetime at realistic speeds", "the Sun is 1 AU from the classroom", "seasons stop spacecraft"), "B", "Scale of space.", "Other stars sit so far away that a realistic spacecraft would take far longer than a school year."),
        _LF_MCQ("foundational", "three", "How many items are in this lesson's simple needs list (energy, liquid water, chemicals)?", _mcq_opts("one", "three", "eight", "fourteen"), "B", "Three.", "Count the items named in the simple needs list: energy, liquid water, chemicals."),
        _LF_KEY("foundational", "water_word", "Write the word for the liquid this lesson treats as a common need for life as we know it.", "water", "Liquid water.", "Name the liquid the lesson treats as a common need for life as we know it."),
        _LF_NUM("foundational", "needs_n", "Enter how many needs are in the simple list: energy, liquid water, chemicals.", 3, "Three.", "Count energy, liquid water and chemicals as one list. How many needs is that?"),
        _LF_ORD("foundational", "need_ord", "Order energy, then liquid water.", ["energy", "water"], _NEED_BANK, "Energy then water.", "Put a source of energy first, then liquid water as a common requirement."),
        _LF_PICK("foundational", "need_ok", "Select the two needs from the simple list that are named energy and water.", ["energy", "water"], _NEED_BANK, 2, "Energy and water. A rumour is not a need.", "Choose the energy need and the liquid-water need. A social-media rumour is not a requirement."),
    ],
    "intermediate": [
        _LF_MCQ("intermediate", "luca", "LUCA in this lesson is", _mcq_opts("a planet between Earth and Mars", "a model of a last universal common ancestor based on shared chemistry", "proof that aliens visited last week", "a unit of distance"), "B", "Evidence-based model.", "This is a model of a shared ancestor from chemistry, not a planet or a recent alien visit."),
        _LF_MCQ("intermediate", "early", "Ideas about early Earth should come from", _mcq_opts("unchecked rumours only", "rocks, chemistry and models that other scientists can criticise", "a vote on favourite movies", "a blurry light in a photo album"), "B", "Public evidence.", "Ideas about early Earth should come from rocks, chemistry and models other scientists can criticise."),
        _LF_MCQ("intermediate", "claim", "A scientific claim that a moon has microbes must", _mcq_opts("stay secret so rivals cannot test it", "be testable with measurements others can check", "be believed if it is exciting", "replace the need for water"), "B", "Testable and public.", "A claim that a moon has microbes must be testable with measurements others can check — not a secret."),
        _LF_MCQ("intermediate", "ufo", "A blurry photo of a light in the sky", _mcq_opts("proves life on Mars", "is not, by itself, evidence of extraterrestrial life", "is a light-year", "is LUCA"), "B", "Not automatic proof.", "A blurry light in a photo is not, by itself, proof of microbes on another world."),
        _LF_MCQ("intermediate", "air", "A habitat on an airless world must still", _mcq_opts("rely on rumours for oxygen", "supply breathable air by engineering, not by hoping", "ignore energy needs", "be a 5-minute walk from Earth"), "B", "Engineering constraints.", "An airless world does not supply oxygen by rumour. A habitat must be engineered to provide breathable air."),
        _LF_MCQ("intermediate", "star_years", "The nearest other star system is of the order of a few light-years away. At light speed that trip would still take", _mcq_opts("a few seconds", "a few years", "a few minutes of moonlight", "one classroom lesson"), "B", "Years even at light speed.", "A few light-years at light speed still takes a few years, not a few seconds."),
        _LF_KEY("intermediate", "energy_word", "Write the word for a source living things use to do work and keep organisation (sunlight or chemicals).", "energy", "Energy is a requirement.", "Name what living things use to do work and keep organisation — sunlight or chemicals can supply it."),
        _LF_NUM("intermediate", "proxima", "This lesson uses 4 as the whole number of years for light to reach the nearest other star. Enter that number.", 4, "About 4 years at light speed.", "The lesson uses a whole number of years for light to reach the nearest other star — a small single digit."),
        _LF_ORD("intermediate", "earth_ord", "Order early-Earth reconstruction, then the LUCA model.", ["early", "luca"], _EARTH_BANK, "Rocks and models, then LUCA.", "Put reconstructing early Earth from rocks first, then the shared-ancestor model."),
        _LF_PICK("intermediate", "alien_ok", "Select the two careful ideas about life elsewhere.", ["testable", "none_yet"], _ALIEN_BANK, 2, "Testable claims; no confirmed life yet.", "Choose that claims must be testable, and that this course has no confirmed life beyond Earth yet."),
    ],
    "difficult": [
        _LF_MCQ("difficult", "chemicals", "Useful chemicals in the simple life model include", _mcq_opts("only empty rumours", "carbon compounds and other raw materials that can be measured", "light-years of time stored in a bottle", "geocentric votes"), "B", "Chemistry, not slogans.", "Useful chemicals include carbon compounds and other raw materials you can measure, not empty rumours."),
        _LF_MCQ("difficult", "not_person", "Treating LUCA as a king in a history book is wrong because", _mcq_opts("LUCA is a planet", "LUCA is a scientific model of relatedness, not a biography of one named person", "LUCA is a light-year", "LUCA is a telescope"), "B", "Model, not a celebrity.", "The shared-ancestor idea is a scientific model of relatedness, not a biography of a king."),
        _LF_MCQ("difficult", "habit", "Habitation beyond Earth is constrained by", _mcq_opts("only the colour of a spacesuit in a film", "air, water, energy, temperature and radiation shielding", "the number of planets being eight exactly", "Moon phases voting"), "B", "Engineering list.", "A place beyond Earth must still supply air, water, energy, a workable temperature and shielding from radiation."),
        _LF_MCQ("difficult", "rocket", "A chemical rocket is much slower than light, so a trip of a few light-years", _mcq_opts("takes an afternoon on foot", "would take far longer than a few years with current rockets", "is the same as 1 AU", "proves microbes exist"), "B", "Speed and distance.", "Chemical rockets are much slower than light, so a few light-years would take far longer than a few years."),
        _LF_MCQ("difficult", "open", "The honest S2 position on extraterrestrial life is", _mcq_opts("it is already proved by any bright star", "search with testable methods; do not treat rumours as results", "it is rude to ask for evidence", "telescopes must be pointed at the Sun to find it"), "B", "Evidence first.", "Search with methods others can test. Do not treat rumours as results, and do not point a telescope at the Sun to look."),
        _LF_MCQ("difficult", "three_chem", "Energy, liquid water and chemicals are how many listed needs?", _mcq_opts("two", "three", "four", "zero"), "B", "Three.", "Count energy, liquid water and chemicals. The lesson lists that many needs."),
        _LF_KEY("difficult", "habitat_word", "Write the word for a place that supplies what living things need to stay alive.", "habitat", "A habitat supplies needs.", "Name a place that supplies what living things need to stay alive."),
        _LF_NUM("difficult", "shield", "A simple habitation list in this lesson has 4 items: air, water, energy, shielding. Enter 4.", 4, "Four constraints.", "The simple habitation list names air, water, energy and shielding. Count those items."),
        _LF_ORD("difficult", "travel_ord", "Order huge distance, then the need for a supplied habitat.", ["distance", "habitat"], _TRAVEL_BANK, "Distance, then life-support.", "Put the huge distance to other stars first, then the need for a supplied place to live."),
        _LF_PICK("difficult", "travel_not", "Select the two travel claims that are not realistic.", ["walk", "airless_easy"], _TRAVEL_BANK, 2, "You cannot walk to Proxima; airless worlds need engineering.", "Choose walking to the nearest other star in an afternoon, and the claim that an airless world needs no engineering."),
    ],
}

_LF_STANDARD = {
    "foundational": (
        'life_earth_elsewhere_foundational_mcq_elsewhere',
        'life_earth_elsewhere_foundational_keyword_water_word',
        'life_earth_elsewhere_foundational_number_needs_n',
        'life_earth_elsewhere_foundational_order_need_ord',
        'life_earth_elsewhere_foundational_pick_need_ok',
    ),
    "intermediate": (
        'life_earth_elsewhere_intermediate_mcq_air',
        'life_earth_elsewhere_intermediate_keyword_energy_word',
        'life_earth_elsewhere_intermediate_number_proxima',
        'life_earth_elsewhere_intermediate_order_earth_ord',
        'life_earth_elsewhere_intermediate_pick_alien_ok',
    ),
    "difficult": (
        'life_earth_elsewhere_difficult_mcq_chemicals',
        'life_earth_elsewhere_difficult_keyword_habitat_word',
        'life_earth_elsewhere_difficult_number_shield',
        'life_earth_elsewhere_difficult_order_travel_ord',
        'life_earth_elsewhere_difficult_pick_travel_not',
    ),
}
eursc_science_life_earth_elsewhere, eursc_science_life_earth_elsewhere_variants = bind_eursc_topic(
    'life_earth_elsewhere', _LF_POOLS, _LF_STANDARD
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

_AM_POOLS = {
    "foundational": [
        _AM_MCQ("foundational", "particle", "In the particle model, a solid, liquid or gas is", _mcq_opts("empty of any particles", "made of particles that are still there even if you cannot see them", "a rumour", "a light-year"), "B", "Particles persist.", "Solids, liquids and gases are still made of particles you cannot see. They do not empty out when you look away."),
        _AM_MCQ("foundational", "element", "An element is", _mcq_opts("any mixture of different atoms", "a substance made of only one type of atom", "a molecule of water only", "a unit of time"), "B", "One type of atom.", "This is a substance with only one type of atom, not a jumble of different particles."),
        _AM_MCQ("foundational", "symbol", "The symbol O in this lesson stands for", _mcq_opts("orbit", "oxygen", "a light-year", "a season"), "B", "Oxygen.", "The letter O in this lesson is a chemical symbol for an element, not 'orbit' or a season."),
        _AM_MCQ("foundational", "molecule", "A molecule is", _mcq_opts("a planet", "atoms joined together", "a geocentric model", "a telescope"), "B", "Joined atoms.", "When atoms join together they make this kind of particle — not a planet or a telescope."),
        _AM_MCQ("foundational", "water_mol", "A water molecule is modelled as", _mcq_opts("one atom of iron", "hydrogen and oxygen atoms joined", "a mixture of eight planets", "empty space with no particles"), "B", "H and O joined.", "A water molecule is modelled as hydrogen joined with oxygen, not a single iron atom."),
        _AM_MCQ("foundational", "atom_box", "<p>Which letter is a single atom?</p>" + str(atom_molecule_boxes(title="Single atom")), _mcq_opts("B", "A", "C", "the mixed jumble only"), "B", "A is one atom.", "On the sketch, find the box that shows one particle of an element on its own and match it to a letter."),
        _AM_KEY("foundational", "atom_word", "Write the word for a single particle of an element in this S2 model.", "atom", "An atom.", "Name a single particle of an element in this S2 model — not a group of joined particles."),
        _AM_NUM("foundational", "water_n", "A water molecule is modelled as 2 hydrogen atoms and 1 oxygen atom. Enter the total number of atoms.", 3, "Three atoms.", "Add the two hydrogens and the one oxygen in the water-molecule model to get the total atom count."),
        _AM_ORD("foundational", "part_el", "Order particles-always-there, then an element as one type of atom.", ["particles", "element"], _PART_BANK, "Particles, then element.", "Put particles-still-there-even-if-unseen first, then a substance with only one type of atom."),
        _AM_PICK("foundational", "part_ok", "Select the two particle-model ideas.", ["particles", "element"], _PART_BANK, 2, "Particles and elements. Melting does not invent magic atoms.", "Choose particles that persist when you cannot see them, and a substance with one type of atom. Melting does not invent magic atoms."),
    ],
    "intermediate": [
        _AM_MCQ("intermediate", "h_symbol", "The symbol H stands for", _mcq_opts("helium in this lesson", "hydrogen", "a habitat", "a light-year"), "B", "Hydrogen.", "The letter H in this lesson is the symbol for one particular element — not helium, a habitat, or a distance unit."),
        _AM_MCQ("intermediate", "mix", "Box C in the particle sketch (a jumble of different particles) is best called", _mcq_opts("a single element", "a mixture of different particles, not one element", "a light-year", "an empty universe"), "B", "Mixed, not an element.", "A jumble of different particles is not a substance with only one type of atom."),
        _AM_MCQ("intermediate", "join", "When two atoms join as a molecule, the atoms", _mcq_opts("vanish", "are still there, now bonded", "become planets", "become a unit of time"), "B", "Rearranged, not destroyed.", "When two atoms join, they are still there, now bonded. They do not vanish."),
        _AM_MCQ("intermediate", "word_eq", "A word equation for making water from hydrogen and oxygen is", _mcq_opts("water → hydrogen + oxygen only as a creation spell", "hydrogen + oxygen → water", "Sun + Moon → water", "rotation + season → water"), "B", "Reactants to product.", "Put the starting substances before the arrow and the new substance after it."),
        _AM_MCQ("intermediate", "not_magic", "In a closed reaction story, atoms", _mcq_opts("appear from nowhere as a new element", "are rearranged; the counts should match", "leave the universe", "become light-years"), "B", "Conservation.", "In a closed story the atom counts should match before and after. Atoms change partners; they are not created from nowhere."),
        _AM_MCQ("intermediate", "mol_box", "<p>Which letter is two atoms joined as a molecule?</p>" + str(atom_molecule_boxes(title="Molecule box")), _mcq_opts("A", "B", "C", "the empty page"), "B", "B is the molecule.", "On the sketch, find the box that shows two atoms joined together and match it to a letter."),
        _AM_KEY("intermediate", "mol_word", "Write the word for atoms joined together.", "molecule", "A molecule.", "Name what you get when atoms join together — one word, not the name of a single particle."),
        _AM_NUM("intermediate", "h_in_water", "How many hydrogen atoms are in the water-molecule model in this lesson?", 2, "Two hydrogens.", "In the water-molecule model, count only the hydrogen atoms, not the oxygen."),
        _AM_ORD("intermediate", "mol_ord", "Order a single atom, then a molecule as joined atoms.", ["atom", "molecule"], _MOL_BANK, "Atom, then molecule.", "Put a single particle of an element first, then atoms joined together."),
        _AM_PICK("intermediate", "sym_ok", "Select atom and molecule.", ["atom", "molecule"], _MOL_BANK, 2, "Atom and molecule. A symbol is not a weather sentence.", "Choose a single particle of an element, and atoms joined together. A symbol is not a weather sentence."),
    ],
    "difficult": [
        _AM_MCQ("difficult", "rearrange", "Burning hydrogen in oxygen to make water is best described as", _mcq_opts("destroying hydrogen atoms forever", "rearranging hydrogen and oxygen atoms into water molecules", "creating iron atoms from light", "a season on Earth"), "B", "Rearrangement.", "Burning hydrogen in oxygen to make water is atoms changing partners, not destroying hydrogen forever."),
        _AM_MCQ("difficult", "co2", "A word equation carbon + oxygen → carbon dioxide says", _mcq_opts("carbon atoms vanish", "carbon and oxygen atoms rearrange into a new substance", "a new type of atom is invented from nothing", "the product has no particles"), "B", "Same types, new arrangement.", "Carbon and oxygen atoms rearrange into a new substance. They do not vanish or invent a brand-new type of atom."),
        _AM_MCQ("difficult", "count", "If 2 hydrogen molecules and 1 oxygen molecule make 2 water molecules in a simple count story, atoms are", _mcq_opts("created extra from fame", "conserved: they change partners, not disappear", "turned into light-years", "voted into a new element"), "B", "Conservation of atoms.", "If the counts match, atoms change partners rather than appearing from fame or disappearing."),
        _AM_MCQ("difficult", "fe", "The symbol Fe stands for", _mcq_opts("a season", "iron", "a filter", "a light-year"), "B", "Iron.", "The symbol Fe in this lesson is a metal element, not a season or a light-year."),
        _AM_MCQ("difficult", "not_element", "A box of mixed different particles is not an element because", _mcq_opts("elements cannot be drawn", "an element needs one type of atom, not a jumble", "molecules are forbidden", "symbols must be sentences"), "B", "One type of atom.", "An element needs one type of atom. A mixed jumble is a mixture, not that."),
        _AM_MCQ("difficult", "mix_box", "<p>Which letter is a mixed jumble of different particles?</p>" + str(atom_molecule_boxes(title="Mixed jumble")), _mcq_opts("A", "C", "B", "a single atom only"), "B", "C is mixed.", "On the sketch, find the box that shows a jumble of different particles and match it to a letter."),
        _AM_KEY("difficult", "el_word", "Write the word for a substance made of only one type of atom.", "element", "An element.", "Name a substance made of only one type of atom — not a mixture and not a joined group."),
        _AM_NUM("difficult", "o_in_water", "How many oxygen atoms are in one water molecule in this lesson's model?", 1, "One oxygen.", "In one water molecule in this model, count only the oxygen atoms, not the hydrogens."),
        _AM_ORD("difficult", "rxn_ord", "Order rearrangement of atoms, then writing a word equation.", ["rearrange", "word"], _RXN_BANK, "What happens, then how we write it.", "Put atoms changing partners first, then writing the names of reactants and products."),
        _AM_PICK("difficult", "rxn_ok", "Select the two reaction ideas that belong in this lesson.", ["rearrange", "word"], _RXN_BANK, 2, "Rearrange and word equation. Not a spell.", "Choose atoms rearranging (not created from nothing) and a word equation that names reactants and products. Skip a spell."),
    ],
}

_AM_STANDARD = {
    "foundational": (
        'atoms_molecules_foundational_mcq_atom_box',
        'atoms_molecules_foundational_keyword_atom_word',
        'atoms_molecules_foundational_number_water_n',
        'atoms_molecules_foundational_order_part_el',
        'atoms_molecules_foundational_pick_part_ok',
    ),
    "intermediate": (
        'atoms_molecules_intermediate_mcq_h_symbol',
        'atoms_molecules_intermediate_keyword_mol_word',
        'atoms_molecules_intermediate_number_h_in_water',
        'atoms_molecules_intermediate_order_mol_ord',
        'atoms_molecules_intermediate_pick_sym_ok',
    ),
    "difficult": (
        'atoms_molecules_difficult_mcq_co2',
        'atoms_molecules_difficult_keyword_el_word',
        'atoms_molecules_difficult_number_o_in_water',
        'atoms_molecules_difficult_order_rxn_ord',
        'atoms_molecules_difficult_pick_rxn_ok',
    ),
}
eursc_science_atoms_molecules, eursc_science_atoms_molecules_variants = bind_eursc_topic(
    'atoms_molecules', _AM_POOLS, _AM_STANDARD
)
