# Problem Bank — Solid-draft security hardening

**Last updated:** 2026-08-01  
**Status:** Implemented and merged to `main` (history purged of tracked SQLite)  
**Related plan:** Cursor plan *Solid draft audit* (local only; not in repo)  

This document records **what was wrong**, **what we changed**, and **what the next agent must preserve**. It complements `docs/ARCHITECTURE.md` (system overview) and `docs/AI_HANDOFF.md` (reading order / next steps).

**Forward-looking companion:** `docs/SECURITY_AND_GDPR.md` covers what is still missing — data subject rights, retention, transparency, the remaining header and CSP work, and the compliance obligations that attach once real users exist. This file is the record of what was fixed; that one is the plan for what comes next.

---

## 1. Why this existed

The app was feature-complete for G1–G7 and auto-correct, but **not** a safe production draft. An audit found Critical issues (RCE via SymPy grading, credentials in git, unsafe defaults) plus High/Medium gaps. **G8 was blocked** until Phase 0 (and preferably Phase 1) landed.

Success criteria that are now met:

- [x] No untrusted string reaches bare `sympify` / unsafe eval; exploit smoke green  
- [x] No SQLite DB or bak files in the git index; smoke uses ephemeral DB  
- [x] App refuses default `SECRET_KEY` outside testing; local run not debug-on-all-interfaces  
- [x] MCQ correctness and saved-problem HTML cannot be forged by the client  
- [x] Web auth rate-limited; logged-in API rate-limited; DB connections closed  
- [x] Core smoke suite passes (`python scripts/run_smoke_tests.py`)

---

## 2. Critical fixes (Phase 0)

### C1 / C2 — SymPy RCE + check API trust

**Was:** `sympify()` on user/correct strings during algebraic / quadratic-roots grading. Combined with `POST /api/v1/problems/check` accepting client `answer_type` / `correct_answer_raw` without a session problem, this was **unauthenticated RCE** (e.g. `sympify("__import__('os').name")`).

**Now:**

| Change | Where |
|--------|--------|
| `_safe_sympify` / `_is_safe_math_expr` — `parse_expr` + restricted transformations, empty locals, length cap | `generators/shared/answer_checkers.py` |
| Same path used for algebraic equivalence and `_root_to_sympy` / quadratic roots | same |
| `MAX_USER_ANSWER_LEN`, `MAX_SYMPY_EXPR_LEN` | `answer_checkers.py` |
| SymPy types require session-bound problem; otherwise `400 session_required` | `app.py` → `api_v1_problems_check` |
| Regression smoke | `scripts/test_sympy_security_smoke.py` |

**Do not:** reintroduce bare `sympify` on untrusted input, or allow client-supplied SymPy types without session.

### C3 / H10 — SQLite in git + smoke pollution

**Was:** `data/quicktest.db` tracked (~3.7MB, user emails + password hashes). Smoke wrote into the same path.

**Now:**

- `.gitignore`: `data/*.db`, `data/*.db-*`, `data/backups/`, `*.bak`
- DB and bak files removed from the index and **purged from git history** (`git filter-repo`); `main` force-pushed
- Smoke / testing: `PB_TESTING=1` → temp DB; optional `PB_DB_PATH` override (`app.py` `_db_path`, `scripts/run_smoke_tests.py`)

**Local file** `data/quicktest.db` may still exist on disk for development; it must stay untracked.

**Assume** any real passwords that lived in that DB are compromised if reused elsewhere.

### C4 / C5 — SECRET_KEY and `__main__`

**Was:** Hardcoded default secret; `app.run(debug=True, host="0.0.0.0")`.

**Now:**

- Fail-fast unless `SECRET_KEY` is set and ≠ default, or `PB_TESTING` / `PB_ALLOW_DEV_SECRET=1`
- `__main__` in `app.py` and `flask_app.py`: host `127.0.0.1` by default; debug only via `FLASK_DEBUG`

---

## 3. High fixes (Phase 1)

| ID | Fix | Notes |
|----|-----|--------|
| **H1** | `_safe_redirect_target` | Rejects `//evil` open redirects on login `next` |
| **H2** | Save API session-only | `POST /api/v1/me/saved-problems` uses session problem, not client HTML |
| **H3** | Web `/login` `/register` rate-limited | Same daily bucket pattern as API auth |
| **H4** | Authenticated API rate-limited by `user_id` | No longer bypasses `_api_rate_limit` |
| **H5** | MCQ graded server-side | From `last_problem_payload.correct_answer`; returns `correct` |
| **H6** | Request-scoped DB + WAL | `g.db`, `teardown_appcontext`, `PRAGMA journal_mode=WAL`, `busy_timeout` |
| **H7** | Slim session problem | `_slim_problem_for_session` drops bulky SVG/HTML keys |
| **H8** | UTC day keys | Streaks, rate limits, QOTD, revision due — unified on UTC |
| **H9** | Atomic rate-limit upsert | `models/rate_limit.py` |
| **H11** | CSRF on `/api/*` mutations | Cookie sessions; Bearer + `PB_TESTING` exempt; forms still validated |
| **H12** | Pinned deps | `requirements.txt`: Flask 3.1.3, Flask-Login, Werkzeug, sympy, python-docx |

