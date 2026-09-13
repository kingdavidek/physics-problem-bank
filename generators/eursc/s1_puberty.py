"""S1 Unit 1.4 Puberty — 1.4.1–1.4.3.

Clinical, third-person banks. No prompts that ask a pupil to disclose
health, sexuality, relationships or experiences.
"""
from generators.eursc.s1_unit14_puberty_advanced import (
    PREGNANCY_SEXUAL_HEALTH_MS_POOLS,
    PREGNANCY_SEXUAL_HEALTH_SMS_POOLS,
    PUBERTY_MATURITY_MS_POOLS,
    PUBERTY_MATURITY_SMS_POOLS,
    REPRODUCTIVE_ANATOMY_MS_POOLS,
)
from generators.eursc.science_shared import bind_eursc_topic, organ_labels
from generators.shared.utils import (
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE

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


_PM_MCQ, _PM_NUM, _PM_KEY, _PM_ORD, _PM_PICK = _topic_bank("puberty_maturity")
_RA_MCQ, _RA_NUM, _RA_KEY, _RA_ORD, _RA_PICK = _topic_bank("reproductive_anatomy")
_PS_MCQ, _PS_NUM, _PS_KEY, _PS_ORD, _PS_PICK = _topic_bank("pregnancy_sexual_health")

_CHANGE_BANK = (
    {"id": "physical", "text": "Typical physical changes such as growth spurts and new hair"},
    {"id": "emotional", "text": "Typical mood and friendship changes for many teenagers"},
    {"id": "confess", "text": "A quiz that requires a pupil to describe their own body"},
    {"id": "rank", "text": "Ranking classmates by who looks more adult"},
)
_HORMONE_BANK = (
    {"id": "messenger", "text": "Hormones are chemical messengers in the blood"},
    {"id": "vary", "text": "The age when puberty starts varies and that is normal"},
    {"id": "same_day", "text": "Every person starts puberty on the same calendar day"},
    {"id": "fame", "text": "A celebrity's timeline is the scientific standard"},
)
_GAMETE_BANK = (
    {"id": "egg", "text": "An egg (ovum) is the female gamete"},
    {"id": "sperm", "text": "A sperm is the male gamete"},
    {"id": "bone", "text": "A bone cell is a gamete"},
    {"id": "rumour", "text": "A rumour on social media is a gamete"},
)
_CYCLE_BANK = (
    {"id": "lining", "text": "The uterus lining thickens"},
    {"id": "ovulation", "text": "An egg is released (ovulation)"},
    {"id": "period", "text": "If the egg is not fertilised, the lining is shed (a period)"},
    {"id": "quiz", "text": "The class must report who has started periods"},
)
_ORGAN_BANK = (
    {"id": "ovary", "text": "An ovary can release an egg"},
    {"id": "uterus", "text": "The uterus is where a fetus can develop"},
    {"id": "testis", "text": "A testis can produce sperm"},
    {"id": "femur", "text": "The femur is a gamete-making organ"},
)
_PREG_BANK = (
    {"id": "fertilise", "text": "Fertilisation is egg and sperm joining"},
    {"id": "develop", "text": "A fetus develops in the uterus"},
    {"id": "birth", "text": "Birth is the baby leaving the uterus"},
    {"id": "disclose_sex", "text": "Pupils must describe their own sexual experience"},
)
_HEALTH_BANK = (
    {"id": "contraception", "text": "Contraception can reduce the chance of pregnancy"},
    {"id": "sti", "text": "Some infections spread through sexual contact (STIs)"},
    {"id": "consent", "text": "Consent means a clear, voluntary yes that can be withdrawn"},
    {"id": "pressure", "text": "Pressuring someone after they say no is still allowed if they are famous"},
)


_PM_POOLS = {
    "foundational": [
        _PM_MCQ("foundational", "phys", "A typical physical change at puberty is", _mcq_opts("the skeleton turning into helium", "growth and new body hair for many young people", "mass becoming zero", "air becoming a hormone"), "B", "Physical changes are general patterns, not a classroom inspection.", "Look for everyday body changes that often appear as a child grows toward adulthood, not a science-fiction option."),
        _PM_MCQ("foundational", "feel", "Emotional changes at puberty", _mcq_opts("never happen", "can include stronger moods; this is discussed in third person, not as a confession", "must be ranked in class", "are measured in newtons"), "B", "Feelings can change; the quiz does not collect them.", "Moods can get stronger at this stage. Science describes that in general, and never as a class ranking or a force measurement."),
        _PM_MCQ("foundational", "hormone", "Hormones in this lesson are", _mcq_opts("rumours", "chemical messengers that help trigger puberty changes", "bones", "banned sports drinks only"), "B", "Hormones travel in the blood.", "They are chemicals that travel in the blood and carry messages that help trigger the changes of this stage."),
        _PM_MCQ("foundational", "vary", "The age when puberty starts", _mcq_opts("is identical for every person on Earth", "varies; starting earlier or later than a friend can still be healthy", "must be announced to the class", "is set by kit colour"), "B", "Variation is normal.", "Friends the same age do not all change on the same timetable, and that can still be healthy."),
        _PM_MCQ("foundational", "not_ask", "This lesson must not", _mcq_opts("name hormones", "ask a pupil to describe their own puberty or private body", "use third-person examples", "mention that timing varies"), "B", "No personal disclosure.", "Science class can name facts. It must not collect private details about a pupil."),
        _PM_MCQ("foundational", "help", "If a fictional character is worried about puberty timing, a scientific classroom response is", _mcq_opts("diagnose them in the quiz comments", "suggest a teacher or qualified health professional, not a pupil survey", "rank the class", "ignore science"), "B", "Signpost care.", "Worry about timing belongs with a trusted adult who can give proper advice, not with a class vote or a quiz diagnosis."),
        _PM_KEY("foundational", "hormone_word", "Write the word for a chemical messenger in the blood that helps control puberty.", "hormone", "Hormones are messengers.", "Think of a chemical that travels in the blood and carries a message to organs, helping growth and other changes at this stage of life."),
        _PM_NUM("foundational", "chart100", "A public textbook chart of 100 fictional young people marks 40 as having started a typical physical change. How many of those 100 have not yet started, on this chart?", 60, "100 - 40 = 60. Aggregate chart only, not a class survey.", "The chart is about 100 fictional people. Forty have started the change. Subtract to find how many of the 100 have not yet started."),
        _PM_ORD("foundational", "talk", "Order a physical-change idea, then an emotional-change idea.", ["physical", "emotional"], _CHANGE_BANK, "Both can happen. Confession quizzes do not.", "Put a typical body-change idea first, then a typical mood-or-friendship-change idea. Skip anything that inspects a pupil."),
        _PM_PICK("foundational", "ok_change", "Select the two puberty ideas that belong in science class.", ["physical", "emotional"], _CHANGE_BANK, 2, "General changes. Not ranking or confession.", "Choose the two general patterns science can discuss. Skip ranking classmates or asking someone to describe themselves."),
        _PM_PICK("foundational", "horm_ok", "Select the two hormone and timing facts.", ["messenger", "vary"], _HORMONE_BANK, 2, "Messengers and variation. Not a single calendar day.", "Choose the blood-messenger idea and the idea that start age is not the same for everyone."),
    ],
    "intermediate": [
        _PM_MCQ("intermediate", "both", "Sam and Lee are the same age. Sam has a deeper voice; Lee does not yet. Science says", _mcq_opts("Lee has failed", "timing varies; neither person should be mocked", "the class should vote", "hormones are rumours"), "B", "Variation is expected.", "Two people of the same age can be at different points in this stage. That is expected, not a contest."),
        _PM_MCQ("intermediate", "brain", "Mood changes at puberty are linked with", _mcq_opts("kit colour", "brain and hormone changes as well as social life; still not a reason to collect private diaries", "the newton", "buoyancy"), "B", "Biology plus life context; no diary harvest.", "Moods can link to chemicals in the blood, the brain, and everyday life. That is still not a reason to collect private diaries."),
        _PM_MCQ("intermediate", "mature", "Sexual maturity in this syllabus means", _mcq_opts("being famous", "the body becoming able to produce mature gametes, at a time that varies", "winning a race", "a forced classroom announcement"), "B", "Biological capability, not a public identity test.", "This phrase is about whether the body can make mature sex cells, at a time that differs between people."),
        _PM_MCQ("intermediate", "compare", "Comparing who 'looks older' in class is", _mcq_opts("required practical work", "not a scientific method and can be unkind", "how hormones are measured", "an SI unit"), "B", "No body ranking.", "Looking older is not a measurement. Science does not rank classmates by appearance."),
        _PM_MCQ("intermediate", "blood", "Hormones travel mainly in the", _mcq_opts("skeleton only", "blood", "distance–time graph", "friction pad"), "B", "Blood-borne messengers.", "These chemical messengers need a transport system that circulates around the body."),
        _PM_MCQ("intermediate", "signpost", "Personal medical questions about puberty belong with", _mcq_opts("a public leaderboard", "a teacher or health professional, not this app's answer box", "a sports slogan", "a force pair"), "B", "Signpost, do not store health stories.", "A personal medical worry belongs with a trusted adult or health professional, not a public scoreboard."),
        _PM_KEY("intermediate", "puberty_word", "Write the word for the stage when a child's body changes toward adult sexual maturity.", "puberty", "Puberty is that stage.", "One word names that growing-up stage itself, not the chemical messengers and not the sex cells."),
        _PM_NUM("intermediate", "ages", "A textbook says puberty often starts somewhere in a span of about 5 years for many people. How many years is that span?", 5, "The point is a range, not one day.", "The textbook already gives the length of the span in years. Copy that number — the point is a range, not one birthday."),
        _PM_ORD("intermediate", "horm_then", "Order hormone messenger, then variation in timing.", ["messenger", "vary"], _HORMONE_BANK, "Messengers, then variation.", "First the idea of a chemical messenger in the blood, then the idea that start age differs."),
        _PM_PICK("intermediate", "not_class", "Select the two actions that do not belong in this lesson.", ["confess", "rank"], _CHANGE_BANK, 2, "No confession, no ranking.", "Choose the two actions that would turn the lesson into a private confession or a ranking of who looks more adult."),
    ],
    "difficult": [
        _PM_MCQ("difficult", "not_fail", "A person who starts puberty later than classmates", _mcq_opts("has failed science", "may still be within a normal range; worry is for a professional, not a quiz", "must publish a timeline", "has no hormones ever"), "B", "Ranges, then signpost.", "Starting later than friends can still be within a normal range. Worry belongs with a professional, not a quiz score."),
        _PM_MCQ("difficult", "media", "Media images of 'ideal' teenage bodies", _mcq_opts("are controlled scientific samples", "are not a measurement of healthy puberty", "replace hormones", "are SI units"), "B", "Images are not clinical data.", "Photos of an 'ideal' teenager are advertising or media, not a scientific sample of healthy change."),
        _PM_MCQ("difficult", "emotion_ok", "It is scientific to say moods can change at puberty. It is not scientific to", _mcq_opts("name hormones", "require pupils to submit private feelings as homework to this site", "use a fictional example", "mention variation"), "B", "No special-category mood files.", "Naming a general pattern is science. Demanding private feelings as homework is not."),
        _PM_MCQ("difficult", "gamete_ready", "Producing mature sperm or eggs is part of", _mcq_opts("a distance–time graph", "sexual maturity, which arrives at different ages", "friction", "buoyancy"), "B", "Link to 1.4.2 without asking who has started.", "Making mature sex cells is part of becoming sexually mature, and that happens at different ages."),
        _PM_MCQ("difficult", "help2", "Alex in a scenario wants private advice about body changes. The lesson answer is", _mcq_opts("post it for the class", "talk to a trusted adult or health professional; the quiz will not store that story", "rank Alex", "ignore all adults"), "B", "Signpost.", "Private worries about changing go to a trusted adult or health professional. This quiz will not store that story."),
        _PM_KEY("difficult", "variation_word", "Write the word for differences in timing that are still normal (one word: variation).", "variation", "Timing varies.", "One word meaning 'not all the same', used here for different start times that can still be healthy."),
        _PM_NUM("difficult", "two_people", "Two fictional classmates are compared only by age in years: 12 and 14. What is the difference in years?", 2, "Age difference is not a puberty score.", "Subtract the two ages. The result is only an age gap, not a score for this stage of life."),
        _PM_ORD("difficult", "phys_em", "Order physical then emotional as two lesson strands.", ["physical", "emotional"], _CHANGE_BANK, "Both strands; no ranking.", "First a typical physical-change idea, then a typical emotional-change idea. Skip ranking or confession."),
        _PM_PICK("difficult", "keep_h", "Select the two scientific hormone ideas.", ["messenger", "vary"], _HORMONE_BANK, 2, "Messengers and variation.", "Choose the messenger-in-the-blood idea and the idea that start age differs."),
        _PM_PICK("difficult", "reject", "Select the two unscientific timing claims.", ["same_day", "fame"], _HORMONE_BANK, 2, "Not one calendar day and not celebrity as the standard.", "Choose the two claims that pretend everyone starts on one calendar day or that a celebrity sets the science."),
    ],
}

_PM_STANDARD = {
    "foundational": (
        'puberty_maturity_foundational_mcq_hormone',
        'puberty_maturity_foundational_keyword_hormone_word',
        'puberty_maturity_foundational_number_chart100',
        'puberty_maturity_foundational_order_talk',
        'puberty_maturity_foundational_pick_horm_ok',
    ),
    "intermediate": (
        'puberty_maturity_intermediate_mcq_blood',
        'puberty_maturity_intermediate_keyword_puberty_word',
        'puberty_maturity_intermediate_number_ages',
        'puberty_maturity_intermediate_order_horm_then',
        'puberty_maturity_intermediate_pick_not_class',
    ),
    "difficult": (
        'puberty_maturity_difficult_mcq_emotion_ok',
        'puberty_maturity_difficult_keyword_variation_word',
        'puberty_maturity_difficult_number_two_people',
        'puberty_maturity_difficult_order_phys_em',
        'puberty_maturity_difficult_pick_keep_h',
    ),
}
eursc_science_puberty_maturity, eursc_science_puberty_maturity_variants = bind_eursc_topic(
    "puberty_maturity",
    _PM_POOLS,
    _PM_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: PUBERTY_MATURITY_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: PUBERTY_MATURITY_SMS_POOLS,
    },
)


