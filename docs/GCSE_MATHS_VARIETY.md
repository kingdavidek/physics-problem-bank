# GCSE Maths variety plan: retire duplicate variants, grow the multiple-choice banks

**Goal:** a pupil working through a GCSE maths topic should meet genuinely different questions, not the same question with new numbers. Retire or merge duplicate practice variants without breaking anything stored, fill thin tiers with new kinds of question chosen from the specification gaps, and grow the multiple-choice (MCQ) pools so that bands, practice queues and lesson quizzes stop repeating themselves.
**Status:** planned 2026-10-27 on `1bd6362` plus the large uncommitted, reviewed tree (verification Phases 1 to 4, hints Phases 1 to 5c), which is left intact. **Phases 0 and 1 are built (2026-10-27, section 13) and independently reviewed (section 14); Phase 2 is built (section 15) and independently reviewed (section 16); nothing committed.** Decisions V1 to V9 (section 11) are recorded as chosen (all A, David 2026-10-27). Phase 3 batches A, B, C1 and C2 are built (sections 17, 19, 21 and 23) and A, B and C1 reviewed (sections 18, 20 and 22); decision V8 (the whole-pool draw) landed in batch C2; Phase 4 is not started. One decision is open for David: the question-of-the-day deploy precaution (sections 15.6 and 16.6).
**Pipeline per phase (as for the verification and hints tracks):** implementer builds, an independent reviewer checks against this doc and the code, fixes, sync to David's laptop, full smoke suite green. One commit per phase, only when David asks.

Read first: `docs/GCSE_MATHS_VERIFICATION.md` (sections 2 to 4, 15 and the later notes) and `docs/GCSE_MATHS_HINTS.md` (sections 3, 4, 7, 8, 23 to 25). Every question change in this plan touches both.

---

## 1. Where things stand (measured 2026-10-27)

All figures come from throwaway scripts run against the current tree (16 seeds per practice slot for templates, 8 shared seeds per slot for output identity, 150 MCQ draws per band, 30 seeded lesson quizzes per topic, the real `build_lesson_quiz` and the real verification harness). Section 2 defines every term. Phase 0 turns the scripts into a committed report so these numbers are reproducible.

### 1.1 Headline table

| Measure | Value |
|---|---|
| Practice slots (topic x tier x variant) | 1,072 (1,069 functions), 96 tiers |
| Exact duplicates in the same tier (D1) | **42 slots** in 4 topics: statistics 21, ratio_proportion 10, graphs 9, probability 2 (one-line wrappers that call the same helper), plus 2 in algebra (`algebra_practice_quadratic_2` is `consecutive_integers`, `algebra_practice_quadratic_3` is `expand_mixed`) |
| Siblings in the same tier (D2: same template, same record family) | 20 more slots (algebra linear 1/2/3, bearings compass NE/NW/SE/SW, magnitude 3-4/6-8, Pythagoras yes/no, correlation positive/negative/none and others; Appendix A) |
| Redundant slots in total (D1 + D2, keeping one per group) | **64 of 1,072 (6.0%)**: 1,008 strict kinds |
| Tier echoes (the same helper in two or three tiers) | 65 slots (for example `_prob_two_coins` is foundational, intermediate and difficult) |
| Near-duplicate pairs for review (D3) | 121 pairs in the same tier, 188 across tiers (938 loose kinds) |
| Fixed variants (2 or fewer distinct questions in 16 seeds) | 82 slots (proofs, constructions, fixed-formula rearrangements, and 6 correlation graphs that always give the same answer) |
| Tiers with fewer than 7 slots (the practice queue is 7, so a variant repeats in every queue) | 27 of 96 |
| Tiers with fewer than 7 strict kinds | **28 of 96** |
| 7-question practice queues with a repeated strict kind | mean 38.7% over tiers; **28 tiers repeat in every queue** (algebra foundational has 3 slots, all "solve ax + b = c") |
| MCQ slots / bands | 611 / 96 |
| Distinct MCQ kinds per band | median 6, minimum 3; 12 bands below 5, 51 bands below 7 |
| Bands that draw only from fixed bank items | 40 of 96 (procedural MCQs reach only the difficult band of the 20 bank topics) |
| Topics whose three MCQ bands serve identical kinds | **10**: number, ratio_proportion, changing_the_subject, completing_the_square, quadratic_simultaneous_equations, graphical_simultaneous_equations, algebraic_fractions, functions, statistics, probability |
| MCQ generators already written but unreachable by pupils | **37**: `number_mcq` types 8 to 18 (11), `ratio_proportion_mcq` types 8 and 9 (2), and the pool members past the fourth in `changing_the_subject` (8), `completing_the_square` (4), `graphical_simultaneous_equations` (4), `algebraic_fractions` (4), `functions` (4) |
| Lesson quizzes with two questions of the same kind | **511 of 960 (53.2%)**; mean 8.26 distinct kinds per 10-question quiz; 11 topics at 29 or 30 of 30; only mensuration and constructions_loci at 0 |
| Strict MCQ coverage (every question a slot can serve is re-solved) | 556 of 611 (91.0%); trigonometry 0 of 21, constructions_loci 7, bidmas 14, pythagoras 14, simultaneous_equations 12 of 18 |
| Static bank items | 340: 325 re-solved by digest specs, 15 reviewed exemptions (7 of them trigonometry definitions or method choices) |
| Hints: practice slots with a topic rule | 657 of 1,072 (61.3%), floor `TOPIC_FLOOR_SLOTS = 657` (absolute) |

### 1.2 Practice: duplicates and kinds by topic

Columns are slots / strict kinds / loose kinds per tier (F, I, D). Topics not listed have every slot a distinct strict kind and at least 7 kinds per tier.

| Topic | F | I | D | What is wrong |
|---|---|---|---|---|
| statistics | 15/8/8 | 15/10/10 | 17/8/8 | 21 one-line wrapper copies; difficult serves `_stats_diff_cf_multipart` and `_stats_diff_histogram_multipart` four times each |
| ratio_proportion | 16/16/16 | 19/15/15 | 19/13/13 | 10 wrapper copies (`_ratio_diff_plumbers_job` three times in difficult) |
| graphs | 15/10/9 | 15/12/11 | 17/12/12 | 9 wrapper copies; 6 fixed correlation graphs (positive, negative, none, in two tiers) |
| algebra | 3/1/1 | 8/8/6 | 8/6/6 | foundational is three range variants of one equation; difficult has two exact copies with misleading names; intermediate factorise 1/2/3 differ only by range |
| bidmas | 6/6/2 | 6/6/5 | 6/6/3 | pool of 6 per tier (always repeats in a 7-queue); loose kinds 2 to 5 |
| simultaneous_equations | 5/5/1 | 5/5/4 | 5/5/4 | pool of 5 per tier |
| completing_the_square, quadratic_simultaneous_equations, algebraic_fractions, algebraic_proof | 5 per tier | 5 | 5 | pools of 5 per tier |
| graphical_simultaneous_equations | 5 | 6 | 4 | pools below 7 |
| functions | 7 | 5 | 8 | intermediate pool of 5 |
| fdp, multiples_factors, surds | 3 | 8 to 9 | 7 to 8 | foundational pool of 3 |
| decimals | 6 | 10 | 9 | foundational pool of 6 |
| changing_the_subject | 8/8/2 | 10/10/1 | 10/10/5 | every variant is a fixed formula; the loose measure merges them, which is right for "kind" (make x the subject) but each formula is a different skill step, so no retirement here (section 4) |
| transformations | 15/12/6 | 14/13/11 | 13/13/13 | siblings: reflect in x-axis / y-axis, x = k / y = k, enlarge negative / not at origin |
| bearings | 15/11/11 | 18/18/17 | 18/18/18 | four compass-quadrant siblings and two back-bearing siblings |
| vectors, pythagoras, sequences, probability, equations_inequalities, constructions_loci | small | | | one or two siblings each (Appendix A) |

### 1.3 MCQ: pool depth by topic

Distinct kinds per band (F / I / D), procedural share of draws, and why.

| Topic | Kinds F / I / D | Source | Note |
|---|---|---|---|
| number | 7 / 7 / 7 | procedural only | `mcq_variants_from_fn(slot_param='mcq_type')` binds slot i to type i, so only types 1 to 7 of 18 are reachable, in every band |
| ratio_proportion | 8 / 8 / 8 | procedural only | types 1 to 7 of 9 reachable, same in every band |
| changing_the_subject | 4 / 4 / 4 | procedural only | `mcq_variants_from_pool(..., count=4)`: only the first 4 of 12 pool members reachable |
| algebraic_fractions | 4 / 4 / 4 | procedural only | first 4 of 8 |
| functions | 6 / 6 / 6 | procedural only | first 4 of 8 functions (6 templates) |
| completing_the_square | 9 / 9 / 9 | procedural only | first 4 of 8 functions (9 templates) |
| graphical_simultaneous_equations | 6 / 6 / 6 | procedural only | first 4 of 8 |
| quadratic_simultaneous_equations | 11 / 11 / 11 | procedural only | all 4 reachable; same in every band |
| statistics, probability | 18, 40 per band | procedural only | the band is ignored |
| graphs | 12 / 37 / 34 | procedural | the only direct topic whose bands differ |
| algebraic_proof | 5 / 10 / 15 | procedural | per-band pools (added 2026-10-23) |
| pythagoras, vectors | 3 / 5 / 6 | bank + 2 procedural (difficult only) | thinnest foundational bands |
| simultaneous_equations | 3 / 5 / 5 | bank + 2 procedural | |
| bearings, transformations | 4 / 6 / 8, 4 / 5 / 7 | bank + 2 procedural | |
| trigonometry | 5 / 5 / 7 | bank + 2 procedural | 7 of 15 bank items are definitions or method choices; strict coverage 0 of 21 |
| bidmas | 7 / 6 / 4 | bank + 2 procedural | difficult has 40 stems but only 4 templates |
| the other 12 bank topics | 5 to 12 per band | bank + 2 to 5 procedural | F and I bands are bank only |

### 1.4 Lesson quizzes

`build_lesson_quiz` (`generators/shared/lesson_quiz.py`) rejects a repeat only when the whole question text is identical (`_question_key`). Each draw picks a random slot and each dispatch slot picks a random pool member, so two questions with the same stem and different numbers land in the same quiz whenever a band has few kinds. Worst repeats over 30 seeds: decimals "# × # =" bank items (26 quizzes), multiples_factors "HCF of # and #" (19), surds "√# simplifies to" (22), simultaneous_equations "x + y = #, x - y = #" (16), number "Increase # by #%" and "value of the hundreds digit" (17 each), functions "f(#) when f(x) = #x + #" (25), statistics "midpoint of the class interval" (17).

### 1.5 Other places a pupil meets repeats

- **Quick Test** (`models/quicktest.py`, 10 questions) and **set work** (up to 20) are built from the 7-slot queue, so at least 3 Quick Test questions and up to 13 set-work questions repeat a variant by construction, whatever the pool size.
- **Cross-topic overlap:** `geometry_angles` difficult serves alternate segment, tangent, cyclic quadrilateral and bearing questions that `circle_theorems` and `bearings` own; `algebra` serves change of subject and simultaneous equations that have their own topics. Out of scope for retirement (a pupil picks one topic at a time), but new kinds must not add more overlap.

### 1.6 Where variant names are stored (safety analysis)

Pupils never choose a variant and no page shows a variant name. Names live in:

| Where | What happens if a name disappears | Handling in this plan |
|---|---|---|
| `user_problem_queues.queue_json` / `variant_name` (logged-in) and the session queue (guests) | `_generate_queued_problem` catches `ValueError('Unknown variant')` and rebuilds the queue once | safe; aliases avoid even the rebuild |
| Saved problems (`saved_problems.problem_json['variant_name']`) | the saved copy still displays (the problem is stored whole); `_can_reroll_variant` returns false, so "new numbers" disappears for that save | keep the name resolvable (section 3) |
| Frozen set work (`_freeze_problem_payload`) | the frozen payload is graded as stored; never regenerated | safe |
| Friend challenges (`create_challenge(..., problems)`) | problems stored whole | safe |
| Question of the day (`models/qotd.py`) | **regenerated from the day seed on every call**, from the difficult MCQ band | a deploy that changes difficult MCQ pools changes that day's question mid-day (risk R3) |
| Cohort stats (`compute_problem_key`) | the key includes `variant_name` and the question text, so a renamed variant starts new anonymous counters | acceptable (counters are per question instance anyway) |
| API payloads (`_problem_client_payload`, `variant_name`) | JSON only, not documented in `docs/API.md`, not read by any JS | no teacher or pupil surface |
| Tests (`test_answer_check_smoke.py` calls `_ratio_found_01`, `_prob_found_01`, `algebra_practice_linear_1/2`; `register.ORDER_FREE_PAIRS` keys by `slug/standard/fn`) | a test failure | aliases keep them working; `ORDER_FREE_PAIRS` entries are proofs, none retired |
| Verification and hints enumeration (`harness.enumerate_slots` samples `variants_func`) | a retired slot simply leaves the enumeration, and with it verification | the alias register is verified separately (section 3) |

`pick_named_variant` already falls back to `lookup_variant_by_name`, which finds any module-level generator function by its `__name__`. A function kept at module level but taken out of the pool therefore still serves a stored name. No slot name currently collides across generator modules (checked; 211 helper names do collide, so the fallback must stay guarded by a test).

---

## 2. Definitions and metrics

**Normalised template** `T(q)`: the pupil-visible question text (HTML and SVG removed, LaTeX flattened as `gcse_verify/latex.plain` does), every number (integers, decimals, fractions, money, signs) replaced by `#`, capitalised words outside a short function-word list (names, places) by `@`, one to three capital letters (labels) by `L`, single lower-case letters by `v`, runs collapsed. Two questions with the same template differ only in numbers, names, labels or letters.

**Practice duplicates (per topic):**

- **D1 exact duplicate:** two slots that make the same helper call (detected structurally from the source: a one-line `return helper(args)` with the same call), or that give the same question, solution and key on 8 shared seeds with SVG ids normalised.
- **D2 sibling:** not D1, but the same set of templates over 16 seeds and the same `record()` family with the same input keys. They differ only in a number range or one fixed parameter (quadrant, axis, yes/no).
- **D3 near-duplicate (review list, never automatic):** template overlap (Jaccard) of at least 0.5 with the same answer types, or the same family and answer types with representative templates at least 90% alike.
- **Tier echo:** a D1 pair whose slots are in different tiers.
- **Fixed variant:** at most 2 distinct question texts in 16 seeds.

**Kind:** the classes of slots in one (topic, tier) after merging D1 and D2 (**strict kinds**); after also merging D3 (**loose kinds**, reported only). For MCQ, a bank item's kind is its template; a procedural question's kind is (record family, template). A band's MCQ kinds are enumerated structurally (bank items of the band plus every procedural function or type the band's slots can reach), so the count needs no sampling.

**Variety metrics (printed every run, section 7):**

| Metric | Now | Target | Phase |
|---|---|---|---|
| D1 slots in the same tier | 44 | 0 | 1 |
| D2 slots in the same tier | 20 | 0, or listed in `VARIETY_EXEMPT` with a reason | 1 |
| Tiers with fewer than 7 strict kinds | 28 | 0 | 3 |
| Tiers with fewer than 9 strict kinds (V3 option A) | 42 | 0 | 3 |
| Practice queues with a repeated strict kind (exact, from pool composition) | mean 38.7%, 28 tiers at 100% | 0 tiers above 0% | 3 |
| Tier echoes | 65 slots | at most 1 declared F-I echo per tier, none into difficult | 3 |
| Fixed variants | 82 | at most 60, each with a category (proof, construction, definition, fixed formula) | 3 |
| MCQ kinds per band | median 6, minimum 3 | every band at least 5 (Phase 2), at least 8 (Phase 4) | 2, 4 |
| Topics with identical MCQ kinds in all bands | 10 | 0 | 2 |
| Bank-only MCQ bands | 40 | at most 12 | 4 |
| Lesson quizzes with a repeated kind | 53.2% | 0% for every topic whose bands have at least 3 / 4 / 3 kinds; at most 2% overall | 2 |
| Strict MCQ coverage | 91.0% (trigonometry 0 of 21) | at least 96% (trigonometry at least 18 of 21) | 2, 4 |
| Topic-rule share of practice slots | 61.3% | at least 61% after every phase; at least 60% of new practice slots carry a topic rule | all |
| Verified notes on new procedural MCQ distractors | n/a | at least 60% | 2, 4 |

---

## 3. Retiring and merging safely

**Rule 1: retire from the pool, never delete the name.** A retired variant leaves its tier's pool list in `*_variants()` but its function stays defined at module level, so `pick_named_variant` still resolves every stored queue entry, saved problem and test call (V2 option A). For D1 wrappers the kept function is already identical; for D2 siblings the retired functions keep their exact code (a saved problem rerolled from `_brg_found_compass_SW` still gives an SW question).

**Rule 2: merge siblings into one new slot.** Siblings are replaced in the pool by one new function that draws the parameter (quadrant, axis, yes or no, triple family), records the same family and reuses the same solver, for example `_brg_found_compass_any`, `_trans_found_reflect_axis`, `_py_f_is_right_angled`, `_gra_scatter_correlation_any`, `_vectors_found_magnitude_triple`, `algebra_practice_linear` (one range per tier, not three variants). The new name gets its own `slot_seed`, so drift is confined to it.

**Rule 3: a register of retired names.** New `scripts/gcse_verify/register.py` entry `RETIRED = {'slug/fn': ('replaced_by_fn', reason)}`. The verification smoke (check `retired`) for every entry: the name resolves through the topic's real `func` in its old tier and mode; it is not in any pool; it is defined in exactly one generator module (no fallback collision); 2 seeds generate and pass `engine.verify_problem` (its family solver already exists). A retired name that resolves elsewhere, or a pool that still lists it, fails.

**Rule 4: no tier may drop below 7 slots** by retirement alone. Where retiring would, the phase that retires also adds (or moves) enough kinds (Phase 1 never retires below 7; the small tiers are filled in Phase 3).

**Rule 5: MCQ slot names only grow.** MCQ slot names are positional (`{topic}_mcq_{tier}_{i}`). Phases may change what a slot serves but never lower a topic's slot count, so stored MCQ names keep resolving.

**What is not retired:** changing_the_subject fixed formulas (each is a different rearranging step, the loose measure over-merges them), the 7 proof slots in `ORDER_FREE_PAIRS`, constructions described in words, and any D3 pair the reviewer judges different.

**Stored data, checked per phase:** the alias check above; one browser pass on a saved problem from a retired variant (view, reroll); a logged-in queue saved before the change and continued after it (the DB row from a copy of the pre-phase tree).

---

## 4. What replaces them: gaps against the specification

Priorities against AQA 8300 and Edexcel 1MA1 content (P1: Foundation core, commonly examined; P2: Higher core; P3: useful extension). "Host" is the topic slug that should own the new kind. Absence was checked by name and text search of the generators; Phase 0 confirms each row before work starts.

