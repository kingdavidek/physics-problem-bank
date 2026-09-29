/* Node harness for scripts/test_buddy_gate_smoke.py.
 * Runs the real static/js/study-buddy.js source against a minimal hand-rolled
 * fake DOM + localStorage (no jsdom / npm deps -- none are available offline),
 * exercising the pb-buddy-quiet gate (maybeShow/shouldShow) exactly as a real
 * page load + click would. Each scenario gets a completely fresh vm context
 * (module-level code in study-buddy.js runs once per "page load", same as
 * in a real browser), fresh DOM, and its own localStorage.
 *
 * Usage: node buddy_gate_harness.js <path-to-study-buddy.js>
 */
'use strict';
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

const SRC_PATH = process.argv[2];
if (!SRC_PATH) {
  console.error('usage: node buddy_gate_harness.js <study-buddy.js path>');
  process.exit(2);
}
const SOURCE = fs.readFileSync(SRC_PATH, 'utf8');

function matchesSel(el, sel) {
  if (sel[0] === '#') return el.attrs.id === sel.slice(1);
  const m = sel.match(/^\[([a-zA-Z0-9-]+)\]$/);
  if (m) return Object.prototype.hasOwnProperty.call(el.attrs, m[1]);
  return false;
}

function walk(el, fn) {
  el.children.forEach((c) => {
    fn(c);
    walk(c, fn);
  });
}

function queryOne(el, sel) {
  let found = null;
  walk(el, (c) => {
    if (!found && matchesSel(c, sel)) found = c;
  });
  return found;
}

function queryAll(el, sel) {
  const out = [];
  walk(el, (c) => {
    if (matchesSel(c, sel)) out.push(c);
  });
  return out;
}

function makeEl(tag, attrs) {
  const el = {
    tag,
    attrs: Object.assign({}, attrs || {}),
    children: [],
    parentNode: null,
    listeners: {},
    _hidden: false,
    _text: '',
    get hidden() { return this._hidden; },
    set hidden(v) { this._hidden = !!v; },
    get textContent() { return this._text; },
    set textContent(v) { this._text = v == null ? '' : String(v); },
    setAttribute(k, v) { this.attrs[k] = String(v); },
    getAttribute(k) {
      return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
    },
    removeAttribute(k) { delete this.attrs[k]; },
    hasAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); },
    addEventListener(type, fn) {
      (this.listeners[type] = this.listeners[type] || []).push(fn);
    },
    dispatch(type, evt) {
      (this.listeners[type] || []).forEach((fn) => fn(evt || {}));
    },
    appendChild(c) {
      c.parentNode = this;
      this.children.push(c);
      return c;
    },
    removeChild(c) {
      this.children = this.children.filter((x) => x !== c);
      c.parentNode = null;
      return c;
    },
    insertBefore(newNode, refNode) {
      const idx = this.children.indexOf(refNode);
      this.children.splice(idx < 0 ? this.children.length : idx, 0, newNode);
      newNode.parentNode = this;
      return newNode;
    },
    querySelector(sel) { return queryOne(this, sel); },
    querySelectorAll(sel) { return queryAll(this, sel); },
    matches(sel) { return matchesSel(this, sel); },
  };
  return el;
}

function makeStorage(opts) {
  opts = opts || {};
  const data = Object.assign({}, opts.seed || {});
  const order = Object.keys(data);
  const broken = !!opts.broken;
  return {
    getItem(key) {
      if (broken) throw new Error('storage broken');
      return Object.prototype.hasOwnProperty.call(data, key) ? data[key] : null;
    },
    setItem(key, value) {
      if (broken) throw new Error('storage broken');
      if (!Object.prototype.hasOwnProperty.call(data, key)) order.push(key);
      data[key] = String(value);
    },
    removeItem(key) {
      if (broken) throw new Error('storage broken');
      delete data[key];
      const i = order.indexOf(key);
      if (i >= 0) order.splice(i, 1);
    },
    key(i) { return order[i]; },
    get length() { return order.length; },
    _dump() { return Object.assign({}, data); },
  };
}

