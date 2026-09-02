"""S1 Unit 1.2 Food advanced Practice pools (MS / SMS). Isolated from lesson banks.

Eight topics: food_formulas, water_substances, cooking_heat, cooking_acid,
cooking_salt, cooking_fermentation, nutrition, healthy_meal_project.
Three named blueprints per supported topic × tier × mode; foundational MS
stays empty for food_formulas and cooking_acid (matrix —).
"""
import random

from generators.eursc.science_shared import particle_states, ph_scale
from generators.shared.utils import graded_answer_number_fields, make_graded_problem
from models.svg_kit import bar_chart

_LEVEL = "eursc"
_SUBJECT = "science"


def _u12_variant(topic, mode_tag, difficulty, suffix):
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


def _u12_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _u12_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"1|{'|'.join(step_ids)}", bank


def _u12_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f"c{i + 1}" for i in range(len(correct_texts)))
    bank = [{"id": cid, "text": text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"pick|{pick_count}|{'|'.join(correct_ids)}", bank, pick_count


# ---------------------------------------------------------------------------
# food_formulas — multi_step (I, D only)
# ---------------------------------------------------------------------------

_FF_MS_I_MENU_PACKS = (
    {"place": "fictional school canteen", "beans": 1, "rice": 1, "oil": 1},
    {"place": "fictional market stall", "beans": 2, "rice": 1, "oil": 0},
    {"place": "fictional cookery demo", "beans": 1, "rice": 2, "oil": 1},
)


@_u12_variant("food_formulas", "ms", "intermediate", "menu_count_then_groups")
def _food_formulas_intermediate_ms_menu_count_then_groups():
    pack = random.choice(_FF_MS_I_MENU_PACKS)
    groups = pack["beans"] + pack["rice"] + pack["oil"]
    correct = "carbohydrate from rice, protein from beans, fat from oil"
    distractors = (
        "only water molecules with no nutrient groups",
        "a celebrity slogan with no ingredients",
        "plastic packaging as the main nutrient",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional menu card from a {pack['place']} lists "
        f"{pack['beans']} bean dish, {pack['rice']} rice dish and "
        f"{pack['oil']} oil serving.</p>"
        "<p>(i) How many of the lesson's three nutrient groups "
        "(protein, fat, carbohydrate) appear on this card?</p>"
        "<p>(ii) Using that count from (i), this meal supplies</p>"
    )
    solution = (
        f"(i) <strong>{groups}</strong> groups<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count how many nutrient groups are "
        "represented, then match beans, rice and oil to their roles."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (groups, letter),
            ("Number of nutrient groups", "What the meal supplies"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the groups, then choose how beans, rice and oil map.",
        ),
    )


@_u12_variant("food_formulas", "ms", "intermediate", "h2o_atoms_then_solvent")
def _food_formulas_intermediate_ms_h2o_atoms_then_solvent():
    hydrogen = 2
    correct = "a solvent that carries dissolved flavours and salts in food"
    distractors = (
        "a protein chain for growth and repair only",
        "a metal element on the periodic table",
        "a celebrity diet with no listed ingredients",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional food-science poster shows water written H2O.</p>"
        "<p>(i) How many hydrogen atoms are in one water molecule?</p>"
        "<p>(ii) In a soup, using that molecule from (i), water acts as</p>"
    )
    solution = (
        f"(i) <strong>{hydrogen}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the small number after H, then "
        "name water's role when salt and flavour dissolve."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (hydrogen, letter),
            ("Hydrogen atoms in H2O", "Role of water in soup"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count H in H2O, then choose water's role in a mixture.",
        ),
    )


@_u12_variant("food_formulas", "ms", "intermediate", "sources_order_then_pick")
def _food_formulas_intermediate_ms_sources_order_then_pick():
    order_raw, order_bank = _u12_order_field(
        (
            "Plant foods such as beans and oats",
            "Animal foods such as eggs and fish",
            "Carbohydrate energy from bread and rice",
        ),
        ("A rumour with no ingredients listed",),
    )
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Protein for growth and repair",
            "Fat as an energy store",
        ),
        (
            "A celebrity diet with no ingredients",
            "Plastic packaging as a nutrient",
        ),
        2,
    )
    question = (
        "<p>A fictional textbook page lists plant sources, animal sources "
        "and carbohydrate foods.</p>"
        "<p>(i) Order plant source, then animal source, then carbohydrate.</p>"
        "<p>(ii) Using that order from (i), select the two nutrient roles "
        "those sources can supply.</p>"
    )
    solution = (
        "(i) <strong>plant → animal → carbohydrate</strong><br>"
        "(ii) Protein and fat are nutrient roles from those sources."
    )
    hint = (
        "<strong>Key idea:</strong> Order the three source types, then pick "
        "the two nutrient jobs they can provide."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Source order", "Nutrient roles"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the sources, then select two nutrient roles.",
        ),
    )


_FF_MS_D_LABEL_PACKS = (
    {"kcal": 420, "protein_g": 12},
    {"kcal": 250, "protein_g": 8},
    {"kcal": 180, "protein_g": 15},
)


@_u12_variant("food_formulas", "ms", "difficult", "label_kcal_then_protein")
def _food_formulas_difficult_ms_label_kcal_then_protein():
    pack = random.choice(_FF_MS_D_LABEL_PACKS)
    correct = "protein from an animal or plant source on the ingredients list"
    distractors = (
        "pure table salt with no amino acids",
        "helium gas trapped in the wrapper",
        "a rumour that all labels are optional",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public food label shows "
        f"{pack['kcal']} kcal per serving and "
        f"{pack['protein_g']} g protein per serving.</p>"
        "<p>(i) What is the energy per serving in kcal?</p>"
        "<p>(ii) Using that protein mass from the same label, the food is "
        "mainly providing</p>"
    )
    solution = (
        f"(i) <strong>{pack['kcal']}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the kcal value, then interpret "
        "the protein grams as a growth-and-repair nutrient."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["kcal"], letter),
            ("Energy (kcal)", "Main nutrient supplied"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read kcal from the label, then classify the protein.",
        ),
    )


@_u12_variant("food_formulas", "ms", "difficult", "plate_groups_then_photo")
def _food_formulas_difficult_ms_plate_groups_then_photo():
    groups = 3
    correct = (
        "plant foods can supply carbohydrate that animals did not build from light"
    )
    distractors = (
        "animals make carbohydrate directly from sunlight",
        "oil is a metal on the periodic table",
        "water is a protein chain",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional balanced plate has beans, rice, oil and water.</p>"
        "<p>(i) How many of the lesson's three nutrient groups "
        "(protein, fat, carbohydrate) are represented by beans, rice and oil?</p>"
        "<p>(ii) Using that count from (i), photosynthesis explains why</p>"
    )
    solution = (
        f"(i) <strong>{groups}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the three nutrient groups on the "
        "plate, then link plant carbohydrate to photosynthesis."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (groups, letter),
            ("Nutrient groups on plate", "Photosynthesis link"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count groups on the plate, then choose the photosynthesis fact.",
        ),
    )


@_u12_variant("food_formulas", "ms", "difficult", "fatty_count_then_energy")
def _food_formulas_difficult_ms_fatty_count_then_energy():
    fatty_acids = 3
    correct = "a small mass of oil can supply a large amount of energy"
    distractors = (
        "fats never store energy in food",
        "bread cannot contain carbohydrate",
        "water is the most energy-rich nutrient per gram",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional fat model shows 1 glycerol joined to fatty acids.</p>"
        "<p>(i) If the model uses 3 fatty-acid parts, how many fatty acids "
        "are shown?</p>"
        "<p>(ii) Using that model from (i), fats in food mainly mean</p>"
    )
    solution = (
        f"(i) <strong>{fatty_acids}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the fatty-acid parts, then recall "
        "why fats are energy-dense."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (fatty_acids, letter),
            ("Fatty acids in model", "What fats mean in food"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count fatty acids, then choose what fats mean for energy.",
        ),
    )


FOOD_FORMULAS_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _food_formulas_intermediate_ms_menu_count_then_groups,
        _food_formulas_intermediate_ms_h2o_atoms_then_solvent,
        _food_formulas_intermediate_ms_sources_order_then_pick,
    ],
    "difficult": [
        _food_formulas_difficult_ms_label_kcal_then_protein,
        _food_formulas_difficult_ms_plate_groups_then_photo,
        _food_formulas_difficult_ms_fatty_count_then_energy,
    ],
}
# ---------------------------------------------------------------------------
# food_formulas — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_FF_SMS_F_CANTEEN_PACKS = (
    {"place": "fictional school canteen", "beans": 1, "rice": 1, "oil": 1},
    {"place": "fictional market stall", "beans": 2, "rice": 1, "oil": 0},
    {"place": "fictional cookery demo", "beans": 1, "rice": 2, "oil": 1},
)


@_u12_variant("food_formulas", "sms", "foundational", "canteen_groups_then_role")
def _food_formulas_foundational_sms_canteen_groups_then_role():
    pack = random.choice(_FF_SMS_F_CANTEEN_PACKS)
    groups = pack["beans"] + pack["rice"] + pack["oil"]
    correct = "protein from beans, carbohydrate from rice, fat from oil"
    distractors = (
        "only water with no nutrient groups",
        "a celebrity slogan with no ingredients",
        "plastic packaging as the main nutrient",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional menu from a {pack['place']} lists "
        f"{pack['beans']} bean dish, {pack['rice']} rice dish and "
        f"{pack['oil']} oil serving.</p>"
        "<p>(i) How many of the lesson's three nutrient groups "
        "(protein, fat, carbohydrate) appear on this card?</p>"
        "<p>(ii) Using that count from (i), this meal supplies</p>"
    )
    solution = (
        f"(i) <strong>{groups}</strong> groups<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the groups on the card, then map "
        "beans, rice and oil to their nutrient roles."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (groups, letter),
            ("Nutrient groups on card", "What the meal supplies"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count groups, then choose how beans, rice and oil map.",
        ),
    )


@_u12_variant("food_formulas", "sms", "foundational", "poster_h2o_then_solvent")
def _food_formulas_foundational_sms_poster_h2o_then_solvent():
    hydrogen = 2
    correct = "a solvent that carries dissolved flavours and salts in food"
    distractors = (
        "a protein chain for growth only",
        "a metal element on the periodic table",
        "a celebrity diet with no listed ingredients",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional food-science poster shows water written H2O.</p>"
        "<p>(i) How many hydrogen atoms are in one water molecule?</p>"
        "<p>(ii) In soup, using that molecule from (i), water acts as</p>"
    )
    solution = (
        f"(i) <strong>{hydrogen}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read H in H2O, then name water's role "
        "when salt and flavour dissolve."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (hydrogen, letter),
            ("Hydrogen atoms in H2O", "Role of water in soup"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count H in H2O, then choose water's role in a mixture.",
        ),
    )


@_u12_variant("food_formulas", "sms", "foundational", "demo_order_then_pick")
def _food_formulas_foundational_sms_demo_order_then_pick():
    order_raw, order_bank = _u12_order_field(
        (
            "Plant foods such as beans and oats",
            "Animal foods such as eggs and fish",
            "Carbohydrate energy from bread and rice",
        ),
        ("A rumour with no ingredients listed",),
    )
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Protein for growth and repair",
            "Fat as an energy store",
        ),
        (
            "A celebrity diet with no ingredients",
            "Plastic packaging as a nutrient",
        ),
        2,
    )
    question = (
        "<p>A fictional textbook page lists plant sources, animal sources "
        "and carbohydrate foods.</p>"
        "<p>(i) Order plant source, then animal source, then carbohydrate.</p>"
        "<p>(ii) Using that order from (i), select the two nutrient roles "
        "those sources can supply.</p>"
    )
    solution = (
        "(i) <strong>plant → animal → carbohydrate</strong><br>"
        "(ii) Protein and fat are nutrient roles from those sources."
    )
    hint = (
        "<strong>Key idea:</strong> Order the three source types, then pick "
        "two nutrient jobs they can provide."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Source order", "Nutrient roles"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the sources, then select two nutrient roles.",
        ),
    )


_FF_SMS_I_MENU_PACKS = (
    {"kcal": 300, "protein_g": 10},
    {"kcal": 450, "protein_g": 14},
    {"kcal": 220, "protein_g": 6},
)


@_u12_variant("food_formulas", "sms", "intermediate", "menu_kcal_then_group")
def _food_formulas_intermediate_sms_menu_kcal_then_group():
    pack = random.choice(_FF_SMS_I_MENU_PACKS)
    kj = pack["kcal"] * 4
    correct = "protein from an animal or plant source on the ingredients list"
    distractors = (
        "pure table salt with no amino acids",
        "helium gas trapped in the wrapper",
        "a rumour that all labels are optional",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public label shows "
        f"{pack['kcal']} kcal per serving and "
        f"{pack['protein_g']} g protein per serving.</p>"
        "<p>(i) Using 1 kcal = 4 kJ, what is the energy in kJ?</p>"
        "<p>(ii) Using that protein mass from the same label, the food mainly "
        "provides</p>"
    )
    solution = (
        f"(i) {pack['kcal']} × 4 = <strong>{kj}</strong> kJ<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Multiply kcal by 4 for kJ, then interpret "
        "protein grams as a growth-and-repair nutrient."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (kj, letter),
            ("Energy (kJ)", "Main nutrient supplied"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Convert kcal to kJ, then classify the protein.",
        ),
    )


@_u12_variant("food_formulas", "sms", "intermediate", "fatty_count_then_dense")
def _food_formulas_intermediate_sms_fatty_count_then_dense():
    fatty_acids = 3
    correct = "a small mass of oil can supply a large amount of energy"
    distractors = (
        "fats never store energy in food",
        "bread cannot contain carbohydrate",
        "water is the most energy-rich nutrient per gram",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional fat model in a cookery demo shows 1 glycerol joined "
        "to fatty acids.</p>"
        "<p>(i) If the model uses 3 fatty-acid parts, how many fatty acids "
        "are shown?</p>"
        "<p>(ii) Using that model from (i), fats in food mainly mean</p>"
    )
    solution = (
        f"(i) <strong>{fatty_acids}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the fatty-acid parts, then recall "
        "why fats are energy-dense."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (fatty_acids, letter),
            ("Fatty acids in model", "What fats mean in food"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count fatty acids, then choose what fats mean for energy.",
        ),
    )


_FF_SMS_I_PLATE_PACKS = (
    {"starch": "rice"},
    {"starch": "bread"},
    {"starch": "pasta"},
)


@_u12_variant("food_formulas", "sms", "intermediate", "plate_items_then_groups")
def _food_formulas_intermediate_sms_plate_items_then_groups():
    pack = random.choice(_FF_SMS_I_PLATE_PACKS)
    groups = 3
    correct = "carbohydrate for energy"
    distractors = (
        "only helium gas",
        "a metal on the periodic table",
        "plastic packaging as a nutrient",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional balanced plate shows beans, {pack['starch']} and oil.</p>"
        "<p>(i) How many of the lesson's three nutrient groups "
        "(protein, fat, carbohydrate) do those three foods cover?</p>"
        "<p>(ii) Using that count from (i), which group does the starchy "
        f"item ({pack['starch']}) mainly supply?</p>"
    )
    solution = (
        f"(i) <strong>{groups}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count how many nutrient groups appear, "
        "then match the starchy item to carbohydrate."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (groups, letter),
            ("Nutrient groups covered", "Starchy item's main group"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count groups on the plate, then name the starch role.",
        ),
    )


_FF_SMS_D_LABEL_PACKS = (
    {"kj": 840, "kcal_equiv": 210},
    {"kj": 1200, "kcal_equiv": 300},
    {"kj": 600, "kcal_equiv": 150},
)


@_u12_variant("food_formulas", "sms", "difficult", "label_kj_kcal_then_claim")
def _food_formulas_difficult_sms_label_kj_kcal_then_claim():
    pack = random.choice(_FF_SMS_D_LABEL_PACKS)
    correct = (
        "plant foods can supply carbohydrate that animals did not build from light"
    )
    distractors = (
        "animals make carbohydrate directly from sunlight",
        "oil is a metal on the periodic table",
        "water is a protein chain",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public label shows "
        f"{pack['kj']} kJ per serving.</p>"
        "<p>(i) Using 1 kcal = 4 kJ, about how many kcal is that?</p>"
        "<p>(ii) Using that energy figure from (i), photosynthesis explains why</p>"
    )
    solution = (
        f"(i) {pack['kj']} ÷ 4 = <strong>{pack['kcal_equiv']}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Divide kJ by 4 for kcal, then link plant "
        "carbohydrate to photosynthesis."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["kcal_equiv"], letter),
            ("Energy (kcal)", "Photosynthesis link"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Convert kJ to kcal, then choose the photosynthesis fact.",
        ),
    )


@_u12_variant("food_formulas", "sms", "difficult", "vegan_protein_then_pick")
def _food_formulas_difficult_sms_vegan_protein_then_pick():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Protein for growth and repair",
            "Carbohydrate for energy",
        ),
        (
            "A celebrity diet with no ingredients",
            "Plastic packaging as a nutrient",
        ),
        2,
    )
    groups = 3
    question = (
        "<p>A fictional vegan kitchen menu lists beans, rice and oil with "
        "no animal foods.</p>"
        "<p>(i) How many of the lesson's three nutrient groups "
        "(protein, fat, carbohydrate) can still be supplied?</p>"
        "<p>(ii) Using that count from (i), select the two nutrient roles "
        "those plant foods can still provide.</p>"
    )
    solution = (
        f"(i) <strong>{groups}</strong><br>"
        "(ii) Protein and carbohydrate are supplied by beans and rice."
    )
    hint = (
        "<strong>Key idea:</strong> Count groups a plant menu can cover, "
        "then pick protein and carbohydrate roles."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (groups, pick_raw),
            ("Nutrient groups possible", "Nutrient roles"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count groups, then select protein and carbohydrate roles.",
        ),
    )


_FF_SMS_D_ICE_PACKS = (
    {"ice_g": 100},
    {"ice_g": 50},
    {"ice_g": 200},
)


@_u12_variant("food_formulas", "sms", "difficult", "mass_ice_then_groups")
def _food_formulas_difficult_sms_mass_ice_then_groups():
    pack = random.choice(_FF_SMS_D_ICE_PACKS)
    correct = "the state changed but the amount of water substance stayed the same"
    distractors = (
        "the water molecules were destroyed",
        "ice is not water at all",
        "mass always doubles when ice melts",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional food-science demo melts {pack['ice_g']} g of ice "
        "completely to liquid water.</p>"
        "<p>(i) What is the mass of liquid water in grams?</p>"
        "<p>(ii) Using that mass from (i), melting shows that</p>"
    )
    solution = (
        f"(i) <strong>{pack['ice_g']}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Mass is conserved when ice melts; only "
        "the state changes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["ice_g"], letter),
            ("Mass of liquid water (g)", "What melting shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Record the same mass in grams, then choose what melting shows.",
        ),
    )


FOOD_FORMULAS_SMS_POOLS = {
    "foundational": [
        _food_formulas_foundational_sms_canteen_groups_then_role,
        _food_formulas_foundational_sms_poster_h2o_then_solvent,
        _food_formulas_foundational_sms_demo_order_then_pick,
    ],
    "intermediate": [
        _food_formulas_intermediate_sms_menu_kcal_then_group,
        _food_formulas_intermediate_sms_fatty_count_then_dense,
        _food_formulas_intermediate_sms_plate_items_then_groups,
    ],
    "difficult": [
        _food_formulas_difficult_sms_label_kj_kcal_then_claim,
        _food_formulas_difficult_sms_vegan_protein_then_pick,
        _food_formulas_difficult_sms_mass_ice_then_groups,
    ],
}


# ---------------------------------------------------------------------------
# water_substances — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_WS_MS_F_MELT_PACKS = (
    {"ice_g": 50, "place": "fictional freezer demo"},
    {"ice_g": 120, "place": "fictional market ice display"},
    {"ice_g": 80, "place": "fictional cookery lab"},
)


@_u12_variant("water_substances", "ms", "foundational", "melt_mass_then_state")
def _water_substances_foundational_ms_melt_mass_then_state():
    pack = random.choice(_WS_MS_F_MELT_PACKS)
    correct = "liquid water with the same mass as the ice"
    distractors = (
        "no water substance left after melting",
        "a gas with double the mass",
        "a solid salt crystal",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} melts {pack['ice_g']} g of ice "
        "completely.</p>"
        + str(particle_states(title="Fictional ice, water and steam particle boxes"))
        + "<p>(i) What is the mass of liquid water in grams?</p>"
        "<p>(ii) Using that mass from (i), melting shows the beaker now holds</p>"
    )
    solution = (
        f"(i) <strong>{pack['ice_g']}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Mass is conserved when ice melts; only "
        "the particle arrangement changes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["ice_g"], letter),
            ("Mass of liquid water (g)", "What melting shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Record the same mass, then choose what melting shows.",
        ),
    )


_WS_MS_F_MIX_PACKS = (
    {"parts": ("salt", "water"), "n": 2},
    {"parts": ("sugar", "water"), "n": 2},
    {"parts": ("sand", "water"), "n": 2},
)


