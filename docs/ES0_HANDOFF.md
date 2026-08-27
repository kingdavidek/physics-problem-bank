# ES0 handoff — European School Integrated Science (platform only)

**Start here.** This file is the agent entry point for Phase ES0.

| | |
|--|--|
| **Full curriculum plan** | `docs/EUROPEAN_SCHOOL_SCIENCE.md` |
| **Phase** | **ES0 only** — mixed-quiz engine + `eursc` hierarchy shell |
| **Do not start** | ES1+ lesson content, 46-topic registry, Practice generator |

---

## Step 0 — sync repo (run before anything else)

Cloud agents often boot on a stale branch. Run:

```bash
git fetch origin main
git checkout main
git pull origin main
test -f docs/EUROPEAN_SCHOOL_SCIENCE.md && test -f docs/ES0_HANDOFF.md && echo "Spec files OK"
```

If `EUROPEAN_SCHOOL_SCIENCE.md` is missing after pull, stop and report — do not guess.

---

## Session scope

### IN SCOPE (ES0)

- Generalise lesson quiz to mixed formats (MCQ, order, pick/set, numeric, keyword)
- Fix GCSE-only quiz gates; keep Practice generator closed
- Add `eursc` level hierarchy shell (labels, filter, icon, year/unit grouping)
- Lesson-template filename allowlist for `eursc_science_*.html`
- Synthetic test fixtures + smoke tests (web, API, retry, session security)
- Commit, push, PR, full smoke suite

### OUT OF SCOPE

- ES1 pilot (`measurement`) and all ES2–ES10 content
- All 46 topics in `topic_registry.py`
- Real lesson templates (except minimal test fixtures)
- QOTD for `eursc/science`

**Stop when ES0 exit criteria below are met.** Do not continue unless the user asks.

---

## ES0 tasks (detail in `docs/EUROPEAN_SCHOOL_SCIENCE.md` §5–§8)

1. **Mixed quiz** — `generators/shared/lesson_quiz.py`; reuse `answer_checkers.py`, `quicktest_question.html`, `free_response_inline.html`
2. **Gates** — `app.py::_lesson_quiz_available`, `models/buddy.py`; leave `GENERATOR_LAUNCH_GCSE_MATHS_CS=True`
3. **Hierarchy** — `app.py`, `topics.html`, `u4.js`, `icon.html`, `lesson_search.py`, `topic_status.py`
4. **Tests** — mixed quiz + session security + `eursc` filename pattern

### ES0 exit criteria

> Synthetic MCQ/order/pick/numeric quiz passes web/API/retry/session-security tests

Also read: `docs/AI_HANDOFF.md`, `docs/API.md` §Problems, `docs/COMPLEX_MECHANISMS.md` §1.

Run: `PB_TESTING=1 python scripts/run_smoke_tests.py`

---

## When done

Report: changes made, exit checklist, smoke result, **"ES0 complete. Ready for ES1 on request."**
