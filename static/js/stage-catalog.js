/* Stage scenes (E10 phase 1 and 2, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A1 and section 10). Copy and choreography only:
   the runtime is static/js/zorp-stage.js, which loads this file with itself, only when a stage is about to play.
   UK English; every line follows docs/ZORP_CHARM.md section 3.3 (scripts/test_zorp_voice_smoke.py reads this file).
   A scene: id, heading, props (shown while it plays), layout, face (start) and end (positive or neutral, the face it ends
   on; scripts/test_zorp_stage_smoke.py checks both against models/zorp_rig.py CONTEXT_MAP['stage']), lines, and beats:
   one list per line, run when that line appears at full motion. Reduced motion shows each scene as a still frame (props
   in place, the end face) with a fade; off shows it with no fade. Beats:
     prop: show a prop (its entrance); prop + set: add a state to it (CSS); async: do not wait for it
     zorp: 'arrive' (float in from the top and land) | play: a clip (target, facing) | turn: a view (facing)
     face: a preset | crew: a clip for the crew | burst: the light burst | talk: mouth flaps for the line | wait: ms */
(function () {
  'use strict';

  window.pbStageCatalog = {
    // the arrival film: these five, then the welcome page adds scene 6 (the real level and topic choices)
    arrival: ['arrival.land', 'arrival.novara', 'arrival.mission', 'arrival.crew', 'arrival.help'],
    scenes: [
      {
        id: 'arrival.land',
        heading: 'Arrival',
        props: [],
        layout: 'centre',
        face: 'happy',
        end: 'grin',
        lines: [
          'Hi, I’m Zorp. I’m a maths and physics bot from a planet called Novara.',
        ],
        beats: [
          [{ prop: 'streak' }, { burst: 1 }, { zorp: 'arrive' }, { talk: 1 }, { play: 'wave' }],
        ],
        primary: 'Continue',
        skipLabel: 'Skip intro',
      },
      {
        id: 'arrival.novara',
        heading: 'Novara',
        props: ['planet'],
        layout: 'centre',
        face: 'happy',
        end: 'soft-smile',
        lines: [
          'On Novara, most things run on puzzles. Doors open when you solve them. Even the toaster.',
          'Out past it is the maths belt: a ring of rocks covered in numbers.',
        ],
        beats: [
          [{ prop: 'planet', async: 1 }, { wait: 450 }, { turn: 'side', facing: 'l' }, { talk: 1 }, { play: 'stage-gaze' }],
          [{ turn: 'front' }, { prop: 'planet', set: 'belt' }, { talk: 1 }, { play: 'think-chin' }],
        ],
        primary: 'Continue',
        skipLabel: 'Skip intro',
      },
      {
        id: 'arrival.mission',
        heading: 'The mission',
        props: ['planet', 'logbook'],
        layout: 'left',
        face: 'soft-smile',
        end: 'grin',
        lines: [
          'My crew and I came to Earth to learn how people here solve problems.',
          'I keep a logbook of what people here work out. When you reach something new, I cheer.',
        ],
        beats: [
          [{ prop: 'logbook' }, { talk: 1 }, { play: 'hop' }],
          [{ prop: 'logbook', set: 'open' }, { wait: 300 }, { play: 'side-point', target: 'down' }, { prop: 'logbook', set: 'notes' }, { talk: 1 }, { play: 'nod' }],
        ],
        primary: 'Continue',
        skipLabel: 'Skip intro',
      },
      {
        id: 'arrival.crew',
        heading: 'The crew',
        props: ['ship'],
        layout: 'centre',
        face: 'happy',
        end: 'grin',
        lines: [
          'That’s my crew on the ship. They’re keeping the engine warm.',
        ],
        beats: [
          [{ prop: 'ship' }, { crew: 'wave', async: 1 }, { turn: 'back-glance', facing: 'l' }, { wait: 900 }, { turn: 'front' }, { talk: 1 }, { play: 'wink' }],
        ],
        primary: 'Continue',
        skipLabel: 'Skip intro',
      },
      {
        id: 'arrival.help',
        heading: 'How I help',
        props: ['card'],
        layout: 'left',
        face: 'soft-smile',
        end: 'soft-smile',
        lines: [
          'Try a question first. If it goes wrong, I’ll show you a hint.',
          'I’m a bot, not a person. You can skip me any time.',
        ],
        beats: [
          [{ prop: 'card' }, { prop: 'card', set: 'try' }, { wait: 500 }, { prop: 'card', set: 'wrong' }, { wait: 500 }, { play: 'side-point' }, { prop: 'card', set: 'hint' }, { talk: 1 }],
          [{ prop: 'card', set: 'right' }, { play: 'hop' }, { talk: 1 }, { play: 'bow' }],
        ],
        primary: 'Continue',
        skipLabel: 'Skip intro',
        // the film without scene 6 (an account that never saw the old origin story) ends here
        story: {
          primary: 'Let’s go',
        },
      },
      {
        // scene 6: the page hands over its real forms (welcome.html) as the slot; the lines are the page's own
        id: 'arrival.choose',
        heading: 'Your turn',
        props: ['planet'],
        layout: 'choose',
        face: 'curious',
        end: 'soft-smile',
        slot: true,
        beats: [
          [{ play: 'think-chin' }],
        ],
      },
    ],
  };
})();