@_u12_variant("water_substances", "ms", "foundational", "mix_count_then_filter")
def _water_substances_foundational_ms_mix_count_then_filter():
    pack = random.choice(_WS_MS_F_MIX_PACKS)
    correct = "filter paper to trap the insoluble solid"
    distractors = (
        "a magnet to attract dissolved sugar",
        "a thermometer to change the state",
        "a celebrity slogan with no method",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional kitchen jar mixes {pack['parts'][0]} and "
        f"{pack['parts'][1]}.</p>"
        "<p>(i) How many different substances are in this mixture?</p>"
        "<p>(ii) Using that count from (i), to separate an insoluble solid "
        "from water you would use</p>"
    )
    solution = (
        f"(i) <strong>{pack['n']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the substances mixed, then choose "
        "filtration for an insoluble solid."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["n"], letter),
            ("Number of substances", "Separation method"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count substances, then choose filtration.",
        ),
    )


@_u12_variant("water_substances", "ms", "foundational", "states_boxes_then_gas")
def _water_substances_foundational_ms_states_boxes_then_gas():
    states = 3
    correct = "box C, where particles are far apart and move freely"
    distractors = (
        "box A, where particles are packed in a fixed pattern",
        "box B, where particles slide past each other",
        "a celebrity poster with no particle diagram",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional textbook shows ice, water and steam as three particle "
        "boxes.</p>"
        + str(particle_states(title="Fictional solid, liquid and gas particle boxes"))
        + "<p>(i) How many states of matter are shown?</p>"
        "<p>(ii) Using that count from (i), steam is best represented by</p>"
    )
    solution = (
        f"(i) <strong>{states}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count solid, liquid and gas boxes, then "
        "match steam to widely spaced particles."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (states, letter),
            ("States shown", "Steam representation"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the states, then choose the gas box.",
        ),
    )


_WS_MS_I_EVAP_PACKS = (
    {"start_ml": 100, "left_ml": 60},
    {"start_ml": 80, "left_ml": 40},
    {"start_ml": 50, "left_ml": 20},
)


@_u12_variant("water_substances", "ms", "intermediate", "evap_volume_then_gas")
def _water_substances_intermediate_ms_evap_volume_then_gas():
    pack = random.choice(_WS_MS_I_EVAP_PACKS)
    lost = pack["start_ml"] - pack["left_ml"]
    correct = "water particles escape as gas from the liquid surface"
    distractors = (
        "the liquid turns into a solid salt crystal",
        "water molecules are destroyed by heat",
        "a celebrity claim that volume never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional open dish starts with {pack['start_ml']} mL water. "
        f"After heating, {pack['left_ml']} mL remains.</p>"
        "<p>(i) How many millilitres of water evaporated?</p>"
        "<p>(ii) Using that loss from (i), evaporation means</p>"
    )
    solution = (
        f"(i) {pack['start_ml']} − {pack['left_ml']} = "
        f"<strong>{lost}</strong> mL<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract to find evaporated volume, then "
        "link the loss to particles becoming gas."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (lost, letter),
            ("Volume evaporated (mL)", "What evaporation means"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract volumes, then choose what evaporation means.",
        ),
    )


@_u12_variant("water_substances", "ms", "intermediate", "dissolve_order_then_solvent")
def _water_substances_intermediate_ms_dissolve_order_then_solvent():
    order_raw, order_bank = _u12_order_field(
        (
            "Add solute to the solvent",
            "Stir so particles spread through the liquid",
            "Observe a clear homogeneous mixture",
        ),
        ("Boil away the solvent before adding solute",),
    )
    correct = "the liquid that dissolves the solute"
    distractors = (
        "the solid that disappears into the liquid",
        "a metal on the periodic table",
        "a rumour with no ingredients",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional lab card dissolves salt in water.</p>"
        "<p>(i) Order add solute, then stir, then observe a clear mixture.</p>"
        "<p>(ii) In that method from (i), water is</p>"
    )
    solution = (
        "(i) <strong>add → stir → observe</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the dissolving steps, then name "
        "water as the solvent."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Dissolving order", "Role of water"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose water's role.",
        ),
    )


_WS_MS_I_BOIL_PACKS = (
    {"temp_c": 100, "state": "gas (steam)"},
    {"temp_c": 100, "state": "gas (steam)"},
    {"temp_c": 100, "state": "gas (steam)"},
)


@_u12_variant("water_substances", "ms", "intermediate", "boil_temp_then_state")
def _water_substances_intermediate_ms_boil_temp_then_state():
    pack = random.choice(_WS_MS_I_BOIL_PACKS)
    correct = pack["state"]
    distractors = (
        "solid ice at 100 °C",
        "liquid water that never boils",
        "a celebrity poster with no temperature",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional kettle log shows water boiling at 100 °C at sea level.</p>"
        "<p>(i) At what temperature in °C does the log show boiling?</p>"
        "<p>(ii) Using that temperature from (i), the dominant state leaving "
        "the surface is</p>"
    )
    solution = (
        f"(i) <strong>{pack['temp_c']}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the boiling temperature, then name "
        "the gas state at the surface."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["temp_c"], letter),
            ("Boiling temperature (°C)", "State at the surface"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the boiling point, then choose the gas state.",
        ),
    )


_WS_MS_D_VOL_PACKS = (
    {"a_ml": 50, "b_ml": 50, "total_ml": 97},
    {"a_ml": 40, "b_ml": 40, "total_ml": 78},
    {"a_ml": 30, "b_ml": 30, "total_ml": 58},
)


@_u12_variant("water_substances", "ms", "difficult", "non_additive_then_reason")
def _water_substances_difficult_ms_non_additive_then_reason():
    pack = random.choice(_WS_MS_D_VOL_PACKS)
    naive = pack["a_ml"] + pack["b_ml"]
    diff = naive - pack["total_ml"]
    correct = "particles of one liquid fit into spaces between particles of the other"
    distractors = (
        "volume is always exactly additive in every mixture",
        "water molecules are destroyed on mixing",
        "a celebrity claim that 50 + 50 must equal 100",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional mixing demo pours {pack['a_ml']} mL of ethanol and "
        f"{pack['b_ml']} mL of water into one graduated cylinder.</p>"
        "<p>(i) If volumes were simply additive, the total would be how many "
        "millilitres?</p>"
        f"<p>(ii) The cylinder reads {pack['total_ml']} mL. Using the "
        "difference from (i), the non-additive volume happens because</p>"
    )
    solution = (
        f"(i) {pack['a_ml']} + {pack['b_ml']} = <strong>{naive}</strong> mL<br>"
        f"(ii) <strong>{correct}</strong> (difference {diff} mL)"
    )
    hint = (
        "<strong>Key idea:</strong> Add the two volumes first, then explain "
        "why the real reading is slightly lower."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (naive, letter),
            ("Naive total (mL)", "Why volume is not additive"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Add the volumes, then choose why the reading is lower.",
        ),
    )


@_u12_variant("water_substances", "ms", "difficult", "distill_order_then_pure")
def _water_substances_difficult_ms_distill_order_then_pure():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat the mixture so one substance boils",
            "Cool vapour in a condenser to collect liquid",
            "Collect the distillate in a clean receiver",
        ),
        ("Stir forever without heating",),
    )
    correct = "distillation separates by boiling point differences"
    distractors = (
        "filtration removes dissolved salt from water",
        "a magnet attracts dissolved sugar",
        "a rumour that all mixtures are identical",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public lab separates salty water.</p>"
        "<p>(i) Order heat to boil, then condense vapour, then collect "
        "distillate.</p>"
        "<p>(ii) Using that sequence from (i), the method works because</p>"
    )
    solution = (
        "(i) <strong>heat → condense → collect</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the distillation steps, then link "
        "them to different boiling points."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Distillation order", "Why the method works"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose why distillation works.",
        ),
    )


@_u12_variant("water_substances", "ms", "difficult", "heat_chain_then_state")
def _water_substances_difficult_ms_heat_chain_then_state():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Solid ice melts to liquid water",
            "Liquid water boils to steam",
        ),
        (
            "Steam freezes directly to metal",
            "A rumour that states never change",
        ),
        2,
    )
    states = 3
    question = (
        "<p>A fictional heating curve shows ice, then water, then steam.</p>"
        + str(particle_states(title="Fictional heating path through three states"))
        + "<p>(i) How many states appear on this curve?</p>"
        "<p>(ii) Using that count from (i), select the two correct phase "
        "changes when heat is added.</p>"
    )
    solution = (
        f"(i) <strong>{states}</strong><br>"
        "(ii) Melting and boiling are the two correct changes."
    )
    hint = (
        "<strong>Key idea:</strong> Count the states on the curve, then pick "
        "melting and boiling."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (states, pick_raw),
            ("States on curve", "Phase changes"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count states, then select melting and boiling.",
        ),
    )


WATER_SUBSTANCES_MS_POOLS = {
    "foundational": [
        _water_substances_foundational_ms_melt_mass_then_state,
        _water_substances_foundational_ms_mix_count_then_filter,
        _water_substances_foundational_ms_states_boxes_then_gas,
    ],
    "intermediate": [
        _water_substances_intermediate_ms_evap_volume_then_gas,
        _water_substances_intermediate_ms_dissolve_order_then_solvent,
        _water_substances_intermediate_ms_boil_temp_then_state,
    ],
    "difficult": [
        _water_substances_difficult_ms_non_additive_then_reason,
        _water_substances_difficult_ms_distill_order_then_pure,
        _water_substances_difficult_ms_heat_chain_then_state,
    ],
}

# ---------------------------------------------------------------------------
# water_substances — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_WS_SMS_F_ICE_PACKS = (
    {"ice_g": 40, "place": "fictional market freezer"},
    {"ice_g": 75, "place": "fictional cookery school"},
    {"ice_g": 90, "place": "fictional science fair"},
)


@_u12_variant("water_substances", "sms", "foundational", "market_melt_then_same")
def _water_substances_foundational_sms_market_melt_then_same():
    pack = random.choice(_WS_SMS_F_ICE_PACKS)
    correct = "liquid water with the same mass as the ice"
    distractors = (
        "no water substance left after melting",
        "a gas with double the mass",
        "a solid salt crystal",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} melts {pack['ice_g']} g of ice "
        "in a public demo.</p>"
        + str(particle_states(title="Fictional ice melting to liquid water"))
        + "<p>(i) What is the mass of liquid water in grams?</p>"
        "<p>(ii) Using that mass from (i), melting shows the beaker now holds</p>"
    )
    solution = (
        f"(i) <strong>{pack['ice_g']}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Mass is conserved when ice melts; only "
        "the particle arrangement changes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["ice_g"], letter),
            ("Mass of liquid water (g)", "What melting shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Record the same mass, then choose what melting shows.",
        ),
    )


@_u12_variant("water_substances", "sms", "foundational", "jar_mix_then_filter")
def _water_substances_foundational_sms_jar_mix_then_filter():
    n = 2
    correct = "filter paper to trap the insoluble solid"
    distractors = (
        "a magnet to attract dissolved sugar",
        "a thermometer to change the state",
        "a celebrity slogan with no method",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional kitchen jar mixes sand and water for a public display.</p>"
        "<p>(i) How many different substances are in this mixture?</p>"
        "<p>(ii) Using that count from (i), to separate the sand you would use</p>"
    )
    solution = (
        f"(i) <strong>{n}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the substances mixed, then choose "
        "filtration for an insoluble solid."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (n, letter),
            ("Number of substances", "Separation method"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count substances, then choose filtration.",
        ),
    )


@_u12_variant("water_substances", "sms", "foundational", "museum_states_then_gas")
def _water_substances_foundational_sms_museum_states_then_gas():
    states = 3
    correct = "box C, where particles are far apart and move freely"
    distractors = (
        "box A, where particles are packed in a fixed pattern",
        "box B, where particles slide past each other",
        "a celebrity poster with no particle diagram",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional museum exhibit shows ice, water and steam.</p>"
        + str(particle_states(title="Fictional museum particle state display"))
        + "<p>(i) How many states of matter are shown?</p>"
        "<p>(ii) Using that count from (i), steam is best represented by</p>"
    )
    solution = (
        f"(i) <strong>{states}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count solid, liquid and gas boxes, then "
        "match steam to widely spaced particles."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (states, letter),
            ("States shown", "Steam representation"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the states, then choose the gas box.",
        ),
    )


_WS_SMS_I_DISH_PACKS = (
    {"start_ml": 100, "left_ml": 55},
    {"start_ml": 60, "left_ml": 30},
    {"start_ml": 90, "left_ml": 45},
)


@_u12_variant("water_substances", "sms", "intermediate", "dish_evap_then_particles")
def _water_substances_intermediate_sms_dish_evap_then_particles():
    pack = random.choice(_WS_SMS_I_DISH_PACKS)
    lost = pack["start_ml"] - pack["left_ml"]
    correct = "water particles escape as gas from the liquid surface"
    distractors = (
        "the liquid turns into a solid salt crystal",
        "water molecules are destroyed by heat",
        "a celebrity claim that volume never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional open dish at a cookery demo starts with "
        f"{pack['start_ml']} mL water. After heating, {pack['left_ml']} mL "
        "remains.</p>"
        "<p>(i) How many millilitres of water evaporated?</p>"
        "<p>(ii) Using that loss from (i), evaporation means</p>"
    )
    solution = (
        f"(i) {pack['start_ml']} − {pack['left_ml']} = "
        f"<strong>{lost}</strong> mL<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract to find evaporated volume, then "
        "link the loss to particles becoming gas."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (lost, letter),
            ("Volume evaporated (mL)", "What evaporation means"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract volumes, then choose what evaporation means.",
        ),
    )


@_u12_variant("water_substances", "sms", "intermediate", "salt_dissolve_then_solvent")
def _water_substances_intermediate_sms_salt_dissolve_then_solvent():
    order_raw, order_bank = _u12_order_field(
        (
            "Add salt to water",
            "Stir so particles spread through the liquid",
            "Observe a clear homogeneous mixture",
        ),
        ("Boil away the water before adding salt",),
    )
    correct = "the liquid that dissolves the solute"
    distractors = (
        "the solid that disappears into the liquid",
        "a metal on the periodic table",
        "a rumour with no ingredients",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public lab card dissolves salt in water.</p>"
        "<p>(i) Order add salt, then stir, then observe a clear mixture.</p>"
        "<p>(ii) In that method from (i), water is</p>"
    )
    solution = (
        "(i) <strong>add → stir → observe</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the dissolving steps, then name "
        "water as the solvent."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Dissolving order", "Role of water"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose water's role.",
        ),
    )


@_u12_variant("water_substances", "sms", "intermediate", "kettle_boil_then_steam")
def _water_substances_intermediate_sms_kettle_boil_then_steam():
    temp_c = 100
    correct = "gas (steam)"
    distractors = (
        "solid ice at 100 °C",
        "liquid water that never boils",
        "a celebrity poster with no temperature",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional kettle log from a cookery school shows water boiling "
        "at 100 °C.</p>"
        "<p>(i) At what temperature in °C does the log show boiling?</p>"
        "<p>(ii) Using that temperature from (i), the dominant state leaving "
        "the surface is</p>"
    )
    solution = (
        f"(i) <strong>{temp_c}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the boiling temperature, then name "
        "the gas state at the surface."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (temp_c, letter),
            ("Boiling temperature (°C)", "State at the surface"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the boiling point, then choose the gas state.",
        ),
    )


_WS_SMS_D_VOL_PACKS = (
    {"a_ml": 50, "b_ml": 50, "total_ml": 96},
    {"a_ml": 40, "b_ml": 40, "total_ml": 77},
    {"a_ml": 25, "b_ml": 25, "total_ml": 48},
)


@_u12_variant("water_substances", "sms", "difficult", "ethanol_mix_then_fit")
def _water_substances_difficult_sms_ethanol_mix_then_fit():
    pack = random.choice(_WS_SMS_D_VOL_PACKS)
    naive = pack["a_ml"] + pack["b_ml"]
    correct = "particles of one liquid fit into spaces between particles of the other"
    distractors = (
        "volume is always exactly additive in every mixture",
        "water molecules are destroyed on mixing",
        "a celebrity claim that 50 + 50 must equal 100",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public mixing demo pours {pack['a_ml']} mL ethanol and "
        f"{pack['b_ml']} mL water into one cylinder.</p>"
        "<p>(i) If volumes were simply additive, the total would be how many "
        "millilitres?</p>"
        f"<p>(ii) The cylinder reads {pack['total_ml']} mL. Using the naive "
        "total from (i), the lower reading happens because</p>"
    )
    solution = (
        f"(i) {pack['a_ml']} + {pack['b_ml']} = <strong>{naive}</strong> mL<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Add the two volumes first, then explain "
        "why the real reading is slightly lower."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (naive, letter),
            ("Naive total (mL)", "Why volume is not additive"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Add the volumes, then choose why the reading is lower.",
        ),
    )


@_u12_variant("water_substances", "sms", "difficult", "salty_distill_then_pure")
def _water_substances_difficult_sms_salty_distill_then_pure():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat salty water so water boils",
            "Cool vapour in a condenser",
            "Collect the distillate as purer water",
        ),
        ("Stir forever without heating",),
    )
    correct = "distillation separates by boiling point differences"
    distractors = (
        "filtration removes dissolved salt from water",
        "a magnet attracts dissolved sugar",
        "a rumour that all mixtures are identical",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public water-treatment display separates salty water.</p>"
        "<p>(i) Order heat to boil, then condense vapour, then collect "
        "distillate.</p>"
        "<p>(ii) Using that sequence from (i), the method works because</p>"
    )
    solution = (
        "(i) <strong>heat → condense → collect</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the distillation steps, then link "
        "them to different boiling points."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Distillation order", "Why the method works"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose why distillation works.",
        ),
    )


@_u12_variant("water_substances", "sms", "difficult", "curve_pick_then_count")
def _water_substances_difficult_sms_curve_pick_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Solid ice melts to liquid water",
            "Liquid water boils to steam",
        ),
        (
            "Steam freezes directly to metal",
            "A rumour that states never change",
        ),
        2,
    )
    states = 3
    question = (
        "<p>A fictional heating curve poster shows ice, water and steam.</p>"
        + str(particle_states(title="Fictional heating curve particle display"))
        + "<p>(i) How many states appear on this curve?</p>"
        "<p>(ii) Using that count from (i), select the two correct phase "
        "changes when heat is added.</p>"
    )
    solution = (
        f"(i) <strong>{states}</strong><br>"
        "(ii) Melting and boiling are the two correct changes."
    )
    hint = (
        "<strong>Key idea:</strong> Count the states on the curve, then pick "
        "melting and boiling."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (states, pick_raw),
            ("States on curve", "Phase changes"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count states, then select melting and boiling.",
        ),
    )


WATER_SUBSTANCES_SMS_POOLS = {
    "foundational": [
        _water_substances_foundational_sms_market_melt_then_same,
        _water_substances_foundational_sms_jar_mix_then_filter,
        _water_substances_foundational_sms_museum_states_then_gas,
    ],
    "intermediate": [
        _water_substances_intermediate_sms_dish_evap_then_particles,
        _water_substances_intermediate_sms_salt_dissolve_then_solvent,
        _water_substances_intermediate_sms_kettle_boil_then_steam,
    ],
    "difficult": [
        _water_substances_difficult_sms_ethanol_mix_then_fit,
        _water_substances_difficult_sms_salty_distill_then_pure,
        _water_substances_difficult_sms_curve_pick_then_count,
    ],
}

# ---------------------------------------------------------------------------
# cooking_heat — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CH_MS_F_PAN_PACKS = (
    {"method": "frying in a pan", "transfer": "conduction from the hot pan"},
    {"method": "grilling bread", "transfer": "radiation from the grill element"},
    {"method": "simmering soup", "transfer": "convection in the liquid"},
)


@_u12_variant("cooking_heat", "ms", "foundational", "pan_transfer_then_name")
def _cooking_heat_foundational_ms_pan_transfer_then_name():
    pack = random.choice(_CH_MS_F_PAN_PACKS)
    correct = pack["transfer"]
    distractors = (
        "photosynthesis in the saucepan",
        "a magnet attracting dissolved salt",
        "a celebrity slogan with no heat source",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery card describes {pack['method']}.</p>"
        "<p>(i) How many of the lesson's three heat-transfer types "
        "(conduction, convection, radiation) could apply in cooking?</p>"
        "<p>(ii) Using that count from (i), the main transfer in this card is</p>"
    )
    transfers = 3
    solution = (
        f"(i) <strong>{transfers}</strong> types exist in cooking<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Recall the three transfer types, then "
        "match the method to the dominant one."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (transfers, letter),
            ("Heat-transfer types in cooking", "Main transfer here"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count transfer types, then choose the main one.",
        ),
    )


@_u12_variant("cooking_heat", "ms", "foundational", "heat_path_order_then_denature")
def _cooking_heat_foundational_ms_heat_path_order_then_denature():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat transfers to the food",
            "Food temperature rises",
            "Proteins unfold (denature)",
        ),
        ("Food cools before any heat arrives",),
    )
    correct = "the protein structure changes and the food texture alters"
    distractors = (
        "water molecules are destroyed forever",
        "the food becomes a metal element",
        "a rumour that heat has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional egg-cooking poster shows how heat reaches protein.</p>"
        "<p>(i) Order heat transfer, then temperature rise, then denaturing.</p>"
        "<p>(ii) Using that sequence from (i), denaturing means</p>"
    )
    solution = (
        "(i) <strong>heat → temperature rise → denature</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the heat chain, then define "
        "denaturing as protein unfolding."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Heat path order", "What denaturing means"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the heat chain, then choose what denaturing means.",
        ),
    )


