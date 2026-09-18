# G8 — Teacher / class mode — agent handoff

**Track:** Optional teacher mode, class rosters, progress dashboards (T0–T2), teacher-set frozen question work, handle invites, audit log, and CSV export.  
**Audience:** Solo tutors and classroom teachers (not school orgs).  
**Design (locked 2026-08-30):** `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2.  
**Review contract:** `docs/G8_TEACHER_REVIEW_RUBRIC.md`.  
**Privacy:** Phase 1–6 shipped. Qualified legal review remains the operator’s before public HTTPS. T3 stays private. No student Leave.  
**Prerequisite:** G1–G7 shipped; solid-draft security + S0–S3 code shipped.

---

## Copy-paste prompt for the next agent

```
G8 teacher / class mode is complete (Phases 0–6, 2026-08-30 / 2026-08-31).
Post-track audit landed 2026-09-01 (join/invite/class-work hardening). Do not start a new G8 phase unless the user explicitly asks.
Do not add student Leave.
Do not show T3 free-text to teachers.
Do not reopen locked product decisions in docs/POTENTIAL_FUTURE_FUNCTIONALITY.md §2.2.
Do not start docs/OPERATOR_LAUNCH.md during a product session.

If the user has not named the next track, read docs/AI_HANDOFF.md §7 and wait.
```

---

## Delivery phases (do one phase per user cue)

| Phase | Name | Scope |
|-------|------|--------|
| **0** | **Baseline and contract** | **Done (2026-08-30).** 65/65 smoke; feature-gate recorded; DPIA §9 draft. No schema/routes. |
| **1** | **Teacher identity and classes** | **Done (2026-08-30).** Soft teacher enable; create / list / archive class; join code + rotate. Cap 40 later enforced on join. |
| **2** | **Roster (teacher-only remove)** | **Done (2026-08-30).** Student join by code + disclosure; many classes; **no student leave**; teacher remove; cap 40 on join; GDPR delete still erases memberships. |
| **3** | **Progress dashboards T0–T2** | **Done (2026-08-30).** Class aggregates + named progress + skill-gap chips. No T3. Authz on every endpoint. |
| **4** | **Set work** | **Done (2026-08-31).** Frozen X questions (1–20) from the live catalogue; preview then assign to selected or all; student class-work cannot reroll; teacher n/X + scores; graded from stored JSON. |
| **5** | **Hardening** | **Done (2026-08-31).** Handle invites (opt-in + disclosure); view audit log; CSV (handles only); erase/export leftovers for invites and audit; pending-invite prune. |
| **6** | **Verification** | **Done (2026-08-31).** Full suite **71/71**; sample teacher/student flows; no Leave route; no T3 in teacher payloads; invites still require disclosure; CSV/audit handles only. **Post-track audit 2026-09-01:** pending-invite cap on re-invite; join-by-code respects blocks and treats archived codes as unknown; 14-day invite expiry on accept/list; invite status claim; membership insert races map to `already_member`; class-work GET requires active membership; assignment previews expire after 2 hours on consume. |

**Rule:** This track is complete. Do not proceed to extra G8 work until the user explicitly asks.

---

## Locked invariants (do not “fix” these)

1. **Join is opt-in** (code or handle invite after disclosure). **Silent add is never allowed.**
2. **No student Leave.** Only the teacher removes. Account deletion is GDPR, not leave.
3. **T3 free-text reflections stay private** to the student. T2 chips are in from Phase 3 with join copy, no extra toggle.
4. **Set work is frozen generator payloads**, graded server-side from the stored set. Same trust model as challenges / shared questions.
5. **Do not** extend `study_pairs` or fan out `question_suggestions` for class work. Do not turn friend `quiz_challenges` into homework.
6. **Do not** add A-Level / Physics / MYP to `GENERATOR_LAUNCH_PATHS` as a side effect. Set work uses the **live** generator catalogue.
7. **Do not** add `eursc` to QOTD.
8. **Do not** start `docs/OPERATOR_LAUNCH.md` (public HTTPS / ICO) during this track.
9. Commit only if the user asks.

---

## Key paths

| Area | Path |
|------|------|
| Design | `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2 |
| Models | `models/classes.py`, `models/class_progress.py`, `models/class_assignments.py`, `models/class_invites.py`, `models/class_audit.py`, `models/class_csv.py` |
| Authz | `teacher_can_view` / `teacher_owns_class` on every class endpoint |
| G1–G7 reuse | `models/weak_topics.py`, quiz history, `lesson_progress`, revision queue, `models/skill_gaps.py` |
| Frozen sets | `models/class_assignments.py` — same trust model as `models/challenges.py` `problems_json` |
| Erase | `models/account_deletion.py` leftover checks include assignment, invite, and audit tables; FK CASCADE; audit handles scrubbed |
| API | `docs/API.md` |
| Smoke | `scripts/test_g8_phase1_smoke.py` … `test_g8_phase6_smoke.py` |
| Full smoke | `scripts/run_smoke_tests.py` (`PB_TESTING=1`) — **71** passed 2026-08-31; G8 hardening re-checked 2026-09-01 |

---

## What not to do

- Build school SSO, Google Classroom, billing, or co-teaching
- Let students leave a class from the UI or API
- Show free-text reflections to teachers
- Let the client send `correct_answer` / problem HTML that the server trusts
- Reopen §2.2 decisions without an explicit user cue
- Silently add a student to a roster (invite still requires accept + disclosure)
