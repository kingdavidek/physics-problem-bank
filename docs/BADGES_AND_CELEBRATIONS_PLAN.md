# Badges and celebrations plan (E11)

Written 2026-11-10 after David's report: he finished the whole BIDMAS lesson and did not get **Lesson learner**, got **First quiz** with no animation, and scored 10/10 with nothing to mark it. This plan fixes those first (Phase 0), then sets out which events earn a full-screen moment, which earn something smaller, new badges, and improvements to how progress and badges are shown.

Builds on E10 (`docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md`): the stage engine, the badge stage and its 11 family choreographies, moments (`level`, `perfect`, `toast`, `micro`), the wardrobe and the story chapters all exist. Section 7 lists the decisions for David and his answers (7.1). Phases 0 and 1 are built (sections 8 and 9); Phases 2 to 4 are not.

---

## 1. What went wrong (reproduced and confirmed)

### 1.1 Badges and moments delivered with a page never show once the service worker is active

**Symptom.** First quiz was awarded at 16:57 on David's account, and the 10/10 earned a "Full marks" moment, but the results page played nothing.

**Cause.** When our service worker (`static/js/sw.js`) relays a page load, Chrome sends `Sec-Fetch-Mode: navigate` with `Sec-Fetch-Dest: empty` instead of `document`. `_pending_may_emit()` in `app.py` (E10 review fix 7, 2026-11-08) treats any `Sec-Fetch-Dest` other than `document` as a background request, so the page is rendered without its `pb-new-milestones` and `pb-new-moments` islands. The badges stay in the session lists (`pb_ms`, `pb_mm`) and wait there.

**Evidence.**
- Logged headers: with the service worker in control, every navigation in the walk arrived as `mode=navigate, dest=empty`. That covers `/`, `/topics`, `/profile`, and `/quiz-attempts/<id>` after the quiz submit.
- Same walk with service workers blocked: the results page carried both islands, and the First quiz badge stage and the "Full marks, 10 out of 10" stage both played.
- With the service worker allowed, the session cookie still held `"pb_ms": ["first_quiz"]` and `"pb_mm": [{"type": "perfect", ...}]` after the results page had loaded.

**Reach.** Anything handed over with a page rather than with a fetch, for every pupil after their first visit:
- lesson quiz and Quick Test results;
- badges and level-ups earned while a page renders, such as opening topics;
- story catch-up offers;
- anything carried over a redirect after a form post.

Badges that come back in a fetch's JSON still work, which is why the lesson quick checks and the practice page celebrate. Two things hid it during testing:
- A hard reload (Ctrl+Shift+R) bypasses the service worker, so the first page after a reload did show held badges.
- The Flask test client sends no `Sec-Fetch-*` headers, so the smoke tests count every request as a navigation.

**Fix.**
- Treat `Sec-Fetch-Mode: navigate` as a page view whatever `Sec-Fetch-Dest` says.
- Keep refusing requests that carry `Service-Worker`, and modes other than `navigate`. The offline page precache is a `no-cors` fetch, so it stays refused.
- Add test-client cases with real browser headers:
  - `navigate` + `document` emits;
  - `navigate` + `empty` emits;
  - `cors` + `empty` does not;
  - a `Service-Worker` header does not.
- Add a browser walk under an active service worker to the checklist.
- Pending lists already held in sessions (at most 8 badges and 8 moments) play on the next page after the fix. That includes David's First quiz and Full marks, if they are still held (a sign-out or a hard reload since then would have used them up).

### 1.2 Lesson progress in the browser is shared by everyone who signs in on it

**Symptom.** On David's account from today (777), BIDMAS showed as done. Answering the quick checks did nothing and saved nothing, so there was no Lesson learner, no lesson-complete moment and no topic badge. The 10/10 also could not count towards Topic ninja, which needs the lesson complete.

**Cause.**
- `static/js/lesson-progress.js` keeps progress in local storage under `lesson-progress:<level>:<subject>:<topic>`, plus `…:celebrated`. Those keys are not tied to an account.
- On load it ticks every step listed there. A step that is already ticked ignores a correct answer (`markStepComplete` returns early).
- The load-time merge only saves to the server when the server already holds progress for this pupil. A new pupil has none, so nothing is ever sent.

