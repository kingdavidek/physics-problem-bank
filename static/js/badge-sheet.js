/* Badge detail sheet on the profile (E10 phase 4). A badge button opens a native modal <dialog> (focus stays inside, Esc closes, focus
   goes back to the badge). Filled with textContent only; no markup from data.
   E11 Phase 3: the sheet reads every badge from the #pb-badge-data island by key, so a row, Next up and a wardrobe "Earn ... to unlock"
   link all open it, whether or not the badge has a button on the shelf. Watch again replays an earned badge's celebration on the badge
   stage (window.pbGuide.badges, the same stage the badge played on when it was earned). */
(function () {
  'use strict';
  var sheet = document.getElementById('badge-sheet');
  if (!sheet || typeof sheet.showModal !== 'function') return;
  var data = {};
  try { data = JSON.parse((document.getElementById('pb-badge-data') || {}).textContent || '{}') || {}; } catch (e) { data = {}; }
  var medal = document.getElementById('badge-sheet-medal');
  var replay = document.getElementById('badge-sheet-replay');
  var els = {
    title: document.getElementById('badge-sheet-title'),
    blurb: document.getElementById('badge-sheet-blurb'),
    date: document.getElementById('badge-sheet-date'),
    next: document.getElementById('badge-sheet-next')
  };
  var shown = '';

  function prettyDate(iso) {
    var d = new Date(iso + 'T00:00:00');
    if (isNaN(d.getTime())) return iso;
    try { return d.toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { return iso; }
  }

  function canReplay() { return !!(window.pbGuide && typeof window.pbGuide.badges === 'function'); }

  function open(key) {
    var b = data[key];
    if (!b) return;
    shown = key;
    medal.className = 'bd-medal bd-medal--' + (b.tier || 'bronze') + (b.family === 'streak' ? ' bd-medal--streak' : '') + (b.earned ? '' : ' is-locked');
    medal.firstChild.textContent = b.emoji || '★';
    els.title.textContent = b.title || '';
    els.blurb.textContent = b.earned ? (b.blurb || '') : 'How to earn it: ' + (b.how || '');
    els.date.textContent = b.earned && b.date ? 'Earned on ' + prettyDate(b.date) + '.' : '';
    els.next.textContent = b.next_title ? 'Next: ' + b.next_title + '. ' + (b.next_how || '') : '';
    if (replay) replay.hidden = !(b.earned && canReplay());
    sheet.showModal();
    document.getElementById('badge-sheet-close').focus();
  }

  function watchAgain() {
    var b = data[shown];
    if (!b || !b.earned || !canReplay()) return;
    sheet.close();
    var badge = { key: shown, title: b.title, blurb: b.blurb, family: b.family, emoji: b.emoji, tier: b.tier, next_title: b.next_title || '', next_how: b.next_how || '' };
    window.pbGuide.badges([{ type: 'milestone', key: shown, badge: badge, replay: true }]).catch(function () {});
  }

  document.addEventListener('click', function (e) {
    var hit = e.target.closest && e.target.closest('[data-badge-id], [data-badge-open]');
    if (hit) { open(hit.getAttribute('data-badge-id') || hit.getAttribute('data-badge-open')); return; }
    if (e.target === replay) { watchAgain(); return; }
    if (e.target === sheet || e.target.id === 'badge-sheet-close') sheet.close();   // the backdrop is the dialog itself
  });
}());
