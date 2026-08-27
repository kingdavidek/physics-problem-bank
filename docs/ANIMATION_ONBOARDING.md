# Problem Bank — Guide & celebration (Phase A / E6)

**Last updated:** 2026-08-27  
**Status:** A1–A6 shipped — origin overlay, badge/streak/first-correct/lesson-complete rewards, five section tours, `guide_json` persist + Replay intro, CSS streak-fire on streak rewards. No Lottie.  
**Audience:** The next AI agent implementing this (and David, for copy/tone)  
**Parent:** new engagement track. Distinct from **E4.2 mascot farm** (economy / collectibles — still deferred).  
**Companions:** `docs/ENGAGEMENT_VISUAL.md`, `docs/ENGAGEMENT_E5.md`, `docs/UI_REDESIGN.md` §10 (U7 motion), `docs/SECURITY_AND_GDPR.md` §6.1, `docs/DPIA.md`

This is the canonical implementation plan. Do not invent a parallel onboarding system. Do not start E4.2 (farm / collectibles) from this doc.

---

## 0. What we are building

Two related surfaces that reuse the **existing alien buddy** (`templates/partials/buddy.html`):

1. **Guide** — Pokémon-style talking bubble / overlay.
   - Once: an **origin story** (came from another planet; the helper aliens users see are from there).
   - After that: **first-visit tours** of major sections (Practice, Learn, Daily, Compete, Profile). The overlay highlights real UI (buttons, tabs, cards) and explains them.
2. **Celebration beats** — Duolingo-style “whole moment” when something lands: badge unlock, streak milestone, and a few other wins. Not a new engine; an upgrade of `static/js/celebrate.js`.

**Not** a native app, not Lottie in v1, not a mascot farm, not a second character.

Tone: encouraging tutor, UK English, short. Fiction is clearly a **bot / mascot**, not a person (`docs/ENGAGEMENT_VISUAL.md` §1). Users are mainly **13+**.

---

## 1. Why this is feasible

The stack already has the hard parts. This track is **presentation + state**, not a new product domain.

| Piece | Where it lives today | Reuse |
|-------|----------------------|--------|
| Alien mascot (SVG, seven faces) | `templates/partials/buddy.html` | Same character on the big stage |
| Corner coach | `static/js/study-buddy.js`, `models/buddy.py` | Keep for nudges; Guide is a separate overlay |
| Confetti, XP float, checkmark, badge/streak once-per-key | `static/js/celebrate.js` (`window.pbCelebrate`) | Hook reward beats here |
| Modal + backdrop | `#site-search-overlay`, `#share-suggest-overlay` in `templates/base.html` | Copy overlay pattern, do not invent a third system |
| Motion policy | `prefers-reduced-motion` in CSS; celebrate/buddy already gate | All Guide motion must too |
| Sound | `sound.js`, default **off** | Optional celebrate clip; never auto-enable |
| Tab identity | `_resolve_nav_tab` / `_NAV_TAB_ENDPOINTS` in `app.py` | Tours key off **endpoint**, not only `nav_tab` |
| Overlay CSS home | `static/css/chrome.css` | New Guide styles live here |

**What does not exist yet:** fullscreen cinematic intro, dialogue runtime, per-section first-visit tours, a dedicated badge “moment” modal.

v1 is **dialogue overlay + 3–5 tours + upgraded badge/streak modal**. Not a Disney pipeline.

---

## 2. Design decisions (do not reopen unless David asks)

1. **One mascot.** Origin story and tours use the existing buddy SVG. Do not add a second character or emoji-only stand-in.
2. **One runtime.** `static/js/guide.js` owns story, tour, and reward presentation. `celebrate.js` still fires micro-delight (confetti, XP); Guide may listen and open a larger beat.
3. **Same overlay family.** Backdrop + panel + focus trap + Escape. Match search/share, do not import Driver.js / Shepherd / Lottie in v1 (CSP `'self'`, no extra eval, UI rule: no third-party UI framework).
4. **Never block study.** Skip / Not now always available except during a 1–2 second reward flash that still has a close control. If JS fails, the page is fully usable (same as buddy).
5. **Settings, legal, auth chrome are never auto-toured.** `profile_settings`, `/privacy`, `/terms`, `/login`, `/register`, `/offline` — skip.
6. **Tours fire on first visit to a primary surface**, not on every nested page. Example: Learn tour on `topics_index`, not on every lesson.
7. **State: localStorage for A1–A4; server JSON in A5.** Pilot can be client-only. Account switch / new device re-shows tours until A5. That is acceptable for the pilot.
8. **No analytics.** Do not send “tour completed” anywhere off-box. Logging is local/server flags only.
9. **E4.2 farm stays deferred.** Origin story is lore, not an economy, inventory, or collectible unlock tree.
10. **Animation format:** CSS + existing SVG face swaps + the existing confetti particles. A6 is CSS streak fire on the 7/30/100 reward beat. Do not add Lottie, WebM, or a CDN.