**Evidence.**
- David's database: account 777 (created 9 Nov) has no lesson progress at all, one badge (`first_quiz`) and one BIDMAS quiz at 10/10. Account 774, used on the same browser on 7 Nov, finished all six BIDMAS steps.
- Reproduced with two pupils in one browser. Pupil B opened BIDMAS with all six steps ticked, answered all six correctly, and still had no progress and no badges.

**Why it matters beyond testing.** Pupils share school computers. Today a pupil who signs in after a classmate sees the classmate's ticks and cannot earn their own.

**Fix.**
- Name the keys per account (`lesson-progress:u<id>:…`) and use the plain key only for signed-out reading.
- For a signed-in pupil the server is the record. The local copy is only a cache of that pupil's own progress, and the merge saves whenever this page has steps the server lacks.
- Old plain keys from before the fix are ignored for signed-in pupils, because there is no way to know whose they are. Section 7, question 9 asks whether progress made while signed out should be carried into a new account at sign-up.

Other per-browser keys to name per account in the same sweep:

| Key | Holds | Risk today |
|---|---|---|
| `pb-u74-ms-<badge>`, `pb-u74-streak-<n>` (celebrate.js) | badge or streak already celebrated (fallback path only, when the guide is missing) | a second pupil's badge is silenced if the guide fails to load |
| `pb-guide-v1` (guide.js) | the guide's seen-state, before the server has a copy | before the welcome flow saves, a new pupil reads the last pupil's seen-state and can push it to their own account |
| `pb-buddy-milestone-<badge>`, `pb-buddy-stay-weak_topic-<topic>-<day>`, `pb-buddy-hide-<day>`, `pb-buddy-quiet` (buddy.js, study-buddy.js) | the corner Zorp's "already said that" flags | the next pupil's corner Zorp stays quiet about things it said to the last pupil, and a weak-topic name sits in the key |

The theme (`pb-theme`) belongs to the device and stays as it is.

### 1.3 Smaller things the walk showed

1. **Two beats on the first quick check.** A "First correct" dialog opens, then the Lesson learner badge stage straight after.
2. **Two stages at the end of a lesson.** "Lesson complete" plays, then a second full stage, "New badge: Order of Operations & Negatives lesson complete", says the same thing.
3. **The lesson-quiz spotlight stays on screen during a stage.** Its card sat under the badge and lesson stages and was still there afterwards.
4. **The Milestones shelf is hard to read:**
   - It lists every badge in the catalogue (38 for a new pupil), sorted alphabetically, so "10 lessons complete" comes before "5 lessons complete".
   - Five of the six subjects shown are ones the pupil does not study.
   - Every locked badge shows the same grey placeholder.
5. **Practice regular and Practice veteran count questions started, not answered.** Pressing New question 25 times earns a badge.
6. **Some lines stop early:**
   - First quiz has no next badge.
   - Lesson learner's "next" is First quiz rather than the lessons line.
   - A perfect quiz has a moment but no badge.
   - A perfect Quick Test gets the same corner card as any other score.

---

## 2. The celebration ladder: what earns a full screen

Principle: **full screen for firsts and real milestones, a corner card for good moments, a small reaction for every right answer.** A full screen should feel earned and rare, never routine.

### 2.1 Full screen (the stage)

| Event | Today | Plan |
|---|---|---|
| A new badge | badge stage, choreography by family | keep; several at once become one sequence (2.4) |
| A level-up | level stage | keep |
| Finishing a lesson (every quick check right) | lesson stage, then a second stage for the topic badge (1.3.2) | **one** stage: the lesson scene ends on the topic badge card |
| A 10/10 lesson quiz | perfect stage (lost to bug 1.1) | the first ever earns the new **Full marks** badge (perfect scene plus badge card). The first 10/10 on each topic is full screen. A repeat on the same topic is a corner card with confetti (section 7, question 1) |
| Topic ninja, topic master, subject complete | badge stage; ninja or master replaces the perfect scene | keep |
| Streak of 3 (new), 7, 30, 100 (new) days | 7 and 30 are badges; 100 is a streak round | add the 3 and 100 badges |
| Finishing the app tour | Pathfinder | keep |
| A story chapter opens | corner offer, watched on demand | keep (never plays by itself) |
| **New:** your week | none | the first visit of a new week, if last week had any work: a short skippable stage with three cards (days studied, questions right, best moment). Section 7, question 6 |

