/* E7 Phase 4: declarative Zorp clip triggers for server-rendered pages.
   An element with data-zorp-autoplay="<name>" plays that clip once, as soon as this script
   runs. It's loaded `defer` immediately after zorp-motion.js in base.html, so by the time its
   own top-level code executes, every earlier `defer` script — including zorp-motion.js — has
   already run and window.pbZorp is guaranteed to exist (browsers run `defer` scripts in
   document order before firing DOMContentLoaded; `document.readyState` is already
   'interactive' at that point, not 'loading', which is why this runs immediately rather than
   waiting for a 'DOMContentLoaded' listener to fire separately).

   This exists instead of inline <script> blocks because the app's CSP has no
   'unsafe-inline' for script-src and inline blocks would either be silently blocked or (if
   they predated the nonce requirement) run before zorp-motion.js's deferred script had
   defined window.pbZorp.

   Named "data-zorp-autoplay" (not "data-zorp-clip") deliberately: static/js/styleguide.js and
   static/js/guide-preview.js already use "data-zorp-clip" on their dev-demo buttons for
   click-triggered playback — a different attribute avoids this script also matching (and
   auto-firing on load) those unrelated buttons.

   Optional attributes:
   - data-zorp-autoplay-once-key="<prefix>": gate the clip to once per UTC day via
     localStorage, using the same date-suffixed key shape as static/js/study-buddy.js's daily
     flags.
   - data-zorp-autoplay-delay="<ms>": wait this long before playing (e.g. so it doesn't
     collide with another animation already running on the same element, like the streak
     ring's own 800ms draw-on). */
(function () {
  'use strict';

  function utcDayKey(prefix) {
    return prefix + '-' + new Date().toISOString().slice(0, 10);
  }

  function trigger(el) {
    var clip = el.getAttribute('data-zorp-autoplay');
    if (!clip) return;
    var onceKey = el.getAttribute('data-zorp-autoplay-once-key');
    if (onceKey) {
      try {
        if (window.localStorage.getItem(utcDayKey(onceKey)) === '1') return;
      } catch (e) { /* localStorage unavailable — treat as not-yet-shown */ }
    }
    window.pbZorp.play(clip, { el: el });
    if (onceKey) {
      try { window.localStorage.setItem(utcDayKey(onceKey), '1'); } catch (e) { /* ignore */ }
    }
  }

  function run() {
    if (!window.pbZorp || typeof window.pbZorp.play !== 'function') return;
    var els = document.querySelectorAll('[data-zorp-autoplay]');
    var i;
    for (i = 0; i < els.length; i += 1) {
      (function (el) {
        var delay = parseInt(el.getAttribute('data-zorp-autoplay-delay'), 10) || 0;
        if (delay > 0) window.setTimeout(function () { trigger(el); }, delay);
        else trigger(el);
      }(els[i]));
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
}());
