'use strict';
/* E8 Phase 3: behavioural harness for views and the pinch-turn in static/js/zorp-motion.js
   (run by test_zorp_rig_smoke.py). Deterministic: no jsdom, no real timers. The runtime runs in a
   vm sandbox against a small fake DOM that is built from the REAL rendered markup
   (templates/partials/buddy.html, zorp_library.html) and the REAL island (models/zorp_rig.py), and
   every animation is a controllable fake: nothing finishes until a scenario says so.
   Usage: node zorp_rig_harness.js <zorp-motion.js> <fixture.json>
   fixture: { island, library, svgs: { front, sideL } } (HTML strings). */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const [, , scriptPath, fixturePath] = process.argv;
if (!scriptPath || !fixturePath) {
  console.error('usage: node zorp_rig_harness.js <zorp-motion.js> <fixture.json>');
  process.exit(2);
}
const fx = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
const eq = (a, b, msg) => assert.strictEqual(JSON.stringify(a), JSON.stringify(b), msg);
const flush = async () => { for (let i = 0; i < 6; i += 1) await new Promise((r) => setImmediate(r)); };

class El {
  constructor(tag, attrs) {
    this.tagName = tag;
    this.attrs = {};
    this.childNodes = [];
    this.parentNode = null;
    this.style = {};
    const self = this;
    this._cls = [];
    this.classList = {
      contains: (c) => self._cls.indexOf(c) !== -1,
      add: (c) => { if (self._cls.indexOf(c) === -1) self._cls.push(c); },
      remove: (c) => { self._cls = self._cls.filter((x) => x !== c); },
      toggle: (c, on) => { if (on) self.classList.add(c); else self.classList.remove(c); },
    };
    Object.keys(attrs || {}).forEach((k) => this.setAttribute(k, attrs[k]));
  }
  get firstChild() { return this.childNodes[0] || null; }
  get firstElementChild() { return this.childNodes[0] || null; }
  setAttribute(k, v) {
    this.attrs[k] = String(v);
    if (k === 'class') this._cls = String(v).split(/\s+/).filter(Boolean);
    if (k === 'style') String(v).split(';').forEach((d) => { const i = d.indexOf(':'); if (i > 0) this.style[d.slice(0, i).trim()] = d.slice(i + 1).trim(); });
  }
  getAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null; }
  removeAttribute(k) { delete this.attrs[k]; }
  hasAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); }
  appendChild(c) { if (c.parentNode) c.parentNode.removeChild(c); c.parentNode = this; this.childNodes.push(c); return c; }
  removeChild(c) { this.childNodes = this.childNodes.filter((x) => x !== c); c.parentNode = null; return c; }
  cloneNode(deep) {
    const n = new El(this.tagName, this.attrs);
    Object.assign(n.style, this.style);
    if (deep) this.childNodes.forEach((c) => n.appendChild(c.cloneNode(true)));
    return n;
  }
  _compound(sel) {
    const m = /^([a-z]+)?((?:\.[\w-]+)*)((?:\[[^\]]+\])*)$/.exec(sel);
    assert(m, 'unsupported selector ' + sel);
    if (m[1] && m[1] !== this.tagName) return false;
    const classes = m[2] ? m[2].split('.').filter(Boolean) : [];
    if (!classes.every((c) => this._cls.indexOf(c) !== -1)) return false;
    const attrs = m[3] ? m[3].match(/\[[^\]]+\]/g) : [];
    return attrs.every((a) => {
      const am = /^\[([\w-]+)(?:="([^"]*)")?\]$/.exec(a);
      return am && (am[2] === undefined ? this.hasAttribute(am[1]) : this.getAttribute(am[1]) === am[2]);
    });
  }
  matches(sel) { return this._compound(sel); }
  closest(sel) { for (let e = this; e; e = e.parentNode) if (e._compound && e._compound(sel)) return e; return null; }
  _descendants(out) { this.childNodes.forEach((c) => { out.push(c); c._descendants(out); }); return out; }
  querySelectorAll(sel) {
    const parts = sel.trim().split(/\s+/);
    return this._descendants([]).filter((e) => {
      if (!e._compound(parts[parts.length - 1])) return false;
      let anc = e.parentNode;
      for (let i = parts.length - 2; i >= 0; i -= 1) {
        while (anc && !anc._compound(parts[i])) anc = anc.parentNode;
        if (!anc) return false;
        anc = anc.parentNode;
      }
      return true;
    });
  }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
  getClientRects() { return [1]; }
  getBoundingClientRect() { return { width: 1, height: 1 }; }
  animate(frames, opts) { return makeAnim(this, frames, opts); }
  // structure signature (tag, class, path data): equal for a slot and the library part it was cloned from
  sig() { return this.tagName + '.' + this._cls.join('.') + '#' + (this.attrs.d || '') + '(' + this.childNodes.map((c) => c.sig()).join(',') + ')'; }
}