### 2.2 Corner card (toast with a small Zorp)

These stay: quiz done, personal best, all fixed (a retry run cleared), Quick Test done, set work done, a week of daily questions, challenge done, weekly skip used, story offer.

New ones:
- **Full marks again** on a topic.
- **Welcome back** after 3 or more days away: "You’re back. Your streak starts again today." (kind, never guilt).
- **Close to a badge**, at most once a day, for example "Two more quizzes for Quiz habit."

### 2.3 Small reaction (micro)

These stay: the tick and sparkle on a right answer, the "+N XP" float, the daily dot, the progress fill on a lesson step.

The **first right answer** becomes a micro moment with one corner line, instead of a dialog that sits in front of the badge stage (1.3.1).

### 2.4 Rules

1. **One full-screen sequence per page.** It holds up to 3 cards in a fixed order:
   1. the scene (lesson done, or Full marks);
   2. badges, highest tier first;
   3. level-up.

   It has one Continue and a "Skip all". Anything beyond 3 cards is kept for the next page.
2. **Merge, never repeat.** A scene that a badge already tells plays once inside that badge's card:
   - Lesson learner with the first right answer;
   - the topic lesson badge with lesson complete;
   - ninja or master with a perfect quiz (this one exists).

   The same badge never plays twice; server awards are unique and the client keeps a seen-state per account.
3. **Never in the way.**
   - Nothing full screen on question pages (already a rule).
   - Nothing during the coach, the arrival film or a tour stop.
   - Spotlights hide while a stage plays and come back after it (1.3.3).
4. **A daily budget.** Badges, level-ups and 10/10 lesson quizzes are always full screen (7.1, answers 1 and 11). Other full screens (lesson complete, your week) are limited to 6 a day; after that they become corner cards (section 7, question 5).
5. **Settings and access.**
   - Already true today: every full screen can be closed at once (Continue is there from the first moment, Esc works, nothing advances by itself). Reduced motion shows a still scene with the words, sound follows the pupil's setting, and each stage is a focus-trapped dialog.
   - **New in Phase 1:** a setting to turn full screens down (7.1, answer 11). Correction, 2026-11-10: an earlier version of this plan said a "full screens off" setting already existed. It does not.
6. **Back-fill quietly.** When new badges ship, badges already earned from history are awarded without stages. One corner card says "You already earned 4 new badges" and links to Milestones.

---

## 3. New badges (proposed)

Each line has a next step, so "Next up" always points somewhere. Effort and recovery are rewarded as well as scores. The copy follows the Zorp voice rules (`docs/ZORP_CHARM.md` 3.3).

| Line (family) | Badges (tier) | How |
|---|---|---|
| Quizzes (learning) | First quiz (bronze, exists) → **Quiz habit** (silver) → **Quiz veteran** (gold) | finish 1, 5 and 25 quizzes |
| Perfect (**new family `perfect`**: a target, Zorp’s antennae spark) | **Full marks** (bronze) → **Bullseye** (silver) → **Flawless** (gold) | 10/10 on 1, 5 and 20 lesson quizzes |
| Lessons (topic_completed) | Lesson learner (exists) → 5, 10, 20 lessons complete (exist) | Lesson learner's next changes to 5 lessons complete |
| Recovery (**new family `growth`**: a sprout that grows) | **Bounce back** (bronze) → **Keeps going** (silver); **Learned from a hint** (bronze) → **Hint to habit** (silver); **All fixed** (bronze) | right on a second try (1, 25); right after a hint (1, 25); a retry run with every missed question right |
| Practice (practice) | Practice regular, Practice veteran (exist; **changed to answered right**: 25, 100) → **Problem solver** (gold, 250) | pupils who already hold them keep them |
| Streaks (streak) | **Three in a row** (bronze) → Week warrior → Dedicated (exist) → **Century** (violet) | 3, 7, 30 and 100 days in a row |
| Daily (daily) | Daily starter, Seven days of questions (exist) → **Daily devotee** (gold) | the daily question on 30 days |
| Explorer (explorer) | **Curious** (bronze) → Broad explorer (exists) → **Globetrotter** (gold) | 3, 10 and 25 topics |
| Class work (learning; shown only to pupils in a class) | **Set work done** (bronze) → **Ten tasks done** (silver) | finish 1 and 10 pieces of set work |