_RA_POOLS = {
    "foundational": [
        _RA_MCQ("foundational", "egg", "The female gamete is the", _mcq_opts("sperm", "egg (ovum)", "femur", "newton"), "B", "Egg is the female gamete.", "A gamete is a sex cell. Which one is made in the ovaries?"),
        _RA_MCQ("foundational", "sperm", "The male gamete is the", _mcq_opts("egg", "sperm", "uterus", "joint"), "B", "Sperm is the male gamete.", "A gamete is a sex cell. Which one is made in the testes?"),
        _RA_MCQ("foundational", "uterus", "The uterus is", _mcq_opts("a bone in the arm", "the organ where a fetus can develop", "a lung", "a unit of speed"), "B", "Uterus is the womb.", "This organ is the place where a fetus can grow. It is not a bone, a lung, or a unit."),
        _RA_MCQ("foundational", "ovary", "An ovary's job in this lesson is to", _mcq_opts("pump blood like the heart", "release eggs and make some hormones", "store urine only", "measure pulse"), "B", "Ovaries produce eggs.", "This organ releases eggs and also makes some chemical messengers. It is not the heart or the bladder."),
        _RA_MCQ("foundational", "testis", "A testis can", _mcq_opts("release eggs", "produce sperm", "be a distance–time graph", "replace the kidney as the only urinary organ"), "B", "Testes produce sperm.", "This organ produces the male sex cells. It does not release eggs."),
        _RA_MCQ("foundational", "fig", "<p>Which letter labels the uterus on this educational schematic?</p>" + str(organ_labels()), _mcq_opts("A", "B", "C", "none"), "B", "B is uterus. Schematic boxes only.", "Match the letter on the schematic to the organ where a fetus can develop."),
        _RA_KEY("foundational", "gamete_word", "Write the word for a sex cell such as an egg or a sperm.", "gamete", "Gametes are sex cells.", "One scientific word names a sex cell. Egg and sperm are both examples of that kind of cell."),
        _RA_NUM("foundational", "two_gametes", "This lesson names egg and sperm. How many types of human gamete is that?", 2, "Two types. The question is about the model, not anyone's body.", "Egg is one type and sperm is the other. Count how many types that is."),
        _RA_ORD("foundational", "cycle", "Order lining thickens, then ovulation, then a period if no fertilisation.", ["lining", "ovulation", "period"], _CYCLE_BANK, "Do not collect who has periods.", "First the uterus lining builds up, then an egg is released, then the lining is shed if there is no fertilisation."),
        _RA_PICK("foundational", "gametes", "Select the two genuine gametes.", ["egg", "sperm"], _GAMETE_BANK, 2, "Egg and sperm. Bones and rumours are not gametes.", "Choose the two genuine sex cells. A bone cell and a rumour are not."),
        _RA_PICK("foundational", "organs", "Select the two organs that belong in this reproductive list.", ["ovary", "uterus"], _ORGAN_BANK, 2, "Ovary and uterus.", "Choose the organ that can release an egg and the organ where a fetus can develop."),
    ],
    "intermediate": [
        _RA_MCQ("intermediate", "urinary", "The urethra can carry urine. In males it can also carry sperm at ejaculation. This means", _mcq_opts("urine and gametes are the same substance", "reproductive and urinary structures can share a pathway in males", "females have no urinary system", "science forbids the word urine"), "B", "Shared pathway in males; still two jobs.", "One tube can have two jobs at different times. That does not make urine and sperm the same substance."),
        _RA_MCQ("intermediate", "fert", "Fertilisation is", _mcq_opts("a muscle pair", "the joining of egg and sperm", "a pulse measurement", "a banned drug"), "B", "Gametes join.", "This is the event when the two sex cells join."),
        _RA_MCQ("intermediate", "oviduct", "After release, an egg typically travels in the", _mcq_opts("femur", "oviduct (Fallopian tube) toward the uterus", "trachea", "aorta as a red blood cell"), "B", "Oviduct to uterus.", "After leaving the ovary, the egg travels along a tube toward the uterus, not through a bone or the windpipe."),
        _RA_MCQ("intermediate", "sperm_from", "Sperm are produced in the", _mcq_opts("ovaries", "testes", "alveoli", "knees"), "B", "Testes.", "Where are male sex cells made?"),
        _RA_MCQ("intermediate", "cycle_point", "The menstrual cycle is", _mcq_opts("a one-off event that never repeats", "a repeating sequence involving hormones, ovulation and the uterus lining", "a sports tournament", "a graph of speed"), "B", "A cycle.", "A cycle repeats. Look for a repeating sequence that includes chemical messengers, egg release, and the uterus lining."),
        _RA_MCQ("intermediate", "fig_ovary", "<p>Which letter is an ovary?</p>" + str(organ_labels(title="A ovary")), _mcq_opts("B", "A", "C", "the word testis"), "B", "A is ovary.", "Find the letter that marks the organ that releases eggs."),
        _RA_KEY("intermediate", "uterus_word", "Write the word for the organ where a fetus can develop.", "uterus", "The uterus.", "Name the organ often called the womb — the place a fetus can grow."),
        _RA_NUM("intermediate", "gamete_n", "How many types of human gamete does this lesson name (egg and sperm)?", 2, "Two types.", "Count the types named: egg and sperm."),
        _RA_ORD("intermediate", "org_ord", "Order ovary, then uterus, as egg path ideas.", ["ovary", "uterus"], _ORGAN_BANK, "Egg from ovary toward uterus.", "Start where the egg is released, then the organ where a fetus can develop."),
        _RA_PICK("intermediate", "not_gamete", "Select the two items that are not gametes.", ["bone", "rumour"], _GAMETE_BANK, 2, "Bone cells and rumours are not gametes.", "Choose the two items that are not sex cells."),
    ],
    "difficult": [
        _RA_MCQ("difficult", "implants", "If fertilisation happens, the early embryo can implant in the", _mcq_opts("femur", "uterus lining", "alveolus", "tendon"), "B", "Implantation in the uterus.", "After the sex cells join, the early embryo attaches to the lining of the organ where a fetus can grow."),
        _RA_MCQ("difficult", "period_why", "A period happens when", _mcq_opts("the person failed a test", "the uterus lining is shed after an egg was not fertilised", "sperm become eggs", "the heart stops"), "B", "Unfertilised cycle.", "If the egg is not fertilised, the built-up lining of the uterus is shed."),
        _RA_MCQ("difficult", "not_survey", "Teaching the menstrual cycle must not become", _mcq_opts("a labelled diagram", "a survey of who in the room has periods", "a hormone name", "a third-person timeline"), "B", "No period roll-call.", "A diagram and a sequence belong in class. A roll-call of who has started does not."),
        _RA_MCQ("difficult", "penis", "The penis can deliver sperm into the vagina. This is", _mcq_opts("a rumour with no anatomy", "clinical reproductive anatomy, not a prompt for personal stories", "a force in newtons only", "unrelated to fertilisation"), "B", "Clinical language; no confession.", "This is anatomy of how sperm can be delivered. It is not a prompt for personal stories."),
        _RA_MCQ("difficult", "fig_testis", "<p>Which letter is a testis?</p>" + str(organ_labels(title="C testis")), _mcq_opts("A", "C", "B", "ovary"), "B", "C is testis.", "Find the letter that marks the organ that produces sperm."),
        _RA_KEY("difficult", "sperm_word", "Write the word for the male gamete.", "sperm", "Sperm.", "Name the male sex cell, not the organ that makes it."),
        _RA_NUM("difficult", "one_egg", "In a simple S1 model, ovulation releases how many eggs in a typical cycle?", 1, "Usually one egg per cycle in the simple model.", "In this simple classroom model, a typical cycle releases one egg. That is the number to enter."),
        _RA_ORD("difficult", "cycle2", "Order ovulation then period in an unfertilised cycle.", ["ovulation", "period"], _CYCLE_BANK, "Egg release, then lining shed if no fertilisation.", "First the egg is released, then — if there is no fertilisation — the lining is shed."),
        _RA_PICK("difficult", "three_org", "Select the three reproductive organs on the schematic list.", ["ovary", "uterus", "testis"], _ORGAN_BANK, 3, "Femur is a bone, not a gamete organ.", "Choose the three reproductive organs. Skip the thigh bone."),
        _RA_PICK("difficult", "keep_g", "Select the two gametes.", ["egg", "sperm"], _GAMETE_BANK, 2, "Egg and sperm.", "Choose the female sex cell and the male sex cell."),
    ],
}

