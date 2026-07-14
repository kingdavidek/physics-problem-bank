"""Run all smoke tests — exit non-zero on first failure."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('CORS_ORIGINS', 'https://app.example.com')
os.environ['PB_TESTING'] = '1'
SCRIPTS = sorted((ROOT / 'scripts').glob('test_*_smoke.py'))


def main():
    failures = []
    for path in SCRIPTS:
        name = path.name
        print(f'--- {name} ---')
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(ROOT),
            check=False,
            env={**os.environ, 'CORS_ORIGINS': os.environ.get('CORS_ORIGINS', '')},
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
