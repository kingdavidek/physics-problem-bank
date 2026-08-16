# Problem Bank — Engagement Phase E5 (retention polish)

**Last updated:** 2026-08-16
**Status:** E5.2 shipped; remaining items planned
**Audience:** The next AI agent implementing this
**Predecessor:** E1–E3 shipped 2026-08-15 (see `docs/AI_HANDOFF.md` §6)

E5 is deliberately small. Every item extends something that already exists — the buddy widget, the milestone catalog, `qotd_attempts`, `user_streaks`, the avatar picker. No new subsystems, no economy, no farm.

---

## 0. Items and suggested order

| # | Item | Size | Schema change | Depends on | Status |
|---|---|---|---|---|---|
| **E5.1** | Buddy v0.5 — more message types and faces | S | none | — | Planned |
| **E5.2** | Richer badges — 4 new milestones | S | none | — | **Shipped 2026-08-16** |
| **E5.3** | QOTD week challenge — 7-day friend board | M | none | — | Planned |
| **E5.4** | Streak freeze — one skip per week | M | `user_streaks` + 1 table | — | Planned |
| **E5.5** | Avatar extras unlocked by badges | S | none | E5.2 | Planned |
| **E5.6** | Revision planner subject dropdown (polish) | XS | none | — | Planned |
| **E5.7** | Web push | L | new table | production HTTPS (M5) | Planned (blocked) |

Recommended sequence: **E5.2 (done) → E5.5 → E5.3 → E5.1 → E5.4 → E5.6**, then E5.7 only once a real HTTPS origin exists. Badges first because the buddy and the avatar unlocks both want to talk about them.

**Safeguarding invariants (unchanged from E3):** friends/follows scope only, no global public ranking, every social surface respects the profile opt-out settings.

---

## E5.1 — Buddy v0.5

### Why

`models/buddy.py` picks one of four messages (`celebrate`, `streak_risk`, `weak_topic`, `nudge`) and the widget always shows the same 👾. Three more message types and a matching face make the corner widget feel responsive to what the user just did.

### What exists

- `build_buddy_prompt(conn, user_id, *, now, topic_label_fn)` in `models/buddy.py` — returns one dict, never raises, first match wins.
- `_serialize_buddy_prompt()` + `GET /api/v1/me/buddy` in `app.py` (~line 4931) — maps `action_kind` (`topic` / `topics` / `qotd`) to a URL.
- `static/js/buddy.js` — fetches once per page, writes text into `[data-buddy-message]`, honours a per-UTC-day localStorage dismiss.
- Widget markup with the hard-coded face in `templates/base.html` (~line 3840).

### Changes

**New message types** (added to `BUDDY_TYPES`, evaluated in this priority order, before the existing `nudge` fallback):

| Type | Trigger | Message shape | Action |
|---|---|---|---|
| `milestone` | A milestone earned in the last 24 h that the buddy has not shown yet | "New badge: Week warrior 🏅" | Profile milestones section |
| `qotd_nudge` | No `qotd_attempts` row for today (after any other activity today) | "Today's question is still open." | `/qotd` |
| `friend_challenge` | User follows ≥ 1 person and has sent no challenge in 7 days | "Challenge @handle to today's topic?" | Challenge flow / friend profile |

Priority: `milestone` > `celebrate` > `qotd_nudge` > `streak_risk` > `weak_topic` > `friend_challenge` > `nudge`.

**Faces** — return a `face` per type so the widget can change expression:

```python
BUDDY_FACES = {
    BUDDY_MILESTONE: '🎉',
    BUDDY_CELEBRATE: '😄',
    BUDDY_QOTD_NUDGE: '❓',
    BUDDY_STREAK_RISK: '🔥',
    BUDDY_WEAK_TOPIC: '🤔',
    BUDDY_FRIEND_CHALLENGE: '🤝',
    BUDDY_NUDGE: '👾',
}
```

Add `'face'` to the dict returned by `build_buddy_prompt` and to `_serialize_buddy_prompt`. In `base.html`, give the face span `data-buddy-face`; in `buddy.js`, set its `textContent` from the payload (default 👾 if absent). Keep the emoji as text — no new assets.

