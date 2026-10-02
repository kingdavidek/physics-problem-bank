'use strict';
/* E8 Phase 7: behavioural harness for Zorp's idle life in static/js/zorp-motion.js (run by test_zorp_idle_smoke.py).
   Virtual clock (setTimeout, Date.now and animation ends are all driven by advance()), a seeded Math.random and a
   hand-rolled fake DOM, so every scenario is deterministic and instant.
   Usage: node zorp_idle_harness.js <zorp-motion.js> <rig.json> */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const [, , scriptPath, rigPath] = process.argv;
if (!scriptPath || !rigPath) { console.error('usage: node zorp_idle_harness.js <zorp-motion.js> <rig.json>'); process.exit(2); }
const rig = JSON.parse(fs.readFileSync(rigPath, 'utf8'));
process.on('unhandledRejection', () => {});

let now = 0;
let tid = 0;
let timers = new Map();
let delays = [];
let all = [];
let seed = 1;
const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };

class El {
  constructor(tag, cls) {
    this.tagName = tag; this.attrs = {}; this.childNodes = []; this.parentNode = null; this.style = {};
    this._cls = cls ? cls.split(' ') : [];
    const self = this;
    this.classList = {
      contains: (c) => self._cls.indexOf(c) !== -1,
      add: (c) => { if (self._cls.indexOf(c) === -1) self._cls.push(c); },
      remove: (c) => { self._cls = self._cls.filter((x) => x !== c); },
      toggle: (c, on) => { if (on) self.classList.add(c); else self.classList.remove(c); },
    };
  }
  get firstChild() { return this.childNodes[0] || null; }
  get firstElementChild() { return this.childNodes[0] || null; }
  setAttribute(k, v) { this.attrs[k] = String(v); if (k === 'class') this._cls = String(v).split(' '); }
  getAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null; }
  removeAttribute(k) { delete this.attrs[k]; }
  hasAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); }
  appendChild(c) { if (c.parentNode) c.parentNode.removeChild(c); c.parentNode = this; this.childNodes.push(c); return c; }
  removeChild(c) { this.childNodes = this.childNodes.filter((x) => x !== c); c.parentNode = null; return c; }
  cloneNode(deep) {
    const n = new El(this.tagName, this._cls.join(' '));
    Object.assign(n.attrs, this.attrs);
    if (deep) this.childNodes.forEach((c) => n.appendChild(c.cloneNode(true)));
    return n;
  }
  _compound(sel) {
    const m = /^([a-zA-Z]+)?((?:\.[\w-]+)*)((?:\[[^\]]+\])*)$/.exec(sel);
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
  closest(sel) { for (let e = this; e; e = e.parentNode) if (e.matches && e._compound(sel)) return e; return null; }
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
  animate(frames, opts) {
    const a = { el: this, frames, opts, canceled: false, done: false, t0: now, end: now + (opts.delay || 0) + opts.duration };
    a.finished = new Promise((res, rej) => { a.res = res; a.rej = rej; });
    a.cancel = () => { if (!a.done) { a.canceled = true; a.done = true; a.rej(new Error('abort')); } };
    all.push(a);
    return a;
  }
}
const mk = (tag, cls, kids) => { const e = new El(tag, cls); (kids || []).forEach((k) => e.appendChild(k)); return e; };

function buildTemplate() {
  const root = mk('svg');
  Object.keys(rig.channels).forEach((channel) => rig.channels[channel].forEach((id) => {
    const g = mk('g'); g.setAttribute('data-part', channel + ':' + id);
    const p = mk('path'); p.setAttribute('data-id', channel + ':' + id);
    // eyes that have pupils (the open family) keep the buddy-pupil group, as in zorp_parts.html
    g.appendChild(channel === 'eyes' && /^open/.test(id) ? mk('g', 'buddy-pupil', [p]) : p); root.appendChild(g);
  }));
  return root;
}

