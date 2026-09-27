"""Buddy quiet-gate behavioural smoke (2026-09-27 face-only-Zorp round).

Runs the *real* static/js/study-buddy.js against a small hand-rolled fake DOM +
localStorage in Node (scripts/buddy_gate_harness.js) -- no jsdom/npm deps, none
are available offline. Confirms: a prompt shows the card; clicking the primary
action or "Not now" hides only the card (the root/face stay visible, so answer
reactions keep working) and sets the 10/30-minute quiet window; an unchanged
task_mark stays quiet even after the window passes; a changed task_mark shows
again; an ignored (un-acted-on) bubble keeps showing on a later load rather than
going quiet on its own; and a throwing localStorage never crashes the page.

Skips cleanly (prints a message, exits 0) when `node` isn't on PATH, so CI
runners without Node still get a clean run rather than a false failure.

Run: python scripts/test_buddy_gate_smoke.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / 'scripts' / 'buddy_gate_harness.js'
STUDY_BUDDY_JS = ROOT / 'static' / 'js' / 'study-buddy.js'


def main():
    node = shutil.which('node')
    if not node:
        print('node not found on PATH -- skipping buddy gate behavioural smoke.')
        return
    assert HARNESS.is_file(), f'missing harness: {HARNESS}'
    assert STUDY_BUDDY_JS.is_file(), f'missing source: {STUDY_BUDDY_JS}'
    result = subprocess.run(
        [node, str(HARNESS), str(STUDY_BUDDY_JS)],
        cwd=str(ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit('buddy gate behavioural smoke FAILED (see node output above)')
    print('Buddy gate behavioural smoke OK')


if __name__ == '__main__':
    main()
