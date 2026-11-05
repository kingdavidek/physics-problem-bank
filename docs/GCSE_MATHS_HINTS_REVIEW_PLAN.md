# GCSE maths hints: review plan (2026-11-04, Stage 2 in progress)

## Why

David found the same hint shown twice on a question. The 2026-11-04 change fixed that by removing the pre-attempt Hint drawer, so every hint now appears only after an attempt, in one Hint card. The hints were built for coverage and checked by automated rules. Nobody has yet read them all the way a pupil meets them. This plan does that.

## What a pupil sees now

1. **After a wrong typed answer:** a short feedback line, then the Hint card. Its first line is chosen in this order:
   - the slip message, when a slip is recognised;
   - the topic family's nudge;
   - the question's own hint;
   - the topic nudge;
   - the default line.
2. **"Show a bigger hint" (optional):** the first step of the worked solution, with its final number left off.
3. **A wrong multiple-choice pick:** the option's note, in the same card.
4. **Set work and lesson-quiz results:** a general slip message, after marking.
5. **Quick Test:** the one-line hint only.

**Scale:**

| Item | Count |
|---|---|
| Practice slots | about 1,173 |
| Practice slots whose first line is the question's own hint | about 900 |
| Practice slots with a bigger hint | about 690 |
| Topic slip messages | more than 150 |
| Nudges | about 30 |
| Multiple-choice notes | about 500 |

The 900 question hints were written as tips to read before an attempt. Some will read oddly after one, and some are generic.

## What a good hint looks like (the review criteria)

**The first line**
- It names the idea or the next step for this question, not generic filler.
- It does not restate the question.
- It never states the answer, the final number, or an operation to do to the pupil's own number.
- It is at most two short sentences.
- It reads naturally after a wrong attempt.

**The bigger hint**
- It is one concrete step that moves the pupil on, using the question's numbers and stopping before the result. Example: "Multiplier = 1 + 20/100".
- It is clearly more than the first line and never repeats it.
- It is not the whole method.

**Slip messages and notes**
- They are right for the exact question on screen.

**Style**
- Kind, British spelling, no em dashes, no emoji. This is checked by the voice lint.

## Stages

### Stage 1: automated census

This is cheap, run by a small model.
- A script generates every practice slot at three seeds, and every multiple-choice slot.
- For each one it records the first line and its source, the bigger hint, and the notes.
- It flags:
  - a first line equal or nearly equal to the bigger hint;
  - a bigger hint that only restates the question or rephrases the first line;
  - the same text across many slots (generic);
  - text pointing at something not on screen (for example "the diagram" with no diagram);
  - before-attempt phrasing;
  - lines that are too long;
  - a missing bigger hint where the solution has usable steps.
- Output is a sheet grouped by topic, with the flags.

### Stage 2: David's read-through

- A private review page, one section per topic. Each row shows the question, the Hint, the Bigger hint and the slip messages most likely to show, with Keep / Change / Note buttons.
- Choices are saved, so the review can be done on a phone in short sittings.
- Flagged rows come first, then the topics David will use first with pupils.
- Reviewing only the flagged rows takes about 15 to 20 minutes per topic.

### Stage 3: rewrite

- A mid-size model rewrites the rows marked Change, topic by topic, using the criteria above. Flagged rows David did not reach can be included too.
- A stronger model checks each batch for maths accuracy and answer leaks.
- The existing hint smokes and the voice lint must pass.
- Census flags must reach zero, or be marked as reviewed.

### Stage 4: keep it fixed

- The census flags become checks in the hints ladder smoke: no duplicate rungs, and a ceiling on generic text.
- Docs rule: hints in new generators are written to be read after an attempt.

## Decisions for David

1. **Source of the first line:**
   - (a) Keep the question's own hint first, and rewrite the weak ones in Stage 3. **Recommended.**
   - (b) Prefer a written topic nudge where one exists.
2. **The bigger hint and the question's numbers:** may it show a calculation with them, stopping before the result, as in "Multiplier = 1 + 20/100"?
   - (a) Yes. **Recommended.**
   - (b) Method in words only.
3. **How to review:**
   - (a) The review page with Keep / Change buttons. **Recommended.**
   - (b) A written list in chat.
   - (c) Leave it to the agents, with a stronger-model check.
4. **Order:** which topics first.

## Cost

Stage 1 is small. Stage 3 is the bulk of the work. It runs topic by topic, so David controls how much is done and when.

## Progress

- **Decisions (2026-11-04):** 1(a) keep the question's own hint first and rewrite the weak ones; 2(a) the bigger hint may show a calculation with the question's numbers, stopping before the result; 3(a) review through the page; 4 GCSE maths topics only, in alphabetical order.
- **Stage 1 done:** `scripts/hints_census.py` writes the census JSON (32 topics, about 2,190 items, flags included). Run with `python -B scripts/hints_census.py --out PATH`.
- **Stage 2 open:** the private review page "GCSE Maths Hint Review" is published on claude.ai. Choices are stored in its `reviews` collection, keyed `p:<topic>:<tier>:<slot>` (hints), `m:<hash of text>` (mistake messages, one choice covers every topic that shares the text) and `n:<topic>:<note id>` (multiple-choice notes). Stage 3 reads that collection.
