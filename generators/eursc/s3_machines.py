"""S3 Unit 3.1 Machines — 3.1.1–3.1.6."""
from generators.eursc.science_shared import (
    bind_eursc_topic,
    charge_pair,
    circuit_boxes,
    lever_boxes,
    magnet_poles,
    sankey_bars,
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


_FW_MCQ, _FW_NUM, _FW_KEY, _FW_ORD, _FW_PICK = _topic_bank("force_work_machines")
_EN_MCQ, _EN_NUM, _EN_KEY, _EN_ORD, _EN_PICK = _topic_bank("energy")
_ES_MCQ, _ES_NUM, _ES_KEY, _ES_ORD, _ES_PICK = _topic_bank("electrostatics")
_EC_MCQ, _EC_NUM, _EC_KEY, _EC_ORD, _EC_PICK = _topic_bank("electric_current")
_MG_MCQ, _MG_NUM, _MG_KEY, _MG_ORD, _MG_PICK = _topic_bank("magnetism")
_RB_MCQ, _RB_NUM, _RB_KEY, _RB_ORD, _RB_PICK = _topic_bank("robotics_project")

_LEVER_BANK = (
    {"id": "effort", "text": "Effort is the input force on the lever"},
    {"id": "fulcrum", "text": "The fulcrum is the pivot"},
    {"id": "load", "text": "The load is the output the machine moves"},
    {"id": "rank_arm", "text": "The quiz should store a private map of whose joints they are"},
)
_WORK_BANK = (
    {"id": "wfd", "text": "Work in this lesson is force times distance along the same line"},
    {"id": "joule", "text": "The unit of work used here is the joule"},
    {"id": "trade", "text": "A simple machine can trade a smaller force for a larger distance"},
    {"id": "power_claim", "text": "This lesson claims power calculations in watts"},
)
_FW_NOT_BANK = (
    {"id": "effort", "text": "Effort is the input force on the lever"},
    {"id": "wfd", "text": "Work in this lesson is force times distance along the same line"},
    {"id": "rank_arm", "text": "The quiz should store a private map of whose joints they are"},
    {"id": "power_claim", "text": "This lesson claims power calculations in watts"},
)

_FW_POOLS = {
    "foundational": [
        _FW_MCQ("foundational", "force_vec", "In this S3 model a force is", _mcq_opts("a food group", "a push or pull that can be drawn as a vector", "a stored joint file", "a class league"), "B", "Vector model of a push or pull.", "Look for a push or pull you could draw with an arrow, not a food group or a ranking."),
        _FW_MCQ("foundational", "machines", "Simple machines named here include", _mcq_opts("only a computer", "a lever, a pulley and a ramp", "a vaccination", "a mood survey"), "B", "Lever, pulley, ramp.", "Name the three everyday tools in this unit: the turning bar, the wheel-and-rope, and the slope."),
        _FW_MCQ("foundational", "fulcrum_idea", "The fulcrum of a lever is", _mcq_opts("a private diary", "the pivot the bar turns about", "a joule of time", "a ranking"), "B", "Pivot.", "Think of the point the bar turns about, not a diary or a ranking."),
        _FW_MCQ("foundational", "effort_letter", "<p>Which letter is the effort?</p>" + str(lever_boxes(title="Effort letter")), _mcq_opts("B", "A", "C", "a pupil handle"), "B", "A is the effort.", "On the labelled bar, find the input push, not the pivot and not the output."),
        _FW_MCQ("foundational", "no_power", "Power calculations in watts", _mcq_opts("are required in every item", "are not claimed in this lesson", "replace work", "store whose arms they are"), "B", "No power claim.", "This unit stays with W = Fd. It does not ask you to work out how fast that quantity is done."),
        _FW_MCQ("foundational", "alex", "Alex (fictional) uses a ramp to raise a box. A science line is", _mcq_opts("rank Alex's strength", "the ramp can trade a smaller force for a longer distance", "store a joint map", "skip the fulcrum idea"), "B", "Trade-off.", "A slope can make the push smaller if you travel farther up the slope."),
        _FW_KEY("foundational", "force_word", "Write the word for a push or pull in this lesson.", "force", "Force.", "One short word names a push or a pull in this model."),
        _FW_NUM("foundational", "w15", "A force of 5 N moves an object 3 m along the same line. Work in joules?", 15, "W = Fd = 5 × 3 = 15 J.", "Use W = Fd: multiply the 5 N by the 3 m along the same line."),
        _FW_ORD("foundational", "efl", "Order effort, then fulcrum, then load.", ["effort", "fulcrum", "load"], _LEVER_BANK, "Input, pivot, output.", "First the input push, then the pivot, then what the bar is moving."),
        _FW_PICK("foundational", "lever_ok", "Select effort and fulcrum.", ["effort", "fulcrum"], _LEVER_BANK, 2, "Two lever parts. No joint map.", "Choose the input push and the pivot. Skip anything about mapping someone's joints."),
    ],
    "intermediate": [
        _FW_MCQ("intermediate", "trade", "A force–distance trade-off means", _mcq_opts("force and distance must both shrink", "a smaller force can act over a larger distance", "work becomes a vaccine", "the quiz stores a body map"), "B", "Trade smaller force for larger distance.", "A smaller push can still do the job if it acts over a longer stretch."),
        _FW_MCQ("intermediate", "wfd", "Work in this lesson is", _mcq_opts("force divided by time", "force times distance along the same line", "a private score", "a colour"), "B", "W = Fd.", "Here it is not force divided by time. It is force multiplied by distance along one line."),
        _FW_MCQ("intermediate", "fulcrum_letter", "<p>Which letter is the fulcrum?</p>" + str(lever_boxes(title="Fulcrum letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is the fulcrum.", "On the labelled bar, find the pivot letter, not the input push and not the output."),
        _FW_MCQ("intermediate", "sam", "Sam (fictional) lifts a load with a long lever arm. A science reply is", _mcq_opts("publish Sam in a league", "a longer effort distance can reduce the effort force needed", "store Sam's joints", "claim a power in watts"), "B", "Trade-off.", "A longer stretch for the input can mean you need a smaller input push."),
        _FW_MCQ("intermediate", "body", "A body lever in this lesson is", _mcq_opts("a demand to map a pupil's joints live", "a teaching model using a fictional case, not a private map", "a stored medical file", "a class rank"), "B", "Fictional case.", "The body example is a teaching story. It is not a request to map your own joints."),
        _FW_MCQ("intermediate", "pulley", "A pulley in this S3 set is", _mcq_opts("a mood", "a simple machine that can change the direction of a force", "a prescription", "a league"), "B", "Simple machine.", "Think of a wheel-and-rope that can turn a pull around a corner."),
        _FW_KEY("intermediate", "work_word", "Write the word for force times distance along the same line.", "work", "Work.", "One short word names force multiplied by distance along the same line."),
        _FW_NUM("intermediate", "w12", "A force of 4 N moves an object 3 m along the same line. Work in joules?", 12, "4 × 3 = 12 J.", "Use W = Fd: multiply the 4 N by the 3 m along the same line."),
        _FW_ORD("intermediate", "w_trade", "Order the work idea, then the force–distance trade-off.", ["wfd", "trade"], _WORK_BANK, "Define work, then the trade-off.", "First the force-times-distance idea, then the smaller-push-for-longer-stretch idea."),
        _FW_PICK("intermediate", "work_ok", "Select work as Fd and the joule.", ["wfd", "joule"], _WORK_BANK, 2, "Two ideas. No power claim.", "Choose the force-times-distance idea and the unit of that quantity. Skip any watts claim."),
    ],
    "difficult": [
        _FW_MCQ("difficult", "load_letter", "<p>Which letter is the load?</p>" + str(lever_boxes(title="Load letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the load.", "On the labelled bar, find the output being moved, not the input and not the pivot."),
        _FW_MCQ("difficult", "same_line", "W = Fd in this lesson needs", _mcq_opts("a power in watts", "force and distance along the same line", "a joint diary", "a class vote"), "B", "Along the same line.", "W = Fd only when the push and the movement share the same line."),
        _FW_MCQ("difficult", "jordan", "Jordan (fictional) says a machine creates energy. A science reply is", _mcq_opts("agree and rank Jordan", "a machine can trade force and distance; it does not create energy", "store a map", "switch to watts"), "B", "Trade-off, not creation.", "A machine can swap a smaller push for a longer path. It does not make energy from nowhere."),
        _FW_MCQ("difficult", "limit", "A limit of this lesson is", _mcq_opts("that W = Fd is never used", "that power calculations are not claimed", "that levers do not exist", "that joints must be uploaded"), "B", "No power claim.", "This unit still uses W = Fd. What it does not claim is a later idea about how fast that quantity is done."),
        _FW_MCQ("difficult", "ramp", "A ramp used to raise a box", _mcq_opts("must store a private photo", "can increase the distance so the effort force can be smaller", "is a vaccination", "ranks classmates"), "B", "Longer distance, smaller force.", "A longer slope path can let you use a smaller push to raise the box."),
        _FW_MCQ("difficult", "misuse", "A misuse of the body-lever idea is", _mcq_opts("using a fictional case", "asking for a live map of a pupil's joints", "labelling effort on a bar", "stating W = Fd"), "B", "No live map.", "Using a made-up case is fine. Asking for a live map of a pupil's joints is not."),
        _FW_KEY("difficult", "joule_word", "Write the word for the unit of work used in this lesson.", "joule", "Joule.", "One short word names the unit of W = Fd used here."),
        _FW_NUM("difficult", "w16", "A force of 2 N moves an object 8 m along the same line. Work in joules?", 16, "2 × 8 = 16 J.", "Use W = Fd: multiply the 2 N by the 8 m along the same line."),
        _FW_ORD("difficult", "efl2", "Order fulcrum, then load.", ["fulcrum", "load"], _LEVER_BANK, "Pivot then output.", "First the pivot, then what the bar is moving."),
        _FW_PICK("difficult", "not_claim", "Select the two items that do not belong.", ["rank_arm", "power_claim"], _FW_NOT_BANK, 2, "No joint map; no power claim.", "Choose the joint-map demand and the watts-calculation claim. Those two do not belong."),
    ],
}

_FW_STANDARD = {
    "foundational": (
        'force_work_machines_foundational_mcq_alex',
        'force_work_machines_foundational_keyword_force_word',
        'force_work_machines_foundational_number_w15',
        'force_work_machines_foundational_order_efl',
        'force_work_machines_foundational_pick_lever_ok',
    ),
    "intermediate": (
        'force_work_machines_intermediate_mcq_body',
        'force_work_machines_intermediate_keyword_work_word',
        'force_work_machines_intermediate_number_w12',
        'force_work_machines_intermediate_order_w_trade',
        'force_work_machines_intermediate_pick_work_ok',
    ),
    "difficult": (
        'force_work_machines_difficult_mcq_jordan',
        'force_work_machines_difficult_keyword_joule_word',
        'force_work_machines_difficult_number_w16',
        'force_work_machines_difficult_order_efl2',
        'force_work_machines_difficult_pick_not_claim',
    ),
}
eursc_science_force_work_machines, eursc_science_force_work_machines_variants = bind_eursc_topic(
    'force_work_machines', _FW_POOLS, _FW_STANDARD
)

_FORM_BANK = (
    {"id": "kinetic", "text": "Kinetic energy is the energy of motion in this model"},
    {"id": "thermal", "text": "Thermal energy is a less useful form in many wasted-output stories"},
    {"id": "chem", "text": "Chemical energy is a store named for food and fuels here"},
    {"id": "diary", "text": "The quiz should store a private energy diary"},
)
_CONS_BANK = (
    {"id": "transform", "text": "Energy can be transformed from one form to another"},
    {"id": "transfer", "text": "Energy can be transferred from one store or place to another"},
    {"id": "conserve", "text": "Conservation means energy is not created or destroyed in this model"},
    {"id": "create", "text": "A machine can create energy from nothing"},
)

_EN_POOLS = {
    "foundational": [
        _EN_MCQ("foundational", "forms", "Energy forms named in this S3 model include", _mcq_opts("only a rumour", "kinetic, chemical and thermal examples", "a glasses file", "a class rank"), "B", "Named forms.", "Look for named stores such as motion, food-or-fuel, and a heat-style less-useful form, not a rumour."),
        _EN_MCQ("foundational", "transform", "An energy transformation in this lesson is", _mcq_opts("deleting energy", "changing energy from one form to another", "a private diary", "a vaccination"), "B", "Form change.", "It can change from one named form into another. It is not deleted."),
        _EN_MCQ("foundational", "input_letter", "<p>Which letter is the energy input?</p>" + str(sankey_bars(title="Input letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is the input.", "On the split diagram, find the incoming bar, not the useful split and not the wasted split."),
        _EN_MCQ("foundational", "waste", "Wasted energy in this lesson is", _mcq_opts("proof conservation is false", "energy transferred into a less useful form such as thermal", "a stored household bill", "a league"), "B", "Less useful form.", "What goes into a less useful form is still there. It is not proof that it vanished."),
        _EN_MCQ("foundational", "alex_en", "Alex (fictional) reads a public appliance table. A science use is", _mcq_opts("rank Alex's home", "compare public figures, not a private diary", "upload a bill", "skip conservation"), "B", "Public data.", "Use a public table of figures. Do not turn it into a diary of someone's home."),
        _EN_MCQ("foundational", "no_diary", "This quiz", _mcq_opts("stores a private energy diary", "does not store a private energy diary", "ranks homes", "claims energy is created"), "B", "No diary.", "This quiz does not collect a private log of how much a household uses."),
        _EN_KEY("foundational", "energy_word", "Write the word for the quantity that can be stored, transferred or transformed here.", "energy", "Energy.", "One short word names the quantity that can be stored, moved, or changed in form here."),
        _EN_NUM("foundational", "useful60", "Input 100 units; wasted 40 units. Useful output in the same units?", 60, "100 − 40 = 60.", "Start with 100 units in. Forty units are wasted. Subtract to find the useful leftover."),
        _EN_ORD("foundational", "forms_ord", "Order kinetic energy, then thermal energy.", ["kinetic", "thermal"], _FORM_BANK, "Motion then thermal.", "Put the motion store first, then the heat-style less-useful form."),
        _EN_PICK("foundational", "form_ok", "Select kinetic and chemical energy.", ["kinetic", "chem"], _FORM_BANK, 2, "Two forms. No diary.", "Choose the motion store and the food-or-fuel store. Skip a private diary."),
    ],
    "intermediate": [
        _EN_MCQ("intermediate", "transfer", "An energy transfer in this lesson is", _mcq_opts("a class vote", "energy moving from one store or place to another", "creating energy", "a joint map"), "B", "Place or store change.", "It can move from one store or place to another. That is not a class vote."),
        _EN_MCQ("intermediate", "useful_letter", "<p>Which letter is the useful output?</p>" + str(sankey_bars(title="Useful letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is useful.", "On the split diagram, find the useful outgoing bar, not the incoming bar and not the wasted part."),
        _EN_MCQ("intermediate", "conserve", "Conservation of energy in this model means", _mcq_opts("energy can appear from nowhere", "energy is not created or destroyed", "bills must be uploaded", "homes are ranked"), "B", "Not created or destroyed.", "In this model it does not appear from nowhere and does not vanish."),
        _EN_MCQ("intermediate", "sam_en", "Sam (fictional) says a wasted bar means energy vanished. A science reply is", _mcq_opts("agree", "the energy is still there as a less useful form", "store Sam's bill", "rank Sam"), "B", "Still there.", "A wasted bar is still there, just in a less useful form. It has not disappeared."),
        _EN_MCQ("intermediate", "source", "An energy source impact in this lesson is", _mcq_opts("a private confession", "a public environmental idea, not a household rank", "a glasses file", "a joke only"), "B", "Public impact idea.", "Impacts of sources are public environmental ideas, not a ranking of homes."),
        _EN_MCQ("intermediate", "food", "Food energy in this S3 model is", _mcq_opts("a demand to log meals here", "a chemical store example, not a private menu", "a magnet pole", "a circuit"), "B", "Example store.", "Food is an example of a chemical store. This quiz does not ask you to log meals."),
        _EN_KEY("intermediate", "conserve_word", "Write the word for the idea that energy is not created or destroyed in this model.", "conservation", "Conservation.", "One short word names the idea that it is not made or destroyed in this model."),
        _EN_NUM("intermediate", "waste25", "Input 80 units; useful 55 units. Wasted output in the same units?", 25, "80 − 55 = 25.", "Start with 80 units in. Fifty-five are useful. Subtract to find how many are wasted."),
        _EN_ORD("intermediate", "ttc", "Order transformation, then transfer, then conservation.", ["transform", "transfer", "conserve"], _CONS_BANK, "Change form, move, then conserve.", "First change of form, then moving from place to place, then the not-created-or-destroyed idea."),
        _EN_PICK("intermediate", "cons_ok", "Select transformation and conservation.", ["transform", "conserve"], _CONS_BANK, 2, "Two ideas. Not creation.", "Choose the form-change idea and the not-created-or-destroyed idea. Skip making it from nothing."),
    ],
    "difficult": [
        _EN_MCQ("difficult", "waste_letter", "<p>Which letter is the wasted output?</p>" + str(sankey_bars(title="Wasted letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is wasted.", "On the split diagram, find the less-useful outgoing bar, not the incoming bar and not the useful split."),
        _EN_MCQ("difficult", "sankey", "A Sankey-style split is used to", _mcq_opts("rank classmates", "show how an input splits into useful and wasted parts", "store bills", "claim energy is created"), "B", "Split of the input.", "The split diagram shows how one input divides into a useful part and a wasted part."),
        _EN_MCQ("difficult", "jordan_en", "Jordan (fictional) wants a league of whose home uses least energy. The lesson says", _mcq_opts("publish the league", "use public data; do not rank households here", "upload meters", "skip conservation"), "B", "No household rank.", "Public figures are fine. A league of whose home uses least is not this lesson."),
        _EN_MCQ("difficult", "both", "Transformation and transfer both", _mcq_opts("create energy", "keep conservation as the background model", "require a diary", "are magnets"), "B", "Conservation still holds.", "Changing form and moving place still sit under the idea that it is not created or destroyed."),
        _EN_MCQ("difficult", "limit_en", "A limit of this lesson is", _mcq_opts("that forms cannot be named", "that it does not collect private bills or replace a meter reading at home", "that Sankey bars are illegal", "that energy is created"), "B", "No private bills.", "This lesson does not harvest private bills or replace a meter reading at home."),
        _EN_MCQ("difficult", "misuse_en", "A misuse of the appliance table is", _mcq_opts("quoting a public figure", "demanding a live household diary in the quiz", "drawing a Sankey split", "naming thermal waste"), "B", "No live diary.", "Quoting a public figure is fine. Demanding a live household diary in the quiz is not."),
        _EN_KEY("difficult", "thermal_word", "Write the word for the less useful form often shown as wasted output here.", "thermal", "Thermal.", "One short word names the less useful form often shown as the wasted bar."),
        _EN_NUM("difficult", "in90", "Useful 70 units and wasted 20 units. Input in the same units if they add to the input?", 90, "70 + 20 = 90.", "Add the 70 useful units to the 20 wasted units. That sum is the input if they add up."),
        _EN_ORD("difficult", "tf2", "Order transfer, then conservation.", ["transfer", "conserve"], _CONS_BANK, "Move, then conserve.", "First moving from place to place, then the not-created-or-destroyed idea."),
        _EN_PICK("difficult", "not_en", "Select the two items that do not belong.", ["diary", "create"], _FORM_BANK[:1] + _CONS_BANK[2:] + _FORM_BANK[3:], 2, "No diary; no creation.", "Choose the private diary demand and the claim that a machine makes it from nothing."),
    ],
}

_EN_STANDARD = {
    "foundational": (
        'energy_foundational_mcq_alex_en',
        'energy_foundational_keyword_energy_word',
        'energy_foundational_number_useful60',
        'energy_foundational_order_forms_ord',
        'energy_foundational_pick_form_ok',
    ),
    "intermediate": (
        'energy_intermediate_mcq_conserve',
        'energy_intermediate_keyword_conserve_word',
        'energy_intermediate_number_waste25',
        'energy_intermediate_order_ttc',
        'energy_intermediate_pick_cons_ok',
    ),
    "difficult": (
        'energy_difficult_mcq_both',
        'energy_difficult_keyword_thermal_word',
        'energy_difficult_number_in90',
        'energy_difficult_order_tf2',
        'energy_difficult_pick_not_en',
    ),
}
eursc_science_energy, eursc_science_energy_variants = bind_eursc_topic('energy', _EN_POOLS, _EN_STANDARD)

_CHARGE_BANK = (
    {"id": "friction", "text": "Charging by friction can separate charge in this model"},
    {"id": "two", "text": "Two kinds of charge attract or repel"},
    {"id": "ground", "text": "Grounding can provide a path for charge to leave an object"},
    {"id": "shock_ask", "text": "The quiz should ask who has been shocked at home"},
)
_INDUCE_BANK = (
    {"id": "transfer", "text": "Charge can be transferred by contact"},
    {"id": "induce", "text": "Induction can rearrange charge without contact in this model"},
    {"id": "insulator", "text": "An insulator does not let charge flow easily"},
    {"id": "league", "text": "The quiz should rank whose spark is biggest"},
)

_ES_POOLS = {
    "foundational": [
        _ES_MCQ("foundational", "friction", "Charging by friction in this lesson is", _mcq_opts("a diet", "rubbing or contact that can separate charge", "a stored shock file", "a class rank"), "B", "Friction or contact.", "Rubbing or contact can separate charge. That is not a diet or a ranking."),
        _ES_MCQ("foundational", "two", "This S3 model uses how many kinds of charge that attract or repel?", _mcq_opts("one only ever", "two", "eighty", "zero"), "B", "Two kinds.", "This model uses a pair of kinds that attract or repel, not eighty kinds."),
        _ES_MCQ("foundational", "a_letter", "<p>Which letter is charge A?</p>" + str(charge_pair(title="Charge A letter")), _mcq_opts("B", "A", "neither", "a handle"), "B", "A is labelled A.", "On the pair diagram, find the label A, not B."),
        _ES_MCQ("foundational", "attract", "Opposite charges in this model", _mcq_opts("must be uploaded", "attract", "rank classmates", "are food"), "B", "Attract.", "Kinds that are opposite pull toward each other in this model."),
        _ES_MCQ("foundational", "alex_es", "Alex (fictional) rubs a balloon on a jumper in a demo. A science line is", _mcq_opts("ask who has been shocked", "charge can be separated by friction", "store a medical file", "skip safety"), "B", "Friction demo.", "Rubbing a balloon on a jumper is a demo of separating charge. Do not turn it into a shock survey."),
        _ES_MCQ("foundational", "no_shock", "This quiz", _mcq_opts("asks who has been shocked at home", "does not collect a shock story", "ranks sparks", "replaces a risk assessment"), "B", "No shock survey.", "This quiz does not collect stories of who has been shocked at home."),
        _ES_KEY("foundational", "charge_word", "Write the word for the two kinds that attract or repel in this lesson.", "charge", "Charge.", "One short word names the two kinds that attract or repel here."),
        _ES_NUM("foundational", "two_n", "How many kinds of charge are used in this S3 attract-or-repel model?", 2, "Two.", "Count how many kinds this attract-or-repel model uses. It is a small whole number."),
        _ES_ORD("foundational", "fr_two", "Order charging by friction, then two kinds of charge.", ["friction", "two"], _CHARGE_BANK, "How it starts, then two kinds.", "First how rubbing can start it, then the two kinds that attract or repel."),
        _ES_PICK("foundational", "ch_ok", "Select friction charging and two kinds of charge.", ["friction", "two"], _CHARGE_BANK, 2, "Two ideas. No shock survey.", "Choose rubbing-to-separate and the two-kinds idea. Skip a shock survey."),
    ],
    "intermediate": [
        _ES_MCQ("intermediate", "induce", "Induction in this lesson is", _mcq_opts("a vaccination", "rearranging charge without needing contact in this model", "a joint map", "a league"), "B", "Rearrange without contact.", "It can be rearranged even without touching, in this model."),
        _ES_MCQ("intermediate", "b_letter", "<p>Which letter is charge B?</p>" + str(charge_pair(title="Charge B letter")), _mcq_opts("A", "B", "a brand", "a menu"), "B", "B is labelled B.", "On the pair diagram, find the label B, not A."),
        _ES_MCQ("intermediate", "ground", "Grounding is", _mcq_opts("a class vote", "a path that can let charge leave an object", "a stored diary", "a food"), "B", "Path off the object.", "Think of a path that can let it leave an object."),
        _ES_MCQ("intermediate", "insulator", "An insulator", _mcq_opts("lets charge flow easily always", "does not let charge flow easily in this model", "ranks sparks", "is a magnet pole"), "B", "Charge does not flow easily.", "Think of a material that does not let it flow easily."),
        _ES_MCQ("intermediate", "sam_es", "Sam (fictional) stands on an insulator mat in a demo. A science point is", _mcq_opts("ask Sam's medical history", "the mat can reduce an unwanted path for charge", "rank Sam", "skip the teacher"), "B", "Insulator path.", "Standing on a mat that it does not cross easily can cut an unwanted path."),
        _ES_MCQ("intermediate", "atom", "A simple atomic link in this lesson is", _mcq_opts("that nuclei must be uploaded", "that electrons can move", "that charge is a diet", "that sparks are a league"), "B", "Electrons can move.", "A simple link is that tiny negative particles can move. Nuclei are not uploaded."),
        _ES_KEY("intermediate", "induction_word", "Write the word for rearranging charge without contact in this model.", "induction", "Induction.", "One short word names rearranging it without needing contact."),
        _ES_NUM("intermediate", "zero_shock", "How many live 'who has been shocked' items should this quiz ask? Enter 0.", 0, "Zero.", "This quiz should ask nobody about being shocked at home. Enter that count."),
        _ES_ORD("intermediate", "ti", "Order transfer by contact, then induction.", ["transfer", "induce"], _INDUCE_BANK, "Contact, then without contact.", "First it moving by touching, then rearranging without touching."),
        _ES_PICK("intermediate", "ind_ok", "Select induction and insulator.", ["induce", "insulator"], _INDUCE_BANK, 2, "Two ideas. No spark league.", "Choose rearranging without contact and the material it does not flow through easily."),
    ],
    "difficult": [
        _ES_MCQ("difficult", "like", "Like charges in this model", _mcq_opts("attract always", "repel", "must be photographed", "rank the class"), "B", "Repel.", "Kinds that are the same push each other apart in this model."),
        _ES_MCQ("difficult", "lightning", "Lightning in this lesson is", _mcq_opts("a stored clinical file", "a large discharge; follow teacher safety, not a shock survey", "a food", "a magnet only"), "B", "Discharge plus safety.", "Treat it as a large discharge and follow the teacher. It is not a shock survey."),
        _ES_MCQ("difficult", "jordan_es", "Jordan (fictional) wants a league of whose hair stands up most. The lesson says", _mcq_opts("publish the league", "use a demo; do not rank pupils", "store files", "skip grounding"), "B", "No league.", "A demo is fine. A league of whose hair stands up most is not."),
        _ES_MCQ("difficult", "both_es", "Transfer and induction both", _mcq_opts("require a shock diary", "are ways charge can be rearranged in this model", "are ramps", "are Sankey bars"), "B", "Rearrange charge.", "Touching and rearranging without touching are both ways it can be moved around."),
        _ES_MCQ("difficult", "safety_es", "Classroom electrostatics safety is", _mcq_opts("the app's stored medical file", "the teacher's risk assessment, not a home interrogation", "a class rank", "optional always"), "B", "Teacher rules.", "Classroom rules come from the teacher's risk assessment, not from this app storing medical files."),
        _ES_MCQ("difficult", "misuse_es", "A misuse of this lesson is", _mcq_opts("drawing two charges", "asking who has been shocked at home", "naming an insulator", "stating opposite charges attract"), "B", "No shock survey.", "Drawing two kinds is fine. Asking who has been shocked at home is not."),
        _ES_KEY("difficult", "insulator_word", "Write the word for a material that does not let charge flow easily here.", "insulator", "Insulator.", "One short word names a material that does not let it flow easily here."),
        _ES_NUM("difficult", "kinds2", "Attract and repel are modelled with how many kinds of charge?", 2, "Two.", "Attract and repel are modelled with a pair of kinds. How many is that pair?"),
        _ES_ORD("difficult", "gi", "Order grounding, then an insulator idea.", ["ground", "insulator"], _CHARGE_BANK[:3] + _INDUCE_BANK[2:3], "Path off, then material.", "First a path for it to leave, then a material it does not flow through easily."),
        _ES_PICK("difficult", "not_es", "Select the two items that do not belong.", ["shock_ask", "league"], _CHARGE_BANK[:1] + _CHARGE_BANK[3:] + _INDUCE_BANK[1:2] + _INDUCE_BANK[3:], 2, "No shock survey; no spark league.", "Choose the shock-survey demand and the spark-size league. Those two do not belong."),
    ],
}

_ES_STANDARD = {
    "foundational": (
        'electrostatics_foundational_mcq_a_letter',
        'electrostatics_foundational_keyword_charge_word',
        'electrostatics_foundational_number_two_n',
        'electrostatics_foundational_order_fr_two',
        'electrostatics_foundational_pick_ch_ok',
    ),
    "intermediate": (
        'electrostatics_intermediate_mcq_atom',
        'electrostatics_intermediate_keyword_induction_word',
        'electrostatics_intermediate_number_zero_shock',
        'electrostatics_intermediate_order_ti',
        'electrostatics_intermediate_pick_ind_ok',
    ),
    "difficult": (
        'electrostatics_difficult_mcq_both_es',
        'electrostatics_difficult_keyword_insulator_word',
        'electrostatics_difficult_number_kinds2',
        'electrostatics_difficult_order_gi',
        'electrostatics_difficult_pick_not_es',
    ),
}
eursc_science_electrostatics, eursc_science_electrostatics_variants = bind_eursc_topic(
    'electrostatics', _ES_POOLS, _ES_STANDARD
)

_PATH_BANK = (
    {"id": "loop", "text": "A complete circuit is a loop that allows current"},
    {"id": "series", "text": "A series circuit has one path"},
    {"id": "parallel", "text": "A parallel circuit has more than one path"},
    {"id": "vir", "text": "This lesson requires V = IR calculations"},
)
_SAFE_BANK = (
    {"id": "electron", "text": "Electrons can move in the teaching model of current"},
    {"id": "conductor", "text": "A conductor lets current pass more easily than an insulator"},
    {"id": "safety", "text": "Classroom electrical safety follows the teacher's risk assessment"},
    {"id": "home_inspect", "text": "The quiz should inspect whose home wiring it is"},
)

_EC_POOLS = {
    "foundational": [
        _EC_MCQ("foundational", "loop", "A complete circuit in this lesson is", _mcq_opts("a food group", "a loop that allows current", "a stored shock file", "a class rank"), "B", "A loop.", "The flow here needs a closed path. Look for a loop, not a food group."),
        _EC_MCQ("foundational", "series", "A series circuit has", _mcq_opts("no path", "one path", "eighty independent paths always", "a diet"), "B", "One path.", "In this model that circuit type has a single path, not dozens."),
        _EC_MCQ("foundational", "cell_letter", "<p>Which letter is the cell?</p>" + str(circuit_boxes(title="Cell letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is the cell.", "On the circuit boxes, find the cell, not the lamp and not the switch."),
        _EC_MCQ("foundational", "no_vir", "V = IR calculations", _mcq_opts("are required in every item", "are not claimed in this lesson", "replace safety", "store home wiring"), "B", "Qualitative only.", "This unit stays with path ideas. It does not claim a calculation homework with that formula."),
        _EC_MCQ("foundational", "alex_ec", "Alex (fictional) opens a switch and a lamp goes out. A science line is", _mcq_opts("rank Alex", "the loop is no longer complete", "inspect Alex's home", "compute V = IR"), "B", "Open switch breaks the loop.", "Opening a switch breaks the closed path, so the lamp goes out."),
        _EC_MCQ("foundational", "conductor", "A conductor in this model", _mcq_opts("never lets current pass", "lets current pass more easily than an insulator", "is a lever", "ranks pupils"), "B", "Easier path.", "Think of a material that lets the flow pass more easily than an insulator does."),
        _EC_KEY("foundational", "current_word", "Write the word for the flow in a complete circuit in this lesson.", "current", "Current.", "One short word names the flow in a complete circuit here."),
        _EC_NUM("foundational", "one_path", "A series circuit in this model has how many paths?", 1, "One.", "A one-path circuit type in this model has a single path. Enter that count."),
        _EC_ORD("foundational", "loop_ser", "Order a complete loop, then a series path.", ["loop", "series"], _PATH_BANK, "Loop, then one path.", "First a complete loop, then the one-path circuit type."),
        _EC_PICK("foundational", "path_ok", "Select complete loop and series.", ["loop", "series"], _PATH_BANK, 2, "Two ideas. No V = IR claim.", "Choose the complete-loop idea and the one-path circuit type. Skip any calculation-formula claim."),
    ],
    "intermediate": [
        _EC_MCQ("intermediate", "parallel", "A parallel circuit has", _mcq_opts("zero paths", "more than one path", "only a magnet", "a private diary"), "B", "More than one path.", "That circuit type has more than one path, not zero."),
        _EC_MCQ("intermediate", "lamp_letter", "<p>Which letter is the lamp?</p>" + str(circuit_boxes(title="Lamp letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is the lamp.", "On the circuit boxes, find the lamp, not the cell and not the switch."),
        _EC_MCQ("intermediate", "conventional", "Conventional current (the arrow convention) in this teaching model is", _mcq_opts("a demand for a home photo", "a direction convention, distinct from electron flow", "a joule of mass", "a class league"), "B", "Convention vs electrons.", "The arrow convention is a teaching direction. It is not the same label as electron flow."),
        _EC_MCQ("intermediate", "effects", "Effects of current named here include", _mcq_opts("only a rumour", "heating, lighting and a magnetic effect", "a joint map", "a menu"), "B", "Heat, light, magnetic.", "The flow here can heat, light, and have a magnetic effect. Not a rumour."),
        _EC_MCQ("intermediate", "sam_ec", "Sam (fictional) adds a second lamp on its own branch. That fits", _mcq_opts("a series-only rule always", "a parallel path idea", "V = IR as a required calculation", "a home inspection"), "B", "Parallel.", "A second lamp on its own branch fits the more-than-one-path idea."),
        _EC_MCQ("intermediate", "meter", "A meter in this lesson is used", _mcq_opts("to store whose home it is", "qualitatively; this lesson does not claim V = IR calculations", "to rank sparks", "to skip safety"), "B", "Qualitative meters.", "Meters here are qualitative. This lesson does not claim that formula as homework."),
        _EC_KEY("intermediate", "series_word", "Write the word for a circuit with one path.", "series", "Series.", "One short word names a circuit with one path."),
        _EC_NUM("intermediate", "zero_vir", "How many V = IR calculation items does this lesson claim? Enter 0.", 0, "Zero.", "This lesson claims none of those formula-calculation items. Enter that count."),
        _EC_ORD("intermediate", "sp", "Order series, then parallel.", ["series", "parallel"], _PATH_BANK, "One path, then more than one.", "First the one-path type, then the more-than-one-path type."),
        _EC_PICK("intermediate", "par_ok", "Select series and parallel.", ["series", "parallel"], _PATH_BANK, 2, "Two path ideas.", "Choose the one-path type and the more-than-one-path type."),
    ],
    "difficult": [
        _EC_MCQ("difficult", "switch_letter", "<p>Which letter is the switch?</p>" + str(circuit_boxes(title="Switch letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the switch.", "On the circuit boxes, find the switch, not the cell and not the lamp."),
        _EC_MCQ("difficult", "electrons", "Electron flow in this teaching model", _mcq_opts("is the same label as conventional current always", "is distinguished from the conventional-current arrow", "must be a home confession", "ranks classmates"), "B", "Two descriptions.", "Electron flow and the conventional arrow are two descriptions, not the same label."),
        _EC_MCQ("difficult", "jordan_ec", "Jordan (fictional) wants to test mains sockets at home for the quiz. The lesson says", _mcq_opts("go ahead and upload photos", "do not inspect home wiring here; follow classroom safety", "compute V = IR first", "rank Jordan"), "B", "No home inspection.", "Do not inspect home wiring for this quiz. Follow classroom safety."),
        _EC_MCQ("difficult", "safety_ec", "Electrical safety in class is", _mcq_opts("optional if the lamp is small", "the teacher's risk assessment, not this app's inspection", "a league", "a Sankey bar"), "B", "Teacher rules.", "Electrical safety in class is the teacher's risk assessment, not this app inspecting homes."),
        _EC_MCQ("difficult", "qual", "Current and voltage in this lesson are", _mcq_opts("always calculated with V = IR", "treated qualitatively; V = IR is not claimed", "a diet", "a joint map"), "B", "Qualitative.", "Current and voltage here are treated as ideas, not as a required formula calculation."),
        _EC_MCQ("difficult", "misuse_ec", "A misuse of this lesson is", _mcq_opts("drawing a series loop", "requiring V = IR calculations as if they were in the S3 claim", "naming a conductor", "opening a switch in a model"), "B", "No V = IR claim.", "Drawing a one-path loop is fine. Treating that formula as an S3 claim is not."),
        _EC_KEY("difficult", "parallel_word", "Write the word for a circuit with more than one path.", "parallel", "Parallel.", "One short word names a circuit with more than one path."),
        _EC_NUM("difficult", "paths2", "A simple parallel model here is described as more than one path. Enter 2 for that teaching count of path-types named (series and parallel).", 2, "Two path-types.", "The lesson names two path-types. Enter that teaching count."),
        _EC_ORD("difficult", "cs", "Order conductor, then classroom safety.", ["conductor", "safety"], _SAFE_BANK, "Material, then safety.", "First the material that lets the flow pass more easily, then classroom safety."),
        _EC_PICK("difficult", "not_ec", "Select the two items that do not belong.", ["vir", "home_inspect"], _PATH_BANK[:1] + _PATH_BANK[3:] + _SAFE_BANK[1:2] + _SAFE_BANK[3:], 2, "No V = IR claim; no home inspection.", "Choose the formula-calculation claim and the home-wiring inspection. Those two do not belong."),
    ],
}

_EC_STANDARD = {
    "foundational": (
        'electric_current_foundational_mcq_alex_ec',
        'electric_current_foundational_keyword_current_word',
        'electric_current_foundational_number_one_path',
        'electric_current_foundational_order_loop_ser',
        'electric_current_foundational_pick_path_ok',
    ),
    "intermediate": (
        'electric_current_intermediate_mcq_conventional',
        'electric_current_intermediate_keyword_series_word',
        'electric_current_intermediate_number_zero_vir',
        'electric_current_intermediate_order_sp',
        'electric_current_intermediate_pick_par_ok',
    ),
    "difficult": (
        'electric_current_difficult_mcq_electrons',
        'electric_current_difficult_keyword_parallel_word',
        'electric_current_difficult_number_paths2',
        'electric_current_difficult_order_cs',
        'electric_current_difficult_pick_not_ec',
    ),
}
eursc_science_electric_current, eursc_science_electric_current_variants = bind_eursc_topic(
    'electric_current', _EC_POOLS, _EC_STANDARD
)

_POLE_BANK = (
    {"id": "poles", "text": "Magnets have poles that attract or repel"},
    {"id": "field", "text": "A field region is where a magnetic effect can be shown"},
    {"id": "electro", "text": "An electromagnet is a current-made magnet that can be switched"},
    {"id": "rank_mag", "text": "The quiz should rank whose magnet is strongest"},
)
_EARTH_BANK = (
    {"id": "material", "text": "Some materials are magnetic in this S3 model and some are not"},
    {"id": "earth", "text": "Earth can be modelled as having a magnetic field a compass uses"},
    {"id": "taxis", "text": "Magnetotaxis is a public animal example, not a pupil ranking"},
    {"id": "super", "text": "The quiz should rank which pupil has a magnetic superpower"},
)

_MG_POOLS = {
    "foundational": [
        _MG_MCQ("foundational", "poles", "Magnetic poles in this lesson", _mcq_opts("are a food", "attract or repel", "must be a home file", "rank classmates"), "B", "Attract or repel.", "Ends of a magnet attract or repel. They are not a food."),
        _MG_MCQ("foundational", "n_letter", "<p>Which letter is pole A?</p>" + str(magnet_poles(title="Pole A letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is pole A.", "On the pole diagram, find pole A, not pole B and not the field region."),
        _MG_MCQ("foundational", "material", "Materials in this S3 model", _mcq_opts("are all magnets always", "can be magnetic or not", "are diets", "are private scores"), "B", "Classify.", "Some materials are magnetic in this model and some are not. Not all objects are magnets."),
        _MG_MCQ("foundational", "electro", "An electromagnet is", _mcq_opts("a stored ranking", "a current-made magnet that can be switched", "a joule of time", "a shock survey"), "B", "Current-made, switchable.", "Think of a magnet made with current that you can switch on and off."),
        _MG_MCQ("foundational", "alex_mg", "Alex (fictional) brings a compass on a field trip. A science line is", _mcq_opts("rank Alex", "a compass can line up with Earth's field in this model", "store a superpower", "skip poles"), "B", "Earth and compass.", "A compass can line up with Earth's field in this model. Do not rank Alex."),
        _MG_MCQ("foundational", "no_rank", "This quiz", _mcq_opts("ranks whose magnet is strongest", "does not rank whose magnet is strongest", "inspects home wiring", "claims V = IR"), "B", "No strength league.", "This quiz does not keep a league of whose magnet is strongest."),
        _MG_KEY("foundational", "magnet_word", "Write the word for an object with poles that attract or repel here.", "magnet", "Magnet.", "One short word names an object with ends that attract or repel here."),
        _MG_NUM("foundational", "two_poles", "How many poles are named on a simple bar magnet in this lesson?", 2, "Two.", "Count the named ends on a simple bar magnet. It is a small whole number."),
        _MG_ORD("foundational", "pf", "Order poles, then the field region.", ["poles", "field"], _POLE_BANK, "Poles, then field.", "First the attracting-or-repelling ends, then the region where the effect can be shown."),
        _MG_PICK("foundational", "pole_ok", "Select poles and electromagnet.", ["poles", "electro"], _POLE_BANK, 2, "Two ideas. No strength rank.", "Choose the attracting-or-repelling ends and the current-made switchable magnet."),
    ],
    "intermediate": [
        _MG_MCQ("intermediate", "s_letter", "<p>Which letter is pole B?</p>" + str(magnet_poles(title="Pole B letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is pole B.", "On the pole diagram, find pole B, not pole A and not the field region."),
        _MG_MCQ("intermediate", "field", "A magnetic field in this schematic is", _mcq_opts("a menu", "a region where a magnetic effect can be shown", "a private diary", "a vaccination"), "B", "Region of effect.", "Think of a region around a magnet where the effect can be shown, not a menu."),
        _MG_MCQ("intermediate", "magnetise", "Magnetisation in this lesson is", _mcq_opts("a class vote", "aligning or making a magnet in this model", "a shock file", "a ramp"), "B", "Make or align.", "Think of aligning or making a magnet in this model, not a class vote."),
        _MG_MCQ("intermediate", "earth", "Earth in this lesson is modelled as", _mcq_opts("having no field", "having a magnetic field a compass can use", "a household rank", "a V = IR claim"), "B", "Earth field.", "Earth is modelled as having a field a compass can use."),
        _MG_MCQ("intermediate", "sam_mg", "Sam (fictional) switches a coil off and the paperclips drop. That fits", _mcq_opts("a permanent-only rule always", "an electromagnet that can be switched", "a superpower league", "a home inspection"), "B", "Switchable.", "Switching the coil off so paperclips drop fits a magnet you can switch."),
        _MG_MCQ("intermediate", "taxis", "Magnetotaxis here is", _mcq_opts("a pupil ranking", "a public animal example, not a superpower quiz", "a stored clinical file", "a diet"), "B", "Public example.", "It is a public animal example. It is not a ranking of pupils."),
        _MG_KEY("intermediate", "pole_word", "Write the word for one end of a magnet that attracts or repels here.", "pole", "Pole.", "One short word names one end of a magnet that attracts or repels here."),
        _MG_NUM("intermediate", "zero_rank", "How many 'whose magnet is strongest' ranks should this quiz keep? Enter 0.", 0, "Zero.", "This quiz should keep none of those strength leagues. Enter that count."),
        _MG_ORD("intermediate", "et", "Order Earth's field idea, then magnetotaxis.", ["earth", "taxis"], _EARTH_BANK, "Earth, then the animal example.", "First Earth's field idea, then the public animal example."),
        _MG_PICK("intermediate", "earth_ok", "Select magnetic materials and Earth's field.", ["material", "earth"], _EARTH_BANK, 2, "Two ideas.", "Choose magnetic-or-not materials and Earth's field idea."),
    ],
    "difficult": [
        _MG_MCQ("difficult", "c_letter", "<p>Which letter is the field region?</p>" + str(magnet_poles(title="Field letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the field region.", "On the diagram, find the field region, not pole A and not pole B."),
        _MG_MCQ("difficult", "like_p", "Like poles in this model", _mcq_opts("attract always", "repel", "must be uploaded", "rank the class"), "B", "Repel.", "Ends of the same kind push each other apart in this model."),
        _MG_MCQ("difficult", "jordan_mg", "Jordan (fictional) wants a league of who is most like a magnetotactic microbe. The lesson says", _mcq_opts("publish the league", "study the public model; do not rank pupils as animals", "store files", "skip fields"), "B", "No ranking.", "Study the public animal model. Do not rank pupils as if they were those organisms."),
        _MG_MCQ("difficult", "coil", "A coil with current can", _mcq_opts("only be a diet", "act as an electromagnet in this model", "replace classroom safety", "inspect homes"), "B", "Electromagnet.", "A coil with current can act as a switchable magnet in this model."),
        _MG_MCQ("difficult", "limit_mg", "A limit of this lesson is", _mcq_opts("that poles cannot be named", "that it does not store a magnet-strength league", "that compasses are banned", "that Earth has no model field"), "B", "No league.", "This lesson does not store a league of magnet strengths."),
        _MG_MCQ("difficult", "misuse_mg", "A misuse of magnetotaxis teaching is", _mcq_opts("using a public animal example", "ranking which pupil has a superpower", "drawing a field region", "naming two poles"), "B", "No superpower rank.", "A public animal example is fine. Ranking which pupil has a superpower is not."),
        _MG_KEY("difficult", "electro_word", "Write the word for a current-made magnet that can be switched.", "electromagnet", "Electromagnet.", "One short word names a current-made magnet that can be switched."),
        _MG_NUM("difficult", "switch1", "An electromagnet can be switched. Enter 1 if that is the lesson model.", 1, "One: it can be switched.", "If the lesson model is that it can be switched, enter 1."),
        _MG_ORD("difficult", "fe", "Order the field region, then the electromagnet.", ["field", "electro"], _POLE_BANK, "Field, then current-made magnet.", "First the region of effect, then the current-made switchable magnet."),
        _MG_PICK("difficult", "not_mg", "Select the two items that do not belong.", ["rank_mag", "super"], _POLE_BANK[:1] + _POLE_BANK[3:] + _EARTH_BANK[1:2] + _EARTH_BANK[3:], 2, "No strength rank; no superpower rank.", "Choose the magnet-strength league and the superpower ranking. Those two do not belong."),
    ],
}

_MG_STANDARD = {
    "foundational": (
        'magnetism_foundational_mcq_alex_mg',
        'magnetism_foundational_keyword_magnet_word',
        'magnetism_foundational_number_two_poles',
        'magnetism_foundational_order_pf',
        'magnetism_foundational_pick_pole_ok',
    ),
    "intermediate": (
        'magnetism_intermediate_mcq_earth',
        'magnetism_intermediate_keyword_pole_word',
        'magnetism_intermediate_number_zero_rank',
        'magnetism_intermediate_order_et',
        'magnetism_intermediate_pick_earth_ok',
    ),
    "difficult": (
        'magnetism_difficult_mcq_c_letter',
        'magnetism_difficult_keyword_electro_word',
        'magnetism_difficult_number_switch1',
        'magnetism_difficult_order_fe',
        'magnetism_difficult_pick_not_mg',
    ),
}
eursc_science_magnetism, eursc_science_magnetism_variants = bind_eursc_topic('magnetism', _MG_POOLS, _MG_STANDARD)

_REQ_BANK = (
    {"id": "require", "text": "Write requirements another group could test"},
    {"id": "machine", "text": "Choose simple machines that match the requirements"},
    {"id": "iterate", "text": "Test, then iterate the design"},
    {"id": "league_bot", "text": "The quiz should rank whose robot is best as a stored league"},
)
_BUILD_BANK = (
    {"id": "electro_plan", "text": "Plan electromagnetism or electronics only with teacher-approved parts"},
    {"id": "sense", "text": "A classroom program can be modelled as sense, then decide, then act"},
    {"id": "present", "text": "Present evidence; the physical robot is not auto-graded here"},
    {"id": "upload", "text": "Pupils must upload private home-workshop photos to this app"},
)

_RB_POOLS = {
    "foundational": [
        _RB_MCQ("foundational", "require", "The first project phase is to", _mcq_opts("hide the method", "write requirements another group could test", "rank robots in a stored league", "skip safety"), "B", "Requirements.", "Start by writing needs another group could actually test."),
        _RB_MCQ("foundational", "machine", "Simple machines in the project", _mcq_opts("must be a secret", "should match the written requirements", "replace the teacher", "inspect homes"), "B", "Match requirements.", "Choose levers, pulleys or ramps that match those written needs."),
        _RB_MCQ("foundational", "not_auto", "The physical robot in this app is", _mcq_opts("fully auto-graded as a product", "not auto-graded; class uses a rubric", "a diet", "a shock survey"), "B", "Rubric in class.", "This app does not mark the physical robot as a finished product. Class uses a rubric."),
        _RB_MCQ("foundational", "alex_rb", "Alex (fictional) writes 'move 20 cm on a table'. That is", _mcq_opts("a private confession", "a testable requirement", "a stored league", "a V = IR claim"), "B", "Testable.", "'Move 20 cm on a table' is something another group could test. That is the point."),
        _RB_MCQ("foundational", "ibl", "Classroom build time", _mcq_opts("is replaced by this web page", "still needs the class, parts and the teacher's risk assessment", "uploads home photos here", "ranks pupils"), "B", "Page does not replace practical.", "This web page does not replace class time, parts, or the teacher's risk assessment."),
        _RB_MCQ("foundational", "no_league", "This quiz", _mcq_opts("stores whose robot is best", "does not store a robot league", "inspects home wiring", "skips requirements"), "B", "No league.", "This quiz does not store whose robot is best."),
        _RB_KEY("foundational", "requirement_word", "Write the word for a testable need the robot should meet.", "requirement", "Requirement.", "One short word names a testable need the robot should meet."),
        _RB_NUM("foundational", "zero_grade", "How many physical robots does this app auto-grade as a finished product? Enter 0.", 0, "Zero.", "This app auto-grades none of the physical robots as a finished product. Enter that count."),
        _RB_ORD("foundational", "rm", "Order requirements, then choosing machines.", ["require", "machine"], _REQ_BANK, "Need, then mechanism.", "First the testable needs, then choosing machines that match them."),
        _RB_PICK("foundational", "req_ok", "Select requirements and iteration.", ["require", "iterate"], _REQ_BANK, 2, "Two project actions. No league.", "Choose writing testable needs and changing the design after a test. Skip a stored league."),
    ],
    "intermediate": [
        _RB_MCQ("intermediate", "parts", "Electronics or electromagnets in the project", _mcq_opts("may be any home mains part", "need teacher-approved parts and a risk assessment", "replace the rubric", "must be photographed at home for the app"), "B", "Teacher-approved parts.", "Electronics or electromagnets need teacher-approved parts, not any home mains part."),
        _RB_MCQ("intermediate", "sense", "Sense–decide–act in this lesson is", _mcq_opts("a private code upload", "a classroom model of a simple program", "a joint map", "a household rank"), "B", "Classroom model.", "Think of a classroom model: sense, then decide, then act. Not a private code upload."),
        _RB_MCQ("intermediate", "iterate", "Iteration means", _mcq_opts("never testing", "changing the design after a test", "storing a league", "skipping safety"), "B", "Test then change.", "After a test, you change the design. That is not 'never testing'."),
        _RB_MCQ("intermediate", "sam_rb", "Sam (fictional) finds the robot misses the line. A project next step is", _mcq_opts("publish a league", "record the miss and iterate the method", "upload home photos", "hide the data"), "B", "Record and iterate.", "Record that the robot missed the line, then change the method. Do not hide the data."),
        _RB_MCQ("intermediate", "present", "Presentation in this project is", _mcq_opts("a stored popularity score", "evidence another group could follow, judged with a class rubric", "a shock survey", "a V = IR test"), "B", "Evidence plus rubric.", "Show evidence another group could follow. A class rubric judges it, not a popularity score."),
        _RB_MCQ("intermediate", "safety_rb", "Build safety is", _mcq_opts("optional", "the teacher's risk assessment; this page does not replace it", "a private medical file", "a magnet league"), "B", "Teacher rules.", "Build safety is the teacher's risk assessment. This page does not replace it."),
        _RB_KEY("intermediate", "iterate_word", "Write the word for changing the design after a test.", "iterate", "Iterate.", "One short word names changing the design after a test."),
        _RB_NUM("intermediate", "phases5", "This project names how many classroom phases in the lesson?", 5, "Five phases.", "Count the named classroom phases in this project lesson. Enter that whole number."),
        _RB_ORD("intermediate", "si", "Order the sense–decide–act idea, then presenting evidence.", ["sense", "present"], _BUILD_BANK, "Program model, then present.", "First the sense-then-decide-then-act idea, then presenting evidence."),
        _RB_PICK("intermediate", "build_ok", "Select teacher-approved parts and presenting evidence.", ["electro_plan", "present"], _BUILD_BANK, 2, "Two project ideas. No photo upload.", "Choose teacher-approved parts and presenting evidence. Skip a home-photo upload."),
    ],
    "difficult": [
        _RB_MCQ("difficult", "jordan_rb", "Jordan (fictional) wants the app to crown a winner. The lesson says", _mcq_opts("store the league", "use a class rubric; do not store a robot ranking here", "upload homes", "skip tests"), "B", "No stored league.", "Use a class rubric. This app should not store a winner league."),
        _RB_MCQ("difficult", "code", "Classroom programming here is", _mcq_opts("a demand to upload a private repository", "a sense–decide–act model with teacher tools", "a diet", "a shock survey"), "B", "Classroom model.", "Programming here is a classroom sense-decide-act model with teacher tools, not a private repo upload."),
        _RB_MCQ("difficult", "fail", "A failed test in the project is", _mcq_opts("proof to hide the method", "evidence for iteration, not a stored ranking", "a medical file", "a reason to skip safety"), "B", "Iterate.", "A missed test is evidence to change the design, not a reason to hide the method."),
        _RB_MCQ("difficult", "limit_rb", "A limit of this page is", _mcq_opts("that requirements cannot be written", "that it does not replace the practical build or auto-grade the robot", "that machines cannot be named", "that teachers have no rubric"), "B", "Support page only.", "This page supports the project. It does not replace the practical build or auto-grade the robot."),
        _RB_MCQ("difficult", "misuse_rb", "A misuse of the project is", _mcq_opts("writing a testable requirement", "forcing private home-workshop photos into this app", "iterating after a miss", "using a class rubric"), "B", "No private photo harvest.", "Writing a testable need is fine. Forcing private home-workshop photos into this app is not."),
        _RB_MCQ("difficult", "roles", "Collaboration in the build", _mcq_opts("must be a secret", "has shared roles the teacher can see in class, not a hidden league here", "uploads medical files", "replaces the risk assessment"), "B", "Shared roles in class.", "Shared roles the teacher can see in class are fine. A hidden league here is not."),
        _RB_KEY("difficult", "safety_word", "Write the word for following the teacher's risk rules in the build.", "safety", "Safety.", "One short word names following the teacher's risk rules in the build."),
        _RB_NUM("difficult", "zero_upload", "How many private home-workshop photo uploads does this quiz require? Enter 0.", 0, "Zero.", "This quiz requires none of those private home-workshop photo uploads. Enter that count."),
        _RB_ORD("difficult", "mi", "Order choosing machines, then iteration.", ["machine", "iterate"], _REQ_BANK, "Mechanism, then iterate.", "First choosing machines that match the needs, then changing the design after a test."),
        _RB_PICK("difficult", "not_rb", "Select the two items that do not belong.", ["league_bot", "upload"], _REQ_BANK[:1] + _REQ_BANK[3:] + _BUILD_BANK[1:2] + _BUILD_BANK[3:], 2, "No stored league; no photo harvest.", "Choose the stored robot league and the home-photo harvest. Those two do not belong."),
    ],
}

_RB_STANDARD = {
    "foundational": (
        'robotics_project_foundational_mcq_alex_rb',
        'robotics_project_foundational_keyword_requirement_word',
        'robotics_project_foundational_number_zero_grade',
        'robotics_project_foundational_order_rm',
        'robotics_project_foundational_pick_req_ok',
    ),
    "intermediate": (
        'robotics_project_intermediate_mcq_iterate',
        'robotics_project_intermediate_keyword_iterate_word',
        'robotics_project_intermediate_number_phases5',
        'robotics_project_intermediate_order_si',
        'robotics_project_intermediate_pick_build_ok',
    ),
    "difficult": (
        'robotics_project_difficult_mcq_code',
        'robotics_project_difficult_keyword_safety_word',
        'robotics_project_difficult_number_zero_upload',
        'robotics_project_difficult_order_mi',
        'robotics_project_difficult_pick_not_rb',
    ),
}
eursc_science_robotics_project, eursc_science_robotics_project_variants = bind_eursc_topic(
    'robotics_project', _RB_POOLS, _RB_STANDARD
)




