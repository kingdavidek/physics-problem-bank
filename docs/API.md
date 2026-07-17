# Problem Bank API v1

Auth: **session cookie** (web + PWA on same origin) or **`Authorization: Bearer <token>`** (native apps).
All `/api/v1/*` errors return JSON: `{ "ok": false, "error": "...", "code": "..." }`.

## Health

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/health` | No |

Returns `{ "ok": true, "status": "up" }`.

## CORS (native / separate frontend)

Set env var **`CORS_ORIGINS`** to a comma-separated list of allowed browser origins, e.g.:

```
CORS_ORIGINS=https://app.example.com,http://localhost:5173
```

When set, `/api/*` responses include `Access-Control-Allow-Origin` for matching `Origin` headers, and `OPTIONS` preflight is supported. Credentials (cookies) are allowed for whitelisted origins.

Same-origin web and PWA do **not** need CORS.

## Authentication (M3)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/auth/register` | No | Rate limit: 10/day/IP |
| POST | `/api/v1/auth/login` | No | Rate limit: 30/day/IP |
| POST | `/api/v1/auth/logout` | Bearer | Revokes current token |
| GET | `/api/v1/auth/me` | Yes | Current user |
| GET | `/api/v1/auth/tokens` | Yes | List app sessions |
| POST | `/api/v1/auth/revoke-all` | Yes | Optional `{ "keep_current": true }` |

Example: `Authorization: Bearer pb_xxxxxxxx`

## Rate limits (daily, per user or IP)

| Action | Limit | Endpoints |
|--------|-------|-----------|
| Register | 10 | `POST /api/v1/auth/register` |
| Login | 30 | `POST /api/v1/auth/login` |
| Generate problem | 200 | `POST /api/v1/problems/generate` |
| Quick test start | 30 | `POST /api/v1/quicktest/start` |
| Lesson quiz start | 20 | `POST /api/v1/lesson-quiz/start` |
| Share question | 50 | `POST /api/v1/shared-questions`, web share form |
| Suggest question | 50 | `POST /api/v1/suggestions`, web suggest form |
| Report user | 20 | `POST /api/v1/users/<handle>/report` |

Limited responses use HTTP **429** with `"code": "rate_limited"` and `"rate_limit_remaining": 0`.
Successful share/suggest/generate responses may include `"rate_limit_remaining"`.

Storage caps (not daily): saved problems 200, shared questions 200, recipient suggestion inbox 100.

## Catalog & generator

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/topics` | No |
| GET | `/api/v1/topics/<level>/<subject>/<topic>/lesson` | Optional |
| POST | `/api/v1/problems/generate` | Optional |

### Check typed answer (Phase 1)

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/problems/check` | Optional |

Marks a typed (free-response) answer correct or incorrect. Used by the generator, Quick Test, saved/shared/suggested question pages, and native clients.

#### Request body

```json
{
  "user_answer": "42",
  "correct_answer_raw": "42",
  "answer_type": "number",
  "level": "gcse",
  "subject": "maths",
  "topic": "bidmas",
  "difficulty": "foundational",
  "attempt_group_id": "g_optional",
  "part_index": 0,
  "part_total": 3
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `user_answer` | Yes | What the learner typed |
| `correct_answer_raw` | Yes* | Canonical answer (see types below). \*Optional when session already has `last_problem_payload` with a graded problem — then the server uses the stored raw/type |
| `answer_type` | No | Defaults to `number`. Must match the stored type when session-bound |
| `level` / `subject` / `topic` / `difficulty` | No | When the caller is logged in, used to record practice history |
| `attempt_group_id` / `part_index` / `part_total` | No | Multipart field attempts (e.g. `number_fields`) |

#### Session binding

When the browser (or client) has a recent generator / Quick Test / saved problem in session (`last_problem_payload`) **with** `correct_answer_raw`, the server:

1. Grades against the **stored** raw and type (not the client’s copy of the answer key).
2. Rejects a mismatched `correct_answer_raw` or `answer_type` with HTTP **403** and `"code": "session_mismatch"` (`"error": "Problem mismatch"`).
3. Allows a **partial field** check for `number_fields`: client may send one field’s raw plus that field’s `answer_type` if the value appears in the stored multipart string (`|` or `\x1e` separated).

Without a graded problem in session, `correct_answer_raw` is required in the body.

#### Success response

```json
{
  "ok": true,
  "correct": true,
  "normalized_user": "42",
  "normalized_correct": "42",
  "feedback": "Correct!",
  "practice_streak": 3
}
```

| Field | Notes |
|-------|-------|
| `correct` | Whether the answer matched |
| `normalized_user` / `normalized_correct` | Canonical forms used for comparison |
| `feedback` | Short human-readable message |
| `practice_streak` | Present when logged in |

#### Error responses

| HTTP | `code` | When |
|------|--------|------|
| 400 | `invalid_payload` | Body is not a JSON object |
| 400 | `missing_fields` | Empty `user_answer`, or missing `correct_answer_raw` with no session problem |
| 400 | `unknown_answer_type` | Unsupported `answer_type` |
| 400 | `invalid_correct_answer` | Stored/raw answer could not be parsed |
| 403 | `session_mismatch` | Client raw/type does not match session problem |

#### Supported `answer_type` values (Phase 1)

| Type | `correct_answer_raw` format | User input examples |
|------|----------------------------|---------------------|
| `number` | `42`, `1/2`, `-3.5` | Same; fractions and decimals accepted when equivalent |
| `standard_form` | `coeff\|exp` e.g. `3.2\|5` | Coefficient + power of 10 fields |
| `number_pair` | `a\|b` | Two numeric fields |
| `number_list` | `1,2,3` | Comma-separated numbers |
| `power` | `base\|index` e.g. `2\|10` | Base ^ index |
| `number_fields` | `v1\|v2\|…` (or `\x1e` sep when a value contains `\|`) | One field per label; optional per-field Check |
| `ratio` | `a\|b` | `a:b` (equivalent ratios OK) |
| `ratio_exact` | `a\|b` | `a:b` must match exactly (not simplified) |
| `linear_equation` | `m\|c` e.g. `2\|3` for \(y = 2x + 3\) | `y = 2x + 3` |
| `keyword` | e.g. `positive` | Case-insensitive keyword / alias match |
| `number_estimate` | `centre~tol` e.g. `10~2` | Estimate within tolerance |
| `bearing` | `045` | `45`, `045`, `045°` |
| `pi_multiple` | coefficient of π e.g. `4`, `1/2` | `4`, `4π`, `0.5` |
| `surd` | `coeff\|radicand` e.g. `1\|113`, `2\|5` | `√113`, `2√5` |
| `binary` | `width\|bits` e.g. `8\|10010110` (`0\|…` = no fixed width) | Binary digits |
| `hex` | `width\|hex` e.g. `0\|FF` | Hex digits (case-insensitive) |

Phase 2+ will add richer fraction/surd/algebra types; ungraded conceptual variants omit `correct_answer_raw` and do not show the Check UI.
## Quick Test (M4)

| Method | Path |
|--------|------|
| POST | `/api/v1/quicktest/start` |
| GET | `/api/v1/quicktest/<session_id>/question` |
| POST | `/api/v1/quicktest/<session_id>/answer` |
| GET | `/api/v1/quicktest/<session_id>/results` |

## Lesson quiz (M4b)

10-question mixed-difficulty MCQ quiz (same as web `/lesson-quiz/...`). GCSE Maths and GCSE CS topics with MCQ support.

| Method | Path |
|--------|------|
| POST | `/api/v1/lesson-quiz/start` |
| GET | `/api/v1/lesson-quiz/<session_id>/question` |
| POST | `/api/v1/lesson-quiz/<session_id>/answer` |
| GET | `/api/v1/lesson-quiz/<session_id>/results` |

Logged-in users get `attempt_id` and `attempt_url` when the quiz completes. Lesson metadata includes `lesson_quiz_api` when available.

## Lesson progress

**Preferred (mobile / Bearer):**

| Method | Path |
|--------|------|
| GET | `/api/v1/me/lesson-progress` |
| GET | `/api/v1/me/lesson-progress/<level>/<subject>/<topic>` |
| POST | `/api/v1/me/lesson-progress` |
| DELETE | `/api/v1/me/lesson-progress/<level>/<subject>/<topic>` |

**Legacy (web lesson JS only):** `GET/POST /api/lesson-progress` — requires session + CSRF. Responses include `Deprecation: true` header; use v1 for new clients.

## Weak topics (G1)

Topics ranked by quiz and generator MCQ struggle signals (logged-in only).

| Method | Path |
|--------|------|
| GET | `/api/v1/me/weak-topics` |

Query: `limit` (1–20, default 8), optional `lookback_days` (only count attempts within N days).

Response includes `weak_topics[]` with `level`, `subject`, `topic`, `topic_label`, `weakness_score`, `reasons`, `quiz_average_pct`, `mcq_accuracy_pct`, `quiz_attempts`, `mcq_attempts`, `best_quiz_pct`, `last_practised`, `topic_url`, and `lesson_quiz_url` when a lesson quiz exists.

## Quiz history (G2)

Paginated lesson quiz and generator MCQ history for the logged-in user.

| Method | Path |
|--------|------|
| GET | `/api/v1/me/quiz-attempts` |
| GET | `/api/v1/me/quiz-attempts/<id>` |
| GET | `/api/v1/me/mcq-attempts` |
| GET | `/api/v1/me/mcq-attempts/<id>` |

Query (list endpoints): `limit` (1–100, default 20), `before_id` (cursor — pass last item’s `id` for the next page).

**Quiz attempt list** items include `id`, `level`, `subject`, `topic`, `topic_label`, `score`, `total`, `score_pct`, `created_at`, `has_review`, `topic_url`, `review_url`.

**Quiz attempt detail** adds `questions[]` (when stored): each has `index`, `question_html`, `options`, `user_answer`, `correct`, `correct_answer`, `solution_html`, etc. Older attempts without stored problems return `has_review: false` and an empty `questions` array.

**MCQ attempt** items include `user_answer`, `correct_answer`, `correct`, `mode`, `difficulty`, `topic_url`.

Pagination: responses include `next_before_id` (null when no more pages).

## Saved problems, social, moderation

See prior phases. Pagination: `?limit=&before_id=` on feed and notifications.

## Error codes

| Code | HTTP | Meaning |
|------|------|---------|
| `auth_required` | 401 / 403 | Login or token required |
| `invalid_credentials` | 401 | Wrong email/password |
| `invalid_token` | 401 | Bad or revoked Bearer token |
| `validation_error` | 400 | Register validation failed (`fields` object) |
| `email_taken` | 409 | Register: email in use |
| `handle_taken` | 409 | Register: handle in use |
| `rate_limited` | 429 | Daily limit exceeded |
| `not_found` | 404 | Resource missing |
| `user_not_found` | 404 | Handle not found |
| `topic_not_found` | 404 | Invalid topic path |
| `lesson_not_found` | 404 | No lesson for topic |
| `quiz_not_available` | 404 | Topic has no lesson MCQ quiz |
| `forbidden` | 403 | Not allowed (e.g. quick test session) |
| `blocked` | 403 | User blocked |
| `not_accessible` | 403 | Share visibility |
| `profile_private` | 403 | Profile hidden |
| `invalid_json` | 400 | Body not JSON object |
| `invalid_field` | 400 | Bad field value |
| `invalid_payload` | 400 | Malformed request |
| `missing_fields` | 400 | Required fields absent |
| `invalid_action` | 400 | Bad generate/quicktest action |
| `invalid_difficulty` | 400 | Unknown difficulty |
| `invalid_visibility` | 400 | Bad visibility value |
| `invalid_topic` | 400 | Topic validation failed |
| `self_follow` / `self_block` / `self_report` / `self_suggest` | 400 | Self-action |
| `query_too_short` | 400 | Search query < 2 chars |
| `no_problem` | 400 | No generated problem to save/share |
| `no_variant` | 400 | Nothing to reroll |
| `reroll_failed` | 400 | Reroll error |
| `generate_failed` | 500 | Generator error |
| `server_error` | 500 | Unhandled exception |
| `method_not_allowed` | 405 | Wrong HTTP method |
| `finished` / `not_finished` | 400 | Quick test state |
| `share_limit` | 400 | 200 shared questions cap |
| `saved_limit` | 400 | 200 saved problems cap |
| `inbox_limit` | 400 | Recipient inbox full |
| `invalid_csrf` | 403 | Legacy lesson-progress CSRF |

Success shape: `{ "ok": true, ... }`.

## PWA (M2)

| Asset | Path |
|-------|------|
| Manifest | `/manifest.webmanifest` |
| Service worker | `/sw.js` |
| Offline page | `/offline` |

Deploy notes: `docs/DEPLOY.md`.
