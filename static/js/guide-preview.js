(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  function wireZorpDemo(scope) {
    var z = window.pbZorp;
    if (!z || !scope) return;
    var demos = scope.querySelectorAll('[data-zorp-demo]');
    for (var d = 0; d < demos.length; d += 1) z.bind(demos[d]);
    var level = scope.querySelector('[data-zorp-motion-level]');
    if (level) level.textContent = 'motionLevel(): ' + z.motionLevel();
    var btns = scope.querySelectorAll('[data-zorp-clip]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function (event) {
        var btn = event.currentTarget;
        for (var k = 0; k < demos.length; k += 1) {
          z.play(btn.getAttribute('data-zorp-clip'), { el: demos[k], target: btn.getAttribute('data-zorp-target') || undefined });
        }
      });
    }
    var off = scope.querySelector('[data-zorp-idle-off]');
    if (off) off.addEventListener('click', function () { for (var k = 0; k < demos.length; k += 1) z.idle(false, demos[k]); });
  }

  // E10: the stage. "arrival" is the whole film with the demo choices as scene 6; "story" the film alone; a scene id one scene.
  function wireStage(scope) {
    var g = window.pbGuide;
    if (!scope || !g || typeof g.loadStage !== 'function') return;
    var demo = scope.querySelector('[data-stage-demo]');
    function run(id) {
      g.loadStage().then(function (stage) {
        var ids = ((window.pbStageCatalog || {}).arrival || []).slice();
        if (id === 'arrival') stage.play(ids.concat('arrival.choose'), { slot: [demo], skipTo: ids.length });
        else if (id === 'story') stage.play('arrival', { story: true });
        else stage.play([id], { slot: [demo] });
      }).catch(function () {});
    }
    var btns = scope.querySelectorAll('[data-stage-play]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function (event) { run(event.currentTarget.getAttribute('data-stage-play')); });
    }
    var picks = scope.querySelectorAll('[data-stage-demo-pick]');
    for (var k = 0; k < picks.length; k += 1) {
      picks[k].addEventListener('click', function () {
        if (window.pbStage) window.pbStage.cue([{ play: 'cheer' }]);
      });
    }
    var want = '';
    try { want = new URLSearchParams(window.location.search).get('stage') || ''; } catch (err) { want = ''; }
    if (/^[a-z.]{1,40}$/.test(want)) run(want);
  }

  // E10 phase 8: Zorp's story chapters (0 is the arrival), played straight with no unlock check; ?story=<0-6> or ?story=offer<1-6>.
  function wireStory(scope) {
    var g = window.pbGuide;
    if (!scope || !g || typeof g.story !== 'function') return;
    function run(want) {
      var m = /^offer([1-6])$/.exec(want);
      if (m) g.offerStory(parseInt(m[1], 10)).catch(function () {});
      else if (/^[0-6]$/.test(want)) g.story(want).catch(function () {});
    }
    var btns = scope.querySelectorAll('[data-story-chapter]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function (event) { run(event.currentTarget.getAttribute('data-story-chapter')); });
    }
    var offer = scope.querySelector('[data-story-offer]');
    if (offer) offer.addEventListener('click', function () { run('offer' + offer.getAttribute('data-story-offer')); });
    var want = '';
    try { want = new URLSearchParams(window.location.search).get('story') || ''; } catch (err) { want = ''; }
    run(want);
  }

  // E10 phase 4: the badge stage, one family at a time, three at once, or the 100-day streak. Played straight on the stage, so a
  // replay is never held back by the seen-state.
  function wireBadges(scope) {
    var g = window.pbGuide;
    if (!scope || !g || typeof g.badges !== 'function') return;
    var data = {};
    try { data = JSON.parse(document.getElementById('guide-preview-badges').textContent || '{}'); } catch (err) { data = {}; }
    function spec(name) { return { type: 'milestone', key: data[name].key, badge: data[name] }; }
    function run(id) {
      var specs;
      if (id === 'streak100') specs = [{ type: 'streak', days: 100 }];
      else if (id === 'multi') specs = [spec('learning'), spec('daily'), spec('topic_master')];
      else if (data[id]) specs = [spec(id)];
      else return;
      g.badges(specs).catch(function () {});
    }
    var btns = scope.querySelectorAll('[data-badge-play]');
    for (var i = 0; i < btns.length; i += 1) {
      btns[i].addEventListener('click', function (event) { run(event.currentTarget.getAttribute('data-badge-play')); });
    }
    var want = '';
    try { want = new URLSearchParams(window.location.search).get('badge') || ''; } catch (err) { want = ''; }
    if (/^[a-z0-9_]{1,24}$/.test(want)) run(want);
  }

  ready(function () {
    wireBadges(document.getElementById('guide-preview-badge-stage'));
    wireZorpDemo(document.getElementById('guide-preview-motion-section'));
    wireStage(document.getElementById('guide-preview-stage'));
    wireStory(document.getElementById('guide-preview-story'));
    if (!window.pbGuide) return;
    var playBtn = document.getElementById('guide-preview-play');
    var resetBtn = document.getElementById('guide-preview-reset');
    var badgeBtn = document.getElementById('guide-preview-badge');
    var streakBtn = document.getElementById('guide-preview-streak');
    var practiceBtn = document.getElementById('guide-preview-practice');
    var profileBtn = document.getElementById('guide-preview-profile');
    var dailyBtn = document.getElementById('guide-preview-daily');
    var learnBtn = document.getElementById('guide-preview-learn');
    var competeBtn = document.getElementById('guide-preview-compete');
    var firstBtn = document.getElementById('guide-preview-first');
    var lessonBtn = document.getElementById('guide-preview-lesson');
    var winkBtn = document.getElementById('guide-preview-wink');
    var nodBtn = document.getElementById('guide-preview-nod');
    var shakeBtn = document.getElementById('guide-preview-shake');
    var tapBtn = document.getElementById('guide-preview-tap');

    if (playBtn) {
      playBtn.addEventListener('click', function () {
        window.pbGuide.play('origin');
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        window.pbGuide.resetOrigin();
        window.pbGuide.play('origin');
      });
    }
    if (badgeBtn) {
      badgeBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'milestone', key: 'first_quiz' });
      });
    }
    if (streakBtn) {
      streakBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'streak', days: 7 });
      });
    }
    if (practiceBtn) {
      practiceBtn.addEventListener('click', function () {
        window.pbGuide.play('practice');
      });
    }
    if (profileBtn) {
      profileBtn.addEventListener('click', function () {
        window.pbGuide.play('profile');
      });
    }
    if (dailyBtn) {
      dailyBtn.addEventListener('click', function () {
        window.pbGuide.play('daily');
      });
    }
    if (learnBtn) {
      learnBtn.addEventListener('click', function () {
        window.pbGuide.play('learn');
      });
    }
    if (competeBtn) {
      competeBtn.addEventListener('click', function () {
        window.pbGuide.play('compete');
      });
    }
    if (firstBtn) {
      firstBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'first_correct' });
      });
    }
    if (lessonBtn) {
      lessonBtn.addEventListener('click', function () {
        window.pbGuide.reward({ type: 'lesson_complete' });
      });
    }
    function bindGesture(btn, name) {
      if (!btn) return;
      btn.addEventListener('click', function () {
        if (window.pbGuide && typeof window.pbGuide.gesture === 'function') {
          window.pbGuide.gesture(name);
        }
      });
    }
    bindGesture(winkBtn, 'wink');
    bindGesture(nodBtn, 'nod');
    bindGesture(shakeBtn, 'shake');
    bindGesture(tapBtn, 'tap');
  });
})();
