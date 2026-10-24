# GCSE Maths answer verification plan (step 2)

**Goal (approved by David):** add an automatic test that re-solves generated questions, so wrong answers like the ones fixed in `fbd7685` cannot come back.
**Status:** planned 2026-10-22; decisions confirmed (section 8). Phases 1 to 4 are built (Phase 4: 2026-10-23, section 15); nothing is committed yet, and each phase is one commit, made only when David explicitly asks. Where an older section says static bank items are "pinned" (`register.STATIC_ITEMS`), section 15 supersedes it: 319 of 334 are now re-solved and 15 are listed in `register.STATIC_EXEMPT`.
**Pipeline per phase:** implementer builds, an independent reviewer checks against this doc and the code, fixes, sync to David's laptop, hash parity check, full smoke suite green.

## 1. Where things stand (measured on `fbd7685`)

| Measure | Value |
|---|---|
| GCSE maths topics | 32 |
| Practice (standard) variant slots (topic x tier x variant) | 1,072 (1,069 unique functions) |
| MCQ variant slots | 606 (417 wrap a procedural function, 189 dispatch bank or procedural) |
| Practice slots independently re-solved today | about 52 (4.9%): 46 in `independent_check` plus 6 bearings |
| Topics with no independent re-solving | 24 of 32 (all of algebra, statistics, probability, transformations, angles, circle theorems, trigonometry, mensuration, ratio) |
| Generation cost | about 0.45 s per seed for all 1,072 practice slots |
| What a problem dict carries | `question`, `solution`, `hint`, `correct_answer_raw`, `answer_type` (practice); `options`, `correct_answer` (MCQ). No structured inputs, so today every check parses text. |
| Answer types in use | 29, led by `number` (400), `number_fields` (251), `number_pair`, `algebraic`, `fraction`, `proof_steps`, `linear` |

Bugs found while prototyping the sympy re-solver (not caught by the current structural checks):

1. `changing_the_subject._cts_i_linear_fraction`: key `x=(c*y-2)/(5)`; the literal letter `c` was never replaced by the denominator, so a pupil typing the correct `x=(6y-2)/5` is marked wrong.
2. `changing_the_subject._cts_d_subject_on_both_sides`: can generate `3x + 7 = 3x + 10` with key `x=(3)/(0)` (no solution, division by zero).
3. Cosmetic: `1x + 2y` in `_eq_inter_simult_elim`; `\dfrac{1}{2}2t^2` in the rearranging variants renders like a mixed number.

## 2. Approach: a hybrid, each check matched to the kind of question

| Layer | Applies to | How it re-solves | Brittleness to wording |
|---|---|---|---|
| L1 generic properties | Every slot | Checker round-trip, pupil-typed forms, stated accuracy, MCQ structure; per answer type: substitute the key back in, probability in [0, 1], angle sums, nth term reproduces listed terms, image points match | None (reads the answer only) |
| L2 sympy re-solve from the displayed maths | Algebra families: equations, inequalities, rearranging, simultaneous, quadratics, completing the square, functions, algebraic fractions, sequences, surds | Extract the `\( ... \)` maths, convert LaTeX to a restricted string, parse with the allowlisted parser, solve or simplify, compare with the key | Low: prose is ignored |
| L3 recorded inputs plus a family solver | Numeric word problems: number, ratio, FDP, compound measures, mensuration, trigonometry, bearings, statistics, probability, geometry, vectors, transformations | Generators call a no-op `record(family, **inputs)`; the test activates recording, receives the inputs and recomputes the asked quantity with its own formula | None |
| L4 text regex | Legacy only | Current `independent_check` functions move into L3 solvers in Phase 1, then retire | High (avoid) |

**The recorder hook (`generators/shared/verify_hook.py`).** A `contextvars.ContextVar` sink; `record()` returns at once unless a test has activated it. It never touches `random`, the returned tuple or the problem dict, so pupil output stays byte-identical (checked by `verify_no_output_drift`). One line per variant, placed after the inputs are drawn, for example `record('direct_proportion', x1=12, y1=84, x2=17, ask='y', dp=None)`.

- **Presence guard:** every recorded numeric input must appear in the plain question text, or be declared `derived=`. This stops recorded values drifting from shown values, which would make the check self-confirming.
- **Independence rule:** a solver may import only `math`, `fractions`, `decimal`, `sympy` and `generators/shared/rounding.py`; never the generator module or its helpers.

**MCQs** are keyed on the recorded family, not the variant name. The keyed option must equal the recomputed value (numeric or symbolic comparison, not text), and no distractor may be equivalent to the key (`0.5` and `1/2` clash). Fixed hand-written bank items with no recorder are reviewed once and hash-pinned (section 3).

**Quizzes** (`lesson_quiz.build_lesson_quiz`) reuse the generators: one seeded quiz per topic runs through the same checks.

## 3. Coverage register and ratchet

`scripts/gcse_verify/register.py` holds `EXEMPT = {'slug/variant_fn': (category, reason)}` with categories:

- `pending`: not done yet; must reach zero by the end of Phase 3.
- `self-marked`: written descriptions and proofs that the checker does not mark; the solution's final statement is still checked where possible.
- `static-bank:<sha1>`: a reviewed fixed MCQ item; any edit changes the hash and fails the test until reviewed again.
- `infeasible`: needs a reason of at least 20 characters.

The test fails when a slot is neither verified nor exempt (for example a new variant without a solver), an exempt slot now verifies (stale exemption), a registered solver returns "could not read" on any seed, or the `pending` count exceeds `PENDING_CEILING` (each phase lowers it). A coverage table (verified, exempt by category, total, per topic and per mode) prints on every run.

## 4. Test design

**Files.** `scripts/test_gcse_maths_verification_smoke.py` (picked up by `run_smoke_tests.py`); helpers in `scripts/gcse_verify/` (`latex.py`, `solvers_number.py`, `solvers_algebra.py`, `solvers_geometry.py`, `solvers_stats.py`, `mcq.py`, `forms.py`, `register.py`, `report.py`). The existing `test_gcse_maths_correctness_smoke.py` stays as the structural check; its `independent_check` code moves out.

**Named checks (each prints a tally).**

- `verify_practice_resolve`: L2 and L3 recomputation against `correct_answer_raw`.
- `verify_mcq_key`: keyed letter equals the recomputed value; exactly one key; no equivalent distractor.
- `verify_checker_roundtrip`: the key and common typed forms from `forms.py` are accepted; mutations are rejected. Forms (decision 2, generous): `x = 3` and `3`; Unicode minus; `1,548`; trailing zeros (`20.00`); quadratic roots in either order; coordinates with or without brackets; reordered or expanded algebra; fractions with spaces; unsimplified fractions unless the question says "simplest form"; an exact decimal for a fraction unless it says "as a fraction".
- `verify_stated_accuracy`: if the question says N d.p., N s.f. or "nearest", the key equals half-up rounding of the exact recomputed value; without a stated accuracy the key must be exact.
- `verify_properties`: L1 checks for slots without an L2 or L3 solver yet (counted as partial; they do not clear `pending`).
- `verify_no_output_drift`: every slot for 3 seeds with recording on and off; SHA-256 of question, solution, key and options identical.
- `verify_quiz_items`: one seeded quiz per topic.

**Determinism.** Seed per question is `zlib.crc32(f'{slug}/{tier}/{fn}') + run` (not `hash()`, which is randomised). Table-row walking (`make_choice`) is reused so every hard-coded row is exercised. sympy point sampling uses `random.Random(0)`.

**Failure report** (one block per slot and message, at most 3 seeds):

```
[answer] changing_the_subject/intermediate/_cts_i_linear_fraction seed=3121
  question  : Make x the subject of the formula y = (5x + 2)/6.
  keyed     : x=(c*y-2)/(5)
  recomputed: x = (6y - 2)/5   (layer L2, sympy)
  reproduce : python scripts/test_gcse_maths_verification_smoke.py --only changing_the_subject/intermediate/_cts_i_linear_fraction --seed 3121
```

`--json PATH` writes the same data.

**Comparison rules.** Algebra: equivalence by exact evaluation at 4 random rational points, `simplify` only if inconclusive; plus-or-minus roots and either order accepted; free symbols must match the question's symbols (catches the stray `c`); sympy's own names (`E`, `I`, `S`, `N`, `Q`, `O`) are always overridden with plain symbols. Numbers: exact `Fraction` or `Decimal`; `number_estimate` keeps its tolerance. Intermediate rounding is mirrored only where the question tells pupils to round an intermediate value.

**Security.** No `eval` and no bare `sympify`; parsing goes through `answer_checkers._safe_sympify` or the same allowlist. Input capped at 300 characters, exponents at 10, polynomial degree at 4. `signal.alarm` is not used (not available on Windows); the caps make timeouts unnecessary.

**Runtime.** Default run: 10 seeds per practice slot and 4 per MCQ slot (about 13,000 questions) in 30 s or less; a warning prints above 45 s. *Budget note (2026-10-23, Phase 3 review): David accepts a default run of up to about 35 s on this machine, so seeds are not cut to meet 30 s; the run measured 28 to 31 s after the review.* `--deep` (Phase 4): 200 seeds per slot plus a 40-seed quiz sweep, run manually (decision 3).

## 5. Phases (one commit each, only when David asks)

### Phase 1: framework plus number, ratio and numeric geometry

- **New:** `generators/shared/verify_hook.py`, `scripts/gcse_verify/*`, the new test.
- **Changed:** `record()` lines in `maths_num_stats_prob_rat.py` (number and ratio parts), `maths_basic_topics_mcq.py`, `maths_bank_procedural_mcq.py` (number-type functions), `maths_pythagoras.py`, `maths_compound_measures.py`, `maths_mensuration.py`, `maths_bearings.py`, `maths.py` (trigonometry).
- **Work:** move the existing Pythagoras, compound measures, bearings and surds checks into L3 solvers; build the register with every other slot `pending` and set `PENDING_CEILING` to that count; add the forms table and stated-accuracy check.
- **Topics:** bidmas, multiples_factors, decimals, fdp, number, ratio_proportion, pythagoras, compound_measures, mensuration, trigonometry, bearings (practice and MCQ); about 430 practice slots.
- **Likely findings:** intermediate rounding, direct versus inverse proportion slips, unit conversions, reverse percentages, bounds, trigonometry rounding.
- **Done when:** no `pending` slots in these topics; `verify_no_output_drift` passes; run time 15 s or less; AI_HANDOFF updated.

### Phase 2: algebra via sympy (L2), L3 only where text gives out

- **Topics:** algebra, equations_inequalities, changing_the_subject, sequences, surds, simultaneous_equations, completing_the_square, quadratic_simultaneous_equations, graphs, graphical_simultaneous_equations, algebraic_fractions, functions, algebraic_proof; about 340 practice slots.
- **Checks:** solve stated equations; inequalities including sign direction; rearranging for the subject; simultaneous values substituted into both equations; nth term reproduces listed terms; functions composition and inverse; algebraic fractions equivalence and excluded values; graphs gradient and intercept; proof stays `self-marked` but its identity is checked with sympy.
- **Fix in this commit:** the two `changing_the_subject` bugs and the cosmetic issues from section 1.
- **Done when:** no `pending` slots in these topics; sympy share of runtime 12 s or less.  *Built 2026-10-22, see section 10.*

### Phase 3: statistics, probability, transformations and the rest of geometry

- **Topics:** statistics, probability, transformations, geometry_angles, circle_theorems, similarity_congruence, constructions_loci, vectors; about 300 practice slots.
- **Checks:** recorded data feeds mean, median, IQR, grouped estimates (estimate tolerance) and pie-chart angles; exact probability with and without replacement, Venn regions summing to the total; transformations applied to recorded vertices, and stated centre, angle or factor for "describe" questions; polygon sums and angle facts; circle theorem relations.
- **Done when:** `pending` is zero across all 32 topics and the ceiling constant is deleted; at least 90% of practice slots and 80% of MCQ slots fully verified, the rest categorised exemptions.

### Phase 4: deep mode and exemption burn-down

- `--deep` mode (200 seeds per slot plus a 40-seed quiz sweep, about 5 to 10 minutes), run manually; no scheduled CI job (decision 3).
- Review `infeasible` and `static-bank` exemptions; target 95% practice and 90% MCQ fully verified.
- **Done when:** a clean deep run and a reviewed, dated exemption list. **Done 2026-10-23; see section 15.**

## 6. Policy when a check fails

1. Reproduce with `--only` and `--seed`, decide which side is wrong.
2. **Generator wrong** (wrong key, inconsistent question, degenerate case, wrong stated accuracy): fix it in the same phase commit (decision 4); note the changed variant in the commit message.
3. **Solver wrong** (missed alternative answer, convention): fix the solver and add a regression case to its unit table.
4. **Checker too strict or lenient:** fix `answer_checkers.py` and add a probe.
5. **Exempt only when re-solving is infeasible.** An exemption is never a way to make the build green.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| False positives from equivalent forms | Point-evaluation equivalence, plus-or-minus and order handling, explicit forms table, solver unit tables |
| Self-confirming checks | Presence guard; solvers never import generator code |
| Wording changes break solvers | L3 ignores prose; L2 reads only maths segments; "could not read" fails loudly |
| sympy slowness or blow-ups | Numeric points first; input caps; per-phase timing in the report |
| Parsing generated text as code | No `eval`; allowlisted `_safe_sympify`; length and exponent caps |
| Hook changes pupil output | `verify_no_output_drift`; `record()` has no random draws or side effects |
| Static banks silently edited | SHA-pinned `static-bank` exemptions |

## 8. Decisions (confirmed 2026-10-22)

1. **Inputs:** one-line `record(...)` calls in the generators (recommended); pupil output stays byte-identical.
2. **Typed forms:** generous (recommended): unsimplified fractions unless "simplest form"; exact decimals unless "as a fraction"; trailing zeros.
3. **Deep run:** manual only (not the recommendation); `--deep` exists but no scheduled CI job.
4. **Bugs found:** fixed in the same phase commit (recommended).
5. **Fixed hand-written MCQ items:** reviewed once and hash-pinned (recommended default; not separately asked).

## 9. Phase 1 build notes (2026-10-22)

**Built.** `generators/shared/verify_hook.py` (a `ContextVar` sink; `record()` is a no-op outside `recording()` and never draws random numbers); `scripts/gcse_verify/` (`latex`, `registry`, `core`, `engine`, `harness`, `solvers_number`, `solvers_geometry`, `mcq`, `forms`, `register`, `report`); `scripts/test_gcse_maths_verification_smoke.py`. Options: `--deep`, `--only NAME[,NAME]`, `--seed N`, `--json`, `--print-digests`. The test is picked up by `run_smoke_tests.py` through its `test_*_smoke.py` glob.

**Coverage (1,678 slots; the 11 Phase 1 topics have 621).**

| Category | Count | How |
|---|---|---|
| Practice slots re-solved | 390 of 390 | recorded inputs re-solved by independent solvers, 20 seeds per slot (`--deep`: 200) |
| MCQ slots re-solved directly | 42 | number and ratio_proportion wrap one procedural function per slot |
| MCQ dispatch slots | 189 (9 topics x 21) | each slot draws at random from a bank plus, in the difficult tier, procedural functions; covered by 24 procedural functions re-solved over 8 seeds (`--deep`: 100) and 159 static bank items |
| Static bank items pinned | 159 | reviewed by hand; sha1 pin per item; structure check (A to D, one key, unique option texts) |
| Pending | 1,057 | all other topics; `PENDING_CEILING = 1057` (ratchet: the test fails if the count rises, and also if it falls without the ceiling being lowered) |
| Exempt | 0 | nothing in Phase 1 needed an exemption |