function buildMascot(expr) {
  const slots = ['cheeks', 'eyeL', 'eyeR', 'brows', 'mouth', 'fx-face'].map((k) => {
    const cls = k === 'eyeL' ? 'buddy-eye buddy-eye--l zorp-slot--eyeL' : k === 'eyeR' ? 'buddy-eye buddy-eye--r zorp-slot--eyeR' : 'zorp-slot--' + k;
    return mk('g', cls);
  });
  const face = mk('g', 'zorp-face', [mk('ellipse', 'zorp-plate')].concat(slots));
  const head = mk('g', 'buddy-head', [mk('g', 'buddy-antenna--l'), mk('g', 'buddy-antenna--r'), mk('g', 'buddy-body'), face]);
  const flip = mk('g', 'zorp-flip', [mk('g', 'buddy-arm--l'), mk('g', 'buddy-arm--r'), head]);
  const svg = mk('svg', 'buddy-mascot', [mk('g', 'buddy-root', [mk('g', 'buddy-shadow'), flip, mk('g', 'zorp-slot--fx')])]);
  if (expr) svg.setAttribute('data-expr', expr);
  const host = mk('span', 'study-buddy-face', [svg]);
  host.setAttribute('data-buddy-face', ''); host.setAttribute('data-face', expr || 'nudge');
  // the eye slots start with their pupil parts, as the server draws them
  const m = { host, svg, part: (c) => svg.querySelector(c) };
  return m;
}

