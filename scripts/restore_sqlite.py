"""Restore a Problem Bank SQLite backup (plaintext or Fernet-encrypted).

Usage:
  python scripts/restore_sqlite.py --from data/backups/quicktest-….db.enc --to /tmp/restore.db

Uses PB_BACKUP_PASSPHRASE when the file is encrypted.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from backup_sqlite import passphrase, restore_backup_file  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description='Restore a Problem Bank SQLite backup.')
    parser.add_argument('--from', dest='src', required=True, help='Backup file (.db or .db.enc)')
    parser.add_argument('--to', dest='dest', required=True, help='Destination .db path')
    parser.add_argument('--passphrase', default='', help='Override PB_BACKUP_PASSPHRASE')
    args = parser.parse_args()
    src = Path(args.src)
    dest = Path(args.dest)
    if not src.is_file():
        print(f'Backup not found: {src}', file=sys.stderr)
        return 1
    pass_text = (args.passphrase or passphrase()).strip()
    try:
        restore_backup_file(src, dest, pass_text)
    except Exception as exc:
        print(f'Restore failed: {exc}', file=sys.stderr)
        return 1
    try:
        with sqlite3.connect(str(dest)) as conn:
            conn.execute('SELECT count(*) FROM sqlite_master').fetchone()
    except sqlite3.Error as exc:
        print(f'Restored file is not a readable SQLite database: {exc}', file=sys.stderr)
        return 1
    print(f'Restored {dest}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
