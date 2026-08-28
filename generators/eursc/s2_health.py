"""S2 Unit 2.2 Health — 2.2.1–2.2.5."""
from generators.eursc.science_shared import (
    habit_bars,
    infection_chain,
    outbreak_bars,
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
                "Use health ideas from the lesson. Scenarios are fictional.",
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
                "Check the health idea. This is not a personal survey.",
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
        _HL_MCQ("foundational", "diet", "A balanced diet in this lesson is", _mcq_opts("one magic food that replaces all others", "a mix of food groups over time so the body gets what it needs", "a ranking of classmates by lunch", "a private meal survey stored by the app"), "B", "Mix over time, not a survey."),
        _HL_MCQ("foundational", "activity", "Regular physical activity is modelled as", _mcq_opts("a way to rank bodies in the quiz", "something that can support health, using public evidence", "a replacement for sleep forever", "a demand that pupils post step counts"), "B", "Public health idea, not a body contest."),
        _HL_MCQ("foundational", "mental", "Mental health in this course is", _mcq_opts("not part of health", "part of health; personal distress is signposted to qualified help", "a joke to share in the quiz", "a mood ranking of the class"), "B", "Health includes mind; no disclosure."),
        _HL_MCQ("foundational", "micro", "The microbiome is", _mcq_opts("a brand of trainers", "living microorganisms that interact with the body", "a light-year", "a class confession list"), "B", "Living microbes, not a survey."),
        _HL_MCQ("foundational", "sleep", "This lesson treats sleep as", _mcq_opts("optional if a poster is famous", "a health need that late screens can crowd out", "a contest to stay awake", "data the quiz must collect from each pupil"), "B", "Sleep vs unmanaged screens."),
        _HL_MCQ("foundational", "sleep_bar", "<p>Which letter is the tall sleep bar?</p>" + str(habit_bars(title="Sleep bar")), _mcq_opts("C", "A", "B", "a classmate's name"), "B", "A is sleep."),
        _HL_KEY("foundational", "diet_word", "Write the word for the usual mix of foods a person eats over time.", "diet", "Diet here means the mix of foods, not a confession."),
        _HL_NUM("foundational", "sleep_h", "This lesson uses 8 as a rounded whole number of hours of sleep often discussed in health advice. Enter 8.", 8, "Eight hours as a teaching figure, not a personal target collected here."),
        _HL_ORD("foundational", "diet_act", "Order a mixed diet, then regular activity.", ["mix", "activity"], _DIET_BANK, "Diet mix, then activity."),
        _HL_PICK("foundational", "diet_ok", "Select the two healthy-living ideas that belong here.", ["mix", "activity"], _DIET_BANK, 2, "Mix and activity. Ranking bodies is not the lesson."),
    ],
    "intermediate": [
        _HL_MCQ("intermediate", "alex", "Alex (fictional) skips mixed food groups for weeks. A scientific comment is", _mcq_opts("rank Alex in the class", "the body may miss nutrients over time; this is not a demand for Alex's menu", "Alex must post meals in the quiz", "skipping groups is always a joke"), "B", "Third-person nutrient idea."),
        _HL_MCQ("intermediate", "screen", "Unmanaged late screen use can", _mcq_opts("increase sleep automatically", "crowd out sleep and recovery time", "replace the need for food", "require pupils to list every app they open"), "B", "Time trade-off."),
        _HL_MCQ("intermediate", "respect", "Respectful relationships in this lesson means", _mcq_opts("the quiz storing who likes whom", "communication and consent ideas without asking for private stories", "ranking popularity", "ignoring a classmate in distress as a health plan"), "B", "Curriculum idea, not a social graph."),
        _HL_MCQ("intermediate", "help", "If a fictional character is in distress, the lesson's next step is", _mcq_opts("publish the story in the quiz", "signpost a trusted adult or qualified help; the app does not diagnose", "compare moods with the class", "ignore it because health is only food"), "B", "Signpost."),
        _HL_MCQ("intermediate", "micro2", "Not every microorganism is a pathogen. That is why", _mcq_opts("the microbiome idea can include helpful as well as harmful roles", "pupils must swab each other for the quiz", "all microbes should be named in a confession", "sleep is a bacterium"), "B", "Nuance, no swabs in the app."),
        _HL_MCQ("intermediate", "activity_bar", "<p>Which letter is the medium activity bar?</p>" + str(habit_bars(title="Activity bar")), _mcq_opts("A", "B", "C", "a private step count"), "B", "B is activity."),
        _HL_KEY("intermediate", "sleep_word", "Write the word for the regular rest period this lesson treats as a health need.", "sleep", "Sleep."),
        _HL_NUM("intermediate", "groups3", "A simple mix in this lesson names 3 ideas: food mix, activity, sleep. Enter 3.", 3, "Three teaching ideas."),
        _HL_ORD("intermediate", "mind", "Order mental health as part of health, then signposting qualified help.", ["mental", "signpost"], _MIND_BANK, "Name it, then signpost."),
        _HL_PICK("intermediate", "habit_ok", "Select sleep and screen-time as health ideas.", ["sleep", "screens"], _HABIT_BANK, 2, "Sleep and screens. The app does not spy on lunch seats."),
    ],
    "difficult": [
        _HL_MCQ("difficult", "not_rank", "A health lesson is misused if it", _mcq_opts("uses public evidence about activity", "ranks pupils' bodies, meals or moods", "signposts qualified help", "uses a fictional case"), "B", "No ranking, no disclosure."),
        _HL_MCQ("difficult", "evidence", "Claims about a food or app should be", _mcq_opts("believed if the advert is exciting", "checked against public evidence, not a classmate's private list", "stored as medical records in this app", "used to diagnose the class"), "B", "Evidence, not records."),
        _HL_MCQ("difficult", "micro3", "Calling the microbiome a class vote is wrong because", _mcq_opts("votes are SI units", "it is a biological community idea, not a popularity poll", "microbes are light-years", "sleep is a vote"), "B", "Biology, not a poll."),
        _HL_MCQ("difficult", "both", "Food mix and activity together matter because", _mcq_opts("health is only one slogan", "the body uses food energy and also needs movement and rest", "the quiz must weigh pupils", "screens replace food"), "B", "Several needs."),
        _HL_MCQ("difficult", "jordan", "Jordan (fictional) is exhausted after late screens. A fair science comment is", _mcq_opts("demand Jordan's screen log in the quiz", "late screens can trade off against sleep; personal logs stay private", "exhaustion is always a virus", "rank Jordan against the class"), "B", "Mechanism without a log."),
        _HL_MCQ("difficult", "screen_bar", "<p>Which letter is the short screen-time bar?</p>" + str(habit_bars(title="Screen bar")), _mcq_opts("A", "C", "B", "a pupil handle"), "B", "C is screens."),
        _HL_KEY("difficult", "health_word", "Write the word for living microorganisms that interact with the body (one token).", "microbiome", "Microbiome."),
        _HL_NUM("difficult", "bars3", "The habit sketch has how many labelled bars?", 3, "A, B and C."),
        _HL_ORD("difficult", "micro_ord", "Order the microbiome as living microbes, then the false idea that it is a snack vote.", ["live", "not_vote"], _MICRO_BANK, "Biology first, then the misconception."),
        _HL_PICK("difficult", "mind_not", "Select the two items that do not belong in this lesson.", ["joke", "rank_mood"], _MIND_BANK, 2, "Jokes and mood rankings are out."),
    ],
}

