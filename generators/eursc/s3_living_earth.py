"""S3 Unit 3.2 Living Earth — 3.2.1–3.2.5."""
from generators.eursc.s3_unit32_living_earth_advanced import (
    CLASSIFICATION_BIODIVERSITY_MS_POOLS,
    CLASSIFICATION_BIODIVERSITY_SMS_POOLS,
    ECOLOGY_FIELD_PROJECT_MS_POOLS,
    ECOLOGY_FIELD_PROJECT_SMS_POOLS,
    ECOSYSTEM_CHARACTERISTICS_MS_POOLS,
    ECOSYSTEM_CHARACTERISTICS_SMS_POOLS,
    ECOSYSTEMS_CYCLES_MS_POOLS,
    ECOSYSTEMS_CYCLES_SMS_POOLS,
    FOOD_ENVIRONMENT_MS_POOLS,
    FOOD_ENVIRONMENT_SMS_POOLS,
)
from generators.eursc.science_shared import (
    bind_eursc_topic,
    factor_boxes,
    key_boxes,
    lifecycle_boxes,
    trophic_boxes,
)
from generators.shared.variant_utils import (
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
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


_FE_MCQ, _FE_NUM, _FE_KEY, _FE_ORD, _FE_PICK = _topic_bank("food_environment")
_EC_MCQ, _EC_NUM, _EC_KEY, _EC_ORD, _EC_PICK = _topic_bank("ecosystems_cycles")
_CH_MCQ, _CH_NUM, _CH_KEY, _CH_ORD, _CH_PICK = _topic_bank("ecosystem_characteristics")
_CL_MCQ, _CL_NUM, _CL_KEY, _CL_ORD, _CL_PICK = _topic_bank("classification_biodiversity")
_FP_MCQ, _FP_NUM, _FP_KEY, _FP_ORD, _FP_PICK = _topic_bank("ecology_field_project")

_LIFE_BANK = (
    {"id": "produce", "text": "Produce is the start of the food lifecycle"},
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
        _FE_MCQ("foundational", "ghg", "Greenhouse gases are", _mcq_opts("gases made only by cars and factories", "a public atmosphere and climate idea", "the same thing as the ozone layer", "gases that cool the whole planet down"), "B", "Public climate idea.", "Look for gases in the air the class can discuss as a shared climate idea; they trap heat rather than cool the planet, and they are not the ozone layer."),
        _FE_MCQ("foundational", "produce_letter", "<p>Which letter is produce?</p>" + str(lifecycle_boxes(title="Produce letter")), _mcq_opts("B", "A", "C", "none of them"), "B", "A is produce.", "Read the caption under each box on the lifecycle strip. Match the letter to the start-of-food stage; it is one of the three boxes."),
        _FE_MCQ("foundational", "waste_idea", "Food waste is", _mcq_opts("a demand to photograph plates", "a system leftover, not a private plate survey", "only the packaging around food", "food that has no environmental cost"), "B", "System idea.", "Leftover food is a system idea for the class, not a demand to photograph anyone's plate."),
        _FE_MCQ("foundational", "alex", "Alex (fictional) reads a public footprint table. A science use is", _mcq_opts("rank Alex's home", "compare public figures, not a live family diary", "copy the largest figure as a rule for everyone", "treat the table as proof about one family"), "B", "Public data.", "Alex is fictional. Use a published table the class can share, not a live family diary or a home rank."),
        _FE_MCQ("foundational", "no_diary", "This quiz", _mcq_opts("stores a private carbon diary", "does not store a private carbon diary", "ranks households by footprint", "asks for a home energy bill"), "B", "No diary.", "Ask what this quiz is allowed to keep. It should not store a private household carbon file."),
        _FE_MCQ("foundational", "land", "Land use in a food system can", _mcq_opts("only affect the soil, never wildlife", "affect habitats and biodiversity", "be ignored because farms are natural", "increase biodiversity in every case"), "B", "Land and biodiversity.", "Think how growing food can change habitats. That can affect variety of living things."),
        _FE_KEY("foundational", "carbon_word", "Write the word for the element named in greenhouse-gas talk here.", "carbon", "Carbon.", "Name the element often mentioned when the class talks about greenhouse gases in the air."),
        _FE_NUM("foundational", "three_st", "Produce, use and waste are how many lifecycle stages named here?", 3, "Three.", "Count the named stages: start of food, eating or using it, then leftover material. How many is that?"),
        _FE_ORD("foundational", "puw", "Order produce, then use, then waste.", ["produce", "use", "waste"], _LIFE_BANK, "Start, use, leftover.", "Put the start of the food model first, then eating or using, then leftover material. Skip a private diary."),
        _FE_PICK("foundational", "life_ok", "Select produce and waste.", ["produce", "waste"], _LIFE_BANK, 2, "Two stages. No diary.", "Tick the start of the model and leftover material. Leave out eating-or-using if it is not asked, and skip a diary."),
    ],
    "intermediate": [
        _FE_MCQ("intermediate", "climate", "Climate change is linked to", _mcq_opts("the weather on one unusually hot day", "public evidence, not a household interrogation", "the hole in the ozone layer only", "natural causes alone, never human activity"), "B", "Public evidence.", "Long-term weather-pattern change rests on public evidence over many years, not one hot day, the ozone hole or a household interrogation."),
        _FE_MCQ("intermediate", "use_letter", "<p>Which letter is use?</p>" + str(lifecycle_boxes(title="Use letter")), _mcq_opts("A", "B", "C", "none of them"), "B", "B is use.", "On the three-box strip, find the middle stage — eating or using food — and match its letter."),
        _FE_MCQ("intermediate", "foot", "A footprint idea is", _mcq_opts("a live family diary", "a public comparison, not a stored household file", "the area of ground a person stands on", "a count of steps walked to the shops"), "B", "Public comparison.", "A footprint figure is something the class can compare from public numbers, not a stored household file."),
        _FE_MCQ("intermediate", "sam", "Sam (fictional) wants a league of whose lunch is greener. The right response is", _mcq_opts("publish the league", "use public examples; do not rank plates here", "let the class vote on the winner", "keep a private lunch list for Sam"), "B", "No plate rank.", "Sam wants a lunch league. Science class can use public examples without ranking whose plate is greener."),
        _FE_MCQ("intermediate", "choice", "Sustainable choices are", _mcq_opts("only choices that cost more money", "public options the class can discuss", "always the choice with the least packaging", "choices that only governments can make"), "B", "Public options.", "Looking-after-the-planet options are things the class can discuss in the open; they are not only for governments and not always the dearest choice."),
        _FE_MCQ("intermediate", "life", "A food lifecycle", _mcq_opts("ends when the food is bought in a shop", "runs from produce through use to waste", "starts when the food reaches the plate", "only covers the growing of the food"), "B", "Produce to waste.", "Follow the food model from growing or making, through eating or using, to leftover material — it does not stop at the shop or the plate."),
        _FE_KEY("intermediate", "climate_word", "Write the word for long-term weather-pattern change used in this public model.", "climate", "Climate.", "Write the one-word name for long-term change in weather patterns used in this public model."),
        _FE_NUM("intermediate", "zero_diary", "How many live family carbon diaries should this quiz store? Enter 0.", 0, "Zero.", "The quiz should store no live family carbon diaries. The question already tells you the number to enter."),
        _FE_ORD("intermediate", "gc", "Order greenhouse gases, then climate evidence.", ["ghg", "climate"], _CLIM_BANK, "Atmosphere, then climate.", "First the gases in the atmosphere, then the long-term weather-pattern evidence. Skip ranking households."),
        _FE_PICK("intermediate", "clim_ok", "Select greenhouse gases and sustainable choices.", ["ghg", "choice"], _CLIM_BANK, 2, "Two ideas. No household rank.", "Tick the atmosphere-gases idea and the public looking-after-the-planet options. Skip ranking whose home is greenest."),
    ],
    "difficult": [
        _FE_MCQ("difficult", "waste_letter", "<p>Which letter is waste?</p>" + str(lifecycle_boxes(title="Waste letter")), _mcq_opts("A", "C", "B", "none of them"), "B", "C is waste.", "On the three-box strip, find leftover material at the end of the food model and match its letter."),
        _FE_MCQ("difficult", "jordan", "Jordan (fictional) wants the app to score whose family is greenest. The right response is", _mcq_opts("store the score", "use public data; do not rank households here", "let the class vote on the greenest family", "keep the scores in a private list"), "B", "No household rank.", "Jordan wants a family score. Use public data in class; do not turn the app into a household ranking."),
        _FE_MCQ("difficult", "both", "Land use and waste both", _mcq_opts("require a plate photo", "are food-system ideas without a private survey here", "only matter for meat, never for plants", "happen only after food reaches the shop"), "B", "System ideas.", "Growing food on land and leftover material are both food-system ideas. Neither needs a private plate survey here."),
        _FE_MCQ("difficult", "limit", "Which of these is true about this quiz?", _mcq_opts("that GHGs cannot be named", "that it does not collect private plates or family diaries", "that it stores each pupil's lunch choices", "that it ranks the class by footprint"), "B", "No private harvest.", "Think what this quiz refuses to collect: private plates and family diaries. That is a limit, not a ban on naming gases."),
        _FE_MCQ("difficult", "misuse", "A misuse of the footprint table is", _mcq_opts("quoting a public figure from the published table", "demanding a live household carbon diary in the quiz", "ordering produce, then use, then waste with it", "naming the greenhouse gases the table refers to"), "B", "No live diary.", "Quoting a public figure from the table is fine. Demanding a live household carbon diary in the quiz is the misuse."),
        _FE_MCQ("difficult", "bio", "Biodiversity in a food-system story is", _mcq_opts("the number of crops one farm grows", "a public habitat idea, not a pupil confession", "a measure of how much food is produced", "the same thing as a food chain"), "B", "Public habitat idea.", "Variety of living things in a food-system story is a public habitat idea, not a count of one farm's crops or the amount of food grown."),
        _FE_KEY("difficult", "waste_word", "Write the word for leftover material in the food system here.", "waste", "Waste.", "Name leftover material in the food system — the last stage after eating or using, not a plate photo."),
        _FE_NUM("difficult", "stages3", "A produce–use–waste model has how many named stages?", 3, "Three.", "The hyphenated model names a start, a middle, and an end. Count those named stages."),
        _FE_ORD("difficult", "uw", "Order use, then waste.", ["use", "waste"], _LIFE_BANK, "Use, then leftover.", "Eating or using comes before leftover material. Skip the start-of-food box for this order."),
        _FE_PICK("difficult", "not_fe", "Select the two items that do not belong.", ["diary", "rank_home"], _LIFE_BANK[:1] + _LIFE_BANK[3:] + _CLIM_BANK[1:2] + _CLIM_BANK[3:], 2, "No diary; no household rank.", "Pick the two that turn the quiz into a private diary or a household rank. Those do not belong."),
    ],
}

