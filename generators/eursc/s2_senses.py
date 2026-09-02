"""S2 Unit 2.3 Senses — 2.3.1–2.3.8."""
from generators.eursc.science_shared import bind_eursc_topic, canal_boxes, ear_boxes, eye_boxes
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
        _VI_MCQ("foundational", "lens", "In this schematic the lens mainly", _mcq_opts("stores a glasses file", "refracts light to help form an image", "is a food group", "ranks classmates"), "B", "Refraction by the lens.", "Think what that part does to light so an image can form, not about storing a glasses file."),
        _VI_MCQ("foundational", "retina", "The retina", _mcq_opts("is a unit of time", "detects the image at the back of the eye in this model", "is an advert", "must be photographed for the quiz"), "B", "Detector.", "Look for the detecting layer at the back of the eye in this model, not a unit of time."),
        _VI_MCQ("foundational", "brain", "Signals from the eye", _mcq_opts("stay in the lens only", "travel toward the brain, which interprets them", "are a vaccination record", "are a sleep bar"), "B", "Interpretation in the brain.", "After the eye detects something, the signals still need to be interpreted. Where do they go?"),
        _VI_MCQ("foundational", "accom", "Accommodation is", _mcq_opts("a class vote on posters", "changing lens shape so near or far can be in focus", "a demand for a prescription list", "an antibiotic"), "B", "Lens shape.", "This word is about changing the focusing part's shape so near or far can be sharp."),
        _VI_MCQ("foundational", "stereo", "Stereo depth uses", _mcq_opts("one identical view only, always", "two slightly different views from two eyes", "a rumour", "a private scoreboard"), "B", "Two views.", "Judging depth in this model uses two slightly different views, not one identical photo."),
        _VI_MCQ("foundational", "lens_letter", "<p>Which letter is the lens?</p>" + str(eye_boxes(title="Lens letter")), _mcq_opts("B", "A", "C", "a pupil name"), "B", "A is the lens.", "Match the letter on the schematic to the part that bends light to help form an image."),
        _VI_KEY("foundational", "lens_word", "Write the word for the part that refracts light to help form an image.", "lens", "Lens.", "One short word names the part that bends light so an image can form. It is not a food group."),
        _VI_NUM("foundational", "eyes2", "How many eyes are used for stereo depth in this lesson's usual model?", 2, "Two eyes.", "Stereo depth in this model uses a pair. Count how many that is."),
        _VI_ORD("foundational", "path", "Order lens, then retina, then path toward the brain.", ["lens", "retina", "brain"], _EYE_BANK, "Optics, detector, interpretation.", "First the part that bends light, then the detector at the back, then signals heading for interpretation."),
        _VI_PICK("foundational", "eye_ok", "Select lens and retina.", ["lens", "retina"], _EYE_BANK, 2, "Two parts. No ranking.", "Choose the bending part and the detecting layer. Skip ranking whose sight is best."),
    ],
    "intermediate": [
        _VI_MCQ("intermediate", "near", "Near-sight in this S2 model means", _mcq_opts("near objects cannot be seen at all", "distant objects are not in focus", "the retina is a virus", "the quiz stores a prescription"), "B", "Far blur.", "In this model, near-sight means far things are blurry, not that close things vanish."),
        _VI_MCQ("intermediate", "far", "Far-sight in this model means", _mcq_opts("distant objects are the only possible image", "near objects are not in focus", "stereo is a food", "pupils must list glasses brands"), "B", "Near blur.", "Far-sight here means close-up things are not sharp, not that only distant images exist."),
        _VI_MCQ("intermediate", "alex", "Alex (fictional) squints at a board far away. A science comment is", _mcq_opts("demand Alex's prescription in the quiz", "that can fit a focusing error; the app does not store whose glasses they are", "rank Alex", "it cannot be optics"), "B", "Third person, no file.", "A science comment can mention a focusing error without storing whose glasses they are."),
        _VI_MCQ("intermediate", "illusion", "A visual illusion is often", _mcq_opts("proof the instrument is always broken", "the brain interpreting cues in a way that mismatches the object", "a vaccination", "a class eye-test league"), "B", "Interpretation.", "An illusion is often the brain reading cues in a way that does not match the object."),
        _VI_MCQ("intermediate", "not_rank", "This quiz", _mcq_opts("ranks whose eyesight is best", "does not rank eyesight and does not store prescriptions", "collects optician letters", "diagnoses Alex"), "B", "No ranking, no file.", "This quiz does not make a league of whose sight is best and does not keep prescription files."),
        _VI_MCQ("intermediate", "retina_letter", "<p>Which letter is the retina?</p>" + str(eye_boxes(title="Retina letter")), _mcq_opts("A", "B", "C", "a glasses brand"), "B", "B is the retina.", "Match the letter to the detecting layer at the back of the eye, not a glasses brand."),
        _VI_KEY("intermediate", "retina_word", "Write the word for the layer that detects the image at the back of the eye.", "retina", "Retina.", "Name the detecting layer at the back of the eye. Do not name a glasses brand."),
        _VI_NUM("intermediate", "focus2", "Near-sight and far-sight are how many focusing-error kinds in this lesson?", 2, "Two kinds.", "The lesson names two kinds of focusing error. How many is that?"),
        _VI_ORD("intermediate", "accom_near", "Order accommodation, then near-sight as distant blur.", ["accom", "near"], _FOCUS_BANK, "How focus changes, then one error.", "First how the focusing part changes shape, then the error where distant things are blurry."),
        _VI_PICK("intermediate", "stereo_ok", "Select two-views and illusion-as-interpretation.", ["two", "illusion"], _STEREO_BANK, 2, "Depth and brain. No test scores.", "Choose two-views for depth and the idea that an illusion is interpretation. Skip private test scores."),
    ],
    "difficult": [
        _VI_MCQ("difficult", "path_c", "Letter C in the eye schematic is", _mcq_opts("a lunch ranking", "the path of signals toward the brain", "a virus", "a stored prescription"), "B", "C is the path.", "Letter C on the schematic is the route of signals toward interpretation, not a lunch ranking."),
        _VI_MCQ("difficult", "both_err", "Near-sight and far-sight both", _mcq_opts("require a class league table", "are focusing errors in this model, not a demand for private scores", "are smells", "are semicircular canals"), "B", "Focus errors.", "Both are focusing errors in this model. They are not a demand for private scores."),
        _VI_MCQ("difficult", "brain2", "Two people can see the same drawing differently because", _mcq_opts("science forbids interpretation", "the brain uses cues; that is not a ranking of whose brain is better", "the quiz must store IQ", "lenses vote"), "B", "Cues, not a ranking.", "The same drawing can be read differently because the brain uses cues. That is not a ranking of whose brain is better."),
        _VI_MCQ("difficult", "accom2", "For a near object the lens in this model", _mcq_opts("must be thrown away", "changes shape (accommodation)", "becomes a canal", "uploads a prescription"), "B", "Shape change.", "For something close, the focusing part changes shape rather than being thrown away."),
        _VI_MCQ("difficult", "jordan", "Jordan (fictional) is fooled by an illusion. A fair sentence is", _mcq_opts("Jordan failed a secret eye exam stored here", "the brain misread cues; it is not a stored clinical test", "rank Jordan", "illusions are bacteria"), "B", "Cues.", "Being fooled by an illusion means cues were misread, not that a secret clinical test was stored."),
        _VI_MCQ("difficult", "path_letter", "<p>Which letter is the path toward the brain?</p>" + str(eye_boxes(title="Path letter")), _mcq_opts("A", "C", "B", "a pupil handle"), "B", "C is the path.", "Find the letter that marks the signal path toward interpretation, not a pupil handle."),
        _VI_KEY("difficult", "accom_word", "Write the word for changing lens shape so near or far can be in focus.", "accommodation", "Accommodation.", "One word names the process of changing focusing-part shape so near or far can be sharp."),
        _VI_NUM("difficult", "zero_rx", "How many glasses prescriptions should this quiz store? Enter 0.", 0, "Zero.", "This quiz should store no glasses prescriptions. What number is that?"),
        _VI_ORD("difficult", "full", "Order lens, retina, then brain path.", ["lens", "retina", "brain"], _EYE_BANK, "Same chain.", "Same chain again: bend light, detect, then interpret."),
        _VI_PICK("difficult", "focus_not", "Select the two items that do not belong.", ["vote_lens", "spy_rx"], _FOCUS_BANK, 2, "No votes, no prescription files.", "Choose the class vote on focus and the item that spies on prescriptions. Those do not belong."),
    ],
}

