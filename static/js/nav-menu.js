(function () {
  'use strict';

  var openBtn = document.getElementById('nav-menu-open');
  var panel = document.getElementById('nav-menu-panel');
  if (!openBtn || !panel) return;

  var isOpen = false;

  function openPanel() {
    isOpen = true;
    panel.hidden = false;
    openBtn.setAttribute('aria-expanded', 'true');
  }

  function closePanel() {
    isOpen = false;
    panel.hidden = true;
    openBtn.setAttribute('aria-expanded', 'false');
  }

  openBtn.addEventListener('click', function (event) {
    event.stopPropagation();
    if (isOpen) closePanel();
    else openPanel();
  });

  document.addEventListener('click', function (event) {
    if (!isOpen) return;
    if (event.target.closest('.nav-menu-wrap')) return;
    closePanel();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && isOpen) closePanel();
  });
})();