_FE_STANDARD = {
    "foundational": (
        'food_environment_foundational_mcq_alex',
        'food_environment_foundational_keyword_carbon_word',
        'food_environment_foundational_number_three_st',
        'food_environment_foundational_order_puw',
        'food_environment_foundational_pick_life_ok',
    ),
    "intermediate": (
        'food_environment_intermediate_mcq_choice',
        'food_environment_intermediate_keyword_climate_word',
        'food_environment_intermediate_number_zero_diary',
        'food_environment_intermediate_order_gc',
        'food_environment_intermediate_pick_clim_ok',
    ),
    "difficult": (
        'food_environment_difficult_mcq_bio',
        'food_environment_difficult_keyword_waste_word',
        'food_environment_difficult_number_stages3',
        'food_environment_difficult_order_uw',
        'food_environment_difficult_pick_not_fe',
    ),
}
eursc_science_food_environment, eursc_science_food_environment_variants = bind_eursc_topic(
    'food_environment',
    _FE_POOLS,
    _FE_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: FOOD_ENVIRONMENT_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: FOOD_ENVIRONMENT_SMS_POOLS,
    },
)

_TROPH_BANK = (
    {"id": "producer", "text": "A producer makes food using energy"},
    {"id": "consumer", "text": "A consumer eats other organisms"},
    {"id": "decomposer", "text": "A decomposer breaks down dead material"},
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
        _EC_MCQ("foundational", "eco", "An ecosystem is", _mcq_opts("only the animals in one area", "living things and their surroundings", "only the non-living parts of a place", "a single food chain"), "B", "Living things plus surroundings.", "Think of living things together with the place around them, not just the animals or a single food chain."),
        _EC_MCQ("foundational", "prod_letter", "<p>Which letter is the producer?</p>" + str(trophic_boxes(title="Producer letter")), _mcq_opts("B", "A", "C", "none of them"), "B", "A is the producer.", "On the trophic strip, find who makes food using energy. Match that box's letter."),
        _EC_MCQ("foundational", "water", "The water cycle is", _mcq_opts("water being made new in the clouds", "public stages water can move through", "water only flowing downhill to the sea", "rain that never returns to the air"), "B", "Public stages.", "Water moving through named public stages is the cycle idea here; water is not made new in the clouds and does not stop at the sea."),
        _EC_MCQ("foundational", "alex_ec", "Alex (fictional) names a plant as a producer. That fits", _mcq_opts("the consumer role", "the producer role", "the decomposer role", "the predator role"), "B", "Producer.", "Alex names a plant that makes food. That matches the first trophic role, not the consumer or decomposer role."),
        _EC_MCQ("foundational", "no_rank", "This quiz", _mcq_opts("ranks pupils as animals", "does not rank pupils as animals", "gives each pupil an animal score", "keeps a private class league"), "B", "No ranking.", "This quiz must not turn pupils into animals on a league. Pick what the quiz actually does instead."),
        _EC_MCQ("foundational", "flow", "Energy in a simple web", _mcq_opts("is created by consumers when they eat", "can be modelled as flowing between trophic roles", "is passed on completely at every level", "flows from consumers back to producers"), "B", "Flow between roles.", "Energy in a simple web can be drawn as moving between trophic roles; it is not created by consumers and is not passed on completely."),
        _EC_KEY("foundational", "ecosystem_word", "Write the word for living things and their surroundings.", "ecosystem", "Ecosystem.", "One word names living things plus their surroundings. It is not a diet file."),
        _EC_NUM("foundational", "roles3", "Producer, consumer and decomposer are how many trophic roles named here?", 3, "Three.", "Count who makes food, who eats other organisms, and who breaks down dead material. How many roles is that?"),
        _EC_ORD("foundational", "pcd", "Order producer, then consumer, then decomposer.", ["producer", "consumer", "decomposer"], _TROPH_BANK, "Make food, eat, then break down.", "Start with who makes food, then who eats other organisms, then who breaks down dead material."),
        _EC_PICK("foundational", "troph_ok", "Select producer and decomposer.", ["producer", "decomposer"], _TROPH_BANK, 2, "Two roles. No pupil ranking.", "Tick who makes food and who breaks down dead material. Skip ranking which pupil is which animal."),
    ],
    "intermediate": [
        _EC_MCQ("intermediate", "cons_letter", "<p>Which letter is the consumer?</p>" + str(trophic_boxes(title="Consumer letter")), _mcq_opts("A", "B", "C", "none of them"), "B", "B is the consumer.", "On the trophic strip, find who eats other organisms. Match that box's letter."),
        _EC_MCQ("intermediate", "carbon", "The carbon cycle is", _mcq_opts("carbon being created by plants", "public stages carbon can move through", "carbon being destroyed by animals", "carbon dioxide leaving Earth for space"), "B", "Public stages.", "This cycle moves an element through public stages the class can name; carbon is not created or destroyed on the way."),
        _EC_MCQ("intermediate", "photo", "Photosynthesis is", _mcq_opts("a process in which plants take in food through their roots", "a word-equation idea linking light, carbon dioxide and a food store", "a process that releases energy from a food store in every cell", "a process in which plants breathe out carbon dioxide at night"), "B", "Word-equation idea.", "Photosynthesis is a word equation linking light, a gas in air, and a food store — plants make food, they do not take it in through roots."),
        _EC_MCQ("intermediate", "sam_ec", "Sam (fictional) says a decomposer is optional in every web. A science reply is", _mcq_opts("dead matter just vanishes", "decomposers return matter", "consumers do that job", "decomposers make food"), "B", "Return matter.", "Sam thinks the breakdown role is optional. That role returns matter; dead material does not just vanish."),
        _EC_MCQ("intermediate", "resp", "Respiration is", _mcq_opts("another name for breathing in and out", "a word-equation idea that can release energy from a food store", "a process that only happens in animals", "a process that makes a food store using light"), "B", "Word-equation idea.", "This word-equation idea can release energy from a food store. It is not just breathing, and it is not making food with light."),
        _EC_MCQ("intermediate", "web", "A food web schematic is", _mcq_opts("a single line of who eats whom", "a model of feeding links, not a pupil league", "a diagram of where animals live", "a chart of how big each animal is"), "B", "Feeding links.", "A food-web drawing shows feeding links. It is not a single line, a map of homes or a size chart."),
        _EC_KEY("intermediate", "producer_word", "Write the word for an organism that makes food using energy.", "producer", "Producer.", "Name the organism that makes food using energy — the start of the trophic strip."),
        _EC_NUM("intermediate", "cycles2", "Water and carbon are how many cycles named here?", 2, "Two.", "There is a water path and an element path. Count how many cycles that is."),
        _EC_ORD("intermediate", "wc", "Order the water cycle, then the carbon cycle.", ["water", "carbon"], _CYCLE_BANK, "Water, then carbon.", "Put the water path first, then the path that moves the named element. Skip the claim that matter appears from nothing."),
        _EC_PICK("intermediate", "cyc_ok", "Select the water cycle and photosynthesis.", ["water", "photo"], _CYCLE_BANK, 2, "Two ideas. Matter is not created from nothing.", "Tick the water path and the word-equation idea that uses light. Skip matter-from-nothing."),
    ],
    "difficult": [
        _EC_MCQ("difficult", "dec_letter", "<p>Which letter is the decomposer?</p>" + str(trophic_boxes(title="Decomposer letter")), _mcq_opts("A", "C", "B", "none of them"), "B", "C is the decomposer.", "On the trophic strip, find who breaks down dead material. Match that box's letter."),
        _EC_MCQ("difficult", "jordan_ec", "Jordan (fictional) wants a league of who is most like a wolf. The right response is", _mcq_opts("publish the league", "study trophic roles; do not rank pupils as animals", "let the class vote on the wolf", "keep a private animal list"), "B", "No ranking.", "Jordan wants a wolf-likeness league. Study trophic roles; do not rank pupils as animals."),
        _EC_MCQ("difficult", "both_ec", "Photosynthesis and respiration both", _mcq_opts("happen only in plants", "are word-equation ideas", "happen only in daylight", "make a food store"), "B", "Word equations.", "Making a food store with light and releasing energy from a food store are both word-equation ideas here."),
        _EC_MCQ("difficult", "pyramid", "A pyramid schematic is", _mcq_opts("proof one pupil is best", "a model of amounts at trophic levels, not a class rank", "a map of where each organism lives", "a drawing of which animal is largest"), "B", "Amounts model.", "A pyramid sketch models amounts at trophic levels. It does not prove one pupil is best."),
        _EC_MCQ("difficult", "limit_ec", "Which of these is true about this quiz?", _mcq_opts("that producers cannot be named", "that it does not replace a field visit or rank pupils as animals", "that it stores an animal score for each pupil", "that it counts as a field visit"), "B", "Support only.", "This quiz supports ideas in class. It does not replace a field visit or rank pupils as animals."),
        _EC_MCQ("difficult", "misuse_ec", "A misuse of a food web is", _mcq_opts("drawing feeding links between organisms", "ranking which pupil is which animal", "naming the decomposer role in the web", "showing where the carbon cycle links in"), "B", "No ranking.", "Drawing feeding links between organisms is fine. Ranking which pupil is which animal is the misuse of a food web."),
        _EC_KEY("difficult", "photo_word", "Write the word for the process that makes a food store using light in this S3 idea.", "photosynthesis", "Photosynthesis.", "Name the process that makes a food store using light in this S3 idea — a word-equation process, not a meal photo."),
        _EC_NUM("difficult", "roles_again", "How many trophic roles are named as producer, consumer and decomposer?", 3, "Three.", "The question lists the making-food, eating, and breaking-down names. Count those named roles."),
        _EC_ORD("difficult", "cp", "Order carbon cycle, then photosynthesis.", ["carbon", "photo"], _CYCLE_BANK, "Cycle, then the word-equation idea.", "First the path that moves the named element, then the word-equation idea that uses light."),
        _EC_PICK("difficult", "not_ec", "Select the two items that do not belong.", ["rank_animal", "create_mat"], _TROPH_BANK[:1] + _TROPH_BANK[3:] + _CYCLE_BANK[1:2] + _CYCLE_BANK[3:], 2, "No pupil ranking; matter is not created from nothing.", "Pick ranking pupils as animals, and the claim that matter is created from nothing. Those do not belong."),
    ],
}

