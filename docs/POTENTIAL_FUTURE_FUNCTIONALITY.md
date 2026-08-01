# Problem Bank — Potential Future Functionality

**Last updated:** 2026-07-31  
**Repository:** `maths_generator/physics-problem-bank`  
**Audience:** Product owners, developers, AI agents  

This document captures **ideas and designs that are not yet implemented**. It is separate from `docs/ARCHITECTURE.md`, which describes the live system. Items here may be promoted to implementation plans when prioritised.

---

## 1. How to read this document

| Status | Meaning |
|--------|---------|
| **Planned (designed)** | Requirements and options explored; ready to implement |
| **Idea** | Directionally useful; needs more design |
| **Deferred** | Explicitly out of scope for near-term work |

**Current product baseline:** Phase G G1–G7 shipped (weak topics through exam revision planner). Auto-correct is complete. **No teacher/class mode exists today.**

---

## 2. G8 — Teacher / class mode (planned, designed)

### 2.1 Summary

Give teachers an **optional teacher capability** with **class rosters** and **read-focused progress dashboards** over students who **explicitly join** their class. Reuse existing learning data (quizzes, weak topics, revision queue, skill gaps). This is **not** a full LMS.

**Handoff plan reference:** Phase G step G8 — “Teacher / class mode — B2B last.” Depends on lesson/quiz APIs (already shipped in G2).

### 2.2 Goals

| Goal | Detail |
|------|--------|
| **Optional teacher mode** | Not every account is a teacher; enable when needed |
| **Classes / rosters** | Named groups with a join mechanism |
| **Progress visibility** | Teachers see aggregated and per-student activity for roster members only |
| **Reuse existing analytics** | Weak topics, quiz history, lesson progress, revision queue — no duplicate tracking |
| **Safeguarding-first** | Student opt-in; no silent enrollment; minimal sensitive data in v1 |

### 2.3 Non-goals (version 1)

- School SSO / MIS / Google Classroom sync  
- Assigning homework or marking teacher-uploaded scripts  
- Live lesson control or seating plans  
- Parent accounts  
- Replacing friends / follows / study buddies (peer social stays separate)  
- Free-text reflection notes visible to teachers (high risk for minors)

### 2.4 Actors

| Actor | Capability |
|-------|------------|
| **Student** | Same app as today; optionally joins one or more classes |
| **Teacher** | Optional teacher mode; create classes; view roster progress |
| **Class** | Named group with optional level/subject metadata and join code |

One account may be both teacher and student (e.g. tutor who also practises).

### 2.5 Design decisions and options

#### A. How “teacher” exists

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Soft flag** — `is_teacher` / “Enable teacher mode” | Fast; one login | Easy to abuse | **Start here (v1)** |
| **Role + verification** — email domain or manual approve | Better trust | Approval flow needed | Phase 2 |
| **Org/school entity** — school → teachers → classes | Real B2B | Heavy | Later |

Design schema with nullable `org_id` so B/C can layer on without rewrite.

#### B. How students join a class

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Class join code** (6–8 chars, rotatable) | Simple classroom UX | Codes can leak | **v1 primary** |
| **Invite link** (token URL) | Nice share UX | Same leak risk | Optional alongside code |
| **Teacher invites by handle** + student accepts | Explicit consent | Needs handle knowledge | **v1 secondary** |
| **Email invite** | Familiar for schools | Email infra + minors | Later |
| **Teacher adds silently** | Zero friction | Bad for privacy | **Never** |

**Default package:** Join code for bulk in-class join; optional invite-by-handle with accept. Codes expire or rotate.

#### C. What teachers can see (data tiers)

| Tier | Data | v1? |
|------|------|-----|
| **T0 — Class aggregates** | Class avg quiz %, top weak topics, activity counts | Yes |
| **T1 — Named progress** | Per student: weak topics, recent quiz scores, lesson progress, due-today count | Yes |
| **T2 — Diagnostic** | Skill-gap labels (reflection chip rollups, not free text) | Optional toggle |
| **T3 — Full reflections** | Free-text “what tripped me up” notes | **No** |

