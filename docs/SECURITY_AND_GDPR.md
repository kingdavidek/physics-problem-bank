# Problem Bank — Security and UK GDPR compliance plan

**Last updated:** 2026-08-26
**Status:** Phases S0–S3 implemented. S3 is the keep-it-true calendar (`docs/CADENCE.md`). Operator S0.1 (ICO fee, live contact address) is still required before the URL is public. GitHub secret scanning / push protection is a UI setting (S1.4).
**Audience:** The next AI agent (and the operator, for the non-code actions)
**Companions:** `docs/SOLID_DRAFT_SECURITY.md` (what is already hardened — do not regress), `docs/DEPLOY.md`, `docs/OPERATOR_LAUNCH.md`, `docs/CADENCE.md` (S3 calendar), `docs/INCIDENT_RESPONSE.md`, `docs/DATA_RIGHTS.md`, `docs/MODERATION.md`, `docs/ZAP.md`, `docs/MOBILE.md` (M5 production HTTPS), `docs/DPIA.md`, `docs/ROPA.md`, `docs/SUBPROCESSORS.md`

> **Not legal advice.** This is an engineering plan written against the UK GDPR, the Data Protection Act 2018, PECR, and the ICO's Age Appropriate Design Code (the "Children's Code"). Before taking real users, have the privacy notice and DPIA read by someone qualified. Everything in §2–§4 is factual about the codebase; the legal framing in §1 is a good-faith summary.

---

## 0. The one-paragraph summary

The platform is a UK-facing study site whose users are **mainly children (13+)**. It stores emails, password hashes, IP-derived rate-limit keys, and a rich behavioural record (every attempt, score, weak topic, streak, and social interaction). The security engineering is already better than average for a solo project — safe grading, hashed tokens, parameterised SQL, CSRF, rate limits, a real CSP. **Phases S0–S3 are implemented:** S0/S1 rights and launch blockers, **S2** (no `unsafe-inline` in `script-src`, self-hosted MathJax/Pyodide, ZAP runbook, GDPR action log, reports CLI), and **S3** (cadence runbook, `scripts/ops_cadence.py`, Monday `pip-audit` workflow). Remaining launch blockers are **operator actions** (S0.1, GitHub secret scanning). Keep the calendar in `docs/CADENCE.md`.

---

## 1. Legal position in plain terms

| Question | Answer for this platform |
|---|---|
| Who is the **controller**? | The operator (you) — you decide why and how the data is processed. Name and contact address must appear in the privacy notice. |
| Which law? | **UK GDPR + DPA 2018.** If you knowingly take EU users, EU GDPR applies too and you may need an EU representative (Art 27). Simplest realistic stance at launch: UK-facing, say so in the notice. |
| Who are the **processors**? | Hosting provider, email sender (Resend / SendGrid / SMTP), and the LLM provider if lesson assist is switched on. Each needs a written contract (their standard DPA is fine) and a line in the subprocessor list. |
| Children? | Yes — the age gate is 13+. In the UK a child can consent to information society services at 13, **but** the Children's Code applies to any service likely to be accessed by children, and it is a code of practice the ICO enforces. |
| Is a **DPIA** required? | **Yes.** The ICO expects one when you offer an online service directly to children and when you profile people (weak-topic analysis, streaks, leaderboards, recommendations all count). |
| Do we need an **ICO registration fee**? | Almost certainly yes once you are live and not purely personal/household use. Tier 1 is currently around £40–£60/year. Operator action, five minutes online. |
| Do we need a **cookie banner**? | **Not today.** Only strictly necessary storage is used (session cookie, remember-me, and functional `localStorage`). No analytics, no ads, no third-party trackers. **This changes the moment anyone adds analytics** — see the rule in §6.4. |
| Special category data? | None intended. Keep it that way: no health, ethnicity, or SEN fields, ever. |

### Lawful bases to state in the notice

| Processing | Basis |
|---|---|
| Account, practice history, progress features | **Contract** (Art 6(1)(b)) — you cannot deliver the service without it |
| Rate limiting, abuse prevention, moderation, security logging | **Legitimate interests** (Art 6(1)(f)) — write a two-paragraph legitimate interests assessment and keep it with the DPIA |
| Weekly digest email | **Consent** (Art 6(1)(a)) — already opt-in and default off, with an unsubscribe link. Keep it that way |
| Optional AI lesson assist | **Consent** at point of use, if enabled at all — see §5.3 |

---

## 2. What the platform actually holds today (evidence)

Verified against the code on 2026-08-15. Schema is created in `app.py` lines ~750–1249.

### 2.1 Personal data inventory (seed for the ROPA)