_ECY_STANDARD = {
    "foundational": (
        'ecosystems_cycles_foundational_mcq_alex_ec',
        'ecosystems_cycles_foundational_keyword_ecosystem_word',
        'ecosystems_cycles_foundational_number_roles3',
        'ecosystems_cycles_foundational_order_pcd',
        'ecosystems_cycles_foundational_pick_troph_ok',
    ),
    "intermediate": (
        'ecosystems_cycles_intermediate_mcq_carbon',
        'ecosystems_cycles_intermediate_keyword_producer_word',
        'ecosystems_cycles_intermediate_number_cycles2',
        'ecosystems_cycles_intermediate_order_wc',
        'ecosystems_cycles_intermediate_pick_cyc_ok',
    ),
    "difficult": (
        'ecosystems_cycles_difficult_mcq_both_ec',
        'ecosystems_cycles_difficult_keyword_photo_word',
        'ecosystems_cycles_difficult_number_roles_again',
        'ecosystems_cycles_difficult_order_cp',
        'ecosystems_cycles_difficult_pick_not_ec',
    ),
}
eursc_science_ecosystems_cycles, eursc_science_ecosystems_cycles_variants = bind_eursc_topic(
    'ecosystems_cycles',
    _ECY_POOLS,
    _ECY_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: ECOSYSTEMS_CYCLES_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: ECOSYSTEMS_CYCLES_SMS_POOLS,
    },
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
        _CH_MCQ("foundational", "abiotic", "Abiotic factors are", _mcq_opts("living influences such as grazing or disease", "non-living conditions such as light or temperature", "only the rocks and soil of a habitat", "conditions that never change in a habitat"), "B", "Non-living conditions.", "These factors are non-living conditions such as light or temperature, not living influences such as grazing."),
        _CH_MCQ("foundational", "a_letter", "<p>Which letter is the abiotic factor?</p>" + str(factor_boxes(title="Abiotic letter")), _mcq_opts("B", "A", "C", "none of them"), "B", "A is abiotic.", "On the factor strip, find the non-living-conditions box and match its letter."),
        _CH_MCQ("foundational", "biotic", "Biotic factors are", _mcq_opts("non-living conditions such as light or rainfall", "living influences such as feeding or competition", "only the plants growing in a habitat", "only the largest predators in a habitat"), "B", "Living influences.", "These factors are living influences such as feeding or competition, not non-living conditions such as light."),
        _CH_MCQ("foundational", "alex_ch", "Alex (fictional) measures shade with a teacher kit. That fits", _mcq_opts("a private garden upload", "a classroom measurement of an abiotic factor", "a classroom measurement of a biotic factor", "a survey that needs no written method"), "B", "Classroom measurement.", "Alex uses a teacher kit to measure shade. That is a classroom measure of a non-living condition, not a garden upload."),
        _CH_MCQ("foundational", "no_replace", "This page", _mcq_opts("replaces a field visit completely", "does not replace a field visit", "stores each pupil's backyard photos", "ranks the class's home habitats"), "B", "Support only.", "A web page supports the lesson. It does not stand in for going outside with the teacher, and it does not store or rank anyone's home."),
        _CH_MCQ("foundational", "survey", "A survey method should be", _mcq_opts("a secret only one pupil knows", "repeatable so another group could follow it", "changed each time to get a better result", "done once, since repeats waste time"), "B", "Repeatable.", "A method another group could follow is repeatable. A secret only one pupil knows is not."),
        _CH_KEY("foundational", "abiotic_word", "Write the word for non-living conditions such as light or temperature here.", "abiotic", "Abiotic.", "Name the type of factor that is non-living, such as light or temperature."),
        _CH_NUM("foundational", "two_fact", "Abiotic and biotic are how many factor types named here?", 2, "Two.", "Count the named types: non-living conditions and living influences. How many factor types is that?"),
        _CH_ORD("foundational", "ab", "Order abiotic, then biotic, then a survey.", ["abiotic", "biotic", "survey"], _FACT_BANK, "Non-living, living, then a count.", "Non-living conditions first, then living influences, then a repeatable count. Skip the claim that the page replaces a visit."),
        _CH_PICK("foundational", "fact_ok", "Select abiotic and survey.", ["abiotic", "survey"], _FACT_BANK, 2, "Two ideas. The page does not replace a visit.", "Tick non-living conditions and a repeatable count. The page still does not replace a visit."),
    ],
    "intermediate": [
        _CH_MCQ("intermediate", "b_letter", "<p>Which letter is the biotic factor?</p>" + str(factor_boxes(title="Biotic letter")), _mcq_opts("A", "B", "C", "none of them"), "B", "B is biotic.", "On the factor strip, find the living-influences box and match its letter."),
        _CH_MCQ("intermediate", "trophic_lim", "A simple trophic model is", _mcq_opts("the whole ecosystem always", "incomplete, not the whole ecosystem", "a complete list of every species present", "exact, because it uses arrows"), "B", "Incomplete model.", "A simple feeding-role sketch leaves things out. It is not the whole ecosystem."),
        _CH_MCQ("intermediate", "thermo", "Thermoregulation is", _mcq_opts("an animal changing its body temperature to match the air", "a public animal example, not a classmate league", "a plant turning its leaves to face the light", "a way of measuring air temperature in a habitat"), "B", "Public example.", "Keeping a steady body temperature is a public animal example, not a classmate league."),
        _CH_MCQ("intermediate", "sam_ch", "Sam (fictional) counts daisies in two quadrats the teacher set. That is", _mcq_opts("a backyard photo upload", "a survey another group could repeat if the method is written", "a result that already counts for the whole field", "a measurement of an abiotic factor"), "B", "Written survey.", "Sam counts daisies in teacher quadrats. If the method is written, another group could repeat it."),
        _CH_MCQ("intermediate", "measure", "Measuring an abiotic factor in class", _mcq_opts("can be estimated by eye without a kit", "needs teacher-approved instruments and a method", "only ever needs a thermometer", "needs no written method if done once"), "B", "Teacher rules.", "Class measurement of a non-living condition needs teacher-approved instruments and a written method."),
        _CH_MCQ("intermediate", "activity", "Activity of an animal is", _mcq_opts("a demand to track classmates", "a public example linked to conditions, not a pupil tracker", "a factor that never depends on temperature", "an abiotic factor like light"), "B", "Public example.", "Animal activity is a public example linked to conditions, not a demand to track classmates."),
        _CH_KEY("intermediate", "biotic_word", "Write the word for living influences such as feeding or competition here.", "biotic", "Biotic.", "Name the type of factor that is a living influence, such as feeding or competition."),
        _CH_NUM("intermediate", "zero_replace", "How many field visits does this web page replace? Enter 0.", 0, "Zero.", "This page replaces no field visits. The question already tells you the number to enter."),
        _CH_ORD("intermediate", "tm", "Order trophic-model limits, then measuring an abiotic factor.", ["trophic", "measure"], _MODEL_BANK, "Critique the model, then measure.", "First say what a simple feeding-role sketch leaves out, then measure a non-living condition."),
        _CH_PICK("intermediate", "mod_ok", "Select trophic-model limits and thermoregulation as a public example.", ["trophic", "thermo"], _MODEL_BANK, 2, "Two ideas. No backyard rank.", "Tick the incomplete-model idea and the public animal temperature example. Skip ranking backyards."),
    ],
    "difficult": [
        _CH_MCQ("difficult", "c_letter", "<p>Which letter is the survey step?</p>" + str(factor_boxes(title="Survey letter")), _mcq_opts("A", "C", "B", "none of them"), "B", "C is the survey.", "On the factor strip, find the repeatable-count box and match its letter."),
        _CH_MCQ("difficult", "jordan_ch", "Jordan (fictional) wants a league of whose garden is wildest. The right response is", _mcq_opts("publish the league", "use a class survey; do not rank backyards here", "upload photos to the app", "let the class vote on the wildest garden"), "B", "No backyard rank.", "Jordan wants a wildest-garden league. Use a class survey; do not rank backyards in this app."),
        _CH_MCQ("difficult", "both_ch", "Abiotic and biotic factors both", _mcq_opts("are non-living conditions", "help describe an ecosystem", "are living influences", "stay the same in every habitat"), "B", "Describe the system.", "Non-living conditions and living influences both help describe an ecosystem here. One kind is non-living, the other living."),
        _CH_MCQ("difficult", "critique", "A model critique is", _mcq_opts("proof science is a vote", "saying what the trophic sketch leaves out", "saying the sketch is wrong and useless", "redrawing the sketch with more arrows"), "B", "What it leaves out.", "Critiquing a model means saying what the trophic sketch leaves out, not treating science as a vote."),
        _CH_MCQ("difficult", "limit_ch", "Which of these is true about this quiz?", _mcq_opts("that factors cannot be named", "that it does not replace a field visit or harvest home photos", "that it counts as a field visit", "that it stores photos of gardens"), "B", "Support only.", "This quiz does not replace a field visit or harvest home photos. Factors can still be named."),
        _CH_MCQ("difficult", "misuse_ch", "A misuse of a survey is", _mcq_opts("writing a repeatable method for the count", "ranking whose backyard is the best habitat in this app", "naming temperature as an abiotic factor", "counting in a quadrat the teacher has set"), "B", "No backyard league.", "Writing a repeatable method for the count is fine. Ranking whose backyard is the best habitat in this app is the misuse."),
        _CH_KEY("difficult", "survey_word", "Write the word for a repeatable count or measure another group could follow.", "survey", "Survey.", "Name a repeatable count or measure another group could follow — not a secret method."),
        _CH_NUM("difficult", "types2", "How many factor types are named as abiotic and biotic?", 2, "Two.", "The question names non-living and living factor kinds. Count how many factor types that is."),
        _CH_ORD("difficult", "mt", "Order measuring an abiotic factor, then thermoregulation as a public example.", ["measure", "thermo"], _MODEL_BANK, "Measure, then the animal example.", "First measure a non-living condition, then the public animal temperature example."),
        _CH_PICK("difficult", "not_ch", "Select the two items that do not belong.", ["visit_replace", "rank_field"], _FACT_BANK[:1] + _FACT_BANK[3:] + _MODEL_BANK[1:2] + _MODEL_BANK[3:], 2, "The page does not replace a visit; no backyard rank.", "Pick the claim that the page replaces a visit, and ranking backyards. Those do not belong."),
    ],
}

