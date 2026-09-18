# Keep-it-true cadence (S3)

**Audience:** operator (David) and the next agent  
**Status:** shipped 2026-08-26 — this is the calendar, not a product feature.  
**Companions:** `docs/SECURITY_AND_GDPR.md` §3 / §6.1, `docs/DPIA.md`, `docs/SUBPROCESSORS.md`, `docs/MODERATION.md`, `docs/DEPLOY.md`

Dependabot is already weekly (`.github/dependabot.yml`). Smoke + `pip-audit` already run on every PR (`.github/workflows/smoke.yml`). This file is how you **keep doing it** after S0–S2.

Do **not** treat a missed weekly check as an incident. Treat a missed **quarterly restore** or an unread reports queue as one.

---

## Commands

```bash
python scripts/ops_cadence.py weekly
python scripts/ops_cadence.py monthly
python scripts/ops_cadence.py restore-drill
python scripts/ops_cadence.py feature-gate
```

`--json` for scripts. Each weekly / monthly / restore-drill run appends one line to `data/cadence_log.jsonl` (gitignored; no emails). Override path with `PB_CADENCE_LOG`.

---

## Every release

- `python scripts/run_smoke_tests.py`
- Production env must **not** have `PB_TESTING=1`
- If JS/CSS/templates changed, bump `CACHE_VERSION` in `static/js/sw.js` and the matching `?v=` query params

CI already runs the smoke suite on push/PR.

---

## Weekly (operator, ~10 minutes)

1. `python scripts/ops_cadence.py weekly` on the **host** (or a machine that can see `data/backups/`). Expect `backup_ok: true`. `--strict` exits 1 if the newest backup is older than 8 days or missing.
2. GitHub → Dependabot PRs. Merge or dismiss with a reason.
3. Actions → **S3 cadence (pip-audit)** (Monday 09:00 UTC, also `workflow_dispatch`) and the non-blocking `security` job on the last PR.
4. Confirm the host prune cron still logs JSON counts: `python scripts/prune_expired_data.py`

Until public launch there may be no backups. That is expected; do not use `--strict` locally.

---

## Monthly

1. `python scripts/ops_cadence.py monthly` — open reports and accounts with failed-login pressure.
2. If `open_reports` > 0, `python scripts/moderate_reports.py list` and follow `docs/MODERATION.md` timescales.

---

## Quarterly

1. `python scripts/ops_cadence.py restore-drill`  
   Restores the **newest** backup to `data/restore-scratch.db` (gitignored). **Refuses** to overwrite the live DB. Then:

   ```bash
   python -c "import sqlite3; c=sqlite3.connect('data/restore-scratch.db'); print(c.execute('SELECT count(*) FROM users').fetchone())"
   ```

   Delete the scratch file when you are done looking. Wrong passphrase fails closed.
2. Re-read `templates/legal_privacy.html` (and `/privacy/simple`) against what the code actually stores.
3. Review `docs/SUBPROCESSORS.md`. Remove anything you no longer use; add anything you added.
4. Set **Last reviewed** at the top of `docs/DPIA.md` and add a line to the review log there.

Prove a restore after every **host** change as well (`docs/DEPLOY.md`).

---

## Annually, or on any material change

Revisit the DPIA (`docs/DPIA.md` review triggers). Renew the ICO fee (`docs/OPERATOR_LAUNCH.md`). Material means: new data category, G8 teacher mode, enabling lesson assist, analytics, new processor, or a personal-data breach.

---

## On every new feature (agents too)

Run `python scripts/ops_cadence.py feature-gate` and answer the four questions in `docs/SECURITY_AND_GDPR.md` §6.1 **before** writing code. If any answer is yes, the matching privacy/ROPA/DPIA/subprocessor edit ships in the **same** PR.
