import React, { useEffect, useRef, useState, useCallback } from 'react';
import { PoseLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';
import {
  FILESET_WASM_URL,
  POSE_MODEL_CANDIDATES,
  getModelAssetUrl,
  preloadPoseAssets,
} from '../utils/poseModelPreload';

// ─── COMPREHENSIVE MOVEMENT PATTERNS ──
// Pattern mapping for 1300+ exercise dataset via keyword matching
const MOVEMENT_PATTERNS = {
  CURL:   ['curl', 'bicep', 'hammer', 'preacher', 'concentration', 'incline curl', 'cable curl', 'db curl'],
  PRESS:  ['press', 'push', 'extension', 'tricep', 'dip', 'punch', 'bench press', 'chest press', 'overhead press', 'shoulder press', 'arnold press', 'push up', 'pushup'],
  SQUAT:  ['squat', 'leg press', 'wall sit', 'box jump', 'goblet', 'hack', 'sissy', 'front squat', 'back squat', 'split squat'],
  HINGE:  ['deadlift', 'good morning', 'row', 'swing', 'pull', 'chin up', 'chin-up', 'lat', 'shrug', 'upright row', 'bent over', 'hip thrust', 'glute bridge', 'back extension'],
  LUNGE:  ['lunge', 'step', 'bulgarian', 'split squat', 'step up', 'curtsey'],
  RAISE:  ['raise', 'fly', 'delt', 'abduction', 'adduction', 'lateral', 'front raise', 'rear delt', 'reverse fly', 'shrug'],
  CORE:   ['plank', 'crunch', 'sit up', 'sit-up', 'situp', 'twist', 'bend', 'roll', 'waist', 'core', 'ab ', 'abs', 'leg raise', 'dead bug', 'bird dog', 'hollow', 'mountain climber', 'bicycle'],
  CARDIO: ['run', 'bike', 'jump', 'burpee', 'skip', 'cardio', 'mountain climber', 'high knee', 'jumping jack', 'jog', 'sprint'],
  CALF:   ['calf', 'heel raise', 'toe raise', 'ankle'],
};

const getMovementPattern = (name) => {
  const lower = (name || '').toLowerCase();
  for (const [pat, kws] of Object.entries(MOVEMENT_PATTERNS)) {
    if (kws.some(kw => lower.includes(kw))) return pat;
  }
  return 'GENERIC';
};

// ─── Speed category for adaptive smoothing & frame skip ──
const SPEED_CATEGORY = {
  CURL: 'fast', PRESS: 'fast', RAISE: 'fast',
  SQUAT: 'slow', HINGE: 'slow', LUNGE: 'slow',
  CORE: 'slow', CALF: 'fast',
  CARDIO: 'fast', GENERIC: 'medium',
};

// ─── ANGLE MATH ──
const calcAngle = (a, b, c) => {
  const rad = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let deg = Math.abs(rad * 180 / Math.PI);
  if (deg > 180) deg = 360 - deg;
  return deg;
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

const getFrameSkip = (pattern) => {
  const speed = SPEED_CATEGORY[pattern] || 'medium';
  if (speed === 'slow') return 1; // process every other frame
  return 0; // process every frame for fast/medium exercises
};

// Minimum visibility threshold for reliable angle calculations
const MIN_VISIBILITY = 0.30;
const TRACK_STALE_MS = 180;

const getPrimaryVisibility = (pattern, pts) => {
  switch (pattern) {
    case 'CURL':
    case 'PRESS':
    case 'RAISE':
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

// ─── POSTURE STATUS CONSTANTS ──
const POSTURE_STATUS = {
  GOOD: 'good',
  WARNING: 'warning',
  TRACKING_LOST: 'tracking_lost',
};

// Stability thresholds: how many consecutive frames before state changes
const WARNING_THRESHOLD = 3;  // bad frames before warning fires
const GOOD_THRESHOLD = 3;     // good frames before warning clears
const TRACKING_LOST_THRESHOLD = 4; // lost frames before showing tracking-lost

// ─── FORM SAFETY RULES per pattern ──
const checkForm = (pattern, angles, calibration = {}, repStage = 'rest') => {
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
      // Priority order: body straightness > shoulder alignment > elbow flare > symmetry > depth
      // A. Body straightness — hip sagging or pike
      if (avgHip < 140)
        return { warning: 'Hips too low — keep your body in a straight line!', color: '#ef4444' };
      if (avgHip > 185)
        return { warning: 'Hips too high — lower them in line with shoulders.', color: '#ef4444' };
      // B. Shoulder alignment — detect twisting
      if (Math.abs(leftShoulder - rightShoulder) > 30)
        return { warning: 'Keep shoulders level — avoid twisting.', color: '#f59e0b' };
      // C. Elbow flare — elbows too wide
      if (avgElbow < 75 && avgShoulder > 125)
        return { warning: 'Don\'t flare elbows too wide — injury risk!', color: '#ef4444' };
      // D. Elbow symmetry — uneven arm pressure
      if (Math.abs(leftElbow - rightElbow) > 35)
        return { warning: 'Press evenly with both arms!', color: '#f59e0b' };
      // E. Depth — shallow push-ups during the extension phase
      if (avgElbow > 150 && repStage === 'extended')
        return { warning: 'Go lower for a full push-up!', color: '#f59e0b' };
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
    case 'CORE':
      // Good plank: avgHip ~160-180°. Sagging hips: avgHip < 130°. Over-crunch: avgHip < 80°.
      if (avgHip < 80)
        return { warning: 'Control the movement — don\'t over-flex your spine.', color: '#f59e0b' };
      if (avgHip < 130)
        return { warning: 'Engage your core — don\'t let your hips sag!', color: '#ef4444' };
      break;
    default:
      break;
  }
  return { warning: null, color: '#22c55e' };
};

// ─── REP COUNTING CONFIG with ROM validation ──
// PRESS: starts EXTENDED (arms ~160°), goes DOWN (contracted ~80°), back UP.
// cfg.down > cfg.up → triggers the "inverted" branch in the state machine.
const REP_CONFIG = {
  CURL:    { joint: 'elbow',    down: 150, up: 60,  startStage: 'rest', cooldown: 400, minROM: 0.50 },
  PRESS:   { joint: 'elbow',    down: 160, up: 85,  startStage: 'rest', cooldown: 400, minROM: 0.50 },  // FIX: inverted so state machine uses correct branch
  SQUAT:   { joint: 'knee',     down: 100, up: 160, startStage: 'rest', cooldown: 600, minROM: 0.50 },
  HINGE:   { joint: 'hip',      down: 120, up: 160, startStage: 'rest', cooldown: 600, minROM: 0.50 },
  LUNGE:   { joint: 'knee',     down: 100, up: 150, startStage: 'rest', cooldown: 600, useMin: true, minROM: 0.45 },
  RAISE:   { joint: 'shoulder', down: 30,  up: 80,  startStage: 'rest', cooldown: 400, minROM: 0.50 },
  CORE:    { joint: 'hip',      down: 110, up: 150, startStage: 'rest', cooldown: 500, minROM: 0.40, isHold: false },
  CALF:    { joint: 'ankleY',   down: 0,   up: 0,   startStage: 'rest', cooldown: 300, minROM: 0.30 },
  CARDIO:  { joint: 'avg',      down: 100, up: 140, startStage: 'rest', cooldown: 400, minROM: 0.40 },
  GENERIC: { joint: 'avg',      down: 100, up: 140, startStage: 'rest', cooldown: 400, minROM: 0.40 },
};

// Hysteresis band to avoid jitter-based double counting
const HYSTERESIS = 8;

export default function PoseDetector({
  videoRef,
  isActive,
  exerciseName,
  onRepUpdate,
  onFormFeedback,
  onLoadingChange, // Bug #2 Fix: Callback to notify parent about loading status
  resetKey,        // FIX: When this value changes the rep counter resets (used on new set)
}) {
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
  // Stability window: count consecutive bad/good frames to prevent jitter
  const badFrameCountRef = useRef(0);
  const goodFrameCountRef = useRef(0);
  const trackingLostCountRef = useRef(0);
  // Track current posture status to avoid redundant callbacks
  const currentPostureStatusRef = useRef(POSTURE_STATUS.GOOD);

  // Rep state — 3-phase state machine
  const stateRef = useRef({
    stage: 'rest',       // rest → contracting → extended → rest
    reps: 0,
    pattern: 'GENERIC',
    lastRepTime: 0,
    lastFeedbackTime: 0,
    minAngleInRep: 999,  // Track min angle during contraction for ROM validation
    maxAngleInRep: 0,    // Track max angle during extension for ROM validation
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

  // ─── Initialise MediaPipe ──
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        // Warm CDN/model caches before creating the detector for faster first use.
        await preloadPoseAssets();
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
              minPoseDetectionConfidence: 0.5,
              minPosePresenceConfidence: 0.5,
              minTrackingConfidence: 0.55,
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

  // ─── Reset state on exercise change OR when resetKey changes (new set) ──
  useEffect(() => {
    const p = getMovementPattern(exerciseName || '');
    stateRef.current = {
      stage: 'rest',
      reps: 0,
      pattern: p,
      lastRepTime: 0,
      lastFeedbackTime: 0,
      minAngleInRep: 999,
      maxAngleInRep: 0,
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
    badFrameCountRef.current = 0;
    goodFrameCountRef.current = 0;
    trackingLostCountRef.current = 0;
    currentPostureStatusRef.current = POSTURE_STATUS.GOOD;
  }, [exerciseName, resetKey]);  // resetKey changes when a new set starts

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
      v: rawLandmarks[idx].visibility || 0,
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
    const now = Date.now();

    // ─── TRACKING LOST HANDLING ──
    // Separate tracking loss from bad posture: low visibility is NOT bad form.
    if (!isConfident && !isPredictionStale) {
      trackingLostCountRef.current += 1;
      badFrameCountRef.current = 0;
      goodFrameCountRef.current = 0;

      if (trackingLostCountRef.current >= TRACKING_LOST_THRESHOLD &&
          currentPostureStatusRef.current !== POSTURE_STATUS.TRACKING_LOST) {
        currentPostureStatusRef.current = POSTURE_STATUS.TRACKING_LOST;
        onFormFeedback?.({
          status: POSTURE_STATUS.TRACKING_LOST,
          message: 'Camera tracking momentarily lost. Stay in frame.',
        });
      }
    }

    // Personalized baseline update for shoulder raises.
    // We only adapt baseline on confident frames to avoid jitter drift.
    if (pattern === 'RAISE' && isConfident) {
      if (s.baselineShoulder === null) {
        s.baselineShoulder = avgShoulder;
      } else if (s.stage === 'rest') {
        s.baselineShoulder = s.baselineShoulder * 0.90 + avgShoulder * 0.10;
      }
    }

    // ─── FORM CHECK with stability window ──
    const formCheck = checkForm(pattern, allAngles, {
      baselineShoulder: s.baselineShoulder,
    }, s.stage);
    let mainColor = formCheck.color;
    if (isPredictionStale) mainColor = '#f59e0b';

    // ─── STABILITY WINDOW: badFrames / goodFrames counter ──
    // Prevents single-frame noise from triggering warnings or clearing them.
    if (!isPredictionStale && isConfident) {
      trackingLostCountRef.current = 0; // Reset tracking lost counter on confident frame

      if (formCheck.warning) {
        // Bad frame: increment bad counter, reset good counter
        badFrameCountRef.current += 1;
        goodFrameCountRef.current = 0;

        // Fire warning after WARNING_THRESHOLD consecutive bad frames
        if (badFrameCountRef.current >= WARNING_THRESHOLD) {
          if (formCheck.warning !== lastWarningRef.current ||
              currentPostureStatusRef.current !== POSTURE_STATUS.WARNING) {
            currentPostureStatusRef.current = POSTURE_STATUS.WARNING;
            onFormFeedback?.({
              status: POSTURE_STATUS.WARNING,
              message: formCheck.warning,
            });
            lastWarningRef.current = formCheck.warning;
            s.lastFeedbackTime = now;
          }
        }
      } else {
        // Good frame: increment good counter, reset bad counter
        goodFrameCountRef.current += 1;
        badFrameCountRef.current = 0;

        // ── THE CORE FIX: Clear warning after GOOD_THRESHOLD consecutive good frames ──
        if (goodFrameCountRef.current >= GOOD_THRESHOLD &&
            currentPostureStatusRef.current !== POSTURE_STATUS.GOOD) {
          currentPostureStatusRef.current = POSTURE_STATUS.GOOD;
          onFormFeedback?.({
            status: POSTURE_STATUS.GOOD,
            message: null,
          });
          lastWarningRef.current = '';
        }
      }
    }

    // ─── DEBUG LOGGING (every 30 frames) ──
    if (isConfident && frameCountRef.current % 30 === 0) {
      console.log({
        postureValid: !formCheck.warning,
        postureStatus: currentPostureStatusRef.current,
        feedbackMessage: formCheck.warning || 'Good Form',
        avgElbow: Math.round(avgElbow),
        avgHip: Math.round(avgHip),
        avgShoulder: Math.round(avgShoulder),
        avgKnee: Math.round(avgKnee),
        keyVisibility: parseFloat(keyVisibility.toFixed(2)),
        stage: s.stage,
        reps: s.reps,
        badFrames: badFrameCountRef.current,
        goodFrames: goodFrameCountRef.current,
        frameTimestamp: now,
      });
    }

    // ─── REP COUNTING — 3-phase state machine with ROM validation ──
    const cfg = REP_CONFIG[pattern] || REP_CONFIG.GENERIC;
    const cooldownOK = now - s.lastRepTime > cfg.cooldown;
    const expectedROM = Math.abs(cfg.up - cfg.down);

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
      s.minAngleInRep = Math.min(s.minAngleInRep, trackAngle);
      s.maxAngleInRep = Math.max(s.maxAngleInRep, trackAngle);

      if (cfg.down < cfg.up) {
        // "Normal" — angle starts high (rest), goes low (contracted), back to high
        // rest → contracting (angle drops below down threshold)
        // contracting → extended (angle rises above up threshold) → count rep if ROM valid
        if (s.stage === 'rest' && trackAngle < cfg.down - HYSTERESIS) {
          s.stage = 'contracting';
          s.minAngleInRep = trackAngle;
          s.maxAngleInRep = trackAngle;
        }
        if (s.stage === 'contracting' && trackAngle > cfg.up + HYSTERESIS && cooldownOK) {
          // Validate ROM before counting
          const actualROM = s.maxAngleInRep - s.minAngleInRep;
          if (actualROM >= expectedROM * cfg.minROM) {
            s.stage = 'rest';
            s.reps += 1;
            s.lastRepTime = now;
            s.minAngleInRep = 999;
            s.maxAngleInRep = 0;
            onRepUpdate?.(s.reps);
          } else {
            // Partial rep — reset without counting
            s.stage = 'rest';
            s.minAngleInRep = 999;
            s.maxAngleInRep = 0;
            // Feedback for partial reps (debounced)
            if (now - s.lastFeedbackTime > 3000) {
              onFormFeedback?.('Complete the full range of motion!');
              s.lastFeedbackTime = now;
            }
          }
        }
      } else {
        // "Inverted" — angle starts high, drops to contracted, rises back
        if (s.stage === 'rest' && trackAngle > cfg.up + HYSTERESIS) {
          s.stage = 'extended';
          s.minAngleInRep = trackAngle;
          s.maxAngleInRep = trackAngle;
        }
        if (s.stage === 'extended' && trackAngle < cfg.down - HYSTERESIS) {
          s.stage = 'contracting';
        }
        if (s.stage === 'contracting' && trackAngle > cfg.up + HYSTERESIS && cooldownOK) {
          const actualROM = s.maxAngleInRep - s.minAngleInRep;
          if (actualROM >= expectedROM * cfg.minROM) {
            s.stage = 'rest';
            s.reps += 1;
            s.lastRepTime = now;
            s.minAngleInRep = 999;
            s.maxAngleInRep = 0;
            onRepUpdate?.(s.reps);
          } else {
            s.stage = 'rest';
            s.minAngleInRep = 999;
            s.maxAngleInRep = 0;
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
      if (a.v > 0.4 && b.v > 0.4) {
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
    const drawAngleArc = (a, b, c, angle, label) => {
      if (a.v < 0.4 || b.v < 0.4 || c.v < 0.4) return;
      const radius = 25;
      const startAng = Math.atan2(a.y - b.y, a.x - b.x);
      const endAng   = Math.atan2(c.y - b.y, c.x - b.x);

      // Arc
      ctx.beginPath();
      ctx.arc(b.x, b.y, radius, startAng, endAng, false);
      ctx.strokeStyle = angle < 90 ? '#ef4444' : angle < 140 ? '#f59e0b' : '#22c55e';
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
      ctx.fillStyle = angle < 90 ? '#f87171' : angle < 140 ? '#fbbf24' : '#4ade80';
      ctx.fillText(text, tx, ty);
    };

    // Show key angles per pattern
    const showAngles = {
      CURL:    () => { drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow'); drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow'); },
      PRESS:   () => { drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow'); drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow'); },
      SQUAT:   () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee'); drawAngleArc(r_hi, r_kn, r_an, rightKnee, 'R Knee'); drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); },
      HINGE:   () => { drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); drawAngleArc(r_sh, r_hi, r_kn, rightHip, 'R Hip'); },
      LUNGE:   () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee'); drawAngleArc(r_hi, r_kn, r_an, rightKnee, 'R Knee'); },
      RAISE:   () => { drawAngleArc(l_hi, l_sh, l_el, leftShoulder, 'L Shoulder'); drawAngleArc(r_hi, r_sh, r_el, rightShoulder, 'R Shoulder'); },
      CORE:    () => { drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); drawAngleArc(r_sh, r_hi, r_kn, rightHip, 'R Hip'); },
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
      if (n.v > 0.35) {
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

    // ─── Rep stage indicator (small HUD) ──
    if (isConfident) {
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
            Object.assign(canvasRef.current, { width: video.videoWidth, height: video.videoHeight });

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
