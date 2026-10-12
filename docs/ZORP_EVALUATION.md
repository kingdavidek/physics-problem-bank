# Zorp charm: evaluation kit (E9 Phase 5)

**Status:** kit built 2026-10-06. **The class session has not happened yet, so the results table in section 9 is blank on purpose.** Nothing in this file is a result. No tuning has been applied on the strength of an opinion; section 10 lists the knobs to use after the session.
**Spec:** `docs/ZORP_CHARM.md` section 3.5 (plan), D9 in section 7.1 (teacher-led, offline, anonymous), section 5 (safeguarding checklist).
**Printable kit:** `docs/zorp_evaluation_print.html` (open it in a browser and print on A4: page 1 is the pupil prompt sheet, page 2 is the teacher sheet). A PDF render is attached to the Phase 5 report.
**Language:** British spelling, no emoji, no em dashes.

---

## 1. Purpose

E9 added four things at a few named moments: a talking mouth, a softer body, one consistent voice and optional sound. They are meant to be encouraging. The risk is that they distract, get tiresome on repeat, or are too noisy in a room. This session finds out which, from real pupils, without collecting anything in the app.

The questions it answers:

1. Do pupils find Zorp's charm encouraging, neutral or distracting?
2. Does the talking mouth help pupils read the line, or do they wait for it?
3. Is the sound acceptable in a classroom, even when it is opt-in?
4. Did anything upset or confuse anyone (bot versus person, the origin lore line)?
5. Which constants, if any, should be tuned (section 10)?

It is a short, friendly check, not research. Nothing is graded and nobody is rated.

## 2. Teacher-led and offline (D9)

- Nothing is recorded in the app. There is no "Is Zorp helpful?" toggle, no survey, no analytics (`docs/AI_HANDOFF.md` invariant 11). Nothing is typed into the app for this evaluation.
- The teacher runs the demo, hands out sticky notes, reads the room and fills in a paper table.
- Pupils never give a name, an account handle or an email.

## 3. Who sees what

| Class | How Zorp is shown | Why |
|---|---|---|
| **S1 and S2** (under 13) | **Projector demo only**, from the teacher's laptop. Pupils do not use pupil accounts, and nobody signs in. | The app's age gate is 13+ (`docs/DPIA.md` section 1; no under-13 accounts). |
| **S3 and older, where every pupil is 13 or over** | Projector demo first. Pupils **may** then try their own account for a few minutes, if school policy allows and they wish to. | Their own accounts are allowed for 13+. Using one is always optional. |
| Mixed ages or unsure | Projector demo only. | Safest default. |

The projector demo needs no account: run the app on the laptop (`Open Problem Bank.bat`, or `python app.py`) and open `http://127.0.0.1:5001/styleguide#zorp-charm`. That page is a developer page and only works on the laptop itself or with the dev switches, never on a public site, which is what you want in front of a class.

## 4. Before the session (5 minutes, on your own)

1. Open `/styleguide#zorp-charm` and press **Preview at full motion** in the banner. Windows with "Animation effects" off reports reduced motion, so without this the mouth and body stay still (by design).
2. Press the six showreel buttons once, in order, to check the projector and the speakers. Zoom the browser (Ctrl and +) until Zorp and the line under "Zorp says" can be read from the back row. Set the volume low. Zorp's cues are quiet (peak gain 0.06, below every answer tone) but a classroom is a different room.
3. Press **Motion: reduced** in the picker, then showreel step 1 again, to see what a pupil with reduced motion sees: the line appears at once and Zorp stays still. The picker switches the full-motion preview off, so press **Motion: system** and then **Preview at full motion** again before the class arrives (the banner and the status line under the showreel say which level is active). (Do not run this part for pupils unless you want to.)
4. Print the kit: page 1 for you to read the prompts from or to hand out, page 2 to keep.
5. Bring sticky notes (one colour is fine), a few pens and an empty space on the board or a table. Do not bring a phone or camera for taking pictures.

## 5. The session plan (15 to 20 minutes)

