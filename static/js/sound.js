(function () {
  'use strict';

  var ctx = null;
  var unlockBound = false;

  function isEnabled() {
    var body = document.body;
    if (!body) return false;
    return body.getAttribute('data-sound-enabled') === '1';
  }

  function ensureCtx() {
    if (ctx) return ctx;
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
      return ctx;
    } catch (err) {
      return null;
    }
  }

  function ctxReady() {
    var audio = ensureCtx();
    if (!audio) return Promise.resolve(null);
    if (audio.state === 'suspended') {
      return audio.resume().then(function () { return audio; }).catch(function () { return null; });
    }
    return Promise.resolve(audio);
  }

  function bindUnlock() {
    if (unlockBound || !isEnabled()) return;
    unlockBound = true;
    var unlock = function () {
      ctxReady();
    };
    document.addEventListener('pointerdown', unlock, { capture: true, passive: true });
    document.addEventListener('keydown', unlock, { capture: true, passive: true });
  }

  function playTone(audio, freq, durationMs, type, gain, delayMs) {
    var startAt = (delayMs || 0) / 1000;
    var osc = audio.createOscillator();
    var amp = audio.createGain();
    osc.type = type || 'sine';
    osc.frequency.value = freq;
    var peak = gain || 0.12;
    amp.gain.setValueAtTime(0.0001, audio.currentTime + startAt);
    amp.gain.exponentialRampToValueAtTime(peak, audio.currentTime + startAt + 0.02);
    amp.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + startAt + durationMs / 1000);
    osc.connect(amp);
    amp.connect(audio.destination);
    osc.start(audio.currentTime + startAt);
    osc.stop(audio.currentTime + startAt + durationMs / 1000 + 0.04);
  }

  function playSequence(steps) {
    if (!isEnabled()) return;
    ctxReady().then(function (audio) {
      if (!audio) return;
      steps.forEach(function (step) {
        playTone(audio, step.freq, step.dur, step.type, step.gain, step.delay);
      });
    });
  }

  function playCorrect() {
    playSequence([
      { freq: 523.25, dur: 90, type: 'sine', gain: 0.11, delay: 0 },
      { freq: 659.25, dur: 110, type: 'sine', gain: 0.1, delay: 70 },
    ]);
  }

  function playWrong() {
    playSequence([
      { freq: 196, dur: 160, type: 'triangle', gain: 0.14, delay: 0 },
    ]);
  }

  function playCelebrate() {
    var notes = [523.25, 659.25, 783.99, 1046.5];
    playSequence(notes.map(function (freq, i) {
      return { freq: freq, dur: 100, type: 'sine', gain: 0.1, delay: i * 90 };
    }));
  }

  function setEnabled(value) {
    var on = !!value;
    if (document.body) {
      document.body.setAttribute('data-sound-enabled', on ? '1' : '0');
    }
    if (on) bindUnlock();
  }

  if (isEnabled()) bindUnlock();

  window.pbSound = {
    enabled: isEnabled,
    setEnabled: setEnabled,
    correct: playCorrect,
    wrong: playWrong,
    celebrate: playCelebrate,
    preview: playCorrect,
  };
})();
