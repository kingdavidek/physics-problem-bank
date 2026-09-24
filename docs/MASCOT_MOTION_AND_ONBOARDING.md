# Zorp motion package, mobile onboarding, and kid-facing UX polish (E7)

**Status:** Phase 0–1.6 built. Written 2026-09-18 after reviewing `docs/ANIMATION_ONBOARDING.md` (E6, shipped), `docs/ENGAGEMENT_E5.md`, `docs/ENGAGEMENT_VISUAL.md`, `docs/MOBILE.md`, `docs/UI_REDESIGN.md`, the mascot partials, `celebrate.js`, `guide.js`, `sound.js`, the PWA files and the smokes that pin them.
**Owner of decisions:** David. **Builder:** any agent, one phase per commit, David confirms each phase before the next starts.
**Read first:** `docs/AI_HANDOFF.md` §3 (hard invariants), `docs/SECURITY_AND_GDPR.md` §S0.3 and §6.1, `docs/ANIMATION_ONBOARDING.md` §2 (E6 decisions — this plan keeps every one of them).

---

## 0. What we are building, in one paragraph

Zorp stays the one hand-drawn inline SVG we have, but gets a proper rig (separately animatable head, eyes, pupils, antennae, feet, and new arms) and a small motion runtime (`static/js/zorp-motion.js`) that plays named clips — idle breathing with blinks, cheer, wobble, think, wave, point, sleep — on **both** the corner buddy and the Guide overlay, with a sequencer so clips chain smoothly instead of snapping. `celebrate.js` gains a mascot channel so every correct and incorrect answer gets a reaction on the same beat as the checkmark and sound. New users on mobile get a four-screen welcome flow (`/welcome`) before the profile page: Zorp says hello, the pupil picks a level and a starting topic, and lands directly on that topic's Practice page with a first question ready. Around that: bouncier buttons, a proper page-to-page transition, a confetti/sparkle refresh, a "less motion" setting for pupils who find the movement distracting, and a small set of ambient touches (Zorp peeks in on the streak ring, sleeps on the offline page, waves on the install banner). No new libraries, no Lottie, no CDN, no new personal data.

---

## 1. What already exists (so we extend, not rebuild)

