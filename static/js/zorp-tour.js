/* App tour and spotlights (E10 phase 6, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A3, A4 and section 10). guide.js loads this file
   and static/css/tour.css only when one is due (the #pb-tour-assets island); ordinary pages never fetch either.
   The tour ("Show me around") walks the app one page at a time: a small card with Zorp beside a real element (outlined, never
   covered), Next, and Skip tour (Esc does the same). Between pages Zorp turns side-on and hops along the tab bar (mobile) or the top
   nav (desktop) to the next tab, then the next page carries on. The step lives in the guide state ("run": {id: 'app', step}), so a
   reload or a new page loses nothing. A step whose element is not on the page is skipped. Finishing plays a short stage scene (Zorp
   bows) and then asks the server for the Pathfinder badge (POST /api/v1/me/tour/complete), which arrives by the ordinary badge delivery.
   Spotlights are one or two lines the first time a pupil meets a feature (hint, bigger hint, lesson quiz, Quick Test, AI explain,
   set work, challenge, revision plan, saved question): at most one per page view, never during a stage, the coach, a dialog or the tour.
   The tour and a spotlight never open over a stage or a dialog: they wait. UK English; every line follows docs/ZORP_CHARM.md 3.3
   (scripts/test_zorp_voice_smoke.py reads the COPY block). Faces come from models/zorp_rig.py CONTEXT_MAP['tour']. Motion: full =
   fade, a 6 px rise, Zorp's clips and the hop; reduced = a fade, and the hopper fades in at the next tab; off = nothing moves. */