_VI_STANDARD = {
    "foundational": (
        'vision_foundational_mcq_accom',
        'vision_foundational_keyword_lens_word',
        'vision_foundational_number_eyes2',
        'vision_foundational_order_path',
        'vision_foundational_pick_eye_ok',
    ),
    "intermediate": (
        'vision_intermediate_mcq_alex',
        'vision_intermediate_keyword_retina_word',
        'vision_intermediate_number_focus2',
        'vision_intermediate_order_accom_near',
        'vision_intermediate_pick_stereo_ok',
    ),
    "difficult": (
        'vision_difficult_mcq_accom2',
        'vision_difficult_keyword_accom_word',
        'vision_difficult_number_zero_rx',
        'vision_difficult_order_full',
        'vision_difficult_pick_focus_not',
    ),
}
eursc_science_vision, eursc_science_vision_variants = bind_eursc_topic('vision', _VI_POOLS, _VI_STANDARD)

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
        _HE_MCQ("foundational", "outer", "The outer ear mainly", _mcq_opts("stores a medical file", "collects sound", "is a retina", "ranks classmates"), "B", "Collector.", "The outer part of the ear is a collector of sound, not a medical-file store."),
        _HE_MCQ("foundational", "vib", "Sound in this lesson is", _mcq_opts("a light-year of mass", "vibration that needs a medium", "a vaccine", "a private score"), "B", "Vibration in a medium.", "Sound here is back-and-forth motion that needs something to travel through, not a vaccine."),
        _HE_MCQ("foundational", "two", "Two ears help to", _mcq_opts("store prescriptions", "locate a sound source (stereo)", "create a vacuum", "rank the class"), "B", "Localisation.", "A pair of ears helps work out where a sound comes from, not to store prescriptions."),
        _HE_MCQ("foundational", "aid", "A hearing aid in this lesson is", _mcq_opts("a class league", "a tool that can help; the app does not store whose it is", "a bacterium", "a demand for a private test"), "B", "Tool, no file.", "An aid is a tool that can help. This app does not store whose it is."),
        _HE_MCQ("foundational", "medium", "Without a medium, the S2 model says sound", _mcq_opts("is louder", "does not travel as it does in air", "becomes a lens", "must be listed from home"), "B", "Needs a medium.", "If there is nothing to travel through, sound does not travel as it does in air."),
        _HE_MCQ("foundational", "outer_letter", "<p>Which letter is the outer ear?</p>" + str(ear_boxes(title="Outer letter")), _mcq_opts("B", "A", "C", "a pupil name"), "B", "A is outer.", "Match the letter to the collecting region of the ear, not a pupil name."),
        _HE_KEY("foundational", "vib_word", "Write the word for the back-and-forth motion that sound is in this model.", "vibration", "Vibration.", "One word names the back-and-forth motion that sound is in this model."),
        _HE_NUM("foundational", "ears2", "How many ears are used for stereo localisation in this lesson?", 2, "Two.", "Stereo localisation in this lesson uses a pair. Count how many that is."),
        _HE_ORD("foundational", "path", "Order outer, then middle, then inner ear.", ["outer", "middle", "inner"], _EAR_BANK, "Inward path.", "Follow the sound inward: collector first, then the passing-on region, then the sensing region."),
        _HE_PICK("foundational", "ear_ok", "Select outer and inner ear ideas.", ["outer", "inner"], _EAR_BANK, 2, "Two regions. No ranking.", "Choose the collector and the inner sensing region. Skip ranking whose hearing is best."),
    ],
    "intermediate": [
        _HE_MCQ("intermediate", "middle", "The middle ear", _mcq_opts("is a taste", "passes vibration inward", "is a vacuum requirement", "stores who has an aid"), "B", "Pass inward.", "The middle region passes the back-and-forth motion further in, not a taste."),
        _HE_MCQ("intermediate", "pitch", "Pitch in this S2 acoustic idea is about", _mcq_opts("how heavy a planet is", "how high or low a sound is taken to be", "a glasses file", "a class ranking"), "B", "High/low.", "Pitch is about how high or low a sound is taken to be, not how heavy a planet is."),
        _HE_MCQ("intermediate", "loud", "Loudness in this model is about", _mcq_opts("a food group", "how strong a sound is taken to be", "a retina", "publishing a test"), "B", "Strength.", "Loudness is about how strong a sound is taken to be, not a food group."),
        _HE_MCQ("intermediate", "sam", "Sam (fictional) uses an aid. A fair comment is", _mcq_opts("publish Sam's audiogram here", "an aid can help; this app does not store whose it is", "rank Sam", "aids are viruses"), "B", "No file.", "A fair comment treats an aid as a helpful tool and does not publish a private test here."),
        _HE_MCQ("intermediate", "illusion", "An auditory illusion can be", _mcq_opts("proof science is a vote", "the brain interpreting sound cues", "a stored clinical test", "a canal made of food"), "B", "Interpretation.", "An auditory illusion can be the brain interpreting sound cues, not a vote or a stored clinical test."),
        _HE_MCQ("intermediate", "middle_letter", "<p>Which letter is the middle ear?</p>" + str(ear_boxes(title="Middle letter")), _mcq_opts("A", "B", "C", "an aid brand"), "B", "B is middle.", "Match the letter to the middle region that passes motion inward, not an aid brand."),
        _HE_KEY("intermediate", "cochlea_word", "Write the word for a coiled inner-ear structure named in this lesson.", "cochlea", "Cochlea.", "Name the coiled inner-ear structure this lesson names. One token."),
        _HE_NUM("intermediate", "parts3", "Outer, middle and inner are how many labelled regions?", 3, "Three.", "Count the labelled regions: outer, middle and inner."),
        _HE_ORD("intermediate", "vib_st", "Order vibration-in-a-medium, then two-ear location.", ["vib", "stereo"], _SOUND_BANK, "What sound is, then localisation.", "First what sound is (motion that needs a medium), then using two ears to locate a source."),
        _HE_PICK("intermediate", "sound_ok", "Select vibration-needs-medium and two-ear location.", ["vib", "stereo"], _SOUND_BANK, 2, "Two ideas. No aid file.", "Choose motion-needs-a-medium and two-ear location. Skip storing whose aid it is."),
    ],
    "difficult": [
        _HE_MCQ("difficult", "inner", "The inner ear in this schematic includes", _mcq_opts("only a lunch box", "sensing structures such as the cochlea", "a glasses league", "a vacuum pump for ranking"), "B", "Inner sensors.", "The inner region includes sensing structures such as the coiled part, not a lunch box."),
        _HE_MCQ("difficult", "vacuum", "Saying sound travels best in a classroom vacuum is", _mcq_opts("required S2 physics", "a poor fit: this model needs a medium", "a retina fact", "a reason to store tests"), "B", "Needs a medium.", "A classroom vacuum is a poor fit: this model needs a medium for sound to travel."),
        _HE_MCQ("difficult", "both", "Pitch and loudness both", _mcq_opts("require a published private score", "are acoustic ideas, not a class hearing league", "are smells only", "are prescriptions"), "B", "Acoustics, no league.", "Pitch and loudness are acoustic ideas. They are not a class hearing league."),
        _HE_MCQ("difficult", "jordan", "Jordan (fictional) mis-locates a sound with one ear covered. That fits", _mcq_opts("a stored clinical file", "stereo localisation using two ears", "a taste illusion only", "ranking Jordan"), "B", "Two ears.", "Covering one ear makes locating harder because this model uses two ears to locate a source."),
        _HE_MCQ("difficult", "not_test", "This quiz", _mcq_opts("must publish hearing-test scores", "does not store hearing tests or whose aid it is", "diagnoses Sam", "ranks the class"), "B", "No tests stored.", "This quiz does not store hearing tests or whose aid it is."),
        _HE_MCQ("difficult", "inner_letter", "<p>Which letter is the inner ear?</p>" + str(ear_boxes(title="Inner letter")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is inner.", "Find the letter that marks the inner sensing region, not a handle."),
        _HE_KEY("difficult", "coch2", "Write the word for the inner-ear coil that this lesson names.", "cochlea", "Cochlea.", "Name the inner-ear coil this lesson names. Same structure as before, one token."),
        _HE_NUM("difficult", "zero_aid", "How many hearing-aid records should this quiz store? Enter 0.", 0, "Zero.", "This quiz should store no hearing-aid records. What number is that?"),
        _HE_ORD("difficult", "aid_ill", "Order aid-as-a-tool, then illusion-as-interpretation.", ["aid", "illusion"], _AID_BANK, "Tool, then brain.", "First an aid as a tool that can help, then an illusion as interpretation of cues."),
        _HE_PICK("difficult", "aid_not", "Select the two items that do not belong.", ["force_test", "no_medium"], _AID_BANK, 2, "No forced scores; pitch is not a food.", "Choose forcing a private hearing-test score, and calling pitch a food group. Those do not belong."),
    ],
}

_HE_STANDARD = {
    "foundational": (
        'hearing_foundational_mcq_aid',
        'hearing_foundational_keyword_vib_word',
        'hearing_foundational_number_ears2',
        'hearing_foundational_order_path',
        'hearing_foundational_pick_ear_ok',
    ),
    "intermediate": (
        'hearing_intermediate_mcq_illusion',
        'hearing_intermediate_keyword_cochlea_word',
        'hearing_intermediate_number_parts3',
        'hearing_intermediate_order_vib_st',
        'hearing_intermediate_pick_sound_ok',
    ),
    "difficult": (
        'hearing_difficult_mcq_both',
        'hearing_difficult_keyword_coch2',
        'hearing_difficult_number_zero_aid',
        'hearing_difficult_order_aid_ill',
        'hearing_difficult_pick_aid_not',
    ),
}
eursc_science_hearing, eursc_science_hearing_variants = bind_eursc_topic('hearing', _HE_POOLS, _HE_STANDARD)

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
        _TO_MCQ("foundational", "pressure", "Pressure receptors in this lesson detect", _mcq_opts("a light-year", "contact or pressure", "a vaccination file", "whose skin to rank"), "B", "Contact.", "These sensors pick up contact or pressure, not a light-year and not a ranking of skin."),
        _TO_MCQ("foundational", "temp", "Temperature receptors detect", _mcq_opts("a retina only", "hot or cold in this S2 model", "a glasses brand", "a class league"), "B", "Hot/cold.", "These sensors pick up hot or cold in this S2 model, not a glasses brand."),
        _TO_MCQ("foundational", "pain", "Pain receptors", _mcq_opts("are a popularity score", "warn of possible damage", "store a medical file here", "are a vacuum"), "B", "Warning.", "These sensors warn of possible damage. They are not a popularity score."),
        _TO_MCQ("foundational", "dense", "Receptor density is modelled as", _mcq_opts("identical on every region always", "higher in some regions such as a fingertip than in some others", "a reason to rank bodies", "a stored private map"), "B", "Not uniform.", "Packing of sensors is modelled as higher in some regions, such as a fingertip, than in some others."),
        _TO_MCQ("foundational", "consent", "A classroom two-point test", _mcq_opts("must proceed without consent", "needs teacher rules and consent; it is not a body ranking", "uploads a map to this app", "replaces all other senses"), "B", "Consent, no ranking.", "A classroom two-point test needs teacher rules and consent. It is not a ranking of bodies."),
        _TO_MCQ("foundational", "not_rank", "This quiz", _mcq_opts("ranks whose skin is toughest", "does not rank skin and does not store a private body map", "forces contact", "diagnoses pain"), "B", "No ranking.", "This quiz does not rank whose skin is toughest and does not store a private map of the skin."),
        _TO_KEY("foundational", "rec_word", "Write the word for a sensor cell that detects a stimulus such as pressure.", "receptor", "Receptor.", "One word names a sensor cell that detects a stimulus such as pressure."),
        _TO_NUM("foundational", "types3", "Pressure, temperature and pain are how many receptor ideas in this lesson?", 3, "Three.", "Count the sensor ideas named: pressure, temperature and the warning sense."),
        _TO_ORD("foundational", "pt", "Order pressure receptors, then temperature receptors.", ["pressure", "temp"], _REC_BANK, "Two types.", "Put contact-or-pressure sensors first, then hot-or-cold sensors."),
        _TO_PICK("foundational", "rec_ok", "Select pressure and pain receptor ideas.", ["pressure", "pain"], _REC_BANK, 2, "Two types. No toughness league.", "Choose contact-or-pressure sensors and the warning-of-damage idea. Skip a toughness league."),
    ],
    "intermediate": [
        _TO_MCQ("intermediate", "two_pt", "A two-point threshold is smaller where", _mcq_opts("receptors are modelled as rarer", "receptors are modelled as denser, so two points are easier to tell apart", "the quiz ranks bodies", "consent is skipped"), "B", "Denser → finer.", "Where sensors are packed more tightly, two points are easier to tell apart, so the threshold is smaller."),
        _TO_MCQ("intermediate", "alex", "Alex (fictional) tells two pin-pricks apart on a fingertip but not on a forearm in a teacher-approved demo. That fits", _mcq_opts("a stored body map in this app", "density differing by region", "a virus", "ranking Alex"), "B", "Density map as a model.", "Telling two pin-pricks apart on a fingertip but not a forearm fits packing differing by region, not a stored map here."),
        _TO_MCQ("intermediate", "temp2", "The same lukewarm water can feel different after hot or cold. That is", _mcq_opts("proof temperature is a vote", "a perception effect; not a demand to log whose hands they are", "a glasses file", "a reason to skip consent"), "B", "Perception.", "The same lukewarm water can be judged differently after hot or cold. That is a perception effect, not a hand log."),
        _TO_MCQ("intermediate", "plan", "A fair investigation plan names", _mcq_opts("secret touching with no method", "independent, dependent and control variables, plus consent", "a private map stored here", "a class toughness league"), "B", "Variables + consent.", "A fair plan names independent, dependent and control variables, and it needs consent."),
        _TO_MCQ("intermediate", "pain2", "Pain in this model is", _mcq_opts("a popularity contest", "a warning sense, not a ranking of who is tougher", "a cochlea", "a stored diagnosis"), "B", "Warning.", "This warning sense is not a ranking of who is tougher."),
        _TO_MCQ("intermediate", "no_force", "If a volunteer does not consent, the method", _mcq_opts("continues anyway for the quiz", "stops; the app does not require contact", "stores a map anyway", "ranks the volunteer"), "B", "Stop.", "If a volunteer does not consent, the method stops. This app does not require contact."),
        _TO_KEY("intermediate", "dense_word", "Write the word for how tightly packed receptors are in a region.", "density", "Density.", "One word names how tightly packed the sensors are in a region."),
        _TO_NUM("intermediate", "points2", "A two-point test uses how many points of contact in the name?", 2, "Two.", "The name already says how many points of contact. Enter that number."),
        _TO_ORD("intermediate", "map_ord", "Order denser fingertips, then a consented two-point map.", ["dense", "map"], _DENS_BANK, "Density, then method.", "First tighter packing in fingertips, then a consented two-point mapping. Skip forced contact."),
        _TO_PICK("intermediate", "dens_ok", "Select density-by-region and consented mapping.", ["dense", "map"], _DENS_BANK, 2, "Two ideas. No forced contact.", "Choose packing-by-region and a consented mapping. Skip forced contact and a stored private map."),
    ],
    "difficult": [
        _TO_MCQ("difficult", "control", "A control in a two-point mapping might be", _mcq_opts("skipping consent", "the same tool and the same pressure rule on each region", "storing a private map", "ranking skin"), "B", "Fair test.", "A control keeps the tool and the pressure rule the same on each region. Skipping consent is not a control."),
        _TO_MCQ("difficult", "not_league", "Using the mapping to rank classmates is", _mcq_opts("the scientific aim", "a misuse; density is a model, not a toughness league", "required by SI", "a reason to skip teacher rules"), "B", "No league.", "Using the mapping to rank classmates is a misuse. Packing is a model, not a toughness league."),
        _TO_MCQ("difficult", "three", "Pressure, temperature and pain are", _mcq_opts("one receptor only", "three receptor ideas in this lesson", "tastes", "prescriptions"), "B", "Three.", "Contact, hot-or-cold, and the warning sense are three sensor ideas in this lesson."),
        _TO_MCQ("difficult", "jordan", "Jordan (fictional) feels cold after ice, then lukewarm as hot. A science line is", _mcq_opts("store Jordan's hand log", "context changes temperature perception; no personal log here", "rank Jordan", "it cannot be receptors"), "B", "Context.", "After ice, lukewarm can be judged as hot. Context changes temperature perception; there is no personal log here."),
        _TO_MCQ("difficult", "app", "This app", _mcq_opts("stores a private body map", "does not store a body map and does not force contact", "diagnoses pain", "replaces the teacher"), "B", "No map file.", "This app does not store a private map of the skin and does not force contact."),
        _TO_MCQ("difficult", "iv", "The independent variable in the fingertip-vs-forearm demo is", _mcq_opts("a popularity score", "the skin region tested, if that is what the plan changes", "whose toughness rank it is", "a stored map"), "B", "Region.", "If the plan changes which skin region is tested, that is the independent variable."),
        _TO_KEY("difficult", "pain_word", "Write the word for the warning sense named in this lesson.", "pain", "Pain.", "One word names the warning sense in this lesson. It is not a popularity contest."),
        _TO_NUM("difficult", "zero_map", "How many private body maps should this quiz store? Enter 0.", 0, "Zero.", "This quiz should store no private maps of the skin. What number is that?"),
        _TO_ORD("difficult", "rec3", "Order pressure, then temperature, then pain.", ["pressure", "temp", "pain"], _REC_BANK, "Three types.", "Order the three sensor ideas: contact, then hot-or-cold, then the warning sense."),
        _TO_PICK("difficult", "dens_not", "Select the two items that do not belong.", ["force", "spy_map"], _DENS_BANK, 2, "No forced contact; no stored map.", "Choose forced contact without consent, and storing a private map. Those do not belong."),
    ],
}