| Min | What | Notes |
|---|---|---|
| 0 to 2 | **Frame it.** "Zorp is the little alien in our practice app. I want your honest ideas about him. It is not a test, nothing is marked, and there are no names." | Say that "it got in my way" is just as useful as "I liked it". Say they can skip any prompt. |
| 2 to 9 | **Showreel**, six steps, about one minute each (section 6). | Stand where you can see faces. Do not explain much, let them react. |
| 9 to 10 | **Quiet moment.** "Think about it for a few seconds." | |
| 10 to 16 | **Sticky notes.** Show the prompts (page 1 or on the board). Pupils pick one or two, write or draw one idea per note, no name. | Six minutes is enough. Nobody has to write. |
| 16 to 18 | **Collect.** Pupils fold their notes and put them in a pile or a box, face down (or stick them on the board if the class is happy to). | Notes go in without anyone watching who wrote which. |
| 18 to 20 (optional) | **Short chat.** Read two or three notes aloud, anonymously, and ask "does anyone feel the same, or different?" | Skip if time is short. Only read notes that are kind about other people. |
| Right after | Tick the teacher checklist (page 2), sort the notes (section 8), fill in the table (section 9), destroy the notes (section 11). | Do it the same day, while you remember the room. |

For a 15-minute slot, skip the optional chat and shorten the showreel to steps 1, 2, 4 and 5.

**Pupils trying their own accounts (13+ classes only, optional, 5 extra minutes).** Ask them to answer one practice question and notice anything Zorp does. Zorp's sounds are off by default and are only a pupil's own choice in Settings ("Zorp's sounds: Celebrations", best with headphones): in class, leave them off. Do not ask anyone to change a setting for the evaluation. The Guide's origin story plays only once ever per account, so use the projector for it.

## 6. What to show: the showreel order

The six buttons are in `/styleguide#zorp-charm`, in the block headed "Showreel". They use the real talk caps and clips.

| # | Button | What pupils see and hear | Say something like |
|---|---|---|---|
| 1 | **Origin line, talking** | Zorp waves and his mouth follows the first origin line (at most 1.6 s). The text is all there at once. | "This is the first thing Zorp says when you start." |
| 2 | **Reward: soft fist-pump** | "You earned this." with a fist-pump and a little jelly wobble on landing. | "This is what happens when you earn a badge or finish something." |
| 3 | **Same reward, soft body off (A/B)** | The same clip with the extra squash and wobble removed (the E8 look). | "Spot the difference? Which one feels better, or neither?" (Do not ask for a vote. Let it go into the notes.) |
| 4 | **Corner bubble, talking** | The small Zorp says "Nice work: 7/10 on Forces." once. | "This is how he pops up in the corner." |
| 5 | **Sound on (preview cues)** | The fist-pump again, with a quiet jump sound and a landing sound. | Warn first: "A short, quiet sound is coming." |
| 6 | **Sound off (silent)** | The same reward in silence, which is what every pupil gets unless they choose otherwise. | "This is the normal. Sounds are off unless you switch them on." |

If a step does nothing visible, the status line under the buttons says why (usually reduced motion: press **Preview at full motion**).

## 7. Pupil prompts (open, reflective, fun, not graded)

Say once: "These are just for fun. Not a test, no marks, no names. Skip any you like."

On the sheet, and on the board. Pupils choose one or two. One idea per sticky note.

1. **What did you think when Zorp cheered?**
2. **Was there a moment Zorp got in the way? Tell us about it.**
3. **When Zorp talked, what did you look at?**
4. **If Zorp could say one sentence when a question goes wrong, what would be kind and helpful?**
5. **If Zorp could do one new thing, what would it be?**
6. **If Zorp made a sound in our classroom, when would that be fun, and when would it be too much?**

Prompts 1 and 3 are worded so they do not suggest an answer (no "how fun was it", no list of options to pick from); prompt 2 balances prompt 1 by inviting the other side. What is deliberately not here: no matching, no true or false, no recall questions ("which clip came second?"), and no rating scales, stars or faces to circle. Those feel like a test and would change the answers. Drawings and one-word notes are welcome.

## 8. Sorting the sticky notes into themes

Do this alone, after the session, in about ten minutes. Read each note once and give it **one main theme** (a second one only if it clearly says two things). Use the codes in the table.

