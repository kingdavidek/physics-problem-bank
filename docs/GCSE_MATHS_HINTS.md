# GCSE Maths hints after a wrong answer (plan)

**Goal:** when a pupil types or picks a wrong answer in GCSE maths, point at the likely slip (misconception diagnosis) instead of a bare "Not quite", and when no slip is recognised, offer a graded hint ladder: a nudge, then a stronger hint, then the worked solution.
**Status:** planned 2026-10-24 on `1bd6362` plus the uncommitted verification leftovers (left intact). **Phase 1 built and independently reviewed 2026-10-24, not committed** (build notes in section 13, review notes in section 14). **Phase 2 built and independently reviewed 2026-10-26, not committed** (build notes in section 15, review notes in section 16). **Phase 3 built and independently reviewed 2026-10-26, not committed** (build notes in section 17, review notes in section 18). **Phase 5 built and independently reviewed 2026-10-26, not committed** (build notes in section 21, review notes in section 22; the 60% slot-coverage target is not met: 41.1% of practice slots have a topic rule). Phase 6 (teacher-visible "things to revisit") was side-lined by David on 2026-10-26 (see section 10, Phase 6); nothing for it is built or stored. Decisions D1 to D8 were settled by David on 2026-10-24 (section 11). **Phase 4 built and independently reviewed 2026-10-26, not committed** (build notes in section 19, review notes in section 20). **Phase 5b (wider topic rules) and three small fixes built and independently reviewed 2026-10-27, not committed** (build notes in section 23, review notes in section 24; after the review 640 of 1,072 practice slots (59.7%) have a topic rule, 4 slots short of the 60% target; **Phase 5c (2026-10-27, section 25) closed the gap: 657 of 1,072, 61.3%; independently reviewed the same day, count unchanged, see "§25 review notes"**).
**Pipeline per phase (as for the verification track):** implementer builds, an independent reviewer checks against this doc and the code, fixes, sync to David's laptop, full smoke suite green. One commit per phase, only when David asks.

---

## 1. Where things stand (measured 2026-10-24)

| Area | What the code does today |
|---|---|
| Typed answers | `POST /api/v1/problems/check` (`app.py`, about line 7224) grades against the session problem (`session['last_problem_payload']`) through `check_answer(type, raw, user, form=, subject=, labels=, prereqs=)` and returns `{'ok': True, **result}`. `result` is `correct`, `normalized_user`, `normalized_correct`, `feedback`, and `wrong_form` for the form rules. |
| Feedback strings | 52 "Not quite" strings in `generators/shared/answer_checkers.py`, most of them in the style "Not quite, em dash, check your working.". Kind exceptions: `_WRONG_FORM_FEEDBACK` ("That's equal, but the question asks you to expand it."), the wrong-letter message in `check_formula_fraction`, `_RECURRING_FEEDBACK` for probabilities. |
| Front end | `static/js/site.js` (207,046 B, `?v=34`, no byte cap) puts `data.feedback` into `.free-response-feedback` with `textContent`, prefixed by a cross glyph, colour `var(--on-wrong)`; fallback "Not quite, em dash, try again.". A per-problem `answer_wrong_hint` (only used by `functions.py` for fraction brackets) is appended. |
| Attempts | Practice allows unlimited retries; only the first attempt is recorded (`freeResponsePersisted`). Set work (`models/class_assignments.py`) allows one answer per question (`already_answered`) and reveals the key afterwards. Lesson quizzes take one answer per question with no per-question feedback, then a results page with everything revealed. |
| Hints and solutions | Practice shows a "Hint" drawer (`problem.hint`, one string per problem) and a "Show answer" drawer (`problem.solution`) that are **always open to the pupil**, before any attempt. No generator has step-level hints. |
| MCQ (practice) | Checked in the browser against `data-correct` in the DOM; a wrong pick highlights the right option with "Not quite, em dash, the correct answer is highlighted." Persistence goes to `POST /api/v1/generator/mcq-answer`, which is login-only. |
| Zorp | `pbCelebrate.wrong` plays the soft sound and `reactMascot('wrong')`, which resolves to `oops-encourage` (then `determined` or `soft-smile`), never a negative preset (`models/zorp_rig.py` `CONTEXT_MAP`). Feedback text is system voice: `scripts/test_zorp_voice_smoke.py` asserts Zorp never speaks in grading feedback. |
| Voice lint | `models/zorp_voice.py` extracts site.js feedback strings only; dashes and emoji in system strings are `info`, not errors. `answer_checkers.py` strings are not extracted at all. The banned list already includes "you forgot", "failed", "easy", "simply", "obviously". |
| Recorded inputs | `generators/shared/verify_hook.record(family, **inputs)` is called once per variant (437 distinct families; 1,072 of 1,072 practice slots). It is a **no-op in production**: inputs exist only while the verification test holds a sink. The presence guard means every numeric input is visible in the question text. |
| Storage of answers | `_track_mcq_answered` already stores each first attempt (typed text and key) in `generator_mcq_attempts` and as a followers-visible activity event; cohort stats store anonymous per-question samples. Wrong-answer reflections ("What tripped you up?") are stored only when the pupil saves one. |
| Budgets | CSS 237,078 of 246,000 B total, core 212,086 of 216,000 B (3,914 B headroom). `sw.js` `CACHE_VERSION = 'pb-v105'`. Session cookie (signed, zlib-compressed, not encrypted) with a GCSE maths problem: median 624 B, p90 1,707 B, max 2,418 B of about 4,093 B. |

Typed-answer shape of the 1,072 practice slots: 474 single-value numeric slots (number, fraction, bearing, surd, standard form, pi multiple), 251 `number_fields` multipart slots, the rest algebraic, linear, roots, proofs and others. Single-value slots are concentrated in probability (45), mensuration (44), number (37), compound measures (32), bearings (32), sequences (30), statistics (27), trigonometry (27), geometry angles (24), ratio (22) and decimals (21).

---

## 2. Design in one paragraph

A new server-side module, `generators/shared/misconceptions.py`, holds a catalogue of misconception rules keyed by answer family (the `record()` family) plus a small set of key-only generic rules that need no inputs. Each rule computes a candidate wrong value. After a wrong typed answer, `diagnose()` compares the pupil's value with every candidate for that problem and returns a message only when exactly one message matches (exact or rounding-aware), the candidate is not itself accepted by the checker, and no other rule with a different message lands on the same value. Otherwise the response carries the next rung of a hint ladder. To make recorded inputs available at check time, a capture wrapper around the GCSE maths topic generators stores a compact `answer_record` (family and inputs, at most 256 B) on the problem as a server-only key. MCQ distractors gain notes keyed by option text, and the verification framework confirms that each tagged distractor equals its rule's value. Nothing new is stored about the pupil in Phases 1 to 5: no misconception id reaches a database row, an activity event, cohort stats or a log. David has asked for per-pupil labels visible to teachers (D2); that is Phase 6, it is not built, and it changes this sentence (section 10).

---

## 3. Architecture

### 3.1 The rule catalogue (`generators/shared/misconceptions.py`)

```python
@dataclass(frozen=True)
class Rule:
    id: str                    # 'pyth.no_sqrt', 'mens.diameter_as_radius', 'gen.sign'
    families: tuple            # record() families it applies to; () for a generic key-only rule
    message: str               # id into MESSAGES (several rules may share one message)
    value: Callable            # (inputs, key) -> Fraction | tuple | None  (None: not applicable here)
    match: str = 'numeric'     # 'numeric' | 'angle' | 'pair' | 'roots' | 'bearing'
    when: Callable = None      # optional predicate on inputs (e.g. only when ask == 'hyp')
```

- **`MESSAGES`**: one dict, id to text, the only place copy lives (lintable, reviewable line by line). Messages may use named placeholders filled from recorded inputs only (for example `{pct}`), never from the key.
- **`FAMILY_RULES`**: family to rules. Generic families that appear in many contexts (`quotient` 20 call sites, `arith` 21) get only context-free rules (order of operations, reciprocal); context-specific rules need a context string on the `record()` line (for example `given='diameter'`), which the presence guard allows because it checks numeric inputs only.
- **`GENERIC_RULES`**: key-only rules that work on a numeric slot with no inputs (Phase 1, built): sign flip, a factor of 10, 100 or 1000 either way, rounded to the wrong accuracy (fewer places, or not rounded), truncated instead of rounded, a near miss in the last place (early rounding), reciprocal, a swapped pair (`number_pair`, `vector`), one root only (`quadratic_roots`), and for angle topics 180 minus and 90 minus the key. The built list, with the choices made, is in section 13.
- **`NUDGES`**: family (or topic) to a one-line method nudge for rung 1 of the ladder.
- **Independence:** the rule formulas are deliberately written from the maths, not by calling generator helpers, so a generator bug cannot hide inside a rule.

### 3.2 Getting the inputs to check time

`record()` stays exactly as specified in `docs/GCSE_MATHS_VERIFICATION.md` (no random draws, never changes the problem). Changes:

