import { SPEED_CATEGORY } from './poseMath';

// ─── REP COUNTING CONFIG with ROM validation ──
// Initial thresholds are intentionally wide; auto-calibration narrows them
// to each user's real range after the first rep is observed.
export const REP_CONFIG = {
  // Elbow angle (shoulder→elbow→wrist): extended ~160°, fully curled ~35°
  CURL:    { joint: 'elbow',    down: 70,  up: 145, cooldown: 400, minROM: 0.20 },
  // Push-up / press: elbow extended ~165°, at bottom ~70-90°
  PRESS:   { joint: 'elbow',    down: 95,  up: 145, cooldown: 400, minROM: 0.20 },
  // Pull-up / row: elbow extended ~165°, arm drawn in ~50-70°
  PULL:    { joint: 'elbow',    down: 70,  up: 145, cooldown: 500, minROM: 0.20 },
  // Knee angle (hip→knee→ankle): standing ~170°, full squat ~80-100°
  SQUAT:   { joint: 'knee',     down: 120, up: 158, cooldown: 600, minROM: 0.20 },
  // Hip angle (shoulder→hip→knee): standing ~165°, hinge bottom ~60-90°
  HINGE:   { joint: 'hip',      down: 100, up: 158, cooldown: 600, minROM: 0.20 },
  // Lead knee for lunges; same range as squat
  LUNGE:   { joint: 'knee',     down: 110, up: 158, cooldown: 600, useMin: true, minROM: 0.20 },
  // Shoulder angle (hip→shoulder→elbow): arm at side ~10-20°, raised ~90°
  RAISE:   { joint: 'shoulder', down: 25,  up: 75,  cooldown: 400, minROM: 0.20 },
  // Hip angle for crunch/sit-up: flat ~165°, full crunch ~60-80°
  CORE:    { joint: 'hip',      down: 85,  up: 158, cooldown: 500, minROM: 0.20 },
  CALF:    { joint: 'ankleY',   down: 0,   up: 0,   cooldown: 300, minROM: 0.20 },
  CARDIO:  { joint: 'avg',      down: 100, up: 145, cooldown: 400, minROM: 0.15 },
  GENERIC: { joint: 'avg',      down: 100, up: 145, cooldown: 400, minROM: 0.15 },
};

export const ENTRY_HYSTERESIS = 5;
export const EXIT_HYSTERESIS  = 8;

export const getConfirmFrames = (pattern) => {
  const speed = SPEED_CATEGORY[pattern] || 'medium';
  if (speed === 'slow') return 3;
  return 2;
};

export const createInitialRepState = (pattern = 'GENERIC', initialReps = 0) => ({
  stage: 'rest',       // rest → contracting → extended → rest
  reps: initialReps,
  pattern,
  lastRepTime: 0,
  lastFeedbackTime: 0,
  minAngleInRep: 999,
  maxAngleInRep: 0,
  pendingStage: null,
  stageConfirmCount: 0,
  dynDown: null,
  dynUp: null,
  baselineAnkleY: null,
  peakAnkleY: null,
  holdStartTime: 0,
  holdReported: false,
  baselineShoulder: null,
  lastStableLandmarks: null,
  lastSeenAt: 0,
  lostFrames: 0,
  lastTrackAngle: null,
});

