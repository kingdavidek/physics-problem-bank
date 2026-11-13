'use strict';
/* Celebration sounds (docs/CELEBRATION_SOUNDS_PLAN.md): behavioural harness for static/js/sound-library.js and pbSound.play in
   static/js/sound.js, run by test_celebration_sounds_smoke.py. A fake AudioContext records every oscillator, noise source, filter and
   gain automation; Date.now() is a virtual clock. No browser, no audio.
   Usage: node celebration_sound_harness.js <sound.js> <sound-library.js> */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const [, , soundPath, libPath] = process.argv;
if (!soundPath || !libPath) {
  console.error('usage: node celebration_sound_harness.js <sound.js> <sound-library.js>');
  process.exit(2);
}
const SOUND_SRC = fs.readFileSync(soundPath, 'utf8');
const LIB_SRC = fs.readFileSync(libPath, 'utf8');
const tick = async () => { for (let i = 0; i < 8; i += 1) await new Promise((r) => setImmediate(r)); };
const NAMES = ['whoosh', 'stamp-bronze', 'stamp-silver', 'stamp-gold', 'stamp-violet', 'sparkle', 'confetti', 'gem', 'level', 'book',
  'sprout', 'fire', 'week', 'story', 'pop'];
const PEAK = 0.08;   // soft, the quietest answer tone: no tone is louder
const LOUD = 0.1;    // the sum of every tone sounding at once stays near that
const NOISE = 0.15;  // a filtered noise burst keeps a small share of its gain; its real loudness is measured (celebration_sound_loudness.py)
const MAX_MS = 1800;

function load(o) {
  o = o || {};
  const clock = { t: 1e6 };
  const made = [];
  const doc = { listeners: {}, hidden: !!o.hidden, scripts: [] };
  const attrs = { 'data-zorp-sound': o.zorp || 'off', 'data-pb-sound-lib': o.lib === false ? null : '/static/js/sound-library.js?v=1' };
  const bodyAttrs = {};
  if (o.quiz) bodyAttrs['data-guide-quiz'] = '1';
  if (o.results) bodyAttrs['data-guide-quiz-results'] = '1';
  doc.documentElement = { getAttribute: (k) => (k in attrs ? attrs[k] : null), setAttribute: (k, v) => { attrs[k] = String(v); } };
  doc.body = { getAttribute: (k) => (k in bodyAttrs ? bodyAttrs[k] : null), setAttribute: (k, v) => { bodyAttrs[k] = String(v); } };
  doc.addEventListener = (type, fn) => { (doc.listeners[type] = doc.listeners[type] || []).push(fn); };
  doc.fire = (type) => (doc.listeners[type] || []).forEach((fn) => fn({ type }));
  doc.createElement = (tag) => ({ tag, set src(v) { this._src = v; }, get src() { return this._src; } });
  // a script loads (or fails) later, as in a browser
  doc.head = { appendChild: (n) => { doc.scripts.push(n); setImmediate(() => { if (o.libLoads !== false) { vm.runInContext(LIB_SRC, ctx); n.onload(); } else n.onerror(); }); } };

  class Param {
    constructor() { this.events = []; this._v = 1; }
    set value(v) { this._v = v; this.events.push(['value', v, 0]); }
    get value() { return this._v; }
    setValueAtTime(v, t) { this.events.push(['set', v, t]); }
    exponentialRampToValueAtTime(v, t) { this.events.push(['ramp', v, t]); }
    linearRampToValueAtTime(v, t) { this.events.push(['lin', v, t]); }
    cancelScheduledValues(t) { this.events.push(['cancel', 0, t]); }
  }
  class Node {
    constructor(kind) { this.kind = kind; this.out = []; }
    connect(n) { this.out.push(n); return n; }
    disconnect() { this.out = []; this.dead = true; }
  }
  class AudioContext {
    constructor() {
      this.state = 'suspended';
      this.currentTime = 10;
      this.sampleRate = 48000;
      this.destination = new Node('destination');
      this.voices = [];
      this.gains = [];
      made.push(this);
    }
    resume() {
      if (o.resume) return o.resume(this);
      this.state = 'running';
      return Promise.resolve();
    }
    createGain() { const g = new Node('gain'); g.gain = new Param(); this.gains.push(g); return g; }
    createOscillator() {
      const n = new Node('osc');
      n.frequency = new Param();
      n.start = (t) => { n.startAt = t; };
      n.stop = (t) => { n.stopAt = t; };
      this.voices.push(n);
      return n;
    }
    createBuffer(ch, len, rate) { return { len, rate, getChannelData: () => new Float32Array(len) }; }
    createBufferSource() {
      const n = new Node('noise');
      n.start = (t) => { n.startAt = t; };
      n.stop = (t) => { n.stopAt = t; };
      this.voices.push(n);
      return n;
    }
    createBiquadFilter() { const f = new Node('filter'); f.frequency = new Param(); f.Q = new Param(); return f; }
  }
  const store = {};
  const sandbox = {
    document: doc, Date: { now: () => clock.t }, Promise, Object, Math, JSON, console, Array, String, Number, Float32Array, parseInt,
    setTimeout: (fn) => { fn(); return 0; }, clearTimeout() {},
    addEventListener: (type, fn) => { (doc.listeners['win:' + type] = doc.listeners['win:' + type] || []).push(fn); },
  };
  if (o.storage !== false) {
    sandbox.sessionStorage = { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); } };
    Object.assign(store, o.store || {});
  }
  sandbox.window = sandbox;
  if (o.audio !== false) sandbox.AudioContext = AudioContext;
  const ctx = vm.createContext(sandbox);
  if (o.preload) vm.runInContext(LIB_SRC, ctx);
  vm.runInContext(SOUND_SRC, ctx);
  return { sb: sandbox, pb: sandbox.pbSound, made, clock, doc, attrs, bodyAttrs, store };
}

