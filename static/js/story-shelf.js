/* Zorp's story shelf (E10 phase 8). Profile page only: a Watch button plays its chapter through pbGuide.story, which loads the chapter
   scenes only now; nothing about the chapters is fetched until a button is pressed. When a chapter has been watched
   the row says so and its button changes to Watch again. The shelf itself is server-rendered (templates/partials/story_shelf.html). */
(function () {
  'use strict';
  var D = document;
  var root = D.querySelector('[data-story-shelf]');
  var busy = false;
  if (!root) return;

  function row(n) { return root.querySelector('[data-story-item="' + n + '"]'); }

  root.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('[data-story-play]') : null;
    var g = window.pbGuide;
    if (!btn || !g || typeof g.story !== 'function') return;
    if (busy) return;
    busy = true;
    g.story(btn.getAttribute('data-story-play')).catch(function () { /* the page works without it */ }).then(function () { busy = false; });
  });

  D.addEventListener('pb-story-watched', function (e) {
    var item = row(e.detail && e.detail.n);
    if (!item) return;
    var state = item.querySelector('[data-story-state]');
    var label = item.querySelector('[data-story-label]');
    var btn = item.querySelector('[data-story-play]');
    if (state) state.textContent = 'Watched.';
    if (label) label.textContent = 'Watch again';
    if (btn) btn.setAttribute('aria-label', 'Watch again: ' + (item.querySelector('.sty-item-title') || {}).textContent);
  });
}());
