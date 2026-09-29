# Zorp expressions, poses and turning (E8)

**Status:** Phase 0 built and committed (17b8b38); Phase 1 built and committed upstream (a951fd5); Phase 2 built 2026-09-29, awaiting David's review. Decisions D1–D5 confirmed by David 2026-09-29 (§7.1); §2 is frozen. Written 2026-09-29 against `main` at 4db62e2. Sources read: `templates/partials/buddy.html`, `partials/zorp_overlays.html`, `partials/zorp_kit.html`, `models/zorp_kit.py`, `static/js/zorp-motion.js`, `zorp-triggers.js`, `celebrate.js`, `study-buddy.js`, `guide.js`, `guide-catalog.js`, `welcome.js`, `styleguide.js`, `static/css/motion.css`, `chrome.css`, `static/js/sw.js`, `docs/MASCOT_MOTION_AND_ONBOARDING.md` (E7), `docs/ANIMATION_ONBOARDING.md` (E6), `docs/SECURITY_AND_GDPR.md`, `docs/DPIA.md`, `docs/AI_HANDOFF.md`, and every smoke test that pins the mascot.
**Owner of decisions:** David. **Builder:** any agent. One phase per commit. David confirms each phase before the next one starts. Commit and push only when David explicitly asks.
**Read first:** `docs/AI_HANDOFF.md` §3 rule 17 (`AI_HANDOFF.md:88`), `docs/MASCOT_MOTION_AND_ONBOARDING.md` §2 (E7 decisions; all still stand), `docs/SECURITY_AND_GDPR.md` §6.1 (`:346-351`), the DPIA nudge row (`docs/DPIA.md:48`, `:70`).
**Epic id:** E8. Checked: no `E8` exists anywhere in `docs/`, `app.py`, `static/js/` or `scripts/`. The ids in use are E1–E7 plus the G8/ES tracks, which use different prefixes.

---

## 0. What we are building, in one paragraph

Zorp stays the same hand-drawn inline SVG character: the same blob, face plate, antennae and colours. What changes is that the face stops being seven hard-coded drawings and becomes a set of parts that can be combined. There are separate channels for **eyes, brows, mouth, cheeks and effects**, drawn once in a shared parts library. Named **presets** combine them: several kinds of smile, a closed-eyes "^^" smile, rosy cheeks, bashful blush with a sweat drop, "aww" goo-goo eyes, wow, dizzy, sleepy, sparkle and love eyes, and more. The body gets **views** (front, ¾, side profile at 90°, back, back-glance) with a "pinch-turn" between them. It also gets a **pose library** (fist-pump jump, victory jump, flex, shrug, bow, think-with-chin-hand, dance, sit, float…), all driven by data tables. A small **choreography layer** in `zorp-motion.js` chains poses, expressions and effects with anticipation, squash-and-stretch and follow-through. Every existing clip, face name, API call and smoke keeps working. Every new clip has a reduced-motion variant and a `data-motion="off"` variant. A safeguarding table decides which expressions may appear at which app moments, and a smoke enforces it, so no sad face is ever used to pressure a pupil. Each phase ends with a `/styleguide#zorp-gallery` update and a screenshot contact sheet David can check on his phone. No libraries, no Lottie, no CDN, no new personal data.

---

## 1. Where Zorp is today, and the gaps

### 1.1 What exists (verified)

| Thing | Where | State |
|---|---|---|
| Live rig, one inline 64×64 SVG | `templates/partials/buddy.html:25-174` | The `<svg>` opens at `:27`. It contains `buddy-root` (`:28`), `buddy-shadow` (`:29-31`), `buddy-arm--l/--r` single-stroke paths behind the body (`:33-38`), and `buddy-head` (`:39`) holding the antennae (`:41-48`), body plus highlight (`:50-53`), face plate (`:55`), **7 hand-drawn face groups** (`:57-163`) and the hat overlay (`:163`). Feet are outside the head (`:166-171`). |
| Faces | same file | `nudge` (`:57-73`, with the `data-mouth` smile/grin/cat swap at `:70-72`), `milestone` (`:74-90`, gold stars), `celebrate` (`:91-101`, closed "^^" eyes plus cheeks at `:99-100`), `qotd-nudge` (`:102-117`, one brow at `:103`, "o" mouth), `streak-risk` (`:118-134`, **a frown** at `:131` plus a flame), `weak-topic` (`:135-151`, brows at `:136-137`, flat mouth), `friend-challenge` (`:152-162`, one closed eye). Brows already exist informally in two faces. |
| Face switching | `static/css/chrome.css:767-777` | `.buddy-face{display:none}` plus eight `.study-buddy-face[data-face=…]` show-rules. All seven faces are in the DOM of every instance. |
| Look / cosmetics | `buddy.html:27`, `motion.css:59-70`, `models/zorp_kit.py:60-90`, `partials/zorp_overlays.html` | `data-zorp-colour/antenna/feet`, `data-mouth` (resting face only), hats and shoes anchored at (32, 14.5) and (24/40, 56.5). |
| Runtime `window.pbZorp` | `static/js/zorp-motion.js` (26,602 B, 735 lines) | `CLIP_NAMES` (`:7`), `FACES` allowlist (`:8`), E6 `GESTURES` (`:9`), react tables (`:13-26`, with `wrong → weak_topic` face at `:23`), JS-created thought bubble (`:28-33`, `:171-208`), `motionLevel()` reading `data-motion` (`:41-49`), `visiblePupils` keyed by face class (`:106-109`), `setFace`/`tempFace` (`:111-135`), clips table (`:259-536`), and `play()` with a reduced branch that does face swap plus colour pulse only (`:538-599`, `:573-587`). `react()` bails when motion is `off` (`:643`) and has cooldowns and a rare-protect window (`:641-681`). Idle blink (`:695-718`). Export (`:726-734`). |
| `sleep` face | `zorp-motion.js:512-535` | A hack. `data-face="sleep"` matches no show-rule, so **no face is drawn at all** (a blank plate). `templates/offline.html` sets it in markup. |
| CSS | `static/css/motion.css` (4,844 B; cap 8,000 at `test_zorp_motion_smoke.py:33`) | Pivots (`:4-18`), CSS idle (`:19-31`), reduced and `data-motion` mirrors (`:36-53`), cosmetics (`:59-70`). E6 gestures and `.buddy-head/.buddy-eye` pivots live in `chrome.css:761-766` and `:1338-1380`. The `.buddy-mascot` has `filter: drop-shadow` (`chrome.css:759`). |
| Consumers | `celebrate.js:19-30` (`reactMascot`), `:170`, `:177`; `study-buddy.js:44-61` (its own `FACE_OK` plus emoji map), `:71-83`, `:339-341`; `guide.js:35-36` (`LEGACY_GESTURES`/`ZORP_GESTURES`), `:310-323` (its own face allowlist), `:366-374`; `guide-catalog.js` (`face:`/`gesture:` per step); `welcome.js:39-55`, `:77`; `zorp-triggers.js:34-47` (`data-zorp-autoplay`) | Face names are allowlisted in **three** separate places (`zorp-motion.js:8`, `study-buddy.js:44-52`, `guide.js:311-319`). |
| Instances per page | `base.html:257` (PWA banner, every page including anonymous), `:242` via `partials/guide.html:6` (authenticated), `:289` (corner buddy) | Plus empty states, the streak-ring peek, `/welcome` hero, `/offline`, `/styleguide`, `/guide-preview`. |
| Static pose kit | `models/zorp_kit.py:15-32` (viewBox 80×80, 11 tokens), `partials/zorp_kit.html:15-31` (same art offset by +8,+8) | Separate drawing. `test_zorp_kit_smoke.py` pins the tokens, the markup and the headwear byte-for-byte (`:57-117`, `:182-264`). |
| Dev preview | `/styleguide` (`app.py:5485-5494`), `/guide-preview`; gate `_guide_preview_enabled()` (`app.py:5474-5483`) | `PB_STYLEGUIDE=1` or `PB_TESTING=1`; else localhost; else any host when `SITE_URL` is not `https://`. Styleguide sections: faces grid (`styleguide.html:115-126`), gestures, pose kit, Motion (`:157-199`). `styleguide.js?v=4` (`:562`). |
| CSP | `app.py:1128-1131` | `script-src 'self' 'nonce-…'` (no `'unsafe-inline'`); `style-src 'self' 'unsafe-inline'`, so inline `style=""` attributes are allowed. JSON data islands are allowed and pinned by `test_csp_smoke.py`. |

### 1.2 Measured baseline (record these; the budgets below compare to them)

Measured by rendering `buddy_mascot()` through Jinja in memory, the same way as `test_default_render_has_no_look`:

| Measure | Today |
|---|---|
| One default instance | **7,249 B** (1,277 B gzip), **98 elements** |
| One instance with the fullest look (violet + short antenna + mortarboard + big feet + grin + sneakers) | 8,344 B (1,551 B gzip), 111 elements |
| Of which the 7 face groups | 5,463 B (75%) |
| 3 instances on an authenticated page | 21,747 B (1,425 B gzip; repeats compress well) |
| `motion.css` | 4,844 B / 8,000 cap |
| `zorp-motion.js` | 26,602 B (no cap) |
| CSS tree (`test_u8_a11y_smoke.py:61`, `:87`) | 232,501 / 240,000 total; **207,509 / 210,000 core (about 2.5 KB of headroom)** |
| Cache pins | `chrome.css?v=44`, `motion.css?v=3`, `zorp-motion.js?v=4`, `zorp-triggers.js?v=1`, `study-buddy.js?v=25`, `guide-catalog.js?v=10`, `guide.js?v=14`, `celebrate.js?v=10` (`base.html:30-69`), `welcome.js?v=2` (`welcome.html:115`), `styleguide.js?v=4`, `guide-preview.js?v=7`, `sw.js` `pb-v93` (`sw.js:2`) |

### 1.3 Gaps against David's wish list

| Wish | Gap today |
|---|---|
| "More expressive face": embarrassed cheeks, goo-goo eyes, rouge cheeks, closed-eyes smile, many smile types | 7 fixed faces. Only one closed-eye smile ("^^" in `celebrate`) and one cheek style. No blush, sweat, tears, sparkle or love eyes, wow, dizzy or laugh. A new face costs about 800 B in every instance on every page. The `sleep` face is blank. |
| Faces that combine | No channels. Mouth swaps work on `nudge` only (`motion.css:67-70`). |
| "From the side, turning 90 degrees" | Front view only. Nothing can mirror. Arms are always behind the body. No face-slide. |
| "Striking poses", "jumping with one fist in the air" | Arms are one curved stroke with no hand or elbow. Poses exist only inside clips as keyframes; there is no pose vocabulary, no hold, and no way to chain pose A → pose B. `cheer` raises both arms. There is no one-arm fist pump. |
| Dynamic feel | Clips are single keyframe lists. No shared anticipation or follow-through helpers. The arm pivots are bbox-relative (`motion.css:13-14`), so a new arm shape would move its own pivot. |
| One vocabulary everywhere | Face names are duplicated in three JS files. The static pose kit is a separate drawing and will drift from the live rig. |

---

## 2. Design decisions (confirmed 2026-09-29; frozen like E7 §2)

