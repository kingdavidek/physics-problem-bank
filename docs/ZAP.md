# OWASP ZAP baseline (S2.3)

**Audience:** operator / next agent  
**Not a substitute for a pentest.** Baseline is for regressions and obvious misconfig.

Run against a **throwaway** instance (`PB_TESTING=1` is fine for local; do not point ZAP at production with real pupil data).

## Local

```bash
PB_TESTING=1 SECRET_KEY=zap-local python app.py
```

In another terminal:

```bash
docker run --rm --network host -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://127.0.0.1:5000 -J zap-report.json
```

On Windows, `--network host` may not work; use `-p 8080:8080` and a target the container can reach, or run WSL.

GitHub: **Actions → ZAP baseline → Run workflow** (`.github/workflows/zap.yml`). The job is `workflow_dispatch` only and `continue-on-error`.

## Accepted findings (triage)

Record new alerts here when you accept them. Re-open if the code changes.

| Alert | Why accepted | Review |
|---|---|---|
| CSP `style-src 'unsafe-inline'` | Lesson SVG and presentation still use style attributes. Scripts no longer use `unsafe-inline`. | S2 / S3 |
| CSP `script-src` `'unsafe-eval'` / `'wasm-unsafe-eval'` | Required by self-hosted MathJax and Pyodide. Documented in `docs/SECURITY_AND_GDPR.md`. | Keep |
| Missing `Content-Security-Policy-Report-Only` | We enforce CSP; report-only is optional. | Keep |
| Cookie `Secure` on HTTP localhost | Production sets Secure when `SITE_URL` is https. | Keep |
| Information disclosure — `X-Powered-By` / server version | Hosting header; set on the reverse proxy if it bothers you. | Host config |

Do not accept XSS, open redirect, or CSRF findings without a written reason.
