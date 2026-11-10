# Zorp arrival, app tour and celebrations: plan (E10, 2026-11-08, approved, building)

**Status:** approved by David on 2026-11-08 with the answers in section 10, which override anything above them. Building phases 1 to 4 first (stage engine, arrival, first question, badges), then David decides the rest.
**Why:** David made a new account and found the start underwhelming: "not back story to zorp really, and no introduction to the functionality across the app". He asked for an ambitious plan that puts the Zorp animation work to good use, finds more places for animation, celebrations and full-screen moments, and makes badges properly described and celebrated ("a layover screen with a dance and something else depending on the badge").
**Companions:** `docs/ZORP_EXPRESSIVENESS.md` (E8 rig, faces, clips), `docs/ZORP_CHARM.md` (E9 voice, soft body, sound), `docs/MASCOT_MOTION_AND_ONBOARDING.md` (E7 welcome), `docs/ANIMATION_ONBOARDING.md` (E6 guide), `docs/ENGAGEMENT_E5.md` (streaks, XP), `docs/SECURITY_AND_GDPR.md`, `docs/DPIA.md`.

---

## 1. What a new pupil sees today, and what we already have

### 1.1 Today (walked as a new account on 2026-11-07)

1. `/welcome`, four screens: "Hi, I'm Zorp. I live in Problem Bank and I'll cheer you on.", pick what to practise, pick a first topic, start.
2. The origin story on the next page: 6 beats, 11 short lines, one click each, in a dialogue box. Novara, "my crew", a homesick line, "I'll cheer and nudge", a list of the five tab names.
3. First-visit tours, one or two lines per tab (Practice 3 to 4, Learn 2, Daily 2, Compete 2, Profile 1 to 3; steps vanish when their target is not on screen).
4. Rewards: first correct, a badge (one line for every badge: "You earned this."), streak 7/30/100, first lesson complete.

What is missing: any scene or story beyond three lines; anything about how the site works (the hint after a try, bigger hint, Show answer, lessons and quizzes, AI explain, Quick Test, Daily, revision plan, saved questions, classes and set work, notes); a proper badge moment; most wins go uncelebrated.

### 1.2 The toolkit we built (E7 to E9), mostly unused by onboarding

- **Runtime** `window.pbZorp`: `play(clip, {face, view, facing, target, cue})`, `react(kind)`, `setExpression`, `pose`, `turn(view, facing)` (front, three-quarter, side, back, back-glance), `say(target, text)` with mouth flaps, `idle`, `motionLevel()`, `register()` for extensions.
- **13 beat clips:** cheer, hop, wave, fist-pump, victory (stars), flex, shrug, bow, think-chin (bulb), dance (notes; trip variant), float, oops-encourage, turn. Legacy: blink, wobble, think, point, peek, sleep, side-point, look-around. CSS gestures: wink, nod, shake, tap.
- **23 poses** (sit, crouch, peek, point-down, dance-a/b/up, float, sleep, victory, flex ...), **31 face presets** across eyes, brows, mouth, cheeks and fx (stars, flame, zzz, sparkles, hearts, notes, bulb, thought), soft body squash and stretch.
- **Cosmetics** (automatic only): colours violet, sunny, mint; antennae; hats mortarboard and beanie; sneakers; three live looks (scholar, jump, wave); a static pose kit (showman, scholar, explorer, chef).
- **Effects:** confetti (40 bits), sparkle bursts, XP float, streak flame, drawn tick; WebAudio cues (jump, land, tada) behind the opt-in "Zorp's sounds" setting.
- **Guide overlay** with story, tour (spotlight) and reward modes; reward queue; seen-state in `guide_json`; Replay intro and Replay welcome in Settings; motion levels full, reduced, off.

### 1.3 Gaps found while reading the code

- Badge descriptions disappear once earned (`profile.html:468-474`); the reward overlay never shows them; per-topic badges show as "New badge" with a generic title (`guide.js` `lookupMilestone`); only the newest badge of the last 24 hours is celebrated, so two badges at once means one is never celebrated; a badge earned in a quiz waits for the next ordinary page.
- The "+10 XP" float and the "+score × 5 XP" line on quiz results do not match the real effort points (1 per question, 3 per quiz, 2 per lesson step). Levels exist (`50 × L²`) but nothing happens on a level-up.
- Badge `streak_7` and reward `streak:7` can both fire for the same day.
- No celebration for: lesson-quiz perfect score, Quick Test results, Daily answered or a full week, level-up, retry-wrong cleared, set work done, challenge completed, revision item done, personal best.
- Set work answers and typed practice checks do not record a study day, so they never move streaks or badges.

---

## 2. Principles (unchanged rules this plan keeps)

