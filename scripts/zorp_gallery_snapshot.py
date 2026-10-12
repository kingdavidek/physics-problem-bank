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
* `--clips` (E9): the same `clip-filmstrips.png`, but for the E9 set (cheer, hop, fist-pump, victory, flex, dance), shot
  with motion forced to full (the run stops with an error if `pbZorp.motionLevel()` is not `full`, so a sheet of
  reduced-motion stills can never pass for motion);
* `--copy` (E9): `copy-guide.png`, every Guide line in its panel at 375 px, light and dark, taken on `/guide-preview`
  by pressing Continue through the origin story, the five tours and the rewards (tour highlights are removed in the page
  first, because a tour skips steps whose target is not on the preview page; nothing is saved), plus `copy-guide.json`;
* `--talk` (E9 Phase 1): `talk-filmstrip.png` / `talk-filmstrip-dark.png` (one Guide line spoken, a frame every 60 ms of
  the talk plan, face crop at 160 px and the whole Zorp at 56 px, front and side) and `talk-mouths.png` /
  `talk-mouths-dark.png` (the closed, half-open and open frames over several expressions, front 160, side 160 and front
  56 px). Frames are taken by pausing the talk animations and stepping `currentTime`, so they are exact; the run
  stops with an error if the motion level is not `full`. `--talk-only` does just that, without the gallery;
* `--soft` (E9 Phase 2): the soft body sheets, light and dark, from a stage of live Zorps the tool builds in the styleguide page:
  `soft-ab-filmstrips[-dark].png` (160 px) and `soft-ab-filmstrips-56[-dark].png` (56 px): for hop, cheer, fist-pump, victory,
  dance and flex, an E8 row (soft layer off; for cheer and hop the legacy track clips, from a page with zorp-poses.js blocked)
  above an E9 row, 12 frames, front and side; `soft-landing[-dark].png` (the hop landing close-up every 20 ms of clip time, with
  the body scale curve); `soft-silhouette[-dark].png` (flat-colour outlines of the take-off stretch and the landing squash, on and off);
  `belly-ab[-dark].png` (D4: no belly, the plan's belly and a wider belly, at 160 px and 56 px, at the landing; the belly is
  prototyped in the page by this tool, never shipped unless the sheet reads at 56 px). Frames are real-time shots at a tenth of
  the speed of mascots that all start in the same tick, so a row pair shows the same instant; the run stops if the motion level is
  not `full`. `--soft-only` does just that, without the gallery;
* `cells/<scheme>-<motion>-<size>-<face>.png`: every gallery cell on its own;
* `manifest.json`: label, time, URL, viewport, versions, files, per-cell visible face
  groups and console errors.

Usage:
    python scripts/zorp_gallery_snapshot.py --label baseline
    python scripts/zorp_gallery_snapshot.py --label after --compare baseline
    python scripts/zorp_gallery_snapshot.py --label e9-baseline --clips --copy
    python scripts/zorp_gallery_snapshot.py --label phase1 --talk-only
    python scripts/zorp_gallery_snapshot.py --label phase2 --soft-only --server-python .venv312/bin/python

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
            # the pose, view and silhouette cells share cells/ but are not face cells and have no manifest box (review 2026-10-04:
            # they were printed as OVER, though the summary never counted them); only a legacy face cell without a box is a failure
            if path.stem.split('-', 3)[-1] in GALLERY_FACES:
                lines.append(f'{path.name}  no mascot box in the {label} manifest  OVER')
            else:
                lines.append(f'{path.name}  not a face cell (no mascot box), skipped')
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
E9_CLIPS = ('cheer', 'hop', 'fist-pump', 'victory', 'flex', 'dance')  # --clips: the clips E9 changes or leans on
LEGACY_CLIP_DUR = {'cheer': 700, 'hop': 450}  # legacy track clips have no clipInfo(); durations from zorp-motion.js
COPY_VIEWPORT = {'width': 375, 'height': 812}
COPY_PER_ROW = 3  # light/dark pairs per row of copy-guide.png
CLIP_FRAMES = 10
CLIP_SPEED = 0.1
_CLIP_DEMO = "document.getElementById('sg-zorp-poselib-demo')"


def _pose_clip_frames(page, out, motion, clips=None):
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
    if motion == 'full' and clips is not None:
        level = page.evaluate('() => window.pbZorp.motionLevel()')
        if level != 'full':
            raise SystemExit(f'zorp_gallery_snapshot: --clips needs full motion but pbZorp.motionLevel() is {level!r}; '
                             'not writing a filmstrip of stills.')
    for name in (clips or POSE_CLIPS):
        page.evaluate(f"() => {{ for (const id of ['sg-zorp-poselib-demo', 'sg-zorp-poselib-demo-small']) {{ const el = document.getElementById(id); window.pbZorp.bind(el); window.pbZorp.idle(false, el); }} }}")
        info = page.evaluate("(c) => window.pbZorp.clipInfo(c)", name) or {}
        dur = info.get('dur') or LEGACY_CLIP_DUR.get(name, 1200)
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


def _build_clip_filmstrips(out, label, full, reduced, clips=None):
    """clip-filmstrips.png: one row per clip, CLIP_FRAMES full-motion frames, then the reduced frame."""
    from PIL import Image, ImageDraw

    rows = [(n, full[n], reduced[n][0]) for n in (clips or POSE_CLIPS) if len(full.get(n, ())) == CLIP_FRAMES and reduced.get(n)]
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


def _reward_specs(catalog):
    """pbGuide.reward() arguments for every reward in the catalog, in catalog order."""
    specs = []
    for key in catalog.get('rewards', {}):
        if key == 'milestone':
            specs.append((key, {'type': 'milestone', 'key': 'first_quiz'}))
        elif key.startswith('streak:'):
            specs.append((key, {'type': 'streak', 'days': int(key.split(':')[1])}))
        else:
            specs.append((key, {'type': key}))
    return specs


