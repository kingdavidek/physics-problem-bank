# Subprocessors and third parties

Mirror this list in the privacy notice (`/privacy`). Update this file in the same change as any new outbound processor.

**Last reviewed:** 2026-08-26

| Party | Purpose | Personal data | Location | Contract | Launch position |
|---|---|---|---|---|---|
| Hosting provider (e.g. PythonAnywhere) | Runs the app and SQLite database | Everything in the database; host access logs | Confirm at deploy | Their DPA | Required |
| Resend / SendGrid / SMTP host | Verification, password reset, optional weekly digest | Email, handle, digest summary | Provider-dependent | Their DPA | Only if mail is enabled |
| jsDelivr | MathJax and Pyodide static assets | Visitor IP, user agent | Global CDN | None | **Removed in S2.2** — files now in `static/vendor/` |
| Cloudinary / PythonAnywhere assets in some lesson templates | Images and lesson scripts | Visitor IP | Global | Audit | Self-host where practical |
| OpenAI / Anthropic / DeepSeek | Lesson assist | Lesson text, context, typed question | US / China | DPA + transfer mechanism | **Disabled in production** unless `LESSON_ASSIST_ENABLED=1` (S0.10 Option A) |

**Removed in S0.11:** Google Fonts. **Removed in S2.2:** jsDelivr MathJax and Pyodide. Work Sans / Source Serif 4, MathJax, and Pyodide core are served from `/static/`.

No analytics, advertising, or social tracking pixels. Adding any of those requires a consent banner and a rewritten privacy notice in the same release (`docs/SECURITY_AND_GDPR.md` §6.4).