// Builds one fresh "page load": a document containing the study-buddy aside
// markup (mirroring templates/base.html) plus the pb-buddy-prompt JSON island,
// runs study-buddy.js in its own vm context, and returns handles to poke at.
function loadPage({ prompt, storageSeed, storageBroken, zorp }) {
  const root = makeEl('aside', { 'data-buddy-root': '', 'data-buddy-state': 'face' });
  const faceEl = makeEl('span', { 'data-buddy-face': '', 'data-face': 'nudge' });
  const card = makeEl('div', { 'data-buddy-card': '', hidden: '' });
  card.hidden = true;
  const detailEl = makeEl('span', { 'data-buddy-detail': '' });
  const messageEl = makeEl('p', { 'data-buddy-message': '' });
  const actionsEl = makeEl('div', { 'data-buddy-actions': '' });
  const actionEl = makeEl('a', { 'data-buddy-action': '' });
  const dismissEl = makeEl('button', { 'data-buddy-dismiss': '' });
  actionsEl.appendChild(actionEl);
  actionsEl.appendChild(dismissEl);
  card.appendChild(detailEl);
  card.appendChild(messageEl);
  card.appendChild(actionsEl);
  root.appendChild(faceEl);
  root.appendChild(card);

  const promptIsland = makeEl('script', { id: 'pb-buddy-prompt', type: 'application/json' });
  promptIsland.textContent = JSON.stringify(prompt === undefined ? null : prompt);

  const bodyRoot = makeEl('body', {});
  bodyRoot.appendChild(promptIsland);
  bodyRoot.appendChild(root);

  const documentStub = {
    _root: bodyRoot,
    getElementById(id) { return queryOne(this._root, '#' + id); },
    querySelector(sel) { return queryOne(this._root, sel); },
    querySelectorAll(sel) { return queryAll(this._root, sel); },
    createElement(tag) { return makeEl(tag); },
    addEventListener() {},
  };

  const storage = makeStorage({ seed: storageSeed, broken: storageBroken });
  const windowStub = {
    localStorage: storage,
    location: { pathname: '/topic/gcse/maths/algebra', search: '' },
    matchMedia() { return { matches: false }; },
    setTimeout: () => 0,
    clearTimeout: () => {},
  };
  // E8 Phase 1: optional pbZorp stub (real study-buddy.js asks pbZorp.hasExpression for face names).
  if (zorp) windowStub.pbZorp = zorp;

  const sandbox = { window: windowStub, document: documentStub, console };
  vm.createContext(sandbox);
  vm.runInContext(SOURCE, sandbox, { filename: 'study-buddy.js' });

  return { root, card, faceEl, actionEl, actionsEl, dismissEl, storage };
}

function clickPrimary(page) {
  page.actionsEl.dispatch('click', { target: page.actionEl });
}

function clickDismiss(page) {
  page.dismissEl.dispatch('click', {});
}

function readQuiet(page) {
  const raw = page.storage.getItem('pb-buddy-quiet');
  return raw ? JSON.parse(raw) : null;
}

const results = [];
function scenario(name, fn) {
  try {
    fn();
    results.push([name, true, null]);
    console.log('OK:', name);
  } catch (err) {
    results.push([name, false, err && err.stack || String(err)]);
    console.error('FAIL:', name);
    console.error(err && err.stack || err);
  }
}

const PROMPT_A = {
  type: 'streak_risk',
  message: 'Your streak is at risk.',
  detail: 'Streak reminder',
  action_url: '/topics',
  action_label: 'Browse topics',
  task_mark: '2026-09-27.q1.d0.l.m0',
};
const PROMPT_B = Object.assign({}, PROMPT_A, { task_mark: '2026-09-27.q2.d0.l.m0' });