**Deviation from the plan: per-item pins, not per-slot.** The plan pinned one sha1 per MCQ slot. Dispatch slots draw randomly from a pool, so a slot has no single content and a per-slot hash would be meaningless. Each static item is pinned instead, over its plain question, its sorted option texts and its keyed text, so shuffling options or editing solution wording does not trip it. Editing or adding an item fails the test until the item is re-checked by hand and its digest updated in `register.STATIC_ITEMS` (`--print-digests` lists them). The plan's `static-bank:<sha1>` register category therefore becomes a per-topic `STATIC_ITEMS` table.

**Checks.** `practice_resolve`, `mcq_key`, `checker_roundtrip` (7,500 typed forms in deep mode: trailing zeros, thousands commas, Unicode minus, spaced fractions, `000` bearings; wrong forms rejected), `stated_accuracy` (stated d.p., s.f. or "nearest X" must match half-up rounding of the exact value; with none stated the key must be exact, which found the missing "to the nearest penny" below), `properties` (Phase 1 topics only: pending topics have known gaps such as three-option items and keys in checker formats, which belong to later phases), `no_output_drift` (every slot, 3 seeds, recording on and off; SVG title ids are normalised because they come from a process-wide counter). Also: an AST independence check on the solver modules (stdlib, sympy, `generators.shared.rounding` and siblings only; no `eval`/`exec` anywhere in the package), a solver unit table with a negative control, a tampered-key negative control (every wrong key tried, 340 of 340 caught) and register consistency.

**Runtime.** Default run about 12 s (limit 30 s); `--deep` about 28 s. Seeds are `zlib.crc32(f'{slug}/{tier}/{fn}') + run`. Deep sweeps at seed offsets 0, 1000, 5000, 9000, 13000, 17000 and 21000 were used to find the rarer bugs below.

**Pupil output against HEAD.** Generating 3,726 Phase 1 questions on HEAD and on the working tree (6 seeds per slot): 298 differ, spread over 91 slots, all attributable to the fixes below. Every other slot is byte-identical, so the `record()` lines change nothing.

**Bugs found in the generators and fixed (all in this phase).**

Number, ratio and decimals:
- `_number_inter_calculator_estimate_fraction`: the 1 s.f. divisor did not divide the estimate exactly and rounding used `round(x/10)*10`; the divisor is now picked so its 1 s.f. value divides exactly. `_number_found_estimate_simple` now rounds with the shared 1 s.f. helper.
- `gcse_bidmas_hard`: could produce a recurring decimal with no rounding instruction; it now keeps only terminating quotients.
- `_ratio_inter_garden_compost` and the milk-and-syrup variant: part (c) asked "how much more" of one quantity than another when the other could be larger, and the working subtracted the wrong quantities (`608 - 76 - 266`); parts are now ordered and the working is correct. `_ratio_share_three` gives the first place the largest share.
- Ratio MCQs: "simplest form" key now genuinely simplified; the "bigger share" item keyed the first part even when it was smaller.
- Best-buy questions (practice and MCQ): equal unit prices left no right answer; ties are now avoided and compared in whole pence.
- Repeated percentage change, compound interest and depreciation: float error lost half-penny and half-pound ties (1285.125 keyed 1285.12); now exact. `gcse_fdp_compound_percentage` also gains "to the nearest penny" when the answer needs it.
- `_number_inter_calculate_to_sf`: `4.1 x 0.35` evaluated to 1.4349999 and rounded the wrong way; now exact.
- Recurring decimals (fdp and decimals): the recurring picker could return `3/15 = 1/5`, a terminating decimal presented as recurring; it now requires a denominator with a prime factor other than 2 or 5. The recurring display now shows the repeating block enough times to read it (`0.666...`, not `0.6...`).
- `gcse_fdp_decimal_to_percentage`, `gcse_fdp_fraction_to_percentage`: key `56.00000000000001`. `gcse_dec_proc_map_scale`, `gcse_dec_practice_word_unit_price`, `gcse_fdp_reverse_percentage_two_step`, `gcse_fdp_profit_loss_percentage`: no stated accuracy for a rounded answer; each now says what to round to. `gcse_dec_proc_multi_step_shop` could land on a half penny.

Geometry and measures:
- Mensuration: composite cylinder plus hemisphere, tank, garden plot, cone from slant, prism surface area, open box, silo, frustum tank, hemisphere plus cone, segment, density, submerged sphere: keys were built from intermediate values rounded to 2 d.p. and so differed from the value a correct pupil gets; keys now use unrounded values and say so in the solution. Area-to-length and pyramid items gain a "2 d.p." note; the pyramid wording was wrong ("A pyramid has a rectangular base").
- Bearings: `_brg_diff_sine_rule_find_distance` used sin C instead of sin B (wrong key). `_brg_diff_position_from_two_bearings` was rewritten because the answer was not determined by the bearings shown. Two-leg, return, three-leg and port multipart questions now use unrounded components; `bearing_from_south` asked for one value but keyed two; several distances were asked without the 1 d.p. they were keyed to.
- Trigonometry: isosceles apex angle and 3D angle used rounded intermediates.
- Pythagoras MCQ: cuboid diagonal option B ("sqrt50 cm only") duplicated the answer; now "5 cm".

Static MCQ banks (hand-written items):
- fdp "Which is the largest?" was keyed 38% when 0.4 and 2/5 were larger (options changed to 0.35 and 1/3).
- decimals 0.3 recurring item: 3/9 was also correct (now "in its simplest form").
- mensuration frustum key 488.69 corrected to 490.09; silo key 636.61 corrected to 636.70.
- bearings item "70 km / 90 km AB" key 98.62 corrected to 93.22, with its solution.
- trigonometry item wording ("opposite 3 and adjacent 4").

Procedural MCQ functions (`maths_bank_procedural_mcq.py`): fdp reverse-percentage and percent-change gave non-whole originals and malformed LaTeX; decimals divide could recur; multiples/factors "factor of" distractors included true factors; mensuration circle mixed pi and 3.14; trapezium area non-integer; compound-measures speed and density divided unevenly; trigonometry find-side lacked "to 1 d.p."; the trigonometry exact-value item had an option (`cos 45 = sqrt2/2`) that was also correct.

**Not done / carried forward.**
- Solvers are in `solvers_number.py` and `solvers_geometry.py`; there is no `solvers_algebra.py` or `solvers_stats.py` yet (Phases 2 and 3).
- `verify_quiz_items` (one seeded quiz per topic) is not built; it was not in the Phase 1 scope list.
- The existing `independent_check` code in `test_gcse_maths_correctness_smoke.py` was left in place rather than moved out; the new solvers supersede it for Phase 1 topics.
- Procedural MCQ coverage is by direct function calls rather than through the dispatch slots, because a dispatch slot's content is random.
- Nothing is committed; the changes are in the working tree for review.

### Phase 1 review notes (independent reviewer, 2026-10-22)

**Confirmed.** Every solver recomputes from recorded inputs with its own formula; none imports or calls generator code (the AST check now also covers `engine.py` and any future `solvers_*.py`, and `from . import x` and `__import__` can no longer slip past it). Re-derived by hand: sine rule OB = OA sin A / sin B; the two-observer triangulation (N = sep / (tan a − tan b)); frustum 156π = 490.09; silo 608π/3 = 636.70; AB² = 70² + 90² − 12600 cos 70° gives 93.22; the "how much more" ratio parts; the rounding fixes. The numeric static bank items in mensuration, trigonometry, bearings, compound measures and Pythagoras were re-checked by hand. Pupil output against HEAD (6 seeds per slot): the 298 changed questions (91 slots) all belong to fixed variants, and 303 after this review's fixes (still 91 slots); every other Phase 1 slot is byte-identical, and output is identical across processes with different `PYTHONHASHSEED`. No `eval`, `exec` or `sympify` in the package; `answer_checkers.py` is untouched. Slot enumeration with 400 seeds finds the same 1,678 slots as 40.

**Mutation tests** (each applied alone, test run, file restored): frustum key + 1, frustum rounded to 1 d.p., sine rule back to sin C, ratio share off by one, speed as d × t, procedural density + 1, procedural trapezium + 2, static bearings key 93.22 changed to 93.23, `record()` removed from the frustum variant, equal-parts ratio MCQ restored, garden ratio without the larger-first ordering, a solver importing `generators.gcse.maths`, and a wrong `sign=` on a percentage decrease. All 13 made the test fail.

**Found and fixed.**
- Generator, wrong: `ratio_proportion_mcq` type 2 could ask for "the larger share" of a 5:5 ratio, with filler options "1" and "0"; equal parts are now avoided. The `ratio_larger_share` solver now fails when the shares tie, and the "how much more" solvers (`ratio_share_diff`, `ratio_garden`, `ratio_prize`) fail when the difference is not positive, so these slips cannot return.
- Generator, wrong: `_number_diff_best_value` could still give equal unit prices (5 for £2.96 against 10 for £5.92, found by a deep sweep at seed offset 41000); it now uses the same whole-pence tie guard as the ratio and MCQ best-buy items.
- Generator, accuracy: `_mens_proc_circle` keyed 28.3 for 3.14 × 9 = 28.26 with no accuracy stated; it now says "to 1 d.p.". The stated-accuracy check did not run on procedural MCQ functions, which is why this was missed; it now does.
- Checks: stale exemptions and malformed `EXEMPT` entries (wrong key format, category or a reason under 20 characters) now fail, as section 3 requires. Static and generated MCQ items now fail when a distractor has the same value as the key (0.5 and 1/2), unless the question is about the form (simplest form, three-figure bearings). An `arith` record must match the expression shown in the question, and a recorded `sign=` must match increase or decrease wording. The checker round-trip now also types an unsimplified fraction (unless the question asks for the simplest form) and the exact decimal of a terminating fraction (unless it asks for a fraction), as decision 2 requires. Mismatches are now labelled "accuracy" only when the key is a genuine rounding of the exact value (a 2% closeness test labelled an off-by-one share as an accuracy slip); both labels fail the test as before. `brg_two_ships` now takes the reflex-safe angle (360° minus the difference above 180°).

**Not changed (noted for later phases).** About 30 records use the generic `quotient` and `product` families, so the formula choice (for example speed = distance ÷ time) is stated in the record line next to the generator rather than in a named solver; the recomputation is still independent of the generator's arithmetic, but a semantic family per formula would be stronger. String inputs other than `sign` and `expr` (`want`, `known_kind`, `direction`) are not cross-checked against the wording. The deep sweep was extended to offsets 41000 to 90000 (six more runs): clean after the fixes above.

## 10. Phase 2 build notes (2026-10-22)

**Built.** `scripts/gcse_verify/solvers_algebra.py` (about 3,300 lines, family `alg` with a `task` name per question shape) and `solvers_algebra_parse.py` (a hand-written recursive-descent parser for the displayed `\( \)` maths, plus `tex_to_text`; no `eval`, `exec` or `sympify`, so the independence AST check passes). Each solver reads the displayed question, re-solves it with sympy, and judges the key (`judge` for value, set, tuple, pair, inequality and text keys; `judge_pred` for MCQ options; `form` checks for "simplest form", "write in the form" and similar). Sequence, surd, graph and proof tasks parse the question text. Every algebra practice and MCQ variant carries a one-line `record(...)` or the new `@verifies(family, **inputs)` decorator (`generators/shared/verify_hook.py`; it records after the function returns, draws no random numbers and changes no output). `forms.py` now types every answer type used by these topics (only `proof_steps` stays untyped) and has a `tampered_keys` negative control.

**Coverage (1,678 slots; the 24 verified topics have 1,350 practice-and-MCQ slots).**

| Category | Count | How |
|---|---|---|
| Practice slots re-solved | 713 of 713 (Phase 1 390 + algebra 323) | 14 seeds per algebra slot (`practice_algebra`; `--deep`: 200), 20 for the Phase 1 topics |
| MCQ slots re-solved directly | 147 | all MCQ slots of changing_the_subject, completing_the_square, quadratic_simultaneous_equations, graphical_simultaneous_equations, graphs, algebraic_fractions, functions, algebraic_proof, plus Phase 1 |
| MCQ dispatch slots | 291 | covered by 37 procedural functions and 240 pinned static bank items |
| Static bank items pinned | 240 (algebra 19, equations_inequalities 15, sequences 18, simultaneous_equations 10, surds 19 new) | sha1 per item in `register.STATIC_ITEMS`; re-pin after editing a bank item |
| Pending | 527 | `PENDING_CEILING` lowered from 1057 to 527 |
| Negative control | 664 of 664 tampered keys rejected | includes proof tampering (0 mutation survivors) |
| Checker round trips | 3,328 | canonical and equivalent forms accepted, wrong values rejected, against the real `answer_checkers.py` |

**Runtime.** Default run about 22 to 25 s (Phase 1 budget was 15 s; the task limit for this phase is 30 s). Reached with a linear fast path for rearrangement, a substitute-the-key fast path for non-linear rearrangement, per-topic seed counts, and caching `enumerate_slots`. `--deep` is manual only; run at seed offsets 0, 1000, 41000 and 77777 (see below).

**Deviations from the plan.** (1) Static bank items are pinned item by item, not whole banks, as in Phase 1. (2) Algebra topics use 14 seeds per slot, not 20, to hold the runtime. (3) Proofs stay self-marked, but each proof's identity and step sequence are checked (recurring decimals, odd sum, divisibility). (4) The sympy share of runtime was not measured separately; the whole run is under the budget.

**Bugs found and fixed** (generators; each now has a check that would catch it).
- changing_the_subject: `_cts_i_linear_fraction` put a literal `c` in the key; `_cts_d_subject_on_both_sides` could give x = 3/0 (now `while c == a`); `\dfrac{1}{2}2t^2` and `1t^2` shown for a half coefficient (`_half_coeff_tex(2)` now returns ''); "Divide by 1" step; `_cts_i_F_ma` printed "F = 8m".
- algebra / equations_inequalities / simultaneous_equations: `1x`, `1y`, `0x`, `+ 0` and `+ -` shown in questions (now via `coef`); `y = 3x + 0`; the bank item "2x+3y=12, 5x-y=9, eliminating x gives 3y=3" was wrong (replaced by 2x+3y=12, 2x+y=8); proportional baskets in `_sim_d_apples_oranges` (no unique solution); several `_eq_diff_*` and `_eq_inter_*` items with wrong or ambiguous wording ("positive" root, phone-plan multipart, quadratic-formula part).
- `_eq_proc_inequality_flip` keyed `x < b//a`, which is wrong (correct `x > -b/a`); rewritten.
- surds: `_surd_largest_square_factor` knew only a short list, so `gcse_surds_multiply` keyed 5√4 for √10 × √10 and `gcse_surds_exact_area` mishandled 49; it is now general. `1√6` shown. Bank: `(2+√3)(2-√3)` had duplicate values among options; `√2×√8+√18` keyed 7√2 (correct 4+3√2, option A); `√72÷√8` had a "√9" option equal to 3; the `1/(√5-√3)` solution text was wrong. Procedural: `_surd_proc_multiply` with a == b, duplicate distractors in `_surd_proc_add_like` and `_surd_proc_rationalise`.
- sequences: `_seq_inter_two_sequences_same` met at n = 0 or a fraction (and its solution text replaced the letter n inside words); `_seq_inter_first_term_over` was off by one (now strictly greater); `_seq_diff_convergence_check` used unreduced ratios and a wrong n; several multipart questions never said which part to enter; `_seq_found_continue_pattern` was ambiguous; `1n^2` style coefficients.
- algebraic_proof: `_ap_f_sum_consecutive` had the wrong parity in its key; counterexample questions had several valid answers (now ask for the smallest); k/j clash in proof steps; `_ap_mcq_even_odd` had two correct options; the option "It can be prime only" replaced by "It is always prime".
- completing_the_square: a coefficient of 0 allowed for p; "maximum profit" lacked the unit (thousands of pounds).
- quadratic_simultaneous_equations: `a = 0` lines; a duplicate second-solution distractor; unordered answer boxes (roots now sorted, hint says so).
- graphical_simultaneous_equations: a parabola MCQ distractor equal to the other solution; no-solution wording; answer boxes now say "smaller x first".
- graphs: duplicate speed options; a reciprocal key that did not terminate; a weak "no correlation" scatter; three-option correlation items (now allowed by the structure check); `1x` in a cubic.
- functions: "-1/1" as a key (now "-1").
- Found only by the deep runs (offsets 1000 and 41000): `_sim_d_cafe_prices` and `_sim_i_word_tickets` could draw two days in proportion, so the equations were parallel; `_cts_d_subject_on_both_sides` could key x = 0 (as `0/-1`, which the loose `algebraic` checker also accepts as `0/-2`); `_eq_inter_angle_equation` could show "+ 0"; four scatter-graph generators (`_gra_scatter_line_of_best_fit`, `_gra_diff_scatter_multipart` and the estimate-from-line variant) could draw a line of best fit that missed the mean point by 2 or more (now redrawn until within 1).