---

## 3. Architecture

### 3.1 Three modes of one overlay

| Mode | When | Layout |
|------|------|--------|
| `story` | Origin (once after first login / register) | Near-fullscreen: large mascot + speech bubble + Continue / Skip intro |
| `tour` | First visit to a section | Dimmed page + spotlight on a real element + bubble nearby (bottom sheet on narrow viewports) |
| `reward` | Badge, streak round, a few other wins | Centered modal: badge/flame + one line + optional confetti; auto-focus Close |

Step shape (data, not hardcoded in templates):

```javascript
{
  id: 'origin.planet',
  mode: 'story',          // story | tour | reward
  face: 'nudge',          // buddy SVG data-face
  lines: ['…', '…'],      // 1–3 short sentences
  highlight: null,        // CSS selector or null
  primary: 'Continue',
  skipLabel: 'Skip intro' // omit to hide skip (reward may use Close only)
}
```

### 3.2 Module split

| File | Role |
|------|------|
| `static/js/guide.js` | Runtime: queue, overlay, spotlight, typewriter-or-line reveal, reduced-motion, seen-flags |
| `static/js/guide-beats.js` **or** JSON in `static/js/guide-catalog.js` | Catalog of beats (copy + selectors + tour ids). Keep copy out of the runtime. |
| `static/css/chrome.css` | Overlay, bubble, spotlight, reward modal (tokens from `tokens.css`) |
| `templates/partials/guide.html` | One overlay shell in `base.html` (hidden until JS opens it). Include mascot via `buddy_mascot()`. |
| `static/js/celebrate.js` | Keep micro-animations. Call `window.pbGuide.reward(...)` when a Guide beat exists; otherwise current confetti-only path. |

Load `guide.js` **defer**, logged-in only (same gate as `study-buddy.js`). Guests do not see origin or tours.

### 3.3 Spotlight (tours) without a library

1. Show a full-viewport backdrop (`rgba` dim).
2. Measure `el.getBoundingClientRect()` for `highlight`.
3. Position a hole / clone box: `box-shadow: 0 0 0 9999px rgba(15, 23, 36, 0.55)` on a rounded rect matching the target, `pointer-events: none` on the dim, **do not** disable the highlighted control if the step says “try it” — v1 can be explain-only (pointer-events none on everything except overlay buttons) so tours cannot submit forms by accident.
4. Scroll the target into view (`scrollIntoView`, gated on reduced motion).
5. Recalculate on `resize` / `orientationchange`. If the selector is missing, skip that step (do not crash).

On viewports ≤640px: ignore XY spotlight; use a **bottom sheet** + named label (“The Practice tab at the bottom”) so we do not fight the tab bar.

### 3.4 Dialogue (Pokémon-like)

- Left/center: mascot (`data-face` swapped per step).
- Right/below: speech panel. Reveal **line by line** on tap/Continue (not a 90s typewriter unless reduced-motion is off **and** the line is short). Reduced motion: show full text immediately.
- Primary button: Continue / Next / Let’s go.
- Secondary: Skip intro (story) or Not now (tour). Skipping a tour marks it **seen** so it does not nag. Skipping origin marks origin complete.

### 3.5 State keys

**A1–A4 (localStorage):**

```
pb-guide-v1
```

JSON blob, not dozens of keys:

```json
{
  "v": 1,
  "origin": true,
  "tours": { "practice": true, "profile": false },
  "rewards": { "milestone:qotd_first": true, "streak:7": true }
}
```

If `localStorage` throws, treat everything as already seen (fail closed — no infinite overlay). Same spirit as buddy dismiss.

**A5 (server):** column `guide_json` on `user_profile_settings` (TEXT, default `'{}'`). Client hydrates on load (`<script type="application/json" id="pb-guide-state">`) and PATCHes via `PATCH /api/v1/me/settings` with `{ "guide": { ... } }` **or** a tiny `POST /api/v1/me/guide` — prefer extending settings if the payload stays small. Merge, do not overwrite unknown keys.