scenario('prompt shows the card on initial load', () => {
  const page = loadPage({ prompt: PROMPT_A });
  assert.strictEqual(page.card.hidden, false);
  assert.strictEqual(page.root.getAttribute('data-buddy-state'), 'card');
  assert.strictEqual(page.root.hidden, false, 'root must never be hidden');
});

scenario('no prompt (null) leaves the card hidden, face stays put', () => {
  const page = loadPage({ prompt: null });
  assert.strictEqual(page.card.hidden, true);
  assert.strictEqual(page.root.getAttribute('data-buddy-state'), 'face');
  assert.strictEqual(page.root.hidden, false);
});

scenario('primary click hides the card, keeps root visible, quiets 10 min', () => {
  const page = loadPage({ prompt: PROMPT_A });
  assert.strictEqual(page.card.hidden, false);
  const before = Date.now();
  clickPrimary(page);
  const after = Date.now();
  assert.strictEqual(page.card.hidden, true);
  assert.strictEqual(page.root.hidden, false, 'root must stay visible after acting on the bubble');
  assert.strictEqual(page.root.getAttribute('data-buddy-state'), 'face');
  const quiet = readQuiet(page);
  assert.ok(quiet, 'expected a pb-buddy-quiet entry after clicking');
  const diff = quiet.until - before;
  assert.ok(diff >= 10 * 60 * 1000 - 50 && diff <= (after - before) + 10 * 60 * 1000 + 50,
    `expected ~10 minute quiet window, got ${diff}ms`);
  assert.strictEqual(quiet.mark, PROMPT_A.task_mark);
});

scenario('secondary (extra) link click also hides the card and quiets 10 min', () => {
  const prompt = Object.assign({}, PROMPT_A, {
    actions: [
      { kind: 'link', label: 'Take a quiz', url: '/lesson-quiz/gcse/maths/algebra' },
      { kind: 'link', label: 'Practise MCQ', url: '/?level=gcse&topic=algebra' },
    ],
  });
  const page = loadPage({ prompt });
  const extra = page.actionsEl.querySelector('[data-buddy-extra]');
  assert.ok(extra, 'expected study-buddy.js to render a [data-buddy-extra] link');
  const before = Date.now();
  page.actionsEl.dispatch('click', { target: extra });
  assert.strictEqual(page.card.hidden, true);
  assert.strictEqual(page.root.hidden, false);
  const quiet = readQuiet(page);
  assert.ok(quiet, 'expected a pb-buddy-quiet entry after clicking an extra link');
  const diff = quiet.until - before;
  assert.ok(diff >= 10 * 60 * 1000 - 50 && diff <= 10 * 60 * 1000 + 2000,
    `expected ~10 minute quiet window, got ${diff}ms`);
});

scenario('dismiss ("Not now") hides the card and quiets 30 min', () => {
  const page = loadPage({ prompt: PROMPT_A });
  const before = Date.now();
  clickDismiss(page);
  assert.strictEqual(page.card.hidden, true);
  assert.strictEqual(page.root.hidden, false);
  const quiet = readQuiet(page);
  assert.ok(quiet);
  const diff = quiet.until - before;
  assert.ok(diff >= 30 * 60 * 1000 - 50 && diff <= 30 * 60 * 1000 + 2000,
    `expected ~30 minute quiet window, got ${diff}ms`);
});

scenario('same mark, still within the quiet window: card stays hidden', () => {
  const until = Date.now() + 5 * 60 * 1000; // 5 minutes still to go
  const page = loadPage({
    prompt: PROMPT_A,
    storageSeed: { 'pb-buddy-quiet': JSON.stringify({ until, mark: PROMPT_A.task_mark }) },
  });
  assert.strictEqual(page.card.hidden, true, 'a bubble must not reappear mid-quiet-window');
  assert.strictEqual(page.root.getAttribute('data-buddy-state'), 'face');
});