**Drift against HEAD.** 12 seeds x 530 algebra slots (6,360 generations): 376 slots byte-identical, 154 slots differ in 953 generations. Every difference traces to one of the fixes above (coefficient display, sorted roots, edited bank items, hints, sequences, surds). Detail was kept outside the repo.

**Checker findings, not changed (for the checker owner).** `algebraic` is value equivalence only, so an unexpanded or unfactorised form is accepted for an "expand" or "factorise" question; `linear` ignores the variable letter (`y=2` accepted for 2); `surd` accepts unsimplified equal values (`√3240`, `9√40`); a surd binomial is rejected as `-4√5+9`; `formula_fraction` is strict text (`(p-1)|6` rejected for `2p-2|12`); `keyword` has substring leniency (`14:30x` accepted); `linear_equation` rejects `y=-2*x-7`; `number_estimate` accepts a wide tolerance band; `number_pair` and `number_fields` are order dependent, which is why generators sort roots and say so in the hint.

**Deep runs.** `--deep --seed N` (about 3 minutes each, 142,600 practice questions) at offsets 0, 1000, 41000 and 77777 all pass after the fixes above. The checker round trip passes the question's `answer_field_types` to `number_fields` (as `app.py` does); a plain-text echo is accepted if it passes with or without the types.

### Phase 2 review notes (independent reviewer, 2026-10-23)

**Confirmed.** Solvers re-solve from the displayed `\( \)` maths and the recorded question inputs; none imports generator code, and none reads a problem's `solution` or `hint`. The `@verifies` decorator records only the constants written in the decorator line (fixed when the module loads), after the function returns, so a generator cannot pass its own answer through it. The few dynamic `record('alg', ...)` lines (`two_equations_multipart`, `phone_plans`, `ineq_linear_rec`) record question inputs, which the presence guard ties to the question text. `keyed_text` decorators hold a hand-written expected option for conceptual MCQs; they act like a static pin. Hand-checked about 45 generated algebra questions across all 13 topics (linear and simultaneous equations, rearranging, completing the square, quadratic simultaneous, functions and inverses, algebraic fractions, sequences, surds, proofs, graphs) plus the listed fixes (literal `c`, `x = 3/0`, the inequality flip, `√10 × √10 = 10`, `√2×√8+√18 = 4+3√2`, smallest counterexamples, parallel equations, scatter lines): all keys correct.

**Found and fixed.**
- Parser safety: nested powers were capped per exponent only, so `((9^10)^10)^10` built a 1,000-digit integer and one more level raised an uncaught `ValueError`. `solvers_algebra_parse.py` now rejects nested powers whose exponents multiply beyond 100 (a nested `f(f(x))` call counts as a power of 10), brackets nested deeper than 40, and turns any arithmetic error into `Cannot`.
- `solvers_algebra.py` still called `sympy.sympify` in three places (on solver-computed numbers, not on text). Replaced by `num()`, which accepts only numbers; the independence check now also fails on `sympy.sympify`, `sympy.parse_expr` and `sympy.S`.
- Probability, statistics and graphs MCQs (Phase 2 edit to `maths_num_stats_prob_rat.py`, undocumented): the new duplicate-distractor filter compared only the leading number, so with a key of 1/2 it dropped 1/6 and 1/3 and filled in 0 and 1. It now compares whole values (0.5, 0.50 and 1/2 still clash; 1/6 and 1/2 do not). Against HEAD, probability now differs only where HEAD showed two equal values (2/5 and 4/10, 0.5 and 0.50, 1/2 and 3/6).
- Answer boxes marked in order with nothing saying which value goes first: graphs "Find the roots" (3 slots) keyed the roots unsorted under "First root / Second root"; the graphs multipart asked for "one point" then "the other point" of intersection; "First integer / Second integer" in the consecutive-integers quadratic. Keys are now sorted and labelled smaller and larger (the intersection part asks for the point with the smaller x-coordinate); the ratio pair labels name their ratio part. A new `properties` check (`unordered_box_errors`) fails when two boxes of the same kind have no order stated, or are labelled smaller and larger but keyed the other way.
- Solution text: `y = -2^2 = 4` (now `(-2)^2`); a `t` equation factorised as `(x - 11)(x - 14)`; `x = 3/(-2)` and `x = -13/-2` (fractions now in lowest terms with a positive denominator, in the key too); `-1x`, `1n^2`, `1(13)^2`, a repeated `x = 2` line, `+ 0`, `3(1x  + 2)` and an unclosed `\(` in the substitution steps.

**Answer checker (`generators/shared/answer_checkers.py`).**
- Fixed: the surd binomial form (key `const|coef|rad|sign`) read a surd-first answer's sign as the constant's sign, so for 9 − 4√5 it accepted `4√5-9` and `√5-9` (both wrong) and rejected `-4√5+9`; `9-4sqrt(5)` was also rejected. It now reads the sign that belongs to each term.
- Fixed: `linear_equation` accepts `y=-2*x-7`, `y = -2×x - 7` and a Unicode minus.
- Unit cases added to `scripts/test_answer_check_smoke.py`; `forms.py` now types the surd-first form and `2*x`, and tries the old wrongly accepted surd-first negative as a wrong answer.
- Left for David (not small or not safe to change here):
  1. `algebraic` checks value only, so the question's own unexpanded or unfactorised expression is accepted for "expand" or "factorise". Recommendation: generators pass a form flag (`expanded`, `factorised`) and the checker checks the structure as the solver's form check already does.
  2. `formula_fraction` is strict text, so correct equivalent answers are rejected (`b-d|c-a` for `d-b|a-c`, `p-1|6` for `2p-2|12`). A value check would need sympy, which means adding the type to `SYMPY_ANSWER_TYPES` (session-bound keys only); recommended, with a probe for each case.
  3. `linear` ignores the letter (`y=2` accepted when the key is `x=2`). Recommendation: reject with "check the letter" only when the key names a letter.
  4. `surd` accepts unsimplified equal values (`√3240` for 18√10) even when the question says "simplify". Recommendation: a "simplest form" flag, as in item 1.
  5. `number_estimate` bands (±3 to ±5 on scatter estimates) are wide but deliberate; recommendation: keep, and tie each band to the grid spacing of its graph.
  6. `keyword` substring leniency (`14:30x`) is minor; leave.

**Mutation tests** (each applied alone, full default test run, file restored and checked by SHA-256): wrong sign in a linear key, off-by-one quadratic-simultaneous root, swapped simultaneous solution, wrong rearrangement, `@verifies` removed, wrong nth term, wrong completed-square constant, the inequality flip restored, wrong inverse function, wrong surd coefficient, proof parity swapped, the literal `c` restored, the old ceiling rule in "first term over", and a drawn graph that differs from its record: all 14 failed. A 15th, relabelling a `rearrange` decorator as `solve_linear`, passed correctly: for a one-letter equation both tasks give the same answer.

**Drift against HEAD** (re-run after all fixes, 8 seeds × 1,678 slots = 13,424 generations): 1,108 generations in 258 slots differ, and every differing slot was read by topic and traced to a documented fix. The 11 Phase 1 topics are byte-identical to the reviewed Phase 1 state (3,726 generations). No slot outside Phases 1 and 2 changes except the 9 probability MCQ generations above.

**Runtime and determinism.** Default run about 25 s on this machine (limit 30 s); the ratchet fails if pending slots rise or fall without lowering `PENDING_CEILING`. `--deep` passes at seed offsets 0 and 23000.

## 11. Checker decisions (2026-10-23)

David approved five of the six items left in the Phase 2 review notes and said to leave the sixth. Built and tested; nothing committed. No static, JS or template file changed, so there is no `?v=` or `CACHE_VERSION` bump (the feedback text reaches the page through the existing `feedback` field of `/api/v1/problems/check`, which `site.js` already prints).

**1. Expand and factorise forms (`algebraic`).** A generator sets `answer_form` on the problem (`'expanded'` or `'factorised'`, constants `FORM_EXPANDED` and `FORM_FACTORISED` in `answer_checkers.py`). `check_algebraic(..., form=)` first runs the old value check; when the value is right it also checks the written structure of the pupil's answer on the unevaluated SymPy tree. Expanded means no sum is still multiplied or raised to a power, and the like terms are collected (`2x^2+8x+x+4` is refused). Factorised means a product (or a power of a bracket) whose every bracket is irreducible with no common integer factor left (`2(12x+9)` is refused as partly factorised). A right value in the wrong form returns `correct: false`, a `wrong_form` kind and a kind message: "That's equal, but the question asks you to expand it.", "That's equal, and nearly there. Now collect the like terms to finish.", "That's equal, but the question asks you to factorise it fully.", "That's equal, but you can factorise it further. Is there a bigger common factor to take out?". A wrong value gets the ordinary "Not quite" message. Wired into every typed expand or factorise variant in GCSE maths: `algebra_practice_expand_binomial`, `algebra_practice_expand_mixed` (and `algebra_practice_quadratic_3`, which calls it), `algebra_practice_factorise_hcf`, `_ap_f_expand_consecutive`, `_ap_i_identity_expand` and `gcse_surds_identity`. The surd `p + q√r` expand variants are left without a flag because the key format already fixes the expanded shape (a product does not parse); the MCQ expand and factorise items have no typed answer. The verification smoke finds expand and factorise slots by their recorded `@verifies` task and fails if one lacks the flag, if a flag sits on a question that does not ask for it, or on a type that ignores it.

**How the form travels.** `problem['answer_form']` is set by the generator, stored in the session problem like the other answer metadata, and read by `app.py` from the session-stored problem only (never from the request body; a body that sends `answer_form` or `form` is ignored, and a problem with no stored form keeps the old value-only check). `lesson_quiz.grade_lesson_quiz_problem` and `class_assignments.grade_frozen_answer` read it from their stored problems the same way. It is not added to `_problem_client_payload`, so the client sees nothing new. `check_answer(answer_type, raw, user, form=None, subject=None)` refuses an unknown form with `invalid_answer_form` and ignores a form on a type that does not use one.

**2. `formula_fraction` accepts any equivalent formula.** `(b-d)/(c-a)` for `(d-b)/(a-c)`, `(2p-2)/12` or `(p-1)/2` over 3 for `(p-1)/6`, `1-p` over `-6`. Both sides go through `_safe_sympify` (200 characters, character whitelist, single letters and `sqrt`/`pi` only) and are compared with `cancel(together(a/b - c/d)) == 0`: no `simplify` search, a zero denominator or `zoo` is refused. `formula_fraction` joined `SYMPY_ANSWER_TYPES`, so the API now requires a session-bound key for it (same rule as `algebraic`); the key was already in the client payload and nothing was added to it. The subject letter stays required: a typed `x = ...` is accepted only when the left side equals the stored `answer_subject`; any other left side gets "Check the letter before the equals sign, or type only the top and bottom of the fraction."

**Parser caps (new, shared by every SymPy-backed type).** The existing checks capped length and characters only, so `9**9**9**9` and `(x+1)**99999` hung the `algebraic` checker (found while writing the item 2 DoS test; both timed out at 20 s on the previous tree). `_safe_sympify` now rejects, on the unevaluated tree and before anything is expanded: more than 160 nodes, a power whose exponent is not a plain number or fraction, any |exponent| over 12, nested exponents that multiply past 100, an effective degree over 8 summed across powers that contain a letter, more than 6 different letters, and integer literals over 12 digits. `algebraic` equality now tries `expand` then `cancel` and keeps `simplify` only for roots and pi. A bomb list (sixteen inputs per checker, including all of the above) runs in the test and each must return in under 2 s.

**3. `linear` checks the letter.** When the key names a letter (`w=12`) and the pupil names another (`y = 12`), the answer is refused with "Check the letter. This question asks you to find w." (`wrong_letter: true`). A bare number, the right letter in either case, and a key with no letter (`x` is not assumed) behave as before. All generator keys that name a letter name one the question uses (checked in the test).

**4. Surd "simplest form".** `_surd_answer(k, r, simplest=True)` and `_algebraic_fraction_surd(..., simplest=True)` set `answer_form = 'simplest_surd'`. `check_surd` and the `k√r` over `n` branch of `check_algebraic_fraction` then re-read the pupil's text without simplifying it and refuse an unsimplified or unreduced entry that is equal in value: "That's equal, but the surd can be simpler. Take a square factor out from under the root." (`√3240` and `6√90` for `18√10`) and, for the rationalised fraction, "That's equal, but it can be simpler. Check the surd, then see if the fraction cancels." (`2√6/6` for `√6/3`). Flagged variants (the question says simplify, simplest or form k√r): `gcse_surds_simplify`, `gcse_surds_simplify_multiple`, `gcse_surds_add_subtract`, `gcse_surds_multiply`, `gcse_surds_exact_area`, `gcse_surds_expand_diff_subtract`, `gcse_surds_practice_divide`, `gcse_surds_practice_mixed_simplify`, `gcse_surds_rationalise_simple`. Left alone on purpose: questions that only say "exact" or "surd form" (`gcse_surds_practice_perimeter_exact`, the Pythagoras distance and vector magnitude questions, trig exact values), because they do not ask for simplification; and the two denominator-binomial rationalise forms (`b|...`, `d|...`), whose parsers already insist on a whole-number denominator but still normalise the numerator.

