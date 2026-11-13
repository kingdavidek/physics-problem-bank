# Celebration sounds: a small sound library (plan)

2026-11-13. Planned, then built the same day after David's answers (section 6.1). What was built is in section 7; nothing is committed yet.

The goal: the celebrations and badges get short, pleasant sounds, from a small library of named sounds. It stays quiet and safe for a classroom.

---

## 1. What exists today

- **One sound module.** `static/js/sound.js` (`window.pbSound`) builds every sound in the browser from WebAudio oscillators. It uses no audio files (E7 section 2 #9), so:
  - there is nothing to license;
  - no CSP change (`media-src`) is needed;
  - there is nothing to download or precache;
  - it works offline.
- **Two settings** (Settings, "Sound & feedback"):
  - **Sound effects** (`sound_enabled`, on for new accounts): the tones for a right or wrong answer, and the small arpeggio with answer confetti.
  - **Zorp's sounds** (`zorp_sound`): with "Celebrations", Zorp's moves on a stage make three tiny cues (`jump`, `land`, `tada`). New accounts start on "Celebrations" (since E10, `apply_new_account_defaults`); accounts made before E10 keep the value they had, usually Off. (The first version of this plan said off by default; that was wrong.)
- **The rules for Zorp's cues** (`docs/ZORP_CHARM.md` 3.4.3):
  - a tap or key in the last 5 seconds;
  - the page is visible;
  - never on a quiz question page;
  - full motion only;
  - 400 ms between any two sounds, and at most one cue sequence every 7 seconds;
  - peak gain 0.06; the answer tones go up to 0.14.
- **So today** the badge stage, the 10/10, the level-up, Lesson complete, Your week, the streak rounds, the story and the corner cards make no sound of their own. Only Zorp's jump and land can sound, for pupils who chose Celebrations.

---

## 2. The library

About 14 named sounds, all made in code as today, with no files. Three new building blocks give them more character than plain tones:
- a short noise buffer, made in code, for airy and fizzy sounds;
- a filter;
- a gentle echo, made with a delay node.

| Sound | Sounds like | Length | Peak gain |
|---|---|---|---|
| `whoosh` | a soft sweep of air as a stage opens | 0.3 s | 0.04 |
| `stamp-bronze`, `stamp-silver`, `stamp-gold`, `stamp-violet` | a medal landing: a warm thud and a chime, brighter tier by tier; violet adds a shimmer | 0.5 to 0.9 s | 0.06 to 0.08 |
| `sparkle` | three tiny high pings, the twinkles | 0.4 s | 0.03 |
| `confetti` | a short, light fizz | 0.35 s | 0.03 |
| `gem` | the 10/10: a rising, glassy four-note run | 0.7 s | 0.08 |
| `level` | level up: a run that climbs with the ring, then a bright chord | 1.2 s | 0.08 |
| `book` | Lesson complete: a soft book thump, then a tick chime | 0.6 s | 0.06 |
| `sprout` | the Recovery badges: a little rising glide | 0.5 s | 0.05 |
| `fire` | the streaks: a warm swell | 0.7 s | 0.05 |
| `week` | Your week: one soft note per card, rising across the three | 0.25 s each | 0.05 |
| `story` | a story chapter opens: a short music-box phrase | 1 s | 0.05 |
| `pop` | a corner card (if decision 3 says yes) | 0.08 s | 0.03 |

Nothing is louder than 0.08, the gain of today's quietest answer tone (`soft`). Celebrations should feel warm, not loud.

**Where it lives.**
- A new `static/js/sound-library.js`, loaded only with the stage (like `moments.js`), so ordinary pages carry no extra bytes. It uses `pbSound`'s audio context and its shared volume node, so `pbSound.stopAll()` cuts everything at once.
- `pbSound` gains `play(name, { force })`.

---

## 3. What plays when

| Moment | Sound |
|---|---|
| a badge stage | `whoosh` as it opens; the medal's `stamp-<tier>` as it lands; a family touch after it: `sparkle` (Full marks line), `sprout` (Recovery), `fire` (streaks) |
| a sequence ("1 of 3") | each card's own sound as that card appears; Skip all, Continue past the end, or Escape stops the sound at once |
| the 10/10 | `gem` as the seal lands, `confetti` with the burst |
| level up | `level`, timed with the ring |
| Lesson complete | `book` |
| Your week | `week`, one note per card |
| the 7-, 30- and 100-day streaks | `fire`, then the tier stamp; at 100, the violet shimmer |
| a story chapter | `story` as it opens |
| a corner card | silent, or `pop` (decision 3) |
| Watch again (profile) | the badge's sounds, as when it was earned |

**One layer at a time.** While a scene's sound plays, Zorp's own jump and land cues are held back, so two sounds never stack. The 400 ms gap between sounds stays.

---

## 4. Rules (a classroom app)

- **The default** (decision 6): on for new accounts, which was already the case for Zorp's sounds since E10. Older accounts keep their choice.
- **The same gates as Zorp's cues:** a tap or key in the last 5 seconds, a visible page, never on a quiz question page, and a hidden tab stops all sound.
- **A browser limit.** Browsers do not let a page play sound before the pupil touches it.
  - A celebration that arrives after a tap on the same page (an answer check, a lesson quick check, Watch again) plays with sound straight away.
  - A celebration that opens with a new page (the quiz results after submitting) starts silent, and the cards after the first Continue have sound.
  - Nothing can change this, and the plan does not try to.
- **Reduced motion:** decision 4.
- **A mute button on the stage:** decision 5. It saves the setting, so it holds on every page.
- **Settings copy** says plainly that the sounds are best with headphones or at home.

---

## 5. Phases

| Phase | What | Size |
|---|---|---|
| **S1. The library** | `sound-library.js` with the sounds of section 2, `pbSound.play(name)`, tests (every sound defined; gains and lengths within the caps; no audio files and no `media-src`), and a Sounds section on the celebrations gallery to audition each one | small |
| **S2. The wiring** | the badge stage (by tier and family), the moments (10/10, level up, Lesson complete, Your week), the streak rounds, the story, the cards if chosen; stop on Skip all, Escape or a hidden tab; Zorp's cues held during a scene sound; a "with sound" switch on the gallery; tests that record which sound each moment asks for, and when | medium |
| **S3. Polish** | the stage mute button (if chosen), the settings copy, and gain changes after David listens (and after a class session, if he runs one) | small |

**Testing.** A headless browser cannot judge how a sound sounds. The tests check:
- which sound each moment asks for, and when;
- that nothing plays when it should not (setting off, no tap, a question page, a hidden tab);
- the gains and lengths.

David listens on the gallery, where every sound and every celebration can be played.

---

## 6. Decisions for David

1. **Made in code or recorded files.** Sounds made in code, as today (recommended: no licensing, no CSP change, nothing to download, works offline), or a few small recorded files (richer, but each needs a free licence, a CSP change, extra bytes and offline caching)?
2. **Which setting turns them on.** Options:
   - Zorp's sounds, "Celebrations" (recommended: one switch, already named for this; its line would read "Short sounds when you earn a badge and when Zorp celebrates");
   - a new, third setting.
3. **Corner cards.** Silent (recommended: they are frequent), or a very soft `pop`?
4. **Reduced motion.** Silent, as Zorp's cues are today, or one soft sound per moment (recommended: sound is not motion, and the pupil chose to hear it)?
5. **A mute button on the stage.** Yes (recommended: one tap for quiet in class), or no?
6. **The default.** Off for every account, or on for new accounts, as Sound effects is? (Asked as if the setting were off by default. It is not: new accounts have started on "Celebrations" since E10, so "on for new accounts" keeps today's behaviour.)

### 6.1 David's answers (2026-11-13)

1. Made in code, as today.
2. The Zorp's sounds setting, reworded to cover the badges.
3. Corner cards get a soft `pop`.
4. Reduced motion: one soft sound per celebration.
5. A mute button on the stage: yes.
6. On for new accounts (already true since E10, see section 1).

---

## 7. Built (2026-11-13, not committed)

**The library.** `static/js/sound-library.js` (new, 6,924 B, own cap 7,500 in `scripts/test_celebration_sounds_smoke.py`), `window.pbSoundLib`:
- the 15 sounds of section 2, made from tones, a noise burst made in code, and a filter;
- no echo: the delay node of section 2 was left out, since the short sounds did not need it;
- every voice at most 0.08, every moment's loudest instant at most 0.1 (the sum of the voices sounding at once; the worst is 0.098), every sound under 1.8 s;
- loaded by `sound.js` the first time a sound may play (its URL is on `<html data-pb-sound-lib>`); `pbSound.prepare()` starts the load when the stage script loads, so ordinary pages carry no extra bytes.

**`pbSound.play(name, o)`** in `sound.js` (v5; cap raised 9,900 to 13,600, 12,418 B):
- the rules of section 4: the setting, a tap or key in the last 5 s, a visible page, never a question page (a quiz results page may sound);
- 400 ms after any other sound, unless `o.chain` (a later layer of the same moment);
- a scene sound holds Zorp's own cues back for 7 s, so the two never stack;
- `o.soft` plays at 0.6; `o.force` (the gallery only) skips the setting, the tap and the gap;
- every sound goes through the shared bus, so `stopAll()` cuts it.

**Two changes to section 4's "browser limit".**
- **A tap on the page before counts.** The page saves the time of the last tap as it goes (`pagehide`, sessionStorage `pb-tap`), and the next page counts it for the rest of its 5 s. Chrome lets audio start on a page reached by a tap on the same site (checked in headless Chromium: an audio context on a page opened directly stays suspended; on a page reached by a link or a form submit it runs). So in Chrome the quiz results celebrations (the 10/10, a level-up, the badges) now sound straight away. Other browsers may still keep audio off until a tap on the page.
- **Never late.** A sound whose audio is not ready within 1 s is dropped, so a browser that keeps audio off never plays a celebration's sound later, at the wrong moment.

**The wiring.**

| Moment | What plays | Reduced motion |
|---|---|---|
| a badge stage (`badge-stage.js` v7) | `whoosh` as it opens (streaks: `fire`), `stamp-<tier>` as the medal lands at 1,250 ms (100 days: `stamp-violet`), then the family touch 600 ms later (Full marks line `sparkle`, Recovery line `sprout`) | the stamp alone, soft |
| the 10/10 (`moments.js` v7) | `gem` at 780 ms, so its top note meets the landing seal; `confetti` with the burst at 1,060 ms | `gem`, soft |
| level up | `level` from 900 ms, with the ring; its chord when the number turns | `level`, soft |
| Lesson complete | `book` as the book closes (1,300 ms, or 715 ms for another lesson); its chime meets the tick | `book`, soft |
| Your week | `week`, one rising note per card | the same, soft |
| a story chapter (`story-chapters.js` v2) | `story` as the first scene opens (the arrival film stays silent) | `story`, soft |
| a corner card | `pop` | `pop` |

Each sound is timed with the scene's own timers, so a card that is skipped never sounds afterwards. The stage cuts all sound when it closes (Continue at the end, Skip, Skip all, Esc), and a timer still due during the closing fade stays silent (the walk caught a stamp sounding 300 ms after Continue; fixed).

**Checked in a browser** (headless Chromium, `scratchpad/snd_walk.py`, which records each sound asked for, whether it played and the audio state):
- on the gallery, every badge family, moment, card and the story asked for the sounds in the table, at the planned times, and played them;
- with reduced motion, one soft sound each (gain 0.6);
- with the switch off, nothing played;
- a real pupil: a lesson quiz at 10/10, submitted, then the results page. The First quiz and Full marks badges sounded straight away with no tap on the results page, and a second 10/10 played `gem` then `confetti` 280 ms later;
- a page opened without a tap stayed silent;
- the speaker button saved `{"zorp_sound": "off"}`; after a reload the page and Settings showed Off. In the gallery it saved nothing.

**The stage's speaker button** (`zorp-stage.js` v3, `stage.css` v2):
- top right of every stage, while Celebration sounds is on (and after it was turned off there, so it can be turned back on);
- `aria-label` "Celebration sounds", `aria-pressed`; 44 by 44 px;
- one tap saves `zorp_sound` off (or back on) as Settings does, and cuts the sound at once; turning it back on plays a soft pop;
- in the previews (the gallery, the guide preview) it changes this page only.

**Settings** (`profile_settings.html`):
- the section is now "Celebration sounds";
- the line reads "Short, quiet sounds when you earn a badge and when Zorp celebrates. Best with headphones or at home. The speaker button on a celebration turns them off.";
- the options are "Off: no celebration sounds" and "On: a short sound for each badge and celebration";
- "They play only with full motion" went, since the new sounds also play (soft) with reduced motion. Zorp's own jump and land cues still need full motion.

**The gallery** (`/celebrations-gallery`, `celebrations-gallery.js` v2): a Sounds section with a button for each sound, a "Soft" box (as with reduced motion), and "Play the celebrations with sound", which lets every moment, badge and card on the page sound as a pupil's would (this page only).

**Caps and pins.**
- Raised: `sound.js` 9,900 to 13,600; `badge-stage.js` 22,500 to 23,600 (23,243 B); `moments.js` 43,500 to 44,600 (44,230 B); `zorp-stage.js` 24,000 to 27,000 (26,386 B); `stage.css` 10,000 to 11,000 (10,564 B); the CSS tree 282,200 to 283,000 (282,301 B).
- `story-chapters.js` stays inside its 20,500 cap (20,001 B).
- `sw.js` `pb-v129`.

**Tests.**
- New: `scripts/test_celebration_sounds_smoke.py`.
- New: `scripts/celebration_sound_harness.js` (Node, a fake AudioContext). It covers every sound's gains and length, soft, the gates, the gap and chained layers, the 7 s hold on Zorp's cues, force, `stopAll`, the carried tap, the late guard and a failed load.
- Changed: `test_zorp_sound_smoke.py` (the settings copy; the gallery may pass force and arm, like the styleguide), `test_zorp_charm_smoke.py`.

**Not testable headless:** how the sounds sound. David listens on the gallery; gains change after that (S3).