// what reached the speakers: voices whose chain ends at the destination through the shared bus
function route(n, dest) {
  const chain = [];
  let x = n;
  while (x && x.out && x.out.length) { x = x.out[0]; chain.push(x); }
  return { reaches: chain[chain.length - 1] === dest, chain };
}
function peakOf(voice) {
  const amp = voice.out[0].kind === 'filter' ? voice.out[0].out[0] : voice.out[0];
  return Math.max(...amp.gain.events.filter((e) => e[0] === 'ramp').map((e) => e[1]));
}
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
  await scenario('the library: the planned names, each one plays; no tone above 0.08, no noise above 0.15, no moment above 0.1, none longer than 1.8 s', async () => {
    const h = load({ preload: true });
    const lib = h.sb.pbSoundLib;
    assert.deepStrictEqual([...lib.names].sort(), [...NAMES].sort());
    for (const name of NAMES) {
      const m = lib.meta(name);
      assert.ok(m.peak + m.noise > 0 && m.peak <= PEAK && m.noise <= NOISE, `${name} peak ${m.peak} noise ${m.noise}`);
      assert.ok(m.loud <= LOUD, `${name} loud ${m.loud}`);
      assert.ok(m.ms > 0 && m.ms <= MAX_MS, `${name} ${m.ms} ms`);
      const ac = new h.sb.AudioContext();
      const out = ac.createGain();
      out.connect(ac.destination);
      assert.strictEqual(lib.play(name, ac, out, 1, { step: 1 }), true, name);
      assert.ok(ac.voices.length > 0, `${name} made no voice`);
      ac.voices.forEach((v) => {
        assert.ok(route(v, ac.destination).reaches && route(v, ac.destination).chain.includes(out), `${name}: every voice goes through the shared node`);
        assert.ok(peakOf(v) <= (v.kind === 'noise' ? NOISE : PEAK) + 1e-9, `${name} ${v.kind} peak ${peakOf(v)}`);
        assert.ok(v.stopAt > v.startAt && v.stopAt - 10 <= MAX_MS / 1000 + 0.1, `${name} stops`);
      });
    }
    assert.strictEqual(lib.play('nonsense', new h.sb.AudioContext(), {}, 1), false);
    assert.strictEqual(lib.meta('nonsense'), null);
  });

  await scenario('soft plays every voice at 0.6 of its gain; Your week picks one note per card, rising', async () => {
    const h = load({ preload: true });
    const lib = h.sb.pbSoundLib;
    const peaks = (k) => { const ac = new h.sb.AudioContext(); const out = ac.createGain(); lib.play('stamp-gold', ac, out, k); return ac.voices.map(peakOf); };
    const full = peaks(1);
    const soft = peaks(0.6);
    full.forEach((p, i) => assert.ok(Math.abs(soft[i] - p * 0.6) < 1e-9, `voice ${i}: ${soft[i]} vs ${p}`));
    const freq = (step) => { const ac = new h.sb.AudioContext(); lib.play('week', ac, ac.createGain(), 1, { step }); return ac.voices[0].frequency.events[0][1]; };
    assert.ok(freq(0) < freq(1) && freq(1) < freq(2), 'C5, E5, G5');
    assert.strictEqual(freq(9), freq(2), 'a step past the end is the top note');
  });

  await scenario('off by setting: no sound and no context; on with a tap: plays through the bus, once the library loads', async () => {
    const off = load({ zorp: 'off' });
    await tap(off);
    assert.strictEqual(off.pb.play('gem'), false);
    await tick();
    assert.strictEqual(off.made.length, 0);
    assert.strictEqual(off.doc.scripts.length, 0, 'the library is not even loaded');
    off.pb.prepare();
    assert.strictEqual(off.doc.scripts.length, 0, 'prepare loads nothing while the setting is off');
    const on = load({ zorp: 'celebrations' });
    on.pb.prepare();
    assert.strictEqual(on.doc.scripts.length, 1, 'prepare loads the library');
    assert.strictEqual(on.doc.scripts[0].src, '/static/js/sound-library.js?v=1', 'from html[data-pb-sound-lib]');
    await tap(on);
    assert.strictEqual(on.pb.play('gem'), true);
    await tick();
    assert.strictEqual(on.doc.scripts.length, 1, 'loaded once');
    const ac = on.made[0];
    assert.ok(ac && ac.voices.length >= 4, 'the gem run');
    const bus = ac.voices[0].out[0].out[0];
    ac.voices.forEach((v) => assert.ok(route(v, ac.destination).chain.includes(bus), 'one shared bus'));
  });

  await scenario('the gates: a tap in the last 5 s, a visible page, never a question page (a results page may sound)', async () => {
    const h = load({ zorp: 'celebrations' });
    assert.strictEqual(h.pb.play('pop'), false, 'no tap yet');
    await tap(h);
    h.clock.t += 5001;
    assert.strictEqual(h.pb.play('pop'), false, 'the tap is too old');
    const quiz = load({ zorp: 'celebrations', quiz: true });
    await tap(quiz);
    assert.strictEqual(quiz.pb.play('pop'), false, 'a question page');
    const results = load({ zorp: 'celebrations', quiz: true, results: true });
    await tap(results);
    assert.strictEqual(results.pb.play('pop'), true, 'the results page');
    const hidden = load({ zorp: 'celebrations', hidden: true });
    await tap(hidden);
    assert.strictEqual(hidden.pb.play('pop'), false, 'a hidden tab');
    const none = load({ zorp: 'celebrations', audio: false });
    await tap(none);
    assert.strictEqual(none.pb.play('pop'), false, 'no WebAudio: a safe no-op');
  });

  await scenario('400 ms between sounds unless chained (a later layer of the same moment); a scene sound holds Zorp cues for 7 s', async () => {
    const h = load({ zorp: 'celebrations' });
    await tap(h);
    assert.strictEqual(h.pb.play('whoosh'), true);
    h.clock.t += 100;
    assert.strictEqual(h.pb.play('pop'), false, 'within 400 ms');
    assert.strictEqual(h.pb.play('stamp-gold', { chain: true }), true, 'a chained layer');
    h.clock.t += 2000;
    assert.strictEqual(h.pb.zorp('jump'), false, 'Zorp waits while a scene sounds (7 s rule)');
    h.clock.t += 5000;
    await tap(h);
    assert.strictEqual(h.pb.zorp('jump'), true, 'and cues again after');
  });

  await scenario('force (the gallery) skips the setting, the tap and the gap, never a hidden tab', async () => {
    const h = load({ zorp: 'off' });
    assert.strictEqual(h.pb.play('gem', { force: true }), true);
    assert.strictEqual(h.pb.play('gem', { force: true }), true, 'no gap');
    await tick();
    assert.ok(h.made[0].voices.length >= 8);
    const hidden = load({ zorp: 'off', hidden: true });
    assert.strictEqual(hidden.pb.play('gem', { force: true }), false);
  });

  await scenario('stopAll cuts the celebration bus; the next sound builds a new one', async () => {
    const h = load({ zorp: 'celebrations' });
    await tap(h);
    h.pb.play('level');
    await tick();
    const ac = h.made[0];
    const bus = ac.voices[0].out[0].out[0];
    h.pb.stopAll();
    assert.ok(bus.gain.events.some((e) => e[0] === 'lin' && e[1] === 0), 'ramped to zero');
    assert.ok(bus.dead, 'then disconnected');
    h.clock.t += 500;
    await tap(h);
    h.pb.play('pop');
    await tick();
    const bus2 = ac.voices[ac.voices.length - 1].out[0].out[0];
    assert.ok(bus2 !== bus && !bus2.dead);
  });

  await scenario('a tap on the page before (a quiz submit) counts here for its 5 s; an older one does not; pagehide carries it on', async () => {
    const h = load({ zorp: 'celebrations', store: { 'pb-tap': String(1e6 - 2000) } });
    assert.strictEqual(h.pb.play('gem'), true, 'the submit tap 2 s ago');
    const old = load({ zorp: 'celebrations', store: { 'pb-tap': String(1e6 - 6000) } });
    assert.strictEqual(old.pb.play('gem'), false, '6 s ago is too old');
    const junk = load({ zorp: 'celebrations', store: { 'pb-tap': 'x' } });
    assert.strictEqual(junk.pb.play('gem'), false);
    const no = load({ zorp: 'celebrations', storage: false });
    assert.strictEqual(no.pb.play('gem'), false, 'no storage: only a tap here');
    const p = load({ zorp: 'celebrations' });
    await tap(p);
    (p.doc.listeners['win:pagehide'] || []).forEach((fn) => fn());
    assert.strictEqual(p.store['pb-tap'], String(p.clock.t - 1), 'the last tap is saved as the page goes');
    const off = load({ zorp: 'off', store: { 'pb-tap': String(1e6 - 1000) } });
    assert.strictEqual(off.pb.play('gem'), false, 'the setting still decides');
  });

  await scenario('a sound whose audio is not ready within 1 s is dropped, never played late (the browser kept audio off)', async () => {
    let release = null;
    const h = load({ zorp: 'celebrations', resume: (ac) => new Promise((ok) => { release = () => { ac.state = 'running'; ok(); }; }) });
    await tap(h);
    assert.strictEqual(h.pb.play('gem'), true);
    await tick();
    h.clock.t += 1500;
    release();
    await tick();
    assert.strictEqual(h.made[0].voices.length, 0, 'nothing played 1.5 s late');
  });

  await scenario('a library that fails to load is a silent no-op, and the next sound tries again', async () => {
    const h = load({ zorp: 'celebrations', libLoads: false });
    await tap(h);
    assert.strictEqual(h.pb.play('gem'), true);
    await tick();
    assert.strictEqual(h.made[0].voices.length, 0);
    h.clock.t += 500;
    await tap(h);
    h.pb.play('pop');
    await tick();
    assert.strictEqual(h.doc.scripts.length, 2, 'tried again');
    const nolib = load({ zorp: 'celebrations', lib: false });
    await tap(nolib);
    nolib.pb.play('gem');
    await tick();
    assert.strictEqual(nolib.doc.scripts.length, 0, 'no library URL: nothing loads');
  });

  finished = true;
  console.log(`\n${passed} passed, ${failed} failed`);
  if (failed) process.exitCode = 1;
})();