_TO_STANDARD = {
    "foundational": (
        'touch_foundational_mcq_consent',
        'touch_foundational_keyword_rec_word',
        'touch_foundational_number_types3',
        'touch_foundational_order_pt',
        'touch_foundational_pick_rec_ok',
    ),
    "intermediate": (
        'touch_intermediate_mcq_alex',
        'touch_intermediate_keyword_dense_word',
        'touch_intermediate_number_points2',
        'touch_intermediate_order_map_ord',
        'touch_intermediate_pick_dens_ok',
    ),
    "difficult": (
        'touch_difficult_mcq_app',
        'touch_difficult_keyword_pain_word',
        'touch_difficult_number_zero_map',
        'touch_difficult_order_rec3',
        'touch_difficult_pick_dens_not',
    ),
}
eursc_science_touch, eursc_science_touch_variants = bind_eursc_topic('touch', _TO_POOLS, _TO_STANDARD)

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
        _SM_MCQ("foundational", "rec", "Smell receptors detect", _mcq_opts("only a light-year", "a range of airborne chemicals", "a glasses file", "whose nose to rank"), "B", "Airborne chemicals.", "These sensors pick up a range of chemicals in the air, not a light-year and not a nose ranking."),
        _SM_MCQ("foundational", "range", "Receptor diversity in this lesson means", _mcq_opts("one receptor for the whole species only", "many receptor types for different chemicals", "a class league", "a stored odour diary"), "B", "Many types.", "Diversity here means many sensor types for different chemicals, not one sensor for the whole species."),
        _SM_MCQ("foundational", "cat", "Categorising smells should use", _mcq_opts("private home lists stored here", "public examples, not a private odour list", "a toughness rank", "forced unknown chemicals"), "B", "Public examples.", "Grouping should use public examples, not a private odour list stored here."),
        _SM_MCQ("foundational", "context", "Context can", _mcq_opts("never change a smell judgement", "change what a smell is taken to mean", "store a diary", "rank noses"), "B", "Context matters.", "The surrounding situation can change what an odour is taken to mean."),
        _SM_MCQ("foundational", "differ", "Two people can judge a smell differently. That", _mcq_opts("requires a nose league", "can happen without ranking classmates", "must be stored as a medical file", "proves science is a vote"), "B", "Difference without ranking.", "Two people can judge an odour differently. That can happen without ranking classmates."),
        _SM_MCQ("foundational", "not_list", "This quiz", _mcq_opts("must list private home odours", "does not collect private odour lists", "ranks noses", "forces sniffing unknowns"), "B", "No list.", "This quiz does not collect private odour lists from home."),
        _SM_KEY("foundational", "smell_word", "Write the word for the sense that detects airborne chemicals in this lesson.", "smell", "Smell.", "One word names the sense that detects chemicals in the air. It is not a nose league."),
        _SM_NUM("foundational", "air1", "Smell in this model detects chemicals in the air. Enter 1 if that statement is the lesson model.", 1, "One: airborne.", "If the lesson model is chemicals in the air, enter 1. If it were not, the number would not be 1."),
        _SM_ORD("foundational", "rec_ctx", "Order receptors detecting chemicals, then context changing meaning.", ["receptors", "context"], _SMELL_BANK, "Detect, then interpret.", "First sensors detecting chemicals, then the surrounding situation changing the meaning."),
        _SM_PICK("foundational", "smell_ok", "Select receptors and context.", ["receptors", "context"], _SMELL_BANK, 2, "Two ideas. No nose league.", "Choose sensors detecting chemicals and the surrounding situation changing meaning. Skip a nose league."),
    ],
    "intermediate": [
        _SM_MCQ("intermediate", "alex", "Alex (fictional) calls the same vapour 'food' in a kitchen and 'chemical' in a lab photo. That fits", _mcq_opts("a stored diary", "context changing interpretation", "a ranking of Alex", "a vacuum"), "B", "Context.", "The same vapour judged as 'food' in a kitchen and 'chemical' in a lab photo fits the surrounding situation changing interpretation."),
        _SM_MCQ("intermediate", "public", "A public example (for example a labelled bottle in a textbook photo) is better than", _mcq_opts("a teacher-approved demo", "harvesting private home odours for the quiz", "a control variable", "consent"), "B", "No harvest.", "A labelled textbook photo is better than harvesting private home odours for the quiz."),
        _SM_MCQ("intermediate", "many", "Many receptor types help because", _mcq_opts("there is only one chemical in air", "different chemicals can be distinguished in the model", "noses must be ranked", "the app stores diaries"), "B", "Diversity.", "Many sensor types help because different chemicals can be distinguished in the model."),
        _SM_MCQ("intermediate", "safety", "Sniffing an unknown chemical in class", _mcq_opts("is required by this quiz", "is not required; follow the teacher's risk rules", "uploads a list here", "ranks the class"), "B", "Teacher rules.", "Sniffing an unknown chemical is not required by this quiz. Follow the teacher's risk rules."),
        _SM_MCQ("intermediate", "not_rank", "A better nose is", _mcq_opts("the thing this quiz ranks", "not a league table in this lesson", "a prescription file", "a cochlea"), "B", "No league.", "A 'better nose' is not a league table in this lesson."),
        _SM_MCQ("intermediate", "group", "Grouping smells is", _mcq_opts("a private confession", "a categorisation using shared examples", "a body map", "a hearing test"), "B", "Categories.", "Grouping odours is a categorisation using shared examples, not a private confession."),
        _SM_KEY("intermediate", "context_word", "Write the word for the surrounding situation that can change what a smell means.", "context", "Context.", "One word names the surrounding situation that can change what an odour means."),
        _SM_NUM("intermediate", "zero_list", "How many private odour diaries should this quiz collect? Enter 0.", 0, "Zero.", "This quiz should collect no private odour diaries. What number is that?"),
        _SM_ORD("intermediate", "cat_dif", "Order grouping with public examples, then perception can differ.", ["category", "differ"], _CAT_BANK, "Group, then differ.", "First grouping with public examples, then the idea that perception can differ without ranking."),
        _SM_PICK("intermediate", "cat_ok", "Select categorisation and differing perception.", ["category", "differ"], _CAT_BANK, 2, "Two ideas.", "Choose grouping with public examples and the idea that perception can differ. Skip one-sensor-only and forced unknown sniffs."),
    ],
    "difficult": [
        _SM_MCQ("difficult", "same_mol", "The same chemical can be judged differently because", _mcq_opts("molecules vote", "context and prior learning affect interpretation", "the quiz stores homes", "noses must be ranked"), "B", "Interpretation.", "The same chemical can be judged differently because the surrounding situation and prior learning affect interpretation."),
        _SM_MCQ("difficult", "not_one", "Saying there is only one smell receptor for the whole species", _mcq_opts("matches this lesson", "does not match the diversity model here", "is a taste", "is a stored map"), "B", "Diversity.", "One sensor for the whole species does not match the diversity model in this lesson."),
        _SM_MCQ("difficult", "jordan", "Jordan (fictional) dislikes a smell others call pleasant. A science line is", _mcq_opts("rank Jordan's nose", "perception can differ; no ranking and no home list", "store Jordan's kitchen", "force a sniff of an unknown"), "B", "Difference.", "Disliking an odour others call pleasant can happen. Perception can differ; there is no ranking and no home list."),
        _SM_MCQ("difficult", "evidence", "A claim that a smell 'always means danger' needs", _mcq_opts("a class vote only", "evidence; context can change the meaning", "a private diary", "a league"), "B", "Evidence.", "A claim that an odour 'always means danger' needs evidence. The surrounding situation can change the meaning."),
        _SM_MCQ("difficult", "app", "This app", _mcq_opts("collects private odour lists", "does not collect private odour lists or rank noses", "forces unknown sniffs", "diagnoses"), "B", "No lists.", "This app does not collect private odour lists or rank noses."),
        _SM_MCQ("difficult", "airborne", "Airborne chemicals are the stimulus for", _mcq_opts("stereo depth only", "smell in this lesson", "a glasses file", "semicircular canals only"), "B", "Smell.", "Chemicals in the air are the stimulus for this airborne sense in this lesson, not for stereo depth."),
        _SM_KEY("difficult", "chem_word", "Write the word for substances in the air that smell receptors detect.", "chemicals", "Chemicals.", "One word names the substances in the air that these sensors detect."),
        _SM_NUM("difficult", "zero_rank", "How many nose-ranking tables should this quiz keep? Enter 0.", 0, "Zero.", "This quiz should keep no nose-ranking tables. What number is that?"),
        _SM_ORD("difficult", "rec_ctx2", "Order receptors, then context.", ["receptors", "context"], _SMELL_BANK, "Detect then interpret.", "Detect with sensors first, then the surrounding situation. Same order as the earlier chain, worded for this round."),
        _SM_PICK("difficult", "cat_not", "Select the two items that do not belong.", ["one_rec", "force_sniff"], _CAT_BANK, 2, "Not one receptor; no forced unknown sniffs.", "Choose one-sensor-for-the-species and forcing unknown sniffs. Those do not belong."),
    ],
}

