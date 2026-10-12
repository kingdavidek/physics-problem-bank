'use strict';
/* E9 Phase 1: behavioural harness for static/js/zorp-talk.js (run by test_zorp_talk_smoke.py).
   Hand-rolled fake DOM and a fake clock (no jsdom offline). Usage: node zorp_talk_harness.js <zorp-motion.js> <zorp-talk.js> <rig.json> */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const [, , motionPath, talkPath, rigPath] = process.argv;
if (!motionPath || !talkPath || !rigPath) {
  console.error('usage: node zorp_talk_harness.js <zorp-motion.js> <zorp-talk.js> <rig.json>');
  process.exit(2);
}
const rig = JSON.parse(fs.readFileSync(rigPath, 'utf8'));
const log = [];                 // every animate() call, in order: { el, frames, opts, cancelled }
const hold = { on: false };       // see El.animate
const events = [];              // ordered 'text:' / 'animate' markers for the text-first check

class El {
  constructor(tag, cls) {
    this.tagName = tag;
    this.attrs = {};
    this.childNodes = [];
    this.parentNode = null;
    this.style = {};
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
  get nextSibling() {
    if (!this.parentNode) return null;
    const kids = this.parentNode.childNodes;
    return kids[kids.indexOf(this) + 1] || null;
  }
  setAttribute(k, v) { this.attrs[k] = String(v); if (k === 'class') this._cls = String(v).split(' '); }
  getAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null; }
  removeAttribute(k) { delete this.attrs[k]; }
  hasAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); }
  appendChild(c) { if (c.parentNode) c.parentNode.removeChild(c); c.parentNode = this; this.childNodes.push(c); return c; }
  insertBefore(c, ref) {
    if (c.parentNode) c.parentNode.removeChild(c);
    const i = this.childNodes.indexOf(ref);
    c.parentNode = this;
    if (i === -1) this.childNodes.push(c); else this.childNodes.splice(i, 0, c);
    return c;
  }
  removeChild(c) { this.childNodes = this.childNodes.filter((x) => x !== c); c.parentNode = null; return c; }
  cloneNode(deep) {
    const n = new El(this.tagName, this._cls.join(' '));
    Object.assign(n.attrs, this.attrs);
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
      if (!am) return false;
      return am[2] === undefined ? this.hasAttribute(am[1]) : this.getAttribute(am[1]) === am[2];
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
  getClientRects() { return this._hidden ? [] : [1]; }
  getBoundingClientRect() { return { width: 1, height: 1 }; }
  set textContent(v) { this._text = String(v); events.push('text:' + this._text); }
  get textContent() { return this._text === undefined ? '' : this._text; }
  animate(frames, opts) {
    events.push('animate');
    // hold.on: only the turn's 50 percent clock (two opacity-1 frames) finishes, so a view excursion stays in flight
    const isClock = frames.length === 2 && frames[0].opacity === 1 && frames[1].opacity === 1;
    const finished = hold.on && !isClock ? new Promise(() => {}) : Promise.resolve();
    const a = { el: this, frames, opts, cancelled: false, finished, cancel() { a.cancelled = true; } };
    log.push(a);
    return a;
  }
}

// fake clock
let now = 0;
let timers = [];
let nextId = 1;
const fakeSetTimeout = (fn, ms) => { const id = nextId++; timers.push({ id, at: now + (ms || 0), fn }); return id; };
const fakeClearTimeout = (id) => { timers = timers.filter((t) => t.id !== id); };
function advance(ms) {
  const to = now + ms;
  for (;;) {
    const due = timers.filter((t) => t.at <= to).sort((a, b) => a.at - b.at)[0];
    if (!due) break;
    timers = timers.filter((t) => t !== due);
    now = due.at;
    due.fn();
  }
  now = to;
}

function mk(tag, cls, kids) { const e = new El(tag, cls); (kids || []).forEach((k) => e.appendChild(k)); return e; }

function buildTemplate() {
  const root = mk('svg');
  Object.keys(rig.channels).forEach((channel) => {
    rig.channels[channel].forEach((id) => {
      const g = mk('g');
      g.setAttribute('data-part', channel + ':' + id);
      const p = mk('path');
      p.setAttribute('data-id', channel + ':' + id);
      g.appendChild(p);
      root.appendChild(g);
    });
  });
  return root;
}

