# European School Integrated Science advanced-question contract

**Scope:** `eursc/science` advanced Practice questions only  
**Sources:** `docs/EUROPEAN_SCHOOL_SCIENCE.md` and the `SYLLABUS_MODULES` manifest in `generators/eursc/science_shared.py`  
**Status:** contract + mode plumbing shipped; **operational pilot (scope A) signed 2026-09-02**. **S1 Batch 2.1 (Unit 1.1) enabled 2026-09-02.** Remaining S1 batches, S2–S3 waves, and the whole-matrix audit are not done. This document remains the authoring contract; it does not by itself enable remaining matrix cells.

This contract adds two possible advanced question modes without changing the
curriculum, lesson banks, lesson quizzes, or existing scoring contract:

- **`multi_step` (MS):** a linked scientific calculation, data interpretation,
  classification, sequence, or evidence argument.
- **`situational_multi_step` (SMS):** the same linked structure inside one
  fictional, public-data, laboratory, fieldwork, or aggregate scenario.

Support is deliberately selective. A topic is enabled only where 2–4 dependent
parts test its manifest objectives authentically. A compact recall topic does
not gain an advanced mode merely to make the matrix look complete.

## Capability legend

- **F** = `foundational`
- **I** = `intermediate`
- **D** = `difficult`
- A list such as **I, D** means the mode is supported only at those tiers.
- **—** means unsupported; the cell gives the curriculum or safeguarding
  reason.

“Supported” is an authoring commitment, not permission for runtime fallback.
Every supported topic/tier/mode combination must satisfy the blueprint and pack
requirements below before it can be registered.

## Capability matrix

### S1

| Ref | Slug | `multi_step` | `situational_multi_step` | Practical boundary |
|---|---|---|---|---|
| 1.1.1 | `what_is_science` | I, D | F, I, D | Link claim, evidence, repeatability, and critique; F MS alone would mostly repackage recall. |
| 1.1.2 | `measurement` | F, I, D | F, I, D | Read, convert, compare, and diagnose measurements from one coherent dataset. |
| 1.1.3 | `science_lab` | F, I, D | F, I, D | Apparatus, variables, safety, method, and error reduction naturally form dependent parts. |
| 1.2.1 | `food_formulas` | I, D | F, I, D | Use food-source evidence to classify nutrients and justify a conclusion; F MS would be disconnected naming. |
| 1.2.2 | `water_substances` | F, I, D | F, I, D | Link particle state, phase change, mixture, and suitable separation method. |
| 1.2.3 | `cooking_heat` | F, I, D | F, I, D | Follow heat transfer through a cooking process, then predict denaturing or browning. |
| 1.2.4 | `cooking_acid` | I, D | F, I, D | Interpret pH/indicator evidence before selecting an acid-cooking or preservation explanation; F MS would be forced. |
| 1.2.5 | `cooking_salt` | F, I, D | F, I, D | Concentration, evaporation, crystallisation, and preservation provide a linked chain. |
| 1.2.6 | `cooking_fermentation` | F, I, D | F, I, D | Conditions determine microorganism activity and products in one controlled process. |
| 1.2.7 | `nutrition` | F, I, D | F, I, D | Labels, kJ/kcal, ingredients, deficiencies, and claim critique support linked public-data questions. |
| 1.2.8 | `healthy_meal_project` | F, I, D | F, I, D | Grade readiness, hygiene, repeatable method, evidence, and reflection—not the physical meal. |
| 1.3.1 | `movement` | F, I, D | F, I, D | Distance/time readings feed speed, conversion, and graph conclusions. |
| 1.3.2 | `forces_sport` | F, I, D | F, I, D | One fictional sporting event can link force effects, friction, stability, and equilibrium. |
| 1.3.3 | `breathing` | I, D | F, I, D | Use aggregate pulse/gas evidence to connect breathing, circulation, and muscle work; F MS would over-compress several systems. |
| 1.3.4 | `sport_health` | I, D | F, I, D | Apply anatomy and protection evidence to fictional cases; no pupil fitness, injury, drug, or hydration disclosure. |
| 1.4.1 | `puberty_maturity` | I, D | F, I, D | Link hormones, typical changes, timing, and variation only through clinical third-person or aggregate cases. |
| 1.4.2 | `reproductive_anatomy` | I, D | — Clinical labelling and cycle/fertilisation sequences are sufficient; a personal-style situation adds privacy risk without a curriculum gain. |
| 1.4.3 | `pregnancy_sexual_health` | I, D | F, I, D | Use fictional clinical and healthy-decision scenarios; never ask about identity, relationships, behaviour, symptoms, or experience. |