_SM_STANDARD = {
    "foundational": (
        'smell_foundational_mcq_cat',
        'smell_foundational_keyword_smell_word',
        'smell_foundational_number_air1',
        'smell_foundational_order_rec_ctx',
        'smell_foundational_pick_smell_ok',
    ),
    "intermediate": (
        'smell_intermediate_mcq_alex',
        'smell_intermediate_keyword_context_word',
        'smell_intermediate_number_zero_list',
        'smell_intermediate_order_cat_dif',
        'smell_intermediate_pick_cat_ok',
    ),
    "difficult": (
        'smell_difficult_mcq_airborne',
        'smell_difficult_keyword_chem_word',
        'smell_difficult_number_zero_rank',
        'smell_difficult_order_rec_ctx2',
        'smell_difficult_pick_cat_not',
    ),
}
eursc_science_smell, eursc_science_smell_variants = bind_eursc_topic('smell', _SM_POOLS, _SM_STANDARD)

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
        _TA_MCQ("foundational", "five", "This S2 model names how many tastes as a teaching set?", _mcq_opts("one", "five", "eighty", "zero"), "B", "Five.", "The teaching set in this S2 model is a small named list, not one and not eighty. Count the named set."),
        _TA_MCQ("foundational", "flavour", "Flavour in this lesson", _mcq_opts("ignores smell", "uses taste and smell together", "is a glasses file", "ranks tongues"), "B", "Taste + smell.", "Flavour here uses the tongue sense and the airborne sense together, not one of them alone."),
        _TA_MCQ("foundational", "colour", "Colour of a drink can", _mcq_opts("never affect a judgement", "change how the drink is judged in some demos", "store a menu", "force unknown foods"), "B", "Context/colour.", "In some demos the colour of a drink can change how it is judged. That is not a stored menu."),
        _TA_MCQ("foundational", "block", "A blocked nose in a fictional case can", _mcq_opts("improve stereo depth", "reduce flavour because smell is reduced", "rank the tongue", "upload a menu"), "B", "Smell contributes.", "A blocked nose in a fictional case can reduce flavour because the airborne sense is reduced."),
        _TA_MCQ("foundational", "control", "A classroom tasting", _mcq_opts("must force unknown foods", "needs teacher rules; nobody is forced to eat", "stores private menus here", "ranks tongues"), "B", "No force.", "A classroom tasting needs teacher rules. Nobody is forced to eat an unknown food."),
        _TA_MCQ("foundational", "not_rank", "This quiz", _mcq_opts("ranks whose tongue is best", "does not rank tongues and does not store menus", "forces eating", "diagnoses"), "B", "No ranking.", "This quiz does not rank tongues and does not store private menus."),
        _TA_KEY("foundational", "taste_word", "Write the word for the sense of sweet, salt, sour, bitter and umami in this lesson.", "taste", "Taste.", "One word names the sense of sweet, salt, sour, bitter and the savoury fifth in this lesson."),
        _TA_NUM("foundational", "five_n", "Enter the number of tastes named in this lesson.", 5, "Five.", "Count the named teaching set: sweet, salt, sour, bitter and the savoury fifth."),
        _TA_ORD("foundational", "five_smell", "Order five tastes, then smell working with taste.", ["five", "smell"], _TASTE_BANK, "Tastes, then flavour.", "First the five named on the tongue, then the airborne sense working with them."),
        _TA_PICK("foundational", "taste_ok", "Select five-tastes and taste–smell.", ["five", "smell"], _TASTE_BANK, 2, "Two ideas. No tongue league.", "Choose the five named on the tongue and the airborne sense working with them. Skip a tongue league."),
    ],
    "intermediate": [
        _TA_MCQ("intermediate", "umami", "Umami in this model is", _mcq_opts("a hearing aid", "one of the five tastes", "a private menu", "a canal"), "B", "Fifth taste.", "The savoury fifth is one of the five named in this model, not a hearing aid."),
        _TA_MCQ("intermediate", "alex", "Alex (fictional) with a blocked nose says food is bland. That fits", _mcq_opts("a stored menu", "reduced smell reducing flavour", "ranking Alex", "forced eating"), "B", "Interaction.", "A blocked nose making food seem bland fits a reduced airborne sense reducing flavour."),
        _TA_MCQ("intermediate", "same", "The same yoghurt dyed different colours can be judged differently. That is", _mcq_opts("proof science is a vote only", "a colour/context effect", "a reason to upload menus", "a toughness league"), "B", "Colour.", "The same yoghurt dyed different colours can be judged differently. That is a colour and surrounding-situation effect."),
        _TA_MCQ("intermediate", "iv", "If colour is the independent variable, a control might be", _mcq_opts("forcing everyone to eat", "the same yoghurt base and the same temperature", "storing menus", "ranking tongues"), "B", "Fair test.", "If colour is what you change, keep the yoghurt base and the temperature the same."),
        _TA_MCQ("intermediate", "sour", "Sour is", _mcq_opts("not in the five", "one of the five tastes in this model", "a retina", "a prescription"), "B", "In the five.", "Sour belongs in the five named in this model, not outside that set."),
        _TA_MCQ("intermediate", "bitter", "Bitter is", _mcq_opts("a glasses file", "one of the five tastes in this model", "a class rank", "a vacuum"), "B", "In the five.", "Bitter also belongs in the five named in this model, not a glasses file."),
        _TA_KEY("intermediate", "flavour_word", "Write the word for the combined taste-and-smell experience named in this lesson.", "flavour", "Flavour.", "One word names the combined tongue-and-airborne experience in this lesson."),
        _TA_NUM("intermediate", "zero_force", "How many pupils must eat an unknown food because this quiz says so? Enter 0.", 0, "Zero.", "This quiz forces nobody to eat an unknown food. What number is that?"),
        _TA_ORD("intermediate", "sw_sa", "Order sweet, then salt, as two of the five.", ["sweet", "salt"], _FIVE_BANK, "Two of five.", "Put sweet first, then salt, as two of the five named."),
        _TA_PICK("intermediate", "five_col", "Select sweet and colour/context.", ["sweet", "colour"], _FIVE_BANK, 2, "Taste and context.", "Choose sweet as one of the five, and colour or surrounding situation changing a judgement. Skip a private menu upload."),
    ],
    "difficult": [
        _TA_MCQ("difficult", "jordan", "Jordan (fictional) rates a brown drink as 'cola' and the same clear drink as 'not cola'. A science line is", _mcq_opts("upload Jordan's fridge", "colour/context can steer the judgement", "rank Jordan's tongue", "force an unknown"), "B", "Cues.", "Rating a brown drink as 'cola' and the same clear drink as 'not cola' fits colour and surrounding situation steering the judgement."),
        _TA_MCQ("difficult", "not_five", "Ignoring smell when discussing flavour is", _mcq_opts("required", "an incomplete model in this lesson", "a stored menu", "a hearing test"), "B", "Include smell.", "Ignoring the airborne sense when discussing flavour is an incomplete model in this lesson."),
        _TA_MCQ("difficult", "ethics", "A tasting demo that forces an unknown food is", _mcq_opts("good science in this app", "not what this lesson requires", "a density map", "a canal"), "B", "No force.", "A tasting demo that forces an unknown food is not what this lesson requires."),
        _TA_MCQ("difficult", "five2", "Sweet, salt, sour, bitter and umami are", _mcq_opts("two tastes", "the five tastes in this S2 set", "ear regions", "prescriptions"), "B", "Five.", "Those five named items are the teaching set in this S2 model, not two and not ear regions."),
        _TA_MCQ("difficult", "app", "This app", _mcq_opts("stores private menus", "does not store menus or rank tongues", "forces eating", "diagnoses"), "B", "No menus.", "This app does not store private menus or rank tongues."),
        _TA_MCQ("difficult", "dv", "The dependent variable in a colour-of-drink demo could be", _mcq_opts("a toughness rank", "the labelled judgement of the drink, recorded as data not as a personal diet file", "whose tongue it is", "a stored fridge"), "B", "Judgement as data.", "The dependent variable could be the labelled judgement of the drink, recorded as data, not as a personal diet file."),
        _TA_KEY("difficult", "umami_word", "Write the word for the savoury fifth taste named in this lesson.", "umami", "Umami.", "One word names the savoury fifth in this lesson's set. It is not salt and not sweet."),
        _TA_NUM("difficult", "five_again", "Enter 5 for the teaching set of tastes.", 5, "Five.", "The prompt already names the size of the teaching set. Enter that number."),
        _TA_ORD("difficult", "col_after", "Order salt as a taste, then colour/context effects.", ["salt", "colour"], _FIVE_BANK, "Taste, then cues.", "First salt as one of the five, then colour or surrounding situation as a cue that can change a judgement."),
        _TA_PICK("difficult", "taste_not", "Select the two items that do not belong.", ["rank_tongue", "force_eat"], _TASTE_BANK, 2, "No ranking; no forced eating.", "Choose ranking tongues and forcing unknown foods. Those do not belong."),
    ],
}

