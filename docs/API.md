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

When the checker accepts an equivalent form (e.g. `6/8` for `3/4`, `2√5` for surd answers, `6:10` for `3:5`), `normalized_user` differs from what the student typed. The free-response UI appends **“Equivalent forms accepted.”** to the success feedback in that case. Input placeholders come from each problem’s `answer_format_hint` when set.

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
| `fraction` | `3/4` or `num\|den` e.g. `3\|4` | `3/4`, `6/8`, `1 1/2` (mixed), `0.75` (decimal equivalent) |
| `standard_form` | `coeff\|exp` e.g. `3.2\|5` | Coefficient + power of 10 fields |
| `number_pair` | `a\|b` | Two numeric fields |
| `number_list` | `1,2,3` | Comma-separated numbers |
| `power` | `base\|index` e.g. `2\|10` | Base ^ index |
| `number_fields` | `v1\|v2\|…` (or `\x1e` sep when a value contains `\|`) | One field per label; optional per-field Check |
| `ratio` | `a\|b` | `a:b` (equivalent ratios OK) |
| `ratio_exact` | `a\|b` | `a:b` must match exactly (not simplified) |
| `linear_equation` | `m\|c` e.g. `2\|3` for \(y = 2x + 3\) | `y = 2x + 3` |
| `linear` | `3` or `x=3` (one-variable solution) | `3`, `x = 3`, `x=-2`; fractions/decimals when equivalent |
| `quadratic_roots` | `3,-2` or `{3,-2}` (sorted set) | Two (or more) root fields when there are multiple solutions; order ignored; equivalent fractions OK. Single field only for one-root edge cases. |
| `vector` | `x\|y` e.g. `3\|4` (top \| bottom) | `(3, 4)`, `3, 4`, `3\|4`, column matrix notation; fractions/decimals when equivalent |
| `keyword` | e.g. `positive` | Case-insensitive keyword / alias match |
| `number_estimate` | `centre~tol` e.g. `10~2` | Estimate within tolerance |
| `bearing` | `045` | `45`, `045`, `045°` |
| `pi_multiple` | coefficient of π e.g. `4`, `1/2` | `4`, `4π`, `0.5` |
| `surd` | `coeff\|radicand` e.g. `1\|113`, `2\|5` | `√113`, `2√5` |
| `binary` | `width\|bits` e.g. `8\|10010110` (`0\|…` = no fixed width) | Binary digits |
| `hex` | `width\|hex` e.g. `0\|FF` | Hex digits (case-insensitive) |
| `completed_square` | `kind\|v1\|v2\|…` e.g. `scaled\|3\|4\|-9` for \(y = 3((x+4)^2-9)\) | Fixed template with integer blanks: `plus` \((x+p)^2+k\), `minus` \((x-p)^2+k\), `scaled` \(a((x+p)^2+k)\), `expand` \(x^2+bx+c\) |

