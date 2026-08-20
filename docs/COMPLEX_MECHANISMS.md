# Problem Bank — Three complex mechanisms

**Last updated:** 2026-08-15  
**Audience:** Developers and AI agents who already know the product overview  
**Companion docs:** `docs/ARCHITECTURE.md` (system map), `docs/AI_HANDOFF.md` (start here), `docs/SOLID_DRAFT_SECURITY.md` (trust boundaries)

This document explains **the three hardest, most cross-cutting parts** of Problem Bank: how they are structured, and what **Flask / Python / Jinja / JavaScript / CSS** each contribute.

These are not the only complex areas (lesson quizzes, Quick Test, and Pyodide each deserve their own deep dive), but they are the ones every major feature depends on.

| Rank | Mechanism | One-line summary |
|------|-----------|------------------|
| **1** | Typed auto-grading + session trust | Browser collects an answer; server grades against session-stored truth |
| **2** | Generator + variant queues + problem payload | Curriculum registry → procedural problem → queue state → page/API payload |
| **3** | Phase G learning pipeline | Attempt history → weak topics → due queue / exam plan / skill gaps |

---

## Layer roles (how to read the rest)

| Layer | What it does in this app |
|-------|---------------------------|
| **Flask (`app.py`)** | HTTP routes, sessions, CSRF/CSP, SQLite schema, JSON API, wiring models ↔ templates |
| **Python (generators / models)** | Pure-ish business logic: make questions, compare answers, score weakness, sync queues |
| **Jinja templates** | Server-rendered HTML shell; embed problem HTML and grading metadata as `data-*` attributes |
| **JavaScript (`static/js/`)** | Collect user input, call `/api/v1/*`, update feedback UI, reflections, some client-only grading (Pyodide) |
| **CSS (mostly in `templates/base.html`)** | Layout and interaction styling for forms, problem cards, free-response widgets, profile panels — little logic |

---

# Mechanism 1 — Typed auto-grading and session trust

## Why this is hard

A single “Check” button has to support ~35 answer encodings (`number`, `fraction`, `algebraic`, `number_fields`, `sql`, `python_run`, `proof_steps`, …). The UI must serialize multi-box answers into one string the checker understands. The server must **not trust** the client for correctness (especially SymPy types), while still giving fast, clear feedback.

## End-to-end flow

```text
Generate / load problem
        │
        ▼
Flask stores slim grading keys in session
  last_problem_payload.problem.{correct_answer_raw, answer_type, …}
        │
        ▼
Jinja renders free_response_inline.html
  (inputs + data-* metadata)
        │
        ▼
JS (site.js) gathers fields → POST /api/v1/problems/check
        │
        ▼
Flask resolves correct raw/type from SESSION (preferred)
        │
        ▼
Python check_answer(answer_type, raw, user) → feedback JSON
        │
        ├── optional: record attempt / streak / cohort
        └── optional: JS shows reflection chips (Phase G4)
```

## What each layer does

### Flask

- **`POST /api/v1/problems/check`** (`api_v1_problems_check` in `app.py`):
  - Cap `user_answer` length.
  - If `session['last_problem_payload'].problem` has `correct_answer_raw` → **session-bound** grading; reject mismatched client raw/type (`403 session_mismatch`); allow multipart `number_fields` partial checks via `part_index`.
  - If no session problem → allow client raw/type **except** SymPy types (`algebraic`, `quadratic_roots`) which return `400 session_required`.
- **`POST /api/v1/generator/mcq-answer`**: compares letter to session `correct_answer` (never a client `correct` boolean).
- **`_sync_last_problem_payload` / `_slim_problem_for_session`**: keep cookie sessions under size limits by dropping SVG/huge HTML while keeping grading keys.
- CSRF on cookie-session API writes; Bearer tokens exempt.

### Python (graders)

