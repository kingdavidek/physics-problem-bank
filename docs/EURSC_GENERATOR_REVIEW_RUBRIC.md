# European School Integrated Science — Practice generator review rubric

**Track:** Open and curate the main Practice generator for Integrated Science S1–S3 (46 topics).  
**Use:** Every agent curating `standard` practice slots, launch-gate work, or generator smokes in this track.  
**Slot-recipe source of truth:** Cursor canvas `eursc-generator-question-plan.canvas.tsx`.  
**Curriculum / safeguarding:** `docs/EUROPEAN_SCHOOL_SCIENCE.md`; `DISCLOSE_RE` in `scripts/test_es10_whole_suite_smoke.py`.  
**Handoff:** `docs/EURSC_GENERATOR_HANDOFF.md`.  
**Last updated:** 2026-08-30 (Phase 6 year-by-year Practice-home QA)

This is not a rewrite of the 46 lesson templates. Lesson banks (`mode=lesson`) and ten-question quizzes stay as they are. Practice work is **select / lightly rewrite** five generator-safe items per topic per difficulty from those banks.

---

## Delivery phases

Do **one phase per user cue**. Stop and report when the phase is done. Do not reopen the completed lesson-clarity track (Stages 0–7) unless fixing a regression.

| Phase | Name | Scope | Status |
|-------|------|--------|--------|
| **0** | **Baseline and contract** | Smoke baseline + this rubric | **Complete** (2026-08-29) |
| **1** | **Explicit standard pools** | Name five curated slots per topic×difficulty; `standard` returns exactly those five; **no** fallback from standard → lesson | **Complete** (2026-08-29) |
| **2** | **Align to canvas recipes** | Curate/lightly rewrite so each tier matches MCQ / keyword / data / ordered / pick-set intent | **Complete** (2026-08-29) |
| **3** | **Launch gate** | Replace `GENERATOR_LAUNCH_GCSE_MATHS_CS` boolean with an allowlist including `eursc/science`; fix home selectors, POST, and `problems/generate` validation | **Complete** (2026-08-29) |
| **4** | **Safety regression** | Sensitive banks + templates still pass `DISCLOSE_RE`; no QOTD eursc; IBL not in generator | **Complete** (2026-08-30) |
| **5** | **Matrix smoke** | Assert 46×3×5 standard variants, unique names, valid payloads, API/web generate, no leakage | **Complete** (2026-08-30) |
| **6** | **Roll out by year** | Year-by-year Practice-home QA (S1 then S2 then S3); full smoke + desktop/mobile after each year | **Complete** (2026-08-30) |
| 7 | Verification | Full suite green + sample generate on Practice home for sensitive and S3 topics | Pending |

---

## Phase 0 baseline (2026-08-29)

Recorded locally against current `main` worktree. No Practice home, launch-gate, or bank rewrites in this phase.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Suite size | **65** files (`scripts/test_*_smoke.py`) |
| Result | **All 65 smoke tests passed.** |
| Slot constant | `EURSC_PRACTICE_SLOT_COUNT = 5` in `generators/eursc/science_shared.py` |
| Standard pools | All **46** syllabus topics × **3** difficulties return **exactly five** `standard` variants (`138` of `138` tiers) |
| Lesson pools | `mode=lesson` still returns the **full** bank (10–13 items per tier; mean ≈ 10.07). Every practice slot is a member of that lesson pool. |
| Practice home | Still GCSE-only: `GENERATOR_LAUNCH_GCSE_MATHS_CS = True`; `GENERATOR_LAUNCH_SUBJECTS = {'maths', 'cs'}` |
| QOTD | `models/qotd.py::list_mcq_topic_paths` skips `level == 'eursc'`; ES10 `test_practice_and_qotd_stay_closed` still asserts this |

**Kind-mix vs canvas (Phase 0 measurement, now historical):** the old `eursc_practice_pool()` sampler walked `_PRACTICE_KIND_ORDER` and could pick two MCQs or two numerics. Phase 1 replaced that runtime path with named lists. Of 138 tiers, **116** already had all five recipe families in the lesson bank; **20** still lack a data or ordered *item* (see Phase 1).

---

## Phase 1 explicit pools (2026-08-29)