### S2

| Ref | Slug | `multi_step` | `situational_multi_step` | Practical boundary |
|---|---|---|---|---|
| 2.1.1 | `solar_system` | F, I, D | F, I, D | Positions, scale, models, and evidence can be linked within one observation set. |
| 2.1.2 | `light_telescopes` | F, I, D | F, I, D | A single ray/space-observation variant can drive shadow, reflection, refraction, lens, or scale parts. |
| 2.1.3 | `life_earth_elsewhere` | I, D | F, I, D | Weigh requirements, evidence quality, and travel/habitation constraints; F MS would manufacture a calculation not in scope. |
| 2.1.4 | `atoms_molecules` | F, I, D | F, I, D | Particle diagrams feed element/molecule classification, rearrangement, word equations, and conservation. |
| 2.2.1 | `healthy_living` | I, D | F, I, D | Use fictional or aggregate public-health evidence; no body, diet, mental-health, relationship, or screen-time survey. |
| 2.2.2 | `infectious_disease` | F, I, D | F, I, D | Transmission chains and outbreak tables naturally support linked inference and intervention selection. |
| 2.2.3 | `noninfectious_disease` | I, D | F, I, D | Classify public clinical/environmental evidence and then select support; no diagnosis or classmate ranking. |
| 2.2.4 | `dependence_addiction` | I, D | F, I, D | Fictional cases may link risk factors, consequences, evidence, and support routes; no confession or behaviour inventory. |
| 2.2.5 | `tobacco` | I, D | F, I, D | Critique public mortality/marketing/vaping evidence and choose prevention reasoning; no use disclosure. |
| 2.3.1 | `vision` | I, D | F, I, D | Diagram evidence may feed focusing, accommodation, stereo depth, and interpretation; F MS would mostly chain labels. |
| 2.3.2 | `hearing` | I, D | F, I, D | Link vibration/medium evidence to anatomy, localisation, or aid function; never collect hearing-test data. |
| 2.3.3 | `touch` | I, D | I, D | Advanced tasks may use supplied aggregate two-point data; F SMS is excluded because a personal test is neither needed nor appropriate. |
| 2.3.4 | `smell` | — The compact objectives are qualitative and do not provide an authentic context-free dependent chain. | I, D | Use supplied public examples to move from chemical signal to receptor/category and context-dependent interpretation; no smell diary. |
| 2.3.5 | `taste` | I, D | I, D | Link supplied controlled-test evidence to taste–smell or colour/context conclusions; no forced tasting or private menu. |
| 2.3.6 | `proprioception_balance` | I, D | I, D | Link canal/vision/position evidence in a fictional model; no spinning task, symptom prompt, or dizziness record. |
| 2.3.7 | `interoception` | — A context-free chain would encourage artificial inference about internal states. | I, D | Only fictional cases may connect an ambiguous signal, alternative interpretations, and an appropriate support signpost; no live mood/body survey. |
| 2.3.8 | `nonhuman_senses` | F, I, D | F, I, D | Match a supplied signal to receptor/adaptation, infer function, then compare with a technology sensor. |

### S3

