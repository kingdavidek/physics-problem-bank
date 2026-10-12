(function () {
  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }
  ready(function () {
    var correctBtn = document.getElementById('sg-celebrate-correct');
    if (correctBtn) {
      correctBtn.addEventListener('click', function () {
        var mark = correctBtn.querySelector('.answer-check-mark');
        if (mark) mark.remove();
        var xp = correctBtn.querySelector('.answer-xp-float');
        if (xp) xp.remove();
        correctBtn.classList.remove('has-drawn-check', 'is-pop');
        correctBtn.classList.add('is-correct');
        if (window.pbCelebrate) window.pbCelebrate.correct(correctBtn);
      });
    }
    var confettiBtn = document.getElementById('sg-celebrate-confetti');
    if (confettiBtn) {
      confettiBtn.addEventListener('click', function () {
        if (window.pbCelebrate && window.pbCelebrate.confetti) window.pbCelebrate.confetti();
      });
    }
    function toastDemo(id, fn) {
      var btn = document.getElementById(id);
      if (btn) btn.addEventListener('click', fn);
    }
    toastDemo('sg-toast-success', function () {
      if (window.showAppToast) window.showAppToast('Saved to your collection.', 'success');
    });
    toastDemo('sg-toast-error', function () {
      if (window.showAppToast) window.showAppToast('Could not save that problem.', 'error');
    });
    toastDemo('sg-toast-action', function () {
      if (window.showAppToast) {
        window.showAppToast('Problem saved.', 'success', { linkUrl: '/saved', linkLabel: 'View saved' });
      }
    });
    var buddyFace = document.getElementById('sg-buddy-react');
    var buddyBtn = document.getElementById('sg-buddy-react-btn');
    if (buddyBtn && buddyFace) {
      buddyBtn.addEventListener('click', function () {
        buddyFace.classList.remove('is-reacting');
        void buddyFace.offsetWidth;
        buddyFace.classList.add('is-reacting');
        window.setTimeout(function () { buddyFace.classList.remove('is-reacting'); }, 560);
      });
    }
    var gestureDemo = document.getElementById('sg-zorp-gesture');
    var gestureTimer = 0;
    var gestureBtns = document.querySelectorAll('[data-zorp-gesture]');
    for (var i = 0; i < gestureBtns.length; i += 1) {
      gestureBtns[i].addEventListener('click', function (event) {
        if (!gestureDemo) return;
        var name = event.currentTarget.getAttribute('data-zorp-gesture');
        if (!name) return;
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        if (gestureTimer) window.clearTimeout(gestureTimer);
        gestureDemo.removeAttribute('data-gesture');
        void gestureDemo.getBoundingClientRect();
        gestureDemo.setAttribute('data-gesture', name);
        gestureTimer = window.setTimeout(function () {
          gestureTimer = 0;
          gestureDemo.removeAttribute('data-gesture');
        }, 1200);
      });
    }
    wireZorpDemo(document.getElementById('zorp-motion'));
    wireZorpDemo(document.getElementById('zorp-views'));
    wireZorpDemo(document.getElementById('zorp-poselib'));
    wireZorpDemo(document.getElementById('zorp-charm'));
    wireTalk(document.getElementById('zorp-charm'));
    wireSoft(document.getElementById('zorp-charm'));
    wireSound(document.getElementById('zorp-charm'));
    wireShowreel(document.getElementById('zorp-charm'));
    buildMatrix(document.getElementById('sg-zorp-matrix'));
    wireMotionBanners();
  });

  // E8 readability pass (2026-10-02): the clip demos make the effective motion level obvious. Reduced motion (the
  // OS asks for it, e.g. Windows "Animation effects" off, or the app's motion setting) only swaps the face, so every
  // demo section carries a banner saying so, plus a dev-only "preview at full motion" switch. The switch sets
  // html[data-motion-preview="full"], which zorp-motion.js honours; only this script ever sets it, so no real page
  // is affected.
  var lastClip = '';
  function motionBanners() {
    var z = window.pbZorp;
    var root = document.documentElement;
    var level = z && z.motionLevel ? z.motionLevel() : 'unknown';
    var attr = root.getAttribute('data-motion') || 'system';
    var preview = root.getAttribute('data-motion-preview') === 'full';
    var text;
    if (preview) text = 'Full-motion preview is ON for this page only. Your real setting (' + attr + ') is unchanged.';
    else if (level === 'full') text = 'Motion level: full. Clips animate normally.';
    else if (attr === 'off') text = 'Motion is OFF (app setting or the simulator below), so clips only swap the face. Use the full-motion preview button to see the movement.';
    else if (attr === 'reduced') text = 'Reduced motion is ON (app setting or the simulator below), so clips show the face only (bow and side-point also switch to the side view at once), with no body or arm movement. Use the full-motion preview button to see the movement.';
    else text = 'Reduced motion is ON (from your system: on Windows, Settings > Accessibility > Visual effects > Animation effects is off), so clips show the face only (bow and side-point also switch to the side view at once), with no body or arm movement. Use the full-motion preview button to see the movement.';
    var limited = level !== 'full';
    if (limited && lastClip) text += ' Last clip you pressed: ' + lastClip + ' (no movement).';
    var boxes = document.querySelectorAll('[data-zorp-motion-banner]');
    for (var i = 0; i < boxes.length; i += 1) {
      var msg = boxes[i].querySelector('[data-zorp-motion-text]');
      var btn = boxes[i].querySelector('[data-zorp-preview-full]');
      if (msg) msg.textContent = text;
      boxes[i].classList.toggle('is-limited', limited);
      if (btn) {
        btn.setAttribute('aria-pressed', preview ? 'true' : 'false');
        btn.textContent = preview ? 'Stop full-motion preview' : 'Preview at full motion';
      }
    }
    var labels = document.querySelectorAll('[data-zorp-motion-level]');
    for (var k = 0; k < labels.length; k += 1) labels[k].textContent = 'motionLevel(): ' + level;
  }
  function wireMotionBanners() {
    var root = document.documentElement;
    var btns = document.querySelectorAll('[data-zorp-preview-full]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function () {
        if (root.getAttribute('data-motion-preview') === 'full') root.removeAttribute('data-motion-preview');
        else root.setAttribute('data-motion-preview', 'full');
        motionBanners();
      });
    }
    if (window.MutationObserver) new MutationObserver(motionBanners).observe(root, { attributes: true, attributeFilter: ['data-motion', 'data-motion-preview'] });
    var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
    if (mq && mq.addEventListener) mq.addEventListener('change', motionBanners);
    motionBanners();
  }

  // E8 Phase 2: eyes x mouths review grid, cloned from the inert parts library (no pbZorp needed).
  function buildMatrix(table) {
    var tpl = document.getElementById('pb-zorp-parts');
    if (!table || !tpl || !tpl.content) return;
    var NS = 'http://www.w3.org/2000/svg';
    var eyes = (table.getAttribute('data-eyes') || '').split(' ');
    var mouths = (table.getAttribute('data-mouths') || '').split(' ');
    function part(channel, id) { return tpl.content.querySelector('[data-part="' + channel + ':' + id + '"]'); }
    function put(parent, node) {
      if (!node) return;
      for (var i = 0; i < node.childNodes.length; i += 1) parent.appendChild(node.childNodes[i].cloneNode(true));
    }
    function el(name, attrs) {
      var n = document.createElementNS(NS, name);
      for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) n.setAttribute(k, attrs[k]);
      return n;
    }
    function face(eye, mouth) {
      var svg = el('svg', { viewBox: '14 22 36 32', 'aria-hidden': 'true', 'class': 'buddy-mascot' });
      svg.appendChild(el('ellipse', { cx: 32, cy: 36, rx: 21, ry: 21.5, fill: 'var(--brand-500)' }));
      svg.appendChild(el('ellipse', { cx: 32, cy: 38, rx: 15.5, ry: 13.5, fill: 'var(--brand-50)' }));
      var l = el('g', { transform: 'translate(26.2 35.2)' });
      var r = el('g', { transform: 'translate(37.8 35.2)' });
      put(l, part('eyes', eye));
      put(r, part('eyes', part('eyes', eye + '-r') ? eye + '-r' : eye));
      svg.appendChild(l);
      svg.appendChild(r);
      var m = el('g', {});
      put(m, part('mouth', mouth));
      svg.appendChild(m);
      return svg;
    }
    var head = document.createElement('tr');
    head.appendChild(document.createElement('th'));
    mouths.forEach(function (mouth) {
      var th = document.createElement('th');
      th.setAttribute('scope', 'col');
      th.textContent = mouth;
      head.appendChild(th);
    });
    var thead = document.createElement('thead');
    thead.appendChild(head);
    table.appendChild(thead);
    var body = document.createElement('tbody');
    eyes.forEach(function (eye) {
      var tr = document.createElement('tr');
      var th = document.createElement('th');
      th.setAttribute('scope', 'row');
      th.textContent = eye;
      tr.appendChild(th);
      mouths.forEach(function (mouth) {
        var td = document.createElement('td');
        td.setAttribute('data-matrix-cell', eye + ':' + mouth);
        td.appendChild(face(eye, mouth));
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    table.appendChild(body);
  }

  // E8 Phase 1 picker: preset chips, channel dropdowns, motion-level simulator (sets
  // html[data-motion] on this dev page only) and the 0.25x slow-motion toggle.
  function wireExpressionPicker(scope, z, demos, getSlow, setSlow) {
    var selects = scope.querySelectorAll('[data-zorp-channel]');
    var i;
    function apply(input) {
      for (var k = 0; k < demos.length; k += 1) z.setExpression(input, { el: demos[k] });
    }
    function sync(name) {
      var ch = z.channelsOf ? z.channelsOf(name) : null;
      if (!ch) return;
      for (var n = 0; n < selects.length; n += 1) {
        var key = selects[n].getAttribute('data-zorp-channel');
        if (ch[key]) selects[n].value = ch[key];
      }
    }
    var chips = scope.querySelectorAll('[data-zorp-expr]');
    for (i = 0; i < chips.length; i += 1) {
      chips[i].addEventListener('click', function (event) {
        var name = event.currentTarget.getAttribute('data-zorp-expr');
        apply(name);
        sync(name);
      });
    }
    for (i = 0; i < selects.length; i += 1) {
      selects[i].addEventListener('change', function () {
        var input = {};
        for (var n = 0; n < selects.length; n += 1) input[selects[n].getAttribute('data-zorp-channel')] = selects[n].value;
        apply(input);
      });
    }
    var label = scope.querySelector('[data-zorp-motion-level]');
    var levels = scope.querySelectorAll('[data-zorp-set-motion]');
    for (i = 0; i < levels.length; i += 1) {
      levels[i].addEventListener('click', function (event) {
        document.documentElement.removeAttribute('data-motion-preview');
        document.documentElement.setAttribute('data-motion', event.currentTarget.getAttribute('data-zorp-set-motion'));
        if (label) label.textContent = 'motionLevel(): ' + z.motionLevel();
      });
    }
    var slowBtn = scope.querySelector('[data-zorp-slow]');
    if (slowBtn) {
      slowBtn.addEventListener('click', function () {
        setSlow(!getSlow());
        slowBtn.setAttribute('aria-pressed', getSlow() ? 'true' : 'false');
        slowBtn.textContent = 'Slow 0.25x: ' + (getSlow() ? 'on' : 'off');
      });
    }
    sync('nudge');
  }

  // E9 Phase 2 (docs/ZORP_CHARM.md 3.2.6): the dev A/B switch for the soft body. html[data-zorp-soft="off"] makes zorp-poses.js leave the
  // soft layer out of the clips that start afterwards; only this script ever sets it, so no real page is affected.
  function wireSoft(scope) {
    var btn = scope && scope.querySelector('[data-zorp-soft-toggle]');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var root = document.documentElement;
      var off = root.getAttribute('data-zorp-soft') === 'off';
      if (off) root.removeAttribute('data-zorp-soft'); else root.setAttribute('data-zorp-soft', 'off');
      btn.setAttribute('aria-pressed', off ? 'true' : 'false');
      btn.textContent = 'Soft body: ' + (off ? 'on' : 'off');
    });
  }

  // E9 Phase 5 (docs/ZORP_EVALUATION.md): the showreel for the projector, in the order of the class session. It only presses what the
  // buttons above already press (say, play, the soft toggle, the forced cue preview), at the real caps (1,600 ms story and reward,
  // 1,200 ms bubble). The sound steps run the preview cues (force), timed to the fist-pump's take-off (110 ms) and landing (620 ms),
  // and only at full motion, as a pupil with Zorp's sounds on Celebrations would hear them.
  function wireShowreel(scope) {
    var box = scope && scope.querySelector('[data-zorp-showreel]');
    var z = window.pbZorp;
    if (!box || !z || typeof z.say !== 'function') return;
    var big = box.querySelector('[data-showreel-stage="big"]');
    var small = box.querySelector('[data-showreel-stage="small"]');
    if (!big || !small) return;
    z.bind(big);
    z.bind(small);
    var line = box.querySelector('[data-showreel-line]');
    var bubble = box.querySelector('[data-showreel-bubble]');
    var status = box.querySelector('[data-showreel-status]');
    var soft = scope.querySelector('[data-zorp-soft-toggle]');
    var timers = [];
    function setSoft(on) {
      if (soft && (document.documentElement.getAttribute('data-zorp-soft') !== 'off') !== on) soft.click();
    }
    function later(fn, ms) { timers.push(window.setTimeout(fn, ms)); }
    function report(name) {
      var level = z.motionLevel();
      status.textContent = name + (level === 'full' ? '' : ' (motion level ' + level + ': the text is shown and nothing moves or sounds. Press Preview at full motion in the banner.)');
    }
    function originLine() {
      var cat = window.pbGuideCatalog;
      var first = cat && cat.origin && cat.origin[0] && cat.origin[0].lines && cat.origin[0].lines[0];
      return first || 'A bit about me: I\u2019m Zorp, from Novara, out past the maths belt.';
    }
    function reward(name, withSoft) {
      setSoft(withSoft);
      z.say(line, 'You earned this.', { el: big, max: 1600 });
      z.play('fist-pump', { el: big });
      report(name);
    }
    var steps = {
      origin: function () {
        z.say(line, originLine(), { el: big, max: 1600 });
        z.play('wave', { el: big });
        report('1. Origin line: the mouth follows the text, at most 1.6 s');
      },
      reward: function () { reward('2. Reward: fist-pump with the soft body on', true); },
      'reward-flat': function () {
        reward('3. The same reward with the soft body off (the E8 look)', false);
        later(function () { setSoft(true); }, 2400);
      },
      bubble: function () {
        z.say(bubble, 'Nice work: 7/10 on Forces.', { el: small, max: 1200 });
        report('4. Corner bubble: the mouth talks once, at most 1.2 s, no body clip');
      },
      'sound-on': function () {
        var s = window.pbSound;
        if (z.motionLevel() === 'full' && s && typeof s.zorp === 'function') {
          later(function () { s.zorp('jump', { force: true }); }, 110);
          later(function () { s.zorp('land', { force: true }); }, 620);
        }
        reward('5. Sound on: a quiet jump cue and a land cue with the fist-pump (pupils get these only with Zorp\u2019s sounds on Celebrations in Settings)', true);
      },
      'sound-off': function () {
        if (window.pbSound && typeof window.pbSound.stopAll === 'function') window.pbSound.stopAll();
        reward('6. Sound off: the same reward in silence, which is the default for every pupil', true);
      }
    };
    var btns = box.querySelectorAll('[data-showreel]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function (event) {
        var step = steps[event.currentTarget.getAttribute('data-showreel')];
        if (!step) return;
        timers.forEach(window.clearTimeout);
        timers = [];
        setSoft(true);   // every step starts soft, so a quick press after the A/B never leaves it off
        z.hush(big);
        z.hush(small);
        step();
      });
    }
  }

  // E9 Phase 4 (docs/ZORP_CHARM.md 3.4.7): the audio preview. Only this script passes force (it skips the zorp_sound setting and the
  // one-sequence-per-7-s limit, nothing else) or turns the D7 blips on; pbSound.arm() makes the page record taps without the setting.
  function wireSound(scope) {
    var s = window.pbSound;
    var z = window.pbZorp;
    if (!scope || !s || typeof s.zorp !== 'function') return;
    s.arm();
    var out = scope.querySelector('[data-zorp-sound-out]');
    function say(text) { if (out) out.textContent = text; }
    var cues = scope.querySelectorAll('[data-zorp-cue]');
    for (var i = 0; i < cues.length; i += 1) {
      cues[i].addEventListener('click', function (event) {
        var cue = event.currentTarget.getAttribute('data-zorp-cue');
        var ok = s.zorp(cue === 'sequence' ? 'jump' : cue, { force: true });
        if (ok && cue === 'sequence') window.setTimeout(function () { s.zorp('land', { force: true }); }, 280);
        say(cue + (ok ? ': playing' : ': skipped (it needs a tap in the last 5 seconds, a visible page, and 400 ms since the last sound)'));
      });
    }
    var stop = scope.querySelector('[data-zorp-sound-stop]');
    if (stop) stop.addEventListener('click', function () { s.stopAll(); say('stopped'); });
    var blips = scope.querySelector('[data-zorp-blips]');
    var demo = scope.querySelector('[data-zorp-demo]');
    var box = scope.querySelector('[data-zorp-talk-text]');
    var cap = scope.querySelector('[data-zorp-talk-cap]');
    if (blips && z && demo && box && typeof z.talk === 'function') {
      blips.addEventListener('click', function () {
        z.talk({ el: demo, text: box.value, max: +cap.value || 1200, blips: true, force: true }).then(function (done) {
          say('blips: ' + (done ? 'finished' : 'cut short or not played (full motion needed: use the preview button above)'));
        });
      });
    }
  }

  // E9 Phase 1 (docs/ZORP_CHARM.md 3.1): the talk demo. The first Zorp's text line is written by pbZorp.say (text first),
  // the others then talk the same text in turn; the readout prints the plan (pbZorp.talkPlan), including at reduced and off, where
  // nothing flaps. Every Guide line from the catalog becomes a chip.
  function wireTalk(scope) {
    var z = window.pbZorp;
    if (!z || !scope || typeof z.say !== 'function') return;
    var demos = scope.querySelectorAll('[data-zorp-demo]');
    var box = scope.querySelector('[data-zorp-talk-text]');
    var cap = scope.querySelector('[data-zorp-talk-cap]');
    var line = scope.querySelector('[data-zorp-talk-line]');
    var out = scope.querySelector('[data-zorp-talk-plan]');
    var chips = scope.querySelector('[data-zorp-talk-chips]');
    function speak(text, clip) {
      var max = +cap.value || 1200;
      var plan = z.talkPlan(text, { max: max });
      var opens = 0;
      var minOpen = 1e9;
      for (var f = 1; f < plan.frames.length; f += 1) {
        if (plan.frames[f][1] > 0) {
          opens += 1;
          if (plan.frames[f + 1]) minOpen = Math.min(minOpen, plan.frames[f + 1][0] - plan.frames[f][0]);
        }
      }
      var level = z.motionLevel();
      out.textContent = 'plan: ' + plan.ms + ' ms of ' + max + ' cap, ' + plan.words.length + ' words, ' + opens + ' open frames, shortest open frame ' +
        (opens ? minOpen + ' ms' : 'none') + ', peak rate ' + (opens ? (1000 / Math.max(111, plan.ms / Math.max(1, opens))).toFixed(1) : '0') +
        ' Hz at most.\nmotionLevel(): ' + level + (level === 'full' ? '' : ' (no flapping; the text is still shown at once)');
      // One talker at a time (a runtime rule), so the six Zorps take turns; Hush or a new Talk ends the round.
      var run = ++round;
      var chain = z.say(line, text, { el: demos[0], max: max });
      for (var k = 0; k < demos.length; k += 1) {
        if (clip) z.play(clip, { el: demos[k] });
        if (k) chain = chain.then(turnOf(demos[k], text, max, run));
      }
    }
    var round = 0;
    function turnOf(el, text, max, run) {
      return function () { return run === round ? z.talk({ el: el, text: text, max: max }) : false; };
    }
    var go = scope.querySelector('[data-zorp-talk]');
    if (go) go.addEventListener('click', function () { speak(box.value); });
    var hush = scope.querySelector('[data-zorp-hush]');
    if (hush) {
      hush.addEventListener('click', function () {
        round += 1;
        for (var k = 0; k < demos.length; k += 1) z.hush(demos[k]);
      });
    }
    var clipBtns = scope.querySelectorAll('[data-zorp-talk-clip]');
    for (var c = 0; c < clipBtns.length; c += 1) {
      clipBtns[c].addEventListener('click', function (event) { speak(box.value, event.currentTarget.getAttribute('data-zorp-talk-clip')); });
    }
    function collect(node, found) {
      if (Array.isArray(node)) {
        for (var i = 0; i < node.length; i += 1) {
          if (typeof node[i] === 'string') found.push(node[i]); else collect(node[i], found);
        }
      } else if (node && typeof node === 'object') {
        if (Array.isArray(node.lines)) collect(node.lines, found);
        for (var key in node) {
          if (Object.prototype.hasOwnProperty.call(node, key) && key !== 'lines' && typeof node[key] === 'object') collect(node[key], found);
        }
      }
      return found;
    }
    var lines = collect(window.pbGuideCatalog || {}, []);
    if (chips && lines.length) {
      lines.forEach(function (text) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'btn btn-outline btn-sm';
        b.textContent = text;
        b.addEventListener('click', function () { box.value = text; speak(text); });
        chips.appendChild(b);
      });
    }
  }

  function wireZorpDemo(scope) {
    var z = window.pbZorp;
    if (!z || !scope) return;
    var demos = scope.querySelectorAll('[data-zorp-demo]');
    for (var d = 0; d < demos.length; d += 1) z.bind(demos[d]);
    var level = scope.querySelector('[data-zorp-motion-level]');
    if (level) level.textContent = 'motionLevel(): ' + z.motionLevel();
    var slow = false;   // E8: dev-only 0.25x slow motion for clips
    var facing = 'r';
    var btns = scope.querySelectorAll('[data-zorp-clip]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function (event) {
        var btn = event.currentTarget;
        lastClip = btn.getAttribute('data-zorp-clip') + (btn.hasAttribute('data-zorp-trip') ? ' (trip)' : '');
        motionBanners();
        for (var k = 0; k < demos.length; k += 1) {
          z.play(btn.getAttribute('data-zorp-clip'), {
            el: demos[k],
            target: btn.getAttribute('data-zorp-target') || undefined,
            trip: btn.hasAttribute('data-zorp-trip') ? true : undefined,
            facing: facing,
            speed: slow ? 0.25 : undefined
          });
        }
      });
    }
    wireExpressionPicker(scope, z, demos, function () { return slow; }, function (on) { slow = on; });
    // E8 Phase 3: turn buttons, the front-side-front cycle and the facing toggle (views section).
    var turnBtns = scope.querySelectorAll('[data-zorp-turn]');
    var t;
    for (t = 0; t < turnBtns.length; t += 1) {
      turnBtns[t].addEventListener('click', function (event) {
        var view = event.currentTarget.getAttribute('data-zorp-turn');
        for (var k = 0; k < demos.length; k += 1) z.turn(view, facing, { el: demos[k], speed: slow ? 0.25 : undefined, required: true });
      });
    }
    var cycle = scope.querySelector('[data-zorp-turn-cycle]');
    if (cycle) {
      cycle.addEventListener('click', function () {
        for (var k = 0; k < demos.length; k += 1) {
          (function (el) {
            var o = { el: el, speed: slow ? 0.25 : undefined, required: true };
            var p = z.turn('side', facing, o);
            var back = function () { z.turn('front', facing, o); };
            if (p && p.then) p.then(back, back); else back();
          })(demos[k]);
        }
      });
    }
    var facingBtns = scope.querySelectorAll('[data-zorp-facing]');
    for (t = 0; t < facingBtns.length; t += 1) {
      facingBtns[t].addEventListener('click', function (event) {
        facing = event.currentTarget.getAttribute('data-zorp-facing');
        for (var n = 0; n < facingBtns.length; n += 1) facingBtns[n].setAttribute('aria-pressed', facingBtns[n] === event.currentTarget ? 'true' : 'false');
        for (var k = 0; k < demos.length; k += 1) z.turn((z.viewOf(demos[k]) || { view: 'front' }).view, facing, { el: demos[k], required: true });
      });
    }
    // E8 Phase 4: resting poses (pbZorp.pose); the pose's own preset is drawn too.
    var poseBtns = scope.querySelectorAll('[data-zorp-pose]');
    for (t = 0; t < poseBtns.length; t += 1) {
      poseBtns[t].addEventListener('click', function (event) {
        if (!z.pose) return;
        for (var k = 0; k < demos.length; k += 1) z.pose(event.currentTarget.getAttribute('data-zorp-pose'), { el: demos[k], expr: true, facing: facing, speed: slow ? 0.25 : undefined });
      });
    }
    // E8 Phase 4 (docs 3.10): gallery-only silhouette check. One CSS filter on each mascot flattens it to a single
    // colour (ink on light, white on dark), so a pose has to read from its outline alone. No per-pose rules.
    var silBtn = scope.querySelector('[data-zorp-silhouette]');
    if (silBtn) {
      silBtn.addEventListener('click', function () {
        var on = silBtn.getAttribute('aria-pressed') !== 'true';
        var bg = scope.querySelector('svg.buddy-mascot');
        var rgb = [255, 255, 255];
        for (; bg; bg = bg.parentElement) {   // the first opaque background behind the mascots
          var c = window.getComputedStyle(bg).backgroundColor.match(/[\d.]+/g);
          if (c && (c.length < 4 || +c[3] > 0.5)) { rgb = c.slice(0, 3).map(Number); break; }
        }
        var dark = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000 < 128;
        var marks = scope.querySelectorAll('svg.buddy-mascot');
        for (var m = 0; m < marks.length; m += 1) marks[m].style.filter = on ? (dark ? 'brightness(0) invert(1)' : 'brightness(0)') : '';
        silBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
        silBtn.textContent = 'Silhouette: ' + (on ? 'on' : 'off');
      });
    }
    var off = scope.querySelector('[data-zorp-idle-off]');
    if (off) off.addEventListener('click', function () { for (var k = 0; k < demos.length; k += 1) z.idle(false, demos[k]); });
    var reactBtns = scope.querySelectorAll('[data-zorp-react]');
    for (var r = 0; r < reactBtns.length; r += 1) {
      reactBtns[r].addEventListener('click', function (event) {
        if (!z.react) return;
        var kind = event.currentTarget.getAttribute('data-zorp-react');
        for (var k = 0; k < demos.length; k += 1) z.react(kind, { el: demos[k] });
      });
    }
  }
})();