@_u12_variant("cooking_heat", "ms", "foundational", "oven_temp_then_brown")
def _cooking_heat_foundational_ms_oven_temp_then_brown():
    pack = random.choice(
        (
            {"temp_c": 180, "minutes": 15},
            {"temp_c": 200, "minutes": 12},
            {"temp_c": 160, "minutes": 20},
        )
    )
    correct = "browning from the Maillard reaction at high surface temperature"
    distractors = (
        "ice forming on the hot surface",
        "photosynthesis in the oven",
        "a rumour that colour never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional oven log bakes bread at {pack['temp_c']} °C for "
        f"{pack['minutes']} minutes until the crust turns brown.</p>"
        "<p>(i) What oven temperature in °C is logged?</p>"
        "<p>(ii) Using that temperature from (i), the brown crust mainly shows</p>"
    )
    solution = (
        f"(i) <strong>{pack['temp_c']}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the oven temperature, then link "
        "browning to surface heating."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["temp_c"], letter),
            ("Oven temperature (°C)", "What browning shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the temperature, then choose what browning shows.",
        ),
    )


_CH_MS_I_GRILL_PACKS = (
    {"distance_cm": 10, "effect": "stronger radiation"},
    {"distance_cm": 20, "effect": "weaker radiation"},
    {"distance_cm": 15, "effect": "moderate radiation"},
)


@_u12_variant("cooking_heat", "ms", "intermediate", "grill_distance_then_radiation")
def _cooking_heat_intermediate_ms_grill_distance_then_radiation():
    pack = random.choice(_CH_MS_I_GRILL_PACKS)
    correct = (
        "radiation decreases with distance from the heat source"
        if pack["distance_cm"] >= 15
        else "radiation is stronger when the food is closer to the grill"
    )
    distractors = (
        "conduction through empty air with no contact",
        "photosynthesis on the grill rack",
        "a rumour that distance has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional grill test places food {pack['distance_cm']} cm from "
        "the element.</p>"
        "<p>(i) Record the distance in centimetres.</p>"
        "<p>(ii) Using that distance from (i), compared with a closer position, "
        "this setup shows that</p>"
    )
    solution = (
        f"(i) <strong>{pack['distance_cm']}</strong> cm<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Note the distance, then relate it to "
        "radiation strength."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["distance_cm"], letter),
            ("Distance (cm)", "Radiation effect"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Record the distance, then choose the radiation effect.",
        ),
    )


@_u12_variant("cooking_heat", "ms", "intermediate", "stir_soup_then_convection")
def _cooking_heat_intermediate_ms_stir_soup_then_convection():
    correct = "convection currents spread heat through the liquid"
    distractors = (
        "radiation through a solid metal spoon only",
        "photosynthesis in the soup",
        "a rumour that stirring has no thermal effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    order_raw, order_bank = _u12_order_field(
        (
            "Liquid near the heat source warms and expands",
            "Warm liquid rises and cooler liquid sinks",
            "Stirring helps mix the convection currents",
        ),
        ("The soup freezes before any heat arrives",),
    )
    question = (
        "<p>A fictional soup demo heats a pot from below.</p>"
        "<p>(i) Order warm-and-rise, then sink, then stirring helps mix.</p>"
        "<p>(ii) Using that convection picture from (i), stirring mainly improves</p>"
    )
    solution = (
        "(i) <strong>warm/expand → rise/sink → stir</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order convection steps, then choose how "
        "stirring helps heat spread."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Convection order", "What stirring improves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order convection, then choose what stirring improves.",
        ),
    )


@_u12_variant("cooking_heat", "ms", "intermediate", "protein_temp_then_texture")
def _cooking_heat_intermediate_ms_protein_temp_then_texture():
    pack = random.choice(
        (
            {"start_c": 20, "end_c": 65},
            {"start_c": 4, "end_c": 70},
            {"start_c": 15, "end_c": 60},
        )
    )
    rise = pack["end_c"] - pack["start_c"]
    correct = "denatured protein gives a firmer, changed texture"
    distractors = (
        "the egg becomes a metal",
        "heat removes all protein permanently",
        "a rumour that texture never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional egg demo warms from {pack['start_c']} °C to "
        f"{pack['end_c']} °C.</p>"
        "<p>(i) By how many degrees Celsius did the temperature rise?</p>"
        "<p>(ii) Using that rise from (i), the visible texture change shows</p>"
    )
    solution = (
        f"(i) {pack['end_c']} − {pack['start_c']} = "
        f"<strong>{rise}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract temperatures, then link the "
        "rise to protein denaturing."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (rise, letter),
            ("Temperature rise (°C)", "What texture change shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the temperature rise, then choose the texture link.",
        ),
    )


@_u12_variant("cooking_heat", "ms", "difficult", "three_transfer_pick_then_brown")
def _cooking_heat_difficult_ms_three_transfer_pick_then_brown():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Conduction through a metal pan base",
            "Radiation from a grill element",
        ),
        (
            "Photosynthesis in the oven",
            "A rumour that heat types do not exist",
        ),
        2,
    )
    methods = 3
    correct = "high surface heat drives browning while inside cooks by conduction"
    distractors = (
        "browning happens only below 0 °C",
        "no heat transfer occurs in cooking",
        "a celebrity claim that colour is unrelated to temperature",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional cookery exam lists conduction, convection and radiation.</p>"
        "<p>(i) How many named heat-transfer types are listed?</p>"
        "<p>(ii) Select two that can apply in real cooking methods.</p>"
        "<p>(iii) Using those two from (ii), searing then baking shows</p>"
    )
    solution = (
        f"(i) <strong>{methods}</strong><br>"
        "(ii) Conduction and radiation are valid cooking transfers.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count transfer types, pick two real ones, "
        "then link surface heat to browning."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (methods, pick_raw, letter),
            ("Transfer types listed", "Two real transfers", "Sear then bake"),
            field_types=("number", "pick", "mcq"),
            field_options=(None, pick_bank, options),
            field_pick_counts=(None, pick_count, None),
            format_hint="Count types, pick two transfers, then choose the browning link.",
        ),
    )


@_u12_variant("cooking_heat", "ms", "difficult", "chain_order_then_maillard")
def _cooking_heat_difficult_ms_chain_order_then_maillard():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat reaches the food surface",
            "Surface temperature rises enough for browning",
            "Maillard reaction produces colour and flavour",
        ),
        ("Food freezes before heat arrives",),
    )
    correct = "browning needs sufficient surface temperature, not just any warmth"
    distractors = (
        "browning happens instantly at 0 °C",
        "Maillard reaction requires no heat",
        "a rumour that colour is unrelated to temperature",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional toast test tracks heat to browning.</p>"
        "<p>(i) Order heat arrival, surface heating, then Maillard browning.</p>"
        "<p>(ii) Using that chain from (i), the lesson explains that</p>"
    )
    solution = (
        "(i) <strong>heat → surface temp → Maillard</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the browning chain, then state the "
        "temperature requirement."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Browning chain order", "Temperature requirement"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the chain, then choose the temperature fact.",
        ),
    )


@_u12_variant("cooking_heat", "ms", "difficult", "denature_count_then_safety")
def _cooking_heat_difficult_ms_denature_count_then_safety():
    changes = 2
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Cook food thoroughly so harmful bacteria are reduced",
            "Use a food thermometer for high-risk dishes",
        ),
        (
            "Taste raw poultry to check doneness",
            "Leave cooked food at room temperature for hours",
        ),
        2,
    )
    question = (
        "<p>A fictional food-safety poster links heat, denaturing and hygiene.</p>"
        "<p>(i) Name two visible changes when egg protein denatures "
        "(e.g. colour and texture).</p>"
        "<p>(ii) Using those changes from (i) as evidence of heating, select "
        "two safe public-kitchen actions.</p>"
    )
    solution = (
        f"(i) <strong>{changes}</strong> visible changes (colour and texture)<br>"
        "(ii) Thorough cooking and thermometers are safe actions."
    )
    hint = (
        "<strong>Key idea:</strong> Count visible denaturing signs, then pick "
        "safe heating practices."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (changes, pick_raw),
            ("Visible changes", "Safe actions"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count visible changes, then select two safe actions.",
        ),
    )


COOKING_HEAT_MS_POOLS = {
    "foundational": [
        _cooking_heat_foundational_ms_pan_transfer_then_name,
        _cooking_heat_foundational_ms_heat_path_order_then_denature,
        _cooking_heat_foundational_ms_oven_temp_then_brown,
    ],
    "intermediate": [
        _cooking_heat_intermediate_ms_grill_distance_then_radiation,
        _cooking_heat_intermediate_ms_stir_soup_then_convection,
        _cooking_heat_intermediate_ms_protein_temp_then_texture,
    ],
    "difficult": [
        _cooking_heat_difficult_ms_three_transfer_pick_then_brown,
        _cooking_heat_difficult_ms_chain_order_then_maillard,
        _cooking_heat_difficult_ms_denature_count_then_safety,
    ],
}

# ---------------------------------------------------------------------------
# cooking_heat — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CH_SMS_F_DEMO_PACKS = (
    {"place": "fictional school kitchen", "method": "frying eggs in a pan"},
    {"place": "fictional cookery fair", "method": "toasting bread under a grill"},
    {"place": "fictional community cafe", "method": "simmering soup on a hob"},
)


@_u12_variant("cooking_heat", "sms", "foundational", "demo_transfer_then_name")
def _cooking_heat_foundational_sms_demo_transfer_then_name():
    pack = random.choice(_CH_SMS_F_DEMO_PACKS)
    transfers = 3
    transfer_map = {
        "frying eggs in a pan": "conduction from the hot pan",
        "toasting bread under a grill": "radiation from the grill element",
        "simmering soup on a hob": "convection in the liquid",
    }
    correct = transfer_map[pack["method"]]
    distractors = (
        "photosynthesis in the saucepan",
        "a magnet attracting dissolved salt",
        "a celebrity slogan with no heat source",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} demo uses {pack['method']}.</p>"
        "<p>(i) How many of the lesson's three heat-transfer types "
        "(conduction, convection, radiation) exist in cooking?</p>"
        "<p>(ii) Using that count from (i), the main transfer in this demo is</p>"
    )
    solution = (
        f"(i) <strong>{transfers}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count transfer types, then match the "
        "demo method to the dominant one."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (transfers, letter),
            ("Heat-transfer types", "Main transfer in demo"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count types, then choose the main transfer.",
        ),
    )


@_u12_variant("cooking_heat", "sms", "foundational", "egg_poster_order_then_denature")
def _cooking_heat_foundational_sms_egg_poster_order_then_denature():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat transfers to the egg",
            "Egg temperature rises",
            "Proteins unfold (denature)",
        ),
        ("The egg cools before any heat arrives",),
    )
    correct = "the protein structure changes and the texture alters"
    distractors = (
        "water molecules are destroyed forever",
        "the egg becomes a metal element",
        "a rumour that heat has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional school poster shows how heat cooks an egg.</p>"
        "<p>(i) Order heat transfer, temperature rise, then denaturing.</p>"
        "<p>(ii) Using that sequence from (i), denaturing means</p>"
    )
    solution = (
        "(i) <strong>heat → temperature rise → denature</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the heat chain, then define "
        "denaturing as protein unfolding."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Heat path order", "What denaturing means"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the chain, then choose what denaturing means.",
        ),
    )


_CH_SMS_F_OVEN_PACKS = (
    {"temp_c": 180, "item": "bread rolls"},
    {"temp_c": 200, "item": "pastry"},
    {"temp_c": 170, "item": "muffins"},
)


@_u12_variant("cooking_heat", "sms", "foundational", "oven_log_then_brown")
def _cooking_heat_foundational_sms_oven_log_then_brown():
    pack = random.choice(_CH_SMS_F_OVEN_PACKS)
    correct = "browning from the Maillard reaction at high surface temperature"
    distractors = (
        "ice forming on the hot surface",
        "photosynthesis in the oven",
        "a rumour that colour never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional bakery log bakes {pack['item']} at {pack['temp_c']} °C "
        "until the crust turns brown.</p>"
        "<p>(i) What oven temperature in °C is logged?</p>"
        "<p>(ii) Using that temperature from (i), the brown crust mainly shows</p>"
    )
    solution = (
        f"(i) <strong>{pack['temp_c']}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the oven temperature, then link "
        "browning to surface heating."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["temp_c"], letter),
            ("Oven temperature (°C)", "What browning shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the temperature, then choose what browning shows.",
        ),
    )


_CH_SMS_I_GRILL_PACKS = (
    {"distance_cm": 8},
    {"distance_cm": 18},
    {"distance_cm": 25},
)


@_u12_variant("cooking_heat", "sms", "intermediate", "fair_grill_then_radiation")
def _cooking_heat_intermediate_sms_fair_grill_then_radiation():
    pack = random.choice(_CH_SMS_I_GRILL_PACKS)
    correct = (
        "radiation is stronger when the food is closer to the grill"
        if pack["distance_cm"] <= 12
        else "radiation decreases with distance from the heat source"
    )
    distractors = (
        "conduction through empty air with no contact",
        "photosynthesis on the grill rack",
        "a rumour that distance has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery fair places food {pack['distance_cm']} cm "
        "from a grill element.</p>"
        "<p>(i) Record the distance in centimetres.</p>"
        "<p>(ii) Using that distance from (i), this setup shows that</p>"
    )
    solution = (
        f"(i) <strong>{pack['distance_cm']}</strong> cm<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Note the distance, then relate it to "
        "radiation strength."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["distance_cm"], letter),
            ("Distance (cm)", "Radiation effect"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Record the distance, then choose the radiation effect.",
        ),
    )


@_u12_variant("cooking_heat", "sms", "intermediate", "cafe_soup_then_convection")
def _cooking_heat_intermediate_sms_cafe_soup_then_convection():
    order_raw, order_bank = _u12_order_field(
        (
            "Liquid near the heat warms and expands",
            "Warm liquid rises and cooler liquid sinks",
            "Stirring helps mix the convection currents",
        ),
        ("The soup freezes before any heat arrives",),
    )
    correct = "convection currents spread heat through the liquid"
    distractors = (
        "radiation through a solid spoon only",
        "photosynthesis in the soup",
        "a rumour that stirring has no thermal effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional community cafe heats soup from below on a hob.</p>"
        "<p>(i) Order warm-and-rise, sink, then stirring helps mix.</p>"
        "<p>(ii) Using that convection picture from (i), stirring mainly improves</p>"
    )
    solution = (
        "(i) <strong>warm/expand → rise/sink → stir</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order convection steps, then choose how "
        "stirring helps heat spread."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Convection order", "What stirring improves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order convection, then choose what stirring improves.",
        ),
    )


_CH_SMS_I_EGG_PACKS = (
    {"start_c": 20, "end_c": 68},
    {"start_c": 5, "end_c": 72},
    {"start_c": 18, "end_c": 65},
)


@_u12_variant("cooking_heat", "sms", "intermediate", "demo_egg_then_texture")
def _cooking_heat_intermediate_sms_demo_egg_then_texture():
    pack = random.choice(_CH_SMS_I_EGG_PACKS)
    rise = pack["end_c"] - pack["start_c"]
    correct = "denatured protein gives a firmer, changed texture"
    distractors = (
        "the egg becomes a metal",
        "heat removes all protein permanently",
        "a rumour that texture never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery demo warms an egg from {pack['start_c']} °C to "
        f"{pack['end_c']} °C.</p>"
        "<p>(i) By how many degrees Celsius did the temperature rise?</p>"
        "<p>(ii) Using that rise from (i), the visible texture change shows</p>"
    )
    solution = (
        f"(i) {pack['end_c']} − {pack['start_c']} = "
        f"<strong>{rise}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract temperatures, then link the "
        "rise to protein denaturing."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (rise, letter),
            ("Temperature rise (°C)", "What texture change shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the temperature rise, then choose the texture link.",
        ),
    )


@_u12_variant("cooking_heat", "sms", "difficult", "exam_pick_then_brown")
def _cooking_heat_difficult_sms_exam_pick_then_brown():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Conduction through a metal pan",
            "Radiation from a grill element",
        ),
        (
            "Photosynthesis in the oven",
            "A rumour that heat types do not exist",
        ),
        2,
    )
    methods = 3
    correct = "high surface heat drives browning while inside cooks by conduction"
    distractors = (
        "browning happens only below 0 °C",
        "no heat transfer occurs in cooking",
        "a celebrity claim that colour is unrelated to temperature",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional cookery exam lists conduction, convection and radiation.</p>"
        "<p>(i) How many named heat-transfer types are listed?</p>"
        "<p>(ii) Select two that can apply in real cooking methods.</p>"
        "<p>(iii) Using those two from (ii), searing then baking shows</p>"
    )
    solution = (
        f"(i) <strong>{methods}</strong><br>"
        "(ii) Conduction and radiation are valid cooking transfers.<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count types, pick two real transfers, "
        "then link surface heat to browning."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (methods, pick_raw, letter),
            ("Transfer types listed", "Two real transfers", "Sear then bake"),
            field_types=("number", "pick", "mcq"),
            field_options=(None, pick_bank, options),
            field_pick_counts=(None, pick_count, None),
            format_hint="Count types, pick two transfers, then choose browning link.",
        ),
    )


@_u12_variant("cooking_heat", "sms", "difficult", "toast_chain_then_maillard")
def _cooking_heat_difficult_sms_toast_chain_then_maillard():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat reaches the bread surface",
            "Surface temperature rises enough for browning",
            "Maillard reaction produces colour and flavour",
        ),
        ("Bread freezes before heat arrives",),
    )
    correct = "browning needs sufficient surface temperature, not just any warmth"
    distractors = (
        "browning happens instantly at 0 °C",
        "Maillard reaction requires no heat",
        "a rumour that colour is unrelated to temperature",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional toast competition tracks heat to browning.</p>"
        "<p>(i) Order heat arrival, surface heating, then Maillard browning.</p>"
        "<p>(ii) Using that chain from (i), the lesson explains that</p>"
    )
    solution = (
        "(i) <strong>heat → surface temp → Maillard</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the browning chain, then state the "
        "temperature requirement."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Browning chain order", "Temperature requirement"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the chain, then choose the temperature fact.",
        ),
    )


@_u12_variant("cooking_heat", "sms", "difficult", "safety_pick_then_count")
def _cooking_heat_difficult_sms_safety_pick_then_count():
    changes = 2
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Cook food thoroughly so harmful bacteria are reduced",
            "Use a food thermometer for high-risk dishes",
        ),
        (
            "Taste raw poultry to check doneness",
            "Leave cooked food at room temperature for hours",
        ),
        2,
    )
    question = (
        "<p>A fictional food-safety workshop links heat, denaturing and hygiene.</p>"
        "<p>(i) How many visible changes (e.g. colour and texture) show egg "
        "protein has denatured?</p>"
        "<p>(ii) Using those changes from (i) as evidence of heating, select "
        "two safe public-kitchen actions.</p>"
    )
    solution = (
        f"(i) <strong>{changes}</strong> visible changes<br>"
        "(ii) Thorough cooking and thermometers are safe actions."
    )
    hint = (
        "<strong>Key idea:</strong> Count visible denaturing signs, then pick "
        "safe heating practices."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (changes, pick_raw),
            ("Visible changes", "Safe actions"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count visible changes, then select two safe actions.",
        ),
    )


COOKING_HEAT_SMS_POOLS = {
    "foundational": [
        _cooking_heat_foundational_sms_demo_transfer_then_name,
        _cooking_heat_foundational_sms_egg_poster_order_then_denature,
        _cooking_heat_foundational_sms_oven_log_then_brown,
    ],
    "intermediate": [
        _cooking_heat_intermediate_sms_fair_grill_then_radiation,
        _cooking_heat_intermediate_sms_cafe_soup_then_convection,
        _cooking_heat_intermediate_sms_demo_egg_then_texture,
    ],
    "difficult": [
        _cooking_heat_difficult_sms_exam_pick_then_brown,
        _cooking_heat_difficult_sms_toast_chain_then_maillard,
        _cooking_heat_difficult_sms_safety_pick_then_count,
    ],
}

# ---------------------------------------------------------------------------
# cooking_acid — multi_step (I, D only; foundational —)
# ---------------------------------------------------------------------------

_CA_MS_I_PH_PACKS = (
    {"ph": 3, "food": "lemon juice"},
    {"ph": 4, "food": "tomato sauce"},
    {"ph": 5, "food": "yoghurt dressing"},
)


@_u12_variant("cooking_acid", "ms", "intermediate", "ph_read_then_acid")
def _cooking_acid_intermediate_ms_ph_read_then_acid():
    pack = random.choice(_CA_MS_I_PH_PACKS)
    correct = "acidic, below pH 7 on the scale"
    distractors = (
        "neutral at exactly pH 14",
        "alkaline above pH 7",
        "a celebrity claim with no indicator reading",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional food-lab card tests {pack['food']} and records "
        f"pH {pack['ph']}.</p>"
        + str(ph_scale(title="Fictional pH scale for food acids"))
        + "<p>(i) What pH value was recorded?</p>"
        "<p>(ii) Using that reading from (i), the sample is</p>"
    )
    solution = (
        f"(i) <strong>{pack['ph']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the pH value, then classify it as "
        "acidic when below 7."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["ph"], letter),
            ("pH reading", "Classification"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read pH, then choose acidic or not.",
        ),
    )