**5. Graph-reading bands follow the grid.** Rule: the tolerance is half a grid square on the axis being read (`generators/shared/utils.grid_estimate_tolerance(spacing)`; spacing is the gap between neighbouring gridlines, or between labelled ticks where the graph has no gridlines, in that axis's units). It returns a whole number when the half is whole, else up to 2 d.p. Applied to the scatter-graph line-of-best-fit estimates (y from x, and x from y with 1 d.p.) in graphs and statistics, where spacing is the drawn tick step (`_gr_scatter_axis_steps`), and to the cumulative-frequency median, where the x ticks are one class width apart (bands 2.5, 5 or 10). The old rule was `max(2, round(step / 2))`: the floor of 2 made a 1-unit grid far too loose and the rounding made odd steps drift (step 5 gave 2, not 2.5). Generators pass `grid_spacing` (`_gr_number_estimate_answer(..., grid_spacing=)`, or `grid_spacing` in a graded `number_estimate` payload); with no spacing the explicit `tolerance` is the fallback, so other number-estimate questions are unchanged. The test redraws each scatter graph, reads the tick step off the SVG and checks the key's band is half of it. Solution text still says "accept estimates within ±t" with the new t.

**6. `keyword` substring leniency** unchanged, as decided.

**Tests.** `scripts/test_answer_check_smoke.py`: 15 new tests (accept, reject, wrong-form-with-message, session-bound API, copy lint, parser bomb list, generator flag presence, grid rule). `scripts/test_gcse_maths_verification_smoke.py`: the checker round-trip now passes each problem's stored `answer_form` and `answer_subject` to the checker like the app does, a new `answer_form` check (presence by recorded task, no stray flags, and every flagged slot's key accepted while a value-equal unexpanded, unfactorised, partly factorised or unsimplified entry is refused with the form message and accepted without the flag), and linear keys with a letter now try the right and a wrong letter. No static bank item changed, so no digest was re-pinned.

**Not done / open.** (a) Closed in the review below (`simplified` form). (b) The `b|` and `d|` surd rationalise forms do not check numerator radicands. (c) Surd questions that say only "exact" accept an unsimplified equal value.

**Results.** Default verification run about 22 s (670 of 670 negative-control keys caught, 75 round-trips with a required form); `--deep --seed 41000` passes (about 158 s); answer-check smoke, GCSE correctness smoke, `ruff check .` and the full suite (104 of 104) pass.

### Checker decisions review notes (independent reviewer, 2026-10-23)

Reviewed the §11 changes against David's six decisions and the code (`answer_checkers.py`, `utils.py`, `lesson_quiz.py`, `class_assignments.py`, `app.py`, the flagged generators, both smoke tests). Nothing committed.

**Confirmed.** `answer_form` and `answer_subject` reach `check_answer` only from the session-stored problem (`app.py`), the stored lesson-quiz problem and the frozen class-assignment problem; a body that sends `answer_form` or `form` is ignored (mutation-tested). No `eval`, `exec` or bare `sympify` on pupil text; every SymPy path goes through `_safe_sympify`. `formula_fraction` and `linear` are used only by GCSE maths generators (searched `generators/`, templates and `site.js`); other levels see no change except the wider surd spellings below and the shared parser caps. Linear keys with no letter, and compound keys, behave as before. Graph bands: scatter estimates pass the drawn tick step (2 to about 12, so bands of 1 to 6), the cumulative-frequency median passes the class width (bands 2.5, 5, 10); neither graph has a finer grid, so half a square is fair, and the polyline curve matches the interpolated key.

**Found and fixed.**
- High, DoS: the degree caps did not bound products. `(a+b+c+d+e+f)(a-b+c+d+e+f)...` (11 brackets, 143 characters) took 12 s per check in `algebraic`; `(a+b+c+d+e+f)^8|(a-b+c-d+e-f)^8` ran past 20 s in `formula_fraction` (each part passed the caps alone, then `cancel()` met both). `_within_sympy_caps` now also bounds the number of terms once multiplied out (`_expanded_terms_bound`, at most 400: sums add, products multiply, a power n of a t-term sum gives C(t+n-1, n)), and `formula_fraction` applies the caps to numerator over denominator together before `cancel()`.
- Medium, code run at parse time: `parse_expr`'s default namespace binds the one-letter SymPy names E, I, N, O, Q, S, so `N(pi,99999999)` ran inside `_safe_sympify` and never returned (not reachable through today's checkers, which lower-case or split on commas first, but the guard should not rely on that). The parser now gets SymPy's names without the one-letter ones (a capital letter is a plain symbol), commas are refused, and a result that is not a SymPy expression (a tuple) is refused instead of raising.
- Decision 1 gap: `_af_i_difference_of_squares` and `_af_i_quadratic_cancel` accepted the question's own fraction. New form `simplified` (`FORM_SIMPLIFIED`): when the key has no letter underneath, an equal answer that still divides by something with a letter is refused with "That's equal, but it can be simpler. Factorise the top if needed, then cancel the matching bracket." A key that is itself a fraction is never refused. The verification smoke now wants the flag on any "Simplify" algebraic slot whose question is a fraction with a letter underneath and whose key is whole (85 form round-trips, was 75), and types the question's own fraction back as the wrong-form entry.
- Surd spellings rejected as unreadable: `2√(3)`, `√3×2`, `√3*2`, `√3·2`, `sqrt(3)*2`, and in the rationalised fraction `sqrt(6)/3` and `√(6)/3`. All now read (unsimplified ones still get the form message).
- Copy: four form messages were over the Zorp line length (100) or used a four-syllable word, and the `formula_fraction` letter and parse messages used "just", "numerator"/"denominator" and a spaced hyphen. Reworded (quotes above updated); a test now runs `zorp_voice.lint` over every new message as a Zorp line.
- `answer_form` was sent to pupils in class-assignment payloads (`strip_problem_keys` strips a fixed list); added to that list. The check API response does carry `wrong_form` / `wrong_letter` (the kind, which only restates the feedback), never the stored form.

**Probes.** Expanded: term order, `x²`, `x**2`, `5*x`, `x*x`, spaces, leading `+`, `y=` prefix all accepted; brackets left in, like terms uncollected and `x(x+5)+6` get the form message; a wrong value gets "Not quite". Factorised: factor order, `(3+x)`, `-(x-3)(x+2)` = `(3-x)(x+2)` = `(x-3)(-x-2)` = `-1(x-3)(x+2)`, coefficient after the bracket, `(x+2)^2` = `(x+2)(x+2)` = `(-x-2)^2`, `3x(2x+3)` = `(2x+3)(3x)` = `-3x(-2x-3)` all accepted; `x(6x+9)`, `3(2x^2+3x)`, `(2x+6)(x-1)`, `2(x^2+2x-3)` partly factorised; `x^2-25` for the difference of two squares unfactorised. Surd: `2√3`, `2sqrt(3)`, `2×√3`, `√3·2` accepted; `√12`, `√3240`, `6√90` form message; `17√10` "Not quite". `formula_fraction`: sign flips, common factors, `x=` with the right letter, capitals accepted; wrong letter gets the letter message; zero denominators (`0`, `a-a`) refused.

**Left open (pre-existing, not part of these decisions).** (1) Letters written side by side in another order (`2ba` for `2ab`, `5(x^2-2xy)`) are not parsed by SymPy (multi-letter names are refused) and fall back to text equality, so they are marked wrong; no flagged key has two letters side by side. (2) `(1/3)√6` is not read in the rationalised fraction (the stacked boxes ask for top and bottom). (3) The default run now reports 669 negative-control keys (§11 said 670); the count is the same with the `simplified` flags taken out of the generators, and the deep run at offset 5000 reports 670 of 670, so it is a count of tamperable slots, not a lost check.

**Bombs** (each through `algebraic` with and without forms, `formula_fraction`, `quadratic_roots`, `algebraic_fraction`, `surd`, `linear`): 54 inputs including nested powers, `(x+1)^99999`, 12-digit integers to the 12th, `1e999999`, hex and binary literals, 40 to 90 nested brackets, products of 29 brackets, 6 and 8 letters, nested radicals, `N(pi,99999999)`, `S(9)**S(9)`, tuples, full-width digits and letters, zero-width space, mathematical italic x, Arabic-Indic digits, `½x`. Slowest after the fixes 0.09 s (was 12 s and more than 20 s for the two product bombs).

**Results.** Answer-check smoke, default verification (about 23 s, 85 form round-trips, 669 of 669 tampered keys caught), `--deep --seed 5000` (155 s, 343 form round-trips, 670 of 670), GCSE correctness smoke, `ruff check .` and the full suite (104 of 104) pass.

**Mutation tests** (each alone, file restored and checked by SHA-256): partly-factorised check removed, like-terms count removed, simplest-surd check removed, term cap removed, default SymPy namespace restored, linear letter check removed, `simplified` refusal removed, form read from the request body, `formula_fraction` equivalence removed, the `simplified` flags removed from both generators, the `expanded` flag removed from `algebra_practice_expand_binomial`, a scatter band set from twice the grid: all 12 failed a test.


## 12. Phase 3 build notes (2026-10-23)

**Built.** Eight topics are now verified: statistics, probability, geometry_angles, transformations, similarity_congruence, circle_theorems, constructions_loci, vectors. `PENDING_TOPICS` is empty and `PENDING_CEILING` is deleted; the test now fails if any slot is pending. New solver modules, all independent of generator code (the AST independence check passes; no `eval`, `exec`, `sympify` or `parse_expr`; probability uses exact `Fraction`): `solvers_shapes.py`, `solvers_svg.py`, `solvers_transform.py`, `solvers_loci.py`, `solvers_vectors.py` (the last has a small hand-written linear-combination parser, `parse_lin`). Every remaining variant has a one-line `record(...)` or `@verifies`; `record()` adds no RNG draw and leaves generator output unchanged. Diagrams are checked by reading the emitted SVG (`@diagram` checks for vectors, loci, probability trees, pie charts and the similarity and circle figures).

**Coverage (1,678 slots; all 32 topics).**

| Category | Phase 3 topics | All topics |
|---|---|---|
| Practice slots re-solved | 352 of 359 | 1,065 of 1,072 (99.3%) |
| Practice exemptions (infeasible, reason recorded) | 7 | 7 |
| MCQ slots re-solved directly | 42 (statistics, probability) | 189 |
| MCQ dispatch slots | 126 | 417, covered by 49 procedural functions and 334 pinned static bank items |
| Pending | 0 | 0 |
| Negative control, tampered keys | | 968 of 968 rejected |
| Negative control, damaged drawings | | 20 of 20 families caught |

Per topic (practice / MCQ slots): statistics 47/21, probability 47/21, geometry_angles 44/21, transformations 42/21, similarity_congruence 45/21 (3 exempt), circle_theorems 45/21 (3 exempt), constructions_loci 48/21 (1 exempt), vectors 41/21.

**Honest note on the MCQ target.** The 80% target for MCQ is met only if the dispatch slots count: 189 of 606 MCQ slots are re-solved by an independent solver; the other 417 are served by procedural functions that call `record()` (verified) or by hand-reviewed bank items pinned per item by sha1 (reviewed once, not re-solved; editing one fails the test until re-reviewed and re-pinned with `--print-digests`). In the five geometry topics only the procedural share is solver-verified.

**Exemptions (7, all infeasible).** Worded proofs answered by ordering sentences, so there is no numeric or symbolic form to recompute; the keyed order and wrong steps were read by hand: `_sc_i9_proof_aa_parallel`, `_sc_d1_midpoint_theorem_proof`, `_sc_d7_congruence_proof`, `_ct_d2_prove_angle`, `_ct_d4_alternate_segment_proof`, `_ct_d10_prove_cyclic` and `_cl_d1_locus_proof`. The full list with reasons is `register.EXEMPT` (each reason is 20 or more characters). Nothing is skipped silently.

**Wrong, ambiguous or unanswerable questions fixed.**
- Vectors: `inter_magnitude_advanced` could give x²+y² a perfect square and then say "not a perfect square" (re-rolled); `_vec_magnitude_answer` gave an unstated 3 d.p. value for non-squares (now an exact surd); `inter_magnitude_distance` could use coincident points and did not say how to give the answer (re-rolled; wording "as a whole number or as a surd"); `inter_ratio_point` gave a recurring-decimal point (AB now a multiple of ratio+1); `diff_ratio_theorem` likewise; `inter_magnitude_comparison` could tie; `diff_collinear_proof` used `//` and printed a wrong multiple (k is now a Fraction); `diff_parallelogram_area` could use parallel vectors (area 0); `diff_parallel_unit` did not say "unit vector" or the accuracy; `_vectors_direction_words` said "0 units left".
- Vector diagrams: path-addition arrows left the frame (adaptive scale); the parallelogram grid clipped vertices above y = 10 (grid extended).
- Constructions and loci: `f14` two-circle region, `d3` chord midpoint, `d6` difference of squares, `d8` circumcentre sign, `d11` sector area, `d12` two radio towers (infinite re-roll loop and sides matched in listed order), `d15`/`d16` garden diagrams (`_garden_loci_svg(length, width)`), `i1` combined loci, `i13` garden sprinkler, `d5` Apollonius rounding.
- Transformations: the enlargement check line used a fixed (-2) instead of the scale factor in use; a zero constant printed as "3n0" in a sequence-style label; two points could coincide so there was no triangle; MCQ distractors that duplicated the key or the origin were replaced; a wrong translation distractor (-8, 0) became (-4, 0).
- Similarity: `_sc_d2_frustum_volume` divided floats by pi (wrong coefficients, now exact); `_sc_d8_both_sa_and_vol_similar` used cone numbers that were not a real cone (now 3-4-5 and 6-8-10 cones); `_sc_i12_map_area` held 500 000 cm2 where 8 x 25 000 squared was meant (now computed); MCQ "linear scale factor" for areas 36 and 81 asked an ambiguous direction (now "smaller : larger") and others had distractors equal to the key or to each other.
- Circle theorems: chord length answers had an unstated 2 d.p. and double rounding (`_ct_i5`, `_ct_d14`, now "to 2 decimal places" and rounded once); `_ct_i6` could give a non-whole base angle; `_ct_d13`, the same-segment question, named angles that did not match the diagram (rewritten to angle CAD, ACB, CBD, ADB); `_ct_i14` asked for an angle "beyond this question scope" (rewritten as angle BAC and ABC from the tangent-chord angle, with a check line); a wrong-step distractor in a proof-ordering item was in fact a true statement (now genuinely wrong), and two part-(ii) wordings were made unambiguous.
- Geometry angles (found by the 4-seed `--deep` run): `_geom_inter_kite_angles` could make angle C 180 degrees or more (not a kite); the loop now keeps C below 180.
- Statistics: `_stats_found_15` and the other scatter "no correlation" clouds were accepted at |r| below 0.3, which after the drawn-pixel rounding could land on 0.30 and be arguable; the threshold is now 0.2. The cumulative-frequency interpolation (`_stats_cf_interp`) now computes exactly (float noise made 11.25 round to 11.2 instead of 11.3).
- Statistics: the pie-chart question printed a literal backslash-n before the chart (now a real line break).
- Probability: "Find the relative frequency" now says "correct to 3 decimal places" (the key was rounded without saying so).
- Left alone, reported: a dead duplicate `vectors_mcq()` earlier in `maths.py` (overridden by the live `_VECTORS_MCQ_BANK`; its options repeat "(4,1)"); the parallelogram-three-points diagram draws D at its true position, which gives the answer away; duplicate variants (`found_magnitude_3_4` and `6_8` are identical, `proof_sim` calls `geometry_proof`).

