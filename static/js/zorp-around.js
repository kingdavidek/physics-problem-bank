/* Zorp around the site (E10 phase 7, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md Part C). Loaded on demand, only by the pages that use it:
   lesson pages with the AI helper (the thinking Zorp), quiz and Quick Test results (the ring counts up, a small Zorp shows a face by
   score band), the profile (the level ring fills once per visit) and the practice page (Zorp's eyes follow the focused option or the
   hint). No library, no markup from data, nothing inline. The runtime is optional: without window.pbZorp the ring still counts up and
   the kind lines are plain text. Faces here are always positive or neutral (models/zorp_rig.py CONTEXT_MAP['around.results']).
   Cap 6,000 B in scripts/test_zorp_around_smoke.py. */
(function () {
  'use strict';
  var D = document;
  var W = window;
  if (W.pbAround) return;

  var FACES = { joy: 1, determined: 1, 'soft-smile': 1, nudge: 1 };

  function Z() { return W.pbZorp && typeof W.pbZorp.play === 'function' ? W.pbZorp : null; }
  function level() {
    var z = Z();
    if (z && z.motionLevel) return z.motionLevel();
    var m = D.documentElement.getAttribute('data-motion') || 'system';
    if (m === 'reduced' || m === 'off') return m;
    return W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduced' : 'full';
  }
  function full() { return level() === 'full'; }

  // A small Zorp for a host span: the page's own rig, cloned (nothing extra in the page), facing front.
  function rig(host) {
    var src = D.querySelector('[data-guide-face] svg.buddy-mascot') || D.querySelector('svg.buddy-mascot');
    if (!src) return null;
    var svg = src.cloneNode(true);
    svg.classList.remove('is-zorp-idle');
    host.appendChild(svg);
    var z = Z();
    if (z) {
      z.bind(host);
      z.turn('front', 'r', { el: svg, instant: true });
    }
    return svg;
  }

  // ---- results: the face by score band ----
  function faces() {
    var hosts = D.querySelectorAll('[data-around-face]');
    var i;
    for (i = 0; i < hosts.length; i += 1) {
      var face = hosts[i].getAttribute('data-around-face');
      var svg = FACES[face] === 1 ? rig(hosts[i]) : null;
      if (!svg) { hosts[i].hidden = true; continue; }
      var z = Z();
      if (z && z.hasExpression(face) && z.valenceOf(face) !== 'negative') z.setExpression(face, { el: svg });
      if (z && face === 'joy' && full()) {
        (function (s) { W.setTimeout(function () { z.play('hop', { el: s }); }, 1100); }(svg));
      }
    }
  }

  // ---- results: the score ring counts up once (the ring's fill is the --quiz-pct custom property) ----
  function ring(el) {
    var pct = Math.max(0, Math.min(100, parseInt(el.getAttribute('data-around-pct'), 10) || 0));
    var label = el.querySelector('.quiz-results-accuracy');
    function paint(v) {
      el.style.setProperty('--quiz-pct', String(v));
      if (label) label.textContent = Math.round(v) + '% correct';
    }
    el.classList.add('is-set');
    if (!pct || !full()) { paint(pct); return; }
    var t0 = null;
    var dur = 350 + pct * 7;
    paint(0);
    function step(ts) {
      if (t0 === null) t0 = ts;
      var k = Math.min(1, (ts - t0) / dur);
      paint(pct * (1 - Math.pow(1 - k, 3)));
      if (k < 1) W.requestAnimationFrame(step); else paint(pct);
    }
    W.requestAnimationFrame(step);
  }

  // ---- profile: the level ring fills once per visit (session) ----
  function levelRing() {
    var f = D.querySelector('.xp-level-ring-fill');
    if (!f || !f.animate || !full()) return;
    try {
      if (W.sessionStorage.getItem('pb-around-xp')) return;
      W.sessionStorage.setItem('pb-around-xp', '1');
    } catch (e) { /* no storage: it simply plays on each load */ }
    f.animate(
      [{ strokeDashoffset: parseFloat(f.getAttribute('stroke-dasharray')) || 113.1 }, { strokeDashoffset: parseFloat(f.getAttribute('stroke-dashoffset')) || 0 }],
      { duration: 900, delay: 150, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' }
    );
  }

  // ---- waiting: after 400 ms a small Zorp thinks beside the wait and nods when the answer arrives ----
  function wait(body) {
    if (!body || body._aw) return;
    var w = body._aw = { t: 0, loop: 0, box: null, svg: null };
    body.setAttribute('aria-busy', 'true');
    w.t = W.setTimeout(function () { w.t = 0; mount(body, w); }, 400);
  }
  function mount(body, w) {
    if (body._aw !== w || !body.parentNode) return;
    var box = D.createElement('div');
    box.className = 'around-wait';
    box.setAttribute('aria-hidden', 'true');
    var host = D.createElement('span');
    host.className = 'study-buddy-face';
    host.setAttribute('data-buddy-face', '');
    box.appendChild(host);
    body.parentNode.insertBefore(box, body);
    var svg = rig(host);
    if (!svg) { box.parentNode.removeChild(box); return; }
    w.box = box;
    w.svg = svg;
    var z = Z();
    if (!z) return;
    z.setExpression('thinking', { el: svg });
    (function again() {
      z.play('think-chin', { el: svg });
      w.loop = W.setTimeout(again, 2000);
    }());
  }
  function done(body) {
    var w = body && body._aw;
    if (!w) return;
    body._aw = null;
    body.removeAttribute('aria-busy');
    W.clearTimeout(w.t);
    W.clearTimeout(w.loop);
    var box = w.box;
    if (!box) return;
    var z = Z();
    function gone() { if (box.parentNode) box.parentNode.removeChild(box); }
    if (z && full()) { z.play('nod', { el: w.svg }); W.setTimeout(gone, 900); } else gone();
  }

  // ---- practice: the corner Zorp's eyes follow the focused option or input, and glance at the hint card (eyes only) ----
  function look() {
    if (D.body.getAttribute('data-guide-endpoint') !== 'index') return;
    var face = D.querySelector('#study-buddy .study-buddy-face');
    var q = D.querySelector('.question');
    if (!face || !q) return;
    var back = 0;
    var cur = '0px 0px';
    function apply() {
      var list = face.querySelectorAll('.zorp-face .buddy-pupil');
      var i;
      for (i = 0; i < list.length; i += 1) {
        list[i].style.transition = 'translate 220ms ease-out';
        list[i].style.translate = cur;
      }
    }
    function aim(target) {
      var dx = 0;
      var dy = 0;
      if (target && full()) {
        var a = face.getBoundingClientRect();
        var b = target.getBoundingClientRect();
        var vx = b.left + b.width / 2 - (a.left + a.width / 2);
        var vy = b.top + b.height / 2 - (a.top + a.height / 2);
        var len = Math.sqrt(vx * vx + vy * vy) || 1;
        dx = 2.2 * vx / len;
        dy = 1.6 * vy / len;
      }
      cur = dx.toFixed(2) + 'px ' + dy.toFixed(2) + 'px';
      apply();
    }
    // a face change swaps the eye nodes, so the look is written onto the new pupils too
    if (W.MutationObserver) {
      new W.MutationObserver(function () { W.requestAnimationFrame(apply); }).observe(face, { childList: true, subtree: true });
    }
    function focused() {
      var a = D.activeElement;
      return a && a.matches && a.matches('.mcq-btn, .question input, .question textarea, .question select') ? a : null;
    }
    D.addEventListener('focusin', function () {
      W.clearTimeout(back);
      var f = focused();
      if (f) aim(f);
    });
    D.addEventListener('focusout', function () {
      W.clearTimeout(back);
      back = W.setTimeout(function () { aim(focused()); }, 140);
    });
    if (W.MutationObserver) {
      new W.MutationObserver(function (list) {
        var i;
        for (i = 0; i < list.length; i += 1) {
          var t = list[i].target;
          if (t.classList && t.classList.contains('hint-card') && !t.hidden) {
            aim(t);
            W.clearTimeout(back);
            back = W.setTimeout(function () { aim(focused()); }, 2600);
            return;
          }
        }
      }).observe(q, { attributes: true, subtree: true, attributeFilter: ['hidden'] });
    }
  }

  W.pbAround = { wait: wait, done: done };

  function init() {
    faces();
    var rings = D.querySelectorAll('[data-around-ring]');
    var i;
    for (i = 0; i < rings.length; i += 1) ring(rings[i]);
    levelRing();
    look();
  }
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', init); else init();
}());
