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
- **Close to a badge**, at most once a day, for example "Two more quizzes for Quiz fan."

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
| Quizzes (learning) | First quiz (bronze, exists) → **Quiz fan** (silver) → **Quiz veteran** (gold) | finish 1, 5 and 25 quizzes |
| Perfect (**new family `perfect`**: a target, Zorp’s antennae spark) | **Full marks** (bronze) → **Bullseye** (silver) → **Flawless** (gold) | 10/10 on 1, 5 and 20 lesson quizzes |
| Lessons (topic_completed) | Lesson learner (exists) → 5, 10, 20 lessons complete (exist) | Lesson learner's next changes to 5 lessons complete |
| Recovery (**new family `growth`**: a sprout that grows) | **Bounce back** (bronze) → **Keeps going** (silver); **Learned from a hint** (bronze) → **Hint hero** (silver); **All fixed** (bronze) | right on a second try (1, 25); right after a hint (1, 25); a retry run with every missed question right |
| Practice (practice) | Practice regular, Practice veteran (exist; **changed to answered right**: 25, 100) → **Problem solver** (gold, 250) | pupils who already hold them keep them |
| Streaks (streak) | **Three in a row** (bronze) → Week warrior → Dedicated (exist) → **Century** (violet) | 3, 7, 30 and 100 days in a row |
| Daily (daily) | Daily starter, Seven days of questions (exist) → **Daily devotee** (gold) | the daily question on 30 days |
| Explorer (explorer) | **Curious** (bronze) → Broad explorer (exists) → **Globetrotter** (gold) | 3, 10 and 25 topics |
| Class work (learning; shown only to pupils in a class) | **Set work done** (bronze) → **Ten tasks done** (silver) | finish 1 and 10 pieces of set work |

That is 18 new badges (19 in the first draft was a miscount); Full marks came in Phase 1, so Phase 2 adds 17. Quiz habit and Hint to habit were renamed Quiz fan and Hint hero when built, because the voice rules keep "habit" out of reward copy. They need:
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
- **"Next up" picks the nearest badge** by progress, not the catalogue order. It shows a bar and a link to where to earn it: "Two more quizzes for Quiz fan. Take a quiz".
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

**Fixed 2026-11-11 (found in the Phase 2 walks).** Phase 1 gave `badge-stage.js` a second function called `part` (the cards as one part of a sequence) in the same scope as `part(id)`, which clones a prop. The later one replaced the first, so from Phase 1 on every badge stage played with no medal and no prop: Zorp, the card and a glow only. The sequence part is now `cardsPart` (still exported as `pbBadgeStage.part`), and `scripts/test_e11_phase2_smoke.py` fails if any celebration script declares one name twice in its top scope. The Phase 1 walks checked the card text and the count, not the medal; the Phase 2 walks also count `.bd-medal`.

---

## 10. Phase 2 built (2026-11-11)

Nothing committed. David's answers 2, 3, 4, 7 and 8 applied; the badges of section 3, with two renames.

**The new badges (17; the catalogue now holds 56).**

| Line (family) | Badges | How (the shelf copy) |
|---|---|---|
| Quizzes (learning) | Quiz fan 📋 silver, Quiz veteran 🗂️ gold | Finish 5 quizzes; finish 25 |
| Perfect (`perfect`, new) | Full marks (Phase 1) → Bullseye 🌟 silver → Flawless 💎 gold | Every answer right on 5 and 20 lesson quizzes |
| Recovery (`growth`, new) | Bounce back 🌱 bronze → Keeps going 🌿 silver; Learned from a hint 💡 bronze → Hint hero 🔦 silver; All fixed 🛠️ bronze | Right after a wrong try (1, 25); right after the bigger hint (1, 25); a retry run of the missed questions, all right |
| Practice | Practice regular, Practice veteran → Problem solver 🧩 gold | Practice questions answered right: 25, 100, 250 |
| Streaks | Three in a row 🕯️ bronze → Week warrior → Dedicated → Century 🏆 violet | 3, 7, 30, 100 days in a row |
| Daily | Daily starter → Seven days of questions → Daily devotee 🗓️ gold | The daily question on 30 days |
| Explorer | Curious 🔎 bronze → Broad explorer → Globetrotter 🌍 gold | 3, 10, 25 topics |
| Class work (learning) | Set work done 📬 bronze → Ten tasks done 📦 silver | 1 and 10 pieces of set work finished |

