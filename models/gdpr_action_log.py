"""Append-only log of operator GDPR export/erase actions (S2.4)."""
import json
import os
from pathlib import Path

from models.user import utc_now_iso

ROOT = Path(__file__).resolve().parents[1]
_ENV = 'PB_GDPR_ACTION_LOG'


def log_path() -> Path:
    override = (os.environ.get(_ENV) or '').strip()
    if override:
        return Path(override)
    return ROOT / 'data' / 'gdpr_actions.log'


def append_gdpr_action(action, handle, *, row_counts=None, operator='cli'):
    """Append one JSON line. Do not log emails, tokens, or answer content."""
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        'ts': utc_now_iso(),
        'action': action,
        'handle': handle,
        'operator': operator,
        'row_counts': row_counts or {},
    }
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, default=str) + '\n')
    return path
