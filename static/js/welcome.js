/* E7 Phase 3: /welcome mobile onboarding — Zorp clips on the hero mascot,
   celebrate-then-submit on topic cards. CSP forbids inline scripts, so this file
   is the only place any of this logic lives. Plain forms still work with no
   JS: every screen is a real <form> POST.
   E8 Phase 5: hello = turn in from the side, then wave (the server draws the hello hero in profile and this
   turns it to face the pupil; reduced and off turn instantly, never leaving it sideways); level = point
   down from the side; topic = think with a hand on the chin; a card tap = the fist-pump jump. Each clip
   falls back to its E7 twin when zorp-poses.js is missing. */
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

  ready(function () {
    var section = document.getElementById('welcome');
    var hero = document.querySelector('[data-welcome-hero]');
    if (!section || !hero || !window.pbZorp) return;

    var svg = window.pbZorp.bind(hero);
    if (!svg) return;

    var step = section.getAttribute('data-step');
    var zorp = window.pbZorp;
    var settle = function () { zorp.idle(true, hero); };
    var clipOr = function (name, fallback) {
      return typeof zorp.hasClip === 'function' && zorp.hasClip(name) ? name : fallback;
    };

    if (step === 'hello') {
      var greet = function () {
        zorp.turn('front', 'r', { el: hero, required: true }).then(function () {
          return zorp.play('wave', { el: hero });
        }).then(settle, settle);
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
    }

    if (step === 'topic') {
      var form = document.getElementById('welcome-topic-form');
      if (form) {
        var submitting = false;
        // Safari's back-forward cache can restore this exact page (and this exact
        // closure) with `submitting` still true from a tap that never actually
        // navigated away — without this, every card silently does nothing until
        // reload. `event.persisted` is true only for a bfcache restore.
        window.addEventListener('pageshow', function (evt) {
          if (evt.persisted) submitting = false;
        });
        var buttons = form.querySelectorAll('button[name="topic"]');
        for (var i = 0; i < buttons.length; i += 1) {
          buttons[i].addEventListener('click', function (evt) {
            if (window.pbZorp.motionLevel() !== 'full') return; // plain submit
            evt.preventDefault();
            if (submitting) return;
            submitting = true;
            var btn = evt.currentTarget;
            try {
              var cheerDone = window.pbZorp.play(clipOr('fist-pump', 'cheer'), { el: hero });
              var timeoutDone = new Promise(function (resolve) {
                setTimeout(resolve, 450);
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
          });
        }
      }
    }
  });
})();