**Milestone de-duplication:** the buddy must not repeat the same badge every page load. Store the shown key in localStorage (`pb-buddy-milestone-<key>`) client-side and, server-side, only consider milestones with `earned_at` within 24 h. Do not add a table for this.

**Action kinds:** `_serialize_buddy_prompt` gains `milestone` → `url_for('profile') + '#milestones'` and `challenge` → the friend's public profile.

### Constraints

- Still non-blocking: any failure leaves the page fully usable (the widget stays `hidden`).
- Respect `prefers-reduced-motion` (already handled in the CSS).
- No message may name another user unless the viewer follows them.

### Tests

Extend `scripts/test_buddy_smoke.py`: one test per new type driving the DB into the trigger state and asserting `type`, `face`, and `action_url`; one test that the priority order holds when two triggers are true at once.

---

## E5.2 — Richer badges — **shipped 2026-08-16**

### Why

`MILESTONE_CATALOG` in `models/gamification.py` had six entries and none of them rewarded the daily habit the QOTD was built for. It now has ten, including the four keys below.

### What exists

- Catalog + `evaluate_milestones(conn, user_id)` + `list_user_milestones()` in `models/gamification.py`.
- `user_milestones (user_id, milestone_key, earned_at)` — key-based, so **new badges need no migration**.
- Single evaluation choke point: `_record_study_activity()` in `app.py` (~line 2846) calls `record_study_day` then `evaluate_milestones`.
- Profile already renders earned milestones.

### New keys

| Key | Title | Condition |
|---|---|---|
| `qotd_first` | Daily starter | ≥ 1 row in `qotd_attempts` |
| `qotd_7` | Seven days of questions | ≥ 7 distinct `day_key` rows in `qotd_attempts` (lifetime, not consecutive — cheaper and less punishing) |
| `questions_50` | Practice veteran | ≥ 50 `ACTIVITY_QUESTION_GENERATED` events (mirrors the existing 25 badge) |
| `accuracy_top_friend` | Top of the class | Rank 1 on `friend_accuracy_leaderboard` with ≥ 2 ranked participants and ≥ 10 answered questions in the window |

### Implementation notes

- Add constants + catalog entries, then four blocks in `evaluate_milestones`, following the existing `if <count> >= n and _award_milestone(...)` pattern.
- **Cost:** `evaluate_milestones` runs on every study activity. The first three conditions are single indexed `COUNT(*)` queries — fine. `accuracy_top_friend` runs the full leaderboard, so guard it: skip when the badge is already held, and only compute it when the user has ≥ 10 answered questions this week.
- Optional but nice: add an `emoji` field to each catalog entry (🏅 style) and render it on the profile; the buddy `milestone` message in E5.1 can reuse it.
- The buddy in E5.1 announces new badges — there is no separate toast component to build.

### Tests

`scripts/test_milestones_smoke.py` (registered via `scripts/run_smoke_tests.py`): seed the DB to each threshold, call `evaluate_milestones`, assert the key is awarded exactly once and appears in `list_user_milestones`. Negative: a single-participant accuracy board awards nothing. Rank 2 among friends is not awarded. Profile and `GET /api/v1/me/gamification` include catalog `emoji`.

**Shipped 2026-08-16.**

---

## E5.3 — QOTD week challenge

### Why

`qotd_attempts` already stores one row per user per UTC day, and `friend_qotd_leaderboard` already ranks today. A 7-day rollup turns a one-shot into a week-long reason to come back — with no new writes.

### Model

New function in `models/qotd.py`:

```python
def friend_qotd_week_leaderboard(conn, viewer_id, *, days=7, end_day=None):
    """Viewer + follows ranked by correct QOTD answers over the last `days` UTC days."""
```

- Participants: same set as `friend_qotd_leaderboard` (viewer + everyone they follow).
- Window: the 7 `day_key` strings ending today (inclusive), computed in Python so the SQL is a simple `IN` filter.
- Row shape: `{rank, user_id, handle, correct_days, answered_days, days_in_window, is_viewer}`.
- Sort: `correct_days DESC`, then `answered_days DESC`, then earliest `answered_at`, then handle.
- Respect `show_accuracy_leaderboard` from `user_profile_settings` — reuse the same opt-out as the E3 accuracy board rather than adding another setting.

### Surfaces