- **`generators/shared/answer_checkers.py`**
  - Registry: `@register_checker('…')` → `CHECKERS` map.
  - Entry: `check_answer(answer_type, correct_raw, user_answer)` → `{correct, feedback, normalized_user, normalized_correct, …}`.
  - SymPy path uses **`_safe_sympify`** (allowlisted `parse_expr`), never bare `sympify` on untrusted strings.
- Helpers: `sql_checker.py` (token compare / LCS score), `text_keywords.py`.
- Payload builders in `generators/shared/utils.py` (`graded_answer_*`, `problem_extra_from_graded_answer`) attach `correct_answer_raw` + `answer_type` (+ UI hints) when generators create problems.

### Jinja

- **`templates/partials/free_response_inline.html`**: huge conditional tree of input layouts (standard form, pairs, fields, proof step banks, Python starter, …).
- Embeds **metadata for JS**, not the final grade:
  - `data-correct-raw`, `data-answer-type`, `data-field-types`, `data-step-bank`, `data-answer-tests`, topic ids, etc.
- Included from `index.html`, Quick Test, saved/shared views.

### JavaScript

- **`static/js/site.js`**:
  - Reads the free-response block, builds the canonical `user_answer` string (e.g. `coeff|exp`, pipe-joined fields, proof step ids).
  - `fetch('/api/v1/problems/check', { headers: apiHeaders(…), body: JSON })` with CSRF.
  - Paints feedback / step hints; may open reflection UI after a wrong answer.
- **`static/js/python-run-grader.js`** (+ worker): for `python_run`, runs student code **in the browser** via Pyodide, then posts captured stdout JSON for the server to compare. The server does **not** `eval` student code.

### CSS

- Free-response rows, field stacks, Check button, correct/wrong colours live under `.free-response-*` in `base.html`.
- Pure presentation: grid of inputs, MCQ buttons, feedback text weight — no grading rules in CSS.

## Mental model

| Trusted | Untrusted |
|---------|-----------|
| Session `correct_answer_raw` / `answer_type` / MCQ letter | Client’s claimed correctness |
| Server `check_answer` result | Client-chosen SymPy type without session |
| Pyodide stdout as *input to* server compare | Pyodide as authority of record |

## Key files

`app.py` (check/MCQ APIs, session sync) · `generators/shared/answer_checkers.py` · `templates/partials/free_response_inline.html` · `static/js/site.js` · `static/js/python-run-grader.js` · `docs/SOLID_DRAFT_SECURITY.md`

---

# Mechanism 2 — Generator, variant queues, and problem payloads

## Why this is hard

Practice content is **procedural**, not a fixed bank. Many topics expose dozens of **named variants**. The app must walk a shuffled queue without repeats until exhausted, support “new numbers” rerolls of the same variant, work for anonymous (session-only) and logged-in (SQLite-backed) users, and produce a **problem dict** that both Jinja and the JSON API can render — while leaving grading keys ready for Mechanism 1.

## End-to-end flow

```text
User picks level / subject / topic / mode / difficulty
        │
        ▼
Flask resolves TOPICS[level][subject][topic]
        │
        ├── has variants_func?
        │     yes → build/advance name queue (session ± DB)
        │           call func(difficulty, mode, variant_name=…)
        │     no  → call func(difficulty, mode)
        ▼
Generator returns HTML + optional graded extras
        │
        ▼
make_problem(…) normalises dict
        │
        ├── store last_problem_payload (Mechanism 1)
        └── render index.html  OR  return _problem_client_payload JSON
```

## What each layer does

### Flask

- Web: **`POST /`** (`index`) with CSRF — actions `start` / `next` / `reroll`.
- API: **`POST /api/v1/problems/generate`**.
- Orchestration helpers:
  - `_selection_key` → `"level|subject|topic|mode|difficulty"`
  - `_build_problem_queue` → list of variant **function names** from `variants_func`
  - `_load_queue_state` / `_persist_queue_state` → dual write: cookie session + `user_problem_queues` table when logged in
  - `_generate_queued_problem`, `_reroll_current_problem`
- Rate limits generate attempts (per user or IP).
- Returns HTML page or JSON `{ problem, selection: { variant_name, queue_position, … } }`.