Named five-slot lists live next to each lesson pool. `standard` resolves those names only. Practice home and `GENERATOR_LAUNCH_*` unchanged.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Result | **All 65 smoke tests passed.** |
| Named lists | `_XX_STANDARD` (or `_MEAS_STANDARD` / `_WIS_STANDARD` / `_LAB_STANDARD` / `_STANDARD`) in `s1_*.py` … `s3_*.py` and `science_es0_fixture.py` — 46 topics + es0 fixture |
| Binder | `bind_eursc_topic(topic, pools, standard_slots)` requires the name map; `generate(mode='standard')` raises if the pool is empty or the name is not one of the five |
| Lesson quizzes | Unchanged — `mode=lesson` still returns the full bank |
| Slot smoke | `scripts/test_es_practice_slots_smoke.py` asserts count, stability, no lesson leak, no empty-pool fallback |

**Still Phase 2 at the time:** 20 lesson-bank tiers still had no data (or measurement foundational had no ordered) item to name.

---

## Phase 2 canvas recipes (2026-08-29)

Every `standard` tier is now **MCQ, keyword, data/numeric, ordered, pick/set** in that order. Missing S1 items were added to the lesson banks (quizzes still draw 10 from the full pool). Practice home and `GENERATOR_LAUNCH_*` unchanged.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Result | **All 65 smoke tests passed.** |
| New bank items | Data/numeric on 19 S1 tiers that lacked them; ordered conversion steps on measurement foundational |
| 1.3.1 Movement | Syllabus kinematics (`v=d/t`, distance–time); not the canvas joint/muscle row (that stays 1.3.4) |
| Safeguarding | 1.4 data items use public/fictional aggregate charts only; ES10 `DISCLOSE_RE` still clean |
| S3 | Existing no-power / no \(V=IR\) claims kept; numeric slots use \(W=Fd\) or qualitative path counts |
| Slot smoke | `test_standard_recipe_order` + `test_movement_standard_is_kinematics` |

**Left for later phases:** launch allowlist (Phase 3 — done); payload/API matrix (Phase 5); year-by-year Practice-home QA (Phase 6).

---

## Phase 3 launch gate (2026-08-29)

Practice home and `POST /api/v1/problems/generate` accept GCSE Maths, GCSE CS, and European School Integrated Science. Physics, A-Level, and MYP stay out of the live catalogue. QOTD still skips `eursc`. IBL pages are not generator topics.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Result | **All 65 smoke tests passed.** |
| Allowlist | `GENERATOR_LAUNCH_PATHS` = `{('gcse','maths'), ('gcse','cs'), ('eursc','science')}` |
| Home | Level select shows GCSE + European School; subject includes Integrated Science; topic list is allowlisted (es0 fixture omitted from the picker) |
| API | `problems/generate` accepts `eursc/science`; rejects `gcse/physics` |
| QOTD | `list_mcq_topic_paths` still skips `level == 'eursc'` |
| Slot smoke | `test_practice_home_and_api_accept_eursc` |

**Left for later phases:** payload/API matrix (Phase 5); year-by-year Practice-home QA (Phase 6).

---

## Phase 4 safety regression (2026-08-30)

No disclose hits, no QOTD eursc, IBL stays off the Practice catalogue, and S3 standard slots do not ask for power or \(V=IR\) calculations. Lesson templates were not reopened.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Result | **All 65 smoke tests passed.** |
| Disclose | 1.4 / 2.2 / 2.3.7 (`interoception`) templates + lesson and standard banks clean under ES10 `DISCLOSE_RE` |
| QOTD | `list_mcq_topic_paths` still skips `level == 'eursc'` |
| IBL | `IBL_PAGES` slugs are not in `TOPICS` or the Practice topic picker; `/ibl/eursc/science/<slug>` still 200 |
| S3 | `force_work_machines`, `energy`, `electric_current` standard slots: no `power in watts?` / `P=W/t` / resistance-calculation stems |
| Slot smoke | `test_sensitive_standard_slots_and_templates_pass_disclose`, `test_ibl_pages_are_not_generator_topics`, `test_s3_standard_slots_have_no_power_or_vir_calculations` |

**Left for later phases:** final verification samples (Phase 7).

---

## Phase 5 matrix smoke (2026-08-30)

Every syllabus topic×difficulty returns five named standard variants with unique names and the MCQ / keyword / data / ordered / pick recipe. Direct `fn()` and `generate(..., variant_name=...)` payloads are grader-ready. Web POST `/` and `POST /api/v1/problems/generate` succeed for S1 measurement, 1.4.1 puberty, 2.2.1 health, and 3.1.4 electric current. Standard generate still cannot pull a lesson-only name. IBL and QOTD invariants unchanged.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Result | **All 65 smoke tests passed.** |
| Matrix | 46 topics × 3 difficulties × 5 slots = **690**; unique names per tier; recipe families in order |
| Payloads | MCQ: `options` + `correct_answer`; typed: `correct_answer_raw` + `answer_type`; order/pick: `proof_steps` |
| Web / API | Foundational generate for `measurement`, `puberty_maturity`, `healthy_living`, `electric_current` |
| Leakage | Every topic×difficulty with extra lesson items rejects hidden names (`Unknown standard variant`) |
| Slot smoke | `test_standard_matrix_payloads`, `test_standard_generate_never_leaks_lesson_items`, `test_web_and_api_generate_year_sample` |

