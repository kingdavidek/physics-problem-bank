# Zorp charm: talking mouth, soft body, one voice, optional sound (E9)

**Status:** Planned 2026-10-04. **Phase 0 built 2026-10-04** (spec freeze, feature gate in §7.2, copy inventory in Appendix A, ledger baseline in §2.1, e9-baseline snapshots; templates, scripts, docs and models only, no static or cache change), awaiting review. Decisions D1 to D9 confirmed by David on 2026-10-04 (§7.1); D10 and D11 confirmed later the same day. **Phase 1 built 2026-10-04** (talking mouth in the Guide, corner bubble and welcome), awaiting review. **Phase 2 built 2026-10-04** (soft body and secondary motion; D4 belly dropped), awaiting review. **Phase 3 built 2026-10-05** (voice guide 3.3.6, copy pass, enforcing lint), awaiting David's line-by-line review. **Phase 4 built 2026-10-06** (the `zorp_sound` setting, synthesised cues, privacy docs), awaiting review. **Phase 5 built 2026-10-06** (evaluation kit, showreel, docs): **E9 built; evaluation pending.** The class session has not happened, so the results are blank and no tuning is applied.
**Written against:** `main` at 43e387e (E8 Phases 0 to 5 and 7, plus the clip readability pass; E8 Phase 6 not built). Every file:line reference below was checked against that tree.
**Owner of decisions:** David. **Builder:** any agent, using the pipeline in §6.0. One phase per commit, and only when David explicitly asks. David confirms each phase before the next one starts.
**Read first:** `docs/ZORP_EXPRESSIVENESS.md` (E8; §2 #2 bans path morphing at `:66`; squash limits in §3.10 at `:310`; developer API in §10 at `:875-898`), `docs/AI_HANDOFF.md` rule 17 (`:89`) and the settings-switch bug (`:36`), `docs/MASCOT_MOTION_AND_ONBOARDING.md` §2 #7 and #9 (`:41`, `:43`: sound off by default, oscillator tones only, no audio files), `docs/ANIMATION_ONBOARDING.md:114` (the Guide reveals line by line, not with a typewriter), `docs/SECURITY_AND_GDPR.md` §6.1 (`:346-351`) and `:235`, `docs/DPIA.md:48`, `:71`, `:111`.
**Epic id:** E9. No Markdown source in `docs/`, `app.py`, `static/js/` or `scripts/` uses `E9`. The only hits are two `.docx` binaries, which are false positives.

---

## 0. What we are building, in one paragraph

Zorp gets "Duo-level charm at a few key moments", not everywhere. The moments are the Guide's story and reward lines, the corner bubble when it appears, the welcome hello, and the big celebration clips. There are four additions, in order of value:

- **A talking mouth.** It flaps loosely in time with the text he is "saying", pauses at punctuation, and stops within 1.6 s.
- **A softer body.** The body shape squashes and stretches on its own, on top of the existing whole-rig squash. The face, antennae and hat ride along, and there is a little jelly wobble on landing and a whip in the antennae.
- **One consistent voice.** A short tone guide, a pass over every line Zorp says, and a copy-lint smoke so the voice stays consistent.
- **Optional sound.** A couple of tiny synthesised celebration cues, off by default, that never play on page load, in a quiz or without a recent tap.

It ends with a teacher-led, offline evaluation kit that collects no data in the app. The rules from E8 all stand: hand-built SVG, WAAPI with `transform` and `opacity` only (no path morphing), no libraries, no audio files, no new personal data beyond one stored display preference, `zorp_sound` (D6 = B; the voice-blip option of D7 stays off the pupil-facing settings), reduced and off motion respected, and screen readers always get the full text at once.

---

## 1. Where we are today, and the gaps

### 1.1 What exists (verified)

| Thing | Where | State |
|---|---|---|
| Guide text | `templates/partials/guide.html:10` (`<p id="guide-bubble" aria-live="polite">`, also the dialog's `aria-describedby` at `:5`); `static/js/guide.js:558-562` | One line at a time via `textContent`. Continue moves to the next line (`onPrimary`, `:641-650`). Under reduced motion all lines are joined with `\n` (`:546`, `:559-561`). Focus goes to Continue on open (`:587-589`). The gesture plays on the last line (`:576`) through `pbZorp.play` (`:369-381`). |
| Guide reduced-motion check | `guide.js:76-78` | Reads the OS media query only, not `data-motion`. This is the known gap at `AI_HANDOFF.md:324`. |
| Guide copy | `static/js/guide-catalog.js` | 31 lines; the longest is 88 characters (`:108`). Em dashes at `:29` and `:82`. "freeze" at `:142`, while the profile page says "skip" (`templates/profile.html:117`). "Daily habit" at `:175`. "No DMs." at `:231`. "maths (and a bit of science)" at `:16`. |
| Guide fallback copy | `guide.js:491`, `:507`, `:524`, `:555` | "You earned this.", "N-day streak. Nice work keeping it going.", "Well done.", headings. |
| Corner bubble | `templates/base.html:288-322`; `static/js/study-buddy.js:244-289` | `show()` sets `messageEl.textContent` (`:247`) and unhides the card. No live region (correct: it must not interrupt). The face is bound with idle life on (`:372-375`). |
| Bubble copy | `models/buddy.py` | `:191` friend challenge; `:211` "looks shaky" (judges the pupil); `:232`, `:343` em dashes; `:345` "Quiz logged... Another go?"; `:365`, `:368` streak lines (`:368` is pinned by `test_buddy_smoke.py:296` and `test_zorp_expression_smoke.py:810`); `:269` "Keep learning X". |
| Welcome copy | `templates/welcome.html:30-31`, `:96` | `:96` says "When you get one right, I'll do a little dance." This is now wrong: a correct answer rotates cheer, hop and wave, and only `lesson_complete` dances. It is pinned by `test_welcome_smoke.py:292`. |
| System-voice copy beside Zorp | `app.py:3985-4029` (notifications; milestone adds an emoji at `:4026-4027`); empty states (`saved_problems.html:38-39`, `leaderboard_friends.html:77-78`, `:117-118`, `qotd.html:101-102`, `follow_list.html:34-36`); `offline.html:14`; tab-badge label `base.html:352`; answer feedback `static/js/site.js:1006`, `:1166` | Not in Zorp's voice, and should stay that way (§3.3). |
| Mouth art | `templates/partials/zorp_parts.html:106-146`; `models/zorp_rig.py:33-37` (24 mouth variants), `:250-256` (side map) | Mouth slot `g.zorp-slot--mouth` at `buddy.html:93`. A mouth swap pops with WAAPI `scale(0.9)` to `1` over 90 ms (`zorp-motion.js:227`). |
| Body | `buddy.html:82-85` | `g.buddy-body` holds the ellipse (cx 32, cy 36, rx 21, ry 21.5; bottom at y 57.5) and the highlight. The face (`:87-95`), antennae (`:73-80`) and hat (`:95`) are siblings inside `buddy-head`. Pivot: `motion.css:7-12` (`.buddy-body` origin 50% 100%, fill-box). No clip transforms `.buddy-body` today; only the reduced cheer pulse uses it, through a class (`motion.css:47`). |
| Squash and stretch | `static/js/zorp-poses.js:39-57`, `:223-268` | Root-only `scale(sx,sy)` per beat (`crouch` is 1.11 x 0.89, `:19`). Antennae follow with one 80 ms overshoot (`:28-30`, `:245`). Head lags 40 ms and arms 30 ms. `STRETCH_MAX = .12` (`zorp_rig.py:361`). `cheer` and `hop` are still legacy track clips in `zorp-motion.js:816-900`. |
| Runtime hooks | `zorp-motion.js:80-91` (`motionLevel`, honours `data-motion` and the styleguide `data-motion-preview="full"`), `:678-707` (`stop` cancels `inst.anims`), `:1123-1131` (`once`), `:1142-1146` (`lively` gates idle life), `:1227` (hidden tab stops every instance), `:1255-1261` (`register` payload) | Clean extension point: `zorp-poses.js` already plugs in through `register`. |
| Sound | `static/js/sound.js` (3,557 B, `?v=3`, loaded on every page, `base.html:54`) | WebAudio oscillators. Gate: `body[data-sound-enabled="1"]` (`:7-11`, set at `base.html:82` for signed-in users with `sound_enabled`). The context is unlocked on the first tap or key (`:34-42`). Peak gains: correct 0.11, wrong 0.14, celebrate 0.10, ding 0.11, soft 0.08 (`:70-103`). |
| Sound setting | `templates/profile_settings.html:195-201` (`settings_switch('sound_enabled', ...)`), `settings-sound.js?v=1` | Default off. Known bug: the switch UI may not persist (`AI_HANDOFF.md:36`). `motion_preference` uses a radio group that avoids the bug (`profile_settings.html` near `:170-190`; `models/social.py:24`, `:208`). |
| Sound callers | `celebrate.js:117`, `:147`, `:161-167`, `:175-176` | Confetti plays `celebrate()`, but `burstConfetti` returns before any sound under reduced motion (`:114-117`). Correct, ding, soft and wrong play whatever the motion level. |
| CSP | `app.py:1127-1132` | `script-src 'self' 'nonce-...'`, no `unsafe-inline`. WebAudio oscillators fetch nothing. |
| Dev pages | `/styleguide` (`app.py:5485-5496`), gate `_guide_preview_enabled()` (`:5474-5483`) | Sections `#zorp-motion`, `#zorp-gallery`, `#zorp-views`, `#zorp-poselib` (`styleguide.html:24-27`); full-motion preview switch (E8 readability pass). |
| Snapshot tool | `scripts/zorp_gallery_snapshot.py` | `--label`, `--compare`, `--clips`, `--looks`. Playwright and Pillow optional; output in `data/zorp_gallery/<label>/`. |

### 1.2 Measured baseline (2026-10-04; the ledger in §2.1 compares to these)

Measured from the files with `wc -c`, and for templates by rendering through Jinja in memory exactly as the E8 smokes do.

| Measure | Today | Cap today |
|---|---|---|
| `zorp-motion.js` | 53,406 B | 56,000 (`test_zorp_expression_smoke.py:47`) |
| `zorp-poses.js` | 30,185 B | 33,200 (`:48`) |
| Parts library `<template>` | 16,562 B | 18,200 (`:49`) |
| Rig JSON island (with tags) | 5,362 B | 6,000 (`:50`) |
| Default instance | 3,036 B, 50 elements | 4,500 B, 70 elements (`:42-43`) |
| Page mascot bytes (logged-in `/`) | 31,137 B (ledger 2026-10-02) | 36,000 B, 6,000 B gzip (`:45-46`) |
| `motion.css` | 9,170 B | 12,000 (`test_zorp_motion_smoke.py:33`) |
| CSS tree / core | 236,921 / 211,929 B (core headroom 4,071 B) | 246,000 / 216,000 (`test_u8_a11y_smoke.py:67`, `:99`) |
| `sound.js` | 3,557 B | none |
| `guide.js`, `study-buddy.js`, `guide-catalog.js` | 24,347 / 13,398 / 8,805 B | none |
| Cache pins | `chrome.css?v=45`, `motion.css?v=8`, `zorp-motion.js?v=11`, `zorp-poses.js?v=4`, `zorp-triggers.js?v=2`, `sound.js?v=3`, `study-buddy.js?v=28`, `guide-catalog.js?v=11`, `guide.js?v=17`, `celebrate.js?v=10` (`base.html:30-70`), `welcome.js?v=3` (`welcome.html:116`), `styleguide.js?v=9` (`styleguide.html:738`), `settings-sound.js?v=1` (`profile_settings.html:330`), `sw.js` `pb-v100` | Pinned by `test_buddy_smoke.py:119`, `:121`, `:405`, `test_zorp_expression_smoke.py:517`, `:1238`, `test_pwa_smoke.py:47` |
| Smoke suite | 98 files (`scripts/run_smoke_tests.py:16` globs `test_*_smoke.py`) | All green at 43e387e (as reported) |

### 1.3 Gaps against the brief

| Wish | Gap today |
|---|---|
| Talking mouth | No talk state. The only mouth motion is the 90 ms pop when the expression changes. Text appears with no character response. |
| Soft body | Squash is a uniform scale of the whole rig about the feet. Body, face and feet deform together, so landings read as rigid scaling. The antennae have one overshoot and no damped whip. Nothing jiggles. `cheer` and `hop`, the everyday correct-answer reactions, are outside the beat engine. |
| One voice | Copy is spread over 6 files and 2 voices with no rules: em dashes, one judgement ("looks shaky"), an inaccurate promise (welcome dance), mixed terms ("freeze" and "skip"), jargon ("DMs"), and a streak "habit" nudge. Nothing stops regressions except four exact-string pins. |
| Sound | Answer tones exist. There is no mascot cue, no rule about how many sounds play per moment, and no explicit "recent tap" gate (`celebrate()` can be called on page load for a milestone island, `celebrate.js:244-258`; it is silent today only because the context starts suspended). |
| Evaluation | No structured way to check whether the charm encourages or distracts. |

---

## 2. Design decisions (proposed; frozen once David confirms §7)

1. **Same character, same rules.** E6 §2 #1, E7 §2 #1 to #13 and E8 §2 #1 to #11 all stand. In particular, only `transform` and `opacity` animate (E8 §2 #2). That rules out path `d` morphing, animating `rx` and `ry`, SMIL and animated filters.
2. **Charm is rationed to named moments** (the §3.0 moment table). Idle life never talks or makes a sound. Answer reactions never talk. Nothing new happens on a page where nothing was asked of the pupil, except the corner bubble, which is already rare because of its quiet-window gate.
3. **The talking mouth is a dedicated talk mouth set stepped by opacity (D1).** Two new talk parts (half-open and open, plus profile twins) are cloned once into a JS-created `g.zorp-slot--talk` at talk start. The base mouth slot is the "closed" frame. One stepped opacity keyframe list per layer: no DOM churn per flap, compositor-friendly, and `stop()` for clips does not touch it.
4. **Text appears at once; the mouth follows the text, not the other way round (D2).** The Guide keeps the E6 line-by-line reveal (`ANIMATION_ONBOARDING.md:114`). The full line is in the DOM, and so in the live region, before the first flap. A word reveal is specified in §3.1.4 but only built if David picks it.
5. **The soft body is a transform rig (D3).** The body group gets its own extra squash and stretch, anchored at the bottom of the body. The face, antennae and hat ride it by translation, with a damped jelly settle. An optional "belly" layer (D4) gives a pear shape on landing. This works on every browser that runs the runtime today: Chromebooks, iPad Safari and Firefox.
6. **Sound is synthesised WebAudio, off by default, and tied to the animation (D6, D8).** No files (E7 §2 #9). At most one celebration sound per moment, and a Zorp cue replaces the generic arpeggio rather than adding to it. Cues only after a tap or key press in the last 5 s. Never on page load, in quiz-runner mode, from idle life or autoplay, or in a hidden tab. Cues play only when the full-motion clip plays, so reduced and off motion are silent for mascot cues. Answer tones are unchanged.
7. **Copy is data with a linter.** The voice guide (§3.3) is enforced by `scripts/test_zorp_voice_smoke.py`. The inventory is generated from the sources into Appendix A between markers, and the smoke fails when it drifts (the same pattern as the `POSES` markers in `zorp-poses.js:18-20`).
8. **Motion-level matrix (extends E8 §2 #5):**

   | | `full` | `reduced` (OS or setting) | `off` |
   |---|---|---|---|
   | Text | at once (word reveal only if D2 = B) | at once, all Guide lines joined (as today) | at once, all lines joined |
   | Talking mouth | yes | no | no |
   | Soft body, jelly, antenna whip | yes (inside beat clips) | no (beat clips do not run) | no |
   | Zorp cues (sound on) | with the clip | none | none |
   | Voice blips (only if D7 = yes) | with the flaps | none | none |
   | Styleguide `data-motion-preview="full"` | n/a | talk and soft body run (dev only) | talk and soft body run (dev only) |

9. **Budgets are recorded, not guessed** (E8 §2 #7). New caps are named constants. Any raise is a dated ledger entry in §2.1 and in the constant's comment, measured need plus about 10 percent (the rule David authorised on 2026-10-02).
10. **One new display preference (D6 = B, confirmed).** A new `zorp_sound` setting (`off` default, `celebrations`; `chatter` defined but hidden until after the evaluation, D7) is stored with the other display preferences. Phase 4 adds ROPA row 1, both privacy notices and a DPIA row in the same commit, and checks export and erase. Evaluation is offline and anonymous (D9).
11. **Back-compat is additive.** Every E8 API name, clip name, `data-*` hook, test assertion and fallback keeps working. Pins change only deliberately, in the same commit, with the reason in the commit message.

### 2.1 Budget ledger (the implementer fills in "measured" per phase)

| Budget | Today | Proposed cap | Pinned in | P0 | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|---|---|---|---|
| `zorp-motion.js` | 53,406 | 56,000 (unchanged; E9 adds about 150 B: the `talking` idle gate and two `findParts` selectors) | `RUNTIME_JS_MAX_BYTES` | 53,406 | 53,658 | 53,971 | 53,971 | 54,019 | 54,019 |
| `zorp-poses.js` | 30,185 | 33,200, raised to **36,500 on 2026-10-04 in Phase 2** (measured 35,531 B, need plus about 3 percent; 35,909 B after the Phase 2 review, headroom 591 B for the Phase 4 cue hooks; soft-body tracks about 1.4 KB, `cheer`/`hop` beat clips about 0.9 KB, cue hooks about 0.3 KB in Phase 4) | `POSES_JS_MAX_BYTES` | 30,185 | 30,185 | 35,909 | 35,909 | 36,448 | 36,448 |
| `zorp-talk.js` (new) | n/a | **10,500**, raised from 9,000 on 2026-10-12 in the final audit (A3: the hush when the motion level drops mid-talk; measured 9,550 B, need plus about 10 percent). Earlier: raised from 7,000 on 2026-10-04 in Phase 1 (estimate was 5.5 KB; measured 8,298 B, need plus about 9 percent; 8,662 B after the review fix) | `TALK_JS_MAX_BYTES` (new, `test_zorp_charm_smoke.py`) | n/a | 8,662 | 8,662 | 8,662 | 8,982 | 8,982 |
| `sound.js` | 3,557 | **9,900**, raised from 7,000 on 2026-10-06 in Phase 4 (estimate was 5.6 KB; measured 9,364 B after the review fixes (8,971 B as built), headroom 536 B; the estimate did not allow for the gate, the arbiter, the cue bus, `stopAll`, the blips and the unlock hooks) | `SOUND_JS_MAX_BYTES` (new) | 3,557 | 3,557 | 3,557 | 3,557 | 9,364 | 9,364 |
| Parts library | 16,562 | 18,200 (talk mouths add about 600 B; raise only with a ledger entry) | `PARTS_LIBRARY_MAX_BYTES` | 16,562 | 17,409 | 17,409 | 17,409 | 17,409 | 17,409 |
| Rig island | 5,362 | 6,000 (talk side map adds about 40 B) | `RIG_JSON_MAX_BYTES` | 5,362 | 5,454 | 5,454 | 5,454 | 5,454 | 5,454 |
| Default instance | 3,036 B / 50 el. | 4,500 / 70 (ride wrapper and belly add about 120 B, 2 el.) | `INSTANCE_DEFAULT_MAX_BYTES`, `INSTANCE_MAX_ELEMENTS` | 3,036 B / 50 el. | 3,036 B / 50 el. | 3,067 B / 51 el. | 3,067 B / 51 el. | 3,067 B / 51 el. | 3,067 B / 51 el. |
| Page mascot | 31,137 | 36,000 / 6,000 gzip | `PAGE_MASCOT_MAX_BYTES`, `_GZIP` | 31,137 / 5,096 gzip | 32,076 / 5,255 gzip | 32,169 / 5,263 gzip | 32,169 / 5,263 gzip | 32,169 / 5,263 gzip | 32,169 / 5,263 gzip |
| `motion.css` | 9,170 | 12,000 (adds about 450 B: talk and ride pivots, `.zorp-sr`, belly origin) | `MOTION_CSS_BUDGET_BYTES` | 9,170 | 9,304 | 9,304 | 9,304 | 9,304 | 9,304 |
| CSS tree / core | 236,921 / 211,929 | 246,000 / 216,000 (unchanged; core headroom 4,071 B covers the about 600 B E9 needs) | `test_u8_a11y_smoke.py:67`, `:99` | 236,921 / 211,929 | 237,055 / 212,063 | 237,055 / 212,063 | 237,078 / 212,086 | 237,078 / 212,086 | 237,078 / 212,086 |

**Measured (Phase 1, 2026-10-04, after the review fixes):** `zorp-talk.js` 8,662 B of 9,000 (8,298 B as built; the review added the open-mouth swap handler and shortened the header comment) (new; the cap was raised from the 7,000 estimate by a dated entry, because the plan's 5.5 KB estimate did not allow for the plan fitter, the open-base closed frame, the off-screen observer and the hush paths; comments were stripped to the minimum first). `zorp-motion.js` 53,658 B of 56,000 (+252 B: the `talking` idle gate, two talk hooks in `setView` and `turnRun`, and the mouth-swap hook in `drawChannels`). Parts library 17,409 B of 18,200 (+847 B for the four talk mouths; the plan expected about 17,200, so no raise). Rig island 5,454 of 6,000 (+92 B: the talk side map). `motion.css` 9,304 of 12,000 (+134 B). Default instance unchanged (3,036 B, 50 elements). Page mascot 32,076 B of 36,000, 5,255 B gzip of 6,000. CSS tree 237,055 of 246,000, core 212,063 of 216,000 (headroom 3,937 B). `zorp-poses.js` and `sound.js` unchanged. Also recorded, no cap: `guide.js` 25,736 B, `study-buddy.js` 13,959 B, `welcome.js` 4,846 B, `styleguide.js` 20,602 B.

**Measured (Phase 5, 2026-10-06):** nothing capped changed. `zorp-motion.js` 54,019 B of 56,000, `zorp-poses.js` 36,448 B of 36,500 (headroom 52 B), `zorp-talk.js` 8,982 B of 9,000 (headroom 18 B), `sound.js` 9,364 B of 9,900, parts library 17,409 B, rig island 5,454 B, default instance 3,067 B and 51 elements, page mascot 32,169 B and 5,263 B gzip, `motion.css` 9,304 B, CSS tree 237,078 B and core 212,086 B (headroom 3,914 B), all equal to the Phase 4 figures, re-measured by `test_zorp_charm_smoke.py`. No cap was raised: Phase 5 needed no bytes in `zorp-poses.js` or `zorp-talk.js`. The only static file that changed is `styleguide.js` (dev page, no cap; 23,399 B before, 27,473 B after: the showreel). Recorded, no cap: `guide.js` 25,856 B, `welcome.js` 4,857 B, `celebrate.js` 10,825 B (unchanged).

**Measured (final audit, 2026-10-12):** `zorp-talk.js` 9,550 B of **10,500** (raised from 9,000; was 8,982 B; the motion-drop hush added 568 B, need plus about 10 percent), `zorp-motion.js` 54,114 B of 56,000 (+95 B), `sound.js` 9,634 B of 9,900 (+270 B, headroom 266 B), `study-buddy.js` 14,096 B, `zorp-poses.js` 36,448 B, parts library 17,409 B, rig island 5,454 B, default instance 3,067 B and 51 elements, page mascot 32,169 B and 5,263 B gzip, `motion.css` 9,304 B, CSS tree 237,078 B and core 212,086 B. Only the `zorp-talk.js` cap was raised.

**Measured (Phase 4, 2026-10-06):** `sound.js` 9,364 B of 9,900 (8,971 B as built; the review added `cued` and the 30 ms `stopAll` ramp; +5,807 B on P0; cap raised from 7,000 by the dated entry above). `zorp-poses.js` 36,448 B of 36,500 (+539 B for the cue beats and the start hook; comments were trimmed to fit, no raise; headroom 52 B). `zorp-talk.js` 8,982 B of 9,000 (+320 B for the blips hook and `stopAll` on hush; comments trimmed, no raise; headroom 18 B). `zorp-motion.js` 54,019 B of 56,000 (+48 B: the cue pass-through). Unchanged: parts library 17,409 B, rig island 5,454 B, default instance 3,067 B and 51 elements, page mascot 32,169 B and 5,263 B gzip, `motion.css` 9,304 B, CSS tree 237,078 B and core 212,086 B. Recorded, no cap: `guide.js` 25,856 B, `welcome.js` 4,857 B, `celebrate.js` 10,825 B, `styleguide.js` 23,399 B. Peak cue gain 0.06 (about -24.4 dBFS), blips 0.03; offline renders: jump -24.8 dBFS 124 ms, land -25.2 dBFS 66 ms, tada -24.3 dBFS 262 ms, jump then land 347 ms, blips -30.8 dBFS.

**Measured (Phase 3, 2026-10-05):** every capped value equals its Phase 2 figure except the CSS tree: `zorp-poses.js` 35,909 B, `zorp-motion.js` 53,971 B, `zorp-talk.js` 8,662 B, parts library 17,409 B, default instance 3,067 B and 51 elements, page mascot 32,169 B and 5,263 B gzip, `motion.css` 9,304 B, CSS tree 237,078 B and core 212,086 B (+23 B after the review: `text-wrap: pretty` on `.guide-bubble` in `chrome.css`, v45 to v46, so a Guide line no longer ends on a lone word such as "chat." at 375 px). Recorded, no cap: `guide-catalog.js` 8,961 B (+156 B on P0 8,805: the voice-guide pointer in the header comment, net of the shorter lines), `feed.js` 6,488 B (-3 B). `guide.js` 25,736 B, `study-buddy.js` 13,959 B and `welcome.js` 4,846 B are unchanged. The `data-zorp-voice` attributes are short (about 35 B each); `base.html` carries 12 of them on every page and `welcome.html` 11, so no page grows by more than about 0.5 KB, and no budget row above includes them.

**Measured (Phase 2, 2026-10-04, after the review fixes):** `zorp-poses.js` 35,909 B of 36,500 (35,531 B as built; the review added the drawn-squash jelly and the exact antenna ride, +378 B) (+5,724 B on P0; the plan expected about 2.6 KB. The soft body is a body-scale list, three rider lists, the jelly and cheek tracks, the antenna whip, the auto stretch for dance steps and float, and the `cheer` and `hop` beat clips; comments were cut to the minimum first). The cap was raised 33,200 to 36,500 by the dated entry above, so Phase 4's cue hooks have 591 B. `zorp-motion.js` 53,971 B of 56,000 (+313 B: four `findParts` selectors for face, ride, hat ride and cheeks). Default instance 3,067 B and 51 elements (+31 B and 1 element: the antenna wrapper; the hat wrapper only exists with a hat), cap 4,500 / 70. Page mascot 32,169 B of 36,000, 5,263 B gzip of 6,000. `motion.css` unchanged at 9,304 B (see the Phase 2 notes). Parts library, rig island and CSS tree unchanged. Also recorded: `styleguide.js` 21,429 B.

**P0 (Phase 0, 2026-10-04):** measured from the tree at 43e387e by `scripts/test_zorp_charm_smoke.py` (`BASELINE`, the same rendering as the E8 ledger). Nothing in `static/` changed, so every value equals the §1.2 figure. The page mascot gzip figure of 5,096 B is new (cap 6,000). Also recorded, with no cap: `guide.js` 24,347 B, `study-buddy.js` 13,398 B, `guide-catalog.js` 8,805 B. Core CSS headroom is 4,071 B. **Ledger rule:** the smoke fails only when a measured value passes its cap. `BASELINE` stays frozen at these P0 numbers; the smoke prints each value's drift from it, and every later phase copies its measured numbers into its own column here. Exact equality would fail on any unrelated CSS or page change outside E9.

---

## 3. Detailed design

### 3.0 The moments (the whole scope of "charm")

| Moment | Talk | Soft body | Zorp cue (sound on) |
|---|---|---|---|
| Guide origin story (once ever) | every line, cap 1,600 ms | gestures (`wave`, `cheer`, `fist-pump`) | none (story, not a reward) |
| Guide reward panels (first correct, lesson complete, streak 7/30/100, badge) | every line, cap 1,600 ms | reward gesture | yes: `jump` and `land`, or `tada` |
| Guide tours | every line, cap 1,200 ms | gestures | none |
| Corner bubble appears | once per show, cap 1,200 ms | none | none |
| Welcome hello and ready | the copy line, cap 1,400 ms | hello wave, card-tap `fist-pump` | card tap only (`jump`, `land`) |
| Answer reactions (`correct`, `wrong`, `streak`) | no | yes (`cheer`, `hop`, `fist-pump`, `oops-encourage`) | no: answer tones already speak |
| `lesson_complete` on later lessons (corner dances) | no | yes (`dance`) | yes (`jump`, `land` on the hop) |
| Idle life, empty-state autoplay, offline, PWA banner | never | autoplay clips only | never |

### 3.1 The talking mouth

**3.1.1 Art (`zorp_parts.html`, `zorp_rig.py`).**
- New mouth variants `talk-1` (half open) and `talk-2` (open), centred at x 32, top edge y 43.4, in the `grin` style (`.zf` fill with a 1.2 ink stroke).
  - `talk-1`: rounded D, 7.2 wide and 3.0 tall.
  - `talk-2`: 9.0 wide and 4.6 tall, with a small `--zorp-rouge` tongue.
- Profile twins `side-talk-1` and `side-talk-2` are 4.5 and 5.5 wide, in the `side-grin` position.
- Colours: ink and rouge only; never `--wrong-*` or `--correct-*` (E8 §3.1).
- Readability at 56 px: the two frames must differ by at least 1.3 units of height. `talk-2` is 1.6 units taller.
- Add them to `CHANNELS['mouth']` and `_SIDE_MOUTH`, so `validate()`'s "every mouth has profile art" rule covers them.
- Add a new `TALK_MOUTHS` tuple. No preset may use them (tested). They are neutral shapes: no downturn, no valence of their own, so talking can never put a negative face on screen.

**3.1.2 Mechanism (`static/js/zorp-talk.js`, new).**
- At talk start, create `g.zorp-slot--talk` with `createElementNS` as the next sibling of the mouth slot inside `g.zorp-face`. Clone the two talk parts into it with `rt.node` (the existing `partNode`). Copy the mouth slot's resting `translate` and `scale` (the view state) onto the group. Pick the side art when `inst.view` is `side` or `back-glance`. In the `back` view, refuse (resolve `false`).
- When the base mouth is itself open (`grin`, `grin-tongue`, `laugh`, `wow`, `o`, `side-grin`, `side-o`), also clone `smile` (or `side-smile`) as a third child to serve as the closed frame, and hide the base slot for the whole talk.
- Emit one WAAPI animation per layer: the base slot (or the alternative closed frame), `talk-1` and `talk-2`. Each animates `opacity` with per-keyframe `easing: 'steps(1, end)'`, built from the plan (§3.1.3).
- Talk animations live in `inst.talk` (`{ anims, node, timer }`), not `inst.anims`. A gesture or clip that calls `stop(inst)` (`zorp-motion.js:678`) therefore keeps the mouth talking. Expression swaps underneath still work, because the base mouth shows only in closed frames.
- `hush` cancels the animations, removes the group and restores the base slot's opacity. Every exit path calls it: end of plan, a new talk, a hidden tab (`visibilitychange` listener in `zorp-talk.js`), Guide close or advance, bubble dismiss, and a turn starting.
- One talker at a time: starting a talk hushes every other instance.
- `lively()` (`zorp-motion.js:1142`) gains `!inst.talking`, so no glance or look-around starts mid-sentence. Blinks may still happen.

**3.1.3 The talk plan (pure function `talkPlan(text, opts)`, exported for tests and the styleguide).**
- **Words.** Split on whitespace. Syllables are vowel groups (`[aeiouy]+`), minus a silent final `e`, minimum 1. A digit group counts as 1 syllable per 2 digits. An `@handle` counts as 2.
- **Syllables.** Each syllable is an open frame then a closed frame. The base timing is 75 ms open and 60 ms closed (135 ms, about 7.4 Hz). The first syllable of a word uses `talk-2`, the others `talk-1`, and 1 or 2 letter words use `talk-1`. There is a 40 ms closed gap between words.
- **Punctuation pauses (closed):**
  - `,` and `;`: 140 ms
  - `:` and a bracket: 180 ms
  - `.`, `!` and `?` inside the line: 260 ms
  - an ellipsis: 360 ms
  - punctuation at the very end of the line adds no pause; the talk simply ends
- **Start and end.** The talk starts 120 ms after the text is set, so the text is always there first and the 90 ms expression pop has finished. It always ends on a closed frame.
- **Caps:** Guide story and reward 1,600 ms; tours and corner bubble 1,200 ms; welcome 1,400 ms. Absolute ceiling 2,000 ms, well under the WCAG 2.2.2 five-second limit for moving content.
- **Fitting to the cap.** If the natural length exceeds the cap:
  1. Compress the syllable timing down to a floor of 60 ms open and 51 ms closed (a 111 ms cycle, so at most 9 Hz), with pauses no shorter than 60 percent of the values above.
  2. If it is still too long, stop after the last whole syllable that fits.

  The sync is deliberately loose: the mouth "says" the start of the line.
- **WCAG.** A mouth flap is a small dark shape, far below the WCAG 2.3.1 general-flash area, but it stays at or below 9 Hz to look gentle. Talk never runs at reduced or off motion.

**3.1.4 Optional word reveal (only if D2 = B; specified so it can be built without redesign).**
- `say(target, text, { reveal: 'words' })` writes two children with `createElement` and `textContent` (never `innerHTML`):
  - `span.zorp-sr`: the full text, visually hidden (new 7-line utility in `motion.css`). This is what the live region and `aria-describedby` read, once.
  - `span[aria-hidden="true"]`: one `span` per word, separated by text nodes so the line wraps naturally. Each word starts at `opacity: 0` and gets a `.is-on` class (opacity 1, 120 ms transition) at the time of its first open frame.
- No reflow: every word takes up its final space from the start.
- Tapping or clicking the bubble shows all words at once and hushes the mouth.
- Continue always advances (keyboard and screen-reader flow unchanged).
- The whole reveal shares the talk cap (at most 1.6 s).
- Reduced, off, or no runtime: plain `textContent`.
- Proposed use: only the origin story (once ever).

**3.1.5 Consumers.**
- **Guide** (`guide.js` `renderStep`):
  - Compute the line as now.
  - If `pbZorp.say` exists, call `pbZorp.say(bubbleEl, text, { el: faceEl, max, reveal, talk: level === 'full' })`. Otherwise keep `bubbleEl.textContent = text`, so the literal pinned at `test_guide_smoke.py:110` stays.
  - Replace the OS-only `prefersReducedMotion()` decision for the line reveal with `pbZorp.motionLevel() !== 'full'` when the runtime exists. Keep the media-query fallback, and with it the string pinned at `:113`. This closes the `data-motion` gap at `AI_HANDOFF.md:324` for the Guide.
  - `closeOverlay` and `advanceStep` call `pbZorp.hush(faceEl)`.
- **Corner bubble** (`study-buddy.js` `show()`): after unhiding the card, call `talk({ el: faceEl, text: prompt.message, max: 1200 })`. The dismiss and action handlers call `hush`.
- **Welcome** (`welcome.js`): on hello, chain after the wave: `talk({ el: hero, text: copyEl.textContent, max: 1400 })`. On ready, talk the line once after 400 ms.
- **Celebrate:** no change (no text).

### 3.2 The soft body

**3.2.1 Principle.** The root keeps every keyframe it has today, so silhouettes, durations and existing tests do not move. `compileBeats` (`zorp-poses.js:223`) adds one extra layer: **the body alone carries an additional 40 percent of each beat's root deviation**, anchored at its own bottom (y 57.5; the `.buddy-body` origin already in `motion.css:12`).

`b = 1 + 0.4 * (s - 1)` per axis, where `s` is the beat's root scale. For `crouch` that is 1.044 x 0.956, so the body as drawn becomes 1.159 x 0.851 (product 0.986).

Because the face, feet and arms do not take the extra layer, Zorp reads as a soft body squashing over planted feet, not a scaled sprite. The arms need no ride: their shoulders sit at least 4.6 units inside the body edge in every case (16.4 x 0.044 is at most 0.75 units of shift), which a test checks.

**3.2.2 Riders (translate only, so the face never distorts more than today).** Each rider's `dy` is the vertical shift of its anchor point when the body scales about its bottom:
- Face (`.zorp-face`): `dy = 19.5 * (1 - b_sy)` (plate centre y 38).
- Antennae: `dy = 41.5 * (1 - b_sy)` (base y 16). This goes on a new wrapper `g.zorp-ride` around both antennae, because the antennae's own transform carries the lagged rotation, and a lagged ride would detach them from the body.
- Hat: `dy = 43 * (1 - b_sy)`, on a `g.zorp-ride` wrapper drawn around the hat only when a look has a hat. A CSS transform on the hat itself would replace its `transform` attribute.
- All riders share the body's timing exactly (lag 0).

**3.2.3 Jelly and whip (secondary motion).**
- **Jelly.** On each landing beat (the root's dy goes from negative to 0 or more while `sy < 1`), with landing deviation `w = b_sx - 1`, the body adds a damped wobble inside the following beat:
  - +70 ms: `(1 - 0.6w, 1 + 0.6w)`
  - +140 ms: `(1 + 0.3w, 1 - 0.3w)`
  - +210 ms: `(1, 1)`

  That is about 7 Hz, two half cycles. It is truncated if the next beat is shorter than 210 ms, and **clip durations do not change**.
- **Cheeks.** When the cheeks are drawn: `translateY` +0.8 at +60 ms, -0.3 at +130 ms, 0 at +200 ms.
- **Antennae.** The existing single overshoot (`zorp-poses.js:245`) becomes a damped whip: target `v` at +80 ms (as now), `-0.4v` at +170 ms, `+0.15v` at +250 ms, then 0, still capped at 16 degrees.

**3.2.4 Belly (D4, optional pear shape).**
- New `ellipse.zorp-belly` inside `.buddy-body`, before the highlight. Starting values: cx 32, cy 46.5, rx 15, ry 10.5, filled with `--zorp-body`. At rest it is entirely inside the body: sampled at 360 points, it clears the outline by at least 0.2 units.
- On landing, the belly gets `scaleX(1 + 2.2 * (b_sx - 1))` about its own bottom. The lower body bulges out by up to about 1 unit: a pear on the squash and a slimmer drop on the stretch.
- Cost: 1 element, about 95 B per instance.
- Built behind a flag. It ships only if the Phase 2 A/B filmstrip reads at 56 px.

**3.2.5 Limits (tested).**
- Body layer: each axis within 0.08 of 1.
- Body as drawn (root times body): each axis within 0.16 of 1, product within [0.97, 1.03].
- Root: `STRETCH_MAX` 0.12 unchanged.
- Plate inside the body at every keyframe (sampled).
- Antenna base within 0.3 units of the body top.

**3.2.6 Coverage.**
- Every beat clip (`fist-pump`, `victory`, `flex`, `shrug`, `bow`, `think-chin`, `dance`, `float`, `oops-encourage`, `wave`), and `cheer` and `hop` once they are re-authored as beat clips in `zorp-poses.js` (D5).
- `cheer` and `hop` keep their names, durations within 100 ms and their reduced behaviour. The legacy versions stay in `zorp-motion.js` as the fallback when the poses file is missing, as `wave` already does.
- Not touched: `turn`, `look-around`, the CSS idle breathe, legacy E6 gestures.
- Dev A/B: `html[data-zorp-soft="off"]` disables the layer. Only `styleguide.js` sets it, which a test checks, as with `data-motion-preview`.

### 3.3 Voice and copy

**3.3.1 Who Zorp is.**
- A small, curious alien from Novara who loves a good problem and finds Earth fascinating.
- He is a bot, not a person, and says so plainly when it matters.
- Warm, playful and encouraging, never sarcastic.
- Jokes point at himself, never at the pupil. At most one physics pun per tour.
- British spelling. Plain English at CEFR B1 level, because many European School pupils read English as a second or third language.

**3.3.2 Two voices.**
- **Zorp voice** (first person allowed): Guide lines and labels, corner bubble messages, welcome hero lines, the Guide bot note.
- **System voice** (no "I", no character): notifications, empty states, answer feedback, offline, PWA banner, tab badges, settings.

Zorp never speaks in notifications or in grading feedback. The lint enforces the split in both directions.

**3.3.3 Do and don't.**

| Do | Don't |
|---|---|
| Invite: "Fancy another go?" | Command or urge: "Do it now", "Hurry", "Before midnight" |
| Notice effort: "Nice work: 7/10 on Forces." | Judge ability: "looks shaky", "easy", "obviously", "simply" |
| Frame streaks as optional: "One quick question counts, if you like." | Loss or risk: "lose", "break", "at risk", "don't miss", "last chance" |
| Make dismissal neutral: "Not now" | Confirmshame: "No thanks, I don't want to learn" |
| Own his feelings lightly, in lore only | Tie his feelings to the pupil's choices: "I'm sad when you leave", "I missed you", "come back" |
| Speak to the pupil alone | Compare: "your friends are ahead", "everyone else" |
| Say he is a bot | Ask for personal details (name, school, age) or invite free text |

**3.3.4 Mechanical rules (enforced by the lint):**
- **Banned phrases** (case-insensitive): lose, losing, lost (your streak), break (your streak), at risk, don't miss, last chance, hurry, before it's too late, come back, miss you, missed you, I'm sad, disappointed, failed, you forgot, only N left, everyone else, friends are ahead, easy, obviously, simply, lazy.
- **Warn-level** (allowed with a justification comment in the source): just, don't worry.
- **US spellings:** color, favorite, center, behavior, analyze, organize, realize, recognize, practicing, license (noun), math (as a word), gotten, mom.
- **Verb and noun:** `practise` for the verb, `practice` for the noun. The lint checks "practice this", "practice a", "to practice".
- **Characters:** no emoji, no em dash or en dash in Zorp lines (house style; use a comma, colon or full stop). At most one `!` per line and at most one line in four with an exclamation mark across the inventory.
- **Length limits:**

  | Surface | Limit |
  |---|---|
  | Guide line | 100 characters (today's longest is 88) |
  | Reward line | 80 |
  | Corner message (rendered with a 30-character sample topic label) | 100 |
  | Button and dismiss labels | 22 (the stay label is just "Keep learning", D10) |
  | Bubble detail labels | 20 |
  | Welcome line | 70 |

- **Reading level:** Flesch-Kincaid grade at most 8 per line **for lines of 8 words or more only (D11)**, and at most 5 averaged over all Zorp lines (every line counts toward the mean), using a vowel-group syllable counter with no dependency. Words of 4 or more syllables only from an allowlist (physics terms, `Novara`, placeholders); this check, like the mean, applies to every line whatever its length (D11). Phase 0 records today's numbers before the thresholds bite.
- **Glossary:** "streak skip", matching `profile.html:117` (never "freeze" in Zorp lines); "badge"; "quiz"; "Practice tab"; "Not now".

**3.3.5 Sample rewrites (Phase 3 drafts; David approves every line).**

| Where | Today | Proposed |
|---|---|---|
| `buddy.py:211` | "{topic} looks shaky. A short practice set will help." | "{topic} could use another look. A few questions will help it stick." |
| `buddy.py:343` | "Nice work — {s}/{t} on {topic}." | "Nice work: {s}/{t} on {topic}." |
| `buddy.py:345` | "Quiz logged on {topic} ({s}/{t}). Another go?" | "Quiz done on {topic}: {s}/{t}. Fancy another go?" |
| `buddy.py:365` | "You have a skip in hand this week, and one quick question still keeps your streak going." | "You have a streak skip this week, so no rush. One quick question also counts." |
| `buddy.py:368` | "Keep your {days}-day streak going with one quick question." | "You’re on a {days}-day streak. One quick question counts, if you like." (David review: "Day N" was off by one) |
| `guide-catalog.js:16` | "...to make maths (and a bit of science) less scary." | "...to make maths and physics feel less scary." |
| `:29` | "I'm the one in the corner — a bot, not a person." | "I'm the one in the corner. I'm a bot, not a person." |
| `:82` | "Ready when you are. Skip this any time — you won't see it again." | "Ready when you are. You can skip this any time, and it won't show again." |
| `:119` | "Check your answer here. I'll pop when you get a streak of correct ones." | "Check your answer here. I'll cheer when you get a few right in a row." |
| `:142` | "Missing a day can use a freeze if you have one." | "If you miss a day, a streak skip can cover it." |
| `:175` | "One question a day. That's the Daily habit." | "A new question every day, whenever suits you." |
| `:231` | "Challenges are optional. No DMs." | "Challenges are optional. There is no chat." |
| `welcome.html:96` | "When you get one right, I'll do a little dance." | "Get one right and I'll cheer. Finish a lesson and I'll dance." |

Pins that change on purpose in Phase 3: `test_welcome_smoke.py:292`, `test_buddy_smoke.py:296`, `test_zorp_expression_smoke.py:810`. `test_guide_smoke.py:179`, `:188` and `:199` stay green (`Novara`, "You earned this.", "Not now" are kept).

**3.3.6 Voice guide (as built in Phase 3; the short version for anyone writing copy).**

*Who is talking.*
- **Zorp** (a small, curious alien from Novara, warm and playful, a bot who says so): the Guide lines and labels, the corner bubble, the welcome screens (heading, hello line, "Skip for now", "Surprise me"), and the Guide bot note. First person is fine ("I'll cheer"), but it is not required.
- **The system** (no "I", no character): notifications and toasts, empty states, the offline page, the install banners, the tab badge label, answer feedback, settings copy.
- **The Problem Bank bot** (`problem_bot`, the daily challenge card) is a system account with a nerd-face avatar, not Zorp, so it speaks in the system voice. Its "not a person" note is the same words everywhere: "A Problem Bank bot, not a person." (`models/bot.py`, `feed.js`, `public_profile.html`, the Guide panel). Zorp's own line is "I'm a bot, not a person." (decided 2026-10-05; the planner left it open).

*How he sounds.* Short sentences. Plain words for pupils who read English as a second or third language. British spelling. Invite, never urge ("Fancy another go?"). Notice effort ("Nice work: 7/10"), never ability. Jokes point at himself. Streaks are optional and upbeat ("One quick question counts, if you like"). He never says he is sad or missed anyone because of what a pupil did. He does not ask for personal details and does not invite free text.

*Words.* Use "streak skip" (never "freeze"), "badge", "quiz", "Practice tab" (the noun), "practise" (the verb), "Not now", "Keep learning". Avoid "DMs" (say "chat"), "habit", "easy", "just", "simply". No emoji, em dashes or en dashes in a Zorp line (use a comma, a colon or a full stop). At most one "!" in a line and one line in four.

*Limits.* Guide line 100 characters, reward line 80, corner message 100 (with a 30-character topic), button label 22, bubble detail label 20, welcome line 70. Reading grade at most 8 per line of 8 words or more, at most 5 on average, no word of four or more syllables unless it is in `LONG_WORD_ALLOW` in `models/zorp_voice.py`.

*Promises must be true.* A line may only promise what Zorp does. A correct answer rotates cheer, hop and wave; a streak milestone is a fist-pump; a first correct is a victory pose; only a completed lesson dances. `test_welcome_line_is_truthful` pins that for the welcome line.

*How it is enforced.* `scripts/test_zorp_voice_smoke.py` extracts every line (JavaScript by regex, Python by `ast`, templates by `data-zorp-voice="<voice>:<surface>[:dismiss]"`) and fails on any rule above. Add a template line with the attribute (a new template file also needs an entry in `MIN_ITEMS` in the smoke), then run `python scripts/test_zorp_voice_smoke.py --write` to refresh Appendix A. A `just` or `don't worry` needs a `voice-ok` comment on the source line.

### 3.4 Sound

**3.4.1 Technique.** WebAudio oscillators in `sound.js`, the E7 §2 #9 rule: no files, so no licensing, no decoding, no `media-src` CSP change, no precache bytes, and offline-safe. Each cue is an envelope (`setValueAtTime`, `exponentialRampToValueAtTime`) on one or two sine or triangle oscillators through one shared `GainNode`, so `stopAll()` can cut it.

**3.4.2 Cues.**

| Cue | Sound | Duration | Peak gain | Used by (only when the caller passes `cue: true`) |
|---|---|---|---|---|
| `jump` | sine glide 330 to 660 Hz | 160 ms | 0.06 | take-off beat of `fist-pump`, `victory`, `dance-up` |
| `land` | triangle 180 to 120 Hz, fast decay | 90 ms | 0.06 | landing beat after a `jump` |
| `tada` | sine 523, 659, 784 Hz, 70 ms apart | 300 ms | 0.06 | `flex`, `bow`, `wave` when used as a reward |
| `blip` (D7 only) | sine 520 to 680 Hz, pitch from a hash of the word, the last syllable of a `?` line 15 percent higher | 35 ms | 0.03 | every second open frame, at most 6 per second and 12 per line |

All cue gains are below today's quietest answer tone, `soft` at 0.08 (`sound.js:101`).

**3.4.3 When a cue may play (all must hold; enforced in `pbSound.zorp`).**
1. The pupil's `zorp_sound` setting is `celebrations` (D6 = B). Answer tones keep following `sound_enabled`.
2. A `pointerdown` or `keydown` happened within the last 5,000 ms. The capture listeners are already bound in `bindUnlock` (`sound.js:34-42`); they now also record the time.
3. The page is visible.
4. Not quiz-runner mode (`body[data-guide-quiz]`).
5. The motion level is `full`. This is automatic, because cues are scheduled by the beat engine's `start()`, which only runs at full motion.
6. No other `pbSound` sound in the last 400 ms.
7. At most one cue sequence per 7,000 ms (the same window as `BIG_GAP_MS`).

**3.4.4 One sound per moment.** When `pbSound.cuesActive()` is true (`zorp_sound` is `celebrations`, full motion, runtime present, not in a quiz), `celebrate.js` `burstConfetti` waits 1 s (the dance cue starts about 0.8 s after the reaction) and plays the arpeggio only if no Zorp cue started in the last 1.5 s (`pbSound.cued`). A cue that actually starts carries the moment; if none does (no Guide clip on the page, a tap older than 5 s, inside the 7 s window) the arpeggio plays, so a pupil with Zorp sounds on never gets silence. Correct, ding, soft and wrong answer tones are unchanged and are never replaced.

**3.4.5 Reduced motion (D8).** No mascot cues. A cue belongs to a movement, and the reduced experience is meant to be calm. This mirrors today's behaviour, where confetti and its arpeggio are already skipped under the device's reduce-motion setting (`celebrate.js:115`, `prefers-reduced-motion` only). The app's own Less motion and Off settings do not skip the arpeggio, at 43e387e or now: there `cuesActive()` is false, so the arpeggio plays as before (checked in the Phase 4 review). Pupils who want sound still get the answer tones.

**3.4.6 Classroom.**
- Default off.
- Nothing on page load. Even a milestone island firing at load is silent, by rule 2.
- Never during answer entry: idle life is silent, answer reactions have no cues, and quiz-runner mode is excluded.
- Settings copy says plainly that sounds are for headphones or home.

**3.4.7 Styleguide audio preview.** Buttons call `pbSound.zorp(cue, { force: true })`. `force` bypasses only rules 1 and 7, and only `styleguide.js` may pass it (tested).

### 3.5 Evaluation (Phase 5)

*Built in Phase 5 as `docs/ZORP_EVALUATION.md` and `docs/zorp_evaluation_print.html`. The prompts and checklist below are the plan's drafts; where they differ the evaluation doc wins (it has six open, reflective prompts, per David's preference for pupil-facing prompts: no matching, true or false, recall or rating scales, framed as fun and low-stakes).*

**3.5.1 Teacher-led and offline (D9).** Nothing is recorded in the app. An in-app "Is Zorp helpful?" toggle would be new processing and is close to analytics (`AI_HANDOFF.md` invariant 11), so it is not built.

**3.5.2 New `docs/ZORP_EVALUATION.md`:**
- **A 15-minute session plan.** Projector demo from the teacher's laptop at `/styleguide#zorp-charm` (§6.7), or a test account. Pupils use their own accounts only in classes where everyone is 13+ (the app's age gate; `DPIA.md:18`). For younger classes (S1 and S2 at a European School), use the projector demo only.
- **A teacher observation checklist (10 items):**
  - eyes on the question or on Zorp
  - time to press Continue
  - smiles and laughter
  - irritation on the second or third repeat
  - anyone asking to turn it off
  - sound acceptable in the room
  - any confusion about bot versus person
  - any upset at the `origin.home` lore line
  - pupils reading the text or waiting for the mouth
  - distraction during practice
- **Five open-ended, low-stakes pupil prompts on anonymous sticky notes** (no names, not graded, framed as fun):
  - "Describe Zorp in three words."
  - "When did Zorp make you smile, and when did he get in the way?"
  - "If Zorp could say one sentence when a question goes wrong, what should it be?"
  - "Should Zorp make sounds in class? Why, or why not?"
  - "Invent a new move for Zorp."
- **A results table** (date, class level, n, themes, decisions).
- **Success criteria:** at least two thirds of the notes read as encouraging rather than distracting; no reports of discomfort; sound judged acceptable only when opt-in.
- **Tuning.** Findings may change constants only (caps, rates, gains, which moments talk) in the same phase.

---

## 4. Architecture

### 4.1 Files touched

- **New:**
  - `static/js/zorp-talk.js` (talk, say, hush, `talkPlan`, blip scheduling hook; the optional reveal was not built, D2 = A)
  - `models/zorp_voice.py` (rules, extractor, Flesch-Kincaid helper, inventory renderer)
  - `scripts/test_zorp_voice_smoke.py`
  - `scripts/test_zorp_charm_smoke.py` (E9 ledger constants and static wiring checks)
  - `scripts/test_zorp_talk_smoke.py` with `scripts/zorp_talk_harness.js`
  - `scripts/test_zorp_sound_smoke.py` with `scripts/zorp_sound_harness.js` (fake `AudioContext`)
  - `docs/ZORP_CHARM.md` (this file)
  - `docs/ZORP_EVALUATION.md`
- **Changed:**
  - `templates/partials/zorp_parts.html` (talk mouths)
  - `models/zorp_rig.py` (`TALK_MOUTHS`, side map; the belly flag was not built, D4 dropped)
  - `templates/partials/buddy.html` (`g.zorp-ride` around the antennae and the hat; the optional belly was not built, D4 dropped)
  - `templates/base.html` (load `zorp-talk.js` under the runtime guard at `:57`, after `zorp-poses.js`; cache pins)
  - `static/js/zorp-motion.js` (`lively` talking gate; `findParts` adds `ride`, `hatRide`, `belly`, `face`, `cheeks`)
  - `static/js/zorp-poses.js` (soft-body layer, jelly, whip, `cheer` and `hop` beat clips, `cue` beats)
  - `static/js/guide.js`, `study-buddy.js`, `welcome.js`, `celebrate.js`, `sound.js`, `styleguide.js`, `static/css/motion.css`
  - `templates/styleguide.html`, `templates/profile_settings.html` (the `zorp_sound` radio, D6 = B; the chatter option stays hidden, D7)
  - `models/social.py` and the settings save path in `app.py` (`/profile/settings` and the settings API) (`zorp_sound` field, default `off`, validation), `templates/base.html` (`data-zorp-sound`)
  - `templates/legal_privacy.html`, `templates/legal_privacy_simple.html`, `docs/ROPA.md` (row 1), `scripts/test_gdpr_smoke.py` (export and erase) for `zorp_sound` (Phase 4, same commit)
  - `static/js/sw.js` (precache `zorp-talk.js`, `CACHE_VERSION`)
  - `scripts/zorp_gallery_snapshot.py`, `scripts/buddy_gate_harness.js` (stub `talk`/`hush`), `scripts/zorp_poses_harness.js`
  - the pinned smokes listed per phase
  - `docs/ZORP_EXPRESSIVENESS.md` §10, `docs/AI_HANDOFF.md`, `docs/DPIA.md`

### 4.2 API (added to `window.pbZorp` by `zorp-talk.js` through `pb.register`)

```js
pbZorp.talk({ el, text, max })            // Promise<boolean>: flaps the mouth; false at reduced/off motion, hidden tab, off screen, quiz runner, back view, missing parts
pbZorp.say(target, text, { el, max, talk })   // writes text synchronously, then talks (no `reveal` option: not built, D2 = A)
pbZorp.hush(el)                           // stop talking now; idempotent
pbZorp.isTalking(el)                      // boolean
pbZorp.talkPlan(text, { max })            // pure: { ms, frames: [[t, 0|1|2]], words: [t...] }
pbSound.zorp(cue, { force })              // cue gate of section 3.4.3; returns boolean
pbSound.cuesActive()                      // used by celebrate.js for the one-sound rule
pbSound.blips(times, seed) / pbSound.stopAll()   // D7 only
```

- Beat objects gain `cue` (`'jump'|'land'|'tada'`). `play()` and `react()` options gain `cue: true`.
- `guide.js` `playGesture` passes `cue: step.mode === 'reward'`.
- The `react` plan passes it for `first_correct`, `milestone` and `lesson_complete` only.

### 4.3 Fallbacks

| Missing | Behaviour |
|---|---|
| `zorp-talk.js` | Consumers see no `say`/`talk` and keep plain `textContent`. Nothing else changes. |
| `zorp-poses.js` | Legacy `cheer`, `hop` and `wave` play as today with no soft body. Cues never schedule. |
| Parts library or talk parts | `talk` resolves `false` and the text is unaffected. |
| `AudioContext` | `pbSound` no-ops (as today). |
| Individual `translate`/`scale` properties | Talk group copies no view state (front placement). Already the E8 fallback. |

### 4.4 CSP and cache discipline

- External script only. Every node is built with `createElement`/`createElementNS` and `textContent`. No `innerHTML` in any new code (the guide smoke already bans it in `guide.js`; the talk smoke extends the ban to `zorp-talk.js`).
- Every changed static file bumps its `?v=`. `sw.js` `CACHE_VERSION` goes up by one per phase, with `test_pwa_smoke.py:47` updated in the same commit. `test_welcome_smoke.py:145-155` cross-checks the precache list, which gains `/static/js/zorp-talk.js` unversioned (E8 Phase 7 note: the offline fallback ignores `?v=`).

### 4.5 Accessibility

- Mascots stay `aria-hidden`. Talking adds nothing to the accessibility tree.
- The full text is in the DOM before the first flap (`say` is synchronous, the talk starts 120 ms later). The Guide live region announces once per line, as today. The corner card stays without a live region (no spam).
- Focus never moves because of talk. Continue keeps its meaning. (The optional word reveal with tap-to-show-all was not built, D2 = A.)
- Talk stays under 5 s (WCAG 2.2.2) and at or below 9 Hz. Reduced and off motion: no flaps, no cues.

---

## 5. Safeguarding, accessibility and privacy checklist (every phase)

- **Children's Code std 13.**
  - Charm only at the §3.0 moments, all of them the pupil's own action or an achievement. Nothing reacts to hesitation, absence, dismissal or leaving.
  - No streak pressure in copy (§3.3.4).
  - Cues replace sounds and never add to them, and never play to pull a pupil back.
  - Phase 5 adds a dated `docs/DPIA.md` review-log row in the style of `:111`.
- **No guilt.** The E8 valence rules are untouched. Talk mouths are neutral and never change the expression. The lint bans loss and guilt framing and confirmshaming. Zorp's feelings appear only in allowlisted lore that resolves positively (`GUIDE_LORE_STEPS`).
- **Transparency.** The "bot, not a person" line stays (`guide.html:11`, and the origin line kept by `test_bot_qotd_smoke.py:89`).
- **Privacy.** D6 = B adds one stored display preference, `zorp_sound`: ROPA row 1, both privacy notices and a DPIA row in the same commit (precedent `DPIA.md:109`). Export and erase already cover `user_profile_settings` wholesale; Phase 4 tests confirm it. Evaluation is offline and anonymous.
- **Classroom.** Sound is off by default. No sound without a recent tap. None in quizzes, on load, from idle or autoplay, or in a hidden tab.
- **Accessibility.** §4.5 for every phase. Reduced and off motion are checked in every harness.
- **Security.** CSP-safe, no `innerHTML`, no new third party, no CDN (`test_guide_smoke.py` and `test_zorp_motion_smoke.py` library bans still pass).

---

## 6. Phases

### 6.0 Every phase

- **Pipeline:** implementer (Sonnet) builds on the cloud copy, then an independent reviewer (Opus) checks against this doc and the code, then fixes, then sync to David's laptop, then a parity check (file hashes cloud versus laptop, full suite on the laptop).
- One commit, only when David explicitly asks.
- Full suite green: `PB_TESTING=1 CORS_ORIGINS=https://app.example.com .venv312/bin/python scripts/run_smoke_tests.py` (98 today; 100 after Phase 0, 101 after Phase 1, 102 after Phase 4). `ruff check .` clean.
- `?v=` and `sw.js` bumps exactly as listed. Ledger measured in §2.1. A line in `docs/AI_HANDOFF.md` §1 and §9. Preview artefacts attached to the phase report.
- Docs prose: British spelling, no emoji, no em dashes.
- `?v=` numbers assume nothing else lands in between; always bump from the current number.

### Phase 0: Spec freeze, feature gate, copy inventory, baselines (about 1.5 h)

- David confirms §2 and D1 to D9.
- Run `python scripts/ops_cadence.py feature-gate` and record the answers in §7.2. Expected (revised for D6 = B; the first draft assumed D6 = A, where Q1 was no):
  - Q1 yes (the new `zorp_sound` display preference; ROPA, notices and DPIA rows in Phase 4, same commit)
  - Q2 no
  - Q3 no (synthesised audio, no files, no third party)
  - Q4 yes (talking and cues add salience to reward moments, so std 13 applies; the §5 rules bind)
- `models/zorp_voice.py`: rules from §3.3.4, the Flesch-Kincaid helper, and the extractor. The extractor covers:
  - `guide-catalog.js` lines and labels (regex)
  - `guide.js` reward fallbacks
  - `models/buddy.py` messages and labels via `ast` (f-strings rendered with sample values, including a 30-character topic)
  - template lines marked `data-zorp-voice` (attribute added in Phase 3; Phase 0 lists the welcome and guide lines by selector)
  - system-voice sources (`app.py` notification messages, empty states, offline)
- `scripts/test_zorp_voice_smoke.py` in report mode:
  - `test_inventory_extracts` fails only on extraction errors
  - `test_lint_report` prints violations and today's reading levels, and does not fail
  - `test_inventory_doc_in_sync` regenerates Appendix A between the markers and compares
- `scripts/test_zorp_charm_smoke.py`: E9 ledger constants at baseline values; `test_no_animation_or_audio_libraries` (no lottie, howler, tone.js, `.mp3`, `.ogg` or `.wav` under `static/`).
- Snapshot `--label e9-baseline --clips` (filmstrips of `cheer`, `hop`, `fist-pump`, `victory`, `flex`, `dance`) and `--copy` (new: Guide panel per line at 375 px, light and dark).
- **Cache/pins:** none (templates, scripts and docs only).
- **Preview:** `e9-baseline/clip-filmstrips.png`, `copy-guide.png`, `docs/ZORP_CHARM.md` Appendix A on the phone.
- **Done when:** decisions and gate are recorded, the inventory is generated, baselines exist, and the suite is green at 100.

**Phase 0 build notes (2026-10-04).**

- **Built:** `models/zorp_voice.py`; `scripts/test_zorp_voice_smoke.py` (report mode, `--write` regenerates Appendix A); `scripts/test_zorp_charm_smoke.py` (ledger baseline, caps, library and audio bans); `--clips` and `--copy` in `scripts/zorp_gallery_snapshot.py`; baselines in `data/zorp_gallery/e9-baseline/` (gitignored; `clip-filmstrips.png` for cheer, hop, fist-pump, victory, flex and dance at full motion, `copy-guide.png` with all 31 catalogue lines in the Guide panel at 375 px, light and dark, 62 panels, plus the standard sheets). No static file, template or cache pin changed. Suite 100 of 100.
- **Audio files:** none exist under `static/` (checked by extension), and no animation or audio library is vendored; `static/vendor/` holds only MathJax and Pyodide. Pyodide's runtime mentions audio formats in its own source, so the text scan for audio references covers first-party files only, while the audio-file and library-name checks cover the whole tree.
- **Feature gate:** §7.2. Q1 is yes because of D6 = B (the first draft assumed D6 = A).
- **Today's copy (Appendix A):** 178 items, 134 Zorp and 44 system; 48 Zorp lines. Flesch-Kincaid grade mean 3.1 (limit 5), highest 12.5; no line is over its length limit except the stay label below; no line uses `!`. Rule hits to settle in Phase 3: em dashes (guide-catalog `:29`, `:82`, `buddy.py:232`, `:343`, the bot note), "freeze" (`:142`), "DMs" (`:231`), "habit" (`:175`, `:255`), and four-syllable words ("celebration", "Accuracy", "Extraordinary").
- **Plan corrections made in this document:**
  1. The em dash in the "I'm the one in the corner" line is at `guide-catalog.js:29`, not `:30` (§1.1 and the §3.3.5 table).
  2. The §3.3.5 draft for `:82` ended "it won't come back", which is a banned phrase ("come back"). Changed to "it won't show again" (72 characters, grade 1.5).
  3. The §3.3.5 draft for `:231` ("there are no private messages") scores grade 8.1 to 8.9, over the per-line limit of 8. Changed to "Challenges are optional. There is no chat." (grade 4.3).
  4. §6 Phase 0 expected Q1 = no; with D6 = B it is yes (§7.2). §0 said "no new personal data unless D7"; corrected to name `zorp_sound`.
  5. §6 Phase 0 said to record the gate in §7.1; it is §7.2.
  6. The Appendix A summary written from the plan is replaced by the generated one (the 178 items above replace "about 25 labels" and similar estimates; the notification list has 8 strings because the fallback "New notification" counts, the PWA install and iOS banners are included, and `qotd.html` has two empty states).
- **Open questions for David or the Phase 3 reviewer (not fixed here):**
  1. The stay label `Keep learning {topic}` is 44 characters with a 30-character topic, over the 22-character button limit. Settled by D10 (§7.1): the label becomes "Keep learning" in Phase 3.
  2. "100-day streak. Extraordinary." scores grade 12.5 because it is two very short sentences with a five-syllable word; settled by D11 (§7.1): the per-line limit applies from 8 words, and the line becomes "100-day streak. Amazing." in Phase 3.
  3. The "lost (your streak)" and "break (your streak)" bans are implemented as same-sentence matches with "streak", since a bare "lost" or "break" would be too broad. The "don't worry" and "just" warn level is satisfied by a `voice-ok` comment on the source line.
  4. The tour screenshots remove each step's `highlight` in the page, because a tour silently skips steps whose target is not on `/guide-preview`; the panel copy is unaffected, but a spotlight is never shown in `copy-guide.png`. The clip filmstrips crop in the styleguide motion-level banner above the mascot; this matches the E8 sheet.
- **Review fixes (2026-10-04):** the ledger smoke now fails on caps only and prints drift from the frozen P0 `BASELINE` (rule in §2.1); the inventory sync check ignores a shift of line numbers alone; the streak bans match "streak" before or after "lost", "break", "broke" and "broken"; the library and audio scans are word-bounded (so `milestone.js` and `.wave` do not trip them); the catalogue extractor reports double-quoted or template strings and empty `lines` arrays instead of skipping them, and ignores `//` comments; `buddy.py` string concatenation is rendered or reported; `--write` keeps the doc's line endings and requires exactly one pair of markers; §4.1 lists the D6 = B files.

### Phase 1: Talking mouth in the Guide, corner bubble and welcome (about 4 h). The biggest visible win.

- **Files:** `zorp_parts.html`, `zorp_rig.py` (talk parts, `TALK_MOUTHS`, side map); new `zorp-talk.js`; `zorp-motion.js` (`lively` gate); `guide.js` (`say` with fallback, `motionLevel()` for the line reveal, hush on close and advance); `study-buddy.js`; `welcome.js`; `motion.css` (talk-group pivot, `.zorp-sr`); `base.html`; `sw.js`; `styleguide.html`/`styleguide.js` (new `#zorp-charm` section: a talk demo with a text box and every Guide line as chips, at 56, 72 and 128 px, front and side; plan readout).
- **Tests:**
  - `test_zorp_talk_smoke.py` (node harness scenarios):
    - `plan caps per surface`
    - `rate at most 9 Hz, no open frame under 60 ms`
    - `punctuation pauses`
    - `ends closed`
    - `reduced and off make no animate calls and resolve false`
    - `hidden tab hushes`
    - `back view refuses`
    - `clip stop keeps talking`
    - `expression swap mid-talk`
    - `one talker at a time`
    - `hush restores base mouth and removes the group`
    - `say writes the text synchronously`
    - `no innerHTML`
    - `lively false while talking`
    - `side view uses side art and copies view styles`
    - reveal scenarios (only if D2 = B)
  - `test_zorp_charm_smoke.py`:
    - `test_talk_js_budget`
    - `test_talk_loaded_under_runtime_guard_after_poses`
    - `test_talk_precached`
    - `test_talk_mouths_not_in_presets`
    - `test_talk_mouths_have_side_art`
    - `test_guide_say_with_textcontent_fallback`
    - `test_guide_reveal_uses_motion_level`
  - Changed: `test_buddy_smoke.py:119`, `:121`, `:405` pins; `test_zorp_expression_smoke.py:517`, `:1238` (styleguide pin); `buddy_gate_harness.js` stub; library budget measured.
- **Cache/pins:** `zorp-talk.js` v1, `zorp-motion.js` v11 to v12, `guide.js` v17 to v18, `study-buddy.js` v28 to v29, `welcome.js` v3 to v4, `motion.css` v8 to v9, `styleguide.js` v9 to v10, `sw.js` `pb-v100` to `pb-v101`.
- **Budget:** `zorp-talk.js` at most 7,000. Library at most 18,200 (expected about 17,200).
- **Preview:**
  - `phase1/talk-filmstrip.png`: one Guide line, every plan frame, 56 and 128 px, front and side, light and dark
  - `phase1/talk-mouths.png`: each base mouth times the closed, half and open frames
  - optional `phase1/talk.webm`
- **Done when:** the mouth reads clearly at 56 px, the text is complete before the first flap, reduced and off are still, and screen-reader output is unchanged (checked with Chromium's accessibility tree snapshot in the snapshot tool).

**Phase 1 build notes (2026-10-04).**

- **Built:**
  - Art: `talk-1`, `talk-2`, `side-talk-1`, `side-talk-2` in `zorp_parts.html` (rounded D, ink fill and stroke as `grin`; `talk-2` has a small rouge tongue; geometry as 3.1.1: 7.2 x 3.0 and 9.0 x 4.6, top edge y 43.4, centred at x 32; twins 4.5 and 5.5 wide with the same heights). `models/zorp_rig.py`: the four ids in `CHANNELS['mouth']`, `TALK_MOUTHS`, the side map, and `validate()` checks (no preset uses them, profile art exists).
  - `static/js/zorp-talk.js` (new, `?v=1`): `talk`, `say`, `hush`, `isTalking`, `talkPlan`, as 4.2. `zorp-motion.js` (`?v=12`): `lively()` also needs `!inst.talking`, and `setView()` and `turnRun()` end a running talk (the mouth group is placed for one view). `motion.css` (`?v=9`): the talk group pivots on its own centre like the mouth slot.
  - Consumers: `guide.js` (`?v=18`), `study-buddy.js` (`?v=29`), `welcome.js` (`?v=4`), as 3.1.5. `base.html` loads `zorp-talk.js` after `zorp-poses.js` under the runtime guard; `sw.js` is `pb-v101` and precaches `/static/js/zorp-talk.js` unversioned.
  - Dev: `/styleguide#zorp-charm` (`styleguide.js?v=10`): six live Zorps (56, 72 and 128 px, front and side), a text box, a cap menu, Talk, Hush, Talk with `cheer` and `fist-pump`, expression chips, motion-level and slow buttons, the plan readout, the full-motion preview banner, and every Guide line as a chip. `scripts/zorp_gallery_snapshot.py --talk` (or `--talk-only`) writes `talk-filmstrip.png` and `talk-mouths.png`, light and dark (`e9-phase1`).
  - Tests: `test_zorp_talk_smoke.py` with `zorp_talk_harness.js` (18 scenarios after the review, a fake clock, every name in the plan list except `lively false while talking`, which `test_runtime_hooks_for_talk` checks statically because `lively` is internal); eleven Phase 1 tests in `test_zorp_charm_smoke.py` (the seven named in the plan plus mouth geometry, consumer wiring and caps, runtime hooks, pins and the styleguide section); two scenarios in `buddy_gate_harness.js` (talk once per show, hush on every exit, an old runtime without `talk`). Changed pins: `test_buddy_smoke.py`, `test_zorp_expression_smoke.py`, `test_pwa_smoke.py`.
- **Ledger:** section 2.1 "Measured (Phase 1)". Suite 101 of 101.
- **Deviations from the plan, with the reason:**
  1. `TALK_JS_MAX_BYTES` is 9,000, not 7,000: the file measured 8,298 B as built and 8,662 B after the review (see 2.1).
  2. The word reveal and `.zorp-sr` are not built (D2 = A), so `motion.css` has no `.zorp-sr`, and `say` takes no `reveal` option; the `talk: false` option is the only switch.
  3. A last-line gesture that turns Zorp side-on (`side-point` on three tour lines, `bow`) is not talked: the pinch-turn moves the mouth slot, which the talk group does not follow, so any view change ends a talk. Those lines show their text at once and the gesture plays as before. The plan did not cover a view change mid-talk.
  4. `hush(el)` and a talk that is cut short resolve `false`; only a talk that runs to its end resolves `true`.
  5. The off-screen stop uses one `IntersectionObserver` created on the first talk (idle life's observer only runs when idle is on).
  6. A talk over an already open base mouth (`grin`, `grin-tongue`, `laugh`, `wow`, `o`, `side-grin`, `side-o`) shows that mouth until the first flap, then a drawn `smile` as the closed frame until the end; the group is removed at the end, so the base mouth returns. If an expression swap changes the base mouth mid-talk from closed to open (the reward gestures `fist-pump`, `victory`, `flex` and `dance` do this on the talked last line), `drawChannels` calls `inst.talk.swap`, which switches the closed frames to the drawn `smile` for the rest of the talk (review fix, 2026-10-04; before it, the closed frames showed the open grin, so the mouth never closed). A swap from open back to closed mid-talk keeps the smile until the end.
  7. The styleguide chips use the catalogue (`window.pbGuideCatalog`); the page loads `guide-catalog.js` itself when the viewer is not signed in. The expression chips leave out negative presets (the E8 template check bans them in the page source).
  8. Previews are in `data/zorp_gallery/e9-phase1/` (`talk-filmstrip.png`, `talk-mouths.png` and the dark twins), not `phase1/`, because `phase1` is the E8 snapshot label.
- **Checked in Chromium** (a registered test user, `/welcome` hello and ready, `/guide-preview` origin, five tours and two rewards, a corner bubble injected on `/topics`) at system, OS reduced, `data-motion="reduced"` and `data-motion="off"`: zero console errors; no talk group or mouth animation left after a quiet period; at full motion the Guide talked on 22 of 27 lines (the rest are very short, or the side-on gestures), the welcome and the corner bubble talked once; at reduced and off nothing flapped and every line was written at once; the Guide live region saw one text change per line and Continue kept keyboard focus; `data-motion="reduced"` now joins the Guide lines (21 panels) as the OS setting does.
- **Open for the reviewer:** (a) whether 9,000 B for `zorp-talk.js` is acceptable or the fitter should be simplified; (b) the side-on gesture rule above; (c) an expression change from a closed to an open base mouth mid-talk (deviation 6). **Review (2026-10-04):** (a) kept at 9,000 (8,662 B; the fitter is small, the header comment was shortened instead); (b) accepted; (c) fixed, see deviation 6, with the harness scenario `a swap to an open mouth mid-talk closes on a smile`. The styleguide demo now talks its six Zorps in turn (one talker at a time had left five of them silent).

### Phase 2: Soft body and secondary motion (about 4 to 5 h)

- **Files:** `buddy.html` (`g.zorp-ride` around the antennae, around the hat when present, optional belly); `zorp-motion.js` (`findParts`); `zorp-poses.js` (body layer, riders, jelly, cheek wobble, antenna whip, `cheer` and `hop` beat clips, `data-zorp-soft` dev switch); `motion.css` (ride and belly origins); `styleguide.js` (A/B toggle, belly toggle).
- **Tests:**
  - `zorp_poses_harness.js` scenarios: `soft body volume`, `face stays seated`, `antenna ride`, `arms clear without riding`, `durations unchanged` (every beat clip equal to the Phase 0 table), `cheer and hop beat versions within 100 ms with the same reduced face`, `jelly truncates in short beats`, `soft off switch`
  - `test_zorp_charm_smoke.py`: `test_soft_switch_only_in_styleguide`, `test_belly_inside_body_at_rest` (360 samples, if D4)
  - `test_poses_js_budget` gets the new cap
  - `test_rig_markup` and `test_existing_arm_clips_unchanged` stay green
  - Default instance and page budgets re-measured
  - `--compare e9-baseline` on still faces: 0 over the limit (the stills must not change)
- **Cache/pins:** `zorp-motion.js` to v13, `zorp-poses.js` v4 to v5, `motion.css` to v10, `styleguide.js` to v11, `sw.js` to `pb-v102`.
- **Budget:** `POSES_JS_MAX_BYTES` 33,200 to 36,500 (dated ledger entry).
- **Preview:**
  - `phase2/soft-ab-filmstrips.png`: E8 row against E9 row for `hop`, `cheer`, `fist-pump`, `victory`, `dance`, `flex`; 12 frames; 56 and 160 px
  - `phase2/belly-ab.png`
  - `phase2/soft-silhouette.png`
  - perf rerun at 4x CPU throttle: no long task over 50 ms, frame p95 at most 20 ms
- **Done when:** landings read as soft at 56 px in the A/B sheet, nothing detaches, durations are unchanged, and perf targets are met.

**Phase 2 build notes (2026-10-04).**

- **Built:**
  - Markup: `buddy.html` wraps both antennae in `g.zorp-ride`, and the hat in `g.zorp-hatride` only when `look.hat` is set. Plain groups, no pixel change. `findParts` in `zorp-motion.js` (`?v=13`) now also returns `face`, `ride`, `hatRide` and `cheeks`.
  - `zorp-poses.js` (`?v=5`), transforms only: a body layer of `scale(x, y)` at 40 percent of each clip's root squash and stretch, anchored at the feet (y 57.5), so volume is kept. The face, antenna group and hat group only translate by `RIDE x (1 - body sy)` (19.5, 41.5, 43 units), so they stay seated in front and side views and through turns, and the arms (not riders) stay on the shoulders. Jelly after a real landing (root `sy` below 1): three damped body overshoots at +70, +140 and +210 ms, cut short when the next beat starts. Cheek bounce at +60, +130 and +200 ms. Antenna whip: follows each beat's antenna target, then three decaying counter-swings, capped at 16 degrees. Beats that travel 3 units or more with no squash of their own (dance steps, float) get a small body-only stretch and squash.
  - `cheer` and `hop` are rebuilt as soft beat clips (about 760 and 540 ms; legacy 700 and 450, so within 100 ms). Reduced face is `celebrate` for both. The legacy clips stay in `zorp-motion.js` as the fallback when `zorp-poses.js` is missing. Every other big clip (fist-pump, victory, dance, flex, shrug, bow and so on) gets the soft body with the same durations as the Phase 0 table.
  - Reduced and off motion, and `data-motion`, give none of it (the beat engine already ends there). `html[data-zorp-soft="off"]` (set only by `styleguide.js`, `?v=11`, read at compile time) is a dev A/B switch.
  - Dev: `/styleguide#zorp-charm` has a soft body toggle and six clip buttons. `scripts/zorp_gallery_snapshot.py --soft` (or `--soft-only`) writes `soft-ab-filmstrips[-56][-dark].png`, `soft-landing`, `soft-curve`, `soft-silhouette` and `belly-ab` (light and dark) under `data/zorp_gallery/e9-phase2/`.
  - Tests: nine new `zorp_poses_harness.js` scenarios (51 in all; the fake animate now throws on bad offsets, like WAAPI); in `test_zorp_charm_smoke.py`: `test_soft_switch_only_in_styleguide`, `test_belly_not_shipped`, `test_ride_wrappers_markup`, plus the pins and cap. `test_rig_markup`, `test_existing_arm_clips_unchanged` and the E8 budgets are unchanged and green. Pins: `zorp-motion.js` v12 to v13, `zorp-poses.js` v4 to v5, `styleguide.js` v10 to v11, `sw.js` `pb-v101` to `pb-v102`.
- **D4 outcome: dropped.** The 56 and 160 px A/B sheet (`belly-ab.png`) with a pear belly prototype that follows the body scale showed no visible difference from no belly at 56 px, and a small one at 160 px, so the plan's rule ("only if it reads at 56 px") applies. Nothing ships; `test_belly_not_shipped` guards it. `test_belly_inside_body_at_rest` is therefore not written.
- **Ledger:** section 2.1 "Measured (Phase 2)".
- **Deviations from the plan, with the reason:**
  1. `POSES_JS_MAX_BYTES` is 36,500 as planned, but the file measures 35,531 B (plan estimate about 2.6 KB growth; actual 5.3 KB), leaving about 970 B for Phase 4's cue hooks. The reviewer may want a further dated raise then.
  2. `motion.css` is unchanged (`?v=9`, not v10): the riders only translate, so no ride or belly pivots are needed.
  3. The antenna-base gap while whipping measures 0.322 units, against the plan's 0.3, so the harness limit is 0.35 (resolved in review: 0.136, limit 0.3).
  4. The volume rule has a tolerance of 0.002 for the `victory` pose, and the body scale is written at three decimals.
  5. The auto stretch values (up -2.5 and +4.5 percent, down +4.5 and -4.5 percent) were raised from the first values after the sheets showed dance and flex barely differed from E8.
  6. Hop and cheer settle beats are longer than the legacy ones (hop 190 ms, cheer 120 plus 90 hold) so the jelly is not cut off.
  7. The cheek bounce is cut where the jelly window ends and always ends at rest (WAAPI rejects offsets above 1).
  8. `flex` keeps its existing puff, which is exempt from the cheek bounce.
- **Open for the reviewer:** the poses cap headroom (deviation 1); whether the jelly is strong enough at 56 px on dance and flex; the D4 decision.
- **Review (2026-10-04):**
  - **Jelly strength.** The jelly used `w = b_sx - 1`, the body layer's own share of the landing (about 3 percent on `hop`), so the wobble was under a pixel at 56 px and about 2 px at 160 px. `w` is now the drawn landing squash (root times body, capped at 0.12), so the first overshoot on `hop` is about 7 percent (about 2.5 px at 56 px). Every body keyframe stays within 0.075 of 1, inside the 0.08 limit of section 3.2.5, and the drawn body stays within 0.16 with its volume kept. `soft-landing.png` and the 56 px sheets now show it. `dance` and `flex` still differ little from E8: `flex` has no landing (its motion is the arms and the chest puff) and the dance steps are small; left as they are.
  - **Antenna ride (deviation 3 resolved).** The antenna wrapper now follows the body top at the antennae's x (8 units off centre), width included, instead of `41.5 x (1 - sy)`. The widest base-to-body gap over every clip is 0.136 units (0.12 of it at rest), so the harness limit is back to the plan's 0.3.
  - **Tests.** A new `test_body_squash_anchored_at_feet` (`test_zorp_charm_smoke.py`): moving the `.buddy-body` origin off the feet passed every other test. The jelly scenario now checks 0.6 w on both axes against the drawn squash and the 0.075 cap. Mutations (squash limit, detached riders, face lag, soft under reduced, the switch set elsewhere or inverted, legacy `cheer` removed, ride markup removed, jelly or whip removed, `cheer` length) all fail a test.
  - **Checked, no change:** nothing detaches (plate at least 1.7 units inside the body, antenna gap at most 0.14, shoulders at least 3 units inside, hat steady) in front and side views, with and without a hat, light and dark, 56 and 160 px; a clip during a clip, a stop or turn mid-jelly and talk during a soft clip leave no animation or inline transform on the body, face, rides or cheeks; reduced, off, OS reduce and `data-motion` create no soft animation; the legacy `cheer` and `hop` play when `zorp-poses.js` is missing; `--compare e9-baseline` and `--compare baseline` 0 over. The styleguide long tasks at 4x throttle happen with the soft layer on and off and on the Phase 1 tree as well (they come with the page's size, not the soft body); the logged-in home page has none.

### Phase 3: Voice guide, copy pass, enforcing lint (about 3 h plus David's review)

- Rewrite every Zorp-voice line to §3.3, starting from the §3.3.5 drafts. Two confirmed changes ride along: the corner bubble stay label becomes just "Keep learning" (D10, `buddy.py:269`; the topic is already in the message above it), and "100-day streak. Extraordinary." becomes "100-day streak. Amazing." (D11; the new word is also under four syllables).
- Mark the template lines with `data-zorp-voice`. Lint the system-voice strings for the first-person and banned-phrase rules only.
- Switch `test_zorp_voice_smoke.py` to enforcing: `test_banned_phrases`, `test_british_spelling`, `test_practise_verb`, `test_lengths_per_surface`, `test_reading_level`, `test_no_emoji_or_dashes_in_zorp_lines`, `test_exclamation_budget`, `test_system_voice_has_no_first_person`, `test_glossary_terms`, `test_dismiss_labels_neutral`, `test_inventory_doc_in_sync`.
- Update the pins in `test_welcome_smoke.py:292`, `test_buddy_smoke.py:296` and `test_zorp_expression_smoke.py:810`, with the reason in the commit message.
- Add a pointer to §3.3 in the `guide-catalog.js` header and in AI_HANDOFF rule 17.
- **Cache/pins:** `guide-catalog.js` v11 to v12, `guide.js` (if fallbacks change) to v19, `sw.js` to `pb-v103`. Templates and `buddy.py` need no pin.
- **Preview:** `phase3/copy-guide.png` (every line in its panel at 375 px, before and after) and `phase3/copy-diff.md` (old and new side by side).
- **Done when:** David has approved every changed line and the lint is enforcing and green.

**Phase 3 build notes (2026-10-05).**

- **Built:**
  - Voice guide: 3.3.6 (above), with the bot-voice decision.
  - Copy pass, 26 lines changed (Guide lines 8, reward lines 2, corner bubble 9, welcome 1, bot 5, settings 1). The old and new text of each, with the reason, is in `copy-changes.md` (preview, `e9_p3_preview`). The 13 sample rewrites of 3.3.5 are all applied, plus D10 and D11, except that `:142` keeps its opening ("Your streak and XP. If you miss a day, a streak skip can cover it.") so the line still says what the tour is pointing at.
  - Lines the plan did not draft: `:152` "little celebration" became "little cheer" (four syllables); `:255` "solid habit" became "great run of practice"; `buddy.py:232` "Nice, want a quiz" became "Nice work. Want a quiz"; the corner detail label "Weak topic" became "Worth another look" (it labelled the topic as weak in the pupil's own bubble); the bot prompt lost its "!" and its dash-note; "Match my device" in settings became "Match your device" (the system voice has no "my").
  - Extractor (`models/zorp_voice.py`): templates are now read from `data-zorp-voice` attributes (eleven files, the selector list is gone); new sources `models/bot.py`, `study-buddy.js` fallbacks, `notifications.js` toasts, `feed.js` bot note, settings copy, and the welcome headings and skip buttons. 210 items (149 Zorp, 61 system, 19 sources; 178 before).
  - Lint enforcing (`scripts/test_zorp_voice_smoke.py`, 20 tests): banned phrases, warn phrases without `voice-ok`, US spellings (now also in the system voice), the `practise` verb, glossary terms, dismissal labels (neutral wording and an approved list), lengths per surface (limits pinned to 3.3.4), reading level (D11: per line from 8 words, mean 5, long words), emoji and dashes in Zorp lines, the `!` budget, no first person in the system voice, voice-by-source in both directions, the bot voice and note, the welcome promise, guide.js fallbacks against the catalogue, a mutation test that each rule fires on a synthetic bad line, and Appendix A in sync. Today: 0 errors, 0 warnings, mean grade 2.5, highest of 8+ words 7.2, 0 lines with "!".
  - Pins changed on purpose: `test_welcome_smoke.py` (welcome line), `test_buddy_smoke.py` (streak and skip messages), `test_zorp_expression_smoke.py` (streak message, the 100-day line, `pb-v103`), `test_guide_smoke.py` ("There is no chat."), `test_pwa_smoke.py` and `test_zorp_charm_smoke.py` (`pb-v103`). The plan's `:810` pin and the catalogue `:213` pin moved with the copy. Review fixes: the leaderboard page's own "No DMs" now reads "There is no chat." like the Guide line that points at it (`test_guide_smoke.py` pin moved), and the QOTD friends board says "Answered today" instead of "✗ Missed today" for a friend who answered wrongly (it was untrue, since that friend did answer, and it marked a friend's wrong answer with a cross).
  - Docs that quoted copy: `ANIMATION_ONBOARDING.md` (tour lines), `ENGAGEMENT_VISUAL.md` (bot lines), `ZORP_EXPRESSIVENESS.md` (streak line).
- **Pins:** `guide-catalog.js` v11 to v12 (`base.html`, `styleguide.html`), `feed.js` v4 to v5 (`feed.html`), `chrome.css` v45 to v46 (review fix, `text-wrap: pretty` on the Guide bubble), `sw.js` `pb-v102` to `pb-v103`. `guide.js` did not change (its fallbacks already met the rules), so no bump; `buddy.py` and templates need none.
- **Deviations:** (1) `accuracy` is on the long-word allowlist: it is the name of a leaderboard tab, and the line must say it. (2) `:142` keeps its opening, above. (3) The plan's list of safe system strings with a dash or symbol (notifications, answer feedback, offline, settings) is only listed as notes, per 3.3.4 ("first-person and banned-phrase rules only"), so 17 system strings still carry a dash or symbol. (4) The `phase3/` preview folder is `e9_p3_preview`, and the before and after panels are the e9-baseline and e9-phase3 `copy-guide.png`.
- **Checked in Chromium** at 375 px, signed in: Guide origin and tours, reward panels, the five corner bubble types (weak topic with three actions, quiz, both streak lines, friend challenge), `/welcome` in all four steps, settings, `/offline`, and the four empty states: no console error, no horizontal page scroll, no clipped or off-screen text.
- **Open for David:** every changed line (see `copy-changes.md`); "Worth another look" as the detail label; the two review fixes on the leaderboard and QOTD boards. The "chat." orphan at 375 px is fixed by `text-wrap: pretty` on `.guide-bubble`.

### Phase 4: Sound (off by default) (about 3 h)

- **Files:**
  - `sound.js`: cues, gate, arbiter, `cuesActive`, `stopAll`, gesture timestamp, blips (built either way; wired to pupils only if D7 = yes)
  - `zorp-poses.js`: `cue` beats on `fist-pump`, `victory`, `dance`, `flex`, `bow`, `wave`
  - `guide.js`, `zorp-poses.js` react plan: `cue: true` callers
  - `celebrate.js`: the one-sound rule
  - `zorp-talk.js`: blip scheduling
  - `profile_settings.html`: the new `zorp_sound` radio (see D6 below); the sound effects switch keeps covering answer tones only
  - `styleguide.js`: audio preview list
- **D6 = B (confirmed): new `zorp_sound` setting.**
  - Model and validation: `zorp_sound` in the profile settings (values `off`, `celebrations`, `chatter`; default `off`; `chatter` rejected by the PATCH validator until D7 is revisited), mirrored to the page like `motion_preference` (`data-zorp-sound` on `<html>`), read by `pbSound.zorp`.
  - UI: a radio group on `profile_settings.html` under the sound switch: "Zorp's sounds: Off / Celebrations". Copy: "Short, quiet sounds when Zorp celebrates. Best with headphones."
  - Privacy, same commit: ROPA row 1 lists `zorp_sound` beside `theme_preference` and `motion_preference`; both privacy notices; a DPIA row; export includes it; erase removes it.
  - Tests: settings round trip, PATCH validation (rejects `chatter` and junk), default `off` for new and existing users, export check in `test_gdpr_smoke.py`, cues silent when `zorp_sound` is `off` even if `sound_enabled` is on.
- **Settings bug.** Verify the §1.1 switch bug first: Playwright clicks the switch, saves and reloads. If it is still broken, fix it per `AI_HANDOFF.md:36` (native checkbox, in-flow 44 x 26 target) in this phase.
- **Tests:**
  - `test_zorp_sound_smoke.py` (fake `AudioContext` harness):
    - `silent by default`
    - `no context created on load`
    - `no cue without a gesture in the last 5 s`
    - `none in quiz mode`
    - `hidden tab silent`
    - `400 ms arbiter`
    - `one cue per 7 s`
    - `cue gain at most 0.07 and below soft`
    - `blip gain at most 0.035`
    - `durations within the table`
    - `force only from styleguide.js`
    - `confetti silent when cues are active`
  - `test_zorp_charm_smoke.py`: `test_sound_js_budget`, `test_cues_only_from_beat_start`
  - Keep `test_zorp_motion_smoke.py:523-524`
- **Cache/pins:** `sound.js` v3 to v4, `zorp-poses.js` to v6, `guide.js` to v20, `celebrate.js` v10 to v11, `zorp-talk.js` to v2, `styleguide.js` to v12, `sw.js` to `pb-v104`.
- **Preview:** `phase4/audio/` (each cue rendered with `OfflineAudioContext` in headless Chromium to WAV via Python's `wave` module, plus `audio.html` with players, plus peak dBFS and duration per cue).
- **Done when:** cues sound gentle on laptop speakers at mid volume, are silent in every forbidden case, and the switch persists.

**Phase 4 build notes (2026-10-06).**

- **Built:**
  - `zorp_sound` end to end: `models/social.py` (`off` default, `celebrations`, `chatter` defined but never accepted; the normaliser turns anything else into `off`), a startup migration (`TEXT NOT NULL DEFAULT 'off'`, so existing users are off), the form POST, the PATCH validator (400, `invalid_zorp_sound`), `data-zorp-sound` on `<html>`, export and erase.
  - Settings page: a "Zorp's sounds" panel with an Off / Celebrations radio group, after "Sound & feedback", marked as system voice for the copy lint.
  - `sound.js`: `zorp`, `cuesActive`, `blips`, `stopAll`, `arm`; three synthesised cues (jump, land, tada), no audio file, no context before a tap. Rules 1 to 7 of 3.4.3. `force` skips rules 1 and 7 only and is passed only by `styleguide.js`.
  - Cues are scheduled only from the beat engine's `start()` (`zorp-poses.js`), which runs at full motion only, so rule 5 holds by construction. `cue` beats on cheer, fist-pump, victory, dance (hop), flex, wave and bow. Callers pass `cue: true` (`guide.js` reward and story, `welcome.js` card tap).
  - `celebrate.js` stays silent when `cuesActive()` is true; at reduced and off motion, or with Zorp off, the confetti arpeggio plays as before.
  - `zorp-talk.js` schedules the D7 blips, reachable from `styleguide.js` only.
  - Privacy: ROPA row 1, both privacy notices, a DPIA row and the `SECURITY_AND_GDPR.md` preferences row.
- **Settings bug:** not reproducible. Real clicks and taps (desktop and 375 px) save the switch on, off and on again and it survives a reload, so no fix was made. `test_sound_switch_persists` guards the markup.
- **Tests:** `test_zorp_sound_smoke.py` (14 tests, `zorp_sound_harness.js` with a fake `AudioContext`), five new scenarios in `zorp_poses_harness.js`, `test_gdpr_smoke.py` export and erase checks, and the Phase 4 budget and pin checks in `test_zorp_charm_smoke.py`.
- **Deviations:** (1) the `sound.js` cap went 7,000 to 9,900 (ledger). (2) `guide.js` is v19 and `styleguide.js` v12, not v20 and v12 as drafted; each changed file was bumped once from its current value. (3) `zorp-poses.js` and `zorp-talk.js` stay within their caps after trimming comments. (4) A land cue only plays as the follow-up of a jump (or with `force`), so a lone land never sounds.
- **Preview:** `e9_p4_preview` (WAVs rendered offline from the real `sound.js`, `audio.html`, `summary.md`).

### Phase 5: Evaluation kit, tuning, docs (about 2 h plus a class session)

- `docs/ZORP_EVALUATION.md` (§3.5). The `/styleguide#zorp-charm` showreel buttons play, in order: origin line talking, a reward with soft `fist-pump` (and the A/B toggle), a corner bubble talking, sound on and off.
- After the session, apply constant tuning only.
- Docs:
  - `docs/ZORP_EXPRESSIVENESS.md` §10 gains `talk`, `say`, `hush`, `talkPlan`, `cue` and the soft-body notes
  - AI_HANDOFF rule 17 gains "talk and cues only at E9 moments; text first; sound off by default and tap-gated"
  - a DPIA review-log row ("E9: presentation only, sound off by default, evaluation offline and anonymous; std 13")
- **Tests:** `test_showreel_section` (styleguide markup); budgets re-measured.
- **Cache/pins:** `styleguide.js` to v13, plus any file the tuning touches, and `sw.js` to `pb-v105` if a static file changed.
- **Preview:** a filled-in results table and an optional `phase5/showreel.webm`. (Built with the results table blank: see the Phase 5 build notes.)
- **Done when:** the evaluation is recorded, tuning is applied, and the docs are updated.

**Phase 5 build notes (2026-10-06). E9 built; evaluation pending.**

- **The class session has not happened.** So the results table in `docs/ZORP_EVALUATION.md` section 9 is a clearly marked blank template with instructions, no result is invented, and **no tuning was applied**: none of the Phase 1 to 4 review notes flagged a constant as clearly beneficial. After the session, "Done when" is met by recording the dated result and any constant change here, then re-measuring the ledger.
- **Built:**
  - `docs/ZORP_EVALUATION.md`: purpose; the offline, teacher-led rule (D9); who sees what (S1 and S2 projector only, older classes optional accounts); setup; a 15 to 20 minute session plan; the showreel order; six open, reflective sticky-note prompts (David's preference: fun, low-stakes, no test-style items): "What did you think when Zorp cheered?", "Was there a moment Zorp got in the way? Tell us about it.", "When Zorp talked, what did you look at?", "If Zorp could say one sentence when a question goes wrong, what would be kind and helpful?", "If Zorp could do one new thing, what would it be?", "If Zorp made a sound in our classroom, when would that be fun, and when would it be too much?"; a ten-item teacher observation checklist; how to sort notes into themes (E, D, N, C, I, S); the blank results table; decision rules (what counts as encouraging or distracting, success criteria, what to do per pattern); the tuning knobs with names, files, current values and ranges; when to revisit D7 voice blips and the hidden `chatter` setting; privacy; safeguarding (std 13).
  - `docs/zorp_evaluation_print.html`: one A4 pupil prompt sheet and one A4 teacher sheet, inline CSS only, no script, no external asset. Checked as a PDF render in headless Chromium (two pages).
  - `/styleguide#zorp-charm`: a six-button showreel under the six Zorps (`data-showreel`: origin, reward, reward-flat, bubble, sound-on, sound-off). It uses the real caps and clips (1,600 ms origin and reward, 1,200 ms bubble). Step 3 turns the soft body off through the existing A/B toggle, plays the reward, then restores it. Steps 5 and 6 run the forced cue preview (a jump at 110 ms and a land at 620 ms, the fist-pump's take-off and landing) and silence; the cues need full motion, as in the product (D8), and a status line says when motion is limited. `styleguide.js` v13, `data-charm-phase="5"`.
  - Docs: `docs/ZORP_EXPRESSIVENESS.md` section 10 (the `cue` option and `pbSound.zorp`, a paragraph on talk, say, hush, `talkPlan` and cues, a soft-body paragraph); `docs/AI_HANDOFF.md` rule 17, sections 1 and 9; a `docs/DPIA.md` review-log row (presentation only, std 13, evaluation offline and anonymous); this file's status line, ledger and notes.
  - Tests (`scripts/test_zorp_charm_smoke.py`): `test_showreel_section`, `test_evaluation_kit` (docs exist and obey the house style, six open prompts without test-style wording, a blank results table with no invented figures, the print file is self-contained), `test_phase5_docs`, and the Phase 5 pins.
- **Pins:** `styleguide.js` v12 to v13 (`styleguide.html`), `sw.js` `pb-v104` to `pb-v105`. Assertions moved in `test_pwa_smoke.py`, `test_zorp_charm_smoke.py` and `test_zorp_expression_smoke.py`. No other static file changed.
- **Budgets:** section 2.1 "Measured (Phase 5)". No cap raised; `zorp-poses.js` and `zorp-talk.js` are untouched.
- **Previews (`e9_p5_preview`):** `zorp_evaluation_kit.pdf` (the printable kit) and `showreel.webm` (the showreel at full motion; screen recording cannot capture sound).
- **Deviations:** (1) six prompts, not the plan's five, and different wording, per David's open-prompts preference. (2) The print file is `docs/zorp_evaluation_print.html` (the plan did not name a location). (3) The checklist is the plan's ten items, with reduced motion as a note under it. (4) No `phase5/` folder name (as in earlier phases, the folder is `e9_p5_preview`).
- **Final audit fixes (2026-10-12):** a three-auditor review of E9 found the items below; all are fixed, each code fix has a test that fails without it (checked by reverting). Nothing since GitHub `43e387e` is published, so the `?v=` pins E9 already bumped stay as they are; every static file changed here was already changed in E9, so no pin and no `sw.js` `CACHE_VERSION` change (still `pb-v105`).
  - **A1** `zorp-motion.js` `stop()`: when it restores `inst.view` from `inst.home` it ends any talk first (a side-view talk mouth had stayed on a front-facing Zorp after a cut-short side-view clip). Test: `zorp_talk_harness.js` "a cut-short side-view clip ends the talk it carried" (the fake animate can now hold a turn in flight; `.zorp-flip` and `CSS.supports` added to the fake page). `test_zorp_charm_smoke.py` pin: `stop()` touches `inst.talk` only for this.
  - **A2** `sound.js` `playCelebrate()`: when the confetti arpeggio plays it marks the moment (`seq.at`), so the 7 s one-sequence rule blocks a later Zorp cue (repro: `streak:100` reward, arpeggio at +1 s, then jump and land on Continue). Test: `zorp_sound_harness.js` "the confetti arpeggio is the moment's sound" (arpeggio then cue within 7 s is blocked; a silent arpeggio blocks nothing; badge reward is tada only; lesson_complete is still jump and land with no arpeggio).
  - **A3** `zorp-talk.js`: a talk is hushed when the motion level drops below full mid-talk, on the `prefers-reduced-motion` query change and through a `MutationObserver` on `<html>` (`data-motion`, `data-motion-preview`). Test: `zorp_talk_harness.js` "motion dropping mid-talk hushes". Cap `TALK_JS_MAX_BYTES` raised 9,000 to **10,500** (measured 9,550 B, need plus about 10 percent; ledger in 2.1 and the constant's comment).
  - **A4** `welcome.js`: the card tap holds 650 ms (not 450 ms) while `pbSound.cuesActive()` is true, so the land cue (about 620 ms) is not cut; 450 ms otherwise. Test: `test_welcome_smoke.py` `test_card_tap_waits_for_the_land_cue`.
  - **A5** `sound.js` unlock: `pointerup` and `touchend` join `pointerdown` and `keydown` (iPad/WebKit counts the end of a tap as the gesture that may resume audio); all update the same gesture timestamp. Test: `zorp_sound_harness.js` "unlock also listens for pointerup and touchend".
  - **B1** `study-buddy.js` `show()`: no talk for a `streak_risk` prompt (charm never reacts to absence, `DPIA.md:113` and section 5); the bubble still shows. Test: `buddy_gate_harness.js` "Final audit B1" (the E9 Phase 1 talk scenario now uses a `nudge` prompt).
  - **B2** `models/zorp_voice.py` lint: new banned phrases `before midnight`, `tonight`, a streak in the same sentence as reset, end or gone, `ahead of you`, and `behind` (Zorp voice only); `do not worry` joins `don't worry` at warn level; a spaced hyphen counts as a dash; `lose` is banned per sentence and allowed when the sentence names a physics quantity (energy, mass, charge, heat, friction, momentum and so on); the system-voice first-person rule bans only I, me and my (not we, our, us). Tests: `test_zorp_voice_smoke.py` mutation lines for each rule and both false positives; all current copy passes.
  - **B3** `guide-catalog.js:120`: "Check your answer here. I’ll cheer when you get one right." (true to the welcome line and to behaviour). Appendix A regenerated.
  - **B4** `profile_settings.html`: the Zorp sounds intro adds "They play only with full motion."; the two new option labels use colons ("Off: Zorp is silent", "Celebrations: a short sound when Zorp celebrates"). Test: `test_zorp_sound_smoke.py` `test_settings_page_markup_and_copy`.
  - **B5** `profile.html`: the calendar legend says "Skip used" (was "Freeze used"; matches "streak skip"). Test: `test_zorp_voice_smoke.py` `test_glossary_terms`.
  - **C** Docs: the broken table in ZORP_EXPRESSIVENESS section 10 closed up; the real streak string quoted; section 10 and 4.1, 4.2, 4.5 here say the word reveal, tap-to-show-all and belly were not built (D2 = A, D4 dropped) and list talk's full false-conditions; byte-cap locations named; `catalogue` spelling; `docs/API.md` documents `theme_preference`, `motion_preference` and `zorp_sound` on `/api/v1/me/settings`; section 7.2 row 2 says `zorp_sound` is in the user's own settings API only; `ENGAGEMENT_E5.md` "Keep learning" label; `ROPA.md` last reviewed 2026-10-12; `test_zorp_charm_smoke.py` message "version 2" and the redundant `setters` clause dropped.
  - **Outside E9:** O1 `test_es_advanced_downstream_smoke.py` now seeds the RNG per try over 200 seeds (it failed about one run in three with 12 unseeded tries; 30 runs green); O2 `app.py` build-info reads `study_buddy_js` from the `?v=` pin in `base.html` (it said `v11` while the page loaded `v29`; `test_buddy_smoke.py` checks it against `base.html`).

### 6.7 How David previews each phase

1. **Phone first.** The phase report attaches the PNG sheets and WAVs from `python scripts/zorp_gallery_snapshot.py --label phaseN [--talk] [--soft] [--audio] [--copy] [--compare e9-baseline]`. Playwright and Pillow stay optional and outside `requirements.txt`.
2. **Laptop.** `Open Problem Bank.bat`, then `http://127.0.0.1:5001/styleguide#zorp-charm`. The section has:
   - a talk demo with a text box and Guide-line chips
   - the soft A/B and belly toggles
   - the audio preview list
   - the full-motion preview switch (needed when Windows "Animation effects" is off)
   - the 0.25x speed toggle

   `/guide-preview` shows the Guide talking end to end.
3. **Phone against the laptop** (home network only, never at school): E8 §6.9 point 3 unchanged.

---

## 7. Open decisions for David (recommendation first)

| # | Decision | Recommendation | Alternatives |
|---|---|---|---|
| D1 | Mouth-flap technique | **Dedicated talk mouth set** (2 frames plus profile twins), stepped by opacity in a temporary slot | `scaleY` of the mouth slot (a smile only flattens, unreadable at 56 px); swapping parts per flap (DOM churn 8 times a second, fights the expression-swap pop) |
| D2 | Text sync | **A: text at once, mouth talks** (keeps the E6 line reveal and all a11y as today) | B: word reveal at most 1.6 s, origin story only, with a screen-reader span and tap to show all; C: character typewriter (rejected: hard for EAL and dyslexic readers, many spans) |
| D3 | Body deformation | **Transform soft rig**: a body layer anchored at its bottom, with riders | WAAPI path `d` morph (banned by E8 §2 #2; no Safari); animating `rx`/`ry` (patchy browser support, repaints every frame); CSS keyframes (cannot sync with beats) |
| D4 | Pear "belly" layer | **Yes, if the Phase 2 A/B sheet reads at 56 px**; otherwise drop it | Never; always |
| D5 | Re-author `cheer` and `hop` as beat clips so everyday reactions feel soft | **Yes** (legacy versions kept as fallbacks) | Soft body on big clips only |
| D6 | Which setting controls Zorp's cues | **A: the existing `sound_enabled`**, relabelled; no new data | B: a new radio `zorp_sound` (off / celebrations / with chatter), a new stored preference with DPIA rows; C: no Zorp sounds |
| D7 | Voice blips for pupils | **Not in E9.** Build them, preview them on the styleguide, and decide after the evaluation | Ship behind a new opt-in radio now (DPIA, ROPA, notices) |
| D8 | Sound under reduced motion | **No mascot cues** (they belong to the movement); answer tones unchanged | Cues play regardless of motion level |
| D9 | Evaluation | **Teacher-led, offline, anonymous** sticky notes plus a checklist | An in-app anonymous toggle (rejected: new processing, close to analytics) |

### 7.1 Decisions confirmed (2026-10-04)

- **D1:** dedicated talk mouth set (recommended).
- **D2:** A, text appears at once and the mouth talks (recommended). The word reveal is not built.
- **D3:** transform soft rig (recommended).
- **D4:** pear belly only if the Phase 2 A/B sheet reads at 56 px (recommended).
- **D5:** rebuild `cheer` and `hop` as soft beat clips, legacy versions kept as fallbacks (recommended).
- **D6:** **B, a new `zorp_sound` setting** (not the recommendation). It is a new stored preference, so Phase 4 adds the DPIA, ROPA and privacy-notice rows and the export/erase handling. Because of D7, the pupil-facing radio offers only `off` (default) and `celebrations` in E9; the `with chatter` value is defined in code but hidden until the evaluation.
- **D7:** voice blips built and previewed on the styleguide only (recommended).
- **D8:** no Zorp cues under reduced or off motion; answer tones unchanged (recommended).
- **D9:** teacher-led, offline, anonymous evaluation (recommended).
- **D10:** the corner bubble stay label becomes just "Keep learning" (the topic is dropped; it is already in the message above). This settles Phase 0 open question 1. Built in Phase 3 (`buddy.py:269`); the label then fits the 22-character button limit.
- **D11:** the per-line reading-grade limit (8) applies only to lines of 8 words or more. The long-word check and the mean grade across lines (limit 5) still apply to every line. "Extraordinary." becomes "Amazing." in Phase 3 (the line "100-day streak. Amazing."). This settles Phase 0 open question 2. `models/zorp_voice.py` implements it already (`FK_MIN_WORDS_LINE = 8`, report mode); no user-facing copy changed yet.

### 7.2 Feature gate (filled in Phase 0)

Run on 2026-10-04: `python scripts/ops_cadence.py feature-gate` (source `docs/SECURITY_AND_GDPR.md` §6.1; it prints the four questions and takes no input, so the answers are recorded here). Answered against D1 to D9 as confirmed in §7.1, including D6 = B.

| # | Question (as the script prints it) | Answer | Why, in one line |
|---|---|---|---|
| 1 | Does it collect a new category of personal data? If yes, update the ROPA, privacy notice, and retention schedule in the same PR. | **Yes** | D6 = B stores a new display preference, `zorp_sound` (`off` or `celebrations`), beside `theme_preference` and `motion_preference` (precedent `DPIA.md:109`, ROPA row 1); nothing else is collected, and the evaluation is offline (D9). |
| 2 | Does it make anything about a child more visible to anyone else? If yes, it defaults to off. | **No** | Talking, soft body and cues are local presentation; `zorp_sound` stays out of public profiles, the friends views and every API another user can read (checked in Phase 4; it is in the user's own `/api/v1/me/settings` only), and it defaults to off anyway. |
| 3 | Does it send data to a new third party? If yes, subprocessor entry and transfer basis before it ships. | **No** | Oscillator audio and WAAPI only: no audio files, no library, no CDN, no new request, CSP unchanged. |
| 4 | Does it profile, rank, or nudge? If yes, revisit the DPIA section on Children's Code standard 13. | **Yes** | A talking mouth and a celebration sound add salience to reward moments, which is a nudge technique; the §5 rules bind, the copy lint bans loss and guilt framing, and Phase 5 adds the dated DPIA row. |

**Consequence of D6 = B:** the first draft of §6 Phase 0 expected Q1 = no (it assumed D6 = A, "relabel `sound_enabled`"). That expectation is corrected above. Q1 = yes means Phase 4, in the same commit as the setting: ROPA row 1 lists `zorp_sound`; both privacy notices (`templates/legal_privacy.html`, `legal_privacy_simple.html`) name it; a DPIA review-log row; the retention schedule is unchanged (it lives in `user_profile_settings`, deleted with the account); export and erase are tested. No personal-data processing starts before Phase 4. §5 and §6 already say this.

---

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Talking becomes noise | Rationed to the §3.0 moments, 1.2 to 1.6 s caps, never idle, one talker at a time; the evaluation can cut moments by constant |
| A screen-reader regression | Text is synchronous and before any flap; the live region is unchanged; harness `say writes the text synchronously`; accessibility-tree check in the snapshot tool |
| A clip `stop()` killing the talk, or talk leaking after close | Separate `inst.talk` list; hush on every exit path; harness scenarios |
| The soft body detaches the face or antennae, or bloats | Riders share the body's timing; plate and antenna containment tests; stills compared against `e9-baseline` |
| `zorp-poses.js` growth | Dated cap raise in Phase 2; per-phase measurements in the ledger |
| Surprise sound in class | Off by default; 5 s gesture gate; no quiz, load or idle sound; one sound per moment; low gains; settings copy |
| A pupil turns on Zorp's sounds in class | `zorp_sound` defaults to off, the label says headphones, cues are quieter than answer tones and limited to one per 7 s; one tap turns them off |
| The settings switch does not persist (`AI_HANDOFF.md:36`) | Verified and fixed in Phase 4 before relying on it |
| Copy drift after E9 | Enforcing lint plus the inventory-in-sync check on every future change |
| Stale pins (a past source of CI failures) | Every pin listed per phase; suite run on the cloud copy and the laptop; parity check |
| Low-end Chromebooks | Transform and opacity only; one animation per layer; perf pass at 4x throttle in Phase 2 |

## 9. Out of scope

- A full Rive or Lottie rewrite, or any animation or audio library (E7 §2 #12 stands).
- A cast of characters or a second mascot (E6 §2 #1, E7 §2 #13).
- Push notifications (E5.7, blocked on M5).
- Text to speech or recorded voice.
- Lip sync to audio.
- A pupil-facing personality picker.
- A "Zorp talks less" setting (revisit after the evaluation).
- E8 Phase 6 (pose-kit parity), which stays independent.

---

## Appendix A. Copy inventory (generated in Phase 0 between markers; summary at 43e387e)

<!--COPY-INVENTORY-BEGIN-->
Generated by `python scripts/test_zorp_voice_smoke.py --write` from `models/zorp_voice.py`. Do not edit by hand: `test_inventory_doc_in_sync` fails when the copy drifts (line numbers alone may lag; `--write` refreshes them). Sources: JavaScript by regex, Python by `ast`, templates by `data-zorp-voice`. F-strings are rendered with sample values (topic label of 30 characters). `FK` is the Flesch-Kincaid grade of a line (section 3.3.4); labels have none.

| Source | Voice | Items |
|---|---|---|
| `static/js/guide-catalog.js` | Zorp | 90: 24 guide lines, 7 reward lines, 44 button labels, 13 tour spot labels, 2 headings |
| `static/js/guide.js` | Zorp | 13: 3 reward lines, 4 button labels, 6 headings |
| `static/js/study-buddy.js` | Zorp | 4: 3 button labels, 1 bubble detail label |
| `models/buddy.py` | Zorp | 23: 10 corner messages, 8 button labels, 5 bubble detail labels |
| `models/bot.py` | System | 4: 1 bot note, 3 bot cards |
| `templates/base.html` | System | 8: 3 button labels, 4 pwa banners, 1 tab badge label |
| `templates/base.html` | Zorp | 4: 4 button labels |
| `templates/follow_list.html` | System | 4: 1 button label, 3 empty states |
| `templates/leaderboard_friends.html` | System | 6: 2 button labels, 4 empty states |
| `templates/offline.html` | System | 2: 1 button label, 1 offline page |
| `templates/partials/guide.html` | Zorp | 4: 2 button labels, 1 bot note, 1 heading |
| `templates/profile_settings.html` | System | 11: 11 settings copys |
| `templates/public_profile.html` | System | 1: 1 bot note |
| `templates/qotd.html` | System | 5: 1 button label, 4 empty states |
| `templates/saved_problems.html` | System | 3: 1 button label, 2 empty states |
| `templates/welcome.html` | Zorp | 11: 5 button labels, 6 welcome lines |
| `app.py` | System | 8: 8 notifications |
| `static/js/notifications.js` | System | 3: 3 toasts |
| `static/js/feed.js` | System | 1: 1 bot note |
| `static/js/site.js` | System | 8: 8 answer feedbacks |

**Status (the lint is enforcing since Phase 3; the numbers below are limits that now hold):**

- Zorp lines: 51. Flesch-Kincaid grade: mean 2.5 (limit 5), pooled 2.3, highest 7.4; highest among lines of 8 words or more 7.2 (limit 8, D11).
- Lines with a "!": 0 of 51 (0%; limit 25%).
- Guide line: longest 88 characters (limit 100), 0 over.
- Reward line: longest 55 characters (limit 80), 0 over.
- Corner message: longest 90 characters (limit 100), 0 over.
- Button label: longest 14 characters (limit 22), 0 over.
- Bubble detail label: longest 18 characters (limit 20), 0 over.
- Welcome line: longest 61 characters (limit 70), 0 over.
- Rule hits: 0 errors and 0 warnings (any of either fails `scripts/test_zorp_voice_smoke.py`); 17 notes (a dash or symbol in a system string, listed only).

| Ref | Voice | Surface | Chars | FK | Text |
|---|---|---|---|---|---|
| `static/js/guide-catalog.js:16` | Zorp | Guide line | 63 | 4.0 | A bit about me: I’m Zorp, from Novara, out past the maths belt. |
| `static/js/guide-catalog.js:17` | Zorp | Guide line | 71 | 5.8 | Novara sent helpers to Earth to make maths and physics feel less scary. |
| `static/js/guide-catalog.js:21` | Zorp | Button label | 8 |  | Continue |
| `static/js/guide-catalog.js:22` | Zorp | Button label | 10 |  | Skip intro |
| `static/js/guide-catalog.js:29` | Zorp | Guide line | 47 | 0.7 | Those little aliens you’ll see? That’s my crew. |
| `static/js/guide-catalog.js:30` | Zorp | Guide line | 51 | 0.5 | I’m the one in the corner. I’m a bot, not a person. |
| `static/js/guide-catalog.js:34` | Zorp | Button label | 8 |  | Continue |
| `static/js/guide-catalog.js:35` | Zorp | Button label | 10 |  | Skip intro |
| `static/js/guide-catalog.js:44` | Zorp | Guide line | 67 | 1.5 | Novara is a long way from here. I do think about home now and then. |
| `static/js/guide-catalog.js:45` | Zorp | Guide line | 74 | 3.9 | But Earth has plenty of good problems to work on, and I’m glad to be here. |
| `static/js/guide-catalog.js:48` | Zorp | Button label | 8 |  | Continue |
| `static/js/guide-catalog.js:49` | Zorp | Button label | 10 |  | Skip intro |
| `static/js/guide-catalog.js:56` | Zorp | Guide line | 78 | 4.7 | I’ll cheer when you earn a badge, and nudge you if a topic needs another look. |
| `static/js/guide-catalog.js:57` | Zorp | Guide line | 27 | 0.5 | You can always tap Not now. |
| `static/js/guide-catalog.js:61` | Zorp | Button label | 8 |  | Continue |
| `static/js/guide-catalog.js:62` | Zorp | Button label | 10 |  | Skip intro |
| `static/js/guide-catalog.js:70` | Zorp | Guide line | 28 | 2.9 | This site is for practising. |
| `static/js/guide-catalog.js:71` | Zorp | Guide line | 54 | 7.4 | Bottom tabs: Practice, Learn, Daily, Compete, Profile. |
| `static/js/guide-catalog.js:74` | Zorp | Button label | 8 |  | Continue |
| `static/js/guide-catalog.js:75` | Zorp | Button label | 10 |  | Skip intro |
| `static/js/guide-catalog.js:83` | Zorp | Guide line | 72 | 1.5 | Ready when you are. You can skip this any time, and it won’t show again. |
| `static/js/guide-catalog.js:86` | Zorp | Button label | 8 |  | Let’s go |
| `static/js/guide-catalog.js:87` | Zorp | Button label | 10 |  | Skip intro |
| `static/js/guide-catalog.js:98` | Zorp | Tour spot label | 16 |  | The topic picker |
| `static/js/guide-catalog.js:99` | Zorp | Guide line | 48 | 5.2 | Pick a subject and topic, then Start practising. |
| `static/js/guide-catalog.js:100` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:101` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:108` | Zorp | Tour spot label | 10 |  | Difficulty |
| `static/js/guide-catalog.js:109` | Zorp | Guide line | 88 | 3.0 | Choose how hard the question is. For GCSE you can also pick Standard or Multiple Choice. |
| `static/js/guide-catalog.js:110` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:111` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:119` | Zorp | Tour spot label | 17 |  | Check your answer |
| `static/js/guide-catalog.js:120` | Zorp | Guide line | 58 | -0.6 | Check your answer here. I’ll cheer when you get one right. |
| `static/js/guide-catalog.js:121` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:122` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:130` | Zorp | Tour spot label | 30 |  | The Practice tab at the bottom |
| `static/js/guide-catalog.js:131` | Zorp | Guide line | 64 | 2.6 | This tab is home. The others are Learn, Daily, Compete, Profile. |
| `static/js/guide-catalog.js:132` | Zorp | Button label | 6 |  | Got it |
| `static/js/guide-catalog.js:133` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:142` | Zorp | Tour spot label | 13 |  | Streak and XP |
| `static/js/guide-catalog.js:143` | Zorp | Guide line | 66 | -0.1 | Your streak and XP. If you miss a day, a streak skip can cover it. |
| `static/js/guide-catalog.js:144` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:145` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:152` | Zorp | Tour spot label | 6 |  | Badges |
| `static/js/guide-catalog.js:153` | Zorp | Guide line | 45 | 1.9 | Badges you earn. New ones get a little cheer. |
| `static/js/guide-catalog.js:154` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:155` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:162` | Zorp | Tour spot label | 18 |  | Revision and saved |
| `static/js/guide-catalog.js:163` | Zorp | Guide line | 49 | 5.2 | Saved questions and your revision plan live here. |
| `static/js/guide-catalog.js:164` | Zorp | Button label | 6 |  | Got it |
| `static/js/guide-catalog.js:165` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:175` | Zorp | Tour spot label | 16 |  | Today’s question |
| `static/js/guide-catalog.js:176` | Zorp | Guide line | 45 | 6.7 | A new question every day, whenever suits you. |
| `static/js/guide-catalog.js:177` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:178` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:185` | Zorp | Tour spot label | 17 |  | The friends board |
| `static/js/guide-catalog.js:186` | Zorp | Guide line | 69 | 1.5 | Friends can see the week board. There is no public worldwide ranking. |
| `static/js/guide-catalog.js:187` | Zorp | Button label | 6 |  | Got it |
| `static/js/guide-catalog.js:188` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:198` | Zorp | Tour spot label | 14 |  | The topic list |
| `static/js/guide-catalog.js:199` | Zorp | Guide line | 72 | 2.3 | Lessons and quizzes live here. Open a topic to read, then take the quiz. |
| `static/js/guide-catalog.js:200` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:201` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:208` | Zorp | Tour spot label | 13 |  | Level filters |
| `static/js/guide-catalog.js:209` | Zorp | Guide line | 59 | 4.8 | Filter by GCSE, A-Level, or MYP if you want a shorter list. |
| `static/js/guide-catalog.js:210` | Zorp | Button label | 6 |  | Got it |
| `static/js/guide-catalog.js:211` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:220` | Zorp | Tour spot label | 19 |  | Effort and accuracy |
| `static/js/guide-catalog.js:221` | Zorp | Guide line | 66 | 6.9 | This is friends only. Accuracy and effort among people you follow. |
| `static/js/guide-catalog.js:222` | Zorp | Button label | 4 |  | Next |
| `static/js/guide-catalog.js:223` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:231` | Zorp | Tour spot label | 10 |  | Challenges |
| `static/js/guide-catalog.js:232` | Zorp | Guide line | 42 | 4.3 | Challenges are optional. There is no chat. |
| `static/js/guide-catalog.js:233` | Zorp | Button label | 6 |  | Got it |
| `static/js/guide-catalog.js:234` | Zorp | Button label | 7 |  | Not now |
| `static/js/guide-catalog.js:242` | Zorp | Reward line | 16 | 1.3 | You earned this. |
| `static/js/guide-catalog.js:243` | Zorp | Button label | 5 |  | Close |
| `static/js/guide-catalog.js:249` | Zorp | Reward line | 41 | -0.7 | 7-day streak. Nice work keeping it going. |
| `static/js/guide-catalog.js:250` | Zorp | Button label | 5 |  | Close |
| `static/js/guide-catalog.js:256` | Zorp | Reward line | 46 | -0.8 | 30-day streak. That’s a great run of practice. |
| `static/js/guide-catalog.js:257` | Zorp | Button label | 5 |  | Close |
| `static/js/guide-catalog.js:265` | Zorp | Reward line | 24 | 4.7 | 100-day streak. Amazing. |
| `static/js/guide-catalog.js:265` | Zorp | Reward line | 51 | 1.7 | I’m a little teary, in the happiest way. Well done. |
| `static/js/guide-catalog.js:266` | Zorp | Button label | 8 |  | Continue |
| `static/js/guide-catalog.js:273` | Zorp | Heading | 13 |  | First correct |
| `static/js/guide-catalog.js:274` | Zorp | Reward line | 55 | 1.9 | Nice. I’ll celebrate this first one, then stay quieter. |
| `static/js/guide-catalog.js:275` | Zorp | Button label | 5 |  | Close |
| `static/js/guide-catalog.js:282` | Zorp | Heading | 15 |  | Lesson complete |
| `static/js/guide-catalog.js:283` | Zorp | Reward line | 46 | 0.7 | Well done. Practise or quiz when you’re ready. |
| `static/js/guide-catalog.js:284` | Zorp | Button label | 5 |  | Close |
| `static/js/guide.js:523` | Zorp | Reward line | 16 | 1.3 | You earned this. |
| `static/js/guide.js:539` | Zorp | Reward line | 41 | -0.7 | {n}-day streak. Nice work keeping it going. |
| `static/js/guide.js:556` | Zorp | Reward line | 10 | -3.0 | Well done. |
| `static/js/guide.js:492` | Zorp | Heading | 9 |  | New badge |
| `static/js/guide.js:538` | Zorp | Heading | 12 |  | {n}-day streak |
| `static/js/guide.js:555` | Zorp | Heading | 13 |  | First correct |
| `static/js/guide.js:555` | Zorp | Heading | 15 |  | Lesson complete |
| `static/js/guide.js:588` | Zorp | Heading | 9 |  | Well done |
| `static/js/guide.js:588` | Zorp | Heading | 4 |  | Zorp |
| `static/js/guide.js:524` | Zorp | Button label | 5 |  | Close |
| `static/js/guide.js:540` | Zorp | Button label | 5 |  | Close |
| `static/js/guide.js:557` | Zorp | Button label | 5 |  | Close |
| `static/js/guide.js:594` | Zorp | Button label | 8 |  | Continue |
| `static/js/study-buddy.js:260` | Zorp | Bubble detail label | 5 |  | Buddy |
| `static/js/study-buddy.js:266` | Zorp | Button label | 4 |  | Open |
| `static/js/study-buddy.js:275` | Zorp | Button label | 4 |  | Open |
| `static/js/study-buddy.js:294` | Zorp | Button label | 7 |  | Not now |
| `models/buddy.py:191` | Zorp | Corner message | 41 | 4.0 | Challenge @{handle} to today's topic? |
| `models/buddy.py:192` | Zorp | Bubble detail label | 16 |  | Friend challenge |
| `models/buddy.py:195` | Zorp | Button label | 14 |  | Send challenge |
| `models/buddy.py:211` | Zorp | Corner message | 90 | 4.6 | {topic_label} could use another look. A few questions will help it stick. |
| `models/buddy.py:212` | Zorp | Bubble detail label | 18 |  | Worth another look |
| `models/buddy.py:217` | Zorp | Button label | 13 |  | Practise this |
| `models/buddy.py:222` | Zorp | Button label | 13 |  | Practise this |
| `models/buddy.py:232` | Zorp | Corner message | 85 | 3.1 | Nice work on {topic_label}. A few more questions will help it stick. |
| `models/buddy.py:232` | Zorp | Corner message | 76 | 2.3 | Nice work. Want a quiz on {topic_label} to check it sticks? |
| `models/buddy.py:238` | Zorp | Corner message | 63 | 7.2 | Try a few practice questions on {topic_label}. |
| `models/buddy.py:238` | Zorp | Corner message | 89 | 6.3 | Try a few questions on {topic_label}, or take a quiz to check it sticks. |
| `models/buddy.py:247` | Zorp | Button label | 12 |  | Practise MCQ |
| `models/buddy.py:255` | Zorp | Button label | 11 |  | Take a quiz |
| `models/buddy.py:269` | Zorp | Button label | 13 |  | Keep learning |
| `models/buddy.py:276` | Zorp | Bubble detail label | 18 |  | Worth another look |
| `models/buddy.py:343` | Zorp | Corner message | 50 | 5.0 | Nice work: {score}/{total} on {topic_label}. |
| `models/buddy.py:345` | Zorp | Corner message | 68 | 5.4 | Quiz done on {topic_label}: {score}/{total}. Fancy another go? |
| `models/buddy.py:349` | Zorp | Bubble detail label | 12 |  | Today’s quiz |
| `models/buddy.py:354` | Zorp | Button label | 14 |  | Practise again |
| `models/buddy.py:365` | Zorp | Corner message | 77 | 0.7 | You have a streak skip this week, so no rush. One quick question also counts. |
| `models/buddy.py:368` | Zorp | Corner message | 65 | -0.5 | You’re on a {days}-day streak. One quick question counts, if you like. |
| `models/buddy.py:372` | Zorp | Bubble detail label | 15 |  | Streak reminder |
| `models/buddy.py:374` | Zorp | Button label | 13 |  | Browse topics |
| `models/bot.py:11` | System | Bot card | 45 |  | The Problem Bank bot has a challenge for you. |
| `models/bot.py:12` | System | Bot card | 44 |  | You took today's Problem Bank bot challenge. |
| `models/bot.py:64` | System | Bot card | 15 |  | Daily challenge |
| `models/bot.py:75` | System | Bot note | 33 |  | A Problem Bank bot, not a person. |
| `templates/base.html:261` | System | PWA banner | 20 |  | Install Problem Bank |
| `templates/base.html:262` | System | PWA banner | 55 |  | Add to your home screen for quicker practice on mobile. |
| `templates/base.html:265` | System | Button label | 7 |  | Install |
| `templates/base.html:266` | System | Button label | 7 |  | Not now |
| `templates/base.html:271` | System | PWA banner | 18 |  | Add to Home Screen |
| `templates/base.html:272` | System | PWA banner | 62 |  | Tap Share, then “Add to Home Screen” for an app-like shortcut. |
| `templates/base.html:275` | System | Button label | 6 |  | Got it |
| `templates/base.html:312` | Zorp | Button label | 4 |  | Open |
| `templates/base.html:316` | Zorp | Button label | 7 |  | Not now |
| `templates/base.html:318` | Zorp | Button label | 4 |  | Open |
| `templates/base.html:319` | Zorp | Button label | 7 |  | Not now |
| `templates/base.html:353` | System | Tab badge label | 40 |  | A quick question keeps your streak going |
| `templates/follow_list.html:34` | System | Empty state | 20 |  | No users to show yet |
| `templates/follow_list.html:36` | System | Empty state | 48 |  | When someone follows Sam, they will appear here. |
| `templates/follow_list.html:38` | System | Empty state | 71 |  | Find other learners and follow them to see their activity in your feed. |
| `templates/follow_list.html:40` | System | Button label | 11 |  | Find people |
| `templates/leaderboard_friends.html:77` | System | Empty state | 20 |  | No accuracy data yet |
| `templates/leaderboard_friends.html:78` | System | Empty state | 62 |  | Follow people and complete quizzes to compare weekly accuracy. |
| `templates/leaderboard_friends.html:79` | System | Button label | 12 |  | Find friends |
| `templates/leaderboard_friends.html:117` | System | Empty state | 28 |  | Start competing with friends |
| `templates/leaderboard_friends.html:118` | System | Empty state | 39 |  | Follow people to compare weekly effort. |
| `templates/leaderboard_friends.html:119` | System | Button label | 12 |  | Find friends |
| `templates/offline.html:14` | System | Offline page | 47 |  | No signal here — your saved lessons still work. |
| `templates/offline.html:15` | System | Button label | 9 |  | Try again |
| `templates/partials/guide.html:9` | Zorp | Heading | 4 |  | Zorp |
| `templates/partials/guide.html:11` | Zorp | Bot note | 33 | 2.3 | A Problem Bank bot, not a person. |
| `templates/partials/guide.html:14` | Zorp | Button label | 8 |  | Continue |
| `templates/partials/guide.html:15` | Zorp | Button label | 10 |  | Skip intro |
| `templates/profile_settings.html:174` | System | Settings copy | 89 |  | Less motion — calmer animations. Applies across practice, lessons, and the installed app. |
| `templates/profile_settings.html:179` | System | Settings copy | 62 |  | Match your device — follow your device's reduce-motion setting |
| `templates/profile_settings.html:184` | System | Settings copy | 40 |  | Less motion — calmer, minimal animations |
| `templates/profile_settings.html:189` | System | Settings copy | 19 |  | Off — no animations |
| `templates/profile_settings.html:198` | System | Settings copy | 99 |  | Short correct/incorrect sounds when you check answers. Off by default — useful in class when muted. |
| `templates/profile_settings.html:200` | System | Settings copy | 111 |  | Toggle on, then tap Check on a practice question to hear feedback. A short preview plays when you turn this on. |
| `templates/profile_settings.html:207` | System | Settings copy | 96 |  | Short, quiet sounds when Zorp celebrates. Best with headphones. They play only with full motion. |
| `templates/profile_settings.html:212` | System | Settings copy | 19 |  | Off: Zorp is silent |
| `templates/profile_settings.html:217` | System | Settings copy | 48 |  | Celebrations: a short sound when Zorp celebrates |
| `templates/profile_settings.html:226` | System | Settings copy | 116 |  | Zorp’s origin story plays once. Replay it if you want to see it again — tours you have already skipped stay skipped. |
| `templates/profile_settings.html:228` | System | Settings copy | 49 |  | Replay welcome shows the first-day screens again. |
| `templates/public_profile.html:15` | System | Bot note | 33 |  | A Problem Bank bot, not a person. |
| `templates/qotd.html:101` | System | Empty state | 27 |  | No friends on the board yet |
| `templates/qotd.html:102` | System | Empty state | 43 |  | Follow classmates to compare daily answers. |
| `templates/qotd.html:103` | System | Button label | 12 |  | Find friends |
| `templates/qotd.html:126` | System | Empty state | 22 |  | Be the first to answer |
| `templates/qotd.html:127` | System | Empty state | 56 |  | Submit today's question, then invite friends to compete. |
| `templates/saved_problems.html:38` | System | Empty state | 22 |  | No saved questions yet |
| `templates/saved_problems.html:39` | System | Empty state | 62 |  | Save a question from the generator to practise it again later. |
| `templates/saved_problems.html:40` | System | Button label | 15 |  | Go to generator |
| `templates/welcome.html:30` | Zorp | Welcome line | 13 | -2.6 | Hi, I’m Zorp. |
| `templates/welcome.html:31` | Zorp | Welcome line | 45 | 1.3 | I live in Problem Bank and I’ll cheer you on. |
| `templates/welcome.html:40` | Zorp | Button label | 12 |  | Skip for now |
| `templates/welcome.html:46` | Zorp | Welcome line | 29 | 0.5 | What do you want to practise? |
| `templates/welcome.html:61` | Zorp | Button label | 12 |  | Skip for now |
| `templates/welcome.html:67` | Zorp | Welcome line | 18 | 0.7 | Pick a first topic |
| `templates/welcome.html:81` | Zorp | Button label | 11 |  | Surprise me |
| `templates/welcome.html:88` | Zorp | Button label | 12 |  | Skip for now |
| `templates/welcome.html:94` | Zorp | Welcome line | 12 | 2.9 | You’re ready |
| `templates/welcome.html:96` | Zorp | Welcome line | 61 | 0.5 | Get one right and I’ll cheer. Finish a lesson and I’ll dance. |
| `templates/welcome.html:110` | Zorp | Button label | 12 |  | Skip for now |
| `app.py:3998` | System | Notification | 67 |  | @{handle} sent you a question on {topic} |
| `app.py:4002` | System | Notification | 35 |  | @{handle} started following you |
| `app.py:4007` | System | Notification | 72 |  | @{handle} challenged you to a quiz on {topic} |
| `app.py:4013` | System | Notification | 41 |  | Challenge complete — {cs}/{os_} vs @{payload.get('opponent_handle', 'friend')} |
| `app.py:4017` | System | Notification | 45 |  | @{handle} invited you to be study buddies |
| `app.py:4031` | System | Notification | 48 |  | @{handle} invited you to join {class_name} |
| `app.py:4038` | System | Notification | 25 |  | New badge: {title} {emoji} |
| `app.py:4041` | System | Notification | 16 |  | New notification |
| `static/js/notifications.js:226` | System | Toast | 22 |  | Study buddy connected! |
| `static/js/notifications.js:231` | System | Toast | 15 |  | Invite ignored. |
| `static/js/notifications.js:243` | System | Toast | 36 |  | Could not update study buddy invite. |
| `static/js/feed.js:69` | System | Bot note | 33 |  | A Problem Bank bot, not a person. |
| `static/js/site.js:987` | System | Answer feedback | 10 |  | ✓ Correct! |
| `static/js/site.js:1006` | System | Answer feedback | 48 |  | ✗ Not quite — the correct answer is highlighted. |
| `static/js/site.js:1155` | System | Answer feedback | 8 |  | Correct! |
| `static/js/site.js:1166` | System | Answer feedback | 22 |  | Not quite — try again. |
| `static/js/site.js:3467` | System | Answer feedback | 10 |  | ✓ Correct! |
| `static/js/site.js:3485` | System | Answer feedback | 48 |  | ✗ Not quite — the correct answer is highlighted. |
| `static/js/site.js:3643` | System | Answer feedback | 10 |  | ✓ Correct! |
| `static/js/site.js:3660` | System | Answer feedback | 10 |  | Not quite. |
<!--COPY-INVENTORY-END-->