// ---- fake animations: nothing finishes or is cancelled unless a scenario (or the runtime) says so ----
let animations = [];
let commitMode = 'ok';   // ok | throws | missing
function makeAnim(el, frames, opts) {
  const a = { el, frames, opts: opts || {}, state: 'running', canceled: false, commits: 0, _p: null };
  Object.defineProperty(a, 'finished', {
    get() {
      if (!a._p) {
        a._p = new Promise((res, rej) => { a._res = res; a._rej = rej; });
        if (a.state === 'finished') a._res();
        else if (a.canceled) a._rej(new Error('AbortError'));
      }
      return a._p;
    },
  });
  a.finish = () => { if (a.canceled) return; a.state = 'finished'; if (a._res) a._res(); };
  a.cancel = () => { if (a.state === 'finished' && !a.commits && !a.opts.fill) return; a.canceled = true; a.state = 'idle'; if (a._rej) a._rej(new Error('AbortError')); };
  if (commitMode !== 'missing') {
    a.commitStyles = () => {
      if (commitMode === 'throws') throw new Error('InvalidStateError');
      a.commits += 1;
      const last = frames[frames.length - 1];
      Object.keys(last).forEach((k) => { if (k !== 'offset' && k !== 'easing') el.style[k] = last[k]; });
    };
  }
  animations.push(a);
  return a;
}
const live = () => animations.filter((a) => !a.canceled && a.state !== 'finished');
const finishAll = async () => { for (let i = 0; i < 4; i += 1) { animations.forEach((a) => { if (!a.canceled) a.finish(); }); await flush(); } };