_CH_STANDARD = {
    "foundational": (
        'ecosystem_characteristics_foundational_mcq_a_letter',
        'ecosystem_characteristics_foundational_keyword_abiotic_word',
        'ecosystem_characteristics_foundational_number_two_fact',
        'ecosystem_characteristics_foundational_order_ab',
        'ecosystem_characteristics_foundational_pick_fact_ok',
    ),
    "intermediate": (
        'ecosystem_characteristics_intermediate_mcq_activity',
        'ecosystem_characteristics_intermediate_keyword_biotic_word',
        'ecosystem_characteristics_intermediate_number_zero_replace',
        'ecosystem_characteristics_intermediate_order_tm',
        'ecosystem_characteristics_intermediate_pick_mod_ok',
    ),
    "difficult": (
        'ecosystem_characteristics_difficult_mcq_both_ch',
        'ecosystem_characteristics_difficult_keyword_survey_word',
        'ecosystem_characteristics_difficult_number_types2',
        'ecosystem_characteristics_difficult_order_mt',
        'ecosystem_characteristics_difficult_pick_not_ch',
    ),
}
eursc_science_ecosystem_characteristics, eursc_science_ecosystem_characteristics_variants = bind_eursc_topic(
    'ecosystem_characteristics',
    _CH_POOLS,
    _CH_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: ECOSYSTEM_CHARACTERISTICS_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: ECOSYSTEM_CHARACTERISTICS_SMS_POOLS,
    },
)

