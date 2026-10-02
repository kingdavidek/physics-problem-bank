"""E8 Phase 7: idle-life behavioural smoke for static/js/zorp-motion.js in Node (virtual clock, fake DOM).

Runs scripts/zorp_idle_harness.js against the real runtime and rig island on a virtual clock: idle life
starts only at full motion, visible, on screen and quiet; pauses on hidden tabs, off-screen, typing and
busy mascots; stop() cancels it; timers are offset per mascot; the expression never changes.
Skips cleanly when `node` is not on PATH.

Run: python scripts/test_zorp_idle_smoke.py
"""
import os

os.environ['PB_TESTING'] = '1'

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HARNESS = ROOT / 'scripts' / 'zorp_idle_harness.js'
RUNTIME = ROOT / 'static' / 'js' / 'zorp-motion.js'


def main():
    from models import zorp_rig

    node = shutil.which('node')
    if not node:
        print('node not found on PATH -- skipping zorp idle behavioural smoke.')
        return
    with tempfile.TemporaryDirectory() as tmp:
        rig = Path(tmp) / 'rig.json'
        rig.write_text(json.dumps({
            'island': zorp_rig.rig_json(),
            'channels': {k: list(v) for k, v in zorp_rig.CHANNELS.items()},
        }), encoding='utf-8')
        result = subprocess.run([node, str(HARNESS), str(RUNTIME), str(rig)], cwd=str(ROOT),
                                check=False, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit('zorp idle behavioural smoke FAILED (see node output above)')
    print('Zorp idle behavioural smoke OK')


if __name__ == '__main__':
    main()
