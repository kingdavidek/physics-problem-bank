# Problem Bank — Security and UK GDPR compliance plan

**Last updated:** 2026-08-15
**Status:** Planned — not implemented
**Audience:** The next AI agent (and the operator, for the non-code actions)
**Companions:** `docs/SOLID_DRAFT_SECURITY.md` (what is already hardened — do not regress), `docs/DEPLOY.md`, `docs/MOBILE.md` (M5 production HTTPS)

> **Not legal advice.** This is an engineering plan written against the UK GDPR, the Data Protection Act 2018, PECR, and the ICO's Age Appropriate Design Code (the "Children's Code"). Before taking real users, have the privacy notice and DPIA read by someone qualified. Everything in §2–§4 is factual about the codebase; the legal framing in §1 is a good-faith summary.

---

## 0. The one-paragraph summary

The platform is a UK-facing study site whose users are **mainly children (13+)**. It stores emails, password hashes, IP-derived rate-limit keys, and a rich behavioural record (every attempt, score, weak topic, streak, and social interaction). The security engineering is already better than average for a solo project — safe grading, hashed tokens, parameterised SQL, CSRF, rate limits, a real CSP. The **compliance** side is close to empty: no privacy notice, no way to delete an account, no way to export data, no retention limits, no DPIA, and default profile settings that are more open than the Children's Code expects. Almost all of that is fixable in code you already know how to write, and the site is **not yet public** — which is the cheapest possible moment to fix it.

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
| Preferences and privacy settings | `user_profile_settings` (`app.py:883`) — visibility toggles, avatar, digest opt-in | Defaults discussed in §3.1 |
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
| G14 | Google Fonts, MathJax, and Pyodide load from third-party CDNs, disclosing every visitor's IP | GDPR transfers | Medium | 1 |
| G15 | `PB_TESTING=1` disables CSRF **and** rate limits, with no guard against it reaching production | Security | Medium | 0.25 |
| G16 | No cross-user authorisation (IDOR) regression test, though the queries do filter by `user_id` | Security assurance | Medium | 0.5 |
| G17 | CSP still allows `'unsafe-inline'` and `'unsafe-eval'` | Security | Medium | 3 |
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
**Files:** none — operator action; record the outcome in the privacy notice and `docs/DEPLOY.md`.
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

**Do:** pick one and write it down.
- **Option A (recommended for launch):** keep `LESSON_ASSIST_ENABLED=0` in production. Zero transfer, zero paperwork, feature stays available locally.
- **Option B:** enable with a single provider that offers a DPA, a no-training-on-inputs commitment, and UK/EU or adequacy-covered processing. Then: add the provider to the subprocessor list, add a transfer mechanism, show a one-time notice at the point of use ("your question and the highlighted text are sent to *X* to generate an explanation — don't include personal details"), and strip identifiers from the payload (it already sends no handle or email — keep it that way).

**Never** send the user's handle, email, or user ID to an LLM provider. Add that as an invariant.

#### S0.11 Self-host the fonts

**Why:** Google Fonts loaded from `fonts.googleapis.com` (`templates/base.html:27`) discloses every visitor's IP to Google, including children who never logged in. It has been litigated in the EU and it is the single easiest third-party transfer to eliminate.

**Do:** download the two font families into `static/fonts/`, serve them with `@font-face`, drop the two `<link>` tags, and remove `fonts.googleapis.com` / `fonts.gstatic.com` from the CSP. Bump `CACHE_VERSION`.
**Acceptance:** page loads with no request to a Google domain; the CSP no longer names one.

---

### Phase S1 — First fortnight after launch

| # | Item | Detail |
|---|---|---|
| S1.1 | **Encrypt backups** | `scripts/backup_sqlite.py` currently does a plain `shutil.copy2`. Encrypt with a passphrase from `PB_BACKUP_PASSPHRASE` (Fernet via `cryptography`, or shell out to `gpg` if it is available on the host). **Then actually restore one** into a scratch directory and open it — an untested backup is not a backup. Document the restore steps in `docs/DEPLOY.md`. |
| S1.2 | **Breach response runbook** | `docs/INCIDENT_RESPONSE.md`: what counts as a breach, the 72-hour ICO clock and when it starts, who decides, how to notify affected users (you will need the verified emails from S0.7), how to preserve evidence, and a template notification. Include the "contain → assess → notify → learn" sequence and a decision table for *risk* vs *high risk*. |
| S1.3 | **Rights-request workflow** | `docs/DATA_RIGHTS.md`: one calendar month to respond; how to verify identity without collecting more data than necessary (respond to the registered email; never ask for ID documents for a simple export); how to handle a parent requesting on behalf of a child; the CLI commands from S0.4/S0.5; a log of requests and outcomes. |
| S1.4 | **CI security gates** | Add to `.github/workflows/smoke.yml` (or a second workflow): `pip-audit` for known CVEs, `gitleaks` for secrets, `ruff` for lint. Enable GitHub secret scanning and push protection on the repo. Add `.github/dependabot.yml` for `pip` and `github-actions`, weekly. Start them non-blocking for a week, then make them required. |
| S1.5 | **Authorisation regression tests** | `scripts/test_authz_smoke.py`: user B attempts to read, update, and delete user A's saved problem, quiz attempt, reflection, revision plan, notification, and API token, by ID — every one must 403/404. Also assert a private profile stays private to a logged-out visitor and to a non-follower. This closes the assurance gap: the queries already filter by `user_id`, but nothing proves it stays that way. |
| S1.6 | **Login abuse controls** | Per-account failed-attempt throttling (exponential backoff or a 15-minute lock after 10 failures) on top of the existing per-IP daily cap, so one account cannot be sprayed from many IPs. Keep the generic error messages. |
| S1.7 | **Log hygiene** | Decide what the production host logs and for how long (30 days is a defensible default). Remove recipient emails from digest stdout in non-console providers (`models/email_digest.py:238`, `scripts/send_weekly_digest.py:77`) or gate them behind a debug flag. Never log passwords, tokens, session cookies, or answer content. |
| S1.8 | **Unsubscribe token expiry** | Add a timestamp to the HMAC payload and reject tokens older than 90 days (`models/email_digest.py:52`). Low risk, five minutes. |