**Left for later phases:** final verification samples (Phase 7).

---

## Phase 6 year-by-year Practice-home QA (2026-08-30)

Live catalogue already includes `eursc/science`. This phase generated every syllabus topic on Practice home and the API, then sampled S1 / S2 / S3 in the browser at desktop and a 390px mobile viewport. Lesson templates were not reopened.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Result | **All 65 smoke tests passed.** |
| Picker | Home topic list includes all **46** syllabus slugs (es0 fixture still omitted) |
| Web / API | Registered session: every S1 (18) / S2 (17) / S3 (11) topic × 3 difficulties; guest `difficult` still account-gated |
| Sensitive HTML | Rendered Practice-home bodies for 1.4 / 2.2 / 2.3.7 pass `DISCLOSE_RE` |
| S3 HTML | `force_work_machines`, `energy`, `electric_current` rendered bodies have no power / resistance-calculation stems |
| Browser (desktop) | `what_is_science` keyword Check → Correct; `puberty_maturity` (hormone, third-person); `healthy_living` MCQ Check → Correct; `interoception` third-person heartbeat model; `electric_current` switch/lamp loop, Check → Correct |
| Browser (mobile 390px) | Same `electric_current` MCQ grades after scrolling option D above the tab bar; `puberty_maturity` MCQ renders |
| Slot smoke | `test_web_and_api_generate_all_years` |

**Observations (not blocking; do not reopen banks for these):**

- `make_problem` `topic_name` still uses hyphens only, so Revise links show `What_Is_Science` / `Puberty_Maturity`.
- Foundational `electric_current` MCQ lists `compute V = IR` as a **distractor**, not a calculation prompt.
- On a 390px viewport the guest tab bar can cover the lowest MCQ option until the student scrolls; the option is tappable after scroll.

**Left for later phases:** final verification samples (Phase 7).

---

## Five-slot recipe (every topic × every difficulty)

The generator always has a difficulty control. “Five per topic” means **five stable slots at each of foundational / intermediate / difficult**, not five total split across tiers.

**Sizing:** 46 topics × 3 difficulties × 5 slots = **690** curated entries. Most already exist in lesson banks — select or lightly rewrite; do not invent a parallel bank from scratch.

| Slot | Intent | Typical platform tokens |
|------|--------|-------------------------|
| **1 · MCQ** | Misconception, diagram, or scenario; single best answer | `options` + `correct_answer` |
| **2 · Keyword** | Named structure, process, unit, or term | `keyword` |
| **3 · Data / numeric** | Table, graph, conversion, estimate, or qualitative meter reading | `number`, `number_estimate`, `number_fields`, `number_pair` (use ratio/fraction only where the syllabus supports it) |
| **4 · Ordered process** | Method, pathway, chain, or lifecycle in order | `proof_steps` with order flag `1` (`_kind` `order`) |
| **5 · Pick / set** | Classify, choose valid evidence, or pick N true statements | `proof_steps` with order flag `0` or `pick` (`_kind` `pick`) |

Match the **named canvas row** for that syllabus ref where practical. Do not force algebra, SQL, Python-run, surds, or vectors into science for variety.

---

## Canvas coverage matrix (summary)

Full per-topic wording lives in `eursc-generator-question-plan.canvas.tsx`. Every row is one MCQ + keyword + data/numeric + ordered + pick/set slot. Counts:

| Year | Units | Topics | Tiered entries (×3×5) |
|------|-------|--------|------------------------|
| **S1** | 1.1 Science Lab, 1.2 Food, 1.3 Sports, 1.4 Puberty | 18 | 270 |
| **S2** | 2.1 Universe, 2.2 Health, 2.3 Senses | 17 | 255 |
| **S3** | 3.1 Machines, 3.2 Living Earth | 11 | 165 |
| **Total** | 9 official themes | **46** | **690** |

**Emphasis by cluster (canvas intent, not current bank names):**

