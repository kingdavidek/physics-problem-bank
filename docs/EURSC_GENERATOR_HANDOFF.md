# European School Practice generator — agent handoff

**Track:** Open and curate the main Practice generator for Integrated Science S1–S3 (46 topics).  
**Prerequisite:** Lesson-improvement track complete (Stages 0–7) — see `docs/EURSC_LESSON_IMPROVEMENT_HANDOFF.md`.  
**Visual plan (source of truth for slot recipes):** Cursor canvas `eursc-generator-question-plan.canvas.tsx`.  
**Curriculum / safeguarding:** `docs/EUROPEAN_SCHOOL_SCIENCE.md`, `DISCLOSE_RE` in `scripts/test_es10_whole_suite_smoke.py`.

---

## Copy-paste prompt for the next agent

```
You are starting the European School Integrated Science Practice-generator track.

Read first (in order):
1. docs/EURSC_GENERATOR_HANDOFF.md          (this file — your scope and rules)
2. docs/EUROPEAN_SCHOOL_SCIENCE.md          (curriculum, safeguarding, launch history)
3. docs/AI_HANDOFF.md                       (repo conventions, smoke tests, do-not-regress)
4. docs/ARCHITECTURE.md                     (generator queues, modes, Practice home)
5. docs/COMPLEX_MECHANISMS.md §1–2          (formats + variant queues) if touching app/queues

Optional visual plan (Cursor canvas — treat as the slot-recipe source of truth):
- eursc-generator-question-plan.canvas.tsx

Do NOT reopen the completed lesson-clarity track (Stages 0–7) unless fixing a regression.

YOUR TASK THIS SESSION: Phase 0 only — “Baseline and contract”.
Do NOT open the Practice home page, change GENERATOR_LAUNCH_*, or rewrite banks yet.
When Phase 0 is complete, stop and wait for my cue before Phase 1.

Phase 0 deliverables:
1. Confirm current state: EURSC_PRACTICE_SLOT_COUNT = 5 and eursc_variants_for_mode() already return five standard slots; lesson mode still returns the full bank; Practice home still GCSE-only; QOTD excludes eursc.
2. Write docs/EURSC_GENERATOR_REVIEW_RUBRIC.md with: the five-slot recipe (MCQ, keyword, data/numeric, ordered, pick/set), canvas coverage matrix summary, rollout by year (S1→S2→S3), acceptance gate, and what Stage 6 already shipped vs what remains.
3. Run PB_TESTING=1 python scripts/run_smoke_tests.py and record the pass line as baseline.
4. Note gaps vs the canvas: kind-mix selection vs explicit named slots; generate() still falls back from standard→lesson; launch gate still GCSE-only boolean.

Hard constraints (all phases):
- Lesson banks (mode=lesson) and 10-question lesson quizzes must keep working; do not drop correct_answer / correct_answer_raw unless a stem is wrong.
- Exactly five standard practice slots per topic per difficulty (46 × 3 × 5 = 690 curated entries — mostly select/rewrite from existing pools, not invent from scratch).
- Slot recipe per tier: (1) MCQ (2) keyword (3) data/numeric (4) ordered process (5) pick/set — match canvas topic rows where practical.
- IBL pages stay outside the generator.
- Keep eursc out of QOTD.
- Puberty (1.4) and Health (2.2): fictional/public/aggregate only — no disclosure prompts (ES10 DISCLOSE_RE).
- S3 Machines: no power calculations; electric_current has no V=IR.
- Only commit if the user asks.

End message: “Phase 0 complete. Baseline: [smoke line]. Rubric: docs/EURSC_GENERATOR_REVIEW_RUBRIC.md. Ready for Phase 1 on your cue.”
```

---

## Delivery phases (do one phase per user cue)

| Phase | Name | Scope |
|-------|------|--------|
| **0** | **Baseline and contract** | **NEXT** — smoke baseline + `docs/EURSC_GENERATOR_REVIEW_RUBRIC.md` |
| 1 | Explicit standard pools | Name five curated slots per topic×difficulty in the nine `generators/eursc` unit modules; `standard` returns exactly those five; **no** fallback from standard → lesson |
| 2 | Align to canvas recipes | Curate/lightly rewrite so each tier matches MCQ / keyword / data / ordered / pick-set intent; align terminology with improved lessons |
| 3 | Launch gate | Replace `GENERATOR_LAUNCH_GCSE_MATHS_CS` boolean with an allowlist including `eursc/science`; fix home selectors, POST, and `problems/generate` validation |
| 4 | Safety regression | Sensitive banks + templates still pass `DISCLOSE_RE`; no QOTD eursc; IBL not in generator |
| 5 | Matrix smoke | Assert 46×3×5 standard variants, unique names, valid payloads, API/web generate, no leakage |
| 6 | Roll out by year | Ship S1, then S2, then S3 (or one allowlist with year-by-year content QA); full smoke + manual desktop/mobile after each year |
| 7 | Verification | Full suite green + sample generate on Practice home for sensitive and S3 topics |

**Rule:** Complete one phase, report, **stop**. Do not proceed until the user explicitly asks.

---

## Already shipped (lesson track Stage 6 — do not redo blindly)

| Piece | Where |
|-------|--------|
| Five-slot helper | `EURSC_PRACTICE_SLOT_COUNT`, `eursc_practice_pool()`, `eursc_variants_for_mode()`, `bind_eursc_topic()` in `generators/eursc/science_shared.py` |
| Wiring | All `s1_*.py` … `s3_*.py` + measurement/lab/es0 fixture variants |
| Slot smoke | `scripts/test_es_practice_slots_smoke.py` |
| Practice home | **Still closed** — `GENERATOR_LAUNCH_GCSE_MATHS_CS = True` |
| Lesson quizzes | Unchanged full `lesson` pools |

**Gaps vs canvas:** slots are a **stable kind-mix sample** of the lesson bank, not yet **explicit named five-slot pools**; `generate()` still falls back to `lesson` when the practice pool is empty; launch allowlist not done.

---

## Key paths

| Area | Path |
|------|------|
| Canvas plan | `eursc-generator-question-plan.canvas.tsx` (Cursor canvases) |
| Practice helpers | `generators/eursc/science_shared.py` |
| Unit banks | `generators/eursc/s1_*.py` … `s3_*.py` |
| Launch gate | `app.py` — `GENERATOR_LAUNCH_GCSE_MATHS_CS`, `_normalize_generator_scope` |
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
