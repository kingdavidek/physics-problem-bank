/* E7 Phase 1: Zorp motion runtime (docs/MASCOT_MOTION_AND_ONBOARDING.md §3.2).
   WAAPI clips on rig groups; CSS idle loop in static/css/motion.css. No libraries.
   E8 Phase 1 (docs/ZORP_EXPRESSIVENESS.md §4.2-4.4): faces are presets of channels (eyes, brows,
   mouth, cheeks, fx) whose parts are cloned from the inert #pb-zorp-parts template into the
   face slots; presets come from the #pb-zorp-rig data island.
   E8 Phase 3 (docs 3.8): views and the pinch-turn. A view is a resting `translate`/`scale` per part
   (CSS individual transform properties, so clips and E6 gestures animate `transform` on top of it
   without replacing it), plus visibility and side-view part variants, all from the island. */
(function () {
  'use strict';
  if (window.pbZorp) return;

  var CLIP_NAMES = ['idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake', 'hop', 'peek', 'sleep', 'side-point'];
  // E8: preset rows are [eyeL, eyeR, brows, mouth, cheeks, fx, valence], from the island
  // (zorp_rig.rig_json) read lazily; this table keeps the legacy faces working without it.
  var SLOT_KEYS = ['eyeL', 'eyeR', 'brows', 'mouth', 'cheeks', 'fx'];
  var SLOT_CHANNEL = { eyeL: 'eyes', eyeR: 'eyes', brows: 'brows', mouth: 'mouth', cheeks: 'cheeks', fx: 'fx' };
  var LEGACY_PRESETS = {
    nudge: ['open', 'open', 'none', 'smile', 'none', 'none', '0'],
    milestone: ['open-lift', 'open-lift', 'none', 'smile-wide', 'none', 'stars', '+'],
    celebrate: ['happy-arc', 'happy-arc', 'none', 'smile-big', 'rosy', 'none', '+'],
    qotd_nudge: ['curious', 'curious-r', 'raised-l', 'o', 'none', 'none', '0'],
    streak_risk: ['open-big', 'open-big', 'raised', 'smile', 'none', 'flame', '+'],
    weak_topic: ['low', 'low-r', 'skeptical', 'flat', 'none', 'none', '0'],
    friend_challenge: ['wink-line', 'open-off', 'none', 'smile-w', 'none', 'none', '+'],
    sleep: ['closed', 'closed-r', 'none', 'sleepy', 'none', 'zzz', '0']
  };
  var ID_RE = /^[a-z0-9-]+$/;
  var presetTable = null;
  var partsTpl;   // undefined until looked up; null when the page has no library
  var GESTURES = { nod: 1, wink: 1, tap: 1, shake: 1 };   // E6 CSS keyframes via data-gesture
  var GESTURE_MS = 1200;                                    // same as guide.js playGesture

  // E7 Phase 2: react() gating + clip mapping (docs/MASCOT_MOTION_AND_ONBOARDING.md Phase 2).
  var REACT_GAP_MS = 900;                                     // global cooldown for correct/wrong/streak
  var CORRECT_VARIANTS = ['cheer', 'wave', 'hop'];            // never repeats lastVariant
  var REACT_CLIP = {
    wrong: 'wobble',
    streak: 'cheer',
    milestone: 'wave',
    lesson_complete: 'cheer',
    first_correct: 'cheer'
  };
  var REACT_RARE = { milestone: 1, lesson_complete: 1, first_correct: 1 };   // bypass the 900ms gate
  var REACT_FACE = { wrong: 'weak_topic' };                   // wrong overrides wobble's resting face
  var lastReactAt = 0;
  var lastVariant = '';
  var rareProtectUntil = 0;   // a rare reaction, once started, can't be cut short by a gated one

  // Thought bubble (wrong reaction, full motion): the `thought` fx part, WAAPI-animated, never in motion.css.
  var THOUGHT_MS = 1200;
  var VAL_WORD = { '+': 'positive', '0': 'neutral', '-': 'negative' };
  var FALLBACK_GUIDE = ['nudge', 'milestone', 'celebrate', 'qotd_nudge', 'streak_risk', 'weak_topic', 'friend_challenge', 'sleep'];
  var rigCtx = null;   // island "c": context -> allowed preset names
  var rigFxFace = [];  // island "ff": fx ids drawn in the face-attached slot
  var rigViews = { front: { armLf: 0, armRf: 0 } };   // island "w": view -> part -> 0 (hidden) | [dx, dy, sx, sy]; missing = visible, unchanged
  var rigVarMap = {};  // island "m": view -> channel -> { front variant id: side variant id }

  // E8 Phase 3: parts a view moves or hides (models/zorp_rig.py VIEW_PARTS) and their selectors.
  var VIEW_SEL = {
    plate: '.zorp-plate', eyeL: '.zorp-slot--eyeL', eyeR: '.zorp-slot--eyeR', brows: '.zorp-slot--brows',
    mouth: '.zorp-slot--mouth', cheeks: '.zorp-slot--cheeks', fxFace: '.zorp-slot--fx-face',
    antL: '.buddy-antenna--l', antR: '.buddy-antenna--r', hl: '.zorp-highlight',
    footL: '.buddy-foot--l', footR: '.buddy-foot--r',
    armL: '.buddy-arm--l', armR: '.buddy-arm--r', armLf: '.buddy-arm--l-front', armRf: '.buddy-arm--r-front'
  };
  var VIEW_KEYS = Object.keys(VIEW_SEL);
  var FRONT_HIDDEN = { armLf: 1, armRf: 1 };
  var TURN_MS = 300;       // pinch-turn: dip, flip to 0.15 by 45%, commit at 50%, overshoot, settle
  var ANT_LAG_MS = 60;     // antennae follow a beat late
  var HAS_PROPS = (function () {
    try { return !!(window.CSS && CSS.supports && CSS.supports('translate', '1px') && CSS.supports('scale', '1')); } catch (e) { return false; }
  }());
  // composite:'add' layers a clip on any resting `transform`; without it clips replace it as before Phase 3.
  var HAS_COMPOSITE = typeof KeyframeEffect !== 'undefined' && !!KeyframeEffect.prototype && 'composite' in KeyframeEffect.prototype;

  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var canAnimate = typeof Element !== 'undefined' && typeof Element.prototype.animate === 'function' &&
    typeof Animation !== 'undefined' && 'finished' in Animation.prototype;
  var instances = [];
  var blinkTimer = 0;

  function motionLevel() {
    // E7 Phase 5: data-motion (set from the user's motion_preference setting) takes
    // priority over the OS-level prefers-reduced-motion media query below.
    var pref = (document.documentElement.getAttribute('data-motion') || 'system');
    if (pref === 'off') return 'off';
    if (pref === 'reduced') return 'reduced';
    if ((mq && mq.matches) || !canAnimate) return 'reduced';
    return 'full';
  }

  function presets() {
    if (presetTable) return presetTable;
    var table = null;
    try {
      var el = document.getElementById('pb-zorp-rig');
      var data = el ? JSON.parse(el.textContent || 'null') : null;
      if (data && data.p && typeof data.p === 'object') {
        table = data.p;
        rigCtx = data.c && typeof data.c === 'object' ? data.c : null;
        rigFxFace = Array.isArray(data.ff) ? data.ff : [];
        if (data.w && typeof data.w === 'object' && data.w.front) rigViews = data.w;
        if (data.m && typeof data.m === 'object') rigVarMap = data.m;
      }
    } catch (e) { table = null; }
    if (table || document.readyState !== 'loading') presetTable = table || LEGACY_PRESETS;
    return table || LEGACY_PRESETS;
  }

  function hasExpression(name) {
    return typeof name === 'string' && Object.prototype.hasOwnProperty.call(presets(), name);
  }

  // 'positive' | 'neutral' | 'negative', or null; prompt consumers refuse 'negative' (docs section 5).
  function valenceOf(name) {
    return hasExpression(name) ? (VAL_WORD[presets()[name][6]] || null) : null;
  }

  // Is this preset in the named allowlist ('guide', 'guide.lore') from the island?
  function allowedIn(context, name) {
    if (!hasExpression(name)) return false;
    presets();
    var list = rigCtx && rigCtx[context];
    if (list) return list.indexOf(name) !== -1;
    return FALLBACK_GUIDE.indexOf(name) !== -1;
  }

  function partNode(channel, id) {
    if (partsTpl === undefined) {
      var tpl = document.getElementById('pb-zorp-parts');
      partsTpl = (tpl && tpl.content) || null;
    }
    if (!partsTpl || !ID_RE.test(id)) return null;
    return partsTpl.querySelector('[data-part="' + channel + ':' + id + '"]');
  }

  function own(obj, key) { return !!obj && Object.prototype.hasOwnProperty.call(obj, key); }

  function viewRow(name) { presets(); return typeof name === 'string' && own(rigViews, name) ? rigViews[name] : null; }

  // undefined: visible, unchanged; 0: hidden; [dx, dy, sx, sy]: resting translate and scale.
  function entryOf(view, key) {
    var row = viewRow(view);
    if (!row) return undefined;
    return own(row, key) ? row[key] : undefined;
  }

  // `translate`/`scale` strings for an entry (`full`: identity written out, for tweens).
  function restVals(e, full) {
    var t = '';
    var sc = '';
    if (e && e !== 0) {
      if (e[0] || e[1]) t = e[0] + 'px ' + e[1] + 'px';
      if (e[2] !== 1 || e[3] !== 1) sc = e[2] + ' ' + e[3];
    }
    if (full) return { t: t || '0px 0px', s: sc || '1 1' };
    return { t: t, s: sc };
  }

  // The variant a view draws for a channel id (side art when it has some).
  function mapId(view, key, id) {
    var by = own(rigVarMap, view) ? rigVarMap[view][SLOT_CHANNEL[key]] : null;
    var to = by && own(by, id) ? by[id] : id;
    return to !== id && partNode(SLOT_CHANNEL[key], to) ? to : id;
  }

  // Channel ids as drawn in a view (fx are not remapped).
  function drawnFor(view, ch) {
    var out = {};
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) {
      var key = SLOT_KEYS[i];
      out[key] = key === 'fx' ? ch[key] : mapId(view, key, ch[key]);
    }
    return out;
  }

  // Channel ids for a preset. The live look's mouth (data-mouth) replaces the nudge mouth only.
  function channelsFor(inst, name) {
    var row = hasExpression(name) ? presets()[name] : null;
    if (!row) return null;
    var ch = {};
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) ch[SLOT_KEYS[i]] = row[i];
    var look = name === 'nudge' && inst ? inst.svg.getAttribute('data-mouth') : null;
    if (look && ID_RE.test(look)) ch.mouth = look;
    return ch;
  }

  function copyChannels(ch) {
    var out = {};
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) out[SLOT_KEYS[i]] = ch[SLOT_KEYS[i]];
    return out;
  }

  function isFaceFx(id) {
    presets();
    return rigFxFace.indexOf(id) !== -1;
  }

  function fillSlot(slot, node) {
    while (slot.firstChild) slot.removeChild(slot.firstChild);
    if (!node) return;
    var kids = node.childNodes;
    var n;
    for (n = 0; n < kids.length; n += 1) slot.appendChild(kids[n].cloneNode(true));
  }

  // fx live in one of two slots: face-attached (moves with the head) or ambient (never mirrored).
  function paintFx(inst, id) {
    var ambient = inst.slots.fx;
    var face = inst.slots.fxFace || ambient;
    var node = partNode('fx', id);
    if (!node || !ambient) return false;
    fillSlot(ambient, null);
    if (face !== ambient) fillSlot(face, null);
    fillSlot(isFaceFx(id) ? face : ambient, node);
    return true;
  }

  // Full-motion swaps: eye squeeze 80 ms, mouth pop 90 ms, cheeks fade 120 ms.
  function swapAnim(slot, key, id) {
    var frames;
    var dur;
    if (key === 'eyeL' || key === 'eyeR') { frames = [{ transform: 'scale(1,0.2)' }, { transform: 'scale(1,1)' }]; dur = 80; }
    else if (key === 'mouth') { frames = [{ transform: 'scale(0.9)' }, { transform: 'scale(1)' }]; dur = 90; }
    else if (key === 'cheeks' && id !== 'none') { frames = [{ opacity: 0 }, { opacity: 1 }]; dur = 120; }
    else return;
    try { slot.animate(frames, { duration: dur, easing: 'ease-out', fill: 'none' }); } catch (e) { /* ignore */ }
  }

  function sameChannels(a, b) {
    var i;
    if (!a || !b) return false;
    for (i = 0; i < SLOT_KEYS.length; i += 1) {
      if (a[SLOT_KEYS[i]] !== b[SLOT_KEYS[i]]) return false;
    }
    return true;
  }

  // data-expr names what is drawn: `hint` when the channels match that preset, else the first
  // matching preset, else 'custom' (channels set one by one).
  function markExpr(inst, hint) {
    if (!inst.cur) return;
    var name = 'custom';
    if (hint && hasExpression(hint) && sameChannels(inst.cur, channelsFor(inst, hint))) name = hint;
    else {
      var names = Object.keys(presets());
      var i;
      for (i = 0; i < names.length; i += 1) {
        if (sameChannels(inst.cur, channelsFor(inst, names[i]))) { name = names[i]; break; }
      }
    }
    inst.svg.setAttribute('data-expr', name);
  }

  // Swap only slots whose drawn variant changed. `inst.cur` = the expression's channels; `inst.drawn` = what this view draws.
  function drawChannels(inst, ch, hint) {
    var next = inst.cur ? copyChannels(inst.cur) : {};
    var animate = canAnimate && motionLevel() === 'full' && rendered(inst);
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) {
      var key = SLOT_KEYS[i];
      var slot = inst.slots[key];
      if (!slot || !ch[key]) continue;
      var id = key === 'fx' ? ch[key] : mapId(inst.view, key, ch[key]);
      if (inst.drawn && inst.drawn[key] === id) { next[key] = ch[key]; continue; }
      if (key === 'fx') {
        if (!paintFx(inst, ch.fx)) continue;
      } else {
        var node = partNode(SLOT_CHANNEL[key], id);
        if (!node) continue;
        fillSlot(slot, node);
        if (animate && entryOf(inst.view, key) !== 0) swapAnim(slot, key, id);
      }
      next[key] = ch[key];
      if (inst.drawn) inst.drawn[key] = id;
    }
    inst.cur = next;
    markExpr(inst, hint);
  }

  function found(svg, a, b) {
    return [svg.querySelector(a), svg.querySelector(b)].filter(Boolean);
  }

  function findViewParts(svg) {
    var out = { flip: svg.querySelector('.zorp-flip') };
    var i;
    for (i = 0; i < VIEW_KEYS.length; i += 1) out[VIEW_KEYS[i]] = svg.querySelector(VIEW_SEL[VIEW_KEYS[i]]);
    return out;
  }

  function findParts(svg) {
    return {
      root: svg.querySelector('.buddy-root'),
      shadow: svg.querySelector('.buddy-shadow'),
      head: svg.querySelector('.buddy-head'),
      body: svg.querySelector('.buddy-body'),
      // back-layer arm + front-layer twin: clips move both
      armL: found(svg, '.buddy-arm--l', '.buddy-arm--l-front'),
      armR: found(svg, '.buddy-arm--r', '.buddy-arm--r-front'),
      antL: svg.querySelector('.buddy-antenna--l'),
      antR: svg.querySelector('.buddy-antenna--r')
    };
  }

  function findSlots(svg) {
    var slots = {};
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) slots[SLOT_KEYS[i]] = svg.querySelector('.zorp-slot--' + SLOT_KEYS[i]);
    slots.fxFace = svg.querySelector('.zorp-slot--fx-face');
    return slots;
  }

  function findInstanceBySvg(svg) {
    for (var i = 0; i < instances.length; i += 1) {
      if (instances[i].svg === svg) return instances[i];
    }
    return null;
  }

  function bind(el) {
    if (!el) return null;
    var svg = (el.matches && el.matches('svg.buddy-mascot')) ? el : el.querySelector('svg.buddy-mascot');
    if (!svg) return null;
    var existing = findInstanceBySvg(svg);
    if (existing) return existing.svg;
    var host = (svg.closest && svg.closest('[data-buddy-face]')) || svg.parentNode;
    var inst = {
      svg: svg,
      host: host,
      parts: findParts(svg),
      slots: findSlots(svg),
      vp: findViewParts(svg),
      view: 'front',
      facing: 'r',
      home: null,
      dirty: false,
      drawn: null,
      cur: null,
      anims: [],
      seq: 0,
      busy: false,
      idle: false,
      faceTimer: 0,
      faceSwap: null,
      gestureTimer: 0,
      gestureResolve: null,
      pulseTimer: 0,
      thought: null
    };
    // What the server drew (data-view, data-facing, data-expr) is the starting point.
    inst.view = viewRow(svg.getAttribute('data-view')) ? svg.getAttribute('data-view') : 'front';
    inst.facing = inst.view !== 'front' && svg.getAttribute('data-facing') === 'l' ? 'l' : 'r';
    inst.cur = channelsFor(inst, svg.getAttribute('data-expr') || 'nudge');
    inst.drawn = drawnFor(inst.view, inst.cur);
    instances.push(inst);
    return svg;
  }

  function getInst(opts) {
    if (opts && opts.el) {
      var svg = bind(opts.el);
      if (!svg) return null;
      return findInstanceBySvg(svg);
    }
    return instances[0] || null;
  }

  // Pupils that are drawn (the far eye in profile is hidden and neither blinks nor animates).
  function visiblePupils(inst) {
    var all = inst.svg.querySelectorAll('.zorp-face .buddy-pupil');
    var out = [];
    var i;
    for (i = 0; i < all.length; i += 1) {
      var hidden = (entryOf(inst.view, 'eyeL') === 0 && all[i].closest('.zorp-slot--eyeL')) ||
        (entryOf(inst.view, 'eyeR') === 0 && all[i].closest('.zorp-slot--eyeR'));
      if (!hidden) out.push(all[i]);
    }
    return out;
  }

  function clearFaceSwap(inst) {
    if (inst.faceTimer) { clearTimeout(inst.faceTimer); inst.faceTimer = 0; }
    inst.faceSwap = null;
  }

  // setExpression('happy') or ({ mouth: 'grin' }): a preset or channel ids merged onto the face; false if unknown.
  function setExpression(input, opts) {
    var inst = getInst(opts);
    if (!inst) return false;
    var ch = null;
    var name = null;
    var i;
    if (typeof input === 'string') {
      name = input;
      ch = channelsFor(inst, name);
    } else if (input && typeof input === 'object') {
      // All-or-nothing: every channel given must name an existing part, else nothing changes.
      ch = inst.cur ? copyChannels(inst.cur) : channelsFor(inst, 'nudge');
      var given = 0;
      if (ch && input.eyes !== undefined) {
        if (typeof input.eyes !== 'string' || !partNode('eyes', input.eyes)) return false;
        ch.eyeL = input.eyes;
        ch.eyeR = partNode('eyes', input.eyes + '-r') ? input.eyes + '-r' : input.eyes;
        given += 1;
      }
      for (i = 0; ch && i < SLOT_KEYS.length; i += 1) {
        var v = input[SLOT_KEYS[i]];
        if (v === undefined) continue;
        if (typeof v !== 'string' || !partNode(SLOT_CHANNEL[SLOT_KEYS[i]], v)) return false;
        ch[SLOT_KEYS[i]] = v;
        given += 1;
      }
      if (!given) return false;
    }
    if (!ch) return false;
    clearFaceSwap(inst);
    drawChannels(inst, ch, name);
    if (name) inst.host.setAttribute('data-face', name);
    return true;
  }

  function setFace(name, opts) {
    return typeof name === 'string' ? setExpression(name, opts) : false;
  }

  function tempFace(inst, face, ms) {
    var ch = channelsFor(inst, face);
    if (!ch) return;
    inst.faceSwap = {
      prev: inst.host.getAttribute('data-face'),
      face: face,
      prevCh: inst.cur ? copyChannels(inst.cur) : null
    };
    inst.host.setAttribute('data-face', face);
    drawChannels(inst, ch, face);
    if (inst.faceTimer) clearTimeout(inst.faceTimer);
    inst.faceTimer = setTimeout(function () { restoreFace(inst); }, ms);
  }

  function restoreFace(inst) {
    var swap = inst.faceSwap;
    if (swap && inst.host.getAttribute('data-face') === swap.face) {
      if (swap.prev) inst.host.setAttribute('data-face', swap.prev);
      else inst.host.removeAttribute('data-face');
      var back = swap.prevCh || channelsFor(inst, swap.prev || 'nudge');
      if (back) drawChannels(inst, back, swap.prev || 'nudge');
    }
    inst.faceSwap = null;
    if (inst.faceTimer) { clearTimeout(inst.faceTimer); inst.faceTimer = 0; }
  }

  // ---- Views (E8 Phase 3) ----

  function setRest(el, key, e) {
    if (!el) return;
    var v = restVals(e === 0 ? undefined : e);
    el.style.display = e === 0 ? 'none' : (FRONT_HIDDEN[key] ? 'inline' : '');
    el.style.translate = v.t;
    el.style.scale = v.s;
  }

  // Write the whole resting view as inline styles. Idempotent: used by stop(), instant view
  // changes and as the fallback when commitStyles() is missing.
  function applyRest(inst) {
    var i;
    for (i = 0; i < VIEW_KEYS.length; i += 1) setRest(inst.vp[VIEW_KEYS[i]], VIEW_KEYS[i], entryOf(inst.view, VIEW_KEYS[i]));
    if (inst.vp.flip) inst.vp.flip.style.scale = inst.facing === 'l' ? '-1 1' : '';
    if (inst.view === 'front') inst.svg.removeAttribute('data-view');
    else inst.svg.setAttribute('data-view', inst.view);
    if (inst.facing === 'l') inst.svg.setAttribute('data-facing', 'l');
    else inst.svg.removeAttribute('data-facing');
  }

  // Draw the variants the current view uses for the current expression (no animation).
  function redrawView(inst) {
    if (!inst.cur) return;
    var want = drawnFor(inst.view, inst.cur);
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) {
      var key = SLOT_KEYS[i];
      if (key === 'fx' || !inst.slots[key] || inst.drawn[key] === want[key]) continue;
      var node = partNode(SLOT_CHANNEL[key], want[key]);
      if (!node) continue;
      fillSlot(inst.slots[key], node);
      inst.drawn[key] = want[key];
    }
  }

  function setView(inst, view, facing) {
    inst.view = view;
    inst.facing = facing;
    redrawView(inst);
    applyRest(inst);
  }

  // Pinch-turn: root dip, mirror pinched to 0.15 by 45%, new view committed at 50%, overshoot, settle.
  // Moving parts tween translate/scale and end with commitStyles() (applyRest() if unavailable).
  // Resolves true on arrival, false if stop() or a newer clip cut it short.
  function turnRun(inst, view, facing, spd) {
    var seq = inst.seq;
    var dur = TURN_MS / spd;
    var s0 = inst.facing === 'l' ? -1 : 1;
    var s1 = facing === 'l' ? -1 : 1;
    var made = [];
    var keep = [];
    var k;
    inst.dirty = true;
    function add(el, frames, o, hold) {
      if (!el) return;
      o.duration = o.duration || dur;
      o.easing = 'linear';
      o.fill = hold ? 'forwards' : 'none';
      if (!hold && HAS_COMPOSITE) o.composite = 'add';
      var a = el.animate(kf(frames), o);
      made.push(a);
      if (hold) keep.push(a);
    }
    for (k = 0; k < VIEW_KEYS.length; k += 1) {
      var a0 = entryOf(inst.view, VIEW_KEYS[k]);
      var b0 = entryOf(view, VIEW_KEYS[k]);
      if (a0 === 0 || b0 === 0) continue;   // shown or hidden at the commit
      var va = restVals(a0, true);
      var vb = restVals(b0, true);
      if (va.t === vb.t && va.s === vb.s) continue;
      add(inst.vp[VIEW_KEYS[k]], [[0, va], [0.15, va], [0.45, vb], [1, vb]].map(function (f) {
        return { offset: f[0], translate: f[1].t, scale: f[1].s };
      }), {}, true);
    }
    // flip: [offset, scaleX, easing]; root dip: [offset, transform]; antennae lag by ANT_LAG_MS
    add(inst.vp.flip, [[0, s0, 'ease-in'], [0.15, s0, 'ease-in'], [0.45, s0 * 0.15, 'linear'], [0.55, s1 * 0.15, 'ease-out'],
      [0.8, s1 * 1.04, 'ease-in-out'], [1, s1]].map(function (f) {
      return { offset: f[0], scale: f[1] + ' 1', easing: f[2] };
    }), {}, true);
    add(inst.parts.root, [[0, '1,1'], [0.15, '1.04,0.96'], [0.5, '1,1'], [0.8, '0.99,1.02'], [1, '1,1']].map(function (f) {
      return { offset: f[0], transform: 'scale(' + f[1] + ')' };
    }), {}, false);
    [inst.parts.antL, inst.parts.antR].forEach(function (ant) {
      add(ant, [0, s1 > 0 ? -6 : 6, 0].map(function (deg, i) {
        return { offset: i / 2, transform: 'rotate(' + deg + 'deg)' };
      }), { delay: ANT_LAG_MS / spd, duration: dur - ANT_LAG_MS / spd }, false);
    });
    // The 50% commit rides on a half-length animation, so it stays in step with the document
    // timeline (pausing or slowing the animations moves it too).
    var clock = inst.vp.flip.animate([{ opacity: 1 }, { opacity: 1 }], { duration: dur / 2 });
    made.push(clock);
    clock.finished.then(function () {
      if (inst.seq === seq) setView(inst, view, facing);
    }, function () { /* cancelled */ });
    inst.anims = inst.anims.concat(made);
    return Promise.all(made.map(function (a) { return a.finished.catch(function () {}); })).then(function () {
      if (inst.seq !== seq) return false;
      var committed = keep.length > 0;
      keep.forEach(function (a) {
        try { a.commitStyles(); } catch (e) { committed = false; }
        try { a.cancel(); } catch (e2) { /* ignore */ }
      });
      if (!committed) applyRest(inst);
      inst.anims = [];
      inst.dirty = false;
      inst.busy = false;
      return true;
    });
  }

  // turn('side', 'l'): full = pinch-turn; reduced = instant only with opts.required; off = stays front.
  // Returning to front is always allowed.
  function turn(view, facing, opts) {
    opts = opts || {};
    var inst = getInst(opts);
    if (!inst || !HAS_PROPS || !viewRow(view) || !inst.vp.flip) return Promise.resolve(false);
    var face = view !== 'front' && facing === 'l' ? 'l' : 'r';
    // dirty = a turn in flight (inst.view is still the old one): stop it first
    if (inst.view === view && inst.facing === face && !inst.dirty) return Promise.resolve(true);
    var level = motionLevel();
    if (view !== 'front' && (level === 'off' || (level === 'reduced' && !opts.required))) return Promise.resolve(false);
    stop(inst);
    if (inst.view === view && inst.facing === face) return Promise.resolve(true);
    if (level !== 'full' || !rendered(inst)) {
      setView(inst, view, face);
      return Promise.resolve(true);
    }
    inst.busy = true;
    return turnRun(inst, view, face, opts.speed > 0 && opts.speed < 1 ? opts.speed : 1);
  }

  // A clip in the side view (side-point; point with view:'side'): turn in, clip, turn back.
  // inst.home is the view stop() restores if it is cut short.
  function viewClip(inst, c, opts, spd, face) {
    var seq = inst.seq;
    var home = { view: inst.view, facing: inst.facing };
    inst.home = home;
    return turnRun(inst, 'side', opts.facing === 'l' ? 'l' : 'r', spd).then(function (ok) {
      if (!ok || inst.seq !== seq) return false;
      inst.busy = inst.dirty = true;   // stop() mid-clip must still restore home
      if (face) tempFace(inst, face, c.dur / spd);
      return run(inst, c.tracks(inst.parts, visiblePupils(inst), { target: 'right' }), c.dur / spd);
    }).then(function (ok) {
      if (!ok || inst.seq !== seq) return false;
      inst.busy = true;
      return turnRun(inst, home.view, home.facing, spd);
    }).then(function (ok) {
      if (inst.seq === seq) { inst.home = null; inst.busy = false; }
      return ok === true;
    });
  }

  function stop(inst) {
    inst.seq += 1;
    var i;
    for (i = 0; i < inst.anims.length; i += 1) {
      try { inst.anims[i].cancel(); } catch (e) { /* ignore */ }
    }
    inst.anims = [];
    if (inst.dirty) {
      // A turn or side-view excursion was cut short: settle on the view it left (excursion) or the
      // one the turn had committed, so nothing stays half-mirrored.
      if (inst.home) { inst.view = inst.home.view; inst.facing = inst.home.facing; inst.home = null; redrawView(inst); }
      applyRest(inst);
      inst.dirty = false;
    }
    if (inst.gestureTimer) { clearTimeout(inst.gestureTimer); inst.gestureTimer = 0; }
    if (inst.gestureResolve) {
      var resolveGesture = inst.gestureResolve;
      inst.gestureResolve = null;
      resolveGesture(false);
    }
    inst.host.removeAttribute('data-gesture');
    if (inst.pulseTimer) { clearTimeout(inst.pulseTimer); inst.pulseTimer = 0; }
    if (inst.parts.body) inst.parts.body.classList.remove('is-zorp-pulse');
    if (inst.faceSwap) restoreFace(inst);
    clearThought(inst);
    inst.busy = false;
  }

  function clearThought(inst) {
    if (!inst.thought) return;
    var node = inst.thought.node;
    var anim = inst.thought.anim;
    inst.thought = null;
    if (anim) {
      try { anim.cancel(); } catch (e) { /* ignore */ }
    }
    // Put the current expression's fx back if the bubble is still what the slot shows.
    if (node && node.parentNode === inst.slots.fx) {
      if (!(inst.cur && inst.cur.fx && paintFx(inst, inst.cur.fx))) fillSlot(inst.slots.fx, null);
    }
  }

  function showThought(inst) {
    clearThought(inst);
    var slot = inst.slots.fx;
    var part = partNode('fx', 'thought');
    if (!slot || !part) return;
    fillSlot(slot, part);
    var g = slot.firstElementChild;
    if (!g) return;
    g.style.opacity = '0';
    var entry = { node: g, anim: null };
    inst.thought = entry;
    if (!canAnimate) return;
    try {
      var anim = g.animate(kf([
        { opacity: 0, transform: 'translate(0, 4px)' },
        { offset: 0.2, opacity: 1, transform: 'translate(0, 0)' },
        { offset: 0.75, opacity: 1, transform: 'translate(0, 0)' },
        { opacity: 0, transform: 'translate(0, -3px)' }
      ]), { duration: THOUGHT_MS, easing: 'ease-in-out', fill: 'none' });
      entry.anim = anim;
      anim.finished.then(function () {
        if (inst.thought === entry) clearThought(inst);
      }).catch(function () { /* cancelled — clearThought already handled cleanup */ });
    } catch (e) {
      clearThought(inst);
    }
  }

  function kf(frames) {
    var out = [];
    var i;
    for (i = 0; i < frames.length; i += 1) {
      var frame = {};
      var key;
      for (key in frames[i]) {
        if (Object.prototype.hasOwnProperty.call(frames[i], key)) frame[key] = frames[i][key];
      }
      if (!frame.easing) frame.easing = 'ease-in-out';
      out.push(frame);
    }
    return out;
  }

  function run(inst, tracks, dur) {
    var anims = [];
    var t;
    // Away from the front view, layer the clip on the resting view.
    var add = HAS_COMPOSITE && inst.view !== 'front';
    function go(node, frames) {
      var o = { duration: dur, easing: 'linear', fill: 'none' };
      if (add) o.composite = 'add';
      anims.push(node.animate(kf(frames), o));
    }
    for (t = 0; t < tracks.length; t += 1) {
      var el = tracks[t][0];
      var frames = tracks[t][1];
      if (!el) continue;
      if (el.length !== undefined && typeof el.animate !== 'function') {
        var n;
        for (n = 0; n < el.length; n += 1) go(el[n], frames);
      } else {
        go(el, frames);
      }
    }
    inst.anims = inst.anims.concat(anims);
    var seq = inst.seq;
    return Promise.all(anims.map(function (a) { return a.finished.catch(function () {}); })).then(function () {
      if (inst.seq === seq) { inst.anims = []; inst.busy = false; }
      return true;
    });
  }

  function delay(inst, ms) {
    var seq = inst.seq;
    return new Promise(function (resolve) {
      setTimeout(function () {
        if (inst.seq === seq) inst.busy = false;
        resolve(true);
      }, ms);
    });
  }

  var CLIPS = {
    blink: {
      dur: 160,
      tracks: function (parts, pupils) {
        return [[pupils, [
          { transform: 'scale(1,1)' },
          { offset: 0.45, transform: 'scale(1,0.1)' },
          { offset: 0.55, transform: 'scale(1,0.1)' },
          { transform: 'scale(1,1)' }
        ]]];
      }
    },
    cheer: {
      dur: 700,
      face: 'celebrate',
      reducedFace: 'celebrate',
      pulse: true,
      tracks: function (parts) {
        return [
          [parts.root, [
            { transform: 'translate(0,0) scale(1,1)' },
            { offset: 0.15, transform: 'translate(0,1px) scale(1.04,0.94)' },
            { offset: 0.45, transform: 'translate(0,-8px) scale(0.97,1.05)' },
            { offset: 0.75, transform: 'translate(0,0) scale(1.06,0.92)' },
            { transform: 'translate(0,0) scale(1,1)' }
          ]],
          [parts.shadow, [
            { transform: 'scale(1,1)', opacity: 1 },
            { offset: 0.45, transform: 'scale(0.7,1)', opacity: 0.5 },
            { offset: 0.75, transform: 'scale(1.1,1)', opacity: 1 },
            { transform: 'scale(1,1)', opacity: 1 }
          ]],
          [parts.armL, [
            { transform: 'rotate(0deg)' },
            { offset: 0.35, transform: 'rotate(115deg)' },
            { offset: 0.75, transform: 'rotate(100deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [parts.armR, [
            { transform: 'rotate(0deg)' },
            { offset: 0.35, transform: 'rotate(-115deg)' },
            { offset: 0.75, transform: 'rotate(-100deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [parts.antL, [
            { transform: 'rotate(0deg)' },
            { offset: 0.45, transform: 'rotate(-14deg)' },
            { offset: 0.8, transform: 'rotate(6deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [parts.antR, [
            { transform: 'rotate(0deg)' },
            { offset: 0.45, transform: 'rotate(14deg)' },
            { offset: 0.8, transform: 'rotate(-6deg)' },
            { transform: 'rotate(0deg)' }
          ]]
        ];
      }
    },
    wobble: {
      dur: 600,
      face: 'nudge',
      reducedFace: 'nudge',
      tracks: function (parts) {
        return [
          [parts.root, [
            { transform: 'rotate(0deg)' },
            { offset: 0.2, transform: 'rotate(6deg)' },
            { offset: 0.45, transform: 'rotate(-5deg)' },
            { offset: 0.65, transform: 'rotate(3deg)' },
            { offset: 0.85, transform: 'rotate(-1.5deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [parts.armR, [
            { transform: 'rotate(0deg)' },
            { offset: 0.3, transform: 'rotate(-25deg)' },
            { offset: 0.7, transform: 'rotate(-25deg)' },
            { transform: 'rotate(0deg)' }
          ]]
        ];
      }
    },
    think: {
      dur: 900,
      face: 'weak_topic',
      reducedFace: 'weak_topic',
      tracks: function (parts, pupils) {
        return [
          [parts.head, [
            { transform: 'rotate(0deg)' },
            { offset: 0.3, transform: 'rotate(-8deg)' },
            { offset: 0.8, transform: 'rotate(-8deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [pupils, [
            { transform: 'translate(0,0)' },
            { offset: 0.25, transform: 'translate(1px,-1.2px)' },
            { offset: 0.85, transform: 'translate(1px,-1.2px)' },
            { transform: 'translate(0,0)' }
          ]],
          [parts.antL, [
            { transform: 'rotate(0deg)' },
            { offset: 0.5, transform: 'rotate(6deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [parts.antR, [
            { transform: 'rotate(0deg)' },
            { offset: 0.5, transform: 'rotate(-6deg)' },
            { transform: 'rotate(0deg)' }
          ]]
        ];
      }
    },
    wave: {
      dur: 900,
      face: 'milestone',
      reducedFace: 'milestone',
      tracks: function (parts) {
        return [
          [parts.armR, [
            { transform: 'rotate(0deg)' },
            { offset: 0.2, transform: 'rotate(-95deg)' },
            { offset: 0.35, transform: 'rotate(-80deg)' },
            { offset: 0.5, transform: 'rotate(-105deg)' },
            { offset: 0.65, transform: 'rotate(-80deg)' },
            { offset: 0.8, transform: 'rotate(-95deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [parts.head, [
            { transform: 'rotate(0deg)' },
            { offset: 0.3, transform: 'rotate(3deg)' },
            { offset: 0.8, transform: 'rotate(3deg)' },
            { transform: 'rotate(0deg)' }
          ]]
        ];
      }
    },
    point: {
      dur: 900,
      face: 'qotd_nudge',
      reducedFace: 'qotd_nudge',
      tracks: function (parts, pupils, opts) {
        var side = { left: 1, right: 1, down: 1 }[opts.target] ? opts.target : 'right';
        if (side === 'left') {
          return [
            [parts.armL, [
              { transform: 'rotate(0deg)' },
              { offset: 0.25, transform: 'rotate(80deg)' },
              { offset: 0.8, transform: 'rotate(80deg)' },
              { transform: 'rotate(0deg)' }
            ]],
            [parts.head, [
              { transform: 'rotate(0deg)' },
              { offset: 0.25, transform: 'rotate(-4deg)' },
              { offset: 0.8, transform: 'rotate(-4deg)' },
              { transform: 'rotate(0deg)' }
            ]],
            [pupils, [
              { transform: 'translate(0,0)' },
              { offset: 0.25, transform: 'translate(-1px,0)' },
              { offset: 0.8, transform: 'translate(-1px,0)' },
              { transform: 'translate(0,0)' }
            ]]
          ];
        }
        if (side === 'down') {
          return [
            [parts.armR, [
              { transform: 'rotate(0deg)' },
              { offset: 0.25, transform: 'rotate(-35deg)' },
              { offset: 0.8, transform: 'rotate(-35deg)' },
              { transform: 'rotate(0deg)' }
            ]],
            [parts.head, [
              { transform: 'rotate(0deg)' },
              { offset: 0.25, transform: 'rotate(6deg)' },
              { offset: 0.8, transform: 'rotate(6deg)' },
              { transform: 'rotate(0deg)' }
            ]],
            [pupils, [
              { transform: 'translate(0,0)' },
              { offset: 0.25, transform: 'translate(0,1px)' },
              { offset: 0.8, transform: 'translate(0,1px)' },
              { transform: 'translate(0,0)' }
            ]]
          ];
        }
        return [
          [parts.armR, [
            { transform: 'rotate(0deg)' },
            { offset: 0.25, transform: 'rotate(-80deg)' },
            { offset: 0.8, transform: 'rotate(-80deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [parts.head, [
            { transform: 'rotate(0deg)' },
            { offset: 0.25, transform: 'rotate(4deg)' },
            { offset: 0.8, transform: 'rotate(4deg)' },
            { transform: 'rotate(0deg)' }
          ]],
          [pupils, [
            { transform: 'translate(0,0)' },
            { offset: 0.25, transform: 'translate(1px,0)' },
            { offset: 0.8, transform: 'translate(1px,0)' },
            { transform: 'translate(0,0)' }
          ]]
        ];
      }
    },
    hop: {
      dur: 450,
      face: 'celebrate',
      reducedFace: 'celebrate',
      tracks: function (parts) {
        return [
          [parts.root, [
            { transform: 'translate(0,0) scale(1,1)' },
            { offset: 0.25, transform: 'translate(0,2px) scale(1.08,0.9)' },
            { offset: 0.6, transform: 'translate(0,-9px) scale(0.94,1.08)' },
            { offset: 0.85, transform: 'translate(0,0) scale(1.05,0.94)' },
            { transform: 'translate(0,0) scale(1,1)' }
          ]],
          [parts.shadow, [
            { transform: 'scale(1,1)', opacity: 1 },
            { offset: 0.6, transform: 'scale(0.75,1)', opacity: 0.55 },
            { offset: 0.85, transform: 'scale(1.05,1)', opacity: 1 },
            { transform: 'scale(1,1)', opacity: 1 }
          ]]
        ];
      }
    },
    // E7 Phase 4: streak-ring peek: slides in from off-screen, head tilt. No face/reducedFace, so
    // reduced motion skips it (play() resolves false for a clip without one).
    peek: {
      dur: 500,
      tracks: function (parts) {
        return [
          [parts.root, [
            { transform: 'translateX(-32px)' },
            { offset: 0.55, transform: 'translateX(2px)' },
            { offset: 0.8, transform: 'translateX(-2px)' },
            { transform: 'translateX(0)' }
          ]],
          [parts.head, [
            { transform: 'rotate(0deg)' },
            { offset: 0.4, transform: 'rotate(-10deg)' },
            { offset: 0.8, transform: 'rotate(-10deg)' },
            { transform: 'rotate(0deg)' }
          ]]
        ];
      }
    },
    // E7 Phase 4: head droop with the real `sleep` preset (offline.html draws it server-side).
    // Same face in reduced motion: a face swap is content, not motion.
    sleep: {
      dur: 1400,
      face: 'sleep',
      reducedFace: 'sleep',
      tracks: function (parts) {
        return [
          [parts.head, [
            { transform: 'rotate(0deg)' },
            { offset: 0.35, transform: 'rotate(12deg)' },
            { offset: 0.85, transform: 'rotate(12deg)' },
            { transform: 'rotate(0deg)' }
          ]]
        ];
      }
    }
  };

  // side-point: turn to the side, point forward, turn back (about 1.1 s). Reduced motion swaps the
  // view instantly (this clip's meaning needs it, docs 2 #5); off stays front.
  CLIPS['side-point'] = {
    dur: 500,
    reducedMs: 1100,
    face: 'curious',
    reducedFace: 'curious',
    tracks: function (parts, pupils) { return CLIPS.point.tracks(parts, pupils, { target: 'right' }); }
  };

  function play(name, opts) {
    opts = opts || {};
    var inst = getInst(opts);
    if (!inst) return Promise.resolve(false);
    if (opts.ifIdle && (inst.busy || inst.thought)) return Promise.resolve(false);
    if (name === 'idle') { idle(true, inst.svg); return Promise.resolve(true); }
    if (CLIP_NAMES.indexOf(name) === -1) return Promise.resolve(false);
    stop(inst);
    inst.busy = true;
    var reduced = motionLevel() !== 'full';
    var faceOverride = hasExpression(opts.face) ? opts.face : null;
    var spd = opts.speed > 0 && opts.speed < 1 ? opts.speed : 1;   // dev slow-motion (styleguide 0.25x)

    if (GESTURES[name]) {
      if (reduced) { inst.busy = false; return Promise.resolve(false); }
      var seq = inst.seq;
      inst.host.removeAttribute('data-gesture');
      void inst.host.getBoundingClientRect();
      inst.host.setAttribute('data-gesture', name);
      return new Promise(function (resolve) {
        inst.gestureResolve = resolve;
        inst.gestureTimer = setTimeout(function () {
          inst.gestureTimer = 0;
          inst.gestureResolve = null;
          if (inst.seq === seq) {
            inst.host.removeAttribute('data-gesture');
            inst.busy = false;
          }
          resolve(true);
        }, GESTURE_MS);
      });
    }

    var c = CLIPS[name];
    if (!c) { inst.busy = false; return Promise.resolve(false); }

    var viewed = (name === 'side-point' || (name === 'point' && opts.view === 'side')) && HAS_PROPS && !!viewRow('side');

    if (reduced) {
      // Thought bubble is a full-motion-only effect — never created here.
      var did = false;
      var hold = (c.reducedMs || c.dur) / spd;
      var rseq = inst.seq;
      var reducedFace = faceOverride || c.reducedFace;
      if (name === 'side-point' && viewed && motionLevel() === 'reduced') {
        inst.home = { view: inst.view, facing: inst.facing };
        inst.dirty = true;
        setView(inst, 'side', opts.facing === 'l' ? 'l' : 'r');
      }
      if (reducedFace && channelsFor(inst, reducedFace)) { tempFace(inst, reducedFace, hold); did = true; }
      if (c.pulse && inst.parts.body) {
        inst.parts.body.classList.add('is-zorp-pulse');
        did = true;
        inst.pulseTimer = setTimeout(function () {
          inst.pulseTimer = 0;
          if (inst.parts.body) inst.parts.body.classList.remove('is-zorp-pulse');
        }, 350);
      }
      return delay(inst, hold).then(function () {
        if (inst.home && inst.seq === rseq) { setView(inst, inst.home.view, inst.home.facing); inst.home = null; inst.dirty = false; }
        return did;
      });
    }

    try {
      var fullFace = faceOverride || c.face;
      if (viewed && inst.vp.flip && rendered(inst)) return viewClip(inst, c, opts, spd, fullFace);
      if (fullFace) tempFace(inst, fullFace, c.dur / spd);
      var promise = run(inst, c.tracks(inst.parts, visiblePupils(inst), opts), c.dur / spd);
      if (opts.thought) showThought(inst);
      return promise;
    } catch (e) {
      stop(inst);
      return Promise.resolve(false);
    }
  }

  function idle(on, el) {
    var list = el ? [getInst({ el: el })].filter(Boolean) : instances;
    list.forEach(function (inst) { inst.idle = !!on; });
    refreshIdle();
    return !!on;
  }

  function rendered(inst) {
    return inst.svg.getClientRects().length > 0;
  }

  function inGuide(inst) {
    return !!(inst.svg.closest && inst.svg.closest('[data-guide-root]'));
  }

  // E7 Phase 4: decorative mascots (data-zorp-autoplay: empty states, streak-ring peek) bind before
  // the corner buddy, so reactTarget() must skip them or answers would animate the wrong mascot.
  function isDecorative(inst) {
    return !!(inst.host && inst.host.hasAttribute && inst.host.hasAttribute('data-zorp-autoplay'));
  }

  function nextCorrectVariant(prev) {
    var pool = CORRECT_VARIANTS.filter(function (name) { return name !== prev; });
    if (!pool.length) pool = CORRECT_VARIANTS.slice();
    return pool[Math.floor(Math.random() * pool.length)];
  }

  function reactTarget() {
    var i;
    for (i = 0; i < instances.length; i += 1) {
      var inst = instances[i];
      if (!inGuide(inst) && !isDecorative(inst) && rendered(inst)) return inst;
    }
    return null;
  }

  function react(kind, opts) {
    opts = opts || {};
    if (motionLevel() === 'off') return Promise.resolve(false);
    if (document.body && document.body.classList.contains('guide-open')) return Promise.resolve(false);
    var known = kind === 'correct' || Object.prototype.hasOwnProperty.call(REACT_CLIP, kind);
    if (!known) return Promise.resolve(false);

    var inst;
    if (opts.el) {
      var svg = bind(opts.el);
      inst = svg ? findInstanceBySvg(svg) : null;
      if (inst && inGuide(inst)) inst = null;
    } else {
      inst = reactTarget();
    }
    if (!inst) return Promise.resolve(false);

    var rare = !!REACT_RARE[kind];
    var now = Date.now();
    if (!rare) {
      if (now - lastReactAt < REACT_GAP_MS) return Promise.resolve(false);
      // A rare reaction that is still playing takes priority — an ordinary correct/wrong/
      // streak reaction arriving right after it must wait rather than cancelling its clip.
      if (now < rareProtectUntil) return Promise.resolve(false);
      lastReactAt = now;
    }

    var clip = kind === 'correct' ? nextCorrectVariant(lastVariant) : REACT_CLIP[kind];
    if (CORRECT_VARIANTS.indexOf(clip) !== -1) lastVariant = clip;

    if (rare) {
      var clipDur = (CLIPS[clip] && CLIPS[clip].dur) || REACT_GAP_MS;
      rareProtectUntil = now + clipDur;
    }

    return play(clip, {
      el: inst.svg,
      face: REACT_FACE[kind],
      thought: kind === 'wrong'
    });
  }

  function refreshIdle() {
    var active = !document.hidden && motionLevel() === 'full';
    var any = false;
    instances.forEach(function (inst) {
      var onNow = inst.idle && active;
      inst.svg.classList.toggle('is-zorp-idle', onNow);
      if (onNow) any = true;
    });
    if (any && !blinkTimer) scheduleBlink();
    else if (!any && blinkTimer) { clearTimeout(blinkTimer); blinkTimer = 0; }
  }

  function scheduleBlink() {
    blinkTimer = setTimeout(function () {
      blinkTimer = 0;
      instances.forEach(function (inst) {
        if (inst.idle && !inst.busy && rendered(inst)) {
          var pupils = visiblePupils(inst);
          if (pupils.length) {
            var n;
            for (n = 0; n < pupils.length; n += 1) {
              try {
                pupils[n].animate(kf([
                  { transform: 'scale(1,1)' },
                  { offset: 0.45, transform: 'scale(1,0.1)' },
                  { offset: 0.55, transform: 'scale(1,0.1)' },
                  { transform: 'scale(1,1)' }
                ]), { duration: 160, easing: 'linear', fill: 'none' });
              } catch (e) { /* ignore */ }
            }
          }
        }
      });
      refreshIdle();
    }, 3000 + Math.random() * 3000);
  }

  document.addEventListener('visibilitychange', refreshIdle);
  if (mq) {
    if (mq.addEventListener) mq.addEventListener('change', refreshIdle);
    else if (mq.addListener) mq.addListener(refreshIdle);
  }

  window.pbZorp = {
    bind: bind,
    play: play,
    idle: idle,
    setFace: setFace,
    setExpression: setExpression,
    turn: turn,
    viewOf: function (el) {
      var inst = getInst({ el: el });
      return inst ? { view: inst.view, facing: inst.facing } : null;
    },
    hasExpression: hasExpression,
    valenceOf: valenceOf,
    allowedIn: allowedIn,
    channelsOf: function (name) { return channelsFor(null, name); },
    motionLevel: motionLevel,
    react: react,
    clips: CLIP_NAMES.slice()
  };
  // View names (front first), read lazily from the island.
  Object.defineProperty(window.pbZorp, 'views', {
    enumerable: true,
    get: function () { presets(); return Object.keys(rigViews); }
  });
  // Preset names, read lazily so they include the island's new presets.
  Object.defineProperty(window.pbZorp, 'expressions', {
    enumerable: true,
    get: function () { return Object.keys(presets()); }
  });
}());
