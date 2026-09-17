"""S2 Unit 2.2 Health — 2.2.1–2.2.5."""
import random

from generators.eursc.s2_unit22_health_advanced import (
    DEPENDENCE_ADDICTION_MS_POOLS,
    DEPENDENCE_ADDICTION_SMS_POOLS,
    HEALTHY_LIVING_MS_POOLS,
    HEALTHY_LIVING_SMS_POOLS,
    INFECTIOUS_DISEASE_MS_POOLS,
    NONINFECTIOUS_DISEASE_MS_POOLS,
    NONINFECTIOUS_DISEASE_SMS_POOLS,
    TOBACCO_MS_POOLS,
    TOBACCO_SMS_POOLS,
)
from generators.eursc.science_shared import (
    bind_eursc_topic,
    habit_bars,
    infection_chain,
    outbreak_bars,
)
from generators.shared.utils import (
    graded_answer_number_fields,
    make_graded_problem,
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import (
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from models.svg_kit import bar_chart

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


_HL_MCQ, _HL_NUM, _HL_KEY, _HL_ORD, _HL_PICK = _topic_bank("healthy_living")
_ID_MCQ, _ID_NUM, _ID_KEY, _ID_ORD, _ID_PICK = _topic_bank("infectious_disease")
_NI_MCQ, _NI_NUM, _NI_KEY, _NI_ORD, _NI_PICK = _topic_bank("noninfectious_disease")
_DA_MCQ, _DA_NUM, _DA_KEY, _DA_ORD, _DA_PICK = _topic_bank("dependence_addiction")
_TB_MCQ, _TB_NUM, _TB_KEY, _TB_ORD, _TB_PICK = _topic_bank("tobacco")

_DIET_BANK = (
    {"id": "mix", "text": "A balanced diet mixes food groups over time"},
    {"id": "activity", "text": "Regular physical activity supports health"},
    {"id": "rank", "text": "Health is ranking classmates by body shape"},
    {"id": "survey", "text": "The quiz should collect private meal lists"},
)
_MIND_BANK = (
    {"id": "mental", "text": "Mental health is part of health"},
    {"id": "signpost", "text": "Personal distress is for a trusted adult or qualified help, not this app"},
    {"id": "joke", "text": "Mental illness is only a joke in a group chat"},
    {"id": "rank_mood", "text": "Pupils must compare moods in the quiz"},
)
_HABIT_BANK = (
    {"id": "sleep", "text": "Sleep is a health need, not a contest"},
    {"id": "screens", "text": "Unmanaged late screens can crowd out sleep"},
    {"id": "respect", "text": "Respectful relationships are a health idea"},
    {"id": "spy", "text": "The app should store who a pupil sits with at lunch"},
)
_MICRO_BANK = (
    {"id": "live", "text": "The microbiome is living microorganisms that interact with the body"},
    {"id": "not_vote", "text": "A microbiome is not a class vote on favourite snacks"},
    {"id": "all_harm", "text": "Every microorganism in the body is always a pathogen"},
    {"id": "confession", "text": "Pupils must list private gut symptoms"},
)

_HL_POOLS = {
    "foundational": [
        _HL_MCQ("foundational", "diet", "A balanced diet is", _mcq_opts("one magic food eaten in large amounts to replace all the others", "a mix of food groups over time so the body gets what it needs", "only fruit and vegetables, with no fats or sugars at all", "the same set of meals eaten at exactly the same times every day"), "B", "Mix over time, not one food.", "Think of eating as a mix of groups over days, not one magic item or a single food group."),
        _HL_MCQ("foundational", "activity", "Regular physical activity is modelled as", _mcq_opts("something only athletes need, since ordinary bodies rest enough", "something that can support health, using public evidence", "a way to burn off any food, so diet then stops mattering", "a replacement for sleep, since moving keeps the body awake"), "B", "Public health idea, not an athletes-only one.", "Look for the option that treats movement as a public-health idea, not an athletes-only one or a replacement for sleep."),
        _HL_MCQ("foundational", "mental", "Mental health is", _mcq_opts("separate from health, because only the body can be ill", "part of health; personal distress is signposted to qualified help", "part of health; distress should be shared with the class for advice", "part of health; the app can diagnose distress from quiz answers"), "B", "Health includes mind; no disclosure.", "Health includes the mind. Distress is pointed to real help, not shared with the class or diagnosed by the app."),
        _HL_MCQ("foundational", "micro", "The microbiome is", _mcq_opts("harmful germs that must all be removed from the body", "living microorganisms that interact with the body", "the body's own cells that fight off every infection", "a single large organism living inside the gut"), "B", "Living microbes, not all harmful.", "This is a community of living things that live with a person, not only harmful germs and not the body's own cells."),
        _HL_MCQ("foundational", "sleep", "Sleep is", _mcq_opts("a habit that the body can train itself to do without", "a health need that late screens can crowd out", "wasted time that regular exercise can replace", "a need that late screens help by tiring the eyes"), "B", "Sleep vs unmanaged screens.", "Late unmanaged screens can steal rest time. Rest is a need, not a habit the body can drop."),
        _HL_MCQ("foundational", "sleep_bar", "<p>Which letter is the tall sleep bar?</p>" + str(habit_bars(title="Sleep bar")), _mcq_opts("C", "A", "B", "all three bars are equal"), "B", "A is sleep.", "Find the tallest bar on the sketch and match its letter."),
        _HL_KEY("foundational", "diet_word", "Write the word for the usual mix of foods a person eats over time.", "diet", "Diet means the mix of foods, not a confession.", "Think of the everyday pattern of meals across a week, not one snack or a private list."),
        _HL_NUM("foundational", "sleep_h", "Health advice often gives 8 as a rounded number of hours of sleep a night. Enter 8.", 8, "Eight hours as a rounded figure.", "The question already gives the rounded figure. Copy that whole number."),
        _HL_ORD("foundational", "diet_act", "Order a mixed diet, then regular activity.", ["mix", "activity"], _DIET_BANK, "Diet mix, then activity.", "Start with mixing food groups over time, then the idea of regular movement."),
        _HL_PICK("foundational", "diet_ok", "Select the two healthy-living ideas that belong here.", ["mix", "activity"], _DIET_BANK, 2, "Mix and activity. Ranking bodies is not the lesson.", "Keep the two public-health habits. Drop ranking by shape and collecting private meal lists."),
    ],
    "intermediate": [
        _HL_MCQ("intermediate", "alex", "Alex (fictional) skips mixed food groups for weeks. A scientific comment is", _mcq_opts("the body makes any missing nutrients itself, so nothing is lost", "the body may miss nutrients over time; this is not a demand for Alex's menu", "only the total amount of food matters, not which groups are eaten", "Alex should list every meal in the quiz so the class can check"), "B", "Third-person nutrient idea.", "Talk about missing nutrients in third person. Do not ask for a real menu."),
        _HL_MCQ("intermediate", "screen", "Unmanaged late screen use can", _mcq_opts("help the body fall asleep faster", "crowd out sleep and recovery time", "count as rest, so no sleep is lost", "only affect eyesight, never sleep"), "B", "Time trade-off.", "Think about time: late unmanaged screens can squeeze out rest and recovery."),
        _HL_MCQ("intermediate", "respect", "Respectful relationships means", _mcq_opts("agreeing to whatever a friend wants so that nobody is upset", "communication and consent ideas without asking for private stories", "sharing private stories with the class to build trust", "being popular with as many classmates as possible"), "B", "Curriculum idea, not a social graph.", "This is about communication and consent as ideas, not about always agreeing or sharing private stories."),
        _HL_MCQ("intermediate", "help", "If a fictional character is in distress, the right next step is", _mcq_opts("let the app diagnose the problem from the quiz answers", "signpost a trusted adult or qualified help; the app does not diagnose", "ask the class to vote on what the character should do", "wait for the distress to pass, since feelings are not health"), "B", "Signpost.", "Distress belongs with a trusted adult or qualified help. The app does not diagnose."),
        _HL_MCQ("intermediate", "micro2", "Not every microorganism is a pathogen. That is why", _mcq_opts("antibiotics should be taken to remove all gut bacteria", "the microbiome idea can include helpful as well as harmful roles", "only bacteria count as microorganisms, never viruses", "microbes living in the body can never cause disease"), "B", "Nuance: helpful and harmful roles.", "Some microorganisms can help; not every one is a pathogen, but some still are."),
        _HL_MCQ("intermediate", "activity_bar", "<p>Which letter is the medium activity bar?</p>" + str(habit_bars(title="Activity bar")), _mcq_opts("A", "B", "C", "all three bars are equal"), "B", "B is activity.", "Find the middle-height bar on the sketch and match its letter."),
        _HL_KEY("intermediate", "sleep_word", "Write the word for the regular rest period the body needs.", "sleep", "Sleep.", "One word names the regular rest period that late screens can crowd out."),
        _HL_NUM("intermediate", "groups3", "A simple healthy routine has 3 parts: food mix, activity, sleep. Enter 3.", 3, "Three parts.", "Count the parts named: food mix, movement, and rest."),
        _HL_ORD("intermediate", "mind", "Order mental health as part of health, then signposting qualified help.", ["mental", "signpost"], _MIND_BANK, "Name it, then signpost.", "Name mental health as part of health first, then the signpost to qualified help."),
        _HL_PICK("intermediate", "habit_ok", "Select sleep and screen-time as health ideas.", ["sleep", "screens"], _HABIT_BANK, 2, "Sleep and screens. The app does not spy on lunch seats.", "Choose rest as a need and unmanaged late screens as a time problem. Skip storing lunch seats."),
    ],
    "difficult": [
        _HL_MCQ("difficult", "not_rank", "A health lesson is misused if it", _mcq_opts("uses public evidence about activity", "ranks pupils' bodies, meals or moods", "signposts qualified help", "uses a fictional case"), "B", "No ranking, no disclosure.", "A lesson is misused if it ranks bodies, meals or moods. Fictional cases and public evidence are fine."),
        _HL_MCQ("difficult", "evidence", "Claims about a food or app should be", _mcq_opts("trusted if the product has many five-star reviews online", "checked against public evidence, not a classmate's private list", "accepted once a famous athlete has recommended the product", "believed when the advert quotes an impressive percentage"), "B", "Evidence, not records.", "Check a food or app claim against public evidence, not a classmate's private list."),
        _HL_MCQ("difficult", "micro3", "Calling the microbiome a class vote is wrong because", _mcq_opts("it is a single organism, not a group of any kind", "it is a biological community idea, not a popularity poll", "it is a count of harmful germs only, not a choice", "it is fixed at birth and never changes with food"), "B", "Biology, not a poll.", "This is a biological community idea, not a popularity poll about snacks."),
        _HL_MCQ("difficult", "both", "Food mix and activity together matter because", _mcq_opts("exercise cancels out any food, so what is eaten stops mattering", "the body uses food energy and also needs movement and rest", "food gives the body energy but movement only wastes it", "a mixed diet alone keeps the body fit without any movement"), "B", "Several needs.", "A person needs food energy, movement and rest together — not one of them alone."),
        _HL_MCQ("difficult", "jordan", "Jordan (fictional) is exhausted after late screens. A fair science comment is", _mcq_opts("exhaustion must mean an infection, since screens cannot affect sleep", "late screens can trade off against sleep; personal logs stay private", "screens give off energy, so the tiredness must come from food", "Jordan should post a screen log in the quiz so the class can compare"), "B", "Mechanism without a log.", "Late screens can trade off against rest. Personal logs stay private."),
        _HL_MCQ("difficult", "screen_bar", "<p>Which letter is the short screen-time bar?</p>" + str(habit_bars(title="Screen bar")), _mcq_opts("A", "C", "B", "all three bars are equal"), "B", "C is screens.", "Find the shortest bar on the sketch and match its letter."),
        _HL_KEY("difficult", "health_word", "Write the word for living microorganisms that interact with the body (one token).", "microbiome", "Microbiome.", "One token names the community of living microorganisms that interact with a person."),
        _HL_NUM("difficult", "bars3", "The habit sketch has how many labelled bars?", 3, "A, B and C.", "Count the labelled bars on the habit sketch — they use three letters."),
        _HL_ORD("difficult", "micro_ord", "Order the microbiome as living microbes, then the false idea that it is a snack vote.", ["live", "not_vote"], _MICRO_BANK, "Biology first, then the misconception.", "Put the living-microorganisms idea first, then the false idea that it is a snack vote."),
        _HL_PICK("difficult", "mind_not", "Select the two items that do not belong in a science class.", ["joke", "rank_mood"], _MIND_BANK, 2, "Jokes and mood rankings are out.", "Pick the two items that treat mental illness as a joke or as a class mood ranking."),
    ],
}

_HL_STANDARD = {
    "foundational": (
        'healthy_living_foundational_mcq_activity',
        'healthy_living_foundational_keyword_diet_word',
        'healthy_living_foundational_number_sleep_h',
        'healthy_living_foundational_order_diet_act',
        'healthy_living_foundational_pick_diet_ok',
    ),
    "intermediate": (
        'healthy_living_intermediate_mcq_activity_bar',
        'healthy_living_intermediate_keyword_sleep_word',
        'healthy_living_intermediate_number_groups3',
        'healthy_living_intermediate_order_mind',
        'healthy_living_intermediate_pick_habit_ok',
    ),
    "difficult": (
        'healthy_living_difficult_mcq_both',
        'healthy_living_difficult_keyword_health_word',
        'healthy_living_difficult_number_bars3',
        'healthy_living_difficult_order_micro_ord',
        'healthy_living_difficult_pick_mind_not',
    ),
}
eursc_science_healthy_living, eursc_science_healthy_living_variants = bind_eursc_topic(
    'healthy_living',
    _HL_POOLS,
    _HL_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: HEALTHY_LIVING_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: HEALTHY_LIVING_SMS_POOLS,
    },
)

_PATH_BANK = (
    {"id": "bacteria", "text": "Bacteria are living cells that can be pathogens"},
    {"id": "virus", "text": "Viruses need a host cell to multiply"},
    {"id": "same", "text": "Bacteria and viruses are the same object"},
    {"id": "who", "text": "The quiz should list who was ill last week"},
)
_CHAIN_BANK = (
    {"id": "source", "text": "A source holds the pathogen"},
    {"id": "route", "text": "A route carries it to a new host"},
    {"id": "host", "text": "A new host can then become a further source"},
    {"id": "magic", "text": "Infection jumps with no route because of a rumour"},
)
_VAX_BANK = (
    {"id": "immune", "text": "Immunity is the body's defence, innate or learned"},
    {"id": "vaccine", "text": "A vaccine trains immunity using a safe exposure"},
    {"id": "antibiotics_virus", "text": "Antibiotics are a treatment for all viruses"},
    {"id": "vax_spy", "text": "The app should store whose jabs they have had"},
)
_HYG_BANK = (
    {"id": "hygiene", "text": "Hand hygiene and sanitation can cut some routes"},
    {"id": "data", "text": "Outbreak numbers are public counts, not a pupil's medical file"},
    {"id": "blame", "text": "An outbreak graph is for blaming a named classmate"},
    {"id": "skip_wash", "text": "Sanitation never changes spread"},
)

_ID_POOLS = {
    "foundational": [
        _ID_MCQ("foundational", "bact", "Bacteria are", _mcq_opts("non-living particles that need a host cell", "living cells that can act as pathogens", "the same thing as a virus, only larger", "always harmful and never found in a healthy body"), "B", "Living cells.", "These are living cells that can cause disease — not non-living particles, and not always harmful."),
        _ID_MCQ("foundational", "vir", "Viruses typically", _mcq_opts("are living cells that divide on their own", "need a host cell to multiply", "are killed quickly by antibiotics", "are much larger than bacteria"), "B", "Host required.", "This pathogen typically needs a host cell before it can multiply."),
        _ID_MCQ("foundational", "spread", "An infectious disease can spread because", _mcq_opts("it is passed down in families through genetic information", "a pathogen can pass from a source along a route to a new host", "cold weather on its own creates the pathogen in the body", "the body makes a pathogen whenever a person is very tired"), "B", "Chain of infection.", "Think source, then a route, then a new host — not inheritance or cold weather."),
        _ID_MCQ("foundational", "immune", "Immunity is", _mcq_opts("a medicine taken to kill every pathogen at once", "the body's defence, which can be innate or learned", "being completely unable to catch any disease ever", "the same thing as receiving a vaccine injection"), "B", "Defence.", "This is the defence system of a person, which can be innate or learned."),
        _ID_MCQ("foundational", "hygiene", "Hand hygiene can help because it may", _mcq_opts("kill every pathogen inside the body", "reduce some transmission routes", "replace all vaccines automatically", "stop diseases that are inherited"), "B", "Cut some routes.", "Clean hands can cut some paths a pathogen uses to travel."),
        _ID_MCQ("foundational", "source_letter", "<p>Which letter is the source in this chain?</p>" + str(infection_chain(title="Source letter")), _mcq_opts("B", "A", "C", "all three letters"), "B", "A is the source.", "On the chain sketch, find the letter that marks where the pathogen is held first."),
        _ID_KEY("foundational", "virus_word", "Write the word for a pathogen that needs a host cell to multiply.", "virus", "A virus.", "Name the pathogen that cannot multiply unless it is inside a host cell."),
        _ID_NUM("foundational", "chain3", "The simple infection chain has source, route and new host. Enter how many parts that is.", 3, "Three parts.", "Count the parts named: source, route, and new host."),
        _ID_ORD("foundational", "chain_ord", "Order source, then route, then new host.", ["source", "route", "host"], _CHAIN_BANK, "Source → route → host.", "Start where the pathogen is held, then the path it travels, then the new person it can reach."),
        _ID_PICK("foundational", "path_ok", "Select bacteria and viruses as different pathogens.", ["bacteria", "virus"], _PATH_BANK, 2, "Two kinds. The quiz does not list who was ill.", "Choose the two different pathogen kinds. Skip the idea they are identical, and skip listing who was ill."),
    ],
    "intermediate": [
        _ID_MCQ("intermediate", "vax", "A vaccine is modelled as", _mcq_opts("an antibiotic that kills every virus", "a safe exposure that trains immunity", "a medicine that cures an infection already caught", "a way of removing all microbes from the body"), "B", "Train immunity.", "A safe exposure can train the defence system. This is not a cure for an infection already caught."),
        _ID_MCQ("intermediate", "abx", "Antibiotics", _mcq_opts("treat all viruses as well as bacteria if the dose is high enough", "can treat some bacterial infections but not viruses, and resistance matters", "cure colds and flu, which is why doctors always prescribe them", "work on every bacterium and never lose their effect over time"), "B", "Not for viruses; resistance.", "These medicines can help some bacterial infections. They do not work on viruses, and resistance matters."),
        _ID_MCQ("intermediate", "route", "A transmission route can be", _mcq_opts("only direct touch, since pathogens cannot travel through the air", "droplets, contact or another path the teacher names, without naming who was ill", "only the air, since pathogens die at once on any surface", "the list of who was ill, which shows where the disease came from"), "B", "Routes, not names.", "A path can be droplets or contact. Teach the path, not who was ill."),
        _ID_MCQ("intermediate", "epi", "Epidemiology uses", _mcq_opts("one patient's story as proof for a whole population", "counts and patterns that can be checked, not a pupil's file", "the names of everyone who was ill, listed in public", "guesses about causes that nobody needs to check"), "B", "Public counts.", "This subject uses counts and patterns that can be checked, not a pupil's file."),
        _ID_MCQ("intermediate", "resist", "Antibiotic resistance becomes more likely when", _mcq_opts("a person's body gets used to the drug, so the drug stops working on that person alone", "bacteria are exposed in ways that let resistant strains spread; viruses are still not treated by antibiotics", "antibiotics are given for viruses, which then learn to resist them and pass that on", "a full course is always finished, because that gives the bacteria more time to adapt"), "B", "Selection; still not for viruses.", "When bacteria are exposed in certain ways, strains that survive can spread. Viruses are still the wrong target."),
        _ID_MCQ("intermediate", "route_letter", "<p>Which letter is the route?</p>" + str(infection_chain(title="Route letter")), _mcq_opts("A", "B", "C", "all three letters"), "B", "B is the route.", "On the chain sketch, find the letter that marks the path between source and new host."),
        _ID_KEY("intermediate", "vax_word", "Write the word for a preparation that trains immunity using a safe exposure.", "vaccine", "Vaccine.", "Think of a safe exposure designed to train the defence system — not a snack vote and not a stored injection record."),
        _ID_NUM("intermediate", "day3", "A model outbreak has 2, then 4, then 8 cases. Enter the number of cases on the third day.", 8, "Doubling model: 8.", "The model doubles each day: start at 2, then 4, then double once more for the third day."),
        _ID_ORD("intermediate", "vax_ord", "Order immunity as defence, then a vaccine as training.", ["immune", "vaccine"], _VAX_BANK, "Defence, then training.", "First name the defence, then the safe-exposure idea that trains it."),
        _ID_PICK("intermediate", "hyg_ok", "Select hygiene and outbreak-as-counts.", ["hygiene", "data"], _HYG_BANK, 2, "Hygiene and public counts. Not blame.", "Choose hand hygiene and outbreak numbers as public counts. Skip blaming a named classmate."),
    ],
    "difficult": [
        _ID_MCQ("difficult", "not_abx", "Giving antibiotics for a typical virus infection is a poor fit because", _mcq_opts("viruses are too small for any medicine to reach them at all", "antibiotics target bacteria, not viruses, and misuse can feed resistance", "antibiotics only start to work once a person has a high fever", "antibiotics switch off the body's own immune defence for weeks"), "B", "Wrong target plus resistance.", "These medicines target bacteria. Using them on a typical virus infection can also feed resistance."),
        _ID_MCQ("difficult", "double", "If cases go 2, then 4, then 8 in a classroom token model,", _mcq_opts("the count is adding 2 each step in that model, so day 4 will show 10", "the count is doubling each step in that model, not a named person's file", "the count is rising by the same amount each step, so the pattern is linear", "the count will fall on day 4 because the pathogen runs out in that model"), "B", "Model counts.", "In this token model the count doubles each step. It is not a named person's file."),
        _ID_MCQ("difficult", "host", "A new host can later act as a source. That is why", _mcq_opts("only the first source ever matters, so later cases can safely be ignored", "breaking a route (hygiene, distance rules the teacher sets) can slow a chain", "the chain stops by itself once a single new host has been infected", "hygiene cannot help any more once a second person has been infected"), "B", "Break the chain.", "A new host can later become a source, so breaking a route can slow the chain."),
        _ID_MCQ("difficult", "vax2", "Vaccination programmes are public health tools. This app", _mcq_opts("keeps a private list of which pupils have had each injection", "teaches the idea; it does not store vaccination status", "checks each pupil's vaccination status before a quiz starts", "replaces the clinic by telling pupils which jab to have"), "B", "No status file.", "Programmes are public-health tools. This app teaches the idea; it does not store status."),
        _ID_MCQ("difficult", "model", "A sticker or counter 'infection' in class is", _mcq_opts("a real pathogen, since the stickers carry live bacteria between pupils", "a model of spread; it does not replace a risk-assessed practical and is not a diagnosis", "proof that the pupil holding a sticker is actually ill with the disease", "a full replacement for a laboratory practical, since it shows the same thing"), "B", "Model only.", "Stickers or counters stand for spread. They are not a real culture and not a diagnosis."),
        _ID_MCQ("difficult", "host_letter", "<p>Which letter is the new host?</p>" + str(infection_chain(title="Host letter")), _mcq_opts("A", "C", "B", "all three letters"), "B", "C is the new host.", "On the chain sketch, find the letter that marks the new host at the end of the path."),
        _ID_MCQ("difficult", "bar_c", "<p>Which day has the most cases?</p>" + str(outbreak_bars(title="Most cases")), _mcq_opts("A", "C", "B", "all three days are equal"), "B", "C is 8 cases.", "Compare the three day-bars and pick the letter with the highest case count."),
        _ID_KEY("difficult", "imm_word", "Write the word for the body's defence that can be innate or learned.", "immunity", "Immunity.", "Name the defence of a person that can be innate or learned."),
        _ID_NUM("difficult", "abx0", "How many virus infections are treated by antibiotics? Enter 0.", 0, "Antibiotics are not for viruses.", "Those medicines target bacteria. Count how many virus infections they treat here."),
        _ID_ORD("difficult", "full_chain", "Order source, route, then host.", ["source", "route", "host"], _CHAIN_BANK, "The chain again.", "Walk the chain again: where it is held, how it travels, who it can reach next."),
        _ID_PICK("difficult", "path_not", "Select the two statements that do not belong.", ["same", "who"], _PATH_BANK, 2, "Not the same object; no illness list.", "Pick the two statements that treat bacteria and viruses as identical, or that harvest who was ill."),
    ],
}

# infectious difficult has 7 MCQ - that's 7+1+1+1+1=11 items in difficult. Foundational and intermediate have 10. Need exactly unique stems - extra MCQ is OK as long as counts: mcq will be 6+6+7=19 >=15, typed 4*3=12. Wait difficult has 7 MCQ + key + num + ord + pick = 11 items. That's fine, more than 10.

# Actually wait I counted difficult: 7 mcq (not_abx, double, host, vax2, model, host_letter, bar_c) + key + num + ord + pick = 11. Good.

_ID_STANDARD = {
    "foundational": (
        'infectious_disease_foundational_mcq_bact',
        'infectious_disease_foundational_keyword_virus_word',
        'infectious_disease_foundational_number_chain3',
        'infectious_disease_foundational_order_chain_ord',
        'infectious_disease_foundational_pick_path_ok',
    ),
    "intermediate": (
        'infectious_disease_intermediate_mcq_abx',
        'infectious_disease_intermediate_keyword_vax_word',
        'infectious_disease_intermediate_number_day3',
        'infectious_disease_intermediate_order_vax_ord',
        'infectious_disease_intermediate_pick_hyg_ok',
    ),
    "difficult": (
        'infectious_disease_difficult_mcq_bar_c',
        'infectious_disease_difficult_keyword_imm_word',
        'infectious_disease_difficult_number_abx0',
        'infectious_disease_difficult_order_full_chain',
        'infectious_disease_difficult_pick_path_not',
    ),
}
def _id_sms_variant(difficulty, suffix):
    def decorator(builder):
        def _fn():
            return make_graded_problem(
                builder(), difficulty, _LEVEL, _SUBJECT, "infectious_disease"
            )

        _fn.__name__ = f"infectious_disease_{difficulty}_sms_{suffix}"
        _fn._kind = "number_fields"
        _fn._randomizable = True
        return _fn

    return decorator


def _id_sms_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _id_sms_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    raw = f"1|{'|'.join(step_ids)}"
    return raw, bank


def _id_sms_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f"c{i + 1}" for i in range(len(correct_texts)))
    bank = [{"id": cid, "text": text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    raw = f"pick|{pick_count}|{'|'.join(correct_ids)}"
    return raw, bank, pick_count


_ID_SMS_FOUND_CHAIN_PACKS = (
    {
        "setting": "fictional camp canteen",
        "source": "unwashed serving tongs holding the pathogen",
        "route": "contact with the shared tongs",
        "host": "later diners who use the same tongs",
        "break_a": "Wash hands and clean the shared tongs to break that contact route",
        "break_b": "Treat the case counts as a public model, not a named person's file",
    },
    {
        "setting": "fictional sports changing room",
        "source": "a shared towel holding the pathogen",
        "route": "contact with the shared towel",
        "host": "the next athlete who uses the towel",
        "break_a": "Use clean towels and wash hands to break that contact route",
        "break_b": "Treat the case counts as a public model, not a named person's file",
    },
    {
        "setting": "fictional clinic waiting area",
        "source": "an uncleaned door handle holding the pathogen",
        "route": "contact with the door handle",
        "host": "the next visitor who uses the same handle",
        "break_a": "Clean the handle and wash hands to break that contact route",
        "break_b": "Treat the case counts as a public model, not a named person's file",
    },
)


@_id_sms_variant("foundational", "canteen_chain_break")
def _infectious_disease_foundational_sms_canteen_chain_break():
    pack = random.choice(_ID_SMS_FOUND_CHAIN_PACKS)
    order_raw, order_bank = _id_sms_order_field(
        (
            f"Source: {pack['source']}",
            f"Route: {pack['route']}",
            f"New host: {pack['host']}",
        ),
        (
            "Infection jumps with no route because of a rumour",
            "The quiz should publish who was ill",
        ),
    )
    pick_raw, pick_bank, pick_count = _id_sms_pick_field(
        (pack["break_a"], pack["break_b"]),
        (
            "Publish the names of who used the shared item",
            "Give antibiotics because every illness is a virus",
        ),
        2,
    )
    question = (
        f"<p>Public-health staff model spread in a {pack['setting']}.</p>"
        f"<p>The model names a source ({pack['source']}), a route "
        f"({pack['route']}), and a new host ({pack['host']}).</p>"
        + str(infection_chain(title="Fictional chain of infection"))
        + "<p>(i) Order source, then route, then new host.</p>"
        "<p>(ii) Using the route from (i), select the two actions that belong "
        "in this public-health response.</p>"
    )
    solution = (
        f"(i) <strong>Source → route → new host</strong> in this "
        f"{pack['setting']}<br>"
        f"(ii) Break the contact route, and keep counts as public data: "
        f"<strong>{pack['break_a']}</strong>; <strong>{pack['break_b']}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Walk the chain in this scenario, then "
        "break that route without naming who was ill."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Chain order", "Public-health actions"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the chain, then select two actions that fit this route.",
        ),
    )


_ID_SMS_FOUND_TOKEN_PACKS = (
    {"place": "classroom token model", "start": 2},
    {"place": "camp sticker model", "start": 3},
    {"place": "clinic counter model", "start": 4},
)


@_id_sms_variant("foundational", "token_double_safeguard")
def _infectious_disease_foundational_sms_token_double_safeguard():
    pack = random.choice(_ID_SMS_FOUND_TOKEN_PACKS)
    day1 = pack["start"]
    day2 = day1 * 2
    day3 = day2 * 2
    correct = (
        "a doubling model of public counts, not a named person's medical file"
    )
    distractors = (
        "proof that one named pupil started the whole outbreak",
        "a linear model that adds the same number of cases each day",
        "a list the quiz should store of which pupils coughed",
    )
    options, letter = _id_sms_mcq_field(correct, distractors)
    question = (
        f"<p>In a fictional {pack['place']}, tokens stand for cases. Day 1 has "
        f"{day1} cases, then day 2 has {day2} cases if the count doubles "
        "each step.</p>"
        "<p>(i) If doubling continues, how many cases are there on day 3?</p>"
        "<p>(ii) The day-3 count from (i) is</p>"
    )
    solution = (
        f"(i) {day2} × 2 = <strong>{day3}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Double the day-2 count, then remember "
        "these are model counts, not a medical file."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (day3, letter),
            ("Day-3 cases", "What the count is"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Double the day-2 count, then choose what those numbers are.",
        ),
    )


_ID_SMS_FOUND_VIRUS_PACKS = (
    {
        "setting": "fictional sports-camp poster",
        "clue": "the pathogen needs a host cell to multiply",
    },
    {
        "setting": "fictional clinic teaching sheet",
        "clue": "the pathogen is not a living cell and needs a host cell",
    },
    {
        "setting": "fictional science-week display",
        "clue": "the pathogen multiplies only inside a host cell",
    },
)


@_id_sms_variant("foundational", "virus_abx_zero")
def _infectious_disease_foundational_sms_virus_abx_zero():
    pack = random.choice(_ID_SMS_FOUND_VIRUS_PACKS)
    correct = "a virus, because it needs a host cell to multiply"
    distractors = (
        "a bacterium, because bacteria never need a host",
        "a bacterium, because bacteria are not living cells",
        "a bacterium, because only bacteria can multiply",
    )
    options, letter = _id_sms_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['setting']} describes an infectious-disease model: "
        f"{pack['clue']}.</p>"
        "<p>(i) The pathogen is</p>"
        "<p>(ii) Using that classification from (i), how many virus "
        "infections do antibiotics treat?</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) Antibiotics target bacteria, not viruses, so "
        "<strong>0</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Name the pathogen from the host-cell "
        "clue, then count how many virus infections antibiotics treat here."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, 0),
            ("Pathogen type", "Virus infections treated by antibiotics"),
            field_types=("mcq", "number"),
            field_options=(options, None),
            format_hint="Classify the pathogen, then enter how many virus infections antibiotics treat here.",
        ),
    )


