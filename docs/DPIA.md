# Data Protection Impact Assessment (DPIA)

**Controller:** set via `CONTROLLER_NAME` (placeholder until S0.1 is completed by the operator)  
**Contact:** `PRIVACY_CONTACT_EMAIL`  
**Last reviewed:** 2026-08-31  
**Status:** Draft for operator review — not legal advice  
**Companion:** `docs/SECURITY_AND_GDPR.md`, `docs/ROPA.md`, `docs/SUBPROCESSORS.md`

This DPIA covers Problem Bank, a UK-facing GCSE/A-level practice site whose users are **mainly children aged 13+**. A DPIA is required because the service is offered directly to children and because practice history, weak-topic analysis, streaks, and friend leaderboards amount to **profiling** of educational performance.

---

## 1. Nature, scope, context, and purposes

| | |
|---|---|
| **What** | Accounts for study practice: generated questions, quizzes, lessons, reflections, streaks, optional follows and friend challenges. |
| **Who** | Students 13+. No date of birth is stored; age is a registration checkbox. |
| **Where** | UK-facing. Hosting location is confirmed at deploy. |
| **Data** | Email, handle, password hash, study record, social graph, hashed rate-limit keys. No real name, photos, payment data, health, ethnicity, or SEN fields. |
| **Purposes** | Deliver the study service (contract); prevent abuse (legitimate interests); optional weekly digest (consent); optional AI lesson assist **off in production unless explicitly enabled** (consent at point of use if ever enabled). |

Processing is limited to what the product already does. There is no advertising, analytics, or third-party tracking.

---

## 2. Necessity and proportionality

The study record is necessary to provide progress, revision queues, and difficulty gating. Social features are optional and default to **followers-only** profiles with activity toggles **off**. Digest mail is opt-in and default off. Lesson assist does not run in production unless `LESSON_ASSIST_ENABLED=1`.

Collecting a real name, school, or date of birth would be disproportionate; the product does not.

---

## 3. Consultation

Users are told, in language a 13-year-old can follow, on `/privacy/simple`. Parents can email the privacy contact. The ICO Children's Code (Age Appropriate Design Code) is the primary framework. This draft should be read by someone qualified before public launch.

---

## 4. Risks and mitigations

| Risk | Likelihood / impact (unmitigated) | Mitigation already in place | Residual / gap |
|---|---|---|---|
| A child's academic weaknesses are visible to others | High / High | Weak topics, revision queues, and skill gaps are private to the account. Friend leaderboards are friends-only; there is **no global ranking**. | Keep weak topics out of the public profile and activity feed forever. **G8 (Phase 1–5 shipped):** a teacher who the student joined sees T0–T2 and set-work completion for roster members only. T3 free-text stays off. Join is opt-in (code or handle invite); only the teacher can remove. |
| Stranger contact through follows, challenges, suggestions | Medium / High | No DMs. Block and report exist. System bot cannot be messaged as a person. Follows are one-way and do not expose email. | S2: report action on suggestions; documented escalation. Operator must read reports. |
| Public exposure of study activity | High / High | Default visibility is `followers_only`. Last topic, last activity, lesson progress, and quiz stats default **off**. Logged-out visitors see handle (and the private-profile page), not study data. | Users can still opt into a public profile; the settings page explains that public means anyone on the internet. |
| Competitive pressure / compulsive use (streaks, boards, buddy nudges) | Medium / Medium | Friends-only boards. Dismissible buddy. No streak-loss shaming copy. No push notifications until production HTTPS (E5.7), and quiet hours are specified there. **A1–A4 Guide (2026-08-27):** optional onboarding dialogue, first-visit section tours, and once-only first-correct / lesson-complete reward modals; Skip / Not now / Escape always; seen-flag in localStorage only; no extra processors. | Children's Code standard 12/13: each tour/origin/reward once; no streak-loss shaming; no night-time push or public ranking. **G8 (Phase 4 shipped):** teacher-set frozen question work can add class pressure — completion is class-roster only, no public ranking of assignments. |
| Free-text fields leaking name, school, or address | Medium / High | Length caps; Jinja autoescape. Child-friendly notice: do not put real name, school, or address in notes. | Cannot fully prevent. Moderation/report remains the backstop. |
| Child's question sent to an LLM (OpenAI / Anthropic / DeepSeek) | High / High if enabled | **Option A:** disabled in production unless `LESSON_ASSIST_ENABLED=1`. Payload must not contain handle, email, or user id. Mock mode for local/CI. | Do not enable DeepSeek (no UK adequacy) without an IDTA and transfer risk assessment. Prefer a UK/EU or adequacy-covered provider with a DPA and no-training commitment. |
| Account takeover / rights requests to the wrong person | Medium / High | Password reset (60 min, single use). Email verification required before export and deletion. Password change on settings. | S1: per-account login lockout. Operator CLI erase/export for email requests. |
| IP addresses retained forever | Medium / Medium | Rate-limit and lesson-assist keys store a keyed hash, not the raw IP. Daily prune. | Host access logs still need a 30-day cap on the hosting panel (operator). |
| Breach of the SQLite file / backups | Medium / High | Parameterised SQL, hashed passwords, hashed API tokens, HTTPS cookies in production. Encrypted backups (S1) and a quarterly restore drill (`docs/CADENCE.md`). | Operator must set `PB_BACKUP_PASSPHRASE` and run the drill on the host. |
| `PB_TESTING=1` in production (CSRF and rate limits off) | Low / Critical | Boot refuses to start when `PB_TESTING=1` is combined with `SITE_URL=https://…` or `FLASK_ENV=production`. | Keep the flag out of the hosting env. |

