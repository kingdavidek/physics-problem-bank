# Deploying Problem Bank (PythonAnywhere / production)

> **Before the first deploy that real users can reach:** follow **`docs/OPERATOR_LAUNCH.md`** (your ICO fee, privacy inbox, prune/backup schedule). Phases **S0–S2 code are shipped**. Set `PB_BACKUP_PASSPHRASE` before the first production backup.

## Pre-deploy checklist

- [ ] Set a strong **`SECRET_KEY`** env var (app **refuses** to start with the default outside testing / `PB_ALLOW_DEV_SECRET`).
- [ ] Serve the site over **HTTPS** (required for PWA install and secure cookies; `SITE_URL=https://…` enables Secure cookies).
- [ ] Configure **`CORS_ORIGINS`** if a native app or separate dev frontend calls the API (comma-separated origins, e.g. `https://app.example.com,http://localhost:5173`).
- [ ] Do **not** set `PB_TESTING=1` or `PB_ALLOW_DEV_SECRET=1` in production.
- [ ] Ensure `data/quicktest.db` is writable and backed up regularly (use `python scripts/backup_sqlite.py` on a schedule with `PB_BACKUP_PASSPHRASE`; keep backups off git — DB files are gitignored).
- [ ] Run smoke tests locally: `python scripts/run_smoke_tests.py`
- [ ] Confirm `/api/v1/health` returns `{ "ok": true, "status": "up" }` (pings the database).
- [ ] Security posture details: `docs/SOLID_DRAFT_SECURITY.md`.
- [ ] **Compliance gate:** `docs/OPERATOR_LAUNCH.md` complete (ICO number in `ICO_REGISTRATION_NUMBER`, monitored privacy inbox, daily backup + prune). See `docs/SECURITY_AND_GDPR.md` §7.

## PythonAnywhere notes

1. **WSGI** — point the WSGI file at the Flask `app` object (`from app import app as application` or equivalent).
2. **Static files** — map `/static/` to the project `static/` directory.
3. **Service worker** — `/sw.js` is served by Flask with `Cache-Control: no-cache`. After deploys, users may need one refresh to pick up a new SW version.
4. **Database** — SQLite lives at `data/quicktest.db`. Back it up with `python scripts/backup_sqlite.py` (see **Encrypted backups** below).
5. **Environment variables** — set in the Web tab or WSGI file:
   - `SECRET_KEY`
   - `PB_BACKUP_PASSPHRASE` (required for production backups; also set it on the scheduled-task environment)
   - `CONTROLLER_NAME`, `PRIVACY_CONTACT_EMAIL`, `ICO_REGISTRATION_NUMBER` (shown on `/privacy`)
   - `CORS_ORIGINS` (optional)
   - Leave lesson assist **off** in production unless you have completed the S0.10 transfer paperwork: do **not** set `LESSON_ASSIST_ENABLED=1` (see `.env.example`)
   - Weekly digest email (`MAIL_*`, `SITE_URL` — see **`docs/EMAIL_SETUP.md`**)

## Encrypted backups

`scripts/backup_sqlite.py` writes Fernet-encrypted files `data/backups/quicktest-{UTC}.db.enc` when `PB_BACKUP_PASSPHRASE` is set. Production (`SITE_URL` starts with `https://`, or `FLASK_ENV=production`) **exits** if the passphrase is missing. Dev without a passphrase still writes plaintext and prints a warning.

Keep **14** newest files (`PB_BACKUP_KEEP`). Store the passphrase in the host secrets, not in git.

Restore into a **scratch** path first (never overwrite the live DB until you have opened the copy):

```bash
python scripts/restore_sqlite.py --from data/backups/quicktest-YYYYMMDDTHHMMSSZ.db.enc --to /tmp/restore.db
```

Pass `--passphrase` or rely on `PB_BACKUP_PASSPHRASE`. Then:

```bash
python -c "import sqlite3; c=sqlite3.connect('/tmp/restore.db'); print(c.execute('SELECT count(*) FROM users').fetchone())"
```

Wrong passphrase fails closed. Prove a restore after every host change; `scripts/test_backup_smoke.py` covers encrypt → restore → wrong passphrase.

## Host logs