---

### Phase S2 — Hardening (when the basics are stable)

| # | Item | Detail |
|---|---|---|
| S2.1 | **Remove `unsafe-inline` from the CSP** | The real work is moving inline `<script>` blocks and `onclick=` handlers out of templates into `static/js/`. Do it a template at a time, then switch to per-request nonces. `unsafe-eval` must stay for MathJax and Pyodide — document that as an accepted, scoped exception rather than pretending it will go away. Budget several days; this is the biggest remaining security item. |
| S2.2 | **Self-host MathJax and Pyodide** | Removes two more third-party IP disclosures and a supply-chain dependency. Pyodide is large — check the hosting quota first. Keep SRI if you stay on a CDN. |
| S2.3 | **Automated baseline scan** | OWASP ZAP baseline against a throwaway instance in CI, or run it manually each release. Triage and record accepted findings. |
| S2.4 | **Personal-data action log** | When the CLI erase/export scripts run, append to an append-only log (who, when, which handle, row counts). This is your evidence that you honoured a request. |
| S2.5 | **Two-factor for the operator account** | Only if an admin surface ever exists. Today there is no admin role, which is itself a good control — think hard before adding one. |
| S2.6 | **Moderation depth** | Report action on suggestions and shared notes; a triage view (even a CLI listing of open reports); documented takedown timescales. Safeguarding matters more than most security controls for this audience. |

---

### Phase S3 — Keep it true

| Cadence | Task |
|---|---|
| Every release | Run the full smoke suite; confirm `PB_TESTING` is not set in production; bump `CACHE_VERSION` when assets change |
| Weekly | Review Dependabot and `pip-audit` output; check the backup ran and prune job logged sensible counts |
| Monthly | Read the open reports queue; skim auth failure rates for spraying |
| Quarterly | Restore a backup for real; re-read the privacy notice against what the code now does; review the subprocessor list |
| Annually, or on any material change | Revisit the DPIA (new feature that profiles, any new data category, any new processor); renew the ICO fee |
| On every new feature | Ask the four questions in §6.1 before writing code |

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
| jsDelivr (MathJax, Pyodide) | Static assets | Visitor IP, user agent | Global CDN | None — remove via S2.2 |
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
models/account_deletion.py     erasure
models/data_export.py          access + portability
scripts/gdpr_erase_user.py     operator CLI
scripts/gdpr_export_user.py    operator CLI
scripts/prune_expired_data.py  retention
scripts/test_gdpr_smoke.py     erasure + export + retention tests
scripts/test_authz_smoke.py    cross-user access tests
templates/legal_privacy.html   /privacy
templates/legal_privacy_simple.html   /privacy/simple
templates/legal_terms.html     /terms
```

### 6.4 The cookie banner rule

The site needs no consent banner **today** because it stores only what is strictly necessary to deliver a service the user asked for. Add one line of analytics, one embedded YouTube video, or one advertising pixel and that stops being true immediately — at which point PECR requires prior consent, and consent from children is its own problem. The cheapest compliance decision available to this project is simply never to add tracking.

---

## 7. Definition of done

**Phase S0 (before any real user can reach the site):**

- [ ] Controller identified, ICO fee paid, contact address monitored
- [ ] `/privacy`, `/privacy/simple`, `/terms` live and linked from the footer and registration
- [ ] New accounts default to high privacy; anonymous visitors see nothing but handle and avatar
- [ ] Account deletion works self-serve and by CLI, verified by test across every table
- [ ] Data export works self-serve and by CLI, contains no other user's data and no password hash
- [ ] IPs pseudonymised; prune job written and scheduled
- [ ] Password reset and email verification live; password change form added
- [ ] Security headers set; production boot guard refuses `PB_TESTING`
- [ ] `docs/DPIA.md` and `docs/ROPA.md` written and reviewed
- [ ] Lesson-assist position decided and documented (default: disabled in production)
- [ ] Fonts self-hosted; CSP no longer names Google
- [ ] Full smoke suite green, including the new GDPR tests

**Phase S1:** backups encrypted and a restore proven; incident and rights runbooks written; CI scanning enabled; authorisation tests green; login abuse controls live; log hygiene done.

**Phase S2:** `unsafe-inline` gone; CDN assets self-hosted; baseline scan clean or triaged; personal-data action log in place.
