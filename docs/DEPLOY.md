# Deploying Problem Bank (PythonAnywhere / production)

## Pre-deploy checklist

- [ ] Set a strong **`SECRET_KEY`** env var (never use the dev default in production).
- [ ] Serve the site over **HTTPS** (required for PWA install and secure cookies).
- [ ] Configure **`CORS_ORIGINS`** if a native app or separate dev frontend calls the API (comma-separated origins, e.g. `https://app.example.com,http://localhost:5173`).
- [ ] Do **not** set `PB_TESTING=1` in production (disables daily rate limits; smoke tests only).
- [ ] Ensure `data/quicktest.db` is writable and backed up regularly.
- [ ] Run smoke tests locally: `python scripts/run_smoke_tests.py`
- [ ] Confirm `/api/v1/health` returns `{ "ok": true, "status": "up" }`.

## PythonAnywhere notes

1. **WSGI** — point the WSGI file at the Flask `app` object (`from app import app as application` or equivalent).
2. **Static files** — map `/static/` to the project `static/` directory.
3. **Service worker** — `/sw.js` is served by Flask with `Cache-Control: no-cache`. After deploys, users may need one refresh to pick up a new SW version.
4. **Database** — SQLite lives at `data/quicktest.db`. Use PythonAnywhere scheduled tasks or manual copy for backups.
5. **Environment variables** — set in the Web tab or WSGI file:
   - `SECRET_KEY`
   - `CORS_ORIGINS` (optional)
   - Lesson assist / OpenAI keys if used (`LESSON_ASSIST_*` — see `.env` example in repo)
   - Weekly digest email (`MAIL_*`, `SITE_URL` — see **`docs/EMAIL_SETUP.md`**)

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

- Session cookies: `HttpOnly`, `SameSite=Lax` (default in app config).
- API tokens: Bearer only over HTTPS; users can revoke via Settings → **Log out all devices**.
- Rate limits apply per user (or IP when anonymous) — see `docs/API.md`.
- Content-Security-Policy is set on all responses; Pyodide lessons add cross-origin isolation headers.

## CI

GitHub Actions workflow `.github/workflows/smoke.yml` runs all `scripts/test_*_smoke.py` on push/PR.

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