Keep production access logs **30 days** (PythonAnywhere / VPS log rotation). Never log passwords, session cookies, reset/API tokens, or answer content. Digest stdout prints recipient emails only for the `console` provider, dry-run, or `MAIL_LOG_RECIPIENTS=1`.

## Retention prune

Schedule daily, same host as backups:

```bash
python scripts/prune_expired_data.py
```

Operator GDPR tools (email requests):

```bash
python scripts/gdpr_export_user.py --handle NAME --out export.json
python scripts/gdpr_erase_user.py --handle NAME --confirm
```

Each CLI run appends one JSON line to `data/gdpr_actions.log` (or `PB_GDPR_ACTION_LOG`). The log records handle, action, and timestamp — not emails. Gitignored.

Triage user reports with `python scripts/moderate_reports.py list` (`docs/MODERATION.md`). Optional ZAP baseline: `docs/ZAP.md`.

## Weekly email digest

Code and opt-in UI ship with the app; **you** configure the provider and cron when launching. Full checklist: **`docs/EMAIL_SETUP.md`**.

Quick production steps:

1. Set `SITE_URL`, `MAIL_ENABLED=1`, provider API key
2. Verify DNS (SPF/DKIM) with your email provider
3. Test with `python scripts/send_weekly_digest.py --handle YOURHANDLE --force-handle`
4. Schedule `scripts/send_weekly_digest.py` weekly (e.g. Monday morning UTC)


- **Manifest:** `/manifest.webmanifest`
- **Service worker:** `/sw.js` (scope `/`)
- Static assets are cache-first; **API routes are always network-only**.
- After template or static changes, bump cache version in `static/js/sw.js` if users report stale UI.

## Security

- Session cookies: `HttpOnly`, `SameSite=Lax`; `Secure` when HTTPS / `SESSION_COOKIE_SECURE=1`.
- API tokens: Bearer; default **90-day** expiry; users can revoke via Settings → **Log out all devices**.
- Rate limits apply per user (or IP when anonymous), including web login/register — see `docs/API.md`. Per-account login lockout: **15 minutes after 10 failures** (generic “Invalid email or password”).
- Cookie-session JSON API mutations require CSRF (Bearer exempt).
- Content-Security-Policy is set on all responses (`script-src` has no `unsafe-inline`; MathJax/Pyodide keep `unsafe-eval`). Pyodide lessons add cross-origin isolation headers.
- MathJax and Pyodide are self-hosted (`static/vendor/`). Disk: ~13 MB Pyodide core + ~2 MB MathJax.
- Full hardening notes: `docs/SOLID_DRAFT_SECURITY.md`.

## CI

GitHub Actions workflow `.github/workflows/smoke.yml` runs all `scripts/test_*_smoke.py` on push/PR, plus a **non-blocking** `security` job (`pip-audit`, `ruff`, `gitleaks`). Dependabot is weekly for `pip` and `github-actions` (`.github/dependabot.yml`). A Monday `pip-audit` also runs from `.github/workflows/cadence.yml` even when there are no PRs.

Keep-it-true calendar after launch: **`docs/CADENCE.md`**. On the host:

```bash
python scripts/ops_cadence.py weekly
python scripts/ops_cadence.py monthly
python scripts/ops_cadence.py restore-drill
```

`restore-drill` writes `data/restore-scratch.db` and **refuses** to overwrite the live database.

**Operator (GitHub UI, cannot be set in YAML):** Settings → Code security → enable **Secret scanning** and **Push protection**. After a clean week of security-job output, remove `continue-on-error: true` so the job is required.

## Post-deploy verification

```bash
curl -s https://your-domain/api/v1/health
curl -s https://your-domain/api/v1/topics | head
curl -sI https://your-domain/sw.js
curl -sI https://your-domain/manifest.webmanifest
```

Optional CORS check (replace origin if configured):

```bash
curl -sI -X OPTIONS https://your-domain/api/v1/health \
  -H "Origin: https://app.example.com" \
  -H "Access-Control-Request-Method: GET"
```

## Rollback

- Redeploy the previous git revision on PythonAnywhere.
- SQLite schema is forward-compatible (`CREATE IF NOT EXISTS`); no down-migrations required for typical releases.
- Rights requests: `docs/DATA_RIGHTS.md`. Suspected breach: `docs/INCIDENT_RESPONSE.md`.
