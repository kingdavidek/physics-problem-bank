(function () {
  'use strict';

  var ctx = null;
  var unlockBound = false;

  // E9 Phase 4 (docs/ZORP_CHARM.md 3.4): Zorp's cues. Times are Date.now() values.
  var lastGesture = -1e9;   // last pointerdown, pointerup, touchend or keydown
  var lastSound = -1e9;     // latest pbSound sound of any kind (the 400 ms arbiter)
  var seq = { at: -1e9, cue: '', cueAt: -1e9 };   // latest cue sequence start; latest cue
  var bus = null;           // cues and blips share one node, so stopAll() can cut them
  var GESTURE_MS = 5000;
  var ARBITER_MS = 400;
  var SEQ_MS = 7000;
  var CUE_GAIN = 0.06;      // below soft (0.08), the quietest answer tone
  var BLIP_GAIN = 0.03;
  // [wave, from Hz, to Hz, ms, delay ms, attack ms]
  var CUES = {
    jump: [['sine', 330, 660, 160, 0, 20]],
    land: [['triangle', 180, 120, 90, 0, 6]],
    tada: [['sine', 523.25, 523.25, 160, 0, 12], ['sine', 659.25, 659.25, 160, 70, 12], ['sine', 783.99, 783.99, 160, 140, 12]]
  };

  function isEnabled() {
    var body = document.body;
    if (!body) return false;
    return body.getAttribute('data-sound-enabled') === '1';
  }

  // html[data-zorp-sound] mirrors zorp_sound: off (default), celebrations (chatter is defined, never offered).
  function zorpMode() {
    return document.documentElement.getAttribute('data-zorp-sound');
  }

  function inQuiz() {
    return !!document.body && document.body.getAttribute('data-guide-quiz') === '1';
  }

  // rules 2, 3 and 4 (3.4.3): a tap in the last 5 s, a visible page, not the quiz runner
  function awake(now) {
    return now - lastGesture <= GESTURE_MS && !document.hidden && !inQuiz();
  }

  function audioClass() {
    return window.AudioContext || window.webkitAudioContext;
  }

  function ensureCtx() {
    if (ctx) return ctx;
    try {
      var AC = audioClass();
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

  function stopAll() {
    var b = bus;
    bus = null;
    if (!b) return;
    try {
      var t = ctx.currentTime;
      b.gain.cancelScheduledValues(t);
      b.gain.setValueAtTime(b.gain.value, t);
      b.gain.linearRampToValueAtTime(0, t + 0.03);
    } catch (err) { /* no ramp: cut at once */ }
    setTimeout(function () { try { b.disconnect(); } catch (err) { /* gone */ } }, 45);
  }

  function bindUnlock(always) {
    if (unlockBound || !(always || isEnabled() || zorpMode() === 'celebrations')) return;
    unlockBound = true;
    var unlock = function () {
      lastGesture = Date.now();
      ctxReady();
    };
    // pointerup and touchend too: iPad/WebKit counts the end of a tap, not its start, as the gesture that may resume audio
    ['pointerdown', 'pointerup', 'touchend', 'keydown'].forEach(function (type) {
      document.addEventListener(type, unlock, { capture: true, passive: true });
    });
    document.addEventListener('visibilitychange', function () { if (document.hidden) stopAll(); });
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
    lastSound = Date.now();
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
    if (isEnabled()) seq.at = Date.now();   // the arpeggio is this moment's sound: the 7 s rule then blocks a later Zorp cue
    var notes = [523.25, 659.25, 783.99, 1046.5];
    playSequence(notes.map(function (freq, i) {
      return { freq: freq, dur: 100, type: 'sine', gain: 0.1, delay: i * 90 };
    }));
  }

  // E7 Phase 2: streak-of-3 "ding" — brighter/higher than playCorrect, not louder.
  function playDing() {
    playSequence([
      { freq: 987.77, dur: 90, type: 'sine', gain: 0.11, delay: 0 },
      { freq: 1318.51, dur: 130, type: 'sine', gain: 0.1, delay: 80 },
    ]);
  }

  // E7 Phase 2: gentler wrong-answer tone. Peak gain (0.08) is strictly below playWrong's (0.14).
  function playSoft() {
    playSequence([
      { freq: 261.63, dur: 140, type: 'sine', gain: 0.08, delay: 0 },
    ]);
  }

  function cueTone(audio, n, gain) {
    if (!bus) {
      bus = audio.createGain();
      bus.connect(audio.destination);
    }
    var t = audio.currentTime + n[4] / 1000;
    var end = t + n[3] / 1000;
    var osc = audio.createOscillator();
    var amp = audio.createGain();
    osc.type = n[0];
    osc.frequency.setValueAtTime(n[1], t);
    if (n[2] !== n[1]) osc.frequency.exponentialRampToValueAtTime(n[2], end);
    amp.gain.setValueAtTime(0.0001, t);
    amp.gain.exponentialRampToValueAtTime(gain, t + n[5] / 1000);
    amp.gain.exponentialRampToValueAtTime(0.0001, end);
    osc.connect(amp);
    amp.connect(bus);
    osc.start(t);
    osc.stop(end + 0.01);
  }

  // 3.4.3 rules 1 to 7. Called by the beat engine's start() (full motion, rule 5) and the styleguide ({ force } skips 1 and 7 only).
  function zorp(cue, o) {
    var notes = CUES[Object.prototype.hasOwnProperty.call(CUES, cue) ? cue : ''];
    var force = !!(o && o.force);
    var now = Date.now();
    if (!notes || !audioClass() || !(force || zorpMode() === 'celebrations')) return false;   // 1
    if (!awake(now)) return false;                                                       // 2, 3, 4
    var follow = cue === 'land' && seq.cue === 'jump' && lastSound === seq.cueAt && now - seq.cueAt < 1500;
    if (cue === 'land' && !follow && !force) return false;                               // a land belongs to its jump
    if (!follow && now - lastSound < ARBITER_MS) return false;                           // 6
    if (!follow && !force && now - seq.at < SEQ_MS) return false;                        // 7
    if (!follow) seq.at = now;
    seq.cue = cue;
    seq.cueAt = lastSound = now;
    ctxReady().then(function (audio) {
      if (audio) notes.forEach(function (n) { cueTone(audio, n, CUE_GAIN); });
    });
    return true;
  }

  // 3.4.4: true when a Zorp cue carries the moment, so burstConfetti stays silent.
  function cuesActive() {
    var z = window.pbZorp;
    return zorpMode() === 'celebrations' && !inQuiz() && !!z && typeof z.hasPose === 'function' && z.hasPose('stand') &&
      typeof z.motionLevel === 'function' && z.motionLevel() === 'full';
  }

  function hash(s) {
    var h = 0;
    for (var i = 0; i < s.length; i += 1) h = (h * 31 + s.charCodeAt(i)) | 0;
    return Math.abs(h);
  }

  // D7 voice blips (styleguide only): times = open frame ms, o.words = word start ms, seed = the line. Every second frame, at most
  // 6 a second and 12 a line, 520 to 680 Hz from a hash of the word, a question's last blip 15 percent higher.
  function blips(times, seed, o) {
    var force = !!(o && o.force);
    var now = Date.now();
    if (!times || !times.length || !audioClass() || !(force || zorpMode() === 'chatter')) return false;
    if (!awake(now)) return false;
    var text = String(seed || '');
    var ws = text.split(/\s+/).filter(Boolean);
    var starts = (o && o.words) || [];
    var picks = [];
    for (var i = 0; i < times.length && picks.length < 12; i += 2) {
      if (picks.length && times[i] - picks[picks.length - 1][0] < 167) continue;
      var k = 0;
      while (k < starts.length && starts[k] <= times[i]) k += 1;
      picks.push([times[i], 520 + hash(ws[Math.max(0, k - 1)] || '') % 161]);
    }
    if (/\?\s*$/.test(text)) picks[picks.length - 1][1] *= 1.15;
    ctxReady().then(function (audio) {
      if (audio) picks.forEach(function (p) { cueTone(audio, ['sine', p[1], p[1], 35, p[0], 5], BLIP_GAIN); });
    });
    return true;
  }

  function setEnabled(value) {
    var on = !!value;
    if (document.body) {
      document.body.setAttribute('data-sound-enabled', on ? '1' : '0');
    }
    if (on) bindUnlock();
  }

  bindUnlock();

  window.pbSound = {
    enabled: isEnabled,
    setEnabled: setEnabled,
    correct: playCorrect,
    wrong: playWrong,
    celebrate: playCelebrate,
    ding: playDing,
    soft: playSoft,
    preview: playCorrect,
    zorp: zorp,
    cuesActive: cuesActive,
    cued: function (ms) { return Date.now() - seq.cueAt <= ms; },   // a Zorp cue started in the last ms
    blips: blips,
    stopAll: stopAll,
    arm: function () { bindUnlock(true); },   // the styleguide records taps without either setting on
  };
})();