- Every line has a next step: First quiz now leads to Quiz fan, Lesson learner to 5 lessons complete, Broad explorer to Globetrotter, Dedicated to Century, Seven days of questions to Daily devotee, Practice veteran to Problem solver.
- Full marks moved from `accuracy` to the new `perfect` family.
- **Answered right (answer 4).** Practice regular and Practice veteran now count practice questions answered right (`generator_mcq_attempts` with `correct = 1`, one row per question: the parts of a multi-part question are not counted one by one). Pupils who already hold them keep them.
- **Class work (section 3).** The set-work badges are marked `class_only`: the shelf hides them from a pupil who is not in a class, unless already earned.

**The Recovery line (new data).**
- Two private activity events, `retry_correct` and `hint_correct`. Their payload is the level, subject and topic only. They earn no effort points and are never in a feed.
- `_note_recovery()` in `app.py` watches the tries at the session problem (`last_problem_payload`, replaced for each new question) and keeps small flags on it: a wrong try seen, a hint sent, done. A right answer after a wrong try is `retry_correct`; a right answer after the bigger hint of a question the server sent a hint for is `hint_correct`. Each is recorded once per question.
- The typed checks send `bigger_hint: true` when the page shows rung 2. An MCQ answer after "Try again" now goes to `/api/v1/generator/mcq-answer` as `retry: true`: checked and noted, never recorded as an attempt, so the first answer stays the one in the stats.
- **Show answer closes the question.** Once the pupil has opened Show answer, the page sends `answer_seen: true` with every check, and that question earns no Recovery badge.
- Out: Quick Test, the lesson quiz (session `mode` `lesson`) and the lesson quick checks (not tied to a session problem).

**The quiet back-fill (answer 3).** The migration `e11_backfill_phase2` runs `backfill_quiet_badges()` over 15 keys: every new badge whose history is already recorded (quizzes, perfect quizzes, the cleared retry, answers right, streaks, the daily question, topics, set work), plus Practice regular and Practice veteran under the new rule. Bounce back, Keeps going and both hint badges have no history and start from now. As in Phase 1, there is no stage and no notification, only one corner card on the next page ("You already earned {n} badges").

**Story chapters (answer 7).** The badge counts that open chapters are now 3, 6, 10, 15, 22 and 30 (they were 3, 5, 8, 10, 15, 20).

**The stage and the wardrobe.**
- The `perfect` family plays Zorp's victory and dance with the target rings. The `growth` family plays a nod and a cheer while two sprouts grow up beside the medal (drawn in `badge-stage.js`, `DRAW.sprout`: the stems first, then the leaves). Century, at 100 days, also marks `streak:100`.
- Two new hats, one per family as before: the **crown** (any Perfect badge) and the **sprout** (any Recovery badge). Both are drawn in `templates/partials/zorp_overlays.html` and listed in `models/zorp_kit.py` and `models/zorp_wardrobe.py`.
- **Fixed with it:** two badges of one family that arrive with one answer (Bounce back and Learned from a hint) used to leave both cards without the wardrobe line, because an item was credited only when one earned badge opened it. Now the first one recorded carries the line (`items_unlocked_by()`).

**Browser walks** (Chromium, walk server):

| Walk | What appeared |
|---|---|
| a typed question: wrong, the bigger hint, then right | "1 of 2" Bounce back, bronze medal and two sprouts, "New in your wardrobe: the sprout." and Try it on; then Learned from a hint |
| an MCQ question: wrong, Try again, then right | Bounce back with the sprouts |
| Bullseye, then Flawless | the silver and gold medals on the target rings, Zorp's victory; Bullseye names the crown |
| the crown and the sprout worn, light at 1280 px and dark at 390 px | the hat on the wardrobe preview and on the topic page's Zorp; before a Recovery badge the sprout tile reads "Earn a recovery badge to unlock" |