@_u12_variant("cooking_acid", "ms", "intermediate", "indicator_colour_then_ph")
def _cooking_acid_intermediate_ms_indicator_colour_then_ph():
    pack = random.choice(
        (
            {"colour": "red", "ph": 2},
            {"colour": "orange", "ph": 4},
            {"colour": "yellow-green", "ph": 6},
        )
    )
    correct = "the indicator colour matches an acidic pH below 7"
    distractors = (
        "the colour proves the food is a metal",
        "indicators never change colour",
        "a rumour that pH is unrelated to colour",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery test dips indicator paper into vinegar; "
        f"it turns {pack['colour']} and the meter reads pH {pack['ph']}.</p>"
        + str(ph_scale(title="Fictional indicator and pH scale"))
        + "<p>(i) What pH does the meter show?</p>"
        "<p>(ii) Using that pH from (i), the indicator result shows</p>"
    )
    solution = (
        f"(i) <strong>{pack['ph']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the pH meter, then link the colour "
        "to an acidic reading."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["ph"], letter),
            ("pH on meter", "What indicator shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read pH, then choose what the indicator shows.",
        ),
    )


@_u12_variant("cooking_acid", "ms", "intermediate", "preserve_order_then_acid")
def _cooking_acid_intermediate_ms_preserve_order_then_acid():
    order_raw, order_bank = _u12_order_field(
        (
            "Test pH of the food sample",
            "Confirm the sample is acidic",
            "Explain how acid slows bacterial growth",
        ),
        ("Skip testing and rely on a rumour",),
    )
    correct = "low pH makes the environment less suitable for many bacteria"
    distractors = (
        "acid destroys all nutrients instantly",
        "pH has no role in preservation",
        "a celebrity poster with no data",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional pickling poster explains acid preservation.</p>"
        + str(ph_scale(title="Fictional pickling pH scale"))
        + "<p>(i) Order test pH, confirm acidity, then explain preservation.</p>"
        "<p>(ii) Using that sequence from (i), acid helps preserve food because</p>"
    )
    solution = (
        "(i) <strong>test → confirm acid → explain</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the acid-preservation steps, then "
        "link low pH to slowed bacterial growth."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Preservation order", "Why acid preserves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose why acid preserves.",
        ),
    )


_CA_MS_D_PH_PACKS = (
    {"ph_a": 3, "ph_b": 6},
    {"ph_a": 2, "ph_b": 5},
    {"ph_a": 4, "ph_b": 7},
)


@_u12_variant("cooking_acid", "ms", "difficult", "compare_ph_then_stronger")
def _cooking_acid_difficult_ms_compare_ph_then_stronger():
    pack = random.choice(_CA_MS_D_PH_PACKS)
    diff = pack["ph_b"] - pack["ph_a"]
    correct = f"sample A at pH {pack['ph_a']} is more acidic"
    distractors = (
        "sample B is more acidic because its number is larger",
        "both samples are alkaline",
        "a rumour that lower pH means less acid",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional taste-test lab records pH {pack['ph_a']} for sample A "
        f"and pH {pack['ph_b']} for sample B.</p>"
        + str(ph_scale(title="Fictional comparison on the pH scale"))
        + "<p>(i) How many pH units apart are the two readings?</p>"
        "<p>(ii) Using that difference from (i), which sample is more acidic?</p>"
    )
    solution = (
        f"(i) {pack['ph_b']} − {pack['ph_a']} = <strong>{diff}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the pH gap, then recall that lower "
        "pH means stronger acid."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("pH difference", "More acidic sample"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract pH values, then choose the more acidic sample.",
        ),
    )


@_u12_variant("cooking_acid", "ms", "difficult", "marinade_ph_then_tender")
def _cooking_acid_difficult_ms_marinade_ph_then_tender():
    pack = random.choice(
        (
            {"ph": 3, "time_h": 2},
            {"ph": 4, "time_h": 4},
            {"ph": 2, "time_h": 1},
        )
    )
    correct = "acid can break down surface protein structure over time"
    distractors = (
        "acid has no effect on protein in food",
        "marinating always makes food alkaline",
        "a rumour that pH cannot change texture",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional marinade log soaks meat at pH {pack['ph']} for "
        f"{pack['time_h']} hours.</p>"
        + str(ph_scale(title="Fictional marinade pH scale"))
        + "<p>(i) How many hours does the log show?</p>"
        "<p>(ii) Using that acidic pH from the same log, the tenderising effect "
        "happens because</p>"
    )
    solution = (
        f"(i) <strong>{pack['time_h']}</strong> h<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the marinating time, then link "
        "acidic pH to protein breakdown at the surface."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["time_h"], letter),
            ("Marinating time (h)", "Why acid tenderises"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the time, then choose why acid tenderises.",
        ),
    )


@_u12_variant("cooking_acid", "ms", "difficult", "claim_critique_then_ph")
def _cooking_acid_difficult_ms_claim_critique_then_ph():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "A published pH reading from a tested sample",
            "A repeatable indicator colour change",
        ),
        (
            "A celebrity claim with no method",
            "A colourful advert with no data",
        ),
        2,
    )
    evidence = 2
    question = (
        "<p>A fictional food advert claims a drink is 'perfectly balanced' "
        "without showing any test data.</p>"
        + str(ph_scale(title="Fictional pH evidence scale"))
        + "<p>(i) How many pieces of scientific evidence would you need at "
        "minimum to check an acid/alkali claim?</p>"
        "<p>(ii) Using that count from (i), select the two acceptable evidence "
        "types to test the claim.</p>"
    )
    solution = (
        f"(i) <strong>{evidence}</strong> evidence types<br>"
        "(ii) pH reading and repeatable indicator change are acceptable."
    )
    hint = (
        "<strong>Key idea:</strong> Count needed evidence types, then pick "
        "measurement-based proof over adverts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (evidence, pick_raw),
            ("Evidence types needed", "Acceptable evidence"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count evidence types, then select measurement-based proof.",
        ),
    )


COOKING_ACID_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _cooking_acid_intermediate_ms_ph_read_then_acid,
        _cooking_acid_intermediate_ms_indicator_colour_then_ph,
        _cooking_acid_intermediate_ms_preserve_order_then_acid,
    ],
    "difficult": [
        _cooking_acid_difficult_ms_compare_ph_then_stronger,
        _cooking_acid_difficult_ms_marinade_ph_then_tender,
        _cooking_acid_difficult_ms_claim_critique_then_ph,
    ],
}

# ---------------------------------------------------------------------------
# cooking_acid — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CA_SMS_F_LEMON_PACKS = (
    {"ph": 2, "place": "fictional lemonade stand"},
    {"ph": 3, "place": "fictional fruit-juice cart"},
    {"ph": 4, "place": "fictional salad-dressing demo"},
)


@_u12_variant("cooking_acid", "sms", "foundational", "stand_ph_then_acid")
def _cooking_acid_foundational_sms_stand_ph_then_acid():
    pack = random.choice(_CA_SMS_F_LEMON_PACKS)
    correct = "acidic, below pH 7 on the scale"
    distractors = (
        "neutral at exactly pH 14",
        "alkaline above pH 7",
        "a celebrity claim with no indicator reading",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} tests a sample and records "
        f"pH {pack['ph']}.</p>"
        + str(ph_scale(title="Fictional street-food pH scale"))
        + "<p>(i) What pH value was recorded?</p>"
        "<p>(ii) Using that reading from (i), the sample is</p>"
    )
    solution = (
        f"(i) <strong>{pack['ph']}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the pH value, then classify it as "
        "acidic when below 7."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["ph"], letter),
            ("pH reading", "Classification"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read pH, then choose acidic or not.",
        ),
    )


@_u12_variant("cooking_acid", "sms", "foundational", "vinegar_indicator_then_ph")
def _cooking_acid_foundational_sms_vinegar_indicator_then_ph():
    ph = 3
    correct = "the indicator colour matches an acidic pH below 7"
    distractors = (
        "the colour proves the food is a metal",
        "indicators never change colour",
        "a rumour that pH is unrelated to colour",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional cookery fair dips indicator paper into vinegar; "
        f"the meter reads pH {ph}.</p>"
        + str(ph_scale(title="Fictional vinegar pH on the scale"))
        + "<p>(i) What pH does the meter show?</p>"
        "<p>(ii) Using that pH from (i), the indicator result shows</p>"
    )
    solution = (
        f"(i) <strong>{ph}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the pH meter, then link the result "
        "to an acidic reading."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (ph, letter),
            ("pH on meter", "What indicator shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read pH, then choose what the indicator shows.",
        ),
    )


@_u12_variant("cooking_acid", "sms", "foundational", "pickle_poster_order_then_why")
def _cooking_acid_foundational_sms_pickle_poster_order_then_why():
    order_raw, order_bank = _u12_order_field(
        (
            "Test pH of the pickle brine",
            "Confirm the brine is acidic",
            "Explain how acid slows bacterial growth",
        ),
        ("Skip testing and rely on a rumour",),
    )
    correct = "low pH makes the environment less suitable for many bacteria"
    distractors = (
        "acid destroys all nutrients instantly",
        "pH has no role in preservation",
        "a celebrity poster with no data",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional pickling workshop poster explains acid preservation.</p>"
        + str(ph_scale(title="Fictional workshop pH scale"))
        + "<p>(i) Order test pH, confirm acidity, then explain preservation.</p>"
        "<p>(ii) Using that sequence from (i), acid helps preserve food because</p>"
    )
    solution = (
        "(i) <strong>test → confirm acid → explain</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the preservation steps, then link "
        "low pH to slowed bacterial growth."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Preservation order", "Why acid preserves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose why acid preserves.",
        ),
    )


_CA_SMS_I_COMPARE_PACKS = (
    {"ph_a": 3, "ph_b": 6},
    {"ph_a": 2, "ph_b": 5},
    {"ph_a": 4, "ph_b": 7},
)


@_u12_variant("cooking_acid", "sms", "intermediate", "lab_compare_then_stronger")
def _cooking_acid_intermediate_sms_lab_compare_then_stronger():
    pack = random.choice(_CA_SMS_I_COMPARE_PACKS)
    diff = pack["ph_b"] - pack["ph_a"]
    correct = f"sample A at pH {pack['ph_a']} is more acidic"
    distractors = (
        "sample B is more acidic because its number is larger",
        "both samples are alkaline",
        "a rumour that lower pH means less acid",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional food-lab compares pH {pack['ph_a']} (sample A) and "
        f"pH {pack['ph_b']} (sample B).</p>"
        + str(ph_scale(title="Fictional lab pH comparison scale"))
        + "<p>(i) How many pH units apart are the two readings?</p>"
        "<p>(ii) Using that difference from (i), which sample is more acidic?</p>"
    )
    solution = (
        f"(i) {pack['ph_b']} − {pack['ph_a']} = <strong>{diff}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the pH gap, then recall that lower "
        "pH means stronger acid."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("pH difference", "More acidic sample"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract pH values, then choose the more acidic sample.",
        ),
    )


_CA_SMS_I_MARINADE_PACKS = (
    {"ph": 3, "time_h": 3},
    {"ph": 4, "time_h": 5},
    {"ph": 2, "time_h": 2},
)


@_u12_variant("cooking_acid", "sms", "intermediate", "marinade_log_then_tender")
def _cooking_acid_intermediate_sms_marinade_log_then_tender():
    pack = random.choice(_CA_SMS_I_MARINADE_PACKS)
    correct = "acid can break down surface protein structure over time"
    distractors = (
        "acid has no effect on protein in food",
        "marinating always makes food alkaline",
        "a rumour that pH cannot change texture",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery-school marinade log records pH {pack['ph']} "
        f"for {pack['time_h']} hours.</p>"
        + str(ph_scale(title="Fictional marinade pH scale"))
        + "<p>(i) How many hours does the log show?</p>"
        "<p>(ii) Using that acidic pH from the same log, tenderising happens because</p>"
    )
    solution = (
        f"(i) <strong>{pack['time_h']}</strong> h<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the marinating time, then link "
        "acidic pH to protein breakdown."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["time_h"], letter),
            ("Marinating time (h)", "Why acid tenderises"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the time, then choose why acid tenderises.",
        ),
    )


@_u12_variant("cooking_acid", "sms", "intermediate", "dressing_ph_then_preserve")
def _cooking_acid_intermediate_sms_dressing_ph_then_preserve():
    ph = 4
    correct = "acidic dressing can slow spoilage when pH stays low enough"
    distractors = (
        "any pH above 7 preserves food best",
        "pH has no role in food safety",
        "a rumour that dressings never contain acid",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional salad-dressing test records pH {ph} in a sealed jar.</p>"
        + str(ph_scale(title="Fictional dressing pH scale"))
        + "<p>(i) What pH was recorded?</p>"
        "<p>(ii) Using that reading from (i), the preservation claim is valid because</p>"
    )
    solution = (
        f"(i) <strong>{ph}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the pH, then link low acidity to "
        "slowed bacterial growth."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (ph, letter),
            ("pH recorded", "Preservation claim"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read pH, then choose why preservation can work.",
        ),
    )


@_u12_variant("cooking_acid", "sms", "difficult", "advert_pick_then_count")
def _cooking_acid_difficult_sms_advert_pick_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "A published pH reading from a tested sample",
            "A repeatable indicator colour change",
        ),
        (
            "A celebrity claim with no method",
            "A colourful advert with no data",
        ),
        2,
    )
    evidence = 2
    question = (
        "<p>A fictional drink advert claims 'perfect balance' without test data.</p>"
        + str(ph_scale(title="Fictional advert critique pH scale"))
        + "<p>(i) How many evidence types are needed minimum to check an "
        "acid/alkali claim?</p>"
        "<p>(ii) Using that count from (i), select two acceptable evidence types.</p>"
    )
    solution = (
        f"(i) <strong>{evidence}</strong><br>"
        "(ii) pH reading and repeatable indicator change are acceptable."
    )
    hint = (
        "<strong>Key idea:</strong> Count needed evidence types, then pick "
        "measurement-based proof over adverts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (evidence, pick_raw),
            ("Evidence types needed", "Acceptable evidence"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count evidence types, then select measurement proof.",
        ),
    )


@_u12_variant("cooking_acid", "sms", "difficult", "ferment_ph_then_lactic")
def _cooking_acid_difficult_sms_ferment_ph_then_lactic():
    pack = random.choice(
        (
            {"start_ph": 6, "end_ph": 4},
            {"start_ph": 7, "end_ph": 5},
            {"start_ph": 5, "end_ph": 3},
        )
    )
    drop = pack["start_ph"] - pack["end_ph"]
    correct = "lactic acid from fermentation lowers the pH"
    distractors = (
        "pH rises because bacteria add alkali",
        "fermentation never changes pH",
        "a rumour that pH is fixed in all food",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional yoghurt fermentation log shows pH falling from "
        f"{pack['start_ph']} to {pack['end_ph']}.</p>"
        + str(ph_scale(title="Fictional fermentation pH scale"))
        + "<p>(i) By how many pH units did the reading drop?</p>"
        "<p>(ii) Using that drop from (i), the change happens because</p>"
    )
    solution = (
        f"(i) {pack['start_ph']} − {pack['end_ph']} = <strong>{drop}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the pH readings, then link the "
        "drop to lactic acid production."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (drop, letter),
            ("pH drop", "Why pH falls"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the pH drop, then choose why fermentation acidifies.",
        ),
    )


@_u12_variant("cooking_acid", "sms", "difficult", "safety_order_then_acid")
def _cooking_acid_difficult_sms_safety_order_then_acid():
    order_raw, order_bank = _u12_order_field(
        (
            "Measure pH of the preserved sample",
            "Check pH stayed low during storage",
            "Conclude acid helped limit bacterial growth",
        ),
        ("Ignore pH and trust the label colour",),
    )
    correct = "low pH alone does not replace proper storage temperature and hygiene"
    distractors = (
        "any acidic food never spoils regardless of storage",
        "pH measurement is useless in food science",
        "a rumour that acid replaces all safety rules",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional food-safety audit reviews an acid-preserved product.</p>"
        + str(ph_scale(title="Fictional audit pH scale"))
        + "<p>(i) Order measure pH, check storage pH, then conclude on bacteria.</p>"
        "<p>(ii) Using that audit from (i), a balanced conclusion is that</p>"
    )
    solution = (
        "(i) <strong>measure → check → conclude</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the audit steps, then note that acid "
        "helps but does not replace all hygiene."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Audit order", "Balanced conclusion"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the audit, then choose the balanced conclusion.",
        ),
    )


COOKING_ACID_SMS_POOLS = {
    "foundational": [
        _cooking_acid_foundational_sms_stand_ph_then_acid,
        _cooking_acid_foundational_sms_vinegar_indicator_then_ph,
        _cooking_acid_foundational_sms_pickle_poster_order_then_why,
    ],
    "intermediate": [
        _cooking_acid_intermediate_sms_lab_compare_then_stronger,
        _cooking_acid_intermediate_sms_marinade_log_then_tender,
        _cooking_acid_intermediate_sms_dressing_ph_then_preserve,
    ],
    "difficult": [
        _cooking_acid_difficult_sms_advert_pick_then_count,
        _cooking_acid_difficult_sms_ferment_ph_then_lactic,
        _cooking_acid_difficult_sms_safety_order_then_acid,
    ],
}

# ---------------------------------------------------------------------------
# cooking_salt — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CS_MS_F_BRINE_PACKS = (
    {"salt_g": 10, "water_ml": 100},
    {"salt_g": 5, "water_ml": 50},
    {"salt_g": 20, "water_ml": 200},
)


@_u12_variant("cooking_salt", "ms", "foundational", "brine_mass_then_concentration")
def _cooking_salt_foundational_ms_brine_mass_then_concentration():
    pack = random.choice(_CS_MS_F_BRINE_PACKS)
    correct = "a higher salt concentration in the water"
    distractors = (
        "less salt dissolved in the same water",
        "salt turns water into a metal",
        "a rumour that mass does not affect concentration",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional brine recipe dissolves {pack['salt_g']} g salt in "
        f"{pack['water_ml']} mL water.</p>"
        "<p>(i) What mass of salt in grams is used?</p>"
        "<p>(ii) Using that mass from (i) in the same volume of water, adding "
        "more salt would give</p>"
    )
    solution = (
        f"(i) <strong>{pack['salt_g']}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the salt mass, then link more solute "
        "in the same solvent to higher concentration."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["salt_g"], letter),
            ("Salt mass (g)", "Effect of more salt"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read the salt mass, then choose the concentration effect.",
        ),
    )


@_u12_variant("cooking_salt", "ms", "foundational", "evap_volume_then_crystals")
def _cooking_salt_foundational_ms_evap_volume_then_crystals():
    pack = random.choice(
        (
            {"start_ml": 100, "left_ml": 40},
            {"start_ml": 80, "left_ml": 30},
            {"start_ml": 50, "left_ml": 10},
        )
    )
    evaporated = pack["start_ml"] - pack["left_ml"]
    correct = "salt crystals form as water evaporates and concentration rises"
    distractors = (
        "salt disappears when water is heated",
        "crystals form only in ice",
        "a rumour that evaporation has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional salt solution starts at {pack['start_ml']} mL. After "
        f"heating, {pack['left_ml']} mL of liquid remains.</p>"
        "<p>(i) How many millilitres of water evaporated?</p>"
        "<p>(ii) Using that loss from (i), crystallisation happens because</p>"
    )
    solution = (
        f"(i) {pack['start_ml']} − {pack['left_ml']} = "
        f"<strong>{evaporated}</strong> mL<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract volumes to find evaporation, then "
        "link it to crystal formation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (evaporated, letter),
            ("Volume evaporated (mL)", "Why crystals form"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find evaporated volume, then choose why crystals form.",
        ),
    )


@_u12_variant("cooking_salt", "ms", "foundational", "preserve_salt_then_osmosis")
def _cooking_salt_foundational_ms_preserve_salt_then_osmosis():
    order_raw, order_bank = _u12_order_field(
        (
            "Salt draws water out of food cells",
            "Concentration at the surface rises",
            "Growth of many bacteria is slowed",
        ),
        ("Bacteria grow faster in dry salt",),
    )
    correct = "high salt concentration reduces water available to microbes"
    distractors = (
        "salt has no effect on bacteria",
        "osmosis only happens in metals",
        "a rumour that preservation needs no salt",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional curing poster explains salting fish.</p>"
        "<p>(i) Order water drawn out, concentration rises, bacteria slowed.</p>"
        "<p>(ii) Using that sequence from (i), salting preserves because</p>"
    )
    solution = (
        "(i) <strong>draw water → concentration → slow bacteria</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the salting chain, then link high "
        "salt to reduced microbial water."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Salting order", "Why salting preserves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the chain, then choose why salting preserves.",
        ),
    )


_CS_MS_I_EVAP_PACKS = (
    {"start_ml": 200, "left_ml": 80},
    {"start_ml": 150, "left_ml": 45},
    {"start_ml": 120, "left_ml": 36},
)


