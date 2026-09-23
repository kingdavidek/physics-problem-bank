/* E7 Phase 1: Zorp motion runtime (docs/MASCOT_MOTION_AND_ONBOARDING.md §3.2).
   WAAPI clips on rig groups; CSS idle loop in static/css/motion.css. No libraries. */
(function () {
  'use strict';
  if (window.pbZorp) return;

  var CLIP_NAMES = ['idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake'];
  var FACES = { nudge: 1, milestone: 1, celebrate: 1, qotd_nudge: 1, streak_risk: 1, weak_topic: 1, friend_challenge: 1 };
  var GESTURES = { nod: 1, wink: 1, tap: 1, shake: 1 };   // E6 CSS keyframes via data-gesture
  var GESTURE_MS = 1200;                                    // same as guide.js playGesture
  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var canAnimate = typeof Element !== 'undefined' && typeof Element.prototype.animate === 'function' &&
    typeof Animation !== 'undefined' && 'finished' in Animation.prototype;
  var instances = [];
  var blinkTimer = 0;

  function motionLevel() {
    // 'off' arrives in Phase 5 with data-motion.
    if ((mq && mq.matches) || !canAnimate) return 'reduced';
    return 'full';
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
      anims: [],
      seq: 0,
      busy: false,
      idle: false,
      faceTimer: 0,
      faceSwap: null,
      gestureTimer: 0,
      gestureResolve: null,
      pulseTimer: 0
    };
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
    var face = inst.host.getAttribute('data-face') || 'nudge';
    return inst.svg.querySelectorAll('.buddy-face--' + face.replace(/_/g, '-') + ' .buddy-pupil');
  }

  function setFace(name, opts) {
    var inst = getInst(opts);
    if (!inst || !FACES[name]) return false;
    if (inst.faceTimer) { clearTimeout(inst.faceTimer); inst.faceTimer = 0; }
    inst.faceSwap = null;
    inst.host.setAttribute('data-face', name);
    return true;
  }

  function tempFace(inst, face, ms) {
    var prev = inst.host.getAttribute('data-face');
    inst.host.setAttribute('data-face', face);
    inst.faceSwap = { prev: prev, face: face };
    if (inst.faceTimer) clearTimeout(inst.faceTimer);
    inst.faceTimer = setTimeout(function () { restoreFace(inst); }, ms);
  }

  function restoreFace(inst) {
    if (inst.faceSwap && inst.host.getAttribute('data-face') === inst.faceSwap.face) {
      if (inst.faceSwap.prev) inst.host.setAttribute('data-face', inst.faceSwap.prev);
      else inst.host.removeAttribute('data-face');
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
    inst.busy = false;
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
    }
  };

  function play(name, opts) {
    var inst = getInst(opts);
    if (!inst) return Promise.resolve(false);
    if (name === 'idle') { idle(true, inst.svg); return Promise.resolve(true); }
    if (CLIP_NAMES.indexOf(name) === -1) return Promise.resolve(false);
    stop(inst);
    inst.busy = true;
    var reduced = motionLevel() !== 'full';

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
      var did = false;
      if (c.reducedFace) { tempFace(inst, c.reducedFace, c.dur); did = true; }
      if (c.pulse && inst.parts.body) {
        inst.parts.body.classList.add('is-zorp-pulse');
        did = true;
        inst.pulseTimer = setTimeout(function () {
          inst.pulseTimer = 0;
          if (inst.parts.body) inst.parts.body.classList.remove('is-zorp-pulse');
        }, 350);
      }
      return delay(inst, c.dur).then(function () { return did; });
    }

    try {
      if (c.face) tempFace(inst, c.face, c.dur);
      return run(inst, c.tracks(inst.parts, visiblePupils(inst), opts || {}), c.dur);
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
    motionLevel: motionLevel,
    clips: CLIP_NAMES.slice()
  };
}());
