# European School lesson improvement — agent handoff

**Track:** Lesson clarity, examples, diagrams and tables for Integrated Science S1–S3 (46 lessons).  
**Prerequisite:** ES10 curriculum shipped — see `docs/EUROPEAN_SCHOOL_SCIENCE.md`.  
**Out of scope for this track (until Stage 7):** Opening the main Practice home page to `eursc/science`, QOTD changes.

---

## Copy-paste prompt for the next agent

```
You are continuing the European School Integrated Science lesson-improvement track.

Read first (in order):
1. docs/EURSC_LESSON_IMPROVEMENT_HANDOFF.md  (this file — your scope and rules)
2. docs/EUROPEAN_SCHOOL_SCIENCE.md           (curriculum manifest, template rules, safeguarding)
3. docs/AI_HANDOFF.md                        (repo conventions, smoke tests, do-not-regress)
4. docs/ARCHITECTURE.md                      (lesson/quiz architecture if you touch app or shared code)

Optional visual plans (Cursor canvas, if available in the workspace):
- eursc-lesson-quality-plan.canvas.tsx   — lesson-by-lesson priorities and delivery stages 0–7
- eursc-generator-question-plan.canvas.tsx — Practice generator plan (Stage 6)

YOUR TASK THIS SESSION: Track complete (Stages 0–7). Only work further if the user requests follow-ups.

Read the review checklist: docs/EURSC_LESSON_REVIEW_RUBRIC.md (all stages complete).

If the user asks for fixes or polish, scope narrowly and preserve shipped constraints.
```

---

## Step 0 — sync repo (done 2026-08-28)

Active branch was already up to date with origin. `docs/EUROPEAN_SCHOOL_SCIENCE.md` and `generators/eursc/science_shared.py` confirmed present.

```bash
git fetch origin
git status
git pull   # if on a tracking branch and behind
```

---

## Delivery stages (do one stage per user cue)

| Stage | Name | Scope |
|-------|------|--------|
| **0** | **Baseline and rubric** | **Complete** — smoke 62 files (61/1 then ES0 isolated pass); `docs/EURSC_LESSON_REVIEW_RUBRIC.md` |
| **1** | **Shared lesson system** | **Complete** — science hero, figure/figcaption contract, table wrap + scope, aria-live MCQ feedback, gloss CSS, print CSS |
| **2** | **Diagram foundation** | **Complete** — SVG contract tests, measurement ruler/targets on shared helpers, axes/legend/arrow/branch primitives |
| **3** | **S1 pass** | **Complete** (2026-08-29) — 18 S1 lessons; priority 1.1.2, 1.3.3, 1.4.2 |
| **4** | **S2 pass** | **Complete** (2026-08-29) — 17 S2 lessons; priority 2.1.1–2.1.2, 2.2.2, 2.2.4–2.2.5, 2.3.8 |
| **5** | **S3 pass** | **Complete** (2026-08-29) — 11 S3 lessons; priority 3.1.2, 3.1.4–3.1.5, 3.2.1–3.2.4 |
| **6** | **Question alignment** | **Complete** (2026-08-29) — five practice slots per topic per difficulty; lesson banks unchanged for quizzes |
| **7** | **Verification** | **Complete** (2026-08-29) — full smoke + mobile/dark/print sample + sensitive-lesson checks |

**Rule:** Complete one stage, report, **stop**. Do not proceed to the next stage until the user explicitly asks.

---

## Key paths

| Area | Path |
|------|------|
| Curriculum manifest | `generators/eursc/science_shared.py` (`SYLLABUS_MODULES`, `IBL_PAGES`, SVG helpers) |
| Lesson templates | `templates/eursc_science_{slug}_lesson.html` (46) |
| IBL templates | `templates/eursc_science_ibl_*.html` (6) |
| Figure injection | `app.py` — `_lesson_render_spec()` |
| Quiz banks | `generators/eursc/s1_*.py` … `s3_*.py` |
| Practice slots (Stage 6) | `generators/eursc/science_shared.py` — `EURSC_PRACTICE_SLOT_COUNT`, `eursc_variants_for_mode`, `bind_eursc_topic` |
| Practice-slot QA | `scripts/test_es_practice_slots_smoke.py` |
| Stage 7 verification | `scripts/test_es_stage7_verification_smoke.py` |
| Lesson CSS | `static/css/lesson-pages.css`, `static/css/components.css`, `static/css/diagrams.css` |
| SVG kit | `models/svg_kit.py` |
| Whole-suite QA | `scripts/test_es10_whole_suite_smoke.py` |
| Sensitive regression | `DISCLOSE_RE` in `scripts/test_es10_whole_suite_smoke.py` |
| Full smoke | `scripts/run_smoke_tests.py` (`PB_TESTING=1`) |

---

## Review themes (for the rubric and later edits)

- **Language:** S1 concrete; S2 models and evidence; S3 mechanism then apply. Gloss hard terms on first use.
- **Examples:** One worked example per hard idea (with units where relevant).
- **Figures:** Visible caption; named axes/units; arrows/labels; not colour-only.
- **Quick checks:** Test the section idea; plausible misconceptions; limit joke distractors.
- **Safeguarding:** No first-person health, body, diet, sexuality, or substance-use questions.

---

## What not to do (unless a later stage says so)

- Rewrite all 46 lessons in one session
- Change checkpoint/section counts without approval
- Enable `eursc/science` on the Practice home page only as Stage 6 specifies
- Add QOTD entries for `eursc`
- Regress ES10 smoke tests or disclosure scans

---

## When Stage 6 is done

Report Practice-slot / generator alignment, smoke result, and wait for the user before Stage 7.

## Stage 6 question alignment (shipped 2026-08-29)

| Piece | Where |
|-------|--------|
| Five practice slots per tier | `EURSC_PRACTICE_SLOT_COUNT = 5`; `eursc_practice_pool()` picks a stable MCQ + typed mix |
| Lesson bank unchanged | `mode='lesson'` still returns the full pool (≥10 items/tier) for ten-question quizzes |
| Shared bind | `bind_eursc_topic()` in `science_shared.py`; all `s1_*.py` … `s3_*.py` banks use it |
| Practice home | Still GCSE maths/CS only (`GENERATOR_LAUNCH_GCSE_MATHS_CS`); slots are backend-ready |
| Stem tweaks | Measurement accuracy/precision; S3 energy transform/transfer; electric_current conventional-current wording |
| Tests | `scripts/test_es_practice_slots_smoke.py`; ES1–ES10 smokes green |

## When Stage 7 is done

Report verification results. The lesson-improvement track (Stages 0–7) is complete unless the user requests follow-ups.

## Stage 7 verification (shipped 2026-08-29)

| Piece | Result |
|-------|--------|
| Full smoke | **65/65** smoke files green (`PB_TESTING=1 python scripts/run_smoke_tests.py`) |
| ES suite | ES0–ES10, practice slots, SVG contract, Stage 7 sample — all pass in isolation |
| Mobile sample | Viewport meta, `lesson-shell`, 700px/900px breakpoints, `lesson-table-wrap` on measurement, reproductive_anatomy, dependence_addiction, ecosystems_cycles |
| Dark sample | `tokens.css` dark tokens + `theme.js` `pb_theme`; lesson SVG remaps via CSS variables |
| Print sample | `@media print` expands lesson sections in `lesson-pages.css` |
| Sensitive sample | No `DISCLOSE_RE` hits on 1.4 (`reproductive_anatomy`) and 2.2 (`dependence_addiction`) templates or rendered HTML |
| Practice / quizzes | Home still GCSE-only; five practice slots per tier; ten-question lesson quizzes on sample topics |
