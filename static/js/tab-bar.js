(function () {
  'use strict';

  document.querySelectorAll('.page-shell').forEach(function (shell) {
    shell.classList.add('page-enter');
  });

  var bar = document.getElementById('app-tab-bar');
  if (!bar || window.matchMedia('(min-width: 900px)').matches) {
    return;
  }
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  var lastY = window.scrollY || 0;
  var hidden = false;
  var ticking = false;

  function onScroll() {
    var y = window.scrollY || 0;
    if (y > lastY && y > 96) {
      if (!hidden) {
        bar.classList.add('is-hidden');
        hidden = true;
      }
    } else if (y < lastY || y <= 48) {
      if (hidden) {
        bar.classList.remove('is-hidden');
        hidden = false;
      }
    }
    lastY = y;
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(onScroll);
      ticking = true;
    }
  }, { passive: true });
})();