_RA_STANDARD = {
    "foundational": (
        'reproductive_anatomy_foundational_mcq_egg',
        'reproductive_anatomy_foundational_keyword_gamete_word',
        'reproductive_anatomy_foundational_number_two_gametes',
        'reproductive_anatomy_foundational_order_cycle',
        'reproductive_anatomy_foundational_pick_gametes',
    ),
    "intermediate": (
        'reproductive_anatomy_intermediate_mcq_cycle_point',
        'reproductive_anatomy_intermediate_keyword_uterus_word',
        'reproductive_anatomy_intermediate_number_gamete_n',
        'reproductive_anatomy_intermediate_order_org_ord',
        'reproductive_anatomy_intermediate_pick_not_gamete',
    ),
    "difficult": (
        'reproductive_anatomy_difficult_mcq_fig_testis',
        'reproductive_anatomy_difficult_keyword_sperm_word',
        'reproductive_anatomy_difficult_number_one_egg',
        'reproductive_anatomy_difficult_order_cycle2',
        'reproductive_anatomy_difficult_pick_keep_g',
    ),
}
eursc_science_reproductive_anatomy, eursc_science_reproductive_anatomy_variants = bind_eursc_topic(
    "reproductive_anatomy",
    _RA_POOLS,
    _RA_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: REPRODUCTIVE_ANATOMY_MS_POOLS,
    },
)