Phase 2 adds dedicated `fraction` and SymPy-backed `surd` types; ungraded conceptual variants omit `correct_answer_raw` and do not show the Check UI. Phase 3 adds `linear` (one-variable equation solutions), `quadratic_roots` (order-independent root sets via SymPy), and `vector` (column vectors with flexible `(x, y)` input). Simultaneous linear topics (`simultaneous_equations`, `graphical_simultaneous_equations`) use `number_pair` for `(x, y)` solutions, `linear` when only one variable is requested, and `number_fields` for two intersection points. The quadratics cluster (`completing_the_square`, `quadratic_simultaneous_equations`) reuses those types for numeric roots, turning points, and full `(x, y)` solution pairs; completed-square **form** variants use structured `completed_square` blanks (only show-that proofs stay ungraded). `changing_the_subject` uses the `algebraic` checker for rearranged formulae; `functions` uses `number`, `linear`, `quadratic_roots`, and `number_fields` for numeric evaluation and solving (inverse/composite-rule algebra and multipart exam-style variants stay ungraded). General `algebra` practice uses `linear`, `quadratic_roots`, `number_pair`, `number`, and `algebraic` for equations, expansions, factorisation, simultaneous pairs, and rearranging formulae. `algebraic_fractions` uses stacked `algebraic_fraction` fields for single-fraction answers (equivalent forms accepted), plus `algebraic`, `linear`, and `number` where the simplified result is not a fraction. `vectors` uses `vector`, `number_pair`, `surd`, `number`, `keyword`, `vector_combo`, `vector_pair`, Plan B `number_fields` scaffolds for geometry proofs, and Plan C `proof_steps` banks for worded conceptual / triangle-inequality proofs. `trigonometry` uses `number` for lengths and angles, `fraction` and `algebraic_fraction` for exact trig values, `surd` for exact surds, `keyword` for yes/no, and a Plan B `number_fields` scaffold for the \(\sin^2 30+\cos^2 30\) identity. `transformations` uses `number_fields` for image coordinates (six boxes for P′Q′R′), `number` for scale factors and areas, `number_pair` for centres, `keyword` for transformation type, and `algebraic` fields for symbolic coordinate rules; “describe the transformation” and conceptual proof variants stay ungraded. `constructions_loci` uses `number` for scale-drawing lengths, intersection counts, locus radii, and sector areas, and `number_fields` for multipart numeric answers (e.g. incircle / triangle centres); construction-step and descriptive locus variants stay ungraded. `geometry_angles` proof variants (triangle sum, cyclic quad, exterior-angle sum) use Plan B `number_fields` scaffolds. `sequences` pure theorem proofs (sum of odds, divisibility, recurring decimals) use Plan C `proof_steps` banks. Show-that identities and express-in-terms questions use Plan A checkpoints or Plan B scaffolds (when the stem already states the result): grade intermediate steps / the simplified result with existing checkers rather than free-text proof marking. Plan C `proof_steps` answers are selected step ids from a shuffled bank (`orderFlag|id1|id2|…`); order may or may not matter.
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

## Revision queue (G3)

Rule-based spaced revision queue built on top of weak topics (logged-in only). The queue is synced from the latest weak-topic analysis every time it's read — there's no background job. New weak topics get a due date based on how weak they currently look (worse recent accuracy → sooner due date); topics that stop being weak are dropped automatically.

| Method | Path |
|--------|------|
| GET | `/api/v1/me/revision-queue` |
| POST | `/api/v1/me/revision-queue/dismiss` |
| POST | `/api/v1/me/revision-queue/complete` |

**GET** query: `limit` (1–20, default 3), `due_only` (default `1` — only items due today or overdue; pass `0` for the full queue including items snoozed into the future).

Response: `revision_queue[]` with `level`, `subject`, `topic`, `topic_label`, `priority`, `reason`, `due_at`, `due_date`, `last_completed_at`, `topic_url`, and `lesson_quiz_url` when a lesson quiz exists.

