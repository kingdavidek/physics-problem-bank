(function () {
  'use strict';

  var correctStreak = 0;
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

  function burstConfetti() {
    if (prefersReducedMotion()) return;
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

  window.pbCelebrate = {
    correct: celebrateCorrect,
    wrong: celebrateWrong,
    confetti: burstConfetti,
    lessonComplete: function () {
      showXpFloat(null, 25);
      burstConfetti();
      correctStreak = 0;
    },
  };
})();