No console errors on any walk.

**Versions and caps.**
- `site.js` v41, `badge-stage.js` v5, `moments.js` v4, `sw.js` `pb-v125`.
- Caps: `badge-stage.js` 22,500 (22,086 now); the site.js Recovery allowance 1,300 B (804 B for the Recovery wiring, 466 B for `answer_seen`), both with dated ledger notes.
- Tests: `scripts/test_e11_phase2_smoke.py` (new: the catalogue and its next steps, the rules from seeded history, the Recovery line through the real check routes, the back-fill and its one card, the families and hats, the class-only shelf, the client wiring, no shadowed functions). `test_milestones_smoke.py` counts answers right; `test_story_chapters_smoke.py` has the new thresholds.
- Privacy: DPIA log row, ROPA row 2, `SECURITY_AND_GDPR.md` and `API.md`.

**Next.** Phase 3, the shelf (section 4): "Next up" by progress, other subjects behind Show all (answer 8). Then Phase 4, progress around the site and Your week (answer 6).

---

## 11. Phase 3 built (2026-11-11)

Nothing committed. Section 4.1, with David's answer 8. It fixes the shelf problems in 1.3.4: every badge in one alphabetical grid, subjects the pupil does not study, and one grey placeholder for every locked badge.

**Rows by line.**
- `models/badge_shelf.py` builds the shelf; the profile shows it in place of the old grid.
- Each line is a card: the badges earned, in threshold order, then the next one with a progress meter ("3 of 5 quizzes"). A finished line says "All earned".
- The lines, in shelf order: Lessons, Quizzes, Full marks, Practice, Second tries, Hints, Retries, Streaks, Daily question, Explorer, Topic ninjas, Topic masters, Class work (only for a pupil in a class, or once one is earned), then Extras (Pathfinder and Sharp week, which have no count behind them).
- The meters count from the same records that award the badges, so a full meter means the badge comes with the next check. The streak meter counts the run going now, since a streak badge is earned when the run reaches the count.
- A badge whose next step is a single action (First quiz, Bounce back) shows its how-to line instead of a meter.

**Subjects (answer 8).**
- "Your subjects" shows the subject chosen at welcome, every subject the pupil has lessons, quizzes or practice in, and any subject they hold a badge in. The rest sit behind "Show all subjects (n)", a plain `<details>`.
- A subject row is its line (complete, ninja, master), with "0 of 32 lessons"-style meters. The topic badges earned in that subject sit under it.

**Locked badges** show their own glyph, greyed, with a small lock.

**Next up.**
- It points at the line closest to its next badge: the largest share done, then the fewest to go, then shelf order.
- A line that cannot move again today (the streak once studied today, the daily question once answered) comes after the rest, and has no link if it is still the one chosen.
- It shows the badge, a sentence ("Get seven more questions right."), the meter and a link to where to earn it:

  | Link | Goes to |
  |---|---|
  | Open a lesson, Study today | the topic page |
  | Take a quiz | that topic's lesson quiz, if it has one |
  | Try a question | the generator, opened on that topic |
  | Try a new topic | the topic list |
  | Today's question | the daily question |
  | Open class work | class work |
  | Take the tour | Settings |

  "That topic" is the one practised or read most recently, else the one chosen at welcome; with none, the links open the topic list.

**The badge sheet.**
- It now reads every badge from a data island on the page (`#pb-badge-data`: the fields it shows), so it opens any badge by key. That includes a wardrobe "Earn ... to unlock" link whose badge has no button on the shelf (Week warrior, while Three in a row is the next streak badge).
- **Watch again** (earned badges only) closes the sheet and replays that badge on the badge stage. A replay's kicker reads "Your badge", not "New badge".

**Copy.** All shelf copy is in the SHELF COPY block of `models/badge_shelf.py`: row titles, meter units, the one-more and n-more sentences, link labels and labels. It is linted as system voice through `models/zorp_voice.py` `extract_shelf_copy` (71 lines).

