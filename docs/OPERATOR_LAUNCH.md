# Your launch checklist (operator S0.1)

**Who this is for:** you (David) — not the next AI coding agent.  
**When to do it:** when you are about to put a **real public HTTPS URL** in front of 13+ users (PythonAnywhere / `docs/MOBILE.md` M5). Not during real-world questions, UI work, or other product tracks.  
**Why it exists:** the app already has privacy pages, delete/export, and a prune script. Those pages still show placeholders until you name yourself, give parents a real inbox, pay the ICO, and schedule the daily jobs.  
**Not legal advice.** Use the ICO’s own pages if anything here disagrees with them.

Companions: `docs/DEPLOY.md` (hosting), `docs/SECURITY_AND_GDPR.md` (full S0–S3 plan), `docs/EMAIL_SETUP.md` (mail later).

---

## Do this only when launching

You can ignore this file while you are still on local `python app.py`. Start it when **any** of these is true:

- You have (or are buying) a public domain and HTTPS
- Pupils or other real 13+ users will be able to create accounts
- You are implementing **M5** in `docs/MOBILE.md` or following `docs/DEPLOY.md` for production

Until then, leaving `CONTROLLER_NAME` / `PRIVACY_CONTACT_EMAIL` unset is fine. The site must not be advertised to students with the localhost placeholders.

---

## 1. Pick a controller name and a privacy inbox

The **controller** is you (or a trading name): the person who decides why the site holds emails, handles, and study data.

| Env var | What to put | Where it appears |
|---|---|---|
| `CONTROLLER_NAME` | Your real name, or a trading name you are happy to publish | `/privacy` — “The controller is **…**” |
| `PRIVACY_CONTACT_EMAIL` | An address a parent can use. Prefer `privacy@yourdomain` | `/privacy`, `/privacy/simple`, Settings, rights emails |
| `ICO_REGISTRATION_NUMBER` | The number the ICO gives you (leave empty until then) | `/privacy` |

You must **actually read** the privacy inbox. Settings and the child-friendly notice tell people to email it.

Until these are set, the app falls back to `Problem Bank operator` and `privacy@localhost`. That is not good enough for a public 13+ site.

---

## 2. Put them in the environment (never commit `.env`)

**Local** — in the project `.env` (copy from `.env.example` if needed):

```
CONTROLLER_NAME=Your name or trading name
PRIVACY_CONTACT_EMAIL=privacy@yourdomain.com
ICO_REGISTRATION_NUMBER=
```

Restart `python app.py`, open `/privacy`, and check the name and the mailto link.

**Production (PythonAnywhere)** — set the same three in the **Web** tab environment, or in the WSGI file, then **Reload**. A `.env` next to `app.py` on the server also works (`app.py` loads it). Do not put `.env` in git.

---

## 3. Pay the ICO data protection fee

UK organisations (including sole traders) that process personal data usually must pay an **annual fee** unless an exemption applies. Once real pupils have accounts, this is almost certainly not “household use”.

Official starting points:

- Self-assessment / pay: [ico.org.uk/fee](https://ico.org.uk/for-organisations/data-protection-fee/)
- First-time register: [Register \| ICO](https://ico.org.uk/for-organisations/data-protection-fee/register/)
- GOV.UK: [Pay the data protection fee](https://www.gov.uk/data-protection-register-notify-ico-personal-data)

Practical steps:

1. Use the ICO self-assessment so you are not guessing the tier.
2. Register as a new fee payer (~15 minutes). You will need organisation name, address, staff/turnover, and a card or Direct Debit.
3. A one-person study site typically lands in the **smallest tier**. The engineering plan’s ballpark was ~£40–£60/year; GOV.UK has cited £52 or £78 for most small organisations. Direct Debit is a few pounds cheaper. **Confirm the amount on the ICO site when you pay.**
4. Your name and address go on the **public register of fee payers**. If you work from home and do not want that address published, use a PO box or other correspondence address (GOV.UK explains this).
5. Keep the **registration number** and a yearly renewal reminder.

The ICO does not send an invoice; it is a statutory fee.

---

## 4. Put the registration number in the app

When you have the number:

```
ICO_REGISTRATION_NUMBER=Z1234567
```

(use the real number)

Reload production, open `https://your-domain/privacy`, and confirm it is **not** still “Not yet registered — required before public launch”.

**S0.1 is done when:** a parent can see who you are, email you, and see a real ICO number — and you answer that inbox.

---

## 5. Schedule prune next to backups

The scripts already exist. They do nothing until something runs them **every day on the production database**, from the **project root**:

```bash
python scripts/backup_sqlite.py
python scripts/prune_expired_data.py
```

- Backup writes timestamped copies under `data/backups/` and keeps 14.
- Prune prints JSON counts (rate-limit rows, expired tokens, inactive accounts, and so on).

**PythonAnywhere:** Dashboard → **Tasks** → add two daily scheduled tasks (or one task that runs both). Working directory = project root. Example:

```bash
cd /home/YOURUSER/physics-problem-bank && /usr/bin/python3.10 scripts/backup_sqlite.py
```

```bash
cd /home/YOURUSER/physics-problem-bank && /usr/bin/python3.10 scripts/prune_expired_data.py
```

Use the same Python as the web app. After the first run, check the task log: backup should print `Wrote …`; prune should print a JSON object.

If the Web tab already sets `SECRET_KEY` / `PB_DB_PATH`, either rely on `.env` in that directory or export those vars in the task (same idea as the digest cron in `docs/EMAIL_SETUP.md`).

On a VPS, two cron lines at a quiet hour (for example 03:00 UTC) do the same thing.

Set **`PB_BACKUP_PASSPHRASE`** in the same environment as the backup task (`.env` in the project root, or export it in the task). Production (`SITE_URL=https://…` or `FLASK_ENV=production`) **refuses** a plaintext backup. Restore steps: `docs/DEPLOY.md`.

---

## 6. If a parent emails you

After launch, rights requests can also come by email (not only Settings):

```bash
python scripts/gdpr_export_user.py --handle NAME --out export.json
python scripts/gdpr_erase_user.py --handle NAME --confirm
```

Reply from the privacy address. Full runbook: **`docs/DATA_RIGHTS.md`**. Breach: **`docs/INCIDENT_RESPONSE.md`**.

---

## Done when

| Check | How you know |
|---|---|
| Name + email on `/privacy` | Real, not localhost placeholders |
| Inbox | You received and can reply to a test mail |
| ICO number on `/privacy` | Matches the ICO confirmation |
| Daily jobs | PythonAnywhere (or cron) log shows backup **and** prune succeeding |

Then continue `docs/DEPLOY.md` and, if you want Play/PWA install, `docs/MOBILE.md` M5. After launch, keep the calendar in **`docs/CADENCE.md`** (weekly backup check, monthly reports, quarterly restore). Operator S0.1 above is still the public-HTTPS gate.
