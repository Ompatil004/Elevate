// ─── COMPREHENSIVE MOVEMENT PATTERNS ──
// Pattern mapping for 1300+ exercise dataset via keyword matching
export const LEGACY_MOVEMENT_PATTERNS = {
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

export const getLegacyFallback = (name) => {
  const lower = (name || '').toLowerCase();
  for (const [pat, kws] of Object.entries(LEGACY_MOVEMENT_PATTERNS)) {
    if (kws.some(kw => lower.includes(kw))) return pat;
  }
  return 'GENERIC';
};

export const PATTERN_MAP = {
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
export const SPEED_CATEGORY = {
  CURL: 'fast', PRESS: 'fast', RAISE: 'fast', PULL: 'medium',
  SQUAT: 'slow', HINGE: 'slow', LUNGE: 'slow',
  CORE: 'slow', CALF: 'fast',
  CARDIO: 'fast', GENERIC: 'medium',
};

// ─── ANGLE MATH ──
export const calcAngle = (a, b, c) => {
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
// Fast exercises (curls): high alpha (0.40) = more responsive to quick movement
// Slow exercises (squats): low alpha (0.22) = smoother, less jitter
export const emaSmooth = (prev, curr, alpha) => ({
  x: prev.x * (1 - alpha) + curr.x * alpha,
  y: prev.y * (1 - alpha) + curr.y * alpha,
  z: (prev.z || 0) * (1 - alpha) + (curr.z || 0) * alpha,
  v: prev.v * 0.3 + curr.v * 0.7,
});

export const getAlpha = (pattern) => {
  const speed = SPEED_CATEGORY[pattern] || 'medium';
  if (speed === 'fast') return 0.40;
  if (speed === 'slow') return 0.22;
  return 0.30; // medium
};

export const getFrameSkip = () => 0; // process every frame for smooth overlay

// Minimum visibility threshold for reliable angle calculations
export const MIN_VISIBILITY = 0.40;
export const TRACK_STALE_MS = 180;

export const getPrimaryVisibility = (pattern, pts) => {
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

export const smoothPoint = (prev, curr, alpha) => {
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
