"""S1 Unit 1.3 Sports — 1.3.1–1.3.4."""
from generators.eursc.science_shared import (
    bind_eursc_topic,
    antagonistic_pair,
    circulation_boxes,
    distance_time_graph,
    force_pair,
)
from generators.shared.utils import (
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)

_LEVEL = "eursc"
_SUBJECT = "science"


def _topic_bank(topic):
    def mcq(difficulty, suffix, question, options, answer, solution):
        def _fn():
            return make_problem(
                question,
                solution,
                "Use movement, force, breathing or sport-health ideas from the lesson.",
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
                "Check the sport science idea and the evidence.",
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


def _mcq_opts(a, b, c, d):
    return [f"A  {a}", f"B  {b}", f"C  {c}", f"D  {d}"]


_MV_MCQ, _MV_NUM, _MV_KEY, _MV_ORD, _MV_PICK = _topic_bank("movement")
_FS_MCQ, _FS_NUM, _FS_KEY, _FS_ORD, _FS_PICK = _topic_bank("forces_sport")
_BR_MCQ, _BR_NUM, _BR_KEY, _BR_ORD, _BR_PICK = _topic_bank("breathing")
_SH_MCQ, _SH_NUM, _SH_KEY, _SH_ORD, _SH_PICK = _topic_bank("sport_health")

_SPEED_BANK = (
    {"id": "measure", "text": "Measure distance and time with SI units"},
    {"id": "divide", "text": "Divide distance by time to get average speed"},
    {"id": "guess", "text": "Guess the winner from the colour of the kit"},
    {"id": "secret", "text": "Hide the stopwatch reading so nobody can check"},
)
_GRAPH_BANK = (
    {"id": "slope", "text": "A sloping line means the object is moving"},
    {"id": "flat", "text": "A flat line means rest (distance not changing)"},
    {"id": "colour", "text": "A red line is always faster than a blue line"},
    {"id": "fame", "text": "A famous athlete's graph cannot be measured"},
)
_FORCE_BANK = (
    {"id": "push", "text": "A force can start, stop, speed up, slow down or change shape"},
    {"id": "pair", "text": "Forces are interactions: if A pushes B, B pushes A"},
    {"id": "magic", "text": "A force can appear with no object involved"},
    {"id": "unitless", "text": "Force has no unit in science"},
)
_FRIC_BANK = (
    {"id": "grip", "text": "Friction can help a shoe grip the ground"},
    {"id": "slow", "text": "Friction can slow a sliding object"},
    {"id": "vacuum", "text": "Friction is the only force in outer space with no contact"},
    {"id": "massless", "text": "Friction is the same as mass in kilograms"},
)
_AIR_BANK = (
    {"id": "nitrogen", "text": "Nitrogen is the main gas in ordinary air"},
    {"id": "oxygen", "text": "Oxygen is used by cells in respiration"},
    {"id": "helium_air", "text": "Air is mostly helium in a sports hall"},
    {"id": "no_gas", "text": "Air contains no gases, only thoughts"},
)
_CIRC_BANK = (
    {"id": "heart", "text": "The heart pumps blood"},
    {"id": "lungs", "text": "The lungs add oxygen to blood"},
    {"id": "body", "text": "Body tissues use oxygen and produce carbon dioxide"},
    {"id": "bone_pump", "text": "Bones pump air like a bicycle tyre"},
)
_BODY_BANK = (
    {"id": "skeleton", "text": "The skeleton supports and protects"},
    {"id": "joint", "text": "A joint is where bones meet and can move"},
    {"id": "pair", "text": "Antagonistic muscles pull in opposite ways"},
    {"id": "slogan", "text": "A sports slogan replaces anatomy"},
)
_SAFE_BANK = (
    {"id": "injury", "text": "Warm-up and sensible load reduce some injury risk"},
    {"id": "uv", "text": "Covering skin and shade reduce UV damage in outdoor sport"},
    {"id": "drug", "text": "Some drugs are banned or unsafe because they harm health or cheat"},
    {"id": "ignore", "text": "Ignore bleeding and keep playing no matter what"},
)


_MV_POOLS = {
    "foundational": [
        _MV_MCQ("foundational", "avg", "Average speed is", _mcq_opts("time divided by distance", "distance divided by time", "mass divided by volume", "a feeling"), "B", "v = d/t for average speed."),
        _MV_MCQ("foundational", "si", "A fair speed calculation should use", _mcq_opts("a mix of miles and seconds with no conversion", "consistent units, such as metres and seconds", "only the athlete's fame", "guessed times"), "B", "Units must match."),
        _MV_MCQ("foundational", "rest", "If distance does not change while time passes, average speed is", _mcq_opts("infinite", "zero", "the same as mass", "1 newton"), "B", "No distance change means speed 0."),
        _MV_MCQ("foundational", "measure", "To find a runner's average speed you need", _mcq_opts("only the colour of the vest", "a distance and a time", "only the crowd noise", "a force in newtons only"), "B", "Speed needs d and t."),
        _MV_MCQ("foundational", "unit_s", "The SI unit of time in v = d/t is usually the", _mcq_opts("kilogram", "second", "ampere", "candela"), "B", "Time is in seconds in SI."),
        _MV_MCQ("foundational", "graph_rest", "<p>Which labelled part of this distance–time graph shows rest?</p>" + str(distance_time_graph()), _mcq_opts("A", "B", "C", "the word time"), "B", "B is the flat section."),
        _MV_KEY("foundational", "speed_word", "Write the word for distance divided by time.", "speed", "Average speed is distance over time."),
        _MV_NUM("foundational", "v0", "Distance 10 m, time 2 s. What is average speed in m/s?", 5, "10 / 2 = 5."),
        _MV_ORD("foundational", "calc", "Order measuring, then dividing, to get average speed.", ["measure", "divide"], _SPEED_BANK, "Measure d and t, then divide."),
        _MV_PICK("foundational", "need_two", "Select the two steps that belong in a speed investigation.", ["measure", "divide"], _SPEED_BANK, 2, "Measure and divide. Guessing kit colour is not a method."),
        _MV_PICK("foundational", "graph_ok", "Select the two correct graph ideas.", ["slope", "flat"], _GRAPH_BANK, 2, "Slope means moving; flat means rest."),
    ],
    "intermediate": [
        _MV_MCQ("intermediate", "num", "A cyclist travels 20 m in 4 s. Average speed is", _mcq_opts("80 m/s", "5 m/s", "16 m/s", "0 m/s"), "B", "20 / 4 = 5 m/s."),
        _MV_MCQ("intermediate", "km", "3 km in 1/2 hour is the same as 3000 m in 1800 s. Average speed is", _mcq_opts("0.6 m/s", "about 1.67 m/s", "3000 m/s", "1800 m/s"), "B", "3000 / 1800 ≈ 1.67 m/s."),
        _MV_MCQ("intermediate", "convert", "2 minutes is how many seconds?", _mcq_opts("2", "120", "60", "200"), "B", "2 × 60 = 120 s."),
        _MV_MCQ("intermediate", "read_d", "A graph shows 12 m at 3 s on a straight slope from the origin. Average speed so far is", _mcq_opts("36 m/s", "4 m/s", "9 m/s", "15 m/s"), "B", "12 / 3 = 4 m/s."),
        _MV_MCQ("intermediate", "steeper", "On a distance–time graph, a steeper slope means", _mcq_opts("slower movement", "greater speed", "the object has more mass", "time has stopped"), "B", "Steeper d–t slope is faster."),
        _MV_MCQ("intermediate", "graph_move", "<p>Which labelled part shows the object moving after rest?</p>" + str(distance_time_graph(title="Distance–time: C is moving again")), _mcq_opts("B only", "C", "the word d", "a force arrow"), "B", "C is the later slope. B is rest."),
        _MV_KEY("intermediate", "metre_word", "Write the SI unit of distance used with seconds to give metres per second.", "metre", "Distance in metres."),
        _MV_NUM("intermediate", "v1", "Distance 30 m, time 5 s. What is average speed in m/s?", 6, "30 / 5 = 6."),
        _MV_ORD("intermediate", "graph_read", "Order the moving idea, then the rest idea, when reading a d–t graph.", ["slope", "flat"], _GRAPH_BANK, "Slope first as movement, then flat as rest."),
        _MV_PICK("intermediate", "not_method", "Select the two choices that are not scientific speed methods.", ["guess", "secret"], _SPEED_BANK, 2, "Guessing kit and hiding times are not methods."),
    ],
    "difficult": [
        _MV_MCQ("difficult", "avg_vs", "Average speed for a whole lap can be low even if a sprint section was fast because", _mcq_opts("speed cannot be calculated", "the total distance is divided by the total time, including slower parts", "mass changes the formula", "graphs are forbidden"), "B", "Average uses whole d and whole t."),
        _MV_MCQ("difficult", "units", "A student writes 8 km/h as 8 m/s without converting. The error is", _mcq_opts("there is no error", "the units are not the same; 8 km/h is much slower than 8 m/s", "time is in kilograms", "distance is in newtons"), "B", "Convert before comparing."),
        _MV_MCQ("difficult", "zero_t", "Time in v = d/t cannot be zero because", _mcq_opts("athletes dislike clocks", "dividing by zero is not a valid speed", "distance must be zero too", "SI units fail"), "B", "You need a time interval."),
        _MV_MCQ("difficult", "plateau", "A flat d–t section then a slope means", _mcq_opts("the object was always at rest", "rest then movement again", "negative mass", "a force with no interaction"), "B", "Read each part of the graph."),
        _MV_MCQ("difficult", "graph_a", "<p>Which labelled part is the first moving section?</p>" + str(distance_time_graph(title="Distance–time: A is the first slope")), _mcq_opts("B", "A", "the caption only", "C only and never A"), "B", "A is the first slope."),
        _MV_KEY("difficult", "average_word", "Write the word that describes speed over a whole journey, not one instant.", "average", "Average speed uses total d and t."),
        _MV_NUM("difficult", "v2", "A swimmer covers 100 m in 50 s. Average speed in m/s?", 2, "100 / 50 = 2."),
        _MV_ORD("difficult", "full", "Order measure, then divide, for a fair average speed.", ["measure", "divide"], _SPEED_BANK, "Do not hide the stopwatch."),
        _MV_PICK("difficult", "graph_false", "Select the two graph myths.", ["colour", "fame"], _GRAPH_BANK, 2, "Line colour and fame are not speed."),
        _MV_PICK("difficult", "keep_speed", "Select the two scientific speed steps.", ["measure", "divide"], _SPEED_BANK, 2, "Measure and divide."),
    ],
}

_MV_STANDARD = {
    "foundational": (
        'movement_foundational_mcq_avg',
        'movement_foundational_keyword_speed_word',
        'movement_foundational_number_v0',
        'movement_foundational_order_calc',
        'movement_foundational_pick_graph_ok',
    ),
    "intermediate": (
        'movement_intermediate_mcq_num',
        'movement_intermediate_keyword_metre_word',
        'movement_intermediate_number_v1',
        'movement_intermediate_order_graph_read',
        'movement_intermediate_pick_not_method',
    ),
    "difficult": (
        'movement_difficult_mcq_avg_vs',
        'movement_difficult_keyword_average_word',
        'movement_difficult_number_v2',
        'movement_difficult_order_full',
        'movement_difficult_pick_graph_false',
    ),
}
eursc_science_movement, eursc_science_movement_variants = bind_eursc_topic('movement', _MV_POOLS, _MV_STANDARD)


_FS_POOLS = {
    "foundational": [
        _FS_MCQ("foundational", "effect", "A force can", _mcq_opts("only change an object's colour", "change motion or shape", "remove mass from the universe", "replace time"), "B", "Forces change motion or shape."),
        _FS_MCQ("foundational", "unit", "The SI unit of force is the", _mcq_opts("metre", "newton", "second", "candela"), "B", "Force is measured in newtons."),
        _FS_MCQ("foundational", "pair", "If a footballer pushes a ball, the ball", _mcq_opts("does nothing back", "pushes back on the footballer (an interaction)", "gains infinite mass", "stops time"), "B", "Forces come in interaction pairs."),
        _FS_MCQ("foundational", "friction", "Friction between shoe and track can", _mcq_opts("only exist in a vacuum", "help the athlete push forward without slipping", "be the same as weight in newtons always", "remove the need for mass"), "B", "Useful grip is friction."),
        _FS_MCQ("foundational", "mass", "Mass is", _mcq_opts("the pull of the Earth in newtons", "the amount of matter, in kilograms", "a type of friction", "a feeling of tiredness"), "B", "Mass is kilograms of matter."),
        _FS_MCQ("foundational", "boxes", "<p>In this sketch the two boxes push on each other. The interaction idea is that</p>" + str(force_pair()), _mcq_opts("only A can push", "A and B push each other", "there is no force", "mass is zero"), "B", "Each pushes the other."),
        _FS_KEY("foundational", "newton_word", "Write the SI unit of force.", "newton", "The newton is the force unit."),
        _FS_NUM("foundational", "net0", "Two 2 N forces pull a ring equally opposite. The net force in newtons is", 0, "Equal opposite forces cancel."),
        _FS_ORD("foundational", "think", "Order a force effect, then the interaction idea.", ["push", "pair"], _FORCE_BANK, "Effects, then pairs. Magic forces are not used."),
        _FS_PICK("foundational", "force_ok", "Select the two scientific force ideas.", ["push", "pair"], _FORCE_BANK, 2, "Effects and interactions."),
        _FS_PICK("foundational", "fric_ok", "Select the two friction ideas that belong in sport.", ["grip", "slow"], _FRIC_BANK, 2, "Grip and slowing. Vacuum-only and mass mix-ups are wrong."),
    ],
    "intermediate": [
        _FS_MCQ("intermediate", "weight", "Weight is", _mcq_opts("mass in kilograms", "the gravitational force on a mass, in newtons", "friction only", "speed"), "B", "Weight is a force."),
        _FS_MCQ("intermediate", "balance", "A gymnast still on a beam with no acceleration has", _mcq_opts("no forces at all", "balanced forces (equilibrium)", "infinite speed", "zero mass"), "B", "Balanced forces, not zero forces."),
        _FS_MCQ("intermediate", "cog", "A high centre of gravity on a narrow base tends to be", _mcq_opts("more stable", "less stable", "heavier in kilograms automatically", "frictionless"), "B", "Stability links CoG and base."),
        _FS_MCQ("intermediate", "slow_fric", "A puck sliding on ice slows because", _mcq_opts("mass disappears", "friction (and air) act against the motion", "time reverses", "weight becomes mass"), "B", "Friction opposes sliding."),
        _FS_MCQ("intermediate", "same_mass", "On the Moon a shot-put has the same mass as on Earth but", _mcq_opts("the same weight", "a smaller weight", "negative mass", "no matter"), "B", "Mass stays; gravitational force changes."),
        _FS_MCQ("intermediate", "pair2", "<p>Arrow A on B and B on A in this diagram are</p>" + str(force_pair(title="Matching pushes")), _mcq_opts("unrelated rumours", "a matching interaction pair", "units of time", "masses in kilograms"), "B", "Interaction pair."),
        _FS_KEY("intermediate", "friction_word", "Write the word for a contact force that opposes slipping or sliding.", "friction", "Friction can grip or slow."),
        _FS_NUM("intermediate", "n1", "Two 3 N forces pull a ring equally opposite. The net force in newtons is", 0, "Equal opposite forces cancel."),
        _FS_ORD("intermediate", "fric_order", "Order helpful grip, then slowing, as friction jobs.", ["grip", "slow"], _FRIC_BANK, "Grip then slowing."),
        _FS_PICK("intermediate", "not_force", "Select the two unscientific force claims.", ["magic", "unitless"], _FORCE_BANK, 2, "Forces need objects and have a unit."),
    ],
    "difficult": [
        _FS_MCQ("difficult", "eq", "Equilibrium of a still object means", _mcq_opts("no gravity exists", "resultant force is zero", "mass is zero", "friction is forbidden"), "B", "Net force zero."),
        _FS_MCQ("difficult", "lean", "A rugby player leaning with a wide stance is more stable because", _mcq_opts("mass becomes infinite", "the line from the centre of gravity more easily stays over a wider base", "friction disappears", "weight is not a force"), "B", "Base and CoG."),
        _FS_MCQ("difficult", "n3", "A sprinter pushes the blocks backwards; the blocks", _mcq_opts("do nothing", "push the sprinter forwards", "remove the sprinter's mass", "stop the clock"), "B", "Interaction pair."),
        _FS_MCQ("difficult", "air", "Air resistance on a speeding cyclist is a force that", _mcq_opts("always helps the cyclist", "usually acts against the motion through air", "is measured in seconds", "is the same as mass"), "B", "Drag opposes motion."),
        _FS_MCQ("difficult", "read_n", "A spring balance reads 10 N for a bag on Earth. That reading is closest to", _mcq_opts("the bag's mass in kilograms", "the bag's weight", "the time of fall", "friction in metres"), "B", "Newtons on a spring balance are weight."),
        _FS_KEY("difficult", "weight_word", "Write the word for the gravitational force on an object.", "weight", "Weight is a force in newtons."),
        _FS_NUM("difficult", "sum", "Forces 4 N right and 1 N left along a line. Resultant size in newtons?", 3, "4 − 1 = 3 N."),
        _FS_ORD("difficult", "pair_after", "Order a force effect, then the interaction pair.", ["push", "pair"], _FORCE_BANK, "Effects then pairs."),
        _FS_PICK("difficult", "keep_f", "Select the two force facts.", ["push", "pair"], _FORCE_BANK, 2, "Effects and interactions."),
        _FS_PICK("difficult", "bad_f", "Select the two friction mix-ups.", ["vacuum", "massless"], _FRIC_BANK, 2, "Friction is not 'only in space' and not mass."),
    ],
}

_FS_STANDARD = {
    "foundational": (
        'forces_sport_foundational_mcq_boxes',
        'forces_sport_foundational_keyword_newton_word',
        'forces_sport_foundational_number_net0',
        'forces_sport_foundational_order_think',
        'forces_sport_foundational_pick_force_ok',
    ),
    "intermediate": (
        'forces_sport_intermediate_mcq_balance',
        'forces_sport_intermediate_keyword_friction_word',
        'forces_sport_intermediate_number_n1',
        'forces_sport_intermediate_order_fric_order',
        'forces_sport_intermediate_pick_not_force',
    ),
    "difficult": (
        'forces_sport_difficult_mcq_air',
        'forces_sport_difficult_keyword_weight_word',
        'forces_sport_difficult_number_sum',
        'forces_sport_difficult_order_pair_after',
        'forces_sport_difficult_pick_bad_f',
    ),
}
eursc_science_forces_sport, eursc_science_forces_sport_variants = bind_eursc_topic(
    'forces_sport', _FS_POOLS, _FS_STANDARD
)


_BR_POOLS = {
    "foundational": [
        _BR_MCQ("foundational", "air", "Ordinary air is mostly", _mcq_opts("oxygen only", "nitrogen, with oxygen as a smaller share", "pure carbon dioxide", "liquid water"), "B", "Nitrogen dominates air."),
        _BR_MCQ("foundational", "exhale", "Compared with inhaled air, exhaled air usually has", _mcq_opts("more oxygen and less carbon dioxide", "less oxygen and more carbon dioxide", "no nitrogen", "only helium"), "B", "Respiration uses O2 and produces CO2."),
        _BR_MCQ("foundational", "resp", "Respiration in this lesson means", _mcq_opts("only the chest moving", "cells using oxygen to release energy from food", "the skeleton growing", "friction"), "B", "Cellular respiration, not only breathing movements."),
        _BR_MCQ("foundational", "pulse", "Pulse rate is a clue to", _mcq_opts("shoe size", "how often the heart is beating", "the newton", "air's colour"), "B", "Pulse tracks heart beats."),
        _BR_MCQ("foundational", "heart", "The heart's job in this unit is to", _mcq_opts("digest food", "pump blood", "store oxygen as a metal", "measure distance"), "B", "The heart is a pump."),
        _BR_MCQ("foundational", "boxes", "<p>Which letter is the heart on this schematic?</p>" + str(circulation_boxes()), _mcq_opts("B", "A", "C", "the word lungs"), "B", "A is labelled heart."),
        _BR_KEY("foundational", "oxygen_word", "Write the gas cells use in respiration.", "oxygen", "Oxygen is used by cells."),
        _BR_NUM("foundational", "pulse60", "A pulse of 10 beats in 10 s is how many beats in 60 s if the rate stays the same?", 60, "10 × 6 = 60."),
        _BR_ORD("foundational", "path", "Order heart pump, then lungs adding oxygen, then body use.", ["heart", "lungs", "body"], _CIRC_BANK, "Heart, lungs, tissues."),
        _BR_PICK("foundational", "air_ok", "Select the two true statements about air gases.", ["nitrogen", "oxygen"], _AIR_BANK, 2, "Nitrogen majority; oxygen used in respiration."),
        _BR_PICK("foundational", "circ_ok", "Select the two circulation jobs.", ["heart", "lungs"], _CIRC_BANK, 2, "Heart pumps; lungs oxygenate."),
    ],
    "intermediate": [
        _BR_MCQ("intermediate", "breathe", "Breathing movements move air so that", _mcq_opts("bones can pump", "gas exchange at the lungs can happen", "mass becomes weight", "friction disappears"), "B", "Ventilation supports gas exchange."),
        _BR_MCQ("intermediate", "co2", "More carbon dioxide in exhaled air is evidence that", _mcq_opts("the person did not respire", "respiration produced CO2", "air is helium", "the heart is a lung"), "B", "CO2 is a product."),
        _BR_MCQ("intermediate", "sport", "During hard exercise, pulse often rises because", _mcq_opts("the skeleton wants fame", "muscles need more oxygen delivered by blood", "time stops", "air contains no oxygen"), "B", "Demand for oxygen rises."),
        _BR_MCQ("intermediate", "blood", "Blood carries", _mcq_opts("only nitrogen bubbles as the whole job", "oxygen (and other substances) around the body", "newtons of force only", "distance in metres"), "B", "Blood is a transport tissue."),
        _BR_MCQ("intermediate", "pressure", "Deeper under water, pressure on the body", _mcq_opts("falls to zero", "increases", "becomes a mass in kilograms", "removes buoyancy"), "B", "Pressure increases with depth."),
        _BR_MCQ("intermediate", "lungs_box", "<p>Which letter marks the lungs?</p>" + str(circulation_boxes(title="B lungs")), _mcq_opts("A", "B", "C", "none"), "B", "B is lungs."),
        _BR_KEY("intermediate", "pulse_word", "Write the word for the beat you can feel that matches the heart.", "pulse", "Pulse follows heart rate."),
        _BR_NUM("intermediate", "beats", "A pulse of 20 beats in 15 s is how many beats in 60 s if the rate stays the same?", 80, "20 × 4 = 80."),
        _BR_ORD("intermediate", "circ2", "Order lungs, then body tissues, after the heart has pumped.", ["lungs", "body"], _CIRC_BANK, "Oxygenate, then use."),
        _BR_PICK("intermediate", "air_myth", "Select the two false air claims.", ["helium_air", "no_gas"], _AIR_BANK, 2, "Air is not mostly helium and is not 'thoughts'."),
    ],
    "difficult": [
        _BR_MCQ("difficult", "link", "Breathing, circulation and respiration link because", _mcq_opts("they are three names for friction", "air movement, blood transport and cell chemistry work together", "the skeleton stores oxygen as a solid bar", "speed is force"), "B", "The three ideas connect in sport."),
        _BR_MCQ("difficult", "buoy", "A swimmer floats more easily in denser salty water because", _mcq_opts("mass becomes zero", "upthrust (buoyancy) is greater in the denser liquid", "pulse stops", "oxygen is a metal"), "B", "Buoyancy depends on the liquid."),
        _BR_MCQ("difficult", "not_same", "Chest movement is not the same as respiration because", _mcq_opts("science forbids the word oxygen", "moving air is ventilation; respiration is the cell process that uses oxygen", "the heart is a lung", "CO2 is nitrogen"), "B", "Keep the words distinct."),
        _BR_MCQ("difficult", "recover", "After a sprint, breathing stays fast for a while because", _mcq_opts("the race clock is broken", "the body is still supplying extra oxygen and clearing extra carbon dioxide", "mass increased", "friction is respiration"), "B", "Recovery needs gas exchange."),
        _BR_MCQ("difficult", "body_box", "<p>Which letter is body tissue using oxygen?</p>" + str(circulation_boxes(title="C body")), _mcq_opts("A", "C", "B only", "the word heart"), "B", "C is body."),
        _BR_KEY("difficult", "buoyancy_word", "Write the word for the upward force from a liquid on an immersed object.", "buoyancy", "Buoyancy is upthrust in water sport."),
        _BR_NUM("difficult", "pulse2", "12 beats in 10 s. Beats per minute if the rate is steady?", 72, "12 × 6 = 72."),
        _BR_ORD("difficult", "full_circ", "Order heart, lungs, then body.", ["heart", "lungs", "body"], _CIRC_BANK, "Pump, oxygenate, use."),
        _BR_PICK("difficult", "circ_three", "Select the three genuine circulation roles.", ["heart", "lungs", "body"], _CIRC_BANK, 3, "Bones do not pump air here."),
        _BR_PICK("difficult", "keep_air", "Select the two air facts.", ["nitrogen", "oxygen"], _AIR_BANK, 2, "Nitrogen and oxygen."),
    ],
}

_BR_STANDARD = {
    "foundational": (
        'breathing_foundational_mcq_air',
        'breathing_foundational_keyword_oxygen_word',
        'breathing_foundational_number_pulse60',
        'breathing_foundational_order_path',
        'breathing_foundational_pick_air_ok',
    ),
    "intermediate": (
        'breathing_intermediate_mcq_blood',
        'breathing_intermediate_keyword_pulse_word',
        'breathing_intermediate_number_beats',
        'breathing_intermediate_order_circ2',
        'breathing_intermediate_pick_air_myth',
    ),
    "difficult": (
        'breathing_difficult_mcq_body_box',
        'breathing_difficult_keyword_buoyancy_word',
        'breathing_difficult_number_pulse2',
        'breathing_difficult_order_full_circ',
        'breathing_difficult_pick_circ_three',
    ),
}
eursc_science_breathing, eursc_science_breathing_variants = bind_eursc_topic('breathing', _BR_POOLS, _BR_STANDARD)


_SH_POOLS = {
    "foundational": [
        _SH_MCQ("foundational", "skel", "The skeleton mainly", _mcq_opts("pumps blood", "supports the body and protects organs", "stores rumours", "is a type of friction"), "B", "Support and protection."),
        _SH_MCQ("foundational", "joint", "A joint is", _mcq_opts("a muscle that never attaches", "where bones meet and movement can happen", "a gas in air", "a unit of speed"), "B", "Bones meet at joints."),
        _SH_MCQ("foundational", "antag", "Antagonistic muscles", _mcq_opts("always pull the same way", "work in pairs that pull in opposite ways", "are bones", "are banned drugs"), "B", "Opposite pulls."),
        _SH_MCQ("foundational", "uv", "UV from the sun can damage skin. Outdoor sport should", _mcq_opts("ignore covering and shade", "use shade, covering or teacher-approved protection, not a classroom skin survey", "require pupils to compare tans", "replace water with bleach"), "B", "Protection without body ranking."),
        _SH_MCQ("foundational", "sweat", "Sweating helps because", _mcq_opts("it adds mass in kilograms to the bones", "evaporation of water can cool the body", "it is a joint", "it is a newton"), "B", "Evaporative cooling."),
        _SH_MCQ("foundational", "muscle_fig", "<p>A and B in this sketch are</p>" + str(antagonistic_pair()), _mcq_opts("two lungs", "an antagonistic pair of muscles", "two distances", "two food groups"), "B", "A and B pull opposite ways."),
        _SH_KEY("foundational", "joint_word", "Write the word for the place where two bones meet and can move.", "joint", "Joints allow movement."),
        _SH_NUM("foundational", "rest2", "A coach tables 2 rest days in a 7-day week. How many rest days is that?", 2, "Two rest days."),
        _SH_ORD("foundational", "body", "Order skeleton, then joint, then muscle pair.", ["skeleton", "joint", "pair"], _BODY_BANK, "Support, then joints, then antagonistic muscles."),
        _SH_PICK("foundational", "body_ok", "Select the two anatomy facts.", ["skeleton", "joint"], _BODY_BANK, 2, "Skeleton and joint. A slogan is not anatomy."),
        _SH_PICK("foundational", "safe_ok", "Select the two sport-health protections.", ["injury", "uv"], _SAFE_BANK, 2, "Injury sense and UV protection."),
    ],
    "intermediate": [
        _SH_MCQ("intermediate", "flex", "When the muscle on the front of the upper arm shortens, the arm typically", _mcq_opts("lengthens the bones", "bends at the elbow; the opposite muscle relaxes", "becomes a joint made of air", "stops having mass"), "B", "Antagonistic pair."),
        _SH_MCQ("intermediate", "infect", "Broken skin in contact sport should be", _mcq_opts("ignored as a badge of honour", "cleaned and covered following teacher first-aid rules", "used to diagnose classmates", "proof that UV is a joint"), "B", "Infection control, not confession."),
        _SH_MCQ("intermediate", "drug", "A banned performance drug is a problem because it can", _mcq_opts("only change kit colour", "harm health and make the contest unfair", "increase the newton as a unit", "replace water"), "B", "Health and fairness."),
        _SH_MCQ("intermediate", "water", "After heavy sweating a person needs", _mcq_opts("to never drink again", "water; minerals are also lost in sweat", "only a slogan", "to skip first aid"), "B", "Replace water and consider salts."),
        _SH_MCQ("intermediate", "protect", "A helmet in cycling is mainly", _mcq_opts("a fashion unit", "protection for the skull (skeleton)", "a way to measure pulse", "a buoyancy aid made of nitrogen"), "B", "Protect the skeleton."),
        _SH_MCQ("intermediate", "b_label", "<p>Which letter is the muscle below the bone?</p>" + str(antagonistic_pair(title="B below")), _mcq_opts("A", "B", "the bone only", "a joint gas"), "B", "B is below."),
        _SH_KEY("intermediate", "muscle_word", "Write the word for a tissue that pulls on bones to move a joint.", "muscle", "Muscles pull; they do not push bones like pistons."),
        _SH_NUM("intermediate", "pair_n", "One antagonistic pair has how many muscles in the pair?", 2, "A pair is two."),
        _SH_ORD("intermediate", "safe_ord", "Order injury sense, then UV protection.", ["injury", "uv"], _SAFE_BANK, "Load sense, then sun sense."),
        _SH_PICK("intermediate", "not_body", "Select the two items that are not anatomy.", ["slogan", "ignore"], (
            {"id": "slogan", "text": "A sports slogan replaces anatomy"},
            {"id": "ignore", "text": "Ignore bleeding and keep playing no matter what"},
            {"id": "skeleton", "text": "The skeleton supports and protects"},
            {"id": "joint", "text": "A joint is where bones meet and can move"},
        ), 2, "Slogan and ignoring injury are not anatomy."),
    ],
    "difficult": [
        _SH_MCQ("difficult", "both", "A joint needs muscles and a skeleton because", _mcq_opts("bones push themselves with no tissue", "muscles pull on bones that meet at the joint", "air is a muscle", "speed is a bone"), "B", "Levers: muscle, bone, joint."),
        _SH_MCQ("difficult", "overuse", "Repeating the same action with no rest can", _mcq_opts("only improve slogans", "raise injury risk; load and recovery matter", "turn muscle into nitrogen", "ban water"), "B", "Training load is a health idea."),
        _SH_MCQ("difficult", "uv2", "Cloud does not make UV automatically safe. That is why", _mcq_opts("pupils must compare skin colour in the quiz", "outdoor sessions still follow the school's sun policy", "joints become lungs", "drugs replace shade"), "B", "Policy, not a body survey."),
        _SH_MCQ("difficult", "honest", "Fair sport includes", _mcq_opts("secret banned drugs", "following anti-doping and medical rules, not asking classmates what they take", "ignoring bleeding", "skipping water"), "B", "No personal drug disclosure in the app."),
        _SH_MCQ("difficult", "a_label", "<p>Which letter is the muscle above the bone?</p>" + str(antagonistic_pair(title="A above")), _mcq_opts("B", "A", "neither", "a banned drug"), "B", "A is above."),
        _SH_KEY("difficult", "skeleton_word", "Write the word for the body's framework of bones.", "skeleton", "The skeleton supports and protects."),
        _SH_NUM("difficult", "rest", "A coach plans 3 rest days in a 7-day week. How many rest days is that?", 3, "Three rest days."),
        _SH_ORD("difficult", "chain", "Order skeleton, joint, then antagonistic pair.", ["skeleton", "joint", "pair"], _BODY_BANK, "Framework, meeting point, opposite muscles."),
        _SH_PICK("difficult", "protect_two", "Select the two health protections.", ["injury", "uv"], _SAFE_BANK, 2, "Injury and UV."),
        _SH_PICK("difficult", "drug_uv", "Select the two ideas about drugs and ignoring injury.", ["drug", "ignore"], _SAFE_BANK, 2, "Drugs can be unsafe or unfair; ignoring bleeding is wrong."),
    ],
}

_SH_STANDARD = {
    "foundational": (
        'sport_health_foundational_mcq_antag',
        'sport_health_foundational_keyword_joint_word',
        'sport_health_foundational_number_rest2',
        'sport_health_foundational_order_body',
        'sport_health_foundational_pick_body_ok',
    ),
    "intermediate": (
        'sport_health_intermediate_mcq_b_label',
        'sport_health_intermediate_keyword_muscle_word',
        'sport_health_intermediate_number_pair_n',
        'sport_health_intermediate_order_safe_ord',
        'sport_health_intermediate_pick_not_body',
    ),
    "difficult": (
        'sport_health_difficult_mcq_a_label',
        'sport_health_difficult_keyword_skeleton_word',
        'sport_health_difficult_number_rest',
        'sport_health_difficult_order_chain',
        'sport_health_difficult_pick_drug_uv',
    ),
}
eursc_science_sport_health, eursc_science_sport_health_variants = bind_eursc_topic(
    'sport_health', _SH_POOLS, _SH_STANDARD
)
