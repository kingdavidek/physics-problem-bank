(function () {
  'use strict';

  var correctStreak = 0;
  var lastBurstAt = 0;
  var STREAK_ROUNDS = { 7: 1, 30: 1, 100: 1 };
  var LS_MILESTONE = 'pb-u74-ms-';
  var LS_STREAK = 'pb-u74-streak-';
  var CHECK_MARK_SVG =
    '<circle class="answer-check-mark-ring" cx="12" cy="12" r="10"/>' +
    '<path class="answer-check-mark-tick" d="M7 12.5l3.2 3.2L17 8.8"/>';

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
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

  function showXpFloat(anchor, points) {
    var label = '+' + points + ' XP';
    if (anchor && anchor.appendChild) {
      var prev = anchor.querySelector('.answer-xp-float');
      if (prev) prev.remove();
      anchor.classList.add('is-celebrate-host');
      var floatEl = document.createElement('span');
      floatEl.className = 'answer-xp-float';
      floatEl.setAttribute('aria-hidden', 'true');
      floatEl.textContent = label;
      anchor.appendChild(floatEl);
      window.setTimeout(function () { floatEl.remove(); }, prefersReducedMotion() ? 900 : 1300);
      return;
    }
    var host = toastHost();
    if (!host) return;
    var el = document.createElement('div');
    el.className = 'xp-toast';
    el.textContent = label;
    host.appendChild(el);
    window.setTimeout(function () {
      el.classList.add('is-gone');
      window.setTimeout(function () { el.remove(); }, 280);
    }, 1400);
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

  function burstConfetti() {
    if (prefersReducedMotion()) return;
    if (window.pbSound && window.pbSound.celebrate) window.pbSound.celebrate();
    var now = Date.now();
    if (now - lastBurstAt < 1600) return;
    lastBurstAt = now;
    var root = document.createElement('div');
    root.className = 'confetti-burst';
    root.setAttribute('aria-hidden', 'true');
    var palettes = 5;
    for (var i = 0; i < 40; i += 1) {
      var bit = document.createElement('span');
      bit.className = 'confetti-bit confetti-bit--' + (i % palettes);
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
    var xp = typeof points === 'number' ? points : 10;
    if (window.pbSound && window.pbSound.correct) window.pbSound.correct();
    if (anchor && !prefersReducedMotion()) {
      anchor.classList.add('is-pop');
      window.setTimeout(function () { anchor.classList.remove('is-pop'); }, 420);
    }
    drawCheckmark(anchor);
    showXpFloat(anchor, xp);
    if (correctStreak >= 3) {
      burstConfetti();
      correctStreak = 0;
    }
  }

  function celebrateWrong(target, correctTarget) {
    correctStreak = 0;
    if (window.pbSound && window.pbSound.wrong) window.pbSound.wrong();
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

  function celebrateMilestone(key) {
    var token = String(key || 'badge').replace(/\s+/g, '_');
    if (claimed(LS_MILESTONE + token)) return false;
    burstConfetti();
    return true;
  }

  function celebrateStreakRound(days) {
    var n = parseInt(days, 10);
    if (!STREAK_ROUNDS[n]) return false;
    if (claimed(LS_STREAK + n)) return false;
    burstConfetti();
    return true;
  }

  function fromPayload(data) {
    if (!data) return;
    var keys = data.new_milestones || data.awarded_milestones;
    if (Array.isArray(keys)) {
      keys.forEach(function (key) { celebrateMilestone(key); });
    }
    if (data.milestone_key) celebrateMilestone(data.milestone_key);
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
    var promptEl = document.getElementById('pb-buddy-prompt');
    var buddyRoot = document.querySelector('[data-buddy-root]');
    if (promptEl && buddyRoot && !buddyRoot.hidden) {
      try {
        fromBuddyPrompt(JSON.parse(promptEl.textContent || 'null'));
      } catch (err) {}
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
    fromBuddy: fromBuddyPrompt,
    lessonComplete: function () {
      showXpFloat(null, 25);
      burstConfetti();
      correctStreak = 0;
    },
  };

  scanPageTriggers();
})();