eursc_science_healthy_living, eursc_science_healthy_living_variants = _bind(
    "healthy_living", _HL_POOLS
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
        _ID_MCQ("foundational", "bact", "Bacteria in this lesson are modelled as", _mcq_opts("a unit of time", "living cells that can act as pathogens", "the same as a virus always", "a class attendance list"), "B", "Living cells."),
        _ID_MCQ("foundational", "vir", "Viruses typically", _mcq_opts("are exactly the same as bacteria", "need a host cell to multiply", "are a food group", "are a sleep bar"), "B", "Host required."),
        _ID_MCQ("foundational", "spread", "An infectious disease can spread because", _mcq_opts("it is always inherited only", "a pathogen can pass from a source along a route to a new host", "the Moon votes", "the quiz names who coughed"), "B", "Chain of infection."),
        _ID_MCQ("foundational", "immune", "Immunity is", _mcq_opts("a brand of soap", "the body's defence, which can be innate or learned", "a light-year", "a private diagnosis the app stores"), "B", "Defence."),
        _ID_MCQ("foundational", "hygiene", "Hand hygiene can help because it may", _mcq_opts("create extra pathogens from nothing", "reduce some transmission routes", "replace all vaccines automatically", "require listing illnesses in the quiz"), "B", "Cut some routes."),
        _ID_MCQ("foundational", "source_letter", "<p>Which letter is the source in this chain?</p>" + str(infection_chain(title="Source letter")), _mcq_opts("B", "A", "C", "a pupil name"), "B", "A is the source."),
        _ID_KEY("foundational", "virus_word", "Write the word for a pathogen that needs a host cell to multiply.", "virus", "A virus."),
        _ID_NUM("foundational", "chain3", "The simple chain in this lesson has source, route and new host. Enter how many parts that is.", 3, "Three parts."),
        _ID_ORD("foundational", "chain_ord", "Order source, then route, then new host.", ["source", "route", "host"], _CHAIN_BANK, "Source → route → host."),
        _ID_PICK("foundational", "path_ok", "Select bacteria and viruses as different pathogens.", ["bacteria", "virus"], _PATH_BANK, 2, "Two kinds. The quiz does not list who was ill."),
    ],
    "intermediate": [
        _ID_MCQ("intermediate", "vax", "A vaccine is modelled as", _mcq_opts("a snack vote", "a safe exposure that trains immunity", "an antibiotic for every virus", "a record of who had which injection, stored here"), "B", "Train immunity."),
        _ID_MCQ("intermediate", "abx", "Antibiotics in this S2 model", _mcq_opts("treat all viruses", "can treat some bacterial infections but not viruses, and resistance matters", "are a food group", "must be listed from home cabinets in the quiz"), "B", "Not for viruses; resistance."),
        _ID_MCQ("intermediate", "route", "A transmission route can be", _mcq_opts("only a light-year", "droplets, contact or another path the teacher names, without naming who was ill", "a geocentric model", "a private medical file in this app"), "B", "Routes, not names."),
        _ID_MCQ("intermediate", "epi", "Epidemiology in this lesson uses", _mcq_opts("secret rumours only", "counts and patterns that can be checked, not a pupil's file", "a ranking of bodies", "Moon phases as the only cause"), "B", "Public counts."),
        _ID_MCQ("intermediate", "resist", "Antibiotic resistance becomes more likely when", _mcq_opts("antibiotics are never discussed in science", "bacteria are exposed in ways that let resistant strains spread; viruses are still not treated by antibiotics", "sleep bars get taller", "the quiz stores prescriptions"), "B", "Selection; still not for viruses."),
        _ID_MCQ("intermediate", "route_letter", "<p>Which letter is the route?</p>" + str(infection_chain(title="Route letter")), _mcq_opts("A", "B", "C", "a cough confession"), "B", "B is the route."),
        _ID_KEY("intermediate", "vax_word", "Write the word for a preparation that trains immunity using a safe exposure.", "vaccine", "Vaccine."),
        _ID_NUM("intermediate", "day3", "A model outbreak has 2, then 4, then 8 cases. Enter the number of cases on the third day.", 8, "Doubling model: 8."),
        _ID_ORD("intermediate", "vax_ord", "Order immunity as defence, then a vaccine as training.", ["immune", "vaccine"], _VAX_BANK, "Defence, then training."),
        _ID_PICK("intermediate", "hyg_ok", "Select hygiene and outbreak-as-counts.", ["hygiene", "data"], _HYG_BANK, 2, "Hygiene and public counts. Not blame."),
    ],
    "difficult": [
        _ID_MCQ("difficult", "not_abx", "Giving antibiotics for a typical virus infection is a poor fit because", _mcq_opts("viruses are food", "antibiotics target bacteria, not viruses, and misuse can feed resistance", "vaccines are bacteria", "the app must record every tablet"), "B", "Wrong target plus resistance."),
        _ID_MCQ("difficult", "double", "If cases go 2, then 4, then 8 in a classroom token model,", _mcq_opts("the pattern cannot be a model", "the count is doubling each step in that model, not a named person's file", "C must be a pupil handle", "sanitation is a light-year"), "B", "Model counts."),
        _ID_MCQ("difficult", "host", "A new host can later act as a source. That is why", _mcq_opts("routes never matter", "breaking a route (hygiene, distance rules the teacher sets) can slow a chain", "the quiz should publish names", "bacteria equal viruses"), "B", "Break the chain."),
        _ID_MCQ("difficult", "vax2", "Vaccination programmes are public health tools. This app", _mcq_opts("stores whose injections they have had", "teaches the idea; it does not store vaccination status", "diagnoses coughs", "replaces the teacher"), "B", "No status file."),
        _ID_MCQ("difficult", "model", "A sticker or counter 'infection' in class is", _mcq_opts("a real pathogen cultured in the app", "a model of spread; it does not replace a risk-assessed practical and is not a diagnosis", "proof a named pupil is ill", "an antibiotic"), "B", "Model only."),
        _ID_MCQ("difficult", "host_letter", "<p>Which letter is the new host?</p>" + str(infection_chain(title="Host letter")), _mcq_opts("A", "C", "B", "a medical file"), "B", "C is the new host."),
        _ID_MCQ("difficult", "bar_c", "<p>Which day has the most cases in this model?</p>" + str(outbreak_bars(title="Most cases")), _mcq_opts("A", "C", "B", "a named pupil"), "B", "C is 8 cases."),
        _ID_KEY("difficult", "imm_word", "Write the word for the body's defence that can be innate or learned.", "immunity", "Immunity."),
        _ID_NUM("difficult", "abx0", "How many virus infections are treated by antibiotics in this lesson's model? Enter 0.", 0, "Antibiotics are not for viruses here."),
        _ID_ORD("difficult", "full_chain", "Order source, route, then host.", ["source", "route", "host"], _CHAIN_BANK, "The chain again."),
        _ID_PICK("difficult", "path_not", "Select the two statements that do not belong.", ["same", "who"], _PATH_BANK, 2, "Not the same object; no illness list."),
    ],
}