| Cluster | Refs | Slot 3 (data) flavour | Slot 4 (ordered) flavour | Safeguarding |
|---------|------|------------------------|--------------------------|--------------|
| 1.1 Lab | 1.1.1–1.1.3 | Mean, conversion, scale, table | Investigation / safety sequence | — |
| 1.2 Food | 1.2.1–1.2.8 | Counts, pH, concentration, label kJ | Process / project phases | 1.2.7–1.2.8: no personal diet diary |
| 1.3 Sports | 1.3.1–1.3.4 | Motion / force / pulse data | Pathway or recovery plan | — |
| 1.4 Puberty | 1.4.1–1.4.3 | Anonymous / public / fictional graphs | Endocrine, gamete, development sequences | **DISCLOSE_RE**; third-person only |
| 2.1 Universe | 2.1.1–2.1.4 | Scale, angles, particle counts | Models, light path, formulae | — |
| 2.2 Health | 2.2.1–2.2.5 | Population / outbreak / public charts | Claim evaluation, infection chain | **DISCLOSE_RE**; aggregate only |
| 2.3 Senses | 2.3.1–2.3.8 | Threshold / frequency / fictional aggregates | Sensory pathways | 2.3.7 interoception: no first-person body prompts |
| 3.1 Machines | 3.1.1–3.1.6 | \(W=Fd\), efficiency, qualitative meters | Machine / circuit / design loops | **No power**; **no \(V=IR\)** on 3.1.4 |
| 3.2 Living Earth | 3.2.1–3.2.5 | Footprint, pyramid, quadrat data | Lifecycle, cycle, key, field phases | Public/fictional field numbers |

**Canvas vs syllabus (Phase 2 applied this):** canvas row **1.3.1 Movement** names joint/muscle slots; the official module is distance/time, \(v=d/t\), and distance–time graphs (joints/muscles belong with 1.3.4). Practice slots for 1.3.1 follow the **syllabus**, keeping the five-format recipe.

Project modules (1.2.8, 3.1.6, 3.2.5) still get five **readiness / method / safety** generator slots. The physical product stays IBL/rubric and is **not** auto-graded in the generator.

---

## Stage 6 already shipped vs what remains

Lesson-improvement **Stage 6** (do not redo blindly) wired a **stable kind-mix sample** of the lesson bank into `standard`. It did **not** finish the Practice-generator track.

| Shipped (Stage 6) | Still this track |
|-------------------|------------------|
| `EURSC_PRACTICE_SLOT_COUNT`, `eursc_practice_pool()`, `eursc_variants_for_mode()`, `bind_eursc_topic()` | **Phase 1 (done):** explicit named five-slot pools in `s1_*.py` … `s3_*.py`; no `generate()` fallback |
| All unit modules + measurement/lab/es0 fixture variants call the helper | Keep lesson pools full |
| `scripts/test_es_practice_slots_smoke.py` (count + stability + no leak + matrix/API + year-wave) | **Phase 6 (done):** 46×3 Practice-home + API generate |
| Lesson quizzes still use the full `lesson` pool | Keep that invariant in every later phase |
| Practice home **open** for `eursc/science`; QOTD excludes `eursc` | **Phase 3 (done):** `GENERATOR_LAUNCH_PATHS`; **never** add eursc to QOTD |
| Some stem wording aligned with improved lessons | **Phase 2 (done):** five-family recipe on all 138 tiers; S1 gaps filled |

**Code gaps vs canvas (Phase 6 year-wave done):**

1. **Phase 7 remains:** final Practice-home verification samples.

---

## Rollout by year (Phase 6)

Ship behind **one** allowlist flag once Phase 3 lands, but **QA content year by year**:

| Wave | Scope | Exit |
|------|--------|------|
| **S1** | 18 topics (1.1–1.4), including 1.4 safeguarding | Five named slots × 3 difficulties; `DISCLOSE_RE` clean; desktop + mobile generate sample |
| **S2** | 17 topics (2.1–2.3), including 2.2 + interoception | Same; public/aggregate health data only |
| **S3** | 11 topics (3.1–3.2) | No power calculations; `electric_current` has no \(V=IR\); qualitative meters only |

After each wave: full `PB_TESTING=1 python scripts/run_smoke_tests.py` plus a manual Practice-home pass (once the gate is open) on at least one sensitive topic and one S3 machines topic.

---

## Acceptance gate (track complete when)

- All 46 topics expose **exactly five** `standard` variants at each of foundational / intermediate / difficult.
- Those five match the recipe (MCQ, keyword, data/numeric, ordered, pick/set) and the canvas row where practical.
- Every generated payload **renders and grades** on Practice home and `POST /api/v1/problems/generate`.
- Lesson quizzes (10 questions, mixed bank) **unchanged** in behaviour; do not drop `correct_answer` / `correct_answer_raw` unless a stem is wrong.
- IBL pages remain practical-support-only (`IBL_PAGES` / `templates/eursc_science_ibl_*.html`) — **not** in the generator catalogue.
- **eursc excluded from QOTD.**
- Sensitive-topic scans pass (`DISCLOSE_RE` on 1.4 / 2.2 banks and templates).
- S3: no power; no \(V=IR\).
- Full smoke suite green.