function buildMascot(expr, view) {
  const slots = ['cheeks', 'eyeL', 'eyeR', 'brows', 'mouth', 'fx-face'].map((k) => {
    const cls = k === 'eyeL' ? 'buddy-eye buddy-eye--l zorp-slot--eyeL' : k === 'eyeR' ? 'buddy-eye buddy-eye--r zorp-slot--eyeR' : 'zorp-slot--' + k;
    return mk('g', cls);
  });
  const face = mk('g', 'zorp-face', slots);
  const head = mk('g', 'buddy-head', [mk('g', 'buddy-antenna--l'), mk('g', 'buddy-antenna--r'), mk('g', 'buddy-body'), face]);
  const rootG = mk('g', 'buddy-root', [mk('g', 'buddy-shadow'), mk('g', 'buddy-arm--l'), mk('g', 'buddy-arm--r'), head, mk('g', 'zorp-slot--fx')]);
  const svg = mk('svg', 'buddy-mascot', [mk('g', 'zorp-flip'), rootG]);
  if (expr) svg.setAttribute('data-expr', expr);
  if (view) svg.setAttribute('data-view', view);
  const host = mk('span', 'study-buddy-face', [svg]);
  host.setAttribute('data-buddy-face', '');
  host.setAttribute('data-face', expr || 'nudge');
  return { host, svg, face, slot: (k) => svg.querySelector('.zorp-slot--' + k), talkGroup: () => face.querySelector('.zorp-slot--talk') };
}

