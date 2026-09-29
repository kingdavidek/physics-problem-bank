/* E7 Phase 1: Zorp motion runtime (docs/MASCOT_MOTION_AND_ONBOARDING.md §3.2).
   WAAPI clips on rig groups; CSS idle loop in static/css/motion.css. No libraries.
   E8 Phase 1 (docs/ZORP_EXPRESSIVENESS.md §4.2-4.4): faces are presets of channels (eyes, brows,
   mouth, cheeks, fx) whose parts are cloned from the inert #pb-zorp-parts template into the
   face slots; presets come from the #pb-zorp-rig data island. */
(function () {
  'use strict';
  if (window.pbZorp) return;

  var CLIP_NAMES = ['idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake', 'hop', 'peek', 'sleep'];
  // E8 Phase 1: preset rows are [eyeL, eyeR, brows, mouth, cheeks, fx, valence]. The island
  // (models/zorp_rig.py rig_json) is read once, lazily; this built-in table keeps the eight
  // legacy faces working if a page has the runtime but not the island.
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

  // Thought bubble (wrong reaction, full-motion only): the `thought` fx part, drawn into the
  // ambient fx slot for THOUGHT_MS and animated with WAAPI (never styled in motion.css).
  var THOUGHT_MS = 1200;
  var VAL_WORD = { '+': 'positive', '0': 'neutral', '-': 'negative' };
  var FALLBACK_GUIDE = ['nudge', 'milestone', 'celebrate', 'qotd_nudge', 'streak_risk', 'weak_topic', 'friend_challenge', 'sleep'];
  var rigCtx = null;   // island "c": context -> allowed preset names
  var rigFxFace = [];  // island "ff": fx ids drawn in the face-attached slot

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
      }
    } catch (e) { table = null; }
    if (table || document.readyState !== 'loading') presetTable = table || LEGACY_PRESETS;
    return table || LEGACY_PRESETS;
  }

  function hasExpression(name) {
    return typeof name === 'string' && Object.prototype.hasOwnProperty.call(presets(), name);
  }

  // 'positive' | 'neutral' | 'negative', or null for an unknown name. Consumers that draw a face
  // for a prompt refuse 'negative' (docs/ZORP_EXPRESSIVENESS.md section 5).
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

  // Short WAAPI swaps (full motion only; the caller has already checked): the new part settles
  // in, an eye from a squeeze (80 ms), a mouth with a pop (90 ms), cheeks with a fade (120 ms).
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

  // Swap only the slots whose variant changed; a missing part leaves that slot as it was.
  function drawChannels(inst, ch, hint) {
    var next = inst.cur ? copyChannels(inst.cur) : {};
    var animate = canAnimate && motionLevel() === 'full' && rendered(inst);
    var i;
    for (i = 0; i < SLOT_KEYS.length; i += 1) {
      var key = SLOT_KEYS[i];
      var slot = inst.slots[key];
      if (!slot || !ch[key] || (inst.cur && inst.cur[key] === ch[key])) continue;
      if (key === 'fx') {
        if (!paintFx(inst, ch.fx)) continue;
      } else {
        var node = partNode(SLOT_CHANNEL[key], ch[key]);
        if (!node) continue;
        fillSlot(slot, node);
        if (animate) swapAnim(slot, key, ch[key]);
      }
      next[key] = ch[key];
    }
    inst.cur = next;
    markExpr(inst, hint);
  }

  function findParts(svg) {
    return {
      root: svg.querySelector('.buddy-root'),
      shadow: svg.querySelector('.buddy-shadow'),
      head: svg.querySelector('.buddy-head'),
      body: svg.querySelector('.buddy-body'),
      armL: svg.querySelector('.buddy-arm--l'),
      armR: svg.querySelector('.buddy-arm--r'),
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
    // What the server drew (data-expr, else the resting face) is the starting point for diffs.
    inst.cur = channelsFor(inst, svg.getAttribute('data-expr') || 'nudge');
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

  function visiblePupils(inst) {
    return inst.svg.querySelectorAll('.zorp-face .buddy-pupil');
  }

  function clearFaceSwap(inst) {
    if (inst.faceTimer) { clearTimeout(inst.faceTimer); inst.faceTimer = 0; }
    inst.faceSwap = null;
  }

  // setExpression('happy') or setExpression({ mouth: 'grin', cheeks: 'rosy' }): a preset name,
  // or channel ids merged onto the current face. Returns false for anything unknown.
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

  function stop(inst) {
    inst.seq += 1;
    var i;
    for (i = 0; i < inst.anims.length; i += 1) {
      try { inst.anims[i].cancel(); } catch (e) { /* ignore */ }
    }
    inst.anims = [];
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
    for (t = 0; t < tracks.length; t += 1) {
      var el = tracks[t][0];
      var frames = tracks[t][1];
      if (!el) continue;
      if (el.length !== undefined && typeof el.animate !== 'function') {
        var n;
        for (n = 0; n < el.length; n += 1) {
          anims.push(el[n].animate(kf(frames), { duration: dur, easing: 'linear', fill: 'none' }));
        }
      } else {
        anims.push(el.animate(kf(frames), { duration: dur, easing: 'linear', fill: 'none' }));
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
    // E7 Phase 4: streak-ring peek — root slides in from off-screen with a head tilt, then
    // settles. No `face`/`reducedFace` (reduced motion skips this clip entirely, per the
    // existing play() branch that resolves `false` for any clip lacking `reducedFace`).
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
    // E7 Phase 4: "sleep" — head droop, held with the real `sleep` preset since E8 Phase 1
    // (closed eyes, sleepy mouth, zzz). templates/offline.html draws the same preset
    // server-side, because zorp-motion.js isn't loaded for anonymous/offline sessions (gated in
    // base.html). Same face for reduced motion: a face swap is content, not motion.
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

    if (reduced) {
      // Thought bubble is a full-motion-only effect — never created here.
      var did = false;
      var reducedFace = faceOverride || c.reducedFace;
      if (reducedFace && channelsFor(inst, reducedFace)) { tempFace(inst, reducedFace, c.dur / spd); did = true; }
      if (c.pulse && inst.parts.body) {
        inst.parts.body.classList.add('is-zorp-pulse');
        did = true;
        inst.pulseTimer = setTimeout(function () {
          inst.pulseTimer = 0;
          if (inst.parts.body) inst.parts.body.classList.remove('is-zorp-pulse');
        }, 350);
      }
      return delay(inst, c.dur / spd).then(function () { return did; });
    }

    try {
      var fullFace = faceOverride || c.face;
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

  // E7 Phase 4: one-off decorative mascots (empty states, streak-ring peek — anything driven
  // by zorp-triggers.js's data-zorp-autoplay) must never be picked as the ambient react()
  // target for correct/wrong/streak/milestone answers. zorp-triggers.js runs (and binds these
  // via play()) before study-buddy.js binds and unhides the corner buddy, so without this
  // check reactTarget()'s "first rendered instance" scan could pick a visible decorative
  // mascot on a page like /profile or the empty-state pages instead of the intended buddy.
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
    hasExpression: hasExpression,
    valenceOf: valenceOf,
    allowedIn: allowedIn,
    channelsOf: function (name) { return channelsFor(null, name); },
    motionLevel: motionLevel,
    react: react,
    clips: CLIP_NAMES.slice()
  };
  // Preset names, read lazily so they include the island's new presets.
  Object.defineProperty(window.pbZorp, 'expressions', {
    enumerable: true,
    get: function () { return Object.keys(presets()); }
  });
}());
