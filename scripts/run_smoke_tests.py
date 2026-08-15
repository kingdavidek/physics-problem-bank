"""Run all smoke tests — exit non-zero on first failure."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('CORS_ORIGINS', 'https://app.example.com')
os.environ['PB_TESTING'] = '1'
if os.environ.get('LESSON_ASSIST_LIVE_SMOKE', '').strip() not in ('1', 'true', 'yes', 'on'):
    os.environ['LESSON_ASSIST_MOCK'] = '1'
# Ephemeral DB so smoke never writes into a tracked/developer database file.
_smoke_dir = tempfile.mkdtemp(prefix='pb_smoke_')
os.environ['PB_DB_PATH'] = str(Path(_smoke_dir) / 'smoke.db')
SCRIPTS = sorted((ROOT / 'scripts').glob('test_*_smoke.py'))


def main():
    failures = []
    for path in SCRIPTS:
        name = path.name
        print(f'--- {name} ---')
        env = {
            **os.environ,
            'CORS_ORIGINS': os.environ.get('CORS_ORIGINS', ''),
            'PB_TESTING': '1',
            'PB_DB_PATH': os.environ['PB_DB_PATH'],
        }
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(ROOT),
            check=False,
            env=env,
        )
        if result.returncode != 0:
            failures.append(name)
        print()

    if failures:
        print(f'FAILED: {", ".join(failures)}')
        sys.exit(1)
    print(f'All {len(SCRIPTS)} smoke tests passed.')


if __name__ == '__main__':
    main()
