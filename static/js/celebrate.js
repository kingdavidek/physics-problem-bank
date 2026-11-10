(function () {
  'use strict';

  var correctStreak = 0;
  var lastBurstAt = 0;
  var STREAK_ROUNDS = { 7: 1, 30: 1, 100: 1 };
  // E11 Phase 0 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 1.2): "already celebrated" flags belong to one pupil (the account's storage
  // name, meta pb-store), so a second pupil on the same browser is never silenced by the first one's badges. The old shared flags
  // ('pb-u74-ms-<key>', 'pb-u74-streak-<n>') are not read any more.
  var STORE_NS = (function () {
    var m = document.querySelector('meta[name="pb-store"]');
    return (m && m.getAttribute('content')) || 'anon';
  })();
  var LS_MILESTONE = 'pb-ms:' + STORE_NS + ':';
  var LS_STREAK = 'pb-streak:' + STORE_NS + ':';
  var CHECK_MARK_SVG =
    '<circle class="answer-check-mark-ring" cx="12" cy="12" r="10"/>' +
    '<path class="answer-check-mark-tick" d="M7 12.5l3.2 3.2L17 8.8"/>';

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  // E7 Phase 2: schedule a mascot reaction on the next frame, never blocking grading feedback.
  // The only references to the global motion runtime in this file live inside this function.
  function reactMascot(kind, opts) {
    if (!window.pbZorp || typeof window.pbZorp.react !== 'function') return;
    var fire = function () {
      try {
        window.pbZorp.react(kind, opts || {});
      } catch (err) { /* a mascot glitch must never break grading */ }
    };
    if (typeof window.requestAnimationFrame === 'function') {
      window.requestAnimationFrame(fire);
    } else {
      window.setTimeout(fire, 0);
    }
  }

  function toastHost() {
    return document.getElementById('app-toast-host');
  }

  function celebrateAnchor(target) {
    if (!target || !target.closest) return null;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
      return target.closest('.free-response-inline, .free-response-row, .problem-card, .mcq-inline')
        || target.parentElement;
    }
    return target;
  }

  // E10 phase 5, honest XP: a number is shown only when it is what was really recorded (points > 0, passed by the caller from the
  // server: models/gamification.py EFFORT_WEIGHTS). A check records no effort points, so a correct answer shows the sparkle alone.
  function showXpFloat(anchor, points) {
    var label = points > 0 ? '+' + points + ' XP' : '';
    if (anchor && anchor.appendChild) {
      anchor.classList.add('is-celebrate-host');
      if (label) {
        var prev = anchor.querySelector('.answer-xp-float');
        if (prev) prev.remove();
        var floatEl = document.createElement('span');
        floatEl.className = 'answer-xp-float';
        floatEl.setAttribute('aria-hidden', 'true');
        floatEl.textContent = label;
        anchor.appendChild(floatEl);
        window.setTimeout(function () { floatEl.remove(); }, prefersReducedMotion() ? 900 : 1300);
      }
      if (!prefersReducedMotion()) burstSparkle(anchor);
      return;
    }
    var host = toastHost();
    if (!host || !label) return;
    var el = document.createElement('div');
    el.className = 'xp-toast';
    el.textContent = label;
    host.appendChild(el);
    window.setTimeout(function () {
      el.classList.add('is-gone');
      window.setTimeout(function () { el.remove(); }, 280);
    }, 1400);
  }

  // E7 Phase 4: a small 3-5 particle sparkle burst next to the XP float, reusing the
  // confetti append/animate mechanism at a smaller scale and shorter duration.
  function burstSparkle(anchor) {
    if (!anchor || !anchor.appendChild) return;
    var n = 3 + Math.floor(Math.random() * 3);
    for (var i = 0; i < n; i += 1) {
      var bit = document.createElement('span');
      bit.className = 'sparkle-bit sparkle-bit--' + (i % 3);
      bit.style.setProperty('--sx', (Math.random() * 36 - 18) + 'px');
      bit.style.setProperty('--sy', (-10 - Math.random() * 22) + 'px');
      bit.style.animationDelay = (Math.random() * 80) + 'ms';
      anchor.appendChild(bit);
      (function (el) {
        window.setTimeout(function () { el.remove(); }, 650);
      }(bit));
    }
  }

  function drawCheckmark(anchor) {
    if (!anchor || !anchor.appendChild) return;
    if (anchor.querySelector('.answer-check-mark')) return;
    anchor.classList.add('has-drawn-check');
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'answer-check-mark');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    svg.innerHTML = CHECK_MARK_SVG;
    anchor.appendChild(svg);
  }

  function claimed(storageKey) {
    try {
      if (window.localStorage.getItem(storageKey) === '1') return true;
      window.localStorage.setItem(storageKey, '1');
      return false;
    } catch (err) {
      return false;
    }
  }

  function burstConfetti(opts) {
    if (prefersReducedMotion()) return;
    // E9 Phase 4 (3.4.4): one sound per moment. A cue that actually starts replaces the arpeggio. With cues on, wait 1 s (the
    // clip's first cue starts about 0.8 s after react) and play the arpeggio only if none started (no Guide, stale tap, 7 s window).
    var ps = window.pbSound;
    if (!(opts && opts.silent) && ps && ps.celebrate) {
      if (ps.cuesActive && ps.cuesActive() && ps.cued) {
        window.setTimeout(function () { if (!ps.cued(1500)) ps.celebrate(); }, 1000);
      } else {
        ps.celebrate();
      }
    }
    var now = Date.now();
    if (now - lastBurstAt < 1600) return;
    lastBurstAt = now;
    var root = document.createElement('div');
    root.className = 'confetti-burst';
    root.setAttribute('aria-hidden', 'true');
    var palettes = 5;
    for (var i = 0; i < 40; i += 1) {
      var bit = document.createElement('span');
      var shape = (i % 2 === 0) ? 'dot' : 'star';
      bit.className = 'confetti-bit confetti-bit--' + (i % palettes) + ' confetti-bit--' + shape;
      bit.style.left = (8 + Math.random() * 84) + 'vw';
      bit.style.top = (8 + Math.random() * 28) + 'vh';
      bit.style.width = (6 + Math.random() * 6) + 'px';
      bit.style.height = (8 + Math.random() * 10) + 'px';
      bit.style.animationDelay = (Math.random() * 180) + 'ms';
      bit.style.animationDuration = (700 + Math.random() * 500) + 'ms';
      bit.style.setProperty('--drift', (Math.random() * 220 - 110) + 'px');
      bit.style.setProperty('--spin', (160 + Math.random() * 200) + 'deg');
      root.appendChild(bit);
    }
    document.body.appendChild(root);
    window.setTimeout(function () { root.remove(); }, 1400);
  }

  function celebrateCorrect(target, points) {
    correctStreak += 1;
    var anchor = celebrateAnchor(target);
    var xp = typeof points === 'number' ? points : 0;
    if (window.pbSound && window.pbSound.correct) window.pbSound.correct();
    if (anchor && !prefersReducedMotion()) {
      anchor.classList.add('is-pop');
      window.setTimeout(function () { anchor.classList.remove('is-pop'); }, 420);
    }
    drawCheckmark(anchor);
    // points === 0 means "no per-step XP" (lesson-quiz steps): nothing at all; no points given: the sparkle without a number.
    if (points !== 0) showXpFloat(anchor, xp);
    var openedFirst = false;
    if (window.pbGuide && typeof window.pbGuide.reward === 'function') {
      openedFirst = window.pbGuide.reward({ type: 'first_correct' });
      if (openedFirst) burstConfetti();
    }
    var isStreak = correctStreak >= 3;
    if (isStreak) {
      if (window.pbSound && window.pbSound.ding) {
        burstConfetti({ silent: true });
        window.pbSound.ding();
      } else {
        burstConfetti();
      }
      correctStreak = 0;
    }
    reactMascot(openedFirst ? 'first_correct' : (isStreak ? 'streak' : 'correct'));
  }

  function celebrateWrong(target, correctTarget) {
    correctStreak = 0;
    if (window.pbSound && window.pbSound.soft) window.pbSound.soft();
    else if (window.pbSound && window.pbSound.wrong) window.pbSound.wrong();
    reactMascot('wrong');
    if (prefersReducedMotion()) return;
    if (target) {
      target.classList.add('is-shake');
      window.setTimeout(function () { target.classList.remove('is-shake'); }, 380);
    }
    if (correctTarget) {
      correctTarget.classList.add('is-reveal');
      window.setTimeout(function () { correctTarget.classList.remove('is-reveal'); }, 700);
    }
  }

  // E10 phase 4: a badge arrives as a key or as the display data the server sends ({key, title, blurb, family, emoji, tier, next_title, next_how}).
  // pbGuide.reward answers 'stage' when the badge stage will play it (full screen, with its own burst), so no confetti behind it.
  function celebrateMilestone(item) {
    var data = item && typeof item === 'object' ? item : null;
    var token = String((data ? data.key : item) || 'badge').replace(/\s+/g, '_');
    if (window.pbGuide && typeof window.pbGuide.reward === 'function') {
      var spec = { type: 'milestone', key: token };
      if (data) spec.badge = data;
      var opened = window.pbGuide.reward(spec);
      if (opened !== false && opened !== 'stage') {
        burstConfetti();
        reactMascot('milestone');
      }
      if (opened !== false) {
        try { window.localStorage.setItem(LS_MILESTONE + token, '1'); } catch (err) {}
      }
      return opened !== false;
    }
    if (claimed(LS_MILESTONE + token)) return false;
    burstConfetti();
    reactMascot('milestone');
    return true;
  }

  function celebrateStreakRound(days) {
    var n = parseInt(days, 10);
    if (!STREAK_ROUNDS[n]) return false;
    if (window.pbGuide && typeof window.pbGuide.reward === 'function') {
      var opened = window.pbGuide.reward({ type: 'streak', days: n });
      if (opened !== false && opened !== 'stage') {
        burstConfetti();
        reactMascot('streak');
      }
      if (opened !== false) {
        try { window.localStorage.setItem(LS_STREAK + n, '1'); } catch (err) {}
      }
      return opened !== false;
    }
    if (claimed(LS_STREAK + n)) return false;
    burstConfetti();
    reactMascot('streak');
    return true;
  }

  // E10 phase 5: moments (level-up, perfect quiz, toasts, micro reactions) go to guide.js, which loads moments.js when one is due.
  function handOver(list) {
    if (Array.isArray(list) && list.length && window.pbGuide && window.pbGuide.moments) window.pbGuide.moments(list);
  }

  function fromPayload(data) {
    if (!data) return;
    var keys = data.new_milestones || data.awarded_milestones;
    if (Array.isArray(keys)) {
      keys.forEach(function (item) { celebrateMilestone(item); });
    }
    if (data.milestone_key) celebrateMilestone(data.milestone_key);
    handOver(data.new_moments);
    var streak = data.study_streak;
    if (streak && typeof streak === 'object') {
      celebrateStreakRound(streak.current);
    } else if (data.study_streak_current != null) {
      celebrateStreakRound(data.study_streak_current);
    }
  }

  function fromBuddyPrompt(prompt) {
    if (!prompt || prompt.type !== 'milestone') return;
    celebrateMilestone(prompt.milestone_key);
  }

  function scanPageTriggers() {
    // Milestones now surface via the notifications bell + this JSON island rather
    // than the corner buddy bubble, so this no longer depends on the buddy root
    // being visible (it can be hidden entirely, e.g. during a quiz).
    var milestoneEl = document.getElementById('pb-new-milestones');
    if (milestoneEl) {
      try {
        var list = JSON.parse(milestoneEl.textContent || 'null');
        if (Array.isArray(list)) list.forEach(function (item) { if (item) celebrateMilestone(item); });
      } catch (err) {}
    }
    var momentEl = document.getElementById('pb-new-moments');
    if (momentEl) {
      try { handOver(JSON.parse(momentEl.textContent || 'null')); } catch (err) {}
    }
    var ring = document.querySelector('[data-streak-current]');
    if (ring) celebrateStreakRound(ring.getAttribute('data-streak-current'));
    var nav = document.querySelector('.nav-streak[data-streak]');
    if (nav) celebrateStreakRound(nav.getAttribute('data-streak'));
  }

  window.pbCelebrate = {
    correct: celebrateCorrect,
    wrong: celebrateWrong,
    confetti: burstConfetti,
    milestone: celebrateMilestone,
    streakRound: celebrateStreakRound,
    fromPayload: fromPayload,
    xp: function (points) { showXpFloat(null, points); },   // E10 phase 5: the real points as a corner float (moments.js, set work)
    fromBuddy: fromBuddyPrompt,
    // E10 phase 5: every finished lesson is a stage moment (info: level, subject, topic, name, quiz); no fixed XP float any more, because
    // finishing a lesson records no points of its own. Without the stage (offline, blocked file) the older confetti and dialog remain.
    lessonComplete: function (info) {
      correctStreak = 0;
      var opened = false;
      if (window.pbGuide && typeof window.pbGuide.reward === 'function') {
        opened = window.pbGuide.reward(Object.assign({ type: 'lesson_complete' }, info || {}));
      }
      if (opened !== 'stage') {
        burstConfetti();
        reactMascot('lesson_complete');
      }
    },
  };

  // E10 phase 4: any fetch whose JSON answer carries badges (the server sets X-PB-Milestones) plays them, whoever made the call.
  if (window.fetch && !window.fetch.pbMilestones) {
    var plainFetch = window.fetch;
    // E10 review fix 3: a quiz question page is quiet, so a same-origin call made from one says so (X-PB-Quiz) and the server keeps
    // any badge or moment for the results page instead of sending it in an answer that would be dropped.
    var fromQuestionPage = function (input) {
      var body = document.body;
      if (!body || !body.hasAttribute('data-guide-quiz') || body.hasAttribute('data-guide-quiz-results')) return false;
      var url = typeof input === 'string' ? input : (input && input.url) || '';
      return (url.charAt(0) === '/' && url.charAt(1) !== '/') || url.indexOf(location.origin + '/') === 0;
    };
    var watchedFetch = function (input, init) {
      var args = arguments;
      try {
        if (fromQuestionPage(input)) {
          var headers = new Headers((init && init.headers) || (input && input.headers) || undefined);
          headers.set('X-PB-Quiz', '1');
          args = (typeof Request !== 'undefined' && input instanceof Request && !init)
            ? [new Request(input, { headers: headers })]
            : [input, Object.assign({}, init, { headers: headers })];
        }
      } catch (err) { args = arguments; }
      return plainFetch.apply(this, args).then(function (res) {
        try {
          if (res && res.headers && res.headers.get('X-PB-Milestones')) {
            res.clone().json().then(fromPayload, function () {});
          }
        } catch (err) { /* the answer itself is untouched */ }
        return res;
      });
    };
    watchedFetch.pbMilestones = true;
    window.fetch = watchedFetch;
  }

  // E10 phase 5: "Got there with a hint." when a right answer follows a hint (events from site.js; the line itself is in moments.js)
  var hinted = false;
  document.addEventListener('pb-hint-shown', function () { hinted = true; });
  document.addEventListener('pb-answer-checked', function (e) {
    if (!(e.detail && e.detail.correct && hinted)) return;
    hinted = false;
    handOver([{ type: 'micro', id: 'micro:hint', kind: 'hint' }]);
  });

  scanPageTriggers();
})();
