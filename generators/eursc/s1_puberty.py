"""S1 Unit 1.4 Puberty — 1.4.1–1.4.3.

Clinical, third-person banks. No prompts that ask a pupil to disclose
health, sexuality, relationships or experiences.
"""
from generators.eursc.science_shared import organ_labels
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
                "Use clinical lesson ideas. The quiz never asks for personal disclosure.",
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
                "Answer with the science, not with anyone's private story.",
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
        _PM_MCQ("foundational", "phys", "A typical physical change at puberty is", _mcq_opts("the skeleton turning into helium", "growth and new body hair for many young people", "mass becoming zero", "air becoming a hormone"), "B", "Physical changes are general patterns, not a classroom inspection."),
        _PM_MCQ("foundational", "feel", "Emotional changes at puberty", _mcq_opts("never happen", "can include stronger moods; this is discussed in third person, not as a confession", "must be ranked in class", "are measured in newtons"), "B", "Feelings can change; the quiz does not collect them."),
        _PM_MCQ("foundational", "hormone", "Hormones in this lesson are", _mcq_opts("rumours", "chemical messengers that help trigger puberty changes", "bones", "banned sports drinks only"), "B", "Hormones travel in the blood."),
        _PM_MCQ("foundational", "vary", "The age when puberty starts", _mcq_opts("is identical for every person on Earth", "varies; starting earlier or later than a friend can still be healthy", "must be announced to the class", "is set by kit colour"), "B", "Variation is normal."),
        _PM_MCQ("foundational", "not_ask", "This lesson must not", _mcq_opts("name hormones", "ask a pupil to describe their own puberty or private body", "use third-person examples", "mention that timing varies"), "B", "No personal disclosure."),
        _PM_MCQ("foundational", "help", "If a fictional character is worried about puberty timing, a scientific classroom response is", _mcq_opts("diagnose them in the quiz comments", "suggest a teacher or qualified health professional, not a pupil survey", "rank the class", "ignore science"), "B", "Signpost care."),
        _PM_KEY("foundational", "hormone_word", "Write the word for a chemical messenger in the blood that helps control puberty.", "hormone", "Hormones are messengers."),
        _PM_ORD("foundational", "talk", "Order a physical-change idea, then an emotional-change idea.", ["physical", "emotional"], _CHANGE_BANK, "Both can happen. Confession quizzes do not."),
        _PM_PICK("foundational", "ok_change", "Select the two puberty ideas that belong in science class.", ["physical", "emotional"], _CHANGE_BANK, 2, "General changes. Not ranking or confession."),
        _PM_PICK("foundational", "horm_ok", "Select the two hormone and timing facts.", ["messenger", "vary"], _HORMONE_BANK, 2, "Messengers and variation. Not a single calendar day."),
    ],
    "intermediate": [
        _PM_MCQ("intermediate", "both", "Sam and Lee are the same age. Sam has a deeper voice; Lee does not yet. Science says", _mcq_opts("Lee has failed", "timing varies; neither person should be mocked", "the class should vote", "hormones are rumours"), "B", "Variation is expected."),
        _PM_MCQ("intermediate", "brain", "Mood changes at puberty are linked with", _mcq_opts("kit colour", "brain and hormone changes as well as social life; still not a reason to collect private diaries", "the newton", "buoyancy"), "B", "Biology plus life context; no diary harvest."),
        _PM_MCQ("intermediate", "mature", "Sexual maturity in this syllabus means", _mcq_opts("being famous", "the body becoming able to produce mature gametes, at a time that varies", "winning a race", "a forced classroom announcement"), "B", "Biological capability, not a public identity test."),
        _PM_MCQ("intermediate", "compare", "Comparing who 'looks older' in class is", _mcq_opts("required practical work", "not a scientific method and can be unkind", "how hormones are measured", "an SI unit"), "B", "No body ranking."),
        _PM_MCQ("intermediate", "blood", "Hormones travel mainly in the", _mcq_opts("skeleton only", "blood", "distance–time graph", "friction pad"), "B", "Blood-borne messengers."),
        _PM_MCQ("intermediate", "signpost", "Personal medical questions about puberty belong with", _mcq_opts("a public leaderboard", "a teacher or health professional, not this app's answer box", "a sports slogan", "a force pair"), "B", "Signpost, do not store health stories."),
        _PM_KEY("intermediate", "puberty_word", "Write the word for the stage when a child's body changes toward adult sexual maturity.", "puberty", "Puberty is that stage."),
        _PM_NUM("intermediate", "ages", "A textbook says puberty often starts somewhere in a span of about 5 years for many people. How many years is that span?", 5, "The point is a range, not one day."),
        _PM_ORD("intermediate", "horm_then", "Order hormone messenger, then variation in timing.", ["messenger", "vary"], _HORMONE_BANK, "Messengers, then variation."),
        _PM_PICK("intermediate", "not_class", "Select the two actions that do not belong in this lesson.", ["confess", "rank"], _CHANGE_BANK, 2, "No confession, no ranking."),
    ],
    "difficult": [
        _PM_MCQ("difficult", "not_fail", "A person who starts puberty later than classmates", _mcq_opts("has failed science", "may still be within a normal range; worry is for a professional, not a quiz", "must publish a timeline", "has no hormones ever"), "B", "Ranges, then signpost."),
        _PM_MCQ("difficult", "media", "Media images of 'ideal' teenage bodies", _mcq_opts("are controlled scientific samples", "are not a measurement of healthy puberty", "replace hormones", "are SI units"), "B", "Images are not clinical data."),
        _PM_MCQ("difficult", "emotion_ok", "It is scientific to say moods can change at puberty. It is not scientific to", _mcq_opts("name hormones", "require pupils to submit private feelings as homework to this site", "use a fictional example", "mention variation"), "B", "No special-category mood files."),
        _PM_MCQ("difficult", "gamete_ready", "Producing mature sperm or eggs is part of", _mcq_opts("a distance–time graph", "sexual maturity, which arrives at different ages", "friction", "buoyancy"), "B", "Link to 1.4.2 without asking who has started."),
        _PM_MCQ("difficult", "help2", "Alex in a scenario wants private advice about body changes. The lesson answer is", _mcq_opts("post it for the class", "talk to a trusted adult or health professional; the quiz will not store that story", "rank Alex", "ignore all adults"), "B", "Signpost."),
        _PM_KEY("difficult", "variation_word", "Write the word for differences in timing that are still normal (one word: variation).", "variation", "Timing varies."),
        _PM_NUM("difficult", "two_people", "Two fictional classmates are compared only by age in years: 12 and 14. What is the difference in years?", 2, "Age difference is not a puberty score."),
        _PM_ORD("difficult", "phys_em", "Order physical then emotional as two lesson strands.", ["physical", "emotional"], _CHANGE_BANK, "Both strands; no ranking."),
        _PM_PICK("difficult", "keep_h", "Select the two scientific hormone ideas.", ["messenger", "vary"], _HORMONE_BANK, 2, "Messengers and variation."),
        _PM_PICK("difficult", "reject", "Select the two unscientific timing claims.", ["same_day", "fame"], _HORMONE_BANK, 2, "Not one calendar day and not celebrity as the standard."),
    ],
}