- `templates/qotd.html`: a **Today / This week** tab pair, same pattern as `templates/leaderboard_friends.html` (`?board=` query arg).
- `GET /api/v1/qotd/week/leaderboard` returning `{ok, day_keys, leaderboard}` — document it in `docs/API.md`.
- Add `qotd_week_leaderboard` to `GET /api/v1/me/gamification` alongside the existing boards.

### Rules

- Streak semantics stay as they are: a QOTD answer counts for the study streak only, never topic history or `generator_mcq_attempts` rows.
- No global ranking. A user with no follows sees only themselves.

### Tests

New `scripts/test_qotd_week_smoke.py`: two users following each other, seeded attempts across 8 day keys, assert the 8th-day-ago row is excluded, ranking order is correct, opted-out users are hidden from others' boards but still see themselves, and the API shape matches the doc.

---

## E5.4 — Streak freeze

### Why

One missed day currently zeroes a 20-day streak (`get_study_streak` resets when the gap exceeds one day). A single weekly forgiveness keeps the habit without making streaks meaningless.

### Rules (keep these exact)

1. Every user has at most **1 freeze available**, regranted at the start of each ISO week (Monday, UTC).
2. A freeze is consumed **automatically** when the user studies after exactly one missed day — no button to forget to press.
3. A freeze covers **one** missed day. Two consecutive missed days still reset the streak.
4. Freezes never accumulate: unused, they expire at the week boundary.
5. A frozen day is **not** a study day: it does not count toward weekly recap activity or effort scores.

### Schema (in `init_db`, using the existing `PRAGMA table_info` + `ALTER TABLE` pattern)