Also **exclude:** passwords, classmates’ emails, private follows/feed, study-buddy content.

#### D. What teachers can do (beyond view)

| Option | Scope | v1? |
|--------|-------|-----|
| **Monitor only** | Dashboard + optional CSV export | **Yes (MVP)** |
| **Suggest** | “Try this topic” link (like existing suggestions) | Phase 2 |
| **Assign** | “Complete quiz X by Friday” + tracking | Later |
| **Create class content** | Custom questions / lessons | Out of scope |

#### E. Privacy and consent

**Must-haves:**

1. Student **opts in** by joining or accepting invite.  
2. Student can **leave** anytime; teacher can **remove**.  
3. Clear copy before join: “Your teacher can see X.”  
4. Teacher sees only **roster members**, never whole user directory.  
5. Assume many GCSE users are minors — default to **less** data.  
6. Optional audit log for teacher views of individual student detail (G8b).

**Recommended consent model:** Join implies T1 visibility. T2 (skill-gap chips) behind explicit student checkbox on join or in settings.

### 2.6 Proposed data model (MVP)

```
teacher_profiles
  user_id PK, enabled_at, display_name_optional

classes
  id, teacher_id, name, level?, subject?,
  join_code, join_code_rotated_at, created_at, archived_at?

class_memberships
  class_id, student_id, status (active|left|removed),
  joined_at, left_at,
  share_skill_gaps INTEGER DEFAULT 0
  UNIQUE(class_id, student_id)

class_invites (optional v1)
  id, class_id, from_teacher_id, to_user_id,
  status (pending|accepted|declined), created_at
```

Progress metrics read from existing tables: `quiz_attempts`, weak-topic analysis, `lesson_progress`, revision queue, skill gaps (only if `share_skill_gaps`).

### 2.7 Proposed UX

**Teacher journey**

1. Profile → “Teacher mode” → Enable  
2. Create class (name, optional level/subject) → receive join code  
3. Class page: roster, last active, quiz count (7d), top weak topics (aggregate)  
4. Student detail: weak topics, recent quizzes, due-today count, skill patterns if shared  

**Student journey**

1. “Join a class” → enter code or accept invite  
2. Confirm visibility disclosure → Join  
3. Profile lists enrolled classes; Leave class anytime  

### 2.8 Proposed API sketch

| Method | Path |
|--------|------|
| POST | `/api/v1/me/teacher/enable` |
| POST / GET | `/api/v1/teacher/classes` |
| POST | `/api/v1/teacher/classes/<id>/rotate-code` |
| GET | `/api/v1/teacher/classes/<id>/roster` |
| GET | `/api/v1/teacher/classes/<id>/students/<id>/progress` |
| POST | `/api/v1/me/classes/join` `{ "code": "..." }` |
| POST | `/api/v1/me/classes/<id>/leave` |
| GET | `/api/v1/me/classes` |

Web UI first; APIs in same pass so mobile can follow.

**Authz helper:** `teacher_can_view(conn, teacher_id, student_id) → class_id | None` — checked on every progress endpoint.

### 2.9 Implementation approach

| Approach | Verdict |
|----------|---------|
| **Thin teacher layer** — new `models/classes.py`; progress endpoints call G1–G7 helpers with membership authz | **Preferred** |
| **Extend study_pairs** for teacher–student | Rejected — wrong trust model |
| **Org-first B2B** with billing | Deferred |

### 2.10 Phased delivery

#### G8a — MVP (ship first)

- Opt-in teacher mode  
- Create class + join code  
- Join / leave / remove  
- Class roster + aggregate stats (T0)  
- Per-student T1 progress (weak topics, recent quizzes, lesson summary)  
- Smoke tests + `docs/API.md` updates  

