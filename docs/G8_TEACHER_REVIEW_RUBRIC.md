# G8 — Teacher / class mode — review rubric

**Track:** Teacher mode, rosters, T0–T2 dashboards, frozen set-work.  
**Use:** Every agent on this track.  
**Design:** `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2.  
**Handoff:** `docs/G8_TEACHER_HANDOFF.md`.  
**Last updated:** 2026-08-30 (contract written; Phase 0 baseline not yet recorded)

Do **one phase per user cue**. Stop and report when the phase is done.

---

## Delivery phases

| Phase | Name | Scope | Status |
|-------|------|--------|--------|
| **0** | **Baseline and contract** | Smoke + feature-gate + DPIA draft notes; no schema/routes | **Not started** |
| **1** | **Teacher identity and classes** | Enable teacher; create/list/archive class; join code + rotate | Not started |
| **2** | **Roster (teacher-only remove)** | Join by code; many classes; teacher remove; no student leave | Not started |
| **3** | **Progress dashboards T0–T2** | Aggregates + named progress + skill-gap chips; no T3 | Not started |
| **4** | **Set work** | Frozen X questions to selected or all; student complete; teacher scores | Not started |
| **5** | **Hardening** | Invites; audit log; CSV; GDPR erase/export for class rows | Not started |
| **6** | **Verification** | Full smoke + sample flows | Not started |

---

## Locked decisions (do not reopen)

Copied from `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2.2:

1. Solo tutors and teachers; 40 active students per class; no org/verification in this track.
2. Students may be in many classes.
3. T2 skill-gap chips ship with dashboards (join disclosure, no extra toggle).
4. No extra “never see” list beyond T3 free-text reflections (plus operational exclusions: passwords, emails, follows/feed, buddy).
5. Teacher-only remove. No student Leave. GDPR delete still erases memberships.
6. Set work is in this track: X frozen questions for n students or all.

---

## Phase 0 baseline (fill this in Phase 0)

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Suite size | *(record)* |
| Result | *(record)* |
| Teacher/class tables in schema | Must be **absent** before Phase 1 |
| Teacher/class routes | Must be **absent** before Phase 1 |
| `python scripts/ops_cadence.py feature-gate` | *(record the four answers)* |

**Feature-gate expectation:** G8 is a new sharing of children’s educational performance with a teacher. At least one §6.1 answer is yes. Privacy / DPIA / ROPA notes belong in the **same later implementation PRs** as schema, not as a silent skip.

---

## Invariants to keep green every phase

- [ ] No `POST /api/v1/me/classes/<id>/leave` (or web Leave control)
- [ ] Join requires the student and shows disclosure (no silent add)
- [ ] Teacher progress/set-work APIs 403 unless `teacher_can_view` / `teacher_owns_class`
- [ ] T3 free-text reflection body never in teacher JSON or HTML
- [ ] Assignment student GET strips `correct_answer` / solution until after server grade
- [ ] Frozen assignment answers graded from stored `problems_json`, not client keys
- [ ] Account deletion leaves no class/assignment rows for that user (once tables exist)
- [ ] Full `scripts/run_smoke_tests.py` stays green
- [ ] `GENERATOR_LAUNCH_PATHS` and QOTD eursc skip unchanged unless the user explicitly asks

---

## Phase 4 set-work acceptance

- Teacher can generate a preview of X questions (1–20) from a live catalogue topic
- Assign to a subset of the roster **or** all active members
- Different students can receive **different sets** via two assignments, not via per-row mutation of one set
- Student cannot reroll the assigned items
- Teacher sees n/X and score per recipient
- Peer challenges and friend suggestions remain unchanged

---

## Phase 6 verification (when cued)

- Teacher: enable → class → code → roster → remove → T0–T2 student detail → set work → scores
- Student: join (second class too) → no Leave → complete work
- Guest / other teacher cannot see roster or progress
- Sensitive: no T3; no emails in roster payloads