@_u12_variant("cooking_salt", "ms", "intermediate", "pan_evap_then_percent")
def _cooking_salt_intermediate_ms_pan_evap_then_percent():
    pack = random.choice(_CS_MS_I_EVAP_PACKS)
    lost = pack["start_ml"] - pack["left_ml"]
    pct = round(100 * lost / pack["start_ml"])
    correct = "crystallisation becomes more likely as concentration rises"
    distractors = (
        "salt dissolves more as more water evaporates",
        "evaporation removes salt crystals first",
        "a rumour that percent lost has no meaning",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional pan of brine starts at {pack['start_ml']} mL and ends "
        f"at {pack['left_ml']} mL after heating.</p>"
        "<p>(i) What percentage of the starting volume evaporated?</p>"
        "<p>(ii) Using that percentage from (i), the remaining solution is "
        "closer to crystallisation because</p>"
    )
    solution = (
        f"(i) {lost}/{pack['start_ml']} × 100 = <strong>{pct}</strong>%<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the percent evaporated, then link "
        "higher concentration to crystallisation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pct, letter),
            ("Percent evaporated", "Closer to crystallisation because"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Calculate percent evaporated, then choose the crystallisation link.",
        ),
    )


@_u12_variant("cooking_salt", "ms", "intermediate", "dissolve_rate_then_temp")
def _cooking_salt_intermediate_ms_dissolve_rate_then_temp():
    pack = random.choice(
        (
            {"cold_g": 4, "hot_g": 12},
            {"cold_g": 5, "hot_g": 15},
            {"cold_g": 6, "hot_g": 18},
        )
    )
    diff = pack["hot_g"] - pack["cold_g"]
    correct = "warmer solvent particles move faster and dissolve solute quicker"
    distractors = (
        "cold water always dissolves more salt",
        "temperature has no effect on dissolving",
        "a rumour that salt cannot dissolve",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional dissolving test records {pack['cold_g']} g salt "
        f"dissolved in cold water and {pack['hot_g']} g in hot water in equal "
        "times.</p>"
        "<p>(i) How many more grams dissolved in hot water?</p>"
        "<p>(ii) Using that difference from (i), hot water dissolves faster because</p>"
    )
    solution = (
        f"(i) {pack['hot_g']} − {pack['cold_g']} = <strong>{diff}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract the two masses, then link warmer "
        "solvent to faster dissolving."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("Extra grams dissolved (g)", "Why hot water is faster"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the mass difference, then choose why hot is faster.",
        ),
    )


@_u12_variant("cooking_salt", "ms", "intermediate", "saturated_then_crystal")
def _cooking_salt_intermediate_ms_saturated_then_crystal():
    pack = random.choice(
        (
            {"dissolved_g": 36, "added_g": 40},
            {"dissolved_g": 30, "added_g": 35},
            {"dissolved_g": 42, "added_g": 50},
        )
    )
    undissolved = pack["added_g"] - pack["dissolved_g"]
    correct = "the solution was saturated and excess salt formed crystals"
    distractors = (
        "salt cannot form crystals in water",
        "all added salt always dissolves",
        "a rumour that saturation does not exist",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional hot-water test dissolves {pack['dissolved_g']} g of "
        f"{pack['added_g']} g salt added, leaving solid at the bottom.</p>"
        "<p>(i) How many grams of salt did not dissolve?</p>"
        "<p>(ii) Using that mass from (i) at the bottom, the solution was</p>"
    )
    solution = (
        f"(i) {pack['added_g']} − {pack['dissolved_g']} = "
        f"<strong>{undissolved}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find undissolved mass, then name saturation "
        "and crystal formation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (undissolved, letter),
            ("Undissolved salt (g)", "What the bottom solid shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find undissolved mass, then choose what saturation means.",
        ),
    )


@_u12_variant("cooking_salt", "ms", "difficult", "evap_chain_order_then_crystal")
def _cooking_salt_difficult_ms_evap_chain_order_then_crystal():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat the salt solution gently",
            "Water evaporates and volume falls",
            "Concentration rises until crystals nucleate",
        ),
        ("Cool the solution before any evaporation",),
    )
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Evaporation removes solvent water",
            "Crystallisation forms solid salt",
        ),
        (
            "Salt molecules are destroyed by heat",
            "A rumour that crystals are plastic",
        ),
        2,
    )
    question = (
        "<p>A fictional salt-recovery lab poster shows evaporation to crystals.</p>"
        "<p>(i) Order heat, evaporate, then crystallise.</p>"
        "<p>(ii) Using that sequence from (i), select the two processes that "
        "explain the change.</p>"
    )
    solution = (
        "(i) <strong>heat → evaporate → crystallise</strong><br>"
        "(ii) Evaporation and crystallisation explain the change."
    )
    hint = (
        "<strong>Key idea:</strong> Order the lab chain, then pick evaporation "
        "and crystallisation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Process order", "Key processes"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the chain, then select evaporation and crystallisation.",
        ),
    )


@_u12_variant("cooking_salt", "ms", "difficult", "brine_compare_then_preserve")
def _cooking_salt_difficult_ms_brine_compare_then_preserve():
    pack = random.choice(
        (
            {"weak_g": 5, "strong_g": 15},
            {"weak_g": 8, "strong_g": 20},
            {"weak_g": 10, "strong_g": 25},
        )
    )
    ratio = pack["strong_g"] / pack["weak_g"]
    correct = "the stronger brine removes more water from microbial cells"
    distractors = (
        "weak brine always preserves better",
        "salt concentration has no preservation role",
        "a rumour that ratios do not matter",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional curing trial compares {pack['weak_g']} g and "
        f"{pack['strong_g']} g salt per 100 mL water.</p>"
        "<p>(i) How many times greater is the strong brine salt mass?</p>"
        "<p>(ii) Using that factor from (i), the stronger brine preserves better because</p>"
    )
    solution = (
        f"(i) {pack['strong_g']}/{pack['weak_g']} = <strong>{ratio:g}</strong>×<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Compare the two salt masses, then link "
        "higher concentration to better preservation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (ratio, letter),
            ("Strong-to-weak factor", "Why stronger brine preserves better"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find the mass ratio, then choose the preservation reason.",
        ),
    )


@_u12_variant("cooking_salt", "ms", "difficult", "label_sodium_then_critique")
def _cooking_salt_difficult_ms_label_sodium_then_critique():
    pack = random.choice(
        (
            {"sodium_mg": 400, "portion_g": 100},
            {"sodium_mg": 600, "portion_g": 150},
            {"sodium_mg": 300, "portion_g": 80},
        )
    )
    per_100 = round(100 * pack["sodium_mg"] / pack["portion_g"])
    correct = "compare the per-100 g sodium value to public health guidance"
    distractors = (
        "ignore sodium because labels are optional",
        "assume all salt is protein",
        "a rumour that sodium is unrelated to salt",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public label shows {pack['sodium_mg']} mg sodium per "
        f"{pack['portion_g']} g portion.</p>"
        "<p>(i) About how many mg sodium per 100 g is that?</p>"
        "<p>(ii) Using that per-100 g value from (i), a balanced critique should</p>"
    )
    solution = (
        f"(i) <strong>{per_100}</strong> mg per 100 g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Scale sodium to per 100 g, then compare "
        "to public guidance."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (per_100, letter),
            ("Sodium per 100 g (mg)", "Balanced critique"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Scale to per 100 g, then choose how to critique the claim.",
        ),
    )


COOKING_SALT_MS_POOLS = {
    "foundational": [
        _cooking_salt_foundational_ms_brine_mass_then_concentration,
        _cooking_salt_foundational_ms_evap_volume_then_crystals,
        _cooking_salt_foundational_ms_preserve_salt_then_osmosis,
    ],
    "intermediate": [
        _cooking_salt_intermediate_ms_pan_evap_then_percent,
        _cooking_salt_intermediate_ms_dissolve_rate_then_temp,
        _cooking_salt_intermediate_ms_saturated_then_crystal,
    ],
    "difficult": [
        _cooking_salt_difficult_ms_evap_chain_order_then_crystal,
        _cooking_salt_difficult_ms_brine_compare_then_preserve,
        _cooking_salt_difficult_ms_label_sodium_then_critique,
    ],
}

# ---------------------------------------------------------------------------
# cooking_salt — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CS_SMS_F_KITCHEN_PACKS = (
    {"salt_g": 8, "water_ml": 80, "place": "fictional school kitchen"},
    {"salt_g": 12, "water_ml": 120, "place": "fictional cookery fair"},
    {"salt_g": 6, "water_ml": 60, "place": "fictional community cafe"},
)


@_u12_variant("cooking_salt", "sms", "foundational", "kitchen_brine_then_more")
def _cooking_salt_foundational_sms_kitchen_brine_then_more():
    pack = random.choice(_CS_SMS_F_KITCHEN_PACKS)
    correct = "a higher salt concentration in the water"
    distractors = (
        "less salt dissolved in the same water",
        "salt turns water into a metal",
        "a rumour that mass does not affect concentration",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} dissolves {pack['salt_g']} g salt in "
        f"{pack['water_ml']} mL water.</p>"
        "<p>(i) What mass of salt in grams is used?</p>"
        "<p>(ii) Using that mass from (i) in the same volume, adding more salt "
        "would give</p>"
    )
    solution = (
        f"(i) <strong>{pack['salt_g']}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the salt mass, then link more solute "
        "to higher concentration."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["salt_g"], letter),
            ("Salt mass (g)", "Effect of more salt"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read salt mass, then choose the concentration effect.",
        ),
    )


_CS_SMS_F_EVAP_PACKS = (
    {"start_ml": 90, "left_ml": 35},
    {"start_ml": 70, "left_ml": 25},
    {"start_ml": 60, "left_ml": 20},
)


@_u12_variant("cooking_salt", "sms", "foundational", "fair_evap_then_crystals")
def _cooking_salt_foundational_sms_fair_evap_then_crystals():
    pack = random.choice(_CS_SMS_F_EVAP_PACKS)
    evaporated = pack["start_ml"] - pack["left_ml"]
    correct = "salt crystals form as water evaporates and concentration rises"
    distractors = (
        "salt disappears when water is heated",
        "crystals form only in ice",
        "a rumour that evaporation has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery fair heats a salt solution from "
        f"{pack['start_ml']} mL to {pack['left_ml']} mL.</p>"
        "<p>(i) How many millilitres of water evaporated?</p>"
        "<p>(ii) Using that loss from (i), crystallisation happens because</p>"
    )
    solution = (
        f"(i) {pack['start_ml']} − {pack['left_ml']} = "
        f"<strong>{evaporated}</strong> mL<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract volumes, then link evaporation to "
        "crystal formation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (evaporated, letter),
            ("Volume evaporated (mL)", "Why crystals form"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find evaporated volume, then choose why crystals form.",
        ),
    )


@_u12_variant("cooking_salt", "sms", "foundational", "cure_poster_order_then_why")
def _cooking_salt_foundational_sms_cure_poster_order_then_why():
    order_raw, order_bank = _u12_order_field(
        (
            "Salt draws water out of food cells",
            "Concentration at the surface rises",
            "Growth of many bacteria is slowed",
        ),
        ("Bacteria grow faster in dry salt",),
    )
    correct = "high salt concentration reduces water available to microbes"
    distractors = (
        "salt has no effect on bacteria",
        "osmosis only happens in metals",
        "a rumour that preservation needs no salt",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional fish-curing workshop poster explains salting.</p>"
        "<p>(i) Order water drawn out, concentration rises, bacteria slowed.</p>"
        "<p>(ii) Using that sequence from (i), salting preserves because</p>"
    )
    solution = (
        "(i) <strong>draw water → concentration → slow bacteria</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the salting chain, then link high "
        "salt to reduced microbial water."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Salting order", "Why salting preserves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the chain, then choose why salting preserves.",
        ),
    )


_CS_SMS_I_PAN_PACKS = (
    {"start_ml": 180, "left_ml": 72},
    {"start_ml": 140, "left_ml": 56},
    {"start_ml": 100, "left_ml": 40},
)


@_u12_variant("cooking_salt", "sms", "intermediate", "cafe_pan_then_percent")
def _cooking_salt_intermediate_sms_cafe_pan_then_percent():
    pack = random.choice(_CS_SMS_I_PAN_PACKS)
    lost = pack["start_ml"] - pack["left_ml"]
    pct = round(100 * lost / pack["start_ml"])
    correct = "crystallisation becomes more likely as concentration rises"
    distractors = (
        "salt dissolves more as more water evaporates",
        "evaporation removes salt crystals first",
        "a rumour that percent lost has no meaning",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional community cafe reduces brine from {pack['start_ml']} mL "
        f"to {pack['left_ml']} mL by heating.</p>"
        "<p>(i) What percentage of the starting volume evaporated?</p>"
        "<p>(ii) Using that percentage from (i), crystallisation is more likely because</p>"
    )
    solution = (
        f"(i) <strong>{pct}</strong>%<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find percent evaporated, then link higher "
        "concentration to crystallisation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pct, letter),
            ("Percent evaporated", "Crystallisation link"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Calculate percent evaporated, then choose crystallisation link.",
        ),
    )


_CS_SMS_I_DISSOLVE_PACKS = (
    {"cold_g": 3, "hot_g": 11},
    {"cold_g": 7, "hot_g": 19},
    {"cold_g": 5, "hot_g": 14},
)


@_u12_variant("cooking_salt", "sms", "intermediate", "demo_dissolve_then_temp")
def _cooking_salt_intermediate_sms_demo_dissolve_then_temp():
    pack = random.choice(_CS_SMS_I_DISSOLVE_PACKS)
    diff = pack["hot_g"] - pack["cold_g"]
    correct = "warmer solvent particles move faster and dissolve solute quicker"
    distractors = (
        "cold water always dissolves more salt",
        "temperature has no effect on dissolving",
        "a rumour that salt cannot dissolve",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery demo dissolves {pack['cold_g']} g salt in cold "
        f"water and {pack['hot_g']} g in hot water in equal times.</p>"
        "<p>(i) How many more grams dissolved in hot water?</p>"
        "<p>(ii) Using that difference from (i), hot water dissolves faster because</p>"
    )
    solution = (
        f"(i) <strong>{diff}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract masses, then link warmer solvent "
        "to faster dissolving."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("Extra grams dissolved (g)", "Why hot water is faster"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find mass difference, then choose why hot is faster.",
        ),
    )


@_u12_variant("cooking_salt", "sms", "intermediate", "lab_saturated_then_crystal")
def _cooking_salt_intermediate_sms_lab_saturated_then_crystal():
    pack = random.choice(
        (
            {"dissolved_g": 34, "added_g": 40},
            {"dissolved_g": 28, "added_g": 32},
            {"dissolved_g": 40, "added_g": 48},
        )
    )
    undissolved = pack["added_g"] - pack["dissolved_g"]
    correct = "the solution was saturated and excess salt formed crystals"
    distractors = (
        "salt cannot form crystals in water",
        "all added salt always dissolves",
        "a rumour that saturation does not exist",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public lab dissolves {pack['dissolved_g']} g of "
        f"{pack['added_g']} g salt added to hot water.</p>"
        "<p>(i) How many grams of salt did not dissolve?</p>"
        "<p>(ii) Using that mass from (i), the solution was</p>"
    )
    solution = (
        f"(i) <strong>{undissolved}</strong> g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find undissolved mass, then name saturation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (undissolved, letter),
            ("Undissolved salt (g)", "What the bottom solid shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find undissolved mass, then choose what saturation means.",
        ),
    )


@_u12_variant("cooking_salt", "sms", "difficult", "recovery_order_then_pick")
def _cooking_salt_difficult_sms_recovery_order_then_pick():
    order_raw, order_bank = _u12_order_field(
        (
            "Heat the salt solution gently",
            "Water evaporates and volume falls",
            "Concentration rises until crystals nucleate",
        ),
        ("Cool before any evaporation",),
    )
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Evaporation removes solvent water",
            "Crystallisation forms solid salt",
        ),
        (
            "Salt molecules are destroyed by heat",
            "A rumour that crystals are plastic",
        ),
        2,
    )
    question = (
        "<p>A fictional salt-recovery workshop shows evaporation to crystals.</p>"
        "<p>(i) Order heat, evaporate, then crystallise.</p>"
        "<p>(ii) Using that sequence from (i), select the two key processes.</p>"
    )
    solution = (
        "(i) <strong>heat → evaporate → crystallise</strong><br>"
        "(ii) Evaporation and crystallisation explain the change."
    )
    hint = (
        "<strong>Key idea:</strong> Order the chain, then pick evaporation and "
        "crystallisation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Process order", "Key processes"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the chain, then select evaporation and crystallisation.",
        ),
    )


_CS_SMS_D_BRINE_PACKS = (
    {"weak_g": 6, "strong_g": 18},
    {"weak_g": 9, "strong_g": 27},
    {"weak_g": 4, "strong_g": 12},
)


@_u12_variant("cooking_salt", "sms", "difficult", "trial_brine_then_preserve")
def _cooking_salt_difficult_sms_trial_brine_then_preserve():
    pack = random.choice(_CS_SMS_D_BRINE_PACKS)
    ratio = pack["strong_g"] / pack["weak_g"]
    correct = "the stronger brine removes more water from microbial cells"
    distractors = (
        "weak brine always preserves better",
        "salt concentration has no preservation role",
        "a rumour that ratios do not matter",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional curing trial compares {pack['weak_g']} g and "
        f"{pack['strong_g']} g salt per 100 mL water.</p>"
        "<p>(i) How many times greater is the strong brine salt mass?</p>"
        "<p>(ii) Using that factor from (i), the stronger brine preserves better because</p>"
    )
    solution = (
        f"(i) <strong>{ratio:g}</strong>×<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Compare salt masses, then link higher "
        "concentration to preservation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (ratio, letter),
            ("Strong-to-weak factor", "Why stronger brine preserves better"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find mass ratio, then choose preservation reason.",
        ),
    )


_CS_SMS_D_LABEL_PACKS = (
    {"sodium_mg": 500, "portion_g": 125},
    {"sodium_mg": 350, "portion_g": 70},
    {"sodium_mg": 720, "portion_g": 180},
)


@_u12_variant("cooking_salt", "sms", "difficult", "public_label_then_critique")
def _cooking_salt_difficult_sms_public_label_then_critique():
    pack = random.choice(_CS_SMS_D_LABEL_PACKS)
    per_100 = round(100 * pack["sodium_mg"] / pack["portion_g"])
    correct = "compare the per-100 g sodium value to public health guidance"
    distractors = (
        "ignore sodium because labels are optional",
        "assume all salt is protein",
        "a rumour that sodium is unrelated to salt",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public snack label shows {pack['sodium_mg']} mg sodium "
        f"per {pack['portion_g']} g portion.</p>"
        "<p>(i) About how many mg sodium per 100 g is that?</p>"
        "<p>(ii) Using that per-100 g value from (i), a balanced critique should</p>"
    )
    solution = (
        f"(i) <strong>{per_100}</strong> mg per 100 g<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Scale sodium to per 100 g, then compare "
        "to public guidance."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (per_100, letter),
            ("Sodium per 100 g (mg)", "Balanced critique"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Scale to per 100 g, then choose how to critique.",
        ),
    )


COOKING_SALT_SMS_POOLS = {
    "foundational": [
        _cooking_salt_foundational_sms_kitchen_brine_then_more,
        _cooking_salt_foundational_sms_fair_evap_then_crystals,
        _cooking_salt_foundational_sms_cure_poster_order_then_why,
    ],
    "intermediate": [
        _cooking_salt_intermediate_sms_cafe_pan_then_percent,
        _cooking_salt_intermediate_sms_demo_dissolve_then_temp,
        _cooking_salt_intermediate_sms_lab_saturated_then_crystal,
    ],
    "difficult": [
        _cooking_salt_difficult_sms_recovery_order_then_pick,
        _cooking_salt_difficult_sms_trial_brine_then_preserve,
        _cooking_salt_difficult_sms_public_label_then_critique,
    ],
}

# ---------------------------------------------------------------------------
# cooking_fermentation — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CF_MS_F_YEAST_PACKS = (
    {"temp_c": 25, "hours": 2},
    {"temp_c": 30, "hours": 3},
    {"temp_c": 28, "hours": 2},
)


@_u12_variant("cooking_fermentation", "ms", "foundational", "yeast_temp_then_gas")
def _cooking_fermentation_foundational_ms_yeast_temp_then_gas():
    pack = random.choice(_CF_MS_F_YEAST_PACKS)
    correct = "carbon dioxide gas makes the dough rise"
    distractors = (
        "oxygen from photosynthesis inflates the dough",
        "yeast turns flour into metal",
        "a rumour that fermentation produces no gas",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional bread demo ferments yeast at {pack['temp_c']} °C for "
        f"{pack['hours']} hours.</p>"
        "<p>(i) What temperature in °C is used?</p>"
        "<p>(ii) Using that warm condition from (i), the rising dough shows</p>"
    )
    solution = (
        f"(i) <strong>{pack['temp_c']}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the fermentation temperature, then "
        "link yeast activity to CO₂ production."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["temp_c"], letter),
            ("Temperature (°C)", "What rising dough shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read temperature, then choose what gas causes rising.",
        ),
    )


