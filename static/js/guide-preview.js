(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
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
  });
})();