| Category | Where | Notes |
|---|---|---|
| Identity | `users` (`app.py:766`) — email, handle, password hash, created/last login | Werkzeug scrypt hash (`models/user.py:82`) |
| Preferences and privacy settings | `user_profile_settings` (`app.py`) — visibility toggles, avatar, digest opt-in, `guide_json` (onboarding/tour/reward seen flags) | Defaults discussed in §3.1 |
| Behavioural / educational record | `saved_problems`, `quiz_attempts`, `generator_mcq_attempts`, `lesson_progress`, `user_activity_events`, `user_activity_summary`, `user_streaks`, `user_study_days`, `user_milestones`, `qotd_attempts`, `user_revision_queue`, `user_revision_plans` | The richest and most sensitive set — it profiles a child's academic weaknesses |
| Free text written by users | `user_wrong_answer_reflections.reflection_text` (≤500), `shared_questions.note` (≤200), `question_suggestions`, `user_reports.note` (≤500) | Users can type anything, including personal details |
| Social graph | `follows`, `study_pairs`, `quiz_challenges`, `user_blocks`, `user_reports` | |
| Auth tokens | `api_tokens` — SHA-256 hash of a 256-bit random token, 90-day expiry (`models/api_tokens.py`) | |
| Email operations | `email_digest_log` | |
| **IP-derived identifiers** | `rate_limit_buckets.bucket_key` contains `:ip:{address}` (`app.py:2558`, `5402`); `lesson_assist_usage.client_key` contains `ip:{address}` (`app.py:7133`) | **Personal data.** No FK to `users`, **no pruning anywhere** |
| Session state | Flask signed cookie: CSRF token, current problem payload, queue, anon counter | HttpOnly, SameSite=Lax, Secure when HTTPS (`app.py:330–341`) |

Not collected: date of birth, real name, address, phone, photos (avatars are emoji + colour only), payment data, uploaded files (there is no upload endpoint at all).

### 2.2 What is already good — do not regress

Safe SymPy parser and session-bound grading; parameterised SQL everywhere; CSRF on cookie-session API writes; daily rate limits; hashed API tokens with expiry and revocation; CORS allowlist; a real CSP with `frame-src 'none'` and `object-src 'none'`; MathJax SRI; bot account cannot log in; Jinja autoescaping for all user-typed text; no file uploads; no analytics or ad tech; friends-only leaderboards with no global ranking; block and report already exist; no DMs. Details in `docs/SOLID_DRAFT_SECURITY.md`.

### 2.3 The gap register

Severity is about **risk to users and to you**, not difficulty. "Effort" is a rough half-day unit for an AI agent working with this codebase.

