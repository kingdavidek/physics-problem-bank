# Problem Bank — Architecture & Product Overview

**Last updated:** 2026-08-24  
**Repository:** `maths_generator/physics-problem-bank`  
**Audience:** Developers, AI agents, and technical stakeholders  

This document describes **what Problem Bank is today**: product goals, system architecture, major features, data model, and how the pieces fit together.

**AI agents:** start with `docs/AI_HANDOFF.md`, then this file, then `docs/SOLID_DRAFT_SECURITY.md` before changing auth/grading/sessions. API: `docs/API.md`. Deploy: `docs/DEPLOY.md`. Planned work (incl. G8): `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md`. Phase U graphics: `models/svg_kit.py` and `docs/UI_REDESIGN.md` §8.

---

## 1. Product vision and goals

### 1.1 What Problem Bank is

Problem Bank is a **free curriculum problem bank** for secondary and early post-16 study. Learners browse revision content, generate fresh exam-style questions with instant worked solutions, and optionally create an account to track progress, save work, and study with friends.

**Primary audiences:** GCSE, A-Level, and IB MYP students studying **maths**, **physics**, and **computer science**.

**Core value proposition:**

- **Learn** — topic pages with explanations, formulae, worked examples, and embedded quick checks.
- **Practise** — unlimited generated questions at chosen difficulty and mode (written or MCQ).
- **Check** — instant auto-grading for typed answers and MCQs, with hints and model solutions.
- **Improve** — logged-in users get weak-topic detection, spaced revision, reflections, and exam planning (Phase G).

### 1.2 Design principles (as implemented)

| Principle | How it shows up |
|-----------|-----------------|
| **Same backend, web + API** | Flask serves Jinja templates and `/api/v1/*` JSON for PWA and future native clients |
| **Generator-first** | Most practice content is procedurally generated, not a fixed question bank |
| **Progressive account value** | Anonymous use is supported; accounts unlock difficult tier, saves, history, social, analytics |
| **Privacy-aware social** | Follows, visibility settings, blocks; peer features are opt-in and separate from authority roles |
| **Forward-compatible schema** | SQLite tables created with `CREATE IF NOT EXISTS`; no migration framework required for typical releases |

### 1.3 What Problem Bank is not

- Not a full LMS (no course authoring, timetabling, or school MIS integration today).
- Not a live tutoring or chat platform (study pairs are accountability buddies, not messaging).
- Not a paid subscription product in current code (free accounts, optional email digest).

---

## 2. Technology stack

| Layer | Technology | Notes |
|-------|------------|-------|
| **Runtime** | Python 3.12+ | CI uses 3.12 |
| **Web framework** | Flask 3.1.x (pinned in `requirements.txt`) | Single main app in `app.py` |
| **Auth** | Flask-Login + Werkzeug password hashing | Session cookies + Bearer API tokens (default 90-day expiry) |
| **Database** | SQLite | Local `data/quicktest.db` (**gitignored**); schema init inline in `app.py`; WAL |
| **Math / grading** | SymPy (pinned) | Safe allowlisted parsing only — never bare `sympify` on untrusted input |
| **Templates** | Jinja2 | HTML under `templates/` (lessons are `*_lesson.html`; generator snippets live in `scripts/legacy/`) |
| **Frontend CSS** | Token-first sheets in `static/css/` | `tokens.css` first; `lesson-pages.css` and lesson-assist CSS are lesson-only (U8.6) |
| **Frontend JS** | Vanilla JavaScript | `static/js/site.js` and feature modules |
| **Math rendering** | MathJax | `static/js/mathjax-config.js` |
| **CS Python grading** | Pyodide (in-browser) | `python-run-grader.js`, worker for write-code questions |
| **PWA** | Service worker + manifest | Offline shell; API always network-only. **M0–M4 done** (standalone chrome, install/A2HS, device QA) — `docs/MOBILE.md`. M5–M7 need production HTTPS |
| **Optional AI** | DeepSeek / OpenAI | Lesson/quiz assist via env-configured keys |
| **Optional email** | Resend / SendGrid / SMTP | Weekly digest (`docs/EMAIL_SETUP.md`) |
| **Deployment** | PythonAnywhere (documented) | WSGI entry: `from app import app as application` |

**Legacy note:** `flask_app.py` is an early prototype with two topics only. Production uses `app.py`.

