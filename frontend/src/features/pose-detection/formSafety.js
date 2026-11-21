// ─── FORM SAFETY RULES per pattern ──
export const checkForm = (pattern, angles, calibration = {}) => {
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