**Removed.** The alphabetical grid and `next_up_badge()`, which went by catalogue order. `list_milestone_shelf()` stays for its tests.

**Browser walks** (Chromium; a pupil with 3 quizzes, 18 answers right and five badges, at 1280 px light and 390 px dark):

| Walk | What appeared |
|---|---|
| the shelf | Next up "Practice regular. Get seven more questions right." with 18 of 25 and Try a question (the generator on Pythagoras, the latest practised topic); 13 rows, GCSE Maths under Your subjects with its topic badge, five subjects behind Show all; no sideways scroll |
| Show all | opens in place |
| a locked badge | the sheet: "How to earn it", no Watch again |
| an earned badge | the sheet with its date and Watch again; the replay plays the stage with the medal and "Your badge" |
| a wardrobe link to Week warrior | the sheet opens though the badge has no button on the shelf |

No console errors. Fixed during the walks: the "New" ribbon sat under the smaller medal.

**Versions and caps.**
- `badge-sheet.js` v2 (cap 3,300, was 2,500), `shelf.css` v1 (profile only, not precached, own cap 3,900), `badge-stage.js` v6, `sw.js` `pb-v126`.
- The CSS total is 278,200 (was 274,400), with dated ledger notes in the three tests that hold it.
- Tests: `scripts/test_e11_phase3_smoke.py` (new). It covers the lines against the catalogue, the meters against the rules, the class-only line, the Next up order, subjects and topic badges, the page and its links, the sheet and Watch again, the copy lint and the CSS.
- No new data and no API change, so no privacy document changes.

**Next.** Phase 4: progress around the site (sections 4.2 to 4.4) and Your week (answer 6).

---

## 12. Phase 4 built (2026-11-11)

