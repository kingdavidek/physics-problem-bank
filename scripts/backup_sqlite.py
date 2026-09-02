"""Copy SQLite DB to a timestamped backup under data/backups/.

Usage (cron / PythonAnywhere scheduled task):
  python scripts/backup_sqlite.py

Restore:
  python scripts/restore_sqlite.py --from data/backups/quicktest-….db.enc --to /tmp/restore.db

Env:
  PB_DB_PATH — source DB (default: data/quicktest.db)
  PB_BACKUP_DIR — destination directory (default: data/backups)
  PB_BACKUP_KEEP — how many newest backups to retain (default: 14)
  PB_BACKUP_PASSPHRASE — required in production; encrypts with Fernet
"""
from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAGIC = b'PBENC1'
SALT_LEN = 16
KDF_ITERATIONS = 480_000


def _is_production() -> bool:
    site = (os.environ.get('SITE_URL') or '').strip().lower()
    return site.startswith('https://') or os.environ.get('FLASK_ENV') == 'production'


def passphrase() -> str:
    return (os.environ.get('PB_BACKUP_PASSPHRASE') or '').strip()


def _fernet(pass_text: str, salt: bytes):
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(pass_text.encode('utf-8')))
    return Fernet(key)


def encrypt_bytes(plain: bytes, pass_text: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    token = _fernet(pass_text, salt).encrypt(plain)
    return MAGIC + salt + token


def decrypt_bytes(blob: bytes, pass_text: str) -> bytes:
    if not blob.startswith(MAGIC):
        raise ValueError('Not an encrypted Problem Bank backup (missing PBENC1 header)')
    salt = blob[len(MAGIC):len(MAGIC) + SALT_LEN]
    token = blob[len(MAGIC) + SALT_LEN:]
    return _fernet(pass_text, salt).decrypt(token)


def snapshot_sqlite(src: Path, dest: Path) -> None:
    """Consistent copy via the SQLite backup API (includes committed WAL)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(str(src))
    target = sqlite3.connect(str(dest))
    try:
        source.backup(target)
        target.commit()
    finally:
        target.close()
        source.close()


def write_backup_file(snapshot: Path, dest_db: Path, pass_text: str) -> Path:
    data = snapshot.read_bytes()
    if pass_text:
        dest = dest_db.with_name(dest_db.name + '.enc')
        dest.write_bytes(encrypt_bytes(data, pass_text))
        return dest
    dest_db.write_bytes(data)
    return dest_db


def restore_backup_file(src: Path, dest: Path, pass_text: str = '') -> Path:
    blob = src.read_bytes()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if blob.startswith(MAGIC):
        if not pass_text:
            raise ValueError('Encrypted backup requires PB_BACKUP_PASSPHRASE')
        dest.write_bytes(decrypt_bytes(blob, pass_text))
    else:
        dest.write_bytes(blob)
    return dest


def _backup_sort_key(path: Path):
    return path.name


def prune_old_backups(backup_dir: Path, keep: int) -> list[Path]:
    files = sorted(
        list(backup_dir.glob('quicktest-*.db')) + list(backup_dir.glob('quicktest-*.db.enc')),
        key=_backup_sort_key,
        reverse=True,
    )
    removed = []
    for old in files[keep:]:
        old.unlink(missing_ok=True)
        removed.append(old)
        for suffix in ('-wal', '-shm'):
            Path(str(old) + suffix).unlink(missing_ok=True)
    return removed


def run_backup(
    src: Path | None = None,
    backup_dir: Path | None = None,
    keep: int | None = None,
    pass_text: str | None = None,
) -> Path:
    src = src or Path(os.environ.get('PB_DB_PATH') or (ROOT / 'data' / 'quicktest.db'))
    backup_dir = backup_dir or Path(os.environ.get('PB_BACKUP_DIR') or (ROOT / 'data' / 'backups'))
    keep = int(os.environ.get('PB_BACKUP_KEEP', '14') if keep is None else keep)
    pass_text = passphrase() if pass_text is None else pass_text

    if _is_production() and not pass_text:
        raise SystemExit(
            'PB_BACKUP_PASSPHRASE is required in production. '
            'Set it before running backups (see docs/DEPLOY.md).'
        )

    if not src.is_file():
        raise FileNotFoundError(f'Source DB not found: {src}')

    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    snapshot = backup_dir / f'.snapshot-{stamp}.db'
    dest = backup_dir / f'quicktest-{stamp}.db'
    try:
        snapshot_sqlite(src, snapshot)
        written = write_backup_file(snapshot, dest, pass_text)
    finally:
        snapshot.unlink(missing_ok=True)
    for old in prune_old_backups(backup_dir, keep):
        print(f'Removed old backup {old.name}')
    return written


def main() -> int:
    try:
        written = run_backup()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f'Wrote {written}')
    if passphrase():
        print('Backup is encrypted (Fernet). Restore with scripts/restore_sqlite.py')
    else:
        print('WARNING: backup is plaintext — set PB_BACKUP_PASSPHRASE before a public launch')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
