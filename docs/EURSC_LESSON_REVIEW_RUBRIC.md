# European School Integrated Science — lesson review rubric

**Track:** Lesson clarity, examples, diagrams and tables for S1–S3 (46 modules).  
**Use:** Every agent editing a lesson, figure, table, quick check, or unit bank in this track.  
**Source of truth:** `generators/eursc/science_shared.py` (`SYLLABUS_MODULES`, `IBL_PAGES`) and `docs/EUROPEAN_SCHOOL_SCIENCE.md`.  
**Priorities:** optional canvas `eursc-lesson-quality-plan.canvas.tsx` (lesson-by-lesson worklist).  
**Last updated:** 2026-08-29 (Stage 5 S3 pass complete)

This is not a rewrite. Structure, checkpoint coverage and safeguarding are already in place. Improve explanations, examples and visuals where they help learning.

---

## Delivery stages

Do **one stage per user cue**. Stop and report when the stage is done.

| Stage | Name | Scope | Status |
|-------|------|--------|--------|
| **0** | **Baseline and rubric** | Smoke baseline + this checklist | **Complete** (2026-08-28) |
| **1** | Shared lesson system | Science hero accent, `<figure>`/`<figcaption>`, table a11y/mobile, aria-live MCQ feedback, vocabulary-gloss pattern, print CSS — **before** per-lesson edits | **Complete** (2026-08-28) |
| **2** | Diagram foundation | `science_shared` SVG contract tests; consolidate measurement SVGs; reusable axes, legends, units, arrows, branching, colour-independent cues | **Complete** (2026-08-29) |
| **3** | S1 pass | Units 1.1–1.4 (18 lessons). Prioritise 1.1.2, 1.3.3, 1.4.2 | **Complete** (2026-08-29) |
| **4** | S2 pass | Units 2.1–2.3 (17 lessons). Prioritise 2.1.1–2.1.2, 2.2.2, 2.2.4–2.2.5, 2.3.8 | **Complete** (2026-08-29) |
| **5** | S3 pass | Units 3.1–3.2 (11 lessons). Prioritise 3.1.2, 3.1.4–3.1.5, 3.2.1–3.2.4 | **Complete** (2026-08-29) |
| 6 | Question alignment | Five Practice slots per topic per difficulty — **do not start until Stage 6** | **Next** |
| 7 | Verification | Full smoke + manual mobile/dark/print + sensitive-lesson sample | Pending |

---

## Stage 0 baseline

Recorded 2026-08-28 on `cursor/cloud-agent-1787823476595-0do93` at `7045d5c` (up to date with origin). Manifest and curriculum spec present.

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Suite size | **62** files (`scripts/test_*_smoke.py`) |
| First full run | **61 passed, 1 failed** — `FAILED: test_es0_mixed_quiz_smoke.py` |
| Isolated re-run | `python scripts/test_es0_mixed_quiz_smoke.py` **passed** |

**ES0 flake:** `test_mixed_quiz_api_web_retry_security` asserts `'mcq' in types_seen` on an **unseeded** API quiz. The fixture pool is 1 MCQ + 4 typed per difficulty; `build_lesson_quiz` draws 3/4/3, so a quiz can omit every MCQ. The seeded `build_lesson_quiz(..., seed=7)` check in the same test is stable. Do not treat this as a lesson-content failure. Do not “fix” it in Stages 1–5 (no generator/quiz-engine work until Stage 6 unless the user asks).

## Stage 1 shared system (shipped)

| Piece | Where |
|-------|--------|
| Science hero accent | `components.css` — `[data-lesson-subject="science"] .lesson-hero` |
| Figure/caption contract | `figure.lesson-figure` + `figcaption` / `.lesson-figure-caption`; JS upgrades `div.lesson-figure` |
| Tables | `.lesson-table-wrap` overflow; JS sets `scope="col"` on `thead th` |
| MCQ live feedback | `enhanceMcqFeedback` in `site.js` (`aria-live="polite"`, `role="status"`); `.mcq-feedback.is-correct` / `.is-wrong` in `practice.css` |
| Vocabulary gloss | `.lesson-gloss` / `.lesson-gloss-def` — use in Stages 3–5, do not bulk-rewrite |
| Print | `@media print` in `lesson-pages.css` opens `.lesson-section` bodies and hides quiz/progress chrome |
| IBL | Loads `lesson-pages.css` and `data-lesson-subject="science"` without `data-lesson-content` |

## Stage 2 diagram foundation (shipped)

| Piece | Where |
|-------|--------|
| Primitives | `science_arrow`, `science_axes`, `science_cue`, `science_legend`, `science_branch` in `generators/eursc/science_shared.py` |
| Measurement SVGs | `ruler_scale(4.7)` and `accuracy_targets()` injected as `ruler_fig` / `accuracy_fig` |
| Colour-independent hits | circle / square / diamond / plus on the four accuracy targets |
| Contract tests | `scripts/test_es_science_svg_smoke.py` over `SCIENCE_SVG_FIGURES` |