| Thing | Where | State |
|---|---|---|
| Corner buddy SVG (64×64), 7 faces switched by `data-face` | `templates/partials/buddy.html`, `study-buddy.js` | Shipped. Groups: `.buddy-head`, `.buddy-eye--l/--r`, `.buddy-foot--l/--r`. No arms, no antenna/pupil groups, no `transform-origin` per part |
| Guide overlay (origin story, 5 tours, reward beats) | `guide.js`, `guide-catalog.js`, `partials/guide.html` | Shipped (E6). Gestures `wink/nod/shake/tap` are overlay-only, ~1.2 s CSS keyframes |
| Static pose kit (11 stills, 80×80) for badges | `models/zorp_kit.py`, `partials/zorp_kit.html` | Shipped. Smoke pins the 11 tokens and that the live buddy stays separate |
| Answer celebration (pop, drawn tick, XP float, confetti every 3rd, tones) | `celebrate.js`, `sound.js`, `practice.css` | Shipped. **Does not touch the mascot.** `quiz-runner.js` bypasses it |
| Custom DOM events | `mcq-correct`, `mcq-reset`, `pb-quicktest-checked`, `pb-buddy-refetch` | Available hooks |
| Reduced motion | 22 files gate on `prefers-reduced-motion`; no in-app toggle | OS-level only |
| Signup flow | `register()` → `/profile` + Guide origin overlay on first load | No welcome screens, no topic picker |
| Settings storage | `user_profile_settings` via `models/social.py` (`guide_json` with size cap) | Reusable for onboarding state and a motion preference |
| Budgets and pins | `test_u8_a11y_smoke.py` (CSS 240 kB total / 210 kB core per §2 #11, raised from 226/199; today 220,510 B total / 195,518 B core), `test_pwa_smoke.py` (`pb-v87`), `test_guide_smoke.py` (bans `lottie`/`jsdelivr`), `test_zorp_kit_smoke.py`, `test_buddy_smoke.py` (`v4`/`v8` markers) | Every phase must keep these green or update them deliberately in the same commit |

The gaps are therefore precise: no rig, no clip runtime, no mascot channel in `celebrate.js`, no welcome flow, no motion setting, no cosmetics layer, and CSS headroom of ~24 kB against the raised budget (§2 #11) before it bites again.

---

## 2. Design decisions (proposed — David confirms, then they are frozen like E6 §2)

1. **One character, one drawing.** Rig the existing buddy SVG; do not redraw Zorp. Badge stills stay as they are (the pose-kit smoke pins them).
2. **Motion is CSS keyframes + Web Animations API (WAAPI) driven from one runtime.** WAAPI (`element.animate`) is native, CSP-safe, needs no library, and gives us sequencing, cancel, and `finished` promises that pure CSS class-toggling cannot. Keyframe *definitions* live in CSS custom properties/keyframes where they are shared with the Guide; the runtime only chooses and chains them.
3. **Every clip has a reduced-motion variant** (a face swap and a colour pulse, no translation) and the runtime honours both the OS setting and a new in-app "Less motion" switch. Default follows the OS.
4. **Reactions never delay answers.** The mascot reacts *after* the grading UI has rendered (next animation frame); grading, XP and feedback text never wait on a clip. If `zorp-motion.js` fails to load, `celebrate.js` behaves exactly as today.
5. **Incorrect-answer reactions are warm, never mocking.** No head-shake on wrong (that reads as disapproval to a 12-year-old); Zorp does a small "hmm" tilt with a thought bubble and the feedback copy stays "Not quite — look at the hint". The shake keyframe stays on the *button* only.
6. **Onboarding is a server-rendered route, not an overlay**, so it works before the Guide loads, survives reloads, and is testable with the existing route smokes. It is logged-in-only (same as the Guide) and skippable on every screen. It stores exactly two new facts: chosen level and chosen starting topic (both already public-in-app choices, not personal data) plus a `welcome_done` flag in `guide_json`.
7. **No dark patterns.** No streak-loss shaming, no "your friends are ahead", no countdowns, no notification prompt inside onboarding. Sound stays default off. Nothing new defaults to visible to other users (SECURITY §S0.3).
8. **CSS budget is a hard wall.** New motion CSS goes into a route-agnostic `static/css/motion.css` (≤ 8 kB minified-ish) and the budgets in `test_u8_a11y_smoke.py` are raised by exactly that amount in the same commit, with the reason in the commit message. Nothing else grows.
9. **No new third-party code, fonts, or assets.** Sparkles/confetti stay procedural (canvas/DOM particles as now). Sounds stay oscillator tones; a phase may add two or three new *tones*, not files.
10. **Feature gate answered once, in Phase 0.** `python scripts/ops_cadence.py feature-gate`: Q1 (new personal data) no — level and topic are preferences, not profile data; Q2 (child more visible) no; Q3 (new processor) no; Q4 (profile/rank/nudge) yes for the onboarding recommendation and reactions → note the DPIA Children's Code standard-13 review in the Phase 0 commit and keep nudges to "here is a first question" only.
11. **CSS budget raised once, deliberately (2026-09-20).** David confirmed a bigger CSS budget is fine *because* it buys headroom for planned work, not because bytes make motion smoother — WAAPI is already the fluidity lever, not the budget (see Phase 1). `CSS_BUDGET_BYTES` 226,000→240,000 and `CSS_CORE_BUDGET_BYTES` 199,000→210,000 (+14,000/+11,000) in `scripts/test_u8_a11y_smoke.py`, covering `motion.css`'s existing 8 kB cap (§2 #8) plus a first slice of Zorp cosmetics (#12/#13 below). Record actual bytes used per phase in the constant's comment; do not raise further without a new dated, justified entry here.
12. **No animation library.** Reconsidered and confirmed out: Lottie, GSAP, Rive and similar stay banned (E6 §2 #3/#10 stand unchanged). WAAPI + hand-authored SVG/CSS is the right architecture for a CSP `'self'`, no-CDN, no-build-pipeline site; a library would cost real CSP/maintenance/weight budget to solve a problem (fluidity) that actually lives in rig quality and runtime easing, not the animation engine.
13. **No second character — cosmetics instead (2026-09-20).** E6 §2 #1 ("one mascot") stays frozen. Instead of a second character, Zorp gets a small cosmetics/customisation layer on the *same* rig: colour, antenna/feet size, mouth shape (free — CSS variables and `transform: scale()` on rig groups Phase 1 already creates) and, later, hats/hair/shoes (costs new artwork — small SVG overlays positioned relative to `buddy-head`/`buddy-foot`). **First slice is automatic/content-facing, not pupil-facing**: cosmetics change on their own (seasonal, or tied to the existing `MILESTONE_CATALOG['pose']` mechanism in `models/gamification.py`, resolved through `models/zorp_kit.py`'s `resolve_pose`), with no new pupil-facing picker, no new stored personal preference, and no feature-gate re-run needed. A pupil-facing picker (a child choosing Zorp's own look) is real, larger scope — new UI, a new stored preference, a fresh Q1 feature-gate answer, a Children's Code DPIA touch — and is **explicitly deferred**: do not build it until David asks for it as its own phase. This supersedes the smaller "seasonal hats via pose-kit costume tokens" idea in the old §6, which is folded into Phase 1.5/1.6 below.

---

## 3. Architecture

### 3.1 The rig (`templates/partials/buddy.html`)

Add groups and origins without changing the seven face names or their order (the zorp-kit smoke asserts them):

```
svg.buddy-mascot
└─ g.buddy-root                 (whole-body squash/stretch, transform-origin 50% 90%)
   ├─ g.buddy-shadow            (ellipse under feet, scales with jumps)
   ├─ g.buddy-foot--l / --r     (exist)
   ├─ g.buddy-arm--l / --r      NEW: short rounded paths, transform-origin at shoulder
   ├─ g.buddy-body              (ellipse + highlight; transform-origin 50% 100%)
   └─ g.buddy-head              (exists; transform-origin 50% 80%)
      ├─ g.buddy-antenna--l/--r NEW groups around the existing paths, origin at base
      └─ g.buddy-face--* ×7     (exist)  each eye: g.buddy-eye > g.buddy-pupil NEW
```

Rules: every animated group gets `transform-box: fill-box; transform-origin` in CSS so rotations pivot correctly on all browsers (Safari needs `transform-box`). Antennae get a tiny independent wobble so idle never looks frozen. Arms default tucked so existing 56 px corner rendering does not change silhouette noticeably.

### 3.2 The runtime (`static/js/zorp-motion.js`, ~300 lines)

```js
window.pbZorp = {
  play(name, opts)        // 'idle'|'blink'|'cheer'|'wobble'|'think'|'wave'|'point'|'sleep'|'peek'|'nod'|'wink'|'tap'|'shake'
  react(kind, opts)       // 'correct'|'wrong'|'streak'|'milestone'|'lesson_complete'|'first_correct' → picks a clip + face, respects cooldowns
  setFace(name)           // thin wrapper over data-face, used by study-buddy.js and guide.js
  idle(on)                // start/stop the ambient loop (breathing + random blinks + occasional antenna twitch)
  bind(el)                // attach to a mascot svg (corner buddy, overlay mascot, welcome hero)
  motionLevel()           // 'full' | 'reduced' | 'off' (OS + in-app setting)
}
```

Clip table (name → keyframes on which groups, duration, reduced-motion fallback). All clips are additive over the idle loop (idle runs on `.buddy-root`, clips on sub-groups) so they blend instead of snapping.

| Clip | What moves | Duration | Reduced fallback |
|---|---|---|---|
| `idle` | root scaleY 1→1.02 breathing 3.2 s; blink every 3–6 s (pupils scaleY→0.1 for 120 ms); antenna 2° sway | loop | face only, no loop |
| `cheer` | root jump (translateY −8, squash on landing), arms up, face `celebrate`, antennae flick | 700 ms | face `celebrate` + brand-colour pulse on body 300 ms |
| `wobble` | root rotate ±6° damped ×3, face `nudge`, one arm to "chin" | 600 ms | face `nudge` |
| `think` | head tilt 8°, pupils look up-right, antenna slow bob | 900 ms | face `weak-topic` |
| `wave` | arm--r rotate −40°↔−70° ×3, face `milestone` | 900 ms | face `milestone` |
| `point` | arm--r extends toward `opts.target` side (left/right/down), head follows | 500 ms hold | face only |
| `sleep` | head droop 12°, eyes closed (pupils hidden), slow breathing, "z" sparkle | loop | closed-eye face |
| `peek` | root translateX from edge, head tilt | 500 ms | none (skip) |
| `nod/wink/tap/shake` | keep existing E6 keyframes, now runnable on the corner buddy too | as now | as now |

Cooldowns: `react('correct')` alternates among three variants (cheer / wave / small hop) and never repeats the same one twice; `react('wrong')` is always `wobble` (predictable is kinder). A global rate limit of one reaction per 900 ms stops rapid quick-check clicking from stacking clips.

### 3.3 Hooks

* `celebrate.js` `correct()`/`wrong()`: after existing work, `requestAnimationFrame(() => window.pbZorp && pbZorp.react(ok ? 'correct' : 'wrong', { streak: n }))`. `milestone`, `streakRound`, `lessonComplete` call `react` with their kind. Nothing else in `celebrate.js` changes.
* `quiz-runner.js` (lesson quizzes, quicktest): route its `is-correct`/`is-wrong` marking through `pbCelebrate.correct/wrong` so lesson quizzes get the tick, sound and mascot for the first time (today they get none). Timed quizzes (`data-guide-quiz`) keep reactions but the mascot is `off` for the overlay per E6.
* `guide.js`: replace the four `playGesture` cases with `pbZorp.play(gesture)` on the overlay mascot; catalog `gesture:` field values extend to the new clip names. `test_guide_smoke.py` still finds `playGesture`, `data-gesture`, and the four keyframe names because the CSS keyframes are kept and the function name stays.
* `study-buddy.js`: on `pb-buddy-refetch` face change, call `pbZorp.play('nod')` instead of the bare `.is-reacting` hop; start `idle(true)` on mount, `idle(false)` when the tab is hidden (`visibilitychange`) to save battery.

### 3.4 Mobile onboarding route (`/welcome`)

Server: `app.py` `welcome()` (GET) + `welcome_step()` (POST, CSRF, logged-in). `register()` redirects to `/welcome` instead of `/profile` when `guide_json.welcome_done` is false; `/welcome` redirects to Practice if already done. Four screens, one template `templates/welcome.html` with `data-step`:

1. **Hello** — full-bleed Zorp hero (same SVG at 160 px, `wave` on load, `idle` after), "Hi, I'm Zorp. I live in Problem Bank and I'll cheer you on." One button: *Let's go*. Skip link top-right on every screen ("Skip for now" → Practice home).
2. **Where are you studying?** — big tap cards: European School S1 / S2 / S3, GCSE, A-level, G8 (whatever `topic_registry` levels are enabled). Zorp `point`s at the cards. Stores `level`.
3. **Pick a first topic** — 6–8 topic cards for that level with the existing topic icons and one-line blurbs from `SYLLABUS_MODULES`; a "Surprise me" card. Zorp `think`s while the pupil reads, `cheer`s on tap. Stores `topic`.
4. **Ready** — "Your first question is ready. Answer it and I'll do a dance." Button *Start* → `/practice/<level>/<subject>/<topic>` with `?first=1` so `celebrate.js` treats the first correct answer as `first_correct` (already a reward beat). Sets `welcome_done`.

Mobile-first layout: one column, 44 px targets, bottom-anchored primary button above the safe area, progress dots. Desktop shows the same at `--shell-max`. On desktop/existing users nothing changes; **Replay intro** in settings gets a second link, *Replay welcome*. The Guide origin story still plays on first Practice load after welcome, but its first line is shortened since Zorp has already introduced himself (catalog copy change only).

### 3.5 Motion preference

* `user_profile_settings.motion_preference` ∈ `system|reduced|off` (default `system`), handled in `models/social.py` beside `theme_preference`; exposed in settings next to Sound with the same partial (`settings_switch.html`). Rendered as `data-motion` on `<body>` by `base.html`; `pbZorp.motionLevel()` and the CSS `@media` blocks both respect it (CSS via `body[data-motion="reduced"]` selectors that mirror the media query).
* Because of the known settings-switch persistence bug (AI_HANDOFF §1.1), this phase uses a plain `<select>` for the three values, not the switch partial, and adds a smoke asserting a POST persists all three.

### 3.6 Files touched per phase (so cache bumps are predictable)

`templates/partials/buddy.html`, `static/css/motion.css` (new, loaded in `base.html` after `chrome.css`), `static/js/zorp-motion.js` (new), `celebrate.js`, `quiz-runner.js`, `study-buddy.js`, `guide.js`, `guide-catalog.js`, `app.py` (welcome routes + settings), `templates/welcome.html` (new), `templates/profile_settings.html`, `models/social.py`, `static/js/sw.js` (`CACHE_VERSION`), `templates/base.html` (`?v=` bumps + `data-motion`), smokes.

---

## 4. Safeguarding, accessibility, privacy checklist (apply to every phase)

* Mascot SVGs stay `aria-hidden`; reactions never carry meaning that is not also in text (the feedback line and `aria-live` region already do this).
* `prefers-reduced-motion` and `data-motion` honoured by every keyframe and WAAPI call; no clip flashes more than 3 times a second; no full-screen colour flashes (confetti is fine — small particles).
* Onboarding copy: no "everyone else", no timers, no shame. Skip is a real link, not a small grey text. Age-neutral wording; Zorp never asks anything about the pupil.
* New stored fields: `level`, `topic` (preferences), `welcome_done`, `motion_preference`. Add one row each to the ROPA table in `docs/SECURITY_AND_GDPR.md` and to the export/erase scripts (`scripts/gdpr_export_user.py`, `gdpr_erase_user.py` — settings are already exported wholesale; verify, do not assume).
* Nothing new is visible to other users. No analytics, no "tour completed" beacons.
* Offline: `/welcome` is not precached; if offline mid-flow, the existing `/offline` page appears (with sleeping Zorp, Phase 4).

---

## 5. Phases

Each phase is one commit, ends with `python scripts/run_smoke_tests.py` green, both cache bumps (`?v=` in `base.html` and `CACHE_VERSION` in `sw.js` + `test_pwa_smoke.py`), and a line in `docs/AI_HANDOFF.md` §1/§9. Estimates are agent-time on the laptop.

### Phase 0 — Spec freeze + gate (½ h)
Confirm §2 with David. Run the feature gate, record answers in this file. Add `scripts/test_zorp_motion_smoke.py` skeleton that asserts: no `lottie`/`jsdelivr`/`unpkg` anywhere in `static/js` or `static/css`; every `@keyframes` in `motion.css` has a matching rule inside a reduced-motion block; `motion.css` ≤ 8 kB.

### Phase 1 — Rig + runtime + idle (2–3 h)
* Add groups/origins to `buddy.html` per §3.1's rig diagram — this must land named `buddy-antenna--l`/`buddy-antenna--r` and confirm `buddy-foot--l`/`buddy-foot--r` (existing) both get `transform-box: fill-box; transform-origin`, since Phase 1.5's cosmetics scale variants hook onto exactly these groups (faces untouched). Update `test_zorp_kit_smoke.py::test_live_mascot_unchanged` only if it greps for markup that legitimately changed (it checks face names/order and the absence of pose-kit classes — both still hold).
* `zorp-motion.js` with `bind/play/idle/setFace/motionLevel` and the clips `idle`, `blink`, `cheer`, `wobble`, `think`, `wave`, `point`, `nod/wink/tap/shake`.
* `motion.css` with shared keyframes + reduced variants + `transform-box` rules.
* Wire `study-buddy.js` to bind the corner buddy and run idle. Add a *Motion* section to `/styleguide` and to `/guide-preview` with a button per clip (dev only).
* Smoke: runtime file exposes the API names; corner buddy markup has `buddy-arm--l`, `buddy-pupil`; `test_buddy_smoke.py` version markers bumped (`study_buddy_js == 'v8'`).
**Done when:** on Practice, Zorp breathes and blinks in the corner; each clip plays from the styleguide; with reduced motion only faces change.

**Built 2026-09-22 (D5 resolutions kept as shipped):** `g.buddy-body` is nested *inside* `.buddy-head` (a sibling of the antennae), not a sibling of it, so the E6 nod/shake still rotate the whole blob as before; `.buddy-head`'s `transform-origin: 50% 72%` in `chrome.css` was **not** changed (§3.1's 50% 80% was not applied) so the E6 gestures stay pixel-identical; the existing `study-buddy-bob` animation on `<svg>` was left in place alongside the new breathing loop (flagged for David to judge visually, not removed here).

### Phase 1.5 — Cosmetics, free set (1–2 h)
* Add a mascot-scoped custom property (e.g. `--zorp-accent`, `--zorp-antenna`, `--zorp-foot`) to `.buddy-mascot` in `buddy.html`, defaulting to today's `var(--brand-500)`/`var(--brand-400)`/`var(--brand-700)` values so nothing changes visually until a cosmetic is actually applied. **Do not** repoint the shared `--brand-*` tokens themselves — they're used site-wide (buttons, site title, chrome.css); a mascot cosmetic must not recolour the whole UI.
* Add 2–4 colour presets, a `scale()`-based size variant for `.buddy-antenna--l/--r` / `.buddy-foot--l/--r` (from Phase 1's rig), and 2–3 alternate mouth `<path>`s behind a `data-mouth` attribute.
* Wire selection through the existing milestone/seasonal mechanism (`MILESTONE_CATALOG['pose']` in `models/gamification.py`, resolved via `models/zorp_kit.py`'s `resolve_pose`) — automatic, no new pupil-facing UI, no new stored personal preference (§2 #13).
* This is where the old §6 "seasonal hats via pose-kit costume tokens" idea is absorbed: generalise `zorp_kit.py`'s costume macros from one fixed full-body macro per costume into overlay-only macros (a hat/shoes/etc. `<g>` emitted on its own), so the same mechanism can eventually sit over either a pose-kit still or the live rig. Only relax `test_zorp_kit_smoke.py`'s live-buddy/pose-kit separation assertions if this phase actually shares an overlay macro between the two systems — don't relax them speculatively otherwise.
* Smoke: new attribute/variable names exist; existing pinned `POSE_TOKENS` (11) and `COSTUME_TOKENS` tuple in `test_zorp_kit_smoke.py` are unchanged unless a genuinely new named token is added, called out explicitly.
* Raise `CSS_BUDGET_BYTES`/`CSS_CORE_BUDGET_BYTES` per §2 #11 in the same commit as the CSS that uses the new headroom; record the actual bytes used.
**Done when:** Zorp's colour/antenna-size/mouth can vary automatically (e.g. by milestone) without any pupil-facing control, existing pinned tokens/smokes are untouched or deliberately and visibly updated, and CSS stays under the raised budget.

**Built 2026-09-23:** `data-mouth` was scoped to the resting `.buddy-face--nudge` face only, as a swap (the existing mouth `<path>` got `buddy-mouth buddy-mouth--smile`; `--grin`/`--cat` siblings were added with `display="none"` and CSS shows exactly one), not an overlay — buddy.html's other six hand-drawn faces have no shared mouth element, so this ambiguity in the plan was resolved in the markup and CSS rather than touching them. A dev-only `#sg-zorp-looks` demo on `/styleguide` renders each `LIVE_LOOKS` entry for visual review (not a pupil-facing picker, so in scope); `scripts/test_guide_smoke.py`'s pinned assertion that `guide.html` shares the mascot macro was updated to also pin that it passes `look=buddy_look`, which tightens rather than weakens that check. Colour/limb properties are `--zorp-body`/`--zorp-accent`/`--zorp-limb` (fallback to `--brand-500`/`--brand-400`/`--brand-700`, never redefining `--brand-*` itself), with three presets (`violet`/`sunny`/`mint`) built from the existing `--xp-*`/`--streak-*`/`--chem-*` ramps. Antenna/foot size uses the CSS `scale` property (not `transform: scale()`), so it composes with the idle-sway/WAAPI clips already running on those parts. Selection is server-side only: `models/gamification.py`'s new `latest_pose_milestone()` reads the user's most-recently-earned catalog milestone that carries a pose (`user_milestones`, no stored cosmetic preference), and `models/zorp_kit.py`'s new `live_look()` maps that pose token to a look dict (`scholar`→violet/long antennae, `jump`→sunny/long antennae/big feet/grin, `wave`→mint/short antennae/cat mouth); `buddy_mascot(look=...)` renders it as `data-zorp-*`/`data-mouth` attributes, defaulting to today's exact markup when there's no look. The costume/overlay-macro refactor of `zorp_kit.py` and any seasonal (non-milestone) selection are explicitly deferred to Phase 1.6, per D6 — `partials/zorp_kit.html`, `ACTION_TOKENS`, `COSTUME_TOKENS`, `POSE_TOKENS` and `MILESTONE_CATALOG` pose values are untouched. `motion.css` is 4,028 bytes (cap 8,000); the site-wide CSS budget was **not** raised — `CSS_BUDGET_BYTES`/`CSS_CORE_BUDGET_BYTES` in `scripts/test_u8_a11y_smoke.py` keep their existing values, with their comments updated to the measured bytes.

### Phase 1.6 — Cosmetics, artwork set (later, separately confirmed)
* Design 2–4 hats/hair/shoes as new, simple, original (not stock-asset) SVG `<g>` overlays positioned relative to `buddy-head`/`buddy-foot`. Phase 1.5 did not build an overlay-macro mechanism (deferred, per its "Built" note above) — this phase's own first job is generalising `zorp_kit.py`'s costume macros from one fixed full-body macro per costume into overlay-only macros, so the same mechanism can eventually sit over either a pose-kit still or the live rig. Only relax `test_zorp_kit_smoke.py`'s live-buddy/pose-kit separation assertions if this phase actually shares an overlay macro between the two systems. Seasonal (non-milestone) cosmetic selection is also this phase's to pick up if wanted.
* Only start once Phase 1.5 is confirmed working and its actual CSS cost is known; top up the budget further only if truly needed, with a new dated §2 entry recording the reason and the delta (same discipline as #11).
**Done when:** at least one hat/hair/shoe overlay renders correctly on the live rig at both corner (64 px) and welcome-hero (160 px) sizes, still automatic/content-facing only.

**Built 2026-09-24:** Added `templates/partials/zorp_overlays.html` with two overlay-only macros, `zorp_hat(name, x, y)` and `zorp_shoe(name, x, y)`, each emitting exactly one `<g class="zorp-hat(--shoe) zorp-hat(--shoe)--NAME" transform="translate(x y)">` in an anchor-local coordinate frame — the gear's own centre is local `(0,0)`, so the caller's `translate()` is the only thing that differs between contexts. The pose kit's three costumes that had inline hardcoded headwear (showman's quiff, scholar's mortarboard, chef's toque) now call `zorp_hat(name, 40, 22.5)` at the exact same point in their paint order, with the shape data translated into the local frame; this was verified byte-for-byte against pre-edit captures (same geometry, only the wrapping `<g>` differs) and the default `buddy_mascot()` render plus explorer/all 7 action-token stills remain byte-identical to before this phase. The live rig (`partials/buddy.html`) imports the same macros and conditionally renders `zorp_hat(look.hat, 32, 14.5)` as the last child of `.buddy-head`, and `zorp_shoe(look.shoes, 24|40, 56.5)` inside each foot group — plain `{% if look.hat %}`/`{% if look.shoes %}` Jinja (not CSS display toggling), written on the same source line as the preceding element so a look without hat/shoes keys still renders byte-identical to before this phase (also verified directly). Three designs: `mortarboard` is the extracted-and-shared original scholar art, now wired into `LIVE_LOOKS['scholar']`; `beanie` (hat) and `sneakers` (shoes) are two new original designs, wired into `LIVE_LOOKS['wave']` and `LIVE_LOOKS['jump']` respectively. `OVERLAY_HATS`/`OVERLAY_SHOES` in `models/zorp_kit.py` hold the full art catalogue (`mortarboard`, `beanie`, `toque`, `quiff` / `sneakers`); `LOOK_HATS`/`LOOK_SHOES` are a deliberate subset actually approved for the live rig — `toque` and `quiff` stay kit-only for now. Selection stays exactly the Phase 1.5 mechanism (`latest_pose_milestone()` → `live_look()`, server-resolved, no stored preference, no pupil-facing picker); this phase added no new preference and no `/welcome` route (still Phase 3 — the 160px "welcome-hero" demo lives only in a dev-only `#sg-zorp-overlays` section on `/styleguide`, using a new `.sg-zorp-hero` CSS class). `static/css/motion.css` was not touched at all (confirmed no `zorp-hat`/`zorp-shoe` strings in it); only `static/css/pages.css` grew by the ~84-byte `.sg-zorp-hero` rule, so the CSS budget was **not** raised (`motion.css` still 4,028 bytes; tree now 220,510 bytes, core 195,518). `scripts/test_zorp_kit_smoke.py`'s live-buddy/pose-kit separation check was tightened, not relaxed: it now also asserts `buddy.html` never imports `partials/zorp_kit.html`, that it does import the shared overlay macros, and that `zorp_overlays.html` itself contains none of either character's internal drawing-code strings (`buddy-`, `zorp-pose`, `_standing_body`, `_nudge_face`, `pose_`). Seasonal (non-milestone) cosmetic selection was **not** built this phase — it was optional per the doc's own plan and needs its own precedence rule against the milestone look; left for a later, separately confirmed slice.

### Phase 2 — Answer reactions everywhere (1–2 h)
* `celebrate.js` mascot channel (§3.3), `react()` cooldowns and variant rotation, `first_correct` handling.
* `quiz-runner.js` routed through `pbCelebrate` so lesson quizzes and quick checks get tick + tone + mascot.
* `guide.js` gestures via `pbZorp` on the overlay mascot; catalog gains `cheer`/`wave`/`think` where the copy asks for them.
* Two new tones in `sound.js` (`ding` for streak-of-3, `soft` for wrong — quieter than today's) still behind the sound switch.
**Done when:** correct → tick + Zorp cheers (varying), wrong → button shake + Zorp wobbles with a thought bubble; rapid clicking does not stack; timed quizzes unaffected; a pupil with reduced motion sees the face change only.

### Phase 3 — Mobile welcome flow (3–4 h)
* Routes, template, state (`guide_json.welcome_done`, `level`, `topic` in settings), redirect from `register()`, *Replay welcome* in settings, shortened origin-story opener.
* `welcome.html` uses the hero-sized rig; screens are plain forms (works without JS), enhanced with slide transitions and Zorp clips when JS is present.
* Smokes: `test_welcome_smoke.py` — GET/POST flow for a fresh user, skip at each step lands on Practice, done users are redirected, CSRF enforced, no `onclick=`, copy contains no banned nudges (regex: `friends are|behind|hurry|don't lose`), level/topic values validated against `topic_registry`. Extend `gdpr` export smoke to include the two preferences.
**Done when:** a new account on a 390 px viewport goes Hello → level → topic → first question in four taps, and *Skip* works everywhere.

### Phase 4 — Ambient touches and page feel (2 h)
* Page transition: replace `page-enter` fade with a 160 ms slide-up-and-fade on the main shell; back navigation slides down (View Transitions API where supported, CSS fallback).
* Buttons: `--ease-spring` press (scale 0.97 → 1.02 → 1) on `.btn` and `.mcq-btn`, 140 ms, reduced-motion → colour only.
* Sparkle refresh: confetti gets 2 shapes (dot, star) in brand/gold/xp colours; a small sparkle burst on the XP float; streak ring gets a one-second draw-on with Zorp `peek`ing over its edge on profile load (once per day, flag in localStorage like existing buddy flags).
* Offline page: sleeping Zorp with "No signal here — your saved lessons still work."; PWA install banner: Zorp `wave` line (E6 §5.4 backlog item, no focus steal).
* Empty states (no saved problems, no friends yet): Zorp `think` + one friendly line instead of plain text.
**Done when:** navigating feels continuous on a phone; nothing new triggers under reduced motion except colour; CSS total still under the (raised) budget.

### Phase 5 — Motion preference + polish (1 h)
* `motion_preference` end to end (§3.5), settings copy "Less motion — calmer animations", smoke for persistence.
* Battery/perf: idle loop paused on `visibilitychange` and when the buddy is scrolled out of view (`IntersectionObserver`); WAAPI animations cancelled on unmount; a Playwright check in the cloud clone that Practice with 30 quick answers stays under 5 % long-frame time (optional, not a smoke).
* Docs: update `docs/ANIMATION_ONBOARDING.md` §11 to point here; add rule 17 to `AI_HANDOFF.md` §3: *"Mascot motion lives in `zorp-motion.js` + `motion.css`; every clip needs a reduced-motion variant; never add a third-party animation library."*

---

## 6. Optional later (not in E7)

* ~~Seasonal hats on Zorp via the pose kit's costume tokens~~ — superseded by the cosmetics system, §2 #13 and Phase 1.5/1.6.
* Pupil-facing cosmetics picker (a child chooses Zorp's own look) — deferred per §2 #13 until David asks for it explicitly as its own phase: new UI, a new stored preference, a fresh Q1 feature-gate answer, a Children's Code DPIA touch.
* Zorp "reads" the hint: `point` at the hint panel when a pupil gets two wrong in a row on one topic (E5.1 buddy weak-topic already tracks this).
* A lightweight "mood" that follows the streak (sleepy after 3 idle days, bouncy on a 7-day streak) — only with no guilt copy.
* Web push (E5.7) stays blocked on M5, unchanged.

---

## 7. Risks and how the plan handles them

| Risk | Mitigation |
|---|---|
| Safari transform-origin quirks on SVG groups | `transform-box: fill-box` on every animated group; test on iOS Safari via the styleguide before Phase 2 |
| CSS budget smoke fails | `motion.css` capped at 8 kB and budget raised by exactly that in the same commit; no other sheet grows |
| Clip stacking on fast clicking | global 900 ms cooldown in `react()`; WAAPI `cancel()` before a new clip on the same group |
| Onboarding annoys returning users | route only for `welcome_done == false`; Skip everywhere; *Replay* is opt-in |
| Reactions read as judgement | no head-shake on wrong; wobble + thought bubble; copy reviewed by David before Phase 2 ships |
| Settings persistence bug bites the motion switch | plain `<select>`, not the switch partial; smoke asserts persistence |
| Guide smoke bans | keep the four E6 keyframe names and `playGesture`; add strings, never remove |
