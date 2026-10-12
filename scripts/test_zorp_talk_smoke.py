"""E9 Phase 1: behavioural smoke for static/js/zorp-talk.js in Node (fake DOM and clock, no jsdom).

Runs scripts/zorp_talk_harness.js against the real runtime, the real talk file and the real rig island and
parts list (models/zorp_rig.py): plan caps per surface, the 9 Hz rate limit, punctuation pauses, ends closed,
reduced and off (no animate calls), hidden tab and off-screen hush, back view, quiz runner, a clip stop that
keeps talking, an expression swap mid-talk, one talker at a time, hush cleanup, text first, side art, no innerHTML.
Skips cleanly when `node` is not on PATH.

Run: python scripts/test_zorp_talk_smoke.py
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

HARNESS = ROOT / 'scripts' / 'zorp_talk_harness.js'
RUNTIME = ROOT / 'static' / 'js' / 'zorp-motion.js'
TALK = ROOT / 'static' / 'js' / 'zorp-talk.js'


def main():
    from models import zorp_rig

    node = shutil.which('node')
    if not node:
        print('node not found on PATH -- skipping zorp talk behavioural smoke.')
        return
    with tempfile.TemporaryDirectory() as tmp:
        rig = Path(tmp) / 'rig.json'
        rig.write_text(json.dumps({
            'island': zorp_rig.rig_json(),
            'channels': {k: list(v) for k, v in zorp_rig.CHANNELS.items()},
        }), encoding='utf-8')
        result = subprocess.run([node, str(HARNESS), str(RUNTIME), str(TALK), str(rig)], cwd=str(ROOT),
                                check=False, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit('zorp talk behavioural smoke FAILED (see node output above)')
    print('Zorp talk behavioural smoke OK')


if __name__ == '__main__':
    main()