eursc_science_puberty_maturity, eursc_science_puberty_maturity_variants = _bind(
    "puberty_maturity", _PM_POOLS
)


_RA_POOLS = {
    "foundational": [
        _RA_MCQ("foundational", "egg", "The female gamete is the", _mcq_opts("sperm", "egg (ovum)", "femur", "newton"), "B", "Egg is the female gamete."),
        _RA_MCQ("foundational", "sperm", "The male gamete is the", _mcq_opts("egg", "sperm", "uterus", "joint"), "B", "Sperm is the male gamete."),
        _RA_MCQ("foundational", "uterus", "The uterus is", _mcq_opts("a bone in the arm", "the organ where a fetus can develop", "a lung", "a unit of speed"), "B", "Uterus is the womb."),
        _RA_MCQ("foundational", "ovary", "An ovary's job in this lesson is to", _mcq_opts("pump blood like the heart", "release eggs and make some hormones", "store urine only", "measure pulse"), "B", "Ovaries produce eggs."),
        _RA_MCQ("foundational", "testis", "A testis can", _mcq_opts("release eggs", "produce sperm", "be a distance–time graph", "replace the kidney as the only urinary organ"), "B", "Testes produce sperm."),
        _RA_MCQ("foundational", "fig", "<p>Which letter labels the uterus on this educational schematic?</p>" + str(organ_labels()), _mcq_opts("A", "B", "C", "none"), "B", "B is uterus. Schematic boxes only."),
        _RA_KEY("foundational", "gamete_word", "Write the word for a sex cell such as an egg or a sperm.", "gamete", "Gametes are sex cells."),
        _RA_ORD("foundational", "cycle", "Order lining thickens, then ovulation, then a period if no fertilisation.", ["lining", "ovulation", "period"], _CYCLE_BANK, "Do not collect who has periods."),
        _RA_PICK("foundational", "gametes", "Select the two genuine gametes.", ["egg", "sperm"], _GAMETE_BANK, 2, "Egg and sperm. Bones and rumours are not gametes."),
        _RA_PICK("foundational", "organs", "Select the two organs that belong in this reproductive list.", ["ovary", "uterus"], _ORGAN_BANK, 2, "Ovary and uterus."),
    ],
    "intermediate": [
        _RA_MCQ("intermediate", "urinary", "The urethra can carry urine. In males it can also carry sperm at ejaculation. This means", _mcq_opts("urine and gametes are the same substance", "reproductive and urinary structures can share a pathway in males", "females have no urinary system", "science forbids the word urine"), "B", "Shared pathway in males; still two jobs."),
        _RA_MCQ("intermediate", "fert", "Fertilisation is", _mcq_opts("a muscle pair", "the joining of egg and sperm", "a pulse measurement", "a banned drug"), "B", "Gametes join."),
        _RA_MCQ("intermediate", "oviduct", "After release, an egg typically travels in the", _mcq_opts("femur", "oviduct (Fallopian tube) toward the uterus", "trachea", "aorta as a red blood cell"), "B", "Oviduct to uterus."),
        _RA_MCQ("intermediate", "sperm_from", "Sperm are produced in the", _mcq_opts("ovaries", "testes", "alveoli", "knees"), "B", "Testes."),
        _RA_MCQ("intermediate", "cycle_point", "The menstrual cycle is", _mcq_opts("a one-off event that never repeats", "a repeating sequence involving hormones, ovulation and the uterus lining", "a sports tournament", "a graph of speed"), "B", "A cycle."),
        _RA_MCQ("intermediate", "fig_ovary", "<p>Which letter is an ovary?</p>" + str(organ_labels(title="A ovary")), _mcq_opts("B", "A", "C", "the word testis"), "B", "A is ovary."),
        _RA_KEY("intermediate", "uterus_word", "Write the word for the organ where a fetus can develop.", "uterus", "The uterus."),
        _RA_NUM("intermediate", "gamete_n", "How many types of human gamete does this lesson name (egg and sperm)?", 2, "Two types."),
        _RA_ORD("intermediate", "org_ord", "Order ovary, then uterus, as egg path ideas.", ["ovary", "uterus"], _ORGAN_BANK, "Egg from ovary toward uterus."),
        _RA_PICK("intermediate", "not_gamete", "Select the two items that are not gametes.", ["bone", "rumour"], _GAMETE_BANK, 2, "Bone cells and rumours are not gametes."),
    ],
    "difficult": [
        _RA_MCQ("difficult", "implants", "If fertilisation happens, the early embryo can implant in the", _mcq_opts("femur", "uterus lining", "alveolus", "tendon"), "B", "Implantation in the uterus."),
        _RA_MCQ("difficult", "period_why", "A period happens when", _mcq_opts("the person failed a test", "the uterus lining is shed after an egg was not fertilised", "sperm become eggs", "the heart stops"), "B", "Unfertilised cycle."),
        _RA_MCQ("difficult", "not_survey", "Teaching the menstrual cycle must not become", _mcq_opts("a labelled diagram", "a survey of who in the room has periods", "a hormone name", "a third-person timeline"), "B", "No period roll-call."),
        _RA_MCQ("difficult", "penis", "The penis can deliver sperm into the vagina. This is", _mcq_opts("a rumour with no anatomy", "clinical reproductive anatomy, not a prompt for personal stories", "a force in newtons only", "unrelated to fertilisation"), "B", "Clinical language; no confession."),
        _RA_MCQ("difficult", "fig_testis", "<p>Which letter is a testis?</p>" + str(organ_labels(title="C testis")), _mcq_opts("A", "C", "B", "ovary"), "B", "C is testis."),
        _RA_KEY("difficult", "sperm_word", "Write the word for the male gamete.", "sperm", "Sperm."),
        _RA_NUM("difficult", "one_egg", "In a simple S1 model, ovulation releases how many eggs in a typical cycle?", 1, "Usually one egg per cycle in the simple model."),
        _RA_ORD("difficult", "cycle2", "Order ovulation then period in an unfertilised cycle.", ["ovulation", "period"], _CYCLE_BANK, "Egg release, then lining shed if no fertilisation."),
        _RA_PICK("difficult", "three_org", "Select the three reproductive organs on the schematic list.", ["ovary", "uterus", "testis"], _ORGAN_BANK, 3, "Femur is a bone, not a gamete organ."),
        _RA_PICK("difficult", "keep_g", "Select the two gametes.", ["egg", "sperm"], _GAMETE_BANK, 2, "Egg and sperm."),
    ],
}

