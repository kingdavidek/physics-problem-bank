"""Append-only log of S3 cadence checks (weekly / monthly / restore drill)."""
import json
import os
from pathlib import Path

from models.user import utc_now_iso

ROOT = Path(__file__).resolve().parents[1]
_ENV = 'PB_CADENCE_LOG'


def log_path() -> Path:
    override = (os.environ.get(_ENV) or '').strip()
    if override:
        return Path(override)
    return ROOT / 'data' / 'cadence_log.jsonl'


def append_cadence(kind, *, summary=None, operator='cli'):
    """Append one JSON line. Do not log emails, tokens, or answer content."""
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        'ts': utc_now_iso(),
        'kind': kind,
        'operator': operator,
        'summary': summary or {},
    }
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, default=str) + '\n')
    return path