@_u12_variant("cooking_fermentation", "ms", "foundational", "anaerobic_order_then_product")
def _cooking_fermentation_foundational_ms_anaerobic_order_then_product():
    order_raw, order_bank = _u12_order_field(
        (
            "Yeast breaks down sugar without oxygen",
            "Energy is released for the cell",
            "Carbon dioxide and ethanol form",
        ),
        ("Oxygen is required for every fermentation step",),
    )
    correct = "fermentation is anaerobic respiration by yeast"
    distractors = (
        "fermentation only happens in sunlight",
        "yeast is a plant that photosynthesises bread",
        "a rumour that yeast needs no sugar",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional brewery poster shows yeast fermentation.</p>"
        "<p>(i) Order sugar breakdown, energy release, then CO₂ and ethanol.</p>"
        "<p>(ii) Using that sequence from (i), the process is called</p>"
    )
    solution = (
        "(i) <strong>sugar → energy → products</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the fermentation steps, then name "
        "anaerobic respiration."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Fermentation order", "Process name"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose the process name.",
        ),
    )


@_u12_variant("cooking_fermentation", "ms", "foundational", "lactic_count_then_food")
def _cooking_fermentation_foundational_ms_lactic_count_then_food():
    foods = 2
    correct = "yoghurt and sauerkraut use lactic acid bacteria"
    distractors = (
        "only metal ores use lactic fermentation",
        "lactic acid bacteria need sunlight only",
        "a rumour that fermentation never makes acid",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional food-science chart lists yoghurt and sauerkraut as "
        "lactic-acid fermented foods.</p>"
        "<p>(i) How many fermented foods are named on the chart?</p>"
        "<p>(ii) Using that count from (i), both examples show</p>"
    )
    solution = (
        f"(i) <strong>{foods}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the named foods, then link them to "
        "lactic acid bacteria."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (foods, letter),
            ("Foods named", "What both examples show"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count foods, then choose the lactic acid link.",
        ),
    )


_CF_MS_I_BUBBLE_PACKS = (
    {"bubbles": 12, "minutes": 30},
    {"bubbles": 18, "minutes": 45},
    {"bubbles": 8, "minutes": 20},
)


@_u12_variant("cooking_fermentation", "ms", "intermediate", "bubble_rate_then_active")
def _cooking_fermentation_intermediate_ms_bubble_rate_then_active():
    pack = random.choice(_CF_MS_I_BUBBLE_PACKS)
    rate = round(pack["bubbles"] / pack["minutes"], 2)
    correct = "yeast is actively fermenting and producing carbon dioxide"
    distractors = (
        "no gas is being produced",
        "the dough is photosynthesising",
        "a rumour that bubbles mean the yeast is dead",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional dough log counts {pack['bubbles']} CO₂ bubbles in "
        f"{pack['minutes']} minutes.</p>"
        "<p>(i) What is the bubble rate per minute (bubbles/min)?</p>"
        "<p>(ii) Using that rate from (i), the log shows</p>"
    )
    solution = (
        f"(i) {pack['bubbles']}/{pack['minutes']} = "
        f"<strong>{rate:g}</strong> bubbles/min<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Divide bubbles by time, then link a steady "
        "rate to active fermentation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (rate, letter),
            ("Bubble rate (bubbles/min)", "What the log shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find bubbles per minute, then choose what it shows.",
        ),
    )


@_u12_variant("cooking_fermentation", "ms", "intermediate", "temp_compare_then_yeast")
def _cooking_fermentation_intermediate_ms_temp_compare_then_yeast():
    pack = random.choice(
        (
            {"cold_c": 5, "warm_c": 30},
            {"cold_c": 10, "warm_c": 35},
            {"cold_c": 8, "warm_c": 28},
        )
    )
    diff = pack["warm_c"] - pack["cold_c"]
    correct = "warmth closer to optimum speeds yeast metabolism up to a limit"
    distractors = (
        "yeast never works below 100 °C",
        "cold always ferments faster than warmth",
        "a rumour that temperature has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional trial compares fermentation at {pack['cold_c']} °C and "
        f"{pack['warm_c']} °C.</p>"
        "<p>(i) How many degrees warmer is the warm trial?</p>"
        "<p>(ii) Using that difference from (i), the warm trial usually rises "
        "faster because</p>"
    )
    solution = (
        f"(i) {pack['warm_c']} − {pack['cold_c']} = <strong>{diff}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the temperature gap, then link warmth "
        "to faster yeast activity."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("Temperature difference (°C)", "Why warm rises faster"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract temperatures, then choose why warm is faster.",
        ),
    )


@_u12_variant("cooking_fermentation", "ms", "intermediate", "yoghurt_ph_then_lactic")
def _cooking_fermentation_intermediate_ms_yoghurt_ph_then_lactic():
    pack = random.choice(
        (
            {"start_ph": 6, "end_ph": 4},
            {"start_ph": 7, "end_ph": 5},
            {"start_ph": 5, "end_ph": 3},
        )
    )
    drop = pack["start_ph"] - pack["end_ph"]
    correct = "lactic acid bacteria produce acid that lowers pH"
    distractors = (
        "pH rises during yoghurt fermentation",
        "bacteria remove all acid from milk",
        "a rumour that pH never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional yoghurt log shows pH falling from {pack['start_ph']} to "
        f"{pack['end_ph']}.</p>"
        + str(ph_scale(title="Fictional yoghurt fermentation pH scale"))
        + "<p>(i) By how many pH units did the reading drop?</p>"
        "<p>(ii) Using that drop from (i), the change happens because</p>"
    )
    solution = (
        f"(i) <strong>{drop}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract pH readings, then link the drop "
        "to lactic acid production."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (drop, letter),
            ("pH drop", "Why pH falls"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find pH drop, then choose why fermentation acidifies.",
        ),
    )


@_u12_variant("cooking_fermentation", "ms", "difficult", "conditions_pick_then_count")
def _cooking_fermentation_difficult_ms_conditions_pick_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Suitable warm temperature for yeast",
            "Sugars available as food for microbes",
        ),
        (
            "Direct sunlight is always required",
            "A rumour that microbes need no food",
        ),
        2,
    )
    factors = 2
    question = (
        "<p>A fictional fermentation exam lists temperature, sugar, oxygen level "
        "and time.</p>"
        "<p>(i) Select the two conditions yeast bread fermentation most needs.</p>"
        "<p>(ii) Using those two from (i), how many critical conditions did you "
        "select?</p>"
    )
    solution = (
        "(i) Warmth and sugar are critical for yeast bread.<br>"
        f"(ii) <strong>{factors}</strong> conditions selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick warmth and sugar for yeast, then "
        "count your selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, factors),
            ("Critical conditions", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select warmth and sugar, then count selections.",
        ),
    )


@_u12_variant("cooking_fermentation", "ms", "difficult", "sourdough_order_then_flavour")
def _cooking_fermentation_difficult_ms_sourdough_order_then_flavour():
    order_raw, order_bank = _u12_order_field(
        (
            "Wild yeast and bacteria colonise the starter",
            "Acids and gases build up over days",
            "Bread gains sour flavour and texture",
        ),
        ("Sterilise the starter with boiling oil first",),
    )
    correct = "long fermentation allows organic acids to develop flavour"
    distractors = (
        "flavour comes only from food colouring",
        "fermentation never changes taste",
        "a rumour that microbes add no flavour",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional sourdough bakery tracks a starter over several days.</p>"
        "<p>(i) Order colonise, acids/gases build, then flavour develops.</p>"
        "<p>(ii) Using that timeline from (i), sour flavour mainly comes because</p>"
    )
    solution = (
        "(i) <strong>colonise → build → flavour</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the starter timeline, then link "
        "acids to sour flavour."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Starter timeline", "Why flavour develops"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the timeline, then choose why flavour develops.",
        ),
    )


@_u12_variant("cooking_fermentation", "ms", "difficult", "safety_temp_then_stop")
def _cooking_fermentation_difficult_ms_safety_temp_then_stop():
    pack = random.choice(
        (
            {"safe_c": 4, "risk_c": 25},
            {"safe_c": 5, "risk_c": 30},
            {"safe_c": 3, "risk_c": 28},
        )
    )
    gap = pack["risk_c"] - pack["safe_c"]
    correct = "baking to a safe internal temperature stops active fermentation"
    distractors = (
        "fermentation continues forever after baking",
        "heat has no effect on microbes",
        "a rumour that baking is unrelated to safety",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional food-safety chart stores starter at {pack['safe_c']} °C "
        f"but risks spoilage above {pack['risk_c']} °C without baking.</p>"
        "<p>(i) How many degrees separate safe storage from the risk threshold?</p>"
        "<p>(ii) Using that gap from (i), finishing bread in a hot oven helps because</p>"
    )
    solution = (
        f"(i) {pack['risk_c']} − {pack['safe_c']} = <strong>{gap}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the temperature gap, then link baking "
        "to stopping microbes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (gap, letter),
            ("Temperature gap (°C)", "Why baking helps"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract temperatures, then choose why baking helps.",
        ),
    )


COOKING_FERMENTATION_MS_POOLS = {
    "foundational": [
        _cooking_fermentation_foundational_ms_yeast_temp_then_gas,
        _cooking_fermentation_foundational_ms_anaerobic_order_then_product,
        _cooking_fermentation_foundational_ms_lactic_count_then_food,
    ],
    "intermediate": [
        _cooking_fermentation_intermediate_ms_bubble_rate_then_active,
        _cooking_fermentation_intermediate_ms_temp_compare_then_yeast,
        _cooking_fermentation_intermediate_ms_yoghurt_ph_then_lactic,
    ],
    "difficult": [
        _cooking_fermentation_difficult_ms_conditions_pick_then_count,
        _cooking_fermentation_difficult_ms_sourdough_order_then_flavour,
        _cooking_fermentation_difficult_ms_safety_temp_then_stop,
    ],
}

# ---------------------------------------------------------------------------
# cooking_fermentation — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_CF_SMS_F_BAKERY_PACKS = (
    {"temp_c": 27, "hours": 2, "place": "fictional school bakery"},
    {"temp_c": 32, "hours": 3, "place": "fictional community oven"},
    {"temp_c": 29, "hours": 2, "place": "fictional cookery fair"},
)


@_u12_variant("cooking_fermentation", "sms", "foundational", "bakery_temp_then_gas")
def _cooking_fermentation_foundational_sms_bakery_temp_then_gas():
    pack = random.choice(_CF_SMS_F_BAKERY_PACKS)
    correct = "carbon dioxide gas makes the dough rise"
    distractors = (
        "oxygen from photosynthesis inflates the dough",
        "yeast turns flour into metal",
        "a rumour that fermentation produces no gas",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} ferments yeast at {pack['temp_c']} °C "
        f"for {pack['hours']} hours.</p>"
        "<p>(i) What temperature in °C is used?</p>"
        "<p>(ii) Using that warm condition from (i), the rising dough shows</p>"
    )
    solution = (
        f"(i) <strong>{pack['temp_c']}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read the temperature, then link yeast to "
        "CO₂ production."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["temp_c"], letter),
            ("Temperature (°C)", "What rising dough shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read temperature, then choose what gas causes rising.",
        ),
    )


@_u12_variant("cooking_fermentation", "sms", "foundational", "brew_poster_order_then_name")
def _cooking_fermentation_foundational_sms_brew_poster_order_then_name():
    order_raw, order_bank = _u12_order_field(
        (
            "Yeast breaks down sugar without oxygen",
            "Energy is released for the cell",
            "Carbon dioxide and ethanol form",
        ),
        ("Oxygen is required for every fermentation step",),
    )
    correct = "fermentation is anaerobic respiration by yeast"
    distractors = (
        "fermentation only happens in sunlight",
        "yeast is a plant that photosynthesises bread",
        "a rumour that yeast needs no sugar",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional brewery education poster shows yeast fermentation.</p>"
        "<p>(i) Order sugar breakdown, energy release, then CO₂ and ethanol.</p>"
        "<p>(ii) Using that sequence from (i), the process is called</p>"
    )
    solution = (
        "(i) <strong>sugar → energy → products</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the steps, then name anaerobic "
        "respiration."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Fermentation order", "Process name"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose the process name.",
        ),
    )


@_u12_variant("cooking_fermentation", "sms", "foundational", "chart_lactic_then_examples")
def _cooking_fermentation_foundational_sms_chart_lactic_then_examples():
    foods = 2
    correct = "yoghurt and sauerkraut use lactic acid bacteria"
    distractors = (
        "only metal ores use lactic fermentation",
        "lactic acid bacteria need sunlight only",
        "a rumour that fermentation never makes acid",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional food festival chart lists yoghurt and sauerkraut as "
        "lactic-acid fermented foods.</p>"
        "<p>(i) How many fermented foods are named on the chart?</p>"
        "<p>(ii) Using that count from (i), both examples show</p>"
    )
    solution = (
        f"(i) <strong>{foods}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the foods, then link them to lactic "
        "acid bacteria."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (foods, letter),
            ("Foods named", "What both examples show"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count foods, then choose the lactic acid link.",
        ),
    )


_CF_SMS_I_LOG_PACKS = (
    {"bubbles": 15, "minutes": 30},
    {"bubbles": 20, "minutes": 40},
    {"bubbles": 10, "minutes": 25},
)


@_u12_variant("cooking_fermentation", "sms", "intermediate", "dough_log_then_active")
def _cooking_fermentation_intermediate_sms_dough_log_then_active():
    pack = random.choice(_CF_SMS_I_LOG_PACKS)
    rate = round(pack["bubbles"] / pack["minutes"], 2)
    correct = "yeast is actively fermenting and producing carbon dioxide"
    distractors = (
        "no gas is being produced",
        "the dough is photosynthesising",
        "a rumour that bubbles mean the yeast is dead",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional bakery log counts {pack['bubbles']} CO₂ bubbles in "
        f"{pack['minutes']} minutes.</p>"
        "<p>(i) What is the bubble rate per minute (bubbles/min)?</p>"
        "<p>(ii) Using that rate from (i), the log shows</p>"
    )
    solution = (
        f"(i) <strong>{rate:g}</strong> bubbles/min<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Divide bubbles by time, then link rate to "
        "active fermentation."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (rate, letter),
            ("Bubble rate (bubbles/min)", "What the log shows"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find bubbles per minute, then choose what it shows.",
        ),
    )


_CF_SMS_I_TEMP_PACKS = (
    {"cold_c": 6, "warm_c": 32},
    {"cold_c": 12, "warm_c": 34},
    {"cold_c": 9, "warm_c": 27},
)


@_u12_variant("cooking_fermentation", "sms", "intermediate", "trial_temp_then_yeast")
def _cooking_fermentation_intermediate_sms_trial_temp_then_yeast():
    pack = random.choice(_CF_SMS_I_TEMP_PACKS)
    diff = pack["warm_c"] - pack["cold_c"]
    correct = "warmth closer to optimum speeds yeast metabolism up to a limit"
    distractors = (
        "yeast never works below 100 °C",
        "cold always ferments faster than warmth",
        "a rumour that temperature has no effect",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional fermentation trial compares {pack['cold_c']} °C and "
        f"{pack['warm_c']} °C.</p>"
        "<p>(i) How many degrees warmer is the warm trial?</p>"
        "<p>(ii) Using that difference from (i), the warm trial usually rises "
        "faster because</p>"
    )
    solution = (
        f"(i) <strong>{diff}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the temperature gap, then link warmth "
        "to faster yeast activity."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("Temperature difference (°C)", "Why warm rises faster"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract temperatures, then choose why warm is faster.",
        ),
    )


@_u12_variant("cooking_fermentation", "sms", "intermediate", "yoghurt_demo_ph_then_lactic")
def _cooking_fermentation_intermediate_sms_yoghurt_demo_ph_then_lactic():
    pack = random.choice(
        (
            {"start_ph": 6, "end_ph": 4},
            {"start_ph": 7, "end_ph": 5},
            {"start_ph": 5, "end_ph": 3},
        )
    )
    drop = pack["start_ph"] - pack["end_ph"]
    correct = "lactic acid bacteria produce acid that lowers pH"
    distractors = (
        "pH rises during yoghurt fermentation",
        "bacteria remove all acid from milk",
        "a rumour that pH never changes",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional yoghurt demo records pH falling from {pack['start_ph']} "
        f"to {pack['end_ph']}.</p>"
        + str(ph_scale(title="Fictional yoghurt demo pH scale"))
        + "<p>(i) By how many pH units did the reading drop?</p>"
        "<p>(ii) Using that drop from (i), the change happens because</p>"
    )
    solution = (
        f"(i) <strong>{drop}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract pH readings, then link drop to "
        "lactic acid."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (drop, letter),
            ("pH drop", "Why pH falls"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Find pH drop, then choose why fermentation acidifies.",
        ),
    )


@_u12_variant("cooking_fermentation", "sms", "difficult", "exam_pick_then_count")
def _cooking_fermentation_difficult_sms_exam_pick_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Suitable warm temperature for yeast",
            "Sugars available as food for microbes",
        ),
        (
            "Direct sunlight is always required",
            "A rumour that microbes need no food",
        ),
        2,
    )
    factors = 2
    question = (
        "<p>A fictional fermentation exam lists temperature, sugar, oxygen and time.</p>"
        "<p>(i) Select the two conditions yeast bread fermentation most needs.</p>"
        "<p>(ii) Using those two from (i), how many critical conditions did you "
        "select?</p>"
    )
    solution = (
        "(i) Warmth and sugar are critical for yeast bread.<br>"
        f"(ii) <strong>{factors}</strong> conditions selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick warmth and sugar, then count selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, factors),
            ("Critical conditions", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select warmth and sugar, then count selections.",
        ),
    )


@_u12_variant("cooking_fermentation", "sms", "difficult", "starter_order_then_flavour")
def _cooking_fermentation_difficult_sms_starter_order_then_flavour():
    order_raw, order_bank = _u12_order_field(
        (
            "Wild yeast and bacteria colonise the starter",
            "Acids and gases build up over days",
            "Bread gains sour flavour and texture",
        ),
        ("Sterilise the starter with boiling oil first",),
    )
    correct = "long fermentation allows organic acids to develop flavour"
    distractors = (
        "flavour comes only from food colouring",
        "fermentation never changes taste",
        "a rumour that microbes add no flavour",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional sourdough school tracks a starter over several days.</p>"
        "<p>(i) Order colonise, acids/gases build, then flavour develops.</p>"
        "<p>(ii) Using that timeline from (i), sour flavour mainly comes because</p>"
    )
    solution = (
        "(i) <strong>colonise → build → flavour</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the timeline, then link acids to sour "
        "flavour."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Starter timeline", "Why flavour develops"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the timeline, then choose why flavour develops.",
        ),
    )


@_u12_variant("cooking_fermentation", "sms", "difficult", "safety_chart_then_bake")
def _cooking_fermentation_difficult_sms_safety_chart_then_bake():
    pack = random.choice(
        (
            {"safe_c": 4, "risk_c": 26},
            {"safe_c": 5, "risk_c": 32},
            {"safe_c": 3, "risk_c": 29},
        )
    )
    gap = pack["risk_c"] - pack["safe_c"]
    correct = "baking to a safe internal temperature stops active fermentation"
    distractors = (
        "fermentation continues forever after baking",
        "heat has no effect on microbes",
        "a rumour that baking is unrelated to safety",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional food-safety chart stores starter at {pack['safe_c']} °C "
        f"but risks spoilage above {pack['risk_c']} °C without baking.</p>"
        "<p>(i) How many degrees separate safe storage from the risk threshold?</p>"
        "<p>(ii) Using that gap from (i), finishing bread in a hot oven helps because</p>"
    )
    solution = (
        f"(i) <strong>{gap}</strong> °C<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the temperature gap, then link baking "
        "to stopping microbes."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (gap, letter),
            ("Temperature gap (°C)", "Why baking helps"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract temperatures, then choose why baking helps.",
        ),
    )


COOKING_FERMENTATION_SMS_POOLS = {
    "foundational": [
        _cooking_fermentation_foundational_sms_bakery_temp_then_gas,
        _cooking_fermentation_foundational_sms_brew_poster_order_then_name,
        _cooking_fermentation_foundational_sms_chart_lactic_then_examples,
    ],
    "intermediate": [
        _cooking_fermentation_intermediate_sms_dough_log_then_active,
        _cooking_fermentation_intermediate_sms_trial_temp_then_yeast,
        _cooking_fermentation_intermediate_sms_yoghurt_demo_ph_then_lactic,
    ],
    "difficult": [
        _cooking_fermentation_difficult_sms_exam_pick_then_count,
        _cooking_fermentation_difficult_sms_starter_order_then_flavour,
        _cooking_fermentation_difficult_sms_safety_chart_then_bake,
    ],
}

# ---------------------------------------------------------------------------
# nutrition — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_NU_MS_F_LABEL_PACKS = (
    {"kcal": 200, "kj": 800},
    {"kcal": 150, "kj": 600},
    {"kcal": 250, "kj": 1000},
)


@_u12_variant("nutrition", "ms", "foundational", "label_kcal_then_kj")
def _nutrition_foundational_ms_label_kcal_then_kj():
    pack = random.choice(_NU_MS_F_LABEL_PACKS)
    calc_kj = pack["kcal"] * 4
    correct = "1 kcal is about 4 kJ on public labels"
    distractors = (
        "1 kcal equals 4000 kJ always",
        "kJ and kcal are unrelated units",
        "a rumour that labels never show energy",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public label shows {pack['kcal']} kcal and "
        f"{pack['kj']} kJ per serving.</p>"
        "<p>(i) Using 1 kcal = 4 kJ, what kJ matches the kcal value?</p>"
        "<p>(ii) Using that conversion from (i), the label relationship shows</p>"
    )
    solution = (
        f"(i) {pack['kcal']} × 4 = <strong>{calc_kj}</strong> kJ<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Multiply kcal by 4 for kJ, then recall "
        "the public conversion factor."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (calc_kj, letter),
            ("Energy (kJ)", "Label relationship"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Convert kcal to kJ, then choose the unit relationship.",
        ),
    )