**Typed-form generosity (decision 2) and checker changes** (`generators/shared/answer_checkers.py`, tests in `scripts/test_answer_check_smoke.py`; all DoS guards kept):
- Probability answers: new form `FORM_PROBABILITY` accepts a fraction, a decimal or a percentage; a recurring decimal that was asked as a decimal gets a kind "write it as a fraction" message instead of a flat wrong. `check_fraction` and `check_number` now take `form=` (both in `FORM_AWARE_ANSWER_TYPES`); generators pass the form through `graded_answer_number(val, form=None)` and the probability builders.
- Leading-dot decimals (`.25`) and percentages (`25%`) parse.
- Transformation names: keyword aliases for the four transformation names (describe in equivalent words).
- Vector pairs: `3 -4` and `(3 -4)` (space separated) are accepted for column vectors.
- `check_keyword` stays a substring match (David's decision); one-letter keys now need the letter as a whole answer (so "y" cannot pass inside "yes please" for a key "A").
- Pupil-facing false rejections still open (flagged, not fixed): a Unicode `½` is not accepted for fractions or algebra; `x=3, y=-4` is rejected for column vectors; `1/2 AB` is rejected for combination vectors (accepted by `algebraic`); a lone `y` or `n` is rejected for yes/no keys; geometry-type diagrams are schematic and not labelled "not drawn to scale".
- Transformation "describe fully" slots have `answer_type` None and are self-marked (the solver checks the key against the recorded vertices).

**Runtime.** Default run 32 to 35 s on this machine (was 24 s after Phase 2; the new diagram negative control and eight topics add the rest). The 30 s target is missed by about 2 s: the choice is to keep every seed or cut seeds for the new topics; I kept the seeds. `--deep` passes at seed offsets 0, 1000, 41000 and 77777 (about 470 s each when the four run in parallel; about 170 s alone). The first deep pass found the kite, scatter-correlation and cumulative-frequency tie bugs above and one over-eager probability-form test (point names such as P(2, 3) were read as a probability question); all fixed and re-run clean.

**Drift.** `git archive HEAD` into the scratchpad, 1,678 slots x 3 runs dumped for HEAD and the working tree, and the working tree also compared with the end-of-Phase-2 dump. Differences against the Phase 2 tree are limited to: `answer_form` keys added by the earlier checker-decision work (algebra, surds, algebraic_fractions, algebraic_proof, probability), the Phase 2 graph-reading tolerance and algebraic-circle fixes (graphs, statistics, geometry_angles), and the Phase 3 fixes above in the eight topics (probability: relative-frequency wording and form keys; statistics: the pie line break). number, ratio_proportion, bidmas, multiples_factors, decimals, fdp, pythagoras, compound_measures, mensuration, trigonometry and bearings are byte-identical to the Phase 2 tree. Re-run after the last fix: no further differences in runs 0 to 2.

### Phase 3 review notes (independent reviewer, 2026-10-23)

Reviewed §12 against the plan and the code (the five new solver modules, `engine.py`, `harness.py`, `register.py`, the test, every Phase 3 generator diff, `answer_checkers.py`, `app.py`, `lesson_quiz.py`, `class_assignments.py`). Nothing committed. Part of this review ran in an earlier session that stopped before writing these notes; its changes were already in the working tree and were reviewed again here as if new. Some §12 items are therefore out of date: the dead duplicate `vectors_mcq()` (the copy with the repeated "(4,1)" option) is gone, the parallelogram diagram no longer shows D, the "Not drawn accurately" captions and the listed pupil-facing spellings are done (all below).

**Confirmed.** No solver imports generator code or calls `eval`, `exec`, `sympify` or `parse_expr` (AST check; probability is exact `Fraction` throughout). Every diagram check compares the drawing with the recorded question inputs or with a value the solver computes itself, never with the key: tree branches and fill-in box answers against probabilities computed from the counts, Venn regions, bar heights, pie sectors, box-plot labels and positions, histogram bars (the mean is then computed from the bars as drawn), the cumulative-frequency curve, the section point P, the parallelogram's A, B and C, the path-addition arrows and the centre angle in the CT1 diagram. "Describe fully" transformation options are judged by what they do to the vertices, not by their wording. The 7 exemptions are ordered-sentence proofs with no record call (checked: 0 records), so they cannot verify by accident; each keyed order and every wrong step was read again and is right (one note below). Drift: against the end-of-Phase-2 tree (HEAD plus the reviewed checker-decision files), 3 seeds x 1,678 slots, only the eight Phase 3 topics differ (437 generations in 168 slots) and each difference was read and traced to a §12 fix, a "Not drawn accurately" caption or the review fixes below; the other 24 topics are byte-identical. Against HEAD the earlier phases' differences are as their notes say.

**Mutation tests** (each applied alone in a copy of the tree, the test run, the file restored and checked by SHA-256): wrong bag probability; without-replacement key computed with replacement; mean over n - 1; median off by one place; IQR as Q3 - Q2; co-interior angle equal instead of supplementary; angle at the circumference equal to the angle at the centre; enlargement centre x + 1; enlargement drawn with scale factor k + 1; wrong vector sum component; locus circle radius r + 1; section point P drawn at the wrong fraction (key unchanged); without-replacement tree drawn with the with-replacement branch (key unchanged); box-plot median drawn and labelled wrong; `record()` removed from a vector variant; geometry bank item key edited; a verifying slot added to `EXEMPT` (stale exemption); an exemption key misspelt (slot unclassified); the probability form dropped from the fraction builder; the scatter "no correlation" threshold relaxed to 0.9; the similar-area key scaled by k instead of k squared; two construction steps swapped; D drawn back on the parallelogram grid. All 23 made the test fail.

**Static bank items.** All 94 pinned items in the six Phase 3 banks (geometry_angles 15, circle_theorems 24, similarity_congruence 15, transformations 15, constructions_loci 15, vectors 10; statistics and probability have no static bank) were solved by hand: every key is right, no item has two correct options, and no distractor equals the key or another option in value. The earlier review pass had already fixed and re-pinned two similarity items (an option "20/3 cm" equal to the key "6⅔ cm", replaced by 2.4 cm; area and radius ratios that did not say which way round) and the circle-theorem items whose diagrams gained the caption. No digest changed in this session.

**Hand checks** (about 80 generated questions across the eight topics, plus every listed fix): grouped and listed means, medians, modes, ranges, frequency density, pie angles, cumulative-frequency parts, line-of-best-fit estimates; conditional, union, complement, at-least-one, coin, Venn (three-set clues completed region by region) and tree probabilities; kite, polygon-algebra, bearing, tangent and cyclic angles; all circle-theorem keys including chord length 2 x 12 sin 60° = 20.78; similar areas, map areas (8 x 25 000² cm² = 0.5 km²), the scale model (4 000 m³, 12 m²), the 3-4-5 cones (96π, 96π); rotations, oblique reflections and the three-transformation chain; difference of squares, circumcentre (25/16 = 1.56), incircle and loci counts; vector sums, parallels, unit vectors and magnitudes. All correct.

**Found and fixed in this review.**
- High, DoS (older code, newly reachable through more pupil spellings): the column-vector bracket pattern backtracked on long runs of spaces, so a 2,000-character answer (the app's limit) took 36 s in `vector`; the π-suffix pattern in `pi_multiple` took 46 s on the same kind of input. `_parse_vector_pair` now refuses text over 200 characters before any pattern runs, and `pi_multiple` does not strip a suffix from text over 200 characters. A scan of every checker with 64 long inputs now has a slowest call of 0.11 s. New test `test_vector_and_pi_inputs_are_capped_and_fast`.
- Medium: the single-character fraction expansion (½ to 1/2) ran on every answer type, so code (`python_run`, `sql`), free text, keywords and choices were rewritten before checking (`print("½")` became `print("(1/2)")`). It now runs only on maths types; `_VERBATIM_ANSWER_TYPES` lists the others, with a regression test.
- Earlier review pass, re-checked here: the parallelogram diagram drew D (now three points and two sides only; the diagram check fails on a fourth point, a D label or a closed shape); "Not drawn accurately" on fixed-layout angle, circle-theorem and similarity sketches (diagrams drawn to the stated angle, such as CT1 and the alternate segment layout, keep `accurate=True` and no caption); the Venn activities "chess" and "coding club" shared the letter C (now chess, debating, orchestra); the independent-events questions now name A and B; the loci question that could name a point A or B (the segment's own ends); "1x" in a cyclic-quadrilateral expression; the scale-drawing part that did not ask for cm; checker spellings ½ and other single-character fractions, `x = 3, y = -4` for a column vector, a lone y or n for a yes/no key, and `1/2AB` for a vector combination read only against the stored box label (labels come from the session problem, never the request).
- Low, this session: `_geom_diff_algebraic_circle` printed "x = 15" twice when the coefficient was 1; the similar-area question lacked a full stop before its line break; the garden PQRS and triangle-centres sketches (fixed shapes with side labels) now carry "Not drawn accurately". Found by this review's deep runs (the cosmetic check now covers the Phase 3 topics): `_trans_diff_algebraic_coords` printed "1n + 3" and "1q" (seed offset 2000), and `algebra_practice_brackets_both_sides` printed "3(x + 2) + 0" (offset 63000, a Phase 2 slot); both fixed and swept clean over 4,000 seeds.

**One-letter keyword change.** A sweep of every level and subject in `topic_registry` (95 topics, 4 seeds per slot) finds one-letter keyword keys only in `_vectors_inter_magnitude_comparison` (a or b); yes and no keys only in GCSE maths. Nothing else is affected.

**Checker probes.** Probability form: fraction, decimal, `.375` and `37.5%` accepted with the form and a percentage refused without it; `0.333` for 1/3 gets the kind "write it as a fraction" message. Vectors: `(3 -4)`, `3 -4`, `x=3, y=-4` (either order, `;` or "and") accepted; swapped, repeated or extra components refused. Keywords: "vector a", "a is longer than b" accepted for a; "b is larger", "ab", "banana" refused; y and n only for yes and no keys. Bombs (all through `check_answer`): 400 and 5,000 copies of ½, ½ after 300 digits, nested brackets, `1e999999%`, `.` runs, 2,000-character space runs in every checker, named-component and vector-label bombs: slowest 0.11 s after the fixes above.

**Runtime.** Default run 28 to 31 s alone on this machine (the earlier pass reused the queue-building probe per slot function in `harness.py`, which only the test patches, and reused the cached practice problems in the properties check; pupil code is unchanged). Budget note added to §4. `--deep` at seed offsets 2000 and 63000: see Results.

**Left for David (not changed).**
1. (Decided 2026-10-23, built: see "Decisions (2026-10-23, proofs and loci)".) Ordered proof keys mark a pupil wrong for swapping two independent facts (the corresponding-angle and common-angle steps of `_sc_i9_proof_aa_parallel`; the three equal-side steps of `_sc_d7_congruence_proof`). The checker would need groups of steps that may come in any order; recommended.
2. (Decided 2026-10-23: keep as a trap, see Decisions.) Two wrong steps contain a true statement with a wrong reason (`_ct_d4` "angle AOB = 2 x angle TAB = 80° because the tangent doubles the angle"; `_ct_d10` quotes CT4 itself instead of its converse). They are wrong as proof steps, so the keys stand; rewording would make them clearer.
3. (Decided 2026-10-23, built: see Decisions.) `_cl_d12_two_radio_towers` always has the answer "Yes, they overlap" (the loop keeps only overlapping ranges). Correct, but a no-overlap case would make the item worth more.
4. The remaining `vectors_mcq()` in `maths.py` is unreferenced (the live MCQs come from `_VECTORS_MCQ_BANK`); it is no longer a duplicate, so it was left. The identical magnitude variants (`found_magnitude_3_4` and `6_8`) are left for the variant-dedupe work.
5. The presence guard now ignores the value 1 as well as 0 (both are often unwritten, as in x for 1x); a recorded 1 is therefore not tied to the question text.

**Results.** Default verification 28.9 s alone (968 of 968 tampered keys and 20 of 20 damaged-drawing families caught); `--deep --seed 2000` and `--deep --seed 63000` pass after the fixes above (971 of 971 and 969 of 969; about 390 s each when run together); GCSE correctness smoke, answer-check smoke, `ruff check .` and the full suite (104 of 104) pass. No static, JS or template file changed, so there is no `?v=` or `CACHE_VERSION` bump.

## 13. Decisions (2026-10-23, proofs and loci)

David decided three of the items left in the Phase 3 review notes. Built and tested; nothing committed. No static, JS or template file changed (the pupil page already sends the answer as an ordered list of step ids and shows the checker's feedback), so there is no `?v=` or `CACHE_VERSION` bump.

**1. Proof ordering accepts any valid order.** Where two steps are logically independent, a pupil who swaps them is marked correct; swapping dependent steps is still wrong.

*Representation.* A generator passes `after=` to `proof_steps_answer()` (`generators/shared/utils.py`): a map from a 1-based position in the canonical order to the positions that step needs first. A position not listed needs the position just before it (so a proof with no `after` is a strict chain and is unchanged), and a step may only need earlier positions, which keeps the canonical order valid. `proof_steps_prereqs()` turns that into `{step id: [ids needed first]}`, and `proof_steps_problem_extra()` stores it as `problem['answer_step_prereqs']`, only for proofs that give `after`. It is the same kind of server-side grading data as `answer_form`. The key shown to pupils (`correct_answer_raw`, `1|s1|s2|...`) is still one canonical order, and `normalized_correct` still reports it.

*Checking.* `check_proof_steps(raw, typed, prereqs=)` accepts the canonical order, or any order that uses every step exactly once and puts each step after its prerequisites (one pass over the answer with a position map, no enumeration of orders, so the cost is linear in the answer and nothing is stored per order). A spec that is malformed (wrong keys, a self or unknown reference, not a list) is ignored, which leaves the strict canonical order. Other proof modes (`0|...` set, `pick|...`) ignore it. For a wrong order the per-step hints follow the prerequisites ("This step needs an earlier step to come before it") instead of canonical positions, which would mislead when several orders are right; a repeated step is marked as repeated; the hints keep the amber, green and red statuses the page already shows.

*Where it comes from.* `check_answer(..., prereqs=)` takes the spec from `problem_answer_prereqs(problem)`, read from the stored problem in all three graders: `app.py` `/api/v1/problems/check` (session-bound, and not for the per-field partial path), `generators/shared/lesson_quiz.grade_lesson_quiz_problem` and `models/class_assignments.grade_frozen_answer`. A request body can not supply it (keys named `answer_step_prereqs`, `prereqs` or `step_prereqs` are ignored; tested), a problem stored without it is checked against the canonical order only, and the client payload (`_problem_client_payload`) does not include it, so what is sent to the page is exactly what it was. `_freeze_problem_payload` keeps the spec in frozen set-work problems and `strip_problem_keys` removes it on the way out. (The review in section 14 found that set work also lost `answer_form` the same way, and fixed both together.) DoS guards are unchanged (the app's `MAX_USER_ANSWER_LEN` cap, the length test before any work, and no per-order work); tested with 2,000-character answers (bars, spaces, repeated ids, hundreds of unknown ids) against 4-step and 399-step specs in well under a second.

*Slots that gained alternatives (16 of the 36 ordered-proof slots).* Each listed pair is a pair of canonical step positions that were read and judged independent; `register.ORDER_FREE_PAIRS` pins them.

| Slot | Independent steps |
|---|---|
| `_sc_i9_proof_aa_parallel` | "angle A is common" (3) with the parallel-line steps (1, 2) |
| `_sc_d1_midpoint_theorem_proof` | "angle A is common" (3) with the midpoint steps (1, 2); the two results after SAS, DE parallel to BC (5) and DE = half BC (6) |
| `_sc_d7_congruence_proof` | the three equal-side facts (1, 2, 3), both the isosceles and the parallelogram versions |
| `_ct_d2_prove_angle` | the two isosceles triangles OAC and OBC (2, 3) |
| `_ct_d10_prove_cyclic` | "opposite angles", "the sum is 180" and the converse theorem (1, 2, 3) |
| `_ap_f_even_form` | the definition of even (1) with the rewriting and its bracket remark (2, 3) |
| `_ap_f_odd_form` | "2n is even" (1) with "even plus odd is odd" (2) |
| `_ap_i_product_consecutive`, `_ap_d_n_squared_plus_n` | the two cases, v even and v + gap even (3, 4) |
| `_cl_i2_equilateral_triangle` | draw AB (1) with set the compasses to the side length (2) |
| `_cl_i11_circumcircle` | the two perpendicular bisectors (1, 2) |
| `_cl_i12_incircle` | the two angle bisectors (1, 2) |
| `_cl_d1_locus_proof` | the two directions of the proof (2 to 4 with 5 to 7), and the second direction with "let M be the midpoint" (1 with 5, 6); step 7 also needs 1. The wording "Conversely, if PA = PB, ..." became "Suppose PA = PB, ..." so the second direction stands on its own and reads naturally in either place |
| `_seq_diff_show_divisible` | "one of n, n + 1 is even" (1) with "even times anything is even" (2) |
| `_seq_diff_arithmetic_proof` | "the odd numbers form an AP" (1) with "use the AP sum formula" (2) |
| `_vectors_diff_vector_inequality` | the tip-to-tail triangle (1) with the triangle inequality for sides (2) |

*Strict chains kept (20 slots).* A step that restates or uses the one before stays after it: the algebraic proofs that expand and then simplify, the recurring-decimal proofs, `_ct_d4_alternate_segment_proof`, the two "put these values in order" questions (no proof), and `_cl` constructions whose steps say "without changing the radius", "the previous arc", "the first arcs" or "the previous one" (`_cl_f9`, `_cl_f10`, `_cl_i6`, `_cl_i7`, `_cl_i8`, `_cl_i9`, `_cl_d2`, `_cl_d9`, `_cl_d13`, `_cl_d14`). The two arcs of a construction are independent in principle, but those steps are worded as depending on each other, and rewording them would change the keyed text the loci solver checks, so they are treated as dependent. Say if you want them freed too.

*The test* (`ordering` check in `test_gcse_maths_verification_smoke.py`, helper `scripts/gcse_verify/ordering.py`, which shares no code with the checker): for every ordered-proof question generated (all 36 slots), it lists the valid orders itself (every topological order of the spec), then checks that the canonical key is among them, that each listed order really puts every step after its prerequisites and is accepted by `check_answer`, that every other permutation is refused (all of them for up to 7 steps; each distinct spec once), that swapping two dependent adjacent steps is refused, that a missing, repeated, extra or foreign step is refused, that a request without the stored spec gets the canonical order only, and that the independent pairs equal the reviewed ones in `register.ORDER_FREE_PAIRS` (a slot not listed there must be a strict chain, so a new or wider alternative fails until someone reads it). Unit tests in `test_answer_check_smoke.py` cover the checker (all 24 orders of a 4-step proof, malformed specs, bombs and long inputs, the new hint copy against the pupil-copy and Zorp voice rules), the generators (`_sc_i9`, `_sc_d7`, `_sc_d1`, the client payload), and the session API plus quiz and set-work graders.

**2. `_ct_d4` and `_ct_d10` keep their trap steps.** The wrong steps with a correct number but a wrong reason ("angle AOB = 2 x angle TAB = 80 degrees because the tangent doubles the angle" in `_ct_d4`; quoting CT4 itself instead of its converse in `_ct_d10`) are fine as they are. Nothing changed. They stay wrong as proof steps, which is the point of a distractor that reads plausibly.

**3. `_cl_d12_two_radio_towers` has both answers.** The generator picks the outcome first (a fair coin), then a case with that outcome. Distances 8, 10 or 12 km, ranges 2 to 7 km each, and the two ranges always add up to at least 2 km more than the distance (overlap, 22 cases) or at least 2 km less (no overlap, 47 cases), so there is never a tangent or borderline case, and one circle can never lie inside the other (the ranges differ by at most 5 km, the distance is at least 8). Over 4,000 production draws the answer was yes 2,023 times and no 1,977 times (50.6 percent yes). The options, the worked solution and the hint match the outcome: for no, the key is "No, the circles do not overlap because the sum of the radii is less than the distance between the towers" with a gap of d minus r1 minus r2 km in the solution, and the distractors are the lens answer, the straight-line answer and "touch at exactly one point"; for yes the options are as before. The hint no longer gives the result away. The question has no diagram (it is a text question), so there is none to keep consistent. The new copy has no em dashes (the options now read "Yes, ..." and "No, ...").

*Verifier.* `loci_overlap` in `solvers_loci.py` works the outcome out from the three recorded numbers (the radii add to more than the distance) and refuses a borderline case (the sum within 2 km of the distance, or one circle inside the other); the key must be the "yes, lens, sum of the radii exceeds" option or the "no, do not overlap, sum of the radii is less than" option, and no other option may read that way. A new check, `overlap_outcomes`, generates the slot for 100 seeds (400 with `--deep`) and fails unless the outcome (again computed from the record) is yes for 30 to 70 percent, every case has the margin, the keyed option agrees with the numbers and the worked solution says "DO overlap" or "do NOT overlap" to match. `--deep` also sees both outcomes through its 200 practice seeds per slot.

**Results.** Default verification 28.8 s alone (968 of 968 tampered keys and 20 of 20 damaged-drawing families caught; 642 ordered-proof questions in 36 slots, 284 with alternative orders in 16 slots; `overlap_outcomes` 50 of 100 yes); `--deep --seed 3000` passes (214,400 practice questions, 7,200 ordered-proof questions, 3,200 with alternatives, towers 201 of 400 yes; 263 s); GCSE correctness smoke, answer-check smoke, `ruff check .` and the full suite (104 of 104) pass.

## 14. Proofs and loci review notes (2026-10-23)

An independent review of section 13 against David's three decisions and the code. Nothing committed.

**Alternative orders, slot by slot.** Every one of the 36 ordered slots was read step by step (a swap must still read as a valid proof). All 16 specs in section 13 are right: each freed pair is genuinely independent, and each pair kept in order has a later step that uses or restates the earlier one. Verdicts in brief: `_sc_i9`, `_sc_d7`, `_sc_d1`, `_ct_d2` (the two isosceles triangles both need the radii of step 1, and step 5 needs step 4's α + β), `_ct_d10`, `_ap_f_even_form` ("the bracket (4k)" needs step 2, so only the definition is free), `_ap_f_odd_form`, the two case-split proofs, `_cl_i2` (the arc from A needs both AB and the compass setting), `_cl_i11`, `_cl_i12`, `_cl_d1`, `_seq_diff_show_divisible`, `_seq_diff_arithmetic_proof` (naming the method before checking it applies still reads as a proof) and the vector inequality: correct. Of the 20 strict chains, the one borderline case is `_ap_d_even_sum_squares` step 3 ("16 has factor 2 because 4 is even"), a standalone fact that could in principle come first; it names the 16 that step 2 produces, so it stays after it, in line with the bracket steps of the other factorising proofs. No further pairs were freed, so `register.ORDER_FREE_PAIRS` and the section 13 table are unchanged. The two "put these values in order" questions use distinct values (`_fdp_random_order_items` refuses repeats), so a single order is right.

**`_cl_d1` wording.** "Now suppose PA = PB, ..." became "Suppose PA = PB, ...": with the two directions free, this step can open the proof, where "Now" read oddly. The mathematics is right (RHS on the right angles at P′ with the equal hypotenuses PA = PB and the common side PP′ gives AP′ = BP′, so P′ is the midpoint M and P lies on the perpendicular through M).

**Checker hardening.** `_clean_proof_prereqs` now also ignores a spec whose canonical key breaks it (which covers every cycle), a key with a repeated step id, and entries that are not step ids (an unhashable entry used to raise `TypeError` instead of being ignored). Before this, a spec such as "step 1 needs step 3" was accepted as given and let a non-canonical order through. Specs only ever come from the stored problem, so this is defence in depth; unit tests cover each case.

**Set work kept too little checker data (fixed).** `_freeze_problem_payload` builds the frozen problem from the client payload, so set work lost `answer_form`: an expand, factorise, simplify, simplest-surd or probability question set as class work accepted an answer in the wrong form that practice refuses. Every field the three graders read was compared with the client payload; `answer_form` and `answer_step_prereqs` are the only checker fields the payload leaves out (`answer_subject`, `answer_labels` and `answer_field_types` are already in it). `models/class_assignments.SERVER_ONLY_KEYS` now names those two; `_freeze_problem_payload` copies them from the generated problem, and `strip_problem_keys` removes them on every way out, including once a question is answered (before, an answered question's full stored copy, spec included, was sent back to the pupil). Teacher views, previews and the CSV and data exports carry no problem checker data. Test: `test_set_work_keeps_server_side_checker_fields` (frozen copy keeps both fields, the unexpanded product is refused and a valid proof swap accepted, and neither field appears in the pupil, teacher or preview payloads, answered or not). Set work frozen before this fix has no `answer_form` and is still graded on value alone, as it was.

**Radio towers.** All 69 cases checked by hand: overlap needs r1 + r2 at least d + 2 (15 cases at 8 km, 6 at 10 km, 1 at 12 km), no overlap needs r1 + r2 at most d - 2 (6, 15 and 26). The largest range is 7 km and the smallest distance 8 km, so neither tower is inside the other's zone and one zone can never contain the other (that would need d to be at most the difference of the ranges, at most 5 km); "lens" is always the right word for the overlap. Both keyed statements, the distractors (none true for its outcome; "each tower covers less than half the distance" is offered only when the answer is yes, where it is false), the hint and both worked solutions read correctly. The 30 to 70 percent check runs on fixed seeds, so it is deterministic for a given `--seed`; for a fair coin over 100 questions the chance of falling outside the band is about 3 in 100,000 per new seed, and 45 to 53 yes were seen over six seed offsets.

**Zorp voice.** `test_zorp_voice_smoke.py` passed with a notice that Appendix A line numbers had shifted (app.py moved); `--write`, the documented procedure, refreshed them. The regenerated rows differ from the old ones only in numbers; the copy is unchanged.

**Mutation tests** (each applied, run, then restored and confirmed by SHA-256): freeing a dependent pair in `_sc_i9` (ordering check and unit test fail); making `_cl_i11` strict again (ordering check fails); dropping `answer_step_prereqs` from the server-only keys, skipping it in `strip_problem_keys`, or returning the full stored copy on reveal (set-work and session tests fail); reading the spec from the request in `/api/v1/problems/check` (session test fails); dropping `answer_form` from the frozen copy (set-work test fails); removing the canonical-order guard (checker test fails); forcing the towers to always overlap (`overlap_outcomes` fails, 100 of 100 yes). All caught.

**Left as they are.** The practice session is a signed cookie, so the stored problem (key, form and spec alike) can be decoded by the pupil's browser; this is how practice has always worked and is not new to the spec. Saved problems store the full generated problem and the account data export includes it, by design. The `_cl_d1` worked solution still has an em dash before "the perpendicular bisector of AB" in its last line; it is older copy, outside this change.

## 15. Phase 4 build notes (2026-10-23)

Deep mode, the lesson-quiz sweep and the exemption burn-down. Nothing committed; no static, JS or template file changed, so no `?v=` or `CACHE_VERSION` bump. Two bank items in `maths_basic_topics_mcq.py` and two answer-checker behaviours changed (below).

### Coverage, before and after

| Measure | Before (end of Phase 3) | After |
|---|---|---|
| Practice slots fully re-solved | 1,065 of 1,072 (99.3%) | 1,072 of 1,072 (100%) |
| Practice exemptions | 7 (worded proofs) | 0 |
| MCQ slots whose whole pool is re-solved ("strict") | 189 of 606 (31.2%) | 551 of 606 (90.9%) |
| MCQ, mean share of each slot's pool that is re-solved | 38.7% | 96.7% |
| Static bank items re-solved (not just hash-pinned) | 0 of 334 | 319 of 334 (95.5%) |
| Static bank items exempt, with a reason | 334 pinned | 15 |

"Fully verified" for MCQ is reported two ways because dispatch slots draw at random from a pool of bank items plus procedural questions. The strict figure (a slot counts only when every question it can serve is re-solved) meets the 90% target; the pool-share figure is the share of generated questions that are re-solved. Both are printed on every run (`scripts/gcse_verify/coverage.py`).

By topic, MCQ strict slots / pool share / static items re-solved (every topic not listed is 21 of 21, 100%, with all its static items re-solved; the 12 direct-generator topics have no static bank):

| Topic | Strict | Pool share | Static items re-solved |
|---|---|---|---|
| trigonometry | 0 of 21 | 57.1% | 8 of 15 |
| constructions_loci | 7 of 21 | 70.5% | 10 of 15 |
| simultaneous_equations | 12 of 18 | 93.3% | 9 of 10 |
| pythagoras | 14 of 21 | 88.9% | 9 of 10 |
| bidmas | 14 of 21 | 95.2% | 14 of 15 |

Trigonometry is the weak spot: 7 of its 15 bank items are definitions, mnemonics or choices of rule, which have no number to recompute, and every one of its dispatch slots can serve one of them, so no trigonometry slot is strict. Earlier "before" figures count the Phase 3 position with the static items only pinned.

### How the bank items are re-solved

`scripts/gcse_verify/solvers_bank.py` (toolkit and the `bank` family) with the specs in `solvers_bank_number.py`, `solvers_bank_algebra.py` and `solvers_bank_geometry.py`. A spec is keyed by the item's digest (`mcq.item_digest`: plain question, sorted option texts, keyed text). It reads the numbers or the mathematics from the displayed question only (never the solution, hint or key), works out the answer itself, and returns an expected value or a test on the option text. The generic MCQ check in `engine.verify_problem` then needs exactly one option to be the recomputed answer, and for it to be the keyed one, and no two options to be equivalent. Editing a bank item changes its digest, so it fails until the spec is looked at. Negative control: each of the 319 re-solved items is tried with every wrong letter as the key (957 of 957 caught). All solver modules pass the independence check (stdlib, sympy and sibling solvers only; an exact `Fraction` BIDMAS evaluator in `solvers_bank.calc`).

### The seven proofs

All seven worded-proof practice slots are out of exemption (`register.EXEMPT` is empty). `scripts/gcse_verify/solvers_proofs.py` holds a model of each proof (`record('proof_model', proof=...)`, one line per generator, no change to output; `_sc_d7_congruence_proof` records which of its two proofs it drew). The model checks that each keyed step says what step k of that proof must say (patterns, with the numbers taken from the question: 80 and 40 degrees, the angle in the alternate segment, 70 and 110), that no distractor reads as a correct step, and that the dependency structure matches: the transitive step dependencies written in the model are compared with the problem's `answer_step_prereqs` (or a strict chain when it has none), so a loosened or over-tight order fails. It also tries each theorem on 25 deterministic pseudo-random coordinate sets (the AA similarity, the midpoint theorem, SSS in the isosceles and parallelogram figures, the angle at the centre, the alternate segment theorem, opposite angles of a cyclic quadrilateral, and the perpendicular bisector locus). Negative control (`proof_tampers` in the test): no order, a strict order where the proof allows two, two steps swapped, a distractor that says what a keyed step says, a changed number: 34 of 34 caught. The `ordering` check and `register.ORDER_FREE_PAIRS` are unchanged and still agree with the models.

### Remaining exemptions (reviewed 2026-10-23)

None among practice slots. The 15 static MCQ bank items below are kept pinned by digest because there is nothing to compute; every key and option was read by hand again on this date. Category `conceptual` is a definition, name or interpretation; `method` is a choice of rule or construction procedure.

| Digest | Category | Item and reason |
|---|---|---|
| `d2ad3f201b3c` | conceptual | BIDMAS: what the letter I stands for. Vocabulary of the mnemonic. |
| `bbd4b325472c` | conceptual | Definition of the hypotenuse. A naming convention. |
| `74b0c6a3fb7c` | conceptual | What SOH CAH TOA is for. Vocabulary. |
| `2383102f84e0` | method | Cosine rule for two sides and the included angle. A method judgement. |
| `e747319c3334` | conceptual | Which ratio is outside the GCSE right-angled set (sec). Syllabus knowledge. |
| `6b871d529a0a` | conceptual | Definition of the angle of elevation. A naming convention. |
| `44b1476f6ef1` | method | Best first step in a 3D trigonometry problem. A method judgement. |
| `f201e85aaa3b` | method | Rule for an angle from three sides (cosine rule rearranged). A method judgement. |
| `e8537eb33269` | conceptual | Meaning of sin A greater than 1 in the sine rule (no such triangle). Interpretation. |
| `0b8800279556` | conceptual | Plain-language description of elimination. A definition. |
| `5d9cdf21e4ce` | method | Which tools construct a triangle from three sides. A method statement. |
| `cfc695431cea` | conceptual | Locus equidistant from two intersecting lines. Described in words only. |
| `aa47f1d3264c` | conceptual | Region closer to A and within 6 cm of B, in words. A region has no single value. |
| `9ff174a302c5` | conceptual | Shape of the locus at a fixed distance from a segment (stadium), in words. |
| `c0446fea7f9a` | method | Constructing 30 degrees (build 60 then bisect). A construction procedure. |

The test checks the format of this table (category, reason of 20 or more characters), fails on a stale entry (a digest with a spec, or one that matches no item) and on an item that is neither re-solved nor listed. The reasons are in `register.STATIC_EXEMPT`.

### Deep mode and the lesson-quiz sweep

`--deep` is 200 seeds per practice slot (algebra included), 40 per direct MCQ slot, 100 per procedural MCQ function, and a quiz sweep of 40 seeds per topic. About 200 s on this machine with two runs side by side. No scheduled job (decision 3). The default run keeps 14 to 20 seeds and a two-seed quiz slice (64 quizzes, 630 questions, about 1.5 s of the run).

A GCSE maths topic has no `lesson_bank`, so its ten-question quiz (`build_lesson_quiz`) draws MCQ problems from the same variant slots; what the quiz adds is the draw (3 foundational, 4 intermediate, 3 difficult, no repeated question text), the option shuffle and the grading. `scripts/gcse_verify/quiz.py` (`verify_quiz_items` in the plan) builds each seeded quiz through the real builder with a recording wrapper, so a question's records belong to the exact problem drawn, then checks: the shape; the key (a generated question is re-solved from its records; a bank question is re-solved by its digest spec after the quiz's own shuffle, so a key lost in the shuffle is caught; or it is one of the 15 reviewed exemptions); four distinct options lettered A to D with the key naming one of them; and `grade_lesson_quiz_problem` marking the keyed letter right and each other letter wrong. Negative control: a quiz with every key moved to another option is reported question by question (44 of 44 in the default run, 47 of 47 in the deep run at 123456).

Results (deep, per seed offset below): 1,280 quizzes, 12,600 questions each, about 5,500 from generators and 6,700 bank questions re-solved, 380 to 400 reviewed exemptions, about 50,350 letters graded, no failure. The sweep found one shape limit that is a content gap, not a wrong answer, now recorded in `register.QUIZ_SHAPE` with the measured reason: `algebraic_proof` has only 5 distinct multiple-choice question texts across all three bands, so its quiz holds 5 questions, not 10 (3 foundational, 2 intermediate, no difficult); `vectors` and `pythagoras` have only 3 distinct foundational and 3 distinct intermediate questions, so the quiz is 3 / 3 / 4; `simultaneous_equations` has 3 intermediate, so it is 4 / 3 / 3. **For David:** these four topics need more multiple-choice questions in the short bands (the quiz builder is behaving as designed). The other 28 topics build ten questions in the 3 / 4 / 3 mix on every seed.

### Deep runs

| Seed offset | Practice questions | Result | Time |
|---|---|---|---|
| 0 | 214,400 | clean | 194 s |
| 50000 | 214,400 | clean | 195 s |
| 123456 | 214,400 | clean | 199 s |

Each run also does about 19,300 checker round-trips, 5,034 drift generations and the quiz sweep above. Offsets 0 and 50000 ran side by side; 123456 ran with a drift dump alongside. No fix was needed for any deep-run failure: there were none. Default run (alone, `--seed 0`): 24 to 28 s (limit about 35 s).

### Fixes in Phase 4

1. `_FDP_MCQ_BANK`, "0.2 recurring as a fraction": option C was `2/10`, the same value as option A `1/5`. Now `22/100`. Found by the generic option check once the item was re-solved.
2. `_SURD_MCQ_BANK`, "(sqrt 5) squared equals": option C was `sqrt 25`, which is 5, a second correct answer beside A. Now `sqrt 10`.
3. `check_algebraic_fraction` (rationalised surd answers): `(1/3)sqrt6` is now read as sqrt 6 over 3. Only a bracketed fraction of whole numbers directly before a surd is read this way; `1/3sqrt6` stays refused (it could mean 1 over 3 sqrt 6), and zero and malformed forms are refused. With the simplest-surd form on, `(4/10)sqrt3` for 2sqrt3 over 5 gets the "equal but not simplest" message. Tests: `test_check_algebraic_fraction_surd_bracketed_fraction_coefficient`.
4. `algebraic` checker: letters written side by side are a product in any order, so `2ba` is `2ab`, `3yx+2` is `3xy+2` and `ca+ba` is `ab+ac`. Runs of letters are split into single letters only for SymPy, after the existing length, symbol, exponent and node caps are applied to the result; a bare name on either side (`AB`, `BC`, `ba` against `ab`) is never reordered, so a vector name keeps its direction. Tests: `test_check_algebraic_letters_in_any_order` and `..._keeps_the_caps` (long letter runs, exponent towers, 1,000-character inputs, all refused in well under 5 s). Left for later, as agreed: identical-magnitude variants.
5. Test-side: a lesson-quiz record map keyed by question text alone attached a rejected attempt's records to the question that was kept (a trigonometry exact-value question was checked against another angle); records are now keyed by question, options and key.

### Drift

Against `bb3f366` (a `git archive` copy): 3 runs of every one of the 1,678 slots (5,034 generations, all 32 topics, SVG ids normalised). Only 5 differ, all of them the two bank edits above (the `22/100` option twice, the `sqrt 10` option three times): every other generation is byte-identical, including the seven proof slots, which now call `record('proof_model', ...)`. The checker changes do not touch generators.

### Checks run

Verification smoke (default, alone): passes. Three deep runs: clean. `test_gcse_maths_correctness_smoke.py` and `test_answer_check_smoke.py`: pass. `ruff check .`: clean. Full suite: see the AI handoff line.

### Phase 4 review notes (independent reviewer, 2026-10-23)

Reviewed section 15 against the plan and the code (`solvers_bank*.py`, `solvers_proofs.py`, `quiz.py`, `coverage.py`, `register.py`, `mcq.py`, the test, the four generator diffs, `answer_checkers.py`, `lesson_quiz.py`). Nothing committed.

**Confirmed.** Every bank spec is keyed by the item digest (plain question, sorted option texts, keyed text), so any edit to a question, an option or the key fails the test until a person looks at the spec; moving the key together with its option text is a shuffle and still verifies. Specs read only the displayed question and the option texts (never the solution, hint or key), and the independence check passes. The proof models compare each keyed step with the step the proof needs, with the numbers recomputed from the question, check that no distractor reads as a correct step, and compare the transitive dependencies with `answer_step_prereqs`; one limit worth stating plainly is that the step patterns are the generator's wording copied as patterns, so for wording they act as a reviewed pin, and only the numbers, the order, the dependencies and the geometry (random coordinates) are recomputed. The quiz sweep uses the real `build_lesson_quiz` (with the option shuffle in `make_problem`) and the real `grade_lesson_quiz_problem`. Drift against `bb3f366`, re-run by this review (3 runs of all 1,678 slots, 5,034 generations, SVG ids normalised): exactly 5 generations differ, all from the two bank edits (`22/100` twice, `√10` three times); the generator diffs are those two option texts and seven `record('proof_model', ...)` lines.

**Spec sample.** All 318 distinct specs were read (319 items: the item "x + y = 7 and x - y = 3" sits in two banks and shares one spec). Beyond reading, a bypass harness changed each number in each re-solved question by one and re-registered the spec under the new digest, so the digest guard was out of the way and only the spec could catch the change. After the fixes below, 28 specs have no number in the question (definitions checked on a model: angle in a semicircle measured on a circle, tangent found as the direction that meets the circle once, Pythagoras formula tried on triples, and so on), 256 fail whenever any number in the question changes, 26 fail on some numbers, and 8 on none. The survivors were read one by one: labels ("3-figure", "u_6", "(2) from (1)"), prime factorisations written beside a number, angles in a diagram caption, a repeated "0.2" in "(0.2̄)", and changes too small to move a rounded or categorical answer (290° is still in the NW quadrant, 81 g in 120 cm³ still floats, √51 is still between 7 and 8, sides 6, 12, 14 are still not right-angled).

**Found and fixed: specs that restated the answer or ignored the numbers asked about.**
- Medium, transformations: `8e6eb7b34c18` (rotation of (a, b)) had (-b, a) written in and ignored "90° anticlockwise"; the five point-image items (`67e074311bc1`, `26ae5054fad2`, `f4faf6e386cd`, `a9368b1e8f04`, `ff6d24d02cbf`) each had their transformation written in by hand. A new `stem_map` reads the angle and direction, or the mirror line, from the question and builds the rotation or reflection matrix.
- Medium, `5715064775f3` (make t the subject): hard-coded s = ½at² and ignored the formula shown; it now reads the formula and the given u.
- Medium, `46b407f316cd`: read the HCF and LCM but not the products actually asked ("Does 7 × 70 = 14 × 35?"); now reads them (and keys "No" if they differ). `e7a10ff5f23b`: the divisor 6 was written in; now read.
- Medium, circular truths: `4955f0684fe7` computed the "true" area with ½ab sin C itself (now from coordinates); `f3f3040bb606` wrote the bisector direction in as upright (now found as the points equally far from A and B); `2ce353347cfd` used (θ + 180) mod 360 as the truth (now the bearing of the reversed displacement); `6ae9a944a425` had constant counts for SSS, AAA and two angles (now built: cosine rule, the same angles at two sizes); `497512b19b51` had AAS as a constant and a trivial RHS test (now read from the given right angle, hypotenuse and leg); `496ad8a7cb8d` named the vector quantity by writing it as a pair (now: the quantity that changes when the journey is reversed).
- Low, consistency: the silo's hemisphere radius was assumed equal to the cylinder's (now read); the map scale numerator, the bus start minutes, and the arithmetic and geometric terms shown after the first two are now checked.
- Low, proof model `centre_angle` halved the angle with `//`, so an odd angle with a truncated half would have passed (generators use even angles only); now exact.

**Found and fixed: the letter-order checker change (High).** The value check split letters but the form check did not, and a structure it cannot read is accepted once the value is right: `3(2ab+a)` was marked correct for an "expand" key `6ab+3a`, and `5(x^2-2xy)` as fully factorised for `5x(x-2y)` (before Phase 4 both were marked wrong by value, so this was a new way round the form rules). The form check now reads the pupil's answer with the same letter rule. Also, letter runs were split inside larger answers whatever they named: `BA+BC` was accepted for `AB+BC`, `2BA` for `2AB`, and `2sin(x)` for `sin(2x)`. No generator key has these today (a sweep of every level and subject, 4 seeds per slot: the only `algebraic` key with letters side by side is `u=v-at`, and `algebraic` and `algebraic_fraction` are produced only by GCSE maths), but the rule is now: no reordering when the key names something in capitals (`AB`), when either side names a function (sin, cos, tan, log, ln, exp, abs), or when either whole answer is a bare name. Test: `test_check_algebraic_letters_in_any_order_keeps_forms_and_names`. Bombs (26 letters x 3, `ab` x 500, `(abcdef)` x 30, long products of brackets, towers, `pi` and `sqrt` runs, 2,000-character inputs) through `algebraic`, `formula_fraction`, `algebraic_fraction`, `surd` and `linear`: slowest 0.005 s; the caps are applied after the split. `(1/3)√6` probes: `(1/3)√(6)`, `(1/3) √6`, `(3/9)√6` and `(1/3)sqrt(6)` read; `1/3√6`, `1/3 √6`, `(1/3)√6+1`, `(0/3)√6` and `(1/0)√6` refused. Not read (low, left): `(1/3)*√6`, `(1/3)sqrt6` and a negative bracketed coefficient.

**Coverage, recomputed.** Independently of `coverage.py`, every MCQ dispatch slot was generated 120 times and each drawn question matched to its bank item: 551 of 606 slots strict (90.9%), with the same per-topic figures as section 15 (trigonometry 0 of 21, constructions_loci 7, bidmas 14, pythagoras 14, simultaneous_equations 12 of 18), and no drawn item outside the pool `coverage.py` assumes. The metric is honest (a slot counts only when every bank item it can serve has a spec, and an item with a spec that does not verify fails the test). The printed summary called the pool share (96.7%) "fully verified"; it now leads with the strict figure and prints the pool share beside it.

**Exemptions.** All 15 read again; every key is right and none has a second correct option. Three loci items (`cfc695431cea`, `aa47f1d3264c`, `9ff174a302c5`) could be "re-solved" the way `852f2a72edd4` is, by a dictionary from option words to point sets, but that dictionary is itself a reading of the options, so they stay exempt.

**Short quizzes.** Over 200 seeds each the builder never crashed or repeated a question: `algebraic_proof` always 5 questions (3 / 2 / 0), `vectors` and `pythagoras` 3 / 3 / 4, `simultaneous_equations` 4 / 3 / 3; the quiz pages use the length of the list, so a 5-question quiz plays and scores normally. **Content needed for David:** `algebraic_proof` has 5 multiple-choice stems shared by all three bands (always even, n(n+1), always odd, the n² + 1 counterexample, (n+1)² - n²); at least 5 more distinct ones are needed for ten questions, with at least 2 reachable in the intermediate band and 3 in the difficult band for the 3 / 4 / 3 mix. `vectors`, `pythagoras` and `simultaneous_equations` each need 1 more distinct intermediate question.

**Mutation tests** (each applied alone, the test run, the file restored and checked by SHA-256): bank question number changed with the key kept; bank key letter changed; two bank options swapped with the key letter kept; two keyed proof steps swapped (`_sc_i9`); a wrong number in a keyed proof step (`_ct_d4`); a proof dependency loosened (`_sc_i9`); a distractor made to say a keyed step; one quiz key moved after the quiz is built; quiz grading comparing the wrong letter; the form check reading letters unsplit; the capital-name guard removed. All 11 failed, each for the expected reason (bank: digest not reviewed; proofs: `proof_model` verdicts; quiz: the quiz check; checker: the new unit test). Swapping two options and moving the key with them still verifies, as intended.

**Results.** Default verification alone 25.3 s (26.2 s wall); `--deep --seed 271828` on the implementer's tree clean (192.7 s); `--deep --seed 314159` after this review's fixes clean (214,400 practice questions, 1,280 quizzes, 47 of 47 wrong quiz keys caught; 202.6 s). Answer-check smoke, GCSE correctness smoke and `ruff check .` pass.

### Quiz content additions (2026-10-23)

The Phase 4 sweep found four topics whose lesson quiz could not reach ten questions in the 3 / 4 / 3 mix because a band had too few distinct question texts. This adds the missing multiple-choice content. Nothing committed; no static, JS or template file changed, so no `?v=` or `CACHE_VERSION` bump. `register.QUIZ_SHAPE` is now empty and `quiz.py` asserts ten questions, 3 foundational + 4 intermediate + 3 difficult, no repeated question, for every topic. Over 200 seeds each, `algebraic_proof`, `vectors`, `pythagoras` and `simultaneous_equations` build 10 questions in the 3 / 4 / 3 mix with no repeat on every seed (2,000 questions per topic, no verification finding).

**Static bank items (six).** Each has a digest-keyed spec that reads the numbers from the displayed question and computes the answer (`solvers_bank_number.py`, `solvers_bank_geometry.py`, `solvers_bank_algebra.py`). Changing any number in a question makes its spec fail (tried for every number in all six; the wrong-key negative control catches every wrong letter, 975 of 975 across the bank). To keep the bands exactly as they were, every existing item in the `pythagoras` and `vectors` banks now carries an explicit `difficulty` (before, the band came from the item's position, which a longer bank would have shifted).

| Topic | Band | Question | Key | Distractors (misconception) |
|---|---|---|---|---|
| pythagoras | intermediate | A rectangle has a diagonal of 17 cm and one side of 8 cm. What is the area of the rectangle? | 120 cm² | 136 cm² (8 × 17, diagonal used as a side); 225 cm² (square of the missing side); 68 cm² (half of 136) |
| pythagoras | intermediate | Points A (1, 2) and B (7, 10) are plotted on a coordinate grid. What is the distance AB? | 10 units | 14 units (6 + 8); 100 units (no square root); 48 units (6 × 8) |
| vectors | intermediate | If a = (3, 1) and b = (-2, 4), find 2a + b. | (4, 6) | (4, 5) (only the first component doubled); (1, 5) (a + b); (8, -2) (2a - b) |
| vectors | intermediate | The position vectors of P and Q are OP = (1, 2) and OQ = (4, 6). What is the length of PQ? | 5 | 7 (3 + 4, no Pythagoras); 25 (no square root); 10 (4 + 6, uses OQ not the difference) |
| simultaneous_equations | intermediate | Solve simultaneously: 3x + 2y = 16 and x + y = 6. What is x? | x = 4 | x = 2 (the value of y); x = 6 (the total of the second equation); x = 10 (16 - 6) |
| simultaneous_equations | intermediate | At a cinema, 2 adult tickets and 1 child ticket cost £14. 1 adult ticket and 1 child ticket cost £9. How much is one adult ticket? | £5 | £4 (the child price); £7 (14 ÷ 2); £9 (the second total) |

Specs: `rectangle_area_from_diagonal` (reads "diagonal of" and "one side of", other side by Pythagoras, then the product), `distance_between_points` (reads the two written points), `combination_of_a_and_b` (reads the two columns and the coefficients in "find 2a + b"), `length_between_position_vectors` (reads OP and OQ and the vector named in the question, works out the difference), `system_asks` (the existing sympy solve of the pair, asked for x) and `ticket_prices` (reads the two purchases and the price asked about, solves the pair).

**Algebraic proof (nine new generators, and four existing ones now served).** Before, one list of nine generators was shared by all three bands and `count=4` meant only its first four ever ran, so every band served the same five question texts. Now each band has its own pool (`_AP_MCQ_FOUNDATIONAL`, `_AP_MCQ_INTERMEDIATE`, `_AP_MCQ_DIFFICULT` in `generators/gcse/algebraic_proof.py`) and every generator in it is reachable (one MCQ slot per generator). Four existing generators that were never served now are (the sum of two consecutive numbers, the sum of three, the valid proof method, factorising n² + n); `_ap_mcq_odd_square` stays unused (its "Sometimes prime only" distractor is not a misconception). Nine are new, and every generator in the pools is re-solved, none exempt:

| Band | Question (procedural parts in brackets) | Key | Distractors | Re-solved by |
|---|---|---|---|---|
| foundational | Even or odd? (already live, now foundational only), n + (n + 1), (n - 1) + n + (n + 1), valid proof method | as before | as before | existing tasks `ap_always`, `simplify`, `keyed_text` |
| intermediate | (n + 1)² - n²; n(n + 1); the n² + 1 counterexample; factorise n² + n | as before | as before | existing tasks |
| intermediate (new) | Which pair of expressions always represents two consecutive odd (or even) numbers? | 2n + 1 and 2n + 3 (or 2n and 2n + 2) | three of: consecutive integers (2n and 2n + 1), mixed parity (2n + 1 and 2n + 2), n and n + 2, a gap of 4 (2n + 1 and 2n + 5, 2n and 2n + 4) | `ap_consecutive_form`: both expressions have the stated parity for every n in -12 to 12 and differ by 2 |
| intermediate (new) | The sum of two consecutive odd numbers is (2n + 1) + (2n + 3). For any integer n, this sum is: | Always a multiple of 4 | Always odd; Always a multiple of 3; Always a multiple of 8 (try n = 0) | `ap_prop` (property tested over n = -12 to 12) |
| intermediate (new) | For any integer n, which expression is always a multiple of k? (k from 3, 4, 5, 6, 7, 9) | kn + kj, k(n + j) or kn - kj | three of: n + k; kn + k/2 (rounded down); n² + k; n(n + k) | `ap_mult_expr`: k read from the question, each option tested for every n |
| intermediate (new) | Which value of n is a counterexample to the claim that f(n) is prime for every positive integer n? (f from 2n + 1, n² + n + 1, 6n + 1) | the one value that makes f(n) composite | three values that give primes | `ap_counter_value`: the expression is read from the question, each option tested for primality |
| difficult (new) | For any integer n, which expression is always a multiple of 8? | (2n + 1)² - 1 | (2n + 1)² + 1; (2n)² + 4; (2n + 2)² - 4 | `ap_mult_expr` |
| difficult (new) | The difference between the squares of two consecutive odd numbers is (2n + 3)² - (2n + 1)². This simplifies to: | 8(n + 1) | 8 (middle terms dropped); 12n + 8 (one middle term dropped); 4n + 4 (halved) | `simplify` (sympy; also checks no other option is equal) |
| difficult (new) | A student is showing that the expression in line 1, (2n + k)² - k², is a multiple of 4. Which line of the working contains the first mistake, if any? (k from 1, 3, 5; four lines; the mistake is in line 2, 3 or 4, or there is none) | the line where the working first stops equalling the line before, or "There is no mistake" | the other lines and "There is no mistake" | `ap_find_error`: the lines are read from the question and compared by expanding each with the one before |
| difficult (new) | For any integer n, the expression f(n) is: (f from n² + (n + 1)², 3n + 1, 2n(2n + 2), n³ - n, n² + n + 1, (n + 1)² - (n - 1)², (n + 3)² - n²) | one true statement (always even, odd, a multiple of 3, 4 or 8, or sometimes even and sometimes odd) | three statements that fail for some n | `ap_prop` (extended with "sometimes even and sometimes odd") |
| difficult (new) | n is a whole number and n² is even (or odd). Which statement must be true? | n is even (or odd) | n is odd (even); n could be either odd or even; n is a multiple of 4 (or 3) | `ap_square_parity`: the whole numbers with that square parity are listed and each statement tested |

The statement options in the property question are only ever drawn from the false statements plus one true one, so exactly one offered option is true even where another true statement (for example "Always even" beside "Always a multiple of 4") exists but is not offered. The foundational pool is the four generators above (5 distinct texts, because the even or odd generator has two); intermediate has 8 generators and difficult has 5, so a 3 / 4 / 3 quiz never runs short. Negative control: for every new generator, every wrong key over 40 seeds is caught (2,040 of 2,040).

**Verification integration.** No exemption was added: the static bank has 325 re-solved items and 15 exempt (unchanged), `register.STATIC_EXEMPT` and `register.EXEMPT` are untouched. Five new tasks (`ap_consecutive_form`, `ap_mult_expr`, `ap_counter_value`, `ap_find_error`, `ap_square_parity`) were added to `solvers_algebra.py` and `ap_prop` gained one phrase; they read the displayed maths and options only (the generators record nothing but the task name). Coverage after this change: MCQ 556 of 611 slots strict (91.0%, was 90.9%), pool share 96.8%, static items 325 of 340 re-solved (95.6%).

**Drift.** Against the working tree before this change (3 runs of every slot, 5,049 generations): only the multiple-choice slots of `algebraic_proof` (33 changed, 15 new), `vectors` (17), `pythagoras` (18) and `simultaneous_equations` (15) differ; every other generation, and every practice slot, is byte-identical.

**Results.** Default verification alone 25.1 s; `--deep --seed 424242` clean (214,400 practice questions, 1,280 quizzes of 10 questions, 195.5 s); `test_gcse_maths_correctness_smoke.py`, `test_answer_check_smoke.py` and `ruff check .` pass; full suite in the AI handoff line.

### Quiz content review notes (2026-10-23)

Independent review of the quiz content additions, read as a GCSE maths teacher and as code. Every new or newly served generator was run over 400 seeds and every distinct question (with its options, key, solution and hint) was read; a separate checker written for this review (not the verification tasks) confirmed exactly one true option on 3,000 seeds of each procedural generator. No key was wrong and no question had two right answers.

**Changed in this review (all in `generators/gcse/algebraic_proof.py`).**

* Expression property question (difficult). The solution said "test \(n = 0\) and \(n = 1\): it is always ..." for every expression, which models the very mistake the proof-method question warns against, and for \(n^3 - n\) both tests give 0, which is a multiple of everything, so following the hint could not rule out "Always a multiple of 4" or "of 8". Each expression now carries its own algebra (for example \(n^3 - n = (n - 1)n(n + 1)\), three consecutive integers multiplied together), and each offered wrong statement gets a value of \(n\) where it fails (for example "“Always a multiple of 8” fails when \(n = 2\): the expression is 6"). Hint: "Expand and simplify first. To rule an option out, find one value of n where it fails."
* Always a multiple of k (intermediate). The solution now shows the factor (\(6n + 12 = 6(n + 2)\)) instead of only asserting it, and the hint names the number ("A multiple of 6 has 6 as a factor") instead of a bare "k".
* First mistake question. The line 3 explanation wrote the middle term outside LaTeX; it is now \(20n\).
* Even or odd question (now foundational). Its options were plain text beside LaTeX neighbours; they are now in LaTeX.
* Two newly served questions had hints that did not fit: "Three consecutive integers always sum to 3n" gave the answer away (now "Collect the n terms, then collect the number terms"), and "Factorise first, then explain using consecutive integers" on a plain factorising question is now "Look for a factor that both terms share".

**Checked and left as they are.** The consecutive odd or even pair question cannot be read two ways (\(n\) and \(n + 2\) are consecutive odd numbers only when \(n\) is odd, and the question says "always ... for any integer \(n\)"). The counterexample value question always offers exactly one composite value (the others are primes for that expression). In the first mistake question the lines after a mistake follow correctly from the wrong line, so exactly one line is first wrong, and no wrong line is accidentally right for \(k = 1, 3, 5\). In the property question "Always even" and "Always a multiple of 4" (or 8) can both be true, but only one true statement is ever offered. The six static items are correct, their distractors match the misconceptions in the table above, and the bands are sensible (all six intermediate, where the short band was). British spelling, no em or en dash, no emoji in any new text (the em dashes the lint finds in these topics are in hints that predate this change).

**Bands of the existing bank items.** Before, the band came from position (10 items, so items 1 to 3 foundational, 4 to 6 intermediate, 7 to 10 difficult). Stripping the new `difficulty` fields and the two new items and re-running `normalize_mcq_bank` gives exactly the bands now written in both banks, so nothing moved. Some of those inherited bands are generous (for example the length of \((0, 5)\) and "which is a unit vector" are difficult in `vectors`; "which calculation finds the distance from (0,0) to (6,8)" is difficult in `pythagoras` while the new A (1, 2) to B (7, 10) item is intermediate); they were kept so this change does not move questions pupils already see, and are worth a look in a later content pass.

**Algebraic proof structure.** Practice mode still uses `_POOLS` unchanged and its output is byte-identical; only the `mcq` branch reads the band pools. The pools hold 4, 8 and 5 generators and the queue has one slot per generator, so all 17 are reachable. A difficulty outside the three bands falls back to all 17 (before, the first four). Nothing else references `_AP_MCQ_POOL` or the old slot names.

**Mutation tests (all restored afterwards).** Static items, run through their spec under the original digest: every number in each question changed one at a time is caught (2, 4, 5, 4, 4 and 6 numbers, 25 of 25); every moved key is caught (18 of 18); a distractor made equal to the key in number form (120.0 cm², (4,6), x = 4.0, £5.00, 10.0 units, 5.0) is caught. A distractor written as an unevaluated surd equal to the key (√100 units, √25) is not caught: the generic option matcher does not evaluate a surd against a whole-number answer. No current item has such an option; it is an engine-wide limit, not a fault of these specs. Generators, 60 seeds each: the moved key is caught for all 14 served generators (2,520 of 2,520); a distractor rewritten to be a second right answer (for example \(2n + 2\) and \(2n + 4\) for consecutive even, \(2kn + k\) for a multiple of \(k\), a second composite value, "Always even" for \(4n + 4\), \(8n + 8\), "\(n\) is a multiple of 2") is caught for the ten generators where that can be written (600 of 600); in the first mistake question, making the wrong line right (or breaking a right line when the key is "no mistake") is caught 200 of 200, and correcting only line 2 while the later lines still follow the old wrong line (so line 3 becomes the first mistake) is caught 54 of 54.

**Quiz shape.** 300 seeds per topic on `algebraic_proof`, `vectors`, `pythagoras` and `simultaneous_equations`, and 100 on every other topic: every quiz has 10 questions, 3 / 4 / 3, and no repeated question. The same question with other numbers can appear twice in one quiz (for example two "always a multiple of k" questions, or two counterexample value questions): 28%, 17%, 17% and 29% of quizzes on the four topics. The app already does this elsewhere (100% of quizzes on `number`, `ratio_proportion`, `functions` and others, 80% or more on `decimals`, `statistics`, `probability`), so it is reported, not changed.

**Results after the review edits.** Coverage unchanged: MCQ 556 of 611 slots strict (91.0%), pool share 96.8%, static items 325 of 340 re-solved. Default verification alone 24.7 s. `--deep --seed 737373` clean (214,400 practice questions, 1,280 quizzes of 10 questions, 195.3 s). Drift against the tree with the four generator files at `bb3f366` (3 runs of every slot, 5,049 generations): only multiple-choice slots of `algebraic_proof` (36 changed, 15 new), `pythagoras` (18), `vectors` (17) and `simultaneous_equations` (15) differ; every other generation is byte-identical. `test_gcse_maths_correctness_smoke.py`, `test_answer_check_smoke.py` and `ruff check .` pass; full suite 104/104.
