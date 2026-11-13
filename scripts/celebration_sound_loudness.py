"""Celebration sounds: how loud each one really is (docs/CELEBRATION_SOUNDS_PLAN.md section 8).

Dev only, like zorp_gallery_snapshot.py: it needs Playwright and its Chromium, which stay out of requirements.txt, and exits 0
with a note when they are missing.

Renders every sound of static/js/sound-library.js offline (an OfflineAudioContext in headless Chromium, the real library),
K-weights it (ITU-R BS.1770, the weighting behind LUFS) and takes its loudest 400 ms and 100 ms windows. Today's answer tones and
Zorp's cues are rendered the same way (their notes copied from static/js/sound.js), so every number is comparable.

With --check it exits 1 when a sound leaves its band, all relative to the correct-answer tone measured in the same run:
  * no celebration sound is louder than that tone plus 1 dB (400 ms window);
  * the main sounds sit within 6 dB below that ceiling;
  * the layers (whoosh, sparkle, confetti, pop) sit 3 to 14 dB below it.

Run: python scripts/celebration_sound_loudness.py [--check]   (PB_CHROMIUM=<path to chrome> picks a browser)
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'static' / 'js' / 'sound-library.js'
LAYERS = ('whoosh', 'sparkle', 'confetti', 'pop')
CEILING_DB = 1.0
MAIN_SPAN_DB = 6.0
LAYER_BAND_DB = (3.0, 14.0)

PAGE = r"""async () => {
  const SR = 48000;
  function kweight(x) {
    const st = [[[1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585]],
      [[1, -2, 1], [1, -1.99004745483398, 0.99007225036621]]];
    let y = Float64Array.from(x);
    for (const [b, a] of st) {
      const z = new Float64Array(y.length); let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
      for (let i = 0; i < y.length; i++) { const v = b[0] * y[i] + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2; x2 = x1; x1 = y[i]; y2 = y1; y1 = v; z[i] = v; }
      y = z;
    }
    return y;
  }
  function measure(x) {
    const y = kweight(x);
    const win = (ms) => {
      const n = Math.round(SR * ms / 1000); let best = 0; let s = 0;
      for (let i = 0; i < y.length; i++) { s += y[i] * y[i]; if (i >= n) s -= y[i - n] * y[i - n]; if (i >= n - 1) best = Math.max(best, s / n); }
      return best > 0 ? -0.691 + 10 * Math.log10(best) : -99;
    };
    let pk = 0; for (const v of x) pk = Math.max(pk, Math.abs(v));
    return { m400: +win(400).toFixed(1), m100: +win(100).toFixed(1), peak: +(20 * Math.log10(pk || 1e-9)).toFixed(1) };
  }
  async function render(fn) {
    const ctx = new OfflineAudioContext(1, Math.round(SR * 2.4), SR);
    const g = ctx.createGain(); g.connect(ctx.destination);
    fn(ctx, g);
    return (await ctx.startRendering()).getChannelData(0);
  }
  // sound.js playTone and cueTone: from 0.0001 up to the peak in the attack, down to 0.0001 at the end
  function tone(ctx, out, f, ms, type, gain, delay, attack, f2) {
    const t = delay / 1000, end = t + ms / 1000; const o = ctx.createOscillator(); const a = ctx.createGain();
    o.type = type; o.frequency.setValueAtTime(f, t); if (f2 && f2 !== f) o.frequency.exponentialRampToValueAtTime(f2, end);
    a.gain.setValueAtTime(0.0001, t); a.gain.exponentialRampToValueAtTime(gain, t + (attack || 20) / 1000); a.gain.exponentialRampToValueAtTime(0.0001, end);
    o.connect(a); a.connect(out); o.start(t); o.stop(end + 0.04);
  }
  const REF = {
    'answer: correct': (c, g) => { tone(c, g, 523.25, 90, 'sine', 0.11, 0); tone(c, g, 659.25, 110, 'sine', 0.1, 70); },
    'answer: wrong': (c, g) => tone(c, g, 196, 160, 'triangle', 0.14, 0),
    'answer: soft': (c, g) => tone(c, g, 261.63, 140, 'sine', 0.08, 0),
    'answer: confetti arpeggio': (c, g) => [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => tone(c, g, f, 100, 'sine', 0.1, i * 90)),
    'zorp cue: jump': (c, g) => tone(c, g, 330, 160, 'sine', 0.06, 0, 20, 660),
    'zorp cue: tada': (c, g) => { [523.25, 659.25, 783.99].forEach((f, i) => tone(c, g, f, 160, 'sine', 0.06, i * 70, 12)); },
  };
  const rows = [];
  for (const [k, fn] of Object.entries(REF)) rows.push(Object.assign({ name: k, ref: true }, measure(await render(fn))));
  for (const n of window.pbSoundLib.names) {
    for (const step of (n === 'week' ? [0, 2] : [0])) {
      const x = await render((c, g) => window.pbSoundLib.play(n, c, g, 1, { step }));
      rows.push(Object.assign({ name: n, step: n === 'week' ? step : null, ms: window.pbSoundLib.meta(n).ms }, measure(x)));
    }
  }
  return rows;
}"""


def measure():
    try:
        from playwright.sync_api import sync_playwright  # lazy: dev only
    except ImportError:
        return None
    with sync_playwright() as p:
        exe = os.environ.get('PB_CHROMIUM')   # a Chromium of another Playwright version, when this one has none
        try:
            browser = p.chromium.launch(**({'executable_path': exe, 'args': ['--no-sandbox']} if exe else {}))
        except Exception as exc:  # no Chromium for this Playwright
            print(f'Chromium did not start ({str(exc).splitlines()[0][:120]}); run `playwright install chromium`.')
            return None
        page = browser.new_page()
        page.goto('about:blank')
        page.add_script_tag(content=LIB.read_text(encoding='utf-8'))
        rows = page.evaluate(PAGE)
        browser.close()
    return rows


def check(rows):
    ref = next(r for r in rows if r['name'] == 'answer: correct')['m400']
    ceiling = ref + CEILING_DB
    bad = []
    for r in rows:
        if r.get('ref'):
            continue
        label = r['name'] + (f" {r['step']}" if r.get('step') is not None else '')
        if r['name'] in LAYERS:
            lo, hi = ceiling - LAYER_BAND_DB[1], ceiling - LAYER_BAND_DB[0]
        else:
            lo, hi = ceiling - MAIN_SPAN_DB, ceiling
        if not lo <= r['m400'] <= hi:
            bad.append(f'{label}: {r["m400"]} outside {lo:.1f} to {hi:.1f}')
    return ceiling, bad


def main(argv):
    rows = measure()
    if rows is None:
        print('Playwright (or its Chromium) is not installed: loudness not measured. It is a dev-only tool (pip install playwright).')
        return 0
    print(f'{"sound":<28}{"400 ms":>8}{"100 ms":>8}{"peak dBFS":>11}   (K-weighted, LUFS-like)')
    for r in rows:
        label = r['name'] + (f" {r['step']}" if r.get('step') is not None else '')
        print(f'{label:<28}{r["m400"]:>8}{r["m100"]:>8}{r["peak"]:>11}' + (f'   {r["ms"]} ms' if r.get('ms') else ''))
    ceiling, bad = check(rows)
    print(f'\nCeiling (the correct-answer tone plus {CEILING_DB:g} dB): {ceiling:.1f}')
    if '--check' in argv:
        for b in bad:
            print('OUT OF BAND:', b)
        print('Loudness check passed.' if not bad else 'Loudness check FAILED.')
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