That is 19 new badges. They need:
- **Two new choreographies** (`perfect`, `growth`) in the badge stage, and **two new wardrobe items**, one per family as now.
- **New data** for the Recovery line, since the rest is already recorded:
  - a right answer on a second try (the quick checks save only the first attempt today);
  - a right answer after a hint was opened.

  Both would be small private activity events. Other badges come from existing tables, so they can be back-filled.
- **Re-tuned story chapter thresholds.** With more badges, chapters open faster. Proposed counts: 3, 6, 10, 15, 22, 30 (today 3, 5, 8, 10, 15, 20).

---

## 4. Showing progress and badges

### 4.1 The Milestones shelf

- **Rows by line**, in threshold order. Each row shows the badges earned, then the next one with a progress meter ("3 of 5 quizzes").
- **Only relevant subjects.** The pupil's own subjects (studied, or chosen at welcome) are shown; the rest sit behind "Show all".
- **Locked badges** show their own glyph in grey with a small lock, not a shared placeholder.
- **"Next up" picks the nearest badge** by progress, not the catalogue order. It shows a bar and a link to where to earn it: "Two more quizzes for Quiz habit. Take a quiz".
- **"Watch again"** in the badge sheet replays that badge's celebration.

### 4.2 Results pages

- **What you earned.** A strip under the score ring: the XP, with the level bar moving, and the topic's mastery path (Lesson complete · Ninja · Master) with the next step in words. For example: "Finish the lesson’s quick checks for Ninja", or "One more 10/10 in a row for Master".
- **Quick Test full marks.** A perfect Quick Test gets the corner card "Full marks". Quick Tests do not count towards the Perfect line, which is for lesson quizzes.

### 4.3 Lesson pages

- **Mastery path.** The three steps of the topic's path appear at the top as small chips.
- **The end-of-lesson quiz bar** changes once the quick checks are done: "Lesson done. A 10/10 on the quiz makes you a ninja on this topic."

### 4.4 Profile and Practice

- **A "Today" card.** Questions right, XP and the streak, with the week's dots that exist already.

---

## 5. Engineering notes

- **One celebration director on the client.**
  - guide.js already queues badges, then moments. That queue becomes the single place that sorts, merges and budgets everything arriving in one beat: JSON from a fetch, the page islands, and the lesson-complete call from lesson-progress.js.
  - It holds items for about 300 ms so a badge and its scene arrive together, then plays one sequence.
  - It tells the spotlight and tour code when a stage starts and ends.
- **The server stays the source of truth** for badges, moments and the budget count (a small per-day counter in the protected guide state). The client never invents a badge.
- **Tests:**
  - browser headers in the delivery tests (1.1);
  - two pupils on one browser (1.2);
  - the merge and budget rules;
  - back-fill awarding without stages;
  - the new badge rules against seeded history;
  - voice lint for all new copy.
- **Caps and versions:** byte caps raised with dated ledger lines, `?v=` and the `sw.js` cache version bumped, as usual.
- **Privacy.** The new events (second-try right, hint then right) are private, have no free text, and follow the existing activity events in export and erasure. DPIA and ROPA get one line each.

---

## 6. Phases

| Phase | What | Size |
|---|---|---|
| **0. Fixes** | 1.1 navigations under the service worker; 1.2 per-account browser storage (and the other keys in the table); 1.3.1 and 1.3.2 merge the double beats; 1.3.3 spotlights wait for stages. Tests for each, and a browser walk with the service worker active and two pupils on one browser | small, first |
| 1. The ladder | the director (5), the rules (2.4), the Full marks badge and the 10/10 repeat rule, Welcome back | medium |
| 2. New badges | section 3: catalogue, rules, the two events, back-fill, two choreographies, two wardrobe items, story thresholds | medium to large |
| 3. The shelf | section 4.1 | medium |
| 4. Progress around the site | 4.2 to 4.4, and Your week | medium |