---

## Per-slot checklist (Phases 1–2)

Work through this list for **each** topic×difficulty you curate.

### 1. Mode separation

- [ ] `variants_func(difficulty, "lesson")` still returns the **full** mixed bank (unchanged length and membership except for stem fixes).
- [ ] `variants_func(difficulty, "standard")` returns **exactly five** named callables.
- [ ] `variants_func(difficulty, "mcq")` still returns MCQs only.
- [ ] `generate(..., mode="standard")` never falls back to the lesson pool.
- [ ] Practice names are unique within the tier and stable across calls.

### 2. Recipe and canvas

- [ ] Slots 1–5 are MCQ, keyword, data/numeric, ordered, pick/set (one of each).
- [ ] Stem intent matches the canvas row for that `syllabus_ref`, unless a documented syllabus override applies (e.g. 1.3.1 kinematics).
- [ ] Terminology matches the improved lesson (glosses, transform vs transfer, conventional current, accuracy vs precision).
- [ ] Prefer existing bank items; rewrite only when the stem is wrong, unsafe, or the wrong format family.

### 3. Grading payload

- [ ] MCQ: `options` + `correct_answer` letter; server grades from session, never a client `correct` flag.
- [ ] Typed: `correct_answer_raw` + `answer_type` present and checker-compatible.
- [ ] Do not drop keys on a still-valid stem.
- [ ] No new answer types invented for this subject.

### 4. Safeguarding

**Highest scrutiny:** `1.4.*`, `2.2.*`, also `2.3.7` interoception, `1.2.7` nutrition, `1.2.8` healthy meal.

- [ ] Fictional third parties or **public/aggregate** data only.
- [ ] No first-person disclosure (`DISCLOSE_RE`: `your diet`, `have you ever`, `your body`, `are you attracted`, `do you smoke`, `are you addicted`, `how do you feel`, `map your body`, …).
- [ ] Banks assess knowledge and healthy decision-making, not identity or behaviour.

### 5. S3 machines

- [ ] **3.1.1** may use \(W=Fd\); **no power** (\(P=W/t\) or equivalent).
- [ ] **3.1.4** qualitative current/voltage and circuit diagnosis only; **no \(V=IR\)**, no resistance calculations.

### 6. Out of scope

- [ ] IBL templates not registered as generator topics.
- [ ] `eursc` not added to QOTD.
- [ ] Lesson checkpoint counts / `SYLLABUS_MODULES` sections unchanged unless the user approves a manifest change.

---

## Hard constraints (every phase)

1. Lesson banks (`mode=lesson`) and 10-question lesson quizzes must keep working.
2. Exactly five `standard` slots per topic per difficulty (690 curated entries — mostly select/rewrite).
3. Slot recipe: (1) MCQ (2) keyword (3) data/numeric (4) ordered (5) pick/set — canvas rows where practical.
4. IBL pages stay outside the generator.
5. Keep eursc out of QOTD.
6. Puberty (1.4) and Health (2.2): fictional/public/aggregate only — no disclosure prompts.
7. S3 Machines: no power calculations; `electric_current` has no \(V=IR\).
8. Practice home is open for `eursc/science` via `GENERATOR_LAUNCH_PATHS`. Do not add A-Level / Physics / MYP without an explicit cue. Do not add eursc to QOTD.
9. Commit only when the user asks.

---

## Related paths

| Area | Path |
|------|------|
| Canvas plan | `eursc-generator-question-plan.canvas.tsx` |
| Practice helpers | `generators/eursc/science_shared.py` |
| Unit banks | `generators/eursc/s1_*.py` … `s3_*.py` |
| Launch gate | `app.py` — `GENERATOR_LAUNCH_PATHS`, `_normalize_generator_scope` |
| Variant / mode | `generators/shared/variant_utils.py` — `normalize_mode`, queues |
| Lesson quiz | `generators/shared/lesson_quiz.py` |
| QOTD exclusion | `models/qotd.py` — `list_mcq_topic_paths` |
| ES10 / disclose | `scripts/test_es10_whole_suite_smoke.py` |
| Practice-slot smoke | `scripts/test_es_practice_slots_smoke.py` |
| Full smoke | `scripts/run_smoke_tests.py` (`PB_TESTING=1`) |
