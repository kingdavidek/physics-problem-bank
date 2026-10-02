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