_ID_SMS_INTER_OUTBREAK_PACKS = (
    {"place": "fictional town clinic", "days": (2, 4, 8)},
    {"place": "fictional camp medical tent", "days": (3, 6, 12)},
    {"place": "fictional regional public table", "days": (4, 8, 16)},
)


@_id_sms_variant("intermediate", "outbreak_next_hygiene")
def _infectious_disease_intermediate_sms_outbreak_next_hygiene():
    pack = random.choice(_ID_SMS_INTER_OUTBREAK_PACKS)
    d1, d2, d3 = pack["days"]
    d4 = d3 * 2
    labels = ["1", "2", "3"]
    pick_raw, pick_bank, pick_count = _id_sms_pick_field(
        (
            "Hand hygiene and sanitation can cut some routes",
            "Outbreak numbers are public counts, not a pupil's medical file",
        ),
        (
            "An outbreak graph is for blaming a named classmate",
            "Sanitation never changes spread",
        ),
        2,
    )
    chart = outbreak_bars(title="Fictional outbreak model") if pack["days"] == (2, 4, 8) else bar_chart(
        labels,
        [d1, d2, d3],
        title=f"Public case counts at a {pack['place']}",
        desc=(
            f"Bar chart of three public case counts: {d1}, {d2} and {d3}."
        ),
    )
    question = (
        f"<p>A {pack['place']} publishes a three-day model of cases: "
        f"{d1}, then {d2}, then {d3}. The count doubles each day.</p>"
        + str(chart)
        + "<p>(i) How many cases does day 3 show?</p>"
        "<p>(ii) If doubling continues, how many cases does the model give "
        "for day 4?</p>"
        "<p>(iii) Using those public counts, select the two ideas that belong "
        "in this response.</p>"
    )
    solution = (
        f"(i) Day 3 = <strong>{d3}</strong><br>"
        f"(ii) {d3} × 2 = <strong>{d4}</strong><br>"
        "(iii) <strong>Hygiene can cut routes</strong>; "
        "<strong>counts are public, not a medical file</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read day 3, double it for day 4, then "
        "keep hygiene and public counts — not blame."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (d3, d4, pick_raw),
            ("Day-3 cases", "Day-4 cases", "Response ideas"),
            field_types=("number", "number", "pick"),
            field_options=(None, None, pick_bank),
            field_pick_counts=(None, None, pick_count),
            format_hint="Read day 3, double it, then select two public-health ideas.",
        ),
    )