---

## 5. Children's Code mapping (abbreviated)

| Standard | How this product answers it |
|---|---|
| 1 Best interests | Study tool first; no ads, no dark-pattern sharing. |
| 2 Data protection by design | High-privacy defaults; hashed IPs; no extra identity fields. |
| 3 Age appropriate | 13+ gate; simple privacy page; no under-13 accounts. |
| 4 Transparency | `/privacy`, `/privacy/simple`, `/terms`, footer and register links. |
| 5 Detrimental use | No profiling for ads; educational profiling stays on-account. **G8:** T0–T2 and set-work scores may be shown to a teacher after join — not for ads; no T3 (§9). |
| 6 Default settings | Followers-only; activity toggles off. |
| 7 Data minimisation | Email + handle only for identity. |
| 8 Data sharing | Subprocessors listed; lesson assist off by default. **G8:** sharing T0–T2 and set-work completion with a teacher after join is not a new processor — see §9. |
| 12 Nudge techniques | Friends-only competition; no public league table. Origin overlay and (later) tours are dismissible, once per browser, no analytics. **G8:** set-work is a class nudge — roster only, no public assignment ranking (§9). |
| 13 Connected toys / geolocation | Not used. Permissions-Policy disables camera/mic/geo. |

---

## 6. Legitimate interests (abuse prevention)

**Interest:** keep the service usable and safe (rate limits, blocks, reports, hashed IP buckets).  
**Necessity:** without this, a single IP or account can spam register/login/share.  
**Balancing:** children are the users, so we hash IPs, prune buckets in 7 days, keep generic error messages, and do not build advertising profiles from the same data. Users can object by contacting the privacy address; core security processing may still apply.

---

## 7. Decision

Proceed to public launch **only after**:

1. Operator completes S0.1 at public launch (`docs/OPERATOR_LAUNCH.md`: real controller name, monitored privacy inbox, ICO fee / registration number in `ICO_REGISTRATION_NUMBER`).
2. `docs/SECURITY_AND_GDPR.md` Phase S0 code items remain green (they are implemented as of this date).
3. Phase S1 backup encryption, S2 CSP/self-hosting, and S3 cadence (`docs/CADENCE.md`) are implemented. Keep `PB_BACKUP_PASSPHRASE` off git.

**Review triggers:** any new data category; teacher/class mode (G8); enabling lesson assist; adding analytics; transferring hosting or mail provider; a personal-data breach.

---

## 8. Review log

