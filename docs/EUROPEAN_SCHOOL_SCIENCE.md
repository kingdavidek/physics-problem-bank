# European School Integrated Science S1–S3 — lesson suite plan

**Last updated:** 2026-08-27
**Status:** Planned (designed) — not started
**Source syllabus:** Schola Europaea, *Integrated Science Syllabus S1-S3*, ref **2018-12-D-6-en-2**, approved by the Joint Teaching Committee 7–8 February 2019. In force 1 Sept 2019 (S1), 2020 (S2), 2021 (S3). [Official PDF](https://www.eursc.eu/Syllabuses/2018-12-D-6-en-2.pdf)
**Companion docs:** `docs/ARCHITECTURE.md` (registry + templates), `docs/AI_HANDOFF.md` (phases), `docs/UI_REDESIGN.md` (lesson shell)

Adds a new level `eursc` with one subject `science`, covering the compulsory Observation Cycle science course (4 periods/week, all three years). This is a **content track**, not a new engine: it reuses the existing lesson shell, quick-check MCQs, lesson quiz, and Quick Test.

---

## 1. What the syllabus actually contains

Integrated Science is a **thematic** course, not three separate sciences. Nine units across three years, each broken into numbered subsections. Biology, chemistry and physics are interleaved inside each theme.

| Year | Unit | Subsections |
|------|------|-------------|
| S1 | 1.1 Science Lab | 1.1.1 What is science? · 1.1.2 Measurement · 1.1.3 A science lab |
| S1 | 1.2 Food, Cooking and Nutrition | 1.2.1 Food formulas · 1.2.2 Water and heating · 1.2.3 Heat transfer · 1.2.4 Acidity · 1.2.5 Salt · 1.2.6 Fermentation · 1.2.7 Nutrition · 1.2.8 Capstone meal |
| S1 | 1.3 Sports | 1.3.1 Movement · 1.3.2 Forces · 1.3.3 Body mechanics · 1.3.4 Sports and health |
| S1 | 1.4 Puberty and Sexuality | 1.4.1 Puberty · 1.4.2 Reproductive anatomy · 1.4.3 Pregnancy, contraception, STIs |
| S2 | 2.1 Our Place in the Universe | 2.1.1 Solar system · 2.1.2 Light · 2.1.3 Life on Earth · 2.1.4 Atoms |
| S2 | 2.2 Mens Sana in Corpore Sano | 2.2.1 Healthy living · 2.2.2 Infectious disease · 2.2.3 Noninfectious disorders · 2.2.4 Dependence · 2.2.5 Tobacco |
| S2 | 2.3 The Senses | 2.3.1 Vision · 2.3.2 Hearing · 2.3.3 Touch · 2.3.4 Smell · 2.3.5 Taste · 2.3.6 Proprioception · 2.3.7 Interoception · 2.3.8 Nonhuman senses |
| S3 | 3.1 Machines and How They Work | 3.1.1 Force and machines · 3.1.2 Energy · 3.1.3 Electrostatics · 3.1.4 Electric current · 3.1.5 Magnetism · 3.1.6 Capstone robotics |
| S3 | 3.2 Our Living Earth | 3.2.1 Human impact · 3.2.2 Ecosystems · 3.2.3 Ecosystem dynamics · 3.2.4 Classification · 3.2.5 Capstone field study |

That is ~46 subsections including three **optional practical capstones** (cook a meal, build a robot, run a field study). Capstones cannot be auto-assessed, so they become a project-brief section inside the neighbouring lesson, never a standalone topic.

### Consequence for this platform

The site is built around **generated, auto-graded practice**. Much of Integrated Science is qualitative (classification, anatomy, disease, senses). Only part of it supports numeric generators:

| Practice model | Subsections |
|----------------|-------------|
| **Numeric generator** (free response, answer checker) | Measurement / SI conversion, movement (speed–distance–time), forces, energy and power, electric current (V = IR), astronomical scale, nutrition energy (kJ/kcal), ecosystem data |
| **MCQ bank only** | Everything else (~22 topics) |

So the default practice mode for this subject is **MCQ**, with numeric generators layered on the ~10 quantitative topics. This is a deliberate departure from GCSE maths and must be accepted up front.

---

## 2. Proposed topic map (32 lessons)

Subsections are merged where they are too thin to carry a full lesson. `order` runs 1–32 continuously so `/topics` renders one syllabus path S1 → S3.

### S1 — orders 1–12

| # | Slug | Name | Covers | Practice |
|---|------|------|--------|----------|
| 1 | `what_is_science` | What Science Is and How It Works | 1.1.1 | MCQ |
| 2 | `measurement` | Measurement and SI Units | 1.1.2 | Numeric |
| 3 | `science_lab` | The Science Lab: Instruments and Safety | 1.1.3 | MCQ |
| 4 | `food_molecules` | Molecules of Life | 1.2.1 | MCQ |
| 5 | `water_and_heat` | Water, Heat and Phase Change | 1.2.2 | Numeric |
| 6 | `heat_transfer` | Cooking with Heat: Conduction, Convection, Radiation | 1.2.3 | MCQ |
| 7 | `acid_salt_fermentation` | Acids, Salt and Fermentation | 1.2.4–1.2.6 | MCQ |
| 8 | `nutrition` | Nutrition and Healthy Eating | 1.2.7, 1.2.8 brief | Numeric |
| 9 | `movement` | Movement: Speed, Distance and Time | 1.3.1 | Numeric |
| 10 | `forces` | Forces in Sport | 1.3.2 | Numeric |
| 11 | `body_mechanics` | Muscles, Bones and Joints | 1.3.3–1.3.4 | MCQ |
| 12 | `puberty_reproduction` | Puberty, Reproduction and Sexual Health | 1.4.1–1.4.3 | MCQ · see §5 |

### S2 — orders 13–23

| # | Slug | Name | Covers | Practice |
|---|------|------|--------|----------|
| 13 | `solar_system` | The Solar System | 2.1.1 | Numeric |
| 14 | `light_and_telescopes` | Light and Telescopes | 2.1.2 | Numeric |
| 15 | `life_on_earth` | Life on Earth and Elsewhere | 2.1.3 | MCQ |
| 16 | `atoms` | Atoms: Building Blocks of Matter | 2.1.4 | MCQ |
| 17 | `healthy_living` | Healthy Living: Diet, Exercise, Sleep | 2.2.1 | MCQ |
| 18 | `infectious_disease` | Infectious Disease and Immunity | 2.2.2 | MCQ |
| 19 | `noninfectious_disease` | Noninfectious and Environmental Disease | 2.2.3 | MCQ |
| 20 | `dependence_tobacco` | Dependence, Addiction and Tobacco | 2.2.4–2.2.5 | MCQ |
| 21 | `vision_hearing` | Vision and Hearing | 2.3.1–2.3.2 | MCQ |
| 22 | `touch_smell_taste` | Touch, Smell and Taste | 2.3.3–2.3.5 | MCQ |
| 23 | `other_senses` | Balance, Body Awareness and Animal Senses | 2.3.6–2.3.8 | MCQ |

### S3 — orders 24–32

| # | Slug | Name | Covers | Practice |
|---|------|------|--------|----------|
| 24 | `simple_machines` | Forces and Simple Machines | 3.1.1 | Numeric |
| 25 | `energy_work_power` | Energy, Work and Power | 3.1.2 | Numeric |
| 26 | `electrostatics` | Electrostatics | 3.1.3 | MCQ |
| 27 | `electric_circuits` | Electric Current and Circuits | 3.1.4 | Numeric |
| 28 | `magnetism` | Magnetism and Electromagnetism | 3.1.5, 3.1.6 brief | MCQ |
| 29 | `human_impact` | Human Production and Consumption | 3.2.1 | MCQ |
| 30 | `ecosystems` | Ecosystems, Water and Carbon Cycles | 3.2.2 | Numeric |
| 31 | `biodiversity` | Ecosystem Dynamics and Biodiversity | 3.2.3, 3.2.5 brief | MCQ |
| 32 | `classification` | Classification of Living Things | 3.2.4 | MCQ |

`prereqs` follow the syllabus sequence within a year only (for example `forces` after `movement`, `electric_circuits` after `electrostatics`). No cross-year prereqs, so an S3 pupil is not blocked by S1 topics.

---

## 3. Platform enablement (blocking, do first)

Three hardcoded gates currently make any non-GCSE content second class. All three must be widened before content lands.

| # | File | Current | Change |
|---|------|---------|--------|
| 1 | [`app.py`](app.py) `_lesson_quiz_available` (~1892) | `if level != "gcse" or subject not in ("maths", "cs")` | Allowlist `('eursc', 'science')` |
| 2 | [`models/buddy.py`](models/buddy.py) `_quiz_available` (~146) | same gate, duplicated | Share one helper instead of duplicating |
| 3 | [`app.py`](app.py) `GENERATOR_LAUNCH_GCSE_MATHS_CS` (~2101) | clamps generator UI to GCSE maths + CS | Add `eursc/science` to launch scope, or leave lessons-only (see §5) |

Then the standard new-level wiring:

| File | Change |
|------|--------|
| [`topic_registry.py`](topic_registry.py) | `TOPICS['eursc']['science']` with 32 entries (`name`, `order`, `func`, `variants_func`, `prereqs`). **`func` is mandatory** — `app.py` does `topic_config['func']` and raises `KeyError` without it |
| [`app.py`](app.py) | `_TOPIC_LEVEL_ORDER += ('eursc',)`; `_TOPIC_SUBJECT_ORDER['eursc'] = ('science',)`; `LEVEL_LABELS['eursc'] = 'European School'`; `SUBJECT_LABELS['science'] = 'Integrated Science'` |
| [`models/lesson_search.py`](models/lesson_search.py) | `_LEVEL_LABELS` / `_SUBJECT_LABELS` entries (index itself is automatic) |
| [`models/topic_status.py`](models/topic_status.py) | Same label dicts; generalise `gcse_subject_slugs()` if subject-wide badges are wanted |
| [`templates/topics.html`](templates/topics.html) | Level filter button + `subject_icons['science']` |
| [`static/js/u4.js`](static/js/u4.js) | Level whitelist at ~115 and ~120 |
| [`templates/partials/icon.html`](templates/partials/icon.html) | New `#icon-science` symbol |
| [`templates/index.html`](templates/index.html) | Level and subject `<option>` entries (only if generator scope opens) |
| [`scripts/test_lesson_unify_smoke.py`](scripts/test_lesson_unify_smoke.py) | `FILENAME_RE` currently `^(gcse\|alevel\|myp)_…` — **must add `eursc` or CI fails** |
| [`static/js/sw.js`](static/js/sw.js) | `CACHE_VERSION` bump |

What updates automatically once registered: `/topics` grid, `/api/v1/topics`, lesson search index, QOTD pool, revision planner, weak-topic detection, mastery rings.

---

## 4. Per-lesson shape

Match the GCSE maths standard so lesson progress, ninja badges and the quiz all work.

```
templates/eursc_science_{topic}_lesson.html
  {% extends "base.html" %}
  .lesson-shell
    .lesson-hero          h1 + hero-sub + pill-row (year tag "S1")
    .lesson-quiz-cta      -> lesson_mcq_quiz(level='eursc', subject='science', topic=...)
    details.lesson-section  x6-7   (chip number, summary, body)
      .lesson-quickcheck > .mcq-inline[data-correct]   one per section
    final section: quick reference card
    .lesson-practice-cta
```

Hard rules enforced by [`scripts/test_lesson_unify_smoke.py`](scripts/test_lesson_unify_smoke.py):

- No inline `style="…"` anywhere in a lesson template
- `class="lesson-shell"` present
- `mcq-inline` count must equal `data-correct=` count
- Route must return 200

`lesson_step_total` counts `class="mcq-inline"` occurrences, so **6–7 quick checks per lesson** gives a sensible progress bar and unlocks lesson-complete / ninja status.

Per topic the deliverables are:

1. Lesson template (~450–700 lines, 6–7 sections, 6–7 quick checks)
2. MCQ bank of **≥15 items** (needed so a 10-question lesson quiz can deduplicate)
3. Generator function + `variants_func` in `generators/eursc/science_*.py`
4. Registry entry
5. Optional `topics_data.py` entry for search enrichment

Diagrams should use [`models/svg_kit.py`](models/svg_kit.py) where a primitive already exists (bar charts, pie charts, tables); new science diagrams (cell, circuit, eye) are hand-authored inline SVG using CSS variable colours, matching the existing lesson pattern.

---

## 5. Decisions needed before content starts

**A. Unit 1.4 Puberty and Sexuality — safeguarding.**
This is compulsory syllabus content (anatomy, pregnancy, contraception, STIs) for pupils around 12. The platform is used by minors and has a strict safeguarding posture (`docs/ENGAGEMENT_VISUAL.md` §5). Options:

1. Ship it with clinical, curriculum-faithful framing and no imagery beyond labelled diagrams — matches the syllabus and what pupils are taught in class
2. Ship a reduced version (puberty and reproduction only, no contraception/STI detail)
3. Defer the topic; the path shows 31 lessons and one "covered in class" placeholder

Recommendation: **option 1**, because omitting compulsory content makes the suite incomplete, but this is a product call, not an engineering one.

**B. Generator scope.** `GENERATOR_LAUNCH_GCSE_MATHS_CS = True` deliberately hides everything except GCSE maths/CS from the practice generator. Either open it for `eursc/science` (more surface, more risk of half-finished generators being visible) or ship **lessons + lesson quizzes only** and leave the generator GCSE-only. Recommendation: lessons + quizzes first, open the generator in a later slice once MCQ banks are proven.

**C. Depth.** Full GCSE-quality lessons across 32 topics is roughly **16,000+ lines** of lesson HTML plus ~32 generator modules — the dominant cost is authoring, not wiring. The alternative is MYP-style thin pages (~150 lines, no quick checks), which ship far faster but give no progress tracking, no ninja badges and no quiz. Recommendation: **full quality**, phased by year, rather than 32 thin pages.

---

## 6. Phasing

| Phase | Scope | Exit criteria |
|-------|-------|---------------|
| **E0 — Enablement + pilot** | All of §3, plus **one** complete lesson (`measurement`, order 2 — quantitative, so it exercises numeric generator + MCQ bank + quiz together) | `/topic/eursc/science/measurement` renders; quiz runs 10 MCQs; Quick Test works; progress ring moves; all smoke tests green |
| **E1 — S1** | Orders 1–12 | 12 lessons live, each with quiz; `/topics` shows the S1 path |
| **E2 — S2** | Orders 13–23 | 11 lessons live |
| **E3 — S3** | Orders 24–32 | 9 lessons live; subject-complete badge fires |
| **E4 — Polish** | `topics_data.py` entries, revision-plan tuning, subject badges, docs, screenshots | Search returns science lessons; docs updated |

Within E1–E3, work in **unit-sized batches** (one thematic unit per commit) so review stays manageable and a half-finished unit never ships.

---

## 7. Risks

| Risk | Mitigation |
|------|------------|
| Qualitative content does not fit an auto-graded generator | MCQ-first practice model; numeric generators only on the ~10 quantitative topics |
| Content volume dwarfs previous phases | Unit-sized batches; pilot first to lock the template pattern |
| Sensitive content (1.4) | Explicit product decision in §5A before authoring |
| CSS budget | Lessons reuse existing classes; `lesson-pages.css` is route-only and outside the core budget. No new keyframes expected |
| Three hardcoded GCSE gates silently degrade the new level | Fixed in E0 before any content lands |
| Syllabus drift | Pin to ref `2018-12-D-6-en-2`; re-check the [all-syllabi index](https://www.eursc.eu/en/european-schools/studies/syllabuses/all-syllabi/) before each phase |

---

## 8. Definition of done

- [ ] `eursc` / `science` registered, 32 topics, `validate_topic_registry()` clean
- [ ] All three GCSE-only gates widened or consciously left closed with a comment
- [ ] 32 lesson templates, each 6–7 sections with 6–7 quick checks, no inline styles
- [ ] MCQ bank ≥15 items per topic; lesson quiz returns 10 unique questions
- [ ] Numeric generators on the 10 quantitative topics with `variants_func`
- [ ] `/topics` shows a European School path S1 → S3 with working mastery rings
- [ ] Lesson search returns science lessons with correct level/subject labels
- [ ] `python scripts/run_smoke_tests.py` green, `FILENAME_RE` updated, cache bumped
- [ ] `docs/ARCHITECTURE.md` curriculum table and `docs/AI_HANDOFF.md` updated