Include in GDPR export (`models/data_export.py` already dumps `user_profile_settings`). Erasure already cascades that row.

Do **not** log emails, tokens, or answer content in this blob.

### 3.6 Triggers (single dispatcher)

On `DOMContentLoaded` in `guide.js`, **logged-in only**:

```
if quiz_runner_mode: return          // never overlay a timed quiz
if endpoint in NEVER_TOUR: return
if !originSeen: play('origin'); return   // origin first, one session
if tour = tourFor(endpoint) and !seen(tour): play(tour)
```

Do not run a tour on the same load as origin. Do not stack Guide + buddy milestone toast: if Guide `reward` is showing, buddy `milestone` card may stay hidden that load (`study-buddy.js` already has show/hide). Spec: **Guide reward wins** over buddy milestone for that page load when both would fire (badge just earned). Buddy still handles weak-topic / streak-risk when no Guide overlay is open.

Celebrate micro-confetti can still run under a reward modal.

### 3.7 Endpoints vs tabs

`_NAV_TAB_ENDPOINTS` maps many routes to `profile` (including **settings** and search). Tours **must** use `request.endpoint` (or `document.body` data attribute), not `nav_tab` alone.

Expose in `base.html` on `<body>` or `#guide-root`:

```html
data-guide-endpoint="{{ request.endpoint }}"
data-guide-quiz="{% if quiz_runner_mode %}1{% endif %}"
```

---

## 4. Safeguarding, a11y, GDPR

Answer `python scripts/ops_cadence.py feature-gate` before coding:

| Q | Answer for this track |
|---|------------------------|
| New personal data? | **A5:** `guide_json` (boolean flags). ROPA + privacy notice updated in the same change. A1–A4 localStorage is strictly necessary functional storage (like buddy dismiss). |
| Child more visible? | No. |
| New third party? | No. A6 is CSS-only; do not load Lottie/CDN. |
| Profile / rank / nudge? | **Yes.** Tours and celebrations are nudges. Revisit DPIA Children’s Code **standard 12/13**. Copy: no streak-loss shaming; Skip always; no night-time push (E5.7 still blocked). |

Implementation rules:

- `role="dialog"`, `aria-modal="true"`, labelled by heading / bubble.
- Focus trap; restore focus on close.
- Escape = Skip / Close (same as search overlay).
- `prefers-reduced-motion: reduce` → no typewriter, no bob, no confetti, no streak fire (text + static mascot still OK).
- Sound stays default off.
- Origin is **fiction**; one line can say this is the study buddy, not a real person (consistent with `@problem_bot` labelling).
- Do not flash overlays on every page load. Seen flags are mandatory.
- Competitive copy on Compete tour: **friends only**, no global league.

When A1 ships, add a DPIA residual note: optional onboarding overlay, dismissible, no extra processors.

---

## 5. Content catalog

Draft copy — David can tighten. Keep each line ≤ ~90 characters where possible. UK English.

### 5.1 Origin story (`story`, id `origin`)

Suggested 5 steps (6 max). Face: `nudge` → `celebrate`.

1. “I’m not from around here. My planet sent helpers to Earth — to make maths (and a bit of science) less scary.”
2. “Those little aliens you’ll see? That’s my crew. I’m the one who hangs around in the corner.”
3. “I’ll cheer when you earn a badge, and I’ll nudge you if a topic needs another look. You can always tap Not now.”
4. “This site is for practising. Bottom tabs: Practice, Learn, Daily, Compete, Profile.”
5. “Ready when you are. Skip this any time from Settings later — if we add Replay intro.”

Primary last step: **Let’s go**. Skip intro on every origin step.

**When:** first authenticated HTML page after register/login if `origin` not seen. Do not wait for email verification (the verify banner must remain visible; overlay sits above content but below… actually overlay is on top; make sure Skip is obvious so they can reach the banner). Prefer showing origin **after** first successful login redirect to `/`, not on `/register` itself.

### 5.2 Section tours

| Tour id | Trigger endpoint | Skip if |
|---------|------------------|---------|
| `practice` | `index` | Guest; origin not yet done (origin plays first) |
| `learn` | `topics_index` | — |
| `daily` | `qotd_page` | — |
| `compete` | `friend_leaderboard_page` (not challenge_detail) | — |
| `profile` | `profile` only — **not** `profile_settings` | — |