eursc_science_reproductive_anatomy, eursc_science_reproductive_anatomy_variants = _bind(
    "reproductive_anatomy", _RA_POOLS
)


_PS_POOLS = {
    "foundational": [
        _PS_MCQ("foundational", "sex", "Sexual intercourse can allow sperm to", _mcq_opts("turn into bone instantly", "enter the vagina and swim toward an egg", "become nitrogen in air", "measure speed"), "B", "Clinical mechanism, not a personal question."),
        _PS_MCQ("foundational", "preg", "Pregnancy in this lesson means", _mcq_opts("winning a match", "development after fertilisation, usually in the uterus", "a pulse of 80", "a friction force"), "B", "Development after fertilisation."),
        _PS_MCQ("foundational", "contra", "Contraception is", _mcq_opts("a type of joint", "a set of methods that can reduce the chance of pregnancy", "a requirement to disclose personal use in this quiz", "a banned sports drug by definition"), "B", "Knowledge of methods; no 'which do you use'."),
        _PS_MCQ("foundational", "sti", "An STI is", _mcq_opts("a distance–time slope", "an infection that can spread through sexual contact", "a hormone that is always harmless", "a muscle pair"), "B", "Sexually transmitted infection."),
        _PS_MCQ("foundational", "consent", "Consent means", _mcq_opts("silence after someone looks famous", "a clear, voluntary agreement that can be withdrawn", "the other person already started so it is too late", "a teacher collecting relationship lists"), "B", "Yes can be withdrawn."),
        _PS_MCQ("foundational", "orient", "Sexual orientation in this syllabus is the idea that", _mcq_opts("everyone must announce theirs in the quiz", "people can be attracted to different sexes; the lesson does not ask which applies to a pupil", "orientation is a newton", "science forbids the topic"), "B", "Fact without disclosure."),
        _PS_KEY("foundational", "consent_word", "Write the word for a clear voluntary yes that can be taken back.", "consent", "Consent can be withdrawn."),
        _PS_ORD("foundational", "preg_ord", "Order fertilisation, then fetal development, then birth.", ["fertilise", "develop", "birth"], _PREG_BANK, "Join, develop, birth. No personal sexual history."),
        _PS_PICK("foundational", "health_ok", "Select the two sexual-health ideas.", ["contraception", "sti"], _HEALTH_BANK, 2, "Contraception and STIs. Pressure-after-no is wrong."),
        _PS_PICK("foundational", "preg_ok", "Select the two pregnancy science steps.", ["fertilise", "develop"], _PREG_BANK, 2, "Fertilisation and development."),
    ],
    "intermediate": [
        _PS_MCQ("intermediate", "fetus", "A fetus is", _mcq_opts("a type of joint", "the developing offspring in the uterus after the early embryo stage", "exhaled carbon dioxide", "a sports slogan"), "B", "S1 wording: developing in the uterus."),
        _PS_MCQ("intermediate", "birth", "Birth is usually", _mcq_opts("the fetus remaining in the ovary forever", "the baby leaving the uterus, often through the vagina", "a pulse measurement", "unrelated to pregnancy"), "B", "Clinical, not graphic."),
        _PS_MCQ("intermediate", "condom", "A condom is discussed here as", _mcq_opts("a way to rank classmates", "a barrier method that can reduce pregnancy chance and some STI risk", "proof that consent is optional", "an SI unit"), "B", "Barrier method knowledge."),
        _PS_MCQ("intermediate", "test", "If a scenario character might have an STI, the scientific next step is", _mcq_opts("post symptoms on a leaderboard", "qualified health advice and testing; this app does not diagnose", "ignore all infections", "ask the whole class who has had sex"), "B", "Signpost health care."),
        _PS_MCQ("intermediate", "media", "Media can show unrealistic sex or relationships. A scientific habit is to", _mcq_opts("copy any video as evidence", "compare claims with curriculum facts and consent rules", "collect pupils' viewing lists in the quiz", "ban all science"), "B", "Critique media; no viewing-history harvest."),
        _PS_MCQ("intermediate", "no", "Jordan hears 'no' and continues. That is", _mcq_opts("fine if Jordan is popular", "not consent", "a hormone", "a buoyancy effect"), "B", "No means no."),
        _PS_KEY("intermediate", "contraception_word", "Write the word for methods that can reduce the chance of pregnancy.", "contraception", "Contraception."),
        _PS_NUM("intermediate", "two_people", "Consent needs how many people to agree in a two-person scenario?", 2, "Both must agree."),
        _PS_ORD("intermediate", "health_ord", "Order contraception knowledge, then STI knowledge.", ["contraception", "sti"], _HEALTH_BANK, "Pregnancy risk and infection risk are both taught."),
        _PS_PICK("intermediate", "not_disclose", "Select the two items that must not happen in this quiz.", ["disclose_sex", "pressure"], (
            {"id": "disclose_sex", "text": "Pupils must describe their own sexual experience"},
            {"id": "pressure", "text": "Pressuring someone after they say no is still allowed if they are famous"},
            {"id": "fertilise", "text": "Fertilisation is egg and sperm joining"},
            {"id": "consent", "text": "Consent means a clear, voluntary yes that can be withdrawn"},
        ), 2, "No disclosure and no 'fame overrides no'."),
    ],
    "difficult": [
        _PS_MCQ("difficult", "identity", "Gender identity and sexual orientation", _mcq_opts("must be declared in every science answer box", "can differ between people; classwork uses general facts, never a roll-call", "are newtons", "are banned from European School science"), "B", "Curriculum-faithful and non-inquisitive."),
        _PS_MCQ("difficult", "comm", "Healthy communication in a relationship includes", _mcq_opts("ignoring a withdrawn yes", "listening and respecting a no, in third-person scenarios", "forcing a public confession in class", "collecting partner names in this app"), "B", "Communication and consent."),
        _PS_MCQ("difficult", "limit", "Contraception can fail. That is why", _mcq_opts("science never mentions it", "methods reduce chance; they are not a magic shield, and personal choices belong with qualified advice", "STIs cannot exist", "consent is optional"), "B", "Reduce chance, not certainty; signpost."),
        _PS_MCQ("difficult", "preg_help", "A fictional character is pregnant and scared. The classroom answer is", _mcq_opts("diagnose and treat in the quiz", "a trusted adult or health professional; do not harvest private stories here", "a sports ranking", "to post online for fame"), "B", "Signpost."),
        _PS_MCQ("difficult", "sti2", "Some STIs can be present with few symptoms. That is why", _mcq_opts("testing is never useful", "qualified testing matters; the lesson does not ask who has been tested", "air is an STI", "joints cause pregnancy"), "B", "Asymptomatic possibility; no test-history survey."),
        _PS_KEY("difficult", "fertilisation_word", "Write the word for egg and sperm joining.", "fertilisation", "Fertilisation."),
        _PS_NUM("difficult", "withdraw", "A person said yes, then said no. How many of those statements is the current decision?", 1, "The later no is the current decision."),
        _PS_ORD("difficult", "full_p", "Order fertilisation, development, then birth.", ["fertilise", "develop", "birth"], _PREG_BANK, "The pregnancy sequence."),
        _PS_PICK("difficult", "three_h", "Select the three healthy decision ideas.", ["contraception", "sti", "consent"], _HEALTH_BANK, 3, "Not 'fame overrides no'."),
        _PS_PICK("difficult", "keep_p", "Select the two pregnancy science ideas.", ["fertilise", "birth"], _PREG_BANK, 2, "Join and birth. Disclosure is not science here."),
    ],
}

eursc_science_pregnancy_sexual_health, eursc_science_pregnancy_sexual_health_variants = _bind(
    "pregnancy_sexual_health", _PS_POOLS
)