// ---- fixture -> fake DOM ----
function parse(html) {
  const root = new El('root');
  const stack = [root];
  const re = /<(\/?)([a-zA-Z][\w-]*)((?:\s+[^\s=>/]+(?:="[^"]*")?)*)\s*(\/?)>/g;
  let m;
  while ((m = re.exec(html))) {
    if (m[1]) { stack.pop(); continue; }
    const attrs = {};
    (m[3].match(/[^\s=]+(?:="[^"]*")?/g) || []).forEach((a) => {
      const i = a.indexOf('=');
      attrs[i < 0 ? a : a.slice(0, i)] = i < 0 ? '' : a.slice(i + 2, -1);
    });
    const el = new El(m[2], attrs);
    stack[stack.length - 1].appendChild(el);
    if (!m[4]) stack.push(el);
  }
  return root;
}

function mascot(which, face) {
  const html = fx.svgs[which];
  const svg = parse(html).childNodes[0];
  const host = new El('span', { class: 'study-buddy-face', 'data-buddy-face': '', 'data-face': face || 'nudge' });
  host.appendChild(svg);
  return { host, svg, slot: (k) => svg.querySelector('.zorp-slot--' + k), part: (sel) => svg.querySelector(sel) };
}

function load(motion, env) {
  animations = [];
  commitMode = (env && env.commit) || 'ok';
  const island = new El('script', { id: 'pb-zorp-rig' });
  island.textContent = fx.island;
  const tpl = new El('template', { id: 'pb-zorp-parts' });
  tpl.content = parse(fx.library).childNodes[0];
  const htmlEl = new El('html');
  if (motion !== 'system') htmlEl.setAttribute('data-motion', motion);
  const byId = { 'pb-zorp-rig': island, 'pb-zorp-parts': tpl };
  class KE { }
  if (!env || env.composite !== false) KE.prototype.composite = 'replace';
  const sandbox = {
    document: {
      readyState: 'complete', hidden: false, body: new El('body'), documentElement: htmlEl,
      getElementById: (id) => byId[id] || null, addEventListener() {},
    },
    Element: El, Animation: class { get finished() { return null; } },
    KeyframeEffect: KE,
    CSS: { supports: () => !env || env.props !== false },
    setTimeout, clearTimeout, Promise, Object, Date, Math, JSON, console, Array, String,
  };
  sandbox.window = sandbox;
  sandbox.matchMedia = () => ({ matches: false, addEventListener() {} });
  vm.runInNewContext(fs.readFileSync(scriptPath, 'utf8'), sandbox);
  return { z: sandbox.pbZorp, html: htmlEl };
}

const PARTS = {
  plate: '.zorp-plate', eyeL: '.zorp-slot--eyeL', eyeR: '.zorp-slot--eyeR', brows: '.zorp-slot--brows',
  mouth: '.zorp-slot--mouth', cheeks: '.zorp-slot--cheeks', fxFace: '.zorp-slot--fx-face',
  antL: '.buddy-antenna--l', antR: '.buddy-antenna--r', hl: '.zorp-highlight', footL: '.buddy-foot--l',
  footR: '.buddy-foot--r', armL: '.buddy-arm--l', armR: '.buddy-arm--r', armLf: '.buddy-arm--l-front',
  armRf: '.buddy-arm--r-front',
};
const libPart = (channel, id) => parse(fx.library).querySelector('[data-part="' + channel + ':' + id + '"]');
const drawn = (m, slot, channel, id) => {
  const want = libPart(channel, id).childNodes.map((c) => c.sig()).join('|');
  return m.slot(slot).childNodes.map((c) => c.sig()).join('|') === want;
};
// resting state of the whole rig as { part: 'hidden' | 'translate | scale' }, identity written as ''
const restOf = (m) => {
  const out = {};
  Object.keys(PARTS).forEach((k) => {
    const st = m.part(PARTS[k]).style;
    const id = (v) => (!v || v === '0px 0px' || v === '1 1' || v === '1' ? '' : v);
    out[k] = st.display === 'none' ? 'hidden' : (id(st.translate) + ' | ' + id(st.scale));
  });
  out.flip = (m.part('.zorp-flip').style.scale || '').replace(/^1( 1)?$/, '');
  return out;
};
const sideR = { plate: '7.6px 0px | 0.66 1', eyeL: 'hidden', eyeR: '6.5px 0px | ', armL: 'hidden', armR: 'hidden', armRf: '-19.4px 2px | ', armLf: 'hidden' };

let finished = false;
setTimeout(() => { console.error('harness timed out (a scenario is waiting for an animation nobody finishes)'); process.exit(1); }, 30000).unref();
process.on('exit', () => { if (!finished) { console.error('harness ended before every scenario ran'); process.exitCode = 1; } });
const results = [];
async function scenario(name, fn) {
  try { await fn(); results.push([name, true]); console.log('OK: ' + name); }
  catch (e) { results.push([name, false]); console.error('FAIL: ' + name + '\n  ' + (e && e.stack || e)); }
}
const compositeKeys = () => animations.filter((a) => a.opts.composite).length;

(async () => {
  await scenario('views come from the island, front first', () => {
    const { z } = load('system');
    eq(z.views, ['front', 'three-quarter', 'side', 'back', 'back-glance']);
    assert.strictEqual(typeof z.turn, 'function');
  });

  await scenario('bind reads the server-drawn view and facing', () => {
    const { z } = load('system');
    const m = mascot('sideL');
    z.bind(m.host);
    eq(z.viewOf(m.host), { view: 'side', facing: 'l' });
    const f = mascot('front');
    z.bind(f.host);
    eq(z.viewOf(f.host), { view: 'front', facing: 'r' });
  });

  for (const level of ['reduced', 'off']) {
    await scenario('turn() under ' + level + ' makes no animation calls and follows the matrix', async () => {
      const { z } = load(level);
      const m = mascot('front');
      z.bind(m.host);
      assert.strictEqual(await z.turn('side', 'r', { el: m.host }), false, 'not required: stays front');
      assert.strictEqual(await z.turn('three-quarter', 'l', { el: m.host }), false);
      eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
      if (level === 'off') {
        assert.strictEqual(await z.turn('side', 'r', { el: m.host, required: true }), false, 'off never leaves front');
      } else {
        assert.strictEqual(await z.turn('side', 'l', { el: m.host, required: true }), true, 'required: instant swap');
        eq(z.viewOf(m.host), { view: 'side', facing: 'l' });
        assert.strictEqual(m.part('.zorp-flip').style.scale, '-1 1');
        assert.strictEqual(m.part('.zorp-slot--eyeL').style.display, 'none');
        assert.strictEqual(await z.turn('front', 'r', { el: m.host }), true, 'front is always reachable');
        eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
        eq(restOf(m).eyeL, ' | ');
      }
      assert.strictEqual(animations.length, 0, level + ' must not call animate');
    });
  }

  await scenario('side-point: reduced swaps the view instantly and stop() restores it; off stays front', async () => {
    const r = load('reduced');
    const m = mascot('front');
    r.z.bind(m.host);
    const p = r.z.play('side-point', { el: m.host });
    eq(r.z.viewOf(m.host), { view: 'side', facing: 'r' }, 'reduced: the clip needs the side view');
    assert.strictEqual(m.host.getAttribute('data-face'), 'curious');
    r.z.play('cheer', { el: m.host });   // any newer clip calls stop(): the excursion must not stick
    eq(r.z.viewOf(m.host), { view: 'front', facing: 'r' });
    assert.strictEqual(m.part('.zorp-slot--eyeL').style.display, '');
    assert.strictEqual(animations.length, 0);
    void p;
    const o = load('off');
    const n = mascot('front');
    o.z.bind(n.host);
    const op = o.z.play('side-point', { el: n.host });
    eq(o.z.viewOf(n.host), { view: 'front', facing: 'r' }, 'off: never leaves front, not even for the hold');
    assert.strictEqual(n.part('.zorp-flip').style.scale || '', '');
    await op;
    eq(o.z.viewOf(n.host), { view: 'front', facing: 'r' });
    assert.strictEqual(animations.length, 0, 'off: face swap only');
  });

  await scenario('full turn: pinch animations, commit at 50%, commitStyles at the end, resting state written', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    const done = z.turn('side', 'r', { el: m.host });
    await flush();
    const flip = animations.find((a) => a.el === m.part('.zorp-flip') && a.frames[0].scale);
    assert.ok(flip && flip.opts.fill === 'forwards', 'flip tween holds its end value');
    eq(flip.frames.map((f) => f.scale), ['1 1', '1 1', '0.15 1', '0.15 1', '1.04 1', '1 1']);
    eq(flip.frames.map((f) => f.offset), [0, 0.15, 0.45, 0.55, 0.8, 1]);
    assert.strictEqual(animations.filter((a) => a.opts.duration === 300).length >= 8, true, 'about 300 ms');
    const clock = animations.find((a) => a.opts.duration === 150);
    assert.ok(clock, 'the 50% commit clock');
    const dip = animations.find((a) => a.el === m.part('.buddy-root'));
    assert.ok(dip && /scale\(1\.04,0\.96\)/.test(dip.frames[1].transform), 'anticipation dip');
    const ants = animations.filter((a) => a.el === m.part('.buddy-antenna--l') || a.el === m.part('.buddy-antenna--r'));
    assert.ok(ants.some((a) => a.opts.delay === 60), 'antennae lag by 60 ms');
    assert.ok(compositeKeys() > 0 && animations.filter((a) => a.opts.composite).every((a) => a.opts.composite === 'add'),
      'overlays are composite:add when the browser has it');
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' }, 'nothing committed before 50%');
    assert.strictEqual(m.part('.zorp-slot--eyeL').style.display || '', '');
    clock.finish();
    await flush();
    eq(z.viewOf(m.host), { view: 'side', facing: 'r' }, 'committed at 50%');
    assert.strictEqual(m.part('.zorp-slot--eyeL').style.display, 'none', 'far eye hidden');
    assert.strictEqual(m.part('.buddy-arm--r-front').style.display, 'inline', 'near arm moves to the front layer');
    assert.ok(drawn(m, 'eyeR', 'eyes', 'side'), 'the side eye is drawn');
    assert.ok(drawn(m, 'mouth', 'mouth', 'side-smile'), 'the side mouth is drawn');
    await finishAll();
    assert.strictEqual(await done, true);
    const held = animations.filter((a) => a.opts.fill === 'forwards');
    assert.ok(held.length >= 8 && held.every((a) => a.commits === 1 && a.canceled), 'every held tween is committed, then cancelled');
    assert.strictEqual(live().length, 0, 'no animation left running');
    const rest = restOf(m);
    Object.keys(sideR).forEach((k) => assert.strictEqual(rest[k], sideR[k], k));
    assert.strictEqual(rest.flip, '');
  });

  await scenario('turning back to front leaves no identity translate/scale inline (commitStyles residue is tidied)', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    let done = z.turn('side', 'r', { el: m.host });
    await flush(); await finishAll();
    assert.strictEqual(await done, true);
    done = z.turn('front', 'r', { el: m.host });
    await flush(); await finishAll();
    assert.strictEqual(await done, true);
    ['.zorp-flip', '.zorp-plate', '.zorp-slot--mouth', '.buddy-antenna--l', '.zorp-highlight'].forEach((sel) => {
      assert.ok(!m.part(sel).style.translate && !m.part(sel).style.scale, sel + ' carries "' + m.part(sel).style.translate + '" "' + m.part(sel).style.scale + '"');
    });
  });

  for (const mode of ['throws', 'missing']) {
    await scenario('commitStyles ' + mode + ': the same resting state is written by the fallback', async () => {
      const { z } = load('system', { commit: mode });
      const m = mascot('front');
      z.bind(m.host);
      const done = z.turn('side', 'l', { el: m.host });
      await flush();
      await finishAll();
      assert.strictEqual(await done, true);
      eq(z.viewOf(m.host), { view: 'side', facing: 'l' });
      const rest = restOf(m);
      Object.keys(sideR).forEach((k) => assert.strictEqual(rest[k], sideR[k], k));
      assert.strictEqual(rest.flip, '-1 1');
      assert.strictEqual(live().length, 0);
    });
  }

  await scenario('composite fallback: without composite support nothing passes it and clips still run', async () => {
    const { z } = load('system', { composite: false });
    const m = mascot('sideL');
    z.bind(m.host);
    const p = z.play('wave', { el: m.host });
    await flush();
    assert.ok(animations.length >= 2, 'the clip runs');
    assert.strictEqual(compositeKeys(), 0, 'no composite option is passed');
    await finishAll();
    await p;
    const turned = z.turn('front', 'r', { el: m.host });
    await flush();
    assert.strictEqual(compositeKeys(), 0);
    await finishAll();
    assert.strictEqual(await turned, true, 'turns work without composite');
  });

  await scenario('clips are layered with composite:add away from the front view only; front is unchanged', async () => {
    const { z } = load('system');
    const f = mascot('front');
    z.bind(f.host);
    z.play('cheer', { el: f.host });
    assert.strictEqual(compositeKeys(), 0, 'front view: clips are exactly as before Phase 3');
    const armsFront = animations.filter((a) => (a.el._cls.indexOf('buddy-arm--l') !== -1 || a.el._cls.indexOf('buddy-arm--l-front') !== -1));
    assert.strictEqual(armsFront.length, 2, 'both members of the arm pair are animated');
    eq(armsFront[0].frames, armsFront[1].frames, 'with identical keyframes');
    assert.ok(armsFront.some((a) => a.frames[1].transform === 'rotate(115deg)'), 'existing cheer angle');
    animations = [];
    const s = mascot('sideL');
    z.bind(s.host);
    z.play('cheer', { el: s.host });
    const clip = animations.filter((a) => a.opts.duration === 700);   // the cheer tracks (not the 80-120 ms part swaps)
    assert.ok(clip.length >= 4 && clip.every((a) => a.opts.composite === 'add'), 'side view: clips add on the resting view');
  });

  await scenario('stop() before the commit restores the view it was leaving, with nothing left running', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    const done = z.turn('side', 'r', { el: m.host });
    await flush();
    const started = animations.slice();
    z.play('blink', { el: m.host });   // any newer clip calls stop()
    await flush();
    assert.strictEqual(await done, false, 'the cut-short turn resolves false');
    assert.ok(started.every((a) => a.canceled), 'every turn animation is cancelled');
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
    const rest = restOf(m);
    Object.keys(PARTS).forEach((k) => assert.strictEqual(rest[k], k === 'armLf' || k === 'armRf' ? 'hidden' : ' | ', k));
    assert.strictEqual(m.part('.buddy-arm--r-front').style.display, 'none');
  });

  await scenario('turn back to the view a turn is still leaving cancels that turn (no stale commit)', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    const away = z.turn('side', 'r', { el: m.host });
    await flush();
    const started = animations.slice();
    assert.strictEqual(await z.turn('front', 'r', { el: m.host }), true);
    assert.strictEqual(await away, false, 'the turn to side is cut short');
    assert.ok(started.every((a) => a.canceled), 'nothing from the cancelled turn keeps running');
    await finishAll();
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
    assert.strictEqual(m.part('.buddy-arm--r-front').style.display, 'none');
  });

  await scenario('stop() after the commit settles on the committed view', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    const done = z.turn('side', 'l', { el: m.host });
    await flush();
    const started = animations.slice();
    animations.find((a) => a.opts.duration === 150).finish();
    await flush();
    z.play('blink', { el: m.host });
    await flush();
    assert.strictEqual(await done, false);
    assert.ok(started.filter((a) => a.state !== 'finished').every((a) => a.canceled), 'everything still running is cancelled');
    eq(z.viewOf(m.host), { view: 'side', facing: 'l' });
    const rest = restOf(m);
    Object.keys(sideR).forEach((k) => assert.strictEqual(rest[k], sideR[k], k));
    assert.strictEqual(rest.flip, '-1 1');
  });

  await scenario('side-point in full motion: turns in, points, turns back; stop() mid-way restores the origin', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    const done = z.play('side-point', { el: m.host });
    await flush();
    animations.find((a) => a.opts.duration === 150).finish();
    await flush();
    eq(z.viewOf(m.host), { view: 'side', facing: 'r' });
    z.play('blink', { el: m.host });
    await flush();
    assert.strictEqual(await done, false);
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' }, 'the excursion is undone');
    assert.strictEqual(m.part('.zorp-slot--eyeL').style.display, '');
    assert.ok(drawn(m, 'eyeR', 'eyes', 'open') && drawn(m, 'mouth', 'mouth', 'smile'), 'front variants are back');
    // cut short during the point itself (after the first turn has settled): still restored
    const z3 = load('system');
    const q = mascot('front');
    z3.z.bind(q.host);
    const d3 = z3.z.play('side-point', { el: q.host });
    const pointing = () => live().some((a) => /rotate/.test(JSON.stringify(a.frames)));
    for (let i = 0; i < 6 && !(z3.z.viewOf(q.host).view === 'side' && pointing()); i += 1) {
      live().forEach((a) => a.finish());
      await flush();
    }
    eq(z3.z.viewOf(q.host), { view: 'side', facing: 'r' });
    assert.ok(pointing(), 'the point clip is running');
    z3.z.play('blink', { el: q.host });
    await flush();
    assert.strictEqual(await d3, false);
    eq(z3.z.viewOf(q.host), { view: 'front', facing: 'r' }, 'stop() during the point undoes the excursion');
    // and run to the end: three phases (turn, point, turn back) end in the starting view
    const z2 = load('system');
    const n = mascot('front');
    z2.z.bind(n.host);
    const d2 = z2.z.play('point', { el: n.host, view: 'side' });
    for (let i = 0; i < 12; i += 1) { await finishAll(); }
    assert.strictEqual(await d2, true);
    eq(z2.z.viewOf(n.host), { view: 'front', facing: 'r' });
    assert.strictEqual(live().length, 0);
  });

  await scenario('expressions and blink keep working in every view; parts hidden in a view do not blink', async () => {
    const { z } = load('system');
    const m = mascot('sideL');
    z.bind(m.host);
    assert.strictEqual(z.setExpression('happy', { el: m.host }), true);
    assert.ok(drawn(m, 'eyeR', 'eyes', 'smile-arc'), 'arc eyes have no side art and stay');
    assert.ok(drawn(m, 'mouth', 'mouth', 'side-smile'), 'the smile is drawn as its side variant');
    assert.ok(drawn(m, 'brows', 'brows', 'side') && drawn(m, 'cheeks', 'cheeks', 'side-rosy'));
    assert.strictEqual(z.setExpression('wow', { el: m.host }), true);
    assert.ok(drawn(m, 'mouth', 'mouth', 'side-o'));
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'wow');
    const back = z.turn('front', 'r', { el: m.host });   // full motion: animated
    await flush();
    await finishAll();
    await back;
    assert.ok(drawn(m, 'mouth', 'mouth', 'wow') && drawn(m, 'eyeL', 'eyes', 'wide'), 'front art returns');
    const s = mascot('sideL');
    z.bind(s.host);
    animations = [];
    z.play('blink', { el: s.host });
    const pupils = animations.map((a) => a.el);
    assert.strictEqual(pupils.length, 1, 'only the visible eye blinks in profile');
    assert.ok(s.slot('eyeR').querySelectorAll('.buddy-pupil').indexOf(pupils[0]) !== -1);
    animations = [];
    const f = mascot('front');
    z.bind(f.host);
    z.play('blink', { el: f.host });
    assert.strictEqual(animations.length, 2, 'both eyes blink from the front');
  });

  await scenario('facing: the front view has no facing; unknown views and browsers without the properties refuse', async () => {
    const { z } = load('reduced');
    const m = mascot('front');
    z.bind(m.host);
    assert.strictEqual(await z.turn('front', 'l', { el: m.host }), true, 'front already');
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
    assert.strictEqual(await z.turn('sideways', 'r', { el: m.host, required: true }), false);
    assert.strictEqual(await z.turn('back', 'l', { el: m.host, required: true }), true);
    eq(z.viewOf(m.host), { view: 'back', facing: 'l' });
    assert.strictEqual(m.part('.zorp-highlight').style.translate, '20px 0px');
    const old = load('system', { props: false });
    const o = mascot('front');
    old.z.bind(o.host);
    assert.strictEqual(await old.z.turn('side', 'r', { el: o.host }), false, 'no translate/scale support: stays front');
    assert.strictEqual(animations.length, 0);
  });

  finished = true;
  const failed = results.filter((r) => !r[1]);
  if (failed.length) { console.error(`\n${failed.length}/${results.length} zorp rig scenarios FAILED`); process.exit(1); }
  console.log(`\nAll ${results.length} zorp rig scenarios passed.`);
  process.exit(0);
})();
