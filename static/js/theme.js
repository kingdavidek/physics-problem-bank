(function () {
  'use strict';

  var STORAGE_KEY = 'pb-theme';
  var COOKIE_KEY = 'pb_theme';
  var META_LIGHT = '#1a86d4';
  var META_DARK = '#0f1724';
  var CHOICES = ['system', 'light', 'dark'];

  function normalize(theme) {
    return CHOICES.indexOf(theme) >= 0 ? theme : 'system';
  }

  function effectiveDark(theme) {
    theme = normalize(theme);
    if (theme === 'dark') return true;
    if (theme === 'light') return false;
    try {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch (e) {
      return false;
    }
  }

  function setCookie(theme) {
    document.cookie = COOKIE_KEY + '=' + encodeURIComponent(theme) +
      ';path=/;max-age=31536000;SameSite=Lax';
  }

  function updateChrome(theme) {
    var dark = effectiveDark(theme);
    var color = dark ? META_DARK : META_LIGHT;
    document.querySelectorAll('meta[name="theme-color"]:not([media])').forEach(function (meta) {
      meta.content = color;
    });
    document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    theme = normalize(theme);
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {}
    setCookie(theme);
    updateChrome(theme);
  }

  window.pbTheme = {
    apply: applyTheme,
    effectiveDark: effectiveDark,
    normalize: normalize,
  };

  var current = document.documentElement.getAttribute('data-theme') || 'system';
  updateChrome(current);

  try {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
      var active = document.documentElement.getAttribute('data-theme') || 'system';
      if (active === 'system') updateChrome('system');
    });
  } catch (e) {}

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[name="theme_preference"]').forEach(function (input) {
      input.addEventListener('change', function () {
        applyTheme(input.value);
      });
    });
  });
})();
