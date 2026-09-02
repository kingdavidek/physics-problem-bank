# Problem Bank — Potential Future Functionality

**Last updated:** 2026-08-31  
**Repository:** `maths_generator/physics-problem-bank`  
**Audience:** Product owners, developers, AI agents  

This document captures **ideas and designs that are not yet implemented**. It is separate from `docs/ARCHITECTURE.md`, which describes the live system. Items here may be promoted to implementation plans when prioritised. Agents: see `docs/AI_HANDOFF.md` first (includes **engagement phases E1–E3**).

---

## 1. How to read this document

| Status | Meaning |
|--------|---------|
| **Planned (designed)** | Requirements and options explored; ready to implement |
| **Idea** | Directionally useful; needs more design |
| **Deferred** | Explicitly out of scope for near-term work |

**Current product baseline:** Phase G G1–G7 shipped. Auto-correct complete. Solid-draft security done. **Engagement E1–E3 shipped.** **Engagement E4** (content depth) is below §3.0. Mobile polish **M0–M4 done** (`docs/MOBILE.md`). **G8 teacher/class mode** is designed with locked decisions (2026-08-30); **Phases 0–6 complete** — `docs/G8_TEACHER_HANDOFF.md`.

---

## 2. G8 — Teacher / class mode (designed; Phases 0–6 complete)

**Status:** Phases 0–6 complete (2026-08-30 / 2026-08-31) — teacher enable, classes, join codes, roster, teacher-only remove, T0–T2 dashboards, frozen set-work, handle invites, audit log, CSV, verification. Track closed unless the user opens a follow-up.  
**Decisions locked:** 2026-08-30 (David).  
**Delivery track:** `docs/G8_TEACHER_HANDOFF.md` (one phase per user cue).  
**Review contract:** `docs/G8_TEACHER_REVIEW_RUBRIC.md`.

### 2.1 Summary

Give **solo tutors and classroom teachers** an optional teacher capability: **class rosters**, **progress dashboards**, and the ability to **set a frozen set of specific questions** to some or all students in a class. Students **join by code** (consent). After that, **only the teacher can remove** a student from the class. Reuse G1–G7 analytics. This is **not** a full LMS (no custom lessons, no uploaded scripts, no school SSO).

### 2.2 Locked product decisions (2026-08-30)

| # | Question | Decision |
|---|----------|----------|
| 1 | Audience | **Solo tutors and teachers** for now. Soft teacher flag. No school org, verification, or multi-teacher co-teaching in this track. Cap **40 active students per class**. Nullable `org_id` on `classes` so B2B can layer later. |
| 2 | Many classes | **Yes.** A student may be active in more than one class at once. |
| 3 | Skill-gap chips (T2) | **In the dashboard from the first progress phase**, as part of the join disclosure — **no extra student checkbox**. Chips are G6 rollups, not free text. |
| 4 | Extra “never see” list | **No.** The only progress-data hard block remains **T3 free-text reflections**. Operational exclusions still apply (passwords, emails, private follows/feed, buddy copy). |
| 5 | Leaving a class | **Teacher-only.** No student Leave control. Account **deletion** still erases memberships (GDPR), which is not “leave class”. |
| 6 | Set work | **In this track** (not deferred). Teacher sets **X frozen questions** for **selected students or the whole class**. |

### 2.3 Goals

| Goal | Detail |
|------|--------|
| **Optional teacher mode** | Soft flag; one login; tutors who also practise keep a student app |
| **Classes / rosters** | Named groups; join code; teacher remove |
| **Progress visibility** | T0 class aggregates + T1 named progress + T2 skill-gap chips, roster only |
| **Set work** | Same frozen question set assigned to n students or all; teacher sees completion |
| **Reuse analytics** | Weak topics, quiz history, lesson progress, revision queue, skill-gap chips — no duplicate tracking of study history |
| **Safeguarding** | Join is opt-in; no silent add; no T3 notes; teacher sees roster members only |

### 2.4 Non-goals (this track)

- School SSO / MIS / Google Classroom / org billing
- Teacher-uploaded worksheets or custom lesson authoring
- Live lesson control, seating plans, parent accounts
- Replacing friends / follows / study buddies
- T3 free-text reflection notes visible to teachers
- Student self-remove from a class
- Due-by-Friday calendars and late-work workflows (completion tracking is enough for v1)

### 2.5 Actors

| Actor | Capability |
|-------|------------|
| **Student** | Same app as today; joins one or more classes by code; **cannot** leave; completes assigned question sets |
| **Teacher** | Enable teacher mode; create classes; rotate join code; remove students; view T0–T2; set work |
| **Class** | Named group, optional level/subject, join code, ≤40 active members |

