/* Zorp's wardrobe (E10 phase 6b, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md section 11.10). Loaded on the profile page only. The panel
   (templates/partials/wardrobe.html) is native radio groups, so the keyboard works without this file; this file changes the preview
   Zorp when a choice changes (a small hop at full motion), saves through PATCH /api/v1/me/settings (the server checks every item
   against the pupil's badges), and puts the saved outfit on the page's own Zorps (the corner buddy and the guide rig, which the
   stages copy). Hats and shoes are cloned from the panel's inert <template>; no markup from data; transform and opacity only. */
(function () {
  'use strict';
  var D = document;
  var root = D.querySelector('[data-wardrobe]');
  if (!root) return;
  var SVGNS = 'http://www.w3.org/2000/svg';
  // BEGIN COPY
  var UI = {
    saved: 'Saved. I will wear this on every page.',
    failed: 'That did not save. Please try again.'
  };
  // END COPY
  var SLOTS = ['colour', 'antenna', 'feet', 'mouth', 'hat', 'shoes'];
  var ATTR = { colour: 'data-zorp-colour', antenna: 'data-zorp-antenna', feet: 'data-zorp-feet', mouth: 'data-mouth' };
  var host = root.querySelector('[data-wd-zorp]');
  var preview = host && host.querySelector('svg.buddy-mascot');
  var status = root.querySelector('[data-wd-status]');
  var art = root.querySelector('template[data-wd-art]');
  var RT = null;

  function Z() { return window.pbZorp || null; }
  function full() { var z = Z(); return !!(z && z.motionLevel && z.motionLevel() === 'full'); }
  function say(text) { if (status) status.textContent = text; }

  function draft() {
    var d = {};
    SLOTS.forEach(function (s) {
      var on = root.querySelector('[data-wd-slot="' + s + '"] input:checked');
      d[s] = on ? on.value : '';
    });
    return d;
  }

  function piece(id) {
    var src = art && art.content && art.content.querySelector('[data-art="' + id + '"]');
    return src && src.firstElementChild ? D.importNode(src.firstElementChild, true) : null;
  }
  function inst(svg) { return RT && RT.inst ? RT.inst({ el: svg }) : null; }

  // put a look on one rig: attributes, the hat, the shoes, the smile
  function wear(svg, look) {
    if (!svg) return;
    Object.keys(ATTR).forEach(function (k) {
      if (look[k]) svg.setAttribute(ATTR[k], look[k]); else svg.removeAttribute(ATTR[k]);
    });
    var head = svg.querySelector('.buddy-head');
    var ride = svg.querySelector('.zorp-hatride');
    var i = inst(svg);
    var hat = look.hat ? piece('hat.' + look.hat) : null;
    if (ride && !hat) {
      ride.parentNode.removeChild(ride);
      if (i && i.parts) i.parts.hatRide = null;
    } else if (hat && head) {
      if (!ride) {
        ride = D.createElementNS(SVGNS, 'g');
        ride.setAttribute('class', 'zorp-hatride');
        head.appendChild(ride);
        if (i && i.parts) i.parts.hatRide = ride;
      }
      while (ride.firstChild) ride.removeChild(ride.firstChild);
      ride.appendChild(hat);
    }
    ['l', 'r'].forEach(function (side) {
      var foot = svg.querySelector('.buddy-foot--' + side);
      if (!foot) return;
      Array.prototype.forEach.call(foot.querySelectorAll('.zorp-shoe'), function (n) { foot.removeChild(n); });
      var shoe = look.shoes ? piece('shoes.' + look.shoes + '.' + side) : null;
      if (shoe) foot.appendChild(shoe);
    });
    smile(svg, look);
  }

  // the resting smile (the nudge face only, as the live look does); redone after a clip, which puts back the smile it started with
  function smile(svg, look) {
    var z = Z();
    var h = svg && svg.closest('[data-buddy-face]');
    if (z && z.setExpression && z.channelsOf && h && (h.getAttribute('data-face') || 'nudge') === 'nudge') {
      var base = z.channelsOf('nudge');
      z.setExpression({ mouth: look.mouth || (base && base.mouth) }, { el: svg });
    }
  }

  function csrf() {
    var m = D.querySelector('meta[name="csrf-token"]');
    return m ? m.getAttribute('content') : '';
  }
  function patch(outfit) {
    var headers = { Accept: 'application/json', 'Content-Type': 'application/json' };
    var t = csrf();
    if (t) headers['X-CSRF-Token'] = t;
    return fetch(root.getAttribute('data-wd-api'), {
      method: 'PATCH', headers: headers, body: JSON.stringify({ zorp_outfit: outfit }), credentials: 'same-origin'
    }).then(function (r) { return r.json().then(function (j) { return r.ok && j && j.ok; }, function () { return false; }); });
  }

  function mark(chose) {
    root.setAttribute('data-wd-chose', chose ? '1' : '0');
    root.querySelector('[data-wd-note-auto]').hidden = chose;
    root.querySelector('[data-wd-note-saved]').hidden = !chose;
  }

  function onChange() {
    say('');
    wear(preview, draft());
    var z = Z();
    if (z && preview && full()) z.play('hop', { el: preview }).then(function () { smile(preview, draft()); });
  }

  function save() {
    var d = draft();
    patch(d).then(function (ok) {
      if (!ok) { say(UI.failed); return; }
      mark(true);
      say(UI.saved);
      Array.prototype.forEach.call(D.querySelectorAll('#study-buddy svg.buddy-mascot, [data-guide-face] svg.buddy-mascot'), function (svg) { wear(svg, d); });
    }).catch(function () { say(UI.failed); });
  }

  function reset() {
    patch(null).then(function (ok) {
      if (!ok) { say(UI.failed); return; }
      location.reload();   // the pages draw Zorp's own look again; the server decides which
    }).catch(function () { say(UI.failed); });
  }

  var z0 = Z();
  if (z0) {
    if (z0.register) z0.register(function (rt) { RT = rt; });
    if (host && z0.bind) z0.bind(host);
  }
  root.addEventListener('change', function (e) { if (e.target && e.target.name && e.target.name.indexOf('wd-') === 0) onChange(); });
  root.querySelector('[data-wd-save]').addEventListener('click', save);
  root.querySelector('[data-wd-reset]').addEventListener('click', reset);
}());
