(function () {
  'use strict';

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var correctStreak = 0;

  function toastHost() {
    return document.getElementById('app-toast-host');
  }

  function showXpToast(points) {
    var host = toastHost();
    if (!host) return;
    var el = document.createElement('div');
    el.className = 'xp-toast';
    el.textContent = '+' + points + ' XP';
    host.appendChild(el);
    window.setTimeout(function () {
      el.classList.add('is-gone');
      window.setTimeout(function () { el.remove(); }, 280);
    }, 1400);
  }

  function burstConfetti() {
    if (reduceMotion) return;
    var root = document.createElement('div');
    root.className = 'confetti-burst';
    root.setAttribute('aria-hidden', 'true');
    var colors = ['#1a86d4', '#8b5cf6', '#eab308', '#22c55e', '#f59e0b'];
    for (var i = 0; i < 18; i += 1) {
      var bit = document.createElement('span');
      bit.className = 'confetti-bit';
      bit.style.background = colors[i % colors.length];
      bit.style.left = (40 + Math.random() * 20) + 'vw';
      bit.style.animationDelay = (Math.random() * 120) + 'ms';
      bit.style.setProperty('--drift', (Math.random() * 160 - 80) + 'px');
      root.appendChild(bit);
    }
    document.body.appendChild(root);
    window.setTimeout(function () { root.remove(); }, 900);
  }

  function celebrateCorrect(target) {
    correctStreak += 1;
    if (target && !reduceMotion) {
      target.classList.add('is-pop');
      window.setTimeout(function () { target.classList.remove('is-pop'); }, 420);
    }
    showXpToast(10);
    if (correctStreak >= 3) {
      burstConfetti();
      correctStreak = 0;
    }
  }

  function celebrateWrong(target, correctTarget) {
    correctStreak = 0;
    if (reduceMotion) return;
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
    lessonComplete: function () {
      showXpToast(25);
      burstConfetti();
      correctStreak = 0;
    },
  };
})();