| Date | What changed | Outcome |
|---|---|---|
| 2026-08-26 | S0–S2 code shipped; S3 cadence runbook and restore-drill CLI added | Draft still pending qualified review before public launch. Next scheduled re-read: first quarter after launch, or sooner on a review trigger. |
| 2026-08-27 | E6 A5 `guide_json` on `user_profile_settings` (boolean seen-flags; no extra processors). Privacy notice + ROPA updated. | Residual: dismissible onboarding persisted per account. Replay intro is user-initiated. |
| 2026-08-30 | G8 product decisions locked (solo tutors/teachers; many classes; T2 chips with join disclosure; teacher-only remove; frozen set-work in-track). Implementation **not started**. | Draft still pending qualified review. |
| 2026-08-30 | G8 **Phase 1:** `teacher_profiles` + `classes` schema; enable/create/list/archive/rotate-code. ROPA row 9; privacy notices; retention; erase/export inventory. Join still not shipped. | Draft still pending qualified review. Sharing a child’s study record with a teacher remains **planned** until Phase 2 join. |
| 2026-08-30 | G8 **Phase 2:** `class_memberships`; join-by-code after disclosure; teacher-only remove; cap 40; no Leave. Roster is handles not emails. Notices + ROPA + export `classes_joined` updated. | Draft still pending qualified review. Sharing a child’s study record with a teacher is **live after join**. Dashboards (T0–T2) still Phase 3. |
| 2026-08-30 | G8 **Phase 3:** T0 class aggregates + T1 named progress + T2 skill-gap chips for roster members. Authz on every progress endpoint. T3 free-text never in teacher JSON/HTML. | Draft still pending qualified review. Educational profiling disclosed to the joined teacher, roster-only. Set-work still Phase 4. |
| 2026-08-31 | G8 **Phase 4:** frozen set-work from the live catalogue; preview then assign; student class-work cannot reroll; teacher n/X + scores; graded from stored JSON; student GET strips keys until after grade. No Leave. No T3. | Draft still pending qualified review. Set-work completion is roster-only (std 13). |
| 2026-08-31 | G8 **Phase 5:** handle invites (accept + disclosure; no silent add); teacher audit log; roster/set-work CSV (handles only); erase leftovers for `class_invites` / audit `actor_id`; export invites + teacher audit without keys or other people’s emails. Pending invites pruned after 14 days. No Leave. No T3. | Draft still pending qualified review. |
| 2026-08-31 | G8 **Phase 6:** verification. Full smoke **71/71**; sample teacher/student flows; no Leave route in `url_map`; no T3 in teacher JSON/HTML; invites still require disclosure; CSV/audit handles only. Track complete. | Draft still pending qualified review. Qualified legal review still required before public HTTPS. |

---

## 9. G8 teacher / class mode (join, T0–T2, set-work, and hardening shipped; verified)

**Status:** Phase 1–6 shipped and verified 2026-08-30 / 2026-08-31 (`teacher_profiles`, `classes`, `class_memberships`, `class_assignments`, `class_assignment_recipients`, `class_invites`, `class_audit_events`; enable / create / list / archive / rotate-code / join / handle invite / roster / teacher remove / T0–T2 dashboards / frozen set-work / audit / CSV). Sample flows confirmed in `scripts/test_g8_phase6_smoke.py`. This section remains a draft residual/gap note. It is **not** a completed qualified legal review and is **not** legal advice.