_PS_POOLS = {
    "foundational": [
        _PS_MCQ("foundational", "sex", "Sexual intercourse can allow sperm to", _mcq_opts("turn into bone instantly", "enter the vagina and swim toward an egg", "become nitrogen in air", "measure speed"), "B", "Clinical mechanism, not a personal question.", "Think about the path sperm can take toward an egg. This is a mechanism, not a personal question."),
        _PS_MCQ("foundational", "preg", "Pregnancy in this lesson means", _mcq_opts("winning a match", "development after fertilisation, usually in the uterus", "a pulse of 80", "a friction force"), "B", "Development after fertilisation.", "After the sex cells join, development usually continues in the uterus."),
        _PS_MCQ("foundational", "contra", "Contraception is", _mcq_opts("a type of joint", "a set of methods that can reduce the chance of pregnancy", "a requirement to disclose personal use in this quiz", "a banned sports drug by definition"), "B", "Knowledge of methods; no 'which do you use'.", "These are methods that can lower the chance of pregnancy. The quiz does not ask what anyone uses."),
        _PS_MCQ("foundational", "sti", "An STI is", _mcq_opts("a distance–time slope", "an infection that can spread through sexual contact", "a hormone that is always harmless", "a muscle pair"), "B", "Sexually transmitted infection.", "Some infections can spread through sexual contact."),
        _PS_MCQ("foundational", "consent", "Consent means", _mcq_opts("silence after someone looks famous", "a clear, voluntary agreement that can be withdrawn", "the other person already started so it is too late", "a teacher collecting relationship lists"), "B", "Yes can be withdrawn.", "A real yes is clear, freely given, and can be taken back."),
        _PS_MCQ("foundational", "orient", "Sexual orientation in this syllabus is the idea that", _mcq_opts("everyone must announce theirs in the quiz", "people can be attracted to different sexes; the lesson does not ask which applies to a pupil", "orientation is a newton", "science forbids the topic"), "B", "Fact without disclosure.", "People can be attracted to different sexes. The lesson states that as a fact, without asking which applies to a pupil."),
        _PS_KEY("foundational", "consent_word", "Write the word for a clear voluntary yes that can be taken back.", "consent", "Consent can be withdrawn.", "One word for agreeing freely — and being allowed to change that agreement."),
        _PS_NUM("foundational", "two_agree", "A public leaflet says consent in a two-person scenario needs both people to agree. How many people is that?", 2, "Both must agree. The item is about the rule, not a pupil's relationships.", "In a two-person situation, both people must agree. How many people is that?"),
        _PS_ORD("foundational", "preg_ord", "Order fertilisation, then fetal development, then birth.", ["fertilise", "develop", "birth"], _PREG_BANK, "Join, develop, birth. No personal sexual history.", "First the sex cells join, then the fetus develops, then the baby is born."),
        _PS_PICK("foundational", "health_ok", "Select the two sexual-health ideas.", ["contraception", "sti"], _HEALTH_BANK, 2, "Contraception and STIs. Pressure-after-no is wrong.", "Choose methods that can reduce pregnancy chance, and infections that can spread through sexual contact. Skip the claim that fame overrides a no."),
        _PS_PICK("foundational", "preg_ok", "Select the two pregnancy science steps.", ["fertilise", "develop"], _PREG_BANK, 2, "Fertilisation and development.", "Choose joining of the sex cells, then development of the fetus."),
    ],
    "intermediate": [
        _PS_MCQ("intermediate", "fetus", "A fetus is", _mcq_opts("a type of joint", "the developing offspring in the uterus after the early embryo stage", "exhaled carbon dioxide", "a sports slogan"), "B", "S1 wording: developing in the uterus.", "After the early embryo stage, this is the name for the offspring developing in the uterus."),
        _PS_MCQ("intermediate", "birth", "Birth is usually", _mcq_opts("the fetus remaining in the ovary forever", "the baby leaving the uterus, often through the vagina", "a pulse measurement", "unrelated to pregnancy"), "B", "Clinical, not graphic.", "The baby leaves the uterus, often through the vagina."),
        _PS_MCQ("intermediate", "condom", "A condom is discussed here as", _mcq_opts("a way to rank classmates", "a barrier method that can reduce pregnancy chance and some STI risk", "proof that consent is optional", "an SI unit"), "B", "Barrier method knowledge.", "A barrier method can lower pregnancy chance and some infection risk."),
        _PS_MCQ("intermediate", "test", "If a scenario character might have an STI, the scientific next step is", _mcq_opts("post symptoms on a leaderboard", "qualified health advice and testing; this app does not diagnose", "ignore all infections", "ask the whole class who has had sex"), "B", "Signpost health care.", "Possible infection needs qualified testing and advice — not a class leaderboard."),
        _PS_MCQ("intermediate", "media", "Media can show unrealistic sex or relationships. A scientific habit is to", _mcq_opts("copy any video as evidence", "compare claims with curriculum facts and consent rules", "collect pupils' viewing lists in the quiz", "ban all science"), "B", "Critique media; no viewing-history harvest.", "Check videos against curriculum facts and consent rules, rather than treating any clip as evidence."),
        _PS_MCQ("intermediate", "no", "Jordan hears 'no' and continues. That is", _mcq_opts("fine if Jordan is popular", "not consent", "a hormone", "a buoyancy effect"), "B", "No means no.", "If someone says no, continuing is not agreement."),
        _PS_KEY("intermediate", "contraception_word", "Write the word for methods that can reduce the chance of pregnancy.", "contraception", "Contraception.", "One group name for methods that can lower the chance of pregnancy."),
        _PS_NUM("intermediate", "two_people", "Consent needs how many people to agree in a two-person scenario?", 2, "Both must agree.", "Both people in a two-person scenario must agree. That is how many people?"),
        _PS_ORD("intermediate", "health_ord", "Order contraception knowledge, then STI knowledge.", ["contraception", "sti"], _HEALTH_BANK, "Pregnancy risk and infection risk are both taught.", "First methods that can reduce pregnancy chance, then infections that can spread through sexual contact."),
        _PS_PICK("intermediate", "not_disclose", "Select the two items that must not happen in this quiz.", ["disclose_sex", "pressure"], (
            {"id": "disclose_sex", "text": "Pupils must describe their own sexual experience"},
            {"id": "pressure", "text": "Pressuring someone after they say no is still allowed if they are famous"},
            {"id": "fertilise", "text": "Fertilisation is egg and sperm joining"},
            {"id": "consent", "text": "Consent means a clear, voluntary yes that can be withdrawn"},
        ), 2, "No disclosure and no 'fame overrides no'.", "Choose collecting a pupil's sexual history, and treating a no as optional because someone is famous."),
    ],
    "difficult": [
        _PS_MCQ("difficult", "identity", "Gender identity and sexual orientation", _mcq_opts("must be declared in every science answer box", "can differ between people; classwork uses general facts, never a roll-call", "are newtons", "are banned from European School science"), "B", "Curriculum-faithful and non-inquisitive.", "These ideas can differ between people. Classwork uses general facts, never a roll-call."),
        _PS_MCQ("difficult", "comm", "Healthy communication in a relationship includes", _mcq_opts("ignoring a withdrawn yes", "listening and respecting a no, in third-person scenarios", "forcing a public confession in class", "collecting partner names in this app"), "B", "Communication and consent.", "Healthy communication includes listening and respecting a no."),
        _PS_MCQ("difficult", "limit", "Contraception can fail. That is why", _mcq_opts("science never mentions it", "methods reduce chance; they are not a magic shield, and personal choices belong with qualified advice", "STIs cannot exist", "consent is optional"), "B", "Reduce chance, not certainty; signpost.", "Methods can fail, so they reduce chance rather than giving a magic shield."),
        _PS_MCQ("difficult", "preg_help", "A fictional character is pregnant and scared. The classroom answer is", _mcq_opts("diagnose and treat in the quiz", "a trusted adult or health professional; do not harvest private stories here", "a sports ranking", "to post online for fame"), "B", "Signpost.", "A scared fictional character needs a trusted adult or health professional, not a quiz diagnosis."),
        _PS_MCQ("difficult", "sti2", "Some STIs can be present with few symptoms. That is why", _mcq_opts("testing is never useful", "qualified testing matters; the lesson does not ask who has been tested", "air is an STI", "joints cause pregnancy"), "B", "Asymptomatic possibility; no test-history survey.", "Few symptoms does not mean there is no infection. Qualified testing still matters; the lesson does not ask who has been tested."),
        _PS_KEY("difficult", "fertilisation_word", "Write the word for egg and sperm joining.", "fertilisation", "Fertilisation.", "Name the event when the two sex cells join."),
        _PS_NUM("difficult", "withdraw", "A person said yes, then said no. How many of those statements is the current decision?", 1, "The later no is the current decision.", "Yes, then no. Only the later statement is the current decision. How many current decisions is that?"),
        _PS_ORD("difficult", "full_p", "Order fertilisation, development, then birth.", ["fertilise", "develop", "birth"], _PREG_BANK, "The pregnancy sequence.", "Join, then develop, then the baby is born."),
        _PS_PICK("difficult", "three_h", "Select the three healthy decision ideas.", ["contraception", "sti", "consent"], _HEALTH_BANK, 3, "Not 'fame overrides no'.", "Choose contraception, STI knowledge, and consent. Skip the claim that fame overrides a no."),
        _PS_PICK("difficult", "keep_p", "Select the two pregnancy science ideas.", ["fertilise", "birth"], _PREG_BANK, 2, "Join and birth. Disclosure is not science here.", "Choose joining of the sex cells and birth. A demand to describe personal experience is not pregnancy science."),
    ],
}