_TA_STANDARD = {
    "foundational": (
        'taste_foundational_mcq_block',
        'taste_foundational_keyword_taste_word',
        'taste_foundational_number_five_n',
        'taste_foundational_order_five_smell',
        'taste_foundational_pick_taste_ok',
    ),
    "intermediate": (
        'taste_intermediate_mcq_alex',
        'taste_intermediate_keyword_flavour_word',
        'taste_intermediate_number_zero_force',
        'taste_intermediate_order_sw_sa',
        'taste_intermediate_pick_five_col',
    ),
    "difficult": (
        'taste_difficult_mcq_app',
        'taste_difficult_keyword_umami_word',
        'taste_difficult_number_five_again',
        'taste_difficult_order_col_after',
        'taste_difficult_pick_taste_not',
    ),
}
eursc_science_taste, eursc_science_taste_variants = bind_eursc_topic('taste', _TA_POOLS, _TA_STANDARD)

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
        _PR_MCQ("foundational", "prop", "Proprioception is", _mcq_opts("a food group", "sensing body position without looking", "a glasses league", "a stored dizziness file"), "B", "Position sense.", "This sense is knowing limb position without looking, not a food group."),
        _PR_MCQ("foundational", "bal", "Balance is", _mcq_opts("a vaccination record", "keeping the body oriented against a fall", "ranking who is least dizzy", "a private map"), "B", "Orientation.", "This idea is keeping oriented against a fall, not a vaccination record and not a dizziness league."),
        _PR_MCQ("foundational", "canal", "Semicircular canals detect", _mcq_opts("only tastes", "rotation of the head in this model", "a menu", "whose score to publish"), "B", "Rotation.", "The fluid-filled loops detect rotation of the head in this model, not tastes."),
        _PR_MCQ("foundational", "three", "This lesson models how many canal loops in the sketch?", _mcq_opts("one", "three", "eighty", "zero"), "B", "Three.", "Count the loops in the sketch. The model is a small number of loops, not eighty."),
        _PR_MCQ("foundational", "look", "Knowing an arm is raised without looking fits", _mcq_opts("a stored clinical file", "proprioception", "a tongue rank", "forced spinning"), "B", "Proprioception.", "Knowing an arm is raised without looking fits the position sense, not a stored clinical file."),
        _PR_MCQ("foundational", "a_letter", "<p>Which letter is one canal loop?</p>" + str(canal_boxes(title="Canal A")), _mcq_opts("none of them", "A", "a pupil name", "a menu"), "B", "A is a loop.", "Match the letter to one fluid-filled loop on the sketch, not a pupil name."),
        _PR_KEY("foundational", "bal_word", "Write the word for keeping oriented against a fall.", "balance", "Balance.", "One word names keeping oriented against a fall. It is not a vaccination record."),
        _PR_NUM("foundational", "canals3", "Enter the number of semicircular canals in this lesson's sketch.", 3, "Three.", "Count the loops drawn in this lesson's sketch."),
        _PR_ORD("foundational", "pos_bal", "Order proprioception as position, then balance.", ["position", "balance"], _PROP_BANK, "Position, then balance.", "First sensing position without looking, then keeping oriented against a fall."),
        _PR_PICK("foundational", "prop_ok", "Select position sense and canals-detect-rotation.", ["position", "canals"], _PROP_BANK, 2, "Two ideas. No dizziness league.", "Choose sensing position without looking, and loops detecting rotation. Skip a dizziness league."),
    ],
    "intermediate": [
        _PR_MCQ("intermediate", "together", "Canals, vision and proprioception", _mcq_opts("never interact", "work together in this model", "must be ranked", "are stored as who felt dizzy"), "B", "Together.", "The loops, seeing, and position sense work together in this model. They are not stored as who felt unwell."),
        _PR_MCQ("intermediate", "eyes", "Closing the eyes can make standing on one foot harder because", _mcq_opts("taste vanishes", "vision often helps balance", "the quiz stores dizziness", "canals become food"), "B", "Vision helps.", "Closing the eyes can make standing on one foot harder because seeing often helps staying oriented."),
        _PR_MCQ("intermediate", "alex", "Alex (fictional) can touch their nose with eyes closed. That fits", _mcq_opts("a stored file", "proprioception", "ranking Alex", "forced spinning"), "B", "Position sense.", "Touching a nose with eyes closed fits the position sense, not a stored file."),
        _PR_MCQ("intermediate", "spin", "A teacher-approved slow turn can show canals at work. The quiz still", _mcq_opts("must spin pupils until unwell", "does not require spinning anyone unwell and does not store who felt dizzy", "ranks dizziness", "uploads a map"), "B", "No forced illness.", "A slow turn can show the loops at work. The quiz still does not require spinning anyone unwell."),
        _PR_MCQ("intermediate", "planes", "Three canals in different orientations help detect", _mcq_opts("menus", "rotation in more than one plane", "a tongue rank", "a glasses file"), "B", "Planes.", "Three loops in different orientations help detect rotation in more than one plane."),
        _PR_MCQ("intermediate", "b_letter", "<p>Which letter is the middle canal loop?</p>" + str(canal_boxes(title="Canal B")), _mcq_opts("A", "B", "a handle", "a rank"), "B", "B is the middle loop.", "Match the letter to the middle loop on the sketch, not a handle."),
        _PR_KEY("intermediate", "canal_word", "Write the word for a fluid-filled loop that detects head rotation (one token).", "canal", "Canal.", "One token names a fluid-filled loop that detects head rotation."),
        _PR_NUM("intermediate", "systems3", "Canals, vision and proprioception are how many cooperating ideas here?", 3, "Three.", "Count the cooperating ideas: loops, seeing, and position sense."),
        _PR_ORD("intermediate", "vis_tog", "Order vision helping balance, then the three working together.", ["vision", "together"], _TOGETHER_BANK, "Vision, then together.", "First seeing helping orientation, then the three ideas working together."),
        _PR_PICK("intermediate", "tog_ok", "Select vision-helps and working-together.", ["vision", "together"], _TOGETHER_BANK, 2, "Two ideas.", "Choose seeing helping orientation, and the three working together. Skip forced spinning."),
    ],
    "difficult": [
        _PR_MCQ("difficult", "mismatch", "If vision and canals disagree, a person may feel odd. That is", _mcq_opts("a reason to store who felt dizzy here", "a cue mismatch in the model, not a class league", "a menu", "forced spinning"), "B", "Mismatch.", "If seeing and the loops disagree, a person may feel odd. That is a cue mismatch in the model, not a class league."),
        _PR_MCQ("difficult", "not_rank", "Ranking who is least dizzy is", _mcq_opts("the aim of this quiz", "a misuse of the lesson", "required SI", "a taste"), "B", "No ranking.", "Ranking who is least unwell is a misuse of the lesson, not the aim of this quiz."),
        _PR_MCQ("difficult", "jordan", "Jordan (fictional) sways when asked to stand still with eyes closed. A science line is", _mcq_opts("publish Jordan's file", "vision often helps; this is not a stored clinical test", "rank Jordan", "spin Jordan until unwell"), "B", "Vision + balance.", "Swaying with eyes closed fits seeing often helping orientation. This is not a stored clinical test."),
        _PR_MCQ("difficult", "prop2", "Without looking, knowing a joint angle fits", _mcq_opts("a stored map", "proprioception", "umami", "an advert"), "B", "Proprioception.", "Without looking, knowing a joint angle fits the position sense, not a stored map."),
        _PR_MCQ("difficult", "app", "This app", _mcq_opts("stores who felt dizzy", "does not store dizziness reports or force spinning", "ranks the class", "replaces the teacher"), "B", "No reports.", "This app does not store unwellness reports or force spinning."),
        _PR_MCQ("difficult", "c_letter", "<p>Which letter is the right-hand canal loop?</p>" + str(canal_boxes(title="Canal C")), _mcq_opts("A", "C", "B", "a handle"), "B", "C is the right loop.", "Find the letter that marks the right-hand loop on the sketch, not a handle."),
        _PR_KEY("difficult", "prop_word", "Write the word for sensing body position without looking.", "proprioception", "Proprioception.", "One long word names sensing limb position without looking. It is not the word for staying oriented against a fall."),
        _PR_NUM("difficult", "zero_dizzy", "How many dizziness files should this quiz store? Enter 0.", 0, "Zero.", "This quiz should store no unwellness files. What number is that?"),
        _PR_ORD("difficult", "pos_can", "Order position sense, then canals detecting rotation.", ["position", "canals"], _PROP_BANK, "Then canals.", "First sensing position without looking, then loops detecting rotation."),
        _PR_PICK("difficult", "tog_not", "Select the two items that do not belong.", ["spin_force", "spy_dizzy"], _TOGETHER_BANK, 2, "No forced spinning; no dizziness file.", "Choose spinning until unwell, and storing who felt unwell. Those do not belong."),
    ],
}

