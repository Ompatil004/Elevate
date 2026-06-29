import React, { useEffect, useRef, useState, useCallback } from 'react';
import { PoseLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';
import {
  FILESET_WASM_URL,
  POSE_MODEL_CANDIDATES,
  getModelAssetUrl,
  preloadPoseAssets,
  preloadWasm,
} from '../utils/poseModelPreload';

// Start WASM + lite model fetch as soon as this module is imported
preloadPoseAssets();

// ─── COMPREHENSIVE MOVEMENT PATTERNS ──
// Pattern mapping for 1300+ exercise dataset via keyword matching
const LEGACY_MOVEMENT_PATTERNS = {
  CURL:   ['curl', 'bicep', 'hammer', 'preacher', 'concentration'],
  PRESS:  ['press', 'push', 'extension', 'tricep', 'dip', 'punch', 'bench press', 'overhead'],
  SQUAT:  ['squat', 'leg press', 'wall sit', 'box jump', 'goblet', 'hack', 'sissy'],
  HINGE:  ['deadlift', 'good morning', 'row', 'swing', 'pull', 'chin up', 'chin-up', 'lat', 'shrug', 'upright row', 'bent over'],
  LUNGE:  ['lunge', 'step', 'bulgarian', 'split squat'],
  RAISE:  ['raise', 'fly', 'delt', 'abduction', 'adduction', 'lateral', 'front raise'],
  CORE:   ['plank', 'crunch', 'sit up', 'sit-up', 'twist', 'bend', 'roll', 'waist', 'core', 'ab ', 'abs'],
  CARDIO: ['run', 'bike', 'jump', 'burpee', 'skip', 'cardio', 'mountain climber', 'high knee'],
  CALF:   ['calf', 'heel raise'],
};

const getLegacyFallback = (name) => {
  const lower = (name || '').toLowerCase();
  for (const [pat, kws] of Object.entries(LEGACY_MOVEMENT_PATTERNS)) {
    if (kws.some(kw => lower.includes(kw))) return pat;
  }
  return 'GENERIC';
};

const PATTERN_MAP = {
  curl: "CURL",

  horizontal_push: "PRESS",
  vertical_push: "PRESS",
  dip: "PRESS",
  tricep_extension: "PRESS",

  squat: "SQUAT",
  lunge: "LUNGE",

  hinge: "HINGE",

  // Pulling exercises track elbow angle (arm draws in), NOT hip angle
  row: "PULL",
  horizontal_pull: "PULL",
  vertical_pull: "PULL",

  crunch: "CORE",
  plank: "CORE",

  lateral_raise: "RAISE",

  calf: "CALF",
  cardio: "CARDIO",

  generic: "GENERIC"
};

// ─── Speed category for adaptive smoothing & frame skip ──
const SPEED_CATEGORY = {
  CURL: 'fast', PRESS: 'fast', RAISE: 'fast', PULL: 'medium',
  SQUAT: 'slow', HINGE: 'slow', LUNGE: 'slow',
  CORE: 'slow', CALF: 'fast',
  CARDIO: 'fast', GENERIC: 'medium',
};

// ─── ANGLE MATH ──
const calcAngle = (a, b, c) => {
  // Vector BA (from b to a)
  const ba = { x: a.x - b.x, y: a.y - b.y, z: (a.z || 0) - (b.z || 0) };
  // Vector BC (from b to c)
  const bc = { x: c.x - b.x, y: c.y - b.y, z: (c.z || 0) - (b.z || 0) };
  
  // Dot product
  const dotProduct = ba.x * bc.x + ba.y * bc.y + ba.z * bc.z;
  
  // Magnitudes
  const magBA = Math.sqrt(ba.x * ba.x + ba.y * ba.y + ba.z * ba.z);
  const magBC = Math.sqrt(bc.x * bc.x + bc.y * bc.y + bc.z * bc.z);
  
  if (magBA * magBC === 0) return 0;
  
  // Clamp to prevent NaN due to floating point precision
  const cosTheta = Math.max(-1.0, Math.min(1.0, dotProduct / (magBA * magBC)));
  
  // Angle in radians converted to degrees
  return Math.abs(Math.acos(cosTheta) * 180 / Math.PI);
};

// ─── Adaptive EMA smoother ──
// Fast exercises (curls): high alpha (0.50) = more responsive to quick movement
// Slow exercises (squats): low alpha (0.25) = smoother, less jitter
const emaSmooth = (prev, curr, alpha) => ({
  x: prev.x * (1 - alpha) + curr.x * alpha,
  y: prev.y * (1 - alpha) + curr.y * alpha,
  z: (prev.z || 0) * (1 - alpha) + (curr.z || 0) * alpha,
  v: prev.v * 0.3 + curr.v * 0.7,
});

const getAlpha = (pattern) => {
  const speed = SPEED_CATEGORY[pattern] || 'medium';
  if (speed === 'fast') return 0.40;
  if (speed === 'slow') return 0.22;
  return 0.30; // medium
};

const getFrameSkip = (_pattern) => 0; // process every frame for smooth overlay

// Minimum visibility threshold for reliable angle calculations
const MIN_VISIBILITY = 0.40;
const TRACK_STALE_MS = 180;

const getPrimaryVisibility = (pattern, pts) => {
  switch (pattern) {
    case 'CURL':
    case 'PRESS':
    case 'RAISE':
    case 'PULL':
      return Math.min(pts.l_sh.v, pts.r_sh.v, pts.l_el.v, pts.r_el.v, pts.l_wr.v, pts.r_wr.v);
    case 'SQUAT':
    case 'LUNGE':
    case 'HINGE':
    case 'CALF':
      return Math.min(pts.l_hi.v, pts.r_hi.v, pts.l_kn.v, pts.r_kn.v, pts.l_an.v, pts.r_an.v);
    case 'CORE':
      return Math.min(pts.l_sh.v, pts.r_sh.v, pts.l_hi.v, pts.r_hi.v, pts.l_kn.v, pts.r_kn.v);
    default:
      return Math.min(
        pts.l_sh.v, pts.r_sh.v, pts.l_el.v, pts.r_el.v,
        pts.l_hi.v, pts.r_hi.v, pts.l_kn.v, pts.r_kn.v
      );
  }
};

const smoothPoint = (prev, curr, alpha) => {
  if (!prev) return curr;
  if (curr.v < 0.2 && prev.v > 0.3) {
    return {
      x: prev.x,
      y: prev.y,
      z: prev.z || 0,
      v: Math.max(0, prev.v * 0.92),
    };
  }
  return emaSmooth(prev, curr, alpha);
};

// ─── FORM SAFETY RULES per pattern ──
const checkForm = (pattern, angles, calibration = {}) => {
  const { baselineShoulder = null } = calibration;
  const { avgElbow, avgKnee, avgHip, avgShoulder,
          leftElbow, rightElbow, leftKnee, rightKnee,
          leftShoulder, rightShoulder } = angles;

  switch (pattern) {
    case 'CURL':
      // Shoulder angle here is not torso tilt; only flag extreme compensation.
      if (avgShoulder > 100 && avgElbow < 120)
        return { warning: 'Keep elbows closer to your sides — avoid shoulder swing.', color: '#ef4444' };
      if (Math.abs(leftElbow - rightElbow) > 45)
        return { warning: 'Curl both arms evenly!', color: '#f59e0b' };
      break;
    case 'SQUAT':
      if (Math.abs(leftKnee - rightKnee) > 35)
        return { warning: 'Keep knees even — avoid shifting weight to one side.', color: '#f59e0b' };
      if (avgKnee < 60)
        return { warning: 'Don\'t go too deep — protect your knees!', color: '#ef4444' };
      break;
    case 'PRESS':
      if (avgElbow < 75 && avgShoulder > 125)
        return { warning: 'Don\'t flare elbows too wide — injury risk!', color: '#ef4444' };
      if (Math.abs(leftElbow - rightElbow) > 35)
        return { warning: 'Press evenly with both arms!', color: '#f59e0b' };
      break;
    case 'HINGE':
      if (avgHip < 70 && avgKnee < 105)
        return { warning: 'Keep legs straighter — this is a hip hinge.', color: '#ef4444' };
      if (avgHip < 90 && Math.abs(leftShoulder - rightShoulder) > 35)
        return { warning: 'Keep shoulders level — don\'t twist.', color: '#f59e0b' };
      break;
    case 'LUNGE':
      if (Math.min(leftKnee, rightKnee) < 55)
        return { warning: 'Control depth — avoid collapsing too low.', color: '#ef4444' };
      break;
    case 'RAISE':
      // Personalized tolerance: allow users with different limb lengths/mobility
      // to move slightly above the default target without false "bad form" warnings.
      {
        const dynamicCeil = baselineShoulder !== null
          ? Math.max(130, baselineShoulder + 38)
          : 130;
        if (avgShoulder > dynamicCeil)
          return { warning: 'Great control. Lower slightly to stay in the target raise range.', color: '#f59e0b' };
      }
      break;
    case 'PULL':
      if (Math.abs(leftElbow - rightElbow) > 45)
        return { warning: 'Pull evenly with both arms!', color: '#f59e0b' };
      break;
    case 'CORE':
      if (avgHip < 55)
        return { warning: 'Control the movement — don\'t over-flex your spine.', color: '#f59e0b' };
      break;
    default:
      break;
  }
  return { warning: null, color: '#22c55e' };
};

// ─── REP COUNTING CONFIG with ROM validation ──
// Initial thresholds are intentionally wide; auto-calibration narrows them
// to each user's real range after the first rep is observed.
const REP_CONFIG = {
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

// Hysteresis bands:
//   ENTRY_HYSTERESIS – smaller so users don't need to go far past the threshold to begin a rep
//   EXIT_HYSTERESIS  – larger to prevent noise from prematurely counting a rep
const ENTRY_HYSTERESIS = 5;
const EXIT_HYSTERESIS  = 8;

// How many consecutive frames an angle must hold past a threshold before a state
// transition is confirmed.  Slow exercises need more frames because they move
// deliberately; fast ones would feel sluggish with 3 frames.
const getConfirmFrames = (pattern) => {
  const speed = SPEED_CATEGORY[pattern] || 'medium';
  if (speed === 'slow') return 3;
  return 2;
};

export default function PoseDetector({
  videoRef,
  isActive,
  exercise,
  currentReps = 0,
  onRepUpdate,
  onFormFeedback,
  onLoadingChange, // Bug #2 Fix: Callback to notify parent about loading status
}) {
  const exerciseName = exercise?.name || '';
  const canvasRef = useRef(null);
  const requestRef = useRef(null);
  const landmarkerRef = useRef(null);
  const lastVideoTimeRef = useRef(-1);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  
  // Bug #2 Fix: Warming message auto-dismiss timer
  const warmingTimerRef = useRef(null);

  // Auto-dismiss timer for warming message
  useEffect(() => {
    // When model loads, notify parent and set 3-second warming message
    if (isModelLoaded) {
      // Notify parent about loading status
      onLoadingChange?.('warming');

      // Clear any existing timer
      if (warmingTimerRef.current) {
        clearTimeout(warmingTimerRef.current);
      }

      // Auto-dismiss after 3 seconds
      warmingTimerRef.current = setTimeout(() => {
        onLoadingChange?.('ready');
        // Hide ready message after 2 seconds
        warmingTimerRef.current = setTimeout(() => {
            onLoadingChange?.('hidden');
        }, 2000);
      }, 3000);
    } else {
      onLoadingChange?.('initializing');
    }

    // Cleanup on unmount
    return () => {
      if (warmingTimerRef.current) {
        clearTimeout(warmingTimerRef.current);
      }
    };
  }, [isModelLoaded, onLoadingChange]);

  // EMA smoothed landmarks
  const smoothedRef = useRef(null);
  // Frame counter for skip logic
  const frameCountRef = useRef(0);
  // Track the last warning to avoid repeating the same message
  const lastWarningRef = useRef('');
  const warningStabilityRef = useRef({ warning: '', count: 0 });

  // Rep state — 3-phase state machine
  const stateRef = useRef({
    stage: 'rest',       // rest → contracting → extended → rest
    reps: 0,
    pattern: 'GENERIC',
    lastRepTime: 0,
    lastFeedbackTime: 0,
    minAngleInRep: 999,  // Track min angle during rep for ROM validation
    maxAngleInRep: 0,    // Track max angle during rep for ROM validation
    // Multi-frame noise gate: stage changes only after N consecutive confirming frames
    pendingStage: null,
    stageConfirmCount: 0,
    // Auto-calibration: updated after each rep to fit the user's personal ROM
    dynDown: null,
    dynUp: null,
    // Calf-specific: track ankle Y position
    baselineAnkleY: null,
    peakAnkleY: null,
    // Hold detection for isometric exercises
    holdStartTime: 0,
    holdReported: false,
    baselineShoulder: null,
    // Stabilize brief landmark dropouts
    lastStableLandmarks: null,
    lastSeenAt: 0,
    lostFrames: 0,
  });

  // Sync internal rep count when parent resets it (e.g. new set starts)
  useEffect(() => {
    if (currentReps === 0) {
      stateRef.current.reps = 0;
      stateRef.current.stage = 'rest';
    } else {
      stateRef.current.reps = currentReps;
    }
  }, [currentReps]);

  // ─── Initialise MediaPipe ──
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        // Reuse the WASM resolver that was pre-initialised at page load.
        // If not ready yet this awaits the same promise — no duplicate work.
        await preloadWasm();
        const vision = await FilesetResolver.forVisionTasks(FILESET_WASM_URL);

        let lm = null;
        let lastErr = null;

        for (const candidate of POSE_MODEL_CANDIDATES) {
          try {
            lm = await PoseLandmarker.createFromOptions(vision, {
              baseOptions: {
                modelAssetPath: getModelAssetUrl(candidate.model),
                delegate: candidate.delegate,
              },
              runningMode: 'VIDEO',
              numPoses: 1,
              minPoseDetectionConfidence: 0.45,
              minPosePresenceConfidence: 0.45,
              minTrackingConfidence: 0.5,
            });
            break;
          } catch (err) {
            lastErr = err;
          }
        }

        if (!lm) throw lastErr || new Error('Unable to load any MediaPipe pose model');

        if (active) {
          landmarkerRef.current = lm;
          setIsModelLoaded(true);
        }
      } catch (err) {
        console.error('MediaPipe init failed', err);
        onFormFeedback?.('Pose model failed to load. Check internet/GPU support and refresh.');
      }
    })();
    return () => { active = false; };
  }, [onFormFeedback]);

  // ─── Reset state on exercise change ──
  useEffect(() => {
    const p = exercise?.movement_pattern
      ? (PATTERN_MAP[exercise.movement_pattern] || "GENERIC")
      : getLegacyFallback(exerciseName);

    console.log(`[PoseDetector] Routing exercise: "${exerciseName}" | backend pattern: "${exercise?.movement_pattern || 'none'}" -> resolved detector: "${p}"`);

    stateRef.current = {
      stage: 'rest',
      reps: 0,
      pattern: p,
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
    };
    smoothedRef.current = null;
    lastWarningRef.current = '';
    warningStabilityRef.current = { warning: '', count: 0 };
  }, [exerciseName, exercise?.movement_pattern]);

  // ─────────────────────────────────────
  //  MAIN ANALYSIS & DRAWING
  // ─────────────────────────────────────
  const analyzeAndDraw = useCallback((rawLandmarks, canvas, isPredictionStale = false) => {
    const ctx = canvas.getContext('2d');
    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const toPoint = (idx) => ({
      x: rawLandmarks[idx].x * canvas.width,
      y: rawLandmarks[idx].y * canvas.height,
      z: rawLandmarks[idx].z || 0,
      v: rawLandmarks[idx].visibility || 1,
    });

    // Extract raw points
    const raw = {
      l_sh: toPoint(11), r_sh: toPoint(12),
      l_el: toPoint(13), r_el: toPoint(14),
      l_wr: toPoint(15), r_wr: toPoint(16),
      l_hi: toPoint(23), r_hi: toPoint(24),
      l_kn: toPoint(25), r_kn: toPoint(26),
      l_an: toPoint(27), r_an: toPoint(28),
    };

    // Apply adaptive EMA smoothing based on exercise speed
    const pattern = stateRef.current.pattern;
    const alpha = getAlpha(pattern);
    if (smoothedRef.current) {
      for (const key of Object.keys(raw)) {
        raw[key] = smoothPoint(smoothedRef.current[key], raw[key], alpha);
      }
    }
    smoothedRef.current = { ...raw };

    const { l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hi, r_hi, l_kn, r_kn, l_an, r_an } = raw;

    // Calculate all angles
    const leftElbow    = calcAngle(l_sh, l_el, l_wr);
    const rightElbow   = calcAngle(r_sh, r_el, r_wr);
    const leftShoulder = calcAngle(l_hi, l_sh, l_el);
    const rightShoulder= calcAngle(r_hi, r_sh, r_el);
    const leftKnee     = calcAngle(l_hi, l_kn, l_an);
    const rightKnee    = calcAngle(r_hi, r_kn, r_an);
    const leftHip      = calcAngle(l_sh, l_hi, l_kn);
    const rightHip     = calcAngle(r_sh, r_hi, r_kn);

    const avgElbow    = (leftElbow + rightElbow) / 2;
    const avgKnee     = (leftKnee + rightKnee) / 2;
    const avgHip      = (leftHip + rightHip) / 2;
    const avgShoulder = (leftShoulder + rightShoulder) / 2;

    const allAngles = {
      leftElbow, rightElbow, leftKnee, rightKnee,
      leftHip, rightHip, leftShoulder, rightShoulder,
      avgElbow, avgKnee, avgHip, avgShoulder,
    };

    // ─── CONFIDENCE GATE ──
    const keyVisibility = getPrimaryVisibility(pattern, raw);
    const isConfident = keyVisibility > MIN_VISIBILITY;

    const s = stateRef.current;

    // Personalized baseline update for shoulder raises.
    // We only adapt baseline on confident frames to avoid jitter drift.
    if (pattern === 'RAISE' && isConfident) {
      if (s.baselineShoulder === null) {
        s.baselineShoulder = avgShoulder;
      } else if (s.stage === 'rest') {
        s.baselineShoulder = s.baselineShoulder * 0.90 + avgShoulder * 0.10;
      }
    }

    // ─── FORM CHECK with dedup ──
    const formCheck = checkForm(pattern, allAngles, {
      baselineShoulder: s.baselineShoulder,
    });
    let mainColor = formCheck.color;
    if (isPredictionStale) mainColor = '#f59e0b';
    const now = Date.now();

    // Only fire feedback if: different warning than last, and enough time passed
    // Require warning stability across multiple confident frames to avoid jitter false alarms.
    if (!isPredictionStale && formCheck.warning) {
      if (warningStabilityRef.current.warning === formCheck.warning) {
        warningStabilityRef.current.count += 1;
      } else {
        warningStabilityRef.current = { warning: formCheck.warning, count: 1 };
      }

      const stableEnough = warningStabilityRef.current.count >= 8;
      if (
        stableEnough &&
        formCheck.warning !== lastWarningRef.current &&
        (now - stateRef.current.lastFeedbackTime > 5000)
      ) {
        onFormFeedback?.(formCheck.warning);
        stateRef.current.lastFeedbackTime = now;
        lastWarningRef.current = formCheck.warning;
      }
    } else {
      warningStabilityRef.current = { warning: '', count: 0 };
      if (!formCheck.warning && lastWarningRef.current !== '') {
        onFormFeedback?.(null);
        lastWarningRef.current = '';
      }
    }

    // ─── REP COUNTING — 3-phase state machine with ROM validation ──
    const cfg = REP_CONFIG[pattern] || REP_CONFIG.GENERIC;
    const cooldownOK = now - s.lastRepTime > cfg.cooldown;
    // Use auto-calibrated thresholds if available, otherwise fall back to config defaults.
    // dynDown/dynUp are updated after each rep based on the user's observed ROM.
    const effectiveDown = s.dynDown !== null ? s.dynDown : cfg.down;
    const effectiveUp   = s.dynUp   !== null ? s.dynUp   : cfg.up;
    const expectedROM = Math.abs(effectiveUp - effectiveDown);

    if (!isPredictionStale && isConfident && pattern === 'CALF') {
      // ── CALF RAISE: Use ankle Y-position delta instead of angle ──
      const ankleY = (l_an.y + r_an.y) / 2;

      if (s.baselineAnkleY === null) {
        s.baselineAnkleY = ankleY;
        s.peakAnkleY = ankleY;
      }

      // Detect upward movement (heel raise = Y decreases)
      if (s.stage === 'rest' && ankleY < s.baselineAnkleY - 8) {
        s.stage = 'contracting';
        s.peakAnkleY = ankleY;
      }
      if (s.stage === 'contracting') {
        if (ankleY < s.peakAnkleY) s.peakAnkleY = ankleY;
        // Coming back down
        if (ankleY > s.peakAnkleY + 5 && cooldownOK) {
          const lift = s.baselineAnkleY - s.peakAnkleY;
          if (lift > 6) { // Minimum lift threshold
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
    } else if (!isPredictionStale && isConfident && cfg.joint !== 'ankleY') {
      // ── Standard angle-based rep counting ──
      let trackAngle;
      switch (cfg.joint) {
        case 'elbow':   trackAngle = avgElbow;   break;
        case 'knee':    trackAngle = cfg.useMin ? Math.min(leftKnee, rightKnee) : avgKnee; break;
        case 'hip':     trackAngle = avgHip;     break;
        case 'shoulder':trackAngle = avgShoulder;break;
        case 'avg':
        default:        trackAngle = (avgElbow + avgKnee + avgHip + avgShoulder) / 4; break;
      }

      // Track angle extremes during the rep for ROM validation
      s.lastTrackAngle = trackAngle;
      s.minAngleInRep = Math.min(s.minAngleInRep, trackAngle);
      s.maxAngleInRep = Math.max(s.maxAngleInRep, trackAngle);

      // ── Multi-frame confirmation helpers ──
      // A state transition is only accepted after the angle holds past the threshold
      // for `cfr` consecutive frames.  This rejects single-frame noise spikes while
      // still responding quickly to genuine movement.
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
          // ── Auto-calibrate thresholds from this rep's observed range ──
          // Set dynDown/dynUp to 25% inside the user's actual min/max so the
          // state machine stays within their personal ROM rather than the config defaults.
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
        // "Normal" — angle starts high (rest), drops during contraction, rises to count
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
        // "Inverted" — angle starts low, rises to contracted, drops back to count
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
        const isInHoldPosition = avgHip > 140 && avgHip < 185; // Plank position range
        if (isInHoldPosition) {
          if (s.holdStartTime === 0) s.holdStartTime = now;
          const heldMs = now - s.holdStartTime;
          // Report every 5 seconds held
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

    // ─── DRAWING ──
    ctx.lineWidth = 4;
    ctx.strokeStyle = mainColor;
    ctx.shadowColor = mainColor;
    ctx.shadowBlur = 6;

    const drawLine = (a, b) => {
      if (a.v > 0.1 && b.v > 0.1) {
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
    };

    // Skeleton connections
    drawLine(l_sh, r_sh); drawLine(l_hi, r_hi);
    drawLine(l_sh, l_hi); drawLine(r_sh, r_hi);
    drawLine(l_sh, l_el); drawLine(l_el, l_wr);
    drawLine(r_sh, r_el); drawLine(r_el, r_wr);
    drawLine(l_hi, l_kn); drawLine(l_kn, l_an);
    drawLine(r_hi, r_kn); drawLine(r_kn, r_an);

    ctx.shadowBlur = 0;

    // ─── ANGLE ARC + TEXT on key joints ──
    const drawAngleArc = (a, b, c, angle, label, isPrimary = false) => {
      if (a.v < 0.1 || b.v < 0.1 || c.v < 0.1) return;
      const radius = 25;
      const startAng = Math.atan2(a.y - b.y, a.x - b.x);
      const endAng   = Math.atan2(c.y - b.y, c.x - b.x);

      let arcColor = '#22c55e'; // default green
      let textColor = '#4ade80';

      if (isPrimary && effectiveUp !== effectiveDown) {
        const extended = Math.max(effectiveUp, effectiveDown);
        const contracted = Math.min(effectiveUp, effectiveDown);
        // Warning zone if they hyper-extend or over-contract past safe limits
        if (angle > extended + 15 || angle < contracted - 15) {
          arcColor = '#ef4444'; // Red (Danger)
          textColor = '#f87171';
        } else if (angle > extended + EXIT_HYSTERESIS || angle < contracted - EXIT_HYSTERESIS) {
          arcColor = '#f59e0b'; // Yellow (Warning)
          textColor = '#fbbf24';
        } else {
          arcColor = '#3b82f6'; // Blue (Safe Target Zone)
          textColor = '#60a5fa';
        }
      } else {
         // Generic secondary joint coloring
         arcColor = angle < 90 ? '#ef4444' : angle < 140 ? '#f59e0b' : '#22c55e';
         textColor = angle < 90 ? '#f87171' : angle < 140 ? '#fbbf24' : '#4ade80';
      }

      // Arc
      ctx.beginPath();
      ctx.arc(b.x, b.y, radius, startAng, endAng, false);
      ctx.strokeStyle = arcColor;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Text background
      const tx = b.x + 15;
      const ty = b.y - 15;
      const text = `${label}: ${Math.round(angle)}°`;
      ctx.font = 'bold 13px monospace';
      const metrics = ctx.measureText(text);
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.fillRect(tx - 2, ty - 12, metrics.width + 6, 16);
      ctx.fillStyle = textColor;
      ctx.fillText(text, tx, ty);
    };

    // Show key angles per pattern
    const showAngles = {
      CURL:    () => { drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow', true); drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow', true); },
      PRESS:   () => { drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow', true); drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow', true); },
      PULL:    () => { drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow', true); drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow', true); },
      SQUAT:   () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee', true); drawAngleArc(r_hi, r_kn, r_an, rightKnee, 'R Knee', true); drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); },
      HINGE:   () => { drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip', true); drawAngleArc(r_sh, r_hi, r_kn, rightHip, 'R Hip', true); },
      LUNGE:   () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee', true); drawAngleArc(r_hi, r_kn, r_an, rightKnee, 'R Knee', true); },
      RAISE:   () => { drawAngleArc(l_hi, l_sh, l_el, leftShoulder, 'L Shoulder', true); drawAngleArc(r_hi, r_sh, r_el, rightShoulder, 'R Shoulder', true); },
      CORE:    () => { drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip', true); drawAngleArc(r_sh, r_hi, r_kn, rightHip, 'R Hip', true); },
      CALF:    () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee'); },
    };
    (showAngles[pattern] || (() => {
      drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow');
      drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow');
      drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee');
      drawAngleArc(r_hi, r_kn, r_an, rightKnee, 'R Knee');
    }))();

    // ─── Draw JOINT NODES ──
    const nodes = [l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hi, r_hi, l_kn, r_kn, l_an, r_an];
    for (const n of nodes) {
      if (n.v > 0.1) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, 7, 0, 2 * Math.PI);
        const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, 7);
        grad.addColorStop(0, '#fff');
        grad.addColorStop(1, mainColor);
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = mainColor;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }

    // ─── Rep stage indicator and Gauge HUD ──
    if (isConfident) {
      // Draw massive progress ring for visual coaching
      if (s.lastTrackAngle && effectiveUp !== effectiveDown) {
        const extended = Math.max(effectiveUp, effectiveDown);
        const contracted = Math.min(effectiveUp, effectiveDown);
        let progress = (extended - s.lastTrackAngle) / (extended - contracted);
        progress = Math.max(0, Math.min(1, progress));
        
        // Draw the ring (canvas is mirrored horizontally, so drawing at x=60 renders it on the right)
        const cx = 60;
        const cy = 60;
        const r = 40;
        
        // Background ring
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.lineWidth = 10;
        ctx.stroke();
        
        // Progress ring
        ctx.beginPath();
        ctx.arc(cx, cy, r, -Math.PI / 2, (-Math.PI / 2) + (2 * Math.PI * progress), false);
        ctx.strokeStyle = mainColor;
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        // Text inside ring
        ctx.font = 'bold 18px Inter, sans-serif';
        ctx.fillStyle = '#fff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${Math.round(progress * 100)}%`, cx, cy);
      }

      // Reset text alignment for other UI
      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';

      const stageLabel = s.stage === 'rest' ? 'READY' : s.stage === 'contracting' ? '⬇ DOWN' : '⬆ UP';
      const stageColor = s.stage === 'rest' ? '#a1a1aa' : s.stage === 'contracting' ? '#f59e0b' : '#22c55e';
      ctx.font = 'bold 14px Inter, sans-serif';
      ctx.fillStyle = 'rgba(0,0,0,0.5)';
      ctx.fillRect(10, canvas.height - 35, 80, 25);
      ctx.fillStyle = stageColor;
      ctx.fillText(stageLabel, 18, canvas.height - 17);
    }

    ctx.restore();
  }, [onFormFeedback, onRepUpdate]);

  // ─── Processing loop with adaptive frame skipping ──
  useEffect(() => {
    const processVideo = () => {
      if (!videoRef?.current || !canvasRef.current || !landmarkerRef.current || !isActive) {
        if (isActive) requestRef.current = requestAnimationFrame(processVideo);
        return;
      }

      const video = videoRef.current;
      if (video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
        if (video.currentTime !== lastVideoTimeRef.current) {
          lastVideoTimeRef.current = video.currentTime;
          frameCountRef.current += 1;
          const now = Date.now();

          // Adaptive frame skip based on exercise speed
          const frameSkip = getFrameSkip(stateRef.current.pattern);
          if (frameCountRef.current % (frameSkip + 1) !== 0) {
            requestRef.current = requestAnimationFrame(processVideo);
            return;
          }

          try {
            const results = landmarkerRef.current.detectForVideo(video, performance.now());
            const cv = canvasRef.current;
            if (cv.width !== video.videoWidth || cv.height !== video.videoHeight) {
              cv.width = video.videoWidth;
              cv.height = video.videoHeight;
            }

            if (results.landmarks?.length > 0) {
              stateRef.current.lastStableLandmarks = results.landmarks[0];
              stateRef.current.lastSeenAt = now;
              stateRef.current.lostFrames = 0;
              analyzeAndDraw(results.landmarks[0], canvasRef.current, false);
            } else {
              stateRef.current.lostFrames += 1;
              const canUseRecent = stateRef.current.lastStableLandmarks && (now - stateRef.current.lastSeenAt) < TRACK_STALE_MS;
              if (canUseRecent) {
                analyzeAndDraw(stateRef.current.lastStableLandmarks, canvasRef.current, true);
              } else {
                const ctx = canvasRef.current.getContext('2d');
                ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
              }
            }
          } catch (err) {
            // Bug #1 fix: log frame errors for debugging; don't crash the animation loop.
            console.warn('[PoseDetector] Frame processing error:', err?.message || err);
            stateRef.current.lostFrames = (stateRef.current.lostFrames || 0) + 1;
            // Notify user every ~30 dropped frames to avoid feedback spam
            if (stateRef.current.lostFrames % 30 === 1) {
              onFormFeedback?.('Camera tracking momentarily lost. Please stay in frame.');
            }
          }
        }
      }

      if (isActive) requestRef.current = requestAnimationFrame(processVideo);
    };

    if (isActive && isModelLoaded) {
      frameCountRef.current = 0;
      requestRef.current = requestAnimationFrame(processVideo);
    } else if (requestRef.current) {
      cancelAnimationFrame(requestRef.current);
    }

    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [analyzeAndDraw, isActive, isModelLoaded, onFormFeedback, videoRef]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        transform: 'scaleX(-1)',
        transformOrigin: 'center',
        pointerEvents: 'none',
        zIndex: 20,
      }}
    />
  );
}

/* eslint-disable-next-line react-refresh/only-export-components */
export { getLegacyFallback, PATTERN_MAP };