1. **Show, do not tell.** Every intro beat either plays a scene or points at the real thing on screen.
2. **Always skippable, never trapping.** Skip on every story and tour step; Esc closes; one tap to continue.
3. **Every beat ends positive or neutral** (E8 valence rules, `CONTEXT_MAP`, lore steps carry a positive `resolve`).
4. **Bot, not a person; 13+; no guilt, urgency, loss or comparison language; no reaction to absence or hesitation** (ZORP_CHARM 3.3, Children's Code std 13). Promises must be true.
5. **Motion levels are respected everywhere:** full plays scenes; reduced shows still frames with a fade; off shows text and the medal only. Sound stays opt-in.
6. **No libraries:** transform and opacity only, SVG built from templates, no Lottie, GSAP, Rive or CDN; CSP unchanged.
7. **Light pages:** new scene code loads only when a scene plays (same-origin script, allowed by `script-src 'self'`), so ordinary pages do not grow.
8. **Honest numbers:** any XP shown is the real figure.

---

## 3. Part A: the arrival (first run)

### A1. The arrival story: a short animated film in six scenes

A new full-screen **stage** (section 6.1) replaces the welcome hello screen and the dialogue-box origin story with one continuous piece, about 60 to 90 seconds, every scene skippable. Draft script (all lines go through the voice lint; Zorp lines at most 100 characters):

| Scene | On screen | Zorp | Lines (draft) |
|---|---|---|---|
| 1. Arrival | CSS starfield drifting; a small light streaks down | `float` in from the top, lands (soft-body jelly), `wave`, face `happy` | "Hi, I'm Zorp. I'm a maths and physics bot from a planet called Novara." |
| 2. Novara | A ringed planet rises behind him; the ring is the maths belt, made of drifting numbers and symbols | `turn` to three-quarter to look up at it, `think-chin`, bulb fx | "On Novara, everything runs on puzzles. Doors open when you solve them. Even the toaster." / "Out past it is the maths belt: a ring of rocks covered in numbers." |
| 3. The mission | A logbook prop opens beside him | `point-down` at the book, `nod` | "My crew and I came to Earth to learn how people here solve problems." / "I keep a logbook. When you reach something new, I stamp a page in it." |
| 4. The crew (D2) | A ship window with three Novarans (Zorp's rig in sunny and mint colours, other antennae) waving | `turn` back-glance to them, then front, `wink` | "That's my crew on the ship. They're keeping the engine warm." |
| 5. How I help | A small mock question card: a wrong tick, then the hint card slides up | `side-point` at the card, face `soft-smile` | "Try a question first. If it goes wrong, I'll show you a hint." / "I'm a bot, not a person. You can skip me any time." |
| 6. Your turn | The welcome cards (level, then topic) inside the stage | `think-chin` while choosing, `cheer` on each pick, `fist-pump` on Start | "What do you want to practise?" / "Good choice. Your first question is ready." |

- The homesick lore line moves to a later chapter (A6), so the first minute is upbeat.
- The level and topic choices stay real forms (`welcome_step`), so nothing about saving the choice changes.
- Reduced motion: each scene is a still frame with a fade; off: text and buttons only.
- Replay from Settings ("Replay the arrival"), which replaces Replay intro and Replay welcome.

### A2. A guided first question ("practice run")

The first question after the arrival is coached live by a new **coach** mode: short tour steps that wait for real events instead of Next buttons.

1. Spotlight on the answer box: "Type your answer and press Check." (waits for `pb-answer-checked`)
2. If right: the `first_correct` moment (B4) with `victory`.
3. If wrong: spotlight on the Hint card: "Here's a hint. I only show them after you try." Then on "Show a bigger hint": "Want more? This gives the first step." Then on the greyed Show answer, now open: "And here's the full answer whenever you want it."
4. Signed-in: a one-line pointer to "Add a note".
5. Close: "That's the loop: try, hint, try again. Want me to show you round the rest?" with **Show me around** and **Later** (D5).

Needs small events dispatched from `site.js` (`pb-answer-checked`, `pb-hint-shown`, `pb-hint-bigger`, `pb-answer-unlocked`), and the same for multiple choice (`mcq-correct` already exists).

### A3. "Show me around": one tour across the whole app

A cross-page tour that walks the tab bar in one go. Between pages Zorp `turn`s to side view and `hop`s along the tab bar to the next tab (desktop: the top nav). Tour progress lives in `guide_json` so it survives page loads. About 14 stops:

- **Practice:** topic picker; Standard or Multiple Choice and difficulty; the hint card and Show answer (if a question is on screen); Save and Share.
- **Learn:** topic list and status chips (completed, ninja, master); a lesson's sections and quick checks; the lesson quiz and "AI explain this question"; Retry wrong ones.
- **Quick Test:** where to start one and what the results show.
- **Daily:** today's question; the week board (friends only, no public ranking).
- **Compete:** friends board, challenges (optional, no chat), following.
- **Profile:** streak and the weekly skip; level ring and effort points; the logbook (badges); saved questions; revision plan; quiz history.
- **Classes** (only if the pupil is in a class): set work.
- **Settings:** motion, sounds, replay.

Ends with a short stage scene: Zorp `bow`s, then the first logbook stamp, **Explorer** (a new badge for finishing the tour, D10).

### A4. Just-in-time spotlights

Short spotlights the first time a pupil meets a feature anywhere, so pupils who skip the tour still learn it: the first hint card, first bigger hint, first lesson quiz, first Quick Test, first AI explain, first set work, first challenge, first revision plan item, first saved question. Each is one or two lines with a real target, shown once (seen-state per spotlight id). They replace most of today's per-tab tours, which are rewritten to say what you can do there (A5).

### A5. Copy rewrite

All guide lines rewritten against the voice guide: the five tab tours, rewards, spotlights, the arrival script. One pun per tour at most, jokes pointing at Zorp.

### A6. Logbook chapters (stretch, D3)

Zorp's story continues in small chapters unlocked by logbook stamps: a short stage scene every few badges (for example the maths belt at 3 stamps, the crew's ship at 5, the homesick line resolved warmly at 10, "Novara's puzzle doors" at a first topic master). Optional, never blocking, replayable from the logbook.

---

## 4. Part B: celebrations

### B1. Three sizes of celebration

| Size | When | What |
|---|---|---|
| **Micro** (inline) | each correct answer, a hint that led to a right answer, a revision item done, a Daily answer | existing pop and tick, a sparkle, corner Zorp `react` |
| **Toast** (corner card with mini Zorp) | lesson quiz finished, Quick Test finished, set work done, challenge completed, streak skip used, personal best | Zorp face plus one line and a link ("Retry the 3 you missed") |
| **Stage** (full screen) | a badge, a level-up, streak 7/30/100, a perfect lesson quiz, a topic mastered, a subject complete, the end of the tour | full-screen scene with medal, Zorp choreography, description and next step |

At most one stage per page view; others queue (B3). Never inside the quiz runner while questions are on screen; quiz results pages may show them.

### B2. The badge stage ("a stamp in the logbook")

Each badge gets a full-screen moment:

1. Backdrop dims; a light burst behind the centre.
2. The logbook opens; the badge medal drops in and "stamps" the page (scale, a soft thud, sparkle ring).
3. Zorp plays the badge's **choreography** (B2.1), with the matching face and fx.
4. Text: the badge title, **what you did** (past tense, specific: "You answered the question of the day on 7 different days."), and **what's next** ("Next stamp: 30 different days.").
5. Buttons: **Continue** and **See my logbook**. Optional opt-in sound cue (tada).
6. Two or more badges at once: "2 new stamps", one after another, then a summary page.

#### B2.1 Choreography by badge family (all from the existing library plus the new stage props)

| Badge family | Medal and props | Zorp |
|---|---|---|
| Streak (`streak_7`, `streak_30`, streak 100) | flame medal, flame burst, the week dots lighting up | `fist-pump` then `flex`, flame fx; 100 days: `victory` then `dance`, `aww-teary` resolving to `proud` (already the rule) |
| Daily (`qotd_first`, `qotd_7`) | sun rising over a calendar strip | `wave` then `hop`, face `happy` |
| Practice volume (`questions_25`, `questions_50`) | a stack of question cards fanning out | `dance` with notes |
| Explorer (`topics_10`) | a map unrolling with pins | explorer look from the pose kit, `float` across the map |
| Learning (`first_quiz`, `first_lesson_step`) | a book and mortarboard | the mortarboard hat drops onto Zorp, `bow` |
| Topic completed | bronze medal | `cheer` |
| Topic ninja | silver medal, a quick spin | `turn` back then front (a "ninja" spin), `victory` |
| Topic master | gold medal, stars | `victory` then `float`, stars fx, face `proud` |
| Subject complete (completed, ninja, master on every topic) | a full page of stamps, confetti rain | `dance`, then wears the subject's hat, `fist-pump` |
| `accuracy_top_friend` | see D9 | quiet: `nod`, no comparison wording |
| Explorer tour badge (new) | the tab bar lighting up | `bow` |

### B3. Fixing how badges work

- **Descriptions everywhere:** every badge gets `blurb` (what you did), `how` (how to earn, shown while locked) and `next` (the next tier, if any). Earned badges keep their description on the profile; tapping one opens a detail sheet with the medal, Zorp in the family pose, the date and what's next.
- **Per-topic and subject badges** get real titles and blurbs in the overlay ("Topic master: Pythagoras").
- **Immediate delivery:** routes that can award a badge return `new_milestones` (the client already handles it in `pbCelebrate.fromPayload`), and a small server-side **pending celebrations** list (in the session, no new personal data) carries a moment across a page load, including out of the quiz runner to its results page. The 24-hour single-badge island goes.
- **No double moments:** `streak_7` badge and `streak:7` reward merge into one stage.
- **The profile section** becomes **Zorp's logbook** (D3): pages of stamps, locked pages showing how to earn them, the badge count without the huge locked total (show "12 stamps" and "next up: ..." instead of "12 / 140").

### B4. New moments to celebrate (with their hook points)

| Moment | Size | Hook |
|---|---|---|
| First correct (exists) | stage, smaller | keep; reuse `victory` |
| Lesson quiz finished | toast; perfect score: stage | `lesson_mcq_submit` and `_render_quiz_results` (`app.py` 2228, 11150) |
| Quick Test finished | toast with the score ring counting up | `quicktest_results` (11276) |
| Level-up (new) | stage: the level ring fills and rolls over, `flex` | compare `lifetime_effort_xp` levels before and after in `_record_study_activity` (4304) |
| Daily answered | micro; a full week of Daily: toast | `api_v1_qotd_answer` (11874), `qotd_page` POST |
| Streak skip used | toast, informative and kind: "Your weekly skip kept your streak going." | streak update in `record_study_day` |
| Retry wrong cleared | toast: "All fixed." | `lesson_mcq_retry_wrong` and `quicktest_retry_wrong` results |
| A hint, then right | micro: "Got there with a hint." | `site.js` ladder state plus a correct check |
| Set work done | toast; whole assignment done: stage | `submit_student_answer` (`models/class_assignments.py`), plus D11 |
| Challenge completed | toast, no win or lose language | `challenge_detail` POST and `api_v1_challenges_submit` |
| Revision item done | micro | `api_v1_revision_queue_complete` (8696) |
| Personal best quiz score on a topic | toast | `recent_accuracy_trend` |
| Lesson complete (exists) | stage, every lesson (not only the first), smaller after the first | `lesson-progress.js` |

Not included, on purpose: anything reacting to a break or absence ("welcome back"), streak-at-risk overlays, or comparisons with friends (voice and safeguarding rules).

### B5. Honest XP

The answer float shows the real effort points (+1 for a question; quizzes and lesson steps their real values), or no number (D10). The quiz results "+score × 5 XP" line shows the real figure.

---

## 5. Part C: more Zorp around the site

| Place | Animation |
|---|---|
| First hint card | a 40 px Zorp peeks from the card's edge and `side-point`s at it (backlog item from E7) |
| Show answer opening | a small sparkle on the bar as it un-greys |
| AI explain and question generating | `think-chin` with the bulb while waiting |
| Quiz and Quick Test results | the score ring counts up; Zorp face by score band (always positive or neutral) |
| Daily | the week dot fills with a pop when answered |
| Profile | the level ring animates once per visit; new stamps have a "new" ribbon; Zorp wears the newest earned hat (live looks, no picker) |
| Empty states | no saved questions: `peek` into an empty box; no friends: `wave`; no quiz history: `sit`; empty revision plan: `think-chin` |
| Errors | 404: `shrug`, "This page drifted off into the maths belt."; offline (exists): sleeping Zorp |
| Answer options | Zorp's eyes follow the focused option or the hint (`lookAt`, backlog from E8) |
| Space week or end of term (optional) | seasonal idle such as `float` |

---

## 6. How it would be built

### 6.1 The stage

- A new guide mode `stage` in `guide.js`, rendered by a new partial and a lazily loaded module `static/js/zorp-stage.js` plus `static/css/stage.css`, fetched only when a stage is about to play.
- Scenes are data in the catalog: `{id, backdrop, props[], zorp: {x, y, size, view, clip, face}, lines[], primary, skipLabel, resolve}`. A scene runs its beats in order and waits for Continue.
- Backdrops in CSS: starfield, planet and belt, logbook page, light burst, confetti rain. Transform and opacity only.
- Props from a new SVG template `#pb-stage-props` (planet, ring of numbers, ship window, logbook, medals in four tiers, map, card stack, calendar strip), cloned like `#pb-zorp-parts`. Crew members are Zorp's rig with cosmetics colours (D2).
- New composite clips (stamp, ninja spin, walk along the tab bar) are registered from `zorp-stage.js` through `pbZorp.register`, so `zorp-poses.js` (52 bytes of headroom) does not grow.
- Accessibility: a dialog with a heading and a description; focus moves to it and back; Esc closes; lines are text (mouth flaps only decorate); reduced motion and off as in section 2.

### 6.2 Coach mode and the cross-page tour

- Coach steps wait for named events from `site.js` and `quiz-runner.js`; a step times out quietly if the event never comes.
- Tour progress `{tour: 'app', step: n}` stored in `guide_json` (existing field); a tour step can name the page it needs and the tour navigates there.

### 6.3 The reward pipeline

- `rewardId` extended for the new kinds (`level:<n>`, `quiz_perfect:<topic>`, `badge:<key>` and so on), each shown once.
- Server: routes that change progress return `rewards[]` (badges, level-up, streak milestones); a session list holds pending moments across a redirect; the results pages of the quiz runner may play them.
- Badge catalogue: `blurb`, `how`, `next`, `family` added to `MILESTONE_CATALOG` and the generated topic badges; the client gets the earned ones in a JSON data island.

### 6.4 Budgets, versions and tests

- New files get their own caps (proposed: `zorp-stage.js` 24 KB, `stage.css` 10 KB, props template 12 KB), loaded on demand, so the normal page budget does not change. Any raise elsewhere gets a dated ledger line.
- `?v=` and `sw.js` cache bumps per phase; the new files go into the precache list only if they must work offline (proposal: no).
- Tests: a stage smoke (catalog shape, every scene ends positive, valence and voice rules, reduced and off paths, one stage per page view, queue order); the voice lint covers every new line; a browser walk (Playwright) of the arrival, the first question and the app tour in light, dark and phone width, with screenshots; badge catalogue smoke (every badge has blurb, how and family); XP honesty test.

---

## 7. Safeguarding, privacy, accessibility

- No new personal data: tour progress and seen-state live in the existing `guide_json`; pending celebrations live in the session. DPIA rows for the new moments.
- No reactions to absence, no streak-loss drama, no comparison, no urging; Zorp says he is a bot in the arrival.
- Every full-screen moment can be closed at once; nothing auto-advances faster than reading speed; motion and sound settings respected; screen readers get the text.
- Teachers: set-work celebrations stay with the pupil; nothing becomes more visible to others.

---

## 8. Phases

| Phase | What | Model | Size |
|---|---|---|---|
| 0 | Decisions (section 9); final script for the arrival and badge lines, approved by David | Opus drafts, David approves | small |
| 1 | Stage engine, props template, backdrops, reduced and off paths, preview at `/guide-preview?stage=` | Opus | large |
| 2 | Arrival film (A1) replacing the welcome hello and origin story; Replay the arrival | Sonnet, Opus review | medium |
| 3 | Coach mode and the guided first question (A2) | Sonnet | medium |
| 4 | Badges: catalogue fields, logbook profile section, detail sheet, immediate delivery, queue, choreography (B2, B3) | Opus engine, Sonnet content | large |
| 5 | New moments: level-up, quiz and Quick Test results, Daily, retry cleared, set work, challenge, revision, personal best; honest XP (B4, B5) | Sonnet | medium |
| 6 | App tour across pages, Explorer badge, just-in-time spotlights, rewritten tab tours (A3 to A5) | Sonnet, Opus review | medium |
| 7 | Zorp around the site: hint peek, waiting states, empty states, errors, lookAt (Part C) | Sonnet | medium |
| 8 | Logbook chapters (A6), if wanted | Sonnet | small to medium |
| 9 | Whole-change review, browser walk with screenshots, accessibility and voice pass | Opus | medium |

Each phase ends with the full test suite, the voice lint, cache bumps and a short section in this file; nothing is committed until David asks.

---

## 9. Decisions for David

1. **Arrival length:** (a) the six-scene film, about 60 to 90 seconds, skippable. **Recommended.** (b) A shorter three-scene version. (c) The six scenes plus logbook chapters later (A6).
2. **The crew on screen:** (a) show the crew in the arrival (and chapters) as recoloured copies of Zorp's rig, story scenes only. This relaxes the frozen "one mascot" rule (E6 2 #1, E7 2 #13). **Recommended.** (b) Keep the crew as words only.
3. **The logbook thread:** (a) badges become stamps in Zorp's logbook, and the profile's Milestones section becomes "Zorp's logbook". **Recommended.** (b) Keep "Milestones" and "badges".
4. **Welcome and story:** (a) merge into one arrival before the level and topic choice. **Recommended.** (b) Keep the welcome screens and upgrade only the story after them.
5. **App tour:** (a) offered after the first question ("Show me around" or "Later") and in Settings. **Recommended.** (b) Starts automatically. (c) Per-tab tours only, as now (rewritten).
6. **Celebration sizes:** (a) the three sizes in B1, full screen only for badges, level-ups, streak milestones, perfect quizzes, topic or subject mastery and the end of the tour. **Recommended.** (b) Full screen for more moments. (c) Fewer.
7. **Sound:** (a) stays opt-in ("Zorp's sounds" off by default). **Recommended.** (b) On by default for full-screen moments only.
8. **Zorp's outfits:** (a) badges unlock looks Zorp wears automatically (hat on a learning badge, explorer look for Explorer), no picker. **Recommended.** (b) A wardrobe picker on the profile (relaxes another frozen rule, more work).
9. **"Top of the class" badge:** comparison wording is banned by the voice rules. (a) Rename it and celebrate it quietly with no ranking words. **Recommended.** (b) Retire it. (c) Keep as is.
10. **Numbers:** (a) show the real effort points in floats and results, add level-ups, and add the Explorer badge for finishing the tour. **Recommended.** (b) Remove XP numbers from floats.
11. **Set work and typed practice:** (a) count them as study days (streaks and badges move). **Recommended.** (b) Leave as now.
12. **Order:** start with phases 1 to 4 (stage, arrival, first question, badges), then decide on the rest. **Recommended.** Or another order.

---

## 10. David's answers (2026-11-08); these override the sections above

1. **Arrival:** the six-scene film (A1).
2. **Crew:** shown in story scenes as recoloured copies of Zorp's rig (relaxes the "one mascot" rule for story scenes only).
3. **Naming:** keep "Milestones" and "badges". The logbook stays a story device in the arrival ("when you reach something new, I mark it"), but the profile section keeps its name and badges stay badges. Scene 3 copy changes accordingly.
4. **Welcome and story:** merged into one arrival before the level and topic choice.
5. **App tour:** starts automatically after the first question, and can be replayed from Settings.
6. **Full-screen moments:** badges, level-ups, streak milestones, perfect quizzes, topic or subject mastery, finishing the tour, and **finishing a full lesson** (every lesson, not only the first).
7. **Sound:** on by default for everything (answer sounds and Zorp's sounds, including full-screen moments), and can be switched off in Settings. Browsers only allow sound after a tap, so the existing cue rules still decide when a sound can play.
8. **Outfits:** add a wardrobe picker (relaxes the "no picker" rule). Badges unlock outfits; the pupil chooses what Zorp wears. New phase 6b.
9. **"Top of the class":** renamed and celebrated. Zorp's lines celebrate the pupil's own accuracy without ranking words; the badge's how-to-earn text states the rule plainly.
10. **Numbers:** real effort points in floats and results; level-ups added; Explorer badge for finishing the tour.
11. **Study days:** left to Claude for engagement. Decision: set work answers and typed practice checks count as study days (they move streaks, effort points and badges), as the plan recommended.
12. **Order:** phases 1 to 4 first, then David decides the rest.

### 10.1 Phase plan after the answers

| Phase | What | Status |
|---|---|---|
| 1 + 2 | Stage engine and the arrival film (merged welcome and story, crew, scene 6 with the real level and topic forms, Replay in Settings); sound on by default | built 2026-11-08 (section 11), awaiting David's review |
| 3 | Coach mode: the guided first question, then the app tour starts automatically (the tour itself is phase 6) | after 1 + 2 |
| 4 | Badges: descriptions, full-screen badge stage with choreography by family, immediate delivery and queue, merged streak moments, renamed accuracy badge, study days for set work and typed practice | after 3 |
| 5 to 9 | New moments, app tour and spotlights, wardrobe picker (6b, built 2026-11-08, section 11.10), Zorp around the site, chapters, review | David decides after phase 4 |

---

## 11. Progress

### 11.1 Phases 1 and 2 built (2026-11-08): the stage and the arrival film

Nothing committed. Built against the answers in section 10; nothing here follows an earlier, overridden draft.

**Files**

| File | What |
|---|---|
| `static/js/zorp-stage.js` (new, 23,350 B, cap 24,000) | The stage engine: builds the full-screen dialog from DOM nodes, clones props from the template and Zorp (plus three crew) from the page's own rig, runs scenes as data, queues stages, registers the composite clips `stage-arrive` and `stage-gaze` through `pbZorp.register` (so `zorp-poses.js` does not grow). |
| `static/js/stage-catalog.js` (new, 5,095 B, cap 8,000) | The copy and choreography of the six arrival scenes (copy separate from runtime; read by the voice lint). |
| `static/css/stage.css` (new, 9,876 B, cap 10,000) | Backdrop (two drifting starfields, Earth's horizon, light burst, falling streak), prop states, the text panel, scene 6 layout, phone layout. Transform and opacity only. |
| `static/images/stage-props.svg` (new, 7,923 B, cap 12,000) | The props template: Novara with the maths belt (glyphs that orbit and stay upright), the ship (hull and a separate rim so the crew sit inside the window), the logbook (shut, then open with notes), the question card with a hint card that slides up. Inert: no script, links or foreign content; fixed colours (night sky in both themes). |
| `static/js/guide.js` (v19 -> v20) | `pbGuide.loadStage()` inserts the four stage files only when a stage is about to play (URLs from a JSON island); `pbGuide.stage(spec, opts)`; `pbGuide.markSeen('origin')`; the origin story now plays as the film; rewards and tours wait while a stage is loading or open (`pb-stage-closed`). |
| `templates/partials/guide.html` | The `#pb-stage-assets` island (four URLs with `?v=1`); no script or link tags. |
| `static/js/welcome.js` (v5 -> v6), `templates/welcome.html` | The arrival controller; the hello step carries the level choice hidden for scene 6; `data-arrival-slot` marks the nodes scene 6 shows; the ready screen says "Good choice. Your first question is ready." The E7 hero animations stay as the fallback. |
| `app.py`, `models/social.py` | `set_guide_origin()` on every accepted welcome step; `replay_arrival`; `apply_new_account_defaults()` on web and API registration. |
| `models/zorp_rig.py`, `models/zorp_voice.py` | `CONTEXT_MAP['stage']` (the plain guide list); `extract_stage_catalog`. |
| `templates/profile_settings.html` | One "Replay the arrival" button; the sound copy says sounds are on for new accounts. |
| `templates/guide_preview.html`, `static/js/guide-preview.js` (v7 -> v8) | A Stage section: the whole arrival, the story alone, each scene alone; `/guide-preview?stage=<scene id>` (or `arrival`, `story`) opens one on load. |
| `scripts/test_zorp_stage_smoke.py` (new) | The stage smoke (section 11.4). |

**The film, scene by scene** (full motion; Continue moves on line by line, nothing advances by itself):

1. *Arrival.* Stars drift; a light streaks down to the horizon and glows; Zorp floats down from the top with dangling legs and lands with the soft-body squash and jelly, waves (mouth flaps on the line), ends on a grin. "Hi, I'm Zorp. I'm a maths and physics bot from a planet called Novara."
2. *Novara.* The ringed planet rises upper left; its belt is fourteen numbers and symbols orbiting the tilted ring (they pass behind and in front of the planet and stay upright). Zorp turns side-on toward it and looks up (eyes up, round mouth, head tipped back). Line 2: he turns back, the belt brightens, think-chin with the bulb.
3. *The mission.* Zorp steps left (a transform-only move); a shut logbook lands beside him and he hops; on line 2 it opens, he points down at it from the side, a tick, a star and a squiggle pop onto the page, a nod. Copy per answer 3: "I keep a logbook of what people here work out. When you reach something new, I cheer." (no stamp promise).
4. *The crew.* The ship slides in upper right, engine glowing, beacon pulsing; three crew (Zorp's rig in mint and sunny, short and long antennae, grin, happy and joy faces) bob in the window and wave in turn; Zorp looks over his shoulder at them (back-glance), turns back and winks.
5. *How I help.* The question card: answer 4, a soft orange cross, Zorp points at it from the side, the hint card slides up ("Take 7 from both sides."). Line 2: the answer becomes 5 with a green tick, a hop and a bow: "I'm a bot, not a person. You can skip me any time."
6. *Your turn.* The sky shrinks to a band; Zorp peeks over the panel (think-chin); the page's real level form moves into the panel. A pick cheers, then the form posts (same `welcome_step`); the topic and ready pages reopen the stage straight at scene 6 (no entrance fade, the six progress dots continue). Start fist-pumps, then posts to Practice.

Skip intro (and Esc) on scenes 1 to 5 jumps to scene 6; Skip for now is in scene 6 and posts the skip step as before; Esc on scene 6 closes the stage and leaves the plain page with the same forms. Reduced motion: each scene is a still frame (props in their final states, all lines at once, the end face) with a 320 ms opacity fade; off: the same frame with no fade. Sound: clips pass `cue: true`, so `pbSound` alone decides (a tap in the last 5 s, full motion, not a quiz); the first scene starts without a tap, so it is silent.

**API for later phases** (badge stage, tour end scene): `pbGuide.loadStage().then(stage => stage.play(scenesOrIdOrIds, opts))`, or `pbGuide.stage(...)`. Resolves `{ ended: 'done' | 'skip' | 'close', scene }` when the stage closes; a second `play` queues behind the first. Scenes are objects (`id, heading, props, layout, face, end, lines, beats, primary, skipLabel, slot, story`) or catalog ids; beats are `prop` (+ `set`), `zorp: 'arrive'`, `play`, `turn`, `face`, `crew`, `burst`, `talk`, `wait`, each optionally `async`. opts: `start`, `skipTo`, `story`, `slot` (nodes shown in a slot scene and put back on close), `resume`, `onScene(i, scene)`. Also `stage.cue(beats)`, `stage.zorp()`, `stage.isOpen()`, `stage.close()`, the `pb-stage-closed` event. New props go into `stage-props.svg` (one `svg[id^=st-]` each) and `PARTS` in `zorp-stage.js`; new composite clips are registered the same way as `stage-arrive`.

### 11.2 Decisions made while building

- **Origin story for existing accounts:** an account that never saw the origin story now gets the film's scenes 1 to 5 on its next ordinary page (the stage, story mode, last button "Let's go", Skip intro and Esc close it), then `origin` is marked seen. One story everywhere, and the homesick line is gone from it as A1 asks. The dialogue-box origin in `guide-catalog.js` stays as the fallback when the stage cannot load (offline, a blocked file), so the E8 lore tests and the old copy keep working.
- **Recording the arrival:** the server records `origin = true` on every accepted welcome step (Let's go, a level, a topic, Skip for now), and the client also marks it when scene 6 opens (in case the pupil leaves there). A refused step writes nothing. `welcome_done` is set as before (topic chosen, or skip). Because `origin` is now stored, `data-guide-persisted` is 1 after the arrival (the welcome smoke's check 16 was updated on purpose).
- **Replay the arrival** sets `welcome_done = false` only and opens `/welcome` from scene 1; it leaves `origin` alone, so abandoning a replay never makes the story pop up elsewhere. `replay_guide_intro` and `replay_welcome` are still accepted (a cached settings page) but no longer shown.
- **Sound default:** new accounts (web and API registration) start with answer sounds on and Zorp's sounds on ("celebrations"). Existing accounts are left as they are: `sound_enabled` (0/1) and `zorp_sound` (off/celebrations) cannot tell "never chose" from "chose off", so nothing is migrated and the column defaults stay off. Settings switches both off as before; the cue rules are unchanged. DPIA row, ROPA row 1, both privacy notices, the settings copy, AI_HANDOFF rule 17 and ZORP_CHARM notes updated.
- **Props as a static SVG file** fetched once and parsed with DOMParser, not a `<template>` in every page, so ordinary pages carry nothing but the 4-URL island. The rig is cloned from the page's own Zorp (the guide overlay rig), so the stage needs no extra markup.
- **Crew:** three copies in mint and sunny (as answer 2 and the brief ask), long and short antennae; no hats or shoes; story scenes only.
- **Faces:** `CONTEXT_MAP['stage']` is the plain guide list (positive or neutral, no slapstick). It is not shipped in the island (pages do not grow); the runtime refuses a negative preset by valence. The look-up in `stage-gaze` is a channel set (eyes up, raised brows, round mouth), not a preset.
- **After Start**, the existing first-visit Practice tour still opens on the first question page (before E10 the dialogue origin opened there). Phase 3's coach mode replaces it.

### 11.3 Budgets, versions, caps

- Own caps (new): `zorp-stage.js` 24,000 B, `stage.css` 10,000 B, `stage-props.svg` 12,000 B, `stage-catalog.js` 8,000 B (all in `scripts/test_zorp_stage_smoke.py`).
- Raised: the CSS tree total 246,000 -> 256,000 B (exactly the new on-demand `stage.css` cap) in `test_u8_a11y_smoke.py`, `test_zorp_charm_smoke.py` and `test_gcse_maths_hints_ladder_smoke.py`, with dated comments; `stage.css` joins the not-core set there, so the core budget (216,000) is unchanged (core 214,142).
- Versions: `guide.js` v20, `welcome.js` v6, `guide-preview.js` v8, stage files v1 (in the island), `sw.js` `pb-v112` (pins updated in the ladder, MCQ, PWA, charm and expression smokes). The stage files are not precached.

### 11.4 Tests

- New `scripts/test_zorp_stage_smoke.py`: caps; no library, CDN or markup strings; CSS and WAAPI move transform and opacity only; the props template is inert and self-contained; catalog shape (every beat names a real clip, view, prop and CSS state); every scene starts and ends positive or neutral; the voice rules on every line and answer 3's wording; lazy loading on guest and signed-in pages; the welcome slot markers; welcome done and origin seen on every path; Replay the arrival; sound on for new accounts; reduced and off paths; the API, queue, dialog, Esc and focus rules; the preview.
- Updated with dated comments: `test_guide_smoke.py` and `test_welcome_smoke.py` (the replay button id; check 16 now expects the stored origin), `test_zorp_sound_smoke.py` (new-account default, non-default-first loops, viewer B switched off before the privacy check, the new DPIA row), `test_zorp_voice_smoke.py` (the new source in `MIN_ITEMS`, `MIN_LINES`, `ZORP_ONLY`), the cache and version pins above, and the CSS totals. No check was weakened: each changed assertion now checks the new behaviour.
- Voice appendix regenerated (`docs/ZORP_CHARM.md` Appendix A).
- `welcome.js` finds the choice buttons through their forms (as the E8 node harness in `test_zorp_poses_smoke.py` expects), so the E7 hero path is unchanged there.
- Full suite (2026-11-08): `All 111 smoke tests passed.`
- Browser walk (Playwright, a new pupil from /register to the first question): 1280 x 860 light and dark, 390 x 844 light and dark, 360 x 740, and 1280 x 860 with reduced motion. No console errors, no horizontal scroll, every stage control at least 44 px. Also checked: Skip intro and Esc go to scene 6, Tab stays inside, Esc on scene 6 restores the page with nothing left inert, the story-only film for an existing account ends on "Let's go" and marks origin, the dialogue fallback when `zorp-stage.js` is blocked, motion off (no running animations). Screenshots: `/mnt/user-data/outputs/e10_arrival/`.

### 11.6 Phase 3 built (2026-11-08): the coach, the guided first question

Nothing committed. Built against section 10; A2's draft lines were kept (they already passed the voice rules) apart from the signed-in note pointer and the closing line, which drops "Want me to show you round the rest?" because the tour is phase 6 (answer 5: it starts by itself from the closing step; for now the coach just ends).

**Files**

| File | What |
|---|---|
| `static/js/zorp-coach.js` (new, 13,474 B, cap 14,000) | The coach: copy (seven steps) and engine in one file, so the voice lint and the runtime read the same lines. Loaded only when due. |
| `static/css/coach.css` (new, 2,213 B, cap 3,000) | The callout: tokens only (light and dark follow the page), in the page flow, no backdrop, nothing fixed, no animation (the script animates). A phone rule rests the corner Zorp while the coach runs. |
| `static/js/guide.js` (v20 -> v21) | `coachDue()`, `startCoach()` (loads the two files through `addAsset`), `coachState`; `maybePlayTour` decides the coach before any tour and opens no tour while it loads or runs; on `pb-coach-ended` it marks `tours.coach` and `tours.practice` seen and flushes. |
| `static/js/site.js` (v39 -> v40, +269 B) | Four events (below). |
| `templates/partials/guide.html` | The `#pb-coach-assets` island (two URLs, `?v=1`). |
| `templates/welcome.html`, `app.py`, `templates/base.html` | The ready form (Start) carries a hidden `coach=1`; `index()` passes `coach_first` only for that POST when a question was made; `<body data-guide-coach="1">`. A picker change, New question, a reload (GET) or any other question is not coached. |
| `models/zorp_rig.py`, `models/zorp_voice.py` | `CONTEXT_MAP['coach']` (the plain guide list); `extract_coach_catalog`. |
| `scripts/test_zorp_coach_smoke.py` (new) | The coach smoke (below). |

**Behaviour** (one callout at a time, in the page flow beside the real element, with a small Zorp, a "Got it" link where the step is not action-driven, and "Skip for now"; Esc also skips; nothing steals focus; the text goes to a polite live region):

1. *Answer box* (typed) or *the options* (multiple choice): "Type your answer and press Check." / "Pick an answer." Waits for `pb-answer-checked`.
2. *Right:* the existing first-correct overlay plays as it does today; the coach waits while any guide dialog or stage is open (and 0.9 s after it closes), then shows the closing step.
3. *Wrong:* the Hint card ("Here's a hint. I only show them after you try."), then the "Show a bigger hint" button when it exists ("Want more? This shows the first step."), then the Show answer bar, now unlocked ("And here's the full answer whenever you want it."). Each moves on when the pupil does the thing (presses the bigger hint, opens Show answer) or presses Got it; a step with nothing to point at is skipped (topics without a hint card go straight on); an unattended step fades out after 20 s. Answering right at any point jumps to the closing step.
4. *Signed in, wrong:* one pointer to the folded "Add a note" toggle when it appears (waits up to 2.5 s for it).
5. *Closing:* "That's the loop: try, hint, try again." (Got it, or it ends itself after 10 s). Then `pb-coach-ended` fires.

**Events added to `site.js`:** `pb-answer-checked` ({correct}; one place, `celebrateResult`, so it covers every typed answer type and multiple choice picks), `pb-answer-unlocked` (when Show answer is first unlocked), `pb-hint-shown` (the hint card is shown, ladder and multiple choice option notes), `pb-hint-bigger`. Multiple choice needs no extra pick event: a pick is a check. The coach ends with `pb-coach-ended` {how: done | skip | leave}; phase 6 can start the app tour from it.

**Motion:** full: fade and a 6 px rise, Zorp's clip (wave, nod, side-point) and expression; reduced: a fade, no limbs, expression only; off: static. Faces: happy on the first tip, soft-smile on the wrong-answer tips, grin on the close (all from `CONTEXT_MAP['coach']`).

**Practice tour:** it cannot open on the coached page (`coachState`), and `tours.practice` is marked seen whenever the coach ends in any way, including leaving the page (pagehide), so a pupil is not toured twice. If the page turns out to have no question to coach, the coach reports that and the normal tour runs as before.

**Budgets and versions:** `site.js` cap +300 (ledger line "2026-11-08: E10 phase 3 coach events, +269", in the ladder and MCQ smokes); `coach.css` joins the not-core sheets in `test_u8_a11y_smoke.py`, `test_zorp_charm_smoke.py` and the ladder smoke (the core budget is unchanged); the CSS tree total stays under 256,000 (no raise). `guide.js` v21, `site.js` v40, `sw.js` `pb-v113` (pins updated in the ladder, MCQ, PWA, charm and expression smokes). The coach files are not precached.

**Tests:** `scripts/test_zorp_coach_smoke.py`: caps and rules (no library, CDN, innerHTML, inline handler; no animation or fixed position in the CSS; script animates opacity and transform only; clips only at full motion), catalog shape (faces and clips), the voice lint on every line and label, the four events in `site.js` and in the coach, lazy loading (no page carries the files, island on guide pages, not precached), which page is coached (the Start POST only), the Practice tour held back and both flags marked seen on every exit, and the seen-state going through the ordinary guide state. The voice smoke counts the new file (`MIN_ITEMS`, `MIN_LINES`, `ZORP_ONLY`); the stage smoke's island count is now six `?v=`; the voice appendix was regenerated.

**Browser walk** (Playwright, new pupil from /register through the arrival to the first question): 1280 x 860 light, dark and reduced motion; 390 x 844 light and dark; 360 x 740. Path A (right), path B (wrong, hint, bigger hint, Show answer, note, close, Esc), path C (a multiple choice topic; a topic with no hint card), typed and multiple choice. No console errors, no horizontal scroll, the callout never overlaps its target, tips scroll into the gap between the header and the fixed bars. Screenshots: `/mnt/user-data/outputs/e10_coach/`.

**Rough:** the "Add a note" outline is clipped a little by its panel; the coach is not shown to a pupil who reloads the first question after it ended (by design); non-ladder topics get "try, hint, try again" although they have no hint card (the plan's line, kept); the scroll is by hand (`scrollBy`) because `scrollIntoView` stops at the question card's own scroll boxes.

### 11.7 Phase 4 built (2026-11-08): badges and the badge stage

Built, nothing committed, awaiting David's review.

**What it does.** Every badge now has a family, a one-line blurb (80 characters at most), a "how to earn it" line and a "next up" pointer (`models/gamification.py` `MILESTONE_CATALOG`, `models/topic_status.py` for the 285 generated topic and subject badges). A new badge plays on the stage (`static/js/badge-stage.js`, `static/css/badge-stage.css`, `static/images/badge-props.svg`, lazy, loaded only when a badge or streak moment plays): Zorp on the left, the medal dropping in on the right, one prop and one choreography per family (flame, sunrise, fan of cards, map pins, book with a graduation hat, swish, stars, page of medals, target). Two or more badges at once play as one scene; the streak 7 and 30 moments merge into the badge scene; streak 100 gets its own big scene. Reduced motion shows the still scene, off shows the panel only. The profile has a badge shelf of buttons that open a native `<dialog>` sheet (`static/js/badge-sheet.js`) with the blurb and date, or the how-to for a locked badge, and a "Next up" button.

**Delivery.** `after_request` adds `new_milestones` and the header `X-PB-Milestones` to any successful JSON object response that earned a badge; `celebrate.js` plays them for any fetch. Badges earned on a redirect or error wait in `session['pb_ms']` (at most 8 keys, no personal data) and the next page emits them once through the `#pb-new-milestones` island. Question pages stay quiet: badges earned during a quiz wait for the results page (`quiz_results_mode`).

**Study-day rule (owner answer 11).** A typed check (`/api/v1/problems/check`, recorded attempts only) and a set-work answer now count as a study day, so streaks and day badges move. Set work also writes one private activity event (`set_work_answered`, effort weight 1, never in a feed); a typed check writes no effort event, so it earns no second point.

**Decisions.** `accuracy_top_friend` is renamed "Sharp week" (emoji 🎯) because it compares friends and the old title read as a ranking. `recent_milestone` was removed from the buddy (the stage replaces the corner prompt). Fixed a latent bug: `get_weekly_recap` used a hard-coded four-placeholder query and raised on the new event type.

**Budgets and versions.** Caps (`scripts/test_badge_stage_smoke.py`): badge-stage.js 18,000, badge-stage.css 5,500, badge-props.svg 8,000, badge-sheet.js 2,500. The CSS tree total rises 256,000 -> 261,500 for the on-demand sheet (core unchanged apart from about 350 B in `chrome.css`, see the ledger line "2026-11-08: E10 phase 4"). Pins: `guide.js` v22, `celebrate.js` v12, `chrome.css` v47, `coach.css` v2, `guide-preview.js` v9, `sw.js` `pb-v114`. New files are not precached. Preview: `/guide-preview?badge=<family>`.

**Coach phone fix.** The rule hiding the corner buddy while the coach runs worked, but coach.css loaded about 240 ms late, so the buddy flashed. The rule now lives in `chrome.css` and `guide.js` adds `pb-coach-on` to the body at once.

**Tests.** New `scripts/test_badge_stage_smoke.py`; the voice lint reads the new copy (`extract_badge_copy`, Appendix A regenerated).

### 11.8 Phase 5 built (2026-11-08): new moments, toasts, honest XP

Built, nothing committed, awaiting David's review. Against section 10 answers 6 and 10 and B1, B4, B5.

**Sizes**

| Moment | Size | Where it comes from |
|---|---|---|
| Level-up | stage: the level ring fills, flashes and rolls over to the new number; Zorp flex then fist-pump; "Level 4. Your effort points keep adding up." Second button "See my profile" | `record_activity_event` wrapper in `app.py` |
| Perfect lesson quiz (every answer right, 3 or more questions) | stage: score seal and stars; Zorp victory then dance | `_note_quiz_finished` (lesson quiz submit and API) |
| Finished lesson (every lesson) | stage: the first time a full scene (open book closes, tick, burst, confetti, cheer), after that a smaller scene (book closes, tick, one cheer, no confetti); second button "Try the quiz" | `lesson-progress.js` |
| Lesson quiz finished (not perfect) | toast: "7 out of 10. Retry the 3 you missed?" and a "Retry wrong ones" link that focuses the real button (`#retry-wrong`) | `_note_quiz_finished` |
| Personal best on a topic | toast: "Your best so far on this topic: 8 out of 10." (against the pupil's own earlier quizzes only) | `personal_best_quiz` |
| Quick Test finished | toast with the marks and the Retry link | `_finalize_quicktest_session` |
| Retry wrong cleared | toast "All fixed." | a retry run with every answer right |
| Daily, seven days in a calendar week (Monday to Sunday, UTC) | toast, once a week | `_note_daily_answered` |
| Set work: last question answered | toast; every answer also floats the real "+1 XP" | `_record_set_work_answer` |
| Challenge answers submitted | toast "Your answers are in. 6 out of 8." (no win or lose words) | `challenge_detail`, `api_v1_challenge_submit` |
| Weekly streak skip used | toast "Your weekly skip kept your streak going." | `_record_study_activity` (freeze count before and after) |
| Right answer after a hint | micro: "Got there with a hint." and a small sparkle under the feedback | `pb-hint-shown` then `pb-answer-checked` (events from phase 3) |
| Daily answered | micro: Zorp's small cheer when right, nothing when wrong | `_note_daily_answered` |

**Level-up detection.** Every place that records effort points goes through `record_activity_event` in `app.py`, which is now a thin wrapper over the model function: for an event type with a weight (`EFFORT_WEIGHTS`) it reads the pupil's lifetime points first, writes the event, and asks `level_up_between(before, before + weight)`. A new level becomes the moment `{type: level, id: level:<n>, level, pct}` (the highest level when two are crossed). Nothing is compared against a stored level, so existing accounts are never retro-celebrated.

**Delivery** is the badge pipeline plus a second list: `_note_moment` collects small dicts (a whitelist of keys, no personal data); a JSON object response gets `new_moments` and the `X-PB-Milestones` header (`celebrate.js` reads them for any fetch); a rendered page carries `#pb-new-moments`; a redirect keeps them in `session['pb_mm']` (at most 8) for the next page, once. They are held back on quiz question pages and emitted on results pages. `celebrate.js` hands them to `pbGuide.moments`, which waits for the badge stage and any open dialog or stage, then loads `moments.js` and `moments.css` (island `#pb-moment-assets`). Toasts wait until a stage has closed, so a toast is never behind a stage.

**Queue order, decided.** One stage at a time, in this order: the badge stage first (it always plays before moments run), then perfect, lesson, level (one batch, "1 of 3", Esc leaves the batch), then toasts, then micro. A perfect quiz that earns a topic ninja or topic master badge in the same request is **not** sent at all (no perfect stage, no toast): the badge stage already says it. An unrelated badge plays first and the perfect stage follows. A retry run with every answer right is "All fixed.", never a perfect quiz.

**Seen-state.** Level: `level:<n>` in the guide state (`pbGuide.markReward`). Lesson: `lesson:<level>:<subject>:<topic>` (cut to 64 characters), and the old single `lesson_complete` flag decides the full or the smaller scene. A lesson celebrates only when its last quick check is answered on the page (live), not when a finished lesson loads, so older lessons and other devices are not celebrated. Perfect: once per attempt because the server notes it at submit time and the list is emitted once; the client also remembers the attempt id in `sessionStorage`. Toasts and micro: server once, and `sessionStorage` per id.

**Honest XP** (answer 10, B5). The "+10 XP" float is gone: a correct check records no effort points, so it shows the pop, tick and sparkle with no number (`celebrate.correct(target, points)` floats a number only when given a positive one). The "+25" on lesson complete is gone (finishing a lesson records nothing of its own). The quiz results "+score x 5 XP" line (shown only on perfect scores) is now the quiz's real recorded points (`EFFORT_WEIGHTS['quiz_completed']`, 3), shown once, right after the pupil submits (`session['pb_qxp']`), never on a later visit. A set-work answer floats its real "+1 XP". The profile figures were already computed from the events. The styleguide text was corrected.

**Files.** New: `static/js/moments.js` (23,649 B, cap 24,000; copy, faces and choreography are data blocks the voice lint reads), `static/css/moments.css` (4,231 B, cap 5,000; not core CSS), `scripts/test_celebration_moments_smoke.py`. Changed: `app.py`, `models/gamification.py` (`effort_weight`, `level_up_between`, `personal_best_quiz`), `models/zorp_rig.py` (`CONTEXT_MAP['stage.moment']`), `models/zorp_voice.py` (`extract_moment_copy`), `guide.js` v23, `celebrate.js` v13, `lesson-progress.js` v26, `partials/guide.html` (the `#pb-moment-assets` island), `base.html` (`#pb-new-moments`), the two results templates (`id="retry-wrong"`, the XP line). `sw.js` `pb-v115` (pins updated in the ladder, MCQ, PWA, charm and expression smokes). The props are the badge stage's `badge-props.svg`. No cap was raised: the CSS tree is 260,077 of 261,500, `site.js` is unchanged.

**Tests.** `test_celebration_moments_smoke.py`: caps and rules; copy, faces and clips; level-up detection (a threshold crossed once, twice in one step, none below) and once-only delivery in JSON, the page island and the session; a real lesson quiz through its results page (perfect moment, the XP line equal to the recorded points, gone on reload; an imperfect run with the toast; retry cleared); personal best, Quick Test, Daily week, set work (the float equals the points recorded), streak skip; the queue rule for a perfect quiz with a ninja badge; honest XP; lazy loading. Voice lint and Appendix A regenerated.

**Browser walk** (Playwright, a new pupil, real flows): level-up (1280 x 860 light and dark, 390 x 844 light and dark, reduced motion), a perfect lesson quiz through the quiz runner to its results page (badge stage first, then "Full marks"), a finished lesson (full scene, then a second lesson with the smaller scene), the quiz toast with the Retry link (focus lands on the real button), three stacked toasts with the "+1 XP" float, the hint micro. No console errors. Screenshots: `/mnt/user-data/outputs/e10_moments/`.

**Rough.**
- The guide seen-state blob is capped at 4,096 bytes and 40 flags per update (`models/social.py`). Badges (phase 4), levels and lessons all use it; a very active pupil will fill it and an over-large merge is refused, which would also stop tour flags saving. A separate small table for seen moments would fix it; not done.
- `/api/lesson-progress` records a lesson-step event on every save, including the save a lesson page makes on load, so opening a part-finished lesson adds points (and can cross a level). That is real and shown honestly, but it is farmable; a fix would record only when a new step completes.
- Retry runs are saved as quiz attempts with their own small totals, so a retry of 3 questions can make a later full quiz look "not a best". Conservative, not wrong.
- After a level-up the ring restarts almost empty (the points that crossed the line are 1 to 3 of 250 or more), so the rolled-over ring shows a sliver.
- Guests get no moments (they have no session list or Zorp overlay).
- The `moments.js` cap has 351 B of headroom.

### 11.9 Phase 6 built (2026-11-08): the app tour, spotlights, and three phase 5 fixes

Built, nothing committed, awaiting David's review. Against A3, A4, A5, 6.2 and section 10.

**Part 1: the three phase 5 faults, fixed first**

- Guide seen-state overflow. The guide state (`guide_json`, still 4,096 B and 40 flags per update from the client) is now kept in seen-state regions, each with its own byte budget, so one kind of flag can never crowd out another. `tours` (the tours, the coach, the app tour and the spotlights, stored as `sp_<id>`, 1,400 B) and durable `rewards` (`streak:*`, `first_correct`, `lesson_complete`, 800 B) are never evicted. `recent` is a ring (1,400 B, 80 flags) for the volatile `level:`, `lesson:` and `milestone:` flags; when it is full the oldest go. Forgetting one is safe because the server emits each badge and level once. `run` holds the tour in progress (`{id, step}`). Old accounts migrate on their next write. The incoming patch limit is 16,384 B. Test: `scripts/test_guide_state_budget_smoke.py` (hundreds of lessons, levels and badges, and the tour and coach flags still there).
- Lesson-step farming. `/api/lesson-progress` records a lesson-step effort event only for steps that are newly completed (capped by the lesson's step total); the save on page load, and a repeat, record none. The study day is still recorded. Test: `scripts/test_lesson_points_retry_stats_smoke.py`.
- Retry runs. A retry-wrong run is still saved, now with `quiz_attempts.is_retry = 1`. Personal best, the accuracy trend, the weekly best, friends' accuracy, topic status, weak topics and the class average count full quizzes only. The history list, activity counts and the quiz summary still show every run. Same test file. This also closes the hole where a retry of ten wrong answers could score a perfect ten.

**The tour.** `static/js/zorp-tour.js` and `static/css/tour.css` load only when a tour or a spotlight is due (island `#pb-tour-assets`, with `inClass`). Stops, in order (steps in brackets): Practice picker (2), hints and Show answer (1), save a question (1), Quick Test (1); Learn topic list (1), lesson quiz (1); Daily today (1), week (1); Compete friends (1), challenges (1); Profile streak (1), progress with badges and the revision plan (1), history (1); Classes (1, only for a pupil in a class); Settings motion (1), replay (1). That is 16 stops (15 without a class) and 19 steps. Each step outlines a real element and a small fixed card holds Zorp, a line, Next and "Skip tour". A step whose element is missing is skipped. Between pages Zorp turns side-on and hops along the tab bar or top nav, then the page changes (reduced motion fades; motion off does neither). The step is in `guide_json` `run`, so a reload loses nothing; a page reached by hand restarts at that page's first step. Esc and "Skip tour" always work; the card announces politely; it waits for a stage, a dialog or a toast. The Study Buddy hides while it runs. The end is a stage scene (Zorp bows) and then `POST /api/v1/me/tour/complete`, which awards the badge.

**Auto-start and replay.** `pb-coach-ended` with a way other than "leave" starts the tour (`guide.js beginAppTour`). Settings has "Replay the tour" next to "Replay the arrival" (`replay_tour` sets `tours.app` false and `run` to the first step, then goes to Practice).

**The badge.** Owner answer: an "Explorer" badge. `topics_10` is already "Broad explorer" in the `explorer` family, so this one is **Pathfinder**, key `app_tour`, family `tour`, bronze, a signpost prop (`bp-sign` in `badge-props.svg`, `FAMILIES.tour` in `badge-stage.js`: Zorp beams, the boards swing in, a bow). Server-awarded once, and only after the tour was started, finished or skipped. Replaying never awards it twice.

**How the tour and the per-tab tours coexist; existing accounts.** The per-tab tours (rewritten in `guide-catalog.js` to say what you can do on each page) remain as the fallback for an account that has never had the app tour. A new account gets the app tour after the coach and skips them all. An existing account (origin seen, no `app` flag) gets one offer on Practice instead of that page's own first-visit tour: "Show me around" starts the tour, "Not now" counts as skipped. Once the app tour is taken (finished, skipped or declined) the per-tab tours stay quiet, and `endAppTour` marks them seen. They are never shown on top of the tour.

**Spotlights (A4).** Nine, each one or two lines the first time a pupil meets the thing: first hint card (not in the coached question), first bigger hint, first lesson quiz, first Quick Test, first AI explain, first set work, first challenge, first revision plan item, first saved question. One per page view, never during a stage, the coach, a dialog or the tour. Seen-state is `sp_<id>` in the protected `tours` region.

**Files.** New: `static/js/zorp-tour.js` (cap 34,000), `static/css/tour.css` (cap 2,800), `scripts/test_zorp_tour_smoke.py`, `scripts/test_guide_state_budget_smoke.py`, `scripts/test_lesson_points_retry_stats_smoke.py`. Changed: `models/social.py`, `models/gamification.py`, `models/user_data.py`, `models/topic_status.py`, `models/weak_topics.py`, `models/class_progress.py`, `models/zorp_rig.py` (`CONTEXT_MAP['tour']`), `models/zorp_voice.py`, `app.py`, `guide.js` (v24), `guide-catalog.js` (v13), `badge-stage.js`, `badge-stage.css`, `badge-props.svg`, `guide.html`, `profile_settings.html`, `sw.js` (`pb-v116`).

**Caps.** The CSS tree cap was **raised 261,500 to 262,500** (tree 262,304 with `tour.css`), with a dated entry in `test_u8_a11y_smoke.py`, `test_zorp_charm_smoke.py` and `test_gcse_maths_hints_ladder_smoke.py`; `tour.css` is on demand, so the core cap stays 216,000. No other cap was raised (`badge-stage.js` 17,402 of 18,000, `badge-props.svg` 6,889 of 8,000).

**Browser walk.** A new pupil registers, skips the arrival to the choices, picks GCSE Maths, gets the coach question, skips the coach, and the tour runs to the Pathfinder badge: 1280 x 860 light, 390 x 844 dark, 360 x 740 light, and 1280 x 860 with reduced motion (no overlaps, no horizontal scroll, no console errors). Spotlights: first lesson quiz and first hint at 1280 light and 390 dark; the second visit is quiet. Screenshots: `/mnt/user-data/outputs/e10_tour/`.

**Rough.**
- The badge request is sent after the end stage closes, so the Pathfinder stage follows it; closing the page in between loses the badge (replay and finish again earns it).
- A pupil who joins a class mid-tour gets the Classes stop only on the next page load.
- The hop is a quick arc along the bar, not a walk cycle; the end-of-tour stage is checked only in the browser walk below, and the spotlights were walked for two cases (lesson quiz, hint) at 1280 and 390.
- A target taller than 45% of the screen is passed over for a smaller one later in its selector list (Practice picker, revision plan, Daily board); a page that settles after the card is placed gets the card moved clear (up to 8 times).

### 11.10 Phase 6b built (2026-11-08): Zorp's wardrobe

Built, nothing committed, awaiting David's review. Against section 10 answer 8 (badges unlock outfits; the pupil chooses). This relaxes E7 section 2 #13 ("cosmetics automatic only, no pupil-facing picker"); `docs/ZORP_EXPRESSIVENESS.md` and `docs/MASCOT_MOTION_AND_ONBOARDING.md` now say so.

**Items.** Only art the live rig already draws (`models/zorp_kit.py` `LOOK_FIELDS`); no new art, and the kit-only toque and quiff stay out. Six slots, 17 items: each slot has one always-available default (Zorp blue, Standard antennae, Standard feet, Usual smile, No hat, No shoes) and 11 unlockable items, one per badge family (a test fails if a family unlocks nothing, or if one badge opens two items, so the badge stage line is never ambiguous).

| Item | Slot | Unlocked by | Badge family |
|---|---|---|---|
| Mortarboard | hat | Lesson learner (`first_lesson_step`) | learning |
| Beanie | hat | Pathfinder (`app_tour`) | tour |
| Sneakers | shoes | Week warrior (`streak_7`) | streak |
| Sunny | colour | Daily starter (`qotd_first`) | daily |
| Mint | colour | 5 topic masters (`topics_master_5`) | topic_master |
| Violet | colour | Sharp week (`accuracy_top_friend`) | accuracy |
| Long antennae | antenna | Broad explorer (`topics_10`) | explorer |
| Short antennae | antenna | any subject badge (family rule) | subject |
| Big feet | feet | 5 lessons complete (`topics_completed_5`) | topic_completed |
| Wide grin | smile | Practice regular (`questions_25`) | practice |
| Cat smile | smile | 5 topic ninjas (`topics_ninja_5`) | topic_ninja |

First quiz (learning) and the later badges of a family open nothing more; with only 11 live-approved items one badge per family is what the art allows. The table is `models/zorp_wardrobe.py` (`_RAW`), the single source.

**The picker.** A "Zorp's wardrobe" panel on the profile Progress tab, directly under Milestones (`templates/partials/wardrobe.html`, included by `profile.html`; `#wardrobe` opens the Progress tab through `u4.js`). A live preview Zorp, one fieldset per slot with native radio buttons (arrow keys, Tab and Space work with no script), swatches 44 px or more, a text name on every swatch. A locked item is a disabled radio with its reason as visible text, "Earn <badge title> to unlock", a link to the badge sheet when it is a specific badge. Save outfit and Reset to default. A change plays a hop on the preview at full motion. Reset gives the choice back to Zorp's automatic look (the page reloads to draw it). `?try=<item id>` puts an unlocked item on in the preview without saving (the server ignores a locked or junk id).

**Storage and validation.** New column `user_profile_settings.zorp_outfit_json` (`TEXT NOT NULL DEFAULT ''`, added with the usual `ALTER TABLE` loop in `init_db`). `''` means never chose; otherwise `{"v":1,"hat":"beanie",...}` with only the non-default slots (an empty one is a deliberate plain Zorp). Written through `PATCH /api/v1/me/settings` with a new `zorp_outfit` key (object, or `null` to reset): unknown slot or value gives `400 invalid_outfit`, an item the pupil has not earned gives `400 locked_item`, and the whole PATCH is refused. The save touches only its own column. On every read the stored outfit is filtered against the pupil's badges again, so storage is not trusted either. The GET settings answer carries `zorp_outfit` (owner only).

**Where it applies.** `buddy_look` (the context processor) is now the stored outfit when the pupil chose, else today's automatic look. That one value draws the corner buddy, the guide overlay rig (which the coach, the tour and every stage copy) and the arrival hero, so the badge stage, moments, tour and coach all show the outfit with no change to them. The arrival crew keeps its own colours (it strips hat and shoes and sets its own colour). After Save the wardrobe also dresses the corner and guide rigs on the same page.

**Badge stage tie-in.** `_badge_payload` adds `wardrobe` {id, name, noun} when a badge newly opens an item (not for a second badge of a family that already opened it). `badge-stage.js` adds a line, "New in your wardrobe: the beanie." (33 characters, a reward line), and a "Try it on" button that goes to the profile with `?try=<id>#wardrobe`: the item is on the preview and the pupil presses Save.

**Privacy.** DPIA row, ROPA row 1, both privacy notices, `SECURITY_AND_GDPR.md` and `API.md` name it. It is owner only: the public profile, friends views, leaderboards, the avatar and every other pupil's pages never carry it (`test_not_visible_to_others`). The export is `SELECT *` on the settings row and erase deletes the row, so both include it (tested).

**Files.** New: `models/zorp_wardrobe.py`, `templates/partials/wardrobe.html`, `static/js/wardrobe.js` (6,500 B cap), `static/css/wardrobe.css` (2,800 B cap), `scripts/test_wardrobe_smoke.py`. Changed: `app.py`, `models/social.py`, `models/zorp_voice.py` (extractor for the new copy), `static/js/badge-stage.js`, `static/js/u4.js`, templates `profile.html`, `partials/guide.html`, `base.html`, both privacy notices, and the tests and docs named above. Versions: `badge-stage.js` `?v=2` to `?v=3`, `u4.js` `?v=12` to `?v=13`, `sw.js` `pb-v116` to `pb-v117` with its pins in the six smokes that hold it. The two new files load on the profile page only and are not precached.

**Caps.** Two raised, each with a dated ledger comment: the CSS tree **262,500 to 265,300** (+2,800 for the on-demand `wardrobe.css`; tree 265,025; `wardrobe.css` added to the on-demand lists, so the core cap stays 216,000) in `test_u8_a11y_smoke.py`, `test_zorp_charm_smoke.py` and `test_gcse_maths_hints_ladder_smoke.py`; and `badge-stage.js` **18,000 to 18,500** (18,373 B) in `test_badge_stage_smoke.py`. Untouched: the default rig instance, the page mascot, the parts library and the rig island (the wardrobe adds no art and does not touch `buddy.html` or `zorp_library.html`).

**Browser walk.** A new pupil sees only the defaults (17 radios, 6 enabled); a real lesson step earns Lesson learner; the badge stage shows the wardrobe line and Try it on; the profile opens with the mortarboard on the preview; Save dresses the corner buddy, a reload keeps it, and a stage (the streak stage) shows the saved colour, antennae, beanie and sneakers. Reset brings back the automatic look. 1280 x 860 light, 390 x 844 dark, 360 x 740 light, and 1280 x 860 with reduced motion: no horizontal scroll, no console errors. Screenshots: `/mnt/user-data/outputs/e10_wardrobe/`.

**Rough.**
- A pupil who never chose sees Zorp's automatic look in the corner but a plain Zorp in the wardrobe preview, with the note "Until you save, I choose my own look."
- The two files are loaded by the profile page whenever it opens (the panel is on the hidden Progress tab), not only when the tab is opened.
- With 11 live-approved items each family gives one item; more would need new art within the rig budgets.
- Save and Reset need script; there is no form fallback.
- All six slots (with every badge pre-earned) were walked at 1280 light and 360 light; 390 dark and reduced motion walked the earn, Try it on, Save path with the hat.

### 11.11 Phase 7 built (2026-11-08): Zorp around the site

Built, nothing committed, awaiting David's review. Part C, adapted.

**Built.** Files: `static/js/zorp-around.js` (cap 8,600 B), `static/css/around.css` (cap 4,000 B), `templates/partials/around.html`, `scripts/test_zorp_around_smoke.py`.
- **Waiting:** AI explain (lesson pages and the quiz review) shows a small `think-chin` Zorp with the bulb after 400 ms and a nod when the answer lands; `aria-busy` and the real "Thinking..." text stay. The Zorp is cloned from the page's own rig at run time, so no mascot bytes.
- **Results:** the ring counts up once on lesson quiz results, the saved attempt view and Quick Test results (the Quick Test had no ring; a hero with ring was added). Face by band: 80+ joy, 50 to 79 determined, below 50 soft-smile with "Every go teaches something. Try the tricky ones again when you like."
- **Show answer sparkle:** CSS only, no `site.js` change. **Daily:** there was no week strip on the Daily page, so a "Your Daily week" strip of the viewer's own answers was added; today's dot pops once on the page after answering. **Profile:** level ring fills once per session; "New" ribbon for badges earned in the last 7 days.
- **Empty states:** saved questions peek (out of a drawn box), follows and friends boards and Daily board wave (with "Search for a handle, open their profile and press Follow."), quiz history sit, revision plan think-chin. **Errors:** 404 and 500 with the shrug; offline untouched.
- **lookAt:** corner Zorp's pupils, practice page, full motion only, on focus changes (see ZORP_EXPRESSIVENESS 8; text inputs are followed on focus, not while typing).

**Skipped or adapted.** New-question generation has no visible wait (a page load), so nothing was added. The "peek at the first hint" and "newest hat" lines were not built (phase 6 spotlight and the wardrobe cover them). Seasonal idle skipped. The 405 handler still returns plain text.

**Fixed:** the results ring never showed its fill (`--correct-400` is not a token); now `--correct-300`, `pages.css` v59.

**Caps and versions.** CSS tree 265,300 to 268,900 (ledger comments in the three tests); `around.css` added to the on-demand lists. `lesson-assist.js` v18, `quiz-assist.js` v2, `pages.css` v59, `sw.js` `pb-v118` with its pins.

**Rough.** The ring and level-ring animate `--quiz-pct` and `stroke-dashoffset` (paint, not transform; same as the streak ring). With script blocked a scripting-enabled browser shows an empty ring until the script runs. Revision-plan empty state was checked in the template and by test, not walked.

### 11.12 Review fixes (2026-11-08)

Eight defects found by an independent review of phases 1 to 7, fixed; nothing committed. Each line: what changed, and the test.

1. **Privacy.** The pending badge and moment lists and the XP line (`pb_ms`, `pb_mm`, `pb_qxp`) now sit beside an owner mark (`pb_own`, the pupil's id). They are cleared on every login and logout (a Flask-Login signal covers web login, register, logout and account deletion) and in the three API auth routes, and are dropped when read or written under a different pupil or with no owner mark. Test: `test_review_pending_lists_belong_to_the_pupil` in `scripts/test_celebration_moments_smoke.py`.
2. **Two dialogs at once.** `guide.js` keeps a "moments in flight" counter that `stageBusy()` counts from the moment a batch is taken until `pbMoments.play` settles (success or failure; whatever waited then resumes), and its Esc handler returns early while a stage is open. Test: `test_review_guide_js_stage_and_tour_offer` (wiring), plus a Playwright walk (badge stage, level-up stage, tour offer; sampled every 25 ms: no moment with both open; Esc on the level-up stage left the tour offer undeclined, a second Esc declined it).
3. **Badges lost on question pages.** `celebrate.js`'s shared fetch wrapper sends `X-PB-Quiz: 1` for same-origin calls made from a quiz question page; the server then keeps new badges and moments in the session list for the results page instead of the JSON answer. Test: `test_review_quiz_question_fetches_keep_badges_for_results` (a streak 7 badge on a Quick Test's first answer plays on the Quick Test results page, once). Playwright confirmed the header on the real calls and the "7-day streak" stage on the results page.
4. **Mixed lesson quizzes.** `lesson_mcq_next` finishes as `/submit` does (`_note_quiz_finished`, `pb_qxp`). Test: `test_review_mixed_lesson_quiz_next_path_finishes_like_submit` (a perfect run and a two-wrong run of the Measurement quiz through `/next`).
5. **Lesson-step points.** Points follow a new ledger table `lesson_step_awards` (kept when the bookmark is cleared; seeded once from existing progress), counted against the server's `lesson_step_total` (the client's `step_total` is ignored for points and no longer stored when the server knows the count); only `step-N` keys below that total are real. In the data export and the post-deletion checks; DPIA, ROPA and `SECURITY_AND_GDPR.md` updated. Tests: `test_lesson_points_only_for_new_steps` now sends `step_total=80` and invented keys; new `test_lesson_points_not_farmable_by_clearing_and_redoing` (`scripts/test_lesson_points_retry_stats_smoke.py`).
6. **Challenge toast.** The results mode is decided per request (`_quiz_results_now`): `challenge_detail` counts as a results page once the viewer has submitted, so the toast plays there; the JSON submit route called from a question page keeps its toast the same way as fix 3. Test: `test_review_challenge_page_is_a_results_page_once_submitted`.
7. **Background renders.** Only a navigation reads the pending lists: `_pending_may_emit` refuses `/offline`, the static endpoint, any error page (404, 500) and requests with `Service-Worker`, a `Sec-Fetch-Dest` other than `document` or a `Sec-Fetch-Mode` other than `navigate`. A client that sends none of those headers (older browsers, the Flask test client) counts as a navigation. Test: `test_review_background_renders_leave_pending_lists_alone`.
8. **Pathfinder without the tour.** New `POST /api/v1/me/tour/reached-end`: the client saves the guide state, then calls it when the last tour step is on screen; the server records a server-only marker (`tour_finished` in `guide_json`, not writable through the guide PATCH) only if the stored run is the app tour on its last page (step 16 or later). `/api/v1/me/tour/complete` requires the marker, so "Not now" earns nothing; a replay clears it. The client waits for the call before clearing the run. Test: `test_the_badge` in `scripts/test_zorp_tour_smoke.py`.

**Versions and caps.** `guide.js` v25, `celebrate.js` v14, `zorp-tour.js` v2 (the island), `sw.js` `pb-v119` (pins updated in the ladder, MCQ, PWA, charm and expression smokes). `zorp-tour.js` is 33,967 of 34,000 bytes.

**Limits.** The tour's end is recorded from the client's own saved run, so a pupil who forges `run` through the settings API and then calls both endpoints can still claim Pathfinder (it is a cosmetic badge; the marker closes "Not now", the case the review found).

### 11.13 Phase 8 built (2026-11-08): story chapters (A6)

Built, nothing committed, awaiting David's review.

| # | Title | Unlocks at | What happens |
|---|---|---|---|
| 0 | Arrival | always | Replays the arrival story scenes only (no level or topic choices). |
| 1 | The maths belt | 3 badges | Zorp flies the belt; a rock covered in a puzzle (6 x 7) is solved and tumbles away; "someone is on a roll". |
| 2 | Meet the crew | 5 badges | Pim (cook), Juno (pilot, terrible at parking: the ship bumps a moon) and Tock (engineer) wave from the ship. |
| 3 | Puzzle doors | 8 badges or a topic master badge | A Novara door opens when 8 + 5 is solved; even the toaster has a puzzle; Zorp's own front door wanted a square root. |
| 4 | Home | 10 badges | The one wistful beat: Zorp looks up at Novara (about his own feelings only), then remembers how much there is to learn on Earth and cheers up. |
| 5 | The logbook | 15 badges | The logbook fills with general things people on Earth worked out (the Earth measured with a stick and a shadow, the feather and the hammer on the Moon). |
| 6 | A postcard from Novara | 20 badges or a subject complete badge | A postcard from the crew; ends with "More stories may come one day". |

**Unlock and delivery.** `models/story.py` derives the unlocks from `user_milestones` (nothing stored). `_note_new_milestones` compares the earned badges with and without the new ones and adds one toast moment `story_offer` for the lowest chapter that just opened (never two at once). It rides the moments pipeline, so it appears after the badge stage; `guide.js` `runMoments` shows it last through `loadStory()`. The toast (a mini Zorp, "Zorp has a new story for you", the chapter title, Watch, Later, a dismiss button, 20 s, paused on hover or focus, Esc) never takes focus and never plays anything; only Watch does. Existing pupils: `_story_catchup` adds one offer for the first unlocked chapter on an ordinary page, only after the arrival and the app tour are done, never during a tour, never on /welcome or Settings, and never once any chapter was offered or watched, so Later is final until a new badge opens a new chapter.

**State.** `story_w<n>` (watched, on a finished chapter) and `story_o<n>` (offered) in the protected `tours` region of `guide_json`; no new table, column or personal data. Skip leaves a chapter unwatched.

**Shelf.** "Zorp's story" in the Milestones section of the Progress tab (`templates/partials/story_shelf.html`, `static/js/story-shelf.js`, profile page only): Chapter 0 first, unlocked chapters with Watch or Watch again, locked ones with "Unlocks at N badges" and, for chapters 3 and 6, the second way in.

**Files and caps.** New: `models/story.py`, `static/js/story-chapters.js` (cap 20,500 B), `static/css/story.css` (4,800), `static/images/story-props.svg` (6,200; a rock, a door, a toaster, a postcard; the planet, ship, crew and logbook are the arrival's), `static/js/story-shelf.js` (1,800), `templates/partials/story_shelf.html`, `scripts/test_story_chapters_smoke.py`. `zorp-stage.js` got four prop names and `addProps` (23,771 of 24,000). Raised: the CSS tree 268,900 to 273,700 (+4,800, the new on-demand `story.css`) in `test_u8_a11y_smoke.py`, `test_zorp_charm_smoke.py` and `test_gcse_maths_hints_ladder_smoke.py`, dated "2026-11-08: E10 phase 8". Versions: `guide.js` v26, `guide-preview.js` v10, `zorp-stage.js` v2 (island), story files v1, `sw.js` `pb-v120`. `DISMISS_APPROVED` gained "Skip story" and "Later". Preview: `/guide-preview?story=0..6`, `?story=offer3`.

**Rough.** The Home chapter uses the positive `aww` face for the wistful beat (no negative face, so no new lore context). The crew's names are not tied to which rig is which; the line says "from the left". The shelf's watched state needs the page's guide state, so a flag lost to the tours byte budget would show a chapter as new again.

### 11.5 Left for later or rough

- ~~The Practice tour still opens right after Start~~ (phase 3: the coach replaces it, section 11.6).
- `stage.css` has 124 B of headroom (the badge stage got its own sheet, section 11.7).
- The scene-1 landing has no sound (no tap yet on that page, by the existing rule); later scenes can sound after Continue.
- No automated test runs the stage in a browser; the Playwright walk above is manual (scripts not in the repo).

### 11.14 Amber highlights (2026-11-09)

David asked for Zorp's highlights to contrast more with the blue UI. The app tour and spotlight outline (`.pb-tour-target`), the tour card's left edge, the coach callout's left edge and target outline, and the per-tab tour spotlight (`.guide-spot`) now use `--on-streak` (amber: `#b45309` light, 4.9:1 on the page; `#fcd34d` dark) instead of `--primary`. `coach.css?v=3`, `tour.css?v=2`, `chrome.css?v=48`, `sw.js` `pb-v121`.

### 11.15 Lesson quiz spotlight fix (2026-11-10)

David saw the lesson-quiz spotlight card on entering a lesson with nothing highlighted. Cause: the spotlight matched the inline quiz button at the top of the lesson, which `lesson-progress.js` (`initQuizCta`) removes a moment later and replaces with the end-of-lesson bar (`.lesson-quiz-cta-bar`, `a.lesson-quiz-cta-btn`). Fix in `zorp-tour.js`: the `lessonquiz` target is now that bar's button; the spotlight waits, with no time limit, until the pupil scrolls it into view (so nothing shows at the top of the lesson); and any open spotlight now closes itself if its target is removed or hidden, so a card can never point at nothing. Copy: "Here’s the quiz. It covers the whole lesson, and afterwards you can retry any you missed." Checked in a browser at 1280 and 390 wide: no card at the top, amber outline on "Take the quiz" with the card clear of it, no card on a second visit. `zorp-tour.js?v=3` (cap 34,600), `sw.js` `pb-v122`.