### Python (generators)

- **`topic_registry.py`**: canonical map  
  `TOPICS[level][subject][topic] → { name, func, variants_func? }`.
- Topic modules under `generators/gcse/`, `alevel/`, `myp/` implement `func` / `variants_func`.
- **`generators/shared/variant_utils.py`**: pick named variant, randomisability for reroll.
- **`generators/shared/utils.py` → `make_problem`**: stamps level/subject/topic, marks, URLs, merges graded extras / MCQ option shuffle.
- Lesson quizzes and Quick Test **reuse** the same generators (`lesson_quiz.py`, `models/quicktest.py`) rather than inventing a second problem engine.

### Jinja

- **`templates/index.html`**: selection form + problem card (`|safe` / `format_question_html` for authored HTML/MathJax markup).
- Includes free-response / answer-hint partials when `correct_answer_raw` is present.
- Queue UI: “New numbers”, Quick Test start — secondary forms with their own CSRF fields.

### JavaScript

- Home page is mostly **classic form POST** (full page reload).
- API / PWA clients use `site.js` generate/next/reroll against `/api/v1/problems/generate` and then mount free-response/MCQ from JSON fields.
- Dropdown cascading (level → subject → topic) is JS/DOM filtering of `<option data-level>` attributes.

### CSS

- `.form-card`, `.form-grid`, `.problem-card`, badges, answer `<details>` disclosure — structure the generator UX.
- Does not know about queues or variants.

## Important data

**Problem dict (core):** `question`, `solution`, `hint`, `difficulty`, `marks`, `level`, `subject`, `topic`, optional MCQ `options`/`correct_answer`, optional grading `correct_answer_raw`/`answer_type`/`answer_*`.

**Queue state:**

| Store | Keys / columns |
|-------|----------------|
| Session | `problem_queue_key`, `problem_queue`, `problem_index`, `problem_variant_name` |
| SQLite | `user_problem_queues(user_id, queue_key, queue_json, queue_index, variant_name)` |

## Mental model

Think of the registry as a **catalogue of factories**. Flask is the **dispatcher + queue cursor**. Generators are **pure content factories**. Templates/JS are **renderers** of the resulting dict. Grading (Mechanism 1) is a separate concern that only needs the grading keys left on the dict and in session.

**Mode:** every entry point passes the requested mode through `normalize_mode()` before touching a queue or a generator. It recognises `standard` (with legacy `revision`/`exam`/`practice` aliases), `mcq`, and `lesson`; **anything else silently becomes `standard`**. Adding a mode means changing that function first — see `docs/REAL_WORLD_QUESTIONS.md` for the planned `real_world` style.

## Key files

`topic_registry.py` · `generators/**` · `generators/shared/utils.py` · `generators/shared/variant_utils.py` · `models/problem_queue.py` · `app.py` (index + generate) · `templates/index.html`

---

# Mechanism 3 — Phase G learning pipeline

## Why this is hard

After enough practice, the product must answer: *what should this learner revisit, when, and how?* That requires aggregating heterogeneous attempt tables, applying thresholds, syncing a spaced “due today” list, folding optional reflections into skill patterns, and (G7) packing weak topics into an exam calendar — **without a background job**. Everything is **compute-on-read** when the profile or `/api/v1/me/*` is hit.

## End-to-end flow

```text
Practice events
  quiz_attempts  +  generator_mcq_attempts  (+ optional reflections)
        │
        ▼
G1 analyze_weak_topics  →  ranked weak list + reasons
        │
        ├──────────────┬────────────────────┐
        ▼              ▼                    ▼
G3 sync_revision_queue   G7 build_revision_plan   (profile SSR / APIs)
   due dates by severity   max 2 topics/day to exam
        │
        ▼
Due today widget  ·  Exam plan card  ·  Skill gaps (G6 from reflections)
```

Wrong Check/MCQ (Mechanism 1) can open reflection chips → `user_wrong_answer_reflections` → G4/G6.

## What each layer does

