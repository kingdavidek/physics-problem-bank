"""S3 cadence CLI smoke — run: python scripts/test_s3_cadence_smoke.py"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ['SITE_URL'] = 'http://127.0.0.1:5000'
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-s3-cadence-smoke')
os.environ['PB_BACKUP_PASSPHRASE'] = 's3-cadence-passphrase-not-for-prod'

from backup_sqlite import MAGIC, run_backup  # noqa: E402


def _run(args, env, cwd):
    return subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / 'ops_cadence.py'), *args],
        cwd=str(cwd),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def main():
    with tempfile.TemporaryDirectory(prefix='pb_s3_cadence_') as raw:
        tmp = Path(raw)
        log_path = tmp / 'cadence_log.jsonl'
        backup_dir = tmp / 'backups'
        scratch = tmp / 'scratch.db'
        src = tmp / 'source.db'

        conn = sqlite3.connect(str(src))
        try:
            conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, handle TEXT)')
            conn.execute("INSERT INTO users (handle) VALUES ('s3drill')")
            conn.commit()
        finally:
            conn.close()

        written = run_backup(
            src=src,
            backup_dir=backup_dir,
            keep=14,
            pass_text=os.environ['PB_BACKUP_PASSPHRASE'],
        )
        assert written.suffix == '.enc'
        assert written.read_bytes().startswith(MAGIC)

        env = {
            **os.environ,
            'PB_CADENCE_LOG': str(log_path),
            'PB_BACKUP_DIR': str(backup_dir),
            'PB_DB_PATH': str(tmp / 'live.db'),
        }

        weekly = _run(['--json', 'weekly', '--backup-dir', str(backup_dir)], env, tmp)
        assert weekly.returncode == 0, weekly.stderr
        weekly_data = json.loads(weekly.stdout)
        assert weekly_data['backup_ok'] is True
        assert weekly_data['backup_count'] >= 1

        missing = _run(
            ['--json', 'weekly', '--backup-dir', str(tmp / 'empty'), '--strict'],
            env,
            tmp,
        )
        assert missing.returncode == 1

        gate = _run(['--json', 'feature-gate'], env, tmp)
        assert gate.returncode == 0, gate.stderr
        gate_data = json.loads(gate.stdout)
        assert len(gate_data['questions']) == 4
        assert 'personal data' in gate_data['questions'][0]

        live = tmp / 'live.db'
        refuse = _run(
            ['restore-drill', '--from', str(written), '--to', str(live)],
            env,
            tmp,
        )
        assert refuse.returncode == 1
        assert 'live database' in (refuse.stderr or '').lower()
        assert not live.exists()

        drill = _run(
            ['--json', 'restore-drill', '--from', str(written), '--to', str(scratch)],
            env,
            tmp,
        )
        assert drill.returncode == 0, drill.stderr + drill.stdout
        drill_data = json.loads(drill.stdout)
        assert drill_data['users'] == 1
        assert drill_data['readable'] is True
        assert scratch.is_file()

        monthly = _run(['--json', 'monthly'], env, tmp)
        assert monthly.returncode == 0, monthly.stderr
        monthly_data = json.loads(monthly.stdout)
        assert monthly_data['open_reports'] >= 0
        assert 'lockouts_active' in monthly_data

        lines = log_path.read_text(encoding='utf-8').strip().splitlines()
        kinds = [json.loads(line)['kind'] for line in lines]
        assert 'weekly' in kinds
        assert 'restore_drill' in kinds
        assert 'monthly' in kinds
        assert '@' not in log_path.read_text(encoding='utf-8')

    print('S3 cadence smoke tests passed.')


if __name__ == '__main__':
    main()