| # | Gap | Type | Severity | Effort |
|---|---|---|---|---|
| G1 | No privacy notice, no terms, no child-friendly explanation anywhere in the app | GDPR (Art 13) | **Critical** | 1 |
| G2 | No account deletion — nothing in the code deletes a `users` row | GDPR (Art 17) | **Critical** | 1 |
| G3 | No data export / access request mechanism | GDPR (Art 15/20) | **Critical** | 1 |
| G4 | No DPIA and no ROPA, for a children's service that profiles users | GDPR (Art 35/30) | **Critical** | 1 |
| G5 | Default `profile_visibility` is `'public'` and several activity toggles default on (`app.py:885`, `models/social.py`) | Children's Code std 6 | **High** | 0.5 |
| G6 | IP addresses stored in `rate_limit_buckets` / `lesson_assist_usage` with no retention limit or pruning | GDPR (Art 5(1)(e)) | **High** | 0.5 |
| G7 | No password reset and no email verification — you cannot recover an account or verify a rights request | Security + Art 12(6) | **High** | 1.5 |
| G8 | Lesson assist can send lesson text plus a child's typed question to OpenAI / Anthropic / **DeepSeek** with no notice, no DPA check, and no transfer assessment | GDPR Ch. V | **High** | 1 |
| G9 | Missing HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options` | Security | **High** | 0.5 |
| G10 | Backups are unencrypted full-database copies (`scripts/backup_sqlite.py`) | Security (Art 32) | **High** | 0.5 |
| G11 | No breach detection or response plan; 72-hour ICO clock would start with nothing prepared | GDPR (Art 33) | **High** | 0.5 |
| G12 | CI has no dependency, secret, or static analysis scanning; no Dependabot | Security | Medium | 0.5 |
| G13 | No account lockout beyond a 30/day per-IP login limit; no password change flow | Security | Medium | 1 |
| G14 | Google Fonts, MathJax, and Pyodide no longer load from third-party CDNs (S0.11 + S2.2). Remaining third-party: hosting, mail, optional lesson-assist | GDPR transfers | Medium | done |
| G15 | `PB_TESTING=1` disables CSRF **and** rate limits, with no guard against it reaching production | Security | Medium | 0.25 |
| G16 | No cross-user authorisation (IDOR) regression test, though the queries do filter by `user_id` | Security assurance | Medium | 0.5 |
| G17 | CSP `script-src` no longer allows `'unsafe-inline'` (S2.1). `'unsafe-eval'` / `'wasm-unsafe-eval'` remain for MathJax and Pyodide; `style-src` still has `'unsafe-inline'` | Security | Medium | done |
| G18 | Unsubscribe HMAC tokens never expire (`models/email_digest.py:52`) | Security | Low | 0.25 |
| G19 | Digest console/CLI paths print recipient emails to stdout (`models/email_digest.py:238`, `scripts/send_weekly_digest.py:77`) | Data minimisation | Low | 0.25 |
| G20 | API token hashes are unsalted SHA-256 | Security | **Low — see note** | — |

> **Note on G20:** a subagent flagged this as a priority. It is not. The token is 32 bytes from `secrets.token_urlsafe`, so there is no dictionary to attack and no rainbow table that helps; unsalted SHA-256 over 256 bits of entropy is fine. Switch to HMAC-SHA256 with a pepper only if you are touching that file anyway. Do not spend a slot on it.

---

## 3. The plan

Four phases. **S0 must be complete before the site is reachable by a real user** — which is the same gate as `docs/MOBILE.md` M5 (production HTTPS), so plan them together. S1 is the first fortnight after launch. S2 is hardening. S3 is the recurring calendar.

Each item is written as *Why → Do → Files → Acceptance*.

### Phase S0 — Launch blockers

#### S0.1 Establish the controller identity and contact route

**Why:** Every other document needs a named controller and a working contact address.
**Do:** Decide the trading name and a dedicated address (e.g. `privacy@yourdomain`). Register with the ICO and pay the data protection fee. Record the ICO registration number.
**Files:** none in the app — operator action. Step-by-step for David: **`docs/OPERATOR_LAUNCH.md`**. Record the outcome on `/privacy` via env vars (`CONTROLLER_NAME`, `PRIVACY_CONTACT_EMAIL`, `ICO_REGISTRATION_NUMBER`).
**Acceptance:** an address that a parent could email, and someone reads it.

#### S0.2 Publish a privacy notice, terms, and a child-friendly summary

**Why:** Articles 13 and 12 require you to tell people what you do with their data, in language a child can understand. The app currently has no such page — confirmed, there is no privacy or terms route or template anywhere.

**Do:** Add three static pages plus footer and registration links:

| Route | Template | Contents |
|---|---|---|
| `/privacy` | `templates/legal_privacy.html` | Full notice: controller, contact, what is collected (use §2.1), lawful bases (§1), retention (§4), rights and how to use them, subprocessors, transfers, ICO complaint route |
| `/privacy/simple` | `templates/legal_privacy_simple.html` | The Children's Code version: short sentences, "what we know about you", "who can see it", "how to delete it", "how to complain" |
| `/terms` | `templates/legal_terms.html` | Acceptable use, 13+ rule, no impersonation, moderation and blocking, service-as-is, contact |

Add a footer block in `templates/base.html` linking all three, and a line above the registration button: *"By creating an account you agree to the Terms and the Privacy notice."* — link both, do not pre-tick anything, and keep the existing 13+ checkbox as a separate explicit action.

**Files:** `app.py` (three trivial routes), the three templates, `templates/base.html`, `templates/register.html`.
**Acceptance:** a new smoke test asserts all three routes return 200 while logged out, and that `/register` HTML contains links to `/privacy` and `/terms`.

#### S0.3 High-privacy defaults for children

**Why:** Children's Code standard 6 says settings must default to high privacy. Today `profile_visibility` defaults to `'public'` (`app.py:885`) and the "show last topic", "show last activity", "show lesson progress", and "show quiz stats" toggles default on — so a new 13-year-old's recent study activity is visible to anonymous visitors by default.

**Do:**
1. Change the column default to `'followers_only'` and flip the four activity toggles to default off. Because the schema uses `CREATE TABLE IF NOT EXISTS`, changing the DDL only affects fresh databases — also add a one-time migration that updates existing rows that have never been touched, or (simpler, and honest while the user base is tiny) reset all existing rows to the new defaults and say so.
2. Keep the settings page exactly as it is — users can still opt into a public profile deliberately.
3. Add a short explainer line above the visibility radio: *"Public means anyone on the internet, including people who are not logged in."*

**Files:** `app.py` schema block, `models/social.py` (`get_profile_settings` defaults), `templates/profile_settings.html`.
**Acceptance:** smoke test — a freshly registered user's public profile, fetched logged out, exposes nothing beyond handle and avatar.

#### S0.4 Right to erasure: account deletion

**Why:** Article 17. There is currently no code path anywhere that deletes a user.

**Do:** Build both a self-serve route and an operator CLI, sharing one function.

```
models/account_deletion.py
    delete_user_account(conn, user_id) -> dict   # returns a per-table row count for the audit log