One account may be both teacher and student.

### 2.6 Join, stay, and remove

| Action | Who |
|--------|-----|
| Join with code (after disclosure) | Student |
| Accept handle invite (after disclosure) | Student |
| Rotate / expire join code | Teacher |
| Remove from roster | **Teacher only** |
| Silent add to roster | **Never** |
| Erase memberships with the account | System (GDPR delete) |

Join disclosure must say, in plain language: the teacher can see class and named progress (including skill-gap labels), can set questions, and **only the teacher can take you off the class**. If the student wants to leave, they ask the teacher.

### 2.7 What teachers can see (data tiers)

| Tier | Data | This track |
|------|------|------------|
| **T0 — Class aggregates** | Avg quiz %, top weak topics, activity counts, set-work completion | Yes |
| **T1 — Named progress** | Per student: weak topics, recent quizzes, lesson summary, due-today count | Yes |
| **T2 — Diagnostic** | Skill-gap **chip** rollups (not free text) | **Yes** — join disclosure, no extra toggle |
| **T3 — Full reflections** | Free-text “what tripped me up” | **No** |

Also exclude: passwords, classmates’ emails, private follows/feed, study-buddy content.

### 2.8 Set work (specific questions)

Not a “practise this topic” nudge and not peer `quiz_challenges`.

1. Teacher picks **level / subject / topic / difficulty / mode** from the live generator catalogue and a count **X** (cap **1–20**).
2. Server **generates and freezes** X problem payloads (same session-trust model as challenges / shared questions — stored JSON, graded from the stored set, never from a client-supplied answer key).
3. Teacher assigns that **same frozen set** to **selected roster members** or **all active members**.
4. To give Alice different questions from Bob, the teacher creates **two sets** and assigns each to the matching students.
5. Students open **My class work**, answer the frozen items, cannot reroll onto a different bank item.
6. Teacher sees per-student **n / X** and scores.

Do **not** reuse `study_pairs`. Do **not** fan out `question_suggestions` (1:1 optional inbox). New assignment tables (names may be refined in implementation). Friend challenges stay peer-vs-peer.

### 2.9 Proposed data model

```
teacher_profiles
  user_id PK, enabled_at

classes
  id, teacher_id, name, level?, subject?, org_id NULL,
  join_code, join_code_rotated_at, created_at, archived_at?

class_memberships
  class_id, student_id, status (active|removed),
  joined_at, removed_at, removed_by_teacher_id
  UNIQUE(class_id, student_id)

class_assignments
  id, class_id, teacher_id,
  level, subject, topic, mode, difficulty,
  problems_json, question_count, created_at

class_assignment_recipients
  assignment_id, student_id, status (assigned|complete),
  answers_json, score, completed_at
  UNIQUE(assignment_id, student_id)
```

Progress metrics still read from existing G1–G7 tables. T2 skill gaps are included whenever the student is an active member (no `share_skill_gaps` column).

### 2.10 Proposed UX

**Teacher**

1. Profile → Enable teacher mode
2. Create class → join code
3. Roster: last active, quiz count (7d), remove student
4. Student detail: T1 + T2 chips
5. Set work: pick topic / X questions / generate preview → assign to selected or all
6. Assignment results: n/X and scores

**Student**

1. Join a class → disclosure → enter code
2. Profile lists classes (no Leave)
3. My class work → frozen questions → Check

### 2.11 Proposed API sketch

| Method | Path |
|--------|------|
| POST | `/api/v1/me/teacher/enable` |
| POST / GET | `/api/v1/teacher/classes` |
| POST | `/api/v1/teacher/classes/<id>/rotate-code` |
| GET | `/api/v1/teacher/classes/<id>/roster` |
| POST | `/api/v1/teacher/classes/<id>/members/<student_id>/remove` |
| GET | `/api/v1/teacher/classes/<id>/students/<id>/progress` |
| POST | `/api/v1/teacher/classes/<id>/assignments` |
| GET | `/api/v1/teacher/classes/<id>/assignments/<id>` |
| POST | `/api/v1/me/classes/join` `{ "code": "..." }` |
| GET | `/api/v1/me/classes` |
| GET | `/api/v1/me/class-work` |
| POST | `/api/v1/me/class-work/<assignment_id>/answer` |

**No** `POST /api/v1/me/classes/<id>/leave`.

**Authz:** `teacher_can_view(conn, teacher_id, student_id)` and `teacher_owns_class` on every class/progress/assignment endpoint.

### 2.12 Implementation approach