def _copy_guide(browser, base, out):
    """Every Guide line in its panel at 375 px, light and dark. -> (captures, missing, errors)
    captures: [{'scheme', 'step', 'line', 'of', 'text', 'chars', 'file'}] in play order."""
    (out / 'copy').mkdir(exist_ok=True)
    captures, errors, missing = [], [], []
    expected = {}
    for scheme in ('light', 'dark'):
        ctx = browser.new_context(viewport=COPY_VIEWPORT, device_scale_factor=DEVICE_SCALE_FACTOR, service_workers='block')
        page = ctx.new_page()
        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        page.on('pageerror', lambda exc: errors.append(f'pageerror: {exc}'))
        page.emulate_media(color_scheme=scheme, reduced_motion='no-preference')
        page.goto(f'{base}/guide-preview', wait_until='networkidle')
        page.wait_for_function('() => window.pbGuide && window.pbGuideCatalog')
        page.evaluate('document.fonts.ready')
        if page.locator('[data-guide-root]:not([hidden])').count():
            page.keyboard.press('Escape')
            page.wait_for_timeout(300)
        # A tour skips steps whose highlight target is missing from this page; the copy does not depend on it.
        page.evaluate("() => { const t = window.pbGuideCatalog.tours; Object.keys(t).forEach(k => t[k].forEach(s => { s.highlight = null; })); }")
        catalog = page.evaluate('() => JSON.parse(JSON.stringify(window.pbGuideCatalog))')
        lookup = {}
        steps = [('origin', st) for st in catalog['origin']]
        steps += [(tour, st) for tour, group in catalog['tours'].items() for st in group]
        steps += [(key, st) for key, st in catalog['rewards'].items()]
        for owner, st in steps:
            sid = st.get('id') or owner
            for n, text in enumerate(st['lines'], 1):
                lookup.setdefault(text, (sid, n, len(st['lines'])))
        expected[scheme] = {t: v for t, v in lookup.items()}
        plays = [('origin', "() => window.pbGuide.play('origin')")]
        plays += [(tour, f"() => window.pbGuide.play('{tour}')") for tour in catalog['tours']]
        plays += [(key, f"() => window.pbGuide.reward({json.dumps(spec)})") for key, spec in _reward_specs(catalog)]
        seen_text = set()
        for owner, call in plays:
            page.evaluate(call)
            page.wait_for_timeout(500)
            for _ in range(12):
                if not page.locator('[data-guide-root]:not([hidden])').count():
                    break
                text = page.locator('#guide-bubble').inner_text().strip()
                sid, n, of = lookup.get(text, (f'{owner}?', 0, 0))
                slug = re.sub(r'[^A-Za-z0-9]+', '-', sid)
                idx = sum(1 for c in captures if c['scheme'] == scheme)
                rel = f'copy/{scheme}-{idx:02d}-{slug}-{n}.png'
                panel = page.locator('.guide-panel')
                panel.screenshot(path=str(out / rel), caret='hide')
                captures.append({'scheme': scheme, 'step': sid, 'line': n, 'of': of, 'text': text, 'chars': len(text), 'file': rel})
                seen_text.add(text)
                page.locator('[data-guide-primary]').click()
                page.wait_for_timeout(450)
            if page.locator('[data-guide-root]:not([hidden])').count():
                page.keyboard.press('Escape')
                page.wait_for_timeout(300)
        missing += [f'{scheme}: {t}' for t in expected[scheme] if t not in seen_text]
        ctx.close()
    return captures, missing, errors