```

The function must:
1. Load the handle before deleting.
2. `DELETE FROM users WHERE id = ?` — the `ON DELETE CASCADE` foreign keys clear the ~25 child tables. **Verify `PRAGMA foreign_keys = ON` is actually set on the connection** — SQLite defaults it off, so confirm this before trusting cascade, and if it is off, either enable it or delete explicitly table by table.
3. Clean up the tables with **no** foreign key: `user_reports.reported_user_id` (no FK at all — anonymise to `NULL` and keep the report for safeguarding), `rate_limit_buckets` rows keyed `:user:{id}`, `quicktest_sessions` whose JSON carries `owner_user_id`, `lesson_assist_usage` rows for that session key.
4. Sweep other users' `user_notifications.payload_json` and `user_activity_events.payload_json` for the departing handle and either delete those rows or replace the handle with `"a deleted account"`.
5. Reserve the freed handle for 90 days in a small `deleted_handles(handle, deleted_at)` table, checked by `validate_handle`, so nobody can immediately impersonate a departed user.

Surfaces:
- `POST /me/delete` — requires the current password, a typed confirmation of the handle, and CSRF. Show an interstitial page listing exactly what will be destroyed and warning that it cannot be undone.
- `scripts/gdpr_erase_user.py --handle <h> [--confirm]` — for requests that arrive by email, and for a parent exercising a child's rights.

**Backups:** you cannot practically rewrite 14 days of rotating backups. Say so in the notice: *"Deleted data disappears from live systems immediately and from encrypted backups within 14 days."* That is the standard, accepted position.

**Files:** new `models/account_deletion.py`, `app.py` routes, `templates/account_delete.html`, `scripts/gdpr_erase_user.py`, `models/user.py` (handle validation).
**Acceptance:** new `scripts/test_gdpr_smoke.py` — create a user with data in every table, delete, then assert zero rows remain for that `user_id` in every table named in §2.1, that the handle is reserved, and that another user's feed no longer references them.

#### S0.5 Right of access and portability: data export

**Why:** Articles 15 and 20. A JSON download satisfies both and takes an afternoon.

**Do:** `models/data_export.py` → `build_user_export(conn, user_id)` returning a dict: `{generated_at, schema_version, account, settings, practice: {...}, social: {...}, notes}`. One key per table, each a list of rows filtered by `user_id`. Exclude other people's personal data beyond what the user can already see in the UI (handles they follow, handles who follow them).

Surfaces: `GET /me/export` (web button on the settings page, downloads `problem-bank-export-<handle>-<date>.json`), `GET /api/v1/me/export`, and `scripts/gdpr_export_user.py`. Rate-limit to 2/day using the existing bucket helper.

**Acceptance:** smoke test asserts the export contains a seeded reflection, quiz attempt, and saved problem, contains no `password_hash`, and no other user's email.

#### S0.6 Retention: prune what you do not need

**Why:** Article 5(1)(e). IP-derived keys currently live forever.

**Do:** two changes.

1. **Pseudonymise the IP at the point of use.** The rate-limit key is only ever compared, never read back — so hash it. In `_client_ip()` callers, replace the raw address with `hmac_sha256(SECRET_KEY, ip)[:16]`. Same for the lesson-assist `client_key`. Functionality is identical; you stop storing IP addresses at all. Do this **before** the pruning job, because it makes the remaining risk small.
2. **`scripts/prune_expired_data.py`** implementing the retention schedule in §4, safe to run daily from the same scheduler as the backup script, logging counts per table.

**Acceptance:** smoke test seeds old rows, runs the prune function, asserts they are gone and current rows survive.

#### S0.7 Password reset and email verification

**Why:** Without reset, a forgotten password means a dead account and a support burden; without a verified email, you cannot safely honour a rights request or notify a breach. This is the largest S0 item — budget for it.

**Do:**
- `password_reset_tokens(user_id, token_hash, created_at, expires_at, used_at)`. Token = `secrets.token_urlsafe(32)`, stored hashed, **60-minute expiry, single use**, invalidated when the password changes.
- `/forgot-password` and `/reset-password/<token>`, both rate-limited (5/day/IP), with a response that never reveals whether an email exists.
- Reuse `models/email_digest.py`'s sending layer rather than writing a second mailer.
- `email_verified_at` on `users`, a verification email on registration, and a gentle banner until verified. Do **not** hard-block practice on unverified email — that punishes a child who mistyped an address; do block the digest and rights requests.
- Add a password change form (current password required) on the settings page while you are in there.

**Acceptance:** smoke test covers happy path, expired token, reused token, and token invalidation after a password change.

#### S0.8 Security headers and the production boot guard

**Why:** Cheap wins, and one genuine footgun.

**Do:** in the existing `@app.after_request` (`app.py:619`), add:

```
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=(), interest-cohort=()
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains    # only when the request is HTTPS
```

Add HSTS **only** behind the same HTTPS condition that already drives `SESSION_COOKIE_SECURE`, and start with a short `max-age` on the first deploy in case the certificate misbehaves.

Then the footgun: `PB_TESTING=1` disables CSRF and rate limiting. Add a startup guard that **refuses to boot** when `PB_TESTING` is set alongside a production signal (`SITE_URL` starting `https://`, or `FLASK_ENV=production`). Fail loudly at import time, the same way the `SECRET_KEY` check already does.