_ID_SMS_INTER_VAX_PACKS = (
    {"place": "fictional town vaccination campaign"},
    {"place": "fictional regional immunisation poster"},
    {"place": "fictional public-health week display"},
)


@_id_sms_variant("intermediate", "vax_campaign_status")
def _infectious_disease_intermediate_sms_vax_campaign_status():
    pack = random.choice(_ID_SMS_INTER_VAX_PACKS)
    order_raw, order_bank = _id_sms_order_field(
        (
            "Immunity is the body's defence, innate or learned",
            "A vaccine trains immunity using a safe exposure",
        ),
        (
            "Antibiotics are a treatment for all viruses",
            "The app should store whose jabs they have had",
        ),
    )
    correct = "teaches the idea; it does not store vaccination status"
    distractors = (
        "keeps a private list of which pupils have had each injection",
        "checks each pupil's vaccination status before the quiz starts",
        "replaces the clinic by telling pupils which jab to have",
    )
    options, letter = _id_sms_mcq_field(correct, distractors)
    question = (
        f"<p>A {pack['place']} explains immunity and vaccines using public "
        "teaching material, not a list of who has been vaccinated.</p>"
        "<p>(i) Order the defence idea, then the vaccine-as-training idea, "
        "for this campaign.</p>"
        "<p>(ii) Using that public-health teaching from (i), this app</p>"
    )
    solution = (
        "(i) <strong>Immunity as defence</strong>, then "
        "<strong>vaccine as training</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Defence first, then training; the app "
        "does not store vaccination status."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Immunity then vaccine", "What this app does"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order defence then training, then choose what this app stores.",
        ),
    )


