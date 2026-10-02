/* Zorp motion runtime: WAAPI clips on rig groups (E7); CSS idle loop in static/css/motion.css. No libraries.
   E8 (docs/ZORP_EXPRESSIVENESS.md 4.2-4.4): faces are presets of channels cloned from the inert #pb-zorp-parts
   template into the face slots (presets from the #pb-zorp-rig island); views and the pinch-turn (3.8) are resting
   `translate`/`scale` per part, so clips animate `transform` on top of them.
   E8 Phase 7: idle life (blink, glance, antenna twitch, rare three-quarter look-around), see "Idle life" below. */
(function () {
  'use strict';
  if (window.pbZorp) return;

  var CLIP_NAMES = ['idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake', 'hop', 'peek', 'sleep', 'side-point', 'look-around'];
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
  var reactHook = null;       // zorp-poses.js: (kind, now) -> { clip, face, thought, map, big, dur } | false

  // Thought bubble: the `thought` fx part, full motion only.
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

  function motionLevel() {
    // data-motion (the motion_preference setting) outranks the OS prefers-reduced-motion query.
    var pref = (document.documentElement.getAttribute('data-motion') || 'system');
    // Dev only: static/js/styleguide.js sets data-motion-preview="full" on /styleguide so the clips can be seen with
    // reduced motion on. Nothing else ever sets it.
    if (canAnimate && document.documentElement.getAttribute('data-motion-preview') === 'full') return 'full';
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
  function swapAnim(inst, slot, key, id) {
    var frames;
    var dur;
    if (key === 'eyeL' || key === 'eyeR') { frames = [{ transform: 'scale(1,0.2)' }, { transform: 'scale(1,1)' }]; dur = 80; }
    else if (key === 'mouth') { frames = [{ transform: 'scale(0.9)' }, { transform: 'scale(1)' }]; dur = 90; }
    else if (key === 'cheeks' && id !== 'none') { frames = [{ opacity: 0 }, { opacity: 1 }]; dur = 120; }
    else return;
    once(inst, slot, frames, { duration: dur, easing: 'ease-out' });
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
    var missing = false;
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) {
      var key = SLOT_KEYS[i];
      var slot = inst.slots[key];
      if (!slot || !ch[key]) continue;
      var id = key === 'fx' ? ch[key] : mapId(inst.view, key, ch[key]);
      if (inst.drawn && inst.drawn[key] === id) { next[key] = ch[key]; continue; }
      if (key === 'fx') {
        if (!paintFx(inst, ch.fx)) { missing = true; continue; }
      } else {
        var node = partNode(SLOT_CHANNEL[key], id);
        if (!node) { missing = true; continue; }
        fillSlot(slot, node);
        if (animate && entryOf(inst.view, key) !== 0) swapAnim(inst, slot, key, id);
      }
      next[key] = ch[key];
      if (inst.drawn) inst.drawn[key] = id;
    }
    inst.cur = next;
    markExpr(inst, hint);
    return !missing;   // false when a part has no art (a page without the parts library)
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
      antR: svg.querySelector('.buddy-antenna--r'),
      footL: svg.querySelector('.buddy-foot--l'),
      footR: svg.querySelector('.buddy-foot--r')
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
      vis: true,
      lt: { b: 0, a: 0 },
      look: Date.now(),
      faceTimer: 0,
      faceSwap: null,
      gestureTimer: 0,
      gestureResolve: null,
      pulseTimer: 0,
      thought: null,
      tm: [],
      undo: [],
      pose: svg.getAttribute('data-pose'),
      post: null
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
    var drawn = drawChannels(inst, ch, name);
    if (name && drawn) inst.host.setAttribute('data-face', name);
    return drawn;
  }

  function setFace(name, opts) {
    return typeof name === 'string' ? setExpression(name, opts) : false;
  }

  // A temporary face (optionally with another fx). A second call before the restore keeps the first call's
  // "before" face, so a clip can change expression at beat boundaries and still restore the original.
  function tempFace(inst, face, ms, fx) {
    var ch = channelsFor(inst, face);
    if (!ch) return;
    if (fx) ch.fx = fx;
    var keep = inst.faceSwap;
    inst.faceSwap = {
      prev: keep ? keep.prev : inst.host.getAttribute('data-face'),
      face: face,
      prevCh: keep ? keep.prevCh : (inst.cur ? copyChannels(inst.cur) : null)
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

  // Side view: a plain rest arm is drawn as the profile paddle (arm:side-rest); any other view puts the rest arm back.
  function sideArms(inst) {
    ['L', 'R'].forEach(function (S) {
      (inst.parts['arm' + S] || []).forEach(function (el) {
        var k = el.firstElementChild;
        var cls = k ? (k.getAttribute('class') || '') : 'x';
        var to = inst.view === 'side' ? (cls === '' ? 'side-rest' : '') : (cls === 'zn zsa' ? 'rest' : '');
        var node = to && partNode('arm', to + '-' + S.toLowerCase());
        if (node) fillSlot(el, node);
      });
    });
  }

  // Side-view arm angle for a front-view one: zorp_rig.side_rot (the rule is documented there), same numbers.
  function sideRot(d, shape) {
    if (shape === 'bent') return 0;
    var a = Math.min(Math.abs(d), 180);
    if (a < 70) return a <= 40 ? d : (d < 0 ? -40 : 40);
    var o = +(225 - (a - 70) * 0.4).toFixed(2);
    if (shape === 'fist' || shape === 'bent-fist' || shape === 'reach') o = Math.min(o, 190);
    return d < 0 ? o : -o;
  }

  // A clip's arm tracks as the side view draws them.
  function sideTracks(inst, tracks) {
    if (inst.view !== 'side') return tracks;
    return tracks.map(function (t) {
      if (t[0] !== inst.parts.armL && t[0] !== inst.parts.armR) return t;
      return [t[0], t[1].map(function (f) {
        var o = {};
        for (var k in f) if (own(f, k)) o[k] = f[k];
        o.transform = String(f.transform).replace(/rotate\((-?[\d.]+)deg\)/, function (m, d) { return 'rotate(' + sideRot(+d) + 'deg)'; });
        return o;
      })];
    });
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
    sideArms(inst);
    if (inst.post) inst.post(inst);   // zorp-poses.js: re-apply the resting pose over the view
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

  // commitStyles() writes identity values ("translate: 0px; scale: 1"); drop them so a Zorp turned back to front
  // carries no inline residue.
  function tidy(inst) {
    VIEW_KEYS.concat('flip').forEach(function (k) {
      var st = inst.vp[k] && inst.vp[k].style;
      if (!st) return;
      if (/^(0(px)?\s?){1,2}$/.test(String(st.translate))) st.translate = '';
      if (/^1(\s1)?$/.test(String(st.scale))) st.scale = '';
    });
  }

  // Pinch-turn: root dip, flip pinched to 0.15 by 45%, view committed at 50%, overshoot, settle. Moving parts tween
  // translate/scale and end with commitStyles() (applyRest() if missing). Resolves false if stop() cut it short.
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
    // The 50% commit rides on a half-length animation, so pausing or slowing the timeline moves it too.
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
      tidy(inst);
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
    if (level !== 'full' || opts.instant || !rendered(inst)) {
      setView(inst, view, face);
      return Promise.resolve(true);
    }
    inst.busy = true;
    return turnRun(inst, view, face, opts.speed > 0 && opts.speed < 1 ? opts.speed : 1);
  }

  // A clip in a turned view (side-point and bow: side; point with view:'side'; look-around: three-quarter): turn in, clip, turn back.
  // inst.home is the view stop() restores if it is cut short.
  function viewClip(inst, c, opts, spd, face) {
    var seq = inst.seq;
    var home = { view: inst.view, facing: inst.facing };
    inst.home = home;
    var vw = c.view || 'side';
    return turnRun(inst, vw, opts.facing === 'l' ? 'l' : 'r', spd).then(function (ok) {
      if (!ok || inst.seq !== seq) return false;
      inst.busy = inst.dirty = true;   // stop() mid-clip must still restore home
      if (face) tempFace(inst, face, c.dur / spd);
      var o = { target: opts.target || 'right', trip: opts.trip, facing: opts.facing, view: vw };
      var done = run(inst, c.beats ? c.tracks(inst.parts, visiblePupils(inst), o) : sideTracks(inst, c.tracks(inst.parts, visiblePupils(inst), o)), c.dur / spd);
      if (c.start) c.start(inst, spd, o);
      return done;
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
    inst.tm.forEach(clearTimeout);
    inst.tm = [];
    while (inst.undo.length) inst.undo.pop()();   // beat-clip changes (arm shapes) put back
    if (inst.dirty) {
      // Cut-short turn or side excursion: settle on a whole view, never half-mirrored.
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
    if (inst.slots.fxFace) inst.slots.fxFace.style.display = '';
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
    if (inst.slots.fxFace) inst.slots.fxFace.style.display = 'none';   // a sweat drop or tear never shares the spot
    if (!canAnimate) return;
    try {
      var anim = g.animate(kf([{ opacity: 0, transform: 'translate(0, 4px)' }, { offset: 0.2, opacity: 1, transform: 'translate(0, 0)' },
        { offset: 0.75, opacity: 1, transform: 'translate(0, 0)' }, { opacity: 0, transform: 'translate(0, -3px)' }]),
      { duration: THOUGHT_MS, easing: 'ease-in-out', fill: 'none' });
      entry.anim = anim;
      anim.finished.then(function () {
        if (inst.thought === entry) clearThought(inst);
      }).catch(function () { /* cancelled — clearThought already handled cleanup */ });
    } catch (e) {
      clearThought(inst);
    }
  }

  function kf(frames) {
    return frames.map(function (f) {
      var o = {};
      for (var key in f) if (own(f, key)) o[key] = f[key];
      if (!o.easing) o.easing = 'ease-in-out';
      return o;
    });
  }

  function run(inst, tracks, dur) {
    var anims = [];
    var t;
    // Away from the front view, layer the clip on the resting view.
    var add = HAS_COMPOSITE && (inst.view !== 'front' || (inst.pose && inst.pose !== 'stand'));
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

  // A timer guarded by inst.seq and cleared by stop(): beat-boundary changes (zorp-poses.js).
  function after(inst, ms, fn) {
    var seq = inst.seq;
    inst.tm.push(setTimeout(function () { if (inst.seq === seq) fn(); }, ms));
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

  // Frame helpers for the clip tables (kf() adds the default easing).
  function F(transform, offset) { return offset === undefined ? { transform: transform } : { offset: offset, transform: transform }; }
  var BLINK = [F('scale(1,1)'), F('scale(1,0.1)', 0.45), F('scale(1,0.1)', 0.55), F('scale(1,1)')];

  var CLIPS = {
    blink: { dur: 160, tracks: function (parts, pupils) { return [[pupils, BLINK]]; } },
    cheer: {
      dur: 700,
      face: 'celebrate',
      reducedFace: 'celebrate',
      pulse: true,
      tracks: function (parts) {
        return [
          [parts.root, [F('translate(0,0) scale(1,1)'), F('translate(0,1px) scale(1.04,0.94)', 0.15), F('translate(0,-8px) scale(0.97,1.05)', 0.45),
            F('translate(0,0) scale(1.06,0.92)', 0.75), F('translate(0,0) scale(1,1)')]],
          [parts.shadow, [{ transform: 'translate(0,0) scale(1,1)', opacity: 1 }, { offset: 0.15, transform: 'translate(0,-1px) scale(1,1)', opacity: 1 },
            { offset: 0.45, transform: 'translate(0,8px) scale(0.7,1)', opacity: 0.5 }, { offset: 0.75, transform: 'translate(0,0) scale(1.1,1)', opacity: 1 },
            { transform: 'translate(0,0) scale(1,1)', opacity: 1 }]],
          [parts.armL, [F('rotate(0deg)'), F('rotate(115deg)', 0.35), F('rotate(100deg)', 0.75), F('rotate(0deg)')]],
          [parts.armR, [F('rotate(0deg)'), F('rotate(-115deg)', 0.35), F('rotate(-100deg)', 0.75), F('rotate(0deg)')]],
          [parts.antL, [F('rotate(0deg)'), F('rotate(-14deg)', 0.45), F('rotate(6deg)', 0.8), F('rotate(0deg)')]],
          [parts.antR, [F('rotate(0deg)'), F('rotate(14deg)', 0.45), F('rotate(-6deg)', 0.8), F('rotate(0deg)')]]
        ];
      }
    },
    wobble: {
      dur: 600,
      face: 'nudge',
      reducedFace: 'nudge',
      tracks: function (parts) {
        return [
          [parts.root, [F('rotate(0deg)'), F('rotate(6deg)', 0.2), F('rotate(-5deg)', 0.45), F('rotate(3deg)', 0.65), F('rotate(-1.5deg)', 0.85), F('rotate(0deg)')]],
          [parts.armR, [F('rotate(0deg)'), F('rotate(-25deg)', 0.3), F('rotate(-25deg)', 0.7), F('rotate(0deg)')]]
        ];
      }
    },
    think: {
      dur: 900,
      face: 'weak_topic',
      reducedFace: 'weak_topic',
      tracks: function (parts, pupils) {
        return [
          [parts.head, [F('rotate(0deg)'), F('rotate(-8deg)', 0.3), F('rotate(-8deg)', 0.8), F('rotate(0deg)')]],
          [pupils, [F('translate(0,0)'), F('translate(1px,-1.2px)', 0.25), F('translate(1px,-1.2px)', 0.85), F('translate(0,0)')]],
          [parts.antL, [F('rotate(0deg)'), F('rotate(6deg)', 0.5), F('rotate(0deg)')]],
          [parts.antR, [F('rotate(0deg)'), F('rotate(-6deg)', 0.5), F('rotate(0deg)')]]
        ];
      }
    },
    wave: {
      dur: 900,
      face: 'milestone',
      reducedFace: 'milestone',
      tracks: function (parts) {
        return [
          [parts.armR, [F('rotate(0deg)'), F('rotate(-95deg)', 0.2), F('rotate(-80deg)', 0.35), F('rotate(-105deg)', 0.5), F('rotate(-80deg)', 0.65),
            F('rotate(-95deg)', 0.8), F('rotate(0deg)')]],
          [parts.head, [F('rotate(0deg)'), F('rotate(3deg)', 0.3), F('rotate(3deg)', 0.8), F('rotate(0deg)')]]
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
            [parts.armL, [F('rotate(0deg)'), F('rotate(80deg)', 0.25), F('rotate(80deg)', 0.8), F('rotate(0deg)')]],
            [parts.head, [F('rotate(0deg)'), F('rotate(-4deg)', 0.25), F('rotate(-4deg)', 0.8), F('rotate(0deg)')]],
            [pupils, [F('translate(0,0)'), F('translate(-1px,0)', 0.25), F('translate(-1px,0)', 0.8), F('translate(0,0)')]]
          ];
        }
        if (side === 'down') {
          return [
            [parts.armR, [F('rotate(0deg)'), F('rotate(-35deg)', 0.25), F('rotate(-35deg)', 0.8), F('rotate(0deg)')]],
            [parts.head, [F('rotate(0deg)'), F('rotate(6deg)', 0.25), F('rotate(6deg)', 0.8), F('rotate(0deg)')]],
            [pupils, [F('translate(0,0)'), F('translate(0,1px)', 0.25), F('translate(0,1px)', 0.8), F('translate(0,0)')]]
          ];
        }
        return [
          // in profile sideTracks() lifts the arm over the top, never across the face
          [parts.armR, [F('rotate(0deg)'), F('rotate(-80deg)', 0.25), F('rotate(-80deg)', 0.8), F('rotate(0deg)')]],
          [parts.head, [F('rotate(0deg)'), F('rotate(4deg)', 0.25), F('rotate(4deg)', 0.8), F('rotate(0deg)')]],
          [pupils, [F('translate(0,0)'), F('translate(1px,0)', 0.25), F('translate(1px,0)', 0.8), F('translate(0,0)')]]
        ];
      }
    },
    hop: {
      dur: 450,
      face: 'celebrate',
      reducedFace: 'celebrate',
      tracks: function (parts) {
        return [
          [parts.root, [F('translate(0,0) scale(1,1)'), F('translate(0,2px) scale(1.08,0.9)', 0.25), F('translate(0,-9px) scale(0.94,1.08)', 0.6),
            F('translate(0,0) scale(1.05,0.94)', 0.85), F('translate(0,0) scale(1,1)')]],
          [parts.shadow, [{ transform: 'translate(0,0) scale(1,1)', opacity: 1 }, { offset: 0.25, transform: 'translate(0,-2px) scale(1,1)', opacity: 1 },
            { offset: 0.6, transform: 'translate(0,9px) scale(0.75,1)', opacity: 0.55 }, { offset: 0.85, transform: 'translate(0,0) scale(1.05,1)', opacity: 1 },
            { transform: 'translate(0,0) scale(1,1)', opacity: 1 }]]
        ];
      }
    },
    // Streak-ring peek: no face/reducedFace, so reduced motion skips it.
    peek: {
      dur: 500,
      tracks: function (parts) {
        return [
          [parts.root, [F('translateX(-32px)'), F('translateX(2px)', 0.55), F('translateX(-2px)', 0.8), F('translateX(0)')]],
          [parts.head, [F('rotate(0deg)'), F('rotate(-10deg)', 0.4), F('rotate(-10deg)', 0.8), F('rotate(0deg)')]]
        ];
      }
    },
    // Head droop with the real `sleep` preset (offline.html draws it server-side); a face swap is content, so reduced keeps it.
    sleep: {
      dur: 1400,
      face: 'sleep',
      reducedFace: 'sleep',
      tracks: function (parts) {
        return [[parts.head, [F('rotate(0deg)'), F('rotate(12deg)', 0.35), F('rotate(12deg)', 0.85), F('rotate(0deg)')]]];
      }
    }
  };

  // side-point: turn to the side, point, turn back (about 1.1 s). Reduced motion swaps the view
  // instantly (this clip's meaning needs it, docs 2 #5); off stays front.
  CLIPS['side-point'] = {
    dur: 500,
    reducedMs: 1100,
    view: 'side',
    needView: 1,
    face: 'curious',
    reducedFace: 'curious',
    tracks: function (parts, pupils, opts) { return CLIPS.point.tracks(parts, pupils, { target: (opts || {}).target, view: 'side' }); }
  };

  // look-around: the idle life's rare glance over the shoulder. It keeps the expression, and reduced motion skips it.
  CLIPS['look-around'] = {
    dur: 1000,
    view: 'three-quarter',
    tracks: function (parts, pupils) {
      return [[pupils, [F('translate(0,0)'), F('translate(1.2px,-.3px)', 0.25), F('translate(1.2px,-.3px)', 0.8), F('translate(0,0)')]],
        [parts.head, [F('rotate(0deg)'), F('rotate(3deg)', 0.25), F('rotate(3deg)', 0.8), F('rotate(0deg)')]]];
    }
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
    if (c.custom) return c.custom(inst, opts, spd);

    var viewed = !!(c.view || (name === 'point' && opts.view === 'side')) && HAS_PROPS && !!viewRow(c.view || 'side');

    if (reduced) {
      // Thought bubble is a full-motion-only effect — never created here.
      var did = false;
      var hold = (c.reducedMs || c.dur) / spd;
      var rseq = inst.seq;
      var reducedFace = faceOverride || c.reducedFace;
      if (c.needView && viewed && motionLevel() === 'reduced') {
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
      if (c.pre) c.pre(inst, opts);   // zorp-poses.js: a beat clip starts from the standing pose
      var fullFace = faceOverride || c.face;
      if (viewed && inst.vp.flip && rendered(inst)) return viewClip(inst, c, opts, spd, fullFace);
      if (fullFace) tempFace(inst, fullFace, c.dur / spd);
      // beat clips mirror the root (outside the flip) by the facing Zorp already has
      var promise = run(inst, c.beats ? c.tracks(inst.parts, visiblePupils(inst), { trip: opts.trip, facing: inst.facing, view: inst.view })
        : sideTracks(inst, c.tracks(inst.parts, visiblePupils(inst), opts)), c.dur / spd);
      if (c.start) c.start(inst, spd, opts);
      if (opts.thought) showThought(inst);
      return promise;
    } catch (e) {
      stop(inst);
      return Promise.resolve(false);
    }
  }

  function idle(on, el) {
    var list = el ? [getInst({ el: el })].filter(Boolean) : instances;
    list.forEach(function (inst) { inst.idle = !!on; watch(inst, !!on); });
    refreshIdle();
    return !!on;
  }

  function rendered(inst) {
    return inst.svg.getClientRects().length > 0;
  }

  function inGuide(inst) {
    return !!(inst.svg.closest && inst.svg.closest('[data-guide-root]'));
  }

  // data-zorp-autoplay mascots bind first: reactTarget() skips them.
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
      // A rare reaction still playing takes priority: a gated one right after it must wait.
      if (now < rareProtectUntil) return Promise.resolve(false);
      lastReactAt = now;
    }

    var plan = reactHook ? reactHook(kind, now) : null;
    if (plan === false) return Promise.resolve(false);
    var clip = plan ? plan.clip : kind === 'correct' ? nextCorrectVariant(lastVariant) : REACT_CLIP[kind];
    if (CORRECT_VARIANTS.indexOf(clip) !== -1) lastVariant = clip;

    if (rare || (plan && plan.big)) {
      var clipDur = (plan && plan.dur) || (CLIPS[clip] && CLIPS[clip].dur) || REACT_GAP_MS;
      rareProtectUntil = now + clipDur;
    }

    return play(clip, {
      el: inst.svg,
      face: plan ? plan.face : REACT_FACE[kind],
      thought: plan ? !!plan.thought : kind === 'wrong',
      map: plan && plan.map
    });
  }

  // ---- Idle life (E8 Phase 7, docs 4.4) ----
  // Only at full motion, visible, on screen, with nothing running, and never while someone is typing or has just
  // pressed a key or tapped. Per Zorp: a blink every 3-6 s; every 6-14 s one of a pupil glance, an antenna twitch or
  // (at least 45 s apart, rarely) a three-quarter look-around. One timer per stream, random delays, so mascots never
  // move in step. WAAPI one-shots, no frame loop. The expression never changes here.
  var io = null;
  var lastInput = 0;
  var QUIET_MS = 2500;
  var LOOK_GAP_MS = 45000;

  function rnd(lo, hi) { return lo + Math.random() * (hi - lo); }

  // A short tracked animation: stop() cancels it, and it leaves inst.anims when it ends.
  function once(inst, el, frames, o) {
    try {
      o.fill = 'none';
      var a = el.animate(frames, o);
      var drop = function () { var i = inst.anims.indexOf(a); if (i !== -1) inst.anims.splice(i, 1); };
      inst.anims.push(a);
      a.finished.then(drop, drop);
    } catch (e) { /* ignore */ }
  }

  function typing() {
    var el = document.activeElement;
    return !!el && (/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName) || el.isContentEditable === true);
  }

  function mayLive(inst) {
    return inst.idle && inst.vis && !document.hidden && motionLevel() === 'full';
  }

  function lively(inst) {
    var body = document.body;
    return mayLive(inst) && rendered(inst) && !inst.busy && !inst.dirty && !inst.thought && !inst.faceSwap && !inst.anims.length &&
      inst.view === 'front' && (!inst.pose || inst.pose === 'stand') && !typing() && Date.now() - lastInput > QUIET_MS &&
      !(body && body.classList.contains('guide-open'));
  }

  function blink(inst) {
    visiblePupils(inst).forEach(function (el) { once(inst, el, kf(BLINK), { duration: 160, easing: 'linear' }); });
  }

  function glance(inst) {
    var v = 'translate(' + (Math.random() < 0.5 ? -1 : 1) * rnd(0.9, 1.3).toFixed(1) + 'px,' + rnd(-1, 0.4).toFixed(1) + 'px)';
    visiblePupils(inst).forEach(function (el) {
      once(inst, el, kf([F('translate(0,0)'), F(v, 0.2), F(v, 0.7), F('translate(0,0)')]), { duration: rnd(900, 1500), easing: 'linear' });
    });
  }

  // One antenna flicks; composite:'add' keeps it on top of the CSS sway.
  function twitch(inst) {
    var left = Math.random() < 0.5;
    var s = left ? -1 : 1;
    var o = { duration: 520, easing: 'linear' };
    if (HAS_COMPOSITE) o.composite = 'add';
    if (inst.parts[left ? 'antL' : 'antR']) {
      once(inst, inst.parts[left ? 'antL' : 'antR'], kf([F('rotate(0deg)'), F('rotate(' + 9 * s + 'deg)', 0.25), F('rotate(' + -4 * s + 'deg)', 0.5),
        F('rotate(' + 5 * s + 'deg)', 0.75), F('rotate(0deg)')]), o);
    }
  }

  function act(inst) {
    var r = Math.random();
    var now = Date.now();
    if (r < 0.12 && now - inst.look > LOOK_GAP_MS) {
      inst.look = now;
      play('look-around', { el: inst.svg, ifIdle: true, facing: Math.random() < 0.5 ? 'l' : 'r' });
    } else if (r < 0.35) twitch(inst);
    else glance(inst);
  }

  function lifeLoop(inst, key, lo, hi, fn) {
    inst.lt[key] = setTimeout(function () {
      inst.lt[key] = 0;
      if (!mayLive(inst)) return;   // refreshIdle() starts it again when Zorp may live again
      if (lively(inst)) fn(inst);
      lifeLoop(inst, key, lo, hi, fn);
    }, rnd(lo, hi));
  }

  function refreshIdle() {
    instances.forEach(function (inst) {
      var on = mayLive(inst);
      inst.svg.classList.toggle('is-zorp-idle', on);
      if (!on) {
        ['b', 'a'].forEach(function (k) { if (inst.lt[k]) { clearTimeout(inst.lt[k]); inst.lt[k] = 0; } });
        return;
      }
      if (!inst.lt.b) lifeLoop(inst, 'b', 3000, 6000, blink);
      if (!inst.lt.a) lifeLoop(inst, 'a', 6000, 14000, act);
    });
  }

  // Off-screen mascots neither animate nor keep timers.
  function watch(inst, on) {
    if (typeof IntersectionObserver === 'undefined') return;
    if (!io) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var i = findInstanceBySvg(e.target);
          if (i) i.vis = e.isIntersecting;
        });
        refreshIdle();
      });
    }
    if (on) io.observe(inst.svg);
    else { io.unobserve(inst.svg); inst.vis = true; }
  }

  ['keydown', 'pointerdown'].forEach(function (type) {
    document.addEventListener(type, function () { lastInput = Date.now(); }, { capture: true, passive: true });
  });
  if (typeof MutationObserver !== 'undefined') {
    new MutationObserver(refreshIdle).observe(document.documentElement, { attributes: true, attributeFilter: ['data-motion', 'data-motion-preview'] });
  }

  document.addEventListener('visibilitychange', function () { if (document.hidden) instances.forEach(stop); refreshIdle(); });
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
    hasClip: function (name) { return CLIP_NAMES.indexOf(name) !== -1; },
    // Stubs until zorp-poses.js replaces them.
    pose: function () { return Promise.resolve(false); },
    hasPose: function () { return false; },
    poses: [],
    // zorp-poses.js calls register(fn) with the runtime internals.
    register: function (fn) {
      fn({ clips: CLIPS, names: CLIP_NAMES, level: motionLevel, inst: getInst, stop: stop, own: own,
        tempFace: tempFace, after: after, thought: showThought, node: partNode, fill: fillSlot, turn: turn, rendered: rendered,
        setExpression: setExpression, rest: applyRest, side: sideArms, sideRot: sideRot,
        react: function (fn) { reactHook = fn; } });
    }
  };
  // Clip names, read at call time so registered clips are included.
  Object.defineProperty(window.pbZorp, 'clips', { enumerable: true, get: function () { return CLIP_NAMES.slice(); } });
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
