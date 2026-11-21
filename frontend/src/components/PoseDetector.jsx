import React, { useEffect, useRef, useState, useCallback } from 'react';
import { PoseLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';
import {
  FILESET_WASM_URL,
  POSE_MODEL_CANDIDATES,
  getModelAssetUrl,
  preloadPoseAssets,
  preloadWasm,
} from '../utils/poseModelPreload';
import {
  getLegacyFallback,
  PATTERN_MAP,
  calcAngle,
  getAlpha,
  getFrameSkip,
  MIN_VISIBILITY,
  TRACK_STALE_MS,
  getPrimaryVisibility,
  smoothPoint,
  checkForm,
  createInitialRepState,
  processRepCounters,
  drawSkeleton,
  drawExerciseAngles,
  drawJointNodes,
  drawGaugeHud,
} from '../features/pose-detection';

// Start WASM + lite model fetch as soon as this module is imported
preloadPoseAssets();

// Global singleton storage to cache initialized PoseLandmarker instance
let globalPoseLandmarker = null;
let globalPoseLandmarkerPromise = null;

export default function PoseDetector({
  videoRef,
  isActive,
  exercise,
  currentReps = 0,
  onRepUpdate,
  onFormFeedback,
  onLoadingChange,
}) {
  const exerciseName = exercise?.name || '';
  const canvasRef = useRef(null);
  const requestRef = useRef(null);
  const landmarkerRef = useRef(null);
  const lastVideoTimeRef = useRef(-1);
  const [isModelLoaded, setIsModelLoaded] = useState(false);

  // Warming message auto-dismiss timer
  const warmingTimerRef = useRef(null);

  useEffect(() => {
    if (isModelLoaded) {
      onLoadingChange?.('warming');

      if (warmingTimerRef.current) {
        clearTimeout(warmingTimerRef.current);
      }

      warmingTimerRef.current = setTimeout(() => {
        onLoadingChange?.('ready');
        warmingTimerRef.current = setTimeout(() => {
          onLoadingChange?.('hidden');
        }, 2000);
      }, 3000);
    } else {
      onLoadingChange?.('initializing');
    }

    return () => {
      if (warmingTimerRef.current) {
        clearTimeout(warmingTimerRef.current);
      }
    };
  }, [isModelLoaded, onLoadingChange]);

  const smoothedRef = useRef(null);
  const frameCountRef = useRef(0);
  const lastWarningRef = useRef('');
  const warningStabilityRef = useRef({ warning: '', count: 0 });
  const stateRef = useRef(createInitialRepState('GENERIC', currentReps));

  // Sync internal rep count when parent resets it
  useEffect(() => {
    if (currentReps === 0) {
      stateRef.current.reps = 0;
      stateRef.current.stage = 'rest';
    } else {
      stateRef.current.reps = currentReps;
    }
  }, [currentReps]);

  // Initialise MediaPipe (Cached Singleton)
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        if (globalPoseLandmarker) {
          if (active) {
            landmarkerRef.current = globalPoseLandmarker;
            setIsModelLoaded(true);
          }
          return;
        }

        if (!globalPoseLandmarkerPromise) {
          globalPoseLandmarkerPromise = (async () => {
            await preloadWasm();
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
            globalPoseLandmarker = lm;
            return lm;
          })();
        }

        const lm = await globalPoseLandmarkerPromise;
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

  // Reset state on exercise change
  useEffect(() => {
    const p = exercise?.movement_pattern
      ? (PATTERN_MAP[exercise.movement_pattern] || "GENERIC")
      : getLegacyFallback(exerciseName);

    console.log(`[PoseDetector] Routing exercise: "${exerciseName}" | backend pattern: "${exercise?.movement_pattern || 'none'}" -> resolved detector: "${p}"`);

    stateRef.current = createInitialRepState(p, 0);
    smoothedRef.current = null;
    lastWarningRef.current = '';
    warningStabilityRef.current = { warning: '', count: 0 };
  }, [exerciseName, exercise?.movement_pattern]);

  // Main Analysis & Drawing Callback
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

    const raw = {
      l_sh: toPoint(11), r_sh: toPoint(12),
      l_el: toPoint(13), r_el: toPoint(14),
      l_wr: toPoint(15), r_wr: toPoint(16),
      l_hi: toPoint(23), r_hi: toPoint(24),
      l_kn: toPoint(25), r_kn: toPoint(26),
      l_an: toPoint(27), r_an: toPoint(28),
    };

    const pattern = stateRef.current.pattern;
    const alpha = getAlpha(pattern);
    if (smoothedRef.current) {
      for (const key of Object.keys(raw)) {
        raw[key] = smoothPoint(smoothedRef.current[key], raw[key], alpha);
      }
    }
    smoothedRef.current = { ...raw };

    const { l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hi, r_hi, l_kn, r_kn, l_an, r_an } = raw;

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

    const keyVisibility = getPrimaryVisibility(pattern, raw);
    const isConfident = keyVisibility > MIN_VISIBILITY;
    const s = stateRef.current;

    if (pattern === 'RAISE' && isConfident) {
      if (s.baselineShoulder === null) {
        s.baselineShoulder = avgShoulder;
      } else if (s.stage === 'rest') {
        s.baselineShoulder = s.baselineShoulder * 0.90 + avgShoulder * 0.10;
      }
    }

    const formCheck = checkForm(pattern, allAngles, {
      baselineShoulder: s.baselineShoulder,
    });
    let mainColor = formCheck.color;
    if (isPredictionStale) mainColor = '#f59e0b';
    const now = Date.now();

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

    const { effectiveDown, effectiveUp } = processRepCounters({
      s,
      pattern,
      angles: allAngles,
      rawPoints: raw,
      isPredictionStale,
      isConfident,
      now,
      onRepUpdate,
      onFormFeedback,
    });

    drawSkeleton(ctx, raw, mainColor);
    drawExerciseAngles(ctx, pattern, raw, allAngles, effectiveUp, effectiveDown);
    drawJointNodes(ctx, raw, mainColor);

    if (isConfident) {
      drawGaugeHud(ctx, s, canvas, effectiveUp, effectiveDown, mainColor);
    }

    ctx.restore();
  }, [onFormFeedback, onRepUpdate]);

  // Video processing frame loop
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

          const frameSkip = getFrameSkip();
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
            console.warn('[PoseDetector] Frame processing error:', err?.message || err);
            stateRef.current.lostFrames = (stateRef.current.lostFrames || 0) + 1;
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