**Acceptance:** extend `scripts/test_phase_m5_smoke.py` to assert each header is present; add a test that the guard raises when both flags are set.

#### S0.9 DPIA and ROPA

**Why:** Article 35 for a children's service that profiles; Article 30 records. These are documents, not code, but the next agent can draft them from the inventory in §2.

**Do:** create `docs/DPIA.md` and `docs/ROPA.md`.

The DPIA must actually engage with this product's real risks, not boilerplate:

| Risk | Mitigation already in place | Gap to close |
|---|---|---|
| A child's academic weaknesses are visible to others | Weak topics are private to the user | Keep them out of the feed and public profile forever |
| Stranger contact through follows, challenges, suggestions | No DMs; block and report exist; bot cannot be messaged | Add a report action on suggestions; document escalation |
| Public exposure of study activity | Visibility settings exist | S0.3 defaults |
| Competitive pressure / compulsive use from streaks, leaderboards, buddy nudges | Friends-only boards, no global ranking, dismissible buddy | Document the assessment against Children's Code std 13 (nudge techniques); no streak-loss shaming copy; no push notifications to children at night (see E5.7 quiet hours) |
| Free-text fields leaking personal details | Length caps, autoescaped | Say plainly in the child-friendly notice: "don't put your real name, school, or address in notes" |
| Child's content sent to an LLM | Env-gated, mock by default | S0.10 |

The ROPA is a single table: purpose, categories of data, categories of subjects, recipients, transfers, retention, security measures. Copy from §2.1 and §4.

#### S0.10 Decide the lesson-assist position

**Why:** `generators/shared/lesson_assist.py` sends selected lesson text, up to 1200 characters of surrounding context, and **the child's own typed question** to OpenAI, Anthropic, or DeepSeek depending on configuration. DeepSeek in particular means a transfer to China, which has no UK adequacy decision and would need an IDTA plus a transfer risk assessment. Today this is env-gated and defaults to mock, so **nothing leaks unless a key is configured** — the decision is what happens at launch.

**Do:** pick one and write it down. **Decision (2026-08-26): Option A.**
- **Option A (implemented):** production stays off unless `LESSON_ASSIST_ENABLED=1`. Zero transfer, zero paperwork, feature stays available locally. `is_enabled()` treats HTTPS `SITE_URL` / `FLASK_ENV=production` as off when the flag is not an explicit on-value.
- **Option B:** enable with a single provider that offers a DPA, a no-training-on-inputs commitment, and UK/EU or adequacy-covered processing. Then: add the provider to the subprocessor list, add a transfer mechanism, show a one-time notice at the point of use ("your question and the highlighted text are sent to *X* to generate an explanation — don't include personal details"), and strip identifiers from the payload (it already sends no handle or email — keep it that way).

**Never** send the user's handle, email, or user ID to an LLM provider. Add that as an invariant.

#### S0.11 Self-host the fonts

**Why:** Google Fonts loaded from `fonts.googleapis.com` (`templates/base.html:27`) discloses every visitor's IP to Google, including children who never logged in. It has been litigated in the EU and it is the single easiest third-party transfer to eliminate.

**Do:** download the two font families into `static/fonts/`, serve them with `@font-face`, drop the two `<link>` tags, and remove `fonts.googleapis.com` / `fonts.gstatic.com` from the CSP. Bump `CACHE_VERSION`.
**Acceptance:** page loads with no request to a Google domain; the CSP no longer names one.

---

### Phase S1 — First fortnight after launch

**Implemented in code (2026-08-26).** Operator still enables GitHub secret scanning and push protection in the GitHub UI (S1.4).