_ID_SMS_INTER_ABX_PACKS = (
    {
        "setting": "fictional clinic teaching case",
        "illness": "a typical virus infection",
    },
    {
        "setting": "fictional camp health briefing",
        "illness": "a viral infection that needs a host cell",
    },
    {
        "setting": "fictional public leaflet",
        "illness": "a virus infection, not a bacterial one",
    },
)


@_id_sms_variant("intermediate", "clinic_abx_resist")
def _infectious_disease_intermediate_sms_clinic_abx_resist():
    pack = random.choice(_ID_SMS_INTER_ABX_PACKS)
    correct = (
        "antibiotics target bacteria, not viruses, and misuse can feed resistance"
    )
    distractors = (
        "viruses are too small for any medicine to reach them",
        "antibiotics only start to work once a fever has begun",
        "antibiotics switch off the body's own immune defence",
    )
    options, letter = _id_sms_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _id_sms_pick_field(
        (
            "Hand hygiene and sanitation can still cut some routes",
            "Outbreak and treatment ideas stay public; this app does not store prescriptions",
        ),
        (
            "The quiz should list who was ill last week",
            "Antibiotics treat all viruses",
        ),
        2,
    )
    question = (
        f"<p>A {pack['setting']} discusses {pack['illness']}.</p>"
        "<p>(i) Giving antibiotics for that typical virus infection is a "
        "poor fit because</p>"
        "<p>(ii) Using the wrong-target idea from (i), select the two "
        "statements that belong in this public-health model.</p>"
    )
    solution = (
        f"(i) <strong>{correct}</strong><br>"
        "(ii) <strong>Hygiene can still cut routes</strong>; "
        "<strong>this app does not store prescriptions</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Antibiotics miss viruses and can feed "
        "resistance; keep hygiene and public data, not a prescription file."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (letter, pick_raw),
            ("Why antibiotics are a poor fit", "What still belongs"),
            field_types=("mcq", "pick"),
            field_options=(options, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Choose why antibiotics miss this virus, then select two fitting ideas.",
        ),
    )


_ID_SMS_DIFF_HOST_PACKS = (
    {
        "setting": "fictional canteen chain",
        "source": "a contaminated serving spoon",
        "route": "contact with the spoon",
        "host": "a later diner, who can then act as a further source",
    },
    {
        "setting": "fictional camp cabin model",
        "source": "a shared water bottle",
        "route": "contact with the bottle",
        "host": "the next person who drinks, who can then act as a further source",
    },
    {
        "setting": "fictional clinic door-handle model",
        "source": "an uncleaned handle",
        "route": "contact with the handle",
        "host": "the next visitor, who can then act as a further source",
    },
)


@_id_sms_variant("difficult", "host_source_break")
def _infectious_disease_difficult_sms_host_source_break():
    pack = random.choice(_ID_SMS_DIFF_HOST_PACKS)
    order_raw, order_bank = _id_sms_order_field(
        (
            f"Source: {pack['source']}",
            f"Route: {pack['route']}",
            f"New host: {pack['host']}",
        ),
        (
            "Infection jumps with no route because of a rumour",
            "The quiz should publish names from this model",
        ),
    )
    correct = (
        "breaking a route (hygiene, distance rules the teacher sets) can slow a chain"
    )
    distractors = (
        "routes never matter once a new host exists",
        "the chain stops by itself after one new host is infected",
        "hygiene cannot help once a second person has been infected",
    )
    options, letter = _id_sms_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _id_sms_pick_field(
        (
            "Bacteria and viruses are different kinds of pathogen",
            "Outbreak numbers are public counts, not a pupil's medical file",
        ),
        (
            "Bacteria and viruses are the same object",
            "The quiz should list who was ill last week",
        ),
        2,
    )
    question = (
        f"<p>Staff model a {pack['setting']}: {pack['source']}, then "
        f"{pack['route']}, then {pack['host']}.</p>"
        + str(infection_chain(title="Fictional chain: new host can become a source"))
        + "<p>(i) Order source, then route, then new host.</p>"
        "<p>(ii) Using that chain, a new host can later act as a source. "
        "That is why</p>"
        "<p>(iii) Select the two statements that belong with this public model.</p>"
    )
    solution = (
        "(i) <strong>Source → route → new host</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>Different pathogens</strong>; "
        "<strong>public counts, not a medical file</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Walk the chain, break the route because "
        "a new host can become a source, and keep names out of the quiz."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (order_raw, letter, pick_raw),
            ("Chain order", "Why breaking a route matters", "Statements that belong"),
            field_types=("order", "mcq", "pick"),
            field_options=(order_bank, options, pick_bank),
            field_pick_counts=(None, None, pick_count),
            format_hint="Order the chain, choose why the route matters, then select two fitting statements.",
        ),
    )