**Never tour:** `profile_settings`, `legal_privacy`, `legal_privacy_simple`, `legal_terms`, `login`, `register`, `forgot_password`, `offline`, quiz runner endpoints (`_QUIZ_RUNNER_ENDPOINTS`).

**A3 ships three:** `practice`, `profile`, `daily`. **A3b** (optional same PR or follow-up): `learn`, `compete`.

#### Practice (`index`) — 4 steps

1. Highlight `#main-form` or `.practice-picker-card` — “Pick a subject and topic, then Start practising.”
2. Highlight mode/difficulty selects if present — “Standard is a typed answer. Multiple Choice is taps.”
3. If a problem is on screen, highlight Check / MCQ list — “Check your answer here. I’ll pop when you get a streak of correct ones.” If no problem, skip this step.
4. Highlight tab bar Practice — “This tab is home. The others are Learn, Daily, Compete, Profile.”

#### Learn (`topics_index`)

1. Topic grid — “Lessons and quizzes live here. Open a topic to read, then take the quiz.”
2. Optional: subject filters if they exist.

#### Daily (`qotd_page`)

1. Today’s question card — “One question a day. That’s the Daily habit.”
2. Streak / week board if visible — “Friends can see the week board. There is no public worldwide ranking.”

#### Compete (`friend_leaderboard_page`)

1. Board tabs — “This is friends only. Accuracy and effort among people you follow.”
2. Challenges link if in chrome — “Challenges are optional. No DMs.”

#### Profile (`profile`)

1. Streak / XP ring — “Your streak and XP. Missing a day can use a freeze if you have one.”
2. `#milestones` — “Badges you earn. New ones get a little celebration.”
3. Saved / revision if present — “Saved questions and your revision plan live here.”

### 5.3 Reward beats

| Reward id | Trigger | Visual |
|-----------|---------|--------|
| `milestone:<key>` | `pbCelebrate.milestone` / buddy prompt type `milestone` / `fromPayload` new_milestones | Large badge emoji from catalog + title + “You earned this.” Confetti if motion OK |
| `streak:7` / `30` / `100` | `celebrateStreakRound` | Flame / ring fill; copy “7-day streak” etc. No shame if they later drop |
| `lesson_complete` | `pbCelebrate.lessonComplete` | **A4:** short reward modal once; later lessons stay confetti-only |

Do not add a reward for every correct answer (U7.3 already pops check + XP). **first_correct** is A4, once, localStorage.

### 5.4 Other beats (backlog — do not build in A1–A3 unless leftover time)

| Beat | Notes |
|------|--------|
| First saved problem | “Find these under Profile → Saved.” |
| First friend / first challenge | Compete tour may be enough |
| Streak at risk | Keep **buddy** `streak_risk`; do not add a second overlay |
| Streak freeze consumed | Small shield on profile; buddy copy already softer |
| QOTD week complete | Tie to week board; reward modal optional |
| Topic mastered / status chip | Only if topic-status UI has a clear “complete” event |
| Lesson quiz 100% | `lesson_mcq_results` — confetti already possible via lessonComplete |
| PWA install | Optional mascot line on existing install banner — do not steal focus |
| Return after long absence | Welcome back, **no** guilt copy |
| Replay intro | Settings link in A5 |

---

## 6. Implementation steps

Ship in order. Each step is a reviewable slice. Full smoke green after each.

### A0 — Spec freeze (this file)

Already this document. When implementing, do not expand scope into farm/Lottie/App Store.

**Exit:** Agent has read this file, `ENGAGEMENT_VISUAL.md`, U7 in `UI_REDESIGN.md`, and feature-gate.

### A1 — Dialogue overlay + origin story

**Build:**

1. Partial `templates/partials/guide.html`: hidden overlay (`hidden`, `aria-hidden="true"`), mascot slot, `[data-guide-bubble]`, `[data-guide-primary]`, `[data-guide-skip]`.
2. Include from `base.html` for authenticated users only.
3. `guide.js` + origin steps in catalog. Line-by-line Continue. Skip marks `origin: true`.
4. CSS in `chrome.css`: full-viewport flex center; speech panel using existing card/radius/brand tokens; 44px taps; safe-area padding.
5. `data-guide-endpoint` on body.
6. Do not tour yet.

**Tests (`scripts/test_guide_smoke.py`):** overlay markup on `/` when logged in; absent when logged out; `guide.js` served 200; origin JSON/catalog contains ≥4 steps; no `onclick=` in the partial.