_PS_STANDARD = {
    "foundational": (
        'pregnancy_sexual_health_foundational_mcq_consent',
        'pregnancy_sexual_health_foundational_keyword_consent_word',
        'pregnancy_sexual_health_foundational_number_two_agree',
        'pregnancy_sexual_health_foundational_order_preg_ord',
        'pregnancy_sexual_health_foundational_pick_health_ok',
    ),
    "intermediate": (
        'pregnancy_sexual_health_intermediate_mcq_birth',
        'pregnancy_sexual_health_intermediate_keyword_contraception_word',
        'pregnancy_sexual_health_intermediate_number_two_people',
        'pregnancy_sexual_health_intermediate_order_health_ord',
        'pregnancy_sexual_health_intermediate_pick_not_disclose',
    ),
    "difficult": (
        'pregnancy_sexual_health_difficult_mcq_comm',
        'pregnancy_sexual_health_difficult_keyword_fertilisation_word',
        'pregnancy_sexual_health_difficult_number_withdraw',
        'pregnancy_sexual_health_difficult_order_full_p',
        'pregnancy_sexual_health_difficult_pick_keep_p',
    ),
}
eursc_science_pregnancy_sexual_health, eursc_science_pregnancy_sexual_health_variants = bind_eursc_topic(
    "pregnancy_sexual_health",
    _PS_POOLS,
    _PS_STANDARD,
    advanced_pools={
        MULTI_STEP_MODE: PREGNANCY_SEXUAL_HEALTH_MS_POOLS,
        SITUATIONAL_MULTI_STEP_MODE: PREGNANCY_SEXUAL_HEALTH_SMS_POOLS,
    },
)