```sql
-- new columns on user_streaks
freeze_available    INTEGER NOT NULL DEFAULT 1
freeze_week_key     TEXT              -- ISO year-week the current grant belongs to

-- new table
CREATE TABLE IF NOT EXISTS user_streak_freezes (
    user_id   INTEGER NOT NULL,
    freeze_date TEXT NOT NULL,        -- the missed day that was covered
    used_at   TEXT NOT NULL,
    PRIMARY KEY (user_id, freeze_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

### Logic (`models/gamification.py`)

- `_grant_weekly_freeze(conn, user_id, today)` — called from `ensure_user_streak`; if `freeze_week_key` differs from `today.isocalendar()` year-week, set `freeze_available = 1` and update the key.
- `record_study_day`: where the gap is computed, insert a branch — if `(today - previous).days == 2` and a freeze is available, write the covered day to `user_streak_freezes`, decrement `freeze_available`, and treat the streak as continued (`current += 1`) instead of resetting.
- `get_study_streak`: the display-side reset must agree. Today it zeroes when `gap > 1`; it must zero when `gap > 1` **and** the intervening day is not covered by a freeze (and no freeze is available to cover it). Return `freeze_available` and `freeze_used_dates` (last 7 days) in the payload so the UI can show them.

Both functions are the only places that reason about streak continuity — do not scatter this logic.

### Surfaces

- Profile streak card: a small "❄️ 1 skip available this week" line, and "❄️ used" on the covered day if a calendar is shown.
- Buddy: when `streak_risk` fires and a freeze is available, soften the copy ("You have one skip left this week — but a question now keeps the run honest").
- `GET /api/v1/me/gamification` `study_streak` object gains `freeze_available`.

### Tests

New `scripts/test_streak_freeze_smoke.py` driving `record_study_day` with explicit `on_date` values: one-day gap with a freeze continues the streak and consumes it; a second gap in the same week resets; a gap in the following week is covered again after the regrant; `get_study_streak` agrees with `record_study_day` in every case; the covered day is absent from `user_study_days`.

---

## E5.5 — Avatar extras unlocked by badges

### Why

`AVATAR_EXTRAS = ('', '🎓', '🎧', '⭐')` in `models/avatar.py` are free to anyone. Gating them on milestones gives badges a visible payoff without inventing a shop or a currency.

### Mapping

| Extra | Requires |
|---|---|
| `🎓` | `topics_10` |
| `🎧` | `questions_25` |
| `⭐` | `streak_7` |

### Implementation

- `AVATAR_EXTRA_REQUIREMENTS` dict in `models/avatar.py` and `unlocked_extras(conn, user_id)` returning the allowed tuple (always includes `''`).
- **Server-side enforcement** in the settings save route: reject a locked extra and keep the previous value. `parse_avatar()` has no DB access, so it must stay unaware of unlocks — do the check in the route, not the parser.
- **Grandfathering:** if a user already wears a locked extra, keep it. Only new selections are gated.
- `templates/profile_settings.html`: render locked options disabled with a "Earn *Broad explorer* to unlock" caption; keep the picker keyboard-accessible.
- `BOT_AVATAR` (which wears ⭐) is set directly in `models/avatar.py`, not through the route — unaffected.

### Tests

Extend `scripts/test_avatar_smoke.py`: a fresh user cannot save `⭐`; after `streak_7` is awarded they can; an existing wearer keeps theirs; the settings page marks locked options disabled.

---

## E5.6 — Revision planner subject dropdown (polish)

**What §3.7 of the future doc actually means:** on `/profile`, the exam revision plan form renders its Subject `<select>` from `_revision_plan_subjects_for_level()` for **one** level — the saved plan's level, or `gcse` when there is no plan. Change the Level dropdown in the browser and the Subject list does not follow, so you can submit an invalid pair (e.g. A-Level + Computer Science) and the plan silently saves nothing useful.

**Fix:** render every level/subject pair with a `data-level` attribute and filter client-side, exactly like the generator form already does:

- `app.py`: pass all pairs (there is already a helper building `{'level', 'subject'}` options nearby) instead of one level's subjects.
- `templates/profile.html`: add `data-level="{{ pair.level }}"` to each option.
- `static/js/site.js`: a small `initRevisionPlanForm()` reusing `setOptionVisibility` / `ensureValidSelection`, bound to the level select's `change`.
- Server-side validation in `profile_revision_plan_save` stays as the source of truth — this is UX only.

**Test:** extend the existing planner smoke to assert that a mismatched level/subject POST is rejected (or coerced) rather than saved.

---

## E5.7 — Web push (gated, do not start yet)

**What §3.3 means and why it is parked:** in-app notifications exist (`models/notifications.py`, the bell in the navbar); *push* means the browser or Android shell waking the user when the app is closed. The Push API requires a **secure origin with a stable HTTPS certificate** — the site currently runs on `127.0.0.1` for development, and `docs/MOBILE.md` M5 (production HTTPS) has not happened. Building push before M5 means writing code that cannot be tested end to end.

When M5 lands, the shape is:

1. VAPID keypair in env (`PB_VAPID_PUBLIC_KEY` / `PB_VAPID_PRIVATE_KEY`, documented in `.env.example`); `pywebpush` in `requirements.txt`.
2. `push_subscriptions (id, user_id, endpoint UNIQUE, p256dh, auth, user_agent, created_at, last_success_at, failure_count)`.
3. `POST /api/v1/me/push/subscribe` and `DELETE /api/v1/me/push/subscription` — CSRF-protected, login required.
4. `push` and `notificationclick` handlers in `static/js/sw.js` (bump `CACHE_VERSION`).
5. Reuse the existing notification types as the payload source; **never** put question content or another user's real name in a push body.
6. Per-user opt-in in profile settings (default off), plus quiet hours (no sends 21:00–07:00 local) — this is a minors-facing product.
7. Prune subscriptions after repeated `410 Gone` responses.

**Do not start E5.7 until `docs/MOBILE.md` M5 is done.** Until then, the honest answer to "can we notify users?" is the weekly email digest and the in-app bell.

---

## Definition of done (per item)

- [x] E5.2 richer badges (four new keys, catalog emoji, `scripts/test_milestones_smoke.py`)
- [ ] Remaining items: behaviour matches the rules above, including the edge cases named in the tests section
- [ ] Smoke test added and registered in `scripts/run_smoke_tests.py`
- [ ] Full suite green with `PB_TESTING=1`
- [ ] `CACHE_VERSION` in `static/js/sw.js` bumped if JS/CSS/templates changed (and `scripts/test_pwa_smoke.py` updated)
- [ ] `docs/API.md` updated for any new or changed endpoint
- [ ] `docs/ARCHITECTURE.md` feature table updated; item marked shipped in `docs/AI_HANDOFF.md`
- [ ] Friends-only scope and opt-out settings verified on every social surface