**Cache:** bump `CACHE_VERSION` (`pb-v67` → next) and `guide.js?v=` in `base.html`; update `test_pwa_smoke.py` if it lists scripts.

**Exit:** After register/login, origin plays once; Skip works; refresh does not replay; reduced-motion shows full lines.

### A2 — Badge (and streak) reward modal

**Build:**

1. Same overlay, `mode: 'reward'`. Centered medallion (reuse profile milestone emoji from `MILESTONE_CATALOG` if passed in).
2. `celebrate.js`: when `celebrateMilestone(key)` would burst, also `pbGuide && pbGuide.reward({ type: 'milestone', key })`. If Guide missing, keep current confetti-only.
3. Dedupe: Guide `rewards["milestone:"+key]` **and** existing `pb-u74-ms-` localStorage in celebrate.js — do not double-modal. Prefer one authority: if Guide is present, Guide records seen and celebrate still may confetti.
4. Streak 7/30/100: same, id `streak:N`. Copy without shame.

**Tests:** logged-in profile with a newly earned milestone (drive DB like `test_milestones_smoke.py`) shows overlay **or** celebrate still confetti if you stub Guide; at least assert `pbGuide.reward` is called from a tiny unit in the smoke by importing isn’t possible (browser JS) — assert catalog has reward ids and celebrate.js contains `pbGuide` hook string.

**Exit:** Earning a badge shows a closeable modal once; second page load does not.

### A3 — Section tours (Practice, Profile, Daily)

**Build:**

1. Catalog + spotlight helper.
2. Dispatcher using `data-guide-endpoint`.
3. Missing selector → skip step.
4. Mobile bottom-sheet fallback.

**Tests:** GET `/` logged-in with origin already set in… (client-only flags cannot be set from Flask test client easily). Options: (a) server A5 first for tests, or (b) assert catalog + selectors exist in HTML (`#main-form`, `#milestones`, tab bar). Prefer (b) in A3 and (a) in A5. Also: settings page HTML has `data-guide-endpoint="profile_settings"` and catalog never maps that id.

**Exit:** First visit to Profile explains streak + badges; Settings never auto-opens a tour.

### A3b — Learn + Compete tours

Same pattern. Compete copy: friends-only.

### A4 — Extra celebration polish

**Shipped:** `first_correct` once, and `lesson_complete` once (later lessons stay confetti-only). Streak flame CSS is A6 (reward-only, not every tab change).

### A5 — Persist `guide_json` + Replay intro

**Shipped:** `user_profile_settings.guide_json` (boolean flags). Hydrate `#pb-guide-state`; PATCH merge on `PATCH /api/v1/me/settings` `{ "guide": { ... } }` (debounced from `guide.js`). Settings **Replay intro** sets `origin: false` and redirects to Practice. Export/erase include the settings row. Privacy notice + ROPA updated in this change.

### A6 — Streak fire (CSS)

**Shipped:** CSS `pb-streak-fire` on `.nav-streak` / profile ring / reward medal / Profile tab icon when a **streak** reward plays (`playStreakFlame` in `guide.js`). Gated on `prefers-reduced-motion: no-preference`. Does **not** animate every tab change. CSS can do this beat — **no Lottie, WebM, jsDelivr, or extra vendor**.

---

## 7. How it would look in code (contracts)

### 7.1 `window.pbGuide`

```javascript
window.pbGuide = {
  play: function (id) {},      // 'origin' | 'practice' | …
  reward: function (spec) {},  // { type: 'milestone', key } | { type: 'streak', days }
  seen: function (id) {},
  resetOrigin: function () {}  // settings Replay
};
```

### 7.2 Priority if two overlays want the screen

1. Origin (until seen)
2. Reward (badge just earned this response)
3. Section tour
4. Study buddy card (corner)

Quiz runner: nothing.

### 7.3 CSP

Inline handlers remain forbidden. Guide is external JS. Dynamic HTML in the bubble is **text only** (`textContent`), never `innerHTML` with catalog strings that could include user data. Catalog is ours.

---

## 8. Files to touch (checklist)

```
docs/ANIMATION_ONBOARDING.md     this plan
docs/AI_HANDOFF.md               status + reading order
docs/ARCHITECTURE.md             related docs
docs/POTENTIAL_FUTURE_FUNCTIONALITY.md  E6 row
docs/DPIA.md                     nudge row when A1 ships
docs/ENGAGEMENT_VISUAL.md        pointer to Guide faces
templates/base.html              include partial; data-guide-endpoint; script tag
templates/partials/guide.html    new
static/js/guide.js               new
static/js/guide-catalog.js       new
static/js/celebrate.js           hook pbGuide.reward
static/css/chrome.css            overlay / bubble / spotlight
static/js/sw.js                  CACHE_VERSION
scripts/test_guide_smoke.py      new
scripts/test_pwa_smoke.py        version string if listed
app.py                           A5 column only
models/social.py                 A5 read/write guide_json
```