(function () {
  'use strict';
  if (window.pbTour) return;

  var D = document;
  var W = window;
  // BEGIN COPY
  var UI = {
    primary: 'Next',
    skipLabel: 'Skip tour',
    finish: 'Finish',
    gotIt: 'Got it',
  };
  // The steps, in order. A step: id, page, heading (the page), target (selectors, the first one on show wins; panel:Name is the
  // settings panel with that header), open (a tab to open first), classOnly, lines, face and clip (full motion). `stop` groups the steps
  // of one stop (about fourteen stops, one to three steps each).
  var STEPS = [
    {
      id: 'practice.picker',
      stop: 'picker',
      page: 'practice',
      heading: 'Practice',
      target: '.practice-picker-card, .practice-picker-card .form-group',
      lines: ['This is Practice. Pick a subject and topic and I’ll make you a fresh question.'],
      face: 'happy',
      clip: 'wave',
    },
    {
      id: 'practice.mode',
      stop: 'picker',
      page: 'practice',
      heading: 'Practice',
      target: '#mode-row:not([hidden]), #difficulty-row',
      lines: ['Choose how hard it is. For GCSE you can pick Standard or Multiple Choice too.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    {
      id: 'practice.hints',
      stop: 'hints',
      page: 'practice',
      heading: 'Practice',
      target: 'details.answer-reveal, .free-response-hint, #mcq-options',
      lines: ['Stuck? After a try, a hint appears, and a bigger one if you need it. Show answer is below.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    {
      id: 'practice.save',
      stop: 'save',
      page: 'practice',
      heading: 'Practice',
      target: '#save-problem-form, #practice-action-bar',
      lines: ['Save a question to keep it for later, or share it with a friend.'],
      face: 'soft-smile',
      clip: 'nod',
    },
    {
      id: 'practice.quicktest',
      stop: 'quicktest',
      page: 'practice',
      heading: 'Quick test',
      target: '#quicktest-btn',
      lines: ['Quick test is a short run of questions. The results show your marks and let you retry the misses.'],
      face: 'happy',
      clip: 'side-point',
    },
    {
      id: 'learn.list',
      stop: 'learn',
      page: 'learn',
      heading: 'Learn',
      target: '.topic-group-title, #topics-grid',
      lines: ['Learn has a lesson for every topic. Open one to read it and try the quick checks.'],
      face: 'happy',
      clip: 'wave',
    },
    {
      id: 'learn.chips',
      stop: 'learn',
      page: 'learn',
      heading: 'Learn',
      target: '.topic-group-progress',
      lines: ['Here you can see how many lessons you’ve finished, and your ninja and master topics.'],
      face: 'proud',
      clip: 'nod',
    },
    {
      id: 'learn.quiz',
      stop: 'lessonquiz',
      page: 'learn',
      heading: 'Learn',
      target: '.topic-card',
      lines: ['Each lesson ends with a quiz. Afterwards you can retry the misses, or ask AI to explain one.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    {
      id: 'daily.today',
      stop: 'today',
      page: 'daily',
      heading: 'Daily',
      target: '.qotd-daily-card',
      lines: ['There’s a new question every day. Answer it whenever suits you.'],
      face: 'curious',
      clip: 'side-point',
    },
    {
      id: 'daily.board',
      stop: 'week',
      page: 'daily',
      heading: 'Daily',
      target: '#qotd-board, #qotd-board .section-panel-header',
      lines: ['Friends can see each other’s Daily answers. There is no public worldwide ranking.'],
      face: 'soft-smile',
      clip: 'nod',
    },
    {
      id: 'compete.board',
      stop: 'friends',
      page: 'compete',
      heading: 'Compete',
      target: '#leaderboard-board-tabs',
      lines: ['Switch between effort and accuracy for friends you follow. Nobody else is listed.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    {
      id: 'compete.challenges',
      stop: 'challenges',
      page: 'compete',
      heading: 'Compete',
      target: '#compete-challenges',
      lines: ['Challenges are optional: send a friend the same questions. There is no chat.'],
      face: 'wink',
      clip: 'nod',
    },
    {
      id: 'profile.streak',
      stop: 'streak',
      page: 'profile',
      heading: 'Profile',
      target: '.streak-panel, .streak-ring-wrap, .profile-stats-row',
      lines: ['Your streak and effort points live here. A weekly skip can cover a day you can’t study.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    {
      id: 'profile.badges',
      stop: 'progress',
      page: 'profile',
      heading: 'Profile',
      open: '#profile-tab-btn-progress',
      target: '#milestones .section-panel-header, #milestones',
      lines: ['Badges you earn are kept here, with what to aim for next.'],
      face: 'proud',
      clip: 'side-point',
    },
    {
      id: 'profile.revision',
      stop: 'progress',
      page: 'profile',
      heading: 'Profile',
      open: '#profile-tab-btn-progress',
      target: '#revision-plan, #revision-plan .section-panel-header',
      lines: ['Set an exam date and I’ll spread your weak topics across the days before it.'],
      face: 'soft-smile',
      clip: 'nod',
    },
    {
      id: 'profile.history',
      stop: 'history',
      page: 'profile',
      heading: 'Profile',
      open: '#profile-tab-btn-history',
      target: '#profile-tab-history .section-panel',
      lines: ['Saved questions and your quiz results are kept here, so you can look back any time.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    {
      id: 'classes.work',
      stop: 'classes',
      page: 'classes',
      heading: 'Classes',
      classOnly: 1,
      target: 'panel:My class work, .section-panel',
      lines: ['Set work from your teacher appears here. Each question can be answered once.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    {
      id: 'settings.motion',
      stop: 'settings',
      page: 'settings',
      heading: 'Settings',
      target: 'panel:Motion',
      lines: ['Choose light or dark, how much I move, and how I cheer, with or without sound.'],
      face: 'happy',
      clip: 'wave',
    },
    {
      id: 'settings.replay',
      stop: 'replay',
      page: 'settings',
      heading: 'Settings',
      target: '#guide-replay-tour',
      lines: ['You can replay the arrival or this tour from here whenever you like.'],
      face: 'grin',
      clip: 'nod',
    },
  ];
  // The end of the tour: a short stage scene, Zorp bows. Then the badge.
  var END = {
    id: 'tour.end',
    heading: 'The tour',
    props: [],
    layout: 'centre',
    face: 'happy',
    end: 'proud',
    lines: ['That’s the tour. Thanks for coming round with me.'],
    beats: [[{ burst: 1 }, { talk: 1 }, { play: 'bow' }]],
    primary: 'Continue',
  };
  // The spotlights: one or two lines, the first time a pupil meets a feature. `when` is how each is found (code below).
  var SPOTS = {
    hint: {
      id: 'sp.hint',
      lines: ['That’s a hint. It nudges you to the next step without giving the answer away.'],
      face: 'curious',
      clip: 'side-point',
    },
    bigger: {
      id: 'sp.bigger',
      lines: ['That’s a bigger hint, with the first step. Have another go from there.'],
      face: 'soft-smile',
      clip: 'nod',
    },
    lessonquiz: {
      id: 'sp.lessonquiz',
      lines: ['Here’s the quiz. It covers the whole lesson, and afterwards you can retry any you missed.'],
      face: 'happy',
      clip: 'side-point',
    },
    quicktest: {
      id: 'sp.quicktest',
      lines: ['That was a Quick test. Your marks are here, and you can retry the ones you missed.'],
      face: 'proud',
      clip: 'nod',
    },
    aiexplain: {
      id: 'sp.aiexplain',
      lines: ['Not sure why an answer was right? AI explain goes through that question with you.'],
      face: 'curious',
      clip: 'side-point',
    },
    setwork: {
      id: 'sp.setwork',
      lines: ['This is work set by your teacher. Each question can be answered once, so take your time.'],
      face: 'soft-smile',
      clip: 'side-point',
    },
    challenge: {
      id: 'sp.challenge',
      lines: ['A challenge is the same questions for you and a friend. It’s optional, and there is no chat.'],
      face: 'wink',
      clip: 'nod',
    },
    revision: {
      id: 'sp.revision',
      lines: ['This is your revision plan: weak topics spread over the days before your exam.'],
      face: 'proud',
      clip: 'side-point',
    },
    saved: {
      id: 'sp.saved',
      lines: ['Saved questions wait here. Open one to try it again, or remove it when you’re done.'],
      face: 'soft-smile',
      clip: 'nod',
    },
  };
  // END COPY

  var PAGE_OF = { index: 'practice', topics_index: 'learn', qotd_page: 'daily', friend_leaderboard_page: 'compete', profile: 'profile', student_classes: 'classes', profile_settings: 'settings' };
  var URL_OF = { practice: '/', learn: '/topics', daily: '/qotd', compete: '/leaderboard/friends', profile: '/profile', classes: '/classes', settings: '/profile/settings' };
  // where each spotlight points (the first selector that is on show wins); lessonquiz, quicktest, aiexplain, setwork, challenge,
  // revision and saved are found on their pages, hint and bigger when the pupil asks for them
  var SPOT_TARGET = {
    hint: '.free-response-hint .hint-card, .mcq-hint-slot .hint-card, .hint-card',
    bigger: '.free-response-hint .hint-card, .mcq-hint-slot .hint-card, .hint-card',
    // the quiz bar lesson-progress.js adds at the end of the lesson (it removes the inline button at the top); shown when it scrolls into view
    lessonquiz: '.lesson-quiz-cta-btn, .lesson-quiz-cta-bar a.btn',
    quicktest: '.lesson-hero + .section-panel, .section-panel',
    aiexplain: '.quiz-assist-btn',
    setwork: 'row:My class work',
    challenge: '.challenge-vs-card, #compete-challenges',
    revision: '#revision-plan ul.profile-list li',
    saved: 'saved:',
  };
  var HOP_KEY = 'pb-tour-hop';
  var S = null;           // the app tour on this page
  var P = null;           // a spotlight on this page
  var spotDone = false;   // one spotlight per page view

  function Z() { return W.pbZorp || null; }
  function G() { return (W.pbGuide && W.pbGuide.tour) || null; }
  function q(sel, root) { try { return (root || D).querySelector(sel); } catch (e) { return null; } }
  function level() {
    var z = Z();
    if (z && z.motionLevel) return z.motionLevel();
    return W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduced' : 'full';
  }
  function shown(n) { return !!n && !n.hidden && !(n.closest && n.closest('[hidden]')) && !!(n.offsetWidth || n.offsetHeight || n.getClientRects().length); }
  function inClass() {
    try { return !!JSON.parse((D.getElementById('pb-tour-assets') || {}).textContent || '{}').inClass; } catch (e) { return false; }
  }
  function pageNow() { return PAGE_OF[D.body.getAttribute('data-guide-endpoint') || ''] || ''; }
  function el(tag, cls, parent) {
    var n = D.createElement(tag);
    if (cls) n.className = cls;
    if (parent) parent.appendChild(n);
    return n;
  }

  // something else is on screen (a dialog, a stage, a badge or moment waiting to play): the tour and the spotlights wait
  function blocked() {
    var g = D.getElementById('guide-root');
    var t = G();
    return !!((g && !g.hidden) || (W.pbStage && W.pbStage.isOpen && W.pbStage.isOpen()) || (t && t.busy()) || q('.pb-mtoast')); 
  }

  // ---- finding things on the page ----
  function panelByHeader(text) {
    var heads = D.querySelectorAll('.section-panel-header');
    for (var i = 0; i < heads.length; i += 1) {
      if ((heads[i].textContent || '').trim().indexOf(text) === 0 && shown(heads[i].parentNode)) return heads[i].parentNode;
    }
    return null;
  }
  function find(spec) {
    var parts = String(spec || '').split(',');
    var tall = null;
    for (var i = 0; i < parts.length; i += 1) {
      var sel = parts[i].trim();
      var n = null;
      if (!sel) continue;
      if (sel.indexOf('panel:') === 0) n = panelByHeader(sel.slice(6));
      else if (sel.indexOf('row:') === 0) { var p = panelByHeader(sel.slice(4)); n = p && q('ul.profile-list li', p); }
      else if (sel === 'saved:') n = savedRow();
      else n = q(sel);
      if (!n || !shown(n)) continue;
      // a target taller than the free band would sit under the card: a later, smaller choice in the list wins
      if (n.getBoundingClientRect().height > W.innerHeight * 0.45) { tall = tall || n; continue; }
      return n;
    }
    return tall;
  }
  function savedRow() {
    var links = D.querySelectorAll('#profile-tab-history li a[href*="/saved"]');
    for (var i = 0; i < links.length; i += 1) if (shown(links[i])) return links[i].closest('li');
    return null;
  }
  // the bar a page keeps along the bottom (tab bar, sticky New question): cards sit above it
  function bounds() {
    var top = 0;
    var bot = W.innerHeight;
    // the sticky headers stacked at the top (the site header, and a page's own such as the profile hero once it has stuck)
    Array.prototype.forEach.call(D.querySelectorAll('header'), function (h) {
      var pos = W.getComputedStyle(h).position;
      var r = h.getBoundingClientRect();
      if ((pos === 'sticky' || pos === 'fixed') && r.top <= top + 100 && r.bottom > top) top = r.bottom;
    });
    ['practice-new-question-bar', 'app-tab-bar'].forEach(function (id) {
      var n = D.getElementById(id);
      if (shown(n) && W.getComputedStyle(n).position === 'fixed') bot = Math.min(bot, n.getBoundingClientRect().top);
    });
    return { top: top, bot: bot };
  }

  // ---- the card (shared by the tour and the spotlights) ----
  function mascot(box) {
    var src = q('[data-guide-face] svg.buddy-mascot') || q('svg.buddy-mascot');
    var face = el('span', 'study-buddy-face pb-tour-zorp', box);
    face.setAttribute('data-buddy-face', '');
    face.setAttribute('aria-hidden', 'true');
    if (!src) { face.hidden = true; return null; }
    var svg = src.cloneNode(true);
    svg.classList.remove('is-zorp-idle');
    face.appendChild(svg);
    var z = Z();
    if (z) {
      z.bind(face);
      z.turn('front', 'r', { el: svg, instant: true });
    }
    return svg;
  }

  function buildCard(kind) {
    var box = el('div', 'pb-tour pb-tour--' + kind);
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', kind === 'tour' ? 'Tour of the site' : 'A tip from Zorp');
    box.hidden = true;
    var c = { box: box, svg: mascot(box) };
    var body = el('div', 'pb-tour-body', box);
    c.kicker = el('p', 'pb-tour-kicker', body);
    c.line = el('p', 'pb-tour-line', body);
    var acts = el('div', 'pb-tour-actions', body);
    c.next = el('button', 'btn btn-primary btn-sm pb-tour-next', acts);
    c.next.type = 'button';
    c.skip = el('button', 'btn-link pb-tour-skip', acts);
    c.skip.type = 'button';
    c.live = el('div', 'pb-tour-live');
    c.live.setAttribute('aria-live', 'polite');
    D.body.appendChild(c.live);
    D.body.appendChild(box);
    return c;
  }

  function enter(box) {
    var lv = level();
    if (lv === 'off' || !box.animate) return;
    try {
      box.animate(lv === 'full' ? [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }] : [{ opacity: 0 }, { opacity: 1 }],
        { duration: lv === 'full' ? 240 : 160, easing: 'ease-out' });
    } catch (e) { /* no animation */ }
  }

  function overlap(a, b) { return !(a.bottom <= b.top + 1 || a.top >= b.bottom - 1 || a.right <= b.left + 1 || a.left >= b.right - 1); }

  // Put the card where it does not cover the target: scroll the target into the free band first, then try the corners in turn.
  function place(c, target) {
    var box = c.box;
    var vw = W.innerWidth;
    var narrow = vw <= 640;
    var edge = bounds();
    box.style.visibility = 'hidden';
    box.hidden = false;
    var w = narrow ? vw - 32 : Math.min(380, vw - 48);
    box.style.width = w + 'px';
    var h = box.offsetHeight;
    var spots = narrow
      ? [{ x: 16, y: edge.bot - h - 10 }, { x: 16, y: edge.top + 8 }]
      : [{ x: vw - w - 24, y: edge.bot - h - 16 }, { x: 24, y: edge.bot - h - 16 }, { x: vw - w - 24, y: edge.top + 12 }, { x: 24, y: edge.top + 12 }];
    if (target) {
      var r = target.getBoundingClientRect();
      var limit = spots[0].y - 12;
      var free = limit - (edge.top + 8);
      var want = r.height >= free ? edge.top + 8 : edge.top + 8 + (free - r.height) / 2;
      // instant: the page may smooth-scroll, and the card must be placed against where the target really is
      if (r.top < edge.top + 8 || r.bottom > limit) { try { W.scrollBy({ top: r.top - want, left: 0, behavior: 'instant' }); } catch (e) { W.scrollBy(0, r.top - want); } }
    }
    var tr = target ? target.getBoundingClientRect() : null;
    var pick = spots[0];
    for (var i = 0; i < spots.length; i += 1) {
      var rect = { left: spots[i].x, top: spots[i].y, right: spots[i].x + w, bottom: spots[i].y + h };
      if (!tr || !overlap(rect, tr)) { pick = spots[i]; break; }
    }
    box.style.left = Math.max(8, pick.x) + 'px';
    box.style.top = Math.max(edge.top + 4, pick.y) + 'px';
    box.style.visibility = '';
  }

  function say(c, text) {
    c.line.textContent = text;
    c.live.textContent = '';
    W.setTimeout(function () { if (c.live) c.live.textContent = text; }, 60);
  }

  function mood(c, face, clip) {
    var z = Z();
    if (!z || !c.svg) return;
    if (z.valenceOf && face && z.valenceOf(face) !== 'negative') z.setExpression(face, { el: c.svg });
    if (clip && level() === 'full') z.play(clip, { el: c.svg });
  }

  function mark(target, on) {
    if (target && target.classList) target.classList[on ? 'add' : 'remove']('pb-tour-target');
  }

  // ---- the app tour ----
  function pageOf(i) { return STEPS[i] ? STEPS[i].page : ''; }
  function skipped(step) { return !!step.classOnly && !inClass(); }

  function openFor(step) {
    if (!step.open) return;
    var tab = q(step.open);
    if (tab && tab.getAttribute('aria-selected') !== 'true') tab.click();
  }
  function targetFor(step) {
    if (skipped(step)) return null;
    openFor(step);
    return find(step.target);
  }
  // the first step from i on that page that has something to point at; -1 when the page has no more
  function resolve(i) {
    var page = pageOf(i);
    for (var k = i; k < STEPS.length && STEPS[k].page === page; k += 1) {
      var t = targetFor(STEPS[k]);
      if (t) return { i: k, target: t };
    }
    return null;
  }
  // the first step of the page after the one step i is on (steps for a class are passed over when the pupil is in none)
  function afterPage(i) {
    var page = pageOf(i);
    var k = i;
    while (k < STEPS.length && STEPS[k].page === page) k += 1;
    while (k < STEPS.length && skipped(STEPS[k])) k += 1;
    return k;
  }
  // true when nothing follows step i: no later step on this page has a target, and no page comes after it
  function lastStep(i) {
    for (var k = i + 1; k < STEPS.length && STEPS[k].page === STEPS[i].page; k += 1) if (!skipped(STEPS[k]) && find(STEPS[k].target)) return false;
    return afterPage(i) >= STEPS.length;
  }

  function save(i) {
    var t = G();
    if (t) t.setRun({ id: 'app', step: i });
  }

  function showStep(found) {
    var step = STEPS[found.i];
    var c = S.card;
    S.i = found.i;
    S.fixes = 0;
    S.target = found.target;
    save(S.i);
    mark(S.marked, false);
    S.marked = found.target;
    mark(found.target, true);
    var last = lastStep(S.i);
    if (last && !S.told) S.told = tellEnd();
    c.kicker.textContent = step.heading;
    c.next.textContent = last ? UI.finish : UI.primary;
    c.skip.textContent = UI.skipLabel;
    c.next.setAttribute('data-last', last ? '1' : '0');
    say(c, step.lines[0]);   // the text first: place() measures the card
    place(c, found.target);
    mood(c, step.face, step.clip);
    enter(c.box);
    S.shownAt = Date.now();
    if (!S.focused) { S.focused = true; try { c.next.focus({ preventScroll: true }); } catch (e) { /* old browser */ } }
  }

  function show(i) {
    var found = resolve(i);
    if (found) { showStep(found); return; }
    // nothing left to point at on this page: carry on to the next one
    var k = afterPage(i);
    if (k >= STEPS.length) { finish('done'); return; }
    leave(k, true);
  }

  function next() {
    if (!S) return;
    var i = S.i + 1;
    if (i >= STEPS.length) { finish('done'); return; }
    var found = STEPS[i].page === STEPS[S.i].page ? resolve(i) : null;
    if (found) { showStep(found); return; }
    var j = afterPage(S.i);
    if (j >= STEPS.length) { finish('done'); return; }
    leave(j, false);
  }

  // ---- Zorp hops along the bar to the next tab, then the next page takes over ----
  function navEl(page) {
    var href = URL_OF[page];
    if (page === 'classes' || page === 'settings') return D.getElementById('nav-menu-open');
    var list = D.querySelectorAll('#app-tab-bar a[href="' + href + '"], .header-primary-nav a[href="' + href + '"]');
    for (var i = 0; i < list.length; i += 1) if (shown(list[i])) return list[i];
    return null;
  }
  function hopper(from) {
    var h = el('div', 'pb-tour-hopper');
    h.setAttribute('aria-hidden', 'true');
    var face = el('span', 'study-buddy-face', h);
    face.setAttribute('data-buddy-face', '');
    var src = q('[data-guide-face] svg.buddy-mascot') || q('svg.buddy-mascot');
    var svg = null;
    if (src) {
      svg = src.cloneNode(true);
      svg.classList.remove('is-zorp-idle');
      face.appendChild(svg);
      var z = Z();
      if (z) z.bind(face);
    }
    D.body.appendChild(h);
    return { h: h, svg: svg, from: from };
  }
  // the spot above a tab on the bottom bar, below a link in the header
  function spotAt(n) {
    var r = n.getBoundingClientRect();
    var top = !!(n.closest && n.closest('header'));
    return { x: r.left + r.width / 2 - 22, y: top ? r.bottom + 2 : r.top - 46 };
  }
  function rest(p, pos) { p.h.style.transform = 'translate(' + pos.x + 'px,' + pos.y + 'px)'; }

  function hop(fromPage, toPage) {
    var lv = level();
    var to = navEl(toPage);
    if (lv === 'off' || !to) return Promise.resolve();
    var fromEl = navEl(fromPage);
    var a = fromEl ? spotAt(fromEl) : (S && S.card ? (function () { var r = S.card.box.getBoundingClientRect(); return { x: r.left + 8, y: r.top }; })() : spotAt(to));
    var b = spotAt(to);
    var p = hopper();
    var z = Z();
    S.card.box.hidden = true;
    mark(S.marked, false);
    if (lv !== 'full' || !p.h.animate) {
      rest(p, b);
      try { p.h.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 200, fill: 'both' }); } catch (e) { /* none */ }
      return new Promise(function (done) { W.setTimeout(done, 260); });
    }
    rest(p, a);
    var dir = b.x >= a.x ? 'r' : 'l';
    if (z && p.svg) z.turn('side', dir, { el: p.svg });
    var arc = Math.min(a.y, b.y) - 24;
    var ms = Math.round(Math.min(900, 520 + Math.abs(b.x - a.x) * 0.6));
    return new Promise(function (done) {
      W.setTimeout(function () {
        if (z && p.svg) z.play('hop', { el: p.svg });
        var anim = null;
        try {
          anim = p.h.animate([
            { transform: 'translate(' + a.x + 'px,' + a.y + 'px)' },
            { transform: 'translate(' + ((a.x + b.x) / 2) + 'px,' + arc + 'px)', offset: 0.5 },
            { transform: 'translate(' + b.x + 'px,' + b.y + 'px)' },
          ], { duration: ms, easing: 'ease-in-out', fill: 'forwards' });
        } catch (e) { /* none */ }
        if (anim) anim.onfinish = function () { rest(p, b); W.setTimeout(done, 80); };
        else { rest(p, b); done(); }
      }, 320);
    });
  }

  // on the new page: Zorp is already standing on the tab it hopped to, then the card takes over
  function arrive() {
    var page = pageNow();
    var flag = '';
    try { flag = W.sessionStorage.getItem(HOP_KEY) || ''; W.sessionStorage.removeItem(HOP_KEY); } catch (e) { flag = ''; }
    var to = flag === page ? navEl(page) : null;
    if (!to || level() === 'off') return;
    var p = hopper();
    rest(p, spotAt(to));
    var z = Z();
    if (z && p.svg) z.turn('side', 'r', { el: p.svg, instant: true });
    var lv = level();
    if (lv === 'full' && z && p.svg) { z.turn('front', 'r', { el: p.svg }); z.play('wave', { el: p.svg }); }
    var gone = function () { if (p.h.parentNode) p.h.parentNode.removeChild(p.h); };
    if (p.h.animate) {
      try { var a = p.h.animate([{ opacity: 1 }, { opacity: 1, offset: 0.6 }, { opacity: 0 }], { duration: lv === 'full' ? 1100 : 500, fill: 'forwards' }); a.onfinish = gone; return; } catch (e) { /* fall through */ }
    }
    W.setTimeout(gone, 600);
  }

  // go to the page of step k: remember the step, hop, wait for the save, navigate
  function leave(k, quiet) {
    var t = G();
    var fromPage = pageOf(S.i);
    var toPage = pageOf(k);
    if (t) t.setRun({ id: 'app', step: k });
    S.leaving = true;
    var go = function () {
      try { W.sessionStorage.setItem(HOP_KEY, toPage); } catch (e) { /* no storage */ }
      W.location.assign(URL_OF[toPage]);
    };
    var saved = t && t.commit ? t.commit() : Promise.resolve();
    var timer = new Promise(function (done) { W.setTimeout(done, 1800); });
    var hopped = quiet ? Promise.resolve() : hop(fromPage, toPage);
    Promise.all([Promise.race([saved, timer]), hopped]).then(go, go);
  }

  function teardown() {
    if (!S) return;
    W.clearInterval(S.timer);
    D.removeEventListener('keydown', onKey);
    W.removeEventListener('resize', onResize);
    mark(S.marked, false);
    [S.card.box, S.card.live].forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
    S = null;
  }

  // E10 review fix 8: the last step is on screen; save the state, then tell the server (the badge needs this to be recorded)
  function tellEnd() {
    var t = G();
    var headers = { Accept: 'application/json', 'Content-Type': 'application/json' };
    var token = t && t.csrf ? t.csrf() : '';
    if (token) headers['X-CSRF-Token'] = token;
    var send = function () { return W.fetch('/api/v1/me/tour/reached-end', { method: 'POST', headers: headers, body: '{}', credentials: 'same-origin' }).catch(function () {}); };
    return (t && t.commit ? t.commit() : Promise.resolve()).then(send, send);
  }

  function finish(how) {
    if (!S) return;
    var told = S.told;
    teardown();
    var t = G();
    var go = function () { if (t) t.end(); if (how === 'done') celebrate(); };   // end() clears the run: after the server has the end
    if (how === 'done' && told) told.then(go, go); else go();
  }

  // Zorp bows on the stage, then the server awards the badge; the badge arrives through the ordinary delivery (celebrate.js)
  function celebrate() {
    var post = function () {
      var t = G();
      var headers = { Accept: 'application/json', 'Content-Type': 'application/json' };
      var token = t && t.csrf ? t.csrf() : '';
      if (token) headers['X-CSRF-Token'] = token;
      try { W.fetch('/api/v1/me/tour/complete', { method: 'POST', headers: headers, body: '{}', credentials: 'same-origin' }).catch(function () { /* the tour is done either way */ }); } catch (e) { /* no fetch */ }
    };
    if (!W.pbGuide || !W.pbGuide.stage) { post(); return; }
    W.pbGuide.stage(END).then(post, post);
  }

  function onKey(e) {
    if (e.key !== 'Escape' || !S || blocked()) return;
    e.preventDefault();
    finish('skip');
  }
  function onResize() {
    if (!S || S.leaving || S.card.box.hidden || !S.target) return;
    W.clearTimeout(S.rz);
    S.rz = W.setTimeout(function () { if (S && S.target) place(S.card, S.target); }, 120);
  }

  // while something else is on screen the card steps aside; when it has gone the card comes back where it was
  function watch() {
    if (!S || S.leaving) return;
    var b = blocked();
    if (b && !S.paused) { S.paused = true; S.card.box.hidden = true; }
    else if (!b && S.paused) {
      S.paused = false;
      var found = resolve(S.i);
      if (found) { S.focused = false; showStep(found); } else show(S.i);
    } else if (!b && S.target && !S.card.box.hidden && (S.fixes || 0) < 8) {
      // the page can settle after the card was placed (tabs, images, the profile header): put the card clear of the target again
      var cr = S.card.box.getBoundingClientRect();
      var tr = S.target.getBoundingClientRect();
      if (overlap(cr, tr)) { S.fixes = (S.fixes || 0) + 1; place(S.card, S.target); }
    }
  }

  // true when this page has something to show (the tour is running here); false leaves the page as it was
  function start() {
    if (S) return true;
    var t = G();
    var run = t && t.run();
    var page = pageNow();
    if (!run || run.id !== 'app' || !page) return false;
    var i = run.step;
    if (i >= STEPS.length) { t.end(); return false; }
    if (pageOf(i) !== page) {
      // the pupil went to a different page by hand: carry on from the first stop of this one
      for (i = 0; i < STEPS.length && STEPS[i].page !== page; i += 1) { /* find it */ }
      if (i >= STEPS.length) return false;
    }
    S = { i: i, card: buildCard('tour'), target: null, marked: null, paused: false, leaving: false, focused: false };
    S.card.next.addEventListener('click', function () {
      if (S && S.card.next.getAttribute('data-last') === '1') finish('done'); else next();
    });
    S.card.skip.addEventListener('click', function () { finish('skip'); });
    D.addEventListener('keydown', onKey);
    W.addEventListener('resize', onResize);
    arrive();
    S.timer = W.setInterval(watch, 400);
    if (blocked()) { S.paused = true; return true; }
    show(i);
    return true;
  }

  // ---- spotlights ----
  function endSpot() {
    if (!P) return;
    mark(P.target, false);
    D.removeEventListener('keydown', onSpotKey);
    W.removeEventListener('resize', onSpotResize);
    W.clearTimeout(P.timer);
    [P.card && P.card.box, P.card && P.card.live].forEach(function (n) { if (n && n.parentNode) n.parentNode.removeChild(n); });
    P = null;
  }
  function onSpotKey(e) { if (e.key === 'Escape' && P && P.card && !blocked()) { e.preventDefault(); endSpot(); } }
  function onSpotResize() { if (P && P.card && P.target) place(P.card, P.target); }

  function openSpot(id, target) {
    var t = G();
    var spec = SPOTS[id];
    if (!spec || spotDone || S) return false;
    spotDone = true;
    if (t) t.markSeen('sp_' + id);
    var c = buildCard('spot');
    c.kicker.textContent = '';
    c.kicker.hidden = true;
    c.next.textContent = UI.gotIt;
    c.skip.hidden = true;
    P.card = c;
    P.target = target;
    mark(target, true);
    c.next.addEventListener('click', endSpot);
    D.addEventListener('keydown', onSpotKey);
    W.addEventListener('resize', onSpotResize);
    say(c, spec.lines[0]);
    place(c, target);
    mood(c, spec.face, spec.clip);
    enter(c.box);
    // never leave the card pointing at nothing: it goes if its target is removed or hidden. E11 Phase 0: it also steps aside while
    // something else is on screen (a stage, a dialog, a moment) and comes back, re-placed, when that has gone
    P.timer = W.setInterval(function () {
      if (!P || !P.card) return;
      if (P.target && !(P.target.isConnected && shown(P.target))) { endSpot(); return; }
      var away = blocked();
      if (away === !!P.away) return;
      P.away = away;
      P.card.box.hidden = away;
      mark(P.target, !away);
      if (!away) place(P.card, P.target);
    }, 300);
    return true;
  }

  // wait until nothing else is on screen (and the target is in view for the page-based ones), for a little while
  function watchSpot(id, tries, needsView) {
    if (!P || P.id !== id || spotDone) return;
    var t = G();
    var target = find(SPOT_TARGET[id]);
    var ready = target && !blocked() && !(t && t.seen('sp_' + id));
    if (ready && needsView) {
      var r = target.getBoundingClientRect();
      ready = r.bottom > 0 && r.top < W.innerHeight * 0.85;
    }
    if (ready) { openSpot(id, target); return; }
    if (tries <= 0) { P = null; return; }
    P.timer = W.setTimeout(function () { watchSpot(id, tries - 1, needsView); }, 700);
  }

  // ids: the spotlights this moment could show. The first one that is due and whose target is on show wins.
  function spot(ids) {
    var t = G();
    if (S || P || spotDone || !t) return;
    for (var i = 0; i < ids.length; i += 1) {
      var id = ids[i];
      if (!SPOTS[id] || t.seen('sp_' + id)) continue;
      var byEvent = id === 'hint' || id === 'bigger';
      var late = id === 'lessonquiz';   // added after load and far down the page: wait for the pupil to reach it
      if (!byEvent && !late && !find(SPOT_TARGET[id])) continue;
      P = { id: id, card: null, target: null, timer: 0 };
      watchSpot(id, byEvent ? 6 : late ? 1e6 : 80, !byEvent);
      return;
    }
  }

  W.pbTour = {
    start: start,
    spot: spot,
    active: function () { return !!S; },
    steps: STEPS,
    spots: SPOTS,
    end: END,
    stop: function () { if (S) finish('skip'); endSpot(); },
  };
})();