| Ref | Slug | `multi_step` | `situational_multi_step` | Practical boundary |
|---|---|---|---|---|
| 3.1.1 | `force_work_machines` | F, I, D | F, I, D | Link machine diagram, force–distance trade-off, and \(W=Fd\); **never calculate power**. |
| 3.1.2 | `energy` | F, I, D | F, I, D | Sankey values feed transformations, useful/wasted amounts, conservation, and public-impact comparison; no private usage diary. |
| 3.1.3 | `electrostatics` | F, I, D | F, I, D | A charge sequence can link transfer/induction, attraction/repulsion, grounding, and discharge safety. |
| 3.1.4 | `electric_current` | F, I, D | F, I, D | Diagnose one series/parallel circuit qualitatively from topology, meters, effects, and safety; **never use \(V=IR\)**. |
| 3.1.5 | `magnetism` | I, D | F, I, D | Link poles, materials, fields, electromagnets, and compass evidence; F MS alone would mostly concatenate recognition. |
| 3.1.6 | `robotics_project` | F, I, D | F, I, D | Grade requirements, component choice, sense–decide–act logic, test evidence, and iteration—not a physical robot or private code upload. |
| 3.2.1 | `food_environment` | F, I, D | F, I, D | Public lifecycle/footprint data can feed ordering, impact comparison, and sustainable-choice justification; no household diary. |
| 3.2.2 | `ecosystems_cycles` | F, I, D | F, I, D | Cycle/web evidence links stores, trophic roles, matter, energy, photosynthesis, and respiration. |
| 3.2.3 | `ecosystem_characteristics` | F, I, D | F, I, D | Supplied field data can link factors, measurement, survey method, organism activity, and model critique. |
| 3.2.4 | `classification_biodiversity` | F, I, D | F, I, D | Follow a key, justify a grouping, place a taxon, and infer biodiversity implications from public evidence. |
| 3.2.5 | `ecology_field_project` | F, I, D | F, I, D | Grade question, risk, sampling, records, analysis, and reflection—not fieldwork completion or a home-garden upload. |

## Authoring contract

### Linked graded parts

1. Each question has **2–4 graded parts**.
2. Every later part must genuinely depend on an earlier result, classification,
   selected evidence, diagram reading, or established scenario fact. Repeating
   the stem, asking unrelated recall, or merely increasing wording length does
   not count as dependency.
3. Dependency must survive answer review. For example, part 2 may use the
   measurement calculated in part 1, and part 3 may use both that value and a
   method flaw identified in part 2.
4. Use **existing graders only**: MCQ; `proof_steps` order; `proof_steps`
   pick/set; `number`; `number_estimate`; `number_pair`; `number_fields` with
   existing `number`, `mcq`, `order`, or `pick` fields; `keyword`; or tightly
   constrained `text`. Diagrams and charts are presentation, not new graders.
   There is no new matching grader.
5. One mark corresponds to one meaningful graded part. A two-part question has
   two available marks; a four-part question has four. Do not split a trivial
   response into fragments to inflate marks.
6. Preserve the platform's existing **overall question scoring**. Part marks
   populate the existing per-question `score`/`score_total` shape; they do not
   create weighted topics, a new gradebook, or a second progress scale.

### Blueprints and curated packs

Before a matrix cell is enabled, that exact
`topic × tier × mode` combination must provide:

- at least **three explicitly named blueprints**, each representing a genuinely
  different dependency graph or evidence form; and
- at least **three explicitly named curated packs**, each binding one blueprint
  to a reviewed family of same-context variants.

Names must be stable and auditable, for example:

```text
measurement__intermediate__multi_step__scale_convert_compare
measurement__intermediate__multi_step__repeat_error_diagnose
measurement__intermediate__multi_step__precision_summary_conclude

measurement__intermediate__multi_step__pack_lab_bench
measurement__intermediate__multi_step__pack_field_lengths
measurement__intermediate__multi_step__pack_temperature_series
```

A pack is not “three random questions.” It is a curated set whose quantities,
diagram, evidence, distractors, units, and dependency path have been reviewed
together. Registration must fail closed if a supported cell has fewer than
three blueprints or fewer than three packs.

