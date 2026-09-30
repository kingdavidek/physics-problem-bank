"""Zorp gallery snapshot (E8 dev tool; NOT a smoke test).

Renders `/styleguide#zorp-gallery` in headless Chromium and writes review images to
`data/zorp_gallery/<label>/` (gitignored):

* `faces.png` (full motion) and `faces-reduced.png` (prefers-reduced-motion): one
  contact sheet each, rows light-56 / light-128 / dark-56 / dark-128, one column per legacy face;
* `expressions.png` (Phase 1+): every preset in the gallery, same rows, in blocks of seven;
* `faces-parity.png` (with `--compare`): the compared snapshot on top, this one below, for the
  legacy faces at 128 px in light and dark;
* `matrix.png` / `matrix-dark.png` (Phase 2+): the eyes x mouths channel matrix from the styleguide;
* `fx-filmstrips.png` (Phase 2+): one row per preset whose fx animate in full motion, five frames
  (0/25/50/75/100% of the animation) then the reduced-motion still, side by side;
* `views.png` (Phase 3+): the styleguide views grid (5 views x 2 facings at 56 and 160 px), light and dark;
* `turn-filmstrip.png` (Phase 3+): ten frames of the pinch-turn front -> side -> front, taken from
  the bound demo by pausing every animation and stepping currentTime (full motion, light), then a
  reduced-motion row of stills (turn not required stays front, required swaps instantly, side-point);
* `poses.png` (Phase 4+): the styleguide pose library (every pose at 56 and 160 px, front and, where a pose has a
  default view, that view), light and dark;
* `poses-silhouette.png` (Phase 4+): the same grid with the gallery's silhouette toggle on (one flat colour);
* `clip-filmstrips.png` (Phase 4+): ten frames of fist-pump and each Phase 4 clip (160 px, with the 56 px mascot under each frame), taken in real time at a tenth of
  the speed, full motion on the left and the reduced-motion end state on the right;
* `cells/<scheme>-<motion>-<size>-<face>.png`: every gallery cell on its own;
* `manifest.json`: label, time, URL, viewport, versions, files, per-cell visible face
  groups and console errors.

Usage:
    python scripts/zorp_gallery_snapshot.py --label baseline
    python scripts/zorp_gallery_snapshot.py --label after --compare baseline

Container recipe (Playwright + Pillow live in `python`, the app runs on 3.12):
    python scripts/zorp_gallery_snapshot.py --label baseline --server-python .venv312/bin/python

The app is started as a child process (`--serve`, an internal flag) using
`--server-python` (or `PB_GALLERY_SERVER_PYTHON`, default: this interpreter) with
`PB_TESTING=1` on a random localhost port and a throwaway database. This interpreter only
needs Playwright and Pillow. Both are optional dev dependencies that are never added to
requirements.txt: without them, or without a Chromium build, the tool prints a message
and exits 0.

Pixel comparisons (`--compare`) look at the mascot box only (found in each cell image from the
non-background pixels beside the `svg.buddy-mascot` box the manifest records), then align the two
crops on that bounding box and allow a 3 px shift. They report changed pixel counts per cell.
Only meaningful on the same machine and Chromium build. Look sheets are still to come (`--looks`).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / 'data' / 'zorp_gallery'

GALLERY_FACES = ('nudge', 'milestone', 'celebrate', 'qotd_nudge', 'streak_risk',
                 'weak_topic', 'friend_challenge', 'sleep')  # the legacy names, in baseline order
# E8 Phase 1: faces whose art changed on purpose are reported but never counted as failures.
PARITY_EXEMPT = {'streak_risk': 'D4: frown replaced by the upbeat heads-up look',
                 'sleep': 'baseline drew a blank face; now drawn'}
BLOCK = 7  # faces per block on the expressions sheet
SIZES = (56, 128)
VARIANTS = (('light', 'full'), ('dark', 'full'), ('light', 'reduced'), ('dark', 'reduced'))
VIEWPORT = {'width': 1024, 'height': 900}
DEVICE_SCALE_FACTOR = 2
# Must start with an alphanumeric: '.', '..' and '...' would otherwise resolve to
# data/zorp_gallery or data/ itself, and the tool deletes the output dir it writes to.
LABEL_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$')
DIFF_THRESHOLD = 16  # largest per-channel difference that counts as a changed pixel
OVER_PCT = 0.15  # legacy faces must be ~0 changed pixels inside the mascot box (Phase 2, was 0.5 on the whole cell)
FRAMES = (0.0, 0.25, 0.5, 0.75, 1.0)  # fx filmstrip sample points
TURN_FRAMES = (0.1, 0.3, 0.5, 0.7, 0.9)  # per leg of the turn filmstrip (front->side, then side->front)
VIEW_SIZES = (56, 160)


def serve():
    """Child process: run the app on a random localhost port and print the port."""
    os.environ['PB_TESTING'] = '1'
    os.environ.setdefault('PB_STYLEGUIDE', '1')
    os.environ.setdefault('MAIL_PROVIDER', 'console')
    os.environ.setdefault('CORS_ORIGINS', 'https://app.example.com')
    sys.path.insert(0, str(ROOT))
    from werkzeug.serving import make_server

    from app import app

    srv = make_server('127.0.0.1', 0, app, threaded=True)
    print(f'PB_GALLERY_PORT={srv.server_port}', flush=True)
    srv.serve_forever()


def _label(value):
    if not LABEL_RE.match(value):
        raise argparse.ArgumentTypeError('label must match ^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$')
    return value


def _out_dir(label):
    """Resolve OUT_ROOT/label and refuse anything that isn't a direct child of OUT_ROOT."""
    root = OUT_ROOT.resolve()
    out = (OUT_ROOT / label).resolve()
    if out.parent != root:
        raise SystemExit(f'zorp_gallery_snapshot: refusing label {label!r} (resolves outside {root}).')
    return out


