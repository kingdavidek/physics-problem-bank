'use strict';
/* E9 Phase 4: behavioural harness for static/js/sound.js (Zorp's cues, the gate rules of docs/ZORP_CHARM.md 3.4.3, the one-sound
   rule of 3.4.4 and the D7 blips), run by test_zorp_sound_smoke.py. A fake AudioContext records every oscillator, every gain
   automation and every connection; Date.now() is a virtual clock the scenarios move by hand. No browser, no audio.
   Usage: node zorp_sound_harness.js <sound.js> <celebrate.js> */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const [, , soundPath, celebratePath] = process.argv;
if (!soundPath || !celebratePath) {
  console.error('usage: node zorp_sound_harness.js <sound.js> <celebrate.js>');
  process.exit(2);
}
const SOUND_SRC = fs.readFileSync(soundPath, 'utf8');
const CELEBRATE_SRC = fs.readFileSync(celebratePath, 'utf8');
const tick = async () => { for (let i = 0; i < 6; i += 1) await new Promise((r) => setImmediate(r)); };

// The cue table of docs/ZORP_CHARM.md 3.4.2 (ms, Hz, peak gain). soft is the quietest answer tone.
const TABLE = { jump: { ms: 160, peak: 0.06 }, land: { ms: 90, peak: 0.06 }, tada: { ms: 300, peak: 0.06 } };
const SOFT = 0.08;

function load(o) {
  o = o || {};
  const clock = { t: 1e6 };
  const timers = [];
  const made = [];                       // every AudioContext
  const doc = { listeners: {}, hidden: !!o.hidden };
  const attrs = { zorp: o.zorp || 'off' };
  const bodyAttrs = {};
  if (o.sound) bodyAttrs['data-sound-enabled'] = '1';
  if (o.quiz) bodyAttrs['data-guide-quiz'] = '1';
  doc.documentElement = { getAttribute: (k) => (k === 'data-zorp-sound' ? attrs.zorp : null), setAttribute: (k, v) => { if (k === 'data-zorp-sound') attrs.zorp = v; } };
  doc.body = {
    getAttribute: (k) => (Object.prototype.hasOwnProperty.call(bodyAttrs, k) ? bodyAttrs[k] : null),
    setAttribute: (k, v) => { bodyAttrs[k] = String(v); },
    classList: { contains: () => false },
    appendChild() {},
  };
  doc.addEventListener = (type, fn, opts) => { (doc.listeners[type] = doc.listeners[type] || []).push({ fn, opts }); };
  doc.fire = (type) => (doc.listeners[type] || []).forEach((l) => l.fn({ type }));
  doc.getElementById = () => null;
  doc.querySelector = () => null;
  doc.querySelectorAll = () => [];
  doc.createElement = () => ({ style: { setProperty() {} }, setAttribute() {}, appendChild() {}, remove() {}, classList: { add() {}, remove() {} } });

  class Param {
    constructor(sink) { this.sink = sink; this.events = []; }
    set value(v) { this.events.push(['value', v, 0]); }
    setValueAtTime(v, t) { this.events.push(['set', v, t]); }
    exponentialRampToValueAtTime(v, t) { this.events.push(['ramp', v, t]); }
    linearRampToValueAtTime(v, t) { this.events.push(['lin', v, t]); }
    cancelScheduledValues(t) { this.events.push(['cancel', 0, t]); }
  }
  class Node {
    constructor(kind) { this.kind = kind; this.out = []; this.dead = false; }
    connect(n) { this.out.push(n); return n; }
    disconnect() { this.out = []; this.dead = true; this.cutAt = timers.length; }
  }
  class AudioContext {
    constructor() {
      this.state = 'suspended';
      this.currentTime = 10;
      this.destination = new Node('destination');
      this.oscs = [];
      this.gains = [];
      made.push(this);
    }
    resume() { this.state = 'running'; return Promise.resolve(); }
    createGain() { const g = new Node('gain'); g.gain = new Param(g); this.gains.push(g); return g; }
    createOscillator() {
      const n = new Node('osc');
      n.frequency = new Param(n);
      n.start = (t) => { n.startAt = t; };
      n.stop = (t) => { n.stopAt = t; };
      this.oscs.push(n);
      return n;
    }
  }
  const sandbox = {
    document: doc, Date: { now: () => clock.t }, Promise, Object, Math, JSON, console, Array, String, Number,
    setTimeout: (fn, ms) => { if (o.defer) timers.push({ fn, ms }); else fn(); return 0; }, clearTimeout() {},
  };
  sandbox.window = sandbox;
  if (o.audio !== false) sandbox.AudioContext = AudioContext;
  sandbox.matchMedia = () => ({ matches: false });
  sandbox.requestAnimationFrame = (fn) => fn();
  if (o.zorpRuntime) {
    sandbox.pbZorp = { motionLevel: () => o.zorpRuntime.level, hasPose: (n) => n === 'stand' && o.zorpRuntime.poses !== false, react() {} };
  }
  vm.runInNewContext(SOUND_SRC, sandbox);
  const flush = () => { while (timers.length) timers.shift().fn(); };
  return { sb: sandbox, pb: sandbox.pbSound, made, clock, doc, attrs, bodyAttrs, timers, flush };
}

