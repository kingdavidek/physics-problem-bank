'use strict';
/* E8 Phase 2: behavioural harness for static/js/zorp-motion.js (run by test_zorp_runtime_smoke.py).
   No jsdom is available offline, so this uses a very small hand-rolled fake DOM (just what the
   runtime touches). Usage: node zorp_runtime_harness.js <zorp-motion.js> <rig.json>
   rig.json: { island: <rig_json() text>, channels: { eyes: [...], brows: [...], ... } }. */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const [, , scriptPath, rigPath] = process.argv;
if (!scriptPath || !rigPath) {
  console.error('usage: node zorp_runtime_harness.js <zorp-motion.js> <rig.json>');
  process.exit(2);
}
const rig = JSON.parse(fs.readFileSync(rigPath, 'utf8'));

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
  getClientRects() { return [1]; }
  getBoundingClientRect() { return { width: 1, height: 1 }; }
  animate(frames, opts) { animations.push({ el: this, frames, opts }); return { finished: Promise.resolve(), cancel() {} }; }
}
const animations = [];

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

function buildMascot(expr) {
  const slots = ['cheeks', 'eyeL', 'eyeR', 'brows', 'mouth', 'fx-face'].map((k) => {
    const cls = k === 'eyeL' ? 'buddy-eye buddy-eye--l zorp-slot--eyeL' : k === 'eyeR' ? 'buddy-eye buddy-eye--r zorp-slot--eyeR' : 'zorp-slot--' + k;
    return mk('g', cls);
  });
  const face = mk('g', 'zorp-face', slots);
  const head = mk('g', 'buddy-head', [mk('g', 'buddy-antenna--l'), mk('g', 'buddy-antenna--r'), mk('g', 'buddy-body'), face]);
  const rootG = mk('g', 'buddy-root', [mk('g', 'buddy-shadow'), mk('g', 'buddy-arm--l'), mk('g', 'buddy-arm--r'), head, mk('g', 'zorp-slot--fx')]);
  const svg = mk('svg', 'buddy-mascot', [rootG]);
  if (expr) svg.setAttribute('data-expr', expr);
  const host = mk('span', 'study-buddy-face', [svg]);
  host.setAttribute('data-buddy-face', '');
  host.setAttribute('data-face', expr || 'nudge');
  return { host, svg, slot: (k) => svg.querySelector('.zorp-slot--' + k) };
}

function load(motion) {
  animations.length = 0;
  const island = mk('script');
  island.setAttribute('id', 'pb-zorp-rig');
  island.textContent = rig.island;
  const tpl = mk('template');
  tpl.setAttribute('id', 'pb-zorp-parts');
  tpl.content = buildTemplate();
  const htmlEl = mk('html');
  if (motion !== 'system') htmlEl.setAttribute('data-motion', motion);
  const byId = { 'pb-zorp-rig': island, 'pb-zorp-parts': tpl };
  const sandbox = {
    document: {
      readyState: 'complete', hidden: false, body: mk('body'), documentElement: htmlEl,
      getElementById: (id) => byId[id] || null,
      addEventListener() {},
    },
    Element: El,
    Animation: class { get finished() { return null; } },
    setTimeout, clearTimeout, Promise, Object, Date, Math, JSON, console, Array, String,
  };
  sandbox.window = sandbox;
  sandbox.matchMedia = () => ({ matches: false, addEventListener() {} });
  vm.runInNewContext(fs.readFileSync(scriptPath, 'utf8'), sandbox);
  return sandbox.pbZorp;
}

