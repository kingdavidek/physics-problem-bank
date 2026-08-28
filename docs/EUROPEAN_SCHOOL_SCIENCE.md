# European School Integrated Science S1–S3 — full lesson-suite plan

**Repo path:** `docs/EUROPEAN_SCHOOL_SCIENCE.md` (from repository root)  
**ES0 agent entry point:** `docs/ES0_HANDOFF.md` — platform enablement only; run `git checkout main && git pull` first  
**Last updated:** 2026-08-28
**Status:** **ES10 shipped** — whole-suite QA complete. S1–S3 complete (46 syllabus modules, six IBL tracks). Curriculum track closed. QOTD still excludes `eursc` (clinical 1.4 / 2.2 / interoception must not appear as site-wide daily questions).
**Official source:** Schola Europaea, *Integrated Science Syllabus S1–S3*, ref **2018-12-D-6-en-2**, approved 7–8 February 2019 and phased into force for S1–S3 from 2019–2021. [Official PDF](https://www.eursc.eu/Syllabuses/2018-12-D-6-en-2.pdf)
**Platform question contract:** `docs/API.md` §Problems and `docs/COMPLEX_MECHANISMS.md` §1
**Decisions locked:** full curriculum-faithful puberty/sexuality coverage; launch **lessons + lesson quizzes**, while the main Practice generator remains GCSE maths/CS only.

This adds level `eursc`, subject `science`, covering the compulsory four-period-per-week Observation Cycle course. Biology, chemistry and physics remain integrated around the syllabus themes.

---

## 1. Corrections to the first draft

The official detailed tables do **not** support a fixed “6–7 sections and 6–7 checks per lesson” rule. Breadth varies sharply:

- compact modules need 4–5 teaching sections;
- broad practical/data modules need 8–10;
- project modules need 4–6 project phases and rubric checkpoints;
- every normal lesson still receives a 10-question end quiz so the current ninja/mastery model remains coherent.

The first draft also merged unrelated or very broad official subsections. This revision maps **each of the 46 numbered syllabus subsections to its own module**. Three capstones are first-class project modules rather than footnotes.

Corrections from the official headings/content:

- 1.2.2 is **Water and Other Substances**, not merely “water and heating”.
- 1.3.3 is **Breathing**; it includes respiration, circulation, pulse, pressure and buoyancy.
- 3.1.1 is **Force and Work**; 3.1.2 is **Energy**. Power calculations are not claimed.
- 3.1.4 treats current and voltage qualitatively. \(V=IR\) and resistance calculations are not claimed.
- 3.2.1 is **Human Nutrition and Its Effects on Our Environment**.
- Biodiversity and sustainable development sit mainly under 3.2.4 Classification.
- Section 2.3 requires at least three senses in depth. This suite offers all eight as a comprehensive resource, not as a claim that every school must teach all eight equally.
- Capstones are not fully auto-gradable, but planning, safety, method, data, iteration and presentation can receive rubric checkpoints.

---

## 2. Question formats: what exists and where it will be used

The platform already has richer grading than MCQ. The canonical list is in `docs/API.md`; implementations are in `generators/shared/answer_checkers.py` and `templates/partials/free_response_inline.html`.

| Format | Existing token | Science use |
|--------|----------------|-------------|
| Single best answer | MCQ | misconceptions, diagrams, safety scenarios |
| Ordered steps | `proof_steps`, order flag `1` | scientific method, heat/food processes, disease chains, life cycles |
| Select a set / pick N | `proof_steps`, order flag `0` or `pick` | classify variables, identify controls, choose valid evidence |
| Numeric | `number`, `number_estimate`, `number_pair` | measurement, speed, scales, work, energy, graph/data work |
| Multi-part structured response | `number_fields` with per-field `number`, `mcq`, `order`, `pick` | tables, linked calculations, investigation plans |
| Keyword | `keyword` | units, named structures and processes |
| Short text | `text` | tightly constrained scientific vocabulary; use sparingly |
| Diagram/data interpretation | existing SVG/chart + one of the above graders | circuits, optics, food webs, graphs |

There is no dedicated matching grader. Matching tasks use a pick/set bank or a structured multi-field question; do not invent a new type unless testing shows these are inadequate.

### Current surface limitation

Native ordering already works in the generator and Quick Test, but:

- lesson inline progress currently listens only for `.mcq-inline`;
- the current lesson quiz builder and runner accept MCQ letters only.

Therefore **mixed-format lesson quizzes are an enablement task**, not merely content authoring. Inline lesson checkpoints remain lightweight MCQs in the first release; rich ordering/pick/numeric questions appear in each end-of-lesson quiz. A later enhancement can make inline lesson checkpoints mixed-format without blocking this curriculum.

### Mixed quiz design

Generalise the current MCQ-only lesson quiz into a session-bound mixed quiz:

1. Rename/generalise `build_lesson_mcq_quiz()` in `generators/shared/lesson_quiz.py` to build 10 unique problems from a topic’s **lesson bank**.
2. Permit both:
   - `{options, correct_answer}` for MCQ; and
   - `{correct_answer_raw, answer_type, ...}` for existing typed questions.
3. Reuse the rendering branch in `templates/quicktest_question.html`: options for MCQ, otherwise `partials/free_response_inline.html`.
4. Grade typed answers server-side against the problem saved in the lesson-quiz session; never trust a client-supplied answer key.
5. Store per-question `score` / `score_total`, while preserving the quiz’s overall ten-question score for existing progress, ninja and retry behaviour.
6. Keep the web and `/api/v1/lesson-quiz/*` flows equivalent.

Target mix varies by module, but a typical conceptual quiz is 4 MCQ + 2 pick/set + 2 ordering + 1 diagram/data + 1 keyword. A quantitative quiz uses 3–4 numeric/data questions. Project quizzes assess readiness, method and safety; the practical product itself uses a rubric.

---

## 3. Full curriculum map: 46 modules with variable depth

`order` runs 1–46, but every entry also carries `year`, `unit_code` and `unit_name`. `/topics` groups the long path by S1/S2/S3 and the nine official themes.

**Legend:** `S` = teaching sections, `C` = inline progress checkpoints (MCQ in v1), `Q` = recommended end-quiz formats. Every normal module has a 10-question mixed quiz.

### S1 — 18 modules

| # | Ref / slug | Lesson | Scope | S / C | Q emphasis |
|---|------------|--------|-------|-------|------------|
| 1 | 1.1.1 `what_is_science` | What Is Science? | reliable knowledge, reproducibility, evidence, peer critique, provisional explanations | 5 / 4 | MCQ, pick, evidence order |
| 2 | 1.1.2 `measurement` | Measurement and SI Units | universal units, SI prefixes, conversion, calibration, accuracy/precision/error | 6 / 7 | numeric, estimate, data |
| 3 | 1.1.3 `science_lab` | The Science Laboratory | instruments, safety, technical drawings, controlled investigations, reducing error | 8 / 7 | diagram, pick, order |
| 4 | 1.2.1 `food_formulas` | Food Formulas: Molecules of Life | water, proteins, fats, carbohydrates, food sources, plant/animal nutrition | 5 / 5 | classify, pick, MCQ |
| 5 | 1.2.2 `water_substances` | Water and Other Substances | states, phase change, mixtures, separation, non-additive volume | 6 / 6 | diagrams, order, data |
| 6 | 1.2.3 `cooking_heat` | Basic Cooking: Heat | conduction, convection, radiation, cooking methods, denaturing and browning | 6 / 6 | process order, prediction |
| 7 | 1.2.4 `cooking_acid` | Basic Cooking: Acid | sensory acidity, pH/indicators, acid cooking and preservation | 5 / 4 | pH/data, pick |
| 8 | 1.2.5 `cooking_salt` | Basic Cooking: Salt | inorganic mineral, solutions, concentration, crystallisation, preservation | 5 / 5 | numeric, order, MCQ |
| 9 | 1.2.6 `cooking_fermentation` | Basic Cooking: Fermentation | microorganisms, yeast/alcoholic and bacterial/lactic fermentation, controlled spoilage | 6 / 5 | order, matching via pick |
| 10 | 1.2.7 `nutrition` | Nutrition and Food Information | balanced diet, deficiencies, allergy/intolerance, obesity/eating disorders, labels, kJ/kcal, additives, marketing | 10 / 9 | label maths, claim critique |
| 11 | 1.2.8 `healthy_meal_project` | Project: A Healthy Meal | plan, safety, preparation, evidence-based menu, presentation and reflection | 4 phases / 4 rubric | readiness/safety quiz + rubric |
| 12 | 1.3.1 `movement` | Movement | distance/time measurement, average speed, \(v=d/t\), unit conversion, distance–time graphs | 6 / 7 | numeric, graph/data |
| 13 | 1.3.2 `forces_sport` | Forces in Sport | effects, interaction, newtons, friction, mass/weight, centre of gravity, equilibrium | 8 / 7 | numeric, diagrams, classify |
| 14 | 1.3.3 `breathing` | Breathing, Respiration and Circulation | air gases, inhaled/exhaled air, respiration, pulse, heart/blood/oxygen, pressure/buoyancy | 8 / 7 | anatomy, data, order |
| 15 | 1.3.4 `sport_health` | Sport and Health | skeleton, joints, antagonistic muscles, injury/infection/UV protection, drugs, sweating, water/minerals | 7 / 6 | labels, scenarios, pick |
| 16 | 1.4.1 `puberty_maturity` | Puberty and Sexual Maturity | physical/emotional changes, hormones, variation and maturity | 5 / 4 | clinical MCQ, sequence |
| 17 | 1.4.2 `reproductive_anatomy` | Human Reproductive Anatomy | reproductive/urinary anatomy, gametes, menstrual cycle, fertilisation | 6 / 5 | labels, ordering, keyword |
| 18 | 1.4.3 `pregnancy_sexual_health` | Pregnancy and Sexual Health | intercourse, pregnancy, fetal development, birth, contraception, STIs, identity/orientation, media, consent, communication and healthy relationships | 8 / 7 | clinical scenarios, sequence, misconception correction |

### S2 — 17 modules

| # | Ref / slug | Lesson | Scope | S / C | Q emphasis |
|---|------------|--------|-------|-------|------------|
| 19 | 2.1.1 `solar_system` | The Solar System | rotation/revolution, seasons, Moon, planets/bodies, scale, universe age/expansion, historical models | 9 / 8 | scale numeric, order, models |
| 20 | 2.1.2 `light_telescopes` | Light and Telescopes | propagation/speed, light-year, shadows, phases/eclipses, reflection/refraction, colour, lenses, instruments | 9 / 8 | ray diagrams, numeric/data |
| 21 | 2.1.3 `life_earth_elsewhere` | Life on Earth and Elsewhere | requirements for life, early Earth/LUCA, extraterrestrial life, travel/habitation constraints | 5 / 4 | evidence pick, constraints |
| 22 | 2.1.4 `atoms_molecules` | Atoms and Molecules | particle model, elements/atoms, symbols, molecules, reactions/rearrangement, word equations | 7 / 7 | particle diagrams, order |
| 23 | 2.2.1 `healthy_living` | Healthy Living | diet, physical/mental health, microbiome, relationships, screen-time management | 6 / 5 | case studies, data, pick |
| 24 | 2.2.2 `infectious_disease` | Infectious Disease and Immunity | bacteria/viruses, transmission, spread, immunity, vaccination, antibiotics/resistance, epidemiology, sanitation | 9 / 8 | chain order, outbreak data |
| 25 | 2.2.3 `noninfectious_disease` | Noninfectious and Environmental Disease | systemic/inherited, deficiency, pollution/occupation, mental illness, treatment/support | 7 / 6 | classify, sources, scenarios |
| 26 | 2.2.4 `dependence_addiction` | Pleasure, Dependence and Addiction | substance/behavioural dependence, risk, social context, consequences and support | 6 / 5 | scenarios, pick, evidence |
| 27 | 2.2.5 `tobacco` | Tobacco, Nicotine and Vaping | mortality/disease, addiction/initiation, industry influence, vaping uncertainty, prevention | 6 / 5 | advert critique, data |
| 28 | 2.3.1 `vision` | Vision | eye anatomy/optics, accommodation, near/far sight, stereo depth, brain processing/illusions | 7 / 6 | labels, ray diagrams |
| 29 | 2.3.2 `hearing` | Hearing | ear anatomy, vibration/medium, acoustics, stereo localisation, aids and illusions | 7 / 6 | labels, sequence, data |
| 30 | 2.3.3 `touch` | Touch | receptor types/density, temperature perception, mapping and controlled investigation | 5 / 4 | data, experiment design |
| 31 | 2.3.4 `smell` | Smell | receptor diversity, categorisation, context and perception | 4 / 4 | classify, evidence |
| 32 | 2.3.5 `taste` | Taste | five tastes, taste–smell interaction, colour/context effects | 4 / 4 | pick, controlled method |
| 33 | 2.3.6 `proprioception_balance` | Proprioception and Balance | body position, balance, semicircular canals | 5 / 4 | labels, sequence |
| 34 | 2.3.7 `interoception` | Interoception | sensing internal bodily states and interpreting wellbeing | 4 / 4 | scenarios, classify |
| 35 | 2.3.8 `nonhuman_senses` | Nonhuman Senses | UV/IR/polarised light, electromagnetic sensing, echolocation, infra/ultrasound, chemical senses, technology | 7 / 6 | adaptation matching/pick |

### S3 — 11 modules

| # | Ref / slug | Lesson | Scope | S / C | Q emphasis |
|---|------------|--------|-------|-------|------------|
| 36 | 3.1.1 `force_work_machines` | Force, Work and Simple Machines | force vectors/models, machine types, levers/torque, force–distance trade-off, \(W=Fd\), body levers | 8 / 8 | numeric, diagrams, models |
| 37 | 3.1.2 `energy` | Energy | forms, transformations/transfers/losses, Sankey diagrams, food/appliances, sources, impacts, conservation | 9 / 8 | chains, Sankey/data, compare |
| 38 | 3.1.3 `electrostatics` | Electrostatics | friction/contact, charges, transfer/induction, grounding, insulators, atomic model, sparks/lightning | 6 / 6 | charge diagrams, prediction |
| 39 | 3.1.4 `electric_current` | Electric Current and Circuits | series/parallel circuits, conventional current, electrons, conductors, effects, meters, qualitative current/voltage, safety | 9 / 8 | circuit diagnosis, diagrams; no \(V=IR\) |
| 40 | 3.1.5 `magnetism` | Magnetism and Electromagnetism | poles, materials/magnetisation, fields, electromagnets, Earth/compass/magnetotaxis | 8 / 7 | fields, classify, explain |
| 41 | 3.1.6 `robotics_project` | Project: Build a Simple Robot | requirements, machines, electromagnetism/electronics, programming, build/test/iterate, presentation | 5 phases / 5 rubric | readiness quiz + rubric |
| 42 | 3.2.1 `food_environment` | Human Nutrition and the Environment | atmosphere/GHGs, climate, land/biodiversity, food lifecycle/waste, footprints, sustainable choices | 8 / 7 | lifecycle order, carbon data |
| 43 | 3.2.2 `ecosystems_cycles` | Ecosystems, Matter and Energy | ecosystems, water/carbon cycles, nutrition, trophic roles, flows, webs/pyramids, photosynthesis/respiration | 9 / 8 | cycles, webs, word equations |
| 44 | 3.2.3 `ecosystem_characteristics` | Ecosystem Characteristics | trophic models, abiotic/biotic factors, measurement, activity and thermoregulation, surveys | 8 / 7 | field data, model critique |
| 45 | 3.2.4 `classification_biodiversity` | Classification and Biodiversity | life/species, grouping, dichotomous keys, taxonomy/Linnaeus, common descent, groups, biodiversity loss, sustainability | 9 / 8 | keys, taxonomy order, classify |
| 46 | 3.2.5 `ecology_field_project` | Project: An Ecological Field Study | question, risk, sampling, method, data, analysis, report, presentation/reflection | 6 phases / 6 rubric | readiness/data quiz + rubric |

### Curriculum-sensitive content rules

Unit 1.4 ships **completely and faithfully**, as requested:

- clinical, age-appropriate language;
- labelled educational diagrams only;
- no sensational imagery;
- no first-person prompts asking pupils to disclose health, sexuality, relationships or experiences;
- scenarios use fictional third parties;
- signpost teacher/qualified-health guidance where the curriculum concerns personal decisions;
- question banks assess knowledge and healthy decision-making, not personal identity or behaviour.

This avoids creating special-category profile data. Ordinary attempt records store answers to curriculum questions, never a pupil’s personal health information.

---

## 4. Inquiry-based learning and projects

The syllabus requires **at least two substantial inquiry-based learning units (≥10 class periods) per year**. An online lesson cannot claim to replace the practical work.

The suite includes planning, data and rubric support for six IBL tracks:

| Year | IBL 1 | IBL 2 |
|------|-------|-------|
| S1 | Measurement/controlled-investigation lab | Healthy meal or fermentation investigation |
| S2 | Light/telescope investigation | Disease-spread model or model-rocket investigation |
| S3 | Simple robot project | Ecological field study |

Each project support page provides:

1. brief and learning objectives;
2. planning template and variables;
3. safety/risk checklist;
4. data-table and graph guidance;
5. analysis/evaluation prompts;
6. teacher rubric for method, evidence, collaboration, communication and reflection.

Rubrics are printable/local UI in v1; no teacher grading database is introduced.

---

## 5. What the “hidden gates” mean

They are ordinary code allowlists left over from the initial GCSE launch—not access-control or payment gates.

| Gate | Current effect | Decision/change |
|------|----------------|-----------------|
| `app.py::_lesson_quiz_available` | Returns false for anything except GCSE maths/CS, even if a science quiz bank exists; the quiz URL then 404s and CTA is omitted | Replace curriculum-name check with capability detection and allow `eursc/science` mixed quizzes |
| `models/buddy.py::_quiz_available` | Duplicate check makes Zorp say no quiz is available and withholds quiz links | Remove duplication; call the shared capability helper |
| `GENERATOR_LAUNCH_GCSE_MATHS_CS` | Forces the **main Practice page** back to GCSE maths/CS | **Leave closed in v1**, per decision. Backend lesson banks still power lesson quizzes |
| `scripts/test_lesson_unify_smoke.py::FILENAME_RE` | CI treats `eursc_science_*.html` as an invalid filename and fails | Add `eursc`; this is only a test allowlist |

So lessons and quizzes can launch without exposing Integrated Science in the main Practice generator. The generator clamp is intentional for v1; the other three checks must change.

---

## 6. Registry and topic-path model

Add metadata without changing existing topic entries:

```python
"measurement": {
    "name": "Measurement and SI Units",
    "order": 2,
    "year": "s1",
    "unit_code": "1.1",
    "unit_name": "Science Lab",
    "syllabus_ref": "1.1.2",
    "func": eursc_science_measurement,
    "variants_func": eursc_science_measurement_variants,
}
```

Platform wiring:

| File | Change |
|------|--------|
| `topic_registry.py` | Add `TOPICS['eursc']['science']` with 46 entries and validate optional year/unit metadata |
| `app.py` | Add `eursc` level and `science` subject labels/orders; group topic cards by year/unit |
| `models/lesson_search.py`, `models/topic_status.py` | Add display labels |
| `templates/topics.html`, `static/js/u4.js` | European School filter; S1/S2/S3 and unit headings; science icon |
| `templates/partials/icon.html` | Original Integrated Science SVG icon |
| `scripts/test_lesson_unify_smoke.py` | Extend filename regex |
| `models/topic_status.py` | Generalise GCSE-only subject-completion badge helper |

No cross-year prerequisite locks. Within each unit, use prerequisites only when required for comprehension; an S3 learner may start S3 without completing S1 cards.

Lesson search indexing, revision planner, progress rings and API topic catalog update automatically from the registry once labels are added. Exclude `eursc/science` from QOTD until its first complete year is live so incomplete banks do not leak.

---

## 7. Content architecture

Split generators/banks by official unit to keep files reviewable:

```text
generators/eursc/
  __init__.py
  science_shared.py
  s1_science_lab.py
  s1_food.py
  s1_sports.py
  s1_puberty.py
  s2_universe.py
  s2_health.py
  s2_senses.py
  s3_machines.py
  s3_living_earth.py
```

Each normal module provides:

- variable-depth lesson template `templates/eursc_science_{slug}_lesson.html`;
- inline MCQ checkpoint after each assessable concept cluster (counts in §3);
- ≥15 MCQs plus ≥8 non-MCQ typed problems, enough to assemble varied ten-question quizzes;
- `variants_func(difficulty, 'lesson')` for the mixed lesson bank;
- at least one diagram/data question where appropriate;
- concise quick-reference card;
- explicit `syllabus_ref` shown in metadata.

Project modules provide a readiness/method question bank, project phases, printable rubric and quick-reference checklist. They do not pretend the physical product is auto-graded.

Hard lesson-template rules remain: `lesson-shell`, no inline `style=`, matching checkpoint markup, 200 route, CSP-safe external JS only.

---

## 8. Delivery phases

| Phase | Scope | Exit |
|-------|-------|------|
| **ES0 — Mixed-quiz engine + hierarchy** | Generalise lesson quiz to existing typed formats; capability-based quiz gate; `eursc` labels/icon/filter; year/unit path grouping; filename test; keep Practice generator closed | Synthetic MCQ/order/pick/numeric quiz passes web/API/retry/session-security tests |
| **ES1 — Pilot** | 1.1.2 Measurement, chosen because it exercises numeric, data, MCQ and progress | Complete lesson + ten-question mixed quiz; mastery ring; mobile/a11y pass |
| **ES2 — S1 Science Lab** | 1.1.1–1.1.3 | Official objectives covered; first IBL support |
| **ES3 — S1 Food** | 1.2.1–1.2.8 | Eight modules including meal project |
| **ES4 — S1 Sports + Puberty** | 1.3.1–1.4.3 | Seven modules; clinical/safeguarding review; S1 complete |
| **ES5 — S2 Universe** | 2.1.1–2.1.4 | Four modules + IBL support |
| **ES6 — S2 Health** | 2.2.1–2.2.5 | Five modules |
| **ES7 — S2 Senses** | 2.3.1–2.3.8 | Eight modules; S2 complete |
| **ES8 — S3 Machines** | 3.1.1–3.1.6 | Six modules including robot project |
| **ES9 — S3 Living Earth** | 3.2.1–3.2.5 | Five modules including field project; S3 complete |
| **ES10 — Whole-suite QA** | Search, revision planning, subject badges, content matrix, browser/mobile/accessibility, docs/cache | **Shipped** — `scripts/test_es10_whole_suite_smoke.py`; 62 smoke files green |

Each official unit is one reviewed change. Never register partially authored topics: build the templates and banks behind tests, then add that complete unit to `TOPICS`.

---

## 9. Verification

Add:

- curriculum coverage test: all 46 official refs appear exactly once;
- registry test: valid year/unit/ref metadata and unique order;
- lesson depth test: expected section/checkpoint counts come from a manifest, not a global 6–7 assertion;
- mixed-quiz tests for MCQ, numeric, keyword, ordered `proof_steps`, pick/set, partial structured score, retry and results;
- session-security tests: answer keys come only from saved quiz sessions;
- content safety test: no first-person disclosure prompts in 1.4/2.2;
- project tests: six IBL support pages, rubrics and printable view;
- route/search/progress tests for each registered module;
- existing CSS budget, CSP, accessibility, PWA and full smoke suite.

Maintain a machine-readable curriculum manifest alongside the bank:

```python
SYLLABUS_MODULES = {
    "1.1.2": {
        "slug": "measurement",
        "sections": 6,
        "checkpoints": 7,
        "objectives": (...),
    },
}
```

Tests compare registry, templates and manifest so “full curriculum” is measurable rather than a documentation claim.

---

## 10. Definition of done

- [x] `eursc/science` presents all 46 numbered syllabus modules under nine official units and three years.
- [x] Section/checkpoint counts follow §3; there is no fixed 6–7 rule.
- [x] Every official objective is mapped to teaching content and an auto-graded or rubric checkpoint.
- [x] Every normal lesson has a secure ten-question mixed quiz using appropriate existing graders.
- [x] Ordering and pick/set questions are used where pedagogically appropriate; matching is represented with existing formats.
- [x] Six substantial IBL support tracks exist, while clearly requiring classroom practical work.
- [x] Puberty/sexuality is complete, clinical, age-appropriate and never solicits personal disclosure.
- [x] Main Practice generator remains GCSE maths/CS only; European Science banks are lesson-quiz-only in v1.
- [x] Topic path, progress, search, revision planner and subject badges work for S1–S3.
- [x] Curriculum coverage, security, browser/mobile/accessibility and all smoke tests pass.