_ID_SMS_DIFF_TOTAL_PACKS = (
    {"place": "fictional town clinic table", "days": (2, 4, 8)},
    {"place": "fictional camp public board", "days": (3, 6, 12)},
    {"place": "fictional regional model", "days": (5, 10, 20)},
)


@_id_sms_variant("difficult", "outbreak_total_model")
def _infectious_disease_difficult_sms_outbreak_total_model():
    pack = random.choice(_ID_SMS_DIFF_TOTAL_PACKS)
    d1, d2, d3 = pack["days"]
    total = d1 + d2 + d3
    labels = ["1", "2", "3"]
    correct = "counts and patterns that can be checked, not a pupil's file"
    distractors = (
        "one patient's story as proof for a whole population",
        "the names of everyone who was ill, listed in public",
        "guesses about causes that nobody needs to check",
    )
    options, letter = _id_sms_mcq_field(correct, distractors)
    chart = outbreak_bars(title="Fictional outbreak model") if pack["days"] == (2, 4, 8) else bar_chart(
        labels,
        [d1, d2, d3],
        title=f"Public case counts at a {pack['place']}",
        desc=(
            f"Bar chart of three public case counts: {d1}, {d2} and {d3}."
        ),
    )
    question = (
        f"<p>Epidemiology staff publish a {pack['place']}: {d1} cases, "
        f"then {d2}, then {d3} on three days of a doubling model.</p>"
        + str(chart)
        + "<p>(i) How many cases does day 3 show?</p>"
        "<p>(ii) Using day 3 from (i) with the first two days, what is the "
        "total number of cases in the three-day model?</p>"
        "<p>(iii) Epidemiology uses</p>"
    )
    solution = (
        f"(i) Day 3 = <strong>{d3}</strong><br>"
        f"(ii) {d1} + {d2} + {d3} = <strong>{total}</strong><br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Read day 3, add the three public counts, "
        "then remember epidemiology uses checkable counts, not a pupil's file."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (d3, total, letter),
            ("Day-3 cases", "Three-day total", "What epidemiology uses"),
            field_types=("number", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Read day 3, add the three days, then choose what epidemiology uses.",
        ),
    )


_ID_SMS_DIFF_ABX_PACKS = (
    {"setting": "fictional clinic case discussion"},
    {"setting": "fictional camp medical briefing"},
    {"setting": "fictional public-health leaflet"},
)


@_id_sms_variant("difficult", "wrong_abx_safeguard")
def _infectious_disease_difficult_sms_wrong_abx_safeguard():
    pack = random.choice(_ID_SMS_DIFF_ABX_PACKS)
    correct = (
        "antibiotics target bacteria, not viruses, and misuse can feed resistance"
    )
    distractors = (
        "viruses are too small for any medicine to reach",
        "antibiotics only work once a person has a fever",
        "the body's immune defence is switched off by antibiotics",
    )
    options, letter = _id_sms_mcq_field(correct, distractors)
    pick_raw, pick_bank, pick_count = _id_sms_pick_field(
        (
            "This app teaches the idea; it does not store vaccination or prescription status",
            "A sticker or counter 'infection' is a model of spread, not a diagnosis",
        ),
        (
            "The quiz should publish names of who was ill",
            "Stickers in class prove a named pupil is ill",
        ),
        2,
    )
    question = (
        f"<p>A {pack['setting']} asks whether antibiotics treat a typical "
        "virus infection.</p>"
        "<p>(i) How many virus infections are treated by antibiotics?</p>"
        "<p>(ii) Using (i), giving antibiotics for a typical virus infection "
        "is a poor fit because</p>"
        "<p>(iii) Select the two safeguarding statements that belong with "
        "this model.</p>"
    )
    solution = (
        "(i) <strong>0</strong><br>"
        f"(ii) <strong>{correct}</strong><br>"
        "(iii) <strong>No status file in this app</strong>; "
        "<strong>classroom tokens are a model, not a diagnosis</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Antibiotics treat 0 virus infections here; "
        "misuse feeds resistance; the app does not diagnose or store status."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (0, letter, pick_raw),
            (
                "Virus infections treated by antibiotics",
                "Why antibiotics are a poor fit",
                "Safeguarding statements",
            ),
            field_types=("number", "mcq", "pick"),
            field_options=(None, options, pick_bank),
            field_pick_counts=(None, None, pick_count),
            format_hint="Enter 0, choose why antibiotics miss viruses, then select two safeguarding statements.",
        ),
    )


_ID_SITUATIONAL_POOLS = {
    "foundational": [
        _infectious_disease_foundational_sms_canteen_chain_break,
        _infectious_disease_foundational_sms_token_double_safeguard,
        _infectious_disease_foundational_sms_virus_abx_zero,
    ],
    "intermediate": [
        _infectious_disease_intermediate_sms_outbreak_next_hygiene,
        _infectious_disease_intermediate_sms_vax_campaign_status,
        _infectious_disease_intermediate_sms_clinic_abx_resist,
    ],
    "difficult": [
        _infectious_disease_difficult_sms_host_source_break,
        _infectious_disease_difficult_sms_outbreak_total_model,
        _infectious_disease_difficult_sms_wrong_abx_safeguard,
    ],
}

eursc_science_infectious_disease, eursc_science_infectious_disease_variants = bind_eursc_topic(
    "infectious_disease",
    _ID_POOLS,
    _ID_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: INFECTIOUS_DISEASE_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: _ID_SITUATIONAL_POOLS,
    },
)

_CLASS_BANK = (
    {"id": "infect", "text": "Infectious disease can pass from host to host"},
    {"id": "noninfect", "text": "Noninfectious disease does not spread like an infection"},
    {"id": "all_catch", "text": "Every illness is caught from a classmate"},
    {"id": "spy_fam", "text": "The quiz should collect family medical histories"},
)
_CAUSE_BANK = (
    {"id": "inherit", "text": "Some conditions are inherited or long-term systemic"},
    {"id": "deficiency", "text": "Some diseases link to missing nutrients"},
    {"id": "pollution", "text": "Some diseases link to pollution or occupation"},
    {"id": "blame", "text": "A condition is always the person's fault to rank in class"},
)
_SUPPORT_BANK = (
    {"id": "mental_ill", "text": "Mental illness is a health condition, not a joke"},
    {"id": "support", "text": "Treatment and support are clinical; this app does not diagnose"},
    {"id": "rank_ill", "text": "Pupils must compare whose relative is ill"},
    {"id": "ignore", "text": "Support is never needed because slogans replace care"},
)