Stages 3–5 should call these helpers (or `svg()` + primitives) instead of new inline lesson SVG.

## Stage 3 S1 pass (shipped)

Units 1.1–1.4 (18 lessons). Checkpoint and section counts unchanged. No inline `style=`.

| Focus | What changed |
|-------|----------------|
| **1.1.2** measurement | Glosses (SI, prefix, calibration, accuracy/precision); mean/range and zero-error worked examples; `<figure>`/`<figcaption>` |
| **1.3.3** breathing | Air tables; respiration vs ventilation; pulse worked example; circulation arrows + caption; pressure/buoyancy glosses |
| **1.4.2** reproductive anatomy | Egg-path arrow; menstrual-cycle sequence figure (`menstrual_cycle_steps`); gamete/ovulation/fertilisation glosses; third-person safeguarding |
| Other S1 | Captions on existing figures; one gloss and one worked example per hard idea; distance–time axes with units; force-pair arrows |

## Stage 4 S2 pass (shipped)

Units 2.1–2.3 (17 lessons). Checkpoint and section counts unchanged. No inline `style=`. Chemical senses/technology folded into 2.3.8 without a new section.

| Focus | What changed |
|-------|----------------|
| **2.1.1** solar system | AU scale figure; rotation/revolution/AU/heliocentric glosses; tilt and distance worked examples |
| **2.1.2** light | Reflection arrows (\(i=r\)); light-year and refraction glosses; speed and eclipse sequences |
| **2.2.2** infectious disease | Chain arrows and captions; source→route→host check; outbreak doubling example; pathogen/vaccine glosses |
| **2.2.4–2.2.5** | Dependence vs pleasure example; nicotine/marketing glosses; public-count table; third-person safeguarding |
| **2.3.8** nonhuman senses | Chemical signal → sensor → reading figure; echolocation/infra/ultrasound glosses |
| Other S2 | Captions on existing figures; LUCA/element/molecule/microbiome/accommodation glosses |

## Stage 5 S3 pass (shipped)

Units 3.1–3.2 (11 lessons). Checkpoint and section counts unchanged. No inline `style=`. No power calculations; `electric_current` has no \(V=IR\).

| Focus | What changed |
|-------|----------------|
| **3.1.2** energy | Sankey arrows and 100 J → 40 J / 60 J split; transform/transfer/waste/conservation glosses |
| **3.1.4** electric current | Closed-loop circuit figure; series vs parallel worked examples; qualitative meters only |
| **3.1.5** magnetism | N/S labels (not colour-only); field caption; electromagnet on/off example |
| **3.2.1** food and environment | Produce→use→waste sequence; public GHG table; no plate or household diary |
| **3.2.2** ecosystems | Water and carbon cycle sequences; trophic caption; photosynthesis/respiration word equations |
| **3.2.3** ecosystem characteristics | Abiotic/biotic/survey figure caption; model-critique example |
| **3.2.4** classification | Dichotomous `science_branch` key; taxonomy/descent glosses |
| Other S3 | Lever labels and \(W=Fd\) example (no power); charge attract/repel caption; fictional robot and field-plan examples |

---

## Per-lesson checklist

Work through this list for **each** lesson you touch. Tick in review notes; do not add checklist markup to the HTML.

### 1. Objective coverage

- [ ] Every string in `SYLLABUS_MODULES[ref]["objectives"]` remains traceable in the template (ES10 `test_templates_depth_and_objectives` / `_objective_traceable`).
- [ ] Hero subtitle and section titles match the official module scope in `docs/EUROPEAN_SCHOOL_SCIENCE.md` §3.
- [ ] Do not add off-syllabus topics, extra official subsections, or new learning objectives.
- [ ] `syllabus_ref` (e.g. `1.1.2`) still appears in the template.

### 2. Age-appropriate language

| Year | Voice |
|------|--------|
| S1 | Concrete first. Short sentences. Gloss a hard term on first use (`provisional`, `reproducibility`, `denature`, `saturated`, …). |
| S2 | Compare models and evidence. Distinguish observation, model, and speculation. |
| S3 | Mechanism, then apply. Name the process; then one worked use. |

- [ ] Active voice; one new term at a time.
- [ ] Spell out symbols pupils may not know (`O₂` / oxygen, `CO₂` / carbon dioxide) on first use in that lesson.
- [ ] Gloss a hard term with the shared pattern (do not invent inline styles):

```html
<dfn class="lesson-gloss" title="Can change if better evidence appears">provisional</dfn>
<span class="lesson-gloss-def">A scientific explanation that can change if better evidence appears.</span>
```

