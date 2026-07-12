# Problem Bank API v1 (Phase F / mobile readiness)

Auth: **session cookie** (web + PWA on same origin) or **`Authorization: Bearer <token>`** (native apps, Phase M3).
Unauthenticated `/api/*` calls return JSON `401`.

## Authentication (M3)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/auth/register` | No | Body: `email`, `handle`, `password`, `age_confirm` (must be `true`), optional `label`. Returns `{ token, user }`. Rate limit: 10/day/IP. |
| POST | `/api/v1/auth/login` | No | Body: `email`, `password`, optional `label`. Returns `{ token, user }`. Rate limit: 30/day/IP. |
| POST | `/api/v1/auth/logout` | Bearer | Revokes the token used in the request. |
| GET | `/api/v1/auth/me` | Yes | Current user summary. |
| GET | `/api/v1/auth/tokens` | Yes | List active app sessions (no secret values). |
| POST | `/api/v1/auth/revoke-all` | Yes | Revoke all tokens; body optional `{ "keep_current": true }` (default). |

Tokens are prefixed with `pb_`, stored as SHA-256 hashes, and shown only once at creation. Web settings include **Log out all devices** to revoke every token.

Example:

```http
Authorization: Bearer pb_xxxxxxxx
Accept: application/json
```

## Catalog & generator

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/api/v1/topics` | No | Levels → subjects → topics with modes/difficulties |
| GET | `/api/v1/topics/<level>/<subject>/<topic>/lesson` | Optional | Full lesson HTML for WebView + metadata |
| POST | `/api/v1/problems/generate` | Optional | Body: `level`, `subject`, `topic`, `mode`, `difficulty`, `action` (`start`\|`next`\|`reroll`) |

## Quick Test (M4)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/quicktest/start` | Optional | Body: `level`, `subject`, `topic`, `mode`, `difficulty`. Returns `session_id` + first question. |
| GET | `/api/v1/quicktest/<session_id>/question` | Optional* | Current question (no solutions). |
| POST | `/api/v1/quicktest/<session_id>/answer` | Optional* | Body optional `{ "user_answer": "B" }`. Advances to next question. |
| GET | `/api/v1/quicktest/<session_id>/results` | Optional* | All questions with solutions after test is finished. |

\*Logged-in sessions are tied to the account; other users cannot access them.

## Lesson progress (M4)

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/me/lesson-progress` | Yes |
| GET | `/api/v1/me/lesson-progress/<level>/<subject>/<topic>` | Yes |
| POST | `/api/v1/me/lesson-progress` | Yes |
| DELETE | `/api/v1/me/lesson-progress/<level>/<subject>/<topic>` | Yes |

Legacy web JS still uses `GET/POST /api/lesson-progress` (CSRF + session).

Generate response:
```json
{
  "ok": true,
  "problem": { "question_html", "solution_html", "hint_html", "options", "correct_answer", "variant_name", ... },
  "selection": { "variant_name", "queue_position", "queue_length", "can_reroll" },
  "rate_limit_remaining": 199
}
```

Logged-in queues persist in `user_problem_queues`. Daily generate limit: 200.

## Saved problems

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/me/saved-problems` | Yes |
| GET | `/api/v1/me/saved-problems/<id>` | Yes |
| POST | `/api/v1/me/saved-problems` | Yes (session last problem, or inline `problem` JSON) |
| DELETE | `/api/v1/me/saved-problems/<id>` | Yes |

## Social / gamification (existing)

Profiles, follow, search, feed, notifications, suggestions, shares, gamification — see prior phases.

Pagination: `?limit=&before_id=` on feed and notifications; response includes `next_before_id`.

## Moderation

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/users/<handle>/block` | Yes |
| DELETE | `/api/v1/users/<handle>/block` | Yes |
| GET | `/api/v1/me/blocks` | Yes |
| POST | `/api/v1/users/<handle>/report` | Yes (`report_type`: spam\|harassment\|inappropriate\|other) |

Blocks hide profiles from each other and remove follows. Daily report limit: 20.

## Settings

`PATCH /api/v1/me/settings` accepts privacy toggles including `show_study_streak` and `show_milestones`.

## Progressive web app (M2)

| Asset | Path |
|-------|------|
| Manifest | `/manifest.webmanifest` |
| Service worker | `/sw.js` (scope `/`) |
| Offline page | `/offline` |
| Icons | `/static/icons/icon-192.png`, `icon-512.png` |

Behaviour:
- Static assets cached for faster loads
- `/api/*` always network-only (returns JSON `503` / `code: offline` when disconnected)
- Navigation failures show `/offline`
- Install prompt appears when the browser fires `beforeinstallprompt`