### Flask

- Profile route loads the same helpers the APIs use (single source of truth).
- APIs (all under `/api/v1/me/…`, login required):
  - `GET weak-topics`
  - `GET revision-queue` (+ `POST …/complete`, `…/dismiss`)
  - `GET|POST reflections`
  - `GET skill-gaps`
  - `GET|PUT|DELETE revision-plan`
- Records study activity / streaks when grading paths succeed (feeds gamification and digests).

### Python (models)

| Phase | Module | Job |
|-------|--------|-----|
| **G1** | `models/weak_topics.py` | Aggregate quiz avg + MCQ accuracy per topic; flag below ~70% with min samples; `weakness_score` |
| **G2** | `models/user_data.py` | Paginated attempt history |
| **G3** | `models/revision_queue.py` | On read: insert/update/drop queue rows from current weaks; due-in 2/4/7 days by severity |
| **G4** | `models/reflections.py` | Store chip + note after wrong answers |
| **G5** | `models/cohort_stats.py` | Anonymous “X% got this wrong” (hooked from check) |
| **G6** | `models/skill_gaps.py` | Roll up reflection `prompt_type` across topics |
| **G7** | `models/revision_planner.py` | Spread scoped weaks across days before exam (`MAX_TOPICS_PER_DAY = 2`) |

Day keys and lookbacks use **UTC** (aligned with rate limits / streaks after solid-draft hardening).

### Jinja

- **`templates/profile.html`**: server-rendered sections — Topics to revisit, Due today, Skill patterns, Exam revision plan forms.
- Mostly HTML forms for plan save/clear; due-today can also be driven by fetch.

### JavaScript

- **`site.js`**: reflection panel after wrong graded answers; revision-queue complete/dismiss via fetch + CSRF.
- Profile is not a SPA — JS enhances islands, Flask owns the data load.

### CSS

- Profile panels reuse `.section-panel`, badges, form layouts from `base.html`.
- Visual hierarchy only; scheduling math is all Python.

## Mental model

| Piece | Role |
|-------|------|
| Attempt tables | Raw evidence |
| G1 | Sensor (“what’s weak?”) |
| G3 | Inbox (“what’s due?”) |
| G7 | Calendar (“before this exam”) |
| G4/G6 | Qualitative layer (“why / which skill pattern?”) |
| Flask | Auth gate + HTTP |
| Jinja/JS | Display and light mutations |

No cron is required for queue sync; opening profile or calling the API refreshes state.

## Key files

`models/weak_topics.py` · `revision_queue.py` · `revision_planner.py` · `reflections.py` · `skill_gaps.py` · `app.py` (`/api/v1/me/*`, profile) · `templates/profile.html` · `static/js/site.js`

---

## How the three connect

```text
Mechanism 2 (generate)
        │
        ├──► Mechanism 1 (check / MCQ)
        │         │
        │         └──► attempt rows + optional reflections
        │                     │
        └─────────────────────┴──► Mechanism 3 (weak → due → plan)
```

Quick Test and lesson quizzes are **batch wrappers** around Mechanism 2 (and MCQ submit), then sync into Mechanism 1’s session payload so Check still works question-by-question.

---

## Related but not expanded here

| Area | Relationship |
|------|----------------|
| **Pyodide / `python_run`** | Client execution branch of Mechanism 1 |
| **Lesson MCQ quiz** | Fixed 10-question builder over generators + session answers |
| **Quick Test** | Multi-question session using generate + `_sync_last_problem_payload` |
| **Social / PWA** | Orthogonal product surfaces; do not drive grading math |

---

## Maintenance tips

1. New graded question type → register a checker **and** a free-response Jinja/JS serialization path; keep session binding rules.
2. New topic → registry + generator (+ `variants_func` if queued); do not fork a second payload shape.
3. New learning signal → prefer feeding G1/G4 inputs over inventing a parallel analytics store.
4. After JS/CSS that is cached, bump `site.js?v=` and `CACHE_VERSION` in `static/js/sw.js`.