Do **not** change grading, generators, or `normalize_mode`.

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Overlay blocks Check | Quiz runner + problem-solving: no tour; Skip always; pointer-events on overlay chrome only |
| Infinite origin loop | Fail closed if storage throws; mark seen on Skip **and** last Continue |
| Settings tour by mistake | Endpoint allowlist, not `nav_tab == profile` |
| Double celebration (buddy + Guide + confetti) | Reward wins; buddy milestone hidden that load; confetti once |
| Wordy copy / 360px overflow | Max 2 sentences per step; bottom sheet on small screens |
| Children’s Code nagging | Each tour once; Replay is user-initiated |
| Scope creep to farm | E4.2 stays out of this file’s done definition |
| Lottie / unsafe-eval | Not in v1 |

---

## 10. Definition of done (whole track)

**A1–A3 minimum to call the track “real”:**

- [x] Origin story once per browser (A1) / per account (A5)
- [x] Badge reward modal once per key (A2)
- [x] Tours for Practice, Profile, Daily; never Settings/legal/auth (A3)
- [x] Learn + Compete tours; Compete copy friends-only (A3b)
- [x] First-correct and lesson-complete reward modals, once each (A4)
- [x] Skip / Escape / reduced-motion / no inline JS
- [x] `scripts/test_guide_smoke.py` green; full `python scripts/run_smoke_tests.py`
- [x] Cache bump; docs status updated *(A6 — `pb-v77`)*
- [x] Persist `guide_json` + Replay intro (A5)
- [x] CSS streak fire on streak reward (A6; no Lottie)

**E6 Guide track is complete.** Next product item is E4.1 if David asks.

---

## 11. Suggested build order for the next agent

**A1–A6 shipped.** Do not reopen Guide unless David asks.

Do not start E4.1, M5, or E5.7 in the same session unless asked.

---

## 12. Prompt for the next AI agent

Copy everything in the block below into a new chat (Agent mode). Attach or open this repo.

```
You are implementing Problem Bank Phase A / E6 (Guide & celebration).

Read first, in order:
1. docs/AI_HANDOFF.md (invariants, do not touch operator launch / M5)
2. docs/ANIMATION_ONBOARDING.md — THIS IS THE SPEC. Follow it. Do not invent a mascot farm (E4.2), Lottie, or a second character.
3. docs/ENGAGEMENT_VISUAL.md (tone, buddy SVG faces)
4. docs/UI_REDESIGN.md §10 U7 (motion already shipped; extend, don’t replace)
5. docs/SECURITY_AND_GDPR.md §6.1 — run the four questions; this feature is a nudge.

Goal for this session: implement A1 (dialogue overlay + origin story) unless the user asks for more. If A1 is already in the tree, continue with A2 then A3 as specified.

Constraints:
- Vanilla JS + existing Flask templates. No React, no Driver.js/Shepherd, no new CDN.
- Reuse templates/partials/buddy.html mascot. External JS only (CSP: no unsafe-inline, no onclick).
- Logged-in only. Never tour settings, legal, login, or quiz-runner pages.
- Skip / Escape / prefers-reduced-motion. Page must work if JS fails.
- Do not change grading, generators, or analytics.
- Bump CACHE_VERSION in static/js/sw.js and ?v= on new JS.
- Add scripts/test_guide_smoke.py; run python scripts/run_smoke_tests.py before you finish.
- Update docs/AI_HANDOFF.md status when a slice ships.
- UK English copy is drafted in ANIMATION_ONBOARDING.md §5; you may tighten but keep the origin lore (helpers from another planet).

Do not start E4.1 real-world questions, Play/TWA, or web push in this work.

Verify in the browser if you change UI: origin plays once after login, Skip works, refresh does not replay.
```

---

## 13. Document maintenance

When a slice ships: tick §10, move a one-liner into `docs/ARCHITECTURE.md`, set status at the top of this file (`A1 shipped`, etc.), and point `docs/AI_HANDOFF.md` here.

When the whole of A1–A3 is done: this track is the Guide; E4.2 farm remains a separate explicit product call.