#### G8b — Hardening

- Invite-by-handle  
- Rotate / expire join codes  
- Skill-gap sharing toggle (T2)  
- CSV export for class  
- Teacher view audit log  

#### G8c — B2B polish (later)

- Teacher verification / school org entity  
- “Suggest topic to class” or lightweight assignments  
- Multi-teacher co-teaching  
- GDPR export/delete for class-related data  

### 2.11 Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Join codes shared outside class | Rotate code; visible member list; teacher remove |
| Over-sharing reflections | No free-text to teachers in v1 |
| Teacher views non-students | Strict membership check on every API |
| Scope creep into LMS | Monitor-only MVP; assignments explicitly later |
| Large class performance | Cap page size; aggregate queries; index memberships |

### 2.12 Recommended default package

If implementing G8 without further product decisions:

1. Soft teacher opt-in  
2. Join codes + leave/remove  
3. T1 per-student + T0 class aggregates; no reflection text  
4. Monitor only (no assignments)  
5. Thin module on existing G1–G7 analytics  
6. Ship **G8a**, then iterate from real usage  

### 2.13 Open product questions

1. Prioritise solo tutors (≤40 students) or multi-teacher orgs soon?  
2. Allow students in many classes simultaneously? (Recommend: yes)  
3. Include skill-gap chips in MVP or only after student toggle?  
4. Any hard “teacher must never see X” beyond free-text reflections?

---

## 3. Other potential future ideas

These are **not designed to the same depth as G8**. Listed for prioritisation discussion.

### 3.1 Native mobile app

- **Idea:** Consume existing `/api/v1/*` with Bearer auth; offline cache for saved problems.  
- **Depends on:** Stable API (largely done), push notifications (not built).  
- **Status:** Idea  

### 3.2 Push notifications

- **Idea:** Mobile/web push for challenges, study-pair invites, revision due reminders.  
- **Status:** Idea — in-app notifications exist; push does not  

### 3.3 Assignments / teacher-suggested topics (post-G8)

- **Idea:** Teacher sends “practise topic X” to class; track completion.  
- **Status:** Deferred — after G8a monitor-only MVP  

### 3.4 School / org billing (B2B)

- **Idea:** School accounts, seat licensing, admin dashboard.  
- **Status:** Deferred — G8c territory  

### 3.5 Expanded curriculum coverage

- **Idea:** More GCSE/A-Level/MYP topics; additional subjects.  
- **Status:** Ongoing content work, not a single feature flag  

### 3.6 Improved profile subject dropdown for revision planner

- **Idea:** Client-side subject list updates when level changes (currently server-rendered for saved plan level only).  
- **Status:** Idea — small UX polish  

### 3.7 Logged-out MCQ cohort recording

- **Idea:** Record anonymous cohort stats for logged-out MCQ attempts (G5 currently strongest for logged-in flows).  
- **Status:** Idea — privacy review needed  

### 3.8 Parent / guardian view

- **Idea:** Read-only progress for linked child account.  
- **Status:** Deferred — significant consent/safeguarding design  

### 3.9 Advanced spaced repetition

- **Idea:** SM-2 or similar algorithm replacing rule-based G3 queue.  
- **Status:** Idea — G3 works; upgrade if data shows benefit  

### 3.10 AI tutoring depth

- **Idea:** Expand lesson/quiz assist beyond current explain endpoint.  
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
| **G8** | **Teacher / class mode** | **Designed — not started** |

---

## 5. Document maintenance

When a feature ships:

1. Move its description from this file into `docs/ARCHITECTURE.md`.  
2. Add API details to `docs/API.md`.  
3. Add smoke tests under `scripts/`.  
4. Update `Problem_Bank_AI_Handoff_Plan.md` status table if agents rely on it.

When prioritising G8 or other items, record the chosen options (especially §2.13 answers) at the top of the relevant section.