const results = [];
async function scenario(name, fn) {
  try { await fn(); results.push([name, true]); console.log('OK: ' + name); }
  catch (e) { results.push([name, false]); console.error('FAIL: ' + name + '\n  ' + (e && e.stack || e)); }
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const partIds = (slot) => slot.childNodes.map((c) => c.attrs['data-id']);

(async () => {
  await scenario('valenceOf and allowedIn read the island', () => {
    const z = load('system');
    assert.strictEqual(z.valenceOf('sad'), 'negative');
    assert.strictEqual(z.valenceOf('nudge'), 'neutral');
    assert.strictEqual(z.valenceOf('joy'), 'positive');
    assert.strictEqual(z.valenceOf('bogus'), null);
    assert.strictEqual(z.allowedIn('guide', 'sad'), false);
    assert.strictEqual(z.allowedIn('guide.lore', 'sad'), true);
    assert.strictEqual(z.allowedIn('guide', 'joy'), true);
    assert.strictEqual(z.allowedIn('guide.lore', 'embarrassed'), false);
    assert.strictEqual(z.allowedIn('guide', 'bogus'), false);
    assert.ok(z.expressions.indexOf('sad') !== -1 && z.expressions.indexOf('wink') !== -1);
  });

  await scenario('fx route to the face-attached slot or the ambient slot, never both', () => {
    const z = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    assert.strictEqual(z.setExpression('sad', { el: m.host }), true);
    assert.deepStrictEqual(partIds(m.slot('fx-face')), ['fx:tear-shine']);
    assert.strictEqual(m.slot('fx').childNodes.length, 0);
    assert.strictEqual(z.setExpression('joy', { el: m.host }), true);
    assert.deepStrictEqual(partIds(m.slot('fx')), ['fx:sparkles']);
    assert.strictEqual(m.slot('fx-face').childNodes.length, 0);
    assert.strictEqual(z.setExpression('embarrassed', { el: m.host }), true);
    assert.deepStrictEqual(partIds(m.slot('fx-face')), ['fx:sweat']);
    assert.strictEqual(m.slot('fx').childNodes.length, 0);
  });

  await scenario('data-expr follows presets, duplicates keep the asked name, object form is custom', () => {
    const z = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    z.setExpression('heads-up', { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'heads-up');
    z.setExpression('streak_risk', { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'streak_risk');
    z.setExpression('nudge', { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'nudge');
    assert.strictEqual(z.setExpression({ mouth: 'grin' }, { el: m.host }), true);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'custom', 'nudge with a grin is no preset');
    assert.strictEqual(z.setExpression({ mouth: 'smile' }, { el: m.host }), true);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'nudge', 'channels that match a preset name it again');
    z.setExpression({ eyes: 'smile-arc', brows: 'soft', mouth: 'smile-wide', cheeks: 'rosy' }, { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'happy');
    assert.strictEqual(z.setExpression({ mouth: 'no-such-mouth' }, { el: m.host }), false);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'happy', 'a refused call changes nothing');
  });

  await scenario('data-expr stays in sync during a clip and after it', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    const done = z.play('cheer', { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'celebrate', 'during the clip');
    assert.strictEqual(m.host.getAttribute('data-face'), 'celebrate');
    await done;
    await sleep(760);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'nudge', 'restored after the clip');
    assert.strictEqual(m.host.getAttribute('data-face'), 'nudge');
    // a clip that starts from a custom face restores the custom channels
    z.setExpression({ mouth: 'grin' }, { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'custom');
    await z.play('wave', { el: m.host });
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'milestone');
    await sleep(960);
    assert.strictEqual(m.svg.getAttribute('data-expr'), 'custom');
  });

  await scenario('full motion animates part swaps (80/90/120 ms); reduced and off swap instantly', () => {
    const z = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    z.setExpression('happy', { el: m.host });   // eyes, brows, mouth, cheeks all change
    const durs = animations.map((a) => a.opts.duration).sort((a, b) => a - b);
    assert.deepStrictEqual(durs, [80, 80, 90, 120], 'eye, eye, mouth, cheeks');
    const cheek = animations.find((a) => a.opts.duration === 120);
    assert.strictEqual(JSON.stringify(cheek.frames.map((f) => f.opacity)), '[0,1]');
    for (const level of ['reduced', 'off']) {
      const z2 = load(level);
      const m2 = buildMascot('nudge');
      z2.bind(m2.host);
      assert.strictEqual(z2.setExpression('happy', { el: m2.host }), true);
      assert.strictEqual(animations.length, 0, level + ' must not animate swaps');
      assert.deepStrictEqual(partIds(m2.slot('mouth')), ['mouth:smile-wide'], level + ' still swaps instantly');
    }
  });

  await scenario('thought is an fx part: shown on a wrong reaction, put back afterwards, never in reduced', async () => {
    const z = load('system');
    const m = buildMascot('nudge');
    z.bind(m.host);
    z.setExpression('joy', { el: m.host });
    animations.length = 0;
    const p = z.play('wobble', { el: m.host, thought: true });
    assert.deepStrictEqual(partIds(m.slot('fx')), ['fx:thought'], 'thought drawn in the ambient slot');
    assert.ok(animations.some((a) => a.el === m.slot('fx').firstElementChild), 'bubble animated with WAAPI');
    assert.ok(!m.svg._descendants([]).some((e) => e._cls.indexOf('buddy-thought') !== -1), 'no buddy-thought node');
    await p;
    await sleep(1250);
    assert.deepStrictEqual(partIds(m.slot('fx')), ['fx:sparkles'], 'the current expression fx come back');
    const zr = load('reduced');
    const mr = buildMascot('nudge');
    zr.bind(mr.host);
    await zr.play('wobble', { el: mr.host, thought: true });
    assert.strictEqual(mr.slot('fx').childNodes.length, 0, 'reduced motion never draws the thought bubble');
  });

  const failed = results.filter((r) => !r[1]);
  if (failed.length) { console.error(`\n${failed.length}/${results.length} zorp runtime scenarios FAILED`); process.exit(1); }
  console.log(`\nAll ${results.length} zorp runtime scenarios passed.`);
  process.exit(0);
})();