_KEY_BANK = (
    {"id": "couplet", "text": "A dichotomous key asks one checkable feature at a time"},
    {"id": "group", "text": "The key ends in a named group another pupil could reach"},
    {"id": "species", "text": "A species is a grouping idea"},
    {"id": "collect", "text": "The quiz should harvest a private home collection"},
)
_TAX_BANK = (
    {"id": "taxonomy", "text": "Taxonomy is a historical grouping system, including Linnaeus"},
    {"id": "descent", "text": "Common descent is a scientific model, not a class ranking"},
    {"id": "loss", "text": "Biodiversity loss is linked to public evidence here"},
    {"id": "rank_kid", "text": "The quiz should rank which pupil is most related to an ape"},
)

_CL_POOLS = {
    "foundational": [
        _CL_MCQ("foundational", "species", "A species is", _mcq_opts("a single animal", "a grouping idea", "a type of habitat", "a food chain"), "B", "Grouping idea.", "This grouping idea organises living things. It is not one animal or a habitat."),
        _CL_MCQ("foundational", "a_letter", "<p>Which letter is the first couplet?</p>" + str(key_boxes(title="Couplet A letter")), _mcq_opts("B", "A", "C", "none of them"), "B", "A is the first couplet.", "On the key diagram, find the first yes/no check and match its letter."),
        _CL_MCQ("foundational", "group_feat", "Grouping features should be", _mcq_opts("a secret only one pupil knows", "checkable so another pupil could use them", "a home collection harvest", "based on size, which changes as things grow"), "B", "Checkable.", "Features for grouping should be checkable so another pupil could use them, not a secret or a home harvest."),
        _CL_MCQ("foundational", "alex_cl", "Alex (fictional) follows a public leaf key. That fits", _mcq_opts("a private collection upload", "a dichotomous key on a public example", "a guess based on the leaf's colour", "a survey of how many leaves there are"), "B", "Public key.", "Alex follows a public leaf key. That is a yes/no key on a public example, not a private collection upload."),
        _CL_MCQ("foundational", "no_collect", "This quiz", _mcq_opts("harvests a private home collection", "does not harvest a private home collection", "ranks relatedness of classmates", "asks for photos of pets at home"), "B", "No harvest.", "This quiz must not harvest a private home collection. Pick what the quiz actually does."),
        _CL_MCQ("foundational", "groups", "Broad groups are", _mcq_opts("the same as a single species", "named sets used to organise living things", "sets of animals that live in the same place", "lists that only include animals"), "B", "Named sets.", "Broad named sets organise living things. They are not one species or one habitat."),
        _CL_KEY("foundational", "species_word", "Write the word for the grouping idea used for living things here.", "species", "Species.", "Write the grouping-idea word used for living things here — the usual name for one kind of organism."),
        _CL_NUM("foundational", "zero_collect", "How many private home collections should this quiz harvest? Enter 0.", 0, "Zero.", "The quiz should harvest no private home collections. The question already tells you the number to enter."),
        _CL_ORD("foundational", "cg", "Order a couplet, then a named group.", ["couplet", "group"], _KEY_BANK, "Check a feature, then name the group.", "First one checkable yes/no step, then the named group another pupil could reach."),
        _CL_PICK("foundational", "key_ok", "Select a couplet and a species idea.", ["couplet", "species"], _KEY_BANK, 2, "Two ideas. No private collection.", "Tick a yes/no check and the grouping-idea for living things. Skip harvesting a private collection."),
    ],
    "intermediate": [
        _CL_MCQ("intermediate", "b_letter", "<p>Which letter is the second couplet?</p>" + str(key_boxes(title="Couplet B letter")), _mcq_opts("A", "B", "C", "none of them"), "B", "B is the second couplet.", "On the key diagram, find the second yes/no check and match its letter."),
        _CL_MCQ("intermediate", "taxonomy", "Taxonomy is", _mcq_opts("the study of how animals move", "a historical grouping system, including Linnaeus", "a way of measuring biodiversity in a habitat", "the study of stuffed animals in museums"), "B", "Grouping system.", "This historical grouping system includes Linnaeus. It is not taxidermy or a biodiversity count."),
        _CL_MCQ("intermediate", "descent", "Common descent is", _mcq_opts("proof that humans came from monkeys alive today", "a scientific model, not a class ranking", "a rule that species never change over time", "a ranking of which species is most advanced"), "B", "Scientific model.", "Shared ancestry is a scientific model, not a ranking of classmates."),
        _CL_MCQ("intermediate", "sam_cl", "Sam (fictional) wants to upload a home insect box. The right response is", _mcq_opts("upload it here", "use public examples; do not harvest a private collection", "let the class vote on Sam's box", "keep a private list of Sam's insects"), "B", "Public examples.", "Sam wants to upload a home insect box. Use public examples; do not harvest a private collection here."),
        _CL_MCQ("intermediate", "loss", "Biodiversity loss is linked to", _mcq_opts("the number of animals in one zoo", "public evidence and sustainability ideas", "a rise in the number of species", "natural change that humans cannot affect"), "B", "Public evidence.", "Fewer kinds of living things is linked to public evidence and looking-after-life ideas, not a rise in species or one zoo."),
        _CL_MCQ("intermediate", "key", "A dichotomous key", _mcq_opts("asks many features at once always", "asks one checkable feature at a time", "gives the name without any questions", "asks about colour only, never shape"), "B", "One feature at a time.", "A dichotomous key asks one checkable feature at a time, not many at once."),
        _CL_KEY("intermediate", "taxonomy_word", "Write the word for the grouping system that includes Linnaeus.", "taxonomy", "Taxonomy.", "Name the grouping system that includes Linnaeus — a historical organising system."),
        _CL_NUM("intermediate", "two_coup", "A simple key is drawn as two couplets then a group. How many couplets are shown before the group?", 2, "Two.", "The simple key is drawn as yes/no checks then a group. Count the checks shown before the group."),
        _CL_ORD("intermediate", "td", "Order taxonomy, then common descent.", ["taxonomy", "descent"], _TAX_BANK, "System, then the descent model.", "First the historical grouping system, then the shared-ancestry model. Skip ranking relatedness of classmates."),
        _CL_PICK("intermediate", "tax_ok", "Select taxonomy and biodiversity loss.", ["taxonomy", "loss"], _TAX_BANK, 2, "Two ideas. No relatedness rank of classmates.", "Tick the grouping system and the public evidence of fewer kinds of living things. Skip a classmate relatedness rank."),
    ],
    "difficult": [
        _CL_MCQ("difficult", "c_letter", "<p>Which letter is the named group?</p>" + str(key_boxes(title="Group letter")), _mcq_opts("A", "C", "B", "none of them"), "B", "C is the named group.", "On the key diagram, find the named group at the end and match its letter."),
        _CL_MCQ("difficult", "jordan_cl", "Jordan (fictional) wants a league of who is most related to an ape. The right response is", _mcq_opts("publish the league", "teach common descent as a model; do not rank pupils", "let the class vote on the most ape-like", "keep a private relatedness list"), "B", "No ranking.", "Jordan wants an ape-relatedness league. Teach shared ancestry as a model; do not rank pupils."),
        _CL_MCQ("difficult", "sustain", "Sustainability is", _mcq_opts("a rule that no resources may ever be used", "a public idea linked to biodiversity, not a household interrogation", "a plan that only affects future generations", "an idea that only applies to recycling"), "B", "Public idea.", "Looking after living things is a public idea linked to variety of life, not a household interrogation."),
        _CL_MCQ("difficult", "both_cl", "Keys and taxonomy both", _mcq_opts("put every animal into one group", "organise living things so another pupil could follow the steps", "only work for animals, never plants", "depend on colour alone"), "B", "Followable grouping.", "Yes/no keys and the grouping system both organise living things so another pupil could follow the steps."),
        _CL_MCQ("difficult", "limit_cl", "Which of these is true about this quiz?", _mcq_opts("that species cannot be named", "that it does not harvest private collections or rank relatedness of classmates", "that it stores photos of home pets", "that it ranks the class by relatedness"), "B", "No harvest.", "This quiz does not harvest private collections or rank relatedness of classmates. Living-thing groups can still be named."),
        _CL_MCQ("difficult", "misuse_cl", "A misuse of common descent teaching is", _mcq_opts("stating it as a scientific model of shared ancestry", "ranking which pupil is most related to an ape", "following a public key to a named group", "naming biodiversity loss as public evidence"), "B", "No ranking.", "Stating shared ancestry as a scientific model is fine. Ranking which pupil is most related to an ape is the misuse."),
        _CL_KEY("difficult", "biodiversity_word", "Write the word for variety of living things used with loss and sustainability here.", "biodiversity", "Biodiversity.", "Name the variety of living things used with loss and looking-after-life ideas here."),
        _CL_NUM("difficult", "zero_rank", "How many classmate-relatedness leagues should this quiz keep? Enter 0.", 0, "Zero.", "The quiz should keep no classmate-relatedness leagues. The question already tells you the number to enter."),
        _CL_ORD("difficult", "dl", "Order common descent, then biodiversity loss.", ["descent", "loss"], _TAX_BANK, "Model, then loss evidence.", "First the shared-ancestry model, then public evidence that variety of life is falling."),
        _CL_PICK("difficult", "not_cl", "Select the two items that do not belong.", ["collect", "rank_kid"], _KEY_BANK[:1] + _KEY_BANK[3:] + _TAX_BANK[1:2] + _TAX_BANK[3:], 2, "No private collection; no relatedness rank.", "Pick harvesting a private collection, and ranking which pupil is most related to an ape. Those do not belong."),
    ],
}

