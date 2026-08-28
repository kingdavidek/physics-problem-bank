"""S2 Unit 2.3 Senses — 2.3.1–2.3.8."""
from generators.eursc.science_shared import canal_boxes, ear_boxes, eye_boxes
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
                "Use sense ideas from the lesson. This is not a personal body survey.",
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
                "Check the sense idea. Scenarios are fictional.",
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


_VI_MCQ, _VI_NUM, _VI_KEY, _VI_ORD, _VI_PICK = _topic_bank("vision")
_HE_MCQ, _HE_NUM, _HE_KEY, _HE_ORD, _HE_PICK = _topic_bank("hearing")
_TO_MCQ, _TO_NUM, _TO_KEY, _TO_ORD, _TO_PICK = _topic_bank("touch")
_SM_MCQ, _SM_NUM, _SM_KEY, _SM_ORD, _SM_PICK = _topic_bank("smell")
_TA_MCQ, _TA_NUM, _TA_KEY, _TA_ORD, _TA_PICK = _topic_bank("taste")
_PR_MCQ, _PR_NUM, _PR_KEY, _PR_ORD, _PR_PICK = _topic_bank("proprioception_balance")
_IN_MCQ, _IN_NUM, _IN_KEY, _IN_ORD, _IN_PICK = _topic_bank("interoception")
_NH_MCQ, _NH_NUM, _NH_KEY, _NH_ORD, _NH_PICK = _topic_bank("nonhuman_senses")

_EYE_BANK = (
    {"id": "lens", "text": "The lens refracts light to help form an image"},
    {"id": "retina", "text": "The retina detects the image"},
    {"id": "brain", "text": "Signals travel toward the brain for interpretation"},
    {"id": "rank_eye", "text": "The quiz should rank whose eyesight is best"},
)
_FOCUS_BANK = (
    {"id": "accom", "text": "Accommodation is changing lens shape for near or far"},
    {"id": "near", "text": "Near-sight in this model means distant objects are not in focus"},
    {"id": "vote_lens", "text": "Focus is voted by the class"},
    {"id": "spy_rx", "text": "The app should store whose glasses prescription it is"},
)
_STEREO_BANK = (
    {"id": "two", "text": "Two slightly different views help judge depth"},
    {"id": "illusion", "text": "An illusion can be the brain's interpretation of cues"},
    {"id": "one_enough", "text": "Stereo depth needs only one identical photo forever"},
    {"id": "test_class", "text": "Pupils must publish a private eye test score"},
)

_VI_POOLS = {
    "foundational": [
        _VI_MCQ("foundational", "lens", "In this schematic the lens mainly", _mcq_opts("stores a glasses file", "refracts light to help form an image", "is a food group", "ranks classmates"), "B", "Refraction by the lens."),
        _VI_MCQ("foundational", "retina", "The retina", _mcq_opts("is a unit of time", "detects the image at the back of the eye in this model", "is an advert", "must be photographed for the quiz"), "B", "Detector."),
        _VI_MCQ("foundational", "brain", "Signals from the eye", _mcq_opts("stay in the lens only", "travel toward the brain, which interprets them", "are a vaccination record", "are a sleep bar"), "B", "Interpretation in the brain."),
        _VI_MCQ("foundational", "accom", "Accommodation is", _mcq_opts("a class vote on posters", "changing lens shape so near or far can be in focus", "a demand for a prescription list", "an antibiotic"), "B", "Lens shape."),
        _VI_MCQ("foundational", "stereo", "Stereo depth uses", _mcq_opts("one identical view only, always", "two slightly different views from two eyes", "a rumour", "a private scoreboard"), "B", "Two views."),
        _VI_MCQ("foundational", "lens_letter", "<p>Which letter is the lens?</p>" + str(eye_boxes(title="Lens letter")), _mcq_opts("B", "A", "C", "a pupil name"), "B", "A is the lens."),
        _VI_KEY("foundational", "lens_word", "Write the word for the part that refracts light to help form an image.", "lens", "Lens."),
        _VI_NUM("foundational", "eyes2", "How many eyes are used for stereo depth in this lesson's usual model?", 2, "Two eyes."),
        _VI_ORD("foundational", "path", "Order lens, then retina, then path toward the brain.", ["lens", "retina", "brain"], _EYE_BANK, "Optics, detector, interpretation."),
        _VI_PICK("foundational", "eye_ok", "Select lens and retina.", ["lens", "retina"], _EYE_BANK, 2, "Two parts. No ranking."),
    ],
    "intermediate": [
        _VI_MCQ("intermediate", "near", "Near-sight in this S2 model means", _mcq_opts("near objects cannot be seen at all", "distant objects are not in focus", "the retina is a virus", "the quiz stores a prescription"), "B", "Far blur."),
        _VI_MCQ("intermediate", "far", "Far-sight in this model means", _mcq_opts("distant objects are the only possible image", "near objects are not in focus", "stereo is a food", "pupils must list glasses brands"), "B", "Near blur."),
        _VI_MCQ("intermediate", "alex", "Alex (fictional) squints at a board far away. A science comment is", _mcq_opts("demand Alex's prescription in the quiz", "that can fit a focusing error; the app does not store whose glasses they are", "rank Alex", "it cannot be optics"), "B", "Third person, no file."),
        _VI_MCQ("intermediate", "illusion", "A visual illusion is often", _mcq_opts("proof the instrument is always broken", "the brain interpreting cues in a way that mismatches the object", "a vaccination", "a class eye-test league"), "B", "Interpretation."),
        _VI_MCQ("intermediate", "not_rank", "This quiz", _mcq_opts("ranks whose eyesight is best", "does not rank eyesight and does not store prescriptions", "collects optician letters", "diagnoses Alex"), "B", "No ranking, no file."),
        _VI_MCQ("intermediate", "retina_letter", "<p>Which letter is the retina?</p>" + str(eye_boxes(title="Retina letter")), _mcq_opts("A", "B", "C", "a glasses brand"), "B", "B is the retina."),
        _VI_KEY("intermediate", "retina_word", "Write the word for the layer that detects the image at the back of the eye.", "retina", "Retina."),
        _VI_NUM("intermediate", "focus2", "Near-sight and far-sight are how many focusing-error kinds in this lesson?", 2, "Two kinds."),
        _VI_ORD("intermediate", "accom_near", "Order accommodation, then near-sight as distant blur.", ["accom", "near"], _FOCUS_BANK, "How focus changes, then one error."),
        _VI_PICK("intermediate", "stereo_ok", "Select two-views and illusion-as-interpretation.", ["two", "illusion"], _STEREO_BANK, 2, "Depth and brain. No test scores."),
    ],
    "difficult": [
        _VI_MCQ("difficult", "path_c", "Letter C in the eye schematic is", _mcq_opts("a lunch ranking", "the path of signals toward the brain", "a virus", "a stored prescription"), "B", "C is the path."),
        _VI_MCQ("difficult", "both_err", "Near-sight and far-sight both", _mcq_opts("require a class league table", "are focusing errors in this model, not a demand for private scores", "are smells", "are semicircular canals"), "B", "Focus errors."),
        _VI_MCQ("difficult", "brain2", "Two people can see the same drawing differently because", _mcq_opts("science forbids interpretation", "the brain uses cues; that is not a ranking of whose brain is better", "the quiz must store IQ", "lenses vote"), "B", "Cues, not a ranking."),
        _VI_MCQ("difficult", "accom2", "For a near object the lens in this model", _mcq_opts("must be thrown away", "changes shape (accommodation)", "becomes a canal", "uploads a prescription"), "B", "Shape change."),
        _VI_MCQ("difficult", "jordan", "Jordan (fictional) is fooled by an illusion. A fair sentence is", _mcq_opts("Jordan failed a secret eye exam stored here", "the brain misread cues; it is not a stored clinical test", "rank Jordan", "illusions are bacteria"), "B", "Cues."),
        _VI_MCQ("difficult", "path_letter", "<p>Which letter is the path toward the brain?</p>" + str(eye_boxes(title="Path letter")), _mcq_opts("A", "C", "B", "a pupil handle"), "B", "C is the path."),
        _VI_KEY("difficult", "accom_word", "Write the word for changing lens shape so near or far can be in focus.", "accommodation", "Accommodation."),
        _VI_NUM("difficult", "zero_rx", "How many glasses prescriptions should this quiz store? Enter 0.", 0, "Zero."),
        _VI_ORD("difficult", "full", "Order lens, retina, then brain path.", ["lens", "retina", "brain"], _EYE_BANK, "Same chain."),
        _VI_PICK("difficult", "focus_not", "Select the two items that do not belong.", ["vote_lens", "spy_rx"], _FOCUS_BANK, 2, "No votes, no prescription files."),
    ],
}

