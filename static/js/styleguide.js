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
  });

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
})();