_CL_STANDARD = {
    "foundational": (
        'classification_biodiversity_foundational_mcq_a_letter',
        'classification_biodiversity_foundational_keyword_species_word',
        'classification_biodiversity_foundational_number_zero_collect',
        'classification_biodiversity_foundational_order_cg',
        'classification_biodiversity_foundational_pick_key_ok',
    ),
    "intermediate": (
        'classification_biodiversity_intermediate_mcq_b_letter',
        'classification_biodiversity_intermediate_keyword_taxonomy_word',
        'classification_biodiversity_intermediate_number_two_coup',
        'classification_biodiversity_intermediate_order_td',
        'classification_biodiversity_intermediate_pick_tax_ok',
    ),
    "difficult": (
        'classification_biodiversity_difficult_mcq_both_cl',
        'classification_biodiversity_difficult_keyword_biodiversity_word',
        'classification_biodiversity_difficult_number_zero_rank',
        'classification_biodiversity_difficult_order_dl',
        'classification_biodiversity_difficult_pick_not_cl',
    ),
}
eursc_science_classification_biodiversity, eursc_science_classification_biodiversity_variants = bind_eursc_topic(
    'classification_biodiversity',
    _CL_POOLS,
    _CL_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: CLASSIFICATION_BIODIVERSITY_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: CLASSIFICATION_BIODIVERSITY_SMS_POOLS,
    },
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
        _FP_MCQ("foundational", "question", "The first project phase is to", _mcq_opts("start counting before any question is set", "write a field question another group could test", "rank garden plots in a stored league", "decide the answer, then look for the data"), "B", "A testable question.", "Start by writing a field question another group could test, not by counting first, deciding the answer in advance or ranking plots."),
        _FP_MCQ("foundational", "risk", "Risk in the field study", _mcq_opts("is only needed for trips abroad", "follows the teacher's assessment, not a home-garden harvest", "can be judged by each pupil on the day", "is the same for every site"), "B", "Teacher assessment.", "Field risk follows the teacher's assessment. It is not something each pupil decides on the day, and not a home-garden harvest."),
        _FP_MCQ("foundational", "not_auto", "The field product in this app is", _mcq_opts("fully auto-graded as a product", "not auto-graded; class uses a rubric", "graded only on the biggest count", "graded by a class vote"), "B", "Rubric in class.", "The finished field product is judged with a class rubric. This app does not auto-grade it as a product."),
        _FP_MCQ("foundational", "alex_fp", "Alex (fictional) writes 'How does shade affect daisy counts in the school lawn?'. That is", _mcq_opts("a prediction, not a question", "a testable field question", "a question with no variable to compare", "a conclusion drawn before counting"), "B", "Testable.", "Alex's shade-and-daisy question can be tested on the school lawn. That is a field question, not a conclusion."),
        _FP_MCQ("foundational", "ibl", "Classroom field time", _mcq_opts("is replaced by this web page", "still needs the site, kit and the teacher's risk assessment", "can be done from photos without a visit", "needs no risk assessment on the school lawn"), "B", "Page does not replace practical.", "Classroom field time still needs the site, kit and the teacher's risk assessment. A web page does not replace that."),
        _FP_MCQ("foundational", "no_league", "This quiz", _mcq_opts("stores whose plot is best", "does not store a field-plot league", "asks for garden photos", "grades the plots by class vote"), "B", "No league.", "This quiz must not store whose plot is best. Pick what the quiz actually does."),
        _FP_KEY("foundational", "sampling_word", "Write the word for choosing where and how to count in a field study here.", "sampling", "Sampling.", "Name choosing where and how to count in a field study — not a stored plot league."),
        _FP_NUM("foundational", "zero_grade", "How many field products does this app auto-grade as a finished product? Enter 0.", 0, "Zero.", "This app auto-grades no finished field products. The question already tells you the number to enter."),
        _FP_ORD("foundational", "qr", "Order the field question, then risk planning.", ["question", "risk"], _FIELD_BANK, "Question, then risk.", "First write a testable field question, then plan risk with the teacher."),
        _FP_PICK("foundational", "q_ok", "Select a testable question and sampling.", ["question", "sample"], _FIELD_BANK, 2, "Two project actions. No plot league.", "Tick a testable question and choosing where to count. Skip ranking garden plots."),
    ],
    "intermediate": [
        _FP_MCQ("intermediate", "quadrat", "A quadrat in this project is", _mcq_opts("a trap for catching small animals", "a sampling frame the teacher approves", "a net for sampling a pond", "a device for measuring light"), "B", "Approved sampling frame.", "This square frame is a sampling tool the teacher approves, not a trap or a net."),
        _FP_MCQ("intermediate", "method", "A useful method is one that", _mcq_opts("only the original group can remember", "another group could follow, with units in the table", "gives the biggest count of all the teams", "changes each time to suit the site"), "B", "Followable.", "A useful method is one another group could follow, with units in the table — not one only the original group can remember."),
        _FP_MCQ("intermediate", "analyse", "Analysis in this project", _mcq_opts("is only a feeling", "uses numbers from the table", "uses only the largest count", "is done before the counts are recorded"), "B", "Numbers from the table.", "Look at the numbers in the table. Analysis uses those counts, not only a feeling."),
        _FP_MCQ("intermediate", "sam_fp", "Sam (fictional) finds one quadrat empty. A project next step is", _mcq_opts("hide the zero", "keep the raw count and comment in the evaluation", "replace the zero with the mean", "move the quadrat until it is not empty"), "B", "Keep the raw count.", "An empty frame is still data. Keep the raw count and comment in the evaluation; do not hide the zero."),
        _FP_MCQ("intermediate", "present", "Presentation in this project is", _mcq_opts("a stored popularity score", "evidence another group could follow, judged with a class rubric", "a poster judged on how colourful it is", "only the final answer, without the method"), "B", "Evidence plus rubric.", "Show evidence another group could follow, judged with a class rubric — not a stored popularity score."),
        _FP_MCQ("intermediate", "safety_fp", "Field safety is", _mcq_opts("optional if the site is on school grounds", "the teacher's risk assessment; this page does not replace it", "only needed for pond work", "checked after the visit, not before"), "B", "Teacher rules.", "Field safety is the teacher's risk assessment. This page does not replace it."),
        _FP_KEY("intermediate", "quadrat_word", "Write the word for a square sampling frame used if the teacher approves it.", "quadrat", "Quadrat.", "Name the square sampling frame used if the teacher approves it — not a household rank."),
        _FP_NUM("intermediate", "phases6", "This project names how many classroom phases?", 6, "Six phases.", "Count the named classroom phases in the project sequence from question through present."),
        _FP_ORD("intermediate", "ma", "Order recording a method, then analysing with table numbers.", ["method", "analyse"], _DATA_BANK, "Method, then numbers.", "First record a method another group could repeat, then analyse the pattern with table numbers."),
        _FP_PICK("intermediate", "data_ok", "Select a followable method and presenting evidence.", ["method", "present"], _DATA_BANK, 2, "Two project ideas. No photo harvest.", "Tick a followable method and presenting evidence. Skip forcing private garden photos into the app."),
    ],
    "difficult": [
        _FP_MCQ("difficult", "jordan_fp", "Jordan (fictional) wants the app to crown a winner. The right response is", _mcq_opts("store the league", "use a class rubric; do not store a plot ranking here", "let the class vote on the winner", "keep a private winners list"), "B", "No stored league.", "Jordan wants the app to crown a winner. Use a class rubric; do not store a plot ranking here."),
        _FP_MCQ("difficult", "site", "The study site", _mcq_opts("must be a private garden uploaded here", "is the place the teacher approves, recorded in the lab book", "is chosen on the day without recording it", "must be the same for every team in the country"), "B", "Teacher-approved site.", "The study site is the place the teacher approves, recorded in the lab book — not a private garden uploaded here."),
        _FP_MCQ("difficult", "fail", "An unexpected count in the project is", _mcq_opts("proof to hide the method", "evidence for evaluation, not a stored ranking", "a mistake to remove from the table", "proof the whole study failed"), "B", "Evaluate.", "An unexpected count is evidence for evaluation. It is not a reason to hide the method or store a ranking."),
        _FP_MCQ("difficult", "limit_fp", "A limit of this page is", _mcq_opts("that questions cannot be written", "that it does not replace the field visit or auto-grade the product", "that it stores photos of home gardens", "that it ranks the teams' plots"), "B", "Support page only.", "This page does not replace the field visit or auto-grade the product. Questions can still be written."),
        _FP_MCQ("difficult", "misuse_fp", "A misuse of the project is", _mcq_opts("writing a testable question about the school lawn", "forcing private home-garden photos into this app", "keeping a zero count in the results table", "using a class rubric to judge the product"), "B", "No private photo harvest.", "Writing a testable question about the school lawn is fine. Forcing private home-garden photos into this app is the misuse."),
        _FP_MCQ("difficult", "roles", "Collaboration in the field", _mcq_opts("must be a secret", "has shared roles the teacher can see in class, not a hidden league here", "means one pupil does all the counting", "means every result must agree exactly"), "B", "Shared roles in class.", "Collaboration has shared roles the teacher can see in class, not a hidden league or a secret."),
        _FP_KEY("difficult", "safety_word", "Write the word for following the teacher's risk rules in the field.", "safety", "Safety.", "Name following the teacher's risk rules in the field — not a stored popularity score."),
        _FP_NUM("difficult", "zero_upload", "How many private home-garden photo uploads does this quiz require? Enter 0.", 0, "Zero.", "This quiz requires no private home-garden photo uploads. The question already tells you the number to enter."),
        _FP_ORD("difficult", "sp", "Order sampling, then presenting evidence.", ["sample", "present"], _FIELD_BANK[:3] + _DATA_BANK[2:3], "Sample, then present.", "First choose where and how to count, then present evidence. Skip ranking whose plot is best."),
        _FP_PICK("difficult", "not_fp", "Select the two items that do not belong.", ["league_plot", "upload"], _FIELD_BANK[:1] + _FIELD_BANK[3:] + _DATA_BANK[1:2] + _DATA_BANK[3:], 2, "No stored league; no photo harvest.", "Pick ranking whose garden plot is best, and forcing private garden photos into the app. Those do not belong."),
    ],
}