**Design (locked):** `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §2.2. Do not reopen those decisions here.

### 9.1 What would be processed

Optional teacher capability for solo tutors and classroom teachers (not school orgs). After a student **joins by code or accepts a handle invite**, the teacher can see **T0–T2** progress for roster members and can **set frozen generator questions**. Processing stays on the same controller and host — the teacher is another registered user, not a new subprocessor.

New record types: teacher flag; class metadata; join codes; memberships; handle invites; class audit events (handles, not emails); frozen assignment payloads; per-student answers and scores. Progress metrics continue to be read from existing G1–G7 tables. Cap 40 active students per class; a student may be in many classes.

### 9.2 Join consent

Join is **opt-in**. The student enters a code **or accepts a handle invite** **after** disclosure. Silent add is never allowed.

Disclosure (plain language, 13+) must say: the teacher can see class and named progress, including skill-gap labels; can set questions; **only the teacher can take you off the class**; if you want to leave, ask the teacher.

**Default:** off. Teacher mode is a soft flag the teacher enables. Students are not in any class until they join.

**Gap:** `/privacy` and `/privacy/simple` describe this sharing. Join copy is product UX, not a substitute for the notice. Qualified legal review is still required before public HTTPS.

### 9.3 Teacher-only remove

There is **no student Leave** control (UI or API). Only the teacher removes a member. **Account deletion** still erases memberships and assignment rows (GDPR) — that is erasure, not “leave class”.

**Residual:** a student who joined a class they later regret cannot self-remove. Mitigations already designed: teacher remove; GDPR delete of the whole account; join disclosure; existing report/block of the person; handle-invite still requires accept; view audit log.

**Confirm:** there is still **no** `POST /api/v1/me/classes/<id>/leave`. Memberships, invites, and assignment rows are erased with the account (`ON DELETE CASCADE`). Audit `actor_id` is SET NULL; matching `subject_handle` values are scrubbed. Export includes `classes_joined`, `class_work` (the student’s own answers, not stored keys), `class_invites_received`, and for teachers `invites_sent` / `class_audit`.

### 9.4 T0–T2 in; T3 out

| Tier | This track |
|------|------------|
| T0 class aggregates | Yes — roster only |
| T1 named progress (weak topics, recent quizzes, lesson summary, due-today) | Yes — roster only |
| T2 skill-gap **chips** (G6 rollups, not free text) | Yes — part of join disclosure; **no extra checkbox** |
| T3 free-text “what tripped me up” | **No** — never in teacher JSON or HTML |

Also exclude: passwords, classmates’ emails, private follows/feed, study-buddy content.

Authz on every class/progress/assignment endpoint: `teacher_can_view` / `teacher_owns_class`. Guests and other teachers must not see roster or progress.

**ICO Children’s Code std 12 (profiling):** educational performance profiling already exists on-account (weak topics, skill gaps, streaks). G8 discloses a slice of that profile to a teacher the child joined (class aggregates, named progress, skill-gap chips). It must not become public ranking or advertising. Phase 3 keeps this **roster-only**; no class leaderboard.

**Residual:** T2 chips without an extra toggle means join disclosure has to carry the skill-gap point. T3 remaining private is the hard block.

### 9.5 Frozen set-work

Teacher generates **X** questions (1–20) from the **live** catalogue, server **freezes** payloads, assigns the same set to selected students or all active members. Graded from stored `problems_json`, never from a client-supplied answer key. Student GET strips `correct_answer` / solution until after server grade (same trust model as challenges / shared questions).

**ICO Children’s Code std 13 (nudge):** set work can add class pressure. Completion is **class-roster only**; no public assignment leaderboard; no due-by-Friday late-work workflow in this track.

Do **not** extend `study_pairs` or fan out `question_suggestions`. Friend `quiz_challenges` stay peer-vs-peer.

### 9.6 Residuals and gaps (implementation PRs)

These belong in the **same PRs as schema**, not as a silent skip (`docs/SECURITY_AND_GDPR.md` §6.1):

| Gap | When |
|-----|------|
| New ROPA row (class membership + assignment attempts; recipient = teacher user; retention = life of account / erase on delete) | **Phase 1–5:** row 9 covers teacher flag, classes, memberships, frozen assignments, per-student answers, handle invites, and class audit events |
| Privacy notice + simple notice: who can see progress, join/remove, no T3 | **Phase 2–5:** notices describe live join sharing, handle invites, and set-work scores |
| Retention: class rows die with the account; listed in `docs/SECURITY_AND_GDPR.md` §4 | **Phases 1–6 done** for profiles, classes, memberships, assignments, recipients, previews, invites; audit actor SET NULL; pending invites pruned after 14 days |
| Erase/export cover new tables | **Phase 5:** leftover checks for invites + audit; export `class_work` / `assignments_created` / `class_invites_received` / `invites_sent` / `class_audit` without stored keys or other students’ emails |
| Join-code leak: rotate code; roster; teacher remove | **Phase 1–2 done** |
| Membership authz on every endpoint; no emails in roster payloads | **Phase 2–5:** roster/remove/progress/assignments/audit/CSV 404 unless owner; active member for student progress; handles only |
| No T3 leak in teacher JSON/HTML | **Phase 3–5 done** |
| Frozen-set answer stripping + server-side grade | **Phase 4 done** (`test_g8_phase4_smoke.py`) |
| Handle invites still opt-in; audit + CSV handles only | **Phase 5 done** (`test_g8_phase5_smoke.py`) |
| Sample flows: no Leave, no T3 leak, authz on roster/progress/audit/CSV | **Phase 6 done** (`test_g8_phase6_smoke.py`; full suite 71/71) |
| Qualified legal review of this DPIA + notices | Operator, **before public HTTPS** — not claimed done by Phase 0 |

**Feature-gate (2026-08-30):** Q1 yes · Q2 yes · Q3 no · Q4 yes. Recorded in `docs/G8_TEACHER_REVIEW_RUBRIC.md`.