def _font(size):
    from PIL import ImageFont

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _build_sheet(out, label, motion, records, faces=GALLERY_FACES, name=None, block=None):
    """records: {(scheme, size, face): Path}. Write faces.png / faces-reduced.png (or `name`).

    `faces` are the columns; with `block` set they are split into stacked blocks of that many
    columns, each with its own header and the four light/dark rows."""
    from PIL import Image, ImageDraw

    rows = [(scheme, size) for scheme in ('light', 'dark') for size in SIZES]
    title_font, label_font = _font(28), _font(22)
    images = {}
    for key, path in records.items():
        images[key] = Image.open(path).convert('RGBA')
    pad, header_h, title_h = 24, 64, 64
    label_w = 190
    blocks = [faces[i:i + block] for i in range(0, len(faces), block)] if block else [faces]
    col_w = max(max(im.width for im in images.values()), 120) + pad
    ncols = max(len(b) for b in blocks)
    layouts = []
    for chunk in blocks:
        heights = [max(images[(scheme, size, f)].height for f in chunk) + pad for scheme, size in rows]
        layouts.append((chunk, heights))
    width = label_w + col_w * ncols + pad
    height = title_h + sum(header_h + sum(h) for _, h in layouts) + pad
    sheet = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    kind = 'faces' if name is None else name.replace('.png', '')
    draw.text((pad, 16), f'Zorp gallery · {label} · {kind} ({motion})', fill=(20, 20, 20, 255), font=title_font)
    y = title_h
    for chunk, row_heights in layouts:
        for ci, face in enumerate(chunk):
            tw = draw.textlength(face, font=label_font)
            draw.text((label_w + ci * col_w + (col_w - tw) / 2, y + 14), face,
                      fill=(60, 60, 60, 255), font=label_font)
        y += header_h
        for (scheme, size), row_h in zip(rows, row_heights):
            # Give the dark rows a dark backing strip so the row reads as a dark-theme row.
            sample = images[(scheme, size, chunk[0])]
            bg = sample.getpixel((2, 2))
            draw.rectangle([0, y - pad // 2, width, y - pad // 2 + row_h], fill=bg)
            text_fill = (245, 245, 245, 255) if scheme == 'dark' else (20, 20, 20, 255)
            draw.text((pad, y + 8), f'{scheme} {size}px', fill=text_fill, font=label_font)
            for ci, face in enumerate(chunk):
                im = images[(scheme, size, face)]
                x = label_w + ci * col_w + (col_w - im.width) // 2
                sheet.alpha_composite(im, (x, y + (row_h - pad - im.height) // 2))
            y += row_h
    name = name or ('faces.png' if motion == 'full' else 'faces-reduced.png')
    sheet.convert('RGB').save(out / name)
    return name


def _build_parity(label, other):
    """faces-parity.png: `other` (before) above `label` (after), legacy faces, 128 px, light and dark."""
    from PIL import Image, ImageDraw

    a_dir, b_dir = _out_dir(label) / 'cells', _out_dir(other) / 'cells'
    font, small = _font(22), _font(28)
    cells = {}
    for tag, d in ((other, b_dir), (label, a_dir)):
        for scheme in ('light', 'dark'):
            for face in GALLERY_FACES:
                path = d / f'{scheme}-full-128-{face}.png'
                if path.is_file():
                    cells[(tag, scheme, face)] = Image.open(path).convert('RGBA')
    if not cells:
        return None
    pad, label_w = 24, 190
    cw = max(im.width for im in cells.values()) + pad
    ch = max(im.height for im in cells.values()) + pad
    rows = [(scheme, tag) for scheme in ('light', 'dark') for tag in (other, label)]
    sheet = Image.new('RGBA', (label_w + cw * len(GALLERY_FACES) + pad, 64 + 40 + ch * len(rows) + pad),
                      (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 16), f'Zorp parity · {other} (top) vs {label} (bottom) · 128 px', fill=(20, 20, 20, 255), font=small)
    for ci, face in enumerate(GALLERY_FACES):
        tw = draw.textlength(face, font=font)
        draw.text((label_w + ci * cw + (cw - tw) / 2, 64 + 6), face, fill=(60, 60, 60, 255), font=font)
    for ri, (scheme, tag) in enumerate(rows):
        y = 64 + 40 + ri * ch
        sample = next((cells[(tag, scheme, f)] for f in GALLERY_FACES if (tag, scheme, f) in cells), None)
        if sample is not None:
            draw.rectangle([0, y - pad // 2, sheet.width, y - pad // 2 + ch], fill=sample.getpixel((2, 2)))
        fill = (245, 245, 245, 255) if scheme == 'dark' else (20, 20, 20, 255)
        draw.text((pad, y + 8), f'{scheme} {tag}', fill=fill, font=font)
        for ci, face in enumerate(GALLERY_FACES):
            im = cells.get((tag, scheme, face))
            if im is not None:
                sheet.alpha_composite(im, (label_w + ci * cw + (cw - im.width) // 2, y))
    out = _out_dir(label) / 'faces-parity.png'
    sheet.convert('RGB').save(out)
    return out


def _changed(ca, cb):
    """Number of pixels whose largest channel difference exceeds DIFF_THRESHOLD."""
    from PIL import ImageChops

    r, g, b, a = ImageChops.difference(ca, cb).split()
    worst = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(b, a))
    return worst.point(lambda v: 255 if v > DIFF_THRESHOLD else 0).histogram()[255]


def _mascot_bbox(img, y0, y1):
    """Bounding box (device px) of the non-background pixels in rows y0..y1 of a cell image.

    The gallery cell's background is the pixel at (2, 2); the rows are the ones the manifest says
    the svg occupies (padded a little), so the caption below never counts."""
    from PIL import Image, ImageChops

    y0, y1 = max(0, y0), min(img.height, y1)
    band = img.crop((0, y0, img.width, y1))
    bg = Image.new('RGBA', band.size, img.getpixel((2, 2)))
    r, g, b, a = ImageChops.difference(band, bg).split()
    worst = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(b, a))
    box = worst.point(lambda v: 255 if v > DIFF_THRESHOLD else 0).getbbox()
    if not box:
        return None
    return (box[0], box[1] + y0, box[2], box[3] + y0)


def _mascot_pct(ia, ib, box_a, reach=3):
    """(changed pixels, area) inside the mascot box after aligning both crops on their own
    non-background bounding boxes (best of a small +-reach px shift)."""
    from PIL import Image

    pad = 6  # device px of context around the drawn mascot
    y0, y1 = box_a
    ba = _mascot_bbox(ia, y0, y1)
    bb = _mascot_bbox(ib, y0 - 24, y1 + 4)
    if not ba or not bb:
        return None
    # The crop covers the larger of the two boxes, so a part that went missing (or appeared) at
    # the mascot's right or bottom edge is still inside the compared area (review 2026-09-29).
    w = max(ba[2] - ba[0], bb[2] - bb[0]) + 2 * pad
    h = max(ba[3] - ba[1], bb[3] - bb[1]) + 2 * pad
    crop_a = ia.crop((ba[0] - pad, ba[1] - pad, ba[0] - pad + w, ba[1] - pad + h))
    best = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            x, y = bb[0] - pad + dx, bb[1] - pad + dy
            crop_b = ib.crop((x, y, x + w, y + h))
            changed = _changed(crop_a, crop_b)
            if best is None or changed < best[0]:
                best = (changed, w * h, (bb[2] - bb[0]) - (ba[2] - ba[0]), (bb[3] - bb[1]) - (ba[3] - ba[1]))
    return best


def compare(label, other):
    """Regression check between two snapshot directories, mascot box only. Always exit 0."""
    from PIL import Image

    a_dir, b_dir = _out_dir(label) / 'cells', _out_dir(other) / 'cells'
    if not a_dir.is_dir() or not b_dir.is_dir():
        print(f'compare: missing cells directory ({a_dir} or {b_dir}); nothing to compare.')
        return
    try:
        boxes = {c['file']: c for c in json.loads((_out_dir(label) / 'manifest.json').read_text('utf-8'))['cells']}
    except (OSError, ValueError, KeyError):
        boxes = {}
    scale = DEVICE_SCALE_FACTOR
    lines = ['cell  changed_px/mascot_px  pct  (bbox size delta w,h in device px)']
    for name in sorted(p.name for p in b_dir.glob('*.png') if not (a_dir / p.name).is_file()):
        lines.append(f'{name}  MISSING in {label}  OVER')
    for path in sorted(a_dir.glob('*.png')):
        twin = b_dir / path.name
        if not twin.is_file():
            lines.append(f'{path.name}  NEW in {label} (no {other} cell)')
            continue
        meta = boxes.get(f'cells/{path.name}')
        if not meta or 'box' not in meta:
            lines.append(f'{path.name}  no mascot box in the {label} manifest  OVER')
            continue
        _, by, _, bh = meta['box']
        ia, ib = Image.open(path).convert('RGBA'), Image.open(twin).convert('RGBA')
        res = _mascot_pct(ia, ib, (int(by * scale) - 8, int((by + bh) * scale) + 8))
        face = path.stem.split('-', 3)[-1]
        if res is None:
            lines.append(f'{path.name}  mascot not found  OVER')
            continue
        changed, area, dw, dh = res
        pct = 100.0 * changed / area
        text = f'{path.name}  {changed}/{area}  {pct:.2f}%  (bbox {dw:+d},{dh:+d})'
        if face in PARITY_EXEMPT:
            lines.append(f'{text}  EXEMPT ({PARITY_EXEMPT[face]})')
        elif face in GALLERY_FACES:
            lines.append(text + ('  OVER' if pct > OVER_PCT else ''))
        else:
            lines.append(f'{text}  (new preset, informational)')
    report = '\n'.join(lines)
    print(report)
    (_out_dir(label) / f'compare-{other}.txt').write_text(report + '\n', encoding='utf-8')
    legacy = [ln for ln in lines[1:] if ln.split('  ')[0].split('-', 3)[-1][:-4] in GALLERY_FACES]
    over = sum(1 for line in legacy if line.endswith('OVER'))
    print(f'compare: {len(legacy)} legacy cells compared inside the mascot box, {over} over {OVER_PCT}%.')


def _build_filmstrips(out, label, strips):
    """fx-filmstrips.png. strips: {face: ([full frame paths], reduced path)}."""
    from PIL import Image, ImageDraw

    if not strips:
        return None
    font, small = _font(22), _font(28)
    names = list(strips)
    first = Image.open(strips[names[0]][0][0])
    fw, fh = first.width, first.height
    pad, label_w, gap = 16, 190, 40
    cols = len(FRAMES) + 1
    width = label_w + cols * (fw + pad) + gap + pad
    head_h = 96
    sheet = Image.new('RGB', (width, head_h + len(names) * (fh + pad) + pad), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 14), f'Zorp fx filmstrips · {label} · 128 px · full motion frames vs reduced motion (static)',
              fill=(20, 20, 20), font=small)
    for i, f in enumerate(FRAMES):
        x = label_w + i * (fw + pad)
        draw.text((x + 8, head_h - 36), f'{int(f * 100)}%', fill=(60, 60, 60), font=font)
    draw.text((label_w + len(FRAMES) * (fw + pad) + gap, head_h - 36), 'reduced', fill=(60, 60, 60), font=font)
    for r, face in enumerate(names):
        y = head_h + r * (fh + pad)
        draw.text((pad, y + fh // 2 - 10), face, fill=(20, 20, 20), font=font)
        frames, reduced = strips[face]
        for i, path in enumerate(frames):
            sheet.paste(Image.open(path).convert('RGB'), (label_w + i * (fw + pad), y))
        sheet.paste(Image.open(reduced).convert('RGB'), (label_w + len(FRAMES) * (fw + pad) + gap, y))
    sheet.save(out / 'fx-filmstrips.png')
    return 'fx-filmstrips.png'


def _film(cell, out, motion, face, strips):
    """Filmstrip frames for one 128 px light cell. Full motion: restart the fx animations by
    re-inserting the fx nodes, pause them, and step every animation to 0/25/50/75/100% of its
    iteration. Reduced motion: one still of the same mascot (nothing animates)."""
    host = cell.locator('[data-buddy-face]')
    if motion == 'reduced':
        if face in strips:
            path = out / 'fx' / f'{face}-reduced.png'
            host.screenshot(path=str(path), animations='allow', caret='hide')
            strips[face] = (strips[face][0], path)
        return
    n = cell.evaluate(
        "el => { el.querySelectorAll('[class*=\"zorp-slot--fx\"]').forEach(s => s.replaceChildren(...s.childNodes));"
        " const a = el.getAnimations({subtree: true}); a.forEach(x => x.pause()); return a.length; }")
    if not n:
        return
    frames = []
    for i, f in enumerate(FRAMES):
        cell.evaluate(
            "(el, f) => el.getAnimations({subtree: true}).forEach(a => { const t = a.effect.getComputedTiming();"
            " a.currentTime = (t.delay || 0) + f * 0.999 * t.duration; })", f)
        path = out / 'fx' / f'{face}-{i}.png'
        host.screenshot(path=str(path), animations='allow', caret='hide')
        frames.append(path)
    strips[face] = (frames, None)


def _build_views(out, label, shots):
    """views.png. shots: [(scheme, size, facing, Path)] row screenshots of the styleguide views grid."""
    from PIL import Image, ImageDraw

    if not shots:
        return None
    font, small = _font(22), _font(28)
    images = [(scheme, size, facing, Image.open(path).convert('RGB')) for scheme, size, facing, path in shots]
    pad, label_w = 16, 190
    width = label_w + max(im.width for *_, im in images) + pad
    height = 64 + sum(im.height + pad for *_, im in images)
    sheet = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 16), f'Zorp views · {label} · front, three-quarter, side, back, back-glance', fill=(20, 20, 20), font=small)
    y = 64
    for scheme, size, facing, im in images:
        draw.rectangle([0, y - pad // 2, width, y - pad // 2 + im.height + pad], fill=im.getpixel((2, 2)))
        draw.text((pad, y + 8), f'{scheme} {size}px', fill=(245, 245, 245) if scheme == 'dark' else (20, 20, 20), font=font)
        draw.text((pad, y + 36), 'facing left' if facing == 'l' else 'facing right', fill=(140, 140, 140), font=font)
        sheet.paste(im, (label_w, y))
        y += im.height + pad
    sheet.save(out / 'views.png')
    return 'views.png'


_TURN_STEP = """async ([f]) => { const el = document.getElementById('sg-zorp-views-demo');
  const an = el.getAnimations({subtree: true}); an.forEach(a => a.pause());
  const total = Math.max(...an.map(a => { const t = a.effect.getComputedTiming(); return (t.delay || 0) + t.duration; }));
  for (const a of an) { const t = a.effect.getComputedTiming(); const end = (t.delay || 0) + t.duration;
    if (f * total >= end) a.finish(); else a.currentTime = f * total; }
  await new Promise(r => setTimeout(r, 30)); return an.length; }"""


def _turn_filmstrip(page):
    """Ten full-motion frames, front -> side (five), side -> front (five), from the bound demo."""
    import io
    from PIL import Image

    el = page.locator('#sg-zorp-views-demo')
    if not el.count():
        return None
    el.scroll_into_view_if_needed()
    frames = []
    for view in ('side', 'front'):
        page.evaluate("([v]) => { const el = document.getElementById('sg-zorp-views-demo'); window.pbZorp.bind(el);"
                      " window.pbZorp.idle(false, el); window.__turn = window.pbZorp.turn(v, 'r', {el}); }", [view])
        for f in TURN_FRAMES:
            page.evaluate(_TURN_STEP, [f])
            frames.append(Image.open(io.BytesIO(el.screenshot(animations='allow', caret='hide'))).convert('RGB'))
        page.evaluate("async () => { document.getElementById('sg-zorp-views-demo').getAnimations({subtree: true})"
                      ".forEach(a => a.finish()); await window.__turn; }")
    return frames


# Reduced motion (plan 2 #5): turn() without `required` stays front, with it the view swaps instantly,
# side-point holds the side view; each state is a still.
_REDUCED_TURN_STEPS = (
    ('start', "() => true"),
    ('turn side', "(el) => window.pbZorp.turn('side', 'r', {el})"),
    ('turn side, required', "(el) => window.pbZorp.turn('side', 'r', {el, required: true})"),
    ('turn front', "(el) => window.pbZorp.turn('front', 'r', {el})"),
    ('side-point (hold)', "(el) => { window.pbZorp.play('side-point', {el}); return true; }"),
)


def _reduced_turn_frames(page):
    import io
    from PIL import Image

    el = page.locator('#sg-zorp-views-demo')
    if not el.count():
        return None
    el.scroll_into_view_if_needed()
    page.evaluate("() => { const el = document.getElementById('sg-zorp-views-demo'); window.pbZorp.bind(el);"
                  " window.pbZorp.idle(false, el); }")
    frames = []
    for _name, js in _REDUCED_TURN_STEPS:
        page.evaluate(f"async () => {{ const el = document.getElementById('sg-zorp-views-demo'); await ({js})(el); }}")
        frames.append(Image.open(io.BytesIO(el.screenshot(animations='disabled', caret='hide'))).convert('RGB'))
    return frames


def _build_turn_filmstrip(out, label, frames, reduced):
    """turn-filmstrip.png: full-motion frames (two rows) and, when captured, a reduced-motion row."""
    from PIL import Image, ImageDraw

    if not frames:
        return None
    fw, fh = frames[0].size
    head, gap = 64, 48
    rows = 2 + (1 if reduced else 0)
    sheet = Image.new('RGB', (fw * 5, head + fh * rows + (gap if reduced else 0)), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 16), f'Zorp turn · {label} · front -> side (top), side -> front (middle), frames at 10/30/50/70/90%',
              fill=(20, 20, 20), font=_font(28))
    for i, im in enumerate(frames):
        sheet.paste(im, ((i % 5) * fw, head + (i // 5) * fh))
    if reduced:
        y = head + fh * 2
        draw.text((16, y + 8), 'reduced motion: ' + ' | '.join(n for n, _ in _REDUCED_TURN_STEPS),
                  fill=(20, 20, 20), font=_font(24))
        for i, im in enumerate(reduced[:5]):
            sheet.paste(im.resize((fw, fh)) if im.size != (fw, fh) else im, (i * fw, y + gap))
    sheet.save(out / 'turn-filmstrip.png')
    return 'turn-filmstrip.png'


POSE_CLIPS = ('fist-pump', 'victory', 'flex', 'shrug', 'bow', 'think-chin', 'dance', 'float', 'oops-encourage', 'turn')
CLIP_FRAMES = 10
CLIP_SPEED = 0.1
_CLIP_DEMO = "document.getElementById('sg-zorp-poselib-demo')"


def _pose_clip_frames(page, out, motion):
    """Real-time frames of each Phase 4 clip on the pose-library demo. Pausing WAAPI would leave the
    expression timers running, so the clips are played at a tenth of the speed and shot as they go.
    Full motion: CLIP_FRAMES frames per clip. Reduced: the single settled frame. -> {clip: [paths]}"""
    demo = page.locator('#sg-zorp-poselib-demo svg.buddy-mascot')
    small = page.locator('#sg-zorp-poselib-demo-small svg.buddy-mascot')
    demo.scroll_into_view_if_needed()
    page.evaluate("window.scrollBy({top: -320, behavior: 'instant'})")   # room above the mascot for the jump
    page.wait_for_timeout(300)

    def box_of(loc):
        box = loc.bounding_box()
        pad = box['width'] * 0.15
        top = box['width'] * 0.6   # room for the jump
        return {'x': max(0, box['x'] - pad), 'y': max(0, box['y'] - top), 'width': box['width'] + 2 * pad, 'height': box['height'] + top + pad * 0.3}

    clip_box, small_box = box_of(demo), box_of(small)
    (out / 'clips').mkdir(exist_ok=True)
    result = {}
    for name in POSE_CLIPS:
        page.evaluate(f"() => {{ for (const id of ['sg-zorp-poselib-demo', 'sg-zorp-poselib-demo-small']) {{ const el = document.getElementById(id); window.pbZorp.bind(el); window.pbZorp.idle(false, el); }} }}")
        info = page.evaluate("(c) => window.pbZorp.clipInfo(c)", name) or {}
        dur = info.get('dur') or 1200
        paths = []
        if motion == 'full':
            page.evaluate("([c, s]) => { window.__t0 = performance.now(); for (const id of ['sg-zorp-poselib-demo', 'sg-zorp-poselib-demo-small'])"
                          " window.pbZorp.play(c, {el: document.getElementById(id), speed: s}); }", [name, CLIP_SPEED])
            for i in range(CLIP_FRAMES):
                target = i / (CLIP_FRAMES - 1) * 0.97 * dur / CLIP_SPEED
                page.evaluate("(t) => new Promise(r => { const w = () => performance.now() - window.__t0 >= t ? r() : setTimeout(w, 4); w(); })", target)
                path = out / 'clips' / f'{name}-{i}.png'
                path.write_bytes(page.screenshot(clip=clip_box, animations='allow'))
                paths.append(path)
                spath = out / 'clips' / f'{name}-{i}-s.png'
                spath.write_bytes(page.screenshot(clip=small_box, animations='allow'))
            page.wait_for_timeout(int(dur / CLIP_SPEED * 0.1) + 300)
        else:
            page.evaluate(f"(c) => window.pbZorp.play(c, {{el: {_CLIP_DEMO}}})", name)
            page.wait_for_timeout(int(dur) + 700)
            path = out / 'clips' / f'{name}-reduced.png'
            path.write_bytes(page.screenshot(clip=clip_box, animations='allow'))
            paths.append(path)
        result[name] = paths
    return result


def _build_clip_filmstrips(out, label, full, reduced):
    """clip-filmstrips.png: one row per clip, CLIP_FRAMES full-motion frames, then the reduced frame."""
    from PIL import Image, ImageDraw

    rows = [(n, full[n], reduced[n][0]) for n in POSE_CLIPS if len(full.get(n, ())) == CLIP_FRAMES and reduced.get(n)]
    if not rows:
        return None
    ims = {n: [Image.open(f).convert('RGB') for f in fr] for n, fr, _ in rows}
    smalls = {n: [Image.open(f.with_name(f.stem + '-s.png')).convert('RGB') for f in fr] for n, fr, _ in rows}
    fw, fh = ims[rows[0][0]][0].size
    scale = 0.5
    tw, th0 = int(fw * scale), int(fh * scale)
    sh = int(smalls[rows[0][0]][0].height * scale)
    th = th0 + sh
    font, small = _font(22), _font(28)
    pad, label_w, gap = 8, 190, 40
    width = label_w + CLIP_FRAMES * (tw + pad) + gap + tw + pad
    head_h = 64
    sheet = Image.new('RGB', (width, head_h + len(rows) * (th + pad)), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 14), f'Zorp clips · {label} · frames 0-100% of each clip (left, full motion) vs reduced motion (right)',
              fill=(20, 20, 20), font=small)
    for r, (name, _, red) in enumerate(rows):
        y = head_h + r * (th + pad)
        draw.text((pad, y + th // 2 - 12), name, fill=(20, 20, 20), font=font)
        for i, im in enumerate(ims[name]):
            sheet.paste(im.resize((tw, th0), Image.LANCZOS), (label_w + i * (tw + pad), y))
            sm = smalls[name][i]
            sheet.paste(sm.resize((int(sm.width * scale), sh), Image.LANCZOS), (label_w + i * (tw + pad), y + th0))
        sheet.paste(Image.open(red).convert('RGB').resize((tw, th0), Image.LANCZOS), (label_w + CLIP_FRAMES * (tw + pad) + gap, y))
    sheet.save(out / 'clip-filmstrips.png')
    return 'clip-filmstrips.png'


def _pose_cells(page, out, scheme, tag):
    """Screenshot each pose cell of the styleguide grid on its own (no row compositing). -> {size: [Path]}"""
    got = {}
    for size in (56, 160):
        got[size] = []
        cells = page.locator(f'#sg-zorp-poses-{size} [data-zorp-pose-cell]')
        for i in range(cells.count()):
            cell = cells.nth(i)
            cell.scroll_into_view_if_needed()
            path = out / 'cells' / f'{tag}-{scheme}-{size}-{i:02d}.png'
            cell.screenshot(path=str(path), animations='disabled', caret='hide')
            got[size].append(path)
    return got


def _build_poses(out, label, shots, name='poses.png', kind='every pose, front and default view, 56 and 160 px'):
    """poses.png. shots: {scheme: {size: [Path]}} cell screenshots, laid out in a grid per scheme and size."""
    from PIL import Image, ImageDraw

    if not shots:
        return None
    font, small = _font(22), _font(28)
    per_row = {56: 9, 160: 6}
    pad, label_w, head = 12, 190, 64
    blocks = []
    for scheme, by_size in shots.items():
        for size, paths in by_size.items():
            ims = [Image.open(p).convert('RGB') for p in paths]
            if not ims:
                continue
            cw, ch = max(i.width for i in ims), max(i.height for i in ims)
            n = per_row[size]
            rows = -(-len(ims) // n)
            blocks.append((scheme, size, ims, cw, ch, n, rows))
    width = label_w + max(b[3] * b[5] for b in blocks) + pad
    height = head + sum(b[4] * b[6] + pad * 2 for b in blocks)
    sheet = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 16), f'Zorp poses · {label} · {kind}', fill=(20, 20, 20), font=small)
    y = head
    for scheme, size, ims, cw, ch, n, rows in blocks:
        band = ims[0].getpixel((1, 1)) if scheme == 'dark' else (255, 255, 255)
        draw.rectangle([0, y - pad, width, y + ch * rows + pad], fill=band)
        draw.text((pad, y + 8), f'{scheme} {size}px', fill=(245, 245, 245) if scheme == 'dark' else (20, 20, 20), font=font)
        for i, im in enumerate(ims):
            sheet.paste(im, (label_w + (i % n) * cw, y + (i // n) * ch))
        y += ch * rows + pad * 2
    sheet.save(out / name)
    return name


def snapshot(label, server_python):
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
        from PIL import Image  # noqa: F401
    except ImportError:
        print('zorp_gallery_snapshot: Playwright/Pillow not installed in this interpreter; skipping (dev tool, not required).')
        return 0

    tmp = Path(tempfile.mkdtemp(prefix='pb_gallery_'))
    proc = None
    log_handle = None
    try:
        log_path = tmp / 'server.log'
        log_handle = open(log_path, 'w', encoding='utf-8')
        proc = subprocess.Popen(
            [server_python, str(Path(__file__).resolve()), '--serve'],
            env={**os.environ, 'PB_TESTING': '1', 'PB_DB_PATH': str(tmp / 'gallery.db')},
            stdout=subprocess.PIPE, stderr=log_handle, text=True, cwd=str(ROOT),
        )
        timer = threading.Timer(60, proc.kill)
        timer.start()
        port = None
        try:
            for line in proc.stdout:
                if line.startswith('PB_GALLERY_PORT='):
                    port = int(line.split('=', 1)[1])
                    break
        finally:
            timer.cancel()
        if port is None:
            log_handle.flush()
            tail = log_path.read_text(encoding='utf-8', errors='ignore')[-1500:]
            print(f'zorp_gallery_snapshot: the app server did not start ({server_python}).\n{tail}')
            return 1
        threading.Thread(target=lambda: [None for _ in proc.stdout], daemon=True).start()
        base = f'http://127.0.0.1:{port}'
        url = f'{base}/styleguide#zorp-gallery'

        final_out = _out_dir(label)
        # Write into a sibling staging dir and swap it in only after a complete run, so a
        # skipped/failed/interrupted run never destroys the previous snapshot.
        out = OUT_ROOT.resolve() / f'.{label}.partial'
        if out.exists():
            shutil.rmtree(out)
        (out / 'cells').mkdir(parents=True)

        manifest_cells = []
        console = {}
        files = []
        records = {m: {} for m in ('full', 'reduced')}
        (out / 'fx').mkdir()
        strips = {}
        view_shots = []
        turn_frames = turn_reduced = None
        pose_shots = {}
        sil_shots = {}
        clip_full = clip_reduced = None
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except PlaywrightError:
                print(f'Chromium not available (PLAYWRIGHT_BROWSERS_PATH={os.environ.get("PLAYWRIGHT_BROWSERS_PATH")}); skipping.')
                return 0
            for scheme, motion in VARIANTS:
                ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=DEVICE_SCALE_FACTOR,
                                          service_workers='block')
                page = ctx.new_page()
                errors = []
                page.on('console', lambda msg, errors=errors: errors.append(msg.text) if msg.type == 'error' else None)
                page.on('pageerror', lambda exc, errors=errors: errors.append(f'pageerror: {exc}'))
                page.emulate_media(color_scheme=scheme,
                                   reduced_motion='reduce' if motion == 'reduced' else 'no-preference')
                page.goto(url, wait_until='networkidle')
                page.wait_for_selector('#zorp-gallery [data-zorp-gallery-cell]')
                page.evaluate('document.fonts.ready')
                page.locator('#zorp-gallery').scroll_into_view_if_needed()
                cells = page.locator('#zorp-gallery [data-zorp-gallery-cell]')
                for i in range(cells.count()):
                    cell = cells.nth(i)
                    face = cell.get_attribute('data-gallery-face')
                    size = int(cell.get_attribute('data-gallery-size'))
                    rel = f'cells/{scheme}-{motion}-{size}-{face}.png'
                    cell.screenshot(path=str(out / rel), animations='disabled', caret='hide')
                    visible = cell.evaluate("el => el.querySelectorAll('.zorp-face').length")
                    box = cell.evaluate(
                        "el => { const s = el.querySelector('svg.buddy-mascot'); const c = el.getBoundingClientRect();"
                        " const r = s.getBoundingClientRect(); return [r.left - c.left, r.top - c.top, r.width, r.height]; }")
                    files.append(rel)
                    records[motion][(scheme, size, face)] = out / rel
                    manifest_cells.append({'scheme': scheme, 'motion': motion, 'size': size,
                                           'face': face, 'file': rel, 'zorp_faces': visible, 'box': box})
                    if scheme == 'light' and size == 128:
                        _film(cell, out, motion, face, strips)
                if motion == 'full':
                    matrix = page.locator('#sg-zorp-matrix')
                    if matrix.count():
                        name = 'matrix.png' if scheme == 'light' else 'matrix-dark.png'
                        page.wait_for_selector('#sg-zorp-matrix td')
                        matrix.scroll_into_view_if_needed()
                        matrix.screenshot(path=str(out / name), animations='disabled', caret='hide')
                        files.append(name)
                if motion == 'full':
                    for size in VIEW_SIZES:
                        for facing in ('r', 'l'):
                            row = page.locator(f'#sg-zorp-views-{size}-{facing}')
                            if row.count():
                                row.scroll_into_view_if_needed()
                                path = out / 'cells' / f'views-{scheme}-{size}-{facing}.png'
                                row.screenshot(path=str(path), animations='disabled', caret='hide')
                                view_shots.append((scheme, size, facing, path))
                    if scheme == 'light':
                        turn_frames = _turn_filmstrip(page)
                if motion == 'reduced' and scheme == 'light':
                    turn_reduced = _reduced_turn_frames(page)
                if motion == 'full':
                    # the sticky site header would paint over cell screenshots taken mid-page
                    page.add_style_tag(content='header, .site-header, .site-nav { position: static !important; }')
                    pose_shots[scheme] = _pose_cells(page, out, scheme, 'poses')
                    silhouette = page.locator('[data-zorp-silhouette]')
                    if silhouette.count():
                        silhouette.click()
                        sil_shots[scheme] = _pose_cells(page, out, scheme, 'poses-silhouette')
                        silhouette.click()
                if scheme == 'light' and page.locator('#sg-zorp-poselib-demo').count():
                    got = _pose_clip_frames(page, out, motion)
                    if motion == 'full':
                        clip_full = got
                    else:
                        clip_reduced = got
                console[f'{scheme}-{motion}'] = errors
                ctx.close()
            version = browser.version
            browser.close()
        turn_sheet = _build_turn_filmstrip(out, label, turn_frames, turn_reduced)
        if turn_sheet:
            files.append(turn_sheet)

        seen = []
        for _key in records['full']:
            if _key[2] not in seen:
                seen.append(_key[2])
        for motion in ('full', 'reduced'):
            legacy = {k: v for k, v in records[motion].items() if k[2] in GALLERY_FACES}
            files.append(_build_sheet(out, label, motion, legacy))
        files.append(_build_sheet(out, label, 'full', records['full'], faces=tuple(seen),
                                  name='expressions.png', block=BLOCK))
        for sheet_name in (_build_poses(out, label, pose_shots),
                           _build_poses(out, label, sil_shots, 'poses-silhouette.png',
                                        'silhouettes (one flat colour: the outline alone has to read)'),
                           _build_clip_filmstrips(out, label, clip_full or {}, clip_reduced or {})):
            if sheet_name:
                files.append(sheet_name)
        views_sheet = _build_views(out, label, view_shots)
        if views_sheet:
            files.append(views_sheet)
        strip_sheet = _build_filmstrips(out, label, {f: v for f, v in strips.items() if len(v[0]) == len(FRAMES) and v[1]})
        if strip_sheet:
            files.append(strip_sheet)
        try:
            from importlib.metadata import version as pkg_version
            pw_version = pkg_version('playwright')
        except Exception:
            pw_version = 'unknown'
        manifest = {
            'label': label,
            'generated_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'url': url,
            'viewport': VIEWPORT,
            'device_scale_factor': DEVICE_SCALE_FACTOR,
            'playwright': pw_version,
            'browser': {'name': 'chromium', 'version': version},
            'files': sorted(files),
            'cells': manifest_cells,
            'console_errors': console,
        }
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        if final_out.exists():
            shutil.rmtree(final_out)
        out.rename(final_out)
        print(f'Wrote {final_out}')
        print(f'  sheets: {final_out / "faces.png"}, {final_out / "faces-reduced.png"}, {final_out / "expressions.png"}, matrix.png, fx-filmstrips.png, views.png, turn-filmstrip.png, poses.png, poses-silhouette.png, clip-filmstrips.png')
        print(f'  cells:  {len(manifest_cells)} PNGs in {final_out / "cells"}')
        print(f'  manifest: {final_out / "manifest.json"}')
        return 0
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                proc.kill()
        if log_handle is not None:
            log_handle.close()
        shutil.rmtree(tmp, ignore_errors=True)
        partial = OUT_ROOT.resolve() / f'.{label}.partial'
        if partial.exists():
            shutil.rmtree(partial, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    ap.add_argument('--label', type=_label, default='baseline')
    ap.add_argument('--compare', type=_label, metavar='OTHER', help='compare this label with OTHER after snapshotting')
    ap.add_argument('--server-python', default=os.environ.get('PB_GALLERY_SERVER_PYTHON') or sys.executable)
    ap.add_argument('--serve', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--clips', action='store_true', help='filmstrips (Phase 1+)')
    ap.add_argument('--looks', action='store_true', help='look sheets (Phase 1+)')
    args = ap.parse_args(argv)
    if args.serve:
        serve()
        return 0
    if args.clips or args.looks:
        print('--clips/--looks: not built until Phase 1+')
    rc = snapshot(args.label, args.server_python)
    if rc == 0 and args.compare:
        try:
            compare(args.label, args.compare)
            parity = _build_parity(args.label, args.compare)
            if parity:
                print(f'  parity sheet: {parity}')
        except ImportError:
            pass
    return rc


if __name__ == '__main__':
    sys.exit(main())