After Phase 0 on David's laptop:
- Account 777 shows its held First quiz and Full marks once, on the next page, if they are still in the session.
- BIDMAS shows fresh on that account, because the ticks were 774's. Redoing its quick checks earns Lesson learner, the lesson moment, the topic badge and Topic ninja, since the 10/10 is already on record.

---

## 7. Decisions for David

1. **Repeat 10/10s.** Full screen the first time on each topic and a corner card after that (proposed), or full screen every time?
2. **New badge lines** (section 3). All of them, or which ones?
3. **Back-fill.** Award history-based badges quietly with one summary card (proposed), or play each one?
4. **Practice regular and veteran.** Change them to count questions answered right (proposed; holders keep them)?
5. **Daily budget.** 6 non-badge full screens a day, then corner cards (proposed)? A different number?
6. **Your week.** Yes or no? If yes, on the first visit of each week (proposed)?
7. **Story chapters.** Re-tune the thresholds to 3, 6, 10, 15, 22, 30 (proposed)?
8. **The shelf.** Hide other subjects' badges behind "Show all" (proposed)?
9. **Signed-out progress.** When someone reads lessons signed out and then makes an account, carry that progress into the new account, or start fresh (proposed, simpler and safe on shared computers)?
10. **Order of work.** Phase 0 now on its own (proposed), then the rest after your answers?

### 7.1 David's answers (2026-11-10)

1. **Full screen every time** for a 10/10 lesson quiz, on every topic and every repeat (not the proposal). This changes 2.1: the "Full marks again" corner card is dropped, and the first 10/10 ever still earns the Full marks badge.
2. All 19 new badges.
3. Back-fill quietly with one summary card.
4. Practice regular and veteran count questions answered right; holders keep theirs.
5. A budget of 6 non-badge full screens a day, then corner cards.
6. Your week: yes, on the first visit of each week.
7. Story thresholds 3, 6, 10, 15, 22, 30.
8. Other subjects' badges behind "Show all".
9. No: signed-out progress is not carried into a new account. A signed-in pupil never reads the signed-out keys.
10. Phase 0 first, on its own.

11. **(Follow-up, same day.)** A 10/10 lesson quiz skips the daily budget, so it is full screen every time. Pupils also get an option to skip full screens.

    David confirmed this form (2026-11-10): a Settings choice, **Celebrations**, with three values, and the link below.
    - **Full screen** (the default);
    - **Big moments only**: badges and level-ups full screen, everything else as corner cards;
    - **Small cards only**: every stage becomes a corner card; badges still show their card, and nothing is lost from Milestones.

    The 10/10 screen also gets a quiet link, "Show these as a small card", which sets that pupil's 10/10s to corner cards from then on and can be undone in Settings.

---

## 8. Phase 0 built (2026-11-10)

Nothing committed.

**1.1 Pages relayed by the service worker.**
- `_pending_may_emit()` in `app.py` now treats `Sec-Fetch-Mode: navigate` as a page view whatever `Sec-Fetch-Dest` says, except a frame (`iframe`, `frame`, `embed`, `object`, `fencedframe`).
- Still refused: a `Service-Worker` header, any other mode, and, when no mode is sent, a `Sec-Fetch-Dest` other than `document`.
- Test: `test_e11_service_worker_navigation_reads_pending_lists` in `scripts/test_celebration_moments_smoke.py` uses the exact headers Chrome sends:
  - a relayed page and a direct page both emit, once;
  - fetches, a frame and the worker's own fetch do not;
  - a real 10/10 lesson quiz, opened through a relayed results page, carries First quiz and the perfect moment.

