"""Encrypted backup / restore smoke — run: python scripts/test_backup_smoke.py"""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

os.environ['PB_BACKUP_PASSPHRASE'] = 'smoke-backup-passphrase-not-for-prod'

from backup_sqlite import MAGIC, run_backup, restore_backup_file  # noqa: E402


def main():
    with tempfile.TemporaryDirectory(prefix='pb_backup_smoke_', ignore_cleanup_errors=True) as raw:
        tmp = Path(raw)
        src = tmp / 'source.db'
        src_conn = sqlite3.connect(str(src))
        try:
            src_conn.execute('CREATE TABLE probe (id INTEGER PRIMARY KEY, note TEXT)')
            src_conn.execute("INSERT INTO probe (note) VALUES ('s1-encrypted')")
            src_conn.commit()
        finally:
            src_conn.close()

        backup_dir = tmp / 'backups'
        written = run_backup(
            src=src,
            backup_dir=backup_dir,
            keep=14,
            pass_text=os.environ['PB_BACKUP_PASSPHRASE'],
        )
        assert written.suffix == '.enc', written
        blob = written.read_bytes()
        assert blob.startswith(MAGIC)
        assert b's1-encrypted' not in blob

        dest = tmp / 'restored.db'
        restore_backup_file(written, dest, os.environ['PB_BACKUP_PASSPHRASE'])
        conn = sqlite3.connect(str(dest))
        try:
            note = conn.execute('SELECT note FROM probe').fetchone()[0]
        finally:
            conn.close()
        assert note == 's1-encrypted'

        try:
            restore_backup_file(written, tmp / 'bad.db', 'wrong-passphrase')
        except Exception:
            pass
        else:
            raise AssertionError('wrong passphrase should fail')

        old_env = os.environ.get('FLASK_ENV')
        os.environ['FLASK_ENV'] = 'production'
        try:
            try:
                run_backup(src=src, backup_dir=backup_dir, keep=14, pass_text='')
                raise AssertionError('production backup without passphrase should fail')
            except SystemExit:
                pass
        finally:
            if old_env is None:
                os.environ.pop('FLASK_ENV', None)
            else:
                os.environ['FLASK_ENV'] = old_env

    print('Backup encryption smoke tests passed.')


if __name__ == '__main__':
    main()