_PR_STANDARD = {
    "foundational": (
        'proprioception_balance_foundational_mcq_a_letter',
        'proprioception_balance_foundational_keyword_bal_word',
        'proprioception_balance_foundational_number_canals3',
        'proprioception_balance_foundational_order_pos_bal',
        'proprioception_balance_foundational_pick_prop_ok',
    ),
    "intermediate": (
        'proprioception_balance_intermediate_mcq_alex',
        'proprioception_balance_intermediate_keyword_canal_word',
        'proprioception_balance_intermediate_number_systems3',
        'proprioception_balance_intermediate_order_vis_tog',
        'proprioception_balance_intermediate_pick_tog_ok',
    ),
    "difficult": (
        'proprioception_balance_difficult_mcq_app',
        'proprioception_balance_difficult_keyword_prop_word',
        'proprioception_balance_difficult_number_zero_dizzy',
        'proprioception_balance_difficult_order_pos_can',
        'proprioception_balance_difficult_pick_tog_not',
    ),
}
eursc_science_proprioception_balance, eursc_science_proprioception_balance_variants = bind_eursc_topic(
    'proprioception_balance', _PR_POOLS, _PR_STANDARD
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
        _IN_MCQ("foundational", "what", "Interoception is", _mcq_opts("ranking classmates", "sensing internal states such as hunger or heartbeat", "a glasses league", "a stored mood diary"), "B", "Internal sense.", "This sense is about internal states in a third-person model, such as a need-for-food signal or a heartbeat example, not a classmate ranking."),
        _IN_MCQ("foundational", "hunger", "Hunger in this lesson is", _mcq_opts("a class confession", "an example of an internal signal, not a demand to log meals", "a canal rank", "a prescription file"), "B", "Example, no log.", "The need-for-food idea is an example of an internal signal, not a demand to log meals."),
        _IN_MCQ("foundational", "heart", "A heartbeat the person can notice is", _mcq_opts("a public league", "an internal signal in this model, not a stored ECG", "a tongue rank", "a forced spin"), "B", "Signal, no ECG.", "A heartbeat a fictional person can notice is an internal signal in this model, not a stored ECG."),
        _IN_MCQ("foundational", "interpret", "The same signal", _mcq_opts("has only one meaning forever", "can be interpreted in more than one way", "must be a mood ranking", "is a joke only"), "B", "Interpretation.", "The same internal signal can be read in more than one way. It is not a mood ranking."),
        _IN_MCQ("foundational", "not_ask", "This quiz", _mcq_opts("collects how each pupil feels right now", "does not collect how a pupil feels right now", "diagnoses", "ranks moods"), "B", "No survey.", "This quiz does not collect live feelings from anyone in the room."),
        _IN_MCQ("foundational", "signpost", "Personal distress belongs with", _mcq_opts("this generator as a clinic", "a trusted adult or qualified help; this app does not diagnose", "a mood league", "a joke"), "B", "Signpost.", "Personal distress belongs with a trusted adult or qualified help. This app does not diagnose."),
        _IN_KEY("foundational", "hunger_word", "Write the word for the internal signal that food is needed, used as an example here.", "hunger", "Hunger.", "One word names the internal signal that food is needed, used as a teaching example, not a meal log."),
        _IN_NUM("foundational", "zero_mood", "How many live mood surveys should this quiz run? Enter 0.", 0, "Zero.", "This quiz should run no live mood surveys. What number is that?"),
        _IN_ORD("foundational", "int_int", "Order internal sensing, then interpretation can vary.", ["internal", "interpret"], _INT_BANK, "Sense, then interpret.", "First sensing internal states in the model, then the idea that interpretation can vary."),
        _IN_PICK("foundational", "int_ok", "Select internal sensing and variable interpretation.", ["internal", "interpret"], _INT_BANK, 2, "Two ideas. No live survey.", "Choose sensing internal states and variable interpretation. Skip a live survey of the room."),
    ],
    "intermediate": [
        _IN_MCQ("intermediate", "alex", "Alex (fictional) notices a fast heartbeat after a run and after a scare. A science line is", _mcq_opts("store Alex's feelings", "the same kind of signal can be read in more than one context", "rank Alex", "diagnose Alex here"), "B", "Context.", "Alex notices a fast heartbeat after a run and after a scare. The same kind of signal can be read in more than one situation."),
        _IN_MCQ("intermediate", "thirst", "Thirst is used here as", _mcq_opts("a confession", "another internal example, not a demand to log drinks", "a hearing test", "a league"), "B", "Example.", "The need-for-drink idea is another internal example, not a demand to log drinks."),
        _IN_MCQ("intermediate", "well", "Wellbeing in this lesson is", _mcq_opts("a mood ranking of the class", "an idea linked to how signals are interpreted, without a survey", "a stored diary", "a joke"), "B", "Idea, no survey.", "Wellbeing here is an idea linked to how signals are interpreted, without a survey of the class."),
        _IN_MCQ("intermediate", "not_joke", "Treating internal signals as only a joke is", _mcq_opts("required", "a poor fit for this lesson", "a canal fact", "an SI unit"), "B", "Not a joke.", "Treating internal signals as only a joke is a poor fit for this lesson."),
        _IN_MCQ("intermediate", "app", "This app", _mcq_opts("diagnoses anxiety from a story", "does not diagnose; it teaches the idea and signposts help", "ranks moods", "collects live feelings"), "B", "No diagnosis.", "This app does not diagnose. It teaches the idea and signposts help."),
        _IN_MCQ("intermediate", "sam", "Sam (fictional) is in distress in a scenario. The next step in the lesson is", _mcq_opts("publish Sam in a league", "signpost a trusted adult; do not collect a diary here", "ignore it as a joke", "store a heartbeat file"), "B", "Signpost.", "If Sam is in distress in a scenario, signpost a trusted adult. Do not collect a diary here."),
        _IN_KEY("intermediate", "thirst_word", "Write the word for the internal signal that drink is needed, used as an example here.", "thirst", "Thirst.", "One word names the internal signal that drink is needed, used as a teaching example, not a drinks log."),
        _IN_NUM("intermediate", "two_ex", "Hunger and thirst are how many example signals named here?", 2, "Two.", "Count the two named example signals: need-for-food and need-for-drink."),
        _IN_ORD("intermediate", "well_sig", "Order wellbeing as interpretation, then signposting qualified help.", ["wellbeing", "signpost"], _WELL_BANK, "Idea, then signpost.", "First wellbeing as an interpretation idea, then signposting qualified help."),
        _IN_PICK("intermediate", "well_ok", "Select wellbeing-as-idea and signposting.", ["wellbeing", "signpost"], _WELL_BANK, 2, "Two ideas. No mood rank.", "Choose wellbeing as an idea and signposting qualified help. Skip a mood ranking of the class."),
    ],
    "difficult": [
        _IN_MCQ("difficult", "jordan", "Jordan (fictional) reads a fast heartbeat as 'excited' in one story and 'worried' in another. That fits", _mcq_opts("a stored diagnosis", "interpretation of the same kind of signal", "a tongue rank", "a live class survey"), "B", "Interpretation.", "Jordan reads a fast heartbeat as 'excited' in one story and 'worried' in another. That fits interpretation of the same kind of signal."),
        _IN_MCQ("difficult", "not_ecg", "A heartbeat example is", _mcq_opts("an ECG stored for each pupil", "a teaching case, not a medical record", "a ranking", "a forced confession"), "B", "Teaching case.", "A heartbeat example is a teaching case, not a medical record stored for each pupil."),
        _IN_MCQ("difficult", "limit", "Limits of this lesson include", _mcq_opts("that it diagnoses the class", "that it does not collect live feelings or replace a clinician", "that jokes replace support", "that moods must be compared"), "B", "Limits.", "Limits include that the lesson does not collect live feelings or replace a clinician."),
        _IN_MCQ("difficult", "both", "Hunger and heartbeat both", _mcq_opts("must be logged from each pupil", "are internal examples without a personal log here", "are tastes", "are canals only"), "B", "Examples.", "Need-for-food and a heartbeat example are both internal examples without a personal log here."),
        _IN_MCQ("difficult", "misuse", "A misuse of interoception teaching is", _mcq_opts("using a fictional case", "running a live mood survey in the quiz", "signposting help", "saying interpretation can vary"), "B", "No live survey.", "A misuse is running a live mood survey in the quiz. A fictional case is allowed."),
        _IN_MCQ("difficult", "help", "Qualified help is", _mcq_opts("this app", "outside the app: teacher signpost, trusted adult, health professional", "a league", "a joke"), "B", "Outside.", "Qualified help is outside the app: a teacher signpost, a trusted adult, or a health professional."),
        _IN_KEY("difficult", "intero_word", "Write the word for sensing internal bodily states.", "interoception", "Interoception.", "One long word names sensing internal states in a third-person model. It is not the need-for-food example itself."),
        _IN_NUM("difficult", "zero_feel", "How many live feeling-survey items should this quiz ask a pupil? Enter 0.", 0, "Zero.", "This quiz should ask no live feeling-survey items. What number is that?"),
        _IN_ORD("difficult", "int2", "Order internal sensing, then variable interpretation.", ["internal", "interpret"], _INT_BANK, "Again.", "Same chain as before: sensing internal states first, then variable interpretation."),
        _IN_PICK("difficult", "well_not", "Select the two items that do not belong.", ["rank_mood", "diagnose"], _WELL_BANK, 2, "No mood rank; no diagnosis.", "Choose comparing moods in the quiz, and this app diagnosing from a story. Those do not belong."),
    ],
}