1. **Same character, more acting.** Silhouette, colours, face plate, antennae, feet and overlays stay as they are. E6 §2 #1 ("one mascot"), E7 §2 #1 and E7 §2 #13 (no second character; cosmetics automatic-only, no pupil-facing picker) all stand.
2. **Hand-built SVG + WAAPI/CSS only** (rule 17, `AI_HANDOFF.md:88`). Also banned for performance: animating path `d` (morphing), SMIL `<animate>`, animating `filter`, canvas. Only `transform` and `opacity` are animated. Expressions change by **swapping parts**, the way 2D cartoons do, with a tiny squeeze across the swap so it doesn't look like a hard cut.
3. **Faces are made from channels.** The channels are `eyeL`, `eyeR` (set together as `eyes`), `brows`, `mouth`, `cheeks`, `fx`. A **preset** is a named combination. The 7 legacy face names plus `sleep` stay valid forever as presets. `setFace(name)` keeps its signature and behaviour. The API emoji field (`models/buddy.py:32-40`) does not change.
4. **One source of truth for data and one for art.**
   - Data: `models/zorp_rig.py` holds the channel variants, presets, views, poses, the context map and valence classes. It ships to JS as a JSON data island `#pb-zorp-rig`.
   - Art: `templates/partials/zorp_parts.html` holds Jinja macros, one per part variant. The live rig, the client-side parts library and (Phase 6) the pose-kit faces all draw from it.
   - Choreography (clip timing) stays in `zorp-motion.js` and refers to poses and presets by name. A smoke checks that every name it references exists in `zorp_rig.py`.
