const STORE_KEY = 'do_wk_v2';
const BLOCK_KEY = 'do_wk_block_v2';

const BLOCKS = {
  1: [
    {
      name: 'Day 1 — Heavy strength',
      shortName: 'Heavy Strength',
      badge: 'Strength', badgeClass: 'badge-str',
      exercises: [
        { name: 'Movement Prep', sets: 1, reps: '10 min', load: '—', pattern: 'mobility', emoji: '🔄',
          muscles: 'Hip flexors, T-spine, Shoulders',
          desc: 'Hip flexor stretch 60s each side, thoracic spine rotations on foam roller, shoulder CARs — full slow circles through complete shoulder range. Non-negotiable given shoulder history.' },
        { name: 'Trap Bar Deadlift', sets: 4, reps: '4–5', load: '~240 lbs, +10/wk', pattern: 'hip hinge', emoji: '🏋️',
          muscles: 'Primary: Glutes, Hamstrings, Quads · Secondary: Erectors, Traps',
          desc: 'Stand center of trap bar. Hinge at hips, neutral spine, chest up. Drive through the floor — push the floor away. Lock out hips at the top. Preferred over conventional: better for 6\'3" frame, protects left foot under heavy load.',
          tip: 'Target: add 10 lbs per week for the first 4 weeks. Week 1: 240, Week 2: 250, Week 3: 260, Week 4: 270.' },
        { name: 'Goblet Squat', sets: 3, reps: '6–8', load: 'Moderate KB', pattern: 'squat', emoji: '🔔',
          muscles: 'Primary: Quads, Glutes · Secondary: Core, Upper back',
          desc: 'KB at chest, elbows inside knees at bottom. Sit back and down — not just down. Drive knees out. Full depth as mobility allows. Builds squat pattern safely while monitoring ACL tracking.' },
        { name: 'Chest-Supported DB Row', sets: 3, reps: '8–10', load: 'Moderate DB', pattern: 'horizontal pull', emoji: '🏋️',
          muscles: 'Primary: Mid traps, Rhomboids, Lats · Secondary: Rear delts, Biceps',
          desc: 'Incline bench ~45°. Chest on pad, feet on floor. Row both DBs to hips — lead with elbows. Pause 1 second at top. Chest support eliminates lower back involvement and is safe for both shoulder repairs.' },
        { name: 'Single-Leg RDL', sets: 3, reps: '8 each side', load: 'Light DB or bodyweight', pattern: 'unilateral', emoji: '🦵',
          muscles: 'Primary: Hamstrings, Glutes · Secondary: Balance, Hip stabilizers',
          desc: 'Stand on one leg. Hinge forward flat back, free leg extends behind. Touch DB to floor or shin. Feel stretch in standing hamstring. Addresses left/right DEXA asymmetry. Start bodyweight — balance is the challenge.' },
        { name: 'Rowing Ergometer', sets: 1, reps: '10 min', load: 'Easy pace', pattern: 'conditioning', emoji: '🚣',
          muscles: 'Primary: Lats, Rhomboids, Hamstrings · Secondary: Quads, Core',
          desc: 'Legs to hips to arms on the drive. Arms to hips to legs on recovery. 22–24 strokes/min, easy effort. Zero foot impact — ideal given Jones fracture history.' }
      ]
    },
    {
      name: 'Day 2 — Moderate hypertrophy',
      shortName: 'Hypertrophy',
      badge: 'Hypertrophy', badgeClass: 'badge-hyp',
      exercises: [
        { name: 'Movement Prep', sets: 1, reps: '10 min', load: '—', pattern: 'mobility', emoji: '🔄',
          muscles: 'Hip flexors, T-spine, Shoulders',
          desc: 'Hip flexor stretch 60s each side, thoracic spine rotations, shoulder CARs. Same as Day 1 — always do this before loading.' },
        { name: 'Landmine Press', sets: 3, reps: '10–12 each', load: 'Moderate plate', pattern: 'horizontal push', emoji: '💪',
          muscles: 'Primary: Anterior delt, Upper chest · Secondary: Triceps, Serratus',
          desc: 'Anchor barbell in corner or landmine. Press from shoulder height at ~45°. Neutral grip arc — the key shoulder-safe pressing variation. Takes shoulder out of impingement zone. Split stance for stability.' },
        { name: 'Bulgarian Split Squat', sets: 3, reps: '10 each side', load: 'Bodyweight to DB', pattern: 'unilateral', emoji: '🦵',
          muscles: 'Primary: Quads, Glutes · Secondary: Hamstrings, Hip flexors',
          desc: 'Rear foot on bench, front foot 2–3 feet forward. Lower until front thigh parallel. Front shin vertical. Directly addresses left/right leg asymmetry from DEXA. ACL-safe.' },
        { name: 'Eccentric Pull-Up / Cable Pulldown', sets: 3, reps: '5–6 eccentric OR 10–12 pulldown', load: 'Bodyweight / Moderate stack', pattern: 'vertical pull', emoji: '🏋️',
          muscles: 'Primary: Lats, Teres major · Secondary: Biceps, Rear delts',
          desc: 'ECCENTRIC: Stand on box, neutral grip. Jump to top — chin over bar. Lower under control for 4–6 seconds to dead hang. You are 20–30% stronger eccentrically — this is how you build to full pull-ups. PULLDOWN: Neutral grip V-bar, pull to upper chest, lead elbows down and back. Alternate between eccentric pull-ups and pulldowns across different sessions.',
          tip: 'Goal: bodyweight pull-up. Grip strength is a top longevity predictor (Lancet 2015). Eccentric-only builds the strength base faster than assisted pull-ups.', isNew: true },
        { name: 'Incline DB Press', sets: 3, reps: '10–12', load: 'Moderate DB', pattern: 'horizontal push', emoji: '💪',
          muscles: 'Primary: Upper chest, Anterior delt · Secondary: Triceps',
          desc: 'Bench at 30–45°. Feet flat. Elbows at ~45° from torso — not 90°. Full range. Stop if you feel shoulder impingement — reduce range or angle.' },
        { name: 'Face Pull / Band Pull-Apart Superset', sets: 3, reps: '15–20 each', load: 'Light cable / band', pattern: 'rotator cuff', emoji: '🎯',
          muscles: 'Primary: Rear delts, External rotators · Secondary: Mid traps, Rhomboids',
          desc: 'Face pull: cable at face height, rope attachment, pull to forehead with external rotation — show your biceps at end. Immediately follow with band pull-apart: arms straight, pull to chest width. Protects both shoulder repairs over time. Never skip.' },
        { name: 'Half-Kneeling Pallof Press', sets: 3, reps: '8–10 each side', load: 'Light cable', pattern: 'anti-rotation core', emoji: '🎯',
          muscles: 'Primary: Obliques, Deep core · Secondary: Glutes, Hip stabilizers',
          desc: 'Half-kneeling perpendicular to cable, inside knee down. Cable at chest height. Press straight out and hold 2 seconds — resist rotation the entire time. The goal is NOT to rotate. Pull back in. Anti-rotation work is the missing piece for long-term spine health.',
          tip: 'New to program — from the Evernote archive. Anti-rotation training protects the lumbar spine and improves transfer to deadlift and carry patterns.', isNew: true },
        { name: 'Farmer Carry', sets: 3, reps: '35 meters', load: '~50 lbs/hand to start', pattern: 'loaded carry', emoji: '💼',
          muscles: 'Primary: Grip, Traps, Core · Secondary: Glutes, Quads',
          desc: 'Two KBs, stand tall, walk controlled line. Head up, shoulders packed. Strong grip throughout. Conservative load given left foot history — drop if any foot discomfort.' },
        { name: 'Rowing Ergometer', sets: 1, reps: '10 min', load: 'Moderate pace', pattern: 'conditioning', emoji: '🚣',
          muscles: 'Full body — posterior chain dominant',
          desc: '24–26 strokes/min, moderate effort. Should be able to hold a broken conversation.' }
      ]
    },
    {
      name: 'Day 3 — Power/metabolic',
      shortName: 'Power & Metabolic',
      badge: 'Metabolic', badgeClass: 'badge-met',
      exercises: [
        { name: 'Movement Prep', sets: 1, reps: '5 min', load: '—', pattern: 'mobility', emoji: '🔄',
          muscles: 'Hip flexors, Glutes, Shoulders',
          desc: 'Hip circles, leg swings, arm circles. Shorter prep for the metabolic session — get blood moving.' },
        { name: 'KB Swing', sets: 5, reps: '10', load: '35–53 lbs KB', pattern: 'hip hinge power', emoji: '🏋️',
          muscles: 'Primary: Glutes, Hamstrings · Secondary: Core, Lats',
          desc: 'Hip hinge — not a squat. Drive hips forward explosively to float the bell to chest height. Hike it back between legs, load the hips. Speed and hip drive matter more than load. Stand on both feet — protects left foot.' },
        { name: 'Sled Push', sets: 4, reps: '20 meters', load: 'Moderate — start light', pattern: 'metabolic', emoji: '🛷',
          muscles: 'Primary: Quads, Glutes, Calves · Secondary: Core, Shoulders',
          desc: 'Lean into sled ~45°, drive through floor with short powerful steps. No eccentric load — best recovery cost-benefit ratio of any exercise. Best tool for VAT reduction alongside Zone 2 cardio.' },
        { name: 'Step-Up', sets: 3, reps: '10 each side', load: 'Bodyweight to DB', pattern: 'unilateral', emoji: '🪜',
          muscles: 'Primary: Glutes, Quads · Secondary: Hamstrings, Balance',
          desc: 'Box or bench ~16". Step up, drive through heel of top foot — don\'t push off back foot. Stand fully at top. Step down controlled. ACL and foot-friendly.' },
        { name: 'TRX Row', sets: 3, reps: '12', load: 'Body angle', pattern: 'horizontal pull', emoji: '🏋️',
          muscles: 'Primary: Mid traps, Rhomboids, Rear delts · Secondary: Biceps',
          desc: 'Lean back, straight body. Pull chest to hands — elbows back, shoulder blades squeeze. More horizontal = harder. Good posterior chain finisher.' },
        { name: 'Rowing Ergometer Intervals', sets: 3, reps: '4 min on / 2 min off', load: 'Zone 2', pattern: 'conditioning', emoji: '🚣',
          muscles: 'Full body',
          desc: 'Zone 2: can talk but would rather not. ~65–75% max HR. Primary VAT burner. Three 4-minute intervals beats one long cruise.' }
      ]
    }
  ],
  2: [
    {
      name: 'Day 1 — Heavy strength (Block 2)',
      shortName: 'Heavy Strength B2',
      badge: 'Strength', badgeClass: 'badge-str',
      exercises: [
        { name: 'Movement Prep', sets: 1, reps: '10 min', load: '—', pattern: 'mobility', emoji: '🔄',
          muscles: 'Hip flexors, T-spine, Shoulders',
          desc: 'Same as Block 1. Hip flexor stretch, thoracic rotations, shoulder CARs.' },
        { name: 'Romanian Deadlift (Barbell)', sets: 4, reps: '5–6', load: 'Moderate barbell, +10/wk', pattern: 'hip hinge', emoji: '🏋️',
          muscles: 'Primary: Hamstrings, Glutes · Secondary: Erectors, Traps',
          desc: 'Barbell from rack or floor. Hinge to just below the knee — feel the hamstring stretch. Drive hips forward to lockout. Greater hamstring emphasis than trap bar, more hip mobility demand. Keep shins nearly vertical.',
          tip: 'Block 2 swap for trap bar deadlift. Same hip hinge pattern, different loading arc.' },
        { name: 'Safety Bar Squat or Heel-Elevated Goblet Squat', sets: 3, reps: '6–8', load: 'Moderate', pattern: 'squat', emoji: '🔔',
          muscles: 'Primary: Quads, Glutes · Secondary: Core',
          desc: 'Safety bar: more upright torso than back squat, easier on shoulders. Heel-elevated goblet: 1–2 inch plates under heels, dramatically improves depth and quad emphasis. Choose based on what the gym has.',
          tip: 'Heel elevation is a plateau-breaker for quad development when mobility limits goblet squat depth.' },
        { name: 'Barbell Row (Pendlay Style)', sets: 3, reps: '6–8', load: 'Moderate barbell', pattern: 'horizontal pull', emoji: '🏋️',
          muscles: 'Primary: Lats, Mid traps, Rhomboids · Secondary: Erectors, Biceps',
          desc: 'Bar on floor each rep. Hinge to near-horizontal back. Pull bar to lower chest — elbows close. Reset to floor. The full stop eliminates momentum. More total back development than chest-supported row.',
          tip: 'Block 2 swap for chest-supported row. Monitor lower back — if fatigue affects form, drop to chest-supported.' },
        { name: 'Reverse Lunge', sets: 3, reps: '8–10 each side', load: 'DB or KB', pattern: 'unilateral', emoji: '🦵',
          muscles: 'Primary: Glutes, Quads · Secondary: Hamstrings, Balance',
          desc: 'Step back — not forward. Rear knee drops to just above floor. Front shin stays vertical. ACL-safer than forward lunge and easier on the Jones fracture side.',
          tip: 'Block 2 swap for single-leg RDL. Alternates unilateral pattern.' },
        { name: 'Rowing Ergometer', sets: 1, reps: '10 min', load: 'Easy–Moderate', pattern: 'conditioning', emoji: '🚣',
          muscles: 'Full body, posterior chain dominant',
          desc: '22–26 strokes/min. Push a bit harder than Block 1.' }
      ]
    },
    {
      name: 'Day 2 — Moderate hypertrophy (Block 2)',
      shortName: 'Hypertrophy B2',
      badge: 'Hypertrophy', badgeClass: 'badge-hyp',
      exercises: [
        { name: 'Movement Prep', sets: 1, reps: '10 min', load: '—', pattern: 'mobility', emoji: '🔄',
          muscles: 'Hip flexors, T-spine, Shoulders',
          desc: 'Same as Block 1.' },
        { name: 'Dumbbell Z-Press', sets: 3, reps: '8–10 each', load: 'Light–Moderate DB', pattern: 'overhead push', emoji: '💪',
          muscles: 'Primary: Anterior delt, Triceps · Secondary: Core, Serratus',
          desc: 'Sit on floor, legs straight out. Press DBs overhead from shoulder height. Floor position eliminates leg drive, forces true shoulder strength. Neutral or slight pronation grip — don\'t fully lock out if you feel impingement.',
          tip: 'Block 2 swap for landmine press. Lower weight is expected and correct.' },
        { name: 'Walking Lunge', sets: 3, reps: '10 each side', load: 'DB or bodyweight', pattern: 'unilateral', emoji: '🦵',
          muscles: 'Primary: Quads, Glutes · Secondary: Hamstrings, Balance',
          desc: 'Step forward into lunge, drive through front heel to standing, step through into next lunge. Keep torso upright. Monitor left foot on impact — reduce load if any discomfort.' },
        { name: 'Weighted Pull-Up or Eccentric Pull-Up', sets: 3, reps: '4–6 or 5 eccentric', load: 'Bodyweight or added weight', pattern: 'vertical pull', emoji: '🏋️',
          muscles: 'Primary: Lats, Teres major · Secondary: Biceps, Rear delts',
          desc: 'Block 2 progression from Block 1 eccentric protocol. If you can do 3–4 bodyweight reps, do those then switch to eccentric for remaining sets. If not, continue eccentric-only 5-second lowering.',
          tip: 'Goal by week 8: at least one clean bodyweight neutral-grip pull-up.' },
        { name: 'Cable Fly', sets: 3, reps: '12–15', load: 'Light cable', pattern: 'chest isolation', emoji: '💪',
          muscles: 'Primary: Pectorals · Secondary: Anterior delt',
          desc: 'Cables at shoulder height. Step forward, slight lean. Bring handles together in front of chest — slight elbow bend, don\'t lock. Slow on the way back.' },
        { name: 'Half-Kneeling Face Pull', sets: 3, reps: '12–15', load: 'Light cable', pattern: 'rotator cuff', emoji: '🎯',
          muscles: 'Primary: Rear delts, External rotators · Secondary: Mid traps',
          desc: 'Half-kneeling facing cable. Pull rope to face with external rotation — elbows high, show your biceps at end. Half-kneeling increases core and glute demand vs. standing.',
          isNew: true },
        { name: 'Pallof Press (Standing)', sets: 3, reps: '10 each side', load: 'Light–Moderate cable', pattern: 'anti-rotation core', emoji: '🎯',
          muscles: 'Primary: Obliques, Transverse abdominis · Secondary: Glutes',
          desc: 'Stand perpendicular to cable, feet shoulder width. Press cable straight out from chest, hold 2 seconds, return. Standing version increases demand vs. half-kneeling Block 1 version.' },
        { name: 'Suitcase Carry', sets: 3, reps: '35 meters each side', load: '~50–60 lbs KB', pattern: 'loaded carry', emoji: '💼',
          muscles: 'Primary: Obliques, Grip, Traps · Secondary: Glutes, Core',
          desc: 'Single KB in one hand, walk tall. Unilateral load drives lateral core anti-flexion. Harder than farmer carry for core demand.',
          tip: 'Block 2 swap for bilateral farmer carry. Builds lateral spine stiffness that protects against falls.' },
        { name: 'Rowing Ergometer', sets: 1, reps: '10 min', load: 'Moderate–Hard', pattern: 'conditioning', emoji: '🚣',
          muscles: 'Full body',
          desc: '26–28 strokes/min. Push the effort up a notch from Block 1.' }
      ]
    },
    {
      name: 'Day 3 — KB Conditioner (Block 2)',
      shortName: 'KB Conditioner',
      badge: 'KB Circuit', badgeClass: 'badge-kb',
      exercises: [
        { name: 'Movement Prep', sets: 1, reps: '5 min', load: '—', pattern: 'mobility', emoji: '🔄',
          muscles: 'Hip flexors, Glutes, Shoulders',
          desc: 'Hip circles, leg swings, arm circles, shoulder rolls. Quick prep for the KB circuit.' },
        { name: 'One-Arm KB Clean', sets: 4, reps: '10–12 each side', load: 'Moderate KB', pattern: 'power', emoji: '🏋️',
          muscles: 'Primary: Glutes, Traps, Forearm · Secondary: Core, Lats',
          desc: 'KB between feet, hinge. Drive hips — punch the KB up and catch in rack position (KB resting on forearm, elbow tucked). Power comes from hip drive, not your arm. From your Evernote KB Conditioner archive.',
          tip: 'From your Evernote KB Conditioner archive — proven pattern from your earlier training.' },
        { name: 'Double-Arm KB Front Swing', sets: 4, reps: '12–15', load: 'Moderate KB', pattern: 'hip hinge power', emoji: '🏋️',
          muscles: 'Primary: Glutes, Hamstrings · Secondary: Core, Lats',
          desc: 'Both hands on KB. Same hip-hinge drive as single-arm swing — but double handle gives more control and allows a heavier bell. Float to chest height, load the hips on the backswing.' },
        { name: 'Goblet Squat (KB)', sets: 4, reps: '10–12', load: 'Moderate–Heavy KB', pattern: 'squat', emoji: '🔔',
          muscles: 'Primary: Quads, Glutes · Secondary: Core, Upper back',
          desc: 'KB at chest, elbows inside knees at bottom. Same pattern as Block 1 Day 1 — in circuit context, focus on speed and depth, not max strength.' },
        { name: 'One-Arm KB Overhead Press', sets: 3, reps: '8–10 each side', load: 'Light–Moderate KB', pattern: 'overhead push', emoji: '💪',
          muscles: 'Primary: Deltoids, Triceps · Secondary: Core, Rotator cuff',
          desc: 'KB in rack position. Press straight overhead — full lockout if shoulder allows. KB wrist rotation is more shoulder-friendly than barbell. Monitor both shoulders — reduce load at any sign of impingement.',
          tip: 'Watch the shoulder repairs carefully. Light weight, perfect form, full range only if pain-free.' },
        { name: 'Reverse Lunge (KB Contralateral)', sets: 3, reps: '10 each side', load: 'Moderate KB', pattern: 'unilateral', emoji: '🦵',
          muscles: 'Primary: Glutes, Quads · Secondary: Hamstrings, Core',
          desc: 'Hold KB in opposite hand to the stepping leg (right leg steps back = KB in left hand). Contralateral load increases core demand significantly. From the KB Conditioner archive.' },
        { name: 'Rowing Ergometer Intervals', sets: 3, reps: '4 min on / 2 min off', load: 'Zone 2–3', pattern: 'conditioning', emoji: '🚣',
          muscles: 'Full body',
          desc: 'Push into low Zone 3 by Block 2 — ~70–80% max HR. Should feel harder to talk but not gasping.' }
      ]
    }
  ]
};

