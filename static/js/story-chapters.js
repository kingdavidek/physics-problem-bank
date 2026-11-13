/* Zorp's story chapters (E10 phase 8, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A6 and section 11.13). Loaded on demand by guide.js
   (pbGuide.story, or when a moment offers a chapter) with story.css and static/images/story-props.svg, only when a chapter plays or
   is offered; never on an ordinary page. Six short chapters continue the arrival film on the same stage (zorp-stage.js), with the
   arrival's planet, ship, crew and logbook plus four new props (rock, door, toaster, postcard). Chapter 0 is the arrival itself.
   Which chapters a pupil may watch is the server's (models/story.py); this file holds the words and the choreography.
   A scene is the stage-catalog.js shape: id, heading, props, layout, face (start), end (the face it ends on), lines, one list of beats
   per line, primary and skipLabel; `lore` marks the one wistful beat, which carries a positive `resolve` (the face the chapter ends
   on). Every face is positive or neutral (CONTEXT_MAP['stage']); every chapter ends positive. Copy (UI and scene lines) is read by the
   voice lint (models/zorp_voice.py extract_story_copy); scripts/test_story_chapters_smoke.py checks shape, beats and valence.
   Motion, dialog, focus, Esc and Skip are the stage's. The offer is a corner toast (Watch, Later): it never plays by itself.
   Watched and offered chapters are flags (story_w<n>, story_o<n>) in the protected tours region of the guide state. */
