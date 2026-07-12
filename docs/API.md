# Problem Bank API v1 (Phase F / mobile readiness)

Auth: session cookie (web + PWA). Native tokens come later (Phase M3).
Unauthenticated `/api/*` calls return JSON `401`.

## Catalog & generator

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/api/v1/topics` | No | Levels → subjects → topics with modes/difficulties |
| POST | `/api/v1/problems/generate` | Optional | Body: `level`, `subject`, `topic`, `mode`, `difficulty`, `action` (`start`\|`next`\|`reroll`) |

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
