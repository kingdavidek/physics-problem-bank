(function () {
  'use strict';

  var openBtn = document.getElementById('nav-menu-open');
  var panel = document.getElementById('nav-menu-panel');
  var backdrop = document.getElementById('nav-menu-backdrop');
  var closeBtn = document.getElementById('nav-menu-close');
  if (!openBtn || !panel) return;

  var isOpen = false;

  function isMobileSheet() {
    return window.matchMedia('(max-width: 640px)').matches;
  }

  function openPanel() {
    isOpen = true;
    panel.hidden = false;
    openBtn.setAttribute('aria-expanded', 'true');
    if (isMobileSheet()) {
      document.body.classList.add('nav-menu-open');
      if (backdrop) backdrop.hidden = false;
    }
  }

  function closePanel() {
    isOpen = false;
    panel.hidden = true;
    openBtn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('nav-menu-open');
    if (backdrop) backdrop.hidden = true;
  }

  openBtn.addEventListener('click', function (event) {
    event.stopPropagation();
    if (isOpen) closePanel();
    else openPanel();
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', function (event) {
      event.stopPropagation();
      closePanel();
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', closePanel);
  }

  document.addEventListener('click', function (event) {
    if (!isOpen) return;
    if (event.target.closest('.nav-menu-wrap')) return;
    closePanel();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && isOpen) closePanel();
  });

  if (window.matchMedia) {
    window.matchMedia('(max-width: 640px)').addEventListener('change', function (event) {
      if (!isOpen) return;
      if (event.matches) {
        document.body.classList.add('nav-menu-open');
        if (backdrop) backdrop.hidden = false;
      } else {
        document.body.classList.remove('nav-menu-open');
        if (backdrop) backdrop.hidden = true;
      }
    });
  }
})();