_IN_STANDARD = {
    "foundational": (
        'interoception_foundational_mcq_heart',
        'interoception_foundational_keyword_hunger_word',
        'interoception_foundational_number_zero_mood',
        'interoception_foundational_order_int_int',
        'interoception_foundational_pick_int_ok',
    ),
    "intermediate": (
        'interoception_intermediate_mcq_alex',
        'interoception_intermediate_keyword_thirst_word',
        'interoception_intermediate_number_two_ex',
        'interoception_intermediate_order_well_sig',
        'interoception_intermediate_pick_well_ok',
    ),
    "difficult": (
        'interoception_difficult_mcq_both',
        'interoception_difficult_keyword_intero_word',
        'interoception_difficult_number_zero_feel',
        'interoception_difficult_order_int2',
        'interoception_difficult_pick_well_not',
    ),
}
eursc_science_interoception, eursc_science_interoception_variants = bind_eursc_topic(
    'interoception', _IN_POOLS, _IN_STANDARD
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
        _NH_MCQ("foundational", "uv", "UV sensing is modelled as", _mcq_opts("a pupil superpower league", "detecting light humans do not see the same way", "a stored mood", "a menu"), "B", "Different band.", "UV sensing is detecting light humans do not see the same way, not a pupil superpower league."),
        _NH_MCQ("foundational", "ir", "Infrared sensing in an animal example is", _mcq_opts("a joke only", "a heat-related signal humans do not see the same way", "a glasses rank", "a forced spin"), "B", "IR.", "Infrared in an animal example is a heat-related signal humans do not see the same way, not a joke."),
        _NH_MCQ("foundational", "echo", "Echolocation uses", _mcq_opts("a private diary", "returning sound to locate objects", "a tongue league", "a prescription"), "B", "Returning sound.", "This locating method uses returning sound to find objects, not a private diary."),
        _NH_MCQ("foundational", "ultra", "Ultrasound in this model is", _mcq_opts("a food", "sound above the usual human hearing band", "a retina file", "a superpower rank"), "B", "Above human band.", "This is sound above the usual human hearing band, not a food."),
        _NH_MCQ("foundational", "tech", "A sensor that detects a chemical", _mcq_opts("cannot be compared to a sense", "uses the same idea: detect a signal", "ranks pupils", "stores moods"), "B", "Signal.", "A lab sensor that detects a chemical uses the same idea as a sense: detect a signal."),
        _NH_MCQ("foundational", "not_super", "This quiz", _mcq_opts("ranks which pupil has a superpower", "does not rank pupils as having animal superpowers", "diagnoses", "stores who echolocates"), "B", "No superpower league.", "This quiz does not rank pupils as having animal superpowers."),
        _NH_KEY("foundational", "echo_word", "Write the word for locating objects using returning sound.", "echolocation", "Echolocation.", "One word names locating objects using returning sound. It is not a diary."),
        _NH_NUM("foundational", "bands2", "UV and IR are how many extra light-related bands named here?", 2, "Two.", "Count the extra light-related bands named: UV and infrared."),
        _NH_ORD("foundational", "uv_echo", "Order UV sensing, then echolocation.", ["uv", "echo"], _NH_BANK, "Light band, then sound.", "First a light band humans do not see the same way, then locating with returning sound."),
        _NH_PICK("foundational", "nh_ok", "Select UV sensing and echolocation.", ["uv", "echo"], _NH_BANK, 2, "Two adaptations. No superpower rank.", "Choose UV sensing and locating with returning sound. Skip ranking pupils as having superpowers."),
    ],
    "intermediate": [
        _NH_MCQ("intermediate", "polar", "Polarised-light sensing is", _mcq_opts("a menu", "a cue some animals use in the public model", "a pupil league", "a stored ECG"), "B", "Polarisation cue.", "Polarised-light sensing is a cue some animals use in the public model, not a pupil league."),
        _NH_MCQ("intermediate", "em", "Electromagnetic sensing in this lesson is", _mcq_opts("a spell", "a scientific model of detecting electric or magnetic cues", "a tongue rank", "forced spinning"), "B", "Model, not magic.", "Electromagnetic sensing here is a scientific model of detecting electric or magnetic cues, not a spell."),
        _NH_MCQ("intermediate", "infra", "Infrasound is modelled as", _mcq_opts("a taste", "sound below the usual human hearing band", "a glasses file", "a mood survey"), "B", "Below band.", "This is sound below the usual human hearing band, not a taste."),
        _NH_MCQ("intermediate", "chem", "A dog's chemical sense and a lab sensor both", _mcq_opts("rank pupils", "detect a chemical signal in this comparison", "store diaries", "are superpower leagues"), "B", "Same idea.", "A dog's chemical sense and a lab sensor both detect a chemical signal in this comparison."),
        _NH_MCQ("intermediate", "alex", "Alex (fictional) claims a classmate can see UV. A science reply is", _mcq_opts("rank the classmate", "humans do not see UV the same way; do not invent a superpower league", "store a file", "diagnose"), "B", "No league.", "Humans do not see UV the same way. Do not invent a superpower league about a classmate."),
        _NH_MCQ("intermediate", "bat", "A bat example of echolocation is", _mcq_opts("a stored clinical test", "returning sound as a locating tool", "a menu", "a prescription"), "B", "Echo.", "A bat example uses returning sound as a locating tool, not a stored clinical test."),
        _NH_KEY("intermediate", "ultra_word", "Write the word for sound above the usual human hearing band in this lesson.", "ultrasound", "Ultrasound.", "One word names sound above the usual human hearing band in this lesson."),
        _NH_NUM("intermediate", "zero_super", "How many pupil-superpower ranks should this quiz keep? Enter 0.", 0, "Zero.", "This quiz should keep no pupil-superpower ranks. What number is that?"),
        _NH_ORD("intermediate", "polar_em", "Order polarised-light cue, then electromagnetic sensing.", ["polar", "em"], _TECH_BANK, "Light cue, then EM.", "First polarised light as a cue, then detecting electric or magnetic cues."),
        _NH_PICK("intermediate", "tech_ok", "Select polarised light and ultrasound.", ["polar", "ultra"], _TECH_BANK, 2, "Two ideas.", "Choose polarised light as a cue, and sound above the usual human hearing band. Skip spells and superpower ranks."),
    ],
    "difficult": [
        _NH_MCQ("difficult", "ir2", "A pit-organ style IR example is best called", _mcq_opts("a pupil superpower", "an adaptation to a heat-related signal", "a mood file", "a forced sniff"), "B", "Adaptation.", "A pit-organ style infrared example is best called an adaptation to a heat-related signal, not a pupil superpower."),
        _NH_MCQ("difficult", "not_magic", "Calling nonhuman senses spells is wrong because", _mcq_opts("spells are SI units", "they are models of detecting signals that can be studied", "pupils must be ranked", "the app stores who has which sense"), "B", "Signals.", "Calling nonhuman senses spells is wrong because they are models of detecting signals that can be studied."),
        _NH_MCQ("difficult", "both_sound", "Infrasound and ultrasound both", _mcq_opts("are tastes", "sit outside the usual human hearing band in this model", "rank classmates", "are prescriptions"), "B", "Outside the band.", "Sound below the usual band and sound above it both sit outside the usual human hearing band in this model."),
        _NH_MCQ("difficult", "tech2", "Technology can extend detection because", _mcq_opts("sensors replace all ethics", "a device can detect a signal a human sense does not", "pupils become bats in the quiz", "moods are stored"), "B", "Extend detection.", "Technology can extend detection because a device can detect a signal a human sense does not."),
        _NH_MCQ("difficult", "jordan", "Jordan (fictional) wants a league of 'who is most like a shark'. The lesson says", _mcq_opts("publish the league", "do not rank pupils; study animal models and instruments", "store files", "force spinning"), "B", "No league.", "A league of 'who is most like a shark' is not the lesson. Study animal models and instruments instead."),
        _NH_MCQ("difficult", "uv_ir", "UV and IR both", _mcq_opts("are umami", "are light-related bands humans do not use the same way", "are canals", "are menus"), "B", "Bands.", "UV and infrared are both light-related bands humans do not use the same way."),
        _NH_KEY("difficult", "infra_word", "Write the word for sound below the usual human hearing band in this lesson.", "infrasound", "Infrasound.", "One word names sound below the usual human hearing band in this lesson. It is not the above-band word."),
        _NH_NUM("difficult", "echo1", "Echolocation uses returning sound. Enter 1 if that is the lesson model.", 1, "One: returning sound.", "If locating with returning sound is the lesson model, enter 1."),
        _NH_ORD("difficult", "uv_ir_ord", "Order UV sensing, then infrared sensing.", ["uv", "ir"], _NH_BANK, "Two bands.", "First UV sensing, then infrared as a heat-related signal. Two light-related bands."),
        _NH_PICK("difficult", "tech_not", "Select the two items that do not belong.", ["magic", "rank_tech"], _TECH_BANK, 2, "Not spells; no superpower rank.", "Choose treating nonhuman senses as spells, and ranking which pupil has a superpower. Those do not belong."),
    ],
}

_NH_STANDARD = {
    "foundational": (
        'nonhuman_senses_foundational_mcq_echo',
        'nonhuman_senses_foundational_keyword_echo_word',
        'nonhuman_senses_foundational_number_bands2',
        'nonhuman_senses_foundational_order_uv_echo',
        'nonhuman_senses_foundational_pick_nh_ok',
    ),
    "intermediate": (
        'nonhuman_senses_intermediate_mcq_alex',
        'nonhuman_senses_intermediate_keyword_ultra_word',
        'nonhuman_senses_intermediate_number_zero_super',
        'nonhuman_senses_intermediate_order_polar_em',
        'nonhuman_senses_intermediate_pick_tech_ok',
    ),
    "difficult": (
        'nonhuman_senses_difficult_mcq_both_sound',
        'nonhuman_senses_difficult_keyword_infra_word',
        'nonhuman_senses_difficult_number_echo1',
        'nonhuman_senses_difficult_order_uv_ir_ord',
        'nonhuman_senses_difficult_pick_tech_not',
    ),
}
eursc_science_nonhuman_senses, eursc_science_nonhuman_senses_variants = bind_eursc_topic(
    'nonhuman_senses', _NH_POOLS, _NH_STANDARD
)
