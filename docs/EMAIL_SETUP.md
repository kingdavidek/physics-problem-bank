# Weekly email digest — launch setup

This guide is for **after** the digest code is deployed. The app already includes opt-in settings, HTML/text templates, unsubscribe links, preview scripts, and a batch sender — but **no emails leave the server** until you configure a provider and schedule the job.

## What is already built

- **Opt-in** — Settings → “Send me a weekly study recap email” (`email_weekly_digest`, default off)
- **Content** — Same weekly recap as on your profile (active days, topics, best quiz, streak)
- **Unsubscribe** — Signed link at `/email/unsubscribe?token=…`
- **API** — `PATCH /api/v1/me/settings` with `email_weekly_digest`; preview via `GET /api/v1/me/email/digest-preview`; test send via `POST /api/v1/me/email/test-digest`
- **Scripts** — `scripts/preview_weekly_digest.py`, `scripts/send_weekly_digest.py`
- **Send log** — `email_digest_log` table (one row per user per week, prevents duplicates)

## Step 1 — Choose an email provider

Pick one transactional email service (recommended for a small app):

| Provider | Env vars | Notes |
|----------|----------|--------|
| **[Resend](https://resend.com)** | `MAIL_PROVIDER=resend`, `RESEND_API_KEY` | Simple API, good free tier |
| **[SendGrid](https://sendgrid.com)** | `MAIL_PROVIDER=sendgrid`, `SENDGRID_API_KEY` | Widely used |
| **SMTP** (e.g. Gmail app password, Mailgun SMTP) | `MAIL_PROVIDER=smtp`, `SMTP_*` | Works on PythonAnywhere if outbound SMTP is allowed |
| **Console (dev only)** | `MAIL_PROVIDER=console` | Prints to stdout; no real delivery |

You need a **domain you control** (e.g. `yourdomain.com`) for production. Sending from `@gmail.com` via API often fails SPF/DKIM checks.

## Step 2 — DNS (SPF, DKIM, optional DMARC)

In your provider’s dashboard, add the DNS records they give you for your sending domain. Typical setup:

1. **SPF** — TXT on `@` or mail subdomain authorizing the provider to send
2. **DKIM** — CNAME/TXT for cryptographic signing
3. **DMARC** (optional but recommended) — TXT `_dmarc` policy once SPF/DKIM pass

Wait for DNS propagation (often 15 minutes–48 hours). Use the provider’s “verify domain” tool until green.

## Step 3 — Set environment variables

Copy from `.env.example` into production (PythonAnywhere Web tab or WSGI file). Minimum for live sending:

```bash
SECRET_KEY=your-long-random-production-secret
SITE_URL=https://yourdomain.com

MAIL_ENABLED=1
MAIL_PROVIDER=resend
MAIL_FROM_EMAIL=noreply@yourdomain.com
MAIL_FROM_NAME=Problem Bank
RESEND_API_KEY=re_xxxxxxxx
```

**Important:** `SECRET_KEY` must be stable in production — it signs unsubscribe links. Changing it invalidates old unsubscribe URLs.

Optional:

```bash
# Skip users with zero active days this week (default on)
EMAIL_DIGEST_SKIP_INACTIVE=1
```

For local testing without sending:

```bash
MAIL_PROVIDER=console
SITE_URL=http://127.0.0.1:5000
```

## Step 4 — Deploy the latest code

Deploy as usual (see `docs/DEPLOY.md`). On first request, SQLite migrations add:

- `user_profile_settings.email_weekly_digest`
- `email_digest_log` table

No manual SQL required.

## Step 5 — Test before go-live

On your **production** server (or locally with console provider):

```bash
# Preview text/HTML for your account
python scripts/preview_weekly_digest.py --handle yourhandle

# Dry-run batch (console provider or --dry-run)
python scripts/send_weekly_digest.py --dry-run

# Force one real send to yourself (opt-in not required with --force-handle)
python scripts/send_weekly_digest.py --handle yourhandle --force-handle
```

Also in the browser:

1. Log in → **Settings** → enable weekly recap → **Save**
2. Click **Send test recap** (visible when mail is configured or using console)
3. Open the email — check links (`SITE_URL`, profile, unsubscribe)
4. Click **Unsubscribe** — confirm setting turns off

Or via API (Bearer token):

```bash
curl -X POST https://yourdomain.com/api/v1/me/email/test-digest \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Step 6 — Schedule the weekly job

The app does **not** send digests automatically. Add a **scheduled task** (cron) on your host.

**Suggested schedule:** Monday 09:00 UTC (adjust to your audience).

**PythonAnywhere scheduled task** (example):

```bash
cd /home/youruser/physics-problem-bank && \
MAIL_ENABLED=1 MAIL_PROVIDER=resend RESEND_API_KEY=... \
SITE_URL=https://yourdomain.com SECRET_KEY=... \
/usr/local/bin/python3.10 scripts/send_weekly_digest.py
```

Prefer setting env vars in the PA **Web** config and sourcing them in the task script, rather than pasting secrets in the command line.

**Linux cron** (example — Sunday 8pm local):

```cron
0 20 * * 0 cd /path/to/physics-problem-bank && /usr/bin/python3 scripts/send_weekly_digest.py >> /var/log/pb-digest.log 2>&1
```

The script only emails users who:

1. Opted in (`email_weekly_digest = 1`)
2. Have not already received this week’s digest (by `week_key` = Monday’s date)
3. Had at least one active day in the last 7 days (unless `EMAIL_DIGEST_SKIP_INACTIVE=0`)

## Step 7 — Monitor after launch

- Check `email_digest_log` for `failed` rows and error messages
- Watch provider dashboard for bounces/spam complaints
- If deliverability is poor, review DNS and “from” address reputation

Query recent sends (SQLite):

```sql
SELECT u.handle, l.week_key, l.status, l.error_message, l.sent_at
FROM email_digest_log l
JOIN users u ON u.id = l.user_id
ORDER BY l.sent_at DESC
LIMIT 20;
```

## Step 8 — Legal / UX checklist (your responsibility)

- [ ] Privacy policy mentions optional marketing/activity emails and unsubscribe
- [ ] Weekly email is **opt-in** (already default off in app)
- [ ] Unsubscribe works without logging in (link in every email)
- [ ] `SITE_URL` uses HTTPS in production

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| “Email sending is not enabled” in Settings | `MAIL_ENABLED=1` not set, or provider not `console` |
| Unsubscribe link 404 / wrong host | `SITE_URL` missing or wrong |
| Invalid unsubscribe link after deploy | `SECRET_KEY` changed |
| No one receives mail | Users not opted in; or all skipped (no activity); or cron not running |
| Duplicate emails same week | Should not happen — check `email_digest_log`; don’t run script twice with different `week_key` logic |
| SMTP blocked on host | Use Resend/SendGrid API instead of raw SMTP |

## Quick reference — files

| File | Purpose |
|------|---------|
| `models/email_digest.py` | Build, render, send, log, tokens |
| `scripts/send_weekly_digest.py` | Production batch sender |
| `scripts/preview_weekly_digest.py` | Local preview |
| `docs/EMAIL_SETUP.md` | This guide |
| `.env.example` | Variable template |
