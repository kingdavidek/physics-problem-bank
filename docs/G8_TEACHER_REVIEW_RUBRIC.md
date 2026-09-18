# G8 — Teacher / class mode — review rubric

**Track:** Teacher mode, rosters, T0–T2 dashboards, frozen set-work, handle invites, audit, CSV.  
**Use:** Every agent on this track.  
**Design:** `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2.  
**Handoff:** `docs/G8_TEACHER_HANDOFF.md`.  
**Last updated:** 2026-09-01 (post-track audit — join/invite/class-work hardening)

Do **one phase per user cue**. Stop and report when the phase is done.

---

## Delivery phases

| Phase | Name | Scope | Status |
|-------|------|--------|--------|
| **0** | **Baseline and contract** | Smoke + feature-gate + DPIA draft notes; no schema/routes | **Done (2026-08-30)** |
| **1** | **Teacher identity and classes** | Enable teacher; create/list/archive class; join code + rotate | **Done (2026-08-30)** |
| **2** | **Roster (teacher-only remove)** | Join by code; many classes; teacher remove; no student leave | **Done (2026-08-30)** |
| **3** | **Progress dashboards T0–T2** | Aggregates + named progress + skill-gap chips; no T3 | **Done (2026-08-30)** |
| **4** | **Set work** | Frozen X questions to selected or all; student complete; teacher scores | **Done (2026-08-31)** |
| **5** | **Hardening** | Invites; audit log; CSV; GDPR erase/export for class rows | **Done (2026-08-31)** |
| **6** | **Verification** | Full smoke + sample flows | **Done (2026-08-31)** |

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

## Phase 0 baseline (recorded 2026-08-30)

| Item | Result |
|------|--------|
| Command | `PB_TESTING=1 python scripts/run_smoke_tests.py` |
| Suite size | **65** |
| Result | **All 65 smoke tests passed** (2026-08-30) |
| Teacher/class tables in schema | **Absent.** No `teacher_profiles`, `classes`, `class_memberships`, `class_assignments`, or `class_assignment_recipients` in `app.py` `CREATE TABLE` or `models/`. No `models/classes.py`. `models/account_deletion.py` has no class rows. |
| Teacher/class routes | **Absent.** No `/api/v1/teacher/*`, `/api/v1/me/teacher/enable`, `/api/v1/me/classes`, `/api/v1/me/class-work`, and **no** leave route. `docs/API.md` still marks G8 as not implemented. Privacy HTML does not mention teacher/class mode. |
| `python scripts/ops_cadence.py feature-gate` | Four answers below. **At least one yes** — privacy / ROPA / notice edits ship in the **same PRs as schema** (Phase 1+), not as a silent skip. |

**Feature-gate answers** (`docs/SECURITY_AND_GDPR.md` §6.1). G8 shares children’s study data with a teacher after join:

| # | Question | Answer |
|---|----------|--------|
| 1 | Does it collect a new category of personal data? | **Yes.** New records: teacher flag, class metadata, join codes, memberships (teacher–student link), frozen assignment payloads, per-student answers and scores. Existing G1–G7 study data is not a new category but is newly disclosed to a teacher. Update ROPA, privacy notice (`/privacy` and `/privacy/simple`), and retention in the **same PR as schema**. |
| 2 | Does it make anything about a child more visible to anyone else? | **Yes.** After opt-in join, the teacher sees T0–T2 (class aggregates, named progress, skill-gap chips) and set-work completion. **Default off** until the student joins with disclosure. No silent add. Roster-only; no public ranking. Emails, passwords, T3 free-text, follows/feed, and buddy copy stay out. |
| 3 | Does it send data to a new third party? | **No.** The teacher is another registered user of the same controller, not a new processor. No new subprocessor or international transfer. Do not add analytics or a new AI path for class work. |
| 4 | Does it profile, rank, or nudge? | **Yes.** Educational profiling (weak topics, quiz %, skill-gap chips) is shown to the teacher. Set work is a class nudge. No public ranking of minors. Revisit DPIA Children’s Code **std 12 (profiling)** and **std 13 (nudge)** — draft notes in `docs/DPIA.md` §9. Qualified legal review is **not** complete. |

**Feature-gate expectation:** G8 is a new sharing of children’s educational performance with a teacher. At least one §6.1 answer is yes. Privacy / DPIA / ROPA notes belong in the **same later implementation PRs** as schema, not as a silent skip. Phase 0 drafted planned-processing notes only (`docs/DPIA.md` §9).

---

## Invariants to keep green every phase

Phase 6: leave route still absent. Join and handle-invite accept require disclosure. Progress 404 unless class owner + active member. T3 never in teacher payloads. Frozen set-work graded from stored JSON. CSV and audit are handles only. Full smoke must stay green.

- [x] No `POST /api/v1/me/classes/<id>/leave` (or web Leave control)
- [x] Join requires the student and shows disclosure (no silent add)
- [x] Handle invite does not add to the roster until accept + disclosure
- [x] Teacher class APIs 404 unless `teacher_owns_class` (progress requires active member of that class)
- [x] T3 free-text reflection body never in teacher JSON or HTML
- [x] Assignment student GET strips `correct_answer` / solution until after server grade
- [x] Frozen assignment answers graded from stored `problems_json`, not client keys
- [x] Account deletion leaves no `teacher_profiles` / `classes` / `class_memberships` / `class_assignments` / `class_assignment_recipients` / `class_invites` rows for that user; audit `actor_id` is SET NULL
- [x] CSV and audit payloads never include emails or T3
- [x] Full `scripts/run_smoke_tests.py` stays green (**71** passed, 2026-08-31, including `test_g8_phase1_smoke.py` … `test_g8_phase6_smoke.py`; hardening re-checked 2026-09-01)
- [x] `GENERATOR_LAUNCH_PATHS` and QOTD eursc skip unchanged unless the user explicitly asks

---

## Phase 4 set-work acceptance

- [x] Teacher can generate a preview of X questions (1–20) from a live catalogue topic
- [x] Assign to a subset of the roster **or** all active members
- [x] Different students can receive **different sets** via two assignments, not via per-row mutation of one set
- [x] Student cannot reroll the assigned items
- [x] Teacher sees n/X and score per recipient
- [x] Peer challenges and friend suggestions remain unchanged

---

## Phase 5 hardening acceptance

- [x] Teacher can invite by handle; student is not on the roster until they accept
- [x] Accept requires the same join disclosure as code join
- [x] Teacher can view a class audit log (handles, not emails)
- [x] Teacher can download roster and set-work CSVs (handles, not emails)
- [x] Erase leftovers include `class_invites` and `class_audit_events.actor_id`; export includes invites and teacher audit without keys or other people’s emails

---

## Phase 6 verification (done 2026-08-31)

- [x] Teacher: enable → class → code or handle invite → roster → remove → T0–T2 student detail → set work → scores → audit → CSV (`scripts/test_g8_phase6_smoke.py`)
- [x] Student: join (second class too) or accept invite after disclosure → no Leave → complete work
- [x] Guest / other teacher cannot see roster, progress, audit, or CSV
- [x] Sensitive: no T3; no emails in roster / audit / CSV payloads
- [x] Flask `url_map` has no `/leave` rule; `GENERATOR_LAUNCH_PATHS` unchanged
- [x] Full suite **71/71**
- [x] Post-track audit (2026-09-01): re-invite cap; blocked/archived join-by-code; 14-day invite expiry; class-work GET after remove; stale preview consume
