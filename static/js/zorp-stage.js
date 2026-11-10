/* Zorp stage (E10 phase 1, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md 6.1): a full-screen layer with a backdrop, props, a large
   Zorp (and his crew), a text panel, Continue and Skip. Loaded on demand by guide.js (pbGuide.loadStage) with stage.css and
   stage-catalog.js, so ordinary pages never carry it. Scenes are catalog data (stage-catalog.js); this file only runs them.
   API: pbStage.play(idOrScenes, opts) -> Promise({ ended: 'done' | 'skip' | 'close', scene }); stages queue, never overlap.
   opts: start (scene index), skipTo (Skip and Esc jump there instead of closing), story (the scene's story labels), slot
   (nodes a slot scene shows; they go back where they were on close), resume (no entrance fade), onScene(i, scene).
   pbStage.cue(beats) runs beats on the open stage; pbStage.zorp() is its Zorp. Motion: full plays the beats; reduced shows
   each scene as a still frame with a fade; off shows the same frame at once. Transform and opacity only, DOM nodes only (no
   markup strings), props cloned from static/images/stage-props.svg. A dialog: heading, live lines, focus kept inside and given back,
   Esc and a visible Skip always work, nothing advances by itself. */
(function () {
  'use strict';
  if (window.pbStage) return;
  var D = document;
  var R = null;      // the built stage (elements)
  var S = null;      // the running stage
  var RT = null;     // pbZorp internals (register)
  var queue = [];
  var props = null;
  var more = [];     // extra props documents (story-props.svg, handed over by story-chapters.js)
  var propsP = null;
  var EASE = 'cubic-bezier(.2,.7,.3,1)';
  var CREW = [{ colour: 'mint', antenna: 'short', face: 'grin' }, { colour: 'sunny', antenna: 'long', face: 'happy' },
    { colour: 'mint', antenna: 'long', face: 'joy' }];
  var PARTS = { planet: ['st-planet'], ship: ['st-ship', 0, 'st-ship-rim'], logbook: ['st-logbook'], card: ['st-card'],
    rock: ['st-rock'], door: ['st-door'], toaster: ['st-toaster'], postcard: ['st-postcard'] };   // the last four are the story chapters' props (story-props.svg, phase 8)
  var ENTER = {
    planet: [[{ transform: 'translateY(70px) scale(.94)', opacity: 0 }, { transform: 'none', opacity: 1 }], 1500],
    ship: [[{ transform: 'translate(90px,-24px) rotate(4deg)', opacity: 0 }, { transform: 'none', opacity: 1 }], 1000],
    _: [[{ transform: 'translateY(28px) scale(.92)', opacity: 0 }, { transform: 'none', opacity: 1 }], 600]
  };
  function noop() {}
  function Z() { return window.pbZorp || null; }
  function cat() { return window.pbStageCatalog || { scenes: [] }; }
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
  function wait(ms) { return new Promise(function (res) { setTimeout(res, ms); }); }
  function track(a) { if (S && a) S.anims.push(a); return a; }
  function anim(node, frames, ms, o) {
    if (!node || !node.animate) return Promise.resolve();
    o = o || {};
    o.duration = ms;
    o.easing = o.easing || EASE;
    try { return track(node.animate(frames, o)).finished.then(noop, noop); } catch (e) { return Promise.resolve(); }
  }

  // ---- composite clips, registered on the runtime (zorp-poses.js has no room to grow) ----
  function registerClips() {
    var z = Z();
    if (!z || !z.register || RT) return;
    z.register(function (rt) {
      RT = rt;
      var pre = rt.clips.cheer && rt.clips.cheer.pre;
      var info = z.clipInfo && z.clipInfo('cheer');
      if (!pre || !z.compileBeats || !info) return;
      function beatClip(beats, face) {
        var span = beats.reduce(function (s, b) { return s + (b.ms || 0) + (b.hold || 0); }, 0) + info.tail;
        var c = { dur: span, beats: beats, face: face, reducedFace: face, pre: pre };
        c.tracks = function (parts, pupils, o) { return z.compileBeats(beats, parts, o); };
        // a beat's preset changes at its start and the clip's own face comes back at the end (tempFace); `ch` draws channels
        // that no preset has (the look up), and the stage puts the scene's face back after the beat list
        c.start = function (inst, spd) {
          var t = 0;
          beats.forEach(function (b) {
            var t0 = t;
            if (b.ch) rt.after(inst, t0 / spd, function () { rt.setExpression(b.ch, { el: inst.svg }); });
            if (b.expr) rt.after(inst, t0 / spd, function () { rt.tempFace(inst, b.expr, Math.max(1, (span - t0) / spd), b.fx || ''); });
            t += (b.ms || 0) + (b.hold || 0);
          });
        };
        return c;
      }
      function add(name, c) { rt.clips[name] = c; if (rt.names.indexOf(name) === -1) rt.names.push(name); }
      // stage-arrive: legs dangling (the float pose), a slow hover while the stage brings him down, then the soft-body
      // landing (squash, jelly) and a happy settle. About 2.2 s.
      add('stage-arrive', beatClip([
        { pose: 'float', expr: 'happy', ms: 300, ease: 'out' },
        { pose: 'float', y: -3, hr: 3, ms: 450, ease: 'io' },
        { pose: 'float', y: 2, hr: -3, ms: 450, ease: 'io' },
        { pose: 'float', y: -2, hr: 2, ms: 450, ease: 'io' },
        { pose: 'stand', y: 1, s: [1.1, 0.9], ms: 160, ease: 'in' },
        { pose: 'stand', ms: 260, hold: 60, ease: 'overshoot' }], 'happy'));
      // stage-gaze: head tipped back, eyes up and mouth round at something big overhead, then a happy settle. About 1.7 s.
      add('stage-gaze', beatClip([
        { pose: 'stand', ch: { eyes: 'look-up', brows: 'raised', mouth: 'o', fx: 'none' }, y: -1, hr: -10, ms: 320, hold: 900, ease: 'out' },
        { pose: 'stand', expr: 'happy', ms: 340, ease: 'io' }], 'happy'));
    });
  }

  // ---- props ----
  function assets() {
    try { return JSON.parse((D.getElementById('pb-stage-assets') || {}).textContent || '{}') || {}; } catch (e) { return {}; }
  }
  function ready() {
    registerClips();
    if (!propsP) {
      var url = assets().props;
      propsP = (url && window.fetch && window.DOMParser ? fetch(url, { credentials: 'same-origin' }).then(function (r) {
        return r.ok ? r.text() : '';
      }).then(function (text) {
        var doc = text ? new window.DOMParser().parseFromString(text, 'image/svg+xml') : null;
        if (doc && !doc.getElementsByTagName('parsererror').length) props = doc;
      }) : Promise.resolve()).catch(noop).then(function () { return api; });
    }
    return propsP;
  }
  function part(id) {
    var src = null;
    [props].concat(more).forEach(function (d) { if (d && !src) src = d.querySelector('[id="' + id + '"]'); });
    if (!src) return null;
    var n = D.importNode(src, true);
    n.removeAttribute('id');
    n.setAttribute('aria-hidden', 'true');
    n.setAttribute('focusable', 'false');
    return n;
  }

  // A copy of the page's own Zorp (the guide overlay rig, which every signed-in page and the preview have). A crew member is
  // the same rig in a cosmetics colour and other antennae, without hat or shoes.
  function rig(host, look) {
    var src = D.querySelector('[data-guide-face] svg.buddy-mascot') || D.querySelector('svg.buddy-mascot');
    if (!src) return null;
    var svg = src.cloneNode(true);
    svg.classList.remove('is-zorp-idle');
    if (look) {
      ['colour', 'antenna', 'feet'].forEach(function (k) { svg.removeAttribute('data-zorp-' + k); });
      svg.removeAttribute('data-mouth');
      svg.setAttribute('data-zorp-colour', look.colour);
      svg.setAttribute('data-zorp-antenna', look.antenna);
      Array.prototype.forEach.call(svg.querySelectorAll('.zorp-hatride, .zorp-shoe'), function (n) { n.parentNode.removeChild(n); });
    }
    host.appendChild(svg);
    var z = Z();
    if (z) {
      z.bind(host);
      z.turn('front', 'r', { el: svg, instant: true });
      if (look) z.setExpression(look.face, { el: svg });
    }
    return svg;
  }

  function build() {
    var st = el('div', 'pb-stage');
    st.setAttribute('role', 'dialog');
    st.setAttribute('aria-modal', 'true');
    st.setAttribute('aria-labelledby', 'pb-stage-h');
    st.setAttribute('aria-describedby', 'pb-stage-lines');
    var sky = el('div', 'pb-st-sky', st);
    sky.setAttribute('aria-hidden', 'true');
    el('div', 'pb-st-stars', sky);
    el('div', 'pb-st-stars pb-st-stars--far', sky);
    var set = el('div', 'pb-st-set', st);
    set.setAttribute('aria-hidden', 'true');
    el('div', 'pb-st-horizon', set);
    var r = { st: st, set: set, props: {}, crew: [] };
    r.burst = el('div', 'pb-st-burst', set);
    r.streak = el('div', 'pb-st-streak', set);
    Object.keys(PARTS).forEach(function (name) {
      var box = el('div', 'pb-st-prop pb-st-prop--' + name, set);
      box.hidden = true;
      PARTS[name].forEach(function (id) {
        if (id) { var n = part(id); if (n) box.appendChild(n); return; }
        var crew = el('div', 'pb-st-crew', box);
        CREW.forEach(function (look) {
          var host = el('span', 'study-buddy-face pb-st-mate', crew);
          host.setAttribute('data-buddy-face', '');
          var svg = rig(host, look);
          if (svg) r.crew.push(svg);
        });
      });
      r.props[name] = box;
    });
    r.actor = el('div', 'pb-st-actor', set);
    el('div', 'pb-st-glow', r.actor);
    var host = el('span', 'study-buddy-face pb-st-zorp', r.actor);
    host.setAttribute('data-buddy-face', '');
    r.zorp = rig(host, null);
    var panel = el('div', 'pb-st-panel', st);
    r.panel = panel;
    var top = el('div', 'pb-st-top', panel);
    r.heading = el('h2', 'pb-st-heading', top);
    r.heading.id = 'pb-stage-h';
    r.dots = el('ol', 'pb-st-dots', top);
    r.dots.setAttribute('aria-hidden', 'true');
    r.lines = el('div', 'pb-st-lines', panel);
    r.lines.id = 'pb-stage-lines';
    r.lines.setAttribute('aria-live', 'polite');
    r.slot = el('div', 'pb-st-slot', panel);
    var acts = el('div', 'pb-st-actions', panel);
    r.next = el('button', 'btn btn-primary', acts);
    r.skip = el('button', 'btn btn-outline', acts);
    r.next.type = r.skip.type = 'button';
    r.next.addEventListener('click', onNext);
    r.skip.addEventListener('click', onSkip);
    return r;
  }

  // ---- scenes ----
  function sceneOf(x) {
    if (typeof x !== 'string') return x;
    var list = cat().scenes || [];
    for (var i = 0; i < list.length; i += 1) if (list[i].id === x) return list[i];
    return null;
  }
  function expand(spec) {
    if (typeof spec === 'string' && Array.isArray(cat()[spec])) spec = cat()[spec];
    return (Array.isArray(spec) ? spec : [spec]).map(sceneOf).filter(Boolean);
  }
  function linesOf(sc) { return (sc.lines || []).filter(function (t) { return typeof t === 'string' && t; }); }
  function eachBeat(sc, fn) { (sc.beats || []).forEach(function (list) { (list || []).forEach(fn); }); }

  function stopRigs() {
    if (!R || !RT) return;
    [R.zorp].concat(R.crew).forEach(function (svg) {
      var inst = svg && RT.inst({ el: svg });
      if (inst) RT.stop(inst);
    });
  }
  function face(name) {
    var z = Z();
    // valence guard: a stage never rests on a negative preset (the catalog is also checked by the smoke)
    if (z && R && R.zorp && name && z.valenceOf(name) !== 'negative') z.setExpression(name, { el: R.zorp });
  }

  function propShow(name, animate) {
    if (name === 'streak') {
      if (!animate || !full()) return null;
      return anim(R.streak, [{ transform: 'translate(46vw,-52vh) rotate(-35deg)', opacity: 0 }, { opacity: 1, offset: 0.25 },
        { transform: 'translate(0,0) rotate(-35deg)', opacity: 0 }], 900, { easing: 'cubic-bezier(.5,0,.8,.6)' });
    }
    var box = R.props[name];
    if (!box || !box.hidden) return null;
    box.hidden = false;
    if (!animate || !full()) return null;
    var k = ENTER[name] || ENTER._;
    return anim(box, k[0], k[1]);
  }
  function propSet(name, state) {
    var box = R.props[name];
    if (!box) return null;
    var now = ' ' + (box.getAttribute('data-set') || '') + ' ';
    if (now.indexOf(' ' + state + ' ') === -1) box.setAttribute('data-set', (now + state).trim());
    return null;
  }
  function propsFor(sc, animate) {
    var want = sc.props || [];
    Object.keys(R.props).forEach(function (name) {
      var box = R.props[name];
      if (want.indexOf(name) !== -1 || box.hidden) return;
      if (!animate) { box.hidden = true; box.removeAttribute('data-set'); return; }
      anim(box, [{ opacity: 1 }, { opacity: 0 }], 300).then(function () { box.hidden = true; box.removeAttribute('data-set'); });
    });
  }

  function arrive() {
    var a = R.actor;
    var z = Z();
    var dist = a.offsetTop + a.offsetHeight + 80;
    a.style.opacity = '';
    var clip = z && z.hasClip('stage-arrive') ? z.play('stage-arrive', { el: R.zorp }) : null;
    anim(a.firstChild, [{ opacity: 0 }, { opacity: 0.9, offset: 0.6 }, { opacity: 0 }], 2600);
    return Promise.all([anim(a, [{ transform: 'translate(40px,' + -dist + 'px)', opacity: 0 }, { opacity: 1, offset: 0.12 },
      { transform: 'none', opacity: 1 }], 1650, { easing: 'cubic-bezier(.22,.8,.35,1)' }), clip]).then(noop);
  }

  function beat(b) {
    var z = Z();
    if (b.wait) return full() ? wait(b.wait) : null;
    if (b.prop) return b.set ? propSet(b.prop, b.set) : propShow(b.prop, true);
    if (b.burst) {
      if (full()) anim(R.burst, [{ opacity: 0, transform: 'scale(.6)' }, { opacity: 0.9, transform: 'scale(1)', offset: 0.4 }, { opacity: 0, transform: 'scale(1.15)' }], 2400);
      return null;
    }
    if (b.zorp === 'arrive') return arrive();
    if (!z || !R.zorp) return null;
    if (b.talk) {
      if (z.talk && S && S.line) z.talk({ el: R.zorp, text: S.line, max: 1600 });
      return null;
    }
    if (b.face) { face(b.face); return null; }
    if (b.turn) return z.turn(b.turn, b.facing === 'l' ? 'l' : 'r', { el: R.zorp });
    if (b.crew) {
      return Promise.all(R.crew.map(function (svg, i) {
        return wait(i * 180).then(function () { return z.play(b.crew, { el: svg }); });
      }));
    }
    if (b.play) return z.play(b.play, { el: R.zorp, target: b.target, facing: b.facing, cue: true });
    return null;
  }

  // Beats in order; `async` ones do not hold the next. A newer line or scene (S.tok) stops the rest.
  function runBeats(list, tok, after) {
    var p = Promise.resolve();
    (list || []).forEach(function (b) {
      p = p.then(function () {
        if (!S || S.tok !== tok) return null;
        var r = beat(b);
        return b.async ? null : r;
      });
    });
    return p.then(function () { if (S && S.tok === tok && after) after(); }, noop);
  }

  function dots() {
    while (R.dots.firstChild) R.dots.removeChild(R.dots.firstChild);
    if (S.scenes.length < 2) return;
    S.scenes.forEach(function (sc, i) {
      el('li', i === S.i ? 'is-current' : (i < S.i ? 'is-done' : ''), R.dots);
    });
  }

  function layout(name, animate) {
    var a = R.actor;
    var before = animate ? a.getBoundingClientRect() : null;
    R.st.setAttribute('data-layout', name || 'centre');
    if (!before || !before.width) return;
    var after = a.getBoundingClientRect();
    var dx = before.left - after.left;
    var dy = before.top - after.top;
    var s = before.width / (after.width || 1);
    if (Math.abs(dx) < 1 && Math.abs(dy) < 1 && Math.abs(s - 1) < 0.01) return;
    anim(a, [{ transform: 'translate(' + dx + 'px,' + dy + 'px) scale(' + s + ')' }, { transform: 'none' }], 650);
  }

  function showLine(li) {
    var sc = S.scene;
    var lines = linesOf(sc);
    var still = !full();
    var from = still ? 0 : li;
    var to = still ? lines.length - 1 : li;
    Array.prototype.forEach.call(R.lines.children, function (p) { p.classList.add('is-past'); });
    for (var k = from; k <= to; k += 1) {
      var p = el('p', 'pb-st-line', R.lines);
      p.textContent = lines[k];
      if (level() === 'full') anim(p, [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], 300);
      else if (level() === 'reduced') anim(p, [{ opacity: 0 }, { opacity: 1 }], 300);
    }
    S.li = to;
    S.line = lines[to] || '';
    var last = to >= lines.length - 1;
    var labels = (S.opts.story && sc.story) || {};
    R.next.textContent = (last && labels.primary) || sc.primary || 'Continue';
    S.tok += 1;
    if (still) return;
    runBeats((sc.beats || [])[li], S.tok, function () { face(last ? sc.end : sc.face); });
  }

  function slotIn(nodes) {
    (nodes || []).forEach(function (n) {
      if (!n || !n.parentNode) return;
      var mark = D.createComment('stage');
      n.parentNode.insertBefore(mark, n);
      S.moved.push([n, mark, n.hidden, n.inert]);
      n.hidden = false;
      n.inert = false;   // a body child (the sticky Start bar) was made inert with the page
      R.slot.appendChild(n);
    });
  }
  function slotOut() {
    if (!S) return;
    S.moved.forEach(function (m) {
      if (m[1].parentNode) { m[1].parentNode.insertBefore(m[0], m[1]); m[1].parentNode.removeChild(m[1]); }
      m[0].hidden = m[2];
      m[0].inert = !!m[3];
    });
    S.moved = [];
  }

  function goScene(i) {
    var sc = S.scenes[i];
    if (!sc) { finish('done'); return; }
    var first = S.i < 0;
    var animate = full() && !first;
    S.tok += 1;
    S.anims.forEach(function (a) { try { a.cancel(); } catch (e) { /* gone */ } });
    S.anims = [];
    stopRigs();
    slotOut();
    S.i = i;
    S.scene = sc;
    R.st.setAttribute('data-scene', sc.id || '');
    R.heading.textContent = sc.heading || 'Zorp';
    dots();
    layout(sc.layout, animate);
    propsFor(sc, animate);
    // a listed prop that no beat brings in (it stayed from the scene before, or the scene plays alone) is simply there
    var shown = {};
    eachBeat(sc, function (b) { if (b.prop && !b.set) shown[b.prop] = 1; });
    (sc.props || []).forEach(function (name) { if (!shown[name]) propShow(name, animate); });
    while (R.lines.firstChild) R.lines.removeChild(R.lines.firstChild);
    R.actor.style.opacity = '';
    var z = Z();
    var view = z && R.zorp ? z.viewOf(R.zorp) : null;
    if (view && view.view !== 'front') z.turn('front', 'r', { el: R.zorp, instant: !full() });
    face(full() ? sc.face : sc.end);
    var slot = !!sc.slot;
    R.st.toggleAttribute('data-slot', slot);
    R.next.hidden = slot;
    R.skip.hidden = slot || !sc.skipLabel;
    R.skip.textContent = sc.skipLabel || '';
    if (!full()) {
      // still frame: every prop and state the beats would reach, the end face
      eachBeat(sc, function (b) { if (b.prop) { if (b.set) propSet(b.prop, b.set); else propShow(b.prop, false); } });
      if (level() === 'reduced' && !(first && S.opts.resume)) anim(R.set, [{ opacity: 0 }, { opacity: 1 }], 320, { easing: 'ease-out' });
    } else {
      var arrives = false;
      eachBeat(sc, function (b) { if (b.zorp === 'arrive') arrives = true; });
      if (arrives) R.actor.style.opacity = '0';
    }
    if (slot) {
      slotIn(S.opts.slot);
      S.tok += 1;
      if (full()) runBeats((sc.beats || [])[0], S.tok, function () { face(sc.end); });
      var h = R.slot.querySelector('h1, h2');
      if (h) { h.setAttribute('tabindex', '-1'); focus(h); }
    } else {
      showLine(0);
      if (first || !R.st.contains(D.activeElement)) focus(R.next);
    }
    if (S.opts.onScene) { try { S.opts.onScene(i, sc); } catch (e) { /* the caller's hook must not stop the stage */ } }
  }

  function focus(n) { setTimeout(function () { try { n.focus({ preventScroll: true }); } catch (e) { /* gone */ } }, 0); }

  function onNext() {
    if (!S || S.i < 0) return;
    if (S.li < linesOf(S.scene).length - 1) showLine(S.li + 1);
    else goScene(S.i + 1);
  }
  function onSkip() {
    if (!S || S.i < 0) return;
    var to = S.opts.skipTo;
    if (typeof to === 'number' && to > S.i && S.scenes[to]) goScene(to);
    else finish('skip');
  }

  function focusables() {
    return Array.prototype.filter.call(R.st.querySelectorAll('button, a[href], input:not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])'), function (n) {
      return !n.disabled && !n.closest('[hidden]') && n.getClientRects().length > 0;
    });
  }
  function onKey(e) {
    if (!S || S.i < 0) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      if (S.scene && S.scene.slot) finish('close');
      else onSkip();
      return;
    }
    if (e.key !== 'Tab') return;
    var items = focusables();
    if (!items.length) return;
    var a = items[0];
    var b = items[items.length - 1];
    if (!R.st.contains(D.activeElement)) { e.preventDefault(); a.focus(); }
    else if (e.shiftKey && D.activeElement === a) { e.preventDefault(); b.focus(); }
    else if (!e.shiftKey && D.activeElement === b) { e.preventDefault(); a.focus(); }
  }

  function open(scenes, job) {
    R = build();
    S = { scenes: scenes, opts: job.opts, job: job, i: -1, li: 0, tok: 0, anims: [], moved: [], inert: [], back: D.activeElement };
    Array.prototype.forEach.call(D.body.children, function (n) {
      if (n.inert || n.classList.contains('app-toast-host') || n.tagName === 'SCRIPT') return;
      n.inert = true;
      S.inert.push(n);
    });
    D.body.appendChild(R.st);
    D.body.classList.add('pb-stage-open');
    D.addEventListener('keydown', onKey, true);
    var z = Z();
    if (z && R.zorp) z.idle(true, R.zorp);
    var start = Math.max(0, Math.min(scenes.length - 1, job.opts.start || 0));
    goScene(start);
    if (!job.opts.resume && level() !== 'off') anim(R.st, [{ opacity: 0 }, { opacity: 1 }], 400, { easing: 'ease-out' });
  }

  function finish(how) {
    if (!S) return;
    var s = S;
    var r = R;
    s.tok += 1;
    stopRigs();
    slotOut();
    D.removeEventListener('keydown', onKey, true);
    s.inert.forEach(function (n) { n.inert = false; });
    D.body.classList.remove('pb-stage-open');
    var z = Z();
    if (z) [r.zorp].concat(r.crew).forEach(function (svg) { if (svg) z.idle(false, svg); });
    var done = function () {
      if (r.st.parentNode) r.st.parentNode.removeChild(r.st);
      S = null;
      R = null;
      if (s.back && s.back.focus && D.contains(s.back)) { try { s.back.focus({ preventScroll: true }); } catch (e) { /* gone */ } }
      s.job.resolve({ ended: how, scene: s.scene ? s.scene.id : '' });
      try { D.dispatchEvent(new CustomEvent('pb-stage-closed', { detail: { ended: how } })); } catch (e) { /* old browser */ }
      next();
    };
    r.st.style.pointerEvents = 'none';
    if (level() === 'off') done();
    else anim(r.st, [{ opacity: 1 }, { opacity: 0 }], 250, { easing: 'ease-in' }).then(done);
  }

  function next() {
    if (S || !queue.length) return;
    var job = queue.shift();
    var scenes = expand(job.spec);
    if (!scenes.length) { job.resolve({ ended: 'empty', scene: '' }); next(); return; }
    S = { pending: true };
    ready().then(function () { S = null; open(scenes, job); });
  }

  function play(spec, opts) {
    return new Promise(function (resolve) {
      queue.push({ spec: spec, opts: opts || {}, resolve: resolve });
      next();
    });
  }

  var api = {
    play: play,
    ready: ready,
    isOpen: function () { return !!S; },
    close: function () { if (S && S.i >= 0) finish('close'); },
    cue: function (beats) { return S && S.i >= 0 ? runBeats(beats, S.tok) : Promise.resolve(); },
    zorp: function () { return R ? R.zorp : null; },
    scenes: expand,
    addProps: function (doc) { if (doc && more.indexOf(doc) === -1) more.push(doc); }
  };
  window.pbStage = api;
  registerClips();
}());