| Approach | Verdict |
|----------|---------|
| Thin layer — `models/classes.py` + assignment module; G1–G7 helpers behind membership authz | **Preferred** |
| Extend `study_pairs` or `quiz_challenges` | Rejected |
| Org-first B2B | Deferred |

### 2.13 Delivery on this track

Phases are in `docs/G8_TEACHER_HANDOFF.md`. Order: contract → teacher/classes → roster (teacher-only remove) → T0–T2 dashboards → set work → hardening → verification.

**Later (not this track):** teacher verification, school org, co-teaching, due-date workflows.

### 2.14 Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Join codes leak | Rotate code; roster; teacher remove |
| Student cannot leave a bad class | Teacher remove; GDPR account delete; join disclosure; report/block still exist for the person |
| Frozen set leaks answers | Same as challenges: strip keys from student GET until graded server-side |
| Over-sharing reflections | No T3 |
| Teacher views non-students | Membership check on every API |
| LMS scope creep | No custom content; no SSO; set work is frozen generator items only |
| Large classes | Cap 40 active members; paginate roster |

---

## 3. Other potential future ideas

These are **not designed to the same depth as G8**. Listed for prioritisation discussion.

**Near-term engagement (E1–E3, shipped)** and the planned **E5** are tracked in `docs/AI_HANDOFF.md` §6 — not duplicated here.

### 3.0 Engagement Phase E4 — Content depth

E1–E3 shipped 2026-08-15. Of the three E4 items below, only **E4.1** is scheduled; the other two remain stretch.

#### 3.0.1 New real-world GCSE question styles

| | |
|--|--|
| **Idea** | Everyday scenarios (cooking, sport, shopping, travel) for high-traffic GCSE topics, keeping the same graders and session trust model. |
| **Scope now** | A third generator **question style** (`real_world`) alongside Standard and Multiple Choice, piloted on **percentages (`fdp`), ratio and proportion, compound measures**. New variants inside the existing generators — no second problem engine, no A/B testing in v1. |
| **Plan** | **`docs/REAL_WORLD_QUESTIONS.md`** — step-by-step implementation, content authoring rules, and tests |
| **Status** | **Planned and specified** — ready to implement |

#### 3.0.2 Sub-mascot story / farm perks

| | |
|--|--|
| **Idea** | Deeper mascot meta-game (story arcs, collectibles, “farm” perks) beyond E1’s bot QOTD card and E3’s alien buddy. |
| **Action** | Only if DAU / session length clearly lift after E1–E3. Needs dedicated schema, economy design, and ongoing content — treat as its **own project**, not a quick add-on. |
| **Depends on** | E1.2 mascot bot + E3.1 buddy patterns; product metrics |
| **Status** | Deferred stretch |
| **Do not confuse with** | **E6 Guide** (`docs/ANIMATION_ONBOARDING.md`) — origin story + tours + celebration. That is lore and overlay UX, not an economy. |

#### 3.0.3 Desmos-like graphing / transform SVGs

| | |
|--|--|
| **Idea** | Interactive graphing / transformation playground (Desmos-class UX). |
| **Action** | **Defer indefinitely** as a custom Canvas/SVG engine (likely 2000+ lines, high maintenance). If users explicitly request graphs, prefer **embedding a maintained library** (e.g. Chart.js / Plotly) for basic visualisations first — still only on demand. |
| **Status** | Deferred — do not schedule unless there is a clear user request and capacity |

### 3.1 Mobile polish (app-like PWA) + Play Android — planned

- **Plan:** Polish the existing site (phases **M0–M4**), then optionally ship Android via **TWA** (**M5** HTTPS → **M6** wrapper → **M7** Play listing). One web codebase — not a separate native UI.  
- **Doc:** `docs/MOBILE.md` (canonical step-by-step for agents).  
- **Status:** **Done (M0–M4)** — see `docs/MOBILE.md`. M5–M7 gated on production HTTPS.  

### 3.2 Native mobile app (beyond TWA)

- **Idea:** Full native or Capacitor app with offline cache / richer push — only if TWA + PWA prove insufficient. Prefer finishing `docs/MOBILE.md` through **M7** first.  
- **Depends on:** Stable API (largely done), push notifications (not built).  
- **Status:** Idea — after M5–M7 if still needed  

### 3.3 Push notifications

