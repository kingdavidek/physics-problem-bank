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

### Check typed answer (Phase 0)

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/problems/check` | Optional |

Body:

```json
{
  "user_answer": "42",
  "correct_answer_raw": "42",
  "answer_type": "number",
  "level": "gcse",
  "subject": "maths",
  "topic": "bidmas",
  "difficulty": "foundational"
}
```

When the browser has a recent generator problem in session (`last_problem_payload`), the server validates against that stored problem and rejects mismatched `correct_answer_raw` / `answer_type` with HTTP **403** (`session_mismatch`). Otherwise `correct_answer_raw` must be supplied in the body.

Response:

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

`practice_streak` is included when the caller is logged in. Supported `answer_type` values: `number` (more types planned).

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