### Same-variant randomisation

- Randomise the scenario **once**, then derive every part from that same variant
  payload. Parts must not independently choose people, apparatus, datasets,
  organisms, units, circuit layouts, or numerical values.
- Store stable intermediate values and evidence identifiers in the payload so
  later parts refer to exactly what earlier parts established.
- A retry may choose another curated variant. Within one rendered attempt,
  values and evidence remain coherent.
- Distractor order may vary only when the stored correct-answer mapping varies
  with it. Randomisation must never change the science claim or safeguarding
  classification.

### Safeguarding and syllabus boundaries

- Use third-person fictional cases, published/public data, or aggregates.
  Health, puberty, sexuality, senses, dependence, diet, disability, households,
  and environmental choices must never become profiles of a pupil or family.
- Do not request personal disclosure, live symptoms, body measurements, mood,
  diagnosis, medication, sexual identity or behaviour, relationship history,
  substance use, diet logs, household bills, photographs, private code, or
  location-linked field samples.
- Do not rank classmates, bodies, homes, identities, abilities, health, or
  behaviours. Signpost trusted-adult or qualified support where the manifest
  requires it; the generator does not diagnose.
- S3 force/work questions may use \(W=Fd\), but **must not introduce power
  calculations**.
- S3 circuit questions are qualitative and **must not introduce \(V=IR\)** or
  resistance calculations.
- The physical product or practical performance in meal, robot, and ecology
  projects is not auto-graded. Only readiness, method, safety, supplied data,
  analysis, iteration, and reflection may be graded.

### Isolation from existing surfaces

- **QOTD remains unchanged.** `eursc` stays excluded; advanced content must not
  leak into site-wide daily questions.
- **Lesson pools remain unchanged.** Do not add, remove, rename, reweight, or
  repurpose lesson-bank variants to satisfy this contract.
- Existing lesson quizzes, ten-question scoring, mastery, retry behaviour,
  standard five-slot Practice selection, and topic registration remain
  unchanged unless a later implementation plan explicitly scopes those changes.
- Advanced blueprints and packs live in their own mode-specific registry. An
  unsupported or incomplete cell returns unavailable; it never falls back to a
  lesson-pool question or a different tier.

## Rollout waves

Each wave is content-gated. A topic is enabled only after every intended cell in
that wave has its three blueprints, three packs, contract tests, curriculum
review, and safeguarding review where relevant. Partial authoring stays hidden.

### Pilot

Enable a deliberately small cross-curriculum sample:

1. `measurement` — numeric/data dependencies and unit conversion;
2. `infectious_disease` — ordering, outbreak evidence, interventions, and
   health-data safeguards;
3. `energy` — diagram/data dependencies, conservation, and aggregate/public
   evidence.

Pilot exit requires deterministic same-variant tests, grader compatibility,
per-part/overall score tests, unavailable-cell fail-closed tests, mobile and
accessibility review, and confirmation that QOTD and lesson-pool snapshots are
unchanged.

#### Pilot sign-off (2026-09-02)

