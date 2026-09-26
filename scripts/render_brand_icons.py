"""Rasterize the Problem Bank mark to PWA PNGs and favicon.ico.

Geometry matches static/icons/mark.svg (U5.7). Stdlib only.

Run: python scripts/render_brand_icons.py
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / 'static' / 'icons'

BRAND = (0x1A, 0x86, 0xD4, 255)  # --brand-500
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)
_MARK_RX = 8 / 32

# Mark viewBox is 32×32. P path: M9 8h14v10H14v6H9V8zm5 3.5h5.5v3.5H14V11.5z
_P_OUTER = (9 / 32, 8 / 32, 23 / 32, 24 / 32)  # x0, y0, x1, y1 of bounding box
# Stem is x in [9,14] for y in [18,24]; bowl is full [9,23]×[8,18]
_STEM_X1 = 14 / 32
_BOWL_Y1 = 18 / 32
_COUNTER = (14 / 32, 11.5 / 32, 19.5 / 32, 15 / 32)


def _in_rect(u: float, v: float, box: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = box
    return x0 <= u < x1 and y0 <= v < y1


def _in_p(u: float, v: float) -> bool:
    """True if (u, v) in [0,1]² of the 32-unit mark sits on the white P."""
    if not _in_rect(u, v, _P_OUTER):
        return False
    if u >= _STEM_X1 and v >= _BOWL_Y1:
        return False
    if _in_rect(u, v, _COUNTER):
        return False
    return True


def _in_rounded_rect(u: float, v: float, radius: float = _MARK_RX) -> bool:
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        return False
    if radius <= u <= 1.0 - radius or radius <= v <= 1.0 - radius:
        return True
    cx = radius if u < 0.5 else 1.0 - radius
    cy = radius if v < 0.5 else 1.0 - radius
    return (u - cx) ** 2 + (v - cy) ** 2 <= radius ** 2


def _sample_pwa(nx: float, ny: float, inset: float) -> tuple[int, int, int, int]:
    """Full-bleed brand field; P mapped into the inner (1-2*inset) square."""
    span = 1.0 - 2.0 * inset
    u = (nx - inset) / span
    v = (ny - inset) / span
    if 0.0 <= u < 1.0 and 0.0 <= v < 1.0 and _in_p(u, v):
        return WHITE
    return BRAND


def _sample_mark(nx: float, ny: float) -> tuple[int, int, int, int]:
    """Rounded square mark with transparent corners (favicon / apple)."""
    if not _in_rounded_rect(nx, ny):
        return CLEAR
    if _in_p(nx, ny):
        return WHITE
    return BRAND


def _write_png(path: Path, width: int, height: int, pixels: bytes) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', crc)

    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
        + chunk(b'IEND', b'')
    )


def _raster(size: int, sample_fn) -> bytes:
    out = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            acc = [0, 0, 0, 0]
            for dy in (0.25, 0.75):
                for dx in (0.25, 0.75):
                    colour = sample_fn((x + dx) / size, (y + dy) / size)
                    for i in range(4):
                        acc[i] += colour[i]
            i = (y * size + x) * 4
            out[i] = acc[0] // 4
            out[i + 1] = acc[1] // 4
            out[i + 2] = acc[2] // 4
            out[i + 3] = acc[3] // 4
    return bytes(out)


def _write_ico(path: Path, png_bytes: bytes, size: int) -> None:
    # ICO with a PNG payload (Vista+). One 32×32 image.
    header = struct.pack('<HHH', 0, 1, 1)
    entry = struct.pack(
        '<BBBBHHII',
        size if size < 256 else 0,
        size if size < 256 else 0,
        0,
        0,
        1,
        32,
        len(png_bytes),
        22,
    )
    path.write_bytes(header + entry + png_bytes)


def main() -> None:
    ICONS.mkdir(parents=True, exist_ok=True)

    any_inset = 0.18
    mask_inset = 0.22

    png_192 = _raster(192, lambda nx, ny: _sample_pwa(nx, ny, any_inset))
    png_512 = _raster(512, lambda nx, ny: _sample_pwa(nx, ny, any_inset))
    png_mask = _raster(512, lambda nx, ny: _sample_pwa(nx, ny, mask_inset))
    _write_png(ICONS / 'icon-192.png', 192, 192, png_192)
    _write_png(ICONS / 'icon-512.png', 512, 512, png_512)
    _write_png(ICONS / 'icon-maskable-512.png', 512, 512, png_mask)

    fav_pixels = _raster(32, _sample_mark)
    fav_png = ICONS / '_favicon-32.png'
    _write_png(fav_png, 32, 32, fav_pixels)
    _write_ico(ICONS / 'favicon.ico', fav_png.read_bytes(), 32)
    fav_png.unlink()

    print('Wrote icon-192.png, icon-512.png, icon-maskable-512.png, favicon.ico')


if __name__ == '__main__':
    main()
