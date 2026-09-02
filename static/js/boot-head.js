(function () {
  try {
    var standalone = (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches)
      || window.navigator.standalone === true;
    if (standalone) document.documentElement.classList.add('pwa-standalone');
  } catch (e) {}
  try {
    var stored = localStorage.getItem('pb-theme');
    if (stored && ['system', 'light', 'dark'].indexOf(stored) >= 0) {
      document.documentElement.setAttribute('data-theme', stored);
    }
  } catch (e) {}
})();
