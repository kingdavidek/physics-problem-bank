# Data-rights requests

**Audience:** you (the operator)  
**Deadline:** **one calendar month** from the day you receive the request (UK GDPR Art 12). You can extend by two months for complex cases — tell the person within the first month if you need to.  
**Not legal advice.**

Self-serve (preferred): Settings → download JSON / delete account, after email is confirmed. This file is for requests that arrive by **email**.

Companions: `docs/OPERATOR_LAUNCH.md`, `docs/INCIDENT_RESPONSE.md`, CLIs in `scripts/gdpr_export_user.py` and `scripts/gdpr_erase_user.py`.

---

## 1. What people can ask for

| Right | What you do |
|---|---|
| Access / portability (Art 15 / 20) | Export JSON |
| Erasure (Art 17) | Delete the account |
| Rectification | They can change handle/password/settings themselves; email change is not built — treat as a support note |
| Object to digest mail | Unsubscribe link or turn the setting off |
| Complain | Point them at the ICO |

Do not invent extra forms.

---

## 2. Verify identity without collecting more data

For a **simple export or delete**:

1. Reply **only** to the **registered email** on the account (the address in `users.email`).
2. Ask them to confirm the **handle**.
3. Do **not** ask for passports, school IDs, or photos.
4. If the inbox is unverified (`email_verified_at` is empty), do not honour a rights request to that address until they confirm via the in-app link — or they log in and use Settings.

If someone writes from a different address, say: sign in on the site and use Settings, or write from the email on the account.

---

## 3. Parent requesting for a child (13+)

The child can exercise rights themselves. A parent may email on their behalf.

- Still send the export **to the child’s registered email**, not only to the parent, unless the child cannot access it and the parent is clearly acting for them.
- Do not ask the parent for the child’s password.
- If unsure it is the same family, reply to the registered email: “Someone asked to download or delete @handle — reply yes if you want that.”

---

## 4. Commands

From the **production** project root (same DB as the live site):

```bash
python scripts/gdpr_export_user.py --handle NAME --out export.json
python scripts/gdpr_erase_user.py --handle NAME --confirm
```

Export first if they asked for a copy **and** deletion. Then delete. The JSON must not contain `password_hash` or other people’s emails (this is tested in `scripts/test_gdpr_smoke.py`).

Erasure is immediate on live data. Backups drop it within 14 days (say so if they ask). Handles stay reserved 90 days.

---

## 5. Log of requests

Keep a private log **off git** (spreadsheet or a locked note) for email requests, **and** check `data/gdpr_actions.log` (gitignored) for CLI export/erase. Columns for the human log:

| Date received | Handle | Request type | How verified | Date completed | Outcome | Notes |
|---|---|---|---|---|---|---|
| | | export / erase / other | registered email reply | | done / refused | |

CLI lines are JSON: `ts`, `action`, `handle`, `operator`, `row_counts`. Override path with `PB_GDPR_ACTION_LOG`.

---

## 6. Refusals

You can refuse if the request is manifestly unfounded or excessive. For this product that should be rare. If you refuse, say why, and that they can complain to the ICO. Do not ghost the request.
