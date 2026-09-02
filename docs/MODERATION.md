# Moderation and takedown (S2.6)

**Audience:** you (the operator)  
There is **no admin UI**. That is a control (S2.5 — do not add 2FA for an operator role that does not exist). Use the CLI.

Companions: `docs/INCIDENT_RESPONSE.md`, `docs/DATA_RIGHTS.md`.

## Timescales

| Kind | Target |
|---|---|
| Safeguarding / illegal / sexual content involving a child | **Same day** — hide the content, then email the privacy address trail |
| Harassment, hate, threats | **24 hours** |
| Spam, off-topic, other | **7 days** |

If you cannot meet the target, still act; write why in the report note after `resolve`.

## Commands

```bash
python scripts/moderate_reports.py list
python scripts/moderate_reports.py resolve --id N
python scripts/moderate_reports.py hide-share --id N
python scripts/moderate_reports.py dismiss-suggestion --id N
```

`list` prints open rows (oldest first): reporter handle, reported handle, type, note, context JSON.

Context from the in-app report form may include a share or suggestion id. Hide that content **before** or as you resolve.

There is still no DM surface. Block is self-serve. Reports are user-to-user; this CLI is how you action a suggestion or shared note.

## After you act

Mark the report resolved. Do not put passwords, tokens, or the child's email in the terminal history if you can avoid it — handles are enough.