**1.2 Per-account browser storage.**
- `_storage_ns()` in `app.py` gives each signed-in page `<meta name="pb-store">`. The value is `a` followed by 12 hex characters of an HMAC-SHA256 of the account id, keyed with the app secret, so the id itself never appears. It is empty when signed out.
- The scripts add that name to every key that holds one pupil's state, and remove the old shared key unread:

  | Script | New key | Old key, removed |
  |---|---|---|
  | `lesson-progress.js` | `lesson-progress:<ns>:<level>:<subject>:<topic>` and `…:celebrated`; signed out `lesson-progress:anon:…`, which a signed-in pupil never reads (answer 9) | `lesson-progress:<level>:<subject>:<topic>` |
  | `guide.js` | `pb-guide-v1:<ns>` (`:anon` signed out) | `pb-guide-v1` |
  | `celebrate.js` | `pb-ms:<ns>:<badge>`, `pb-streak:<ns>:<n>` (fallback path only) | `pb-u74-ms-…`, `pb-u74-streak-…` (no longer read) |
  | `study-buddy.js` | `pb-buddy-quiet:<ns>` | `pb-buddy-quiet` |

- A signed-in page with no storage name keeps nothing in the browser and relies on the server.
- The lesson page now saves steps the pupil's own copy has and the server lacks, even when the server has no row yet.
- `buddy.js` is not loaded by any page, so it was left alone.
- DPIA: one new risk row (shared school computers).

