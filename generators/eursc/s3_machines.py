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
    def mcq(difficulty, suffix, question, options, answer, solution):
        def _fn():
            return make_problem(
                question,
                solution,
                "Use S3 machine ideas from the lesson. Scenarios are fictional.",
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
                "Check the machine idea. This quiz does not grade a physical robot.",
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
            difficulty, suffix, "number", question, {"type": "number", "value": value}, solution
        )

    def keyword(difficulty, suffix, question, value, solution):
        return typed(
            difficulty, suffix, "keyword", question, {"type": "keyword", "value": value}, solution
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
        _FW_MCQ("foundational", "force_vec", "In this S3 model a force is", _mcq_opts("a food group", "a push or pull that can be drawn as a vector", "a stored joint file", "a class league"), "B", "Vector model of a push or pull."),
        _FW_MCQ("foundational", "machines", "Simple machines named here include", _mcq_opts("only a computer", "a lever, a pulley and a ramp", "a vaccination", "a mood survey"), "B", "Lever, pulley, ramp."),
        _FW_MCQ("foundational", "fulcrum_idea", "The fulcrum of a lever is", _mcq_opts("a private diary", "the pivot the bar turns about", "a joule of time", "a ranking"), "B", "Pivot."),
        _FW_MCQ("foundational", "effort_letter", "<p>Which letter is the effort?</p>" + str(lever_boxes(title="Effort letter")), _mcq_opts("B", "A", "C", "a pupil handle"), "B", "A is the effort."),
        _FW_MCQ("foundational", "no_power", "Power calculations in watts", _mcq_opts("are required in every item", "are not claimed in this lesson", "replace work", "store whose arms they are"), "B", "No power claim."),
        _FW_MCQ("foundational", "alex", "Alex (fictional) uses a ramp to raise a box. A science line is", _mcq_opts("rank Alex's strength", "the ramp can trade a smaller force for a longer distance", "store a joint map", "skip the fulcrum idea"), "B", "Trade-off."),
        _FW_KEY("foundational", "force_word", "Write the word for a push or pull in this lesson.", "force", "Force."),
        _FW_NUM("foundational", "w15", "A force of 5 N moves an object 3 m along the same line. Work in joules?", 15, "W = Fd = 5 × 3 = 15 J."),
        _FW_ORD("foundational", "efl", "Order effort, then fulcrum, then load.", ["effort", "fulcrum", "load"], _LEVER_BANK, "Input, pivot, output."),
        _FW_PICK("foundational", "lever_ok", "Select effort and fulcrum.", ["effort", "fulcrum"], _LEVER_BANK, 2, "Two lever parts. No joint map."),
    ],
    "intermediate": [
        _FW_MCQ("intermediate", "trade", "A force–distance trade-off means", _mcq_opts("force and distance must both shrink", "a smaller force can act over a larger distance", "work becomes a vaccine", "the quiz stores a body map"), "B", "Trade smaller force for larger distance."),
        _FW_MCQ("intermediate", "wfd", "Work in this lesson is", _mcq_opts("force divided by time", "force times distance along the same line", "a private score", "a colour"), "B", "W = Fd."),
        _FW_MCQ("intermediate", "fulcrum_letter", "<p>Which letter is the fulcrum?</p>" + str(lever_boxes(title="Fulcrum letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is the fulcrum."),
        _FW_MCQ("intermediate", "sam", "Sam (fictional) lifts a load with a long lever arm. A science reply is", _mcq_opts("publish Sam in a league", "a longer effort distance can reduce the effort force needed", "store Sam's joints", "claim a power in watts"), "B", "Trade-off."),
        _FW_MCQ("intermediate", "body", "A body lever in this lesson is", _mcq_opts("a demand to map a pupil's joints live", "a teaching model using a fictional case, not a private map", "a stored medical file", "a class rank"), "B", "Fictional case."),
        _FW_MCQ("intermediate", "pulley", "A pulley in this S3 set is", _mcq_opts("a mood", "a simple machine that can change the direction of a force", "a prescription", "a league"), "B", "Simple machine."),
        _FW_KEY("intermediate", "work_word", "Write the word for force times distance along the same line.", "work", "Work."),
        _FW_NUM("intermediate", "w12", "A force of 4 N moves an object 3 m along the same line. Work in joules?", 12, "4 × 3 = 12 J."),
        _FW_ORD("intermediate", "w_trade", "Order the work idea, then the force–distance trade-off.", ["wfd", "trade"], _WORK_BANK, "Define work, then the trade-off."),
        _FW_PICK("intermediate", "work_ok", "Select work as Fd and the joule.", ["wfd", "joule"], _WORK_BANK, 2, "Two ideas. No power claim."),
    ],
    "difficult": [
        _FW_MCQ("difficult", "load_letter", "<p>Which letter is the load?</p>" + str(lever_boxes(title="Load letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the load."),
        _FW_MCQ("difficult", "same_line", "W = Fd in this lesson needs", _mcq_opts("a power in watts", "force and distance along the same line", "a joint diary", "a class vote"), "B", "Along the same line."),
        _FW_MCQ("difficult", "jordan", "Jordan (fictional) says a machine creates energy. A science reply is", _mcq_opts("agree and rank Jordan", "a machine can trade force and distance; it does not create energy", "store a map", "switch to watts"), "B", "Trade-off, not creation."),
        _FW_MCQ("difficult", "limit", "A limit of this lesson is", _mcq_opts("that W = Fd is never used", "that power calculations are not claimed", "that levers do not exist", "that joints must be uploaded"), "B", "No power claim."),
        _FW_MCQ("difficult", "ramp", "A ramp used to raise a box", _mcq_opts("must store a private photo", "can increase the distance so the effort force can be smaller", "is a vaccination", "ranks classmates"), "B", "Longer distance, smaller force."),
        _FW_MCQ("difficult", "misuse", "A misuse of the body-lever idea is", _mcq_opts("using a fictional case", "asking for a live map of a pupil's joints", "labelling effort on a bar", "stating W = Fd"), "B", "No live map."),
        _FW_KEY("difficult", "joule_word", "Write the word for the unit of work used in this lesson.", "joule", "Joule."),
        _FW_NUM("difficult", "w16", "A force of 2 N moves an object 8 m along the same line. Work in joules?", 16, "2 × 8 = 16 J."),
        _FW_ORD("difficult", "efl2", "Order fulcrum, then load.", ["fulcrum", "load"], _LEVER_BANK, "Pivot then output."),
        _FW_PICK("difficult", "not_claim", "Select the two items that do not belong.", ["rank_arm", "power_claim"], _FW_NOT_BANK, 2, "No joint map; no power claim."),
    ],
}

eursc_science_force_work_machines, eursc_science_force_work_machines_variants = bind_eursc_topic(
    "force_work_machines", _FW_POOLS
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
        _EN_MCQ("foundational", "forms", "Energy forms named in this S3 model include", _mcq_opts("only a rumour", "kinetic, chemical and thermal examples", "a glasses file", "a class rank"), "B", "Named forms."),
        _EN_MCQ("foundational", "transform", "An energy transformation in this lesson is", _mcq_opts("deleting energy", "changing energy from one form to another", "a private diary", "a vaccination"), "B", "Form change."),
        _EN_MCQ("foundational", "input_letter", "<p>Which letter is the energy input?</p>" + str(sankey_bars(title="Input letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is the input."),
        _EN_MCQ("foundational", "waste", "Wasted energy in this lesson is", _mcq_opts("proof conservation is false", "energy transferred into a less useful form such as thermal", "a stored household bill", "a league"), "B", "Less useful form."),
        _EN_MCQ("foundational", "alex_en", "Alex (fictional) reads a public appliance table. A science use is", _mcq_opts("rank Alex's home", "compare public figures, not a private diary", "upload a bill", "skip conservation"), "B", "Public data."),
        _EN_MCQ("foundational", "no_diary", "This quiz", _mcq_opts("stores a private energy diary", "does not store a private energy diary", "ranks homes", "claims energy is created"), "B", "No diary."),
        _EN_KEY("foundational", "energy_word", "Write the word for the quantity that can be stored, transferred or transformed here.", "energy", "Energy."),
        _EN_NUM("foundational", "useful60", "Input 100 units; wasted 40 units. Useful output in the same units?", 60, "100 − 40 = 60."),
        _EN_ORD("foundational", "forms_ord", "Order kinetic energy, then thermal energy.", ["kinetic", "thermal"], _FORM_BANK, "Motion then thermal."),
        _EN_PICK("foundational", "form_ok", "Select kinetic and chemical energy.", ["kinetic", "chem"], _FORM_BANK, 2, "Two forms. No diary."),
    ],
    "intermediate": [
        _EN_MCQ("intermediate", "transfer", "An energy transfer in this lesson is", _mcq_opts("a class vote", "energy moving from one store or place to another", "creating energy", "a joint map"), "B", "Place or store change."),
        _EN_MCQ("intermediate", "useful_letter", "<p>Which letter is the useful output?</p>" + str(sankey_bars(title="Useful letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is useful."),
        _EN_MCQ("intermediate", "conserve", "Conservation of energy in this model means", _mcq_opts("energy can appear from nowhere", "energy is not created or destroyed", "bills must be uploaded", "homes are ranked"), "B", "Not created or destroyed."),
        _EN_MCQ("intermediate", "sam_en", "Sam (fictional) says a wasted bar means energy vanished. A science reply is", _mcq_opts("agree", "the energy is still there as a less useful form", "store Sam's bill", "rank Sam"), "B", "Still there."),
        _EN_MCQ("intermediate", "source", "An energy source impact in this lesson is", _mcq_opts("a private confession", "a public environmental idea, not a household rank", "a glasses file", "a joke only"), "B", "Public impact idea."),
        _EN_MCQ("intermediate", "food", "Food energy in this S3 model is", _mcq_opts("a demand to log meals here", "a chemical store example, not a private menu", "a magnet pole", "a circuit"), "B", "Example store."),
        _EN_KEY("intermediate", "conserve_word", "Write the word for the idea that energy is not created or destroyed in this model.", "conservation", "Conservation."),
        _EN_NUM("intermediate", "waste25", "Input 80 units; useful 55 units. Wasted output in the same units?", 25, "80 − 55 = 25."),
        _EN_ORD("intermediate", "ttc", "Order transformation, then transfer, then conservation.", ["transform", "transfer", "conserve"], _CONS_BANK, "Change form, move, then conserve."),
        _EN_PICK("intermediate", "cons_ok", "Select transformation and conservation.", ["transform", "conserve"], _CONS_BANK, 2, "Two ideas. Not creation."),
    ],
    "difficult": [
        _EN_MCQ("difficult", "waste_letter", "<p>Which letter is the wasted output?</p>" + str(sankey_bars(title="Wasted letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is wasted."),
        _EN_MCQ("difficult", "sankey", "A Sankey-style split is used to", _mcq_opts("rank classmates", "show how an input splits into useful and wasted parts", "store bills", "claim energy is created"), "B", "Split of the input."),
        _EN_MCQ("difficult", "jordan_en", "Jordan (fictional) wants a league of whose home uses least energy. The lesson says", _mcq_opts("publish the league", "use public data; do not rank households here", "upload meters", "skip conservation"), "B", "No household rank."),
        _EN_MCQ("difficult", "both", "Transformation and transfer both", _mcq_opts("create energy", "keep conservation as the background model", "require a diary", "are magnets"), "B", "Conservation still holds."),
        _EN_MCQ("difficult", "limit_en", "A limit of this lesson is", _mcq_opts("that forms cannot be named", "that it does not collect private bills or replace a meter reading at home", "that Sankey bars are illegal", "that energy is created"), "B", "No private bills."),
        _EN_MCQ("difficult", "misuse_en", "A misuse of the appliance table is", _mcq_opts("quoting a public figure", "demanding a live household diary in the quiz", "drawing a Sankey split", "naming thermal waste"), "B", "No live diary."),
        _EN_KEY("difficult", "thermal_word", "Write the word for the less useful form often shown as wasted output here.", "thermal", "Thermal."),
        _EN_NUM("difficult", "in90", "Useful 70 units and wasted 20 units. Input in the same units if they add to the input?", 90, "70 + 20 = 90."),
        _EN_ORD("difficult", "tf2", "Order transfer, then conservation.", ["transfer", "conserve"], _CONS_BANK, "Move, then conserve."),
        _EN_PICK("difficult", "not_en", "Select the two items that do not belong.", ["diary", "create"], _FORM_BANK[:1] + _CONS_BANK[2:] + _FORM_BANK[3:], 2, "No diary; no creation."),
    ],
}

eursc_science_energy, eursc_science_energy_variants = bind_eursc_topic("energy", _EN_POOLS)

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
        _ES_MCQ("foundational", "friction", "Charging by friction in this lesson is", _mcq_opts("a diet", "rubbing or contact that can separate charge", "a stored shock file", "a class rank"), "B", "Friction or contact."),
        _ES_MCQ("foundational", "two", "This S3 model uses how many kinds of charge that attract or repel?", _mcq_opts("one only ever", "two", "eighty", "zero"), "B", "Two kinds."),
        _ES_MCQ("foundational", "a_letter", "<p>Which letter is charge A?</p>" + str(charge_pair(title="Charge A letter")), _mcq_opts("B", "A", "neither", "a handle"), "B", "A is labelled A."),
        _ES_MCQ("foundational", "attract", "Opposite charges in this model", _mcq_opts("must be uploaded", "attract", "rank classmates", "are food"), "B", "Attract."),
        _ES_MCQ("foundational", "alex_es", "Alex (fictional) rubs a balloon on a jumper in a demo. A science line is", _mcq_opts("ask who has been shocked", "charge can be separated by friction", "store a medical file", "skip safety"), "B", "Friction demo."),
        _ES_MCQ("foundational", "no_shock", "This quiz", _mcq_opts("asks who has been shocked at home", "does not collect a shock story", "ranks sparks", "replaces a risk assessment"), "B", "No shock survey."),
        _ES_KEY("foundational", "charge_word", "Write the word for the two kinds that attract or repel in this lesson.", "charge", "Charge."),
        _ES_NUM("foundational", "two_n", "How many kinds of charge are used in this S3 attract-or-repel model?", 2, "Two."),
        _ES_ORD("foundational", "fr_two", "Order charging by friction, then two kinds of charge.", ["friction", "two"], _CHARGE_BANK, "How it starts, then two kinds."),
        _ES_PICK("foundational", "ch_ok", "Select friction charging and two kinds of charge.", ["friction", "two"], _CHARGE_BANK, 2, "Two ideas. No shock survey."),
    ],
    "intermediate": [
        _ES_MCQ("intermediate", "induce", "Induction in this lesson is", _mcq_opts("a vaccination", "rearranging charge without needing contact in this model", "a joint map", "a league"), "B", "Rearrange without contact."),
        _ES_MCQ("intermediate", "b_letter", "<p>Which letter is charge B?</p>" + str(charge_pair(title="Charge B letter")), _mcq_opts("A", "B", "a brand", "a menu"), "B", "B is labelled B."),
        _ES_MCQ("intermediate", "ground", "Grounding is", _mcq_opts("a class vote", "a path that can let charge leave an object", "a stored diary", "a food"), "B", "Path off the object."),
        _ES_MCQ("intermediate", "insulator", "An insulator", _mcq_opts("lets charge flow easily always", "does not let charge flow easily in this model", "ranks sparks", "is a magnet pole"), "B", "Charge does not flow easily."),
        _ES_MCQ("intermediate", "sam_es", "Sam (fictional) stands on an insulator mat in a demo. A science point is", _mcq_opts("ask Sam's medical history", "the mat can reduce an unwanted path for charge", "rank Sam", "skip the teacher"), "B", "Insulator path."),
        _ES_MCQ("intermediate", "atom", "A simple atomic link in this lesson is", _mcq_opts("that nuclei must be uploaded", "that electrons can move", "that charge is a diet", "that sparks are a league"), "B", "Electrons can move."),
        _ES_KEY("intermediate", "induction_word", "Write the word for rearranging charge without contact in this model.", "induction", "Induction."),
        _ES_NUM("intermediate", "zero_shock", "How many live 'who has been shocked' items should this quiz ask? Enter 0.", 0, "Zero."),
        _ES_ORD("intermediate", "ti", "Order transfer by contact, then induction.", ["transfer", "induce"], _INDUCE_BANK, "Contact, then without contact."),
        _ES_PICK("intermediate", "ind_ok", "Select induction and insulator.", ["induce", "insulator"], _INDUCE_BANK, 2, "Two ideas. No spark league."),
    ],
    "difficult": [
        _ES_MCQ("difficult", "like", "Like charges in this model", _mcq_opts("attract always", "repel", "must be photographed", "rank the class"), "B", "Repel."),
        _ES_MCQ("difficult", "lightning", "Lightning in this lesson is", _mcq_opts("a stored clinical file", "a large discharge; follow teacher safety, not a shock survey", "a food", "a magnet only"), "B", "Discharge plus safety."),
        _ES_MCQ("difficult", "jordan_es", "Jordan (fictional) wants a league of whose hair stands up most. The lesson says", _mcq_opts("publish the league", "use a demo; do not rank pupils", "store files", "skip grounding"), "B", "No league."),
        _ES_MCQ("difficult", "both_es", "Transfer and induction both", _mcq_opts("require a shock diary", "are ways charge can be rearranged in this model", "are ramps", "are Sankey bars"), "B", "Rearrange charge."),
        _ES_MCQ("difficult", "safety_es", "Classroom electrostatics safety is", _mcq_opts("the app's stored medical file", "the teacher's risk assessment, not a home interrogation", "a class rank", "optional always"), "B", "Teacher rules."),
        _ES_MCQ("difficult", "misuse_es", "A misuse of this lesson is", _mcq_opts("drawing two charges", "asking who has been shocked at home", "naming an insulator", "stating opposite charges attract"), "B", "No shock survey."),
        _ES_KEY("difficult", "insulator_word", "Write the word for a material that does not let charge flow easily here.", "insulator", "Insulator."),
        _ES_NUM("difficult", "kinds2", "Attract and repel are modelled with how many kinds of charge?", 2, "Two."),
        _ES_ORD("difficult", "gi", "Order grounding, then an insulator idea.", ["ground", "insulator"], _CHARGE_BANK[:3] + _INDUCE_BANK[2:3], "Path off, then material."),
        _ES_PICK("difficult", "not_es", "Select the two items that do not belong.", ["shock_ask", "league"], _CHARGE_BANK[:1] + _CHARGE_BANK[3:] + _INDUCE_BANK[1:2] + _INDUCE_BANK[3:], 2, "No shock survey; no spark league."),
    ],
}

eursc_science_electrostatics, eursc_science_electrostatics_variants = bind_eursc_topic(
    "electrostatics", _ES_POOLS
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
        _EC_MCQ("foundational", "loop", "A complete circuit in this lesson is", _mcq_opts("a food group", "a loop that allows current", "a stored shock file", "a class rank"), "B", "A loop."),
        _EC_MCQ("foundational", "series", "A series circuit has", _mcq_opts("no path", "one path", "eighty independent paths always", "a diet"), "B", "One path."),
        _EC_MCQ("foundational", "cell_letter", "<p>Which letter is the cell?</p>" + str(circuit_boxes(title="Cell letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is the cell."),
        _EC_MCQ("foundational", "no_vir", "V = IR calculations", _mcq_opts("are required in every item", "are not claimed in this lesson", "replace safety", "store home wiring"), "B", "Qualitative only."),
        _EC_MCQ("foundational", "alex_ec", "Alex (fictional) opens a switch and a lamp goes out. A science line is", _mcq_opts("rank Alex", "the loop is no longer complete", "inspect Alex's home", "compute V = IR"), "B", "Open switch breaks the loop."),
        _EC_MCQ("foundational", "conductor", "A conductor in this model", _mcq_opts("never lets current pass", "lets current pass more easily than an insulator", "is a lever", "ranks pupils"), "B", "Easier path."),
        _EC_KEY("foundational", "current_word", "Write the word for the flow in a complete circuit in this lesson.", "current", "Current."),
        _EC_NUM("foundational", "one_path", "A series circuit in this model has how many paths?", 1, "One."),
        _EC_ORD("foundational", "loop_ser", "Order a complete loop, then a series path.", ["loop", "series"], _PATH_BANK, "Loop, then one path."),
        _EC_PICK("foundational", "path_ok", "Select complete loop and series.", ["loop", "series"], _PATH_BANK, 2, "Two ideas. No V = IR claim."),
    ],
    "intermediate": [
        _EC_MCQ("intermediate", "parallel", "A parallel circuit has", _mcq_opts("zero paths", "more than one path", "only a magnet", "a private diary"), "B", "More than one path."),
        _EC_MCQ("intermediate", "lamp_letter", "<p>Which letter is the lamp?</p>" + str(circuit_boxes(title="Lamp letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is the lamp."),
        _EC_MCQ("intermediate", "conventional", "Conventional current (the arrow convention) in this teaching model is", _mcq_opts("a demand for a home photo", "a direction convention, distinct from electron flow", "a joule of mass", "a class league"), "B", "Convention vs electrons."),
        _EC_MCQ("intermediate", "effects", "Effects of current named here include", _mcq_opts("only a rumour", "heating, lighting and a magnetic effect", "a joint map", "a menu"), "B", "Heat, light, magnetic."),
        _EC_MCQ("intermediate", "sam_ec", "Sam (fictional) adds a second lamp on its own branch. That fits", _mcq_opts("a series-only rule always", "a parallel path idea", "V = IR as a required calculation", "a home inspection"), "B", "Parallel."),
        _EC_MCQ("intermediate", "meter", "A meter in this lesson is used", _mcq_opts("to store whose home it is", "qualitatively; this lesson does not claim V = IR calculations", "to rank sparks", "to skip safety"), "B", "Qualitative meters."),
        _EC_KEY("intermediate", "series_word", "Write the word for a circuit with one path.", "series", "Series."),
        _EC_NUM("intermediate", "zero_vir", "How many V = IR calculation items does this lesson claim? Enter 0.", 0, "Zero."),
        _EC_ORD("intermediate", "sp", "Order series, then parallel.", ["series", "parallel"], _PATH_BANK, "One path, then more than one."),
        _EC_PICK("intermediate", "par_ok", "Select series and parallel.", ["series", "parallel"], _PATH_BANK, 2, "Two path ideas."),
    ],
    "difficult": [
        _EC_MCQ("difficult", "switch_letter", "<p>Which letter is the switch?</p>" + str(circuit_boxes(title="Switch letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the switch."),
        _EC_MCQ("difficult", "electrons", "Electron flow in this teaching model", _mcq_opts("is the same label as conventional current always", "is distinguished from the conventional-current arrow", "must be a home confession", "ranks classmates"), "B", "Two descriptions."),
        _EC_MCQ("difficult", "jordan_ec", "Jordan (fictional) wants to test mains sockets at home for the quiz. The lesson says", _mcq_opts("go ahead and upload photos", "do not inspect home wiring here; follow classroom safety", "compute V = IR first", "rank Jordan"), "B", "No home inspection."),
        _EC_MCQ("difficult", "safety_ec", "Electrical safety in class is", _mcq_opts("optional if the lamp is small", "the teacher's risk assessment, not this app's inspection", "a league", "a Sankey bar"), "B", "Teacher rules."),
        _EC_MCQ("difficult", "qual", "Current and voltage in this lesson are", _mcq_opts("always calculated with V = IR", "treated qualitatively; V = IR is not claimed", "a diet", "a joint map"), "B", "Qualitative."),
        _EC_MCQ("difficult", "misuse_ec", "A misuse of this lesson is", _mcq_opts("drawing a series loop", "requiring V = IR calculations as if they were in the S3 claim", "naming a conductor", "opening a switch in a model"), "B", "No V = IR claim."),
        _EC_KEY("difficult", "parallel_word", "Write the word for a circuit with more than one path.", "parallel", "Parallel."),
        _EC_NUM("difficult", "paths2", "A simple parallel model here is described as more than one path. Enter 2 for that teaching count of path-types named (series and parallel).", 2, "Two path-types."),
        _EC_ORD("difficult", "cs", "Order conductor, then classroom safety.", ["conductor", "safety"], _SAFE_BANK, "Material, then safety."),
        _EC_PICK("difficult", "not_ec", "Select the two items that do not belong.", ["vir", "home_inspect"], _PATH_BANK[:1] + _PATH_BANK[3:] + _SAFE_BANK[1:2] + _SAFE_BANK[3:], 2, "No V = IR claim; no home inspection."),
    ],
}

eursc_science_electric_current, eursc_science_electric_current_variants = bind_eursc_topic(
    "electric_current", _EC_POOLS
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
        _MG_MCQ("foundational", "poles", "Magnetic poles in this lesson", _mcq_opts("are a food", "attract or repel", "must be a home file", "rank classmates"), "B", "Attract or repel."),
        _MG_MCQ("foundational", "n_letter", "<p>Which letter is pole A?</p>" + str(magnet_poles(title="Pole A letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is pole A."),
        _MG_MCQ("foundational", "material", "Materials in this S3 model", _mcq_opts("are all magnets always", "can be magnetic or not", "are diets", "are private scores"), "B", "Classify."),
        _MG_MCQ("foundational", "electro", "An electromagnet is", _mcq_opts("a stored ranking", "a current-made magnet that can be switched", "a joule of time", "a shock survey"), "B", "Current-made, switchable."),
        _MG_MCQ("foundational", "alex_mg", "Alex (fictional) brings a compass on a field trip. A science line is", _mcq_opts("rank Alex", "a compass can line up with Earth's field in this model", "store a superpower", "skip poles"), "B", "Earth and compass."),
        _MG_MCQ("foundational", "no_rank", "This quiz", _mcq_opts("ranks whose magnet is strongest", "does not rank whose magnet is strongest", "inspects home wiring", "claims V = IR"), "B", "No strength league."),
        _MG_KEY("foundational", "magnet_word", "Write the word for an object with poles that attract or repel here.", "magnet", "Magnet."),
        _MG_NUM("foundational", "two_poles", "How many poles are named on a simple bar magnet in this lesson?", 2, "Two."),
        _MG_ORD("foundational", "pf", "Order poles, then the field region.", ["poles", "field"], _POLE_BANK, "Poles, then field."),
        _MG_PICK("foundational", "pole_ok", "Select poles and electromagnet.", ["poles", "electro"], _POLE_BANK, 2, "Two ideas. No strength rank."),
    ],
    "intermediate": [
        _MG_MCQ("intermediate", "s_letter", "<p>Which letter is pole B?</p>" + str(magnet_poles(title="Pole B letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is pole B."),
        _MG_MCQ("intermediate", "field", "A magnetic field in this schematic is", _mcq_opts("a menu", "a region where a magnetic effect can be shown", "a private diary", "a vaccination"), "B", "Region of effect."),
        _MG_MCQ("intermediate", "magnetise", "Magnetisation in this lesson is", _mcq_opts("a class vote", "aligning or making a magnet in this model", "a shock file", "a ramp"), "B", "Make or align."),
        _MG_MCQ("intermediate", "earth", "Earth in this lesson is modelled as", _mcq_opts("having no field", "having a magnetic field a compass can use", "a household rank", "a V = IR claim"), "B", "Earth field."),
        _MG_MCQ("intermediate", "sam_mg", "Sam (fictional) switches a coil off and the paperclips drop. That fits", _mcq_opts("a permanent-only rule always", "an electromagnet that can be switched", "a superpower league", "a home inspection"), "B", "Switchable."),
        _MG_MCQ("intermediate", "taxis", "Magnetotaxis here is", _mcq_opts("a pupil ranking", "a public animal example, not a superpower quiz", "a stored clinical file", "a diet"), "B", "Public example."),
        _MG_KEY("intermediate", "pole_word", "Write the word for one end of a magnet that attracts or repels here.", "pole", "Pole."),
        _MG_NUM("intermediate", "zero_rank", "How many 'whose magnet is strongest' ranks should this quiz keep? Enter 0.", 0, "Zero."),
        _MG_ORD("intermediate", "et", "Order Earth's field idea, then magnetotaxis.", ["earth", "taxis"], _EARTH_BANK, "Earth, then the animal example."),
        _MG_PICK("intermediate", "earth_ok", "Select magnetic materials and Earth's field.", ["material", "earth"], _EARTH_BANK, 2, "Two ideas."),
    ],
    "difficult": [
        _MG_MCQ("difficult", "c_letter", "<p>Which letter is the field region?</p>" + str(magnet_poles(title="Field letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the field region."),
        _MG_MCQ("difficult", "like_p", "Like poles in this model", _mcq_opts("attract always", "repel", "must be uploaded", "rank the class"), "B", "Repel."),
        _MG_MCQ("difficult", "jordan_mg", "Jordan (fictional) wants a league of who is most like a magnetotactic microbe. The lesson says", _mcq_opts("publish the league", "study the public model; do not rank pupils as animals", "store files", "skip fields"), "B", "No ranking."),
        _MG_MCQ("difficult", "coil", "A coil with current can", _mcq_opts("only be a diet", "act as an electromagnet in this model", "replace classroom safety", "inspect homes"), "B", "Electromagnet."),
        _MG_MCQ("difficult", "limit_mg", "A limit of this lesson is", _mcq_opts("that poles cannot be named", "that it does not store a magnet-strength league", "that compasses are banned", "that Earth has no model field"), "B", "No league."),
        _MG_MCQ("difficult", "misuse_mg", "A misuse of magnetotaxis teaching is", _mcq_opts("using a public animal example", "ranking which pupil has a superpower", "drawing a field region", "naming two poles"), "B", "No superpower rank."),
        _MG_KEY("difficult", "electro_word", "Write the word for a current-made magnet that can be switched.", "electromagnet", "Electromagnet."),
        _MG_NUM("difficult", "switch1", "An electromagnet can be switched. Enter 1 if that is the lesson model.", 1, "One: it can be switched."),
        _MG_ORD("difficult", "fe", "Order the field region, then the electromagnet.", ["field", "electro"], _POLE_BANK, "Field, then current-made magnet."),
        _MG_PICK("difficult", "not_mg", "Select the two items that do not belong.", ["rank_mag", "super"], _POLE_BANK[:1] + _POLE_BANK[3:] + _EARTH_BANK[1:2] + _EARTH_BANK[3:], 2, "No strength rank; no superpower rank."),
    ],
}

eursc_science_magnetism, eursc_science_magnetism_variants = bind_eursc_topic("magnetism", _MG_POOLS)

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
        _RB_MCQ("foundational", "require", "The first project phase is to", _mcq_opts("hide the method", "write requirements another group could test", "rank robots in a stored league", "skip safety"), "B", "Requirements."),
        _RB_MCQ("foundational", "machine", "Simple machines in the project", _mcq_opts("must be a secret", "should match the written requirements", "replace the teacher", "inspect homes"), "B", "Match requirements."),
        _RB_MCQ("foundational", "not_auto", "The physical robot in this app is", _mcq_opts("fully auto-graded as a product", "not auto-graded; class uses a rubric", "a diet", "a shock survey"), "B", "Rubric in class."),
        _RB_MCQ("foundational", "alex_rb", "Alex (fictional) writes 'move 20 cm on a table'. That is", _mcq_opts("a private confession", "a testable requirement", "a stored league", "a V = IR claim"), "B", "Testable."),
        _RB_MCQ("foundational", "ibl", "Classroom build time", _mcq_opts("is replaced by this web page", "still needs the class, parts and the teacher's risk assessment", "uploads home photos here", "ranks pupils"), "B", "Page does not replace practical."),
        _RB_MCQ("foundational", "no_league", "This quiz", _mcq_opts("stores whose robot is best", "does not store a robot league", "inspects home wiring", "skips requirements"), "B", "No league."),
        _RB_KEY("foundational", "requirement_word", "Write the word for a testable need the robot should meet.", "requirement", "Requirement."),
        _RB_NUM("foundational", "zero_grade", "How many physical robots does this app auto-grade as a finished product? Enter 0.", 0, "Zero."),
        _RB_ORD("foundational", "rm", "Order requirements, then choosing machines.", ["require", "machine"], _REQ_BANK, "Need, then mechanism."),
        _RB_PICK("foundational", "req_ok", "Select requirements and iteration.", ["require", "iterate"], _REQ_BANK, 2, "Two project actions. No league."),
    ],
    "intermediate": [
        _RB_MCQ("intermediate", "parts", "Electronics or electromagnets in the project", _mcq_opts("may be any home mains part", "need teacher-approved parts and a risk assessment", "replace the rubric", "must be photographed at home for the app"), "B", "Teacher-approved parts."),
        _RB_MCQ("intermediate", "sense", "Sense–decide–act in this lesson is", _mcq_opts("a private code upload", "a classroom model of a simple program", "a joint map", "a household rank"), "B", "Classroom model."),
        _RB_MCQ("intermediate", "iterate", "Iteration means", _mcq_opts("never testing", "changing the design after a test", "storing a league", "skipping safety"), "B", "Test then change."),
        _RB_MCQ("intermediate", "sam_rb", "Sam (fictional) finds the robot misses the line. A project next step is", _mcq_opts("publish a league", "record the miss and iterate the method", "upload home photos", "hide the data"), "B", "Record and iterate."),
        _RB_MCQ("intermediate", "present", "Presentation in this project is", _mcq_opts("a stored popularity score", "evidence another group could follow, judged with a class rubric", "a shock survey", "a V = IR test"), "B", "Evidence plus rubric."),
        _RB_MCQ("intermediate", "safety_rb", "Build safety is", _mcq_opts("optional", "the teacher's risk assessment; this page does not replace it", "a private medical file", "a magnet league"), "B", "Teacher rules."),
        _RB_KEY("intermediate", "iterate_word", "Write the word for changing the design after a test.", "iterate", "Iterate."),
        _RB_NUM("intermediate", "phases5", "This project names how many classroom phases in the lesson?", 5, "Five phases."),
        _RB_ORD("intermediate", "si", "Order the sense–decide–act idea, then presenting evidence.", ["sense", "present"], _BUILD_BANK, "Program model, then present."),
        _RB_PICK("intermediate", "build_ok", "Select teacher-approved parts and presenting evidence.", ["electro_plan", "present"], _BUILD_BANK, 2, "Two project ideas. No photo upload."),
    ],
    "difficult": [
        _RB_MCQ("difficult", "jordan_rb", "Jordan (fictional) wants the app to crown a winner. The lesson says", _mcq_opts("store the league", "use a class rubric; do not store a robot ranking here", "upload homes", "skip tests"), "B", "No stored league."),
        _RB_MCQ("difficult", "code", "Classroom programming here is", _mcq_opts("a demand to upload a private repository", "a sense–decide–act model with teacher tools", "a diet", "a shock survey"), "B", "Classroom model."),
        _RB_MCQ("difficult", "fail", "A failed test in the project is", _mcq_opts("proof to hide the method", "evidence for iteration, not a stored ranking", "a medical file", "a reason to skip safety"), "B", "Iterate."),
        _RB_MCQ("difficult", "limit_rb", "A limit of this page is", _mcq_opts("that requirements cannot be written", "that it does not replace the practical build or auto-grade the robot", "that machines cannot be named", "that teachers have no rubric"), "B", "Support page only."),
        _RB_MCQ("difficult", "misuse_rb", "A misuse of the project is", _mcq_opts("writing a testable requirement", "forcing private home-workshop photos into this app", "iterating after a miss", "using a class rubric"), "B", "No private photo harvest."),
        _RB_MCQ("difficult", "roles", "Collaboration in the build", _mcq_opts("must be a secret", "has shared roles the teacher can see in class, not a hidden league here", "uploads medical files", "replaces the risk assessment"), "B", "Shared roles in class."),
        _RB_KEY("difficult", "safety_word", "Write the word for following the teacher's risk rules in the build.", "safety", "Safety."),
        _RB_NUM("difficult", "zero_upload", "How many private home-workshop photo uploads does this quiz require? Enter 0.", 0, "Zero."),
        _RB_ORD("difficult", "mi", "Order choosing machines, then iteration.", ["machine", "iterate"], _REQ_BANK, "Mechanism, then iterate."),
        _RB_PICK("difficult", "not_rb", "Select the two items that do not belong.", ["league_bot", "upload"], _REQ_BANK[:1] + _REQ_BANK[3:] + _BUILD_BANK[1:2] + _BUILD_BANK[3:], 2, "No stored league; no photo harvest."),
    ],
}

eursc_science_robotics_project, eursc_science_robotics_project_variants = bind_eursc_topic(
    "robotics_project", _RB_POOLS
)




