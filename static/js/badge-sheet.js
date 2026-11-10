/* Badge detail sheet on the profile (E10 phase 4). A badge button opens a native modal <dialog> (focus stays inside, Esc closes, focus
   goes back to the badge). Filled from the button's data-* attributes with textContent only; no markup from data. */
(function () {
  'use strict';
  var sheet = document.getElementById('badge-sheet');
  if (!sheet || typeof sheet.showModal !== 'function') return;
  var medal = document.getElementById('badge-sheet-medal');
  var els = {
    title: document.getElementById('badge-sheet-title'),
    blurb: document.getElementById('badge-sheet-blurb'),
    date: document.getElementById('badge-sheet-date'),
    next: document.getElementById('badge-sheet-next')
  };

  function prettyDate(iso) {
    var d = new Date(iso + 'T00:00:00');
    if (isNaN(d.getTime())) return iso;
    try { return d.toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { return iso; }
  }

  function open(btn) {
    var earned = btn.getAttribute('data-earned') === '1';
    var family = btn.getAttribute('data-family');
    medal.className = 'bd-medal bd-medal--' + (btn.getAttribute('data-tier') || 'bronze') + (family === 'streak' ? ' bd-medal--streak' : '') + (earned ? '' : ' is-locked');
    medal.firstChild.textContent = btn.getAttribute('data-emoji') || '★';
    els.title.textContent = btn.getAttribute('data-title');
    els.blurb.textContent = earned ? btn.getAttribute('data-blurb') : 'How to earn it: ' + btn.getAttribute('data-how');
    els.date.textContent = earned ? 'Earned on ' + prettyDate(btn.getAttribute('data-date')) + '.' : '';
    var nextTitle = btn.getAttribute('data-next-title');
    els.next.textContent = nextTitle ? 'Next: ' + nextTitle + '. ' + (btn.getAttribute('data-next-how') || '') : '';
    sheet.showModal();
    document.getElementById('badge-sheet-close').focus();
  }

  document.addEventListener('click', function (e) {
    var open1 = e.target.closest && e.target.closest('[data-badge-id]');
    var link = e.target.closest && e.target.closest('[data-badge-open]');
    if (open1) { open(open1); return; }
    if (link) {
      var btn = document.querySelector('[data-badge-id="' + link.getAttribute('data-badge-open') + '"]');
      if (btn) open(btn);
      return;
    }
    if (e.target === sheet || e.target.id === 'badge-sheet-close') sheet.close();   // the backdrop is the dialog itself
  });
}());