**POST** `dismiss` / `complete` body: `{ "level": ..., "subject": ..., "topic": ... }`. `dismiss` ("not now") snoozes the item a few days; `complete` ("done") snoozes it further and records `last_completed_at`. Both return `404 not_found` if the topic isn't currently in the user's queue (e.g. it's no longer weak).

The profile page shows the top 3 due-today items in a "Due today" widget with the same actions.

## Wrong-answer reflections (G4)

Optional student notes after a wrong Check or MCQ answer (logged-in only). Reflections can link to a practice attempt when the client received `attempt_id` from the check or mcq-answer APIs.

| Method | Path |
|--------|------|
| POST | `/api/v1/me/reflections` |
| GET | `/api/v1/me/reflections` |

**POST** body: `{ "level", "subject", "topic", "source" }` required (`source`: `check` or `mcq`); plus at least one of `prompt_type` or non-empty `reflection_text`. Optional: `difficulty`, `attempt_id` (must belong to the logged-in user).

`prompt_type` values: `calculation_error`, `misread_question`, `forgot_formula`, `guessed`, `other`. `reflection_text` max 500 characters.

Response `201`: `{ "ok": true, "reflection": { ... } }` with `id`, `topic_label`, `topic_url`, `attempt_id`, `prompt_type`, `reflection_text`, `created_at`.

**GET** query: `limit` (1–100, default 20), `before_id` (cursor), optional `topic` filter, optional `prompt_type` chip filter.

**Check / MCQ APIs** now include `attempt_id` in the JSON response when a practice attempt is recorded (logged-in, valid topic). Retries with `record_attempt: false` do not return a new `attempt_id`.

After a wrong answer on the website (logged-in, generator / Quick Test / saved / shared practice with topic context), an optional **“What tripped you up?”** panel appears with quick-reason chips, optional free text, **Save note**, and **Not now**. Chip-only saves are one click when the text box is empty.

## Cohort stats (G5)

Anonymous aggregate difficulty for the **exact question** on screen (same stem + mark-scheme key). No individual student data is exposed. Stats appear only after at least **20** attempts on that question instance.

Returned on **`POST /api/v1/problems/check`** and **`POST /api/v1/generator/mcq-answer`** (when the session holds the matching generated problem):

```json
"cohort": {
  "wrong_pct": 68.0,
  "sample_size": 142,
  "min_sample_size": 20
}
```

The website shows a muted line such as: *About 68% of students got this wrong (142 attempts).* Below the minimum sample size, `cohort` is omitted.

## Skill gaps and reflections (G6)

Cross-topic roll-up of wrong-answer reflection chips (logged-in only), plus profile history.

| Method | Path |
|--------|------|
| GET | `/api/v1/me/skill-gaps` |
| GET | `/api/v1/me/reflections` (extended) |

**Skill gaps** query: `limit` (1–20, default 6), optional `lookback_days` (default 90). A gap appears when the same `prompt_type` has at least **2** reflections in the lookback window.

Response `skill_gaps[]`: `prompt_type`, `label`, `reflection_count`, `topic_count`, `last_reflected_at`, `overlaps_weak_topic` (true when any linked topic is also in weak-topics), and `topics[]` with `topic_label`, `topic_url`, `lesson_quiz_url`, `is_weak_topic`, `reflection_count`.

**Reflections list** adds query `prompt_type` (chip filter, same values as G4). Items include `prompt_type_label`.

Profile page: **Skill patterns** section (when gaps exist) and **My reflections** with filter chips (`?reflection_type=`).

## Revision planner (G7)

Exam-date study schedule from weak topics (logged-in only). Spreads scoped weak topics across calendar days from **today** through the day **before** the exam (max **2 topics/day**, up to **180** days ahead).

| Method | Path |
|--------|------|
| GET | `/api/v1/me/revision-plan` |
| PUT | `/api/v1/me/revision-plan` |
| DELETE | `/api/v1/me/revision-plan` |

**PUT** body: `{ "level", "subject", "exam_date" }` (`exam_date`: `YYYY-MM-DD`, today or future).

Response `revision_plan`: `exam_date`, `days_remaining`, `study_day_count`, `topics_scheduled`, `weak_topic_count`, `sessions[]` (`plan_date`, `topics[]` with `topic_label`, `topic_url`, `lesson_quiz_url`, `reasons`, weakness metadata).

Profile page: **Exam revision plan** section with date/scope form and day-by-day schedule. Web form: `POST /profile/revision-plan` (CSRF); `action=clear` removes the plan.

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

`GET /api/v1/feed` (auth) also returns `qotd_challenge`: today’s `@problem_bot` card on `filter=all` with no `before_id`, or `null`. The card is synthetic (not an activity-event `id`). Web `/feed` shows the same card. Feed items include `actor_avatar` (`face`, `bg`, `extra`); the QOTD card includes `avatar`.

`GET /api/v1/search` also matches **lesson body keywords** (FTS5) as well as topic name/slug/group. The index covers `topics_data.py` metadata and stripped `*_lesson.html` pages. Name/slug hits rank first (`"via": "title"`); other lesson-text hits use `"via": "keywords"`. Topic rows include 1-based `"rank"` (name matches first, then keyword relevance). User rows include `avatar`.

`GET`/`PATCH /api/v1/me/settings` include `avatar: { face, bg, extra }`. PATCH accepts that object, or `avatar_face` / `avatar_bg` / `avatar_extra`. Unknown emoji/colours fall back to the default 🙂 on `#eef6fc`. No image upload. Avatar extras 🎓/🎧/⭐ require milestones `topics_10`, `questions_25`, and `streak_7` respectively (E5.5); locked selections are rejected server-side (existing wearers are grandfathered). Public profiles (`GET /api/v1/users/<handle>/profile`) and `GET /api/v1/me/gamification` friend leaderboard rows also include `avatar`.

`GET /api/v1/me/buddy` (auth) returns `{ type, message, detail, face, action_url, action_label, actions, topic, milestone_key?, friend_handle? }`. Types: `milestone` (badge earned in last 24 h), `celebrate` (quiz today), `qotd_nudge` (activity today but no QOTD attempt), `streak_risk` (streak would break tomorrow), `weak_topic` (G1), `friend_challenge` (follows ≥1 person, no challenge sent in 7 days — links to followed friend's profile), `nudge`. Priority: milestone > celebrate > qotd_nudge > streak_risk > weak_topic > friend_challenge > nudge. Optional query `level`, `subject`, `topic` is the page the widget is on (the widget also sends `X-PB-Buddy-Path` and the API falls back to the Referer). On that weak topic’s lesson/generator page, `actions` is **Practise MCQ**, **Take a quiz** (when a lesson quiz exists), and a `stay` action **Keep learning {topic}** (hides the card for that topic today; not a global dismiss). `action_url` / `action_label` remain the first link for older clients. Off that page, weak topic still has a single **Practise this** link. Milestone prompts link to `profile#milestones`; **Not now** or **View badges** stores `pb-buddy-milestone-<key>` in localStorage so the same badge is not repeated. After a persisted generator MCQ on the current topic, the client dispatches `pb-buddy-refetch` and the widget updates in place. `GET /api/v1/build-info` returns `{ buddy_embed, study_buddy_js }` version strings for cache debugging. The web widget is non-blocking. Off that page, **Not now** lasts until the next UTC day. On the weak topic’s own lesson page the last button is **Keep learning {topic}** (hides only that on-page card for the UTC day); a previous **Not now** does not hide the on-page coach.

`GET /api/v1/me/gamification` includes `friend_accuracy_leaderboard`: friends-only weekly lesson-quiz + generator-MCQ accuracy (`accuracy_pct`, `earned`/`possible`). `show_accuracy_leaderboard` (settings, default true) hides you from other people’s accuracy boards. Web: `/leaderboard/friends?board=accuracy`. **No global ranking.** `milestones` items are `{key, title, description, emoji, earned_at}`. Catalog includes QOTD badges (`qotd_first`, `qotd_7`), `questions_50`, and friends-only `accuracy_top_friend` (E5.2 — awarded only at rank 1 with ≥2 scored friends and ≥10 answered questions in the week).

`GET /api/v1/qotd/today` is a **difficult** MCQ. Solution HTML and `correct_answer` are omitted until the user has answered. `POST /api/v1/qotd/today/answer` records the attempt for the friend mini-leaderboard and the study streak only — it does **not** write generator MCQ history or topic activity. After a wrong answer the JSON includes `solution_html` (same idea as the generator “Show Answer” panel).

### Planned additions (not implemented)

Document these here when they ship — specs live in `docs/ENGAGEMENT_E5.md`:

- `GET /api/v1/qotd/week/leaderboard` — 7-day friends-only QOTD board (E5.3)
- `GET /api/v1/me/gamification` gains `qotd_week_leaderboard` and `study_streak.freeze_available` (E5.3 / E5.4)
- `POST /api/v1/me/push/subscribe`, `DELETE /api/v1/me/push/subscription` — blocked on production HTTPS (E5.7)

The generator endpoints gain a `real_world` value for `mode` when `docs/REAL_WORLD_QUESTIONS.md` is implemented; the request/response shape is otherwise unchanged from `standard`.

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