# infectious difficult has 7 MCQ - that's 7+1+1+1+1=11 items in difficult. Foundational and intermediate have 10. Need exactly unique stems - extra MCQ is OK as long as counts: mcq will be 6+6+7=19 >=15, typed 4*3=12. Wait difficult has 7 MCQ + key + num + ord + pick = 11 items. That's fine, more than 10.

# Actually wait I counted difficult: 7 mcq (not_abx, double, host, vax2, model, host_letter, bar_c) + key + num + ord + pick = 11. Good.

eursc_science_infectious_disease, eursc_science_infectious_disease_variants = _bind(
    "infectious_disease", _ID_POOLS
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
        _NI_MCQ("foundational", "split", "A noninfectious disease", _mcq_opts("always jumps from host to host like a cold", "does not spread like an infection", "is always a virus", "must be listed from home in the quiz"), "B", "Not a chain of infection."),
        _NI_MCQ("foundational", "infect_vs", "An infectious disease", _mcq_opts("never involves a pathogen", "can pass from a source along a route to a new host", "is always inherited only", "is a sleep bar"), "B", "Can spread."),
        _NI_MCQ("foundational", "inherit", "An inherited condition in this lesson is", _mcq_opts("proof the quiz should store family files", "a long-term or genetic idea taught with public examples, not a family survey", "always an infection", "a ranking of classmates"), "B", "No family files."),
        _NI_MCQ("foundational", "defic", "A deficiency disease can link to", _mcq_opts("a light-year", "missing nutrients in the diet over time, using public examples", "a class vote", "a demand for private menus"), "B", "Nutrient gap, not a menu upload."),
        _NI_MCQ("foundational", "mental", "Mental illness in this lesson is", _mcq_opts("a joke", "a health condition that can be supported; the app does not diagnose", "always an infection from a cough", "a mood ranking"), "B", "Clinical, no diagnosis here."),
        _NI_MCQ("foundational", "support", "Treatment and support belong with", _mcq_opts("this quiz storing diagnoses", "qualified people; the page teaches categories, not personal files", "a popularity poll", "ignoring symptoms as a science method"), "B", "Signpost."),
        _NI_KEY("foundational", "support_word", "Write the word for help and treatment around a health condition (one token).", "support", "Support."),
        _NI_NUM("foundational", "two_kinds", "This lesson splits disease into infectious and noninfectious. Enter how many kinds that is.", 2, "Two kinds."),
        _NI_ORD("foundational", "split_ord", "Order infectious as able to pass, then noninfectious as not spreading that way.", ["infect", "noninfect"], _CLASS_BANK, "Spread vs not."),
        _NI_PICK("foundational", "class_ok", "Select the two correct classification ideas.", ["infect", "noninfect"], _CLASS_BANK, 2, "Two kinds. No family-history harvest."),
    ],
    "intermediate": [
        _NI_MCQ("intermediate", "pollute", "Pollution or occupation can matter because", _mcq_opts("air quality is a rumour only", "some exposures are linked to disease in public evidence", "the quiz must list every workplace of relatives", "occupation is a virus"), "B", "Environmental risk, not a job survey."),
        _NI_MCQ("intermediate", "sam", "Sam (fictional) has a long-term condition that is not catching. A fair comment is", _mcq_opts("avoid Sam as if it were a cold", "it can be noninfectious; do not treat Sam as a source of infection", "publish Sam's file in the quiz", "long-term always means a virus"), "B", "Third person, no file."),
        _NI_MCQ("intermediate", "both", "Infectious and noninfectious can both", _mcq_opts("require a classmate ranking", "need evidence and, where personal, qualified care — not this app's diagnosis", "be cured by a slogan only", "be stored as family trees here"), "B", "Evidence and signpost."),
        _NI_MCQ("intermediate", "def2", "Public examples of deficiency (for example scurvy historically) teach that", _mcq_opts("pupils must confess snacks", "missing a nutrient can harm health over time", "deficiency is always a virus", "the app is a clinic"), "B", "History/public evidence."),
        _NI_MCQ("intermediate", "not_fault", "Blaming a person as the whole cause of every condition is", _mcq_opts("required science", "often unfair; inherited, environmental and infectious causes differ", "how the quiz grades bodies", "a sanitation unit"), "B", "Causes differ."),
        _NI_MCQ("intermediate", "clinic", "This app", _mcq_opts("diagnoses mental illness", "does not diagnose; it teaches that mental illness is real and support exists", "ranks whose relative is ill", "replaces a nurse"), "B", "No diagnosis."),
        _NI_KEY("intermediate", "pollute_word", "Write the word for harmful substances in air, water or land that can link to disease.", "pollution", "Pollution."),
        _NI_NUM("intermediate", "causes3", "A simple list in this lesson names inherited, deficiency and pollution/occupation. Enter 3.", 3, "Three cause-groups."),
        _NI_ORD("intermediate", "cause_ord", "Order inherited/systemic, then deficiency.", ["inherit", "deficiency"], _CAUSE_BANK, "Then nutrients."),
        _NI_PICK("intermediate", "cause_ok", "Select inherited/systemic and pollution/occupation.", ["inherit", "pollution"], _CAUSE_BANK, 2, "Two cause groups. Blame-ranking is out."),
    ],
    "difficult": [
        _NI_MCQ("difficult", "mix_up", "Treating a noninfectious condition as catching can", _mcq_opts("improve SI units", "stigmatise a person who is not a source of infection", "replace sanitation", "fill the quiz with family files"), "B", "Stigma from a wrong model."),
        _NI_MCQ("difficult", "env", "Occupation-linked disease is a reason to", _mcq_opts("harvest job titles from pupils", "study exposures with public evidence and workplace controls, not a family survey", "ignore pollution", "call it a vaccine"), "B", "Public occupational health."),
        _NI_MCQ("difficult", "mental2", "A mental illness is", _mcq_opts("always a choice to rank in class", "a health condition; jokes and rankings do not belong in the quiz", "always bacterial", "stored automatically from chat logs"), "B", "Condition, not a joke."),
        _NI_MCQ("difficult", "support2", "Qualified support can include", _mcq_opts("this app setting a diagnosis code", "clinical care the teacher signposts; the page does not collect who attends", "a popularity contest", "ignoring environmental causes always"), "B", "Signpost, no attendance list."),
        _NI_MCQ("difficult", "alex_def", "Alex (fictional) lacks a named nutrient in a textbook case. The scientific move is", _mcq_opts("demand Alex's real shopping list", "link the case to deficiency using the public story, not a personal menu", "call it a virus automatically", "rank Alex"), "B", "Case study, not a list."),
        _NI_MCQ("difficult", "two_n", "Infectious vs noninfectious is how many top-level kinds in this lesson?", _mcq_opts("one", "two", "eight", "zero"), "B", "Two."),
        _NI_KEY("difficult", "inherit_word", "Write the word for a condition passed in families by genetic information (one token).", "inherited", "Inherited."),
        _NI_NUM("difficult", "zero_file", "How many family medical histories should this quiz collect? Enter 0.", 0, "Zero."),
        _NI_ORD("difficult", "sup_ord", "Order mental illness as a condition, then support without diagnosing in the app.", ["mental_ill", "support"], _SUPPORT_BANK, "Name it, then signpost."),
        _NI_PICK("difficult", "sup_not", "Select the two items that do not belong.", ["rank_ill", "ignore"], _SUPPORT_BANK, 2, "No ranking relatives; slogans are not care."),
    ],
}