| Host | Missing kind (practice unless marked MCQ) | Priority | Natural misconception (hint rule or note) |
|---|---|---|---|
| fdp | Add and subtract fractions with different denominators; mixed numbers | P1 | denominators added; whole parts dropped |
| fdp | Multiply and divide fractions and mixed numbers | P1 | divided without flipping; mixed number not converted |
| fdp | One quantity as a fraction or percentage of another | P1 | ratio of the wrong way round |
| fdp | Simple interest (and simple versus compound comparison) | P1 | compound used for simple |
| number | Product rule for counting (outcomes, codes, menus) | P2 | added instead of multiplied |
| number | Reciprocals, and calculator answers in exact form | P1 | reciprocal confused with negative |
| ratio_proportion | y proportional to x², x³, √x, 1/x² (find k, then y or x) | P2 | treated as linear proportion |
| ratio_proportion | Combine a:b and b:c; ratio from a difference ("Ann gets £20 more") | P1/P2 | difference treated as one part |
| algebra | Simplify with index laws (2x³)⁴, x⁵ ÷ x², collect like terms with powers | P1 | indices multiplied when adding |
| algebra | Expand three binomials; factorise ax² + bx + c with a > 1; difference of two squares | P2 | cross term missed; a ignored |
| algebra | Form an expression or equation from words or a shape | P1 | |
| equations_inequalities | Iteration x(n+1) = g(x(n)), and the change of sign to locate a root | P2 | iterated from the wrong start |
| quadratic_simultaneous_equations | Line and circle x² + y² = r² | P2 | one root only |
| graphs | Perpendicular gradient and equation of a perpendicular line | P2 | negative not reciprocal |
| graphs | Equation of a circle centre O and the tangent at a point | P2 | gradient of radius used |
| graphs | Velocity-time graphs: gradient as acceleration, area as distance | P2 | gradient taken as distance |
| graphs | Recognise linear, quadratic, cubic, reciprocal, exponential graphs (MCQ) | P1/P2 | |
| graphs | Graph transformations y = f(x) + a, f(x + a), -f(x), f(-x) | P2 | horizontal shift the wrong way |
| graphs | Exponential growth and decay graphs; estimating the gradient of a curve | P2/P3 | |
| trigonometry | Graphs of sin, cos and tan; solving sin x = k in 0 to 360 | P2 | second solution missed |
| statistics | Two-way tables (complete and read) | P1 | totals double counted |
| statistics | Frequency polygons; stem-and-leaf (median, range); time series | P1 | class end used for midpoint |
| statistics | Mode and median from a frequency table; combined mean and a missing value from a mean | P1 | mean of the means |
| statistics | Sampling, bias and capture-recapture | P1/P2 | proportion set up upside down |
| probability | Sample space diagrams (two dice, spinners) | P1 | 11 outcomes for the sum |
| probability | Frequency trees and probability from a two-way table | P1 | conditional denominator wrong |
| probability | Set notation (A ∩ B, A ∪ B, A') on Venn diagrams | P2 | union read as intersection |
| mensuration | Plans and elevations (MCQ with drawn views) | P1 | front and side swapped |
| bidmas | Negative numbers with indices and division in one line; inverse checks ("which calculation gives...") | P1 | |
| simultaneous_equations | Fractions or decimals as coefficients; forming from a two-item context with a check | P1/P2 | |
| completing_the_square | Show x² - 6x + 11 > 0 for all x; axis of symmetry and sketch | P2 | sign of p flipped |
| algebraic_proof | (2n+1)² - (2n-1)² is a multiple of 8; sum of three consecutive odd numbers; product of two odd numbers is odd | P2 | |
| functions | Inverse of a fraction function f(x) = (x + 3)/(2x - 1); solve fg(x) = k | P2 | inverse taken as reciprocal |
| algebraic_fractions | Equations leading to a quadratic; simplify after factorising both parts | P2 | |
| multiples_factors, surds | Foundational tiers of 3: fill from existing intermediate items that are Foundation level (move, not copy) | P1 | |

**Sizing.** Reaching 7 strict kinds in every tier needs about 61 new kinds (bidmas 3, simultaneous 6, algebra 7, algebraic_fractions 6, completing_the_square 6, functions 2, algebraic_proof 6, quadratic simultaneous 6, decimals 1, fdp 4, graphical simultaneous 6, multiples_factors 4, surds 4); reaching 9 needs about 134. Some of the shortfall in fdp, multiples_factors and surds is met by moving existing items to the right tier. Tier echoes into the difficult tier (statistics, probability, graphs, ratio) are replaced from the gap list where a harder kind fits (for example a frequency tree or set notation in place of `_prob_two_coins` in difficult).

---

## 5. MCQ growth

### 5.1 Unlock what is written (Phase 2)

- `number_mcq` (18 types) and `ratio_proportion_mcq` (9 types): replace the one-type-per-slot binding with a per-band type list (each band's slots draw from its list), so every type is reachable and the bands differ. Each type is assigned to the band(s) its content fits; a type may serve two adjacent bands.
- `mcq_variants_from_pool(..., count=4)` in changing_the_subject, completing_the_square, graphical_simultaneous_equations, algebraic_fractions and functions: per-band pools of the existing functions (as `algebraic_proof` already does), count 7, so every written generator is reachable. Slot names only grow (Rule 5).
- statistics and probability: a band list over the existing generators (the difficulty argument is already passed to `statistics_mcq`).
- Bank topics: let the procedural MCQ functions of `maths_bank_procedural_mcq.py` serve the band their content fits, not only difficult.
- These generators are already verified as functions (procedural sweep, `check_option_units`, the MCQ notes smoke covers `number_mcq(1..18)` and `ratio_proportion_mcq(1..9)`), so Phase 2 mostly widens reach; the verification smoke must enumerate MCQ kinds per band (section 7), because 4 seeds per slot no longer reach every kind of a wider pool.

### 5.2 New procedural MCQs (Phase 4)

Preference (V5 option A): a new MCQ kind is procedural when it has a number or expression to compute, with distractors that are computed slips, each tagged with a note through `_letter_opts_tagged` / `_string_opts_tagged` and a rule value that `gcse_verify/mcq_notes.py` recomputes. Hand-written bank items stay for genuinely conceptual or visual items (a drawn graph shape, a plan and elevation, a locus in words). Targets per band: at least 8 kinds (V4 option A), at most one conceptual kind per band, and procedural kinds in the foundational and intermediate bands of every bank topic.

**Trigonometry computed MCQs (first in Phase 4):**

| Kind | Band | Distractors (tagged where a rule exists) |
|---|---|---|
| Find a side with sin, cos or tan | F | wrong ratio (`trig.wrong_ratio`); multiplied instead of divided for the hypotenuse; radians mode (`trig.radians`) |
| Find an angle with the inverse | F/I | ratio not inverted; wrong ratio; opposite over hypotenuse swapped |
| Exact values in a calculation (2 sin 30 + cos 60) | I | sin 30 taken as √3/2; values added before the coefficient |
| Angle of elevation or depression in context | I | tan inverted (adjacent over opposite); angle from the vertical |
| Sine rule side | D | ratio upside down; angle opposite the wrong side |
| Cosine rule side | D | the 2bc cos A term added; cos A dropped |
| Area ½ab sin C | D | half forgotten; non-included angle used |
| 3D: angle between a diagonal and a base | D | base diagonal not found first |

Seven new kinds across the bands lift trigonometry from 5 / 5 / 7 to at least 8 per band once the definitions are confined (5.3).

### 5.3 Conceptual items and strict coverage (Phase 2)

Strict coverage counts a dispatch slot only when every item it can serve is re-solved, and today every trigonometry slot can serve a definition. Option V6-A: a **concept slot** per band. Slots 1 to 6 of a band draw from the re-solved items and procedural kinds; slot 7 draws from the reviewed exemptions (`register.STATIC_EXEMPT`) and computed items. The definitions stay in the course at one seventh of the draws, and strict coverage becomes at least 6 of 7 slots per affected band: trigonometry at least 18 of 21, constructions_loci at least 18, bidmas, pythagoras and simultaneous_equations at least 18 (15 of 18), overall at least 96%. The verification register gains `CONCEPT_SLOTS` so coverage reports them as their own category, not as failures.

---

## 6. Quiz-level repetition

`lesson_quiz._generate_quiz_problem` gains a kind check for GCSE maths quizzes (V7 option A): a second key, `_quiz_kind(problem)`, the normalised template of section 2 computed from the question text only (no generator change, nothing stored). A draw whose kind is already in the quiz is rejected like a repeated text; after 60 of the 120 attempts the kind check relaxes for that question so a thin band still fills ten questions (the shape assertion in `scripts/gcse_verify/quiz.py` keeps the 3 / 4 / 3 mix). The verification quiz sweep asserts no repeated kind for every topic whose bands have at least 3 / 4 / 3 kinds and prints the overall share. Expected effect on the measured state, before any new content: every topic already has at least 3 / 4 / 3 kinds, so the repetition share should fall from 53.2% to near 0; the residual comes from template merges and is reported.

The same template function is used by the builder and by the metric, so the number in the report is the behaviour pupils get. EURSC lesson-bank quizzes are not touched.

Quick Test and set work (section 1.5) repeat by construction because they cycle a 7-slot queue; V8 decides whether GCSE maths draws them from the whole tier pool instead.

---

## 7. How every new or changed item is verified, hinted and pinned

**Practice variant (new or merged):**

1. One `record(family, **inputs)` line after the inputs are drawn; reuse an existing family where the maths is the same (the merged siblings always do); a new family needs a solver in the right `solvers_*.py` (independence rule: stdlib, sympy, `rounding.py` only) and a `registry.distinct(...)` declaration for any pair of quantities that must differ.
2. Presence guard: every recorded number is in the question or declared `derived=`.
3. The verification smoke must show the slot `verified` on all default seeds and on a `--deep` run; forms and stated accuracy pass.
4. Hints: if a natural slip exists, add a rule to `FAMILY_RULES` (or a Phase 5b/5c parser), a hand-worked `unit_table` row, and a message that passes the `system_hint` lint (`python scripts/test_zorp_voice_smoke.py --write` regenerates Appendix A of `docs/ZORP_CHARM.md`). Rules must differ from what the generic rules already say.
5. `answer_record` at most 256 B; session cookie maximum stays under the current 2,714 B plus 5%.

**Procedural MCQ (new or unlocked):** `record()` plus `@verifies` where the module uses it; the generic MCQ check (one keyed option equals the recomputed value, no equivalent distractor, units and fillers via `options.py`); tagged distractors verified by `gcse_verify/mcq_notes.py`; notes in `generators/shared/mcq_notes.py`, no digit in a note (D5). When a tagged generator's output changes, `DRIFT_PIN` in `test_gcse_maths_hints_mcq_smoke.py` moves only with a written drift explanation.

**Bank item (new or edited):** a digest-keyed spec in `solvers_bank_number.py` / `_algebra.py` / `_geometry.py` that reads the numbers from the question only; the wrong-key negative control; any `why` note becomes a `BANK_WHY` row and a `BANK_PINS` entry (re-reviewed on purpose); a conceptual item goes into `STATIC_EXEMPT` with a reason of 20 characters or more and into a concept slot.

**Variety checks (new, Phase 0):** `scripts/gcse_verify/variety.py` (template, kinds, structural MCQ band enumeration, wrapper detection by AST) used by the verification smoke as check `variety`, reading the problems the smoke already generated (no extra generation for practice). Ratchets in `register.py`: `VARIETY_FLOORS` (minimum strict kinds per tier, minimum MCQ kinds per band, may only rise), `VARIETY_EXEMPT` (accepted D2 pairs with a reason), `RETIRED` (section 3), `CONCEPT_SLOTS` (5.3). Report-only in Phase 0, enforcing from Phase 1.

**Hint floors become shares.** `TOPIC_FLOOR_SLOTS = 657`, `COMBINED_FLOOR_SLOTS = 825` and `HINTS_FLOOR_SLOTS = 775` are absolute counts of practice slots, so retiring 64 slots would fail them although nothing got worse: measured, the topic count falls to 620 but the share rises to 61.5% of 1,008 (generic 741, 73.5%; combined 784, 77.8%; combined today 834). Phase 0 replaces them with share floors (topic at least 61.0%, combined at least 77.0%, generic at least 72.0%) plus the existing per-rule reach check, so a phase can retire slots and the floor still only rises.

---

## 8. Drift expectations

| Change | What moves | What must not move |
|---|---|---|
| Retiring D1 wrappers (Phase 1) | which variants a queue draws; the slot list (1,072 falls to 1,008, plus about 9 merged slots) | every kept slot's output for every seed (seeds are keyed by slot name); every retired name's output when called by name |
| Merging D2 siblings (Phase 1) | only the new merged slots (new names, new seeds) | the retired sibling functions, byte for byte |
| Unlocking MCQ types and pools (Phase 2) | what each MCQ slot serves (`number_mcq_foundational_3` may now serve another type) | the generator functions themselves: `number_mcq(k)` for every k, so `DRIFT_PIN` and the option-unit sweep stay put |
| Quiz kind check (Phase 2) | the composition of seeded quizzes (friend challenges store their problems, so nothing stored changes) | grading, option shuffle, the 3 / 4 / 3 shape |
| Concept slots (Phase 2) | which items slots 1 to 7 serve in affected bands | bank item digests |
| New practice and MCQ kinds (Phases 3 and 4) | additions only | existing slots |
| Tier echo replacement (Phase 3) | the replaced slot leaves the higher tier (its function stays, Rule 1) | the function's output |

Each phase runs the drift comparison against a `git archive` copy of the previous phase (as the verification Phase 4 did: every slot, 3 runs, SVG ids normalised, plus 40 draws per MCQ slot) and lists every differing slot with its reason. Anything unexplained blocks the phase.

---

## 9. Runtime budgets

Measured on this machine: verification smoke about 37 to 38 s alone (practice 20 seeds per slot, 14 for algebra; MCQ 4 per direct slot; 8 per procedural function; quiz slice 2 seeds per topic); hints smoke 16 to 18 s (2 seeds per practice slot plus 12 extra rounds); MCQ notes smoke about 10 s (budget 12 s); the throwaway measurement scripts took about 5 s each.

**Rule: no growth.** At the end of every phase the default verification run stays at or under 38 s alone and the hints smoke at or under 18 s, measured three times and reported. Offsets, in order:

1. Retired slots leave the default run (64 slots, 6.0% of practice generation).
2. Fixed variants (section 2) need 2 seeds, not 20: a slot whose first 4 seeds give one question text drops to 2 seeds in the default run (deep run unchanged). About 82 slots, roughly 1,400 fewer generations.
3. The variety check reuses the smoke's cached problems and enumerates MCQ bands structurally (target cost under 0.5 s).
4. Wider MCQ pools are verified per generator function and type (8 seeds each), not by more seeds per slot.
5. The retired-name check uses 2 seeds per name (about 120 generations).

New practice slots cost about the same as retired ones; with V3 option A (9 kinds per tier, about 134 new slots) the offsets above roughly balance the additions. If a phase cannot meet the budget, it says so with the measured numbers and David decides (as for the 35 s note in the verification plan).

---

## 10. Phases (each shippable on its own)

### Phase 0: measure and ratchet (no pupil-visible change)

- `scripts/gcse_verify/variety.py` and check `variety` in the verification smoke (report-only); a `--variety-report` flag that prints the section 1 tables.
- Hint floors restated as shares (section 7); `register.RETIRED`, `VARIETY_EXEMPT`, `VARIETY_FLOORS` (set to today's values), `CONCEPT_SLOTS` (empty).
- Confirm each gap row of section 4 by search; record the confirmed list in this doc.
- **Done when:** the report reproduces section 1 within sampling noise (practice kinds and MCQ kinds exactly, quiz share within 3 points); no generator output changes (drift run: 0 differences); verification at or under 38.5 s; hints unchanged.

### Phase 1: retire duplicates and merge siblings

- Retire the 44 D1 slots (Appendix A), merge the 20 D2 siblings into about 9 new slots (V1 option A), all under Rules 1 to 5; replace the two misleading algebra names in pools by their real kinds.
- Fixed-variant seed cut (offset 2).
- **Done when:** 0 D1 and 0 unexempted D2 slots in any tier; every retired name passes the `retired` check; no tier lost slots below 7 that it had before; topic-hint share at least 61.0%; drift limited to the merged slots and queue composition; verification at or under 38 s; a saved problem and a stored queue from before the phase still work (browser pass).

### Phase 2: MCQ reach, concept slots and quiz kinds

- Section 5.1 (37 unreachable generators, band lists for the 10 band-blind topics, procedural MCQs in fitting bands), 5.3 (concept slots) and section 6 (quiz kind check).
- **Done when:** every MCQ band has at least 5 kinds; no topic serves identical kinds in all three bands; quiz repetition at most 2% overall and 0% for every eligible topic over the deep sweep (40 seeds per topic); strict MCQ coverage at least 96%, trigonometry at least 18 of 21; verified notes unchanged or higher; `DRIFT_PIN` unchanged; QOTD deploy note followed (R3).

### Phase 3: new practice kinds where tiers are thin

- Fill every tier below the V3 target, smallest pools first (algebra foundational, fdp, multiples_factors and surds foundational, the 5-slot algebra topics), taking kinds from the P1 rows of section 4, then P2; move Foundation-level items into foundational tiers where they already exist; replace tier echoes into difficult tiers.
- V8 (Quick Test and set work drawn from the whole tier pool), if David chooses it, lands here, once pools are deep enough.
- **Done when:** every tier has at least the V3 number of strict kinds; no practice queue repeats a strict kind; at least 60% of new slots carry a topic rule; every new slot verified on a deep run; fixed variants at most 60, each categorised; hints and verification within budget.

### Phase 4: MCQ growth to target

- Section 5.2: trigonometry computed MCQs first, then procedural kinds for the foundational and intermediate bands of bank topics, then the P1 gap kinds that suit MCQ (graph shapes, plans and elevations, two-way tables, sample spaces).
- **Done when:** every band has at least the V4 number of kinds, at most one conceptual kind per band; bank-only bands at most 12; at least 60% of new procedural distractors carry a verified note; all new bank items re-solved or exempt with a reason; MCQ notes smoke within 12 s.

**Not in this plan:** cross-topic overlap clean-up (1.5), the P3 gap rows, and the EURSC quiz builder.

---

## 11. Decisions for David

**Recorded 2026-10-27: David chose A for V1 to V9.** The options are kept below for the record. Each has the recommendation first.

**V1. How aggressive is the dedupe?**
- **A (recommended):** retire exact duplicates (44) and merge parameter siblings (20) now; review near-duplicates (121 pairs) only where a new kind replaces them; replace tier echoes in Phase 3 rather than delete them. Removes every guaranteed repeat without losing a skill.
- B: exact duplicates only (44). Smallest change; siblings keep crowding thin tiers (bearings foundational keeps four compass questions).
- C: also merge every near-duplicate the reviewer agrees with (about 80 to 120 slots). Most variety per slot, but many tiers fall below 7 until Phase 3 lands, so it cannot ship alone.

**V2. What happens to retired names?**
- **A (recommended):** keep the function at module level, out of the pool, listed in `register.RETIRED` and checked each run. Uses the existing fallback; saved problems keep "new numbers"; tests that name variants keep working.
- B: an explicit alias map in `variant_utils` that redirects a retired name to its replacement. Cleaner modules, but a saved SW compass question would reroll as any quadrant.
- C: delete. Queues rebuild themselves, but saved problems lose rerolling and several tests need edits.

**V3. Target distinct strict kinds per practice tier.**
- **A (recommended):** 9. A 7-question queue never repeats a kind and still varies from one queue to the next. About 134 new kinds over Phase 3.
- B: 7. The minimum for no repeat in a queue (about 61 new kinds), but a 7-kind tier serves the same seven every time in a different order.
- C: 12. Closest to exam breadth, roughly 250 new kinds; runtime budget at risk.

**V4. Target MCQ kinds per band.**
- **A (recommended):** at least 5 after Phase 2, at least 8 after Phase 4 (the 7-slot MCQ practice queue then never repeats a kind).
- B: 5 only (enough for the 3 / 4 / 3 quiz with the kind check).
- C: 10 (fewest repeats across sessions; about 300 new kinds).

**V5. Procedural generators or hand-written bank items for new MCQs?**
- **A (recommended):** procedural wherever there is something to compute, with tagged misconception distractors; bank items only for conceptual or visual questions. Verifies itself, varies every draw, carries notes.
- B: hand-written bank items first (faster to write, each reviewed and pinned by digest, but fixed text repeats across sessions).
- C: a fixed split, half and half per band.

**V6. Definitions and method-choice MCQs (15 exempt items, 7 in trigonometry).**
- **A (recommended):** concept slot (one slot of seven per band). Keeps the definitions, lifts strict coverage to about 96%.
- B: remove them from the MCQ pools (strict coverage about 99%, but vocabulary questions disappear).
- C: leave as is and accept trigonometry at 0 of 21 strict.

**V7. Scope of the quiz kind check.**
- **A (recommended):** GCSE maths quizzes only. EURSC quizzes have their own tests and mixed lesson banks.
- B: every MCQ-mode quiz (also GCSE CS and A-level).
- C: no builder change; rely on content growth alone (repetition stays high until Phase 4).

**V8. Quick Test and set work for GCSE maths.**
- **A (recommended):** after Phase 3, draw from the whole tier pool (no repeat up to the pool size) instead of cycling the 7-slot queue. Set-work previews and frozen work are unaffected; only new sets change.
- B: keep the 7-slot queue (10-question Quick Tests always repeat at least 3 variants).

**V9. Variant names and teachers.** Variant names are not shown to teachers or pupils anywhere (only `variant_name` in API JSON and saved-problem JSON).
- **A (recommended):** keep them internal; no copy change.
- B: show a plain "question kind" label in the set-work preview so a teacher can see the spread (new copy, voice lint, a later phase).

---

## 12. Risks

| Risk | Mitigation |
|---|---|
| R1 Hint floors are absolute slot counts, so retiring slots fails the hints smoke although coverage is unchanged | Phase 0 restates them as shares before anything is retired (section 7) |
| R2 A retired name resolves to the wrong function through the global fallback (211 helper names already collide across modules) | `retired` check asserts one defining module per retired name and resolution through the topic's own `func` |
| R3 Question of the day is regenerated from the day seed, so changing the difficult MCQ pools changes that day's question mid-day | deploy Phase 2 and Phase 4 close to UTC midnight, or freeze the day's problem at first build (small change, ask David) |
| R4 Retired slots leave verification and hints enumeration, so a later bug in a retired function that a saved problem still rerolls would go unseen | the `retired` check generates and verifies every retired name each run |
| R5 Unlocked MCQ types land in the wrong band | each band list is reviewed against the specification tier in Phase 2; the reviewer reads every type's stem |
| R6 The template normaliser merges different kinds or splits one kind (names written in lower case, units) | the report prints every merge; `VARIETY_EXEMPT` takes reviewed pairs; the quiz check relaxes after 60 attempts so it never shortens a quiz |
| R7 Runtime creep from new content | section 9 offsets, measured per phase; a phase over budget reports and asks |
| R8 Pin churn (`DRIFT_PIN`, `BANK_PINS`, bank digests) hides an unintended change | pins move only with a written drift list; generator functions unchanged in Phases 1 and 2 except the merged slots |
| R9 Cohort stats keyed by variant name restart for renamed slots | accepted: counters are anonymous and per question instance already |
| R10 New items carry answer forms the checker does not accept (surds, completed square) | the round-trip and forms checks run on every new slot; a new form goes through `answer_checkers.py` with probes, never a bare `sympify` (AI_HANDOFF invariant 1) |
| R11 The large uncommitted tree under this work | each phase commits only when David asks; drift is compared against a `git archive` of the previous phase, not `HEAD` |
| R12 `scripts/update_maths_variants.py` is a legacy rewriter that would cut pools to 3 per tier | do not run it; Phase 0 adds a note at its top or moves it to `scripts/legacy/` |

---

## 13. Build notes: Phases 0 and 1 (2026-10-27)

Built on `1bd6362` plus the reviewed uncommitted tree. **Nothing is committed.** Decisions V1 to V9 are recorded in section 11 (all A). No pupil-visible change except fewer repeats in the practice queues of the topics below; the multiple-choice bands, the lesson-quiz builder and the question of the day did not change.

### 13.1 Phase 0: the variety report and the ratchets

* `scripts/gcse_verify/variety.py` (new, a test helper that may import generators) computes the section 2 metrics from the problems the verification smoke has already generated: D1 exact duplicates (AST wrappers), D2 siblings (same template set and record-family set over the cached seeds), strict kinds (union-find over D1 and D2), the exact queue-repeat share (elementary symmetric polynomials, 1.0 for a pool under 7 slots), echoes, fixed variants, MCQ kinds per band (bank bands enumerated structurally, direct topics sampled from 4 fixed-seed draws per slot, 25 in report mode) and the lesson-quiz repeat rate. It reproduced the plan's baseline (D1 45 counting the vectors proof wrapper, D2 19, echoes 65).
* The verification smoke prints a "Variety" block every run and takes `--variety-report` (the full per-topic tables of section 1.2 and 1.3, the quiz sweep at 30 seeds a topic). The ratchets live in `scripts/gcse_verify/register.py`: `RETIRED` (76 names as built, 74 after the review, each with the slot that replaced it and its tier), `VARIETY_EXEMPT` (one reviewed pair as built, two after the review), `CONCEPT_SLOTS` (empty until Phase 2) and `VARIETY_FLOORS` (strict kinds per practice tier, MCQ kinds per band, a ceiling on the mean queue-repeat share). The smoke fails on any D1 or D2 pair that is neither retired nor exempt, and on any floor that drops. The MCQ floors of the direct topics sit one under the measured value because they are read from 4 draws.
* The three hint coverage floors are shares of the practice slots now (`HINTS_FLOOR_SHARE` 72.0%, `TOPIC_FLOOR_SHARE` 61.0%, `COMBINED_FLOOR_SHARE` 77.0%, plus the unchanged types floor), so retiring slots cannot fail them.
* `scripts/update_maths_variants.py` carries a DO NOT RUN note (R12).

### 13.2 Phase 1: what was retired and merged

Pools only. Every kept slot's function is untouched. A merged slot is a thin dispatcher (`random.choice` over the retired sibling functions, then a call), so it serves exactly the questions its siblings served. Decision V2=A: every retired function stays defined at module level in exactly one module, is out of the pools, and resolves by name through `variant_utils` (saved problems, stored queues, tests that name a variant). The verification smoke generates and verifies every retired name each run (`retired` check, 2 seeds a name by default, 20 with `--deep`, with 4 negative-control mutants) and checks the one-module rule statically.

Totals: **76 names retired (45 exact duplicates, 31 siblings), 14 slots added (13 merged dispatchers, 1 new kind), net 62 fewer practice slots (1,072 to 1,010).** After the review (section 14) the enlargement pair is apart again: 74 names (45 exact duplicates, 29 siblings), 12 merged dispatcher slots, 1,072 to 1,011. The 45 exact duplicates are the plan's 44 plus `_vectors_diff_vector_proof_sim`, a wrapper of the geometry proof that the plan counted under siblings. Two further slots were fixed rather than retired: `algebra_practice_quadratic_2` and `_3` were misnamed (they called the consecutive-integers and mixed-expansion generators, so they were duplicates, not quadratics); they are retired and replaced by a new kind, `algebra_practice_factorise_quadratic` (factorise ax2 + bx + c with a above 1, answer like `(2x - 3)(x + 1)`, `@verifies('alg', task='factorise')`) in the difficult tier. Algebra foundational is now one slot (`algebra_practice_linear`, merging `_linear_1` to `_3`), which is a thin tier until Phase 3.

| Topic | Tier | Slot that stays (or the new merged slot) | Kind | Retired names (still defined, out of the pool) |
|---|---|---|---|---|
| algebra | D | `algebra_practice_consecutive_integers` | duplicate | `algebra_practice_quadratic_2` |
| algebra | D | `algebra_practice_expand_mixed` | duplicate | `algebra_practice_quadratic_3` |
| algebra | F | `algebra_practice_linear` | merged | `algebra_practice_linear_1`, `algebra_practice_linear_2`, `algebra_practice_linear_3` |
| bearings | F | `_brg_found_back_bearing` | merged | `_brg_found_back_gt_180`, `_brg_found_back_lt_180` |
| bearings | F | `_brg_found_compass_any` | merged | `_brg_found_compass_NE`, `_brg_found_compass_NW`, `_brg_found_compass_SE`, `_brg_found_compass_SW` |
| constructions_loci | D | `_cl_d_construct_angle` | merged | `_cl_d13_construct_45`, `_cl_d14_construct_30` |
| equations_inequalities | F | `_eq_found_two_step_any` | merged | `_eq_found_negative_answer`, `_eq_found_two_step` |
| graphs | D | `_gra_diff_01` | duplicate | `_gra_diff_11` |
| graphs | D | `_gra_diff_02` | duplicate | `_gra_diff_16` |
| graphs | D | `_gra_diff_04` | duplicate | `_gra_diff_17` |
| graphs | D | `_gra_diff_06` | duplicate | `_gra_diff_13` |
| graphs | D | `_gra_diff_10` | duplicate | `_gra_diff_15` |
| graphs | F | `_gra_found_02` | duplicate | `_gra_found_13` |
| graphs | F | `_gra_found_04` | duplicate | `_gra_found_14` |
| graphs | F | `_gra_found_08` | duplicate | `_gra_found_15` |
| graphs | F | `_gra_scatter_correlation_any` | merged | `_gra_found_10`, `_gra_found_11`, `_gra_found_12` |
| graphs | I | `_gra_inter_06` | duplicate | `_gra_inter_15` |
| graphs | I | `_gra_scatter_correlation_any` | merged | `_gra_inter_11`, `_gra_inter_12`, `_gra_inter_13` |
| probability | D | `_prob_diff_03` | duplicate | `_prob_diff_17` |
| probability | F | `_prob_found_01` | duplicate | `_prob_found_13` |
| pythagoras | F | `_py_f_is_right_angled` | merged | `_py_f3_is_right_yes`, `_py_f4_is_right_no` |
| ratio_proportion | D | `_ratio_diff_01` | duplicate | `_ratio_diff_05` |
| ratio_proportion | D | `_ratio_diff_02` | duplicate | `_ratio_diff_07` |
| ratio_proportion | D | `_ratio_diff_03` | duplicate | `_ratio_diff_08`, `_ratio_diff_13` |
| ratio_proportion | D | `_ratio_diff_04` | duplicate | `_ratio_diff_12` |
| ratio_proportion | D | `_ratio_diff_10` | duplicate | `_ratio_diff_18` |
| ratio_proportion | I | `_ratio_inter_01` | duplicate | `_ratio_inter_10` |
| ratio_proportion | I | `_ratio_inter_02` | duplicate | `_ratio_inter_11` |
| ratio_proportion | I | `_ratio_inter_03` | duplicate | `_ratio_inter_12` |
| ratio_proportion | I | `_ratio_inter_09` | duplicate | `_ratio_inter_13` |
| sequences | I | `_seq_inter_find_nth_term_any` | merged | `_seq_inter_find_nth_term`, `_seq_inter_nth_term_negative_d` |
| statistics | D | `_stats_diff_03` | duplicate | `_stats_diff_10` |
| statistics | D | `_stats_diff_04` | duplicate | `_stats_diff_12` |
| statistics | D | `_stats_diff_05` | duplicate | `_stats_diff_11`, `_stats_diff_13`, `_stats_diff_16` |
| statistics | D | `_stats_diff_06` | duplicate | `_stats_diff_14` |
| statistics | D | `_stats_diff_09` | duplicate | `_stats_diff_02`, `_stats_diff_15`, `_stats_diff_17` |
| statistics | F | `_stats_found_01` | duplicate | `_stats_found_09` |
| statistics | F | `_stats_found_02` | duplicate | `_stats_found_10` |
| statistics | F | `_stats_found_03` | duplicate | `_stats_found_11` |
| statistics | F | `_stats_found_04` | duplicate | `_stats_found_12` |
| statistics | F | `_stats_found_05` | duplicate | `_stats_found_13` |
| statistics | F | `_stats_found_06` | duplicate | `_stats_found_14` |
| statistics | F | `_stats_found_07` | duplicate | `_stats_found_15` |
| statistics | I | `_stats_inter_02` | duplicate | `_stats_inter_10` |
| statistics | I | `_stats_inter_05` | duplicate | `_stats_inter_12` |
| statistics | I | `_stats_inter_06` | duplicate | `_stats_inter_13` |
| statistics | I | `_stats_inter_07` | duplicate | `_stats_inter_14` |
| statistics | I | `_stats_inter_08` | duplicate | `_stats_inter_15` |
| transformations | F | `_trans_found_reflect_axis` | merged | `_trans_found_reflect_xaxis`, `_trans_found_reflect_yaxis` |
| transformations | F | `_trans_found_reflect_line_k` | merged | `_trans_found_reflect_xk`, `_trans_found_reflect_yk` |
| transformations | I | ~~`_trans_inter_enlarge_general`~~ | un-merged in review (section 14) | none: `_trans_inter_enlarge_neg_sf` and `_trans_inter_enlarge_not_origin` are back in the pool as two slots |
| vectors | D | `_vectors_diff_geometry_proof` | duplicate | `_vectors_diff_vector_proof_sim` |
| vectors | F | `_vectors_found_magnitude_triple` | merged | `_vectors_found_magnitude_3_4`, `_vectors_found_magnitude_6_8` |

Flags for the reviewer:
* **Transformations enlarge merge.** `_trans_inter_enlarge_neg_sf` and `_not_origin` are merged as the plan said, with the note "negative scale factor is a distinct skill, may stay". Reviewer to confirm or split them again (one line each in the pool and in `RETIRED`). **Review: split again** (section 14).
* The transformations pools listed some functions twice (literal duplicate list entries); the pool rewrite kept the lists as they were apart from the merges, so the queue builder still deduplicates them. Worth tidying in Phase 3.
* `algebra_practice_factorise_quadratic` has no topic hint rule (generic hints only). Adding one belongs to a hints phase; hint coverage is held by the share floors.
* The statistics MCQ difficulty-6 and 7 variants and the other MCQ bands are unchanged (252 MCQ slots in the touched topics, 30 seeds each, identical template sets before and after).

### 13.3 Metrics, before and after (default verification run; `--variety-report` for the lesson-quiz line)

| Metric | Before | After |
|---|---|---|
| Practice slots | 1,072 | 1,010 |
| D1 exact duplicates / D2 siblings | 45 / 18 (one more pair, the transformations describe pair, is exempt) | 0 / 0 (1 exempt) |
| Strict kinds | 1,009 | 1,010 |
| Tiers below 7 kinds / below 9 kinds | 28 / 42 | 27 / 42 |
| Mean share of 7-question queues that repeat a kind | 38.7% | 28.1% |
| Tiers that repeat in every queue | 28 | 27 |
| Tier echoes / fixed variants | 65 / 84 | 63 / 79 |
| MCQ kinds per band (median, minimum, below 5, below 7) | 6, 3, 12, 51 | unchanged |
| Lesson quizzes with two questions of one kind (960 built by the sweep) | 53.2% | 53.2% (unchanged, MCQ untouched) |

The strict-kind count before is 1,009 here against 1,008 in section 1.1: the report counts the vectors proof wrapper as a duplicate. The remaining tiers under 7 kinds are Phase 3's work.

### 13.4 Evidence

* **Drift.** Seeded generation of every standard slot (3 runs a slot) on a snapshot of the tree before the change against the new tree, calling each variant function directly with the same seed: all 3,030 outputs of the 1,010 kept slots are byte-identical (SVG counters normalised); the only slots that differ are the 76 retired names (gone from the pools, present as functions) and the 14 added slots. Through `harness.generate` (the topic function, which builds the pool before choosing) the same seed picks different random draws in the 18 touched topics, because the pool length changes what the pool builder consumes; the questions come from the same functions and the pupil path is unseeded, so this is not a content change. Merged dispatchers reference every retired sibling they replace (checked from source, and 120 draws of each give no template outside the siblings' templates).
* **Compatibility.** `scripts/test_gcse_maths_retired_compat_smoke.py` (new): all 76 retired names generate through their topic function, all 76 resume from a stored queue holding them (`_generate_queued_problem`, queue position and length unchanged, no rebuild), 73 reroll (the other three are not randomised, as before), a name unknown everywhere still rebuilds the queue, no retired name is in a pool a queue is built from, and each is defined in exactly one module. The answer-check smoke covers the merged and new algebra slots.
* **Question of the day (R3).** Phase 1 changes practice pools only. The question of the day is the difficult MCQ band (`models/qotd.py`), which did not change: the question, options and key for each of the next 120 days (86 of them GCSE maths) are identical before and after. No deploy-time precaution is needed for this phase.
* **Runtimes** (this machine, run alone): verification smoke 37.7 s (target about 38; the fixed-variant cut now probes 3 seeds instead of 4, and 52 fixed variants run on 2 seeds in the default run, `--deep` keeps all of them; the variety check itself costs 0.8 s and the retired check 0.3 s); hints smoke 16.6 s (target 18; the measured previous tree takes 18.4 to 18.8 s on the same machine today); hint ladder 2.7 s; MCQ notes smoke 2.0 s; correctness 14.0 s; answer check 6.8 s; `--deep --seed 5000` verification 261 s and passes; `ruff check .` clean; full suite 109 of 109 (108 plus the new compatibility smoke).

### 13.5 Deferred

* Section 4's "confirm each gap row by search" (a Phase 0 item) was not done; the Phase 3 planner should do it before choosing new kinds.
* The "browser pass" of Phase 1's done-when (a saved problem and a stored queue opened in the app) was covered at function level by the compatibility smoke, not in a browser.
* Algebra foundational is down to one slot (it was three duplicates of one kind) and the transformations enlarge merge is for the reviewer to confirm; both are listed in 13.2.
* No `VARIETY_FLOORS` for the quiz repeat rate (MCQ untouched in these phases); it joins the ratchets in Phase 2.

---

## 14. Phase 0 and 1 review notes (2026-10-27, independent review, nothing committed)

Reviewed against sections 2, 3, 7, 8, 10 and 13 and the code, as a maths teacher and as a code reviewer. Everything below was fixed in the tree unless it says otherwise.

### 14.1 Findings

| # | Severity | Finding | Outcome |
|---|---|---|---|
| 1 | High | **The fixed-variant cut lost bug-finding power.** "Fixed" was guessed from the first 3 seeds of the run, so any slot whose 3 consecutive seeds happened to agree ran on 2 seeds instead of 20. Measured: 3 such slots at seed offset 0 (`_ap_f_sum_consecutive` has 8 different questions in 20 seeds, `_py_f8_square_diagonal` 5, `_cm_f10_convert_kmh_to_ms` 7), 6 at offset 5000 (`_eq_found_double_inequality` 9) and 7 at offset 77; which slots were hit changed with `--seed`. | Fixed. `register.FIXED_VARIANTS` lists the 49 slots that give one question, solution and key on every one of 220 seeds; only those run on 2 seeds by default. The smoke fails if a listed slot gives two questions or stops being a slot; `--deep` runs every seed and prints any unlisted slot that was fixed throughout (none at seed 9100). `--deep` never cut anything, before or after. |
| 2 | High | **The sibling rule (D2) depended on the seeds.** The deep run at a new offset (`--deep --seed 9100`) failed: `algebra_practice_factorise_1`, `_2` and `_3` ("solve x² + bx + c = 0 by factorising", roots up to 6, 8 and 10) are siblings by section 2, missed on the default seeds and caught on 40. The plan's own 1.2 table had noted them ("differ only by range"). A wider sweep (60 seeds a slot, offset 20000) found no other unlisted group. | Fixed. New `register.VARIETY_DEFERRED`: reviewed siblings that always count as one strict kind whatever the samples show, and are not reported as D2. Merging the three now would take algebra intermediate from 8 slots to 6 (Rule 4), so the merge is Phase 3 work. The honest counts are lower: algebra intermediate 6 strict kinds (floor 8 to 6), 1,009 strict kinds, 28 tiers below 7 kinds, mean queue repeat 29.2% (ceiling 0.286 to 0.293). Pupils' queues did not change. The deep run then passes. |
| 3 | Medium | **Enlargement merge.** As a maths teacher: a negative scale factor is its own skill. It is Higher-only content in AQA 8300 and Edexcel 1MA1 (G7), it has its own misconception (the image drawn on the same side of the centre, not inverted), and fractional scale factors already have their own slot. | Un-merged. `_trans_inter_enlarge_not_origin` and `_trans_inter_enlarge_neg_sf` are back in the intermediate pool at their old positions (the pool is byte-for-byte what it was before Phase 1) and in the mixed list; `_trans_inter_enlarge_general` is deleted (never committed or deployed, so nothing stored can name it); the two `RETIRED` entries are gone and the pair is in `VARIETY_EXEMPT` with the reason. Transformations intermediate floor 13 to 14. |
| 4 | Medium | **Nothing failed when a merged slot stopped drawing a sibling.** The `retired` check proved the sibling still exists, resolves and verifies, but not that its merged slot can still ask it (mutation: SW dropped from `_brg_found_compass_any` passed every test). | Fixed. A merged sibling's slot must name it in its source, or name the helper the sibling's one-line wrapper calls (the correlation slot calls the three graph helpers). New negative-control mutant; the negative controls now match on each mutant's own message (5 of 5), not on "any message". |
| 5 | Medium | **Floors could be lowered quietly.** `VARIETY_FLOORS` only failed when a value fell below its floor, so lowering a floor, or leaving a tier without one, passed. | Fixed. In the default run (offset 0, default sampling) a floor below the measured value, or a tier or band with no floor, fails `variety`; MCQ bands read from fixed-seed draws may sit one under, and the queue-repeat ceiling 0.005 over. All floors were already tight apart from the two changed above. |
| 6 | Medium | **An unknown variant name could crash the global lookup.** `lookup_variant_by_name` imports every module under `generators/` in name order; in a process where the hints modules are not yet loaded, `generators.shared.misconception_5b` starts an import cycle and raises `AttributeError` (not `ImportError`), so an unknown name raised instead of returning None and `_generate_queued_problem` could not fall back. Pre-existing (hints Phase 5b), but it sits on the retired-name path. In the running app the modules are already loaded, so pupils were not affected. | Fixed: the lookup skips `generators.shared` (helpers only; every practice variant lives in a level package; checked over every topic's pools). The compat smoke now checks a fresh process: a retired name resolves and an unknown one returns None (fails on the tree without the fix). The import cycle itself is left for the hints track (importing `misconception_5b` or `misconception_cd` first still fails; `misconceptions` and `misconception_topics` are fine). |
| 7 | Low | `algebra_practice_factorise_quadratic` worked solution printed `\times` outside the maths delimiters (a pupil saw the raw command) and never named the two numbers or showed the split. | Fixed: a × c, the two numbers, the split middle term, the factorising in pairs and the boxed answer, each line checked by SymPy over 500 seeds (the split and the pairs both expand to the question). Question, key, form flag (`factorised`) and grading unchanged: 129 different questions in 400 draws, a > 1 always, both brackets primitive, no difference of two squares; the key, the swapped brackets, `*` between brackets and no spaces are all accepted, the expanded form and a sign-flipped bracket rejected. Generic hints only, as section 13.2 says (a topic rule belongs to a hints phase). |
| 8 | Low | The transformations mixed-tier list held 3 functions after the merge but sampled 4 (`ValueError`). The mixed tier is not reachable from the app (`_GENERATOR_DIFFICULTIES` has three tiers). | Fixed by finding 3 (the list has 4 again); all 32 topics' mixed lists build for 30 seeds. |
| 9 | Low | The compat smoke's "not in a pool" check read one 7-slot queue per tier, so a retired name back in a larger pool could be missed. | Fixed: 25 seeded queue builds per tier. (The verification `retired` check already enumerated pools over 40 seeds.) |
| 10 | Low, not changed | `_trans_inter_enlarge_not_origin` can still choose the centre (0, 0) about 1 time in 12. A correct question, but a misnomer; changing it would move a kept slot's output, so it is left for Phase 3. | Open. |

### 14.2 Duplicate verification (priority 1)

Each of the 45 exact duplicates was called directly against its kept slot with the same seed, 200 seeds each (9,000 pairs): every question, solution, hint, marks and answer dict is identical once the process-wide SVG id counter (`sk-*-N`) is normalised; without that normalisation the only differences are those ids. Every one is a one-line `return helper()` wrapper of the same helper with no arguments, so no difficulty or argument differs and no question kind was lost. The 45 include `_vectors_diff_vector_proof_sim` (same parallelogram-diagonals proof) and the four statistics histogram wrappers found by source.

### 14.3 Merge audit

Twelve merged slots (eleven functions; the correlation slot serves two tiers). Each was called 400 times with its siblings wrapped: every sibling is reached with probability 1/k (bearings compass 4 x about 100, the linear ranges and the correlation graphs 3 x 120 to 150, the rest 2 x 191 to 209), every merged slot sits in its siblings' old tier, and it returns the sibling's own output, so marks and difficulty are unchanged. As a maths teacher I agree with every remaining merge: the compass quadrants, back bearings below and above 180°, 45° and 30° constructions, two-step equations with a positive or negative answer, the three correlation graphs, "is it right-angled?" yes or no (keeping them apart made the answer predictable from the slot), the nth term with d of either sign, reflections in an axis or in x = k / y = k, magnitude triples, and the three linear ranges.

### 14.4 Other claims checked

* **Algebra foundational, one slot (priority 2).** Practice queue (7 x `algebra_practice_linear`, positions 1 to 7 then a new queue, 20 steps), Quick Test standard and MCQ (10 questions each, also through `/api/v1/quicktest/start`, 201), set work (20 frozen questions) and the practice page (200) all work; no crash, loop or empty queue. MCQ bands are bank-based and unchanged. Acceptable until Phase 3: the three slots it replaced were one kind, so pupils lost no variety.
* **Retired names (priority 3).** 74 names: each resolves through its topic function, resumes from a stored queue without a rebuild, 71 reroll (the other three are fixed, as before), none is in a pool, each is defined once (checked from source over all of `generators/`, so the 211 colliding helper names cannot capture one), and each is generated and verified on 2 seeds every run (20 with `--deep`). Set work, challenges and Quick Test store problems whole; no share link stores a variant name; no route or template shows one.
* **Question of the day and drift (priority 6).** Built on the tree before Phase 1 and on this tree for 150 days from 2026-10-27: identical topic, question, options and key every day. Direct calls of every kept slot and every retired name (3 seeds, slot seeds) on both trees: all identical; only the new slots differ (the eleven merged functions and the new algebra kind).
* **Hints (priority 4).** The hints smoke uses fixed seeds and was run three times: identical results apart from the timing line (1,011 slots, generic 742, topic 619, either 785). The 2-slot topic margin cannot flap; it can only be used up by a change, which is what a ratchet is for.

### 14.5 Mutation tests (on a copy of the tree, each restored and compared)

| Mutation | Verification smoke | Compat smoke |
|---|---|---|
| A retired name deleted (`_stats_found_09`) | fails `retired` (defined 0 times; does not generate) | fails (does not generate) |
| A sibling dropped from its merged slot (compass SW) | fails `retired` (merged slot does not draw it) | passes |
| A practice floor lowered below the measured value (bearings F 11 to 10) | fails `variety` | passes |
| An MCQ floor lowered (surds F 5 to 3) | fails `variety` | passes |
| The one-module rule broken (`_stats_found_09` also defined in `transformations.py`) | fails `retired` | fails |
| A retired name back in its pool | fails `variety` (exact duplicate) and `retired` | fails |
| The enlargement exemption removed | fails `variety` (siblings) | passes |

The mutations ran on a copy of the tree; each mutated file was restored and compared byte for byte, and the working tree was never edited by them.

### 14.6 Results after the review (this machine, 2 CPUs, each run alone)

| Run | Result |
|---|---|
| Verification smoke, default | passes; 36.9 to 44.5 s wall over five runs (the machine is noisy today: the tree before Phase 1 took 42.1 s back to back with 41.7 s for this tree), 17,622 practice questions (19,502 before Phase 1), 49 fixed variants on 2 seeds |
| Verification `--deep --seed 9100` | passes, 268 s (failed before finding 2) |
| Hints smoke | passes, 16.5, 17.2, 17.3 and 16.0 s; identical counts |
| Hint ladder / hints MCQ / compat | 2.5 s / 2.0 s / 2.3 s, pass |
| Correctness / answer check | 14.1 s / 6.3 s, pass |
| `ruff check .` | clean |
| Full suite | 109 of 109 (`/tmp/claude-0/suite_v01_review.log`) |

Metrics after the review: 1,011 practice slots, 1,009 strict kinds (2 deferred siblings), D1 0, D2 0 (2 exempt pairs), 28 tiers below 7 kinds, 42 below 9, mean queue repeat 29.2% (28 tiers repeat in every queue), echoes 63, fixed variants 76 by the section 2 measure (49 fixed on every seed); MCQ and lesson quizzes unchanged (`--variety-report`: median 6, minimum 3, 12 bands below 5, 51 below 7, 10 band-blind topics, 53.2% of 960 quizzes).

### 14.7 For the next phases

* Phase 3: merge the three algebra factorise ranges once the intermediate tier has 7 other kinds (drop the `VARIETY_DEFERRED` entries), decide `_trans_inter_enlarge_not_origin`'s (0, 0) centre, and tidy the doubled transformations pool entries (13.2).
* Any new fixed slot (a proof or a construction) can join `FIXED_VARIANTS` after a deep run lists it; until then it simply runs on every seed.
* Before any phase claims a D2 count, run `--deep` at a fresh `--seed`: the sibling rule is a sample, and more seeds find more siblings.

---

## 15. Build notes: Phase 2, MCQ reach, concept slots and quiz kinds (2026-10-27, not committed)

Decisions V1 to V9 all A. Practice is untouched (3,636 seeded outputs compared, 0 practice differences); the MCQ bands, the quiz builder and the verification register changed.

### 15.1 Metrics, before and after (`--variety-report`; the quiz line is 30 seeded quizzes per topic, 960)

| Metric | Before | After |
|---|---|---|
| MCQ kinds per band: median / minimum / bands below 5 / below 7 | 6 / 3 / 12 / 51 | 7 / 5 / 0 / 30 |
| Bank-only MCQ bands (no computed question) | 40 | 3 |
| Topics that serve identical kinds in all three bands | 10 | 0 |
| Strict MCQ coverage (slots whose every question is re-solved) | 556 of 611 (91.0%) | 660 of 668 (98.8%), plus 8 concept slots counted on their own |
| Trigonometry strict MCQ slots | 0 of 21 | 18 of 21 (the other 3 are the concept slot of each band) |
| Lesson quizzes with two questions of one kind | 53.2% (960) | 0.1% (960); 0.2% in `--deep --seed 5000` (1,280) |
| Mean distinct kinds in a ten-question quiz | 8.26 | 10.00 |
| Verification smoke, alone | 37.7 s | 38.0 s |

Bands that still sit at 5 kinds (they cannot rise without Phase 4 content): algebraic_proof F, circle_theorems D, constructions_loci F, equations_inequalities F, pythagoras F, simultaneous_equations F and D, trigonometry F, vectors F. Bands under 7 kinds: 30 (the Phase 4 target).

### 15.2 The 37 unreachable generators, and where each now sits

Each band has its own list (`_X_MCQ_BANDS` in the topic's module); a band cycles its list over its 7 slots. A band list is a placement judgment: read as a teacher, not by position.

* `number_mcq` (types 8 to 18; bands in `_NUMBER_MCQ_BANDS`): F 1 to 6 and 16; I 5, 7, 8, 9, 10, 17, 18; D 11 to 15 and 18. Types 8 (standard form to ordinary number), 9 and 10 (index laws), 17 (ordinary number to standard form) and 18 (compound interest) are Intermediate; 11 (error interval), 12 (product in standard form), 13 (fractional index), 14 (negative index), 15 (percentage error) and 18 are Difficult; 16 (HCF of two numbers; three fixed question forms) is Foundation.
* `ratio_proportion_mcq` (`_RATIO_MCQ_BANDS`): types 8 and 9 now reachable. Three more types were added so a ten-question quiz has enough kinds (see 15.5): 10 fraction of the whole, 11 missing part from a ratio, 12 recipe scaling. F 1, 2, 3, 5, 10, 12, 9; I 4, 6, 11, 8, 5, 9, 3; D 7, 8, 4, 6, 11, 9. Ratio has no harder computed content until Phase 4, so Difficult reuses the upper Intermediate kinds.
* Pool members cut by `count=4` (each module has its own `_X_MCQ_BANDS`): changing_the_subject (4 more: speed, density, inverse, square root), completing_the_square (4 more), graphical_simultaneous_equations (tangent count, parabola point, and others), algebraic_fractions (factorise-and-cancel, difference of squares, solve, subtract), functions (composite and inverse forms), plus quadratic_simultaneous_equations, which had only the first 4 of its pool (kept to its own band lists). Foundation holds the first-step generators, Difficult the ones that need factorising, inverses, tangents or composites.
* Statistics (6 generators were unreachable because the slot index was taken per band) and probability: `_STATISTICS_MCQ_BANDS` and `_PROBABILITY_MCQ_BANDS` index the whole generator list globally.
* Bank topics: the procedural functions that used to be offered only in the Difficult band are now also offered in Foundation and Intermediate where they fit (`procedural_mcq_for(topic, band)` in `maths_bank_procedural_mcq.py`, lists `_FOUNDATIONAL_FNS` and `_INTERMEDIATE_FNS`). Nothing left the Difficult band (the question of the day reads it).
* simultaneous_equations grew from 6 to 7 slots a band (the `count=6` was removed; slot names only grow).

### 15.3 Concept slots

A band that holds reviewed definition or concept items (the 15 `STATIC_EXEMPT` entries, flagged `"concept": True` in the banks) gives them one slot: the last of the band. Every other slot of the band serves computed items only. A band with no concept items, or only concept items, keeps all slots on the whole pool. `register.CONCEPT_SLOTS` lists the 8 slots: bidmas F 7, constructions_loci I and D 7, pythagoras F 7, simultaneous_equations D 7, trigonometry F, I and D 7. The smoke (`check_concepts_and_reach`) checks that the flags equal `STATIC_EXEMPT`, that the concept slot serves only definitions and no other slot serves one, that every generator in `mcq.REACH` is placed in some band, that no band list names a stray one, and that the three bands differ. Strict coverage counts a concept slot as its own category (`concept` column), not strict.

Bank retags made while splitting (content placement, to be reviewed): trigonometry cosine-rule choice and 3D-trig first step moved to Difficult (trig bands now F 4, I 4, D 7 bank items); bidmas `-(2)^2` and `6 + 18 ÷ 3² =` to Difficult; simultaneous_equations "How many solutions do two non-parallel lines have?" to Foundation; vectors `-2a` to Foundation.

### 15.4 Quiz kind check (V7, GCSE maths only)

`generators/shared/question_kind.py` holds the text normaliser (shared by the builder and the variety report, so the report shows what pupils get). `lesson_quiz.build_lesson_quiz` keeps the 3/4/3 shape and the no-repeat-question rule, and for `gcse`/`maths` also refuses a second question of one kind: each draw is rejected for a kind already in the quiz for the first 60 of 120 attempts (`_KIND_CHECK_ATTEMPTS`). If the greedy fill still leaves a repeat (the bands share kinds), the whole quiz is drawn again from the same seeded stream, up to 6 times (`_KIND_CHECK_BUILDS`), so a seed still gives one quiz. Other subjects take the old path. The kind drops rounding instructions ("Give your answer correct to 2 decimal places") and reads f^-1 as an inverse, not a power. Ratchet: `VARIETY_FLOORS['quiz_repeat_max'] = 0.02`, enforced on every run's quiz sweep (64 quizzes by default, 1,280 in `--deep`), with a negative control (3 of 100 repeating must fail).

*Amended in review (section 16.1, findings 1 to 3): the kind also ignores the sign between terms, the builder also refuses a second question from one generator while the band still has another, the redraws share a budget of 400 generator calls and the best build is kept, and the 2% ceiling applies to topics with ten kinds or more (`register.QUIZ_THIN_TOPICS` lists the two that have fewer).*

### 15.5 Bugs found in newly reachable generators (all fixed)

| Generator | Bug |
|---|---|
| `_af_mcq_subtract_same` | with `2x` as denominator an even numerator was unsimplified and p = 3q made two options equal |
| `_af_mcq_diff_squares` | the distractor `x + {r^2}` was a bitwise XOR, not r squared |
| `_fn_mcq_evaluate_quadratic` | printed `f((-2))` |
| `number_mcq(15)` | "12%" beside 1 d.p. options |
| `number_mcq(17)` | "52.0 x 10^-5" |
| `number_mcq(18)` | money options mixed "832" and "865.28" |
| statistics 8, 9, 11 (and 0, 6) | key form showed in the options (".0", mixed precision, float noise such as 7.199999999999999); `_match_number_form` fixes the form of every option |

Algebraic fractions (11 generators) and ratio (12 types) were the only topics with fewer than 10 distinct kinds across the three bands, so a ten-question quiz could not avoid a repeat; each got new MCQ generators (`_af_mcq_unlike_add`, `_af_mcq_common_factor_cancel`, `_af_mcq_solve_over_number`; ratio types 10 to 12), all verified by the existing `alg`, `ratio_part_fraction`, `ratio_find_missing` and `prop_scale` solvers. Stress at 400 seeds each: no failures.

### 15.6 Question of the day (R3)

`models/qotd.py` draws from the difficult MCQ band. Direct topics, bands with a concept slot, and the bidmas retags change the Difficult band; the Difficult band of every other bank topic is byte-identical. Over the next 150 days (105 GCSE maths) the topic chosen each day is unchanged, but the question differs on 37 of the 105 GCSE maths days (changing_the_subject 5, simultaneous_equations 5, bidmas 4, statistics 4, algebraic_fractions 4, probability 3, trigonometry 2, ratio_proportion 2, functions 2, graphical_simultaneous_equations 2, quadratic_simultaneous_equations 2, number 1, constructions_loci 1). The day seed makes the question a pure function of the date, so a deploy changes the current day's question for anyone who opens it before and after. No code change; deploy close to 00:00 UTC, or decide whether to freeze the day's question (a decision for David, not made here).

### 15.7 Pins and ratchets changed

* `VARIETY_FLOORS['mcq_kinds']`: all 96 bands re-set to the measured kinds (sampled bands one under); `probability/difficult` is 15 (it was 22 under the old list; the band was re-cut to its own five generators: 18 kinds in the report, 16 in the default run). 58 floors rose. Six fell, each for a reason that is not lost content: probability D 22 to 15 (above), ratio_proportion D 7 to 5 and I 7 to 6 and quadratic_simultaneous_equations F 6 to 4 (the bands now hold only the generators that fit them, where before every band served the same first generators), number I 6 to 5 (one slot's variants moved), decimals D 10 to 9 (the new kind drops rounding instructions, which merges two decimals kinds that differed only by the clause). A ratchet that fell is listed here so the next phase can see it.
*Review (section 16.3): the decimals D fall was not a merge of two kinds but the rounding rule erasing every "Round ... to n decimal places" question; it is back to 10.*
* `VARIETY_FLOORS['quiz_repeat_max']` 0.02 (new). `queue_repeat_mean_max` unchanged (practice untouched).
* `DRIFT_PIN` in `scripts/test_gcse_maths_hints_mcq_smoke.py` moved from `b9506240b2b852da` to `7f9c174ebfed69c0`: only `number_mcq` 15, 17 and 18 changed among the tagged generators (45 compared by label). `BANK_PINS` unchanged (the bank rows and notes did not change; the `concept` flag is an extra key outside the digest). The notes smoke's endpoint check now also accepts any reviewed misconception message for a question whose option carries a generator tag.
* `mcq.REACH` ratio types 9 to 12; `CONCEPT_SLOTS` 8 entries.

### 15.8 Evidence

Drift (pb before against after, 1,235 MCQ and practice slots, 3 seeded runs each, SVG counters normalised): 0 practice outputs differ; 377 of 611 MCQ slots differ in at least one run (expected: the bands were re-cut). Statistics and probability, plus 15 bank topics, show the change; algebraic_proof and graphs MCQ are untouched. `--deep --seed 5000` verification passes (1,280 quizzes, 0.2% repeat). Verification smoke 38.0 s alone (target 37 to 44 s), hints smoke 15.5 s, ladder 3.3 s, notes 2.8 s.

### 15.9 Deferred

* Bands at 5 kinds need Phase 4 content (list in 15.1).
* Left alone (shared practice generators or judgment): statistics 12 "(larger IQR)" distractor, statistics 10's repeated plus-or-minus 2 pattern, the probability 6 and statistics 4 fallback distractors, `number_mcq(8)` silly "1.6" distractor, `number_mcq(16)` has 3 fixed question forms, the trigonometry find-side stem "Opposite = (tan 30°)", and bank difficulty tags are generally uncalibrated.
* The retags in 15.3 are placement judgments for a maths teacher to confirm.

---

## 16. Phase 2 review notes (2026-10-27, independent review, nothing committed)

Reviewed against sections 5, 6, 10 and 15 and the code, as a GCSE maths teacher and as a code reviewer. Every band's slots were read over 25 to 60 seeds each; the source of every quiz question was traced (the generator function behind it, read with a profiler, not the text). Everything below was fixed in the tree unless it says otherwise.

### 16.1 Findings

| # | Severity | Finding | Outcome |
|---|---|---|---|
| 1 | High | **The quiz kind split one kind into many, so repeats went through.** The template keeps the sign between terms and every context word, so "If f(x) = 5x - 3, what is f(2)?" and "If f(x) = 6x + 7 ..." were two kinds, and so were "the mean number of pets" and "the mean number of books". Traced by generator over 320 seeded quizzes: 24.1% of quizzes asked two questions from one generator (statistics and probability 10 of 10, algebraic fractions 8 of 10, sequences, ratio), while the builder's own measure said 0.3%. It also hid that functions (seven kinds once f(g(4)) and g(f(4)) are one) and quadratic simultaneous equations (four generators) cannot fill ten questions without a repeat. | Fixed. `quiz_kind` ignores the sign between terms. Each MCQ slot helper in `variant_utils` records the generator it drew from (`mcq_source()`, a context variable; no random number is drawn, so no output moves) and the GCSE maths builder also refuses a second question from one generator for the first 30 attempts, while the band can still draw another (`_SOURCE_CHECK_ATTEMPTS`). The ceiling `quiz_repeat_max` applies to topics with ten kinds or more; `register.QUIZ_THIN_TOPICS` (functions, quadratic simultaneous equations, each with its reason) are counted apart and must keep repeating (a stale entry fails). The report prints the share of quizzes with two questions from one generator. Same-generator repeats 24.1% to 16.2% (320 quizzes; the rest are the five topics with eight generators or fewer); repeated kinds in the other 30 topics 1 of 360 (0.3%). |
| 2 | Medium | **The kind merged different questions.** The rounding-instruction rule erased the whole of "Round 24.211 to 1 decimal place." and "Round 8228 to 2 significant figures.", so both had the empty template (one kind, and a quiz could ask only one of them); this, not "two decimals kinds that differed only by the clause", is why the decimals D floor fell. Also: HCF and LCM were one kind (three capitals read as a label), a fractional and a negative index were one kind ("Evaluate #^#"), and the f^-1 rule turned 8^-1 into an inverse. | Fixed in `question_kind.template`: the instruction clause is dropped only when words remain; HCF and LCM are kept; a negative index is marked (`^neg`); only f, g, h, sin, cos and tan take the inverse reading. Practice is unaffected (1,009 strict kinds, every tier floor identical). MCQ floors raised to the measured kinds: decimals D 9 to 10 (restored), decimals F 7 to 8, multiples_factors I and D 11 to 12. |
| 3 | Medium | **Worst-case cost.** A topic that cannot avoid a repeat rebuilt the quiz six times at up to 61 generator calls a question (3,660 calls; graphical simultaneous equations takes about 15 ms a call, so close to a minute), and returned the last build, not the best. | Fixed: the redraws share a budget of 400 generator calls (`_KIND_CHECK_BUDGET`, a count, so a seed still gives one quiz) and the build with the fewest repeated kinds is kept. A synthetic topic with one kind fills ten questions in 550 calls; a broken generator still raises as before. |
| 4 | Medium | **Pie-chart MCQ gave the answer away.** `statistics_mcq` matched "fx" inside the pie chart's SVG and took the frequency-table branch, so the key "45.0°" stood beside the fillers "10", "14" and "12" (the only option with a degree sign). Reachable before Phase 2; now served in F and I. | Fixed: the branch reads the visible text, and the distractors are the other sector, the percentage taken as the angle, the frequency taken as the angle, and half the angle, all to 1 d.p. with a degree sign. The practice question is untouched. |
| 5 | Medium | **`_mf_proc_prime_factors`, now in F and I:** about 1 draw in 5 was a prime ("Write 139 as a product of prime factors", options 140 and 140^2), and for a product of distinct primes the "powers left out" distractor equalled the key, so fillers such as "4^2 × 13^2" appeared. | Fixed: a prime moves to the next composite; distractors are the powers raised, the powers left out, a composite factor left in the tree, 1 taken as a prime, and the number itself (400 seeds: four different options every time). |
| 6 | Medium | **`_dec_proc_round`, now in F:** 1 draw in 10 had two decimal places, so "Round 45.74 to 2 decimal places" was its own answer. | Fixed: the third decimal is never 0. |
| 7 | Medium | **`_trig_proc_find_side`, now in F and I:** at 45° the side itself was both key and distractor (fillers 11 and 12 stood in), and the options mixed "10" with "5.0" under "to 1 d.p.". | Fixed: every option to 1 d.p.; at 45° the slips are sin 45° × side and side ÷ sin 45° (both `trig.wrong_ratio`, verified by `mcq_notes.py`: notes 460 to 466 of 675). `DRIFT_PIN` moved to `5e5176eeffc25658`; a per-generator hash against the tree before Phase 2 shows only this generator and `number_mcq` 15, 17, 18 differ. |
| 8 | Medium | **The loosened notes check could not catch its bug.** "body ignored" accepted any reviewed text, and an endpoint that honoured the request's `option_notes` returns a reviewed text too. | Fixed: the answer must equal `option_notes.picked_note(stored problem, 'A')` exactly, and the request names a note that option A does not carry. Mutation: an endpoint that reads the body fails it. |
| 9 | Low, not changed | Fillers in Difficult bands that are short of harder content: ratio type 6 (a percentage increase) and type 4 (map scale), changing the subject v = d/t and ρ = m/V, algebraic fractions (5x + 35)/(x + 7), functions "solve f(x) = k", graphical simultaneous equations "two parallel lines". Probability F's coins generator sometimes asks "5 coins, exactly 4 heads", which is beyond Foundation (as before Phase 2). | Phase 4 (listed in 16.2). Removing them now would drop those bands under 5 kinds. |
| 11 | Low, not changed | With the sign-blind kind, algebraic_fractions repeats a kind in about 7 of 40 deep quizzes (also ratio_proportion and completing_the_square once in 40): the intermediate band serves four of the difficult band's six kinds (factorising first, difference of two squares, unlike denominators, dividing), so after a greedy fill the difficult band can be left with kinds already asked, and the redraw budget runs out. Overall 0.7% of the 1,200 eligible deep quizzes, under the 2% ceiling, but not the plan's "0% for every eligible topic". | Phase 3 or 4: a further difficult kind (the section 4 row "equations leading to a quadratic") or an intermediate list without the factorising kinds (the band comment already says they are the top). |
| 10 | Low, not changed | Weak distractors that were reachable before Phase 2 and are already in 15.9: the probability complement and relative frequency fallbacks (0, 0.5, 1), "15/15" in the bag questions, a mean "to 1 d.p." keyed "10". The vectors bank's solution text has em dashes (bank rows predate this plan). | Open; a hints or content pass. |

### 16.2 Band placement (as a teacher, every band list read)

* **number:** agree. F place value, rounding (d.p. and s.f.), percentage of an amount, percentage change, HCF; I percentage change, standard form both ways, index laws, compound interest; D error interval, standard form product, fractional and negative indices, percentage error, compound interest.
* **ratio_proportion:** F and I agree. D is thin: inverse proportion and three-part sharing are the only harder kinds; types 4, 6, 9 and 11 are fillers until Phase 4.
* **changing_the_subject, completing_the_square, algebraic_fractions, functions, graphical and quadratic simultaneous equations:** agree with the order (first steps, then the middle, then factorising, inverses, composites and tangents). These topics are Higher content as a whole, so their F band is the easiest part of a Higher topic, not Foundation content. Fillers in D as in finding 9. Functions and quadratic simultaneous equations are thin (finding 1).
* **statistics:** agree (F averages, bar chart, pie chart, scatter; I class midpoint, frequency-table and grouped means, comparing distributions; D box plot, histogram, grouped mean). **probability:** agree, with the coins caveat in finding 9.
* **Bank topics' procedural generators in F and I:** agree with every placement. Higher-only content in F appears only inside Higher topics (circle theorems, surds, similarity area factor is in I only); trigonometry "find a side" in F is Foundation content (SOHCAHTOA).
* **Retags confirmed:** trigonometry "two sides and the included angle: which rule?" and "3D: the best first step" are Higher-only (cosine rule, 3D trigonometry), so Difficult is right; BIDMAS -(2)² and 6 + 18 ÷ 3² are the hardest order-of-operations items of a Foundation topic, so Difficult is right; "two non-parallel lines have how many solutions" and -2a are Foundation knowledge.

### 16.3 Floor audit (the six floors that fell)

| Band | Was / now | Verdict |
|---|---|---|
| probability D | 22 / 15 | Justified: the band left one die, one bag and the complement (Foundation) and gained independent events; five generators, 18 kinds in the report, 16 in the default sample. |
| ratio_proportion D | 7 / 5 | Justified: six types (7, 8, 4, 6, 11, 9), six kinds, the floor one under as for every sampled band. Before, D served types 1 to 7, four of them Foundation. |
| ratio_proportion I | 7 / 6 | Justified: seven types, seven kinds, floor one under. |
| quadratic_simultaneous_equations F | 6 / 4 | Justified: three generators (finding the point moved to I and D); the topic is thin (finding 1). |
| number I | 6 / 5 | Justified: seven types; 7 and 17 share "Write # in standard form", which is one kind; six kinds, floor one under. |
| decimals D | 10 / 9 | **Not justified:** the rounding rule erased the rounding questions (finding 2). Restored to 10. |

### 16.4 Quiz kind audit

* **Definition:** text template, sign-blind, plus the generator for the first 30 attempts (finding 1). Merges that remain are of the same kind (reflect in the x-axis or the y-axis, f(g(4)) or g(f(4)), the same bank stem with other numbers); one doubtful merge is left: the similar-triangles items "Find EC" and "Find DE" in similarity_congruence share a template.
* **Determinism:** 32 topics x 2 seeds built twice with the same seed give identical quizzes (SVG ids aside).
* **Termination and cost:** see finding 3. Quiz sweep in the smoke 3.0 s to 3.6 s (64 quizzes); graphs quizzes now take 30 to 90 generator calls (the sign-blind kind refuses more of its linear-graph items).
* **V7:** 124 non-GCSE-maths quizzes (every other level and subject, 2 seeds each) are identical before Phase 2 and now.

### 16.5 Concept slots and coverage

All 15 `STATIC_EXEMPT` items are reachable, each in exactly one concept slot (bidmas F; pythagoras F; trigonometry F 1, I 2, D 4; simultaneous_equations D; constructions_loci I 3, D 2). Strict coverage is honest: a slot is strict only when every entry it can draw is a procedural generator or a bank item re-solved by its digest spec; concept slots are counted in their own column and never as strict. 660 of 668 (98.8%), trigonometry 18 of 21.

### 16.6 Question of the day

Confirmed on 150 days from 2026-10-27 (105 GCSE maths days): the topic is the same every day, the question differs on 37 days (the same breakdown as 15.6), and no day outside GCSE maths changes. The review's generator fixes change none of the 150 days (SVG ids normalised). **Decision for David:** deploy close to 00:00 UTC, or freeze the day's question at first build.

### 16.7 Drift

Every slot through its topic function, 3 seeded runs (5,037 outputs, SVG ids normalised): practice 0 differences against the tree before Phase 2 and 0 against Phase 2 as built. MCQ against Phase 2 as built: 19 outputs differ, all from the review's fixes (trigonometry find a side, statistics pie chart, multiples_factors prime factors). Bands Phase 2 left unchanged: graphs, algebraic_proof and the Difficult bands of the bank topics without a retag or a concept slot.

### 16.8 Mutation tests (each on a copy of the tree; the working tree's checksums were compared afterwards: unchanged)

| Mutation | Fails |
|---|---|
| Algebraic fractions: an unsimplified form of the key as a distractor (two correct options) | verification `mcq_key` (options equivalent; recomputed value matches two options) |
| Quiz kind check switched off | `variety` (43 of 60 quizzes repeat a kind, above 2%) |
| A trigonometry definition loses its concept flag | `register` (exempt but not flagged; served by six non-concept slots) |
| The concept slot moved to slot 1 | `register` (concept slot must be last) |
| A bank band's MCQ floor lowered (surds I 10 to 9) | `variety` |
| A sampled band's floor two under (ratio D 5 to 4) | `variety` |
| A number type in no band (16) | `register` (unreachable generator) |
| A topic with ten kinds listed in `QUIZ_THIN_TOPICS` | `variety` (stale entry) |
| The notes endpoint honours the request body | hints MCQ smoke `endpoint / body ignored` |

### 16.9 Results after the review (this machine, each run alone)

| Run | Result |
|---|---|
| Verification smoke, default | passes; 38.4, 40.3 and 38.0 s wall alone (Phase 2 as built: 38.0 s); the quiz sweep alone 3.0 s as built, 3.6 s now (the same-generator check and the sign-blind kind refuse more draws, mostly graphs) |
| Verification `--deep --seed 8200` | passes, 270 s; 1,280 quizzes: 0.7% of the 1,200 in topics with ten kinds or more repeat a kind, 80 of 80 in the thin topics, 20.2% ask two questions from one generator |
| Hints smoke / ladder / MCQ notes | 15.3 s (14.2 s internal, budget 15) / 2.8 s / 1.8 s, pass (notes 466 of 675) |
| Retired compat / MCQ letter (6,552 problems) | 2.4 s / 2.5 s, pass |
| Correctness / answer check | 14.8 s / 6.4 s, pass |
| `ruff check .` | clean |
| Full suite | 109 of 109 (`/tmp/claude-0/suite_v2_review.log`) |

Metrics after the review (default run): MCQ kinds per band median 7, minimum 5, none below 5, 32 below 7 in the default run's 4-draw sample (15.1's 30 is the 25-draw `--variety-report`; the template fixes of finding 2 raise decimals F and D, multiples_factors I and D and number F by one kind and lower no band); strict MCQ coverage 660 of 668 (98.8%) plus 8 concept slots; practice unchanged (1,011 slots, 1,009 strict kinds).

---

## 17. Build notes: Phase 3 batch A, thin practice tiers (2026-10-27, not committed)

Batch A brings the practice tiers of algebra, fdp, multiples_factors, surds, decimals and bidmas to at least 9 strict kinds (F, I and D each), adds the section 4 P1 rows to number and ratio_proportion, moves the Foundation-level items out of the intermediate tiers, and merges the three algebra factorise ranges. Nothing was committed. Every new slot has one new generator in `generators/gcse/maths_variety_a.py` (one module, so the drift test sees them as new names), a worked solution, a hint, a `record()` or `@verifies` with an independent solver in `scripts/gcse_verify/solvers_number.py` or `solvers_algebra.py`, and the right answer type (number, fraction, number_pair, number_list, number_fields, linear, algebraic, surd, surd_binomial or choice).

### 17.1 New slots, with one example question each (56 slots; the example is the first seed of the verification harness)

F, I and D are the tier letters. A star marks a slot with a topic hint rule (38 of the 56).


**algebra** (13 new)

| Tier | Slot | Example question |
|---|---|---|
| F | `algebra_practice_collect_terms` | Simplify 2x + 3x - x^2 + 4x^2 |
| F | `algebra_practice_expand_single` | Expand x(4x + 7) |
| F | `algebra_practice_form_equation_shape` * | A rectangle has length (x + 7) cm and width 3 cm. Its perimeter is 40 cm. Form an equation and solve it to find x. |
| F | `algebra_practice_form_expression` * | A rectangle has width w cm and length 6 cm more than its width. Write an expression for the perimeter. |
| F | `algebra_practice_index_laws_simplify` | Simplify x^7 ÷ x^5 |
| I | `algebra_practice_difference_two_squares` | Factorise x^2 - 9 |
| I | `algebra_practice_expand_two_brackets` | Expand and simplify 3(x + 4) - 2(x - 2) |
| I | `algebra_practice_factorise_simple` | Factorise x^2 - 5 x + 4 |
| I | `algebra_practice_form_equation_angles` * | Angles on a straight line are (x + 8)°, (x − 23)° and 3x°. Form an equation and solve it to find x. |
| I | `algebra_practice_index_laws_coefficients` | Simplify (6x^6) ÷ (2x^2) |
| I | `algebra_practice_solve_fraction_equation` * | Solve (3x + 1)/2 = 17 |
| D | `algebra_practice_expand_three_binomials` | Expand and simplify (x + 3)(x + 1)(x - 1) |
| D | `algebra_practice_form_quadratic_area` * | A rectangle has length (x + 4) cm and width (x − 2) cm. Its area is 112 cm². Form an equation and solve it to find x. |

**fdp** (8 new)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_fdp_add_subtract_fractions` * | Work out (1)/(3) + (1)/(6) . Give your answer as a fraction in its simplest form. |
| F | `gcse_fdp_fraction_of_another` * | Write 12 as a fraction of 15. Give your fraction in its simplest form. |
| F | `gcse_fdp_percentage_of_another` * | Write 73 as a percentage of 50. |
| I | `gcse_fdp_mixed_add_subtract` * | Work out 2 1/5 + 4 3/4 . Give your answer as a mixed number in its simplest form. |
| I | `gcse_fdp_mixed_multiply_divide` * | Work out 3 2/5 × 1 1/4 . Give your answer as a mixed number in its simplest form. |
| I | `gcse_fdp_multiply_divide_fractions` * | Work out (3)/(4) × (2)/(3) . Give your answer as a fraction in its simplest form. |
| I | `gcse_fdp_simple_interest` * | Priya invests £200 at 2% simple interest per year. How much is in the account after 2 years? |
| D | `gcse_fdp_simple_vs_compound` * | £5000 is invested for 3 years at 4% per year. How much more interest is earned with compound than with simple interest? |

**multiples_factors** (9 new)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_mf_count_factors` * | How many factors does 36 have? |
| F | `gcse_mf_list_factors` | List all the factors of 48, in order, smallest first. |
| F | `gcse_mf_next_multiple` * | What is the smallest multiple of 11 that is greater than 39? |
| I | `gcse_mf_hcf_simplify_fraction` * | Find the highest common factor of 48 and 88. Use it to write 48/88 in its simplest form. |
| I | `gcse_mf_lcm_laps` * | Anil takes 12 minutes to run one lap and Beth takes 18 minutes. They start together. When they are next together at the start line, how many laps has each run? |
| I | `gcse_mf_multiples_count` * | How many multiples of 12 are there between 67 and 200? |
| I | `gcse_mf_prime_factor_exponents` * | 75 can be written as 3^a × 5^b, where a and b are whole numbers. Find a and b. |
| D | `gcse_mf_factor_count_from_primes` * | N = 2^2 × 3^2 × 7. How many factors does N have? |
| D | `gcse_mf_square_multiplier` * | Find the smallest positive whole number k so that 45k is a square number. |

**surds** (8 new)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_surds_add_like` | Simplify 8√7 + 3√7. |
| F | `gcse_surds_identify_irrational` | Which of these numbers is irrational? (multiple choice) |
| F | `gcse_surds_square_of_surd` * | Work out (4√11)². |
| I | `gcse_surds_expand_single_bracket` | Expand and simplify √5(√5 − 6). |
| I | `gcse_surds_match_simplified` | Which of these is equal to √54? (multiple choice) |
| I | `gcse_surds_multiply_coefficients` | Simplify 5√6 × 5√3. Give your answer in the form a√b, where b has no square factors. |
| I | `gcse_surds_rationalise_coefficient` | Rationalise the denominator of 24/(4√6). Give your answer in its simplest form. |
| D | `gcse_surds_pythagoras_exact` | A right-angled triangle has shorter sides of length √18 cm and √10 cm. Find the exact length of the hypotenuse. Give your answer in the form k√r, wher |

**decimals** (4 new)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_dec_subtract_from_whole` * | Work out 7 − 6.4. |
| I | `gcse_dec_known_product` * | Use the fact that 43 × 31 = 1333 to work out 0.43 × 0.31. |
| D | `gcse_dec_known_division` * | Use the fact that 21 × 27 = 567 to work out 56.7 ÷ 21. |
| D | `gcse_dec_rounding_error` * | x = 5.6938. x is rounded to 1 decimal place. Work out the difference between the rounded value and x. |

**bidmas** (9 new)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_bidmas_inverse_check` | Which calculation can be used to check that 59 + 48 = 107? (multiple choice) |
| I | `gcse_bidmas_fraction_bar` * | Calculate (22 + 2 × 3)/(5 − 1) |
| I | `gcse_bidmas_missing_number` * | Find the positive whole number that goes in the box. 2 × □ − 5 = 19 |
| I | `gcse_bidmas_roots_indices` * | Calculate √36 + 9 × 3² |
| D | `gcse_bidmas_decimals` * | Calculate 0.2 × (5.5 − 1.7)² ÷ 0.4 |
| D | `gcse_bidmas_fraction_bar_negatives` * | Calculate (9 − (−3)^3)/(6 − 2^2) |
| D | `gcse_bidmas_insert_brackets` | Where do the brackets go in 8 + 9 × 7 − 1 = 118? (multiple choice) |
| D | `gcse_bidmas_neg_indices_division` * | Calculate (−5)² ÷ 5 + 3 × (−4)² |
| D | `gcse_bidmas_substitute_negatives` * | Work out the value of 3a^2 - 4b when a = -2 and b = 3 . |

**number** (2 new)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_number_reciprocal` * | Write down the reciprocal of 3. |
| I | `gcse_number_counting_product` * | A cafe sells 4 starters, 5 main courses and 5 desserts. How many three-course meals can be chosen? |

**ratio_proportion** (3 new)

| Tier | Slot | Example question |
|---|---|---|
| I | `gcse_ratio_combine` * | The ratio of red to blue is 4 : 3 and of blue to green is 1 : 7. Write red : blue : green in its simplest form. |
| I | `gcse_ratio_from_difference` * | Ann and Ben share some money in the ratio 5 : 6. Ben gets £10 more than Ann. How much money is shared altogether? |
| D | `gcse_ratio_proportional_square` * | y is directly proportional to the square of x. When x = 2, y = 16. Find the value of y when x = 6. |

### 17.2 Moved items (moved, not copied: each name still resolves through `variant_utils.lookup_variant_by_name`)

| Topic | From | To | Items |
|---|---|---|---|
| fdp | intermediate | foundational | `gcse_fdp_fraction_to_decimal`, `gcse_fdp_fraction_to_percentage`, `gcse_fdp_percentage_to_fraction` |
| multiples_factors | intermediate | foundational | `gcse_mf_factor_pairs`, `gcse_mf_hcf`, `gcse_mf_lcm` |
| surds | intermediate | foundational | `gcse_surds_multiply`, `gcse_surds_practice_divide`, `gcse_surds_practice_compare` |
| algebra | intermediate | foundational | `algebra_practice_substitution`, `algebra_practice_factorise_hcf`, `algebra_practice_change_subject` |
| decimals | intermediate | foundational | `gcse_dec_practice_word_total` (`gcse_dec_practice_money_change` stays: it keeps the intermediate tier at 10 kinds) |
| decimals | difficult | foundational | `gcse_dec_round` |

Two difficult-tier entries that repeated a kind the lower tiers already serve were dropped, not moved: `gcse_dec_divide` (decimals, an echo of the intermediate divide) and the bidmas `gcse_bidmas_brackets` and `gcse_bidmas_with_negatives` lines (still served in F and I). Seeds follow `crc32('slug/tier/fn')`, so a moved slot draws different questions in its new tier.

### 17.3 Merge

`algebra_practice_factorise_1`, `_2` and `_3` (solve x^2 + bx + c = 0 by factorising, roots up to 6, 8 and 10) are one slot, `algebra_practice_factorise` (it draws one of them at random), in the intermediate tier. The three names are in `register.RETIRED` and still resolve. `register.VARIETY_DEFERRED` is now empty. The answer check smoke's reference to `algebra_practice_factorise_1` still passes through the retired-name path.

### 17.4 Metrics, before and after (`--variety-report`, default seeds; before is the Phase 0 and 1 tree with 1,011 slots)

| Metric | Before | After |
|---|---|---|
| Practice slots / strict kinds | 1,011 / 1,009 | 1,064 / 1,064 |
| Tiers below 7 kinds / below 9 kinds | 28 / 42 | 19 / 27 |
| Mean share of 7-question queues that repeat a kind | 29.2% | 19.8% (ceiling 0.293 to 0.2) |
| Tiers that repeat a kind in every queue | 28 | 19 |
| Fixed variants | 76 | 77 (`FIXED_VARIANTS` is unchanged: `gcse_surds_identify_irrational` asks one stem and varies only its options) |
| Verification smoke, alone | 37.7 s | 32.8 s |

Strict kinds per tier (F / I / D):

| Topic | Before | After |
|---|---|---|
| algebra | 1 / 6 / 7 | 9 / 9 / 9 |
| bidmas | 6 / 6 / 6 | 9 / 9 / 9 |
| decimals | 6 / 10 / 9 | 9 / 10 / 9 |
| fdp | 3 / 9 / 8 | 9 / 10 / 9 |
| multiples_factors | 3 / 8 / 7 | 9 / 9 / 9 |
| surds | 3 / 8 / 8 | 9 / 9 / 9 |
| number | 15 / 20 / 20 | 16 / 21 / 20 |
| ratio_proportion | 16 / 15 / 13 | 16 / 17 / 14 |

All of these are the new `VARIETY_FLOORS` values (a ratchet only rises, so each floor equals the measured value; the queue-repeat ceiling is 0.2 against 0.198 measured).

Evidence: `--deep --seed 9100` passes (212,800 practice questions, 19,249 checker round trips, 229 s; D1 and D2 both 0, so no unlisted sibling group). Hints smoke about 12 s, ladder and MCQ smokes, retired compat, correctness, answer check and MCQ letter smokes pass, `ruff check .` is clean, full suite 109 of 109.

### 17.5 Hints (docs/GCSE_MATHS_HINTS.md section 28)

38 of the 56 new slots (67.9%) can produce a topic hint, above the 60% goal. The 18 without one: the multiple choice slots (`inverse_check`, `insert_brackets`, `identify_irrational`, `match_simplified`), the surd answers (`add_like`, `multiply_coefficients`, `rationalise_coefficient`, `pythagoras_exact`, `expand_single_bracket`), `list_factors` (a list), and the algebra slots that have no recorded family yet (`collect_terms`, `expand_single`, `index_laws_simplify`, `factorise_simple`, `difference_two_squares`, `index_laws_coefficients`, `expand_two_brackets`, `expand_three_binomials`).

### 17.6 Bugs found and fixed on the way

* **Checker:** an algebraic answer typed with a superscript above 2 (x^3 as x³, x⁴, and so on) was marked wrong; `answer_checkers._superscripts_to_caret` now reads every superscript digit run, in the power normaliser and in the sympy preparation. The round trip caught it on `algebra_practice_index_laws_simplify`.
* **Algebra parser caps:** the index-law generators keep exponents at 10 or below (the checker's cap).
* **Choice slots in the old wrappers:** `gcse_bidmas_inverse_check`, `gcse_bidmas_insert_brackets`, `gcse_surds_identify_irrational` and `gcse_surds_match_simplified` are graded by option buttons; three answer-check smoke assertions now say so (a choice has no raw answer).
* **Correctness smoke:** two false positives (the "to N d.p." of a question about the error made by rounding, and "estimate ... by rounding each number to 1 s.f." with a longer exact answer) are skipped; the latter was a latent pre-existing case that a pool reorder exposed.
* `gcse_fdp_percentage_of_another` no longer asks "scored 246 out of 200"; a part bigger than the whole appears only in the plain "Write 73 as a percentage of 50" wording.

### 17.7 Deferred

* Topic rules for the 18 slots above (the algebra ones need `DERIVE` parsers, and `DERIVE_NONE` has a reviewed row that keeps "Expand 3(x + 2)" unread, so that is a decision, not a gap).
* `gcse_bidmas_fraction_bar_negatives` solution text is correct but built from two branches; tidy when the bidmas tier is next touched.
* Surd-typed answers have no scalar hint path (the surd checker's own feedback applies).
* number and ratio_proportion: only the section 4 P1 rows were added; P2 rows and the thin F tiers of ratio_proportion are batch B.

---

## 18. Phase 3 batch A review notes (2026-10-27, independent review, nothing committed)

Reviewed against sections 4, 7, 10, 11, 14, 16 and 17, `docs/GCSE_MATHS_HINTS.md` section 28 and the code, as a GCSE maths teacher (AQA 8300 / Edexcel 1MA1) and as a code reviewer. Every one of the 56 new generators was read over 30 seeds (question, worked solution, hint, marks and key on the first 3; question and key on the rest), then scanned by script over 600 seeds for degenerate draws; the 14 moved items over 4 seeds each in their new tier. Everything below was fixed in the tree unless it says otherwise.

### 18.1 Findings

Counts are out of 600 seeded draws of the generator, before and after the fix.

| # | Severity | Finding | Outcome |
|---|---|---|---|
| 1 | High | **"Simplify" answers accepted the question typed back.** The collect-like-terms and both index-law slots had no answer form, so `3a + 6b + 6a + 4b`, `x^2 × x^5`, `2x^4 × 5x^2` and `30x^4/(6x^2)` were marked right for their own questions. | Fixed. `algebra_practice_collect_terms` now asks for the expanded form (like terms collected); `index_laws_simplify` and `index_laws_coefficients` ask for `simplified`, and the checker's simplified form gained a single-term rule: when the key is one term (a number times letters to whole powers), the answer must be one term too, else `powers_not_combined` ("That's equal, but it can be simpler. Use the index laws to write it as a single term."). Keys that are sums or fractions are untouched (the algebraic fractions slots behave as before). The verification smoke now requires these forms (a "Simplify" question whose key is one term needs `simplified`; one whose key is a sum of plain terms needs `expanded`), and `forms.wrong_form_entries` types the question's quotient and a split power back for single-term keys. New unit tests in the answer check smoke. |
| 2 | High | **The format hint was sometimes the answer.** `e.g. x^6` under "Simplify (t^3)^2" (91 of 600), `e.g. (x - 3)(x + 3)` under "Factorise x^2 - 9" (20), `e.g. x^3 + 6x^2 + 11x + 6` under (x + 1)(x + 3)(x + 2) (9), and the same for expand single (1), two brackets (1), factorise (3), form an expression (3), index laws with numbers (3). | Fixed: `_example(result, ...)` picks the first example that is not equal to the answer (0 of 600 in every slot). |
| 3 | High | **Impossible triangles.** `algebra_practice_form_equation_shape` drew sides that cannot make a triangle (x = 4: 4, 11 and 5 cm) or a side of 0 cm (63 of 600). | Fixed (0 of 600), and the `alg_form_perimeter` solver now refuses sides that fail the triangle inequality (mutation G1). |
| 4 | Medium | **"Give your answer as a mixed number" for answers below 1 or whole.** Mixed multiply and divide 200 of 600 (1 1/3 ÷ 3 2/5 = 20/51; 1 1/2 × 2 2/3 = 4), mixed add and subtract 76 (2 5/6 − 2 1/3 = 1/2); "as a fraction" with a whole answer 22 (5/6 ÷ 1/6 = 5). | Fixed: answers are more than 1 and not whole where a mixed number is asked for, and never whole where a fraction is (0 of 600). |
| 5 | Medium | **`gcse_dec_round` (moved to F) asked for rounding that was already done** ("Round 605.944 to 3 decimal places"), rounded with `round()` on a float, and had an em dash in the working; **`gcse_dec_practice_word_total` (moved to F) showed "£4.2 each".** | Fixed (both are moved slots, so their output may change): four decimal places with the last one not 0, half-up rounding of the exact value, no dash; money to the penny. |
| 6 | Medium | **Fraction bar over 1.** `gcse_bidmas_fraction_bar_negatives` had a bottom line of 1 in 282 of 600 draws (the loop accepted any bottom that divides, and 1 always does). | Fixed: the bottom is 2 to 6 (0 of 600). |
| 7 | Medium | **A hint named the wrong cause.** "It looks like the bottoms were added as well" was also given for a subtraction whose bottoms were subtracted; three rules matched a non-whole slip by rounding, so 11 for "7 × □ − 4 = 80" (key 12, a slip by one) was called "the wrong inverse" (76/7 rounds to 11), and 22 for an angles question (key 23) "the sign" (151/7). | Fixed: the message now reads "added or taken away"; `bidmas.missing_wrong_inverse`, `alg.angles_sign_moved`, `alg.angles_x_once` and `alg.perimeter_sign_moved` keep only whole-number slips (the answers are whole numbers), so these stay silent. New cases in `gcse_hints_cd.other_cases` (mutation H3). Docs: `docs/ZORP_CHARM.md` Appendix A regenerated. |
| 8 | Medium | **Flaky tests.** bidmas F now holds a multiple-choice kind (`gcse_bidmas_inverse_check`, 1 slot in 9), so the first question of a fresh bidmas F queue has no free-response box about 1 time in 9; seven tests that start bidmas F and assume a free-response number failed at random (seen here on the first answer check run). | Fixed in the tests: those seven now start bidmas intermediate, which is all free response (`test_answer_check_smoke.py` five, `test_phase1_numeric_smoke.py` two). The product is unchanged. |
| 9 | Medium | **The correctness smoke skip was too broad.** Any question containing "by rounding each" or "difference between the rounded value" skipped every stated-accuracy check, so an answer accuracy stated in the same question would never be checked. | Tightened: only the input-rounding clause itself is taken out of the text (three exact phrasings), and the rest of the question is checked as before. A self-test runs first (an answer that breaks a separately stated accuracy is still flagged; mutation T1). |
| 10 | Low | Coverage gaps in the tests: the hint unit table had no row for "how much does the smaller share get" (a mutant that broke that branch passed), the `mf_pf_exponents` solver did not check that the primes given make up the whole number. | Fixed: a unit row (mutation H2); the solver refuses a number that is not exactly a product of the given prime powers. |
| 11 | Low | Wording and working: "6x + 0 = 180" (71 of 600 angle draws); "2 divides in 2 times"; "3/4 = 3/4, so the reciprocal is 4/3 = 4/3"; "1 × (√3 × √3)"; "10√6 = 10√6"; "18 ÷ 1 × 10"; "7.00 − 2.5"; "x = 7, so x = 7"; "8 − 7 = 1 parts"; "2 × 4 - (25)"; "(5.7 − 4.0)" in a question; a surd hint whose worked example 3x + 4x = 7x could carry the answer's 7. | Fixed (each line now shows only the steps that happen; numbers are never shown with a spare ".0"). Three more lap-time pairs give the laps question ratios 5 : 3, 7 : 4 and 6 : 5 as well as 3 : 2, 4 : 3 and 5 : 2. |
| 12 | Low, not changed | `gcse_bidmas_roots_indices`: the subtraction form ("377 − √64 × 5") has a root but no index, and its first number is up to three digits. | Correct and verified; a second kind of line within the slot. Changing it moves its record shape, solver and hint rule together; left for the next bidmas pass. |
| 13 | Low, fixed 2026-10-28 (pre-existing) | Typed units: "146%", "£1100" and "2√7 cm" are refused by the number and surd checkers (every existing percentage, money and exact-length slot behaves the same; the box says "Enter a number"). `x*x^6` is read as x^(2^6) by the `x*x` to `x^2` rewrite. | Fixed in a checker-wide pass: see "Units and symbols typed with an answer" in `docs/GCSE_MATHS_VERIFICATION.md`. |

### 18.2 Verdicts by topic (as a GCSE teacher)

* **algebra:** correct maths throughout after findings 1 to 3. F (collect terms, index laws, expand one bracket, form an expression, form and solve from a perimeter, plus the moved substitution, common-factor factorising and two-step rearranging) is all Foundation content. I is Foundation content too (factorising x^2 + bx + c, the difference of two squares with a = 1, fraction equations, angle equations) placed at the top of the Foundation range, which suits an intermediate tier. D (three binomials, forming a quadratic from an area) is Higher. Agree.
* **fdp:** correct. F (add and subtract fractions, one quantity as a fraction or percentage of another, plus the three moved conversions) is Foundation. I (multiply and divide, mixed numbers, simple interest) agree; simple interest is Foundation content but sits well beside percentage change. D simple against compound interest agree.
* **multiples_factors:** correct. F (list, count, next multiple, plus the moved factor pairs, HCF and LCM) agree; HCF of two numbers that turn out coprime (answer 1) is a fair Foundation question. I agree. D (smallest multiplier for a square; number of factors from a prime factorisation) is problem-solving beyond the core specification wording but a standard Higher question style; agree.
* **surds:** a Higher-only topic, so F is its easiest part, as section 16.2 says: like surds, the square of k√r, spotting the irrational number, and the moved √a × √b, √a ÷ √b and comparing; agree. I and D agree.
* **decimals:** correct. Known product in I and known division in D agree (division with a decimal divisor is the harder of the two); rounding error in D is fine (its answer has four decimal places by design, which is why finding 9 exists).
* **bidmas:** correct after finding 6. F inverse check is the section 4 row; the two newly reachable directed-number kinds fit F. I and D agree; D decimals with a square is heavy for a non-calculator question but valid.
* **number:** reciprocal F and the counting product rule I agree (the product rule is Foundation in AQA, I is a fair place for it).
* **ratio_proportion:** combining ratios and ratio from a difference I, y proportional to x squared D; agree.

The 14 moved items are Foundation level (sampled in their new tier); every name resolves through `lookup_variant_by_name` and generates (the retired compat smoke now lists 77 names: 74 before plus the three factorise ranges). Nothing was lost: the D tier echoes that were dropped (`gcse_dec_divide`, bidmas `brackets` and `with_negatives`) are still served in their lower tiers, and their functions are byte-identical.

### 18.3 The superscript change

`_superscripts_to_caret` turns a run of superscript digits into `^digits` (`**digits` for SymPy) before any other parsing, so it is exactly as if the pupil had typed a caret: every cap (expression length, exponent 12, nested exponent 100, total letter power 8, node count) and every form rule applies unchanged. Checked: x³, x¹⁰, 4x¹⁰ and x²y³ accepted; x³³, x^³, x**³, 3000 superscript ² and x⁹⁹⁹⁹⁹⁹⁹⁹⁹ refused at once (under 5 ms); ⁰ and ¹ read as powers; negative superscripts (x⁻¹) are not read and are refused, as before; (x+1)³ under the expanded form is refused as unexpanded. The regex is linear. A unit test now covers these.

### 18.4 The DERIVE_NONE row ("Expand 3(x + 2)")

The row is a negative control for `derive_expand2`, the parser of the family `expand2` (two brackets multiplied, whose only rule is the missed cross term). Lifting it would let the two-bracket family read a single bracket, which has no cross term, so the rule could only misfire; the parser's own `u.a == 0` guard already refuses it. **Recommendation: keep the row.** If single brackets should get topic hints, add a separate parser and family (`expand1`, k(ax + b), with slips such as the second term not multiplied, 3x + 2, and the sign of a negative multiplier not applied to the second term), each with its own `DERIVE_TX` and `DERIVE_NONE` rows; `expand_single` and `expand_two_brackets` would both benefit. Not done here (a hints-track change).

### 18.5 Drift

Every practice slot of the tree before Phase 2 (`pb_before`, practice is unchanged by Phase 2) and of this tree, called directly by name with the same seeds (1,007 and 1,063 functions, 3 seeds each, SVG ids normalised): the only differences are `gcse_dec_round` and `gcse_dec_practice_word_total` (moved, fixed in finding 5). The retired factorise ranges and the dropped echoes (`gcse_neg_powers`, `gcse_bidmas_with_negatives`, `gcse_dec_divide`) are byte-identical over 20 seeds. New in this tree: the 56 new slots, the merged `algebra_practice_factorise` and the two directed-number kinds (`gcse_neg_add_subtract`, `gcse_neg_multiply_divide`, edited in batch A: no zero operands, a bracket only round a negative, a record line; they were in no pool before).

The `variant_name=None` fallback pools inside `gcse_maths_bidmas` and `gcse_maths_decimals` do not match the queue pools (bidmas F lacks the directed-number kinds and bidmas D still lists two echoes; decimals I still lists `gcse_dec_round`). They are reached only when a topic has no variant queue, which none of these topics has; left as they were.

### 18.6 Mutation tests (on a copy of the tree; each file restored and compared byte for byte afterwards)

| Mutation | Caught by |
|---|---|
| S1 `frac_mixed_mul_div` solver multiplies the wholes and the fractions apart | verification smoke |
| S2 `mf_square_multiplier` solver returns the square root | verification smoke |
| S3 `prop_square` solver treats y as linear in x | verification smoke |
| G1 the triangle guard removed from the generator | verification smoke (new solver check) |
| G2 an index-law slot loses `simplified` | verification smoke `answer_form` (14 issues); passed before this review |
| G3 collect terms loses `expanded` | verification smoke `answer_form`; passed before this review |
| H1 the mixed-number "parts apart" slip computed wrongly | hints smoke unit table |
| H2 the ratio-from-difference slip wrong for the smaller share | hints smoke unit table (new row); passed before this review |
| H3 the whole-number filter removed from the missing-number rule | hints smoke `other_cases` (new case) |
| C1 superscripts back to ² only | answer check smoke (new unit test) |
| C2 the single-term rule switched off | answer check smoke and verification smoke |
| T1 the stated-rounding check skipped for any question with the clause | correctness smoke self-test |

### 18.7 Results after the review (this machine, 2 CPUs)

| Run | Result |
|---|---|
| Verification smoke, default, alone | passes; 30.7, 31.2 and 33.5 s wall (section 17: 32.8 s) |
| Verification `--deep --seed 31337` | passes, 245 s (run beside the mutation tests) |
| Hints smoke / ladder / MCQ notes | 12.4 s / 2.9 s / 1.6 s, pass (405 topic rules and 175 pair, box and expression rules fire; unit table 481 topic rows) |
| Retired compat / correctness / answer check / MCQ letter / voice | 2.4 s / 11.2 s / 5.5 s / 2.2 s / 6.2 s, pass |
| `ruff check .` | clean |
| Full suite | see the final line of `/tmp/claude-0/suite_v3a_review.log` |

Metrics unchanged by the review: 1,064 practice slots, 1,064 strict kinds, the `VARIETY_FLOORS` of section 17.4, 19 tiers below 7 kinds.


## 19. Build notes: Phase 3 batch B, thin practice tiers (2026-10-28, not committed)

Batch B raises simultaneous equations, completing the square, quadratic simultaneous equations, algebraic fractions, algebraic proof, functions and graphical simultaneous equations to at least 9 strict kinds in every tier, and adds the section 4 P1 and P2 rows (iteration, change of sign) to equations and inequalities. Same standard as batch A (section 17): each slot is generated by code, has a worked solution and a hint, a correct answer type and form flag, a `record()` family or an `@verifies('alg')` task with an independent solver, and goes through the checker round trip.

### 19.1 New slots (82)

Code: `generators/gcse/maths_variety_b.py` (70 slots), `generators/gcse/graphical_simultaneous_equations.py` (12 gsim slots, they draw their own graphs), wiring in each topic module (`_batch_b_pools()`; the practice queue is now the default 7 for the six topics that had 5).

| Topic | Foundation | Intermediate | Difficult | Example (one per tier) |
|---|---|---|---|---|
| simultaneous_equations (12) | `sim_substitute_solution`, `sim_numbers_sum_difference`, `sim_rectangle_perimeter`, `sim_equate_expressions` | `sim_decimal_coefficients`, `sim_two_item_check`, `sim_value_of_expression`, `sim_equal_sides` | `sim_fractional_coefficients`, `sim_ages`, `sim_no_solution_value`, `sim_equal_cost` | F: "The simultaneous equations 4x + 5y = c and 3x + 2y = d have the solution x = 6 and y = 7. Find c and d."; I: "0.2x + 0.5y = 4 and 0.2x + 0.2y = 2.2"; D: "A mother is 4 times as old as her daughter. In 5 years' time ..." |
| completing_the_square (12) | `cts_f_negative_half`, `_line_of_symmetry`, `_read_min_value`, `_find_q_given_p` | `cts_i_hence_solve`, `_a_minus_square`, `_turning_point_expression`, `_count_roots` | `cts_d_leading_coefficient_solve`, `_min_non_monic`, `_fraction_form`, `_vertex_to_coefficients` | F: "x^2 + 12x = (x + 6)^2 + q, find q"; I: "x^2 + 12x + 20 can be written as (x + 6)^2 - 16. Use this to solve ... = 0"; D: "Write x^2 + 3x + 5 in the form (x + p)^2 + q. Give p and q as decimals." |
| quadratic_simultaneous_equations (12) | `qsim_f_expand_substitution`, `_y_from_x_values`, `_circle_line_y`, `_solve_substituted` | `qsim_i_shifted_parabola`, `_circle_line`, `_sum_and_product`, `_hyperbola_line` | `qsim_d_tangent_k`, `_largest_k_miss`, `_midpoint_of_chord`, `_circle_show_that` | F: "y = x^2 meets y = x + 6 where x = -2 and x = 3. Work out the y-coordinate at each point."; I: "x^2 + y^2 = 65, y = 2x + 10"; D: "The line y = 2x + k is a tangent to y = x^2 + 2. Find k." |
| algebraic_fractions (12) | `af_f_numeric_common_factor`, `_add_expression_numerators`, `_evaluate_fraction`, `_undefined_value` | `af_i_simplify_two_quadratics`, `_divide_fractions`, `_add_numeric_denominators`, `_solve_cross_multiply` | `af_d_subtract_linear_denominators`, `_solve_reciprocal_quadratic`, `_simplify_non_monic`, `_solve_two_fractions` | F: "For what value of x is 2/(2x - 4) not defined?"; I: "Simplify (x + 4)/(x - 1) divided by (x + 4)/(x + 6)"; D: "Solve -2/(x + 1) + 3/(x - 1) = 1" |
| algebraic_proof (12) | `ap_f_simplify_to_constant`, `_expand_even_product`, `_common_factor_bracket`, `_multiple_of_five_form` | `ap_i_sum_consecutive_odds`, `_consecutive_squares_difference_odd`, `_difference_of_squares_identity`, `_factorise_to_show_multiple` | `ap_d_sum_consecutive_squares_odd`, `_difference_squares_multiple_of_eight`, `_euler_prime_counterexample`, `_odd_squares_difference_multiple_of_eight` | F: "Explain why 15k + 5 is always a multiple of 5"; I: sum of two consecutive odds is a multiple of 4; D: smallest n for which n^2 + n + 17 is not prime |
| functions (7) | `fn_f_negative_input`, `_three_values_quadratic` | `fn_i_composite_both_orders`, `_solve_square_equals`, `_inverse_value`, `_inverse_divide` | `fn_d_composite_square_expression` | F: "f(x) = 13 - 4x. Work out f(-3)"; I: "f(x) = 6x - 1. Work out f^-1(35)"; D: "f(x) = x^2, g(x) = 4x - 1: write f(g(x)) expanded" |
| graphical_simultaneous_equations (12) | `gsim_f_read_x_at_crossing`, `_read_y_intercept`, `_solve_from_equations`, `_read_gradient` | `gsim_i_standard_form_pair`, `_cost_at_break_even`, `_parabola_two_solutions` | `gsim_d_horizontal_line_roots`, `_tangent_constant`, `_cheaper_up_to`, `_read_roots_then_check`, `_find_second_constant` | F: "The graph shows two lines that meet at P. Write down the x-coordinate of P."; I: two firms' costs, "What is the total cost when they charge the same?"; D: "The line y = 8x + k touches y = x^2 at the marked point. Find k." |
| equations_inequalities (3) | | `eq_i_iteration_linear` | `eq_d_iteration_reciprocal`, `eq_d_change_of_sign` | I: "x(n+1) = 4x(n) - 1 with x(0) = 3. Work out x(1) and x(2)"; D: "f(x) = x^3 + 3x - 24 has a root between two consecutive whole numbers. Work out f(1), f(2), f(3) ... find n." |

Tiers of the seven topics are now 9, 9, 9 strict kinds (`VARIETY_FLOORS['tier_kinds']`); equations_inequalities is 16, 19, 22 (was 16, 18, 20). Foundation and Intermediate use whole-number or terminating-decimal answers; the decimal slots say "as a decimal" and the fraction answers say "fully simplified".

### 19.2 Metrics before and after

| Measure | Before | After |
|---|---|---|
| Practice slots | 1,064 | 1,146 |
| Strict kinds | 1,064 | 1,146 |
| Tiers below 7 kinds | 19 | 0 |
| Tiers below 9 kinds | 27 | 6 |
| Mean queue-repeat share | 19.8% | 0.0% (`queue_repeat_mean_max` 0.2 to 0.005) |
| Fixed variants (`FIXED_VARIANTS`) | 77 | 81 (the list is unchanged; the figure counts the new fixed lookups; 49 run in the default run) |
| Session cookie, practice (p50 / p90 / max) | 659 / 1,739 / 2,711 | 684 / 1,767 / 2,711 |
| Topic hint slots | 659 of 1,064 (61.9%) | 686 of 1,146 (59.9%) |
| Combined hint slots | 820 (77.1%) | 881 (76.9%) |

### 19.3 Verification

* Independent solvers in `scripts/gcse_verify/solvers_variety_b.py` (28 record families, 9 new `gsim_*` tasks that read the drawn lines, curves and marks). The solvers import only the standard library, sympy and sibling `gcse_verify` modules.
* Roots and sets are judged with `judge(Ctx(_p, {}), 'set', ...)` (`@solver(..., problem=True)`) so two roots are compared with the one `quadratic_roots` field.
* Ordered proofs: two slots have independent steps and are in `register.ORDER_FREE_PAIRS`; the rest are strict chains.
* Checker: `answer_checkers.check_algebraic_fraction` now refuses a fraction that is equal but not in lowest terms when the question asks for "fully simplified" (`_fraction_in_lowest_terms`: polynomial gcd and content, and an integer gcd for numeric fractions); `forms.wrong_form_entries` supplies the round-trip entry. New test `test_check_algebraic_fraction_lowest_terms`.
* Drift: 3,192 outputs of the 1,064 old slots (3 seeds each) are byte-identical to the pre-batch tree.

### 19.4 Hints

19 of the 82 new slots carry a topic rule (23%), in 22 new rules for 19 record families (see `docs/GCSE_MATHS_HINTS.md` section 29). The share is below batch A (68%) because most of the new slots are checked by `@verifies('alg')` tasks (roots, expressions, coordinates read from a graph), and those have no record family to hang a rule on; so `TOPIC_FLOOR_SHARE` moves 0.615 to 0.595 and `COMBINED_FLOOR_SHARE` 0.770 to 0.765 (measured 59.9% and 76.9%).

### 19.5 Bugs found on the way

* A wrong sign in the line-of-symmetry slot (bracket of `x + p` has symmetry at `-p`); caught by the solver.
* A generator that looped for ever (two fractions with a quadratic that had to factorise): replaced by 14 precomputed cases.
* The common factor slot always had the answer `a + b`; it now varies the coefficients.
* Solutions that put a worked-out number at the end of a ladder rung 2 (`fn_i_solve_square_equals`) now say "rearrange to leave x^2 on its own".
* An existing test (`test_quicktest_check_wrong_answer_not_session_mismatch`) drew the foundational bidmas pool once, and that pool has a multiple-choice slot with no typed key, so it failed on about one run in a few; it now draws up to 20 times for a typed one.

### 19.6 Deferred

* More topic rules: 63 new slots have none (verified by `@verifies` tasks). A rule family per task (roots, expanded expressions) would need a `record` beside the task.
* Six tiers elsewhere are still below 9 kinds (not part of this batch).
* The deep run at `--seed 7000` showed a pre-existing unit round-trip failure in `transformations/difficult/_trans_diff_algebraic_coords` (an algebraic key typed with a `%` is accepted by `number_fields`); it is not touched by this batch (the slot, the checker path and the seed are unchanged), so it is left for a separate fix.
* `QUIZ_THIN_TOPICS` (functions, quadratic simultaneous equations) was left as it is: the entries still repeat a kind in 4 of 4 quizzes.
* The verification smoke is 43 s alone (batch A 32.8 s), inside the 35 to 44 s budget, mostly from sympy simplification in the new `alg` tasks.

Review (section 20): the deep-run failure is fixed (it was the verification expectation, not the checker), topic hints are back to 60.2% with the floor at 0.60, and the smoke is about 1.5 s over the pre-batch tree instead of 5.


## 20. Phase 3 batch B review notes (2026-10-28, independent review, nothing committed)

Reviewed against sections 4, 7, 10, 11, 17 to 19, `docs/GCSE_MATHS_HINTS.md` section 29, "Units and symbols typed with an answer" in `docs/GCSE_MATHS_VERIFICATION.md` and the code, as a GCSE maths teacher (Higher tier, AQA 8300 / Edexcel 1MA1) and as a code reviewer. Every one of the 82 new generators was read over 30 seeds (question, worked solution, hint, marks, key, form flag and format hint on the first 2 or 3; question and key on the rest), then scanned by script over 60 to 3,000 seeds for degenerate working, answers equal to printed numbers, variety and form flags. The twelve graphs were rendered and checked for whether the value to be read lies on a grid line. Everything below was fixed in the tree unless it says otherwise.

### 20.1 Findings

| # | Severity | Finding | Outcome |
|---|---|---|---|
| 1 | High | **"Expanded and simplified" accepted the bracket typed back.** `gcse_fn_d_composite_square_expression` returns `form: expanded`, but the functions topic wrapper (`_fn_problem_from_output`) dropped it, so (2x - 5)^2 for f(g(x)) was marked right (every draw). Its format hint "e.g. 4x^2 + 12x + 9" was the answer when g(x) = 2x + 3. The smoke's form rule only looked at "Simplify" questions and the `expand` task, so it passed. | Fixed: the wrapper passes `answer_form` (no older functions slot sets one, so nothing else changes); `_example` picks a hint that is not the answer. New smoke rule: an algebraic key that is a sum with no brackets, under a question that says "expand", needs `expanded` (mutation G1). |
| 2 | High | **Graph values not on any grid line.** The grid is drawn only at the label stride (2, 5 or 10), so the value a pupil must read lay between grid lines in 177 of 300 y-intercepts, 240 of 300 break-even costs, 249 of 600 parabola crossings, 296 of 600 horizontal-line roots, 230 of 600 crossing y-values, 145 of 600 tangent points and 72 of 300 "cheaper up to" crossings (for example a y-intercept of 6 on a scale with lines at 0, 5, 10). | Fixed for the 12 new graph slots: faint lines at every whole number between the labelled ones (`_svg_minor_grid`, opt-in `minor_grid=True`; skipped on an axis spanning more than 60). Now 0 off-grid values in 300 draws of each slot. The older gsim slots use the same helper with the flag off, so they are byte-identical (and keep the problem: see 20.7). |
| 3 | Medium | **The final answer line did not render.** Four solutions put `<strong>` inside `\( ... \)` (`cts_f_find_q_given_p`, `cts_f_negative_half`, `_gsim_d_find_second_constant`, `_gsim_d_tangent_constant`); MathJax 3 only joins math across `<br>`, so the line showed raw TeX. | Fixed: the bold is outside the math, as everywhere else in the repo. |
| 4 | Medium | **The counterexample item.** `n^2 - n + 41` had the answer 41, the number in the question; the two 41 versions need 40 values up to 1,601 checked for primes before a pupil can know the answer is the *smallest*, and the solution only said "primes for the early values". The `n^2 + n + 17` case was fine. | Fixed: five quadratics (n^2 + n + 11, n^2 + n + 17, n^2 + 3n + 13, n^2 + 5n + 17, n^2 + 3n + 19) whose first failure is at n = 8 to 16 with every earlier value a prime below 260; no answer is a printed number; the solution lists the earlier values. The answer stays unique (smallest) and is a plain number ("16"; "n = 16" is refused by the number box, as for every number answer). The `counterexample` solver reads all five. |
| 5 | Medium | **Answers equal to the printed numbers.** `af_d_solve_two_fractions`: 2 of its 14 cases had roots equal to the two numerators (-3/(x + 1) + 2/(x - 1) = 1 gives -3 and 2), 8 of 60 draws. | Fixed: those cases are left out (12 remain). Also `af_i_solve_cross_multiply` no longer draws x equal to a denominator and `fn_i_inverse_value` no longer draws the answer equal to m or the constant. |
| 6 | Medium | **A "non-monic" fraction that was really monic.** `af_d_simplify_non_monic` cancelled brackets such as (2x - 2) and (3x + 3) in about a third of draws: a teacher factorises 2x^2 - 8x + 6 as 2(x - 1)(x - 3), and the worked solution's "(2x - 2)(x - 3)" models poor factorising. | Fixed: the common bracket ax + t has gcd(a, t) = 1. |
| 7 | Medium | **Too few different questions.** `sim_ages` gave 7 different questions in 3,000 draws; `qsim_d_largest_k_miss` 6; `_gsim_d_tangent_constant` 4; `_gsim_d_horizontal_line_roots` 3, and it was a Foundation reading ("use the graph to solve x^2 = 16") in the difficult tier. | Fixed: ages from every (k, m, n) with a child of 3 to 15 and a parent 18 to 70 years older (23 cases, 46 with the names); largest k with 12 gradients of either sign and 7 curves y = x^2 + c (the solver and the hint TRUTH read `c0`, default 0); tangent with gradients of either sign (8); the horizontal-line slot now asks for x^2 - 16 = 0, 2x^2 = 32 or x^2 + 3 = 19, so the equation must be rearranged first (12 questions, a Higher step). |
| 8 | Medium | **A stationary iteration.** `eq_i_iteration_linear` started at the fixed point in 5.3% of draws (x(n+1) = 2x(n) - 5 from x(0) = 5 gives 5 and 5). | Fixed: x(1) differs from x(0). |
| 9 | Medium | **The "fully simplified" message named brackets for numbers.** 6/8 and (2x + 6)/(2x + 2) got "Factorise the top if needed, then cancel the matching bracket". | Fixed: a common number gives the new kind `common_factor`, "That's equal, but it can be simpler. Divide the top and the bottom by a number that goes into both."; a common bracket keeps `not_simplified`. `forms.wrong_form_entries` types both. See 20.3. |
| 10 | Medium | **The deep-run failure** (`--seed 7000`, `transformations/difficult/_trans_diff_algebraic_coords`). | Diagnosed and fixed in the verification expectation, not the checker: see 20.4. |
| 11 | Low | Working lines: "1x = 4", "9 + 1n", "1n = 4", "1c = 14", "y = 24, so y = 24", "x = -2, so x = -2", "x = -20, so x = -20", "(x + 5)(x + 0) = 0", "- 81/4 + 0", "((-2))^2" and "+ 0" in f(x) tables, "(4)^2", "-1 × (-2)", "1 × 4", "0 + 4x - x^2" printed in a question, "3x/3" printed in a question. | Fixed (each line shows only the step that happens; x(x + 5) for a zero root). |
| 12 | Low, not changed | `_gsim_d_cheaper_up_to` has only 4 possible answers (2 to 5) and they often equal a printed rate; the reasoning (strictly cheaper, so one less than the crossing) is the point. `cts_f_line_of_symmetry`, `cts_f_read_min_value` and `cts_i_count_roots` print their answer by design (reading the form is the skill). | Accepted. |

### 20.2 Verdicts by topic (as a GCSE teacher)

* **simultaneous_equations:** correct and unique in every draw (the elimination working asserts its values). F (substitute a given solution, sum and difference in words, rectangle perimeter, equate two "y =" lines) is Foundation; I (decimal coefficients, two purchases then a third, value of xy or x^2 + y^2, opposite sides of a rectangle) and D (fractional coefficients, ages, k for no solution or infinitely many, equal cost) agree. "Infinitely many solutions" is beyond the usual wording but a fair Higher extension.
* **completing_the_square:** correct. F is the easiest part of a Higher topic (p from a negative coefficient, line of symmetry, least value, q given p); I and D agree. "Give p and q as decimals" in the fraction-form slot is a checker limitation (the completed-square type does not read 7/2); acceptable, since 3.5 and -7.25 are exact.
* **quadratic_simultaneous_equations:** correct. Every circle chord meets the circle at two lattice points; the tangent slot has exactly one intersection (discriminant zero) and the largest-k slot none; midpoints are exact decimals. Agree with the tiers.
* **algebraic_fractions:** correct after findings 5 and 6; every "fully simplified" key is in lowest terms (the round trip types the key back with the form). Agree.
* **algebraic_proof:** the ordered proofs are valid and their prerequisites right (the two expansions of the difference of squares are independent, and for (n + 2)^2 - (n - 2)^2 step 2 is independent, step 3 needs 1 and 2, step 4 needs 3; the other chains are strict and read naturally). Distractors are plausible slips. Few different questions (the letter n, m or k, and a in two slots), which is normal for proof items. Counterexample: see finding 4.
* **functions:** correct after finding 1. Agree with the tiers.
* **graphical_simultaneous_equations:** the drawings match the keys (the `gsim_*` solvers read the recorded drawing) and, after finding 2, every value to be read is on a grid line. The lines are drawn past the plotting area at the edges (an older helper behaviour, left).
* **equations_inequalities:** the linear iteration is notation practice (it diverges) and fits I; the reciprocal iteration always converges to the positive root of x^2 - ax - b = 0 (|g'(x)| < 1 there) and fits D; the change-of-sign cubic x^3 + px - k is strictly increasing, so the root is unique, with f(1) < 0 < f(3) and f(2) never 0.

### 20.3 The "fully simplified" checker change

Narrowly scoped: the lowest-terms rule runs only in `_check_general_algebraic_fraction` and only when the stored problem's `answer_form` is `simplified`. A scan of every GCSE maths slot (3 seeds) found that form on an `algebraic_fraction` key only in the 8 batch B fraction slots; no other subject or level sets it, the older algebraic fraction slots ask "Simplify fully" with no form (they still accept an unsimplified equal fraction: a pre-existing gap, see 20.7), and every route passes the form from the stored problem only. The unit test now also checks that equal answers already in lowest terms but written another way stay right (6(x + 1) over 5, -(x - 11) over (x + 1)(x + 4), 4 - x over -x - 3, -3 over -4), that a wrong value gets no form message, and that with no form asked (or another form) the same entries are right as before. A decimal top or bottom (1.5 over 2) is left to the value check, as before.

### 20.4 The deep-run unit round-trip failure

`forms._numeric_parts` decided whether a `number_fields` key is numeric with `parse_num`, which reads a trailing unit, so the algebraic field `-2p` parsed as "minus 2 pence". The question prints 180°, so the harness typed `-2p%` as a "wrong unit" and expected the unit message. The app passes the problem's `answer_field_types` (`algebraic`, `algebraic`) and refuses `-2p%` with "Not quite"; only a direct call with no field types reaches the keyword fallback that accepts it. So the expectation was wrong, not the checker: a field with a letter is now not a number for the unit round trip. A fixed-text self-test (`check_unit_variant_cases`) guards it in the default run (mutation F1), with a positive control so the guard cannot widen silently. `--deep --seed 7000` and `--deep --seed 9100` both pass (20.6).

### 20.5 Hints

* Sampled all 22 batch B rules on 30 generated questions each with the key ±1, doubled, halved, negated and every printed number: no message named the wrong cause. Two near-miss overlaps are accepted (xy = 6 typed as 5 = x + y; a non-monic minimum of 4 typed as its x-value 3).
* **Coverage restored honestly: 690 of 1,146 slots (60.2%) can produce a topic hint** (686 before), so `TOPIC_FLOOR_SHARE` is back to 0.600. Seven new rules on five slots, each with a hand-worked unit row, the same contract as section 28 (TRUTH rebuilds the key, `_apart`, echo only for a printed-number slip). Four slots are newly counted; `fn_f_negative_input` was already counted through the `fn_eval` task's question parser (family `gr_subst`, whose one applicable rule reads 5x at x = -1 as 5 - 1), and keeps that slip as `fn.neg_input_implied` beside the new sign slip, so nothing is lost:
  * `qsim.sub_signs_kept` (existing family `qsim_sub_coeffs`): the terms moved across without changing sign; the existing message `alg.sign_moved` (already allowed for sign-only pair slips).
  * `fn.neg_input_sign` (`fn_f_negative_input`): 12 - 5x at x = -2 typed as 2; `fn.neg_input_implied`: typed as 9 (existing message `sub.implied_multiply`).
  * `cts.min_read_x_value` (`cts_f_read_min_value`, echo) and `cts.min_nonmonic_x_value`: the x-value of the minimum typed for the least value.
  * `cts.min_nonmonic_a_missed` (`cts_d_min_non_monic`): 2x^2 + 12x + 25 typed as 16 (the 9 taken away without multiplying by 2).
  * `ap.bracket_second_term` (`ap_f_simplify_to_constant`, echo): 4(n + 6) - 4n typed as 6.
  Four of these slots were `@verifies('alg')` tasks, which carry no answer record (a slot with both a task and a `record()` captures two records and gets none), so they now record a family instead, with an independent solver each in `solvers_variety_b.py` (`cts_min_read`, `cts_min_nonmonic`, `ap_bracket_const`, `fn_neg_input`); their output is byte-identical. Four new messages pass the voice lint; Appendix A of `docs/ZORP_CHARM.md` was regenerated.
* Combined coverage stays 881 of 1,146 (76.9%; floor 0.765): the five slots already had a generic hint. Going back to 0.770 needs 2 more slots with any hint: the candidates are the remaining `@verifies` slots with a natural slip (cross-multiplying the wrong way in `af_i_solve_cross_multiply`; the order of composition in `fn_i_composite_both_orders`), each needing the same conversion to a record family.

### 20.6 Runtime, drift, mutation tests and results

* **Runtime.** Interleaved runs of the default verification smoke on this machine (3 rounds each, alone): the pre-batch tree 36.2 / 36.8 / 37.5 s, batch B as built 42.3 / 41.6 / 41.6 s, after the review 39.5 / 37.4 / 38.0 s (means 36.8, 41.8 and 38.3 s). Two changes, no coverage lost: `t_simplify` puts the expression in lowest terms with `cancel(together())` (0.32 s against 2.24 s over the run's 322 questions, the same value and the same number of expanded terms every time) and falls back to `simplify()` whenever that form does not match the key, so a key passes exactly when it passed before; and the solver parser `expr()` caches the parse of a text (90% hits: a question's segments are parsed again by the checks and by the negative control). Single runs on this machine vary by up to 4 s, so compare interleaved runs.
* **Drift.** Every practice slot of the pre-batch tree (`/tmp/claude-0/pb_b_before`, 1,064 slots, 3 seeds, called directly by name, SVG id counters normalised): 3,192 of 3,192 outputs byte-identical after the review; the 246 others are the new slots. Through the topic wrappers the outputs at a fixed seed do differ, because the practice queue is now 7 long and `select_tier_variants` draws more random numbers before the named variant runs; that is a change of which numbers a variant sees, not of what it does.
* **Mutation tests** (on a copy of the tree; each file restored and compared byte for byte): see the table below.
* **Results**: see the table below.

| Mutation | Caught by |
|---|---|
| S1 the largest-k solver ignores the curve constant | verification smoke |
| S2 the negative-input solver adds m x | verification smoke |
| S3 the non-monic minimum solver drops a | verification smoke |
| S4 the bracket-constant solver multiplies only n | verification smoke |
| G1 the functions wrapper drops the answer form again | verification smoke (new expand rule); passed before this review |
| G2 the largest-k generator ignores c0 in its key | verification smoke |
| F1 the number-field letter guard removed | verification smoke (`check_unit_variant_cases`); before, only `--deep --seed 7000` |
| C1 a common number factor accepted under "fully simplified" | answer check smoke and verification smoke (round trip) |
| C2 the lowest-terms rule applied with no form asked | answer check smoke |
| C3 a common bracket accepted | answer check smoke |
| H1 the signs-kept slip off by one | hints smoke unit table |
| H2 the a-not-multiplied slip without the a | hints smoke unit table |
| H3 the negative-input slip | hints smoke unit table |
| H4 the least-value TRUTH off by one | hints smoke unit table and rule reach |

The cheap form in `t_simplify` is not a mutation target: a broken fast path falls back to `simplify()`, which keeps the verdict right (it only costs time).

| Run | Result |
|---|---|
| Verification smoke, default, alone | passes; 42.7 s in a single run (machine noise; interleaved means above: 38.3 s against 36.8 s for the pre-batch tree and 41.8 s for batch B as built) |
| Verification `--deep --seed 7000` | passes, 293.5 s (beside another job) |
| Verification `--deep --seed 9100` (new offset) | passes, 298.6 s (beside the mutation runs) |
| Hints smoke / ladder / MCQ notes | 18.1 s / 3.0 s / 1.6 s, pass (690 topic and 881 combined slots of 1,146; 422 topic rules, 499 topic unit rows; mutation 669 of 669 topic and 307 of 307 pair, box and expression perturbations caught) |
| Retired compat / correctness / answer check / MCQ letter / voice | 2.4 s / 16.4 s / 6.3 s / 2.8 s / 7.3 s, pass |
| `ruff check .` | clean |
| Full suite | 109 of 109 smoke tests pass (`/tmp/claude-0/suite_v3b_review.log`, run on the final tree) |

### 20.7 Deferred

* The older gsim reading slots have the same off-grid problem as finding 2 (the shared helper keeps `minor_grid` off for them so their output is unchanged); turning it on for all of them is one argument per call and a drift note.
* The older algebraic fraction slots that say "Simplify fully" carry no `simplified` form, so an equal unsimplified fraction is accepted there; giving them the form changes existing slots' behaviour and needs its own drift note.
* Combined hint coverage (76.9%) below the old 0.770 floor: see 20.5.
* Six older slots have the same `<strong>` inside `\( ... \)` as finding 3 (`gcse_neg_powers`, `gcse_surds_practice_surd_equation`, `_sim_i_substitution_rearrange`, `_ap_f_expand_consecutive`, `_ap_i_square_difference`, `_ap_i_identity_expand`; found by a scan of every slot, 2 seeds); left so their output stays byte-identical, worth one pass with a drift note.
* The untyped `number_fields` fallback (a direct call with no field types) reads an algebraic field with the keyword checker, which ignores signs and symbols (`2p%` for `-2p`); every route passes the field types, so pupils never meet it.


## 21. Build notes: Phase 3 batch C1, new content (2026-10-28, not committed)

Batch C1 adds the section 4 gap rows for statistics, probability, graphs, trigonometry and the P2 proportion rows of ratio_proportion, brings the six tiers that were still under 9 strict kinds (changing_the_subject F, pythagoras F, I and D, statistics F and D) to 9 or more, and replaces 22 echoes of foundational and intermediate kinds that sat in the difficult tiers of statistics, probability, graphs and ratio_proportion with harder kinds. Same standard as batches A and B (sections 17 and 19): every slot is generated by code, has a worked solution and a hint, a correct answer type and form flag, a `record()` family with an independent solver in `scripts/gcse_verify/solvers_variety_c.py`, and goes through the checker round trip. Nothing is committed.

### 21.1 New slots (47)

Code: `generators/gcse/maths_variety_c.py` (42 slots: statistics, probability, graphs, ratio and trigonometry; the topic modules import it lazily when they build their pools), `generators/gcse/maths_pythagoras.py` (4) and `generators/gcse/changing_the_subject.py` (1). The drawn questions (tables, stem and leaf diagrams, sample space tables, frequency trees, frequency polygons, a time series, velocity-time, exponential and trigonometric graphs) are drawn with `models.svg_kit` roots and CSS-variable colours, so they follow the light and dark themes, and were checked at 320 px and 700 px in both. Tables are SVG tables (bordered, readable at 320 px) rather than HTML tables, so the verification readers can read the cells back from the drawing. A star marks a slot that can produce a topic hint (41 of the 47, 87.2%, measured by the hints smoke over its seeds).

**statistics** (16 new; F 8 to 12, I 10 to 15, D 8 to 9)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_stats_two_way_read` * | The two-way table shows information about some pets, sorted by type of pet and colour. [table] How many pets are brown altogether? |
| F | `gcse_stats_stem_leaf_median` * | The stem and leaf diagram shows the marks of some pupils in a test. [diagram, key] Work out the median of the data. |
| F | `gcse_stats_mode_from_table` * | The table shows the number of goals scored in 50 matches. [table] Write down the mode. |
| F | `gcse_stats_sample_proportion` * | In a random sample of 40 pupils from a school, 28 walk to school. There are 1500 pupils in the school altogether. Estimate how many of them walk to school. |
| I | `gcse_stats_two_way_complete` * | The two-way table shows information about some pupils, sorted by year group and way of travelling to school. Three of the values are missing. [table with totals] Work out the values of a, b and c. |
| I | `gcse_stats_median_from_table` * | The table shows the number of pets owned by 35 pupils. [table] Find the median. |
| I | `gcse_stats_freq_polygon_read` * | The frequency polygon shows the heights of some plants. The classes are 20 < h ≤ 30, ... [graph] How many plants were there altogether? |
| I | `gcse_stats_missing_value_mean` * | The mean of 5 numbers is 29. 4 of the numbers are 18, 35, 33 and 17. Work out the other number. |
| I | `gcse_stats_time_series_mean` * | The time series graph shows the visitors to a museum, in thousands, for each quarter of 2024 and 2025. [graph] Work out the mean quarterly value for 2025. |
| D | `gcse_stats_capture_recapture` * | A scientist ... catches 60 fish, tags them and releases them. The next week she catches 30 fish and finds that 5 of them are tagged. Estimate the number of fish in the lake. |
| D | `gcse_stats_combined_mean` * | Class A has 30 pupils and their mean mark is 73. Class B has 20 pupils and their mean mark is 68. Work out the mean mark of all 50 pupils together. |
| D | `gcse_stats_missing_frequency_mean` | The table shows the number of goals scored in some matches. One frequency is unknown. [table with x] The mean number of goals scored is 1.5. Work out the value of x. |
| D | `gcse_stats_median_class` | The table shows the times, t minutes, taken by 29 runners. [grouped table] Which class interval contains the median? (choice) |
| D | `gcse_stats_stem_leaf_iqr` * | The stem and leaf diagram shows the ages, in years, of some people at a gym. [diagram] Work out the interquartile range of the data. |
| D | `gcse_stats_freq_polygon_mean` * | The frequency polygon shows the masses of some parcels. The classes are 20 < m ≤ 40, ... [graph] Work out an estimate for the mean. |
| D | `gcse_stats_two_way_percent` * | [two-way table with totals] What percentage of the Year 11 pupils come by car? |

**probability** (10 new; F 14 to 16, I 15 to 18, D 16 to 16)

| Tier | Slot | Example question |
|---|---|---|
| F | `gcse_prob_spinner_sum_space` * | Spinner A is numbered 1 to 4 and spinner B is numbered 1 to 3 ... The sample space diagram shows every possible total. [table] Find the probability that the total is more than 4. |
| F | `gcse_prob_frequency_tree_complete` * | The frequency tree shows information about 128 pupils. 50 of them are boys. Of the boys, 24 walk to school. Of the girls, 37 do not walk. [tree] Work out the values of a, b and c. |
| I | `gcse_prob_two_dice_sum` * | Two fair six-sided dice are rolled and the scores are added together. [6 by 6 table] Find the probability that the total is more than 8. |
| I | `gcse_prob_two_way_table` * | [two-way table with totals] One of the members is chosen at random. Find the probability that this member meets on Monday. |
| I | `gcse_prob_venn_union` * | In a school survey of 44 people, A is the set of people who play football and B ... [Venn diagram] One of the 44 people is chosen at random. Find P(A ∪ B). |
| D | `gcse_prob_two_dice_product` * | Two fair six-sided dice are rolled and the two scores are multiplied together. [table] Find the probability that the product is a square number. |
| D | `gcse_prob_frequency_tree_conditional` * | [completed tree] One of the people who are vegetarian is chosen at random. Find the probability that this person is one of the children. |
| D | `gcse_prob_two_way_conditional` * | [two-way table] One of the girls is chosen at random. Find the probability that this pupil chose art. |
| D | `gcse_prob_venn_set_notation` * | [Venn diagram] One of the 48 people is chosen at random. Find P(A' ∩ B). (also A', A ∩ B', (A ∪ B)') |
| D | `gcse_prob_venn_conditional` * | [Venn diagram] One of the people who play hockey is chosen at random. Find the probability that this person also plays football. |

**graphs** (8 new; I 12 to 14, D 12 to 12)

| Tier | Slot | Example question |
|---|---|---|
| I | `gcse_gra_perpendicular_gradient` | Line L has the equation y = -4x - 2. Write down the gradient of a line that is perpendicular to L. |
| I | `gcse_gra_vt_acceleration` * | The velocity-time graph shows the first 16 seconds of the journey of a cyclist. [graph] Work out the acceleration of the cyclist during the first 8 seconds. |
| D | `gcse_gra_perpendicular_line` | Line L has the equation y = ½x + 4. Find the equation of the line that is perpendicular to L and passes through the point (1, -5). Give your answer in the form y = mx + c. |
| D | `gcse_gra_circle_equation` * | A circle has centre O, the origin, and passes through the point (9, -7). The equation of the circle is x² + y² = k. Work out the value of k. (also: write down the radius of x² + y² = 25) |
| D | `gcse_gra_circle_tangent` | The circle x² + y² = 10 has centre O. The point P(3, 1) lies on the circle. Find the equation of the tangent to the circle at P. |
| D | `gcse_gra_vt_distance` * | The velocity-time graph shows the journey of a car, which lasts 16 seconds. [graph] Work out the total distance travelled by the car. |
| D | `gcse_gra_transformation_point` * | The point M(-7, 1) is the minimum point of the curve y = f(x). Write down the coordinates of the minimum point on the curve y = f(x + 4). (also f(x) ± a, f(-x), and -f(x), which asks for the maximum point of -f(x) when M is a minimum) |
| D | `gcse_gra_exponential_read` * | The graph shows the curve y = a × b^x ... The marked points have whole-number coordinates. [graph] Use the graph to find the values of a and b. (growth, and decay with b = 1/2, 1/3 or 1/4) |

**ratio_proportion** (5 new, all D; D stays at 14 kinds)

| Tier | Slot | Example question |
|---|---|---|
| D | `gcse_ratio_proportional_cube` * | y is directly proportional to the cube of x. When x = 2, y = 40. Find the value of y when x = 3. (or find x from y) |
| D | `gcse_ratio_proportional_root` * | y is directly proportional to the square root of x. When x = 36, y = 24. Find the value of y when x = 100. |
| D | `gcse_ratio_inverse_square` * | y is inversely proportional to the square of x. When x = 5, y = 4. Find the positive value of x when y = 25. |
| D | `gcse_ratio_change_after_adding` * | A bag contains red counters and blue counters in the ratio 3 : 5. 12 more red counters are put in the bag. The ratio of red to blue counters is now 1 : 1. How many blue counters are in the bag? |
| D | `gcse_ratio_recipe_limiting` * | A recipe for 12 cakes needs 100 g of flour and 4 eggs. Sam has 350 g of flour and 12 eggs. What is the greatest number of cakes Sam can make? |

**trigonometry** (3 new; I 10 to 12, D 9 to 10)

| Tier | Slot | Example question |
|---|---|---|
| I | `gcse_trig_graph_read` * | The graph shows y = sin x for 0° ≤ x ≤ 360°. [graph] Use the graph to find the value of x, where 90° ≤ x ≤ 210°, for which sin x = 0.5. |
| I | `gcse_trig_graph_feature` | The graph shows y = cos x for 0° ≤ x ≤ 360°. [graph] Write down the coordinates of the point where the graph crosses the x-axis between 180° and 360°. |
| D | `gcse_trig_solve_two_solutions` * | Solve tan x = 2.1 for 0° ≤ x ≤ 360°. Give both solutions, correct to 1 decimal place. |

**pythagoras** (4 new; 7/8/8 to 9/9/9) and **changing_the_subject** (1 new; F 8 to 9)

| Tier | Slot | Example question |
|---|---|---|
| F | `_py_f9_ladder_height` * | A ladder 10 m long leans against a vertical wall. The foot of the ladder is 8 m from the wall. How far up the wall does the ladder reach? (or a zip wire's ground distance) |
| F | `_py_f10_rhombus_side` * | The diagonals of a rhombus are 12 cm and 16 cm long. The diagonals cross at right angles and cut each other in half. Work out the length of one side of the rhombus. |
| I | `_py_i9_square_area_from_diagonal` * | The diagonal of a square is 10 cm long. Work out the area of the square. |
| D | `_py_d9_algebraic_sides` * | The two shorter sides of a right-angled triangle are x cm and (x + 7) cm. The hypotenuse is (x + 8) cm. Form an equation and find the value of x. |
| F | `_cts_f_subtracted_subject` * | Make t the subject of the formula y = 16 − 4t. |

The six slots without a topic rule: the two line equations (`linear_equation` answers carry no record), `gcse_gra_perpendicular_gradient` (its two slips, the sign changed alone and the fraction flipped alone, are exactly what the generic sign and reciprocal lines say, so a topic rule would always be silent), the choice slot `gcse_stats_median_class`, `gcse_trig_graph_feature` (a coordinate pair whose only natural slip is the generic swap) and `gcse_stats_missing_frequency_mean` (the slip of leaving x out of the total frequency gives a whole number too rarely to carry a rule). `_cts_f_subtracted_subject` has no family of its own: the existing rearrange expression rules of `misconception_cd.py` read its formula. `gcse_prob_two_way_table` and `gcse_stats_freq_polygon_read` carried rules only on some draws until `prob.two_way_one_cell` (one cell typed for a group total) and `stats.polygon_peak_only` (the tallest frequency typed for the total) were added.

### 21.2 Replaced echoes (22 names retired, all in difficult tiers)

Each retired wrapper stays defined, out of the pools, in `register.RETIRED` with the new slot that replaced it (Rule 1 of section 3; the retired compat smoke lists 99 names). Three older entries that pointed at a now-retired wrapper (`_stats_diff_10`, `_12`, `_14`, `_ratio_diff_18`) point at the new slots.

| Topic | Retired from D (the kind it echoed) | Replaced by |
|---|---|---|
| statistics | `_stats_diff_01` (estimated mean, I), `_03` (compare distributions, I), `_04` (line of best fit, I), `_06` (frequency-table mean, I), `_07` (pie angle, F and I), `_08` (box plot IQR, I) | `gcse_stats_freq_polygon_mean`, `_combined_mean`, `_capture_recapture`, `_missing_frequency_mean`, `_two_way_percent`, `_stem_leaf_iqr` (+ `_median_class`) |
| probability | `_prob_diff_09` (relative frequency), `_10` (expected frequency), `_11` (one bag), `_12` (two coins), `_15` (complement) | `gcse_prob_two_dice_product`, `_frequency_tree_conditional`, `_two_way_conditional`, `_venn_set_notation`, `_venn_conditional` |
| graphs | `_gra_diff_03` (root from a factorised quadratic), `_05` (reciprocal value), `_07` (midpoint), `_08` (two simple lines meet), `_09` (equation from gradient and intercept), `_14` (speed from a distance-time graph) | `gcse_gra_circle_tangent`, `_exponential_read`, `_perpendicular_line`, `_circle_equation`, `_transformation_point`, `_vt_distance` |
| ratio_proportion | `_ratio_diff_06` (density-style rate), `_09` (recipe scaling), `_10` (three-part sharing), `_11` (unit conversion), `_15` (best buy) | `gcse_ratio_inverse_square`, `_recipe_limiting`, `_change_after_adding`, `_proportional_cube`, `_proportional_root` |

Tier echoes fall from 63 slots to 41. The echoes that remain in difficult tiers (statistics none; probability `_prob_diff_01`, `_02`, `_03`, `_07`, `_08`, `_14`; graphs `_gra_diff_12`; ratio `_ratio_diff_01`, `_14`, `_16`, `_17`, `_19`) are kept because each difficult tier's floor (section 7 ratchet) may only rise: replacing them needs one more harder kind each (section 21.7).

### 21.3 Metrics, before and after (`--variety-report` and the default run)

| Measure | Before | After |
|---|---|---|
| Practice slots / strict kinds | 1,146 / 1,146 | 1,171 / 1,171 (47 new, 22 retired) |
| Tiers below 7 kinds / below 9 kinds | 0 / 6 | 0 / 0 |
| Mean queue-repeat share | 0.0% | 0.0% (ceiling stays 0.005) |
| Tier echoes | 63 | 41 |
| Fixed variants (section 2 measure) | 81 | 82 (`FIXED_VARIANTS` unchanged; see 21.6) |
| Topic hint slots | 690 of 1,146 (60.2%) | 715 of 1,171 (61.1%); `TOPIC_FLOOR_SHARE` 0.600 to 0.605 |
| Combined hint slots | 881 (76.9%) | 908 (77.5%); `COMBINED_FLOOR_SHARE` 0.765 to 0.770 |
| Verification smoke, alone | 38 to 43 s (batch B review; the pre-batch-B tree measures 39.2 s today) | 40 to 44 s over four timings (45.4 s before the `plain()` cache, see 21.5) |
| Hints smoke | 15 to 18 s | 17 to 19 s |

Strict kinds per tier (F / I / D), `VARIETY_FLOORS['tier_kinds']` raised to the measured values: changing_the_subject 9 / 10 / 10 (was 8 / 10 / 10); graphs 10 / 14 / 12 (10 / 12 / 12); probability 16 / 18 / 16 (14 / 15 / 16); pythagoras 9 / 9 / 9 (7 / 8 / 8); ratio_proportion 16 / 17 / 14 (unchanged); statistics 12 / 15 / 9 (8 / 10 / 8); trigonometry 10 / 12 / 10 (10 / 10 / 9).

### 21.4 Verification

* Solvers: 37 record families in `scripts/gcse_verify/solvers_variety_c.py` (34 for the new module, 3 for Pythagoras; the ladder slot reuses `pyth_leg` and the changing-the-subject slot is an `alg` rearrange task), with 19 `@diagram` checks, one for every drawn question. The readers calibrate each axis from the tick labels (class `tx` and `ty` text elements; every label must sit on the line through the end labels, so a label changed by one unit makes the axis unreadable), read the marked points, the polyline and the table cells (class `cell`, `rowhead`, `leaves`, `space`, `node`) and compare them with the recorded inputs, so a drawing and its key cannot disagree; the smoke's damaged-drawing negative control catches 39 of 39 families. The sine and cosine graphs are checked point by point against the function, the sample space tables cell by cell, the frequency trees box by box.
* Line equations (`gr_perp_line`, `gr_tangent`) are `problem=True` solvers that judge the `linear_equation` key as a tuple; the median class is a `Pick` on the option text; `trig_solve_k` returns `Approx` values against the stated 1 decimal place.
* Round trip: number, fraction (probability form), number_pair, number_fields, linear_equation and choice; the stated accuracy of the trig solutions; the typed units of the v-t slots (m/s², m).
* The harness walks `random.choice` over a list of pairs row by row, so a rejection loop that draws from such a list by `random.choice` never ends under the harness (found on `gcse_prob_two_dice_product`): the sample space and transformation loops index with `random.randrange` instead.
* Drift: every pre-batch slot is byte-identical when called directly (3 seeds, SVG ids normalised; the wrappers' new fallbacks only act on payload types no older slot returns).

### 21.5 Runtime

The smoke rose to 45.4 s alone (the pre-batch-B tree measures 39.2 s on this machine today, the batch B tree about 41 s): the new drawn questions are 6 to 10 KB of SVG and the smoke's text passes (`latex.plain`) ran a dozen times over each. `plain()` is now an LRU cache (4,096 entries) and the retired check builds its tier map in one pass instead of pairwise, which brought one timing of the default run to 40.1 s alone; three later timings the same afternoon gave 43 to 44 s with the machine otherwise idle (the batch B notes record 43.1 s and about 41 s for that tree on this machine), so the batch is at parity with the tree before it despite 25 more slots and 19 drawing checks. The hints smoke takes 17 to 19 s. `--deep --seed 4200` (started after the last generator change) passes in 301 s.

### 21.6 Fixed variants

The section 2 measure counts 82 fixed slots (81 before): `gcse_gra_exponential_read` asks one stem whose variety is in the drawing (23 curves), as `gcse_surds_identify_irrational` does in its options. `register.FIXED_VARIANTS` is unchanged; `--deep --seed 4200` lists no slot that was fixed on every seed.

### 21.7 Deferred

* Eleven echoes into difficult tiers remain (21.2); each needs one more harder kind in its tier before it can leave, because the tier floors only rise.
* `gcse_gra_perpendicular_line` and `_circle_tangent` keep whole-number gradients and intercepts because the `linear_equation` checker reads decimals only (no `-3/4x + 25/4`, no `3x + 4y = 25`); widening that checker is its own change.
* The remaining graphs I echoes of F kinds (gradient, equation, parallel gradient, speed, midpoint, reciprocal, correlation) are untouched: the plan's target of at most one F-I echo per tier is Phase 3 work beyond this batch.
* `gcse_stats_missing_frequency_mean` has generic hints only (21.1).

## 22. Phase 3 batch C1 review notes (2026-10-28, independent review, nothing committed)

Reviewed against sections 4, 7, 10, 11, 14, 16, 18, 20 and 21, `docs/GCSE_MATHS_HINTS.md` section 30, the "Phase 3 batch C1" note of `docs/GCSE_MATHS_VERIFICATION.md` and the code, as a GCSE maths teacher (AQA 8300 / Edexcel 1MA1) and as a code reviewer. Every one of the 47 new generators was read over 30 seeds through its topic wrapper (question, worked solution, hint, marks, key, answer type, form and format hint), then scanned by script over 300 seeds for distinct questions, keys equal to a printed number, cosmetic working ("1 × 50") and slow draws. The 31 drawn slots were rendered in the real practice page (the app running locally with `PB_TESTING=1 PB_ALLOW_DEV_SECRET=1 CORS_ORIGINS=https://app.example.com`, the question injected into the page's own question container so the page CSS, CSP and theme apply) at 1280 px and 360 px, light and dark, two seeds each: 248 screenshots in `/mnt/user-data/outputs/variety_c1_review/` with `report.json` (clipped text, inline `style=` inside the drawing, console errors, CSP violations). Everything below was fixed in the tree unless it says otherwise.

### 22.1 Findings

| # | Severity | Finding | Outcome |
|---|---|---|---|
| 1 | High | **y = −f(x) asked for a point the pupil is not given.** `gcse_gra_transformation_point` said "P(−2, 5) is the maximum point of y = f(x). Write down the coordinates of the maximum point on y = −f(x)" and keyed the image (−2, −5), which is the *minimum* of −f(x); the maximum of −f(x) is the image of f's minimum, which is unknown. About one draw in nine. | Fixed: for −f(x) the question asks for the opposite feature ("the minimum point on y = −f(x)"), the solution says why, and the reflections get their own hint ("a minus sign outside f reflects in the x-axis; inside the bracket, in the y-axis"). The record and the hint rules are unchanged. |
| 2 | High | **The median class was ambiguous in 5 of 30 draws.** `gcse_stats_median_class` used the (n + 1)/2 rule; with an even n and a running total equal to n/2 (14, 26, 39, 52 for n = 52) the n/2-th value ends one class and the (n/2 + 1)-th starts the next, so the n/2 rule that the boards use for grouped data gives the other class, and a pupil taught that rule was marked wrong. The solver used the same rule, so the smoke could not see it. | Fixed: such draws are rejected (both rules then name the same class) and the solver refuses them (`Cannot`, mutation G1 confirms the smoke would now fail on the old generator); the question now says "the times taken by 29 runners" instead of "There are 29 values". The median can now fall in any of the four classes (it was always the second or third). |
| 3 | High | **Wrong units were accepted on the drawn questions.** `answer_units.question_plain_text` cut the stored question to 6,000 characters *before* dropping the markup; a velocity-time graph is 8 to 11 KB of SVG ahead of "Work out the acceleration", so the unit model never read the ask and "2.5 m/s", "2.5 m", "130 km" and "58 cm" (for a mean in minutes) all passed. Eleven older drawn slots (the gsim graphs, a vectors grid, five probability trees) had the same gap; the ten C1 drawn slots over 6,000 characters added the first ones where the unit is the point. | Fixed in `answer_units`: the tags are dropped first (raw bound 120,000 characters, then 6,000 of visible text); a test in the answer check smoke keeps it (mutation U1). The two velocity-time slots also name their unit in the box hint ("Enter the acceleration in m/s²", "Enter the distance in metres"), which `problem_extra_from_graded_answer` now reads from a number payload's `format_hint` (no older number payload carries one), so "2.5 m/s" is refused with the unit message and "130 km" with "the question asks for the answer in m". |
| 4 | Medium | **Drawn labels cut or colliding.** The frequency-table headings "Number of goals scored" and "Number of matches" ran into each other at every width (fixed 150 px and 110 px columns); "First \ Second" overflowed the sample space corner; the pythagoras triangle helper cut "x + 1 cm" at the left edge and drew "x + 2 cm" across the hypotenuse; "? cm" and "s cm" lost their first pixels (the helper's frame is tight for the older two-character labels too, see 22.7). | Fixed: short table headings ("Goals scored", "Frequency"); a 112 px corner; `_pyth_tri_svg` moves its frame and the hypotenuse label out for labels longer than two characters (its output for the older slots is byte-identical); `_rect_diag_svg` takes a `pad_left` for the square. |
| 5 | Medium | **The ladder drawing said cm for a ladder in metres.** `_py_f9_ladder_height` passed its metres to a helper that writes "cm" after every label (the older `_py_f5_ladder_wall` does the same, 22.7). | Fixed: `_pyth_tri_svg(..., unit='m')`. |
| 6 | Medium | **Off-grid points on the exponential graph.** (1, 4) put the y-intercept a = 1 between faint lines drawn every 2; (2, 4) reached y = 128 with lines 3.5 px apart; (81, 3) put 81 and 27 off the grid. | Fixed: those three cases are out; every remaining case has its points at x = 0, 1 and 2 on a grid line. |
| 7 | Medium | **The time series was noise.** Eight values drawn at random, so ice cream sales fell in the summer as often as they rose. | Fixed: a seasonal shape per context (ice cream and museum visitors peak in Q3, gas in Q1 and Q4) with a small trend and ±1 noise; "bookings at a hotel, in tens" is now in hundreds. |
| 8 | Medium | **A 1 d.p. guard that guarded the wrong thing.** `gcse_trig_solve_two_solutions` rejected a first solution within 0.003° of a 1 d.p. value, which is harmless, and kept one within 0.0005° of a rounding boundary (sin x = 0.57 gives 34.7502°, cos x = 0.57 gives 55.2498°), where a display rounded to 2 d.p. first gives the other neighbour. | Fixed: the guard now rejects a first solution within 0.003 of xx.x5. (The checker takes the key to 1 d.p. only, 64.47 for 64.5 is refused, as for every older "correct to 1 d.p." slot.) |
| 9 | Medium | **Stem and leaf leaves were centred.** The leaves of a stem and leaf diagram sit against the stem so the row lengths show the shape; the table drew them centred in a 230 px column. | Fixed: left-aligned leaves and heading (`_svg_table(left=True)`). |
| 10 | Medium | **The rhombus drew the longer diagonal as the shorter line** (6 cm on the 190 px line, 8 cm on the 120 px one). | Fixed: the longer diagonal is always the horizontal one. |
| 11 | Low | Wording: "How many pupils are in the Boys row altogether?" (now "How many boys are there altogether?"); "The boys has 20 pupils" (now "There are 20 boys and their mean height is 145 cm"); "pets who are brown" (now "that"); "the number of goals scored for 50 matches" (now "in 50 matches", "owned by 35 pupils", "delivered to 18 houses"); "There is not enough eggs"; "0 people in each car" as a table value (cars start at 1). The perpendicular working wrote `-1 ÷ -1/2`; it now brackets a negative fraction, `-1 ÷ (−½)`, in TeX. | Fixed. |
| 12 | Low | Working lines "k = 1 × 100", "4 × 1³ = 4 × 1", "Lemon sweets: 1 × 50 = 50"; the inverse-square draw allowed y = 1 and the cube draw x = 1 (no cube to take). | Fixed (x, y ≥ 2 where the working would be trivial; `_times` writes "t = 50"). |
| 13 | Low | Hint coincidences: with A(4, 4) under f(x) + 6 the swapped pair (10, 4) is also the inside-outside slip; on the velocity-time graph the area of a sloping part (25 m) could equal the printed journey time (25 s), so a copied number got "That is the area under that part of the graph". | Fixed in the draws (x ≠ y; the three hint slips of a v-t draw may not equal a printed number). |
| 14 | Low | The hint message `gr.shift_wrong_way` said "f(x + a) moves the graph to the left, not the right" for both kinds, so a pupil who moved f(x − a) the wrong way read the wrong sentence. | Fixed: "The sign inside the bracket works the other way round. f(x + a) moves the graph left, f(x − a) moves it right." |
| 15 | Low | `gcse_gra_perpendicular_line` could key c = −c of the given line and `gcse_gra_transformation_point` could move a coordinate onto the other printed one (Q(−3, −7) under f(x + 4) gave (−7, −7)). | Fixed in the draws. |
| 16 | Low, not changed | `gcse_stats_sample_proportion` sampled 45 faulty bulbs of 60. | Faulty bulbs are now at most a quarter of the sample. |
| 17 | Low, not changed | The Venn diagrams carry the helper's captions ("A only", "A ∩ B", "Neither: 14"), which scaffold the set-notation question more than an exam diagram would; the older Venn slot uses the same helper. | Accepted (house style; a `captions=False` option on `svg_kit.venn2` is a small follow-up, 22.7). |
| 18 | Low, not changed | The frequency tree is 430 px wide, so a phone shows its branch labels at about 8 px (the older probability trees are 600 px wide and smaller still). | Narrowed from 470 px with 13 px labels; accepted. |

### 22.2 Verdicts by topic (as a GCSE teacher)

* **statistics:** correct in every draw after findings 2 and 7 to 11. F (read a two-way table, median or range from a stem and leaf, mode from a table, scale a sample) is Foundation; I (complete a two-way table, median from a frequency table, total from a frequency polygon, missing value from a mean, mean of a year from a time series) agrees. D: capture-recapture, combined mean, missing frequency from a mean, IQR from a stem and leaf and the estimated mean from a polygon are Higher work; the median class (grade 4 to 5) and the percentage of a group from a two-way table (grade 4) are the easiest items in that tier, kept because the tier needed nine kinds. The IQR uses the (n + 1)/4 positions with n = 11 or 15, so the quartiles are data values; the median questions keep n odd.
* **probability:** correct. The sample spaces count cells (7 of 36 for a square total; 20 of 36 for a product over 8); "more than" is strict and the solver reads the event words the generator prints. Frequency trees and two-way tables are consistent (the readers compare every box and cell); the conditional questions name the group the choice is made from, and the Venn questions state the size of the universal set. Agree with the tiers.
* **graphs:** correct after finding 1. The perpendicular gradient is −1/m with the fraction flipped; the perpendicular line and the tangent go through the given point (the tangent at (a, ±1) always has c = k, a true pattern, not a slip); the velocity-time distance is the trapezium, the acceleration positive and the deceleration asked as a deceleration; f(x + a) moves left; a and b are read at x = 0 and x = 1 and every needed point is on a grid line.
* **ratio_proportion:** correct. k is a whole number in every proportion slot and x is recoverable; the recipe question (grade 4) is light for the difficult tier.
* **trigonometry:** correct. The second solution follows the sin, cos and tan rules, the graph readings are at 30° or 90° multiples with a stated range holding exactly one solution, and the drawn curves are checked point by point.
* **pythagoras and changing_the_subject:** correct; every algebraic triangle has one positive root and a valid triangle, the rhombus halves its diagonals, the square's area is d²/2, and t = (16 − y)/4 is accepted as `(16 - y)/4`, `4 - y/4` and `-y/4 + 4` while `16 - y/4` and `(y - 16)/4` are refused.

### 22.3 Diagrams and the drawing checks

* 248 renders (31 drawn slots × 2 seeds × desktop and 360 px × light and dark): after the fixes, no clipped text, no inline `style=` inside a drawing (the `svg_kit` root's own width style is the house pattern), no console errors and no CSP violations. The only report line left is the rotated single-letter "y" axis label, which the box test counts as tiny (a false positive of the rotation).
* Every drawn question is also checked against the drawing by the smoke: the independent readers rebuild the tables, trees, polygons, series and curves from the SVG and compare them with the recorded inputs; the damaged-drawing negative control catches 39 of 39 families. Mutations D1 to D7 (22.6) confirm that a moved point, a tick label one unit off, a wrong box, a wrong cell, a cosine drawn for a sine and marks at the wrong height each fail the smoke, and that a check that accepts any drawing fails the negative control.
* The drawings are smaller: the font sits on one group and the grid lines share their stroke, so a 6 by 6 sample space is 7.2 KB instead of 11.0 KB and a velocity-time graph 6.7 KB instead of 10.6 KB (mean 4.3 KB over the drawn slots, from 6.5 KB).

### 22.4 Checker, wrappers and retired names

* Forms and units: probability fractions take the fraction, a decimal that is exact, 50% and an unsimplified equal fraction (and refuse a recurring decimal, the standing policy); the perpendicular gradient takes −4, −4/1, −8/2 and −4.0; the coordinate pairs take both boxes; the two trig solutions must be typed to 1 d.p. as asked; the line equations take `y = 2x - 7`, `y=2x-7`, `2x - 7` and `y = -7 + 2x` and refuse `y - 2x = -7` with the form message; a percentage takes the % sign; areas refuse a length unit; after finding 3 the velocity-time answers refuse m/s, m and km where they should.
* `problem_extra_from_graded_answer` fallbacks (statistics, ratio, graphs, trigonometry wrappers): they turn a `number` or `fraction` payload the wrapper's own branches do not handle into the usual `correct_answer_raw` / `answer_type` fields (before, such a payload left the problem with no key at all). 795 generations of every older slot of those topics through the wrappers never reach the fallback (instrumented), and the practice payload already carries `correct_answer_raw` for every graded slot, so nothing new is exposed; the lesson quiz payload strips it as before.
* The 22 retirements: each retired difficult slot was generated beside its claimed lower-tier twin and shares its template and record family (26 of 26 entries including the four repointed older ones), so no kind that was unique in its topic left; every retired name resolves through its topic's generator and gives byte-identical output to the pre-batch-B tree; the compat smoke lists 99 names and passes.
* The one-pass tier map is the same set as the pairwise comprehension; a `replaced_by` pointing at a slot of another tier is caught (mutation C2). The `plain()` cache is keyed on the text, so it cannot serve another question's text; a cache that did (mutation C1) and one that returned a cut text (C3) both fail the smoke.

### 22.5 Hints

* All 65 new rules were sampled on 30 generated questions of every C1 slot with the key ±1, doubled, halved, negated, its reciprocal and every printed number (and each field of a multi-field answer in turn): no message named a wrong cause except the two coincidences of finding 13 and the message of finding 14, all fixed. Rules that fire on a printed number do so only where the number is read from a drawing (the exponential a and b, the stem-and-leaf leaf, the mode's frequency), as section 30 says.
* **Coverage, honestly:** 715 of 1,171 slots (61.1%) can produce a topic hint on the default seed pair, but 709 to 713 (60.5% to 60.9%) on five other seed pairs (offsets 2, 4, 10, 20 and 50: the slots that flicker are rarely drawn variants in bidmas, decimals, vectors and `gcse_prob_two_dice_product`), so the 0.605 floor the batch set would fail on another pair by one slot. `TOPIC_FLOOR_SHARE` is back at 0.600 with the measured range noted beside it. The combined share is 906 to 908 of 1,171 (77.4% to 77.5%) on every pair, so `COMBINED_FLOOR_SHARE = 0.770` stands. 41 of the 47 new slots (40 on two of the pairs) carry a topic hint. The hints smoke was run twice after the review (same counts both times, 17 to 19 s).

### 22.6 Runtime, drift, mutation tests and results

* **Runtime.** Interleaved runs on this machine, alone: the pre-batch-B tree 38.8 / 39.5 / 37.5 s and this tree (batch B, batch C1 and this review) 40.2 / 39.9 / 39.4 s (means 38.6 and 39.8 s; a first pair run beside other jobs gave 43.2 s for both). Batch B alone measured 1.5 s over the pre-batch tree after its review, so C1 with the `plain()` cache, the one-pass tier map and the smaller drawings is at parity. A single run of the final tree alone: 38.9 s.
* **Drift.** Every practice slot of the pre-batch-B tree called directly (1,041 common slots, 3 seeds, SVG ids normalised): 0 differ; the 22 functions retired by C1: 0 differ. The pythagoras helpers took new keyword arguments with defaults that reproduce the old output exactly.
* **Mutation tests** (on a copy of the tree, each file restored and its checksum compared with the copy's pre-mutation content):

| Mutation | Caught by |
|---|---|
| S1 the median-class solver names the class before | verification smoke |
| S2 the sample-space solver reads "more than" as at least | verification smoke |
| S3 the tangent solver uses the radius gradient | verification smoke |
| S4 the IQR solver uses n/4 positions | verification smoke |
| S5 the power-proportion solver ignores the power | verification smoke |
| S6 the velocity-time solver takes the whole rectangle | verification smoke |
| D1 the polygon drawing check accepts any drawing | verification smoke (damaged-drawing negative control) |
| D2 polygon points drawn at the class ends | verification smoke |
| D3 a y tick label one unit off | verification smoke (axis unreadable) |
| D4 a frequency tree box one too many | verification smoke |
| D5 a two-way table cell drawn wrong | verification smoke |
| D6 a cosine curve drawn for a sine | verification smoke |
| D7 exponential marks at the wrong height | verification smoke |
| K1 combined mean key off by one | verification smoke |
| K2 trig second solution off by a tenth | verification smoke (stated accuracy) |
| K3 algebraic sides key is the other root | verification smoke |
| K4 f(x + a) moved right in the generator | verification smoke |
| K5 the perpendicular line keyed with the wrong gradient | verification smoke |
| C1 `plain()` returns the previous call's text | verification smoke |
| C2 a retired name repointed to a slot of another tier | verification smoke (retired) |
| C3 `plain()` returns a cut text | verification smoke |
| G1 the median class drawn without the ambiguity guard | verification smoke (the solver refuses the draw) |
| H1 the mean-of-means slip divides by three | hints smoke unit table |
| H2 the shift-wrong-way slip doubled | hints smoke unit table |
| H3 the recapture TRUTH upside down | hints smoke truth guard and unit table |
| U1 the unit model cuts the raw question again | answer check smoke |

| Run | Result |
|---|---|
| Verification smoke, default, alone | passes; 38.0 s (36.3 s inside the run), 20,198 practice questions, 5,210 round trips, 99 retired names, damaged drawings 39/39 |
| Verification `--deep --seed 5300` (new offset) | passes, 264.8 s (234,200 practice questions, 21,274 round trips; run beside the other smokes); no slot fixed on every seed |
| Hints smoke, twice | 16.4 s and 15.8 s, pass; 715 topic and 908 combined slots of 1,171 both times (477 topic rules; mutation 750 of 750 topic and 322 of 322 pair, box and expression perturbations caught) |
| Hints ladder / MCQ notes | 2.5 s / 1.5 s, pass |
| Retired compat / correctness / answer check / MCQ letter / voice | 2.0 s / 15.1 s / 6.2 s / 2.1 s / 6.5 s, pass (the correctness smoke caught a working line this review broke on the way, "2 × 60 = 120 + 3 × 60 = 180", fixed) |
| `ruff check .` | clean |
| Full suite | 109 of 109 smoke tests pass (`/tmp/claude-0/suite_v3c1_review.log`, run on the final tree) |

### 22.7 Deferred

* `_py_f5_ladder_wall` (older) draws "cm" labels for a ladder given in metres, and the older pythagoras drawings lose the first two to six pixels of "12 cm" at the left edge of their frame; the helper now takes `unit=` and a wider frame for long labels, so each is a one-argument change with a drift note.
* The Venn captions (finding 17) and the width of tree diagrams (finding 18).
* The median class and the recipe limit are light for a difficult tier; a harder statistics kind (a histogram with unequal classes, a cumulative frequency reading) and a harder ratio kind (a ratio given as a difference and a change at once) would let them move down when those tiers have nine kinds without them.
* The number box takes a "correct to 1 d.p." answer only to 1 d.p. (64.47 for 64.5 is refused), app-wide; accepting a more precise answer that rounds to the key is a checker policy question.

## 23. Build notes: Phase 3 batch C2, the whole-pool draw and the last echoes (2026-10-28, not committed)

Batch C2 lands decision V8 (Quick Test and set work draw from the whole tier pool), the older fixes that the batch B and C1 reviews deferred (sections 20.7 and 22.7), harder kinds for the last tier echoes (section 21.7) and one harder statistics kind so the median class can leave the difficult tier (section 22.7). Nothing is committed; no static, template or JS file changed, so there is no cache bump.

### 23.1 V8: Quick Test and set work from the whole tier pool

**Before.** `models/quicktest.build_quicktest_problems` asked the topic for its practice queue (`variants_func`, 7 slots), took all of them and cycled the first three again; `app._freeze_class_work_problems` cycled the same queue for up to 20 questions. Measured over every GCSE maths tier (200 seeded draws each): 100% of 10-question Quick Tests and 100% of 20-question set work repeated a kind, by construction (3 of 10 questions and 13 of 20 were repeats of a slot already asked).

**Now.** `generators/shared/whole_pool.py`: `uses_whole_pool(level, subject)` is true for GCSE maths only (other subjects keep the queue cycle; their builders are untouched). `variant_utils.tier_pool(variants_func, difficulty, mode)` returns every slot of the tier once, in pool order: it runs the topic's own `variants_func` under a context flag (`whole_pool()`) that makes `select_tier_variants` return the whole pool instead of a 7-slot sample, so no topic module changed and every pool is read through the code that builds the queues. `PoolDraw` yields the slots in a shuffled order and, once the pool is used up, shuffles afresh, so no slot comes round again until every slot has been asked, and then the same kinds return with new numbers. `generate_from_pool(generator, variants_func, difficulty, mode, count, rng, accept, kind_check)` builds the questions; an identical question text is refused for up to 6 extra draws (fixed-text proofs on the second pass); set work passes `accept=_problem_is_gradable` as before. After Phase 3 every practice slot is its own strict kind (D1 and D2 are 0 and enforced), so no repeated slot means no repeated kind.

**Multiple choice.** A band's seven positional slots each draw at random from the band's entries, so the slot is not the kind. The draw still walks the seven slots without a repeat and, for GCSE maths, also refuses a question whose kind (`question_kind.quiz_kind`) or source generator (`variant_utils.mcq_source`) is already in the test, for the same 6 extra draws, as the lesson quiz does. Measured on every band (3 seeds): mean distinct kinds in a 10-question MCQ Quick Test 6.57 without the check, 6.85 with it; a band holds 5 to 12 kinds until Phase 4, so a 10-question single-band test cannot avoid every repeat, and bands of fewer than ten fixed items must repeat a text.

**Mixed difficulty and topic.** Neither picker offers a mixed difficulty, but the web Quick Test form accepts one; `tier_pool` then returns the union of the three tiers' pools, each slot once, so a mixed test spans the tiers without a repeat either. Quick Test and set work are always one topic, so there is no mixed-topic mode.

**Determinism and storage.** The draw takes an `rng` (tests only; the app passes none and stays unseeded). Nothing new is stored: a Quick Test session row has the same keys as before (`problems`, `answers`, `index`, `topic_name`, `level`, `subject`, `topic`, `difficulty`, `mode`, `owner_user_id`, `updated_at`) and holds the problems whole, a frozen assignment likewise, so a session or a piece of set work created before this change carries on unchanged (the queue the practice page stores, `user_problem_queues`, is not touched). The variant names are not stored (nothing about a pupil, and nothing a teacher sees).

**Measured, after (`scripts/test_gcse_maths_whole_pool_smoke.py`, every tier through the real builders, variant names recorded from the generator calls):** pools hold 9 to 22 slots (42 tiers under 10, 93 under 20). A 10-question Quick Test repeats a kind in 42 of 96 tiers (43.8%): exactly the tiers with 9 kinds, once each, at the tenth question. 20-question set work repeats in 93 tiers (96.9%): every tier under 20 kinds, 20 minus the pool size times. No repeat within the pool size anywhere, and the second pass covers the pool again. The smoke also checks determinism (one seed gives one plan and one set of questions, twice), an old stored session (problems built by cycling the queue) through the question, answer and results routes, a new session through the web and API routes, the stored row's keys and problem keys, 20-question set work through the teacher preview, assignment and pupil routes (no key, solution, form, record or prereqs before grading; a wrong answer graded from the stored copy), the mixed-difficulty union, and that other subjects keep the old builder. 6 s.

### 23.2 Older fixes (each changes an existing slot's output; the drift list is 23.6)

* **Off-grid readings on the older `graphical_simultaneous_equations` slots (section 20.7).** `minor_grid=True` on every older slot that reads a value from the drawing: `_gsim_f_read_intersection`, `_f_which_point_on_both`, `_f_read_y_at_crossing`, `_i_equations_from_graph`, `_i_parabola_read_one_point`, `_i_negative_gradient`, `_i_verify_algebra_from_graph`, `_d_both_parabola_points`, `_d_context_graph`, and the two multiple-choice readings `_gsim_mcq_read_coords` and `_gsim_mcq_parabola_point`. Before, the value to read lay between the labelled grid lines in 72 to 300 of 300 draws per slot (300 of 300 for the plotted points and the parabola readings); now every whole number has a faint line and all spans stay under the helper's 60-unit limit (checked over 300 draws per slot). The two multiple-choice generators change only in the drawing: text, options and key are identical for the same seed (80 of 80 draws), so the question of the day keeps its words and key on those days. The slots that count or compare (how many solutions, parallel, tangent, misses) are unchanged.
* **"Simplify" fraction slots without a form (section 20.7).** `_af_f_cancel_numeric`, `_af_f_multiply`, `_af_f_divide`, `_af_i_multiply_two` and `_af_d_subtract_fractions` now carry `answer_form = simplified`, so the question's own fraction typed back (`6x|8x` for 3/4) is refused with the kind form message. `_af_d_subtract_fractions` also puts its key in lowest terms, as "Simplify" asks: 6/(2x) is 3/x and 6/(2x + 6) is 3/(x + 3) (the solution shows the cancel), and no longer draws equal numerators (a top of 0). The verification smoke's `answer_form` check now requires the form on any "Simplify" question whose key is an `algebraic_fraction` (426 keys with a required form in the default run, from 413: the five slots add 23 and the six retired probability echoes, which carried the probability form, take 10 away). The "Write as a single fraction" slots are left as they are: they do not ask for simplest form (`_af_i_diff_denominator_add` can key 4/(2x), which the checker also accepts as 2/x).
* **Bold inside maths (section 20.7).** Six solutions had `<strong>` inside `\( ... \)` and showed raw TeX: `gcse_neg_powers`, `gcse_surds_practice_surd_equation`, `_sim_i_substitution_rearrange` (its `\(` was never closed either), `_ap_f_expand_consecutive`, `_ap_i_identity_expand` and `_ap_i_square_difference` (an outer `\(` left open before the bold). The bold is outside the maths now. A balance scan of every slot (2 seeds, `\(` against `\)`) found two more unclosed spans, fixed in the same pass: `gcse_surds_practice_divide` (the working never closed) and `_vectors_diff_geometry_parallelogram` (a stray `\)` at the end of the alternative line). The scan now finds 0 bold-in-maths and 0 unbalanced spans.
* **Pythagoras drawings (section 22.7).** `_py_f5_ladder_wall` draws "m" labels for its ladder in metres (`unit='m'`). `_pyth_tri_svg` and `_rect_diag_svg` include the left edge of the vertical label in their frame (about 3.5 px a character, centred on the label), so "12 cm" is no longer cut: every centred label now has the 12 px pad to its left (measured from the viewBox). This widens the frame of every drawn Pythagoras slot by a few pixels: `_py_f1_find_hypotenuse`, `_py_f2_find_shorter_side`, `_py_f5_ladder_wall`, `_py_f6_rectangle_diagonal`, `_py_f8_square_diagonal`, `_py_i1_perimeter` and the batch C1 slots `_py_f9_ladder_height`, `_py_i9_square_area_from_diagonal`, `_py_d9_algebraic_sides`. Rendered with the app's CSS (Playwright): the labels are whole.
* **Long drawn questions and units (section 22.1 finding 3).** The eleven older drawn slots (the gsim graphs, the vectors grid `_vectors_inter_collinear_points`, the probability trees `_prob_diff_04`, `_05`, `_06`, `_13`, `_16`) state no unit except `_gsim_d_context_graph` (pounds); the unit round trip already types every numeric key with the units its question states through `answer_units.problem_question_text`, so they were covered once the reader was fixed. The verification smoke now also pins the reading itself: for every generated question over 6,000 characters it checks that the unit reader reaches the last words of the ask (110 drawn questions in the default run, printed on the summary line), so the C1 cut cannot come back unseen.

### 23.3 New harder kinds (20) and the echoes they replace (18)

Code: `generators/gcse/maths_variety_c2.py`, solvers in `scripts/gcse_verify/solvers_variety_c2.py` (two `@diagram` checks read the drawn line and its marked points through the tick labels), hint rules in the batch C2 block of `generators/shared/misconception_5b.py`, unit rows in `scripts/gcse_hints_5b.py`. Same standard as batches A to C1: a worked solution, a hint, the right answer type and form, a `record()` family with an independent solver, the checker round trip, no degenerate draw (the key and the hint slips never equal a printed number). A star marks a slot with a topic hint rule (16 of 20, 80%).

| Topic, tier | Slot | Example question | Retires |
|---|---|---|---|
| probability D | `gcse_prob_counters_algebraic` * | A bag contains only orange sweets and lemon sweets. There are 3 orange sweets. Two sweets are taken at random, without replacement. The probability that both are orange is 1/35. How many lemon sweets are in the bag? | `_prob_diff_01` (at least one success, F) |
| probability D | `gcse_prob_independent_union` * | A and B are independent events. P(A) = 0.3 and P(B) = 0.2. Find P(A or B). (or exactly one of them) | `_prob_diff_03` (A or B, F and I) |
| probability D | `gcse_prob_three_same_colour` * | A bag contains 7 orange sweets and 3 lemon sweets. Three sweets are taken at random, without replacement. Find the probability that all three are the same colour. | `_prob_diff_07` (Venn total, F and I) |
| probability D | `gcse_prob_two_day_dependent` * | The probability that it rains on Monday is 0.7. If it rains on Monday, the probability that it rains on Tuesday is 0.4. If it does not rain on Monday, ... 0.2. Find the probability that it rains on at least one of the two days. (or exactly one) | `_prob_diff_08` (independent product, F and I) |
| probability D | `gcse_prob_trials_needed` * | A biased coin lands on heads with probability 0.4. How many times must the coin be flipped so that the probability of at least one head is more than 0.99? | `_prob_diff_14` (mutually exclusive, F and I) |
| probability D | `gcse_prob_which_bag` * | Bag A contains 7 orange sweets and 1 lemon sweet. Bag B contains 2 orange and 8 lemon. A bag is chosen at random and a sweet taken. Given that the sweet is orange, find the probability that it came from bag A. | `_prob_diff_02` (conditional from P(A) and P(A and B), F) |
| ratio D | `gcse_ratio_ages` * | The ages of Priya and Tom are in the ratio 2 : 5. In 8 years' time their ages will be in the ratio 2 : 3. How old is Tom now? | `_ratio_diff_19` (map and hike, I) |
| ratio D | `gcse_ratio_fraction_of_groups` * | In a class, 4/5 of the people are girls and the rest are boys. 3/5 of the girls and 1/5 of the boys walk to school. What fraction of the whole class walk to school? | none new; it stands in for the moved recipe slot (the pointer of `_ratio_diff_09`, 23.5) |
| ratio D | `gcse_ratio_percent_more` * | Priya and Tom share £132 so that Priya gets 20% more than Tom. How much does Priya get? | `_ratio_diff_14` (map scale, F and I) |
| ratio D | `gcse_ratio_three_part_difference` * | A : B = 2 : 5 and B : C = 1 : 3. C gets £26 more than A. How much money is shared altogether? (or B's share) | `_ratio_diff_01` (merging classes, I) |
| ratio D | `gcse_ratio_algebraic_parts` * | There are 6x + 6 orange sweets and 2x + 5 lemon sweets. The ratio of orange to lemon is 8 : 3. Find x. | `_ratio_diff_16` (inverse proportion formula, F and I) |
| ratio D | `gcse_ratio_expression_ratio` | x : y = 4 : 1. Find the ratio (4x + 3y) : (2x + y) in its simplest form. (a `ratio` answer) | `_ratio_diff_17` (direct proportion formula, F and I) |
| graphs I | `gcse_gra_line_through_two_points` | Find the equation of the straight line through (-1, -4) and (-4, 2). Give your answer in the form y = mx + c. | `_gra_inter_02` (equation from gradient and intercept, F) |
| graphs I | `gcse_gra_x_intercept` * | The line y = -2x + 12 crosses the x-axis at P. Find the coordinates of P. | `_gra_inter_07` (midpoint, F) |
| graphs I | `gcse_gra_missing_coordinate` * | The point (a, -5) lies on the line y = -2x + 9. Find a. (or the y-coordinate) | `_gra_inter_09` (reciprocal value, F) |
| graphs I | `gcse_gra_parallel_through_point` | Line L has the equation y = 5x + 6. Find the equation of the line parallel to L through (2, 4). | `_gra_inter_03` (parallel gradient, F) |
| graphs I | `gcse_gra_gradient_from_graph` * | The graph shows a straight line. The marked points have whole-number coordinates. [graph] Work out the gradient. | `_gra_inter_01` (gradient from two points, F) |
| graphs I | `gcse_gra_conversion_graph` * | The graph converts between pounds and euros. [graph with a marked point] Use the graph to convert 50 pounds to euros. (either way) | `_gra_inter_04` (speed from a distance-time graph, F) |
| graphs D | `gcse_gra_perpendicular_bisector` | A is (6, 1) and B is (10, 5). Find the equation of the perpendicular bisector of AB. | `_gra_diff_12` (line of best fit, I) |
| statistics D | `gcse_stats_frequency_density` * | A histogram is to be drawn ... The class 20 < t ≤ 40 has a frequency of 18. Work out the frequency density. (or the frequency from a bar's height) | none: lets `gcse_stats_median_class` move to I |

Tiers after the batch (strict kinds F / I / D): probability 16 / 18 / 16, ratio_proportion 16 / 18 / 14, graphs 10 / 14 / 12, statistics 12 / 16 / 9. `VARIETY_FLOORS` rise for ratio_proportion I (17 to 18) and statistics I (15 to 16); every other floor is met at its value. Tier echoes fall from 41 slots to 23; the graphs intermediate tier keeps `_gra_scatter_correlation_any` as its one declared foundational-intermediate echo. The remaining 23 echoes are all foundational-intermediate pairs (probability 9, ratio_proportion 10, statistics 3, graphs 1, the declared correlation slot); none is into a difficult tier (listed by a script over `variety.canonical_keys`). *Correction (whole-change review C7, section 25): that measure counts only one-line wrappers that call one helper from two tiers; by template and record family 10 difficult-tier slots (and 30 more) repeat a lower tier's question, so "none into a difficult tier" held for wrappers only.*

The four slots without a topic rule: the three `linear_equation` answers (`line_through_two_points`, `parallel_through_point`, `perpendicular_bisector`: that answer type carries no record, as in batch C1) and the `ratio` answer (`expression_ratio`: the hint engine has no ratio type). `gcse_gra_gradient_from_graph` asks one stem whose variety is in the drawing (like `gcse_gra_exponential_read`), so the section 2 measure counts 83 fixed variants (82 before); `register.FIXED_VARIANTS` is unchanged.

Kinds considered and not built: a second non-drawn statistics kind for the difficult tier (the drawn candidates, a cumulative frequency reading and a histogram with unequal classes, duplicate `_stats_diff_05` and `_09`); `gcse_stats_two_way_percent` therefore stays in the difficult tier, the lightest item there, and is said so here.

### 23.4 The two light difficult-tier kinds (section 22.7)

`gcse_stats_median_class` (grade 4 to 5) moved to statistics intermediate, with `gcse_stats_frequency_density` keeping the difficult tier at 9 kinds. `gcse_ratio_recipe_limiting` (grade 4) moved to ratio intermediate (18 kinds, floor raised), the six new ratio kinds keeping the difficult tier at 14. A moved slot keeps its function byte for byte; its seeds follow `crc32(slug/tier/fn)`, so it draws different questions in its new tier. `gcse_stats_two_way_percent` stays (23.3).

### 23.5 Retired names

18 names join `register.RETIRED` (117 in all; the compat smoke resolves, resumes and rerolls them): probability `_prob_diff_01`, `_02`, `_03`, `_07`, `_08`, `_14`; ratio `_ratio_diff_01`, `_14`, `_16`, `_17`, `_19`; graphs `_gra_diff_12`, `_gra_inter_01`, `_02`, `_03`, `_04`, `_07`, `_09`. Three older entries pointed at a name this batch retired or moved and were repointed to a live slot of the same tier: `_prob_diff_17` (was `_prob_diff_03`) to `gcse_prob_independent_union`, `_ratio_diff_05` (was `_ratio_diff_01`) to `gcse_ratio_three_part_difference`, `_ratio_diff_09` (was `gcse_ratio_recipe_limiting`, now intermediate) to `gcse_ratio_fraction_of_groups`. Every retired function stays defined in exactly one module.

### 23.6 Drift

Every practice slot and every retired name of the pre-batch-B tree (`/tmp/claude-0/pb_b_before`, the last snapshot; batches B and C1 and their reviews left every common slot byte-identical, section 22.6) called directly by name with the same 3 seeds, SVG ids normalised: 1,140 common names, 28 differ, all listed above: the five `_af_*` form slots, the eight raw-TeX fixes (`gcse_neg_powers`, `gcse_surds_practice_surd_equation`, `gcse_surds_practice_divide`, `_sim_i_substitution_rearrange`, `_ap_f_expand_consecutive`, `_ap_i_identity_expand`, `_ap_i_square_difference`, `_vectors_diff_geometry_parallelogram`), the nine older gsim practice readings, and the six older Pythagoras drawings (`_py_f1`, `_f2`, `_f5`, `_f6`, `_f8`, `_i1`). Outside that dump: the two gsim multiple-choice readings (drawing only) and the three C1 Pythagoras drawings (frame only). The 149 other names are the slots batches B, C1 and C2 added. Nothing else moved.

### 23.7 Metrics, runtimes and results

| Measure | Before (C1 review) | After |
|---|---|---|
| Practice slots / strict kinds | 1,171 / 1,171 | 1,173 / 1,173 |
| Tier echoes | 41 | 23 one-line-wrapper echoes (none into a difficult tier by that measure; by template and family 40 slots, 10 in a difficult tier: section 25) |
| Fixed variants (section 2 measure) | 82 | 83 |
| 10-question Quick Test with a repeated kind (practice mode) | 100% of tiers (3 repeats) | 43.8% of tiers (the 42 with 9 kinds, 1 repeat) |
| 20-question set work with a repeated kind | 100% of tiers (13 repeats) | 96.9% of tiers (20 minus the pool size repeats; 0 in the 3 tiers with 20 kinds or more) |
| Multiple-choice Quick Test, mean distinct kinds in 10 | 6.57 | 6.85 |
| Topic hint slots | 715 of 1,171 (61.1%) | 716 of 1,173 (61.0%); floor 0.600 |
| Combined hint slots | 908 (77.5%) | 908 (77.4%); floor 0.770 |
| Retired names | 99 | 117 |
| Verification smoke, alone | 38.0 s (41.6 s internal in one run at the start of this batch) | 36.9 and 37.2 s internal (37.9 and 38.1 s wall), two runs back to back on the final tree with the machine idle; 39.6 to 41.0 s in three earlier runs with other jobs in flight |
| Hints smoke | 16 s | 16.7 and 17.6 s wall (15.7 s internal on the first) |

Runs (this machine, 2 CPUs): verification default passes (20,238 practice questions, 5,220 round trips, 117 retired names, damaged drawings 41 of 41 with the two new diagram families); `--deep --seed 6100` (section 23.8); hints smoke, ladder and MCQ notes smokes pass (unit table 584 topic rows, mutation 795 of 795 topic and 324 of 324 pair, box and expression perturbations caught); retired compat (117 names), correctness, answer check, MCQ letter and voice smokes pass (Appendix A of `docs/ZORP_CHARM.md` regenerated for the 29 new messages); the whole-pool smoke passes; G8 Phase 4 (set work), Phase M4 and topic status smokes pass; `ruff check .` clean; full suite: see 23.8.

### 23.8 Deep runs and full suite

* `--deep --seed 6100`: passes, 270 s (234,600 practice questions, 21,308 round trips, 472 long drawn questions read to their ask), before the last cosmetic edits (bracketed negatives in four worked solutions, the conversion graph's draw range).
* `--deep --seed 7300`: passes, 261 s, before the conversion graph's wording fix (23.9).
* `--deep --seed 8800`: passes, 260 s, on the final tree (234,600 practice questions, 21,308 round trips, 1,711 with a required form, 6,393 typed with their units, 488 long drawn questions); D1 and D2 both 0, no slot fixed on every seed outside `register.FIXED_VARIANTS`.
* Full suite: `/tmp/claude-0/suite_v3c2.log` (110 smoke tests, the whole-pool smoke new); result on the last line of that log and in the handoff.

### 23.9 Notes from building

* **The unit model reads an SVG description.** The conversion graph's `<desc>` first said "converting miles to kilometres", which the checker's unit model read as "to kilometres", the unit asked for, so "50 km" was accepted for an answer in miles. The description now says "a conversion graph for miles and kilometres", the question ends "Give your answer in miles." and the kilograms-to-pounds conversion was dropped ("pounds" reads as money): typed "40 miles" is right and "40 km" refused, and the same for inches and centimetres. The pounds-to-euros graph accepted either currency symbol on the number (the model takes any currency the question names when two are named); the C2 review (24.1, finding 1) found that "£42" therefore passed for a key in euros and fixed the wording.
* **Harness and `sqrtq`.** `misconception_topics.sqrtq` returns a 60-digit approximation for a non-square; a truth that used it for the counters quadratic produced a huge fraction and the whole diagnosis went quiet, so the batch C2 rules take an exact integer root or nothing (`_exact_root`).
* **Drawn values are `derived`.** The gradient-from-a-graph and conversion-graph records declare the coordinates read from the drawing as derived (the presence guard looks for them in the question text); the diagram checks read them back from the SVG instead.

### 23.9 Deferred

* Multiple-choice Quick Tests still repeat kinds in single bands of 5 to 9 kinds (Phase 4 content); the kind check only pushes a test toward the band's ceiling.
* A second harder statistics kind without a drawing, so that `gcse_stats_two_way_percent` can leave the difficult tier.
* The 23 foundational-intermediate echoes (the plan allows one declared echo per tier; the intermediate tiers of probability, ratio and statistics still hold several).
* `_trans_inter_enlarge_not_origin`'s (0, 0) centre and the doubled transformations pool entries (sections 14.7 and 13.2) are untouched.
* `_gsim_d_context_graph` accepts "£4" for a count of booklets (the unit model takes a currency symbol when the question uses money); pre-existing and lenient, not wrong.

## 24. Phase 3 batch C2 review notes (2026-10-29, independent review, nothing committed)

Reviewed against sections 3, 7, 10, 11 and 23, `docs/GCSE_MATHS_HINTS.md` section 31, the "Phase 3 batch C2" note of `docs/GCSE_MATHS_VERIFICATION.md` and the code (`whole_pool.py`, the `variant_utils` context flag and `tier_pool`, `models/quicktest.py`, `app._freeze_class_work_problems`, the five changed generator modules, the 20 new generators, their solvers and hint rules), as a GCSE maths teacher (AQA 8300 / Edexcel 1MA1), a privacy and security reviewer and a code reviewer. Every new generator was read over 30 seeds through its topic wrapper (question, worked solution, hint, marks, key, answer type and form); every "a op b = c" line of every worked solution was also checked by script over 200 seeds (2,331 lines, 0 false). The drawn slots batch C2 touched (nine older `graphical_simultaneous_equations` practice readings and the two multiple-choice ones, nine Pythagoras frames, the two new graphs) were rendered in the real practice page (the app running locally with `PB_TESTING=1 PB_ALLOW_DEV_SECRET=1 CORS_ORIGINS=https://app.example.com`, the question injected into the page's own question container) at 360 px light and dark and 1280 px light, two seeds each: 106 screenshots in `/mnt/user-data/outputs/variety_c2_review/` with `report.json`. Everything below was fixed in the tree unless it says otherwise.

### 24.1 Findings

| # | Severity | Finding | Outcome |
|---|---|---|---|
| 1 | High | **A wrong currency was accepted on the conversion graph.** The pounds-and-euros draw of `gcse_gra_conversion_graph` wrote "pounds (£)" and "euros (€)" in the question and on its axis labels; the unit model reads a bracketed symbol as a currency asked for, so both currencies were "asked" and "£42" (and "42 pounds") passed for a key of 42 euros, both ways round. Section 23.9 called this lenient; it is a wrong answer marked right. | Fixed: the amount given carries its symbol and the ask names one currency as a word ("Use the graph to convert £35 to euros. Give your answer in euros."), the axis labels are "Pounds" and "Euros", so the model asks for one currency and "£42" is refused with "The question asks for the answer in euros (€)". `forms.wrong_unit_variants` now types the key with any other currency the question names when exactly one is asked for, and `check_conversion_currency` in the verification smoke pins both directions of this slot (mutation M7). |
| 2 | Medium | **A mixed or unknown difficulty on the web Quick Test form gave a 500 for six topics.** `generate_from_pool` took the union of the three tiers' pools but called the generator with the difficulty it was given; algebra, bidmas, decimals, fdp, multiples_factors and surds have no practice pool for anything but the three tiers, so every draw raised and the builder gave up with `generate_failed`, which the web route does not catch. The old builder gave foundational questions labelled with the typed difficulty. Not reachable from the app's pickers (the API checks `DIFFICULTIES`), only from a hand-made POST. | Fixed: `whole_pool.pool_with_tiers` keeps each slot's own tier and the generator is called with it, so a mixed test spans the tiers and each question carries the tier it came from; the whole-pool smoke builds a mixed test on bidmas and surds (mutation M9). |
| 3 | Medium | **The perpendicular bisector drew AB with gradient ±1 three draws in four.** The gradient draw allowed only ±1 and ±1/2 after the whole-number filter, weighted 3 : 1, so the "negative reciprocal" was a sign change in most draws. | Fixed: AB's gradient is ±1, ±1/2 or ±1/3, drawn evenly (the perpendicular gradient stays whole for the `linear_equation` key), the working shows the division ("−2 ÷ 6 = −1/3, so the perpendicular gradient is −1 ÷ (−1/3) = 3"). |
| 4 | Low | **A hint diagnosed the key plus one as "the sign of the term that moved".** `gr.coordinate_sign_moved` on `gcse_gra_missing_coordinate` reaches (given + c)/m, which is a fraction (26/3) when the key is whole (8); the engine rounds a non-terminating slip to the pupil's places, so a typed 9 was called a sign slip. | Fixed: the two rules of that family offer whole-number slips only (`_whole`); the unit-table rows still fire. |
| 5 | Low | Worked lines "y = 1x + c", "1 × 5 + c", "1x = 5", "−1k + 3", "−1 × 3", "1t", "1(7t + 4)", "1t = 12", "1 × 2 = 2", "−1x = −11", "× 12/1", "1 parts", "22 : 15 = 22 : 15", "A : B = 3 : 5 = 3 : 5", "(0.8)^9" in plain text; a hint that said "P(all red) and P(all blue)" for orange and lemon sweets; "In a school trip ... of the whole school trip". | Fixed (helpers `_mx`, `_prod` and `_sub_line`; the equation side with the x terms is written with a positive coefficient; "On a school trip ... of the whole group"; `<sup>` powers). |
| 6 | Low, not changed | `_py_f5_ladder_wall` (older) can put the foot of a ladder 15 m from the wall for a ladder reaching 8 m up (the 8, 15, 17 triple): correct maths, an odd ladder. The web `/quicktest/start` route has no `can_access_difficulty` gate (the API route has one); pre-existing. | Noted for a later pass. |

### 24.2 V8 audit (the whole-pool draw)

* **Determinism and storage.** A Quick Test session and a frozen piece of set work store the generated problems whole, exactly as before (the session row has the same eleven keys; a frozen problem has the same keys whether built by the old queue cycle or the new draw: checked key for key). Nothing about the draw is stored, so reloading a question, resuming mid-test and grading read the stored copy: an old-shaped session with four answers stored resumed at question 5, graded six more and reached the results page; a frozen assignment is graded from `problems_json` as before (`models/class_assignments` is untouched by this batch). The `rng` argument is used only by the tests; the app stays unseeded. The whole-pool smoke's determinism check seeds both the global generator and the draw.
* **The context flag.** `_WHOLE_POOL` is a `contextvars.ContextVar` set only inside `tier_pool`'s `with whole_pool():`, reset by `__exit__` on every path (checked with a variants function that raises), and per thread (a thread holding the flag open saw the whole pool while another saw the 7-slot sample). The generator calls themselves run outside the flag, so the practice queue (`_build_problem_queue`, 7 slots), the lesson quiz and every other caller are unchanged; the new `check_flag_stays_put` in the whole-pool smoke pins this (mutations M3 and M3b).
* **Every pool name resolves and is honoured.** All 1,841 names `tier_pool` returns (96 practice tiers and 96 multiple-choice bands) resolve through `lookup_variant_by_name` to the very object in the pool, and no topic generator draws a random variant when given a name (no `random.choice` over pool callables during a named draw, checked by patching `random.choice`); the MCQ positional slots resolve through the band's own seven wrappers.
* **Repeat rates, measured again with my own instrumentation** (two seeds per tier through `generate_from_pool`): 0 of 96 tiers repeat a slot within the pool size for 10 or 20 questions; pools 9 to 22; multiple choice, 192 ten-question tests with the kind check, mean 6.88 distinct kinds (minimum 4, a band of 4 or 5 kinds), 295 identical texts over all tests (bands of fewer than ten fixed items). Set work's `accept=_problem_is_gradable` can only ever refuse one slot (`_cl_d5_apollonius_circle`, constructions difficult), so the seven attempts per question cannot run out.
* **No new stored data about pupils**; the API and the web question page carry no variant name, key, solution, form or record before grading (checked on an old and a new session). Other subjects take the old builder (`uses_whole_pool` is GCSE maths only). Nothing in the practice page JS or the templates assumes seven questions (the Quick Test template uses the stored length; set work keeps its 5 to 20 count).
* **`_call` swallows only `ValueError`**, as the old Quick Test builder did (the old set-work path also caught `TypeError`); every GCSE maths generator takes `variant_name`, so no `TypeError` arises.

### 24.3 Verdicts by topic (as a GCSE teacher)

* **probability (D):** correct in every draw. The counters question is the classic "n(n − 1) = ..." quadratic with the factorisation shown and the negative root rejected; the union and the two-day questions keep the overlap and the conditional branch straight; "exactly one" and "at least one" are both asked; three the same colour adds the two products; the trials question's threshold is strict and never met exactly (checked over the whole draw space); the "which bag" question is a reverse conditional with the bags chosen at random, stated. Grade 7 to 9 content, right for the tier.
* **ratio_proportion (D):** correct. The ages question needs the ratio to rise towards 1 and does (the draw rejects the other order); the fraction-of-groups question takes "the rest" from one; "p% more" is (100 + p) : 100; the three-part question matches B's parts and uses the difference between the two people named; the algebraic parts cross-multiply with a whole positive x; the expression ratio is simplified. Grade 6 to 8. (Correction, whole-change review C3, fix pass 1a 2026-11-03: the checker did not refuse an unsimplified ratio when this was written, because `check_ratio` normalises both sides, so 16:42 was right for 8:21. The slot now carries the `simplified` form, which refuses an equal ratio with a common factor, and the verification round trip types one and requires the refusal.)
* **graphs (I and D):** correct. The line through two points, the parallel line and the x-intercept are grade 5 work and sit well in the intermediate tier with the missing coordinate; the gradient read from the drawing and the conversion graph have their points on grid lines (the drawing checks read them back); the perpendicular bisector is grade 8 after finding 3.
* **statistics (D):** correct; frequency density both ways (frequency ÷ width, height × width) with widths of 5 to 50. Grade 6 to 7 and the lightest kind of the tier after `gcse_stats_two_way_percent`, as 23.3 says.
* **Moved slots:** the median class (grade 4 to 5) and the limiting recipe (grade 4) are in their intermediate pools only and read as intermediate questions.

### 24.4 Older fixes

* **Gridlines (nine practice readings, two multiple-choice readings):** the drawing is the only thing that changed (question text, solution and key byte-identical over 3 seeds; the MCQ pair identical in text, options and key). A new check in the verification smoke, `_grid_checks` on the `_GRID_TASKS` (the older readings and the batch B readings), calibrates each axis from its numbered ticks and requires a drawn line at every whole number between the labelled extremes; every reading slot passes on 30 seeds, the counting slots (no numbered axes, no faint grid) are not checked, and a reading slot that loses its faint grid fails (mutation M6).
* **Simplified forms (five `_af_*` slots):** only the form changed (and the lowest-terms key of `_af_d_subtract_fractions`). The checker takes every other valid simplest form tried: `1 | 4 − x` for `−1 | x − 4`, `3 | (x + 3)`, `x² | 48`, `x*x | 48`, `(x^2) | 48`, `5 + x | 8 + x`, `3x^-1 | 1`, and a terminating decimal for a numeric key; it refuses the question's own fraction and `6 | 2x` with the kind form message.
* **Bold inside maths (eight solutions):** every `\(` now has its `\)` (a balance scan of the eight over 3 seeds: 0 unbalanced) and the bold sits outside the span.
* **Pythagoras frames and the ladder in metres:** rendered at 360 px, light and dark: "60 cm", "8 m", "15 m" and "? m" are whole, no clipped text, no console error, no CSP violation; the only report line is the rotated single-letter "y" axis label that the box test counts as tiny (the C1 review's false positive).

### 24.5 Retired echoes and hints

* Each of the 18 retired names was generated beside its claimed twin: the same template and record family in the lower tier in every case (`_prob_diff_01` and `_prob_found_14`, ... `_gra_inter_09` and `_gra_found_09`); the three repointed entries point at live slots of their own tier; no retired name is in any pool; the compat smoke resolves, resumes and rerolls 117 names.
* All 31 new rules were sampled on 30 questions of every C2 slot with the key ±1, doubled, halved, negated, its reciprocal and every printed number: apart from finding 4, every topic message named a slip the typed value genuinely reaches (`ratio.groups_one_part` and `ratio.groups_rest_not_taken` can fire on a printed fraction, but that fraction is the slip's own value, so the message still reads right).
* **Coverage, honestly:** 716 of 1,173 slots (61.0%) carry a topic hint on the default seed pair and 710 to 713 (60.5% to 60.8%) on three other pairs (run offsets 2, 10 and 50, in a copy of the tree); combined 906 to 908 (77.2% to 77.4%). Both floors (0.600, 0.770) hold on every pair.

### 24.6 Runtime, drift, mutation tests and results

* **Runtime.** Verification smoke alone on this machine (idle): 28.3, 27.2, 27.9 s wall (the batch measured 37 to 38 s on the build machine's busier day; the budget is 38 s). Hints smoke 11.5 s. Whole-pool smoke 4.3 s.
* **Drift.** Every practice slot and every retired name of the batch C1 review's final tree (1,269 names, called directly, 3 seeds, SVG ids normalised): 32 differ, the 31 that section 23.6 lists (five fraction forms, eight raw-TeX solutions, nine gsim practice readings, six older and three C1 Pythagoras drawings) and `gcse_ratio_change_after_adding`, whose working line the C1 review itself fixed after that copy was taken; the 20 new slots are new; nothing else moved. The gsim multiple-choice readings differ in the drawing only.
* **Mutation tests** (on a copy of the tree, `/tmp/claude-0/pb_mut_c2`, each file restored and compared byte for byte with the working tree afterwards):

| Mutation | Caught by |
|---|---|
| M1 `PoolDraw` shuffles with the global generator, not its `rng` | whole-pool smoke (the same seed gave two draw plans) |
| M2 a draw returns any slot at random (repeats within the pool) | whole-pool smoke (311 issues) |
| M3 `whole_pool.__exit__` no longer resets the flag; M3b `tier_pool` sets it without the context manager | whole-pool smoke (`check_flag_stays_put`, new) |
| M4 `answer_form` no longer stripped from frozen set work; M4b `solution_html` not stripped | whole-pool smoke (preview and pupil leak) |
| M5 the x-intercept solver drops the minus sign; M5b the counters generator keys n − r + 1; M5c the frequency-density solver multiplies | verification smoke |
| M6 `_gsim_f_read_intersection` loses its faint grid | verification smoke (`_grid_checks`, new) |
| M7 the conversion graph writes "(£)" and "(€)" again | verification smoke (`check_conversion_currency`, new) |
| M9 the mixed draw calls the generator with "mixed" | whole-pool smoke (the bidmas and surds mixed tests, new) |

| Run | Result |
|---|---|
| Verification smoke, default, alone | passes; 27 to 28 s, 20,238 practice questions, 5,220 round trips, 117 retired names, damaged drawings 41/41 |
| Verification `--deep --seed 9700` (new offset) | passes, 189 s inside the run (3 min 10 s wall), 234,600 practice questions, 21,315 round trips, 1,703 with a required form, 6,390 typed with their units, 474 long drawn questions read to their ask; D1 and D2 both 0, no slot fixed on every seed outside `register.FIXED_VARIANTS`, damaged drawings 41/41 |
| Hints smoke | passes, 11.5 s; 716 topic and 908 combined slots of 1,173; unit table 584 topic rows; mutation 795 of 795 topic and 324 of 324 pair, box and expression perturbations caught |
| Hints ladder / MCQ notes / retired compat / correctness / answer check / MCQ letter / voice / whole-pool / Quick Test and class-work smokes | 2.0 / 1.3 / 1.6 / 11.0 / 4.6 / 1.7 / 5.6 / 5.1 / 1.0 and 1.5 s, all pass (plus the topic status smoke, 1.2 s) |
| `ruff check .` | clean |
| Full suite | 110 of 110 smoke tests pass (`/tmp/claude-0/suite_v3c2_review.log`, run on the final tree after the review server was stopped) |

### 24.7 Deferred

* The 23 foundational-intermediate echoes and the multiple-choice band sizes (23.9).
* The web Quick Test form's missing difficulty gate (finding 6) and the odd ladder numbers of `_py_f5_ladder_wall`.
* `_gsim_d_context_graph` still accepts "£4" for a count of booklets (23.9).
* The hint engine rounds a non-terminating topic slip to the pupil's places (the policy a 2026-10-26 review set); finding 4 narrowed one family rather than the policy.

## 25. Whole-change review, fix pass 3: honest kinds, template echoes and drift (2026-11-03, not committed)

**Kinds per tier after C6.** `register.VARIETY_NEAR_DUPLICATES` lists ten reviewed groups (17 merges) of slots a teacher reads as one kind although their templates and record families differ, so the sibling rule D2 cannot see them. They count as one strict kind each; the content is unchanged. Practice: 1,173 slots, 1,156 strict kinds (D1 0, D2 0, near-duplicates merged 17). Tiers that fall **below 9 kinds**:

| Tier | Slots | Kinds | The merged groups |
|---|---|---|---|
| quadratic_simultaneous_equations F | 9 | 5 | `_qsim_f_find_y_given_x`, `gcse_qsim_f_y_from_x_values`, `gcse_qsim_f_circle_line_y` (find y at a given x); `_qsim_f_rearrange_only`, `_qsim_f_substitute_step`, `gcse_qsim_f_expand_substitution` (rearrange to a quadratic) |
| decimals F | 9 | 5 | `gcse_dec_add_subtract`, `gcse_dec_subtract_from_whole`, `gcse_dec_proc_difference`, `gcse_dec_proc_three_add` (add or subtract decimals); `gcse_dec_multiply_power10`, `gcse_dec_proc_divide_power10` |
| completing_the_square F | 9 | 6 | `_cts_f_half_coefficient`, `gcse_cts_f_negative_half`; `_cts_f_missing_constant`, `_cts_f_square_the_half`, `gcse_cts_f_find_q_given_p` |
| algebraic_proof D | 9 | 8 | `_ap_d_disprove_always_prime`, `gcse_ap_d_euler_prime_counterexample` |
| functions F | 9 | 8 | `_fn_f_evaluate_linear`, `gcse_fn_f_negative_input` |

Also merged, still at 9 or more: ratio_proportion D 14 to 11 (`y = kx^n` with four exponents), graphs I 14 to 13 (`gcse_gra_x_intercept`, `gcse_gra_missing_coordinate`). Tiers below 7 kinds: 3 (qsim F, decimals F, completing the square F). The mean queue repeat share is 5.3% (it was 0.0 only because every slot counted as a kind); `VARIETY_FLOORS` were set to the new measured values and the ceiling to 0.054. **Follow-up** (not done: replacing a duplicate needs a new, checked kind, not a quick edit): a genuinely new kind for each of the five tiers above, for example a Foundation completing-the-square "read the turning point" and a decimals F "round to a number of significant figures in context". Cross-tier near-duplicates the review named (`gcse_ap_d_difference_squares_multiple_of_eight` against the intermediate difference of squares, `gcse_ap_f_multiple_of_five_form` against `_ap_i_multiple_of_three`, `gcse_fn_i_inverse_value` against `_fn_f_find_input_linear`) are template echoes, below.

**Echoes after C7.** `variety.template_echoes` finds a slot whose question template (30 or more characters once numbers and names are masked) and record family also occur in a lower tier of the same topic: **40 slots, 10 of them in a difficult tier** (algebra `algebra_practice_expand_mixed`, algebraic fractions `_af_d_add_reciprocal_style`, algebraic proof `_ap_d_n_squared_plus_n`, changing the subject `_cts_d_suvat_u_zero`, completing the square `_cts_d_decimal_roots`, equations `_eq_diff_simult_linear_pair_var`, simultaneous equations `_sim_d_general_elimination`, transformations `_trans_diff_negative_enlarge_describe`, trigonometry `_trig_diff_cosine_rule_angle` and `_trig_diff_sine_rule_side`). They are reported (the full list is in `--variety-report`), not a failing ratchet: the draws are sampled, so the count moves by a few with the seed. Reviewed as follow-up, not changed. (The statistics difficult echo, C5, is gone: `gcse_stats_frequency_density` keeps only the harder reverse draw.) Sections 23.3 and 23.7 are corrected: they counted one-line wrappers only.

**Drift (generated output changes; everything else is byte for byte, 4 seeds of every slot compared with the tree before this pass).** By cause: the answer-box example moved off the key (a hint-only change, only on the draws where it equalled the key) in the surds, fractions, ratio, bearings, trigonometry, vectors, equations (rearrangements), changing-the-subject and algebra slots; the surd box hint without an em dash (all slots with it); the slots fixed in C5 to C13 (`gcse_stats_frequency_density`, `gcse_stats_time_series_mean`, `gcse_gra_circle_equation`, `gcse_gra_circle_tangent`, `gcse_qsim_f_circle_line_y`, `gcse_qsim_d_tangent_k`, `gcse_bidmas_decimals`, `gcse_surds_rationalise_coefficient`, `_ap_d_disprove_always_prime`, `_mens_inter_garden_plot_multipart`, `_mens_inter_cone_container_multipart`, `_py_f9_ladder_height`, `_fn_i_composite_linear`, `_sim_proc_elimination`, the money slots `gcse_fdp_percentage_decrease`, `gcse_fdp_reverse_percentage`, `gcse_fdp_reverse_percentage_two_step`, `gcse_fdp_compound_percentage`, `gcse_dec_proc_multi_step_shop`, `_number_inter_reverse_percentage_decrease`, `_number_inter_vat_word_problem`, the ratio MCQ type 6, and the 1x and + 0 workings listed in the verification note); the trees of `_prob_found_08` and `_prob_found_09` (and the no-replacement tree) without the outcome probabilities; `_prob_found_15` leaves Foundation and `_prob_diff_02` returns to the difficult pool. The probability Foundation and difficult slots and `gcse_prob_*` difficult slots draw different numbers on the same seed because the pool sizes changed (16 to 15 and 16 to 17: `select_tier_variants` draws before it picks the named variant); the questions are of the same kinds.

## Appendix A: the 64 redundant practice slots (keep the first, retire the rest)

D1 means an exact duplicate (same helper call or same output); D2 means a sibling (same template and family). Measured 2026-10-27.

| Topic | Tier | Keep | Retire | Class |
|---|---|---|---|---|
| algebra | F | `algebra_practice_linear_1` | `_linear_2`, `_linear_3` (merge into one per-tier linear slot) | D2 |
| algebra | D | `algebra_practice_consecutive_integers` | `algebra_practice_quadratic_2` (calls it) | D1 |
| algebra | D | `algebra_practice_expand_mixed` | `algebra_practice_quadratic_3` (calls it) | D1 |
| bearings | F | new `_brg_found_compass_any` | `_brg_found_compass_NE`, `_NW`, `_SE`, `_SW` | D2 |
| bearings | F | new `_brg_found_back_bearing` | `_brg_found_back_gt_180`, `_back_lt_180` | D2 |
| constructions_loci | D | new `_cl_d_construct_angle` (30 or 45) | `_cl_d13_construct_45`, `_cl_d14_construct_30` | D2 |
| equations_inequalities | F | `_eq_found_negative_answer` | `_eq_found_two_step` | D2 |
| graphs | F | `_gra_found_04`, `_02`, `_08` | `_gra_found_14`, `_13`, `_15` | D1 |
| graphs | F | new `_gra_scatter_correlation_any` | `_gra_found_10`, `_11`, `_12` (each fixed) | D2 |
| graphs | I | `_gra_inter_06`; new correlation slot | `_gra_inter_15`; `_gra_inter_11`, `_12`, `_13` | D1, D2 |
| graphs | D | `_gra_diff_06`, `_01`, `_04`, `_02`, `_10` | `_gra_diff_13`, `_11`, `_17`, `_16`, `_15` | D1 |
| probability | F | `_prob_found_01` | `_prob_found_13` | D1 |
| probability | D | `_prob_diff_03` | `_prob_diff_17` | D1 |
| pythagoras | F | new `_py_f_is_right_angled` | `_py_f3_is_right_yes`, `_py_f4_is_right_no` | D2 |
| ratio_proportion | I | `_ratio_inter_09`, `_02`, `_03`, `_01` | `_ratio_inter_13`, `_11`, `_12`, `_10` | D1 |
| ratio_proportion | D | `_ratio_diff_03`, `_02`, `_01`, `_04`, `_10` | `_ratio_diff_08`, `_13`, `_07`, `_05`, `_12`, `_18` | D1 |
| sequences | I | `_seq_inter_find_nth_term` (draws d of either sign) | `_seq_inter_nth_term_negative_d` | D2 |
| statistics | F | `_stats_found_06`, `_07`, `_05`, `_01`, `_03`, `_02`, `_04` | `_stats_found_14`, `_15`, `_13`, `_09`, `_11`, `_10`, `_12` | D1 |
| statistics | I | `_stats_inter_07`, `_06`, `_08`, `_05`, `_02` | `_stats_inter_14`, `_13`, `_15`, `_12`, `_10` | D1 |
| statistics | D | `_stats_diff_05`, `_06`, `_03`, `_04`, `_09` | `_stats_diff_11`, `_13`, `_16`, `_14`, `_10`, `_12`, `_02`, `_15`, `_17` | D1 |
| transformations | F | new `_trans_found_reflect_axis`, `_reflect_line_k` | `_trans_found_reflect_xaxis`, `_yaxis`, `_xk`, `_yk` | D2 |
| transformations | I | (kept apart) | none | D2 by template, but reviewed as different skills: `VARIETY_EXEMPT` (section 14) |
| vectors | F | new `_vectors_found_magnitude_triple` | `_vectors_found_magnitude_3_4`, `_6_8` | D2 |
| vectors | D | `_vectors_diff_geometry_proof` | `_vectors_diff_vector_proof_sim` | D2 (proof models, check `solvers_proofs.py`) |

Notes: four D1 groups (the statistics difficult histogram wrappers `_stats_diff_02`, `_09`, `_15`, `_17` and the grouped-mean pair `_stats_inter_02` / `_10`) are found by source only, because their names and contexts vary by draw; they count once. `_trans_found_describe_reflection_axis` and `_describe_rotation_90` share a template but ask about different transformations; they are not retired. The exact list is regenerated by the Phase 0 report and reviewed before Phase 1.