| Field | Record |
|---|---|
| **Date** | 2026-09-02 |
| **Signed as** | **Scope A — operational sample.** Not contract-complete (scope B). |
| **Enabled cells** | `measurement` MS (F/I/D); `infectious_disease` SMS (F/I/D); `energy` SMS (F/I/D); extra `movement` MS (F/I/D) as an engineering sample. |
| **Still fail-closed at sign-off** | `infectious_disease` MS; `energy` MS; every other matrix cell. **Update 2026-09-02:** S1 Batches 2.1–2.3 enabled Units 1.1–1.3 cells per matrix (see S1 wave). |
| **Out of this sign-off** | Filling the other mode for the pilot slugs; S1/S2/S3 waves; per-part class-work score UI; lesson banks / QOTD / standard five-slot recipe. |
| **Exit smokes** | `scripts/test_es_advanced_pilot_exit_smoke.py` (same-variant pin, mixed `number_fields` + partial credit, fail-closed matrix, QOTD/lesson snapshots, safeguarding, HTML a11y). Topic smokes: `test_es_measurement_multi_step_smoke.py`, `test_es_movement_multi_step_smoke.py`, `test_es_infectious_disease_sms_smoke.py`, `test_es_energy_sms_smoke.py`. Plumbing: `test_es_advanced_mode_plumbing.py`. Downstream: `test_es_advanced_downstream_smoke.py`. Isolation: `test_es_practice_slots_smoke.py`. Run with `PB_TESTING=1`. |
| **Manual / a11y** | Automated HTML checks in the pilot-exit smoke (Practice mode picker, teacher set-work filter, class-work collect-only banks, Quick Test field Check). Remaining visual click-through: restart the local Flask process so `data-modes` matches this tree, then spot-check Practice home (labelled Mode control, viewport-fit). |
| **QA owner** | Automated gate: the smokes above. Remaining live-server visual pass: **David**. |
| **Code on branch** | Plumbing `a4cf79d`; pilot content + downstream `0e4d83a` on `cursor/cloud-agent-1787823476595-0do93`. At sign-off, QA hardening and `test_es_advanced_pilot_exit_smoke.py` were still uncommitted — land those before treating the branch as merged to `main`. |
| **Track status** | Pilot **signed** (scope A). The advanced-question **track** is **not complete** until the post-S3 whole-matrix audit. S1 wave and **S2 Batch 3.1 (Unit 2.1 Astronomy)** are in this tree; later S2 batches wait on safeguarding gates. |

### S1 wave

Enable the supported cells for all S1 slugs, including the pilot-independent
Science Lab, Food, Sports, and Puberty topics. Review Unit 1.4 and health-related
sport/nutrition scenarios as a dedicated safeguarding gate. Verify that
`reproductive_anatomy` SMS remains unavailable and that no force/power or
electricity scope is imported early.

#### Batch 2.1 — Unit 1.1 (2026-09-02)

| Field | Record |
|---|---|
| **Topics** | `what_is_science`, `measurement` SMS (Option A completion), `science_lab` |
| **Enabled cells** | `what_is_science` MS (I/D only) and SMS (F/I/D); `measurement` SMS (F/I/D); `science_lab` MS and SMS (F/I/D). Foundational `what_is_science` MS stays **—**. |
| **Gate** | Method/evidence stems; third-person fictional/public data; `DISCLOSE_RE` clean; lesson/standard pools unchanged. |
| **Smokes** | `scripts/test_es_s1_unit11_advanced_smoke.py`, plus updated `test_es_measurement_multi_step_smoke.py`, `test_es_advanced_pilot_exit_smoke.py`, `test_es_advanced_mode_plumbing.py`. |
| **Next** | Batch 2.2 Unit 1.2 (`food_formulas` … `healthy_meal_project`). Do not start until this batch's smokes are green. |

#### Batch 2.2 — Unit 1.2 Food (2026-09-02)

| Field | Record |
|---|---|
| **Topics** | `food_formulas`, `water_substances`, `cooking_heat`, `cooking_acid`, `cooking_salt`, `cooking_fermentation`, `nutrition`, `healthy_meal_project` |
| **Enabled cells** | All eight topics: MS and SMS per matrix. Foundational MS stays **—** for `food_formulas` and `cooking_acid` only. |
| **Gate** | Third-person fictional/public food-lab and canteen scenarios; no personal diet or allergy disclosure; `DISCLOSE_RE` clean; lesson/standard pools unchanged. |
| **Smokes** | `scripts/test_es_s1_unit12_food_advanced_smoke.py`, plus updated `test_es_advanced_pilot_exit_smoke.py`, `test_es_advanced_mode_plumbing.py`, and `test_es3_food_smoke.py` regression. |
| **Next** | Batch 2.3 Unit 1.3 Sports (`forces_sport` … `sport_health`). Do not start until this batch's smokes are green. |

#### Batch 2.3 — Unit 1.3 Sports (2026-09-02)