eursc_science_noninfectious_disease, eursc_science_noninfectious_disease_variants = _bind(
    "noninfectious_disease", _NI_POOLS
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
        _DA_MCQ("foundational", "pleasure", "Ordinary pleasure in this lesson is", _mcq_opts("the same as dependence always", "possible without being dependence", "a reason to collect use lists", "a vaccine"), "B", "Pleasure is not automatically addiction."),
        _DA_MCQ("foundational", "depend", "Dependence means", _mcq_opts("a one-off enjoyable event", "it is very hard to stop even when harm is clear", "a food group", "a class popularity score"), "B", "Hard to stop despite harm."),
        _DA_MCQ("foundational", "substance", "Substance dependence involves", _mcq_opts("only a light-year", "a drug or similar chemical, taught with fictional cases, not a use survey", "sleep bars only", "storing who uses what"), "B", "Chemical + no survey."),
        _DA_MCQ("foundational", "behaviour", "Behavioural dependence can involve", _mcq_opts("only bacteria", "a repeated action that is hard to stop, using third-person examples", "a demand for private logs", "a geocentric model"), "B", "Action pattern, no logs."),
        _DA_MCQ("foundational", "help", "If a fictional character needs help, the lesson points to", _mcq_opts("publishing names in the quiz", "a trusted adult or qualified service; this app does not treat addiction", "ignoring harm", "a class vote"), "B", "Signpost."),
        _DA_MCQ("foundational", "not_ask", "This quiz", _mcq_opts("must ask what each pupil uses", "does not ask what a pupil uses", "stores use as medical records", "ranks whose relative uses what"), "B", "No disclosure."),
        _DA_KEY("foundational", "add_word", "Write the word for dependence that is very hard to stop despite harm.", "addiction", "Addiction / dependence idea; keyword addiction."),
        _DA_NUM("foundational", "kinds2", "This lesson names substance and behavioural dependence. Enter 2.", 2, "Two kinds."),
        _DA_ORD("foundational", "plea_dep", "Order ordinary pleasure, then dependence as hard to stop.", ["pleasure", "depend"], _PLEA_BANK, "Pleasure first, then dependence."),
        _DA_PICK("foundational", "plea_ok", "Select pleasure-without-dependence and dependence-despite-harm.", ["pleasure", "depend"], _PLEA_BANK, 2, "Two ideas. No use survey."),
    ],
    "intermediate": [
        _DA_MCQ("intermediate", "sam_use", "Sam (fictional) keeps using a substance after clear harm. That fits", _mcq_opts("ordinary one-off pleasure only", "dependence in this lesson's model", "a virus chain only", "a request for Sam's real cabinet list"), "B", "Third-person dependence."),
        _DA_MCQ("intermediate", "game", "Jordan (fictional) cannot stop a game pattern that harms sleep and learning. That can be", _mcq_opts("impossible by definition", "behavioural dependence in this model", "proof the quiz needs Jordan's login", "an antibiotic"), "B", "Behavioural, no login."),
        _DA_MCQ("intermediate", "social", "Social context can matter because", _mcq_opts("science ignores other people", "pressure, availability and marketing can raise risk, without asking who felt pressure", "the quiz stores friend lists", "context is a bacterium"), "B", "Risk factors, no friend graph."),
        _DA_MCQ("intermediate", "harm", "Harm from dependence can include", _mcq_opts("only a change of SI units", "health, money, learning or relationships in public/fictional cases", "a requirement to confess", "a taller sleep bar automatically"), "B", "Several harms."),
        _DA_MCQ("intermediate", "not_fun", "If something is enjoyable it", _mcq_opts("can never become harmful", "can still become dependence in some cases", "must be logged in the quiz", "is always a vaccine"), "B", "Enjoyable ≠ safe forever."),
        _DA_MCQ("intermediate", "adult", "Personal questions about use belong with", _mcq_opts("this generator", "a trusted adult or qualified service, not a class quiz", "a public leaderboard", "a rumour site"), "B", "Signpost."),
        _DA_KEY("intermediate", "depend_word", "Write the word for finding it very hard to stop even when harm is clear.", "dependence", "Dependence."),
        _DA_NUM("intermediate", "zero_use", "How many personal use-lists should this quiz collect? Enter 0.", 0, "Zero."),
        _DA_ORD("intermediate", "kind_ord", "Order substance dependence, then behavioural dependence.", ["substance", "behaviour"], _KIND_BANK, "Chemical, then action pattern."),
        _DA_PICK("intermediate", "kind_ok", "Select substance and behavioural dependence.", ["substance", "behaviour"], _KIND_BANK, 2, "Two kinds. No class use-list."),
    ],
    "difficult": [
        _DA_MCQ("difficult", "shame", "Shaming a named classmate is", _mcq_opts("the scientific method", "not science and not allowed in this quiz", "a sanitation control", "a vaccine"), "B", "No shame lists."),
        _DA_MCQ("difficult", "risk", "Risk is higher in some social settings. The quiz still", _mcq_opts("asks who felt pressure", "teaches the idea with fictional cases only", "stores DMs", "diagnoses the class"), "B", "Idea, not a confession."),
        _DA_MCQ("difficult", "help2", "Support routes in this lesson are", _mcq_opts("this app as a clinic", "trusted adults and qualified services; no treatment record is stored here", "a popularity poll", "hiding all signposts"), "B", "Signpost only."),
        _DA_MCQ("difficult", "both_k", "Substance and behavioural patterns both", _mcq_opts("require a use survey", "can fit dependence when stopping is very hard despite harm", "are bacteria", "are light-years"), "B", "Shared idea."),
        _DA_MCQ("difficult", "alex_stop", "Alex (fictional) wants to stop but finds it very hard. A fair science sentence is", _mcq_opts("Alex must type a use history here", "that fits dependence; help is signposted, not collected as a file", "Alex should be ranked", "it cannot be dependence if Alex is fictional"), "B", "Model + signpost."),
        _DA_MCQ("difficult", "two_again", "Substance vs behavioural is how many kinds in this lesson?", _mcq_opts("one", "two", "fourteen", "zero"), "B", "Two."),
        _DA_KEY("difficult", "harm_word", "Write the word for damage to health, money, learning or relationships from dependence.", "harm", "Harm."),
        _DA_NUM("difficult", "signpost1", "How many clinics does this app run for addiction treatment? Enter 0.", 0, "The app is not a clinic."),
        _DA_ORD("difficult", "help_ord", "Order harm from dependence, then help as signposted support.", ["harm", "help"], _HELP_BANK, "Harm, then help."),
        _DA_PICK("difficult", "help_not", "Select the two items that do not belong.", ["shame", "hide"], _HELP_BANK, 2, "No shaming; do not hide signposts."),
    ],
}

