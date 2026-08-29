"""S1 Unit 1.2 Food — 1.2.1–1.2.8."""
from generators.eursc.science_shared import bind_eursc_topic, particle_states, ph_scale
from generators.shared.utils import (
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)

_LEVEL = "eursc"
_SUBJECT = "science"


def _topic_bank(topic):
    """MCQ / typed factories bound to one syllabus slug."""

    def mcq(difficulty, suffix, question, options, answer, solution):
        def _fn():
            return make_problem(
                question,
                solution,
                "Use food-group, kitchen and evidence ideas from the lesson.",
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
                "Check the food science idea and the evidence.",
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


_FF_MCQ, _FF_NUM, _FF_KEY, _FF_ORD, _FF_PICK = _topic_bank("food_formulas")
_WS_MCQ, _WS_NUM, _WS_KEY, _WS_ORD, _WS_PICK = _topic_bank("water_substances")
_HT_MCQ, _HT_NUM, _HT_KEY, _HT_ORD, _HT_PICK = _topic_bank("cooking_heat")
_AC_MCQ, _AC_NUM, _AC_KEY, _AC_ORD, _AC_PICK = _topic_bank("cooking_acid")
_SA_MCQ, _SA_NUM, _SA_KEY, _SA_ORD, _SA_PICK = _topic_bank("cooking_salt")
_FE_MCQ, _FE_NUM, _FE_KEY, _FE_ORD, _FE_PICK = _topic_bank("cooking_fermentation")
_NU_MCQ, _NU_NUM, _NU_KEY, _NU_ORD, _NU_PICK = _topic_bank("nutrition")
_MP_MCQ, _MP_NUM, _MP_KEY, _MP_ORD, _MP_PICK = _topic_bank("healthy_meal_project")

_NUTRIENT_BANK = (
    {"id": "protein", "text": "Protein for growth and repair (beans, fish, eggs)"},
    {"id": "fat", "text": "Fat as a store of energy (oils, nuts, butter)"},
    {"id": "carb", "text": "Carbohydrate for energy (bread, rice, fruit)"},
    {"id": "rumour", "text": "A celebrity diet with no ingredients listed"},
)
_SOURCE_BANK = (
    {"id": "plant", "text": "Beans, oats and vegetable oil from plants"},
    {"id": "animal", "text": "Eggs, yoghurt and fish from animals"},
    {"id": "plastic", "text": "Plastic packaging as a nutrient"},
    {"id": "air", "text": "Air as the main protein source"},
)
_STATE_BANK = (
    {"id": "solid", "text": "Particles packed in a fixed pattern"},
    {"id": "liquid", "text": "Particles touching but able to move past each other"},
    {"id": "gas", "text": "Particles far apart and moving freely"},
    {"id": "empty", "text": "A box with no particles at all"},
)
_PHASE_BANK = (
    {"id": "melt", "text": "Solid to liquid (melting)"},
    {"id": "boil", "text": "Liquid to gas (boiling or evaporation)"},
    {"id": "condense", "text": "Gas to liquid (condensation)"},
    {"id": "invent", "text": "Invent a fourth state by stirring harder"},
)
_SEPARATE_BANK = (
    {"id": "filter", "text": "Filtration for an insoluble solid in a liquid"},
    {"id": "evaporate", "text": "Evaporation to recover a dissolved salt"},
    {"id": "taste", "text": "Taste unknown kitchen chemicals to identify them"},
    {"id": "shake", "text": "Shake until the labels fall off"},
)
_HEAT_BANK = (
    {"id": "conduct", "text": "Conduction through a metal pan"},
    {"id": "convect", "text": "Convection in water or oven air"},
    {"id": "radiate", "text": "Radiation from a grill or hot coals"},
    {"id": "secret", "text": "A secret fourth transfer that cannot be tested"},
)
_COOK_ORDER_BANK = (
    {"id": "heat", "text": "Supply energy as heat"},
    {"id": "protein", "text": "Protein chains change shape (denature)"},
    {"id": "texture", "text": "The food firms or sets"},
    {"id": "magic", "text": "Ignore temperature and hope"},
)
_ACID_BANK = (
    {"id": "sour", "text": "Sour taste of lemon or vinegar"},
    {"id": "lowph", "text": "pH below 7"},
    {"id": "sweet", "text": "Sweet taste of table sugar"},
    {"id": "ph14", "text": "pH 14 for all foods"},
)
_PRESERVE_BANK = (
    {"id": "acid", "text": "Acid pickle that slows many microbes"},
    {"id": "salt", "text": "Salt drawing water out of microbes"},
    {"id": "dust", "text": "Leaving food uncovered on a warm windowsill"},
    {"id": "guess", "text": "Guessing the date without a method"},
)
_SALT_BANK = (
    {"id": "mineral", "text": "An inorganic mineral (sodium chloride)"},
    {"id": "solution", "text": "Dissolved particles spread through water"},
    {"id": "crystal", "text": "Crystals forming as water evaporates"},
    {"id": "vitamin", "text": "A vitamin made by green leaves in the dark"},
)
_CONC_BANK = (
    {"id": "more", "text": "More salt in the same volume is more concentrated"},
    {"id": "same", "text": "Keep the volume the same when comparing"},
    {"id": "colour", "text": "Choose the pinker pan because it looks nicer"},
    {"id": "secret", "text": "Hide the mass of salt so nobody can check"},
)
_FERMENT_BANK = (
    {"id": "yeast", "text": "Yeast making carbon dioxide that raises dough"},
    {"id": "lactic", "text": "Lactic bacteria making yoghurt or sauerkraut tangy"},
    {"id": "bleach", "text": "Household bleach as a starter culture"},
    {"id": "stone", "text": "A clean stone as the microorganism"},
)
_COND_BANK = (
    {"id": "food", "text": "A food source such as sugar or milk"},
    {"id": "temp", "text": "A suitable temperature, not boiling the culture"},
    {"id": "bleach2", "text": "Soak the mixture in disinfectant first"},
    {"id": "vacuum_forever", "text": "Remove all water forever so nothing can live"},
)
_DEF_BANK = (
    {"id": "scurvy", "text": "Vitamin C lack linked with scurvy"},
    {"id": "anaemia", "text": "Iron lack linked with anaemia"},
    {"id": "rumour", "text": "A rumour that all fruit is poisonous"},
    {"id": "fame", "text": "A famous person skipping breakfast on camera"},
)
_LABEL_BANK = (
    {"id": "energy", "text": "Energy in kJ or kcal per serving"},
    {"id": "ingredients", "text": "An ingredients list in order of amount"},
    {"id": "slogan", "text": "A slogan with no numbers"},
    {"id": "secret", "text": "A method the company will not describe"},
)
_MEAL_BANK = (
    {"id": "plan", "text": "Plan food groups using lesson evidence"},
    {"id": "hygiene", "text": "Wash hands and keep raw meat separate"},
    {"id": "record", "text": "Record what was prepared and the label energy"},
    {"id": "disclose", "text": "Ask classmates to describe their private eating habits"},
)
_PHASE_MEAL_BANK = (
    {"id": "menu", "text": "Choose a menu with more than one food group"},
    {"id": "safety", "text": "Check hygiene and teacher-approved equipment"},
    {"id": "prepare", "text": "Prepare following a written method"},
    {"id": "skip", "text": "Skip the method and plate whatever is left"},
)


def _mcq_opts(a, b, c, d):
    return [f"A  {a}", f"B  {b}", f"C  {c}", f"D  {d}"]


_FF_POOLS = {
    "foundational": [
        _FF_MCQ("foundational", "water", "Why is water listed with the main molecules of food?", _mcq_opts("It is a celebrity ingredient", "Living things and many foods contain it and it acts as a solvent", "It is a protein", "It has no role in cooking"), "B", "Water is the solvent in cells and in many kitchen mixtures."),
        _FF_MCQ("foundational", "protein", "Proteins in food are especially important for", _mcq_opts("only changing the colour of a plate", "growth and repair of the body", "replacing the need to drink water", "making plastic"), "B", "Proteins supply amino acids used in growth and repair."),
        _FF_MCQ("foundational", "fat", "Fats and oils in a diet mainly", _mcq_opts("are never needed", "store a large amount of energy and carry some vitamins", "are the same as table salt", "are a type of metal"), "B", "Fats are energy-rich and some vitamins dissolve in fat."),
        _FF_MCQ("foundational", "carb", "Bread, rice and fruit are useful mainly as sources of", _mcq_opts("plastic", "carbohydrate for energy", "iron nails", "pure water only"), "B", "Starchy foods and fruit supply carbohydrate."),
        _FF_MCQ("foundational", "beans", "Beans and lentils are plant foods that are rich in", _mcq_opts("only table salt", "protein", "helium", "sand"), "B", "Many pulses are protein-rich plant foods."),
        _FF_MCQ("foundational", "animal", "Eggs and yoghurt are examples of", _mcq_opts("plant oils only", "animal-source foods that can supply protein", "pure carbohydrate crystals", "metals"), "B", "Eggs and dairy come from animals and can supply protein."),
        _FF_KEY("foundational", "protein_word", "Write the nutrient group used especially for growth and repair.", "protein", "Protein supports growth and repair."),
        _FF_NUM("foundational", "h2o_h", "Water is written H2O. How many hydrogen atoms are in one water molecule?", 2, "H2O has two hydrogen atoms."),
        _FF_ORD("foundational", "classify", "Order how to classify an unknown food using evidence.", ["protein", "fat", "carb"], _NUTRIENT_BANK, "Use the three nutrient roles; a rumour is not evidence."),
        _FF_PICK("foundational", "real_nutes", "Select the two nutrient groups that are molecules of food in this lesson.", ["protein", "carb"], _NUTRIENT_BANK, 2, "Protein and carbohydrate are food molecules. A rumour is not."),
        _FF_PICK("foundational", "sources", "Select the two lists that are real food sources.", ["plant", "animal"], _SOURCE_BANK, 2, "Plants and animals both contribute nutrients. Plastic and air are not protein sources."),
    ],
    "intermediate": [
        _FF_MCQ("intermediate", "amino", "Proteins are long chains. Cooking can change their shape. That idea is closest to", _mcq_opts("melting metal", "denaturing", "turning protein into helium", "removing all water instantly"), "B", "Heat and acid can denature proteins."),
        _FF_MCQ("intermediate", "oil", "Olive oil is mainly", _mcq_opts("a carbohydrate syrup", "a fat from a plant", "a pure protein powder", "an element on the periodic table"), "B", "Plant oils are fats."),
        _FF_MCQ("intermediate", "starch", "Starch in rice is a", _mcq_opts("type of sand", "carbohydrate", "metal", "noble gas"), "B", "Starch is a carbohydrate."),
        _FF_MCQ("intermediate", "water_role", "In a soup, water is useful as a", _mcq_opts("protein chain", "solvent that carries dissolved flavours and salts", "source of starch crystals only", "way to remove all nutrients"), "B", "Water is the solvent in many foods."),
        _FF_MCQ("intermediate", "balanced_src", "A meal of rice, beans and oil includes", _mcq_opts("only animal foods", "carbohydrate, plant protein and fat", "only metal", "no molecules of food"), "B", "Those three foods cover carb, protein and fat from plants."),
        _FF_MCQ("intermediate", "fish", "Fish can be a source of", _mcq_opts("only table sugar", "protein and some fats", "pure cellulose packaging", "argon"), "B", "Fish is an animal-source protein food and can supply fats."),
        _FF_KEY("intermediate", "carb_word", "Write the nutrient group that includes sugars and starch.", "carbohydrate", "Carbohydrates include sugars and starch."),
        _FF_NUM("intermediate", "fatty_n", "A simple fat model uses 1 glycerol and 3 fatty acids. How many fatty-acid parts is that?", 3, "Three fatty acids join the glycerol."),
        _FF_ORD("intermediate", "check_food", "Order a fair way to decide what a food supplies.", ["protein", "carb", "fat"], _NUTRIENT_BANK, "Check protein, carbohydrate and fat roles with evidence."),
        _FF_PICK("intermediate", "plant_pair", "Select the two items that come from plants in this list.", ["plant", "carb"], (
            {"id": "plant", "text": "Beans, oats and vegetable oil from plants"},
            {"id": "carb", "text": "Carbohydrate for energy (bread, rice, fruit)"},
            {"id": "plastic", "text": "Plastic packaging as a nutrient"},
            {"id": "air", "text": "Air as the main protein source"},
        ), 2, "Plant foods and plant carbohydrates count. Plastic and air do not."),
        _FF_PICK("intermediate", "not_food", "Select the two items that should not be treated as nutrient groups.", ["rumour", "plastic"], (
            {"id": "rumour", "text": "A celebrity diet with no ingredients listed"},
            {"id": "plastic", "text": "Plastic packaging as a nutrient"},
            {"id": "protein", "text": "Protein for growth and repair (beans, fish, eggs)"},
            {"id": "carb", "text": "Carbohydrate for energy (bread, rice, fruit)"},
        ), 2, "Rumour and packaging are not nutrient groups."),
    ],
    "difficult": [
        _FF_MCQ("difficult", "photo", "Green plants can make carbohydrate using light. Animals cannot. That is why", _mcq_opts("animals never need food", "plant foods can supply energy molecules that animals did not build from light", "oil is a metal", "water is a protein"), "B", "Photosynthesis is a plant process; animals eat ready-made food molecules."),
        _FF_MCQ("difficult", "label", "A label lists 'whey protein'. This food is mainly providing", _mcq_opts("sand", "protein from an animal source", "only water", "helium"), "B", "Whey is an animal-source protein."),
        _FF_MCQ("difficult", "oil_energy", "Per gram, fats usually store more energy than carbohydrates. That means", _mcq_opts("fats are never used in cooking", "a small mass of oil can supply a large amount of energy", "bread cannot be food", "water is the most energy-rich nutrient"), "B", "Fats are energy-dense."),
        _FF_MCQ("difficult", "mix", "A vegan kitchen can still supply protein because", _mcq_opts("only meat contains protein", "some plant foods such as beans are protein-rich", "protein is a metal", "air is protein"), "B", "Pulses and some grains supply plant protein."),
        _FF_MCQ("difficult", "water_mass", "100 g of ice melts to liquid water. The mass of water is", _mcq_opts("0 g because ice is not water", "still 100 g; the state changed, not the amount of substance", "200 g", "50 g"), "B", "Melting does not destroy the water molecules."),
        _FF_KEY("difficult", "fat_word", "Write the nutrient group that includes oils and butter.", "fat", "Oils and butter are fats."),
        _FF_NUM("difficult", "groups", "A plate has beans, rice, oil and water. How many of the lesson's three energy/growth nutrient groups (protein, fat, carbohydrate) are represented? Enter a number.", 3, "Beans (protein), oil (fat), rice (carbohydrate)."),
        _FF_ORD("difficult", "source_then", "Order plant source, then animal source, then carbohydrate.", ["plant", "animal", "carb"], (
            {"id": "plant", "text": "Beans, oats and vegetable oil from plants"},
            {"id": "animal", "text": "Eggs, yoghurt and fish from animals"},
            {"id": "carb", "text": "Carbohydrate for energy (bread, rice, fruit)"},
            {"id": "rumour", "text": "A celebrity diet with no ingredients listed"},
        ), "Plant foods, then animal foods, then carbohydrate."),
        _FF_PICK("difficult", "good_pair", "Select the two scientific food facts.", ["protein", "fat"], _NUTRIENT_BANK, 2, "Protein and fat are nutrient groups. A rumour is not."),
        _FF_PICK("difficult", "avoid", "Select the two choices that are not food sources of nutrients.", ["plastic", "air"], _SOURCE_BANK, 2, "Packaging and air are not nutrient sources."),
    ],
}


_FF_STANDARD = {
    "foundational": (
        'food_formulas_foundational_mcq_animal',
        'food_formulas_foundational_keyword_protein_word',
        'food_formulas_foundational_number_h2o_h',
        'food_formulas_foundational_order_classify',
        'food_formulas_foundational_pick_real_nutes',
    ),
    "intermediate": (
        'food_formulas_intermediate_mcq_amino',
        'food_formulas_intermediate_keyword_carb_word',
        'food_formulas_intermediate_number_fatty_n',
        'food_formulas_intermediate_order_check_food',
        'food_formulas_intermediate_pick_not_food',
    ),
    "difficult": (
        'food_formulas_difficult_mcq_label',
        'food_formulas_difficult_keyword_fat_word',
        'food_formulas_difficult_number_groups',
        'food_formulas_difficult_order_source_then',
        'food_formulas_difficult_pick_avoid',
    ),
}
eursc_science_food_formulas, eursc_science_food_formulas_variants = bind_eursc_topic(
    'food_formulas', _FF_POOLS, _FF_STANDARD
)


_WS_POOLS = {
    "foundational": [
        _WS_MCQ("foundational", "solid", "In a solid, particles are usually", _mcq_opts("far apart and independent", "packed in a fixed pattern", "missing", "only in stars"), "B", "Solids have packed, arranged particles."),
        _WS_MCQ("foundational", "liquid", "In a liquid, particles", _mcq_opts("cannot move at all", "touch but can move past each other", "are always ionised", "occupy no volume"), "B", "Liquids flow because particles can move past one another."),
        _WS_MCQ("foundational", "gas", "In a gas, particles are", _mcq_opts("locked in a crystal", "far apart and moving freely", "always a metal", "the same as a solid"), "B", "Gases fill a container because particles are far apart."),
        _WS_MCQ("foundational", "melt", "Ice becoming liquid water is", _mcq_opts("burning", "melting", "a nuclear change", "condensation"), "B", "Solid to liquid is melting."),
        _WS_MCQ("foundational", "mixture", "Salt stirred into water is a", _mcq_opts("new element", "mixture (a solution)", "pure metal", "gas only"), "B", "The salt and water can be separated; it is a mixture."),
        _WS_MCQ("foundational", "filter", "Sand in water is best separated by", _mcq_opts("a magnet only", "filtration", "tasting", "freezing the labels"), "B", "Insoluble sand is trapped by a filter."),
        _WS_KEY("foundational", "solvent", "Write the word for a liquid that dissolves another substance.", "solvent", "Water is a common solvent in food."),
        _WS_NUM("foundational", "ice_mass", "100 g of ice melts completely. What is the mass of liquid water in grams?", 100, "Mass is conserved; only the state changes."),
        _WS_ORD("foundational", "heat_ice", "Order the changes as ice is heated in an open pan.", ["melt", "boil", "condense"], _PHASE_BANK, "Melt, then boil; steam can later condense."),
        _WS_PICK("foundational", "states", "Select the two particle pictures that are condensed states (not a gas).", ["solid", "liquid"], _STATE_BANK, 2, "Solid and liquid particles stay close. Gas particles do not."),
        _WS_MCQ("foundational", "box_gas", "<p>Which labelled box shows particles of a gas?</p>" + str(particle_states()), _mcq_opts("A", "B", "C", "none of them"), "C", "C has particles far apart."),
    ],
    "intermediate": [
        _WS_MCQ("intermediate", "evap", "Puddles disappearing on a warm day is mainly", _mcq_opts("freezing", "evaporation", "filtration", "a new element forming"), "B", "Liquid water becomes vapour below boiling as well."),
        _WS_MCQ("intermediate", "condense", "Steam hitting a cold lid becoming drops is", _mcq_opts("melting", "condensation", "filtration", "burning"), "B", "Gas to liquid is condensation."),
        _WS_MCQ("intermediate", "pure", "A pure substance has", _mcq_opts("a random mix of anything", "only one kind of particle throughout", "to be a metal", "no mass"), "B", "Pure water is one substance; seawater is a mixture."),
        _WS_MCQ("intermediate", "evap_salt", "To recover salt from salty water you can", _mcq_opts("filter out the salt immediately", "evaporate the water so crystals remain", "use a magnet", "taste until it is gone"), "B", "The dissolved salt stays when water evaporates."),
        _WS_MCQ("intermediate", "nonadd", "50 cm3 of water mixed with 50 cm3 of ethanol often gives less than 100 cm3 because", _mcq_opts("mass is destroyed", "particles pack into spaces; volumes are not always additive", "SI units fail", "the liquids turn to gas instantly"), "B", "Different particles can pack; volume need not add."),
        _WS_MCQ("intermediate", "solvent_food", "Sugar disappearing in tea shows water acting as a", _mcq_opts("protein", "solvent", "filter paper", "grill"), "B", "Sugar dissolves in the water."),
        _WS_KEY("intermediate", "mixture_word", "Write the word for two or more substances together that can be separated.", "mixture", "A mixture can be separated by physical methods."),
        _WS_NUM("intermediate", "mass_ice", "50 g of ice melts completely. What is the mass of liquid water in grams?", 50, "Mass is conserved; only the state changes."),
        _WS_ORD("intermediate", "separate", "Order a sensible pair of methods: insoluble sand first, then dissolved salt.", ["filter", "evaporate"], _SEPARATE_BANK, "Filter the sand, then evaporate to get salt."),
        _WS_PICK("intermediate", "unsafe_sep", "Select the two choices that are not laboratory separation methods.", ["taste", "shake"], _SEPARATE_BANK, 2, "Tasting and shaking off labels are not methods."),
        _WS_MCQ("intermediate", "box_solid", "<p>Which labelled box shows a solid?</p>" + str(particle_states(title="States: solid labelled A")), _mcq_opts("A", "B", "C", "the caption only"), "A", "A has packed particles."),
    ],
    "difficult": [
        _WS_MCQ("difficult", "boil_vs", "Boiling happens at a fixed temperature for a pure liquid. Evaporation", _mcq_opts("only happens at that same temperature", "can happen from the surface over a range of temperatures", "is filtration", "destroys mass"), "B", "Evaporation is surface change, not only at the boiling point."),
        _WS_MCQ("difficult", "chrom", "Food-colouring dyes in a drop can be separated by", _mcq_opts("a magnet", "chromatography", "tasting", "ignoring the paper"), "B", "Different dyes travel different distances."),
        _WS_MCQ("difficult", "distil", "To separate alcohol from water in a lab still you use", _mcq_opts("a magnet", "distillation (boiling then condensing)", "filtration of sand only", "guesswork"), "B", "Different boiling points allow distillation."),
        _WS_MCQ("difficult", "pack", "Non-additive volume is evidence that", _mcq_opts("particles do not exist", "particles have size and can pack into gaps", "mass is a feeling", "SI units are optional"), "B", "Particle packing explains the missing volume."),
        _WS_MCQ("difficult", "box_liquid", "<p>Which labelled box is the liquid?</p>" + str(particle_states(title="States: liquid labelled B")), _mcq_opts("A", "B", "C", "none"), "B", "B is the liquid arrangement."),
        _WS_KEY("difficult", "condense_word", "Write the word for gas turning into liquid.", "condensation", "Condensation is gas to liquid."),
        _WS_NUM("difficult", "range_vol", "Two 40 cm3 samples of water mixed give 80 cm3. What volume in cm3 do you record?", 80, "Same substance: volumes of water add in this simple case."),
        _WS_ORD("difficult", "cycle", "Order melt, boil, then condensation in a heating-cooling story.", ["melt", "boil", "condense"], _PHASE_BANK, "Heat melts and boils; cooling vapour condenses."),
        _WS_PICK("difficult", "three_states", "Select the three particle descriptions of solid, liquid and gas.", ["solid", "liquid", "gas"], _STATE_BANK, 3, "The empty box is not a state of matter here."),
        _WS_PICK("difficult", "good_sep", "Select the two valid separation actions.", ["filter", "evaporate"], _SEPARATE_BANK, 2, "Filter and evaporate. Taste and shake are not."),
    ],
}

_WS_STANDARD = {
    "foundational": (
        'water_substances_foundational_mcq_box_gas',
        'water_substances_foundational_keyword_solvent',
        'water_substances_foundational_number_ice_mass',
        'water_substances_foundational_order_heat_ice',
        'water_substances_foundational_pick_states',
    ),
    "intermediate": (
        'water_substances_intermediate_mcq_box_solid',
        'water_substances_intermediate_keyword_mixture_word',
        'water_substances_intermediate_number_mass_ice',
        'water_substances_intermediate_order_separate',
        'water_substances_intermediate_pick_unsafe_sep',
    ),
    "difficult": (
        'water_substances_difficult_mcq_boil_vs',
        'water_substances_difficult_keyword_condense_word',
        'water_substances_difficult_number_range_vol',
        'water_substances_difficult_order_cycle',
        'water_substances_difficult_pick_good_sep',
    ),
}
eursc_science_water_substances, eursc_science_water_substances_variants = bind_eursc_topic(
    'water_substances', _WS_POOLS, _WS_STANDARD
)


_HEAT_NOT = (
    {"id": "conduct", "text": "Conduction through a metal pan"},
    {"id": "convect", "text": "Convection in water or oven air"},
    {"id": "secret", "text": "A secret fourth transfer that cannot be tested"},
    {"id": "magic", "text": "Ignore temperature and hope"},
)

_HT_POOLS = {
    "foundational": [
        _HT_MCQ("foundational", "conduct", "Heat travelling through a metal pan into the food is mainly", _mcq_opts("convection in a solid crystal of air only", "conduction", "a rumour", "filtration"), "B", "Conduction is through the solid pan."),
        _HT_MCQ("foundational", "convect", "Hot water rising and cooler water sinking in a pan is", _mcq_opts("conduction in a vacuum", "convection", "radiation only", "melting of the pan"), "B", "Fluids transfer heat by convection."),
        _HT_MCQ("foundational", "radiate", "A grill browning the top of food without touching it is mainly", _mcq_opts("conduction through a spoon", "radiation", "filtration", "a magnetic field"), "B", "Hot objects radiate infrared."),
        _HT_MCQ("foundational", "oven", "An oven heating the air that then heats the food is mainly", _mcq_opts("conduction through empty space only", "convection", "a chemical named 'ovenium'", "chromatography"), "B", "Moving hot air is convection."),
        _HT_MCQ("foundational", "denature", "An egg white turning from runny to solid when heated is", _mcq_opts("the pan disappearing", "protein denaturing and setting", "only a colour trick", "filtration"), "B", "Heat changes protein shape."),
        _HT_MCQ("foundational", "brown", "Toast turning brown is best described as", _mcq_opts("a reversible melting of metal", "a chemical change in sugars and proteins", "the bread becoming a gas instantly", "filtration"), "B", "Browning is a chemical change."),
        _HT_KEY("foundational", "conduct_word", "Write the word for heat transfer through a solid by particle vibration.", "conduction", "Conduction is through solids in contact."),
        _HT_NUM("foundational", "rise40", "Soup is heated from 20 C to 60 C. By how many degrees Celsius did the temperature rise?", 40, "60 - 20 = 40."),
        _HT_ORD("foundational", "egg", "Order what happens when an egg is heated.", ["heat", "protein", "texture"], _COOK_ORDER_BANK, "Heat, denature, then the texture sets."),
        _HT_PICK("foundational", "three_heat", "Select the three genuine heat-transfer processes.", ["conduct", "convect", "radiate"], _HEAT_BANK, 3, "There is no secret untestable fourth process here."),
        _HT_PICK("foundational", "fluid_heat", "Select the two processes that need a material in this kitchen list.", ["conduct", "convect"], _HEAT_BANK, 2, "Conduction and convection need matter."),
    ],
    "intermediate": [
        _HT_MCQ("intermediate", "wood", "A wooden spoon handle stays cooler than a metal one because wood is a", _mcq_opts("better conductor", "poorer conductor", "type of radiation", "vacuum"), "B", "Wood conducts less well than metal."),
        _HT_MCQ("intermediate", "boil_conv", "Bubbles of steam carrying heat through boiling water are part of", _mcq_opts("conduction in a crystal of ice only", "convection", "a magnetic recipe", "filtration"), "B", "Boiling water is a convection situation."),
        _HT_MCQ("intermediate", "sun", "Feeling heat from glowing charcoal with no contact is", _mcq_opts("conduction through the air as a solid", "radiation", "the charcoal dissolving", "pH"), "B", "Radiation does not need contact."),
        _HT_MCQ("intermediate", "stir", "Stirring soup spreads hot regions. That is mainly", _mcq_opts("radiation from the spoon only", "forced convection", "turning soup into an element", "chromatography"), "B", "Stirring moves the fluid."),
        _HT_MCQ("intermediate", "raw", "Heating minced meat until proteins set is important because", _mcq_opts("it paints the plate", "the texture change is a sign the food has been heated through", "it removes all water always", "it is only for colour"), "B", "Denaturing is a cooking and safety clue."),
        _HT_MCQ("intermediate", "maillard", "Browning on a steak or bread needs", _mcq_opts("only freezing", "heat and food molecules that can react", "a magnet", "pH 14"), "B", "Browning is a heat-driven chemical change."),
        _HT_KEY("intermediate", "convection_word", "Write the word for heat transfer by a moving fluid.", "convection", "Convection is in liquids and gases."),
        _HT_NUM("intermediate", "temps", "A recipe heats soup from 20 C to 80 C. By how many degrees Celsius did the temperature rise?", 60, "80 - 20 = 60."),
        _HT_ORD("intermediate", "methods", "Order conduction, then convection, then radiation as kitchen examples.", ["conduct", "convect", "radiate"], _HEAT_BANK, "Pan, then fluid, then grill."),
        _HT_PICK("intermediate", "not_heat", "Select the two items that are not heat-transfer processes.", ["secret", "magic"], _HEAT_NOT, 2, "Secret and hoping are not heat transfers."),
    ],
    "difficult": [
        _HT_MCQ("difficult", "vacuum", "Radiation can still heat food in a gap with little air because", _mcq_opts("convection always fills every gap", "radiation does not need a material medium", "the food conducts through empty space as a solid", "pH changes"), "B", "Infrared can cross a gap."),
        _HT_MCQ("difficult", "both", "A pan on a hob uses conduction through metal and convection in the sauce. That means", _mcq_opts("only one process is allowed per recipe", "more than one transfer can happen in one cooking method", "radiation is forbidden", "particles do not exist"), "B", "Real cooking combines transfers."),
        _HT_MCQ("difficult", "irreversible", "Denaturing an egg is not reversed by cooling. That shows", _mcq_opts("it was only melting ice", "a chemical/structural change, not a simple state change of water", "mass vanished", "it was filtration"), "B", "The protein does not un-cook by cooling."),
        _HT_MCQ("difficult", "burn", "Black burnt toast has gone beyond useful browning. The scientific point is", _mcq_opts("burning is a further chemical change", "the bread became a metal", "convection stopped existing", "SI units failed"), "B", "Charring is further chemistry, not a desired brown."),
        _HT_MCQ("difficult", "predict", "A thick metal base and a thin wooden handle are chosen because", _mcq_opts("wood conducts better than metal", "metal should conduct into the food; wood should not burn the cook", "radiation cannot exist", "all materials conduct equally"), "B", "Match conductivity to the job."),
        _HT_KEY("difficult", "radiation_word", "Write the word for heat transfer by infrared from a hot object.", "radiation", "Grills and embers radiate."),
        _HT_NUM("difficult", "rise2", "Water is heated from 18 C to 100 C. What is the temperature rise in degrees Celsius?", 82, "100 - 18 = 82."),
        _HT_ORD("difficult", "cook_chain", "Order heat supply, protein change, then texture change.", ["heat", "protein", "texture"], _COOK_ORDER_BANK, "Do not skip to hoping."),
        _HT_PICK("difficult", "real_three", "Select the three kitchen heat transfers.", ["conduct", "convect", "radiate"], _HEAT_BANK, 3, "The secret process is not used."),
        _HT_PICK("difficult", "egg_keep", "Select the two steps that belong in heating an egg.", ["heat", "protein"], _COOK_ORDER_BANK, 2, "Heat and denature. Magic hoping does not."),
    ],
}

_HT_STANDARD = {
    "foundational": (
        'cooking_heat_foundational_mcq_brown',
        'cooking_heat_foundational_keyword_conduct_word',
        'cooking_heat_foundational_number_rise40',
        'cooking_heat_foundational_order_egg',
        'cooking_heat_foundational_pick_fluid_heat',
    ),
    "intermediate": (
        'cooking_heat_intermediate_mcq_boil_conv',
        'cooking_heat_intermediate_keyword_convection_word',
        'cooking_heat_intermediate_number_temps',
        'cooking_heat_intermediate_order_methods',
        'cooking_heat_intermediate_pick_not_heat',
    ),
    "difficult": (
        'cooking_heat_difficult_mcq_both',
        'cooking_heat_difficult_keyword_radiation_word',
        'cooking_heat_difficult_number_rise2',
        'cooking_heat_difficult_order_cook_chain',
        'cooking_heat_difficult_pick_egg_keep',
    ),
}
eursc_science_cooking_heat, eursc_science_cooking_heat_variants = bind_eursc_topic(
    'cooking_heat', _HT_POOLS, _HT_STANDARD
)


_AC_POOLS = {
    "foundational": [
        _AC_MCQ("foundational", "sour", "Lemon juice tastes sour mainly because it is", _mcq_opts("an alkali with pH 14", "acidic", "pure table salt", "a metal"), "B", "Many sour foods are acids."),
        _AC_MCQ("foundational", "ph", "A pH of 3 compared with pH 7 is", _mcq_opts("more alkaline", "more acidic", "exactly the same", "not a number"), "B", "Lower pH is more acidic."),
        _AC_MCQ("foundational", "ind", "An indicator is used to", _mcq_opts("heat the food by radiation only", "show whether a mixture is acid or alkali by a colour change", "filter sand", "measure mass"), "B", "Indicators change colour with pH."),
        _AC_MCQ("foundational", "vinegar", "Vinegar on fish that firms the flesh is using acid to", _mcq_opts("turn the fish into a gas", "denature proteins without much heat", "add a metal coating", "remove all water instantly"), "B", "Acid can denature proteins, as in some raw-cured dishes."),
        _AC_MCQ("foundational", "pickle", "Acid in a pickle helps preservation because it", _mcq_opts("feeds every microbe equally", "makes conditions harder for many spoilage microbes", "removes the need for a lid ever", "is a protein powder"), "B", "Low pH slows many microbes."),
        _AC_MCQ("foundational", "scale", "<p>On this pH scale, which letter is the alkali side?</p>" + str(ph_scale()), _mcq_opts("A", "B", "C", "the word acid"), "C", "C is labelled alkali."),
        _AC_KEY("foundational", "acid_word", "Write the word for a substance with pH below 7 that often tastes sour.", "acid", "Acids have pH below 7."),
        _AC_NUM("foundational", "ph_neutral", "On the 0 to 14 pH scale, which number is used for a neutral solution such as pure water?", 7, "Neutral is pH 7."),
        _AC_ORD("foundational", "test", "Order sour check, then pH idea, when testing a kitchen liquid.", ["sour", "lowph"], _ACID_BANK, "Sour taste is a clue; pH confirms acid."),
        _AC_PICK("foundational", "acid_clues", "Select the two clues that a food is acidic.", ["sour", "lowph"], _ACID_BANK, 2, "Sour and pH below 7. Sweet and pH 14 are not."),
        _AC_PICK("foundational", "preserve_ok", "Select the two preservation ideas from this unit.", ["acid", "salt"], _PRESERVE_BANK, 2, "Acid pickle and salt. Dust and guessing are not."),
    ],
    "intermediate": [
        _AC_MCQ("intermediate", "seven", "Pure water is close to pH", _mcq_opts("0", "7", "14", "100"), "B", "Neutral is around pH 7."),
        _AC_MCQ("intermediate", "alk", "Baking soda mixture that is not sour is likely", _mcq_opts("strongly acidic", "alkaline (pH above 7)", "a carbohydrate crystal only", "a gas at pH 0"), "B", "Alkalis have pH above 7."),
        _AC_MCQ("intermediate", "redcab", "Red cabbage juice changing colour in vinegar is acting as", _mcq_opts("a grill", "an indicator", "a protein chain", "a filter for sand"), "B", "Plant juices can be indicators."),
        _AC_MCQ("intermediate", "cook", "Acid cooking (for example citrus on fish) mainly", _mcq_opts("uses radiation from the Moon", "changes protein texture without a hot pan", "turns fish into salt crystals instantly", "is the same as frying in oil"), "B", "Acid denatures proteins."),
        _AC_MCQ("intermediate", "jar", "A sealed acid pickle still needs clean jars because", _mcq_opts("acid makes hygiene optional", "unwanted microbes on dirty tools can still spoil food", "pH is a feeling", "glass cannot be cleaned"), "B", "Acid helps but does not replace hygiene."),
        _AC_MCQ("intermediate", "ph_a", "<p>Which letter marks the acid side of the scale?</p>" + str(ph_scale(title="pH: acid labelled A")), _mcq_opts("A", "B", "C", "none"), "A", "A is the acid side."),
        _AC_KEY("intermediate", "indicator", "Write the word for a dye that changes colour with acid or alkali.", "indicator", "Indicators report pH by colour."),
        _AC_NUM("intermediate", "ph7", "What pH number is used for a neutral solution such as pure water?", 7, "Neutral is pH 7."),
        _AC_ORD("intermediate", "pickle_steps", "Order acid clue then preservation.", ["lowph", "acid"], (
            {"id": "lowph", "text": "pH below 7"},
            {"id": "acid", "text": "Acid pickle that slows many microbes"},
            {"id": "sweet", "text": "Sweet taste of table sugar"},
            {"id": "dust", "text": "Leaving food uncovered on a warm windowsill"},
        ), "Confirm acid, then use it to preserve."),
        _AC_PICK("intermediate", "not_acid", "Select the two items that are not acid clues.", ["sweet", "ph14"], _ACID_BANK, 2, "Sweet and pH 14 are not acid clues."),
    ],
    "difficult": [
        _AC_MCQ("difficult", "compare", "pH 2 lemon juice compared with pH 5 tomato is", _mcq_opts("less acidic", "more acidic", "alkaline", "not a measurement"), "B", "Smaller pH is more acidic."),
        _AC_MCQ("difficult", "neutralise", "Mixing a kitchen acid with a kitchen alkali can move pH toward 7. That is", _mcq_opts("filtration of sand", "neutralisation", "convection in a vacuum", "a rumour"), "B", "Acid and alkali can cancel toward neutral."),
        _AC_MCQ("difficult", "limit", "Acid preservation has limits because", _mcq_opts("all microbes love acid equally", "some microbes tolerate acid, so hygiene and sealing still matter", "pH cannot be measured", "glass always melts"), "B", "Acid is a control, not a magic shield."),
        _AC_MCQ("difficult", "ph_b", "<p>Which letter marks pH 7?</p>" + str(ph_scale(title="pH 7 labelled B")), _mcq_opts("A", "B", "C", "the alkali word only"), "B", "B is pH 7."),
        _AC_MCQ("difficult", "safety", "Tasting unknown laboratory acids is", _mcq_opts("required", "unsafe; use indicators and teacher instructions", "the only way to find pH", "how salt is identified"), "B", "Do not taste lab chemicals."),
        _AC_KEY("difficult", "alkali_word", "Write the word for a substance with pH above 7.", "alkali", "Alkalis have pH above 7."),
        _AC_NUM("difficult", "ph3", "A sauce has pH 3. How many pH units below 7 is that?", 4, "7 - 3 = 4."),
        _AC_ORD("difficult", "test_chain", "Order sour clue, then low pH.", ["sour", "lowph"], _ACID_BANK, "Taste is a clue; pH is the measurement."),
        _AC_PICK("difficult", "keep", "Select the two acid facts.", ["sour", "lowph"], _ACID_BANK, 2, "Sour and pH below 7."),
        _AC_PICK("difficult", "bad_keep", "Select the two poor preservation choices.", ["dust", "guess"], _PRESERVE_BANK, 2, "Uncovered food and guessing dates are poor."),
    ],
}

_AC_STANDARD = {
    "foundational": (
        'cooking_acid_foundational_mcq_ind',
        'cooking_acid_foundational_keyword_acid_word',
        'cooking_acid_foundational_number_ph_neutral',
        'cooking_acid_foundational_order_test',
        'cooking_acid_foundational_pick_acid_clues',
    ),
    "intermediate": (
        'cooking_acid_intermediate_mcq_alk',
        'cooking_acid_intermediate_keyword_indicator',
        'cooking_acid_intermediate_number_ph7',
        'cooking_acid_intermediate_order_pickle_steps',
        'cooking_acid_intermediate_pick_not_acid',
    ),
    "difficult": (
        'cooking_acid_difficult_mcq_compare',
        'cooking_acid_difficult_keyword_alkali_word',
        'cooking_acid_difficult_number_ph3',
        'cooking_acid_difficult_order_test_chain',
        'cooking_acid_difficult_pick_bad_keep',
    ),
}
eursc_science_cooking_acid, eursc_science_cooking_acid_variants = bind_eursc_topic(
    'cooking_acid', _AC_POOLS, _AC_STANDARD
)


_SA_POOLS = {
    "foundational": [
        _SA_MCQ("foundational", "mineral", "Table salt used in cooking is mainly", _mcq_opts("a vitamin made in leaves", "an inorganic mineral (sodium chloride)", "a protein chain", "a carbohydrate syrup"), "B", "Salt is a mineral, not a vitamin."),
        _SA_MCQ("foundational", "solution", "Salt disappearing in water makes a", _mcq_opts("new element", "solution", "pure metal bar", "filter paper"), "B", "The salt dissolves; the mixture is a solution."),
        _SA_MCQ("foundational", "conc", "The same volume of water with more salt is", _mcq_opts("less concentrated", "more concentrated", "no longer a mixture", "a gas"), "B", "Concentration is amount in a volume."),
        _SA_MCQ("foundational", "crystal", "Salt crystals appearing when seawater dries are", _mcq_opts("a new metal from the air", "crystallisation as water evaporates", "filtration of sand only", "radiation"), "B", "The solid salt remains when water leaves."),
        _SA_MCQ("foundational", "preserve", "Salted fish keeps longer mainly because salt", _mcq_opts("paints the fish", "draws water out of many microbes", "is a vitamin C source", "raises pH to 14 always"), "B", "Less available water slows spoilage."),
        _SA_MCQ("foundational", "taste", "A little salt can change flavour. That does not mean", _mcq_opts("it is a mineral", "unlimited salt is automatically healthy", "it can dissolve", "it can form crystals"), "B", "Culinary use is not a health instruction to add as much as possible."),
        _SA_KEY("foundational", "solution_word", "Write the word for a mixture of a dissolved substance in a liquid.", "solution", "Salt water is a solution."),
        _SA_NUM("foundational", "salt_double", "A brine has 3 g of salt in 100 cm3. How many grams are in 200 cm3 of the same brine?", 6, "Twice the volume at the same concentration: 6 g."),
        _SA_ORD("foundational", "make_salt", "Order dissolving, then crystals forming as water leaves.", ["solution", "crystal"], _SALT_BANK, "Dissolve, then crystallise by evaporation."),
        _SA_PICK("foundational", "salt_facts", "Select the two correct salt ideas.", ["mineral", "solution"], _SALT_BANK, 2, "Mineral and solution. Vitamin-from-dark-leaves is not."),
        _SA_PICK("foundational", "conc_ok", "Select the two fair concentration ideas.", ["more", "same"], _CONC_BANK, 2, "More salt in the same volume, compared fairly."),
    ],
    "intermediate": [
        _SA_MCQ("intermediate", "nacl", "The chemical name sodium chloride tells you salt is", _mcq_opts("a living vitamin", "an inorganic compound", "a protein from eggs", "a carbohydrate"), "B", "It is a mineral compound."),
        _SA_MCQ("intermediate", "unseen", "You cannot see salt in a clear brine because", _mcq_opts("the salt has turned into a gas and left", "dissolved particles are too small to see as crystals", "mass was destroyed", "the water is a metal"), "B", "Dissolved particles are mixed at a tiny scale."),
        _SA_MCQ("intermediate", "compare", "5 g of salt in 100 cm3 compared with 2 g in 100 cm3 is", _mcq_opts("less concentrated", "more concentrated", "not a solution", "alkaline by definition"), "B", "Same volume, more salt, higher concentration."),
        _SA_MCQ("intermediate", "evap_pan", "A white crust on a dried pan of brine is", _mcq_opts("plastic", "crystallised salt", "pure protein", "a new element named panium"), "B", "Evaporation leaves the salt."),
        _SA_MCQ("intermediate", "cure", "Curing with salt is preservation because", _mcq_opts("salt is a grill", "microbes need water; salt reduces available water", "salt is carbohydrate", "pH becomes 0 always"), "B", "Water activity falls."),
        _SA_MCQ("intermediate", "fair", "To compare two brines fairly you must", _mcq_opts("change both mass and volume wildly", "keep the compared volume the same or calculate per volume", "taste them in the chemistry lab", "hide the masses"), "B", "Concentration is amount per volume."),
        _SA_KEY("intermediate", "crystal_word", "Write the word for a regular solid forming as a solution dries.", "crystal", "Salt forms crystals."),
        _SA_NUM("intermediate", "grams", "A brine has 5 g of salt in 100 cm3. How many grams are in 200 cm3 of the same brine?", 10, "Twice the volume at the same concentration: 10 g."),
        _SA_ORD("intermediate", "conc_then", "Order the idea of a solution, then crystals.", ["solution", "crystal"], _SALT_BANK, "First dissolved, then solid crystals."),
        _SA_PICK("intermediate", "bad_conc", "Select the two unfair concentration habits.", ["colour", "secret"], _CONC_BANK, 2, "Colour and secrecy are not measurements."),
    ],
    "difficult": [
        _SA_MCQ("difficult", "sat", "No more salt will dissolve in a brine at that temperature. The solution is", _mcq_opts("a gas", "saturated", "a protein foam", "empty of particles"), "B", "Saturated means no more solute dissolves."),
        _SA_MCQ("difficult", "temp", "Warm water often dissolves more salt than cold water. That is why", _mcq_opts("concentration cannot be measured", "you must state the conditions when comparing amounts dissolved", "salt is a vitamin", "volume is always additive with ethanol"), "B", "Solubility depends on temperature."),
        _SA_MCQ("difficult", "mass", "If 8 g of salt dissolves in 100 g of water, the solution mass is about", _mcq_opts("8 g", "108 g", "100 g", "0 g"), "B", "Masses add: 8 + 100 = 108 g."),
        _SA_MCQ("difficult", "osmosis_idea", "Salted cucumber slices go floppy because", _mcq_opts("they turn into metal", "water leaves the cells toward the salt", "radiation cooks them", "pH becomes 14"), "B", "Water is drawn out."),
        _SA_MCQ("difficult", "not_enough", "Salt preservation still needs clean handling because", _mcq_opts("salt sterilises every surface instantly", "some spoilage can still happen if the food is dirty or too wet inside", "crystals are vitamins", "SI units fail"), "B", "Salt helps; it is not complete sterility."),
        _SA_KEY("difficult", "mineral_word", "Write the word for a non-living nutrient such as salt, not a vitamin.", "mineral", "Salt is a mineral."),
        _SA_NUM("difficult", "per_litre", "A brine is 4 g of salt per 100 cm3. How many grams in 250 cm3?", 10, "4 g per 100 cm3 → 10 g in 250 cm3."),
        _SA_ORD("difficult", "story", "Order mineral, solution, then crystal.", ["mineral", "solution", "crystal"], _SALT_BANK, "Salt is a mineral, dissolves, then crystallises."),
        _SA_PICK("difficult", "keep_salt", "Select the two scientific salt descriptions.", ["mineral", "crystal"], _SALT_BANK, 2, "Mineral and crystal. A dark-leaf vitamin story is not."),
        _SA_PICK("difficult", "fair_two", "Select the two rules for comparing concentration.", ["more", "same"], _CONC_BANK, 2, "More solute, same volume basis."),
    ],
}

_SA_STANDARD = {
    "foundational": (
        'cooking_salt_foundational_mcq_conc',
        'cooking_salt_foundational_keyword_solution_word',
        'cooking_salt_foundational_number_salt_double',
        'cooking_salt_foundational_order_make_salt',
        'cooking_salt_foundational_pick_conc_ok',
    ),
    "intermediate": (
        'cooking_salt_intermediate_mcq_compare',
        'cooking_salt_intermediate_keyword_crystal_word',
        'cooking_salt_intermediate_number_grams',
        'cooking_salt_intermediate_order_conc_then',
        'cooking_salt_intermediate_pick_bad_conc',
    ),
    "difficult": (
        'cooking_salt_difficult_mcq_mass',
        'cooking_salt_difficult_keyword_mineral_word',
        'cooking_salt_difficult_number_per_litre',
        'cooking_salt_difficult_order_story',
        'cooking_salt_difficult_pick_fair_two',
    ),
}
eursc_science_cooking_salt, eursc_science_cooking_salt_variants = bind_eursc_topic(
    'cooking_salt', _SA_POOLS, _SA_STANDARD
)


_FE_POOLS = {
    "foundational": [
        _FE_MCQ("foundational", "micro", "Fermentation in food uses", _mcq_opts("only magnets", "microorganisms such as yeast or bacteria", "pure helium", "sand filters only"), "B", "Living microbes change the food."),
        _FE_MCQ("foundational", "yeast", "Yeast in bread dough mainly produces", _mcq_opts("table salt crystals", "carbon dioxide that makes the dough rise", "iron nails", "a vacuum"), "B", "CO2 bubbles raise dough; some alcohol also forms."),
        _FE_MCQ("foundational", "lactic", "Yoghurt tang is often from", _mcq_opts("a grill only", "lactic bacteria acting on milk", "pure sodium metal", "chromatography paper"), "B", "Lactic fermentation acidifies milk."),
        _FE_MCQ("foundational", "useful", "Fermentation can be called useful spoilage because", _mcq_opts("all microbes are equally dangerous always", "chosen microbes change food in a controlled way we want", "it removes the need for hygiene", "it is filtration"), "B", "Control and choice of microbe matter."),
        _FE_MCQ("foundational", "need", "Yeast needs a food source such as", _mcq_opts("sand", "sugar", "argon", "a magnet"), "B", "Yeast respires sugars."),
        _FE_MCQ("foundational", "unsafe", "Leaving meat warm for days with no plan is", _mcq_opts("the same as yoghurt making", "uncontrolled spoilage, not a kitchen fermentation method", "distillation", "pH 7 by definition"), "B", "Wanted ferments are planned and hygienic."),
        _FE_KEY("foundational", "yeast_word", "Write the word for the microorganism that raises bread dough.", "yeast", "Yeast produces gas in dough."),
        _FE_NUM("foundational", "rest_min", "Dough rests 30 minutes, then another 30 minutes. Total rest time in minutes?", 60, "30 + 30 = 60."),
        _FE_ORD("foundational", "bread", "Order food for the microbe, then a suitable temperature.", ["food", "temp"], _COND_BANK, "Give sugar/milk and do not boil the culture."),
        _FE_PICK("foundational", "good_micro", "Select the two useful food microbes in this lesson.", ["yeast", "lactic"], _FERMENT_BANK, 2, "Yeast and lactic bacteria. Bleach and stones are not starters."),
        _FE_PICK("foundational", "need_two", "Select the two conditions microorganisms need in this list.", ["food", "temp"], _COND_BANK, 2, "Food and a suitable temperature."),
    ],
    "intermediate": [
        _FE_MCQ("intermediate", "alcohol", "Yeast can produce alcohol as well as carbon dioxide. That is why", _mcq_opts("all bread is a distilled spirit", "some ferments are used for drinks as well as dough", "yeast is a metal", "pH is always 14"), "B", "Alcoholic fermentation is a yeast pathway."),
        _FE_MCQ("intermediate", "sauerkraut", "Cabbage becoming sauerkraut is mainly", _mcq_opts("frying by radiation only", "lactic bacterial fermentation", "crystallising salt into a vitamin", "filtration of sand"), "B", "Lactic bacteria ferment the cabbage."),
        _FE_MCQ("intermediate", "control", "A controlled ferment uses", _mcq_opts("any dirt from the floor", "clean tools, a known starter or method, and sensible time/temperature", "bleach as food", "boiling the live culture for hours first"), "B", "Control is hygiene plus conditions."),
        _FE_MCQ("intermediate", "co2", "Bubbles in a fermenting juice are often", _mcq_opts("argon from the table", "carbon dioxide from respiration of the microbe", "table salt vapour", "iron"), "B", "CO2 is a fermentation product."),
        _FE_MCQ("intermediate", "too_hot", "Boiling a yoghurt culture before it works would", _mcq_opts("always improve flavour", "kill the bacteria you wanted", "turn milk into a metal", "be required for all ferments"), "B", "Live cultures die if overheated."),
        _FE_MCQ("intermediate", "spoil", "Unwanted mould on bread is", _mcq_opts("the same as baker's yeast working as planned", "a different, often unwanted, microbial growth", "a mineral crystal", "pH paper"), "B", "Not all microbes are the chosen starter."),
        _FE_KEY("intermediate", "ferment_word", "Write the word for using microbes to change food in a controlled way.", "fermentation", "Fermentation is controlled microbial change."),
        _FE_NUM("intermediate", "days", "A yoghurt method says keep warm for 8 hours. How many hours is that?", 8, "Follow the stated time."),
        _FE_ORD("intermediate", "plan_fe", "Order a food source for the microbe, then temperature.", ["food", "temp"], _COND_BANK, "Feed them, keep them warm enough, not boiling."),
        _FE_PICK("intermediate", "bad_start", "Select the two things that are not food fermentation starters.", ["bleach", "stone"], _FERMENT_BANK, 2, "Bleach and stones are not cultures."),
    ],
    "difficult": [
        _FE_MCQ("difficult", "anaerobic", "Alcoholic fermentation by yeast happens without needing extra oxygen. That is why", _mcq_opts("dough cannot rise in a bowl", "a covered vat can still produce CO2 and alcohol", "yeast is a plant making starch from light only", "mass disappears"), "B", "Fermentation is anaerobic respiration in this context."),
        _FE_MCQ("difficult", "acid_keep", "Lactic acid from bacteria helps preservation because it", _mcq_opts("raises pH to 14", "lowers pH so many spoilers grow less well", "is a metal coating", "removes the need for clean jars"), "B", "Acid from the ferment is a preservative."),
        _FE_MCQ("difficult", "compete", "A good starter culture can outcompete spoilers if", _mcq_opts("hygiene is ignored", "it is present in useful numbers and conditions suit it", "bleach is the food", "the mixture is boiled after adding live yoghurt"), "B", "Numbers and conditions matter."),
        _FE_MCQ("difficult", "evidence", "To show a bread ferment worked you could record", _mcq_opts("a rumour that dough is lucky", "rise in volume or visible bubbles with a method another group can repeat", "the baker's fame", "a secret step"), "B", "Public, checkable evidence."),
        _FE_MCQ("difficult", "not_replace", "A classroom yoghurt still needs teacher risk assessment because", _mcq_opts("science pages replace the kitchen", "live cultures, temperature and hygiene are practical work", "pH cannot be discussed", "milk is a metal"), "B", "The page does not replace the practical."),
        _FE_KEY("difficult", "bacteria_word", "Write the word for the group of microbes used in yoghurt (lactic ___).", "bacteria", "Lactic bacteria."),
        _FE_NUM("difficult", "hours2", "Dough rests 45 minutes, then another 45 minutes. Total rest time in minutes?", 90, "45 + 45 = 90."),
        _FE_ORD("difficult", "cond_order", "Order food source then temperature for a culture.", ["food", "temp"], _COND_BANK, "Do not disinfect the mixture as food."),
        _FE_PICK("difficult", "useful_pair", "Select the two useful ferments.", ["yeast", "lactic"], _FERMENT_BANK, 2, "Yeast and lactic bacteria."),
        _FE_PICK("difficult", "kill_pair", "Select the two actions that would stop a live culture working.", ["bleach2", "vacuum_forever"], _COND_BANK, 2, "Disinfectant and removing all water are not culture conditions."),
    ],
}

_FE_STANDARD = {
    "foundational": (
        'cooking_fermentation_foundational_mcq_lactic',
        'cooking_fermentation_foundational_keyword_yeast_word',
        'cooking_fermentation_foundational_number_rest_min',
        'cooking_fermentation_foundational_order_bread',
        'cooking_fermentation_foundational_pick_good_micro',
    ),
    "intermediate": (
        'cooking_fermentation_intermediate_mcq_alcohol',
        'cooking_fermentation_intermediate_keyword_ferment_word',
        'cooking_fermentation_intermediate_number_days',
        'cooking_fermentation_intermediate_order_plan_fe',
        'cooking_fermentation_intermediate_pick_bad_start',
    ),
    "difficult": (
        'cooking_fermentation_difficult_mcq_acid_keep',
        'cooking_fermentation_difficult_keyword_bacteria_word',
        'cooking_fermentation_difficult_number_hours2',
        'cooking_fermentation_difficult_order_cond_order',
        'cooking_fermentation_difficult_pick_kill_pair',
    ),
}
eursc_science_cooking_fermentation, eursc_science_cooking_fermentation_variants = bind_eursc_topic(
    'cooking_fermentation', _FE_POOLS, _FE_STANDARD
)


_CLAIM_BANK = (
    {"id": "energy", "text": "Energy in kJ or kcal per serving"},
    {"id": "ingredients", "text": "An ingredients list in order of amount"},
    {"id": "slogan", "text": "A slogan with no numbers"},
    {"id": "secret", "text": "A method the company will not describe"},
)

_NU_POOLS = {
    "foundational": [
        _NU_MCQ("foundational", "balanced", "A balanced diet means", _mcq_opts("only one food group at every meal", "a mix of food groups over time so the body gets what it needs", "never drinking water", "only packaged snacks"), "B", "Balance is variety across groups, not a single magic food."),
        _NU_MCQ("foundational", "scurvy", "A lack of vitamin C has been linked with", _mcq_opts("being famous", "scurvy", "turning into a metal", "pH 14"), "B", "Named deficiencies map to named nutrients."),
        _NU_MCQ("foundational", "allergy", "A food allergy is mainly", _mcq_opts("disliking a colour", "an immune system reaction that can be serious", "the same as choosing not to eat bread", "a marketing slogan"), "B", "Allergy is immune, not a preference."),
        _NU_MCQ("foundational", "intol", "A food intolerance is mainly", _mcq_opts("the immune system making antibodies as in allergy", "difficulty digesting a food, often unpleasant but a different mechanism from allergy", "a vitamin name", "a type of grill"), "B", "Intolerance is not the same as allergy."),
        _NU_MCQ("foundational", "label_e", "A food label's energy value is usually given in", _mcq_opts("metres", "kilojoules or kilocalories", "amperes", "decibels"), "B", "Energy on packs is kJ or kcal."),
        _NU_MCQ("foundational", "add", "Additives are listed so that", _mcq_opts("companies can hide them", "people can see extra ingredients and their job, such as colour or preserve", "SI units fail", "the food becomes a metal"), "B", "Labels make additives public."),
        _NU_KEY("foundational", "allergy_word", "Write the word for an immune reaction to a food that can be serious.", "allergy", "Allergy is immune."),
        _NU_NUM("foundational", "kcal_kj", "This course treats 1 kcal as 4 kJ. How many kJ are in 50 kcal?", 200, "50 × 4 = 200 kJ."),
        _NU_ORD("foundational", "read_label", "Order energy information, then the ingredients list, when checking a pack.", ["energy", "ingredients"], _LABEL_BANK, "Read energy and ingredients. A slogan is not enough."),
        _NU_PICK("foundational", "def_pair", "Select the two nutrient-deficiency links.", ["scurvy", "anaemia"], _DEF_BANK, 2, "Vitamin C–scurvy and iron–anaemia. Rumour and fame are not."),
        _NU_PICK("foundational", "label_ok", "Select the two useful label facts.", ["energy", "ingredients"], _LABEL_BANK, 2, "Energy and ingredients. Slogan and secrecy are not."),
    ],
    "intermediate": [
        _NU_MCQ("intermediate", "iron", "Iron lack is linked with", _mcq_opts("scurvy only", "anaemia", "being a better conductor", "pH paper"), "B", "Iron is needed for healthy blood."),
        _NU_MCQ("intermediate", "vitd", "Vitamin D supports bones. A diet with little of it may need", _mcq_opts("a secret supplement with no label", "evidence-based advice from a qualified professional, not a classmate diagnosis", "ignoring all labels", "adding bleach"), "B", "Class work does not diagnose a pupil."),
        _NU_MCQ("intermediate", "swell", "Sam's lips swell after peanuts and a teacher calls for medical help. This is treated as", _mcq_opts("a marketing claim", "a possible serious allergy", "intolerance only, so it can be ignored", "a balanced diet"), "B", "Swelling after a food is an emergency-style allergy clue in a scenario."),
        _NU_MCQ("intermediate", "lactose", "Lee gets stomach pain after a large glass of milk but no swelling. This is closer to", _mcq_opts("an advert", "intolerance than to a typical severe allergy", "scurvy", "conduction"), "B", "Digestive discomfort without immune swelling is often discussed as intolerance."),
        _NU_MCQ("intermediate", "obesity", "Obesity is discussed in science as", _mcq_opts("a joke about a classmate", "a health condition linked with energy intake and health risks, using third-person evidence", "a moral failing to debate in public", "a food group"), "B", "Keep it clinical and general, never about a named pupil."),
        _NU_MCQ("intermediate", "disorder", "Eating disorders are", _mcq_opts("a quiz to see who in the class has one", "health conditions that need qualified care; a teacher or health professional is the right contact, not a lesson confession", "cured by a slogan", "the same as disliking broccoli"), "B", "No first-person disclosure. Signpost care."),
        _NU_KEY("intermediate", "intolerance_word", "Write the word for difficulty digesting a food that is not the same as allergy.", "intolerance", "Intolerance is digestive, not the same immune mechanism."),
        _NU_NUM("intermediate", "kj", "This course treats 1 kcal as 4 kJ. How many kJ are in 200 kcal?", 800, "200 × 4 = 800 kJ."),
        _NU_ORD("intermediate", "claim_check", "Order the useful label checks: energy, then ingredients.", ["energy", "ingredients"], _LABEL_BANK, "Numbers and the list beat a slogan."),
        _NU_PICK("intermediate", "not_evidence", "Select the two items that are not scientific food evidence.", ["rumour", "fame"], _DEF_BANK, 2, "Rumour and fame are not nutrient evidence."),
    ],
    "difficult": [
        _NU_MCQ("difficult", "kcal", "Using 1 kcal = 4 kJ, 840 kJ is how the pack might also show about", _mcq_opts("840 kcal", "210 kcal", "4 kcal", "0 kcal"), "B", "840 / 4 = 210 kcal."),
        _NU_MCQ("difficult", "serving", "A pack says 500 kJ per serving and the person eats two servings. Energy taken in is", _mcq_opts("250 kJ", "1000 kJ", "500 kcal exactly always", "0"), "B", "Two servings: 1000 kJ."),
        _NU_MCQ("difficult", "claim", "A drink advert says 'boosts energy' with no test. A scientific response is", _mcq_opts("believe the fame of the actor", "ask for the measurements and a controlled comparison", "ban all drinks", "ignore kJ on the label forever"), "B", "Claims need public evidence."),
        _NU_MCQ("difficult", "e_number", "An E-number on a European label is", _mcq_opts("a secret code with no meaning", "an additive with an official number so it can be identified", "a vitamin C deficiency", "a cooking method"), "B", "Additives are listed so they can be checked."),
        _NU_MCQ("difficult", "balance_e", "Energy in greater than energy used over a long time can contribute to", _mcq_opts("scurvy automatically", "weight gain; science describes this without mocking a person", "turning food into helium", "pH 0"), "B", "Energy balance is a general model, not a classroom weigh-in."),
        _NU_MCQ("difficult", "help", "If a fictional character in a scenario shows signs of an eating disorder, the lesson answer is to", _mcq_opts("diagnose them in the quiz comments", "tell a teacher or qualified professional; do not collect classmates' private eating stories", "post about it for fame", "ignore it because science never deals with health"), "B", "Signpost. Do not solicit disclosure."),
        _NU_KEY("difficult", "kilojoule", "Write the energy unit on many European food labels (kJ in words: kilojoule).", "kilojoule", "Kilojoule is the SI-related food energy unit on packs."),
        _NU_NUM("difficult", "two_serv", "A yoghurt is 150 kJ per serving. Three servings are how many kJ?", 450, "3 × 150 = 450."),
        _NU_ORD("difficult", "pack", "Order energy, then ingredients, when judging a marketing claim.", ["energy", "ingredients"], _LABEL_BANK, "Use the numbers and the list."),
        _NU_PICK("difficult", "useful_pack", "Select the two pieces of pack information that can be checked.", ["energy", "ingredients"], _LABEL_BANK, 2, "Energy and ingredients are evidence. Slogan and secrecy are not."),
    ],
}

_NU_STANDARD = {
    "foundational": (
        'nutrition_foundational_mcq_add',
        'nutrition_foundational_keyword_allergy_word',
        'nutrition_foundational_number_kcal_kj',
        'nutrition_foundational_order_read_label',
        'nutrition_foundational_pick_def_pair',
    ),
    "intermediate": (
        'nutrition_intermediate_mcq_disorder',
        'nutrition_intermediate_keyword_intolerance_word',
        'nutrition_intermediate_number_kj',
        'nutrition_intermediate_order_claim_check',
        'nutrition_intermediate_pick_not_evidence',
    ),
    "difficult": (
        'nutrition_difficult_mcq_balance_e',
        'nutrition_difficult_keyword_kilojoule',
        'nutrition_difficult_number_two_serv',
        'nutrition_difficult_order_pack',
        'nutrition_difficult_pick_useful_pack',
    ),
}
eursc_science_nutrition, eursc_science_nutrition_variants = bind_eursc_topic(
    'nutrition', _NU_POOLS, _NU_STANDARD
)


_MP_POOLS = {
    "foundational": [
        _MP_MCQ("foundational", "plan", "The first phase of the classroom meal project is to", _mcq_opts("skip to plating leftovers", "plan a menu using food-group evidence from the unit", "ask everyone to describe their private eating", "hide the method"), "B", "Plan with evidence, not personal confession."),
        _MP_MCQ("foundational", "hygiene", "Before preparing food you should", _mcq_opts("taste raw meat to check it", "wash hands and keep raw meat separate from ready-to-eat food", "run in the kitchen", "skip the teacher's risk assessment"), "B", "Hygiene is a control."),
        _MP_MCQ("foundational", "method", "A useful method is one that", _mcq_opts("only the original group can remember", "another group could follow", "is kept secret", "has no quantities"), "B", "Reproducible method."),
        _MP_MCQ("foundational", "present", "Presentation in this project means", _mcq_opts("ranking classmates' bodies", "explaining the menu with evidence (groups, labels, hygiene)", "a talent show", "deleting inconvenient steps"), "B", "Communicate the science, not personal habits."),
        _MP_MCQ("foundational", "not_quiz", "This project must not", _mcq_opts("use a written plan", "collect pupils' private diet or health stories as answers", "include a hygiene check", "use food-group ideas"), "B", "No special-category health data."),
        _MP_MCQ("foundational", "groups", "An evidence-based plate should include", _mcq_opts("only one food group always", "more than one food group from the unit", "only packaging", "only slogans"), "B", "Variety is the point of the unit."),
        _MP_KEY("foundational", "hygiene_word", "Write the word for cleanliness habits that reduce microbes on hands and surfaces.", "hygiene", "Hygiene is part of kitchen safety."),
        _MP_NUM("foundational", "menu_kj", "A planned meal label shows 200 kJ plus 100 kJ. Combined energy in kJ?", 300, "200 + 100 = 300 kJ."),
        _MP_ORD("foundational", "phases", "Order menu planning, then safety, then prepare.", ["menu", "safety", "prepare"], _PHASE_MEAL_BANK, "Plan, check safety, then prepare. Do not skip the method."),
        _MP_PICK("foundational", "good_proj", "Select the two project actions that belong.", ["plan", "hygiene"], _MEAL_BANK, 2, "Plan and hygiene. Do not collect private eating stories."),
        _MP_PICK("foundational", "bad_proj", "Select the two actions that do not belong in this classroom project.", ["disclose", "skip"], (
            {"id": "disclose", "text": "Ask classmates to describe their private eating habits"},
            {"id": "skip", "text": "Skip the method and plate whatever is left"},
            {"id": "plan", "text": "Plan food groups using lesson evidence"},
            {"id": "hygiene", "text": "Wash hands and keep raw meat separate"},
        ), 2, "No disclosure, no skipping the method."),
    ],
    "intermediate": [
        _MP_MCQ("intermediate", "label_use", "When choosing a packaged item for the menu, use", _mcq_opts("only the cartoon on the front", "energy and ingredients on the label", "a rumour from social media", "the loudest advert"), "B", "Labels are the evidence."),
        _MP_MCQ("intermediate", "allergy_plan", "If a recipe includes nuts, the group should", _mcq_opts("hide the ingredient", "follow the teacher's allergy and kitchen rules; do not quiz classmates about their medical history in the app", "assume nobody is affected", "replace science with a slogan"), "B", "Teacher manages real allergies. The quiz does not store health data."),
        _MP_MCQ("intermediate", "ferment_opt", "A yoghurt or bread ferment as a side dish is allowed if", _mcq_opts("it is left in a bag on a radiator unsupervised", "the teacher approves time, temperature and hygiene", "bleach is the starter", "the method is secret"), "B", "Optional ferment still needs control."),
        _MP_MCQ("intermediate", "record", "The group should record", _mcq_opts("who they think is 'healthy looking'", "what was prepared, quantities and label energy", "private family recipes they must confess", "nothing"), "B", "Record the product of the classwork."),
        _MP_MCQ("intermediate", "reflect", "Reflection should say", _mcq_opts("which classmate should eat less", "what limited the method and how to improve next time", "a diagnosis of an eating disorder", "that science is only opinions"), "B", "Evaluate the method."),
        _MP_MCQ("intermediate", "replace", "This lesson page", _mcq_opts("replaces the kitchen", "does not replace classroom practical work", "is a medical clinic", "stores health questionnaires"), "B", "Practical work stays in class."),
        _MP_KEY("intermediate", "menu_word", "Write the word for the planned list of dishes before cooking.", "menu", "The menu is the plan."),
        _MP_NUM("intermediate", "groups_n", "A plate has rice, beans, salad and yoghurt. How many different food items are listed?", 4, "Four items."),
        _MP_ORD("intermediate", "full", "Order menu, safety, then prepare.", ["menu", "safety", "prepare"], _PHASE_MEAL_BANK, "Do not skip the method."),
        _MP_PICK("intermediate", "record_pair", "Select the two project actions that produce checkable evidence.", ["plan", "record"], _MEAL_BANK, 2, "Plan and record. Disclosure is not evidence for this course."),
    ],
    "difficult": [
        _MP_MCQ("difficult", "tradeoff", "A menu that is only fried snacks is weak because", _mcq_opts("frying is not a heat transfer", "it does not show food-group balance from the unit", "oil is not a molecule of food", "labels cannot show kJ"), "B", "The project is to apply the unit."),
        _MP_MCQ("difficult", "safety_hot", "Hot oil and knives require", _mcq_opts("running", "teacher-approved controls and no horseplay", "tasting raw meat", "secret methods"), "B", "Safety is part of the rubric."),
        _MP_MCQ("difficult", "repro", "Another group should be able to", _mcq_opts("guess the masses", "repeat the quantities and steps from the write-up", "skip hygiene", "invent the conclusion first"), "B", "Reproducible method."),
        _MP_MCQ("difficult", "claim_meal", "If the group claims the meal is 'low energy', they should", _mcq_opts("shout louder", "show label kJ and serving size", "delete the labels", "ask for medical data from friends"), "B", "Claims need numbers."),
        _MP_MCQ("difficult", "rubric", "Collaboration in the rubric means", _mcq_opts("one person hiding the method", "shared roles and peer checks of hygiene and recording", "ranking bodies", "copying a slogan"), "B", "Work together on the method."),
        _MP_MCQ("difficult", "not_db", "Teacher rubric scores in v1 are", _mcq_opts("uploaded to a grading database in this app", "local/printable classroom judgement only", "based on pupils' private health files", "automatic from a photo of the plate"), "B", "No teacher grading database."),
        _MP_KEY("difficult", "reflection_word", "Write the word for looking back at limits of the method and next steps.", "reflection", "Reflection is evaluation, not confession."),
        _MP_NUM("difficult", "kj_menu", "Two items are 300 kJ and 500 kJ. Combined label energy in kJ?", 800, "300 + 500 = 800."),
        _MP_ORD("difficult", "chain", "Order safety then prepare after the menu is chosen.", ["safety", "prepare"], _PHASE_MEAL_BANK, "Safety before preparing."),
        _MP_PICK("difficult", "phase_three", "Select the three genuine project phases.", ["menu", "safety", "prepare"], _PHASE_MEAL_BANK, 3, "Do not skip the method."),
    ],
}

_MP_STANDARD = {
    "foundational": (
        'healthy_meal_project_foundational_mcq_groups',
        'healthy_meal_project_foundational_keyword_hygiene_word',
        'healthy_meal_project_foundational_number_menu_kj',
        'healthy_meal_project_foundational_order_phases',
        'healthy_meal_project_foundational_pick_bad_proj',
    ),
    "intermediate": (
        'healthy_meal_project_intermediate_mcq_allergy_plan',
        'healthy_meal_project_intermediate_keyword_menu_word',
        'healthy_meal_project_intermediate_number_groups_n',
        'healthy_meal_project_intermediate_order_full',
        'healthy_meal_project_intermediate_pick_record_pair',
    ),
    "difficult": (
        'healthy_meal_project_difficult_mcq_claim_meal',
        'healthy_meal_project_difficult_keyword_reflection_word',
        'healthy_meal_project_difficult_number_kj_menu',
        'healthy_meal_project_difficult_order_chain',
        'healthy_meal_project_difficult_pick_phase_three',
    ),
}
eursc_science_healthy_meal_project, eursc_science_healthy_meal_project_variants = bind_eursc_topic(
    'healthy_meal_project', _MP_POOLS, _MP_STANDARD
)
