# G8 — Teacher / class mode — agent handoff

**Track:** Optional teacher mode, class rosters, progress dashboards (T0–T2), and teacher-set frozen question work.  
**Audience:** Solo tutors and classroom teachers (not school orgs).  
**Design (locked 2026-08-30):** `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2.  
**Review contract:** `docs/G8_TEACHER_REVIEW_RUBRIC.md`.  
**Privacy:** Revisit `docs/DPIA.md` in Phase 0 (draft updates). Qualified legal review remains the operator’s before public HTTPS.  
**Prerequisite:** G1–G7 shipped; solid-draft security + S0–S3 code shipped.

---

## Copy-paste prompt for the next agent

```
You are starting the G8 teacher / class mode track. Do Phase 0 only, then stop.

Read first:
1. docs/G8_TEACHER_HANDOFF.md
2. docs/G8_TEACHER_REVIEW_RUBRIC.md
3. docs/POTENTIAL_FUTURE_FUNCTIONALITY.md §2 (decisions are locked)
4. docs/AI_HANDOFF.md
5. docs/DPIA.md (review trigger: teacher/class mode)
6. docs/SECURITY_AND_GDPR.md §6.1

Phase 0 — Baseline and contract:
- Run `PB_TESTING=1 python scripts/run_smoke_tests.py` and record the suite size and result in docs/G8_TEACHER_REVIEW_RUBRIC.md (Phase 0 baseline table).
- Run `python scripts/ops_cadence.py feature-gate` and record the four answers in the rubric (G8 shares children’s study data with a teacher).
- Draft DPIA residual/gap notes for G8 as planned processing (join consent, teacher-only remove, T0–T2, no T3, frozen set-work). Do not claim a qualified legal review is complete.
- Confirm there is still no teacher/class schema or route in the live app.
- Do NOT create tables, routes, templates, or APIs.
- Do NOT implement join, remove, dashboards, or set work.
- Do NOT reopen locked product decisions in §2.2.
- Commit only if the user asks.

When Phase 0 is done: report, then wait for an explicit cue before Phase 1.
```

---

## Delivery phases (do one phase per user cue)

| Phase | Name | Scope |
|-------|------|--------|
| **0** | **Baseline and contract** | **Next.** Smoke baseline + feature-gate + DPIA draft notes. No code. |
| **1** | **Teacher identity and classes** | Soft teacher enable; create / list / archive class; join code + rotate. Cap 40 later enforced on join. |
| **2** | **Roster (teacher-only remove)** | Student join by code + disclosure; many classes; **no student leave**; teacher remove; GDPR delete still erases memberships. |
| **3** | **Progress dashboards T0–T2** | Class aggregates + named progress + skill-gap chips. No T3. Authz on every endpoint. |
| **4** | **Set work** | Frozen X questions (1–20) for selected students or whole class; student class-work UI; teacher n/X + scores. |
| **5** | **Hardening** | Handle invites; view audit log; CSV export; erase/export class rows; indexes / caps. |
| **6** | **Verification** | Full smoke; teacher and student sample flows; confirm no leave route; no T3 leak. |

**Rule:** Complete one phase, report, **stop**. Do not proceed until the user explicitly asks.

---

## Locked invariants (do not “fix” these)

1. **Join is opt-in** (code after disclosure). **Silent add is never allowed.**
2. **No student Leave.** Only the teacher removes. Account deletion is GDPR, not leave.
3. **T3 free-text reflections stay private** to the student. T2 chips are in from Phase 3 with join copy, no extra toggle.
4. **Set work is frozen generator payloads**, graded server-side from the stored set. Same trust model as challenges / shared questions.
5. **Do not** extend `study_pairs` or fan out `question_suggestions` for class work. Do not turn friend `quiz_challenges` into homework.
6. **Do not** add A-Level / Physics / MYP to `GENERATOR_LAUNCH_PATHS` as a side effect. Set work uses the **live** generator catalogue.
7. **Do not** add `eursc` to QOTD.
8. **Do not** start `docs/OPERATOR_LAUNCH.md` (public HTTPS / ICO) during this track.
9. Commit only if the user asks.

---

## Key paths (when implementation starts)

| Area | Path |
|------|------|
| Design | `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2 |
| New models | `models/classes.py` (and assignment module) — Phase 1+ |
| Authz | `teacher_can_view` / `teacher_owns_class` on every class endpoint |
| G1–G7 reuse | `models/weak_topics.py`, quiz history, `lesson_progress`, revision queue, `models/skill_gaps.py` |
| Frozen sets | Same pattern as `models/challenges.py` `problems_json` |
| Erase | `models/account_deletion.py` must cover new tables (Phase 5 at latest; schema from Phase 1 should be listed) |
| API | `docs/API.md` when routes ship |
| Smoke | `scripts/test_g8_*_smoke.py` (name as you add them) |
| Full smoke | `scripts/run_smoke_tests.py` (`PB_TESTING=1`) |

---

## What not to do

- Build school SSO, Google Classroom, billing, or co-teaching
- Let students leave a class from the UI or API
- Show free-text reflections to teachers
- Let the client send `correct_answer` / problem HTML that the server trusts
- Reopen §2.2 decisions without an explicit user cue