@_u12_variant("nutrition", "ms", "foundational", "group_count_then_role")
def _nutrition_foundational_ms_group_count_then_role():
    groups = 3
    correct = "carbohydrate mainly supplies energy"
    distractors = (
        "carbohydrate is only found in metals",
        "fat never stores energy",
        "a rumour that nutrient groups do not exist",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional nutrition poster lists protein, fat and carbohydrate.</p>"
        "<p>(i) How many main nutrient groups are named?</p>"
        "<p>(ii) Using that count from (i), bread mainly provides</p>"
    )
    solution = (
        f"(i) <strong>{groups}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the three groups, then match bread "
        "to carbohydrate energy."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (groups, letter),
            ("Nutrient groups named", "What bread mainly provides"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count groups, then choose bread's main nutrient role.",
        ),
    )


@_u12_variant("nutrition", "ms", "foundational", "deficiency_pick_then_count")
def _nutrition_foundational_ms_deficiency_pick_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Iron deficiency can cause tiredness",
            "Vitamin C deficiency is linked to scurvy",
        ),
        (
            "A celebrity diet with no nutrients listed",
            "Plastic packaging as a vitamin source",
        ),
        2,
    )
    deficiencies = 2
    question = (
        "<p>A fictional public-health leaflet lists nutrient deficiencies.</p>"
        "<p>(i) Select the two evidence-based deficiency links.</p>"
        "<p>(ii) Using those two from (i), how many deficiencies did you select?</p>"
    )
    solution = (
        "(i) Iron–tiredness and vitamin C–scurvy are evidence-based.<br>"
        f"(ii) <strong>{deficiencies}</strong> selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick iron and vitamin C links, then count "
        "your selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, deficiencies),
            ("Deficiency links", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select iron and vitamin C links, then count selections.",
        ),
    )


_NU_MS_I_LABEL_PACKS = (
    {"kcal": 400, "protein_g": 8, "fat_g": 15},
    {"kcal": 320, "protein_g": 12, "fat_g": 10},
    {"kcal": 500, "protein_g": 6, "fat_g": 20},
)


@_u12_variant("nutrition", "ms", "intermediate", "label_macro_then_dense")
def _nutrition_intermediate_ms_label_macro_then_dense():
    pack = random.choice(_NU_MS_I_LABEL_PACKS)
    correct = "fat is the most energy-dense macronutrient per gram"
    distractors = (
        "protein always has more kcal per gram than fat",
        "carbohydrate is never on labels",
        "a rumour that macros are not measured",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public label shows {pack['kcal']} kcal, "
        f"{pack['protein_g']} g protein and {pack['fat_g']} g fat per serving.</p>"
        "<p>(i) What is the energy per serving in kcal?</p>"
        "<p>(ii) Using that energy from (i) and the fat mass on the label, a "
        "balanced comment notes</p>"
    )
    solution = (
        f"(i) <strong>{pack['kcal']}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read total kcal, then recall fat's high "
        "energy per gram."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["kcal"], letter),
            ("Energy (kcal)", "Balanced comment"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read kcal, then choose the energy-density fact.",
        ),
    )


@_u12_variant("nutrition", "ms", "intermediate", "claim_order_then_critique")
def _nutrition_intermediate_ms_claim_order_then_critique():
    order_raw, order_bank = _u12_order_field(
        (
            "Read the full ingredients list",
            "Check per-100 g values on the label",
            "Compare the claim to the evidence",
        ),
        ("Believe the advert because it is colourful",),
    )
    correct = "a 'low fat' claim can still be high in sugar or energy"
    distractors = (
        "all low-fat foods are automatically healthy",
        "ingredient lists are optional decoration",
        "a rumour that labels cannot be checked",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional snack advert claims 'low fat' on the front.</p>"
        "<p>(i) Order read ingredients, check per-100 g values, then compare "
        "claim to evidence.</p>"
        "<p>(ii) Using that critique from (i), a balanced conclusion is</p>"
    )
    solution = (
        "(i) <strong>ingredients → per-100 g → compare</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the critique steps, then note that "
        "one claim does not tell the whole story."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Critique order", "Balanced conclusion"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order critique steps, then choose balanced conclusion.",
        ),
    )


_NU_MS_I_PORTION_PACKS = (
    {"label_kcal": 300, "eaten": 2},
    {"label_kcal": 180, "eaten": 3},
    {"label_kcal": 220, "eaten": 2},
)


@_u12_variant("nutrition", "ms", "intermediate", "portion_count_then_kcal")
def _nutrition_intermediate_ms_portion_count_then_kcal():
    pack = random.choice(_NU_MS_I_PORTION_PACKS)
    total = pack["label_kcal"] * pack["eaten"]
    correct = "multiply per-serving kcal by the number of servings eaten"
    distractors = (
        "divide kcal by the number of servings",
        "ignore the label and guess",
        "a rumour that portions do not affect energy",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional canteen log records {pack['eaten']} servings of a "
        f"food labelled {pack['label_kcal']} kcal per serving.</p>"
        "<p>(i) What total energy in kcal was consumed?</p>"
        "<p>(ii) Using that total from (i), the calculation method was</p>"
    )
    solution = (
        f"(i) {pack['label_kcal']} × {pack['eaten']} = "
        f"<strong>{total}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Multiply kcal per serving by servings "
        "eaten, then name the method."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (total, letter),
            ("Total energy (kcal)", "Calculation method"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Multiply kcal by servings, then choose the method.",
        ),
    )


@_u12_variant("nutrition", "ms", "difficult", "label_compare_then_claim")
def _nutrition_difficult_ms_label_compare_then_claim():
    pack = random.choice(
        (
            {"a_kcal": 250, "b_kcal": 400, "a_sugar": 5, "b_sugar": 22},
            {"a_kcal": 180, "b_kcal": 350, "a_sugar": 3, "b_sugar": 18},
            {"a_kcal": 300, "b_kcal": 450, "a_sugar": 8, "b_sugar": 25},
        )
    )
    diff = pack["b_kcal"] - pack["a_kcal"]
    correct = (
        "product B is higher in both energy and sugar despite any front-of-pack claim"
    )
    distractors = (
        "product A is always healthier because its name is shorter",
        "sugar values on labels are decorative only",
        "a rumour that kcal cannot be compared",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional comparison lists product A at {pack['a_kcal']} kcal and "
        f"{pack['a_sugar']} g sugar; product B at {pack['b_kcal']} kcal and "
        f"{pack['b_sugar']} g sugar per 100 g.</p>"
        "<p>(i) How many more kcal per 100 g does product B provide?</p>"
        "<p>(ii) Using that difference from (i) and the sugar values, a fair "
        "critique concludes</p>"
    )
    solution = (
        f"(i) {pack['b_kcal']} − {pack['a_kcal']} = <strong>{diff}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the kcal gap, then compare both energy "
        "and sugar fairly."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("kcal difference", "Fair critique"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract kcal values, then choose the fair critique.",
        ),
    )


@_u12_variant("nutrition", "ms", "difficult", "deficiency_chain_then_advice")
def _nutrition_difficult_ms_deficiency_chain_then_advice():
    order_raw, order_bank = _u12_order_field(
        (
            "Identify the missing nutrient from public guidance",
            "Link the deficiency to a known symptom pattern",
            "Suggest dietary sources, not personal diagnosis",
        ),
        ("Diagnose a named person from one symptom",),
    )
    correct = "public guidance lists iron-rich foods without diagnosing anyone"
    distractors = (
        "tell a stranger their exact medical condition",
        "ignore symptoms and trust adverts",
        "a rumour that deficiencies cannot be discussed",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public-health case study discusses tiredness and low "
        "iron intake in a population table.</p>"
        "<p>(i) Order identify nutrient, link symptom pattern, suggest dietary "
        "sources.</p>"
        "<p>(ii) Using that sequence from (i), appropriate classroom advice is</p>"
    )
    solution = (
        "(i) <strong>identify → link → suggest sources</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the public-health steps, then keep "
        "advice general and non-diagnostic."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Advice sequence", "Appropriate classroom advice"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose appropriate advice.",
        ),
    )


@_u12_variant("nutrition", "ms", "difficult", "advert_pick_then_evidence")
def _nutrition_difficult_ms_advert_pick_then_evidence():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Per-100 g nutrition table on the pack",
            "Full ingredients list in order of mass",
        ),
        (
            "A celebrity endorsement with no data",
            "A front slogan with no numbers",
        ),
        2,
    )
    evidence = 2
    question = (
        "<p>A fictional sports-drink advert claims 'gives you energy' without "
        "numbers.</p>"
        "<p>(i) How many evidence types minimum are needed to test the claim?</p>"
        "<p>(ii) Using that count from (i), select the two acceptable public "
        "evidence types.</p>"
    )
    solution = (
        f"(i) <strong>{evidence}</strong><br>"
        "(ii) Nutrition table and ingredients list are acceptable."
    )
    hint = (
        "<strong>Key idea:</strong> Count evidence types needed, then pick "
        "label data over slogans."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (evidence, pick_raw),
            ("Evidence types needed", "Acceptable evidence"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count evidence types, then select label-based proof.",
        ),
    )


NUTRITION_MS_POOLS = {
    "foundational": [
        _nutrition_foundational_ms_label_kcal_then_kj,
        _nutrition_foundational_ms_group_count_then_role,
        _nutrition_foundational_ms_deficiency_pick_then_count,
    ],
    "intermediate": [
        _nutrition_intermediate_ms_label_macro_then_dense,
        _nutrition_intermediate_ms_claim_order_then_critique,
        _nutrition_intermediate_ms_portion_count_then_kcal,
    ],
    "difficult": [
        _nutrition_difficult_ms_label_compare_then_claim,
        _nutrition_difficult_ms_deficiency_chain_then_advice,
        _nutrition_difficult_ms_advert_pick_then_evidence,
    ],
}

# ---------------------------------------------------------------------------
# nutrition — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_NU_SMS_F_CANTEEN_PACKS = (
    {"kcal": 180, "kj": 720, "place": "fictional school canteen"},
    {"kcal": 220, "kj": 880, "place": "fictional sports-hall snack bar"},
    {"kcal": 160, "kj": 640, "place": "fictional library cafe"},
)


@_u12_variant("nutrition", "sms", "foundational", "canteen_kcal_then_kj")
def _nutrition_foundational_sms_canteen_kcal_then_kj():
    pack = random.choice(_NU_SMS_F_CANTEEN_PACKS)
    calc_kj = pack["kcal"] * 4
    correct = "1 kcal is about 4 kJ on public labels"
    distractors = (
        "1 kcal equals 4000 kJ always",
        "kJ and kcal are unrelated units",
        "a rumour that labels never show energy",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} label shows {pack['kcal']} kcal and "
        f"{pack['kj']} kJ per serving.</p>"
        "<p>(i) Using 1 kcal = 4 kJ, what kJ matches the kcal value?</p>"
        "<p>(ii) Using that conversion from (i), the label relationship shows</p>"
    )
    solution = (
        f"(i) {pack['kcal']} × 4 = <strong>{calc_kj}</strong> kJ<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Multiply kcal by 4, then recall the public "
        "conversion factor."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (calc_kj, letter),
            ("Energy (kJ)", "Label relationship"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Convert kcal to kJ, then choose the unit relationship.",
        ),
    )


@_u12_variant("nutrition", "sms", "foundational", "poster_groups_then_bread")
def _nutrition_foundational_sms_poster_groups_then_bread():
    groups = 3
    correct = "carbohydrate mainly supplies energy"
    distractors = (
        "carbohydrate is only found in metals",
        "fat never stores energy",
        "a rumour that nutrient groups do not exist",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional nutrition week poster lists protein, fat and carbohydrate.</p>"
        "<p>(i) How many main nutrient groups are named?</p>"
        "<p>(ii) Using that count from (i), bread mainly provides</p>"
    )
    solution = (
        f"(i) <strong>{groups}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the three groups, then match bread "
        "to carbohydrate energy."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (groups, letter),
            ("Nutrient groups named", "What bread mainly provides"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count groups, then choose bread's main nutrient role.",
        ),
    )


@_u12_variant("nutrition", "sms", "foundational", "leaflet_deficiency_then_count")
def _nutrition_foundational_sms_leaflet_deficiency_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Iron deficiency can cause tiredness",
            "Vitamin C deficiency is linked to scurvy",
        ),
        (
            "A celebrity diet with no nutrients listed",
            "Plastic packaging as a vitamin source",
        ),
        2,
    )
    deficiencies = 2
    question = (
        "<p>A fictional health-week leaflet lists nutrient deficiencies.</p>"
        "<p>(i) Select the two evidence-based deficiency links.</p>"
        "<p>(ii) Using those two from (i), how many deficiencies did you select?</p>"
    )
    solution = (
        "(i) Iron–tiredness and vitamin C–scurvy are evidence-based.<br>"
        f"(ii) <strong>{deficiencies}</strong> selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick iron and vitamin C links, then count "
        "selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, deficiencies),
            ("Deficiency links", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select iron and vitamin C links, then count selections.",
        ),
    )


_NU_SMS_I_SNACK_PACKS = (
    {"kcal": 380, "protein_g": 10, "fat_g": 14},
    {"kcal": 290, "protein_g": 8, "fat_g": 11},
    {"kcal": 420, "protein_g": 12, "fat_g": 18},
)


@_u12_variant("nutrition", "sms", "intermediate", "snack_label_then_dense")
def _nutrition_intermediate_sms_snack_label_then_dense():
    pack = random.choice(_NU_SMS_I_SNACK_PACKS)
    correct = "fat is the most energy-dense macronutrient per gram"
    distractors = (
        "protein always has more kcal per gram than fat",
        "carbohydrate is never on labels",
        "a rumour that macros are not measured",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional public snack label shows {pack['kcal']} kcal, "
        f"{pack['protein_g']} g protein and {pack['fat_g']} g fat per serving.</p>"
        "<p>(i) What is the energy per serving in kcal?</p>"
        "<p>(ii) Using that energy from (i) and the fat mass, a balanced comment notes</p>"
    )
    solution = (
        f"(i) <strong>{pack['kcal']}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read total kcal, then recall fat's high "
        "energy per gram."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pack["kcal"], letter),
            ("Energy (kcal)", "Balanced comment"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Read kcal, then choose the energy-density fact.",
        ),
    )


@_u12_variant("nutrition", "sms", "intermediate", "advert_critique_order_then_lowfat")
def _nutrition_intermediate_sms_advert_critique_order_then_lowfat():
    order_raw, order_bank = _u12_order_field(
        (
            "Read the full ingredients list",
            "Check per-100 g values on the label",
            "Compare the claim to the evidence",
        ),
        ("Believe the advert because it is colourful",),
    )
    correct = "a 'low fat' claim can still be high in sugar or energy"
    distractors = (
        "all low-fat foods are automatically healthy",
        "ingredient lists are optional decoration",
        "a rumour that labels cannot be checked",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional vending-machine advert claims 'low fat' on the front.</p>"
        "<p>(i) Order read ingredients, check per-100 g values, then compare "
        "claim to evidence.</p>"
        "<p>(ii) Using that critique from (i), a balanced conclusion is</p>"
    )
    solution = (
        "(i) <strong>ingredients → per-100 g → compare</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order critique steps, then note one claim "
        "does not tell the whole story."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Critique order", "Balanced conclusion"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order critique steps, then choose balanced conclusion.",
        ),
    )


_NU_SMS_I_LOG_PACKS = (
    {"label_kcal": 240, "servings": 2},
    {"label_kcal": 190, "servings": 3},
    {"label_kcal": 210, "servings": 2},
)


@_u12_variant("nutrition", "sms", "intermediate", "log_portions_then_kcal")
def _nutrition_intermediate_sms_log_portions_then_kcal():
    pack = random.choice(_NU_SMS_I_LOG_PACKS)
    total = pack["label_kcal"] * pack["servings"]
    correct = "multiply per-serving kcal by the number of servings eaten"
    distractors = (
        "divide kcal by the number of servings",
        "ignore the label and guess",
        "a rumour that portions do not affect energy",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional canteen log records {pack['servings']} servings of a "
        f"food labelled {pack['label_kcal']} kcal per serving.</p>"
        "<p>(i) What total energy in kcal was consumed?</p>"
        "<p>(ii) Using that total from (i), the calculation method was</p>"
    )
    solution = (
        f"(i) {pack['label_kcal']} × {pack['servings']} = "
        f"<strong>{total}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Multiply kcal by servings, then name the "
        "method."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (total, letter),
            ("Total energy (kcal)", "Calculation method"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Multiply kcal by servings, then choose the method.",
        ),
    )


@_u12_variant("nutrition", "sms", "difficult", "compare_products_then_critique")
def _nutrition_difficult_sms_compare_products_then_critique():
    pack = random.choice(
        (
            {"a_kcal": 210, "b_kcal": 390, "a_sugar": 4, "b_sugar": 20},
            {"a_kcal": 170, "b_kcal": 330, "a_sugar": 6, "b_sugar": 16},
            {"a_kcal": 260, "b_kcal": 410, "a_sugar": 7, "b_sugar": 24},
        )
    )
    diff = pack["b_kcal"] - pack["a_kcal"]
    correct = (
        "product B is higher in both energy and sugar despite any front-of-pack claim"
    )
    distractors = (
        "product A is always healthier because its name is shorter",
        "sugar values on labels are decorative only",
        "a rumour that kcal cannot be compared",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional supermarket comparison lists product A at {pack['a_kcal']} "
        f"kcal and {pack['a_sugar']} g sugar; product B at {pack['b_kcal']} kcal "
        f"and {pack['b_sugar']} g sugar per 100 g.</p>"
        "<p>(i) How many more kcal per 100 g does product B provide?</p>"
        "<p>(ii) Using that difference from (i) and the sugar values, a fair "
        "critique concludes</p>"
    )
    solution = (
        f"(i) <strong>{diff}</strong> kcal<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Find the kcal gap, then compare energy and "
        "sugar fairly."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (diff, letter),
            ("kcal difference", "Fair critique"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract kcal values, then choose the fair critique.",
        ),
    )


@_u12_variant("nutrition", "sms", "difficult", "health_case_order_then_advice")
def _nutrition_difficult_sms_health_case_order_then_advice():
    order_raw, order_bank = _u12_order_field(
        (
            "Identify the missing nutrient from public guidance",
            "Link the deficiency to a known symptom pattern",
            "Suggest dietary sources, not personal diagnosis",
        ),
        ("Diagnose a named person from one symptom",),
    )
    correct = "public guidance lists iron-rich foods without diagnosing anyone"
    distractors = (
        "tell a stranger their exact medical condition",
        "ignore symptoms and trust adverts",
        "a rumour that deficiencies cannot be discussed",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional public-health workshop uses a population table on "
        "tiredness and low iron intake.</p>"
        "<p>(i) Order identify nutrient, link symptom pattern, suggest dietary "
        "sources.</p>"
        "<p>(ii) Using that sequence from (i), appropriate classroom advice is</p>"
    )
    solution = (
        "(i) <strong>identify → link → suggest sources</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order public-health steps, then keep advice "
        "general and non-diagnostic."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Advice sequence", "Appropriate classroom advice"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the steps, then choose appropriate advice.",
        ),
    )


@_u12_variant("nutrition", "sms", "difficult", "drink_ad_pick_then_evidence")
def _nutrition_difficult_sms_drink_ad_pick_then_evidence():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Per-100 g nutrition table on the pack",
            "Full ingredients list in order of mass",
        ),
        (
            "A celebrity endorsement with no data",
            "A front slogan with no numbers",
        ),
        2,
    )
    evidence = 2
    question = (
        "<p>A fictional sports-drink billboard claims 'gives you energy' without "
        "numbers.</p>"
        "<p>(i) How many evidence types minimum are needed to test the claim?</p>"
        "<p>(ii) Using that count from (i), select the two acceptable public "
        "evidence types.</p>"
    )
    solution = (
        f"(i) <strong>{evidence}</strong><br>"
        "(ii) Nutrition table and ingredients list are acceptable."
    )
    hint = (
        "<strong>Key idea:</strong> Count evidence types, then pick label data "
        "over slogans."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (evidence, pick_raw),
            ("Evidence types needed", "Acceptable evidence"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count evidence types, then select label-based proof.",
        ),
    )


NUTRITION_SMS_POOLS = {
    "foundational": [
        _nutrition_foundational_sms_canteen_kcal_then_kj,
        _nutrition_foundational_sms_poster_groups_then_bread,
        _nutrition_foundational_sms_leaflet_deficiency_then_count,
    ],
    "intermediate": [
        _nutrition_intermediate_sms_snack_label_then_dense,
        _nutrition_intermediate_sms_advert_critique_order_then_lowfat,
        _nutrition_intermediate_sms_log_portions_then_kcal,
    ],
    "difficult": [
        _nutrition_difficult_sms_compare_products_then_critique,
        _nutrition_difficult_sms_health_case_order_then_advice,
        _nutrition_difficult_sms_drink_ad_pick_then_evidence,
    ],
}

