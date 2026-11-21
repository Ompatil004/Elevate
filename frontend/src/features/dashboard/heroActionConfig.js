export const HERO_ACTION_VARIANT = 'neonRadial';

export const HERO_ACTION_VARIANTS = {
  minimal: {
    sync: {
      surface: 'linear-gradient(145deg, rgba(39,39,42,0.96) 0%, rgba(24,24,27,0.96) 100%)',
      border: '1px solid rgba(161,161,170,0.34)',
      shadow: '0 12px 24px rgba(0,0,0,0.3)',
      iconBg: 'rgba(255,255,255,0.09)',
      iconBorder: '1px solid rgba(255,255,255,0.2)',
      iconColor: '#f4f4f5',
      tagBg: 'var(--app-border)',
      tagBorder: '1px solid rgba(255,255,255,0.2)',
      tagColor: '#d4d4d8',
      subtitleColor: 'rgba(228,228,231,0.9)'
    },
    workout: {
      surface: 'linear-gradient(145deg, rgba(36,49,108,0.98) 0%, rgba(30,41,59,0.98) 100%)',
      border: '1px solid rgba(129,140,248,0.46)',
      shadow: '0 14px 28px rgba(49,46,129,0.35)',
      iconBg: 'rgba(129,140,248,0.24)',
      iconBorder: '1px solid rgba(199,210,254,0.45)',
      iconColor: '#e0e7ff',
      tagBg: 'rgba(129,140,248,0.2)',
      tagBorder: '1px solid rgba(129,140,248,0.38)',
      tagColor: '#e0e7ff',
      subtitleColor: 'rgba(224,231,255,0.92)'
    },
    meal: {
      surface: 'linear-gradient(145deg, rgba(131,24,67,0.96) 0%, rgba(63,13,44,0.96) 100%)',
      border: '1px solid rgba(244,114,182,0.45)',
      shadow: '0 14px 28px rgba(131,24,67,0.34)',
      iconBg: 'rgba(244,114,182,0.24)',
      iconBorder: '1px solid rgba(251,207,232,0.42)',
      iconColor: '#fce7f3',
      tagBg: 'rgba(244,114,182,0.2)',
      tagBorder: '1px solid rgba(244,114,182,0.36)',
      tagColor: '#fce7f3',
      subtitleColor: 'rgba(252,231,243,0.9)'
    },
    done: {
      surface: 'linear-gradient(145deg, rgba(20,83,45,0.95) 0%, rgba(22,101,52,0.95) 100%)',
      border: '1px solid rgba(74,222,128,0.42)',
      shadow: '0 14px 28px rgba(21,128,61,0.32)',
      iconBg: 'rgba(74,222,128,0.2)',
      iconBorder: '1px solid rgba(187,247,208,0.42)',
      iconColor: '#dcfce7',
      tagBg: 'rgba(74,222,128,0.2)',
      tagBorder: '1px solid rgba(74,222,128,0.36)',
      tagColor: '#dcfce7',
      subtitleColor: 'rgba(220,252,231,0.92)'
    }
  },
  bold: {
    sync: {
      surface: 'linear-gradient(135deg, var(--app-surface2) 0%, var(--app-surface) 100%)',
      border: '1px solid rgba(255,255,255,0.18)',
      shadow: '0 16px 30px rgba(0,0,0,0.34)',
      iconBg: 'var(--app-border)',
      iconBorder: '1px solid rgba(255,255,255,0.3)',
      iconColor: '#f4f4f5',
      tagBg: 'rgba(255,255,255,0.12)',
      tagBorder: '1px solid rgba(255,255,255,0.25)',
      tagColor: '#f4f4f5',
      subtitleColor: 'rgba(228,228,231,0.92)'
    },
    workout: {
      surface: 'linear-gradient(145deg, rgba(79,70,229,0.96) 0%, rgba(49,46,129,0.96) 100%)',
      border: '1px solid rgba(199,210,254,0.36)',
      shadow: '0 18px 34px rgba(79,70,229,0.4)',
      iconBg: 'rgba(199,210,254,0.25)',
      iconBorder: '1px solid rgba(224,231,255,0.45)',
      iconColor: '#eef2ff',
      tagBg: 'rgba(224,231,255,0.18)',
      tagBorder: '1px solid rgba(224,231,255,0.35)',
      tagColor: '#eef2ff',
      subtitleColor: 'rgba(224,231,255,0.95)'
    },
    meal: {
      surface: 'linear-gradient(145deg, rgba(236,72,153,0.96) 0%, rgba(157,23,77,0.96) 100%)',
      border: '1px solid rgba(251,207,232,0.35)',
      shadow: '0 18px 34px rgba(190,24,93,0.36)',
      iconBg: 'rgba(251,207,232,0.2)',
      iconBorder: '1px solid rgba(251,207,232,0.4)',
      iconColor: '#fff1f8',
      tagBg: 'rgba(251,207,232,0.17)',
      tagBorder: '1px solid rgba(251,207,232,0.34)',
      tagColor: '#fff1f8',
      subtitleColor: 'rgba(255,241,248,0.94)'
    },
    done: {
      surface: 'linear-gradient(145deg, rgba(34,197,94,0.94) 0%, rgba(20,83,45,0.96) 100%)',
      border: '1px solid rgba(187,247,208,0.35)',
      shadow: '0 18px 34px rgba(21,128,61,0.34)',
      iconBg: 'rgba(187,247,208,0.22)',
      iconBorder: '1px solid rgba(220,252,231,0.4)',
      iconColor: '#ecfdf5',
      tagBg: 'rgba(220,252,231,0.16)',
      tagBorder: '1px solid rgba(220,252,231,0.32)',
      tagColor: '#ecfdf5',
      subtitleColor: 'rgba(236,253,245,0.93)'
    }
  },
  glass: {
    sync: {
      surface: 'linear-gradient(150deg, rgba(63,63,70,0.62) 0%, rgba(24,24,27,0.75) 100%)',
      border: '1px solid rgba(228,228,231,0.24)',
      shadow: '0 18px 32px rgba(0,0,0,0.34)',
      iconBg: 'rgba(255,255,255,0.13)',
      iconBorder: '1px solid rgba(255,255,255,0.24)',
      iconColor: '#f4f4f5',
      tagBg: 'var(--app-border)',
      tagBorder: '1px solid rgba(255,255,255,0.2)',
      tagColor: 'var(--app-text)',
      subtitleColor: 'rgba(228,228,231,0.9)'
    },
    workout: {
      surface: 'linear-gradient(150deg, rgba(79,70,229,0.44) 0%, rgba(15,23,42,0.82) 100%)',
      border: '1px solid rgba(129,140,248,0.45)',
      shadow: '0 20px 36px rgba(79,70,229,0.34)',
      iconBg: 'rgba(129,140,248,0.22)',
      iconBorder: '1px solid rgba(199,210,254,0.38)',
      iconColor: '#e0e7ff',
      tagBg: 'rgba(129,140,248,0.18)',
      tagBorder: '1px solid rgba(129,140,248,0.34)',
      tagColor: '#e0e7ff',
      subtitleColor: 'rgba(224,231,255,0.9)'
    },
    meal: {
      surface: 'linear-gradient(150deg, rgba(236,72,153,0.4) 0%, rgba(63,13,44,0.84) 100%)',
      border: '1px solid rgba(244,114,182,0.4)',
      shadow: '0 20px 36px rgba(190,24,93,0.32)',
      iconBg: 'rgba(244,114,182,0.2)',
      iconBorder: '1px solid rgba(251,207,232,0.35)',
      iconColor: '#fdf2f8',
      tagBg: 'rgba(244,114,182,0.16)',
      tagBorder: '1px solid rgba(244,114,182,0.32)',
      tagColor: '#fdf2f8',
      subtitleColor: 'rgba(252,231,243,0.9)'
    },
    done: {
      surface: 'linear-gradient(150deg, rgba(34,197,94,0.36) 0%, rgba(20,83,45,0.84) 100%)',
      border: '1px solid rgba(74,222,128,0.38)',
      shadow: '0 20px 36px rgba(21,128,61,0.3)',
      iconBg: 'rgba(74,222,128,0.18)',
      iconBorder: '1px solid rgba(187,247,208,0.35)',
      iconColor: '#f0fdf4',
      tagBg: 'rgba(74,222,128,0.16)',
      tagBorder: '1px solid rgba(74,222,128,0.3)',
      tagColor: '#f0fdf4',
      subtitleColor: 'rgba(220,252,231,0.9)'
    }
  },
  orbitFusion: {
    sync: {
      surface: 'transparent',
      border: '2px solid rgba(6,182,212,0.75)',
      shadow: '0 0 0 1px rgba(6,182,212,0.2), 0 16px 30px rgba(8,47,73,0.36)',
      iconBg: 'rgba(56,189,248,0.18)',
      iconBorder: '1px solid rgba(125,211,252,0.36)',
      iconColor: '#e0f2fe',
      tagBg: 'rgba(56,189,248,0.15)',
      tagBorder: '1px solid rgba(56,189,248,0.35)',
      tagColor: '#bae6fd',
      subtitleColor: 'rgba(224,242,254,0.95)'
    },
    workout: {
      surface: 'transparent',
      border: '2px solid rgba(79,70,229,0.78)',
      shadow: '0 0 0 1px rgba(79,70,229,0.22), 0 18px 34px rgba(49,46,129,0.4)',
      iconBg: 'rgba(99,102,241,0.22)',
      iconBorder: '1px solid rgba(199,210,254,0.42)',
      iconColor: '#eef2ff',
      tagBg: 'rgba(129,140,248,0.2)',
      tagBorder: '1px solid rgba(199,210,254,0.38)',
      tagColor: '#e0e7ff',
      subtitleColor: 'rgba(224,231,255,0.96)'
    },
    meal: {
      surface: 'transparent',
      border: '2px solid rgba(236,72,153,0.78)',
      shadow: '0 0 0 1px rgba(236,72,153,0.22), 0 18px 34px rgba(157,23,77,0.4)',
      iconBg: 'rgba(236,72,153,0.2)',
      iconBorder: '1px solid rgba(251,207,232,0.38)',
      iconColor: '#fdf2f8',
      tagBg: 'rgba(236,72,153,0.18)',
      tagBorder: '1px solid rgba(244,114,182,0.36)',
      tagColor: '#fbcfe8',
      subtitleColor: 'rgba(252,231,243,0.95)'
    },
    done: {
      surface: 'transparent',
      border: '2px solid rgba(34,197,94,0.72)',
      shadow: '0 0 0 1px rgba(34,197,94,0.2), 0 18px 34px rgba(21,128,61,0.34)',
      iconBg: 'rgba(74,222,128,0.2)',
      iconBorder: '1px solid rgba(187,247,208,0.38)',
      iconColor: '#f0fdf4',
      tagBg: 'rgba(74,222,128,0.17)',
      tagBorder: '1px solid rgba(134,239,172,0.36)',
      tagColor: '#dcfce7',
      subtitleColor: 'rgba(220,252,231,0.95)'
    }
  },
  glassSlideNeo: {
    sync: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(56,189,248,0.38)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #1f2937 0%, #111827 100%)',
      iconBorder: '1px solid rgba(56,189,248,0.28)',
      iconColor: '#bae6fd',
      subtitleColor: '#cbd5e1',
      ctaBorder: 'rgba(56,189,248,0.55)',
      ctaBg: 'rgba(14,165,233,0.14)',
      ctaText: '#e0f2fe',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(56,189,248,0.3)',
      slideKnob: 'linear-gradient(135deg, #06b6d4, #0891b2)',
      slideText: '#bae6fd'
    },
    workout: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(129,140,248,0.4)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #2b2f3a 0%, #171a22 100%)',
      iconBorder: '1px solid rgba(129,140,248,0.3)',
      iconColor: '#e0e7ff',
      subtitleColor: '#cbd5e1',
      ctaBorder: 'rgba(99,102,241,0.62)',
      ctaBg: 'rgba(79,70,229,0.18)',
      ctaText: '#eef2ff',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(129,140,248,0.32)',
      slideKnob: 'linear-gradient(135deg, #4f46e5, #06b6d4)',
      slideText: '#c7d2fe'
    },
    meal: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(244,114,182,0.4)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #2b2f3a 0%, #171a22 100%)',
      iconBorder: '1px solid rgba(244,114,182,0.3)',
      iconColor: '#fbcfe8',
      subtitleColor: '#d8b4fe',
      ctaBorder: 'rgba(236,72,153,0.62)',
      ctaBg: 'rgba(236,72,153,0.16)',
      ctaText: '#fdf2f8',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(244,114,182,0.3)',
      slideKnob: 'linear-gradient(135deg, #ec4899, #06b6d4)',
      slideText: '#fbcfe8'
    },
    done: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(74,222,128,0.4)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #2b2f3a 0%, #171a22 100%)',
      iconBorder: '1px solid rgba(74,222,128,0.3)',
      iconColor: '#bbf7d0',
      subtitleColor: '#bbf7d0',
      ctaBorder: 'rgba(34,197,94,0.58)',
      ctaBg: 'rgba(34,197,94,0.15)',
      ctaText: '#dcfce7',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(74,222,128,0.3)',
      slideKnob: 'linear-gradient(135deg, #22c55e, #16a34a)',
      slideText: '#bbf7d0'
    }
  },
  neonRadial: {
    sync: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#06b6d4',
      ringGlow: 'rgba(6,182,212,0.34)',
      coreBg: '#0b1220',
      coreBorder: 'none',
      iconColor: '#bae6fd',
      titleColor: '#e0f2fe',
      subtitleColor: '#bae6fd',
      ctaBorder: 'rgba(6,182,212,0.62)',
      ctaBg: 'rgba(6,182,212,0.14)',
      ctaText: '#e0f2fe'
    },
    workout: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#ec4899',
      ringGlow: 'rgba(236,72,153,0.34)',
      coreBg: '#17131f',
      coreBorder: 'none',
      iconColor: '#fbcfe8',
      titleColor: '#fce7f3',
      subtitleColor: '#fbcfe8',
      ctaBorder: 'rgba(236,72,153,0.64)',
      ctaBg: 'rgba(236,72,153,0.16)',
      ctaText: '#fff1f8'
    },
    meal: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#4f46e5',
      ringGlow: 'rgba(79,70,229,0.34)',
      coreBg: '#111827',
      coreBorder: 'none',
      iconColor: '#c7d2fe',
      titleColor: '#e0e7ff',
      subtitleColor: '#c7d2fe',
      ctaBorder: 'rgba(79,70,229,0.66)',
      ctaBg: 'rgba(79,70,229,0.16)',
      ctaText: '#eef2ff'
    },
    done: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#22c55e',
      ringGlow: 'rgba(34,197,94,0.32)',
      coreBg: '#102019',
      coreBorder: 'none',
      iconColor: '#bbf7d0',
      titleColor: '#dcfce7',
      subtitleColor: '#bbf7d0',
      ctaBorder: 'rgba(34,197,94,0.62)',
      ctaBg: 'rgba(34,197,94,0.14)',
      ctaText: '#dcfce7'
    }
  }
};

