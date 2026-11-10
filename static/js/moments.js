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
    skip: 'Your weekly skip kept your streak going.'
  };
  // END COPY
  // BEGIN FACES
  var FACES = {
    quiz_done: 'soft-smile', personal_best: 'proud', quicktest_done: 'soft-smile', daily_week: 'joy', retry_cleared: 'happy',
    set_work_done: 'proud', challenge_done: 'happy', streak_skip: 'soft-smile', hint: 'happy'
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

  function playStages(list) {
    var g = G();
    var scenes = list.map(sceneFor);
    go = '';
    return g.loadStage().then(ready).then(function () {
      var decorated = null;
      return window.pbStage.play(scenes, {
        onScene: function (i) {
          var st = D.querySelector('.pb-stage');
          if (!st) return;
          if (!decorated) {
            decorated = el('span', 'mo-count');
            st.querySelector('.pb-st-top').appendChild(decorated);
            var skip = st.querySelector('.pb-st-actions .btn-outline');
            if (skip) skip.addEventListener('click', function () { go = (decorated.go || ''); }, true);
          }
          decorated.textContent = list.length > 1 ? (i + 1) + ' of ' + list.length : '';
          decorated.go = scenes[i].go;
          mark(list[i]);
          enter(list[i], st.querySelector('.pb-st-set'));
        }
      });
    }).then(function (res) {
      clear();
      if (res && res.ended === 'skip' && go) {
        var a = D.createElement('a');
        a.href = go;
        if (a.pathname === location.pathname && a.hash) location.hash = a.hash;
        else location.assign(go);
      }
      return res;
    });
  }

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
    return '';
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
  function play(list) {
    list = (list || []).filter(function (m) { return m && m.type; });
    var stages = list.filter(function (m) { return (m.type === 'level' || m.type === 'perfect' || m.type === 'lesson_complete') && wanted(m); });
    stages = stages.filter(function (m, i) { return stages.findIndex(function (x) { return x.type === m.type && (x.id || x.topic) === (m.id || m.topic); }) === i; });
    stages.sort(function (a, b) { return rank(a) - rank(b); });
    var rest = list.filter(function (m) { return m.type === 'toast' || m.type === 'micro'; });
    var p = stages.length ? playStages(stages).catch(function () { clear(); }) : Promise.resolve();
    return p.then(function () {
      rest.filter(function (m) { return m.type === 'toast'; }).forEach(function (m, i) { setTimeout(function () { toast(m); }, i * 700); });
      rest.filter(function (m) { return m.type === 'micro'; }).forEach(function (m) { micro(m); });
    });
  }

  window.pbMoments = { play: play, toast: toast, scenes: SCENES, faces: FACES };
}());
