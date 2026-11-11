/* Badge stage (E10 phase 4, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md B2, B2.1). Loaded on demand by guide.js (pbGuide) with
   badge-stage.css, only when a badge is about to be celebrated; it plays on the phase 1 stage (zorp-stage.js, pbStage.play).
   Each badge is one scene: the medal drops in and stamps, the family's props come in, Zorp plays the family's choreography,
   the panel shows the title, what you did and what is next. Several badges play one after another ("1 of 3"), never two at
   once. Buttons: Continue, and See my milestones (the profile, Progress tab). Esc closes. Motion: full plays everything;
   reduced shows the final frame with the stage's fade; off shows it with no fade. Transform and opacity only, DOM nodes only
   (props cloned from static/images/badge-props.svg). The copy (UI) and the choreography (FAMILIES) are data: the voice lint and
   scripts/test_badge_stage_smoke.py read them. Beats are the stage's (prop, play, turn, face, burst, wait, talk). */
(function () {
  'use strict';
  if (window.pbBadgeStage) return;
  var D = document;
  var EASE = 'cubic-bezier(.2,.7,.3,1)';
  var SVGNS = 'http://www.w3.org/2000/svg';
  // BEGIN COPY
  var UI = {
    kicker: 'New badge',
    of: ' of ',
    next: 'Next: ',
    primary: 'Continue',
    profile: 'See my milestones',
    wardrobe: 'New in your wardrobe: {item}.',
    tryOn: 'Try it on',
    earned: 'You earned this.',
    streakTitle: '{n}-day streak',
    streakBlurb: 'You studied on {n} days in a row.',
    streakNext: { 7: 'Study on 30 days in a row.', 30: 'Study on 100 days in a row.' },
    big: 'I’m a little teary, in the happiest way. Well done.'
  };
  // END COPY
  // BEGIN FAMILIES
  var FAMILIES = {
    streak: { face: 'determined', end: 'proud', prop: 'bp-flame', fx: 'flame', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'fist-pump' }, { play: 'flex' }] },
    streak100: { face: 'wow', end: 'proud', prop: 'bp-flame', fx: 'flame', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'victory' }, { play: 'dance' }, { face: 'aww' }] },
    daily: { face: 'happy', end: 'happy', prop: 'bp-sun', fx: 'sunrise', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'wave' }, { play: 'hop' }] },
    practice: { face: 'happy', end: 'laugh', prop: 'bp-cards', fx: 'fan', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'dance' }] },
    explorer: { face: 'curious', end: 'happy', prop: 'bp-map', fx: 'pins', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'float' }] },
    learning: { face: 'soft-smile', end: 'proud', prop: 'bp-book', fx: 'book', hat: 1, beats: [{ burst: 1 }, { wait: 2300 }, { play: 'bow' }] },
    topic_completed: { face: 'happy', end: 'joy', prop: '', fx: '', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'cheer' }] },
    topic_ninja: { face: 'determined', end: 'grin', prop: 'bp-swish', fx: 'swish', beats: [{ burst: 1 }, { wait: 1300 }, { turn: 'back' }, { turn: 'front' }, { play: 'victory' }] },
    topic_master: { face: 'wow', end: 'proud', prop: 'bp-stars', fx: 'stars', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'victory' }, { play: 'float' }, { face: 'proud' }] },
    subject: { face: 'joy', end: 'proud', prop: 'bp-page', fx: 'page', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'dance' }, { play: 'fist-pump' }] },
    accuracy: { face: 'soft-smile', end: 'grin', prop: 'bp-target', fx: 'target', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'nod' }, { face: 'grin' }] },
    tour: { face: 'happy', end: 'proud', prop: 'bp-sign', fx: 'sign', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'bow' }, { play: 'wave' }] },
    perfect: { face: 'joy', end: 'grin', prop: 'bp-target', fx: 'target', beats: [{ burst: 1 }, { wait: 1300 }, { play: 'victory' }, { play: 'dance' }, { face: 'grin' }] },
    growth: { face: 'happy', end: 'proud', prop: '', fx: 'sprout', beats: [{ burst: 1 }, { wait: 1900 }, { play: 'nod' }, { play: 'cheer' }] }
  };
  // END FAMILIES
  var STAMP = 1250;   // ms into the scene when the medal lands (the soft thud, the sparkle ring, the cue)
  var RT = null;
  var props = null;
  var propsP = null;
  var cur = null;     // what the open scene added: { layer, anims, timers, hat }
  var wantProfile = false;
  var tryId = '';

  function Z() { return window.pbZorp || null; }
  function level() {
    var z = Z();
    if (z && z.motionLevel) return z.motionLevel();
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduced' : 'full';
  }
  function full() { return level() === 'full'; }
  function el(tag, cls, parent) {
    var n = D.createElement(tag);
    if (cls) n.className = cls;
    if (parent) parent.appendChild(n);
    return n;
  }
  function assets() {
    try { return JSON.parse((D.getElementById('pb-badge-assets') || {}).textContent || '{}') || {}; } catch (e) { return {}; }
  }
  function ready() {
    if (!propsP) {
      var url = assets().props;
      propsP = (url && window.fetch && window.DOMParser ? fetch(url, { credentials: 'same-origin' }).then(function (r) {
        return r.ok ? r.text() : '';
      }).then(function (text) {
        var doc = text ? new window.DOMParser().parseFromString(text, 'image/svg+xml') : null;
        if (doc && !doc.getElementsByTagName('parsererror').length) props = doc;
      }) : Promise.resolve()).catch(function () { /* the medal and the text still show */ });
    }
    var z = Z();
    if (z && z.register && !RT) z.register(function (rt) { RT = rt; });
    return propsP;
  }
  function part(id) {
    var src = id && props && props.querySelector('[id="' + id + '"]');
    if (!src) return null;
    var n = D.importNode(src, true);
    n.removeAttribute('id');
    n.setAttribute('aria-hidden', 'true');
    n.setAttribute('focusable', 'false');
    return n;
  }
  function all(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }

  function anim(node, frames, ms, o) {
    if (!node || !node.animate || !cur) return null;
    o = o || {};
    o.duration = ms;
    o.easing = o.easing || EASE;
    o.fill = o.fill || 'both';
    try { var a = node.animate(frames, o); cur.anims.push(a); return a; } catch (e) { return null; }
  }
  function later(fn, ms) {
    if (!cur) return;
    var mine = cur;
    mine.timers.push(setTimeout(function () { if (cur === mine) fn(); }, ms));
  }

  // ---- what each family adds beside the medal (full motion; the still frame is in `still`) ----
  var FX = {
    flame: function (b) {
      anim(b.querySelector('.bp-flick'), [{ transform: 'scale(1,1)' }, { transform: 'scale(1.05,.95)' }, { transform: 'scale(.97,1.05)' }, { transform: 'scale(1,1)' }], 1100, { delay: 700, iterations: 4, easing: 'ease-in-out' });
      all(b, '.bp-dot').forEach(function (d, i) { anim(d, [{ opacity: 0.2, transform: 'scale(.6)' }, { opacity: 1, transform: 'scale(1.35)', offset: 0.6 }, { opacity: 1, transform: 'scale(1)' }], 400, { delay: 1500 + i * 150 }); });
    },
    sunrise: function (b) {
      anim(b.querySelector('.bp-rise'), [{ transform: 'translateY(60px)', opacity: 0 }, { transform: 'none', opacity: 1 }], 1100, { delay: 300 });
      anim(b.querySelector('.bp-strip'), [{ transform: 'translateY(20px)', opacity: 0 }, { transform: 'none', opacity: 1 }], 600, { delay: 900 });
    },
    fan: function (b) {
      all(b, '.bp-card').forEach(function (c, i) { anim(c, [{ transform: 'rotate(0deg)', opacity: 0 }, { opacity: 1, offset: 0.2 }, { transform: 'rotate(' + c.getAttribute('data-a') + 'deg)', opacity: 1 }], 750, { delay: 400 + i * 110 }); });
    },
    pins: function (b) {
      all(b, '.bp-pin').forEach(function (p, i) { anim(p, [{ transform: 'translateY(-34px)', opacity: 0 }, { transform: 'translateY(2px)', opacity: 1, offset: 0.7 }, { transform: 'none', opacity: 1 }], 520, { delay: 900 + i * 260 }); });
      anim(b.querySelector('.bp-trail'), [{ opacity: 0 }, { opacity: 1 }], 700, { delay: 600 });
    },
    book: function (b) { anim(b.querySelector('svg') || b, [{ transform: 'translateY(24px) scale(.92)', opacity: 0 }, { transform: 'none', opacity: 1 }], 700, { delay: 300 }); },
    swish: function (b) {
      all(b, '.bp-sw').forEach(function (s, i) { anim(s, [{ transform: 'translateX(' + (i === 1 ? 40 : -40) + 'px)', opacity: 0 }, { transform: 'none', opacity: 1 }], 520, { delay: 1100 + i * 130 }); });
    },
    stars: function (b) {
      all(b, '.bp-star').forEach(function (s, i) {
        anim(s, [{ transform: 'scale(0) rotate(-40deg)', opacity: 0 }, { transform: 'scale(1.3) rotate(8deg)', opacity: 1, offset: 0.6 }, { transform: 'none', opacity: 1 }], 600, { delay: 900 + i * 170 });
        anim(s, [{ opacity: 1 }, { opacity: 0.45 }, { opacity: 1 }], 1400, { delay: 2200 + i * 230, iterations: 3, fill: 'none', easing: 'ease-in-out' });
      });
    },
    page: function (b) {
      anim(b.querySelector('.bp-mini'), [{ transform: 'scale(.3)', opacity: 0 }, { transform: 'none', opacity: 1 }], 700, { delay: 700 });
      anim(b.firstChild, [{ transform: 'scale(.9)', opacity: 0 }, { transform: 'none', opacity: 1 }], 500, { delay: 200 });
      rain(b);
    },
    sign: function (b) {
      all(b, '.bp-board').forEach(function (s, i) { anim(s, [{ transform: 'rotate(-22deg)', opacity: 0 }, { transform: 'rotate(5deg)', opacity: 1, offset: 0.7 }, { transform: 'none', opacity: 1 }], 520, { delay: 900 + i * 220 }); });
    },
    target: function (b) { anim(b.querySelector('.bp-rings'), [{ transform: 'scale(.4)', opacity: 0 }, { transform: 'scale(1.06)', opacity: 1, offset: 0.7 }, { transform: 'none', opacity: 1 }], 800, { delay: 400 }); },
    // E11 Phase 2 (the Recovery line): two sprouts push up beside the medal, the stems first, then the leaves unfold
    sprout: function (b) {
      all(b, '.bp-stem').forEach(function (s, i) { anim(s, [{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }], 700, { delay: 500 + i * 160 }); });
      all(b, '.bp-leaf').forEach(function (s, i) { anim(s, [{ transform: 'scale(0)', opacity: 0 }, { transform: 'scale(1.12)', opacity: 1, offset: 0.7 }, { transform: 'none', opacity: 1 }], 600, { delay: 1050 + i * 150 }); });
    }
  };
  // a prop drawn here instead of cloned from badge-props.svg (the growth family's sprouts); same 240 by 180 frame
  var DRAW = {
    sprout: function () {
      var s = D.createElementNS(SVGNS, 'svg');
      s.setAttribute('viewBox', '0 0 240 180');
      s.setAttribute('aria-hidden', 'true');
      s.setAttribute('focusable', 'false');
      var add = function (parent, tag, attrs) {
        var n = D.createElementNS(SVGNS, tag);
        Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
        if (tag === 'path' && attrs['class']) { n.style.transformBox = 'fill-box'; n.style.transformOrigin = attrs['class'] === 'bp-stem' ? '50% 100%' : '50% 90%'; }
        parent.appendChild(n);
        return n;
      };
      [[50, 1], [190, -1]].forEach(function (p) {
        var g = add(s, 'g', { transform: 'translate(' + p[0] + ' 170) scale(' + p[1] + ' 1)' });
        add(g, 'ellipse', { cx: 0, cy: 4, rx: 28, ry: 7, fill: '#a16207', opacity: '0.45' });
        add(g, 'path', { 'class': 'bp-stem', d: 'M0 3C0-14-3-30 1-48', fill: 'none', stroke: '#15803d', 'stroke-width': 5, 'stroke-linecap': 'round' });
        add(g, 'path', { 'class': 'bp-leaf', d: 'M0-26C-10-46-34-44-38-34C-28-22-12-20 0-26Z', fill: '#22c55e', stroke: '#15803d', 'stroke-width': 1.5 });
        add(g, 'path', { 'class': 'bp-leaf', d: 'M1-42C10-62 34-60 38-50C28-38 12-36 1-42Z', fill: '#86efac', stroke: '#15803d', 'stroke-width': 1.5 });
      });
      return s;
    }
  };

  function rain(box) {
    var layer = cur.layer;
    var h = layer.getBoundingClientRect().height || 500;
    var colours = ['#fde047', '#f472b6', '#60a5fa', '#34d399', '#fb923c'];
    for (var i = 0; i < 22; i += 1) {
      var bit = el('div', 'bd-conf', layer);
      var s = part('bp-conf');
      if (s) { s.firstElementChild.setAttribute('fill', colours[i % colours.length]); bit.appendChild(s); }
      bit.style.left = (4 + (i * 4.4) % 92) + '%';
      anim(bit, [{ transform: 'translateY(0) rotate(0deg)', opacity: 0 }, { opacity: 1, offset: 0.1 }, { transform: 'translateY(' + h + 'px) rotate(' + (260 + i * 40) + 'deg)', opacity: 1 }], 2600 + (i % 5) * 300, { delay: 1100 + (i % 7) * 230, iterations: 2, fill: 'none', easing: 'linear' });
    }
  }

  // ---- the hat (learning badges): drawn into Zorp's head, so it rides his soft body like the live hats do ----
  function wearHat(drop) {
    var z = Z();
    var svg = window.pbStage && window.pbStage.zorp();
    var head = svg && svg.querySelector('.buddy-head');
    var art = part('bp-hat');
    if (!head || !art || !z || head.querySelector('.zorp-hatride')) return;
    var g = D.createElementNS(SVGNS, 'g');
    g.setAttribute('class', 'zorp-hatride');
    var inner = D.createElementNS(SVGNS, 'g');
    inner.setAttribute('transform', 'translate(32 14.5)');
    while (art.firstElementChild.firstChild) inner.appendChild(art.firstElementChild.firstChild);
    g.appendChild(inner);
    head.appendChild(g);
    var inst = RT && RT.inst ? RT.inst({ el: svg }) : null;
    if (inst && inst.parts) inst.parts.hatRide = g;
    cur.hat = { g: g, inst: inst };
    if (drop) anim(g, [{ transform: 'translate(0,-34px) rotate(-14deg)', opacity: 0 }, { transform: 'translate(0,2px)', opacity: 1, offset: 0.7 }, { transform: 'none', opacity: 1 }], 520, { easing: 'ease-in' });
  }
  function takeOffHat() {
    var h = cur && cur.hat;
    if (!h) return;
    if (h.g.parentNode) h.g.parentNode.removeChild(h.g);
    if (h.inst && h.inst.parts) h.inst.parts.hatRide = null;
    cur.hat = null;
  }

  // ---- one badge's extras on the stage ----
  function clear() {
    if (!cur) return;
    cur.timers.forEach(clearTimeout);
    cur.anims.forEach(function (a) { try { a.cancel(); } catch (e) { /* gone */ } });
    takeOffHat();
    if (cur.layer.parentNode) cur.layer.parentNode.removeChild(cur.layer);
    cur = null;
  }

  function still(box, fam) {
    // the final frame: everything in place, nothing moving
    all(box, '.bp-card').forEach(function (c) { c.style.transform = 'rotate(' + c.getAttribute('data-a') + 'deg)'; });
    if (fam.hat) wearHat(false);
  }

  function enter(item, fam, set) {
    clear();
    var layer = el('div', 'bd-layer', set);
    cur = { layer: layer, anims: [], timers: [], hat: null };
    var box = el('div', 'bd-box', layer);
    var art = part(fam.prop) || (DRAW[fam.fx] ? DRAW[fam.fx]() : null);
    if (art) box.appendChild(art);
    var ring = part('bp-ring');
    if (ring) { ring.style.opacity = '0'; box.appendChild(ring); }
    var wrap = el('div', 'bd-medal-wrap', box);
    var medal = el('div', 'bd-medal bd-medal--' + (item.tier || 'bronze') + (item.family === 'streak' ? ' bd-medal--streak' : ''), wrap);
    el('span', 'bd-medal-glyph', medal).textContent = item.emoji || '★';
    if (!full()) { still(box, fam); if (ring) ring.style.opacity = '0'; return; }
    FX[fam.fx] && art && FX[fam.fx](box);
    if (art && !FX[fam.fx]) anim(art, [{ opacity: 0 }, { opacity: 1 }], 500, { delay: 300 });
    anim(medal, [{ transform: 'translateY(-170%) scale(1.5)', opacity: 0 }, { transform: 'translateY(0) scale(1)', opacity: 1, offset: 0.7 },
      { transform: 'scale(.93,1.07)', opacity: 1, offset: 0.8 }, { transform: 'scale(1.05,.95)', opacity: 1, offset: 0.9 }, { transform: 'none', opacity: 1 }], 1000, { delay: 350, easing: 'cubic-bezier(.4,0,.6,1)' });
    if (ring) anim(ring, [{ opacity: 0, transform: 'scale(.6)' }, { opacity: 1, transform: 'scale(1)', offset: 0.4 }, { opacity: 0, transform: 'scale(1.3)' }], 900, { delay: STAMP, fill: 'forwards' });
    if (fam.hat) later(function () { wearHat(true); }, 1700);
  }

  // ---- items -> scenes ----
  function fill(tpl, n) { return String(tpl).replace('{n}', n); }
  function streakCard(days) {
    var big = days >= 100;
    var next = UI.streakNext[days];
    return {
      key: 'streak:' + days, family: big ? 'streak100' : 'streak', emoji: '🔥', tier: 'gold', title: fill(UI.streakTitle, days),
      blurb: fill(UI.streakBlurb, days) + (big ? '\n' + UI.big : ''), next_title: '', next_how: '', note: next || '', ids: ['streak:' + days]
    };
  }
  function cardFor(spec) {
    var b = spec.badge || {};
    var key = spec.key || b.key || '';
    var meta = (function () { try { return (JSON.parse((D.getElementById('pb-milestone-catalog') || {}).textContent || '{}') || {})[key] || {}; } catch (e) { return {}; } }());
    var card = {
      key: key, family: b.family || 'learning', emoji: b.emoji || meta.emoji || '★', tier: b.tier || 'bronze', title: b.title || meta.title || UI.kicker,
      blurb: b.blurb || UI.earned, next_title: b.next_title || '', next_how: b.next_how || '', note: '', ids: ['milestone:' + key],
      wear: b.wardrobe && b.wardrobe.id ? b.wardrobe : null
    };
    // the streak badges and the streak rewards are one moment
    if (key === 'streak_7') card.ids.push('streak:7');
    if (key === 'streak_30') card.ids.push('streak:30');
    if (key === 'streak_100') card.ids.push('streak:100');   // E11 Phase 2: Century and the 100-day streak round are one moment
    return card;
  }
  function cards(specs) {
    var out = [];
    var byId = {};
    specs.forEach(function (s) {
      if (s.type !== 'milestone') return;
      var c = cardFor(s);
      if (byId[c.ids[0]]) return;
      c.ids.forEach(function (id) { byId[id] = c; });
      out.push(c);
    });
    specs.forEach(function (s) {
      if (s.type !== 'streak') return;
      var days = parseInt(s.days, 10);
      if (byId['streak:' + days]) return;
      var c = streakCard(days);
      byId[c.ids[0]] = c;
      out.push(c);
    });
    return out;
  }
  function sceneFor(card) {
    var fam = FAMILIES[card.family] || FAMILIES.learning;
    var next = card.next_title ? UI.next + card.next_title + (card.next_how ? '. ' + card.next_how : '.') : (card.note ? UI.next + card.note : '');
    return {
      id: 'badge.' + card.family, heading: card.title, props: [], layout: 'badge', face: fam.face, end: fam.end,
      lines: [card.blurb + (next ? '\n' + next : '') + (card.wear ? '\n' + UI.wardrobe.replace('{item}', card.wear.noun) : '')], beats: [fam.beats], primary: UI.primary, skipLabel: UI.profile
    };
  }

  function mark(card) {
    var g = window.pbGuide;
    if (g && g.markReward) card.ids.forEach(function (id) { g.markReward(id); });
  }

  // E11 Phase 1 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 2.4 rule 1): the badge cards as one part of a longer sequence. moments.js plays
  // a finished lesson or a 10/10, then the badges, then a level-up, in one stage with one count; play() below is this part alone.
  // show(i, st) puts card i on the stage (the kicker, Try it on, the medal), hide(st) takes this part's things off it, go() follows
  // the second button (See my milestones, or the wardrobe for Try it on). Named cardsPart, not part: part(id) above clones a prop, and
  // a second function part in this scope replaced it (E11 Phase 1 shipped stages with no medal or prop; fixed 2026-11-11).
  function cardsPart(specs) {
    var list = cards(specs || []);
    var kicker = null;
    return {
      cards: list,
      scenes: list.map(sceneFor),
      show: function (i, st) {
        var card = list[i];
        var fam = FAMILIES[card.family] || FAMILIES.learning;
        var top = st.querySelector('.pb-st-top');
        if (!kicker) { kicker = el('p', 'bd-kicker'); kicker.textContent = UI.kicker; }
        if (kicker.parentNode !== top.parentNode) top.parentNode.insertBefore(kicker, top);
        kicker.hidden = false;
        // E10 phase 6b: a badge that opens a wardrobe item offers "Try it on" (the profile wardrobe with the item put on, unsaved)
        var acts = st.querySelector('.pb-st-actions');
        var old = acts.querySelector('.bd-try');
        if (old) acts.removeChild(old);
        tryId = '';
        if (card.wear) {
          var tb = el('button', 'btn btn-outline bd-try', acts);
          tb.type = 'button';
          tb.textContent = UI.tryOn;
          tb.addEventListener('click', function () { tryId = card.wear.id; acts.querySelector('.btn-outline:not(.bd-try)').click(); });
        }
        mark(card);
        enter(card, fam, st.querySelector('.pb-st-set'));
      },
      hide: function (st) {
        if (kicker) kicker.hidden = true;
        var t = st && st.querySelector('.bd-try');
        if (t && t.parentNode) t.parentNode.removeChild(t);
        clear();
      },
      markAll: function () { list.forEach(mark); },
      go: function () {
        var url = assets().profile;
        if (!url) return;
        var a = D.createElement('a');
        a.href = url;
        if (tryId) { a.search = '?try=' + encodeURIComponent(tryId); a.hash = '#wardrobe'; location.assign(a.href); return; }
        if (a.pathname === location.pathname) location.hash = a.hash || '#milestones';
        else location.assign(url);
      },
      end: clear
    };
  }

  function play(specs) {
    var p = cardsPart(specs);
    var list = p.cards;
    if (!list.length) return Promise.resolve({ ended: 'empty' });
    wantProfile = false;
    tryId = '';
    var count = null;
    return ready().then(function () {
      return window.pbStage.play(p.scenes, {
        onScene: function (i) {
          var st = D.querySelector('.pb-stage');
          if (!st) return;
          if (!count) {
            count = el('span', 'bd-count');
            st.querySelector('.pb-st-top').appendChild(count);
            var skip = st.querySelector('.pb-st-actions .btn-outline');
            if (skip) skip.addEventListener('click', function () { wantProfile = true; }, true);
          }
          count.textContent = list.length > 1 ? (i + 1) + UI.of + list.length : '';
          p.show(i, st);
        }
      });
    }).then(function (res) {
      p.end();
      if (res && res.ended === 'skip' && wantProfile) {
        p.markAll();
        p.go();
      }
      return res;
    });
  }

  window.pbBadgeStage = { play: play, part: cardsPart, ready: ready, families: FAMILIES };
}());