**1.3 One beat, not two.**
- **First correct.** The dialog waits 1.8 s in `guide.js` (the confetti and Zorp's cheer do not wait). A badge, a stage or a moment in that time replaces it, and it is marked seen.
- **The last quick check.** It saves at once, and the lesson stage waits up to 2.5 s for the reply. If the reply carries `topic_completed:<level>:<subject>:<topic>`, the stage adds "New badge: {title}." and keeps "Try the quiz". `guide.js` takes that badge out of the queue, or keeps it out if it arrives later, and `moments.js` marks it seen when the stage plays.
- **Spotlights.** An open spotlight hides, with its outline, while anything else is on screen. It comes back, re-placed, after (`zorp-tour.js`, checked every 300 ms).

**Browser walks** (scratch scripts, Chromium, the service worker in control, two pupils on one browser):

| Pupil and step | What appeared |
|---|---|
| A, first quick check | Lesson learner stage only, no First correct dialog; the spotlight hid and came back |
| A, last quick check | one stage, "Lesson complete … New badge: Order of Operations & Negatives lesson complete." with Try the quiz |
| A, quiz 10/10, relayed results page | First quiz, then Topic ninja ("1 of 2", "2 of 2") |
| B, same browser after A signed out | no ticks on load; Lesson learner earned and saved |
| B, quiz 10/10 | First quiz, then Full marks |
| a first right answer on Practice with no badge | the First correct dialog, after the hold |

At 390 px in dark mode the lesson stage fits: no sideways scroll, both buttons visible.

**Versions and caps.**
- `guide.js` v27, `celebrate.js` v15, `lesson-progress.js` v27, `study-buddy.js` v30, `zorp-tour.js` v4, `moments.js` v2, `sw.js` `pb-v123`.
- Caps: `zorp-tour.js` 35,200 and `moments.js` 24,600, both with dated ledger notes.
- New smoke: `scripts/test_e11_phase0_smoke.py`.

**On David's laptop after the restart.**
- Account 777's held First quiz and Full marks show once, on the next page, if they are still in its session.
- BIDMAS starts with no ticks on that account. Redoing the quick checks earns Lesson learner, the lesson stage with its badge, and Topic ninja, because the 10/10 is already on record.

---

## 9. Phase 1 built (2026-11-10)

Nothing committed. David's answers 1, 3, 5 and 11 applied.

**The Celebrations setting.**
- Two new columns on `user_profile_settings`: `celebration_mode` (`full` by default, `big` or `small`) and `perfect_as_card` (0 by default).
- They are saved by the settings form and by `PATCH /api/v1/me/settings` (`invalid_celebration_mode` for a bad value), kept by every other save, and put on `<body>` as `data-pb-celebrate` and `data-pb-perfect-card` for the client.
- The settings page has a **Celebrations** section with the three choices and a switch, "Show full marks on a quiz as a small card".
- What each choice does:

  | Choice | Full screen | Corner card |
  |---|---|---|
  | Full screen | everything | a finished lesson once the day's budget is spent; a 10/10 when the switch or the link is on |
  | Big moments only | badges and level-ups | finished lessons and 10/10s |
  | Small cards only | nothing | everything; several badges in one moment are one card ("3 new badges: ...") so a phone is not covered |

- **The quiet link.** The 10/10 stage has a link, "Show these as a small card". It saves `perfect_as_card`, closes the stage and confirms in a card with a Settings link.

**One sequence per page (rule 1).**
- `guide.js` waits one beat (`BEAT_MS` 300) and then hands the moments and the badges of that beat to `moments.js` together.
- `moments.js` plays one sequence: the scene (a 10/10 or a finished lesson), then the badges, highest tier first (violet, gold, silver, bronze), then the level-up. It holds at most 3 cards, shows one count ("1 of 3") and has a **Skip all**.
- The badge cards come from `badge-stage.js`, which now exposes `part()`; its own `play()` is built on that part.
- Cards past 3 wait in the tab's session storage (`pb-celebrate-next:<storage name>`), and the next page plays them.
- Things that wait for the moments, such as a story offer, come after the last card.

**The daily budget (rule 4).**
- At most 6 full-screen finished lessons a day; after that they become corner cards.
- A 10/10, a badge and a level-up never count (answer 11).
- The count is `fs:<day>:<n>` flags, which the guide state keeps in its evictable ring (`fs:` added to the volatile prefixes in `models/social.py`).

**Full marks (`perfect_1`).**
- The first 10/10 on a lesson quiz earns it: not a retry run, at least 3 questions, every answer right (the same rule as the perfect moment).
- Its badge stage replaces that 10/10's perfect stage; every later 10/10 is the perfect stage, every time (answer 1).
- Family `accuracy`, with a bigger dance (`victory`). A family of its own needs a wardrobe item, and every look the live Zorp can draw is already in the wardrobe. Phase 2 decides the Perfect line's family when the new cosmetics are drawn.

**The quiet back-fill (rule 6).**
- `user_milestones.quiet` records how a badge arrived: 0 earned live, 1 back-filled and not yet told, 2 told.
- The migration `e11_backfill_perfect_1` gives Full marks to everyone with a 10/10 on record. It plays no stage and sends no notification. The earned date is the first such quiz.
- The next page the pupil looks at shows one corner card: "You already earned a badge: Full marks. It is on your profile." (or "{n} new badges").
- Phase 2 adds its badges to `BACKFILL_RULES`.

**Welcome back (2.2).**
- The first study day after 3 or more days away shows a corner card: "You’re back. Your streak starts again today.", or "You’re back. Good to see you again." when the streak survived.
- No card when a weekly skip kept the streak, because that has its own card.

**First right answer (2.3).** A corner card, "Your first right answer. Nice work.", replaces the dialog. It still waits 1.8 s, and gives way to a badge in the same moment.

**Browser walks** (Chromium, the service worker in control):

| Walk | What appeared |
|---|---|
| a whole lesson, then a 10/10 | Lesson learner; one lesson stage with its badge; then "1 of 3" Topic ninja, First quiz, Full marks, with Skip all |
| five badges at once | violet, gold and silver in the first sequence; the two bronze ones on the next page; Skip all closes |
| the link on a second 10/10 | the 10/10 stage with "Show these as a small card"; the setting saved and a confirmation card; the third 10/10 was a card |
| Small cards only, at 390 px | Lesson learner, the lesson (naming its badge) and one "3 new badges" card, then the story offer |
| the budget spent | Lesson learner still full screen, the finished lesson a card |

**Versions and caps.**
- `guide.js` v28, `moments.js` v3, `moments.css` v2, `badge-stage.js` v4, `sw.js` `pb-v124`.
- Caps: `moments.js` 36,500 and `badge-stage.js` 20,000, both with dated ledger notes.
- Tests: `scripts/test_e11_phase1_smoke.py` (new). The perfect-moment tests in `test_celebration_moments_smoke.py` now give the account Full marks first.
- Privacy: DPIA row, ROPA row 1, both privacy notices, `SECURITY_AND_GDPR.md` and `API.md`.