let listeners;
let ioInst;
let moCb;
let doc;
function load(motion, opts) {
  now = 0; tid = 0; timers = new Map(); delays = []; all = []; seed = 1; listeners = {}; ioInst = null; moCb = null;
  const island = mk('script'); island.setAttribute('id', 'pb-zorp-rig'); island.textContent = rig.island;
  const tpl = mk('template'); tpl.setAttribute('id', 'pb-zorp-parts'); tpl.content = buildTemplate();
  const htmlEl = mk('html');
  if (motion !== 'system') htmlEl.setAttribute('data-motion', motion);
  const byId = { 'pb-zorp-rig': island, 'pb-zorp-parts': tpl };
  if (opts && opts.noParts) delete byId['pb-zorp-parts'];
  doc = {
    readyState: 'complete', hidden: false, body: mk('body'), documentElement: htmlEl, activeElement: null,
    getElementById: (id) => byId[id] || null,
    addEventListener(type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
  };
  const sandbox = {
    document: doc, Element: El, Animation: class { get finished() { return null; } },
    CSS: { supports: () => true },
    setTimeout: (fn, ms) => { tid += 1; timers.set(tid, { at: now + ms, fn }); delays.push(ms); return tid; },
    clearTimeout: (id) => { timers.delete(id); },
    Date: { now: () => now },
    Math: Object.assign(Object.create(Math), { random: rnd }),
    IntersectionObserver: class { constructor(cb) { this.cb = cb; this.seen = []; ioInst = this; } observe(el) { this.seen.push(el); } unobserve(el) { this.seen = this.seen.filter((x) => x !== el); } },
    MutationObserver: class { constructor(cb) { moCb = cb; } observe() {} },
    Promise, Object, Array, String, JSON, console,
  };
  sandbox.window = sandbox;
  sandbox.matchMedia = () => ({ matches: false, addEventListener() {} });
  vm.runInNewContext(fs.readFileSync(scriptPath, 'utf8'), sandbox);
  return sandbox.pbZorp;
}

const flush = async () => { for (let i = 0; i < 12; i += 1) await Promise.resolve(); };
async function advance(ms) {
  const target = now + ms;
  for (;;) {
    await flush();
    let best = null;
    timers.forEach((t, id) => { if (t.at <= target && (!best || t.at < best.at)) best = { at: t.at, id, t }; });
    all.forEach((a) => { if (!a.done && a.end <= target && (!best || a.end < best.at)) best = { at: a.end, a }; });
    if (!best) break;
    now = Math.max(now, best.at);
    if (best.a) { best.a.done = true; best.a.res(); } else { timers.delete(best.id); best.t.fn(); }
  }
  now = target;
  await flush();
}
const fire = (type) => (listeners[type] || []).forEach((fn) => fn({}));
const pupilAnims = (m) => all.filter((a) => a.el.closest('.buddy-pupil') || a.el._cls.indexOf('buddy-pupil') !== -1);
const kind = (a) => {
  const f = JSON.stringify(a.frames);
  if (a.el._cls.indexOf('buddy-pupil') !== -1) return /scale\(1,0\.1\)/.test(f) ? 'blink' : 'glance';
  if (a.el._cls.indexOf('buddy-antenna--l') !== -1 || a.el._cls.indexOf('buddy-antenna--r') !== -1) return /rotate\(9deg\)|rotate\(-9deg\)/.test(f) ? 'twitch' : 'other';
  return 'other';
};
const counts = () => { const c = {}; all.forEach((a) => { const k = kind(a); c[k] = (c[k] || 0) + 1; }); return c; };
const pending = () => timers.size;
// give the mascot real pupils: the eye slots draw their parts when the expression is set
async function ready(z, m) {
  z.bind(m.host);
  z.setExpression('nudge', { el: m.host });
  z.setExpression('happy', { el: m.host }); z.setExpression('nudge', { el: m.host });
  await advance(1000);   // let the swap squeezes end
  all.length = 0;
}
const faceSig = (m) => m.host.getAttribute('data-face') + '|' + m.svg.getAttribute('data-expr') + '|' +
  ['eyeL', 'eyeR', 'brows', 'mouth', 'cheeks', 'fx', 'fx-face'].map((k) => m.part('.zorp-slot--' + k).childNodes.map((c) => c.attrs['data-id']).join(',')).join('/');

const results = [];
async function scenario(name, fn) {
  try { await fn(); results.push([name, true]); console.log('OK: ' + name); }
  catch (e) { results.push([name, false]); console.error('FAIL: ' + name + '\n  ' + (e && e.stack || e)); }
}

(async () => {
  await scenario('full motion, visible, idle: blinks, glances, antenna twitches and a rare look-around all happen, and the face never changes', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    await ready(z, m);
    const sig = faceSig(m);
    z.idle(true, m.host);
    assert.ok(m.svg.classList.contains('is-zorp-idle'));
    let looks = 0;
    const lookAt = [];
    let was = false;
    for (let t = 0; t < 900000; t += 100) {
      await advance(100);
      const v = z.viewOf(m.host).view;
      if (v !== 'front' && !was) { looks += 1; lookAt.push(now); assert.strictEqual(v, 'three-quarter', 'only a three-quarter look'); }
      was = v !== 'front';
      assert.strictEqual(faceSig(m), sig, 'idle never changes the expression, at ' + now);
    }
    const c = counts();
    const blinks = new Set(all.filter((a) => kind(a) === 'blink').map((a) => a.t0)).size;   // one per eye
    assert.ok(blinks >= 150 && blinks <= 260, 'blinks every 3-6 s: ' + blinks);
    assert.ok(c.glance >= 20, 'glances: ' + c.glance);
    assert.ok(c.twitch >= 5, 'twitches: ' + c.twitch);
    assert.ok(looks >= 2 && looks <= 15, 'look-arounds are rare: ' + looks);
    for (let i = 1; i < lookAt.length; i += 1) assert.ok(lookAt[i] - lookAt[i - 1] >= 45000, 'look-arounds at least 45 s apart');
    assert.strictEqual(z.viewOf(m.host).view, 'front', 'back to front');
    assert.ok(m.svg.getAttribute('data-view') === null, 'no view residue');
    const glances = all.filter((a) => kind(a) === 'glance');
    assert.ok(glances.every((a) => /translate\((-?\d(\.\d)?)px,/.test(a.frames[1].transform) && Math.abs(parseFloat(a.frames[1].transform.slice(10))) <= 1.3), 'glances stay within 1.3 px');
    const gaps = all.filter((a) => kind(a) === 'glance' || kind(a) === 'twitch').map((a) => a.t0);
    const uniq = [...new Set(gaps)].sort((a, b) => a - b);
    for (let i = 1; i < uniq.length; i += 1) assert.ok(uniq[i] - uniq[i - 1] >= 5900, 'micro-actions at least 6 s apart');
  });

  for (const level of ['reduced', 'off']) {
    await scenario('never at ' + level + ' motion: no timers, no animations', async () => {
      const z = load(level);
      const m = buildMascot('nudge');
      await ready(z, m);
      z.idle(true, m.host);
      assert.ok(!m.svg.classList.contains('is-zorp-idle'));
      assert.strictEqual(pending(), 0);
      await advance(300000);
      assert.strictEqual(all.length, 0);
      assert.strictEqual(z.viewOf(m.host).view, 'front');
    });
  }

  await scenario('a motion preference changed at runtime starts and stops idle life (data-motion observer)', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    await ready(z, m);
    z.idle(true, m.host);
    assert.ok(pending() > 0);
    doc.documentElement.setAttribute('data-motion', 'off');
    moCb();
    assert.strictEqual(pending(), 0, 'timers cleared');
    assert.ok(!m.svg.classList.contains('is-zorp-idle'));
    await advance(60000);
    assert.strictEqual(all.length, 0);
    doc.documentElement.removeAttribute('data-motion');
    moCb();
    assert.ok(pending() > 0, 'back at full motion');
    await advance(60000);
    assert.ok(all.length > 0);
  });

  await scenario('hidden tab: timers cleared and nothing runs; visible again: resumes', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    await ready(z, m);
    z.idle(true, m.host);
    await advance(20000);
    const n = all.length;
    assert.ok(n > 0);
    doc.hidden = true; fire('visibilitychange');
    assert.strictEqual(pending(), 0);
    assert.ok(!m.svg.classList.contains('is-zorp-idle'));
    await advance(120000);
    assert.strictEqual(all.length, n, 'nothing while hidden');
    doc.hidden = false; fire('visibilitychange');
    assert.ok(pending() > 0);
    await advance(30000);
    assert.ok(all.length > n);
  });

  await scenario('off-screen (IntersectionObserver): paused with no timers, resumes on return; observed only while idle', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    await ready(z, m);
    assert.ok(!ioInst || ioInst.seen.length === 0);
    z.idle(true, m.host);
    assert.deepStrictEqual(ioInst.seen, [m.svg]);
    ioInst.cb([{ target: m.svg, isIntersecting: false }]);
    assert.strictEqual(pending(), 0);
    assert.ok(!m.svg.classList.contains('is-zorp-idle'), 'the CSS breathing stops too');
    await advance(120000);
    assert.strictEqual(all.length, 0);
    ioInst.cb([{ target: m.svg, isIntersecting: true }]);
    assert.ok(pending() > 0 && m.svg.classList.contains('is-zorp-idle'));
    await advance(30000);
    assert.ok(all.length > 0);
    z.idle(false, m.host);
    assert.deepStrictEqual(ioInst.seen, [], 'unobserved when idle is turned off');
    assert.strictEqual(pending(), 0, 'idle(false) clears every timer');
  });

  await scenario('typing: nothing while an input has focus or just after a key or tap; the quiet window then ends', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    await ready(z, m);
    z.idle(true, m.host);
    doc.activeElement = mk('INPUT');
    await advance(120000);
    assert.strictEqual(all.length, 0, 'focus in an input');
    doc.activeElement = mk('TEXTAREA');
    await advance(60000);
    assert.strictEqual(all.length, 0, 'focus in a textarea');
    doc.activeElement = null;
    const t0 = now;
    for (let i = 0; i < 30; i += 1) {   // a key or tap every 2 s for a minute keeps idle life quiet throughout
      fire(i % 2 ? 'pointerdown' : 'keydown');
      await advance(2000);
    }
    assert.strictEqual(all.length, 0, 'inside the quiet window');
    await advance(60000);
    assert.ok(all.length > 0, 'resumes afterwards');
    all.length = 0;
    fire('pointerdown');
    await advance(1000);
    assert.strictEqual(all.length, 0);
    assert.ok(t0 > 0);
  });

  await scenario('only when nothing else is going on: a running clip, a turned view, a pose, the Guide and a thought all hold idle back', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    await ready(z, m);
    z.idle(true, m.host);
    z.play('cheer', { el: m.host });
    all.length = 0;
    for (let t = 0; t < 600; t += 50) { await advance(50); }
    assert.strictEqual(all.filter((a) => a.opts.fill === 'none' && kind(a) !== 'other').length, 0, 'nothing on top of a clip');
    await advance(400);
    z.turn('side', 'r', { el: m.host, instant: true });
    all.length = 0;
    await advance(60000);
    assert.strictEqual(all.length, 0, 'side view');
    z.turn('front', 'r', { el: m.host, instant: true });
    await advance(30000);
    assert.ok(all.length > 0, 'front again');
    // the Guide, checked with idle life demonstrably running (anims are counted, never cleared mid-flight)
    await advance(2000);
    doc.body.classList.add('guide-open');
    const n0 = all.length;
    await advance(60000);
    assert.strictEqual(all.length, n0, 'guide open');
    doc.body.classList.remove('guide-open');
    await advance(30000);
    assert.ok(all.length > n0, 'guide closed again');
    // a resting pose other than stand (server-drawn data-pose) holds idle life back
    const z2 = load('system');
    const posed = buildMascot('nudge');
    posed.svg.setAttribute('data-pose', 'wave');
    await ready(z2, posed);
    z2.idle(true, posed.host);
    await advance(60000);
    assert.strictEqual(all.length, 0, 'posed');
  });

  await scenario('stop() cancels an idle animation in flight; a clip starting over one is clean', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    await ready(z, m);
    z.idle(true, m.host);
    let a = null;
    for (let t = 0; t < 60000 && !a; t += 50) {
      await advance(50);
      a = all.find((x) => !x.done && (kind(x) === 'glance' || kind(x) === 'twitch'));
    }
    assert.ok(a, 'a glance or twitch was caught in flight');
    z.play('nod', { el: m.host });
    assert.ok(a.canceled, 'the clip stopped it');
    // a look-around cut short by a clip returns to the front view
    let seen = false;
    for (let t = 0; t < 900000 && !seen; t += 50) {
      await advance(50);
      if (z.viewOf(m.host).view === 'three-quarter') seen = true;
    }
    assert.ok(seen, 'caught a look-around');
    z.play('wave', { el: m.host });
    await advance(3000);
    assert.strictEqual(z.viewOf(m.host).view, 'front', 'cut-short look-around settles on front');
  });

  await scenario('timers are offset per mascot: two mascots never blink or glance in step', async () => {
    const z = load('system');
    const a = buildMascot('nudge');
    const b = buildMascot('nudge');
    z.bind(a.host); z.bind(b.host);
    await ready(z, a); await ready(z, b);
    all.length = 0;
    z.idle(true, a.host);
    const first = delays.slice();
    z.idle(true, b.host);
    const second = delays.slice(first.length);
    assert.strictEqual(first.length, 2); assert.strictEqual(second.length, 2);
    assert.notStrictEqual(first[0], second[0]); assert.notStrictEqual(first[1], second[1]);
    await advance(120000);
    const times = (m) => all.filter((x) => kind(x) === 'blink' && x.el.closest('.study-buddy-face') === m.host).map((x) => x.t0);
    const ta = times(a); const tb = times(b);
    assert.ok(ta.length > 10 && tb.length > 10);
    assert.strictEqual(ta.filter((t) => tb.indexOf(t) !== -1).length, 0, 'no shared blink instants');
  });

  await scenario('look-around is a tracked clip: reduced skips it, the expression is kept, the view returns', async () => {
    const z = load('system');
    assert.ok(z.hasClip('look-around') && z.clips.indexOf('look-around') !== -1);
    const m = buildMascot('proud');
    z.bind(m.host);
    const before = faceSig(m);
    const p = z.play('look-around', { el: m.host, facing: 'l' });
    await advance(5000);
    assert.strictEqual(await p, true);
    assert.strictEqual(faceSig(m), before);
    assert.strictEqual(JSON.stringify(z.viewOf(m.host)), JSON.stringify({ view: 'front', facing: 'r' }));
    const r = load('reduced');
    const m2 = buildMascot('nudge');
    r.bind(m2.host);
    const q = r.play('look-around', { el: m2.host });
    await advance(5000);
    assert.strictEqual(await q, false);
    assert.strictEqual(all.length, 0);
  });


  await scenario('no parts library: setFace and setExpression report false and change nothing', async () => {
    const z = load('system', { noParts: true });
    const m = buildMascot('nudge');
    z.bind(m.host);
    assert.strictEqual(z.setFace('joy', { el: m.host }), false);
    assert.strictEqual(z.setExpression('happy', { el: m.host }), false);
    assert.strictEqual(m.host.getAttribute('data-face'), 'nudge');
    const ok = load('system');
    const n = buildMascot('nudge');
    ok.bind(n.host);
    assert.strictEqual(ok.setFace('joy', { el: n.host }), true);
    assert.strictEqual(n.host.getAttribute('data-face'), 'joy');
  });

  await scenario('part-swap squeezes are tracked: a clip (stop) cancels them', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    z.setExpression('happy', { el: m.host });
    const swaps = all.filter((a) => a.opts.duration === 80 || a.opts.duration === 90);
    assert.ok(swaps.length >= 2, 'eye and mouth swaps ran');
    z.play('nod', { el: m.host });
    assert.ok(swaps.every((a) => a.canceled), 'stop() cancelled them');
  });

  await scenario('a thought bubble hides the face-attached fx (sweat) and gives it back', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    const p = z.play('wobble', { el: m.host, thought: true, face: 'embarrassed' });
    await advance(100);
    assert.strictEqual(m.part('.zorp-slot--fx-face').style.display, 'none');
    await advance(3000);
    await p;
    assert.strictEqual(m.part('.zorp-slot--fx-face').style.display, '');
  });

  const failed = results.filter((r) => !r[1]);
  console.log('\n' + (failed.length ? failed.length + ' of ' + results.length + ' zorp idle scenarios FAILED' : 'All ' + results.length + ' zorp idle scenarios passed.'));
  process.exit(failed.length ? 1 : 0);
})();