1. `verify_hook` gains a second `ContextVar` sink and a `capture()` context manager; `record()` appends to whichever sinks are active (the test's `recording()` and the production `capture()` can nest without stealing records from each other).
2. `topic_registry.py` wraps each GCSE maths topic `func` once with `with_answer_record(func)`. The wrapper runs the generator inside `capture()` and, when exactly one record was captured (276 of 288 sampled problems today; graphs and graphical simultaneous equations record twice and are skipped until Phase 5), the family has rules, and the JSON is at most 256 B, it sets `problem['answer_record'] = {'f': family, 'i': inputs}`. Wrapping in the registry covers every call site at once (practice queue, reroll, QOTD, lesson quiz, set-work freezing) instead of editing the six `topic_config['func']` call sites in `app.py`.
3. `answer_record` joins `SERVER_ONLY_KEYS` in `models/class_assignments.py`, so it is stripped on every way out, answered or not. `_problem_client_payload` never copies it. **As built (Phase 2) it is not copied into frozen set work**, because the brief for Phase 2 says it is never stored in a database; see section 15. Phase 3 reopens this if set-work messages are wanted.
4. Pupil output must stay byte-identical: the verification smoke's `no_output_drift` already hashes question, solution, key and options with recording on and off; each phase also diffs generated output against the previous commit (as Phase 1 of the verification track did).

### 3.3 Matching a typed answer (`diagnose(problem, user_answer, result)`)

Runs only when all of these hold: GCSE maths, session-bound problem (never a client-supplied key), `result['correct']` is false, there is no `wrong_form`, and the input parsed as a value (an unparseable answer keeps its "Enter a number" message).

1. Parse the pupil's value with the checker's own parsers (`_parse_fraction_or_number`, mixed numbers, percentages when the form is probability), so diagnosis reads exactly what the grader read.
2. Build candidates: every applicable family rule (from `answer_record`) plus the generic rules, each giving an exact `Fraction` (or a pair, multiset of roots, or angle mod 360).
3. Drop any candidate the checker accepts (`check_answer(type, raw, str(candidate))` correct), so a rule can never call a right answer a slip.
4. A candidate matches when the pupil's value equals it exactly, or equals it rounded half up (`generators/shared/rounding.py`) to the key's decimal places or to the pupil's own decimal places (at most 6), because a pupil who made the slip will still round as told.
5. Collect the matched message ids. **Exactly one distinct message id: show it. None, or two or more: no diagnosis** (fall through to the ladder). Rules that share a message (for example two routes to the same "check the units" slip) do not count as a collision.
6. `number_fields` parts are diagnosed per part only when the request is the per-part path (`partial_field`), against that part's key; part-specific family rules come in Phase 5.

The result is `{'id': rule_id, 'message': text}`; the route sets `response['feedback'] = message` and `response['hint'] = {'kind': 'misconception'}`. Because the existing JS already shows `data.feedback`, Phase 1 needs no JavaScript change.

### 3.4 What is stored and what is sent

| Data | Where it lives | Reaches the client? |
|---|---|---|
| `answer_record` (family and question inputs) | session cookie problem (practice), lesson-quiz session row, frozen set-work payload | Never in a payload or the DOM. Note: the practice session cookie is signed, not encrypted, and already holds the key; the inputs are numbers already printed in the question (presence guard), so nothing new is exposed. |
| Misconception candidate values | computed at check time, never stored | Never. |
| Matched message | check response, after a wrong answer only | Yes, as `feedback`. |
| Rule id | check response (`hint.id`), for tests and styling | Yes, after the answer; never stored, logged or added to attempts, activity events, cohort stats or reflections. |
| MCQ option notes | problem field `option_notes` (server-only key) | Only the note for the option the pupil picked, after the pick. |
| Ladder content | computed at check time from `hint`, `NUDGES` and the stored solution | Rung text after a wrong attempt only. |

**Leak rules by surface.** Practice already sends `correct_answer_raw`, `correct_answer`, `solution_html` and `hint_html` to the browser (`data-correct-raw`, `data-correct`, the Show answer drawer) and returns `normalized_correct` on a wrong check, so practice hints add no new exposure; the hard guarantee matters for **set work** and **lesson quizzes**, where keys are server-side: there, misconception messages and MCQ notes appear only after the single answer is graded (set work) or on the results page (quizzes), and `answer_record` and `option_notes` are in `SERVER_ONLY_KEYS`.

---

## 4. MCQ distractor notes

**Keyed by option text, not letter.** `make_problem` reshuffles options through `_shuffle_mcq`, so letters move after the generator returns. `option_notes = {'<option text>': '<rule id or bank note id>'}` survives any shuffle and costs no random draws.

**Procedural MCQs** (`maths_bank_procedural_mcq.py` and topic files): a tagged variant of the builders, `_letter_opts_tagged(correct, [(value, rule_id), ...], fmt=)` and `_string_opts_tagged`, which walks, dedupes, pads and shuffles exactly as `_letter_opts` and `_string_opts` do (same random calls in the same order) and returns the notes for surviving tagged options. Filler options from the `correct plus or minus offset` padding carry no note. If two tagged candidates format to the same text, the option keeps no note (ambiguous).

**Bank items** (static MCQs in the topic banks): an optional `"why": {"<option text>": "<note id>"}` per item, with note text in a `BANK_NOTES` catalogue beside `MESSAGES` (one place for copy). The item digest (question, sorted options, keyed text) is unchanged by adding `why`, so the new smoke must cover notes itself.

**Delivery.**
- Practice: a new session-bound endpoint `POST /api/v1/problems/option-note` (`{letter}` in, `{note}` out; works for guests, rate-limited like `check`, no storage) read from the session problem after the pick. Logged-in pupils could get it from the `mcq-answer` response instead, but guests would then get nothing.
- Set work and lesson quizzes: the note for the picked option is added to the post-answer response or the results payload, never before.

**Verification (each note's claim is checked where possible).**
- *Rule-tagged procedural options:* the new smoke regenerates each tagged function over seeds with `recording()`, recomputes `rule.value(inputs)` and checks the tagged option text equals it (numeric comparison through `scripts/gcse_verify/core.option_quantity`, not text), that the value differs from the independently re-solved key, and that the option is not equal in value to the key.
- *Bank notes:* where a digest-keyed spec in `scripts/gcse_verify/solvers_bank*.py` re-solves the item (325 of 340 items), the spec may also return the misconception values; such notes count as "verified", the rest as "reviewed" (hand-checked, listed with a reason). The coverage report prints both.

---

## 5. Hint ladder (no specific slip recognised)

**Rungs (D3 settled: the first hint is automatic, the bigger hint is pulled by the pupil; D1 settled: the worked solution comes only after the last rung).**

| Rung | When | Content source |
|---|---|---|
| 1 Nudge | automatic after the first wrong attempt with no recognised slip (a recognised slip replaces the nudge for that attempt) | `NUDGES[family]`, else the problem's own `hint`, else a short line per answer type ("Check each step against the numbers in the question.") |
| 2 Bigger hint | only when the pupil taps "Show a bigger hint", offered under the rung 1 line from the first wrong attempt | the first step of the stored worked solution: split `problem['solution']` on line breaks or `<br>`, take the first step that does not contain the key (written at the key's accuracy or as a fraction); if none qualifies, rung 2 is skipped and the button leads straight to rung 3 |
| 3 Worked solution | only after rung 2 (or the skip above) has been shown: the "Show answer" drawer unlocks and the ladder says so | the existing stored solution |

A recognised misconception replaces the rung 1 text for that attempt (it is the better hint) but the ladder still offers the bigger hint, so a pupil who repeats the same slip still reaches the worked solution.

**Attempt counting: session-only, nothing stored.** The browser keeps the rung per question block (`block.dataset.hintRung`, reset on a new question or reroll) and sends it with the check so the server can build the right text. The server stays stateless about attempts, and no new personal data is created. A pupil could fake the rung, but the practice page already carries the solution (see 5.1), so there is nothing to protect.

**Where the ladder runs.** Practice only (unlimited retries). Set work and lesson quizzes are single-answer, so they show the misconception message (or nothing) after grading, plus the existing reveal; no ladder.

**Interplay with existing UI.** The hint sits directly under the feedback line, above the "What tripped you up?" reflection panel and the cohort line. The existing pre-attempt "Hint" drawer (`problem.hint`, one string) is not part of D1 and stays unless David says otherwise.

### 5.1 D1 in practice: what "Show answer" gating means (for Phase 3)

Today `templates/index.html` renders a `details.answer-reveal` drawer ("Show answer") that is **always open to the pupil**, before any attempt, and the page already carries the solution HTML, the key (`data-correct-raw`) and, on a wrong check, `normalized_correct`. D1 changes the drawer to **locked until the last rung**. What has to change in Phase 3:

- `templates/index.html`: the drawer renders locked (not as an open-able control with no effect: either not rendered until unlock, or `hidden`/`inert`, with the ladder announcing the unlock through an `aria-live` polite region and no focus steal). `static/js/site.js` owns the state (`hintRung`) and `static/css/practice.css` the locked look; `initAnswerRevealMathJax` already typesets on toggle, so unlocked content needs no change there.
- **It is pacing, not security.** Hiding the drawer does not hide what the page and the check response already carry (the key in the DOM, `normalized_correct` after a wrong check, `solution_html` in the markup). Making D1 real on the wire would mean serving the solution from a session-bound endpoint after the last rung, not sending it in the page, and dropping `normalized_correct` from wrong checks, which also breaks the client-side MCQ check. That is a separate, larger decision; Phase 3 proposes pacing only and says so in its notes.
- **Typed practice:** one pupil path = wrong attempt, line 1, tap "Show a bigger hint", then Show answer unlocks. Proposed (to confirm in review, not a decision): the drawer also unlocks once the pupil answers correctly, because the worked method is then a reward and a check, not a shortcut.
- **Practice MCQ:** the browser highlights the right option at once on a pick (it holds `data-correct`), so the key is already shown. There is no ladder. Proposal: the drawer unlocks with the pick, with the D4 note beside the highlight.
- **Quick Test** runs on the same page. Proposal: the misconception line is shown (it is the same system feedback as today's "Not quite"), the bigger-hint ladder is not offered, and Show answer stays locked until the test's own results page (`quicktest_results.html`, which already opens every answer). To confirm in review.
- **Set work: D1 already holds, and stays.** One answer per question; the frozen problem's `solution`, `solution_html`, `hint`, `hint_html` and key are removed on every way out (`_STRIP_KEYS` in `models/class_assignments.py`) until the pupil's single answer is graded, then revealed (`strip_problem_keys(..., reveal=True)`). So "solution after the last rung" means "solution after the answer is graded", as today. Phase 3 adds the misconception message to the graded response, nothing before it.
- **Lesson quizzes:** one answer per question and no per-question feedback; the results page reveals everything, as today. Phase 3 adds the message per question on that page. D1 changes nothing here.
- Other pages with their own drawer (`saved_problem.html`, `shared_question.html`, `suggestion_view.html`, `qotd.html`) are not attempts at a ladder; leave them as they are unless David asks, and say so in the Phase 3 notes.
- **Reload and reroll.** The rung lives in the page only (nothing stored), so reloading the page or rerolling the question starts the ladder again with the drawer locked. That is the intended trade-off for storing nothing; say so in the Phase 3 notes.
- **To confirm with David before Phase 3 (proposals above, not decisions):** (a) the drawer unlocks on a correct answer; (b) practice MCQ unlocks the drawer with the pick; (c) Quick Test shows the misconception line but no ladder, and keeps Show answer locked until its results page; (d) the existing pre-attempt "Hint" drawer (`problem.hint`) stays as it is, or becomes rung 1 and is locked until a first attempt; (e) the other drawer pages stay as they are.

---

## 6. Copy rules

Messages are **system voice** (no "I", no Zorp character), because Zorp never speaks in grading feedback.

- **Shape:** at most two short sentences, at most 120 characters: the likely slip, then one action. Hedge the diagnosis, because it is a guess: "It looks like the diameter was used as the radius. Halve it first."
- **Kind and specific, never shaming:** no "wrong", "incorrect", "mistake", "careless", "silly", "you forgot", "failed", "easy", "simply", "obviously", "just". Describe the work, not the pupil ("That is the hypotenuse squared" rather than "You forgot to square root").
- **House style enforced as errors for this surface:** British spelling, no em or en dashes (comma, colon or full stop instead), no emoji, at most one "!" (prefer none), reading grade at most 8 for lines of 8 words or more, words of four or more syllables only from a maths allowlist (hypotenuse, circumference, perpendicular, probability, denominator, numerator, multiplier, approximately).
- **Gives a method, not the answer:** a message may say which step to fix, never state the corrected value or the factor by which to change the pupil's answer (D5).
- **Zorp stays non-negative:** no change to `react.wrong` or `CONTEXT_MAP`; no new expressions in Phase 1 to 4. The soft sound and `oops-encourage` stay as they are.

**Lint.** `models/zorp_voice.py` gains `extract_hint_messages()` (reads `MESSAGES`, `BANK_NOTES` and `NUDGES` by `ast`) on a new surface `system_hint` with the limits above as errors; `python scripts/test_zorp_voice_smoke.py --write` regenerates Appendix A of `docs/ZORP_CHARM.md`.

**Lines (Phase 1 rows are the text as built in `MESSAGES`; later rows are drafts for David's review in Phase 2 and after).**

| Rule | Message |
|---|---|
| gen.sign | Check the sign. Look again at each step where a number could change from positive to negative. |
| gen.pow10 | Check the place value. Count how far the decimal point should move. |
| gen.accuracy | Nearly there. Round to the accuracy the question asks for. |
| gen.truncated | Nearly there. Look at the next digit to decide whether to round up or down. (a task that only asks to round) |
| gen.early_round | Very close. Keep every digit until the last step, then round as the question asks. (a calculation) |
| gen.reciprocal | Check the division. It looks like the numbers were divided the other way round. |
| gen.reciprocal_fraction | Check the fraction. It looks like the top and bottom have been swapped. |
| gen.pair_swapped | Those two values look swapped round. Check which one comes first. |
| gen.one_root | That is one solution. This equation has two, so find the other one too. |
| gen.as_percentage | That looks like a decimal. The question asks for a percentage, so change it into one. |
| gen.as_decimal | That looks like a percentage. The question asks for a decimal, so change it into one. |
| mens.diameter_as_radius | It looks like the diameter was used as the radius. Halve it first. |
| mens.area_units | Check the units. 1 m² is 100 cm by 100 cm, which is 10 000 cm². |
| pyth.no_sqrt | That is the hypotenuse squared. Take the square root to finish. |
| pyth.added_for_short | For a shorter side, subtract: hypotenuse squared minus the other side squared. |
| trig.wrong_ratio | Check which ratio fits. Label the sides from the angle first: opposite, adjacent, hypotenuse. |
| trig.radians | Check that your calculator is in degrees, not radians. |
| pct.reversed | Check the multiplier. An increase multiplies by more than 1, a decrease by less. |
| pct.reverse_of_new | This takes the percentage of the new amount. Divide by the multiplier instead. |
| prob.added_and | For one event and then another, multiply the probabilities. |
| ang.supplement | Check which angle fact applies. Some pairs of angles are equal, and others add up to 180°. |
| ang.complement | Check which total applies. A right angle is 90°, a straight line is 180° and a full turn is 360°. |
| brg.three_figures | Correct! Bearings are written with three figures, so 5° is written 005°. (shown on a correct answer typed without the zero, which the checker already accepts) |
| cm.minutes_decimal | Check the time. 30 minutes is 0.5 hours, not 0.3. |
| stats.median_position | Check the middle position. With n values, the median is value (n + 1) ÷ 2. |
| seq.off_by_one | Check your rule. Put n = 1 into it and see if you get the first term. |
| order.left_to_right | Check the order of operations. Multiply and divide before you add and subtract. |

---

## 7. Coverage plan

**Order (most single-value slots and clearest slips first; there is no live traffic data, since the site is not deployed and the app collects no analytics).**

| Wave | Topics | Target misconceptions |
|---|---|---|
| A (Phase 2) | mensuration, pythagoras, trigonometry | diameter as radius; radius as diameter; circumference with r instead of 2r; area and circumference formulas swapped; triangle area not halved; trapezium without halving; cm² to m² by 100; volume units by 100 or 1000; no square root; added squares for a shorter side; subtracted for the hypotenuse; a + b; wrong ratio (sin, cos, tan swapped); inverse not applied; radians mode; rounded intermediate |
| B (Phase 2) | number, fdp, decimals, bidmas, compound measures, ratio | percentage change reversed; reverse percentage taken of the new amount; percentage of instead of change; simple instead of compound interest; order of operations left to right; place value by a power of ten; standard form power off by one; speed as distance times time; minutes as decimal hours; density inverted; km/h and m/s by 1000 or 3.6 the wrong way; ratio share divided by one part; ratio reversed; inverse proportion treated as direct |
| C (Phase 5) | bearings, geometry angles, probability, statistics, sequences | back bearing by the wrong turn; 360 minus the bearing; angle from the wrong north line; supplement or complement; interior and exterior swapped; polygon sum with n instead of n minus 2; probabilities added for "and", multiplied for "or"; with replacement used for without; complement not taken; median at n ÷ 2; mean of midpoints with class widths; range as the largest value; nth term off by one difference; difference used as the constant |
| D (Phase 5) | algebra families (`alg` records), simultaneous and quadratic, transformations and vectors multipart | sign error moving a term; divided before subtracting; only one root; root signs flipped; x and y swapped; coordinate or vector components swapped; reflection in the wrong axis; enlargement factor inverted |

**Coverage metrics (printed by the new smoke every run, ratchets like the verification register).**

1. *Slot coverage:* share of the 1,072 practice slots whose problem gets at least one family rule (generic rules reported separately). Targets: Phase 2 at least 30%, Phase 5 at least 60%.
2. *Catalogue coverage:* per topic, targets from the table above that have a rule; printed as a checklist with a ratchet (`HINTS_FLOOR`, may only rise).
3. *Reach:* every rule fires unambiguously on at least one seed of a slot that uses its family; the share of seeds on which each rule's value is unambiguous is printed (a rule below 50% is flagged for review).
4. *MCQ notes:* share of procedural distractors with a verified note, and of bank distractors with a verified or reviewed note. Targets: Phase 4 at least 50% of procedural distractors in waves A and B.

---

## 8. Verification and tests

New `scripts/test_gcse_maths_hints_smoke.py` (picked up by the runner's glob), separate from the 34 s verification smoke. **Budget: at most 12 s default run.** Generation is about 0.45 s per seed for all 1,072 practice slots, so 3 seeds per slot for families with rules plus the unit tables fits comfortably. `--deep` (40 seeds) runs by hand.

Named checks:

- `rule_sound`: for every rule and every seed of every slot with its family, the candidate is finite, differs from the independently re-solved key (the verification solvers, `scripts/gcse_verify/`), and is rejected by `check_answer` with the stored form.
- `rule_reachable`: each rule produces at least one unambiguous match (no dead rules); each family named in `FAMILY_RULES` still exists among the `record()` calls (no stale families).
- `no_collision`: when two rules with different messages give the same value on a seed, `diagnose()` returns no message for that value (asserted, and counted per rule).
- `unit_table`: at least one hand-computed example per rule (inputs, typed answer, expected rule id), written by hand, not generated, as the independent check on each formula.
- `negative_control`: random wrong answers far from every candidate return no diagnosis; the exact key never diagnoses; an unparseable answer never diagnoses; a mutation pass (each rule formula perturbed by one unit) must make `unit_table` fail for that rule.
- `mcq_notes`: section 4 checks; notes only on non-key options; notes survive `_shuffle_mcq`.
- `copy_lint`: every message passes the `system_hint` lint (also enforced by the voice smoke).
- `no_leak`: `_problem_client_payload` and `strip_problem_keys` (answered and not answered) never contain `answer_record` or `option_notes`; a check response carries `hint` only when `correct` is false; the lesson-quiz answer route never returns a message mid-quiz.
- `no_drift`: question, solution, key and options identical with capture on and off, and against the previous commit for the tagged MCQ builders.
- `ladder`: rung 2 text never contains the key at its accuracy; rung order and clamping of `attempt_no`.
- `budget`: session `answer_record` at most 256 B on every sampled problem; JS and CSS byte caps (section 10).

Runtime ledger: suite about 4 minutes today; verification smoke about 34 s; the new smoke adds at most 12 s.

---

## 9. Privacy and safeguarding

- **Default: nothing new is stored.** No table, column, activity field, cohort field or log line holds a misconception id or a hint rung. Attempts and activity events keep exactly the fields they have today (they already hold the typed answer for the first attempt). The ladder counter lives in the page and dies with it.
- **Feature gate (`docs/SECURITY_AND_GDPR.md` 6.1):** Q1 new personal data: no (with D2 option A). Q2 more visible to others: no. Q3 new third party: no. Q4 profile, rank or nudge: no profiling or ranking; the hints are feedback on the question in front of the pupil, with the stronger rungs pupil-pulled (D3), no timers, streak wording or pressure. Recommend one DPIA review-log row noting the Children's Code standard 13 check even though no answer is yes.
- **D2 (settled 2026-10-24; side-lined 2026-10-26, not part of the first launch): teachers will see per-pupil labels, stored, in a later phase (Phase 6).** That is a new stored inference about a child shown to another person. It is not built, nothing is stored for it now, and Phases 1 to 5 keep the "nothing new is stored" default above. What Phase 6 would require, and what David must confirm first, is in section 10, Phase 6.
- **Copy safety:** section 6 rules, enforced by lint; Zorp keeps `oops-encourage`.
- **No reflection pre-filling:** the diagnosis never pre-selects a "What tripped you up?" chip, so stored reflections stay the pupil's own choice.

---

## 10. Phases

Each phase ships on its own, behind no flag, with its own done-criteria.

### Phase 1: key-only diagnosis on the server (no JS) - BUILT 2026-10-24 (see section 13)

- **Build:** `misconceptions.py` with `MESSAGES`, `GENERIC_RULES`, `diagnose()`; wire into `/api/v1/problems/check` for session-bound GCSE maths; `system_hint` lint surface and extractor; the new smoke with `rule_sound`, `no_collision`, `unit_table`, `negative_control`, `copy_lint`, `no_leak`; `brg.three_figures` note on correct answers typed without the leading zero. Optional (D7): replace the em dashes in the GCSE-reachable "Not quite" strings in `answer_checkers.py` with full stops.
- **Files:** `generators/shared/misconceptions.py` (new), `app.py` (check route), `models/zorp_voice.py`, `scripts/test_gcse_maths_hints_smoke.py` (new), `scripts/test_zorp_voice_smoke.py` (`--write`), `docs/API.md`, `docs/AI_HANDOFF.md`, this doc.
- **Bytes:** 0 B JS, 0 B CSS, no cache bump (feedback already renders `data.feedback`).
- **Done when:** every generic rule has a unit example and is reachable on at least one GCSE maths slot; no collision returns a message; voice smoke and full suite green; new smoke at most 8 s (the build set the budget at 12 s and runs in about 6 s).

### Phase 2: recorded-input capture and family rules, waves A and B - BUILT AND REVIEWED 2026-10-26 (see sections 15 and 16)

- **Build:** `verify_hook.capture()` and the second sink; `with_answer_record` in `topic_registry.py`; `answer_record` in `SERVER_ONLY_KEYS`; family rules and `NUDGES` for waves A and B; context strings on the `record()` lines that need them (for example `given='diameter'`); `rule_reachable`, `no_drift`, `budget` checks; coverage metrics 1 to 3 with ratchets.
- **Files:** `generators/shared/verify_hook.py`, `topic_registry.py`, `models/class_assignments.py`, `generators/shared/misconceptions.py`, `generators/gcse/maths.py`, `maths_mensuration.py`, `maths_pythagoras.py`, `maths_compound_measures.py`, `maths_num_stats_prob_rat.py` (record lines only), the new smoke, `docs/GCSE_MATHS_VERIFICATION.md` (note on the second sink).
- **Bytes:** 0 B JS, 0 B CSS; session growth at most 256 B per problem.
- **Done when:** slot coverage at least 30%; every wave A and B target either has a rule or a written reason; verification smoke unchanged in result and within 1 s of its old runtime; pupil output identical to Phase 1 for every slot (diffed).

### Phase 3: hint ladder in practice, and messages in set work and quiz results - BUILT AND REVIEWED 2026-10-26 (see sections 17 and 18)

- **Build:** the rung (`hintRung`) in the check request; rung 1 to 3 text from the server (`hint: {kind, text | html, rung}`); `.free-response-hint` line under the feedback; a "Show a bigger hint" button (D3); **D1: the "Show answer" drawer starts locked and unlocks after the last rung (section 5.1)**; MCQ and Quick Test treatment as proposed in 5.1; set work returns the message after grading (the solution is already revealed only then); lesson-quiz results add it per question; D8: reword the cohort line to "About N% of attempts needed another go" when a hint shows (`formatCohortHint` in `site.js`); the three remaining em dashes in `site.js` answer strings (D7 leftovers: the MCQ "Not quite" line at two places and the fallback "Not quite, try again.") are fixed in the same edit.
- **Files:** `app.py` (check route, set-work answer route, lesson-quiz results), `generators/shared/misconceptions.py` (ladder, step split), `models/class_assignments.py`, `static/js/site.js`, `static/css/practice.css`, `templates/base.html` (`site.js?v=35`, `practice.css?v=30`), `static/js/sw.js` (`pb-v106`), quiz results template or JS, the new smoke (`ladder`).
- **Bytes:** `site.js` at most +2,500 B; `practice.css` at most +600 B (core headroom 3,914 B). Add a `SITE_JS_MAX_BYTES` cap to the new smoke (baseline 207,046 B plus this phase), with a ledger line here.
- **Done when:** ladder works for typed answers with reduced motion and screen readers (`aria-live` polite, no focus steal); the Show answer drawer is locked until the last rung and tells the pupil how to unlock it; no rung leaks the key; set work and quizzes never show a message before grading; voice smoke and full suite green.

### Phase 4: MCQ distractor notes - BUILT AND REVIEWED 2026-10-26 (see sections 19 and 20)

- **Build:** tagged option builders; `option_notes` on procedural MCQs for waves A and B; `why` and `BANK_NOTES` for bank items in those topics; `POST /api/v1/problems/option-note`; MCQ JS shows the note after a wrong pick under the existing highlight; notes in set-work and quiz results; `mcq_notes` checks and metric 4.
- **Files:** `generators/gcse/maths_bank_procedural_mcq.py`, `maths_basic_topics_mcq.py` and the topic banks touched, `generators/shared/utils.py` (no change to the shuffle; notes are text-keyed), `models/class_assignments.py`, `app.py`, `static/js/site.js`, `static/css/practice.css`, `scripts/gcse_verify/solvers_bank*.py` (optional misconception values), the new smoke, cache bumps (`site.js?v=36`, `sw.js` `pb-v107`).
- **Bytes:** `site.js` at most +900 B; `practice.css` at most +200 B.
- **Done when:** at least 50% of procedural distractors in waves A and B carry a verified note; every bank note is verified or listed as reviewed; the MCQ letter-consistency and verification smokes stay green; no drift.

### Phase 5: remaining topics, multipart and algebra - BUILT AND REVIEWED 2026-10-26 (see sections 21 and 22; coverage target not met)

- **Build:** waves C and D; per-part rules for `number_fields` (a rule names the part it applies to by `ask`); algebra rules from `alg` records (parse the displayed equation with the safe parser, compute the sign-error and order-of-steps candidates); multi-record families (graphs) by choosing the record whose family has rules; teacher view only if D2 B or C.
- **Bytes:** none expected beyond Phase 3 and 4 caps.
- **Done when:** slot coverage at least 60%; catalogue checklist complete or with reasons; deep run clean at three seed offsets.

### Phase 6: teacher-visible "things to revisit" (D2). SIDE-LINED 2026-10-26. NOT BUILT.

**Status (2026-10-26).** David has side-lined Phase 6. It is not part of the first launch. It is more relevant to his own European School classes in Belgium, so it will be revisited later, in that context. Nothing for it is built or stored, and Phases 1 to 5 stay storage-free. The analysis and open questions below are kept unchanged for that future discussion; do not start Phase 6 without David reopening it and answering them.

**What David asked for:** misconception labels per pupil, stored, visible to teachers.

**Why this is a different kind of feature.** Phases 1 to 5 give a pupil feedback on the question in front of them and keep nothing. Phase 6 would create and keep an inference about an identifiable child (what they seem to misunderstand) and show it to another person. That is a new stored data category, a form of profiling, and a change to who can see what about a child. Nothing for it is built or stored now: no table, column, event field or cache, and Phases 1 to 5 must not be written in a way that quietly collects it (the rule ids are returned to the browser for styling only and are never saved).

**What it would require, all in the same release as the feature:**

1. **Feature gate** (`docs/SECURITY_AND_GDPR.md` 6.1): Q1 new personal data = yes; Q2 more visible to others = yes (teacher); Q4 profile = yes. Record the answers.
2. **DPIA** (`docs/DPIA.md`), written and reviewed **before** any processing starts (UK GDPR Article 35; Children's Code standard 2): a new section after 9 (G8 teacher mode) covering the inference, its accuracy and the harm of a wrong label, the teacher audience, retention, and the Children's Code standards it touches: 1 best interests, 4 transparency, 5 detrimental use, 7 default settings, 8 data minimisation, 11 by analogy (a pupil should see an obvious sign that a teacher can see these notes) and 12 profiling (off by default unless there is a compelling reason, with safeguards). Note: the gate in `docs/SECURITY_AND_GDPR.md` 6.1 cites standard 13 (nudge techniques) for "profile, rank or nudge"; profiling itself is standard 12, so the Phase 6 DPIA must cite both. Add a review-log row.
3. **ROPA** (`docs/ROPA.md`): a new row, or an amended row 9, for the stored inference: purpose, lawful basis, data, recipients (the pupil's teachers only), retention, security.
3a. **Lawful basis, roles and automated decisions:** record the lawful basis for keeping the notes and who is controller (the operator, or a school using the site, with the operator as processor); if a school is controller, it decides and must be told what is processed. The notes are an automated inference: they must never feed a decision with a legal or similarly significant effect on a pupil (UK GDPR Article 22), such as setting, grouping, reports or references, and the teacher view must say so.
4. **Privacy notice and join disclosure**: `templates/legal_privacy.html` and the G8 join copy must say that teachers see things-to-revisit notes, what they are based on, and how long they last. A pupil who joined a class before this ships must be re-informed, not silently covered by an old disclosure.
5. **Teacher-only visibility**: shown only to a teacher with an active membership of the class, on the existing progress views (T0 to T2 tiers in `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` 2.2, which are locked: this reopens 2.2 and needs David's explicit cue). Not on leaderboards, not in friends' activity events, not in the feed, not in cohort stats, not in CSV exports unless David says so. The pupil can see their own.
6. **Storage design (when approved):** one small table keyed by (pupil, class or topic, rule family) holding a count and the last-seen date, never the typed answer and never a rule id per attempt; erased with the account (FK cascade like the G8 tables); pruned on a schedule in `scripts/prune_expired_data.py`; included in the pupil's export (`models/data_export.py`) and covered by the erasure and export smoke tests.
7. **Wording: "things to revisit", never a label on the child.** For example "Often checks the sign: worth a look at negative numbers", based on counts over a window, with the evidence (how many questions) shown, never "has a misconception", never a ranking or a score, never shown to other pupils. Reviewed with the same lint as other copy.
8. **Accuracy guard:** a note appears only after several separate questions show the same slip (threshold to be set), and the teacher sees that it is a pattern from practice answers, not a diagnosis.
9. **Pupil controls:** the pupil can see the notes about them, can say one is wrong and clear it (rectification and objection, UK GDPR Articles 16 and 21), and can opt out of keeping them from settings; clearing must not break class progress. The notes are included in a subject access request (the data export) and erased with the account.
10. **Tests:** teacher authz on every endpoint, no cross-class leakage, no pupil-to-pupil leakage, export and erasure coverage, retention pruning, wording lint, and a "nothing stored when the feature is off" check.

**Open questions David must confirm before this is built:**

- Q-A. Who sees it: the teacher of a class the pupil joined (as for T0 to T2), or every teacher who has the pupil on any roster? Do parents or the pupil see it? Are other pupils excluded (assumed yes)?
- Q-B. What exactly is kept: a count per slip kind per pupil and topic (assumed), or each occurrence with a date? (Per-occurrence is more intrusive and is not recommended.)
- Q-C. How long is it kept: weeks, the term, or the life of the class membership? What happens when a pupil leaves a class or the class is archived?
- Q-D. Is it collected for pupils who are not in any class (self-study)? The recommendation is no: only while the pupil is in a class that has opted in.
- Q-E. Is it opt-in per class (teacher) and does the pupil or a parent get a way to opt out? Under the "anything that makes a child more visible to others defaults to off" rule, the default should be off.
- Q-F. Does it use only set-work answers (already stored, one per question, which the teacher can already see) or also practice answers (which today are visible only to the pupil)? The set-work-only version adds almost no new exposure; the practice version does.
- Q-G. How is the teacher told that a note is a guess from patterns of wrong answers, and may be wrong? Is the "things to revisit" wording above acceptable?
- Q-H. Is this for pupils under 13 anywhere? (The site targets 13 and over; the rules for under 13 are stricter.)
- Q-I. May the notes be used for anything else (grouping, reports, parent letters, a school information system)? The recommendation is no.
- Q-J. Does David want a qualified person to read the DPIA and notice changes before this ships? (The existing docs already say the operator should have them read.)
- Q-K. Who is the controller for these notes: the operator of the site, or the school whose teacher runs the class (with the operator as processor)? What is the lawful basis (for a school, usually public task; for the operator, legitimate interests with a balancing test)? Consent is not recommended as the basis for a pupil in a class.
- Q-L. How does a pupil see that a teacher can see these notes (an obvious sign on the pupil's own practice page or settings, in plain words for a 13 year old), and how does a pupil say a note is wrong?
- Q-M. Confirm the notes are never used for any automated decision about a pupil and never leave the site (no export to a school information system, no parent letters) unless a later decision and DPIA say otherwise.

**Files (when approved):** `models/` (new misconception-notes model), `app.py` (teacher and pupil routes), `templates/` (teacher progress views, pupil settings, privacy notice, join copy), `models/data_export.py`, `models/account_deletion.py`, `scripts/prune_expired_data.py`, `docs/DPIA.md`, `docs/ROPA.md`, `docs/SECURITY_AND_GDPR.md` (gate answers, retention table), `docs/G8_TEACHER_HANDOFF.md`, the new smoke.

---

## 11. Decisions (settled by David, 2026-10-24)

The open list is closed. D1 to D3 and D5 were answered by David; D4 and D6 to D8 were the recommended defaults, taken.

**D1. When can the full worked solution be seen?** Only after the last hint rung. It is no longer always available. Consequence: the "Show answer" drawer becomes locked in practice (Phase 3, section 5.1). Set work and lesson quizzes keep one answer per question and reveal the solution after grading, as today, so D1 changes nothing there; section 5.1 lists what it means for each surface, and which parts are proposals to confirm.

**D2. Do teachers see misconception patterns?** Yes, as per-pupil labels, stored, but later (side-lined by David on 2026-10-26: not part of the first launch, more relevant to his European School classes in Belgium, to be revisited later). Not built and nothing stored now. Phase 6 (section 10) describes what it requires and lists the questions David must answer first. Wording will be "things to revisit", not labels. Phases 1 to 5 stay storage-free.

**D3. How does the ladder escalate?** The first hint is automatic; "Show a bigger hint" is optional (Phase 3, section 5).

**D4. When does an MCQ note appear?** (Default taken.) Straight after a wrong pick in practice, beside the highlighted right option; in set work and quizzes only after grading or on the results page (Phase 4).

**D5. How much may a message give away?** It names the slip and the step to fix, never the corrected value or the factor to apply to the pupil's number. Enforced in Phase 1 by the copy lint (no digits in a message except the angle facts and the bearing form) and by a check that no fired message contains the key or the typed value.

**D6. Do key-only generic rules run on every GCSE maths slot?** (Default taken.) Yes, from Phase 1, with the collision rule.

**D7. Em dashes in the existing "Not quite" strings.** (Default taken.) Fixed in Phase 1 for the strings GCSE maths can reach (47 strings in `answer_checkers.py`: "Not quite, em dash, check your working." became "Not quite. Check your working."). Left alone: the SQL, Python, binary, hex and free-text checkers, which only computer science and science reach, and the three em dashes in `site.js` (changing JavaScript is out of Phase 1; they move into Phase 3).

**D8. The "About N% of students got this wrong" cohort line next to a hint.** (Default taken.) Reword to "About N% of attempts needed another go" when a hint shows. It needs a `site.js` edit (`formatCohortHint`), so it is Phase 3.

---

## 12. Risks and surprises found in the code

| Finding | Consequence for this plan |
|---|---|
| `record()` is a no-op in production | Recorded inputs need the capture wrapper and `answer_record` (section 3.2); the verification test keeps its own sink. |
| Practice sends the key, hint and solution to the browser, and the check response returns `normalized_correct` on a wrong answer | Practice hints add no new exposure; the hard no-leak guarantee is for set work and lesson quizzes. Not changed here (out of scope), but worth knowing. |
| The Flask session is a signed, not encrypted, cookie with about 1.7 KB headroom at p90 | `answer_record` capped at 256 B; candidate values never stored. |
| `make_problem` reshuffles MCQ options; `_letter_opts` dedupes and pads with filler | Notes keyed by option text; filler options carry no note; tagged builders must make the same random calls. |
| Generic families (`quotient`, `arith`) serve many contexts | Context-free rules only, or a context string on the record line. |
| Two families record twice per problem (graphs, graphical simultaneous equations) | Skipped until Phase 5. |
| MCQ persistence is login-only | A guest-safe note endpoint (Phase 4). |
| Existing feedback uses em dashes and a cross glyph, and the lint only lists dashes in system strings as `info` | A stricter `system_hint` surface; D7 for the old strings. |
| Bearings typed without the leading zero are already accepted | The three-figure rule is a note on a correct answer, not a diagnosis. |
| The "What tripped you up?" panel appears on the first wrong attempt for logged-in pupils | Hint shown above it; no pre-filled chips. |
| CSS core headroom is 3,914 B; `site.js` has no cap | Phase budgets of 800 B CSS in total; a new `site.js` cap and ledger in Phase 3. |
| Followers-visible activity events already carry typed answers | Out of scope, but the plan adds nothing to them. |
| The practice page already carries the solution and the key, and a wrong check returns `normalized_correct` (D1 gating is therefore pacing, not security) | Section 5.1; a server-held solution is a separate decision. |
| Quick Test runs on the practice page and the same check route | Phase 1 diagnoses there too (same as practice); its Show answer treatment is a Phase 3 proposal (5.1). |
| Key-only accuracy rules read the accuracy from the question text ("2 decimal places", "nearest 10") and fire only when the key sits on that grid | Questions that state no accuracy, or round the inputs ("estimate by rounding each number"), get no accuracy hint (guarded and tested). Family rules with recorded inputs (Phase 2) remove the guesswork. |
| A key-only rule can name a slip that did not happen (a value that coincides with a candidate by accident) | Messages are hedged ("looks like", "check"), the collision rule drops any value two different messages claim, and the negative control checks 3,300 far-away wrong answers for false positives. |

---

## 13. Phase 1 build notes (2026-10-24, not committed)

**What was built.** `generators/shared/misconceptions.py` (new): `MESSAGES`, `GENERIC_RULES`, `diagnose()`. `app.py`: `POST /api/v1/problems/check` calls it for a GCSE maths problem bound to the session, after the checker has decided, and puts the message in the existing `feedback` field (plus `hint: {"kind": "misconception", "id": ...}` on a wrong answer). `models/zorp_voice.py`: the `system_hint` surface and `extract_hint_messages()`. `generators/shared/answer_checkers.py`: D7 dash fix. `scripts/test_gcse_maths_hints_smoke.py` (new). `scripts/test_zorp_voice_smoke.py`, `docs/ZORP_CHARM.md` (Appendix A regenerated), `docs/API.md`, `docs/AI_HANDOFF.md` section 9, this file. **0 B of JavaScript, 0 B of CSS, no template change, no cache bump** (`site.js?v=34` and `pb-v105` stay). No generator, topic registry, model, table or setting changed, so generated questions are byte-identical (checked, below).

**Rules as built.** Messages are in `MESSAGES` (section 6 lists the text). Candidates are exact `Fraction` values worked out from the stored key, never through a generator helper.

| Rule id | Applies to | Candidate values (K = the key) | Message |
|---|---|---|---|
| `gen.sign` | number, fraction, linear, pi multiple | minus K | `gen.sign` |
| `gen.pow10` | number, linear, pi multiple | K times 10, 100, 1000, 1/10, 1/100, 1/1000 (not K/100 when the answer is a percentage, not 100K when it is a decimal from a percentage) | `gen.pow10` |
| `gen.as_percentage` | number, the question asks for a percentage ("as a percentage", "percentage increase", ...) | K/100 | `gen.as_percentage` |
| `gen.as_decimal` | number, the question asks for a percentage "as a decimal" | 100K | `gen.as_decimal` |
| `gen.accuracy_coarser` | number, linear, when the question states an accuracy the key sits on | K rounded to one or two places fewer (not when within one step of K) | `gen.accuracy` |
| `gen.accuracy_finer` | same | any value that rounds half up to K (not rounded at all) | `gen.accuracy` |
| `gen.truncated` | same, in a task that only asks to round a given number ("Round 5304 to the nearest 10") | one step either side of K | `gen.truncated` |
| `gen.early_round` | same, in any other question, except a value read off a graph | one step either side of K | `gen.early_round` |
| `gen.reciprocal` | number, linear, pi multiple (key not written as a fraction); number and pi multiple only when the question divides (a division sign, "per", speed, density, ratio, mean ...) | 1 over K (K not 0 or plus or minus 1) | `gen.reciprocal` |
| `gen.reciprocal_fraction` | fraction, or a number key written with a slash | 1 over K | `gen.reciprocal_fraction` |
| `ang.supplement` | number in `geometry_angles` or `circle_theorems`, 0 < K < 180, and the answer is an angle (a part labelled in degrees, or a question whose every ask names an angle and no length, count, bearing or letter) | 180 minus K | `ang.supplement` |
| `ang.complement` | same, K < 90 | 90 minus K | `ang.complement` |
| `gen.pair_swapped` | `number_pair`, `vector` | (b, a) for the key (a, b), a different from b | `gen.pair_swapped` |
| `gen.one_root` | `quadratic_roots` with two different roots | either root alone, or one root typed twice | `gen.one_root` |
| `brg.three_figures` | `bearing`, a **correct** answer typed without the leading zero (45 for 045) | not a diagnosis: a note, feedback only, no `hint` field | `brg.three_figures` |

**Choices the plan left open, and why.**

- *Stated accuracy.* The accuracy rules read the question (and `answer_format_hint`) for "N decimal places", "N significant figures" or "nearest X", and fire only if the key sits on that grid. "Estimate by rounding each number to ..." is ignored (that accuracy is for the inputs). With no stated accuracy the accuracy, truncated and early-round rules are off, so a plain integer answer one out gets no rounding advice.
- *Truncated and early round* (changed in review, section 14). From the key alone a value one step from K cannot say which way the pupil went wrong (a cut-off and an early rounding both land on either side), so the two rules split by the kind of question, not by direction: in a task that only asks to round a given number, `gen.truncated` takes both neighbours (rounded the wrong way); in any other question `gen.early_round` takes both, with a message that covers early rounding and cutting off. The two never apply to the same question. A coarser rounding that lands within one step of K is left to them, and `gen.accuracy_coarser` only fires from two steps away.
- *Rounding-aware match.* A candidate matches the pupil's value exactly, or after half-up rounding to the stated accuracy, as long as the rounding moves it by at most 5% (review: so 0.357 typed as 0.36 still matches K/10 for K = 3.57, but 0.007 rounded to 0.01 no longer matches K/10 for K = 0.07). A rounded value of 0 never matches.
- *Angles.* The 180 and 90 rules need the topic, because with no recorded inputs the key alone cannot tell an angle from any other number. They run for `geometry_angles` and `circle_theorems` only; trigonometry angle answers wait for the Phase 2 family rules (wrong ratio, inverse not applied).
- *Multi-part answers.* A part is diagnosed through the existing per-part check (`partial_field`), against that part's key and the part's own type, with the stored problem's topic. The whole `number_fields` answer is never diagnosed.
- *Skipped on purpose.* A result with `wrong_form`, `wrong_letter` or the recurring-decimal message keeps its own (better) message; an answer the checker could not read keeps "Enter a number"; client-supplied keys (no session problem) are never diagnosed; other subjects and levels never are.
- *Fault safety.* `diagnose()` never raises: a fault leaves the checker's own feedback in place. The smoke calls the raising form so a fault fails the test.
- *Lint allowlist.* "calculator", "calculation" and "calculations" (four syllables) joined the maths allowlist beside the plan's eight words.

**Coverage, measured by the new smoke (2 seeds per slot, 2,144 generated questions; 6 seeds gave 783, so the figures are stable).**

| Measure | Result |
|---|---|
| Practice slots (1,072) that can produce at least one hint | **780 (73%)** |
| ... whole-answer hints / per-part hints on multi-part answers | 552 / 228 |
| Single-value answer slots (number, fraction, bearing, surd, standard form, pi multiple: 473) with a hint | 438 |
| `number_fields` slots (251) with a hint on at least one part | 228 |
| Answer types that can produce a hint | **7** of the 28 that practice uses: `number`, `fraction`, `linear`, `pi_multiple`, `number_pair`, `vector`, `quadratic_roots` (plus the `bearing` note on correct answers: up to 15 bearing slots, 6 of them with a key under 100) |
| Answer types with no Phase 1 hint | `algebraic` (51 slots), `proof_steps`, `keyword`, `bearing` (wrong answers), `algebraic_fraction`, `surd`, `number_list`, `standard_form`, `number_estimate`, `completed_square`, inequalities, `ratio`, `power`, vectors in other forms and the rest |
| Topics with no hint at all | `changing_the_subject` (all `algebraic`) |
| Rule reach as built (slots where the rule can fire, 6 seeds; before the review narrowed some rules, see section 14 for the reviewed counts) | sign 697, pow10 653, reciprocal 637, supplement 80, complement 70, pair_swapped 70, early_round 146, truncated 146, accuracy_coarser 138, accuracy_finer 146, reciprocal_fraction 61, one_root 15 |
| Collisions (same value, two different messages: no message shown) | as built 50 values across the 2,144 questions, all `gen.pow10` against `gen.reciprocal` (for example K = 10 and a typed 0.1); after the review 10 |

Each rule's candidates were also checked: all 18,755 are rejected by the checker, none equals the key, and for one candidate per rule per question the message shown is the one its rule owns (or none, where two messages claim the value).

**Leak analysis.**

- *Nothing new is sent before an answer.* `diagnose()` runs only inside the check route, after the grade. No field is added to a generated problem, the session cookie (`last_problem_payload` is byte-identical before and after a check), `_problem_client_payload`, the frozen set-work payload or any stored row. The smoke compares them and scans keys for `misconception`, `candidate`, `answer_record`, `option_notes`.
- *Set work and lesson quizzes.* Only `api_v1_problems_check` reaches the module (an `ast` scan of `app.py` and an import-graph scan of the repo). Set work grades through `grade_frozen_answer` and quizzes through `grade_lesson_quiz_problem`, which return no message, and their stripped payloads are unchanged. A pupil therefore sees no Phase 1 message in set work or in a quiz at all (the messages for those surfaces arrive in Phase 3, after grading).
- *The one place a pupil sees a message* is the check response to that pupil's own wrong typed answer in practice and Quick Test, where the page already holds the key, the hint and the solution (section 3.4).
- *Not stored or counted.* The rule id travels in the response for styling and tests only. `_track_mcq_answered`, attempts, activity events, cohort samples and reflections receive exactly what they received before (the diagnosis is built after, from a copy of the response).
- *Guess-the-key probing.* A message depends on the pupil's answer and the key only through a match, so it tells a pupil only that what they typed is related to the key in one of the listed ways; on a practice page that already carries the key this adds nothing. In set work and quizzes it is never shown.

**Tests.** `scripts/test_gcse_maths_hints_smoke.py`: `rule_sound`, `rule_reachable`, `no_collision`, `unit_table` (95 hand-worked cases), `negative_control` (3,300 far-away wrong answers and about 1,100 exact keys, none diagnosed, plus unparseable, wrong-form, other-subject and client-key cases), `mutation` (12 of 12 perturbed rules caught), `copy_lint`, `no_leak` (route, session, payloads, import graph, set work, lesson quiz), `no_drift` (diagnosis changes nothing, draws no random number, imports no generator; no em dash in any GCSE-reachable checker string, D7), `coverage` (floors `HINTS_FLOOR_SLOTS` = 560 and `HINTS_FLOOR_TYPES` = 7, which may only rise). About 6 s. `scripts/test_zorp_voice_smoke.py` gains `test_hint_messages` (the lint reads `MESSAGES` on the `system_hint` surface and bites on each rule). The "re-solved key" the plan mentions is the stored key, which the 34 s verification smoke already re-solves with the independent solvers; this smoke does not repeat that.

**Deferred.** The ladder, the locked Show answer drawer, the D8 cohort wording and the three `site.js` dashes (Phase 3); MCQ notes (Phase 4); family rules from recorded inputs, wave A to D topics, the `answer_record` capture, trigonometry angle rules, per-part family rules and algebra rules (Phase 2 and 5); everything in Phase 6.


---

## 14. Phase 1 review notes (2026-10-24, independent review, not committed)

**Method.** Every rule's candidates were generated for 3 seeds of every practice slot (3,489 answers a rule can apply to, whole answers and parts), run through `diagnose()` and read beside the question text by topic; hostile inputs were timed; five hand mutations of `misconceptions.py` were run against the smoke; sections 5.1, 9 and 10 (Phase 6) were checked against the code and UK GDPR and the Children's Code.

**Findings and fixes.**

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | High | The 180 minus and 90 minus rules fired on answers in angle topics that are not angles: lengths, radii, chord lengths, areas, numbers of sides and the `x` of an algebra part (for example "Find the length AT", key 4, typed 176, was told "Check which angle fact applies"). | Angle rules now need an angle answer: a part whose label carries a degree sign (and is not a bearing), or a question whose every ask ("find", "calculate", "what is" ...) names an angle and none names a length, count, bearing, sum or a letter to solve for. |
| 2 | Medium | `gen.early_round` ("Keep full values on the calculator") was shown in tasks that only ask to round ("Round 5304 to the nearest 10", typed 5310), where there is no calculation; and the direction split could not tell a cut-off from early rounding (pi as 3.14 lands below the key, which was labelled "truncated"). | The two rules now split by question, not by direction: a rounding task gets "Nearly there. Look at the next digit to decide whether to round up or down." for one step either way; any other question gets the reworded "Very close. Keep every digit until the last step, then round as the question asks." for one step either way. |
| 3 | Medium | Last-place advice on values read off a graph (cumulative frequency median 54 to 1 d.p., typed 53.9). | No rounding rules when the question reads a value off a graph or curve. |
| 4 | Medium | A percentage typed as a decimal ("Write 0.6 as a percentage", typed 0.6; "Find the percentage increase", key 40, typed 0.4) got the place-value line, which misnames the slip. | New `gen.as_percentage` ("That looks like a decimal. The question asks for a percentage, so change it into one.") and `gen.as_decimal` (the reverse, for "Write 36% as a decimal"); `gen.pow10` drops that one factor of 100 on those questions. Neither message states the factor (D5). |
| 5 | Medium | `gen.reciprocal` ("divided the other way round") fired on questions with no division ("Calculate 6 + 2 × 1", typed 0.125). | Number and pi-multiple answers need a division in the question (a division sign or fraction, "per", speed, density, rate, ratio, mean, share ...); linear equations always qualify (the last step divides). |
| 6 | Low | The rounding-aware match accepted roundings that change the value a lot (K = 0.07 to 2 d.p., K/10 = 0.007 rounds to 0.01, so a typed 0.01 was "place value"). | A rounded candidate matches only if rounding moved it by at most 5%. |
| 7 | Low | Below a power of ten the significant-figure grid is finer: for K = 1000 to 3 s.f. the step below is 999, not 990. | Fixed in the neighbour calculation. |
| 8 | Low | `gen.pair_swapped` said "Check which answer goes in which box", but a vector is typed in one box. | "Those two values look swapped round. Check which one comes first." |
| 9 | Low (cost) | A typed list of 600 roots was turned into SymPy a second time by the diagnosis after the checker had done it (about 0.25 s more per request). | More than two roots is rejected before any SymPy work. Other bombs (2,000-digit numbers, `1e99999`, power towers, nested roots, 999-digit fractions) cost under 10 ms; the diagnosis uses the checker's own capped parsers. |
| 10 | Test gap | A mutation that let the diagnosis run on an answer the checker marked right survived (harmless with today's exact checkers, but not guarded). | New unit case: an answer marked right is never diagnosed, even when it equals a candidate. |

**Probed and kept (no change).**

- *Sign.* Minus the key is always literally what the pupil typed, and "look again at each step where a number could change from positive to negative" fits a subtraction done the wrong way round too (2 − 9 typed as 7). Kept.
- *Place value.* Fits unit conversions and money (129.6 for 12.96). Percentages handled by finding 4.
- *Accuracy.* Significant figures and decimal places read correctly from the question; "estimate by rounding each number" and graph readings are ignored; a key not on the stated grid gets no accuracy hint; error-interval questions have keys off the grid, so they get none.
- *Angles.* In a cyclic quadrilateral (opposite angles add to 180°) a pupil who made them equal types 180 minus the key: the message ("Some pairs of angles are equal, and others add up to 180°") is the apt one. In "angle at the centre" questions 180 minus the key is not a natural slip, but the message only asks which angle fact applies, so it does not mislead. The 90 minus line on an equal-angles question ("Check which total applies") is general enough to stay.
- *Bearing note.* The checker accepts 45, 45°, 0045 and 45.0 for 045, so "Correct!" is true; the note is shown only on a correct answer, carries no `hint` field, and "Correct!" is the house success string (`answer_checkers.py` and `site.js`). "Equivalent forms accepted." is not appended (both normalised forms are `045`). Seen in passing, not changed: the bearing checker also accepts 405 for 045 (angles taken modulo 360), a pre-existing checker choice for David.
- *One root.* A single wrong value keeps "Enter 2 roots."; one right and one wrong root is not diagnosed; a repeated-root equation has no rule.
- *D5.* No message holds a value or a factor (copy lint, the independent number scan, and the scan of fired messages for the key and the typed value). "Count how far the decimal point should move" names the step, not the factor.
- *Copy.* All 14 messages pass the `system_hint` lint (British spelling, no dashes, no emoji, at most two sentences and 120 characters, reading grade at most 8, no shaming words). Tone matches the "Not quite. Check ..." lines: a short observation, then one action.
- *Leaks and storage.* Only `api_v1_problems_check` reaches the module; the diagnosis goes only into `response`, while `_track_mcq_answered` and cohort sampling read the unchanged `result` (which holds neither the message nor the rule id); no request or response body logging exists (`after_request` hooks only set headers); the session problem is byte-identical after a check; set work and lesson quizzes never call it. The rule id in `hint` tells the pupil nothing the message does not.
- *D7.* The 47 strings read naturally ("Not quite. Check your working.", "Not quite. 2 correct, 1 should not be selected. Green = ..."); only string literals changed; nothing in `site.js` or the tests matched the old text except the tests updated with it.

**Remaining limits (key-only rules guess; Phase 2 family rules remove most of these).** "Very close" can show for an exact key typed one step off (3.99 for 4 to 2 d.p.); in a BIDMAS question with a division inside, 1 over the key is shown as a division slip although it is rarely typed by chance; the angle-ask test is a word heuristic and stays silent on "Find angle x" phrasings that also mention a letter.

**Mutation (by hand, on a copy, restored and checksummed).** Clash rule removed (first of several messages shown): smoke fails (`no_collision` 10, `unit_table` 3). The "checker accepts the candidate" guard removed: fails (`unit_table` 2). Diagnosis allowed on an answer marked right: survived at first, fails after the new case (`unit_table` 1). A message giving the factor ("It is 10 times too big"): fails (`copy_lint`). A message giving a value ("it is minus 4"): fails (`copy_lint`). The smoke's own per-rule mutation catches 14 of 14 rules.

**Coverage after the review (2 seeds, 2,144 questions).** 780 of 1,072 practice slots can produce a hint (unchanged), 7 answer types. Questions where each rule fired: sign 2,165, pow10 2,062, accuracy_coarser 273, accuracy_finer 353, truncated 8, early_round 345, reciprocal 553, as_percentage 10, as_decimal 2, reciprocal_fraction 124, supplement 221, complement 136, pair_swapped 130, one_root 30. Collisions: 10 values (pow10 against reciprocal), none shown. Unit table 120 cases; negative control 3,306 far answers and 1,104 keys, none diagnosed; about 8 s.

**Docs.** Sections 5.1 (reload and reroll, and a list of the proposals David must confirm before Phase 3) and 10, Phase 6 (DPIA before processing, the Children's Code standards by number with profiling as standard 12, lawful basis and controller role, Article 22, rectification and objection, subject access, a pupil-visible sign, new questions Q-K to Q-M) were tightened; section 6 and 13 updated to the reviewed rules; `docs/API.md`, `docs/AI_HANDOFF.md`, `docs/ZORP_CHARM.md` Appendix A regenerated.

---

## 15. Phase 2 build notes (2026-10-26, not committed)

**What was built.** The production capture of each GCSE maths question's inputs, and 151 topic rules that read them.

- `generators/shared/verify_hook.py`: a second `ContextVar` sink and `capture()`. `record()` appends the same entry to the verification sink and to the capture sink, whichever are active; they nest in either order. Still no random draw, and the problem is never touched.
- `generators/shared/answer_record.py` (new): `with_answer_record(func)` runs a generator inside `capture()` and, when exactly one record was captured, the question is not multiple choice, the answer type is `number`, `pi_multiple` or `fraction`, the family has rules and the compact JSON is at most 256 bytes, sets `problem['answer_record'] = {'f': family, 'i': inputs}`. Any fault inside the wrapper leaves the problem as the generator made it. `public_problem` / `public_problems` return a copy without the key.
- `topic_registry.py`: every GCSE maths topic `func` is wrapped once (covers practice, reroll, QOTD, Quick Test, lesson quiz and set work at once). No generator file changed.
- `generators/shared/misconception_topics.py` (new, no random, no generator, no database import): `TRUTH[family]` rebuilds the correct answer from the inputs (97 families), `RULES` lists the slips (151 rules, 89 messages), plus a small safe expression parser for the `arith` family (standard order, left to right, powers as products, brackets dropped).
- `generators/shared/misconceptions.py`: `read_record`, `topic_candidates`, `topic_examples`, `_topic_hits`; `_diagnose` tries the topic rules first for scalar answers.
- Storage: `models/user_data.py` (saved problem, quiz attempt), `models/sharing.py` (shared question, suggestion), `models/challenges.py`, `models/quicktest.py`, `models/class_assignments.py` (preview, assignment) and `app.py` (`_save_lq`, `_freeze_problem_payload`) strip the record before any write.
- Copy: `models/zorp_voice.py` `HINT_LONG_WORD_ALLOW` gained `perimeter`, `centimetres`, `original`, `pythagoras`; `docs/ZORP_CHARM.md` Appendix A regenerated.
- Tests: `scripts/test_gcse_maths_hints_smoke.py` extended (about 13 s); `scripts/test_answer_check_smoke.py` expects `answer_record` in `SERVER_ONLY_KEYS`.
- 0 B JS, 0 B CSS, no template change, no cache bump (`site.js?v=34`, `pb-v105` stay).

**How a topic rule decides.**

1. The route calls `diagnose` as in Phase 1. The record is read from the session problem only, never from the request, and only if it belongs to this very answer (same answer type, same `correct_answer_raw`).
2. *Truth guard.* The rule fires only if `TRUTH[family]` rebuilt from the inputs reproduces the stored key: exactly when the question states no accuracy, otherwise after rounding as the question says. A record that does not reproduce its key is ignored, and the Phase 1 generic rules run as before. On the 965 records seen in the smoke the guard failed 0 times.
3. Each rule gives exact values (`Fraction`; pi is 60 digits, or 1 for a `pi_multiple` answer, whose key is the coefficient of pi). A value equal to the key, or that rounds to it at the stated accuracy, is dropped.
4. A typed answer matches a value when it is that value, or that value rounded as the question says (half up, within the 5% guard of Phase 1), or, when no accuracy is stated, that value rounded to the decimal places the pupil typed (at most 6, within 5%). A candidate the checker would accept is discarded.
5. *Precedence.* Topic hits win over generic hits on the same typed value. If the topic rules give exactly one distinct message, it is shown. If they give two different messages, nothing is shown and the generic rules do not step in (a pupil who types a value two topic slips explain gets no guess). If there is no topic hit, the generic rules run as in Phase 1. Two topic rules with the same message on one value are not a collision.
6. D5 holds: every message names the slip and never a value or a factor. The lint allows no digits beyond the angle facts.

**Rules as built.** One example per rule (the hand-worked table in the smoke has 163 worked examples, at least one per rule and per family, plus 40 collision, precedence, guard, accuracy and bad-record cases). pi_multiple keys are shown as the coefficient of pi.

| Rule id | Family | Example (key, typed answer) | Message |
|---|---|---|---|
| `mens.area_uses_circumference` | `mens_circle_area` (r=3) | key 9 pi, typed 6 pi | That looks like the circumference. For an area, the radius is squared, not doubled. (reworded in review) |
| `mens.area_not_squared` | `mens_circle_area` (r=3) | key 9 pi, typed 3 pi | Check the power. It looks like the radius was not squared. |
| `mens.circumference_uses_area` | `mens_circumference` (r=3) | key 6 pi, typed 9 pi | That looks like the area formula. The question asks for the circumference. |
| `mens.circumference_pi_r` | `mens_circumference` (r=3) | key 6 pi, typed 3 pi | It looks like the radius was used where the diameter belongs. Check which one the formula needs. |
| `mens.circumference_of_diameter_doubled` | `mens_circumference` (r=3) | key 6 pi, typed 12 pi | It looks like the diameter was used as the radius. Check which one the formula needs. |
| `mens.sector_whole_circle` | `mens_sector_area` (r=6, angle=60) | key 6 pi, typed 36 pi | That is the whole circle. The question asks for only part of it. |
| `mens.sector_uses_arc` | `mens_sector_area` (r=6, angle=60) | key 6 pi, typed 2 pi | That looks like the arc length formula. The question asks for an area. |
| `mens.arc_whole_circle` | `mens_arc` (r=6, angle=60) | key 2 pi, typed 12 pi | That is the whole circle. The question asks for only part of it. |
| `mens.arc_uses_sector` | `mens_arc` (r=6, angle=60) | key 2 pi, typed 6 pi | That looks like the sector area formula. The question asks for a length. |
| `mens.sector_perimeter_arc_only` | `mens_sector_perimeter` (r=6, angle=60) | key 14 pi, typed 2 pi | That is the curved edge only. The perimeter of a sector also has two straight edges. |
| `mens.cylinder_volume_not_squared` | `mens_cyl_vol` (r=3, h=5) | key 45 pi, typed 15 pi | Check the power. It looks like the radius was not squared. |
| `mens.cylinder_volume_is_area` | `mens_cyl_vol` (r=3, h=5) | key 45 pi, typed 48 pi | That looks like a surface area. The question asks for a volume. |
| `mens.cylinder_area_curved_only` | `mens_cyl_sa` (r=3, h=5) | key 48 pi, typed 30 pi | That is the curved surface only. The total surface area also includes the flat ends. |
| `mens.cylinder_area_is_volume` | `mens_cyl_sa` (r=3, h=5) | key 48 pi, typed 45 pi | That looks like a volume. The question asks for a surface area. |
| `mens.cone_area_curved_only` | `mens_cone_sa_slant` (r=3, slant=5) | key 24 pi, typed 15 pi | That is the curved surface only. The total surface area also includes the flat ends. |
| `mens.cone_volume_no_third` | `mens_cone_vol` (r=3, h=4) | key 12 pi, typed 36 pi | That looks like the volume of the matching prism or cylinder. Check the formula for a cone or pyramid. |
| `mens.pyramid_volume_no_third` | `mens_pyramid_vol` (l=3, w=4, h=5) | key 20, typed 60 | That looks like the volume of the matching prism or cylinder. Check the formula for a cone or pyramid. |
| `mens.cone_volume_slant_as_height` | `mens_cone_vol_from_slant` (r=3, slant=5) | key 12 pi, typed 15 pi | Check the height. This volume needs the perpendicular height, not the slant height. |
| `mens.cone_area_height_as_slant` | `mens_cone_sa_height` (r=3, h=4) | key 24 pi, typed 21 pi | Check the slant height. This area needs the slant height, not the perpendicular height. |
| `mens.sphere_area_is_volume` | `mens_sphere_sa` (r=6) | key 144 pi, typed 288 pi | That looks like a volume. The question asks for a surface area. |
| `mens.sphere_volume_is_area` | `mens_sphere_vol` (r=6) | key 288 pi, typed 144 pi | That looks like a surface area. The question asks for a volume. |
| `mens.sphere_volume_not_cubed` | `mens_sphere_vol` (r=6) | key 288 pi, typed 48 pi | Check the power. It looks like the radius was not cubed. |
| `mens.triangle_full_rectangle` | `mens_tri_area` (b=6, h=4) | key 12, typed 24 | That looks like the answer for a full rectangle. A triangle or trapezium covers only part of one. |
| `mens.trapezium_full_rectangle` | `mens_trapezium` (a=3, b=5, h=4) | key 16, typed 32 | That looks like the answer for a full rectangle. A triangle or trapezium covers only part of one. |
| `mens.prism_full_rectangle` | `mens_tri_prism_vol` (b=3, h=4, length=5) | key 30, typed 60 | That looks like the answer for a full rectangle. A triangle or trapezium covers only part of one. |
| `mens.cuboid_volume_is_area` | `mens_cuboid_vol` (l=2, w=3, h=4) | key 24, typed 52 | That looks like a surface area. The question asks for a volume. |
| `mens.cuboid_area_is_volume` | `mens_cuboid_sa` (l=2, w=3, h=4) | key 52, typed 24 | That looks like a volume. The question asks for a surface area. |
| `mens.cuboid_area_faces_missed` | `mens_cuboid_sa` (l=2, w=3, h=4) | key 52, typed 26 | A cuboid has six faces in three matching pairs. Check that every face is counted. |
| `mens.rectangle_perimeter_is_area` | `mens_rect_perimeter` (l=5, w=3) | key 16, typed 15 | That looks like the area. The question asks for the perimeter. |
| `mens.rectangle_perimeter_half` | `mens_rect_perimeter` (l=5, w=3) | key 16, typed 8 | Check the perimeter. A rectangle has two lengths and two widths. |
| `mens.l_shape_added` | `mens_l_shape` (a=8, b=3, c=6, d=2) | key 42, typed 54 | Check the cut-out. It should be taken away from the large rectangle, not added. |
| `mens.annulus_squared_difference` | `mens_annulus` (R=5, r=3) | key 16 pi, typed 4 pi | Check the order. Square each radius first, then subtract. |
| `mens.annulus_outer_only` | `mens_annulus` (R=5, r=3) | key 16 pi, typed 25 pi | That is the whole outer circle. The hole in the middle needs removing. |
| `mens.pipe_squared_difference` | `cm_hollow_cyl_mass` (R=5, r=3, h=10, density=2) | key 320 pi, typed 80 pi | Check the order. Square each radius first, then subtract. |
| `mens.pipe_solid` | `cm_hollow_cyl_mass` (R=5, r=3, h=10, density=2) | key 320 pi, typed 500 pi | That is the whole outer circle. The hole in the middle needs removing. |
| `mens.diameter_found_for_radius` | `mens_radius_from_area` (area=50.3) | key 4, typed 8 | That looks like the diameter. The question asks for the radius. |
| `mens.radius_found_for_diameter` | `mens_diameter` (circ=31.4) | key 10, typed 5 | That looks like the radius. The question asks for the diameter. |
| `mens.radius_squared_not_rooted` | `mens_radius_from_area` (area=50.3) | key 4, typed 16 | That looks like the length squared. Take the square root to finish. |
| `mens.height_from_volume_not_squared` | `mens_cyl_height` (vol=141.4, r=3) | key 5, typed 15 | Check the power. It looks like the radius was not squared. |
| `mens.area_units_squared` | `mens_cm2_to_m2` (l=200, w=300) | key 6, typed 600 | Check the units. An area in square units changes by the conversion factor squared. |
| `mens.area_units_not_converted` | `mens_cm2_to_m2` (l=200, w=300) | key 6, typed 60000 | That is still in the original units. The question asks for a different unit. |
| `mens.litres_not_converted` | `mens_fill_time` (r=10, h=20, rate=2) | key 3.14, typed 3140 | Check the units. The rate is in litres, but the volume is in cubic centimetres. |
| `mens.similar_power` | `mens_similar` (k=2, value=5, power=2) | key 20, typed 10 or 40 | Check the scale factor. Areas and volumes need the right power of it. |
| `pyth.hyp_not_rooted` | `pyth_hyp` (a=3, b=4) | key 5, typed 25 | That looks like the length squared. Take the square root to finish. |
| `pyth.hyp_sides_added` | `pyth_hyp` (a=3, b=4) | key 5, typed 7 | That looks like the side lengths added or subtracted directly. Pythagoras uses their squares. |
| `pyth.hyp_subtracted` | `pyth_hyp` (a=6, b=8) | key 10, typed 5.3 | To find the hypotenuse, add the squares. Subtracting finds a shorter side. |
| `pyth.leg_added` | `pyth_leg` (c=10, a=6) | key 8, typed 11.7 | To find a shorter side, subtract the squares. Adding finds the hypotenuse. |
| `pyth.leg_not_rooted` | `pyth_leg` (c=10, a=6) | key 8, typed 64 | That looks like the length squared. Take the square root to finish. |
| `pyth.leg_sides_subtracted` | `pyth_leg` (c=10, a=6) | key 8, typed 4 | That looks like the side lengths added or subtracted directly. Pythagoras uses their squares. |
| `pyth.distance_not_rooted` | `pyth_dist` (x1=1, y1=2, x2=4, y2=6) | key 5, typed 25 | That looks like the length squared. Take the square root to finish. |
| `pyth.distance_differences_added` | `pyth_dist` (x1=1, y1=2, x2=4, y2=6) | key 5, typed 7 | That looks like the side lengths added or subtracted directly. Pythagoras uses their squares. |
| `pyth.perimeter_sides` | `pyth_perimeter` (a=3, b=4) | key 12, typed 5 or 7 | Check the perimeter. It needs all three sides, and one is the hypotenuse. |
| `pyth.height_base_not_halved` | `pyth_isosceles_height` (side=13, base=10) | key 12, typed 8.3 | Check the base. The height splits it in two, so the triangle uses half of it. |
| `pyth.height_added` | `pyth_isosceles_height` (side=13, base=10) | key 12, typed 13.9 | To find a shorter side, subtract the squares. Adding finds the hypotenuse. |
| `pyth.height_not_rooted` | `pyth_isosceles_height` (side=13, base=10) | key 12, typed 144 | That looks like the length squared. Take the square root to finish. |
| `pyth.space_not_rooted` | `pyth_space_diag` (l=2, w=3, h=6) | key 7, typed 49 | That looks like the length squared. Take the square root to finish. |
| `pyth.space_one_step_short` | `pyth_space_diag` (l=2, w=3, h=6) | key 7, typed 3.6 | That is the diagonal of one face. The space diagonal needs one more step. |
| `pyth.space_sides_added` | `pyth_space_diag` (l=2, w=3, h=6) | key 7, typed 11 | That looks like the side lengths added or subtracted directly. Pythagoras uses their squares. |
| `pyth.ladder_original_position` | `pyth_ladder_slide` (ladder=13, base=3, slide=2) | key 12, typed 12.6 | That is the height before the ladder slid. Use the new distance from the wall. |
| `trig.side_wrong_ratio` | `trig_side` (known=10, angle=30, known_kind=hyp, find_kind=opp) | key 5, typed 8.7 | Check which ratio fits. Label the sides from the angle first. |
| `trig.side_rearranged` | `trig_side` (known=10, angle=30, known_kind=hyp, find_kind=opp) | key 5, typed 20 | Check how the formula is rearranged. Decide whether the unknown side is on the top or the bottom. |
| `trig.side_radians` | `trig_side` (known=10, angle=30, known_kind=hyp, find_kind=opp) | key 5, typed -9.9 | Check that your calculator is in degrees, not radians. |
| `trig.angle_radians` | `trig_angle` (opp=3, adj=4) | key 36.87, typed 0.64 | Check that your calculator is in degrees, not radians. |
| `trig.angle_ratio_only` | `trig_angle` (opp=3, adj=4) | key 36.87, typed 0.75 | That is the ratio of the sides. Use the inverse button to turn it into an angle. |
| `trig.angle_other` | `trig_angle` (opp=3, adj=4) | key 36.87, typed 53.13 | That is the other acute angle. Label the sides from the angle you want, then pick the ratio. (reworded in review) |
| `trig.cosine_side_not_rooted` | `trig_cosine_side` (b=10, c=10, angle=60) | key 10, typed 100 | That looks like the length squared. Take the square root to finish. |
| `trig.cosine_side_sign` | `trig_cosine_side` (b=10, c=10, angle=60) | key 10, typed 17.3 | Check the signs in the cosine rule. Look at which terms are added and which are subtracted. |
| `trig.cosine_side_radians` | `trig_cosine_side` (b=10, c=10, angle=60) | key 10, typed 19.8 | Check that your calculator is in degrees, not radians. |
| `trig.area_full_product` | `trig_area` (a=10, b=10, angle=40) | key 32.1, typed 64.3 | That looks like the area of a parallelogram. A triangle covers only part of it. (new message in review) |
| `trig.area_radians` | `trig_area` (a=10, b=10, angle=40) | key 32.1, typed 37.3 | Check that your calculator is in degrees, not radians. |
| `trig.area_cosine` | `trig_area` (a=10, b=10, angle=40) | key 32.1, typed 38.3 | Check the formula. The area of a triangle uses the sine of the angle between the two sides. (new message in review) |
| `trig.sine_side_inverted` | `trig_sine_side` (known_side=10, known_angle=30, target_angle=90) | key 20, typed 5 | Check the sine rule. Each side goes with the angle opposite it. |
| `trig.sine_side_radians` | `trig_sine_side` (known_side=10, known_angle=30, target_angle=90) | key 20, typed -9 | Check that your calculator is in degrees, not radians. |
| `trig.apex_half` | `trig_isosceles_apex` (base=6, equal=5) | key 73.7, typed 36.9 | That is half of the apex angle. The apex angle is the whole angle between the equal sides. |
| `pct.change_only` | `num_pct_change` (amount=200, pct=15, sign=up) | key 230, typed 30 | That is the size of the change. Now apply it to the original amount. |
| `pct.change_opposite` | `num_pct_change` (amount=200, pct=15, sign=up) | key 230, typed 170 | Check the direction of the change. The percentage looks like it was applied the opposite way. |
| `pct.reverse_as_forward` | `num_reverse_pct` (final=240, pct=20, sign=up) | key 200, typed 192 | This takes the percentage of the new amount. Divide by the multiplier instead. |
| `pct.reverse_opposite` | `num_reverse_pct` (final=240, pct=20, sign=up) | key 200, typed 300 | Check the direction of the change. The percentage looks like it was applied the opposite way. |
| `pct.vat_only` | `num_vat_inclusive` (price=50, vat=20) | key 60, typed 10 | That is the size of the change. Now apply it to the original amount. |
| `pct.vat_taken_off` | `num_vat_inclusive` (price=50, vat=20) | key 60, typed 40 | Check the direction of the change. The percentage looks like it was applied the opposite way. |
| `pct.changes_added` | `num_two_pct_changes` (amount=200, pct1=10, pct2=20) | key 176, typed 180 | Check the two changes. The second percentage applies to the new amount, not the original. |
| `pct.reverse_two_added` | `fdp_reverse_two_step` (final=192, pct_up=20, pct_down=20) | key 200, typed 192 | Check the two changes. The second percentage applies to the new amount, not the original. |
| `pct.compound_simple` | `num_compound` (principal=1000, rate=10, years=2, sign=up) | key 1210, typed 1200 | It looks like the change came from the original amount every year. Each year uses the new amount. |
| `pct.compound_opposite` | `num_compound` (principal=1000, rate=10, years=2, sign=up) | key 1210, typed 810 | Check the direction of the change. The percentage looks like it was applied the opposite way. |
| `pct.reverse_compound_forward` | `num_reverse_compound` (final=1210, rate=10, years=2) | key 1000, typed 980.1 | This takes the percentage of the new amount. Divide by the multiplier instead. |
| `pct.reverse_compound_one_year` | `num_reverse_compound` (final=1210, rate=10, years=2) | key 1000, typed 1100 | Check the number of years. The multiplier applies once for each year. |
| `pct.of_divided` | `num_pct_of` (amount=200, pct=20) | key 40, typed 10 | Check the method. A percentage of an amount is a fraction out of a hundred of it. |
| `pct.wrong_base` | `fdp_pct_change` (original=40, new=50) | key 25, typed 20 | Check which amount to divide by. A percentage change is a fraction of the original amount. |
| `pct.change_not_compared` | `fdp_pct_change` (original=40, new=50) | key 25, typed 10 | That is the change in value. A percentage compares the change with the original amount. |
| `pct.error_wrong_base` (review) | `num_pct_error` (estimate=40, actual=50) | key 20, typed 25 | Check which amount to divide by. Percentage error compares the error with the actual value. |
| `pct.error_not_compared` (review) | `num_pct_error` (estimate=40, actual=50) | key 20, typed 10 | That is the size of the error. A percentage error compares it with the actual value. |
| `pct.discount_only` | `fdp_shop_discount` (unit=5, qty=4, discount_pct=10) | key 18, typed 2 | That is the size of the change. Now apply it to the original amount. |
| `pct.discount_added` | `fdp_shop_discount` (unit=5, qty=4, discount_pct=10) | key 18, typed 22 | Check the direction of the change. The percentage looks like it was applied the opposite way. |
| `fdp.other_part` | `fdp_fraction_not` (total=40, num=3, den=8) | key 25, typed 15 | That answers a different part of the question. Read again what the question asks for. |
| `fdp.fraction_inverted_of` | `num_frac_of` (amount=40, num=2, den=5) | key 16, typed 100 | Check the fraction. It looks like the top and bottom were used the opposite way round. |
| `fdp.bottom_only` | `num_frac_of` (amount=40, num=2, den=5) | key 16, typed 8 | It looks like only the bottom of the fraction was used. The top says how many parts to take. |
| `fdp.fraction_to_pct_inverted` | `fdp_fraction_to_pct` (a=1, b=4) | key 25, typed 400 | Check the fraction. It looks like the top and bottom were used the opposite way round. |
| `fdp.decimal_fraction_place_value` | `fdp_decimal_to_fraction` (dec=0.25) | key 1/4, typed 1/40 or 5/2 | Check the place value. The bottom of the fraction comes from the last decimal place. |
| `fdp.pct_fraction_per_cent` | `fdp_pct_to_fraction` (pct=25) | key 1/4, typed 5/2 or 1/40 | Check the bottom of the fraction. Per cent means out of a hundred. |
| `dec.mean_total` | `dec_mean` (values=[2, 4, 6]) | key 4, typed 12 | That is the total. A mean divides the total by how many values there are. |
| `est.exact_product` | `num_estimate_product_1sf` (a=3.8, b=6.2) | key 24, typed 23.56 | That is the exact calculation. An estimate rounds each number first. |
| `est.exact_fraction` | `num_estimate_fraction_1sf` (a=3.8, b=6.2, c=1.9) | key 12, typed 12.4 | That is the exact calculation. An estimate rounds each number first. |
| `est.rounded_late` | `num_estimate_product_1sf` (a=3.8, b=6.2) | key 24, typed 20 | Check the order. Round each number first, then calculate. |
| `est.rounded_late_fraction` | `num_estimate_fraction_1sf` (a=3.8, b=6.2, c=1.9) | key 12, typed 10 | Check the order. Round each number first, then calculate. |
| `num.double_negative` | `num_directed` (a=5, op=-, b=-3) | key 8, typed 2 | Check the signs. Look again at what happens when a negative number is added or subtracted. |
| `idx.multiplied` | `num_power` (base=3, exp=4) | key 81, typed 12 | Check the power. It looks like the number was multiplied by the power instead of by itself. |
| `idx.negative_power` | `num_neg_index` (base=2, power=3) | key 0.125, typed -8 or -0.125 | Check the negative power. It does not make the number negative. |
| `idx.power_sign_ignored` | `num_neg_index` (base=2, power=3) | key 0.125, typed 8 | Check the sign of the power. A negative power is not the same as a positive one. |
| `idx.zero_power` | `num_zero_neg_index` (a=3, b=2) | key 0.25, typed 0.75 or 0 | Check the power of zero. It has its own rule that does not depend on the number. |
| `idx.fraction_power` | `num_frac_index` (base=16, num=1, den=2) | key 4, typed 8 | Check the fractional power. The bottom of the fraction tells you which root to take. |
| `bidmas.left_to_right` | `arith` (expr=2 + 3 × 4) | key 14, typed 20 | Check the order. Multiply and divide before you add and subtract. |
| `bidmas.brackets_ignored` | `arith` (expr=(2 + 3) × 4) | key 20, typed 14 | Check the brackets. Work out what is inside them first. |
| `bidmas.power_multiplied` | `arith` (expr=3 + 2^3) | key 11, typed 9 | Check the power. It looks like the number was multiplied by the power instead of by itself. |
| `bidmas.negative_square` | `arith` (expr=(−3)^2) | key 9, typed -9 | Check what the power applies to. Brackets decide whether the negative sign is included. |
| `op.divided_for_product` | `product` (a=6, b=4) | key 24, typed 1.5 or 10 | Check the calculation. This one needs the numbers multiplied. |
| `op.multiplied_for_quotient` | `quotient` (a=24, b=4) | key 6, typed 96 | Check the calculation. This one needs a division. |
| `op.quotient_inverted` (review) | `quotient` (a=25, b=4) | key 6.25, typed 0.16 | Check the division. It looks like the numbers were divided the other way round. (the generic message) |
| `ratio.map_not_converted` | `ratio_map_scale` (cm=5, scale=50000, to=km) | key 2.5, typed 250000 | That is still in the original units. The question asks for a different unit. |
| `ratio.map_divided` | `ratio_map_scale` (cm=5, scale=50000, to=km) | key 2.5, typed 0.0001 | Check the scale. A real distance is bigger than its distance on the map. |
| `ratio.direct_inverse_used` | `prop_direct` (y1=12, x1=3, x2=5) | key 20, typed 7.2 | Check the type of proportion. Here, both quantities increase together. |
| `ratio.direct_additive` | `prop_direct` (y1=12, x1=3, x2=5) | key 20, typed 14 | Check the method. Proportion works by multiplying, not by adding the same amount. |
| `ratio.direct_unit_only` | `prop_direct` (y1=12, x1=3, x2=5) | key 20, typed 4 | That is the amount for one. Now scale it up to the number asked for. |
| `ratio.inverse_direct_used` | `prop_inverse` (a=6, b=4, c=3) | key 8, typed 2 | Check the type of proportion. Here, when one quantity goes up, the other goes down. |
| `ratio.scale_inverse_used` | `prop_scale` (q1=12, n1=4, n2=6) | key 18, typed 8 | Check the type of proportion. Here, both quantities increase together. |
| `ratio.scale_unit_only` | `prop_scale` (q1=12, n1=4, n2=6) | key 18, typed 3 | That is the amount for one. Now scale it up to the number asked for. |
| `ratio.scale_additive` | `prop_scale` (q1=12, n1=4, n2=6) | key 18, typed 14 | Check the method. Proportion works by multiplying, not by adding the same amount. |
| `ratio.unitary_unit_only` | `ratio_unitary` (total=12, n1=4, n2=5) | key 15, typed 3 | That is the amount for one. Now scale it up to the number asked for. |
| `ratio.unitary_inverse_used` | `ratio_unitary` (total=12, n1=4, n2=5) | key 15, typed 9.6 | Check the type of proportion. Here, both quantities increase together. |
| `ratio.missing_parts_swapped` | `ratio_find_missing` (known=12, a=3, b=5) | key 20, typed 7.2 | Check which ratio part goes with which quantity. |
| `ratio.missing_unit_only` | `ratio_find_missing` (known=12, a=3, b=5) | key 20, typed 4 | That is the amount for one. Now scale it up to the number asked for. |
| `ratio.missing_additive` | `ratio_find_missing` (known=12, a=3, b=5) | key 20, typed 14 | Check the method. Proportion works by multiplying, not by adding the same amount. |
| `ratio.part_to_part` | `ratio_part_fraction` (parts=[2, 3], which=0) | key 2/5, typed 2/3 | Check the total. A fraction compares one part with the whole, not with the other parts. |
| `cm.speed_direction_kmh` | `cm_kmh_to_ms` (kmh=36) | key 10, typed 129.6 | Check which way the conversion goes. Think about whether the number should get bigger or smaller. |
| `cm.speed_one_unit_kmh` | `cm_kmh_to_ms` (kmh=36) | key 10, typed 36000 or 0.01 | It looks like only one unit was converted. Both the distance and the time units need changing. (hedged in review) |
| `cm.speed_direction_ms` | `cm_ms_to_kmh` (ms=18) | key 64.8, typed 5 | Check which way the conversion goes. Think about whether the number should get bigger or smaller. |
| `cm.speed_one_unit_ms` | `cm_ms_to_kmh` (ms=18) | key 64.8, typed 64800 or 0.018 | It looks like only one unit was converted. Both the distance and the time units need changing. |
| `cm.minutes_decimal_hm` | `cm_speed_hm` (s=60, h=1, m=30) | key 90, typed 78 | Check the time. Minutes are not hundredths of an hour, so they need converting. |
| `cm.minutes_unconverted_hm` | `cm_speed_hm` (s=60, h=1, m=30) | key 90, typed 5400 | Check the units of time. The speed is per hour, but the time is in minutes. |
| `cm.minutes_decimal_mins` | `cm_dist_mins` (s=60, mins=30) | key 30, typed 18 | Check the time. Minutes are not hundredths of an hour, so they need converting. |
| `cm.minutes_unconverted_mins` | `cm_dist_mins` (s=60, mins=30) | key 30, typed 1800 | Check the units of time. The speed is per hour, but the time is in minutes. |
| `cm.mean_of_speeds` | `cm_avg_speed` (legs=[[60, 30], [60, 60]]) | key 40, typed 45 | Check the average speed. It is total distance over total time, not the mean of the speeds. |
| `cm.mean_of_speeds_time` | `cm_avg_speed_time` (legs=[[1, 30], [2, 60]]) | key 50, typed 45 | Check the average speed. It is total distance over total time, not the mean of the speeds. |
| `cm.mean_of_two_speeds` | `cm_avg_speed_equal` (s1=30, s2=60) | key 40, typed 45 | Check the average speed. It is total distance over total time, not the mean of the speeds. |
| `cm.mean_of_densities` | `cm_alloy_vol` (d1=2, d2=6, v1=1, v2=3) | key 5, typed 4 | Check the method. The density of a mixture is its total mass divided by its total volume. |
| `cm.alloy_weighted_mean` | `cm_alloy_pct` (pa=20, pb=80, da=2, db=8) | key 5, typed 6.8 | Check the method. The density of a mixture is its total mass divided by its total volume. |
| `cm.pressure_from_mass` | `cm_box_pressure` (mass=10, g=10, length=2, width=5) | key 10, typed 1 | Pressure uses force, not mass. Turn the mass into a force first. |
| `cm.pipes_combined` | `cm_pipes` (vol=60, fill=8, drain=4) | key 15, typed 5 or 7.5 | Check the combined rate. The drain takes water out while the other pipe fills the tank. |
| `cm.closing_speed_overtake` | `cm_overtake` (head_min=30, slow=40, fast=60) | key 60, typed 12 | Check the relative speed. Whether speeds add or subtract depends on the directions. |
| `cm.closing_speed_relative` | `cm_relative` (s1=50, s2=30, dist=20, direction=same) | key 60, typed 15 | Check the relative speed. Whether speeds add or subtract depends on the directions. |
| `mens.diameter_as_radius.mens_circle_area` | `mens_circle_area` (r=3) | key 9 pi, typed 36 pi | It looks like the diameter was used as the radius. Check which one the formula needs. |
| `mens.diameter_as_radius.mens_cyl_vol` | `mens_cyl_vol` (r=3, h=5) | key 45 pi, typed 180 pi | It looks like the diameter was used as the radius. Check which one the formula needs. |
| `mens.diameter_as_radius.mens_cone_vol` | `mens_cone_vol` (r=3, h=4) | key 12 pi, typed 48 pi | It looks like the diameter was used as the radius. Check which one the formula needs. |
| `mens.diameter_as_radius.mens_sphere_vol` | `mens_sphere_vol` (r=12) | key 2304 pi, typed 18432 pi | It looks like the diameter was used as the radius. Check which one the formula needs. |
| `mens.diameter_as_radius.mens_sphere_sa` | `mens_sphere_sa` (r=3) | key 36 pi, typed 144 pi | It looks like the diameter was used as the radius. Check which one the formula needs. |


**Coverage (2 seeds per practice slot, 1,072 slots, 2,144 questions).**

| Measure | Result |
|---|---|
| Slots whose question carries an answer record | 197 (18.4%) |
| Slots with at least one topic rule that fires unambiguously | **193 (18.0%)** |
| Slots with a Phase 1 generic hint | 780 (72.8%) |
| Slots with either | 780 (72.8%); every topic slot already had a generic hint, so Phase 2 adds no new slot, it replaces a generic or no message with a specific one |
| Topic rules that fire on a generated question | 151 of 151; 1,776 unambiguous diagnoses; 14 silent collisions; 67 diagnoses where a generic rule would have said something else |
| Records | 965 seen; largest 83 bytes (limit 256); 0 fail the truth guard |

**The 30% target was not met, and cannot be from these topics.** The brief asks for topic rules on at least 30% of practice slots. The nine Phase 2 topics (bidmas 18, decimals 25, fdp 20, number 55, ratio_proportion 54, pythagoras 24, trigonometry 29, mensuration 51, compound_measures 45) hold 321 of the 1,072 slots, which is 29.9%, so even a rule on every one of them stays below 30%. Only 223 of those slots (20.8%) have a single typed value that a rule can read; the other 98 are multi-part answers (`number_fields`), keyword, standard form, order or proof steps, ratio and similar. 197 of the 223 carry a record and 193 are covered. Reaching 30% needs per-part rules for multi-part answers (Phase 5) or wave C and D topics (probability, statistics, sequences, bearings, algebra), which are outside this phase. The smoke ratchets the measured numbers (topic at least 190, either at least 775).

**Session size (the point of the 256 B cap).** Measured as the length of the signed cookie holding one `last_problem_payload` with the slimmed problem, for the 1,072 practice slots (seed 0), with the record and with it removed:

| | p50 | p90 | max |
|---|---|---|---|
| Before (no record) | 668 B | 1,764 B | 2,714 B |
| After | 676 B | 1,775 B | 2,714 B |

A record adds a median of 38 B and at most 68 B to the compressed cookie (197 questions carry one); the largest question has none. The plan's figures (624, 1,707 and 2,418 B) used a slightly different measure (they omit the `last_problem_payload` wrapper fields and the signature), so they are not comparable byte for byte; the limit is about 4,093 B. Even a full 256 B record on the biggest question stays under the limit (the smoke asserts max before plus 256 plus 200 is under 4,093, and a ceiling of 3,000 B on the measured maximum).

**Leak analysis.**

- Client: `_problem_client_payload` is a whitelist and never copies the key; `answer_record` is in `SERVER_ONLY_KEYS`, so `strip_problem_keys` removes it from set work whether or not the answer is revealed; the check response carries only `feedback` and `hint: {kind, id}`; no static or template file mentions the word (the smoke scans them). A record sent by the client in the check request is never read.
- Storage: saved problems, shared questions, suggestions, challenges, quiz attempts, Quick Test rows, set-work previews and assignments and the lesson-quiz row are all written through `public_problem(s)`, tested by calling each writer with a mock connection and reading every SQL parameter. The record lives in the signed session cookie and nowhere else. It is never logged.
- Set work: `answer_record` is in `SERVER_ONLY_KEYS` (stripped from anything a pupil receives) and in `NOT_FROZEN_KEYS` (never copied into the frozen problem). This departs from section 3.2 item 3, which said to copy it, because the Phase 2 brief says it is never stored in a database. Phase 3 would have to reopen this to show messages in set work, and then decide where the inputs live.
- Quick Test: the questions are held in `quicktest_sessions`, so the record is stripped before storage and a Quick Test check only gets the generic rules. It is a one-line change (stop stripping in `save_quicktest_session`) if topic messages are wanted there, at the cost of the record entering that table; this needs David's decision.
- Privacy: the record is the inputs the question already prints (the presence guard of the verification track guarantees every numeric input appears in the question), so it holds nothing about the pupil. `docs/DPIA.md` and `docs/ROPA.md` do not list session contents and Phase 1 did not touch them; no line is needed because nothing new is stored, logged or sent. If the record is ever kept in the database (Quick Test, set work), both documents need a line.

**Tests (`scripts/test_gcse_maths_hints_smoke.py`, about 13 s).** Added: topic `rule_sound` (candidate differs from the key, is rejected by the checker, and matches itself) and `rule_reachable` on real questions, with extra seeds for rarely drawn variants; `no_collision` for topic messages; 163 topic worked examples plus 40 collision, precedence, guard, accuracy and bad-record cases; negative controls (existing); mutation (every topic rule perturbed by 5% plus one, every family truth perturbed by one: 248 of 248 caught); copy lint on all 103 messages; D5 scan of fired topic messages; no-leak across the check route, the generate route, client payload, set-work freeze and reveal, lesson quiz and nine writers; the record unit tests; a session-size ceiling; drift (1,072 slots generated with and without the wrapper compared field for field after removing the SVG element counters that rise on every call, 268 compared for random state; no generator or client file mentions `answer_record`); coverage ratchets.

**Drift.** Generated questions are byte-identical to the base (5,049 slot-runs hashed before and after, excluding the new key). No generator file changed.

**Deferred.**

- Multi-part (`number_fields`) per-part rules, and families that record twice (graphs, graphical simultaneous equations): Phase 5. No record is stored for them.
- Wave C and D topics (bearings, geometry angles beyond the Phase 1 rules, probability, statistics, sequences, algebra, transformations, vectors multipart).
- Standard form (power off by one), speed as distance times time, density inverted, unit conversion slips on non-recorded variants: these slots are non-scalar or have no `record()` line yet; adding the lines is a small generator change that Phase 2 did not make.
- Topic messages in Quick Test and set work (the storage decision above).
- Per-rule context strings on `record()` lines (for example `given='diameter'`): not needed, since the inputs and the guard were enough.


---

## 16. Phase 2 review notes (2026-10-26, independent review, not committed)

**Method.** Every recorded family was generated on real practice questions (3 to 12 seeds per slot, all 197 slots that carry a record, including the 18 bearings questions that reuse `trig_*`, `pyth_hyp` and `ratio_map_scale`), every rule's value was worked out and read beside the question as a maths teacher would, looking for values that another slip, a copied number, a near miss or a correct form would also explain. The cases where a topic message replaces a different generic message (75 in the smoke's run; 42 of 12 kinds in a 4-seed probe) were read one by one. The capture, the session, the check route, set work, Quick Test, lesson quiz and every database writer were traced in the code, and a Flask test client generated 162 practice pages (113 of them with a record in the session) and checked answers, scanning the HTML and every response. Seven hand mutations were run against the smoke.

**Findings and fixes.**

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | High | A rule's value that equals a number printed in the question was named as a slip. For a 3, 4, 5 cuboid the face diagonal is 5, the height; "1/4 as a decimal" typed as 4 was told "This one needs a division" (1 times 4) when it is far more likely 4 divided by 1, which the generic rule names; for 5 workers taking 5 hours, 7 workers, the direct-proportion value is 7; at 45 degrees a wrong ratio gives back the given side. 72 such values in 12 seeds, across 20 rules. | A topic value that equals a recorded input (at the accuracy the pupil gives) is silent, and the generic rules run as in Phase 1 (so 1/4 typed as 4 now gets "divided the other way round"). Not applied to answers in terms of pi (3 pi for a radius of 3 is the radius not squared, not a copied number), nor to `pct.reverse_two_added`, `pct.changes_added` (+15% then -15% taken to cancel gives the given price back: that is the slip) and the two mean-of-speeds rules (the mean of 80, 60 and 40 is the middle speed). |
| 2 | High | A topic value next to the key pre-empted the generic early-rounding line or named a slip for what is more likely a small arithmetic slip: a cuboid surface area of 254 typed as 252 was told "That looks like a volume"; with no stated accuracy, a value is also matched after rounding to the pupil's own places, so 79 for a key of 80 matched 79.2 (`pct.reverse_as_forward`) and was told "This takes the percentage of the new amount". 42 values in 12 seeds. | `_near_key`: a typed value within one step of the stated accuracy, or (no accuracy) within two units in the last place and 2% of the key, gets no topic message; the generic rules decide. 7 for a hypotenuse of 5 (sides added) and 79.2 for 80 are still named. |
| 3 | Medium | Radians coincidences: cos of 66 radians is almost minus one, so the cosine rule in radians gives 18.00 for b = c = 9, which is also the two sides added; the triangle-area formula with the sine left out is a plain slip that radians or a 30 degree angle can land on. | `QUIET` values per family, silent when matched: for `trig_cosine_side` b + c, the difference of the sides and the root of the sum of squares; for `trig_area` a b / 2 and a b. |
| 4 | Medium | `pct.wrong_base` never fired on percentage error: the estimate was taken as the base, which made the "wrong base" value equal the key. The messages also spoke of "a percentage change" and "the original amount", which do not fit an error question. | The actual value is the base; two new rules and messages, `pct.error_wrong_base` ("Check which amount to divide by. Percentage error compares the error with the actual value.") and `pct.error_not_compared` ("That is the size of the error. A percentage error compares it with the actual value."). |
| 5 | Medium | Messages that named the wrong concept for the question: the triangle area with a b sin C not halved was told "the answer for a full rectangle ... A triangle or trapezium"; the cosine used in place of the sine was told "Label the sides from the angle first" (there is no opposite or adjacent in that formula). | New `trig.area_parallelogram` ("That looks like the area of a parallelogram. A triangle covers only part of it.") and `trig.area_sine` ("Check the formula. The area of a triangle uses the sine of the angle between the two sides."). "parallelogram" joins `HINT_LONG_WORD_ALLOW`. |
| 6 | Low | Messages that fit only one of the slips giving the same value. 2 pi r for a circle area is the circumference, or the radius doubled instead of squared; 90 minus the angle in right-angled trigonometry is the other acute angle reached either by swapping opposite and adjacent or by using cos instead of sin. "Only one unit was converted" was stated as fact, not hedged. | Reworded: "That looks like the circumference. For an area, the radius is squared, not doubled."; "That is the other acute angle. Label the sides from the angle you want, then pick the ratio."; "It looks like only one unit was converted. Both the distance and the time units need changing." |
| 7 | Low | `product` recorded for g/cm³ to kg/m³ with the 1000 not printed (`derived`): "This one needs the numbers multiplied" speaks of numbers the pupil cannot see. | `build_record` keeps no record for `product` or `quotient` when an input is derived (that one slot falls back to the generic rules). |
| 8 | Low (cost) | A record is read from the signed session, but nothing bounded its numbers: a years or power input of 10 to the 9 would make an exact power run for a very long time; a string input like `1e999999` was read as a Fraction. | Inputs over 10 to the 12, non-finite floats and long or exponent-style strings are refused (`F`); years, powers and indices must be whole numbers from 0 to 60 (`_n`); `read_record` checks the 256-byte cap again. Each refusal means only that the record is not used. |
| 9 | Low | `_plain` turned a list holding an object that is not JSON into `None` instead of refusing it. | Refused (no record). |
| 10 | Coverage | Density inverted (volume over mass) and speed as time over distance with no stated accuracy were never matched: the generic reciprocal rule matches only the exact value, and 25/185 cannot be typed exactly. | New `op.quotient_inverted` on `quotient` records with the generic reciprocal message, matched at the pupil's own places. Speed as distance times time was already `op.multiplied_for_quotient`; standard form with the power one out is the generic place-value line (`gen.pow10`, apt); a standard form answer type has no topic rule (not a one-line change). |

**False-diagnosis probes kept as they are (judged apt or harmless).**

- *Circle area, radius given, typed 4 pi r squared* ("the diameter was used as the radius"): this is the pupil who uses the area formula with d, which the message names. It is also the sphere surface formula by coincidence; rare, and the message still sends the pupil to the right check. Kept. A circle area value for r = 2 (circumference and area both 4 pi) equals the key and is dropped by design.
- *Sector and arc questions* get their own messages ("That is the whole circle. The question asks for only part of it."), never a circle-area message; semicircles are not a recorded family.
- *Rectangle 2 by 2* (area 4 equals half perimeter 4) and *ratio 2 : 4 with A = 14* (parts swapped and amount for one are both 7) stay silent through the collision rule.
- *Trig radians to 1 d.p.* (60 degrees typed as 1, 53.1 typed as 0.9): the radians value rounded as told; no other common slip lands there. A ratio-only value whose rounding moves it more than 5% is matched only exactly, so it cannot fire by accident.
- *Phase 1 `ang.complement`* runs only in geometry angles and circle theorems, so it never meets `trig.angle_other`; if a trigonometry record ever appeared there, the topic message (which names the same 90 minus value) wins.
- *Precedence.* All 12 kinds where a topic message replaces a different generic one were read: a map distance not converted, the hypotenuse squared (100 for 10), cm² to m² by 100, one speed unit converted, a negative power, the amount for one (4 for 40) and so on, each where the generic "place value", "sign" or "reciprocal" line guessed the same value less precisely. With no topic hit, or a quiet or near-key value, the generic rules run unchanged (unit cases).
- *Arithmetic expressions:* the left-to-right, brackets and power-as-product values were checked on every BIDMAS expression shape the generators record; odd powers of a bracketed negative give the key and are dropped.

**D5 and copy.** All 107 messages pass the `system_hint` lint (two sentences at most, 120 characters, British spelling, no dashes, no emoji, reading grade at most 8) and the smoke's scan for values in fired messages; no new message states a value or a factor ("a triangle covers only part of it", not "half"). Tone matches Phase 1: an observation, then one action. `docs/ZORP_CHARM.md` Appendix A regenerated.

**Leak analysis.**

- *Client.* Practice page HTML, `POST /api/v1/problems/generate` and every check response (including a check request that carried its own `answer_record`, which is never read) were scanned in a live test client: no `answer_record`, no family name with inputs. `_problem_client_payload` is a whitelist; `strip_problem_keys` removes the key on every set-work way out; the QOTD is multiple choice and never carries a record.
- *Storage.* Every writer of a problem body (saved, shared, suggested, challenge, quiz attempt, Quick Test, lesson quiz, set-work preview and assignment, frozen payload) goes through `public_problem(s)` or `NOT_FROZEN_KEYS`; the variant queue stores names only; activity events, attempts and cohort samples never held the problem. The subject access export and account deletion read database rows only, so the record cannot reach them. Nothing is logged: the only logger call is `app.logger.exception` in the 500 handler, which writes the traceback, not the session.
- *Session cookie.* The Flask session is signed, not encrypted: a pupil can decode it and read `answer_record` (for example `{"f":"pyth_hyp","i":{"a":6,"b":8}}`). That shows the family name and the numbers the question prints (presence guard), next to the key and the solution the practice session problem already holds. It reveals nothing new. Recorded and accepted.
- *Threads and drift.* `capture()` uses its own `ContextVar`, set and reset around one generator call, so records cannot cross requests or threads, and a nested call keeps its own sink. The wrapper runs after the generator, draws no random number and only adds a key; the smoke compares 1,072 slots with and without it and the random state on 268.

**Quick Test.** Keeping the record out of `quicktest_sessions` is the right default, and it is unchanged. Recommendation to David: keep generic hints in Quick Test and store no new data; the topic messages there would need the record in that table (a new stored field and DPIA and ROPA lines) for a feature whose answers are reviewed on the results page anyway.

**Mutation (by hand on the working tree, restored and checksummed).** `answer_record` removed from `SERVER_ONLY_KEYS`: fails (`no_leak`; the answer-check smoke also asserts the set). Truth guard bypassed: fails (`unit_table` 2, `mutation` 92). Precedence broken (generic first): fails (`unit_table` 11, `rule_reachable` 149). Two topic messages letting the generic rule step in: fails (`unit_table` 1). A value added to a message: fails (`copy_lint`). Quiet values off: fails (`unit_table` 3). Near-key guard off: fails (`unit_table` 2). The smoke's own perturbation catches 251 of 251 topic rules and truths and 14 of 14 generic rules.

**Coverage after the review.** The arithmetic holds: the nine topics hold 321 of 1,072 practice slots (29.9%) and 223 single-value ones, so 30% is out of reach in this phase. 196 slots carry a record (one fewer: finding 7), 192 (17.9%) can produce a topic hint (one fewer); either hint 780 (72.8%, unchanged). 154 topic rules over 97 families, 94 message ids (4 new). 154 of 154 fire on generated questions; 14 silent collisions. The ratchet floor (190) stands. The smoke has 222 topic hand-worked examples and 17 new review cases (quiet values, near key, percentage error, pi coefficients, bad and huge records, the 256-byte check on read), and runs in about 13 s.

**Files changed in review.** `generators/shared/misconception_topics.py`, `generators/shared/misconceptions.py`, `generators/shared/answer_record.py`, `models/zorp_voice.py` (one allowlist word), `scripts/test_gcse_maths_hints_smoke.py`, `docs/ZORP_CHARM.md` (Appendix A), this file.


---

## 17. Phase 3 build notes (2026-10-26, not committed)

**What was built.** The hint ladder on the GCSE maths practice page, the locked Show answer drawer, the graded generic message in set work and lesson-quiz results, the D8 cohort wording and the three `site.js` dashes.

### Decisions as confirmed by David (and how each is built)

| Decision | Built as |
|---|---|
| **D1** Show answer locked until the last rung | `templates/index.html`: for a GCSE maths question with something to answer (`problem.options or problem.correct_answer_raw`) the drawer is `<details class="answer-reveal" hidden>` and a status note sits above it (`role="status"`: "Show answer opens once you have answered or used the hints."). `site.js` `unlockAnswer()` removes `hidden` and rewrites the note to "Show answer is now open." (read out by the live region, no focus move). Other subjects (GCSE computer science, physics, science) keep the open drawer. **It is pacing, not security:** the key (`data-correct-raw`), the solution (in the hidden `<details>`), the pre-attempt Hint drawer and `normalized_correct` on a wrong check are all still in the page or the response. Serving the solution from a session-bound endpoint after the last rung is the separate, larger decision of section 5.1. |
| **D1a** unlock on a correct answer | Typed: `showHintLadder` on `data.correct`; multi-part: when every part is correct; ordered proofs: on `data.correct`. The hint line is cleared at the same time. |
| **D3** rung 1 automatic, bigger hint pulled | After a wrong typed answer the check response carries `hint: {kind, rung: 1, text?, bigger}` (only when the request says `hint_ladder: true`). Rung 1 is the Phase 1/2 message in the feedback line when a slip is recognised, otherwise the `Hint:` line (the nudge). "Show a bigger hint" is a real `<button>`; pressing it shows rung 2 (`Bigger hint:` plus the first step of the stored solution that does not show the key) and opens Show answer. If no step qualifies (27% of typed slots, mostly one-line solutions) the button reads "Open Show answer" and opens it straight away. The rung lives in `block.dataset.hintRung`; a reload or a new question starts again; nothing is stored. After the press the button is disabled, not removed, so keyboard focus stays put. |
| **D1b** practice MCQ unlocks with the pick | The MCQ click handler calls `unlockAnswer()` (the right option is already highlighted). No ladder and no MCQ note (Phase 4). |
| **D1c** Quick Test | The Quick Test page has no Show answer drawer at all (results page opens every answer, unchanged) and no ladder element, so its pupils see the existing one-line feedback only. The server also refuses a ladder for a Quick Test question: `_sync_last_problem_payload(..., source='quicktest')` marks the session problem (19 B in the cookie, Quick Test only) and the check route checks it, so a hand-made `hint_ladder` request gets nothing. |
| **D1d** pre-attempt Hint drawer | Untouched (a test pins it). |
| **D1e** other drawer pages | `saved_problem`, `shared_question`, `suggestion_view`, `qotd` unchanged (a test scans them for the lock, `ladder_copy` and `hint_ladder`). |
| **D8** cohort line | `formatCohortHint(cohort, hinted)`: "About N% of attempts needed another go (n attempts)." on a ladder page after any wrong answer (it stays after a later right one); Quick Test, MCQ and other pages keep "got this wrong". Browser-checked with an injected cohort object. |
| Set work | `serialize_student_work` adds `hint_message` to a graded, wrong, typed GCSE maths answer (from `graded_message`, generic rules only, because `answer_record` is never frozen). Unanswered questions get nothing and still lose the key and solution. `student_class_work_detail.html` shows the line after "Your answer". The API (`POST /api/v1/me/class-work/<id>/answer` and `GET`) returns it in `class_work.problems[i]`. Nothing is stored. |
| Lesson quiz | `hint_message` per question on the results page and in `GET /api/v1/lesson-quiz/<id>/results`, built at fetch time. No message in a question or answer response (tested end to end). **Note:** every GCSE maths lesson quiz is multiple choice today (0 typed questions in 32 topics), so this fires only for typed questions (mixed quizzes, or Phase 4/5 work); the test injects two typed questions into a stored session. |

### Copy (all lintable, in `generators/shared/misconceptions.py`)

- `LADDER_COPY`: `hint` "Hint:", `bigger` "Bigger hint:", `more` "Show a bigger hint", `open` "Open Show answer", `locked` "Show answer opens once you have answered or used the hints.", `opened` "Show answer is now open." The template renders them (`ladder_copy` Jinja global, `data-*` on `.free-response-hint`); `site.js` holds none (a test checks).
- `NUDGES`: one line per GCSE maths topic (32), used when the problem's own hint is long (over 160 characters), shows the key, or is missing. A per-family line is still possible (`NUDGES[family]` is tried first) but none is written; deferred to Phase 5. Last resort `NUDGE_DEFAULT` "Check each step against the numbers in the question."
- `models/zorp_voice.py` `extract_hint_messages` now reads `MESSAGES`, `NUDGES` and `LADDER_COPY` on the `system_hint` surface (house style, 120 characters, two sentences, reading grade, kind words as errors). Four nudges were reworded to pass; Appendix A of `docs/ZORP_CHARM.md` regenerated.

### How rung 1 and rung 2 are chosen (`build_ladder`)

1. Rung 1: a recognised slip is the feedback line (no `text`). Otherwise `NUDGES[family]`, else the problem's own `hint` (plain text, at most 160 characters, never showing the key), else `NUDGES[topic]`, else the default. 909 of 1,005 typed practice slots use their own hint; the rest use the topic line.
2. Rung 2: the stored solution split on `<br>` or line breaks; the first step that is plain, at most 200 characters, free of `$`, `<svg>`, `<pre>`, and that does not show the key (any number equal to a key part, also at the key's accuracy, a fraction written with `\frac`, a non-numeric key as a word or string; a negative key is shown only by a number with a minus sign). LaTeX in `\( \)` is allowed: the page typesets it with MathJax after inserting it as text. 733 of 1,005 typed slots have a rung 2.
3. A recognised slip still gets the ladder, so a pupil who repeats the slip can still reach the worked answer. An unreadable answer ("Enter a valid number") gets no ladder (it is not an attempt).
4. Known limit: the first step that hides the key can be a strong hint when the working is short (for example "b² = c² − a² = 11² − 5² = 96", leaving only the square root). That is what section 5 asks for; softer rules (cap at the first two lines) are Phase 5 candidates.

### Accessibility

- The hint area sits directly under the feedback line, above the "What tripped you up?" panel (browser-checked while logged in), and is two `aria-live="polite"` paragraphs (empty until used, hidden when empty). No `tabindex`, no `focus()` anywhere in the ladder script (a test scans it).
- The locked drawer is not an inert control: the `<details>` is `hidden` (not rendered, not focusable) and a visible sentence explains how it opens; the sentence is a status region that announces the unlock.
- The bigger hint is a native button (Enter and Space work; browser-checked with the keyboard). It is disabled after use, never removed.
- No animation or transition was added (reduced motion and motion off need nothing new; checked in a reduced-motion context); colours use the existing tokens, so light and dark both work; 360 px width has no horizontal scroll.
- Zorp: no new expression; `reactMascot('wrong')` and the soft sound are unchanged. Nothing in the ladder speaks as Zorp.

### Byte ledger and pins

| File | Before | After | Change | Cap |
|---|---|---|---|---|
| `static/js/site.js` | 207,046 | 209,449 | +2,403 | **209,546** (new `SITE_JS_MAX_BYTES` in `scripts/test_gcse_maths_hints_ladder_smoke.py`: baseline plus 2,500) |
| `static/css/practice.css` | 31,381 | 31,947 | +566 | +600 |
| CSS total / core | 237,078 / 212,086 | 237,644 / 212,652 | +566 | 246,000 / 216,000 (core headroom 3,348) |

`site.js?v=35`, `practice.css?v=30`, `sw.js` `CACHE_VERSION = 'pb-v106'`; `test_pwa_smoke.py`, `test_zorp_charm_smoke.py` and `test_zorp_expression_smoke.py` pin the new version; ledger lines added in `test_u8_a11y_smoke.py`. The three em dashes are gone from the answer strings (MCQ "Not quite. The correct answer is highlighted." in two places and "Not quite. Try again."). Two other em dashes remain in `site.js` toasts of the reflection panel ("Thanks, em dash, noted." and "Could not save your note, em dash, try again."); they are not answer feedback and were not in scope. Generator hints used as rung 1 can contain a dash of their own (for example "Count horizontal and vertical steps, em dash, they are the two shorter sides."): that is existing generator text, also shown in the Hint drawer.

### Files changed in Phase 3

`generators/shared/misconceptions.py` (ladder, nudges, copy, `graded_message`), `app.py` (check route ladder, Quick Test source mark, results routes, `ladder_copy` global), `models/class_assignments.py`, `models/zorp_voice.py`, `templates/index.html`, `templates/partials/free_response_inline.html`, `templates/student_class_work_detail.html`, `templates/lesson_mcq_results.html`, `templates/base.html`, `static/js/site.js`, `static/css/practice.css`, `static/js/sw.js`, `docs/API.md`, `docs/ZORP_CHARM.md` (Appendix A), `docs/AI_HANDOFF.md`, this file, and tests: new `scripts/test_gcse_maths_hints_ladder_smoke.py` (about 4 s), edited `test_gcse_maths_hints_smoke.py` (copy lint reads the new dictionaries), `test_zorp_voice_smoke.py`, `test_u8_a11y_smoke.py`, and the three cache pins.

### Tests

`scripts/test_gcse_maths_hints_ladder_smoke.py`: `template` (locked drawer and status note, hint area under the feedback with two polite regions and a hidden real button, MCQ locked with no ladder, other subjects open, Quick Test with no drawer or ladder, other drawer pages unchanged), `route` (no ladder unless `hint_ladder` is `true`; slip, nudge, correct, unreadable; Quick Test by mark and by real flow; client key; other subject; multi-part part check; session unchanged; response keys), `ladder` (13 hand-worked cases; on 1,005 typed practice slots neither rung shows the key by an independent number scan, rung 2 is a step of the solution and the first that hides the key, at least 50% of slots have a rung 2), `graded` (unit cases, set work before and after grading, the rendered set-work page, a lesson quiz end to end, the results page), `client` (byte caps, pins, no em dash in answer strings, ladder script pieces, no copy in the script, no focus, no motion in the new CSS). Three hand mutations were caught (drawer not hidden, key check off, Quick Test mark ignored).

### Browser check (Playwright, Chromium, local app on port 5001, 127 checks, all pass)

Flow checked at 1280 px and 360 px, light and dark, plus reduced motion: Show answer hidden and the note shown on load; wrong typed answer with a known slip (the sign line) shows the slip in the feedback and the bigger-hint button, drawer still locked, focus unchanged, hint after the feedback in the DOM, two polite live regions; keyboard Enter on the button shows `Bigger hint: ...`, unlocks the drawer, note reads "Show answer is now open.", button disabled; a new question locks again; a wrong answer with no slip shows `Hint: ...`; a second wrong attempt keeps it locked; a correct answer unlocks and clears the hint; MCQ pick unlocks; Quick Test shows the one-line feedback with no drawer or ladder; logged in, the hint sits above "What tripped you up?"; no horizontal page scroll; no CSP violation; no console error except one 401 from the login-only `POST /api/v1/generator/mcq-answer` on a guest MCQ pick (existing behaviour, listed in section 1). D8 checked with an injected cohort object. Screenshots in `/mnt/user-data/outputs/hints_p3/` (20 files): `desktop_light_1_locked`, `_2_rung1`, `_3_unlocked`, `_4_nudge` and the same four for `desktop_dark`, `mobile360_light`, `mobile360_dark`; `mcq_1_locked`, `mcq_2_picked`; `quicktest_1_line`; `loggedin_1_reflection_below_hint` (all `.png`).

### Deferred

- Per-family nudge lines (`NUDGES[family]`), per-part rules and algebra rules (Phase 5).
- A server-held solution so the lock is real (a separate decision; today it is pacing).
- A softer rung 2 when the first qualifying step is nearly the whole working.
- MCQ option notes and the MCQ highlight note (Phase 4); `hint_message` for MCQ in set work and quizzes.
- A stale tab (the session holds a different question) gets "Problem mismatch" and no ladder; a reload fixes it. No escape hatch was added.


---

## 18. Phase 3 review notes (2026-10-26, independent review, not committed)

**Method.** The ladder code, the check route, the set-work and lesson-quiz paths, the template, `site.js` and the smoke were read against sections 5, 5.1, 6, 9 and 17 and David's confirmed decisions. Rung 1 and rung 2 were generated for every typed practice slot (1,005 slots, seed 0) and read beside the question as a maths teacher would, with a closer read of 120 random rung 2 lines, every line that changed, and every line that sits directly before the step that shows the answer; three more seeds (3,014 questions) were then scanned for the key. A Playwright walk-through ran on a local server (Chromium, guest and logged in, 1280, 360 and 320 px, light and dark, reduced motion). Ten hand mutations were run against the ladder smoke.

**Findings and fixes.**

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | High | Rung 2 showed the whole answer on 21 of 1,005 typed slots. The key check read numbers and plain words only, so an algebraic key in LaTeX slipped through: `(4x + 5)(x + 4) = \boxed{4 x^{2} + 21 x + 20}` (expand), `d = \dfrac{W}{F}` and five other one-step rearrangements, `y = (A - 1)/3`, `y = 6^2 = 36` for the key `y=36`, a graph reading `y ≈ 2×6 + 11 = 23` for `23~3.5`, and the factorised form `(x + 4)(x + 3) = 0` for the roots -4 and -3. | `reveals_key` also compares a loose algebraic form (LaTeX fractions and roots unwrapped, `\boxed`, spaces, brackets and multiplication signs dropped), reads the numbers of list keys (`6,-3`), assignment keys (`y=36`) and graph readings (`23~3.5`), and treats a factor such as `(x + 4)` as showing the root -4. An item of a list key that the question prints (3 < x ≤ 9) does not count, so good rung 1 hints such as "Substitute n = 1, 2, 3, 4 into 6n" stay. The smoke's independent scan gained the same three readings, written separately. |
| 2 | High | Rung 2 gave the answer away in effect on many more slots: in a short worked solution the first step that hides the key is often the step before it, with its result written out (`240 × 12/100 = 28.8`, then 240 + 28.8; `b² = 11² − 5² = 96`, then the root; `Volume = π × 33² × 98 = 335277.05 cm³`, then divide by 1000). In the first build 302 of the 733 rung 2 lines were the step directly before the step that shows the key. | Rung 2 now shows the method, not the number it produces: a worked-out number at the end of the step (not printed in the question, and not 0, 90, 180 or 360) is cut off, with any unit or bracketed note after it (`Find 12% of 240: 240 × 12/100`; `b² = c² − a² = 11² − 5²`). If what is left shows no working (`The common difference is d`), there is no rung 2 and the search does not move on, because a later step is nearer the answer (the first try did move on and produced `Missing term = 23 + 6`). A step that begins with `=` (the middle of a calculation) also ends the search. 80 lines are now cut; 219 lines still sit directly before the answer step, and on reading they are rules and methods ("Angle at the centre = 2 × angle at the circumference", "Expected frequency = probability × number of trials", "Subtract 2: 4x = -18 - 2") or rearrangement steps that still need the last operation. Coverage: 615 of 1,005 typed slots have a rung 2 (61%, floor 50%). |
| 3 | Medium | Ordering proofs and construction steps (`proof_steps`, 34 slots) got "Step 2. Triangle OAC is isosceles." as rung 2: the answer is the order, so any step placed is part of it. 46 or more slots used a line that only repeats the question as their bigger hint. | `proof_steps` never has a rung 2 (the button reads "Open Show answer"); a step that repeats the question (before or after cutting) is skipped. |
| 4 | Medium | A lesson-quiz question is also the session problem (`mode` `lesson`), and the check route grades it without a client key, so a hand-made `hint_ladder: true` request during a lesson quiz returned the nudge and a solution step. | The route refuses the ladder when the session problem's mode is `lesson`, as for the Quick Test mark; a new route case and a mutation cover it. (Seen, not changed: the same hand-made request already returned the Phase 1 message, `correct` and `normalized_correct` mid-quiz; the lesson-quiz page itself carries `data-correct-raw` for typed questions. That is the pre-existing practice-style exposure and every GCSE maths lesson quiz is multiple choice today.) |
| 5 | Medium (copy) | The locked note said "Show answer opens once you have answered or used the hints." After a first wrong typed answer the pupil has answered and the drawer stays shut, which reads as a broken promise. The same note showed on multiple-choice questions, which have no hints. | "Show answer opens after a correct answer or after the hints." for typed questions; "Show answer opens once you pick an answer." (`locked_pick`) for multiple choice. Both pass the `system_hint` lint; Appendix A regenerated. |
| 6 | Medium (a11y) | The pressed "Show a bigger hint" button was set `disabled`; in Chromium a focused button that becomes disabled drops focus to the page body, so a keyboard or screen-reader user lost their place (checked: `document.activeElement` was BODY). | The button gets `aria-disabled="true"` instead (the existing `.btn[aria-disabled="true"]` style dims it) and the handler ignores a pressed button; focus stays on it (browser-checked) and a second press changes nothing. |
| 7 | Low (safeguarding) | D8: "About N% of attempts needed another go" frames the number as attempts, not people, and normalises a miss. But straight after a pupil's miss a low share ("About 6% of attempts needed another go") is a comparison with others that can discourage (Children's Code standard 13, best interests). | On the hint page the line is not shown when the share is under 20%; from 20% it reads as before. The minimum sample of 20 (`models/cohort_stats.py`) is unchanged. Browser-checked with injected cohorts of 42% (shown, wording exact) and 8% (hidden). |
| 8 | Low | `plain_line` dropped `<br>` without a space, so a hint read "two places right.Example: ...". Generator hints and steps shown as rungs kept their spaced em dashes ("Wall and ground are perpendicular, em dash, ladder is the hypotenuse."), against the house style for a line the page presents. | Line breaks and block tags become a space; a spaced em or en dash becomes a colon ("... perpendicular: ladder is the hypotenuse.", "Step 1: multiply ..."); ranges such as 1–3 are untouched. The slot check fails on a spaced dash in either rung. |
| 9 | Low (copy) | The two reflection-panel toasts in `site.js` still had em dashes. | "Thanks, noted." and "Could not save your note. Please try again." (`site.js` was already at `?v=35` in this change set; no further bump.) |

**Judged and kept.**

- *The cross glyph.* The feedback line keeps its "✗" before a slip message: it is the house wrong-state marker and the only non-colour cue for that state (WCAG 1.4.1), it is a neutral glyph, not a face, and Zorp keeps `oops-encourage`. The hint lines ("Hint:", "Bigger hint:") carry no glyph and no red, which is right: they are help, not a verdict.
- *Copy.* Nudges, labels and slip lines are short, hedged and kind; none blames the pupil. Rung 1 often reuses the problem's own hint, which the pre-attempt Hint drawer already shows (D1d), so a long generator hint (for example "Multiply by 100: 0.5 × 100.") can be strong; it is not new exposure.
- *D8 wording.* Kept as built for 20% and over.
- *Set work and lesson-quiz results.* The message appears only after grading (browser-checked on a real class: before the answer the question shows nothing else; after it, "Your answer: 114 · Incorrect", the message, then the solution; unanswered questions are unchanged). Nothing is stored; `answer_record` is never frozen.
- *Pacing.* Hiding the drawer does not hide the key or the solution from the page (section 5.1), as documented.

**Browser walk-through (Playwright, Chromium, local server, all passing).** Typed Pythagoras with a nudge (locked on load, rung 1 `Hint:` line, keyboard Tab from Check reaches the button, Enter shows rung 2, the drawer opens, the note reads "Show answer is now open.", focus stays on the aria-disabled button, a second press changes nothing, a later wrong answer keeps rung 2 and the open drawer, a right answer clears the hint); geometry angles with a slip (message in the feedback line, empty hint line, button offered, rung 2 a rule); "New numbers" relocks; MCQ (pick note, a pick unlocks); Quick Test (one-line feedback, no ladder, no drawer, and the response carries no ladder); a multi-part ratio question (a wrong part gives the ladder, all parts right unlocks and clears); an ordering proof (button reads "Open Show answer" and opens the drawer, no bigger hint); set work as a pupil; logged in (hint above "What tripped you up?"); D8 with injected cohorts; 1280, 360 and 320 px in light and dark, with and without reduced motion: no horizontal scroll, no CSP violation, no console error except the known 401 from the login-only `mcq-answer` call on a guest MCQ pick. The only transitions on ladder elements are the existing `.btn` ones, neutralised at reduced motion. Seen, not changed: the Check button is disabled while a check runs, so focus drops to the body after Check (pre-existing; Tab still continues from there); the "Revise: Geometry_Angles" label shows an underscore. Screenshots: `/mnt/user-data/outputs/hints_p3_review/`.

**Mutation (by hand on the working tree, restored and checksummed).** Drawer rendered open: fails (`template`). Quick Test mark ignored: fails (`route` 3). Lesson-quiz gate removed: fails (`route` 2). Rung 2 key check off: fails (`ladder` 631). LaTeX algebra comparison off: fails (`ladder` 10). Worked-out number not cut: fails (`ladder` 99). Ordering proofs given a rung 2: fails (`ladder` 35). A nudge sent with an unanswered set-work question: fails (`graded`). Button `disabled` again: fails (`client`). Old locked wording: fails (`template`). 10 of 10 caught.

**Bytes and pins.** `site.js` 209,541 B (+2,495 on 207,046; cap 209,546, unchanged); `practice.css` 31,947 B (+566, unchanged in review); CSS total 237,644 and core 212,652 of 216,000 (3,348 B headroom). `site.js?v=35`, `practice.css?v=30` and `sw.js` `pb-v106` as built (bumped once in this change set). No inline script or `style=` added.

**Files changed in review.** `generators/shared/misconceptions.py` (key scan, rung 2 rules, `plain_line`, copy), `app.py` (lesson-quiz gate), `templates/index.html` (note per question kind), `static/js/site.js` (aria-disabled, D8 guard, two toasts), `scripts/test_gcse_maths_hints_ladder_smoke.py` (independent scan, 15 hand-worked review cases, slot checks for cut steps, question repeats and ordering proofs, lesson-quiz route case, client needles), `docs/ZORP_CHARM.md` (Appendix A), `docs/API.md`, `docs/AI_HANDOFF.md`, this file.


---

## 19. Phase 4 build notes (2026-10-26, not committed)

Notes on multiple-choice distractors: after a wrong pick in practice the feedback line adds one sentence that names the slip behind that option ("That works from left to right. Check which step comes first."). Nothing in a note states the correct value (D5). A distractor with no clear slip gets no note.

### How a note travels

1. **Tagging.** The procedural builders (`maths_bank_procedural_mcq.py`, `number_mcq` and `ratio_proportion_mcq` in `maths_num_stats_prob_rat.py`) tag a distractor as `(value, note_id)`. The tagged builders (`_letter_opts_tagged`, `_string_opts_tagged`, and `_number_mcq_options` / `_mcq_options`, which now accept tagged candidates) make exactly the random calls of their untagged twins, so the questions are byte for byte what they were (pinned, see Tests). After the options are built, `option_notes.attach` registers `{option text: note id}` for the tagged candidates that survived as options. Two tagged candidates that print the same text with different ids make that option ambiguous, so it keeps no note. The key never gets one. The note is keyed by option text, never by letter, because `make_problem` reshuffles the options.
2. **Wrapper.** `answer_record.with_answer_record` (already on every GCSE maths topic function) collects the notes in a `ContextVar` sink and stores the survivors as `problem['option_notes']`. For a fixed bank question with no tagged notes it asks `option_notes.bank_notes(problem)`, which looks the question up in `mcq_notes.BANK_WHY` (same question text, same key text, the distractor still an option). A reworded bank item therefore loses its note instead of keeping a wrong one. No bank item was edited.
3. **Server only.** `option_notes` is in `SERVER_ONLY_KEYS` (set work freezes it, `strip_problem_keys` removes it on every way out, answered or not), is not in `_problem_client_payload` (a whitelist), is dropped by `public_problem` / `public_problems` for saved, shared and challenge copies unless `keep_notes=True`, and is never read by a template. `keep_notes=True` is used in exactly four places: the two set-work writers (`class_assignments.py`), the Quick Test row writer (`quicktest.py`, which also serves the lesson-quiz API) and the lesson-quiz web session (`app._without_answer_records`). The data export carries no stored questions.
4. **Where a pupil sees it.** Practice: the endpoint below, after a wrong pick. Set work and lesson quizzes (API and web): `graded_message()` returns the note of the picked option for a graded wrong MCQ pick, so it arrives in `hint_message` after grading only. Quick Test: nothing during the test (no `data-note-qid`, the endpoint answers 403 for a Quick Test question); the results page shows the note under the badge of a wrong pick (`pick_notes`, new in `quicktest_results`).

### Endpoint `POST /api/v1/problems/option-note`

Body `{"letter": "A", "qid": "<tag>"}`. Works for guests. Since the whole-change review fixes (A5, 2026-11-03) nothing is written to `rate_limit_buckets`: the limit is a count per question kept in the signed session cookie (`on_n`). It reads only the practice problem in the session, never the request, and answers `{"ok": true, "note": "..."}` where `note` is `""` for the key, an option with no note or a damaged problem. The `qid` is a 10-character hash of the question and options (never the key), printed by the page as `data-note-qid` on `#mcq-options` only when the problem has notes; a stale tab gets 409 `session_mismatch`. Other refusals: 400 `invalid_payload`, 400 `invalid_letter` (not A to D), 400 `session_required` (no session, or the session problem has no options), 403 `not_available` (Quick Test source or lesson mode), 429 `rate_limited` (`OPTION_NOTE_PER_QUESTION_LIMIT` = 40 requests for one question; a new question starts a new count; it was `OPTION_NOTE_DAILY_LIMIT` = 300 a day per user or per IP hash before A5). Practice grades in the browser, so the server cannot see the pick itself: the request is the pick. The page only asks after a wrong pick, and the correct letter is already in the page (`data-correct`), so the endpoint tells a pupil nothing the page did not.

### Front end

`site.js` `fetchOptionNote` (about 680 B) runs in the wrong branch of `wireMcqBlock`: it posts the letter and `data-note-qid`, and if the answer carries a note and that button is still marked wrong (a late answer cannot land on a question that was reset by Try again), it appends the note to `#mcq-feedback` with `textContent +=`. `#mcq-feedback` is already an `aria-live="polite"` status region, so a screen reader hears the note as part of the feedback. No new element, no new class, no focus move, no motion, 0 B of CSS, Zorp unchanged. If the request fails or there is no note, nothing extra shows. Try again clears the line as before.

### Copy

`generators/shared/mcq_notes.py`: `NOTES` (35 `mcq.*` lines, new copy) and `BANK_NOTES` (16 `bank.*` lines), plain string literals read by the voice lint (`models/zorp_voice.py` `NOTE_DICTS`) on the `system_hint` surface: at most 2 sentences and 120 characters, grade at most 8, no long words off the allow-list, none of "wrong", "mistake", "just" and the rest. No digit in any note. A tagged option can also use an existing line (`misconceptions.MESSAGES` or a typed-rule message) so a slip keeps one wording for typed and multiple-choice answers. Three lines were reworded to pass the lint ("significant", "inequality", "everything" are long words). `docs/ZORP_CHARM.md` Appendix A regenerated.

### Verification (`scripts/gcse_verify/mcq_notes.py`, independent)

For each note the verifier recomputes the slip from the recorded inputs (`verify_hook.record`) and requires the tagged option to equal it (rounded half-up to the places the option prints; exact for fractions; a `Pred` for text options such as `a x 10^b` and error intervals). 73 slips, one per (note, family). An option worth the same as the key never verifies. Bank rows (`BANK_WHY`) are checked by `verify_bank_row`: the question exists in a bank with that key, the distractor is one of its options, and the slip, written as an arithmetic expression, evaluates (with the verifier's own exact evaluator) to the distractor. Rows about form rather than value (more digits is not bigger, not in simplest form, percent sign on a decimal) have no expression and are reviewed pins only. Every row plus the words of its note is pinned (`BANK_PINS`), so a changed bank question, option or note fails until it is reviewed.

### Coverage (the metric: verified distractors over all distractors of the waves A and B procedural multiple-choice generators)

40 seeds per generator: **3,735 of 5,400 distractors verified (69%)**, floor 50% (the smoke runs 5 seeds: 472 of 675, 70%). No note failed verification.

| Topic | Verified distractors | Share |
|---|---|---|
| mensuration | 234 of 240 | 98% |
| number | 1,825 of 2,160 | 84% |
| ratio and proportion | 798 of 1,080 | 74% |
| pythagoras | 160 of 240 | 67% |
| fdp | 264 of 480 | 55% |
| decimals | 240 of 480 | 50% |
| bidmas | 109 of 240 | 45% |
| compound measures | 80 of 240 | 33% |
| trigonometry | 25 of 240 | 10% |

Overall, across all 611 GCSE maths multiple-choice slots (3 runs each, 1,833 questions): 248 questions (13.5%) carry notes and 492 of 5,490 distractors (9.0%) have one. The rest are fixed banks with no clear slip, or fillers (prefer silence). Bank rows: 30 distractors on 26 questions (27 bank items: 15 fdp, 6 bidmas, 6 decimals).

### Example notes

| Topic | Question | Wrong option | Note |
|---|---|---|---|
| Mensuration | A circle has radius 9 cm. Using pi = 3.14, its area to 1 d.p. is: | 56.5 | That looks like the circumference. For an area, the radius is squared, not doubled. |
| Mensuration | The same, radius 3 cm | 9.0 | Check the formula. The area of a circle uses pi as well as the radius squared. |
| Pythagoras | A right triangle has shorter sides 12 and 16. The hypotenuse is: | 28 | That looks like the side lengths added or subtracted directly. Pythagoras uses their squares. |
| Trigonometry | Angle 30 degrees, adjacent 10. Opposite = (tan 30), to 1 d.p.: | 5.0 | Check which ratio fits. Label the sides from the angle first. |
| Number | What is the value of the hundreds digit in 8917? | 9 | That is the digit itself. Its value depends on the column it sits in. |
| Number | The same, 4652 | 60 | Check the column. Count the place values from the right: ones, tens, hundreds and so on. |
| FDP | After a 20% reduction, a price is 240. What was the original price? | 220 | That adds or takes off the percentage as if it were an amount. A percentage is a share of the amount. |
| FDP | 0.75 as a fraction in simplest form is: | 75/100 | That fraction can be made simpler. Divide the top and bottom by a common factor. |
| Decimals | x is rounded to 1 d.p. as 7.6. Write the error interval. | 7.6 <= x < 7.7 | That treats rounding as cutting off. Numbers a little below the value round to it as well. |
| Decimals | Which is the largest? (0.9, 0.19, 0.091, 0.099) | 0.091 | Compare the digits place by place. More digits does not mean a bigger number. |
| BIDMAS | What is 2 + 3 x 4? | 20 | That works from left to right. Check which step comes first. |
| BIDMAS | Evaluate (4 + 1)^2 | 17 | Check the brackets. The power applies to all of the bracket, not to one number. |
| Compound measures | Distance 90 km in 3 hours. Average speed = | 270 | Check the calculation. This one needs a division. |
| Ratio | Share 63 in the ratio 3:6. How much is the larger share? | 21 | That is the smaller share. The question asks for the larger share. |
| Ratio | Simplify the ratio 20:15. | 20:3 | Both parts of a ratio need dividing by the same number. |

### Byte ledger and pins

- `site.js` 210,208 B (+667 on 209,541; Phase 4 budget +900). **Cap raised 2026-10-26** in `scripts/test_gcse_maths_hints_ladder_smoke.py` (`SITE_JS_MAX_BYTES` 209,546 to 210,446, in two named steps) and in the new smoke (`SITE_JS_BASE_BYTES` 209,541 plus 900).
- `practice.css` 31,947 B (+0; budget +200). Core and total CSS unchanged.
- Cache pins: `site.js?v=36`, `sw.js` `CACHE_VERSION = 'pb-v107'` (`test_pwa_smoke`, `test_zorp_charm_smoke`, `test_zorp_expression_smoke`, the ladder smoke).
- New files: `generators/shared/mcq_notes.py` (copy, 10.8 kB), `generators/shared/option_notes.py` (mechanism, 8.5 kB), `scripts/gcse_verify/mcq_notes.py` (verifier, 24.5 kB), `scripts/test_gcse_maths_hints_mcq_smoke.py` (45.7 kB).
- Session cookie: the signed, compressed cookie with a GCSE maths MCQ problem is at most 651 B over 360 difficult questions of six topics, and the notes add at most 75 B (limit about 4,093 B).

### Tests

- New `scripts/test_gcse_maths_hints_mcq_smoke.py` (about 3 s, suite 108): catalogue and helper unit table (ambiguity, key never noted, shuffle keeps a note on its option, damaged problems); verified coverage with mutation tests (an option changed by one, a note under another slip's id, an option equal to the key must not verify); bank rows (real item, key, expression, reviewed pins, mutations, runtime lookup); a drift pin (`DRIFT_PIN`, a hash of question, options and key of every tagged generator over fixed seeds; it was computed after a snapshot diff of all 4,588 practice and MCQ slot runs against the pre-Phase-4 tree showed 0 changes); no-leak (practice page HTML and data attributes, generate API, `public_problem`, client payload, set-work freeze, student, teacher and preview payloads, lesson-quiz questions and answers, Quick Test page and row, exports, where `keep_notes=True` appears); endpoint abuse (guest, key, silent option, bad letter, bad and stale `qid`, no JSON, no session, typed question, Quick Test, lesson mode, rate limit); graded (set work, lesson-quiz results and Quick Test results show the note for a wrong pick only); client pieces and byte caps.
- Updated: `test_answer_check_smoke` (`SERVER_ONLY_KEYS` now includes `option_notes`), `test_zorp_voice_smoke` (the extractor sees `NOTES` and `BANK_NOTES`).

### Browser check (Playwright, Chromium, local app on port 5077, 173 checks, all pass)

Guest at 1280 px and 360 px, light and dark (bidmas, fdp, decimals bank notes), and a logged-in user at 1280 px light (pythagoras and mensuration at difficult, bidmas) and 360 px dark (number and ratio at difficult, fdp). Each: a wrong pick shows the usual line plus one note, the correct option is highlighted beside it, `#mcq-feedback` is a polite live region, focus is not moved, no digit or dash in the note, no horizontal scroll, Show answer unlocks, Try again clears the note, no CSP violation. A question with no notes shows nothing extra and has no `data-note-qid`; a right pick makes no note request; a Quick Test question makes none either. The only console error is the known guest 401 from `POST /api/v1/generator/mcq-answer` (login only); the new endpoint does not make it moot, because the pick is still persisted there for logged-in users, and it adds no error of its own. Screenshots: `/mnt/user-data/outputs/hints_p4/`.

### Deferred

- Trigonometry coverage is 10%: there are only two procedural trig generators. Find-the-side has one named slip (the wrong ratio); the exact-values table has options that differ in form (cos for sin, a degree over 180) with no single slip behind each, so they stay silent.
- Bank notes cover 27 of 450 bank items. More need a reviewed slip per item; the `BANK_WHY` table and `verify_bank_row` are the place to add them.
- Compound measures, bidmas and fdp procedural builders keep several fillers that have no single slip.
- The practice endpoint cannot observe the pick (practice grades in the browser), so it only refuses what it can: no session, stale tag, Quick Test and lesson questions, and rate.
- A note for a lesson-quiz question is shown on the web results page and the API results through `hint_message`; the lesson MCQ results template (`lesson_mcq_results.html`) needed no change.


---

## 20. Phase 4 review notes (2026-10-26, independent review, not committed)

**Method.** Every tagged generator (37 procedural MCQ functions of waves A and B, 18 `number_mcq` and 9 `ratio_proportion_mcq` types) was run over 40 seeds; every distinct note was read beside its question and option as a maths teacher would, and for each noted option the probe also checked whether the option is worth the key in another unit or at a coarser rounding, and whether a different slip (any other `SLIPS` entry for the family) lands on the same value. All 27 bank items that carry a `BANK_WHY` note were read by hand. The verifier was read line by line for slips that copy the generator instead of the maths. A Flask test client walked practice (guest and logged in), the generate API, a real class with set work (teacher preview, assignment, pupil API and page before and after grading), the lesson quiz (web and API), Quick Test (web and API), QOTD, saved and shared copies and both data exports, posting every letter to the endpoint on each surface. Drift was compared against a tree rebuilt from `1bd6362` plus the pre-Phase-4 patch (`since_1bd6362_latest.patch`; the rebuilt tree differs from the working tree in exactly the Phase 4 files). A Playwright walk-through ran on a local server, and fifteen hand mutations were run against the smoke.

**Findings and fixes.**

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | High | Map scale (`ratio_proportion_mcq` type 4): the option "300 m" for "A map scale is 1:10000. A road is 3 cm on the map. What is the real distance?" (key "0.3 km") is the right distance in metres, and the question names no unit. It carried "Check the units. There is one more conversion to make.", telling a pupil with a right answer that they slipped. The verifier passed it because it compared units as text. | The option has no note; `mcq.map_unit_step` is deleted. The verifier compares lengths in metres (mm, cm, m, km), so an option in other units that is worth the key never verifies. The question itself had two correct options. **Resolved 2026-10-26:** it now asks "What is the real distance in km?" and no option is the key in another unit (the "300 m" option became "300 km", the metres left unconverted), and the verifier compares lengths, areas, volumes, masses, times and money across units (`docs/GCSE_MATHS_VERIFICATION.md`, "Fillers and units"). |
| 2 | Medium | Percentage error (`number_mcq` type 15): "6%" beside a key of "5.9%" (estimate 96, actual 102) carried "That is the size of the error". 6% is also the right answer rounded to a whole percent, which is the likelier route. 3 in 40 seeds. | A general guard in `option_notes.attach`: an option that is the key rounded to fewer decimal places, in the same unit, keeps no note unless the note is itself about rounding (`ROUNDING_NOTES`: `gen.accuracy`, `mcq.round_dropped`, `mcq.round_place`, `mcq.digits_cut`). The verifier refuses the same case independently. |
| 3 | Medium | HCF (`number_mcq` type 16): for 48 and 72 the option 2, and for 90 and 150 the option 3, carried "That is what is left after dividing by the HCF". Both are common factors of the two numbers, so the likelier slip is a common factor that is not the highest. | The cofactor note stays only when the cofactor does not divide the other number (60 and 84, option 5). Otherwise the new `mcq.hcf_not_highest`: "That divides both numbers, but it is not the highest. Look for a bigger common factor." The verifier checks both conditions. |
| 4 | Medium | Equal split (`ratio_proportion_mcq` types 2 and 9): "Share £135 in the ratio 2:7" offers "£67" (`total // 2`) with "That shares the amount equally". Half of £135 is £67.50. The verifier copied the generator's floor division instead of the maths. | The note is tagged only for an even total. The verifier now uses exactly half and only for a two-part ratio. |
| 5 | Medium | Price increase (`ratio_proportion_mcq` type 6): "£3" for "£10 increased by 25%" (key "£12.5") carried "That is the size of the change". The change is £2.50; the option is the generator rounding it to whole pounds. | The note is tagged only when the change is a whole number of pounds. The verifier no longer rounds a slip to fewer places than the key prints. |
| 6 | Low (copy) | `mcq.pct_of_inverted` said "It looks like the percentage was divided by the amount, not the other way round". The other way round (amount divided by the percentage) is also wrong, so the line pointed to a second slip. | "That divides the percentage by the amount. A percentage of an amount is a share of it out of a hundred." |
| 7 | Low (copy) | In ratio sharing (types 2 and 8) the value of one part carried `ratio.unit_only`, "That is the amount for one. Now scale it up to the number asked for.", which is written for unitary questions ("one pen") and asks no number in a ratio question. | New `mcq.ratio_one_part`: "That is the value of one part. The share needs the right number of parts." The unitary pens question keeps `ratio.unit_only`. |
| 8 | Medium (a11y) | `site.js` added the note with `feedback.textContent += ...`. That replaces the live region's text node, so a screen reader reads "Not quite. The correct answer is highlighted." a second time before the note. | The note is appended as a new text node, so the polite region announces only the note (browser-checked with a `MutationObserver`: the second change adds just the note and removes nothing). |
| 9 | Low | A guest's MCQ pick still called the login-only `POST /api/v1/generator/mcq-answer`, which answered 401 on every pick (the console error noted in sections 17 and 18). | `persistMcqAnswer` returns at once for a guest (`isReflectionEligible()`, the same logged-in flag the reflection panel uses; every page with an MCQ block extends `base.html`). The behaviour for guests is the same as before, minus the failed request. Logged-in picks still persist (browser-checked: 200). No extra cache bump (`site.js` was already at `?v=36` in this change set). |

**Probed and kept.**

- *Two slips on one value.* "Increase 100 by 20%", option 80: applied the opposite way, or 20 taken off as an amount. Both are direction slips, and the note ("Check the direction of the change...") fits both. Standard form products where the multiplied indices equal the power plus one (5 × 10^4 times 6 × 10^2, option 3 × 10^8): the index note is the more specific reading. Kept.
- *Same value, wrong form.* "14 × 10^8" beside "1.4 × 10^9" and "0.52 × 10^-3" beside "5.2 × 10^-4" carry "Check the front number" by design: the value is right, the form is the slip.
- *Rounding notes.* "Round 12.384 to 1 decimal place", option 12 ("That drops the decimal part") is the key rounded to a whole number, which is exactly the slip named, so rounding notes are exempt from the guard of finding 2.
- *Notes shown in red.* The note sits in the red feedback line after "Not quite.", as the typed-answer slip messages of Phases 1 to 3 do. The ladder's "Hint:" lines are neutral; a slip note is part of the verdict line. No CSS change.
- *Bank notes (27 items, 30 rows).* All read by hand and kept: each names the slip that gives the distractor exactly, and none states the answer. "1.2 × 0.5 = 6" ("The digits look right but the decimal point is missing") is literally true of 0.6 and 6.
- *Verifier.* The slips are written from the maths and read only recorded inputs. The swapped-id and off-by-one mutation tests in the smoke bite. Apart from findings 1, 2, 4 and 5 (now fixed), no slip echoes its tag.
- *Copy.* The 36 `mcq.*` and 16 `bank.*` lines pass the `system_hint` lint: British spelling, no dashes, no emoji, no digits (D5), at most two sentences and 120 characters, reading grade at most 8, none of the shaming words. Appendix A of `docs/ZORP_CHARM.md` is regenerated.

**Leaks and abuse (test client, 77 checks, all passing).** Nothing leaks before a pick or before grading. The only output that ever names a note's id or text is the endpoint after a wrong pick in practice, or `hint_message` after grading. These were scanned for every note text, every `mcq.*` and `bank.*` id and the key `option_notes`, and none appeared:

- the practice page and its data attributes (only `data-note-qid`, a hash of question and options)
- the generate API
- the QOTD page and API
- the teacher preview and assignment payloads
- the pupil set-work API and page before grading, and the other questions after one is graded
- the lesson quiz page and the API start response
- the Quick Test page and its API start, question and answer responses
- the saved row and page, and the shared API and page
- both data exports (`/me/export`, `/api/v1/me/export`)

The endpoint was abused on every surface:

- **Set work.** Posting each letter with a frozen question's fingerprint gives 409 or 400 and no note. The set-work page never puts its question in the session.
- **Lesson quiz and Quick Test.** Every letter gives 403: lesson web, Quick Test web over six questions, and Quick Test API.
- **Forged or stale `qid`.** Gives 409. The order of checks means a forged `qid` never reaches the rate counter.
- **A saved copy viewed later.** It is synced to the session without notes, so every letter gives "".
- **Iterating letters in practice.** This returns only what `data-correct` already shows.

**Rate limit.** The limit lives in the existing database counter (`check_and_increment_rate_limit`). It is keyed by user id, or for guests by a keyed hash of the IP (invariant 13), never a raw IP. A new session or a cleared cookie does not reset it. Rotating IPs would, but only in practice, where the page already holds the key, so it does not matter.

**Drift.** Two comparisons, both against the rebuilt pre-Phase-4 tree, gave 0 differences:

- **Every slot.** 5,810 generated questions over all 1,683 GCSE maths slots (practice, MCQ and lesson slots; 6 runs per MCQ slot, 2 otherwise), hashed without `answer_record` and `option_notes`.
- **The tagged generators.** 6,750 calls of the 64 tagged generator functions over 150 seeds, hashed with the random state after each call.

Both include the review's tag changes. Those changes only alter which candidates carry a tag, never a value or a random draw.

**Browser (Playwright, Chromium, local server on port 5088, 114 checks, all passing).** Guest at 1280 px light (bidmas, fdp) and dark (decimals), guest at 360 px light (bidmas) and dark (fdp, by keyboard: focus an option, Enter). Logged in at 1280 px light (number and ratio at difficult, by keyboard) and 360 px dark (pythagoras, mensuration). Each case checked:

- the usual line plus exactly one note, with the correct option highlighted and the pick marked
- `#mcq-feedback` is `role="status"` and `aria-live="polite"`, and the note arrives as its own addition (announced once)
- focus is unchanged by the note
- no digit or dash in the note
- no horizontal scroll
- Show answer unlocked, and Try again clears the note

Also checked: a right pick makes no note request; a Quick Test MCQ has no `data-note-qid` and makes no request; logged-in picks persist (200); guests make no `mcq-answer` call. No console error, no HTTP error, no CSP violation. Screenshots: `/mnt/user-data/outputs/hints_p4_review/` (`guest_desktop_light_bidmas`, `guest_desktop_light_fdp`, `guest_desktop_dark_decimals`, `guest_mobile360_light_bidmas`, `guest_mobile360_dark_fdp`, `user_desktop_light_number`, `user_desktop_light_ratio_proportion`, `user_mobile360_dark_pythagoras`, `user_mobile360_dark_mensuration`, `quicktest_pick`, all `.png`).

**Mutation (by hand on the working tree, each file restored and checksummed).** 15 of 15 caught by `test_gcse_maths_hints_mcq_smoke.py`:

| Mutation | Fails in |
|---|---|
| A wrong note on an option (circle "pi missing" option tagged "not squared") | `verified`, `catalogue` |
| `option_notes` dropped from `SERVER_ONLY_KEYS` | `leak`, `graded` |
| The notes printed in a page data attribute | `leak`, `client` |
| The endpoint allowed in Quick Test | `endpoint` |
| The endpoint allowed in a lesson quiz | `endpoint` |
| The `qid` check off | `endpoint` |
| The verifier returning true for any known tag | `verified`, `review` |
| HCF common factor named as cofactor again | `review`, `verified`, `catalogue` |
| The metres option tagged again | `review`, `verified` |
| The key-rounding guard off | `review`, `verified` |
| An odd total tagged as an equal split | `review`, `verified` |
| The verifier's unit comparison off | `review` |
| `textContent +=` back | `client` |
| The guest `mcq-answer` call back | `client` |
| A value written into a note | `catalogue`, `bank` |

**Coverage after the review (40 seeds).** 3,647 of 5,400 procedural distractors in waves A and B are verified (67.5%; the build reported 69%). The floor of 50% holds. The loss is the silenced options of findings 1 to 5.

| Topic | Verified distractors | Share |
|---|---|---|
| mensuration | 234 of 240 | 98% |
| number | 1,815 of 2,160 | 84% |
| pythagoras | 160 of 240 | 67% |
| ratio and proportion | 720 of 1,080 | 67% |
| fdp | 264 of 480 | 55% |
| decimals | 240 of 480 | 50% |
| bidmas | 109 of 240 | 45% |
| compound measures | 80 of 240 | 33% |
| trigonometry | 25 of 240 | 10% |

**Bytes and pins.**

| Item | Value |
|---|---|
| `site.js` | 210,258 B, +717 on 209,541. The Phase 4 budget is +900 B. The cap of 210,446 in the ladder smoke is unchanged and dated 2026-10-26. |
| `practice.css` | 31,947 B, +0 |
| Cache pins | `site.js?v=36` and `sw.js` `pb-v107`, bumped once in this change set |

**Tests and runs.**

| Run | Result |
|---|---|
| `test_gcse_maths_hints_mcq_smoke.py` | Passes in about 2 s. It gains a `review` check (unit, rounding and HCF cases for the helper and the verifier, plus the six changed generators over 60 fixed seeds each) and two `client` needles (the note as a text node; guests skip `mcq-answer`). |
| `test_gcse_maths_hints_smoke.py` | Passes in 10.6 s. |
| `test_gcse_maths_hints_ladder_smoke.py` | Passes in 2.7 s. |
| Answer check smoke | Passes. |
| Zorp voice smoke | Passes. |
| MCQ letter consistency | Passes. |
| GCSE verification smoke, alone | 30.6 s |
| `ruff check .` | Clean. |
| Full suite | 108 of 108 |

**Files changed in review.**

- `generators/gcse/maths_num_stats_prob_rat.py`: tags only.
- `generators/shared/mcq_notes.py`: one line deleted, one reworded, two new.
- `generators/shared/option_notes.py`: `rounds_from_key`, `ROUNDING_NOTES`.
- `scripts/gcse_verify/mcq_notes.py`: units, key rounding, places, exact half, HCF slips, one slip removed.
- `scripts/test_gcse_maths_hints_mcq_smoke.py`
- `static/js/site.js`
- `docs/ZORP_CHARM.md` (Appendix A)
- `docs/AI_HANDOFF.md`
- this file.

**For David.** Both items below were resolved on 2026-10-26 (`docs/GCSE_MATHS_VERIFICATION.md`, "Fillers and units"):

- The map-scale question (finding 1) now says "in km" and offers no equal length in another unit.
- `number_mcq`, `ratio_proportion_mcq` and the statistics multiple-choice fallback no longer pad with "0". Fillers now look like the key (same form, units and precision) and are never 0 or negative beside a positive key.

---

## 21. Phase 5 build notes (2026-10-26, not committed)

Waves C and D: probability, statistics, angles, bearings, sequences, algebra, simultaneous and quadratic equations, completing the square, graphs, vectors and transformations. Multi-part answers, algebraic answers and graphs are covered. Nothing is committed; the base is `1bd6362` plus the reviewed uncommitted work of Phases 1 to 4.

### What was built

- **`generators/shared/misconception_cd.py` (new, about 2,600 lines).** The wave C and D rules. Four kinds, each merged into the Phase 2 machinery at the tail of `misconception_topics.py` (one hook, no change to the matching order):
  - `RULES`: scalar rules over a recorded family (`prob_*`, `stats_*`, `ang_*`, `poly_*`, `brg_*`, `seq_*`, `lin_eq`, `gr_subst`, `vec_magnitude`, `cts_*`). Same contract as Phase 2: the rule fires only when `TRUTH[family](inputs, pi)` rebuilds the stored key.
  - `PAIR_RULES` with `PAIR_TRUTH` (a slip is a pair of numbers: vectors, midpoints, roots, `linear_system_2`).
  - `PART_RULES` with `PART_TRUTH` and `PART_TOKENS` (multi-part answers: a slip is a whole set of boxes, and the message is given for the box the pupil is checking, via `part=` from the check route; `brg_legs`, `brg_en`, `brg_two_ships`, `trans_apply`, `qsim_solve`).
  - `EXPR_RULES` with `EXPR_TRUTH(inputs) -> (subject, text)` (algebraic answers: `expand2`, `rearrange`, `seq_nth_find`). The comparison uses the checker's own `answer_checkers._algebraic_answers_equivalent`, so all the parser caps (length, nesting, exponent size, node count) stay in force, and the rule fires only when the typed text is equivalent to exactly one slip and is not accepted.
- **`DERIVE`.** For tasks whose hook names only the task (`alg`), `answer_record.build_record` calls `misconception_cd.DERIVE[task](plain_text(question))`, which reads the family and inputs from the displayed question (`solve_linear`, `seq_next`, `seq_nth_value`, `seq_which_term`, `seq_find_nth`, `solve_system`, `qsim_solve`, `cts_*`, `gr_subst`, `gr_midpoint`, `gr_roots`, `expand`, `rearrange`). A question the parser cannot read gets no record and so falls back to the generic rules. A record is stored only when it is the one record (drawing records `gr_drawn` and `gsim_drawn` are dropped, so a graph or graphical simultaneous question keeps the record whose family has rules), the question is not multiple choice, the answer type is allowed for the family (`RECORDED_FAMILIES` is now a map from family to answer types), and the JSON is at most 256 B.
- **Guards (unchanged in kind).** Rebuild check; coincidence guard (`_quiet_hit`: a typed value printed in the question stays silent unless the rule is in `ECHO_OK`); near-key guard; the checker's acceptance is applied first; a topic hit beats a generic hit on the same value; two different topic messages mean silence, with no fallback to generic. Never the corrected value or the factor to apply (D5).
- **`generators/shared/misconceptions.py`.** About 45 new messages. `gen.sign` no longer applies to bearings. Some Phase 2 messages were reworded to pass the voice lint after the lint was widened (`alg.wrong_inverse`, `alg.root_signs`).
- **MCQ notes (Phase 4 mechanism extended).** 56 new `BANK_WHY` rows and 28 new `BANK_NOTES` for fixed bank questions of waves C and D (see below). No generator was tagged: waves C and D have no procedural multiple-choice generators with a single clear slip (their multiple-choice items are fixed banks). Trigonometry notes stay as they were.
- **Two approved small fixes.** (a) The "Revise: <topic>" link label shows the display name, fixed server-side (`revise_topic_name` in `app.py`, no `site.js` change). (b) `_mf_proc_lcm`, `_mf_random_pair` and the sibling HCF and LCM generators always give two different numbers (a redraw loop; other questions stay byte-identical), with `registry.distinct` checks (`num_hcf`, `num_lcm`, `num_hcf_lcm`) in the verification smoke.

### Rules by topic (109 scalar and 53 pair, box and expression rules, 162 in all; 316 topic rules with Phase 2)

Messages are in `MESSAGES`; every rule below has a hand-worked example in `scripts/gcse_hints_cd.py` and is also run on real generated questions. Examples are the typed wrong answer and the message.

| Topic | Rules (message ids) | Example |
|---|---|---|
| Probability (35) | boundary, one is not prime, odds for probability, other colour, not complemented, expected count (inverted, not scaled), other outcome, or multiplied, one outcome only, tree: put back missed, removed missed, first draw only, added, one order, complement missed, at least one (all fail, one attempt, all succeed), conditional joint, Venn (overlap, total, complement, neither), union (counted twice, multiplied, removed twice, wrong total), independent added | Two draws with replacement, chance of two reds from 3 red in 5. Typed 6/5 (added) gets "It looks like these were added. When both events must happen, multiply." (reworded in review, section 22) |
| Statistics (23) | median unsorted, median is mean, range is largest, range first and last, mean total, mean divisor, mean is median, mode count, class midpoint (width, not halved), frequency ignored, frequency total, rows divisor, histogram ends and total, pie (percentage, one item, other sector), IQR (range, upper quartile), frequency density (multiplied, inverted) | Mean of 2, 4, 9 typed 15: "That is the total. A mean divides the total by how many values there are." |
| Angles (17) | rule sum not subtracted, wrong total, angle missed, alternate supplemented, co-interior equalled, exterior for interior, polygon formula (n times, exterior total, one interior), exterior half, interior as exterior, angle found for sides, isosceles (one base, bases added), equilateral total | Alternate angles, one is 65. Typed 115: "Check the angle pair. Alternate and corresponding angles are equal, rather than adding to 180°." |
| Bearings (29) | back bearing (same direction, anticlockwise, north line), compass (angle only, quadrant), angle between (added, reflex), from east, legs (swapped, radians, path, components added, acute, from east), per box: swapped, radians, path, components added, acute, from east, reversed, anticlockwise, ships added, reflex, sides added, Pythagoras misused, reversed, anticlockwise | Ship 20 km on 060. East box typed 10 (the north value): "Check which ratio goes with which direction. East uses the sine of the bearing and north uses the cosine." (corrected in review: the build notes quoted a message that does not exist) |
| Sequences (12) | step as term, geometric added, quadratic gaps, nth term (constant forgotten, sign, position off), which term (inverse, divide first), find nth term (first term as constant, step as constant, sign, add not multiply) | nth term of 3, 7, 11, 15, 19, typed 4n+3: "It looks like the first term was used as the constant. Compare the rule with the first term to find it." |
| Algebra (13) | linear (sign moved, wrong inverse, one term divided, bracket partial), expand cross term missed, rearrange (sign moved, one term divided, wrong inverse, root missed), graph substitution (negative power, power multiplied), completing the square (half not squared, whole squared, not halved) | Expand (x + 2)(x + 3), typed x^2+6: "Check every pair of terms. Each term in the first bracket multiplies each term in the second." Make y the subject of A = 3y + 1, typed y=(a+1)/3: "Check the sign of the term that moved." |
| Simultaneous and quadratic simultaneous (5) | back-substitution sign, back-substitution not divided, root signs, pairs swapped, y doubled | y = x^2 and y = -5x - 6 meet at (-3, 9) and (-2, 4). First x box typed 3: "Check the signs of the roots. A root has the opposite sign to the number in its bracket." (x boxes only since the review) |
| Vectors and graphs (17) | subtraction reversed, added for subtracted, displacement reversed, subtracted for added, scalar added, translation opposite and swapped, midpoint (sum, difference), section reversed, equation (sign, not divided), magnitude (not rooted, added), midpoint sum and difference on graphs, root signs on graphs | a - b with a = (4, -2), b = (1, 3), typed (5, 1): "It looks like the vectors were added. The question asks for a subtraction." |
| Transformations (10 boxes) | coordinates swapped, wrong axis, mirror line ignored, rotation opposite, centre ignored, enlargement added, enlargement inverted, negative scale factor ignored, translation opposite, vector swapped | Reflect (3, 4) in the x-axis, x box typed -4: "It looks like x and y were swapped. The x value is written first." (corrected in review: 4 is printed in the question, so it is silent) |

The full list of 162 ids with a hand-worked example each is in `scripts/gcse_hints_cd.py`, tables `TX`, `PAIR_TX`, `PART_TX` and `EXPR_TX`.

### Multi-part answers

A multi-part question is checked box by box. For each checked box `app.py` passes `part=` (`_checked_part_index`) to `diagnose`, which asks `PART_RULES` for a message for that box only: the typed value is compared with the same box of each slip vector, and a hit counts only when it is the single message for that box. The response still carries at most one message, always for the box being checked. A box whose typed value matches slips with two different messages stays silent. Aggregating across boxes (one message for a whole wrong set) was not built.

### Coverage (measured by `scripts/test_gcse_maths_hints_smoke.py`, 2 seeds, 1,072 practice slots)

| | Before Phase 5 | After |
|---|---|---|
| Slots with a topic rule | 192 of 1,072 (17.9%) | **442 of 1,072 (41.2%)** |
| Slots with a rule of any kind (topic or generic) | 780 of 1,072 (72.8%) | **834 of 1,072 (77.8%)** |
| Slots with a generic rule | 786 | 786 |

**Correction (review, section 22): the Phase 5 target is not met.** Section 7, metric 1, defines slot coverage as family (topic) rules, with generic rules reported separately, and sets the Phase 5 target at 60%. Topic coverage is 41.2% (41.1% after the review narrowed some rules); the 77.8% figure counts the key-only generic rules as well and is reported separately. The build note said "rules of any kind", which is not the plan's metric. The smoke pins floors of 400 topic slots and 815 combined slots. 457 slots carry an answer record (456 questions in the session-size sample).

### Session size (signed cookie, practice question, n = 1,072)

p50 684 B (668 before Phase 5), p90 1,796 B (1,764), **max 2,714 B** (unchanged) of about 4,093. A record adds a median of 41 B (max 91 B), 128 B at most per record, on 456 questions. `answer_record` is still server-only; nothing new is stored.

### MCQ notes added (bank rows, Phase 4 mechanism)

56 rows over fixed bank questions, each verified by the independent verifier (`scripts/gcse_verify/mcq_notes.py`, `verify_bank_row`: the question, key and distractor exist; a slip given as an expression is recomputed with exact arithmetic; the verifier now also reads degree and square-unit options for the expression check). Rows are reviewed pins in `BANK_PINS`. Every row was reached on a generated question (checked over all slots, 25 seeds each).

- Transformations: enlargement added to coordinates, mirror line ignored, wrong axis, coordinates swapped, rotation the other way, translation the other way, area scaled by the factor.
- Vectors: subtracted as added, order reversed, magnitude (parts added, total not rooted), length of a displacement.
- Bearings: back bearing not changed, bearing past a full turn.
- Angles: alternate angles taken as supplementary, co-interior taken as equal, isosceles base angles not halved, cyclic opposite angles taken as equal, centre angle halved or copied, interior for exterior.
- Sequences: constant forgotten, wrong position, first term as the constant, second difference used as the coefficient, starting from zero, going back one step only.
- Algebra: the same step repeated (add or multiply again), step missed, cross terms missed, like terms multiplied or powers changed, negative root missed, square halved, division by x, difference of two squares with equal signs, products with added numbers or wrong powers, rearranging (one term divided, not finished), root signs flipped, inequality not reversed, discriminant sign, simultaneous (other letter, constants or letters combined the wrong way round).

Messages follow the same copy rules as Phase 4 (no digit, at most 120 characters, no corrected value).

### Copy and lint changes

`models/zorp_voice.py` `HINT_LONG_WORD_ALLOW` gained `coordinates`, `enlargement` and `corresponding`. Appendix A of `docs/ZORP_CHARM.md` was regenerated (`scripts/test_zorp_voice_smoke.py --write`). Several Phase 2 messages and all new ones were reworded to stay at grade 8 or below; the words "inequality", "discriminant" and "quadrilateral" are avoided in notes rather than allowed.

### Tests

- `scripts/test_gcse_maths_hints_smoke.py` is extended (still one smoke file). Phase 5 data and checks live in the helper `scripts/gcse_hints_cd.py`, which does not match `scripts/test_*_smoke.py`, so the smoke-file count stays 108. Counts: 263 scalar rules and 53 pair, box and expression rules all fire on real questions; 130 generic and 335 topic hand-worked cases; mutation 17 of 17 generic, 403 of 403 topic and 73 of 73 pair, box and expression perturbations caught; negative control 3,358 far answers and 1,121 exact keys, none diagnosed; `check_routes` runs the real check route end to end for a box, a vector and an expression (with the ladder, no `answer_record` leak and a client-supplied record ignored); no_drift (1,072 slots with and without the wrapper) and the import rule cover the new module.
- **Budget.** The hints smoke runs in 14.5 to 17 s on this machine (noisy). Its budget went from 15 s to 17 s and its hard limit from 24 s to 26 s (the review brought it back to 15 s and 24 s, section 22). To keep it there, the rearrange rules avoid `simplify`, `expr_hits` checks the cheap case first, expression questions beyond four per family get one diagnosis (`EXPR_PER_FAMILY`), and extra seeds go only to slots with unfired rules.
- `scripts/test_gcse_maths_hints_mcq_smoke.py`: bank rows, pins (`BANK_PINS`) and a Phase 5 floor (at least 80 rows).
- `scripts/test_gcse_maths_hints_ladder_smoke.py`: a multiple-choice question in the lesson-quiz results now expects the note of the option picked (it used to expect none, because no geometry bank item had a note).
- GCSE verification smoke: 30 to 32 s alone, all checks pass (including the new `distinct` checks).

### Deferred

- No rules for functions, surds, algebraic fractions, circle theorems, similarity, constructions and loci, or the `completed_square` and `algebraic_fraction` answer types.
- Graphical simultaneous equations and quadratic find-y or count variants have only the generic rules.
- One message across all boxes of a multi-part answer was not built; each box is diagnosed on its own.
- No procedural multiple-choice generator of waves C and D was tagged (none has a single clear slip behind a distractor); their notes are bank rows only.
- No new stored data and no teacher view (Phase 6 is still side-lined).

---

## 22. Phase 5 review notes (2026-10-26, independent review, not committed)

**Method.** Every Phase 5 rule was run on real questions: 12 seeds of every practice slot with a wave C or D record (3,124 records; 9,570 diagnoses before the review, 8,877 after). Each diagnosis was read beside its question as a maths teacher would, with targeted probes for the coincidences named in the brief (P = 0.5, repeated data, 90° angles, back bearings near 90°, 180° and 270°, symmetric roots, sequences with a = d, equivalent algebra). The hints smoke was also run with `--deep` (40 seeds) at three seed offsets (0, 7919 and 104729, by shifting `harness.slot_seed`), which found five more real faults. The checker's square-root handling was read line by line. A local server (port 5095) was walked with Playwright on multi-box transformation questions. Eighteen hand mutations were run and each file restored and checksummed.

**Findings and fixes.**

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | High (checker) | Right answers to "make x the subject" refused. `_algebraic_prepare_for_sympy` turned `√( )` into `sqrt( )` only when nothing was nested inside, so `√((y−3)/5)` never reached SymPy and was accepted only if its text happened to match the key. For the key `x=√((y-3)/(5))`, `x=((y-3)/5)^(1/2)`, `x=√(y/5-3/5)` and `x=sqrt(1/5*(y-3))` were refused; for `t=√(s/3)`, `t=√(s/(3))` was refused; for `v=√(2e/11)`, `v=√((2e)/11)` was refused. The page's √ button makes these the likeliest forms. | `√(` is read as `sqrt(` whatever is nested inside (all SymPy caps unchanged; nested-root bombs still cost about 1 ms). |
| 2 | High (checker) | A wrong answer marked right, and the key shown wrongly. The normaliser rewrote `√((y-3)/(5))` as `√(y-3/5)`, which is a different expression: `x=√(y-9/2)` was marked right for `x=√((y-9)/2)`, and the key was shown to the pupil as `x=√(y-3/5)`. The same happened when `√(y-3)/√(5)` was collapsed. | A sum or difference keeps its bracket inside a root (`_keep_sum_bracket`); the key now shows as `x=√((y-3)/5)`. |
| 3 | Medium (checker, found by `--deep`) | "Close. A decimal cannot show this exactly, so give it as a fraction." was given for any decimal within 0.01 of a recurring probability, so for small probabilities a wrong value was called close (0.071429, which is 1/14, for a key of 1/15). The diagnosis also skips that message, so the Venn "wrong total" slip was never named. | "Close" only for the key rounded or cut off at the places typed (0.33 or 0.333 for 1/3, 0.067 or 0.07 for 1/15), never looser than the old rule. |
| 4 | High | `alg.rearr_sign_moved` on formulas where no term moves: "Make I the subject of P = VI", typed `I = -P/V`, and "Make t the subject of D = 7t", typed `t = -D/7`, were told "Check the sign of the term that moved". It also flipped terms on the other side of the formula. | Only a term that starts on the subject's side can be "moved with the wrong sign" (`_rearr_moving`). 379 diagnoses in 12 seeds became 130, all of them a real moved term (`y = 4x + 6` typed `(y + 6)/4`; `5x + 3y = 20` typed `(5x + 20)/3`). |
| 5 | Medium (multi-part) | A per-box message could contradict a box already marked right. About the origin, turning the other way, reflecting in the other axis or ignoring a negative scale factor flips the sign of every box, so one box typed with its sign wrong was told "Check the turn direction" even when the other coordinate, already marked right, proved the turn was right. | In `trans_apply`, a box with only its sign wrong gets the generic sign line ("Check the sign. Look again at each step where a number could change from positive to negative."), never a whole-shape slip (`_NO_SIGN_ONLY_PARTS`). `trans.rotate_opposite` 120 to 24 and `trans.wrong_axis` 172 to 26 in 12 seeds; the remaining ones are values a sign slip cannot reach (reflect in y = 2, x box typed 0 for 4: the image in x = 2). Browser-checked (below). |
| 6 | Medium | `qsim.root_signs` spoke on y boxes, where the "slip" value is only the other pair's y (a pairing slip, not a sign slip); and for roots r and −r (`gr.roots_signs`, `qsim.root_signs`) flipping the signs only changes the order, so (2, −2) for roots −2 and 2 was "Check the signs of the roots" instead of the generic "Those two values look swapped round" (found by `--deep`). | x boxes only; symmetric roots get no sign rule. |
| 7 | Medium | Pair rules matched a pair that is the key with one value negated, which a single sign slip explains as well: the midpoint of (−3, 0) and (0, −1) typed (−1.5, 0.5) was "Add the matching values before halving, rather than subtracting", because the zeros make the subtraction agree with the key in x. | A pair that differs from the key only in sign is named only by a rule whose message is about signs or about the vector pointing the other way (`_one_sign_off`, `_SIGN_MESSAGES`). |
| 8 | Medium (found by `--deep`, `no_collision`) | A rule kept quiet because its value is printed in the question was dropped before the collision test, so the other rule spoke: a mean typed as 9, which is both the middle value (an echo the rules allow) and the total over n − 1 rounded, was told "That is the middle value". | A quiet rule with a different message makes the value ambiguous: silence (`_topic_hits`). |
| 9 | Medium (found by `--deep`) | Rounding to the pupil's own places made short decimals match whole numbers: in "Calculate (5² − 1) ÷ (2 − 3) + 1" (key −23) a typed 23 matched "brackets ignored" (22.5, "rounded" to 23), when a sign slip is the obvious reading. | Own-places rounding only for a value that needs more than two decimal places (1/3, 12.345), never for 22.5 or 3.75. Phase 2 tables and coverage unchanged. |
| 10 | Low | Coin questions named one half as a slip ("3 coins, at least 1 head", typed 1/2: "Check the boundary"); one half is the chance for one coin and is typed for many reasons. The boundary value that equals one outcome (all heads) also collided with the single-outcome rule on most seeds (9 of 25 unambiguous in `--deep`). | One half, and the one-outcome value, are never offered as coin boundary or exact-only slips. |
| 11 | Low | `alg.lin_one_term_divided` on (x + 3)/5 = 4: "When both sides are divided, every term is divided" describes a step that multiplies. | Whole-number coefficients only. |
| 12 | Low | The generic `alg.root_signs` ("A root has the opposite sign to the number in its bracket") ran on surd roots from the formula, where there is no bracket. | Whole-number or fraction roots only. |
| 13 | Low (copy) | `ang.wrong_total` listed 180° and 360° only, so a complementary-angles question (90°) or a four-sided shape (360°) got a line that does not name its total. | "Check which total fits. A right angle is 90°, a line or a triangle 180°, and a point or a four-sided shape 360°." |
| 14 | Low (copy) | `prob.added_for_and` said "When one event follows another, multiply" for independent events A and B, which do not follow each other. | "It looks like these were added. When both events must happen, multiply." |
| 15 | Low (copy) | `bank.cyclic_equal` said opposite angles of a cyclic four-sided shape "are not equal", which is false for a rectangle. | "Check the angle pair. Opposite angles in a cyclic four-sided shape add up to a half turn." (no digit, as the note lint requires; two pins in `BANK_PINS` re-reviewed and updated.) |
| 16 | Medium (doc) | Section 21 called the plan's 60% target met using the combined figure (77.8%). Metric 1 (section 7) is topic rules, with generic rules reported separately. Two examples quoted messages that do not exist or cases that are silent. | Corrected in section 21 (coverage below). |
| 17 | Test | The `--deep` run was not clean (33 `rule_reachable`, 6 `no_collision`); the done-criterion "deep run clean at three seed offsets" had not been met. Apart from the real faults above, the generic section did not know that a Phase 5 pair rule speaks before a generic one on the same value. | Real faults fixed; the generic section now skips values a Phase 5 pair rule decides. Clean at three offsets (below). |

**Probed and kept (no change).**

- *Probability.* With p = 0.5 the complement equals the key and is dropped by the checker's acceptance test; independent and tree "added" values cannot equal the product for probabilities in (0, 1) except p = q = 0 or 2; "odds for probability" also fits the "two colours so 1/2" belief and its message ("A fraction compares one part with the whole") fits that too.
- *Statistics.* Repeated values (5, 5, 5, 5, 5): the mean, median and mode are the key and are dropped; the total (25) and the n − 1 divisor (6.25) are named. "That is the middle value" for a mean typed as the median is a true statement even when the median is also the mode.
- *Angles.* At 90° the alternate, corresponding and co-interior slips equal the key and are dropped; isosceles with a base angle of 60° gives one value for two messages and is silent.
- *Bearings.* Back bearings at 89, 90, 91, 179, 180, 181, 269, 270, 271, 0 and 359: every value claimed by two messages is silent (for example 090 from 270, where "same direction" and "north line" meet). The east and north swap message ("Check which ratio goes with which direction. East uses the sine of the bearing and north uses the cosine.") is clear for one or several legs; for "the shortest distance from a path due north" it still names the right ratio.
- *Sequences.* 4n + 3 for 3, 7, 11, 15, 19 is "the first term as the constant", the likeliest reading; for 4, 8, 12 the first term and the step are both 4, so 4n + 4 is silent; `4(n+1)-5` and `-1+4n` are accepted by the checker and never diagnosed.
- *Algebra.* Every equivalent form tried (`6+5x+x^2`, `x*x+5*x+6`, the root forms in finding 1) is accepted first and never reaches a rule. A required written form (expanded, factorised) keeps its own message.
- *Transformations.* A reflection in y = x is the key with x and y swapped, so the "coordinates swapped" slip is the original point, which is printed in the question and stays silent. "It looks like x and y were swapped" in one box is a true observation (the value is that point's other coordinate).
- *MCQ bank rows (56).* All read beside their question; apart from finding 15 each names the slip that gives the distractor exactly. `(4, 3)` for a reflection of (3, 4) in the x-axis carries "x and y were swapped", which is what a reflection in y = x does.
- *Revise label.* All 32 GCSE maths topics checked on a rendered practice page: each "Revise:" link shows the registry name and `problem['topic']` is the selected slug. A check for four topics whose name differs from the slug is now in the ladder smoke.
- *HCF and LCM.* The redraw loop changes no other question. Both mutations (pair always equal, loop removed) fail the verification smoke's `distinct` check ("given and asked numbers are equal").

**Multi-part answers in the browser** (Chromium, guest, 1280 px light and 360 px dark, transformations at foundational; screenshots in `/mnt/user-data/outputs/hints_p5_review/`). Each box has its own Check button and feedback line, so a pupil sees exactly one line per box checked, and it is always about that box's own value; the ladder's "Show a bigger hint" control is shared and the rung 1 line stays empty when a slip is named (one message, not two). Case A: an x box typed with the y value of the same image point shows "It looks like x and y were swapped. The x value is written first." Case B: that box corrected (marked right), then its y box typed with only the sign wrong shows the generic sign line, never "Check the turn direction". No horizontal scroll, no console error. Files: `trans_light_1280_A_swapped_box.png`, `trans_light_1280_B_sign_after_right_box.png`, `trans_dark_360_A_swapped_box.png`, `trans_dark_360_B_sign_after_right_box.png`. A third screenshot, `trans_light_1280_C_rotation_origin_sign_only.png`, is the case finding 5 fixes: "Rotate P(3, 1) 90° clockwise about the origin", P' x typed 1 (marked right), P' y typed 3 (the other turn's value): the line is now the generic sign line; before the review it was "Check the turn direction" under a box marked right. A bearings east-and-north question was checked through the real check route with a test client instead (east box typed with the north value: the ratio message; north box typed with the east value: the same; east box typed with its sign wrong: the sign line); the browser cannot choose a variant, and most bearing variants it served had no record. (The first browser runs of this review hit a stale server process; every result above is from a fresh server started after the last code change.)

**Coverage (honest, section 7 metric 1).** Topic rules: **441 of 1,072 practice slots (41.1%) against the Phase 5 target of 60%: not met** (41.2% before the review narrowed some rules; 41.3% with 40 seeds). Generic rules, reported separately: 786 slots (73%); either kind: 834 (77.8%). Reaching 60% needs about 204 more slots with a topic rule. Where they are (uncovered practice slots by topic, 2 seeds):

| Source | Uncovered slots | Note |
|---|---|---|
| Deferred topics with no rules | constructions and loci 48, similarity and congruence 45, circle theorems 45, functions 20, surds 19, multiples and factors 18, graphical simultaneous equations 15, algebraic fractions 15, algebraic proof 15 (240) | Circle theorems, similarity, functions, surds and multiples and factors (147) are the realistic ones; proofs and constructions are mostly not typed numbers. |
| Gaps inside covered topics | graphs 38, number 35, sequences 35, equations and inequalities 34, ratio and proportion 32, geometry angles 27, vectors 25, transformations 24, statistics 24 | Variants whose record is missing or whose answer type has no rule (`completed_square`, `algebraic_fraction`, inequalities, lists). |

So the gap closes only with the deferred topics plus the larger in-topic gaps; the waves C and D rules as built cannot reach 60% on their own.

**Leaks and storage.** Unchanged in kind and re-checked: `answer_record` stays in `SERVER_ONLY_KEYS` and under 256 B (largest 132 B in `--deep`); the hints smoke's `no_leak` and the MCQ smoke's leak and endpoint checks pass; the new bank notes reach a pupil only through the existing after-pick endpoint and graded results. The review added no field, table, log line or event. The check route's diff adds no logging.

**Mutation (by hand, each file restored and checksummed; 18 of 18 caught).** Each was run against the test named; the smoke's own per-rule mutation passes (17, 403 and 73 perturbations) are unchanged.

| Mutation | Caught by |
|---|---|
| North-line back bearing off by one | topic table |
| A box rule reads box 0 for every box | Phase 5 box table |
| Sign-only box guard off | review case (turn direction, scale factor) |
| Sign-only pair guard off | review case (midpoint) |
| A quiet rule no longer counts in the collision | review case (mean 9) |
| Every rest term may "move" (P = VI) | review case |
| One-term-divided for a fraction coefficient | review case |
| Coin one half named as a boundary slip | review case |
| Symmetric roots called a sign slip | review case (found by `--deep`) |
| y boxes back in the quadratic root-sign slip | review case |
| Surd roots get the bracket message | review case |
| Own-places rounding for short decimals | review case (22.5 and 23) |
| Checker: nested root not converted | answer check smoke |
| Checker: a sum inside a root loses its bracket | answer check smoke |
| Checker: "Close" for any decimal within 0.01 | answer check smoke |
| "Revise" label back to the slug | ladder smoke (4 topics) |
| HCF and LCM pair always equal | verification smoke, `distinct` |
| HCF and LCM redraw loop removed | verification smoke, `distinct` |

**Smoke budget.** 17 s was not needed. The smoke graded the same candidates many times over (59,600 checker calls); it now remembers the checker's verdict for the run (a pure function; a copy is returned), with no loss of coverage. It runs in about 15 s alone (14.8 s measured), so the budget is back to 15 s and the hard limit to 24 s.

**Runs.**

| Run | Result |
|---|---|
| `test_gcse_maths_hints_smoke.py` | Passes, 14.9 s inside the smoke (16.1 s with start-up). 441 of 1,072 slots with a topic rule, 834 with either kind; 130 generic and 335 topic hand-worked cases; mutation 17 of 17, 403 of 403 and 73 of 73 caught. |
| `test_gcse_maths_hints_smoke.py --deep` at seed offsets 0, 7919 and 104729 | All three pass (113 to 116 s each; 42,880 questions each; topic slots 443, 41.3%). Before the review the same run failed with 33 `rule_reachable` and 6 `no_collision` issues. |
| `test_gcse_maths_hints_mcq_smoke.py` | Passes, 2.3 s. |
| `test_gcse_maths_hints_ladder_smoke.py` | Passes, 3.0 s (now with the "Revise" label check). |
| GCSE verification smoke, alone | Passes, 31.9 s (32.6 s on the first run), under the 35 s limit. |
| `test_gcse_maths_correctness_smoke.py` | Passes, 12.6 s. |
| `test_answer_check_smoke.py` | Passes, 5.6 s (two new tests). |
| `test_zorp_voice_smoke.py` | Passes (Appendix A regenerated with `--write`). |
| `test_mcq_letter_consistency_smoke.py` | Passes. |
| `ruff check .` | Clean. |
| Full suite (`scripts/run_smoke_tests.py`) | 108 of 108 passed (`/tmp/claude-0/suite_h5_review.log`). |

**Files changed in review.**

- `generators/shared/answer_checkers.py`: `√(` read as `sqrt(`; `_keep_sum_bracket`; `_is_key_as_decimal`.
- `generators/shared/misconceptions.py`: two messages; rational roots only for the generic root-sign rule; `_one_sign_off`; `_NO_SIGN_ONLY_PARTS`; quiet rules in the collision test; own-places rounding limit.
- `generators/shared/misconception_cd.py`: `_rearr_moving`; whole-number coefficient for one-term-divided; coin values; symmetric roots; quadratic root signs on x boxes only.
- `generators/shared/mcq_notes.py`: `bank.cyclic_equal`.
- `scripts/gcse_hints_cd.py`: two box examples moved off the origin; 13 review cases; the pair section mirrors the sign-only guard.
- `scripts/test_gcse_maths_hints_smoke.py`: remembered checker; budget 15 s and 24 s; Phase 5 pair precedence in the generic section.
- `scripts/test_gcse_maths_hints_mcq_smoke.py`: two pins.
- `scripts/test_gcse_maths_hints_ladder_smoke.py`: the "Revise" label check.
- `scripts/test_answer_check_smoke.py`: `test_check_algebraic_root_brackets`, `test_recurring_close_is_the_key_rounded`.
- `docs/ZORP_CHARM.md` (Appendix A), `docs/AI_HANDOFF.md`, this file (sections 4, 10, 21 and 22).

**For David (not changed).**

- A rearranged square root typed with ± (`x=±√((y−3)/5)` for `y = 5x² + 3`) is marked wrong; many mark schemes accept or expect it. The generators key the positive root only. A decision for you.
- The sequence generators write "21th", "22th", "23th", "81th" ("Find the {n}th term", `generators/gcse/sequences.py` lines 237, 332 and 338). Pupil-facing; fixing it changes generated text, so it is left for a separate change.
- In algebraic answers the checker does not read `÷` or a decimal power (`^0.5`); both are rare in typed answers.
- When a box's feedback line appears, that box's row in a multi-box answer wraps (x and y no longer side by side). Pre-existing layout.
- A multi-box answer is still diagnosed one box at a time; a message that looks at all boxes (for example "x and y swapped" only when both boxes show it) would need `site.js` to send the other boxes' values, which this phase's budget does not include.


---

## 23. Phase 5b build notes (2026-10-27, not committed)

Part A is three small approved fixes (checker and ordinals); Part B raises topic-rule coverage from 41.1% to 60.5% of the 1,072 practice slots (plan section 7, metric 1: slots whose problem gets at least one family or topic rule; generic rules are reported separately). Nothing is committed. `scripts/gcse_hints_5b.py` (new) holds the hand-worked examples and is read by `scripts/gcse_hints_cd.py`; it is a helper, not a smoke, so the smoke-file count stays 108.

### Part A: three approved fixes

1. **Square-root keys accept a plus-or-minus answer.** For a changing-the-subject key `x=√(...)`, the checker now also accepts `x=±√(...)`, `x = +-sqrt(...)`, `x=+/-√(...)` and `x=±√(y/5-3/5)` (the same value written another way). The key display and every denial-of-service cap (`MAX_SYMPY_EXPR_LEN`, term and power caps) are unchanged. Still refused: a wrong expression under the ±, `∓`, and a ± on the wrong side (`±x=...`, `x=√(y/5)±`). Code: `_canonical_plus_minus` and `_plus_minus_split` in `generators/shared/answer_checkers.py`; tests in `scripts/test_answer_check_smoke.py`.
2. **Ordinals.** `generators/shared/utils.ordinal_suffix` and `ordinal` give 1st, 2nd, 3rd, 4th, 11th to 13th, 21st to 23rd, 101st, 111th, 112th. `generators/gcse/sequences.py`, `maths.py` and `maths_bank_procedural_mcq.py` use them. Only the wrong ordinals change in generated text (drift run: 29,616 generations, 2 differ, "33th" to "33rd" and "32th" to "32nd", nothing else). The independent verifier `scripts/gcse_verify/ordinals.py` is written from the rule, not from the helper, and flags a wrong ending in any question, option, worked solution or hint; its check has a mutation check (the helper broken on purpose is caught). See `docs/GCSE_MATHS_VERIFICATION.md`.
3. **The algebra checker reads `÷` as division, and `^0.5` and `^(1/2)` as a square root.** All caps and the expanded, factorised and simplified form rules are kept. Tests include bombs (very long inputs, deep brackets, huge powers) that must stay refused quickly.

### Part B: what was built

New module `generators/shared/misconception_5b.py` (data and small slip functions; no generator, random numbers or database), installed into `misconception_cd.py` by one hook (`_b5.install(globals())`) plus `DERIVE.update(_b5.DERIVE)`. It adds **194 rules** (75 one-value, 112 per-box, 7 pair) in 64 new messages, and **13 parsers** that read a family from the displayed question. Same contract as Phases 2 to 5: the inputs must rebuild the stored key (truth guard); nothing fires on the key, on a value that rounds to the key at the stated accuracy, next to the key, or on a number printed in the question (unless the rule is in `ECHO_OK`); two different topic messages on one value give silence; `answer_record` is server-only, at most 256 B and stored nowhere. `record()` lines: none added (every slot already had a verify-mode record). Output and random numbers are unchanged (drift run above).

Rules that would only repeat a generic rule's message and value were left out: they cannot pass the mutation check, and they would stop the generic rule firing. A family that is asked only as a plain number has a one-value rule; one that is also asked as a one-box `number_fields` answer has the box rule and a one-value copy (`_s` suffix).

**Parsers (`DERIVE`).** `substitute`, `fn_eval`, `fn_machine`, `fn_inverse_eval`, `fn_solve`, `seq_special`, `seq_sum_arith`, `seq_rows`, `seq_mean`, `seq_geometric`, `seq_u_n`, `gr_parallel`, `gr_speed`. A substitution in a function, formula or nth term reuses the existing `gr_subst` family. A parser that does not recognise the wording returns nothing (no record, no hint); each has hand-worked wording and negative wording in `DERIVE_TX_5B` and `DERIVE_NONE_5B`.

### Rules by topic (194 new)

| Topic | Rules | Examples |
|---|---|---|
| circle theorems (`circ.`) | 54 | half or double the angle at the centre; semicircle, cyclic and tangent angles; alternate segment; secants and chords; reflex centre; chord and radius |
| similarity (`sim.`) | 41 | length scale factor squared or inverted; area and volume scale factors; map scales; area scale factor not rooted; series and chains |
| ratio and proportion (`ratio.`, `prop.`) | 16 | parts swapped; shared equally; additive instead of multiplicative |
| multiples and factors (`mf.`) | 10 | HCF for LCM and back; three-number HCF and LCM; product for LCM |
| number, decimals, fractions (`num.`, `dec.`, `fdp.`) | 16 | power-of-ten direction; digit not place value; decimal place off by one; bounds with a whole unit; recurring decimal block over ten; lining up decimals on the right |
| mensuration (`mens.`) | 11 | hemisphere counted as a whole sphere; one end of a prism; cube root missed; slant height for height; compound prism |
| loci, bearings, vectors, Pythagoras, trigonometry | 17 | chord midpoint, sector area, scale areas; meeting time; vector sign kept; parallel vectors compared; cut corner |
| functions, substitution, sequences, graphs (parsers) | 18 | composite order; f(f(x)) once; machine order and undoing; "5x" read as an addition or as digits side by side; square, triangle and odd numbers; sum and geometric term; parallel gradient; speed |
| angles and polygons (`ang.`, `poly.`) | 11 | isosceles apex, interior and exterior swapped, sum of angles |

Full table (rule, message shown to the pupil, hand-worked example; updated to the reviewed rules, see section 24):

| Rule | Message | Example |
|---|---|---|
| `circ.half_doubled` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 70, box 1 typed 280 |
| `circ.double_halved` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 128, box 1 typed 32 |
| `circ.half_twice_doubled` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 55/55, box 2 typed 220 |
| `circ.semicircle_straight` | That is the angle on a straight line. Use the circle theorem for the angle in a semicircle. | key 90, box 1 typed 180 |
| `circ.semi_third_180` | The angle in a semicircle is 90°, so the other two angles in that triangle add up to 90°. | key 30, box 1 typed 120 |
| `circ.alt_semicircle_180` | The angle in a semicircle is 90°, so the other two angles in that triangle add up to 90°. | key 40/50, box 2 typed 140 |
| `circ.opposite_equal` | Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal. | key 65, box 1 typed 115 |
| `circ.cyclic2_equal` | Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal. | key 75/95, box 1 typed 105 |
| `circ.cyclic_ext_equal` | Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal. | key 100/80, box 1 typed 80 |
| `circ.cyclic_parallel_equal` | Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal. | key 110/110, box 1 typed 70 |
| `circ.cyclic_parallel_cointerior` | Check the angle pair. Co-interior angles add up to 180°, rather than being equal. | key 110/110, box 2 typed 70 (added in review) |
| `circ.centre_cyclic_equal` | Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal. | key 60/120, box 2 typed 60 |
| `circ.cyclic_alg_equal` | Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal. | key 25/106/74, box 1 typed 9 |
| `circ.tangent_triangle_180` | A tangent meets the radius at 90°. That right angle is one of the angles of the triangle. | key 90/30, box 2 typed 120 |
| `circ.tangent_base_whole` | The two base angles are equal, so share what is left after the other angle between them. | key 70, box 1 typed 140 |
| `circ.tangents_not_reflex` | That is the angle that is less than 180°. The question asks for the reflex angle. | key 240, box 1 typed 120 |
| `circ.centre_both_whole` | The two base angles are equal, so share what is left after the other angle between them. | key 25/65, box 1 typed 50 |
| `circ.centre_both_arc` | Check which arc the point is on. The angles from the two arcs add up to 180°. | key 25/65, box 2 typed 115 |
| `circ.centre_minor_whole` | The two base angles are equal, so share what is left after the other angle between them. | key 25/115, box 1 typed 50 |
| `circ.centre_minor_arc` | Check which arc the point is on. The angles from the two arcs add up to 180°. | key 25/115, box 2 typed 65 |
| `circ.both_arcs_swapped` | Check which arc the point is on. The angles from the two arcs add up to 180°. | key 40/140, box 1 typed 140 |
| `circ.both_arcs_sum_swapped` | Check which arc the point is on. The angles from the two arcs add up to 180°. | key 55/125/180, box 2 typed 55 |
| `circ.reflex_half_arc` | Check which arc the point is on. The angles from the two arcs add up to 180°. | key 125, box 1 typed 55 |
| `circ.isos_same_seg_whole` | The two base angles are equal, so share what is left after the other angle between them. | key 69/42, box 1 typed 138 |
| `circ.alt_straight_supplement` | The angle in the alternate segment is the same as the angle between the tangent and chord. | key 65/115, box 1 typed 115 |
| `circ.same_seg2_swapped` | Check which chord each angle stands on. Angles on the same chord and the same side are equal. | key 46/21, box 1 typed 21 |
| `circ.alt_triangle_missed` | It looks like one of the given angles was left out. Take away every angle you are given. | key 50/96, box 2 typed 130 or 146 |
| `circ.two_tangents_missed` | Each tangent meets its radius at a right angle. Count both of them in the four-sided shape. | key 100, box 1 typed 190 or 280 |
| `circ.secants_added` | For two secants from a point outside, take the arcs away from each other. Adding is for chords. | key 50, box 1 typed 70 |
| `circ.chords_subtracted` | For chords that cross inside the circle, add the two arcs before halving. | key 70, box 1 typed 10 |
| `circ.three_whole` | The two base angles are equal, so share what is left after the other angle between them. | key 35/55/55/pick|1|c1, box 1 typed 70 |
| `circ.three_doubled` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 35/55/55/pick|1|c1, box 2 typed 220 |
| `circ.isos_apex_one_base` | It looks like only one base angle was used. Both base angles are equal and both count. | key 120, box 1 typed 150 |
| `circ.chord_half` | That is half the chord. The perpendicular from the centre cuts the chord in two. | key 19.6, box 1 typed 9.8 |
| `circ.tangent_length_added` | To find a shorter side, subtract the squares. Adding finds the hypotenuse. | key 14.14, box 1 typed 15.81 |
| `circ.radius_wrong_ratio` | Check which ratio fits. Label the sides from the angle first. | key 11.26, box 1 typed 6.5 |
| `sim.length_squared` | Lengths and perimeters are multiplied by the scale factor itself. Only areas use its square. | key 36, box 1 typed 72 |
| `sim.length_divided` | Check which way the scale factor goes. The bigger shape has the longer sides. | key 36, box 1 typed 9 |
| `sim.area_k_power` | Check the scale factor. Areas and volumes need the right power of it. | key 240, box 1 typed 60 or 960 |
| `sim.area_down_power` | Check the scale factor. Areas and volumes need the right power of it. | key 20, box 1 typed 60 |
| `sim.vol_k_power` | Check the scale factor. Areas and volumes need the right power of it. | key 540, box 1 typed 60 or 180 |
| `sim.area_ratio_power` | Check the scale factor. Areas and volumes need the right power of it. | key 45, box 1 typed 75 or 27 |
| `sim.vol_lengths_power` | Check the scale factor. Areas and volumes need the right power of it. | key 67.5, box 1 typed 30 or 45 |
| `sim.dim_not_rooted` | The volumes are in the ratio of the cubes of the lengths. Take the cube root first. | key 3, box 1 typed 6.75 |
| `sim.sf_inverted` | Check the scale factor. It is the new length divided by the old length. | key 3/2, box 1 typed 2/3 |
| `sim.tri_angles_360` | Check which total fits. A right angle is 90°, a line or a triangle 180°, and a point or a four-sided shape 360°. | key 70/50/60/70, box 1 typed 250 |
| `sim.tri_angles_sum` | That is the total of the angles given. Take it away from the full total to find the missing one. | key 70/50/60/70, box 4 typed 110 |
| `sim.quad_angles_sum` | That is the total of the angles given. Take it away from the full total to find the missing one. | key 90/85/110/75/90, box 1 typed 270 |
| `sim.overlap_inverted` | Check the scale factor. It is the new length divided by the old length. | key 2/3/3/2, box 3 typed 2/3 |
| `sim.parallel_part` | Compare the small triangle with the whole triangle, so use the whole side, not a part of it. | key 15, box 1 typed 10 |
| `sim.bpt_part` | Compare the small triangle with the whole triangle, so use the whole side, not a part of it. | key 6/10, box 1 typed 9.6 |
| `sim.alg_prop_inverted` | Check which ratio part goes with which quantity. | key 8, box 1 typed 1.75 |
| `sim.chain_one_step` | There are two scale factors. Use both, one after the other. | key 10, box 1 typed 6 |
| `sim.frustum_whole` | That is the volume of the whole cone. The small cone has to be taken away. | key 312, box 1 typed 324 |
| `sim.quad_prop_inverted` | Check the scale factor. It is the new length divided by the old length. | key 6/3/2, box 2 typed 2/3 |
| `sim.shadow_inverted` | Check the type of proportion. Here, both quantities increase together. | key 8, box 1 typed 0.5 |
| `sim.shadow_additive` | Check the method. Proportion works by multiplying, not by adding the same amount. | key 8, box 1 typed 17 |
| `sim.sides_additive` | Check the method. Proportion works by multiplying, not by adding the same amount. | key 21, box 1 typed 18 |
| `sim.sides_inverted` | Check which way the scale factor goes. The bigger shape has the longer sides. | key 18, box 1 typed 8 |
| `sim.bisector_swapped` | Check which ratio part goes with which quantity. | key 6/4, box 1 typed 4 |
| `sim.cone_power` | Check the scale factor. Areas and volumes need the right power of it. | key 80/72, box 1 typed 40 or 20 |
| `sim.model_not_converted` | That is still in the original units. The question asks for a different unit. | key 4000/12, box 1 typed 4000000000 |
| `sim.model_power` | Check the scale factor. Areas and volumes need the right power of it. | key 4000/12, box 1 typed 20 |
| `sim.vol_sa_not_rooted` | That is the ratio of the areas. The scale factor of the lengths is its square root. | key 1.5/135, box 1 typed 2.25 |
| `sim.vol_sa_power` | Check the scale factor. Areas and volumes need the right power of it. | key 1.5/135, box 2 typed 90 |
| `sim.map_not_converted` | That is still in the original units. The question asks for a different unit. | key 2, box 1 typed 200000 |
| `sim.map_divided` | Check the scale. A real distance is bigger than its distance on the map. | key 2, box 1 typed 0.00008 |
| `sim.map_area_linear` | Check the scale factor. Areas and volumes need the right power of it. | key 0.5, box 1 typed 2 |
| `ratio.ratio_share_equal` | That shares the amount out equally. In a ratio, the shares are different sizes. | key 27/18/36, box 2 typed 27 |
| `ratio.ratio_share_swapped` | Check which ratio part goes with which quantity. | key 27/18/36, box 1 typed 36 |
| `ratio.ratio_garden_equal` | That shares the amount out equally. In a ratio, the shares are different sizes. | key 135/180/45, box 1 typed 180 |
| `ratio.ratio_garden_swapped` | Check which ratio part goes with which quantity. | key 135/180/45, box 2 typed 225 |
| `ratio.ratio_share_diff_equal` | That shares the amount out equally. In a ratio, the shares are different sizes. | key 200/120/80, box 2 typed 160 |
| `ratio.ratio_share_diff_swapped` | Check which ratio part goes with which quantity. | key 200/120/80, box 3 typed 40 |
| `ratio.ratio_prize_equal` | That shares the amount out equally. In a ratio, the shares are different sizes. | key 100/300/200, box 1 typed 200 |
| `ratio.ratio_prize_swapped` | Check which ratio part goes with which quantity. | key 100/300/200, box 2 typed 100 |
| `ratio.ratio_holiday_equal` | That shares the amount out equally. In a ratio, the shares are different sizes. | key 300/200/120, box 1 typed 200 |
| `ratio.ratio_holiday_swapped` | Check which ratio part goes with which quantity. | key 300/200/120, box 2 typed 100 |
| `ratio.ratio_concert_equal` | That shares the amount out equally. In a ratio, the shares are different sizes. | key 264/176/4224, box 1 typed 220 |
| `ratio.ratio_concert_swapped` | Check which ratio part goes with which quantity. | key 264/176/4224, box 1 typed 176 |
| `ratio.merge_swapped` | Check which ratio part goes with which quantity. | key 24/48/12:7, box 1 typed 48 |
| `ratio.hike_not_converted` | That is still in the original units. The question asks for a different unit. | key 4000/1900/5.9, box 1 typed 400000 |
| `ratio.hike_divided` | Check the scale. A real distance is bigger than its distance on the map. | key 4000/1900/5.9, box 1 typed 0.00016 |
| `prop.plumbers_direct` | Check the type of proportion. Here, when one quantity goes up, the other goes down. | key 60/5/10, box 2 typed 28.8 |
| `fdp.dec_pct_swapped` | That looks like a percentage. The question asks for a decimal, so change it into one. | key 0.4/40, box 1 typed 40 |
| `fdp.pct_decimal` | That looks like a decimal. The question asks for a percentage, so change it into one. | key 0.4/40, box 2 typed 0.4 |
| `fdp.dec_inverted` | Check the fraction. It looks like the top and bottom have been swapped. | key 0.4/40, box 1 typed 2.5 |
| `ang.kite_one_equal` | A kite has one pair of equal angles. Count both of them before taking away from the total. | key 170/56, box 1 typed 226 |
| `ang.isos_parallel_one_base` | It looks like only one base angle was used. Both base angles are equal and both count. | key 74/53, box 1 typed 127 |
| `ang.isos_parallel_supplement` | Check the angle pair. Alternate and corresponding angles are equal, rather than adding to 180°. | key 74/53, box 2 typed 127 |
| `poly.int_ext_swapped_interior` | That is the exterior angle. The question asks for the interior angle. | key 150/30, box 1 typed 30 |
| `poly.int_ext_swapped_exterior` | That is the interior angle. The question asks for the exterior angle. | key 150/30, box 2 typed 150 |
| `ang.alg_wrong_total` | Check which total fits. A right angle is 90°, a line or a triangle 180°, and a point or a four-sided shape 360°. | key 21/94/86, box 1 typed 6 or 51 |
| `poly.alg_wrong_sum` | Check the formula. The sum of the interior angles uses two fewer than the number of sides. | key 70/90/100/120/130/100, box 1 typed 160 or 115 |
| `circ.semicircle_first_180` | The angle in a semicircle is 90°, so the other two angles in that triangle add up to 90°. | key 45/90, box 1 typed 135 |
| `circ.semicircle_straight_box` | That is the angle on a straight line. Use the circle theorem for the angle in a semicircle. | key 45/90, box 2 typed 180 |
| `sim.fields_additive` | Check the method. Proportion works by multiplying, not by adding the same amount. | key 18/50, box 1 typed 15 |
| `sim.fields_inverted` | Check which way the scale factor goes. The bigger shape has the longer sides. | key 18/50, box 1 typed 4.5 |
| `sim.fields_angle_scaled` | Check the angle. In similar shapes, the lengths scale up but the angles stay the same. | key 18/50, box 2 typed 100 |
| `circ.cyclic3_equal` | Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal. | key 134/145/92, box 1 typed 46 |
| `circ.cyclic3_centre` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 134/145/92, box 3 typed 46 |
| `ang.turn_anticlockwise` | Check the direction. Bearings are measured clockwise from north. | key 125/89, box 1 typed 303 |
| `circ.alt_segment_not_doubled` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 43/86, box 2 typed 43 |
| `circ.alt_segment_supplement` | The angle in the alternate segment is the same as the angle between the tangent and chord. | key 43/86, box 1 typed 137 |
| `circ.arcs_swapped` | Check which arc the point is on. The angles from the two arcs add up to 180°. | key 65/115, box 1 typed 115 |
| `circ.tangent_chord_missed` | It looks like one of the given angles was left out. Take away every angle you are given. | key 60/88, box 2 typed 120 or 148 |
| `circ.tangent_chord_supplement` | The angle in the alternate segment is the same as the angle between the tangent and chord. | key 60/88, box 1 typed 120 |
| `circ.alg_halved` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 23/70/35, box 1 typed 2 |
| `num.error_full_unit` | Check the error. The true value can be half of the rounding unit either side. | key (16.55, 16.65), typed (16.5, 16.7) |
| `num.bounds_area_full_unit` | Check the error. The true value can be half of the rounding unit either side. | key (108.75, 131.75), typed (98, 144) |
| `num.bounds_product_full_unit` | Check the error. The true value can be half of the rounding unit either side. | key (834.25, 894.25), typed (805, 925) |
| `num.bounds_density_matched` | Check the pairing. For the smallest answer, divide the smallest top by the largest bottom. | key (4.3, 5.625), typed (5.375, 4.5) |
| `num.share_ratio_swapped` | Check which ratio part goes with which quantity. | key (42, 63), typed (63, 42) |
| `num.share_ratio_equal` | That shares the amount out equally. In a ratio, the shares are different sizes. | key (42, 63), typed (52.5, 52.5) |
| `vec.scale_sign_kept` | Reversing a vector changes the sign of both of its parts. | key (-6, 2), typed (6, -2) |
| `mf.multiple_added` | Check the calculation. This one needs the numbers multiplied. | key 24, typed 10 |
| `mf.hcf_lcm` | That is the lowest common multiple. The question asks for the highest common factor. | key 6, typed 144 |
| `mf.lcm_hcf` | That is the highest common factor. The question asks for the lowest common multiple. | key 36, typed 6 |
| `mf.lcm_product` | That is the two numbers multiplied. Their lowest common multiple is smaller when they share a factor. | key 36, typed 216 |
| `mf.count_hcf` | That is the highest common factor. The question asks how many factors they have in common. | key 6, typed 12 |
| `mf.hcf3_lcm` | That is the lowest common multiple. The question asks for the highest common factor. | key 6, typed 180 |
| `mf.hcf3_two_only` | It looks like only two of the three numbers were used. All three must be included. | key 1, typed 6 |
| `mf.lcm3_hcf` | That is the highest common factor. The question asks for the lowest common multiple. | key 60, typed 2 |
| `mf.lcm3_two_only` | It looks like only two of the three numbers were used. All three must be included. | key 60, typed 12 |
| `mf.other_lcm_only` | Check the rule. The two numbers multiply to give the HCF times the LCM. | key 36, typed 4 |
| `dec.directed_not_aligned` | Line up the decimal points first. Write zeros so each number has the same number of decimal places. | key 4.65, typed 4.11 |
| `dec.arith_not_aligned` | Line up the decimal points first. Write zeros so each number has the same number of decimal places. | key 15.99, typed 15.45 |
| `num.scale_pow10_direction` | Multiplying by a power of ten makes a number bigger, and dividing makes it smaller. Check which. | key 69766, typed 0.069766 |
| `num.place_value_digit_face` | That is the digit itself. The question asks for its value, which depends on its place. | key 400, typed 4 |
| `num.decimal_place_next` | Check the place names. After the decimal point they go tenths, hundredths, thousandths. | key 2, typed 7 |
| `num.standard_form_sign` | Check the sign of the power. A negative power is not the same as a positive one. | key 0.0073, typed 7300 |
| `num.recurring_terminating` | A recurring decimal does not stop. It cannot be written over a power of ten. | key 2/3, typed 3/5 |
| `mens.cyl_hemisphere_whole` | Check the hemisphere. It is half of a sphere, so use half of the sphere formula. | key 169.65, typed 226.19 |
| `mens.tri_prism_face_missed` | A prism has a rectangle for every side of its cross-section. One face has been left out. | key 132, typed 82 |
| `mens.tri_prism_end_once` | A prism has two ends. The end shape has to be counted twice. | key 132, typed 126 |
| `mens.sphere_radius_no_root` | Check the last step. To undo a cube, take the cube root. | key 3, typed 27 or 5.2 |
| `mens.hemi_cone_height` | Check the slant height. This area needs the slant height, not the perpendicular height. | key 103.67, typed 94.25 |
| `mens.submerged_not_divided` | That is the volume of the sphere. The water level rises by that volume divided by the area of the base. | key 3.56, typed 904.78 |
| `mens.cyl_mass_formula` | Check the formula. Mass is density multiplied by volume. | key 282.74, typed 70.69 or 141.37 |
| `mens.segment_sector_only` | That is the whole sector. The segment is what is left when the triangle is taken away. | key 3.26, typed 18.85 |
| `mens.segment_added` | The segment is the sector with the triangle taken away. It looks like the triangle was added. | key 3.26, typed 34.44 |
| `mens.prism_compound_rectangle` | That looks like the answer for a full rectangle. A triangle or trapezium covers only part of one. | key 80, typed 100 |
| `mens.prism_compound_area` | That is the area of the cross-section. Multiply it by the length of the prism. | key 80, typed 16 |
| `pyth.cut_corner_full` | The piece cut off is a triangle, not a rectangle. Check its area. | key 74, typed 68 |
| `trig.area_side_half` | Check the formula. The area of a triangle is half of one side times the other times the sine. | key 5, typed 2.5 |
| `brg.meeting_difference` | Check the relative speed. Whether speeds add or subtract depends on the directions. | key 2.5, typed 10 |
| `loci.chord_midpoint_added` | To find a shorter side, subtract the squares. Adding finds the hypotenuse. | key 12, typed 13.9 |
| `loci.chord_midpoint_whole` | Check the base. The height splits it in two, so the triangle uses half of it. | key 12, typed 8.3 |
| `loci.sector_whole` | That is the whole circle. The question asks for only part of it. | key 12.57, typed 50.27 |
| `loci.sector_arc` | That looks like the arc length formula. The question asks for an area. | key 12.57, typed 6.28 |
| `loci.scale_area_linear` | Check the scale factor. Areas and volumes need the right power of it. | key 500, typed 50 |
| `loci.scale_down_units` | That is still in the original units. The question asks for a different unit. | key 20, typed 0.2 or 0.0002 |
| `loci.scale_down_direction` | Check the scale. A real distance is bigger than its distance on the map. | key 20, typed 12500000000 |
| `vec.parallel_t_inverted` | Parallel vectors are multiples of each other. Compare top with top and bottom with bottom. | key 5, typed 20 |
| `vec.parallel_t_additive` | Check the method. Proportion works by multiplying, not by adding the same amount. | key 5, typed 8 |
| `vec.parallel_k_inverted` | Parallel vectors are multiples of each other. Compare top with top and bottom with bottom. | key 4, typed 0.25 |
| `vec.parallel_k_additive` | Check the method. Proportion works by multiplying, not by adding the same amount. | key 4, typed 6 |
| `brg.ship_ab_sides_added` | That looks like the side lengths added or subtracted directly. Pythagoras uses their squares. | key 8.72, typed 16 |
| `brg.ship_ab_pythagoras` | Pythagoras only works with a right angle. This triangle needs the cosine rule. | key 8.72, typed 11.66 |
| `sub.formula_letters_added` | Two letters side by side are multiplied. They are not added. | key 28, typed 17 |
| `sub.coefficient_implied` | A number next to a letter means multiply. It is not an addition, and the digits do not join up. | key -5, typed 8 |
| `sub.divide_multiplied` | Check the sign between the parts. A fraction bar with x underneath means divide by x. | key 3, typed 48 |
| `fn.comp_wrong_order` | In f(g(x)), work out g first. Then put that answer into f. | key 41, typed 37 |
| `fn.twice_applied_once` | Applying f twice means putting the first answer back into f. Do that step again. | key 68, typed 16 or 32 |
| `fn.machine_swapped` | The machine does its steps in the order shown. Check which step comes first. | key 10, typed 6 |
| `fn.machine_back_order` | To go backwards, undo the last step first. Use the opposite of each step. | key 3, typed 0.5 or 27 |
| `fn.inverse_wrong_way` | To go backwards, undo the last step first. Use the opposite of each step. | key 4, typed 8 or 0 |
| `seq.square_doubled` | Square numbers are n times n. Doubling n gives the even numbers instead. | key 81, typed 18 |
| `seq.triangle_not_halved` | Triangle numbers are half of n times the next number up. Check that last halving step. | key 78, typed 156 |
| `seq.odd_parity` | The nth odd number is double n, take away one. Doubling n alone gives the even numbers. | key 31, typed 32 or 33 |
| `gr.parallel_intercept` | The gradient is the number in front of x. The number on its own is the y-intercept. | key 2, typed 6 |
| `gr.parallel_perpendicular` | Parallel lines have the same gradient. That value is for a line at right angles. | key 2, typed -0.5 |
| `gr.speed_multiplied` | Speed is distance divided by time, not distance times time. | key 24, typed 96 |
| `seq.sum_extra_step` | Between the first and last term there is one step fewer than the number of terms. Check your count of steps. | key 680, typed 714 |
| `seq.sum_not_halved` | Check the sum formula. It starts with half of n, because the terms pair up. | key 680, typed 1360 |
| `seq.mean_extra_step` | Between the first and last term there is one step fewer than the number of terms. Check your count of steps. | key 67, typed 69 |
| `seq.geometric_power` | The first term has no ratio applied. The nth term uses the ratio one time fewer than n. | key 13122, typed 39366 |
| `circ.two_tangents_missed_s` | Each tangent meets its radius at a right angle. Count both of them in the four-sided shape. | key 100, typed 190 or 280 |
| `circ.tangent_length_added_s` | To find a shorter side, subtract the squares. Adding finds the hypotenuse. | key 14.14, typed 15.81 |
| `sim.area_k_power_s` | Check the scale factor. Areas and volumes need the right power of it. | key 240, typed 60 or 960 |
| `sim.map_not_converted_s` | That is still in the original units. The question asks for a different unit. | key 2, typed 200000 |
| `sim.map_divided_s` | Check the scale. A real distance is bigger than its distance on the map. | key 2, typed 0.00008 |
| `circ.centre_halved` | The angle at the centre is double the angle at the circumference. Check whether to double or halve. | key 80, typed 20 |
| `circ.chord_radius_whole` | Check the base. The height splits it in two, so the triangle uses half of it. | key 10, typed 17.09 |
| `circ.chord_radius_added` | That looks like the side lengths added or subtracted directly. Pythagoras uses their squares. | key 10, typed 14 |
| `circ.reflex_centre_only` | That is the angle that is less than 180°. The question asks for the reflex angle. | key 220, typed 140 |
| `sim.area_scale_power` | Check the scale factor. Areas and volumes need the right power of it. | key 48, typed 24 or 96 |
| `sim.area_scale_inverted` | Check which way the scale factor goes. The bigger shape has the longer sides. | key 48, typed 3 |
| `sim.k_area_not_rooted` | That is the ratio of the areas. The scale factor of the lengths is its square root. | key 3, typed 9 |

### Coverage (measured by `scripts/test_gcse_maths_hints_smoke.py`, 2 seeds, 1,072 practice slots)

| | Phase 5 (after review) | Phase 5b |
|---|---|---|
| Slots with a topic rule | 441 (41.1%) | **649 (60.5%)** |
| Slots with a generic rule | 785 (73.2%) | 785 (73.2%) |
| Slots with either | 834 (77.8%) | 834 (77.8%) |
| Rules that fire on generated questions | not recorded | 338 one-value (192 recorded families) and 172 pair, box and expression |
| Unit table, hand-worked one-value topic cases | 397 | 412 |

The combined figure did not move: the slots newly covered by a topic rule already had a generic hint. The ratchet floors are now `TOPIC_FLOOR_SLOTS = 640` and `COMBINED_FLOOR_SLOTS = 825`.

**The remaining 423 slots (39.5%).** 198 have an answer type with no diagnosis route at all (multiple choice 66, ordered proof steps 38, keyword 17, surds 11, algebraic fractions 12, number lists 8, standard form 7, estimates 7, completed square 6, inequalities and others), where a hint would need a new route in the check endpoint and the front end. 225 are diagnosable types (98 of them multi-box diagram answers) where no rule would add anything beyond the generic sign, rounding and reciprocal lines without risking a misleading hint (for example solving a quadratic by factorising: the only common slip is the sign of the roots, which `alg.root_signs` already names). They are left as a list for a later phase rather than padded with rules that restate a generic hint.

### Session size

Practice question cookie (n = 1,072): p50 698 B (668 before the record), p90 1,806 (1,764), max 2,714 (unchanged) of about 4,093. A record adds 40 B on average (max 91) on 653 questions. 0 records fail the truth guard.

### Tests and runtime

- `scripts/test_gcse_maths_hints_smoke.py`: every message is used by a rule; every rule has a hand-worked example and fires on real generated questions; collisions are silent; negative controls (3,358 far-away wrong answers and 1,121 exact keys: none diagnosed); mutation (530 of 530 one-value and 281 of 281 pair, box and expression perturbations caught); no leak; no drift; session ceiling; copy lint (D5: a message names the slip, never a value).
- Speed: the full diagnosis of a rule on a slot now runs once per slot (later seeds of the same slot check only that the candidate matches itself alone) and `topic_more_seeds` stops after 2.5 s. The smoke takes about 16 s here, where the unmodified Phase 5 tree takes about 18 s on this machine, against a 15 s budget (24 s hard limit) set on faster hardware.
- GCSE verification smoke, alone: 37 s on this machine (the Phase 5 tree took 31.8 s on faster hardware; the ordinal check and the wider checker cases add a little).
- `--deep --seed 5000` run in the background; see `docs/AI_HANDOFF.md`.


---

## 24. Part A and Phase 5b review notes (2026-10-27, independent review, not committed)

**Method.** Every Phase 5b candidate (one-value, box and pair) was typed through the real diagnosis on 8 seeds of every practice slot at two seed offsets (0 and 100; 3,019 and 2,866 fired diagnoses) and each fired message was read beside its question, with the same typed value also run with the record removed (what the generic rules alone would say), and flags for a value printed in the question and for a value that is another box's right answer. The 13 parsers were run on 12 seeds of every slot that names their task, and on 2,642 edited questions (each printed number changed in turn) to see whether a misread could still pass the truth guard. The checker changes were read line by line and probed with 56 hostile and edge inputs on the reviewed tree and on the Phase 5 tree (`/tmp/claude-0/pb_h5b_base`). Runtime was measured on this machine on both trees. Sixteen hand mutations were run on a scratch copy of the tree.

**Findings and fixes.**

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | High (checker) | The half-power reading took an optional bracket on each side of `0.5`, so an unbalanced answer that does not parse became a valid one: `(x^(0.5+1)` was rewritten to `(x^(1/2)+1)` and marked right for the key `√x+1`. | `^0.5`, `^.5`, `**0.5` and `^(0.5)` only (the bracket must close on the 0.5). `(x^(0.5+1)` and `x^(0.5+1)` are refused; `x^(0.5)+1` is still right. |
| 2 | High (rule) | `dec.arith_not_aligned` read the numbers and signs out of any expression: "Calculate (−4)³", typed −1, was told "Line up the decimal points first. Write zeros so each number has the same number of decimal places." (−4 + 3). | Only a plain sum or difference of numbers is read (`_arith_terms`); a bracket, power, product or letter means no slip. |
| 3 | Medium (rule) | `dec.directed_not_aligned` on "An item costs £11.36. How much change from £12.50?" (recorded as 12.5 − 11.36), typed 0.69: "Line up the decimal points first." The question prints 12.50, already lined up. | A text guard (`TEXT_GUARDS` in `misconception_5b.py`, read in `topic_candidates`): the short number must be printed short in the question. "Calculate 1.66 − 1.5", typed 0.61, is still named. |
| 4 | Medium (count) | Six rules only ever repeated the generic angle line on the same value (`ang.supplement`, "Check which angle fact applies. Some pairs of angles are equal, and others add up to 180°."): `circ.same_segment_supplement` (and `_s`), `circ.alt_parallel_supplement`, `ang.cross_swapped`, `ang.vertical_swapped`, `ang.turn_supplement`. In 8 seeds they fired 119 times and decided the message 0 times, yet they counted 8 slots towards the 60%. Section 23 said such rules were left out. | Deleted, with their families (`circ_same_segment`, `circ_alt_parallel`, `ang_cross`, `ang_vertical` are no longer recorded for hints; the verification solvers still read them). |
| 5 | Medium (coincidence) | A box typed with another box's right answer was named as a computed slip: "Share 81 sweets in the ratio 3:2:4", second share typed 27 (the first share, and also 81 shared equally): "That shares the amount out equally. In a ratio, the shares are different sizes."; triangle (3x+11), (2x+6), (3x+35), angle 2 typed 83 (angle 3): "Check which total fits..."; cyclic ABCD with DAB = 98 and ABC = 82 (so each slip is the other box's answer); similar cones with printed volume and area both 96π; prize, garden, holiday and class-merge ratio boxes. 45 such diagnoses in 8 seeds. | For the 5b box rules a value equal to another box's right answer is silent (`PART_OTHER_BOX_QUIET`), except the 15 rules whose slip *is* the other box's answer (arcs swapped, ratio parts swapped, interior and exterior swapped, percentage and decimal swapped, and so on: `PART_OTHER_BOX_OK`). Seven hand-worked examples sat on such a coincidence and were moved to other numbers. |
| 6 | Medium (coincidence, all phases) | The right answer cut or rounded short was called a slip: QR = 13.5, typed 13: "Check the method. Proportion works by multiplying, not by adding the same amount." (9 + 12 − 8). | `_near_key` treats the key cut or rounded half up to the pupil's own places as near the key (number answers typed as a plain number only, and only when the short form keeps a digit of the key, so 0 for 0.25 and fraction answers are unchanged). No earlier unit case changed. |
| 7 | Medium (D5) | `circ.semicircle_right` stated the answer: "The angle in a semicircle is a right angle. It is not a straight line." on questions whose key is 90. | "That is the angle on a straight line. Use the circle theorem for the angle in a semicircle." |
| 8 | Medium (maths) | `circ.cyclic_parallel_equal` ("ABCD is a cyclic quadrilateral with AD ∥ BC. Angle DAB = 75°. Find angle BCD and angle ABC.") said "Opposite angles in a cyclic quadrilateral add up to 180°" for angle ABC, which is next to DAB, not opposite it. | The opposite-angles line on the BCD box only; the ABC box has a new rule `circ.cyclic_parallel_cointerior` with the existing line "Check the angle pair. Co-interior angles add up to 180°, rather than being equal." |
| 9 | Low (copy) | `circ.two_tangents_missed` (typed 270 − p or 360 − p for angle APB): "It looks like one of the given angles was left out. Take away every angle you are given." The missing angles are the two right angles at the tangents, which are not given; 360 − p misses both. | New `circ.tangents_right_angles`: "Each tangent meets its radius at a right angle. Count both of them in the four-sided shape." |
| 10 | Low (copy) | `mens.segment_added` (sector plus triangle): "Check the cut-out. It should be taken away from the large rectangle, not added." There is no rectangle. | New `mens.segment_triangle_added`: "The segment is the sector with the triangle taken away. It looks like the triangle was added." |
| 11 | Low (copy) | `pyth.cut_corner_full` (the cut-off piece taken as a full rectangle): "That looks like the answer for a full rectangle. A triangle or trapezium covers only part of one." | New `mens.cut_triangle`: "The piece cut off is a triangle, not a rectangle. Check its area." |
| 12 | Low (copy) | `ang.kite_one_equal` (the equal kite angle missed): "Take away every angle you are given." The pupil did take away both given angles. | New `ang.kite_pair`: "A kite has one pair of equal angles. Count both of them before taking away from the total." |
| 13 | Low (copy) | `loci.scale_area_linear` ("A scale model uses scale 1 : 200. A floor appears as 5.6 cm² on the model. Find the actual floor area in cm²", typed 1120) and `sim.map_area_linear` said "Check the units. An area in square units changes by the conversion factor squared." There is no unit change in the first; the slip is the scale used once. | Both use `sim.wrong_power`: "Check the scale factor. Areas and volumes need the right power of it." |
| 14 | Low (copy) | `circ.centre_double` ended "Check which way you went." | "The angle at the centre is double the angle at the circumference. Check whether to double or halve." |
| 15 | Medium (checker) | A ± was taken for any key whose right-hand side is one square root, including an expression key with no subject: `±√x` was right for `√x` and `±x^0.5` for `x^(1/2)` (index form). No generated question has such a key today, so this was latent. | The ± is read only when the key has a subject (`x = √(...)`). |
| 16 | Medium (test reliability) | `topic_more_seeds` in the hints smoke stopped after 2.5 s, so the topic slot count and "every rule fires" depended on the machine: with no extra seeds the count is 635 and 8 rules never fire. | The rounds bound it; it takes about 1.1 s and the count is the same everywhere. |
| 17 | Low (runtime) | The ordinal check swept every slot of four topics for 30 seeds twice (about 2 s of the 1.5 to 2 s the verification smoke gained). | Slots that print an ordinal at all (43, found over 3 seeds) are swept for 30 seeds and mutated for 12; the property pass still reads every question. 0.7 s; the mutation is caught 11 times. |
| 18 | Test gap | Removing the check that keeps a ± out of the left-hand side survived the answer-check smoke (`±x=±√(...)` was never tried). | New cases `±x=±√(...)`, `+-x=+-√(...)`, `x±=±√(...)`. |
| 19 | Doc | Section 23 and `docs/AI_HANDOFF.md` reported the 60% target as met with 649 slots, 8 of them carried only by rules that could never decide the message. | Corrected (coverage below). |

**Part A decisions and checks.**

- *Where the ± is accepted.* Only for a key of the form `subject = √(...)`: in GCSE maths these are the 12 "make X the subject" rearrangements (`changing_the_subject` and `equations_inequalities`; no other subject or level produces an algebraic answer). Two give a context where only the positive root has meaning: "Make r the subject of A = πr²" (a radius) and "E = ½ × 11 × v², where v is speed in m/s". The ± is accepted there too, because mark schemes for a rearrangement accept `±√` and the checker cannot see the context; no question asks for "the positive value". The positive root alone stays right; the ± is never required. Recorded here for David to overrule.
- *Wrong side, nesting, other functions.* `∓`, a ± after the root, on the left, on both sides, twice, inside the root (`√(±...)`), inside another function, after another sign, or with a second `=` is refused (56 probes, all under 3 ms except the SymPy comparisons, under 200 ms). The length cap is checked before any work (`4 × MAX_SYMPY_EXPR_LEN`); every other cap is unchanged; the bombs in `test_check_algebraic_plus_minus_division_and_half_power` all stay refused within 2 s.
- *Form rules.* A ± is only read for a square-root key, which never carries the expanded, factorised or simplified form, and the form check strips the ± before reading the structure. `÷` and `×` now reach the form checks as `/` and `*`: `x×(x+3)` is "expand it" (it used to be a plain wrong answer) and `(x²−1)÷(x−1)` is "simplify it". `(x²)^0.5` is |x|, not x: refused for the key x, and refused for `x(x+3)` in factorised form, `((x²+3x)^0.5)²` in expanded form and `(x²+2x+1)^0.5` in simplified form.
- *Not in the build notes.* A typed left-hand side must now be the key's subject: `y=√((y−3)/5)` and `±x=√((y−3)/5)` were right for `x=√((y−3)/5)` before Part A and are wrong now. Kept (correct); every generated key's subject is a single letter, compared without case.
- *Ordinals.* Every ordinal site in GCSE maths uses the helper (sequences 14 places, multiples 2, procedural MCQ 1); a search finds no other `{n}th`. The detector strips tags first, so `<strong>5</strong>th` is read. Outside GCSE maths, `generators/gcse/physics.py` lines 290 and 293 print "one-4th", "one-8th" and "one-16th" (half-life); not changed (not maths), for David.

**Parser audit (12 seeds of every slot that names the task).**

| Task | Records (truth guard passed) | No record (wording not read) | Guard failures |
|---|---|---|---|
| `fn_eval` | 72 | 36 (two values asked: "Find f(1) and f(5)") | 0 |
| `fn_machine` | 36 | 0 | 0 |
| `fn_inverse_eval` | 12 | 0 | 0 |
| `fn_solve` | 12 (linear answer) | 12 (quadratics) | 0 |
| `seq_special` | 36 | 0 | 0 |
| `seq_sum_arith`, `seq_rows`, `seq_mean`, `seq_u_n` | 12 each | 0 | 0 |
| `seq_geometric` | 12 | 12 (the sum variant) | 0 |
| `gr_parallel` | 24 | 0 | 0 |
| `gr_speed` | 36 | 0 | 0 |
| `substitute` | 23 | 13 ("F = ma. Find F when ...", "find t when ...") | 0 |

No parser raised. Misread fuzz (each printed number edited in turn, 2,642 edited questions): 1,584 give inputs that fail the truth guard (silent), 1,002 give the same inputs (a number the parser does not read), 2 give no record; 54 pass the guard, and all are consistent readings of the edited text, not misreads: 53 are the intercept of `y = mx + c` (an input the truth does not use; its rule names the printed intercept, so the edited text and the rule agree) and 1 is `f(01)`, which is f(1) and happens to equal f(0). A misread of a number the truth uses is always silent.

**Coverage (honest, section 7 metric 1).** **640 of 1,072 practice slots (59.7%) have a topic rule that produces a message on a generated question: 4 slots short of 60% (644).** The build counted 649. The review removed 9: eight were carried only by the six deleted rules, which never decided the message (a generic rule said the same thing about the same value; finding 4), and one (`gcse_dec_proc_money_change`) by the misleading lining-up rule (finding 3). With the count taken as slots where a topic rule decides the message, nothing is inflated now: on the review audit every topic diagnosis differs from what the generic rules alone would say. Generic: 785 (73.2%); either kind: 834 (77.8%), unchanged. The floor `TOPIC_FLOOR_SLOTS` stays at 640 (now the measured value, deterministic since finding 16). Closing the gap honestly needs rules in topics with real slips that are not yet covered (section 23 lists the remaining 432 slots); padding with rules that repeat a generic line was not done.

**Runtime on this machine (2 cores; wall time with start-up; two runs each).**

| Smoke | Phase 5 tree (5b and Part A reverted) | 5b as built | 5b after review |
|---|---|---|---|
| Hints | 20.5, 18.6, 18.7, 21.8 s | 18.0, 17.7 s | 18.4, 16.8 s |
| GCSE verification, alone | 39.0, 37.3, 39.0, 37.7 s | 39.6, 39.6 s | 38.7, 34.3 s |

The new work does not slow the hints smoke (it is about 2 s faster than the Phase 5 tree, from the build's once-per-slot diagnosis). It added about 1.5 s to the verification smoke, all in the ordinal sweep, which the review cut to 0.7 s (finding 17). The rest of the gap to the 15 s and 35 s budgets is this machine: the Phase 5 tree, which met them on the earlier hardware, takes 19 to 22 s and 37 to 39 s here.

**Mutation (on a scratch copy of the tree; each file restored and its SHA-256 compared with the original; 16 of 16 caught, one of them only after the new cases of finding 18).**

| Mutation | Caught by |
|---|---|
| Parser misreads the time in "travelling 48 km in 2 hours" (t + 1) | hints smoke: unit table, rule_reachable, coverage |
| Parser misreads the intercept of `y = mx + c` | hints smoke: unit table (parser table) |
| One-value topic rules fire without the truth guard | hints smoke: unit table, mutation (186) |
| Box rules fire without the per-box truth guard | hints smoke: unit table, mutation (83) |
| `∓` read as a ± | answer check smoke |
| A ± on the left side as well as the right accepted | answer check smoke (new cases, finding 18) |
| A ± accepted for an expression key | answer check smoke (new case) |
| A half power lets a value through the form check | answer check smoke (`((x²+3x)^0.5)²` in expanded form) |
| Half-power bracket made optional again | answer check smoke (`(x^(0.5+1)`) |
| Ordinal helper without the teens rule (11st, 12nd) | verification smoke, `ordinals` |
| Ordinal helper always "th" | verification smoke, `ordinals` |
| Other-box guard off | hints smoke: review cases |
| Question-text guard off | hints smoke: review case (change from £12.50) |
| Key-cut-short guard off | hints smoke: review case (13 for 13.5) |
| Decimal sum reader loose again | hints smoke: review case (1.5² + 2.25) |
| Semicircle line states the answer again | hints smoke: review case |

(Results of the runs: `/tmp/claude-0/-home-claude/c0dffe08-38bf-543d-a322-a83f0f0e3b42/scratchpad/r5b/mut_results.txt` and `mut_results2.txt`.)

**Leaks, storage and output.** `answer_record` is unchanged in shape and still server-only (at most 128 B on generated questions; four families are no longer recorded for hints); the review adds no field, table, log line or event. Generated questions, options, keys and worked solutions are byte-identical to the 5b build (drift run below); against the Phase 5 tree only the two ordinals differ, as the build notes say.

**Files changed in review.** `generators/shared/answer_checkers.py` (half-power reading, ± needs a subject), `generators/shared/misconception_5b.py` (six rules and four families deleted, one rule added, decimal sum reader, `TEXT_GUARDS`, `PART_OTHER_BOX_OK`, four new and three reworded messages), `generators/shared/misconceptions.py` (text guards in `topic_candidates`, other-box guard in `part_topic`, key cut short in `_near_key`), `scripts/gcse_hints_5b.py` (rows for deleted rules removed, seven coincident examples moved, one new row), `scripts/gcse_hints_cd.py` (17 review cases), `scripts/test_gcse_maths_hints_smoke.py` (no timer in `topic_more_seeds`, floor comment), `scripts/test_answer_check_smoke.py` (`test_check_algebraic_plus_minus_review_edges`), `scripts/test_gcse_maths_verification_smoke.py` and `scripts/gcse_verify/ordinals.py` (ordinal sweep on slots that print one), `docs/ZORP_CHARM.md` (Appendix A regenerated), `docs/AI_HANDOFF.md`, `docs/GCSE_MATHS_VERIFICATION.md`, this file (status line, section 23 table, this section).

**Runs.**

| Run | Result |
|---|---|
| `test_gcse_maths_hints_smoke.py` | Passes, 17.7 s with start-up (16.7 s inside; budget 15 s, see runtime). Topic 640, generic 785, either 834; 337 one-value rules (191 families) and 168 pair, box and expression rules all fire; 411 topic and 130 generic hand-worked cases; mutation 17 of 17, 528 of 528 and 273 of 273. |
| `test_gcse_maths_hints_smoke.py --deep` at a new seed offset (31337, by shifting `harness.slot_seed`) | Passes, 134 s; 42,880 questions; topic 642 slots (59.9%), either 839. |
| `test_gcse_maths_verification_smoke.py`, alone | Passes, 35.9 s wall. |
| `test_gcse_maths_verification_smoke.py --deep --seed 271828` | Passes, 261 s. |
| `test_gcse_maths_correctness_smoke.py` | Passes, 14.6 s. |
| `test_answer_check_smoke.py` | Passes, 6.0 s (new `test_check_algebraic_plus_minus_review_edges`). |
| `test_gcse_maths_hints_mcq_smoke.py`, `..._ladder_smoke.py`, `test_mcq_letter_consistency_smoke.py` | Pass. |
| `test_zorp_voice_smoke.py` | Passes (Appendix A regenerated with `--write`). |
| Drift (29,616 generations) | Identical to the 5b build, random state included; against the Phase 5 tree only "33th" to "33rd" and "32th" to "32nd" in two worked solutions. |
| `ruff check .` | Clean. |
| Full suite (`scripts/run_smoke_tests.py`) | 108 of 108 passed (`/tmp/claude-0/suite_h5b_review.log`). |

**For David (not changed).**

- The ± is accepted for the radius and speed rearrangements (see Part A decisions); say if those two should take the positive root only.
- `generators/gcse/physics.py` prints "one-4th", "one-8th", "one-16th" in a half-life question.
- The Phase 5 box rules (before 5b) have no other-box guard; this review audited the 5b rules only.
- Topic coverage is 4 slots short of 60%.


---

## 25. Phase 5c: closing the gap to 60% (2026-10-27, not committed)

**Result: 657 of 1,072 practice slots (61.3%) have a topic rule that decides a message on a generated question; the 60% target (644) is met with 13 to spare.** Section 24 left the count at 640 (4 short). Seventeen slots are new and nothing else moved (generic 785, either 834 unchanged: all 17 already had a generic hint). Measured as the review did: for every topic diagnosis on a real seed the same typed value was also run with the record removed, and each of the 657 slots has at least one where the topic message differs from the generic-only message (or the generic rules say nothing). The floor `TOPIC_FLOOR_SLOTS` is now 657. Nothing is committed.

**Where the 17 came from.** The list of 225 diagnosable but uncovered slots was re-read slot by slot, with the verification record each one already emits (no `record()` line was added and no generator output changed). Every slip below is one the generic rules cannot name. Candidates that only repeated a generic line on the same value were dropped before building: rounding to fewer decimal places or to the tens (`gen.accuracy_coarser`), a decimal point misplaced in a product, a decimal changed to a percentage ten times too small (`gen.pow10`, `gen.as_percentage`), and the `num_round_unit` slot (the pupil's slip there is the rounded-wrong-place value, which the stated-accuracy rounding turns into the one-step-off value that `gen.truncated` names).

| Slot (family) | Rule (message) | Example question, typed |
|---|---|---|
| Round to d.p. (`num_round_dp`, `gcse_dec_round`) | `num.round_dp_as_sf`: "Decimal places are the digits after the point. Significant figures start at the first digit that is not zero." Decimal places counted as significant figures. Silent when that value is also fewer decimal places, the decimals dropped or the tens (776.4342 to 3 d.p. typed 776; 22.835 to 1 d.p. typed 20). | "Round 812.2411 to 1 decimal place.", typed 800 |
| Round to s.f. (`num_round_sf`) | `num.round_sf_zeros`: "A rounded number stays about the same size. Fill the places after the last digit you keep with zeros." (wording changed in review) Only when the digit alone is four or more places short (the generic place-value line reaches three). | "Round 76243 to 1 significant figure.", typed 8 |
| Find the index (`num_find_index`) | `num.index_divided`: "The index counts how many copies of the base are multiplied together. It is not found by one division." (wording changed in review) | "Find the value of n if 3^n = 729.", typed 243 |
| Consecutive integers, two slots (`consecutive_sum`) | `alg.consecutive_equal`: "The integers go up by one each time, so they are not all equal to x. Add in the extra amounts too." (total over n) | "The sum of 8 consecutive integers starting from x is 124. Find x.", typed 15.5 |
| Taxi, fixed plus rate (`linear_fixed_rate`) | `lin.fixed_ignored` ("The fixed charge is paid once. Take it off the total before dividing by the rate."; 15), `lin.fixed_added` ("The total already includes the fixed charge. Take it away, rather than adding it on."; 17), `lin.cost_not_divided` ("That is the cost of the miles. Divide by the cost of one mile to find how many."; 91) | "A taxi charges a £14 fixed fare plus £7 per mile. The total fare is £105. How many miles were travelled?" |
| Think of a number (`think_number`) | `eq.think_undo_order` (existing `fn.undo_order`; 0.25), `eq.think_wrong_inverse` (existing `seq.constant_inverse`; 2.5) | "I think of a number. I multiply it by 8 and add 2. The result is 18." |
| Rectangle, perimeter in w (`rect_perimeter_linear`) | `eq.perimeter_one_each`: "The perimeter goes all the way round the rectangle. That is two lengths and two widths." (perimeter taken as one length plus one width) | length 2w + 4, width w, perimeter 80 cm, typed 25.33 |
| Fibonacci-type next term (`seq_terms`, existing family) | `seq.fibonacci_constant_step`: "Each term in this sequence is the sum of the two terms before it. Check which two were added." (last gap repeated, which is always also the last term plus the third-last; wording changed in review) | "1, 1, 2, 3, 5, ___", typed 7 |
| Geometric sum (parser `seq_geometric`, `seq_geo_sum`) | `seq.geometric_sum_unshared` ("Check the sum formula. The top of the fraction is divided by one less than the ratio."; silent for r = 2, where it is the key) and `seq.geometric_sum_last_term` ("That is the last term of the series. The question asks for the sum of all the terms.") | "sum of the first 10 terms, first term 2, ratio 3", typed 118096 or 39366 |
| Sum to infinity (`seq_geometric_infinite`, `seq_geo_inf`) | `seq.infinite_over_ratio` and `seq.infinite_plus_ratio`, one message: "The sum to infinity divides the first term by one minus the ratio. Check the bottom of that fraction." | "first term 5, common ratio 1/4", typed 20; "first term 7, common ratio 1/3", typed 5.25 (5 / 1.25 = 4 is the printed 4, so silent) |
| Arithmetic sum from first and last term (`seq_sum_last`) | `seq.sum_last_not_halved` (existing `seq.sum_not_halved`) | "first term 6, last term 120, 20 terms, find S20", typed 2520 |
| Salary in year n (`seq_context`) | `seq.context_extra_step` (existing `seq.steps_one_fewer`) | "£294 in year 1, up £30 a year, salary in year 9", typed 564 |
| Surd equation (`surd`, `surd_sqrt_eq`) | `surd.equation_not_squared` ("Square both sides to remove the square root. The root cannot be ignored."; r - c) and `surd.equation_sign_moved` (existing `alg.sign_moved`; r² + c) | "Solve: sqrt(x + 32) = 8", typed -24 or 96 |
| Surd quotient (`surd_div`) | `surd.quotient_root_missed`: "Dividing the numbers under the roots is the first step. The square root of the result is still needed." | "Simplify sqrt(20) / sqrt(5)", typed 4 |
| Difference of two squares in surds (`surd_conj`) | `surd.conjugate_sign` ("Check the last term. A positive surd times a negative surd gives a negative."; a² + b) and `surd.conjugate_unsquared` ("The whole number is squared as well as the surd. Check the first term."; a - b) | "Expand and simplify (3 + sqrt 7)(3 - sqrt 7)", typed 16 or -4 |
| Angles of a triangle in x (`angle_sum`, `ang_sum_x`) | `ang.sum_x_wrong_total` (existing `ang.wrong_total`; the total taken as 360) | "angles x + 5, 3x + 15, 2x + 70", typed 45 |

That is 23 rules in 15 new families and 16 new messages (the other seven messages are reused), in `generators/shared/misconception_5b.py` (section "Phase 5c"). Five new parsers (`seq_geometric_infinite`, `seq_sum_last`, `seq_context`, `surd`, `angle_sum`) and the `seq_geometric` parser widened to the sum variant. Same contract as before: inputs rebuild the key (a parser that does not recognise the wording returns nothing), nothing fires on the key, next to the key or on a number printed in the question, an ambiguous value is silent, no message gives a value (D5), British spelling, no dash, no emoji. Two words went on the hint long-word list (`significant`, `infinity`, both words the question itself uses; `models/zorp_voice.py`).

**Not done, and why.** Still without a topic rule: the multiple choice (66), proof steps (38), keyword (17) and number-list slots, the 98 diagram-style multi-box slots, and the surd, algebraic-fraction and completed-square answer slots (algebraic fractions 12, surds 11, completed square 6). Those answer types have no route in the check endpoint for a topic rule yet (`RECORDED_ANSWER_TYPES` holds `algebraic` only for expression families with a comparison against the checker's algebra), so a rule there would need a new route and front-end handling, which is a phase of its own. Of the surd slots, the three with a plain number answer are done above.

**Tests.** `scripts/gcse_hints_5b.py` has a hand-worked row for each of the 23 rules, 8 parser rows and 10 parser rows that must read nothing; `scripts/gcse_hints_cd.py` has 13 "5c" cases (silences and coincidences: 776 for 776.4342 to 3 d.p., the tens for 22.835, 5 for 5304 to 1 s.f., a ratio of 1/2 where a over r is the key, a fixed charge printed as 50 / 5, an arithmetic pattern that is not Fibonacci, inputs that do not reproduce the key, 0 decimal places, the angle total of 90). The row for `num.round_sf_zeros` states no accuracy in its question text on purpose: rounding the stated accuracy hides a truth that is out by one, so the mutation check would not notice. Rule mutation: 566 of 566 topic perturbations caught. Hand mutations on a scratch copy of the tree (each caught): the decimal-places exclusion off, the four-places shift guard off, the Fibonacci pattern check off, the surd conjugate same-number check off, the triangle-word check on the angle parser off. One mutation survives by being equivalent: the `r != 2` test in `seq.geometric_sum_unshared` (the value equals the key there and is dropped anyway).

**Physics wording (outside maths, found in section 24).** `generators/gcse/physics.py` `rad_inter_half_life_time` printed "one-4th", "one-8th" and "one-16th" in the question and in the worked solution. It now says "one quarter", "one eighth" and "one sixteenth" (the hint keeps 1/4, 1/8 and 1/16). A drift run over every public physics generator (60 seeds each, 1,860 generations, old file from `HEAD`): only this function differs, in those words. A search of every generator, level and subject, for `{n}th`, `-4th`, `1th`, `2th`, `3th` and `one-Nth` found no other place. The verification smoke's `ordinals` check now also flags a fraction written as an ordinal (`one-4th`, `1/8th`; `scripts/gcse_verify/ordinals.py`, `fraction_word_errors`), reads the half-life generator over 60 seeds (it must name exactly one quarter, one eighth and one sixteenth), scans the source of every generator for a hand-written `}th` or a fraction word (`source_errors`, 0 hits), and has a mutation (the old wording and the old source line must be caught).

**Runs (this machine).** Hints smoke 16 to 17 s (budget 15 s on faster hardware, as in section 24); verification smoke alone about 37 s; correctness, answer check, voice, MCQ notes and ladder smokes pass, `ruff check .` is clean, and the full suite (`scripts/run_smoke_tests.py`) passes 108 of 108 (`/tmp/claude-0/suite_gap.log`).


### §25 review notes (2026-10-27, independent review, not committed)

**Method.** Every 5c candidate was typed through the real diagnosis on every practice slot (12 seeds at offset 0 and 80 seeds at offset 1000; 1,720 fired 5c diagnoses), each read beside its question, with the same value also run with the record removed (generic-only message) and flags for a value printed in the question or equal to another box's key. The six parsers were run on 15 seeds of every slot that names their task (281 surd questions among them, 240 of other surd kinds correctly read as nothing) and on 868 edited questions (each printed number changed in turn): 628 fail the truth guard, 150 no longer parse, 90 give the same inputs (a number the parser does not read: "year 1", the 2 of the printed formula, the S₂₀ label, the first of two "year 9"), and **none is a misread that passes the guard**. Ten wording and LaTeX variants (a minus sign, `\frac`, "decreases", "quadrilateral", a negative ratio, the brackets swapped, a cube root, x − c, 2x, a finite sum) are all silent, except `\frac` in the formula that `seq_sum_last` does not read (same inputs).

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | Medium (coincidence) | A 5c slip on the key with its sign changed, the key upside down or ten times the key was named as the topic slip although the generic line fits as well: "Solve √(x + 21) = 6", typed −15 (6 − 21, and −15): "Square both sides..."; (2 + √3)(2 − √3) typed −1; "multiply by 5 and add 5, result 15" typed −2; "multiply by 4 and add 2, result 10" typed 0.5; a £36 fixed fare at £2 a mile, £44, typed 40. 13 in 80 seeds. | `_apart` in `misconception_5b.py`: every 5c slip is silent on −key, 1/key and key × 10^±1..3, so `gen.sign`, `gen.reciprocal` or `gen.pow10` speaks. The cost of the miles keeps its line at £10 a mile (`pow10=False`: ten times the key is its own step there). |
| 2 | Medium (coincidence) | `ang.sum_x_wrong_total`: the 360 value equals one of the triangle's angles at the right x in 2.2% of draws (x + 30, 4x + 13, x + 17 gives 50, the first angle), which a pupil who found x and typed the angle also reaches. | Silent on any of the three angles. |
| 3 | Low (coincidence) | `num.round_dp_as_sf` on "Round 850.5049 to 2 decimal places", typed 850: that is also the decimals cut off; the exclusion held rounded values only. | Cut-off values at the same places are excluded too. |
| 4 | Low (copy, maths) | In a Fibonacci-type sequence the last gap repeated always equals the last term plus the third-last (for 1, 1, 2, 3, 5 both readings give 5 + 2 = 7), so "The gap between terms is not fixed" misreads half the pupils. | "Each term in this sequence is the sum of the two terms before it. Check which two were added." |
| 5 | Low (copy) | `num.index_divided` said the index counts "how many times the base is multiplied by itself" (3⁶ is five multiplications). | "The index counts how many copies of the base are multiplied together. It is not found by one division." |
| 6 | Low (copy) | "Rounding keeps the size of the number" reads oddly beside 8 for 76243. | "A rounded number stays about the same size. Fill the places after the last digit you keep with zeros." |
| 7 | Low (hardening) | The conjugate parser and truth took a square under the root, (2 + √4)(2 − √4) (not generated today). | Refused in both. |
| 8 | Low (test) | `fraction_word_errors` flagged any hyphenated word before an ordinal ("the n-1th term", "x-4th", "Year-10th") and always suggested "one quarter or 1/4". | Number words only (one to ten, a, an), plural endings caught ("two-3rds"), a neutral message; five new cases. |
| 9 | Low (test, since section 24) | The verification smoke printed "N issue(s)" without the rows of checks missing from `CHECK_NAMES` (`ordinals`), so an ordinal failure showed no detail. | Unlisted checks are printed after the listed ones. |
| 10 | Doc | The table above gave "first term 5, ratio 1/4, typed 4" as a sum-to-infinity example; 4 is printed in that question, so the rule is silent. | Example replaced. |

**Checked and kept.** Typed 8 for "Round 76243 to 1 significant figure" is the digit kept without its zeros (5-digit numbers at 1 s.f. only). Taxi with the fixed fare equal to the rate (£10 to £12): miles + 1 is the total over the rate, miles + 2 the fixed charge added, both lines true. Sum to infinity with ratio 1/2: a over r is the key (silent), a / 1.5 = 2a/3 meets no other modelled value, and values that are a printed number (3 / 1.5 = 2, 4 / (4/3) = 3, 2 / (2/3) = 3) are silent. The conjugate with a² = b cannot be generated. The 360 value on a printed constant (1.5% of draws) is silent by the existing guard. The Fibonacci rule reads only sequences where every term is the sum of the two before. The physics question reads naturally ("fall to one quarter of its original value"; "To fall to one quarter of the original value takes 2 half-lives."); the ordinal checks leave "the 4th term", `\(\frac{1}{4}\)th`, `<strong>5</strong>th`, "4th second" and units alone.

**Coverage (section 24 metric).** **657 of 1,072 practice slots (61.3%)**, unchanged by the review; the floor stays 657. The audit at 8 seeds and offsets 0 and 100 finds 658 slots where a topic message differs from the generic-only message at each offset (one slot more than the smoke's seed plan reaches), and 659 at 80 seeds both before and after the review: no slot was lost. The 17 slots carried only by 5c rules all still have a deciding diagnosis, and all 23 rules still fire (between 20 and 160 times in 80 seeds).

**Mutation** (scratch copy, each file restored and its SHA-256 compared; 20 of 20 caught): `_apart` off; its sign part off; its power-of-ten part off; the angle exclusion off; the cost of the miles under the power-of-ten guard; the square-root refusal off in the parser, and in the truth; the cut-off exclusion off; the sum-to-infinity parser with the ratio inverted; the surd equation parser misreading the right-hand side; the angle parser reading any shape; the salary parser misreading the year; the old Fibonacci line; a sum-to-infinity line that states a value (D5 lint); the fraction detector widened to any word; the fraction detector off; the old physics wording (in text and in source).

**Files changed in review.** `generators/shared/misconception_5b.py`, `scripts/gcse_hints_cd.py` (11 review cases), `scripts/gcse_verify/ordinals.py`, `scripts/test_gcse_maths_verification_smoke.py`, `docs/ZORP_CHARM.md` (Appendix A regenerated), this file.

**Runs.** Hints smoke passes (17.6 s; topic 657, generic 785, either 834; 566 of 566 topic perturbations caught); verification smoke 38.0 s; correctness 15.1 s; answer check 6.5 s; voice, MCQ notes and ladder smokes pass; `ruff check .` clean; full suite `/tmp/claude-0/suite_gap_review.log`.

## 26. Variety plan Phase 1: floors as shares (2026-10-27, not committed)

`docs/GCSE_MATHS_VARIETY.md` Phase 1 retired 76 practice names and merged 31 into 13 dispatcher slots, so the practice slot count went from 1,072 to 1,010. The coverage floors were absolute counts (`HINTS_FLOOR_SLOTS` 775, `TOPIC_FLOOR_SLOTS` 657, `COMBINED_FLOOR_SLOTS` 825) and would have failed although nothing got worse. They are shares of the practice slots now: `HINTS_FLOOR_SHARE` 72.0% (generic), `TOPIC_FLOOR_SHARE` 61.0% (topic rule), `COMBINED_FLOOR_SHARE` 77.0% (either), with `HINTS_FLOOR_TYPES` unchanged at 7. Measured after the phase: generic 741 of 1,010 (73.4%), topic 618 (61.2%), either 784 (77.6%); after the review (the enlargement pair split again, 1,011 slots): generic 742 (73.4%), topic 619 (61.2%), either 785 (77.6%), identical over three runs (the smoke's seeds are fixed, so the 2-slot topic margin cannot flap, it can only be used up by a change); before: 785, 657 (61.3%), 834 of 1,072 (73.2%, 61.3%, 77.8%). The per-rule reach checks are unchanged, and no rule was added or changed.

Two things to know. The topic-share margin is small (618 against a floor of 616), so a phase that retires slots with a topic rule more often than the average needs a rule or a note. And one rule, `prob.die_one_prime`, lost a carrier when `_prob_found_13` was retired (the die question draws "prime number" about 1 time in 12); `topic_more_seeds` now runs 20 rounds instead of 12 and, once every wanted family is carried by a slot, draws only those slots, which keeps the smoke at 16.6 s (18.4 to 18.8 s on the previous tree today, same machine). The new difficult algebra kind `algebra_practice_factorise_quadratic` has generic hints only; a topic rule for it is a later hints phase.

## 27. Variety plan Phase 2: pins (2026-10-27, not committed)

The MCQ notes smoke's `DRIFT_PIN` moved from `b9506240b2b852da` to `7f9c174ebfed69c0`. Of the 45 tagged generators only `number_mcq` 15 (the percentage-error option now has 1 d.p. like its siblings), 17 (standard form no longer prints "52.0") and 18 (money options all to the penny) changed, and each fix is formatting only: no key moved and no note id changed. `BANK_PINS` did not move (bank rows and notes are unchanged; the new `concept` flag is an extra key outside the digest). Notes covered 460 of 675 procedural distractors (was 459). The endpoint check "body ignored" now allows any reviewed misconception message, because the practice question it lands on can now be a different topic. Ratio types 10 to 12 and three algebraic fraction generators were added with at most the existing `ratio.part_to_part` and `mcq.ratio_part_as_amount` notes. The hints smoke takes 15.5 s here, the ladder 3.3 s and the notes smoke 2.8 s.

**Review (2026-10-27, variety plan section 16).** `DRIFT_PIN` moved again, to `5e5176eeffc25658`, for `_trig_proc_find_side` only (per-generator hashes against the tree before Phase 2: this generator and `number_mcq` 15, 17, 18). At 45° the side was both key and distractor and the options mixed "10" with "5.0"; every option is now to 1 d.p. and the 45° slips (sin 45° × side, side ÷ sin 45°) carry `trig.wrong_ratio`, verified: notes 466 of 675 (was 460). The endpoint check "body ignored" is pinned again: the note must equal `option_notes.picked_note` of the stored question's option A, and the request names a note that option A does not carry (a body-honouring endpoint now fails it; with "any reviewed text" it passed).

## 28. Variety plan Phase 3 batch A: rules for the new slots (2026-10-27, not committed)

The 56 new practice slots of `docs/GCSE_MATHS_VARIETY.md` section 17 were built with the hints contract in mind: 38 of them (67.9%) can produce a topic hint, 18 cannot (multiple choice, surd answers, a list answer, and eight algebra slots with no recorded family). The topic count is 659 of 1,064 slots (61.9%), the combined count 820 (77.1%).

* **Rules.** 52 new rules (49 in `generators/shared/misconception_5b.py` (section "Phase 3 batch A"; 3 more are expression rules) for fractions (bottoms added, divided without turning over, mixed numbers split, the fraction written upside down or with the units ignored, the HCF typed for the simplified fraction), simple and compound interest (the wrong kind, one year only, the interest instead of the total and the other way round, the compound interest alone), multiples and factors (the multiple below, the ends of a factor list missed, pairs counted, multiples counted from zero, powers added or multiplied, the lap counts swapped or the lap times typed, the powers matched to the other primes), reciprocal and counting, ratio from a difference, y proportional to x squared, the combined ratio, forming equations (perimeter, angles, area), the missing number and fraction-bar bidmas lines, the square of a surd, and rounding error. Forming an expression has expression rules in `misconception_cd.py` (`alg_form_expr`: numbers matched to the other items, "times as old" read as "older than", one width and one length for the perimeter). The same contract as before: the family's `TRUTH` must rebuild the key, `_apart` drops a slip that a generic sign, reciprocal or power-of-ten rule explains equally well, and a slip that equals a printed number is silent unless the rule is in `ECHO_OK` (a swap, a copied lap time, the number itself).
* **Dropped on the way.** A rule for "the first fraction turned over" was removed: its value is always the reciprocal of the key, so it could never be told apart from the generic reciprocal line.
* **Messages.** 42 new messages are in the main `MESSAGES` literal (the voice lint reads only that literal, so an `update()` call is not enough; the lint now fails if one is missing). Four words were rewritten to pass the voice lint (separately, reciprocal, proportional, operation), and "wrong" was avoided in two lines.
* **Unit table.** `scripts/gcse_hints_5b.py` has a hand-worked row for each of the 52 new rule ids; the mutation check catches all 639 topic and 284 pair, box and expression perturbations.
* **Smoke changes.** `NINE_TOPICS` gained `surds` and `multiples_factors`; `topic_more_seeds` now also counts the pair, box and expression rules that have not fired, and reads the families those rules carry (before, an expression rule on a one-in-three draw could never get extra seeds); `PART_OTHER_BOX_OK` gained `mf.exponents_swapped`. Floors: `TOPIC_FLOOR_SHARE` 0.615, `COMBINED_FLOOR_SHARE` stays 0.770 (the new slots diluted the share; 819 of 1,064 would have fallen under 820 without the form-expression rules). The smoke takes about 12 s here (it was 15.7 s before the batch; the seeds are cheaper once the rules fire early).
* **Pitfall.** `F` in `misconception_5b.py` takes one argument; `Fraction(a, b)` needs the real class. A rule that raises is silently skipped by the machinery, so a typo shows only as a rule that never fires.


**Review notes (2026-10-27, independent review; `docs/GCSE_MATHS_VARIETY.md` section 18).**

* `frac.denominators_added` now reads "It looks like the bottoms were added or taken away as well. A common denominator stays as it is." It is also the message of the subtraction slip ((n1 − n2)/(d1 − d2)), which the old wording called "added". Appendix A of `docs/ZORP_CHARM.md` was regenerated.
* `bidmas.missing_wrong_inverse`, `alg.angles_sign_moved`, `alg.angles_x_once` and `alg.perimeter_sign_moved` keep only whole-number slips (`_whole` in `misconception_5b.py`). The answers are whole numbers, and a non-whole slip was matched by rounding: 11 typed for "7 × □ − 4 = 80" (key 12) was "the wrong inverse" because 76/7 rounds to 11. Two `other_cases` lines in `scripts/gcse_hints_cd.py` keep these silent, and one checks the denominators wording.
* A unit-table row for `ratio.difference_part` when the smaller share is asked for (a mutant of that branch passed before).
* A probe of 22 of the rule-bearing new slots (40 generated questions each, typing the key ±1, ±0.1, doubled, tripled, halved and every printed number) found no other message naming the wrong cause; same-family collisions (sum and product of the powers both 4, pairs and ends both 3 for 16) are silent by the existing `len(hits) != 1` rule.
* `DERIVE_NONE` "Expand 3(x + 2)": keep it (see section 18.4 of the variety plan). Single brackets need their own `expand1` family, not the two-bracket parser.

## 29. Variety plan Phase 3 batch B: rules for the new slots (2026-10-28, not committed)

82 new practice slots (`docs/GCSE_MATHS_VARIETY.md` section 19). Only the record families can carry a topic rule, so 19 of them (23%) can produce a topic hint; the rest are checked by `@verifies('alg')` tasks (roots, expressions, readings from a graph) or are multi-answer lists with no recorded family. Topic slots are 686 of 1,146 (59.9%), combined 881 (76.9%), so `TOPIC_FLOOR_SHARE` is 0.595 and `COMBINED_FLOOR_SHARE` 0.765 (batch A: 0.615 and 0.770).

* **Rules.** 22 new rules in `generators/shared/misconception_5b.py` (section "Phase 3 batch B"), 21 messages in the main `MESSAGES` literal: the expression `xy` or `x^2 + y^2` read as `x + y`; the y term not multiplied when the equations are matched; the fixed fee missed or the rate difference not divided in an equal-cost problem; ages in the future typed; one term used when substituting; the constant of the completed square not adjusted or the square added; the minus-bracket form; the number of solutions with the sign flipped; the constant only for `c`; the x-values typed for the y-values; the circle gives y squared; the discriminant (tangent and no-intersection slots); the midpoint put on the curve; the undefined value not divided; the inverse applied the wrong way or with the wrong sign; the iteration with the added number missed; the change-of-sign table with the sign of the constant changed.
* **Contract.** The same as section 28: `TRUTH` rebuilds the stored key from the printed numbers, messages never give a value, `_apart` drops slips a generic rule explains, printed numbers are silent unless `echo`. Four messages were reworded for the copy lint (length, reading level, "discriminant", "operation", and a number named in a message).
* **Unit table.** `scripts/gcse_hints_5b.py` has a hand-worked row for each of the 22 rule ids; the mutation check catches all 659 topic and 305 pair, box and expression perturbations.
* **Smoke changes.** `check_negative_control` adds the topic-rule candidate values to the values a far-away wrong answer must avoid (a seeded draw landed on 18 = 7 + 11 after the slot lists grew and was read as the generic "divided for product"). Runs: hints 16.9 s (was 18.0 s on the pre-batch tree under load), ladder and MCQ notes pass.


**Review notes (2026-10-28, independent review; `docs/GCSE_MATHS_VARIETY.md` section 20).**

* A probe of the 22 rules (30 generated questions each, typing the key ±1, doubled, halved, negated and every printed number) found no message naming the wrong cause; two near-miss overlaps are accepted (xy = 6 typed as 5, which is also x + y; a minimum of 4 typed as 3, which is also its x-value).
* **Topic coverage is 690 of 1,146 slots (60.2%), so `TOPIC_FLOOR_SHARE` is back to 0.600** (it was lowered to 0.595 for the batch). Seven new rules on five slots, each with a hand-worked unit row: `qsim.sub_signs_kept` (family `qsim_sub_coeffs`, which had a record but no rule; it uses the existing `alg.sign_moved` message, already allowed to speak on a sign-only pair slip), `fn.neg_input_sign`, `fn.neg_input_implied`, `cts.min_read_x_value`, `cts.min_nonmonic_x_value`, `cts.min_nonmonic_a_missed` and `ap.bracket_second_term`. Four slots are newly counted; `fn_f_negative_input` was already counted through the `fn_eval` question parser (family `gr_subst`, rule `sub.coefficient_implied`), and `fn.neg_input_implied` keeps that slip (same message) in its new family. Four new messages (`fn.negative_not_bracketed`, `cts.min_x_not_y`, `cts.a_not_multiplied`, `alg.bracket_not_all`); one draft failed the reading-level lint (9.1) and was reworded. Appendix A of `docs/ZORP_CHARM.md` was regenerated.
* **Why a record line was not enough.** `answer_record.build_record` keeps a record only when exactly one was captured, so a slot tagged `@verifies('alg')` that also calls `record()` gets none. The four slots (`fn_f_negative_input`, `cts_f_read_min_value`, `cts_d_min_non_monic`, `ap_f_simplify_to_constant`) now record a family instead of the task, with an independent solver each (`solvers_variety_b.py`); their output is byte-identical.
* `qsim_largest_k_miss` gained the curve constant `c0` (default 0) in its TRUTH and slip (the generator now varies the curve); a unit row with `c0 = -2` was added.
* Combined coverage is unchanged at 881 (76.9%, floor 0.765): the five slots already had a generic hint. Two more slots with any hint would restore 0.770.
* Hints smoke: 690 topic slots; see the final run in section 20.6 of the variety plan for the unit-table and mutation counts.

## 30. Variety plan Phase 3 batch C1: rules for the new slots (2026-10-28, not committed)

47 new practice slots (`docs/GCSE_MATHS_VARIETY.md` section 21), built with the hints contract in mind: 41 of them (87.2%) can produce a topic hint. The six that cannot are the two line equations (`linear_equation` answers carry no record), the perpendicular gradient (its only slips are the generic sign and reciprocal lines), the median class (a choice), the graph feature (a coordinate pair whose only natural slip is the generic swap) and the missing frequency from a mean (its natural slip is whole too rarely to carry a rule). Topic slots are 715 of 1,171 (61.1%), combined 908 (77.5%), so `COMBINED_FLOOR_SHARE` rises from 0.765 to 0.770. The batch raised `TOPIC_FLOOR_SHARE` to 0.605 as well; the review (docs/GCSE_MATHS_VARIETY.md section 22.5) measured 60.5% to 60.9% on five other seed pairs, so the topic floor stays at 0.600.

* **Rules.** 65 new rules in `generators/shared/misconception_5b.py` (section "Phase 3 batch C1") on 31 record families, 51 messages in the main `MESSAGES` literal. Statistics: the other margin of a two-way table read, one part typed for a total, the grand total typed for a missing cell, a missing cell worked from a line with two gaps, the wrong total under a percentage, a leaf typed without its stem, the largest value, the range or the upper quartile typed for the IQR, the mode's frequency typed for the mode, the middle row typed for the median, the median's position typed for the median, the mean of the known values or the count short by one for a missing value, the mean of the two means, a sample or capture-recapture proportion the wrong way up, the tallest frequency or the class end typed from a frequency polygon, the frequencies averaged, the time series mean over every point or not divided. Probability: distinct totals counted as outcomes in a sample space, the total or the other group's number typed in a frequency tree, the joint probability typed for a conditional one (tree, two-way table, Venn), one cell typed for a group total, union and intersection confused, the overlap counted twice, a set not complemented, "neither" missed, a complement ignored, the wrong circle. Graphs: the radius not squared or the coordinates added for k, the root missed or k halved for the radius, the area typed for a gradient and the gradient for an area, the whole rectangle or the middle section only, a shift the wrong way or inside and outside confused, a at x = 1, b not divided or taken as a difference. Ratio: a cube, square-root or inverse-square relation treated as linear or square, the inverse square as inverse or direct, the counters added typed as a part, the larger ingredient's count typed for the limiting one. Trigonometry: the other solution typed, the second solution from the wrong rule. Pythagoras: the diagonals of the rhombus not halved, the diagonal squared not halved for the square's area, a half diagonal typed as the side, the algebraic sides added.
* **Contract.** As in sections 28 and 29: the family's `TRUTH` rebuilds the stored key from the recorded inputs, messages never give a value, `_apart` drops a slip a generic sign, reciprocal or power-of-ten rule explains equally well, and a slip that equals a printed number is silent unless the rule says `echo=True` (the exponential a and b read from the graph, where the printed coordinates are the natural slips).
* **Dropped on the way.** A "total without x" rule for the missing frequency (whole too rarely to fire), a "reflected in the other axis" rule for the transformed point (the generic sign line), and a radius slip that was a power of ten of the key for k = 100 (the circle generator now draws Pythagorean pairs more often, so the unit example is (3, 4) and k = 25). Two draft ids collided with the existing `prob.venn_not_complemented` and `prob.venn_neither_missed` and were renamed with `_set_`.
* **Review (section 22 of the variety plan).** `gr.shift_wrong_way` now reads the same for both shifts ("The sign inside the bracket works the other way round. f(x + a) moves the graph left, f(x − a) moves it right."); two draws were narrowed so a hint cannot name a wrong cause (x ≠ y in the transformed point; the three velocity-time slips never equal a printed number).
* **Messages.** Several drafts were reworded for the copy lint ("just", "population", "everything", "y-coordinate", "inversely", "proportional", a number named in a line, reading level over 8). Appendix A of `docs/ZORP_CHARM.md` was regenerated.
* **Unit table.** `scripts/gcse_hints_5b.py` has a hand-worked row for each of the 65 rule ids (`_C1_CELLS` and `_C1_VENN` hold the shared table and Venn inputs); the mutation check catches all 750 topic and 322 pair, box and expression perturbations.
* **Runs.** Hints smoke 17 to 19 s on this machine (16.9 s on the batch B tree); ladder and MCQ notes smokes pass.

## 31. Variety plan Phase 3 batch C2: rules for the new slots (2026-10-28, not committed)

20 new practice slots (`docs/GCSE_MATHS_VARIETY.md` section 23), 16 of them (80%) with a topic hint rule. The four without: the three `linear_equation` answers (a line through two points, a parallel line through a point, a perpendicular bisector: that answer type carries no record, as in batch C1) and the `ratio` answer (a ratio of two expressions: the engine has no ratio type). Topic slots are 716 of 1,173 (61.0%), combined 908 (77.4%); both floors (0.600 and 0.770) stand.

* **Rules.** 31 new rules on 16 record families in the batch C2 block of `generators/shared/misconception_5b.py`, 29 new messages (two reuse `ratio.middle_not_matched` and `alg.sign_moved`). Probability: the counters put back (the with-replacement total) or the total typed for the other colour; two chances added without the overlap, the product typed for "or", the union typed for "exactly one"; three picks with replacement or one colour only; the second day taken as independent, both days typed for "at least one", one branch for "exactly one"; the chances added over the tries; the joint probability or the raw counts typed for "which bag". Ratio: the other person's age or the ages after the years; two fractions of different groups added, one group only, the rest not taken from one; the total halved before the percentage, the other share; the middle parts not matched (the existing `ratio.middle_not_matched` message) or the gap taken as one part; the cross-multiplication swapped. Graphs: the y-intercept typed for the x-intercept (a pair rule), the given coordinate put in for the wrong letter or the sign kept when the constant moves (`alg.sign_moved`), the rise typed for the gradient (`echo=True`: the points are read from the drawing), the conversion read the other way. Statistics: the frequency (echo) or the width typed for the frequency density (`_apart(..., pow10=False)`, since a width of 10 is itself a power of ten), the height divided by the width for the frequency.
* **Contract.** As in sections 28 to 30: `TRUTH` rebuilds the key from the recorded inputs (the counters family needs an exact integer root; a 60-digit approximation from `sqrtq` is never used), `_apart` drops a slip a generic rule explains, and a slip equal to a recorded input stays silent unless `echo=True`.
* **Unit table.** `scripts/gcse_hints_5b.py`: a hand-worked row for each of the 31 rule ids (584 topic rows in all); the mutation check catches 795 of 795 topic and 324 of 324 pair, box and expression perturbations. Four first-draft rows typed a value equal to a recorded input (the gap, the gradient, the class edge, an x of 1) and were silent by the echo rule; they were reworked with other numbers rather than marked `echo`. The counters truth first used `sqrtq`, which returns a 60-digit approximation for a non-square, so its "with replacement" slip was a huge fraction and the whole diagnosis went quiet; it now takes an exact integer root or nothing.
* **Messages.** Three drafts were reworded for the copy lint ("probabilities", a 123-character line, "wrong"). Appendix A of `docs/ZORP_CHARM.md` regenerated.
* **Runs.** Hints smoke 17 to 19 s on this machine (the same as the C1 review measured); ladder and MCQ notes smokes pass.

### §31 review notes (2026-10-29, independent review, not committed)

* All 31 rules sampled on 30 generated questions of every C2 slot with the key ±1, doubled, halved, negated, its reciprocal and every printed number (`docs/GCSE_MATHS_VARIETY.md` 24.5). One misdiagnosis: `gr.coordinate_sign_moved` reaches (given + c)/m, a fraction (26/3) when the key is whole (8), and the engine's rounding of a non-terminating slip to the pupil's places called a typed 9 (the key plus one) a sign slip. The two rules of `gr_missing_coordinate` now offer whole-number slips only (`_whole`); their unit-table rows still fire; the hints smoke passes (11.5 s on the review machine, 584 topic rows, 795 of 795 topic perturbations caught).
* Coverage on other seed pairs (offsets 2, 10 and 50, in a copy of the tree): 713, 710 and 713 topic slots (60.5% to 60.8%), 907, 906 and 906 combined (77.2% to 77.4%); both floors hold.

## 32. Whole-change review fixes (2026-11-03, not committed)

Fix pass 2 of the whole-change review (findings F1 to F10 of review B, the hints system). Each fix has a regression test that fails on a copy of the tree from before this pass.

* **F1 (High), the key written short.** `_topic_hits`: when the typed value is the key rounded or cut to the decimal places the pupil typed (`_key_cut_short`, any scalar answer type, typed as a plain decimal), no slip that only rounds to it speaks ("0.4" for 4/9 was "the item is put back"). Stricter than proposed: a slip that is exactly that short decimal by chance is silent too (9/25 typed 0.3 is exactly 3/10 without replacement; 19/36 typed 0.5 is exactly nine of 18 distinct products), because the pupil has more likely divided the right fraction. Only a rule whose slip is the key written short by its nature may speak there, at its exact value (`CUT_SHORT_RULES`: `num.recurring_terminating`, so 0.3 for 1/3 keeps its line). The same slip typed as a fraction (3/10) is still named. Tests: `topic_cases` F1 rows and `check_near_key`.
* **F2 (Medium), whole typed values.** `_topic_shown(..., to_whole=False)`: a slip that is not whole never matches a whole typed value by rounding to no places when the question states no accuracy ("12" for x = 11 was "the sign of the term that moved" through 35/3). A slip that reaches the typed value only that way still counts as another explanation (it silences a different message), and the quiet check keeps rounding to whole numbers. Tests: `topic_cases` F2 rows and `check_near_key`.
* **F3 (Low), a coarser accuracy.** `_near_key` with a stated accuracy also takes the key at one or two coarser steps as next to the key, so "70" for a distance of 69.8 (to 1 d.p.) gets "Round to the accuracy the question asks for", not "the side lengths added". Test: `topic_cases` F3 rows.
* **F4 (High), rung 2 showing the answer.** `_number_tokens` reads a minus followed by spaces as a sign unless it stands between two plain numbers ("5(x − 2)² − 5" holds −5, "3 − 2" does not hold −2); the list exemption compares the question's numbers with their signs, never applies to roots and never once every item is shown; an `algebraic_fraction` key `17|2` also gives 17/2; a `linear_equation` reads a bare x right of "y =" as gradient ±1; for roots a coefficient (2a, 5x) or a power is not a root value. The ladder smoke's `shows_key` is rewritten as a token reader (no shared regular expressions) and checks 4 draws of every slot, not run 0 only. Tests: ladder review cases F4 and 15 blind-spot rows checked against both scans.
* **F5 (Medium), superscripts.** `plain_line` turns `<sup>`/`<sub>` into Unicode superscripts and subscripts (3³, x²ⁿ, a₁, 10⁻³), else `^x` or `_x`, for rung 1 and rung 2 ("54 = 2 × 3³", not "2 × 33"). Tests: ladder review case F5 and `plain_line` rows.
* **F6 (Medium), trivial rung 2.** `answer_in_effect` ends the search with no rung 2 (the page offers Show answer) when a step that hides the key leaves one trivial move: a fraction key and a count at the end of the step ("count the overlap only: 13 people" in a survey of 63) or "N out of D"; a list of three or more numbers with as many items as a whole-number key (one fewer for five or more) or adding up to it; an inequality ending within one of a whole-number key ("so k < −5"); an algebraic key shown without its coefficient; roots one move away ("x + 6 = ±3"); two points whose midpoint is a pair key. Tests: nine ladder review cases F6 (one is a step that must keep its rung 2) and the slot scan's own `_trivial_step`.
* **F7 (Medium), quadratic simultaneous y box.** `qsim_solve` joins `_NO_SIGN_ONLY_PARTS`: a box typed with only its sign wrong gets a sign line, never "multiplied by the power" (for x = −2, −4 is both 2x and −x²); rules whose message is about signs (`qsim.root_signs`) may still speak. The hand-worked `qsim.y_doubled` row moved to x = 3 (y box 6). Test: `other_cases` F7 row in `scripts/gcse_hints_cd.py`.
* **F8 (Medium), D5 wording.** Four messages no longer give the operation to apply to the pupil's number: `pyth.diagonal_squared_not_halved` "That is the area of the square drawn on the diagonal, not of the square itself.", `num.reciprocal_same` "That is the number itself. The answer times this number should make one.", `af.undefined_not_divided` "Check the last step. Once the number is moved across, the x still has a number multiplying it.", `lin.cost_not_divided` "That is the cost of the miles. The question asks how many miles." (the section 25 table quotes the old line). Appendix A of `docs/ZORP_CHARM.md` regenerated. The two midpoint lines ("Halve it to find the midpoint") and `prob.complement_missed` ("Take it away from one") followed the same pattern and were reworded in fix pass 3 ("Pass 2 leftovers" in `docs/GCSE_MATHS_VERIFICATION.md`). Test: `test_hint_messages` in `scripts/test_zorp_voice_smoke.py`.
* **F9 (Medium), tests.** The hints smoke types values next to the key on every question with a record (`check_near_key`: one either side of a whole key, a key that is not whole rounded or cut to no and to one place; 1,796 values) and fails on any topic message reached by rounding, or on the key written short outside `CUT_SHORT_RULES`. A slot whose only topic firing is next to the key no longer counts for coverage. The ladder smoke as in F4 and F6.
* **F10 (Low).** `NUDGE_DEFAULT` is read by the voice lint (`HINT_CONSTANTS` in `models/zorp_voice.py`); a bearing typed with a decimal part is read as typed for the diagnosis ("8.2" for 082 is no longer 8, "measured from east"); `misconception_cd._deg` takes a value within a millionth of a half as that half, so two equal legs on 062° and 155° (exactly 108.5°) rebuild the key 109 and keep their rules; the coarser key is F3. Not changed: the import order of `misconception_5b` (production imports `misconceptions` first) and the `_ratio_diff_03` box guard (silent, coverage only).

**Coverage** (default seed pair, 1,173 practice slots). Before: topic 716 (61.0%), generic or topic 908 (77.4%), generic 860. After: topic 711 (60.6%), combined 908 (77.4%), generic 860; floors 0.600 and 0.770 unchanged. The five slots no longer counted fire only next to the key (F9): three recurring-decimal slots whose rule is the key written short by nature (`gcse_dec_recurring`, `gcse_fdp_recurring`, `_number_diff_recurring_decimal_fraction`), `gcse_mf_prime_factor_exponents` and `_ratio_found_16`. The module fixes alone moved no slot (the new smoke on the old module also counts 711). Rung 2: 676 of 1,110 run-0 slots (61%, was 692, 62%); over 4 draws per slot 2,698 of 4,439 (60.8%, was 2,767): 71 lost (the F4 and F6 cases and cautious holds such as a coefficient equal to a root), 2 gained (a power or coefficient no longer read as a root).

**Runs.** Hints smoke 17.0 to 17.6 s (was 15.9 s; the 15 s budget note was already printed), ladder smoke 5.5 s (four draws per slot), MCQ notes, voice and answer-check smokes and ruff pass.

## Hint card and Show answer change (2026-11-04, committed in 73163d3)

Supersedes D1 (Show answer unlocked by the last hint rung) and D1d (the pre-attempt Hint drawer stays). Requested by David after screenshots showed the same hint text twice.

- **No pre-attempt hint.** The `practice-hint-drawer` is gone from `templates/index.html` and `pages.css`; the server no longer renders `problem.hint` into the practice page for GCSE maths (it still feeds rung 1 through the check response). Only the practice page answers before showing a hint: question of the day already shows its hint after a wrong answer, Quick Test shows answers on the results page, and saved, shared, suggestion and sandbox pages are view-only, so none changed. Practice pages outside GCSE maths have no ladder, so their `problem.hint` now sits in a `hint-reveal` inside the Show answer drawer instead.
- **Show answer.** For GCSE maths it is always on the page: greyed (`details.answer-reveal[data-locked]`, summary `aria-disabled="true"` and `tabindex="-1"`, a muted note "Opens after your first try", clicks cancelled in `site.js`) until the first attempt (any typed check, right or wrong, or an MCQ pick, or a failed check). The unlock removes the attributes and a polite `.answer-reveal-status` region says "Show answer is now open." No "Open Show answer" button and no locked note. A wrong answer alone now unlocks it.
- **Hint card.** `.hint-card`: bold "Hint" heading, thin divider, text. Rung 1 (the slip message, else the nudge) is in the card; "Show a bigger hint" adds a "Bigger hint" section to the same card. The red feedback line is short ("Not quite.") when the card holds the slip. The MCQ option note uses the same card (`.mcq-hint-slot`, polite). No bigger-hint button when rung 2 is empty or equals rung 1.
- **Colour.** The site's existing hint tokens (`--hint-bg`, `--hint-border`, left bar and heading `--on-streak`): amber against the blue site, no new colour. Contrast: heading on `--hint-bg` 4.84:1 light, 11.0:1 dark; body text 15.1:1 light, 14.5:1 dark.
- **Bytes and pins.** `site.js` 211,633 B (+1,217; cap raised 210,446 to 211,696 in the ladder smoke, ledger line dated 2026-11-04), `practice.css` 32,820 B (+873; cap 31,981 to 32,881). `site.js?v=38`, `practice.css?v=31`, `pages.css?v=58`, `sw.js` `pb-v109`. LADDER_COPY lost `open` and `locked_pick`; `hint` and `bigger` lost their colons.
- **Tests.** Ladder, MCQ and PWA/zorp pins updated; the ladder smoke now pins no drawer, the greyed bar, the card markup and the dedupe rules. Screenshots in `/mnt/user-data/outputs/hint_card/`.

## No bigger hint that repeats the first line (2026-11-07, not committed)

Requested by David after a screenshot: "Calculate 3 × 3^2" showed the Hint "Indices (powers) come before multiplication in BIDMAS." and then the Bigger hint "Indices before multiplication.", the same hint twice.

- **Rule.** `build_ladder` drops rung 2 when `adds_nothing(first line, step)` is true, so the page shows no "Show a bigger hint" button (the page already hides the button when `bigger` is empty). Rung 2 adds nothing when it is the same line, a near copy (squashed text contained in the first line, or 90% alike), or, when the first line is the question's own hint, uses only words, numbers and symbols the hint already has (filler words such as "the", "first", "find", "use" and plural endings ignored; a number, a symbol such as `=` or `→`, or a new idea counts as new).
- **General lines are looser.** A slip message or a topic nudge can offer several facts, so a step that picks the one that applies is kept: "Some pairs of angles are equal, and others add up to 180°." then "The angles add up to 180°." stays. Only a near copy of a general line is dropped. The route passes the slip message to `build_ladder` as `slip_text`.
- **Effect.** 85 of 1,110 typed practice slots (run 0) lose a rung 2 that only repeated the hint, for example the BIDMAS, compound measures ("Cover S in the SDT triangle: Speed = Distance ÷ Time." then "Speed = Distance ÷ Time"), mensuration formula and angle-fact slots. 591 keep a rung 2.
- **Second pass, same day: paraphrases.** David then found "Reverse the machine: undo the last operation first, then undo the first operation." followed by "Work backwards, undoing each step in reverse order.": the same advice in other words, which the word check cannot see. So after the question's own hint, rung 2 must also bring something concrete that the hint lacks (`_concrete`): a number (a value from the question or one worked from it), an operation ("subtract" and "−" count as the same operation; a power or a fraction counts as one), or a letter, term or named point from the question. Labels ("Step 1", "(a)", "CT4") and names of rules ("SOH", "LSF", "SAS") do not count. Reviewed by hand on all 155 slots it newly drops: nearly all restate a formula or fact ("Expected frequency = probability × number of trials" after "Multiply the probability by the number of trials"; the transformation rules; the circle theorem names). A few word-only steps that did add a little are dropped too (which side is opposite in the angle of elevation and depression questions, the elimination step after a hint about method marks); the rewrite stage can give them a concrete step instead. Kept: steps with the question's numbers ("Perimeter = 2(l + w) = 2(12 + 6)"), a new operation ("Subtract \(2w\) from both sides" after "Treat P = 2l + 2w like a normal equation"), named points ("angle B = angle D"). Typed practice slots with a rung 2: 591 before this pass, 447 after (229 dropped as repeats in all).
- **Noticed, not changed:** in two multi-part transformation questions rung 2 describes the single transformation the last part asks for (`_trans_diff_combination_single_equiv`, `_trans_inter_combination_reflect_reflect`; in the second the hint already says it). For the rewrite stage.
- **Tests.** The ladder smoke checks the BIDMAS case, a slip case, seven rule cases, nine concrete-rule cases, and that no slot's rung 2 repeats rung 1; its coverage floor counts dropped repeats (a usable step that only repeated the hint). One hand-made case's hint changed from "Use angles on a line." to "Look for parallel lines." so its step still adds something. `hints_census.py` no longer flags a dropped repeat as `no_bigger`. Server-side only: no `site.js` or cache change.

## Folded wrong-answer note (2026-11-07, not committed)

Requested by David after a screenshot: the "What tripped you up?" panel put five large reason buttons, a text box and two actions under every wrong answer.

- **Folded.** After a wrong answer (signed-in pupils, as before) the page shows one quiet "Add a note ▾" toggle (`.wrong-answer-reflection-toggle`, `aria-expanded`, `aria-controls` on `.wrong-answer-reflection-body`). The reasons, the text box, "Save note" and "Not now" open only when it is clicked. "Not now" folds it again and returns focus to the toggle; saving hides the toggle, says "Thanks, noted." and removes the panel as before. Nothing else changed: same five reasons, a reason with no text still saves at once, same API.
- **Smaller.** The reasons are small outline pills (0.8125rem, 31 px tall on desktop, no 3D edge, no `.btn` classes); phones keep the 44 px tap target from `responsive.css`. The panel uses the body font, a thin border and smaller text; "Save note" lost its 3D edge.
- **Bytes and pins.** `site.js` 212,471 B (+838; cap +800 to 212,496, ledger line dated 2026-11-07 in the ladder and MCQ smokes), `practice.css` 33,756 B (+890; cap +900). `site.js?v=39`, `practice.css?v=32`, `sw.js` `pb-v110` (pins in the ladder, MCQ, PWA, zorp charm and zorp expression smokes; `pb-v111` after the MathJax fix below). Screenshots in `/mnt/user-data/outputs/note_toggle/`.

## Formulas drawn as raised blocks (2026-11-07, not committed)

Reported by David on "The force \(F\) (in newtons) is given by \(F = ma\)": every formula and variable in the question sat above the line on a pale box.

- **Cause.** The diagram rule in `static/css/diagrams.css` (`.question-content svg:not(.svg-kit)`, with `display: block`, a `--diagram-paper` background and a 10 px margin, all `!important`) also matched the SVG that MathJax draws for each formula, and its specificity (0,2,1) beat the `mjx-container ... svg` rules in `pages.css` (0,1,2). So every inline formula in any practice question was a block, raised off the baseline. It dates from August (`2a9c2ab`), not from the hints work.
- **Fix.** The selector is now `.question-content svg:not(.svg-kit):not(mjx-container svg)`; the other diagram selectors only take direct children and never matched MathJax. `diagrams.css?v=27`, `sw.js` `pb-v111`. `test_u8_a11y_smoke.py` pins the exclusion.
- **Checked elsewhere.** A browser scan after the fix: every GCSE maths topic at all three levels, two questions each with Show answer forced open (192 pages, 291 MathJax SVGs), and a crawl of 199 pages from `/topics` (lessons, topic pages, Quick Test, the style guide). No MathJax SVG anywhere is a block, has a background or has a margin.

