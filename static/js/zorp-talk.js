/* Zorp talking mouth (E9 Phase 1, docs/ZORP_CHARM.md 3.1, API 4.2): pbZorp.talk/say/hush/isTalking/talkPlan via pb.register.
   Text first (say is synchronous); then talk-1/talk-2 (or side-talk-*) in a temporary g.zorp-slot--talk are stepped by
   opacity for at most `max` ms. Full motion only; never hidden, off screen, back view or quiz. Nodes only. */
(function () {
  'use strict';
  var pb = window.pbZorp;
  if (!pb || typeof pb.register !== 'function' || typeof pb.talk === 'function') return;
  var NS = 'http://www.w3.org/2000/svg';
  var LEAD = 120;
  var MAX_CEIL = 2000;
  var T_OPEN = 75, T_SHUT = 60, T_GAP = 40;
  var F_OPEN = 60, F_SHUT = 51, F_GAP = 24;
  var PAUSE_FLOOR = 0.6;
  var OPEN_BASE = ['grin', 'grin-tongue', 'laugh', 'wow', 'o', 'side-grin', 'side-o'];
  function clamp(n, lo, hi) { return Math.min(hi, Math.max(lo, n)); }
  function syllables(tok) {
    if (tok.charAt(0) === '@') return 2;
    var parts = tok.toLowerCase().replace(/['\u2019]/g, '').match(/[a-z]+|\d+/g) || [];
    var n = 0;
    parts.forEach(function (p) {
      if (/\d/.test(p.charAt(0))) { n += Math.max(1, Math.ceil(p.length / 2)); return; }
      var g = (p.match(/[aeiouy]+/g) || []).length;
      if (g > 1 && /[^aeiouy]e$/.test(p) && !/[^aeiouy]le$/.test(p)) g -= 1;
      n += Math.max(1, g);
    });
    return Math.max(1, n);
  }
  function pauseOf(tok) {
    var run = (/([.,;:!?\u2026)\]]+)["'\u201d\u2019]*$/.exec(tok) || [])[1] || '';
    if (!run) return 0;
    if (/\u2026|\.\.\./.test(run)) return 360;
    if (/[.!?]/.test(run)) return 260;
    if (/[,;]/.test(run)) return 140;
    return 180;
  }
  function tokensOf(text) {
    return String(text === undefined || text === null ? '' : text).split(/\s+/).filter(Boolean).map(function (tok, i, all) {
      var last = i === all.length - 1;
      return {
        n: syllables(tok),
        short: tok.replace(/[^A-Za-z]/g, '').length <= 2,
        pause: last ? 0 : pauseOf(tok),
        lead: /^[(\[]/.test(tok) ? 180 : 0
      };
    });
  }
  function build(toks, p, max) {
    var t = LEAD;
    var end = LEAD;
    var frames = [[0, 0]];
    var words = [];
    var wi;
    var i;
    for (wi = 0; wi < toks.length; wi += 1) {
      var w = toks[wi];
      for (i = 0; i < w.n; i += 1) {
        if (t + p.open + p.shut > max) return { ms: end, frames: frames, words: words, whole: false };
        if (!i) words.push(t);
        frames.push([t, !i && !w.short ? 2 : 1]);
        t += p.open;
        frames.push([t, 0]);
        t += p.shut;
        end = t;
      }
      if (wi < toks.length - 1) {
        t += Math.max(p.gap, Math.round(w.pause * p.pause));
        if (toks[wi + 1].lead) t += Math.round(toks[wi + 1].lead * p.pause);
      }
    }
    return { ms: end, frames: frames, words: words, whole: true };
  }
  function talkPlan(text, opts) {
    var max = clamp(Math.round(+(opts && opts.max) || 1200), LEAD + T_OPEN + T_SHUT, MAX_CEIL);
    var toks = tokensOf(text);
    if (!toks.length) return { ms: 0, frames: [[0, 0]], words: [] };
    var out = build(toks, { open: T_OPEN, shut: T_SHUT, gap: T_GAP, pause: 1 }, max);
    var f = 1;
    while (!out.whole && f > 0.6) {
      f -= 0.02;
      out = build(toks, {
        open: Math.max(F_OPEN, Math.round(T_OPEN * f)), shut: Math.max(F_SHUT, Math.round(T_SHUT * f)),
        gap: Math.max(F_GAP, Math.round(T_GAP * f)), pause: Math.max(PAUSE_FLOOR, f)
      }, max);
    }
    return { ms: out.ms, frames: out.frames, words: out.words };
  }
  pb.register(function (rt) {
    var current = null;
    var io = null;
    function isQuiz() { return !!(document.body && document.body.getAttribute('data-guide-quiz') === '1'); }
    function layer(parent, node) {
      var g = document.createElementNS(NS, 'g');
      g.style.opacity = '0';
      if (node) rt.fill(g, node);
      parent.appendChild(g);
      return g;
    }
    function end(inst, ok) {
      var tk = inst.talk;
      if (!tk) return;
      inst.talk = null;
      inst.talking = false;
      if (current === inst) current = null;
      if (tk.timer) clearTimeout(tk.timer);
      tk.anims.forEach(function (a) { try { a.cancel(); } catch (e) { /* ignore */ } });
      if (tk.node.parentNode) tk.node.parentNode.removeChild(tk.node);
      if (io) { try { io.unobserve(inst.svg); } catch (e2) { /* ignore */ } }
      if (!ok && tk.blips && window.pbSound) window.pbSound.stopAll();
      tk.resolve(!!ok);
    }
    function hush(el) {
      var inst = el ? rt.inst({ el: el }) : current;
      if (inst && inst.talk) end(inst, false);
    }
    function steps(plan, pick) {
      var out = plan.frames.map(function (f, i) { return { offset: f[0] / plan.ms, opacity: pick(f[1], i), easing: 'steps(1, end)' }; });
      out.push({ offset: 1, opacity: out[out.length - 1].opacity });
      return out;
    }
    function talk(o) {
      o = o || {};
      var inst = rt.inst(o);
      if (!inst) return Promise.resolve(false);
      if (current && current !== inst) end(current, false);
      if (inst.talk) end(inst, false);
      var slot = inst.slots && inst.slots.mouth;
      var face = slot && slot.parentNode;
      if (!face || rt.level() !== 'full' || document.hidden || isQuiz() || inst.view === 'back' || !rt.rendered(inst)) return Promise.resolve(false);
      var plan = talkPlan(o.text, { max: o.max });
      if (plan.frames.length < 2) return Promise.resolve(false);
      var side = inst.view === 'side' || inst.view === 'back-glance';
      var n1 = rt.node('mouth', side ? 'side-talk-1' : 'talk-1');
      var n2 = rt.node('mouth', side ? 'side-talk-2' : 'talk-2');
      var open = OPEN_BASE.indexOf(inst.drawn && inst.drawn.mouth) !== -1;
      var nc = open ? rt.node('mouth', side ? 'side-smile' : 'smile') : null;
      if (!n1 || !n2 || (open && !nc)) return Promise.resolve(false);
      var g = document.createElementNS(NS, 'g');
      g.setAttribute('class', 'zorp-slot--talk');
      if (slot.style && slot.style.translate) g.style.translate = slot.style.translate;
      if (slot.style && slot.style.scale) g.style.scale = slot.style.scale;
      var l1 = layer(g, n1);
      var l2 = layer(g, n2);
      var lc = open ? layer(g, nc) : null;
      if (slot.nextSibling) face.insertBefore(g, slot.nextSibling); else face.appendChild(g);
      var tk = { anims: [], node: g, timer: 0, resolve: null };
      var p = new Promise(function (res) { tk.resolve = res; });
      var o2 = { duration: plan.ms, fill: 'none' };
      var base = function (s, i) { return open ? (i === 0 ? 1 : 0) : (s === 0 ? 1 : 0); };
      var shut = function (s, i) { return s === 0 && i > 0 ? 1 : 0; };
      try {
        tk.anims.push(l1.animate(steps(plan, function (s) { return s === 1 ? 1 : 0; }), o2));
        tk.anims.push(l2.animate(steps(plan, function (s) { return s === 2 ? 1 : 0; }), o2));
        tk.anims.push(slot.animate(steps(plan, base), o2));
        if (lc) tk.anims.push(lc.animate(steps(plan, shut), o2));
      } catch (e) {
        inst.talk = tk;
        end(inst, false);
        return Promise.resolve(false);
      }
      tk.stop = function () { end(inst, false); };
      // the base mouth opened mid-talk (a gesture's grin): close on a smile
      tk.swap = function (id) {
        var t = tk.anims[0].currentTime;
        var n = rt.node('mouth', side ? 'side-smile' : 'smile');
        if (open || !n || OPEN_BASE.indexOf(id) === -1) return;
        open = true;
        try {
          tk.anims[2].cancel();
          [[slot, base], [layer(g, n), shut]].forEach(function (x) { var a = x[0].animate(steps(plan, x[1]), o2); a.currentTime = t; tk.anims.push(a); });
        } catch (e2) { end(inst, false); }
      };
      // D7 blips: styleguide only
      if (o.blips && window.pbSound) {
        tk.blips = window.pbSound.blips(plan.frames.filter(function (f) { return f[1]; }).map(function (f) { return f[0]; }), o.text, { force: o.force, words: plan.words });
      }
      tk.timer = setTimeout(function () { end(inst, true); }, plan.ms + 20);
      inst.talk = tk;
      inst.talking = true;
      current = inst;
      if (typeof IntersectionObserver !== 'undefined') {
        if (!io) {
          io = new IntersectionObserver(function (entries) {
            entries.forEach(function (en) { if (!en.isIntersecting && current && current.svg === en.target) hush(); });
          });
        }
        io.observe(inst.svg);
      }
      return p;
    }
    function say(target, text, o) {
      o = o || {};
      if (target) target.textContent = text;
      if (o.el) hush(o.el);
      if (!o.el || o.talk === false) return Promise.resolve(false);
      return talk({ el: o.el, text: text, max: o.max });
    }
    document.addEventListener('visibilitychange', function () { if (document.hidden) hush(); });
    // motion dropped to reduced or off mid-talk (OS query or the data-motion settings): hush
    function calm() { if (current && rt.level() !== 'full') hush(); }
    var mq = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mq) { if (mq.addEventListener) mq.addEventListener('change', calm); else if (mq.addListener) mq.addListener(calm); }
    if (typeof MutationObserver !== 'undefined') new MutationObserver(calm).observe(document.documentElement, { attributes: true, attributeFilter: ['data-motion', 'data-motion-preview'] });
    pb.talk = talk;
    pb.say = say;
    pb.hush = hush;
    pb.isTalking = function (el) { var inst = el ? rt.inst({ el: el }) : current; return !!(inst && inst.talk); };
  });
  pb.talkPlan = talkPlan;
}());
