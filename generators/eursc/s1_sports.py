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
        _MV_MCQ("foundational", "avg", "Average speed is", _mcq_opts("time divided by distance", "distance divided by time", "mass divided by volume", "a feeling"), "B", "v = d/t for average speed.", "You combine how far with how long. Which way round: distance over time, or time over distance?"),
        _MV_MCQ("foundational", "si", "A fair speed calculation should use", _mcq_opts("a mix of miles and seconds with no conversion", "consistent units, such as metres and seconds", "only the athlete's fame", "guessed times"), "B", "Units must match.", "Do not mix miles with seconds and skip converting. Keep distance and time in matching SI units."),
        _MV_MCQ("foundational", "rest", "If distance does not change while time passes, average speed is", _mcq_opts("infinite", "zero", "the same as mass", "1 newton"), "B", "No distance change means speed 0.", "Staying in the same place means the distance travelled is 0. What does v = d/t give when d is 0?"),
        _MV_MCQ("foundational", "measure", "To find a runner's average speed you need", _mcq_opts("only the colour of the vest", "a distance and a time", "only the crowd noise", "a force in newtons only"), "B", "Speed needs d and t.", "A speed calculation needs two measurements of the run, not vest colour, crowd noise, or a force on its own."),
        _MV_MCQ("foundational", "unit_s", "The SI unit of time in v = d/t is usually the", _mcq_opts("kilogram", "second", "ampere", "candela"), "B", "Time is in seconds in SI.", "SI time for this formula is the usual clock unit, not a unit of mass, current, or light."),
        _MV_MCQ("foundational", "graph_rest", "<p>Which labelled part of this distance–time graph shows rest?</p>" + str(distance_time_graph()), _mcq_opts("A", "B", "C", "the word time"), "B", "B is the flat section.", "Rest is where distance stays the same while the clock still runs. Find the flat stretch, not a sloping stretch."),
        _MV_KEY("foundational", "speed_word", "Write the word for distance divided by time.", "speed", "Average speed is distance over time.", "One word names what you get when you divide how far by how long. Do not write the formula v = d/t."),
        _MV_NUM("foundational", "v0", "Distance 10 m, time 2 s. What is average speed in m/s?", 5, "10 / 2 = 5.", "Use v = d/t with metres and seconds already matching. Divide 10 by 2."),
        _MV_ORD("foundational", "calc", "Order measuring, then dividing, to get average speed.", ["measure", "divide"], _SPEED_BANK, "Measure d and t, then divide.", "First collect distance and time in SI units, then divide those two readings. Skip kit-colour guesses and hiding the clock."),
        _MV_PICK("foundational", "need_two", "Select the two steps that belong in a speed investigation.", ["measure", "divide"], _SPEED_BANK, 2, "Measure and divide. Guessing kit colour is not a method.", "Choose taking SI readings of distance and time, then dividing. Skip guessing from kit colour and hiding the stopwatch."),
        _MV_PICK("foundational", "graph_ok", "Select the two correct graph ideas.", ["slope", "flat"], _GRAPH_BANK, 2, "Slope means moving; flat means rest.", "Choose what a sloping line means and what a flat line means. Line colour and fame are not graph science."),
    ],
    "intermediate": [
        _MV_MCQ("intermediate", "num", "A cyclist travels 20 m in 4 s. Average speed is", _mcq_opts("80 m/s", "5 m/s", "16 m/s", "0 m/s"), "B", "20 / 4 = 5 m/s.", "Units already match. Divide the 20 m by the 4 s; do not multiply them."),
        _MV_MCQ("intermediate", "km", "3 km in 1/2 hour is the same as 3000 m in 1800 s. Average speed is", _mcq_opts("0.6 m/s", "about 1.67 m/s", "3000 m/s", "1800 m/s"), "B", "3000 / 1800 ≈ 1.67 m/s.", "The conversion to metres and seconds is already done. Divide 3000 by 1800 and pick the close value."),
        _MV_MCQ("intermediate", "convert", "2 minutes is how many seconds?", _mcq_opts("2", "120", "60", "200"), "B", "2 × 60 = 120 s.", "Each minute has 60 seconds. Multiply 2 by 60; do not leave the answer as 2, and 60 would be only one minute."),
        _MV_MCQ("intermediate", "read_d", "A graph shows 12 m at 3 s on a straight slope from the origin. Average speed so far is", _mcq_opts("36 m/s", "4 m/s", "9 m/s", "15 m/s"), "B", "12 / 3 = 4 m/s.", "Read 12 m and 3 s from the straight slope that starts at the origin, then divide distance by time."),
        _MV_MCQ("intermediate", "steeper", "On a distance–time graph, a steeper slope means", _mcq_opts("slower movement", "greater speed", "the object has more mass", "time has stopped"), "B", "Steeper d–t slope is faster.", "Slope on this graph is how quickly distance grows. A steeper line means distance is growing faster, not that mass changed."),
        _MV_MCQ("intermediate", "graph_move", "<p>Which labelled part shows the object moving after rest?</p>" + str(distance_time_graph(title="Distance–time: C is moving again")), _mcq_opts("B only", "C", "the word d", "a force arrow"), "B", "C is the later slope. B is rest.", "The flat stretch is rest. Movement after that rest is the sloping part that comes later. Match the letter to that later slope."),
        _MV_KEY("intermediate", "metre_word", "Write the SI unit of distance used with seconds to give metres per second.", "metre", "Distance in metres.", "Name the SI length unit you pair with seconds for this speed unit. Do not write the time unit or the letters m/s."),
        _MV_NUM("intermediate", "v1", "Distance 30 m, time 5 s. What is average speed in m/s?", 6, "30 / 5 = 6.", "v = d/t again, still with matching metres and seconds. Divide 30 by 5."),
        _MV_ORD("intermediate", "graph_read", "Order the moving idea, then the rest idea, when reading a d–t graph.", ["slope", "flat"], _GRAPH_BANK, "Slope first as movement, then flat as rest.", "Put the sloping-line idea first, then the flat-line idea. Skip line colour and a famous athlete."),
        _MV_PICK("intermediate", "not_method", "Select the two choices that are not scientific speed methods.", ["guess", "secret"], _SPEED_BANK, 2, "Guessing kit and hiding times are not methods.", "Choose guessing the winner from kit colour, and hiding the stopwatch so nobody can check. Those are not methods."),
    ],
    "difficult": [
        _MV_MCQ("difficult", "avg_vs", "Average speed for a whole lap can be low even if a sprint section was fast because", _mcq_opts("speed cannot be calculated", "the total distance is divided by the total time, including slower parts", "mass changes the formula", "graphs are forbidden"), "B", "Average uses whole d and whole t.", "The whole-lap value uses all the distance and all the time, including slow parts, not only the fastest sprint."),
        _MV_MCQ("difficult", "units", "A student writes 8 km/h as 8 m/s without converting. The error is", _mcq_opts("there is no error", "the units are not the same; 8 km/h is much slower than 8 m/s", "time is in kilograms", "distance is in newtons"), "B", "Convert before comparing.", "The number 8 is the same but the units are not. Kilometres per hour is not the same as metres per second until you convert."),
        _MV_MCQ("difficult", "zero_t", "Time in v = d/t cannot be zero because", _mcq_opts("athletes dislike clocks", "dividing by zero is not a valid speed", "distance must be zero too", "SI units fail"), "B", "You need a time interval.", "The formula divides by the time interval. Think what happens in maths if that interval is 0."),
        _MV_MCQ("difficult", "plateau", "A flat d–t section then a slope means", _mcq_opts("the object was always at rest", "rest then movement again", "negative mass", "a force with no interaction"), "B", "Read each part of the graph.", "Read the graph in order: first a stretch where distance does not change, then a stretch where it does. That is two different motions in sequence."),
        _MV_MCQ("difficult", "graph_a", "<p>Which labelled part is the first moving section?</p>" + str(distance_time_graph(title="Distance–time: A is the first slope")), _mcq_opts("B", "A", "the caption only", "C only and never A"), "B", "A is the first slope.", "The first moving section is the first sloping part, before any rest. Match the letter to that opening slope, not the flat middle."),
        _MV_KEY("difficult", "average_word", "Write the word that describes speed over a whole journey, not one instant.", "average", "Average speed uses total d and t.", "One word means 'for the whole trip' when you use total distance and total time, not one instant. Do not write 'speed'."),
        _MV_NUM("difficult", "v2", "A swimmer covers 100 m in 50 s. Average speed in m/s?", 2, "100 / 50 = 2.", "v = d/t with 100 m and 50 s already matching. Divide 100 by 50."),
        _MV_ORD("difficult", "full", "Order measure, then divide, for a fair average speed.", ["measure", "divide"], _SPEED_BANK, "Do not hide the stopwatch.", "A fair method still starts with SI readings of distance and time, then the division. Do not hide the stopwatch or guess from kit."),
        _MV_PICK("difficult", "graph_false", "Select the two graph myths.", ["colour", "fame"], _GRAPH_BANK, 2, "Line colour and fame are not speed.", "Choose the two unscientific graph claims: that a red line is always faster, and that a famous athlete cannot be measured."),
        _MV_PICK("difficult", "keep_speed", "Select the two scientific speed steps.", ["measure", "divide"], _SPEED_BANK, 2, "Measure and divide.", "Choose the two proper steps for a fair whole-journey value: take the SI readings, then divide. Skip guesses and secrets."),
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
        _FS_MCQ("foundational", "effect", "A force can", _mcq_opts("only change an object's colour", "change motion or shape", "remove mass from the universe", "replace time"), "B", "Forces change motion or shape.", "A push or pull can start, stop, speed up, slow down, or squash something. Colour-only and deleting mass from the universe are not those effects."),
        _FS_MCQ("foundational", "unit", "The SI unit of force is the", _mcq_opts("metre", "newton", "second", "candela"), "B", "Force is measured in newtons.", "Force has its own SI unit, named after a scientist. It is not a length unit, a time unit, or a light unit."),
        _FS_MCQ("foundational", "pair", "If a footballer pushes a ball, the ball", _mcq_opts("does nothing back", "pushes back on the footballer (an interaction)", "gains infinite mass", "stops time"), "B", "Forces come in interaction pairs.", "Forces are interactions between two objects. If one object pushes another, think what the second object does to the first."),
        _FS_MCQ("foundational", "friction", "Friction between shoe and track can", _mcq_opts("only exist in a vacuum", "help the athlete push forward without slipping", "be the same as weight in newtons always", "remove the need for mass"), "B", "Useful grip is friction.", "This contact force between shoe and track can stop a slip. That useful grip is how you push forward on a track, not a vacuum-only idea."),
        _FS_MCQ("foundational", "mass", "Mass is", _mcq_opts("the pull of the Earth in newtons", "the amount of matter, in kilograms", "a type of friction", "a feeling of tiredness"), "B", "Mass is kilograms of matter.", "This is how much matter is in an object, in kilograms. The Earth's pull in newtons is a different idea."),
        _FS_MCQ("foundational", "boxes", "<p>In this sketch the two boxes push on each other. The interaction idea is that</p>" + str(force_pair()), _mcq_opts("only A can push", "A and B push each other", "there is no force", "mass is zero"), "B", "Each pushes the other.", "Look at the sketch: two boxes touch. Each can push the other. That is the interaction, not 'only A' and not 'no force'."),
        _FS_KEY("foundational", "newton_word", "Write the SI unit of force.", "newton", "The newton is the force unit.", "Name the SI unit used for a push or pull. Do not write kilogram, metre, or second."),
        _FS_NUM("foundational", "net0", "Two 2 N forces pull a ring equally opposite. The net force in newtons is", 0, "Equal opposite forces cancel.", "The two pulls are equal and opposite, so they cancel. Subtract 2 from 2, or add them as opposites: what leftover is there?"),
        _FS_ORD("foundational", "think", "Order a force effect, then the interaction idea.", ["push", "pair"], _FORCE_BANK, "Effects, then pairs. Magic forces are not used.", "First what a force can do to motion or shape, then the idea that if A pushes B, B pushes A. Skip magic and missing units."),
        _FS_PICK("foundational", "force_ok", "Select the two scientific force ideas.", ["push", "pair"], _FORCE_BANK, 2, "Effects and interactions.", "Choose the motion-or-shape effect and the interaction-pair idea. Skip a force with no object and force having no unit."),
        _FS_PICK("foundational", "fric_ok", "Select the two friction ideas that belong in sport.", ["grip", "slow"], _FRIC_BANK, 2, "Grip and slowing. Vacuum-only and mass mix-ups are wrong.", "Choose helpful shoe grip and slowing a slide. Skip 'only in outer space with no contact' and mixing this force with mass in kilograms."),
    ],
    "intermediate": [
        _FS_MCQ("intermediate", "weight", "Weight is", _mcq_opts("mass in kilograms", "the gravitational force on a mass, in newtons", "friction only", "speed"), "B", "Weight is a force.", "This is the Earth's pull on an object. It is a force in newtons, not the kilograms-of-matter reading and not a contact force that opposes slipping."),
        _FS_MCQ("intermediate", "balance", "A gymnast still on a beam with no acceleration has", _mcq_opts("no forces at all", "balanced forces (equilibrium)", "infinite speed", "zero mass"), "B", "Balanced forces, not zero forces.", "Still, with no acceleration, does not mean 'no forces'. Gravity still pulls; other forces cancel it so the leftover is zero."),
        _FS_MCQ("intermediate", "cog", "A high centre of gravity on a narrow base tends to be", _mcq_opts("more stable", "less stable", "heavier in kilograms automatically", "frictionless"), "B", "Stability links CoG and base.", "Think how easy it is to tip something tall and thin compared with something low and wide. Kilograms of matter do not jump up just because the centre is high."),
        _FS_MCQ("intermediate", "slow_fric", "A puck sliding on ice slows because", _mcq_opts("mass disappears", "friction (and air) act against the motion", "time reverses", "weight becomes mass"), "B", "Friction opposes sliding.", "Ice still has a contact force that opposes the slide, and air acts too. Matter does not vanish, and time does not run backwards."),
        _FS_MCQ("intermediate", "same_mass", "On the Moon a shot-put has the same mass as on Earth but", _mcq_opts("the same weight", "a smaller weight", "negative mass", "no matter"), "B", "Mass stays; gravitational force changes.", "Kilograms of matter stay the same if you take the shot-put to the Moon. The gravitational pull is weaker there, so that force changes."),
        _FS_MCQ("intermediate", "pair2", "<p>Arrow A on B and B on A in this diagram are</p>" + str(force_pair(title="Matching pushes")), _mcq_opts("unrelated rumours", "a matching interaction pair", "units of time", "masses in kilograms"), "B", "Interaction pair.", "The two arrows are the two sides of one interaction between the boxes, not rumours, seconds, or kilograms."),
        _FS_KEY("intermediate", "friction_word", "Write the word for a contact force that opposes slipping or sliding.", "friction", "Friction can grip or slow.", "Name the contact force that can help a shoe grip or can slow a sliding puck. Do not write 'grip', 'newton', or 'mass'."),
        _FS_NUM("intermediate", "n1", "Two 3 N forces pull a ring equally opposite. The net force in newtons is", 0, "Equal opposite forces cancel.", "Now the equal opposite pulls are 3 N each. They still cancel: subtract 3 from 3 for the leftover on the ring."),
        _FS_ORD("intermediate", "fric_order", "Order helpful grip, then slowing, as friction jobs.", ["grip", "slow"], _FRIC_BANK, "Grip then slowing.", "Put shoe-grip first, then slowing a slide. Skip vacuum-only and treating this force as mass."),
        _FS_PICK("intermediate", "not_force", "Select the two unscientific force claims.", ["magic", "unitless"], _FORCE_BANK, 2, "Forces need objects and have a unit.", "Choose a force appearing with no object, and force having no unit in science. Those two claims are unscientific."),
    ],
    "difficult": [
        _FS_MCQ("difficult", "eq", "Equilibrium of a still object means", _mcq_opts("no gravity exists", "resultant force is zero", "mass is zero", "friction is forbidden"), "B", "Net force zero.", "The object can still have several forces. Equilibrium means those forces add to nothing leftover (the resultant is 0), not that gravity has vanished."),
        _FS_MCQ("difficult", "lean", "A rugby player leaning with a wide stance is more stable because", _mcq_opts("mass becomes infinite", "the line from the centre of gravity more easily stays over a wider base", "friction disappears", "weight is not a force"), "B", "Base and CoG.", "A wider stance makes a wider base, so the line down from the centre of gravity is more likely to stay inside that base. Matter does not become infinite."),
        _FS_MCQ("difficult", "n3", "A sprinter pushes the blocks backwards; the blocks", _mcq_opts("do nothing", "push the sprinter forwards", "remove the sprinter's mass", "stop the clock"), "B", "Interaction pair.", "The sprinter pushes the blocks one way. Interaction pairs mean the blocks act on the sprinter the other way, which is what starts the run."),
        _FS_MCQ("difficult", "air", "Air resistance on a speeding cyclist is a force that", _mcq_opts("always helps the cyclist", "usually acts against the motion through air", "is measured in seconds", "is the same as mass"), "B", "Drag opposes motion.", "Moving fast through air, you feel a force from the air. Which way does that force usually act relative to the motion? It is not a time unit."),
        _FS_MCQ("difficult", "read_n", "A spring balance reads 10 N for a bag on Earth. That reading is closest to", _mcq_opts("the bag's mass in kilograms", "the bag's weight", "the time of fall", "friction in metres"), "B", "Newtons on a spring balance are weight.", "A spring balance in newtons is measuring a force. On Earth, that hanging reading is the gravitational pull on the bag, not the kilograms-of-matter value."),
        _FS_KEY("difficult", "weight_word", "Write the word for the gravitational force on an object.", "weight", "Weight is a force in newtons.", "Name the Earth's pull on an object (a force in newtons). Do not write 'mass', 'newton', or 'gravity' as a unit."),
        _FS_NUM("difficult", "sum", "Forces 4 N right and 1 N left along a line. Resultant size in newtons?", 3, "4 − 1 = 3 N.", "The forces are along one line but not equal. Subtract the smaller from the larger to get the size of the leftover."),
        _FS_ORD("difficult", "pair_after", "Order a force effect, then the interaction pair.", ["push", "pair"], _FORCE_BANK, "Effects then pairs.", "Start with what a force can do to motion or shape, then the matching-push idea. Same scientific order, still skipping magic."),
        _FS_PICK("difficult", "keep_f", "Select the two force facts.", ["push", "pair"], _FORCE_BANK, 2, "Effects and interactions.", "Choose start-stop-shape effects and the A-pushes-B idea. Skip a force with no object and a missing unit."),
        _FS_PICK("difficult", "bad_f", "Select the two friction mix-ups.", ["vacuum", "massless"], _FRIC_BANK, 2, "Friction is not 'only in space' and not mass.", "Choose 'only in outer space with no contact' and treating this contact force as mass in kilograms. Those two are mix-ups."),
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
        _BR_MCQ("foundational", "air", "Ordinary air is mostly", _mcq_opts("oxygen only", "nitrogen, with oxygen as a smaller share", "pure carbon dioxide", "liquid water"), "B", "Nitrogen dominates air.", "Ordinary air is a mixture. The largest share is not the gas cells use, and it is not carbon dioxide or liquid water."),
        _BR_MCQ("foundational", "exhale", "Compared with inhaled air, exhaled air usually has", _mcq_opts("more oxygen and less carbon dioxide", "less oxygen and more carbon dioxide", "no nitrogen", "only helium"), "B", "Respiration uses O2 and produces CO2.", "Cells take in one gas from air and give out another. So the air you breathe out has less of the used gas and more of the waste gas."),
        _BR_MCQ("foundational", "resp", "Respiration in this lesson means", _mcq_opts("only the chest moving", "cells using oxygen to release energy from food", "the skeleton growing", "friction"), "B", "Cellular respiration, not only breathing movements.", "This is the cell process that uses a gas from air to get energy from food. Chest movement is a different idea."),
        _BR_MCQ("foundational", "pulse", "Pulse rate is a clue to", _mcq_opts("shoe size", "how often the heart is beating", "the newton", "air's colour"), "B", "Pulse tracks heart beats.", "This is the beat you can feel in a wrist or neck. It matches how often the chest pump is working, not shoe size or a force unit."),
        _BR_MCQ("foundational", "heart", "The heart's job in this unit is to", _mcq_opts("digest food", "pump blood", "store oxygen as a metal", "measure distance"), "B", "The heart is a pump.", "This organ moves blood around the body. It is not a stomach, a metal store, or a tape measure."),
        _BR_MCQ("foundational", "boxes", "<p>Which letter is the heart on this schematic?</p>" + str(circulation_boxes()), _mcq_opts("B", "A", "C", "the word lungs"), "B", "A is labelled heart.", "Match the letter to the organ that pumps blood. Use the schematic labels, not the word for the gas-exchange organs."),
        _BR_KEY("foundational", "oxygen_word", "Write the gas cells use in respiration.", "oxygen", "Oxygen is used by cells.", "Name the gas in air that cells use to release energy from food. Do not write nitrogen or carbon dioxide."),
        _BR_NUM("foundational", "pulse60", "A pulse of 10 beats in 10 s is how many beats in 60 s if the rate stays the same?", 60, "10 × 6 = 60.", "Ten beats in ten seconds is one beat per second. Scale that rate up to 60 s: there are six lots of 10 s in a minute, so multiply the count by 6."),
        _BR_ORD("foundational", "path", "Order heart pump, then lungs adding oxygen, then body use.", ["heart", "lungs", "body"], _CIRC_BANK, "Heart, lungs, tissues.", "Start with the pump, then the organs that add the useful gas to blood, then the tissues that use it. Skip bones pumping air."),
        _BR_PICK("foundational", "air_ok", "Select the two true statements about air gases.", ["nitrogen", "oxygen"], _AIR_BANK, 2, "Nitrogen majority; oxygen used in respiration.", "Choose the main gas in ordinary air, and the gas cells use. Skip helium in a sports hall and 'air contains no gases'."),
        _BR_PICK("foundational", "circ_ok", "Select the two circulation jobs.", ["heart", "lungs"], _CIRC_BANK, 2, "Heart pumps; lungs oxygenate.", "Choose the pump and the organs that add the useful gas. Skip tissues using the gas for this pick, and skip bones as pumps."),
    ],
    "intermediate": [
        _BR_MCQ("intermediate", "breathe", "Breathing movements move air so that", _mcq_opts("bones can pump", "gas exchange at the lungs can happen", "mass becomes weight", "friction disappears"), "B", "Ventilation supports gas exchange.", "Chest movements move air in and out so gases can swap at the lungs. Bones do not pump air, and mass does not turn into a force."),
        _BR_MCQ("intermediate", "co2", "More carbon dioxide in exhaled air is evidence that", _mcq_opts("the person did not respire", "respiration produced CO2", "air is helium", "the heart is a lung"), "B", "CO2 is a product.", "Extra waste gas in the air you breathe out is a product of the cell energy process, not a sign that it did not happen, and not helium."),
        _BR_MCQ("intermediate", "sport", "During hard exercise, pulse often rises because", _mcq_opts("the skeleton wants fame", "muscles need more oxygen delivered by blood", "time stops", "air contains no oxygen"), "B", "Demand for oxygen rises.", "Working muscles need more of the useful gas. Blood delivers it, so the pump often beats faster. Time does not stop, and air still contains that gas."),
        _BR_MCQ("intermediate", "blood", "Blood carries", _mcq_opts("only nitrogen bubbles as the whole job", "oxygen (and other substances) around the body", "newtons of force only", "distance in metres"), "B", "Blood is a transport tissue.", "This liquid tissue carries gases and other substances around the body. It is not a unit of force or a distance in metres."),
        _BR_MCQ("intermediate", "pressure", "Deeper under water, pressure on the body", _mcq_opts("falls to zero", "increases", "becomes a mass in kilograms", "removes buoyancy"), "B", "Pressure increases with depth.", "Deeper water means a taller column of liquid above. What happens to the squeeze on a swimmer? It is still pressure, not kilograms of matter."),
        _BR_MCQ("intermediate", "lungs_box", "<p>Which letter marks the lungs?</p>" + str(circulation_boxes(title="B lungs")), _mcq_opts("A", "B", "C", "none"), "B", "B is lungs.", "Match the letter to the organs that add the useful gas to blood. Use the schematic, not 'none'."),
        _BR_KEY("intermediate", "pulse_word", "Write the word for the beat you can feel that matches the heart.", "pulse", "Pulse follows heart rate.", "Name the beat you can feel at a wrist or neck that matches how often the chest pump works. Do not write 'heart'."),
        _BR_NUM("intermediate", "beats", "A pulse of 20 beats in 15 s is how many beats in 60 s if the rate stays the same?", 80, "20 × 4 = 80.", "Twenty beats in fifteen seconds. Fifteen seconds is a quarter of a minute, so multiply that count by 4 to scale up to 60 s."),
        _BR_ORD("intermediate", "circ2", "Order lungs, then body tissues, after the heart has pumped.", ["lungs", "body"], _CIRC_BANK, "Oxygenate, then use.", "After the pump has sent blood, first the gas-exchange organs, then the tissues that use the gas. Skip bones pumping air."),
        _BR_PICK("intermediate", "air_myth", "Select the two false air claims.", ["helium_air", "no_gas"], _AIR_BANK, 2, "Air is not mostly helium and is not 'thoughts'.", "Choose air mostly helium in a sports hall, and air containing no gases, only thoughts. Those two claims are false."),
    ],
    "difficult": [
        _BR_MCQ("difficult", "link", "Breathing, circulation and respiration link because", _mcq_opts("they are three names for friction", "air movement, blood transport and cell chemistry work together", "the skeleton stores oxygen as a solid bar", "speed is force"), "B", "The three ideas connect in sport.", "Air movement, blood carrying gases, and cell chemistry are three different jobs that work together in sport, not three names for a contact force."),
        _BR_MCQ("difficult", "buoy", "A swimmer floats more easily in denser salty water because", _mcq_opts("mass becomes zero", "upthrust (buoyancy) is greater in the denser liquid", "pulse stops", "oxygen is a metal"), "B", "Buoyancy depends on the liquid.", "A denser liquid pushes up more on an immersed body. That upward force is why floating feels easier in salty water. Matter does not become zero."),
        _BR_MCQ("difficult", "not_same", "Chest movement is not the same as respiration because", _mcq_opts("science forbids the word oxygen", "moving air is ventilation; respiration is the cell process that uses oxygen", "the heart is a lung", "CO2 is nitrogen"), "B", "Keep the words distinct.", "Chest movement moves air. The cell process that uses the useful gas is a different idea with a different name. Keep those two words distinct."),
        _BR_MCQ("difficult", "recover", "After a sprint, breathing stays fast for a while because", _mcq_opts("the race clock is broken", "the body is still supplying extra oxygen and clearing extra carbon dioxide", "mass increased", "friction is respiration"), "B", "Recovery needs gas exchange.", "After a sprint the cells still need extra useful gas and still need to get rid of extra waste gas, so breathing stays high for a bit. The race clock is not the reason."),
        _BR_MCQ("difficult", "body_box", "<p>Which letter is body tissue using oxygen?</p>" + str(circulation_boxes(title="C body")), _mcq_opts("A", "C", "B only", "the word heart"), "B", "C is body.", "Match the letter to the tissues that use the useful gas and make the waste gas. That is not the pump and not only the lungs."),
        _BR_KEY("difficult", "buoyancy_word", "Write the word for the upward force from a liquid on an immersed object.", "buoyancy", "Buoyancy is upthrust in water sport.", "Name the upward force a liquid exerts on something immersed in it. Do not write 'weight' or 'mass'."),
        _BR_NUM("difficult", "pulse2", "12 beats in 10 s. Beats per minute if the rate is steady?", 72, "12 × 6 = 72.", "Twelve beats in ten seconds. Ten seconds is one-sixth of a minute, so multiply that count by 6 to get a minute."),
        _BR_ORD("difficult", "full_circ", "Order heart, lungs, then body.", ["heart", "lungs", "body"], _CIRC_BANK, "Pump, oxygenate, use.", "Pump first, then gas-exchange organs, then tissues — the full path this time, all three genuine roles, still skipping bones as pumps."),
        _BR_PICK("difficult", "circ_three", "Select the three genuine circulation roles.", ["heart", "lungs", "body"], _CIRC_BANK, 3, "Bones do not pump air here.", "Choose the pump, the gas-exchange organs, and the tissues that use the gas. Skip bones pumping air like a bicycle tyre."),
        _BR_PICK("difficult", "keep_air", "Select the two air facts.", ["nitrogen", "oxygen"], _AIR_BANK, 2, "Nitrogen and oxygen.", "Choose the majority gas in ordinary air and the gas cells use, again. Skip helium-hall and thoughts-instead-of-gases."),
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
        _SH_MCQ("foundational", "skel", "The skeleton mainly", _mcq_opts("pumps blood", "supports the body and protects organs", "stores rumours", "is a type of friction"), "B", "Support and protection.", "This framework of bones holds you up and shields organs. It does not pump blood, store rumours, or act as a contact force."),
        _SH_MCQ("foundational", "joint", "A joint is", _mcq_opts("a muscle that never attaches", "where bones meet and movement can happen", "a gas in air", "a unit of speed"), "B", "Bones meet at joints.", "Bones need a meeting place so the body can bend. That meeting place is not a gas and not a unit of speed."),
        _SH_MCQ("foundational", "antag", "Antagonistic muscles", _mcq_opts("always pull the same way", "work in pairs that pull in opposite ways", "are bones", "are banned drugs"), "B", "Opposite pulls.", "These tissues pull; they cannot push a bone like a piston. So they work as a pair pulling opposite ways, not as bones or banned drugs."),
        _SH_MCQ("foundational", "uv", "UV from the sun can damage skin. Outdoor sport should", _mcq_opts("ignore covering and shade", "use shade, covering or teacher-approved protection, not a classroom skin survey", "require pupils to compare tans", "replace water with bleach"), "B", "Protection without body ranking.", "Sunlight includes radiation that can damage skin. Outdoor sport uses shade and covering. This quiz does not rank tans or replace water with bleach."),
        _SH_MCQ("foundational", "sweat", "Sweating helps because", _mcq_opts("it adds mass in kilograms to the bones", "evaporation of water can cool the body", "it is a joint", "it is a newton"), "B", "Evaporative cooling.", "Water on the skin can evaporate. That change of state takes heat away from the body. It is not a meeting of bones and not a force unit."),
        _SH_MCQ("foundational", "muscle_fig", "<p>A and B in this sketch are</p>" + str(antagonistic_pair()), _mcq_opts("two lungs", "an antagonistic pair of muscles", "two distances", "two food groups"), "B", "A and B pull opposite ways.", "The sketch shows two tissues that pull opposite ways around a bone. They are not lungs, distances, or food groups."),
        _SH_KEY("foundational", "joint_word", "Write the word for the place where two bones meet and can move.", "joint", "Joints allow movement.", "Name the place where two bones meet and movement can happen. Do not write 'bone' or the name of the pulling tissue."),
        _SH_NUM("foundational", "rest2", "A coach tables 2 rest days in a 7-day week. How many rest days is that?", 2, "Two rest days.", "The table already states how many rest days are in the week. Copy that count; do not add the training days or enter 7."),
        _SH_ORD("foundational", "body", "Order skeleton, then joint, then muscle pair.", ["skeleton", "joint", "pair"], _BODY_BANK, "Support, then joints, then antagonistic muscles.", "First the bone framework, then where bones meet, then the opposite-pull pair. Skip a slogan standing in for anatomy."),
        _SH_PICK("foundational", "body_ok", "Select the two anatomy facts.", ["skeleton", "joint"], _BODY_BANK, 2, "Skeleton and joint. A slogan is not anatomy.", "Choose the bone framework and where bones meet. A slogan is not anatomy, and skip the opposite-pull pair for this pick."),
        _SH_PICK("foundational", "safe_ok", "Select the two sport-health protections.", ["injury", "uv"], _SAFE_BANK, 2, "Injury sense and UV protection.", "Choose sensible load and warm-up, and reducing sun damage outdoors. Skip banned drugs and ignoring bleeding."),
    ],
    "intermediate": [
        _SH_MCQ("intermediate", "flex", "When the muscle on the front of the upper arm shortens, the arm typically", _mcq_opts("lengthens the bones", "bends at the elbow; the opposite muscle relaxes", "becomes a joint made of air", "stops having mass"), "B", "Antagonistic pair.", "When one tissue of a pair shortens, the other relaxes. At the elbow that typically bends the arm. Bones do not get longer, and matter does not vanish."),
        _SH_MCQ("intermediate", "infect", "Broken skin in contact sport should be", _mcq_opts("ignored as a badge of honour", "cleaned and covered following teacher first-aid rules", "used to diagnose classmates", "proof that UV is a joint"), "B", "Infection control, not confession.", "Broken skin can let in germs. Follow first-aid rules: clean and cover. Do not ignore it as a badge or use it to diagnose classmates."),
        _SH_MCQ("intermediate", "drug", "A banned performance drug is a problem because it can", _mcq_opts("only change kit colour", "harm health and make the contest unfair", "increase the newton as a unit", "replace water"), "B", "Health and fairness.", "Some substances are banned because they can harm the body and because they make the contest unfair. Kit colour and the newton as a unit do not change."),
        _SH_MCQ("intermediate", "water", "After heavy sweating a person needs", _mcq_opts("to never drink again", "water; minerals are also lost in sweat", "only a slogan", "to skip first aid"), "B", "Replace water and consider salts.", "Sweat is mostly water, and some minerals leave with it. After heavy sweating you need to replace liquid, not skip drinks or first aid."),
        _SH_MCQ("intermediate", "protect", "A helmet in cycling is mainly", _mcq_opts("a fashion unit", "protection for the skull (skeleton)", "a way to measure pulse", "a buoyancy aid made of nitrogen"), "B", "Protect the skeleton.", "A helmet sits on the head. Its main job is to protect the bony framework of the skull, not to measure a wrist beat or to keep you afloat."),
        _SH_MCQ("intermediate", "b_label", "<p>Which letter is the muscle below the bone?</p>" + str(antagonistic_pair(title="B below")), _mcq_opts("A", "B", "the bone only", "a joint gas"), "B", "B is below.", "Match the letter to the pulling tissue drawn below the bone in the sketch, not the bone itself."),
        _SH_KEY("intermediate", "muscle_word", "Write the word for a tissue that pulls on bones to move a joint.", "muscle", "Muscles pull; they do not push bones like pistons.", "Name the tissue that pulls on bones to move a meeting of bones. Do not write the meeting-place word or 'bone'."),
        _SH_NUM("intermediate", "pair_n", "One antagonistic pair has how many muscles in the pair?", 2, "A pair is two.", "A pair means two. Count how many pulling tissues are in one opposite-pull pair."),
        _SH_ORD("intermediate", "safe_ord", "Order injury sense, then UV protection.", ["injury", "uv"], _SAFE_BANK, "Load sense, then sun sense.", "First sensible load and warm-up, then sun protection outdoors. Skip banned drugs and ignoring bleeding for this order."),
        _SH_PICK("intermediate", "not_body", "Select the two items that are not anatomy.", ["slogan", "ignore"], (
            {"id": "slogan", "text": "A sports slogan replaces anatomy"},
            {"id": "ignore", "text": "Ignore bleeding and keep playing no matter what"},
            {"id": "skeleton", "text": "The skeleton supports and protects"},
            {"id": "joint", "text": "A joint is where bones meet and can move"},
        ), 2, "Slogan and ignoring injury are not anatomy.", "Choose a slogan standing in for science, and ignoring bleeding. Those two are not anatomy."),
    ],
    "difficult": [
        _SH_MCQ("difficult", "both", "A joint needs muscles and a skeleton because", _mcq_opts("bones push themselves with no tissue", "muscles pull on bones that meet at the joint", "air is a muscle", "speed is a bone"), "B", "Levers: muscle, bone, joint.", "Bones meet at a meeting place; pulling tissues pull on those bones. Bones do not push themselves, and air is not a pulling tissue."),
        _SH_MCQ("difficult", "overuse", "Repeating the same action with no rest can", _mcq_opts("only improve slogans", "raise injury risk; load and recovery matter", "turn muscle into nitrogen", "ban water"), "B", "Training load is a health idea.", "Repeating the same action with no recovery can raise the chance of injury. Load and rest both matter. Tissue does not turn into nitrogen."),
        _SH_MCQ("difficult", "uv2", "Cloud does not make UV automatically safe. That is why", _mcq_opts("pupils must compare skin colour in the quiz", "outdoor sessions still follow the school's sun policy", "joints become lungs", "drugs replace shade"), "B", "Policy, not a body survey.", "Cloud does not switch the sun's damaging radiation off. Follow the school's outdoor sun policy. Do not compare skin colour in this quiz."),
        _SH_MCQ("difficult", "honest", "Fair sport includes", _mcq_opts("secret banned drugs", "following anti-doping and medical rules, not asking classmates what they take", "ignoring bleeding", "skipping water"), "B", "No personal drug disclosure in the app.", "Fair sport follows medical and anti-doping rules. This quiz does not ask classmates what they take, and it does not treat ignoring bleeding as fair."),
        _SH_MCQ("difficult", "a_label", "<p>Which letter is the muscle above the bone?</p>" + str(antagonistic_pair(title="A above")), _mcq_opts("B", "A", "neither", "a banned drug"), "B", "A is above.", "Match the letter to the pulling tissue drawn above the bone in the sketch, not the one below."),
        _SH_KEY("difficult", "skeleton_word", "Write the word for the body's framework of bones.", "skeleton", "The skeleton supports and protects.", "Name the body's framework of bones. Do not write the meeting-place word or the pulling-tissue word."),
        _SH_NUM("difficult", "rest", "A coach plans 3 rest days in a 7-day week. How many rest days is that?", 3, "Three rest days.", "The plan already states how many rest days are in this week. Enter that count, not 7 and not the number of training days."),
        _SH_ORD("difficult", "chain", "Order skeleton, joint, then antagonistic pair.", ["skeleton", "joint", "pair"], _BODY_BANK, "Framework, meeting point, opposite muscles.", "Framework of bones, then the meeting place, then the opposite-pull pair. Same chain as before, still skip slogans."),
        _SH_PICK("difficult", "protect_two", "Select the two health protections.", ["injury", "uv"], _SAFE_BANK, 2, "Injury and UV.", "Choose reducing some injury risk and reducing sun damage. Skip banned drugs and ignoring bleeding for this pick."),
        _SH_PICK("difficult", "drug_uv", "Select the two ideas about drugs and ignoring injury.", ["drug", "ignore"], _SAFE_BANK, 2, "Drugs can be unsafe or unfair; ignoring bleeding is wrong.", "Choose some drugs harming health or cheating, and ignoring bleeding being wrong. Those two ideas belong together here."),
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