---

## 3. High-level system architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Clients                                   │
│  Browser (Jinja pages) │ PWA │ Native app (Bearer token)        │
└───────────────┬─────────────────────────────────────────────────┘
                │ HTTP(S)
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     app.py (Flask)                               │
│  Routes │ CSRF/CSP/CORS │ Session │ API v1 │ PWA endpoints      │
└───────┬─────────────────────────────────────────────────────────┘
        │
        ├──────────────┬──────────────┬──────────────┬──────────────┐
        ▼              ▼              ▼              ▼              ▼
   topic_registry   generators/    models/      templates/    static/js
   topics_data.py   shared/        (SQLite)     Jinja HTML    PWA, UI
                    answer_checkers
        │              │              │
        └──────────────┴──────────────┴──► data/quicktest.db
```

### 3.1 Request flow — generate and check

1. User selects level / subject / topic / difficulty / mode on `/` or via API.
2. `app.py` resolves generator from `topic_registry.py` → `TOPICS[level][subject][topic]`.
3. Generator callable returns a **problem dict** (`question`, `solution`, optional grading fields).
4. Problem stored in session as **slim** `last_problem_payload` (grading keys; bulky SVG/HTML dropped) for web check/MCQ trust.
5. **MCQ:** client posts chosen letter → `POST /api/v1/generator/mcq-answer` → **server** compares to session `correct_answer`.
6. **Free response:** client posts typed answer → `POST /api/v1/problems/check` → `check_answer()`; SymPy-backed types require session metadata.
7. Logged-in users: attempts recorded; Phase G features (weak topics, reflections, cohort stats) consume this data.

### 3.2 Curriculum map

The canonical topic tree lives in **`topic_registry.py`**:

```
TOPICS[level][subject][topic] → { name, func, variants_func? }
```

Static lesson copy (titles, summaries, formulae, tips) lives in **`topics_data.py`**.

| Level | Subjects (implemented) | Approx. scale |
|-------|------------------------|---------------|
| **gcse** | maths (~30 topics), physics (2), cs (10) | Largest coverage |
| **alevel** | physics (magnetism, photoelectric, particles) | 3 topics |
| **myp** | chemistry (redox, energy_changes_and_rates) | 2 topics |

---

## 4. Repository layout

| Path | Role |
|------|------|
| **`app.py`** | Main application: routes, DB schema, serializers, API v1, web UI |
| **`topic_registry.py`** | Topic catalog → generator functions |
| **`topics_data.py`** | Lesson/revision metadata per topic |
| **`models/`** | Business logic and persistence helpers. Diagrams: `models/svg_kit.py` (Phase U5) |
| **`generators/`** | Problem generators by curriculum level |
| **`generators/shared/`** | Answer checkers, lesson quiz builder, variant utils, lesson assist |
| **`templates/`** | Jinja2 pages (lessons, generator, profile, social) |
| **`static/`** | CSS (`static/css/tokens.css` first; `lesson-pages.css` / lesson-assist CSS are lesson-only), JavaScript, PWA, icons, SW. Contrast/ARIA smokes: `scripts/test_contrast_smoke.py`, `scripts/test_u8_a11y_smoke.py` |
| **`scripts/`** | Smoke tests, maintenance, email digest |
| **`docs/`** | API, deploy, architecture, future ideas |
| **`data/quicktest.db`** | SQLite database (local/dev only; **not in git**; backup in production) |

---

## 5. Core features (as shipped)

### 5.1 Content and practice

| Feature | Entry points | Key modules |
|---------|--------------|-------------|
| **Topic browser** | `/topics`, `/topic/<l>/<s>/<t>` | `topics_data.py`, lesson templates |
| **Diagrams (`svg_kit`)** | lessons, generator questions, `/styleguide`, profile progress | `models/svg_kit.py` (Phase U5) |
| **Motion / celebration** | MCQ + generator check, profile streak ring, `/styleguide#motion` | `static/js/celebrate.js`, motion tokens in `tokens.css` (Phase U7) |
| **Question generator** | `/`, `POST /api/v1/problems/generate` | `topic_registry.py`, `generators/` |
| **Quick Test** | `/quicktest/*`, API v1 quicktest | `models/quicktest.py` |
| **Lesson quizzes** | `/lesson-quiz/*`, API v1 lesson-quiz | `generators/shared/lesson_quiz.py`, `models/lesson_quiz.py` |
| **Saved problems** | `/saved-problems`, API v1 saved-problems | `models/user_data.py` (cap 200) |
| **Variant queue** | Per-user persisted queue | `models/problem_queue.py`, `variant_utils.py` |