| # | Item | Detail |
|---|---|---|
| S1.1 | **Encrypt backups** | `scripts/backup_sqlite.py` encrypts with Fernet (`cryptography`) from `PB_BACKUP_PASSPHRASE` (PBKDF2-HMAC-SHA256, 480k iterations, `PBENC1` header). Production refuses a missing passphrase. Restore: `scripts/restore_sqlite.py`. Proven in `scripts/test_backup_smoke.py`. Steps in `docs/DEPLOY.md`. |
| S1.2 | **Breach response runbook** | `docs/INCIDENT_RESPONSE.md`: what counts as a breach, the 72-hour ICO clock and when it starts, who decides, how to notify affected users (verified emails from S0.7), how to preserve evidence, and a template notification. Include the "contain → assess → notify → learn" sequence and a decision table for *risk* vs *high risk*. |
| S1.3 | **Rights-request workflow** | `docs/DATA_RIGHTS.md`: one calendar month to respond; how to verify identity without collecting more data than necessary (respond to the registered email; never ask for ID documents for a simple export); how to handle a parent requesting on behalf of a child; the CLI commands from S0.4/S0.5; a log of requests and outcomes. |
| S1.4 | **CI security gates** | Added to `.github/workflows/smoke.yml`: `pip-audit`, `gitleaks` (binary), `ruff`. `.github/dependabot.yml` for `pip` and `github-actions`, weekly. **Non-blocking** (`continue-on-error`) until a clean week. **Operator:** enable GitHub secret scanning and push protection in the repo settings. |
| S1.5 | **Authorisation regression tests** | `scripts/test_authz_smoke.py`: user B attempts to read, update, and delete user A's saved problem, quiz attempt, reflection, revision plan, notification, and API token, by ID — every one must 403/404. Also assert a private profile stays private to a logged-out visitor and to a non-follower. This closes the assurance gap: the queries already filter by `user_id`, but nothing proves it stays that way. |
| S1.6 | **Login abuse controls** | Per-account failed-attempt throttling: **15-minute lock after 10 failures** (`models/login_lockout.py`) on top of the existing per-IP daily cap, so one account cannot be sprayed from many IPs. Keep the generic error messages. |
| S1.7 | **Log hygiene** | Host access logs: **30 days** (`docs/DEPLOY.md`). Recipient emails are omitted from digest stdout for non-console providers unless `MAIL_LOG_RECIPIENTS=1`. Never log passwords, tokens, session cookies, or answer content. |
| S1.8 | **Unsubscribe token expiry** | HMAC payload is `{uid}.{unix_ts}.{sig}`; tokens older than 90 days are rejected (`models/email_digest.py`). Old two-part tokens are invalid. |

---

### Phase S2 — Hardening (when the basics are stable)

**Implemented in code (2026-08-26).** `unsafe-eval` / `wasm-unsafe-eval` stay for MathJax and Pyodide. S2.5 (operator 2FA) is skipped — there is no admin role.

| # | Item | Detail |
|---|---|---|
| S2.1 | **Remove `unsafe-inline` from script CSP** | Inline `<script>` and `onclick`/`oninput` moved to `static/js/`. Per-request nonce is on `script-src` if any inline script returns. `unsafe-eval` stays for MathJax/Pyodide. `style-src` still allows `'unsafe-inline'` for SVG/presentation. |
| S2.2 | **Self-host MathJax and Pyodide** | `static/vendor/mathjax/tex-svg.js` (3.2.2) and `static/vendor/pyodide/` (0.25.0 core). Re-download: `python scripts/vendor_cdn_assets.py`. jsDelivr removed from CSP. |
| S2.3 | **Automated baseline scan** | `docs/ZAP.md` plus `.github/workflows/zap.yml` (`workflow_dispatch`, non-blocking). Triage table for accepted findings. |
| S2.4 | **Personal-data action log** | CLI export/erase append JSON lines to `data/gdpr_actions.log` (`models/gdpr_action_log.py`). |
| S2.5 | **Two-factor for the operator account** | **Skipped.** No admin surface exists; do not add one to justify 2FA. |
| S2.6 | **Moderation depth** | `scripts/moderate_reports.py` lists/resolves reports and can hide a shared question or dismiss a suggestion. Timescales: `docs/MODERATION.md`. |

---

### Phase S3 — Keep it true

**Implemented 2026-08-26.** This is a calendar, not a product feature. How to run it: **`docs/CADENCE.md`**. CLI: `python scripts/ops_cadence.py weekly|monthly|restore-drill|feature-gate`. Monday `pip-audit`: `.github/workflows/cadence.yml`.

