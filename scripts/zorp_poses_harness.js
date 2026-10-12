'use strict';
/* E8 Phase 4: behavioural harness for static/js/zorp-poses.js (poses, arm shapes, the beat engine and the new
   clips), run by test_zorp_poses_smoke.py. Same fake DOM as zorp_rig_harness.js, built from the REAL rendered markup,
   parts library and island, with a virtual clock for setTimeout so beat boundaries are deterministic; every
   animation is a fake that finishes only when a scenario says so.
   Usage: node zorp_poses_harness.js <zorp-motion.js> <zorp-poses.js> <fixture.json> [<welcome.js> <zorp-triggers.js>]
   fixture: { island, library, svgs: { front, sideL, sideR, posed }, poses: [names], valence: { preset: '+'|'0'|'-' } }
   E8 Phase 5 adds the react() plan scenarios, and (with the two optional paths) the /welcome and data-zorp-autoplay
   wiring run against the real runtime. */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const [, , scriptPath, posesPath, fixturePath, welcomePath, triggersPath] = process.argv;
if (!scriptPath || !posesPath || !fixturePath) {
  console.error('usage: node zorp_poses_harness.js <zorp-motion.js> <zorp-poses.js> <fixture.json>');
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
  addEventListener(type, fn) { (this._ls = this._ls || []).push([type, fn]); }
  click() {
    const evt = { type: 'click', currentTarget: this, prevented: false, preventDefault() { this.prevented = true; } };
    (this._ls || []).filter((l) => l[0] === 'click').forEach((l) => l[1](evt));
    return evt;
  }
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
  // like WAAPI: offsets within [0, 1] and never decreasing, else a TypeError (E9 Phase 2: a cheek keyframe past the clip end once passed this harness and threw in Chromium)
  let lastOffset = 0;
  frames.forEach((f) => {
    if (f.offset === undefined) return;
    if (f.offset < 0 || f.offset > 1 || f.offset < lastOffset) throw new TypeError('Offsets must be monotonically non-decreasing and within 0 to 1: ' + JSON.stringify(frames.map((x) => x.offset)));
    lastOffset = f.offset;
  });
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

// virtual clock: setTimeout never really waits; advance(ms) fires due timers in order
let now = 0;
const clock = { t: 1e6 };   // Date.now() for react(): scenarios move it by hand
let timers = [];
let tid = 0;
const fakeST = (fn, ms) => { tid += 1; timers.push({ id: tid, fn, at: now + (ms || 0) }); return tid; };
const fakeCT = (id) => { timers = timers.filter((t) => t.id !== id); };
async function advance(ms) {
  const target = now + ms;
  for (;;) {
    const due = timers.filter((t) => t.at <= target).sort((a, b) => a.at - b.at)[0];
    if (!due) break;
    timers = timers.filter((t) => t !== due);
    now = due.at;
    due.fn();
    await flush();
  }
  now = target;
  await flush();
}

function load(motion, env) {
  animations = [];
  timers = [];
  now = 0;
  commitMode = (env && env.commit) || 'ok';
  const island = new El('script', { id: 'pb-zorp-rig' });
  island.textContent = fx.island;
  const tpl = new El('template', { id: 'pb-zorp-parts' });
  tpl.content = parse(fx.library).childNodes[0];
  const htmlEl = new El('html');
  if (motion !== 'system') htmlEl.setAttribute('data-motion', motion);
  const byId = Object.assign({ 'pb-zorp-rig': island, 'pb-zorp-parts': tpl }, (env && env.byId) || {});
  class KE { }
  if (!env || env.composite !== false) KE.prototype.composite = 'replace';
  const sandbox = {
    document: {
      readyState: 'complete', hidden: false, body: new El('body'), documentElement: htmlEl,
      getElementById: (id) => byId[id] || null,
      addEventListener(t, fn) { (sandbox.docListeners = sandbox.docListeners || []).push([t, fn]); },
      querySelector: (sel) => (env && env.query && env.query[sel] && env.query[sel][0]) || null,
      querySelectorAll: (sel) => (env && env.query && env.query[sel]) || [],
    },
    addEventListener() {},
    Element: El, Animation: class { get finished() { return null; } },
    KeyframeEffect: KE,
    CSS: { supports: () => !env || env.props !== false },
    setTimeout: fakeST, clearTimeout: fakeCT, Promise, Object, Date: { now: () => clock.t }, Math, JSON, console, Array, String,
  };
  sandbox.window = sandbox;
  sandbox.matchMedia = () => ({ matches: false, addEventListener() {} });
  vm.runInNewContext(fs.readFileSync(scriptPath, 'utf8'), sandbox);
  if (!env || env.poses !== false) vm.runInContext(fs.readFileSync(posesPath, 'utf8'), sandbox);
  return { z: sandbox.pbZorp, html: htmlEl, sandbox };
}


const libPart = (channel, id) => parse(fx.library).querySelector('[data-part="' + channel + ':' + id + '"]');
const NEW_CLIPS = ['fist-pump', 'victory', 'flex', 'shrug', 'bow', 'think-chin', 'dance', 'float', 'oops-encourage', 'turn'];
const BEAT_CLIPS = NEW_CLIPS.filter((c) => c !== 'turn');
// E9 Phase 2 (D5): cheer and hop are beat clips too; the soft body covers all of these (the legacy twins are the fallback in zorp-motion.js)
const SOFT_CLIPS = BEAT_CLIPS.concat(['cheer', 'hop']);
// Plan 3.11 durations (ms) with headroom; bow and side-point add two 300 ms turns to the clip's own length.
// Clip readability pass (2026-10-02): flex 950 -> 1200, shrug 850 -> 1200 and dance 1500 -> 2000 (David asked for a proper dance of 1.6 to 2 s).
const MAX_MS = { wave: 1200, 'fist-pump': 1300, victory: 1250, flex: 1200, shrug: 1200, bow: 1350, 'think-chin': 1100, dance: 2000, float: 1400, 'oops-encourage': 1000, turn: 350, cheer: 800, hop: 550 };
const parts = (m) => ({
  root: m.part('.buddy-root'), shadow: m.part('.buddy-shadow'), head: m.part('.buddy-head'), body: m.part('.buddy-body'),
  armL: [m.part('.buddy-arm--l'), m.part('.buddy-arm--l-front')], armR: [m.part('.buddy-arm--r'), m.part('.buddy-arm--r-front')],
  antL: m.part('.buddy-antenna--l'), antR: m.part('.buddy-antenna--r'), footL: m.part('.buddy-foot--l'), footR: m.part('.buddy-foot--r'),
});
// the soft body's targets too (E9 Phase 2): what findParts() returns
const softParts = (m) => Object.assign(parts(m), { face: m.part('.zorp-face'), ride: m.part('.zorp-ride'), hatRide: m.part('.zorp-hatride'), cheeks: m.part('.zorp-slot--cheeks') });
const armIs = (m, sel, shape, side) => {
  const want = libPart('arm', shape + '-' + side).childNodes.map((c) => c.sig()).join('|');
  return m.part(sel).childNodes.map((c) => c.sig()).join('|') === want;
};
const val = (z, name) => z.valenceOf(name);
const timersCount = () => timers.length;

let finished = false;
setTimeout(() => { console.error('harness timed out'); process.exit(1); }, 60000).unref();
process.on('exit', () => { if (!finished) { console.error('harness ended before every scenario ran'); process.exitCode = 1; } });
const results = [];
async function scenario(name, fn) {
  try { await fn(); results.push([name, true]); console.log('OK: ' + name); }
  catch (e) { results.push([name, false]); console.error('FAIL: ' + name + '\n  ' + (e && e.stack || e)); }
}

(async () => {
  await scenario('graceful degradation: without zorp-poses.js the new names report false and Phases 1-3 still work', async () => {
    const { z } = load('system', { poses: false });
    NEW_CLIPS.forEach((c) => assert.strictEqual(z.hasClip(c), false, c));
    fx.poses.forEach((p) => assert.strictEqual(z.hasPose(p), false, p));
    eq(z.poses, []);
    const m = mascot('front');
    z.bind(m.host);
    assert.strictEqual(await z.play('fist-pump', { el: m.host }), false);
    assert.strictEqual(await z.pose('fist-up', { el: m.host }), false);
    assert.strictEqual(animations.length, 0);
    ['cheer', 'wave', 'hop', 'side-point', 'blink'].forEach((c) => assert.strictEqual(z.hasClip(c), true, c));
    const p = z.play('cheer', { el: m.host });
    assert.ok(animations.length >= 4, 'legacy clips still animate');
    await finishAll();
    assert.strictEqual(await p, true);
    assert.strictEqual(typeof z.register, 'function');
  });

  await scenario('registered: poses, clips and hasPose come from the pose table', () => {
    const { z } = load('system');
    eq(z.poses, fx.poses);
    fx.poses.forEach((p) => assert.strictEqual(z.hasPose(p), true, p));
    assert.strictEqual(z.hasPose('nonsense'), false);
    NEW_CLIPS.forEach((c) => { assert.strictEqual(z.hasClip(c), true, c); assert.ok(z.clips.indexOf(c) !== -1, c); });
    ['idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake', 'hop', 'peek', 'sleep', 'side-point']
      .forEach((c) => assert.ok(z.clips.indexOf(c) !== -1, 'old clip ' + c));
    assert.strictEqual(z.clipInfo('nonsense'), null);
  });

  await scenario('every clip: ends on a positive preset, no negative face outside the trip, inside the plan duration', () => {
    const { z } = load('system');
    BEAT_CLIPS.forEach((name) => {
      const info = z.clipInfo(name);
      const turns = info.view === 'side' ? 600 : 0;
      assert.ok(info.dur + turns <= MAX_MS[name], name + ' is ' + (info.dur + turns) + ' ms');
      const exprs = info.beats.filter((b) => b.expr).map((b) => b.expr);
      assert.strictEqual(val(z, exprs[exprs.length - 1]), 'positive', name + ' must end positive');
      exprs.forEach((e) => assert.notStrictEqual(val(z, e), 'negative', name + ' uses a negative face: ' + e));
      // positive within 1.2 s: the first positive beat starts early and no later beat is not positive... measured from the start
      let t = 0; let firstPositive = null;
      info.beats.forEach((b) => { if (b.expr && val(z, b.expr) === 'positive' && firstPositive === null) firstPositive = t; t += (b.ms || 0) + (b.hold || 0); });
      assert.ok(firstPositive !== null && firstPositive <= 1200, name + ' reaches a positive face by ' + firstPositive);
      assert.ok(val(z, info.reducedFace) !== 'negative' && info.reducedFace, name + ' has a reduced preset');
      info.beats.forEach((b) => assert.ok(fx.poses.indexOf(b.pose) !== -1, name + ': unknown pose ' + b.pose));
    });
    const dance = z.clipInfo('dance');
    const neg = dance.trip.filter((b) => b.expr && val(z, b.expr) === 'negative');
    assert.strictEqual(neg.length, 1, 'the dance trip is the only negative beat');
    assert.ok((neg[0].ms || 0) + (neg[0].hold || 0) <= 300, 'and it lasts at most 300 ms');
    const last = dance.trip.filter((b) => b.expr).pop();
    assert.strictEqual(val(z, last.expr), 'positive');
    const sum = (l) => l.reduce((s, b) => s + (b.ms || 0) + (b.hold || 0), 0);
    assert.strictEqual(sum(dance.trip), sum(dance.beats), 'trip variant has the same length');
    const oops = z.clipInfo('oops-encourage');
    assert.ok(oops.beats[0].expr === 'oops' && (oops.beats[0].ms + oops.beats[0].hold) <= 300, 'oops is the first beat, at most 300 ms');
  });

  // Clip readability pass (2026-10-02): David saw dance, flex and shrug as "just a smile". The movement existed but was tiny
  // (a 12-unit stub arm behind the body, a 6 degree sway). These floors are in the 64-unit viewBox, where 1 unit is
  // 2.5 px at 160 px and 0.875 px at 56 px, so each floor is still a few pixels at the small size.
  await scenario('readability: dance, flex, shrug, victory and fist-pump move enough to read at 160 and 56 px, with the animated arms in the visible layer', () => {
    const { z } = load('system');
    const m = mascot('front');
    const P = parts(m);
    const nums = (str, re) => { const r = re.exec(str); return r ? r.slice(1).map(Number) : null; };
    const track = (name, target) => {
      const t = z.compileBeats(z.clipInfo(name).beats, P, { facing: 'r' }).find((x) => x[0] === target);
      return t ? t[1].map((f) => f.transform) : [];
    };
    const rot = (list) => list.map((tf) => (nums(tf, /rotate\((-?[\d.]+)deg\)/) || [0])[0]);
    const lift = (list) => list.map((tf) => -(nums(tf, /translate\((-?[\d.]+)px,(-?[\d.]+)px\)/) || [0, 0])[1]);
    const scaleX = (list) => list.map((tf) => (nums(tf, /scale\((-?[\d.]+),(-?[\d.]+)\)/) || [1, 1])[0]);
    const scaleY = (list) => list.map((tf) => (nums(tf, /scale\((-?[\d.]+),(-?[\d.]+)\)/) || [1, 1])[1]);
    const peak = (a) => Math.max(...a.map(Math.abs));
    const flips = (a) => { let n = 0; let last = 0; a.forEach((v) => { const sg = Math.abs(v) < 1 ? 0 : Math.sign(v); if (sg && last && sg !== last) n += 1; if (sg) last = sg; }); return n; };
    const pulses = (a, level) => { let n = 0; let up = false; a.forEach((v) => { if (v >= level && !up) { n += 1; up = true; } if (v < level - 0.015) up = false; }); return n; };
    // dance: a sway of at least 8 degrees that changes side at least five times, a hop of at least 14 px, both arms
    // lifted to 140 degrees or more, and the feet taking turns
    const dRoot = track('dance', P.root);
    assert.ok(peak(rot(dRoot)) >= 8, 'dance sways at least 8 degrees: ' + peak(rot(dRoot)));
    assert.ok(flips(rot(dRoot)) >= 5, 'dance changes side at least 5 times: ' + flips(rot(dRoot)));
    assert.ok(Math.max(...lift(dRoot)) >= 14, 'dance hops at least 14 px: ' + Math.max(...lift(dRoot)));
    assert.ok(peak(rot(track('dance', P.armL))) >= 140 && peak(rot(track('dance', P.armR))) >= 140, 'dance lifts both arms to 140 degrees or more');
    assert.ok(Math.max(...lift(track('dance', P.footL))) >= 3 && Math.max(...lift(track('dance', P.footR))) >= 3, 'dance lifts each foot');
    // flex: the bent arm rises to about 90 degrees and the chest puffs twice (a double pump)
    const fRoot = track('flex', P.root);
    assert.ok(peak(rot(track('flex', P.armR))) >= 88, 'flex raises the arm');
    assert.ok(pulses(scaleY(fRoot), 1.05) >= 2, 'flex pumps the chest twice (root scaleY)');
    // shrug: both palms out and up (at least 28 degrees), the head tilts at least 6 degrees, and the lift happens twice
    assert.ok(peak(rot(track('shrug', P.armL))) >= 28 && peak(rot(track('shrug', P.armR))) >= 28, 'shrug lifts both arms');
    assert.ok(peak(rot(track('shrug', P.head))) >= 6, 'shrug tilts the head');
    assert.ok(pulses(rot(track('shrug', P.armR)).map(Math.abs), 29) >= 2, 'shrug lifts twice');
    // wave: the long arm (front layer) swings between -120 and -176 degrees at least five times, with a lean and a head tilt
    const wArm = rot(track('wave', P.armR));
    assert.ok(Math.max(...wArm.map(Math.abs)) >= 170 && Math.min(...wArm.filter((d) => d !== 0).map(Math.abs)) >= 120, 'wave raises the arm up beside the head');
    let turns = 0; let prevDir = 0;
    wArm.forEach((v, i) => { if (i && Math.abs(v - wArm[i - 1]) >= 30) { const d = Math.sign(v - wArm[i - 1]); if (prevDir && d !== prevDir) turns += 1; prevDir = d; } });
    assert.ok(turns >= 5, 'wave swings side to side at least 3 times (direction changes: ' + turns + ')');
    assert.ok(peak(rot(track('wave', P.root))) >= 2 && peak(rot(track('wave', P.head))) >= 3, 'wave leans and tilts the head');
    assert.ok(z.clipInfo('wave').dur >= 1000 && z.clipInfo('wave').dur <= 1200, 'wave lasts about 1.1 s');
    // victory and fist-pump: the arm goes up past 150 degrees and the body leaves the ground by 12 px or more
    ['victory', 'fist-pump'].forEach((name) => {
      assert.ok(Math.max(peak(rot(track(name, P.armL))), peak(rot(track(name, P.armR)))) >= 150, name + ' raises an arm');
      assert.ok(Math.max(...lift(track(name, P.root))) >= 12, name + ' jumps at least 12 px');
    });
    // visibility: an arm lifted 20 degrees or more is drawn in the front layer (its back twin is hidden behind the body),
    // and the clip moves both twins together
    ['dance', 'flex', 'shrug', 'victory', 'fist-pump', 'wave'].forEach((name) => {
      z.clipInfo(name).beats.forEach((b) => {
        const row = fx.poseTable[b.pose];
        ['L', 'R'].forEach((S) => {
          const [shape, deg, front] = row[S];
          if (shape !== 'rest' && Math.abs(deg) >= 20) assert.strictEqual(front, 1, name + ' beat ' + b.pose + ' arm ' + S + ' (' + shape + ', ' + deg + ') must be in the front layer');
        });
      });
      const tr = z.compileBeats(z.clipInfo(name).beats, P, { facing: 'r' });
      ['armL', 'armR'].forEach((k) => {
        const mover = tr.filter((t) => t[0] === P[k]);
        assert.ok(mover.length <= 1 && (!mover.length || (Array.isArray(mover[0][0]) && mover[0][0].length === 2)), name + ' ' + k + ': one track drives the back and front twins together');
      });
    });
    // flex shows both bent arms (the reach arm's length is pinned by the parts-library reach test in test_zorp_expression_smoke.py)
    assert.ok(fx.poseTable.flex.R[0] === 'bent-fist' && fx.poseTable.flex.L[0] === 'bent-fist', 'flex shows both bent arms');
  });

  // The styleguide's dev-only full-motion preview: only the exact value "full" on html[data-motion-preview] lifts reduced and off.
  await scenario('styleguide full-motion preview: data-motion-preview="full" shows the real dance under reduced and off; anything else changes nothing', async () => {
    for (const level of ['reduced', 'off']) {
      const { z, html } = load(level);
      const m = mascot('front');
      z.bind(m.host);
      z.idle(false, m.host);
      assert.strictEqual(z.motionLevel(), level);
      animations = [];
      z.play('dance', { el: m.host });
      assert.strictEqual(animations.length, 0, level + ': no movement without the preview');
      html.setAttribute('data-motion-preview', 'yes');
      assert.strictEqual(z.motionLevel(), level, 'only the exact value full counts');
      html.setAttribute('data-motion-preview', 'full');
      assert.strictEqual(z.motionLevel(), 'full');
      animations = [];
      z.play('dance', { el: m.host });
      assert.ok(animations.length >= 6, level + ': the dance animates with the preview on (' + animations.length + ' animations)');
      html.setAttribute('data-motion-preview', '');
      assert.strictEqual(z.motionLevel(), level, 'removing the preview restores ' + level);
    }
  });

  await scenario('side-point reads: the near arm is the long reach arm while it points (800 ms clip), the resting arm is back at the end', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    const done = z.play('side-point', { el: m.host });
    for (let i = 0; i < 4; i += 1) await finishAll();
    await advance(300);
    assert.strictEqual(z.clipInfo('side-point').dur, 800, 'the point holds about 440 ms');
    assert.ok(armIs(m, '.buddy-arm--r-front', 'reach', 'r'), 'the long arm points up beside the head, not the 10-unit paddle');
    for (let i = 0; i < 8; i += 1) { await finishAll(); await advance(100); }
    assert.strictEqual(await done, true);
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
    assert.ok(armIs(m, '.buddy-arm--r-front', 'rest', 'r'), 'the resting arm is back in the front view');
  });

  // 2026-10-02: the arm-shape swap back to the short arm used to run 12% into the lowering beat, by which time an eased arm was
  // already sideways, so a long fist stuck out horizontally near the end of fist-pump. No long arm may be shown while its angle is
  // in the sideways band (40 to 150 degrees) and falling.
  await scenario('no long arm (fist, reach, bent-fist) is shown sideways while it lowers, in every beat clip', async () => {
    const bez = (x1, y1, x2, y2) => (x) => {
      let lo = 0; let hi = 1; let t = x;
      for (let i = 0; i < 30; i += 1) { t = (lo + hi) / 2; const cx = 3 * (1 - t) * (1 - t) * t * x1 + 3 * (1 - t) * t * t * x2 + t * t * t; if (cx < x) lo = t; else hi = t; }
      return 3 * (1 - t) * (1 - t) * t * y1 + 3 * (1 - t) * t * t * y2 + t * t * t;
    };
    const ease = (e) => {
      const m = /cubic-bezier\(([^)]+)\)/.exec(e || '');
      if (m) { const v = m[1].split(',').map(Number); return bez(v[0], v[1], v[2], v[3]); }
      if (e === 'ease-in-out') return bez(0.42, 0, 0.58, 1);
      return (x) => x;
    };
    const angleAt = (frames, u) => {
      let i = 0;
      while (i < frames.length - 2 && frames[i + 1].offset <= u) i += 1;
      const a = frames[i]; const b = frames[i + 1];
      const va = parseFloat(/rotate\((-?[\d.]+)deg\)/.exec(a.transform)[1]); const vb = parseFloat(/rotate\((-?[\d.]+)deg\)/.exec(b.transform)[1]);
      const span = b.offset - a.offset;
      const x = span > 0 ? Math.min(1, Math.max(0, (u - a.offset) / span)) : 1;
      return va + (vb - va) * ease(a.easing)(x);
    };
    for (const name of ['fist-pump', 'victory', 'flex', 'shrug', 'dance', 'wave', 'cheer']) {
      for (const trip of name === 'dance' ? [false, true] : [false]) {
        const { z } = load('system');
        const m = mascot('front');
        z.bind(m.host);
        z.idle(false, m.host);
        const info = z.clipInfo(name);
        const beats = trip ? info.trip : info.beats;
        const tracks = z.compileBeats(beats, parts(m), { facing: 'r' });
        const longs = ['fist', 'reach', 'bent-fist'];
        const sides = [['L', 'armL', '.buddy-arm--l'], ['R', 'armR', '.buddy-arm--r']];
        animations = [];
        z.play(name, { el: m.host, trip });
        const prev = { L: 0, R: 0 };
        for (let t = 0; t <= info.dur; t += 5) {
          await advance(t === 0 ? 0 : 5);
          for (const [S, key, sel] of sides) {
            const tr = tracks.find((x) => x[0] === parts(m)[key] || (Array.isArray(x[0]) && x[0][0] === m.part(sel)));
            if (!tr) continue;
            const ang = Math.abs(angleAt(tr[1], Math.min(1, t / info.dur)));
            // lowering = the beat running now has the short resting arm as its target and the angle is falling
            let acc = 0; let cur = beats[beats.length - 1];
            for (const b of beats) { acc += (b.ms || 0) + (b.hold || 0); if (t < acc) { cur = b; break; } }
            const falling = ang < prev[S] - 0.01 && fx.poseTable[cur.pose][S][0] === 'rest';
            prev[S] = ang;
            const isLong = longs.some((shape) => armIs(m, sel, shape, S.toLowerCase()));
            assert.ok(!(isLong && falling && ang > 40 && ang < 150), name + (trip ? ' (trip)' : '') + ': a long arm is shown sideways while lowering (arm ' + S + ' at ' + ang.toFixed(0) + ' degrees, t=' + t + ' ms)');
          }
        }
        await finishAll();
      }
    }
  });

  await scenario('compileBeats: exactly one keyframe list per moving part, offsets monotone, easing valid, stretch within limits', () => {
    const { z } = load('system');
    const m = mascot('front');
    const P = softParts(m);
    SOFT_CLIPS.forEach((name) => {
      const info = z.clipInfo(name);
      [info.beats].concat(info.trip ? [info.trip] : []).forEach((beats) => {
        const tracks = z.compileBeats(beats, P, {});
        assert.ok(tracks.length >= 1, name);
        const seen = new Set();
        tracks.forEach(([target, frames]) => {
          assert.ok(!seen.has(target), name + ': a part has two keyframe lists');
          seen.add(target);
          assert.strictEqual(frames[0].offset, 0, name + ' starts at 0');
          assert.strictEqual(frames[frames.length - 1].offset, 1, name + ' ends at 1');
          frames.forEach((f, i) => {
            assert.ok(f.offset >= 0 && f.offset <= 1 && (i === 0 || f.offset >= frames[i - 1].offset), name + ' offsets must not decrease');
            assert.ok(typeof f.transform === 'string' && f.easing, name + ' frame has transform and easing');
          });
        });
        const scales = [];
        tracks.forEach(([target, frames]) => { if (target === P.root) frames.forEach((f) => scales.push(/scale\(([-\d.]+),([-\d.]+)\)/.exec(f.transform))); });
        scales.forEach((s) => {
          const sx = +s[1]; const sy = +s[2];
          assert.ok(Math.abs(sx - 1) <= 0.12 + 1e-9 && Math.abs(sy - 1) <= 0.12 + 1e-9, name + ' deforms beyond 12%: ' + sx + ',' + sy);
          assert.ok(Math.abs(sx * sy - 1) <= 0.12, name + ' does not keep volume: ' + sx * sy);
        });
      });
    });
    // the shadow stays on the ground: it counters the root's lift and shrinks with it (fist-pump, victory)
    ['fist-pump', 'victory'].forEach((name) => {
      const tr = z.compileBeats(z.clipInfo(name).beats, P, { facing: 'r' });
      const root = tr.find((t) => t[0] === P.root)[1];
      const shadow = tr.find((t) => t[0] === P.shadow)[1];
      const lift = Math.max(...root.map((f) => -parseFloat(/translate\([-\d.]+px,([-\d.]+)px\)/.exec(f.transform)[1])));
      const counter = Math.max(...shadow.map((f) => parseFloat(/translate\(0,([-\d.]+)px\)/.exec(f.transform)[1])));
      assert.ok(lift >= 8 && Math.abs(counter - lift) < 1e-6, name + ': the shadow counters the lift (' + counter + ' vs ' + lift + ')');
      const narrow = Math.min(...shadow.map((f) => parseFloat(/scale\(([-\d.]+),1\)/.exec(f.transform)[1])));
      assert.ok(narrow < 0.9, name + ': the shadow shrinks with height');
    });
    // facing left mirrors the root (it sits outside the flip)
    const bow = z.clipInfo('bow').beats;
    const r = z.compileBeats(bow, P, { facing: 'r' }).find((t) => t[0] === P.root)[1];
    const l = z.compileBeats(bow, P, { facing: 'l' }).find((t) => t[0] === P.root)[1];
    assert.ok(/rotate\(18deg\)/.test(r[2].transform) && /rotate\(-18deg\)/.test(l[2].transform), 'bow leans the other way facing left');
  });

  // ---- E9 Phase 2: the soft body (docs/ZORP_CHARM.md 3.2) ----
  // Geometry of the drawn rig in the 64-unit viewBox: the body ellipse, its bottom (the squash anchor), the face plate and the shoulders.
  const BODY = { cx: 32, cy: 36, rx: 21, ry: 21.5, bottom: 57.5 };
  const PLATE = { cx: 32, cy: 38, rx: 15.5, ry: 13.5 };
  const SHOULDERS = [[15.6, 40], [48.4, 40]];
  const nums2 = (tf) => { const r = /scale\(([-\d.]+),([-\d.]+)\)/.exec(tf); return r ? [+r[1], +r[2]] : [1, 1]; };
  const dyOf = (tf) => { const r = /translate\(0,([-\d.]+)px\)/.exec(tf); return r ? +r[1] : 0; };
  // body ellipse as drawn when the body layer scales by (bx, by) about its bottom
  const bodyAt = (bx, by) => ({ cx: 32, cy: BODY.bottom - (BODY.bottom - BODY.cy) * by, rx: BODY.rx * bx, ry: BODY.ry * by });
  const inside = (e, x, y, shrink) => (((x - e.cx) / (e.rx - shrink)) ** 2 + ((y - e.cy) / (e.ry - shrink)) ** 2) <= 1;
  const trackOf = (tracks, target) => { const t = tracks.find((x) => x[0] === target); return t ? t[1] : null; };
  const SOFT_ALL = ['fist-pump', 'victory', 'flex', 'shrug', 'bow', 'think-chin', 'dance', 'float', 'oops-encourage', 'wave', 'cheer', 'hop'];

  await scenario('soft body volume: the body layer stays within 0.08 per axis, as drawn within 0.16, and a squash or stretch keeps its volume', () => {
    const { z } = load('system');
    const m = mascot('front');
    const P = softParts(m);
    let seen = 0;
    SOFT_ALL.forEach((name) => {
      const info = z.clipInfo(name);
      [info.beats].concat(info.trip ? [info.trip] : []).forEach((beats) => {
        const tr = z.compileBeats(beats, P, { facing: 'r' });
        const body = trackOf(tr, P.body);
        const root = trackOf(tr, P.root);
        if (!body) return;
        seen += 1;
        const rootAt = (u) => {   // the root's scale at offset u, linear between its keyframes (the body shares them, easing aside)
          let i = 0;
          while (i < root.length - 2 && root[i + 1].offset <= u) i += 1;
          const a = nums2(root[i].transform); const b = nums2(root[i + 1].transform);
          const span = root[i + 1].offset - root[i].offset;
          const x = span > 0 ? Math.min(1, Math.max(0, (u - root[i].offset) / span)) : 1;
          return [a[0] + (b[0] - a[0]) * x, a[1] + (b[1] - a[1]) * x];
        };
        assert.strictEqual(body[0].offset, 0);
        assert.strictEqual(body[body.length - 1].offset, 1);
        body.forEach((f) => {
          const [bx, by] = nums2(f.transform);
          assert.ok(Math.abs(bx - 1) <= 0.08 + 1e-9 && Math.abs(by - 1) <= 0.08 + 1e-9, name + ': body layer ' + bx + ',' + by + ' beyond 0.08');
          const [rx, ry] = rootAt(f.offset);
          const dx = rx * bx; const dy = ry * by;
          assert.ok(Math.abs(dx - 1) <= 0.16 + 1e-9 && Math.abs(dy - 1) <= 0.16 + 1e-9, name + ': drawn ' + dx.toFixed(3) + ',' + dy.toFixed(3) + ' beyond 0.16');
          // squash and stretch beats keep volume (the flex chest puff is the only deliberate gain, and its root already says so; 0.002 is the victory pose's own 1.02 stretch with the body's 0.8 percent on top)
          if (Math.abs(rx * ry - 1) <= 0.03) assert.ok(dx * dy >= 0.97 - 0.002 && dx * dy <= 1.03 + 0.002, name + ': drawn volume ' + (dx * dy).toFixed(3));
        });
      });
    });
    assert.ok(seen >= 10, 'most clips have a body track (' + seen + ')');
  });

  await scenario('face stays seated: the plate is inside the body at every keyframe, with the face riding the body by translateY only', () => {
    const { z } = load('system');
    const m = mascot('front');
    const P = softParts(m);
    SOFT_ALL.forEach((name) => {
      const tr = z.compileBeats(z.clipInfo(name).beats, P, { facing: 'r' });
      const body = trackOf(tr, P.body);
      const face = trackOf(tr, P.face);
      if (!body) return;
      assert.ok(face && face.length === body.length, name + ': the face rides on the body\'s own keyframes');
      body.forEach((f, i) => {
        assert.strictEqual(face[i].offset, f.offset, name + ': same timing, no lag');
        assert.strictEqual(face[i].easing, f.easing, name + ': same easing');
        assert.ok(/^translate\(0,-?[\d.]+px\)$/.test(face[i].transform), name + ': the face only translates (it never stretches): ' + face[i].transform);
        const [bx, by] = nums2(f.transform);
        const dy = dyOf(face[i].transform);
        assert.ok(Math.abs(dy - 19.5 * (1 - by)) <= 0.02, name + ': face dy ' + dy + ' for body sy ' + by);
        const e = bodyAt(bx, by);
        for (let k = 0; k < 360; k += 1) {
          const a = k * Math.PI / 180;
          const x = PLATE.cx + PLATE.rx * Math.cos(a); const y = PLATE.cy + dy + PLATE.ry * Math.sin(a);
          assert.ok(inside(e, x, y, 1.0), name + ': the plate leaves the body (margin 1 unit) at offset ' + f.offset.toFixed(3) + ' angle ' + k);
        }
      });
    });
  });

  await scenario('antenna ride: the wrapper follows the body top (within 0.3 units), the antennae keep their own rotation, and the hat has its own wrapper', () => {
    const { z } = load('system');
    const m = mascot('front');
    const h = mascot('hat');
    const P = softParts(m);
    const H = softParts(h);
    assert.ok(P.ride && !P.hatRide, 'the default Zorp has the antenna wrapper and no hat wrapper');
    assert.ok(H.ride && H.hatRide, 'a Zorp with a hat has both');
    let worstAnt = 0;
    assert.strictEqual(P.ride.childNodes.length, 2, 'the wrapper holds exactly the two antennae');
    assert.ok(P.ride.childNodes.every((c) => /buddy-antenna/.test(c.attrs.class)));
    SOFT_ALL.forEach((name) => {
      const tr = z.compileBeats(z.clipInfo(name).beats, H, { facing: 'r' });
      const body = trackOf(tr, H.body);
      if (!body) return;
      const ride = trackOf(tr, H.ride);
      const hat = trackOf(tr, H.hatRide);
      assert.ok(ride && hat && ride.length === body.length && hat.length === body.length, name + ': both riders on the body keyframes');
      body.forEach((f, i) => {
        const [bx, by] = nums2(f.transform);
        const e = bodyAt(bx, by);
        [[24, 16], [40, 16]].forEach(([x, y0]) => {
          const base = y0 + dyOf(ride[i].transform);
          const top = e.cy - e.ry * Math.sqrt(1 - (((x - 32) / e.rx) ** 2));
          worstAnt = Math.max(worstAnt, Math.abs(base - top));
        });
        assert.ok(Math.abs(dyOf(hat[i].transform) - 43 * (1 - by)) <= 0.03, name + ': the hat sits on the body top');
      });
      // the antennae's own tracks are still pure rotations (the ride is a separate wrapper)
      [H.antL, H.antR].forEach((a) => (trackOf(tr, a) || []).forEach((f) => assert.ok(/^rotate\(-?[\d.]+deg\)$/.test(f.transform), name + ': antenna ' + f.transform)));
    });
    // the plan's 0.3 units (review 2026-10-04: the ride follows the body top at the antenna's x, width included, so the gap is the 0.12 at rest plus a little; it was 0.322 with a pure sy ride)
    console.log('antenna base to body top, widest gap over every clip and keyframe: ' + worstAnt.toFixed(3) + ' units');
    assert.ok(worstAnt <= 0.3, 'the antenna base stays within 0.3 units of the body top: ' + worstAnt);
  });

  await scenario('arms clear without riding: the shoulders stay inside the body at every keyframe and no arm track translates', () => {
    const { z } = load('system');
    const m = mascot('front');
    const P = softParts(m);
    let min = 9;
    SOFT_ALL.forEach((name) => {
      const tr = z.compileBeats(z.clipInfo(name).beats, P, { facing: 'r' });
      const body = trackOf(tr, P.body);
      [P.armL, P.armR].forEach((arm) => (trackOf(tr, arm) || []).forEach((f) => assert.ok(/^rotate\(/.test(f.transform) && f.transform.indexOf('translate') === -1, name + ': an arm track is only a rotation')));
      if (!body) return;
      body.forEach((f) => {
        const [bx, by] = nums2(f.transform);
        const e = bodyAt(bx, by);
        SHOULDERS.forEach(([x, y]) => {
          assert.ok(inside(e, x, y, 2.0), name + ': a shoulder is within 2 units of the body edge at ' + f.offset.toFixed(3));
          for (let g = 0; g <= 40; g += 1) { const d = g / 10; if (!inside(e, x, y, d)) { min = Math.min(min, d); break; } }
        });
      });
    });
    assert.ok(min >= 2.0, 'the nearest a shoulder gets to the edge (units): ' + min);
  });

  await scenario('durations unchanged: every Phase 0 beat clip keeps its length, and cheer and hop stay within 100 ms of the legacy clips with the same reduced face', () => {
    const { z } = load('system');
    // measured at the Phase 0 tree (43e387e plus E9 Phases 0 and 1): dur = the beats' span plus the 80 ms tail
    const PHASE0 = { 'fist-pump': 1210, victory: 1180, flex: 1120, shrug: 1050, bow: 660, 'think-chin': 1030, dance: 1820, float: 1340, 'oops-encourage': 920, wave: 1100 };
    Object.keys(PHASE0).forEach((name) => assert.strictEqual(z.clipInfo(name).dur, PHASE0[name], name + ' length changed'));
    const legacy = load('system', { poses: false }).z;
    ['cheer', 'hop'].forEach((name) => {
      const info = z.clipInfo(name);
      assert.ok(info.beats && info.beats.length >= 4, name + ' is a beat clip now');
      const old = { cheer: 700, hop: 450 }[name];
      assert.ok(Math.abs(info.dur - old) <= 100, name + ' is ' + info.dur + ' ms against the legacy ' + old);
      assert.strictEqual(info.reducedFace, 'celebrate', name + ' keeps its reduced preset');
      assert.strictEqual(info.face, 'celebrate', name + ' keeps its resting clip preset (react() may still replace it)');
      assert.strictEqual(val(z, info.face), 'positive');
      assert.strictEqual(legacy.hasClip(name), true, 'the legacy ' + name + ' is still the fallback without zorp-poses.js');
      assert.strictEqual(legacy.clipInfo ? legacy.clipInfo(name) : null, null);
    });
    assert.strictEqual(z.clipInfo('cheer').beats.some((b) => b.expr), false, 'react() passes its own positive face, so the beats set none');
    // the colour pulse for reduced motion: cheer has it, hop never did
    const { z: r } = load('reduced');
    const m = mascot('front');
    r.bind(m.host);
    r.play('cheer', { el: m.host });
    assert.ok(m.part('.buddy-body')._cls.indexOf('is-zorp-pulse') !== -1, 'cheer still pulses at reduced motion');
    r.play('hop', { el: m.host });
    assert.ok(m.part('.buddy-body')._cls.indexOf('is-zorp-pulse') === -1, 'hop never pulsed');
  });

  await scenario('jelly truncates in short beats: a landing wobbles for 70, 140 and 210 ms, cut off by a shorter next beat, and the clip length never changes', () => {
    const { z } = load('system');
    const m = mascot('front');
    const P = softParts(m);
    const mk = (nextMs, hold) => [
      { pose: 'crouch', ms: 100, ease: 'out' },
      { pose: 'stand', y: -9, s: [0.94, 1.08], ms: 140, ease: 'out' },
      { pose: 'stand', y: 1, s: [1.08, 0.93], ms: 80, ease: 'in' },
      { pose: 'stand', ms: nextMs, hold: hold || 0, ease: 'overshoot' }];
    const D = (beats) => beats.reduce((a, b) => a + b.ms + (b.hold || 0), 0) + z.clipInfo('hop').tail;
    const landing = 320;
    [[300, 0], [100, 0], [40, 0], [60, 200]].forEach(([next, hold]) => {
      const beats = mk(next, hold);
      const tr = z.compileBeats(beats, P, { facing: 'r' });
      const body = trackOf(tr, P.body);
      const offs = body.map((f) => Math.round(f.offset * D(beats)));
      const win = Math.min(210, next + hold);
      const inWin = offs.filter((t) => t > landing && t < landing + win);
      const want = [70, 140, 210].filter((j) => j < win || (j === win && !offs.includes(landing + j))).map((j) => landing + j);
      assert.deepStrictEqual(inWin.filter((t) => want.includes(t)).length >= want.filter((t) => t < landing + win).length, true, 'next ' + next + '+' + hold + ': the wobble keyframes are present up to the cut');
      offs.forEach((t, i) => assert.ok(i === 0 || t >= offs[i - 1], 'offsets never decrease'));
      assert.ok(offs[offs.length - 1] === D(beats), 'the body ends at the clip end');
      assert.ok(offs.every((t) => t <= D(beats)), 'nothing after the clip end');
      // nothing of the wobble lies past the window
      assert.ok(inWin.every((t) => t - landing <= 210), 'the wobble never outlasts 210 ms');
      if (next + hold < 70) assert.ok(!offs.some((t) => t === landing + 70), 'a next beat shorter than 70 ms leaves no jelly keyframe at +70');
      if (next + hold >= 210) assert.ok(offs.includes(landing + 210), 'a full window ends at rest at +210');
      // the cheeks bounce with the jelly and are back to rest at the window end
      const ck = trackOf(tr, P.cheeks);
      if (next + hold <= 60) assert.ok(!ck, 'a window of 60 ms or less has no cheek bounce');
      else assert.ok(ck && ck.every((f) => f.offset >= 0 && f.offset <= 1) && dyOf(ck[ck.length - 1].transform) === 0 && ck.some((f) => dyOf(f.transform) === 0.8), 'cheeks bounce to +0.8 and end at rest');
    });
    // the first jelly keyframe swings the other way (stretch after the squash), by 0.6 of the landing deviation
    const tr = z.compileBeats(mk(300), P, { facing: 'r' });
    const body = trackOf(tr, P.body);
    const D0 = D(mk(300));
    const land = body.find((f) => Math.round(f.offset * D0) === landing);
    const j1 = body.find((f) => Math.round(f.offset * D0) === landing + 70);
    // w is the landing's drawn squash, root times body (review 2026-10-04: the body layer's own share wobbled under a pixel at 56 px)
    const rootLand = trackOf(tr, P.root).find((f) => Math.round(f.offset * D0) === landing);
    const w = nums2(rootLand.transform)[0] * nums2(land.transform)[0] - 1;
    assert.ok(w > 0.1 && nums2(j1.transform)[0] < 1 && nums2(j1.transform)[1] > 1, 'a stretch follows the landing squash');
    assert.ok(Math.abs((1 - nums2(j1.transform)[0]) - 0.6 * w) < 0.002 && Math.abs((nums2(j1.transform)[1] - 1) - 0.6 * w) < 0.002, 'by 0.6 w on both axes: ' + j1.transform + ' w ' + w.toFixed(3));
    // a bigger landing is capped so the body layer stays within 0.075 of 1
    const big = trackOf(z.compileBeats([{ pose: 'stand', y: -12, s: [0.9, 1.11], ms: 140, ease: 'out' }, { pose: 'stand', y: 1, s: [1.12, 0.88], ms: 80, ease: 'in' }, { pose: 'stand', ms: 300, ease: 'overshoot' }], P, { facing: 'r' }), P.body);
    assert.ok(big.some((f) => Math.abs(nums2(f.transform)[0] - 1) >= 0.07), 'w is capped at 0.12, so the wobble peaks at 0.072');
    big.forEach((f) => nums2(f.transform).forEach((a) => assert.ok(Math.abs(a - 1) <= 0.075 + 1e-9, 'jelly capped: ' + f.transform)));
  });

  await scenario('antenna whip: a damped swing after the first target, capped at 16 degrees', () => {
    const { z } = load('system');
    const m = mascot('front');
    const P = softParts(m);
    const rot = (f) => +/rotate\((-?[\d.]+)deg\)/.exec(f.transform)[1];
    const tr = z.compileBeats(z.clipInfo('hop').beats, P, { facing: 'r' });
    const a = trackOf(tr, P.antL);
    const D = z.clipInfo('hop').dur;
    a.forEach((f) => assert.ok(Math.abs(rot(f)) <= 16 + 1e-9, 'capped at 16 degrees'));
    // an isolated beat: target v 80 ms after its end, then -0.4 v and +0.15 v, then rest, before the next beat's own target
    const beats = [{ pose: 'stand', y: -6, ms: 100, ease: 'out' }, { pose: 'stand', ms: 500, ease: 'io' }];
    const f = trackOf(z.compileBeats(beats, P, { facing: 'r' }), P.antL);
    const D2 = 100 + 500 + z.clipInfo('hop').tail;
    const at = (t) => f.find((x) => Math.abs(x.offset * D2 - t) < 1.5);
    const v = rot(at(180));
    assert.ok(Math.abs(v - -9) < 0.01, 'the target is 1.5 x dy, at +80 ms');
    assert.ok(Math.abs(rot(at(270)) - 0.4 * 9) < 0.06 && Math.abs(rot(at(350)) - 0.15 * -9) < 0.06 && Math.abs(rot(at(430))) < 0.06, 'then -0.4 v, +0.15 v, rest');
    const r = trackOf(z.compileBeats(beats, P, { facing: 'r' }), P.antR);
    assert.strictEqual(rot(r[1]), -rot(f[1]), 'the right antenna mirrors it');
  });

  await scenario('soft off switch: html[data-zorp-soft="off"] drops the whole layer (E8 clips again), anything else leaves it on', async () => {
    const { z, html } = load('system');
    const m = mascot('front');
    const P = softParts(m);
    const kinds = (tr) => tr.map((t) => t[0]);
    const beats = z.clipInfo('fist-pump').beats;
    const on = z.compileBeats(beats, P, { facing: 'r' });
    ['body', 'face', 'ride', 'cheeks'].forEach((k) => assert.ok(kinds(on).includes(P[k]), k + ' is driven'));
    html.setAttribute('data-zorp-soft', 'off');
    const off = z.compileBeats(beats, P, { facing: 'r' });
    ['body', 'face', 'ride', 'cheeks', 'hatRide'].forEach((k) => assert.ok(!kinds(off).includes(P[k]), k + ' is left alone when the switch is off'));
    // the antenna is the single E8 overshoot again: one target per beat plus the first and last frames
    assert.strictEqual(trackOf(off, P.antL).length, beats.length + 3, 'no whip tail (first frame, one target per beat, the closing frame and the engine\'s end frame)');
    html.setAttribute('data-zorp-soft', 'on');
    assert.ok(kinds(z.compileBeats(beats, P, { facing: 'r' })).includes(P.body), 'only the exact value off switches it');
    html.removeAttribute('data-zorp-soft');
    assert.ok(kinds(z.compileBeats(beats, P, { facing: 'r' })).includes(P.body));
    // played for real, the switch leaves one animation per part and nothing on the body
    html.setAttribute('data-zorp-soft', 'off');
    z.bind(m.host);
    z.idle(false, m.host);
    animations = [];
    z.play('fist-pump', { el: m.host });
    assert.ok(!animations.some((a) => a.el === P.body || a.el === P.face || a.el === P.ride), 'no soft animation runs with the switch off');
    html.removeAttribute('data-zorp-soft');
    z.play('fist-pump', { el: m.host });
    assert.ok(animations.some((a) => a.el === P.body) && animations.some((a) => a.el === P.face) && animations.some((a) => a.el === P.ride), 'and all of them run with it on');
    z.play('blink', { el: m.host });
    assert.strictEqual(P.body.style.transform || '', '', 'stop() leaves the body at rest');
    assert.strictEqual(m.part('.zorp-face').style.transform || '', '');
  });

  await scenario('soft body under reduced and off: no soft animation and nothing left on the body or face', async () => {
    for (const level of ['reduced', 'off']) {
      const { z } = load(level);
      const m = mascot('front');
      z.bind(m.host);
      animations = [];
      for (const name of SOFT_CLIPS) { z.play(name, { el: m.host }); await advance(50); }
      assert.strictEqual(animations.length, 0, level + ': no animate call at all');
      ['.buddy-body', '.zorp-face', '.zorp-ride', '.zorp-slot--cheeks'].forEach((sel) => assert.strictEqual(m.part(sel).style.transform || '', '', level + ' ' + sel));
      await advance(2000);
    }
  });

  await scenario('play(): one animate() per part, at the clip length, and stop()/a newer clip cancels everything and restores the rest', async () => {
    for (const name of SOFT_CLIPS.filter((c) => c !== 'bow')) {
      const { z } = load('system');
      const m = mascot('front');
      z.bind(m.host);
      z.idle(false, m.host);
      const info = z.clipInfo(name);
      const p = z.play(name, { el: m.host });
      const clip = animations.filter((a) => a.opts.duration === info.dur);
      const targets = clip.map((a) => a.el);
      assert.strictEqual(new Set(targets).size, targets.length, name + ': two animate() calls on one part');
      assert.ok(clip.length >= (name === 'think-chin' ? 1 : 2), name + ' animates');
      assert.ok(clip.every((a) => !a.opts.composite), name + ': front view, no composite');
      // run a few beat boundaries, then cut it short
      await advance(300);
      const before = animations.slice();
      z.play('blink', { el: m.host });
      await flush();
      assert.ok(before.filter((a) => a.opts.duration === info.dur).every((a) => a.canceled), name + ': every part animation is cancelled');
      assert.strictEqual(await p, true, 'run() resolves');
      assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r') && armIs(m, '.buddy-arm--l', 'rest', 'l') && armIs(m, '.buddy-arm--r-front', 'rest', 'r'), name + ': arm shapes back to rest');
      assert.strictEqual(m.host.getAttribute('data-face'), 'nudge', name + ': face restored');
      assert.strictEqual(timersCount(), 0, name + ': no timers left');
      assert.strictEqual(m.part('.buddy-root').style.transform || '', '');
      assert.strictEqual(live().filter((a) => a.opts.duration === info.dur).length, 0);
    }
  });

  await scenario('fist-pump: crouch anticipation, fist thrust with stretch and overshoot, landing squash, hold, settle, joy with sparkles', async () => {
    const { z } = load('system');
    const info = z.clipInfo('fist-pump');
    const b = info.beats;
    assert.strictEqual(b[0].pose, 'crouch');
    assert.strictEqual(b[0].expr, 'determined');
    assert.ok(b[0].ms >= 80 && b[0].ms <= 150, 'anticipation of 80-150 ms');
    const up = b.findIndex((x) => x.pose === 'fist-up' && x.y <= -8);
    assert.ok(up > 0, 'a jump beat with the fist up');
    assert.ok(b[up].s[0] < 1 && b[up].s[1] > 1, 'stretch on take-off');
    assert.strictEqual(b[up].aease, 'overshoot', 'the fist overshoots');
    assert.ok(b[up].hold >= 180, 'the apex holds at least 180 ms');
    assert.strictEqual(b[up].expr, 'joy');
    assert.strictEqual(z.channelsOf('joy').fx, 'sparkles');
    assert.ok(b[up + 1].s[0] > 1 && b[up + 1].s[1] < 1 && b[up + 1].pose === 'fist-up', 'landing squash with the fist still up');
    assert.ok(b[up + 2].pose === 'fist-up' && b[up + 2].hold >= 150 && b[up + 2].hr, 'victorious hold with a head tilt');
    assert.strictEqual(b[b.length - 1].pose, 'stand');
    assert.strictEqual(b[b.length - 1].expr, 'grin');
    // runtime: the fist shows during the pump and the face follows the beats
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    z.play('fist-pump', { el: m.host });
    assert.strictEqual(m.host.getAttribute('data-face'), 'determined');
    await advance(b[0].ms + 10);
    assert.strictEqual(m.host.getAttribute('data-face'), 'joy');
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'joy');
    assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r'), 'the long fist waits for the arm to swing up (no fist at foot level)');
    await advance(100);
    assert.strictEqual(m.part('.buddy-arm--r-front').style.display, 'inline', 'the raised fist is drawn in front of the body');
    assert.strictEqual(m.part('.buddy-arm--r').style.display, 'none');
    assert.ok(armIs(m, '.buddy-arm--r', 'fist', 'r') && armIs(m, '.buddy-arm--r-front', 'fist', 'r'), 'a round fist on the right arm (both layers)');
    assert.ok(armIs(m, '.buddy-arm--l', 'rest', 'l'));
    const settleAt = b.slice(0, -1).reduce((s, x) => s + x.ms + (x.hold || 0), 0);
    await advance(settleAt - (b[0].ms + 110) + 20);
    assert.strictEqual(m.host.getAttribute('data-face'), 'grin');
    await advance(200);
    assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r'), 'the arm is back to rest for the settle');
    assert.strictEqual(m.part('.buddy-arm--r').style.display || '', '', 'and behind the body again');
    // the arm animation carries the thrust: one arm tween with an overshoot easing
    const armAnim = animations.find((a) => a.el === m.part('.buddy-arm--r') && a.opts.duration === info.dur);
    assert.ok(armAnim && armAnim.frames.some((f) => /overshoot|1\.56/.test(f.easing)), 'overshoot easing on the arm');
    assert.ok(armAnim.frames.some((f) => /rotate\(-165deg\)/.test(f.transform)), 'arm raised to the fist-up angle');
  });

  await scenario('beat boundaries: expression, fx and the thought bubble arrive on time, guarded by the sequence', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    z.play('dance', { el: m.host });
    assert.strictEqual(m.host.getAttribute('data-face'), 'laugh');
    assert.strictEqual(m.slot('fx').childNodes.length > 0, true, 'notes fx while dancing');
    await advance(600);
    assert.strictEqual(m.host.getAttribute('data-face'), 'laugh', 'still laughing mid-dance (fx carried over)');
    assert.ok(m.slot('fx').childNodes.length > 0, 'notes carried across beats');
    await advance(1400);
    assert.strictEqual(m.host.getAttribute('data-face'), 'nudge', 'the original face comes back at the end');
    // trip: embarrassed for one beat, then laughs it off and ends happy
    const t = load('system');
    const n = mascot('front');
    t.z.bind(n.host);
    t.z.idle(false, n.host);
    t.z.play('dance', { el: n.host, trip: true });
    await advance(790);
    assert.strictEqual(n.host.getAttribute('data-face'), 'embarrassed');
    await advance(260);
    assert.strictEqual(n.host.getAttribute('data-face'), 'laugh');
    await advance(450);
    assert.strictEqual(n.host.getAttribute('data-face'), 'happy');
    // a newer clip in the middle of a boundary wait: the stale timer must not repaint the face
    const s = load('system');
    const q = mascot('front');
    s.z.bind(q.host);
    s.z.idle(false, q.host);
    s.z.play('fist-pump', { el: q.host });
    s.z.play('wobble', { el: q.host });
    await advance(400);
    assert.notStrictEqual(q.host.getAttribute('data-face'), 'joy', 'stale beat timers are gone');
    // oops-encourage shows the thought bubble (full motion only)
    const o = load('system');
    const r = mascot('front');
    o.z.bind(r.host);
    o.z.idle(false, r.host);
    o.z.play('oops-encourage', { el: r.host });
    assert.strictEqual(r.host.getAttribute('data-face'), 'oops');
    await advance(260);
    assert.strictEqual(r.host.getAttribute('data-face'), 'determined');
    assert.ok(r.slot('fx').childNodes.length > 0, 'thought bubble drawn');
  });

  for (const level of ['reduced', 'off']) {
    await scenario('clips under ' + level + ': no animate calls; the preset shows, the view is untouched', async () => {
      const { z } = load(level);
      const m = mascot('front');
      z.bind(m.host);
      for (const name of SOFT_CLIPS) {
        const info = z.clipInfo(name);
        const p = z.play(name, { el: m.host });
        assert.strictEqual(m.host.getAttribute('data-face'), info.reducedFace, name + ' shows its reduced preset');
        eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
        assert.strictEqual(animations.length, 0, name + ' must not call animate');
        assert.strictEqual(m.part('.buddy-root').style.transform || '', '');
        await advance(2000);
        await p;
        assert.strictEqual(m.host.getAttribute('data-face'), 'nudge');
      }
      assert.strictEqual(await z.play('turn', { el: m.host }), false, 'turn is not required: no-op');
      if (level === 'reduced') {
        assert.strictEqual(await z.play('turn', { el: m.host, required: true }), true, 'turn required: instant');
        eq(z.viewOf(m.host), { view: 'side', facing: 'r' });
      }
      assert.strictEqual(animations.length, 0);
    });
  }

  await scenario('side view draws the profile paddle for a rest arm, any other shape stays, and the front view restores rest (side redesign 2026-09-30)', async () => {
    const { z } = load('reduced');
    const m = mascot('front');
    z.bind(m.host);
    assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r') && armIs(m, '.buddy-arm--r-front', 'rest', 'r'), 'front: the plain rest arm');
    assert.strictEqual(await z.turn('side', 'r', { el: m.host, required: true }), true);
    for (const sel of ['.buddy-arm--r', '.buddy-arm--r-front', '.buddy-arm--l']) assert.ok(armIs(m, sel, 'side-rest', sel.indexOf('--l') !== -1 ? 'l' : 'r'), sel + ': side-rest in the side view');
    assert.strictEqual(m.part('.buddy-arm--r-front').style.display, 'inline', 'the near arm is the one drawn');
    assert.strictEqual(await z.turn('front', 'r', { el: m.host, required: true }), true);
    assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r') && armIs(m, '.buddy-arm--r-front', 'rest', 'r') && armIs(m, '.buddy-arm--l', 'rest', 'l'), 'front again: rest arms restored');
  });

  await scenario('side view arm angles: sideRot equals zorp_rig.side_rot, poses and legacy clips lift the near arm over the top, the front view keeps its angles (2026-09-30)', async () => {
    const { z } = load('system');
    let rt = null;
    z.register((r) => { rt = r; });
    Object.keys(fx.sideRot).forEach((shape) => fx.sideRot[shape].forEach((want, i) => assert.strictEqual(rt.sideRot(i - 180, shape), want, shape + ' ' + (i - 180))));
    const m = mascot('front');
    z.bind(m.host);
    const arm = () => m.part('.buddy-arm--r-front').style.transform || '';
    const p = z.pose('wave', { el: m.host, view: 'side' });
    for (let i = 0; i < 4; i += 1) await finishAll();
    assert.strictEqual(await p, true);
    eq(z.viewOf(m.host), { view: 'side', facing: 'r' });
    assert.strictEqual(arm(), fx.sideArms.wave, 'the static render and the runtime draw the same profile arm');
    // a turn back to the front puts the front angle back (the post hook repaints the pose for the view)
    const t = z.turn('front', 'r', { el: m.host });
    for (let i = 0; i < 4; i += 1) await finishAll();
    assert.strictEqual(await t, true);
    assert.strictEqual(m.part('.buddy-arm--r').style.transform, 'rotate(-100deg)', 'front view: the pose angle unchanged');
    // think-chin in profile: the forward-reaching bent art; the front view gets the plain bent arm back
    const c = z.pose('think-chin', { el: m.host, view: 'side' });
    for (let i = 0; i < 4; i += 1) await finishAll();
    assert.strictEqual(await c, true);
    assert.ok(armIs(m, '.buddy-arm--r-front', 'side-bent', 'r'), 'side-bent in profile');
    const f = z.turn('front', 'r', { el: m.host });
    for (let i = 0; i < 4; i += 1) await finishAll();
    assert.strictEqual(await f, true);
    assert.ok(armIs(m, '.buddy-arm--r-front', 'bent', 'r'), 'bent again in the front view');
    // a legacy clip played in the side view: its arm frames are remapped, none keeps a front raise
    const s = z.pose('stand', { el: m.host, view: 'side' });
    for (let i = 0; i < 4; i += 1) await finishAll();
    assert.strictEqual(await s, true);
    animations = [];
    z.play('wave', { el: m.host });
    const armFrames = animations.filter((a) => a.el === m.part('.buddy-arm--r-front')).map((a) => a.frames.map((k) => k.transform).join(' '));
    // wave is a beat clip since 2026-10-02 (reach arm, -120 and -176 in front): in profile it swings between 190 and 182.6, never the front angles
    assert.ok(armFrames.length === 1 && armFrames[0].indexOf('rotate(190deg)') !== -1 && armFrames[0].indexOf('rotate(182.6deg)') !== -1 && !/-1(20|76)/.test(armFrames[0]), armFrames.join(' / '));
    // a beat clip in the side view compiles profile angles (fist-pump: the fist held near vertical)
    animations = [];
    z.play('fist-pump', { el: m.host });
    const pump = animations.filter((a) => a.el === m.part('.buddy-arm--r-front')).map((a) => a.frames.map((k) => k.transform).join(' ')).join(' ');
    assert.ok(pump.indexOf('rotate(187deg)') !== -1 && pump.indexOf('-165') === -1, pump);
    const eases = animations.filter((a) => a.el === m.part('.buddy-arm--r-front')).map((a) => a.frames.map((k) => k.easing).join(' ')).join(' ');
    assert.ok(eases.indexOf('1.56') === -1, 'no overshoot on a profile raise (it would tip the arm into the face): ' + eases);
    z.play('blink', { el: m.host });
  });

  await scenario('pose(): full motion tweens to the resting pose with the arm shape, and stop() leaves it in place', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    const p = z.pose('fist-up', { el: m.host, expr: true });
    await flush();
    assert.strictEqual(m.host.getAttribute('data-face'), 'grin', 'the pose preset when asked for');
    assert.ok(armIs(m, '.buddy-arm--r', 'fist', 'r'), 'the fist is drawn');
    assert.strictEqual(m.part('.buddy-arm--r-front').style.transform, 'rotate(-165deg)');
    assert.strictEqual(m.svg.getAttribute('data-pose'), 'fist-up', 'data-pose follows the pose');
    assert.ok(/rotate\(4deg\)/.test(m.part('.buddy-root').style.transform), 'leans toward the raised side');
    const tweens = animations.filter((a) => a.opts.duration === 240);
    assert.ok(tweens.length >= 2 && tweens.every((a) => !a.opts.composite), 'replace-composite tweens');
    await finishAll();
    assert.strictEqual(await p, true);
    // a legacy clip on a posed Zorp layers on top of the pose (composite add) instead of snapping
    animations = [];
    z.play('wobble', { el: m.host });   // a legacy clip (wave, cheer and hop became beat clips, which start from stand)
    assert.ok(animations.filter((a) => a.opts.composite === 'add').length >= 2, 'clips add to the resting pose');
    z.play('blink', { el: m.host });
    assert.strictEqual(m.part('.buddy-arm--r').style.transform, 'rotate(-165deg)', 'the pose survives stop()');
    // back to stand: identity written as no inline transform, rest shape back
    const back = z.pose('stand', { el: m.host });
    await flush();
    await finishAll();
    assert.strictEqual(await back, true);
    assert.strictEqual(m.part('.buddy-arm--r').style.transform || '', '');
    assert.strictEqual(m.part('.buddy-root').style.transform || '', '');
    assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r'));
    // think-chin draws the front-layer twin over the body and hides the back twin; a turn keeps it that way
    const c = z.pose('think-chin', { el: m.host });
    await flush();
    await finishAll();
    await c;
    assert.strictEqual(m.part('.buddy-arm--r').style.display, 'none');
    assert.strictEqual(m.part('.buddy-arm--r-front').style.display, 'inline');
    assert.ok(armIs(m, '.buddy-arm--r-front', 'bent', 'r'));
    const s = z.pose('stand', { el: m.host });
    await flush();
    await finishAll();
    await s;
    assert.strictEqual(m.part('.buddy-arm--r-front').style.display, 'none', 'front twin hidden again');
    assert.strictEqual(m.part('.buddy-arm--r').style.display, '');
  });

  await scenario('pose() with a default view turns first (bow, sit); unknown poses refuse', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    assert.strictEqual(await z.pose('nonsense', { el: m.host }), false);
    const p = z.pose('bow', { el: m.host, facing: 'l' });
    await flush();
    animations.find((a) => a.opts.duration === 150).finish();
    for (let i = 0; i < 6; i += 1) await finishAll();
    assert.strictEqual(await p, true);
    eq(z.viewOf(m.host), { view: 'side', facing: 'l' });
    assert.ok(/rotate\(-18deg\)/.test(m.part('.buddy-root').style.transform), 'facing left leans the other way');
    const q = z.pose('stand', { el: m.host, view: 'front' });
    for (let i = 0; i < 8; i += 1) { animations.filter((a) => a.opts.duration === 150).forEach((a) => a.finish()); await finishAll(); }
    await q;
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
  });

  for (const level of ['reduced', 'off']) {
    await scenario('pose() under ' + level + ': no limb, view or animate changes; the preset only on request; stand clears instantly', async () => {
      const { z } = load(level);
      const m = mascot('posed');
      z.bind(m.host);
      assert.strictEqual(await z.pose('flex', { el: m.host }), false, 'nothing to do without a preset');
      assert.strictEqual(m.part('.buddy-arm--r-front').style.transform, 'rotate(-165deg)', 'the static pose is untouched');
      assert.strictEqual(await z.pose('bow', { el: m.host, expr: true }), true, 'the preset is applied');
      assert.strictEqual(m.svg.getAttribute('data-expr'), 'bashful');
      eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
      assert.strictEqual(await z.pose('stand', { el: m.host }), true, 'a return to stand clears instantly');
      assert.strictEqual(m.part('.buddy-arm--r').style.transform || '', '');
      assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r'));
      assert.strictEqual(animations.length, 0, level + ' must not call animate');
    });
  }

  await scenario('a statically posed mascot (pose=) is picked up by bind(); beat clips start from stand', async () => {
    const { z } = load('system');
    const m = mascot('posed');
    z.bind(m.host);
    animations = [];
    z.play('shrug', { el: m.host });
    assert.strictEqual(m.part('.buddy-arm--r').style.transform || '', '', 'the static pose was cleared for the beat clip');
    await advance(120);
    assert.ok(armIs(m, '.buddy-arm--r', 'palm', 'r'), 'the fist gave way to the shrug arms (open palms)');
    assert.strictEqual(m.svg.getAttribute('data-pose'), null, 'the clip starts from stand: no data-pose');
    assert.ok(animations.filter((a) => a.opts.composite).length === 0);
  });

  await scenario('bow: the side view is entered and left around the beats (viewClip); stop() mid-way restores the front', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    const done = z.play('bow', { el: m.host });
    await flush();
    animations.find((a) => a.opts.duration === 150).finish();
    await flush();
    eq(z.viewOf(m.host), { view: 'side', facing: 'r' });
    z.play('blink', { el: m.host });
    await flush();
    assert.strictEqual(await done, false);
    eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
    assert.ok(armIs(m, '.buddy-arm--r', 'rest', 'r'));
  });

  await scenario('a beat clip on a Zorp already facing left mirrors the root (it sits outside the flip)', async () => {
    const { z } = load('system');
    const m = mascot('sideL');
    z.bind(m.host);
    z.idle(false, m.host);
    const info = z.clipInfo('fist-pump');
    z.play('fist-pump', { el: m.host });
    const root = animations.find((a) => a.el === m.part('.buddy-root') && a.opts.duration === info.dur);
    assert.ok(root && root.frames.some((f) => /rotate\(-4deg\)/.test(f.transform)), 'leans toward the raised (mirrored) side');
    assert.ok(!root.frames.some((f) => /rotate\(4deg\)/.test(f.transform)), 'no unmirrored lean');
  });

  await scenario('turn clip: full pinch-turn; leaves the view turned like pbZorp.turn', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    const p = z.play('turn', { el: m.host, view: 'three-quarter' });
    await flush();
    animations.find((a) => a.opts.duration === 150).finish();
    for (let i = 0; i < 5; i += 1) await finishAll();
    assert.strictEqual(await p, true);
    eq(z.viewOf(m.host), { view: 'three-quarter', facing: 'r' });
  });

  // ---- E8 Phase 5: react() plan ----
  const SMALL_CORRECT = ['cheer', 'hop', 'wave'];
  const BIG_KINDS = ['streak', 'first_correct', 'milestone', 'lesson_complete'];
  const tick = (ms) => { clock.t += ms; return clock.t; };

  await scenario('react plan: correct rotates the small clips and positive faces, never repeats either, never a big clip', () => {
    const { z } = load('system');
    let prev = { clip: '', face: '' };
    const faces = new Set();
    const clips = new Set();
    for (let i = 0; i < 80; i += 1) {
      const p = z.reactPlan('correct', tick(1000), true);
      assert.ok(SMALL_CORRECT.indexOf(p.clip) !== -1, 'small clip only: ' + p.clip);
      assert.strictEqual(p.big, false);
      assert.ok(z.allowedIn('react.correct', p.face) && val(z, p.face) === 'positive', 'face from CONTEXT_MAP react.correct: ' + p.face);
      assert.notStrictEqual(p.clip, prev.clip, 'clip repeats');
      assert.notStrictEqual(p.face, prev.face, 'face repeats');
      prev = p; faces.add(p.face); clips.add(p.clip);
    }
    assert.ok(faces.size >= 4 && clips.size === 3, 'the whole rotation is used: ' + [...faces] + ' / ' + [...clips]);
    ['grin', 'joy', 'happy', 'smug'].forEach((f) => assert.ok(faces.has(f), f));
  });

  await scenario('react plan: the public reactPlan hook is read-only unless asked to keep (a probe never delays a real reaction)', () => {
    const { z } = load('system');
    const a = z.reactPlan('streak', tick(60000));
    assert.strictEqual(a.clip, 'fist-pump');
    const b = z.reactPlan('streak', tick(500));
    assert.strictEqual(b.clip, 'fist-pump', 'the probe armed no gap guard and no big-clip window');
    const c = z.reactPlan('streak', tick(500), true);
    assert.strictEqual(c.clip, 'fist-pump');
    assert.strictEqual(z.reactPlan('streak', tick(500)), false, 'a kept plan does arm the big-clip window');
  });

  await scenario('react plan: wrong is oops-encourage (oops first beat <= 300 ms, resolves positive), no face override, no blush', () => {
    const { z } = load('system');
    for (let i = 0; i < 5; i += 1) {
      const p = z.reactPlan('wrong', tick(1000), true);
      assert.strictEqual(p.clip, 'oops-encourage');
      assert.strictEqual(p.big, false);
      assert.strictEqual(p.face, undefined);
    }
    const info = z.clipInfo('oops-encourage');
    const exprs = info.beats.filter((b) => b.expr).map((b) => b.expr);
    eq(exprs, ['oops', 'determined', 'soft-smile']);
    assert.ok(info.beats[0].ms + info.beats[0].hold <= 300, 'oops is the first beat only, 300 ms at most');
    exprs.slice(1).forEach((e) => { assert.notStrictEqual(e, 'oops'); assert.ok(z.allowedIn('react.wrong', e), e); });
    assert.strictEqual(val(z, exprs[exprs.length - 1]), 'positive');
    exprs.forEach((e) => { ['sad', 'aww-teary', 'embarrassed', 'dizzy', 'bashful', 'confused'].forEach((n) => assert.notStrictEqual(e, n)); });
    assert.ok(info.beats.some((b) => b.fx === 'thought'), 'the thought bubble is one of its beats (no separate opts.thought)');
  });

  await scenario('react plan: a big clip only for the rarer kinds, with a minimum gap between them and no stacking', () => {
    const { z } = load('system');
    const table = { streak: 'fist-pump', first_correct: 'victory', lesson_complete: 'dance' };
    Object.keys(table).forEach((kind) => {
      const { z: zz } = load('system');
      const p = zz.reactPlan(kind, tick(60000), true);
      assert.strictEqual(p.clip, table[kind], kind);
      assert.strictEqual(p.big, true, kind);
      // the dance (lesson_complete only) was lengthened to about 1.8 s in the readability pass; the other big clips keep the 1.5 s ceiling
      assert.ok(p.dur >= 700 && p.dur <= (kind === 'lesson_complete' ? 2000 : 1500), kind + ' dur ' + p.dur);
    });
    const a = z.reactPlan('streak', tick(60000), true);
    assert.strictEqual(a.clip, 'fist-pump');
    assert.strictEqual(z.reactPlan('milestone', tick(400), true), false, 'a big clip still playing is never cut short by another reaction');
    const soon = z.reactPlan('streak', tick(a.dur + 500), true);
    assert.strictEqual(soon.clip, 'cheer', 'inside the minimum gap a second big moment becomes a small cheer');
    assert.strictEqual(soon.big, false);
    assert.ok(z.allowedIn('react.streak', soon.face) && val(z, soon.face) === 'positive');
    const later = z.reactPlan('streak', tick(8000), true);
    assert.strictEqual(later.clip, 'fist-pump', 'after the gap it is allowed again');
    // correct answers are never big, however many and however spaced
    const { z: z2 } = load('system');
    for (let i = 0; i < 200; i += 1) assert.strictEqual(z2.reactPlan('correct', tick(20000), true).big, false);
  });

  await scenario('react plan: milestone alternates flex (proud) and a wave with a positive face; lesson_complete dances with love, never tripping', () => {
    const { z } = load('system');
    const seen = new Set();
    for (let i = 0; i < 12; i += 1) {
      const p = z.reactPlan('milestone', tick(60000), true);
      seen.add(p.clip);
      assert.ok(['flex', 'wave'].indexOf(p.clip) !== -1, p.clip);
      if (p.clip === 'wave') assert.ok(z.allowedIn('react.milestone', p.face) && val(z, p.face) === 'positive', 'wave face ' + p.face);
      else assert.strictEqual(p.big, true);
    }
    assert.strictEqual(seen.size, 2, 'both milestone clips are used');
    const d = z.reactPlan('lesson_complete', tick(60000), true);
    assert.strictEqual(d.clip, 'dance');
    assert.strictEqual(d.face, 'love');
    eq(d.map, { laugh: 'love' });
    assert.ok(z.allowedIn('react.lesson_complete', d.face));
    assert.strictEqual(d.trip, undefined, 'a reaction never asks for the trip');
    assert.strictEqual(z.reactPlan('nonsense', tick(1), true), null);
  });

  await scenario('react plan: every clip and face any kind can produce exists and is allowed for that kind', () => {
    const { z } = load('system');
    ['correct', 'wrong', 'streak', 'first_correct', 'milestone', 'lesson_complete'].forEach((kind) => {
      for (let i = 0; i < 30; i += 1) {
        const p = z.reactPlan(kind, tick(60000), true);
        assert.ok(z.hasClip(p.clip), p.clip);
        if (p.face) assert.ok(z.allowedIn('react.' + kind, p.face) && val(z, p.face) !== 'negative', kind + ' ' + p.face);
        const info = z.clipInfo(p.clip);
        if (info.beats) {
          const exprs = info.beats.filter((b) => b.expr).map((b) => (p.map && p.map[b.expr]) || b.expr);
          exprs.forEach((e) => assert.ok(z.allowedIn('react.' + kind, e) || (kind === 'wrong' && e === 'oops'), kind + ' beat ' + e));
          // E9 Phase 2: cheer and hop carry their face as the clip's own preset (react() may replace it with a positive one), not in a beat
          assert.strictEqual(val(z, exprs.length ? exprs[exprs.length - 1] : info.face), 'positive', p.clip + ' ends positive');
        }
      }
    });
  });

  await scenario('react(): wrong at full motion is oops, then determined, then soft-smile; nothing left running', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    const r = z.react('wrong', { el: m.host });
    assert.ok(animations.length > 0, 'animates at full motion');
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'oops');
    await advance(300);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'determined');
    await advance(400);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'soft-smile');
    await finishAll();
    await advance(400);
    assert.strictEqual(await r, true);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'nudge', 'back on the resting nudge face');
    assert.strictEqual(live().length, 0);
  });

  await scenario('react(): reduced shows only the preset and pulse (no animate calls), off does nothing at all', async () => {
    ['reduced', 'off'].forEach((level) => {
      ['wrong', 'correct', 'streak', 'milestone', 'lesson_complete', 'first_correct'].forEach((kind) => {
        const { z } = load(level);
        const m = mascot('front');
        z.bind(m.host);
        tick(60000);
        const p = z.react(kind, { el: m.host });
        assert.strictEqual(animations.length, 0, level + ' ' + kind + ' made animate calls');
        if (level === 'off') p.then((v) => assert.strictEqual(v, false));
        else assert.ok(m.svg.getAttribute('data-expr') && val(z, m.svg.getAttribute('data-expr')) !== 'negative', level + ' ' + kind + ' face');
        assert.strictEqual(m.part('.buddy-root').style.transform || '', '');
      });
    });
    const { z } = load('reduced');
    const m = mascot('front');
    z.bind(m.host);
    z.react('wrong', { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'determined', 'reduced wrong shows determined, never oops');
    await advance(3000);
  });

  await scenario('react(): a big reaction is not cut short by the next correct answer (min-gap and protect window)', async () => {
    const { z } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    tick(60000);
    z.react('streak', { el: m.host });
    const n = animations.length;
    assert.ok(n > 4);
    tick(1000);
    assert.strictEqual(await z.react('correct', { el: m.host }), false, 'the fist-pump (about 1.2 s) outlasts the 900 ms reaction gap');
    assert.strictEqual(animations.length, n);
    assert.ok(animations.every((a) => !a.canceled));
    tick(1200);
    z.react('correct', { el: m.host });
    assert.ok(animations.length > n, 'once it is over, reactions play again');
  });

  await scenario('visibilitychange: hiding the page stops the clip and face timers, so a transient oops is never on screen on return', async () => {
    const { z, sandbox } = load('system');
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    const from = animations.length;
    z.react('wrong', { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'oops');
    sandbox.document.hidden = true;
    sandbox.docListeners.filter((l) => l[0] === 'visibilitychange').forEach((l) => l[1]());
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'nudge', 'back on the resting face at once');
    assert.strictEqual(animations.slice(from).filter((a) => !a.canceled && a.state !== 'finished' && a.opts.duration > 200).length, 0, 'no clip animation left running (only the 80-90 ms face swap back to rest)');
    sandbox.document.hidden = false;
    await advance(2000);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'nudge', 'no stale timer repaints a reaction face');
  });

  await scenario('react(): without zorp-poses.js the E7 table still answers (wobble, cheer, weak_topic face)', async () => {
    const { z } = load('system', { poses: false });
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    tick(60000);
    z.react('wrong', { el: m.host });
    assert.ok(animations.length > 0);
    assert.strictEqual(typeof z.reactPlan, 'undefined');
  });

  // ---- E8 Phase 5: /welcome wiring against the real runtime ----
  if (welcomePath) {
    const welcomeSrc = fs.readFileSync(welcomePath, 'utf8');
    const boot = (step, motion, svgKind) => {
      const m = mascot(svgKind || 'front');
      const section = new El('section', { id: 'welcome', 'data-step': step });
      const byId = { welcome: section };
      const env = { byId, query: { '[data-welcome-hero]': [m.host] } };
      let form = null;
      let cards = [];
      if (step === 'topic') {
        form = new El('form', { id: 'welcome-topic-form' });
        cards = [new El('button', { name: 'topic', value: 'a' }), new El('button', { name: 'topic', value: 'b' })];
        cards.forEach((c) => form.appendChild(c));
        form.requestSubmit = (btn) => { form.submitted = btn; };
        byId['welcome-topic-form'] = form;
      }
      const rt = load(motion, env);
      rt.sandbox.window.localStorage = undefined;
      vm.runInContext(welcomeSrc, rt.sandbox);
      return { z: rt.z, m, form, cards };
    };

    await scenario('welcome hello (full): hero (server-drawn front) drops to profile at once, turns in after a beat, then waves; ends on the front view', async () => {
      const { z, m } = boot('hello', 'system');
      eq(z.viewOf(m.host), { view: 'side', facing: 'r' });
      assert.strictEqual(animations.length, 0, 'nothing moves before the beat');
      await advance(360);
      assert.ok(animations.length > 0, 'the pinch-turn starts');
      for (let i = 0; i < 8; i += 1) { await finishAll(); await advance(200); }
      eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
      assert.ok(animations.some((a) => a.frames.some((f) => /rotate\(-176deg\)/.test(f.transform || ''))), 'the wave raised an arm');
    });

    for (const level of ['reduced', 'off']) {
      await scenario('welcome hello (' + level + '): turned to the front at once, no animate calls, never left sideways', async () => {
        const { z, m } = boot('hello', level);
        await flush();
        eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
        await advance(2000);
        assert.strictEqual(animations.length, 0, level + ' must not animate');
        eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
      });
    }

    await scenario('welcome level (full): side-point down, then back to the front; off: no animation and front', async () => {
      const { z, m } = boot('level', 'system');
      assert.ok(animations.length > 0, 'turns to the side');
      for (let i = 0; i < 10; i += 1) { await finishAll(); await advance(200); }
      eq(z.viewOf(m.host), { view: 'front', facing: 'r' });
      const off = boot('level', 'off');
      await advance(2000);
      assert.strictEqual(animations.length, 0);
      eq(off.z.viewOf(off.m.host), { view: 'front', facing: 'r' });
    });

    await scenario('welcome topic: think-chin after 400 ms; a card tap plays the fist-pump and submits inside the 450 ms race', async () => {
      const { z, m, form, cards } = boot('topic', 'system');
      assert.strictEqual(animations.length, 0);
      await advance(410);
      assert.ok(animations.length > 0, 'think-chin animates');
      assert.strictEqual(m.svg.getAttribute('data-expr'), 'thinking');
      await finishAll();
      await advance(400);
      animations = [];
      const evt = cards[0].click();
      assert.strictEqual(evt.prevented, true, 'the tap is held for the jump');
      assert.ok(animations.length > 4, 'fist-pump animations');
      const root = animations.find((a) => a.el === m.part('.buddy-root'));
      assert.ok(root && root.frames.some((f) => /translate\([-\d.]+px,-1[0-9](\.\d+)?px\)/.test(f.transform)), 'it jumps');
      assert.strictEqual(form.submitted, undefined, 'not yet');
      await advance(460);
      assert.strictEqual(form.submitted, cards[0], 'submitted after the race');
      cards[1].click();
      assert.strictEqual(form.submitted, cards[0], 'a second tap is ignored while submitting');
    });

    await scenario('welcome topic (reduced/off): the tap submits plainly, no jump, no think-chin animation', async () => {
      for (const level of ['reduced', 'off']) {
        const { form, cards } = boot('topic', level);
        await advance(500);
        assert.strictEqual(animations.length, 0, level);
        const evt = cards[0].click();
        assert.strictEqual(evt.prevented, false, level + ' leaves the plain submit alone');
        assert.strictEqual(animations.length, 0, level);
        assert.strictEqual(form.submitted, undefined);
      }
    });

    await scenario('welcome: without zorp-poses.js each step falls back to its E7 clip (point, think, cheer)', async () => {
      const m = mascot('front');
      const section = new El('section', { id: 'welcome', 'data-step': 'topic' });
      const form = new El('form', { id: 'welcome-topic-form' });
      const card = new El('button', { name: 'topic', value: 'a' });
      form.appendChild(card);
      form.requestSubmit = (b) => { form.submitted = b; };
      const rt = load('system', { poses: false, byId: { welcome: section, 'welcome-topic-form': form }, query: { '[data-welcome-hero]': [m.host] } });
      vm.runInContext(welcomeSrc, rt.sandbox);
      await advance(410);
      assert.ok(animations.length > 0, 'think still plays');
      await finishAll();
      animations = [];
      card.click();
      assert.ok(animations.length > 0, 'cheer still plays');
      await advance(460);
      assert.strictEqual(form.submitted, card);
    });
  }

  // ---- E8 Phase 5: data-zorp-autoplay allowlist ----
  if (triggersPath) {
    const trigSrc = fs.readFileSync(triggersPath, 'utf8');
    const run = (clips) => {
      const played = [];
      const els = clips.map((c) => new El('span', { 'data-zorp-autoplay': c }));
      const sb = {
        document: { readyState: 'complete', addEventListener() {}, querySelectorAll: () => els },
        setTimeout: fakeST, Date,
        console,
      };
      sb.window = sb;
      sb.pbZorp = { play: (name) => { played.push(name); return Promise.resolve(true); } };
      vm.runInNewContext(trigSrc, sb);
      return played;
    };
    await scenario('autoplay allowlist: only positive or neutral clips start from markup; everything else is ignored', () => {
      const ok = ['think', 'think-chin', 'shrug', 'peek', 'wave', 'nod', 'wink', 'float', 'hop', 'cheer', 'flex', 'side-point'];
      eq(run(ok), ok);
      const bad = ['wobble', 'oops-encourage', 'sleep', 'dance', 'shake', 'turn', 'bow', 'fist-pump', 'victory', '__proto__', 'constructor', 'toString', 'nonsense'];
      eq(run(bad), []);
    });
  }

  // ---- E9 Phase 4: cue beats (docs/ZORP_CHARM.md 3.4.2). The sound itself and its gate are tested in zorp_sound_harness.js ----
  const CUED = {
    cheer: [['jump', 'start', 1], ['land', 'end', 2]], 'fist-pump': [['jump', 'start', 1], ['land', 'end', 2]],
    victory: [['jump', 'start', 1], ['land', 'end', 2]], dance: [['jump', 'start'], ['land', 'end']],
    flex: [['tada', 'start', 0]], wave: [['tada', 'start', 0]],
  };
  const spyOn = (sandbox) => { const calls = []; sandbox.pbSound = { zorp: (c) => { calls.push([c, now]); return true; } }; return calls; };
  const expected = (z, name) => {
    let t = 0;
    const out = [];
    z.clipInfo(name).beats.forEach((b) => {
      if (b.cue) out.push([b.cue, t + (b.cue === 'land' ? (b.ms || 0) : 0)]);
      t += (b.ms || 0) + (b.hold || 0);
    });
    return out;
  };

  await scenario('cue beats: with cue:true a jump or tada sounds at its beat start and a land at its beat end; none without cue', async () => {
    for (const name of Object.keys(CUED)) {
      const { z, sandbox } = load('system');
      const calls = spyOn(sandbox);
      const m = mascot('front');
      z.bind(m.host);
      z.idle(false, m.host);
      const want = expected(z, name);
      eq(want.map((w) => w[0]), CUED[name].map((w) => w[0]), name + ' cue names');
      z.play(name, { el: m.host, cue: true });
      await advance(z.clipInfo(name).dur + 100);
      eq(calls, want, name + ' cue times');
      if (name !== 'wave' && name !== 'flex') assert.ok(want[1][1] > want[0][1] + 200, name + ': the land comes after the take-off');
      // the same clip without cue:true is silent, and so is a clip played by anything else
      const quiet = load('system');
      const q = spyOn(quiet.sandbox);
      const m2 = mascot('front');
      quiet.z.bind(m2.host);
      quiet.z.idle(false, m2.host);
      quiet.z.play(name, { el: m2.host });
      await advance(quiet.z.clipInfo(name).dur + 100);
      eq(q, [], name + ' without cue');
    }
  });

  await scenario('cue beats: only the named beats carry a cue, and nothing else can ask for one', () => {
    const { z } = load('system');
    ['hop', 'shrug', 'think-chin', 'float', 'oops-encourage'].forEach((name) => {
      z.clipInfo(name).beats.forEach((b) => assert.strictEqual(b.cue, undefined, name + ' is silent'));
    });
    const bow = z.clipInfo('bow').beats.filter((b) => b.cue);
    eq(bow.map((b) => b.cue), ['tada']);
    const names = new Set();
    SOFT_CLIPS.forEach((name) => z.clipInfo(name).beats.forEach((b) => { if (b.cue) names.add(b.cue); }));
    eq([...names].sort(), ['jump', 'land', 'tada']);
    ['cheer', 'fist-pump', 'victory', 'dance'].forEach((name) => {
      const list = z.clipInfo(name).beats;
      const j = list.findIndex((b) => b.cue === 'jump');
      assert.ok(j !== -1 && list[j + 1] && list[j + 1].cue === 'land', name + ': a land is the beat right after its jump');
      assert.ok(list[j].y < 0 && list[j + 1].y > 0, name + ': the jump leaves the ground and the land touches it');
    });
  });

  await scenario('cue beats: none at reduced or off motion, none after a stop() mid-clip, none without the sound module', async () => {
    for (const level of ['reduced', 'off']) {
      const { z, sandbox } = load(level);
      const calls = spyOn(sandbox);
      const m = mascot('front');
      z.bind(m.host);
      z.idle(false, m.host);
      ['fist-pump', 'victory', 'flex', 'cheer', 'dance'].forEach((name) => z.play(name, { el: m.host, cue: true }));
      await advance(3000);
      eq(calls, [], level + ': the beat engine never starts, so no cue is scheduled');
    }
    const { z, sandbox } = load('system');
    const calls = spyOn(sandbox);
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    z.play('fist-pump', { el: m.host, cue: true });
    await advance(250);
    eq(calls.map((c) => c[0]), ['jump']);
    z.play('blink', { el: m.host });
    await advance(2000);
    eq(calls.map((c) => c[0]), ['jump'], 'stop() clears the pending land');
    const bare = load('system');   // no pbSound at all: a cue beat must not throw
    const b = mascot('front');
    bare.z.bind(b.host);
    bare.z.idle(false, b.host);
    bare.z.play('victory', { el: b.host, cue: true });
    await advance(2000);
  });

  await scenario('cue beats: bow (a side-view clip) passes cue through viewClip and sounds a tada once the turn is done', async () => {
    const { z, sandbox } = load('system');
    const calls = spyOn(sandbox);
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    const done = z.play('bow', { el: m.host, cue: true });
    await flush();
    for (let i = 0; i < 5; i += 1) { await finishAll(); await advance(1); }
    eq(calls.map((c) => c[0]), ['tada']);
    z.play('blink', { el: m.host });
    await flush();
    await done;
    const plain = load('system');
    const q = spyOn(plain.sandbox);
    const m2 = mascot('front');
    plain.z.bind(m2.host);
    plain.z.idle(false, m2.host);
    plain.z.play('bow', { el: m2.host });
    await flush();
    for (let i = 0; i < 5; i += 1) { await finishAll(); await advance(1); }
    eq(q, [], 'bow without cue:true is silent');
  });

  await scenario('react plan: only first_correct, milestone and lesson_complete ask for cues, and react() hands them to the clip', async () => {
    const { z, sandbox } = load('system');
    ['correct', 'wrong', 'streak'].forEach((kind) => {
      for (let i = 0; i < 10; i += 1) assert.strictEqual(z.reactPlan(kind, tick(60000), true).cue, false, kind);
    });
    ['first_correct', 'milestone', 'lesson_complete'].forEach((kind) => assert.strictEqual(z.reactPlan(kind, tick(60000), true).cue, true, kind));
    const calls = spyOn(sandbox);
    const m = mascot('front');
    z.bind(m.host);
    z.idle(false, m.host);
    tick(60000);
    z.react('lesson_complete', { el: m.host });
    await advance(2300);
    eq(calls.map((c) => c[0]), ['jump', 'land'], 'the corner dance sounds its hop');
    const s2 = load('system');
    const c2 = spyOn(s2.sandbox);
    const m2 = mascot('front');
    s2.z.bind(m2.host);
    s2.z.idle(false, m2.host);
    tick(60000);
    s2.z.react('streak', { el: m2.host });
    await advance(2300);
    eq(c2, [], 'a streak fist-pump never sounds a cue (the answer tones speak)');
    for (let i = 0; i < 6; i += 1) {
      tick(60000);
      s2.z.react('correct', { el: m2.host });
      await advance(1200);
      await finishAll();
    }
    eq(c2, [], 'correct answers (cheer, hop, wave) never sound a cue');
  });

  finished = true;
  const failed = results.filter((r) => !r[1]);
  if (failed.length) { console.error(`\n${failed.length}/${results.length} zorp poses scenarios FAILED`); process.exit(1); }
  console.log(`\nAll ${results.length} zorp poses scenarios passed.`);
  process.exit(0);
})();