function load(motion, opts) {
  opts = opts || {};
  log.length = 0;
  events.length = 0;
  now = 0;
  timers = [];
  const island = mk('script');
  island.setAttribute('id', 'pb-zorp-rig');
  island.textContent = rig.island;
  const tpl = mk('template');
  tpl.setAttribute('id', 'pb-zorp-parts');
  tpl.content = buildTemplate();
  const htmlEl = mk('html');
  if (motion !== 'system') htmlEl.setAttribute('data-motion', motion);
  const byId = { 'pb-zorp-rig': island, 'pb-zorp-parts': tpl };
  const listeners = {};
  const doc = {
    readyState: 'complete', hidden: false, body: mk('body'), documentElement: htmlEl, activeElement: null,
    getElementById: (id) => byId[id] || null,
    createElementNS: (ns, tag) => mk(tag),
    addEventListener(type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
  };
  const observers = [];
  class IO {
    constructor(cb) { this.cb = cb; this.targets = []; observers.push(this); }
    observe(t) { this.targets.push(t); }
    unobserve(t) { this.targets = this.targets.filter((x) => x !== t); }
  }
  const sandbox = {
    document: doc,
    Element: El,
    Animation: class { get finished() { return null; } },
    IntersectionObserver: IO,
    CSS: { supports: () => true },
    setTimeout: fakeSetTimeout, clearTimeout: fakeClearTimeout, Promise, Object, Date, Math, JSON, console, Array, String,
  };
  sandbox.window = sandbox;
  const mq = { matches: !!opts.osReduced, handlers: [], addEventListener(t, fn) { this.handlers.push(fn); } };
  const mutators = [];
  sandbox.MutationObserver = class { constructor(cb) { this.cb = cb; mutators.push(cb); } observe() {} };
  sandbox.matchMedia = () => mq;
  vm.runInNewContext(fs.readFileSync(motionPath, 'utf8'), sandbox);
  vm.runInNewContext(fs.readFileSync(talkPath, 'utf8'), sandbox);
  return {
    z: sandbox.pbZorp, doc, observers,
    fire: (type) => (listeners[type] || []).forEach((fn) => fn()),
    mq, mutate: () => mutators.forEach((cb) => cb([])), html: htmlEl,
  };
}

let finished = false;
process.on('exit', () => { if (!finished) { console.error('FAIL: the harness stopped before every scenario finished (an awaited promise never settled)'); process.exitCode = 1; } });
const results = [];
async function scenario(name, fn) {
  try { await fn(); results.push([name, true]); console.log('OK: ' + name); }
  catch (e) { results.push([name, false]); console.error('FAIL: ' + name + '\n  ' + (e && e.stack || e)); }
}
const flush = () => new Promise((r) => setImmediate(r));
const LONG = 'A bit about me: I’m Zorp, from Novara, out past the maths belt. Novara sent helpers to Earth to make maths and physics feel less scary.';

// open-frame spans of a plan: [[start, end, state]]
function spans(plan) {
  const out = [];
  plan.frames.forEach((f, i) => {
    if (f[1] > 0) out.push([f[0], plan.frames[i + 1] ? plan.frames[i + 1][0] : plan.ms, f[1]]);
  });
  return out;
}

(async () => {
  await scenario('plan caps per surface', () => {
    const { z } = load('system');
    [['story and reward', 1600], ['tour and corner bubble', 1200], ['welcome', 1400]].forEach(([, cap]) => {
      const plan = z.talkPlan(LONG, { max: cap });
      assert.ok(plan.ms <= cap, 'ms ' + plan.ms + ' over cap ' + cap);
      assert.ok(plan.ms > cap - 400, 'a long line should use most of its cap, got ' + plan.ms);
    });
    assert.ok(z.talkPlan(LONG, { max: 99999 }).ms <= 2000, 'absolute ceiling 2,000 ms');
    assert.ok(z.talkPlan('Hello', { max: 1200 }).ms < 600, 'a short line is short');
    assert.strictEqual(z.talkPlan('', { max: 1200 }).frames.length, 1);
    assert.strictEqual(z.talkPlan('   ', { max: 1200 }).words.length, 0);
  });

  await scenario('rate at most 9 Hz, no open frame under 60 ms', () => {
    const { z } = load('system');
    [LONG, 'Hi', 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen', '100-day streak. Amazing.'].forEach((text) => {
      [1200, 1400, 1600, 2000].forEach((cap) => {
        const sp = spans(z.talkPlan(text, { max: cap }));
        sp.forEach(([a, b]) => assert.ok(b - a >= 60, 'open frame ' + (b - a) + ' ms'));
        for (let i = 1; i < sp.length; i += 1) assert.ok(sp[i][0] - sp[i - 1][0] >= 111, 'cycle ' + (sp[i][0] - sp[i - 1][0]) + ' ms is over 9 Hz');
      });
    });
    // the natural pace is the 135 ms cycle (75 open, 60 shut) for a line that fits
    const nat = spans(z.talkPlan('banana', { max: 2000 }));
    assert.strictEqual(nat.length, 3);
    assert.strictEqual(nat[0][1] - nat[0][0], 75);
    assert.strictEqual(nat[1][0] - nat[0][0], 135);
    assert.strictEqual(nat[0][2], 2, 'first syllable of a word is the open frame');
    assert.strictEqual(nat[1][2], 1, 'later syllables are half open');
    assert.strictEqual(spans(z.talkPlan('an', { max: 2000 }))[0][2], 1, 'one and two letter words are half open');
  });

  await scenario('punctuation pauses', () => {
    const { z } = load('system');
    const ms = (t) => z.talkPlan(t, { max: 2000 }).ms;
    const base = ms('Hi there you');
    assert.ok(ms('Hi, there you') - base >= 100, 'comma adds at least 100 ms (140 less the 40 ms gap)');
    assert.ok(ms('Hi; there you') - base >= 100, 'semicolon');
    assert.ok(ms('Hi: there you') - base >= 140, 'colon 180');
    assert.ok(ms('Hi. there you') - base >= 220, 'full stop 260');
    assert.ok(ms('Hi? there you') - base >= 220, 'question mark');
    assert.ok(ms('Hi… there you') - base >= 320, 'ellipsis 360');
    assert.ok(ms('Hi... there you') - base >= 320, 'three dots');
    assert.ok(ms('Hi. there you') > ms('Hi, there you'), 'a full stop pauses longer than a comma');
    assert.strictEqual(ms('Hi there you.'), base, 'punctuation at the very end adds no pause');
    assert.strictEqual(ms('Hi there you!?'), base);
    // a compressed plan keeps its pauses, shortened but not below 60 percent
    const tight = z.talkPlan(LONG, { max: 1200 });
    assert.ok(tight.ms <= 1200);
  });

  await scenario('ends closed', () => {
    const { z } = load('system');
    [LONG, 'Hi', 'Hello there, friend.', 'Wow!'].forEach((t) => [1200, 1600].forEach((cap) => {
      const plan = z.talkPlan(t, { max: cap });
      assert.strictEqual(plan.frames[0][0] === 0 && plan.frames[0][1] === 0, true, 'starts closed');
      assert.strictEqual(plan.frames[plan.frames.length - 1][1], 0, 'last frame is closed');
      assert.ok(plan.ms > plan.frames[plan.frames.length - 1][0], 'the closed frame has a duration');
      assert.strictEqual(plan.frames[1][0], 120, 'the first flap waits 120 ms');
    }));
  });

  await scenario('reduced and off make no animate calls and resolve false', async () => {
    for (const level of ['reduced', 'off']) {
      const { z } = load(level);
      const m = buildMascot('nudge');
      z.bind(m.host);
      log.length = 0;
      assert.strictEqual(await z.talk({ el: m.host, text: LONG, max: 1600 }), false, level);
      assert.strictEqual(log.length, 0, level + ': no animate call');
      assert.strictEqual(m.talkGroup(), null, level + ': no talk group');
      const t = mk('p');
      assert.strictEqual(await z.say(t, 'Hello there', { el: m.host, max: 1200 }), false);
      assert.strictEqual(t.textContent, 'Hello there', level + ': the text is still written at once');
      assert.strictEqual(log.length, 0);
    }
    const { z } = load('system', { osReduced: true });
    const m = buildMascot('nudge');
    z.bind(m.host);
    log.length = 0;
    assert.strictEqual(await z.talk({ el: m.host, text: 'Hello there', max: 1200 }), false, 'the OS setting');
    assert.strictEqual(log.length, 0);
  });

  await scenario('hidden tab hushes', async () => {
    const h = load('system');
    const m = buildMascot('nudge');
    h.z.bind(m.host);
    const p = h.z.talk({ el: m.host, text: LONG, max: 1600 });
    assert.strictEqual(h.z.isTalking(m.host), true);
    h.doc.hidden = true;
    h.fire('visibilitychange');
    assert.strictEqual(h.z.isTalking(m.host), false);
    assert.strictEqual(m.talkGroup(), null);
    assert.strictEqual(await p, false);
    log.length = 0;
    assert.strictEqual(await h.z.talk({ el: m.host, text: 'Hello', max: 1200 }), false, 'no talk in a hidden tab');
    assert.strictEqual(log.length, 0);
    h.doc.hidden = false;
    // off screen: the observer reports it gone
    h.z.talk({ el: m.host, text: LONG, max: 1600 });
    assert.strictEqual(h.z.isTalking(m.host), true);
    h.observers[0].cb([{ target: m.svg, isIntersecting: false }]);
    assert.strictEqual(h.z.isTalking(m.host), false, 'off screen hushes');
    // not rendered (display none): refuse
    m.svg._hidden = true;
    assert.strictEqual(await h.z.talk({ el: m.host, text: 'Hello', max: 1200 }), false);
  });

  await scenario('motion dropping mid-talk hushes (OS query, data-motion, data-motion-preview)', async () => {
    const start = (h, m) => { const p = h.z.talk({ el: m.host, text: LONG, max: 1600 }); assert.strictEqual(h.z.isTalking(m.host), true); return p; };
    // OS prefers-reduced-motion flips on
    let h = load('system');
    let m = buildMascot('nudge');
    h.z.bind(m.host);
    let p = start(h, m);
    h.mq.matches = true;
    h.mq.handlers.forEach((fn) => fn());
    assert.strictEqual(h.z.isTalking(m.host), false, 'the media query hushes');
    assert.strictEqual(m.talkGroup(), null);
    assert.strictEqual(await p, false);
    // data-motion set to reduced / off
    for (const level of ['reduced', 'off']) {
      h = load('system');
      m = buildMascot('nudge');
      h.z.bind(m.host);
      p = start(h, m);
      h.html.setAttribute('data-motion', level);
      h.mutate();
      assert.strictEqual(h.z.isTalking(m.host), false, 'data-motion=' + level + ' hushes');
      assert.strictEqual(await p, false);
    }
    // the dev preview attribute removed while the OS asks for reduced motion
    h = load('system', { osReduced: true });
    h.html.setAttribute('data-motion-preview', 'full');
    m = buildMascot('nudge');
    h.z.bind(m.host);
    p = start(h, m);
    h.html.removeAttribute('data-motion-preview');
    h.mutate();
    assert.strictEqual(h.z.isTalking(m.host), false, 'data-motion-preview removed hushes');
    assert.strictEqual(await p, false);
    // a change that keeps full motion leaves the talk alone
    h = load('system');
    m = buildMascot('nudge');
    h.z.bind(m.host);
    start(h, m);
    h.mutate();
    h.mq.handlers.forEach((fn) => fn());
    assert.strictEqual(h.z.isTalking(m.host), true, 'still full: keeps talking');
  });

  await scenario('a cut-short side-view clip ends the talk it carried (no side mouth on a front Zorp)', async () => {
    const h = load('system');
    const m = buildMascot('nudge');
    h.z.bind(m.host);
    hold.on = true;
    try {
      h.z.play('side-point', { el: m.host });
      await flush();
      assert.strictEqual(h.z.viewOf(m.host).view, 'side', 'the excursion reached the side view');
      const p = h.z.talk({ el: m.host, text: LONG, max: 1600 });
      assert.strictEqual(h.z.isTalking(m.host), true);
      assert.ok(m.talkGroup().childNodes.some((c) => c.firstChild.attrs['data-id'] === 'mouth:side-talk-1'), 'side talk art');
      h.z.play('blink', { el: m.host });   // play() stops the clip: the view goes home
      assert.strictEqual(h.z.viewOf(m.host).view, 'front', 'cut short: back on the front view');
      assert.strictEqual(h.z.isTalking(m.host), false, 'the side talk ended with the view');
      assert.strictEqual(m.talkGroup(), null, 'no side mouth left on a front Zorp');
      assert.strictEqual(await p, false);
    } finally { hold.on = false; }
  });

  await scenario('quiz runner never talks', async () => {
    const h = load('system');
    h.doc.body.setAttribute('data-guide-quiz', '1');
    const m = buildMascot('nudge');
    h.z.bind(m.host);
    log.length = 0;
    assert.strictEqual(await h.z.talk({ el: m.host, text: 'Hello', max: 1200 }), false);
    assert.strictEqual(log.length, 0);
  });

  await scenario('back view refuses', async () => {
    const { z } = load('system');
    const m = buildMascot('nudge', 'back');
    z.bind(m.host);
    log.length = 0;
    assert.strictEqual(await z.talk({ el: m.host, text: 'Hello there', max: 1200 }), false);
    assert.strictEqual(log.length, 0);
    assert.strictEqual(m.talkGroup(), null);
  });

  await scenario('clip stop keeps talking', async () => {
    const { z } = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    z.talk({ el: m.host, text: LONG, max: 1600 });
    const clip = z.play('nod', { el: m.host });   // play() calls stop(inst), which cancels inst.anims
    advance(100);
    assert.strictEqual(z.isTalking(m.host), true, 'a gesture does not end the talk');
    assert.ok(m.talkGroup(), 'the group is still there');
    log.filter((a) => a.el.parentNode && a.el.parentNode.getAttribute && a.el.parentNode.getAttribute('class') === 'zorp-slot--talk').forEach((a) => assert.strictEqual(a.cancelled, false));
    z.hush(m.host);
    advance(1300);
    assert.strictEqual(await clip, true);
  });

  await scenario('expression swap mid-talk', async () => {
    const { z } = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    z.talk({ el: m.host, text: LONG, max: 1600 });
    assert.strictEqual(z.setExpression('happy', { el: m.host }), true);
    assert.strictEqual(z.isTalking(m.host), true, 'an expression swap does not end the talk');
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'happy');
    assert.ok(m.slot('mouth').firstChild, 'the base mouth was redrawn under the talk');
    z.hush(m.host);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'happy', 'hush never touches the expression');
  });

  await scenario('a swap to an open mouth mid-talk closes on a smile', async () => {
    const { z } = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    log.length = 0;
    z.talk({ el: m.host, text: LONG, max: 1600 });
    assert.strictEqual(log.length, 3);
    z.setExpression('joy', { el: m.host });   // grin-tongue: a gesture's open mouth
    assert.strictEqual(z.isTalking(m.host), true);
    const parts = m.talkGroup().childNodes.map((g) => g.firstChild.attrs['data-id']);
    assert.deepStrictEqual(parts, ['mouth:talk-1', 'mouth:talk-2', 'mouth:smile']);
    assert.strictEqual(log[2].cancelled, true, 'the closed-frame base slot animation is replaced');
    const live = log.filter((a) => !a.cancelled && a.frames.length > 2);
    assert.strictEqual(live.length, 4);
    const plan = z.talkPlan(LONG, { max: 1600 });
    plan.frames.forEach((f, i) => {
      if (i === 0) return;
      const on = live.filter((a) => a.frames[i].opacity === 1).map((a) => a.el);
      assert.strictEqual(on.length, 1, 'frame ' + i);
      assert.notStrictEqual(on[0], m.slot('mouth'), 'the open base mouth never shows between flaps');
    });
    z.setExpression('grin', { el: m.host });
    assert.strictEqual(log.filter((a) => !a.cancelled && a.frames.length > 2).length, 4, 'a second open swap changes nothing');
    z.hush(m.host);
    assert.strictEqual(m.talkGroup(), null);
  });

  await scenario('one talker at a time', async () => {
    const { z } = load('system');
    const a = buildMascot('nudge');
    const b = buildMascot('nudge');
    z.bind(a.host);
    z.bind(b.host);
    const pa = z.talk({ el: a.host, text: LONG, max: 1600 });
    assert.strictEqual(z.isTalking(a.host), true);
    const pb = z.talk({ el: b.host, text: LONG, max: 1600 });
    assert.strictEqual(z.isTalking(a.host), false, 'the first talker was hushed');
    assert.strictEqual(z.isTalking(b.host), true);
    assert.strictEqual(a.talkGroup(), null);
    assert.ok(b.talkGroup());
    assert.strictEqual(await pa, false);
    advance(2100);
    assert.strictEqual(await pb, true, 'a talk that runs to its end resolves true');
    assert.strictEqual(b.talkGroup(), null, 'the group is removed at the end');
    assert.strictEqual(timers.length, 0, 'no timer is left behind');
  });

  await scenario('hush restores base mouth and removes the group', async () => {
    const { z } = load('system');
    const m = buildMascot('grin');
    z.bind(m.host);
    const mouth = m.slot('mouth');
    const before = mouth.childNodes.length;
    log.length = 0;
    const p = z.talk({ el: m.host, text: LONG, max: 1600 });
    const mine = log.slice();
    assert.ok(m.talkGroup(), 'group created beside the mouth slot');
    assert.strictEqual(m.face.childNodes[m.face.childNodes.indexOf(mouth) + 1], m.talkGroup(), 'the group is the mouth slot’s next sibling');
    z.hush(m.host);
    assert.strictEqual(m.talkGroup(), null);
    assert.ok(mine.length >= 3 && mine.every((a) => a.cancelled), 'every talk animation cancelled (the base slot opacity returns)');
    assert.strictEqual(mouth.childNodes.length, before, 'the base mouth art is untouched');
    assert.strictEqual(mouth.style.opacity, undefined, 'nothing is written on the base slot');
    assert.strictEqual(await p, false);
    assert.strictEqual(timers.length, 0);
    z.hush(m.host);   // idempotent
    z.hush();
    assert.strictEqual(z.isTalking(m.host), false);
  });

  await scenario('say writes the text synchronously', async () => {
    const { z } = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    const target = mk('p');
    events.length = 0;
    const p = z.say(target, LONG, { el: m.host, max: 1600 });
    assert.strictEqual(target.textContent, LONG, 'the text is there as say() returns');
    assert.strictEqual(events[0], 'text:' + LONG, 'the text is written before any animation is created');
    assert.ok(events.indexOf('animate') > 0);
    // every layer waits 120 ms before its first flap, so the text is on screen first
    const talkLayers = log.filter((a) => a.frames.length > 2);
    talkLayers.forEach((a) => assert.ok(a.frames[0].offset === 0 && (a.frames[1].offset * a.opts.duration) >= 119));
    z.say(target, 'Second line', { el: m.host, max: 1200, talk: false });
    assert.strictEqual(target.textContent, 'Second line');
    assert.strictEqual(z.isTalking(m.host), false, 'say with talk:false hushes and does not talk');
    assert.strictEqual(await p, false);
    assert.strictEqual(await z.say(target, 'No face', { max: 1200 }), false, 'say without a face just writes text');
    assert.strictEqual(target.textContent, 'No face');
  });

  await scenario('layers are stepped opacity only', async () => {
    const { z } = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    log.length = 0;
    z.talk({ el: m.host, text: LONG, max: 1600 });
    assert.strictEqual(log.length, 3, 'base slot, talk-1 and talk-2: one animation per layer');
    log.forEach((a) => {
      assert.strictEqual(a.opts.fill, 'none');
      a.frames.forEach((f) => {
        assert.deepStrictEqual(Object.keys(f).filter((k) => ['offset', 'opacity', 'easing'].indexOf(k) === -1), []);
        if (f.offset < 1) assert.strictEqual(f.easing, 'steps(1, end)');
      });
    });
    // at every moment exactly one of the three layers is shown
    const plan = z.talkPlan(LONG, { max: 1600 });
    plan.frames.forEach((f, i) => {
      assert.strictEqual(log.reduce((n, a) => n + a.frames[i].opacity, 0), 1, 'frame ' + i);
    });
    const parts = m.talkGroup().childNodes.map((g) => g.firstChild.attrs['data-id']);
    assert.deepStrictEqual(parts, ['mouth:talk-1', 'mouth:talk-2']);
    assert.strictEqual(m.talkGroup().getAttribute('class'), 'zorp-slot--talk');
  });

  await scenario('open base mouth gets a drawn smile as the closed frame', async () => {
    const { z } = load('system');
    const m = buildMascot('grin');
    z.bind(m.host);
    log.length = 0;
    z.talk({ el: m.host, text: LONG, max: 1600 });
    assert.strictEqual(log.length, 4, 'base slot, talk-1, talk-2 and the smile');
    const parts = m.talkGroup().childNodes.map((g) => g.firstChild.attrs['data-id']);
    assert.deepStrictEqual(parts, ['mouth:talk-1', 'mouth:talk-2', 'mouth:smile']);
    const plan = z.talkPlan(LONG, { max: 1600 });
    plan.frames.forEach((f, i) => {
      assert.strictEqual(log.reduce((n, a) => n + a.frames[i].opacity, 0), 1, 'frame ' + i);
    });
    assert.strictEqual(log[2].frames[0].opacity, 1, 'the grin (the base slot, third animation) stays until the first flap');
    assert.strictEqual(log[2].frames[2].opacity, 0, 'and is hidden for the rest of the talk');
  });

  await scenario('side view uses side art and copies view styles', async () => {
    const { z } = load('system');
    const m = buildMascot('nudge', 'side');
    z.bind(m.host);
    m.slot('mouth').style.translate = '2px 1px';
    m.slot('mouth').style.scale = '-1 1';
    z.talk({ el: m.host, text: LONG, max: 1600 });
    const g = m.talkGroup();
    assert.deepStrictEqual(g.childNodes.map((x) => x.firstChild.attrs['data-id']), ['mouth:side-talk-1', 'mouth:side-talk-2']);
    assert.strictEqual(g.style.translate, '2px 1px');
    assert.strictEqual(g.style.scale, '-1 1');
    z.hush(m.host);
    const f = buildMascot('grin', 'side');
    z.bind(f.host);
    z.talk({ el: f.host, text: LONG, max: 1600 });
    assert.deepStrictEqual(f.talkGroup().childNodes.map((x) => x.firstChild.attrs['data-id']), ['mouth:side-talk-1', 'mouth:side-talk-2', 'mouth:side-smile']);
    const front = buildMascot('nudge');
    z.bind(front.host);
    z.talk({ el: front.host, text: LONG, max: 1600 });
    assert.strictEqual(front.talkGroup().style.translate, undefined, 'front placement copies nothing');
  });

  await scenario('no innerHTML', () => {
    const src = fs.readFileSync(talkPath, 'utf8');
    assert.ok(!/innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function/.test(src));
    assert.ok(!/requestAnimationFrame|setInterval/.test(src), 'no frame loop');
  });

  const failed = results.filter((r) => !r[1]);
  console.log(results.length - failed.length + ' of ' + results.length + ' scenarios passed');
  finished = true;
  process.exit(failed.length ? 1 : 0);
})();