eursc_science_vision, eursc_science_vision_variants = _bind("vision", _VI_POOLS)

_EAR_BANK = (
    {"id": "outer", "text": "The outer ear collects sound"},
    {"id": "middle", "text": "The middle ear passes vibration inward"},
    {"id": "inner", "text": "The inner ear includes sensing structures such as the cochlea"},
    {"id": "rank_ear", "text": "The quiz should rank whose hearing is best"},
)
_SOUND_BANK = (
    {"id": "vib", "text": "Sound is vibration that needs a medium in this model"},
    {"id": "stereo", "text": "Two ears help locate a source"},
    {"id": "vacuum", "text": "Sound travels best in a perfect vacuum classroom"},
    {"id": "aid_file", "text": "The app should store who uses a hearing aid"},
)
_AID_BANK = (
    {"id": "aid", "text": "A hearing aid is a tool that can help; this app does not store whose it is"},
    {"id": "illusion", "text": "An auditory illusion can be interpretation of cues"},
    {"id": "force_test", "text": "Pupils must publish a private hearing-test score"},
    {"id": "no_medium", "text": "Pitch is a food group"},
)

_HE_POOLS = {
    "foundational": [
        _HE_MCQ("foundational", "outer", "The outer ear mainly", _mcq_opts("stores a medical file", "collects sound", "is a retina", "ranks classmates"), "B", "Collector."),
        _HE_MCQ("foundational", "vib", "Sound in this lesson is", _mcq_opts("a light-year of mass", "vibration that needs a medium", "a vaccine", "a private score"), "B", "Vibration in a medium."),
        _HE_MCQ("foundational", "two", "Two ears help to", _mcq_opts("store prescriptions", "locate a sound source (stereo)", "create a vacuum", "rank the class"), "B", "Localisation."),
        _HE_MCQ("foundational", "aid", "A hearing aid in this lesson is", _mcq_opts("a class league", "a tool that can help; the app does not store whose it is", "a bacterium", "a demand for a private test"), "B", "Tool, no file."),
        _HE_MCQ("foundational", "medium", "Without a medium, the S2 model says sound", _mcq_opts("is louder", "does not travel as it does in air", "becomes a lens", "must be listed from home"), "B", "Needs a medium."),
        _HE_MCQ("foundational", "outer_letter", "<p>Which letter is the outer ear?</p>" + str(ear_boxes(title="Outer letter")), _mcq_opts("B", "A", "C", "a pupil name"), "B", "A is outer."),
        _HE_KEY("foundational", "vib_word", "Write the word for the back-and-forth motion that sound is in this model.", "vibration", "Vibration."),
        _HE_NUM("foundational", "ears2", "How many ears are used for stereo localisation in this lesson?", 2, "Two."),
        _HE_ORD("foundational", "path", "Order outer, then middle, then inner ear.", ["outer", "middle", "inner"], _EAR_BANK, "Inward path."),
        _HE_PICK("foundational", "ear_ok", "Select outer and inner ear ideas.", ["outer", "inner"], _EAR_BANK, 2, "Two regions. No ranking."),
    ],
    "intermediate": [
        _HE_MCQ("intermediate", "middle", "The middle ear", _mcq_opts("is a taste", "passes vibration inward", "is a vacuum requirement", "stores who has an aid"), "B", "Pass inward."),
        _HE_MCQ("intermediate", "pitch", "Pitch in this S2 acoustic idea is about", _mcq_opts("how heavy a planet is", "how high or low a sound is taken to be", "a glasses file", "a class ranking"), "B", "High/low."),
        _HE_MCQ("intermediate", "loud", "Loudness in this model is about", _mcq_opts("a food group", "how strong a sound is taken to be", "a retina", "publishing a test"), "B", "Strength."),
        _HE_MCQ("intermediate", "sam", "Sam (fictional) uses an aid. A fair comment is", _mcq_opts("publish Sam's audiogram here", "an aid can help; this app does not store whose it is", "rank Sam", "aids are viruses"), "B", "No file."),
        _HE_MCQ("intermediate", "illusion", "An auditory illusion can be", _mcq_opts("proof science is a vote", "the brain interpreting sound cues", "a stored clinical test", "a canal made of food"), "B", "Interpretation."),
        _HE_MCQ("intermediate", "middle_letter", "<p>Which letter is the middle ear?</p>" + str(ear_boxes(title="Middle letter")), _mcq_opts("A", "B", "C", "an aid brand"), "B", "B is middle."),
        _HE_KEY("intermediate", "cochlea_word", "Write the word for a coiled inner-ear structure named in this lesson.", "cochlea", "Cochlea."),
        _HE_NUM("intermediate", "parts3", "Outer, middle and inner are how many labelled regions?", 3, "Three."),
        _HE_ORD("intermediate", "vib_st", "Order vibration-in-a-medium, then two-ear location.", ["vib", "stereo"], _SOUND_BANK, "What sound is, then localisation."),
        _HE_PICK("intermediate", "sound_ok", "Select vibration-needs-medium and two-ear location.", ["vib", "stereo"], _SOUND_BANK, 2, "Two ideas. No aid file."),
    ],
    "difficult": [
        _HE_MCQ("difficult", "inner", "The inner ear in this schematic includes", _mcq_opts("only a lunch box", "sensing structures such as the cochlea", "a glasses league", "a vacuum pump for ranking"), "B", "Inner sensors."),
        _HE_MCQ("difficult", "vacuum", "Saying sound travels best in a classroom vacuum is", _mcq_opts("required S2 physics", "a poor fit: this model needs a medium", "a retina fact", "a reason to store tests"), "B", "Needs a medium."),
        _HE_MCQ("difficult", "both", "Pitch and loudness both", _mcq_opts("require a published private score", "are acoustic ideas, not a class hearing league", "are smells only", "are prescriptions"), "B", "Acoustics, no league."),
        _HE_MCQ("difficult", "jordan", "Jordan (fictional) mis-locates a sound with one ear covered. That fits", _mcq_opts("a stored clinical file", "stereo localisation using two ears", "a taste illusion only", "ranking Jordan"), "B", "Two ears."),
        _HE_MCQ("difficult", "not_test", "This quiz", _mcq_opts("must publish hearing-test scores", "does not store hearing tests or whose aid it is", "diagnoses Sam", "ranks the class"), "B", "No tests stored."),
        _HE_MCQ("difficult", "inner_letter", "<p>Which letter is the inner ear?</p>" + str(ear_boxes(title="Inner letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is inner."),
        _HE_KEY("difficult", "coch2", "Write the word for the inner-ear coil that this lesson names.", "cochlea", "Cochlea."),
        _HE_NUM("difficult", "zero_aid", "How many hearing-aid records should this quiz store? Enter 0.", 0, "Zero."),
        _HE_ORD("difficult", "aid_ill", "Order aid-as-a-tool, then illusion-as-interpretation.", ["aid", "illusion"], _AID_BANK, "Tool, then brain."),
        _HE_PICK("difficult", "aid_not", "Select the two items that do not belong.", ["force_test", "no_medium"], _AID_BANK, 2, "No forced scores; pitch is not a food."),
    ],
}

eursc_science_hearing, eursc_science_hearing_variants = _bind("hearing", _HE_POOLS)

_REC_BANK = (
    {"id": "pressure", "text": "Some receptors detect pressure or contact"},
    {"id": "temp", "text": "Some receptors detect temperature"},
    {"id": "pain", "text": "Pain receptors warn of possible damage"},
    {"id": "rank_skin", "text": "The quiz should rank whose skin is toughest"},
)
_DENS_BANK = (
    {"id": "dense", "text": "Fingertips are modelled as denser in receptors than some other regions"},
    {"id": "map", "text": "A two-point test maps density with consent, not a class body league"},
    {"id": "force", "text": "Pupils must be touched without consent for the quiz"},
    {"id": "spy_map", "text": "The app should store a private body map"},
)

_TO_POOLS = {
    "foundational": [
        _TO_MCQ("foundational", "pressure", "Pressure receptors in this lesson detect", _mcq_opts("a light-year", "contact or pressure", "a vaccination file", "whose skin to rank"), "B", "Contact."),
        _TO_MCQ("foundational", "temp", "Temperature receptors detect", _mcq_opts("a retina only", "hot or cold in this S2 model", "a glasses brand", "a class league"), "B", "Hot/cold."),
        _TO_MCQ("foundational", "pain", "Pain receptors", _mcq_opts("are a popularity score", "warn of possible damage", "store a medical file here", "are a vacuum"), "B", "Warning."),
        _TO_MCQ("foundational", "dense", "Receptor density is modelled as", _mcq_opts("identical on every region always", "higher in some regions such as a fingertip than in some others", "a reason to rank bodies", "a stored private map"), "B", "Not uniform."),
        _TO_MCQ("foundational", "consent", "A classroom two-point test", _mcq_opts("must proceed without consent", "needs teacher rules and consent; it is not a body ranking", "uploads a map to this app", "replaces all other senses"), "B", "Consent, no ranking."),
        _TO_MCQ("foundational", "not_rank", "This quiz", _mcq_opts("ranks whose skin is toughest", "does not rank skin and does not store a private body map", "forces contact", "diagnoses pain"), "B", "No ranking."),
        _TO_KEY("foundational", "rec_word", "Write the word for a sensor cell that detects a stimulus such as pressure.", "receptor", "Receptor."),
        _TO_NUM("foundational", "types3", "Pressure, temperature and pain are how many receptor ideas in this lesson?", 3, "Three."),
        _TO_ORD("foundational", "pt", "Order pressure receptors, then temperature receptors.", ["pressure", "temp"], _REC_BANK, "Two types."),
        _TO_PICK("foundational", "rec_ok", "Select pressure and pain receptor ideas.", ["pressure", "pain"], _REC_BANK, 2, "Two types. No toughness league."),
    ],
    "intermediate": [
        _TO_MCQ("intermediate", "two_pt", "A two-point threshold is smaller where", _mcq_opts("receptors are modelled as rarer", "receptors are modelled as denser, so two points are easier to tell apart", "the quiz ranks bodies", "consent is skipped"), "B", "Denser → finer."),
        _TO_MCQ("intermediate", "alex", "Alex (fictional) tells two pin-pricks apart on a fingertip but not on a forearm in a teacher-approved demo. That fits", _mcq_opts("a stored body map in this app", "density differing by region", "a virus", "ranking Alex"), "B", "Density map as a model."),
        _TO_MCQ("intermediate", "temp2", "The same lukewarm water can feel different after hot or cold. That is", _mcq_opts("proof temperature is a vote", "a perception effect; not a demand to log whose hands they are", "a glasses file", "a reason to skip consent"), "B", "Perception."),
        _TO_MCQ("intermediate", "plan", "A fair investigation plan names", _mcq_opts("secret touching with no method", "independent, dependent and control variables, plus consent", "a private map stored here", "a class toughness league"), "B", "Variables + consent."),
        _TO_MCQ("intermediate", "pain2", "Pain in this model is", _mcq_opts("a popularity contest", "a warning sense, not a ranking of who is tougher", "a cochlea", "a stored diagnosis"), "B", "Warning."),
        _TO_MCQ("intermediate", "no_force", "If a volunteer does not consent, the method", _mcq_opts("continues anyway for the quiz", "stops; the app does not require contact", "stores a map anyway", "ranks the volunteer"), "B", "Stop."),
        _TO_KEY("intermediate", "dense_word", "Write the word for how tightly packed receptors are in a region.", "density", "Density."),
        _TO_NUM("intermediate", "points2", "A two-point test uses how many points of contact in the name?", 2, "Two."),
        _TO_ORD("intermediate", "map_ord", "Order denser fingertips, then a consented two-point map.", ["dense", "map"], _DENS_BANK, "Density, then method."),
        _TO_PICK("intermediate", "dens_ok", "Select density-by-region and consented mapping.", ["dense", "map"], _DENS_BANK, 2, "Two ideas. No forced contact."),
    ],
    "difficult": [
        _TO_MCQ("difficult", "control", "A control in a two-point mapping might be", _mcq_opts("skipping consent", "the same tool and the same pressure rule on each region", "storing a private map", "ranking skin"), "B", "Fair test."),
        _TO_MCQ("difficult", "not_league", "Using the mapping to rank classmates is", _mcq_opts("the scientific aim", "a misuse; density is a model, not a toughness league", "required by SI", "a reason to skip teacher rules"), "B", "No league."),
        _TO_MCQ("difficult", "three", "Pressure, temperature and pain are", _mcq_opts("one receptor only", "three receptor ideas in this lesson", "tastes", "prescriptions"), "B", "Three."),
        _TO_MCQ("difficult", "jordan", "Jordan (fictional) feels cold after ice, then lukewarm as hot. A science line is", _mcq_opts("store Jordan's hand log", "context changes temperature perception; no personal log here", "rank Jordan", "it cannot be receptors"), "B", "Context."),
        _TO_MCQ("difficult", "app", "This app", _mcq_opts("stores a private body map", "does not store a body map and does not force contact", "diagnoses pain", "replaces the teacher"), "B", "No map file."),
        _TO_MCQ("difficult", "iv", "The independent variable in the fingertip-vs-forearm demo is", _mcq_opts("a popularity score", "the skin region tested, if that is what the plan changes", "whose toughness rank it is", "a stored map"), "B", "Region."),
        _TO_KEY("difficult", "pain_word", "Write the word for the warning sense named in this lesson.", "pain", "Pain."),
        _TO_NUM("difficult", "zero_map", "How many private body maps should this quiz store? Enter 0.", 0, "Zero."),
        _TO_ORD("difficult", "rec3", "Order pressure, then temperature, then pain.", ["pressure", "temp", "pain"], _REC_BANK, "Three types."),
        _TO_PICK("difficult", "dens_not", "Select the two items that do not belong.", ["force", "spy_map"], _DENS_BANK, 2, "No forced contact; no stored map."),
    ],
}

eursc_science_touch, eursc_science_touch_variants = _bind("touch", _TO_POOLS)

_SMELL_BANK = (
    {"id": "receptors", "text": "Smell receptors detect a range of airborne chemicals"},
    {"id": "context", "text": "Context can change what a smell is taken to mean"},
    {"id": "rank_nose", "text": "The quiz should rank whose nose is best"},
    {"id": "list_home", "text": "Pupils must list private home odours"},
)
_CAT_BANK = (
    {"id": "category", "text": "Smells can be grouped with public examples"},
    {"id": "differ", "text": "Perception can differ without ranking classmates"},
    {"id": "one_rec", "text": "There is only one smell receptor in the whole species in this lesson"},
    {"id": "force_sniff", "text": "Everyone must sniff an unknown chemical for the quiz"},
)

_SM_POOLS = {
    "foundational": [
        _SM_MCQ("foundational", "rec", "Smell receptors detect", _mcq_opts("only a light-year", "a range of airborne chemicals", "a glasses file", "whose nose to rank"), "B", "Airborne chemicals."),
        _SM_MCQ("foundational", "range", "Receptor diversity in this lesson means", _mcq_opts("one receptor for the whole species only", "many receptor types for different chemicals", "a class league", "a stored odour diary"), "B", "Many types."),
        _SM_MCQ("foundational", "cat", "Categorising smells should use", _mcq_opts("private home lists stored here", "public examples, not a private odour list", "a toughness rank", "forced unknown chemicals"), "B", "Public examples."),
        _SM_MCQ("foundational", "context", "Context can", _mcq_opts("never change a smell judgement", "change what a smell is taken to mean", "store a diary", "rank noses"), "B", "Context matters."),
        _SM_MCQ("foundational", "differ", "Two people can judge a smell differently. That", _mcq_opts("requires a nose league", "can happen without ranking classmates", "must be stored as a medical file", "proves science is a vote"), "B", "Difference without ranking."),
        _SM_MCQ("foundational", "not_list", "This quiz", _mcq_opts("must list private home odours", "does not collect private odour lists", "ranks noses", "forces sniffing unknowns"), "B", "No list."),
        _SM_KEY("foundational", "smell_word", "Write the word for the sense that detects airborne chemicals in this lesson.", "smell", "Smell."),
        _SM_NUM("foundational", "air1", "Smell in this model detects chemicals in the air. Enter 1 if that statement is the lesson model.", 1, "One: airborne."),
        _SM_ORD("foundational", "rec_ctx", "Order receptors detecting chemicals, then context changing meaning.", ["receptors", "context"], _SMELL_BANK, "Detect, then interpret."),
        _SM_PICK("foundational", "smell_ok", "Select receptors and context.", ["receptors", "context"], _SMELL_BANK, 2, "Two ideas. No nose league."),
    ],
    "intermediate": [
        _SM_MCQ("intermediate", "alex", "Alex (fictional) calls the same vapour 'food' in a kitchen and 'chemical' in a lab photo. That fits", _mcq_opts("a stored diary", "context changing interpretation", "a ranking of Alex", "a vacuum"), "B", "Context."),
        _SM_MCQ("intermediate", "public", "A public example (for example a labelled bottle in a textbook photo) is better than", _mcq_opts("a teacher-approved demo", "harvesting private home odours for the quiz", "a control variable", "consent"), "B", "No harvest."),
        _SM_MCQ("intermediate", "many", "Many receptor types help because", _mcq_opts("there is only one chemical in air", "different chemicals can be distinguished in the model", "noses must be ranked", "the app stores diaries"), "B", "Diversity."),
        _SM_MCQ("intermediate", "safety", "Sniffing an unknown chemical in class", _mcq_opts("is required by this quiz", "is not required; follow the teacher's risk rules", "uploads a list here", "ranks the class"), "B", "Teacher rules."),
        _SM_MCQ("intermediate", "not_rank", "A better nose is", _mcq_opts("the thing this quiz ranks", "not a league table in this lesson", "a prescription file", "a cochlea"), "B", "No league."),
        _SM_MCQ("intermediate", "group", "Grouping smells is", _mcq_opts("a private confession", "a categorisation using shared examples", "a body map", "a hearing test"), "B", "Categories."),
        _SM_KEY("intermediate", "context_word", "Write the word for the surrounding situation that can change what a smell means.", "context", "Context."),
        _SM_NUM("intermediate", "zero_list", "How many private odour diaries should this quiz collect? Enter 0.", 0, "Zero."),
        _SM_ORD("intermediate", "cat_dif", "Order grouping with public examples, then perception can differ.", ["category", "differ"], _CAT_BANK, "Group, then differ."),
        _SM_PICK("intermediate", "cat_ok", "Select categorisation and differing perception.", ["category", "differ"], _CAT_BANK, 2, "Two ideas."),
    ],
    "difficult": [
        _SM_MCQ("difficult", "same_mol", "The same chemical can be judged differently because", _mcq_opts("molecules vote", "context and prior learning affect interpretation", "the quiz stores homes", "noses must be ranked"), "B", "Interpretation."),
        _SM_MCQ("difficult", "not_one", "Saying there is only one smell receptor for the whole species", _mcq_opts("matches this lesson", "does not match the diversity model here", "is a taste", "is a stored map"), "B", "Diversity."),
        _SM_MCQ("difficult", "jordan", "Jordan (fictional) dislikes a smell others call pleasant. A science line is", _mcq_opts("rank Jordan's nose", "perception can differ; no ranking and no home list", "store Jordan's kitchen", "force a sniff of an unknown"), "B", "Difference."),
        _SM_MCQ("difficult", "evidence", "A claim that a smell 'always means danger' needs", _mcq_opts("a class vote only", "evidence; context can change the meaning", "a private diary", "a league"), "B", "Evidence."),
        _SM_MCQ("difficult", "app", "This app", _mcq_opts("collects private odour lists", "does not collect private odour lists or rank noses", "forces unknown sniffs", "diagnoses"), "B", "No lists."),
        _SM_MCQ("difficult", "airborne", "Airborne chemicals are the stimulus for", _mcq_opts("stereo depth only", "smell in this lesson", "a glasses file", "semicircular canals only"), "B", "Smell."),
        _SM_KEY("difficult", "chem_word", "Write the word for substances in the air that smell receptors detect.", "chemicals", "Chemicals."),
        _SM_NUM("difficult", "zero_rank", "How many nose-ranking tables should this quiz keep? Enter 0.", 0, "Zero."),
        _SM_ORD("difficult", "rec_ctx2", "Order receptors, then context.", ["receptors", "context"], _SMELL_BANK, "Detect then interpret."),
        _SM_PICK("difficult", "cat_not", "Select the two items that do not belong.", ["one_rec", "force_sniff"], _CAT_BANK, 2, "Not one receptor; no forced unknown sniffs."),
    ],
}

eursc_science_smell, eursc_science_smell_variants = _bind("smell", _SM_POOLS)

_TASTE_BANK = (
    {"id": "five", "text": "This lesson names five tastes"},
    {"id": "smell", "text": "Smell and taste work together in flavour"},
    {"id": "rank_tongue", "text": "The quiz should rank whose tongue is best"},
    {"id": "force_eat", "text": "Everyone must eat an unknown food for the quiz"},
)
_FIVE_BANK = (
    {"id": "sweet", "text": "Sweet is one of the five tastes in this model"},
    {"id": "salt", "text": "Salt is one of the five tastes in this model"},
    {"id": "colour", "text": "Colour and context can change how a food is judged"},
    {"id": "spy_menu", "text": "Pupils must upload a private menu"},
)

_TA_POOLS = {
    "foundational": [
        _TA_MCQ("foundational", "five", "This S2 model names how many tastes as a teaching set?", _mcq_opts("one", "five", "eighty", "zero"), "B", "Five."),
        _TA_MCQ("foundational", "flavour", "Flavour in this lesson", _mcq_opts("ignores smell", "uses taste and smell together", "is a glasses file", "ranks tongues"), "B", "Taste + smell."),
        _TA_MCQ("foundational", "colour", "Colour of a drink can", _mcq_opts("never affect a judgement", "change how the drink is judged in some demos", "store a menu", "force unknown foods"), "B", "Context/colour."),
        _TA_MCQ("foundational", "block", "A blocked nose in a fictional case can", _mcq_opts("improve stereo depth", "reduce flavour because smell is reduced", "rank the tongue", "upload a menu"), "B", "Smell contributes."),
        _TA_MCQ("foundational", "control", "A classroom tasting", _mcq_opts("must force unknown foods", "needs teacher rules; nobody is forced to eat", "stores private menus here", "ranks tongues"), "B", "No force."),
        _TA_MCQ("foundational", "not_rank", "This quiz", _mcq_opts("ranks whose tongue is best", "does not rank tongues and does not store menus", "forces eating", "diagnoses"), "B", "No ranking."),
        _TA_KEY("foundational", "taste_word", "Write the word for the sense of sweet, salt, sour, bitter and umami in this lesson.", "taste", "Taste."),
        _TA_NUM("foundational", "five_n", "Enter the number of tastes named in this lesson.", 5, "Five."),
        _TA_ORD("foundational", "five_smell", "Order five tastes, then smell working with taste.", ["five", "smell"], _TASTE_BANK, "Tastes, then flavour."),
        _TA_PICK("foundational", "taste_ok", "Select five-tastes and taste–smell.", ["five", "smell"], _TASTE_BANK, 2, "Two ideas. No tongue league."),
    ],
    "intermediate": [
        _TA_MCQ("intermediate", "umami", "Umami in this model is", _mcq_opts("a hearing aid", "one of the five tastes", "a private menu", "a canal"), "B", "Fifth taste."),
        _TA_MCQ("intermediate", "alex", "Alex (fictional) with a blocked nose says food is bland. That fits", _mcq_opts("a stored menu", "reduced smell reducing flavour", "ranking Alex", "forced eating"), "B", "Interaction."),
        _TA_MCQ("intermediate", "same", "The same yoghurt dyed different colours can be judged differently. That is", _mcq_opts("proof science is a vote only", "a colour/context effect", "a reason to upload menus", "a toughness league"), "B", "Colour."),
        _TA_MCQ("intermediate", "iv", "If colour is the independent variable, a control might be", _mcq_opts("forcing everyone to eat", "the same yoghurt base and the same temperature", "storing menus", "ranking tongues"), "B", "Fair test."),
        _TA_MCQ("intermediate", "sour", "Sour is", _mcq_opts("not in the five", "one of the five tastes in this model", "a retina", "a prescription"), "B", "In the five."),
        _TA_MCQ("intermediate", "bitter", "Bitter is", _mcq_opts("a glasses file", "one of the five tastes in this model", "a class rank", "a vacuum"), "B", "In the five."),
        _TA_KEY("intermediate", "flavour_word", "Write the word for the combined taste-and-smell experience named in this lesson.", "flavour", "Flavour."),
        _TA_NUM("intermediate", "zero_force", "How many pupils must eat an unknown food because this quiz says so? Enter 0.", 0, "Zero."),
        _TA_ORD("intermediate", "sw_sa", "Order sweet, then salt, as two of the five.", ["sweet", "salt"], _FIVE_BANK, "Two of five."),
        _TA_PICK("intermediate", "five_col", "Select sweet and colour/context.", ["sweet", "colour"], _FIVE_BANK, 2, "Taste and context."),
    ],
    "difficult": [
        _TA_MCQ("difficult", "jordan", "Jordan (fictional) rates a brown drink as 'cola' and the same clear drink as 'not cola'. A science line is", _mcq_opts("upload Jordan's fridge", "colour/context can steer the judgement", "rank Jordan's tongue", "force an unknown"), "B", "Cues."),
        _TA_MCQ("difficult", "not_five", "Ignoring smell when discussing flavour is", _mcq_opts("required", "an incomplete model in this lesson", "a stored menu", "a hearing test"), "B", "Include smell."),
        _TA_MCQ("difficult", "ethics", "A tasting demo that forces an unknown food is", _mcq_opts("good science in this app", "not what this lesson requires", "a density map", "a canal"), "B", "No force."),
        _TA_MCQ("difficult", "five2", "Sweet, salt, sour, bitter and umami are", _mcq_opts("two tastes", "the five tastes in this S2 set", "ear regions", "prescriptions"), "B", "Five."),
        _TA_MCQ("difficult", "app", "This app", _mcq_opts("stores private menus", "does not store menus or rank tongues", "forces eating", "diagnoses"), "B", "No menus."),
        _TA_MCQ("difficult", "dv", "The dependent variable in a colour-of-drink demo could be", _mcq_opts("a toughness rank", "the labelled judgement of the drink, recorded as data not as a personal diet file", "whose tongue it is", "a stored fridge"), "B", "Judgement as data."),
        _TA_KEY("difficult", "umami_word", "Write the word for the savoury fifth taste named in this lesson.", "umami", "Umami."),
        _TA_NUM("difficult", "five_again", "Enter 5 for the teaching set of tastes.", 5, "Five."),
        _TA_ORD("difficult", "col_after", "Order salt as a taste, then colour/context effects.", ["salt", "colour"], _FIVE_BANK, "Taste, then cues."),
        _TA_PICK("difficult", "taste_not", "Select the two items that do not belong.", ["rank_tongue", "force_eat"], _TASTE_BANK, 2, "No ranking; no forced eating."),
    ],
}

eursc_science_taste, eursc_science_taste_variants = _bind("taste", _TA_POOLS)

_PROP_BANK = (
    {"id": "position", "text": "Proprioception senses body position without looking"},
    {"id": "balance", "text": "Balance is keeping oriented against a fall"},
    {"id": "canals", "text": "Semicircular canals detect rotation of the head"},
    {"id": "rank_spin", "text": "The quiz should rank who is least dizzy"},
)
_TOGETHER_BANK = (
    {"id": "vision", "text": "Vision can help balance"},
    {"id": "together", "text": "Canals, vision and proprioception work together"},
    {"id": "spin_force", "text": "Pupils must be spun until unwell for the quiz"},
    {"id": "spy_dizzy", "text": "The app should store who felt dizzy"},
)

_PR_POOLS = {
    "foundational": [
        _PR_MCQ("foundational", "prop", "Proprioception is", _mcq_opts("a food group", "sensing body position without looking", "a glasses league", "a stored dizziness file"), "B", "Position sense."),
        _PR_MCQ("foundational", "bal", "Balance is", _mcq_opts("a vaccination record", "keeping the body oriented against a fall", "ranking who is least dizzy", "a private map"), "B", "Orientation."),
        _PR_MCQ("foundational", "canal", "Semicircular canals detect", _mcq_opts("only tastes", "rotation of the head in this model", "a menu", "whose score to publish"), "B", "Rotation."),
        _PR_MCQ("foundational", "three", "This lesson models how many canal loops in the sketch?", _mcq_opts("one", "three", "eighty", "zero"), "B", "Three."),
        _PR_MCQ("foundational", "look", "Knowing an arm is raised without looking fits", _mcq_opts("a stored clinical file", "proprioception", "a tongue rank", "forced spinning"), "B", "Proprioception."),
        _PR_MCQ("foundational", "a_letter", "<p>Which letter is one canal loop?</p>" + str(canal_boxes(title="Canal A")), _mcq_opts("none of them", "A", "a pupil name", "a menu"), "B", "A is a loop."),
        _PR_KEY("foundational", "bal_word", "Write the word for keeping oriented against a fall.", "balance", "Balance."),
        _PR_NUM("foundational", "canals3", "Enter the number of semicircular canals in this lesson's sketch.", 3, "Three."),
        _PR_ORD("foundational", "pos_bal", "Order proprioception as position, then balance.", ["position", "balance"], _PROP_BANK, "Position, then balance."),
        _PR_PICK("foundational", "prop_ok", "Select position sense and canals-detect-rotation.", ["position", "canals"], _PROP_BANK, 2, "Two ideas. No dizziness league."),
    ],
    "intermediate": [
        _PR_MCQ("intermediate", "together", "Canals, vision and proprioception", _mcq_opts("never interact", "work together in this model", "must be ranked", "are stored as who felt dizzy"), "B", "Together."),
        _PR_MCQ("intermediate", "eyes", "Closing the eyes can make standing on one foot harder because", _mcq_opts("taste vanishes", "vision often helps balance", "the quiz stores dizziness", "canals become food"), "B", "Vision helps."),
        _PR_MCQ("intermediate", "alex", "Alex (fictional) can touch their nose with eyes closed. That fits", _mcq_opts("a stored file", "proprioception", "ranking Alex", "forced spinning"), "B", "Position sense."),
        _PR_MCQ("intermediate", "spin", "A teacher-approved slow turn can show canals at work. The quiz still", _mcq_opts("must spin pupils until unwell", "does not require spinning anyone unwell and does not store who felt dizzy", "ranks dizziness", "uploads a map"), "B", "No forced illness."),
        _PR_MCQ("intermediate", "planes", "Three canals in different orientations help detect", _mcq_opts("menus", "rotation in more than one plane", "a tongue rank", "a glasses file"), "B", "Planes."),
        _PR_MCQ("intermediate", "b_letter", "<p>Which letter is the middle canal loop?</p>" + str(canal_boxes(title="Canal B")), _mcq_opts("A", "B", "a handle", "a rank"), "B", "B is the middle loop."),
        _PR_KEY("intermediate", "canal_word", "Write the word for a fluid-filled loop that detects head rotation (one token).", "canal", "Canal."),
        _PR_NUM("intermediate", "systems3", "Canals, vision and proprioception are how many cooperating ideas here?", 3, "Three."),
        _PR_ORD("intermediate", "vis_tog", "Order vision helping balance, then the three working together.", ["vision", "together"], _TOGETHER_BANK, "Vision, then together."),
        _PR_PICK("intermediate", "tog_ok", "Select vision-helps and working-together.", ["vision", "together"], _TOGETHER_BANK, 2, "Two ideas."),
    ],
    "difficult": [
        _PR_MCQ("difficult", "mismatch", "If vision and canals disagree, a person may feel odd. That is", _mcq_opts("a reason to store who felt dizzy here", "a cue mismatch in the model, not a class league", "a menu", "forced spinning"), "B", "Mismatch."),
        _PR_MCQ("difficult", "not_rank", "Ranking who is least dizzy is", _mcq_opts("the aim of this quiz", "a misuse of the lesson", "required SI", "a taste"), "B", "No ranking."),
        _PR_MCQ("difficult", "jordan", "Jordan (fictional) sways when asked to stand still with eyes closed. A science line is", _mcq_opts("publish Jordan's file", "vision often helps; this is not a stored clinical test", "rank Jordan", "spin Jordan until unwell"), "B", "Vision + balance."),
        _PR_MCQ("difficult", "prop2", "Without looking, knowing a joint angle fits", _mcq_opts("a stored map", "proprioception", "umami", "an advert"), "B", "Proprioception."),
        _PR_MCQ("difficult", "app", "This app", _mcq_opts("stores who felt dizzy", "does not store dizziness reports or force spinning", "ranks the class", "replaces the teacher"), "B", "No reports."),
        _PR_MCQ("difficult", "c_letter", "<p>Which letter is the right-hand canal loop?</p>" + str(canal_boxes(title="Canal C")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the right loop."),
        _PR_KEY("difficult", "prop_word", "Write the word for sensing body position without looking.", "proprioception", "Proprioception."),
        _PR_NUM("difficult", "zero_dizzy", "How many dizziness files should this quiz store? Enter 0.", 0, "Zero."),
        _PR_ORD("difficult", "pos_can", "Order position sense, then canals detecting rotation.", ["position", "canals"], _PROP_BANK, "Then canals."),
        _PR_PICK("difficult", "tog_not", "Select the two items that do not belong.", ["spin_force", "spy_dizzy"], _TOGETHER_BANK, 2, "No forced spinning; no dizziness file."),
    ],
}

eursc_science_proprioception_balance, eursc_science_proprioception_balance_variants = _bind(
    "proprioception_balance", _PR_POOLS
)

_INT_BANK = (
    {"id": "internal", "text": "Interoception senses internal states such as hunger or heartbeat"},
    {"id": "interpret", "text": "The same signal can be interpreted in more than one way"},
    {"id": "survey", "text": "The quiz should collect how each pupil feels right now"},
    {"id": "joke", "text": "Internal signals are only a joke"},
)
_WELL_BANK = (
    {"id": "wellbeing", "text": "Interpretation of internal signals links to wellbeing ideas"},
    {"id": "signpost", "text": "Personal distress is for a trusted adult, not this app"},
    {"id": "rank_mood", "text": "Pupils must compare moods in the quiz"},
    {"id": "diagnose", "text": "This app diagnoses anxiety from a heartbeat story"},
)

_IN_POOLS = {
    "foundational": [
        _IN_MCQ("foundational", "what", "Interoception is", _mcq_opts("ranking classmates", "sensing internal states such as hunger or heartbeat", "a glasses league", "a stored mood diary"), "B", "Internal sense."),
        _IN_MCQ("foundational", "hunger", "Hunger in this lesson is", _mcq_opts("a class confession", "an example of an internal signal, not a demand to log meals", "a canal rank", "a prescription file"), "B", "Example, no log."),
        _IN_MCQ("foundational", "heart", "A heartbeat the person can notice is", _mcq_opts("a public league", "an internal signal in this model, not a stored ECG", "a tongue rank", "a forced spin"), "B", "Signal, no ECG."),
        _IN_MCQ("foundational", "interpret", "The same signal", _mcq_opts("has only one meaning forever", "can be interpreted in more than one way", "must be a mood ranking", "is a joke only"), "B", "Interpretation."),
        _IN_MCQ("foundational", "not_ask", "This quiz", _mcq_opts("collects how each pupil feels right now", "does not collect how a pupil feels right now", "diagnoses", "ranks moods"), "B", "No survey."),
        _IN_MCQ("foundational", "signpost", "Personal distress belongs with", _mcq_opts("this generator as a clinic", "a trusted adult or qualified help; this app does not diagnose", "a mood league", "a joke"), "B", "Signpost."),
        _IN_KEY("foundational", "hunger_word", "Write the word for the internal signal that food is needed, used as an example here.", "hunger", "Hunger."),
        _IN_NUM("foundational", "zero_mood", "How many live mood surveys should this quiz run? Enter 0.", 0, "Zero."),
        _IN_ORD("foundational", "int_int", "Order internal sensing, then interpretation can vary.", ["internal", "interpret"], _INT_BANK, "Sense, then interpret."),
        _IN_PICK("foundational", "int_ok", "Select internal sensing and variable interpretation.", ["internal", "interpret"], _INT_BANK, 2, "Two ideas. No live survey."),
    ],
    "intermediate": [
        _IN_MCQ("intermediate", "alex", "Alex (fictional) notices a fast heartbeat after a run and after a scare. A science line is", _mcq_opts("store Alex's feelings", "the same kind of signal can be read in more than one context", "rank Alex", "diagnose Alex here"), "B", "Context."),
        _IN_MCQ("intermediate", "thirst", "Thirst is used here as", _mcq_opts("a confession", "another internal example, not a demand to log drinks", "a hearing test", "a league"), "B", "Example."),
        _IN_MCQ("intermediate", "well", "Wellbeing in this lesson is", _mcq_opts("a mood ranking of the class", "an idea linked to how signals are interpreted, without a survey", "a stored diary", "a joke"), "B", "Idea, no survey."),
        _IN_MCQ("intermediate", "not_joke", "Treating internal signals as only a joke is", _mcq_opts("required", "a poor fit for this lesson", "a canal fact", "an SI unit"), "B", "Not a joke."),
        _IN_MCQ("intermediate", "app", "This app", _mcq_opts("diagnoses anxiety from a story", "does not diagnose; it teaches the idea and signposts help", "ranks moods", "collects live feelings"), "B", "No diagnosis."),
        _IN_MCQ("intermediate", "sam", "Sam (fictional) is in distress in a scenario. The next step in the lesson is", _mcq_opts("publish Sam in a league", "signpost a trusted adult; do not collect a diary here", "ignore it as a joke", "store a heartbeat file"), "B", "Signpost."),
        _IN_KEY("intermediate", "thirst_word", "Write the word for the internal signal that drink is needed, used as an example here.", "thirst", "Thirst."),
        _IN_NUM("intermediate", "two_ex", "Hunger and thirst are how many example signals named here?", 2, "Two."),
        _IN_ORD("intermediate", "well_sig", "Order wellbeing as interpretation, then signposting qualified help.", ["wellbeing", "signpost"], _WELL_BANK, "Idea, then signpost."),
        _IN_PICK("intermediate", "well_ok", "Select wellbeing-as-idea and signposting.", ["wellbeing", "signpost"], _WELL_BANK, 2, "Two ideas. No mood rank."),
    ],
    "difficult": [
        _IN_MCQ("difficult", "jordan", "Jordan (fictional) reads a fast heartbeat as 'excited' in one story and 'worried' in another. That fits", _mcq_opts("a stored diagnosis", "interpretation of the same kind of signal", "a tongue rank", "a live class survey"), "B", "Interpretation."),
        _IN_MCQ("difficult", "not_ecg", "A heartbeat example is", _mcq_opts("an ECG stored for each pupil", "a teaching case, not a medical record", "a ranking", "a forced confession"), "B", "Teaching case."),
        _IN_MCQ("difficult", "limit", "Limits of this lesson include", _mcq_opts("that it diagnoses the class", "that it does not collect live feelings or replace a clinician", "that jokes replace support", "that moods must be compared"), "B", "Limits."),
        _IN_MCQ("difficult", "both", "Hunger and heartbeat both", _mcq_opts("must be logged from each pupil", "are internal examples without a personal log here", "are tastes", "are canals only"), "B", "Examples."),
        _IN_MCQ("difficult", "misuse", "A misuse of interoception teaching is", _mcq_opts("using a fictional case", "running a live mood survey in the quiz", "signposting help", "saying interpretation can vary"), "B", "No live survey."),
        _IN_MCQ("difficult", "help", "Qualified help is", _mcq_opts("this app", "outside the app: teacher signpost, trusted adult, health professional", "a league", "a joke"), "B", "Outside."),
        _IN_KEY("difficult", "intero_word", "Write the word for sensing internal bodily states.", "interoception", "Interoception."),
        _IN_NUM("difficult", "zero_feel", "How many live feeling-survey items should this quiz ask a pupil? Enter 0.", 0, "Zero."),
        _IN_ORD("difficult", "int2", "Order internal sensing, then variable interpretation.", ["internal", "interpret"], _INT_BANK, "Again."),
        _IN_PICK("difficult", "well_not", "Select the two items that do not belong.", ["rank_mood", "diagnose"], _WELL_BANK, 2, "No mood rank; no diagnosis."),
    ],
}

eursc_science_interoception, eursc_science_interoception_variants = _bind(
    "interoception", _IN_POOLS
)

_NH_BANK = (
    {"id": "uv", "text": "Some animals sense UV that humans do not see the same way"},
    {"id": "ir", "text": "Some animals sense infrared as a heat-related signal"},
    {"id": "echo", "text": "Echolocation uses returning sound"},
    {"id": "rank_animal", "text": "The quiz should rank which pupil has a superpower"},
)
_TECH_BANK = (
    {"id": "polar", "text": "Some animals use polarised light as a cue"},
    {"id": "em", "text": "Some animals sense electric or magnetic cues in a scientific model"},
    {"id": "ultra", "text": "Ultrasound is above the usual human hearing band in this model"},
    {"id": "magic", "text": "Nonhuman senses are spells, not detectable signals"},
    {"id": "rank_tech", "text": "The quiz should rank which pupil has a superpower"},
)

_NH_POOLS = {
    "foundational": [
        _NH_MCQ("foundational", "uv", "UV sensing is modelled as", _mcq_opts("a pupil superpower league", "detecting light humans do not see the same way", "a stored mood", "a menu"), "B", "Different band."),
        _NH_MCQ("foundational", "ir", "Infrared sensing in an animal example is", _mcq_opts("a joke only", "a heat-related signal humans do not see the same way", "a glasses rank", "a forced spin"), "B", "IR."),
        _NH_MCQ("foundational", "echo", "Echolocation uses", _mcq_opts("a private diary", "returning sound to locate objects", "a tongue league", "a prescription"), "B", "Returning sound."),
        _NH_MCQ("foundational", "ultra", "Ultrasound in this model is", _mcq_opts("a food", "sound above the usual human hearing band", "a retina file", "a superpower rank"), "B", "Above human band."),
        _NH_MCQ("foundational", "tech", "A sensor that detects a chemical", _mcq_opts("cannot be compared to a sense", "uses the same idea: detect a signal", "ranks pupils", "stores moods"), "B", "Signal."),
        _NH_MCQ("foundational", "not_super", "This quiz", _mcq_opts("ranks which pupil has a superpower", "does not rank pupils as having animal superpowers", "diagnoses", "stores who echolocates"), "B", "No superpower league."),
        _NH_KEY("foundational", "echo_word", "Write the word for locating objects using returning sound.", "echolocation", "Echolocation."),
        _NH_NUM("foundational", "bands2", "UV and IR are how many extra light-related bands named here?", 2, "Two."),
        _NH_ORD("foundational", "uv_echo", "Order UV sensing, then echolocation.", ["uv", "echo"], _NH_BANK, "Light band, then sound."),
        _NH_PICK("foundational", "nh_ok", "Select UV sensing and echolocation.", ["uv", "echo"], _NH_BANK, 2, "Two adaptations. No superpower rank."),
    ],
    "intermediate": [
        _NH_MCQ("intermediate", "polar", "Polarised-light sensing is", _mcq_opts("a menu", "a cue some animals use in the public model", "a pupil league", "a stored ECG"), "B", "Polarisation cue."),
        _NH_MCQ("intermediate", "em", "Electromagnetic sensing in this lesson is", _mcq_opts("a spell", "a scientific model of detecting electric or magnetic cues", "a tongue rank", "forced spinning"), "B", "Model, not magic."),
        _NH_MCQ("intermediate", "infra", "Infrasound is modelled as", _mcq_opts("a taste", "sound below the usual human hearing band", "a glasses file", "a mood survey"), "B", "Below band."),
        _NH_MCQ("intermediate", "chem", "A dog's chemical sense and a lab sensor both", _mcq_opts("rank pupils", "detect a chemical signal in this comparison", "store diaries", "are superpower leagues"), "B", "Same idea."),
        _NH_MCQ("intermediate", "alex", "Alex (fictional) claims a classmate can see UV. A science reply is", _mcq_opts("rank the classmate", "humans do not see UV the same way; do not invent a superpower league", "store a file", "diagnose"), "B", "No league."),
        _NH_MCQ("intermediate", "bat", "A bat example of echolocation is", _mcq_opts("a stored clinical test", "returning sound as a locating tool", "a menu", "a prescription"), "B", "Echo."),
        _NH_KEY("intermediate", "ultra_word", "Write the word for sound above the usual human hearing band in this lesson.", "ultrasound", "Ultrasound."),
        _NH_NUM("intermediate", "zero_super", "How many pupil-superpower ranks should this quiz keep? Enter 0.", 0, "Zero."),
        _NH_ORD("intermediate", "polar_em", "Order polarised-light cue, then electromagnetic sensing.", ["polar", "em"], _TECH_BANK, "Light cue, then EM."),
        _NH_PICK("intermediate", "tech_ok", "Select polarised light and ultrasound.", ["polar", "ultra"], _TECH_BANK, 2, "Two ideas."),
    ],
    "difficult": [
        _NH_MCQ("difficult", "ir2", "A pit-organ style IR example is best called", _mcq_opts("a pupil superpower", "an adaptation to a heat-related signal", "a mood file", "a forced sniff"), "B", "Adaptation."),
        _NH_MCQ("difficult", "not_magic", "Calling nonhuman senses spells is wrong because", _mcq_opts("spells are SI units", "they are models of detecting signals that can be studied", "pupils must be ranked", "the app stores who has which sense"), "B", "Signals."),
        _NH_MCQ("difficult", "both_sound", "Infrasound and ultrasound both", _mcq_opts("are tastes", "sit outside the usual human hearing band in this model", "rank classmates", "are prescriptions"), "B", "Outside the band."),
        _NH_MCQ("difficult", "tech2", "Technology can extend detection because", _mcq_opts("sensors replace all ethics", "a device can detect a signal a human sense does not", "pupils become bats in the quiz", "moods are stored"), "B", "Extend detection."),
        _NH_MCQ("difficult", "jordan", "Jordan (fictional) wants a league of 'who is most like a shark'. The lesson says", _mcq_opts("publish the league", "do not rank pupils; study animal models and instruments", "store files", "force spinning"), "B", "No league."),
        _NH_MCQ("difficult", "uv_ir", "UV and IR both", _mcq_opts("are umami", "are light-related bands humans do not use the same way", "are canals", "are menus"), "B", "Bands."),
        _NH_KEY("difficult", "infra_word", "Write the word for sound below the usual human hearing band in this lesson.", "infrasound", "Infrasound."),
        _NH_NUM("difficult", "echo1", "Echolocation uses returning sound. Enter 1 if that is the lesson model.", 1, "One: returning sound."),
        _NH_ORD("difficult", "uv_ir_ord", "Order UV sensing, then infrared sensing.", ["uv", "ir"], _NH_BANK, "Two bands."),
        _NH_PICK("difficult", "tech_not", "Select the two items that do not belong.", ["magic", "rank_tech"], _TECH_BANK, 2, "Not spells; no superpower rank."),
    ],
}

eursc_science_nonhuman_senses, eursc_science_nonhuman_senses_variants = _bind(
    "nonhuman_senses", _NH_POOLS
)
