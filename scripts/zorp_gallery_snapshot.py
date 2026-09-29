"""Zorp gallery snapshot (E8 dev tool; NOT a smoke test).

Renders `/styleguide#zorp-gallery` in headless Chromium and writes review images to
`data/zorp_gallery/<label>/` (gitignored):

* `faces.png` (full motion) and `faces-reduced.png` (prefers-reduced-motion): one
  contact sheet each, rows light-56 / light-128 / dark-56 / dark-128, one column per legacy face;
* `expressions.png` (Phase 1+): every preset in the gallery, same rows, in blocks of seven;
* `faces-parity.png` (with `--compare`): the compared snapshot on top, this one below, for the
  legacy faces at 128 px in light and dark;
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

Pixel comparisons (`--compare`, best alignment within a few device pixels) are only meaningful on the same machine and Chromium
build. Filmstrips and look sheets are built from Phase 1 (`--clips`, `--looks`).
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
OVER_PCT = 0.5


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


def _best_shift_pct(ia, ib, reach_x=3, reach_y=8):
    """Smallest changed-pixel percentage over small integer shifts of `ib` against `ia`.

    Gallery cells are stretched by their flex row, so a whole cell can sit a few device pixels
    higher or lower when the number of cells changes. That is layout, not art, so the art is
    compared at its best alignment (the shift is at most reach_x / reach_y device pixels)."""
    from PIL import ImageChops

    best = 100.0
    w, h = ia.size
    for dy in range(-reach_y, reach_y + 1):
        for dx in range(-reach_x, reach_x + 1):
            box_a = (max(dx, 0), max(dy, 0), w + min(dx, 0), h + min(dy, 0))
            box_b = (max(-dx, 0), max(-dy, 0), w + min(-dx, 0), h + min(-dy, 0))
            ca, cb = ia.crop(box_a), ib.crop(box_b)
            r, g, b, a = ImageChops.difference(ca, cb).split()
            worst = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(b, a))
            changed = worst.point(lambda v: 255 if v > DIFF_THRESHOLD else 0).histogram()[255]
            best = min(best, 100.0 * changed / (ca.width * ca.height))
    return best


def compare(label, other):
    """Determinism / regression check between two snapshot directories. Always exit 0."""
    from PIL import Image, ImageChops

    a_dir, b_dir = _out_dir(label) / 'cells', _out_dir(other) / 'cells'
    if not a_dir.is_dir() or not b_dir.is_dir():
        print(f'compare: missing cells directory ({a_dir} or {b_dir}); nothing to compare.')
        return
    lines = []
    for name in sorted(p.name for p in b_dir.glob('*.png') if not (a_dir / p.name).is_file()):
        lines.append(f'{name}  MISSING in {label}  OVER')
    for path in sorted(a_dir.glob('*.png')):
        twin = b_dir / path.name
        if not twin.is_file():
            lines.append(f'{path.name}  NEW in {label} (no {other} cell)')
            continue
        ia, ib = Image.open(path).convert('RGBA'), Image.open(twin).convert('RGBA')
        if ia.size != ib.size:
            # Cells stretch with their flex/grid row, so sizes can differ by a few pixels.
            if abs(ia.width - ib.width) > 8 or abs(ia.height - ib.height) > 8:
                pct = 100.0
            else:
                cw, chh = min(ia.width, ib.width), min(ia.height, ib.height)
                pct = _best_shift_pct(ia.crop((0, 0, cw, chh)), ib.crop((0, 0, cw, chh)))
        else:
            diff = ImageChops.difference(ia, ib)
            r, g, b, a = diff.split()
            worst = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(b, a))
            changed = worst.point(lambda v: 255 if v > DIFF_THRESHOLD else 0).histogram()[255]
            pct = 100.0 * changed / (ia.width * ia.height)
            if pct > OVER_PCT:
                pct = min(pct, _best_shift_pct(ia, ib))
        face = path.stem.split('-', 3)[-1]
        if face in PARITY_EXEMPT:
            lines.append(f'{path.name}  {pct:.2f}%  EXEMPT ({PARITY_EXEMPT[face]})')
        else:
            lines.append(f'{path.name}  {pct:.2f}%' + ('  OVER' if pct > OVER_PCT else ''))
    report = '\n'.join(lines) or 'no common cells'
    print(report)
    (_out_dir(label) / f'compare-{other}.txt').write_text(report + '\n', encoding='utf-8')
    over = sum(1 for line in lines if line.endswith('OVER'))
    print(f'compare: {len(lines)} cells, {over} over {OVER_PCT}%.')


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
                    files.append(rel)
                    records[motion][(scheme, size, face)] = out / rel
                    manifest_cells.append({'scheme': scheme, 'motion': motion, 'size': size,
                                           'face': face, 'file': rel, 'zorp_faces': visible})
                console[f'{scheme}-{motion}'] = errors
                ctx.close()
            version = browser.version
            browser.close()

        seen = []
        for _key in records['full']:
            if _key[2] not in seen:
                seen.append(_key[2])
        for motion in ('full', 'reduced'):
            legacy = {k: v for k, v in records[motion].items() if k[2] in GALLERY_FACES}
            files.append(_build_sheet(out, label, motion, legacy))
        files.append(_build_sheet(out, label, 'full', records['full'], faces=tuple(seen),
                                  name='expressions.png', block=BLOCK))
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
        print(f'  sheets: {final_out / "faces.png"}, {final_out / "faces-reduced.png"}, {final_out / "expressions.png"}')
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
