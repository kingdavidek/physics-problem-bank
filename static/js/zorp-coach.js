/* Coach mode (E10 phase 3, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A2 and section 10). The first question after the arrival
   is coached live: small callouts, in the page flow beside real elements, that wait for what the pupil actually does (no
   Next buttons). guide.js loads this file and static/css/coach.css only when the page is the first question
   (body[data-guide-coach], the guided practice not yet seen); ordinary pages never fetch either.
   Events it waits for (dispatched by site.js): pb-answer-checked {correct}, pb-hint-shown, pb-hint-bigger,
   pb-answer-unlocked. When it ends it fires pb-coach-ended {how: done | skip | leave}; guide.js marks the coach and the
   Practice tour seen. UK English; every line follows docs/ZORP_CHARM.md section 3.3 (scripts/test_zorp_voice_smoke.py reads
   this file). Faces come from models/zorp_rig.py CONTEXT_MAP['coach']. A step: id, lines, face, clip (full motion only). */
(function () {
  'use strict';
  if (window.pbCoach) return;

  var D = document;
  var CAT = {
    primary: 'Got it',
    skipLabel: 'Skip for now',
    // the order a wrong answer walks through; a step with nothing on the page to point at is skipped
    wrong: ['hint', 'bigger', 'reveal', 'note', 'close'],
    steps: [
      {
        id: 'answer',
        lines: ['Type your answer and press Check.'],
        face: 'happy',
        clip: 'wave',
      },
      {
        id: 'pick',
        lines: ['Pick an answer.'],
        face: 'happy',
        clip: 'wave',
      },
      {
        id: 'hint',
        lines: ['Here’s a hint. I only show them after you try.'],
        face: 'soft-smile',
        clip: 'side-point',
      },
      {
        id: 'bigger',
        lines: ['Want more? This shows the first step.'],
        face: 'soft-smile',
        clip: 'nod',
      },
      {
        id: 'reveal',
        lines: ['And here’s the full answer whenever you want it.'],
        face: 'soft-smile',
        clip: 'side-point',
      },
      {
        id: 'note',
        lines: ['Add a note if you like. It helps you remember what tripped you up.'],
        face: 'soft-smile',
        clip: 'nod',
      },
      {
        id: 'close',
        lines: ['That’s the loop: try, hint, try again.'],
        face: 'grin',
        clip: 'nod',
      },
    ],
  };
  var STEP = {};
  CAT.steps.forEach(function (s) { STEP[s.id] = s; });
  var AUTO_MS = { close: 10000 };   // the other tips after the first one fade out quietly if nothing happens
  var S = null;

  function Z() { return window.pbZorp || null; }
  function q(sel, root) { return (root || D).querySelector(sel); }
  function level() {
    var z = Z();
    if (z && z.motionLevel) return z.motionLevel();
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduced' : 'full';
  }
  function shown(n) { return !!n && !n.hidden && !!(n.offsetWidth || n.offsetHeight || n.getClientRects().length); }
  // a guide dialog (a reward) or a stage is open: the coach waits
  function blocked() {
    var g = D.getElementById('guide-root');
    return !!((g && !g.hidden) || (window.pbStage && window.pbStage.isOpen && window.pbStage.isOpen()));
  }

  // The part of the window the page leaves free: under the sticky header, above the fixed bars (New question, tab bar).
  function bounds() {
    var top = 0, bot = window.innerHeight, h = q('header');
    if (h && window.getComputedStyle(h).position !== 'static') top = h.getBoundingClientRect().bottom;
    ['practice-new-question-bar', 'app-tab-bar'].forEach(function (id) {
      var n = D.getElementById(id);
      if (shown(n) && window.getComputedStyle(n).position === 'fixed') bot = Math.min(bot, n.getBoundingClientRect().top);
    });
    return [top + 8, bot - 16];
  }

  // Where each tip points: t (outlined), a (the callout goes next to it), pos (before | after). Null: nothing to point at.
  var TARGET = {
    answer: function () {
      var box = q('.free-response-inline');
      if (!box) return null;
      var rows = box.querySelectorAll('.free-response-row'), row = null;
      for (var i = 0; i < rows.length && !row; i += 1) if (shown(rows[i])) row = rows[i];
      return { t: row || box, a: row || box, pos: 'before' };
    },
    pick: function () {
      var o = D.getElementById('mcq-options');
      return o ? { t: o, a: o, pos: 'before' } : null;
    },
    hint: function () {
      var c = q('.free-response-hint .hint-card') || q('.mcq-hint-slot .hint-card');
      return c && !c.hidden ? { t: c, a: c.parentNode, pos: 'before' } : null;
    },
    bigger: function () {
      var b = q('.free-response-hint-more');
      return b && !b.hidden && !b.getAttribute('aria-disabled') ? { t: b, a: b.parentNode, pos: 'after' } : null;
    },
    reveal: function () {
      var d = q('details.answer-reveal');
      return S.locked && d && !d.open && !d.hasAttribute('data-locked') ? { t: d, a: d, pos: 'before' } : null;
    },
    note: function () {
      var b = q('.wrong-answer-reflection-toggle');
      return b && shown(b) ? { t: b, a: b.parentNode, pos: 'before' } : null;
    },
    close: function () {
      if (S.box.parentNode) return { t: null, a: null, pos: S.box.getAttribute('data-pos') || 'before' };
      var f = q('.free-response-feedback') || D.getElementById('mcq-feedback');
      return f ? { t: null, a: f, pos: 'after' } : null;
    }
  };

  function build() {
    var box = D.createElement('div');
    box.className = 'pb-coach';
    box.hidden = true;
    var face = D.createElement('span');
    face.className = 'study-buddy-face pb-coach-zorp';
    face.setAttribute('data-buddy-face', '');
    face.setAttribute('aria-hidden', 'true');
    box.appendChild(face);
    var src = q('[data-guide-face] svg.buddy-mascot') || q('svg.buddy-mascot');
    if (src) {
      var svg = src.cloneNode(true);
      svg.classList.remove('is-zorp-idle');
      face.appendChild(svg);
      var z = Z();
      if (z) {
        z.bind(face);
        z.turn('front', 'r', { el: svg, instant: true });
      }
      S.svg = svg;
    } else {
      face.hidden = true;
    }
    var body = D.createElement('div');
    body.className = 'pb-coach-body';
    S.line = D.createElement('p');
    S.line.className = 'pb-coach-line';
    body.appendChild(S.line);
    var acts = D.createElement('div');
    acts.className = 'pb-coach-actions';
    S.got = D.createElement('button');
    S.got.type = 'button';
    S.got.className = 'btn-link pb-coach-got';
    S.got.textContent = CAT.primary;
    S.skip = D.createElement('button');
    S.skip.type = 'button';
    S.skip.className = 'btn-link pb-coach-skip';
    S.skip.textContent = CAT.skipLabel;
    acts.appendChild(S.got);
    acts.appendChild(S.skip);
    body.appendChild(acts);
    box.appendChild(body);
    S.got.addEventListener('click', next);
    S.skip.addEventListener('click', function () { finish('skip'); });
    return box;
  }

  function untarget() {
    var t = S && S.target;
    if (t && t.classList) t.classList.remove('pb-coach-target');
    if (S) S.target = null;
  }

  function enter(box) {
    var lv = level();
    if (lv === 'off' || !box.animate) return;
    try {
      box.animate(lv === 'full' ? [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }] : [{ opacity: 0 }, { opacity: 1 }],
        { duration: lv === 'full' ? 240 : 160, easing: 'ease-out' });
    } catch (e) {}
  }

  function place(id) {
    var d = TARGET[id]();
    if (!d) return false;
    var step = STEP[id];
    untarget();
    if (d.a) {
      var host = d.a.parentNode;
      host.insertBefore(S.box, d.pos === 'after' ? d.a.nextSibling : d.a);
    }
    S.box.setAttribute('data-pos', d.pos);
    S.box.setAttribute('data-step', id);
    S.line.textContent = step.lines[0];
    S.got.hidden = id === 'answer' || id === 'pick';
    S.box.hidden = false;
    if (d.t && d.t.classList) {
      d.t.classList.add('pb-coach-target');
      S.target = d.t;
    }
    // polite announcement from a region that exists before the text changes; focus stays where the pupil put it
    S.live.textContent = '';
    window.setTimeout(function () { if (S && S.live) S.live.textContent = step.lines[0]; }, 60);
    var z = Z();
    if (z && S.svg) {
      if (z.valenceOf && z.valenceOf(step.face) !== 'negative') z.setExpression(step.face, { el: S.svg });
      if (level() === 'full') z.play(step.clip, { el: S.svg });
    }
    enter(S.box);
    // keep the callout and what it points at in view: below the sticky header, above the fixed bars. Scrolled by hand:
    // scrollIntoView stops at the card's own scroll boxes.
    var hi = d.pos === 'before' ? S.box : (d.t || S.box), lo = d.pos === 'before' ? (d.t || S.box) : S.box;
    var edge = bounds();
    var over = lo.getBoundingClientRect().bottom - edge[1];
    var room = hi.getBoundingClientRect().top - edge[0];
    if (over > 0) window.scrollBy(0, Math.min(over, Math.max(room, 0)));
    else if (room < 0) window.scrollBy(0, room);
    S.cur = id;
    window.clearTimeout(S.auto);
    S.auto = 0;
    if (id !== 'answer' && id !== 'pick') S.auto = window.setTimeout(next, AUTO_MS[id] || 20000);
    return true;
  }

  function wait(id) {
    if (id === 'hint') return S.willHint ? 4000 : 0;
    if (id === 'note') return S.signedIn ? 2500 : 0;
    return 0;
  }

  function run() {
    if (!S) return;
    window.clearTimeout(S.timer);
    var id = S.order[S.i];
    if (!id) { finish('done'); return; }
    if (blocked()) {
      S.settle = Date.now() + 900;
      S.timer = window.setTimeout(run, 300);
      return;
    }
    if (id === 'close' && Date.now() < S.settle) {
      S.timer = window.setTimeout(run, 250);
      return;
    }
    if (place(id)) { S.since = 0; return; }
    S.since = S.since || Date.now();
    if (Date.now() - S.since < wait(id)) {
      S.timer = window.setTimeout(run, 250);
      return;
    }
    S.since = 0;
    S.i += 1;
    run();
  }

  function hideBox() {
    window.clearTimeout(S.auto);
    S.auto = 0;
    S.cur = '';
    S.box.hidden = true;
    untarget();
  }

  function next() {
    if (!S) return;
    hideBox();
    S.i += 1;
    run();
  }

  function onChecked(e) {
    if (!S) return;
    if (e.detail && e.detail.correct) {
      if (S.cur === 'close' && S.right) return;
      // the first-correct moment (an overlay) plays by itself; the closing tip waits until it is gone
      S.right = true;
      S.settle = Date.now() + 1500;
      hideBox();
      S.order = ['close'];
      S.i = 0;
      run();
      return;
    }
    if (S.checked) return;
    S.checked = true;
    hideBox();
    S.order = CAT.wrong.slice();
    S.i = 0;
    S.since = 0;
    run();
  }

  function nudge() {
    if (S && S.checked && !S.cur) {
      window.clearTimeout(S.timer);
      S.timer = window.setTimeout(run, 0);
    }
  }

  function onBigger() { if (S && (S.cur === 'hint' || S.cur === 'bigger')) next(); }
  function onToggle(e) { if (S && S.cur === 'reveal' && e.target && e.target.open && e.target.matches && e.target.matches('details.answer-reveal')) next(); }
  function onClick(e) { if (S && S.cur === 'note' && e.target.closest && e.target.closest('.wrong-answer-reflection-toggle')) next(); }
  function onKey(e) { if (S && e.key === 'Escape' && !blocked()) finish('skip'); }
  function onLeave() { finish('leave'); }

  var EVENTS = [['pb-answer-checked', onChecked], ['pb-hint-bigger', onBigger], ['pb-hint-shown', nudge], ['pb-answer-unlocked', nudge]];

  function finish(how) {
    if (!S) return;
    var s = S;
    window.clearTimeout(s.timer);
    window.clearTimeout(s.auto);
    untarget();
    EVENTS.forEach(function (p) { D.removeEventListener(p[0], p[1]); });
    D.removeEventListener('toggle', onToggle, true);
    D.removeEventListener('click', onClick);
    D.removeEventListener('keydown', onKey);
    window.removeEventListener('pagehide', onLeave);
    if (s.box.parentNode) s.box.parentNode.removeChild(s.box);
    if (s.live.parentNode) s.live.parentNode.removeChild(s.live);
    D.body.classList.remove('pb-coach-on');
    S = null;
    D.dispatchEvent(new CustomEvent('pb-coach-ended', { detail: { how: how } }));
  }

  // true when there is a question to coach; false leaves the page as it was
  function start() {
    if (S) return true;
    var mode = D.getElementById('mcq-options') ? 'pick' : (q('.free-response-inline') ? 'answer' : '');
    if (!mode) return false;
    var wrapper = q('.site-wrapper');
    S = {
      order: [mode], i: 0, timer: 0, auto: 0, since: 0, settle: 0, cur: '', checked: false, right: false, svg: null,
      locked: !!q('details.answer-reveal[data-locked]'),
      willHint: !!(q('.free-response-hint') || q('#mcq-options[data-note-qid]')),
      signedIn: !!(wrapper && wrapper.getAttribute('data-user-logged-in') === '1')
    };
    S.live = D.createElement('div');
    S.live.className = 'pb-coach-live';
    S.live.setAttribute('aria-live', 'polite');
    D.body.appendChild(S.live);
    S.box = build();
    D.body.classList.add('pb-coach-on');
    EVENTS.forEach(function (p) { D.addEventListener(p[0], p[1]); });
    D.addEventListener('toggle', onToggle, true);
    D.addEventListener('click', onClick);
    D.addEventListener('keydown', onKey);
    window.addEventListener('pagehide', onLeave);
    run();
    return true;
  }

  window.pbCoach = { start: start, end: function () { finish('skip'); }, active: function () { return !!S; }, steps: STEP };
})();