def _build_copy_sheet(out, label, captures):
    """copy-guide.png: one cell per line (light left, dark right), COPY_PER_ROW pairs per row, at half the shot size."""
    from PIL import Image, ImageDraw

    pairs = {}
    order = []
    for c in captures:
        key = (c['step'], c['line'], c['text'])
        if key not in pairs:
            pairs[key] = {}
            order.append(key)
        pairs[key].setdefault(c['scheme'], c)
    if not order:
        return None
    font, small = _font(20), _font(28)
    pad, cap_h, head = 14, 34, 64
    cells = []
    for key in order:
        ims = {s: Image.open(out / c['file']).convert('RGB') for s, c in pairs[key].items()}
        ims = {s: im.resize((im.width // 2, im.height // 2), Image.LANCZOS) for s, im in ims.items()}
        cells.append((key, ims))
    cw = max(im.width for _, ims in cells for im in ims.values())
    ch = max(im.height for _, ims in cells for im in ims.values())
    rows = -(-len(cells) // COPY_PER_ROW)
    pair_w = cw * 2 + pad
    width = COPY_PER_ROW * (pair_w + pad * 2) + pad
    height = head + rows * (ch + cap_h + pad * 2)
    sheet = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 16), f'Zorp Guide copy - {label} - every line in its panel, 375 px wide (light left, dark right)',
              fill=(20, 20, 20), font=small)
    for idx, (key, ims) in enumerate(cells):
        r, k = divmod(idx, COPY_PER_ROW)
        x0 = pad + k * (pair_w + pad * 2)
        y0 = head + r * (ch + cap_h + pad * 2)
        sid, n, text = key
        draw.text((x0, y0), f'{sid}  line {n}  ({len(text)} chars)', fill=(20, 20, 20), font=font)
        for j, scheme in enumerate(('light', 'dark')):
            if scheme in ims:
                sheet.paste(ims[scheme], (x0 + j * (cw + pad), y0 + cap_h))
    sheet.save(out / 'copy-guide.png')
    return 'copy-guide.png'


TALK_LINE = 'A bit about me: I\u2019m Zorp, from Novara, out past the maths belt.'
TALK_STEP_MS = 60
TALK_MAX = 1600
TALK_EXPRESSIONS = ('nudge', 'soft-smile', 'happy', 'proud', 'determined', 'curious', 'thinking', 'confused', 'grin', 'joy',
                    'laugh', 'wow', 'smug', 'bashful', 'sad', 'sleep')
# face crop of the 64 x 64 viewBox (fractions): the plate and mouth, where the talk reads
FACE_CROP = (0.2, 0.36, 0.8, 0.86)
_TALK_FREEZE = """([sel, t]) => { const el = document.querySelector(sel);
  for (const a of document.getAnimations()) { const tg = a.effect && a.effect.target;
    if (tg && el.contains(tg)) { a.pause(); a.currentTime = t; } } }"""
_TALK_START = """([sel, text, max]) => { const z = window.pbZorp; const el = document.querySelector(sel);
  if (!window.__st) { window.__st = window.setTimeout; window.setTimeout = (f, ms, ...r) => ms >= 500 ? 0 : window.__st(f, ms, ...r); }
  z.hush(el); z.talk({el, text, max}); return z.isTalking(el); }"""
_TALK_END = """(sel) => { const z = window.pbZorp; const el = document.querySelector(sel); z.hush(el);
  if (window.__st) { window.setTimeout = window.__st; window.__st = null; } }"""


def _talk_clip(page, sel, face):
    box = page.locator(sel + ' svg.buddy-mascot').bounding_box()
    if not face:
        pad = 4
        return {'x': box['x'] - pad, 'y': box['y'] - pad, 'width': box['width'] + 2 * pad, 'height': box['height'] + 2 * pad}
    x0, y0, x1, y1 = FACE_CROP
    return {'x': box['x'] + box['width'] * x0, 'y': box['y'] + box['height'] * y0,
            'width': box['width'] * (x1 - x0), 'height': box['height'] * (y1 - y0)}


def _talk_shots(page, sel, text, times, face, tag, out):
    """Start a talk on the demo `sel`, freeze it, shoot it at each `times` entry (ms into the plan). -> [Path]"""
    clip = _talk_clip(page, sel, face)
    if not page.evaluate(_TALK_START, [sel, text, TALK_MAX]):
        raise SystemExit(f'zorp_gallery_snapshot: talk did not start on {sel} (is zorp-talk.js loaded and the motion level full?)')
    paths = []
    for i, t in enumerate(times):
        page.evaluate(_TALK_FREEZE, [sel, t])
        path = out / 'talk' / f'{tag}-{i:02d}.png'
        path.write_bytes(page.screenshot(clip=clip, animations='allow'))
        paths.append(path)
    page.evaluate(_TALK_END, sel)
    return paths


def _talk_page(browser, base, scheme, errors):
    ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=DEVICE_SCALE_FACTOR, service_workers='block')
    page = ctx.new_page()
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.on('pageerror', lambda exc: errors.append(f'pageerror: {exc}'))
    page.emulate_media(color_scheme=scheme, reduced_motion='no-preference')
    page.goto(f'{base}/styleguide#zorp-charm', wait_until='networkidle')
    page.wait_for_selector('#zorp-charm [data-zorp-demo]')
    page.evaluate('document.fonts.ready')
    # the 128 px demo is shot at 160 px (the size the plan reviews); the sticky header would cover mid-page shots
    page.add_style_tag(content='header, .site-header, .site-nav { position: static !important; }'
                               ' .sg-talk-128, .sg-talk-128 .buddy-mascot { width: 160px !important; height: 160px !important; }'
                               ' #zorp-charm figure { min-width: 190px !important; }')
    level = page.evaluate('() => window.pbZorp.motionLevel()')
    if level != 'full':
        raise SystemExit(f'zorp_gallery_snapshot: --talk needs full motion but pbZorp.motionLevel() is {level!r}.')
    page.evaluate("() => { for (const el of document.querySelectorAll('#zorp-charm [data-zorp-demo]')) { window.pbZorp.bind(el); window.pbZorp.idle(false, el); } }")
    page.locator('#sg-zorp-talk-demos').scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    return ctx, page


def _demo_sel(view, size):
    return f'#zorp-charm [data-zorp-demo][data-talk-view="{view}"][data-talk-size="{size}"]'


def _build_talk_filmstrip(out, label, scheme, plan, rows):
    """rows: [(caption, [paths])] -> talk-filmstrip[-dark].png: a column per frame, state letters under the first row."""
    from PIL import Image, ImageDraw

    ims = [(cap, [Image.open(f).convert('RGB') for f in paths]) for cap, paths in rows]
    n = len(ims[0][1])
    cw = max(im.width for _, fr in ims for im in fr) + 8
    pad, label_w, head = 8, 220, 84
    font, small = _font(22), _font(28)
    bg = ims[0][1][0].getpixel((1, 1))
    fg = (245, 245, 245) if sum(bg) < 380 else (20, 20, 20)
    heights = [max(im.height for im in fr) + 12 for _, fr in ims]
    sheet = Image.new('RGB', (label_w + n * cw + pad, head + sum(heights) + 40), bg)
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), f'Zorp talk \u00b7 {label} \u00b7 {scheme} \u00b7 one frame every {TALK_STEP_MS} ms of the plan for: {TALK_LINE}', fill=fg, font=small)
    frames = plan['frames']
    names = {0: 'shut', 1: 'half', 2: 'open'}
    for i in range(n):
        t = min(plan['ms'], i * TALK_STEP_MS)
        state = 0
        for ft, st in frames:
            if ft <= t:
                state = st
        draw.text((label_w + i * cw + 4, head - 40), f'{t}', fill=fg, font=font)
        draw.text((label_w + i * cw + 4, head - 20), names[state], fill=fg, font=_font(16))
    y = head
    for (cap, fr), h in zip(ims, heights):
        draw.text((pad, y + h // 2 - 12), cap, fill=fg, font=font)
        for i, im in enumerate(fr):
            sheet.paste(im, (label_w + i * cw + 4, y + (h - im.height) // 2))
        y += h
    name = 'talk-filmstrip.png' if scheme == 'light' else f'talk-filmstrip-{scheme}.png'
    sheet.save(out / name)
    return name


def _build_talk_mouths(out, label, scheme, rows, cols):
    from PIL import Image, ImageDraw

    ims = [(cap, [Image.open(f).convert('RGB') for f in paths]) for cap, paths in rows]
    cw = max(im.width for _, fr in ims for im in fr) + 10
    rh = max(im.height for _, fr in ims for im in fr) + 10
    pad, label_w, head = 8, 190, 96
    font, small = _font(22), _font(28)
    bg = ims[0][1][0].getpixel((1, 1))
    fg = (245, 245, 245) if sum(bg) < 380 else (20, 20, 20)
    sheet = Image.new('RGB', (label_w + len(cols) * cw + pad, head + len(ims) * rh + pad), bg)
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), f'Zorp talk mouths \u00b7 {label} \u00b7 {scheme} \u00b7 the expression\u2019s own mouth (shut), then the half and open talk frames', fill=fg, font=small)
    for c, name in enumerate(cols):
        draw.text((label_w + c * cw + 4, head - 30), name, fill=fg, font=_font(17))
    for r, (cap, fr) in enumerate(ims):
        y = head + r * rh
        draw.text((pad, y + rh // 2 - 12), cap, fill=fg, font=font)
        for c, im in enumerate(fr):
            sheet.paste(im, (label_w + c * cw + 4, y + 4))
    name = 'talk-mouths.png' if scheme == 'light' else f'talk-mouths-{scheme}.png'
    sheet.save(out / name)
    return name


def _talk_sheets(browser, base, out, label):
    """The two E9 Phase 1 preview sheets, light and dark. -> (files, errors)"""
    (out / 'talk').mkdir(exist_ok=True)
    files, errors = [], []
    for scheme in ('light', 'dark'):
        ctx, page = _talk_page(browser, base, scheme, errors)
        plan = page.evaluate('([t, m]) => window.pbZorp.talkPlan(t, {max: m})', [TALK_LINE, TALK_MAX])
        times = list(range(0, plan['ms'], TALK_STEP_MS)) + [plan['ms']]
        rows = []
        for view in ('front', 'side'):
            for size, face in ((128, True), (56, False)):
                tag = f'{scheme}-{view}-{160 if size == 128 else size}'
                rows.append((f'{view} {160 if size == 128 else size} px',
                             _talk_shots(page, _demo_sel(view, size), TALK_LINE, times, face, tag, out)))
        files.append(_build_talk_filmstrip(out, label, scheme, plan, rows))
        # mouths over expressions: closed (the expression's own mouth), half, open
        mp = page.evaluate("() => window.pbZorp.talkPlan('Zorp is happy', {max: 1600})")
        first = lambda st: next(t for t, s in mp['frames'][1:] if s == st)  # noqa: E731
        stamps = [first(0) + 20, first(1) + 20, first(2) + 20]
        cols = ['front shut', 'front half', 'front open', 'side shut', 'side half', 'side open', '56 shut', '56 half', '56 open']
        mrows = []
        for name in TALK_EXPRESSIONS:
            cells = []
            for view, size, face in (('front', 128, True), ('side', 128, True), ('front', 56, False)):
                sel = _demo_sel(view, size)
                page.evaluate("([s, n]) => window.pbZorp.setExpression(n, {el: document.querySelector(s)})", [sel, name])
                page.wait_for_timeout(260)
                clip = _talk_clip(page, sel, face)
                page.evaluate(_TALK_START, [sel, 'Zorp is happy', 1600])
                for k, t in enumerate(stamps):
                    page.evaluate(_TALK_FREEZE, [sel, t])
                    path = out / 'talk' / f'{scheme}-mouth-{name}-{view}-{size}-{k}.png'
                    path.write_bytes(page.screenshot(clip=clip, animations='allow'))
                    cells.append(path)
                page.evaluate(_TALK_END, sel)
            mrows.append((name, cells))
        files.append(_build_talk_mouths(out, label, scheme, mrows, cols))
        ctx.close()
    return files, errors


# ---------------------------------------------------------------------------------------------
# E9 Phase 2: the soft body sheets (--soft, --soft-only)
# ---------------------------------------------------------------------------------------------
SOFT_CLIPS = ('hop', 'cheer', 'fist-pump', 'victory', 'dance', 'flex')
SOFT_FRAMES = 12
SOFT_SPEED = 0.1
SOFT_PAD_TOP = 62          # css px of headroom above a 160 px mascot (the biggest jump is 15 units, about 38 px)
_SOFT_STAGE = """(cells) => {
  const old = document.getElementById('sg-soft-stage'); if (old) old.remove();
  const src = document.querySelector('#sg-zorp-poselib-demo svg.buddy-mascot') || document.querySelector('svg.buddy-mascot');
  const stage = document.createElement('div'); stage.id = 'sg-soft-stage';
  let bg = 'rgb(255, 255, 255)';
  for (let e = document.querySelector('#zorp-charm') || document.body; e; e = e.parentElement) {
    const c = getComputedStyle(e).backgroundColor.match(/[\\d.]+/g);
    if (c && (c.length < 4 || +c[3] > 0.5)) { bg = 'rgb(' + c.slice(0, 3).join(',') + ')'; break; } }
  let W = 0, H = 0; cells.forEach(c => { W = Math.max(W, c.x + c.w); H = Math.max(H, c.y + c.h); });
  stage.style.cssText = 'position:fixed;left:0;top:0;z-index:99999;width:' + W + 'px;height:' + H + 'px;background:' + bg;
  const z = window.pbZorp;
  cells.forEach(c => {
    const d = document.createElement('div');
    d.setAttribute('data-soft', c.soft); d.setAttribute('data-key', c.key);
    d.style.cssText = 'position:absolute;display:flex;align-items:flex-end;justify-content:center;box-sizing:border-box;padding-bottom:8px;left:' + c.x + 'px;top:' + c.y + 'px;width:' + c.w + 'px;height:' + c.h + 'px';
    const host = document.createElement('span'); host.className = 'study-buddy-face'; host.setAttribute('data-buddy-face', ''); host.setAttribute('data-face', 'nudge');
    host.style.cssText = 'display:block;width:' + c.size + 'px;height:' + c.size + 'px;flex:none';
    const svg = src.cloneNode(true); svg.style.cssText = 'width:100%;height:100%;overflow:visible;' + (c.silhouette ? 'filter:brightness(0);' : '');
    host.appendChild(svg); d.appendChild(host); stage.appendChild(d);
    z.bind(host); z.idle(false, host);
    if (c.view !== 'front') z.turn(c.view, 'r', {el: host, instant: true, required: true});
  });
  document.body.appendChild(stage);
  return [W, H];
}"""
_SOFT_PLAY = """([clip, speed]) => {
  const z = window.pbZorp, root = document.documentElement;
  const cells = [...document.querySelectorAll('#sg-soft-stage [data-soft]')];
  const go = (off) => {
    if (off) root.setAttribute('data-zorp-soft', 'off'); else root.removeAttribute('data-zorp-soft');
    cells.filter(c => (c.dataset.soft === 'off') === off).forEach(c => z.play(clip, {el: c.querySelector('.study-buddy-face'), speed}));
  };
  go(true); go(false); window.__t0 = performance.now();
  return cells.map(c => !!c.querySelector('svg').getAnimations({subtree: true}).length);
}"""
_SOFT_WAIT = "(t) => new Promise(r => { const w = () => performance.now() - window.__t0 >= t ? r(performance.now() - window.__t0) : setTimeout(w, 2); w(); })"
_SOFT_CLEAR = """() => { const z = window.pbZorp; document.documentElement.removeAttribute('data-zorp-soft');
  document.querySelectorAll('#sg-soft-stage .study-buddy-face').forEach(h => { z.play('blink', {el: h}); }); }"""
# D4 prototype: a belly ellipse in .buddy-body that follows the body's own animation: scaleX(1 + 2.2 * (body sx - 1)) about its bottom
_SOFT_BELLY = """([k, cx, cy, rx, ry]) => {
  const host = document.querySelector('#sg-soft-stage [data-key="' + k + '"] .study-buddy-face');
  const body = host.querySelector('.buddy-body'); if (!body) return 0;
  body.querySelectorAll('.zorp-belly').forEach(b => b.remove());
  const NS = 'http://www.w3.org/2000/svg'; const b = document.createElementNS(NS, 'ellipse');
  b.setAttribute('class', 'zorp-belly'); b.setAttribute('cx', cx); b.setAttribute('cy', cy); b.setAttribute('rx', rx); b.setAttribute('ry', ry);
  b.setAttribute('fill', 'var(--zorp-body, var(--brand-500))'); b.style.transformBox = 'fill-box'; b.style.transformOrigin = '50% 100%';
  body.insertBefore(b, body.querySelector('.zorp-highlight'));
  return 1;
}"""
_SOFT_BELLY_FOLLOW = """(k) => {
  const host = document.querySelector('#sg-soft-stage [data-key="' + k + '"] .study-buddy-face');
  const body = host.querySelector('.buddy-body'), belly = body.querySelector('.zorp-belly');
  const a = body.getAnimations().find(x => x.effect && x.effect.target === body); if (!a || !belly) return 0;
  const fr = a.effect.getKeyframes().map(f => { const m = /scale\\(([-\\d.]+),\\s*([-\\d.]+)\\)/.exec(f.transform);
    return {offset: f.offset, easing: f.easing, transform: 'scaleX(' + (1 + 2.2 * (+m[1] - 1)) + ')'}; });
  const n = belly.animate(fr, {duration: a.effect.getTiming().duration, composite: 'replace', fill: 'none', easing: 'linear'});
  n.startTime = a.startTime; return 1;
}"""


def _belly_fit(cy, ry, clearance=0.2):
    """The widest belly ellipse (cx 32, centre `cy`, radii rx x `ry`) that clears the body outline (cx 32, cy 36, 21 x 21.5) by `clearance` units at rest."""
    import math

    def margin(rx):
        worst = 9e9
        for i in range(360):
            a = math.radians(i)
            x, y = rx * math.cos(a), cy + ry * math.sin(a)
            # distance to the outline, by the first-order gradient estimate of the ellipse equation
            f = (x / 21) ** 2 + ((y - 36) / 21.5) ** 2
            gx, gy = 2 * x / 21 ** 2, 2 * (y - 36) / 21.5 ** 2
            worst = min(worst, (1 - f) / math.hypot(gx, gy) if f < 1 else -1)
        return worst
    lo, hi = 1.0, 21.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if margin(mid) >= clearance:
            lo = mid
        else:
            hi = mid
    return round(lo, 2)


def _soft_page(browser, base, scheme, errors, block_poses=False, dsf=DEVICE_SCALE_FACTOR):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900}, device_scale_factor=dsf, service_workers='block')
    page = ctx.new_page()
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.on('pageerror', lambda exc: errors.append(f'pageerror: {exc}'))
    if block_poses:
        page.route('**/zorp-poses.js*', lambda route: route.abort())
    page.emulate_media(color_scheme=scheme, reduced_motion='no-preference')
    page.goto(f'{base}/styleguide#zorp-charm', wait_until='networkidle')
    page.wait_for_selector('#zorp-charm [data-zorp-demo]')
    page.evaluate('document.fonts.ready')
    level = page.evaluate('() => window.pbZorp.motionLevel()')
    if level != 'full':
        raise SystemExit(f'zorp_gallery_snapshot: --soft needs full motion but pbZorp.motionLevel() is {level!r}.')
    return ctx, page


def _soft_layout(columns, sizes, pad_x=14):
    """cells for the stage: columns [(view, soft)] x rows `sizes`; -> (cells, {(col, size): rect})"""
    cells, rects = [], {}
    y = 0
    for size in sizes:
        w = size + (24 if size < 100 else 30)
        h = size + (SOFT_PAD_TOP if size >= 100 else 34) + 8
        for c, (view, soft) in enumerate(columns):
            rect = {'x': c * w, 'y': y, 'w': w, 'h': h}
            cells.append({**rect, 'size': size, 'view': view, 'soft': soft, 'key': f'{c}-{size}'})
            rects[(c, size)] = rect
        y += h
    return cells, rects


def _soft_shoot(page, rects, clip, times, speed, tag, out, prep=None):
    """Play `clip` in every stage cell at `speed`, shoot the stage at each of `times` (ms of clip time) and cut it into cells.
    -> {(col, size): [PIL image per time]}"""
    from io import BytesIO

    from PIL import Image

    W, H = max(r['x'] + r['w'] for r in rects.values()), max(r['y'] + r['h'] for r in rects.values())
    page.evaluate(_SOFT_CLEAR)
    page.wait_for_timeout(250)
    started = page.evaluate(_SOFT_PLAY, [clip, speed])
    if not all(started):
        raise SystemExit(f'zorp_gallery_snapshot: clip {clip!r} did not start on every stage cell (motion level, or no such clip).')
    if prep:
        prep()
    got = {k: [] for k in rects}
    dsf = DEVICE_SCALE_FACTOR
    for t in times:
        page.evaluate(_SOFT_WAIT, t / speed)
        img = Image.open(BytesIO(page.screenshot(clip={'x': 0, 'y': 0, 'width': W, 'height': H}, animations='allow'))).convert('RGB')
        for k, r in rects.items():
            got[k].append(img.crop((int(r['x'] * dsf), int(r['y'] * dsf), int((r['x'] + r['w']) * dsf), int((r['y'] + r['h']) * dsf))))
    page.wait_for_timeout(int(max(times) / speed * 0.3) + 200)
    return got


def _soft_times(dur, n=SOFT_FRAMES):
    return [round(i / (n - 1) * 0.97 * dur) for i in range(n)]


def _soft_sheet(out, name, title, rows, scheme, headers=None, label_w=230, zoom=1.0):
    """rows: [(label, [PIL image])] -> a sheet (rows may differ in size); `headers` is the text above each column."""
    from PIL import Image, ImageDraw

    def fit(im):
        return im if zoom == 1.0 else im.resize((max(1, int(im.width * zoom)), max(1, int(im.height * zoom))), Image.LANCZOS)
    ims = [(lab, [fit(im) for im in fr]) for lab, fr in rows]
    bg = ims[0][1][0].getpixel((1, 1))
    fg = (245, 245, 245) if sum(bg) < 380 else (20, 20, 20)
    cw = max(im.width for _, fr in ims for im in fr)
    heights = [max(im.height for im in fr) for _, fr in ims]
    n = max(len(fr) for _, fr in ims)
    head = 78
    sheet = Image.new('RGB', (label_w + n * cw + 16, head + sum(heights) + 12), bg)
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 10), title, fill=fg, font=_font(26))
    for i in range(n):
        if headers:
            draw.text((label_w + i * cw + 6, head - 24), str(headers[i]), fill=fg, font=_font(17))
    y = head
    for r, ((lab, fr), ch) in enumerate(zip(ims, heights)):
        draw.text((12, y + ch // 2 - 12), lab, fill=fg, font=_font(20))
        for i, im in enumerate(fr):
            sheet.paste(im, (label_w + i * cw, y + ch - im.height))
        y += ch
        if r % 2 == 1:
            draw.line([(0, y - 1), (sheet.width, y - 1)], fill=(150, 150, 150), width=1)
    sheet.save(out / name)
    return name


def _soft_curve(page, out, scheme, name, clip='hop'):
    """A small chart of the hop's body layer (sx, sy) and the face ride over the clip, read from the keyframes compileBeats() makes."""
    from PIL import Image, ImageDraw

    data = page.evaluate("""(clip) => { const z = window.pbZorp; const info = z.clipInfo(clip);
      const host = document.querySelector('#sg-soft-stage .study-buddy-face'); const svg = host.querySelector('svg');
      const P = { root: svg.querySelector('.buddy-root'), shadow: svg.querySelector('.buddy-shadow'), head: svg.querySelector('.buddy-head'),
        body: svg.querySelector('.buddy-body'), face: svg.querySelector('.zorp-face'), ride: svg.querySelector('.zorp-ride'),
        cheeks: svg.querySelector('.zorp-slot--cheeks'), armL: [], armR: [], antL: svg.querySelector('.buddy-antenna--l'),
        antR: svg.querySelector('.buddy-antenna--r'), footL: svg.querySelector('.buddy-foot--l'), footR: svg.querySelector('.buddy-foot--r') };
      const out = {}; document.documentElement.removeAttribute('data-zorp-soft');
      z.compileBeats(info.beats, P, {}).forEach(([t, fr]) => { const k = ['body', 'face', 'ride', 'cheeks', 'root'].find(n => P[n] === t); if (k) out[k] = fr.map(f => [f.offset * info.dur, f.transform]); });
      out.dur = info.dur; return out; }""", clip)
    dur = data['dur']
    w, h = 1500, 420
    bg = (255, 255, 255) if scheme == 'light' else (24, 24, 27)
    fg = (20, 20, 20) if scheme == 'light' else (240, 240, 240)
    im = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(im)
    d.text((12, 8), f'{clip}: body layer scale (blue x, orange y; 1.00 on the midline, 0.06 per grid line) and face ride (green, units)', fill=fg, font=_font(22))
    x0, x1, y0, y1 = 70, w - 30, 60, h - 40
    mid = (y0 + y1) / 2
    for g in range(-3, 4):
        d.line([(x0, mid + g * 50), (x1, mid + g * 50)], fill=(120, 120, 120) if g else fg, width=1)
    for ms in range(0, int(dur) + 1, 100):
        x = x0 + ms / dur * (x1 - x0)
        d.line([(x, y1), (x, y1 + 6)], fill=fg)
        d.text((x - 12, y1 + 8), str(ms), fill=fg, font=_font(14))

    def num(tf, which):
        import re as _re
        m = _re.search(r'scale\(([-\d.]+),([-\d.]+)\)', tf) if which != 'dy' else _re.search(r'translate\(0,([-\d.]+)px\)', tf)
        return float(m.group(1 if which == 'x' else 2 if which == 'y' else 1))

    def line(key, which, colour, scale, base):
        pts = [(x0 + t / dur * (x1 - x0), mid - (num(tf, which) - base) * scale) for t, tf in data.get(key, [])]
        if len(pts) > 1:
            d.line(pts, fill=colour, width=3)
    line('body', 'x', (60, 110, 230), 50 / 0.06, 1)
    line('body', 'y', (240, 140, 30), 50 / 0.06, 1)
    line('face', 'dy', (40, 170, 90), 50 / 1.0, 0)
    im.save(out / name)
    return name


def _soft_sheets(browser, base, out, label):
    from PIL import Image
    """The E9 Phase 2 preview sheets, light and dark. -> (files, errors)"""
    (out / 'soft').mkdir(exist_ok=True)
    files, errors = [], []
    for scheme in os.environ.get('PB_SOFT_SCHEMES', 'light,dark').split(','):   # dev: PB_SOFT_SCHEMES=light for a quick look
        suffix = '' if scheme == 'light' else '-dark'
        columns = [('front', 'off'), ('front', 'on'), ('side', 'off'), ('side', 'on')]
        cells, rects = _soft_layout(columns, (160, 56))
        # E8 rows: soft layer off. cheer and hop: the legacy track clips, from a page that never loads zorp-poses.js
        legacy_ctx, legacy = _soft_page(browser, base, scheme, errors, block_poses=True)
        ctx, page = _soft_page(browser, base, scheme, errors)
        page.add_style_tag(content='header, .site-header, .site-nav { position: static !important; }')
        legacy.add_style_tag(content='header, .site-header, .site-nav { position: static !important; }')
        page.evaluate(_SOFT_STAGE, cells)
        legacy.evaluate(_SOFT_STAGE, cells)
        strips = {}
        for clip in os.environ.get('PB_SOFT_CLIPS', ','.join(SOFT_CLIPS)).split(','):
            info = page.evaluate('(c) => window.pbZorp.clipInfo(c)', clip) or {}
            dur = info.get('dur') or LEGACY_CLIP_DUR.get(clip, 1200)
            times = _soft_times(dur)
            new = _soft_shoot(page, rects, clip, times, SOFT_SPEED, clip, out)
            if clip in ('hop', 'cheer'):
                old = _soft_shoot(legacy, rects, clip, times, SOFT_SPEED, clip, out)
            else:
                old = new
            strips[clip] = (times, old, new)
        for size, tag in ((160, ''), (56, '-56')):
            rows, heads = [], None
            for clip in strips:
                times, old, new = strips[clip]
                heads = heads or times
                for view, off_col, on_col in (('front', 0, 1), ('side', 2, 3)):
                    rows.append((f'{clip} {view} E8', old[(off_col, size)]))
                    rows.append((f'{clip} {view} E9', new[(on_col, size)]))
            name = f'soft-ab-filmstrips{tag}{suffix}.png'
            _soft_sheet(out, name, f'Zorp soft body · {label} · {scheme} · {size} px · E8 row (soft layer off; cheer and hop: the legacy clips) above E9 row, frames across each clip', rows, scheme, zoom=0.5 if size == 160 else 1.0)
            files.append(name)
        # landing close-up: hop, every 20 ms of clip time across the landing and its wobble
        info = page.evaluate('(c) => window.pbZorp.clipInfo(c)', 'hop')
        land = sum((b.get('ms') or 0) + (b.get('hold') or 0) for b in info['beats'][:3])
        times = list(range(land - 40, land + 261, 25))[:13]
        zc, zr = _soft_layout([('front', 'off'), ('front', 'on'), ('side', 'off'), ('side', 'on')], (160,))
        page.evaluate(_SOFT_STAGE, zc)
        got = _soft_shoot(page, zr, 'hop', times, 0.05, 'land', out)
        rows = [('front E8', got[(0, 160)]), ('front E9', got[(1, 160)]), ('side E8', got[(2, 160)]), ('side E9', got[(3, 160)])]
        name = f'soft-landing{suffix}.png'
        _soft_sheet(out, name, f'Zorp hop landing · {label} · {scheme} · one frame every 25 ms from {land - 40} ms (landing at {land} ms: squash, then 70/140/210 ms of jelly)', rows, scheme,
                    headers=[f'{t} ms' for t in times], zoom=0.65)
        files.append(name)
        page.evaluate(_SOFT_STAGE, zc)
        files.append(_soft_curve(page, out, scheme, f'soft-curve{suffix}.png'))
        # silhouettes: take-off stretch and landing squash of fist-pump, flat colour
        cols = [('front', 'off'), ('front', 'on'), ('side', 'off'), ('side', 'on')]
        sc, sr = _soft_layout(cols, (160, 56))
        for c in sc:
            c['silhouette'] = True
        page.evaluate(_SOFT_STAGE, sc)
        finfo = page.evaluate('(c) => window.pbZorp.clipInfo(c)', 'fist-pump')
        b = finfo['beats']
        marks = [('crouch', sum(x.get('ms', 0) + x.get('hold', 0) for x in b[:1])), ('apex', sum(x.get('ms', 0) + x.get('hold', 0) for x in b[:1]) + b[1]['ms'] + 40),
                 ('landing', sum(x.get('ms', 0) + x.get('hold', 0) for x in b[:2]) + b[2]['ms']), ('wobble', sum(x.get('ms', 0) + x.get('hold', 0) for x in b[:2]) + b[2]['ms'] + 70)]
        got = _soft_shoot(page, sr, 'fist-pump', [t for _, t in marks], SOFT_SPEED, 'sil', out)
        rows = []
        for size in (160, 56):
            for view, off_col, on_col in (('front', 0, 1), ('side', 2, 3)):
                rows.append((f'{view} {size} E8', got[(off_col, size)]))
                rows.append((f'{view} {size} E9', got[(on_col, size)]))
        name = f'soft-silhouette{suffix}.png'
        _soft_sheet(out, name, f'Zorp soft silhouettes · {label} · {scheme} · fist-pump: crouch, apex, landing, wobble (flat colour, E8 above E9)', rows, scheme, headers=[m for m, _ in marks], zoom=0.6)
        files.append(name)
        # D4: the pear belly, prototyped here (never in the shipped markup): none, the plan's numbers, and the widest that clears the outline
        wide = _belly_fit(46.5, 10.5)
        variants = [('no belly', None), ('plan belly (rx 15)', (32, 46.5, 15, 10.5)), (f'wide belly (rx {wide})', (32, 46.5, wide, 10.5))]
        bc, br = [], {}
        columns = [('front', v[0]) for v in variants]
        bc, br = _soft_layout(columns, (160, 56))
        page.evaluate(_SOFT_STAGE, bc)
        for ci, (_, geom) in enumerate(variants):
            for size in (160, 56):
                page.evaluate("(k) => document.querySelector('#sg-soft-stage [data-key=\"' + k + '\"]').setAttribute('data-soft', 'on')", f'{ci}-{size}')
                if geom:
                    page.evaluate(_SOFT_BELLY, [f'{ci}-{size}', *geom])
        t_land = sum((x.get('ms') or 0) + (x.get('hold') or 0) for x in info['beats'][:3])
        times = [t_land - 90, t_land - 10, t_land + 70, t_land + 140, t_land + 220]

        def follow():
            for ci, (_, geom) in enumerate(variants):
                if geom:
                    for size in (160, 56):
                        page.evaluate(_SOFT_BELLY_FOLLOW, f'{ci}-{size}')
        got = _soft_shoot(page, br, 'hop', times, 0.1, 'belly', out, prep=follow)
        rows = []
        for size, zoom in ((160, 0.6), (56, 1.0), (56, 2.5)):
            for ci, (cap, _) in enumerate(variants):
                fr = got[(ci, size)]
                if zoom != 1.0:
                    fr = [im.resize((int(im.width * zoom), int(im.height * zoom)), Image.LANCZOS) for im in fr]
                rows.append((f'{cap} {size} px' + (f' x{zoom}' if size == 56 and zoom > 1 else ''), fr))
        name = f'belly-ab{suffix}.png'
        _soft_sheet(out, name, f'Zorp pear belly A/B (D4) \u00b7 {label} \u00b7 {scheme} \u00b7 hop at 10 percent speed: before landing, at landing, +70, +140, +220 ms', rows, scheme,
                    headers=[f'{t} ms' for t in times])
        files.append(name)
        ctx.close()
        legacy_ctx.close()
    return files, errors



def talk_only(label, server_python):
    """--talk-only: just the talk sheets, from a throwaway app server (no gallery run)."""
    return sheets_only(label, server_python, _talk_sheets)


def soft_only(label, server_python):
    """--soft-only: just the E9 Phase 2 soft body sheets (no gallery run)."""
    return sheets_only(label, server_python, _soft_sheets)


def sheets_only(label, server_python, builder):
    """Run `builder(browser, base, out, label) -> (files, errors)` against a throwaway app server."""
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
        from PIL import Image  # noqa: F401
    except ImportError:
        print('zorp_gallery_snapshot: Playwright/Pillow not installed in this interpreter; skipping (dev tool, not required).')
        return 0
    tmp = Path(tempfile.mkdtemp(prefix='pb_talk_'))
    proc = None
    log_handle = open(tmp / 'server.log', 'w', encoding='utf-8')
    try:
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
            print(f'zorp_gallery_snapshot: the app server did not start ({server_python}).')
            return 1
        threading.Thread(target=lambda: [None for _ in proc.stdout], daemon=True).start()
        final_out = _out_dir(label)
        out = final_out
        out.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except PlaywrightError:
                print('Chromium not available; skipping.')
                return 0
            files, errors = builder(browser, f'http://127.0.0.1:{port}', out, label)
            browser.close()
        print(f'Wrote {", ".join(files)} in {out}; {len(errors)} console errors')
        for e in errors:
            print('  console error:', e)
        return 1 if errors else 0
    finally:
        if proc is not None:
            proc.terminate()
        log_handle.close()
        shutil.rmtree(tmp, ignore_errors=True)


def snapshot(label, server_python, clips=False, copy=False, talk=False, soft=False):
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
                    got = _pose_clip_frames(page, out, motion, E9_CLIPS if clips else None)
                    if motion == 'full':
                        clip_full = got
                    else:
                        clip_reduced = got
                console[f'{scheme}-{motion}'] = errors
                ctx.close()
            copy_info = None
            if copy:
                captures, missing, copy_errors = _copy_guide(browser, base, out)
                copy_sheet = _build_copy_sheet(out, label, captures)
                if copy_sheet:
                    files.append(copy_sheet)
                files.extend(c['file'] for c in captures)
                copy_info = {'captures': captures, 'missing': missing, 'console_errors': copy_errors,
                             'viewport': COPY_VIEWPORT}
                print(f'  copy: {len(captures)} panels, {len(missing)} catalog lines not captured, {len(copy_errors)} console errors')
                for line in missing:
                    print(f'    not captured: {line}')
            if talk:
                talk_files, talk_errors = _talk_sheets(browser, base, out, label)
                files.extend(talk_files)
                print(f'  talk: {", ".join(talk_files)}, {len(talk_errors)} console errors')
            if soft:
                soft_files, soft_errors = _soft_sheets(browser, base, out, label)
                files.extend(soft_files)
                print(f'  soft: {", ".join(soft_files)}, {len(soft_errors)} console errors')
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
                           _build_clip_filmstrips(out, label, clip_full or {}, clip_reduced or {}, E9_CLIPS if clips else None)):
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
        if clips:
            manifest['clips'] = list(E9_CLIPS)
        if copy_info is not None:
            manifest['copy'] = copy_info
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
    ap.add_argument('--clips', action='store_true', help='E9 clip filmstrips: cheer, hop, fist-pump, victory, flex, dance (full motion forced)')
    ap.add_argument('--copy', action='store_true', help='E9 copy sheet: every Guide line in its panel at 375 px, light and dark')
    ap.add_argument('--talk', action='store_true', help='E9 Phase 1 talk sheets: filmstrip of a spoken Guide line and the talk mouths over expressions')
    ap.add_argument('--talk-only', action='store_true', help='only the --talk sheets (no gallery run), written to data/zorp_gallery/<label>/')
    ap.add_argument('--soft', action='store_true', help='E9 Phase 2 soft body sheets: E8 against E9 filmstrips, landing close-up, silhouettes, belly A/B')
    ap.add_argument('--soft-only', action='store_true', help='only the --soft sheets (no gallery run), written to data/zorp_gallery/<label>/')
    ap.add_argument('--looks', action='store_true', help='look sheets (Phase 1+)')
    args = ap.parse_args(argv)
    if args.serve:
        serve()
        return 0
    if args.talk_only:
        return talk_only(args.label, args.server_python)
    if args.soft_only:
        return soft_only(args.label, args.server_python)
    if args.looks:
        print('--looks: not built until Phase 1+')
    rc = snapshot(args.label, args.server_python, clips=args.clips, copy=args.copy, talk=args.talk, soft=args.soft)
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