eursc_science_dependence_addiction, eursc_science_dependence_addiction_variants = _bind(
    "dependence_addiction", _DA_POOLS
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
        _TB_MCQ("foundational", "disease", "Public evidence links tobacco use to", _mcq_opts("longer life only", "disease and earlier death", "a food group", "a class popularity prize"), "B", "Harm evidence."),
        _TB_MCQ("foundational", "nicotine", "Nicotine is", _mcq_opts("a vitamin", "addictive", "a light-year", "a reason to collect who uses it"), "B", "Addictive chemical."),
        _TB_MCQ("foundational", "advert", "A tobacco advert is", _mcq_opts("the same as a peer-reviewed study", "marketing, not independent scientific evidence", "a vaccine", "a sleep bar"), "B", "Critique the source."),
        _TB_MCQ("foundational", "prevent", "Prevention in this lesson means", _mcq_opts("forcing a confession in the quiz", "reducing uptake using public health ideas, not a use survey", "ignoring nicotine", "ranking who looks sporty"), "B", "Reduce uptake, no confession."),
        _TB_MCQ("foundational", "vape", "Vaping in this S2 model is", _mcq_opts("proven harmless for everyone", "still uncertain in important ways; nicotine can still addict", "a fruit", "a demand to list devices"), "B", "Uncertainty plus nicotine."),
        _TB_MCQ("foundational", "not_ask", "This quiz", _mcq_opts("asks who smokes", "does not ask who smokes", "stores cigarette counts", "publishes family use"), "B", "No disclosure."),
        _TB_KEY("foundational", "nic_word", "Write the word for the addictive chemical in tobacco and many vapes.", "nicotine", "Nicotine."),
        _TB_NUM("foundational", "zero_ask", "How many smoking-status questions should this quiz ask a pupil? Enter 0.", 0, "Zero."),
        _TB_ORD("foundational", "dis_nic", "Order disease/death evidence, then nicotine as addictive.", ["disease", "nicotine"], _TOB_BANK, "Harm, then the chemical."),
        _TB_PICK("foundational", "tob_ok", "Select disease-link and nicotine.", ["disease", "nicotine"], _TOB_BANK, 2, "Harm and nicotine. No smoke survey."),
    ],
    "intermediate": [
        _TB_MCQ("intermediate", "young", "Starting young is a concern because", _mcq_opts("adverts are SI units", "initiation can raise addiction risk in the public model", "the quiz must list ages of first use", "nicotine is a vitamin"), "B", "Initiation risk, no age-of-first-use harvest."),
        _TB_MCQ("intermediate", "industry", "Industry influence matters because", _mcq_opts("companies always publish independent trials as the only source", "marketing can push uptake; it is not the same as independent evidence", "influence is a bacterium", "pupils must name brands they like"), "B", "Source critique."),
        _TB_MCQ("intermediate", "second", "Smoke in a shared space can", _mcq_opts("only help health", "expose others; this is a public-health idea, not a household interrogation", "replace sanitation", "require listing who smokes at home"), "B", "Exposure idea, no household file."),
        _TB_MCQ("intermediate", "vape2", "Calling vaping a harmless swap is", _mcq_opts("required by the syllabus", "not the S2 position: uncertainty remains and nicotine can still addict", "the same as a light-year", "a reason to collect device lists"), "B", "Not proven harmless."),
        _TB_MCQ("intermediate", "data", "Mortality figures in a textbook table are", _mcq_opts("a classmate's private file", "public evidence to read, not a survey of the room", "an advert", "a vaccine"), "B", "Public data."),
        _TB_MCQ("intermediate", "bar_more", "<p>In this model sketch, which bar is the largest count?</p>" + str(outbreak_bars(title="Largest count")), _mcq_opts("A", "C", "B", "a named smoker"), "B", "C is the tall bar."),
        _TB_KEY("intermediate", "tob_word", "Write the word for the plant-product smoked or otherwise used that this lesson links to disease.", "tobacco", "Tobacco."),
        _TB_NUM("intermediate", "eight_model", "The model bars use 8 as the largest case count. Enter 8.", 8, "Eight in the sketch."),
        _TB_ORD("intermediate", "mkt", "Order industry adverts as not independent evidence, then initiation risk.", ["industry", "initiate"], _MKT_BANK, "Source, then uptake."),
        _TB_PICK("intermediate", "mkt_ok", "Select industry-as-marketing and initiation risk.", ["industry", "initiate"], _MKT_BANK, 2, "Two ideas. Adverts are not studies."),
    ],
    "difficult": [
        _TB_MCQ("difficult", "critique", "A stylish vape advert that says 'totally safe' should be", _mcq_opts("copied as a method", "treated as marketing to critique, not as a health study", "stored as a medical record", "used to ask who vapes"), "B", "Advert critique."),
        _TB_MCQ("difficult", "both_n", "Tobacco smoke and many vapes can both involve", _mcq_opts("only vitamins", "nicotine and therefore addiction risk in this model", "a requirement to confess", "a geocentric vote"), "B", "Nicotine overlap."),
        _TB_MCQ("difficult", "prevent2", "A prevention message is misused if it", _mcq_opts("uses public evidence", "turns the quiz into a confession about use", "critiques an advert", "signposts qualified help"), "B", "No confession."),
        _TB_MCQ("difficult", "uncertain2", "Uncertainty about long-term vaping harm means", _mcq_opts("it is proven safer than water", "scientists do not yet have the full picture; nicotine can still addict", "adverts replace studies", "pupils must list brands"), "B", "Honest uncertainty."),
        _TB_MCQ("difficult", "alex_ad", "Alex (fictional) believes an advert because it looks sporty. A science reply is", _mcq_opts("ask what Alex uses", "look and sporty branding are not independent evidence", "rank Alex", "store Alex's status"), "B", "Evidence vs branding."),
        _TB_MCQ("difficult", "zero_status", "How many smoking statuses should this app store for a pupil?", _mcq_opts("one per lesson", "none — it teaches ideas, it does not store status", "a family tree", "a daily count"), "B", "None."),
        _TB_KEY("difficult", "prevent_word", "Write the word for reducing uptake of tobacco or nicotine products.", "prevention", "Prevention."),
        _TB_NUM("difficult", "bars_n", "How many labelled bars are in the model sketch (A, B, C)?", 3, "Three."),
        _TB_ORD("difficult", "prev_ord", "Order prevention as reducing uptake, then vaping uncertainty.", ["prevent", "uncertain"], _PREV_BANK, "Prevention, then uncertainty."),
        _TB_PICK("difficult", "prev_not", "Select the two items that do not belong.", ["spy_vape", "ignore_data"], _PREV_BANK, 2, "No device lists; do not ignore mortality data."),
    ],
}

eursc_science_tobacco, eursc_science_tobacco_variants = _bind("tobacco", _TB_POOLS)
