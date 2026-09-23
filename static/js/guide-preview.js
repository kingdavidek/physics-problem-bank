(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  function wireZorpDemo(scope) {
    var z = window.pbZorp;
    if (!z || !scope) return;
    var demos = scope.querySelectorAll('[data-zorp-demo]');
    for (var d = 0; d < demos.length; d += 1) z.bind(demos[d]);
    var level = scope.querySelector('[data-zorp-motion-level]');
    if (level) level.textContent = 'motionLevel(): ' + z.motionLevel();
    var btns = scope.querySelectorAll('[data-zorp-clip]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function (event) {
        var btn = event.currentTarget;
        for (var k = 0; k < demos.length; k += 1) {
          z.play(btn.getAttribute('data-zorp-clip'), { el: demos[k], target: btn.getAttribute('data-zorp-target') || undefined });
        }
      });
    }
    var off = scope.querySelector('[data-zorp-idle-off]');
    if (off) off.addEventListener('click', function () { for (var k = 0; k < demos.length; k += 1) z.idle(false, demos[k]); });
  }

  ready(function () {
    wireZorpDemo(document.getElementById('guide-preview-motion-section'));
    if (!window.pbGuide) return;
    var playBtn = document.getElementById('guide-preview-play');
    var resetBtn = document.getElementById('guide-preview-reset');
    var badgeBtn = document.getElementById('guide-preview-badge');
    var streakBtn = document.getElementById('guide-preview-streak');
    var practiceBtn = document.getElementById('guide-preview-practice');
    var profileBtn = document.getElementById('guide-preview-profile');
    var dailyBtn = document.getElementById('guide-preview-daily');
    var learnBtn = document.getElementById('guide-preview-learn');
    var competeBtn = document.getElementById('guide-preview-compete');
    var firstBtn = document.getElementById('guide-preview-first');
    var lessonBtn = document.getElementById('guide-preview-lesson');
    var winkBtn = document.getElementById('guide-preview-wink');
    var nodBtn = document.getElementById('guide-preview-nod');
    var shakeBtn = document.getElementById('guide-preview-shake');
    var tapBtn = document.getElementById('guide-preview-tap');

    if (playBtn) {
      playBtn.addEventListener('click', function () {
        window.pbGuide.play('origin');
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        window.pbGuide.resetOrigin();
        window.pbGuide.play('origin');
      });
    }
    if (badgeBtn) {
      badgeBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'milestone', key: 'first_quiz' });
      });
    }
    if (streakBtn) {
      streakBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'streak', days: 7 });
      });
    }
    if (practiceBtn) {
      practiceBtn.addEventListener('click', function () {
        window.pbGuide.play('practice');
      });
    }
    if (profileBtn) {
      profileBtn.addEventListener('click', function () {
        window.pbGuide.play('profile');
      });
    }
    if (dailyBtn) {
      dailyBtn.addEventListener('click', function () {
        window.pbGuide.play('daily');
      });
    }
    if (learnBtn) {
      learnBtn.addEventListener('click', function () {
        window.pbGuide.play('learn');
      });
    }
    if (competeBtn) {
      competeBtn.addEventListener('click', function () {
        window.pbGuide.play('compete');
      });
    }
    if (firstBtn) {
      firstBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'first_correct' });
      });
    }
    if (lessonBtn) {
      lessonBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'lesson_complete' });
      });
    }
    function bindGesture(btn, name) {
      if (!btn) return;
      btn.addEventListener('click', function () {
        if (window.pbGuide && typeof window.pbGuide.gesture === 'function') {
          window.pbGuide.gesture(name);
        }
      });
    }
    bindGesture(winkBtn, 'wink');
    bindGesture(nodBtn, 'nod');
    bindGesture(shakeBtn, 'shake');
    bindGesture(tapBtn, 'tap');
  });
})();