scenario('same mark, window has passed: card stays hidden (nothing new happened)', () => {
  const until = Date.now() - 1000; // window already elapsed
  const page = loadPage({
    prompt: PROMPT_A,
    storageSeed: { 'pb-buddy-quiet': JSON.stringify({ until, mark: PROMPT_A.task_mark }) },
  });
  assert.strictEqual(page.card.hidden, true,
    'an unchanged task_mark after the window must still stay quiet');
});

scenario('new mark, window has passed: card shows again', () => {
  const until = Date.now() - 1000;
  const page = loadPage({
    prompt: PROMPT_B,
    storageSeed: { 'pb-buddy-quiet': JSON.stringify({ until, mark: PROMPT_A.task_mark }) },
  });
  assert.strictEqual(page.card.hidden, false,
    'a new task_mark after the window elapses must show again');
  assert.strictEqual(page.root.getAttribute('data-buddy-state'), 'card');
});

scenario('ignored bubble keeps showing on a later load (no auto-quiet-on-display)', () => {
  // Loading the same prompt twice in a row (nobody clicked anything) must show it
  // both times -- David's decision: an ignored bubble persists until clicked.
  const page1 = loadPage({ prompt: PROMPT_A });
  assert.strictEqual(page1.card.hidden, false);
  const page2 = loadPage({ prompt: PROMPT_A, storageSeed: page1.storage._dump() });
  assert.strictEqual(page2.card.hidden, false,
    'an un-acted-on prompt must not go quiet on its own');
});

scenario('a throwing localStorage does not crash the page load', () => {
  const page = loadPage({ prompt: PROMPT_A, storageBroken: true });
  // readQuiet() catches and treats broken storage as "no quiet state" -> shows.
  assert.strictEqual(page.card.hidden, false);
  assert.doesNotThrow(() => clickPrimary(page));
  assert.doesNotThrow(() => clickDismiss(page));
});

function zorpStub(known) {
  const calls = [];
  return {
    calls,
    hasExpression: (name) => known.indexOf(name) !== -1,
    setFace: (name) => { calls.push(name); return true; },
    bind: () => null,
    idle: () => true,
    play: () => Promise.resolve(true),
  };
}

scenario('E8: with pbZorp, a prompt type the runtime knows is applied through setFace', () => {
  const zorp = zorpStub(['nudge', 'streak_risk', 'happy']);
  loadPage({ prompt: Object.assign({}, PROMPT_A, { type: 'happy' }), zorp });
  assert.deepStrictEqual(zorp.calls, ['happy']);
});

scenario('E8: with pbZorp, an unknown prompt type falls back to the emoji map, then nudge', () => {
  const zorp = zorpStub(['nudge', 'streak_risk']);
  loadPage({ prompt: Object.assign({}, PROMPT_A, { type: 'not-a-face', face: '\u{1F525}' }), zorp });
  assert.deepStrictEqual(zorp.calls, ['streak_risk']);
  const zorp2 = zorpStub(['nudge']);
  loadPage({ prompt: Object.assign({}, PROMPT_A, { type: 'not-a-face', face: '?' }), zorp: zorp2 });
  assert.deepStrictEqual(zorp2.calls, ['nudge']);
});

scenario('E8: without pbZorp the local legacy allowlist still applies', () => {
  const page = loadPage({ prompt: Object.assign({}, PROMPT_A, { type: 'happy' }) });
  assert.strictEqual(page.faceEl.getAttribute('data-face'), 'nudge');
  const page2 = loadPage({ prompt: PROMPT_A });
  assert.strictEqual(page2.faceEl.getAttribute('data-face'), 'streak_risk');
});

const failed = results.filter((r) => !r[1]);
if (failed.length) {
  console.error(`\n${failed.length}/${results.length} buddy gate scenarios FAILED`);
  process.exit(1);
}
console.log(`\nAll ${results.length} buddy gate scenarios passed.`);
process.exit(0);