// The gain automation of one oscillator's own gain node: [peak value, ramp end time, value at start]
function envelope(osc) {
  const amp = osc.out[0];
  const ev = amp.gain.events;
  const peaks = ev.filter((e) => e[0] === 'ramp').map((e) => e[1]);
  const times = ev.map((e) => e[2]);
  return { peak: Math.max(...peaks), last: Math.max(...times), first: Math.min(...times), amp };
}
// Follows connect() to see whether an oscillator reaches the destination, and through which gain nodes
function route(osc, dest) {
  const chain = [];
  let n = osc;
  while (n && n.out && n.out.length) { n = n.out[0]; chain.push(n); }
  return { reaches: chain[chain.length - 1] === dest, chain };
}
const startsOf = (ac) => ac.oscs.map((o) => o.startAt);
const tap = async (h) => { h.doc.fire('pointerdown'); h.clock.t += 1; await tick(); };

let finished = false;
setTimeout(() => { console.error('harness timed out'); process.exit(1); }, 30000).unref();
process.on('exit', () => { if (!finished) { console.error('harness ended before every scenario ran'); process.exitCode = 1; } });
let failed = 0;
let passed = 0;
async function scenario(name, fn) {
  try { await fn(); passed += 1; console.log('OK: ' + name); }
  catch (e) { failed += 1; console.error('FAIL: ' + name + '\n  ' + (e && e.stack || e)); }
}

