# Incident response runbook

**Audience:** you (the operator)  
**When:** a suspected personal-data breach, account takeover, leaked backup, or accidental data exposure  
**Law:** UK GDPR Art 33/34 — 72-hour clock to tell the ICO if the breach is notifiable  
**Not legal advice.** If in doubt, treat it as a breach and start the clock.

Companions: `docs/OPERATOR_LAUNCH.md`, `docs/DATA_RIGHTS.md`, `docs/DPIA.md`.

---

## 1. What counts as a breach

A **personal-data breach** is any accidental or unlawful destruction, loss, alteration, unauthorised disclosure of, or access to, personal data. Examples for this site:

- The SQLite file, an unencrypted backup, or `.env` is copied off the host
- A token, password-reset link, or session cookie is posted in a log or ticket
- An IDOR lets user B read user A’s quizzes, reflections, or email
- `PB_TESTING=1` reaches production (CSRF and rate limits off)
- A subprocessors incident (hosting or email provider)

A failed login or a blocked spam account is **not** a breach by itself.

---

## 2. The 72-hour clock

The clock starts when **you** (the controller) become aware — the moment you have a reasonable degree of certainty that a breach happened, not when the investigation is finished.

If the breach is likely to risk people’s rights (almost always true here: children’s emails and study records), notify the ICO **without undue delay and within 72 hours**. Use [ico.org.uk](https://ico.org.uk/) “report a breach”.

If you miss 72 hours, still report and say why it was late.

---

## 3. Who decides

There is no separate DPO. **You decide.** Sequence:

1. **Contain** — stop the leak
2. **Assess** — what data, whose, how many, likely harm
3. **Notify** — ICO and, if high risk, the users
4. **Learn** — rotate secrets, fix the bug, write what happened

Do not wait for a lawyer to contain.

---

## 4. Contain → assess → notify → learn

| Step | Do this |
|---|---|
| **Contain** | Rotate `SECRET_KEY` (logs everyone out). Rotate API/mail keys. Take the site down if you cannot stop the leak. Copy the live DB and logs to a **read-only** evidence folder; do not “tidy” them. Revoke API tokens (`POST /api/v1/auth/revoke-all` per user, or stop the app). |
| **Assess** | What tables leaked? Emails? Password hashes (scrypt — still rotate if the file left the host)? Study records? How many users, were they children, is a parent likely to be harmed? |
| **Notify ICO** | If likely risk: report within 72 hours. Keep the reference number. |
| **Notify users** | If **high risk** (see table below): email **verified** addresses only (`email_verified_at` is set). Unverified addresses are not a reliable contact. |
| **Learn** | Patch, rotate, update `docs/DPIA.md` if the processing changed, calendar a re-read in a week. |

### Risk vs high risk (user notification)

| Situation | ICO (Art 33) | Users (Art 34) |
|---|---|---|
| Encrypted backup stolen; passphrase not leaked | Usually notify ICO | Often **no** — encryption is a mitigating measure |
| Plaintext DB or `.env` stolen | Notify | **Yes — high risk** |
| Single user’s export emailed to the wrong parent after a handle mix-up | Notify | **Yes** — that user / parent |
| Password hashes only, hashes are scrypt, no other data | Notify | Usually yes — tell people to change password if they reused it |
| Public profile data that the user already chose to publish | Maybe not a breach | No |

When notifying users, do **not** ask for more identity documents. Send from the privacy address. Be plain.

### Template — user notification

> We think some Problem Bank account data may have been accessed without permission on **[date]**. This can include your email, username, and study history. Passwords are stored as hashes, not the password itself, but you should choose a new password on the site and anywhere you reused it. We have [contained / taken the site down / rotated keys]. You do not need to send us ID. Questions: **[PRIVACY_CONTACT_EMAIL]**. You can also complain to the ICO (ico.org.uk).

---

## 5. Evidence to keep

- Host access logs (keep **30 days** in production — configure the panel)
- A copy of the DB from *before* you patched, plus the backup taken after contain
- The time you became aware (start of the 72-hour clock)
- Who you told and when

Do not put passwords, session cookies, reset tokens, or question answers into tickets or chat.

---

## 6. After-action

Write one page: what happened, what data, how many people, what you told the ICO, what you changed. Store it off the public repo.