(function () {
  'use strict';
  if (window.pbStory) return;
  var D = document;
  // BEGIN COPY
  var UI = {
    offer: 'Zorp has a new story for you',
    watch: 'Watch',
    later: 'Later'
  };
  // END COPY
  var TOAST_MS = 20000;
  var CHAPTERS = [
    {
      n: 1, title: 'The maths belt',
      scenes: [
        {
          id: 'story.belt.fly',
          heading: 'Chapter 1: The maths belt',
          props: ['planet'],
          layout: 'centre',
          face: 'happy',
          end: 'grin',
          lines: [
            'Today I’m flying along the maths belt, the ring of rocks around Novara.',
            'I steer by wobbling. My antennae do not help.',
          ],
          beats: [
            [{ prop: 'planet', async: 1 }, { wait: 300 }, { prop: 'planet', set: 'belt' }, { talk: 1 }, { play: 'float' }],
            [{ talk: 1 }, { play: 'wobble' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.belt.rock',
          heading: 'Chapter 1: The maths belt',
          props: ['rock'],
          layout: 'centre',
          face: 'curious',
          end: 'happy',
          lines: [
            'Look closer. Every rock has a puzzle painted on it. This one is six times seven.',
            'Oh! It tumbled away. That means someone on Novara solved it.',
          ],
          beats: [
            [{ prop: 'rock' }, { wait: 400 }, { talk: 1 }, { play: 'think-chin' }],
            [{ prop: 'rock', set: 'solved' }, { wait: 700 }, { prop: 'rock', set: 'tumble' }, { talk: 1 }, { play: 'hop' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.belt.roll',
          heading: 'Chapter 1: The maths belt',
          props: ['planet'],
          layout: 'centre',
          face: 'happy',
          end: 'grin',
          lines: [
            'Down there, someone is on a roll. A roll of rocks, mostly.',
            'I tried one myself and said “fish”. The rock let me try again.',
          ],
          beats: [
            [{ prop: 'planet', set: 'belt' }, { talk: 1 }, { play: 'nod' }],
            [{ talk: 1 }, { play: 'cheer' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
          story: {
            primary: 'Done',
          },
        },
      ],
    },
    {
      n: 2, title: 'Meet the crew',
      scenes: [
        {
          id: 'story.crew.hello',
          heading: 'Chapter 2: Meet the crew',
          props: ['ship'],
          layout: 'centre',
          face: 'happy',
          end: 'grin',
          lines: [
            'Time to meet my crew. From the left, that is Pim, Juno and Tock.',
            'Pim is our cook. Pim stirs each pot twice, even the tea.',
          ],
          beats: [
            [{ prop: 'ship' }, { crew: 'wave', async: 1 }, { turn: 'back-glance', facing: 'l' }, { wait: 900 }, { turn: 'front' }, { talk: 1 }, { play: 'wave' }],
            [{ talk: 1 }, { crew: 'hop', async: 1 }, { play: 'nod' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.crew.park',
          heading: 'Chapter 2: Meet the crew',
          props: ['ship'],
          layout: 'centre',
          face: 'happy',
          end: 'soft-smile',
          lines: [
            'Juno is our pilot. Juno flies like a dream and parks like a sneeze.',
            'That bump was a moon. Juno says the moon moved.',
          ],
          beats: [
            [{ talk: 1 }, { crew: 'hop', async: 1 }, { play: 'hop' }],
            [{ prop: 'ship', set: 'bump' }, { wait: 500 }, { talk: 1 }, { play: 'shrug' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.crew.tock',
          heading: 'Chapter 2: Meet the crew',
          props: ['ship'],
          layout: 'centre',
          face: 'soft-smile',
          end: 'grin',
          lines: [
            'Tock is our engineer. Tock chats to the engine, and the engine hums back.',
            'I cannot park either. I never bring it up.',
          ],
          beats: [
            [{ talk: 1 }, { crew: 'wave', async: 1 }, { play: 'nod' }],
            [{ talk: 1 }, { crew: 'wave', async: 1 }, { play: 'wave' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
          story: {
            primary: 'Done',
          },
        },
      ],
    },
    {
      n: 3, title: 'Puzzle doors',
      scenes: [
        {
          id: 'story.doors.door',
          heading: 'Chapter 3: Puzzle doors',
          props: ['door'],
          layout: 'centre',
          face: 'happy',
          end: 'proud',
          lines: [
            'On Novara, a door is a puzzle with a handle. This one wants eight plus five.',
            'Thirteen. And it opens. No key and no knocking, only thinking.',
          ],
          beats: [
            [{ prop: 'door' }, { wait: 400 }, { talk: 1 }, { play: 'think-chin' }],
            [{ prop: 'door', set: 'open' }, { wait: 600 }, { talk: 1 }, { play: 'cheer' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.doors.toaster',
          heading: 'Chapter 3: Puzzle doors',
          props: ['toaster'],
          layout: 'centre',
          face: 'curious',
          end: 'happy',
          lines: [
            'Even the toaster has one. It will not make toast until it is solved.',
            'I once waited ten minutes for breakfast. It was long division.',
          ],
          beats: [
            [{ prop: 'toaster' }, { wait: 300 }, { talk: 1 }, { play: 'shrug' }],
            [{ prop: 'toaster', set: 'pop' }, { wait: 500 }, { talk: 1 }, { play: 'hop' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.doors.front',
          heading: 'Chapter 3: Puzzle doors',
          props: ['door'],
          layout: 'centre',
          face: 'soft-smile',
          end: 'grin',
          lines: [
            'I tried my own front door once. It asked for a square root.',
            'I stood there for an hour. The neighbours brought snacks.',
          ],
          beats: [
            [{ prop: 'door' }, { talk: 1 }, { play: 'think-chin' }],
            [{ talk: 1 }, { play: 'wink' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
          story: {
            primary: 'Done',
          },
        },
      ],
    },
    {
      n: 4, title: 'Home',
      scenes: [
        {
          // the one wistful beat: it opens quiet and tender, about Zorp's own feelings, and resolves warmly in the next scene
          id: 'story.home.look',
          heading: 'Chapter 4: Home',
          props: ['planet'],
          layout: 'centre',
          lore: true,
          resolve: 'joy',
          face: 'aww',
          end: 'aww',
          lines: [
            'Now and then I look up and find Novara, small and far away.',
            'I think about the doors and the belt and the warm toast. Then I go quiet for a bit.',
          ],
          beats: [
            [{ prop: 'planet', async: 1 }, { wait: 400 }, { turn: 'side', facing: 'l' }, { talk: 1 }, { play: 'stage-gaze' }],
            [{ talk: 1 }, { wait: 600 }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.home.cheer',
          heading: 'Chapter 4: Home',
          props: ['planet'],
          layout: 'centre',
          face: 'curious',
          end: 'joy',
          lines: [
            'Then I remember how much there is to learn on Earth. There are so many puzzles.',
            'Novara will keep. The sky here is excellent, and I have a logbook to fill.',
          ],
          beats: [
            [{ turn: 'front' }, { prop: 'planet', set: 'belt' }, { talk: 1 }, { play: 'think-chin' }],
            [{ burst: 1 }, { talk: 1 }, { play: 'cheer' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
          story: {
            primary: 'Done',
          },
        },
      ],
    },
    {
      n: 5, title: 'The logbook',
      scenes: [
        {
          id: 'story.logbook.open',
          heading: 'Chapter 5: The logbook',
          props: ['logbook'],
          layout: 'left',
          face: 'happy',
          end: 'proud',
          lines: [
            'This is my logbook. It is full of things people on Earth worked out.',
            'Like this one. People measured the whole Earth with a stick and its shadow.',
          ],
          beats: [
            [{ prop: 'logbook' }, { talk: 1 }, { play: 'hop' }],
            [{ prop: 'logbook', set: 'open' }, { wait: 300 }, { prop: 'logbook', set: 'notes' }, { talk: 1 }, { play: 'side-point', target: 'down' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.logbook.feather',
          heading: 'Chapter 5: The logbook',
          props: ['logbook'],
          layout: 'left',
          face: 'curious',
          end: 'happy',
          lines: [
            'And this one. On the Moon, a feather and a hammer fall together.',
            'I tried it with a sock and a spanner. The air sided with the sock.',
          ],
          beats: [
            [{ talk: 1 }, { play: 'think-chin' }],
            [{ talk: 1 }, { play: 'shrug' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.logbook.thick',
          heading: 'Chapter 5: The logbook',
          props: ['logbook'],
          layout: 'left',
          face: 'soft-smile',
          end: 'proud',
          lines: [
            'Page after page, people kept asking why. That is how a logbook gets thick.',
            'I am very impressed. I am also nearly out of pages.',
          ],
          beats: [
            [{ talk: 1 }, { play: 'nod' }],
            [{ talk: 1 }, { play: 'bow' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
          story: {
            primary: 'Done',
          },
        },
      ],
    },
    {
      n: 6, title: 'A postcard from Novara',
      scenes: [
        {
          id: 'story.postcard.ship',
          heading: 'Chapter 6: A postcard from Novara',
          props: ['ship'],
          layout: 'centre',
          face: 'happy',
          end: 'grin',
          lines: [
            'A message has landed from the ship. Pim wrote it. Juno posted it, a little crooked.',
            'It is a postcard from Novara.',
          ],
          beats: [
            [{ prop: 'ship' }, { crew: 'wave', async: 1 }, { turn: 'back-glance', facing: 'l' }, { wait: 900 }, { turn: 'front' }, { talk: 1 }, { play: 'wave' }],
            [{ talk: 1 }, { play: 'nod' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.postcard.card',
          heading: 'Chapter 6: A postcard from Novara',
          props: ['postcard'],
          layout: 'centre',
          face: 'curious',
          end: 'proud',
          lines: [
            'It says the engine is warm and the toast is ready.',
            'Juno added a note. It says: “I parked on the first go.” Nobody believes it.',
          ],
          beats: [
            [{ prop: 'postcard' }, { wait: 400 }, { talk: 1 }, { play: 'think-chin' }],
            [{ prop: 'postcard', set: 'stamp' }, { wait: 500 }, { talk: 1 }, { play: 'hop' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
        },
        {
          id: 'story.postcard.more',
          heading: 'Chapter 6: A postcard from Novara',
          props: ['postcard'],
          layout: 'centre',
          face: 'soft-smile',
          end: 'happy',
          lines: [
            'More stories may come one day. I have left some pages free in my logbook.',
            'For now, this goes on the wall, right next to the toaster.',
          ],
          beats: [
            [{ prop: 'postcard', set: 'stamp' }, { talk: 1 }, { play: 'nod' }],
            [{ talk: 1 }, { play: 'wave' }],
          ],
          primary: 'Next',
          skipLabel: 'Skip story',
          story: {
            primary: 'Done',
          },
        },
      ],
    },
  ];

  var propsP = null;
  var toasts = [];

  function Z() { return window.pbZorp || null; }
  function G() { return window.pbGuide || null; }
  function full() {
    var z = Z();
    return !!(z && z.motionLevel && z.motionLevel() === 'full');
  }
  function el(tag, cls, parent) {
    var n = D.createElement(tag);
    if (cls) n.className = cls;
    if (parent) parent.appendChild(n);
    return n;
  }
  function chapter(n) {
    for (var i = 0; i < CHAPTERS.length; i += 1) if (CHAPTERS[i].n === n) return CHAPTERS[i];
    return null;
  }

  // the story props (rock, door, toaster, postcard) are a second template that the stage reads beside its own
  function ready() {
    if (propsP) return propsP;
    var a = {};
    try { a = JSON.parse((D.getElementById('pb-story-assets') || {}).textContent || '{}') || {}; } catch (e) { a = {}; }
    propsP = (a.props && window.fetch && window.DOMParser ? fetch(a.props, { credentials: 'same-origin' }).then(function (r) {
      return r.ok ? r.text() : '';
    }).then(function (text) {
      var doc = text ? new window.DOMParser().parseFromString(text, 'image/svg+xml') : null;
      if (doc && !doc.getElementsByTagName('parsererror').length && window.pbStage) window.pbStage.addProps(doc);
    }) : Promise.resolve()).catch(function () { /* the scenes still play without the new props */ });
    return propsP;
  }

  function mark(flag) {
    var g = G();
    if (g && g.tour && g.tour.markSeen) g.tour.markSeen(flag);
  }

  // n 0 is the arrival film (its story scenes only); 1 to 6 are the chapters. Resolves { ended, scene }.
  function play(n, opts) {
    var stage = window.pbStage;
    n = parseInt(n, 10);
    if (!stage || !(n >= 0 && n <= 6)) return Promise.resolve({ ended: 'none', scene: '' });
    if (n === 0) return ready().then(function () { return stage.play('arrival', opts || {}); });
    var ch = chapter(n);
    if (!ch) return Promise.resolve({ ended: 'none', scene: '' });
    return ready().then(function () {
      // docs/CELEBRATION_SOUNDS_PLAN.md 3: a music-box phrase as the chapter opens (sound.js decides; reduced motion: soft)
      return stage.play(ch.scenes, { story: true, onScene: function (i) { if (!i && window.pbSound && window.pbSound.play) window.pbSound.play('story', { soft: !full() }); } });
    }).then(function (res) {
      if (res && res.ended === 'done') {
        mark('story_w' + n);
        try { D.dispatchEvent(new CustomEvent('pb-story-watched', { detail: { n: n } })); } catch (e) { /* old browser */ }
      }
      return res;
    });
  }

  // ---- the offer: a corner toast with a mini Zorp, "Zorp has a new story for you", Watch and Later. Never plays by itself. ----
  function miniZorp(parent) {
    var holder = el('span', 'sty-mz study-buddy-face', parent);
    holder.setAttribute('data-buddy-face', '');
    holder.setAttribute('aria-hidden', 'true');
    var src = D.querySelector('[data-guide-face] svg.buddy-mascot') || D.querySelector('svg.buddy-mascot');
    var z = Z();
    if (!src) { holder.hidden = true; return; }
    var svg = src.cloneNode(true);
    svg.classList.remove('is-zorp-idle');
    holder.appendChild(svg);
    if (z) {
      z.bind(holder);
      z.turn('front', 'r', { el: svg, instant: true });
      if (z.valenceOf && z.valenceOf('happy') !== 'negative') z.setExpression('happy', { el: svg });
    }
  }
  function dismiss(t) {
    if (!t || t.gone) return;
    t.gone = true;
    clearTimeout(t.timer);
    t.node.classList.add('is-leaving');
    setTimeout(function () { if (t.node.parentNode) t.node.parentNode.removeChild(t.node); }, full() ? 180 : 0);
    toasts = toasts.filter(function (x) { return x !== t; });
  }
  function onEsc(e) {
    if (e.key !== 'Escape' || !toasts.length || (window.pbStage && window.pbStage.isOpen())) return;
    var a = D.activeElement;
    if (a && a !== D.body && !(a.closest && a.closest('.pb-stoast'))) return;
    dismiss(toasts[toasts.length - 1]);
  }
  function onceFor(id) {
    try {
      if (window.sessionStorage.getItem('pb-story:' + id)) return false;
      window.sessionStorage.setItem('pb-story:' + id, '1');
    } catch (e) { /* no storage: the server offers each unlock once */ }
    return true;
  }
  function offer(m) {
    var n = parseInt(m && m.chapter, 10);
    var ch = chapter(n);
    var host = D.getElementById('app-toast-host');
    var g = G();
    if (!ch || !host || !g || !g.tour) return;
    if (!m.force && (g.tour.seen('story_w' + n) || !onceFor(m.id || ('story:' + n)))) return;
    var node = el('div', 'app-toast is-success pb-stoast', host);
    node.setAttribute('role', 'status');
    miniZorp(el('span', 'app-toast-icon', node));
    var body = el('div', 'app-toast-body', node);
    el('p', 'app-toast-message', body).textContent = UI.offer;
    el('p', 'sty-sub', body).textContent = 'Chapter ' + n + ': ' + ch.title;
    var acts = el('div', 'sty-acts', body);
    var watch = el('button', 'btn btn-primary', acts);
    var later = el('button', 'btn btn-outline', acts);
    var x = el('button', 'app-toast-dismiss', node);
    watch.type = later.type = x.type = 'button';
    watch.textContent = UI.watch;
    later.textContent = UI.later;
    x.setAttribute('aria-label', 'Dismiss');
    x.textContent = '×';
    var t = { node: node, timer: 0, gone: false };
    function arm() { clearTimeout(t.timer); t.timer = setTimeout(function () { dismiss(t); }, TOAST_MS); }
    watch.addEventListener('click', function () { dismiss(t); play(n); });
    later.addEventListener('click', function () { dismiss(t); });
    x.addEventListener('click', function () { dismiss(t); });
    node.addEventListener('mouseenter', function () { clearTimeout(t.timer); });
    node.addEventListener('mouseleave', arm);
    node.addEventListener('focusin', function () { clearTimeout(t.timer); });
    node.addEventListener('focusout', arm);
    toasts.push(t);
    if (toasts.length === 1) D.addEventListener('keydown', onEsc);
    if (!m.force) mark('story_o' + n);   // offered: the catch-up offer is made once, and a Later is final
    arm();
  }

  window.pbStory = { play: play, offer: offer, chapters: CHAPTERS };
}());