export const getHeroActionTheme = (variantName, stateKey) => {
  const variant = HERO_ACTION_VARIANTS[variantName] || HERO_ACTION_VARIANTS.bold;
  return variant[stateKey] || variant.sync;
};

export const getFallbackRadialScore = (status) => {
  if (status === 'workout') return 42;
  if (status === 'meal') return 74;
  if (status === 'done') return 100;
  return 18;
};

export const getHeroActionMeta = (status) => {
  if (status === 'workout') {
    return {
      stateKey: 'workout',
      icon: '🏋️‍♂️',
      tag: '',
      title: 'Start Workout',
      subtitle: '',
      disabled: false
    };
  }

  if (status === 'meal') {
    return {
      stateKey: 'meal',
      icon: '🍽️',
      tag: '',
      title: 'Complete Meals',
      subtitle: '',
      disabled: false
    };
  }

  if (status === 'done') {
    return {
      stateKey: 'done',
      icon: '✅',
      tag: '',
      title: 'All Set',
      subtitle: '',
      disabled: true
    };
  }

  return {
    stateKey: 'sync',
    icon: '⏳',
    tag: '',
    title: 'Preparing Data',
    subtitle: '',
    disabled: true
  };
};

export const calculateOverallTrendScore = (entry, calorieGoal, waterGoal) => {
  if (!entry || typeof entry !== 'object') return 0;

  const safeCaloriesGoal = Math.max(1, Number(calorieGoal) || 2200);
  const safeWaterGoal = Math.max(0.1, Number(waterGoal) || 2.3);

  const workoutScore = entry.workout_completed ? 100 : (entry.workout_partial ? 50 : 0);
  const mealRaw = Number(entry.calories) || 0;
  const mealScore = entry.meal_completed
    ? 100
    : (mealRaw > 0 ? Math.min(100, (mealRaw / safeCaloriesGoal) * 100) : 0);
  const waterRaw = Number(entry.water_intake ?? entry.water_glasses) || 0;
  const sleepRaw = Number(entry.sleep_duration ?? entry.sleep_hours) || 0;
  const waterScore = Math.min(100, (waterRaw / safeWaterGoal) * 100);
  const sleepScore = Math.min(100, (sleepRaw / 8) * 100);

  return Math.round(
    (workoutScore * 0.3) +
    (mealScore * 0.25) +
    (waterScore * 0.25) +
    (sleepScore * 0.2)
  );
};

export const getDynamicWaterGoal = (weightKg = 70, sleepHours = 0, workoutCompleted = false) => {
  let targetLiters = weightKg * 0.033;
  if (workoutCompleted) targetLiters += 0.5;
  if (sleepHours > 0 && sleepHours < 7) targetLiters += 0.25;
  const rawGoal = Math.min(5.0, Math.max(2.0, targetLiters));
  return parseFloat(rawGoal.toFixed(1));
};