| Code | Theme | A note reads like |
|---|---|---|
| **E** | Encouraging | Warm, motivating, made me smile, made me want to carry on, felt like a reward. |
| **D** | Distracting | Looked at him instead of the question, too long, too much, annoying when it repeated, hard to read while he moves. |
| **N** | Neutral | Did not notice, did not care, "it was fine", "OK". |
| **C** | Concern | Sad, upset, scared or confused: "is he real?", the home line made me sad, someone is being laughed at, anything about feeling watched. |
| **I** | Idea | A new move, a new sentence, a new thing for Zorp. (Prompts 4 and 5 mostly land here.) |
| **S** | Sound | Anything about noise: fun, too loud, would annoy the class. Count S **as well** as the main theme. |

Rules of thumb:

- **"Encouraging" versus "distracting".** Decide by what the pupil says it did to *them* (made me want to go on, or took my eyes off the work), not by whether they liked Zorp. "I love him but I could not read the question" is **D**. "He is silly but it made me smile when I got it right" is **E**.
- A pupil who says it "got in the way" **and** gives a fix ("make it shorter") is still **D**; the fix is useful for section 10.
- A note about prompt 6 that says sound would be fun **only with headphones or at home** is **S** (acceptable only when opt-in), and does not count as E or D.
- Any **C** note gets read twice and handled before anything else (section 12).
- Do not try to count words or find the "average". Counts of E, D, N, C, I and S are enough.

## 9. Results table (BLANK: no session has been run)

Copy one row per class session. Do not put names, initials, handles or quotations that could identify a pupil in the table. Paraphrase. Counts only.

| Date | Class level (S1 to S7) | Pupils present | Setup (projector only, or own accounts) | Notes (n) | E | D | N | C | I | S | E share of E + D | Checklist flags (teacher sheet) | Themes in a few words | Decisions (section 10) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (blank) | | | | | | | | | | | | | | |
| (blank) | | | | | | | | | | | | | | |
| (blank) | | | | | | | | | | | | | | |

**How to fill it in.**

- **Notes (n)** is the number of sticky notes, not pupils.
- **E share of E + D** is E divided by (E plus D), as a fraction or percentage. Leave N, I and C out of this one.
- **Checklist flags** lists which of the ten teacher checklist items were ticked as a worry (for example "irritation on repeat, sound too loud").
- **Decisions** is one line, written after reading section 10: for example "none", "cut tour talk cap to 1,000 ms", "keep sound opt-in only".
- Add the date, the level and the counts the same day. Come back to the "Themes" and "Decisions" cells after you have slept on it.

When the table has real rows, copy a one-paragraph summary into `docs/ZORP_CHARM.md` section 6 "Phase 5" (a dated "Evaluation results" note, no personal data), and into `docs/AI_HANDOFF.md` section 9 if a decision changes the product.

## 10. Decision rules for after the session

### 10.1 Success criteria (from `docs/ZORP_CHARM.md` 3.5.2)

All three should hold across the sessions you run (at least two classes, and at least ten notes with a lean, E plus D, before you read anything into the share):

1. **Encouraging beats distracting.** E is at least two thirds of E plus D.
2. **No reports of discomfort.** No **C** note that remains unresolved, and no teacher checklist flag for upset or confusion that was not resolved on the day.
3. **Sound only when opt-in.** Pupils judged sound acceptable (or fun) only when it is a choice and quiet. If any class judged sound too much even in the demo, it stays opt-in, off by default, and nothing is added.

### 10.2 What to do with each pattern

| What you saw | What it suggests | Do |
|---|---|---|
| E share two thirds or more, no C, sound fine | The charm works. | Change nothing. Record it. |
| D notes say "too long", "kept talking", "waited for him to finish" | Talk caps are too long, or too many moments talk. | Lower the talk caps first (10.3), then drop talking from the least valued moment (tours before rewards). |
| D notes say "looked at him instead of the question", "moved too much" | Motion competes with the task. | Reduce the soft body share and jelly (10.3). Check that tours and bubbles do not move the body. Consider limiting talk to rewards and the origin story. |
| D notes say "boring on repeat", "same every time" (checklist: irritation on the 2nd or 3rd repeat) | Repetition. | Lengthen the gap between big reactions (`REACT.gap`) and keep rewards rare. Do not add variety by adding moments. |
| S notes say "too loud", "would annoy the class" | Sound is not suited to the room. | Lower the cue gain, keep it opt-in, leave the default off. If objections remain, remove sound from the settings page in a later phase (a decision for David). |
| S notes say "fun" **and** pupils ask for more talking sounds | A signal for D7 (10.4). | See 10.4, do not act on one class. |
| Several pupils confuse bot and person | The "bot" lines are not landing. | Review the origin lines in `static/js/guide-catalog.js` (copy rules in `docs/ZORP_CHARM.md` 3.3.6). Never remove "I'm a bot, not a person." |
| Any C note about the origin home line (`origin.home`) | The lore line may upset. | Read it twice. If a pupil was upset, soften or move the line before anything else, even if the rest is positive. This outranks every other rule here. |
| Pupils read the line aloud, or wait for the mouth to finish before reading | The mouth is leading the reading. | Shorten the talk caps, never slow the text. Text must stay complete and instant. |
| A reduced-motion pupil reports missing out or finding the page odd | Reduced mode is not good enough. | Check the reduced face swaps (`reducedFace` in the clips). Do not add motion to reduced mode. |