Front-end: `static/js/site.js` `apiHeaders` includes CSRF; lesson/quiz/notification fetches updated. CSRF meta always in `templates/base.html`.

---

## 4. Medium polish (Phase 2) — landed

- Secure cookies when `SITE_URL` is https or `SESSION_COOKIE_SECURE=1` (session + remember)
- Health: `GET /api/v1/health` runs `SELECT 1` → 503 if DB down
- Backup: `scripts/backup_sqlite.py` + note in `docs/DEPLOY.md`
- API tokens default **90-day** expiry on issue
- Dummy password-hash verify on failed web login (timing)
- Generic register conflict message (no email vs handle enumeration)
- MathJax (+ Pyodide fallback script) **SRI**; dead PythonAnywhere script tag removed
- Weak-topic lookback capped (default 180 days); revision planner respects max topics/day
- Friend effort leaderboard batched (no N+1 per user)
- SQL / SymPy input size caps; study activity recorded on MCQ answer path

**Still deferred / gradual:** full CSP nonces (CSP still allows `'unsafe-inline'` / `'unsafe-eval'` for MathJax/Pyodide); password-reset product decision; Low escaping nits. See Phase 3 in the original audit plan.

---

## 5. What was already solid (keep)

- Werkzeug password hashing; API tokens via `secrets`, stored as SHA-256 hashes  
- Parameterized SQL; `sql_checker` does token compare only (no SQL execution)  
- `python_run` grading is client-side Pyodide (no server `eval` of student code)  
- IDOR filters on “me” routes by `user_id`  
- CORS allowlist (not `*`); SW does not cache API  
- Jinja autoescape for handles/notes; AI assist escaped in JS  
- 404/500 do not leak stacks when not in debug  

---

## 6. Env and ops checklist for agents

| Variable | Role |
|----------|------|
| `SECRET_KEY` | Required in prod / normal local |
| `PB_ALLOW_DEV_SECRET=1` | Local-only bypass of secret requirement |
| `PB_TESTING=1` | Smoke/tests: temp DB, CSRF/rate exemptions |
| `PB_DB_PATH` | Override SQLite path |
| `FLASK_DEBUG` / `FLASK_RUN_HOST` | Debug and bind for `__main__` |
| `SITE_URL` / `SESSION_COOKIE_SECURE` | Secure cookies |
| `CORS_ORIGINS` | Optional separate frontend origins |

Never commit `.env`. Backup DB off-git (`scripts/backup_sqlite.py`).

---

## 7. Regression tests to run after grading / auth / session changes

```text
scripts/test_sympy_security_smoke.py
scripts/test_answer_check_smoke.py
scripts/test_phase1_numeric_smoke.py
scripts/test_generator_mcq_smoke.py
scripts/test_phase_g4_smoke.py / test_phase_g5_smoke.py
# or full suite:
scripts/run_smoke_tests.py
```

Answer-check smoke uses `_post_problems_check` to bind session for SymPy types and clear session afterwards so mixed-type follow-ups do not hit `session_mismatch`.

---

## 8. Intentional trust model (grading)

```
Generate problem → store slim grading keys in session (last_problem_payload)
       ↓
User submits answer → server uses session correct_answer_raw / answer_type / correct_answer
       ↓
Client may send answer_type/raw for non-SymPy types only when no session problem
       ↓
SymPy types always require session
```

Forging `correct: true` on MCQ or posting XSS HTML into “save problem” must fail.

---

## 9. Related files (quick map)

| File | Security-relevant role |
|------|------------------------|
| `app.py` | Secret, CSRF, redirects, check/MCQ/save APIs, DB lifecycle, cookies, health |
| `generators/shared/answer_checkers.py` | Safe SymPy, length caps |
| `generators/shared/sql_checker.py` | SQL size cap / LCS scoring |
| `models/rate_limit.py` | Atomic UTC buckets |
| `models/gamification.py` / `user_data.py` / `qotd.py` / `weak_topics.py` / `revision_planner.py` | UTC days, caps, streaks |
| `templates/base.html` | CSRF meta, MathJax SRI, CSP-related scripts |
| `static/js/site.js` | CSRF on API fetches |
| `.gitignore` | DB / bak ignore rules |
