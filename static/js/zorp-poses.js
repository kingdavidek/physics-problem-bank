/* Zorp poses, arm shapes and the beat engine (E8 Phase 4, docs/ZORP_EXPRESSIVENESS.md 3.9 to 3.11).
   Loaded after zorp-motion.js under the same guard and joined to it through pbZorp.register(fn); without this
   file everything from Phases 1 to 3 works and the new names simply report hasClip/hasPose false.
   Adds pbZorp.pose(name, opts), .poses, .hasPose, .compileBeats(beats, parts, opts), .clipInfo(name) and the
   clips fist-pump, victory, flex, shrug, bow, think-chin, dance, float, oops-encourage and turn.
   A clip is a `beats` array [{pose, expr, fx, ms, hold, ease, aease, y, dx, r, hr, s}]. compileBeats() turns it
   into ONE keyframe list per moving part, so each part still gets exactly one el.animate() and stop() works
   as for every other clip. Expression, fx and arm-shape changes at beat boundaries are timers guarded by
   inst.seq (rt.after) that stop() clears and undoes. Only `transform` and `opacity` animate; views use the
   `translate`/`scale` properties, so poses and views compose. */
(function () {
  'use strict';
  var pb = window.pbZorp;
  if (!pb || typeof pb.register !== 'function' || pb.hasPose('stand')) return;

  // Pose rows, from models/zorp_rig.py poses_json(); scripts/test_zorp_poses_smoke.py fails when they differ.
  // r root [dx dy rot sx sy], h head [dx dy rot], L/R arm [shape rot front], fl/fr feet [dx dy rot], s shadow [sx opacity].
  /*POSES-BEGIN*/
  var POSES = {"stand":{"r":[0,0,0,1,1],"h":[0,0,0],"L":["rest",0,0],"R":["rest",0,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"front","e":"nudge"},"wave":{"r":[0,0,0,1,1],"h":[0,0,3],"L":["rest",0,0],"R":["straight",-100,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"milestone"},"point-l":{"r":[0,0,0,1,1],"h":[0,0,-4],"L":["straight",82,0],"R":["rest",0,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"qotd_nudge"},"point-r":{"r":[0,0,0,1,1],"h":[0,0,4],"L":["rest",0,0],"R":["straight",-82,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"qotd_nudge"},"point-down":{"r":[0,0,0,1,1],"h":[0,0,6],"L":["rest",0,0],"R":["straight",-35,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"qotd_nudge"},"fist-up":{"r":[0,0,4,1,1],"h":[0,0,0],"L":["rest",0,0],"R":["fist",-165,1],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"grin"},"victory":{"r":[0,0,0,1,1.02],"h":[0,0,0],"L":["fist",160,1],"R":["fist",-160,1],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"joy"},"flex":{"r":[0,0,0,1,1.03],"h":[0,0,0],"L":["rest",0,0],"R":["bent-fist",-90,1],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"proud"},"think-chin":{"r":[0,0,0,1,1],"h":[0,0,-6],"L":["rest",0,0],"R":["bent",0,1],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"thinking"},"shrug":{"r":[0,0,0,1,0.96],"h":[0,0,5],"L":["straight",62,0],"R":["straight",-62,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"soft-smile"},"bow":{"r":[0,0,18,1,1],"h":[0,0,0],"L":["rest",0,0],"R":["rest",0,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"side","e":"bashful"},"peek":{"r":[-8,0,0,1,1],"h":[0,0,-10],"L":["rest",0,0],"R":["rest",0,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"nudge"},"crouch":{"r":[0,3,0,1.11,0.89],"h":[0,0,0],"L":["rest",14,0],"R":["rest",-14,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"determined"},"dance-a":{"r":[0,0,6,1,1],"h":[0,0,0],"L":["straight",130,0],"R":["rest",0,0],"fl":[0,0,0],"fr":[0,-3,0],"s":[1,1],"v":"","e":"laugh"},"dance-b":{"r":[0,0,-6,1,1],"h":[0,0,0],"L":["rest",0,0],"R":["straight",-130,0],"fl":[0,-3,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"laugh"},"sit":{"r":[0,3,0,1,0.95],"h":[0,0,0],"L":["rest",0,0],"R":["rest",0,0],"fl":[3,-1,0],"fr":[3,-1,0],"s":[1,1],"v":"side","e":"happy"},"float":{"r":[0,-8,0,1,1],"h":[0,0,0],"L":["rest",0,0],"R":["rest",0,0],"fl":[0,0,-8],"fr":[0,0,8],"s":[0.7,0.6],"v":"","e":"happy"},"sleep":{"r":[0,1.5,0,1,0.98],"h":[0,0,12],"L":["rest",0,0],"R":["rest",0,0],"fl":[0,0,0],"fr":[0,0,0],"s":[1,1],"v":"","e":"sleep"}};
  /*POSES-END*/

  var EASE = { out: 'cubic-bezier(.2,.8,.2,1)', 'in': 'cubic-bezier(.6,0,.9,.4)', overshoot: 'cubic-bezier(.34,1.56,.64,1)', io: 'ease-in-out' };
  var LAG = { head: 40, armL: 30, armR: 30 };   // follow-through: these parts trail the root by this many ms
  var ANT_LAG = 80;                             // antennae trail by 80 ms and overshoot
  var TAIL = 80;                                // every beat clip ends with this settle so the lagging parts arrive
  var POSE_MS = 240;                            // pbZorp.pose() transition
  var KEYS = ['root', 'shadow', 'head', 'armL', 'armR', 'footL', 'footR'];
  var HAS_PROPS = (function () { try { return !!(window.CSS && CSS.supports && CSS.supports('translate', '1px')); } catch (e) { return false; } }());

  pb.register(function (rt) {
    var num = function (x) { return String(+(+x).toFixed(2)); };

    // A pose row plus a beat's overrides as per-part values; facing left mirrors the root (it sits outside the flip).
    function stateOf(p, b, facing, view) {
      b = b || {};
      var r = p.r.slice();
      r[0] += b.dx || 0; r[1] += b.y || 0; r[2] += b.r || 0;
      if (b.s) { r[3] = b.s[0]; r[4] = b.s[1]; }
      if (facing === 'l') { r[0] = -r[0]; r[2] = -r[2]; }
      // The shadow stays on the ground: it counters the root's dy, and shrinks a little with a beat's own lift.
      var lift = Math.max(0, -(b.y || 0));
      var sh = [p.s[0] * (1 - Math.min(0.25, 0.015 * lift)), p.s[1] * (1 - Math.min(0.3, 0.02 * lift)), -r[1]];
      var arm = function (a) { return view === 'side' ? rt.sideRot(a[1], a[0]) : a[1]; };   // profile: raised arms lift over the top
      return { root: r, head: [p.h[0], p.h[1], p.h[2] + (b.hr || 0)], armL: arm(p.L), armR: arm(p.R), footL: p.fl, footR: p.fr, shadow: sh };
    }

    function tf(key, v) {
      if (key === 'root') return 'translate(' + num(v[0]) + 'px,' + num(v[1]) + 'px) rotate(' + num(v[2]) + 'deg) scale(' + num(v[3]) + ',' + num(v[4]) + ')';
      if (key === 'armL' || key === 'armR' || key === 'antL' || key === 'antR') return 'rotate(' + num(v) + 'deg)';
      if (key === 'shadow') return 'translate(0,' + num(v[2]) + 'px) scale(' + num(v[0]) + ',1)';
      return 'translate(' + num(v[0]) + 'px,' + num(v[1]) + 'px) rotate(' + num(v[2]) + 'deg)';
    }

    var STAND = stateOf(POSES.stand, null, 'r');
    var IDENT = {};
    KEYS.forEach(function (k) { IDENT[k] = tf(k, STAND[k]); });

    function poseRow(name) { return rt.own(POSES, name) ? POSES[name] : null; }

    function elsOf(inst, key) {
      if (key === 'armL' || key === 'armR') return inst.parts[key];
      if (key === 'footL' || key === 'footR') return [inst.parts[key]];
      return [inst.parts[key]];
    }

    // ---- arm shapes ----
    function shapeOf(inst, side) { return inst.shape[side]; }

    // The art a shape draws in the current view (zorp_rig SIDE_ARMS; the rest paddle is swapped by rt.side).
    var SIDE_ART = { bent: 'side-bent', 'bent-fist': 'fist' };
    function artOf(inst, shape) { return inst.view === 'side' && rt.own(SIDE_ART, shape) ? SIDE_ART[shape] : shape; }

    function setShape(inst, side, shape, force) {
      if (inst.shape[side] === shape && !force) return;
      var pair = inst.parts['arm' + side];
      var node = rt.node('arm', artOf(inst, shape) + '-' + side.toLowerCase());
      if (!node) return;
      pair.forEach(function (el) { rt.fill(el, node); });
      inst.shape[side] = shape;
      if (inst.view === 'side') rt.side(inst);   // a rest arm is the profile paddle in the side view
    }

    function init(inst) {
      if (inst.zp) return;
      inst.zp = 1;
      var row = poseRow(inst.pose) || POSES.stand;
      inst.pose = poseRow(inst.pose) ? inst.pose : 'stand';
      inst.ps = stateOf(row, null, inst.facing, inst.view);
      inst.shape = { L: row.L[0], R: row.R[0] };
      inst.post = frontArms;
    }

    // After every view change: redraw the resting pose for the new view and facing (profile arm angles, mirrored root).
    // A front-flag arm (think-chin) draws its front-layer twin over the body; views reset display, so re-apply after them.
    function frontArms(inst) {
      var row = poseRow(inst.pose);
      if (!row) return;
      inst.ps = stateOf(row, null, inst.facing, inst.view);
      KEYS.forEach(function (k) { paint(inst, k, inst.ps[k]); });
      ['L', 'R'].forEach(function (S) { if (rt.own(SIDE_ART, inst.shape[S])) setShape(inst, S, inst.shape[S], 1); });
      if (inst.view === 'side') return;
      ['L', 'R'].forEach(function (S) {
        if (!row[S][2]) return;
        inst.vp['arm' + S].style.display = 'none';
        inst.vp['arm' + S + 'f'].style.display = 'inline';
      });
    }

    // Keep data-pose in step with the resting pose, like data-view (the default stand carries no attribute).
    function mark(inst) {
      if (inst.pose === 'stand') inst.svg.removeAttribute('data-pose');
      else inst.svg.setAttribute('data-pose', inst.pose);
    }

    // Show one arm's front-layer twin over the body (front view only; other views decide their own layers).
    function layer(inst, S, on) {
      if (inst.view !== 'front') return;
      inst.vp['arm' + S].style.display = on ? 'none' : '';
      inst.vp['arm' + S + 'f'].style.display = on ? 'inline' : 'none';
    }

    function paint(inst, key, v) {
      var str = tf(key, v);
      elsOf(inst, key).forEach(function (el) {
        if (!el) return;
        el.style.transform = str === IDENT[key] ? '' : str;
        if (key === 'shadow') el.style.opacity = v[1] === 1 ? '' : String(v[1]);
      });
    }

    // Set the resting pose instantly (transform, opacity, shapes, front arms).
    function applyPose(inst, name, facing) {
      var row = poseRow(name) || POSES.stand;
      var st = stateOf(row, null, facing, inst.view);
      KEYS.forEach(function (k) { paint(inst, k, st[k]); });
      setShape(inst, 'L', row.L[0]);
      setShape(inst, 'R', row.R[0]);
      inst.pose = poseRow(name) ? name : 'stand';
      inst.ps = st;
      mark(inst);
      rt.rest(inst);
    }

    // Animate from the current resting state to a pose. The end state is written inline first, so a cancelled
    // animation (stop()) leaves the pose in place; the tween itself never uses composite:'add'.
    function poseTo(inst, name, facing, spd) {
      var row = POSES[name];
      var from = inst.ps;
      var to = stateOf(row, null, facing, inst.view);
      var seq = inst.seq;
      var made = [];
      inst.busy = true;
      KEYS.forEach(function (k) {
        var a = tf(k, from[k]);
        var b = tf(k, to[k]);
        var fa = { transform: a };
        var fb = { transform: b };
        if (k === 'shadow') { fa.opacity = from[k][1]; fb.opacity = to[k][1]; }
        paint(inst, k, to[k]);
        if (a === b && (k !== 'shadow' || from[k][1] === to[k][1])) return;
        elsOf(inst, k).forEach(function (el) {
          if (!el) return;
          made.push(el.animate([fa, fb], { duration: POSE_MS / spd, easing: (k === 'armL' || k === 'armR') && inst.view !== 'side' ? EASE.overshoot : EASE.out, fill: 'none' }));
        });
      });
      setShape(inst, 'L', row.L[0]);
      setShape(inst, 'R', row.R[0]);
      inst.pose = name;
      inst.ps = to;
      mark(inst);
      rt.rest(inst);
      inst.anims = inst.anims.concat(made);
      return Promise.all(made.map(function (a) { return a.finished.catch(function () {}); })).then(function () {
        if (inst.seq === seq) { inst.anims = []; inst.busy = false; }
        return true;
      });
    }

    // pbZorp.pose(name, { el, view, facing, expr, speed }). Full motion: a short overshoot tween (and a pinch-turn
    // first when the pose or opts name another view). Reduced and off: no limb or view changes, only the preset when
    // opts.expr asks for it; a return to 'stand' is applied instantly so nothing stays posed.
    function pose(name, opts) {
      opts = opts || {};
      var inst = rt.inst(opts);
      var row = poseRow(name);
      if (!inst || !row) return Promise.resolve(false);
      init(inst);
      var facing = opts.facing === 'l' || opts.facing === 'r' ? opts.facing : inst.facing;
      var spd = opts.speed > 0 && opts.speed < 1 ? opts.speed : 1;
      var view = opts.view || row.v;
      var want = opts.expr === true ? row.e : (typeof opts.expr === 'string' ? opts.expr : '');
      var did = false;
      if (rt.level() !== 'full' || !rt.rendered(inst) || !HAS_PROPS) {
        rt.stop(inst);
        if (name === 'stand' && (inst.pose !== 'stand' || inst.view !== 'front')) {
          applyPose(inst, 'stand', facing);
          if (view === 'front') rt.turn('front', 'r', { el: inst.svg });
          did = true;
        }
        if (want && rt.setExpression(want, { el: inst.svg })) did = true;
        return Promise.resolve(did);
      }
      var turned = Promise.resolve(true);
      if (view && (inst.view !== view || (view !== 'front' && inst.facing !== facing))) {
        turned = rt.turn(view, facing, { el: inst.svg, speed: spd, required: true });
      } else {
        rt.stop(inst);
      }
      return turned.then(function (ok) {
        if (!ok) return false;
        if (want) rt.setExpression(want, { el: inst.svg });
        rt.stop(inst);
        return poseTo(inst, name, facing, spd);
      });
    }

    // ---- the beat engine ----
    function listFor(c, opts) { return opts && opts.trip === true && c.trip ? c.trip : c.beats; }
    function span(list) { return list.reduce(function (s, b) { return s + (b.ms || 0) + (b.hold || 0); }, 0); }
    function clamp(v, m) { return Math.max(-m, Math.min(m, v)); }

    // beats -> [[element(s), keyframes]]: one keyframe list per part that moves. Offsets are fractions of
    // span + TAIL and never decrease. Head and arms trail the root (LAG); antennae follow root motion with overshoot.
    function compileBeats(beats, parts, opts) {
      var facing = opts && opts.facing === 'l' ? 'l' : 'r';
      var side = !!opts && opts.view === 'side';
      var D = span(beats) + TAIL;
      var fr = {};
      var prev = STAND;
      var t = 0;
      KEYS.forEach(function (k) { fr[k] = [{ t: 0, v: STAND[k], e: 'linear' }]; });
      fr.antL = [{ t: 0, v: 0, e: EASE.io }];
      beats.forEach(function (b) {
        var s = stateOf(POSES[b.pose] || POSES.stand, b, facing, side ? 'side' : '');
        var e = EASE[b.ease] || EASE.io;
        var ae = EASE[b.aease] || e;
        if (side && ae === EASE.overshoot) ae = EASE.out;   // profile: a raise overshooting past vertical would tip into the face
        var end = t + (b.ms || 0);
        KEYS.forEach(function (k) {
          var list = fr[k];
          list[list.length - 1].e = k === 'armL' || k === 'armR' ? ae : e;
          list.push({ t: end, v: s[k], e: 'linear' });
          if (b.hold) list.push({ t: end + b.hold, v: s[k], e: 'linear' });
        });
        var dy = s.root[1] - prev.root[1];
        fr.antL.push({ t: end + ANT_LAG, v: Math.abs(dy) > 0.5 ? clamp(dy * 1.5, 16) : 0, e: EASE.io });
        prev = s;
        t = end + (b.hold || 0);
      });
      fr.antL.push({ t: D, v: 0, e: EASE.io });
      var out = [];
      function emit(key, list, target, lag, val) {
        var pts = list.map(function (p) { return { t: p.t + (lag || 0), v: p.v, e: p.e }; });
        if (lag) pts.unshift({ t: 0, v: list[0].v, e: 'linear' });
        pts.push({ t: D, v: pts[pts.length - 1].v, e: 'linear' });
        var still = pts.every(function (p) { return val(p.v) === val(pts[0].v); });
        if (still && val(pts[0].v) === (key.indexOf('ant') === 0 ? 'rotate(0deg)' : IDENT[key])) return;
        out.push([target, pts.map(function (p) {
          var f = { offset: p.t / D, transform: val(p.v), easing: p.e };
          if (key === 'shadow') f.opacity = p.v[1];
          return f;
        })]);
      }
      KEYS.forEach(function (k) { emit(k, fr[k], parts[k], LAG[k], function (v) { return tf(k, v); }); });
      emit('antL', fr.antL, parts.antL, 0, function (v) { return tf('antL', v); });
      emit('antR', fr.antL.map(function (p) { return { t: p.t, v: -p.v, e: p.e }; }), parts.antR, 0, function (v) { return tf('antR', v); });
      return out;
    }

    // A beat clip starts from the standing pose (any resting pose is cleared, instantly).
    function pre(inst) {
      init(inst);
      if (inst.pose !== 'stand') applyPose(inst, 'stand', inst.facing);
    }

    // Expression, fx and arm shapes change at beat starts; the clip's original face returns at its end (tempFace) and
    // arm shapes return with stop() (rt undo list).
    function start(inst, spd, opts, c) {
      var list = listFor(c, opts);
      var total = (span(list) + TAIL) / spd;
      var t = 0;
      var expr = '';
      var fx = '';
      inst.undo.push(function () {
        var row = poseRow(inst.pose) || POSES.stand;
        setShape(inst, 'L', row.L[0]);
        setShape(inst, 'R', row.R[0]);
        layer(inst, 'L', !!row.L[2]);
        layer(inst, 'R', !!row.R[2]);
      });
      list.forEach(function (b) {
        var at = t / spd;
        var row = POSES[b.pose] || POSES.stand;
        // The arms trail the root by LAG, so a new shape swaps in once the arm is on its way: a long fist appears
        // when the arm has swung up (30% of the beat), and the short arm returns at once (12%) while the arm is still up, so a long arm never hangs down at foot level.
        var swap = function (S) {
          var raise = row[S][0] !== 'rest';
          var when = (LAG.armL + (b.ms || 0) * (raise ? 0.3 : 0.12)) / spd;
          var apply = function () { setShape(inst, S, row[S][0]); layer(inst, S, !!row[S][2]); };
          if (at + when <= 0) apply(); else rt.after(inst, at + when, apply);
        };
        var go = function () {
          if (b.expr) { expr = b.expr; fx = ''; }
          if (b.fx !== undefined) fx = b.fx === 'thought' ? '' : b.fx;
          if (expr && (b.expr || b.fx !== undefined)) rt.tempFace(inst, expr, Math.max(1, total - at), fx);
          if (b.fx === 'thought') rt.thought(inst);
        };
        swap('L');
        swap('R');
        if (at <= 0) go(); else rt.after(inst, at, go);
        t += (b.ms || 0) + (b.hold || 0);
      });
    }

    function beatClip(o) {
      var c = { dur: span(o.beats) + TAIL, beats: o.beats, trip: o.trip, view: o.view, reducedFace: o.reduced, pulse: !!o.pulse };
      c.pre = pre;
      c.tracks = function (parts, pupils, opts) { return compileBeats(listFor(c, opts), parts, opts); };
      c.start = function (inst, spd, opts) { start(inst, spd, opts, c); };
      return c;
    }

    var CL = rt.clips;
    var add = function (name, c) { CL[name] = c; if (rt.names.indexOf(name) === -1) rt.names.push(name); };

    add('fist-pump', beatClip({ reduced: 'joy', pulse: 1, beats: [
      { pose: 'crouch', expr: 'determined', ms: 110, ease: 'out' },
      { pose: 'fist-up', expr: 'joy', y: -12, dx: 1, s: [0.94, 1.08], ms: 200, hold: 180, ease: 'out', aease: 'overshoot' },
      { pose: 'fist-up', y: 1, s: [1.1, 0.9], ms: 130, ease: 'in' },
      { pose: 'fist-up', ms: 110, hold: 200, ease: 'overshoot', hr: -7 },
      { pose: 'stand', expr: 'grin', ms: 200, ease: 'out' }] }));
    add('victory', beatClip({ reduced: 'joy', pulse: 1, beats: [
      { pose: 'crouch', expr: 'determined', ms: 110, ease: 'out' },
      { pose: 'victory', expr: 'wow', fx: 'stars', y: -14, s: [0.94, 1.08], ms: 200, hold: 60, ease: 'out', aease: 'overshoot' },
      { pose: 'victory', expr: 'joy', y: 1, s: [1.1, 0.9], ms: 140, ease: 'in' },
      { pose: 'victory', ms: 110, hold: 260, ease: 'overshoot' },
      { pose: 'stand', expr: 'happy', ms: 220, ease: 'out' }] }));
    add('flex', beatClip({ reduced: 'proud', beats: [
      { pose: 'flex', expr: 'proud', ms: 220, hold: 350, ease: 'overshoot' },
      { pose: 'stand', expr: 'happy', ms: 200, ease: 'out' }] }));
    add('shrug', beatClip({ reduced: 'soft-smile', beats: [
      { pose: 'shrug', expr: 'soft-smile', ms: 200, hold: 300, ease: 'overshoot' },
      { pose: 'stand', ms: 200, ease: 'out' }] }));
    add('bow', beatClip({ reduced: 'bashful', view: 'side', beats: [
      { pose: 'bow', expr: 'bashful', ms: 200, hold: 200, ease: 'out' },
      { pose: 'stand', ms: 180, ease: 'io' }] }));
    add('think-chin', beatClip({ reduced: 'thinking', beats: [
      { pose: 'think-chin', expr: 'thinking', ms: 250, hold: 450, ease: 'out' },
      { pose: 'stand', expr: 'soft-smile', fx: 'bulb', ms: 250, ease: 'out' }] }));
    add('dance', beatClip({ reduced: 'laugh',
      beats: [
        { pose: 'dance-a', expr: 'laugh', fx: 'notes', ms: 130, hold: 120, ease: 'io' },
        { pose: 'dance-b', ms: 130, hold: 120, ease: 'io' },
        { pose: 'dance-a', ms: 130, hold: 120, ease: 'io' },
        { pose: 'dance-b', ms: 130, hold: 120, ease: 'io' },
        { pose: 'stand', expr: 'happy', ms: 260, ease: 'out' }],
      // opts.trip === true: Zorp's own stumble (embarrassed for 250 ms), then laughs it off. Never used by reactions.
      trip: [
        { pose: 'dance-a', expr: 'laugh', fx: 'notes', ms: 130, hold: 120, ease: 'io' },
        { pose: 'dance-b', ms: 130, hold: 120, ease: 'io' },
        { pose: 'dance-a', expr: 'embarrassed', r: 12, dx: 1.5, ms: 130, hold: 120, ease: 'overshoot' },
        { pose: 'stand', expr: 'laugh', ms: 130, hold: 120, ease: 'out' },
        { pose: 'stand', expr: 'happy', ms: 260, ease: 'out' }] }));
    add('float', beatClip({ reduced: 'happy', beats: [
      { pose: 'float', expr: 'happy', ms: 260, ease: 'out' },
      { pose: 'float', y: -2.5, ms: 220, ease: 'io' },
      { pose: 'float', y: 1.5, ms: 220, ease: 'io' },
      { pose: 'float', y: -2.5, ms: 220, ease: 'io' },
      { pose: 'stand', ms: 280, ease: 'out' }] }));
    add('oops-encourage', beatClip({ reduced: 'determined', beats: [
      { pose: 'stand', expr: 'oops', r: -3, ms: 60, hold: 190, ease: 'out' },
      { pose: 'stand', expr: 'determined', fx: 'thought', y: -4, dx: -1.5, s: [0.97, 1.04], ms: 170, ease: 'out' },
      { pose: 'stand', s: [1.05, 0.95], ms: 120, ease: 'in' },
      { pose: 'stand', expr: 'soft-smile', ms: 110, hold: 190, ease: 'out' }] }));
    // turn: the pinch-turn as a clip (leaves the view turned, like pbZorp.turn); reduced turns only with opts.required.
    add('turn', { dur: 300, custom: function (inst, opts, spd) {
      inst.busy = false;
      return rt.turn(opts.view || 'side', opts.facing, { el: inst.svg, speed: spd, required: opts.required });
    } });

    pb.pose = pose;
    pb.hasPose = function (name) { return !!poseRow(name); };
    pb.compileBeats = compileBeats;
    pb.clipInfo = function (name) {
      var c = rt.own(CL, name) ? CL[name] : null;
      return c ? { dur: c.dur, beats: c.beats || null, trip: c.trip || null, view: c.view || '', reducedFace: c.reducedFace || '', tail: TAIL } : null;
    };
    Object.defineProperty(pb, 'poses', { enumerable: true, get: function () { return Object.keys(POSES); } });
  });
}());
