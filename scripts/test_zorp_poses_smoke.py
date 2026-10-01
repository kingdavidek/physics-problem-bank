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
WELCOME_JS = ROOT / 'static' / 'js' / 'welcome.js'
TRIGGERS_JS = ROOT / 'static' / 'js' / 'zorp-triggers.js'


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


def _embedded_react():
    text = POSES_JS.read_text(encoding='utf-8')
    m = re.search(r'/\*REACT-BEGIN\*/\s*var REACT = (\{.*?\});\s*/\*REACT-END\*/', text, re.S)
    assert m, 'zorp-poses.js lost its REACT-BEGIN/REACT-END markers'
    return json.loads(m.group(1))


def test_react_plan_matches_runtime():
    """E8 Phase 5: the react() clip table in zorp-poses.js is models/zorp_rig.py REACT_CLIPS, and the big
    clips (fist-pump and friends) are only ever produced for the rarer moments, never for a correct answer."""
    from models import zorp_rig

    embedded = _embedded_react()
    assert embedded['clips'] == {k: list(v) for k, v in zorp_rig.REACT_CLIPS.items()}, 'REACT clips differ from zorp_rig.REACT_CLIPS'
    assert embedded['big'] == list(zorp_rig.BIG_CLIPS) and embedded['gap'] == zorp_rig.BIG_GAP_MS
    assert embedded['face'] == zorp_rig.REACT_FACES
    assert zorp_rig.BIG_GAP_MS >= 5000, 'big moments need a real minimum gap'
    # only the rarer kinds may use a big clip; correct and wrong never do
    for kind, clips in zorp_rig.REACT_CLIPS.items():
        big = [c for c in clips if c in zorp_rig.BIG_CLIPS]
        if kind in ('correct', 'wrong'):
            assert not big, f'{kind} must not use a big clip: {big}'
    assert 'fist-pump' in zorp_rig.REACT_CLIPS['streak'] and 'victory' in zorp_rig.REACT_CLIPS['first_correct']
    # every kind celebrate.js can ask for has a plan
    celebrate = (ROOT / 'static' / 'js' / 'celebrate.js').read_text(encoding='utf-8')
    kinds = set(re.findall(r"reactMascot\('(\w+)'", celebrate)) | {'correct'}
    assert kinds <= set(zorp_rig.REACT_CLIPS), kinds - set(zorp_rig.REACT_CLIPS)
    # every clip named exists in the runtime (core list or registered by zorp-poses.js)
    core = set(re.findall(r"'([\w-]+)'", re.search(r'CLIP_NAMES\s*=\s*\[([^\]]*)\]', RUNTIME.read_text(encoding='utf-8')).group(1)))
    added = set(re.findall(r"\badd\('([\w-]+)'", POSES_JS.read_text(encoding='utf-8')))
    for clips in zorp_rig.REACT_CLIPS.values():
        for clip in clips:
            assert clip in core | added, clip


def test_autoplay_allowlist_matches_runtime():
    from models import zorp_rig

    js = (ROOT / 'static' / 'js' / 'zorp-triggers.js').read_text(encoding='utf-8')
    m = re.search(r'AUTOPLAY_OK\s*=\s*\[([^\]]*)\]', js)
    assert m, 'AUTOPLAY_OK missing from zorp-triggers.js'
    assert re.findall(r"'([\w-]+)'", m.group(1)) == list(zorp_rig.AUTOPLAY_CLIPS)
    for banned in ('wobble', 'oops-encourage', 'sleep', 'dance', 'shake', 'turn'):
        assert banned not in zorp_rig.AUTOPLAY_CLIPS, banned
    assert "AUTOPLAY_OK.indexOf(clip) === -1" in js
    # every data-zorp-autoplay value in the templates is on the list
    for path in sorted((ROOT / 'templates').rglob('*.html')):
        for value in re.findall(r'data-zorp-autoplay="([^"{]+)"', path.read_text(encoding='utf-8')):
            assert value in zorp_rig.AUTOPLAY_CLIPS, f'{path.name}: data-zorp-autoplay="{value}" is not allowlisted'


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
            'sideR': str(buddy.buddy_mascot(view='side')),
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
        result = subprocess.run([node, str(HARNESS), str(RUNTIME), str(POSES_JS), str(fixture), str(WELCOME_JS), str(TRIGGERS_JS)], cwd=str(ROOT),
                                check=False, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    assert result.returncode == 0, 'zorp poses behavioural smoke FAILED (see node output above)'


def main():
    test_embedded_pose_table_matches_rig()
    test_react_plan_matches_runtime()
    test_autoplay_allowlist_matches_runtime()
    test_poses_file_registers_through_the_hook_only()
    test_node_behaviour()
    print('Zorp poses smoke OK')


if __name__ == '__main__':
    main()
