/* Moments (E10 phase 5, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md B1, B4, 11.8). Loaded on demand by guide.js (pbGuide.moments) with
   moments.css, only when one is due. Three sizes:
   stage  (full screen, on the phase 1 stage): a level-up (the level ring fills and rolls over), a perfect lesson quiz, a finished
          lesson (full the first time, a smaller scene after that);
   toast  (a corner card with a mini Zorp, in the app toast host): a finished quiz, personal best, Quick Test, a full week of the
          Daily question, retry wrong cleared, set work done, a challenge, a streak skip used;
   micro  (small): "Got there with a hint.", the real "+N XP", Zorp's small cheer for a right Daily answer.
   Order: stages first, one stage at a time (perfect, lesson, level), then toasts, then micro. A badge stage (badge-stage.js) always
   plays before this file runs; a perfect quiz that earned a topic ninja or master badge never arrives here (app.py).
   Motion: full plays everything; reduced shows the final frame with the stage's fade; off shows it with no fade. Transform and
   opacity only, DOM nodes only (props cloned from static/images/badge-props.svg). Copy (UI), faces (FACES) and choreography
   (SCENES) are data: the voice lint and scripts/test_celebration_moments_smoke.py read them. */
(function () {
  'use strict';
  if (window.pbMoments) return;
  var D = document;
  var EASE = 'cubic-bezier(.2,.7,.3,1)';
  var SVGNS = 'http://www.w3.org/2000/svg';
  // BEGIN COPY
  var UI = {
    primary: 'Continue',
    profile: 'See my profile',
    quiz: 'Try the quiz',
    retry: 'Retry wrong ones',
    levelHead: 'Level up',
    levelCap: 'Level',
    levelLine: 'Level {n}. Your effort points keep adding up.',
    perfectHead: 'Full marks',
    perfectLine: '{score} out of {total}. Every answer was right.',
    lessonHead: 'Lesson complete',
    lessonFirst: 'Every quick check in this lesson is done. Well done.',
    lessonMore: 'That is another lesson done.',
    lessonBadge: 'New badge: {title}.',
    hint: 'Got there with a hint.',
    quizMore: '{score} out of {total}. Retry the {wrong} you missed?',
    quizOne: '{score} out of {total}. Retry the one you missed?',
    quizPlain: '{score} out of {total}.',
    best: 'Your best so far on this topic: {score} out of {total}.',
    quicktest: 'Quick Test finished. {score} out of {total} marks.',
    week: 'You answered the Daily question on all seven days this week.',
    fixed: 'All fixed.',
    setwork: 'Every question in this set work is answered.',
    challenge: 'Your answers are in. {score} out of {total}.',
    skip: 'Your weekly skip kept your streak going.',
    // E11 Phase 1 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 2.2 to 2.4)
    skipAll: 'Skip all',
    seeIt: 'See it',
    settings: 'Settings',
    firstCorrect: 'Your first right answer. Nice work.',
    badgeCard: 'New badge: {title}.',
    streakCard: '{days} days in a row. New badge.',
    levelCard: 'Level {level}. Your effort points keep adding up.',
    perfectCard: 'Full marks. {score} out of {total}, every answer right.',
    lessonCard: 'Lesson complete. Every quick check is done.',
    lessonCardBadge: 'Lesson complete. New badge: {title}.',
    badgesCard: '{count} new badges: {title}.',
    and: ' and ',
    back: 'You’re back. Your streak starts again today.',
    backKept: 'You’re back. Good to see you again.',
    backfillOne: 'You already earned a badge: {title}. It is on your profile.',
    backfillMany: 'You already earned {count} new badges. They are on your profile.',
    perfectSmall: 'Show these as a small card',
    perfectSet: 'Full marks will show as a small card now. You can change it in Settings.'
  };
  // END COPY
  // BEGIN FACES
  var FACES = {
    quiz_done: 'soft-smile', personal_best: 'proud', quicktest_done: 'soft-smile', daily_week: 'joy', retry_cleared: 'happy',
    set_work_done: 'proud', challenge_done: 'happy', streak_skip: 'soft-smile', hint: 'happy',
    first_correct: 'happy', badge_card: 'proud', badges_card: 'proud', streak_card: 'proud', level_card: 'proud', perfect_card: 'joy', lesson_card: 'happy',
    welcome_back: 'happy', welcome_back_kept: 'happy', backfill: 'proud', perfect_set: 'soft-smile'
  };
  // END FACES
  // BEGIN SCENES
  var SCENES = {
    level: { face: 'determined', end: 'proud', beats: [{ wait: 1900 }, { burst: 1 }, { play: 'flex' }, { play: 'fist-pump' }] },
    perfect: { face: 'joy', end: 'grin', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'victory' }, { play: 'dance' }] },
    lessonFirst: { face: 'happy', end: 'proud', beats: [{ burst: 1 }, { wait: 1700 }, { play: 'cheer' }] },
    lessonMore: { face: 'happy', end: 'happy', beats: [{ wait: 1100 }, { play: 'cheer' }] }
  };
  // END SCENES
  var TOAST_MS = 9000;
  var cur = null;       // what the open scene added: { layer, anims, timers }
  var props = null;
  var propsP = null;
  var go = '';          // where the second button goes
  var toasts = [];

  function Z() { return window.pbZorp || null; }
  function G() { return window.pbGuide || null; }
  function level() {
    var z = Z();
    if (z && z.motionLevel) return z.motionLevel();
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduced' : 'full';
  }
  function full() { return level() === 'full'; }
  function el(tag, cls, parent) {
    var n = D.createElement(tag);
    if (cls) n.className = cls;
    if (parent) parent.appendChild(n);
    return n;
  }
  function fill(tpl, m) {
    return String(tpl).replace(/\{(\w+)\}/g, function (all, k) { return m && m[k] != null ? m[k] : all; });
  }
  function assets() {
    try { return JSON.parse((D.getElementById('pb-moment-assets') || {}).textContent || '{}') || {}; } catch (e) { return {}; }
  }
  function seenKey(id) { return 'pb-mm:' + id; }
  function once(id) {   // toasts and micro: never twice in a browser session
    try {
      if (window.sessionStorage.getItem(seenKey(id))) return false;
      window.sessionStorage.setItem(seenKey(id), '1');
    } catch (e) { /* no storage: the server already sends each moment once */ }
    return true;
  }
  function ready() {
    if (!propsP) {
      var url = assets().props;
      propsP = (url && window.fetch && window.DOMParser ? fetch(url, { credentials: 'same-origin' }).then(function (r) {
        return r.ok ? r.text() : '';
      }).then(function (text) {
        var doc = text ? new window.DOMParser().parseFromString(text, 'image/svg+xml') : null;
        if (doc && !doc.getElementsByTagName('parsererror').length) props = doc;
      }) : Promise.resolve()).catch(function () { /* the scene still shows */ });
    }
    return propsP;
  }
  function part(id) {
    var src = id && props && props.querySelector('[id="' + id + '"]');
    if (!src) return null;
    var n = D.importNode(src, true);
    n.removeAttribute('id');
    n.setAttribute('aria-hidden', 'true');
    n.setAttribute('focusable', 'false');
    return n;
  }
  function svgEl(tag, attrs, parent) {
    var n = D.createElementNS(SVGNS, tag);
    for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function all(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }
  function anim(node, frames, ms, o) {
    if (!node || !node.animate || !cur) return null;
    o = o || {};
    o.duration = ms;
    o.easing = o.easing || EASE;
    o.fill = o.fill || 'both';
    try { var a = node.animate(frames, o); cur.anims.push(a); return a; } catch (e) { return null; }
  }
  function later(fn, ms) {
    if (!cur) return;
    var mine = cur;
    mine.timers.push(setTimeout(function () { if (cur === mine) fn(); }, ms));
  }
  function clear() {
    if (!cur) return;
    cur.timers.forEach(clearTimeout);
    cur.anims.forEach(function (a) { try { a.cancel(); } catch (e) { /* gone */ } });
    if (cur.layer.parentNode) cur.layer.parentNode.removeChild(cur.layer);
    cur = null;
  }

  // ---- the level ring: two half rings turned by transform alone (the right half fills first, then the left) ----
  function turns(p) {
    var r = 360 * p - 135;
    return [Math.min(r, 45), Math.max(r, 45)];
  }
  function rot(d) { return 'rotate(' + d + 'deg)'; }
  function ringSet(rg, p) {
    var t = turns(p);
    rg.arcs[0].style.transform = rot(t[0]);
    rg.arcs[1].style.transform = rot(t[1]);
    rg.arcs[0].style.opacity = p > 0.004 ? '' : '0';   // an empty half leaves no sliver where it meets the clip
    rg.arcs[1].style.opacity = p > 0.504 ? '' : '0';
  }
  function ringFill(rg, from, to, ms, delay) {
    var span = to - from;
    if (span <= 0) { ringSet(rg, to); return; }
    var a = turns(from);
    var b = turns(to);
    var segR = Math.max(0, Math.min(to, 0.5) - Math.min(from, 0.5));
    var segL = Math.max(0, Math.max(to, 0.5) - Math.max(from, 0.5));
    var tR = ms * segR / span;
    var tL = ms * segL / span;
    if (tR > 0) rg.arcs[0].style.opacity = '';
    if (tL > 0) rg.arcs[1].style.opacity = '';
    if (tR > 0) anim(rg.arcs[0], [{ transform: rot(a[0]) }, { transform: rot(b[0]) }], tR, { delay: delay, easing: 'linear', fill: 'forwards' });
    if (tL > 0) anim(rg.arcs[1], [{ transform: rot(a[1]) }, { transform: rot(b[1]) }], tL, { delay: delay + tR, easing: 'linear', fill: 'forwards' });
  }

  function levelBox(box, m) {
    var n = parseInt(m.level, 10) || 1;
    var pct = Math.max(0, Math.min(1, parseFloat(m.pct) || 0));
    var wrap = el('div', 'mo-ring-wrap', box);
    var ring = el('div', 'mo-ring', wrap);
    el('div', 'mo-track', ring);
    var halves = [el('div', 'mo-half mo-half--r', ring), el('div', 'mo-half mo-half--l', ring)];
    var rg = { arcs: halves.map(function (h) { return el('div', 'mo-arc', h); }) };
    var inner = el('div', 'mo-ring-inner', ring);
    el('span', 'mo-cap', inner).textContent = UI.levelCap;
    var nums = el('div', 'mo-nums', inner);
    var oldN = el('span', 'mo-n', nums);
    var newN = el('span', 'mo-n', nums);
    oldN.textContent = String(Math.max(1, n - 1));
    newN.textContent = String(n);
    if (!full()) {
      oldN.hidden = true;
      ringSet(rg, pct);
      return;
    }
    newN.style.opacity = '0';
    ringSet(rg, 0.86);
    anim(wrap, [{ transform: 'scale(.85)', opacity: 0 }, { transform: 'none', opacity: 1 }], 600, { delay: 250 });
    ringFill(rg, 0.86, 1, 1000, 900);
    later(function () {
      anim(ring, [{ transform: 'scale(1)' }, { transform: 'scale(1.09)', offset: 0.4 }, { transform: 'scale(1)' }], 600, { fill: 'none' });
      anim(oldN, [{ transform: 'none', opacity: 1 }, { transform: 'translateY(-70%)', opacity: 0 }], 450, { fill: 'forwards' });
      anim(newN, [{ transform: 'translateY(70%)', opacity: 0 }, { transform: 'none', opacity: 1 }], 450, { fill: 'forwards' });
      // the old fill is replaced by an empty ring that fills to the new level's share
      cur.anims.filter(function (a) { return a.effect && a.effect.target && rg.arcs.indexOf(a.effect.target) >= 0; }).forEach(function (a) { a.cancel(); });
      ringSet(rg, 0);
      ringFill(rg, 0, pct, 1100, 250);
    }, 2000);
  }

  // ---- a score seal with stars (a perfect quiz) ----
  function sealBox(box, m) {
    var art = part('bp-stars');
    if (art) box.appendChild(art);
    var ring = part('bp-ring');
    if (ring) { ring.style.opacity = '0'; box.appendChild(ring); }
    var wrap = el('div', 'mo-seal-wrap', box);
    var seal = el('div', 'mo-seal', wrap);
    el('span', 'mo-seal-text', seal).textContent = m.score + '/' + m.total;
    if (!full()) return;
    all(box, '.bp-star').forEach(function (s, i) {
      anim(s, [{ transform: 'scale(0) rotate(-40deg)', opacity: 0 }, { transform: 'scale(1.3) rotate(8deg)', opacity: 1, offset: 0.6 }, { transform: 'none', opacity: 1 }], 600, { delay: 900 + i * 170 });
      anim(s, [{ opacity: 1 }, { opacity: 0.45 }, { opacity: 1 }], 1400, { delay: 2200 + i * 230, iterations: 3, fill: 'none', easing: 'ease-in-out' });
    });
    anim(seal, [{ transform: 'translateY(-170%) scale(1.5)', opacity: 0 }, { transform: 'translateY(0) scale(1)', opacity: 1, offset: 0.7 },
      { transform: 'scale(.93,1.07)', opacity: 1, offset: 0.8 }, { transform: 'scale(1.05,.95)', opacity: 1, offset: 0.9 }, { transform: 'none', opacity: 1 }], 1000, { delay: 350, easing: 'cubic-bezier(.4,0,.6,1)' });
    if (ring) anim(ring, [{ opacity: 0, transform: 'scale(.6)' }, { opacity: 1, transform: 'scale(1)', offset: 0.4 }, { opacity: 0, transform: 'scale(1.3)' }], 900, { delay: 1250, fill: 'forwards' });
  }

  // ---- a book that closes, with a tick (a finished lesson) ----
  function bookBox(box, first) {
    var open = part('bp-book');
    var closed = svgEl('svg', { viewBox: '0 0 240 180', 'aria-hidden': 'true', focusable: 'false' }, box);
    svgEl('rect', { x: 62, y: 28, width: 116, height: 132, rx: 10, fill: '#4f46e5' }, closed);
    svgEl('rect', { x: 62, y: 28, width: 14, height: 132, rx: 6, fill: '#3730a3' }, closed);
    svgEl('rect', { x: 92, y: 52, width: 62, height: 8, rx: 4, fill: '#c7d2fe' }, closed);
    svgEl('rect', { x: 92, y: 70, width: 44, height: 8, rx: 4, fill: '#c7d2fe' }, closed);
    var tick = svgEl('g', { class: 'mo-tick' }, closed);
    svgEl('circle', { cx: 150, cy: 128, r: 24, fill: '#22c55e' }, tick);
    svgEl('path', { d: 'M138 128l8 8 16-17', fill: 'none', stroke: '#fff', 'stroke-width': 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, tick);
    if (open) { open.setAttribute('class', 'mo-open'); box.insertBefore(open, closed); }
    if (!full()) { if (open) open.style.opacity = '0'; return; }
    var k = first ? 1 : 0.55;
    anim(open, [{ transform: 'translateY(24px) scale(.92)', opacity: 0 }, { transform: 'none', opacity: 1 }], 600, { delay: 200 * k });
    anim(open, [{ transform: 'none', opacity: 1 }, { transform: 'scaleX(.1)', opacity: 0 }], 450, { delay: 1300 * k, fill: 'forwards' });
    anim(closed, [{ transform: 'scale(1.15)', opacity: 0 }, { transform: 'none', opacity: 1 }], 450, { delay: 1300 * k });
    anim(tick, [{ transform: 'scale(0)', opacity: 0 }, { transform: 'scale(1.3)', opacity: 1, offset: 0.6 }, { transform: 'none', opacity: 1 }], 550, { delay: 1750 * k });
    if (first) rain();
  }

  function rain() {
    var layer = cur.layer;
    var h = layer.getBoundingClientRect().height || 500;
    var colours = ['#fde047', '#f472b6', '#60a5fa', '#34d399', '#fb923c'];
    for (var i = 0; i < 18; i += 1) {
      var bit = el('div', 'mo-conf', layer);
      var s = part('bp-conf');
      if (s) { s.firstElementChild.setAttribute('fill', colours[i % colours.length]); bit.appendChild(s); }
      bit.style.left = (4 + (i * 5.3) % 92) + '%';
      anim(bit, [{ transform: 'translateY(0) rotate(0deg)', opacity: 0 }, { opacity: 1, offset: 0.1 }, { transform: 'translateY(' + h + 'px) rotate(' + (260 + i * 40) + 'deg)', opacity: 1 }], 2400 + (i % 5) * 300, { delay: 1900 + (i % 6) * 230, fill: 'none', easing: 'linear' });
    }
  }

  function enter(m, set) {
    clear();
    var layer = el('div', 'mo-layer', set);
    cur = { layer: layer, anims: [], timers: [] };
    var box = el('div', 'mo-box', layer);
    if (m.type === 'level') levelBox(box, m);
    else if (m.type === 'perfect') sealBox(box, m);
    else bookBox(box, !m.more);
  }

  // ---- moments -> scenes ----
  function sceneFor(m) {
    var key = m.type === 'level' ? 'level' : (m.type === 'perfect' ? 'perfect' : (m.more ? 'lessonMore' : 'lessonFirst'));
    var def = SCENES[key];
    var out = { id: 'moment.' + key, props: [], layout: 'moment', face: def.face, end: def.end, beats: [def.beats], primary: UI.primary, skipLabel: '' };
    if (m.type === 'level') {
      out.heading = UI.levelHead;
      out.lines = [fill(UI.levelLine, { n: m.level })];
      out.skipLabel = UI.profile;
      out.go = assets().profile || '';
    } else if (m.type === 'perfect') {
      out.heading = UI.perfectHead;
      out.lines = [fill(UI.perfectLine, m)];
    } else {
      out.heading = UI.lessonHead;
      // E11 Phase 0: the lesson's own badge, earned by the same save, is named here instead of on a second stage (guide.js)
      var badgeTitle = m.badge && m.badge.title ? String(m.badge.title).slice(0, 80) : '';
      out.lines = [(m.more ? UI.lessonMore : UI.lessonFirst) + (badgeTitle ? '\n' + fill(UI.lessonBadge, { title: badgeTitle }) : '')];
      if (m.quiz) { out.skipLabel = UI.quiz; out.go = m.quiz; }
    }
    return out;
  }

  // ---- E11 Phase 1: how big celebrations are (David's answers 1, 5 and 11; the settings live on <body>) ----
  var MAX_CARDS = 3;      // one sequence holds at most this many cards; the rest wait for the next page
  var BUDGET = 6;         // full-screen finished lessons a day; then corner cards (10/10s, badges and level-ups never count)
  var TIER = { violet: 0, gold: 1, silver: 2, bronze: 3 };
  function mode() {
    var v = D.body && D.body.getAttribute('data-pb-celebrate');
    return v === 'big' || v === 'small' ? v : 'full';
  }
  function perfectAsCard() { return !!D.body && D.body.getAttribute('data-pb-perfect-card') === '1'; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function today() { var d = new Date(); return '' + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()); }
  function budgetUsed() {
    var g = G();
    var n = 0;
    for (var i = 1; g && i <= BUDGET; i += 1) if (g.rewardSeen('fs:' + today() + ':' + i)) n = i;
    return n;
  }
  function spend() {
    var g = G();
    var n = budgetUsed();
    if (g && g.markReward && n < BUDGET) g.markReward('fs:' + today() + ':' + (n + 1));
  }
  function storeNs() {
    var m = D.querySelector('meta[name="pb-store"]');
    return (m && m.getAttribute('content')) || 'anon';
  }
  var CARRY = 'pb-celebrate-next:';
  // cards past MAX_CARDS wait for the next page (guide.js picks them up); this tab only, this pupil only
  function carry(moments, badges) {
    if (!moments.length && !badges.length) return;
    try {
      var key = CARRY + storeNs();
      var old = JSON.parse(window.sessionStorage.getItem(key) || 'null') || { m: [], b: [] };
      window.sessionStorage.setItem(key, JSON.stringify({ m: (old.m || []).concat(moments).slice(-8), b: (old.b || []).concat(badges).slice(-8) }));
    } catch (e) { /* no storage: they show on the profile shelf all the same */ }
  }
  function savePerfectCard() {
    if (D.body) D.body.setAttribute('data-pb-perfect-card', '1');
    var t = D.querySelector('meta[name="csrf-token"]');
    try {
      fetch('/api/v1/me/settings', {
        method: 'PATCH', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json', 'X-CSRF-Token': t ? t.getAttribute('content') : '' },
        body: JSON.stringify({ perfect_as_card: true })
      }).catch(function () { /* the next 10/10 asks again */ });
    } catch (e) { /* no fetch */ }
  }
  function perfectLink(st) {
    var panel = st.querySelector('.pb-st-panel');
    if (!panel || panel.querySelector('.mo-cardlink')) return;
    var b = el('button', 'mo-cardlink', panel);
    b.type = 'button';
    b.textContent = UI.perfectSmall;
    b.addEventListener('click', function () {
      b.disabled = true;
      savePerfectCard();
      if (window.pbStage) window.pbStage.close();
      setTimeout(function () { toast({ type: 'toast', id: 'toast:perfect_set:' + today(), kind: 'perfect_set' }); }, 450);
    });
  }

  function mark(m) {
    var g = G();
    if (!g) return;
    if (m.type === 'level' && g.markReward) g.markReward('level:' + m.level);
    if (m.type === 'lesson_complete' && g.markReward) {
      g.markReward(g.rewardId(m));
      g.markReward('lesson_complete');
      if (m.badge && m.badge.key) g.markReward('milestone:' + String(m.badge.key).replace(/\s+/g, '_'));
    }
    if (m.type === 'perfect') once(m.id);
  }

  // E11 Phase 1 (plan 2.4 rule 1): one full-screen sequence per page, in a fixed order (the scene, the badges, the level-up), with one
  // count and "Skip all". The badge cards come from badge-stage.js (pbBadgeStage.part); each card's things come off the stage when
  // the next card belongs to the other module. The second button (Try the quiz, See my milestones, See my profile) is followed for
  // the card it was pressed on.
  function sequence(front, badgeSpecs, back) {
    var g = G();
    var bs = badgeSpecs.length && window.pbBadgeStage && window.pbBadgeStage.part ? window.pbBadgeStage.part(badgeSpecs) : null;
    var items = [];
    var momentItem = function (m) {
      var sc = sceneFor(m);
      return {
        scene: sc, owner: 'm',
        show: function (st) {
          mark(m);
          if (m.type === 'lesson_complete') spend();
          enter(m, st.querySelector('.pb-st-set'));
          if (m.type === 'perfect') perfectLink(st);
        },
        hide: function (st) {
          clear();
          var l = st && st.querySelector('.mo-cardlink');
          if (l && l.parentNode) l.parentNode.removeChild(l);
        },
        markAll: function () { mark(m); },
        go: function () {
          if (!sc.go) return;
          var a = D.createElement('a');
          a.href = sc.go;
          if (a.pathname === location.pathname && a.hash) location.hash = a.hash;
          else location.assign(sc.go);
        }
      };
    };
    front.forEach(function (m) { items.push(momentItem(m)); });
    if (bs) bs.cards.forEach(function (c, j) {
      items.push({ scene: bs.scenes[j], owner: 'b', show: function (st) { bs.show(j, st); }, hide: bs.hide, markAll: bs.markAll, go: bs.go });
    });
    back.forEach(function (m) { items.push(momentItem(m)); });
    if (!items.length) return Promise.resolve();
    var at = -1;
    var chosen = null;
    var count = null;
    return g.loadStage().then(function () {
      return Promise.all([ready(), bs ? window.pbBadgeStage.ready() : null]);
    }).then(function () {
      return window.pbStage.play(items.map(function (it) { return it.scene; }), {
        onScene: function (i) {
          var st = D.querySelector('.pb-stage');
          if (!st) return;
          if (!count) {
            var top = st.querySelector('.pb-st-top');
            count = el('span', 'mo-count', top);
            var skip = st.querySelector('.pb-st-actions .btn-outline');
            if (skip) skip.addEventListener('click', function () { chosen = items[at]; }, true);
            if (items.length > 1) {
              var all = el('button', 'mo-skipall', top);
              all.type = 'button';
              all.textContent = UI.skipAll;
              all.addEventListener('click', function () {
                items.forEach(function (it) { it.markAll(); });
                window.pbStage.close();
              });
            }
          }
          if (at >= 0 && items[at] && items[at].owner !== items[i].owner) items[at].hide(st);
          at = i;
          count.textContent = items.length > 1 ? (i + 1) + ' of ' + items.length : '';
          items[i].show(st);
        }
      });
    }).then(function (res) {
      clear();
      if (bs) bs.end();
      if (res && res.ended === 'skip' && chosen) {
        chosen.markAll();
        chosen.go();
      }
      return res;
    }, function (err) { clear(); if (bs) bs.end(); throw err; });
  }

  // a stage shown as a corner card instead (the setting, the 10/10 link or the day's budget): marked seen like the stage
  function asCard(m) {
    mark(m);
    var t = { type: 'toast', id: 'card:' + (m.id || m.type + ':' + (m.level || m.topic || '')), score: m.score, total: m.total, level: m.level };
    if (m.type === 'level') t.kind = 'level_card';
    else if (m.type === 'perfect') t.kind = 'perfect_card';
    else { t.kind = 'lesson_card'; t.quiz = m.quiz || ''; t.title = m.badge && m.badge.title ? String(m.badge.title).slice(0, 80) : ''; }
    return t;
  }
  function badgeCard(spec) {
    var g = G();
    var b = spec.badge || {};
    if (spec.type === 'streak') {
      if (g && g.markReward) g.markReward('streak:' + spec.days);
      return { type: 'toast', id: 'card:streak:' + spec.days, kind: 'streak_card', days: spec.days };
    }
    var key = String(spec.key || b.key || '');
    if (g && g.markReward) {
      g.markReward('milestone:' + key);
      if (key === 'streak_7') g.markReward('streak:7');
      if (key === 'streak_30') g.markReward('streak:30');
      if (key === 'streak_100') g.markReward('streak:100');
    }
    var title = b.title;
    if (!title) {
      try { title = ((JSON.parse((D.getElementById('pb-milestone-catalog') || {}).textContent || '{}') || {})[key] || {}).title; } catch (e) { title = ''; }
    }
    return { type: 'toast', id: 'card:milestone:' + key.slice(0, 50), kind: 'badge_card', title: title || key };
  }
  function tierOf(spec) { return spec.type === 'streak' ? TIER.gold : (TIER[(spec.badge || {}).tier] != null ? TIER[(spec.badge || {}).tier] : TIER.bronze); }

  // ---- toasts: the app toast host (polite live region) with a mini Zorp; never takes focus ----
  function miniZorp(parent, face) {
    var holder = el('span', 'pb-mt-zorp study-buddy-face', parent);
    holder.setAttribute('data-buddy-face', '');
    holder.setAttribute('aria-hidden', 'true');
    var src = D.querySelector('[data-guide-face] svg.buddy-mascot') || D.querySelector('svg.buddy-mascot');
    var z = Z();
    if (!src) { holder.hidden = true; return; }
    var svg = src.cloneNode(true);
    svg.classList.remove('is-zorp-idle');
    holder.appendChild(svg);
    if (z) {
      z.bind(holder);
      z.turn('front', 'r', { el: svg, instant: true });
      if (z.valenceOf && z.valenceOf(face) !== 'negative') z.setExpression(face, { el: svg });
    }
  }
  function textFor(m) {
    var k = m.kind;
    var retry = !!D.getElementById('retry-wrong') && m.wrong > 0;
    if (k === 'quiz_done') return fill(retry ? (m.wrong === 1 ? UI.quizOne : UI.quizMore) : UI.quizPlain, m);
    if (k === 'personal_best') return fill(UI.best, m);
    if (k === 'quicktest_done') return fill(UI.quicktest, m);
    if (k === 'daily_week') return UI.week;
    if (k === 'retry_cleared') return UI.fixed;
    if (k === 'set_work_done') return UI.setwork;
    if (k === 'challenge_done') return fill(UI.challenge, m);
    if (k === 'streak_skip') return UI.skip;
    if (k === 'first_correct') return UI.firstCorrect;
    if (k === 'badge_card') return fill(UI.badgeCard, m);
    if (k === 'streak_card') return fill(UI.streakCard, m);
    if (k === 'level_card') return fill(UI.levelCard, m);
    if (k === 'perfect_card') return fill(UI.perfectCard, m);
    if (k === 'lesson_card') return m.title ? fill(UI.lessonCardBadge, m) : UI.lessonCard;
    if (k === 'badges_card') return fill(UI.badgesCard, m);
    if (k === 'welcome_back') return UI.back;
    if (k === 'welcome_back_kept') return UI.backKept;
    if (k === 'backfill') return m.count > 1 ? fill(UI.backfillMany, m) : (m.title ? fill(UI.backfillOne, m) : fill(UI.backfillMany, m));
    if (k === 'perfect_set') return UI.perfectSet;
    return '';
  }
  // where a card's link goes (E11 Phase 1): a badge to the Milestones shelf, a finished lesson to its quiz, the 10/10 setting to Settings
  function linkFor(m) {
    var a = assets();
    if (m.kind === 'badge_card' || m.kind === 'badges_card' || m.kind === 'streak_card' || m.kind === 'backfill') return a.profile ? { href: a.profile + '#milestones', label: UI.seeIt } : null;
    if (m.kind === 'level_card') return a.profile ? { href: a.profile, label: UI.profile } : null;
    if (m.kind === 'lesson_card' && m.quiz) return { href: m.quiz, label: UI.quiz };
    if (m.kind === 'perfect_set' && a.settings) return { href: a.settings + '#celebrations', label: UI.settings };
    return null;
  }
  function dismiss(t) {
    if (!t || t.gone) return;
    t.gone = true;
    clearTimeout(t.timer);
    t.node.classList.add('is-leaving');
    setTimeout(function () { if (t.node.parentNode) t.node.parentNode.removeChild(t.node); }, full() ? 180 : 0);
    toasts = toasts.filter(function (x) { return x !== t; });
  }
  function onEsc(e) {
    if (e.key !== 'Escape' || !toasts.length || (window.pbStage && window.pbStage.isOpen())) return;
    var a = D.activeElement;
    if (a && a !== D.body && !(a.closest && a.closest('.pb-mtoast'))) return;
    dismiss(toasts[toasts.length - 1]);
  }
  function toast(m) {
    var host = D.getElementById('app-toast-host');
    var text = textFor(m);
    if (!host || !text || !FACES[m.kind] || !once(m.id)) return;
    var node = el('div', 'app-toast is-success pb-mtoast', host);
    node.setAttribute('role', 'status');
    var icon = el('span', 'app-toast-icon', node);
    miniZorp(icon, FACES[m.kind]);
    var body = el('div', 'app-toast-body', node);
    el('p', 'app-toast-message', body).textContent = text;
    var go = linkFor(m);
    if (go) {
      var a = el('a', 'app-toast-action', body);
      a.href = go.href;
      a.textContent = go.label;
    }
    var btn = D.getElementById('retry-wrong');
    if ((m.kind === 'quiz_done' || m.kind === 'personal_best' || m.kind === 'quicktest_done') && btn && m.wrong > 0) {
      var link = el('a', 'app-toast-action', body);
      link.href = '#retry-wrong';
      link.textContent = UI.retry;
      link.addEventListener('click', function (e) {
        e.preventDefault();
        btn.scrollIntoView({ block: 'center', behavior: full() ? 'smooth' : 'auto' });
        btn.focus({ preventScroll: true });
        dismiss(t);
      });
    }
    var x = el('button', 'app-toast-dismiss', node);
    x.type = 'button';
    x.setAttribute('aria-label', 'Dismiss');
    var glyph = svgEl('svg', { class: 'app-toast-glyph', width: 18, height: 18, viewBox: '0 0 24 24', 'aria-hidden': 'true', focusable: 'false' }, x);
    svgEl('path', { d: 'M6 6l12 12M18 6L6 18', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', fill: 'none' }, glyph);
    var t = { node: node, timer: 0, gone: false };
    function arm() { clearTimeout(t.timer); t.timer = setTimeout(function () { dismiss(t); }, TOAST_MS); }
    x.addEventListener('click', function () { dismiss(t); });
    node.addEventListener('mouseenter', function () { clearTimeout(t.timer); });
    node.addEventListener('mouseleave', arm);
    node.addEventListener('focusin', function () { clearTimeout(t.timer); });
    node.addEventListener('focusout', arm);
    toasts.push(t);
    if (toasts.length === 1) D.addEventListener('keydown', onEsc);
    arm();
  }

  // ---- micro ----
  function sparkle(near) {
    if (!full()) return;
    var s = svgEl('svg', { viewBox: '0 0 24 24', class: 'pb-micro-spark', 'aria-hidden': 'true', focusable: 'false' }, near);
    svgEl('path', { d: 'M12 1l2.6 8.4L23 12l-8.4 2.6L12 23l-2.6-8.4L1 12l8.4-2.6z', fill: '#fbbf24' }, s);
    s.animate([{ transform: 'scale(0) rotate(-40deg)', opacity: 0 }, { transform: 'scale(1.2) rotate(10deg)', opacity: 1, offset: 0.5 }, { transform: 'scale(1)', opacity: 0.9 }], { duration: 600, easing: EASE, fill: 'both' });
  }
  function micro(m) {
    if (m.kind === 'xp') {
      if (window.pbCelebrate && window.pbCelebrate.xp && m.points > 0) window.pbCelebrate.xp(m.points);
      return;
    }
    if (m.kind === 'daily') {
      if (!once(m.id)) return;
      var z = Z();
      if (m.correct && z && z.react) { try { z.react('correct', {}); } catch (e) { /* a glitch must not break the page */ } }
      return;
    }
    if (m.kind !== 'hint') return;
    var feedback = D.querySelector('#mcq-feedback.is-correct');
    if (!feedback) {
      var list = all(D, '.free-response-feedback').filter(function (n) { return (n.textContent || '').trim(); });
      feedback = list[list.length - 1];
    }
    if (!feedback || !feedback.parentNode) return;
    var old = feedback.parentNode.querySelector('.pb-micro');
    if (old) old.parentNode.removeChild(old);
    var note = el('p', 'pb-micro');
    note.setAttribute('role', 'status');
    note.textContent = UI.hint;
    feedback.parentNode.insertBefore(note, feedback.nextSibling);
    sparkle(note);
    setTimeout(function () { if (note.parentNode) note.parentNode.removeChild(note); }, 9000);
  }

  // ---- entry: stages first (one stage at a time), then toasts, then micro ----
  function rank(m) { return m.type === 'perfect' ? 0 : (m.type === 'lesson_complete' ? 1 : 2); }
  function wanted(m) {
    var g = G();
    if (m.type === 'level') return !!g && !g.rewardSeen('level:' + m.level);
    if (m.type === 'perfect') { try { return !window.sessionStorage.getItem(seenKey(m.id)); } catch (e) { return true; } }
    if (m.type === 'lesson_complete') {
      m.more = !!g && g.rewardSeen('lesson_complete');
      return !!g && !g.rewardSeen(g.rewardId(m));
    }
    return false;
  }
  // E11 Phase 1: list holds the moments, badges the badge and streak rewards (guide.js hands both over in one beat). The setting,
  // the 10/10 link and the day's budget turn stages into corner cards; the rest is one sequence of at most MAX_CARDS cards.
  function play(list, badges) {
    list = (list || []).filter(function (m) { return m && m.type; });
    badges = (badges || []).filter(function (b) { return b && b.type; });
    var md = mode();
    var stages = list.filter(function (m) { return (m.type === 'level' || m.type === 'perfect' || m.type === 'lesson_complete') && wanted(m); });
    stages = stages.filter(function (m, i) { return stages.findIndex(function (x) { return x.type === m.type && (x.id || x.topic) === (m.id || m.topic); }) === i; });
    stages.sort(function (a, b) { return rank(a) - rank(b); });
    var cards = [];
    var lessons = 0;
    stages = stages.filter(function (m) {
      var small = md === 'small' || (md === 'big' && m.type !== 'level') || (m.type === 'perfect' && perfectAsCard());
      if (!small && m.type === 'lesson_complete') { lessons += 1; small = budgetUsed() + lessons > BUDGET; }
      if (small) cards.push(asCard(m));
      return !small;
    });
    var badgeCards = [];
    if (md === 'small' || !(window.pbBadgeStage && window.pbBadgeStage.part)) {
      badgeCards = badges.map(badgeCard);
      badges = [];
      // several badges in one beat are one card, so a phone is never covered in cards
      if (badgeCards.length > 1) {
        var names = badgeCards.map(function (c) { return c.title || fill(UI.streakCard, c).split('.')[0]; });
        badgeCards = [{ type: 'toast', id: badgeCards.map(function (c) { return c.id; }).join('|').slice(0, 120), kind: 'badges_card', count: names.length,
          title: names.slice(0, -1).join(', ') + UI.and + names[names.length - 1] }];
      }
    }
    badges = badges.map(function (b, i) { return { b: b, i: i }; }).sort(function (x, y) { return (tierOf(x.b) - tierOf(y.b)) || (x.i - y.i); }).map(function (x) { return x.b; });
    var front = stages.filter(function (m) { return m.type !== 'level'; });
    var back = stages.filter(function (m) { return m.type === 'level'; });
    var room = MAX_CARDS;
    var f = front.slice(0, room); room -= f.length;
    var b2 = badges.slice(0, room); room -= b2.length;
    var k = back.slice(0, room);
    carry(front.slice(f.length).concat(back.slice(k.length)), badges.slice(b2.length));
    var rest = list.filter(function (m) { return m.type === 'toast' || m.type === 'micro'; });
    var p = (f.length || b2.length || k.length) ? sequence(f, b2, k).catch(function () { clear(); }) : Promise.resolve();
    return p.then(function () {
      var list2 = cards.concat(badgeCards).concat(rest.filter(function (m) { return m.type === 'toast'; }));
      list2.forEach(function (m, i) { setTimeout(function () { toast(m); }, i * 700); });
      rest.filter(function (m) { return m.type === 'micro'; }).forEach(function (m) { micro(m); });
      // what waits for the moments (a story offer) comes after the last card
      return new Promise(function (done) { setTimeout(done, list2.length ? (list2.length - 1) * 700 + 150 : 0); });
    });
  }

  window.pbMoments = { play: play, sequence: sequence, toast: toast, scenes: SCENES, faces: FACES };
}());