| Cadence | Task | How |
|---|---|---|
| Every release | Full smoke suite; `PB_TESTING` off in production; bump `CACHE_VERSION` when assets change | CI `smoke.yml`; `scripts/run_smoke_tests.py` |
| Weekly | Review Dependabot and `pip-audit`; check the backup ran and prune logged counts | `ops_cadence.py weekly`; Dependabot; `cadence.yml` |
| Monthly | Open reports queue; skim auth failure / lockout counts | `ops_cadence.py monthly` then `moderate_reports.py list` |
| Quarterly | Restore a backup for real; re-read the privacy notice; review subprocessors | `ops_cadence.py restore-drill` (scratch DB only) |
| Annually, or on any material change | Revisit the DPIA; renew the ICO fee | `docs/DPIA.md` review log; `docs/OPERATOR_LAUNCH.md` |
| On every new feature | Ask the four questions in §6.1 before writing code | `ops_cadence.py feature-gate` |

---

## 4. Retention schedule

Put this table in the privacy notice and implement it in `scripts/prune_expired_data.py`.

| Data | Retention | Mechanism |
|---|---|---|
| Account and all linked practice/social data | Life of the account, deleted immediately on request | S0.4 cascade delete |
| Inactive accounts | Email a warning at 24 months of no logins; delete at 30 months | Prune job + digest mailer |
| `rate_limit_buckets` | 7 days | Prune job (rows are already day-keyed) |
| `lesson_assist_usage` | 30 days | Prune job |
| `quicktest_sessions` | 7 days | Prune job (per-session delete already exists) |
| `email_digest_log` | 12 months | Prune job |
| `user_reports` | 12 months after resolution — safeguarding justification, note it in the notice | Prune job |
| Expired `api_tokens` rows | Delete 30 days after `expires_at` | Prune job |
| `password_reset_tokens` | Delete 24 hours after expiry | Prune job |
| Database backups | 14 days rolling (already implemented) | `scripts/backup_sqlite.py` |
| Host access logs | 30 days | Hosting configuration |
| Deleted handle reservations | 90 days | S0.4 |

---

## 5. Third parties

Maintain this as `docs/SUBPROCESSORS.md` and mirror it in the privacy notice.

| Party | Purpose | Data | Location | Contract needed |
|---|---|---|---|---|
| Hosting provider | Runs the app and database | Everything | Confirm at deploy | Their DPA |
| Resend / SendGrid / SMTP host | Weekly digest, password reset, verification | Email address, handle, digest stats | Provider-dependent | Their DPA |
| jsDelivr (MathJax, Pyodide) | Static assets | Visitor IP, user agent | Global CDN | None — **removed in S2.2** (self-hosted) |
| Google Fonts | Fonts | Visitor IP | Global | None — remove via S0.11 |
| Cloudinary / PythonAnywhere assets in some lesson templates | Images and scripts embedded in lessons | Visitor IP | Global | Audit and self-host where practical |
| OpenAI / Anthropic / DeepSeek | Lesson assist, **only if enabled** | Lesson text, surrounding context, the child's typed question | US / China | DPA + transfer mechanism, or keep disabled (S0.10) |

---

## 6. Rules for the next agent

### 6.1 Four questions before any new feature

1. **Does it collect a new category of personal data?** If yes, update the ROPA, the privacy notice, and the retention schedule in the same pull request.
2. **Does it make anything about a child more visible to anyone else?** If yes, it defaults to off.
3. **Does it send data to a new third party?** If yes, it needs a subprocessor entry and a transfer basis before it ships — not after.
4. **Does it profile, rank, or nudge?** If yes, revisit the DPIA section on Children's Code standard 13.

### 6.2 Invariants to add to the handoff list

- Never send a handle, email, or user ID to an external AI provider.
- Never introduce a global public leaderboard or any public ranking of minors.
- Never add analytics, advertising, or third-party tracking. If a product decision ever overrides this, a consent banner and a rewritten privacy notice come first, in the same release.
- Never store a raw IP address where a keyed hash would do.
- Never let `PB_TESTING=1` reach production — it disables CSRF and rate limiting.

### 6.3 Files that will exist when this plan is done