### 10.3 Which constants to tune (constants only; no new features in Phase 5)

Nothing has been changed yet. Each change below keeps behaviour within the existing tests unless the test pins the old value, in which case change the pin in the same edit and say why. Byte caps: `zorp-poses.js` has 52 B of headroom and `zorp-talk.js` 18 B; changing a number's value keeps the length the same, but check `scripts/test_zorp_charm_smoke.py` after every edit.

| Knob | Where | Today | Sensible range | Use when |
|---|---|---|---|---|
| `TALK_MAX.story`, `.reward`, `.tour` | `static/js/guide.js` | 1600, 1600, 1200 ms | 800 to 1600 (tour 800 to 1200) | Talking feels long. The ceiling is 2000 (`MAX_CEIL`). |
| corner bubble `max` | `static/js/study-buddy.js` (the `talk` call) | 1200 ms | 800 to 1200 | The bubble talks too long. |
| welcome `max` and the `ready` delay | `static/js/welcome.js` | 1400 ms, 400 ms | 800 to 1400; 400 to 800 ms | Welcome talks too long. |
| `T_OPEN`, `T_SHUT`, `T_GAP` | `static/js/zorp-talk.js` | 75, 60, 40 ms | open 65 to 95, shut 55 to 80, gap 30 to 60 | The flap rate feels frantic or sluggish. The floors `F_OPEN` 60, `F_SHUT` 51 and the 9 Hz ceiling are tested, so keep them. |
| Punctuation pauses | `pauseOf` in `static/js/zorp-talk.js` | 140 (comma), 180 (colon), 260 (full stop), 360 (ellipsis) ms | 100 to 400 | The mouth seems to run over punctuation. |
| Which moments talk | the `say` calls in `guide.js` (story, reward, tour), `talkMessage` in `study-buddy.js`, `talkCopy` in `welcome.js` | all on | each on or off | One moment is the main source of D notes. |
| `SOFT` (body squash share) | `static/js/zorp-poses.js` | 0.4 | 0.2 to 0.5 (tests cap the body layer at 0.08 and the drawn body at 0.16) | "Moved too much" or "too wobbly". Lower it. |
| `JELLY`, `JELLY_MS`, `CHEEK`, `WHIP` | `static/js/zorp-poses.js` | jelly 0.6 then 0.3 of the landing squash over 210 ms; cheek 0.8; whip 0.4, 0.15 | scale each amplitude by 0.5 to 1.2 | The landing wobble distracts, or is invisible at the back of the room. |
| `REACT.gap` (big reaction spacing) | `static/js/zorp-poses.js` (the `REACT` data) | 7000 ms | 7000 to 20000 | Reward clips repeat too often. |
| `CUE_GAIN` | `static/js/sound.js` | 0.06 | 0.03 to 0.07 (tests require at most 0.07 and below `soft` 0.08) | Sound is too loud or too faint. |
| `BLIP_GAIN` | `static/js/sound.js` | 0.03 | 0.02 to 0.035 | Only matters if D7 is revisited. |
| `SEQ_MS`, `ARBITER_MS`, `GESTURE_MS` | `static/js/sound.js` | 7000, 400, 5000 ms | `SEQ_MS` 7000 to 20000; `GESTURE_MS` 2000 to 5000 | Cues are too frequent, or fire too long after a tap. Never loosen them. |
| Confetti arpeggio defer | `static/js/celebrate.js` | 1000 ms wait, 1500 ms `cued` window | keep | Only if the arpeggio and a cue are ever heard together. |

