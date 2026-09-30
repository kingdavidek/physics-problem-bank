"""E8 Phase 3: behavioural smoke for views and the pinch-turn in static/js/zorp-motion.js (Node).

Runs scripts/zorp_rig_harness.js against the real runtime, the real rig island
(models/zorp_rig.py rig_json()), the real parts library and real rendered buddy_mascot() markup.
Deterministic: every animation in the harness is a fake that finishes only when a scenario says so.
It proves that turn() under reduced motion (unless required) and off makes no animation calls,
that the resting view is written through commitStyles() (with an applyRest fallback), the
composite:'add' feature detection and its fallback, and that stop() restores the resting view
without leaking animations. Skips cleanly when `node` is not on PATH.

Run: python scripts/test_zorp_rig_smoke.py
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

HARNESS = ROOT / 'scripts' / 'zorp_rig_harness.js'
RUNTIME = ROOT / 'static' / 'js' / 'zorp-motion.js'


def _fixture():
    from app import app  # noqa: E402
    from models import zorp_rig  # noqa: E402

    with app.app_context():
        buddy = app.jinja_env.get_template('partials/buddy.html').module
        library = app.jinja_env.get_template('partials/zorp_library.html').render()
        svgs = {
            'front': str(buddy.buddy_mascot()),
            'sideL': str(buddy.buddy_mascot(view='side', facing='l')),
        }
    tpl = library[library.index('<template'):library.index('</template>') + len('</template>')]
    return {'island': zorp_rig.rig_json(), 'library': tpl, 'svgs': svgs}


def main():
    node = shutil.which('node')
    if not node:
        print('node not found on PATH -- skipping zorp rig (views and turn) behavioural smoke.')
        return
    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp) / 'fixture.json'
        fixture.write_text(json.dumps(_fixture()), encoding='utf-8')
        result = subprocess.run([node, str(HARNESS), str(RUNTIME), str(fixture)], cwd=str(ROOT),
                                check=False, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit('zorp rig behavioural smoke FAILED (see node output above)')
    print('Zorp rig behavioural smoke OK')


if __name__ == '__main__':
    main()