_NI_POOLS = {
    "foundational": [
        _NI_MCQ("foundational", "split", "A noninfectious disease", _mcq_opts("spreads from host to host, but more slowly than a cold", "does not spread like an infection", "is always caused by a hidden virus", "can be caught by touching someone who has it"), "B", "Not a chain of infection.", "This kind of disease does not jump from host to host the way a cold can."),
        _NI_MCQ("foundational", "infect_vs", "An infectious disease", _mcq_opts("is passed down in families through genetic information", "can pass from a source along a route to a new host", "is caused by missing nutrients over a long time", "is always caused by pollution in the air or water"), "B", "Can spread.", "This kind can pass from a source along a route to a new host."),
        _NI_MCQ("foundational", "inherit", "An inherited condition is", _mcq_opts("an infection that is caught from a parent at birth", "a long-term or genetic idea taught with public examples, not a family survey", "a condition caused by the food a family shares at home", "a reason for the quiz to ask about each pupil's relatives"), "B", "No family files.", "A long-term or genetic idea is taught with public examples, not a family survey."),
        _NI_MCQ("foundational", "defic", "A deficiency disease can link to", _mcq_opts("a pathogen passed on through shared food", "missing nutrients in the diet over time, using public examples", "eating too much of one nutrient in a single day", "a lack of exercise rather than anything in the diet"), "B", "Nutrient gap, not a menu upload.", "Missing nutrients over time can harm health. Public examples, not private menus."),
        _NI_MCQ("foundational", "mental", "Mental illness is", _mcq_opts("a weakness of character rather than a health condition", "a health condition that can be supported; the app does not diagnose", "an infection that passes from person to person like a cough", "a condition that the app can diagnose from a pupil's quiz answers"), "B", "Clinical, no diagnosis here.", "This is a health condition that can be supported. The app does not diagnose and it is not a weakness of character."),
        _NI_MCQ("foundational", "support", "Treatment and support belong with", _mcq_opts("this quiz, which can store a diagnosis for each pupil", "qualified people; the page teaches categories, not personal files", "the class, who should vote on what a person needs", "nobody, since a condition passes if it is ignored"), "B", "Signpost.", "Treatment belongs with qualified people. The page teaches categories, not personal files."),
        _NI_KEY("foundational", "support_word", "Write the word for help and treatment around a health condition (one token).", "support", "Support.", "One token names help and treatment around a condition — not a diagnosis stored here."),
        _NI_NUM("foundational", "two_kinds", "This lesson splits disease into infectious and noninfectious. Enter how many kinds that is.", 2, "Two kinds.", "Count the two top-level kinds this lesson splits disease into."),
        _NI_ORD("foundational", "split_ord", "Order infectious as able to pass, then noninfectious as not spreading that way.", ["infect", "noninfect"], _CLASS_BANK, "Spread vs not.", "First the kind that can pass host to host, then the kind that does not spread that way."),
        _NI_PICK("foundational", "class_ok", "Select the two correct classification ideas.", ["infect", "noninfect"], _CLASS_BANK, 2, "Two kinds. No family-history harvest.", "Keep the two classification ideas. Drop 'every illness is caught' and collecting family histories."),
    ],
    "intermediate": [
        _NI_MCQ("intermediate", "pollute", "Pollution or occupation can matter because", _mcq_opts("polluted air carries a pathogen from one person to the next", "some exposures are linked to disease in public evidence", "working hard is itself the cause of every long-term disease", "the quiz needs the workplace of each pupil's relatives"), "B", "Environmental risk, not a job survey.", "Some exposures in air, work or the environment are linked to disease in public evidence."),
        _NI_MCQ("intermediate", "sam", "Sam (fictional) has a long-term condition that is not catching. A fair comment is", _mcq_opts("keep a distance from Sam, since any illness can be caught", "it can be noninfectious; do not treat Sam as a source of infection", "long-term must mean a slow virus that is still catching", "share Sam's condition with the class so they can avoid it"), "B", "Third person, no file.", "A long-term condition that is not catching should not be treated like a cold. No file is published."),
        _NI_MCQ("intermediate", "both", "Infectious and noninfectious can both", _mcq_opts("be cured with antibiotics if they are taken early enough", "need evidence and, where personal, qualified care — not this app's diagnosis", "be passed from one person to another along a route", "be diagnosed by this app from the answers a pupil gives"), "B", "Evidence and signpost.", "Both kinds need evidence. Personal care is for qualified people, not this app."),
        _NI_MCQ("intermediate", "def2", "Public examples of deficiency (for example scurvy historically) teach that", _mcq_opts("scurvy was an infection caught from other sailors", "missing a nutrient can harm health over time", "deficiency only happens when a person eats too much", "any missing nutrient can be replaced by any other"), "B", "History/public evidence.", "Historical public examples show that missing a nutrient can harm health over time."),
        _NI_MCQ("intermediate", "not_fault", "Blaming a person as the whole cause of every condition is", _mcq_opts("correct, because every condition comes from a person's own choices", "often unfair; inherited, environmental and infectious causes differ", "correct for infections, but not for inherited conditions", "fair, since genes and pollution never cause disease on their own"), "B", "Causes differ.", "Inherited, environmental and infectious causes differ. Blame-ranking is not science."),
        _NI_MCQ("intermediate", "clinic", "This app", _mcq_opts("diagnoses mental illness from the answers a pupil gives in the quiz", "does not diagnose; it teaches that mental illness is real and support exists", "keeps a private record of which pupils need support", "replaces a nurse or counsellor for pupils who need help"), "B", "No diagnosis.", "This app teaches that mental illness is real. It does not diagnose or keep records."),
        _NI_KEY("intermediate", "pollute_word", "Write the word for harmful substances in air, water or land that can link to disease.", "pollution", "Pollution.", "One word for harmful substances in air, water or land — not a rumour and not a job survey of relatives."),
        _NI_NUM("intermediate", "causes3", "The causes of non-infectious disease can be grouped as inherited, deficiency and pollution/occupation. Enter how many groups that is.", 3, "Three cause-groups.", "Count the cause-groups named: inherited, deficiency, and pollution/occupation."),
        _NI_ORD("intermediate", "cause_ord", "Order inherited/systemic, then deficiency.", ["inherit", "deficiency"], _CAUSE_BANK, "Then nutrients.", "Start with inherited or long-term systemic, then the nutrient-gap idea."),
        _NI_PICK("intermediate", "cause_ok", "Select inherited/systemic and pollution/occupation.", ["inherit", "pollution"], _CAUSE_BANK, 2, "Two cause groups. Blame-ranking is out.", "Choose inherited/systemic and pollution/occupation. Skip blaming a person as the whole cause."),
    ],
    "difficult": [
        _NI_MCQ("difficult", "mix_up", "Treating a noninfectious condition as catching can", _mcq_opts("protect others, since any illness can be passed on", "stigmatise a person who is not a source of infection", "cure the condition faster by isolating the person", "stop the condition being inherited by relatives"), "B", "Stigma from a wrong model.", "Treating a non-catching condition as catching can unfairly mark someone as a source."),
        _NI_MCQ("difficult", "env", "Occupation-linked disease is a reason to", _mcq_opts("treat the workers as sources of infection for the people around them", "study exposures with public evidence and workplace controls, not a family survey", "blame each worker for choosing that job in the first place", "ask pupils for the job titles of their relatives so the class can compare"), "B", "Public occupational health.", "Study workplace exposures with public evidence and controls, not a family job survey."),
        _NI_MCQ("difficult", "mental2", "A mental illness is", _mcq_opts("a weakness of character that a person can simply choose to drop", "a health condition; jokes and rankings do not belong in the quiz", "an infection that spreads between people who spend time together", "a mood that the class should compare and rank in the quiz"), "B", "Condition, not a joke.", "A mental illness is a health condition. Jokes and rankings do not belong here."),
        _NI_MCQ("difficult", "support2", "Qualified support can include", _mcq_opts("this app setting a diagnosis code for each pupil who asks", "clinical care the teacher signposts; the page does not collect who attends", "a class vote on which pupils need the most help", "a private list of who attends, kept on this page"), "B", "Signpost, no attendance list.", "Clinical care is signposted. The page does not collect who attends."),
        _NI_MCQ("difficult", "alex_def", "Alex (fictional) lacks a named nutrient in a textbook case. The scientific move is", _mcq_opts("call it an infection, since illness always comes from a pathogen", "link the case to deficiency using the public story, not a personal menu", "ask Alex for a real shopping list so the class can check it", "say Alex simply ate too much of every other nutrient"), "B", "Case study, not a list.", "Link the textbook case to a nutrient gap using the public story, not a shopping list."),
        _NI_MCQ("difficult", "two_n", "Infectious and non-infectious: how many kinds of disease is that?", _mcq_opts("one", "two", "three", "four"), "B", "Two.", "Count the top-level kinds: infectious versus not."),
        _NI_KEY("difficult", "inherit_word", "Write the word for a condition passed in families by genetic information (one token).", "inherited", "Inherited.", "One token for a condition passed in families by genetic information."),
        _NI_NUM("difficult", "zero_file", "How many family medical histories should this quiz collect? Enter 0.", 0, "Zero.", "Family medical histories belong nowhere in this quiz. Count how many it should collect."),
        _NI_ORD("difficult", "sup_ord", "Order mental illness as a condition, then support without diagnosing in the app.", ["mental_ill", "support"], _SUPPORT_BANK, "Name it, then signpost.", "Name mental illness as a condition first, then help without diagnosing in the app."),
        _NI_PICK("difficult", "sup_not", "Select the two items that do not belong.", ["rank_ill", "ignore"], _SUPPORT_BANK, 2, "No ranking relatives; slogans are not care.", "Pick ranking whose relative is ill, and the claim that slogans replace care."),
    ],
}

_NI_STANDARD = {
    "foundational": (
        'noninfectious_disease_foundational_mcq_defic',
        'noninfectious_disease_foundational_keyword_support_word',
        'noninfectious_disease_foundational_number_two_kinds',
        'noninfectious_disease_foundational_order_split_ord',
        'noninfectious_disease_foundational_pick_class_ok',
    ),
    "intermediate": (
        'noninfectious_disease_intermediate_mcq_both',
        'noninfectious_disease_intermediate_keyword_pollute_word',
        'noninfectious_disease_intermediate_number_causes3',
        'noninfectious_disease_intermediate_order_cause_ord',
        'noninfectious_disease_intermediate_pick_cause_ok',
    ),
    "difficult": (
        'noninfectious_disease_difficult_mcq_alex_def',
        'noninfectious_disease_difficult_keyword_inherit_word',
        'noninfectious_disease_difficult_number_zero_file',
        'noninfectious_disease_difficult_order_sup_ord',
        'noninfectious_disease_difficult_pick_sup_not',
    ),
}
eursc_science_noninfectious_disease, eursc_science_noninfectious_disease_variants = bind_eursc_topic(
    'noninfectious_disease',
    _NI_POOLS,
    _NI_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: NONINFECTIOUS_DISEASE_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: NONINFECTIOUS_DISEASE_SMS_POOLS,
    },
)

_PLEA_BANK = (
    {"id": "pleasure", "text": "Ordinary pleasure can be part of life without being dependence"},
    {"id": "depend", "text": "Dependence means it is very hard to stop even when harm is clear"},
    {"id": "confess", "text": "The quiz should ask what a pupil uses"},
    {"id": "joke_add", "text": "Addiction is only a joke if a poster is famous"},
)
_KIND_BANK = (
    {"id": "substance", "text": "Substance dependence involves a drug or similar chemical"},
    {"id": "behaviour", "text": "Behavioural dependence can involve a repeated action that is hard to stop"},
    {"id": "always_fun", "text": "If something is enjoyable it cannot become harmful"},
    {"id": "class_list", "text": "Pupils must name who in the class uses what"},
)
_HELP_BANK = (
    {"id": "harm", "text": "Dependence can harm health, money, learning or relationships"},
    {"id": "help", "text": "Support is a trusted adult or qualified service, not this app"},
    {"id": "shame", "text": "The scientific method is to shame a named classmate"},
    {"id": "hide", "text": "Help should never be signposted"},
)