5. **Motion-level matrix** (extends E7 §2 #3):

   | | `full` | `reduced` (OS or setting) | `off` |
   |---|---|---|---|
   | Expression set by content (Guide line, buddy prompt, server render) | animated swap (80 ms squeeze) | instant swap | instant swap. A face is content, not motion. |
   | FX (sparkles, sweat, tear shine, zzz, !, ?) | animated, ≤3 Hz twinkle | shown **static** for the clip's duration | not shown on reactions (react is already off); static in server stills |
   | View turns | pinch-turn (≈300 ms) | instant view swap **only** if the clip's meaning needs it (e.g. side-point); otherwise stays front | stays front |
   | Poses and clips | full | face swap + E7 colour pulse; no translation, no limb snaps | `react()` returns `false` (unchanged, `zorp-motion.js:643`); explicit `play()` does face swap only |
   | Idle life (blinks, glances, antenna twitch) | yes | none | none |

6. **Valence rules (safeguarding; §4 gives the full checklist).** Every preset is labelled `positive`, `neutral` or `negative`:
   - `negative` presets (`sad`, `aww-teary`, `worried`, `embarrassed`, `dizzy`) are **never** used for streak risk, dismissals ("Not now", Skip, close), idle or absence, leaving a page, notifications, or next to a call to action.
   - A clip may pass through a `negative`/`neutral` beat but must **end on a positive or neutral preset** within ≤1.2 s.
   - **Blush is only for Zorp's own bashfulness** (being thanked, his own slapstick). It is never shown in reaction to the pupil's wrong answer.
   - A smoke enforces all of this from `zorp_rig.CONTEXT_MAP`.
7. **Budgets are recorded, not guessed.** New caps live as named constants in the new `scripts/test_zorp_expression_smoke.py`. Each phase measures and records the real bytes in that constant's comment and in the §2.1 ledger. CSS budgets are raised **once**, in Phase 1, with a dated entry (the E7 §2 #11 discipline).
8. **Each phase is reviewable from a phone.** Each phase updates `/styleguide#zorp-gallery` and produces a contact sheet with `scripts/zorp_gallery_snapshot.py` (Playwright, dev-only, not a smoke). The implementer attaches the PNGs to the phase report.
9. **Back-compat is additive.**
   - These keep working: the existing clip names (`zorp-motion.js:7`), API names (`test_zorp_motion_smoke.py:40`), `data-face` values, E6 gesture keyframe names and `playGesture`/`LEGACY_GESTURES` (`test_guide_smoke.py:145-155`), `data-zorp-autoplay`, and `react()` kinds.
   - Tests change only deliberately, in the same commit, with the reason in the commit message.
10. **No new data, no new processors, nothing more visible to others.** Expressions and poses are presentation only. No pupil-facing picker (E7 §2 #13 still defers that).
11. **viewBox stays `0 0 64 64`** with `overflow: visible` (`motion.css:4`). All pivots, overlay anchors (`zorp_overlays.html` header) and sizes are in this frame. Raised fists and effects may go past the frame and are allowed to overflow. See D5.

### 2.1 Budget ledger (the implementer fills in "actual" per phase)

| Budget | Baseline | Cap from Phase 1 | Where it is pinned | Measured (Phase 0, 2026-09-29) | Measured (Phase 1, 2026-09-29) | Measured (Phase 2, 2026-09-29) |
|---|---|---|---|---|---|---|
| Default instance render | 7,249 B / 98 el. | **≤ 4,500 B, ≤ 70 elements** | `test_zorp_expression_smoke.py` `INSTANCE_DEFAULT_MAX_BYTES`, `INSTANCE_MAX_ELEMENTS` | `7,249 B / 98 el. (1,277 gzip)` | `2,454 B / 39 el. (671 gzip)`; heaviest preset (joy) 3,134 B | `2,493 B / 40 el. (676 gzip)`; heaviest preset (aww-teary) 3,494 B |
| Fullest-look instance | 8,344 B | ≤ 5,800 B | `INSTANCE_LOOK_MAX_BYTES` | `8,344 B / 111 el. (1,551 gzip)` | `3,624 B / 52 el. (960 gzip)` | `3,663 B / 53 el. (966 gzip)` |
| Parts library `<template>` (once per JS page) | n/a | ≤ 16,000 B | `PARTS_LIBRARY_MAX_BYTES` | `n/a` | `6,959 B` (49 parts) | `12,169 B` (70 parts) |
| Rig JSON island (once per JS page) | n/a | ≤ 6,000 B | `RIG_JSON_MAX_BYTES` | `n/a` | `1,359 B` with tags (19 presets) | `2,802 B` with tags (30 presets) |
| Mascot bytes on an authenticated page (3 instances + library + island) | 21,747 B | ≤ 36,000 B uncompressed, ≤ 6,000 B gzip | `PAGE_MASCOT_MAX_BYTES`, `PAGE_MASCOT_MAX_GZIP` (render `/` as a logged-in test user) | `21,747 B / 1,425 gzip (3 instances: PWA banner, Guide overlay, corner)` | `15,680 B / 2,525 gzip` | `22,450 B / 3,824 gzip` |
| `zorp-motion.js` | 26,602 B | ≤ 48,000 B | `RUNTIME_JS_MAX_BYTES` (new) | `26,602 B` | `32,353 B` | `35,308 B` |
| `motion.css` | 4,844 B | 8,000 → **12,000** | `test_zorp_motion_smoke.py:33` | `4,844 B` | `6,445 B` | `7,466 B` |
| CSS total / core | 232,501 / 207,509 | 240,000 → **246,000** / 210,000 → **216,000** | `test_u8_a11y_smoke.py:61`, `:87` (dated comment, same format as the E7 entries at `:26-60`) | `232,501 / 207,509` | `233,523 / 208,531` | `234,544 / 209,552` |

Phase 1 partly offsets its CSS: deleting the 8 face show-rules at `chrome.css:767-777` saves about 600 B.

---

## 3. Art direction

### 3.1 Style rules (so new art matches the old)

- **Strokes:** ink `var(--ink-800)`, stroke width 1.6–2.1 in the 64 frame (the existing faces use 1.6–2.1), round caps and joins.
- **Highlights:** white `#fff`, top-right. One highlight on the default eyes; two ("double catch-light") on the goo-goo and aww eyes.
- **Colours:** new mascot-scoped custom properties in `motion.css`, each falling back to existing tokens, following the `--zorp-body` pattern at `motion.css:59`.
  - `--zorp-rouge: var(--streak-300)` for happy cheeks. This is the existing celebrate cheek colour (`buddy.html:99`).
  - `--zorp-blush: var(--streak-400)` for embarrassed hatching.
  - `--zorp-drop: var(--brand-400)` for sweat and tear drops.
  - **Never use `--wrong-*` or `--correct-*` in the face.** Red reads as "you were wrong", and those tokens carry grading meaning.
  - Never redefine `--brand-*` (pinned at `test_zorp_motion_smoke.py:217-232`).
- **Readability at 56 px.** Every expression must read in the corner (56 px, `chrome.css:755-760`) and the 72 px guide tour size (`chrome.css:1303-1306`). The gallery shows both sizes and the 128/160 px hero sizes.
- **Dark mode.** The gallery renders every expression in light and dark themes. The face plate is `--brand-50`, so check contrast against the dark page.
- **Effects are small.** No single effect may cover more than about 15% of the mascot's box. No full-mascot flashes.

### 3.2 Eyes, the main channel

Each eye is a separate part, drawn centred at its own (0,0) and placed by a positioning group at L (26.2, 35.2) and R (37.8, 35.2). That allows winks, asymmetric looks and side-view single eyes. The pupil group keeps the class `buddy-pupil`, so blink, the think glance and the point glance keep working. The eye group keeps `buddy-eye--l/--r`, so the E6 wink keyframe still works (`chrome.css:1339-1341`).

| Variant id | Look | Notes |
|---|---|---|
| `open` | current dark ellipse (rx 2.6, ry 3.2) + one highlight | default, matches `nudge` |
| `open-big` | rx 3.1, ry 3.6 + one highlight | today's `streak_risk` eyes |
| `goo` | rx 3.3, ry 3.8, two highlights (big top-right, small bottom-left) | the "goo-goo / puppy" eye |
| `goo-shine` | `goo` + a curved lower-lid tear-shine line in `--zorp-drop` | aww/teary; **not** a falling tear |
| `happy-arc` | "^" arc (today's celebrate eye) | closed-eye happy "^^" |
| `smile-arc` | "‿" downward arc | content, closed-eye smile |
| `laugh` | ">" / "<" squeezed chevrons (the right eye is mirrored) | laughing |
| `wink-line` | short flat line with a slight curve | one side of a wink |
| `half` | ellipse with its top third cut by a lid line | sleepy, smug |
| `closed` | gentle "‿" with lashes | sleep |
| `wide` | rx 2.2, ry 2.8 dark + a white ring stroke around it | surprise, wow (smaller pupil = startled) |
| `squint` | flattened ellipse (ry 1.6) under a straight lid line | thinking, determined |
| `sparkle` | `open-big` with a 4-point star highlight | proud, excited |
| `heart` | small heart shape in ink with a highlight | loves learning (lesson complete) |
| `spiral` | small spiral stroke | dizzy "oops" (Zorp's own slapstick only) |
| `look-up` / `look-side` | `open` with pupil offset (−1.2 y / ±1.2 x) | thinking or glancing; could also be done at runtime with the `buddy-pupil` translate |
| `side` | narrower ellipse rx 2.2 for profile | side view only |

### 3.3 Brows (decision D2: recommended yes)

These are small floating strokes 5 px above each eye, with no forehead. The resting face has **no brows**, so default Zorp looks the same as today. Brows add most of the emotional range: the same eyes read as happy, worried or determined depending on the brow. They already exist informally in `qotd_nudge` (`buddy.html:103`) and `weak_topic` (`:136-137`).

| Variant | Shape | Used by |
|---|---|---|
| `none` | n/a | default |
| `soft` | gentle arcs | calm, content |
| `raised` | high arcs | surprise, curious, heads-up |
| `worried` | inner ends up, the "puppy" tilt | aww, sympathy, embarrassed |
| `determined` | inner ends slightly down, **never steep** | you-got-this, fist pump. Must not read as angry. |
| `skeptical` | one raised, one flat | today's `weak_topic`, confused |
| `knit` | both slightly lowered and close together | thinking hard |

### 3.4 Mouths

The anchor is (32, 44). The existing smile, grin and cat paths become variants `smile`, `grin` and `cat`, so `data-mouth` keeps working.

| Variant | Look | Mood |
|---|---|---|
| `smile` | current soft arc | default |
| `smile-wide` | wider, deeper arc (milestone mouth `:87`) | pleased |
| `grin` | big open D, filled ink (existing `:71`) | big happy |
| `grin-tongue` | open D with a small tongue in `--zorp-rouge` | excited, laughing |
| `laugh` | wide open D, tongue, tilted up | laughing |
| `cat` | ":3" (existing `:72`) | playful, cheeky |
| `smirk` | lopsided arc, one corner up | smug-friendly, side smile |
| `tiny` | short small arc | shy, bashful |
| `o` | small circle (existing qotd `:116`) | curious, "ooh" |
| `wow` | larger oval, filled | surprised |
| `flat` | straight line (existing weak-topic `:150`) | thinking, neutral |
| `wavy` | small zigzag "~" | oops, awkward, embarrassed |
| `wobble-smile` | smile with a small wobble | touched, aww (goo-goo pairing) |
| `frown-soft` | shallow downturn (today's streak-risk mouth `:131`) | **negative**; only for the `sad` preset (see §3.7) |
| `sleepy` | small open "o", drooping | sleep |
| `blep` | closed smile + a tongue tip | playful |
| `side-smile` / `side-o` | profile variants | side view |

### 3.5 Cheeks

| Variant | Look | Mood |
|---|---|---|
| `none` | n/a | default |
| `rosy` | soft circles r 2.1 at (21.5, 41) and (42.5, 41), `--zorp-rouge` (today's celebrate) | happy rouge |
| `glow` | larger faint ellipses, opacity 0.45 | proud, love |
| `blush` | three short diagonal hatch strokes "///" per cheek in `--zorp-blush` | embarrassed or bashful (Zorp's own) |

### 3.6 Effects layer (`fx`)

There are two layers:
- **Face-attached effects** move with the face across views: `sweat` (drop at the upper-right temple), `tear-shine` (glint under the eye), `blush-steam` (three tiny puffs, bashful).
- **Ambient effects** sit on a top layer that is **never mirrored**, so "?", "!" and "z" never flip: `sparkles` (2–3 four-point stars), `stars` (today's gold milestone stars `buddy.html:88-89`), `hearts` (2 tiny hearts, love-learning), `exclaim` ("!"), `question` ("?"), `zzz`, `dizzy-orbit` (3 small stars circling the head), `notes` (music notes for dance), `bulb` (idea lightbulb for "got it"), `flame` (today's streak flame `:132-133`, kept for the heads-up preset), `thought` (today's JS-created dots `zorp-motion.js:28-33`, moved here as a normal fx part).

Full motion animates these (twinkle ≤3 Hz, drop slide, zzz float). Reduced motion shows them static. Every fx keyframe gets a reduced mirror (pinned by `test_zorp_motion_smoke.py:86-104`).

### 3.7 Expression presets (vocabulary, valence, where each is used)

Legacy names are kept exactly. Valence: **+** positive, **0** neutral, **−** negative (restricted; see §2 #6 and §4).

| Preset | eyes / brows / mouth / cheeks / fx | Val. | App moment (and forbidden uses) |
|---|---|---|---|
| `nudge` (legacy) | open / none / smile / none / none | 0 | resting default everywhere |
| `milestone` (legacy) | open(-35) / none / smile-wide / none / stars | + | milestone reward |
| `celebrate` (legacy) | happy-arc / none / smile-wide / rosy / none | + | buddy `celebrate` prompt, cheer |
| `qotd_nudge` (legacy) | open / raised(L) / o / none / none | 0 | question of the day, curious |
| `streak_risk` (legacy name) | **changes to** open-big / raised / smile / none / flame (see D4) | + | streak reminder as upbeat "heads-up". **Never a frown or sad eyes.** |
| `weak_topic` (legacy) | open / skeptical / flat / none / none | 0 | buddy weak-topic prompt, think clip |
| `friend_challenge` (legacy) | wink-line(L)+open(R) / none / smirk / none / none | + | friend challenge |
| `sleep` (legacy, now drawn) | closed / none / sleepy / none / zzz | 0 | `/offline`, sleep clip |
| `soft-smile` | open / soft / smile / none | + | calm acknowledgement, "Not now" (if any reaction) |
| `grin` | open-big / none / grin / none | + | correct answer |
| `happy` (closed-eyes smile) | smile-arc / soft / smile-wide / rosy | + | lesson complete, welcome done |
| `joy` ("^^") | happy-arc / raised / grin-tongue / rosy / sparkles | + | streak, first correct |
| `laugh` | laugh / raised / laugh / rosy | + | dance clip, rare correct variant |
| `smug` (side smile) | half / skeptical / smirk / none | + | "nailed it" variant, friend challenge |
| `proud` | sparkle / soft / smile-wide / glow / sparkles | + | milestone, badge |
| `love` | heart / soft / smile-wide / glow / hearts | + | lesson complete (loves learning). No romantic contexts. |
| `wow` | wide / raised / wow / none / exclaim | + | big milestone reveal, first correct |
| `curious` | open / raised / o / none / question | 0 | tours, "what's this?" |
| `thinking` | look-up / knit / flat / none / thought | 0 | empty states, think-chin |
| `determined` | squint / determined / smile / none | + | "you've got this" (after a wrong answer), fist-pump windup |
| `confused` | look-side / skeptical / wavy / none / question | 0 | Zorp's own confusion (lore, "hmm, where did my hat go"). **Not** in reaction to pupil answers. |
| `oops` | wide / worried / wavy / none / none | 0 | the **first beat** of the wrong-answer clip (≤300 ms), then `determined` or `soft-smile` |
| `bashful` | smile-arc / worried / tiny / blush / blush-steam | + | Zorp being thanked or praised (Guide lines), end of dance trip |
| `embarrassed` | half / worried / wavy / blush / sweat | − | Zorp's **own** slapstick only (trips in dance, caught peeking). Never for a pupil's mistake. |
| `aww` (goo-goo) | goo / worried / wobble-smile / glow | + | touched or grateful: welcome finished, milestone "aww, look at you!" It has a smile, so it is not sad. |
| `aww-teary` | goo-shine / worried / wobble-smile / rosy | − | happy tears on rare big moments (100-day milestone). Restricted list. |
| `sad` (sad goo-goo eyes) | goo-shine / worried / frown-soft / none | − | **Guide lore only** (e.g. "I miss Novara sometimes…"), and the same step must resolve to a positive preset. Never in reactions, prompts, streaks or dismissals. |
| `dizzy` | spiral / none / wavy / none / dizzy-orbit | − | Zorp's own slapstick (a spin that goes too far), resolves to `laugh` |
| `sleepy` | half / none / sleepy / none | 0 | late idle (optional §6). Never used as "come back". |
| `wink` | open(L)+wink-line(R) / soft / smirk | + | Guide wink gesture, playful tips |
| `heads-up` | = new `streak_risk` art | + | reminder surfaces |

Why "sad goo-goo eyes" is split into `aww` and `sad`: David asked for "sad cute goo-goo eyes". The **cute goo-goo eyes** (`goo`, double highlights, worried brows) are the appealing part. Paired with a wobbly **smile** they read as "aww / touched", which is safe to use widely. Paired with a **frown** they are the classic "please don't leave" guilt trigger (Children's Code std 13, nudge techniques; `SECURITY_AND_GDPR.md:235`). So `sad` exists and appears in the gallery and in lore, but the context map cannot place it anywhere a pupil is making a choice.

### 3.8 Views and the 90° turn

**Views:** `front`, `three-quarter`, `side`, `back`, `back-glance`. **Facing:** `r` or `l`.

**How it works** (no 3D, no morphing):
1. **A mirror wrapper, `g.zorp-flip`,** sits inside `buddy-root`. Its transform is `scaleX(±1)` around x = 32. It handles facing left or right, so there is only one set of side art. Ambient "?", "!" and "z" live outside it and never mirror.
2. **The face slides.** Each view is a row in `VIEWS`: a per-part transform plus visibility for face plate, eyeL, eyeR, brows, mouth, cheeks, face-fx, antennae, body highlight, feet and arms. Values for facing right:
   - **¾:** plate `translate(3.5px,0) scaleX(.85)`; far eye (L) `translate(4.5px,0) scale(.82,1)`; near eye `translate(3px,0)`; mouth `translate(3.5px,0) scaleX(.85)`; far antenna `translate(4px,0)`; highlight `translate(-2px,0)`; far foot `translate(3px,-.5px)`.
   - **side:** plate `translate(8px,0) scaleX(.5)`; far eye hidden; near eye `translate(6.5px,0)` using the `side` variant; mouth swaps to `side-smile`/`side-o` at `translate(9px,0)`; both antennae shift +3/+6 px; feet overlap (+4/−2 px); far arm hidden; near arm moves to the front layer.
   - **back:** plate and face parts at opacity 0; highlight mirrored to the other side; both antennae visible.
   - **back-glance:** back plus plate `translate(-12px,0) scaleX(.35)` with one near-edge eye (an over-the-shoulder look).
   Parts are **moved and swapped, not squashed.** Scaling the whole face would pinch the eyes to slivers.
3. **Layer pairs.** SVG has no z-index; paint order is DOM order. Each arm therefore exists twice: `buddy-arm--r` behind the body (current position) and `buddy-arm--r-front` painted after the feet. The view table sets which of the pair is visible. Clips animate both members of a pair with the same keyframes, so switching layers mid-turn does not pop. The antennae stay behind the body in every view (already true: `buddy.html:41-48` comes before the body at `:50`).
4. **The pinch-turn clip (`turn`).**
   - 0–15%: anticipation dip (`root` scale 1.04,0.96).
   - 15–45%: `zorp-flip` `scaleX(1 → 0.15)` with the face parts easing toward the new side.
   - 50%: the runtime commits the new `VIEWS` row and, if facing changes, flips the sign.
   - 55–100%: `scaleX(0.15 → 1.04 → 1)` (overshoot).
   - Antennae lag by about 60 ms and overshoot 6°. The face-fx layer follows the face. Total about 300 ms.
   - Reduced motion: instant commit, and only if needed. Off: stays front.
5. **Resting state vs clips.**
   - The current view and pose are the **resting state**, written to inline `style.transform` on each part through `Animation.commitStyles()`. CSP allows inline style (`app.py:1131`).
   - One-shot clips run with WAAPI `composite: 'add'`, on top of the resting state, so a wave in side view waves from the side.
   - Feature-detect `composite`. Without it, clips replace the resting state as they do today, and the only cost is a snap back to front view.

### 3.9 Pose vocabulary

Poses are rows in `POSES`: a transform per part (root, head, armL/R with an arm-shape variant, footL/R, flip), plus an optional default view and preset.

| Pose | Key shape | Arm shape |
|---|---|---|
| `stand` | today's resting silhouette | `rest` |
| `wave` | R arm up, forearm oscillates (clip) | `straight` |
| `point` (left/right/down) | arm extended toward the target; head follows | `straight` |
| `fist-up` | R arm straight up (−165°), L arm tucked, body leans 4° toward the raised side | R `fist`, L `rest` |
| `victory` | both arms up in a V (±140°) | `fist` ×2 |
| `flex` | R arm bent, fist above shoulder, chest out (root scaleY 1.03) | R `bent-fist` |
| `think-chin` | R forearm to the chin, head tilt −6°, eyes `look-up` | R `bent` |
| `shrug` | both arms out low (±60°), head tilt, root scaleY 0.96 | `straight` |
| `bow` | side view, root rotate 18° forward about the feet, arms down | `rest` |
| `peek` | today's clip, now also a held pose (root offset) | `rest` |
| `crouch` | anticipation: root scale(1.08,0.9), arms back | `rest` |
| `dance-a` / `dance-b` | alternating: one foot lifted −3 px, body tilt ±6°, opposite arm up | `straight` |
| `sit` | root translateY 3, feet forward (side view looks best), body squash 0.95 | `rest` |
| `float` | feet dangle (rotate ±8°), shadow 0.7, root −6 px | `rest` |
| `sleep` | head droop 12° (today's clip), body low | `rest` |

**Arm shapes** are new parts, each drawn from the shoulder at (0,0), so a shape swap never moves the pivot:
- `rest`: today's curve (`buddy.html:34`).
- `straight`: a 9 px line plus a hand nub (r 1.9).
- `fist`: `straight` with a nub of r 2.4.
- `bent`: an elbow polyline with a nub.
- `bent-fist`: `bent` with the bigger nub.

The nubs use `--zorp-limb`. They are the "fist" in "fist in the air".

**Pivot fix.** Today the arm pivot comes from the bbox (`motion.css:13-14`, `transform-box: fill-box`). New structure: `<g transform="translate(15.6 40)"><g class="buddy-arm buddy-arm--l">[part]</g></g>` with `transform-box: view-box; transform-origin: 0 0`. That is the SVG-native pivot at the translated local origin. The shoulder point is exactly where the current `fill-box 100% 0%` puts it, so all existing arm clip angles look the same.

### 3.10 Animation principles adopted (and written into the runtime as helpers)

- **Anticipation.** Every jump starts from `crouch` (80–120 ms). Every turn starts with a dip.
- **Squash and stretch, keeping volume.** sx × sy ≈ 1. Maximum 12% deformation at 56 px and 16% at hero sizes (`STRETCH_MAX` in the rig table). Stretch on take-off (0.94, 1.08), squash on landing (1.1, 0.9), settle with overshoot.
- **Slow in, slow out.** A named easing table replaces ad-hoc strings:
  - `EASE.out = cubic-bezier(.2,.8,.2,1)`
  - `EASE.in = cubic-bezier(.6,0,.9,.4)`
  - `EASE.overshoot = cubic-bezier(.34,1.56,.64,1)`
  - `EASE.anticipate = cubic-bezier(.36,0,.66,-.56)`
- **Follow-through and overlap.** Antennae lag the root by 60–100 ms and overshoot. The head lags the body by about 40 ms. Arms settle one beat after landing.
- **Holds.** A key pose holds for at least 250 ms so it reads at 56 px. The fist-pump apex holds for 180 ms.
- **Arcs.** Jumps pair translateY with a tiny translateX (±1 px) and rotation so they don't move in a straight line.
- **Silhouette test.** Every pose must read as a filled black silhouette at 56 px. The gallery has a "silhouette" toggle: `filter: brightness(0)` on the demo only.
- **Less is more.** At most one fx family per beat and at most one clip at a time. Idle micro-actions no more than once every 6 s.

### 3.11 Signature clips (new)

| Clip | Beats (pose + preset) | Duration | Reduced |
|---|---|---|---|
| `fist-pump` | crouch+determined (100) → fist-up jump −10 px + joy + sparkles (260, hold 180) → land squash (120) → stand+grin (200) | ≈860 ms | preset `joy` + static sparkles + colour pulse |
| `victory` | crouch → victory jump −12 + wow→joy + stars → land → stand+happy | ≈950 ms | `joy` + pulse |
| `flex` | stand → flex + proud + sparkles (hold 350) → stand | ≈800 ms | `proud` |
| `shrug` | shrug + confused/soft-smile → stand | ≈700 ms | `soft-smile` |
| `bow` | turn side → bow + bashful → stand, turn front | ≈1,100 ms | `bashful` |
| `think-chin` | think-chin + thinking (+thought fx) hold → stand | ≈1,000 ms | `thinking` |
| `dance` | dance-a/b ×2 + laugh + notes → optional 10% "trip": embarrassed → laugh → stand | ≈1,400 ms | `laugh` |
| `turn` | see §3.8 | ≈300 ms | instant or none |
| `side-point` | turn side → point + curious → turn front | ≈1,100 ms | `curious` (view swap allowed) |
| `float` | float bob loop ×2 + happy | ≈1,200 ms | `happy` |
| `oops-encourage` (wrong) | oops (250) → small hop back + determined (350) → soft-smile, plus thought fx | ≈900 ms | `determined`, no thought bubble (as today, `zorp-motion.js:574`) |

All existing clips (`cheer`, `wobble`, `think`, `wave`, `point`, `hop`, `peek`, `sleep`, `blink`, `idle`, `nod/wink/tap/shake`) keep their names. Phase 4 may re-author `cheer` and `hop` onto the beat engine, but their names, durations (±100 ms) and reduced behaviour stay.

---

## 4. Architecture

### 4.1 Rig v2 (`templates/partials/buddy.html`)

```
svg.buddy-mascot  viewBox 0 0 64 64  (open tag byte-identical for the default render, test_zorp_motion_smoke.py:268-290)
└ g.buddy-root                          squash/stretch/jump; CSS idle breathe (unchanged)
  ├ g.buddy-shadow
  ├ g.zorp-flip                          NEW facing mirror + turn pinch (origin x=32)
  │  ├ g[translate(15.6 40)] > g.buddy-arm--l      back-layer arm (pivot group) > [arm part]
  │  ├ g[translate(48.4 40)] > g.buddy-arm--r
  │  ├ g.buddy-head                      nod/shake/tilt (unchanged)
  │  │  ├ g.buddy-antenna--l/--r
  │  │  ├ g.buddy-body (+ g.zorp-highlight)
  │  │  ├ g.zorp-face                    NEW (replaces the 7 .buddy-face groups)
  │  │  │  ├ ellipse.zorp-plate
  │  │  │  ├ g.zorp-slot--cheeks
  │  │  │  ├ g[translate(26.2 35.2)] > g.buddy-eye.buddy-eye--l > g.buddy-pupil > [eye part]
  │  │  │  ├ g[translate(37.8 35.2)] > g.buddy-eye.buddy-eye--r > g.buddy-pupil > [eye part]
  │  │  │  ├ g.zorp-slot--brows  (l, r)
  │  │  │  ├ g.zorp-slot--mouth > [mouth part]
  │  │  │  └ g.zorp-slot--fx-face
  │  │  └ hat overlay (unchanged position: last in head)
  │  ├ g.buddy-foot--l / --r (+ shoes)
  │  └ g.buddy-arm--l-front / --r-front  NEW front layer, hidden in front view
  └ g.zorp-slot--fx                      NEW ambient fx, outside flip (never mirrored)
```

Order invariants that `test_rig_markup` (`test_zorp_motion_smoke.py:119-133`) relies on still hold: root < arm < head < foot, body inside head, feet after the head closes. Its `buddy-pupil` count (`:122`, currently 11) becomes 2 in the default render and is updated deliberately. The hat stays the last thing in the head, so `test_overlay_rig_wiring` (`:293-300`) holds. `test_live_overlay_matches_kit` (`test_zorp_kit_smoke.py:230-264`) anchors on `buddy-face--friend-challenge` and is re-anchored to `zorp-face`.

**Macro signature:** `buddy_mascot(look=none, face='nudge', pose=none, view=none)`.
- `face` is a preset name (legacy names included). Unknown values fall back to `nudge`, the same fail-closed style as `resolve_pose` (`zorp_kit.py:50-55`).
- `pose` and `view` render the resting state as inline `style="transform:…"` from the same tables JS uses.
- The macro also writes `data-expr="<preset>"` on the `<svg>` for debugging and CSS fx hooks. The host's `data-face` stays where templates put it, because `test_svg_kit_smoke.py:212-218` pins `data-face="sleep"` on `/offline`.

**Call sites** that must pass `face=`, because the server now draws only one face: `base.html:289` (from `buddy_prompt.type` through `zorp_rig.face_for_prompt`), `offline.html:16` (`sleep`), `styleguide.html:122` (the faces grid), and `welcome.html:25`. Sites that use the default `nudge` need no change.

### 4.2 How parts are swapped (decision D1: recommended option A)

**A. Parts library plus clone-into-slot (recommended).**
- The server draws only the current parts in each instance. That drops about 5.4 KB of hidden faces per instance.
- `templates/partials/zorp_library.html` renders every part variant once per page inside an inert HTML `<template id="pb-zorp-parts">` (`<svg><g data-part="eyes:goo">…</g>…</svg>`), next to `<script type="application/json" id="pb-zorp-rig">`. Both are included under the **same guard as `zorp-motion.js`** (`base.html:57`: `current_user.is_authenticated or guide_preview_mode or zorp_motion_demo`). Anonymous pages have no runtime, so they get server-rendered faces only.
- `setExpression` diffs channels and, for each changed slot, calls `replaceChildren(template.content.querySelector('[data-part="…"]').cloneNode(true))`. A `<template>` is not a script, so there is no CSP issue.
- Cloned nodes are real DOM, so WAAPI and CSS fx animations work on them. They would not work inside `<use>` shadow trees.

**B. `<use href>` sprite.** Smallest markup. But parts inside the shadow tree can't be animated individually, and styling cloned content varies by browser.

**C. Everything inline per instance.** Simplest, but about 20–25 KB per instance and ×3 per page. It breaks the budget and the node count on Chromebooks.

**If the per-page library ever becomes a problem:** move it to a cached, versioned route (e.g. `/zorp/parts.svg?v=N`, rendered from the same macros and fetched lazily by the runtime on the first swap). That is recorded as an §6 option, not built now.

### 4.3 Data (`models/zorp_rig.py`) and the JSON island

```python
CHANNELS = {'eyes': (...), 'brows': (...), 'mouth': (...), 'cheeks': (...), 'fx': (...), 'arm': (...)}
PRESETS  = {'nudge': {'eyes': 'open', 'brows': 'none', 'mouth': 'smile', 'cheeks': 'none', 'fx': 'none'}, ...}
LEGACY_FACES = ('nudge','milestone','celebrate','qotd_nudge','streak_risk','weak_topic','friend_challenge','sleep')
VALENCE  = {'sad': 'negative', 'aww': 'positive', ...}          # every preset classified
VIEWS    = {'front': {...}, 'three-quarter': {...}, 'side': {...}, 'back': {...}, 'back-glance': {...}}
POSES    = {'stand': {...}, 'fist-up': {...}, ...}
CONTEXT_MAP = {'react.correct': ('grin','joy','happy','smug'), 'react.wrong': ('oops','determined','soft-smile'),
               'prompt.streak_risk': ('heads-up',), 'guide.lore': (... 'sad' allowed ...), ...}
NEGATIVE_ALLOWED = {'guide.lore', 'clip.dance.trip', 'clip.dizzy', 'styleguide'}
BANNED_CONTEXTS_FOR_NEGATIVE = {'prompt.*', 'react.*', 'dismiss', 'idle', 'autoplay.*', 'notification'}
def resolve_preset(name) -> str        # unknown → 'nudge'
def face_for_prompt(buddy_type) -> str # models/buddy.py types → preset
def rig_json() -> str                  # compact json.dumps(separators=(',',':')) for the island
def validate()                         # used by the smoke: every preset part exists in zorp_parts.html, etc.
```

JS reads the island once, lazily on the first `bind()`. If the island is missing (e.g. a page that loaded the runtime without the include), the runtime falls back to a built-in table of the 8 legacy presets, so faces never break.

### 4.4 Runtime additions (`static/js/zorp-motion.js`; additive)

```js
pbZorp.setExpression(nameOrChannels, opts)   // preset name or {eyes, brows, mouth, cheeks, fx}; returns bool
pbZorp.setFace(name, opts)                   // unchanged signature → setExpression(legacy preset); FACES check widened to PRESETS
pbZorp.hasExpression(name)                   // lets study-buddy.js / guide.js drop their private allowlists
pbZorp.pose(name, opts)                      // animate to a resting pose (commitStyles); reduced/off: no-op or instant per §2 #5
pbZorp.turn(view, facing, opts)              // pinch-turn; reduced: instant only if opts.required
pbZorp.play(name, opts)                      // unchanged; new clip names; opts.speed (dev slow-mo, default 1)
pbZorp.expressions / .poses / .clips         // name lists for the gallery
```

- **Beat engine.** A clip is either a legacy `tracks()` function or a `beats` array: `[{pose, expr, fx, view, ms, ease, hold}]`. `compileBeats()` turns pose-to-pose into **one keyframe list per part** with computed offsets, so each part still gets exactly one `el.animate()` and `stop()`/`cancel()` work as today (`zorp-motion.js:137-156`). Expression, fx and view changes at beat boundaries are `setTimeout`s guarded by `inst.seq`, the same pattern as `tempFace` (`:120-135`), and are restored by `stop()`.
- **Blink and pupils.** `visiblePupils` (`:106-109`) becomes `svg.querySelectorAll('.zorp-face .buddy-pupil')`. Parts without pupils (arcs, closed) just don't blink.
- **Idle life (Phase 7).** Occasional glance (pupil translate), antenna twitch, and a rare ¾ look-around. Only when idle, visible (`rendered()`, `:608-610`) and at `full` motion. Pause on `visibilitychange` (existing) and when off-screen (IntersectionObserver).
- **Thought bubble.** It becomes the `thought` fx part. `showThought` (`:171-208`) keeps its name and behaviour, and the `buddy-thought` class stays out of `motion.css` (pinned at `test_zorp_motion_smoke.py:390-398`).

### 4.5 CSS vs JS responsibilities

- **CSS (`motion.css`):** pivots (`transform-box`/`transform-origin`) for new groups, the colour custom properties (`--zorp-rouge/--zorp-blush/--zorp-drop`), fx keyframes (twinkle, drop slide, zzz float, heart pop) with reduced and `data-motion` mirrors (`motion.css:36-53` pattern), and the gallery-only silhouette toggle. No per-preset or per-pose selectors (these would grow CSS with every expression).
- **JS:** everything that chooses: expressions, poses, views, clips, timing.
- **`chrome.css`:** loses the 8 face show-rules (`:767-777`). Keeps the E6 gesture keyframes (`:1338-1380`, pinned by the guide smoke) and the sizes.

### 4.6 One vocabulary for every consumer

| Consumer | Change |
|---|---|
| Corner buddy (`study-buddy.js:44-76`) | `resolveFace` → `pbZorp.hasExpression`. Keeps `FACE_OK` only as the no-runtime fallback. Server passes `face=` so first paint is right. |
| Guide (`guide.js:310-323`, `guide-catalog.js`) | Allowlist → `pbZorp.hasExpression`. The catalog may use any preset in `CONTEXT_MAP['guide.*']`. `ZORP_GESTURES` (`:36`) gains the new clip names (additive; `test_guide_smoke.py:151-155` only requires a superset). |
| Answers (`celebrate.js:19-30`) | **No change.** It keeps calling `react(kind)`. The mapping lives in the runtime's react tables (`zorp-motion.js:13-23`), which read `CONTEXT_MAP`. |
| Welcome (`welcome.js:39-55`) | hello: turn-in from side + wave; level: side-point down; topic: think-chin; card tap: `fist-pump` instead of `cheer` (`:77`). |
| Empty states / peek (`zorp-triggers.js`) | `data-zorp-autoplay` values may use new clips (think-chin, shrug). Decorative exclusion unchanged (`zorp-motion.js:622-624`). |
| Offline / PWA banner | Server-rendered presets (`sleep`, `nudge` → `wave` pose still). No runtime. |
| Static kit (`zorp_kit.html`) | Phase 6: faces drawn from `zorp_parts.html` macros inside `translate(8 8)`. Tokens and pixels unchanged. New `zorp_rig.still(pose, preset, size)` helper for future stills. |

### 4.7 Files touched overall (so cache bumps are predictable)

- **New:** `models/zorp_rig.py`, `templates/partials/zorp_parts.html`, `templates/partials/zorp_library.html`, `scripts/test_zorp_expression_smoke.py`, `scripts/zorp_gallery_snapshot.py` (dev tool).
- **Changed:** `templates/partials/buddy.html`, `templates/base.html`, `templates/offline.html`, `templates/welcome.html`, `templates/styleguide.html`, `templates/guide_preview.html`, `templates/partials/zorp_kit.html` (Phase 6), `static/js/zorp-motion.js`, `study-buddy.js`, `guide.js`, `guide-catalog.js`, `welcome.js`, `styleguide.js`, `guide-preview.js`, `static/css/motion.css`, `static/css/chrome.css`, `static/js/sw.js`, the smokes listed per phase, `docs/AI_HANDOFF.md`, `docs/DPIA.md`, this file, and `.gitignore` (snapshot output folder).

---

## 5. Safeguarding, accessibility and privacy checklist (every phase)

**Children's Code std 13 (nudge techniques).**
- `SECURITY_AND_GDPR.md:235` requires "no streak-loss shaming copy" and documenting buddy nudges against std 13. §6.1 Q4 (`:351`) requires revisiting the DPIA when a feature "profile[s], rank[s], or nudge[s]".
- Expressions reacting to pupil behaviour are nudge-adjacent, so Phase 0 records the gate answers and Phase 5 adds a dated `docs/DPIA.md` review-log row, in the style of the 2026-09-27 entry at `DPIA.md:110` ("fewer, not more, prompts").
- Rule: **an expression never asks for anything.** The mascot's face never changes in response to a pupil hesitating, dismissing, leaving or being away.

**No guilt faces.**
- `negative` presets are banned from `prompt.*`, `react.*`, `dismiss`, `idle`, `autoplay.*` and notifications.
- `streak_risk` moves from frown to upbeat `heads-up` (D4). The streak copy at `models/buddy.py:369` is unchanged by this epic.
- `test_zorp_expression_smoke.py::test_valence_context_rules` enforces this from `CONTEXT_MAP`. It also greps `celebrate.js`, `study-buddy.js`, `zorp-triggers.js` and all templates for negative preset names used as literals.

**Wrong answers are met with sympathy, not disappointment.** E7 §2 #5 stands: no head-shake. The clip is `oops` (≤300 ms, neutral) → `determined` or `soft-smile`, plus the thought bubble. No blush, no sweat, no sad eyes on a pupil's mistake. `test_react_wrong_resolves_positive` checks that the last beat of every react clip is positive or neutral.

**Embarrassment belongs to Zorp.** `embarrassed`, `bashful`, `dizzy` and `confused` appear only in Zorp's own slapstick or lore contexts, and when he is thanked.

**Emotional dependency.**
- No copy or animation implies Zorp is lonely, hurt or waiting for the pupil.
- `sad` appears only in Guide lore steps listed in `NEGATIVE_ALLOWED` and must resolve positively in the same step. The smoke checks each `guide-catalog.js` step with a negative `face` against the allowlist.

**Accessibility.**
- All mascots stay `aria-hidden` (pinned at `test_zorp_motion_smoke.py:131`). An expression never carries meaning that isn't also in text.
- No flashing above 3 Hz; sparkle twinkle ≤ 3 Hz, WCAG 2.3.1.
- No full-mascot flashes. FX stay within about 15% of the mascot box.
- `prefers-reduced-motion` and `data-motion` follow the §2 #5 matrix for every clip, pose, turn and fx.
- The corner face stays click-through (`chrome.css:750-752`).

**Privacy.**
- No new stored fields, no analytics, no processors.
- Nothing becomes more visible to others (S0.3, `SECURITY_AND_GDPR.md:129`).
- `public_profile.html` badges (kit stills) stay decorative.

**Security and CSP.**
- No inline scripts (`test_csp_smoke.py` scans every template). Only the JSON island is used.
- The parts library is a `<template>`. No `innerHTML` built from data; clone only.
- No CDN or animation library (`test_guide_smoke.py` bans lottie/jsdelivr; `test_zorp_motion_smoke.py:53`).

---

## 6. Phases

Every phase:
- is one commit, only when David explicitly asks;
- ends with `python scripts/run_smoke_tests.py` green;
- bumps `?v=` for every changed static file in `base.html` (or its template) and updates the pins that reference it;
- bumps `CACHE_VERSION` in `static/js/sw.js` by one, and updates `test_pwa_smoke.py:47` in the same commit (`test_welcome_smoke.py:151-155` cross-checks it);
- updates the §2.1 ledger with measured bytes;
- adds a line to `docs/AI_HANDOFF.md` §1/§9;
- produces a contact sheet (§6.9).

The `?v=` numbers below assume nothing else lands in between. Always bump from whatever the current number is. Estimates are agent time on the laptop.

### Phase 0: Spec freeze, feature gate, gallery skeleton, baseline shots (≈1 h)

- David confirms §2 and decisions D1–D5 (§7). Run `python scripts/ops_cadence.py feature-gate` and record the answers here. Expected: Q1 no, Q2 no, Q3 no, Q4 yes (reaction expressions), which triggers the std 13 note. Recorded in §7.1.
- `scripts/test_zorp_expression_smoke.py` skeleton:
  - ledger constants (§2.1) at their baseline values;
  - a `test_no_animation_libraries` re-check;
  - `test_instance_bytes_measured`, which prints the current default and full-look instance sizes and element count (non-failing in Phase 0).
- `scripts/zorp_gallery_snapshot.py` (dev tool, not matched by `run_smoke_tests.py`'s `test_*_smoke.py` glob):
  - Starts the app with `PB_TESTING=1` on a random localhost port (a `--serve` subprocess run by `--server-python`; see the script docstring) and opens `/styleguide#zorp-gallery` in headless Chromium.
  - Writes PNG sheets for faces, looks, clips filmstrips, light/dark, and 56/128 px. Filmstrips/looks from Phase 1.
  - Filmstrips pause every animation via `document.getAnimations()` and step `currentTime` through 0/25/50/75/100%.
  - Also captures the reduced-motion variant (`page.emulate_media(reduced_motion='reduce')`).
  - Output goes to `data/zorp_gallery/<label>/`; add `data/zorp_gallery/` to `.gitignore`.
  - Exits 0 with a message if Playwright or Pillow is missing. Neither is in `requirements.txt`, and they must not be added.
- `/styleguide` gets a `#zorp-gallery` section and a pill link next to "Zorp motion" (`styleguide.html:24`). At first it only shows today's 7 faces at 56 and 128 px. No static file changes.
- Run the snapshot tool with `--label baseline`. These are the "before" images for the Phase 1 parity check.
- **Cache/pins:** none (templates and scripts only).
- **Budget:** none.
- **Preview:** David opens `baseline/faces.png` on his phone.
- **Done when:** the gate is recorded, the baseline sheets exist, and the smokes are green.

### Phase 1: Expression engine, parts library, legacy parity, first 10 new faces (≈4–5 h). The biggest visible win.

**Files:**
- `models/zorp_rig.py` (channels, presets for all 8 legacy names plus `soft-smile`, `grin`, `happy`, `joy`, `laugh`, `smug`, `wow`, `aww`, `bashful`, `determined`; `face_for_prompt`; `rig_json`; `validate`).
- `templates/partials/zorp_parts.html` (eyes: open, open-big, goo, happy-arc, smile-arc, laugh, wink-line, wide, closed; brows: none, soft, raised, worried, determined, skeptical; mouths: smile, smile-wide, grin, grin-tongue, laugh, cat, smirk, tiny, o, wow, flat, wavy, wobble-smile, sleepy; cheeks: none, rosy, blush; fx: none, stars, flame, zzz, sparkles).
- `templates/partials/zorp_library.html`.
- `buddy.html`: replace the 7 face groups with the `zorp-face` slots; add `face=`; keep arms, feet and head as they are. Views, flip and front arms come in Phase 3.
- `base.html`: include the library and island under the `:57` guard; pass `face=` at `:289`.
- `offline.html`, `welcome.html`, `styleguide.html` (call sites).
- `zorp-motion.js`: `setExpression`, `hasExpression`, `expressions`; `setFace` → presets; `visiblePupils`; `sleep` clip uses the real preset.
- `study-buddy.js`, `guide.js` (allowlists → `hasExpression`, with local fallback).
- `motion.css` (colour properties; `.zorp-face` pivots; `zzz`/`sparkles` keyframes + reduced mirrors).
- `chrome.css` (delete `:767-777`).
- `styleguide.js` (expression picker: tap a preset, or pick channels from dropdowns; motion-level simulator buttons that set `html[data-motion]` on the dev page only; `speed` 0.25× toggle).

**Legacy parity:** the 7 legacy faces must look the same. Offsets like milestone's y 35 vs 35.2 are allowed dedicated part variants. The snapshot tool's `--compare baseline` does a Pillow pixel diff per face at 128 px, with a tolerance of ≤0.5% of pixels differing (anti-aliasing). `streak_risk` is exempt (D4 accepted, §7.1) and is shown side by side.

**Tests:**
- New in `test_zorp_expression_smoke.py`: `test_presets_complete` (every legacy name exists; every part referenced by a preset exists in `zorp_parts.html`; `validate()` passes), `test_default_render_budget` (≤4,500 B, ≤70 elements), `test_full_look_budget` (≤5,800 B), `test_library_and_island_budget` (≤16,000 / ≤6,000), `test_page_mascot_budget` (logged-in `/`: ≤36,000 B, ≤6,000 B gzip), `test_unknown_face_fails_closed`, `test_offline_sleep_draws_eyes` (the closed-eye part is present), `test_valence_classified` (every preset has a valence), `test_no_negative_in_prompt_faces` (first slice of the §5 rules), `test_runtime_js_budget` (≤48,000).
- Changed: `test_zorp_motion_smoke.py` `API_NAMES` gains `setExpression`/`hasExpression`; the pupil count at `:122` changes 11 → 2 with a comment; `motion.css` cap 8,000 → 12,000 at `:33`.
- Changed: `test_zorp_kit_smoke.py::test_live_mascot_unchanged` (`:92-117`): the face-name regex becomes `zorp_rig.LEGACY_FACES` order, and the separation asserts are kept. `::test_live_overlay_matches_kit` (`:230-264`) re-anchors to `zorp-face`.
- `test_buddy_smoke.py:119-120`, `:388` pins. `test_buddy_gate_smoke.py`: extend `scripts/buddy_gate_harness.js` stubs if `study-buddy.js` now calls `pbZorp.hasExpression`. `test_u8_a11y_smoke.py` budgets.

**Cache/pins:** `zorp-motion.js` v4→5, `motion.css` v3→4, `chrome.css` v44→45, `study-buddy.js` v25→26, `guide.js` v14→15, `styleguide.js` v4→5, `sw.js` pb-v93→pb-v94.

**Budget:** raise CSS to 246,000 / 216,000 with a dated entry that records measured totals. Record motion.css bytes, instance bytes, library bytes and page bytes in the ledger.

**Preview:**
- `data/zorp_gallery/phase1/faces-parity.png` (before/after grid) and `expressions.png` (all presets, 56 + 128 px, light + dark).
- On the laptop: `/styleguide#zorp-gallery`.
- On the phone: the PNGs, or the LAN option in §6.9.

**Done when:** legacy faces match the baseline, 10+ new expressions render at 56 px, `/offline` shows a real sleeping face, and the budget constants are measured and green.

**Phase 1 build notes (2026-09-29): deviations and choices, for the reviewer.**
- **Ambient fx only.** All Phase 1 fx (`stars`, `flame`, `zzz`, `sparkles`) sit in one ambient slot (`g.zorp-slot--fx`, last child of `buddy-root`, after the feet). The face-attached fx slot arrives with the Phase 2 fx that need it. The legacy stars and flame used to sit inside the head group, so they no longer tilt with a nod or shake; they are still moved by the root.
- **`data-expr` only off the default.** The macro writes `data-expr="<preset>"` for every face except `nudge`, because the default `<svg>` open tag must stay byte-identical (`test_default_render_has_no_look`). The runtime reads it as "what the server drew" when it binds and keeps it in step afterwards.
- **Look mouth.** The automatic look's `grin`/`cat` mouth replaces the mouth of the `nudge` face only, chosen server-side (`zorp_rig.parts_for`). The old `data-mouth` CSS rules are deleted; `data-mouth` stays on the `<svg>` and the runtime applies it whenever it draws `nudge`.
- **Extra part variants for exact parity.** Offsets from the seven drawings became dedicated variants: eyes `open-lift`, `open-off`, `curious`/`curious-r`, `low`/`low-r`; mouths `smile-w` (friend challenge) and `smile-big` (celebrate); brows `raised-l` (qotd). The plan's `smile-wide` for celebrate became `smile-big` for parity; `happy` uses `smile-wide`. `half` (eyes) was pulled forward from Phase 2 because `smug` needs it.
- **Presets pulled forward.** `heads-up` exists now, with the same art as `streak_risk` (D4). `wow`, `aww` and `bashful` ship without their Phase 2 fx and cheeks (`exclaim`, `glow`, `blush-steam`); `aww` uses `rosy` cheeks and `determined` uses `open` eyes (the `squint` part is Phase 2).
- **Right-eye siblings.** A variant named `x-r` is the right-eye twin of `x` (for `laugh`, `closed` and the asymmetric legacy eyes). Presets give one eye id and the right eye is derived.
- **Ink classes.** `.zk` (ink stroke, round caps) and `.zf` (ink fill) live in `motion.css` so the library stays small (6.9 KB against a 16 KB cap). The white highlights and the gold/streak fx keep explicit attributes.
- **Instant swaps.** Phase 1 swaps parts instantly; the 80 ms squeeze is Phase 2 (§6). `pivots` for `.zorp-face` are in `motion.css` ready for it.
- **`opts.speed`.** `play()` accepts a dev-only `speed` below 1 (the styleguide 0.25x toggle). Nothing in the app passes it.
- **`channelsOf(name)`.** Small extra API used by the styleguide picker to sync its menus.
- **Parity numbers.** The snapshot tool's `--compare` now searches small pixel shifts, because gallery cells move by a few pixels when the row has more cells. At 128 px all six non-exempt legacy faces differ by 0.00%. At 56 px five are 0.00% and `friend_challenge` is 1.96% (caption wrapping only; the mascot area is identical).
- **Preview files.** `data/zorp_gallery/phase1/`: `faces-parity.png`, `expressions.png`, `faces.png`, `faces-reduced.png`.
- **Review fixes (2026-09-29).** `setExpression({…})` is now all-or-nothing: any given channel whose id has no part (or no channel given at all) returns `false` and changes nothing. The `blush` cheek part no longer carries `.zk`, whose CSS stroke was overriding its blush colour (it painted ink); the smoke now rejects colour attributes on `.zk`/`.zf` elements. The styleguide `#sg-buddy-react` demo passes `face='celebrate'` to match its host. Ledger numbers above re-measured after these fixes.

### Phase 2: Full expression vocabulary, FX layer, eye life (≈3–4 h)

- Remaining parts and presets from §3.2–§3.7: `goo-shine`, `half`, `squint`, `sparkle`, `heart`, `spiral`, `look-up/side`, `knit` brows, `glow` cheeks, mouths `blep`, `frown-soft`; fx `sweat`, `tear-shine`, `blush-steam`, `hearts`, `exclaim`, `question`, `dizzy-orbit`, `notes`, `bulb`, `thought`.
- Presets: `happy`, `proud`, `love`, `curious`, `thinking`, `confused`, `oops`, `embarrassed`, `aww-teary`, `sad`, `dizzy`, `sleepy`, `wink`, `heads-up`.
- **Animated swaps:** eye swaps squeeze through (scaleY 1 → 0.2 → 1, 80 ms total). Mouth swaps pop (scale 0.9 → 1, 90 ms). Blush fades in at opacity (120 ms). Sweat drop slides 2 px. Tear-shine twinkles once. Reduced and off: instant (per §2 #5).
- Thought bubble becomes the `thought` fx (JS-created node retired; `showThought` keeps its name).
- **Files:** `zorp_parts.html`, `zorp_rig.py`, `zorp-motion.js`, `motion.css` (fx keyframes + mirrors), `styleguide.html`/`styleguide.js` (channel matrix view: eyes × mouths grid for quick review).
- **Tests:**
  - `test_fx_keyframes_have_reduced_mirrors` (reuses the `test_zorp_motion_smoke.py:86-104` approach).
  - `test_twinkle_rate` (every fx keyframe with opacity toggles has `duration / toggles ≥ 333 ms`).
  - `test_negative_presets_restricted` (full §5 rules, including the guide-catalog allowlist).
  - `test_blush_never_on_react` (no `blush`/`sweat` in any `react.*` context).
  - Budgets re-measured.
- **Cache/pins:** `zorp-motion.js` v5→6, `motion.css` v4→5, `styleguide.js` v5→6, `sw.js` →pb-v95.
- **Budget:** library likely ~12–14 KB (must be ≤16,000). motion.css ≤12,000. Record both.
- **Preview:** `phase2/expressions.png`, `phase2/matrix.png`, `phase2/fx-filmstrips.png` (full vs reduced side by side).
- **Done when:** every §3.7 preset is in the gallery at 56 px, fx behave per the matrix, and the valence tests pass.

**Phase 2 build notes (2026-09-29): deviations and choices, for the reviewer.**
- **Vocabulary.** Eyes `goo-shine`, `squint`, `sparkle`, `heart`, `spiral`, `look-up`, `look-side`; brows `knit`; cheeks `glow`; mouths `blep`, `frown-soft`; fx `sweat`, `tear-shine`, `blush-steam`, `hearts`, `exclaim`, `question`, `dizzy-orbit`, `notes`, `bulb`, `thought`. New presets `proud`, `love`, `curious`, `thinking`, `confused`, `oops`, `embarrassed`, `aww-teary`, `sad`, `dizzy`, `sleepy`, `wink` (30 presets in all, valence classified per §3.7: negative are `embarrassed`, `aww-teary`, `sad`, `dizzy`). `wow`, `aww`, `bashful`, `determined` gained their planned fx, cheeks and squint eyes. `notes` and `bulb` have art but no preset uses them yet (Phase 4 clips). `look-side`/`look-up` are parts, not runtime pupil offsets; the 90-degree side views stay Phase 3.
- **`sad` is cute, and boxed in.** Sad goo-goo eyes with a lower-lid line, worried brows, `frown-soft` mouth and two small tear-shine drops. It appears only in `CONTEXT_MAP['guide.lore']` (and the styleguide list). `aww-teary` only in `guide.reward.big`, `embarrassed` in `clip.dance.trip`, `dizzy` in `clip.dizzy`. `GUIDE_LORE_STEPS` is empty until Phase 5 writes lore copy. The plan's table gave `sad` no fx; it has `tear-shine` (David's "sad cute goo-goo eyes").
- **Face-attached fx.** `zorp-slot--fx-face` is inside `g.zorp-face` (so inside the head); `zorp_rig.FX_FACE` (`sweat`, `tear-shine`, `blush-steam`) picks it and is shipped in the island as `ff`. The runtime keeps one `fx` channel and routes it to one slot, clearing the other. Ambient fx stay outside the head.
- **Animated swaps.** Eye squeeze 80 ms, mouth pop 90 ms, blush and any cheek fade 120 ms, all WAAPI on the slot, only at `full` motion and only when the mascot is rendered; instant otherwise. Deviation: the squeeze runs on the new part (scaleY 0.2 to 1) instead of 1 to 0.2 to 1, because the DOM swap is synchronous (clips and `restoreFace` depend on that) and the plan's shape would show one full-size frame of the new eye first. Sweat slides 2 px and `?`/`!` pop once by CSS (keyframes `zorp-drop`, `zorp-pop`); tear-shine twinkles once (`zorp-twinkle` x1); hearts and blush steam and notes drift on `zorp-zzz`; dizzy stars circle on `zorp-orbit` (transform only).
- **Reduced mirrors by wildcard.** Every fx keyframe runs only under `prefers-reduced-motion: no-preference` and is switched off for `.buddy-mascot [class*="zorp-slot--fx"] *` in the reduced media block and in both `html[data-motion="reduced"]` and `"off"` mirrors. That replaced the per-class `.zorp-sp`/`.zorp-z` mirror lines.
- **`thought` is an fx part.** `showThought(inst)` draws the part into the ambient slot, animates it with WAAPI (as before, full motion only) and `clearThought` puts the current expression's fx back. The `buddy-thought` class no longer exists anywhere; `motion.css` has no thought rules; `THOUGHT_DOTS`/`createElementNS` are gone.
- **Review fixes from Phase 1.** (a) `pbZorp.valenceOf` and `allowedIn`; `study-buddy.js` refuses negative presets (island valence; its fallback table now maps names to valence); `guide.js` accepts a preset only through `allowedIn('guide' | 'guide.lore')`, and a lore step (`step.lore`) shows `step.resolve` on its last line. `CONTEXT_MAP`, `NEGATIVE_ALLOWED`, `BANNED_CONTEXTS_FOR_NEGATIVE`, `GUIDE_LORE_STEPS` are in `zorp_rig.py`; `validate()` and `test_negative_presets_restricted` enforce them (including every `guide-catalog.js` step). (b) `data-expr` is recomputed after every draw: the asked preset name when the channels match it, else the first matching preset, else `custom`. (c) `--compare` diffs only the mascot box and prints changed/total pixels per cell (below). (d) the keyframe-pairing test strips CSS comments and checks real rules. (e) `rig_json()` escapes `<`. (f) `determined` brows are a soft arch (peak 1.9 above the ends, inner end 0.5 lower) with wider `squint` eyes; `knit` is a softer arch too.
- **Contexts.** Blush and sweat never appear in `react.*` (`bashful` is not in any react context, even though §6 Phase 5 lists it for milestones; Phase 5 should use `aww` or `proud` there).
- **Matrix and gallery.** `/styleguide#zorp-gallery` (`data-gallery-phase="2"`) shows all 30 presets at 56 and 128 px plus an eyes x mouths matrix (17 x 16) built in the browser from the parts library (`MATRIX_EYES`, `MATRIX_MOUTHS` in `zorp_rig.py`). Review tool only: pairings such as `frown-soft` with any eye are not app faces.
- **Snapshot tool.** Adds `matrix.png`, `matrix-dark.png`, `fx-filmstrips.png` (0/25/50/75/100% frames beside the reduced still) and mascot boxes in `manifest.json`. `--compare baseline` (the pre-E8 look, kept) aligns both cells on the drawn mascot's own bounding box, allows a 3 px shift, and reports per-cell changed pixels; the OVER limit is 0.15% of the mascot area (was 0.5% of the whole cell). Result: all 64 legacy cells within the limit; `streak_risk` (D4) and `sleep` are the exempt ones. The baseline folder holds whole cells only, so mascot boxes come from the new snapshot's manifest and are applied to both images.
- **Runtime smoke.** New `scripts/test_zorp_runtime_smoke.py` runs `scripts/zorp_runtime_harness.js` (a hand-rolled fake DOM, no jsdom) against the real runtime and island: valence and allowlists, fx slot routing, `data-expr` sync (presets, `custom`, during and after clips), 80/90/120 ms swaps at full and none at reduced or off, and the thought part. Skips without node. `scripts/buddy_gate_harness.js` gained the valence-filter scenarios.
- **Measured (2026-09-29).** Default instance 2,493 B / 40 el. (676 gzip); heaviest preset (`aww-teary`) 3,494 B; fullest look 3,663 B; library 12,169 B; island 2,802 B; logged-in `/` 22,450 B (3,824 gzip); `zorp-motion.js` 35,308 B; `motion.css` 7,466 B; CSS tree 234,544 / core 209,552 (caps 246,000 / 216,000 unchanged). Cache pins: `zorp-motion.js` v6, `motion.css` v5, `styleguide.js` v6, `study-buddy.js` v27, `guide.js` v16, `sw.js` `pb-v95`.
- **Review fixes (2026-09-29).** (a) `guide.js` checks the last line of a lore step against the plain `guide` list, so a lore step with a missing or negative `step.resolve` ends on `nudge`, never on `sad`. (b) The `wide` eye's white fill is now `--brand-50`, so the pupil stays visible in dark mode (`wow`, `oops`). (c) `test_twinkle_rate` expands grouped keyframe stops (`0%, 100%`), so a 1 → 0.4 → 1 twinkle counts two changes, not one. (d) `--compare` crops the larger of the two mascot boxes, so a part lost at the right or bottom edge still counts.
- **Preview files.** `data/zorp_gallery/phase2/`: `expressions.png`, `matrix.png`, `matrix-dark.png`, `fx-filmstrips.png`, `faces.png`, `faces-reduced.png`, `faces-parity.png`, `compare-baseline.txt`.

### Phase 3: Views and the 90° turn (≈3–4 h)

- `buddy.html`: `zorp-flip` wrapper, arm pivot groups, `buddy-arm--*-front` pairs, `zorp-slot--fx` outside flip, `zorp-highlight` group. `motion.css`: arm pivot switch to `view-box` / `0 0` (§3.9), flip origin.
- `zorp_rig.VIEWS` (front, three-quarter, side, back, back-glance) and side-variant parts (`eyes:side`, `mouth:side-smile`, `mouth:side-o`).
- Runtime: `turn()`, resting state via `commitStyles()`, clips layered with `composite:'add'` (feature-detected), `side-point` clip, `point` gains an optional `view:'side'`.
- The macro gains a `view=` parameter for static renders (inline style from `VIEWS`).
- **Tests:**
  - `test_rig_markup` stays green (order invariants).
  - New `test_views_complete` (every view defines every part key; transforms parse).
  - `test_ambient_fx_outside_flip` (the `?`/`!`/`zzz` slot is not a descendant of `zorp-flip`).
  - `test_arm_pivot_groups` (arm parts start at `M0 0`; the pivot group carries the old shoulder coordinates 15.6,40 / 48.4,40).
  - `test_existing_arm_clips_unchanged` (Playwright is optional, so this is a structural check: the clip angle literals are unchanged).
  - Node harness smoke (`scripts/zorp_rig_harness.js`, skips without node like `test_buddy_gate_smoke.py`): `turn()` under reduced/off makes no animation calls.
- **Cache/pins:** `zorp-motion.js` →v7, `motion.css` →v6, `styleguide.js` →v7, `sw.js` →pb-v96.
- **Preview:** `phase3/views.png` (5 views × 2 facings × light/dark) and `phase3/turn-filmstrip.png` (10 frames of front → side → front). On the laptop, Chrome DevTools "Animations" panel at 10% speed, or the gallery 0.25× toggle.
- **Done when:** Zorp turns to a clean side profile and back at both 56 and 160 px, existing clips still look the same in front view, and ambient glyphs never mirror.

### Phase 4: Pose library, arm shapes, beat engine and the fist-pump jump (≈4–5 h)

- Arm-shape parts (`rest/straight/fist/bent/bent-fist`) with hand nubs. `zorp_rig.POSES` (§3.9). Runtime `pose()`, `compileBeats()`, the easing table, `STRETCH_MAX`, and follow-through helpers (antenna lag, head lag).
- New clips from §3.11: `fist-pump`, `victory`, `flex`, `shrug`, `bow`, `think-chin`, `dance`, `float`, `oops-encourage`. Optionally re-author `cheer`/`hop` onto beats (same names, same reduced behaviour, duration ±100 ms).
- The macro's `pose=` parameter renders static poses (used by the gallery and later by kit stills).
- **Tests:**
  - `test_clip_names_superset` (every old `CLIP_NAMES` entry is still present; `PHASE4_CLIPS` at `test_zorp_motion_smoke.py:43` is untouched).
  - `test_every_new_clip_has_reduced` (each clip defines `reducedExpr` or is explicitly `reducedSkip`, as `peek` is, `:488-511`).
  - `test_beats_reference_known_names` (regex-extract `pose:`/`expr:`/`fx:`/`view:` literals from `zorp-motion.js` and compare to `zorp_rig`).
  - `test_stretch_within_limits` (parse beat scale pairs: |sx·sy − 1| ≤ 0.12).
  - `test_clips_end_non_negative`.
  - Node harness: `compileBeats()` produces one animation per part; `stop()` cancels all of them.
- **Cache/pins:** `zorp-motion.js` →v8, `motion.css` →v7 (arm-shape pivots only, if any), `styleguide.js` →v8, `sw.js` →pb-v97.
- **Budget:** `zorp-motion.js` expected ~40–45 KB (≤48,000). Record it.
- **Preview:** `phase4/poses.png` (static grid plus a silhouette version) and `phase4/clip-<name>.png` filmstrips. Optional `phase4/clips.webm` from Playwright `record_video_dir` (a short video that opens on a phone).
- **Done when:** the fist-pump jump reads clearly at 56 px, poses pass the silhouette check, and reduced motion shows only the preset.

### Phase 5: Wiring into app moments (≈2–3 h)

- Runtime react tables read `CONTEXT_MAP`:
  - `correct` rotates `grin`/`joy`/`happy`/`smug` with clips `cheer`/`hop`/`wave`/`fist-pump`, never repeating the last one (the same rule as `CORRECT_VARIANTS`, `zorp-motion.js:14`).
  - `streak` → `fist-pump` + sparkles.
  - `first_correct` → `victory` + wow→joy.
  - `milestone` → `flex` or `bow` + proud/bashful.
  - `lesson_complete` → `dance` (no trip in reactions) + love/happy.
  - `wrong` → `oops-encourage` (replaces `wobble` + `weak_topic`, `:16`, `:23`). `wobble` is kept as a clip.
  - Cooldowns and rare-protect are unchanged (`:13`, `:22`, `:660-674`).
- Corner buddy: `face_for_prompt` maps `streak_risk` → `heads-up` (D4 accepted, §7.1), `celebrate` → `happy`, `weak_topic` → `thinking`, `friend_challenge` → `wink`. `reactBuddy` stays `nod` (`study-buddy.js:78-83`).
- Guide: `guide-catalog.js` faces and gestures are refreshed (origin: turn-in + wave; tours: `side-point` toward `highlight`; reward: `victory`/`proud`). Lore lines may use `sad` → `aww`/`happy` only in allowlisted step ids. David reviews that copy.
- Welcome (`welcome.js`): hello turn-in + wave, level `side-point` down, topic `think-chin`, card tap `fist-pump` (keeps the 450 ms timeout race at `:77-80`).
- Empty states: `data-zorp-autoplay="think-chin"` / `"shrug"`. Offline stays a static `sleep`.
- `docs/DPIA.md` review-log row. `docs/SECURITY_AND_GDPR.md` untouched unless the gate says otherwise.
- **Tests:**
  - `test_react_mapping_uses_context_map`.
  - `test_react_wrong_resolves_positive`.
  - `test_guide_negative_faces_allowlisted`.
  - `test_prompt_faces_positive_or_neutral`.
  - `test_guide_smoke.py` stays green (`ZORP_GESTURES` superset; `LEGACY_GESTURES` exact).
  - `test_welcome_smoke.py` pin on `welcome.js?v=`.
- **Cache/pins:** `zorp-motion.js` →v9, `guide-catalog.js` v10→11, `guide.js` →v17, `welcome.js` v2→3, `study-buddy.js` →v28 (if touched), `sw.js` →pb-v98.
- **Preview:** a gallery "Context map" table rendered from `CONTEXT_MAP` (moment → preset/clip → valence), for David's safeguarding review on the phone. `phase5/moments.png` shows each moment's key frame.
- **Done when:** every moment in the map plays its new reaction, `wrong` never ends on negative, and David has approved the context map.

### Phase 6: Pose-kit parity and a static-still helper (≈1–2 h)

- `zorp_kit.html`: replace `_nudge_face` and the other face snippets with `zorp_parts.html` macros inside `<g transform="translate(8 8)">`, so badge stills and the live rig share face art. Tokens (`zorp_kit.py:17-32`), viewBox 80 and headwear (`test_zorp_kit_smoke.py:182-228`) stay. `_standing_body` (`zorp_kit.html:15-23`) is untouched, so `'<ellipse cx="40" cy="46"'` stays.
- `zorp_rig.still(pose, preset, size, view)` renders the live rig statically (inline styles) for any future still. No new kit tokens (the 11-token pin stays).
- **Tests:**
  - `test_zorp_kit_smoke.py` stays green unchanged, or with explicit, reasoned edits.
  - New `test_kit_faces_from_parts` (the kit template imports `zorp_parts.html`).
  - Snapshot `--compare` against a pre-phase capture of the 11 stills (≤0.5% pixel diff).
- **Cache/pins:** templates only, so no static bumps. Bump `sw.js` only if a static file changed.
- **Preview:** `phase6/kit-parity.png`, before/after for all 11 stills.
- **Done when:** the stills look the same and there is one face-art source.

### Phase 7: Polish, idle life, performance, docs (≈2 h)

- **Idle life:** glance, antenna twitch, rare ¾ look-around (≥45 s apart), IntersectionObserver pause, and no micro-action while busy or thinking.
- **Performance pass** in Playwright with CDP `Emulation.setCPUThrottlingRate(4)`, as a proxy for low-end Chromebooks:
  - Run 30 quick answers on Practice plus each clip.
  - Collect frame times with `requestAnimationFrame` deltas.
  - Target p95 ≤ 20 ms and no long task > 50 ms from `zorp-motion.js`.
  - If `filter: drop-shadow` on `.buddy-mascot` (`chrome.css:759`) shows up as repaint cost during clips, replace it with a static shadow ellipse or apply it only when idle.
  - Record the numbers here. This is not a smoke.
- **Docs:**
  - Extend `AI_HANDOFF.md` rule 17: "Expressions and poses are data in `models/zorp_rig.py` + art in `partials/zorp_parts.html`; negative presets obey `CONTEXT_MAP` valence rules."
  - Point `ANIMATION_ONBOARDING.md` and E7 §6 here.
  - Mark this doc's phases "Built" with dates.
- **Tests:** the idle scheduler respects `motionLevel()` (node harness), and budgets are re-measured.
- **Cache/pins:** `zorp-motion.js` →v10, `chrome.css` →v46 (if the filter changes), `sw.js` →pb-v99.
- **Preview:** a perf summary table in the phase report, plus `phase7/idle.webm`.
- **Done when:** perf targets are met at 4× throttle and the docs are updated.

### 6.9 How David previews each phase

1. **Primary (phone-friendly): the implementer attaches the snapshot sheets to every phase report.** `python scripts/zorp_gallery_snapshot.py --label phaseN [--compare baseline]` produces static PNG contact sheets with labels, light/dark and 56/128 px, plus filmstrips of clips at full and reduced motion. Optionally it also records a short `.webm` (Playwright `record_video_dir`). No server is needed to view any of it.
2. **Laptop:** run the app as usual (`Open Problem Bank.bat`, `http://127.0.0.1:5001`) and open `/styleguide#zorp-gallery`.
   - The styleguide is dev-only and always available on localhost (`app.py:5474-5483`). No login is needed, because the page sets `zorp_motion_demo`, which loads the runtime (`base.html:57`).
   - The gallery has buttons for every preset, pose, view and clip; a 0.25× slow-motion toggle; a silhouette toggle; and a motion-level simulator (system/reduced/off).
   - DevTools → Rendering → "Emulate prefers-reduced-motion" double-checks the OS path.
3. **Phone against the laptop (optional, home network only).**
   - Start with `FLASK_RUN_HOST=0.0.0.0` (read at `app.py:11700`) and **debug off**, then open `http://<laptop-LAN-IP>:5001/styleguide#zorp-gallery`.
   - The gate allows non-localhost hosts only when `SITE_URL` is unset or not `https://` (`app.py:5482-5483`). Check `.env` first.
   - Windows may ask for a firewall exception. Never do this on a school network.

---

## 7. Open decisions for David

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | How expressions are swapped | A: parts library `<template>` + clone into slots. B: `<use>` sprite. C: every variant inline in every instance. | **A.** Smallest page weight that still lets every part be animated. The Phase 1 budget smoke proves it. C would roughly triple the mascot bytes per page. |
| D2 | Does Zorp get eyebrows? | Yes, floating strokes, none on the resting face. No. | **Yes.** They provide most of the emotional range, and two current faces already use them (`buddy.html:103`, `:136-137`). Resting Zorp looks unchanged. |
| D3 | Where may "sad goo-goo eyes" appear? | A: gallery only. B: goo-goo eyes with a smile (`aww`) at positive moments, and frowning `sad` only in allowlisted Guide lore that resolves positively in the same step. C: anywhere. | **B.** You get the cute eyes widely without ever using sadness as pressure (std 13). |
| D4 | `streak_risk` face | Keep today's frown + flame (`buddy.html:131-133`). Change it to the upbeat `heads-up` (raised brows, soft smile, flame). | **Change it.** A frowning mascot next to "your streak is at risk" is exactly the streak-shaming the DPIA rules out (`DPIA.md:48`). |
| D5 | Canvas size | Keep viewBox 64×64 with overflow. Move to 80×80 like the kit. | **Keep 64.** Every pivot, overlay anchor, size rule and several smokes assume it. Raised fists and effects can overflow safely (`motion.css:4`). |

### 7.1 Decisions confirmed 2026-09-29

David chose every recommendation on 2026-09-29. Frozen like §2; a change needs David's explicit say-so and a dated note here.
- **D1: A.** Parts-library `<template>` cloned into per-instance slots (§4.2).
- **D2: Yes.** Floating-stroke brows; none on the resting face.
- **D3: B.** `aww` (goo-goo eyes + smile) at positive moments; frowning `sad` only in `NEGATIVE_ALLOWED` Guide lore that resolves positively in the same step.
- **D4: Change.** `streak_risk` swaps its frown for the upbeat `heads-up` look (raised brows, soft smile, flame): the art changes in Phase 1 (exempt from legacy pixel parity, shown side by side), the named `heads-up` preset lands in Phase 2, and the prompt mapping in Phase 5.
- **D5: Keep 64.** viewBox `0 0 64 64`, `overflow: visible`.

**Feature gate** (`python scripts/ops_cadence.py feature-gate`, 2026-09-29; `SECURITY_AND_GDPR.md` §6.1):
- Q1 new personal data: **no**. Presentation only; no stored field, no analytics.
- Q2 child more visible to others: **no**. Mascot is per-viewer; public-profile badges stay decorative kit stills.
- Q3 new third party: **no**. Hand-built SVG + WAAPI/CSS; no library/CDN.
- Q4 profile/rank/nudge: **yes**. Expressions react to pupil actions and sit beside buddy prompts (nudge-adjacent). Children's Code std 13: the §5 rules bind every phase (an expression never asks for anything; no negative preset in prompt/react/dismiss/idle/autoplay/notification contexts; D4 removes the streak-risk frown). Dated `docs/DPIA.md` review-log row in Phase 5 when expressions are wired into app moments. Phase 0 changes nothing pupil-visible.

---

## 8. Optional later (not in E8)

- Library as a cached route (`/zorp/parts.svg?v=N`), if page weight ever matters (§4.2).
- Eyes follow the focused answer option or the hint panel (`lookAt(el)`). Only at full motion, never "watching" text entry.
- Zorp points at the hint after two wrong answers on one question (carried over from E7 §6).
- Seasonal idle variants (e.g. `float` in space week). Automatic only.
- New pose-kit tokens built with `zorp_rig.still()` (would change the 11-token pin deliberately).
- A pupil-facing expression or pose picker. Still deferred per E7 §2 #13. It would need a new stored preference, a fresh gate and a DPIA touch.

---

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Inline SVG bloat on every page | Per-instance cap (≤4,500 B, ≤70 elements) and per-page mascot cap (≤36,000 B / ≤6,000 B gzip) in `test_zorp_expression_smoke.py`. The library is only on pages that load the runtime. The fallback plan is a cached route (§8). |
| Busy, uncanny or over-animated Zorp | §3.10 limits: one fx family per beat, idle micro-actions no more than once per 6 s, holds ≥250 ms, stretch ≤12% at 56 px. Every phase gets a silhouette and 56 px review. David approves the contact sheets before the next phase. |
| Jank on low-end Chromebooks and phones | Only transform and opacity are animated. No path morphing, SMIL or animated filters. One `animate()` per part per clip. Pause when hidden or off-screen. The Phase 7 4× CPU-throttle pass has numeric targets. The drop-shadow filter is a known suspect (`chrome.css:759`). |
| `composite:'add'` or `commitStyles()` missing on an old browser | Feature-detect. The fallback is today's replace behaviour (snap to front), which still works. |
| Arm pivot drift when shapes swap | Pivot groups with parts drawn from (0,0) (§3.9). `test_arm_pivot_groups` checks this. |
| Test churn and stale pins (these have caused real CI failures before) | Each phase lists every pin it bumps. Changed assertions are edited in the same commit with the reason. Existing names are superset-only. Run the full smoke suite before asking David to commit. |
| Style drift between the live rig and the pose kit | Phase 6 moves kit faces onto the shared parts macros, with a pixel-diff guard. The body drawing stays pinned by the existing smoke. |
| Safeguarding regressions from later copy edits | Valence and `CONTEXT_MAP` checks run in the smoke suite on every future change, not just in E8. The rules also go into AI_HANDOFF rule 17. |
| Face allowlists drifting across three JS files | All consumers ask `pbZorp.hasExpression`. Local lists remain only as the no-runtime fallback. |
| Two mascots on screen with conflicting acting (corner plus decorative) | The existing decorative exclusion (`zorp-motion.js:622-624`) and PWA-banner hide rule (`chrome.css:739`) stay. Only one react target at a time. |
| Dark-mode contrast of new marks (blush, drops) | The gallery and snapshots render both themes every phase. Mascot-scoped colour properties can be tuned without touching `--brand-*`. |