| Field | Record |
|---|---|
| **Topics** | `movement` SMS (MS already pilot), `forces_sport`, `breathing`, `sport_health` |
| **Enabled cells** | All four topics: MS and SMS per matrix. Foundational MS stays **—** for `breathing` and `sport_health` only. `movement` SMS completes the pilot slug. |
| **Gate** | Third-person fictional sporting/public aggregate data; no personal fitness, injury, drug, or hydration disclosure; `DISCLOSE_RE` clean; lesson/standard pools unchanged. |
| **Smokes** | `scripts/test_es_s1_unit13_sports_advanced_smoke.py`, updated `test_es_movement_multi_step_smoke.py`, `test_es_advanced_pilot_exit_smoke.py`, `test_es4_sports_puberty_smoke.py` regression. |
| **Next** | Batch 2.4 Unit 1.4 Puberty (`puberty_maturity` … `pregnancy_sexual_health`). Dedicated safeguarding gate before authoring. |

#### Batch 2.4 — Unit 1.4 Puberty (2026-09-02)

| Field | Record |
|---|---|
| **Topics** | `puberty_maturity`, `reproductive_anatomy`, `pregnancy_sexual_health` |
| **Enabled cells** | `puberty_maturity` and `pregnancy_sexual_health`: MS (I/D) + SMS (F/I/D). `reproductive_anatomy`: MS (I/D) only. Foundational MS stays **—** for all three. **`reproductive_anatomy` SMS stays —** (matrix exclusion). |
| **Safeguarding gate** | Third-person fictional clinical cases, textbook aggregates, public leaflets only; `DISCLOSE_RE` clean; no personal puberty/sexual-health disclosure; signpost teacher/health professional; lesson/standard pools unchanged. |
| **Smokes** | `scripts/test_es_s1_unit14_puberty_advanced_smoke.py`, updated `test_es_advanced_pilot_exit_smoke.py`, `test_es_advanced_mode_plumbing.py`, `test_es4_sports_puberty_smoke.py` regression. |
| **Next** | **S1 wave complete** for supported cells — proceed to S2 wave (safeguarding gates per unit). Whole-matrix audit remains after S3. |

### S2 wave

Enable the supported cells for all S2 slugs. Treat Unit 2.2 and the human-senses
topics as a dedicated safeguarding gate. Verify the intentional exclusions and
tier limits for `smell`, `touch`, `taste`, `proprioception_balance`, and
`interoception`; unsupported cells must not be filled with personal experiments.

#### Batch 3.1 — Unit 2.1 Astronomy (2026-09-02)

| Field | Record |
|---|---|
| **Topics** | `solar_system`, `light_telescopes`, `life_earth_elsewhere`, `atoms_molecules` |
| **Enabled cells** | All four topics per matrix. Foundational MS stays **—** for `life_earth_elsewhere` only. |
| **Gate** | Fictional planetarium/telescope/lab scenarios; public evidence and scale models; no personal disclosure. |
| **Smokes** | `scripts/test_es_s2_unit21_universe_advanced_smoke.py`, updated `test_es_advanced_pilot_exit_smoke.py`, `test_es_advanced_mode_plumbing.py`, `test_es5_universe_smoke.py` regression. |
| **Next** | Batch 3.2 Unit 2.2 Health (`healthy_living` … `tobacco`). Dedicated safeguarding gate before authoring. |

### S3 wave

Enable the supported cells for all S3 slugs. Add explicit content tests rejecting
power calculations in `force_work_machines` and \(V=IR\)/resistance calculations
in `electric_current`. Confirm project questions grade planning and evidence
only, and confirm environmental scenarios use supplied public/aggregate data
rather than household or location-linked disclosure.

After S3, run a whole-matrix audit: all 46 manifest slugs appear exactly once,
every enabled cell meets blueprint/pack minimums, every exclusion fails closed,
all graders are pre-existing, and QOTD and lesson-pool snapshots remain
unchanged.