- **Idea:** Mobile/web push for challenges, study-pair invites, revision due reminders. In-app notifications and the weekly email digest already exist; push means waking the user when the app is closed.  
- **Blocked by:** a production HTTPS origin (`docs/MOBILE.md` M5). The Push API needs a secure origin, so this cannot be tested end to end today.  
- **Scope when unblocked:** VAPID keys, `push_subscriptions` table, subscribe/unsubscribe endpoints, `push`/`notificationclick` handlers in `static/js/sw.js`, default-off opt-in, quiet hours, no question content or real names in payloads — written up as **E5.7 in `docs/ENGAGEMENT_E5.md`**.  
- **Status:** Specified, gated on M5  

### 3.4 Assignments / teacher-suggested topics

- **Idea:** Teacher sets frozen generator questions for selected or all class members.
- **Status:** **Shipped in G8 Phase 4** — see §2.8 and `docs/G8_TEACHER_HANDOFF.md`. Do not implement as a separate track.

### 3.5 School / org billing (B2B)

- **Idea:** School accounts, seat licensing, admin dashboard.  
- **Status:** Deferred — G8c territory  

### 3.6 Expanded curriculum coverage

- **Idea:** More GCSE/A-Level/MYP topics; additional subjects.  
- **Status:** Ongoing content work, not a single feature flag  

### 3.7 Improved profile subject dropdown for revision planner

- **Idea:** On `/profile`, the exam-plan Subject list is server-rendered for one level (the saved plan's, else `gcse`), so changing Level in the browser can leave an invalid level/subject pair selected. Filter the list client-side, reusing `initGeneratorForm`'s `setOptionVisibility` helper in `static/js/site.js`.  
- **Status:** Specified as **E5.6 in `docs/ENGAGEMENT_E5.md`** — small UX polish  

### 3.8 Logged-out MCQ cohort recording

- **Idea:** Record anonymous cohort stats for logged-out MCQ attempts (G5 currently strongest for logged-in flows).  
- **Status:** Idea — privacy review needed  

### 3.9 Parent / guardian view

- **Idea:** Read-only progress for linked child account.  
- **Status:** Deferred — significant consent/safeguarding design  

### 3.10 Advanced spaced repetition

- **Idea:** SM-2 or similar algorithm replacing rule-based G3 queue.  
- **Status:** Idea — G3 works; upgrade if data shows benefit  

### 3.11 AI tutoring depth

- **Idea:** Expand lesson/quiz assist beyond current explain endpoint (E1.1 validates the existing path first — see handoff).  
- **Status:** Idea — optional AI already env-gated  

---

## 4. Relationship to Phase G roadmap

| Step | Feature | Status |
|------|---------|--------|
| G1 | Weak topics dashboard + API | ✅ Shipped |
| G2 | Quiz history API | ✅ Shipped |
| G3 | Spaced revision queue | ✅ Shipped |
| G4 | Wrong-answer reflection | ✅ Shipped |
| G5 | Anonymous cohort stats | ✅ Shipped |
| G6 | Cross-topic skill gaps | ✅ Shipped |
| G7 | Revision planner | ✅ Shipped |
| **G8** | **Teacher / class mode** | **Designed, decisions locked 2026-08-30 — Phases 0–6 complete** (`docs/G8_TEACHER_HANDOFF.md`) |
| E1–E3 | Engagement (assist smoke, mascot QOTD, FTS, avatars, buddy, friend accuracy LB) | **E1–E3 shipped** |
| E4.1 | Real-world question style (percentages, ratio, compound measures) | Planned — `docs/REAL_WORLD_QUESTIONS.md` |
| — | European School Integrated Science S1–S3 (new `eursc` level, 46 syllabus modules) | Fully planned — `docs/EUROPEAN_SCHOOL_SCIENCE.md` |
| E4.2 / E4.3 | Mascot farm perks, Desmos-class graphs | Stretch — §3.0 this file |
| E5 | Retention polish | **E5.1–E5.6 shipped**; E5.7 push blocked — `docs/ENGAGEMENT_E5.md` |
| **E6 / Phase A** | Guide & celebration (origin story, first-visit tours, badge/streak moments) | **A1–A6 + B shipped** (origin, tours, reward beats, `guide_json` persist + Replay intro, CSS streak fire, overlay wink/nod/shake/tap). Spec: `docs/ANIMATION_ONBOARDING.md` |

---

## 5. Document maintenance

When a feature ships:

1. Move its description from this file (or from handoff §6) into `docs/ARCHITECTURE.md`.  
2. Add API details to `docs/API.md`.  
3. Add smoke tests under `scripts/`.  
4. Update `docs/AI_HANDOFF.md` status table.

G8 product decisions are locked in §2.2. Do not reopen them without an explicit user cue. Delivery phases live in `docs/G8_TEACHER_HANDOFF.md`.
