/* E7 Phase 3: /welcome mobile onboarding — Zorp clips on the hero mascot,
   cheer-then-submit on topic cards. CSP forbids inline scripts, so this file
   is the only place any of this logic lives. Plain forms still work with no
   JS: every screen is a real <form> POST. */
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

    if (step === 'hello') {
      window.pbZorp.play('wave', { el: hero }).then(function () {
        window.pbZorp.idle(true, hero);
      });
    } else if (step === 'level') {
      window.pbZorp.play('point', { el: hero, target: 'down' }).then(function () {
        window.pbZorp.idle(true, hero);
      });
    } else if (step === 'topic') {
      setTimeout(function () {
        window.pbZorp.play('think', { el: hero }).then(function () {
          window.pbZorp.idle(true, hero);
        });
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
              var cheerDone = window.pbZorp.play('cheer', { el: hero });
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