_DA_POOLS = {
    "foundational": [
        _DA_MCQ("foundational", "pleasure", "Ordinary pleasure is", _mcq_opts("the same thing as dependence", "possible without being dependence", "always the first step to dependence", "harmful whenever it is repeated"), "B", "Pleasure is not automatically addiction.", "Enjoyment can be part of life without automatically being dependence."),
        _DA_MCQ("foundational", "depend", "Dependence means", _mcq_opts("enjoying something a great deal on one occasion", "it is very hard to stop even when harm is clear", "using something only when friends are using it too", "choosing to keep going simply because it is fun"), "B", "Hard to stop despite harm.", "Look for the idea that stopping is very hard even when harm is clear."),
        _DA_MCQ("foundational", "substance", "Substance dependence involves", _mcq_opts("a repeated action such as gaming, with no chemical involved at all", "a drug or similar chemical, taught with fictional cases, not a use survey", "only illegal drugs, never medicines, alcohol or nicotine", "a survey of what each pupil in the class uses, stored by the quiz"), "B", "Chemical + no survey.", "This kind involves a drug or similar chemical. Teach it with fictional cases, not a use survey."),
        _DA_MCQ("foundational", "behaviour", "Behavioural dependence can involve", _mcq_opts("a chemical such as nicotine rather than any kind of action", "a repeated action that is hard to stop, using third-person examples", "any hobby a person enjoys, since enjoying it counts as dependence", "a log of each pupil's own screen time, kept by the quiz"), "B", "Action pattern, no logs.", "This kind is a repeated action that is hard to stop. Third-person examples only."),
        _DA_MCQ("foundational", "help", "If a fictional character needs help, the lesson points to", _mcq_opts("a class vote on what the character should do next", "a trusted adult or qualified service; this app does not treat addiction", "this app, which can set out a treatment plan for the character", "waiting it out, since dependence passes on its own in time"), "B", "Signpost.", "A fictional character who needs help is pointed to a trusted adult or qualified service."),
        _DA_MCQ("foundational", "not_ask", "This quiz", _mcq_opts("asks what each pupil uses so it can help", "does not ask what a pupil uses", "keeps a private record of what each pupil uses", "asks only about what a pupil's relatives use"), "B", "No disclosure.", "The quiz teaches ideas. It does not harvest personal use."),
        _DA_KEY("foundational", "add_word", "Write the word for dependence that is very hard to stop despite harm.", "addiction", "Addiction / dependence idea; keyword addiction.", "One token names that hard-to-stop pattern. Ordinary enjoyment on its own is not the same thing."),
        _DA_NUM("foundational", "kinds2", "Dependence can be substance or behavioural. Enter how many kinds that is.", 2, "Two kinds.", "Count the two kinds named: a chemical, and a repeated action."),
        _DA_ORD("foundational", "plea_dep", "Order ordinary pleasure, then dependence as hard to stop.", ["pleasure", "depend"], _PLEA_BANK, "Pleasure first, then dependence.", "Put ordinary enjoyment first, then the hard-to-stop-despite-harm idea."),
        _DA_PICK("foundational", "plea_ok", "Select pleasure-without-dependence and dependence-despite-harm.", ["pleasure", "depend"], _PLEA_BANK, 2, "Two ideas. No use survey.", "Keep enjoyment-without-dependence and hard-to-stop-despite-harm. Drop a use survey."),
    ],
    "intermediate": [
        _DA_MCQ("intermediate", "sam_use", "Sam (fictional) keeps using a substance after clear harm. That fits", _mcq_opts("a one-off pleasure", "dependence", "a passing phase", "peer pressure only"), "B", "Third-person dependence.", "Keeping going after clear harm fits the hard-to-stop model, not a passing phase."),
        _DA_MCQ("intermediate", "game", "Jordan (fictional) cannot stop a game pattern that harms sleep and learning. That can be", _mcq_opts("substance dependence", "behavioural dependence", "ordinary pleasure", "a passing phase"), "B", "Behavioural, no login.", "A repeated action that harms rest and learning can fit the behavioural model, not the substance one."),
        _DA_MCQ("intermediate", "social", "Social context can matter because", _mcq_opts("dependence only ever comes from a person's own weak will, never from others", "pressure, availability and marketing can raise risk, without asking who felt pressure", "friends and adverts can never influence what a person chooses to use", "the quiz needs a list of which friends put pressure on which pupils"), "B", "Risk factors, no friend graph.", "Pressure, availability and marketing can raise risk. Teach that without asking who felt pressure."),
        _DA_MCQ("intermediate", "harm", "Harm from dependence can include", _mcq_opts("only physical health, never money, learning or friendships", "health, money, learning or relationships in public/fictional cases", "nothing at all, as long as the person still enjoys it", "only the harm that shows up in the first week of use"), "B", "Several harms.", "Public or fictional cases can show damage to health, money, learning or relationships."),
        _DA_MCQ("intermediate", "not_fun", "If something is enjoyable it", _mcq_opts("can never become harmful", "can still become dependence in some cases", "is always the start of dependence", "is safe as long as friends do it too"), "B", "Enjoyable ≠ safe forever.", "Enjoyable does not mean it can never become harmful."),
        _DA_MCQ("intermediate", "adult", "Personal questions about use belong with", _mcq_opts("this quiz, which keeps the answers private", "a trusted adult or qualified service, not a class quiz", "the whole class, so that everyone can give advice", "a group chat with friends of the same age"), "B", "Signpost.", "Personal questions about use belong with a trusted adult or qualified service, not a class quiz."),
        _DA_KEY("intermediate", "depend_word", "Write the word for finding it very hard to stop even when harm is clear.", "dependence", "Dependence.", "One word for finding it very hard to stop even when harm is already clear."),
        _DA_NUM("intermediate", "zero_use", "How many personal use-lists should this quiz collect? Enter 0.", 0, "Zero.", "Personal use-lists belong nowhere in this quiz. Count how many it should collect."),
        _DA_ORD("intermediate", "kind_ord", "Order substance dependence, then behavioural dependence.", ["substance", "behaviour"], _KIND_BANK, "Chemical, then action pattern.", "First the chemical kind, then the repeated-action kind."),
        _DA_PICK("intermediate", "kind_ok", "Select substance and behavioural dependence.", ["substance", "behaviour"], _KIND_BANK, 2, "Two kinds. No class use-list.", "Choose the chemical kind and the repeated-action kind. Skip a class use-list."),
    ],
    "difficult": [
        _DA_MCQ("difficult", "shame", "Shaming a named classmate is", _mcq_opts("a fair way to make the classmate stop", "not science and not allowed in this quiz", "good science if the facts about them are true", "allowed in the quiz if no teacher sees it"), "B", "No shame lists.", "Naming and shaming a classmate is not a scientific method."),
        _DA_MCQ("difficult", "risk", "Risk is higher in some social settings. The quiz still", _mcq_opts("asks which pupils have felt pressure from friends", "teaches the idea with fictional cases only", "keeps a private list of the settings each pupil visits", "works out which pupils in the class are most at risk"), "B", "Idea, not a confession.", "Some social settings raise risk. Teach that with fictional cases, not a confession."),
        _DA_MCQ("difficult", "help2", "Support routes are", _mcq_opts("this app, which can act as a clinic and store a treatment plan", "trusted adults and qualified services; no treatment record is stored here", "a class vote on who needs help and who does not", "friends of the same age only, since adults never understand dependence"), "B", "Signpost only.", "Support is trusted adults and qualified services. No treatment record is stored here."),
        _DA_MCQ("difficult", "both_k", "Substance and behavioural patterns both", _mcq_opts("involve a chemical that changes the body, so both are substance dependence", "can fit dependence when stopping is very hard despite harm", "are impossible to stop once they have started, whatever help is given", "are harmless as long as the person still enjoys them"), "B", "Shared idea.", "Both patterns can fit when stopping is very hard despite harm."),
        _DA_MCQ("difficult", "alex_stop", "Alex (fictional) wants to stop but finds it very hard. A fair science sentence is", _mcq_opts("wanting to stop proves that it was never dependence at all", "that fits dependence; help is signposted, not collected as a file", "Alex only needs more willpower, so no outside help is needed", "Alex should type a use history here so the app can help"), "B", "Model + signpost.", "Wanting to stop but finding it very hard fits the model. Help is signposted, not stored as a file."),
        _DA_MCQ("difficult", "two_again", "Substance and behavioural: how many kinds of dependence is that?", _mcq_opts("one", "two", "three", "four"), "B", "Two.", "Count the two kinds: chemical versus repeated action."),
        _DA_KEY("difficult", "harm_word", "Write the word for damage to health, money, learning or relationships from dependence.", "harm", "Harm.", "Name the damage that can hit health, money, learning or relationships."),
        _DA_NUM("difficult", "signpost1", "How many clinics does this app run for addiction treatment? Enter 0.", 0, "The app is not a clinic.", "This page is not a treatment clinic. Count how many clinics it runs."),
        _DA_ORD("difficult", "help_ord", "Order harm from dependence, then help as signposted support.", ["harm", "help"], _HELP_BANK, "Harm, then help.", "First the damage idea, then signposted help from a trusted adult or service."),
        _DA_PICK("difficult", "help_not", "Select the two items that do not belong.", ["shame", "hide"], _HELP_BANK, 2, "No shaming; do not hide signposts.", "Pick shaming a named classmate, and hiding all signposts."),
    ],
}

_DA_STANDARD = {
    "foundational": (
        'dependence_addiction_foundational_mcq_behaviour',
        'dependence_addiction_foundational_keyword_add_word',
        'dependence_addiction_foundational_number_kinds2',
        'dependence_addiction_foundational_order_plea_dep',
        'dependence_addiction_foundational_pick_plea_ok',
    ),
    "intermediate": (
        'dependence_addiction_intermediate_mcq_adult',
        'dependence_addiction_intermediate_keyword_depend_word',
        'dependence_addiction_intermediate_number_zero_use',
        'dependence_addiction_intermediate_order_kind_ord',
        'dependence_addiction_intermediate_pick_kind_ok',
    ),
    "difficult": (
        'dependence_addiction_difficult_mcq_alex_stop',
        'dependence_addiction_difficult_keyword_harm_word',
        'dependence_addiction_difficult_number_signpost1',
        'dependence_addiction_difficult_order_help_ord',
        'dependence_addiction_difficult_pick_help_not',
    ),
}
eursc_science_dependence_addiction, eursc_science_dependence_addiction_variants = bind_eursc_topic(
    'dependence_addiction',
    _DA_POOLS,
    _DA_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: DEPENDENCE_ADDICTION_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: DEPENDENCE_ADDICTION_SMS_POOLS,
    },
)

_TOB_BANK = (
    {"id": "disease", "text": "Tobacco use is linked to disease and earlier death in public evidence"},
    {"id": "nicotine", "text": "Nicotine is addictive"},
    {"id": "harmless", "text": "Tobacco smoke is a health food"},
    {"id": "ask_smoke", "text": "The quiz should ask who smokes"},
)
_MKT_BANK = (
    {"id": "industry", "text": "Industry adverts are not independent scientific evidence"},
    {"id": "initiate", "text": "Starting young raises addiction risk in the public model"},
    {"id": "trust_ad", "text": "A stylish advert is the same as a health study"},
    {"id": "vape_safe", "text": "Vaping is proven harmless for everyone"},
)
_PREV_BANK = (
    {"id": "prevent", "text": "Prevention aims to reduce uptake, not to run a confession"},
    {"id": "uncertain", "text": "Vaping still has uncertainty; nicotine can still addict"},
    {"id": "spy_vape", "text": "Pupils must list devices they have tried"},
    {"id": "ignore_data", "text": "Mortality data can be ignored if a poster looks confident"},
)

