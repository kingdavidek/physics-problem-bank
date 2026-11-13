/* Celebrations gallery (dev only, /celebrations-gallery). Plays every badge and every celebration on the real stage, cards and reactions:
   badges through pbGuide.badges (the badge stage, no seen-state check), stage moments through pbMoments.sequence (the same one-sequence
   player the site uses), cards through pbMoments.toast. The page is in preview mode, so the guide state is never saved. Each card gets a
   fresh id, because a card shows once per id in a browser session. The Sounds section plays each celebration sound alone. */
(function () {
  'use strict';
  var D = document;
  var root = D.getElementById('celebrations-gallery');
  if (!root) return;
  function G() { return window.pbGuide || null; }
  function island(id) { try { return JSON.parse((D.getElementById(id) || {}).textContent || 'null'); } catch (e) { return null; } }
  var rows = island('gallery-badges') || [];
  var n = 0;
  function uid(prefix) { n += 1; return prefix + ':gallery' + Date.now().toString(36) + n; }

  function addAsset(tag, attrs) {
    return new Promise(function (ok, fail) {
      var node = D.createElement(tag);
      Object.keys(attrs).forEach(function (k) { node.setAttribute(k, attrs[k]); });
      node.onload = ok;
      node.onerror = fail;
      D.head.appendChild(node);
    });
  }
  // the badge stage and the moments player, loaded the way guide.js loads them (the URLs come from the page's asset islands)
  var loading = null;
  function players() {
    if (window.pbMoments && window.pbBadgeStage) return Promise.resolve();
    if (loading) return loading;
    var m = island('pb-moment-assets');
    var b = island('pb-badge-assets');
    loading = G().loadStage().then(function () {
      var list = [];
      if (!window.pbBadgeStage && b) list.push(addAsset('link', { rel: 'stylesheet', href: b.css }), addAsset('script', { src: b.js }));
      if (!window.pbMoments && m) list.push(addAsset('link', { rel: 'stylesheet', href: m.css }), addAsset('script', { src: m.js }));
      return Promise.all(list);
    });
    loading.catch(function () { loading = null; });
    return loading;
  }

  function badgeAt(ref) {
    var p = String(ref).split(':');
    var row = rows[parseInt(p[0], 10)];
    return row ? row.badges[parseInt(p[1], 10)] : null;
  }
  function spec(b) { return { type: 'milestone', key: b.key, badge: b }; }
  function topicBadge() { return badgeAt((rows.length - 1) + ':0'); }

  // ---- stage moments ----
  var LESSON = { type: 'lesson_complete', level: 'gcse', subject: 'maths', topic: 'bidmas', name: 'Order of Operations & Negatives', quiz: '/lesson-quiz/gcse/maths/bidmas' };
  function week(part) {
    return { type: 'week', id: 'wk:gallery', part: part, days: 4, dots: '1101100', count: 37, best: 'badge', title: 'Quiz fan' };
  }
  function moment(name) {
    var front = [];
    var badges = [];
    var back = [];
    if (name === 'level') back = [{ type: 'level', id: uid('level'), level: 4, pct: 0.35 }];
    else if (name === 'perfect') front = [{ type: 'perfect', id: uid('perfect'), score: 10, total: 10 }];
    else if (name === 'lesson') front = [Object.assign({}, LESSON, { more: false })];
    else if (name === 'lesson_more') front = [Object.assign({}, LESSON, { more: true })];
    else if (name === 'lesson_badge') { var t = topicBadge(); front = [Object.assign({}, LESSON, { more: false, badge: { key: t.key, title: t.title } })]; }
    else if (name === 'week') front = [week('days'), week('right'), week('best')];
    else if (name === 'sequence') {
      front = [Object.assign({}, LESSON, { more: false })];
      badges = [spec(badgeAt('1:1'))];   // three cards, the most one sequence holds on the site (moments.js MAX_CARDS)
      back = [{ type: 'level', id: uid('level'), level: 5, pct: 0.1 }];
    }
    players().then(function () { return window.pbMoments.sequence(front, badges, back); }).catch(function () {});
  }

  // ---- corner cards ----
  var CARDS = [
    ['quiz_done', 'Quiz done', { score: 7, total: 10, wrong: 3 }],
    ['personal_best', 'Personal best', { score: 8, total: 10 }],
    ['quicktest_done', 'Quick Test done', { score: 9, total: 12 }],
    ['quicktest_perfect', 'Quick Test full marks', { score: 12, total: 12 }],
    ['retry_cleared', 'All fixed (a retry)', {}],
    ['daily_week', 'Daily question all week', {}],
    ['set_work_done', 'Set work done', {}],
    ['challenge_done', 'Challenge done', { score: 8, total: 10 }],
    ['streak_skip', 'Weekly skip used', {}],
    ['first_correct', 'First right answer', {}],
    ['welcome_back', 'Welcome back', {}],
    ['welcome_back_kept', 'Welcome back (streak kept)', {}],
    ['near_badge', 'Close to a badge', { title: 'Quiz fan', line: 'Finish one more quiz.' }],
    ['backfill', 'Back-filled badge (one)', { count: 1, title: 'Full marks' }],
    ['backfill', 'Back-filled badges (many)', { count: 4, title: 'Quiz fan' }],
    ['badge_card', 'A badge as a card', { title: 'Quiz fan' }],
    ['badges_card', 'Badges as one card', { count: 3, title: 'Quiz fan, Curious and Bounce back' }],
    ['streak_card', 'Streak as a card', { days: 7 }],
    ['level_card', 'Level up as a card', { level: 4 }],
    ['perfect_card', '10/10 as a card', { score: 10, total: 10 }],
    ['lesson_card', 'Lesson complete as a card', { quiz: '/lesson-quiz/gcse/maths/bidmas' }],
    ['lesson_card', 'Lesson complete with badge, as a card', { title: 'Order of Operations & Negatives lesson complete', quiz: '/lesson-quiz/gcse/maths/bidmas' }],
    ['week_card', 'Your week as a card', { days: 4 }],
    ['perfect_set', 'The 10/10 small-card setting saved', {}]
  ];
  function card(i) {
    var c = CARDS[i];
    players().then(function () { window.pbMoments.toast(Object.assign({ type: 'toast', id: uid('toast'), kind: c[0] }, c[2])); }).catch(function () {});
  }
  var host = D.getElementById('gallery-cards');
  CARDS.forEach(function (c, i) {
    var btn = D.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-outline btn-sm';
    btn.textContent = c[1];
    btn.setAttribute('data-gal-card', String(i));
    host.appendChild(btn);
  });

  // ---- sounds (docs/CELEBRATION_SOUNDS_PLAN.md): each one alone, and a switch that lets this page's celebrations sound as a pupil's do.
  // force (a dev page, like the styleguide) skips the setting, the tap and the gap; the switch sets html[data-zorp-sound] here only. ----
  var SOUNDS = [['whoosh', 'Whoosh (a badge stage opens)'], ['stamp-bronze', 'Stamp, bronze'], ['stamp-silver', 'Stamp, silver'],
    ['stamp-gold', 'Stamp, gold'], ['stamp-violet', 'Stamp, violet (100 days)'], ['sparkle', 'Sparkle (Full marks line)'],
    ['sprout', 'Sprout (Recovery line)'], ['fire', 'Fire (streaks)'], ['gem', 'Gem (10/10)'], ['confetti', 'Confetti fizz (10/10)'],
    ['level', 'Level up'], ['book', 'Lesson complete'], ['week', 'Your week (three notes)'], ['story', 'Story chapter'], ['pop', 'Corner card pop']];
  var soft = root.querySelector('[data-gal-soft]');
  var withSound = root.querySelector('[data-gal-with-sound]');
  var html = D.documentElement;
  var mode0 = html.getAttribute('data-zorp-sound') || 'off';
  function hear(name) {
    var s = window.pbSound;
    if (!s || !s.play) return;
    var o = { soft: !!(soft && soft.checked) };
    if (name !== 'week') { s.play(name, Object.assign({ force: true }, o)); return; }
    [0, 1, 2].forEach(function (k) { setTimeout(function () { s.play('week', Object.assign({ force: true, step: k }, o)); }, k * 450); });
  }
  var list = D.getElementById('gallery-sounds-list');
  SOUNDS.forEach(function (x) {
    var btn = D.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-outline btn-sm';
    btn.textContent = x[1];
    btn.setAttribute('data-gal-sound', x[0]);
    if (list) list.appendChild(btn);
  });
  if (withSound) {
    withSound.checked = mode0 === 'celebrations';
    withSound.addEventListener('change', function () {
      html.setAttribute('data-zorp-sound', withSound.checked ? 'celebrations' : 'off');
      if (window.pbSound) { if (withSound.checked) window.pbSound.arm(); else window.pbSound.stopAll(); }
    });
    // the stage's speaker button flips the same attribute (preview: nothing saved); keep the switch honest
    D.addEventListener('pb-stage-closed', function () { withSound.checked = html.getAttribute('data-zorp-sound') === 'celebrations'; });
  }

  root.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('button, a') : null;
    if (!t || !root.contains(t)) return;
    var g = G();
    var a;
    if (t.hasAttribute('data-gal-noop')) { e.preventDefault(); return; }
    if ((a = t.getAttribute('data-gal-sound'))) { hear(a); return; }
    if ((a = t.getAttribute('data-gal-badge'))) { var b = badgeAt(a); if (b && g) g.badges([spec(b)]).catch(function () {}); return; }
    if ((a = t.getAttribute('data-gal-badge-card'))) {
      var b2 = badgeAt(a);
      if (b2) players().then(function () { window.pbMoments.toast({ type: 'toast', id: uid('toast'), kind: 'badge_card', title: b2.title }); });
      return;
    }
    if ((a = t.getAttribute('data-gal-line'))) { var row = rows[parseInt(a, 10)]; if (row && g) g.badges(row.badges.map(spec)).catch(function () {}); return; }
    if ((a = t.getAttribute('data-gal-moment'))) { moment(a); return; }
    if ((a = t.getAttribute('data-gal-streak'))) { if (g) g.badges([{ type: 'streak', days: parseInt(a, 10) }]).catch(function () {}); return; }
    if ((a = t.getAttribute('data-gal-card'))) {
      if (a === 'all') CARDS.forEach(function (c, i) { setTimeout(function () { card(i); }, i * 400); });
      else card(parseInt(a, 10));
      return;
    }
    if ((a = t.getAttribute('data-gal-xp'))) { if (window.pbCelebrate && window.pbCelebrate.xp) window.pbCelebrate.xp(parseInt(a, 10)); return; }
    if ((a = t.getAttribute('data-gal-story'))) { if (g) g.story(parseInt(a, 10)).catch(function () {}); return; }
    if ((a = t.getAttribute('data-gal-offer'))) { if (g) g.offerStory(parseInt(a, 10)).catch(function () {}); return; }
    if (t.hasAttribute('data-gal-refill')) {
      var fill = root.querySelector('.results-level-fill');
      if (fill) { fill.style.animation = 'none'; void fill.offsetWidth; fill.style.animation = ''; }
    }
  });
}());
