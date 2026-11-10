/* E7 Phase 3: /welcome mobile onboarding — Zorp clips on the hero mascot,
   celebrate-then-submit on topic cards. CSP forbids inline scripts, so this file
   is the only place any of this logic lives. Plain forms still work with no
   JS: every screen is a real <form> POST.
   E8 Phase 5: hello = turn in from the side, then wave (the server draws the hello hero in profile and this
   turns it to face the pupil; reduced and off turn instantly, never leaving it sideways); level = point
   down from the side; topic = think with a hand on the chin; a card tap = the fist-pump jump. Each clip
   falls back to its E7 twin when zorp-poses.js is missing.
   E9 Phase 1: hello (after the wave) and ready (after 400 ms) talk the copy line once; see talkCopy.
   E10 (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A1): the arrival film. The stage (pbGuide.loadStage) plays scenes 1 to 5
   on the hello step, then scene 6 shows this page's real forms (the nodes marked data-arrival-slot); the level, topic and
   ready steps open the stage straight at scene 6. Skip intro jumps to scene 6, Skip for now still posts the skip step,
   and reaching scene 6 marks the origin story seen (pbGuide.markSeen; welcome_step also records it). A pick cheers, Start
   fist-pumps, then the form submits. When the stage cannot load, the E7 hero animations below run instead. */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  function submitViaButton(form, btn) {
    if (typeof form.requestSubmit === 'function') {
      form.requestSubmit(btn);
      return;
    }
    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = btn.name;
    hidden.value = btn.value;
    form.appendChild(hidden);
    form.submit();
  }

  // A tap on a choice: Zorp celebrates (`celebrate` returns its clip's promise), then the form submits. Full motion only;
  // otherwise the plain submit goes through at once.
  var submitting = false;
  // Safari's back-forward cache can restore this exact page (and this exact
  // closure) with `submitting` still true from a tap that never actually
  // navigated away — without this, every card silently does nothing until
  // reload. `event.persisted` is true only for a bfcache restore.
  window.addEventListener('pageshow', function (evt) {
    if (evt.persisted) submitting = false;
  });
  function celebrateThenSubmit(evt, form, celebrate) {
    if (!window.pbZorp || window.pbZorp.motionLevel() !== 'full') return; // plain submit
    evt.preventDefault();
    if (submitting) return;
    submitting = true;
    var btn = evt.currentTarget;
    try {
      var cheerDone = celebrate();
      // 650 ms lets the Zorp land cue (about 620 ms) finish; 450 ms when no cue is playing
      var holdMs = window.pbSound && typeof window.pbSound.cuesActive === 'function' && window.pbSound.cuesActive() ? 650 : 450;
      var timeoutDone = new Promise(function (resolve) {
        setTimeout(resolve, holdMs);
      });
      Promise.race([cheerDone, timeoutDone]).then(function () {
        submitViaButton(form, btn);
      }).catch(function () {
        submitViaButton(form, btn);
      });
    } catch (err) {
      // A mascot glitch must never strand the pupil on a dead card.
      submitViaButton(form, btn);
    }
  }

  // The buttons are found through their form (the Start button sits outside its form, so it is passed alone).
  function onChoices(form, buttons, celebrate) {
    if (!form || !buttons) return;
    for (var i = 0; i < buttons.length; i += 1) {
      buttons[i].addEventListener('click', function (evt) {
        celebrateThenSubmit(evt, form, celebrate);
      });
    }
  }
  function formCards(id, name) {
    var form = document.getElementById(id);
    return [form, form && form.querySelectorAll('button[name="' + name + '"]')];
  }

  // ---- E10: the arrival on the stage ----
  function slotNodes() {
    var nodes = Array.prototype.slice.call(document.querySelectorAll('[data-arrival-slot]'));
    return nodes.sort(function (a, b) {
      return (+a.getAttribute('data-arrival-slot') || 0) - (+b.getAttribute('data-arrival-slot') || 0);
    });
  }

  function arrival(section, step) {
    var guide = window.pbGuide;
    var slot = slotNodes();
    if (!guide || typeof guide.loadStage !== 'function' || !slot.length) return false;
    // the plain screen waits under the stage; it comes back if the stage closes or takes too long to load
    section.style.opacity = '0';
    var shown = false;
    var reveal = function () {
      if (shown) return;
      shown = true;
      section.style.opacity = '';
    };
    var slow = setTimeout(reveal, 3000);
    guide.loadStage().then(function (stage) {
      var ids = ((window.pbStageCatalog || {}).arrival || []).concat('arrival.choose');
      var choose = ids.length - 1;
      var cue = function (clip) {
        return function () { return stage.cue([{ play: clip }]); };
      };
      var level = formCards('welcome-level-form', 'level');
      var topic = formCards('welcome-topic-form', 'topic');
      var start = document.getElementById('welcome-ready-btn');
      onChoices(level[0], level[1], cue('cheer'));
      onChoices(topic[0], topic[1], cue('cheer'));
      onChoices(document.getElementById('welcome-ready-form'), start ? [start] : null, cue('fist-pump'));
      clearTimeout(slow);
      return stage.play(ids, {
        slot: slot,
        skipTo: choose,
        start: step === 'hello' ? 0 : choose,
        resume: step !== 'hello',
        onScene: function (i) {
          if (i === choose && typeof guide.markSeen === 'function') guide.markSeen('origin');
        }
      }).then(reveal);
    }).catch(function () {
      clearTimeout(slow);
      reveal();
      plainScreens(step);
    });
    return true;
  }

  // ---- E7 to E9: the hero on the plain screens (no stage) ----
  function plainScreens(step) {
    var hero = document.querySelector('[data-welcome-hero]');
    if (!hero || !window.pbZorp) return;
    var svg = window.pbZorp.bind(hero);
    if (!svg) return;

    var zorp = window.pbZorp;
    var settle = function () { zorp.idle(true, hero); };
    // E9 Phase 1: on hello and ready the mouth says the start of the page's last copy line, once (cap 1.4 s). The text is
    // already on the page; without zorp-talk.js (no talk) nothing changes.
    var copyEls = document.querySelectorAll('.welcome-copy');
    var copyEl = copyEls[copyEls.length - 1];
    var talkCopy = function () {
      if (typeof zorp.talk === 'function' && copyEl) zorp.talk({ el: hero, text: copyEl.textContent, max: 1400 });
    };
    var clipOr = function (name, fallback) {
      return typeof zorp.hasClip === 'function' && zorp.hasClip(name) ? name : fallback;
    };

    if (step === 'hello') {
      var greet = function () {
        zorp.turn('front', 'r', { el: hero, required: true }).then(function () {
          return zorp.play('wave', { el: hero });
        }).then(settle, settle).then(talkCopy);
      };
      if (zorp.motionLevel() === 'full') {
        // The server draws the hero front-facing (no-JS safe); drop to profile at once, then turn in.
        zorp.turn('side', 'r', { el: hero, instant: true });
        setTimeout(greet, 350);
      } else greet();
    } else if (step === 'level') {
      zorp.play(clipOr('side-point', 'point'), { el: hero, target: 'down' }).then(settle);
    } else if (step === 'topic') {
      setTimeout(function () {
        zorp.play(clipOr('think-chin', 'think'), { el: hero }).then(settle);
      }, 400);
    } else if (step === 'ready') {
      window.pbZorp.idle(true, hero);
      setTimeout(talkCopy, 400);
    }

    if (step === 'topic') {
      var cards = formCards('welcome-topic-form', 'topic');
      onChoices(cards[0], cards[1], function () {
        return window.pbZorp.play(clipOr('fist-pump', 'cheer'), { el: hero, cue: true });
      });
    }
  }

  ready(function () {
    var section = document.getElementById('welcome');
    if (!section) return;
    var step = section.getAttribute('data-step');
    if (!arrival(section, step)) plainScreens(step);
  });
})();
