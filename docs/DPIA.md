# Data Protection Impact Assessment (DPIA)

**Controller:** set via `CONTROLLER_NAME` (placeholder until S0.1 is completed by the operator)  
**Contact:** `PRIVACY_CONTACT_EMAIL`  
**Last reviewed:** 2026-08-30  
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
| A child's academic weaknesses are visible to others | High / High | Weak topics, revision queues, and skill gaps are private to the account. Friend leaderboards are friends-only; there is **no global ranking**. | Keep weak topics out of the public profile and activity feed forever. **G8 (planned, not shipped):** a teacher who the student joined will see T0–T2 (including skill-gap chips) for roster members only. T3 free-text stays off. Join is opt-in; only the teacher can remove. Revisit this row when G8 Phase 3+ ships. |
| Stranger contact through follows, challenges, suggestions | Medium / High | No DMs. Block and report exist. System bot cannot be messaged as a person. Follows are one-way and do not expose email. | S2: report action on suggestions; documented escalation. Operator must read reports. |
| Public exposure of study activity | High / High | Default visibility is `followers_only`. Last topic, last activity, lesson progress, and quiz stats default **off**. Logged-out visitors see handle (and the private-profile page), not study data. | Users can still opt into a public profile; the settings page explains that public means anyone on the internet. |
| Competitive pressure / compulsive use (streaks, boards, buddy nudges) | Medium / Medium | Friends-only boards. Dismissible buddy. No streak-loss shaming copy. No push notifications until production HTTPS (E5.7), and quiet hours are specified there. **A1–A4 Guide (2026-08-27):** optional onboarding dialogue, first-visit section tours, and once-only first-correct / lesson-complete reward modals; Skip / Not now / Escape always; seen-flag in localStorage only; no extra processors. | Children's Code standard 12/13: each tour/origin/reward once; no streak-loss shaming; no night-time push or public ranking. **G8 (planned):** teacher-set frozen question work can add class pressure — keep it class-roster only, no public ranking of assignments. Revisit this table when G8 ships. |
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
| 5 Detrimental use | No profiling for ads; educational profiling stays on-account. |
| 6 Default settings | Followers-only; activity toggles off. |
| 7 Data minimisation | Email + handle only for identity. |
| 8 Data sharing | Subprocessors listed; lesson assist off by default. |
| 12 Nudge techniques | Friends-only competition; no public league table. Origin overlay and (later) tours are dismissible, once per browser, no analytics. |
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
| 2026-08-30 | G8 product decisions locked (solo tutors/teachers; many classes; T2 chips with join disclosure; teacher-only remove; frozen set-work in-track). Implementation **not started**. | Draft still pending qualified review. Phase 0 of `docs/G8_TEACHER_HANDOFF.md` records feature-gate answers. Revisit this DPIA when G8 schema ships. |
