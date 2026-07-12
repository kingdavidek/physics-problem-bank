(function () {
  'use strict';

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
    });
  }

  var deferredPrompt = null;
  var banner = document.getElementById('pwa-install-banner');
  var installBtn = document.getElementById('pwa-install-btn');
  var dismissBtn = document.getElementById('pwa-install-dismiss');

  function dismissed() {
    try {
      return localStorage.getItem('pwa_install_dismissed') === '1';
    } catch (e) {
      return false;
    }
  }

  function showBanner() {
    if (!banner || dismissed()) return;
    banner.hidden = false;
  }

  function hideBanner() {
    if (!banner) return;
    banner.hidden = true;
  }

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredPrompt = event;
    showBanner();
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    hideBanner();
    try {
      localStorage.setItem('pwa_install_dismissed', '1');
    } catch (e) {}
  });

  if (installBtn) {
    installBtn.addEventListener('click', function () {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      deferredPrompt.userChoice.finally(function () {
        deferredPrompt = null;
        hideBanner();
      });
    });
  }

  if (dismissBtn) {
    dismissBtn.addEventListener('click', function () {
      hideBanner();
      try {
        localStorage.setItem('pwa_install_dismissed', '1');
      } catch (e) {}
    });
  }

  // Online/offline indicator
  var offlineBar = document.getElementById('pwa-offline-bar');
  function syncOnlineState() {
    if (!offlineBar) return;
    offlineBar.hidden = navigator.onLine;
  }
  window.addEventListener('online', syncOnlineState);
  window.addEventListener('offline', syncOnlineState);
  syncOnlineState();
})();
