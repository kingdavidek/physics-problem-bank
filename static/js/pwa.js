(function () {
  'use strict';

  function isStandalone() {
    try {
      if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
        return true;
      }
    } catch (e) {}
    return navigator.standalone === true;
  }

  function isIosSafari() {
    var ua = navigator.userAgent || '';
    var iOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    var webkit = /WebKit/i.test(ua);
    var notOther = !/CriOS|FxiOS|EdgiOS|OPiOS|Chrome|Android/i.test(ua);
    return iOS && webkit && notOther;
  }

  function markStandalone() {
    if (isStandalone()) {
      document.documentElement.classList.add('pwa-standalone');
      document.body && document.body.classList.add('pwa-standalone');
    }
  }

  markStandalone();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', markStandalone);
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
      if (storageGet('pb_buddy_sw_migrate') !== 'v4') {
        if ('caches' in window) {
          caches.keys().then(function (keys) {
            keys.forEach(function (key) {
              caches.delete(key);
            });
          });
        }
        navigator.serviceWorker.getRegistrations().then(function (regs) {
          regs.forEach(function (reg) {
            reg.update();
          });
        });
        storageSet('pb_buddy_sw_migrate', 'v4');
      }
    });
  }

  var deferredPrompt = null;
  var banner = document.getElementById('pwa-install-banner');
  var installBtn = document.getElementById('pwa-install-btn');
  var dismissBtn = document.getElementById('pwa-install-dismiss');
  var iosHint = document.getElementById('pwa-ios-hint');
  var iosDismiss = document.getElementById('pwa-ios-hint-dismiss');

  function storageGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }

  function storageSet(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {}
  }

  function chromeDismissed() {
    return storageGet('pwa_install_dismissed') === '1';
  }

  function iosDismissed() {
    return storageGet('pwa_ios_hint_dismissed') === '1';
  }

  function showBanner() {
    if (!banner || chromeDismissed() || isStandalone()) return;
    if (iosHint) iosHint.hidden = true;
    banner.hidden = false;
  }

  function hideBanner() {
    if (!banner) return;
    banner.hidden = true;
  }

  function showIosHint() {
    if (!iosHint || iosDismissed() || isStandalone() || !isIosSafari()) return;
    if (banner && !banner.hidden) return;
    iosHint.hidden = false;
  }

  function hideIosHint() {
    if (!iosHint) return;
    iosHint.hidden = true;
  }

  if (isStandalone()) {
    hideBanner();
    hideIosHint();
  }

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredPrompt = event;
    hideIosHint();
    showBanner();
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    hideBanner();
    hideIosHint();
    storageSet('pwa_install_dismissed', '1');
    storageSet('pwa_ios_hint_dismissed', '1');
    markStandalone();
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
      storageSet('pwa_install_dismissed', '1');
    });
  }

  if (iosDismiss) {
    iosDismiss.addEventListener('click', function () {
      hideIosHint();
      storageSet('pwa_ios_hint_dismissed', '1');
    });
  }

  // iOS has no beforeinstallprompt — soft A2HS tip after a short delay.
  if (!isStandalone() && isIosSafari() && !iosDismissed()) {
    window.setTimeout(function () {
      if (!deferredPrompt) showIosHint();
    }, 1800);
  }

  var offlineBar = document.getElementById('pwa-offline-bar');
  function syncOnlineState() {
    if (!offlineBar) return;
    offlineBar.hidden = navigator.onLine;
  }
  window.addEventListener('online', syncOnlineState);
  window.addEventListener('offline', syncOnlineState);
  syncOnlineState();
})();