- [ ] No unexplained jargon in quick checks.

### 3. Concept → example → check

For each hard idea in a section:

1. **Concept** — what it is, in the year’s voice.
2. **Example** — one worked case (see table).
3. **Check** — one inline MCQ that tests that idea.

| Kind of idea | Example required |
|--------------|------------------|
| Quantitative | One worked example with **units** |
| Abstract process | One named sequence (A → B → C) |
| Classification | One example **and** one non-example |
| Sensitive topic | Fictional third party or public/aggregate data only |

- [ ] The quick check comes **after** the concept and example, not before.
- [ ] Project modules: one fictional worked planning/data example; the physical product stays IBL/rubric, not auto-graded.

### 4. Figures and tables

**Markup:** wrap diagrams in `figure.lesson-figure` (a `div.lesson-figure` is upgraded to `<figure>` in the browser). Captions use `<figcaption>` or `p.lesson-figure-caption`. Tables use `table.lesson-table` (JS wraps them in `.lesson-table-wrap` and sets `scope="col"` on `thead th`). No `style=` attributes.

```html
<figure class="lesson-figure">
  <!-- svg or injected figure -->
  <figcaption>What the reader should see, with named parts and units.</figcaption>
</figure>
```

- [ ] Every figure has a **visible** caption (what the reader should see).
- [ ] Graphs: named axes, units, and scale — not colour-only series.
- [ ] Diagrams: arrows and labels; N/S, +/−, flow direction where they matter.
- [ ] Shape or text cues alongside colour (colour-blind / print / dark mode).
- [ ] Tables only when comparison or data reading is easier than prose; header row present.
- [ ] Prefer `science_shared` helpers (`ruler_scale`, `accuracy_targets`, `science_axes`, `science_arrow`, `science_cue`, `science_branch`) or `svg_kit.svg()` over new one-off inline SVG.
- [ ] Figures still make sense in dark mode (`lesson-pages.css` SVG token mapping).

### 5. Quick-check quality

Required markup (counts are tested):

```html
<div class="lesson-quickcheck">
  <p class="lesson-quickcheck-title">Quick Check</p>
  <div class="mcq-inline" data-correct="B">
    <p>Question stem…</p>
    <button class="btn mcq-btn" data-letter="A">…</button>
    <button class="btn mcq-btn" data-letter="B">…</button>
    <button class="btn mcq-btn" data-letter="C">…</button>
    <button class="btn mcq-btn" data-letter="D">…</button>
    <p class="mcq-feedback"></p>
  </div>
</div>
```

- [ ] `class="mcq-inline"` count **equals** `SYLLABUS_MODULES[ref]["checkpoints"]`.
- [ ] `data-correct=` count equals the same number.
- [ ] `class="lesson-section"` count equals `SYLLABUS_MODULES[ref]["sections"]`.
- [ ] The check tests **this section’s** main idea.
- [ ] Distractors are plausible misconceptions, not nonsense.
- [ ] At most **one** humorous or privacy-boundary distractor per check.
- [ ] `data-correct` letter matches the `data-letter` on the intended button.

IBL templates must **not** contain `.mcq-inline` (ES smokes assert this).

### 6. Safeguarding

**Highest scrutiny:** syllabus refs `1.4.*` (puberty/anatomy/sexual health) and `2.2.*` (healthy living, disease, addiction, tobacco). ES10 `SENSITIVE_REFS` and `DISCLOSE_RE` in `scripts/test_es10_whole_suite_smoke.py`. Also careful: `2.3.7` interoception, `1.2.7` nutrition, `1.2.8` healthy meal.

- [ ] Clinical, age-appropriate, third-person language.
- [ ] Scenarios use **fictional** people or **public/aggregate** data — never the reader’s body, diet, sexuality, diagnosis, medication, mood, or substance use.
- [ ] No first-person disclosure prompts. Forbidden patterns include (not exhaustive): `your diet`, `have you ever`, `your body`, `are you attracted`, `do you smoke`, `are you addicted`, `how do you feel`, `map your body`.
- [ ] Labelled educational diagrams only; no sensational imagery.
- [ ] Signpost teacher / qualified-health guidance where personal decisions arise.
- [ ] Question banks assess knowledge and healthy decision-making, not identity or behaviour.
- [ ] Do **not** add `eursc` to QOTD (1.4 / 2.2 / interoception must not appear as site-wide daily questions).

### 7. Scope limits

- [ ] **Do not** change `SYLLABUS_MODULES` `sections` or `checkpoints` unless the user explicitly approves a manifest change.
- [ ] **3.1.1** Force, Work and Simple Machines: keep \(W=Fd\); **no power** calculations.
- [ ] **3.1.4** Electric Current: qualitative current and voltage; **no \(V=IR\)** and no resistance calculations.
- [ ] **2.3.8** Nonhuman senses: close chemical-sense / technology gaps **inside** the current section/checkpoint counts unless a manifest change is approved.
- [ ] IBL pages (`templates/eursc_science_ibl_*.html`) are classroom practical support — not a second lesson rewrite.
- [ ] Do not open `eursc/science` on the main Practice generator until **Stage 6**.
- [ ] Do not register incomplete topics; do not invent new answer types.

