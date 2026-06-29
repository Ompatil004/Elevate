export const FILESET_WASM_URL = '/wasm';

export const POSE_MODEL_CANDIDATES = [
  { model: 'pose_landmarker_lite', delegate: 'GPU' },
  { model: 'pose_landmarker_full', delegate: 'GPU' },
  { model: 'pose_landmarker_lite', delegate: 'CPU' },
  { model: 'pose_landmarker_full', delegate: 'CPU' },
  { model: 'pose_landmarker_heavy', delegate: 'GPU' },
];

export const getModelAssetUrl = (model) =>
  `https://storage.googleapis.com/mediapipe-models/pose_landmarker/${model}/float16/1/${model}.task`;

let preloadPromise = null;

const warmFetch = async (url) => {
  try {
    // no-cors keeps preload robust across CDN CORS policies.
    await fetch(url, { mode: 'no-cors', cache: 'force-cache' });
  } catch {
    // Best-effort warmup. PoseDetector will perform full load fallback.
  }
};

export const preloadPoseAssets = async () => {
  if (typeof window === 'undefined') return;
  if (preloadPromise) return preloadPromise;

  preloadPromise = (async () => {
    try {
      const { FilesetResolver } = await import('@mediapipe/tasks-vision');
      await FilesetResolver.forVisionTasks(FILESET_WASM_URL);
    } catch (error) {
      console.warn('MediaPipe WASM preload failed:', error?.message || error);
    }

    // Optimize: Deduplicate and preload only the primary heavy model to save bandwidth.
    const primaryModel = POSE_MODEL_CANDIDATES[0]?.model || 'pose_landmarker_heavy';
    await warmFetch(getModelAssetUrl(primaryModel));
  })();

  return preloadPromise;
};