_FP_STANDARD = {
    "foundational": (
        'ecology_field_project_foundational_mcq_alex_fp',
        'ecology_field_project_foundational_keyword_sampling_word',
        'ecology_field_project_foundational_number_zero_grade',
        'ecology_field_project_foundational_order_qr',
        'ecology_field_project_foundational_pick_q_ok',
    ),
    "intermediate": (
        'ecology_field_project_intermediate_mcq_analyse',
        'ecology_field_project_intermediate_keyword_quadrat_word',
        'ecology_field_project_intermediate_number_phases6',
        'ecology_field_project_intermediate_order_ma',
        'ecology_field_project_intermediate_pick_data_ok',
    ),
    "difficult": (
        'ecology_field_project_difficult_mcq_fail',
        'ecology_field_project_difficult_keyword_safety_word',
        'ecology_field_project_difficult_number_zero_upload',
        'ecology_field_project_difficult_order_sp',
        'ecology_field_project_difficult_pick_not_fp',
    ),
}
eursc_science_ecology_field_project, eursc_science_ecology_field_project_variants = bind_eursc_topic(
    'ecology_field_project',
    _FP_POOLS,
    _FP_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: ECOLOGY_FIELD_PROJECT_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: ECOLOGY_FIELD_PROJECT_SMS_POOLS,
    },
)


