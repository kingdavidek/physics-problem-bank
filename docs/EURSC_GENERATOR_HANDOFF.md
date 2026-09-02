# European School Practice generator — agent handoff

**Track:** Open and curate the main Practice generator for Integrated Science S1–S3 (46 topics).  
**Prerequisite:** Lesson-improvement track complete (Stages 0–7) — see `docs/EURSC_LESSON_IMPROVEMENT_HANDOFF.md`.  
**Visual plan (source of truth for slot recipes):** Cursor canvas `eursc-generator-question-plan.canvas.tsx`.  
**Curriculum / safeguarding:** `docs/EUROPEAN_SCHOOL_SCIENCE.md`, `DISCLOSE_RE` in `scripts/test_es10_whole_suite_smoke.py`.

---

## Copy-paste prompt for the next agent

```
The European School Integrated Science Practice-generator track is COMPLETE (Phases 0–7).

Read first if asked to touch this area:
1. docs/EURSC_GENERATOR_HANDOFF.md
2. docs/EURSC_GENERATOR_REVIEW_RUBRIC.md
3. docs/AI_HANDOFF.md

Do NOT reopen the completed lesson-clarity track (Stages 0–7) or this Practice-generator track unless the user reports a regression.

Do not add eursc to QOTD. Do not add A-Level / Physics / MYP to GENERATOR_LAUNCH_PATHS without an explicit cue. Keep IBL pages outside the generator. Commit only if the user asks.
```

---

## Delivery phases (do one phase per user cue)

| Phase | Name | Scope |
|-------|------|--------|
| **0** | **Baseline and contract** | **Complete** (2026-08-29) — smoke baseline + `docs/EURSC_GENERATOR_REVIEW_RUBRIC.md` |
| **1** | **Explicit standard pools** | **Complete** (2026-08-29) — named five-slot lists; no standard → lesson fallback |
| **2** | **Align to canvas recipes** | **Complete** (2026-08-29) — five-family recipe on all 138 tiers; S1 data/ordered gaps filled |
| **3** | **Launch gate** | **Complete** (2026-08-29) — `GENERATOR_LAUNCH_PATHS` includes `eursc/science`; home + API generate accept it; QOTD still skips eursc |
| **4** | **Safety regression** | **Complete** (2026-08-30) — DISCLOSE_RE clean on 1.4/2.2/2.3.7; IBL not in Practice catalogue; S3 standard slots have no power / no \(V=IR\) calculations |
| **5** | **Matrix smoke** | **Complete** (2026-08-30) — 46×3×5 payloads grader-ready; web/API generate sample (S1, 1.4, S2, 3.1.4); no lesson leak; IBL/QOTD unchanged |
| **6** | **Roll out by year** | **Complete** (2026-08-30) — web/API generate all 46×3; Practice-home desktop + mobile samples (1.4, 2.2, interoception, 3.1.4) |
| **7** | **Verification** | **Complete** (2026-08-30) — sensitive + S3 Practice-home samples; DISCLOSE / IBL / QOTD / no-power invariants; full smoke green |

**Rule:** Complete one phase, report, **stop**. Do not proceed until the user explicitly asks.

---

## Already shipped (lesson track Stage 6 — do not redo blindly)

| Piece | Where |
|-------|--------|
| Five-slot helper | `EURSC_PRACTICE_SLOT_COUNT`, `eursc_resolve_standard_slots()`, `bind_eursc_topic(topic, pools, standard_slots)` in `generators/eursc/science_shared.py` |
| Named lists | `_XX_STANDARD` in `s1_*.py` … `s3_*.py`; lab/es0 converted to `bind_eursc_topic` |
| Slot smoke | `scripts/test_es_practice_slots_smoke.py` (count, no leak, recipe, launch, safety, 690-payload matrix, year-wave, Phase 7 samples) |
| Practice home | **Open** for GCSE Maths, GCSE CS, and `eursc/science` via `GENERATOR_LAUNCH_PATHS` |
| Lesson quizzes | Unchanged full `lesson` pools |

**Track status:** **Complete** (Phases 0–7, 2026-08-30).

---

## Key paths

| Area | Path |
|------|------|
| Canvas plan | `eursc-generator-question-plan.canvas.tsx` (Cursor canvases) |
| Practice helpers | `generators/eursc/science_shared.py` |
| Unit banks | `generators/eursc/s1_*.py` … `s3_*.py` |
| Launch gate | `app.py` — `GENERATOR_LAUNCH_PATHS`, `_normalize_generator_scope` |
| Variant / mode | `generators/shared/variant_utils.py` — `normalize_mode`, queues |
| Lesson quiz | `generators/shared/lesson_quiz.py` (must stay green) |
| ES10 / disclose | `scripts/test_es10_whole_suite_smoke.py` |
| Practice-slot smoke | `scripts/test_es_practice_slots_smoke.py` |
| Full smoke | `scripts/run_smoke_tests.py` (`PB_TESTING=1`) |

---

## Acceptance gate (track complete when)

- All 46 topics expose **exactly five** `standard` variants at each of foundational / intermediate / difficult
- Every generated payload renders and grades on Practice home and API
- Lesson quizzes (10 questions, mixed bank) unchanged in behaviour
- IBL remains practical-support-only; **eursc excluded from QOTD**
- Sensitive-topic scans pass; S3 no power / no V=IR
- Full smoke suite green

---

## What not to do

- Rewrite all 46 lesson templates again
- Put eursc into QOTD
- Invent a parallel 690-item bank from scratch when curation from existing pools works
- Force algebra/SQL/Python graders into science for variety
- Commit unless the user asks
