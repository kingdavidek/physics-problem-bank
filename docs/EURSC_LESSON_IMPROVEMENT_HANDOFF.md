# European School lesson improvement — agent handoff

**Track:** Lesson clarity, examples, diagrams and tables for Integrated Science S1–S3 (46 lessons).  
**Prerequisite:** ES10 curriculum shipped — see `docs/EUROPEAN_SCHOOL_SCIENCE.md`.  
**Out of scope for this track (until Stage 6):** Practice generator admission, five-question curation, QOTD changes.

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

YOUR TASK THIS SESSION: Stage 6 only — “question alignment”.
Do NOT start Stage 7 verification unless the user asks.
When Stage 6 is complete, stop and report. Wait for the user to say “continue” before Stage 7.

Read the review checklist: docs/EURSC_LESSON_REVIEW_RUBRIC.md (Stages 0–5 complete).

Stage 6 deliverables:
1. Five Practice slots per topic per difficulty for `eursc/science` (see generator plan canvas if present).
2. Align Practice-generator items with lesson objectives; do not drop existing lesson-quiz `correct_answer` values unless a stem is actually wrong.
3. Follow ES10 safeguarding: no disclosure prompts; 1.4/2.2 clinical third-person; S3 no power calculations and no \(V=IR\).
4. Run PB_TESTING=1 python scripts/run_smoke_tests.py. Note: Stage 0 saw a rare ES0 flake (unseeded API quiz with no MCQ); re-run scripts/test_es0_mixed_quiz_smoke.py in isolation if it fails.

Hard constraints (all stages):
- Preserve SYLLABUS_MODULES section/checkpoint counts unless the user explicitly approves a manifest change.
- No inline style= on lesson templates; use lesson-shell and existing CSS classes.
- Puberty (1.4) and Health (2.2): clinical, third-person, fictional/public data only — no disclosure prompts (see ES10 DISCLOSE_RE pattern in scripts/test_es10_whole_suite_smoke.py).
- S3 Machines: no power calculations; electric_current has no V=IR.
- IBL pages are practical support only — not lesson rewrites.
- Only commit if the user asks.

End message: “Stage 6 complete. Question alignment: [brief list]. Smoke: [N] tests. Ready for Stage 7 (verification) on your cue.”
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
| **6** | **Question alignment** | **NEXT** — five Practice slots per topic per difficulty (see generator plan canvas) |
| 7 | Verification | Full smoke + manual mobile/dark/print + sensitive-lesson sample |

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