Nothing committed. Sections 4.2 to 4.4, Your week (2.1, David's answer 6) and Close to a badge (2.2). No phase in section 6 named Close to a badge, so it is built here. With it, every item in sections 2 to 4 is now built.

**Results pages (4.2).**
- **What you earned.** On the page a pupil lands on after a lesson quiz, a strip under the score ring shows:
  - the level bar moving from before this quiz's points to after them (from empty when the quiz crossed into a new level), with "N XP to level M";
  - the topic's mastery path as three chips (Lesson complete, Ninja, Master);
  - the next step in words, for example "One more 10/10 in a row for Master." or "A 10/10 on the quiz makes you a ninja on this topic."

  Reopening the attempt later shows no strip. The "+N XP earned" line stays where it was.
- **Quick Test full marks.** A perfect Quick Test gets its own corner card: "Full marks on the Quick Test. 12 out of 12 marks."
- **Fixed with it: Quick Tests counted as lesson quizzes.** They are saved in the same `quiz_attempts` table, so a perfect Quick Test of 3 marks or more earned Full marks and counted toward Bullseye and Flawless (Phases 1 and 2).
  - A new column, `is_quicktest`, marks them. Older rows are back-filled from their answers: a Quick Test saves each answer as an object, a lesson quiz as text.
  - The Full marks line now counts lesson quizzes only (`_PERFECT_QUIZ_WHERE`).
  - Badges already earned are kept.
  - Topic ninja and master still counted a 10-mark perfect Quick Test, as they always had. David decided on 2026-11-12 that they should not; see 12.1.

**Lesson pages (4.3).**
- For a signed-in pupil on a topic with a quiz, the mastery path chips sit under the lesson's heading (`data-lesson-path`, drawn by `lesson-progress.js`).
- Once every quick check is done, the Lesson complete chip ticks and the quiz bar gains a line: "Lesson done. A 10/10 on the quiz makes you a ninja on this topic." (or the next step for that pupil).
- **Fixed with it:** `components.css` had lost the `.lesson-quiz-cta-bar {` selector line, at least since the git base. Browsers dropped the bar's box and its button rule, so the bar was unstyled. The line is back.

**Today (4.4).**
- Practice page: a Today strip under the greeting, with questions right today, effort points today, the streak and the week's dots.
- Profile: a Today row in the streak panel. The ring and the dots below it are the rest of the card.
- "Questions right" counts:
  - practice questions (whole questions);
  - lesson quiz answers (not retries, and not Quick Tests, whose scores are marks);
  - the daily question.

  The day is UTC, as for the streak.

**Your week (2.1, answer 6).**
- On the first visit of a new week, if last week had a study day, a short stage of up to three cards:
  - "You studied on 4 of 7 days last week." with the week's seven days drawn;
  - "You got 23 questions right.";
  - the best moment: a badge (highest tier), else full marks on a lesson quiz, else the best lesson quiz, else the topic practised most.

  It has one count ("1 of 3"), Continue and Skip all.
- The server offers it on each page until the client saves its flag (`wk:<year>w<week>` in the guide state's ring), so a page that cannot play it loses nothing.
- It plays only on a quiet page; a page with other celebrations leaves it for the next one.
- It spends from the day's budget of 6. With Big moments only or Small cards only, or the budget spent, it is one card: "Your week: you studied on 4 of 7 days."

**Close to a badge (2.2).**
- After a lesson quiz or a Quick Test, when the Next up badge of the shelf is one or two steps away, a card reads, for example, "Nearly there: Quiz fan. Finish one more quiz." with See it.
- It shows at most once a day (`near:<day>` in the guide state's ring) and never beside a new badge.

**Copy.** `models/progress_bits.py` (PROGRESS COPY block, system voice, 22 lines, linted by `extract_progress_copy`) and `moments.js` (12 new lines).

**Browser walks** (Chromium):

| Walk | What appeared |
|---|---|
| Practice and Profile, 1280 px light and 390 px dark | the Today strip ("6 right, 0 XP, No streak yet" and the dots) and the Today row; no sideways scroll |
| BIDMAS: open, all quick checks, then a 10/10 quiz | chips under the heading; Lesson learner, then the lesson stage; the Lesson complete chip ticked and the bar line appeared; the quiz played Ninja and Full marks ("1 of 2"); the results strip showed Level 1, "183 XP to level 2", Lesson complete and Ninja ticked, "One more 10/10 in a row for Master." |
| Your week (4 days, 23 right, Practice regular last week) | three cards with the drawn days, the number and a star; nothing on the next page |
| the three new cards | Close to a badge with See it (its flag saved), Quick Test full marks, Your week as a card |

No console errors. Fixed during the walks: the practice page loaded `around.css` only with a question on screen, so the strip was unstyled without one.

**Versions and caps.**
- `moments.js` v5 (cap 41,500, was 36,500), `lesson-progress.js` v28, `components.css` v36, `around.css` v2 (every page that links it; cap 5,800, was 4,000), `sw.js` `pb-v127`.
- CSS total 281,600 (was 278,200), with dated ledger notes in the three tests that hold it.
- Tests: `scripts/test_e11_phase4_smoke.py` (new). The Phase 1 smoke's pins on the budget line, `spend()` and the ring prefixes follow the new lines.
- Privacy: DPIA log row (the Quick Test mark, and the two kinds of display flag in the guide state).

**What is left.** Nothing in sections 2 to 4.

### 12.1 Quick Tests and the mastery path (2026-11-12)

Built in the cloud (David's laptop was out of reach). Nothing committed. David's answer to the question above: a Quick Test does not count toward a topic's Ninja or Master.
- `topic_status_map` reads lesson quizzes only (`is_quicktest = 0`; the column is checked first, as for `step_total`). The topic status drives every view of it: the Ninja and Master badges, the mastery chips and next step, the topic list's mastery bars, the shelf's topic meters and the subject lines.
- So a perfect Quick Test of 10 marks no longer makes a ninja, and a Quick Test between two 10/10 lesson quizzes no longer breaks a run toward Master.
- Badges already earned are kept. The mastery path also counts a topic's Ninja or Master badge that the pupil holds, so a ninja earned with a Quick Test before this change keeps its chip, and its next step points at Master.
- Tests: `test_quick_tests_make_no_ninja` in `scripts/test_e11_phase4_smoke.py`.

---

## 13. The celebrations gallery (2026-11-12)

Nothing committed. A dev-only page that shows every badge and every celebration, at `/celebrations-gallery` (`python app.py`, then http://127.0.0.1:5000/celebrations-gallery).

- **The gate.** It has the same gate as `/guide-preview`: always on localhost, else only with `PB_STYLEGUIDE=1` or `PB_TESTING=1`, and a 404 on a production HTTPS site.
- **Preview mode** (`data-guide-preview`). Nothing played there is saved to an account. The page never takes the signed-in pupil's own waiting celebrations; they stay for the next real page.
- **Every badge.** All 38 catalogue badges outside the subject lines, by line in shelf order, plus GCSE Maths' three subject badges and the three per-topic badges of Order of Operations as samples. Each badge has:
  - its tier, its family and the wardrobe item it opens;
  - a press that plays its full screen, and a "card" link for its corner card;
  - each line also has Play the line.
- **Full-screen moments.** Level up, a 10/10, Lesson complete (first, another, and with its badge), Your week (three cards), a full sequence (lesson, a badge, level up: "1 of 3" and Skip all), and the 7-, 30- and 100-day streaks.
- **Every corner card.** 24 kinds with sample numbers, and Show them all.
- **Small reactions and the story.** The +XP float, the seven story chapters and the story offer card.
- **Progress around the site.** Static samples of the mastery chips, the quiz bar line, the results strip (with "play the bar again") and the Today strip.
- **Files.** `templates/celebrations_gallery.html` and `static/js/celebrations-gallery.js` (not precached; it loads the badge stage and the moments player the way `guide.js` does). The guide preview links to it.
- **Tests.** `scripts/test_celebrations_gallery_smoke.py`.

### 13.1 The 10/10 redrawn (2026-11-12)

David found the 10/10 stage underwhelming: a gold medal ringed by yellow five-point stars, which read like a flag. The perfect quiz scene (`sealBox` in `moments.js`) now has:
- a cool gem: a glossy cyan, indigo and violet seal with a soft halo that turns behind it;
- seven four-point twinkles in cyan, lilac, pink, mint and ice, scattered rather than in a ring;
- a confetti burst (strips and dots) from the seal as it lands, then a light confetti rain in the same colours.

With reduced motion it is a still scene: the gem, its glow and the twinkles. The topic master badge keeps its own stars prop. `moments.js` v6 (cap 43,500), `moments.css` v3 (cap 5,600), CSS total 282,200, `pb-v128`.

## 14. A topic counts once it is answered in (2026-11-13)

**What David saw.** Curious (3 topics) came when he switched to a third topic, before he answered anything there.

**Why.** The Explorer badges (Curious, Broad explorer, Globetrotter) counted every topic with a `topic_opened` or `question_generated` event, so opening a topic page or being given a new question was enough. The shelf's meter, the badge back-fill and the weekly recap's "topics practised" counted the same way.

**Now.** A topic counts once a question in it is answered:
- a practice check, typed or multiple choice (both log `mcq_answered`, right or wrong);
- a finished quiz;
- a lesson step.

`TOPIC_ANSWER_EVENTS` in `models/gamification.py` is the one list. It is used by:
- `_distinct_topics_count` (the badges, the shelf's meter and Close to a badge);
- the topics back-fill rules;
- the weekly recap.

**Copy.**
- The three badges now say "You answered questions on 3 different topics" and "Answer questions on 3 different topics" (10 and 25 the same way).
- The shelf says "Answer a question on one more topic."

**Badges already earned are kept**, as for every rule change.

**Test.** `test_curious_waits_for_an_answer` in `scripts/test_e11_phase2_smoke.py`, through the real routes. A pupil answers in two topics, then opens a third and is given a question there: no badge, and the count stays at 2. The first answer there earns Curious on that answer, a wrong one included. The test fails under the old rule (checked).