var wakeLock = null;
var currentBlock = parseInt(localStorage.getItem(BLOCK_KEY) || '1');
var workoutStarted = false;
var workoutFinished = false;
var workoutStartTime = Date.now();
var currentExIdx = 0;
var setStates = {};
var completedExercises = new Set();
var restTimer = null;
var restSeconds = 0;

function getData() { try { return JSON.parse(localStorage.getItem(STORE_KEY)) || []; } catch(e) { return []; } }
function saveData(d) { try { localStorage.setItem(STORE_KEY, JSON.stringify(d)); } catch(e) {} }
function getNextDayIdx() {
  var data = getData();
  if (!data.length) return 0;
  return (data[0].dayIdx + 1) % 3;
}
function currentDays() { return BLOCKS[currentBlock]; }

function requestWakeLock() {
  try {
    if ('wakeLock' in navigator) {
      navigator.wakeLock.request('screen').then(function(lock) { wakeLock = lock; }).catch(function() {});
    }
  } catch(e) {}
}
requestWakeLock();
document.addEventListener('visibilitychange', function() { if (document.visibilityState === 'visible') requestWakeLock(); });

function switchTab(name) {
  document.querySelectorAll('.screen').forEach(function(s) { s.classList.remove('active'); });
  document.querySelectorAll('.nav-tab').forEach(function(t) { t.classList.remove('active'); });
  document.getElementById('screen-' + name).classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
  if (name === 'log') renderLog();
  if (name === 'queue') renderQueue();
  if (name === 'workout') renderWorkout();
}