_TB_POOLS = {
    "foundational": [
        _TB_MCQ("foundational", "disease", "Public evidence links tobacco use to", _mcq_opts("better lung capacity", "disease and earlier death", "lower stress and longer life", "harm only after fifty years"), "B", "Harm evidence.", "Public evidence links this product to illness and earlier death, not to longer life."),
        _TB_MCQ("foundational", "nicotine", "Nicotine is", _mcq_opts("a vitamin", "addictive", "harmless", "a flavouring"), "B", "Addictive chemical.", "This chemical can create a hard-to-stop pattern. It is not a vitamin."),
        _TB_MCQ("foundational", "advert", "A tobacco advert is", _mcq_opts("the same as a peer-reviewed study", "marketing, not independent scientific evidence", "reliable evidence, because adverts are checked by law", "a health warning written by doctors"), "B", "Critique the source.", "An advert is marketing. It is not the same as an independent study."),
        _TB_MCQ("foundational", "prevent", "Prevention means", _mcq_opts("treating people who are already dependent on nicotine", "reducing uptake using public health ideas, not a use survey", "banning every product so that nobody can ever buy one", "finding out which pupils in the class already use tobacco"), "B", "Reduce uptake, no confession.", "The aim is to reduce uptake using public-health ideas, not to run a confession."),
        _TB_MCQ("foundational", "vape", "Vaping is", _mcq_opts("proven harmless for everyone who tries it", "still uncertain in important ways; nicotine can still addict", "just flavoured water vapour with nothing addictive in it", "exactly as harmful as smoking tobacco in every single way"), "B", "Uncertainty plus nicotine.", "The scientific position is uncertainty plus the same addictive chemical — not 'harmless for everyone'."),
        _TB_MCQ("foundational", "not_ask", "This quiz", _mcq_opts("asks who smokes so it can give advice", "does not ask who smokes", "keeps a private count of each pupil's cigarettes", "asks only about relatives who smoke"), "B", "No disclosure.", "The quiz teaches ideas. It does not harvest personal tobacco status."),
        _TB_KEY("foundational", "nic_word", "Write the word for the addictive chemical in tobacco and many vapes.", "nicotine", "Nicotine.", "One word for the chemical that can create a hard-to-stop pattern in tobacco and many vapes."),
        _TB_NUM("foundational", "zero_ask", "How many smoking-status questions should this quiz ask a pupil? Enter 0.", 0, "Zero.", "Personal smoking-status questions belong nowhere here. Count how many the quiz should ask."),
        _TB_ORD("foundational", "dis_nic", "Order disease/death evidence, then nicotine as addictive.", ["disease", "nicotine"], _TOB_BANK, "Harm, then the chemical.", "First the public harm evidence, then the addictive chemical."),
        _TB_PICK("foundational", "tob_ok", "Select disease-link and nicotine.", ["disease", "nicotine"], _TOB_BANK, 2, "Harm and nicotine. No smoke survey.", "Keep the disease link and the addictive chemical. Drop asking who uses it."),
    ],
    "intermediate": [
        _TB_MCQ("intermediate", "young", "Starting young is a concern because", _mcq_opts("young people cannot become addicted until they are adults", "initiation can raise addiction risk in the public model", "the quiz needs each pupil's age of first use to check the risk", "nicotine only harms people who start after the age of thirty"), "B", "Initiation risk, no age-of-first-use harvest.", "Starting at a younger age can raise addiction risk in the public model. Do not harvest ages of first use."),
        _TB_MCQ("intermediate", "industry", "Industry influence matters because", _mcq_opts("companies always publish independent trials as the only source", "marketing can push uptake; it is not the same as independent evidence", "a company's own research is the most reliable evidence about its product", "adverts are checked by scientists before they are allowed to be shown"), "B", "Source critique.", "Marketing can push uptake. That is not the same as independent evidence."),
        _TB_MCQ("intermediate", "second", "Smoke in a shared space can", _mcq_opts("only harm the smoker, since exhaled smoke has nothing left in it", "expose others; this is a public-health idea, not a household interrogation", "be made completely safe for others by opening one window", "require the quiz to list who smokes in each pupil's home"), "B", "Exposure idea, no household file.", "Smoke in a shared space can expose others. That is a public-health idea, not a household interrogation."),
        _TB_MCQ("intermediate", "vape2", "Calling vaping a harmless swap is", _mcq_opts("a proven fact, since the long-term studies are finished", "not correct: uncertainty remains and nicotine can still addict", "correct, because vapour contains no nicotine at all", "correct, because anything safer than smoking must be harmless"), "B", "Not proven harmless.", "Calling it a harmless swap is not correct: uncertainty remains and the chemical can still addict."),
        _TB_MCQ("intermediate", "data", "Mortality figures in a textbook table are", _mcq_opts("a prediction of which named people will die", "public evidence to read, not a survey of the room", "an advert paid for by a tobacco company", "an opinion, since numbers about death cannot be checked"), "B", "Public data.", "Textbook mortality figures are public evidence to read, not a survey of the room."),
        _TB_MCQ("intermediate", "bar_more", "<p>In this sketch, which bar is the largest count?</p>" + str(outbreak_bars(title="Largest count")), _mcq_opts("A", "C", "B", "all three bars are equal"), "B", "C is the tall bar.", "Compare the bars and pick the letter with the largest count in the sketch."),
        _TB_KEY("intermediate", "tob_word", "Write the word for the plant-product smoked or otherwise used that this lesson links to disease.", "tobacco", "Tobacco.", "Name the plant-product this lesson links to disease."),
        _TB_NUM("intermediate", "eight_model", "The model bars use 8 as the largest case count. Enter 8.", 8, "Eight in the sketch.", "The stem already names the largest case count on the bars. Copy that whole number."),
        _TB_ORD("intermediate", "mkt", "Order industry adverts as not independent evidence, then initiation risk.", ["industry", "initiate"], _MKT_BANK, "Source, then uptake.", "First that industry adverts are not independent evidence, then the initiation-risk idea."),
        _TB_PICK("intermediate", "mkt_ok", "Select industry-as-marketing and initiation risk.", ["industry", "initiate"], _MKT_BANK, 2, "Two ideas. Adverts are not studies.", "Choose marketing-as-not-a-study and initiation risk. Skip 'stylish advert equals health study'."),
    ],
    "difficult": [
        _TB_MCQ("difficult", "critique", "A stylish vape advert that says 'totally safe' should be", _mcq_opts("trusted, because adverts are checked by law before they are shown", "treated as marketing to critique, not as a health study", "accepted as proof that the product has been tested for safety", "used to find out which pupils in the class vape"), "B", "Advert critique.", "Treat a 'totally safe' stylish advert as marketing to critique, not as a health study."),
        _TB_MCQ("difficult", "both_n", "Tobacco smoke and many vapes can both involve", _mcq_opts("only harmless water vapour", "nicotine and therefore addiction risk", "tar, but no addictive chemical", "a chemical that only addicts adults"), "B", "Nicotine overlap.", "Smoke and many vapes can share the same addictive chemical, so addiction risk still applies."),
        _TB_MCQ("difficult", "prevent2", "A prevention message is misused if it", _mcq_opts("uses public evidence", "turns the quiz into a confession about use", "critiques an advert", "signposts qualified help"), "B", "No confession.", "A prevention message is misused if it turns the quiz into a confession about use."),
        _TB_MCQ("difficult", "uncertain2", "Uncertainty about long-term vaping harm means", _mcq_opts("it has been proven completely safe, since no harm has been found yet", "scientists do not yet have the full picture; nicotine can still addict", "the long-term studies are finished and show no harm at all", "adverts can fill the gap in evidence until the studies are done"), "B", "Honest uncertainty.", "Scientists do not yet have the full picture of long-term vaping harm; the chemical can still addict."),
        _TB_MCQ("difficult", "alex_ad", "Alex (fictional) believes an advert because it looks sporty. A science reply is", _mcq_opts("sporty branding proves the product is safe for athletes", "look and sporty branding are not independent evidence", "an advert is only allowed if every claim in it is true", "ask what Alex uses before replying to the advert"), "B", "Evidence vs branding.", "Look and sporty branding are not independent evidence. Do not ask what a character uses."),
        _TB_MCQ("difficult", "zero_status", "How many smoking statuses should this app store for a pupil?", _mcq_opts("one, updated at the start of each lesson", "none — it teaches ideas, it does not store status", "one for the pupil and one for each relative", "a daily count, kept private to the pupil"), "B", "None.", "This app teaches ideas. It does not store a pupil's smoking status."),
        _TB_KEY("difficult", "prevent_word", "Write the word for reducing uptake of tobacco or nicotine products.", "prevention", "Prevention.", "Name the public-health aim of reducing uptake of these products."),
        _TB_NUM("difficult", "bars_n", "How many labelled bars are in the sketch (A, B, C)?", 3, "Three.", "How many lettered bars does the sketch show? Count A, B and C."),
        _TB_ORD("difficult", "prev_ord", "Order prevention as reducing uptake, then vaping uncertainty.", ["prevent", "uncertain"], _PREV_BANK, "Prevention, then uncertainty.", "First reducing uptake, then the idea that vaping still has uncertainty."),
        _TB_PICK("difficult", "prev_not", "Select the two items that do not belong.", ["spy_vape", "ignore_data"], _PREV_BANK, 2, "No device lists; do not ignore mortality data.", "Pick listing devices a pupil has tried, and ignoring mortality data because a poster looks confident."),
    ],
}

_TB_STANDARD = {
    "foundational": (
        'tobacco_foundational_mcq_advert',
        'tobacco_foundational_keyword_nic_word',
        'tobacco_foundational_number_zero_ask',
        'tobacco_foundational_order_dis_nic',
        'tobacco_foundational_pick_tob_ok',
    ),
    "intermediate": (
        'tobacco_intermediate_mcq_bar_more',
        'tobacco_intermediate_keyword_tob_word',
        'tobacco_intermediate_number_eight_model',
        'tobacco_intermediate_order_mkt',
        'tobacco_intermediate_pick_mkt_ok',
    ),
    "difficult": (
        'tobacco_difficult_mcq_alex_ad',
        'tobacco_difficult_keyword_prevent_word',
        'tobacco_difficult_number_bars_n',
        'tobacco_difficult_order_prev_ord',
        'tobacco_difficult_pick_prev_not',
    ),
}
eursc_science_tobacco, eursc_science_tobacco_variants = bind_eursc_topic(
    'tobacco',
    _TB_POOLS,
    _TB_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: TOBACCO_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: TOBACCO_SMS_POOLS,
    },
)
