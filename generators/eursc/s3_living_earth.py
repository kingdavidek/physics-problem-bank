"""S3 Unit 3.2 Living Earth — 3.2.1–3.2.5."""
from generators.eursc.science_shared import (
    factor_boxes,
    key_boxes,
    lifecycle_boxes,
    trophic_boxes,
)
from generators.shared.utils import (
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import normalize_mode, pick_named_variant

_LEVEL = "eursc"
_SUBJECT = "science"


def _topic_bank(topic):
    def mcq(difficulty, suffix, question, options, answer, solution):
        def _fn():
            return make_problem(
                question,
                solution,
                "Use S3 Living Earth ideas from the lesson. Scenarios are fictional.",
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
                "Check the ecology idea. This quiz does not grade a field product.",
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


def _bind(topic, pools):
    def variants(difficulty, mode="lesson"):
        mode = normalize_mode(mode)
        pool = list(pools.get(difficulty) or [])
        if mode == "mcq":
            return [fn for fn in pool if getattr(fn, "_kind", "") == "mcq"]
        return pool

    def generate(difficulty, mode="lesson", variant_name=None):
        chosen = variants(difficulty, mode)
        if not chosen:
            chosen = variants(difficulty, "lesson")
        fn = pick_named_variant(chosen, variant_name)
        return fn()

    return generate, variants


def _mcq_opts(a, b, c, d):
    return [f"A  {a}", f"B  {b}", f"C  {c}", f"D  {d}"]


_FE_MCQ, _FE_NUM, _FE_KEY, _FE_ORD, _FE_PICK = _topic_bank("food_environment")
_EC_MCQ, _EC_NUM, _EC_KEY, _EC_ORD, _EC_PICK = _topic_bank("ecosystems_cycles")
_CH_MCQ, _CH_NUM, _CH_KEY, _CH_ORD, _CH_PICK = _topic_bank("ecosystem_characteristics")
_CL_MCQ, _CL_NUM, _CL_KEY, _CL_ORD, _CL_PICK = _topic_bank("classification_biodiversity")
_FP_MCQ, _FP_NUM, _FP_KEY, _FP_ORD, _FP_PICK = _topic_bank("ecology_field_project")

_LIFE_BANK = (
    {"id": "produce", "text": "Produce is the start of the food lifecycle in this model"},
    {"id": "use", "text": "Use is eating or using the food in the public model"},
    {"id": "waste", "text": "Waste is leftover material in the system, not a private plate survey"},
    {"id": "diary", "text": "The quiz should store a private family carbon diary"},
)
_CLIM_BANK = (
    {"id": "ghg", "text": "Greenhouse gases in the atmosphere are a public climate idea"},
    {"id": "climate", "text": "Climate change is linked to public evidence here"},
    {"id": "choice", "text": "Sustainable choices are public options the class can discuss"},
    {"id": "rank_home", "text": "The quiz should rank whose household is greenest"},
)

_FE_POOLS = {
    "foundational": [
        _FE_MCQ("foundational", "ghg", "Greenhouse gases in this lesson are", _mcq_opts("a private confession", "a public atmosphere and climate idea", "a stored diet file", "a class rank"), "B", "Public climate idea."),
        _FE_MCQ("foundational", "produce_letter", "<p>Which letter is produce?</p>" + str(lifecycle_boxes(title="Produce letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is produce."),
        _FE_MCQ("foundational", "waste_idea", "Food waste in this lesson is", _mcq_opts("a demand to photograph plates", "a system leftover, not a private plate survey", "a magnet", "a shock survey"), "B", "System idea."),
        _FE_MCQ("foundational", "alex", "Alex (fictional) reads a public footprint table. A science use is", _mcq_opts("rank Alex's home", "compare public figures, not a live family diary", "upload a bill", "skip the lifecycle"), "B", "Public data."),
        _FE_MCQ("foundational", "no_diary", "This quiz", _mcq_opts("stores a private carbon diary", "does not store a private carbon diary", "ranks households", "inspects fridges"), "B", "No diary."),
        _FE_MCQ("foundational", "land", "Land use in a food system can", _mcq_opts("never affect biodiversity", "affect habitats and biodiversity in this model", "replace climate evidence", "rank classmates"), "B", "Land and biodiversity."),
        _FE_KEY("foundational", "carbon_word", "Write the word for the element named in greenhouse-gas talk here.", "carbon", "Carbon."),
        _FE_NUM("foundational", "three_st", "Produce, use and waste are how many lifecycle stages named here?", 3, "Three."),
        _FE_ORD("foundational", "puw", "Order produce, then use, then waste.", ["produce", "use", "waste"], _LIFE_BANK, "Start, use, leftover."),
        _FE_PICK("foundational", "life_ok", "Select produce and waste.", ["produce", "waste"], _LIFE_BANK, 2, "Two stages. No diary."),
    ],
    "intermediate": [
        _FE_MCQ("intermediate", "climate", "Climate change in this lesson is linked to", _mcq_opts("a class popularity prize", "public evidence, not a household interrogation", "a joint map", "a vaccination"), "B", "Public evidence."),
        _FE_MCQ("intermediate", "use_letter", "<p>Which letter is use?</p>" + str(lifecycle_boxes(title="Use letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is use."),
        _FE_MCQ("intermediate", "foot", "A footprint idea here is", _mcq_opts("a live family diary", "a public comparison, not a stored household file", "a lever", "a shock story"), "B", "Public comparison."),
        _FE_MCQ("intermediate", "sam", "Sam (fictional) wants a league of whose lunch is greener. The lesson says", _mcq_opts("publish the league", "use public examples; do not rank plates here", "photograph the class", "skip waste"), "B", "No plate rank."),
        _FE_MCQ("intermediate", "choice", "Sustainable choices in this lesson are", _mcq_opts("a private confession", "public options the class can discuss", "a stored medical file", "a magnet pole"), "B", "Public options."),
        _FE_MCQ("intermediate", "life", "A food lifecycle in this model", _mcq_opts("starts at waste only", "runs from produce through use to waste", "must be a home photo", "ranks families"), "B", "Produce to waste."),
        _FE_KEY("intermediate", "climate_word", "Write the word for long-term weather-pattern change used in this public model.", "climate", "Climate."),
        _FE_NUM("intermediate", "zero_diary", "How many live family carbon diaries should this quiz store? Enter 0.", 0, "Zero."),
        _FE_ORD("intermediate", "gc", "Order greenhouse gases, then climate evidence.", ["ghg", "climate"], _CLIM_BANK, "Atmosphere, then climate."),
        _FE_PICK("intermediate", "clim_ok", "Select greenhouse gases and sustainable choices.", ["ghg", "choice"], _CLIM_BANK, 2, "Two ideas. No household rank."),
    ],
    "difficult": [
        _FE_MCQ("difficult", "waste_letter", "<p>Which letter is waste?</p>" + str(lifecycle_boxes(title="Waste letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is waste."),
        _FE_MCQ("difficult", "jordan", "Jordan (fictional) wants the app to score whose family is greenest. The lesson says", _mcq_opts("store the score", "use public data; do not rank households here", "upload fridges", "skip climate"), "B", "No household rank."),
        _FE_MCQ("difficult", "both", "Land use and waste both", _mcq_opts("require a plate photo", "are food-system ideas without a private survey here", "are magnets", "are V = IR claims"), "B", "System ideas."),
        _FE_MCQ("difficult", "limit", "A limit of this lesson is", _mcq_opts("that GHGs cannot be named", "that it does not collect private plates or family diaries", "that lifecycles are banned", "that climate is a vote"), "B", "No private harvest."),
        _FE_MCQ("difficult", "misuse", "A misuse of the footprint table is", _mcq_opts("quoting a public figure", "demanding a live household carbon diary in the quiz", "ordering produce then waste", "naming greenhouse gases"), "B", "No live diary."),
        _FE_MCQ("difficult", "bio", "Biodiversity in a food-system story is", _mcq_opts("a class ranking", "a public habitat idea, not a pupil confession", "a stored diet", "a shock survey"), "B", "Public habitat idea."),
        _FE_KEY("difficult", "waste_word", "Write the word for leftover material in the food system here.", "waste", "Waste."),
        _FE_NUM("difficult", "stages3", "A produce–use–waste model has how many named stages?", 3, "Three."),
        _FE_ORD("difficult", "uw", "Order use, then waste.", ["use", "waste"], _LIFE_BANK, "Use, then leftover."),
        _FE_PICK("difficult", "not_fe", "Select the two items that do not belong.", ["diary", "rank_home"], _LIFE_BANK[:1] + _LIFE_BANK[3:] + _CLIM_BANK[1:2] + _CLIM_BANK[3:], 2, "No diary; no household rank."),
    ],
}

eursc_science_food_environment, eursc_science_food_environment_variants = _bind(
    "food_environment", _FE_POOLS
)

_TROPH_BANK = (
    {"id": "producer", "text": "A producer makes food using energy in this model"},
    {"id": "consumer", "text": "A consumer eats other organisms in this model"},
    {"id": "decomposer", "text": "A decomposer breaks down dead material in this model"},
    {"id": "rank_animal", "text": "The quiz should rank which pupil is which animal"},
)
_CYCLE_BANK = (
    {"id": "water", "text": "The water cycle moves water through public stages"},
    {"id": "carbon", "text": "The carbon cycle moves carbon through public stages"},
    {"id": "photo", "text": "Photosynthesis is a word-equation idea at S3"},
    {"id": "create_mat", "text": "Matter is created from nothing in an ecosystem"},
)

_ECY_POOLS = {
    "foundational": [
        _EC_MCQ("foundational", "eco", "An ecosystem in this lesson is", _mcq_opts("a class vote", "living things and their surroundings in this model", "a stored diet", "a household rank"), "B", "Living things plus surroundings."),
        _EC_MCQ("foundational", "prod_letter", "<p>Which letter is the producer?</p>" + str(trophic_boxes(title="Producer letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is the producer."),
        _EC_MCQ("foundational", "water", "The water cycle here is", _mcq_opts("a private diary", "public stages water can move through", "a magnet league", "a shock survey"), "B", "Public stages."),
        _EC_MCQ("foundational", "alex_ec", "Alex (fictional) names a plant as a producer. That fits", _mcq_opts("a pupil ranking", "the producer role in this trophic model", "a stored file", "a plate survey"), "B", "Producer."),
        _EC_MCQ("foundational", "no_rank", "This quiz", _mcq_opts("ranks pupils as animals", "does not rank pupils as animals", "stores a diet", "inspects homes"), "B", "No ranking."),
        _EC_MCQ("foundational", "flow", "Energy in a simple web", _mcq_opts("appears from nowhere always", "can be modelled as flowing between trophic roles", "must be a home bill", "ranks families"), "B", "Flow between roles."),
        _EC_KEY("foundational", "ecosystem_word", "Write the word for living things and their surroundings in this model.", "ecosystem", "Ecosystem."),
        _EC_NUM("foundational", "roles3", "Producer, consumer and decomposer are how many trophic roles named here?", 3, "Three."),
        _EC_ORD("foundational", "pcd", "Order producer, then consumer, then decomposer.", ["producer", "consumer", "decomposer"], _TROPH_BANK, "Make food, eat, then break down."),
        _EC_PICK("foundational", "troph_ok", "Select producer and decomposer.", ["producer", "decomposer"], _TROPH_BANK, 2, "Two roles. No pupil ranking."),
    ],
    "intermediate": [
        _EC_MCQ("intermediate", "cons_letter", "<p>Which letter is the consumer?</p>" + str(trophic_boxes(title="Consumer letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is the consumer."),
        _EC_MCQ("intermediate", "carbon", "The carbon cycle here is", _mcq_opts("a class league", "public stages carbon can move through", "a joint map", "a fridge photo"), "B", "Public stages."),
        _EC_MCQ("intermediate", "photo", "Photosynthesis in this S3 model is", _mcq_opts("a demand to log meals", "a word-equation idea linking light, carbon dioxide and a food store", "a stored clinical file", "a robot league"), "B", "Word-equation idea."),
        _EC_MCQ("intermediate", "sam_ec", "Sam (fictional) says a decomposer is optional in every web. A science reply is", _mcq_opts("agree always", "decomposers return matter in this model", "rank Sam", "skip water"), "B", "Return matter."),
        _EC_MCQ("intermediate", "resp", "Respiration here is", _mcq_opts("a private confession", "a word-equation idea that can release energy from a food store", "a household rank", "a key couplet"), "B", "Word-equation idea."),
        _EC_MCQ("intermediate", "web", "A food web schematic is", _mcq_opts("a classmate ranking", "a model of feeding links, not a pupil league", "a shock file", "a V = IR claim"), "B", "Feeding links."),
        _EC_KEY("intermediate", "producer_word", "Write the word for an organism that makes food using energy in this model.", "producer", "Producer."),
        _EC_NUM("intermediate", "cycles2", "Water and carbon are how many cycles named here?", 2, "Two."),
        _EC_ORD("intermediate", "wc", "Order the water cycle, then the carbon cycle.", ["water", "carbon"], _CYCLE_BANK, "Water, then carbon."),
        _EC_PICK("intermediate", "cyc_ok", "Select the water cycle and photosynthesis.", ["water", "photo"], _CYCLE_BANK, 2, "Two ideas. Matter is not created from nothing."),
    ],
    "difficult": [
        _EC_MCQ("difficult", "dec_letter", "<p>Which letter is the decomposer?</p>" + str(trophic_boxes(title="Decomposer letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the decomposer."),
        _EC_MCQ("difficult", "jordan_ec", "Jordan (fictional) wants a league of who is most like a wolf. The lesson says", _mcq_opts("publish the league", "study trophic roles; do not rank pupils as animals", "store files", "skip cycles"), "B", "No ranking."),
        _EC_MCQ("difficult", "both_ec", "Photosynthesis and respiration both", _mcq_opts("require a plate photo", "are word-equation ideas in this S3 model", "rank classmates", "inspect homes"), "B", "Word equations."),
        _EC_MCQ("difficult", "pyramid", "A pyramid schematic is", _mcq_opts("proof one pupil is best", "a model of amounts at trophic levels, not a class rank", "a stored diet", "a shock survey"), "B", "Amounts model."),
        _EC_MCQ("difficult", "limit_ec", "A limit of this lesson is", _mcq_opts("that producers cannot be named", "that it does not replace a field visit or rank pupils as animals", "that cycles are banned", "that webs are illegal"), "B", "Support only."),
        _EC_MCQ("difficult", "misuse_ec", "A misuse of a food web is", _mcq_opts("drawing feeding links", "ranking which pupil is which animal", "naming a decomposer", "outlining the carbon cycle"), "B", "No ranking."),
        _EC_KEY("difficult", "photo_word", "Write the word for the process that makes a food store using light in this S3 idea.", "photosynthesis", "Photosynthesis."),
        _EC_NUM("difficult", "roles_again", "How many trophic roles are named as producer, consumer and decomposer?", 3, "Three."),
        _EC_ORD("difficult", "cp", "Order carbon cycle, then photosynthesis.", ["carbon", "photo"], _CYCLE_BANK, "Cycle, then the word-equation idea."),
        _EC_PICK("difficult", "not_ec", "Select the two items that do not belong.", ["rank_animal", "create_mat"], _TROPH_BANK[:1] + _TROPH_BANK[3:] + _CYCLE_BANK[1:2] + _CYCLE_BANK[3:], 2, "No pupil ranking; matter is not created from nothing."),
    ],
}

eursc_science_ecosystems_cycles, eursc_science_ecosystems_cycles_variants = _bind(
    "ecosystems_cycles", _ECY_POOLS
)

_FACT_BANK = (
    {"id": "abiotic", "text": "Abiotic factors are non-living conditions such as light or temperature"},
    {"id": "biotic", "text": "Biotic factors are living influences such as feeding or competition"},
    {"id": "survey", "text": "A survey is a repeatable count or measure another group could follow"},
    {"id": "visit_replace", "text": "This web page replaces a field visit"},
)
_MODEL_BANK = (
    {"id": "trophic", "text": "A trophic model is incomplete, not the whole ecosystem"},
    {"id": "measure", "text": "An abiotic factor can be measured with teacher-approved instruments"},
    {"id": "thermo", "text": "Thermoregulation is a public animal example, not a pupil ranking"},
    {"id": "rank_field", "text": "The quiz should rank whose backyard is the best habitat"},
)

_CH_POOLS = {
    "foundational": [
        _CH_MCQ("foundational", "abiotic", "Abiotic factors in this lesson are", _mcq_opts("always classmates", "non-living conditions such as light or temperature", "a stored diet", "a shock survey"), "B", "Non-living conditions."),
        _CH_MCQ("foundational", "a_letter", "<p>Which letter is the abiotic factor?</p>" + str(factor_boxes(title="Abiotic letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is abiotic."),
        _CH_MCQ("foundational", "biotic", "Biotic factors in this lesson are", _mcq_opts("only rocks", "living influences such as feeding or competition", "a household rank", "a magnet"), "B", "Living influences."),
        _CH_MCQ("foundational", "alex_ch", "Alex (fictional) measures shade with a teacher kit. That fits", _mcq_opts("a private garden upload", "a classroom measurement of an abiotic factor", "a plate survey", "a league"), "B", "Classroom measurement."),
        _CH_MCQ("foundational", "no_replace", "This page", _mcq_opts("replaces a field visit", "does not replace a field visit", "stores backyard photos", "ranks habitats"), "B", "Support only."),
        _CH_MCQ("foundational", "survey", "A survey method should be", _mcq_opts("a secret only one pupil knows", "repeatable so another group could follow it", "a home photo harvest", "a diet file"), "B", "Repeatable."),
        _CH_KEY("foundational", "abiotic_word", "Write the word for non-living conditions such as light or temperature here.", "abiotic", "Abiotic."),
        _CH_NUM("foundational", "two_fact", "Abiotic and biotic are how many factor types named here?", 2, "Two."),
        _CH_ORD("foundational", "ab", "Order abiotic, then biotic, then a survey.", ["abiotic", "biotic", "survey"], _FACT_BANK, "Non-living, living, then a count."),
        _CH_PICK("foundational", "fact_ok", "Select abiotic and survey.", ["abiotic", "survey"], _FACT_BANK, 2, "Two ideas. The page does not replace a visit."),
    ],
    "intermediate": [
        _CH_MCQ("intermediate", "b_letter", "<p>Which letter is the biotic factor?</p>" + str(factor_boxes(title="Biotic letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is biotic."),
        _CH_MCQ("intermediate", "trophic_lim", "A simple trophic model is", _mcq_opts("the whole ecosystem always", "incomplete, not the whole ecosystem", "a class rank", "a fridge survey"), "B", "Incomplete model."),
        _CH_MCQ("intermediate", "thermo", "Thermoregulation here is", _mcq_opts("a pupil ranking", "a public animal example, not a classmate league", "a stored clinical file", "a carbon diary"), "B", "Public example."),
        _CH_MCQ("intermediate", "sam_ch", "Sam (fictional) counts daisies in two quadrats the teacher set. That is", _mcq_opts("a backyard photo upload", "a survey another group could repeat if the method is written", "a household rank", "a shock story"), "B", "Written survey."),
        _CH_MCQ("intermediate", "measure", "Measuring an abiotic factor in class", _mcq_opts("can skip the teacher", "needs teacher-approved instruments and a method", "uploads home gardens", "ranks pupils"), "B", "Teacher rules."),
        _CH_MCQ("intermediate", "activity", "Activity of an animal in this lesson is", _mcq_opts("a demand to track classmates", "a public example linked to conditions, not a pupil tracker", "a diet file", "a V = IR claim"), "B", "Public example."),
        _CH_KEY("intermediate", "biotic_word", "Write the word for living influences such as feeding or competition here.", "biotic", "Biotic."),
        _CH_NUM("intermediate", "zero_replace", "How many field visits does this web page replace? Enter 0.", 0, "Zero."),
        _CH_ORD("intermediate", "tm", "Order trophic-model limits, then measuring an abiotic factor.", ["trophic", "measure"], _MODEL_BANK, "Critique the model, then measure."),
        _CH_PICK("intermediate", "mod_ok", "Select trophic-model limits and thermoregulation as a public example.", ["trophic", "thermo"], _MODEL_BANK, 2, "Two ideas. No backyard rank."),
    ],
    "difficult": [
        _CH_MCQ("difficult", "c_letter", "<p>Which letter is the survey step?</p>" + str(factor_boxes(title="Survey letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the survey."),
        _CH_MCQ("difficult", "jordan_ch", "Jordan (fictional) wants a league of whose garden is wildest. The lesson says", _mcq_opts("publish the league", "use a class survey; do not rank backyards here", "upload photos to the app", "skip abiotic factors"), "B", "No backyard rank."),
        _CH_MCQ("difficult", "both_ch", "Abiotic and biotic factors both", _mcq_opts("must be a home confession", "help describe an ecosystem in this model", "rank classmates", "replace the teacher"), "B", "Describe the system."),
        _CH_MCQ("difficult", "critique", "A model critique is", _mcq_opts("proof science is a vote", "saying what the trophic sketch leaves out", "a stored diet", "a shock survey"), "B", "What it leaves out."),
        _CH_MCQ("difficult", "limit_ch", "A limit of this lesson is", _mcq_opts("that factors cannot be named", "that it does not replace a field visit or harvest home photos", "that surveys are banned", "that light is not abiotic"), "B", "Support only."),
        _CH_MCQ("difficult", "misuse_ch", "A misuse of a survey is", _mcq_opts("writing a repeatable method", "ranking whose backyard is the best habitat in this app", "naming temperature as abiotic", "counting with a teacher quadrat"), "B", "No backyard league."),
        _CH_KEY("difficult", "survey_word", "Write the word for a repeatable count or measure another group could follow.", "survey", "Survey."),
        _CH_NUM("difficult", "types2", "How many factor types are named as abiotic and biotic?", 2, "Two."),
        _CH_ORD("difficult", "mt", "Order measuring an abiotic factor, then thermoregulation as a public example.", ["measure", "thermo"], _MODEL_BANK, "Measure, then the animal example."),
        _CH_PICK("difficult", "not_ch", "Select the two items that do not belong.", ["visit_replace", "rank_field"], _FACT_BANK[:1] + _FACT_BANK[3:] + _MODEL_BANK[1:2] + _MODEL_BANK[3:], 2, "The page does not replace a visit; no backyard rank."),
    ],
}

eursc_science_ecosystem_characteristics, eursc_science_ecosystem_characteristics_variants = _bind(
    "ecosystem_characteristics", _CH_POOLS
)

_KEY_BANK = (
    {"id": "couplet", "text": "A dichotomous key asks one checkable feature at a time"},
    {"id": "group", "text": "The key ends in a named group another pupil could reach"},
    {"id": "species", "text": "A species is a grouping idea used in this S3 model"},
    {"id": "collect", "text": "The quiz should harvest a private home collection"},
)
_TAX_BANK = (
    {"id": "taxonomy", "text": "Taxonomy is a historical grouping system, including Linnaeus in this lesson"},
    {"id": "descent", "text": "Common descent is a scientific model, not a class ranking"},
    {"id": "loss", "text": "Biodiversity loss is linked to public evidence here"},
    {"id": "rank_kid", "text": "The quiz should rank which pupil is most related to an ape"},
)

_CL_POOLS = {
    "foundational": [
        _CL_MCQ("foundational", "species", "A species in this lesson is", _mcq_opts("a class popularity prize", "a grouping idea used in this S3 model", "a stored diet", "a shock survey"), "B", "Grouping idea."),
        _CL_MCQ("foundational", "a_letter", "<p>Which letter is the first couplet?</p>" + str(key_boxes(title="Couplet A letter")), _mcq_opts("B", "A", "C", "a handle"), "B", "A is the first couplet."),
        _CL_MCQ("foundational", "group_feat", "Grouping features should be", _mcq_opts("a secret only one pupil knows", "checkable so another pupil could use them", "a home collection harvest", "a household rank"), "B", "Checkable."),
        _CL_MCQ("foundational", "alex_cl", "Alex (fictional) follows a public leaf key. That fits", _mcq_opts("a private collection upload", "a dichotomous key on a public example", "a plate survey", "a magnet league"), "B", "Public key."),
        _CL_MCQ("foundational", "no_collect", "This quiz", _mcq_opts("harvests a private home collection", "does not harvest a private home collection", "ranks relatedness of classmates", "inspects fridges"), "B", "No harvest."),
        _CL_MCQ("foundational", "groups", "Broad groups in this lesson are", _mcq_opts("a diet file", "named sets used to organise living things in this model", "a shock story", "a V = IR claim"), "B", "Named sets."),
        _CL_KEY("foundational", "species_word", "Write the word for the grouping idea used for living things here.", "species", "Species."),
        _CL_NUM("foundational", "zero_collect", "How many private home collections should this quiz harvest? Enter 0.", 0, "Zero."),
        _CL_ORD("foundational", "cg", "Order a couplet, then a named group.", ["couplet", "group"], _KEY_BANK, "Check a feature, then name the group."),
        _CL_PICK("foundational", "key_ok", "Select a couplet and a species idea.", ["couplet", "species"], _KEY_BANK, 2, "Two ideas. No private collection."),
    ],
    "intermediate": [
        _CL_MCQ("intermediate", "b_letter", "<p>Which letter is the second couplet?</p>" + str(key_boxes(title="Couplet B letter")), _mcq_opts("A", "B", "C", "a brand"), "B", "B is the second couplet."),
        _CL_MCQ("intermediate", "taxonomy", "Taxonomy in this lesson is", _mcq_opts("a class league", "a historical grouping system, including Linnaeus here", "a stored clinical file", "a carbon diary"), "B", "Grouping system."),
        _CL_MCQ("intermediate", "descent", "Common descent here is", _mcq_opts("a pupil ranking", "a scientific model, not a class ranking", "a fridge photo", "a shock survey"), "B", "Scientific model."),
        _CL_MCQ("intermediate", "sam_cl", "Sam (fictional) wants to upload a home insect box. The lesson says", _mcq_opts("upload it here", "use public examples; do not harvest a private collection", "rank Sam", "skip keys"), "B", "Public examples."),
        _CL_MCQ("intermediate", "loss", "Biodiversity loss is linked to", _mcq_opts("a popularity prize", "public evidence and sustainability ideas", "a joint map", "a robot league"), "B", "Public evidence."),
        _CL_MCQ("intermediate", "key", "A dichotomous key", _mcq_opts("asks many features at once always", "asks one checkable feature at a time in this model", "must be a home secret", "ranks classmates"), "B", "One feature at a time."),
        _CL_KEY("intermediate", "taxonomy_word", "Write the word for the grouping system that includes Linnaeus in this lesson.", "taxonomy", "Taxonomy."),
        _CL_NUM("intermediate", "two_coup", "A simple key here is drawn as two couplets then a group. How many couplets are shown before the group?", 2, "Two."),
        _CL_ORD("intermediate", "td", "Order taxonomy, then common descent.", ["taxonomy", "descent"], _TAX_BANK, "System, then the descent model."),
        _CL_PICK("intermediate", "tax_ok", "Select taxonomy and biodiversity loss.", ["taxonomy", "loss"], _TAX_BANK, 2, "Two ideas. No relatedness rank of classmates."),
    ],
    "difficult": [
        _CL_MCQ("difficult", "c_letter", "<p>Which letter is the named group?</p>" + str(key_boxes(title="Group letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the named group."),
        _CL_MCQ("difficult", "jordan_cl", "Jordan (fictional) wants a league of who is most related to an ape. The lesson says", _mcq_opts("publish the league", "teach common descent as a model; do not rank pupils", "store files", "skip keys"), "B", "No ranking."),
        _CL_MCQ("difficult", "sustain", "Sustainability in this lesson is", _mcq_opts("a private confession", "a public idea linked to biodiversity, not a household interrogation", "a stored diet", "a magnet"), "B", "Public idea."),
        _CL_MCQ("difficult", "both_cl", "Keys and taxonomy both", _mcq_opts("require a home collection", "organise living things so another pupil could follow the steps", "rank classmates", "inspect homes"), "B", "Followable grouping."),
        _CL_MCQ("difficult", "limit_cl", "A limit of this lesson is", _mcq_opts("that species cannot be named", "that it does not harvest private collections or rank relatedness of classmates", "that Linnaeus is banned", "that keys are illegal"), "B", "No harvest."),
        _CL_MCQ("difficult", "misuse_cl", "A misuse of common descent teaching is", _mcq_opts("stating it as a scientific model", "ranking which pupil is most related to an ape", "following a public key", "naming biodiversity loss"), "B", "No ranking."),
        _CL_KEY("difficult", "biodiversity_word", "Write the word for variety of living things used with loss and sustainability here.", "biodiversity", "Biodiversity."),
        _CL_NUM("difficult", "zero_rank", "How many classmate-relatedness leagues should this quiz keep? Enter 0.", 0, "Zero."),
        _CL_ORD("difficult", "dl", "Order common descent, then biodiversity loss.", ["descent", "loss"], _TAX_BANK, "Model, then loss evidence."),
        _CL_PICK("difficult", "not_cl", "Select the two items that do not belong.", ["collect", "rank_kid"], _KEY_BANK[:1] + _KEY_BANK[3:] + _TAX_BANK[1:2] + _TAX_BANK[3:], 2, "No private collection; no relatedness rank."),
    ],
}

eursc_science_classification_biodiversity, eursc_science_classification_biodiversity_variants = _bind(
    "classification_biodiversity", _CL_POOLS
)

_FIELD_BANK = (
    {"id": "question", "text": "Write a field question another group could test"},
    {"id": "risk", "text": "Plan risk with the teacher's assessment"},
    {"id": "sample", "text": "Choose a sampling idea such as a quadrat the teacher approves"},
    {"id": "league_plot", "text": "The quiz should rank whose garden plot is best"},
)
_DATA_BANK = (
    {"id": "method", "text": "Record a method another group could repeat, with units"},
    {"id": "analyse", "text": "Analyse the pattern with numbers from the table"},
    {"id": "present", "text": "Present and reflect; the field product is not auto-graded here"},
    {"id": "upload", "text": "Pupils must upload private home-garden photos to this app"},
)

_FP_POOLS = {
    "foundational": [
        _FP_MCQ("foundational", "question", "The first project phase is to", _mcq_opts("hide the method", "write a field question another group could test", "rank garden plots in a stored league", "skip safety"), "B", "A testable question."),
        _FP_MCQ("foundational", "risk", "Risk in the field study", _mcq_opts("can skip the teacher", "follows the teacher's assessment, not a home-garden harvest", "uploads medical files", "ranks pupils"), "B", "Teacher assessment."),
        _FP_MCQ("foundational", "not_auto", "The field product in this app is", _mcq_opts("fully auto-graded as a product", "not auto-graded; class uses a rubric", "a diet file", "a shock survey"), "B", "Rubric in class."),
        _FP_MCQ("foundational", "alex_fp", "Alex (fictional) writes 'How does shade affect daisy counts in the school lawn?'. That is", _mcq_opts("a private confession", "a testable field question", "a stored league", "a V = IR claim"), "B", "Testable."),
        _FP_MCQ("foundational", "ibl", "Classroom field time", _mcq_opts("is replaced by this web page", "still needs the site, kit and the teacher's risk assessment", "uploads home gardens here", "ranks plots"), "B", "Page does not replace practical."),
        _FP_MCQ("foundational", "no_league", "This quiz", _mcq_opts("stores whose plot is best", "does not store a field-plot league", "inspects homes", "skips sampling"), "B", "No league."),
        _FP_KEY("foundational", "sampling_word", "Write the word for choosing where and how to count in a field study here.", "sampling", "Sampling."),
        _FP_NUM("foundational", "zero_grade", "How many field products does this app auto-grade as a finished product? Enter 0.", 0, "Zero."),
        _FP_ORD("foundational", "qr", "Order the field question, then risk planning.", ["question", "risk"], _FIELD_BANK, "Question, then risk."),
        _FP_PICK("foundational", "q_ok", "Select a testable question and sampling.", ["question", "sample"], _FIELD_BANK, 2, "Two project actions. No plot league."),
    ],
    "intermediate": [
        _FP_MCQ("intermediate", "quadrat", "A quadrat in this project is", _mcq_opts("a private photo album", "a sampling frame the teacher approves", "a household rank", "a magnet"), "B", "Approved sampling frame."),
        _FP_MCQ("intermediate", "method", "A useful method is one that", _mcq_opts("only the original group can remember", "another group could follow, with units in the table", "must be a home secret", "ranks plots"), "B", "Followable."),
        _FP_MCQ("intermediate", "analyse", "Analysis in this project", _mcq_opts("is only a feeling", "uses numbers from the table", "uploads gardens", "skips risk"), "B", "Numbers from the table."),
        _FP_MCQ("intermediate", "sam_fp", "Sam (fictional) finds one quadrat empty. A project next step is", _mcq_opts("hide the zero", "keep the raw count and comment in the evaluation", "rank Sam", "skip the method"), "B", "Keep the raw count."),
        _FP_MCQ("intermediate", "present", "Presentation in this project is", _mcq_opts("a stored popularity score", "evidence another group could follow, judged with a class rubric", "a shock survey", "a diet file"), "B", "Evidence plus rubric."),
        _FP_MCQ("intermediate", "safety_fp", "Field safety is", _mcq_opts("optional", "the teacher's risk assessment; this page does not replace it", "a private medical file", "a biodiversity league"), "B", "Teacher rules."),
        _FP_KEY("intermediate", "quadrat_word", "Write the word for a square sampling frame used if the teacher approves it.", "quadrat", "Quadrat."),
        _FP_NUM("intermediate", "phases6", "This project names how many classroom phases in the lesson?", 6, "Six phases."),
        _FP_ORD("intermediate", "ma", "Order recording a method, then analysing with table numbers.", ["method", "analyse"], _DATA_BANK, "Method, then numbers."),
        _FP_PICK("intermediate", "data_ok", "Select a followable method and presenting evidence.", ["method", "present"], _DATA_BANK, 2, "Two project ideas. No photo harvest."),
    ],
    "difficult": [
        _FP_MCQ("difficult", "jordan_fp", "Jordan (fictional) wants the app to crown a winner. The lesson says", _mcq_opts("store the league", "use a class rubric; do not store a plot ranking here", "upload homes", "skip tests"), "B", "No stored league."),
        _FP_MCQ("difficult", "site", "The study site", _mcq_opts("must be a private garden uploaded here", "is the place the teacher approves, recorded in the lab book", "is a diet file", "is a shock survey"), "B", "Teacher-approved site."),
        _FP_MCQ("difficult", "fail", "An unexpected count in the project is", _mcq_opts("proof to hide the method", "evidence for evaluation, not a stored ranking", "a medical file", "a reason to skip safety"), "B", "Evaluate."),
        _FP_MCQ("difficult", "limit_fp", "A limit of this page is", _mcq_opts("that questions cannot be written", "that it does not replace the field visit or auto-grade the product", "that sampling cannot be named", "that teachers have no rubric"), "B", "Support page only."),
        _FP_MCQ("difficult", "misuse_fp", "A misuse of the project is", _mcq_opts("writing a testable question", "forcing private home-garden photos into this app", "keeping a zero in the table", "using a class rubric"), "B", "No private photo harvest."),
        _FP_MCQ("difficult", "roles", "Collaboration in the field", _mcq_opts("must be a secret", "has shared roles the teacher can see in class, not a hidden league here", "uploads medical files", "replaces the risk assessment"), "B", "Shared roles in class."),
        _FP_KEY("difficult", "safety_word", "Write the word for following the teacher's risk rules in the field.", "safety", "Safety."),
        _FP_NUM("difficult", "zero_upload", "How many private home-garden photo uploads does this quiz require? Enter 0.", 0, "Zero."),
        _FP_ORD("difficult", "sp", "Order sampling, then presenting evidence.", ["sample", "present"], _FIELD_BANK[:3] + _DATA_BANK[2:3], "Sample, then present."),
        _FP_PICK("difficult", "not_fp", "Select the two items that do not belong.", ["league_plot", "upload"], _FIELD_BANK[:1] + _FIELD_BANK[3:] + _DATA_BANK[1:2] + _DATA_BANK[3:], 2, "No stored league; no photo harvest."),
    ],
}

eursc_science_ecology_field_project, eursc_science_ecology_field_project_variants = _bind(
    "ecology_field_project", _FP_POOLS
)