export const processRepCounters = ({
  s,
  pattern,
  angles,
  rawPoints,
  isPredictionStale,
  isConfident,
  now,
  onRepUpdate,
  onFormFeedback,
}) => {
  const cfg = REP_CONFIG[pattern] || REP_CONFIG.GENERIC;
  const cooldownOK = now - s.lastRepTime > cfg.cooldown;
  const effectiveDown = s.dynDown !== null ? s.dynDown : cfg.down;
  const effectiveUp   = s.dynUp   !== null ? s.dynUp   : cfg.up;
  const expectedROM   = Math.abs(effectiveUp - effectiveDown);

  const { l_an, r_an } = rawPoints;
  const { avgElbow, avgKnee, avgHip, avgShoulder, leftKnee, rightKnee } = angles;

  if (!isPredictionStale && isConfident && pattern === 'CALF') {
    // ── CALF RAISE: Use ankle Y-position delta instead of angle ──
    const ankleY = (l_an.y + r_an.y) / 2;

    if (s.baselineAnkleY === null) {
      s.baselineAnkleY = ankleY;
      s.peakAnkleY = ankleY;
    }

    if (s.stage === 'rest' && ankleY < s.baselineAnkleY - 8) {
      s.stage = 'contracting';
      s.peakAnkleY = ankleY;
    }
    if (s.stage === 'contracting') {
      if (ankleY < s.peakAnkleY) s.peakAnkleY = ankleY;
      if (ankleY > s.peakAnkleY + 5 && cooldownOK) {
        const lift = s.baselineAnkleY - s.peakAnkleY;
        if (lift > 6) {
          s.stage = 'rest';
          s.reps += 1;
          s.lastRepTime = now;
          s.baselineAnkleY = ankleY;
          s.peakAnkleY = ankleY;
          onRepUpdate?.(s.reps);

          if (s.reps > 0 && s.reps % 3 === 0 && (now - s.lastFeedbackTime > 5000)) {
            const phrases = ['Great job!', 'Keep it up!', 'Perfect form!', 'You got this!', 'Nice work!'];
            onFormFeedback?.(phrases[Math.floor(Math.random() * phrases.length)]);
            s.lastFeedbackTime = now;
          }
        } else {
          s.stage = 'rest';
          s.baselineAnkleY = ankleY;
        }
      }
    }
    return { effectiveDown, effectiveUp };
  }

  if (!isPredictionStale && isConfident && cfg.joint !== 'ankleY') {
    let trackAngle;
    switch (cfg.joint) {
      case 'elbow':   trackAngle = avgElbow; break;
      case 'knee':    trackAngle = cfg.useMin ? Math.min(leftKnee, rightKnee) : avgKnee; break;
      case 'hip':     trackAngle = avgHip; break;
      case 'shoulder':trackAngle = avgShoulder; break;
      case 'avg':
      default:        trackAngle = (avgElbow + avgKnee + avgHip + avgShoulder) / 4; break;
    }

    s.lastTrackAngle = trackAngle;
    s.minAngleInRep = Math.min(s.minAngleInRep, trackAngle);
    s.maxAngleInRep = Math.max(s.maxAngleInRep, trackAngle);

    const cfr = getConfirmFrames(pattern);

    const confirmPending = (targetStage, conditionMet) => {
      if (conditionMet) {
        if (s.pendingStage === targetStage) {
          s.stageConfirmCount++;
        } else {
          s.pendingStage = targetStage;
          s.stageConfirmCount = 1;
        }
        return s.stageConfirmCount >= cfr;
      }
      if (s.pendingStage === targetStage) {
        s.pendingStage = null;
        s.stageConfirmCount = 0;
      }
      return false;
    };

    const finishRep = () => {
      const actualROM = s.maxAngleInRep - s.minAngleInRep;
      if (actualROM >= expectedROM * cfg.minROM) {
        if (actualROM > 15) {
          const newDown = s.minAngleInRep + actualROM * 0.25;
          const newUp   = s.maxAngleInRep - actualROM * 0.25;
          s.dynDown = s.dynDown === null ? newDown : s.dynDown * 0.5 + newDown * 0.5;
          s.dynUp   = s.dynUp   === null ? newUp   : s.dynUp   * 0.5 + newUp   * 0.5;
        }
        s.stage = 'rest';
        s.reps += 1;
        s.lastRepTime = now;
        s.minAngleInRep = 999;
        s.maxAngleInRep = 0;
        s.pendingStage = null;
        s.stageConfirmCount = 0;
        onRepUpdate?.(s.reps);
        if (s.reps > 0 && s.reps % 3 === 0 && (now - s.lastFeedbackTime > 5000)) {
          const phrases = ['Great job!', 'Keep it up!', 'Perfect form!', 'You got this!', 'Nice work!'];
          onFormFeedback?.(phrases[Math.floor(Math.random() * phrases.length)]);
          s.lastFeedbackTime = now;
        }
      } else {
        s.stage = 'rest';
        s.minAngleInRep = 999;
        s.maxAngleInRep = 0;
        s.pendingStage = null;
        s.stageConfirmCount = 0;
        if (now - s.lastFeedbackTime > 3000) {
          onFormFeedback?.('Complete the full range of motion!');
          s.lastFeedbackTime = now;
        }
      }
    };

    if (effectiveDown < effectiveUp) {
      if (s.stage === 'rest') {
        if (confirmPending('contracting', trackAngle < effectiveDown - ENTRY_HYSTERESIS)) {
          s.stage = 'contracting';
          s.pendingStage = null;
          s.stageConfirmCount = 0;
          s.minAngleInRep = trackAngle;
          s.maxAngleInRep = trackAngle;
        }
      }
      if (s.stage === 'contracting') {
        if (confirmPending('extended', trackAngle > effectiveUp + EXIT_HYSTERESIS && cooldownOK)) {
          finishRep();
        }
      }
    } else {
      if (s.stage === 'rest') {
        if (confirmPending('extended', trackAngle > effectiveUp + ENTRY_HYSTERESIS)) {
          s.stage = 'extended';
          s.pendingStage = null;
          s.stageConfirmCount = 0;
          s.minAngleInRep = trackAngle;
          s.maxAngleInRep = trackAngle;
        }
      }
      if (s.stage === 'extended') {
        if (confirmPending('contracting', trackAngle < effectiveDown - ENTRY_HYSTERESIS)) {
          s.stage = 'contracting';
          s.pendingStage = null;
          s.stageConfirmCount = 0;
        }
      }
      if (s.stage === 'contracting') {
        if (confirmPending('rest', trackAngle > effectiveUp + EXIT_HYSTERESIS && cooldownOK)) {
          finishRep();
        }
      }
    }

    // ── HOLD DETECTION for planks/isometric core ──
    if (pattern === 'CORE') {
      const isInHoldPosition = avgHip > 140 && avgHip < 185;
      if (isInHoldPosition) {
        if (s.holdStartTime === 0) s.holdStartTime = now;
        const heldMs = now - s.holdStartTime;
        if (heldMs > 5000 && !s.holdReported) {
          s.holdReported = true;
          onFormFeedback?.(`Great plank hold! ${Math.floor(heldMs / 1000)}s`);
        }
        if (heldMs > 10000 && s.holdReported && (heldMs % 5000 < 200)) {
          onFormFeedback?.(`Impressive hold! ${Math.floor(heldMs / 1000)}s 🔥`);
        }
      } else {
        if (s.holdStartTime > 0 && (now - s.holdStartTime) > 3000) {
          const totalHeld = Math.floor((now - s.holdStartTime) / 1000);
          onFormFeedback?.(`Hold released — ${totalHeld}s total`);
        }
        s.holdStartTime = 0;
        s.holdReported = false;
      }
    }
  }

  return { effectiveDown, effectiveUp };
};
