"""E8 Phase 4: behavioural smoke for static/js/zorp-poses.js (poses, arm shapes, beat engine, new clips) in Node.

Runs scripts/zorp_poses_harness.js against the real runtime pair (zorp-motion.js + zorp-poses.js), the real
island, parts library and rendered markup. Deterministic: a virtual clock replaces setTimeout and every animation
is a fake that only finishes when a scenario says so. It proves compileBeats() gives one keyframe list per
moving part, every clip ends on a positive preset inside its plan duration, stop() cancels everything and puts
arm shapes and the face back, reduced/off make no animate calls, and the pair degrades to Phases 1-3 when
zorp-poses.js is absent. It also pins the pose table embedded in zorp-poses.js to models/zorp_rig.POSES.
Skips the Node part cleanly when `node` is not on PATH.

Run: python scripts/test_zorp_poses_smoke.py
"""
import os

os.environ['PB_TESTING'] = '1'

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HARNESS = ROOT / 'scripts' / 'zorp_poses_harness.js'
RUNTIME = ROOT / 'static' / 'js' / 'zorp-motion.js'
POSES_JS = ROOT / 'static' / 'js' / 'zorp-poses.js'


def _embedded_poses():
    text = POSES_JS.read_text(encoding='utf-8')
    m = re.search(r'/\*POSES-BEGIN\*/\s*var POSES = (\{.*?\});\s*/\*POSES-END\*/', text, re.S)
    assert m, 'zorp-poses.js lost its POSES-BEGIN/POSES-END markers'
    return json.loads(m.group(1))


def test_embedded_pose_table_matches_rig():
    from models import zorp_rig

    want = json.loads(zorp_rig.poses_json())
    assert _embedded_poses() == want, (
        'the POSES table in static/js/zorp-poses.js differs from models/zorp_rig.POSES; regenerate it with '
        "python -c \"from models import zorp_rig; print(zorp_rig.poses_json())\" and paste it between the markers"
    )


def test_poses_file_registers_through_the_hook_only():
    js = POSES_JS.read_text(encoding='utf-8')
    assert 'pb.register(' in js and 'window.pbZorp' in js
    assert 'innerHTML' not in js and 'setInterval' not in js
    for banned in ('lottie', 'jsdelivr', 'unpkg', 'gsap'):
        assert banned not in js.lower()
    # graceful degradation is structural too: the file is inert when the runtime or the hook is missing
    assert "typeof pb.register !== 'function'" in js and 'pb.hasPose' in js


def _fixture():
    from app import app  # noqa: E402
    from models import zorp_rig  # noqa: E402

    with app.app_context():
        buddy = app.jinja_env.get_template('partials/buddy.html').module
        library = app.jinja_env.get_template('partials/zorp_library.html').render()
        svgs = {
            'front': str(buddy.buddy_mascot()),
            'sideL': str(buddy.buddy_mascot(view='side', facing='l')),
            'posed': str(buddy.buddy_mascot(face='grin', pose='fist-up')),
        }
    tpl = library[library.index('<template'):library.index('</template>') + len('</template>')]
    side_rot = {shape: [zorp_rig.side_rot(a, shape) for a in range(-180, 181)] for shape in zorp_rig.ARM_SHAPES}
    side_arms = {'wave': zorp_rig.pose_styles('wave', 'r', 'side')['armRf'].split('transform:')[1]}
    return {'island': zorp_rig.rig_json(), 'library': tpl, 'svgs': svgs, 'poses': list(zorp_rig.POSE_NAMES),
            'sideRot': side_rot, 'sideArms': side_arms}


def test_node_behaviour():
    node = shutil.which('node')
    if not node:
        print('node not found on PATH -- skipping zorp poses behavioural smoke.')
        return
    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp) / 'fixture.json'
        fixture.write_text(json.dumps(_fixture()), encoding='utf-8')
        result = subprocess.run([node, str(HARNESS), str(RUNTIME), str(POSES_JS), str(fixture)], cwd=str(ROOT),
                                check=False, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    assert result.returncode == 0, 'zorp poses behavioural smoke FAILED (see node output above)'


def main():
    test_embedded_pose_table_matches_rig()
    test_poses_file_registers_through_the_hook_only()
    test_node_behaviour()
    print('Zorp poses smoke OK')


if __name__ == '__main__':
    main()