# ---------------------------------------------------------------------------
# healthy_meal_project — multi_step (F, I, D)
# ---------------------------------------------------------------------------

_HMP_MS_F_READY_PACKS = (
    {"items": 4, "checked": 3},
    {"items": 5, "checked": 4},
    {"items": 6, "checked": 5},
)


@_u12_variant("healthy_meal_project", "ms", "foundational", "ready_count_then_missing")
def _healthy_meal_project_foundational_ms_ready_count_then_missing():
    pack = random.choice(_HMP_MS_F_READY_PACKS)
    missing = pack["items"] - pack["checked"]
    correct = "wash hands and tie back long hair before handling food"
    distractors = (
        "taste raw poultry to check freshness",
        "skip the written method and improvise",
        "a rumour that hygiene is optional",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional project checklist lists {pack['items']} readiness items; "
        f"{pack['checked']} are ticked.</p>"
        "<p>(i) How many readiness items are still unchecked?</p>"
        "<p>(ii) Using that gap from (i), the most important missing step is often</p>"
    )
    solution = (
        f"(i) {pack['items']} − {pack['checked']} = <strong>{missing}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract checked from total, then prioritise "
        "hygiene before cooking."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (missing, letter),
            ("Unchecked items", "Important missing step"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count unchecked items, then choose the hygiene step.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "foundational", "hygiene_order_then_why")
def _healthy_meal_project_foundational_ms_hygiene_order_then_why():
    order_raw, order_bank = _u12_order_field(
        (
            "Wash hands with soap and water",
            "Prepare a clean work surface",
            "Handle raw and cooked foods separately",
        ),
        ("Mix raw meat with ready-to-eat salad",),
    )
    correct = "cross-contamination spreads bacteria from raw to ready-to-eat food"
    distractors = (
        "hygiene has no effect on food safety",
        "raw and cooked foods should always touch",
        "a rumour that washing hands is decorative",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional cookery-project poster lists hygiene steps.</p>"
        "<p>(i) Order wash hands, clean surface, separate raw and cooked.</p>"
        "<p>(ii) Using that order from (i), separating foods prevents</p>"
    )
    solution = (
        "(i) <strong>wash → clean → separate</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order hygiene steps, then link separation "
        "to cross-contamination."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Hygiene order", "What separation prevents"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order hygiene steps, then choose what separation prevents.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "foundational", "method_steps_then_repeat")
def _healthy_meal_project_foundational_ms_method_steps_then_repeat():
    steps = 4
    correct = "another group could follow the same written method and get similar results"
    distractors = (
        "methods should stay secret so results cannot be checked",
        "repeatability is impossible in cookery",
        "a rumour that written methods are useless",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional project method has 4 numbered steps another class could copy.</p>"
        "<p>(i) How many numbered steps are in the method?</p>"
        "<p>(ii) Using that count from (i), a clear written method means</p>"
    )
    solution = (
        f"(i) <strong>{steps}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the method steps, then link a clear "
        "method to repeatability."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (steps, letter),
            ("Method steps", "What a clear method means"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count steps, then choose what repeatability means.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "intermediate", "evidence_table_then_balanced")
def _healthy_meal_project_intermediate_ms_evidence_table_then_balanced():
    pack = random.choice(
        (
            {"groups": 3, "veg": 2, "protein": 1},
            {"groups": 3, "veg": 1, "protein": 2},
            {"groups": 3, "veg": 2, "protein": 1},
        )
    )
    balance_score = pack["veg"] + pack["protein"]
    correct = "the meal includes vegetables and a protein source but portion balance still matters"
    distractors = (
        "any meal with one food group is always perfect",
        "project evidence cannot include tables",
        "a rumour that balance is not graded",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional project evidence table shows {pack['veg']} vegetable "
        f"portions and {pack['protein']} protein portions across "
        f"{pack['groups']} nutrient groups planned.</p>"
        "<p>(i) How many of the two key portions (vegetable + protein) are "
        "represented in the counts?</p>"
        "<p>(ii) Using that total from (i), a balanced project comment notes</p>"
    )
    solution = (
        f"(i) {pack['veg']} + {pack['protein']} = <strong>{balance_score}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Add vegetable and protein portions, then "
        "comment on balance fairly."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (balance_score, letter),
            ("Key portions counted", "Balanced comment"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Add key portions, then choose a balanced comment.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "intermediate", "risk_pick_then_count")
def _healthy_meal_project_intermediate_ms_risk_pick_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Raw meat juices contacting a salad board",
            "Leaving cooked rice warm for many hours",
        ),
        (
            "Washing hands before handling food",
            "Using a separate board for raw meat",
        ),
        2,
    )
    risks = 2
    question = (
        "<p>A fictional project risk log lists four kitchen situations.</p>"
        "<p>(i) Select the two highest food-safety risks.</p>"
        "<p>(ii) Using those two from (i), how many serious risks did you select?</p>"
    )
    solution = (
        "(i) Raw juices on salad board and warm rice are serious risks.<br>"
        f"(ii) <strong>{risks}</strong> serious risks."
    )
    hint = (
        "<strong>Key idea:</strong> Pick cross-contamination and temperature "
        "abuse risks, then count them."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, risks),
            ("Serious risks", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two serious risks, then count selections.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "intermediate", "iterate_order_then_improve")
def _healthy_meal_project_intermediate_ms_iterate_order_then_improve():
    order_raw, order_bank = _u12_order_field(
        (
            "Cook a first trial using the written method",
            "Record what worked and what did not",
            "Change one variable and test again",
        ),
        ("Change every variable at once with no records",),
    )
    correct = "changing one variable makes it clear what caused any improvement"
    distractors = (
        "iteration means never changing the method",
        "records are unnecessary in a project",
        "a rumour that trials cannot be repeated",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional meal-project journal describes improving a recipe.</p>"
        "<p>(i) Order first trial, record results, change one variable.</p>"
        "<p>(ii) Using that iteration order from (i), the method improves because</p>"
    )
    solution = (
        "(i) <strong>trial → record → one change</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order iteration steps, then explain fair "
        "testing with one change."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Iteration order", "Why the method improves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order iteration steps, then choose why one change helps.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "difficult", "rubric_score_then_reflect")
def _healthy_meal_project_difficult_ms_rubric_score_then_reflect():
    pack = random.choice(
        (
            {"ready": 4, "ready_max": 5, "hygiene": 3, "hygiene_max": 4},
            {"ready": 5, "ready_max": 6, "hygiene": 4, "hygiene_max": 5},
            {"ready": 3, "ready_max": 4, "hygiene": 2, "hygiene_max": 3},
        )
    )
    ready_pct = round(100 * pack["ready"] / pack["ready_max"])
    correct = "identify which rubric row to improve next using the evidence table"
    distractors = (
        "ignore the rubric because only taste matters",
        "change every score without evidence",
        "a rumour that reflection is not part of the project",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional project rubric scores readiness {pack['ready']}/"
        f"{pack['ready_max']} and hygiene {pack['hygiene']}/{pack['hygiene_max']}.</p>"
        "<p>(i) What percentage of readiness points were awarded?</p>"
        "<p>(ii) Using that percentage from (i), the best next reflection step is to</p>"
    )
    solution = (
        f"(i) {pack['ready']}/{pack['ready_max']} × 100 = "
        f"<strong>{ready_pct}</strong>%<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Convert readiness to a percentage, then "
        "use the rubric to plan improvement."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (ready_pct, letter),
            ("Readiness (%)", "Best reflection step"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Calculate readiness %, then choose the reflection step.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "difficult", "evidence_chain_then_claim")
def _healthy_meal_project_difficult_ms_evidence_chain_then_claim():
    order_raw, order_bank = _u12_order_field(
        (
            "State the project aim in one sentence",
            "Link method steps to hygiene and balance evidence",
            "Judge whether the evidence supports the aim",
        ),
        ("Claim success with no recorded evidence",),
    )
    correct = "only evidence from the written method and table can support the claim"
    distractors = (
        "a colourful poster alone proves a healthy meal",
        "peer praise replaces all data",
        "a rumour that evidence is optional",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional project report claims a 'healthy balanced meal' was planned.</p>"
        "<p>(i) Order state aim, link evidence, judge support for the aim.</p>"
        "<p>(ii) Using that chain from (i), a scientific conclusion requires</p>"
    )
    solution = (
        "(i) <strong>aim → link evidence → judge</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the evidence chain, then insist on "
        "method and table proof."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Evidence chain order", "What a conclusion requires"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the chain, then choose what evidence is required.",
        ),
    )


@_u12_variant("healthy_meal_project", "ms", "difficult", "safety_pick_then_reflect")
def _healthy_meal_project_difficult_ms_safety_pick_then_reflect():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Record oven temperature and cooking time in the log",
            "Note which hygiene steps were completed before prep",
        ),
        (
            "Skip hand washing to save time",
            "Reuse a raw-meat board for salad without cleaning",
        ),
        2,
    )
    evidence_items = 2
    question = (
        "<p>A fictional project audit lists four actions from a cookery session.</p>"
        "<p>(i) Select the two actions that count as graded evidence.</p>"
        "<p>(ii) Using those two from (i), how many evidence items did you select?</p>"
    )
    solution = (
        "(i) Temperature/time log and hygiene checklist are evidence.<br>"
        f"(ii) <strong>{evidence_items}</strong> evidence items."
    )
    hint = (
        "<strong>Key idea:</strong> Pick recorded method and hygiene evidence, "
        "then count selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, evidence_items),
            ("Evidence actions", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two evidence actions, then count selections.",
        ),
    )


HEALTHY_MEAL_PROJECT_MS_POOLS = {
    "foundational": [
        _healthy_meal_project_foundational_ms_ready_count_then_missing,
        _healthy_meal_project_foundational_ms_hygiene_order_then_why,
        _healthy_meal_project_foundational_ms_method_steps_then_repeat,
    ],
    "intermediate": [
        _healthy_meal_project_intermediate_ms_evidence_table_then_balanced,
        _healthy_meal_project_intermediate_ms_risk_pick_then_count,
        _healthy_meal_project_intermediate_ms_iterate_order_then_improve,
    ],
    "difficult": [
        _healthy_meal_project_difficult_ms_rubric_score_then_reflect,
        _healthy_meal_project_difficult_ms_evidence_chain_then_claim,
        _healthy_meal_project_difficult_ms_safety_pick_then_reflect,
    ],
}

# ---------------------------------------------------------------------------
# healthy_meal_project — situational_multi_step (F, I, D)
# ---------------------------------------------------------------------------

_HMP_SMS_F_CLASS_PACKS = (
    {"items": 5, "checked": 3, "place": "fictional school cookery room"},
    {"items": 4, "checked": 2, "place": "fictional community kitchen"},
    {"items": 6, "checked": 4, "place": "fictional after-school club"},
)


@_u12_variant("healthy_meal_project", "sms", "foundational", "class_ready_then_missing")
def _healthy_meal_project_foundational_sms_class_ready_then_missing():
    pack = random.choice(_HMP_SMS_F_CLASS_PACKS)
    missing = pack["items"] - pack["checked"]
    correct = "wash hands and tie back long hair before handling food"
    distractors = (
        "taste raw poultry to check freshness",
        "skip the written method and improvise",
        "a rumour that hygiene is optional",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional {pack['place']} checklist lists {pack['items']} "
        f"readiness items; {pack['checked']} are ticked.</p>"
        "<p>(i) How many readiness items are still unchecked?</p>"
        "<p>(ii) Using that gap from (i), the most important missing step is often</p>"
    )
    solution = (
        f"(i) <strong>{missing}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract checked from total, then prioritise "
        "hygiene."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (missing, letter),
            ("Unchecked items", "Important missing step"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count unchecked items, then choose the hygiene step.",
        ),
    )


@_u12_variant("healthy_meal_project", "sms", "foundational", "workshop_hygiene_then_cross")
def _healthy_meal_project_foundational_sms_workshop_hygiene_then_cross():
    order_raw, order_bank = _u12_order_field(
        (
            "Wash hands with soap and water",
            "Prepare a clean work surface",
            "Handle raw and cooked foods separately",
        ),
        ("Mix raw meat with ready-to-eat salad",),
    )
    correct = "cross-contamination spreads bacteria from raw to ready-to-eat food"
    distractors = (
        "hygiene has no effect on food safety",
        "raw and cooked foods should always touch",
        "a rumour that washing hands is decorative",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional cookery-workshop poster lists hygiene steps.</p>"
        "<p>(i) Order wash hands, clean surface, separate raw and cooked.</p>"
        "<p>(ii) Using that order from (i), separating foods prevents</p>"
    )
    solution = (
        "(i) <strong>wash → clean → separate</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order hygiene steps, then link separation "
        "to cross-contamination."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Hygiene order", "What separation prevents"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order hygiene steps, then choose what separation prevents.",
        ),
    )


@_u12_variant("healthy_meal_project", "sms", "foundational", "club_method_then_repeat")
def _healthy_meal_project_foundational_sms_club_method_then_repeat():
    steps = 4
    correct = "another group could follow the same written method and get similar results"
    distractors = (
        "methods should stay secret so results cannot be checked",
        "repeatability is impossible in cookery",
        "a rumour that written methods are useless",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional after-school club method has 4 numbered steps another "
        "group could copy.</p>"
        "<p>(i) How many numbered steps are in the method?</p>"
        "<p>(ii) Using that count from (i), a clear written method means</p>"
    )
    solution = (
        f"(i) <strong>{steps}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count method steps, then link a clear method "
        "to repeatability."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (steps, letter),
            ("Method steps", "What a clear method means"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count steps, then choose what repeatability means.",
        ),
    )


_HMP_SMS_I_TABLE_PACKS = (
    {"veg": 2, "protein": 1},
    {"veg": 1, "protein": 2},
    {"veg": 2, "protein": 2},
)


@_u12_variant("healthy_meal_project", "sms", "intermediate", "fair_table_then_balanced")
def _healthy_meal_project_intermediate_sms_fair_table_then_balanced():
    pack = random.choice(_HMP_SMS_I_TABLE_PACKS)
    balance_score = pack["veg"] + pack["protein"]
    correct = "the meal includes vegetables and a protein source but portion balance still matters"
    distractors = (
        "any meal with one food group is always perfect",
        "project evidence cannot include tables",
        "a rumour that balance is not graded",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery-fair evidence table shows {pack['veg']} vegetable "
        f"portions and {pack['protein']} protein portions planned.</p>"
        "<p>(i) How many of the two key portions (vegetable + protein) are counted?</p>"
        "<p>(ii) Using that total from (i), a balanced project comment notes</p>"
    )
    solution = (
        f"(i) <strong>{balance_score}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Add vegetable and protein portions, then "
        "comment on balance fairly."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (balance_score, letter),
            ("Key portions counted", "Balanced comment"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Add key portions, then choose a balanced comment.",
        ),
    )


@_u12_variant("healthy_meal_project", "sms", "intermediate", "kitchen_risk_then_count")
def _healthy_meal_project_intermediate_sms_kitchen_risk_then_count():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Raw meat juices contacting a salad board",
            "Leaving cooked rice warm for many hours",
        ),
        (
            "Washing hands before handling food",
            "Using a separate board for raw meat",
        ),
        2,
    )
    risks = 2
    question = (
        "<p>A fictional community-kitchen risk log lists four situations.</p>"
        "<p>(i) Select the two highest food-safety risks.</p>"
        "<p>(ii) Using those two from (i), how many serious risks did you select?</p>"
    )
    solution = (
        "(i) Raw juices on salad board and warm rice are serious risks.<br>"
        f"(ii) <strong>{risks}</strong> serious risks."
    )
    hint = (
        "<strong>Key idea:</strong> Pick cross-contamination and temperature "
        "abuse risks, then count them."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, risks),
            ("Serious risks", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two serious risks, then count selections.",
        ),
    )


@_u12_variant("healthy_meal_project", "sms", "intermediate", "journal_iterate_then_improve")
def _healthy_meal_project_intermediate_sms_journal_iterate_then_improve():
    order_raw, order_bank = _u12_order_field(
        (
            "Cook a first trial using the written method",
            "Record what worked and what did not",
            "Change one variable and test again",
        ),
        ("Change every variable at once with no records",),
    )
    correct = "changing one variable makes it clear what caused any improvement"
    distractors = (
        "iteration means never changing the method",
        "records are unnecessary in a project",
        "a rumour that trials cannot be repeated",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional meal-project journal at a cookery fair describes improving "
        "a recipe.</p>"
        "<p>(i) Order first trial, record results, change one variable.</p>"
        "<p>(ii) Using that iteration order from (i), the method improves because</p>"
    )
    solution = (
        "(i) <strong>trial → record → one change</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order iteration steps, then explain fair "
        "testing with one change."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Iteration order", "Why the method improves"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order iteration steps, then choose why one change helps.",
        ),
    )


_HMP_SMS_D_RUBRIC_PACKS = (
    {"ready": 4, "ready_max": 5},
    {"ready": 5, "ready_max": 6},
    {"ready": 3, "ready_max": 4},
)


@_u12_variant("healthy_meal_project", "sms", "difficult", "fair_rubric_then_reflect")
def _healthy_meal_project_difficult_sms_fair_rubric_then_reflect():
    pack = random.choice(_HMP_SMS_D_RUBRIC_PACKS)
    ready_pct = round(100 * pack["ready"] / pack["ready_max"])
    correct = "identify which rubric row to improve next using the evidence table"
    distractors = (
        "ignore the rubric because only taste matters",
        "change every score without evidence",
        "a rumour that reflection is not part of the project",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        f"<p>A fictional cookery-fair rubric awards {pack['ready']}/"
        f"{pack['ready_max']} readiness points.</p>"
        "<p>(i) What percentage of readiness points were awarded?</p>"
        "<p>(ii) Using that percentage from (i), the best next reflection step is to</p>"
    )
    solution = (
        f"(i) <strong>{ready_pct}</strong>%<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Convert readiness to a percentage, then "
        "use the rubric to plan improvement."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (ready_pct, letter),
            ("Readiness (%)", "Best reflection step"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Calculate readiness %, then choose the reflection step.",
        ),
    )


@_u12_variant("healthy_meal_project", "sms", "difficult", "report_chain_then_claim")
def _healthy_meal_project_difficult_sms_report_chain_then_claim():
    order_raw, order_bank = _u12_order_field(
        (
            "State the project aim in one sentence",
            "Link method steps to hygiene and balance evidence",
            "Judge whether the evidence supports the aim",
        ),
        ("Claim success with no recorded evidence",),
    )
    correct = "only evidence from the written method and table can support the claim"
    distractors = (
        "a colourful poster alone proves a healthy meal",
        "peer praise replaces all data",
        "a rumour that evidence is optional",
    )
    options, letter = _u12_mcq_field(correct, distractors)
    question = (
        "<p>A fictional project display claims a 'healthy balanced meal' was planned.</p>"
        "<p>(i) Order state aim, link evidence, judge support for the aim.</p>"
        "<p>(ii) Using that chain from (i), a scientific conclusion requires</p>"
    )
    solution = (
        "(i) <strong>aim → link evidence → judge</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order the evidence chain, then insist on "
        "method and table proof."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Evidence chain order", "What a conclusion requires"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the chain, then choose what evidence is required.",
        ),
    )


@_u12_variant("healthy_meal_project", "sms", "difficult", "audit_pick_then_evidence")
def _healthy_meal_project_difficult_sms_audit_pick_then_evidence():
    pick_raw, pick_bank, pick_count = _u12_pick_field(
        (
            "Record oven temperature and cooking time in the log",
            "Note which hygiene steps were completed before prep",
        ),
        (
            "Skip hand washing to save time",
            "Reuse a raw-meat board for salad without cleaning",
        ),
        2,
    )
    evidence_items = 2
    question = (
        "<p>A fictional project audit lists four actions from a public cookery session.</p>"
        "<p>(i) Select the two actions that count as graded evidence.</p>"
        "<p>(ii) Using those two from (i), how many evidence items did you select?</p>"
    )
    solution = (
        "(i) Temperature/time log and hygiene checklist are evidence.<br>"
        f"(ii) <strong>{evidence_items}</strong> evidence items."
    )
    hint = (
        "<strong>Key idea:</strong> Pick recorded method and hygiene evidence, "
        "then count selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, evidence_items),
            ("Evidence actions", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two evidence actions, then count selections.",
        ),
    )


HEALTHY_MEAL_PROJECT_SMS_POOLS = {
    "foundational": [
        _healthy_meal_project_foundational_sms_class_ready_then_missing,
        _healthy_meal_project_foundational_sms_workshop_hygiene_then_cross,
        _healthy_meal_project_foundational_sms_club_method_then_repeat,
    ],
    "intermediate": [
        _healthy_meal_project_intermediate_sms_fair_table_then_balanced,
        _healthy_meal_project_intermediate_sms_kitchen_risk_then_count,
        _healthy_meal_project_intermediate_sms_journal_iterate_then_improve,
    ],
    "difficult": [
        _healthy_meal_project_difficult_sms_fair_rubric_then_reflect,
        _healthy_meal_project_difficult_sms_report_chain_then_claim,
        _healthy_meal_project_difficult_sms_audit_pick_then_evidence,
    ],
}
