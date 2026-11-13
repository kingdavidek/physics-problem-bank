/* Celebration sounds (docs/CELEBRATION_SOUNDS_PLAN.md section 2). A small library of named sounds, all made in code with WebAudio: tones,
   a noise burst made here (no files: nothing to license, download or cache, and it works offline). Loaded only when a celebration may
   sound, by sound.js (pbSound.play), which owns the rules (the setting, a recent tap, a visible page, no question page) and the audio
   context. Every sound goes into the shared output node, so pbSound.stopAll() cuts it. No peak is above 0.08, the gain of the quietest
   answer tone (`soft`). */
(function () {
  'use strict';
  var NOTE = { C5: 523.25, D5: 587.33, E5: 659.25, G5: 783.99, A5: 880, C6: 1046.5, E6: 1318.51, G6: 1567.98, A6: 1760, B6: 1975.53,
    C7: 2093, D7: 2349.32, E7: 2637.02 };

  // one tone: [wave, from Hz, to Hz, ms, delay ms, peak, attack ms]
  function tone(a, out, t0, s, k) {
    var t = t0 + s[4] / 1000;
    var end = t + s[3] / 1000;
    var osc = a.createOscillator();
    var amp = a.createGain();
    osc.type = s[0];
    osc.frequency.setValueAtTime(s[1], t);
    if (s[2] !== s[1]) osc.frequency.exponentialRampToValueAtTime(s[2], end);
    amp.gain.setValueAtTime(0.0001, t);
    amp.gain.exponentialRampToValueAtTime(Math.max(0.0002, s[5] * k), t + (s[6] || 10) / 1000);
    amp.gain.exponentialRampToValueAtTime(0.0001, end);
    osc.connect(amp);
    amp.connect(out);
    osc.start(t);
    osc.stop(end + 0.02);
  }

  // a burst of noise through a filter: [filter type, from Hz, to Hz, ms, delay ms, peak, attack ms, flutter (bursts, 0 for none)]
  var noiseBuf = null;
  function noise(a, out, t0, s, k) {
    if (!noiseBuf) {
      noiseBuf = a.createBuffer(1, Math.floor(a.sampleRate * 1.2), a.sampleRate);
      var d = noiseBuf.getChannelData(0);
      for (var i = 0; i < d.length; i += 1) d[i] = Math.random() * 2 - 1;
    }
    var t = t0 + s[4] / 1000;
    var end = t + s[3] / 1000;
    var src = a.createBufferSource();
    var f = a.createBiquadFilter();
    var amp = a.createGain();
    src.buffer = noiseBuf;
    f.type = s[0];
    f.Q.value = s[0] === 'bandpass' ? 1.4 : 0.7;
    f.frequency.setValueAtTime(s[1], t);
    if (s[2] !== s[1]) f.frequency.exponentialRampToValueAtTime(s[2], end);
    var peak = Math.max(0.0002, s[5] * k);
    amp.gain.setValueAtTime(0.0001, t);
    if (s[7]) {   // a light fizz: short puffs
      var step = (end - t) / s[7];
      for (var j = 0; j < s[7]; j += 1) {
        amp.gain.exponentialRampToValueAtTime(peak * (1 - j / (s[7] + 1)), t + j * step + 0.008);
        amp.gain.exponentialRampToValueAtTime(0.0003, t + (j + 1) * step);
      }
    } else {
      amp.gain.exponentialRampToValueAtTime(peak, t + (s[6] || 20) / 1000);
      amp.gain.exponentialRampToValueAtTime(0.0001, end);
    }
    src.connect(f);
    f.connect(amp);
    amp.connect(out);
    src.start(t);
    src.stop(end + 0.02);
  }

  var THUD = ['sine', 150, 70, 130, 0, 0.045, 4];
  // a chord's voices share its peak, so a chord is no louder than one note
  function chord(notes, ms, delay, peak, gap) {
    return notes.map(function (f, i) { return ['sine', f, f, ms, delay + i * (gap || 0), peak * 1.3 / notes.length, 8]; });
  }
  function pings(notes, delay, gap, peak) {
    return notes.map(function (f, i) { return ['sine', f, f, 130, delay + i * gap, peak, 4]; });
  }

  // name -> { t: tones, n: noise bursts }. `step` (Your week) picks one note.
  var SOUNDS = {
    whoosh: { n: [['bandpass', 380, 2600, 320, 0, 0.04, 140, 0]] },
    'stamp-bronze': { t: [THUD].concat(chord([392, 784], 520, 90, 0.05)) },
    'stamp-silver': { t: [THUD].concat(chord([NOTE.C5, NOTE.C6], 600, 90, 0.05), chord([NOTE.E5], 560, 150, 0.025)) },
    'stamp-gold': { t: [THUD].concat(chord([NOTE.C5, NOTE.E5, NOTE.G5], 720, 90, 0.06, 50), pings([NOTE.G6], 300, 0, 0.02)) },
    'stamp-violet': { t: [THUD].concat(chord([NOTE.C5, NOTE.E5, NOTE.G5, NOTE.C6], 860, 90, 0.06, 50), pings([NOTE.A6, NOTE.C7, NOTE.D7, NOTE.E7], 360, 60, 0.02)) },
    sparkle: { t: pings([NOTE.B6, NOTE.D7, NOTE.E7], 0, 90, 0.03) },
    confetti: { n: [['highpass', 3200, 5200, 360, 0, 0.03, 8, 6]] },
    gem: { t: [['sine', NOTE.E5, NOTE.E5, 220, 0, 0.06, 6], ['sine', NOTE.A5, NOTE.A5, 220, 90, 0.06, 6], ['sine', NOTE.C6, NOTE.C6, 220, 180, 0.065, 6],
      ['sine', NOTE.E6, NOTE.E6, 480, 270, 0.07, 6], ['triangle', NOTE.E6 * 2, NOTE.E6 * 2, 380, 280, 0.015, 6]] },
    level: { t: pings([NOTE.C5, NOTE.D5, NOTE.E5, NOTE.G5], 0, 85, 0.045).concat(chord([NOTE.C5, NOTE.E5, NOTE.G5, NOTE.C6], 600, 1100, 0.07, 30)) },
    book: { t: [['triangle', 220, 110, 100, 0, 0.06, 4], ['sine', NOTE.A5, NOTE.A5, 240, 450, 0.05, 6], ['sine', NOTE.E6, NOTE.E6, 260, 520, 0.045, 6]] },
    sprout: { t: [['sine', 330, 880, 460, 0, 0.05, 30], ['sine', NOTE.E6, NOTE.E6, 200, 440, 0.03, 4]] },
    fire: { n: [['lowpass', 500, 1200, 700, 0, 0.05, 300, 0]], t: [['sine', 110, 110, 650, 0, 0.03, 200]] },
    week: { steps: [NOTE.C5, NOTE.E5, NOTE.G5] },
    story: { t: [['triangle', NOTE.E6, NOTE.E6, 220, 0, 0.04, 4], ['triangle', NOTE.G6, NOTE.G6, 220, 150, 0.04, 4], ['triangle', NOTE.C7, NOTE.C7, 220, 300, 0.04, 4],
      ['triangle', NOTE.B6, NOTE.B6, 220, 450, 0.04, 4], ['triangle', NOTE.G6, NOTE.G6, 420, 600, 0.04, 4]] },
    pop: { t: [['sine', 600, 900, 70, 0, 0.03, 4]] }
  };

  function parts(name, o) {
    var def = SOUNDS[name];
    if (!def) return null;
    if (def.steps) {
      var f = def.steps[Math.max(0, Math.min(def.steps.length - 1, (o && o.step) || 0))];
      return { t: [['sine', f, f, 260, 0, 0.05, 8], ['sine', f * 2, f * 2, 200, 0, 0.012, 8]], n: [] };
    }
    return { t: def.t || [], n: def.n || [] };
  }

  // how long a sound lasts, its loudest single voice, and its loudest moment: the sum of the peaks of every voice sounding at once,
  // a cautious upper bound (each voice decays from its peak). The tests read these.
  function meta(name) {
    var p = parts(name, { step: 2 });
    if (!p) return null;
    var all = p.t.concat(p.n);
    var ms = Math.max.apply(null, all.map(function (s) { return s[3] + s[4]; }));
    var loud = 0;
    for (var t = 0; t <= ms; t += 5) {
      var sum = 0;
      all.forEach(function (s) { if (t >= s[4] && t < s[4] + Math.max(60, s[3] * 0.35)) sum += s[5]; });
      loud = Math.max(loud, sum);
    }
    return { ms: ms, peak: Math.max.apply(null, all.map(function (s) { return s[5]; })), loud: Math.round(loud * 1000) / 1000 };
  }

  // play `name` into `out` now; k scales the gain (soft: 0.6). Returns false for an unknown name.
  function play(name, audio, out, k, o) {
    var p = parts(name, o);
    if (!p || !audio || !out) return false;
    var t0 = audio.currentTime + 0.01;
    p.t.forEach(function (s) { tone(audio, out, t0, s, k || 1); });
    p.n.forEach(function (s) { noise(audio, out, t0, s, k || 1); });
    return true;
  }

  window.pbSoundLib = { names: Object.keys(SOUNDS), meta: meta, play: play };
}());