### 5.2 Auto-correct (grading)

**Status:** Fully complete for Phase A (GCSE CS) and Phase B (GCSE Maths), including Python write-code via Pyodide.

| Component | Location |
|-----------|----------|
| Checker registry | `generators/shared/answer_checkers.py` |
| Entry point | `check_answer(answer_type, correct_raw, user_answer)` |
| Check API | `POST /api/v1/problems/check` |
| MCQ API | `POST /api/v1/generator/mcq-answer` |
| SQL grading | `generators/shared/sql_checker.py` |
| Keyword text | `generators/shared/text_keywords.py` |
| Python run | Client Pyodide + `python_run` checker type |

**Registered answer types include:** `number`, `fraction`, `algebraic`, `surd`, `quadratic_roots`, `vector`, `sql`, `python_run`, `keyword`, `mcq`, `proof_steps`, and many more (see `docs/API.md`).

**Session binding:** When `last_problem_payload` contains grading keys, the server grades against stored values and rejects client mismatches (403 `session_mismatch`). Types `algebraic` and `quadratic_roots` **require** a session problem (`session_required` if missing). See `docs/SOLID_DRAFT_SECURITY.md`.

### 5.3 Accounts and profile

| Feature | Notes |
|---------|-------|
| **Registration** | Email, handle (`^[a-z0-9_]{3,20}$`), password; age 13+ |
| **Login** | Web session + optional 30-day remember; API Bearer tokens |
| **Profile dashboard** | `/profile` — saves, progress, quizzes, streaks, Phase G widgets |
| **Settings** | Visibility, auto-share, notifications, token revoke |
| **Lesson progress** | Bookmark position per topic |
| **Practice streak** | Updated on graded attempts |

### 5.4 Social and gamification

| Feature | Module | Notes |
|---------|--------|-------|
| **Follow / unfollow** | `models/social.py` | Activity feed for followed users |
| **Profile visibility** | `models/social.py` | `public`, `followers_only`, `private` |
| **Share question** | `models/sharing.py` | Cap 200 shared |
| **Suggest question** | `models/sharing.py` | Inbox cap 100 |
| **Friend challenges** | `models/challenges.py` | Same MCQ set, compare scores |
| **Study pairs** | `models/study_pairs.py` | One active buddy; weekly recap |
| **Question of the Day** | `models/qotd.py`, `models/bot.py` | One **difficult** MCQ per UTC day + today and 7-day friend leaderboards (E5.3); `@problem_bot` feed card (E1). Counts for study streak only — not topic / MCQ history. Wrong answers show the worked solution. |
| **Lesson keyword search** | `models/lesson_search.py` | SQLite FTS5 over `topics_data.py` plus stripped `*_lesson.html` pages (E2) |
| **Avatars** | `models/avatar.py` | Emoji + colour JSON on `user_profile_settings.avatar_json` (E2). Extras 🎓/🎧/⭐ gated on milestones (E5.5) |
| **Alien buddy** | `models/buddy.py` | Corner widget (E3 + E5.1): types `milestone`, `celebrate`, `qotd_nudge`, `streak_risk`, `weak_topic`, `friend_challenge`, `nudge`; per-type face emoji. Server HTML embed + `study-buddy.js`. On weak topic’s lesson page: **Practise MCQ** / **Take a quiz** / **Keep learning**; refetches after generator MCQ. Milestone dismiss: `pb-buddy-milestone-<key>` via **Not now** or **View badges**. `friend_challenge` links to a followed friend's profile. Off-page **Not now** = UTC day; on-page **Keep learning** = per-topic per day |
| **Streaks & milestones** | `models/gamification.py` | UTC study-day streak; ten-badge `MILESTONE_CATALOG` (incl. QOTD and friends-only accuracy) shown on the profile with catalog emoji. Awarded via `evaluate_milestones` on any study activity |
| **Friend leaderboard** | `models/gamification.py` | Effort points and weekly quiz+MCQ accuracy (friends only) |
| **Notifications** | `models/notifications.py` | In-app events |
| **Block / report** | `models/moderation.py` | User safety |