After any tuning edit: bump the changed file's `?v=` in the template that loads it, bump `CACHE_VERSION` in `static/js/sw.js` by one, update the pinned assertions (`test_pwa_smoke.py`, `test_zorp_charm_smoke.py`, `test_zorp_expression_smoke.py`, `test_buddy_smoke.py` as the pins list), re-measure the ledger, run the full suite, and write a dated line in `docs/ZORP_CHARM.md` section 2.1.

### 10.4 When to revisit D7 (voice blips) and the hidden `chatter` setting

The voice blips exist (`pbSound.blips`, the `chatter` value of `zorp_sound`) but are reachable from `/styleguide` only. The PATCH validator rejects `chatter` and the settings page never offers it. **Leave it that way unless all of these hold:**

1. Criterion 1 to 3 in 10.1 hold, with sound judged acceptable when opt-in.
2. In at least two classes, several pupils (say three or more notes in each) say they would like Zorp to make talking sounds, and none says sound is too much.
3. The teacher checklist shows no "sound acceptable" flag raised in any session.
4. David decides, after listening to the blips himself in the room they would be used in.

Even then, turning it on is a new phase, not a tuning change: it needs the settings option, a copy line, tests, and a fresh DPIA review-log row. If any class judged sound too much, the answer is not to ship blips.

## 11. Privacy

- **Nothing is typed into the app.** The demo is on the teacher's laptop. No pupil enters anything into Problem Bank for the evaluation.
- **No names on notes.** Not even initials. Pupils should not sign drawings.
- **No photos of faces.** Better: no photos at all. There is no need to photograph notes, and a photo of handwriting can identify a pupil.
- **No recording.** No audio, no video of the class.
- **Notes are destroyed after summarising.** Once the table is filled in (the same day), tear up or shred the notes. Keep only the table: counts and paraphrased themes.
- **Quotations.** If you want to keep a line for the write-up, paraphrase it and drop anything that could identify a pupil.
- The table in section 9 contains no personal data. If it ever gets one, it stops being part of this kit.

## 12. Safeguarding (ICO Children's Code standard 13, and the E9 checklist)

- The session is **optional and low-stakes**. Pupils can skip any prompt, can write nothing, and can ask to stop the sound at any time. Do not praise or single out who wrote what.
- Zorp's moments are the pupil's own action or an achievement. This evaluation tests that, it does not add pressure. **If a note or a reaction suggests a pupil felt pressured, watched or pushed to keep going, treat that as a D and C finding and act on it (section 10.2).**
- **Upset or worry.** If a pupil seems upset (for example by Zorp's line about missing home), deal with it kindly on the spot, in the usual way for your school. If anything on a note or said aloud suggests a pupil needs help, follow your school's safeguarding policy and designated safeguarding lead route. That is outside this kit, and nothing about it is recorded here.
- **Sound.** Keep the volume low. Warn before steps 5 and 6. Anyone who finds it uncomfortable can cover their ears, leave, or ask you to stop, and you stop.
- **Reduced motion.** If a pupil uses reduced motion, ask whether they want to see step 1 at full motion at all. Never press someone to look.
- **Under-13s** never use accounts for this evaluation (section 3).

## 13. After the session, in order

1. Tick the teacher checklist (page 2 of the printable kit).
2. Sort the notes (section 8), fill in the table (section 9).
3. Read every C note twice.
4. Destroy the notes (section 11).
5. Apply the decision rules (section 10). Constants only.
6. Record the dated result and decision in `docs/ZORP_CHARM.md` section 6 "Phase 5" and, if the product changes, in `docs/AI_HANDOFF.md`.
7. If you tuned a constant: pins, `sw.js`, ledger and the full suite (section 10.3).

## 14. Files

| File | What |
|---|---|
| `docs/ZORP_EVALUATION.md` | This plan. |
| `docs/zorp_evaluation_print.html` | The printable A4 kit: pupil prompt sheet and teacher sheet. Self-contained, no external assets. |
| `templates/styleguide.html`, `static/js/styleguide.js` | The showreel buttons at `/styleguide#zorp-charm`. |
| `scripts/test_zorp_charm_smoke.py` | `test_showreel_section`, `test_evaluation_kit` and the Phase 5 docs checks. |
