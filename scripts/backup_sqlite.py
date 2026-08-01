"""Copy SQLite DB to a timestamped backup under data/backups/.

Usage (cron / PythonAnywhere scheduled task):
  python scripts/backup_sqlite.py

Env:
  PB_DB_PATH — source DB (default: data/quicktest.db)
  PB_BACKUP_DIR — destination directory (default: data/backups)
  PB_BACKUP_KEEP — how many newest backups to retain (default: 14)
"""
from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    src = Path(os.environ.get('PB_DB_PATH') or (ROOT / 'data' / 'quicktest.db'))
    backup_dir = Path(os.environ.get('PB_BACKUP_DIR') or (ROOT / 'data' / 'backups'))
    keep = int(os.environ.get('PB_BACKUP_KEEP', '14'))
    if not src.is_file():
        print(f'Source DB not found: {src}', file=sys.stderr)
        return 1
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest = backup_dir / f'quicktest-{stamp}.db'
    shutil.copy2(src, dest)
    # Also copy WAL/SHM if present (best-effort consistency).
    for suffix in ('-wal', '-shm'):
        side = Path(str(src) + suffix)
        if side.is_file():
            shutil.copy2(side, Path(str(dest) + suffix))
    print(f'Wrote {dest}')
    backups = sorted(backup_dir.glob('quicktest-*.db'), reverse=True)
    for old in backups[keep:]:
        old.unlink(missing_ok=True)
        for suffix in ('-wal', '-shm'):
            Path(str(old) + suffix).unlink(missing_ok=True)
        print(f'Removed old backup {old.name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