(async () => {
  await scenario('silent by default: zorp_sound off (even with the sound switch on) plays no cue and creates no context', async () => {
    for (const sound of [false, true]) {
      const h = load({ sound });
      await tap(h);
      ['jump', 'land', 'tada'].forEach((c) => assert.strictEqual(h.pb.zorp(c), false, c));
      await tick();
      assert.strictEqual(h.pb.zorp('nonsense'), false);
      assert.strictEqual(h.pb.zorp('constructor'), false, 'cue names are own properties only');
      h.made.forEach((ac) => assert.strictEqual(ac.oscs.length, 0, 'no oscillator'));
      if (!sound) assert.strictEqual(h.made.length, 0, 'sound off and Zorp off: no listener, no context, ever');
    }
    const h = load({ zorp: 'off' });
    assert.strictEqual(h.pb.cuesActive(), false);
    assert.strictEqual(h.pb.blips([200, 600], 'hello'), false, 'blips need chatter or force');
    const c = load({ zorp: 'chatter' });
    assert.strictEqual(c.pb.zorp('jump'), false, 'chatter is not celebrations');
  });

  await scenario('no context created on load (celebrations, sound switch on): only a tap creates it', async () => {
    const h = load({ zorp: 'celebrations', sound: true });
    await tick();
    assert.strictEqual(h.made.length, 0, 'nothing on load');
    assert.ok((h.doc.listeners.pointerdown || []).length && (h.doc.listeners.keydown || []).length, 'capture listeners for tap and key');
    (h.doc.listeners.pointerdown).forEach((l) => assert.ok(l.opts && l.opts.capture && l.opts.passive, 'capture and passive'));
    await tap(h);
    assert.strictEqual(h.made.length, 1, 'created by the first tap, as the answer tones always did');
    const z = load({ zorp: 'celebrations' });
    await tick();
    assert.strictEqual(z.made.length, 0);
  });

  await scenario('no cue without a gesture in the last 5 s', async () => {
    const h = load({ zorp: 'celebrations' });
    assert.strictEqual(h.pb.zorp('tada'), false, 'page load: no tap yet');
    await tap(h);
    h.clock.t += 4000;
    assert.strictEqual(h.pb.zorp('tada'), true, '4 s after the tap');
    await tick();
    const k = load({ zorp: 'celebrations' });
    k.doc.fire('keydown');
    k.clock.t += 5000;
    assert.strictEqual(k.pb.zorp('tada'), true, 'a key press counts, and 5 s is inside the window');
    const old = load({ zorp: 'celebrations' });
    await tap(old);
    old.clock.t += 5001;
    assert.strictEqual(old.pb.zorp('tada'), false, '5.001 s after the tap');
    old.doc.fire('pointerdown');
    assert.strictEqual(old.pb.zorp('tada'), true, 'a new tap re-opens it');
  });

  await scenario('none in quiz mode', async () => {
    const h = load({ zorp: 'celebrations', quiz: true });
    await tap(h);
    assert.strictEqual(h.pb.zorp('tada'), false);
    assert.strictEqual(h.pb.zorp('tada', { force: true }), false, 'force never overrides the quiz rule');
    assert.strictEqual(h.pb.cuesActive(), false);
    await tick();
    h.made.forEach((ac) => assert.strictEqual(ac.oscs.length, 0));
  });

  await scenario('hidden tab silent, and a tab hidden mid-cue is cut', async () => {
    const h = load({ zorp: 'celebrations', hidden: true });
    await tap(h);
    assert.strictEqual(h.pb.zorp('tada'), false);
    assert.strictEqual(h.pb.zorp('tada', { force: true }), false);
    const v = load({ zorp: 'celebrations' });
    await tap(v);
    assert.strictEqual(v.pb.zorp('jump'), true);
    await tick();
    const bus = v.made[0].oscs[0].out[0].out[0];
    assert.strictEqual(bus.dead, false);
    v.doc.hidden = true;
    v.doc.fire('visibilitychange');
    assert.strictEqual(bus.dead, true, 'the cue bus is disconnected when the tab hides');
  });

  await scenario('400 ms arbiter: no cue within 400 ms of another sound; a land follows its own jump', async () => {
    const h = load({ zorp: 'celebrations', sound: true });
    await tap(h);
    h.pb.correct();
    h.clock.t += 399;
    assert.strictEqual(h.pb.zorp('jump'), false, '399 ms after the answer tone');
    h.clock.t += 2;
    assert.strictEqual(h.pb.zorp('jump'), true, '401 ms after it');
    h.clock.t += 280;
    assert.strictEqual(h.pb.zorp('land'), true, 'land 280 ms after its jump is the same sequence');
    h.clock.t += 100;
    h.pb.soft();
    h.clock.t += 100;
    assert.strictEqual(h.pb.zorp('tada', { force: true }), false, 'an answer tone 100 ms ago blocks even a forced cue');
    // a jump that was blocked never lets its land through
    const b = load({ zorp: 'celebrations', sound: true });
    await tap(b);
    b.pb.correct();
    b.clock.t += 100;
    assert.strictEqual(b.pb.zorp('jump'), false);
    b.clock.t += 500;
    assert.strictEqual(b.pb.zorp('land'), false, 'no lone land');
    // a land after something else played in between is not a follow
    const c = load({ zorp: 'celebrations', sound: true });
    await tap(c);
    assert.strictEqual(c.pb.zorp('jump'), true);
    c.clock.t += 100;
    c.pb.soft();
    c.clock.t += 100;
    assert.strictEqual(c.pb.zorp('land'), false);
  });

  await scenario('one cue sequence per 7 s', async () => {
    const h = load({ zorp: 'celebrations' });
    await tap(h);
    assert.strictEqual(h.pb.zorp('jump'), true);
    h.clock.t += 280;
    assert.strictEqual(h.pb.zorp('land'), true);
    h.doc.fire('pointerdown');
    h.clock.t += 6000;
    h.doc.fire('pointerdown');
    assert.strictEqual(h.pb.zorp('tada'), false, '6.3 s after the jump');
    h.clock.t += 719;
    h.doc.fire('pointerdown');
    assert.strictEqual(h.pb.zorp('tada'), false, '6,999 ms after the start of the sequence');
    h.clock.t += 1;
    h.doc.fire('pointerdown');
    assert.strictEqual(h.pb.zorp('tada'), true, 'the window is 7,000 ms from the start of the sequence');
    h.clock.t += 7000;
    h.doc.fire('pointerdown');
    assert.strictEqual(h.pb.zorp('jump'), true);
    await tick();
    const f = load({ zorp: 'celebrations' });
    await tap(f);
    assert.strictEqual(f.pb.zorp('jump'), true);
    f.clock.t += 1000;
    assert.strictEqual(f.pb.zorp('tada', { force: true }), true, 'force skips the 7 s limit (and only that and the setting)');
  });

  await scenario('cue gain at most 0.07 and below soft; every cue is an enveloped oscillator on one shared bus', async () => {
    for (const cue of Object.keys(TABLE)) {
      const h = load({ zorp: 'celebrations' });
      await tap(h);
      assert.strictEqual(h.pb.zorp(cue, { force: true }), true, cue);
      await tick();
      const ac = h.made[0];
      assert.ok(ac.oscs.length >= 1, cue + ' has oscillators');
      const buses = new Set();
      ac.oscs.forEach((osc) => {
        const env = envelope(osc);
        assert.ok(env.peak <= 0.07, cue + ' peak ' + env.peak);
        assert.ok(env.peak < SOFT, cue + ' is below soft (0.08)');
        assert.ok(env.peak <= TABLE[cue].peak + 1e-9, cue + ' within the table gain');
        assert.ok(['sine', 'triangle'].indexOf(osc.type) !== -1, 'sine or triangle');
        const r = route(osc, ac.destination);
        assert.ok(r.reaches && r.chain.length === 3, 'osc -> own gain -> bus -> destination');
        buses.add(r.chain[1]);
      });
      assert.strictEqual(buses.size, 1, cue + ' shares one bus so stopAll can cut it');
      assert.ok(!ac.oscs.some((o) => o.out[0] === ac.destination), 'nothing bypasses the bus');
      // the bus itself is a plain unity node: no gain automation that could raise a cue
      const bus = [...buses][0];
      assert.strictEqual(bus.gain.events.length, 0, 'the bus adds no gain');
    }
  });

  await scenario('durations within the table (envelope end and oscillator stop)', async () => {
    for (const cue of Object.keys(TABLE)) {
      const h = load({ zorp: 'celebrations' });
      await tap(h);
      h.pb.zorp(cue, { force: true });
      await tick();
      const ac = h.made[0];
      let end = 0;
      ac.oscs.forEach((osc) => {
        const env = envelope(osc);
        const startAt = osc.startAt - 10;
        assert.ok(startAt >= -1e-9, 'scheduled from now');
        end = Math.max(end, (env.last - 10) * 1000);
        assert.ok((osc.stopAt - env.last) * 1000 <= 20, 'stops within 20 ms of the envelope end');
        assert.ok(Math.abs(env.first - osc.startAt) < 1e-9, 'envelope starts with the oscillator');
      });
      assert.ok(end <= TABLE[cue].ms + 1e-6, cue + ' ends at ' + end + ' ms, table ' + TABLE[cue].ms);
      assert.ok(end >= TABLE[cue].ms - 1, cue + ' fills its table length (' + end + ')');
    }
    // the table's pitches
    const j = load({ zorp: 'celebrations' });
    await tap(j);
    j.pb.zorp('jump');
    await tick();
    const jo = j.made[0].oscs[0];
    assert.strictEqual(jo.type, 'sine');
    assert.deepStrictEqual(jo.frequency.events.map((e) => Math.round(e[1])), [330, 660]);
    const l = load({ zorp: 'celebrations' });
    await tap(l);
    l.pb.zorp('land', { force: true });
    await tick();
    assert.strictEqual(l.made[0].oscs[0].type, 'triangle');
    assert.deepStrictEqual(l.made[0].oscs[0].frequency.events.map((e) => Math.round(e[1])), [180, 120]);
    const t = load({ zorp: 'celebrations' });
    await tap(t);
    t.pb.zorp('tada');
    await tick();
    const to = t.made[0].oscs;
    assert.deepStrictEqual(to.map((o) => Math.round(o.frequency.events[0][1])), [523, 659, 784]);
    assert.deepStrictEqual(to.map((o) => Math.round((o.startAt - 10) * 1000)), [0, 70, 140], 'three notes 70 ms apart');
  });

  await scenario('blip gain at most 0.035; every second frame, 6 a second and 12 a line at most, 520 to 680 Hz', async () => {
    const times = [];
    for (let i = 0; i < 40; i += 1) times.push(120 + i * 135);
    const words = [120, 400, 700, 1000];
    const run = async (text, force) => {
      const h = load({ zorp: 'celebrations' });
      await tap(h);
      assert.strictEqual(h.pb.blips(times, text, { force: true, words }), true);
      await tick();
      return h.made[0].oscs;
    };
    const oscs = await run('Hi, I am Zorp and I love a good problem');
    assert.ok(oscs.length > 0 && oscs.length <= 12, 'at most 12 blips a line: ' + oscs.length);
    oscs.forEach((o) => {
      const env = envelope(o);
      assert.ok(env.peak <= 0.035, 'blip peak ' + env.peak);
      assert.ok((env.last - env.first) * 1000 <= 35 + 1e-6, 'a blip lasts at most 35 ms');
      const f = o.frequency.events[0][1];
      assert.ok(f >= 520 && f <= 680 * 1.15 + 1e-6, 'pitch ' + f);
    });
    const at = oscs.map((o) => (o.startAt - 10) * 1000);
    for (let i = 1; i < at.length; i += 1) assert.ok(at[i] - at[i - 1] >= 1000 / 6 - 1e-6, 'at most 6 a second');
    assert.ok(at.length * 2 <= times.length + 1, 'every second open frame at most');
    const q = await run('Fancy another go?');
    const statement = await run('Fancy another go.');
    assert.ok(Math.abs(q[q.length - 1].frequency.events[0][1] - statement[statement.length - 1].frequency.events[0][1] * 1.15) < 0.01, 'a question ends 15 percent higher');
    // no blips unless chatter or forced, and never hidden or without a tap
    const n = load({ zorp: 'celebrations' });
    await tap(n);
    assert.strictEqual(n.pb.blips(times, 'hi'), false, 'celebrations is not chatter');
    const c = load({ zorp: 'chatter' });
    c.pb.arm();
    await tap(c);
    assert.strictEqual(c.pb.blips(times, 'hi'), true, 'chatter would allow them (never offered, rejected by the settings validator)');
    const g = load({ zorp: 'off' });
    assert.strictEqual(g.pb.blips(times, 'hi', { force: true }), false, 'forced, but no tap yet');
    const e = load({ zorp: 'off', quiz: true });
    await tap(e);
    assert.strictEqual(e.pb.blips(times, 'hi', { force: true }), false);
  });

  await scenario('stopAll cuts the bus and the next cue builds a new one', async () => {
    const h = load({ zorp: 'celebrations' });
    await tap(h);
    h.pb.zorp('tada');
    await tick();
    const bus = h.made[0].oscs[0].out[0].out[0];
    h.pb.stopAll();
    assert.strictEqual(bus.dead, true);
    h.pb.stopAll();
    h.clock.t += 8000;
    h.doc.fire('pointerdown');
    h.pb.zorp('jump');
    await tick();
    const fresh = h.made[0].oscs[3].out[0].out[0];
    assert.notStrictEqual(fresh, bus);
    assert.strictEqual(fresh.dead, false);
  });

  await scenario('stopAll ramps the bus to zero over about 30 ms, then disconnects', async () => {
    const h = load({ zorp: 'celebrations', defer: true });
    await tap(h);
    h.pb.zorp('tada');
    await tick();
    const bus = h.made[0].oscs[0].out[0].out[0];
    h.pb.stopAll();
    assert.strictEqual(bus.dead, false, 'not cut yet: the ramp runs first');
    const lin = bus.gain.events.filter((e) => e[0] === 'lin');
    assert.strictEqual(lin.length, 1);
    assert.strictEqual(lin[0][1], 0);
    assert.ok(Math.abs(lin[0][2] - 10 - 0.03) < 1e-9, 'ramp ends 30 ms after now');
    const t = h.timers.find((x) => x.ms >= 30 && x.ms <= 60);
    assert.ok(t, 'a disconnect timer of 30 to 60 ms');
    h.flush();
    assert.strictEqual(bus.dead, true);
  });

  await scenario('styleguide arm(): taps are recorded without either setting, and force plays a cue', async () => {
    const h = load({ zorp: 'off' });
    assert.strictEqual(h.doc.listeners.pointerdown, undefined, 'no listener by default');
    h.pb.arm();
    h.pb.arm();
    assert.strictEqual(h.doc.listeners.pointerdown.length, 1, 'bound once');
    assert.strictEqual(h.pb.zorp('jump', { force: true }), false, 'no tap yet');
    await tap(h);
    assert.strictEqual(h.pb.zorp('jump', { force: true }), true);
    h.clock.t += 280;
    assert.strictEqual(h.pb.zorp('land', { force: true }), true);
    await tick();
    assert.strictEqual(h.made[0].oscs.length, 2);
    const n = load({ zorp: 'off' });
    n.pb.arm();
    await tap(n);
    assert.strictEqual(n.pb.zorp('jump'), false, 'without force the setting still rules');
  });

  await scenario('no AudioContext: every entry point is a safe no-op', async () => {
    const h = load({ zorp: 'celebrations', sound: true, audio: false });
    await tap(h);
    assert.strictEqual(h.pb.zorp('tada'), false);
    assert.strictEqual(h.pb.blips([100, 400], 'hi', { force: true }), false);
    h.pb.correct();
    h.pb.stopAll();
    await tick();
  });

  await scenario('confetti silent when cues are active (one sound per moment), loud otherwise', async () => {
    const run = async (o) => {
      const h = load(o);
      vm.runInContext(CELEBRATE_SRC, h.sb);
      let n = 0;
      h.sb.pbSound.celebrate = () => { n += 1; };
      h.sb.pbCelebrate.confetti();
      return { n, active: h.pb.cuesActive() };
    };
    let r = await run({ zorp: 'celebrations', sound: true, zorpRuntime: { level: 'full' } });
    assert.deepStrictEqual(r, { n: 1, active: true }, 'cues active but none started (no tap): the arpeggio plays after the defer');
    r = await run({ zorp: 'off', sound: true, zorpRuntime: { level: 'full' } });
    assert.deepStrictEqual(r, { n: 1, active: false }, 'Zorp off: the arpeggio as today');
    r = await run({ zorp: 'celebrations', sound: true, zorpRuntime: { level: 'reduced' } });
    assert.strictEqual(r.active, false, 'reduced motion: no cues, so no replacement');
    r = await run({ zorp: 'celebrations', sound: true, zorpRuntime: { level: 'off' } });
    assert.strictEqual(r.active, false);
    r = await run({ zorp: 'celebrations', sound: true, quiz: true, zorpRuntime: { level: 'full' } });
    assert.deepStrictEqual(r, { n: 1, active: false }, 'quiz runner: cues are off, so the arpeggio stays');
    r = await run({ zorp: 'celebrations', sound: true });
    assert.deepStrictEqual(r, { n: 1, active: false }, 'no motion runtime: the arpeggio stays');
    r = await run({ zorp: 'celebrations', sound: true, zorpRuntime: { level: 'full', poses: false } });
    assert.deepStrictEqual(r, { n: 1, active: false }, 'no beat engine (zorp-poses.js missing): no cues would ever schedule');
    // an explicit silent request still wins, and the answer tones are never replaced
    const h = load({ zorp: 'celebrations', sound: true, zorpRuntime: { level: 'full' } });
    vm.runInContext(CELEBRATE_SRC, h.sb);
    let n = 0;
    h.sb.pbSound.celebrate = () => { n += 1; };
    h.sb.pbSound.correct = () => { n += 10; };
    h.sb.pbSound.ding = () => { n += 100; };
    h.sb.pbSound.soft = () => { n += 1000; };
    h.sb.pbCelebrate.correct(null);
    h.sb.pbCelebrate.wrong(null, null);
    assert.strictEqual(n, 1010, 'correct and soft answer tones still play with cues active; the arpeggio does not');
  });

  await scenario('confetti: a cue that started replaces the arpeggio; a blocked cue leaves it', async () => {
    const go = async (o, cueFirst, before) => {
      const h = load(Object.assign({ zorp: 'celebrations', sound: true, defer: true, zorpRuntime: { level: 'full' } }, o));
      vm.runInContext(CELEBRATE_SRC, h.sb);
      let n = 0;
      h.sb.pbSound.celebrate = () => { n += 1; };
      if (before) before(h);
      await tap(h);
      h.sb.pbCelebrate.confetti();
      assert.strictEqual(n, 0, 'nothing plays before the defer');
      if (cueFirst) { h.clock.t += 100; h.pb.zorp('tada'); await tick(); }
      h.clock.t += 1000;
      h.flush();
      return n;
    };
    assert.strictEqual(await go({}, true), 0, 'cue plays -> arpeggio silent');
    assert.strictEqual(await go({}, false), 1, 'no cue scheduled (no Guide clip) -> arpeggio plays');
    assert.strictEqual(await go({}, true, (h) => { h.pb.zorp('jump', { force: true }); }), 0, 'sanity: an earlier cue inside 1.5 s counts');
    // inside the 7 s window: a first sequence just played, so this moment's cue is refused and the arpeggio plays
    const h = load({ zorp: 'celebrations', sound: true, defer: true, zorpRuntime: { level: 'full' } });
    vm.runInContext(CELEBRATE_SRC, h.sb);
    let n = 0;
    h.sb.pbSound.celebrate = () => { n += 1; };
    await tap(h);
    assert.strictEqual(h.pb.zorp('tada'), true);
    h.clock.t += 3000;
    h.sb.pbCelebrate.confetti();
    h.clock.t += 100;
    assert.strictEqual(h.pb.zorp('tada'), false, 'the 7 s window refuses it');
    h.clock.t += 1000;
    h.flush();
    assert.strictEqual(n, 1, 'cue blocked inside the 7 s window -> arpeggio plays');
    // a stale tap (older than 5 s) blocks the cue too
    const s2 = load({ zorp: 'celebrations', sound: true, defer: true, zorpRuntime: { level: 'full' } });
    vm.runInContext(CELEBRATE_SRC, s2.sb);
    let m = 0;
    s2.sb.pbSound.celebrate = () => { m += 1; };
    await tap(s2);
    s2.clock.t += 6000;
    s2.sb.pbCelebrate.confetti();
    assert.strictEqual(s2.pb.zorp('tada'), false);
    s2.flush();
    assert.strictEqual(m, 1, 'cue blocked by a stale tap -> arpeggio plays');
  });

  await scenario('the confetti arpeggio is the moment\'s sound: a Zorp cue within 7 s is blocked, a later one is not', async () => {
    const h = load({ zorp: 'celebrations', sound: true, zorpRuntime: { level: 'full' } });
    await tap(h);
    h.pb.celebrate();                      // streak:100 style reward: the arpeggio at +1 s
    await tick();
    h.clock.t += 1000;
    assert.strictEqual(h.pb.zorp('jump'), false, 'jump inside 7 s of the arpeggio is refused');
    assert.strictEqual(h.pb.zorp('tada'), false, 'so is tada');
    h.clock.t += 5500;                     // 6.5 s after the arpeggio, tap still inside its 5 s window? re-tap
    h.doc.fire('pointerdown');
    assert.strictEqual(h.pb.zorp('tada'), false, 'still inside 7 s');
    h.clock.t += 600;
    assert.strictEqual(h.pb.zorp('tada'), true, 'after 7 s the cue plays again');
    // sound switch off: no arpeggio plays, so nothing is marked
    const q = load({ zorp: 'celebrations', zorpRuntime: { level: 'full' } });
    await tap(q);
    q.pb.celebrate();
    q.clock.t += 1000;
    assert.strictEqual(q.pb.zorp('tada'), true, 'a silent arpeggio does not block the cue');
    // badge reward: tada only, no arpeggio (cues active); lesson_complete: jump then its land
    const b = load({ zorp: 'celebrations', sound: true, defer: true, zorpRuntime: { level: 'full' } });
    vm.runInContext(CELEBRATE_SRC, b.sb);
    let n = 0;
    b.sb.pbSound.celebrate = () => { n += 1; };
    await tap(b);
    assert.strictEqual(b.pb.zorp('tada'), true);
    b.sb.pbCelebrate.confetti();
    b.clock.t += 1000;
    b.flush();
    assert.strictEqual(n, 0, 'badge reward: the cue carries it, no arpeggio');
    const l = load({ zorp: 'celebrations', sound: true, zorpRuntime: { level: 'full' } });
    await tap(l);
    assert.strictEqual(l.pb.zorp('jump'), true);
    l.clock.t += 620;
    assert.strictEqual(l.pb.zorp('land'), true, 'lesson_complete: the land still follows its jump');
    assert.strictEqual(l.pb.cued(2000), true);
  });

  await scenario('unlock also listens for pointerup and touchend (iPad/WebKit gesture), all capture and passive', async () => {
    const h = load({ zorp: 'celebrations', sound: true });
    ['pointerdown', 'pointerup', 'touchend', 'keydown'].forEach((type) => {
      assert.ok((h.doc.listeners[type] || []).length === 1, type + ' bound once');
      h.doc.listeners[type].forEach((l) => assert.ok(l.opts && l.opts.capture && l.opts.passive, type + ' capture and passive'));
    });
    for (const type of ['pointerup', 'touchend']) {
      const k = load({ zorp: 'celebrations', zorpRuntime: { level: 'full' } });
      assert.strictEqual(k.pb.zorp('tada'), false, 'no gesture yet');
      k.doc.fire(type);
      await tick();
      assert.strictEqual(k.made.length, 1, type + ' creates and resumes the context');
      assert.strictEqual(k.made[0].state, 'running', type + ' resumed the context');
      k.clock.t += 4000;
      assert.strictEqual(k.pb.zorp('tada'), true, type + ' counts as the gesture timestamp');
    }
  });

  finished = true;
  console.log(passed + ' of ' + (passed + failed) + ' scenarios passed');
  if (failed) process.exit(1);
})();