Social features are **peer-to-peer**. There is no teacher role or class roster today.

### 5.5 Phase G — Learning depth (G1–G7)

Orthogonal to auto-correct; builds on attempt history and reflections.

| Phase | Name | Purpose | Key file |
|-------|------|---------|----------|
| **G1** | Weak topics | Rank topics where quiz avg & MCQ accuracy fall below thresholds | `models/weak_topics.py` |
| **G2** | Quiz history | Paginated lesson quiz + generator MCQ attempt lists | `models/user_data.py` |
| **G3** | Revision queue | Rule-based spaced queue synced from weak topics; Due today widget | `models/revision_queue.py` |
| **G4** | Wrong-answer reflections | Optional chips + note after wrong Check/MCQ | `models/reflections.py` |
| **G5** | Cohort stats | Anonymous “X% got this wrong” after ≥20 samples | `models/cohort_stats.py` |
| **G6** | Skill gaps | Cross-topic roll-up of reflection chip types | `models/skill_gaps.py` |
| **G7** | Revision planner | Spread weak topics across days before an exam date | `models/revision_planner.py` |

**Profile sections:** Topics to revisit, Due today, Skill patterns, My reflections, Exam revision plan.

**APIs:** Documented in `docs/API.md` under `/api/v1/me/weak-topics`, `revision-queue`, `reflections`, `skill-gaps`, `revision-plan`, `quiz-attempts`.

**Smoke tests:** `scripts/test_phase_g1_smoke.py` through `test_phase_g7_smoke.py`.

### 5.6 PWA and API v1

| Feature | Path |
|---------|------|
| Manifest | `/manifest.webmanifest` |
| Service worker | `/sw.js` (cache-first static, network-only API) |
| Offline page | `/offline` |
| Health check | `GET /api/v1/health` |
| Full API surface | ~70 endpoints — see `docs/API.md` |

Auth: session cookie (same-origin) or `Authorization: Bearer pb_…`.

---

## 6. Data model (overview)

Schema is created in `app.py` on startup. Major table groups:

### 6.1 Users and auth

- `users` — id, email, handle, password_hash, created_at, is_active
- API tokens managed via `models/api_tokens.py`

### 6.2 Practice and progress

- `saved_problems`, `lesson_progress`, `quiz_attempts`, `generator_mcq_attempts`
- `user_problem_queues` — variant queue state
- Quick test and lesson quiz session data (session + persisted attempts)

### 6.3 Social

- `follows`, `user_profile_settings` (including `avatar_json`, `show_accuracy_leaderboard`), `activity_events`
- `shared_questions`, `question_suggestions`
- `quiz_challenges`, `study_pairs`, `qotd_attempts`
- `user_blocks`, notifications tables
- `lesson_search_fts` / `lesson_search_meta` — FTS5 lesson keyword index (E2)

### 6.4 Phase G

- `user_wrong_answer_reflections` — G4/G6
- `problem_cohort_stats` — G5 anonymous aggregates
- `user_revision_plans` — G7
- Revision queue state (G3) — see `models/revision_queue.py`

Weak topics (G1) are computed at read time from attempt tables, not stored separately.

---

## 7. Generator contract

Each topic registers a callable:

```python
func(difficulty, mode, variant_name=None)
# difficulty: foundational | intermediate | difficult
# mode: standard | mcq | lesson
```

Returns a dict with at least `question` and `solution`. Graded problems add:

- `correct_answer_raw` — canonical answer for checking
- `answer_type` — registry key for `check_answer()`
- Optional: `options` (MCQ), `hint`, `answer_format_hint`, multipart fields

Optional `variants_func(difficulty, mode)` provides named variants (typically 7 per tier) for queue diversity.

`normalize_mode()` (`generators/shared/variant_utils.py`) maps legacy `revision`/`exam`/`practice` onto `standard` and collapses anything unrecognised to `standard`. A planned fourth mode, `real_world`, is specified in `docs/REAL_WORLD_QUESTIONS.md`.

Lesson quizzes (`generators/shared/lesson_quiz.py`): 10 questions — 3 foundational + 4 intermediate + 3 difficult — where MCQ mode is supported.

---