```
docs/SECURITY_AND_GDPR.md      this plan
docs/DPIA.md                   data protection impact assessment
docs/ROPA.md                   record of processing activities
docs/SUBPROCESSORS.md          third-party list
docs/INCIDENT_RESPONSE.md      breach runbook
docs/DATA_RIGHTS.md            how to answer a rights request
docs/MODERATION.md             report triage CLI and takedown timescales
docs/ZAP.md                    OWASP ZAP baseline + accepted findings
docs/OPERATOR_LAUNCH.md        operator ICO / inbox / cron (S0.1)
docs/CADENCE.md                S3 weekly / monthly / quarterly calendar
models/cadence_log.py          cadence CLI log
scripts/ops_cadence.py         weekly backup check, monthly reports, restore drill
scripts/test_s3_cadence_smoke.py
models/account_deletion.py     erasure
models/data_export.py          access + portability
models/login_lockout.py        per-account lock
scripts/gdpr_erase_user.py     operator CLI
scripts/gdpr_export_user.py    operator CLI
scripts/prune_expired_data.py  retention
scripts/backup_sqlite.py       encrypted backup
scripts/restore_sqlite.py      backup restore
scripts/test_gdpr_smoke.py     erasure + export + retention tests
scripts/test_authz_smoke.py    cross-user access tests
scripts/test_backup_smoke.py   encrypt + restore
scripts/test_csp_smoke.py      no script unsafe-inline; no jsDelivr
scripts/test_s2_ops_smoke.py   GDPR action log + reports CLI
scripts/moderate_reports.py    report triage CLI
models/gdpr_action_log.py      CLI export/erase log
static/vendor/                 self-hosted MathJax + Pyodide core
templates/legal_privacy.html   /privacy
templates/legal_privacy_simple.html   /privacy/simple
templates/legal_terms.html     /terms
```

### 6.4 The cookie banner rule

The site needs no consent banner **today** because it stores only what is strictly necessary to deliver a service the user asked for. Add one line of analytics, one embedded YouTube video, or one advertising pixel and that stops being true immediately — at which point PECR requires prior consent, and consent from children is its own problem. The cheapest compliance decision available to this project is simply never to add tracking.

---

## 7. Definition of done

**Phase S0 (before any real user can reach the site):**

- [ ] Controller identified, ICO fee paid, contact address monitored (**operator — S0.1**; how-to: `docs/OPERATOR_LAUNCH.md`; env `CONTROLLER_NAME`, `PRIVACY_CONTACT_EMAIL`, `ICO_REGISTRATION_NUMBER`)
- [x] `/privacy`, `/privacy/simple`, `/terms` live and linked from the footer and registration
- [x] New accounts default to high privacy; anonymous visitors see nothing but handle and avatar
- [x] Account deletion works self-serve and by CLI, verified by test across every table
- [x] Data export works self-serve and by CLI, contains no other user's data and no password hash
- [x] IPs pseudonymised; prune job written (`scripts/prune_expired_data.py` — schedule it on the host)
- [x] Password reset and email verification live; password change form added
- [x] Security headers set; production boot guard refuses `PB_TESTING`
- [x] `docs/DPIA.md` and `docs/ROPA.md` written (operator should still have them read by someone qualified)
- [x] Lesson-assist position decided and documented (Option A: disabled in production unless `LESSON_ASSIST_ENABLED=1`)
- [x] Fonts self-hosted; CSP no longer names Google
- [x] Full smoke suite includes `scripts/test_gdpr_smoke.py`

**Phase S1:**

- [x] Backups encrypted (`PB_BACKUP_PASSPHRASE` / Fernet) and a restore proven (`scripts/test_backup_smoke.py`); restore steps in `docs/DEPLOY.md`
- [x] `docs/INCIDENT_RESPONSE.md` (72-hour ICO clock, contain → assess → notify → learn)
- [x] `docs/DATA_RIGHTS.md` (one month, verify via registered email, parent-on-behalf, CLI)
- [x] CI: `pip-audit`, `ruff`, `gitleaks` (non-blocking); Dependabot weekly. **Operator:** GitHub secret scanning + push protection
- [x] `scripts/test_authz_smoke.py` green (cross-user 404/403)
- [x] Per-account lockout: 15 min after 10 failures; generic login error
- [x] Log hygiene: recipient emails gated; host logs 30 days documented
- [x] Unsubscribe tokens timestamped; reject after 90 days

**Phase S2:**

- [x] `script-src` has no `'unsafe-inline'` (nonce + external JS); `'unsafe-eval'` documented for MathJax/Pyodide
- [x] MathJax and Pyodide self-hosted under `static/vendor/`
- [x] ZAP baseline documented and optional CI (`docs/ZAP.md`)
- [x] CLI export/erase append to `data/gdpr_actions.log`
- [x] No admin role — 2FA skipped on purpose
- [x] `scripts/moderate_reports.py` + `docs/MODERATION.md`

**Phase S3:**

- [x] Cadence runbook (`docs/CADENCE.md`)
- [x] `scripts/ops_cadence.py` weekly / monthly / restore-drill / feature-gate
- [x] Restore drill refuses to overwrite the live DB (`scripts/test_s3_cadence_smoke.py`)
- [x] Weekly scheduled `pip-audit` (`.github/workflows/cadence.yml`); Dependabot already weekly (S1.4)
- [x] DPIA review log + triggers (`docs/DPIA.md`)
- [x] Four questions before new features in the handoff invariants