### 8. Quiz-key and progress stability

Lesson progress keys are `step-0`, `step-1`, … in **DOM order** of `.mcq-inline` (`static/js/lesson-progress.js`). Adding, removing, or reordering checks remaps saved progress.

- [ ] Same checkpoint **count** and **order** as the manifest (no inserts, deletes, or swaps).
- [ ] When polishing a check, keep the same correct **letter** if the same option remains the right answer.
- [ ] If you must rewrite options, update `data-correct` in the same edit and keep four `data-letter` buttons A–D.
- [ ] End-of-lesson quiz banks (`generators/eursc/s1_*.py` … `s3_*.py`): do not drop items or change `correct_answer` / `correct_answer_raw` when only improving lesson wording. Recuration of Practice slots is **Stage 6**.
- [ ] Mixed quiz still uses session-stored keys — never a client-supplied correct flag.

### 9. Template and CSS contract

- [ ] Root wrapper is `div.lesson-shell` (no inline `style=`).
- [ ] Existing classes only: `lesson-hero`, `lesson-section`, `lesson-table`, `lesson-figure`, `lesson-callout`, `lesson-quickcheck`, `lesson-quickref`, `pill`, `btn`, `mcq-btn`, …
- [ ] Quick-reference block (`lesson-quickref`) still present.
- [ ] CSP-safe: no new external JS; no inline event handlers.
- [ ] If you change cached JS/CSS/templates, bump cache query params and `CACHE_VERSION` in `static/js/sw.js` (see `docs/AI_HANDOFF.md` §8).

---

## How to edit a lesson (Stages 3–5)

1. Read `SYLLABUS_MODULES[ref]` (objectives, `sections`, `checkpoints`) and the official row in `docs/EUROPEAN_SCHOOL_SCIENCE.md` §3.
2. Open `templates/eursc_science_{slug}_lesson.html`. Count `lesson-section` and `mcq-inline` **before** editing.
3. Apply this rubric. Prefer a short gloss + one example over a new section.
4. If the lesson is in 1.4 or 2.2, grep the template and that topic’s generator bank against `DISCLOSE_RE`.
5. Run the **unit** smoke (`scripts/test_es{n}_*_smoke.py`) plus `scripts/test_es10_whole_suite_smoke.py` if you touched manifest-sensitive markup.
6. Do not start the next lesson’s rewrite in the same stage beyond that stage’s unit list without a user cue.

**High-priority slugs (do these first inside each year pass):**

| Pass | Refs | Why |
|------|------|-----|
| S1 | 1.1.2 `measurement`, 1.3.3 `breathing`, 1.4.2 `reproductive_anatomy` | Shared SVGs; circulation captions; anatomy sequencing |
| S2 | 2.1.1–2.1.2, 2.2.2, 2.2.4–2.2.5, 2.3.8 | Scale/optics; infection chain; health data; chemical senses gap |
| S3 | 3.1.2, 3.1.4–3.1.5, 3.2.1–3.2.4 | Sankey; closed-loop circuits (no \(V=IR\)); cycles, taxonomy, ecology diagrams |

---

## Hard constraints (every stage)

1. Preserve `SYLLABUS_MODULES` section/checkpoint counts unless the user approves a manifest change.
2. No inline `style=` on lesson templates.
3. Units 1.4 and 2.2: clinical, third-person, fictional/public data; `DISCLOSE_RE` must stay clean.
4. S3 machines: no power; `electric_current` has no \(V=IR\).
5. IBL pages are practical support only.
6. No Practice-generator admission for `eursc/science` until Stage 6.
7. Commit only when the user asks.

---

## Related paths

| Area | Path |
|------|------|
| Manifest + SVG helpers | `generators/eursc/science_shared.py` |
| Lesson templates | `templates/eursc_science_{slug}_lesson.html` |
| IBL templates | `templates/eursc_science_ibl_*.html` |
| Figure injection | `app.py` — `_lesson_render_spec()` |
| Quiz banks | `generators/eursc/s1_*.py` … `s3_*.py` |
| Lesson CSS | `static/css/lesson-pages.css`, `components.css`, `diagrams.css` |
| Progress keys | `static/js/lesson-progress.js` (`step-{index}`) |
| Disclosure scan | `DISCLOSE_RE` in `scripts/test_es10_whole_suite_smoke.py` |
| Full smoke | `scripts/run_smoke_tests.py` (`PB_TESTING=1`) |