## 8. Security and operational concerns

**Full solid-draft write-up:** `docs/SOLID_DRAFT_SECURITY.md` (SymPy RCE fix, session trust, CSRF, SECRET_KEY, git hygiene).

| Area | Implementation |
|------|----------------|
| **SECRET_KEY** | Required non-default outside testing; `PB_ALLOW_DEV_SECRET=1` local-only |
| **SymPy grading** | Allowlisted safe parser; check API session-bound for SymPy types |
| **CSRF** | Web forms + cookie-session `/api/*` mutations; Bearer / `PB_TESTING` exempt |
| **CSP** | Content-Security-Policy on responses; MathJax/Pyodide still need unsafe-eval/wasm; CDN SRI where applied |
| **Rate limits** | Daily UTC buckets per user or IP (`models/rate_limit.py`); web auth included |
| **Cookies** | HttpOnly, SameSite=Lax; Secure when HTTPS / `SESSION_COOKIE_SECURE` |
| **CORS** | Optional `CORS_ORIGINS` for separate frontends |
| **DB** | Request-scoped connections, WAL, busy_timeout; DB files gitignored |
| **Testing** | `PB_TESTING=1` → ephemeral DB + limit/CSRF exemptions (smoke only) |
| **CI** | `.github/workflows/smoke.yml` runs all `scripts/test_*_smoke.py` |

---

## 9. Key user flows (web)

| Flow | Route(s) |
|------|----------|
| Browse → generate | `/topics` → `/topic/...` → `/` |
| Quick Test | Generate → Quick Test → 10 questions → results |
| Lesson quiz | Topic page → lesson quiz → results |
| Wrong answer reflection | Check/MCQ wrong → optional “What tripped you up?” |
| Profile analytics | `/profile` — weak topics, due today, skill patterns, exam plan |
| Social | `/feed`, `/u/<handle>`, challenges, QOTD |

---

## 10. Related documentation

| Document | Purpose |
|----------|---------|
| `docs/AI_HANDOFF.md` | **Start here for AI agents** — status, reading order, invariants, engagement E1–E3 (shipped) |
| `docs/COMPLEX_MECHANISMS.md` | How the three hardest subsystems work (grading, queues, Phase G) |
| `docs/MOBILE.md` | Mobile polish (M0–M4) + Play Android via TWA (M5–M7) |
| `docs/SOLID_DRAFT_SECURITY.md` | Solid-draft audit fixes — do not regress |
| `docs/SECURITY_AND_GDPR.md` | S0 **and S1 shipped in code**; S2 next. DPIA/ROPA/subprocessors drafts alongside |
| `docs/INCIDENT_RESPONSE.md` | Breach runbook (72-hour ICO clock) |
| `docs/DATA_RIGHTS.md` | How to answer an access/erasure email |
| `docs/API.md` | REST API v1 contract |
| `docs/DEPLOY.md` | Production deployment checklist (encrypted backups, CI scanning) |
| `docs/OPERATOR_LAUNCH.md` | **Operator (David)** — ICO fee, privacy inbox, prune/backup cron; do at public HTTPS / M5 |
| `docs/EMAIL_SETUP.md` | Weekly digest configuration |
| `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` | G8, engagement E4, other future ideas |
| `docs/ENGAGEMENT_VISUAL.md` | Avatar / buddy visual tokens for E2–E3 |
| `docs/REAL_WORLD_QUESTIONS.md` | **Planned** — real-world question style (E4.1) implementation plan |
| `docs/ENGAGEMENT_E5.md` | **In progress** — E5.1–E5.6 shipped; web push (E5.7) blocked on HTTPS |

---

## 11. Maintenance notes for developers

1. **Do not rebuild** checker infrastructure or G1–G7 features — extend them. **Do not regress** solid-draft security invariants.
2. After JS/template changes affecting cached assets, bump `site.js?v=N` and `CACHE_VERSION` in `static/js/sw.js`.
3. Run `python scripts/run_smoke_tests.py` before deploy (includes SymPy security smoke).
4. Schema changes: add new `CREATE TABLE IF NOT EXISTS` blocks in `app.py`; no down-migrations required for typical releases.
5. New topics: register in `topic_registry.py`, add lesson content in `topics_data.py` and templates as needed.
6. Never commit `data/*.db` or `*.bak`.