function setBlock(n) {
  currentBlock = n;
  localStorage.setItem(BLOCK_KEY, n);
  workoutStarted = false;
  workoutFinished = false;
  renderWorkout();
}

function blockToggleHtml() {
  return '<div class="block-toggle">' +
    '<button class="block-btn ' + (currentBlock===1?'active':'') + '" onclick="setBlock(1)">Block 1 — Jun/Jul</button>' +
    '<button class="block-btn ' + (currentBlock===2?'active':'') + '" onclick="setBlock(2)">Block 2 — Aug/Sep</button>' +
    '</div>';
}

function initWorkout() {
  var dayIdx = getNextDayIdx();
  currentExIdx = 0;
  setStates = {};
  completedExercises = new Set();
  workoutStarted = true;
  workoutFinished = false;
  workoutStartTime = Date.now();
  var day = currentDays()[dayIdx];
  day.exercises.forEach(function(ex, i) {
    var rows = [];
    for (var s = 0; s < Math.max(ex.sets, 1); s++) rows.push({ load: '', repsLogged: '', done: false });
    setStates[i] = rows;
  });
  renderWorkout();
}

function renderWorkout() {
  var dayIdx = getNextDayIdx();
  var day = currentDays()[dayIdx];
  var screen = document.getElementById('screen-workout');

  if (!workoutStarted) {
    var exRows = day.exercises.map(function(ex) {
      return '<div class="start-ex-row">' +
        '<div class="start-ex-emoji">' + ex.emoji + '</div>' +
        '<div><div class="start-ex-name">' + ex.name + (ex.isNew ? ' <span class="new-pill">NEW</span>' : '') + '</div>' +
        '<div class="start-ex-meta">' + (ex.sets === 1 ? ex.reps : ex.sets + ' x ' + ex.reps) + ' · ' + ex.pattern + '</div></div>' +
        '</div>';
    }).join('');
    screen.innerHTML = blockToggleHtml() +
      '<div class="day-header"><div><div class="day-title">' + day.shortName + '</div>' +
      '<div class="day-subtitle">' + day.exercises.length + ' exercises · Block ' + currentBlock + '</div></div>' +
      '<span class="day-badge ' + day.badgeClass + '">' + day.badge + '</span></div>' +
      '<div class="start-ex-list">' + exRows + '</div>' +
      '<button class="save-btn" onclick="initWorkout()">▶  Start Workout</button>';
    return;
  }

  if (workoutFinished) {
    var dur = Math.round((Date.now() - workoutStartTime) / 60000);
    screen.innerHTML = '<div class="complete-banner"><h2>✓ Workout done</h2>' +
      '<p>' + day.shortName + ' · ' + dur + ' min · ' + completedExercises.size + '/' + day.exercises.length + ' exercises</p></div>' +
      '<button class="save-btn" onclick="saveAndFinish(' + dayIdx + ')">Save and finish</button>' +
      '<button class="save-btn" style="background:var(--gray5);color:var(--gray1);" onclick="workoutFinished=false;renderWorkout()">Back to review</button>';
    return;
  }

  var nextEx = day.exercises[currentExIdx + 1];
  var nextBar = nextEx ? '<div class="next-up-bar">&#8594; Up next: <strong>' + nextEx.name + '</strong> · ' + (nextEx.sets === 1 ? nextEx.reps : nextEx.sets + 'x' + nextEx.reps) + '</div>' : '';
  screen.innerHTML = '<div class="day-header"><div><div class="day-title">' + day.shortName + '</div>' +
    '<div class="day-subtitle">' + completedExercises.size + '/' + day.exercises.length + ' done</div></div>' +
    '<span class="day-badge ' + day.badgeClass + '">' + day.badge + '</span></div>' +
    nextBar +
    day.exercises.map(function(ex, i) { return renderExCard(ex, i); }).join('') +
    '<div style="height:20px;"></div>';

  setTimeout(function() {
    var cards = document.querySelectorAll('.ex-card');
    if (cards[currentExIdx]) cards[currentExIdx].scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 80);
}

function renderExCard(ex, i) {
  var isDone = completedExercises.has(i);
  var isCurrent = i === currentExIdx;
  var sets = setStates[i] || [];

  var setRowsHtml = '';
  if (ex.sets > 1) {
    var rows = sets.map(function(s, si) {
      return '<div class="set-row">' +
        '<span class="set-num">Set ' + (si+1) + '</span>' +
        '<input class="set-input" type="number" inputmode="decimal" placeholder="lbs" value="' + (s.load||'') + '" onchange="updateSetLoad(' + i + ',' + si + ',this.value)" style="max-width:75px;">' +
        '<span class="set-sep">x</span>' +
        '<input class="set-input" type="number" inputmode="numeric" placeholder="reps" value="' + (s.repsLogged||'') + '" onchange="updateSetReps(' + i + ',' + si + ',this.value)" style="max-width:65px;">' +
        '<button class="set-check ' + (s.done?'done':'') + '" onclick="toggleSet(' + i + ',' + si + ')">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="' + (s.done?'white':'#dadce0') + '" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></button>' +
        '</div>';
    }).join('');
    setRowsHtml = '<div class="set-tracker"><div class="set-tracker-label">Track your sets</div><div class="set-rows">' + rows + '</div></div>';
  }

  var restHtml = (restTimer !== null && isCurrent) ?
    '<div class="rest-bar"><span class="rest-label">Rest</span><span class="rest-timer" id="rest-display">' + formatTime(restSeconds) + '</span><button class="rest-skip" onclick="stopRest()">Skip</button></div>' : '';

  var innerHtml = '';
  if (isCurrent || isDone) {
    innerHtml = '<div class="ex-desc">' + ex.desc + '</div>' +
      '<div class="ex-muscles">Muscles: <span>' + ex.muscles + '</span></div>' +
      (ex.tip ? '<div class="ex-tip">' + ex.tip + '</div>' : '') +
      setRowsHtml + restHtml +
      (!isDone ? '<button class="ex-done-btn" onclick="markExDone(' + i + ')">Mark complete</button>' : '');
  }

  return '<div class="ex-card' + (isDone?' completed-card':'') + (ex.isNew?' alt-card':'') + '" id="ex-card-' + i + '">' +
    '<div class="ex-card-header">' +
    '<div class="ex-icon">' + ex.emoji + '</div>' +
    '<div class="ex-info">' +
    '<div class="ex-name">' + (isDone?'✓ ':'') + ex.name + '</div>' +
    '<div class="ex-meta">' + (ex.sets===1?ex.reps:ex.sets+' sets x '+ex.reps) + ' · ' + ex.load + '</div>' +
    '<div class="ex-tags"><span class="ex-tag">' + ex.pattern + '</span>' + (ex.isNew?'<span class="ex-tag new-tag">new this block</span>':'') + '</div>' +
    '</div></div>' + innerHtml + '</div>';
}

function updateSetLoad(i, si, v) { setStates[i][si].load = v; }
function updateSetReps(i, si, v) { setStates[i][si].repsLogged = v; }
function toggleSet(i, si) { setStates[i][si].done = !setStates[i][si].done; renderWorkout(); }

function markExDone(i) {
  completedExercises.add(i);
  var day = currentDays()[getNextDayIdx()];
  if (i < day.exercises.length - 1) { currentExIdx = i + 1; startRest(90); }
  else workoutFinished = true;
  renderWorkout();
}

function startRest(s) {
  if (restTimer) clearInterval(restTimer);
  restSeconds = s;
  restTimer = setInterval(function() {
    restSeconds--;
    var el = document.getElementById('rest-display');
    if (el) el.textContent = formatTime(restSeconds);
    if (restSeconds <= 0) stopRest();
  }, 1000);
}
function stopRest() { if (restTimer) clearInterval(restTimer); restTimer = null; renderWorkout(); }
function formatTime(s) { return Math.floor(s/60) + ':' + String(s%60).padStart(2,'0'); }

function saveAndFinish(dayIdx) {
  var day = currentDays()[dayIdx];
  var dur = Math.round((Date.now() - workoutStartTime) / 60000);
  var setLog = {};
  day.exercises.forEach(function(ex, i) { setLog[ex.name] = setStates[i]; });
  var data = getData();
  data.unshift({ id: Date.now(), date: new Date().toLocaleDateString('en-CA'), dayIdx: dayIdx, block: currentBlock, dayName: day.name, duration: dur, completed: completedExercises.size, total: day.exercises.length, setLog: setLog });
  saveData(data);
  workoutStarted = false;
  workoutFinished = false;
  renderWorkout();
  renderQueue();
}

function renderQueue() {
  var nextIdx = getNextDayIdx();
  var data = getData();
  var dayCounts = [0,0,0];
  data.forEach(function(d) { if (d.dayIdx !== undefined) dayCounts[d.dayIdx]++; });
  var thisMonth = data.filter(function(d) { return d.date && d.date.startsWith(new Date().toISOString().slice(0,7)); }).length;
  var colors = ['background:#e8f0fe;color:#1a73e8','background:#e6f4ea;color:#1e8e3e','background:#fef3e2;color:#e37400'];
  var queueItems = [0,1,2,3,4].map(function(i) {
    var idx = (nextIdx + i) % 3;
    var d = BLOCKS[currentBlock][idx];
    return '<div class="queue-card"><div class="queue-num" style="' + colors[idx] + '">' + (i+1) + '</div>' +
      '<div class="queue-info"><div class="queue-name">' + (i===0?'▶ ':'') + d.shortName + '</div>' +
      '<div class="queue-sub">' + d.exercises.length + ' exercises · ' + d.badge + ' · done ' + dayCounts[idx] + 'x</div></div></div>';
  }).join('');
  document.getElementById('screen-queue').innerHTML = blockToggleHtml() +
    '<div class="stats-row">' +
    '<div class="stat-tile"><div class="stat-tile-label">Total sessions</div><div class="stat-tile-val">' + data.length + '</div></div>' +
    '<div class="stat-tile"><div class="stat-tile-label">This month</div><div class="stat-tile-val">' + thisMonth + '</div></div>' +
    '<div class="stat-tile"><div class="stat-tile-label">D1 done</div><div class="stat-tile-val">' + dayCounts[0] + '</div></div>' +
    '<div class="stat-tile"><div class="stat-tile-label">D2 done</div><div class="stat-tile-val">' + dayCounts[1] + '</div></div>' +
    '</div><div class="section-title">Rotation queue — Block ' + currentBlock + '</div>' + queueItems;
}

function renderLog() {
  var data = getData();
  var screen = document.getElementById('screen-log');
  if (!data.length) { screen.innerHTML = '<div class="empty-state">No sessions logged yet.<br>Complete a workout to see history.</div>'; return; }
  screen.innerHTML = data.map(function(d) {
    var highlights = '';
    if (d.setLog) {
      highlights = Object.keys(d.setLog).filter(function(k) {
        return d.setLog[k] && d.setLog[k].some(function(s) { return s.load || s.repsLogged; });
      }).slice(0,3).map(function(k) {
        return k + ': ' + d.setLog[k].filter(function(s){return s.load||s.repsLogged;}).map(function(s){return (s.load?s.load+'lb':'')+(s.load&&s.repsLogged?'x':'')+(s.repsLogged||'');}).join(', ');
      }).join(' · ');
    }
    return '<div class="log-card">' +
      '<button class="log-delete" onclick="deleteEntry(' + d.id + ')">x</button>' +
      '<div class="log-card-date">' + d.date + '</div>' +
      '<div class="log-card-day">' + (d.dayName||'Day '+((d.dayIdx||0)+1)) + ' · Block ' + (d.block||1) + '</div>' +
      '<div class="log-card-meta">' + (d.duration?'<span>⏱ '+d.duration+' min</span>':'') + '<span>✓ '+(d.completed||'?')+'/'+(d.total||'?')+'</span></div>' +
      (highlights?'<div class="log-notes-text">'+highlights+'</div>':'') + '</div>';
  }).join('');
}

function deleteEntry(id) { saveData(getData().filter(function(d){return d.id!==id;})); renderLog(); renderQueue(); }

renderWorkout();
