export const FILESET_WASM_URL = '/wasm';

export const POSE_MODEL_CANDIDATES = [
  { model: 'pose_landmarker_lite', delegate: 'GPU' },
  { model: 'pose_landmarker_lite', delegate: 'CPU' },
  { model: 'pose_landmarker_full', delegate: 'GPU' },
  { model: 'pose_landmarker_full', delegate: 'CPU' },
  { model: 'pose_landmarker_heavy', delegate: 'GPU' },
];

export const getModelAssetUrl = (model) =>
  `https://storage.googleapis.com/mediapipe-models/pose_landmarker/${model}/float16/1/${model}.task`;

// Singleton promises so concurrent callers share the same work
let wasmPromise = null;
let preloadPromise = null;

const warmFetch = async (url) => {
  try {
    await fetch(url, { mode: 'no-cors', cache: 'force-cache' });
  } catch {
    // Best-effort warmup only
  }
};

// Kick off WASM init independently so it can overlap with model download
export const preloadWasm = () => {
  if (typeof window === 'undefined') return Promise.resolve();
  if (wasmPromise) return wasmPromise;
  wasmPromise = import('@mediapipe/tasks-vision')
    .then(({ FilesetResolver }) => FilesetResolver.forVisionTasks(FILESET_WASM_URL))
    .catch((err) => console.warn('MediaPipe WASM preload failed:', err?.message || err));
  return wasmPromise;
};

export const preloadPoseAssets = () => {
  if (typeof window === 'undefined') return Promise.resolve();
  if (preloadPromise) return preloadPromise;
  preloadPromise = (async () => {
    // WASM and model fetch run in parallel
    await Promise.all([
      preloadWasm(),
      warmFetch(getModelAssetUrl('pose_landmarker_lite')),
    ]);
  })();
  return preloadPromise;
};
